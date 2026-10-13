# Resultado — V2: a validação do mundo físico

Data: 2026-10-13. Plano: `docs/PLANO_ANALISE_V2_MUNDO_FISICO.md`, seções 7 e 8 e adendo 1 (A1.2, A1.3, A1.5, A1.8), com os números
congelados na A1.9. Autorizada pelo Matheus em 2026-10-12. Uma run, sem nada ajustado depois.

**Fonte dos números:** `artifacts_v2_mundo/validacao/`. Lá ficam `resultado.json` (os gates, o Holm, a leitura e os descritivos),
`medidas.json` (o registro compacto de cada vida), `medidas_completas.json` e `meta.json`. As vidas (`vidas/*.jsonl`) ficam fora do git e
saem de novo da config e do código.
- **Comando:** `python experiments/run_v2_validacao_mundo.py --config experiments/configs/v2_mundo/validacao.json --processos 8`.
- **A run:** código em `bfc1fa2` (base `930037b`, árvore limpa), Python 3.13.0, Windows, de 2026-10-13 00:33 a 01:23 (50 min de parede,
  6,5 h de CPU, 8 processos).
- **Os sha256** de `mundo.py`, `config.py`, `lobos.py`, `engine.py`, do plano, da config, da calibração (`resultado.json`) e do
  orquestrador estão no `meta.json`. O `mundo.py` é o da calibração: o desempate do cheiro do #232 não entrou.
- **O replay:** cada vida foi gravada e rejogada a partir do texto do disco, bit a bit, e o replay da medição também foi conferido.
  Nenhuma divergência.

## Resumo

- **G-MUNDO passa de novo:** P0z − P0 em `D_FE` **+0,0105 [+0,0048; +0,0159]** (na calibração, +0,0154). Explorar ainda compensa para
  o instinto, então o P1 é lido.
- **G-MF1r: o P1 PERDE.** P0 − P1 em `D_FE` **−0,0097 [−0,0149; −0,0046]**. O P1 termina com déficit de fome e energia **maior** que o
  P0, com o limite superior do IC95 abaixo de 0. O t pareado concorda (t = −3,69, gl 39).
- **G-MF2r não passa:** com o mesmo cuidado (os dois acoplados ao P0z), P0^ac − P1^ac **−0,0088 [−0,0123; −0,0051]**. A perda aparece
  também com o cuidado fixo, então **é do pet, não do dono reagindo**.
- **A leitura da A1.5 (terceira linha):** a consequência imediata não aprende a procurar neste mundo. **Resultado negativo, registrado.**
- **O que mudou no comportamento** (secundários; o G-PERM e o G-DIST passam no Holm, ambos sem Δ nem poder, A1.9):
  - **o P1 fica muito mais tempo em cada mancha:** permanência média de 352 min, contra 191 do P0;
  - a permanência do P1 cresce mais com o custo de viagem (G-PERM) e mais com o layout afastado (G-DIST), a direção que o plano prevê
    para quem forrageia;
  - mas ficar mais não paga: o `D_FE` piora.

## 1. O que rodou

| bloco | braços | vidas por unidade |
|---|---|---|
| malha fechada (A1.2) | P0, P0z, P1 | 12 × 3 = 36 |
| acoplados ao P0z da mesma célula, filtro `nenhum` (A1.2) | P0^ac (`P0<P0z:nenhum`), P1^ac (`P1<P0z:nenhum`) | 12 × 2 = 24 |
| layout afastado (A1.8) | P0 e P1 em `fisico_afastado` | 12 × 2 = 24 |

**As condições:**
- 40 unidades: as bases 32101…32505, K = 8 (prefixo `mundo`);
- 12 células: os 4 donos da v1 × comedouro, perto e longe;
- 14 dias, orçamento de 224;
- o mundo `fisico` (as frutas "iguais", PMF-7), `m` = 1;
- os donos só com o cuidado (PMF-3).
- **Total:** 3.360 vidas.

**O P1** é o do plano (seção 3): o cérebro A na montagem completa, ponto T3, ganho 4, canais ligados e `memoria_ganho` 512, com os
alvos padrão do motor. As chaves que o plano não pede ficaram desligadas e foram conferidas em código (`chaves_desligadas_conferidas` no
`meta.json`).

**A estatística:** por unidade, a média das 12 células da diferença entre os braços. O bootstrap reamostra as 40 unidades, com 10.000
reamostragens e a semente 4242. O IC95 é o primário; o IC90 serve só para a equivalência e para o rótulo "abaixo de Δ".

## 2. A premissa (G-MUNDO)

| contraste | média | IC95 | t pareado | passa |
|---|---|---|---|---|
| P0z − P0 em `D_FE` | +0,0105 | [+0,0048; +0,0159] | t = 3,66, gl 39 | **sim** |

O valor caiu em relação à calibração (+0,0154 [+0,0093; +0,0209]), mas o limite inferior continua acima de 0.

