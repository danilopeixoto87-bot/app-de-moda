# App de Moda — Handoff Atualizado (01/05/2026)

## Status Sessão Claude Code (01/05/2026) — INFRAESTRUTURA COMPLETA

### O que foi entregue nesta sessão
- ✅ **Supabase Storage** configurado: bucket `product-images` criado (público), upload testado OK
- ✅ **PostgreSQL conectado** via Session Pooler `aws-1-us-east-2.pooler.supabase.com:5432`
- ✅ **11 tabelas criadas** via `Base.metadata.create_all()` (SQLAlchemy)
- ✅ **Backend iniciando** com `python-dotenv` carregando `.env` automático
- ✅ **Auth JWT funcionando**: login `admin@appmoda.local / 123456` retorna token
- ✅ **bcrypt corrigido**: downgrade para `4.0.1` (bcrypt 5.x é incompatível com passlib)
- ✅ **Agent Skills instaladas**: `supabase` + `supabase-postgres-best-practices`
- ✅ **Replicate API token** configurado em `.env`
- ✅ **Sprint 3 código verificado**: implementado e aguardando validação E2E

### Configuração do banco (IMPORTANTE)
```
# Session Pooler (funciona com IPv4 — USAR ESTE)
host: aws-1-us-east-2.pooler.supabase.com
port: 5432
user: postgres.xqgmndegptevuihaazee
# Senha: ver .env (não commitar)

# Conexão direta NÃO funciona — IPv6 only (máquina sem IPv6)
# db.xqgmndegptevuihaazee.supabase.co → BLOQUEADO
```

### Aviso de segurança
Credenciais foram expostas em texto na sessão. **Rotacionar antes do deploy:**
- Senha PostgreSQL → Supabase Dashboard → Settings → Database → Reset
- SERVICE_ROLE_KEY → Supabase Dashboard → Settings → API → Regenerate
- REPLICATE_API_TOKEN → replicate.com → Account → API tokens

---

## Status Anterior (30/04/2026)
- Sprint 1 (MapaEmpresasPage + Leaflet/OSM) concluído.
- Sprint 2 (Upload Supabase Storage) concluído e auditado GO.
- Correções pós-auditoria Sprint 2 aplicadas: `safe_name` sanitizado, endpoint GET /images adicionado.

---

## 1. Visão do Produto

SaaS hiperverticalizado para o **Polo de Confecções do Agreste PE**:
- Cidades: **Caruaru**, **Santa Cruz do Capibaribe**, **Toritama**
- Público: fabricantes, facções, lojistas, atacadistas e clientes B2B

**Funcionalidades core:**
- Marketplace multiempresa (catálogo centralizado)
- Pedidos online com timeline logística
- Logística por excursão (transportadores regionais)
- Geração de prompt de imagem profissional com IA
- Integração WhatsApp (links diretos)
- Motor de contexto/compactação para otimizar tokens de IA

**Modelo de negócio:** SaaS R$29–59/mês + créditos por imagem gerada

---

## 2. Stack Técnica

| Camada | Tecnologia |
|--------|-----------|
| Backend | FastAPI 0.5.0 + SQLAlchemy + PostgreSQL |
| Frontend | React/TypeScript (Next.js), mobile-first |
| IA | Multi-tier: Cerebras (FREE) → Groq → Gemini → Claude |
| Auth | JWT (jose) + bcrypt + RBAC (4 roles) |
| ORM | SQLAlchemy, 10 tabelas, UUIDs |

**Pasta do projeto:**
```
C:\Users\danil\OneDrive\Área de Trabalho\Projetos - IA\App de Moda\
```

---

## 3. Estado Atual — O que está implementado e funcionando

### Backend (FastAPI) — PRONTO PARA PRODUÇÃO

**Autenticação (`backend/app/routes/auth.py`):**
- JWT com `APP_SECRET_KEY` obrigatória (servidor não inicia sem ela)
- 4 roles: `admin`, `fabrica`, `lojista`, `cliente`
- Rate limiting: 10 tentativas de login por IP por minuto
- `POST /api/auth/login`
- `POST /api/auth/register` (cliente/lojista/fabrica; admin bloqueado)
- `POST /api/auth/admin/register` (requer token admin)

