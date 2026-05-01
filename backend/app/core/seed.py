from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.models.orm import Company, Product, ProductVariant, User

_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

_SEED_USERS = [
    {"id": "user-admin-001",   "email": "admin@appmoda.dev",   "role": "admin",    "password": "123456", "company_id": None},
    {"id": "user-fabrica-001", "email": "fabrica@appmoda.dev", "role": "fabrica",  "password": "123456", "company_id": "scc-001"},
    {"id": "user-lojista-001", "email": "lojista@appmoda.dev", "role": "lojista",  "password": "123456", "company_id": "tor-001"},
    {"id": "user-cliente-001", "email": "cliente@appmoda.dev", "role": "cliente",  "password": "123456", "company_id": None},
]

_SEED_COMPANIES = [
    {
        "id": "car-001", "trade_name": "Moda Caruaru Atacado", "company_type": "atacadista",
        "city": "Caruaru", "neighborhood": "Centro", "street_address": "Rua Duque de Caxias",
        "address_number": "120", "latitude": -8.2848, "longitude": -35.9699,
        "whatsapp": "+55 81 99999-1001", "phone": "+55 81 3721-1001",
        "instagram": "@modacaruaruatacado", "is_active": True,
    },
    {
        "id": "scc-001", "trade_name": "Fabrica Santa Cruz Jeans", "company_type": "fabrica",
        "city": "Santa Cruz do Capibaribe", "neighborhood": "Nova Santa Cruz",
        "street_address": "Avenida Bela Vista", "address_number": "450",
        "latitude": -7.9575, "longitude": -36.2043, "whatsapp": "+55 81 99999-2001",
        "phone": "+55 81 3759-2001", "instagram": "@santacruzjeans", "is_active": True,
    },
    {
        "id": "tor-001", "trade_name": "Toritama Moda Fitness", "company_type": "loja",
        "city": "Toritama", "neighborhood": "Centro", "street_address": "Rua Joao Chagas",
        "address_number": "89", "latitude": -8.0094, "longitude": -36.0565,
        "whatsapp": "+55 81 99999-3001", "phone": "+55 81 3741-3001",
        "instagram": "@toritamamodafitness", "is_active": True,
    },
]

_SEED_PRODUCTS = [
    {
        "id": "prod-001", "company_id": "car-001", "sku": "CAM-SLIM-001",
        "product_name": "Camisa Slim Masculina", "category": "camisa",
        "gender_target": "masculino", "description": "Camisa casual slim para atacado",
        "base_price": 79.9, "is_active": True,
    },
    {
        "id": "prod-002", "company_id": "scc-001", "sku": "JEA-RET-050",
        "product_name": "Jeans Reto Premium", "category": "calca jeans",
        "gender_target": "unissex", "description": "Jeans de alta durabilidade para revenda",
        "base_price": 129.9, "is_active": True,
    },
]

_SEED_VARIANTS = [
    {
        "id": "var-001", "product_id": "prod-001", "size_label": "M",
        "color_name": "Azul Marinho", "color_hex": "#1F2A44", "fabric_type": "Tricoline",
        "fabric_composition": "100% Algodao", "gsm": 120, "fit_type": "slim",
        "finish_type": "lavado", "variant_price": 84.9, "stock_qty": 60, "is_active": True,
    },
    {
        "id": "var-002", "product_id": "prod-001", "size_label": "G",
        "color_name": "Branco", "color_hex": "#FFFFFF", "fabric_type": "Tricoline",
        "fabric_composition": "100% Algodao", "gsm": 120, "fit_type": "slim",
        "finish_type": "lavado", "variant_price": 84.9, "stock_qty": 45, "is_active": True,
    },
    {
        "id": "var-003", "product_id": "prod-002", "size_label": "42",
        "color_name": "Jeans Escuro", "color_hex": "#213A63", "fabric_type": "Denim",
        "fabric_composition": "98% Algodao, 2% Elastano", "gsm": 320, "fit_type": "reto",
        "finish_type": "stone washed", "variant_price": 139.9, "stock_qty": 80, "is_active": True,
    },
]


def run_seed(db: Session) -> None:
    for u in _SEED_USERS:
        if not db.query(User).filter(User.id == u["id"]).first():
            db.add(User(
                id=u["id"], email=u["email"], role=u["role"], is_active=True,
                company_id=u.get("company_id"),
                hashed_password=_pwd.hash(u["password"]),
            ))

    for c in _SEED_COMPANIES:
        if not db.query(Company).filter(Company.id == c["id"]).first():
            db.add(Company(**c))

    for p in _SEED_PRODUCTS:
        if not db.query(Product).filter(Product.id == p["id"]).first():
            db.add(Product(**p))

    for v in _SEED_VARIANTS:
        if not db.query(ProductVariant).filter(ProductVariant.id == v["id"]).first():
            db.add(ProductVariant(**v))

    db.commit()
