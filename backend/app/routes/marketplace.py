import filetype
import hashlib
import hmac
import os
from collections import defaultdict
from decimal import Decimal
from typing import Dict, List, Optional
from urllib.parse import quote

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, Request
from pydantic import BaseModel, Field
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.auth.security import require_roles, User
from app.routes.auth import _rate_limited
from app.core.ai_client import generate_image_prompt
from app.core.context_engine import build_image_prompt, compact_context
from app.core.db import get_db
from app.core.image_generator import ImageGenConfigError, generate_fashion_image
from app.core.payment import create_payment_preference, get_payment_info
from app.core.storage import StorageConfigError, upload_product_image
from app.models.orm import (
    Company, ExcursionCarrier, Lead, LeadCompany,
    Order, OrderItem, OrderTimeline, Product, ProductImage, ProductVariant,
    _now, row_to_dict,
)

router = APIRouter(tags=["marketplace"])
MAX_IMAGE_BYTES = 8 * 1024 * 1024
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}


# ---------------------------------------------------------------------------
# Pydantic input models
# ---------------------------------------------------------------------------

class CompanyCreate(BaseModel):
    trade_name: str
    company_type: str = Field(pattern="^(loja|fabrica|faccao|atacadista)$")
    city: str = Field(pattern="^(Caruaru|Santa Cruz do Capibaribe|Toritama)$")
    neighborhood: str
    street_address: str
    address_number: str
    latitude: float
    longitude: float
    whatsapp: str
    phone: str | None = None
    instagram: str | None = None


class ProductCreate(BaseModel):
    company_id: str
    sku: str
    product_name: str
    category: str
    gender_target: str | None = None
    description: str | None = None
    base_price: Decimal


class VariantCreate(BaseModel):
    product_id: str
    size_label: str
    color_name: str
    color_hex: str | None = None
    fabric_type: str
    fabric_composition: str | None = None
    gsm: int | None = None
    fit_type: str | None = None
    finish_type: str | None = None
    variant_price: Decimal | None = None
    stock_qty: int = 0


class ExcursionCarrierCreate(BaseModel):
    name: str
    whatsapp: str
    origin_city: str = Field(pattern="^(Caruaru|Santa Cruz do Capibaribe|Toritama)$")
    route_cities: List[str]
    pickup_cutoff_time: str
    max_delivery_hours: int = Field(ge=1, le=72)
    base_fee: Decimal = Field(ge=0)
    is_active: bool = True


class OrderItemInput(BaseModel):
    product_id: str
    variant_id: str | None = None
    quantity: int = Field(ge=1)


class LogisticsInput(BaseModel):
    mode: str = Field(pattern="^(retirada_em_loco|entrega_local|excursao)$")
    delivery_address: str | None = None
    delivery_city: str | None = None
    local_delivery_fee: Decimal | None = None
    excursion_carrier_id: str | None = None
    requested_pickup_at: str | None = None


class OrderCreate(BaseModel):
    customer_name: str
    customer_whatsapp: str
    customer_city: str | None = None
    notes: str | None = None
    items: List[OrderItemInput]
    logistics: LogisticsInput


class LogisticsStatusUpdate(BaseModel):
    order_id: str
    status: str = Field(
        pattern="^(pedido_recebido|em_separacao|pronto_para_coleta|coletado_excursao|em_transito|entregue|cancelado|pedido_pago)$"
    )
    note: str | None = None


class MultiContactCreate(BaseModel):
    customer_name: str
    customer_whatsapp: str
    message: str
    company_ids: List[str]


class CompactContextInput(BaseModel):
    task: str
    payload: Dict


class ImagePromptInput(BaseModel):
    payload: Dict


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _wa_link(phone: str, message: str) -> str:
    clean = "".join(ch for ch in phone if ch.isdigit())
    return f"https://wa.me/{clean}?text={quote(message)}"