**Empresas (`backend/app/routes/companies.py`):**
- `GET /api/companies` — filtros: city, type, q, lat/lng/radius + paginação limit/offset
- `GET /api/companies/{id}`
- `GET /api/companies/{id}/navigation-link` (Google Maps + Waze)
- `GET /api/companies/{id}/whatsapp-link` (URL corretamente encoded)

**Catálogo (`backend/app/routes/catalog.py`):**
- `GET /api/catalog/products` — com paginação
- `GET /api/catalog/products/{id}` — retorna 404 correto
- `GET /api/catalog/variants` — filtros: size, color, fabric, min_stock

**Portal/Marketplace (`backend/app/routes/marketplace.py`):**
- `POST /api/portal/companies` — cadastro empresa (fabrica/lojista/admin)
- `POST /api/portal/catalog/products` — cadastro produto
- `POST /api/portal/catalog/variants` — cadastro variante
- `GET /api/portal/search` — busca centralizada com paginação
- `POST /api/portal/orders` — criar pedido (3 modos de entrega)
- `GET /api/portal/orders` — listar pedidos do usuário
- `PATCH /api/portal/orders/logistics/status` — atualizar status logístico
- `POST /api/portal/logistics/excursion-carriers` — cadastrar transportador
- `GET /api/portal/logistics/excursion-carriers` — listar transportadores
- `POST /api/portal/context/compact` — compactar contexto para IA
- `POST /api/portal/image/prompt` — gerar prompt profissional de imagem
- `POST /api/portal/contacts/multi` — enviar contato para múltiplas empresas
- `GET /health`

**Banco de dados (PostgreSQL — 100% migrado da memória):**
- Tabelas: `users`, `companies`, `products`, `product_variants`, `excursion_carriers`, `orders`, `order_items`, `order_timeline`, `leads`, `lead_companies`
- Seed automático no startup (3 empresas exemplo)
- UUIDs em todos os IDs
- CORS configurado via `ALLOWED_ORIGINS`

**Infraestrutura Multi-IA (scripts/):**
- `ai_router.py` — Cerebras FREE → Groq → Gemini → Claude, fallback automático
- `token_monitor.py` — dashboard de tokens e custos em tempo real
- `task_runner.py` — CLI de tarefas (image_prompt, code_review, content_gen, etc.)
- `check_keys.py` — diagnóstico de API keys
- `token_usage.jsonl` — log automático de todas as chamadas

> **ATENÇÃO (corrigido 30/04/2026):** O modelo Cerebras correto é
> `qwen-3-235b-a22b-instruct-2507` (não `qwen-3-235b`). Já corrigido no `ai_router.py`.

**Motor de IA backend (`backend/app/core/`):**
- `ai_client.py` — `generate_image_prompt()`, `classify_product()`, `normalize_address()`
- `context_engine.py` — `compact_context()` + `build_image_prompt()` (fórmula profissional)
- `db.py` — SQLAlchemy engine + `get_db()` dependency
- `seed.py` — seed das 3 empresas exemplo

### Frontend (React/TypeScript)

| Arquivo | Status | Observação |
|---------|--------|-----------|
| `PortalCentralPage.tsx` | ✅ FUNCIONAL | Login, busca, pedido, logística, WhatsApp |
| `api.ts` | ✅ CORRETO | Usa `API_BASE` sem localhost hardcoded |
| `MapaEmpresasPage.tsx` | ✅ IMPLEMENTADO (Sprint 1) | API real via `API_BASE`, geolocalização e mapa Leaflet/OSM |

---

## 4. Problemas Conhecidos / Pendências Ativas

### Sprint Imediato (frontend)

| # | Problema | Arquivo | Prioridade |
|---|----------|---------|-----------|
| P-01 | CONCLUÍDO: consumo da API real (`GET /api/companies`) com filtros | MapaEmpresasPage.tsx | FECHADO |
| P-02 | CONCLUÍDO: links Rota/WhatsApp via endpoints `/navigation-link` e `/whatsapp-link` | MapaEmpresasPage.tsx | FECHADO |
| P-03 | CONCLUÍDO: mapa visual com `react-leaflet` + OpenStreetMap | MapaEmpresasPage.tsx | FECHADO |
| P-04 | CONCLUÍDO: envio de `lat/lng` via geolocalização do navegador | MapaEmpresasPage.tsx | FECHADO |

