# Sistema de IAs — App de Moda
> Grupo hierárquico de inteligências artificiais para evolução contínua do produto

---

## 1. Hierarquia de IAs

```
┌─────────────────────────────────────────────────────────┐
│          CLAUDE SONNET 4.6  (Arquiteto Sênior)          │
│  Revisor final · Decisões críticas · Validação de code  │
│  Segurança · Arquitetura · Aprovação de sprints         │
└──────────────┬─────────────────────────────────────────┘
               │ valida tudo
   ┌───────────┼────────────┬──────────────┐
   ▼           ▼            ▼              ▼
┌────────┐ ┌────────┐ ┌──────────┐ ┌──────────────┐
│ GEMINI │ │CEREBRAS│ │  GROQ    │ │   COPILOT    │
│2.5Flash│ │qwen-3- │ │(fallback)│ │ (GitHub AI)  │
│        │ │235b    │ │          │ │              │
│• Audit.│ │FREE 1M │ │• Tarefas │ │• Sugestões   │
│  segur.│ │tok/dia │ │  especí- │ │  de código   │
│• Explor│ │        │ │  ficas   │ │  no editor   │
│  code  │ │• Geraç.│ │• Fallback│ │• Completar   │
│• Pesq. │ │  rápida│ │  quando  │ │  boilerplate │
│  UX    │ │• Análise│ │  Cerebras│ │• Docstrings  │
│• Design│ │  dados │ │  lotado  │ │  e testes    │
│        │ │• Batch │ │          │ │• Revisão de  │
│        │ │  jobs  │ │          │ │  PR inline   │
└────────┘ └────────┘ └──────────┘ └──────────────┘
```

### Protocolo de trabalho
1. **Gemini / Cerebras** propõem melhorias com código e justificativa
2. **Claude** revisa: segurança, performance, coerência arquitetural
3. Claude aprova → entra no backlog "Validado"
4. Claude reprova → documentado com motivo, arquivado
5. Implementação só ocorre após aprovação explícita de Claude

---

## 2. Processo de Validação de Melhorias

```
PESQUISA (Agente Semanal)
        ↓
PROPOSTA (Gemini/Cerebras gera código + justificativa)
        ↓
REVISÃO (Claude analisa: segurança, custo, impacto)
        ↓
    ┌───┴───┐
  APROVADO  REPROVADO
    ↓           ↓
  BACKLOG    ARQUIVO
  VALIDADO   (docs/melhorias-reprovadas.md)
    ↓
SPRINT (implementação)
    ↓
TESTE EM STAGING
    ↓
DEPLOY EM PRODUÇÃO
```

---

## 3. Backlog de Melhorias — Priorizado

### SPRINT A — UI/UX Redesign (PRIORIDADE MÁXIMA)
> Impacto: Alto | Custo: Baixo | IA responsável: Gemini

| # | Melhoria | Descrição | Status |
|---|---|---|---|
| A1 | Redesign cards de produto | Imagem 3:4, preço destacado, badge "Menor preço", rating em estrelas | 🔍 A validar |
| A2 | Busca com resultados em tempo real | Debounce 300ms + skeleton loading | 🔍 A validar |
| A3 | Filtros contextuais com opções pré-definidas | Por categoria: tipos completos (10+/cat), 20 cores, 8–9 tecidos por categoria, tamanhos por produto | ✅ Implementado |
| A4 | Tela de comparação de preços | Side-by-side do mesmo produto em lojas diferentes | 🔍 A validar |
| A5 | Header da loja com capa e foto | Banner + logo da empresa na página /loja/[id] | 🔍 A validar |
| A6 | Modo escuro | CSS variables para tema dark/light | 🔍 A validar |
| A7 | Filtros em chips visuais (próximo passo do A3) | Transformar selects em chips clicáveis com scroll horizontal mobile-first | 🔍 A validar |

### SPRINT B — Motor de Comparação de Preços
> Impacto: Alto | Custo: Médio | IA responsável: Cerebras + Claude

| # | Melhoria | Descrição | Status |
|---|---|---|---|
| B1 | Endpoint de comparação | GET /api/portal/compare?category=camisa&city=Caruaru | 🔍 A validar |
| B2 | Agrupamento por similaridade | Agrupar produtos da mesma categoria entre lojas diferentes | 🔍 A validar |
| B3 | Ordenação por preço | Listagem unificada ordenada pelo menor preço | 🔍 A validar |
| B4 | Widget "Loja mais barata" | Destaque na busca mostrando qual loja tem o menor preço daquela categoria | 🔍 A validar |

