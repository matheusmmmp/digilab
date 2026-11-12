# Plano da investigação do núcleo da luta da POC (LUTA_POC, N0)

Worker: Claude Code, Opus 5.5, worktree `D:\Trab\digilab\v3-luta-nucleo`, branch `v3-luta-nucleo-plano`, 2026-11-12, a pedido do Gerente
de sprites e luta (a sessão `local_a6f79153`). A tarefa é a `docs/TAREFA_V3_LUTA_POC.md`. Este plano é a investigação que a D-LP5-13, a
D-LP5-15, a D-LP5-18, a D-LP5-19 e a D-LP5-21 mandaram para depois, e a lista "ficam para depois" da LP6-3.

**Status: APROVADO.** As decisões D-N-1 a D-N-7 (seção 6) estão DECIDIDAS como recomendadas: o Matheus, em 2026-11-12, "Aprovo as 7
(Recommended)" (repassado pelo Gerente). A régua e a ordem foram aprovadas; os números novos (a faixa, os valores do `forca`, os tempos de
máquina) seguem PROPOSTOS, SEM FONTE.

**O que este PR é:** só documento. Nenhum código, nenhuma luta e nenhuma rodada da bancada. As leituras da seção 1.2 usam JSON que já estão
no repositório.

**O que vale:**
- **"Equilíbrio só no fim."** A investigação acha a causa de cada meta que não fecha. Ela não calibra e não muda nenhum número do jogo. A
  calibração geral vem depois, com as causas na mão.
- **Mecânica nova vai atrás de uma chave desligada.** Desligada, as versões vivas lutam byte a byte como hoje (seção 4).
- **A máquina:** no máximo 4 processos, e uma rodada de pesquisa por vez (`tools/pre_run.py --medicao`; as medições da luta contam).
- **Fica como está:** a IA igual para os dois lados (a LP-3), os mapas de cada lugar (a LP-4), as séries sem cura (a decisão 5 da LP2) e o
  Python congelado (a LP-7).

## 1. A pergunta

**Por que estas metas não fecham com nenhuma alavanca da LP5 nem da LP6?** Para cada uma, o que a decide:
- **o núcleo:** uma regra de `sim.ts` ou de `nucleo.ts`;
- **o mapa:** uma regra de `cenas.ts`, como o Ringue;
- **a série sem cura:** a vida que passa de uma luta para a outra;
- **a tabela das formas:** o atributo, o golpe e o projétil de cada forma em `formas.ts`;
- **a régua:** um critério que nenhuma luta pode cumprir.

### 1.1 As metas, com o valor de hoje

Os valores são do `lp5_3`, a luta da v23, e do `lp6_3_u120`, a luta da v29, na calibração
(`web/app/scripts/medicoes/equilibrio_poc/lp5_3/calibracao/resumo.md` e `lp6_3_u120/calibracao/resumo.md`). No Rookie e no Champion as
duas lutas são a mesma.

| meta | o critério | hoje (v23 / v29) |
|---|---|---|
| **G1**, a Liga | título em ≥ 0,25 | 0 títulos em 2 000 tentativas, nas duas |
| **G2**, a Torre | recorde mediano de 3 a 30 | 1, nas duas; o máximo é 2 |
| **G3**, a Fábrica | uma série de 3 em ≥ 0,25 | 0,002 / 0 |
| **P5**, a vida até o Mega | ≥ 0,80 das vidas | 0,19 / 0,18; as vidas param no Champion como colosso (D-LP5-18) |
| **V2**, a espécie | amplitude ≤ 0,15 | 0,25 / 0,19 / 0,07 / 0,20 (v23), do Rookie ao Mega |
| **P2 e P3**, os 7 NPCs | o critério da D-LP5-17 | o Guardromon, o Youkomon, o Myotismon, o Piedmon, o Devidramon, o Puppetmon e o Machinedramon reprovam |
| **A1**, o Ringue | de 0,30 a 0,70 por mapa | 0,09 / 0,13 / 0,15 / 0,21 (v23); 0,19 e 0,26 no Ultimate e no Mega (v29) |
| **A1**, o Castelo | idem | 0,16 e 0,23 no Rookie e no Champion |
| **V1**, a variedade | cada forma de 0,35 a 0,65, amplitude ≤ 0,30 | reprova em todos os estágios |
| **T2**, os stats | cada stat ≥ 0,60 | o fôlego fica em 0,48 e 0,49 |
| **D2**, os empates | ≤ 2 % por forma | 3,7 % no total, até 9,5 % numa forma |
| **S1**, o espelho | fora da Praia (D-LP5-13) | passa; a Praia e o Ringue do Rookie (0,451) ficam na beira |

