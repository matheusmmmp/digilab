# SÍNTESE — SOCIAL_PAR S: o que o substrato permite concluir

Esta é a fase S4 do pedido SOCIAL_PAR S, em 2026-11-19. É um documento sem run e sem código: cada número abaixo vem de um artefato
versionado, com o sha256 na tabela das fontes.

## 0. As fontes

| fase | o quê | documento | artefato (sha256) |
|---|---|---|---|
| A0/B0 | a run de 210 pares no pet de hoje | `docs/RESULTADO_V3_SOCIAL_PAR_A0.md` | `artifacts_v3_social_par_a0/run/resultado.json` (`2ed5058b1405fa9a5635fb224579f3e3ec61a38470f56a490f6eae8664910891`), `medidas.json` (`5685b377a279304609f86c1219418595acd93c0866c45bbd54b9a6148a201e0c`) |
| S0 | a observação, sobre as vidas do A0 refeitas com o sha256 | `docs/OBSERVACAO_V3_SOCIAL_PAR.md` | `artifacts_v3_social_par_s/s0/observacao.json` (`676a5ba758aa1201687dafba35a7deb187cf056dd4a05336e39ae44beebc8508`), `resumo.json` (`c09b1dee47507f43aa708df1c26b241c109d566e5043b9476cda9ed619500d25`) |
| S1 | o plano e o adendo 1 | `docs/PLANO_ANALISE_V3_SOCIAL_PAR_S.md` | — |
| S2 | o substrato (C, B1, B2 e o G-DET), atrás da `ConfigIntervencaoSocial` | `docs/TAREFA_V3_SOCIAL_PAR.md`, seção S2 | os testes em `tests/test_social_par_s.py` |
| S3 | a run de 750 pares | `docs/RESULTADO_V3_SOCIAL_PAR_S.md` | `artifacts_v3_social_par_s/run/resultado.json` (`9c74ebc2c807a2262c1841ec3f6ab1ebc05669b725e368b790bcfae784ab24e7`), `medidas.json` (`5fa7767ddb3b70f147ade7df0a7922b29262a51c1a386ee7d3ab0b73769120c7`), `meta.json` (`b193f56b9557b344fc379a496b5cdbb813c853e900e1d118100bf81e7b0184dd`) |

## 1. Os bloqueios: o que a S0 achou e o que a S3 resolveu

| bloqueio | o que a S0 mostrou | o braço da S3 | resolveu? |
|---|---|---|---|
| **o parceiro não vê o focal deslocado** (o adendo 1) | a percepção social só vai até 6 células (`perceber_social`, `digilab/mundo.py:721`), e no A0 o deslocamento punha os dois de 9 a 12 células um do outro. P não tinha como responder antes do T\* | todos: o primário passa a ser o tempo até o **contato** (1 célula), com F a 5 células de P, dentro da visão | **sim:** a PA-2 deu 200/200 em todo braço (S3, premissas) |
| **o efeito-teto pela casa** | estar perto (≤ 6 células) é 64,3 % da vida, porque a casa atrai os dois. F volta por conta própria: 1051 células líquidas de F contra 34 de P. Em 193 de 201 pares, T\*_GRAV = T\*_VIVO | **B1:** os dois fora da casa, com P em Q (x de 34 a 60) | **sim:** T\*c_GRAV de 52,2 decisões (era ~10), e 43 % dos contatos fora da casa (S3, substrato) |
| **a bola morta** | os pets escolhem brincar ~12 vezes por vida, mas houve só 2 chutes em 420 vidas de pet. A bola fica a ~30 células da casa e fora da visão | **B2:** a bola na posição de P, também nas vidas base | **em parte:** os chutes subiram de ~0 para 0,5–0,6 por dia (S3, substrato), mas só 13 pares foram elegíveis, para um mínimo de 100 |
| **o instrumento vê?** | — | **G-DET:** P trocado por um seguidor de regra | **sim, nos três:** os IC95 vão de [−27,8; −12,3] a [−80,4; −58,8], todos abaixo de −4 |
| o sono de P (B3), a gravação que envelhece (B4) e a CO7 inerte (B5) | a CO7 muda 7 de 201.600 decisões | fora da S, pelo plano (seção 1) | não se aplica |

## 2. O efeito no D_A e no D_B

**O D_A, o primário do A:**

| | n | D_A (decisões) | IC95 | classe |
|---|---|---|---|---|
| A0 (T\* até 6 células) | 201 | −0,119 | [−0,300; +0,061] | ≈ 0 |
| S3, C | 200 | +0,145 | [−0,454; +0,744] | ≈ 0 |
| S3, B1 | 200 | −0,815 | [−1,775; +0,145] | ≈ 0 |
| S3, B2 | 200 | +0,490 | [−0,880; +1,860] | ≈ 0 |

- **Antes da S, o nulo do A0 não distinguia** "o pet não responde" de "o pet não tinha como responder" (o adendo 1).
- **Agora distingue.** No mesmo substrato, o seguidor de regra muda o tempo até o contato em 16 a 70 decisões, e o pet de hoje não sai de
  ±1,9.
