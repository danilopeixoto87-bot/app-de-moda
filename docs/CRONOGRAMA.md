# Cronograma de Desenvolvimento — App de Moda
> Atualizado em 01/05/2026 · Horizonte: 6 semanas

---

## Visão Geral das Sprints

| Semana | Sprint | Tema | IA Responsável | Status |
|--------|--------|------|----------------|--------|
| 1 | A | UI/UX Redesign | Gemini propõe → Claude revisa | 🔜 Próxima |
| 2 | B | Motor de Comparação de Preços | Cerebras propõe → Claude revisa | ⏳ Aguardando |
| 3 | C | Sistema de Avaliações | Cerebras propõe → Claude revisa | ⏳ Aguardando |
| 4 | D | IA de Recomendação de Compra | Claude arquiteta → Cerebras executa | ⏳ Aguardando |
| 5 | E | Carrinho Multi-loja Otimizado | Gemini propõe → Claude revisa | ⏳ Aguardando |
| 6 | F | Performance e Segurança | Gemini audita → Claude corrige | ⏳ Aguardando |

---

## SPRINT A — UI/UX Redesign (Semana 1)
> **Objetivo:** Transformar o portal num marketplace visualmente profissional, mobile-first.

### A1 — Redesign dos Cards de Produto
- **O que:** Imagem em proporção 3:4, preço destacado, badge "Menor Preço", estrelas de rating
- **Como:** Novo componente `ProductCard.tsx` substituindo o `<label>` atual
- **Critérios:** Funciona em 375px, carrega imagem com `next/image`, acessível (alt text)
- **IA:** Gemini gera layout → Claude valida acessibilidade + performance

### A2 — Busca com Resultados em Tempo Real
- **O que:** Debounce 300ms no input de busca, skeleton loading durante requisição
- **Como:** `useDebounce` hook + `<Skeleton>` components
- **Critérios:** Não dispara mais de 1 req/300ms, UX não trava
- **IA:** Copilot sugere hook → Claude revisa

### A3 — Filtros em Chips Horizontais (já iniciado ✅)
- **O que:** Filtros contextuais mobile-first — Cidade, Categoria, Tipo, Manga, Cor, Tamanho, Tecido
- **Status:** Implementado com `select` contextual; próximo passo → transformar em chips visuais
- **Como:** Componente `FilterChips.tsx` com scroll horizontal em mobile
- **IA:** Claude implementa direto (lógica já validada)

### A4 — Tela de Comparação de Preços
- **O que:** Side-by-side do mesmo produto em lojas diferentes, preço + rating lado a lado
- **Como:** Rota `/comparar?produto=camisa-polo` com tabela comparativa
- **Critérios:** Mostra no mínimo 2 lojas, ordenado por preço
- **IA:** Gemini propõe layout → Claude implementa

### A5 — Header da Loja com Capa e Foto
- **O que:** Banner (1200×300) + logo (100×100) na página `/loja/[id]`
- **Como:** Upload de capa via endpoint `PATCH /portal/companies/{id}/cover`
- **Critérios:** Fallback com gradiente quando não tem imagem
- **IA:** Gemini propõe design → Claude implementa

### A6 — Modo Escuro
- **O que:** Toggle dark/light com CSS variables e `prefers-color-scheme`
- **Como:** `ThemeProvider` + `next-themes`
- **Critérios:** Persiste preferência no localStorage, sem flash no carregamento
- **IA:** Copilot sugere variáveis → Claude valida contraste WCAG AA

---

## SPRINT B — Motor de Comparação de Preços (Semana 2)
> **Objetivo:** Usuário encontra o menor preço entre todas as lojas do polo para qualquer produto.

### B1 — Endpoint de Comparação
- **O que:** `GET /api/portal/compare?category=camisa&city=Caruaru`
- **Como:** Query agrupada por categoria, retorna lista de lojas com preço mínimo/médio
- **Critérios:** Responde em < 500ms, cache de 60s
- **IA:** Cerebras gera query SQL → Claude revisa performance + índices

### B2 — Agrupamento por Similaridade
- **O que:** Agrupar produtos da mesma categoria entre lojas (ex: todas as camisas polo)
- **Como:** `category` + `tipo` como chave de agrupamento
- **Critérios:** Produtos sem variante de preço usam `base_price`
- **IA:** Cerebras propõe lógica → Claude valida edge cases

### B3 — Ordenação por Menor Preço
- **O que:** Listagem unificada de produtos do portal ordenada por preço
- **Como:** Parâmetro `sort=price_asc` no `/portal/search`
- **Critérios:** Considera `variant_price` quando disponível, fallback `base_price`
- **IA:** Claude implementa direto

