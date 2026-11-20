# Leitura parcial da V2, fase 1 (2026-10-05)

Tarefa `docs/TAREFA_V2_LEITURA_PARCIAL.md`. **Só papel:** nenhuma run, nenhum código, nenhuma releitura de dado gravado com medida nova.
Todo número aponta o artefato. Não reabre a v1 nem a pergunta do dono (`docs/LEITURA_CONSOLIDADA_DONO.md`). Nenhuma alegação de
novidade. Não antecipa o experimento maior (`docs/PLANO_ANALISE_V2_EXPERIMENTO_MAIOR.md`).

**Por que esta leitura existe.** Em 2026-10-01 o Matheus decidiu que a V2 segue com gates falhando e que as validações iniciais seriam
revistas. Desde então o desenho mudou em cinco pontos:
- **teto 16·S** (T3, decisão R1);
- **E2:** o humor da fruta entra no sinal do P1;
- **os lobos veem a bola e as frutas;**
- **a decisão de comer vê qual fruta está no cenário** (R2);
- **B1 e B2:** o aleatório não põe bola, e a bola fica fora do orçamento.

Este documento diz, nó a nó, o que passou e o que falhou, o que cada mudança toca e quais validações refazer, em que ordem e com que
sementes.

---

## 1. O que passou e o que falhou, por nó

### 1.1 L0: a política com lobos, aprendizado desligado (2026-10-01)

| gate | resultado | artefato |
|---|---|---|
| G2: lobos desligados = instinto byte a byte (2 motores, 4 donos × 5 sementes, as 7 regras) | **passa** | `tests/test_lobos.py` |
| G1: replay bit a bit, estado interno incluído | **passa** | idem |

### 1.2 L1: o lobo de decisão aprende do dono, braço P3 (validação 4101…4505, passo 512, teto 1·S, mundo padrão)

| gate | resultado | número | artefato |
|---|---|---|---|
| G3: divergência atencioso × relapso ≥ 0,10 bit | **falha** | 0,041 bit [0,026; 0,062] | `artifacts_v2_l1/validacao/ponto/resultado.json` (`gates.G3`) |
| G4: o aprendido decide com fator ≥ 50% | **falha** | 0,182 [0,145; 0,236]; bruto 0,703 | idem (`gates.G4`) |
| G5(c): ensino − acoplado | **falha** | +0,0099 [−0,010; +0,025] | `docs/RESULTADO_V2_L1.md`, sobre `artifacts_v2_l1/validacao/ponto/` |
| G6: deriva e teto | **falha pelo teto** | 12 de 20 vidas no teto; razão 14/7 1,45 (passa) | `resultado.json` (`gates.G6`) |
| G3-T (sem gate): acerto na tarefa do atencioso | sobe sobre o instinto | 0,663 × instinto 0,577 | `docs/RESULTADO_V2_L1.md`, `ponto/tarefa.json` |

**Leitura de então** (`docs/RESULTADO_V2_L1.md`): o ensino chega (G3-T, Δα), mas o instinto decide cerca de 80% das decisões e o teto 1·S
limita o resto.

### 1.3 A1: a bola, sem aprendizado (validação 7101…7505, instinto, bola pelo `DonoComBola` dentro do orçamento)

| gate | resultado | número | artefato |
|---|---|---|---|
| 1a-pet: Δp = p(brincar \| bola) − p(brincar \| sem bola) | **passa** | +0,310 [+0,245; +0,375]; bola que o instinto não vê +0,036 [−0,025; +0,107] | `artifacts_v2_a1/validacao/resultado.json` (`resumo.delta_p`, `delta_p_bolacega`) |
| cuidado controlado: privação bola − sem bola | **falha** | IC [+0,009; +0,028], mortes 0 | idem (`gates.cuidado_controlado`) |
| 1a-dono | não testada (D6; exige o aprendiz) | — | idem (`gates.1a_dono`) |

**Causa da falha** (`docs/RESULTADO_V2_A1.md`): só o dono aleatório. Ele sorteia `por_bola` dentro do orçamento e, com o orçamento fixo,
cuida menos.

### 1.4 N3: a consequência como sinal, braço P1 (validação 9101…9505, ganho 4, teto 1·S, mundo padrão)

| gate | resultado | número | artefato |
|---|---|---|---|
| G-P1: privação P0 − P1 > 0 | **falha** | +0,0008 [−0,0067; +0,0077] | `artifacts_v2_n3/validacao/ganho4/resultado.json` (`gates.G_P1_privacao`) |
| G6: deriva e teto | **falha** | 20 de 20 vidas no teto; razão 1,78 | idem (`gates.G6`) |
| sem mortes novas | passa por construção (o mundo padrão não tem morte) | 0 e 0 | idem |