### SPRINT C — Sistema de Avaliações
> Impacto: Alto | Custo: Médio | IA responsável: Cerebras + Claude

| # | Melhoria | Descrição | Status |
|---|---|---|---|
| C1 | Tabela store_ratings no DB | company_id, customer_whatsapp, score 1–5, comment, created_at | 🔍 A validar |
| C2 | API de avaliações | POST /portal/ratings · GET /portal/companies/{id}/ratings | 🔍 A validar |
| C3 | Exibição de rating | Estrelas na card da loja e na vitrine /loja/[id] | 🔍 A validar |
| C4 | Ranking de lojas | GET /portal/ranking?city=Caruaru — ordenado por nota média | 🔍 A validar |

### SPRINT D — IA de Recomendação de Compra
> Impacto: Muito Alto | Custo: Alto | IA responsável: Claude (decisão), Cerebras (execução)

| # | Melhoria | Descrição | Status |
|---|---|---|---|
| D1 | Prompt de recomendação | IA analisa rating + preço + localização e sugere melhor loja | 🔍 A validar |
| D2 | Endpoint /portal/recommend | Recebe lista de produtos e retorna ranking de lojas com justificativa | 🔍 A validar |
| D3 | Widget de sugestão no carrinho | "A loja X tem a melhor avaliação para estes produtos" | 🔍 A validar |
| D4 | Histórico de compras por cliente | Permite IA aprender preferências do cliente | 🔍 A validar |

### SPRINT E — Carrinho Multi-loja Otimizado
> Impacto: Alto | Custo: Médio | IA responsável: Gemini + Claude

| # | Melhoria | Descrição | Status |
|---|---|---|---|
| E1 | Split automático por loja | Divide o carrinho automaticamente por fabricante | 🔍 A validar |
| E2 | Resumo por loja no checkout | Subtotal por loja antes de confirmar | 🔍 A validar |
| E3 | WhatsApp em lote | Botão único que abre WA para cada loja com seu pedido específico | 🔍 A validar |
| E4 | Status unificado de pedidos | Dashboard do cliente com todos os pedidos consolidados | 🔍 A validar |

### SPRINT F — Performance e Segurança
> Impacto: Alto | Custo: Baixo | IA responsável: Gemini (auditoria)

| # | Melhoria | Descrição | Status |
|---|---|---|---|
| F1 | Rate limiting na busca pública | 60 req/min por IP no /portal/search | 🔍 A validar |
| F2 | Cache Redis nas buscas | TTL 60s para buscas idênticas | 🔍 A validar |
| F3 | Paginação cursor-based | Substituir offset por cursor para performance em escala | 🔍 A validar |
| F4 | Compressão de imagens no upload | Redimensionar para max 800px e converter para WebP | 🔍 A validar |
| F5 | Monitoramento com Sentry | Frontend + Backend com alertas automáticos | 🔍 A validar |

---

### SPRINT G — Benchmark VendiZap (Novas Funcionalidades)
> Impacto: Muito Alto | Custo: Médio-Alto | Fonte: Análise VendiZap 01/05/2026

#### G-Design — Landing Page & UX
| # | Melhoria | Descrição | Status |
|---|---|---|---|
| G1 | Landing page profissional | Hero + stats ("X lojas, Y pedidos/semana") + Como Funciona (4 passos) + Depoimentos | 🔍 A validar |
| G2 | Design aspiracional moda | Visual fashion-first, paleta moderna, tipografia premium vs. design genérico atual | 🔍 A validar |
| G3 | Filtros em chips visuais | Substituir selects por chips clicáveis com scroll horizontal (mobile-first) | 🔍 A validar |
| G4 | Cards de produto ricos | Imagem 3:4 + hover zoom + badge de menor preço + estrelas de rating | 🔍 A validar |
| G5 | Vitrine da loja profissional | Banner + logo + coleções em grid + botão "Falar no WhatsApp" fixo | 🔍 A validar |

#### G-Monetização — Planos e Negócio
| # | Melhoria | Descrição | Status |
|---|---|---|---|
| G6 | Página de Planos e Preços | 3 planos (Essencial/Profissional/Empresarial), sem taxas sobre vendas, trial 7 dias | 🔍 A validar |
| G7 | Domínio customizado por loja | /loja/minha-marca → minha-marca.appmoda.com.br | 🔍 A validar |
| G8 | Cupons e descontos | Lojista cria cupom de desconto com código, validade e limite de uso | 🔍 A validar |
| G9 | Programa de afiliados | Representantes ganham comissão por indicar lojas — dashboard de afiliados | 🔍 A validar |
| G10 | Cálculo de frete automático | Integração Melhor Envio / SuperFrete / Correios com cálculo por CEP | 🔍 A validar |