### Funcionalidades MVP+ (não implementadas)

| # | Funcionalidade | Esforço | Prioridade |
|---|---------------|---------|-----------|
| ~~F-01~~ | ~~Upload de imagens (S3/R2/Supabase Storage)~~ | ~~médio~~ | ✅ CONCLUÍDO Sprint 2 |
| ~~F-02~~ | ~~Geração de imagens real (Replicate flux-schnell)~~ | ~~médio~~ | ✅ CÓDIGO PRONTO Sprint 3 — aguarda REPLICATE_API_TOKEN |
| F-03 | Pagamento (Mercado Pago + split marketplace) | alto | ALTA |
| F-04 | Token refresh endpoint (`/api/auth/refresh`) | baixo | MÉDIA |
| F-05 | Observabilidade (structlog + Sentry) | baixo | MÉDIA |
| F-06 | Deploy (Docker + Render/Railway + Vercel) | médio | ALTA |
| F-07 | WhatsApp Business API real (webhooks) | alto | BAIXA |

---

## 5. Sprints Planejados

### Sprint 1 — MapaEmpresasPage + Mapa Leaflet (CONCLUÍDO EM 30/04/2026)

**Objetivo:** Conectar a página de mapa à API real e adicionar mapa visual interativo.

**Tarefas:**
1. Remover array `MOCK` do `MapaEmpresasPage.tsx`
2. Chamar `GET /api/companies` usando `API_BASE` de `api.ts` (mesmo padrão do `PortalCentralPage`)
3. Integrar `react-leaflet` com tiles OpenStreetMap (gratuito, sem key)
4. Adicionar `navigator.geolocation.getCurrentPosition()` para enviar lat/lng
5. Adicionar filtros (cidade, tipo) funcionais
6. Botões "Rota" e "WhatsApp" devem chamar `GET /api/companies/{id}/navigation-link` e `/whatsapp-link`

**Critério de aceite:**
- Mapa exibe pins das empresas vindas do banco PostgreSQL
- Filtros por cidade e tipo funcionam
- Botões Rota e WhatsApp funcionam em qualquer domínio (não apenas localhost)
- Funciona responsivo no mobile

**Arquivos a modificar:**
- `frontend/features/mapa-empresas/MapaEmpresasPage.tsx` — reescrever
- `frontend/package.json` — adicionar `react-leaflet`, `leaflet`, `@types/leaflet`

---

### Sprint 2 — Upload de Imagens + Supabase Storage ✅ CONCLUÍDO (01/05/2026)

**Auditoria:** GO — corrigido por Claude Code pós-entrega do Codex.

**Entregues pelo Codex:**
1. ✅ `POST /api/portal/catalog/products/{id}/images` — multipart, RBAC, validação MIME/tamanho, Supabase
2. ✅ `backend/app/core/storage.py` — cliente Supabase via urllib nativo
3. ✅ `ProductImage` ORM adicionado e persistência ativa
4. ✅ Frontend: formulário de upload no `PortalCentralPage.tsx` com preview de link

**Corrigido por Claude Code na auditoria:**
- `safe_name` agora sanitiza Unicode e espaços via `re.sub(r"[^\w.\-]", "_", ...)` (`storage.py`)
- Adicionado `GET /api/portal/catalog/products/{id}/images` (listagem por produto — necessário para Sprint 3)

**Variáveis necessárias (obrigatórias para funcionar):**
```
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJh...
SUPABASE_STORAGE_BUCKET=product-images
```

---

### Sprint 3 — Geração de Imagens Real (IA) ✅ CÓDIGO IMPLEMENTADO — aguardando credenciais

**Código implementado por Claude Code em 01/05/2026. Só faltam as contas externas.**

**Pré-requisitos externos (fazer para ativar o Sprint 3):**

1. **Criar conta e projeto Supabase** (se ainda não existe)
   - Acessar https://supabase.com → New Project
   - Criar bucket `product-images` (Storage → New Bucket → Public: ON)
   - Copiar `Project URL` e `service_role` key em Settings → API
   - Setar no servidor: `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_STORAGE_BUCKET`