def _build_order_dict(order: Order, items_with_products: list, timelines: list) -> dict:
    items = [
        {"product_id": oi.product_id, "variant_id": oi.variant_id, "quantity": oi.quantity}
        for oi, _ in items_with_products
    ]
    company_ids = sorted({p.company_id for _, p in items_with_products})
    timeline = [
        {"status": t.status, "at": t.created_at.isoformat() + "Z" if t.created_at else None, "note": t.note}
        for t in timelines
    ]
    logistics = {
        "mode": order.logistics_mode,
        "delivery_address": order.delivery_address,
        "delivery_city": order.delivery_city,
        "local_delivery_fee": float(order.local_delivery_fee) if order.local_delivery_fee is not None else None,
        "excursion_carrier_id": order.excursion_carrier_id,
        "requested_pickup_at": order.requested_pickup_at,
        "pickup_cutoff_time": order.pickup_cutoff_time,
        "max_delivery_hours": order.max_delivery_hours,
        "estimated_excursion_fee": float(order.estimated_excursion_fee) if order.estimated_excursion_fee is not None else None,
    }
    return {
        "id": order.id,
        "customer_id": order.customer_id,
        "customer_name": order.customer_name,
        "customer_whatsapp": order.customer_whatsapp,
        "customer_city": order.customer_city,
        "notes": order.notes,
        "status": order.status,
        "payment_status": order.payment_status,
        "payment_url": order.payment_url,
        "items": items,
        "company_ids": company_ids,
        "logistics": logistics,
        "logistics_timeline": timeline,
        "created_at": order.created_at.isoformat() + "Z" if order.created_at else None,
    }


def _serialize_order(order: Order, db: Session) -> dict:
    items_q = (
        db.query(OrderItem, Product)
        .join(Product, OrderItem.product_id == Product.id)
        .filter(OrderItem.order_id == order.id)
        .all()
    )
    timelines = (
        db.query(OrderTimeline)
        .filter(OrderTimeline.order_id == order.id)
        .order_by(OrderTimeline.created_at)
        .all()
    )
    return _build_order_dict(order, items_q, timelines)


def _serialize_orders_batch(orders: list, db: Session) -> list:
    if not orders:
        return []
    order_ids = [o.id for o in orders]

    all_items = (
        db.query(OrderItem, Product)
        .join(Product, OrderItem.product_id == Product.id)
        .filter(OrderItem.order_id.in_(order_ids))
        .all()
    )
    all_timelines = (
        db.query(OrderTimeline)
        .filter(OrderTimeline.order_id.in_(order_ids))
        .order_by(OrderTimeline.created_at)
        .all()
    )

    items_by_order: dict = defaultdict(list)
    for oi, prod in all_items:
        items_by_order[oi.order_id].append((oi, prod))

    timelines_by_order: dict = defaultdict(list)
    for t in all_timelines:
        timelines_by_order[t.order_id].append(t)

    return [_build_order_dict(o, items_by_order[o.id], timelines_by_order[o.id]) for o in orders]


# ---------------------------------------------------------------------------
# Portal routes — cadastro
# ---------------------------------------------------------------------------

@router.post("/portal/companies")
def register_company(
    payload: CompanyCreate,
    user: User = Depends(require_roles("admin", "fabrica", "lojista")),
    db: Session = Depends(get_db),
):
    company = Company(**payload.model_dump())
    db.add(company)
    db.commit()
    db.refresh(company)
    return {"message": "Empresa cadastrada", "company": row_to_dict(company)}


@router.post("/portal/catalog/products")
def register_product(
    payload: ProductCreate,
    user: User = Depends(require_roles("admin", "fabrica")),
    db: Session = Depends(get_db),
):
    if user.role == "fabrica" and user.company_id != payload.company_id:
        raise HTTPException(status_code=403, detail="Nao permitido cadastrar produtos para outra empresa")

    company = db.query(Company).filter(Company.id == payload.company_id, Company.is_active == True).first()
    if not company:
        raise HTTPException(status_code=404, detail="Empresa nao encontrada")
    product = Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return {"message": "Produto cadastrado", "product": row_to_dict(product)}


