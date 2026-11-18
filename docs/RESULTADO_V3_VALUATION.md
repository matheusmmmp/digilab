# RESULTADO V3 — VALUATION: a ablação do Valuation (2026-11-17, Claude Code, Opus 5.5)

**O plano:** [PLANO_ANALISE_V3_VALUATION.md](PLANO_ANALISE_V3_VALUATION.md), APROVADO pelo Matheus em 2026-11-16 ("Aprovado, siga a V2"),
com o adendo 1 APROVADO no mesmo dia ("Aprovo o adendo 1": o braço A fora, D-VAL-11), commitado antes da primeira vida. A tarefa:
[TAREFA_V3_VALUATION.md](TAREFA_V3_VALUATION.md).

**A leitura, pela regra da seção 7: uma hipótese confirmada, a R (o reflexo do sono).** B, C, E, F e G saem refutadas. Pelo CHECKPOINT
V2.5, a R vai à V3 como candidata, **marcada como "piora o bem-estar"** (seção 5.2): desligar o reflexo fecha mais episódios de fome e
deixa o pet exausto em metade das decisões da segunda semana. Qual conserto entra é decisão do Matheus.

## 1. A run

| comando (o do `meta.json`) | commit, árvore | vidas | sementes | duração |
|---|---|---|---|---|
| `python experiments/run_v3_valuation.py --config experiments/configs/v3_valuation/ablacao.json --processos 4` | `cc88e182`, limpa | 5 600 (7 braços × 4 células do `longe_fixo` × 200 unidades) | 99101…99505, K = 40, derivação `digibrain_prototipo` | 1 h 35 (09:27–11:02 de 2026-11-17) |

- **O ambiente:** Python 3.13.0 e Node v24.19.0, este só gravado, porque a run não o usa. A run saiu com o código 0, sem falha alta (o replay, as conferências da C4 e as da seção 3 do plano). Ela rodou **uma vez**.
- **A base do código:** a run rodou sobre o branch do #943 (EVIDENCIA A1), com a `main` de 2026-11-17 dentro (`586b1107`). O Matheus pediu "roda já sobre o branch do #943", em vez de esperar o merge (D-VAL-14).
- **A máquina:** nenhuma outra run do DigiLab rodava. A CPU estava ocupada por um processo de outro projeto, o que pode ter alongado a duração. Os números não mudam, porque a run é determinística.

**Os artefatos** em `artifacts_v3_valuation/ablacao/`, com o sha256 no disco igual ao do `meta.json`. Todo número abaixo sai deles.

| arquivo | sha256 | tamanho e observação |
|---|---|---|
| `resultado.json` | `f087804c…` | |
| `medidas.json` | `71fe146c…` | 53,4 MB, sem `.gz`, porque fica abaixo de 100 MB |
| `vidas.tar.gz` | `da4c41d7…` | 25,6 MB, determinístico |
| `meta.json` | | |

## 2. O primário (seção 5.1)

O primário é a taxa de fechamento por episódio de fome, medida em cada braço como braço − REL na mesma unidade. Os detalhes do teste:
- n = 200 unidades, média das 4 células do `longe_fixo`;
- IC95 pelo t pareado;
- Holm sobre os 6 p unilaterais, com α = 0,025;
- δ = 0,032.

O nível do REL é **0,586**.

| hipótese (braço) | nível | braço − REL | IC95 | classe | p unilateral | Holm | margem efetiva | fração do gap da A1 | **leitura** |
|---|---|---|---|---|---|---|---|---|---|
| **R** (`lambda_sono = 0`, o reflexo do sono desligado) | 0,715 | **+0,129** | [+0,117; +0,141] | > 0 | 3,9 × 10⁻⁵¹ | rejeita | 0,018 | 1,55 | **confirmada** |
| B (ε = 0) | 0,593 | +0,008 | [−0,005; +0,020] | ≈ 0 | 0,118 | não | 0,018 | 0,09 | refutada |
| E (viés do comer −S/2) | 0,588 | +0,003 | [−0,009; +0,014] | ≈ 0 | 0,325 | não | 0,017 | 0,03 | refutada |
| F (V e E zerados no z) | 0,574 | −0,012 | [−0,021; −0,003] | ≈ 0 (sinal −) | 0,995 | não | 0,013 | −0,14 | refutada |
| C (`controle_mem = "sem"`) | 0,528 | −0,058 | [−0,070; −0,046] | < 0 | 1,0 | não | 0,017 | −0,70 | refutada |
| G (`maior_peso`, sem sorteio) | 0,296 | −0,290 | [−0,325; −0,254] | < 0 | 1,0 | não | 0,051 | −3,49 | refutada |

- **A margem efetiva** fica abaixo de δ em todos os braços, menos na G (0,051). Como a G sai "< 0", e não "≈ 0", nenhuma leitura de "≈ 0" fica enfraquecida.
- **A fração do gap da A1** é descritiva: o contraste dividido por 0,083, o módulo do REL − TRIV da A1.
- **O bootstrap** (IC95 percentil, anticonservador com 5 bases e rotulado) concorda com o t na classe dos 6 braços.

## 3. A guarda do bem-estar (seção 5.2, sem gate na V2)

