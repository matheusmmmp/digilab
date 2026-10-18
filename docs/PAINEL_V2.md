# PAINEL V2: onde a pesquisa está, em uma página

**Atualizado em 2026-10-18** (`main` `66bc21b`). Nesta atualização mudaram só o J5, o porte (W), o connectome, as decisões abertas e o risco da saúde do repositório; o resto é o de 2026-10-13.
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
| J5 pet que pensa | prever consequências e planejar | código pronto (etapas 0 a 4). Duas rodadas voltaram ao Matheus com o T1 sem margem (#301; com o paladar, #316). **Agora, o adendo 5** (#317): o dono põe as três frutas ao lado da ração, e o T1 mede a escolha lado a lado; PJ5-1 a PJ5-6 decididas em 2026-10-18. O mundo e o dono estão na `main` (#318); falta a bancada do J5 com a fruta ao lado (o D), e a run pede o sim do Matheus |
| J6 ego | o automodelo com corpo (a rede de si) | etapas 0 a 2 na `main`; faltam a 2b e a bancada |
| J6a livre × condicionado | as frases-modelo só num braço de comparação | decidido (E-11) |
| J7 dois pets | dois pets de verdade no mesmo mundo | degrau 1 pronto no código. A calibração do K não fechou: **inconclusivo por premissa** até um pet aprender no mundo físico |
| J8 cognição social | informação, reputação, normas, tradição | ideia |
| J9 ego social | orgulho, reputação, comparação | ideia |
| J10 órgãos e hormônios | dano, cura, morte | adiado (D-5, D-6) |
| W porte do cérebro A (v11) | o cérebro A no jogo web, com o painel DigiBrain | saiu da pausa em 2026-10-17. Etapas 0 a 2 na `main` (#320, #322, #323: o plano, os gabaritos do Python e o núcleo em TS com o G-PAR-L0); o A na etapa 3 (o aprendizado pela consequência do corpo); o B na PW-3 (a vontade) e na PW-4 (o caráter), primeiro no Python. PW-1 a PW-8 decididas (`docs/TAREFA_V2_W_PORTE_CEREBRO_A.md`) |
| connectome do cérebro A | o grafo dos pesos e dos motivos de cada decisão | ferramenta de pesquisa (#321, `tools/connectome_cerebro_a.py`); CN-1 a CN-9 decididas em 2026-10-18: fora do jogo até o J5 (`docs/futuro/connectome_cerebro_a.md`) |

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
| J5, calibração e piloto (#301) | o `g_plano` fecha; o T1 fica sem margem: nenhum braço escolhe a x antes da mudança | `docs/RESULTADO_V2_CALIBRACAO_PET_QUE_PENSA.md` |
| J5 com o paladar (#316) | o `ganho_gosto` não fecha; a G-REVAL-POSSIVEL passa; o T1 de novo sem margem | `docs/RESULTADO_V2_CALIBRACAO_PET_QUE_PENSA_PALADAR.md` |

## 3. Decisões abertas do Matheus

- **A rodada de saúde:** as etapas 0 a 4 estão na `main` (#297, #300, #307, #312, #313). O Matheus manteve a `Bancada` inteira (SA-4) e ligou
  os hooks H1, H1b e H3, com o H2 desligado (2026-10-14). A tabela da seção 6 de `docs/TAREFA_V2_SAUDE.md` ainda não registra isso.
- **FE-3:** o perfil de cada brasão (`docs/futuro/fisiologia_especies.md`).
- **As saídas do banheiro:** sem decisão até haver dado (`docs/PLANO_ANALISE_V2_BANHEIRO.md`, seção 7).
- **A validação do corpo:** espera a calibração final e um sim.
- **O J5:** a run do adendo 5 (calibração e piloto em 51101…51505) pede o sim do Matheus, depois da bancada do D.
- **O ecossistema genético:** EG-1 a EG-8 decididas (2026-10-14); cada passo G0 a G5 entra com tarefa e plano próprios (`docs/futuro/ecossistema_genetico.md`).

## 4. Riscos

| risco | o que se vê hoje | onde |
|---|---|---|
| O aprendiz não aprende no mundo físico | o P1 perde do instinto (J1), e o A sozinho não sai de 1/3 (J7). O alvo aprendido também perdeu (#296); resta o J5 | J1, J7 |
| O crédito entre decisões | a janela imediata ensina a comer e a poupar energia, não a procurar | `docs/RESULTADO_V2_VALIDACAO_MUNDO.md` |
| O teto de pesos | o degrau 1 tem 990 de 1000, e o banheiro 998. O teto por plano existe (TP-1, TP-2); falta medir o custo do replay com um cérebro maior | `docs/DECISAO_V2_TETO_PESOS.md` |
| O desempate do cheiro fora do motor | a calibração e a validação do mundo rodaram com a ordem fixa | `docs/RESULTADO_V2_CALIBRACAO_MUNDO.md` |
| O rótulo "pensa" | o J5 mede previsão e planejamento; não pode virar alegação de pensamento | `docs/futuro/pet_que_pensa.md` |
| A saúde do repositório | o CLAUDE.md tem 107 linhas (era 4.169); o registro está por mês, com `merge=union` nos arquivos do mês; a bancada é um pacote de módulos, com a fachada `bancada_v2.py` | `docs/TAREFA_V2_SAUDE.md`, seções 8 e 9 |
| O custo | a suíte inteira leva ~36 min | `docs/RESULTADO_V2_VALIDACAO_MUNDO.md`, seção 8 |
