# RESULTADO V3 — PET_VIVO, PV-2: a quimiotaxia e o ganho da fome (2026-11-18)

Worker: Claude Code, Opus 5.5, worktree `v3-pet-vivo-pv2-run`. Plano: [PLANO_ANALISE_V3_PET_VIVO_PV2.md](PLANO_ANALISE_V3_PET_VIVO_PV2.md)
(adendo 1 APROVADO em 2026-11-17, adendo 2 APROVADO em 2026-11-18). Código: `main` em `34894b50` (#981 e #984), `git_limpo` verdadeiro.
O `pre_run` respondeu "pode rodar", e o coordenador deu a vez da máquina. A run rodou uma vez:
`python experiments/run_v3_pet_vivo_pv2.py --config experiments/configs/v3_pet_vivo/pv2.json --processos 4`, de 11:30 a 15:45, 4 h 15 min.

Os artefatos ficam em `artifacts_v3_pet_vivo/pv2/run/`: `meta.json` (os sha256 do código, do plano, da config e dos artefatos),
`resultado.json` (os gates, a leitura e os descritivos) e `medidas.json.gz` (as medidas por vida). O `medidas.json` cru (180 MB) e o
`vidas.tar.gz` (os logs, 72 MB) ficam só na máquina, com o sha256 no `meta.json`. As vidas são regeneráveis da config e do código. Todo
número abaixo sai do `resultado.json`.

## 1. A resposta curta

**A leitura da seção 7: "custa perto de casa", e a sugestão escrita antes é não levar, qualquer que seja o resto.** No `comedouro`, a
taxa por episódio do OLF-DCV fica **−0,142 [−0,164; −0,119]** abaixo da do OLF-0 (n 200), contra uma margem de −0,018.

Os outros gates também não passam:
- **Longe, a quimiotaxia também perde da tropotaxia:** OLF-DCV − OLF-0 é negativo nos dois lugares, com o IC inteiro abaixo de zero.
- **A hora certa não ajuda:** o placebo, que vira em hora sorteada, fica igual ao OLF-DCV.
- **O OLF-G não deixa a escolha mais sensível ao estado:** a SE-C fica igual à do OLF-DCV nos 3 lugares. A leitura dele é "o ganho não
  entra".

O HOJE (com o oráculo) fica acima de todos os braços com o órgão, nos 3 lugares (o H-CUSTO).

## 2. As vidas

- **15 360 vidas:** 6 braços × 12 células × 200 unidades (14 400), mais 960 da checagem do v38 (A2.3).
- **O contrafactual da SE-C** em 1 440 delas: o OLF-0, o OLF-DCV e o OLF-G, nos k de 0 a 7.
- **As conferências que falham alto passaram em todas:** o G1 do replay (sem o leitor), o T-CENARIO-1, a `ConfigPV2` do braço e o
  número de vidas (`esperadas`).
- **O G-UNIDADES** é a conferência dos testes (`tests/test_pv2_codigo.py`), antes da run, e passou no #981.

## 3. Os gates

Os contrastes são pareados por unidade (base, semente), com a média dos 4 donos e o IC95 pelo t.

| gate | contraste | lugar | média [IC95] | n | precisa | passa |
|---|---|---|---|---|---|---|
| **G-PV2-LONGE** | OLF-DCV − OLF-0, taxa por episódio | `longe` | −0,021 [−0,035; −0,007] | 200 | limite de baixo > 0 | não |
| | | `longe_fixo` | −0,041 [−0,057; −0,024] | 200 | limite de baixo > 0 | não |
| **G-PV2-HORA** | OLF-DCV − OLF-PLA, taxa por episódio | `longe` | +0,009 [−0,003; +0,021] | 200 | limite de baixo > 0 | não |
| | | `longe_fixo` | +0,007 [−0,007; +0,021] | 200 | limite de baixo > 0 | não |
| **G-FORR** | OLF-DCV − OLF-0, taxa por episódio | `comedouro` | **−0,142 [−0,164; −0,119]** | 200 | limite de baixo ≥ −0,018 | **não** |
| | OLF-G − OLF-DCV, taxa por episódio | `comedouro` | +0,000 [−0,018; +0,018] | 200 | limite de baixo ≥ −0,018 | sim (−0,0175) |
| **G-ESTADO** | OLF-G − OLF-DCV, SE-C | `comedouro` | −0,0015 [−0,0055; +0,0024] | 40 | limite de baixo > 0,0029 | não |
| | | `longe` | +0,0009 [−0,0011; +0,0029] | 40 | limite de baixo > 0,0042 | não |
| | | `longe_fixo` | −0,0003 [−0,0017; +0,0011] | 40 | limite de baixo > 0,0085 | não |
| **G-ESTADO-NI** | OLF-DCV − OLF-0, SE-C | `comedouro` | −0,0262 [−0,0332; −0,0192] | 40 | limite de baixo > −0,0029 | não |
| | | `longe` | −0,0026 [−0,0054; +0,0002] | 40 | limite de baixo > −0,0042 | não |
| | | `longe_fixo` | −0,0051 [−0,0085; −0,0017] | 40 | limite de baixo > −0,0085 | não (−0,00855) |

O G-FORR pede os dois contrastes. O do OLF-G, sozinho, fica dentro da margem por pouco. O G-ESTADO-NI no `longe_fixo` falha por
0,00005, mas no `comedouro` falha com folga: lá, a quimiotaxia tira o corpo da escolha.

## 4. Os descritivos

**A taxa por episódio, por braço** (a média das 200 unidades):

| lugar | HOJE | OLF-0 | OLF-DC | OLF-DCV | OLF-PLA | OLF-G |
|---|---|---|---|---|---|---|
| `comedouro` | 0,883 | 0,719 | 0,557 | 0,577 | 0,581 | 0,577 |
| `longe` | 0,430 | 0,379 | 0,358 | 0,358 | 0,349 | 0,356 |
| `longe_fixo` | 0,596 | 0,353 | 0,312 | 0,312 | 0,305 | 0,307 |

**O H-CUSTO (HOJE − braço, taxa por episódio):**
- **OLF-0:** `comedouro` +0,164 [+0,152; +0,177]; `longe` +0,051 [+0,038; +0,064]; `longe_fixo` +0,243 [+0,223; +0,263].
- **OLF-DCV:** `comedouro` +0,306 [+0,283; +0,329]; `longe` +0,073 [+0,059; +0,087]; `longe_fixo` +0,284 [+0,263; +0,305].

**O H-VARR (OLF-DCV − OLF-DC):** `longe` +0,000 [−0,005; +0,006]; `longe_fixo` −0,000 [−0,006; +0,005]. A varredura não soma nada. O
adendo 1 (A1.3) já previa isso: só 11 de 592 decisões do executor foram de varredura.

**As viradas** (do `medidas_pv2`; a taxa é a fração das decisões do executor da busca pelo cheiro que viram):

| medida | lugar | OLF-0 | OLF-DC | OLF-DCV | OLF-PLA | OLF-G |
|---|---|---|---|---|---|---|
| a taxa de viradas | `comedouro` | 0,74 | 0,24 | 0,25 | 0,10 | 0,25 |
| | `longe` | 0,73 | 0,28 | 0,29 | 0,10 | 0,29 |
| | `longe_fixo` | 0,82 | 0,26 | 0,27 | 0,09 | 0,27 |
| a hora da virada (fração com o cheiro em queda) | `comedouro` | 0,41 | 1,00 | 0,93 | 0,49 | 0,93 |
| | `longe` | 0,37 | 1,00 | 0,94 | 0,35 | 0,93 |
| | `longe_fixo` | 0,43 | 1,00 | 0,96 | 0,45 | 0,95 |
| as decisões até comer | `comedouro` | 38,1 | 115,0 | 103,5 | 103,7 | 106,2 |

No OLF-DC, a hora da virada é 1,00 por construção: ele só vira na pirueta. O HOJE, no `comedouro`, come em 6,2 decisões.

**A SE-C e a RV** (a média das 40 unidades do contrafactual):

| lugar | SE-C OLF-0 | SE-C OLF-DCV | SE-C OLF-G | RV OLF-0 | RV OLF-DCV | RV OLF-G |
|---|---|---|---|---|---|---|
| `comedouro` | 0,089 | 0,063 | 0,061 | 0,373 | 0,352 | 0,351 |
| `longe` | 0,073 | 0,070 | 0,071 | 0,253 | 0,244 | 0,240 |
| `longe_fixo` | 0,063 | 0,058 | 0,058 | 0,306 | 0,306 | 0,296 |

**A checagem do v38** (A2.3, descritiva, sem o olhar; k de 0 a 7, n 40):
- **HOJE − OLF-DCV:** `longe` +0,058 [+0,027; +0,088]; `longe_fixo` +0,234 [+0,200; +0,268].
- **OLF-DCV − OLF-0:** `longe` +0,012 [−0,017; +0,040]; `longe_fixo` −0,021 [−0,055; +0,014].
- **As taxas por episódio:** `longe` HOJE 0,383, OLF-0 0,314, OLF-DCV 0,325; `longe_fixo` 0,525, 0,311, 0,291.

Com o v38 ligado, o OLF-DCV não se separa do OLF-0 longe (o IC cruza o zero nos dois lugares), e o HOJE continua acima. O `comedouro` não
entra nesta checagem.

## 5. A leitura

1. **A regra de leitura dá "custa perto de casa"**, e ela vale qualquer que seja o resto. O OLF-DCV, com o OLF-DC, o OLF-PLA e o
   OLF-G, perde cerca de 0,14 da taxa por episódio no `comedouro` contra o OLF-0. Os quatro ficam juntos (0,557 a 0,581).
2. **O que os quatro braços com a pirueta têm em comum é virar menos.** O OLF-0 vira para a narina mais forte sempre que elas diferem
   (A1.2), em cerca de 3/4 das decisões do executor da busca. Os braços com a pirueta seguem em frente e viram só quando a queda acumulada passa de
   L, em cerca de 1/4 delas. No `comedouro`, eles levam perto de 3 vezes mais decisões até comer. Isto é uma leitura das medidas, não um
   teste: o plano não tem um braço que separe "virar menos" de "virar na queda".
3. **A hora certa não explica nada.** O OLF-PLA vira menos ainda (0,10), em hora sorteada, e fica com a mesma taxa por episódio do
   OLF-DCV, nos 3 lugares. Virar na queda do cheiro (0,93 das viradas do OLF-DCV) não ganha de virar em hora qualquer.
4. **O ganho da fome não entra.** A SE-C do OLF-G fica igual à do OLF-DCV, e a forma dele no `comedouro` também. O G0 = 512 do adendo 1
   não muda isso. Outro G0 está fora desta run (o "não demonstra" do `resultado.json`).
5. **Tirar o oráculo custa caro, mesmo na tropotaxia.** O OLF-0 fica 0,16 abaixo do HOJE no `comedouro` e 0,24 no `longe_fixo`. A
   seção 7 diz que o OLF-0 fica como a forma sem oráculo "se o H-CUSTO for pequeno", e ele não é pequeno. Trocar o oráculo no jogo é
   decisão do Matheus, à parte.

## 6. O que não muda

Nada vai para a web: a regra de leitura manda não levar. A chave do PV-2 continua desligada por padrão, e o jogo não muda.

## 7. O que esta run não demonstra

- Nada sobre o jogo web (a checagem do v38 é só descritiva, e sem o olhar).
- Nada fora dos 14 dias, do mundo do MVP e dos lugares da C4.
- Nada sobre o freio da saciedade (a lacuna 3).
- Nada sobre outro L da pirueta, outro `w0_dc` ou outro G0 além dos do adendo 1.
- Nada sobre uma pirueta somada à tropotaxia, em vez de no lugar dela: o A1.2 a desenhou no lugar, e esse é o braço que perdeu.
