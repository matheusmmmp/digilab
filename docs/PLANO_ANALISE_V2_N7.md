# Plano de análise — N7: arbitragem entre duas prioridades (a necessidade do pet × o pedido do dono)

Status: **registrado antes de qualquer dado** (2026-10-05). Tarefa `docs/TAREFA_V2_N7_PLANO.md`; nó N7 do `docs/ROADMAP_V2.md` (R6.3);
hipótese H-ACT-03 de `docs/research/digibrain/mechanisms/action_selection.md`; peça "duas prioridades" da seção 5 de `docs/DEFINICOES_V2.md`
(D7). **Só papel:** nenhuma run, nenhum código. Todo número citado aponta o artefato ou a config; os números de desenho sem fonte estão
marcados PROPOSTO; o resto é decisão do Matheus (seção 15).

**Ressalva da peça (D7, literal):** "inspirada no Dwarf Fortress; o análogo citado é inspiração declarada, não validação". O análogo é
o conflito aproximação-evitação (Elliot 2006, `10.1007/s11031-006-9028-7`, VERIFICADA por título e metadados). **A regra de arbitragem é
do projeto.**

**A pergunta.** Quando a necessidade do pet e o pedido do dono apontam para lados diferentes, quem decide? E isso deixa no pet uma marca que
se separa do cuidado?

**O que sustenta, e o que não sustenta:**
- **Camadas fixas.** Controle em camadas de competência, em que uma camada assume quando a sua condição vale, é desenho publicado:
  subsunção, em Brooks 1986 (`10.1109/jra.1986.1087032`, VERIFICADA). O instinto do Digilab já arbitra assim: as regras de sono e de
  necessidade urgente vêm antes do tempo livre (`PoliticaInstinto.agir`, `digilab/policy.py`).
- **Pistas, sem evidência:** a subsunção dinâmica favorecendo a urgência numa tarefa estreita (Fróes e Gudwin 2017) e drives × impulsos
  (Rossi et al. 2024). As duas são do corpus do DigiBrain, sem verificação no projeto.
- **Hipótese do Digilab:** nada na literatura verificada diz como este pet vai arbitrar.
- **Nenhuma alegação de novidade.**

---

## 1. Pré-requisitos (nada roda antes de estarem na `main`)

| # | o quê | quem | estado em 2026-10-05 |
|---|---|---|---|
| R1 | a decisão de comer vê qual fruta está no cenário (R2 da revisão do aprendiz) | chats A e B, `docs/TAREFA_V2_FRUTA_NO_CENARIO.md` | rodada 7 |
| R2 | o ponto T3 (teto 16·S) e as faixas reservadas na bancada | chat D, `docs/TAREFA_V2_BANCADA_EXPERIMENTO.md` | rodada 7 |
| R3 | o mundo `iguais_frutas` na bancada (seção 4.3; decisão N7-5) | chat D | depois deste plano |
| R4 | o lado do mundo do pedido (seção 2): evento, janela, `DonoPedinte` e a bronca da desobediência | chat A | depois deste plano |
| R5 | a entrada `pedido` nos lobos (seção 3) e o fator `pedido` no motivo | chats B e A | depois deste plano |

---

## 2. O que é "pedido do dono" no mundo das frutas

**O pedido é "deixe a fruta X"**: o dono não quer que o pet coma a fruta X (decisão N7-1).

| peça | proposta (os nomes se combinam com o chat A) |
|---|---|
| evento | `AcaoUsuario.PEDIR_DEIXAR_FRUTA_<A\|B\|C>` no fim do enum (`ACOES_PEDIDO`); `AcaoPet` não muda (V5) |
| percepção | `Observacao.pedido_frutas`: −1 na fruta com pedido vigente, 0 nas outras, na ordem de `FRUTAS`; o motor injeta antes de cada decisão |
| janela | `ConfigPedido.janela_min` 240 (PROPOSTO, a mesma da informação do N5); pedir de novo renova |
| chave | `ConfigPedido.ligada` False; desligada, nada muda, e um pedido no log levanta erro |
| quem pede | `DonoPedinte`: logo depois de cada oferta que tem X, pede "deixe X". A fruta X é sorteada uma vez por vida por `derivar_semente("pedido-fruta", semente)` e não depende da preferência inata (decisão N7-6) |
| fase | pedidos só nos dias 1–10; nos dias 11–14 não há pedido, e esta é a fase de **extinção** (decisão N7-7) |