### B4 — Widget "Loja Mais Barata"
- **O que:** Badge verde "Menor Preço" no card da loja quando tem o preço mais baixo daquela categoria na cidade
- **Como:** Calculado no endpoint B1, enviado como flag `is_cheapest: true` no response
- **Critérios:** Atualiza em tempo real ao mudar filtro de categoria
- **IA:** Gemini propõe design do badge → Claude implementa

---

## SPRINT C — Sistema de Avaliações (Semana 3)
> **Objetivo:** Comprador consegue avaliar lojas e ver o ranking de reputação.

### C1 — Tabela `store_ratings` no DB
- **O que:** Migration: `company_id, customer_whatsapp, score (1–5), comment, created_at`
- **Como:** Alembic migration + novo ORM model `StoreRating`
- **Critérios:** Um WhatsApp pode avaliar cada loja apenas uma vez (unique constraint)
- **IA:** Cerebras gera migration → Claude revisa segurança (IDOR, rate limit)

### C2 — API de Avaliações
- **O que:** `POST /portal/ratings` · `GET /portal/companies/{id}/ratings`
- **Como:** Rate limit: 1 avaliação por WhatsApp por loja por mês
- **Critérios:** Não requer conta (autenticação por WhatsApp), valida score 1–5
- **IA:** Cerebras propõe → Claude revisa LGPD (WhatsApp é dado pessoal)

### C3 — Exibição de Rating nos Cards
- **O que:** Estrelas (★★★★☆) no card de loja e na vitrine `/loja/[id]`
- **Como:** `RatingStars.tsx` component com half-stars opcionais
- **Critérios:** Mostra nota média + contagem de avaliações
- **IA:** Copilot gera componente → Claude valida acessibilidade

### C4 — Ranking de Lojas
- **O que:** Página `/ranking?city=Caruaru` com lojas ordenadas por nota média
- **Como:** `GET /portal/ranking?city=Caruaru` — mínimo 3 avaliações para entrar
- **Critérios:** Atualiza automaticamente ao nova avaliação
- **IA:** Claude implementa endpoint + página

---

## SPRINT D — IA de Recomendação de Compra (Semana 4)
> **Objetivo:** IA sugere a melhor loja para o comprador com base em preço, rating e localização.

### D1 — Prompt de Recomendação
- **O que:** IA analisa rating + preço + localização e retorna texto de recomendação
- **Como:** Cerebras qwen-3-235b com contexto enriquecido (catálogo + ratings)
- **Critérios:** Resposta em < 3s, máximo 150 palavras, linguagem amigável
- **IA:** Claude arquiteta o prompt → Cerebras executa

### D2 — Endpoint `/portal/recommend`
- **O que:** Recebe lista de produtos e retorna ranking de lojas com justificativa
- **Como:** `POST /portal/recommend` com `{ products: [...], city: "Caruaru" }`
- **Critérios:** Não aumenta custo de API além de R$0,01/chamada
- **IA:** Claude arquiteta → Cerebras implementa

### D3 — Widget de Sugestão no Carrinho
- **O que:** Caixa "💡 A loja X tem a melhor avaliação para estes produtos"
- **Como:** Exibido após seleção de produtos, antes de criar pedido
- **Critérios:** Dispara apenas quando há ≥ 2 lojas disponíveis para os produtos
- **IA:** Gemini propõe UX → Claude implementa

### D4 — Histórico de Compras por Cliente
- **O que:** Tabela `customer_purchase_history` para IA aprender preferências
- **Como:** Gravado automaticamente ao criar pedido
- **Critérios:** LGPD: dados anonimizados após 90 dias
- **IA:** Claude arquiteta schema → Cerebras implementa

---

## SPRINT E — Carrinho Multi-loja Otimizado (Semana 5)
> **Objetivo:** Comprador fecha pedidos para várias lojas em um único fluxo.

### E1 — Split Automático por Loja
- **O que:** Divide o carrinho automaticamente por empresa/fabricante
- **Como:** Agrupa `selectedProductIds` por `company_id` antes de criar pedidos
- **Critérios:** Cria N pedidos paralelos (1 por loja), exibe subtotal por loja
- **IA:** Gemini propõe lógica → Claude implementa

### E2 — Resumo por Loja no Checkout
- **O que:** Accordion com subtotal, produtos e frete por loja antes de confirmar
- **Como:** Componente `CartSummaryByStore.tsx`
- **Critérios:** Mostra preço final já com taxa de entrega
- **IA:** Copilot gera componente → Claude valida

