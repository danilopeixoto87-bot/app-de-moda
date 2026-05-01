import json
import os
from pathlib import Path
from typing import Any, Dict

_CONTEXT_CACHE: Dict[str, Any] | None = None


def _find_config_path() -> Path:
    env = os.getenv("CONTEXT_CONFIG_PATH")
    if env:
        return Path(env)
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "docs" / "contexto-compactacao.json"
        if candidate.exists():
            return candidate
    return Path("contexto-compactacao.json")  # fallback — will trigger not-found branch


def load_context_config() -> Dict[str, Any]:
    global _CONTEXT_CACHE
    if _CONTEXT_CACHE is not None:
        return _CONTEXT_CACHE

    cfg_path = _find_config_path()
    if not cfg_path.exists():
        _CONTEXT_CACHE = {}
        return _CONTEXT_CACHE

    with cfg_path.open("r", encoding="utf-8") as f:
        _CONTEXT_CACHE = json.load(f)
    return _CONTEXT_CACHE


def normalize_city(city: str | None) -> str | None:
    if not city:
        return None
    c = city.strip().lower()
    if c == "caruaru":
        return "caruaru"
    if c in ("santa cruz do capibaribe", "scc"):
        return "scc"
    if c == "toritama":
        return "toritama"
    return c


def compact_context(task: str, raw: Dict[str, Any]) -> Dict[str, Any]:
    cfg = load_context_config()
    limits = cfg.get("task_limits", {})
    task_cfg = limits.get(task, {"max_chars": 1200, "max_tokens": 800})

    city = normalize_city(raw.get("city"))

    compact = {
        "task": task,
        "region": cfg.get("region", "agreste_pe"),
        "city": city,
        "audience": raw.get("audience") or "atacado",
        "company": {
            "id": raw.get("company_id") or "",
            "type": raw.get("company_type") or "",
        },
        "product": {
            "name": raw.get("product_name") or "",
            "category": raw.get("category") or "",
            "sizes": raw.get("sizes") or [],
            "colors": raw.get("colors") or [],
            "fabric": raw.get("fabric") or {},
            "price": raw.get("price") or 0,
            "stock": raw.get("stock") or 0,
        },
        "goal": raw.get("goal") or "vender",
        "channels": raw.get("channels") or ["whatsapp"],
        "constraints": {
            "max_chars": task_cfg.get("max_chars", 1200),
            "max_tokens": task_cfg.get("max_tokens", 800),
        },
    }

    serialized = json.dumps(compact, ensure_ascii=False)
    max_chars = int(task_cfg.get("max_chars", 1200))
    if len(serialized) > max_chars:
        compact["product"]["colors"] = compact["product"]["colors"][:3]
        compact["product"]["sizes"] = compact["product"]["sizes"][:6]

    return compact


def build_image_prompt(raw: Dict[str, Any]) -> str:
    cfg = load_context_config()
    suffix = cfg.get("image_prompt_suffix", [])

    product = raw.get("product_name") or "peca de vestuario"
    scenario = raw.get("scenario") or "ambiente editorial minimalista"
    lighting = raw.get("lighting") or "iluminacao suave com destaque de textura"
    style = raw.get("style_lens") or "fotografia de moda com lente 85mm e profundidade de campo rasa"
    vibe = raw.get("vibe") or "sofisticacao acessivel para atacado"
    quality = raw.get("quality") or "Ultra-HD"

    base = f"{product}, {scenario}, {lighting}, {style}, {vibe}, {quality}"
    if suffix:
        base = f"{base}, " + ", ".join(suffix)
    return base
