"""
Gerador de imagens via Replicate API — Sprint 3
Modelo: black-forest-labs/flux-schnell (~$0.003/imagem, sem mensalidade)
"""

import os
import urllib.request


class ImageGenConfigError(RuntimeError):
    pass


def _token() -> str:
    t = os.getenv("REPLICATE_API_TOKEN", "").strip()
    if not t:
        raise ImageGenConfigError(
            "Configure REPLICATE_API_TOKEN. "
            "Obtenha em: https://replicate.com/account/api-tokens"
        )
    return t


def generate_fashion_image(prompt: str) -> tuple[bytes, str, str]:
    """
    Gera imagem de moda via Replicate flux-schnell.
    Retorna (bytes, content_type, filename).
    Aspect ratio 3:4 (portrait) — ideal para fotos de produto de moda.
    """
    try:
        import replicate
    except ImportError:
        raise ImageGenConfigError("Instale o pacote: pip install replicate>=0.34.0")

    client = replicate.Client(api_token=_token())

    output = client.run(
        "black-forest-labs/flux-schnell",
        input={
            "prompt": prompt,
            "num_outputs": 1,
            "aspect_ratio": "3:4",
            "output_format": "webp",
            "output_quality": 90,
            "go_fast": True,
        },
    )

    # output é lista de FileOutput; converter para str dá a URL temporária
    image_url = str(output[0])

    with urllib.request.urlopen(image_url, timeout=60) as resp:
        image_bytes = resp.read()

    return image_bytes, "image/webp", "gerado-ia.webp"