### 1.2 O que se lê sem luta nova

**(a) O atributo decide quase toda luta.** Esta leitura foi feita ao escrever o plano, só sobre os JSON das formas que já estão no
repositório. O script e a saída ficaram fora do repositório, na pasta de notas do Gerente (`luta_nucleo_n0/`). A N1 refaz a leitura com
artefato no repositório, e até lá os números abaixo são preliminares.

A conta separa os pares de formas diferentes do mesmo estágio pelo triângulo de `sim.ts` (`VENCE`: o Vaccine vence o Virus, o Virus vence o
Data, o Data vence o Vaccine; `OPCOES_PADRAO.forca` = 1,5):

| luta | com vantagem | sem vantagem | com desvantagem |
|---|---|---|---|
| v21 (`lp5_0`) | de 0,82 a 0,99 | perto de 0,50 | de 0,01 a 0,12 |
| v23 (`lp5_3`) | de 0,99 a 1,00 | de 0,44 a 0,49 | de 0,003 a 0,008 |
| v29 (`lp6_3_u120`) | de 0,99 a 1,00 | de 0,44 a 0,49 | de 0,001 a 0,005 |

O mesmo vale na conferência (`lp5_4`). Um caso direto, no `formas_crianca.json` do `lp5_3`, no Campo: o Agumon (Vaccine) vence o Guilmon
(Virus) em 125 de 125 lutas e perde para o Patamon (Data) em 125 de 125.

Os mesmos JSON mostram o porquê, pelo `gama` da v23 (`motor/luta_poc.ts`, `LUTA_V23`). São contas sobre as constantes, não medida:
- o expoente é 0,02 no vigor, na força e na recuperação. Com ele, um stat 10 vezes menor muda a vida e o ataque em uns 4,5 %
  (0,1^0,02 ≈ 0,955), e o treino típico do Mega muda uns 5 %;
- o atributo multiplica o dano por 1,5 de um lado e por 1/1,5 do outro, uma razão de 2,25 entre os dois.

Na v21, com o expoente 1, os stats ainda pesavam contra o atributo. Na v23, o atributo pesa mais que qualquer diferença de stats.

**(b) Os líderes pelo atributo.** A mesma leitura, sobre o `lideres.json` do `lp5_3`, separa os pets pelo atributo da forma deles contra o
NPC:
- **com vantagem**, o pet vence de 0,99 a 1,00, com treino ou sem;
- **com desvantagem**, perde de 0,92 a 1,00, com treino ou sem;
- **só nas lutas sem vantagem** o treino pesa: no Guardromon, de 0,42 sem treino para 0,96 com o típico;
- **7 dos 10 NPCs são Virus.** Contra eles, de 0,42 a 0,48 dos pets têm vantagem. No Guardromon (líder do Champion, limite 0,35), no
  Piedmon (líder do Mega, 0,27), no Puppetmon e no Machinedramon (desafiantes do Mega, 0,42), essa fração já põe o "sem treino" acima do
  limite da D-LP5-17, qualquer que seja o total do NPC. O Devidramon (desafiante do Champion, 0,50) reprova pelo típico (0,645 contra 0,70);
- **o MarinBullmon, que é None,** é o único com o caminho inteiro do sem treino ao típico (0,26 para 0,82);
- **o Youkomon (Data) e o Myotismon** reprovam pelo outro lado: o típico não chega ao limite. O Myotismon tem a série de 3 da Cidadela, sem
  cura, e o típico com vantagem vence a série só em 0,52.

**(c) O P5 pela forma.** A leitura da vida (`lp5_2/leitura_vida/leitura.json`) dá o colosso no sparring do Champion de 0,52 (o Growlmon,
Virus, da brasa) a 0,78 (limo), contra 0,80 a 0,97 das outras formas. Entre os 16 rivais do Champion, 8 são Vaccine, que vencem o Virus.

