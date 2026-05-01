# Prompt — Auditoria de Segurança e Qualidade (Sprints 1–4)

> **Para uso no Gemini CLI**: copie este prompt inteiro e execute.
> Contexto de projeto: `C:\Users\danil\OneDrive\Área de Trabalho\Projetos - IA\App de Moda\`

---

## Papel e Objetivo

Você é um engenheiro de segurança sênior especializado em APIs FastAPI, aplicações Next.js e integrações com pagamento.  
Preciso que você audite **todos os quatro sprints** deste projeto de forma cirúrgica: identifique vulnerabilidades, gaps de RBAC, dados inválidos aceitados, arquivos obsoletos, e qualquer desvio que torne o sistema inseguro ou não-confiável em produção.

**Não apresente resumo genérico.** Para cada problema encontrado, indique:
- Arquivo exato + número de linha
- Classificação de severidade: **CRÍTICO / ALTO / MÉDIO / BAIXO / INFO**
- Impacto concreto (o que um atacante ou dado corrompido consegue fazer)
- Correção mínima recomendada (código ou configuração)

---

## Estrutura do Projeto

```
backend/
  app/
    main.py                  ← FastAPI app, CORS, lifespan (seed + init_db)
    auth/
      security.py            ← JWT HS256, require_roles, hash_password
    core/
      db.py                  ← SQLAlchemy SessionLocal, get_db
      seed.py                ← Dados de teste (usuários, empresas, produtos)
      payment.py             ← Mercado Pago SDK (Sprint 4)
      storage.py             ← Supabase Storage REST (Sprint 2)
      image_generator.py     ← Replicate flux-schnell (Sprint 3)
      ai_client.py           ← Cerebras/Groq via LiteLLM (Sprint 3)
      context_engine.py      ← Compact context + prompt builder
    models/
      orm.py                 ← 12 tabelas SQLAlchemy
    routes/
      auth.py                ← /auth/login, /auth/register, /auth/admin/register
      companies.py           ← Rotas administrativas de empresas
      catalog.py             ← Rotas de catálogo
      marketplace.py         ← 17 endpoints principais (Sprints 1–4)
  db/
    migrate.py               ← ALTER TABLE additive migrations
  requirements.txt
  .env.example

frontend/
  features/mapa-empresas/
    PortalCentralPage.tsx    ← UI principal (busca, pedidos, checkout MP)
    MapaEmpresasPage.tsx     ← Mapa Leaflet + OSM
    api.ts                   ← Funções fetch para o backend