@router.post("/portal/catalog/variants")
def register_variant(
    payload: VariantCreate,
    user: User = Depends(require_roles("admin", "fabrica")),
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == payload.product_id, Product.is_active == True).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produto nao encontrado")
    
    if user.role == "fabrica" and user.company_id != product.company_id:
        raise HTTPException(status_code=403, detail="Nao permitido cadastrar variantes para outra empresa")

    variant = ProductVariant(**payload.model_dump())
    db.add(variant)
    db.commit()
    db.refresh(variant)
    return {"message": "Variante cadastrada", "variant": row_to_dict(variant)}


# ---------------------------------------------------------------------------
# Portal routes — busca
# ---------------------------------------------------------------------------

@router.get("/portal/search")
def portal_search(
    q: str | None = None,
    city: str | None = None,
    category: str | None = None,
    size: str | None = None,
    color: str | None = None,
    fabric: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    companies_q = db.query(Company).filter(Company.is_active == True)
    products_q = db.query(Product).filter(Product.is_active == True)

    if city:
        companies_q = companies_q.filter(Company.city.ilike(f"%{city}%"))
    if q:
        companies_q = companies_q.filter(
            or_(Company.trade_name.ilike(f"%{q}%"), Company.neighborhood.ilike(f"%{q}%"))
        )
        products_q = products_q.filter(
            or_(Product.product_name.ilike(f"%{q}%"), Product.description.ilike(f"%{q}%"))
        )
    if category:
        products_q = products_q.filter(Product.category.ilike(f"%{category}%"))

    companies = companies_q.offset(offset).limit(limit).all()
    products = products_q.offset(offset).limit(limit).all()

    product_ids = [p.id for p in products]
    variants_q = db.query(ProductVariant).filter(ProductVariant.product_id.in_(product_ids))
    if size:
        variants_q = variants_q.filter(ProductVariant.size_label.ilike(f"%{size}%"))
    if color:
        variants_q = variants_q.filter(ProductVariant.color_name.ilike(f"%{color}%"))
    if fabric:
        variants_q = variants_q.filter(ProductVariant.fabric_type.ilike(f"%{fabric}%"))
    variants = variants_q.limit(100).all()

    return {
        "companies_count": len(companies),
        "products_count": len(products),
        "variants_count": len(variants),
        "companies": [row_to_dict(c) for c in companies],
        "products": [row_to_dict(p) for p in products],
        "variants": [row_to_dict(v) for v in variants],
    }


# ---------------------------------------------------------------------------
# Portal routes — pedidos
# ---------------------------------------------------------------------------

@router.post("/portal/orders")
def create_order(
    payload: OrderCreate,
    request: Request,
    user: User = Depends(require_roles("admin", "fabrica", "lojista", "cliente")),
    db: Session = Depends(get_db),
):
    ip = request.client.host if request.client else "unknown"
    if _rate_limited(ip, max_per_minute=3):
        raise HTTPException(status_code=429, detail="Muitos pedidos. Aguarde.")

    logi = payload.logistics

    order_data = {
        "customer_id": user.id,
        "customer_name": payload.customer_name,
        "customer_whatsapp": payload.customer_whatsapp,
        "customer_city": payload.customer_city,
        "notes": payload.notes,
        "logistics_mode": logi.mode,
        "delivery_address": logi.delivery_address,
        "delivery_city": logi.delivery_city,
        "local_delivery_fee": logi.local_delivery_fee,
        "excursion_carrier_id": logi.excursion_carrier_id,
        "requested_pickup_at": logi.requested_pickup_at,
    }

    if logi.mode == "excursao" and logi.excursion_carrier_id:
        carrier = db.query(ExcursionCarrier).filter(
            ExcursionCarrier.id == logi.excursion_carrier_id,
            ExcursionCarrier.is_active == True,
        ).first()
        if carrier:
            order_data["pickup_cutoff_time"] = carrier.pickup_cutoff_time
            order_data["max_delivery_hours"] = carrier.max_delivery_hours
            order_data["estimated_excursion_fee"] = carrier.base_fee

    order = Order(**order_data)
    db.add(order)
    db.flush()

    for item in payload.items:
        db.add(OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            variant_id=item.variant_id,
            quantity=item.quantity,
        ))

    db.add(OrderTimeline(
        order_id=order.id,
        status="pedido_recebido",
        note="Pedido criado no portal",
    ))

    db.commit()
    db.refresh(order)

    product_ids_in_order = [item.product_id for item in payload.items]
    involved_companies = (
        db.query(Company)
        .join(Product, Product.company_id == Company.id)
        .filter(Product.id.in_(product_ids_in_order), Company.is_active == True)
        .distinct()
        .all()
    )
    factory_notifications = [
        {
            "company_id": c.id,
            "trade_name": c.trade_name,
            "whatsapp_url": _wa_link(
                c.whatsapp,
                f"🛍️ Novo pedido #{order.id[:8].upper()}\n"
                f"Cliente: {payload.customer_name} ({payload.customer_whatsapp})\n"
                f"Itens: {len(payload.items)} produto(s)\n"
                f"Retirada: {logi.mode.replace('_', ' ')}",
            ),
        }
        for c in involved_companies
        if c.whatsapp
    ]
    return {
        "message": "Pedido criado",
        "order": _serialize_order(order, db),
        "factory_notifications": factory_notifications,
    }


