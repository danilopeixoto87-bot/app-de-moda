import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(env_path)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("DATABASE_URL not found")
    exit(1)

engine = create_engine(DATABASE_URL)

queries = [
    # Sprint 2 — imagens
    "ALTER TABLE product_images ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;",
    # Sprint 4 — Mercado Pago
    "ALTER TABLE orders ADD COLUMN IF NOT EXISTS payment_status VARCHAR DEFAULT 'pending';",
    "ALTER TABLE orders ADD COLUMN IF NOT EXISTS payment_id VARCHAR;",
    "ALTER TABLE orders ADD COLUMN IF NOT EXISTS payment_url TEXT;",
    "ALTER TABLE orders ADD COLUMN IF NOT EXISTS paid_at TIMESTAMP WITHOUT TIME ZONE;",
    # Auditoria — RBAC: vínculo usuário↔empresa e pedido↔cliente
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS company_id VARCHAR REFERENCES companies(id);",
    "ALTER TABLE orders ADD COLUMN IF NOT EXISTS customer_id VARCHAR REFERENCES users(id);",
]

with engine.connect() as conn:
    for q in queries:
        try:
            conn.execute(text(q))
            conn.commit()
            print(f"Executed: {q}")
        except Exception as e:
            print(f"Error executing {q}: {e}")
            conn.rollback()

print("Migration completed")
