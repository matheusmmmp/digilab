# PAINEL V2: onde a pesquisa está, em uma página

**Atualizado em 2026-10-13** (`main` `ec09483`).
- Quem atualiza: o coordenador, no fim de cada rodada.
- Regra (`docs/TAREFA_V2_SAUDE.md`, etapa 5): cada linha cita o documento de onde veio, e aqui não entra número novo.
- O detalhe de cada marco está na seção 8 do `docs/ROADMAP_V2.md`.

## 1. Os marcos

| marco | em uma linha | estado |
|---|---|---|
| J1 mundo físico | o pet explora o mapa e acha comida e bola | **validado, negativo**: o P1 perde do instinto. **O alvo aprendido atrapalha** (#296): o déficit fica maior com ele, e a perda some com o cuidado fixo |
| J2 corpo químico | drives como químicos, digestão, Vida, metabolismo | código pronto (etapas 1 a 8). A calibração fecha só com o passo 0: `m_gasto` 4/5 fechou (#293). O resto vai para a calibração final. A validação não rodou |
| J3 sem elogio e bronca | o pet aprende pela consequência; o carinho e o tapa são gestos no corpo | feito na pesquisa; no produto, numa versão de pet futura |
| J4 banheiro | aprender o lugar certo; o carinho pesa mais que o limpador | código pronto; poucos alívios dentro (14% a 21% na fumaça). As saídas estão sem decisão, e nada rodou |
| J5 pet que pensa | prever consequências e planejar | etapas 0 a 4 na `main` (o planejador #294, a bancada #295). Falta ligar o planejador na bancada (o nó `planejador` ainda trava os três braços); depois, as runs |
| J6 ego | o automodelo com corpo (a rede de si) | etapas 0 a 2 na `main`; faltam a 2b e a bancada |
| J6a livre × condicionado | as frases-modelo só num braço de comparação | decidido (E-11) |
| J7 dois pets | dois pets de verdade no mesmo mundo | degrau 1 pronto no código. A calibração do K não fechou: **inconclusivo por premissa** até um pet aprender no mundo físico |
| J8 cognição social | informação, reputação, normas, tradição | ideia |
| J9 ego social | orgulho, reputação, comparação | ideia |
| J10 órgãos e hormônios | dano, cura, morte | adiado (D-5, D-6) |

## 2. As runs, uma linha cada

| run | resultado | onde |
|---|---|---|
| L1, o lobo de decisão aprende | G3, G4, G5 e G6 falham: o ensino chega, mas o instinto decide 80% das vezes | `docs/RESULTADO_V2_L1.md` |
| A1, a bola | 1a-pet passa (Δp +0,310); o cuidado controlado falha, pelo dono aleatório | `docs/RESULTADO_V2_A1.md` |
| Vínculo B | o gate passa: atencioso − aleatório +0,171 [+0,046; +0,280] | `artifacts_v2_vinculo_novo/validacao/` |
| N3, a consequência | G-P1 e G6 falham na validação | `docs/RESULTADO_V2_N3.md` |
| N4, as frutas | G-F7 passa; G-SEP e G-SSE falham | `docs/RESULTADO_V2_N4.md` |
| Revisão do aprendiz | diagnóstico: o teto segura; o gargalo é comer sem saber qual fruta está ali | `docs/RESULTADO_V2_REVISAO_APRENDIZ.md` |
| K2, calibração conjunta | o ponto foi escolhido; o N saiu pelo poder simulado (30) | `docs/RESULTADO_V2_CALIBRACAO_CONJUNTA.md` |
| Validação única (#193) | predições 1, 2 e 5 confirmam; a 3 confirma pelo contraste, mas não conta como ensino; a 4 fica inconclusiva | `docs/RESULTADO_V2_VALIDACAO_UNICA.md` |
| Calibração do cérebro B | não aprende: sai da comparação | `docs/RESULTADO_V2_CALIBRACAO_CEREBRO_B.md` |
| Calibração do cérebro C | fecha | `docs/RESULTADO_V2_CALIBRACAO_CEREBRO_C.md` |
| Comparação A × C (#197) | empate em CC-1 e CC-2. Pela regra (M6) o escolhido seria o C, por pouco; o A ficou (rodada 15) | `docs/RESULTADO_V2_COMPARACAO_CEREBROS.md` |
| Descritivo do platô (#199) | misto: o A aprende qual fruta evitar na escolha, mas come a ruim quando está sozinha | `docs/DESCRITIVO_V2_PLATO.md` |
| Mundo, calibração | `m` = 1, N = 40 | `docs/RESULTADO_V2_CALIBRACAO_MUNDO.md` |
| Mundo, validação (#285) | o G-MUNDO passa; o P1 perde do instinto em `D_FE`, também com o cuidado fixo | `docs/RESULTADO_V2_VALIDACAO_MUNDO.md` |
| Corpo, calibração (#286) | duas faixas não fecharam; decidido: fecha só com o passo 0 | `docs/RESULTADO_V2_CALIBRACAO_CORPO.md` |
| Corpo, passo 0 fino (#293) | `m_gasto` 4/5 fecha: a falta em 0,2018 do tempo acordado; a grade da solidão não rodou | `docs/RESULTADO_V2_CALIBRACAO_CORPO.md`, adendo 5 |
| Mundo com o alvo aprendido (#296) | as premissas passam; **o alvo atrapalha**: P1 − P1-alvo −0,0063 [−0,0105; −0,0022]; com o cuidado fixo, −0,0003 [−0,0047; +0,0042] | `docs/RESULTADO_V2_VALIDACAO_MUNDO_ALVO.md` |
| Dois pets, calibração do K (#287) | não fecha: o A sozinho fica com R_A perto de 1/3 em todo K | `docs/PLANO_ANALISE_V2_DOIS_PETS.md`, adendo 1.2 |

## 3. Decisões abertas do Matheus

- **SA-3 a SA-8:** a rodada de saúde (`docs/TAREFA_V2_SAUDE.md`, seção 6). SA-1 e SA-2 decididas em 2026-10-13. A etapa 0 (o backup) está
  na `main` (#297); a 1 (o CLAUDE.md enxuto) espera o checklist do Matheus; a 2 só começa com o ok dele.
- **FE-3:** o perfil de cada brasão (`docs/futuro/fisiologia_especies.md`).
- **As saídas do banheiro:** sem decisão até haver dado (`docs/PLANO_ANALISE_V2_BANHEIRO.md`, seção 7).
- **A validação do corpo:** espera a calibração final e um sim.
- **O J5:** a calibração do `g_plano` e a validação esperam o planejador ligado na bancada.
- **O porte do cérebro A para a web (v11, #201):** pausado até o J5.

## 4. Riscos

| risco | o que se vê hoje | onde |
|---|---|---|
| O aprendiz não aprende no mundo físico | o P1 perde do instinto (J1), e o A sozinho não sai de 1/3 (J7). O alvo aprendido também perdeu (#296); resta o J5 | J1, J7 |
| O crédito entre decisões | a janela imediata ensina a comer e a poupar energia, não a procurar | `docs/RESULTADO_V2_VALIDACAO_MUNDO.md` |
| O teto de pesos | o degrau 1 tem 990 de 1000, e o banheiro 998. O teto por plano existe (TP-1, TP-2); falta medir o custo do replay com um cérebro maior | `docs/DECISAO_V2_TETO_PESOS.md` |
| O desempate do cheiro fora do motor | a calibração e a validação do mundo rodaram com a ordem fixa | `docs/RESULTADO_V2_CALIBRACAO_MUNDO.md` |
| O rótulo "pensa" | o J5 mede previsão e planejamento; não pode virar alegação de pensamento | `docs/futuro/pet_que_pensa.md` |
| A saúde do repositório | o CLAUDE.md passa de 4.169 a 114 linhas na etapa 1 (PR em revisão); o registro e o CLAUDE.md causam os conflitos de merge; a bancada tem 4.038 linhas num arquivo | `docs/TAREFA_V2_SAUDE.md`, seção 1 |
| O custo | a suíte inteira leva ~36 min | `docs/RESULTADO_V2_VALIDACAO_MUNDO.md`, seção 8 |
