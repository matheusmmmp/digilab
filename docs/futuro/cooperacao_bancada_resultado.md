# A bancada da cooperação: o resultado (2026-11-12, CB4, Claude Code, Opus 5.5)

**De onde vem:** o plano `docs/PLANO_ANALISE_V3_COOPERACAO.md` (APROVADO em 2026-11-12, CB-1 a CB-9), o piloto (D-CB-11, N = 160 pela
regra, D-CB-12) e o registro da análise (D-CB-13, `7922f963`), gravado antes da primeira vida. As 1 280 vidas (sementes 91201 a 91360, oito
braços, 8 dias, o modular nos dois pets, o dono atencioso, o comedouro comum) rodaram em 627 s com 4 processos. O resultado está em
`artifacts_v3_cooperacao_bancada/resultado.json`, e o manifesto, com o sha256 das vidas, ao lado. **Nenhuma alegação de novidade.**

## 1. A tabela (a regra da seção 4, sem nada escolhido depois)

| hipótese | n | o que se mediu | IC 95 % | o limiar | leitura |
|---|---|---|---|---|---|
| **H-EMERGE** | 41 | B1 − B0 na P1: +0,005 | [0,000; 0,015] | acima de δ = 0,10 | **NÃO CONFIRMA** |
| **H-DOSE** | 41 | a inclinação da P1 em D0, DM, B1: +0,005 (médias 0,085, 0,085, 0,090) | [0,000; 0,015] | acima de 0 | **NÃO CONFIRMA** |
| **H-REP** | 16 (a P1 de A) e 160 (o `k` de A) | B1 − RM: o `k` de A −0,03 em S; a P1 de A 0,000 | `k` [−0,33; 0,23]; P1 [0; 0] | os dois acima de 0 | **INCONCLUSIVO POR PREMISSA** (16 < 30) |
| **H-CUSTO** | 160 | B1 − B0 na P3: −0,00001 | [−0,0001; 0,00006] | abaixo de ε = 0,02 | **CONFIRMA** |

## 2. O que explica a tabela

- **A CO7 quase não teve chance de agir.** Só 41 das 160 vidas tiveram ao menos uma oportunidade (o outro aflito indo para uma comida que o
  pet via), 197 oportunidades em todas, as mesmas em todos os braços. Nas vidas com oportunidade, a P1 já no B0 é 0,085: o irmão aflito
  quase nunca come a comida disputada, com ou sem os deveres.
- **O B1 mudou alguma medida em só 5 das 160 vidas.** As contenções foram 703 no B0 e 706 no B1; as disputas "anti", 6 nos dois; nenhum
  encosto em nenhum braço.
- **O pouco que mudou veio só do escudo (o R-ESCUDO).** O B1E (só o escudo) repete o B1 em tudo; o B1U (só a universalização) e o B1A (só a
  culpa e a inveja) repetem o B0 em tudo, como o D0 e o RM. A expectativa E-CB do plano (seção 7) previa o escudo explicando a maior parte;
  ela também previa a H-EMERGE passando, e não passou.
- **O dever chega, mas não encontra a situação.** O `k` do B1 fica no limiar do escudo ou acima em 51 % das decisões a partir do dia 1:
  o sinal da CO6 está lá. O que falta é a situação física que o escudo e a universalização leem, que é rara neste mundo (D-CO1-1, D-CO7b-6).
- **A culpa e a inveja não mudaram nenhuma decisão** (o B1A é igual ao B0 nas 160 vidas). Os pesos são os neutros (`w_culpa` = `w_inveja`
  = S/8, D-CO7b-5); este estudo não separa se elas não disparam ou se disparam e não viram decisão.

## 3. As frases que a leitura sustenta

- "No mundo do produto, com o comedouro comum e o dono atencioso, ligar os deveres (a CO7) não aumentou a parte das vezes em que o irmão
  aflito come a comida disputada: +0,005, IC [0,000; 0,015], longe do δ de 0,10."
- "Os deveres também não custaram nada ao próprio pet: a privação ficou igual (H-CUSTO)."
- "O efeito, onde houve, veio da proibição (o escudo), e não do empurrão (a universalização, a culpa e a inveja)."
- **Não entra:** "a cooperação não emerge nos pets". O estudo mostra que, neste mundo, a situação que a CO7 sabe ler quase não acontece; ele
  não testa a CO7 num mundo em que ela aconteça.

## 4. O que fica para decidir (nada roda sem o ok do Matheus)