| braço | privação, braço − REL [IC95] | classe | exaustão, braço − REL [IC95] | classe | piora o bem-estar |
|---|---|---|---|---|---|
| **R** | **+0,084** [+0,073; +0,095] | > 0 | **+0,276** [+0,264; +0,288] | > 0 | **sim** |
| B | −0,000 [−0,014; +0,013] | ≈ 0 | +0,002 [−0,004; +0,007] | ≈ 0 | não |
| E | +0,037 [+0,025; +0,049] | > 0 | +0,030 [+0,025; +0,035] | > 0 | sim |
| F | +0,007 [−0,000; +0,013] | ≈ 0 | +0,001 [−0,002; +0,005] | ≈ 0 | não |
| C | +0,056 [+0,045; +0,068] | > 0 | −0,000 [−0,005; +0,004] | ≈ 0 | sim |
| G | +0,388 [+0,354; +0,422] | > 0 | +0,159 [+0,146; +0,172] | > 0 | sim |

- **Os níveis do REL:** privação 0,337 e exaustão 0,220.
- **Os níveis da R:** privação 0,421 e exaustão 0,496. Sem o reflexo, o pet passa metade das decisões dos dias 8–14 com energia abaixo de 0,25.

## 4. Os descritivos (seção 5.3, sem gate)

Nível de cada braço. A diferença braço − REL, com o IC95, está no `resultado.json`.

| medida | REL | R | B | E | F | C | G |
|---|---|---|---|---|---|---|---|
| episódios que acabam em `janela_vencida` | 0,410 | **0,282** | 0,402 | 0,407 | 0,422 | 0,468 | 0,702 |
| fração das decisões do episódio em `dormir` | 0,420 | **0,265** | 0,422 | 0,430 | 0,419 | 0,418 | 0,217 |
| fração das decisões do episódio em `comer` | 0,170 | **0,242** | 0,171 | 0,196 | 0,168 | 0,185 | 0,069 |
| refeições de ração por dia | 3,09 | 3,19 | 3,06 | **4,54** | 3,02 | 2,78 | 1,09 |
| episódios de fome por vida | 13,5 | 15,6 | 13,6 | 12,9 | 13,4 | 13,3 | 9,1 |
| latência média do fechamento (ticks) | 49,6 | 44,5 | 49,4 | 53,0 | 49,4 | 58,4 | 41,0 |
| reflexos por vida | 257 | 0 | 257 | 285 | 258 | 244 | 468 |
| intenções de comer trocadas num reflexo, por vida | 13,1 | 0 | 13,2 | 15,7 | 13,1 | 13,3 | 9,5 |
| decisões do episódio com o comer no topo e outra sorteada | 0,097 | 0,112 | 0,095 | 0,173 | 0,094 | 0,112 | — |

As sondas "quem decidiu" (`influencia`) estão no `resultado.json`, sem leitura aqui.

## 5. O que isso diz

- **R:** o reflexo do sono explica a perda, e com folga. Desligado, o REL fecha 0,129 a mais, mais que o gap inteiro da A1, que era de 0,083. O mecanismo aparece nos descritivos:
  - a fração de `dormir` no episódio cai de 0,42 para 0,26;
  - a de `comer` sobe de 0,17 para 0,24;
  - a `janela_vencida` cai de 41 % para 28 %;
  - o reflexo do REL troca 13 intenções de comer por vida.

  Ele faz isso à custa da energia: a exaustão vai de 0,22 a 0,50. Pela seção 5.2, o conserto da V3 tem de fechar mais sem essa piora.
- **Uma comparação entre runs, só descritiva:** na A1, com outras sementes (97xxx), o REL do `longe_fixo` fechava 0,562 e a TRIV 0,645, com exaustão 1,000. A R fecha 0,715 com exaustão 0,496. Não é um contraste do plano: são runs diferentes, e nada aqui foi testado contra a TRIV. Esse teste é a V4.
- **E:** o pet come mais, 4,54 rações por dia contra 3,09, mas a taxa por episódio não muda (+0,003), e o bem-estar piora. Comer mais cedo não fecha a janela. O nulo vale só para o valor testado (viés −512).
- **B e F:** a exploração (ε) e o V e E no z não pesam na perda.
- **C:** a memória de lugar ajuda (−0,058 sem ela), o que concorda com a C4 (REL − SEM = +0,065) em outras sementes. Não é a causa.
- **G:** o sorteio proporcional não é a causa. Tirá-lo é muito pior (−0,290): sem sorteio, 84 % das ações somadas do braço são `dormir` (47 %) ou `chamar_atencao` (37 %), e o `comer` cai a 2 % (as ações somadas estão no `resultado.json`).
- **O que a run não demonstra** (o `nao_demonstra` do `resultado.json`):
  - as interações entre as ablações, porque cada braço muda uma coisa só;
  - um nulo fora do valor testado (E e R);
  - nada fora das 4 células do `longe_fixo`, do mundo do MVP e dos 14 dias;
  - nada sobre o jogo web;
  - que uma ablação confirmada já seja o conserto, que é a V3;
  - a hipótese D, que vai à A2;
  - a hipótese A, fora da run pelo adendo 1.

## 6. O CHECKPOINT V2.5

Uma confirmada, a R, que vai à V3 como candidata e marcada como "piora o bem-estar". A V3 não começa sem o Matheus decidir qual conserto
entra (seção 7 do plano). Esta frente para aqui.