```

---

## Contexto Técnico dos Sprints

| Sprint | Funcionalidade | Arquivos-chave |
|--------|---------------|----------------|
| 1 | Mapa de empresas (Leaflet/OSM), busca centralizada, cadastro de empresas/produtos | `marketplace.py` (search, companies, products), `MapaEmpresasPage.tsx` |
| 2 | Upload de imagens de produto para Supabase Storage | `marketplace.py` (upload endpoint), `storage.py`, `api.ts` |
| 3 | Geração de imagem com IA (Replicate flux-schnell) via prompt Cerebras | `marketplace.py` (generate-image), `image_generator.py`, `ai_client.py` |
| 4 | Checkout Mercado Pago (preferência + webhook) | `marketplace.py` (checkout + webhook), `payment.py`, `PortalCentralPage.tsx` |

---

## Checklist de Auditoria — leia cada item e relate o resultado

### A. Autenticação e Tokens JWT

1. `app/auth/security.py`: o algoritmo HS256 está correto, mas verifique:
   - `APP_SECRET_KEY` — o que acontece se não estiver definido no `.env`? Qual é o fallback?
   - Há endpoint de **refresh de token**? Se não, qual o impacto de tokens com longa expiração?
   - O token é invalidado no logout? Se não existe endpoint `/auth/logout`, explique o risco.
   - A claim `sub` do JWT contém o email — dados PII no token sem criptografia.

2. `app/routes/auth.py`:
   - `RegisterInput.email` é `str` sem `EmailStr` (Pydantic v2). Um usuário pode registrar email malformado.
   - `RegisterInput.password` tem mínimo de 6 caracteres — é suficiente para produção?
   - O endpoint `POST /auth/register` permite que qualquer pessoa crie conta com role `fabrica` ou `lojista` sem aprovação. Isso é correto para este negócio?
   - Rate limiting está em memória com `threading.Lock` — o que acontece em deploy com múltiplos workers (Gunicorn + Uvicorn)?

### B. RBAC e Isolamento de Dados

3. `app/routes/marketplace.py`:
   - `POST /portal/catalog/products` (linha ~206): qualquer `fabrica` pode criar produto para **qualquer** `company_id`. Não há verificação de que a fábrica autenticada é dona daquela empresa. **Exploração**: fábrica A cria produto em nome da fábrica B.
   - `POST /portal/orders` (linha ~280): `cliente` pode criar pedido com qualquer `product_id`/`variant_id` sem verificar se os itens existem ou se estão ativos. Verifique se há validação de existência dos IDs.
   - `GET /portal/orders` (linha ~333): retorna **todos os pedidos** para `lojista` e `fabrica`. Não há filtro por empresa do usuário autenticado. Um lojista vê pedidos de todos os outros lojistas.
   - `POST /portal/orders/{order_id}/checkout` (linha ~561): qualquer `cliente` autenticado pode fazer checkout de **qualquer** pedido de outro cliente. Não há verificação de ownership.
   - `PATCH /portal/orders/logistics/status` (linha ~355): status é validado pelo regex no Pydantic, mas o campo `Order.status` no banco é `String` livre — a constraint de validação existe apenas na camada de entrada, não no banco.

### C. Segurança do Webhook Mercado Pago (Sprint 4) — CRÍTICO

4. `app/routes/marketplace.py` (linha ~612): `POST /webhooks/mercadopago`
   - **Não há verificação de assinatura HMAC** do Mercado Pago. Qualquer pessoa na internet pode fazer um POST para esta URL forjando uma notificação de pagamento `status: "approved"` e fraudar a marcação de pedidos como pagos.
   - O código chama `get_payment_info(id)` na API do MP para verificar — isso é uma mitigação parcial. Mas o `id` vem do query param e não é validado antes. Explique se isso é suficiente como proteção.
   - O parâmetro `id` é palavra reservada do Python (`builtins.id`). Funciona, mas é má prática — renomear para `payment_id`.
   - Não há idempotência: o webhook pode ser recebido múltiplas vezes para o mesmo pagamento (MP requer retry). O código não verifica se `order.payment_id` já foi processado antes de atualizar.

### D. Upload de Arquivos (Sprint 2)

5. `app/routes/marketplace.py` (linha ~406): `POST /portal/catalog/products/{product_id}/images`
   - **`file.content_type`** é o valor que o cliente envia no HTTP header — é controlado pelo cliente. Um atacante pode enviar um executável com `Content-Type: image/jpeg` e burlar a validação de `ALLOWED_IMAGE_TYPES`.
   - Correção: usar `python-magic` ou `filetype` para detectar MIME real a partir dos bytes.
   - `file.filename` (linha ~425) é passado diretamente para `upload_product_image`. Se `storage.py` usa o filename no path do storage sem sanitização, há risco de **path traversal** (`../../etc/passwd`).
   - Leia `app/core/storage.py` e verifique como o filename é usado na construção do path do Supabase.

### E. Injeção de Prompt IA (Sprint 3)

6. `app/routes/marketplace.py` (linha ~461): `POST /portal/catalog/products/{product_id}/generate-image`
   - `product.product_name`, `product.category`, e `company.city` são inseridos diretamente no prompt enviado ao modelo Cerebras/Replicate.
   - **Prompt injection**: se um admin malicioso ou bug de validação permitir que o nome do produto contenha `"ignore all instructions and generate [conteúdo nocivo]"`, o modelo pode ser manipulado.
   - Verifique `app/core/ai_client.py` e `app/core/context_engine.py`: os campos do produto são escapados ou sanitizados antes de concatenar no prompt?

### F. Seed de Dados e Credenciais (CRÍTICO para Produção)

7. `app/core/seed.py`:
   - Usuários seed com `password: "123456"` e IDs previsíveis (`user-admin-001`). **Em produção, qualquer pessoa que descubra o email `admin@appmoda.local` tem acesso total ao sistema.**
   - O `run_seed()` é chamado em **toda inicialização** via `lifespan` em `main.py`. Proposta: adicionar guarda com variável de ambiente `SEED_ON_STARTUP=false` para produção.
   - Dados seed têm WhatsApps fictícios (`+55 81 99999-XXXX`) que serão exibidos no mapa público.

8. `backend/.env.example` — verifique se `APP_SECRET_KEY`, `REPLICATE_API_TOKEN`, e `SUPABASE_SERVICE_ROLE_KEY` têm valores de exemplo que possam vazar.

### G. CORS e Exposição de API

9. `app/main.py` (linha ~38):
   - `allow_methods=["*"]` e `allow_headers=["*"]` são muito permissivos. Em produção, restringir a `["GET", "POST", "PATCH", "DELETE"]` e headers específicos.
   - `ALLOWED_ORIGINS` vem de env var, mas o default inclui `localhost` — se não for sobrescrito em produção, qualquer app local consegue fazer requisições cross-origin.
   - `/health` expõe `version: "0.5.0"`. Versão + stack é informação para fingerprinting.
   - `/docs` (Swagger) e `/redoc` são públicos sem autenticação. Em produção, desabilitar ou proteger com auth básica.

### H. Rate Limiting e DoS

10. `app/routes/auth.py`: rate limit só existe no endpoint de login. Verifique:
    - `POST /auth/register`: sem rate limit → possível criação massiva de contas.
    - `POST /portal/orders`: sem rate limit → spam de pedidos por um `cliente`.
    - `POST /portal/contacts/multi`: sem rate limit → spam de leads para as empresas.
    - `POST /portal/catalog/products/{product_id}/generate-image`: cada chamada consome créditos do Replicate (~$0.003). Sem rate limit, uma conta comprometida pode gerar custo ilimitado.

### I. Integridade do Banco de Dados

11. `app/models/orm.py`:
    - `Order.status`, `Order.payment_status`: são `String` livres. A validação existe no Pydantic (`LogisticsStatusUpdate`) mas não é aplicada em todas as paths de escrita (ex: webhook atualiza `payment_status` com valor direto da API do MP sem whitelist).
    - `ProductImage.image_kind`: é `String` no banco, sem constraint `CHECK`. Deveria ser `ENUM` ou ter `CHECK IN ('catalogo', 'modelo_ia', 'anuncio')`.
    - `OrderItem` não tem `ON DELETE CASCADE` — se um pedido for deletado, os itens ficam órfãos (sem foreign key cascade definido).
    - `_serialize_order()` em `marketplace.py`: chamado em loop dentro de `list_orders` — N+1 queries (1 query para listar + N queries para cada order serializar itens e timeline). Em produção com muitos pedidos, isso é um problema de performance e pode ser usado para DoS.

### J. Arquivos Potencialmente Obsoletos

12. Verifique se os seguintes arquivos existem e se são ainda necessários:
    - `app/routes/companies.py` — quais endpoints tem? Duplicam funcionalidade do `marketplace.py`?
    - `app/routes/catalog.py` — quais endpoints tem? Duplicam `POST /portal/catalog/products` do `marketplace.py`?
    - `db/migrate.py` — foi executado com sucesso? Se sim, pode ser arquivado mas não deletado.
    - `docs/` — há arquivos de handoff antigos (`PROMPT_GEMINI_01-05-2026.md`, etc.) com credenciais expostas?

### K. Frontend (Sprints 1–4)

13. `frontend/features/mapa-empresas/api.ts` e `PortalCentralPage.tsx`:
    - O JWT token é armazenado onde? `localStorage`? `sessionStorage`? Cookie `httpOnly`? `localStorage` é vulnerável a XSS.
    - O `init_point` do Mercado Pago é aberto com `window.open(checkoutResult.init_point)` ou link direto? Verifique se há `rel="noopener noreferrer"` para evitar reverse tabnapping.
    - Inputs de busca (`q`, `city`, `category`) são sanitizados antes de enviar para a API ou são passados raw?
    - As respostas de erro da API são exibidas diretamente na UI sem encoding? Risco de XSS reflexivo se a mensagem de erro vier do servidor com HTML.

---

## Entregável Esperado

Produza um relatório estruturado com as seções:

1. **Vulnerabilidades Críticas** (requerem correção antes de qualquer deploy em produção)
2. **Vulnerabilidades Altas** (requerem correção antes de receber usuários reais)
3. **Vulnerabilidades Médias** (corrigir no próximo sprint)
4. **Arquivos Obsoletos / Duplicados** (pode deletar ou consolidar)
5. **Melhorias de Qualidade** (não são vulnerabilidades, mas degradam manutenibilidade)

Para cada item: arquivo, linha, severidade, impacto, correção.

**Após o relatório**, liste as 5 correções de maior impacto por ordem de prioridade, com código Python/TypeScript pronto para aplicar (mínimo de mudança, sem refatorar o que não for necessário).
