# OBSERVAÇÃO V3 — SOCIAL_PAR S0: o que os dois pets fazem juntos hoje

- **Fase:** S0 do pedido do Matheus de 2026-11-18 (a socialização pet-pet). É um documento descritivo: sem vida nova, sem teste e sem
  mudança no código do jogo ou da bancada.
- **Snapshot:** a `main` em 8c6d17ae (2026-11-18), mais o branch da run do A0 (`v3-social-par-a0-run`, PR #998, ainda aberto). O pedido
  cita o A0 como #973, mas a run está no #998. Os artefatos da run só existem nesse branch, e por isso este PR fica em cima dele.
- **De onde vem cada número:** `artifacts_v3_social_par_s/s0/resumo.json` (sha256 `c09b1dee…0d25`). Ele é feito por
  `python experiments/resumir_v3_social_par_s0.py` a partir de dois arquivos:
  - o `observacao.json` (sha256 `676a5ba7…8508`), feito por `python experiments/observar_v3_social_par_s0.py --processos 1`, no commit
    2044e420, em 275 s;
  - o `medidas.json` da run do A0.
- **Como se observa sem vida nova:** a run do A0 não guardou as vidas inteiras. Ela guardou, por par, a semente, a perturbação, as
  gravações de P e o sha256 do registro e das posições (é o event sourcing). O script refaz a vida VIVO de cada um dos 210 pares com o
  código da run e confere o sha256 contra o `.json.gz` do par; se um par não bate, ele para. **Os 210 bateram.** As vidas lidas aqui são,
  portanto, as da run, bit a bit (D-SP-37).
- **Os nomes:** F é o pet A, o focal, o que a perturbação leva para longe. P é o pet B, o parceiro. "Perto" é a distância de Chebyshev
  ≤ 6 células, o raio perto do A0, medida no começo de cada decisão. O mapa tem 64 × 30 células. O ninho fica em (4, 15) e o comedouro
  em (10, 15), os dois na casa, a 6 células um do outro; a bola começa em (40, 15), no campo.
- **As médias:** são sobre os 210 pares, com o IC95 pela t só como tamanho do que se vê. Nada aqui é teste, e nada se decide com um IC.

## 1. Perto é o estado normal, não um evento

- **Nos 210 pares, F e P passam 64,3 % das decisões a até 6 células um do outro** (IC95 63,6–65,1 %), e 12,1 % em contato, a até 1
  célula. A distância fica até 10 células em 86,8 % das decisões e até 12 em 92,4 % (`resumo.json`, `distancia`).
- O que puxa os dois para o mesmo lugar é a casa: o ninho e o comedouro ficam a 6 células um do outro, e o dono "atencioso" põe a comida
  no comedouro.
- **Daí o efeito-teto do A0:** depois do deslocamento de 12 células, F volta ao raio perto em ~10 decisões em qualquer condição, porque a
  vida de todo dia já o traz de volta para a casa.

## 2. O que F faz com P perto, e o que P faz com F perto

Fração de cada ação com o outro perto, menos a fração com o outro longe, par a par (`resumo.json`, `presenca`; os 210 pares têm ao menos 20
decisões de cada lado):

| ação | F perto | F longe | F: perto − longe [IC95] | P perto | P longe | P: perto − longe [IC95] |
|---|---|---|---|---|---|---|
| dormir | 0,465 | 0,435 | +0,030 [0,024; 0,036] | 0,468 | 0,440 | +0,029 [0,023; 0,035] |
| explorar | 0,342 | 0,324 | +0,018 [0,012; 0,024] | 0,346 | 0,331 | +0,015 [0,008; 0,021] |
| chamar atenção | 0,079 | 0,171 | **−0,091** [−0,097; −0,086] | 0,073 | 0,158 | **−0,086** [−0,091; −0,080] |
| comer | 0,066 | 0,036 | +0,031 [0,028; 0,034] | 0,066 | 0,035 | +0,030 [0,027; 0,033] |
| brincar | 0,028 | 0,019 | +0,009 [0,006; 0,011] | 0,028 | 0,019 | +0,009 [0,007; 0,011] |
| ocioso | 0,016 | 0,013 | +0,003 [0,000; 0,005] | 0,016 | 0,013 | +0,003 [0,001; 0,005] |

- **Há um efeito de presença, e ele é o mesmo nos dois pets:**
  - com o outro perto, cada um chama menos a atenção do dono, em 9 pontos (205 dos 210 pares em F, 207 em P);
  - e come um pouco mais, em 3 pontos (193 pares em F, 194 em P).
- **Ele não prova que o pet vê o outro.** Perto quer dizer, quase sempre, "na casa", onde ficam a comida e o ninho. Longe quer dizer
  fora dela, onde não há comida e o dono está mais longe. Os artefatos não separam a presença do outro do lugar (seção 8).

## 3. O que os dois fazem juntos

Nos 64.550 passos com os dois perto, a dupla "a mesma ação" observada, contra a esperada se cada um agisse sem olhar o outro dentro do
par (o produto das frações dos dois nos mesmos passos; `resumo.json`, `juntos`):

| os dois fazem | observado | esperado | razão |
|---|---|---|---|
| dormem | 14.394 | 14.078 | 1,02 |
| exploram | 8.004 | 7.651 | 1,05 |
| comem | 434 | 278 | 1,56 |
| chamam a atenção | 790 | 391 | 2,02 |
| brincam | 65 | 50 | 1,29 |
| ficam ociosos | 159 | 17 | 9,6 |

- **Dormir e explorar juntos é o acaso:** 1,02 e 1,05. Os dois dormem 45 % da vida cada um (F 0,453, P 0,458), e dormir perto é o que se
  espera de dois pets com o mesmo ninho e o mesmo relógio.
- **Comer juntos passa do acaso (1,56).** A causa mais simples é comum: o dono serve os dois de uma vez no mesmo comedouro. Comer em
  contato acontece 1,8 vez por vida.
- **Chamar a atenção juntos é 2 vezes o acaso,** e ficar ocioso juntos, 9,6 vezes. Esses números são poucos, e a causa provável é
  também comum: o dono, as horas sem comida. Os artefatos não dizem qual é.
- **Brincar juntos:** 65 vezes em 210 vidas. Cada pet escolhe brincar ~12 vezes por vida, mas **a bola foi chutada 2 vezes nas 420
  vidas de pet,** uma por F e uma por P (`mundo.chutes_total`). O pet quer brincar e não chega à bola: ela está no campo, a ~30 células
  do comedouro.

## 4. O que acontece depois de uma aproximação

Uma aproximação é uma decisão em que um pet encurta a distância com o próprio passo, fora do contato. O que o outro faz na decisão
seguinte, contra o que ele faz em toda a vida (`resumo.json`, `depois_da_aproximacao`):

| | n | dorme | explora | chama a atenção | come |
|---|---|---|---|---|---|
| P depois de F se aproximar | 16.320 | 0,452 (vida 0,458) | 0,354 (0,340) | 0,081 (0,104) | 0,068 (0,055) |
| F depois de P se aproximar | 16.158 | 0,450 (vida 0,453) | 0,352 (0,336) | 0,090 (0,112) | 0,064 (0,055) |

- **O outro faz o que faria de qualquer jeito.** A diferença é a mesma do efeito de presença da seção 2: 2 pontos a menos de chamar a
  atenção e 1 a mais de comer. Nada aparece que não estivesse já na presença.

**Quem fecha a distância depois do deslocamento** (as 2.031 decisões da janela antes de os dois voltarem ao raio perto;
`resumo.json`, `fecha_a_distancia`):
- **F encurta** em 21,9 % das decisões e alonga em 5,0 %;
- **P encurta** em 15,7 % e alonga em 15,4 %;
- **o ganho líquido é de 1.051 células de F e 34 de P.**

**É F quem volta; P só anda.** Isso explica o D_A ≈ 0. Em **193 dos 201 pares elegíveis, o T\* da GRAV é exatamente o da VIVO**
(`gravacao.d_a_zero`): F volta no mesmo passo com P vivo ou gravado, porque a volta não depende do que P faz.

## 5. O que a CO7 faz na prática

A CO7 registra o dever em todas as decisões dos dois pets: 100.800 de 100.800 em cada um (`resumo.json`, `co7`). **O pedido diz "96
decisões com dever" e "age em 0,5 %",** mas os números do A0 dizem outra coisa:
- **"96 com dever"** é a janela inteira: o dever é registrado em toda decisão.
- **O 0,5 % (0,004975)** é a média por par de decisões em que o escudo removeu algo na janela. É 1 decisão em 201 pares.

Na vida inteira dos 210 pares:

| | F | P |
|---|---|---|
| o escudo ligado | 25.241 (25 %) | 26.565 (26 %) |
| culpa > 0 | 2.703 (2,7 %) | 2.970 (2,9 %) |
| inveja > 0 | 2.393 (2,4 %) | 2.362 (2,3 %) |
| uma comida proibida | 20 | 17 |
| um candidato removido | 4 | 3 |
| um candidato reprovado | 4 | 3 |

- **A CO7 muda uma escolha em 7 de 201.600 decisões.** A culpa e a inveja sobem em ~5 % das decisões, mas quase nunca há o que tirar.
- **Os exemplos** (`co7.A.exemplos`, `co7.B.exemplos`):
  - **par 101303-0008, tick 3000:** F tinha "comer a comida 16" como candidato. O escudo o removeu, com culpa 128 e delta 128, e F
    dormiu;
  - **par 101303-0019, tick 6105:** F tinha oito comidas reprovadas (58 a 66), com culpa 0 e delta 0, e dormiu;
  - **par 101101-0019, tick 7065:** P tinha cinco comidas removidas (57, 66, 67, 68 e 72), com culpa 128, e dormiu;
  - **par 101101-0000, ticks 7050 e 7155:** P tinha a comida 48 proibida, com culpa 128. Ele chamou a atenção e depois explorou.
- **Em todos os exemplos, o que o escudo tira é uma comida,** e o pet faz outra coisa. A CO7 é um filtro sobre comer a comida que o
  outro quer, e quase nunca há essa comida.

## 6. O mundo comum: a comida

- **Disputar a comida é raro:** 20 disputas em 210 vidas, em 19 pares (`mundo.disputas`). Os 8 exemplos guardados são todos de ração madura, e em 4
  deles o vencedor estava em cima da comida (d_vencedor = 0).
- **Exemplos:** par 101101-0028, tick 6210 (A ganhou a ração 52); par 101101-0031, tick 3165 (B ganhou a ração 21); par 101202-0037,
  tick 7020 (B ganhou a ração 73, sem contato).
- **Cada pet come ~23 vezes por vida** (F 22,9, P 22,7) e **vê o outro comer ~17 vezes** (F 17,2, P 17,8).
- **Os contatos são esbarrões:** são 58 por vida. Dos 12.217 contatos, 12.202 são "esbarrou | esbarrou" e 15 vêm de uma disputa
  (`mundo.contatos`).
- **Há comida para os dois:** um não come a comida que o outro ia buscar, salvo nessas 20 vezes. No A0, 176 dos 201 pares tinham comida
  no mapa no t0.

## 7. A gravação envelhece pouco onde importa

- Na janela da GRAV, P gravado tem o alvo fora do mundo em 0 decisões em 45 pares, em 1 a 2 decisões em 103 pares e em 3 ou mais em 53
  (`gravacao.desvios_P_janela_hist`).
- Os desvios mudam a janela inteira (a fração perto, a contingência) em quase todos os pares: só em 28 de 201 a janela da GRAV é idêntica
  à da VIVO. **Mas eles quase nunca mudam o T\*** (193 de 201), porque o T\* é feito pela volta de F (seção 4).

## 8. O que os artefatos não deixam ver (as lacunas)

- **Presença ou lugar:** a vida não separa "o outro está perto" de "estou na casa". Separar pede uma vida em que os dois se encontrem
  fora da casa, que é uma mudança de substrato (a S1).
- **Para onde F volta:** F fecha a distância (seção 4), mas o script não mediu se ele vai até P ou só até a casa. Dá para medir nas
  mesmas vidas, sem vida nova, com outra passada do script.
- **Por que brincar não chega à bola:** os artefatos dizem que o pet escolhe brincar ~12 vezes por vida e quase nunca chuta. Não dizem se
  o alvo do brincar é a bola longe ou outra coisa.
- **Por que chamar a atenção e ficar ocioso juntos passam do acaso:** a contagem não diz se a causa é o dono, a hora ou o outro pet.
- **O dono é um só e é sintético** (o "atencioso" no comedouro). Os outros donos e lugares não foram observados.
- **O meta.json da observação diz `git_limpo: false`:** o script do resumo ainda não estava commitado quando a observação rodou. O script
  da observação estava (2044e420).

## 9. O que a observação ranqueia para a S1 (proposta, decide o Matheus)

| bloqueio | o que a S0 mostra | a força |
|---|---|---|
| **B1, efeito-teto** | perto é 64 % da vida; F volta sozinho, e P não muda o T\* em 193 de 201 pares | **a mais forte:** é o que faz o D_A ≈ 0 por construção |
| **B2, bola morta** | o pet escolhe brincar ~12 vezes por vida e chuta 2 vezes em 420 vidas de pet; a bola está a ~30 células da casa | **forte:** sem chute, não há B0 |
| **B3, sono** | os dois dormem 45 % da vida, e dormir junto é o acaso (1,02) | **média:** o sono reduz as decisões em que algo pode acontecer, mas é dos dois, não de P |
| **B4, gravação** | os desvios mudam a janela, mas não o T\* | **fraca para o A0:** só importa depois do B1 |
| **B5, CO7** | muda 7 decisões em 201.600 | fora de escopo, como diz o pedido |

**A recomendação:** atacar primeiro o B1 e o B2. O B1 é o que impede o A0 de ver qualquer coisa; o B2 é o que impede o B0 de existir. O B1
precisa de um encontro fora da casa, e não só de um d0 maior: com a casa como ímã, um d0 de 18 ou 24 células ainda é desfeito pela
volta para casa. O custo de errar a ordem é baixo, porque é uma rodada de plano.