@router.get("/portal/orders")
def list_orders(
    status: str | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(require_roles("admin", "lojista", "fabrica", "cliente")),
    db: Session = Depends(get_db),
):
    query = db.query(Order)
    
    if user.role == "cliente":
        query = query.filter(Order.customer_id == user.id)
    elif user.role in ("fabrica", "lojista"):
        # Filtra por pedidos que contenham itens da empresa do usuario
        query = query.join(OrderItem).join(Product).filter(Product.company_id == user.company_id)
        
    if status:
        query = query.filter(Order.status == status)
        
    total = query.distinct().count()
    orders = query.distinct().order_by(Order.created_at.desc()).offset(offset).limit(limit).all()
    return {
        "total": total,
        "count": len(orders),
        "limit": limit,
        "offset": offset,
        "items": _serialize_orders_batch(orders, db),
    }


@router.patch("/portal/orders/logistics/status")
def update_logistics_status(
    payload: LogisticsStatusUpdate,
    user: User = Depends(require_roles("admin", "fabrica", "lojista")),
    db: Session = Depends(get_db),
):
    order = db.query(Order).filter(Order.id == payload.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido nao encontrado")
        
    # RBAC: apenas admin ou empresa dona de um dos produtos do pedido pode atualizar status
    if user.role != "admin":
        has_item = db.query(OrderItem).join(Product).filter(
            OrderItem.order_id == order.id,
            Product.company_id == user.company_id
        ).first()
        if not has_item:
            raise HTTPException(status_code=403, detail="Nao permitido atualizar status de pedido alheio")

    order.status = payload.status
    db.add(OrderTimeline(order_id=order.id, status=payload.status, note=payload.note))
    db.commit()
    db.refresh(order)
    return {"message": "Status logistico atualizado", "order": _serialize_order(order, db)}


# ---------------------------------------------------------------------------
# Portal routes — logística (transportadores)
# ---------------------------------------------------------------------------

@router.post("/portal/logistics/excursion-carriers")
def register_carrier(
    payload: ExcursionCarrierCreate,
    _user=Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    carrier = ExcursionCarrier(**payload.model_dump())
    db.add(carrier)
    db.commit()
    db.refresh(carrier)
    return {"message": "Transportador cadastrado", "carrier": row_to_dict(carrier)}


@router.get("/portal/logistics/excursion-carriers")
def list_carriers(
    city: str | None = None,
    _user=Depends(require_roles("admin", "fabrica", "lojista", "cliente")),
    db: Session = Depends(get_db),
):
    q = db.query(ExcursionCarrier).filter(ExcursionCarrier.is_active == True)
    if city:
        q = q.filter(ExcursionCarrier.route_cities.contains([city]))
    carriers = q.order_by(ExcursionCarrier.name).all()
    return {"count": len(carriers), "items": [row_to_dict(c) for c in carriers]}


# ---------------------------------------------------------------------------
# Portal routes — imagens de produto (Sprint 2: upload, Sprint 3: geração IA)
# ---------------------------------------------------------------------------

@router.post("/portal/catalog/products/{product_id}/images")
def upload_product_image_endpoint(
    product_id: str,
    request: Request,
    file: UploadFile = File(...),
    image_kind: str = Form(default="catalogo"),
    user: User = Depends(require_roles("admin", "fabrica")),
    db: Session = Depends(get_db),
):
    ip = request.client.host if request.client else "unknown"
    if _rate_limited(ip, max_per_minute=10):
        raise HTTPException(status_code=429, detail="Muitos uploads. Aguarde.")

    product = db.query(Product).filter(Product.id == product_id, Product.is_active == True).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produto nao encontrado")
        
    if user.role == "fabrica" and user.company_id != product.company_id:
        raise HTTPException(status_code=403, detail="Nao permitido gerenciar imagens de outra empresa")

    file_bytes = file.file.read()
    
    # MIME Validation
    kind = filetype.guess(file_bytes)
    if not kind or kind.mime not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=415, detail=f"Tipo real do arquivo nao permitido: {kind.mime if kind else 'desconhecido'}")

    if len(file_bytes) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="Imagem excede 8 MB")

    try:
        image_url = upload_product_image(product_id, file.filename or "imagem", file_bytes, kind.mime)
    except StorageConfigError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    image = ProductImage(
        product_id=product_id,
        image_url=image_url,
        image_kind=image_kind,
        sort_order=0,
    )
    db.add(image)
    db.commit()
    db.refresh(image)
    return {"message": "Imagem salva", "image": row_to_dict(image)}


