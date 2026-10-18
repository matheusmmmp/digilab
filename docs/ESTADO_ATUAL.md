# Estado atual — índice derivado (não editar à mão)

Gerado por `tools/gerar_estado_atual.py`. **Não é fonte de verdade:** cada linha copia o que o arquivo citado declara. Quem quer
saber o estado lê a fonte; quem acha um erro corrige a fonte e regenera este arquivo.

- **Estado curado da V2:** [PAINEL_V2.md](PAINEL_V2.md), atualizado em 2026-10-18 (`main` `66bc21b`). Nesta atualização mudaram só o J5, o porte (W), o connectome, as decisões abertas e o risco da saúde do repositório; o resto é o de 2026-10-13. É o coordenador quem o mantém.
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
| [TAREFA_V2_CEREBRO_B](TAREFA_V2_CEREBRO_B.md) | TAREFA V2 — CEREBRO-B (2026-10-05) | ABERTA | nenhum |
| [TAREFA_V2_CEREBRO_C](TAREFA_V2_CEREBRO_C.md) | TAREFA V2 — CEREBRO-C (2026-10-05) | ABERTA | nenhum |
| [TAREFA_V2_CEREBRO_N6_N7](TAREFA_V2_CEREBRO_N6_N7.md) | TAREFA V2 — CEREBRO-N6-N7 (2026-10-05) | ABERTA | nenhum |
| [TAREFA_V2_CLAUDE_SCIENCE_LITERATURA](TAREFA_V2_CLAUDE_SCIENCE_LITERATURA.md) | TAREFA — Revisão de literatura para o experimento maior da V2 (Claude Science) | sem status declarado | nenhum |
| [TAREFA_V2_CLAUDE_SCIENCE_LITERATURA_2](TAREFA_V2_CLAUDE_SCIENCE_LITERATURA_2.md) | TAREFA — Segunda revisão de literatura para a V2 (Claude Science) | sem status declarado | nenhum |
| [TAREFA_V2_CLAUDE_SCIENCE_LITERATURA_3](TAREFA_V2_CLAUDE_SCIENCE_LITERATURA_3.md) | TAREFA — Terceira revisão de literatura para a V2: o corpo digital (Claude Science) | sem status declarado | nenhum |
| [TAREFA_V2_CLAUDE_SCIENCE_LITERATURA_4](TAREFA_V2_CLAUDE_SCIENCE_LITERATURA_4.md) | TAREFA: quarta passada de literatura da V2 — ler os PDFs que ficaram sem leitura (Claude Science) | sem status declarado | nenhum |
| [TAREFA_V2_COMPARACAO_A_C](TAREFA_V2_COMPARACAO_A_C.md) | TAREFA V2 — COMPARACAO-A-C: piloto, adendo de tamanho e validação da comparação dos cérebros (2026-10-06) | ABERTA | [RESULTADO_V2_COMPARACAO_CEREBROS](RESULTADO_V2_COMPARACAO_CEREBROS.md) |
| [TAREFA_V2_CORPO_DRIVES](TAREFA_V2_CORPO_DRIVES.md) | Tarefa — V2: o corpo mínimo e os drives de tédio, curiosidade e solidão (W-TAREFA-CORPO, rodada 16) | PROPOSTO | nenhum |
| [TAREFA_V2_DESCRITIVO_PLATO](TAREFA_V2_DESCRITIVO_PLATO.md) | TAREFA V2 — DESCRITIVO-PLATO: o aprendiz apaga a preferência ou aprende qual fruta faz mal? (2026-10-07) | ABERTA | nenhum |
| [TAREFA_V2_DOIS_PETS](TAREFA_V2_DOIS_PETS.md) | TAREFA V2 — DOIS PETS: dois pets de verdade no mesmo mundo (2026-10-07) | ABERTA | nenhum |
| [TAREFA_V2_F0_CORPUS](TAREFA_V2_F0_CORPUS.md) | TAREFA V2 — F0-CORPUS (2026-10-01) | ABERTA | nenhum |
| [TAREFA_V2_F0_INVENTARIO](TAREFA_V2_F0_INVENTARIO.md) | TAREFA V2 — F0-INVENTARIO (2026-10-01) | ABERTA | nenhum |
| [TAREFA_V2_F0_LIMPEZA](TAREFA_V2_F0_LIMPEZA.md) | TAREFA V2 — F0-LIMPEZA (2026-10-01) | ABERTA (começa com os PRs #102, #104, #105, #106 e #107 na `main`) | nenhum |
| [TAREFA_V2_F0_VINCULO](TAREFA_V2_F0_VINCULO.md) | TAREFA V2 — F0-VINCULO (2026-10-01) | ABERTA | nenhum |
| [TAREFA_V2_F0_VINCULO_NOVO](TAREFA_V2_F0_VINCULO_NOVO.md) | TAREFA V2 — F0-VINCULO-NOVO (2026-10-01) | ABERTA (começa com o PR #109 na `main`) | nenhum |
| [TAREFA_V2_FRUTA_NO_CENARIO](TAREFA_V2_FRUTA_NO_CENARIO.md) | TAREFA V2 — FRUTA-NO-CENARIO (2026-10-05) | sem status declarado | nenhum |
| [TAREFA_V2_FRUTAS_DEFINICOES](TAREFA_V2_FRUTAS_DEFINICOES.md) | TAREFA V2 — FRUTAS-DEFINICOES (2026-10-01) | ABERTA (começa depois de o C fechar o conflito do #114) | nenhum |
| [TAREFA_V2_GPU_ESTILO](TAREFA_V2_GPU_ESTILO.md) | TAREFA V2 — GPU-ESTILO (2026-10-01) | ABERTA (começa só com o PR #107, corpus em português, na `main`) | nenhum |
| [TAREFA_V2_INFRA_MULTIAGENTE](TAREFA_V2_INFRA_MULTIAGENTE.md) | TAREFA V2 — INFRA_MULTIAGENTE (2026-10-18) | ENTREGUE (PR aberto, sem merge) | nenhum |
| [TAREFA_V2_K2_CALIBRACAO_CONJUNTA](TAREFA_V2_K2_CALIBRACAO_CONJUNTA.md) | TAREFA V2 — K2-CALIBRACAO-CONJUNTA (2026-10-05) | ABERTA | [RESULTADO_V2_CALIBRACAO_CONJUNTA](RESULTADO_V2_CALIBRACAO_CONJUNTA.md) |
| [TAREFA_V2_K4_DONO_JULGA_FRUTA](TAREFA_V2_K4_DONO_JULGA_FRUTA.md) | TAREFA V2 — K4-DONO-JULGA-FRUTA (2026-10-05) | ABERTA | nenhum |
| [TAREFA_V2_L0_LOBOS](TAREFA_V2_L0_LOBOS.md) | TAREFA V2 — L0-LOBOS (2026-10-01) | ABERTA | nenhum |
| [TAREFA_V2_L1_DECISAO](TAREFA_V2_L1_DECISAO.md) | TAREFA V2 — L1-DECISAO (2026-10-01) | ABERTA (começa só com o PR #108, L0, na `main`) | [RESULTADO_V2_L1](RESULTADO_V2_L1.md) |
| [TAREFA_V2_LEITURA_PARCIAL](TAREFA_V2_LEITURA_PARCIAL.md) | TAREFA V2 — LEITURA-PARCIAL (2026-10-05) | ABERTA | nenhum |
| [TAREFA_V2_LEITURA_VALIDACAO](TAREFA_V2_LEITURA_VALIDACAO.md) | TAREFA V2 — LEITURA-VALIDACAO: a leitura da validação única (2026-10-06) | ABERTA | nenhum |
| [TAREFA_V2_LITERATURA_P7](TAREFA_V2_LITERATURA_P7.md) | TAREFA V2 — LITERATURA-P7: a segunda passada antes da leitura (2026-10-06) | ABERTA | nenhum |
| [TAREFA_V2_LOBOS_MUNDO](TAREFA_V2_LOBOS_MUNDO.md) | TAREFA V2 — LOBOS-MUNDO (2026-10-04) | ABERTA | nenhum |
| [TAREFA_V2_METABOLISMO](TAREFA_V2_METABOLISMO.md) | TAREFA V2 — METABOLISMO ENERGÉTICO: conversão, reserva e mobilização no corpo (2026-10-08) | ABERTA | nenhum |
| [TAREFA_V2_MUNDO_FISICO](TAREFA_V2_MUNDO_FISICO.md) | Tarefa — V2: o mundo físico mínimo (W-TAREFA-MUNDO, rodada 16) | PROPOSTO | nenhum |
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
| [TAREFA_V2_PET_QUE_PENSA](TAREFA_V2_PET_QUE_PENSA.md) | TAREFA V2 — O PET QUE PENSA (J5): o modelo do desfecho, o mapa da comida e o planejador de um alvo (2026-10-13) | ABERTA | nenhum |
| [TAREFA_V2_PLANO_CALIBRACAO_CONJUNTA](TAREFA_V2_PLANO_CALIBRACAO_CONJUNTA.md) | TAREFA V2 — PLANO-CALIBRACAO-CONJUNTA (2026-10-05) | ABERTA | nenhum |
| [TAREFA_V2_PLANO_COMPARACAO_CEREBROS](TAREFA_V2_PLANO_COMPARACAO_CEREBROS.md) | TAREFA V2 — PLANO-COMPARACAO-CEREBROS (2026-10-05) | ABERTA | nenhum |
| [TAREFA_V2_PLANO_EXPERIMENTO_MAIOR](TAREFA_V2_PLANO_EXPERIMENTO_MAIOR.md) | TAREFA V2 — PLANO-EXPERIMENTO-MAIOR (2026-10-01) | ABERTA | nenhum |
| [TAREFA_V2_REDE_DE_SI](TAREFA_V2_REDE_DE_SI.md) | TAREFA V2 — DIGICORPO (a rede de si): o automodelo em observação (etapa 2 do ego) (2026-10-08) | ABERTA | [RESULTADO_V2_CALIBRACAO_REDE_DE_SI](RESULTADO_V2_CALIBRACAO_REDE_DE_SI.md) |
| [TAREFA_V2_REVISAO_APRENDIZ](TAREFA_V2_REVISAO_APRENDIZ.md) | TAREFA V2 — REVISAO-APRENDIZ (2026-10-04, para a rodada 6) | ABERTA na rodada 6, depois do N5-CEREBRO (`docs/TAREFA_V2_N5_CEREBRO.md`) e da BANCADA-N5… | [RESULTADO_V2_REVISAO_APRENDIZ](RESULTADO_V2_REVISAO_APRENDIZ.md) |
| [TAREFA_V2_SAUDE](TAREFA_V2_SAUDE.md) | TAREFA V2 — RODADA DE SAÚDE: o backup, o CLAUDE.md enxuto, o registro por mês, a bancada em módulos, os hooks e o painel (2026-10-13) | EM CURSO desde 2026-10-13 | nenhum |
| [TAREFA_V2_V1_ADENDO3](TAREFA_V2_V1_ADENDO3.md) | TAREFA V2 — V1-ADENDO3: o orquestrador da validação com o adendo 3 (2026-10-06) | ABERTA | [RESULTADO_V2_VALIDACAO_UNICA](RESULTADO_V2_VALIDACAO_UNICA.md) |
| [TAREFA_V2_V1_LIGAR](TAREFA_V2_V1_LIGAR.md) | TAREFA V2 — V1-LIGAR: faixa nova, P2d e P3i ligados, e a run (2026-10-06) | ABERTA | [RESULTADO_V2_VALIDACAO_UNICA](RESULTADO_V2_VALIDACAO_UNICA.md) |
| [TAREFA_V2_V1_VALIDACAO_UNICA](TAREFA_V2_V1_VALIDACAO_UNICA.md) | TAREFA V2 — V1-VALIDACAO-UNICA (2026-10-06) | ABERTA | [RESULTADO_V2_VALIDACAO_UNICA](RESULTADO_V2_VALIDACAO_UNICA.md) |
| [TAREFA_V2_W_PLANO_PORTE](TAREFA_V2_W_PLANO_PORTE.md) | TAREFA V2 — W-PLANO-PORTE: o plano do porte do cérebro A para a web, pets v11 (2026-10-07) | ABERTA | nenhum |
| [TAREFA_V2_W_PORTE_CEREBRO_A](TAREFA_V2_W_PORTE_CEREBRO_A.md) | TAREFA V2 — W-PORTE: o cérebro A no jogo web, com o painel DigiBrain (2026-10-17) | ABERTA, só papel | nenhum |

## 2. Planos de análise (`docs/PLANO_ANALISE_V2_*.md`)

"nenhum" quer dizer só que nenhum `RESULTADO_V2_*.md` cita o plano: o resultado pode estar num adendo do próprio plano.

| plano | título | resultados que o citam |
|---|---|---|
| [PLANO_ANALISE_V2_A1](PLANO_ANALISE_V2_A1.md) | Plano de análise — V2, A1: a bola como primeiro objeto do mundo com consequência | [RESULTADO_V2_A1](RESULTADO_V2_A1.md) |
| [PLANO_ANALISE_V2_BANHEIRO](PLANO_ANALISE_V2_BANHEIRO.md) | Plano de análise — V2: o banheiro, o carinho e o limpador (W-PLANO-BANHEIRO) | nenhum |
| [PLANO_ANALISE_V2_COMPARACAO_CEREBROS](PLANO_ANALISE_V2_COMPARACAO_CEREBROS.md) | Plano de análise — comparação dos DigiBrains A × B × C (K3/V2) | [RESULTADO_V2_CALIBRACAO_CEREBRO_B](RESULTADO_V2_CALIBRACAO_CEREBRO_B.md), [RESULTADO_V2_CALIBRACAO_CEREBRO_C](RESULTADO_V2_CALIBRACAO_CEREBRO_C.md), [RESULTADO_V2_COMPARACAO_CEREBROS](RESULTADO_V2_COMPARACAO_CEREBROS.md) |
| [PLANO_ANALISE_V2_CORPO_DRIVES](PLANO_ANALISE_V2_CORPO_DRIVES.md) | Plano de análise — V2: o P1 com o corpo e os drives novos | [RESULTADO_V2_CALIBRACAO_CORPO](RESULTADO_V2_CALIBRACAO_CORPO.md) |
| [PLANO_ANALISE_V2_DOIS_PETS](PLANO_ANALISE_V2_DOIS_PETS.md) | Plano de análise — V2: dois pets, o degrau 1 (o B aprende o que só o A viveu?) | nenhum |
| [PLANO_ANALISE_V2_EXPERIMENTO_MAIOR](PLANO_ANALISE_V2_EXPERIMENTO_MAIOR.md) | Plano de análise — o experimento maior (plasticidade por fonte × condição do mundo) | [RESULTADO_V2_VALIDACAO_UNICA](RESULTADO_V2_VALIDACAO_UNICA.md) |
| [PLANO_ANALISE_V2_GPU_ESTILO](PLANO_ANALISE_V2_GPU_ESTILO.md) | Plano de análise — GPU-ESTILO: o estilo da espécie com o corpus em português (V2, fase 0) | nenhum |
| [PLANO_ANALISE_V2_L1](PLANO_ANALISE_V2_L1.md) | Plano de análise — V2, L1: o lobo de decisão aprende com o feedback como vantagem | [RESULTADO_V2_L1](RESULTADO_V2_L1.md) |
| [PLANO_ANALISE_V2_MUNDO_ALVO](PLANO_ANALISE_V2_MUNDO_ALVO.md) | Plano de análise — V2: o mundo físico com o alvo aprendido (aprender para onde ir ajuda a procurar?) | [RESULTADO_V2_VALIDACAO_MUNDO_ALVO](RESULTADO_V2_VALIDACAO_MUNDO_ALVO.md) |
| [PLANO_ANALISE_V2_MUNDO_FISICO](PLANO_ANALISE_V2_MUNDO_FISICO.md) | Plano de análise — V2: o P1 no mundo físico mínimo | [RESULTADO_V2_CALIBRACAO_MUNDO](RESULTADO_V2_CALIBRACAO_MUNDO.md), [RESULTADO_V2_VALIDACAO_MUNDO](RESULTADO_V2_VALIDACAO_MUNDO.md) |
| [PLANO_ANALISE_V2_N3](PLANO_ANALISE_V2_N3.md) | Plano de análise — V2, N3: a consequência da própria ação como sinal (braço P1) | [RESULTADO_V2_N3](RESULTADO_V2_N3.md) |
| [PLANO_ANALISE_V2_N4](PLANO_ANALISE_V2_N4.md) | Plano de análise — V2, N4: frutas no mundo, sem aprendizado de política | [RESULTADO_V2_N4](RESULTADO_V2_N4.md) |
| [PLANO_ANALISE_V2_N5](PLANO_ANALISE_V2_N5.md) | Plano de análise — N5: o dono informa, o mundo valida ou refuta (braços P2 e P2e) | nenhum |
| [PLANO_ANALISE_V2_N6](PLANO_ANALISE_V2_N6.md) | Plano de análise — N6: memória de episódios no mundo das frutas (quatro marcos) | nenhum |
| [PLANO_ANALISE_V2_N7](PLANO_ANALISE_V2_N7.md) | Plano de análise — N7: arbitragem entre duas prioridades (a necessidade do pet × o pedido do dono) | nenhum |
| [PLANO_ANALISE_V2_PET_QUE_PENSA](PLANO_ANALISE_V2_PET_QUE_PENSA.md) | Plano de análise — V2: o pet que pensa (J5), o planejador de um alvo passa nos dois testes da DS-1? | [RESULTADO_V2_CALIBRACAO_PET_QUE_PENSA](RESULTADO_V2_CALIBRACAO_PET_QUE_PENSA.md), [RESULTADO_V2_CALIBRACAO_PET_QUE_PENSA_PALADAR](RESULTADO_V2_CALIBRACAO_PET_QUE_PENSA_PALADAR.md) |
| [PLANO_ANALISE_V2_REDE_DE_SI](PLANO_ANALISE_V2_REDE_DE_SI.md) | Plano de análise — V2: a rede de si em observação (etapa 2 do ego) | [RESULTADO_V2_CALIBRACAO_REDE_DE_SI](RESULTADO_V2_CALIBRACAO_REDE_DE_SI.md) |
| [PLANO_ANALISE_V2_REVISAO_APRENDIZ](PLANO_ANALISE_V2_REVISAO_APRENDIZ.md) | Plano de análise — revisão do aprendiz: teto, janela de crédito ou exposição? | [RESULTADO_V2_REVISAO_APRENDIZ](RESULTADO_V2_REVISAO_APRENDIZ.md) |
| [PLANO_ANALISE_V2_TRANSFERENCIA_REJEICAO](PLANO_ANALISE_V2_TRANSFERENCIA_REJEICAO.md) | Plano de análise — V2: a transferência da rejeição da escolha para o item único (DS-3) | nenhum |
| [PLANO_ANALISE_V2_VINCULO](PLANO_ANALISE_V2_VINCULO.md) | Plano de análise — vínculo B (previsibilidade + desejo) em vidas novas | nenhum |

## 3. Os últimos 10 desvios registrados

Do índice [REGISTRO_DESVIOS.md](REGISTRO_DESVIOS.md) (242 entradas), na ordem em que entraram.

- [2026-10-14 — ECOSSISTEMA-GENETICO (worker C): o desenho do genoma da V2 e das três formas de gerar o genoma de outro](registro/2026-10.md)
- [2026-10-14 — PET-QUE-PENSA-PALADAR, a run (worker D): a calibração do `ganho_gosto` e do `g_plano`, a G-REVAL-POSSIVEL e o piloto](registro/2026-10.md)
- [2026-10-14 — J5-ADENDO-5 (worker C): a fruta ao lado da ração, e as decisões EG marcadas](registro/2026-10.md)
- [2026-10-14 — FRUTA-AO-LADO (worker A): o dono põe a fruta ao lado da ração, o lado do mundo e do dono](registro/2026-10.md)
- [2026-10-17 — CONNECTOME-CEREBRO-A (worker de uma sessão lateral): o cérebro A desenhado como grafo dos pesos](registro/2026-10.md)
- [2026-10-17 — W-PORTE, etapa 1 (esta sessão, coordenador e worker): o ponto do v11 e os gabaritos do cérebro A](registro/2026-10.md)
- [2026-10-18 — W-PORTE, etapa 3 (worker de uma sessão lateral): o G-PAR-L1 pelos ganchos do cérebro, sem o laço do corpo](registro/2026-10.md)
- [2026-10-18 — DECISOES-1018 (worker C): PW-3 a PW-8, CN-1 a CN-9 e PJ5-1 a PJ5-6 marcadas; o painel e o roadmap](registro/2026-10.md)
- [2026-10-18 — PQP-AO-LADO (worker D): a bancada do adendo 5 do J5, a fruta ao lado da ração nos braços e a calibração montada](registro/2026-10.md)
- [2026-10-18 — INFRA-MULTIAGENTE (esta sessão, coordenador e worker): o relato verificado por categoria e o estado derivado](registro/2026-10.md)