**(d) As séries sem cura, pela conta.** O pet que vence leva para a luta seguinte a vida que sobrou (`vida0`, na `bancada.ts`). Contra um
rival do mesmo estágio, com o atributo neutro e os stats a uns 5 % um do outro, o vencedor perde perto de metade da vida (HIPÓTESE, SEM
FONTE; a N2 mede). Seis vitórias seguidas (a Liga) pedem uma perda perto de 1/6 da vida por luta. O fator 0,1 nos rivais da D-LP5-20 tira
uns 4,5 % da vida e do ataque deles pelo `gama` da linha (a), longe do que falta. Isso explica por que a grade `lp5_3/r2` não moveu a Liga
nem a Torre, e põe em dúvida a leitura da LP5-3 de que "quem decide as séries são as regras dos mapas" (D-LP5-21). As duas causas podem
valer juntas, e a N2 as separa.

**(e) O Ringue e o Castelo, pelo código.** São leituras de `cenas.ts` e `sim.ts`, não medida:
- **no Ringue** não há cerca (`prender` não age), o golpe empurra 2 vezes e a habilidade 7 vezes, e quem sai perde 15 % da vida. Quem
  atira recua (o `recuo` 1,5 e o `recuaNaPrep` 2 da v23) e pula na esquiva (380 px/s vezes a agilidade, por 180 ms). O recuo e o pulo não
  olham para a borda. O medo da borda (o `guia`) só começa a 0,8 do raio e soma com o recuo;
- **no Castelo**, os pilares ficam entre os pontos de entrada em x (168 e 312; a entrada é em 110 e 370), a 20 e 40 px da linha delas. O
  pilar quebrável não impede o tiro (`livre` vale com `hp`), então quem atira com um pilar no caminho gasta até 3 tiros nele. Quem bate de
  perto anda pelo centro, onde fica a runa dos 30 %. Quanto cada um pesa não se lê do código: a N2 mede.

**(f) Os empates, pelo código.** Em `aplicarDano` o golpe não confere se quem atirou já caiu, e a luta só acaba quando não há projétil no ar
(`passo`). Um tiro em voo de quem acabou de cair ainda derruba o outro, e a luta acaba em empate. O espelho do Agumon no Campo do `lp5_3`
empata 22 de 125 vezes.

**(g) O fôlego, pelo código.** Com a esquiva da v23, a agilidade é `(fôlego/10)^0,6`. Com 8 pontos de treino a 15 cada, o fôlego vai de
uns 10 a uns 130, e a agilidade a 4,7 (conta sobre as constantes). O pulo da esquiva passa de 68 px para uns 320 px, mais que o raio da
elipse (210). O pulo pode jogar o pet contra a cerca, na lava, na areia, ou para fora do Ringue (HIPÓTESE, SEM FONTE).

**(h) A Praia, pelo mapa.** As duas rochas não são simétricas (x 175, y 146, raio 11, e x 318, y 168, raio 10). A da direita fica na linha
das entradas (y 166) e mais perto do lado B. A IA também não é simétrica no passo: o lado A anda antes do B (`passo`).

### 1.3 As hipóteses de cada meta