@router.get("/portal/catalog/products/{product_id}/images")
def list_product_images(
    product_id: str,
    image_kind: str | None = Query(default=None),
    _user=Depends(require_roles("admin", "fabrica", "lojista", "cliente")),
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == product_id, Product.is_active == True).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produto nao encontrado")
    q = db.query(ProductImage).filter(
        ProductImage.product_id == product_id,
        ProductImage.is_active == True,
    )
    if image_kind:
        q = q.filter(ProductImage.image_kind == image_kind)
    images = q.order_by(ProductImage.sort_order, ProductImage.created_at).all()
    return {"product_id": product_id, "count": len(images), "images": [row_to_dict(i) for i in images]}


@router.post("/portal/catalog/products/{product_id}/generate-image")
def generate_product_image(
    product_id: str,
    request: Request,
    image_kind: str = Query(default="modelo_ia"),
    user: User = Depends(require_roles("admin", "fabrica")),
    db: Session = Depends(get_db),
):
    ip = request.client.host if request.client else "unknown"
    if _rate_limited(ip, max_per_minute=5):
        raise HTTPException(status_code=429, detail="Muitas geracoes de imagem. Aguarde.")

    product = db.query(Product).filter(Product.id == product_id, Product.is_active == True).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produto nao encontrado")
        
    if user.role == "fabrica" and user.company_id != product.company_id:
        raise HTTPException(status_code=403, detail="Nao permitido gerar imagens de outra empresa")

    company = db.query(Company).filter(Company.id == product.company_id).first()

    # Prompt enriquecido via IA (Cerebras FREE)
    try:
        prompt = generate_image_prompt(
            product.product_name,
            {
                "category": product.category,
                "city": company.city if company else "Caruaru",
                "audience": "atacado",
            },
        )
    except Exception:
        prompt = build_image_prompt({
            "product_name": product.product_name,
            "category": product.category,
            "city": company.city if company else "Caruaru",
            "audience": "atacado",
        })

    try:
        image_bytes, content_type, filename = generate_fashion_image(prompt)
    except ImageGenConfigError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    try:
        image_url = upload_product_image(product_id, filename, image_bytes, content_type)
    except StorageConfigError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    image = ProductImage(
        product_id=product_id,
        image_url=image_url,
        image_kind=image_kind,
        sort_order=0,
    )
    db.add(image)
    db.commit()
    db.refresh(image)
    return {"message": "Imagem gerada com sucesso", "prompt_usado": prompt, "image": row_to_dict(image)}


