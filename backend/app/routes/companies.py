from math import asin, cos, radians, sin, sqrt
from typing import Optional
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.orm import Company, row_to_dict

router = APIRouter(tags=["companies"])


def _distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return r * 2 * asin(sqrt(a))


@router.get("/companies")
def list_companies(
    city: Optional[str] = Query(default=None),
    type: Optional[str] = Query(default=None),
    q: Optional[str] = Query(default=None),
    lat: Optional[float] = Query(default=None),
    lng: Optional[float] = Query(default=None),
    radius_km: Optional[float] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(Company).filter(Company.is_active == True)

    if city:
        query = query.filter(Company.city.ilike(city))
    if type:
        query = query.filter(Company.company_type.ilike(type))
    if q:
        term = f"%{q.strip()}%"
        query = query.filter(or_(Company.trade_name.ilike(term), Company.neighborhood.ilike(term)))

    total = query.count()
    companies = query.offset(offset).limit(limit).all()

    items = [row_to_dict(c) for c in companies]

    if lat is not None and lng is not None:
        for item in items:
            item["distance_km"] = round(_distance_km(lat, lng, item["latitude"], item["longitude"]), 2)

        if radius_km is not None:
            items = [i for i in items if i.get("distance_km", 1e9) <= radius_km]

        items.sort(key=lambda x: x.get("distance_km", 1e9))

    return {"total": total, "count": len(items), "limit": limit, "offset": offset, "items": items}


@router.get("/companies/{company_id}")
def get_company(company_id: str, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id, Company.is_active == True).first()
    if not company:
        raise HTTPException(status_code=404, detail="Empresa nao encontrada")
    return row_to_dict(company)


@router.get("/companies/{company_id}/navigation-link")
def get_navigation_link(company_id: str, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id, Company.is_active == True).first()
    if not company:
        raise HTTPException(status_code=404, detail="Empresa nao encontrada")
    return {
        "google_maps": f"https://www.google.com/maps/search/?api=1&query={company.latitude},{company.longitude}",
        "waze": f"https://waze.com/ul?ll={company.latitude},{company.longitude}&navigate=yes",
    }


@router.get("/companies/{company_id}/whatsapp-link")
def get_whatsapp_link(company_id: str, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id, Company.is_active == True).first()
    if not company:
        raise HTTPException(status_code=404, detail="Empresa nao encontrada")
    if not company.whatsapp:
        raise HTTPException(status_code=404, detail="WhatsApp nao cadastrado")
    message = "Ola, vi sua loja no App de Moda e quero saber mais sobre os produtos."
    clean = "".join(ch for ch in company.whatsapp if ch.isdigit())
    return {"whatsapp_url": f"https://wa.me/{clean}?text={quote(message)}"}