**Leitura de então** (`docs/RESULTADO_V2_N3.md`): a consequência imediata ensina a comer e a poupar energia, mas a privação depende do
cuidado do dono, e a redução vista na calibração não se repetiu.

### 1.5 N4: frutas no mundo, sem aprendizado (validação 11101…11505, instinto, mundo do N4)

| gate | resultado | número | artefato |
|---|---|---|---|
| G-SEP(i): comer não é função só da fome | passa | +0,094 [+0,049; +0,136] | `docs/RESULTADO_V2_N4.md`, `artifacts_v2_n4/validacao/resultado.json` |
| G-SEP(ii): qual fruta | **falha** (por 0,007) | +0,110 [−0,007; +0,213] | idem |
| G-SSE: saciedade específica | **falha** pelo β_fome | β_fome IC [−0,159; −0,014]; β_recente [−0,901; −0,635] passa | idem (`gates.G-SSE`) |
| G-F7: frutas − acoplado na saúde; mortes | **passa** | IC [−0,008; 0,000]; mortes 0 e 0 | idem (`gates.G-F7`) |

**Causa do G-SSE:** a regressão do plano não tinha a preferência inata, e o β_fome captou a diferença de preferência entre frutas. A
medida corrigida (`metrics.saciedade_especifica_n1`) existe desde o N5-MUNDO e só foi testada em dados sintéticos.

### 1.6 Revisão do aprendiz (só calibração, 18101…18505, K = 4; diagnóstico, sem gate)

| achado | número | artefato |
|---|---|---|
| no descasado o P1 come menos a fruta ruim que o P0 | G_ap +0,109 [+0,050; +0,182] | `docs/RESULTADO_V2_REVISAO_APRENDIZ.md`, `artifacts_v2_revisao/calibracao/base/` |
| no casado o P1 come **mais** a ruim que o P0 | −0,062 [−0,110; −0,018] | idem |
| o teto não muda nada no P1 | Δ M1 e Δ G_ap 0,000 do T1 ao T3 | idem, `avaliacao.json` |
| no P3 o teto 16·S faz o aprendido decidir mais | Δ M1 +0,039 [+0,008; +0,079]; acerto −0,026 [−0,055; −0,001] | idem |
| a janela de crédito e a exposição não ajudam | J3 Δ G_ap −0,027 [−0,041; −0,014]; `w_fruta` 24: −0,064 [−0,106; −0,024] | idem |
| pós hoc: o P1 come a ruim quando ela está sozinha | 55% dos consumos do P1 com uma fruta só | `pos_hoc_oferta_unica.json` |

O último achado deu a decisão R2.

### 1.7 Outros nós e a infraestrutura

| frente | resultado | artefato |
|---|---|---|
| F0, vínculo B (produto) | **gate passa**: atencioso − aleatório +0,171 [+0,046; +0,280] | `artifacts_v2_vinculo_novo/validacao/resumo.json` |
| bancada; bancada com mundos; bancada com frutas; bancada do N5; bancada do experimento maior | gates passam (P0 = instinto byte a byte, G1, acoplados, unidades derivadas, contrastes e Holm em dados sintéticos) | `tests/test_bancada_v2.py`, `test_bancada_mundos.py`, `test_bancada_frutas.py`, `test_bancada_n5.py`, `test_experimento_maior.py` |
| LOBOS-MUNDO, N5-MUNDO, N5-CEREBRO, N5-ACOPLADO, FRUTA-NO-CENARIO (A e B) | gates passam (desligado = antes, byte a byte; G1; espiões) | `tests/test_lobos_mundo.py`, `test_informacao.py`, `test_lobos_n5.py`, `test_n5_acoplado.py`, `test_frutas_cenario.py`, `test_comer_ve_fruta.py` |
| N5, N6, N7, experimento maior | planos registrados; nenhuma run | `docs/PLANO_ANALISE_V2_N5.md`, `_N6.md`, `_N7.md`, `_EXPERIMENTO_MAIOR.md` |

---

## 2. O que mudou desde cada validação, e o que isso toca

