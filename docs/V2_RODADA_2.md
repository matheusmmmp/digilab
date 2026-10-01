# V2 — marco da rodada 2 (2026-10-01)

Coordenador: chat "Principais jogos Digimon com diálogo". Divisão da rodada 2 em `docs/V2_RODADA_1.md`.

## O que a rodada entregou

| chat | frente | PR | estado | resultado (artefato) |
|---|---|---|---|---|
| A | F0-LIMPEZA | #112 | **mesclado** | `Config.limiar_privacao` passa a ser lido (0,15, sem mudar vida nenhuma); textos corrigidos |
| A | A1-BOLA, desenho | #113 | aberto, só documento | bola como sub-decisão de brincar; efeito só no humor; sem rng nova; bola sozinha antes da L1 (aguarda aprovação) |
| B | L1-DECISAO | — | plano rev. 2 e código commitados, sem run, sem PR | `docs/PLANO_ANALISE_V2_L1.md` (branch `v2-l1-decisao`) |
| C | F0-VINCULO-NOVO | #114 | aberto, **conflito** com a `main`, suíte completa não rodada | GATE PASSA: atencioso − aleatório no vínculo +0,171 [+0,046; +0,280] (`artifacts_v2_vinculo_novo/validacao/resumo.json`); pets v10 |
| D | GPU-ESTILO | #115 | aberto, **conflito**, suíte completa não rodada | estilo em português: 0/30 rejeitadas (`artifacts_voz/estilo_portugues/resumo.json`); comando com estilo PASSA, rodada 4 (`artifacts_fala_livre/comando/rodada4_estilo/resumo.json`) |

Documentos do coordenador nesta rodada: `DEFINICOES_V2.md` (#110, #111, mesclados), `ROADMAP_V2.md` (#116),
`ARQUITETURA_V2_VALIDACAO.md` (#117), `docs/research/digibrain/` (#118).

## Decisões do Matheus na rodada

- D1–D11 aprovadas como recomendadas.
- Frutas, gosto hedônico e vício são a alavanca depois da bola.
- **Pergunta maior** proposta: plasticidade na vida × predisposição herdada, por fonte de plasticidade.
- Arquitetura com o dono informante e o mundo validando.
- **Pesquisa no Python, um DigiBrain na web.**

## O que ficou pendente

- Merge de #113, #114, #115 (os dois últimos depois de resolver o conflito e rodar a suíte).
- Referendo de G3–G6; decisões M1–M9 do `ROADMAP_V2.md`.
- Leituras humanas: `revisao.csv` da moldura; avaliações cegas da fala livre e da voz.
- Claude Science: prompts 09 e 10 (`docs\digibrain\integration\`), e a verificação das fontes CORPUS.

## Rodada 3 (divisão)

| chat | frente | tarefa | começa quando |
|---|---|---|---|
| A | A1-BOLA, implementação | `docs/TAREFA_V2_A1_BOLA_IMPL.md` | #113 aprovado e mesclado |
| B | L1-DECISAO (segue) | `docs/TAREFA_V2_L1_DECISAO.md` | já; validação só depois do referendo |
| C | FRUTAS-DEFINICOES | `docs/TAREFA_V2_FRUTAS_DEFINICOES.md` | #114 resolvido (o C fecha o próprio conflito antes) |
| D | BANCADA | `docs/TAREFA_V2_BANCADA.md` | #115 resolvido (o D fecha o próprio conflito antes) |

Reservas da rodada 3 (fechadas): A1 calibração 6101…6505, validação 7101…7505. As outras faixas do `ROADMAP_V2.md`, seção 6,
ficam reservadas e se fecham na tarefa de cada nó.
