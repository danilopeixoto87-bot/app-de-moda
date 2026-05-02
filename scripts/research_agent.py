"""
Agente de Pesquisa Semanal — App de Moda
Busca tendências e sugestões de melhoria usando Gemini ou Cerebras.
Salva relatório em docs/pesquisa/YYYY-MM-DD.md para revisão de Claude.

Uso:
  python scripts/research_agent.py

Agendar no Windows Task Scheduler para rodar toda segunda-feira às 9h.
"""

import os
import json
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = REPO_ROOT / "docs" / "pesquisa"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TODAY = datetime.now().strftime("%d-%m-%Y")
OUTPUT_FILE = OUTPUT_DIR / f"{TODAY}.md"

SEARCH_TOPICS = [
    "marketplace moda atacado B2B Brasil 2025 tendências UX",
    "Next.js 15 novidades performance lançamentos 2025",
    "FastAPI segurança melhores práticas escalabilidade 2025",
    "comparação preços marketplace fashion app mobile",
    "VendiZap alternativas marketplace moda polo confecções",
    "avaliação sistema rating lojas atacado polo pernambuco",
    "PWA progressive web app moda e-commerce conversão 2025",
    "WhatsApp commerce catálogo pedidos automação 2025",
]

BACKEND_URL = "https://app-de-moda-production.up.railway.app"

# ---------------------------------------------------------------------------
# Health check do backend antes de qualquer coisa
# ---------------------------------------------------------------------------
def check_backend():
    try:
        import urllib.request
        with urllib.request.urlopen(f"{BACKEND_URL}/health", timeout=10) as r:
            data = json.loads(r.read())
            return data.get("status") == "ok"
    except Exception:
        return False

# ---------------------------------------------------------------------------
# Pesquisa usando Gemini (se disponível) ou Cerebras
# ---------------------------------------------------------------------------
def search_with_gemini(topic: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return ""
    try:
        import urllib.request, urllib.parse
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
        payload = {
            "contents": [{
                "parts": [{
                    "text": (
                        f"Pesquise e resuma em português as principais tendências e novidades sobre: '{topic}'. "
                        f"Foque em aplicações práticas para um marketplace de moda B2B brasileiro. "
                        f"Responda em formato markdown com bullets. Máximo 200 palavras."
                    )
                }]
            }],
            "generationConfig": {"maxOutputTokens": 400}
        }
        data = json.dumps(payload).encode()
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as r:
            result = json.loads(r.read())
            return result["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"(erro Gemini: {e})"


def search_with_cerebras(topic: str) -> str:
    api_key = os.getenv("CEREBRAS_API_KEY")
    if not api_key:
        return ""
    try:
        import urllib.request
        url = "https://api.cerebras.ai/v1/chat/completions"
        payload = {
            "model": "qwen-3-235b",
            "messages": [{
                "role": "user",
                "content": (
                    f"Pesquise e resuma em português as principais tendências sobre: '{topic}'. "
                    f"Foque em aplicações para marketplace de moda B2B. "
                    f"Bullets curtos, máximo 150 palavras."
                )
            }],
            "max_tokens": 300
        }
        data = json.dumps(payload).encode()
        req = urllib.request.Request(url, data=data, headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        })
        with urllib.request.urlopen(req, timeout=30) as r:
            result = json.loads(r.read())
            return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"(erro Cerebras: {e})"


def research_topic(topic: str) -> str:
    result = search_with_gemini(topic)
    if not result or result.startswith("(erro"):
        result = search_with_cerebras(topic)
    if not result or result.startswith("(erro"):
        result = "_Nenhuma IA disponível. Configure GEMINI_API_KEY ou CEREBRAS_API_KEY._"
    return result

# ---------------------------------------------------------------------------
# Gera o relatório
# ---------------------------------------------------------------------------
def generate_report():
    backend_ok = check_backend()
    ia_used = "Gemini 2.5 Flash" if os.getenv("GEMINI_API_KEY") else \
              "Cerebras qwen-3-235b" if os.getenv("CEREBRAS_API_KEY") else "Nenhuma"

    lines = [
        f"# Pesquisa Semanal — {TODAY}",
        f"> Gerado automaticamente por research_agent.py",
        f"> IA utilizada: **{ia_used}**",
        f"> Backend App de Moda: {'✅ Online' if backend_ok else '❌ Offline'}",
        "",
        "---",
        "",
        "## Resultados por Tema",
        "",
    ]

    findings = []

    for topic in SEARCH_TOPICS:
        print(f"  Pesquisando: {topic}...")
        result = research_topic(topic)
        lines += [f"### {topic}", "", result, ""]
        findings.append({"topic": topic, "result": result})

    lines += [
        "---",
        "",
        "## TOP 3 — Para Revisão de Claude",
        "",
        "_(Preencher manualmente após leitura dos resultados acima)_",
        "",
        "| # | Sugestão | Impacto | Custo | Recomendação |",
        "|---|---|---|---|---|",
        "| 1 | | | | |",
        "| 2 | | | | |",
        "| 3 | | | | |",
        "",
        "---",
        "",
        "## Status de Aprovação (Claude preenche)",
        "",
        "- [ ] Revisei todos os itens acima",
        "- [ ] Adicionei aprovados ao backlog em docs/AI_SYSTEM.md",
        "- [ ] Descartei itens inviáveis com justificativa",
        "",
        "> **IMPORTANTE:** Nenhuma implementação ocorre sem aprovação explícita de Claude.",
    ]

    OUTPUT_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n✅ Relatório salvo em: {OUTPUT_FILE}")
    print(f"   Abra para revisão: file:///{OUTPUT_FILE}")
    return str(OUTPUT_FILE)


if __name__ == "__main__":
    print(f"\n🔍 Agente de Pesquisa Semanal — App de Moda")
    print(f"   Data: {TODAY}")
    print(f"   Output: {OUTPUT_FILE}\n")
    generate_report()
