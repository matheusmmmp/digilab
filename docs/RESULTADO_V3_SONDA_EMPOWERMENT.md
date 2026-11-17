# RESULTADO V3 — SONDA_EMPOWERMENT, F5: o E(P) varia entre lugares? (2026-11-17, sessão da F5, Claude Code, Opus 5.5)

**A leitura registrada: "plano pelas entradas".** A F5 não acaba. Ela espera a decisão do Matheus sobre a opção (b) da D-F5-2 (uma
run já feita, depois de conferir o replay). Há uma segunda decisão, sobre como ler a M-S2 (seção 4).

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
