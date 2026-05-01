# Contexto e Compactacao - App de Moda (Polo PE)

## Objetivo
Centralizar contexto de negocio e padronizar compactacao para reduzir custo de IA, aumentar velocidade e manter consistencia entre modulos.

## Regiao alvo
- Caruaru
- Santa Cruz do Capibaribe
- Toritama

## Perfis
- admin
- fabrica
- lojista
- cliente

## Entidades nucleares
- company: loja/fabrica/faccao/atacadista
- product: cadastro base
- variant: tamanho, cor, tecido, composicao, gramatura, modelagem, acabamento, estoque
- order: pedido online multiempresa
- lead: contato em lote via WhatsApp

## Politica de Compactacao (IA)
1. Sempre resumir entrada longa em JSON curto antes de chamar LLM/image model.
2. Remover duplicacoes, textos promocionais e campos vazios.
3. Normalizar termos de vestuario:
- tamanho: P, M, G, GG, EXG ou numerico
- cor: nome + hex opcional
- tecido: tipo + composicao + gsm
4. Limite de contexto por tarefa:
- geracao de imagem: ate 1.5k chars
- copy de anuncio: ate 1.2k chars
- busca inteligente: ate 2k chars
5. Preferir codigos curtos:
- city: caruaru | scc | toritama
- company_type: loja | fabrica | faccao | atacadista

## Envelope padrao de Contexto Compactado
```json
{
  "task": "image_generation|search|order|content",
  "region": "agreste_pe",
  "city": "caruaru|scc|toritama",
  "audience": "atacado|varejo|premium|popular",
  "company": {"id": "", "type": ""},
  "product": {
    "name": "",
    "category": "",
    "sizes": ["M","G"],
    "colors": [{"name":"Azul Marinho","hex":"#1F2A44"}],
    "fabric": {"type":"Denim","composition":"98% Algodao, 2% Elastano","gsm":320},
    "price": 0,
    "stock": 0
  },
  "goal": "vender|catalogar|anunciar|repor",
  "channels": ["whatsapp","instagram"],
  "constraints": {"latency_ms": 30000, "max_tokens": 1200}
}
```

## Prompt Builder (imagem)
Formula obrigatoria:
[Produto] + [Cenario] + [Iluminacao] + [Estilo/Lente] + [Vibe] + [Qualidade]

Otimizadores automaticos:
- "Rule of thirds composition"
- "Negative space for copy"
- "Photorealistic, Ultra-HD, 8k, highly detailed"

## Roteamento de IA (todas disponiveis no app)
- LLM (texto): copy, descricao SEO, normalizacao de cadastro, resumo de contexto.
- IA de imagem (diffusion): catalogo, modelo IA, anuncio.
- Heuristica local (sem custo de token): filtros de busca, deduplicacao, ordenacao por distancia/estoque.

## Pipeline de execucao otimizado
1. Ingestao -> valida schema
2. Compactacao -> gera `compact_context`
3. Roteamento -> escolhe IA por tarefa
4. Execucao -> gera output
5. Pos-processamento -> valida formato e salva historico

## Regras de qualidade
- Nao processar pedido sem item valido.
- Nao publicar variante sem tamanho/cor/tecido.
- Nao gerar contato sem WhatsApp valido.

## KPI de eficiencia
- Reducao de tokens por request
- Tempo medio de resposta por tarefa
- Taxa de sucesso em busca com resultado
- Conversao clique WhatsApp -> pedido
