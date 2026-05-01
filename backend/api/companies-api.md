# API - Mapa, Catalogo, Portal e Logistica de Excursao

## Autenticacao
- `POST /api/auth/login`

## Cadastro centralizado
- `POST /api/portal/companies`
- `POST /api/portal/catalog/products`
- `POST /api/portal/catalog/variants`

## Pesquisa centralizada
- `GET /api/portal/search`

## Logistica de excursao
- `POST /api/portal/logistics/excursion-carriers`
- `GET /api/portal/logistics/excursion-carriers`
- `PATCH /api/portal/orders/logistics/status`

## Pedido online
- `POST /api/portal/orders`

Campo obrigatorio no pedido:
```json
"logistics": {
  "mode": "retirada_em_loco|entrega_local|excursao",
  "delivery_address": "...",
  "delivery_city": "...",
  "local_delivery_fee": 0,
  "excursion_carrier_id": "exc-0001",
  "requested_pickup_at": "2026-05-01T16:00:00Z"
}
```

Retorno do pedido inclui:
- `carrier_contact` (quando modo = excursao)
- `logistics_timeline`
- `logistics.max_delivery_hours`
- `logistics.estimated_excursion_fee`

## Contato e IA
- `POST /api/portal/contacts/multi`
- `POST /api/portal/context/compact`
- `POST /api/portal/image/prompt`
