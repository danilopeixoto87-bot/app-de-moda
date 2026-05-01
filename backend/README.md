# Backend — App de Moda (Polo PE)

## Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

## Variáveis de ambiente

Copie `.env.example` para `.env` e preencha:

```bash
copy .env.example .env
```

**APP_SECRET_KEY é obrigatória** — o servidor não inicia sem ela:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Banco de dados

Crie o banco no PostgreSQL:

```sql
CREATE DATABASE app_moda;
```

As tabelas são criadas automaticamente no startup via SQLAlchemy.
Para carregar seed manualmente: `python seed/run_seed.py`

## Rodar em desenvolvimento

```bash
set APP_SECRET_KEY=sua-chave-aqui   # Windows CMD
uvicorn app.main:app --reload --port 8000
```

## Endpoints principais

| Método | Rota | Auth | Descrição |
|--------|------|------|-----------|
| POST | /api/auth/login | — | Login (rate limit: 10/min por IP) |
| POST | /api/auth/register | — | Auto-registro (somente perfil cliente) |
| POST | /api/auth/admin/register | admin | Registro com qualquer perfil |
| GET | /api/companies | — | Listar empresas (paginado, ordenável por distância) |
| GET | /api/catalog/products | — | Listar produtos (paginado) |
| GET | /api/catalog/variants | — | Listar variantes (paginado) |
| GET | /api/portal/search | — | Busca unificada |
| POST | /api/portal/catalog/products/{id}/images | lojista/fabrica/admin | Upload de imagem do produto (Supabase Storage) |
| POST | /api/portal/orders | cliente/lojista/admin | Criar pedido |
| GET | /api/portal/orders | lojista/fabrica/admin | Listar pedidos (paginado) |
| PATCH | /api/portal/orders/logistics/status | lojista/fabrica/admin | Atualizar status logístico |
| POST | /api/portal/logistics/excursion-carriers | lojista/fabrica/admin | Cadastrar transportador |
| GET | /api/portal/logistics/excursion-carriers | — | Listar transportadores |
| GET | /health | — | Health check |

Documentação interativa: http://localhost:8000/docs