## 3. O primário (G-MF1r)

`Δ_MF` = 0,007675785900293976 (A1.9).

| contraste | média | IC95 | IC90 | categoria |
|---|---|---|---|---|
| P0 − P1 em `D_FE` | −0,0097 | [−0,0149; −0,0046] | [−0,0141; −0,0054] | **perde** |

- **Perde:** o limite superior do IC95 fica abaixo de 0. A categoria vem antes da equivalência na ordem da seção 8.
- **O tamanho:** a média passa de `Δ_MF` em módulo, e o IC90 inteiro fica fora de (−Δ, +Δ) pelo lado negativo.
- **A direção:** o P1 sustenta fome e energia **pior** que o instinto.

## 4. Os secundários (Holm, α = 0,05)

| gate | contraste | média | IC95 | p (bootstrap) | Holm | passa | declarado |
|---|---|---|---|---|---|---|---|
| G-MF2r | P0^ac − P1^ac em `D_FE` | −0,0088 | [−0,0123; −0,0051] | 1,000 | não rejeita | não | — |
| G-MF3r | P0 − P1 em privação | −0,0144 | [−0,0302; +0,0013] | 0,964 | não rejeita | não | subpotenciado (A1.9) |
| G-PERM | inclinação da permanência sobre o custo de viagem, P1 − P0 | +25,1 | [+17,2; +33,7] | 0,000 | rejeita (1º, limiar 0,010) | **sim** | sem Δ nem poder |
| G-OPORT | inclinação da permanência sobre a taxa recente, P1 − P0 | +25,6 | [−24,8; +77,5] | 0,828 | não rejeita | não | sem Δ nem poder |
| G-DIST | [P1(afastado) − P1(padrão)] − [P0(afastado) − P0(padrão)] na permanência média | +30,5 | [+12,5; +49,0] | 0,001 | rejeita (2º, limiar 0,0125) | **sim** | sem Δ nem poder |

- **As unidades de medida:**
  - as inclinações estão em minutos de permanência por célula de custo de viagem (G-PERM) e por fruta caída por hora (G-OPORT);
  - o G-DIST está em minutos.
- **Os p:** o p unilateral do bootstrap, orientado para a direção predita (no G-OPORT, P1 − P0 < 0).
- **Um gate passa** quando a regra do IC dele vale e o Holm rejeita.
- **Nenhuma unidade ficou sem valor** nas inclinações nem no G-DIST (40 de 40).
- **O G-MF2r** vai na direção contrária à predita: com o mesmo cuidado, o P1 também tem o déficit maior.
- **O G-OPORT** vai na direção contrária, sem IC fora de 0: o P1 não sai antes depois de dias ricos.
- **As inclinações por braço** (média das unidades):
  - sobre o custo: P0 +10,7, P1 +35,8;
  - sobre a taxa recente: P0 +30,7, P1 +56,3.
- **A permanência média:**
  - P0: 175 min no padrão, 192 no afastado;
  - P1: 260 min no padrão, 308 no afastado.

## 5. A leitura (A1.5)

Com o G-MUNDO passando:

| G-MF1r | G-MF2r | leitura |
|---|---|---|
| **perde** | não passa | **a consequência imediata não aprende a procurar neste mundo** (A1.5, terceira linha; seção 8) |

- **A perda é do pet.** O G-MF2r mostra a mesma direção com o cuidado fixo (P0^ac − P1^ac −0,0088), então não vem do dono reagindo ao P1.
- **O que os descritivos sugerem** (não decide nada):
  - o P1 aprendeu a **ficar** nas manchas, e mais quando elas são longe umas das outras (G-PERM, G-DIST), a forma qualitativa do
    forrageio;
  - mas faz menos visitas (19,3 por vida, contra 26,2 do P0) e fica mais em privação (0,190 contra 0,176);
  - com a janela imediata de crédito, o ganho fica com a decisão que come, e o gasto de andar com as que andam (R-1 do plano). Ficar perto
    da comida é o que essa conta premia. Isto é leitura, não teste.
- **"Ligar a consequência nos pets novos junto com o mundo físico"** (seção 8) não tem apoio nesta validação.

## 6. Descritivos (sem gate)

**Os níveis por braço** (média das 480 vidas; janela dos dias 8 a 14):

| braço | `D_FE` | `D_FE` vida | privação | consumos | visitas | permanência média (min) |
|---|---|---|---|---|---|---|
| P0 | 0,391 | 0,381 | 0,176 | 101,1 | 26,2 | 191 |
| P0z | 0,401 | 0,391 | 0,177 | 84,0 | 10,8 | 520 |
| P1 | 0,400 | 0,383 | 0,190 | 103,0 | 19,3 | 352 |
| P0^ac | 0,402 | 0,390 | 0,186 | 98,7 | 23,1 | 187 |
| P1^ac | 0,411 | 0,392 | 0,186 | 101,7 | 18,8 | 268 |

