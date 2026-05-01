"""
Multi-AI Router — App de Moda
Estratégia de custo:
  TIER 1  Cerebras  qwen-3-235b-a22b-instruct-2507  FREE 1M tok/dia    → bulk, code gen, classify
  TIER 2  Groq      llama-3.3-70b                   $0.0006/1K tok     → fallback rápido
  TIER 3  Gemini    gemini-2.5-flash                grátis/barato      → contexto longo
  TIER 4  Claude    claude-sonnet-4-6               caro               → decisões críticas

Uso:
    from scripts.ai_router import call, FAST, CRITICAL
    result = call(FAST, messages=[{"role":"user","content":"..."}])
"""

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Configuração de modelos
# ---------------------------------------------------------------------------

FAST     = "fast"       # Cerebras → Groq (gratuito/barato)
EXPLORE  = "explore"    # Gemini 2.5 Flash (contexto longo)
CRITICAL = "critical"   # Claude Sonnet (decisões críticas)

# Custo estimado por 1K tokens (input + output combinados)
_COST_PER_1K = {
    "cerebras/qwen-3-235b-a22b-instruct-2507": 0.00,   # FREE
    "groq/llama-3.3-70b-versatile":            0.0007,
    "gemini/gemini-2.5-flash":                 0.0002,
    "anthropic/claude-sonnet-4-6":             0.009,  # (3+15)/2 ≈ médio
}

_MODELS_BY_TIER: dict[str, list[str]] = {
    FAST: [
        "cerebras/qwen-3-235b-a22b-instruct-2507",
        "groq/llama-3.3-70b-versatile",
    ],
    EXPLORE: [
        "gemini/gemini-2.5-flash",
        "groq/llama-3.3-70b-versatile",
    ],
    CRITICAL: [
        "anthropic/claude-sonnet-4-6",
    ],
}

# Variáveis de ambiente esperadas por tier
_ENV_KEYS = {
    "cerebras/qwen-3-235b-a22b-instruct-2507": "CEREBRAS_API_KEY",
    "groq/llama-3.3-70b-versatile":  "GROQ_API_KEY",
    "gemini/gemini-2.5-flash":       "GEMINI_API_KEY",
    "anthropic/claude-sonnet-4-6":   "ANTHROPIC_API_KEY",
}

# Roteamento padrão por tipo de tarefa
TASK_TIER: dict[str, str] = {
    "image_prompt":     FAST,
    "content_gen":      FAST,
    "classification":   FAST,
    "code_review":      FAST,
    "normalization":    FAST,
    "smart_search":     FAST,
    "exploration":      EXPLORE,
    "architecture":     CRITICAL,
    "security_review":  CRITICAL,
    "migration":        CRITICAL,
}

# ---------------------------------------------------------------------------
# Token tracker
# ---------------------------------------------------------------------------

_LOG_FILE = Path(__file__).parent / "token_usage.jsonl"


def _log_usage(model: str, input_tokens: int, output_tokens: int, task: str, latency_ms: int) -> None:
    total = input_tokens + output_tokens
    cost = round(total / 1000 * _COST_PER_1K.get(model, 0.01), 6)
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "model": model,
        "task": task,
        "input_tok": input_tokens,
        "output_tok": output_tokens,
        "total_tok": total,
        "cost_usd": cost,
        "latency_ms": latency_ms,
    }
    with _LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# Chamada unificada
# ---------------------------------------------------------------------------

def call(
    tier: str,
    messages: list[dict[str, str]],
    task: str = "generic",
    max_tokens: int = 1200,
    temperature: float = 0.3,
    system: str | None = None,
) -> dict[str, Any]:
    """
    Chama o melhor modelo disponível no tier informado.
    Faz fallback automático para o próximo modelo se o atual falhar ou a key não estiver setada.

    Retorna:
        {"content": str, "model": str, "input_tok": int, "output_tok": int, "cost_usd": float}
    """
    try:
        import litellm
        litellm.suppress_debug_info = True
    except ImportError:
        raise ImportError("litellm não instalado. Execute: pip install litellm")

    models = _MODELS_BY_TIER.get(tier, _MODELS_BY_TIER[FAST])

    if system:
        messages = [{"role": "system", "content": system}] + messages

    last_error: Exception | None = None
    for model in models:
        env_key = _ENV_KEYS.get(model)
        api_key = os.getenv(env_key) if env_key else None

        if env_key and not api_key:
            continue  # key não disponível, tenta próximo

        try:
            t0 = time.monotonic()
            resp = litellm.completion(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                api_key=api_key,
            )
            latency = int((time.monotonic() - t0) * 1000)

            usage = resp.usage or {}
            in_tok  = getattr(usage, "prompt_tokens", 0) or 0
            out_tok = getattr(usage, "completion_tokens", 0) or 0
            content = resp.choices[0].message.content or ""

            _log_usage(model, in_tok, out_tok, task, latency)

            return {
                "content":    content,
                "model":      model,
                "input_tok":  in_tok,
                "output_tok": out_tok,
                "cost_usd":   round((in_tok + out_tok) / 1000 * _COST_PER_1K.get(model, 0.01), 6),
            }
        except Exception as exc:
            last_error = exc
            continue

    raise RuntimeError(
        f"Todos os modelos do tier '{tier}' falharam. Último erro: {last_error}\n"
        f"Verifique se as API keys estão setadas: {[_ENV_KEYS.get(m) for m in models]}"
    )


def call_by_task(task: str, messages: list[dict[str, str]], **kwargs) -> dict[str, Any]:
    """Rota automaticamente pelo tipo de tarefa."""
    tier = TASK_TIER.get(task, FAST)
    return call(tier, messages, task=task, **kwargs)
