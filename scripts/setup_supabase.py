"""
Setup Supabase — cria bucket product-images e valida conexao.
Uso:
    python scripts/setup_supabase.py

Requer no .env (ou ambiente):
    SUPABASE_URL
    SUPABASE_SERVICE_ROLE_KEY   ← chave sb_secret_* (service_role)
    SUPABASE_STORAGE_BUCKET
"""

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

# Carrega .env se existir
_env_path = Path(__file__).resolve().parents[1] / "backend" / ".env"
if _env_path.exists():
    for line in _env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

SUPABASE_URL    = os.getenv("SUPABASE_URL", "").rstrip("/")
SERVICE_KEY     = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
BUCKET          = os.getenv("SUPABASE_STORAGE_BUCKET", "product-images")

sep = "=" * 56


def _req(method: str, path: str, body: dict | None = None) -> dict:
    url = f"{SUPABASE_URL}/storage/v1{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(
        url, method=method, data=data,
        headers={
            "apikey": SERVICE_KEY,
            "Authorization": f"Bearer {SERVICE_KEY}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        return json.loads(exc.read().decode("utf-8", errors="ignore"))


def check_config() -> bool:
    ok = True
    print(f"\n{sep}")
    print("  SETUP SUPABASE — App de Moda")
    print(sep)
    for var, val in [
        ("SUPABASE_URL", SUPABASE_URL),
        ("SUPABASE_SERVICE_ROLE_KEY", SERVICE_KEY),
        ("SUPABASE_STORAGE_BUCKET", BUCKET),
    ]:
        status = "OK" if val and "PENDENTE" not in val and "[YOUR" not in val else "FALTANDO"
        masked = (val[:12] + "..." if len(val) > 12 else val) if val else "—"
        print(f"  {var:<35} {status}  {masked}")
        if status == "FALTANDO":
            ok = False
    print()
    return ok


def create_bucket() -> None:
    print(f"  Criando bucket '{BUCKET}'...")
    res = _req("POST", "/bucket", {"id": BUCKET, "name": BUCKET, "public": True})
    if res.get("name") == BUCKET or "already exists" in str(res).lower():
        print(f"  Bucket '{BUCKET}' OK (criado ou já existia)")
    else:
        print(f"  ERRO ao criar bucket: {res}")
        if "Unauthorized" in str(res) or "403" in str(res):
            print()
            print("  CAUSA: A chave usada NAO tem permissao para criar buckets.")
            print("  SOLUCAO: Use a chave 'service_role' (sb_secret_...), NAO a anon key.")
            print("  ONDE ACHAR: Supabase Dashboard → Settings → API → service_role")
            sys.exit(1)


def list_buckets() -> None:
    res = _req("GET", "/bucket")
    if isinstance(res, list):
        print(f"\n  Buckets existentes ({len(res)}):")
        for b in res:
            pub = "publico" if b.get("public") else "privado"
            print(f"    - {b['name']} ({pub})")
    else:
        print(f"  Nao foi possivel listar buckets: {res}")


def test_upload() -> None:
    print("\n  Testando upload de imagem de teste...")
    content = b"\x89PNG\r\n\x1a\n" + b"\x00" * 20  # PNG header mínimo
    object_path = f"test/setup-check.png"
    endpoint = f"{SUPABASE_URL}/storage/v1/object/{BUCKET}/{object_path}"
    req = urllib.request.Request(
        endpoint, method="POST", data=content,
        headers={
            "apikey": SERVICE_KEY,
            "Authorization": f"Bearer {SERVICE_KEY}",
            "Content-Type": "image/png",
            "x-upsert": "true",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15):
            pass
        url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{object_path}"
        print(f"  Upload OK! URL pública: {url}")
    except urllib.error.HTTPError as exc:
        print(f"  Upload FALHOU: {exc.read().decode()}")


if __name__ == "__main__":
    if not check_config():
        print("  Configure as variaveis acima antes de continuar.")
        print(f"{sep}\n")
        sys.exit(1)

    create_bucket()
    list_buckets()
    test_upload()
    print(f"\n{sep}")
    print("  Supabase configurado! Pode iniciar o backend.")
    print(f"{sep}\n")