- **Um mundo com mais disputa** (a CB-3 já previa voltar a ela): mais escassez no comedouro, ou o mundo que a CO7b usou no G-PAR-CO7, com
  um pet que emburra e anda muito. Seria um adendo ao plano, com as vidas novas numa faixa nova.
- **Os atos novos** (dividir, levar comida), que a CO7-5 já diz que fariam a universalização valer além da tabela da CO3.
- **A culpa e a inveja:** medir se disparam (uma contagem por decisão), antes de mexer nos pesos.
- **A H-REP** precisa de mais vidas com oportunidade do pet A; ela depende do mesmo mundo com mais disputa.

## 5. O adendo 1: o mecanismo, com o irmão aleatório (2026-11-12, A1-CB4)

**De onde vem:** a seção 12 do plano (DECIDIDA, AD1-1 a AD1-6), o piloto (D-CB-22, N = 80) e o registro (D-CB-24, `0d101300`). As 560
vidas (sementes 92201 a 92280, sete braços, o B com o cérebro aleatório, a CO7 só no A) rodaram em 270 s. O resultado está em
`artifacts_v3_cooperacao_bancada/resultado_ad1.json`, com o manifesto ao lado. **A leitura vale só para o mecanismo** (AD1-2): o B não é um
pet de verdade.

| hipótese | n | o que se mediu | IC 95 % | leitura |
|---|---|---|---|---|
| **A1-EMERGE** | 69 | B1 − B0 na P1 do A: +0,0008 | [−0,0014; 0,0039] | **NÃO CONFIRMA** (δ = 0,10) |
| **A1-DOSE** | 69 | a inclinação: +0,0008 (médias 0,139, 0,140, 0,140) | [−0,0014; 0,0039] | **NÃO CONFIRMA** |
| **A1-CUSTO** | 80 | B1 − B0 na P3 do A: +0,0009 | [−0,0012; 0,0034] | **CONFIRMA** (ε = 0,02) |

**O que explica a tabela:**
- **Agora a situação acontece:** 69 das 80 vidas com oportunidade, 837 a 839 oportunidades por braço, e o `k` do A no limiar do escudo em 56 %
  das decisões. Mesmo assim, a CO7 mudou alguma medida em só 12 das 80 vidas.
- **O pet de verdade quase não disputa a comida do aflito:** sem a CO7, o próprio A come a comida que o escudo proibiria em 8,1 % das
  oportunidades (a P1-neg); com a CO7, 7,2 %. O escudo tira essa pequena parte, e quem come no lugar quase nunca é o aflito: a P1 do A fica
  em 0,14 nos braços.
- **De onde vem o pouco que muda (o A1-ESCUDO):** o B1E (só o escudo) repete o B1 (+0,0008); o B1U (só a universalização) dá +0,0015; o
  B1A (só a culpa e a inveja) e o D0 repetem o B0.
- **A culpa e a inveja disparam, mas não viram decisão:** o termo da culpa passa de 0 em 11,7 % das decisões do A e o da inveja em 5,9 %, e
  o B1A é igual ao B0 em todas as medidas. A questão aberta da CB4 fica respondida: elas disparam, e com os pesos neutros (S/8) não mudam
  nenhuma escolha.

**As frases que a leitura sustenta:**
- "Mesmo quando a situação acontece muitas vezes, os deveres da CO7, com os pesos de hoje, quase não mudam o que o pet de verdade faz: o
  irmão aflito come a comida disputada +0,0008 vezes a mais (IC [−0,0014; 0,0039])."
- "O motivo é que o pet quase não disputava essa comida: o escudo só tem 8 % de escolhas para tirar, e a culpa e a inveja disparam sem mudar a
  escolha."
- **Não entra:** nada sobre os gêmeos do jogo (o B não é um pet de verdade), nem "a CO7 não funciona": o escudo faz o que diz (o G-ESCUDO
  passou em todas as vidas), só que há pouco a proibir.

**O que fica para decidir (nada roda sem o ok do Matheus):**
- **Os pesos da culpa e da inveja** (`w_culpa`, `w_inveja`, hoje S/8, PROPOSTOS) e o `w_univ`, na rodada de equilíbrio: são o único caminho
  da CO7 que empurra para o bem, e hoje não mudam nenhuma escolha.
- **Os atos novos** (dividir, levar comida), que dariam ao pet algo a fazer pelo outro, além de não pegar a comida dele.
