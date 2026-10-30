# Estado atual — índice derivado (não editar à mão)

Gerado por `tools/gerar_estado_atual.py`. **Não é fonte de verdade:** cada linha copia o que o arquivo citado declara. Quem quer
saber o estado lê a fonte; quem acha um erro corrige a fonte e regenera este arquivo.

- **Estado curado da V2:** [PAINEL_V2.md](PAINEL_V2.md), atualizado em 2026-10-24 (`main` `644309c`), pelo PROMPT MESTRE. Nesta atualização entram a direção nova (a seção 0), a competição (#393, #396), o estado do porte W, o Gate I e a P4. O resto é o da atualização anterior. É o coordenador quem o mantém.
- **Onde cada tipo de informação mora** (implementado, decidido, hipótese, proposta, resultado, problema, próximo passo):
  [INDICE.md](INDICE.md).

## 1. Tarefas (`docs/TAREFA_V2_*.md`)

O status é o da linha `Status:` do arquivo, como está escrito. Muitas tarefas ficaram ABERTA depois da entrega; a última coluna
lista os `RESULTADO_V2_*.md` que citam a tarefa pelo nome do arquivo.

| tarefa | título | status declarado | resultados que a citam |
|---|---|---|---|
| [TAREFA_V2_A1_BOLA](TAREFA_V2_A1_BOLA.md) | TAREFA V2 — A1-BOLA, desenho (2026-10-01) | ABERTA | nenhum |
| [TAREFA_V2_A1_BOLA_IMPL](TAREFA_V2_A1_BOLA_IMPL.md) | TAREFA V2 — A1-BOLA, implementação (2026-10-01) | ABERTA | nenhum |
| [TAREFA_V2_BANCADA](TAREFA_V2_BANCADA.md) | TAREFA V2 — BANCADA (2026-10-01) | ABERTA | nenhum |
| [TAREFA_V2_BANCADA_EXPERIMENTO](TAREFA_V2_BANCADA_EXPERIMENTO.md) | TAREFA V2 — BANCADA-EXPERIMENTO (2026-10-05) | ABERTA | nenhum |
| [TAREFA_V2_BANCADA_FRUTAS](TAREFA_V2_BANCADA_FRUTAS.md) | TAREFA V2 — BANCADA-FRUTAS (2026-10-04) | ABERTA | nenhum |
| [TAREFA_V2_BANCADA_K4_CANAIS](TAREFA_V2_BANCADA_K4_CANAIS.md) | TAREFA V2 — BANCADA-K4-CANAIS (2026-10-05) | ABERTA | nenhum |
| [TAREFA_V2_BANCADA_LIGA_N6_N7](TAREFA_V2_BANCADA_LIGA_N6_N7.md) | TAREFA V2 — BANCADA-LIGA-N6-N7 (2026-10-05) | ABERTA | nenhum |
| [TAREFA_V2_BANCADA_MONTAGEM](TAREFA_V2_BANCADA_MONTAGEM.md) | TAREFA V2 — BANCADA-MONTAGEM (2026-10-05) | ABERTA | nenhum |
| [TAREFA_V2_BANCADA_MUNDOS](TAREFA_V2_BANCADA_MUNDOS.md) | TAREFA V2 — BANCADA-MUNDOS (2026-10-01) | ABERTA | nenhum |
| [TAREFA_V2_BANCADA_N5](TAREFA_V2_BANCADA_N5.md) | TAREFA V2 — BANCADA-N5 (2026-10-04) | ABERTA | nenhum |
| [TAREFA_V2_BANCADA_N6_N7](TAREFA_V2_BANCADA_N6_N7.md) | TAREFA V2 — BANCADA-N6-N7 (2026-10-05) | ABERTA | nenhum |
| [TAREFA_V2_BANHEIRO](TAREFA_V2_BANHEIRO.md) | Tarefa — V2: o banheiro, a necessidade no lugar certo e o limpador (W-TAREFA-BANHEIRO) | BN-1 a BN-6 DECIDIDAS pelo Matheus em 2026-10-07, todas pela recomendação (seção 10) | nenhum |
| [TAREFA_V2_CALIBRACAO_CEREBROS_B_C](TAREFA_V2_CALIBRACAO_CEREBROS_B_C.md) | TAREFA V2 — CALIBRACAO-CEREBROS-B-C (2026-10-06) | sem status declarado | [RESULTADO_V2_CALIBRACAO_CEREBRO_B](RESULTADO_V2_CALIBRACAO_CEREBRO_B.md), [RESULTADO_V2_CALIBRACAO_CEREBRO_C](RESULTADO_V2_CALIBRACAO_CEREBRO_C.md) |
| [TAREFA_V2_CANAIS_REFORCO](TAREFA_V2_CANAIS_REFORCO.md) | TAREFA V2 — CANAIS-REFORCO (2026-10-05) | ABERTA | nenhum |
| [TAREFA_V2_CEREBRO_A_BASELINE](TAREFA_V2_CEREBRO_A_BASELINE.md) | TAREFA V2 — CEREBRO_A_BASELINE: os critérios para manter o cérebro A como baseline e para recorrer a ele como fallback (2026-10-24) | os critérios DECIDIDOS pelo Matheus em 2026-10-25 (por relato do | nenhum |
| [TAREFA_V2_CEREBRO_B](TAREFA_V2_CEREBRO_B.md) | TAREFA V2 — CEREBRO-B (2026-10-05) | ABERTA | nenhum |
| [TAREFA_V2_CEREBRO_C](TAREFA_V2_CEREBRO_C.md) | TAREFA V2 — CEREBRO-C (2026-10-05) | ABERTA | nenhum |
| [TAREFA_V2_CEREBRO_N6_N7](TAREFA_V2_CEREBRO_N6_N7.md) | TAREFA V2 — CEREBRO-N6-N7 (2026-10-05) | ABERTA | nenhum |
| [TAREFA_V2_CHATGPT_CLAUDE_POC](TAREFA_V2_CHATGPT_CLAUDE_POC.md) | TAREFA V2 — CHATGPT_CLAUDE_POC (2026-10-18) | ENTREGUE (PR aberto, sem merge; execução Claude Code pendente) | nenhum |
| [TAREFA_V2_CLAUDE_SCIENCE_LITERATURA](TAREFA_V2_CLAUDE_SCIENCE_LITERATURA.md) | TAREFA — Revisão de literatura para o experimento maior da V2 (Claude Science) | sem status declarado | nenhum |
| [TAREFA_V2_CLAUDE_SCIENCE_LITERATURA_2](TAREFA_V2_CLAUDE_SCIENCE_LITERATURA_2.md) | TAREFA — Segunda revisão de literatura para a V2 (Claude Science) | sem status declarado | nenhum |
| [TAREFA_V2_CLAUDE_SCIENCE_LITERATURA_3](TAREFA_V2_CLAUDE_SCIENCE_LITERATURA_3.md) | TAREFA — Terceira revisão de literatura para a V2: o corpo digital (Claude Science) | sem status declarado | nenhum |
| [TAREFA_V2_CLAUDE_SCIENCE_LITERATURA_4](TAREFA_V2_CLAUDE_SCIENCE_LITERATURA_4.md) | TAREFA: quarta passada de literatura da V2 — ler os PDFs que ficaram sem leitura (Claude Science) | sem status declarado | nenhum |
| [TAREFA_V2_COMBATE_TR](TAREFA_V2_COMBATE_TR.md) | TAREFA V2 — COMBATE-TR: a batalha em tempo real como o combate do jogo inteiro (2026-10-29) | ABERTA | nenhum |
| [TAREFA_V2_COMPARACAO_A_C](TAREFA_V2_COMPARACAO_A_C.md) | TAREFA V2 — COMPARACAO-A-C: piloto, adendo de tamanho e validação da comparação dos cérebros (2026-10-06) | ABERTA | [RESULTADO_V2_COMPARACAO_CEREBROS](RESULTADO_V2_COMPARACAO_CEREBROS.md) |
| [TAREFA_V2_CORPO_DRIVES](TAREFA_V2_CORPO_DRIVES.md) | Tarefa — V2: o corpo mínimo e os drives de tédio, curiosidade e solidão (W-TAREFA-CORPO, rodada 16) | PROPOSTO | nenhum |
| [TAREFA_V2_DESCRITIVO_PLATO](TAREFA_V2_DESCRITIVO_PLATO.md) | TAREFA V2 — DESCRITIVO-PLATO: o aprendiz apaga a preferência ou aprende qual fruta faz mal? (2026-10-07) | ABERTA | nenhum |
| [TAREFA_V2_DIGIBRAIN_MODULAR_ESPEC](TAREFA_V2_DIGIBRAIN_MODULAR_ESPEC.md) | TAREFA V2 — DIGIBRAIN_MODULAR_ESPEC: a especificação técnica do DigiBrain modular (2026-10-24) | GATE PASSADO em 2026-10-25: a direção da especificação APROVADA pelo Matheus, com as nove… | nenhum |
| [TAREFA_V2_DIGIBRAIN_MODULAR_LITERATURA](TAREFA_V2_DIGIBRAIN_MODULAR_LITERATURA.md) | TAREFA V2 — DIGIBRAIN-MODULAR-LITERATURA: as fontes do substrato neural (a PE-1) (2026-10-25) | CONCLUÍDA | nenhum |
| [TAREFA_V2_DIGIBRAIN_MODULAR_PRODUTO](TAREFA_V2_DIGIBRAIN_MODULAR_PRODUTO.md) | TAREFA V2 — DIGIBRAIN_MODULAR_PRODUTO: a integração progressiva do DigiBrain modular no jogo (2026-10-24) | ABERTA, só papel | nenhum |
| [TAREFA_V2_DIGIBRAIN_MODULAR_PROTOTIPO](TAREFA_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md) | TAREFA V2 — DIGIBRAIN_MODULAR_PROTOTIPO: o protótipo e a avaliação dos mecanismos do DigiBrain modular (2026-10-24) | EM ANDAMENTO: a etapa 0 (#410), a 1b (#413) e a 1a (#414) na `main` em 2026-10-25; a cali… | [RESULTADO_V2_DIGIBRAIN_MODULAR_PROTOTIPO](RESULTADO_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md) |
| [TAREFA_V2_DOIS_PETS](TAREFA_V2_DOIS_PETS.md) | TAREFA V2 — DOIS PETS: dois pets de verdade no mesmo mundo (2026-10-07) | ABERTA | nenhum |
| [TAREFA_V2_EVOLUCAO](TAREFA_V2_EVOLUCAO.md) | TAREFA V2 — EVOLUCAO (2026-10-21) | ENTREGUE (PR, espera o ok visual e o merge) | nenhum |
| [TAREFA_V2_EXPLORACAO](TAREFA_V2_EXPLORACAO.md) | TAREFA V2 — EXPLORACAO (2026-10-21) | ENTREGUE (PR, espera o ok visual e o merge) | nenhum |
| [TAREFA_V2_F0_CORPUS](TAREFA_V2_F0_CORPUS.md) | TAREFA V2 — F0-CORPUS (2026-10-01) | ABERTA | nenhum |
| [TAREFA_V2_F0_INVENTARIO](TAREFA_V2_F0_INVENTARIO.md) | TAREFA V2 — F0-INVENTARIO (2026-10-01) | ABERTA | nenhum |
| [TAREFA_V2_F0_LIMPEZA](TAREFA_V2_F0_LIMPEZA.md) | TAREFA V2 — F0-LIMPEZA (2026-10-01) | ABERTA (começa com os PRs #102, #104, #105, #106 e #107 na `main`) | nenhum |
| [TAREFA_V2_F0_VINCULO](TAREFA_V2_F0_VINCULO.md) | TAREFA V2 — F0-VINCULO (2026-10-01) | ABERTA | nenhum |
| [TAREFA_V2_F0_VINCULO_NOVO](TAREFA_V2_F0_VINCULO_NOVO.md) | TAREFA V2 — F0-VINCULO-NOVO (2026-10-01) | ABERTA (começa com o PR #109 na `main`) | nenhum |
| [TAREFA_V2_FASES_POSTERIORES](TAREFA_V2_FASES_POSTERIORES.md) | TAREFA V2 — FASES_POSTERIORES: multiplayer, social, genética ampla e comunicação avançada (2026-10-24) | ABERTA, só papel; não começa antes do MVP | nenhum |
| [TAREFA_V2_FRONT_REACT](TAREFA_V2_FRONT_REACT.md) | TAREFA V2 — FRONT-REACT (2026-10-19) | etapa 1 mergeada (#368); | nenhum |
| [TAREFA_V2_FRUTA_NO_CENARIO](TAREFA_V2_FRUTA_NO_CENARIO.md) | TAREFA V2 — FRUTA-NO-CENARIO (2026-10-05) | sem status declarado | nenhum |
| [TAREFA_V2_FRUTAS_DEFINICOES](TAREFA_V2_FRUTAS_DEFINICOES.md) | TAREFA V2 — FRUTAS-DEFINICOES (2026-10-01) | ABERTA (começa depois de o C fechar o conflito do #114) | nenhum |
| [TAREFA_V2_GATE_I](TAREFA_V2_GATE_I.md) | TAREFA V2 — GATE_I: o pet integrado (corpo químico, mundo, aprendizado na vida e replay no mesmo pet) (2026-10-21) | ABERTA (a tarefa e o plano entregues, #382; as GT-1 a GT-8 DECIDIDAS pelo Matheus em | nenhum |
| [TAREFA_V2_GPU_ESTILO](TAREFA_V2_GPU_ESTILO.md) | TAREFA V2 — GPU-ESTILO (2026-10-01) | ABERTA (começa só com o PR #107, corpus em português, na `main`) | nenhum |
| [TAREFA_V2_INFRA_MULTIAGENTE](TAREFA_V2_INFRA_MULTIAGENTE.md) | TAREFA V2 — INFRA_MULTIAGENTE (2026-10-18) | ENTREGUE (PR aberto, sem merge) | nenhum |
| [TAREFA_V2_INFRA_POC](TAREFA_V2_INFRA_POC.md) | TAREFA V2 — INFRA_POC (2026-10-18) | ABERTA | nenhum |
| [TAREFA_V2_INFRA_PREFIXO_V3](TAREFA_V2_INFRA_PREFIXO_V3.md) | TAREFA V2 — INFRA_PREFIXO_V3 (2026-10-30) | ENTREGUE | nenhum |
| [TAREFA_V2_INVESTIGA_336](TAREFA_V2_INVESTIGA_336.md) | TAREFA V2 — INVESTIGA_336 (2026-10-19) | ABERTA | nenhum |
| [TAREFA_V2_K2_CALIBRACAO_CONJUNTA](TAREFA_V2_K2_CALIBRACAO_CONJUNTA.md) | TAREFA V2 — K2-CALIBRACAO-CONJUNTA (2026-10-05) | ABERTA | [RESULTADO_V2_CALIBRACAO_CONJUNTA](RESULTADO_V2_CALIBRACAO_CONJUNTA.md) |
| [TAREFA_V2_K4_DONO_JULGA_FRUTA](TAREFA_V2_K4_DONO_JULGA_FRUTA.md) | TAREFA V2 — K4-DONO-JULGA-FRUTA (2026-10-05) | ABERTA | nenhum |
| [TAREFA_V2_L0_LOBOS](TAREFA_V2_L0_LOBOS.md) | TAREFA V2 — L0-LOBOS (2026-10-01) | ABERTA | nenhum |
| [TAREFA_V2_L1_DECISAO](TAREFA_V2_L1_DECISAO.md) | TAREFA V2 — L1-DECISAO (2026-10-01) | ABERTA (começa só com o PR #108, L0, na `main`) | [RESULTADO_V2_L1](RESULTADO_V2_L1.md) |
| [TAREFA_V2_LAYOUT_HABITAT](TAREFA_V2_LAYOUT_HABITAT.md) | Tarefa V2 — layout "habitat em tela cheia" com menus XCOM | sem status declarado | nenhum |
| [TAREFA_V2_LEITURA_PARCIAL](TAREFA_V2_LEITURA_PARCIAL.md) | TAREFA V2 — LEITURA-PARCIAL (2026-10-05) | ABERTA | nenhum |
| [TAREFA_V2_LEITURA_VALIDACAO](TAREFA_V2_LEITURA_VALIDACAO.md) | TAREFA V2 — LEITURA-VALIDACAO: a leitura da validação única (2026-10-06) | ABERTA | nenhum |
| [TAREFA_V2_LITERATURA_P7](TAREFA_V2_LITERATURA_P7.md) | TAREFA V2 — LITERATURA-P7: a segunda passada antes da leitura (2026-10-06) | ABERTA | nenhum |
| [TAREFA_V2_LOBOS_MUNDO](TAREFA_V2_LOBOS_MUNDO.md) | TAREFA V2 — LOBOS-MUNDO (2026-10-04) | ABERTA | nenhum |
| [TAREFA_V2_LONGE_REGULAR](TAREFA_V2_LONGE_REGULAR.md) | TAREFA V2 — LONGE_REGULAR: o longe com lugares fixos, para separar a distância da falta de regularidade (2026-10-30) | ABERTA, só papel | nenhum |
| [TAREFA_V2_MEMORIA_AUTOBIOGRAFICA](TAREFA_V2_MEMORIA_AUTOBIOGRAFICA.md) | TAREFA V2 — MEMORIA_AUTOBIOGRAFICA: a memória autobiográfica consolidada, com influência causal nas decisões e nas facetas (2026-10-24) | ABERTA, só papel | nenhum |
| [TAREFA_V2_METABOLISMO](TAREFA_V2_METABOLISMO.md) | TAREFA V2 — METABOLISMO ENERGÉTICO: conversão, reserva e mobilização no corpo (2026-10-08) | ABERTA | nenhum |
| [TAREFA_V2_MOLDURA_DESKTOP](TAREFA_V2_MOLDURA_DESKTOP.md) | TAREFA V2 — MOLDURA-DESKTOP (2026-10-20) | ENTREGUE (PR, espera o ok visual e o merge) | nenhum |
| [TAREFA_V2_MUNDO_FISICO](TAREFA_V2_MUNDO_FISICO.md) | Tarefa — V2: o mundo físico mínimo (W-TAREFA-MUNDO, rodada 16) | PROPOSTO | nenhum |
| [TAREFA_V2_MVP_MUNDO_PRODUTO](TAREFA_V2_MVP_MUNDO_PRODUTO.md) | TAREFA V2 — MVP_MUNDO_PRODUTO: o mundo físico no jogo, com a comida posta pelo jogador (2026-10-24) | MVP na `main` (2026-10-24): a etapa 0 (#401), a etapa 1 (#403, o pet v12 com o mundo e o … | nenhum |
| [TAREFA_V2_N3_CONSEQUENCIA](TAREFA_V2_N3_CONSEQUENCIA.md) | TAREFA V2 — N3-CONSEQUENCIA (2026-10-01) | ABERTA | [RESULTADO_V2_N3](RESULTADO_V2_N3.md) |
| [TAREFA_V2_N4_FRUTAS](TAREFA_V2_N4_FRUTAS.md) | TAREFA V2 — N4-FRUTAS (2026-10-01) | ABERTA | nenhum |
| [TAREFA_V2_N5_ACOPLADO](TAREFA_V2_N5_ACOPLADO.md) | TAREFA V2 — N5-ACOPLADO (2026-10-04) | ABERTA | nenhum |
| [TAREFA_V2_N5_CEREBRO](TAREFA_V2_N5_CEREBRO.md) | TAREFA V2 — N5-CEREBRO (2026-10-04) | ABERTA | nenhum |
| [TAREFA_V2_N5_MUNDO](TAREFA_V2_N5_MUNDO.md) | TAREFA V2 — N5-MUNDO (2026-10-04) | ABERTA | nenhum |
| [TAREFA_V2_N5_PLANO](TAREFA_V2_N5_PLANO.md) | TAREFA V2 — N5-PLANO (2026-10-04) | ABERTA | nenhum |
| [TAREFA_V2_N6_PLANO](TAREFA_V2_N6_PLANO.md) | TAREFA V2 — N6-PLANO (2026-10-04) | ABERTA | nenhum |
| [TAREFA_V2_N7_MUNDO](TAREFA_V2_N7_MUNDO.md) | TAREFA V2 — N7-MUNDO (2026-10-05) | ABERTA | nenhum |
| [TAREFA_V2_N7_PLANO](TAREFA_V2_N7_PLANO.md) | TAREFA V2 — N7-PLANO (2026-10-05) | ABERTA | nenhum |
| [TAREFA_V2_P2D_P3I](TAREFA_V2_P2D_P3I.md) | TAREFA V2 — P2D-P3I: os braços que separam momento e interpretação (2026-10-06) | sem status declarado | nenhum |
| [TAREFA_V2_P4_CEREBRO_MUNDO](TAREFA_V2_P4_CEREBRO_MUNDO.md) | TAREFA V2 — P4_CEREBRO_MUNDO: o cérebro A com o planejador no mundo 3D (2026-10-21) | ABERTA (o esboço entregue, #377; as P4-1 a P4-8 | [RESULTADO_V2_VALIDACAO_PET_QUE_PENSA_ADENDO8](RESULTADO_V2_VALIDACAO_PET_QUE_PENSA_ADENDO8.md) |
| [TAREFA_V2_PET_QUADRO](TAREFA_V2_PET_QUADRO.md) | TAREFA V2 — PET-QUADRO (2026-10-20) | ENTREGUE (PR, espera o ok visual e o merge) | nenhum |
| [TAREFA_V2_PET_QUE_PENSA](TAREFA_V2_PET_QUE_PENSA.md) | TAREFA V2 — O PET QUE PENSA (J5): o modelo do desfecho, o mapa da comida e o planejador de um alvo (2026-10-13) | ABERTA | nenhum |
| [TAREFA_V2_PLANO_CALIBRACAO_CONJUNTA](TAREFA_V2_PLANO_CALIBRACAO_CONJUNTA.md) | TAREFA V2 — PLANO-CALIBRACAO-CONJUNTA (2026-10-05) | ABERTA | nenhum |
| [TAREFA_V2_PLANO_COMPARACAO_CEREBROS](TAREFA_V2_PLANO_COMPARACAO_CEREBROS.md) | TAREFA V2 — PLANO-COMPARACAO-CEREBROS (2026-10-05) | ABERTA | nenhum |
| [TAREFA_V2_PLANO_EXPERIMENTO_MAIOR](TAREFA_V2_PLANO_EXPERIMENTO_MAIOR.md) | TAREFA V2 — PLANO-EXPERIMENTO-MAIOR (2026-10-01) | ABERTA | nenhum |
| [TAREFA_V2_PRANCHAS_CELULAR](TAREFA_V2_PRANCHAS_CELULAR.md) | TAREFA V2 — PRANCHAS_CELULAR (2026-10-19) | ABERTA | nenhum |
| [TAREFA_V2_PRODUTO_CUIDADO](TAREFA_V2_PRODUTO_CUIDADO.md) | TAREFA V2 — PRODUTO-CUIDADO (2026-10-30) | ENTREGUE | nenhum |
| [TAREFA_V2_PRODUTO_FOME](TAREFA_V2_PRODUTO_FOME.md) | TAREFA V2 — PRODUTO-FOME (2026-10-29) | ENTREGUE | nenhum |
| [TAREFA_V2_REDE_DE_SI](TAREFA_V2_REDE_DE_SI.md) | TAREFA V2 — DIGICORPO (a rede de si): o automodelo em observação (etapa 2 do ego) (2026-10-08) | ABERTA | [RESULTADO_V2_CALIBRACAO_REDE_DE_SI](RESULTADO_V2_CALIBRACAO_REDE_DE_SI.md) |
| [TAREFA_V2_REVISAO_APRENDIZ](TAREFA_V2_REVISAO_APRENDIZ.md) | TAREFA V2 — REVISAO-APRENDIZ (2026-10-04, para a rodada 6) | ABERTA na rodada 6, depois do N5-CEREBRO (`docs/TAREFA_V2_N5_CEREBRO.md`) e da BANCADA-N5… | [RESULTADO_V2_REVISAO_APRENDIZ](RESULTADO_V2_REVISAO_APRENDIZ.md) |
| [TAREFA_V2_ROTEAMENTO_MODELOS](TAREFA_V2_ROTEAMENTO_MODELOS.md) | TAREFA V2 — ROTEAMENTO_MODELOS (2026-10-18) | ENTREGUE (alteração documental entregue por PR; merge do Matheus) | nenhum |
| [TAREFA_V2_SAUDE](TAREFA_V2_SAUDE.md) | TAREFA V2 — RODADA DE SAÚDE: o backup, o CLAUDE.md enxuto, o registro por mês, a bancada em módulos, os hooks e o painel (2026-10-13) | EM CURSO desde 2026-10-13 | nenhum |
| [TAREFA_V2_TELA_PET](TAREFA_V2_TELA_PET.md) | TAREFA V2 — TELA-PET (2026-10-19) | ENTREGUE (PR, espera o ok visual e o merge) | nenhum |
| [TAREFA_V2_TEMA_MENUS](TAREFA_V2_TEMA_MENUS.md) | Tarefa V2 — tema dos menus: peles Militar e Holográfico | sem status declarado | nenhum |
| [TAREFA_V2_TRANSICAO_V3](TAREFA_V2_TRANSICAO_V3.md) | TAREFA V2 — TRANSICAO_V3: fechar a V2 e propor o plano da V3 (2026-10-30) | ENTREGUE (PR aberto, sem merge) | nenhum |
| [TAREFA_V2_TREINO](TAREFA_V2_TREINO.md) | TAREFA V2 — TREINO (2026-10-22) | ENTREGUE (PR, espera o ok visual e o merge) | nenhum |
| [TAREFA_V2_UI_DESKTOP](TAREFA_V2_UI_DESKTOP.md) | TAREFA V2 — UI-DESKTOP (2026-10-18) | ENTREGUE (PR desta etapa) | nenhum |
| [TAREFA_V2_UP_ARENA](TAREFA_V2_UP_ARENA.md) | TAREFA V2 — UP-ARENA: a arena em tempo real no jogo web (2026-10-29) | CORREÇÃO DO PET ENTREGUE, esperando a revisão e o merge do Matheus (etapa 0 na seção 10, … | nenhum |
| [TAREFA_V2_UP_ATLAS](TAREFA_V2_UP_ATLAS.md) | TAREFA V2 — UP-ATLAS: o atlas com os clipes oficiais do Digimon UP (2026-10-29) | ABERTA (liberada pelo Matheus em | nenhum |
| [TAREFA_V2_UP_EVOLUCAO](TAREFA_V2_UP_EVOLUCAO.md) | TAREFA V2 — UP-EVOLUCAO: a cena oficial de digievolução na Revelação (2026-10-29) | A TELA ENTREGUE, à espera do Matheus (a etapa 0 na seção 10, decidida na seção 9; a tela … | nenhum |
| [TAREFA_V2_UP_SOM](TAREFA_V2_UP_SOM.md) | TAREFA V2 — UP-SOM: o sistema de áudio do jogo web (2026-10-29) | ABERTA (liberada pelo Matheus em | nenhum |
| [TAREFA_V2_V1_ADENDO3](TAREFA_V2_V1_ADENDO3.md) | TAREFA V2 — V1-ADENDO3: o orquestrador da validação com o adendo 3 (2026-10-06) | ABERTA | [RESULTADO_V2_VALIDACAO_UNICA](RESULTADO_V2_VALIDACAO_UNICA.md) |
| [TAREFA_V2_V1_LIGAR](TAREFA_V2_V1_LIGAR.md) | TAREFA V2 — V1-LIGAR: faixa nova, P2d e P3i ligados, e a run (2026-10-06) | ABERTA | [RESULTADO_V2_VALIDACAO_UNICA](RESULTADO_V2_VALIDACAO_UNICA.md) |
| [TAREFA_V2_V1_VALIDACAO_UNICA](TAREFA_V2_V1_VALIDACAO_UNICA.md) | TAREFA V2 — V1-VALIDACAO-UNICA (2026-10-06) | ABERTA | [RESULTADO_V2_VALIDACAO_UNICA](RESULTADO_V2_VALIDACAO_UNICA.md) |
| [TAREFA_V2_V3](TAREFA_V2_V3.md) | TAREFA V2 — V3 (2026-10-19) | ABERTA | nenhum |
| [TAREFA_V2_V3_COMPETICAO](TAREFA_V2_V3_COMPETICAO.md) | TAREFA V2 — V3_COMPETICAO: a competição entre as regras urgentes (V3-3 e V3-4) (2026-10-21) | A VALIDAÇÃO RODOU | [RESULTADO_V2_PILOTO_COMPETICAO](RESULTADO_V2_PILOTO_COMPETICAO.md), [RESULTADO_V2_VALIDACAO_COMPETICAO](RESULTADO_V2_VALIDACAO_COMPETICAO.md) |
| [TAREFA_V2_V3_CREDITO_CANAL](TAREFA_V2_V3_CREDITO_CANAL.md) | TAREFA V2 — V3_CREDITO_CANAL: o crédito do "querer" por canal até o alvo (2026-10-19) | PARADA na G0-PODE-MUDAR | nenhum |
| [TAREFA_V2_W_PLANO_PORTE](TAREFA_V2_W_PLANO_PORTE.md) | TAREFA V2 — W-PLANO-PORTE: o plano do porte do cérebro A para a web, pets v11 (2026-10-07) | ABERTA | nenhum |
| [TAREFA_V2_W_PORTE_CEREBRO_A](TAREFA_V2_W_PORTE_CEREBRO_A.md) | TAREFA V2 — W-PORTE: o cérebro A no jogo web, com o painel DigiBrain (2026-10-17) | ABERTA, só papel | nenhum |
| [TAREFA_V2_WORLD_POC_01](TAREFA_V2_WORLD_POC_01.md) | TAREFA V2 — WORLD_POC_01 (2026-10-19) | ENTREGUE; o Gate A foi APROVADO pelo Matheus em 2026-10-19, com duas ressalvas: um celula… | nenhum |
| [TAREFA_V2_WORLD_POC_02](TAREFA_V2_WORLD_POC_02.md) | TAREFA V2 — WORLD_POC_02 (2026-10-19) | ENTREGUE (E0 a E3; a E4, o Android mais simples, fica para quando houver o aparelho) | nenhum |

## 2. Planos de análise (`docs/PLANO_ANALISE_V2_*.md`)

"nenhum" quer dizer só que nenhum `RESULTADO_V2_*.md` cita o plano: o resultado pode estar num adendo do próprio plano.

| plano | título | resultados que o citam |
|---|---|---|
| [PLANO_ANALISE_V2_A1](PLANO_ANALISE_V2_A1.md) | Plano de análise — V2, A1: a bola como primeiro objeto do mundo com consequência | [RESULTADO_V2_A1](RESULTADO_V2_A1.md) |
| [PLANO_ANALISE_V2_BANHEIRO](PLANO_ANALISE_V2_BANHEIRO.md) | Plano de análise — V2: o banheiro, o carinho e o limpador (W-PLANO-BANHEIRO) | nenhum |
| [PLANO_ANALISE_V2_COMPARACAO_CEREBROS](PLANO_ANALISE_V2_COMPARACAO_CEREBROS.md) | Plano de análise — comparação dos DigiBrains A × B × C (K3/V2) | [RESULTADO_V2_CALIBRACAO_CEREBRO_B](RESULTADO_V2_CALIBRACAO_CEREBRO_B.md), [RESULTADO_V2_CALIBRACAO_CEREBRO_C](RESULTADO_V2_CALIBRACAO_CEREBRO_C.md), [RESULTADO_V2_COMPARACAO_CEREBROS](RESULTADO_V2_COMPARACAO_CEREBROS.md) |
| [PLANO_ANALISE_V2_CORPO_DRIVES](PLANO_ANALISE_V2_CORPO_DRIVES.md) | Plano de análise — V2: o P1 com o corpo e os drives novos | [RESULTADO_V2_CALIBRACAO_CORPO](RESULTADO_V2_CALIBRACAO_CORPO.md) |
| [PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO](PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md) | Plano de análise — o protótipo do DigiBrain modular, etapa 1 | [RESULTADO_V2_DIGIBRAIN_MODULAR_PROTOTIPO](RESULTADO_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md) |
| [PLANO_ANALISE_V2_DOIS_PETS](PLANO_ANALISE_V2_DOIS_PETS.md) | Plano de análise — V2: dois pets, o degrau 1 (o B aprende o que só o A viveu?) | nenhum |
| [PLANO_ANALISE_V2_EXPERIMENTO_MAIOR](PLANO_ANALISE_V2_EXPERIMENTO_MAIOR.md) | Plano de análise — o experimento maior (plasticidade por fonte × condição do mundo) | [RESULTADO_V2_VALIDACAO_UNICA](RESULTADO_V2_VALIDACAO_UNICA.md) |
| [PLANO_ANALISE_V2_GATE_I](PLANO_ANALISE_V2_GATE_I.md) | Plano de análise — V2: o Gate I, o pet integrado aprende na vida pela consequência? | nenhum |
| [PLANO_ANALISE_V2_GPU_ESTILO](PLANO_ANALISE_V2_GPU_ESTILO.md) | Plano de análise — GPU-ESTILO: o estilo da espécie com o corpus em português (V2, fase 0) | nenhum |
| [PLANO_ANALISE_V2_L1](PLANO_ANALISE_V2_L1.md) | Plano de análise — V2, L1: o lobo de decisão aprende com o feedback como vantagem | [RESULTADO_V2_L1](RESULTADO_V2_L1.md) |
| [PLANO_ANALISE_V2_MUNDO_ALVO](PLANO_ANALISE_V2_MUNDO_ALVO.md) | Plano de análise — V2: o mundo físico com o alvo aprendido (aprender para onde ir ajuda a procurar?) | [RESULTADO_V2_VALIDACAO_MUNDO_ALVO](RESULTADO_V2_VALIDACAO_MUNDO_ALVO.md) |
| [PLANO_ANALISE_V2_MUNDO_FISICO](PLANO_ANALISE_V2_MUNDO_FISICO.md) | Plano de análise — V2: o P1 no mundo físico mínimo | [RESULTADO_V2_CALIBRACAO_MUNDO](RESULTADO_V2_CALIBRACAO_MUNDO.md), [RESULTADO_V2_VALIDACAO_MUNDO](RESULTADO_V2_VALIDACAO_MUNDO.md) |
| [PLANO_ANALISE_V2_N3](PLANO_ANALISE_V2_N3.md) | Plano de análise — V2, N3: a consequência da própria ação como sinal (braço P1) | [RESULTADO_V2_N3](RESULTADO_V2_N3.md) |
| [PLANO_ANALISE_V2_N4](PLANO_ANALISE_V2_N4.md) | Plano de análise — V2, N4: frutas no mundo, sem aprendizado de política | [RESULTADO_V2_N4](RESULTADO_V2_N4.md) |
| [PLANO_ANALISE_V2_N5](PLANO_ANALISE_V2_N5.md) | Plano de análise — N5: o dono informa, o mundo valida ou refuta (braços P2 e P2e) | nenhum |
| [PLANO_ANALISE_V2_N6](PLANO_ANALISE_V2_N6.md) | Plano de análise — N6: memória de episódios no mundo das frutas (quatro marcos) | nenhum |
| [PLANO_ANALISE_V2_N7](PLANO_ANALISE_V2_N7.md) | Plano de análise — N7: arbitragem entre duas prioridades (a necessidade do pet × o pedido do dono) | nenhum |
| [PLANO_ANALISE_V2_P4_CORPORIFICADO](PLANO_ANALISE_V2_P4_CORPORIFICADO.md) | Plano de análise — V2: a P4, a revalorização do J5 no mundo com o contrato sensório-motor (a replicação do T1) | nenhum |
| [PLANO_ANALISE_V2_PET_QUE_PENSA](PLANO_ANALISE_V2_PET_QUE_PENSA.md) | Plano de análise — V2: o pet que pensa (J5), o planejador de um alvo passa nos dois testes da DS-1? | [RESULTADO_V2_CALIBRACAO_PET_QUE_PENSA](RESULTADO_V2_CALIBRACAO_PET_QUE_PENSA.md), [RESULTADO_V2_CALIBRACAO_PET_QUE_PENSA_AO_LADO](RESULTADO_V2_CALIBRACAO_PET_QUE_PENSA_AO_LADO.md), [RESULTADO_V2_CALIBRACAO_PET_QUE_PENSA_PALADAR](RESULTADO_V2_CALIBRACAO_PET_QUE_PENSA_PALADAR.md), [RESULTADO_V2_PILOTO_PET_QUE_PENSA_ADENDO7](RESULTADO_V2_PILOTO_PET_QUE_PENSA_ADENDO7.md), [RESULTADO_V2_PILOTO_PET_QUE_PENSA_ADENDO8](RESULTADO_V2_PILOTO_PET_QUE_PENSA_ADENDO8.md), [RESULTADO_V2_VALIDACAO_PET_QUE_PENSA](RESULTADO_V2_VALIDACAO_PET_QUE_PENSA.md), [RESULTADO_V2_VALIDACAO_PET_QUE_PENSA_ADENDO8](RESULTADO_V2_VALIDACAO_PET_QUE_PENSA_ADENDO8.md) |
| [PLANO_ANALISE_V2_REDE_DE_SI](PLANO_ANALISE_V2_REDE_DE_SI.md) | Plano de análise — V2: a rede de si em observação (etapa 2 do ego) | [RESULTADO_V2_CALIBRACAO_REDE_DE_SI](RESULTADO_V2_CALIBRACAO_REDE_DE_SI.md) |
| [PLANO_ANALISE_V2_REVISAO_APRENDIZ](PLANO_ANALISE_V2_REVISAO_APRENDIZ.md) | Plano de análise — revisão do aprendiz: teto, janela de crédito ou exposição? | [RESULTADO_V2_REVISAO_APRENDIZ](RESULTADO_V2_REVISAO_APRENDIZ.md) |
| [PLANO_ANALISE_V2_TRANSFERENCIA_REJEICAO](PLANO_ANALISE_V2_TRANSFERENCIA_REJEICAO.md) | Plano de análise — V2: a transferência da rejeição da escolha para o item único (DS-3) | nenhum |
| [PLANO_ANALISE_V2_V3_COMPETICAO](PLANO_ANALISE_V2_V3_COMPETICAO.md) | Plano de análise — V2/V3: a competição entre as regras urgentes (V3-3/V3-4) | [RESULTADO_V2_PILOTO_COMPETICAO](RESULTADO_V2_PILOTO_COMPETICAO.md), [RESULTADO_V2_VALIDACAO_COMPETICAO](RESULTADO_V2_VALIDACAO_COMPETICAO.md) |
| [PLANO_ANALISE_V2_VINCULO](PLANO_ANALISE_V2_VINCULO.md) | Plano de análise — vínculo B (previsibilidade + desejo) em vidas novas | nenhum |

## 3. Os últimos 10 desvios registrados

Do índice [REGISTRO_DESVIOS.md](REGISTRO_DESVIOS.md) (372 entradas), na ordem em que entraram.

- [2026-10-30 — PRODUTO-CUIDADO (worker A, Claude Code, Opus 5.5, worktree `v2-produto-cuidado`): os chamados do bebê pelo corpo, com os limiares do bebê](registro/2026-10.md)
- [2026-10-30 — COMBATE-TR calibração, fase 4 (worker, Claude Code, Opus 5.5, worktree `v2-combate-tr`): a progressão, o fim de jogo e os itens, com a DE-9 e a DE-10](registro/2026-10.md)
- [2026-10-30 — COMBATE-TR conferência única (fase 5; worker, Claude Code, Opus 5.5, worktree `v2-combate-tr`): o candidato v14 nas sementes de conferência](registro/2026-10.md)
- [2026-10-30 — LONGE-REGULAR, etapa 0 (Claude Code, Opus 5.5, worktree `v2-longe-regular`): a tarefa do longe com lugares fixos](registro/2026-10.md)
- [2026-10-30 — COMBATE-TR, o plano da segunda rodada de equilíbrio (worker, Claude Code, Opus 5.5, worktree `v2-combate-tr`)](registro/2026-10.md)
- [2026-10-30 — TRANSICAO-V3, o G0 (Gerente da transição, Claude Code, Opus 5.5, worktree `v2-transicao-v3`): o fechamento da V2 e o plano da V3](registro/2026-10.md)
- [2026-10-30 — TRANSICAO-V3, as V3-D1 a V3-D8 (Gerente da transição, Claude Code, Opus 5.5, worktree `v2-transicao-v3`): decididas pela recomendação](registro/2026-10.md)
- [2026-10-30 — COMBATE-TR, segunda rodada (worker, Claude Code, Opus 5.5, worktree `v2-combate-tr`): as decisões DR2-1 a DR2-6](registro/2026-10.md)
- [2026-10-30 — COMBATE-TR, segunda rodada, R2-0 e R2-1 (worker, Claude Code, Opus 5.5, worktree `v2-combate-tr`): o ponto de partida e as formas](registro/2026-10.md)
- [2026-10-30 — INFRA-PREFIXO-V3 (worker, Claude Code, Sonnet 5.5, worktree `v3-infra-prefixo`): o CI e as ferramentas passam a aceitar o prefixo V3](registro/2026-10.md)
