# Prompt de Handoff — App de Moda → Gemini (01/05/2026)

## Contexto do Projeto

Você está assumindo o desenvolvimento do **App de Moda**, um SaaS hiperverticalizado para o Polo de Confecções do Agreste PE (Caruaru, Santa Cruz do Capibaribe, Toritama). O projeto é um marketplace multiempresa com geração de imagens por IA.

**Pasta raiz:**
```
C:\Users\danil\OneDrive\Área de Trabalho\Projetos - IA\App de Moda\
```

---

## Estado Atual (verificado por Codex + Claude Code em 01/05/2026)

### O que está 100% pronto e funcionando

| Componente | Status | Detalhe |
|---|---|---|
| FastAPI backend | ✅ RODANDO | `http://localhost:8000`, iniciado com `python -m uvicorn app.main:app` na pasta `backend/` |
| PostgreSQL (Supabase) | ✅ CONECTADO | Session Pooler `aws-1-us-east-2.pooler.supabase.com:5432`, 11 tabelas criadas |
| Auth JWT | ✅ FUNCIONAL | `POST /api/auth/login` retorna token. User: `admin@appmoda.local` / `123456` |
| Supabase Storage | ✅ CONFIGURADO | Bucket `product-images` criado e público em `xqgmndegptevuihaazee.supabase.co` |
| Replicate API | ✅ TOKEN CONFIGURADO | `backend/.env` tem `REPLICATE_API_TOKEN` setado |
| Sprint 1 (Mapa) | ✅ CONCLUÍDO | `MapaEmpresasPage.tsx` com react-leaflet, OSM, geolocalização, filtros |
| Sprint 2 (Upload) | ✅ CONCLUÍDO | `POST /api/portal/catalog/products/{id}/images` multipart + Supabase Storage |
| Sprint 3 (IA) | ✅ CÓDIGO PRONTO | Implementado mas **não testado E2E** — precisa de validação |

### Stack técnica

- **Backend:** FastAPI 0.5.0 + SQLAlchemy + PostgreSQL + `python-dotenv` (carrega `.env` automático)
- **Frontend:** Next.js 14 + TypeScript + react-leaflet
- **Auth:** JWT (jose) + bcrypt==4.0.1 (IMPORTANTE: bcrypt 5.x é incompatível com passlib)
- **IA Imagem:** Replicate `black-forest-labs/flux-schnell` (~$0.003/imagem, aspect_ratio=3:4)
- **Roteamento multi-IA:** Cerebras FREE → Groq → Gemini → Claude (`scripts/ai_router.py`)

### Arquivos chave do Sprint 3 (já implementados)

```
backend/app/core/image_generator.py       ← generate_fashion_image() via Replicate
backend/app/core/storage.py               ← upload_product_image() via Supabase
backend/app/routes/marketplace.py         ← POST /api/portal/catalog/products/{id}/generate-image
                                          ← GET  /api/portal/catalog/products/{id}/images
frontend/features/mapa-empresas/api.ts    ← generateProductImage(), listProductImages()
frontend/features/mapa-empresas/PortalCentralPage.tsx ← botão IA + galeria
```

---

## Sua Tarefa: Validação E2E do Sprint 3

O Sprint 3 tem o código implementado mas **nunca foi testado com as credenciais reais**. Seu trabalho é fazer a validação E2E e corrigir qualquer bug encontrado.

### Pré-requisitos para iniciar

1. Iniciar o backend (se não estiver rodando):
```bash
cd "C:\Users\danil\OneDrive\Área de Trabalho\Projetos - IA\App de Moda\backend"
PYTHONIOENCODING=utf-8 python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

2. O `.env` do backend já tem todas as credenciais configuradas. Não precisa mexer.

### Fluxo E2E a validar (4 etapas sequenciais)

**Etapa 1 — Health check**
```bash
curl http://localhost:8000/health
# Esperado: {"status":"ok","version":"0.5.0"}
```

**Etapa 2 — Obter token de auth**
```bash
curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@appmoda.local","password":"123456"}'
# Salvar o access_token retornado como $TOKEN
```

**Etapa 3 — Gerar imagem com IA**
```bash
# Primeiro obter um product_id válido (seed cria produtos no startup):
curl -s http://localhost:8000/api/catalog/products \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool | grep '"id"' | head -3