#### G-Analytics — Painel do Lojista
| # | Melhoria | Descrição | Status |
|---|---|---|---|
| G11 | Dashboard analytics | Vendas, produtos mais vistos, conversão, ticket médio — disponível em todos os planos | 🔍 A validar |
| G12 | Recuperação de carrinhos abandonados | Alerta via WhatsApp para cliente que não finalizou pedido | 🔍 A validar |
| G13 | Histórico de pedidos do cliente | Área do cliente com todos os pedidos e status em tempo real | 🔍 A validar |
| G14 | Relatório de estoque | Alerta quando variante atinge estoque mínimo configurável | 🔍 A validar |

#### G-Integrações — Redes Sociais e ERP
| # | Melhoria | Descrição | Status |
|---|---|---|---|
| G15 | Instagram Shopping | Feed da loja sincronizado com catálogo; tags de produto nas fotos | 🔍 A validar |
| G16 | WhatsApp Business API | Notificações automáticas de pedido, entrega e avaliação pós-compra | 🔍 A validar |
| G17 | Integração ERP | API aberta para sincronizar com Bling, Tiny, TOTVS e outros ERPs do setor | 🔍 A validar |
| G18 | PWA / App Nativo | Progressive Web App com notificações push (diferencial: VendiZap não tem) | 🔍 A validar |

---

## 4. Agente de Pesquisa Semanal

**Frequência:** Toda segunda-feira às 9h (horário de Brasília)
**Executor:** Claude Code (com WebSearch)
**Output:** `docs/pesquisa/YYYY-MM-DD.md`

### Temas de pesquisa
1. Tendências UX em marketplaces de moda B2B (Brasil + global)
2. Novidades Next.js / React — performance e componentes
3. Melhores práticas FastAPI — segurança e escalabilidade
4. Inovações em sistemas de comparação de preços
5. Aplicativos concorrentes: VendiZap, Bling, Olist, Bom de Fio
6. Feedback de usuários em marketplaces similares (App Store/Play Store reviews)

### Formato do relatório semanal
```markdown
## Pesquisa Semanal — [DATA]

### Destaques da semana
- ...

### Sugestões de melhoria identificadas
| Sugestão | Fonte | Impacto estimado | Recomendação |
|---|---|---|---|

### Itens para revisão de Claude
- ...

### Descartados (motivo)
- ...
```

---

## 5. Passo a Passo de Implantação por Sprint

### Como executar cada sprint
```
1. Claude dispara Gemini com prompt de auditoria do sprint
2. Gemini retorna código + justificativa
3. Claude revisa e marca como APROVADO/REPROVADO
4. Aprovado → Claude implementa com Edit/Write tools
5. Build local: npm run build (frontend) / uvicorn (backend)
6. Push para GitHub → Railway + Vercel auto-deploy
7. Teste em produção via curl + teste manual no celular
8. Marcar sprint como CONCLUÍDO
```

### Critérios de aprovação (checklist Claude)
- [ ] Não introduz vulnerabilidades (SQL injection, XSS, IDOR)
- [ ] Não quebra rotas existentes
- [ ] Build passa localmente sem erros
- [ ] Performance não piora (lighthouse score)
- [ ] Custo de API não aumenta desproporcionalmente
- [ ] Mobile-first (funciona em tela 375px)
- [ ] LGPD: nenhum dado sensível exposto sem consentimento

---

## 6. Cronograma Sugerido

| Semana | Sprint | Responsável |
|---|---|---|
| Semana 1 | Sprint A (UI/UX) | Gemini propõe → Claude revisa → Claude implementa |
| Semana 2 | Sprint B (Comparação de preços) | Cerebras propõe → Claude revisa → Claude implementa |
| Semana 3 | Sprint C (Avaliações) | Cerebras propõe → Claude revisa → Claude implementa |
| Semana 4 | Sprint D (IA Recomendação) | Claude arquiteta → Cerebras gera → Claude revisa |
| Semana 5 | Sprint E (Carrinho multi-loja) | Gemini propõe → Claude revisa → Claude implementa |
| Semana 6 | Sprint F (Performance) | Gemini audita → Claude implementa correções |
| Contínuo | Pesquisa semanal | Agente automático → Claude valida |
