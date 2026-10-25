# PAINEL V2: onde a pesquisa está, em uma página

**Atualizado em 2026-10-24** (`main` `644309c`), pelo PROMPT MESTRE. Nesta atualização entram a direção nova (a seção 0), a competição (#393, #396), o estado do porte W, o Gate I e a P4. O resto é o da atualização anterior.

## 0. A direção e o produto (2026-10-24)

| pergunta | resposta | onde |
|---|---|---|
| Qual é o produto mínimo que será desenvolvido primeiro? | **o MVP:** um jogador e um pet no navegador. O jogador põe a comida num lugar do cenário (arrastando ou por um caminho acessível), e o pet a percebe, vai, come e sente no corpo, com tudo no log e no replay | `docs/PRODUTO_VISAO.md`; `docs/TAREFA_V2_MVP_MUNDO_PRODUTO.md` |
| Qual é a direção definida do cérebro? | **o DigiBrain modular** (DECIDIDO pelo Matheus em 2026-10-24); os detalhes técnicos são PROPOSTOS (DM-1 a DM-9) | `docs/ARQUITETURA_DIGIBRAIN_MODULAR.md` |
| O que o cérebro A é? | **linha de base e controle, e fallback condicionado; não é o cérebro final.** Hoje ele ainda decide os pets v11 do jogo, e continua assim até o modular entrar. "Um DigiBrain na web, o A" e o M6 estão SUPERADOS | `docs/TAREFA_V2_CEREBRO_A_BASELINE.md` |
| Que evidência justificaria recorrer ao A como fallback? | só depois de um protótipo representativo, com os testes de mecanismo, a ablação e a aprendizagem resolvidos (D1, D2, D4), e com o oráculo mostrando que a arquitetura não expressa o comportamento do MVP (D3) ou o custo não cabendo no navegador depois da otimização (D5). **Perder do A sozinho (D6) não basta.** A decisão é do Matheus | `docs/TAREFA_V2_CEREBRO_A_BASELINE.md`, seção 3 |
| Quais módulos, órgãos e sinais estão implementados, em pesquisa ou só planejados? | **Módulos:** nenhum módulo do modular existe; existem peças candidatas (o instinto, a L1, o planejador, a disputa, o N6). **No jogo (v11):** o Sistema neuroquímico, a homeostase, o tato (carinho e tapa), a dor, o susto, o sono, o tédio, a solidão, o estresse, o metabolismo e a digestão. **Só na pesquisa:** a visão, o olfato pela leitura pronta, o paladar, o tato social, a curiosidade e o banheiro. **Implementados e não integrados:** as narinas, os ouvidos e a Vida. **Planejados:** os hormônios, o proprioceptivo, a termorregulação, o imune e o reparo | `docs/AUDITORIA_V2_PRODUTO_MODULAR.md`, seções 2 e 5; `docs/DEFINICOES_CORPO_V2.md`, seção 7 |
| A memória autobiográfica afeta decisões e personalidade hoje? | **não.** A história só alimenta a fala; só o N6 decide (a fruta), fora do jogo; nenhuma memória muda a personalidade; não há memória central. **A tarefa** é a da memória autobiográfica (etapas M0 a M7), e **o gate** é a validação causal REL contra SEM, REC e EMB, com plano antes | `docs/TAREFA_V2_MEMORIA_AUTOBIOGRAFICA.md` |
| Qual é o próximo marco para o pet perceber e buscar a comida no cenário? | **o MVP está na `main`** (2026-10-24: #401, #403, #404): o pet v12 com o `Mundo` no laço, o evento `dc` no log, o G-PAR do laço, a tela com o gesto "Pôr ração" e o caminho acessível. **A ressalva de produto:** o A vai pouco à comida (1 ou 2 refeições em vidas de 2 dias, diagnóstico); o próximo marco é **o protótipo do cérebro modular**, não mexer no A | `docs/TAREFA_V2_MVP_MUNDO_PRODUTO.md` |
| Qual é o estado real dos sprites e das regras? | **os sprites do Digimon UP estão autorizados pelo Matheus, em decisão DEFINITIVA** (2026-10-22 e duas vezes em 2026-10-24; não volta como pendência, pergunta ou bloqueio). Vale a regra de procedência. O atlas fica fora do git, e o e2e roda com o sprite de reserva. Os textos de tela e os comentários que ainda dizem "uso pessoal" são trocados pela etapa 2 do MVP (MV-6, DECIDIDA) | `docs/UI_GUIDELINES.md`, seção 5.1; `docs/AUDITORIA_V2_PRODUTO_MODULAR.md`, seção 7 |
| Que rodadas precisam ser interrompidas ou repensadas? | **pausar:** o piloto e a validação da P4 (o #395 continua aberto, sem run) e a run do Gate I com o A. **Não abrir:** o T2 do J5 só para o A. **Já paradas ou encerradas:** a V3-9 e a V3-3/4. **Manter:** o contrato do motor, os critérios do Gate I e o A no jogo. Tudo isso é a recomendação DM-8, que espera o Matheus | `docs/AUDITORIA_V2_PRODUTO_MODULAR.md`, seção 9 |
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
| J5 pet que pensa | prever consequências e planejar | **a validação do adendo 8 (#370): o G-T1 passa**, o primeiro primário do J5 a passar: `q`(P1-plan) − `q`(P1) = 0,197, IC95 [0,075; 0,323], o Holm rejeita. O G-T2 é inconclusivo por premissa; o G-T1-DESF passa e o G-T1-CONG não; o rótulo "pensa" (R-7) não vale (`docs/RESULTADO_V2_VALIDACAO_PET_QUE_PENSA_ADENDO8.md`). **O Gate C APROVADO EM PARTE pelo Matheus em 2026-10-21:** a revalorização pelo planejador está demonstrada; a busca (o T2) fica pendente, com plano próprio |
| J6 ego | o automodelo com corpo (a rede de si) | etapas 0 a 2 na `main`; faltam a 2b e a bancada |
| J6a livre × condicionado | as frases-modelo só num braço de comparação | decidido (E-11) |
| J7 dois pets | dois pets de verdade no mesmo mundo | degrau 1 pronto no código. A calibração do K não fechou: **inconclusivo por premissa** até um pet aprender no mundo físico |
| J8 cognição social | informação, reputação, normas, tradição | ideia |
| J9 ego social | orgulho, reputação, comparação | ideia |
| J10 órgãos e hormônios | dano, cura, morte | adiado (D-5, D-6) |
| W porte do cérebro A (v11) | o cérebro A no jogo web, com o painel DigiBrain | **entregue:** as etapas 1 a 5 e o mapa dos pesos (`docs/TAREFA_V2_W_PORTE_CEREBRO_A.md`, seções 9 a 18). Desde 2026-10-24, o A fica no jogo para os pets v11 e como fallback condicionado, não como o cérebro final |
| connectome do cérebro A | o grafo dos pesos e dos motivos de cada decisão | ferramenta de pesquisa (#321, `tools/connectome_cerebro_a.py`); CN-1 a CN-9 decididas em 2026-10-18: fora do jogo até o J5 (`docs/futuro/connectome_cerebro_a.md`) |
| mundo 3D (WORLD-POC-001) | a vista inclinada em Three.js sobre o mundo físico, com a física em inteiros no motor | investigação feita; W-1 a W-7 decididas em 2026-10-18 pela recomendação; o POC-01a entregue (#355, #358); **o Gate A APROVADO em 2026-10-19** (ressalvas: um celular só; o cérebro real espera o Gate C); o POC-02 entregue (#362, #363); **o Gate B APROVADO em 2026-10-19** (ressalva: o cérebro de teste, só em TS); **a P4 liberada com o planejador em 2026-10-21** (o Gate C em parte), com o esboço da tarefa em `docs/TAREFA_V2_P4_CEREBRO_MUNDO.md` as P4-1 a P4-8 DECIDIDAS (2026-10-21); as etapas 0 a 3 da P4 na `main` (o contrato no motor, Python e TS, #384, #390, #394); o #395 (o adendo 1, parte A) aberto, sem run. **Desde 2026-10-24:** o contrato serve ao MVP, e o piloto e a validação do A estão em pausa pela recomendação DM-8 |
| Gate I, o pet integrado | o mesmo pet recebe o corpo químico, percebe e age no mundo, aprende na vida e refaz a vida pelo log | marco decidido, **não implementado** (GI-1 a GI-5, GT-1 a GT-8 decididas em 2026-10-21); **repensado em 2026-10-24:** os critérios servem ao pet modular, e a GI-1 ("ao redor do A") está superada (`docs/futuro/gate_integracao_pet.md`) |
| MVP, o mundo no jogo | o jogador põe a comida num lugar; o pet percebe, vai, come e sente no corpo | **etapas 0, 1 e 2 na `main`** (#401, #403, #404, 2026-10-24: os gabaritos; o pet v12 com o mundo, o G-PAR e o layout sem árvores só do produto; a tela com o gesto e o caminho acessível, a MV-6 aplicada); MV-1..10 DECIDIDAS. A ressalva de produto registrada: o A vai pouco à comida, e isso vai ao protótipo modular (`docs/TAREFA_V2_MVP_MUNDO_PRODUTO.md`, seção 9) |
| DigiBrain modular | o cérebro modular do produto | **direção decidida** (2026-10-24); a arquitetura e as tarefas PROPOSTAS (`docs/ARQUITETURA_DIGIBRAIN_MODULAR.md`); nenhum código |

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
| J5 com a fruta ao lado, calibração (#334) | o `ganho_gosto` e o `g_plano` fecham; as margens passam; N = 50, com o poder declarado | `docs/RESULTADO_V2_CALIBRACAO_PET_QUE_PENSA_AO_LADO.md` |
| J5, validação (#342) | **inconclusiva por premissa** nos dois primários (T1: oportunidade; T2: nenhuma busca) | `docs/RESULTADO_V2_VALIDACAO_PET_QUE_PENSA.md` |
| J5, piloto do adendo 7 (#349) | **parado pela G-OPORTUNIDADE** (T1 do P1 e T2): o corte pela x comida numa árvore, não a janela | `docs/RESULTADO_V2_PILOTO_PET_QUE_PENSA_ADENDO7.md` |
| J5, piloto do adendo 8 (#364) | as premissas do T1 passam pela primeira vez; as do T2 falham; `Δ_T1` = 0,258, `Δ_T2` = 0,323, K_u = 10. O Matheus mandou validar com o T1 como primário (adendo 9) | `docs/RESULTADO_V2_PILOTO_PET_QUE_PENSA_ADENDO8.md` |
| J5, validação do adendo 8 (#370) | **o G-T1 passa** (0,197, IC95 [0,075; 0,323]); o G-T2 inconclusivo por premissa; o G-T1-DESF passa, o G-T1-CONG não. O Gate C aprovado em parte (2026-10-21) | `docs/RESULTADO_V2_VALIDACAO_PET_QUE_PENSA_ADENDO8.md` |
| Competição entre regras, piloto (#393) | a G-ABRE passa; K = 10 e N = 50, com o poder de 0,49 declarado | `docs/RESULTADO_V2_PILOTO_COMPETICAO.md` |
| Competição entre regras, validação (#396) | **todos os gates passam:** G-R1 0,0124 [0,0093; 0,0156], "a disputa ajuda, e o aprendido usa a abertura"; só no v11 sem o mundo | `docs/RESULTADO_V2_VALIDACAO_COMPETICAO.md` |

## 3. Decisões abertas do Matheus

- **A rodada de saúde:** as etapas 0 a 4 estão na `main` (#297, #300, #307, #312, #313). O Matheus manteve a `Bancada` inteira (SA-4) e ligou
  os hooks H1, H1b e H3, com o H2 desligado (2026-10-14). A tabela da seção 6 de `docs/TAREFA_V2_SAUDE.md` ainda não registra isso.
- **FE-3:** o perfil de cada brasão (`docs/futuro/fisiologia_especies.md`).
- **As saídas do banheiro:** sem decisão até haver dado (`docs/PLANO_ANALISE_V2_BANHEIRO.md`, seção 7).
- **A validação do corpo:** espera a calibração final e um sim.
- **O J5:** o Gate C foi aprovado em parte (2026-10-21). A busca (o T2, o mapa) espera um plano próprio, ainda sem tarefa.
- **A direção nova (2026-10-24):**
  - a arquitetura modular: DM-1 a DM-9 (`docs/ARQUITETURA_DIGIBRAIN_MODULAR.md`, seção 13);
  - o MVP: MV-1 a MV-9 (`docs/TAREFA_V2_MVP_MUNDO_PRODUTO.md`): todas DECIDIDAS em 2026-10-24 (a MV-6 por decisão definitiva do Matheus sobre os sprites);
  - a memória autobiográfica: ME-1 a ME-7 (`docs/TAREFA_V2_MEMORIA_AUTOBIOGRAFICA.md`);
  - o A como baseline e fallback: AF-1 a AF-6 (`docs/TAREFA_V2_CEREBRO_A_BASELINE.md`).
- **A P4:** as P4-1 a P4-8 decididas; o #395 aberto; o piloto e a validação em pausa pela DM-8, DECIDIDA em 2026-10-24.
- **O crédito por canal (V3-9):** as CC-1 a CC-6 DECIDIDAS em 2026-10-21, pela recomendação (`docs/TAREFA_V2_V3_CREDITO_CANAL.md`, seção 8); a etapa 0 (as tabelas sombra) é a porta, e as faixas 56101…56505 e 57101…57505 estão decididas (entram na `FAIXAS_RESERVADAS` com a etapa 0).
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
