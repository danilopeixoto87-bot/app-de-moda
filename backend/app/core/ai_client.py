"""
Cliente de IA para features do backend — App de Moda.
Usa o ai_router com Cerebras (FREE) como primário.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

# Permite importar scripts.ai_router de dentro do backend
_project_root = Path(__file__).resolve().parents[3]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))


def generate_image_prompt(product_name: str, context: dict) -> str:
    """Gera prompt profissional de imagem via Cerebras (FREE)."""
    # Sanitize input to mitigate prompt injection
    safe_name = product_name.replace('"', '').replace('\n', ' ').strip()[:100]
    safe_category = str(context.get('category', '')).replace('"', '').strip()[:50]
    safe_city = str(context.get('city', 'Caruaru')).replace('"', '').strip()[:50]

    try:
        from scripts.ai_router import FAST, call

        msg = (
            f"Gere um prompt profissional para geracao de imagem de moda para o seguinte produto:\n"
            f"Nome: {safe_name}\n"
            f"Categoria: {safe_category}\n"
            f"Localizacao: {safe_city}\n"
            f"Publico: {context.get('audience', 'atacado')}\n"
            "O prompt deve ser detalhado e focado em alta qualidade fotográfica."
        )
        result = call(
            FAST,
            messages=[{"role": "user", "content": msg}],
            task="image_prompt",
            max_tokens=400,
        )
        return result["content"]
    except Exception:
        # fallback: usa o builder local sem IA
        from app.core.context_engine import build_image_prompt
        return build_image_prompt({"product_name": product_name, **context})


def classify_product(description: str) -> dict[str, Any]:
    """Classifica produto de vestuário via Cerebras (FREE). Retorna dict JSON."""
    import json

    try:
        from scripts.ai_router import FAST, call

        result = call(
            FAST,
            messages=[{"role": "user", "content": f"Classifique: {description}"}],
            task="classification",
            max_tokens=200,
            system=(
                "Classifique produtos de vestuário. Retorne SOMENTE JSON com: "
                "category (camisa|calca|bermuda|vestido|blusa|jaqueta|outro), "
                "gender_target (masculino|feminino|unissex|infantil), "
                "fabric_hint (string ou null)."
            ),
        )
        raw = result["content"].strip()
        # extrai JSON mesmo se vier com markdown
        if "```" in raw:
            raw = raw.split("```")[1].lstrip("json").strip()
        return json.loads(raw)
    except Exception:
        return {"category": "outro", "gender_target": "unissex", "fabric_hint": None}


def normalize_address(raw_address: str) -> dict[str, Any]:
    """Normaliza endereço via Cerebras (FREE). Retorna dict JSON."""
    import json

    try:
        from scripts.ai_router import FAST, call

        result = call(
            FAST,
            messages=[{"role": "user", "content": f"Normalize: {raw_address}"}],
            task="normalization",
            max_tokens=200,
            system=(
                "Normalize endereços do Polo do Agreste PE. Retorne SOMENTE JSON com: "
                "street, number, neighborhood, "
                "city (Caruaru|Santa Cruz do Capibaribe|Toritama), "
                "postal_code (ou null), confidence (0-1)."
            ),
        )
        raw = result["content"].strip()
        if "```" in raw:
            raw = raw.split("```")[1].lstrip("json").strip()
        return json.loads(raw)
    except Exception:
        return {"street": raw_address, "number": None, "neighborhood": None,
                "city": None, "postal_code": None, "confidence": 0.0}
