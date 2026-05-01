# Contexto Mestre - Auditoria Pré-Sprints (Claude Code)

## Objetivo
Executar auditoria técnica e funcional completa do sistema antes do início dos sprints, para identificar gaps críticos, riscos de implementação e prioridade real de execução.

## Escopo do produto
SaaS para Polo de Confecções (Caruaru, Santa Cruz do Capibaribe, Toritama) com:
- Marketplace multiempresa
- Catálogo de vestuário (tamanho, cor, tecido)
- Pedido online
- Logística (retirada, entrega local, excursão)
- Integração operacional via WhatsApp
- Motor de contexto/compactação para IA
- Prompt builder para imagem
- Frontend mobile-first

## Estado atual (resumo)
- Backend FastAPI com rotas de empresas, catálogo e portal.
- Fluxo de pedido com timeline logística.
- Cadastro e consulta de transportador de excursão.
- JWT + perfis de acesso.
- Frontend com busca centralizada e criação de pedido.
- Documentação parcial do contrato de API.
- Dados ainda majoritariamente em memória em partes do sistema.

## Questões obrigatórias da auditoria
1. O sistema está consistente entre frontend e backend (payloads, auth, contratos)?
2. Quais endpoints já estão prontos para produção e quais estão apenas MVP?
3. Quais pontos ainda estão em memória e precisam migração para PostgreSQL?
4. Existem falhas de segurança, validação de input e controle de acesso?
5. O fluxo de logística de excursão está auditável de ponta a ponta?
6. Quais cenários quebram o checkout/pedido/logística?
7. O app já suporta piloto real com 10-20 clientes sem risco operacional grave?

## Critérios de severidade
- CRITICO: bloqueia operação ou gera risco financeiro/jurídico.
- ALTO: impacto relevante em conversão, segurança ou estabilidade.
- MEDIO: degrada UX/eficiência, mas existe contorno.
- BAIXO: melhoria incremental.

## Entregáveis obrigatórios da auditoria
1. Mapa de arquitetura atual (texto objetivo).
2. Lista de findings por severidade com:
- arquivo
- rota/módulo
- risco
- recomendação prática
3. Matriz "Pronto para Sprint" por domínio:
- Produto
- Backend
- Frontend
- Segurança
- Dados
- Logística
- Pagamento
4. Backlog priorizado 80/20 pré-sprint.
5. Go/No-Go para iniciar Sprint 1.

## Regra de saída
- Sem respostas genéricas.
- Cada conclusão deve apontar evidência em código/arquivo.
- Se algo não estiver implementado: marcar como "NAO IMPLEMENTADO".
