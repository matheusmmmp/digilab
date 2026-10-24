# Índice: onde está cada coisa, em níveis

Para uma sessão nova (Claude Code, Codex, ChatGPT Work ou outra) achar o contexto sem ler tudo. Só links: o conteúdo mora nos arquivos
citados. Status: PROPOSTO (`docs/TAREFA_V2_INFRA_MULTIAGENTE.md`).

## Nível 0: as regras (sempre)

- [`CLAUDE.md`](../CLAUDE.md): as regras não negociáveis, o método de pesquisa, o trabalho em paralelo e a arquitetura.
- [`AGENTS.md`](../AGENTS.md): por onde começa um agente que não é o Claude Code, e o que ele pode fazer.

## Nível 1: onde o projeto está (no começo de cada sessão)

- [`PAINEL_V2.md`](PAINEL_V2.md): o estado da V2 em uma página (marcos, runs, decisões abertas, riscos), curado pelo coordenador.
- [`ESTADO_ATUAL.md`](ESTADO_ATUAL.md): o índice derivado das tarefas, dos planos e dos últimos desvios. Gerado por
  `tools/gerar_estado_atual.py`; não é fonte.

- **A direção de 2026-10-24** (o produto primeiro, o DigiBrain modular, o A como baseline e fallback):
  - [`PRODUTO_VISAO.md`](PRODUTO_VISAO.md): a visão, o escopo e o MVP;
  - [`ARQUITETURA_DIGIBRAIN_MODULAR.md`](ARQUITETURA_DIGIBRAIN_MODULAR.md): os módulos, as rotas versionadas, a literatura, DM-1 a DM-9;
  - [`AUDITORIA_V2_PRODUTO_MODULAR.md`](AUDITORIA_V2_PRODUTO_MODULAR.md): o estado real do código, dos PRs e dos documentos.
- **As tarefas da direção nova:** [`TAREFA_V2_MVP_MUNDO_PRODUTO.md`](TAREFA_V2_MVP_MUNDO_PRODUTO.md),
  [`TAREFA_V2_DIGIBRAIN_MODULAR_ESPEC.md`](TAREFA_V2_DIGIBRAIN_MODULAR_ESPEC.md),
  [`TAREFA_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md`](TAREFA_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md),
  [`TAREFA_V2_MEMORIA_AUTOBIOGRAFICA.md`](TAREFA_V2_MEMORIA_AUTOBIOGRAFICA.md),
  [`TAREFA_V2_DIGIBRAIN_MODULAR_PRODUTO.md`](TAREFA_V2_DIGIBRAIN_MODULAR_PRODUTO.md),
  [`TAREFA_V2_CEREBRO_A_BASELINE.md`](TAREFA_V2_CEREBRO_A_BASELINE.md),
  [`TAREFA_V2_FASES_POSTERIORES.md`](TAREFA_V2_FASES_POSTERIORES.md).
- **Onde um documento disser "a web roda um DigiBrain, o A" ou "o M6 escolheu o A",** vale a decisão de 2026-10-24: essas duas
  decisões estão SUPERADAS. Os documentos principais têm uma nota no topo. Ficaram **datados, sem nota**, e são da rodada de saúde:
  - `docs/research/digibrain/synthesis/brain_comparison.md`, `open_questions.md` e `sources/nornbrain.md`;
  - `docs/futuro/decodificador_conceitos.md`, `paladar.md`, `connectome_cerebro_a.md`;
  - `docs/DECISAO_PRODUTO_SEM_ELOGIO_BRONCA.md`, `TAREFA_V2_W_PLANO_PORTE.md`, `TAREFA_V2_PET_QUE_PENSA.md` (o "v11 pausado"),
    `TAREFA_V2_DOIS_PETS.md`, `TAREFA_V2_CORPO_DRIVES.md` (seção 15), `V2_INVENTARIO_JOGO.md` e `MAPA_REPOSITORIO.md`.

## Nível 2: a frente em que se vai trabalhar

| tipo de informação | onde mora |
|---|---|
| funcionalidade implementada | o código da `main` e os testes; o mapa arquivo a arquivo em [`MAPA_REPOSITORIO.md`](MAPA_REPOSITORIO.md) |
| decisão aprovada | a seção 3 do [`PAINEL_V2.md`](PAINEL_V2.md), as "decisões que valem" do `CLAUDE.md`, a seção de decisões de cada tarefa, o [registro de desvios](REGISTRO_DESVIOS.md) |
| hipótese científica | [`PLANO_V2_PESQUISA.md`](PLANO_V2_PESQUISA.md), [`PREDICOES_V2.md`](PREDICOES_V2.md) |
| proposta ainda não aprovada | [`futuro/`](futuro/), as tarefas e os campos com status PROPOSTO |
| experimento planejado | `PLANO_ANALISE_V2_*.md` (commitado antes da run) |
| resultado observado | `RESULTADO_V2_*.md` e os artefatos `artifacts_*/` que eles citam |
| problema conhecido | a seção 4 (riscos) do [`PAINEL_V2.md`](PAINEL_V2.md) e o [registro de desvios](REGISTRO_DESVIOS.md) |
| próxima tarefa | a seção 3 do [`PAINEL_V2.md`](PAINEL_V2.md) e a seção 8 do [`ROADMAP_V2.md`](ROADMAP_V2.md) |
| tarefa de uma frente | `TAREFA_V2_<FRENTE>.md`, pelo [modelo](modelos/TAREFA_V2_MODELO.md) |
| literatura verificada | [`referencias/`](referencias/) e as regras em [`REGRAS_CITACAO_DIGILAB.md`](referencias/REGRAS_CITACAO_DIGILAB.md) |

## Nível 3: história e detalhe (só quando a frente pedir)

- [`historico/LEIA.md`](historico/LEIA.md): o que cada etapa construiu (o resumo antigo do `CLAUDE.md`, seção a seção).
- [`V2_TRABALHO_PARALELO.md`](V2_TRABALHO_PARALELO.md): os papéis de coordenador e worker, as worktrees, as sementes e a GPU.
- [`infra/`](infra/): esta infraestrutura (a matriz de capacidades, a auditoria, o guia operacional, o teste do ChatGPT Work).

- [`TAREFA_V2_V3.md`](TAREFA_V2_V3.md): handoff para investigar o espaço de ações e oportunidades de escolha do DigiBrain V3.
- [`TAREFA_V2_V3_CREDITO_CANAL.md`](TAREFA_V2_V3_CREDITO_CANAL.md): a V3-9, o crédito do "querer" por canal até o alvo (o desenho, PROPOSTO).
- [`TAREFA_V2_V3_COMPETICAO.md`](TAREFA_V2_V3_COMPETICAO.md): a V3-3/V3-4, a competição entre as regras urgentes (o desenho, PROPOSTO).
