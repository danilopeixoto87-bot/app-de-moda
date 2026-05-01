"""
Script standalone para carregar seed data no PostgreSQL.
Uso: python backend/seed/run_seed.py
Requer DATABASE_URL e APP_SECRET_KEY configurados.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.db import SessionLocal, init_db
from app.core.seed import run_seed

if __name__ == "__main__":
    print("Inicializando banco de dados...")
    init_db()
    print("Tabelas criadas.")

    db = SessionLocal()
    try:
        run_seed(db)
        print("Seed concluido com sucesso.")
    finally:
        db.close()
