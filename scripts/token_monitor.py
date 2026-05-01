"""
Monitor de consumo de tokens — App de Moda
Lê token_usage.jsonl e exibe dashboard no terminal.

Uso:
    python scripts/token_monitor.py           # hoje
    python scripts/token_monitor.py --all     # histórico completo
    python scripts/token_monitor.py --alert   # alerta se Cerebras > 80% do limite
"""

import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

LOG_FILE = Path(__file__).parent / "token_usage.jsonl"

# Limites diários estimados
DAILY_LIMITS = {
    "cerebras": 1_000_000,   # FREE tier
    "groq":     None,         # pago, sem limite fixo
    "gemini":   None,
    "anthropic": None,
}

COST_THRESHOLD_USD = 0.50   # alerta se custo diário > $0.50


def _load_records(all_time: bool = False) -> list[dict]:
    if not LOG_FILE.exists():
        return []
    today = datetime.now(timezone.utc).date().isoformat()
    records = []
    with LOG_FILE.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
                if all_time or r["ts"][:10] == today:
                    records.append(r)
            except Exception:
                continue
    return records


def _provider(model: str) -> str:
    if model.startswith("cerebras"):
        return "cerebras"
    if model.startswith("groq"):
        return "groq"
    if model.startswith("gemini"):
        return "gemini"
    if model.startswith("anthropic"):
        return "anthropic"
    return "other"


def _bar(value: int, total: int, width: int = 20) -> str:
    if total == 0:
        return "[" + " " * width + "]"
    filled = min(width, int(width * value / total))
    return "[" + "#" * filled + "." * (width - filled) + "]"


def show_dashboard(all_time: bool = False, alert_mode: bool = False) -> None:
    records = _load_records(all_time)
    period = "histórico completo" if all_time else "hoje (" + datetime.now().strftime("%d/%m/%Y") + ")"

    if not records:
        print(f"Sem registros para {period}. Nenhuma chamada de IA foi feita ainda.")
        return

    by_provider: dict[str, dict] = defaultdict(lambda: {"tokens": 0, "cost": 0.0, "calls": 0, "models": defaultdict(int)})
    by_task: dict[str, dict] = defaultdict(lambda: {"tokens": 0, "calls": 0})

    total_tokens = 0
    total_cost = 0.0

    for r in records:
        prov = _provider(r["model"])
        by_provider[prov]["tokens"] += r["total_tok"]
        by_provider[prov]["cost"]   += r["cost_usd"]
        by_provider[prov]["calls"]  += 1
        by_provider[prov]["models"][r["model"]] += r["total_tok"]
        by_task[r.get("task", "?")]["tokens"] += r["total_tok"]
        by_task[r.get("task", "?")]["calls"]  += 1
        total_tokens += r["total_tok"]
        total_cost   += r["cost_usd"]

    sep = "=" * 58
    print(f"\n{sep}")
    print(f"  TOKEN MONITOR - App de Moda | {period}")
    print(sep)
    print(f"  Total chamadas : {len(records)}")
    print(f"  Total tokens   : {total_tokens:,}")
    print(f"  Custo estimado : U${total_cost:.4f}")
    print(f"{'='*58}")

    print("\n  POR PROVEDOR:\n")
    for prov in ["cerebras", "groq", "gemini", "anthropic", "other"]:
        d = by_provider.get(prov)
        if not d:
            continue
        limit = DAILY_LIMITS.get(prov)
        bar = _bar(d["tokens"], limit or total_tokens)
        pct = f"{d['tokens']*100//limit}%" if limit else "---"
        free_tag = " [FREE]" if prov == "cerebras" else ""
        print(f"  {prov:<12}{free_tag}")
        print(f"    {bar} {d['tokens']:>8,} tok  {pct}  U${d['cost']:.4f}  ({d['calls']} calls)")
        for model, tok in sorted(d["models"].items(), key=lambda x: -x[1]):
            print(f"      ↳ {model:<40} {tok:>8,} tok")

    print("\n  POR TIPO DE TAREFA:\n")
    for task, d in sorted(by_task.items(), key=lambda x: -x[1]["tokens"]):
        print(f"    {task:<25} {d['tokens']:>8,} tok  ({d['calls']} calls)")

    # Alertas
    alerts = []
    cerebras_d = by_provider.get("cerebras", {})
    if cerebras_d and DAILY_LIMITS["cerebras"]:
        pct = cerebras_d["tokens"] / DAILY_LIMITS["cerebras"]
        if pct >= 0.8:
            alerts.append(f"⚠  Cerebras em {pct*100:.0f}% do limite diário ({cerebras_d['tokens']:,}/{DAILY_LIMITS['cerebras']:,} tok)")

    if total_cost >= COST_THRESHOLD_USD:
        alerts.append(f"⚠  Custo diário acima do threshold: U${total_cost:.4f} > U${COST_THRESHOLD_USD}")

    if alerts:
        print("\n  ALERTAS:")
        for a in alerts:
            print(f"  {a}")
        if alert_mode:
            sys.exit(1)

    sep = "=" * 58
    print(f"\n{sep}\n")
    print("  Poupanca estimada vs. Claude puro:")
    claude_equiv = total_tokens / 1000 * 0.009
    real_cost    = total_cost
    saved        = claude_equiv - real_cost
    print(f"    Custo se tudo fosse Claude : U${claude_equiv:.4f}")
    print(f"    Custo real (multi-IA)      : U${real_cost:.4f}")
    print(f"    Economia                   : U${saved:.4f}  ({saved/max(claude_equiv,0.0001)*100:.0f}%)")
    print(f"\n{sep}\n")


if __name__ == "__main__":
    all_time   = "--all"   in sys.argv
    alert_mode = "--alert" in sys.argv
    show_dashboard(all_time=all_time, alert_mode=alert_mode)
