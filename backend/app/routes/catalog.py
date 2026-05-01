from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.orm import Product, ProductVariant, row_to_dict

router = APIRouter(tags=["catalog"])


@router.get("/catalog/products")
def list_products(
    company_id: Optional[str] = Query(default=None),
    category: Optional[str] = Query(default=None),
    q: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(Product).filter(Product.is_active == True)

    if company_id:
        query = query.filter(Product.company_id == company_id)
    if category:
        query = query.filter(Product.category.ilike(category))
    if q:
        term = f"%{q.strip()}%"
        query = query.filter(or_(Product.product_name.ilike(term), Product.description.ilike(term)))

    total = query.count()
    items = [row_to_dict(p) for p in query.offset(offset).limit(limit).all()]
    return {"total": total, "count": len(items), "limit": limit, "offset": offset, "items": items}


@router.get("/catalog/variants")
def list_variants(
    product_id: Optional[str] = Query(default=None),
    size: Optional[str] = Query(default=None),
    color: Optional[str] = Query(default=None),
    fabric: Optional[str] = Query(default=None),
    min_stock: Optional[int] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(ProductVariant).filter(ProductVariant.is_active == True)

    if product_id:
        query = query.filter(ProductVariant.product_id == product_id)
    if size:
        query = query.filter(ProductVariant.size_label.ilike(size))
    if color:
        query = query.filter(ProductVariant.color_name.ilike(f"%{color}%"))
    if fabric:
        query = query.filter(ProductVariant.fabric_type.ilike(f"%{fabric}%"))
    if min_stock is not None:
        query = query.filter(ProductVariant.stock_qty >= min_stock)

    total = query.count()
    items = [row_to_dict(v) for v in query.offset(offset).limit(limit).all()]
    return {"total": total, "count": len(items), "limit": limit, "offset": offset, "items": items}


@router.get("/catalog/products/{product_id}")
def get_product_detail(product_id: str, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id, Product.is_active == True).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produto nao encontrado")
    variants = (
        db.query(ProductVariant)
        .filter(ProductVariant.product_id == product_id, ProductVariant.is_active == True)
        .all()
    )
    return {
        "product": row_to_dict(product),
        "variants": [row_to_dict(v) for v in variants],
        "variant_count": len(variants),
    }