**O pedido não é cuidado nem reforço.** Ele não mexe no estado, não conta como contato e não passa por `receber_acao_dono`. Fica fora do
orçamento, pelo canal das ofertas (B2), e sai nos mesmos ticks em todos os braços da unidade, porque o calendário das ofertas
(`CalendarioFrutas`) não depende do braço.

**Por que o pedido, e não a informação do N5.** As duas coisas diferem em três pontos:

| | informação do N5 | pedido do N7 |
|---|---|---|
| o que é | uma afirmação sobre o mundo ("faz mal"), que o mundo confirma ou refuta | a vontade do dono, sem valor de verdade |
| onde entra | só na escolha de qual fruta comer (N5-2) | na decisão de comer ou não, onde a necessidade compete |
| quem mexe no peso | só a consequência | depende do braço: ninguém, a consequência ou o dono |

**Por que "deixe X" e não "coma X".**
- "Coma X" com fome aponta para o mesmo lado da necessidade: não há conflito.
- "Coma X" sem fome compete com o tempo livre, não com uma necessidade.
- "Deixe X" com X sozinha no cenário e o pet com fome é o conflito da peça: a necessidade diz comer, o pedido diz não.

---

## 3. Onde a arbitragem mora nos lobos (sem mexer no `engine.py`)

**As duas prioridades:**
- **A necessidade** vem pelo lobo de impulsos, isto é, as regras do instinto na ordem de hoje: sono, necessidade urgente (`fome < 0,25` ou
  `higiene < 0,25`, quando o pet chama o dono), abandono, fome moderada (`fome < 0,45`: comer ou chamar) e tempo livre, que inclui
  `fruta_no_cenario`.
- **O pedido** entra pela percepção, como a entrada `pedido`, e pesa no lobo de decisão.

**Onde a arbitragem acontece:** só nas regras em que `comer` é candidato e a necessidade não é urgente, isto é, `fome_moderada` e
`fruta_no_cenario`.
- **Decisão de comer:** o peso efetivo de `comer` ganha o termo `(w_pedido / S) × p`.
  - p = −1 quando **todas** as frutas no cenário têm pedido vigente. Com uma fruta só, é a própria X.
  - p = 0 nos outros casos.
  - Nas ofertas com outra fruta, o pet pode comer a outra e o conflito com a fome não existe.
- **Escolha da fruta:** nas ofertas com duas frutas ou mais, o mesmo `w_pedido` pesa contra X. A forma é a da informação do N5: um termo
  `(w_pedido / S) × pedido_f`, com o piso de hoje.
- **Um peso compartilhado** `w_pedido`, com a confiança de partida `w0_pedido` > 0, calibrada (seção 9), e o teto do ponto T3.
- **`w0_pedido` = 0 desliga a entrada**, e a vida volta a ser a de antes, byte a byte (G2).

**A necessidade forte toma a frente por construção** (decisão N7-3). As regras urgentes vêm antes e não leem a entrada `pedido`:
- na fome urgente, o pet chama o dono e `comer` nem é candidato;
- no sono, dorme.

Nenhuma curva de urgência nova entra: a fronteira entre "o pedido pode pesar" e "a necessidade manda" é a fronteira das regras do instinto
que já existem (`fome` 0,25 e 0,45). Isso é subsunção em camadas fixas (Brooks 1986). A alternativa graduada fica fora deste nó.

**Quem mexe em `w_pedido`** depende do braço (seção 4): ninguém no P0; a consequência no P1, pela regra da L1 no peso compartilhado,
como `atualizar_info` no N5; o dono no P3. **O pedido em si nunca é reforço.**

**Motivo:** o fator `pedido` só vira fator quando, com o mesmo `u` e sem o termo do pedido, a ação seria outra. É a regra de honestidade
de sempre e a base da medida "quem decidiu" (seção 6).

---

## 4. Braços e controles

### 4.1 Braços

Todos com o dono **atencioso**, o dono de cuidado. Todos com as ofertas do `CalendarioFrutas` e no ponto T3.