2. **Testar upload real**
   ```bash
   # Com o backend rodando e as 3 variáveis setadas:
   curl -X POST http://localhost:8000/api/portal/catalog/products/{product_id}/images \
     -H "Authorization: Bearer <token>" \
     -F "file=@foto.jpg" -F "image_kind=catalogo"
   # Verificar: URL pública retornada abre no browser?
   ```

3. **Criar conta Replicate** e obter API key
   - Acessar https://replicate.com → Account → API tokens
   - Setar: `REPLICATE_API_TOKEN=r8_...`
   - Modelo a usar: `black-forest-labs/flux-schnell` (~$0.003/imagem)

4. **Instalar dependência Replicate no backend**
   ```bash
   pip install replicate
   # Adicionar ao backend/requirements.txt: replicate>=0.34.0
   ```

---

**Objetivo do Sprint 3:** Gerar imagens profissionais de produto com IA, salvar no Supabase e vincular ao catálogo.

**Arquivos implementados:**
1. ✅ `backend/app/core/image_generator.py` — `generate_fashion_image()` via Replicate flux-schnell
2. ✅ `POST /api/portal/catalog/products/{id}/generate-image` — orquestra prompt + Replicate + Supabase + persistência
3. ✅ Frontend: botão "Gerar Imagem com IA" + preview inline + galeria do produto em `PortalCentralPage.tsx`
4. ✅ `api.ts`: `generateProductImage()` + `listProductImages()` + tipo `ProductImage`

**Fluxo completo:**
```
Usuário → seleciona produto → clica "Gerar Imagem IA" →
backend: ai_client.generate_image_prompt() via Cerebras (FREE) →
backend: Replicate flux-schnell gera imagem (3-8s) →
backend: baixa bytes da imagem →
backend: upload_product_image() → Supabase Storage →
backend: cria ProductImage (image_kind="modelo_ia") no PostgreSQL →
frontend: exibe imagem gerada + link público
```

**Custo estimado:** Cerebras = $0.00 (prompt) + Replicate ~$0.003/imagem

**Arquivo base já pronto:** `backend/app/core/context_engine.py` tem `build_image_prompt()` — já usa a fórmula profissional. Sprint 3 só precisa passar o resultado para o Replicate.

---

### Sprint 4 — Pagamento (Mercado Pago)

**Objetivo:** Checkout com split automático por vendedor.

**Tarefas:**
1. Integrar Mercado Pago Marketplace API (split por `collector_id`)
2. Adicionar campos `payment_status`, `payment_id`, `paid_at` ao model `Order`
3. Webhook `POST /api/webhooks/mercadopago` para atualizar status
4. Frontend: tela de checkout antes de confirmar pedido

**Docs:** https://www.mercadopago.com.br/developers/pt/docs/checkout-api/payment-methods/receiving-payment-by-card

---

### Sprint 5 — Deploy

**Objetivo:** Subir sistema em produção com banco gerenciado.

**Tarefas:**
1. `Dockerfile` para backend FastAPI
2. `docker-compose.yml` (backend + postgres local)
3. Deploy backend no **Railway** (free tier disponível) ou **Render**
4. PostgreSQL gerenciado: Railway Postgres ou Supabase
5. Deploy frontend no **Vercel** (free tier)
6. Configurar variáveis de ambiente em produção
7. Configurar `ALLOWED_ORIGINS` com domínio real

---

## 6. Setup do Ambiente (Local)

### Backend
```bash
cd "C:\Users\danil\OneDrive\Área de Trabalho\Projetos - IA\App de Moda\backend"
pip install -r requirements.txt

# Variáveis obrigatórias (mínimo para rodar)
export APP_SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/appmoda
export ALLOWED_ORIGINS=http://localhost:3000

# Iniciar
uvicorn app.main:app --reload --port 8000
```

Após iniciar: seed automático cria 3 empresas e estrutura do banco.

