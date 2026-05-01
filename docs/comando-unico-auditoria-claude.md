# Comando Único - Executar Auditoria no Claude Code

Copie e cole no Claude Code:

Leia integralmente os arquivos abaixo e execute uma auditoria completa pré-sprints com saída obrigatória em JSON usando o template docs/AUDIT_TEMPLATE.json.

Arquivos obrigatórios:
- docs/contexto-mestre-auditoria-pre-sprints.md
- docs/prompt-oficial-claude-code-auditoria.md
- docs/contexto-compactacao.md
- docs/contexto-compactacao.json
- docs/mapeamento-empresas.md
- docs/fluxo-logistico-excursao.md
- docs/finalizacao-mvp.md
- backend/api/companies-api.md
- backend/app/main.py
- backend/app/routes/*.py
- backend/app/core/*.py
- frontend/features/mapa-empresas/*.tsx
- frontend/features/mapa-empresas/api.ts

Regras:
1. Não inferir implementação ausente; marque como NAO IMPLEMENTADO.
2. Todo finding deve ter evidência de arquivo.
3. Classificar severidade: CRITICO, ALTO, MEDIO, BAIXO.
4. Entregar:
   - sumário executivo
   - findings por severidade
   - readiness matrix
   - backlog 80/20 pré-sprint
   - decisão GO/NO_GO
5. Formato final obrigatório:
- JSON válido conforme docs/AUDIT_TEMPLATE.json

Salve o resultado final em:
- docs/auditoria-pre-sprints-resultado.json
