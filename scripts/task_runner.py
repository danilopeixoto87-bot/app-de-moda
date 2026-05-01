"""
Task Runner — CLI para tarefas de IA no projeto App de Moda.
Usa Cerebras (FREE) como primário, Groq como fallback, Claude só se explicitamente pedido.

Uso:
    python scripts/task_runner.py --task code_review  --file backend/app/routes/marketplace.py
    python scripts/task_runner.py --task image_prompt --product "Jeans Premium"
    python scripts/task_runner.py --task content_gen  --product "Camisa Slim" --company "Moda Caruaru"
    python scripts/task_runner.py --task classification --description "Calça jeans masculina cintura alta"
    python scripts/task_runner.py --task code_gen  --spec "Endpoint PATCH /api/companies/{id}"
    python scripts/task_runner.py --tier critical --prompt "Revise a arquitetura de autenticação"
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.ai_router import CRITICAL, FAST, TASK_TIER, call, call_by_task

# ---------------------------------------------------------------------------
# Prompts por tarefa
# ---------------------------------------------------------------------------

_SYSTEMS = {
    "code_review": (
        "Você é um revisor de código Python/FastAPI/TypeScript sênior. "
        "Aponte problemas reais com evidência de linha. Seja conciso e direto. "
        "Foque em: segurança, performance, bugs, naming. Responda em português."
    ),
    "code_gen": (
        "Você é um desenvolvedor Python/FastAPI sênior. "
        "Gere código limpo, tipado, sem comentários óbvios. "
        "Siga o padrão SQLAlchemy ORM e Pydantic já usado no projeto."
    ),
    "image_prompt": (
        "Você gera prompts profissionais para geração de imagem de moda. "
        "Fórmula: [Produto] + [Cenário] + [Iluminação] + [Estilo/Lente] + [Vibe] + [Qualidade]. "
        "Adicione ao final: Rule of thirds composition, Negative space for copy, Photorealistic, Ultra-HD, 8k."
    ),
    "content_gen": (
        "Você escreve descrições de produto para marketplace de moda do Agreste PE (Caruaru, SCC, Toritama). "
        "Tom: direto, atraente, voltado para atacado e varejo regional. Máx 120 palavras."
    ),
    "classification": (
        "Você classifica produtos de vestuário. "
        "Retorne JSON com: category (camisa|calca|bermuda|vestido|blusa|jaqueta|outro), "
        "gender_target (masculino|feminino|unissex|infantil), fabric_hint (se identificável). "
        "Somente JSON, sem explicação."
    ),
    "normalization": (
        "Você normaliza endereços do Polo do Agreste PE. "
        "Retorne JSON com: street, number, neighborhood, city (Caruaru|Santa Cruz do Capibaribe|Toritama), "
        "postal_code (se presente), confidence (0-1). Somente JSON."
    ),
}

_USER_TEMPLATES = {
    "code_review":    "Revise o seguinte código e aponte os problemas:\n\n```\n{content}\n```",
    "code_gen":       "Gere o seguinte: {spec}",
    "image_prompt":   "Produto: {product}. Contexto: {context}. Gere prompt de imagem profissional.",
    "content_gen":    "Produto: {product}. Empresa: {company}. Cidade: {city}. Escreva descrição para marketplace.",
    "classification": "Classifique: {description}",
    "normalization":  "Normalize este endereço: {address}",
}

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Task Runner multi-IA — App de Moda",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--task", choices=list(_USER_TEMPLATES.keys()) + ["generic"], default="generic")
    p.add_argument("--tier", choices=["fast", "explore", "critical"], default=None)
    p.add_argument("--file",        help="Arquivo para leitura (code_review)")
    p.add_argument("--spec",        help="Especificação (code_gen)")
    p.add_argument("--product",     help="Nome do produto")
    p.add_argument("--company",     help="Nome da empresa", default="")
    p.add_argument("--city",        help="Cidade", default="")
    p.add_argument("--context",     help="Contexto adicional", default="moda casual atacado")
    p.add_argument("--description", help="Descrição livre")
    p.add_argument("--address",     help="Endereço para normalizar")
    p.add_argument("--prompt",      help="Prompt livre (modo generic)")
    p.add_argument("--max-tokens",  type=int, default=1200)
    p.add_argument("--dry-run",     action="store_true", help="Mostra modelo que seria usado sem chamar")
    return p


def run(args: argparse.Namespace) -> None:
    task = args.task
    tier = args.tier or TASK_TIER.get(task, "fast")

    if args.dry_run:
        from scripts.ai_router import _MODELS_BY_TIER
        print(f"Tarefa : {task}")
        print(f"Tier   : {tier}")
        print(f"Modelos: {_MODELS_BY_TIER.get(tier, [])}")
        return

    # Monta mensagem
    if task == "generic":
        if not args.prompt:
            print("Use --prompt para modo generic.")
            sys.exit(1)
        content_msg = args.prompt
        system = None
    elif task == "code_review":
        if not args.file:
            print("Use --file com code_review.")
            sys.exit(1)
        path = Path(args.file)
        if not path.exists():
            path = Path(__file__).resolve().parents[1] / args.file
        content = path.read_text(encoding="utf-8")
        content_msg = _USER_TEMPLATES["code_review"].format(content=content)
        system = _SYSTEMS["code_review"]
    elif task == "code_gen":
        content_msg = _USER_TEMPLATES["code_gen"].format(spec=args.spec or "")
        system = _SYSTEMS["code_gen"]
    elif task == "image_prompt":
        content_msg = _USER_TEMPLATES["image_prompt"].format(
            product=args.product or "", context=args.context
        )
        system = _SYSTEMS["image_prompt"]
    elif task == "content_gen":
        content_msg = _USER_TEMPLATES["content_gen"].format(
            product=args.product or "", company=args.company, city=args.city
        )
        system = _SYSTEMS["content_gen"]
    elif task == "classification":
        content_msg = _USER_TEMPLATES["classification"].format(
            description=args.description or args.prompt or ""
        )
        system = _SYSTEMS["classification"]
    elif task == "normalization":
        content_msg = _USER_TEMPLATES["normalization"].format(address=args.address or "")
        system = _SYSTEMS["normalization"]
    else:
        content_msg = args.prompt or ""
        system = None

    print(f"\n[ai_router] tier={tier} task={task}")
    result = call(
        tier,
        messages=[{"role": "user", "content": content_msg}],
        task=task,
        max_tokens=args.max_tokens,
        system=system,
    )

    print(f"[ai_router] model={result['model']}  tokens={result['input_tok']}+{result['output_tok']}  custo=U${result['cost_usd']:.5f}\n")
    print("-" * 60)
    print(result["content"])
    print("-" * 60)


if __name__ == "__main__":
    parser = build_parser()
    run(parser.parse_args())