| braço | pedido | quem mexe em `w_pedido` e nos pesos das frutas | o que responde |
|---|---|---|---|
| **P0** | nenhum | ninguém | a referência herdada |
| **P0+ped** | sim | ninguém | quem decide pela predisposição (`w0_pedido`) contra a necessidade |
| **P1+ped** | sim | a consequência (P1 com a E2) | a necessidade aprendida corrói a deferência ao pedido? |
| **P3+ped** | sim, com bronca na desobediência | o dono | o dono ensina a deixar X, e isso fica depois que os pedidos param? |
| **P3** | nenhum | o dono (o feedback de sempre do atencioso) | o ensino de sempre, sem o pedido |

**A bronca da desobediência** (só no P3+ped; decisão N7-8):
- **Quando:** o pet come X com pedido vigente. O `DonoPedinte` dá `repreender` no primeiro passo do dono depois do consumo.
- **Orçamento:** a bronca sai **fora do orçamento**, pelo canal do mundo, para o cuidado e o feedback de sempre do atencioso serem os
  mesmos do P3.
- **O crédito** segue a janela da v1: a bronca credita a última decisão. Se outra decisão cair entre o consumo e a bronca, a bronca cai
  nela; a fração creditada ao consumo é medida (risco 3).

### 4.2 O "só cuidado" acoplado (D4)

**`P0<P3+ped:sem_ensino`:** o registro do P3+ped, sem os pedidos, sem as broncas e sem os sinais do dono, rejogado com o cérebro do P0.
Fica com o mesmo cuidado, as mesmas ofertas e o mesmo genoma, sem nenhum ensino.
- **Pré-requisito:** o filtro `sem_ensino` da bancada passa a tirar também os pedidos (R4).
- **`P0<P0+ped:sem_pedido`:** o controle do P0+ped. Ele é o P0 no registro do P0+ped, e o G2 do acoplado confere que sai igual ao P0.

### 4.3 Mundo (decisão N7-5)

**O mundo `iguais_frutas`:** as três frutas com o mesmo efeito, neutro no humor e a mesma nutrição. É a variante "iguais" do N4
(`ConfigFrutas.mundo`), levada à bancada (R3).

**Por que esse mundo:**
- obedecer ou desobedecer não tem consequência própria da fruta, só a da fome;
- o conflito fica só entre a necessidade e o pedido;
- no `descasado`, comer X seria punido ou premiado pelo humor conforme X fosse a ruim ou a boa, e a erosão do P1 misturaria a necessidade
  com a verdade da fruta.

**Os mundos `casado_frutas` e `descasado`** ficam como descritivo opcional.

---

## 5. As predições (registradas antes)

- **P-N7-1 (quem decide, pela predisposição):** no P0+ped, nas decisões de conflito o pedido decide uma parte; nas regras urgentes,
  nunca.
- **P-N7-2 (a necessidade corrói):** no P1+ped, a fração de conflitos decididos pelo pedido cai da janela inicial (dias 1–5) para a final
  (dias 6–10) e fica abaixo da do P0+ped na final. O motivo: comer reduz o déficit de fome e o sinal empurra `w_pedido` para zero.
- **P-N7-3 (a marca do ensino, separável do cuidado):** na extinção (dias 11–14, sem pedido), o P3+ped come X numa fração menor dos
  consumos de fruta que o acoplado só cuidado.
- **P-N7-4 (a marca é do pedido, não do ensino de sempre):** na extinção, o P3+ped come X numa fração menor que o P3 sem pedido.
- **P-N7-5 (fora do cuidado):** obedecer não muda saúde, privação nem mortes. A fome urgente passa por cima e o atencioso alimenta.

---

## 6. Medidas

| medida | o que é |
|---|---|
| **decisão de conflito** | decisão nas regras `fome_moderada` ou `fruta_no_cenario` com p = −1 (toda fruta no cenário com pedido vigente) |
| **quem decidiu** (por decisão de conflito) | **o pedido**, quando o pet não comeu e, com o mesmo `u` e o termo do pedido zerado, teria comido; **a necessidade ou o gosto**, quando comeu; **ninguém**, quando não comeria de qualquer jeito. A sonda só lê (G1) |
| **deferência** | fração das decisões de conflito decididas pelo pedido, por zona (`fome_moderada` e `fruta_no_cenario`) e por janela (dias 1–5 e 6–10) |
| **fração de X** | consumos de X / consumos de fruta, nas ofertas com X e outra fruta, por janela (1–5, 6–10, extinção 11–14); unidade sem consumo na janela fica fora do contraste (número reportado) |
| `w_pedido` | trajetória diária e o dia em que cruza o zero (P1+ped) |
| saúde média, tempo fora de privação, mortes, humor | G5 (`desempenho_no_ambiente`) |
| exposição | número de decisões de conflito e de ofertas com X por vida |