| meta | a hipótese principal | a alternativa | de quem é |
|---|---|---|---|
| **G1**, a Liga | H-SÉRIE: o vencedor perde cerca de metade da vida por luta, e seis seguidas não cabem | H-MAPA: a Floresta e a Praia (onde a Liga para com o fator 0,1) derrubam o pet; H-ATR: um rival com vantagem na série | a série e o núcleo |
| **G2**, a Torre | H-RINGUE: o pet cai do Ringue (a Torre é toda no Ringue) | H-SÉRIE | o mapa |
| **G3**, a Fábrica | H-RÉGUA: Mega canônico contra Mega canônico, sem cura, não chega a 0,25 nem com a cura (a conta: com 0,5 por luta, 0,125) | H-SÉRIE | a régua; a Fábrica é do Tamer (D-LP5-5-5) |
| **P5** | H-FORMA: a vida chega ao Champion como colosso, e o Growlmon (Virus) perde para os 8 Vaccine | H-ATR no núcleo | a tabela das formas e o núcleo (o `forca`) |
| **V2** | H-ATR: a espécie é um conjunto de atributos | a forma (o golpe) | a tabela das formas e o núcleo |
| **os 7 NPCs** | H-ATR com H-RÉGUA: com o atributo decidindo, o "sem treino" tem um piso igual à fração de pets com vantagem | o total e a divisão (já descartados pela LP5-2) | o núcleo (o `forca`), a tabela (o atributo do NPC) e a régua |
| **A1**, o Ringue | H-RINGUE: o recuo e o pulo de quem atira o levam para fora | H-ATR: as formas de perto de cada estágio têm outro atributo que as de longe | o mapa e o núcleo |
| **A1**, o Castelo | H-PILAR: o tiro gasto no pilar e a runa no centro | H-ATR | o mapa |
| **V1** | H-ATR: a taxa de cada forma é a conta dos atributos do estágio | a forma | a tabela das formas |
| **T2**, o fôlego | H-PULO: a agilidade sem teto faz o pulo passar da arena | o fôlego só move quem anda (sem efeito na luta parada) | o núcleo |
| **D2** | H-TIRO-MORTO: o tiro de quem caiu ainda acerta | o dano do mapa nos dois no mesmo passo | o núcleo |
| **S1** (Praia, Ringue) | H-ROCHA: as rochas assimétricas | H-ORDEM: o lado A anda primeiro | o mapa e o núcleo |

**A H-ATR pode explicar boa parte de V1, V2, P2, P3, P5 e do A1 por estágio,** e ela tem duas partes:
- **o núcleo:** o tamanho do efeito (o `forca` 1,5) e o triângulo;
- **a tabela das formas:** quantas formas de cada atributo há em cada estágio, e o atributo dos NPCs.

## 2. Como separar as hipóteses

A ordem vai do mais barato ao mais caro. **Nenhuma grade** antes que as leituras e as lutas fixas digam onde está a causa.

| medida | o que é | o custo | o que separa |
|---|---|---|---|
| **M0, as releituras** | os JSON que já existem, sem luta nova: cada meta separada pelo atributo do par (vantagem, neutro, desvantagem) | segundos | a H-ATR em V1, V2, A1, P2, P3, P5; o piso de cada NPC |
| **M1, as contas** | as constantes, sem luta: o que o `gama` deixa de cada alavanca; o teto aritmético de cada meta de série | segundos | a H-RÉGUA (G3, os NPCs) |
| **M2, as lutas fixas** | poucas lutas, com o motor de hoje e sem chave nova, gravando os eventos de cada passo (`rodarAteOFim` com o `aoPasso`) | minutos, 1 processo | H-SÉRIE, H-RINGUE, H-PILAR, H-TIRO-MORTO, H-PULO, H-ROCHA |
| **M3, os contrafactuais** | uma chave desligada por hipótese, medida sozinha contra as 21 metas | ~10 min por chave em 4 processos | quanto cada causa move, e o que ela quebra |

### 2.1 O M2: as lutas fixas

Cada pergunta tem uma luta montada, com a forma, o mapa e as sementes fixas, e a contagem dos eventos que já existem: `dano`, `queda`,
`queda_ringue`, `ambiente`, `pilar`, `tiro_bloqueado`, `fim`.

| pergunta | a luta | o que se conta |
|---|---|---|
| **a série (G1)** | o Mega típico contra os 6 Megas da Liga, um a um, com a vida cheia em cada um | a vida que sobra no vencedor, por mapa e por atributo do par. A série cabe se a soma das perdas ficar abaixo de 1 |
| **o Ringue (G2, A1)** | os pares de longe contra perto, e o Mega típico da Torre | cada `queda_ringue`: quem caiu e o que o levou à borda (o empurrão do golpe, o empurrão da habilidade, o recuo, o pulo da esquiva). O motor não diz a causa, e por isso a medida guarda a posição e o estado de quem caiu nos passos antes da queda |
| **o Castelo (A1)** | os mesmos pares, no Castelo | os tiros gastos em pilar (`pilar`), quem pega a runa (`runa`) e a vitória com e sem a runa |
| **os empates (D2)** | os espelhos e os pares com mais empate | o empate em que o último dano veio de quem já tinha caído, contra o empate pelo dano do mapa |
| **o fôlego (T2)** | o pet com 8 pontos no fôlego contra ele sem treino | o tamanho de cada pulo, as quedas e o dano do mapa logo depois do pulo |
| **a Praia (S1)** | o espelho na Praia, e o mesmo com os dois lados trocados de lugar | o lado A contra o lado B, e onde cada um fica preso na rocha |