| validação | aprendiz e mundo dela | teto 16·S | E2 | lobos veem o mundo | comer vê a fruta | B1/B2 | **refazer?** |
|---|---|---|---|---|---|---|---|
| L1 (4101…4505) | P3, teto 1·S, padrão | **toca**: o G6 falhou pelo teto; na revisão, o T3 fez o aprendido do P3 decidir mais | não (sem fruta) | não (padrão) | não | não | **sim** |
| A1 (7101…7505) | instinto, bola dentro do orçamento | não (sem aprendizado) | não | não: P0 com lobos = instinto byte a byte (`test_bancada_n5.py`) | não | **toca**: a causa da falha era o aleatório pondo bola dentro do orçamento | **sim** |
| N3 (9101…9505) | P1, teto 1·S, padrão | toca o G6 (por construção sai do teto); a revisão não viu efeito do teto no P1 | não (sem fruta) | não | não | não | **opcional** |
| N4 (11101…11505) | instinto, mundo do N4 | não | não | não: byte a byte | não: prior 0, byte a byte (`test_comer_ve_fruta.py`) | não | **não** (o G-SSE só por medida nova) |
| revisão (18101…18505) | P0/P1/P3, frutas da bancada | é a origem do T3 | já tinha a E2 | já via | **toca**: o P1 de antes não via a fruta | não | **não** (diagnóstico de calibração; não há validação a refazer) |

**O que fica valendo sem refazer:**
- **A1:** o 1a-pet. O P0 com lobos é o instinto byte a byte, e a resposta à bola é da predisposição.
- **N4:** G-SEP(i), G-SEP(ii) e G-F7. Nada mudou no P0 das frutas.
- **L0 e a infraestrutura:** a suíte confere tudo a cada PR.

---

## 3. Quais validações refazer, em que ordem e com que sementes

**A regra:** só validação, sem calibração nova, porque o ponto de cada uma já está fixado:
- o T3 saiu da revisão, em sementes de calibração;
- o ponto da A1 e o ganho do N3 saíram das calibrações deles.

Cada refeita tem o mesmo desenho e os mesmos gates e alvos da original (nada relaxado). As faixas são novas, e os artefatos vão para
pastas novas. **Os artefatos antigos não mudam.**

| ordem | refeita | o que muda contra a original | gates | faixa (proposta) | custo |
|---|---|---|---|---|---|
| 1 | **A1-B**: a bola com B1/B2 (mundo `bola` da bancada, instinto) | o aleatório não põe bola; a bola entra pela `RegraBola`, fora do orçamento | 1a-pet e cuidado controlado, como na A1 | **23101…23505** | 5 sementes × 4 donos; a A1 levou 38 s (`artifacts_v2_a1/validacao/meta.json`) |
| 2 | **L1-T3**: o P3 no ponto T3, mundo padrão | teto 16·S no lugar de 1·S | G3, G4, G5, G6 e G3-T, alvos de antes (0,10 bit, 50%) | **24101…24505** | 5 sementes × 4 donos, com os controles da L1; a L1 levou 128 s (`artifacts_v2_l1/validacao/ponto/resultado.json`) |
| 3 (opcional) | **N3-T3**: o P1 no ponto T3, mundo padrão | teto 16·S | G-P1, G6 | **25101…25505** | a N3 levou 439 s (`artifacts_v2_n3/validacao/ganho4/resultado.json`) |
| — (opcional) | **N4-N1**: G-SSE com a medida N1 numa validação nova do mundo do N4 | a medida, não o mundo | G-SSE pela N1 | **27101…27505** | a N4 levou 26 s (`artifacts_v2_n4/validacao/meta.json`) |

**Por que esta ordem:**
- **A1-B primeiro:** é a mais barata, não depende do aprendiz e testa diretamente a causa conhecida da falha. Se o cuidado controlado
  passar, a bola volta a ser um mundo limpo para o experimento maior e para o N11.
- **L1-T3 antes da validação do experimento maior:** o P3 do experimento maior roda no T3. Saber, no mundo padrão, se o teto muda o
  veredito da L1 diz como ler o P3 lá.
- **O N3-T3 é opcional:** a revisão já mostrou que o teto não muda o P1 nas frutas (Δ 0,000). No mundo padrão o G6 sai do teto por
  construção, e a pergunta substantiva do P1 (aprender a evitar a fruta ruim, com a E2 e a fruta vista) passou para o experimento maior.

**Nenhuma das refeitas bloqueia a calibração do N5 (12101…12505) nem a do experimento maior (14101…14505).** As duas são em faixas
próprias, já reservadas e ainda não usadas.

**Faixas:**
- **Fora de toda faixa reservada ou usada:** `FAIXAS_RESERVADAS` de `experiments/bancada_v2.py` (até 20505, mais 50001…82004 e as de
  2026); o N7 (21101…22505, decisão N7-9).
- **Busca feita** no repositório, fora dos artefatos: nenhuma base de 23101…25505 aparece.
- **Por que a 26xxx ficou de fora:** o número 26505 aparece como tick em `web/app/test/gabaritos/vinculo_python.json`. Não é semente,
  mas o plano pula a faixa para não haver confusão.