**Por que a marca se mede na extinção.** Com a janela de 240 min e a fruta ficando 120 min no cenário (`ConfigFrutas.duracao_min`), X
nunca está no cenário sem pedido vigente nos dias 1–10. A marca só aparece quando os pedidos param.

---

## 7. Gates (PROPOSTOS)

Contrastes **pareados por unidade**.

**Δ** = metade da fração de X na extinção do acoplado só cuidado na calibração, isto é, metade da distância entre o pet sem ensino e
nunca comer X. É a regra E4 do experimento maior.

| gate | medida e contraste | passa se |
|---|---|---|
| **G1** | replay de toda vida, braço e acoplado | bit a bit |
| **G2** | `w0_pedido` = 0 com pedidos no log = a vida sem pedidos; a chave desligada = a vida de antes; o acoplado do P0+ped = o P0 | byte a byte |
| **G-URG** | no P0+ped, P1+ped e P3+ped, nenhuma decisão das regras urgentes (sono, `pedido_necessidade`, abandono) é decidida pelo pedido | 100%, verificação exata |
| **G-ARB** (verificação da manipulação, fora da família) | deferência do P0+ped nas decisões de conflito, dias 1–10 | limite inferior do IC 95% > 0 |
| **G-EROSAO** | deferência final (dias 6–10): P0+ped − P1+ped | positivo pelo teste da seção 10 |
| **G-MARCA** | fração de X na extinção: `P0<P3+ped:sem_ensino` − P3+ped | positivo pelo teste da seção 10 |
| **G-MARCA-E** | fração de X na extinção: P3 − P3+ped | positivo pelo teste da seção 10 |
| **G5** | P0+ped − P0 e P3+ped − `P0<P3+ped:sem_ensino`, em saúde média e tempo fora de privação; mortes | IC 95% contém 0 nos dois, e mortes iguais |

**Família de Holm:** {G-EROSAO, G-MARCA, G-MARCA-E}, α = 0,05.

### 7.1 Leituras (registradas antes)

- **Quem decide** (P-N7-1) é respondido pela deferência por zona e janela, com G-URG e G-ARB. Na forma descritiva: "nas decisões de
  conflito, o pedido decide x% no tempo livre e y% na fome moderada; na fome urgente, 0% por construção".
- **G-ARB falha:** o pedido nunca decide nada. Os gates de erosão não se leem (não há deferência a corroer). A marca se lê sozinha.
- **G-MARCA passa e G-MARCA-E passa:** o pedido, com a bronca, deixa uma marca que dura sem o pedido, acima do cuidado e acima do ensino de
  sempre.
- **G-MARCA passa e G-MARCA-E falha:** a marca existe, mas o P3 sem pedido chega a ela também. Ela é do feedback do atencioso, não do
  pedido.
- **G-MARCA refuta** (IC 90% de acoplado − P3+ped inteiro em (−Δ, +Δ)) com exposição suficiente: o pedido decide enquanto vale e não deixa
  marca.
- **G5 falha:** a arbitragem virou canal de cuidado (obedecer custou ao corpo). Isso é resultado registrado; os outros gates se leem com
  essa nota.
- **Exposição insuficiente** (seção 13): inconclusivo por exposição.

**Descritivos:**
- P3+ped − P3 na deferência;
- a trajetória de `w_pedido`;
- a fração de X por posição de X na preferência inata (a 1ª, 2ª ou 3ª);
- os mundos `casado_frutas` e `descasado`, se o Matheus quiser.

---

## 8. Ligação com o resto da V2

- **N5:** a informação continua só na escolha da fruta (N5-2). O N7 não a leva para a decisão de comer. Fazer isso é uma alternativa
  registrada (decisão N7-1), não deste plano.
- **N6:** a memória de episódios não entra nos braços do N7. Os dois nós medem coisas diferentes no mesmo lobo de decisão e não se
  misturam.
- **Produto:** o comando pelo chat da web (catálogo fechado) é o "pedido" do jogo. O N7 só testa a arbitragem na simulação e não muda a
  web.

---