**As sementes:** uma faixa nova, a `92101…92505` (PROPOSTA, a D-N-2). A 86xxx é da calibração, e a calibração geral vai precisar dela
limpa. A 87xxx é a conferência, que roda uma vez. Conferido nesta data: a 92xxx não está na `FAIXAS_RESERVADAS` nem é citada nos documentos,
nos scripts ou nas ferramentas. A 91xxx foi proposta pelo plano da cooperação.

### 2.2 O que fica com a tarefa da tabela das formas

A tabela das formas é uma tarefa separada, e ainda não existe. A investigação não mexe nela, mas entrega as causas que são dela:
- **o atributo de cada forma e o de cada NPC.** Hoje 7 dos 10 NPCs são Virus, e no Champion 8 das 16 formas são Vaccine;
- **o colosso:** o Growlmon (Virus) e o golpe de perto do Gatomon, com o clipe de 1 432 ms;
- **o golpe, o tempo e o projétil de cada forma** (o V1 que sobra depois do atributo);
- **a lista da LP-8,** que não muda.

**O que fica com o núcleo:**
- o `forca` (1,5) e o triângulo;
- o tiro de quem caiu;
- o pulo da esquiva sem teto;
- a borda do Ringue para o recuo e o pulo;
- a ordem dos lados.

**O que fica com a régua:** o G3 e o critério dos NPCs. A investigação só diz o teto aritmético de cada meta. Trocar a régua é decisão do
Matheus, depois da N5 (a D-N-4).

## 3. As etapas

| etapa | o quê | o PR | a máquina (SEM FONTE) |
|---|---|---|---|
| **N0** | este plano | este | nenhuma |
| **N1, as releituras e as contas** | um script de leitura em `web/app/scripts/equilibrio_poc/` (`leitura_nucleo.ts`, só leitura, como o `releitura_s1.ts`): o M0 e o M1 sobre os JSON do `lp5_0`, do `lp5_3`, do `lp6_3_u120` e do `lp5_4`. Os artefatos vão em `web/app/scripts/medicoes/luta_nucleo/n1/` | um PR com a N2 | menos de 1 min, 1 processo |
| **N2, as lutas fixas** | um script de lutas fixas (`lutas_fixas_nucleo.ts`) com o motor de hoje, sem chave nova, nas tabelas da v21, da v23 e da v29. Antes, a reserva da 92xxx num commit próprio | o mesmo PR | de 50 000 a 100 000 lutas, com os eventos de cada passo: de 5 a 20 min em 1 processo |
| **N3, as chaves** | uma chave desligada para cada causa que a N2 confirmar (a seção 4). Primeiro, num commit próprio, o gabarito das versões vivas | um PR próprio | a suíte do web e os gabaritos: de 15 a 30 min |
| **N4, os contrafactuais** | cada chave ligada sozinha, e as que se somam juntas, numa medida inteira das 21 metas na 92xxx, com o `lp5_3` e o `lp6_3_u120` de base | um PR com a N5 | de 6 a 10 medidas de ~10 min em 4 processos (a LP5 mediu 1,4 milhão de lutas em 2 134 s de processo): de 1 a 2 h, em cargas separadas |
| **N5, o relatório** | a causa de cada meta, quanto cada chave move, o que cada uma quebra e o que vai para a tabela das formas e para a calibração geral. Nenhum número entra no jogo | o mesmo PR | nenhuma |

**A regra de parada:** cada etapa para e entrega. A N3 só começa com a decisão do Matheus sobre o que a N2 confirmou (a D-N-5). Uma hipótese
que a N1 ou a N2 derruba não ganha chave.

**Cada medida** passa pelo `tools/pre_run.py --medicao`, com o comando, as sementes e o tempo estimado no PR. O H10 já reconhece o
`scripts/equilibrio_poc/`, e os scripts novos ficam nessa pasta para continuar no gate.

## 4. As chaves e o gabarito