# Depois chamar o endpoint de geração:
curl -s -X POST http://localhost:8000/api/portal/catalog/products/{PRODUCT_ID}/generate-image \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"image_kind": "modelo_ia"}'
# Esperado: {"message": "Imagem gerada com sucesso", "prompt_usado": "...", "image": {...}}
# Critério: image.image_url deve ser uma URL pública acessível no browser
```

**Etapa 4 — Listar imagens do produto**
```bash
curl -s http://localhost:8000/api/portal/catalog/products/{PRODUCT_ID}/images \
  -H "Authorization: Bearer $TOKEN"
# Esperado: {"product_id": "...", "count": 1, "images": [{...}]}
```

### Critérios de aceite do Sprint 3

- [ ] `generate-image` retorna HTTP 200 com `image_url` preenchida
- [ ] `image_url` abre no browser e mostra uma imagem de moda (3:4)
- [ ] Imagem está salva no Supabase Storage bucket `product-images`
- [ ] `GET /images` lista a imagem recém-gerada (count=1)
- [ ] Não há exceções no log do uvicorn durante o fluxo

---

## Bugs Conhecidos / Armadilhas

1. **bcrypt incompatível:** Usar apenas `bcrypt==4.0.1`. Se reinstalar dependências, não deixar atualizar para 5.x.

2. **DNS do banco só funciona via PowerShell/Python nativo** (não via Git Bash). Se testar scripts Python de DB, rodar via PowerShell.

3. **`python-dotenv` é carregado no `app/main.py`** — o backend lê `.env` automaticamente ao iniciar com uvicorn. Não precisa exportar variáveis manualmente.

4. **Seed cria usuários e empresas no startup** — ao reiniciar o backend, o seed é executado novamente mas com `get_or_create` (não duplica).

5. **Session Pooler (não Transaction Pooler)** — o banco usa porta 5432 do Session Pooler. Não trocar para 6543 (Transaction Pooler não suporta todas as operações do SQLAlchemy).

---

## Após Validação E2E: Próximas Tarefas (Sprint 4)

Se o Sprint 3 estiver 100% validado, iniciar o Sprint 4:

### Sprint 4 — Pagamento (Mercado Pago)

**Objetivo:** Checkout com split automático por vendedor.

**Tarefas:**
1. Integrar Mercado Pago Checkout API
2. Adicionar campos `payment_status`, `payment_id`, `paid_at` ao model `Order` em `backend/app/models/orm.py`
3. Endpoint: `POST /api/portal/orders/{id}/checkout` — cria preferência de pagamento
4. Webhook: `POST /api/webhooks/mercadopago` — atualiza status do pedido
5. Frontend: tela de confirmação antes do pedido no `PortalCentralPage.tsx`

**Docs Mercado Pago:** https://www.mercadopago.com.br/developers/pt/docs

---

## Aviso de Segurança Importante

As credenciais abaixo foram expostas em texto durante a sessão de desenvolvimento. **Rotacione-as antes do deploy em produção:**

- Senha do banco PostgreSQL (`@Olinad7891*`)
- `SUPABASE_SERVICE_ROLE_KEY` (JWT no `.env`)
- `REPLICATE_API_TOKEN` (`r8_...`)

Para rotacionar:
- Banco: Supabase Dashboard → Settings → Database → Reset database password
- Service Role: Supabase Dashboard → Settings → API → Regenerate
- Replicate: replicate.com → Account → API tokens → Delete + criar novo

Após rotacionar, atualizar `backend/.env` com os novos valores.

---

## Referências Rápidas

| O que | Onde |
|---|---|
| Handoff completo | `docs/HANDOFF_ATUAL.md` |
| Schema do banco | `backend/db/schema.sql` |
| Variáveis de ambiente | `backend/.env` (não commitado) |
| Exemplo de variáveis | `backend/.env.example` |
| Roteador multi-IA | `scripts/ai_router.py` |
| Modelos ORM | `backend/app/models/orm.py` |
| Seed de dados | `backend/app/core/seed.py` |