## 9. Calibração (21101, 21202, 21303, 21404, 21505)

**Só `w0_pedido`** é calibrado.
- **Grade (PROPOSTA):** `w0_pedido` ∈ {S/4, S/2, 3S/4}, todos abaixo do teto. 0 roda como referência descritiva.
- **O resto fica fixo:** o ponto T3, o ganho 4 do P1, a E2, a janela de 240 min, a fase de pedido de 10 dias, o mundo `iguais_frutas`, o
  atencioso e a `ConfigFrutas` que estiver na `main`.
- **Regra de escolha (registrada agora):** o **menor** `w0_pedido` em que G-ARB passa **também na zona `fome_moderada`**. O pedido tem de
  pesar onde a necessidade compete, não só no tempo livre.
- **Se nenhum passa:** o de maior limite inferior da deferência na `fome_moderada`, e o relatório diz que a calibração não fechou.
- **O que não entra na escolha:** G-EROSAO, G-MARCA, G-MARCA-E e G5.
- **Δ** sai da calibração.

---

## 10. Estatística

- **Unidade:** a vida de um par (genoma, semente). Os braços e acoplados de uma unidade são pareados. As unidades de uma mesma base ficam
  juntas no bootstrap.
- **"Positivo pelo teste":** p unilateral na direção predita, pelo bootstrap sobre unidades (`metrics.bootstrap_ic`, parâmetros do
  `PROTOCOLO_ARENA_V1`), abaixo do limiar de Holm sobre a família, α = 0,05.
- **G-ARB** usa o IC 95% bootstrap da fração. **G5** usa o IC 95% bilateral, com as mortes. **Equivalência:** IC 90% dentro de (−Δ, +Δ).
- Tudo fora da família é descritivo.

---

## 11. Validação (22101, 22202, 22303, 22404, 22505), uma vez

- Com o `w0_pedido`, o Δ e o N do adendo (seção 12) commitados neste arquivo antes da run.
- Análise única. Refeita do zero com sementes novas registradas antes, só por erro de execução (G1, G2 e G-URG incluídos), nunca pelo
  resultado.
- Falha registrada não para a V2 (decisão de 2026-10-01).

---

## 12. Sementes, unidades e tamanho da amostra

### 12.1 Faixas propostas (o coordenador fecha)

| o quê | faixa | bases |
|---|---|---|
| N7, calibração | **21101…21505** | 21101, 21202, 21303, 21404, 21505 |
| N7, validação | **22101…22505** | 22101, 22202, 22303, 22404, 22505 |

**Por que estas faixas.** Elas ficam fora de:
- `FAIXAS_RESERVADAS` (`experiments/bancada_v2.py`: 101…15505, 50001…50020, 60001…60160, 69001, 80001…82004, 20260900…20261800);
- o N11 (16101…17505, `docs/ROADMAP_V2.md`);
- a revisão do aprendiz (18101…18505) e o N6 (19101…20505), como a tarefa pede.

**Busca feita** no repositório, fora dos artefatos: nenhuma das 10 bases aparece.

**Ao fechar:** a implementação acrescenta as duas faixas às `FAIXAS_RESERVADAS`. O chat D já atualiza essa lista na rodada 7.

### 12.2 Unidades e N

- **Unidades derivadas** pela regra E3: semente `derivar_semente("n7", b, k)` e genoma `derivar_semente("n7-genoma", b, k)`. O mesmo K
  em todas as bases, e o teste de colisão da bancada.
- **K da calibração (PROPOSTO):** 4 por base (20 unidades), como a revisão do aprendiz, só para estimar a variância.
- **K da validação:** N = ((z₁₋α + z₀,₈) × σ_d / Δ)² por contraste da família, com α/3 (o passo mais exigente de Holm) e poder 0,8. Vale o
  maior N, arredondado ao múltiplo de 5 e conferido por simulação com as unidades da calibração. Entra no adendo.
- **Por quê:** na v1 a variância entre unidades dominou (ICC 0,745; 0,34% vinda das partidas; `artifacts_poder/variancia.json`).

---

## 13. Riscos registrados antes

