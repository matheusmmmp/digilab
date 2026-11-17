# RESULTADO V3 — SONDA_EMPOWERMENT, F5: o E(P) varia entre lugares? (2026-11-17, sessão da F5, Claude Code, Opus 5.5)

**A leitura final, pela (b2) do adendo 1 (seção 7): "plano". A F5 acaba sem plano para a H-EMP-1.** A primeira medida, nas vidas
da AN0, tinha dado **"plano pelas entradas"**. Por isso a F5 seguiu para a opção (b) da D-F5-2,
que as decisões D-F5-10 e D-F5-11 levaram às vidas no mundo com árvores (seções 4, 6 e 7).

O papel é descritivo, sem gate (D-F5-1, "Pesquisa, com sonda").

## 1. De onde vem

- O plano: `docs/PLANO_ANALISE_V3_SONDA_EMPOWERMENT.md`, APROVADO pelo Matheus em 2026-11-17 ("Aprovo o plano"), com a D-F5-9 aceita.
  Ele foi commitado em `c27ecb91`, antes do primeiro artefato. O sha256 dele, `8ada173a…`, está nas fontes do `sonda.json`.
- O código: `experiments/sonda_empowerment_f5.py`, rodado uma vez com `--processos 4`, em 20 s de parede.
- Os artefatos, em `artifacts_v3_f5_sonda/`:

| arquivo | sha256 |
|---|---|
| `sonda.json` | `5d6731b49f38d8d2294c378b634fa5ed017c0d39df4c383dbaa1e257e5c2b8f3` |
| `sonda_decisoes.json.gz` | `d77d22a18d490634633a37b063645b8104c73d11729b34daa655078c6c03d39b` |

- As conferências: as 10 vidas saíram iguais aos gabaritos (G-S0), e as rngs não mudaram em nenhuma leitura (G-S1). Uma leitura por
  decisão: 384 em cada vida, 3.840 no total.

## 2. Os números (FATO VERIFICADO, do `sonda.json`, chave `todas`)

**M-S1, a variação:**
- o `E` do lugar do pet: mínimo 1, quartis 1, 1 e 2, máximo 5;
- `E > 1` em 1.720 das 3.840 decisões;
- a amplitude do `E` entre os lugares de cada decisão: mínimo 0, quartis 0, 0 e 0, máximo 2;
- amplitude ≥ 2 em **42 das 3.840** decisões (1/10 seria 384);
- o `CONT` do lugar do pet ≤ 1 em **3.485 das 3.840** decisões (a metade seria 1.920).

**M-S2, os pares de lugares (122.824 no total):**

| concordantes | discordantes | empate só no `E` | empate só no `CONT` | empate nos dois |
|---|---|---|---|---|
| 0 | 0 | 0 | 5.338 | 117.486 |

**M-S3, exploratória:** nenhuma decisão entrou na conta. As 113 decisões de `explorar/ponto` não tiveram dois ou mais alvos
candidatos.

**Por vida:** as 10 vidas estão em `sonda.json`, chave `vidas`. A amplitude ≥ 2 vai de 0 a 18 decisões em 384. Nas quatro vidas do
`comedouro`, ela é 0, e o `CONT` do lugar do pet ≤ 1 vai de 338 a 384.

## 3. A leitura (plano, seção 4)

Com os limiares PROPOSTOS, SEM FONTE (D-F5-7):
- **"plano": sim.** 42 × 10 < 3.840.
- **"igual ao CONT": sim**, pela conta. Os discordantes são 0 de 122.824 pares (seção 4).
- **A exceção da D-F5-9: sim.** Deu "plano", e o `CONT` do lugar do pet ≤ 1 vale em 3.485 decisões, mais da metade.

A linha que o código escreveu, pela ordem do plano: "plano pelas entradas: a F5 espera a decisão do Matheus sobre a opção (b) da D-F5-2".

## 4. O que a M-S2 não pôde ler (achado, D-F5-A no registro)

**FATO VERIFICADO** (`sonda_decisoes.json.gz`): o `CONT` é o mesmo em todos os lugares de cada uma das 3.840 decisões. Nenhum par tem
`CONT` diferente, então nenhum par pode ser concordante nem discordante. O "igual ao CONT" saiu "sim" porque o `CONT` não varia, não
porque o `E` o acompanha. Nos 5.338 pares em que o `E` muda, o `CONT` fica igual.

**HIPÓTESE:** o alcance da memória de lugar (`d_max = 1024` subunidades, `digilab/config.py:2982`) cobre o mapa inteiro destas vidas.
Assim, todo lugar alcança as mesmas classes, e o `E` só muda pelo custo de andar até elas. Isso não foi medido.

**O que fica para o Matheus decidir:** se o "igual ao CONT" degenerado encerra a F5. O plano, seção 4, encerra a F5 com "plano" ou
"igual ao CONT", e a exceção da D-F5-9 só fala do "plano". A recomendação está na seção 6, como D-F5-10.

## 5. Limitações

As da seção 6 do plano continuam valendo. Além delas:
- **As entradas são estreitas.** O pet alcança no máximo duas classes. O `CONT` vai de 0 a 2, e o `E` de 1 a 5.
- **A M-S3 não leu nada.** Por isso esta medida não diz se o pet escolhe alvos de `E` maior.
- **Nenhuma alegação de novidade.** A conta é a forma determinística do empowerment (Salge, Glackin e Polani 2014).

## 6. As decisões do Matheus

