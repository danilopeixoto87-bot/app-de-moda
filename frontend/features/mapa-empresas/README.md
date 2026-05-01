# Frontend - Portal Central

## Arquivos
- `features/mapa-empresas/PortalCentralPage.tsx`
- `features/mapa-empresas/api.ts`

## Fluxo implementado
1. Login (`/api/auth/login`) para obter token.
2. Pesquisa centralizada com filtros de vestuario.
3. Geracao de prompt de imagem autenticada.
4. Selecao de produtos.
5. Criacao de pedido com logistica:
- `retirada_em_loco`
- `entrega_local`
- `excursao`
6. Se modo `excursao`:
- lista de transportadores por cidade
- selecao de transportador
- horario solicitado para coleta
7. Exibicao de timeline logistica e contatos WhatsApp.

## Credenciais seed (ambiente dev)
- `cliente@appmoda.local` / `123456`
- `lojista@appmoda.local` / `123456`
- `fabrica@appmoda.local` / `123456`
- `admin@appmoda.local` / `123456`

## Dependencia
Backend em `http://localhost:8000`.