**As chaves** entram na `EntradaLuta` (`motor/arena/luta.ts`), como o `tiro`, a `esquiva` e o `apoio`. Sem elas, a luta não muda. Os nomes e
os números são PROPOSTOS, SEM FONTE, e só entram as que a N2 confirmar:

| chave | o que faz | a hipótese |
|---|---|---|
| `forcaAtr` | o `forca` do atributo na entrada (hoje fixo no `OPCOES_PADRAO`); a N4 mede 1,0, 1,15 e 1,25 | H-ATR |
| `tiroDoMorto` | o projétil de quem caiu some (ou não causa dano) | H-TIRO-MORTO |
| `puloMax` | um teto para o pulo da esquiva, em px | H-PULO |
| `bordaRingue` | o recuo e o pulo olham para a borda do Ringue | H-RINGUE |
| `ordemAlterna` | o lado que anda primeiro alterna a cada passo | H-ORDEM |

**As chaves de mapa** (as rochas da Praia, os pilares do Castelo) mudam `cenas.ts`, que é o núcleo da POC pela seção 3.2 do plano da LP5.
Elas só entram se a N2 as confirmar, com a mesma regra.

**O gabarito**, gravado num commit próprio antes da primeira chave e conferido por um teste:
- **as tabelas de luta que existem:** a `LUTA_V21` (a v21 e a v22), a `LUTA_V23` (a v23 à v28 e a v32) e a `LUTA_V29` (a v29). A v30 e a v31
  do PR #872 entram se estiverem na `main` quando a N3 começar;
- **as lutas:** as 384 do `test/arena_lp6_gabarito.test.ts` (a v21 e a v23), mais as mesmas na tabela da v29, nos 8 mapas;
- **as vidas:** os gabaritos que já existem (`lp2_vidas_v21`, `lp2b_torneios_v21` e os da `test/lp6_4_gabaritos.test.ts`, da v24 à v28),
  mais uma vida da v29 e uma da v32 que lutam no Ultimate e no Mega, como a `test/lp6_4_luta_alta.ts`;
- **a fidelidade da LP1** (480 de 480 lutas iguais ao harness), que continua valendo sem as chaves.

Com todas as chaves desligadas, os gabaritos saem byte a byte. Um teste confere cada chave ligada no replay bit a bit.

## 5. As questões abertas

1. **A leitura da seção 1.2 (a) é preliminar.** Ela foi feita fora do repositório, sem artefato. Se a N1 não a reproduzir, as hipóteses H-ATR
   saem, e o plano volta ao Matheus antes da N2.
2. **O que é "neutro" no atributo.** O `Free` e o `None` não entram no triângulo. Se a tabela das formas trocar atributos, o piso dos NPCs
   muda junto. A investigação não escolhe isso.
3. **A Fábrica é do Tamer** e luta com os números da v21 (D-LP5-5-5). A investigação a mede, mas mudar a Fábrica é decisão de outra frente.
4. **A régua das séries.** Se a N1 mostrar que o G3, o G1 ou o critério dos NPCs não cabem em nenhuma luta, a régua volta ao Matheus. A
   investigação não troca a régua no meio (a D-N-4).
5. **O custo no celular** segue SEM FONTE. As chaves não devem mudar o custo de uma luta, mas a N3 não mede no celular.
6. **O A1 com poucas formas de perto.** No Rookie são 3 de perto contra 5 de longe, e o atributo das 3 pesa no A1 do estágio. A N1 lê o A1
   só nos pares neutros, ao lado do A1 de hoje.

## 6. As decisões do Matheus (todas DECIDIDAS como recomendadas, 2026-11-12: "Aprovo as 7 (Recommended)", o Matheus, repassado pelo Gerente)

