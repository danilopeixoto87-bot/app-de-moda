"""
Gera/atualiza docs/HANDOFF_ATUAL.md com o status atual do projeto.
Uso: python scripts/handoff.py

Exibe no terminal:
  - Status das API keys
  - Consumo de tokens do dia
  - Últimas 5 tarefas executadas
  - Resumo do handoff gerado
"""

import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HANDOFF_PATH = ROOT / "docs" / "HANDOFF_ATUAL.md"
LOG_FILE = ROOT / "scripts" / "token_usage.jsonl"

DAILY_LIMITS = {"cerebras": 1_000_000}

COST_PER_1K = {
    "cerebras": 0.00,
    "groq": 0.0007,
    "gemini": 0.0002,
    "anthropic": 0.009,
}


def _provider(model: str) -> str:
    for p in ("cerebras", "groq", "gemini", "anthropic"):
        if model.startswith(p):
            return p
    return "other"


def _load_today() -> list[dict]:
    if not LOG_FILE.exists():
        return []
    today = datetime.now(timezone.utc).date().isoformat()
    out = []
    with LOG_FILE.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
                if r.get("ts", "")[:10] == today:
                    out.append(r)
            except Exception:
                continue
    return out


def _check_keys() -> dict[str, str]:
    keys = {
        "CEREBRAS_API_KEY": "cerebras/qwen-3-235b-a22b-instruct-2507",
        "GROQ_API_KEY": "groq/llama-3.3-70b-versatile",
        "GEMINI_API_KEY": "gemini/gemini-2.5-flash",
        "ANTHROPIC_API_KEY": "anthropic/claude-sonnet-4-6",
    }
    result = {}
    for env, model in keys.items():
        val = os.getenv(env)
        result[env] = (val[:6] + "..." if val else "NAO_DEFINIDA")
    return result


def print_status() -> None:
    sep = "=" * 58
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    print(f"\n{sep}")
    print(f"  HANDOFF - App de Moda | {now}")
    print(sep)

    # Keys
    print("\n  API KEYS:")
    keys = _check_keys()
    for env, masked in keys.items():
        ok = "OK" if masked != "NAO_DEFINIDA" else "FALTANDO"
        free = " [FREE]" if "CEREBRAS" in env else ""
        print(f"    {env:<25} {ok}{free} — {masked}")

    # Tokens do dia
    records = _load_today()
    if records:
        by_prov = defaultdict(lambda: {"tokens": 0, "cost": 0.0, "calls": 0})
        for r in records:
            p = _provider(r["model"])
            by_prov[p]["tokens"] += r["total_tok"]
            by_prov[p]["cost"] += r["cost_usd"]
            by_prov[p]["calls"] += 1

        total_tok = sum(d["tokens"] for d in by_prov.values())
        total_cost = sum(d["cost"] for d in by_prov.values())

        print(f"\n  TOKENS HOJE: {total_tok:,} | CUSTO: U${total_cost:.4f}")
        for prov, d in sorted(by_prov.items(), key=lambda x: -x[1]["tokens"]):
            lim = DAILY_LIMITS.get(prov)
            pct = f" ({d['tokens']*100//lim}% do limite)" if lim else ""
            print(f"    {prov:<12} {d['tokens']:>8,} tok  U${d['cost']:.4f}  ({d['calls']} calls){pct}")

        print("\n  ULTIMAS TAREFAS:")
        for r in records[-5:][::-1]:
            ts = r["ts"][11:16]
            print(f"    {ts}  {r['model'].split('/')[-1]:<35}  {r['task']:<20}  {r['total_tok']:>5} tok")
    else:
        print("\n  Sem chamadas de IA hoje.")

    print(f"\n  Handoff: {HANDOFF_PATH}")
    print(sep + "\n")


def update_handoff_timestamp() -> None:
    if not HANDOFF_PATH.exists():
        print("[handoff] HANDOFF_ATUAL.md nao encontrado. Execute Claude Code para gerar.")
        return
    content = HANDOFF_PATH.read_text(encoding="utf-8")
    today = datetime.now().strftime("%d/%m/%Y")
    marker = "*Gerado em"
    if marker in content:
        lines = content.split("\n")
        lines = [
            f"*Atualizado em {today} | gerado originalmente pelo Claude Code*"
            if l.startswith(marker) else l
            for l in lines
        ]
        HANDOFF_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"[handoff] Timestamp atualizado em HANDOFF_ATUAL.md")


if __name__ == "__main__":
    print_status()
    update_handoff_timestamp()
    sys.exit(0)
