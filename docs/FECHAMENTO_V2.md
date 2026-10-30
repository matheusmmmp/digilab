# FECHAMENTO DA V2: o estado de cada tarefa, marco e frente (2026-10-30)

Escrito pelo Gerente da transição V2 → V3 (`docs/TAREFA_V2_TRANSICAO_V3.md`), sobre a `main` em `b3643bb` (PR #475). As V3-D1 a
V3-D8 foram DECIDIDAS pelo Matheus em 2026-10-30, todas pela recomendação (`docs/PLANO_V3.md`, seção 7). As marcas valem com elas.

**Regras desta tabela:**
- cada linha diz o resultado em uma linha e o documento ou o PR de onde ele vem. Nenhum número entra sem essa origem;
- a coluna "status declarado" é a linha `Status:` do arquivo, como está escrita. Muitas tarefas dizem ABERTA depois de entregues
  (`docs/ESTADO_ATUAL.md`, seção 1); a marca é a leitura do Gerente, não uma edição do arquivo;
- "entregue (o código na `main`)" marca as tarefas de código do começo da V2 (2026-10-01 a 2026-10-06) cujo código está na `main` e
  foi usado pelas runs seguintes; o Gerente não releu cada uma delas por inteiro;
- nenhum documento da V2 é editado, renomeado ou movido por este fechamento (V3-D5).

| marca | o que significa |
|---|---|
| **ENCERRADA** | o resultado fica registrado como está: positivo, negativo, inconclusivo ou "entregue" |
| **HERDADA (trilha)** | continua na V3, na trilha C (cérebro), L (layout) ou B (batalha), sem ser reaberta como tarefa nova (V3-D4) |
| **ADIADA** | vai para o backlog da V3 (`docs/PLANO_V3.md`, seção 5), com o motivo |
| **ARQUIVADA** | sem continuação |

## 0. A contagem

| marca | tarefas (seção 2) | marcos e frentes (seção 1) | total |
|---|---|---|---|
| ENCERRADA | 86 | 14 | 100 |
| HERDADA | 9 | 4 | 13 |
| ADIADA | 9 | 12 | 21 |
| ARQUIVADA | 0 | 1 | 1 |
| **total** | **104** | **31** | **135** |

**PRs abertos na data:** nenhum (`gh pr list --state open`, 2026-10-30). **Frentes em voo sem PR** (trabalho na worktree, visto em
2026-10-30): a M7 do layout (`v2-layout-fecho`, mudanças não commitadas) e a rodada 2 do combate (`v2-combate-tr-r2-formas`, quatro
commits à frente da `main`: as DR2-1 a DR2-6 decididas, as faixas 72101…72505 e 74101…74505 e a fase R2-0). As duas seguem nas sessões
delas e entram na V3 como L1 e B1.

## 1. Marcos, frentes e decisões da V2

### 1.1 O que já estava decidido (só se registra)

| item | marca | o resultado em uma linha | de onde vem |
|---|---|---|---|
| a pergunta do efeito do dono | ENCERRADA | o dono pesa pelo cuidado, não pelo ensino; só se reabre com pergunta nova sobre o aprendiz | `docs/LEITURA_CONSOLIDADA_DONO.md` |
| o bandit | ARQUIVADA | congelado; só reproduz a v1 | `CLAUDE.md`, "Decisões que valem" |
| a L-2 do longe (intenção suspensa no cochilo) | ENCERRADA | negativa: C1 e C4 falham, C2 e C3 passam; fechada pela P-1, LP-2 e LP-3 do Matheus | PR #454, PR #455 |
| a V3-9 (o crédito por canal) | ENCERRADA | parada na G0-PODE-MUDAR, que não passa | `docs/TAREFA_V2_V3_CREDITO_CANAL.md`; PR #376 |
| a P4 (o A com o planejador no mundo 3D) | ADIADA | em pausa pela DM-8: o contrato do motor fica, o piloto e a validação do A não rodam | `docs/AUDITORIA_V2_PRODUTO_MODULAR.md`, seção 9; PR #395 |
| o Gate I com o A | ADIADA | em pausa pela DM-8; os critérios servem ao pet modular; a GI-1 ("ao redor do A") está superada | `docs/futuro/gate_integracao_pet.md`; `docs/PAINEL_V2.md`, seção 1 |

### 1.2 Os marcos J, W, MVP e o modular

| marco | marca | o resultado em uma linha | de onde vem |
|---|---|---|---|
| J1 mundo físico | ENCERRADA | validado, negativo: o P1 perde do instinto, e o alvo aprendido atrapalha (#296) | `docs/RESULTADO_V2_VALIDACAO_MUNDO.md`; `docs/RESULTADO_V2_VALIDACAO_MUNDO_ALVO.md` |
| J2 corpo químico | ADIADA | código pronto (etapas 1 a 8); a calibração fecha só com o passo 0 (#293); a validação não rodou. Motivo: a calibração final espera a estrutura completa | `docs/RESULTADO_V2_CALIBRACAO_CORPO.md`, adendo 5 |
| J3 sem elogio e bronca | ENCERRADA | feito na pesquisa (os gestos no corpo e no cérebro); no produto, numa versão de pet futura | `docs/DECISAO_PRODUTO_SEM_ELOGIO_BRONCA.md` |
| J4 banheiro | ADIADA | código pronto; 14 % a 21 % dos alívios dentro na fumaça (#272); nada rodou. Motivo: as saídas estão sem decisão até haver dado | `docs/PLANO_ANALISE_V2_BANHEIRO.md`, seção 7 |
| J5 pet que pensa, a revalorização (T1) | ENCERRADA | o G-T1 passa (#370); o Gate C aprovado em parte (2026-10-21); o rótulo "pensa" não vale | `docs/RESULTADO_V2_VALIDACAO_PET_QUE_PENSA_ADENDO8.md` |
| J5, a busca (T2) | ADIADA | inconclusivo por premissa. Motivo: espera um plano próprio, sem tarefa | `docs/PAINEL_V2.md`, seção 3 |
| J6 ego (a rede de si) | ADIADA | etapas 0 a 2 e a 2b na `main`; faltam a bancada e as etapas 3 a 6. Motivo: fora das três trilhas | `docs/TAREFA_V2_REDE_DE_SI.md` |
| J6a livre × condicionado | ENCERRADA | decidido (E-11); entra com a etapa 4 do ego | `docs/futuro/ego_existencia.md` |
| J7 dois pets | ADIADA | degrau 1 pronto no código; inconclusivo por premissa até um pet aprender no mundo físico. Vai com a R7 (a perspectiva dos episódios trocados) | `docs/PLANO_ANALISE_V2_DOIS_PETS.md`, adendos 1.2 e 1.3 |
| J8 cognição social | ADIADA | ideia; depende do J7 | `docs/futuro/cognicao_social.md` |
| J9 ego social | ADIADA | ideia; depende do J6 e do J8 | `docs/futuro/ego_existencia.md` |
| J10 órgãos e hormônios | ADIADA | adiado (D-5, D-6), SEM FONTE primária. Vai com a R7 (os hormônios pelo desenho de Khan e Cañamero, a verificar na C0) | `docs/DEFINICOES_CORPO_V2.md` |
| W porte do cérebro A (v11) | ENCERRADA | entregue (etapas 1 a 5 e o painel DigiBrain); o A fica no jogo para os v11 e como fallback | `docs/TAREFA_V2_W_PORTE_CEREBRO_A.md`, seções 9 a 18 |
| connectome do cérebro A | ENCERRADA | ferramenta de pesquisa (#321), fora do jogo (CN-1 a CN-9) | `docs/futuro/connectome_cerebro_a.md` |
| mundo 3D, Gates A e B | ENCERRADA | aprovados em 2026-10-19 com ressalvas | `docs/TAREFA_V2_WORLD_POC_01.md`; `docs/TAREFA_V2_WORLD_POC_02.md` |
| MVP, o mundo no jogo | ENCERRADA | na `main` (#401, #403, #404); a ressalva: o A vai pouco à comida | `docs/TAREFA_V2_MVP_MUNDO_PRODUTO.md`, seção 9 |
| DigiBrain modular: espec e protótipo | HERDADA (C) | a espec aprovada na direção (#407); a avaliação (#420) falha o G-MVP; a reavaliação (#432) dá 0,808 [0,791; 0,826] por episódio e 0,405 por ração, só estimativa | `docs/PAINEL_V2.md`, seção 1; `docs/RESULTADO_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md` |
| o hábito (o P2 ao contrário) | HERDADA (C) | "longe primeiro, hábito depois" (Matheus); vira a C2 com o braço de crédito na intenção | PR #455; `docs/PROPOSTA_LONGE_DIGIBRAIN_MODULAR.md`, seção 6 |
| o jogo web: layout habitat e tema dos menus | HERDADA (L) | M0 a M6 e T0 na `main`; M7 em voo | `docs/TAREFA_V2_LAYOUT_HABITAT.md`; `docs/TAREFA_V2_TEMA_MENUS.md` |
| a batalha em tempo real | HERDADA (B) | R0 a R4 na `main`; a v14 não foi ligada; a rodada 2 em voo | `docs/TAREFA_V2_COMBATE_TR.md`; `docs/EQUILIBRIO_COMBATE_TR.md`, fase 5 |
| o ecossistema genético (G0 a G5) | ADIADA | EG-1 a EG-8 decididas; cada passo com tarefa própria. Motivo: fora das três trilhas | `docs/futuro/ecossistema_genetico.md` |
| a fisiologia por espécie (FE-3) | ADIADA | ideia (#260), decisão aberta | `docs/futuro/fisiologia_especies.md` |
| a validação da competição (V3-3/4) | ENCERRADA | todos os gates passam: G-R1 0,0124 [0,0093; 0,0156], só no v11 sem o mundo | `docs/RESULTADO_V2_VALIDACAO_COMPETICAO.md` |
| a validação única (#193) | ENCERRADA | predições 1, 2 e 5 confirmam; a 3 pelo contraste; a 4 inconclusiva | `docs/RESULTADO_V2_VALIDACAO_UNICA.md` |
| a comparação A × C (#197) | ENCERRADA | empate em CC-1 e CC-2; o A ficou | `docs/RESULTADO_V2_COMPARACAO_CEREBROS.md` |

## 2. As tarefas `docs/TAREFA_V2_*.md` (104)

| tarefa | status declarado | marca | o resultado em uma linha | de onde vem |
|---|---|---|---|---|
| A1_BOLA | ABERTA | ENCERRADA | 1a-pet passa (Δp +0,310); o cuidado controlado falha | `docs/RESULTADO_V2_A1.md` |
| A1_BOLA_IMPL | ABERTA | ENCERRADA | entregue (o código na `main`) | `docs/TAREFA_V2_A1_BOLA_IMPL.md` |
| BANCADA | ABERTA | ENCERRADA | entregue; hoje o pacote `experiments/bancada/` | `docs/TAREFA_V2_SAUDE.md`, etapa 4 |
| BANCADA_EXPERIMENTO | ABERTA | ENCERRADA | entregue (o código na `main`) | `docs/TAREFA_V2_BANCADA_EXPERIMENTO.md` |
| BANCADA_FRUTAS | ABERTA | ENCERRADA | entregue (o código na `main`) | `docs/TAREFA_V2_BANCADA_FRUTAS.md` |
| BANCADA_K4_CANAIS | ABERTA | ENCERRADA | entregue (o código na `main`) | `docs/TAREFA_V2_BANCADA_K4_CANAIS.md` |
| BANCADA_LIGA_N6_N7 | ABERTA | ENCERRADA | entregue (o código na `main`) | `docs/TAREFA_V2_BANCADA_LIGA_N6_N7.md` |
| BANCADA_MONTAGEM | ABERTA | ENCERRADA | entregue (o código na `main`) | `docs/TAREFA_V2_BANCADA_MONTAGEM.md` |
| BANCADA_MUNDOS | ABERTA | ENCERRADA | entregue (o código na `main`) | `docs/TAREFA_V2_BANCADA_MUNDOS.md` |
| BANCADA_N5 | ABERTA | ENCERRADA | entregue (o código na `main`) | `docs/TAREFA_V2_BANCADA_N5.md` |
| BANCADA_N6_N7 | ABERTA | ENCERRADA | entregue (o código na `main`) | `docs/TAREFA_V2_BANCADA_N6_N7.md` |
| BANHEIRO | BN-1 a BN-6 DECIDIDAS | ADIADA | código pronto; nada rodou (o J4) | `docs/PLANO_ANALISE_V2_BANHEIRO.md`, seção 7 |
| CALIBRACAO_CEREBROS_B_C | sem status | ENCERRADA | o B não aprende; o C fecha | `docs/RESULTADO_V2_CALIBRACAO_CEREBRO_B.md`; `docs/RESULTADO_V2_CALIBRACAO_CEREBRO_C.md` |
| CANAIS_REFORCO | ABERTA | ENCERRADA | entregue (#167) | `docs/TAREFA_V2_CANAIS_REFORCO.md` |
| CEREBRO_A_BASELINE | critérios DECIDIDOS 2026-10-25 | HERDADA (C) | AF-1 a AF-6 decididas; o A é linha de base, controle e fallback condicionado; vale como regra da trilha C | `docs/TAREFA_V2_CEREBRO_A_BASELINE.md`, seção 8 |
| CEREBRO_B | ABERTA | ENCERRADA | não aprende; saiu da comparação | `docs/RESULTADO_V2_CALIBRACAO_CEREBRO_B.md` |
| CEREBRO_C | ABERTA | ENCERRADA | calibração fecha; empate com o A | `docs/RESULTADO_V2_COMPARACAO_CEREBROS.md` |
| CEREBRO_N6_N7 | ABERTA | ENCERRADA | entregue (#154) | `docs/TAREFA_V2_CEREBRO_N6_N7.md` |
| CHATGPT_CLAUDE_POC | ENTREGUE | ENCERRADA | o fluxo rastreável provado (#337) | PR #337 |
| CLAUDE_SCIENCE_LITERATURA | sem status | ENCERRADA | a síntese da V2 em `docs/referencias/` | `docs/referencias/V2_SINTESE_Q1_Q7.md` |
| CLAUDE_SCIENCE_LITERATURA_2 | sem status | ENCERRADA | entregue | `docs/referencias/F_REVISAO_V2_SEIS_PERGUNTAS.md` |
| CLAUDE_SCIENCE_LITERATURA_3 | sem status | ENCERRADA | o corpo digital | `docs/referencias/G_REVISAO_CORPO_QUIMICO.md` |
| CLAUDE_SCIENCE_LITERATURA_4 | sem status | ENCERRADA | entregue | `docs/referencias/H_REVISAO_OLFATO_AUDICAO.md` |
| COMBATE_TR | ABERTA | HERDADA (B) | R0 a R4 na `main` (#449, #451–#453, #456, #457); a v14 não ligada | `docs/EQUILIBRIO_COMBATE_TR.md`, fase 5 |
| COMPARACAO_A_C | ABERTA | ENCERRADA | empate em CC-1 e CC-2 | `docs/RESULTADO_V2_COMPARACAO_CEREBROS.md` |
| CORPO_DRIVES | PROPOSTO | ADIADA | código pronto; a validação (34101…34505) não rodou (o J2) | `docs/RESULTADO_V2_CALIBRACAO_CORPO.md`, adendo 5 |
| DESCRITIVO_PLATO | ABERTA | ENCERRADA | misto: o A aprende qual fruta evitar na escolha, mas come a ruim sozinha | `docs/DESCRITIVO_V2_PLATO.md` |
| DIGIBRAIN_MODULAR_ESPEC | GATE PASSADO 2026-10-25 | HERDADA (C) | a espec aprovada na direção (#407); a revisão com as marcas [MECANISMO], [HIPÓTESE] e [EXISTE] fecha a trilha C | `docs/ESPEC_DIGIBRAIN_MODULAR.md` |
| DIGIBRAIN_MODULAR_LITERATURA | CONCLUÍDA | ENCERRADA | as fontes da PE-1 (#408, #409) | `docs/referencias/DM_REVISAO_SUBSTRATO_NEURAL.md` |
| DIGIBRAIN_MODULAR_PRODUTO | ABERTA, só papel | HERDADA (L) | a integração por módulos no jogo; vira a L3 | `docs/TAREFA_V2_DIGIBRAIN_MODULAR_PRODUTO.md` |
| DIGIBRAIN_MODULAR_PROTOTIPO | EM ANDAMENTO | HERDADA (C) | avaliação (#420), conserto (#424–#431), reavaliação (#432), L-2 (#437–#455) | `docs/RESULTADO_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md` |
| DOIS_PETS | ABERTA | ADIADA | degrau 1 inconclusivo por premissa (o J7) | `docs/PLANO_ANALISE_V2_DOIS_PETS.md`, adendo 1.3 |
| EVOLUCAO | ENTREGUE | ENCERRADA | entregue (2026-10-21) | `docs/TAREFA_V2_EVOLUCAO.md`, seção 9 |
| EXPLORACAO | ENTREGUE | ENCERRADA | entregue (2026-10-21) | `docs/TAREFA_V2_EXPLORACAO.md`, seção 9 |
| F0_CORPUS | ABERTA | ENCERRADA | a fase 0 da V2, entregue (#107) | `docs/TAREFA_V2_F0_LIMPEZA.md` |
| F0_INVENTARIO | ABERTA | ENCERRADA | entregue (#102) | `docs/TAREFA_V2_F0_INVENTARIO.md` |
| F0_LIMPEZA | ABERTA | ENCERRADA | entregue (#104–#107) | `docs/TAREFA_V2_F0_LIMPEZA.md` |
| F0_VINCULO | ABERTA | ENCERRADA | substituída pela F0_VINCULO_NOVO | `docs/TAREFA_V2_F0_VINCULO_NOVO.md` |
| F0_VINCULO_NOVO | ABERTA | ENCERRADA | o gate passa: atencioso − aleatório +0,171 [+0,046; +0,280] | `artifacts_v2_vinculo_novo/validacao/`; `docs/PAINEL_V2.md`, seção 2 |
| FASES_POSTERIORES | ABERTA, só papel | ADIADA | multiplayer, social, genética ampla; não começa antes do MVP no jogo com o modular | `docs/TAREFA_V2_FASES_POSTERIORES.md` |
| FRONT_REACT | etapa 1 mergeada | ENCERRADA | as etapas 1 e 2 entregues (#368): React, Tailwind, shadcn, lucide | `docs/TAREFA_V2_FRONT_REACT.md`, seções 9 e 10 |
| FRUTA_NO_CENARIO | sem status | ENCERRADA | entregue (o código na `main`) | `docs/TAREFA_V2_FRUTA_NO_CENARIO.md` |
| FRUTAS_DEFINICOES | ABERTA | ENCERRADA | entregue | `docs/DEFINICOES_FRUTAS_V2.md` |
| GATE_I | ABERTA | ADIADA | tarefa e plano entregues (#382); pausa pela DM-8 | `docs/futuro/gate_integracao_pet.md` |
| GPU_ESTILO | ABERTA | ENCERRADA | entregue (#115) | `docs/TAREFA_V2_GPU_ESTILO.md` |
| INFRA_MULTIAGENTE | ENTREGUE | ENCERRADA | entregue (#326, #344, #345, #355, #358): o relato verificado por categoria e o CI | `docs/infra/GUIA_OPERACIONAL.md` |
| INFRA_POC | ABERTA | ENCERRADA | entregue (#331): o guia operacional | `docs/infra/GUIA_OPERACIONAL.md` |
| INVESTIGA_336 | ABERTA | ENCERRADA | entregue (#345): a prova de ponta a ponta da autorização | PR #345 |
| K2_CALIBRACAO_CONJUNTA | ABERTA | ENCERRADA | o ponto escolhido; N = 30 pelo poder simulado | `docs/RESULTADO_V2_CALIBRACAO_CONJUNTA.md` |
| K4_DONO_JULGA_FRUTA | ABERTA | ENCERRADA | entregue (o código na `main`) | `docs/TAREFA_V2_K4_DONO_JULGA_FRUTA.md` |
| L0_LOBOS | ABERTA | ENCERRADA | entregue (#108): os lobos, hoje o cérebro A | `docs/TAREFA_V2_L1_DECISAO.md` |
| L1_DECISAO | ABERTA | ENCERRADA | G3 a G6 falham: o instinto decide 80 % das vezes | `docs/RESULTADO_V2_L1.md` |
| LAYOUT_HABITAT | sem status | HERDADA (L) | M0 a M6 na `main` (#458, #460, #464, #467–#470); a M7 vira a L1 | `docs/TAREFA_V2_LAYOUT_HABITAT.md`, seção 6 |
| LEITURA_PARCIAL | ABERTA | ENCERRADA | entregue | `docs/LEITURA_PARCIAL_V2_FASE1.md` |
| LEITURA_VALIDACAO | ABERTA | ENCERRADA | entregue | `docs/LEITURA_V2_VALIDACAO_UNICA.md` |
| LITERATURA_P7 | ABERTA | ENCERRADA | entregue | `docs/referencias/E2_SINTESE_PISTAS_P7.md` |
| LOBOS_MUNDO | ABERTA | ENCERRADA | entregue (#127–#137) | `docs/TAREFA_V2_LOBOS_MUNDO.md` |
| LONGE_REGULAR | ABERTA, só papel | HERDADA (C) | a tarefa na `main` (#475); LR-1 a LR-7 abertas; vira a C1 | `docs/TAREFA_V2_LONGE_REGULAR.md`, seção 8 |
| MEMORIA_AUTOBIOGRAFICA | ABERTA, só papel | HERDADA (C) | ME-1 a ME-7 abertas; vira a C4 | `docs/TAREFA_V2_MEMORIA_AUTOBIOGRAFICA.md`, seção 8 |
| METABOLISMO | ABERTA | ADIADA | etapas 0 a 4 entregues; a validação vai com o J2 | `docs/TAREFA_V2_METABOLISMO.md`, seção 10 |
| MOLDURA_DESKTOP | ENTREGUE | ENCERRADA | entregue (2026-10-20); substituída pelo layout habitat (D1) | `docs/TAREFA_V2_LAYOUT_HABITAT.md`, seção 1 |
| MUNDO_FISICO | PROPOSTO | ENCERRADA | o J1, validado, negativo | `docs/RESULTADO_V2_VALIDACAO_MUNDO.md` |
| MVP_MUNDO_PRODUTO | MVP na `main` | ENCERRADA | etapas 0 a 2 (#401, #403, #404) | `docs/TAREFA_V2_MVP_MUNDO_PRODUTO.md`, seção 9 |
| N3_CONSEQUENCIA | ABERTA | ENCERRADA | G-P1 e G6 falham | `docs/RESULTADO_V2_N3.md` |
| N4_FRUTAS | ABERTA | ENCERRADA | G-F7 passa; G-SEP e G-SSE falham | `docs/RESULTADO_V2_N4.md` |
| N5_ACOPLADO | ABERTA | ENCERRADA | entregue (o código na `main`) | `docs/TAREFA_V2_N5_ACOPLADO.md` |
| N5_CEREBRO | ABERTA | ENCERRADA | entregue (o código na `main`) | `docs/TAREFA_V2_N5_CEREBRO.md` |
| N5_MUNDO | ABERTA | ENCERRADA | entregue (o código na `main`) | `docs/TAREFA_V2_N5_MUNDO.md` |
| N5_PLANO | ABERTA | ENCERRADA | o plano entregue | `docs/PLANO_ANALISE_V2_N5.md` |
| N6_PLANO | ABERTA | ENCERRADA | o plano entregue | `docs/PLANO_ANALISE_V2_N6.md` |
| N7_MUNDO | ABERTA | ENCERRADA | entregue (o código na `main`) | `docs/TAREFA_V2_N7_MUNDO.md` |
| N7_PLANO | ABERTA | ENCERRADA | o plano entregue | `docs/PLANO_ANALISE_V2_N7.md` |
| P2D_P3I | sem status | ENCERRADA | os braços ligados na validação única | `docs/RESULTADO_V2_VALIDACAO_UNICA.md` |
| P4_CEREBRO_MUNDO | ABERTA | ADIADA | etapas 0 a 3 na `main`; o #395 (adendo 1, parte A) mergeado; pausa pela DM-8 | `docs/AUDITORIA_V2_PRODUTO_MODULAR.md`, seção 9 |
| PET_QUADRO | ENTREGUE | ENCERRADA | entregue (2026-10-20); o Quadro saiu na M3 (D4) | `docs/TAREFA_V2_LAYOUT_HABITAT.md`, seção 2 |
| PET_QUE_PENSA | ABERTA | ENCERRADA | o G-T1 passa (#370); a busca (T2) vai ao backlog como item próprio (seção 1.2) | `docs/RESULTADO_V2_VALIDACAO_PET_QUE_PENSA_ADENDO8.md` |
| PLANO_CALIBRACAO_CONJUNTA | ABERTA | ENCERRADA | o plano entregue; a run é a K2 | `docs/PLANO_CALIBRACAO_CONJUNTA_V2.md` |
| PLANO_COMPARACAO_CEREBROS | ABERTA | ENCERRADA | o plano entregue | `docs/PLANO_ANALISE_V2_COMPARACAO_CEREBROS.md` |
| PLANO_EXPERIMENTO_MAIOR | ABERTA | ENCERRADA | o plano entregue; a run é a validação única | `docs/PLANO_ANALISE_V2_EXPERIMENTO_MAIOR.md` |
| PRANCHAS_CELULAR | ABERTA | ENCERRADA | a etapa entregue (2026-10-19); substituída pelas pranchas D do layout | `docs/TAREFA_V2_PRANCHAS_CELULAR.md`, seção 9 |
| PRODUTO_CUIDADO | ENTREGUE | ENCERRADA | os chamados do bebê pelo corpo (#465) | PR #465 |
| PRODUTO_FOME | ENTREGUE | ENCERRADA | o chamado de fome pelo corpo (#450); a ração que o bebê não come fica para o equilíbrio | PR #450 |
| REDE_DE_SI | ABERTA | ADIADA | etapas 0 a 2b na `main`; falta a bancada (o J6) | `docs/TAREFA_V2_REDE_DE_SI.md`, seção 9 |
| REVISAO_APRENDIZ | ABERTA | ENCERRADA | diagnóstico: o teto segura; o gargalo é comer sem saber qual fruta está ali | `docs/RESULTADO_V2_REVISAO_APRENDIZ.md` |
| ROTEAMENTO_MODELOS | ENTREGUE | ENCERRADA | a escolha de modelo no `CLAUDE.md` | `docs/TAREFA_V2_ROTEAMENTO_MODELOS.md` |
| SAUDE | EM CURSO | ADIADA | etapas 0 a 4 na `main`; a seção 6 não registra os hooks decididos em 2026-10-14. Motivo: um registro de documento, sem pressa | `docs/PAINEL_V2.md`, seção 3 |
| TELA_PET | ENTREGUE | ENCERRADA | entregue (2026-10-19); substituída pela M3 do layout | `docs/TAREFA_V2_TELA_PET.md`, seção 9 |
| TEMA_MENUS | sem status | HERDADA (L) | a T0 na `main` (#472); as T1 a T3 viram a L2 | `docs/TAREFA_V2_TEMA_MENUS.md`, seção 5 |
| TREINO | ENTREGUE | ENCERRADA | entregue (2026-10-22, #392) | `docs/TAREFA_V2_TREINO.md`, seção 9 |
| UI_DESKTOP | ENTREGUE | ENCERRADA | entregue (2026-10-18); substituída pelo layout habitat | `docs/TAREFA_V2_UI_DESKTOP.md`, seção 7 |
| UP_ARENA | correção entregue | ENCERRADA | entregue (#446, #448); a arena saiu com o R3 da batalha em tempo real (#456) | PR #456 |
| UP_ATLAS | ABERTA | ENCERRADA | entregue (#441, atrás da chave `CLIPES_UP`) | `docs/TAREFA_V2_UP_ATLAS.md`, seção 10 |
| UP_EVOLUCAO | a tela entregue | ENCERRADA | entregue (#447, atrás de `CENA_EVOLUCAO_UP`) | `docs/TAREFA_V2_UP_EVOLUCAO.md`, seção 11 |
| UP_SOM | ABERTA | ENCERRADA | entregue (#440) | `docs/TAREFA_V2_UP_SOM.md`, seção 10 |
| V1_ADENDO3 | ABERTA | ENCERRADA | o orquestrador da validação única | `docs/RESULTADO_V2_VALIDACAO_UNICA.md` |
| V1_LIGAR | ABERTA | ENCERRADA | a run da validação única | `docs/RESULTADO_V2_VALIDACAO_UNICA.md` |
| V1_VALIDACAO_UNICA | ABERTA | ENCERRADA | predições 1, 2 e 5 confirmam | `docs/RESULTADO_V2_VALIDACAO_UNICA.md` |
| V3 (o E0 do "DigiBrain V3") | ABERTA | ENCERRADA | a auditoria E0 e o desenho, PROPOSTOS (#332); superados pela direção modular | `docs/futuro/digibrain_v3_e0.md` |
| V3_COMPETICAO | A VALIDAÇÃO RODOU | ENCERRADA | todos os gates passam (#396) | `docs/RESULTADO_V2_VALIDACAO_COMPETICAO.md` |
| V3_CREDITO_CANAL | PARADA | ENCERRADA | parada na G0-PODE-MUDAR (#376) | `docs/TAREFA_V2_V3_CREDITO_CANAL.md` |
| W_PLANO_PORTE | ABERTA | ENCERRADA | o plano do porte; executado no W | `docs/TAREFA_V2_W_PORTE_CEREBRO_A.md` |
| W_PORTE_CEREBRO_A | ABERTA, só papel | ENCERRADA | entregue (etapas 1 a 5, #343, #347) | `docs/TAREFA_V2_W_PORTE_CEREBRO_A.md`, seções 9 a 18 |
| WORLD_POC_01 | ENTREGUE | ENCERRADA | o Gate A aprovado (2026-10-19) | `docs/TAREFA_V2_WORLD_POC_01.md` |
| WORLD_POC_02 | ENTREGUE | ENCERRADA | o Gate B aprovado; a E4 (Android) espera o aparelho | `docs/TAREFA_V2_WORLD_POC_02.md` |

**Total da seção 2:** 104 linhas. ENCERRADA 86, HERDADA 9 (CEREBRO_A_BASELINE, COMBATE_TR, DIGIBRAIN_MODULAR_ESPEC,
DIGIBRAIN_MODULAR_PRODUTO, DIGIBRAIN_MODULAR_PROTOTIPO, LAYOUT_HABITAT, LONGE_REGULAR, MEMORIA_AUTOBIOGRAFICA, TEMA_MENUS), ADIADA 9.

## 3. O que este fechamento não faz

- Não edita a linha `Status:` de nenhuma tarefa. O cabeçalho "V2, congelado em <data>" entra depois, pela V3-D5.
- Não atualiza o `PAINEL_V2.md` nem o `ESTADO_ATUAL.md`. A última atualização do painel vem com a tag (V3-D3).
- Não reabre nenhuma decisão: a pergunta do dono, o bandit, a L-2, a V3-9, a P4 e o Gate I ficam como estão.