**Por dono** (`D_FE`, média e IC95):

| dono | P0 − P1 | P0^ac − P1^ac | P0z − P0 |
|---|---|---|---|
| atencioso | −0,0266 [−0,0365; −0,0157] | −0,0280 [−0,0356; −0,0202] | +0,0015 [−0,0123; +0,0143] |
| incoerente | −0,0198 [−0,0314; −0,0081] | −0,0246 [−0,0312; −0,0175] | −0,0060 [−0,0195; +0,0070] |
| aleatório | +0,0005 [−0,0052; +0,0062] | +0,0057 [−0,0009; +0,0121] | +0,0314 [+0,0247; +0,0386] |
| relapso | +0,0069 [+0,0017; +0,0123] | +0,0117 [+0,0060; +0,0176] | +0,0152 [+0,0104; +0,0201] |

- **A perda vem dos donos que cuidam** (atencioso e incoerente).
- **Com o relapso, o P1 ganha um pouco**, e com o aleatório empata. São os mesmos donos em que explorar compensa para o instinto (R-3 do
  plano).
- Fica como descritivo, sem gate; o plano não testa por dono.

**Por lugar** (`D_FE`):

| lugar | P0 − P1 | P0^ac − P1^ac | P0z − P0 |
|---|---|---|---|
| comedouro | −0,0083 [−0,0221; +0,0061] | −0,0213 [−0,0299; −0,0126] | −0,0250 [−0,0388; −0,0128] |
| perto | −0,0157 [−0,0197; −0,0118] | −0,0083 [−0,0150; −0,0011] | +0,0170 [+0,0135; +0,0208] |
| longe | −0,0053 [−0,0137; +0,0037] | +0,0033 [−0,0005; +0,0069] | +0,0396 [+0,0307; +0,0485] |

**O lugar como cuidado (P0):** longe − comedouro +0,0249 [+0,0091; +0,0399]; perto − comedouro −0,0716 [−0,0845; −0,0597].

**Medida 2, a taxa no abandono contra a média da vida** (A1.8, só descritiva):
- P0 1,383, P1 1,389;
- P1 − P0 +0,006 [−0,064; +0,076].

Os dois saem da mancha com a taxa recente acima da média, sem diferença entre eles.

**Não medidos** (o plano os lista como descritivos; o orquestrador não os calcula): o ganho líquido por hora de busca, a latência até
achar, as frutas das árvores comidas, o deslocamento por região, o tempo livre por ação, a fome urgente, o teto do P1 e o tempo de
desistência (seção 9).

## 7. O custo

| braço | vidas | s de CPU por vida |
|---|---|---|
| P0 | 480 | 6,70 |
| P0z | 480 | 3,78 |
| P1 | 480 | 8,35 |
| P0^ac | 480 | 6,65 |
| P1^ac | 480 | 8,30 |
| P0 afastado | 480 | 6,66 |
| P1 afastado | 480 | 8,32 |

6,5 h de CPU somadas e 50 min de parede com 8 processos. A calibração estimou 6,3 h e ~0,8 h.

## 8. Desvios e achados (detalhes em `docs/REGISTRO_DESVIOS.md`)

- **O Holm e os "descritivos declarados".** O pedido dizia "G-MF3r e os sem Δ como descritivos declarados"; o plano (A1.8) põe os cinco
  no Holm. Rodou o plano: o Holm cobre os cinco, e cada um leva o rótulo declarado (subpotenciado, ou sem Δ nem poder). O G-PERM e o
  G-DIST passam no Holm, mas não entram na regra de decisão da A1.5, que só lê o G-MF1r e o G-MF2r.
- **O G-MF3r subpotenciado** (A1.9) não passou, e a direção também é contrária (o P1 com mais privação).
- **O disco D: encheu** no meio do trabalho (2026-10-12). A run saiu depois que o Matheus liberou espaço, no lugar pedido. Nada foi
  apagado por mim.
- **A suíte da primeira tentativa,** rodada junto com a validação, teve duas falhas:
  - o teste das faixas, porque a config da validação passou a ter as bases de validação do mundo. O teste foi atualizado para aceitá-las
    nas configs do próprio plano;
  - uma falha do `test_grupo` que não se repete sozinha. Rodada de novo depois da run, com a máquina livre, a suíte passa inteira:
    2481 passed, 2 skipped, 36 min.
- **O desempate do cheiro do #232** continua fora do motor.

## 9. O que vem depois

Nada desta frente roda de novo: a validação é única. As perguntas que ela deixa são para o Matheus:
- a consequência com crédito entre decisões ou com plano (R-1), que o plano já apontava como o caso que a janela imediata não resolve;
- o alvo aprendido (`escolher_alvo`, outro adendo), para o P1 aprender **para onde** ir, e não só **quando**.