| id | pergunta | recomendação | custo de errar |
|---|---|---|---|
| **D-F5-2 (b)** | rejogar uma run já feita, com mais classes ao alcance, depois de conferir o replay dela? | sim, com um adendo a este plano antes da medida | sem ela, a F5 para sem ter visto o `E` num mundo em que ele pode variar; com ela, custa uma etapa de conferência do replay |
| **D-F5-10** | o "igual ao CONT" degenerado (o `CONT` não varia entre lugares) encerra a F5? | não: ler como "a M-S2 não leu", como no caso sem pares do código | se encerrar, a F5 acaba por uma conta que não comparou nada; se não encerrar, a separação do `CONT` continua sem resposta até a opção (b) |

**Decisão:** as duas aceitas como recomendadas. À pergunta "Aprova a D-F5-2 (b) e a D-F5-10 como recomendadas?", o Matheus respondeu "Aprovo as duas" (2026-11-17). A F5 segue para a opção (b): primeiro um adendo a este plano
(PROPOSTO, com a run escolhida e a conferência do replay), depois a medida. A M-S2 desta medida fica como "não leu".

## 7. A (b2): o mundo com árvores (adendo 1, 2026-11-17)

**A leitura: "plano". Pelo plano, seção 4, a F5 acaba aqui, sem plano para a H-EMP-1.**

**De onde vem:**
- o adendo 1, `docs/PLANO_ANALISE_V3_SONDA_EMPOWERMENT_ADENDO1.md`, APROVADO ("Aprovo a (b2)") no commit `1026eb55`;
- o código e os testes no commit `86f7ba5d` (26 testes passam);
- o gabarito, `tests/gabaritos/sonda_f5_b2.json`, num commit próprio, o `096ba70c`, antes da medida.

**As vidas:** as oito células da AN0 (2 donos × 2 lugares × as sementes 101 e 202), 4 dias cada, no `CONFIG_MUNDO_ILHA`, com o sacudir
ligado e nenhum dono sacudindo.

**A medida:** rodou uma vez com `--b2 --processos 4`, em 5 s. As 8 vidas saíram iguais ao gabarito (G-S0), e nenhuma leitura mudou uma
rng (G-S1). São 3.072 decisões.

| arquivo (`artifacts_v3_f5_sonda/b2/`) | sha256 |
|---|---|
| `sonda.json` | `6f8663f3043834d87c73760b981867fff24fc5aa6be1974eebdcabd5d150cd7f` |
| `sonda_decisoes.json.gz` | `f24cecc090e1178f9ddbc92464d6613f9117d1532c8bae5078185626add6d4c1` |

As fontes no `sonda.json`: o plano `8ada173a…`, o adendo `ab2725de…` e o gabarito `0a2b9479…`.

### 7.1 As entradas (a conferência do adendo, seção 5)

As frutas chegaram ao pet. Caíram 4 frutas nas vidas da semente 101 e 10 nas da 202. Em todas as oito vidas há episódios de consumo de
fruta guardados no fim: a `a` em quatro vidas, a `b` em sete, a `c` em quatro. Numa vida também há um consumo de ração podre. Nas duas
vidas da semente 101 no `longe_fixo`, o pet só guardou consumos de fruta.

### 7.2 Os números (FATO VERIFICADO, `sonda.json`, chave `todas`)

**M-S1, a variação:**
- o `E` do lugar do pet: mínimo 1, quartis 1, 1 e 2, máximo **8** (na primeira medida, o máximo era 5);
- `E > 1` em 1.398 das 3.072 decisões;
- a amplitude entre os lugares de cada decisão: quartis 0, 0 e 0, máximo 3;
- amplitude ≥ 2 em **79 das 3.072** decisões (1/10 seria 307). Por vida, isso vai de 1 a 34 em 384;
- o `CONT` do lugar do pet ≤ 1 em **973 das 3.072** decisões. A metade seria 1.536, então a exceção da D-F5-9 não vale.

**M-S2, os pares (122.542):**

| concordantes | discordantes | empate só no `E` | empate só no `CONT` | empate nos dois |
|---|---|---|---|---|
| 0 | 0 | 0 | 10.302 | 112.240 |

Como na primeira medida, o `CONT` é o mesmo em todos os lugares de cada decisão. Pela D-F5-10, a M-S2 **não leu**.

**M-S3:** nenhuma decisão de `explorar/ponto` teve dois candidatos.

### 7.3 A leitura

- **"plano": sim.** 79 × 10 < 3.072.
- **"plano pelas entradas": não.** 973 × 2 < 3.072. Agora o pet tinha mais de uma classe ao alcance na maioria das decisões, e o `E`
  continuou quase igual entre os lugares.
- **"igual ao CONT":** o código escreveu "sim", e a linha do `sonda.json` diz "a F5 acaba: plano e igual ao CONT". O código não lê a
  D-F5-10, que veio depois dele. Pela D-F5-10, essa parte fica "não leu". A conclusão não muda, porque o "plano" sozinho encerra a F5.

**A F5 acaba sem plano.** A H-EMP-1 não segue para um plano depois da F3.

O que esta leitura **não** diz:
- que o `E` não varia em outro mundo. O mapa de hoje cabe no alcance da memória (`d_max = 1024`), e por isso todo lugar alcança o mesmo;
- nada sobre a ilha grande;
- nada sobre a separação do `CONT`, que não leu nas duas medidas.

### 7.4 Limitações

As da seção 5 continuam valendo, e mais duas:
- É um mundo do jogo, sem run de pesquisa, com oito vidas curtas de sementes dos testes. O resultado não fala do pet da pesquisa.
- As frutas são poucas: de 4 a 10 quedas por vida.
