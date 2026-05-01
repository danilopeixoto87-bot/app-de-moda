import json
import os
import re
import urllib.error
import urllib.request
from uuid import uuid4


class StorageConfigError(RuntimeError):
    pass


def _storage_env() -> tuple[str, str, str]:
    url = os.getenv("SUPABASE_URL", "").strip().rstrip("/")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    bucket = os.getenv("SUPABASE_STORAGE_BUCKET", "").strip()
    if not url or not key or not bucket:
        raise StorageConfigError(
            "Configure SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY e SUPABASE_STORAGE_BUCKET"
        )
    return url, key, bucket


def upload_product_image(product_id: str, filename: str, content: bytes, content_type: str) -> str:
    base_url, service_key, bucket = _storage_env()
    safe_name = re.sub(r"[^\w.\-]", "_", (filename or "imagem").replace("\\", "_").replace("/", "_"))
    object_path = f"products/{product_id}/{uuid4()}-{safe_name}"
    endpoint = f"{base_url}/storage/v1/object/{bucket}/{object_path}"

    req = urllib.request.Request(
        endpoint,
        method="POST",
        data=content,
        headers={
            "apikey": service_key,
            "Authorization": f"Bearer {service_key}",
            "Content-Type": content_type,
            "x-upsert": "true",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30):
            pass
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        try:
            payload = json.loads(detail)
            msg = payload.get("message") or detail
        except Exception:
            msg = detail or str(exc)
        raise RuntimeError(f"Falha no upload Supabase: {msg}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Falha de rede no upload Supabase: {exc.reason}") from exc

    return f"{base_url}/storage/v1/object/public/{bucket}/{object_path}"