| # | a pergunta | a recomendação | o custo de errar |
|---|---|---|---|
| **D-N-1** (a ordem) | a investigação segue as etapas da seção 3: releituras e contas, depois lutas fixas, depois chaves, depois contrafactuais, sem grade antes da N4? | **sim.** A N1 e a N2 custam minutos e dizem quais chaves valem o código | começar pelas chaves gasta código e gabarito em hipóteses que uma leitura derrubaria; pular a N4 deixa a calibração geral sem saber o que cada causa move |
| **D-N-2** (as sementes) | reservar a `92101…92505` para as lutas fixas (N2) e os contrafactuais (N4), pedida ao Gerente, num commit próprio da N2? | **sim.** As bases 92101, 92202, 92303, 92404 e 92505, com a derivação da LP5 | usar a 86xxx gasta a calibração geral, que precisa dela limpa; a 87xxx é a conferência, que roda uma vez |
| **D-N-3** (o atributo) | o tamanho do efeito do atributo (o `forca` 1,5 e o triângulo) é do núcleo, e a distribuição dos atributos pelas formas é da tabela das formas? | **sim.** A investigação mede o `forca` na N4 (1,0, 1,15 e 1,25) e entrega a distribuição para a tabela, sem mudar nenhum atributo | medir só a tabela deixa a razão 2,25 decidindo as lutas, qualquer que seja a tabela; mudar os atributos nesta tarefa mexe nos dados do jogo (a LP-2) sem a tarefa dela |
| **D-N-4** (a régua) | a investigação calcula o teto aritmético do G1, do G3 e do critério dos NPCs, mas não troca a régua no meio? | **sim.** A régua volta ao Matheus depois da N5, com as causas | trocar a régua antes de saber a causa esconde o problema; nunca a rever deixa metas que nenhuma luta cumpre |
| **D-N-5** (as chaves) | as chaves da N3 são só as que a N2 confirmar, com a lista levada ao Matheus antes do código? | **sim.** Uma decisão curta no fim da N2, com os números | código para uma hipótese falsa custa o gabarito e a revisão; código sem a decisão quebra a regra da D-LP5-5 (o núcleo só muda por decisão) |