1. **Poucas decisões de conflito.**
   - **A conta pela config** (`config._rotacao_ofertas`, `ConfigFrutas.horarios_oferta`):
     - X sozinha é 1 dos 7 conjuntos da rotação, e X aparece em 4 dos 7;
     - com 4 ofertas por dia e 10 dias de pedido, são cerca de 40 ofertas: X sozinha em cerca de 6 e X com outra fruta em cerca de 17;
     - cada oferta fica 120 min no cenário, cerca de 8 decisões.
   - **O que isso dá:** conflitos com a fome vêm só de X sozinha, algumas dezenas de decisões por vida, das quais poucas na
     `fome_moderada`. O p(comer | fruta no cenário) da validação do N4 foi 0,208 (`artifacts_v2_n4/validacao/resultado.json`,
     `resumo.p_comer`).
   - **A regra:** com mediana de decisões de conflito na `fome_moderada` abaixo de 5 por vida (PROPOSTO), a deferência por zona é
     descritiva. Com mais de metade das unidades sem consumo de fruta na extinção, a marca é **inconclusiva por exposição**.
2. **O teto.** No ponto T3 (16·S) o teto não deve prender `w_pedido`, mas a fração de vidas com `w_pedido` no limite é reportada. G-EROSAO
   refutado com o peso preso é lido como **limitado pelo teto**.
3. **O crédito da bronca.** A janela da v1 credita a última decisão. Se ela não for o consumo, a bronca ensina outra coisa. A fração de
   broncas creditadas ao consumo é reportada. Abaixo de metade, G-MARCA e G-MARCA-E levam essa nota.
4. **A decisão de comer depende de R1.** Sem a decisão de comer ver qual fruta está no cenário, a entrada `pedido` não tem como valer só
   para X. O plano não roda antes de R1.
5. **O atencioso alimenta.** Se o pet obedece e não come, o atencioso pode alimentar: o custo da obediência fica no cuidado do dono, não
   no corpo do pet. É isso que o G5 confere. Também quer dizer que, com um dono relapso, o resultado poderia ser outro (fora deste plano).

---

## 14. Fora deste plano

- código e runs;
- a curva de urgência graduada;
- o pedido "coma X";
- outros pedidos (brincar, descansar);
- a informação do N5 na decisão de comer;
- outros donos;
- o comando pelo chat da web;
- a memória do N6;
- circuitos por classe de estímulo (H-ACT-02).

---

## 15. Decisões que só o Matheus pode tomar

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| N7-1 | o que é o pedido | "deixe a fruta X", evento novo e fora do orçamento, separado da informação do N5 | usar a informação do N5 mistura "o dono quer" com "o mundo é assim", e a consequência validaria o pedido como se fosse verdade |
| N7-2 | onde entra | decisão de comer (`fome_moderada`, `fruta_no_cenario`) e escolha da fruta, com um peso compartilhado | só na escolha da fruta não há conflito com a necessidade; em todas as regras, o pedido passaria por cima da fome urgente |
| N7-3 | como a necessidade forte toma a frente | camadas fixas: as regras urgentes não leem o pedido | uma curva graduada nova é mais um parâmetro a calibrar e pode deixar o pedido matar de fome (G5) |
| N7-4 | confiança de partida | `w0_pedido` > 0, calibrado em {S/4, S/2, 3S/4} pela deferência na fome moderada | com 0, o pedido não decide nada e não há o que corroer nem ensinar |
| N7-5 | mundo | `iguais_frutas` (novo na bancada); casado e descasado só descritivos | no descasado, a consequência da fruta premia ou pune a obediência e a erosão deixa de ser da necessidade |
| N7-6 | qual fruta o dono pede para deixar | sorteada por vida, independente da preferência inata | fixar na preferida mistura o conflito com a necessidade e o conflito com o gosto |
| N7-7 | fases | pedidos nos dias 1–10, extinção nos dias 11–14 | sem extinção, X nunca aparece sem pedido vigente e a marca não se mede |
| N7-8 | a bronca da desobediência | só no P3+ped, fora do orçamento, no primeiro passo do dono depois do consumo | dentro do orçamento, ela tira cuidado ou feedback do P3+ped e o contraste com o P3 deixa de ser só o pedido |
| N7-9 | faixas de sementes | 21101…21505 (calibração) e 22101…22505 (validação) | reusar uma faixa vicia o teste (M7 do roadmap) |
| N7-10 | família de Holm | {G-EROSAO, G-MARCA, G-MARCA-E}; G-ARB e G-URG fora (verificações) | pôr G-ARB na família faz a calibração testar o que a validação testa |