### Multi-IA (scripts)
```bash
cd "C:\Users\danil\OneDrive\Área de Trabalho\Projetos - IA\App de Moda"
pip install -r scripts/requirements.txt

# Keys (Cerebras é FREE — principal)
export CEREBRAS_API_KEY=csk-...
export GROQ_API_KEY=gsk_...
export GEMINI_API_KEY=AIzaSy...

# Verificar keys
PYTHONIOENCODING=utf-8 python scripts/check_keys.py

# Testar router (deve usar Cerebras = FREE)
PYTHONIOENCODING=utf-8 python scripts/task_runner.py --task image_prompt --product "Calça Jeans"

# Dashboard de tokens
PYTHONIOENCODING=utf-8 python scripts/token_monitor.py --all
```

---

## 7. Regras de Roteamento Multi-IA

**Sempre usar `FAST` para bulk tasks. `CRITICAL` apenas para decisões arquiteturais.**

| Tarefa | Tier | Modelo | Custo |
|--------|------|--------|-------|
| image_prompt | FAST | Cerebras qwen-3-235b | **FREE** |
| content_gen | FAST | Cerebras qwen-3-235b | **FREE** |
| classification | FAST | Cerebras qwen-3-235b | **FREE** |
| code_review | FAST | Cerebras qwen-3-235b | **FREE** |
| normalization | FAST | Cerebras qwen-3-235b | **FREE** |
| exploration | EXPLORE | Gemini 2.5 Flash | $0.0002/1K |
| architecture | CRITICAL | Claude Sonnet | $0.009/1K |
| security_review | CRITICAL | Claude Sonnet | $0.009/1K |

**Modelo completo:** `cerebras/qwen-3-235b-a22b-instruct-2507`

**Limite diário Cerebras:** 1.000.000 tokens FREE. Monitorar com:
```bash
PYTHONIOENCODING=utf-8 python scripts/token_monitor.py --alert
```

---

## 8. Usuários Seed de Teste

Criados automaticamente pelo `backend/app/core/seed.py` no startup.

| Email | Senha seed | Role |
|-------|-----------|------|
| Ver `backend/app/core/seed.py` | definida no seed | admin, lojista, fabrica, cliente |

---

## 9. Arquivos-Chave do Projeto

```
backend/
  app/
    main.py                  ← entrypoint FastAPI (CORS, lifespan, routers)
    auth/security.py         ← JWT + bcrypt + RBAC
    core/
      db.py                  ← SQLAlchemy engine + get_db()
      seed.py                ← seed inicial (3 empresas)
      context_engine.py      ← motor de IA (prompt builder + compactação)
      ai_client.py           ← generate_image_prompt, classify_product, normalize_address
    models/orm.py            ← TODOS os modelos SQLAlchemy (10 tabelas)
    routes/
      auth.py                ← login, register, admin/register
      companies.py           ← listagem e detalhe de empresas
      catalog.py             ← produtos e variantes
      marketplace.py         ← MAIOR ARQUIVO: portal, pedidos, logística

scripts/
  ai_router.py              ← roteador multi-IA (SEMPRE usar este)
  token_monitor.py          ← dashboard de consumo
  task_runner.py            ← CLI de tarefas
  check_keys.py             ← diagnóstico de keys
  token_usage.jsonl         ← log gerado automaticamente

docs/
  contexto-compactacao.json ← config de limites por tarefa para IA
  auditoria-pre-sprints-resultado.json ← auditoria completa (histórico)
  HANDOFF_ATUAL.md          ← ESTE ARQUIVO

frontend/features/mapa-empresas/
  api.ts                    ← cliente TypeScript (correto)
  PortalCentralPage.tsx     ← funcional ponta a ponta
  MapaEmpresasPage.tsx      ← CONCLUÍDO: API real + Leaflet + geolocalização
```

---

## 10. Checklist Antes de Iniciar um Sprint

- [ ] `PYTHONIOENCODING=utf-8 python scripts/check_keys.py` — confirmar Cerebras disponível
- [ ] `PYTHONIOENCODING=utf-8 python scripts/token_monitor.py` — ver consumo do dia
- [ ] Cerebras deve aparecer como TIER 1 no task_runner (custo U$0.00000)
- [ ] Backend responde em `http://localhost:8000/health`
- [ ] PostgreSQL rodando com `DATABASE_URL` setado
- [ ] `APP_SECRET_KEY` definida (servidor não inicia sem ela)

---

*Atualizado em 30/04/2026 | gerado originalmente pelo Claude Code*