### E3 — WhatsApp em Lote
- **O que:** Botão único que abre WA para cada loja com o pedido específico já redigido
- **Como:** Gera N links wa.me com texto pré-preenchido por loja
- **Critérios:** Abre um WA por vez (popup) para não ser bloqueado como spam
- **IA:** Claude implementa

### E4 — Status Unificado de Pedidos
- **O que:** Painel do cliente com todos os pedidos (multi-loja) consolidados
- **Como:** `GET /portal/orders/my` (autenticado) com todos os pedidos do cliente
- **Critérios:** Agrupa por data, mostra status de cada loja separadamente
- **IA:** Cerebras propõe → Claude revisa

---

## SPRINT F — Performance e Segurança (Semana 6)
> **Objetivo:** App pronto para escala: 1000+ usuários simultâneos sem degradar.

### F1 — Rate Limiting na Busca Pública
- **O que:** 60 req/min por IP no `/portal/search`
- **Como:** `_rate_limited()` já existente + Redis (ou in-memory dict)
- **Critérios:** Retorna 429 com header `Retry-After`
- **IA:** Gemini audita → Claude implementa

### F2 — Cache Redis nas Buscas
- **O que:** TTL 60s para buscas idênticas (mesmos parâmetros)
- **Como:** Redis no Railway (plano Hobby $5/mês) + chave hash dos params
- **Critérios:** Hit rate > 40% após 24h; não armazena dados de usuário autenticado
- **IA:** Claude implementa

### F3 — Paginação Cursor-based
- **O que:** Substituir `offset` por cursor em `/portal/search`
- **Como:** Parâmetro `after_id` + `ORDER BY id` (UUID v7 já é monotônico)
- **Critérios:** Performance constante mesmo com 100k produtos
- **IA:** Cerebras propõe → Claude revisa

### F4 — Compressão de Imagens no Upload
- **O que:** Redimensionar para max 800px e converter para WebP no upload
- **Como:** `Pillow` no backend antes de salvar no Supabase Storage
- **Critérios:** Redução de 60%+ no tamanho médio das imagens
- **IA:** Claude implementa

### F5 — Monitoramento com Sentry
- **O que:** Frontend + Backend com alertas automáticos de erros
- **Como:** `sentry-sdk` no FastAPI + `@sentry/nextjs` no Next.js
- **Critérios:** Alerta no Slack/email quando taxa de erro > 1% em 5min
- **IA:** Copilot configura DSN → Claude valida privacidade (sem PII nos traces)

---

## Funcionalidades Já Implementadas (Sprint 0 — Base)

| # | Funcionalidade | Status |
|---|---|---|
| 0.1 | Backend FastAPI + PostgreSQL (Supabase) no Railway | ✅ Produção |
| 0.2 | Frontend Next.js 14 no Vercel | ✅ Produção |
| 0.3 | Autenticação JWT (login/registro) | ✅ Produção |
| 0.4 | Cadastro de empresas (lojas/fábricas) | ✅ Produção |
| 0.5 | Busca centralizada (`/portal/search`) com filtros | ✅ Produção |
| 0.6 | Filtros contextuais (Tipo, Manga por categoria) | ✅ Implementado |
| 0.7 | Vitrine pública da loja (`/loja/[id]`) | ✅ Produção |
| 0.8 | Carrinho e pedido com logística (retirada/entrega/excursão) | ✅ Produção |
| 0.9 | Pagamento via Mercado Pago | ✅ Produção |
| 0.10 | Upload de imagens de produtos (Supabase Storage) | ✅ Produção |
| 0.11 | Geração de imagem com IA (Replicate flux-schnell) | ✅ Produção |
| 0.12 | **Importação de catálogo via CSV** | ✅ Implementado |
| 0.13 | Catálogo seed com 19 produtos / 42 variantes / 5 lojas | ✅ Produção |
| 0.14 | Hierarquia multi-IA (Claude + Gemini + Cerebras + Groq + Copilot) | ✅ Configurado |

---

## Regras do Cronograma

1. Nenhuma implementação ocorre sem aprovação explícita de Claude
2. Cada sprint começa com proposta da IA designada (código + justificativa)
3. Claude revisa: segurança, performance, coerência arquitetural
4. Aprovado → entra no backlog "Validado" → implementação → teste → deploy
5. Reprovado → arquivado em `docs/melhorias-reprovadas.md` com motivo
6. Pesquisa semanal todo segunda-feira alimenta o backlog com novas ideias
