# Fluxo Logistico - Excursao

## Objetivo
Permitir que o cliente escolha retirada local ou entrega com excursionista, com horario limite de separacao, coleta e entrega previsivel de baixo custo.

## Fluxo operacional
1. Lojista/fabrica cadastra transportador de excursao com rota, horario de corte e custo base.
2. Cliente cria pedido e escolhe modo logistico:
- retirada_em_loco
- entrega_local
- excursao
3. Sistema abre o pedido com status `pedido_recebido` e `em_separacao`.
4. Loja/fabrica separa itens ate horario limite.
5. Transportador coleta e status passa para:
- `pronto_para_coleta`
- `coletado_excursao`
- `em_transito`
- `entregue`

## Beneficios
- previsibilidade de prazo
- baixo custo de entrega por rota compartilhada
- seguranca operacional com trilha de status
- melhor experiencia para cliente final

## Status padrao
- pedido_recebido
- em_separacao
- pronto_para_coleta
- coletado_excursao
- em_transito
- entregue
- cancelado