# ---------------------------------------------------------------------------
# Portal routes — contatos em lote
# ---------------------------------------------------------------------------

@router.post("/portal/contacts/multi")
def contact_multiple_companies(
    payload: MultiContactCreate,
    request: Request,
    _user=Depends(require_roles("admin", "lojista", "cliente")),
    db: Session = Depends(get_db),
):
    ip = request.client.host if request.client else "unknown"
    if _rate_limited(ip, max_per_minute=5):
        raise HTTPException(status_code=429, detail="Muitos contatos. Aguarde.")

    valid_companies = db.query(Company).filter(
        Company.id.in_(payload.company_ids), Company.is_active == True
    ).all()
    if not valid_companies:
        raise HTTPException(status_code=404, detail="Nenhuma empresa valida encontrada")

    lead = Lead(
        customer_name=payload.customer_name,
        customer_whatsapp=payload.customer_whatsapp,
        message=payload.message,
    )
    db.add(lead)
    db.flush()

    for c in valid_companies:
        db.add(LeadCompany(lead_id=lead.id, company_id=c.id))

    db.commit()
    db.refresh(lead)

    dispatch = []
    for c in valid_companies:
        if c.whatsapp:
            full_text = f"{payload.message} (Cliente: {payload.customer_name})"
            dispatch.append({
                "company_id": c.id,
                "trade_name": c.trade_name,
                "whatsapp_url": _wa_link(c.whatsapp, full_text),
            })

    return {"message": "Contato em lote preparado", "lead": row_to_dict(lead), "dispatch": dispatch}


# ---------------------------------------------------------------------------
# Pagamentos (Sprint 4 — Mercado Pago)
# ---------------------------------------------------------------------------