- **Ao fechar:** entram nas `FAIXAS_RESERVADAS` quando o coordenador as fechar.

---

## 4. O que já dá para dizer sobre a pergunta maior, e o que não dá

**A pergunta** (`docs/PLANO_V2_PESQUISA.md`): em que condições a plasticidade durante a vida produz vantagem adaptativa sobre as
predisposições herdadas?

**O que dá para dizer, neste motor e com estes artefatos:**
- **A predisposição herdada responde ao mundo.** O instinto brinca mais com a bola (A1, Δp +0,310) e come conforme o incentivo e não só
  pela fome (N4, G-SEP(i) +0,094). O P0 da pergunta maior não é inerte.
- **O ensino do dono chega ao aprendiz, mas decide pouco.** Na L1, o acerto na tarefa do atencioso sobe sobre o instinto (0,663 ×
  0,577), mas o aprendido decide com fator em 18% das decisões, e a divergência fica abaixo do alvo. Isso foi com teto 1·S; o T3 ainda não
  foi validado.
- **A consequência sozinha, no mundo padrão, não melhorou o cuidado de si** (N3, G-P1 falha). O P1 mudou o comportamento (come mais,
  poupa energia), sem efeito na privação.
- **No mundo das frutas, em calibração e antes da R2**, o P1 se afastou da fruta ruim no descasado (+0,109) e se aproximou dela no casado
  (−0,062). Ou seja, foi para perto de 1/3 nos dois, não para a fruta certa. É diagnóstico, não validação. A decisão de comer passou a
  ver a fruta depois disso.
- **O dono atencioso não deixa o pet em privação** (revisão: Δ privação 0,000 em todos os pontos). Com esse dono, o G5 tende a passar
  porque o cuidado é teto, não porque o ensino se separou do cuidado.

**O que não dá para dizer:**
- nada sobre P2, P2e e P3 no mundo das frutas, nem sobre a decomposição da plasticidade por fonte (o experimento maior não rodou);
- nada sobre casado × descasado × mutável com validação;
- nada sobre "vantagem adaptativa" da plasticidade: nenhuma validação até aqui comparou o P1 ou o P3 ao P0 numa medida de desempenho no
  mundo das frutas;
- nada sobre animais ou pessoas.

---

## 5. Decisões do Matheus

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| LP-1 | refazer a A1 com B1/B2 | sim, validação só, 23101…23505, primeiro | sem ela, a bola segue registrada como mundo que falha no cuidado por um defeito que o desenho já tirou |
| LP-2 | refazer a L1 no T3 | sim, validação só, 24101…24505, antes da validação do experimento maior, com os alvos de antes | sem ela, o P3 do experimento maior roda num ponto nunca validado no mundo em que a L1 foi definida |
| LP-3 | refazer o N3 no T3 | não; deixar a faixa 25101…25505 proposta para o caso de o experimento maior pedir | refazer gasta sementes para confirmar o que a revisão já mostrou (o teto não muda o P1) |
| LP-4 | G-SSE do N4 com a medida N1 | não agora; faixa 27101…27505 proposta | o G-SSE é propriedade do mundo do N4, que o experimento maior não usa; refazer só muda o rótulo de uma falha de medida |
| LP-5 | sem calibração nova nas refeitas | sim: os pontos já estão fixados | recalibrar abre escolha de ponto olhando a validação antiga |
| LP-6 | alvos e gates das refeitas | os de antes, sem relaxar | relaxar depois de ver os dados vicia o teste |
| LP-7 | artefatos | pastas novas (`artifacts_v2_a1_b/`, `artifacts_v2_l1_t3/`); os antigos ficam como estão | sobrescrever apaga o registro do que falhou e por quê |
| LP-8 | quem roda | A1-B com o chat D (bancada); L1-T3 com o chat B (aprendiz) | com a frente errada, alguém mexe em arquivo que não é dele (`docs/V2_TRABALHO_PARALELO.md`) |

## 6. Nota posterior (2026-10-05): decisões LP substituídas

As decisões LP-1 a LP-7 acima **não serão executadas**. O Matheus decidiu, no mesmo dia, montar o cérebro inteiro, calibrar uma vez e
validar uma vez (`docs/ROADMAP_V2.md`, revisão 3, M10 e M11). As validações L1, A1, N3 e N4 ficam como histórico. As faixas propostas
aqui (23101…27505) não foram usadas e ficam livres. A leitura das seções 1 a 4 continua valendo como registro do que se sabia.
