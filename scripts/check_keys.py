"""
Verifica quais API keys estão disponíveis na sessão atual.
Importante: CEREBRAS_API_KEY precisa ser exportada manualmente em cada sessão nova.

Uso: python scripts/check_keys.py
"""

import os

KEYS = {
    "CEREBRAS_API_KEY":  ("cerebras/qwen-3-235b-a22b-instruct-2507", "FREE 1M tok/dia", "TIER 1 — primário"),
    "GROQ_API_KEY":      ("groq/llama-3.3-70b-versatile", "$0.0007/1K tok",  "TIER 2 — fallback rápido"),
    "GEMINI_API_KEY":    ("gemini/gemini-2.5-flash",       "grátis/baixo",    "TIER 3 — contexto longo"),
    "ANTHROPIC_API_KEY": ("anthropic/claude-sonnet-4-6",   "$0.009/1K tok",   "TIER 4 — crítico apenas"),
}

print("\n  STATUS DAS API KEYS\n  " + "-" * 54)
available = 0
for env_var, (model, cost, role) in KEYS.items():
    val = os.getenv(env_var)
    if val:
        masked = val[:6] + "..." + val[-4:] if len(val) > 10 else "****"
        status = f"✓  {masked}"
        available += 1
    else:
        status = "✗  NÃO DEFINIDA"
    print(f"  {env_var:<25} {status}")
    print(f"     → {model:<40} {cost}")
    print(f"     → {role}\n")

print(f"  {available}/{len(KEYS)} keys disponíveis\n")

if available == 0:
    print("  ⚠  Nenhuma key disponível! Configure pelo menos CEREBRAS_API_KEY:")
    print("     export CEREBRAS_API_KEY=sua-chave")
    print("     (no Windows CMD: set CEREBRAS_API_KEY=sua-chave)\n")
elif "CEREBRAS_API_KEY" not in {k for k, _ in [(k, os.getenv(k)) for k in KEYS] if os.getenv(k)}:
    print("  ⚠  CEREBRAS_API_KEY não definida — Cerebras (FREE) indisponível.")
    print("     Chamadas vão para Groq (pago) ou falhar se sem outras keys.\n")