@router.post("/portal/orders/{order_id}/checkout")
def init_order_checkout(
    order_id: str,
    user: User = Depends(require_roles("admin", "lojista", "cliente")),
    db: Session = Depends(get_db),
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido nao encontrado")
        
    if user.role == "cliente" and order.customer_id != user.id:
        raise HTTPException(status_code=403, detail="Nao permitido checkout de pedido alheio")

    items_q = (
        db.query(OrderItem, Product)
        .join(Product, OrderItem.product_id == Product.id)
        .filter(OrderItem.order_id == order.id)
        .all()
    )

    mp_items = []
    for oi, prod in items_q:
        mp_items.append({
            "title": prod.product_name,
            "quantity": oi.quantity,
            "unit_price": float(prod.base_price),
            "currency_id": "BRL",
        })

    total_fee = (order.local_delivery_fee or 0) + (order.estimated_excursion_fee or 0)
    if total_fee > 0:
        mp_items.append({
            "title": "Taxas de Entrega/Logistica",
            "quantity": 1,
            "unit_price": float(total_fee),
            "currency_id": "BRL",
        })

    try:
        preference = create_payment_preference(
            order_id=order.id,
            items=mp_items,
            customer_email=f"cliente_{order.id}@appmoda.local",
        )
        order.payment_url = preference.get("init_point")
        db.commit()
        return {
            "preference_id": preference.get("id"),
            "init_point": preference.get("init_point"),
            "sandbox_init_point": preference.get("sandbox_init_point"),
        }
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erro ao integrar com Mercado Pago: {e}")


_MP_WEBHOOK_SECRET = os.getenv("MP_WEBHOOK_SECRET", "")


def _verify_mp_signature(request: Request, payment_id: str | None) -> bool:
    if not _MP_WEBHOOK_SECRET:
        return True
    signature = request.headers.get("x-signature", "")
    request_id = request.headers.get("x-request-id", "")
    ts = v1 = ""
    for part in signature.split(","):
        k, _, v = part.partition("=")
        if k.strip() == "ts":
            ts = v.strip()
        elif k.strip() == "v1":
            v1 = v.strip()
    manifest = f"id:{payment_id};request-id:{request_id};ts:{ts};"
    expected = hmac.new(
        _MP_WEBHOOK_SECRET.encode(), manifest.encode(), hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, v1)


@router.post("/webhooks/mercadopago")
async def mercadopago_webhook(
    request: Request,
    topic: str | None = Query(None),
    payment_id: str | None = Query(None, alias="id"),
    db: Session = Depends(get_db),
):
    if not _verify_mp_signature(request, payment_id):
        raise HTTPException(status_code=401, detail="Assinatura invalida")

    if topic == "payment" and payment_id:
        payment_data = get_payment_info(payment_id)
        order_id = payment_data.get("external_reference")
        status = payment_data.get("status")

        if order_id:
            order = db.query(Order).filter(Order.id == order_id).first()
            if order:
                # Idempotencia: evita processar se ja estiver pago
                if order.payment_status == "approved":
                    return {"status": "already_approved"}

                order.payment_status = status
                order.payment_id = str(payment_id)
                if status == "approved":
                    order.status = "pedido_pago"
                    order.paid_at = _now()
                    db.add(OrderTimeline(
                        order_id=order.id,
                        status="pedido_pago",
                        note=f"Pagamento aprovado via Mercado Pago (ID: {payment_id})",
                    ))
                db.commit()
                return {"status": "updated"}

    return {"status": "ignored"}


# ---------------------------------------------------------------------------
# Storefront público — página de loja individual (sem auth)
# ---------------------------------------------------------------------------

@router.get("/portal/storefront/{company_id}")
def get_storefront(company_id: str, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id, Company.is_active == True).first()
    if not company:
        raise HTTPException(status_code=404, detail="Empresa nao encontrada")

    products = db.query(Product).filter(
        Product.company_id == company_id, Product.is_active == True
    ).order_by(Product.product_name).all()

    product_ids = [p.id for p in products]

    all_images = (
        db.query(ProductImage)
        .filter(ProductImage.product_id.in_(product_ids), ProductImage.is_active == True)
        .order_by(ProductImage.sort_order, ProductImage.created_at)
        .all()
    ) if product_ids else []

    all_variants = (
        db.query(ProductVariant)
        .filter(ProductVariant.product_id.in_(product_ids), ProductVariant.is_active == True)
        .all()
    ) if product_ids else []

    images_by: dict = defaultdict(list)
    for img in all_images:
        images_by[img.product_id].append(row_to_dict(img))

    variants_by: dict = defaultdict(list)
    for v in all_variants:
        variants_by[v.product_id].append(row_to_dict(v))

    products_data = []
    for p in products:
        pd = row_to_dict(p)
        pd["images"] = images_by[p.id]
        pd["variants"] = variants_by[p.id]
        products_data.append(pd)

    return {
        "company": row_to_dict(company),
        "products": products_data,
        "product_count": len(products_data),
    }


# ---------------------------------------------------------------------------
# IA — compactação de contexto e prompt de imagem
# ---------------------------------------------------------------------------

@router.post("/portal/context/compact")
def compact_context_endpoint(
    payload: CompactContextInput,
    _user=Depends(require_roles("admin", "fabrica", "lojista", "cliente")),
):
    return {"compact_context": compact_context(payload.task, payload.payload)}


@router.post("/portal/image/prompt")
def image_prompt_endpoint(
    payload: ImagePromptInput,
    _user=Depends(require_roles("admin", "fabrica", "lojista", "cliente")),
):
    prompt = build_image_prompt(payload.payload)
    compact = compact_context(
        "image_generation",
        {
            "city": payload.payload.get("city"),
            "audience": payload.payload.get("audience"),
            "product_name": payload.payload.get("product_name"),
            "category": payload.payload.get("category"),
            "sizes": payload.payload.get("sizes") or [],
            "colors": payload.payload.get("colors") or [],
            "fabric": payload.payload.get("fabric") or {},
            "goal": "anunciar",
            "channels": payload.payload.get("channels") or ["whatsapp", "instagram"],
        },
    )
    return {"prompt": prompt, "compact_context": compact}