**A lista da D-N-5, DECIDIDA (2026-11-12):** depois da N2 (PR #888), o Matheus escolheu as 4 chaves recomendadas: "As 4 (Recommended)" (repassado pelo Gerente). Entram na N3, todas desligadas no jogo: a `forcaAtr`, a `tiroDoMorto`, a `puloMax` e a `bordaRingue`. Ficam fora a `ordemAlterna` e as chaves de mapa da Praia e do Castelo. Os números delas seguem PROPOSTOS, SEM FONTE.
| **D-N-6** (os PRs) | três PRs: este plano; a N1 com a N2; a N3; e a N4 com a N5 num quarto? | **sim.** O worker para depois de cada um | um PR por etapa dá 5 esperas de merge para uma investigação curta; um PR só esconde a N2, onde as hipóteses caem ou ficam |
| **D-N-7** (nada no jogo) | nenhuma chave liga numa versão de pet nesta investigação? | **sim.** As chaves ficam desligadas no jogo. Ligar é da calibração geral, com uma versão nova | ligar uma causa sozinha muda as metas que passam (as 10 da v23), sem a rodada de equilíbrio que a regra "equilíbrio só no fim" pede |

## 7. A entrega

| etapa | o PR |
|---|---|
| **N0** | este plano, a seção no `docs/registro/2026-11.md` e a nota na `docs/TAREFA_V3_LUTA_POC.md` |
| **N1 e N2** | o commit da faixa, os dois scripts, os artefatos e uma seção "Resultado da N1 e da N2" na `docs/TAREFA_V3_LUTA_POC.md`, com a lista da D-N-5 |
| **N3** | o commit do gabarito, as chaves desligadas e os testes |
| **N4 e N5** | os contrafactuais, o relatório e o que vai para a tabela das formas e para a calibração geral |

Os desvios vão na seção da etapa no `docs/registro/AAAA-MM.md`, com o índice regenerado por `python tools/gerar_indice_desvios.py`. **O merge
é só do Matheus.**

## 8. A N4: os contrafactuais (registrado antes de qualquer luta, 2026-11-12)

A N4 está aprovada pela D-N-1. As chaves são as da D-N-5 ("As 4 (Recommended)"), na N3 (PR #893). Esta seção foi commitada antes da
primeira medida. **Nada aqui escolhe um número:** a N4 mede o que cada causa move e o que ela quebra, e a calibração geral vem depois. Os
números são PROPOSTOS, SEM FONTE.

### 8.1 As medidas

Cada medida é a medida inteira da bancada: os 11 grupos e as 21 metas, com o `medir_tudo` em 4 processos. Elas rodam uma por vez, cada uma
liberada pelo `tools/pre_run.py --medicao`.

| # | a fase | o candidato | o que muda sobre a base |
|---|---|---|---|
| 1 | `n4_base_v23` | `lp5_3` (a luta da v23) | nada: a base da v23 nestas sementes |
| 2 | `n4_atr100` | `n4_atr100` | `forcaAtr` 1,0 (o triângulo sem efeito) |
| 3 | `n4_atr115` | `n4_atr115` | `forcaAtr` 1,15 |
| 4 | `n4_atr125` | `n4_atr125` | `forcaAtr` 1,25 |
| 5 | `n4_morto` | `n4_morto` | `tiroDoMorto` |
| 6 | `n4_pulo` | `n4_pulo` | `puloMax` 75 px (perto do pulo neutro, 380 px/s × 192 ms ≈ 73 px) |
| 7 | `n4_borda` | `n4_borda` | `bordaRingue` 0,9 (o medo da borda começa em 0,8, e a queda é acima de 1,02) |
| 8 | `n4_juntas_v23` | `n4_juntas_v23` | as 4 juntas: `forcaAtr` 1,15, `tiroDoMorto`, `puloMax` 75, `bordaRingue` 0,9 |
| 9 | `n4_base_v29` | `lp6_3_u120` (a luta da v29) | nada: a base da v29 |
| 10 | `n4_juntas_v29` | `n4_juntas_v29` | as 4 juntas sobre a v29 |

**As sementes:** a faixa `investigacao`, `92101…92505` (D-N-2), com as bases 92101, 92202, 92303, 92404 e 92505 e a derivação da LP5
(`hashSemente("equilibrio-poc-pet", base, i)` e `hashSemente("equilibrio-poc", base, k)`). Os tamanhos são os de sempre da bancada (o `TAM`
de `bancada.ts`). As lutas fixas da N2 usaram a mesma faixa com outros índices de luta. As duas medidas são descritivas e não escolhem
números, então a repetição de uma semente com outros lutadores não mistura nada.

**A vida (P5)** leva as chaves pela vida do Motor (o `nucleoLutaPoc`), que só a bancada põe. O jogo fica sem elas (D-N-7).

**O comando**, em `web/app`, uma medida por vez:
`node scripts/equilibrio_poc/medir_tudo.ts --faixa investigacao --fase <a fase> --candidato <o candidato> --processos 4`.
Os artefatos vão em `web/app/scripts/medicoes/equilibrio_poc/<a fase>/investigacao/`, com o `resumo.json` e o `resumo.md`.

**O tempo de máquina** (SEM FONTE): a LP5 mediu 1,4 milhão de lutas em 2 134 s de processo, uns 9 a 10 min em 4 processos. São de 1,5 a
2 h nas 10 medidas, em cargas separadas.

### 8.2 Os critérios de leitura (registrados antes)

A comparação é sempre com a base da mesma luta e das mesmas sementes: as medidas 2 a 8 contra a 1, e a 10 contra a 9. Para cada meta e
cada medida, a N5 traz:
- o valor;
- se passa, pelo critério da seção 2 do `PLANO_EQUILIBRIO_LUTA_POC.md`;
- a diferença para a base.

| leitura | a regra (PROPOSTA, SEM FONTE) |
|---|---|
| **a chave move a meta** | o valor entra na faixa da meta, ou chega 0,05 mais perto dela, no estágio ou no mapa pior |
| **a chave quebra a meta** | a meta passa na base e falha com a chave |
| **a chave não age** | a diferença fica abaixo de 0,02 em todos os estágios |
| **o atributo (a curva)** | o V1, o V2, os 7 NPCs e o P5 nas três medidas 2 a 4, lidos como uma curva do `forcaAtr`. Não se escolhe o valor |
| **as juntas** | se as 4 juntas somam o que cada uma move sozinha, ou se uma desfaz a outra (a medida 8 contra as 2 a 7) |

**A régua não muda** (D-N-4). A N5 traz também o teto aritmético do G1 e do G3 e, para os 7 NPCs, o piso e o teto pelo atributo, com os
números da N1.

**Nada liga no jogo** (D-N-7). A N5 entrega:
- a causa de cada meta;
- o que cada chave move e quebra;
- o que vai para a tabela das formas e para a calibração geral;
- as decisões que sobrarem.
