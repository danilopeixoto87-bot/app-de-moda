import threading
from collections import defaultdict
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.auth.security import (
    authenticate_user, create_access_token, hash_password, require_roles,
)
from app.core.db import get_db
from app.models.orm import User

router = APIRouter(tags=["auth"])

_attempts: dict[str, list] = defaultdict(list)
_lock = threading.Lock()

_ALLOWED_ROLES = {"admin", "fabrica", "lojista", "cliente"}


def _rate_limited(ip: str, max_per_minute: int = 10) -> bool:
    now = datetime.utcnow()
    cutoff = now - timedelta(minutes=1)
    with _lock:
        _attempts[ip] = [t for t in _attempts[ip] if t > cutoff]
        if len(_attempts[ip]) >= max_per_minute:
            return True
        _attempts[ip].append(now)
        return False


class LoginInput(BaseModel):
    email: EmailStr
    password: str


class RegisterInput(BaseModel):
    email: EmailStr
    password: str
    role: str = "cliente"
    company_id: str | None = None


def _create_user(email: str, password: str, role: str, db: Session, company_id: str | None = None) -> User:
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="Senha deve ter no minimo 6 caracteres")
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=409, detail="Email ja cadastrado")
    user = User(
        email=email, 
        hashed_password=hash_password(password), 
        role=role,
        company_id=company_id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/auth/login")
def login(payload: LoginInput, request: Request, db: Session = Depends(get_db)):
    ip = request.client.host if request.client else "unknown"
    if _rate_limited(ip):
        raise HTTPException(status_code=429, detail="Muitas tentativas de login. Aguarde 1 minuto.")
    user = authenticate_user(payload.email, payload.password, db)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciais invalidas")
    
    token = create_access_token(user_id=user.id, email=user.email, role=user.role)
    return {
        "access_token": token, 
        "token_type": "bearer", 
        "role": user.role,
        "company_id": user.company_id
    }


@router.post("/auth/register", status_code=201)
def register(payload: RegisterInput, request: Request, db: Session = Depends(get_db)):
    ip = request.client.host if request.client else "unknown"
    if _rate_limited(ip, max_per_minute=5):
        raise HTTPException(status_code=429, detail="Muitos registros. Aguarde.")

    if payload.role not in _ALLOWED_ROLES:
        raise HTTPException(status_code=400, detail=f"Role invalido. Permitidos: {sorted(_ALLOWED_ROLES)}")
    if payload.role == "admin":
        raise HTTPException(
            status_code=403,
            detail="Auto-registro como admin nao permitido.",
        )
    user = _create_user(payload.email, payload.password, payload.role, db, payload.company_id)
    return {"message": "Usuario cadastrado com sucesso", "email": user.email, "role": user.role}


@router.post("/auth/admin/register", status_code=201)
def admin_register(
    payload: RegisterInput,
    _admin=Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    if payload.role not in _ALLOWED_ROLES:
        raise HTTPException(status_code=400, detail=f"Role invalido. Permitidos: {sorted(_ALLOWED_ROLES)}")
    user = _create_user(payload.email, payload.password, payload.role, db)
    return {"message": "Usuario cadastrado com sucesso", "email": user.email, "role": user.role}