- **Pela regra escrita antes (o conjunto da seção 7):** o social não existe no pet de hoje, mesmo num substrato que o deixa ver. O próximo
  passo é mecanismo, e não mais substrato.

**O D_B, o primário do B, segue sem leitura:**
- a PB-1 falhou no A0 (0 de 210 pares) e nos três braços da S3 (0, 0 e 13);
- o B não tem controle positivo (o plano, seção 3).

## 3. O efeito na riqueza descritiva

Estas são as medidas da S0 sobre as vidas VIVO de cada braço (`resultado.json`, `bracos.<braço>.riqueza`). São descritivas e não decidem
nada.

| a razão observada/esperada de fazer a mesma ação juntos | S0 (A0) | C | B1 | B2 |
|---|---|---|---|---|
| comer | 1,56 | 1,63 | 2,13 | 1,61 |
| brincar | 1,29 | 1,09 | 1,34 | 1,70 |
| chamar atenção | 2,02 | 1,88 | 1,46 | 1,84 |
| dormir | 1,02 | 1,01 | 1,03 | 1,02 |

| outras medidas | S0 (A0) | C | B1 | B2 |
|---|---|---|---|---|
| contatos por vida | 58,2 | 57,7 | 63,6 | 56,5 |
| chutes no total (A / B) | 1 / 1 | 0 / 0 | 54 / 47 | 505 / 604 |

- **O "juntos" acima de 1 é do mundo comum, não da resposta.** O secundário S2 (a fração do tempo perto, VIVO − GRAV) inclui 0 em todos os
  braços. Quando P é uma gravação que não responde, os dois ficam juntos do mesmo jeito.
- **O efeito de presença continua o da S0:** com o outro perto, F chama menos atenção (de −0,06 a −0,09 na fração de decisões) e come,
  dorme e explora um pouco mais. Essa diferença vem da presença física e da casa, não do parceiro que responde.
- **O B1 muda o contexto, mas não a relação:** com os dois fora da casa, o comer juntos sobe para 2,13. Esse número também cabe no mundo
  comum: há menos comida fora da casa, e os dois acham a mesma.

## 4. O que ficou sem explicação

- **Por que a bola na posição de P rende só 0,5 chute por dia:** é bem mais que antes, mas pouco. A S não mediu o que o brincar faz quando
  a bola sai da visão depois do primeiro chute. Pode ser a mesma regra do `brincar` (a bola só é alvo dentro do raio da visão), mas isso não
  foi testado.
- **O "comer juntos" do B1 (2,13):** fica para outra medida dizer se é a escassez fora da casa ou outra coisa. Nenhuma das medidas da S
  separa as duas.
- **O G-DET do C passou com folga,** e o previsto era passar por pouco ou falhar. A previsão subestimou quanto um seguidor de regra muda o
  contato com a casa perto.

## 5. O que isso muda no diagnóstico do social no DigiLab

- **Antes (A0 e S0):** o nulo podia ser do instrumento, porque P não via F deslocado, e do teto da casa.
- **Agora (S3):** o instrumento vê nos três substratos, e o pet de hoje continua igual.
  - **No código, a razão é estrutural,** e não de calibração. O modular não tem nenhuma unidade de decisão com o outro como alvo:
    - o motor já oferece os candidatos `seguir` e `onde_comeu` no explorar (`digilab/mundo.py`, `_candidatos_sociais`);
    - mas o `impulso.alvos` (`digilab/digibrain/impulso.py`) só gera unidades de comida, cheiro, bola, vagar e lugar lembrado.
  - **O corpo também não sente o outro:** nenhum receptor muda com a companhia.
- **É o que a investigação já tinha mapeado:** a seção 5 do `docs/INVESTIGACAO_V3_SOCIAL_PAR.md` diz que o caminho quebra em dois pontos,
  na intenção (o M1) e na consequência no corpo (o M2).
- **O que a S acrescenta:** a prova de que não é o substrato que esconde uma resposta.

## 6. O que a S não demonstra

- **Que o pet ignora o outro:** a S mostrou só que o parceiro que responde não muda o tempo até o contato acima de 4 decisões. A presença
  física muda as ações (a seção 3).
- **Nada sobre o B (a bola):** a premissa falhou em todas as fases.
- **Nada com sentidos mais longos:** o olfato e a audição (`ConfigSentidos`) seguem desligados.
- **Nada sobre o pet crescido nem sobre o jogo web:** as vidas são as da bancada, com o modular de hoje, no Python.
- **Nada sobre a CO7:** ficou fora pelo plano.
- **Que o M1 vai fazer o social aparecer.** A espec dele (`docs/ESPEC_SOCIAL_PAR_M1.md`) prevê o contrário para o `seguir` sem o M2.
- **Nenhuma novidade:** o protocolo de parceiro gravado e o de interação mínima estão publicados (`docs/INVESTIGACAO_V3_SOCIAL_PAR.md`,
  seção 10).
