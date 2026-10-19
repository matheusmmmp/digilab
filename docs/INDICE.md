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
