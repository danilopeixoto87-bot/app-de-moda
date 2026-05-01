import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean, Column, DateTime, Float, Integer, Numeric,
    String, Text, JSON, ForeignKey,
)

from app.core.db import Base


def _new_id() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.utcnow()


def _serialize(value):
    if isinstance(value, datetime):
        return value.isoformat() + "Z"
    if isinstance(value, Decimal):
        return float(value)
    return value


def row_to_dict(obj) -> dict:
    return {c.name: _serialize(getattr(obj, c.name)) for c in obj.__table__.columns}


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=_new_id)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)
    company_id = Column(String, ForeignKey("companies.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=_now)


class Company(Base):
    __tablename__ = "companies"

    id = Column(String, primary_key=True, default=_new_id)
    trade_name = Column(String, nullable=False)
    company_type = Column(String, nullable=False)
    city = Column(String, nullable=False, index=True)
    neighborhood = Column(String)
    street_address = Column(String, nullable=False)
    address_number = Column(String)
    complement = Column(String)
    postal_code = Column(String)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    whatsapp = Column(String)
    phone = Column(String)
    instagram = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=_now)
    updated_at = Column(DateTime, default=_now, onupdate=_now)


class Product(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, default=_new_id)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False, index=True)
    sku = Column(String, nullable=False)
    product_name = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False)
    gender_target = Column(String)
    description = Column(Text)
    base_price = Column(Numeric(12, 2), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=_now)
    updated_at = Column(DateTime, default=_now, onupdate=_now)


class ProductVariant(Base):
    __tablename__ = "product_variants"

    id = Column(String, primary_key=True, default=_new_id)
    product_id = Column(String, ForeignKey("products.id"), nullable=False, index=True)
    size_label = Column(String, nullable=False)
    color_name = Column(String, nullable=False)
    color_hex = Column(String)
    fabric_type = Column(String, nullable=False)
    fabric_composition = Column(String)
    gsm = Column(Integer)
    fit_type = Column(String)
    finish_type = Column(String)
    variant_price = Column(Numeric(12, 2))
    stock_qty = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=_now)
    updated_at = Column(DateTime, default=_now, onupdate=_now)


class ExcursionCarrier(Base):
    __tablename__ = "excursion_carriers"

    id = Column(String, primary_key=True, default=_new_id)
    name = Column(String, nullable=False)
    whatsapp = Column(String, nullable=False)
    origin_city = Column(String, nullable=False)
    route_cities = Column(JSON, nullable=False, default=list)
    pickup_cutoff_time = Column(String, nullable=False)
    max_delivery_hours = Column(Integer, nullable=False)
    base_fee = Column(Numeric(12, 2), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=_now)


class Order(Base):
    __tablename__ = "orders"

    id = Column(String, primary_key=True, default=_new_id)
    customer_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    customer_name = Column(String, nullable=False)
    customer_whatsapp = Column(String, nullable=False)
    customer_city = Column(String)
    notes = Column(Text)
    status = Column(String, nullable=False, default="pedido_recebido")
    logistics_mode = Column(String, nullable=False)
    delivery_address = Column(String)
    delivery_city = Column(String)
    local_delivery_fee = Column(Numeric(12, 2))
    excursion_carrier_id = Column(String, ForeignKey("excursion_carriers.id"))
    requested_pickup_at = Column(String)
    pickup_cutoff_time = Column(String)
    max_delivery_hours = Column(Integer)
    estimated_excursion_fee = Column(Numeric(12, 2))
    
    # Mercado Pago Fields
    payment_status = Column(String, default="pending")
    payment_id = Column(String)
    payment_url = Column(Text)
    paid_at = Column(DateTime)
    
    created_at = Column(DateTime, default=_now)


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(String, primary_key=True, default=_new_id)
    order_id = Column(String, ForeignKey("orders.id"), nullable=False, index=True)
    product_id = Column(String, ForeignKey("products.id"), nullable=False)
    variant_id = Column(String, ForeignKey("product_variants.id"))
    quantity = Column(Integer, nullable=False)


class OrderTimeline(Base):
    __tablename__ = "order_timeline"

    id = Column(String, primary_key=True, default=_new_id)
    order_id = Column(String, ForeignKey("orders.id"), nullable=False, index=True)
    status = Column(String, nullable=False)
    note = Column(Text)
    created_at = Column(DateTime, default=_now)


class Lead(Base):
    __tablename__ = "leads"

    id = Column(String, primary_key=True, default=_new_id)
    customer_name = Column(String, nullable=False)
    customer_whatsapp = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=_now)


class LeadCompany(Base):
    __tablename__ = "lead_companies"

    lead_id = Column(String, ForeignKey("leads.id"), primary_key=True)
    company_id = Column(String, ForeignKey("companies.id"), primary_key=True)


class ProductImage(Base):
    __tablename__ = "product_images"

    id = Column(String, primary_key=True, default=_new_id)
    product_id = Column(String, ForeignKey("products.id"), nullable=False, index=True)
    variant_id = Column(String, ForeignKey("product_variants.id"))
    image_url = Column(Text, nullable=False)
    image_kind = Column(String, nullable=False)
    sort_order = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=_now)
