# Por que as duas GV3 deram negativo: cinco hipóteses, o que os artefatos já mostram e as decisões GVN

Status (2026-11-12): **PROPOSTO**. Só papel: nenhuma run, nenhum código, nenhuma faixa. Não autoriza implementação: as decisões GVN-1 a
GVN-6 (seção 4) são do Matheus. A frente é a `docs/TAREFA_V3_GOSTO_VISUAL.md`.

**Regras deste documento:**
- **os dois resultados ficam como estão.** A GV3 (`docs/RESULTADO_V3_GOSTO_VISUAL.md`) e a GV3b (`docs/RESULTADO_V3_GOSTO_VISUAL_ENJOO.md`)
  são negativos registrados: em nenhuma das duas a parte do genoma, a parte do dono ou a interação aparecem com 36 unidades. Nada aqui
  relê essas frases, muda a regra da 7.2 do plano ou vira "o efeito apareceu";
- **a seção 3 é exploração descritiva, não confirmatória.** As contas foram escolhidas depois de ver os dois resultados, não estavam em
  nenhum plano e não têm correção para comparações múltiplas. Elas servem para escolher a próxima pergunta, não para responder a desta.
  Um IC95 que não contém 0 ali não é "a parte do genoma aparece";
- todos os números novos são **PROPOSTOS**, e todos **SEM FONTE**; nenhuma referência é citada. "Gosto", "agrado" e "enjoo" são nomes de
  mecanismo e de medida. **Nenhuma alegação de novidade.**

## 0. O que as duas runs perguntaram e o que voltou

A pergunta das duas (plano, seção 1): entre duas TVs novas, à mesma distância, com os perfis A = C/5 e B = 4C/5 em todos os canais, quanto
da primeira olhada (a **escolha**) e da fração do tempo em A (o **tempo relativo**) acompanha o agrado inato Δ_I = agrado(A) − agrado(B)
do genoma, e quanto acompanha o programa que o dono pôs.

O que voltou, nas duas: as células ficam entre 0,469 e 0,531 nas duas medidas. Os pontos do Spearman(Δ_I, tempo relativo) são positivos
em todos os donos (0,137 a 0,244 na GV3; 0,042 a 0,309 na GV3b), mas todo IC95 contém 0. A repetibilidade fica perto de 0. A exposição
desloca o agrado do cérebro com o sinal do dono no vazio, e o comportamento não acompanha.

## 1. O mecanismo de hoje, no código (o que as hipóteses usam)

- **A escolha entre unidades** (`digilab/digibrain/arb.py`): sorteio proporcional às ativações, `w = a + mul(g_exp, epsilon)` nas unidades
  com a > 0, com a = clamp(soma dos termos, 0, A_max) e A_max = 4S (`ConfigDigibrainInatos.a_max`).
- **A unidade de olhar** (`digilab/digibrain/impulso.py`, `unidades`): uma por TV à vista, com os termos `inato` (o W0[olhar]: o viés
  −S/4, o tédio e a curiosidade a S/2), `prox` e `nov` (S/4 cada, da linha da classe `tela`), `incentivo` (o da classe `tela`, igual
  para as duas TVs), `habito` (a linha H[olhar], igual para as duas), `persistencia` (por chave), `gosto` e, com o enjoo, `enjoo`.
- **O termo `gosto`** (`digilab/digibrain/adapt.py`, `_gosto_da_decisao`): só na unidade da TV que o pet **olhava na decisão anterior**,
  mul(w_gosto, agrado − S/2), com w_gosto = S. A outra TV tem `gosto` = 0. O termo vai de −S/2 a +S/2.
- **Nada guarda o agrado de uma TV que o pet parou de olhar.** O `_olhando` é só o id da última decisão. Com o enjoo, o cérebro ganhou o
  `enjoo_tv` por TV (D-GV-ENJOO-CER-4), uma memória do enjoo, não do agrado.
- **O que o cérebro aprende da TV é da classe, não da TV:** o P1 (`plast.consequencia_olhar`) e o incentivo são da classe `tela`, e o
  hábito é da linha `olhar`. O canal `gosto_visual` no r credita a opção de olhar, mas o que ele move é comum às duas TVs da sonda.
- **A exposição** (`digilab/digibrain/sens.py`, `expor`): o alvo de cada canal anda para o nível visto com τ = 960 ticks, preso em ±S/8 por
  canal (`ConfigOlhar.teto_exposicao`); com o enjoo, o passo satura (D-GV-ENJOO-CER-8).
- **A sonda** (`experiments/sonda_duas_tvs.py`): 240 ticks (16 decisões), as duas TVs a 3 células, ids novos (2 e 3); o termo `gosto`
  começa a janela em 0 nas duas (D-GV-P1e-2). A primeira olhada é sorteio por construção (D-GV-P1e-4).

## 2. As hipóteses

Cada uma tem o mecanismo no código, o que mudaria se ela fosse a causa e uma medida que a separa das outras. As cinco não se excluem.

### H1. Sem memória do agrado por TV, a escolha não lê o gosto

- **O mecanismo:** o `gosto` só existe na unidade da TV olhada na decisão anterior (seção 1). Quando o pet sai da TV (para comer, andar ou
  ficar ocioso) e volta, a nova olhada é de novo um sorteio entre duas unidades iguais em tudo menos a `persistencia`. Cada "volta" à
  sonda dilui o tempo relativo para 0,5. A escolha (a primeira olhada) não pode ler o agrado nunca (D-GV-P1e-4, GVP-1).
- **O que mudaria:** com uma memória do agrado por TV (por exemplo `agrado_tv`, id → [0, S], que cai devagar como o `enjoo_tv`), a unidade
  de olhar de uma TV já vista ganharia o `gosto` mesmo sem o pet a olhar agora. A escolha continuaria sorteio na primeira olhada da janela
  (as TVs são novas), mas as voltas passariam a ler o gosto, e o tempo relativo deixaria de ser diluído.
- **A medida que a separa:** o tempo relativo **condicionado às réplicas em que o pet viu as duas TVs**, contra Δ_I. Se H1 vale, o
  gosto aparece mais forte ali (o pet compara as duas) e quase some nas réplicas de uma TV só (que repetem a escolha). As outras hipóteses
  não preveem essa diferença: H4 prevê ruído igual nas duas; H5 prevê um efeito fraco nas duas. Já dá para ver nos artefatos (seção 3,
  E2 e E4).

### H2. Os perfis da sonda fora da faixa real: o estresse de B e o salto de volume

- **O mecanismo:** B = 4C/5 passa do `estresse_corte` (0,75 C) no volume e no movimento, e o salto de A para B (mais que C/2) dá susto
  (D-GV-ENJOO-PY-2, efeitos 2 e 3; na GV3b só o estresse e o salto real ficam, D-GV-ENJOO-CER-6 e 7). As mídias reais ficam no volume até
  perto de 0,4 C e no movimento até perto de 0,73 C (D-GV-VIDEO-12): o perfil B não tem par no conteúdo real. Esses efeitos valem para todo
  pet, inclusive o vazio, e podem empurrar o tempo relativo para longe de B por um caminho que não é o gosto.
- **O que mudaria:** com os dois perfis abaixo dos cortes, a sonda perderia esse empurrão comum. Se H2 fosse a causa principal, o vazio
  mostraria o desvio (o tempo relativo do vazio acima de 0,5, o pet longe de B), e o próprio teria o efeito do genoma somado a um desvio
  comum, com mais variância.
- **A medida que a separa:** o tempo relativo e a escolha **do vazio**, os três donos juntos (Δ_I = 0: todo desvio de 0,5 é da sonda ou da
  exposição). Já dá para ver (seção 3, E5). A GVP-3 tem um preço aqui: nenhum par simétrico em volta de C/2 cabe abaixo de 0,4 C no
  volume (adendo 1, seção 3); um par dentro da faixa real exige um par assimétrico e um controle novo (GVN-3).

### H3. O gosto aprendido é fraco: a exposição move o agrado, mas o comportamento não segue

- **O mecanismo:** o teto da exposição é S/8 por canal (`teto_exposicao`), e o pet olha pouco a TV da vida (a fração das decisões
  acordadas olhando fica entre 0,043 e 0,061 na GV3 e entre 0,024 e 0,026 na GV3b). Com o enjoo, a exposição ainda satura. O
  deslocamento de Δ_agora que o dono produz é pequeno perto da variação de Δ_I entre os genomas, e o comportamento depende do agrado de
  agora pelo mesmo termo `gosto` que já mal mostra o genoma.
- **O que mudaria:** com um teto maior ou mais exposição, o deslocamento cresceria. Mas, se H1 e H4 valem, ele cairia no mesmo canal
  diluído e continuaria sem aparecer. Por isso H3 é uma hipótese da **parte do dono**, condicionada às outras: ela só pode ser lida
  depois que a parte do genoma aparecer.
- **A medida que a separa:** a razão entre o tamanho do deslocamento (|Δ_agora − Δ_I|) e o desvio-padrão de Δ_I, e o Spearman entre
  Δ_agora e o tempo relativo **no vazio** (onde só a exposição move o agrado). Já dá para ver (seção 3, E6).

### H4. As olhadas raras e curtas: a sonda mede pouco

- **O mecanismo:** a janela tem 16 decisões, e o pet olha algumas delas. Cada pet tem cerca de 20 réplicas válidas, e o tempo relativo de
  uma réplica é quase binário quando o pet vê uma TV só. A média por pet fica com um erro-padrão perto do desvio entre os pets: a
  variação entre os pets é quase toda sorteio. A repetibilidade perto de 0 (as duas runs, seção 2.4 e 3.3) é coerente com isso.
- **O que mudaria:** mais decisões olhando por réplica (uma janela maior, o pet mais perto, mais réplicas por dia) ou mais unidades
  baixariam o erro. Se H4 é a causa, o efeito por réplica existe e só falta precisão; o ponto do Spearman ficaria parecido, e o IC95
  estreitaria.
- **A medida que a separa:** a fração da variância entre os pets que sobra depois de tirar o erro-padrão médio ao quadrado (uma
  confiabilidade das médias por pet), e quantas decisões olhando cabem numa réplica. Já dá para ver (seção 3, E1 e E3).

### H5. O termo `gosto` é fraco diante dos drives

- **O mecanismo:** o `gosto` vai de −S/2 a +S/2. As outras unidades (comer, beber, explorar, dormir, o ocioso) concorrem no mesmo sorteio
  proporcional, com ativações até A_max = 4S, e a `persistencia` da intenção pode chegar a 4S (`w_pers`). Mesmo quando o `gosto` está
  presente, ele muda pouco a fração do peso total que a TV olhada tem: o pet sai da TV pelos drives com quase a mesma chance nas duas.
- **O que mudaria:** com um `w_gosto` maior (ou o `gosto` também no termo da `persistencia`), a TV de agrado alto seguraria o pet mais
  decisões seguidas. Se H5 é a causa, a diferença entre as duas TVs na chance de ficar mais uma decisão é pequena mesmo dentro das
  réplicas em que o pet viu as duas.
- **A medida que a separa:** a parte do peso da unidade de olhar no total, na decisão logo depois de uma olhada, e quanto o `gosto` muda
  essa parte (os termos e os pesos estão no `motivos` de cada decisão). **Isso não se vê nos `medidas.json` nem nos `analise.json`.** Os
  `vidas.tar.gz` das duas runs gravam as sondas, mas este documento não os abriu (o pedido limitava as contas aos dois JSON). Uma leitura
  das sondas gravadas não roda vida nova, mas é uma análise que ainda não tem plano (GVN-2).

## 3. O que os artefatos já mostram (exploração descritiva, não confirmatória)

**O script:** `artifacts_v3_gosto_visual/porque/descritivo.py` (rode `python artifacts_v3_gosto_visual/porque/descritivo.py .` na raiz),
só sobre `artifacts_v3_gosto_visual/gosto_visual/medidas.json` (GV3) e
`artifacts_v3_gosto_visual/gosto_visual_enjoo2/medidas.json` (GV3b), e o `analise.json` de cada uma só para conferir. Ele não importa
nenhum código do repositório. A saída é o `artifacts_v3_gosto_visual/porque/descritivo.json`, na mesma pasta, e sai igual byte a byte a cada execução; cada número abaixo cita a chave dela. Os IC95
são percentis de 2000 reamostras de **unidades inteiras** (a regra do plano), com a semente 20261112 do script; nenhuma reamostra ficou
indefinida. Os três donos entram juntos nos Spearman (108 pets do próprio, cada genoma três vezes): isso é escolha desta exploração, não do
plano, que lê dono por dono.

| id | o que | GV3 | GV3b | chave do `descritivo.json` | hipótese |
|---|---|---|---|---|---|
| **E1** | decisões olhando alguma TV numa réplica (ticks / 15), média e mediana em 16 | 3,59; 3 | 1,86; 2 | `R1_decisoes_olhando_por_replica` | H4 |
| E1 | fração das réplicas com no máximo 1 decisão olhando (0 ou ≤ 1) | 0,184 | 0,336 | idem, `fracao` | H4 |
| **E2** | fração das réplicas válidas em que o pet viu **uma TV só** (o tempo relativo é 0 ou 1 e repete a escolha) | 0,385 | 0,411 | `R2_uma_tv_so` | H1, H4 |
| **E3** | a confiabilidade da média do tempo relativo por pet, no próprio: (variância entre os pets − erro² médio) / variância entre os pets | 0,065 | 0,075 | `R3_confiabilidade_tr_proprio` | H4 |
| E3 | o mesmo no vazio | 0,252 | 0,246 | `R3_confiabilidade_tr_vazio` | H4 |
| **E4** | Spearman(Δ_I, tempo relativo), próprio, os três donos juntos | 0,230 [0,019; 0,426] | 0,168 [−0,078; 0,392] | `R4_proprio_juntos.spearman_di_tr` | H1, H4 |
| E4 | Spearman(Δ_I, escolha), idem | 0,143 [−0,102; 0,383] | −0,098 [−0,341; 0,171] | `R4_proprio_juntos.spearman_di_escolha` | H1 |
| E4 | Spearman(Δ_I, tempo relativo **só nas réplicas em que viu as duas**), idem; em média 11,6 e 11,5 dessas réplicas por pet | 0,479 [0,247; 0,657] | 0,393 [0,192; 0,566] | `R4_proprio_juntos.spearman_di_tr_so_ambas` | H1 |
| **E5** | o vazio, os três donos juntos: o tempo relativo médio | 0,513 [0,494; 0,533] | 0,509 [0,490; 0,528] | `R5_vazio_juntos.tempo_relativo` | H2 |
| E5 | o vazio: a escolha média | 0,509 [0,476; 0,543] | 0,492 [0,456; 0,530] | `R5_vazio_juntos.escolha` | H2 |
| **E6** | o desvio-padrão de Δ_I no próprio (escala S = 1024) | 251,4 | 268,6 | `R6_exposicao.dp_delta_inato_proprio` | H3 |
| E6 | a média de \|Δ_agora − Δ_I\| no vazio (o tamanho da parte da exposição) | 69,9 | 30,5 | `R6_exposicao.media_abs_exposicao_vazio` | H3 |
| E6 | Spearman(Δ_agora, tempo relativo) no vazio (só a exposição move o Δ_agora) | −0,047 [−0,217; 0,123] | 0,021 [−0,181; 0,230] | `R6_exposicao.spearman_dagora_tr_vazio` | H3 |

**O que isso sugere (leitura descritiva, com as ressalvas abaixo):**
- **H1 tem o apoio mais claro.** Perto de 40 % das réplicas válidas são de uma TV só e repetem a escolha, que é sorteio (E2). Nas
  réplicas em que o pet viu as duas, o ponto do Spearman com Δ_I sobe para 0,48 e 0,39, contra 0,23 e 0,17 com todas (E4). O `gosto`
  parece agir quando o pet compara, e a parte de sorteio dilui.
- **H4 também.** A confiabilidade da média por pet no próprio fica perto de 0,07 (E3): quase toda a variação entre os pets do próprio é do
  tamanho do erro da média. Com 36 unidades por dono, o IC95 de um Spearman fica com cerca de ±0,3 a ±0,35 em volta do ponto (a largura vista nas tabelas dos dois resultados), e os
  pontos do plano (0,04 a 0,31) cabem dentro.
- **H2 não aparece no agregado.** O vazio fica perto de 0,5 nas duas medidas e nas duas runs, com o IC95 contendo 0,5 (E5). O estresse de B
  e o salto não empurram o vazio para longe de B de um jeito que se veja com 108 pets. Isso não diz que eles não somam ruído por réplica.
- **H3 é uma questão de tamanho.** A parte da exposição no agrado do cérebro é perto de 1/4 (GV3) e 1/9 (GV3b) do desvio-padrão de Δ_I
  (E6), e o Δ_agora do vazio não acompanha o tempo relativo (E6). Se o efeito do genoma por pet já mal sai do ruído, um deslocamento
  quatro a nove vezes menor não tem como aparecer neste desenho.
- **H5 fica sem medida aqui** (seção 2, H5).
- **A ordem sugerida:** H1 e H4 primeiro (as duas têm apoio e se somam), H3 depois (ela depende de a parte do genoma aparecer), H2 por
  último (sem sinal no agregado), H5 a medir nos `vidas.tar.gz` antes de mexer no `w_gosto`.

**As ressalvas, todas importantes:**
- **Exploração depois de ver os dados.** As contas e o corte "viu as duas" foram escolhidos agora, depois dos dois resultados, e juntar os
  três donos não estava no plano. Com muitas contas possíveis, um IC95 que não contém 0 aparece pelo acaso com frequência. Nada aqui é
  resultado.
- **O corte "viu as duas" condiciona num comportamento.** Ver as duas TVs depende do que o pet fez na janela, e isso pode depender do
  próprio gosto (o pet que não gosta da primeira sai e vê a outra). Sem efeito do gosto, o corte não criaria uma correlação com Δ_I; com
  efeito, ele muda o que se mede (a comparação entre as duas, não o tempo na janela inteira). O número de E4 não se compara com o do plano.
- **A confiabilidade de E3** usa o erro² das médias por réplica como se as réplicas fossem independentes; as três réplicas de um dia saem
  do mesmo momento da vida, então o erro real pode ser outro. Ela é uma ordem de grandeza, não um ICC.
- **O vazio mais "confiável" que o próprio (E3)** não tem leitura aqui: pode vir da exposição, do lugar do pet ou do sorteio, e não foi
  investigado.

## 4. As decisões abertas (GVN-1 a GVN-6), com a recomendação e o custo de errar

Nenhuma autoriza run. Toda pergunta nova sobre o gosto com um mecanismo novo é um plano novo, commitado antes, com uma faixa nova pedida
ao coordenador, e o mecanismo novo entra atrás de uma chave desligada com o gabarito das vidas de hoje gravado antes (CLAUDE.md).

| id | a decisão | a recomendação | o custo de errar |
|---|---|---|---|
| **GVN-1** | Por onde começar: qual hipótese vira a próxima etapa. | **H1, a memória do agrado por TV**, como mecanismo novo atrás de uma chave desligada (uma etapa de código, sem run), com a medida "viu as duas" escrita antes no plano seguinte. É a única com o mecanismo claro no código e o apoio mais claro na seção 3. | Se H4 for a causa sozinha, a memória não muda nada, e o custo é uma etapa de código e um gabarito novo. Se a memória entrar e a escolha passar a ler o gosto "de graça", a próxima run mede um mecanismo novo, não o de hoje: o resultado tem de dizer isso. |
| **GVN-2** | Ler os `vidas.tar.gz` das duas runs para medir H5 (a parte do peso da TV olhada e quanto o `gosto` a muda) e o número de saídas e voltas por réplica, sem vida nova. | **Sim, com um plano curto commitado antes** (as contas, o que se lê, que nada se relê das frases das duas runs), como leitura descritiva. As sondas já estão no git. | Ler sem plano é a mesma exploração da seção 3, só que maior: mais contas, mais acaso. Não ler deixa a H5 sem medida, e um `w_gosto` maior seria ajustado no escuro. |
| **GVN-3** | Os perfis da sonda (H2): manter A = C/5 e B = 4C/5 ou trocar por um par dentro da faixa real. | **Manter na próxima run**, porque o vazio não mostra o desvio no agregado (E5) e trocar os perfis junto com a memória poria duas mudanças numa run. Um par dentro da faixa real fica para uma run própria, com um controle novo (o par assimétrico tira o Δ_I = 0 do vazio). | Se o estresse e o salto somam ruído por réplica, a próxima run perde precisão; se a troca vier junto com a memória, não se sabe qual das duas fez o efeito. |
| **GVN-4** | O tamanho e a janela da próxima run (H4): mais unidades, mais réplicas ou uma janela maior. | **Fixar no plano seguinte uma conta de precisão** a partir da confiabilidade da seção 3 (PROPOSTO: a ordem de 3 vezes as unidades para um IC95 de ±0,2 no Spearman por dono), e preferir mais unidades a uma janela maior, que muda a sonda (GVP-6). | Uma janela maior mistura a habituação com o gosto (o custo já escrito na GVP-6); mais unidades sobem o custo da run (23,5 e 30,6 s por vida, `custo.json` das duas). A conta usa uma confiabilidade que é exploratória. |
| **GVN-5** | A parte do dono (H3): mudar o teto da exposição (S/8) ou a exposição do dono. | **Não agora.** Só depois de a parte do genoma aparecer numa run com plano; antes disso, a parte do dono não tem como ser lida (E6). | Mexer no teto agora é ajustar um número sem uma medida que o leia; não mexer nunca deixa a pergunta do dono presa ao teto de hoje. |
| **GVN-6** | O `w_gosto` (H5): aumentar o termo ou levá-lo à persistência. | **Não antes da GVN-2.** O número é PROPOSTO, SEM FONTE, e a H5 ainda não tem medida. | Aumentar sem medida pode fazer o pet ficar preso na TV (o risco da GV-21); não aumentar, se a H5 for a causa, deixa a memória da GVN-1 sem força para aparecer. |

## 5. O que este documento não faz

- Não reabre a GV3 nem a GV3b, não muda as frases dos dois resultados e não junta as 72 unidades numa análise só.
- Não roda vida, não abre os `vidas.tar.gz`, não toca o código nem as configs.
- Não diz que o pet "gosta", "prefere" ou "enjoa", e não compara com animais.

## 6. A GVN-2: o que as vidas gravadas mostram (2026-11-12, Claude Code, Opus 5.5, branch `v3-gosto-visual-gvn2`)

As GVN-1 a GVN-6 foram DECIDIDAS pela recomendação (Matheus, 2026-11-12; `docs/registro/2026-11.md`, D-GV-GVN-1). Esta seção é a leitura
da GVN-2, pelo plano curto `docs/PLANO_ANALISE_V3_GOSTO_VISUAL_GVN2.md`, commitado e empurrado antes de abrir os `vidas.tar.gz`. **É
descritiva, não confirmatória; os dois negativos ficam como estão, e as frases da GV3 e da GV3b não mudam.** Nenhuma vida nova.

**O script:** `artifacts_v3_gosto_visual/gvn2/leitura.py` (rode `python -I artifacts_v3_gosto_visual/gvn2/leitura.py .` na raiz), só sobre
os `*_sonda.json` dos dois `vidas.tar.gz`, com o `medidas.json` de cada run para ligar e conferir. A saída é o
`artifacts_v3_gosto_visual/gvn2/leitura.json`, igual byte a byte a cada execução (`tests/test_gosto_visual_gvn2.py`). As chaves abaixo são
dela, com o prefixo `gv3.` ou `gv3b.`. Os três donos entram juntos (108 pets por genoma), como na seção 3; os IC95 reamostram unidades
inteiras (2000, semente 20261112), sem nenhuma reamostra indefinida.

**A conferência C0 passou nas duas:** 216 vidas, 4536 réplicas e 72 576 decisões por run, iguais ao `medidas.json` (`C0`).

**M4, a medida da H5 como a seção 2 a escreve:** a parte do peso da unidade de olhar não se lê nos `vidas.tar.gz`: a sonda não gravou os
termos (`M4`; de cada decisão, só `acao` e `olha`). Medi-la pelo replay dos logs é a decisão aberta GVN-2b do plano (seção 5 dele).

| o quê | GV3 próprio | GV3 vazio | GV3b próprio | GV3b vazio | chave |
|---|---|---|---|---|---|
| réplicas válidas | 2138 | 2145 | 2112 | 2114 | `M1_<g>.replicas_validas` |
| saídas por réplica válida, média (mediana) | 2,373 (2) | 2,540 (3) | 1,685 (2) | 1,702 (2) | `M1_<g>.saidas` |
| voltas por réplica válida, média | 1,514 | 1,714 | 0,724 | 0,734 | `M1_<g>.voltas.media` |
| voltas à mesma TV / à outra, média | 0,860 / 0,654 | 0,965 / 0,749 | 0,227 / 0,497 | 0,241 / 0,493 | `M1_<g>.voltas_mesma.media`, `voltas_outra.media` |
| fração das réplicas com pelo menos uma volta | 0,793 | 0,833 | 0,592 | 0,604 | `M1_<g>.fracao_com_volta` |
| viu as duas: réplicas; a segunda TV por troca direta / por volta | 1253; 482 / 771 | 1379; 572 / 807 | 1237; 313 / 924 | 1253; 336 / 917 | `M1_<g>.viu_as_duas` |
| pares (t, t + 1) com a TV olhada em t | 7258 | 8344 | 4118 | 4166 | `M2_<g>.pares.juntas.n` |
| fica / troca / sai, juntas | 0,178 / 0,123 / 0,699 | 0,200 / 0,147 / 0,653 | 0,051 / 0,085 / 0,864 | 0,048 / 0,089 / 0,863 | `M2_<g>.pares.juntas` |
| fica na A / fica na B | 0,168 / 0,188 | 0,196 / 0,204 | 0,045 / 0,057 | 0,051 / 0,045 | `M2_<g>.pares.A.fica`, `B.fica` |
| as três ações mais contadas na saída | dormir 2205, chamar_atencao 1602, brincar 554 | dormir 2256, chamar_atencao 1795, brincar 600 | dormir 1725, chamar_atencao 814, explorar 388 | dormir 1678, chamar_atencao 904, explorar 391 | `M2_<g>.pares.acoes_na_saida` |
| pares por pet, média; por réplica válida | 67,2; 3,39 | 77,3; 3,89 | 38,1; 1,95 | 38,6; 1,97 | `M2_<g>.pares_por_pet_medio`, `pares_por_replica_valida_medio` |
| Spearman(Δ_I, dif_fica), todos os pares | 0,823 [0,694; 0,886] | — | 0,645 [0,485; 0,743] | — | `M2_proprio.spearman_di_dif_fica` |
| o mesmo, só os pares das réplicas em que viu as duas | 0,766 [0,598; 0,860] | — | 0,566 [0,379; 0,690] | — | `M2_proprio.spearman_di_dif_fica_so_ambas` |
| a média de dif_fica | — | −0,003 [−0,030; 0,027] | — | 0,006 [−0,005; 0,018] | `M2_vazio.media_dif_fica` |
| \|d_g\|, o termo `gosto` de A menos o de B, média em S (fração de A_max = 4S); p95 em S | 0,189 (0,047); 0,417 | 0,069 (0,017); 0,174 | 0,217 (0,054); 0,436 | 0,030 (0,007); 0,073 | `M3_<g>.abs_d_g` |

Os 108 pets de cada genoma tiveram pares das duas TVs, inclusive só nas réplicas em que viram as duas (`M2_<g>.pets_com_pares_das_duas`,
`pets_com_pares_das_duas_so_ambas`).

**As frases do plano:**
- Por réplica válida, o pet teve em média 2,373 saídas e 1,514 voltas (0,860 à mesma TV, 0,654 à outra) no próprio da GV3, e 1,685 saídas e
  0,724 voltas (0,227 à mesma, 0,497 à outra) no próprio da GV3b (`M1_proprio`).
- Nas réplicas em que viu as duas, a segunda TV veio por uma troca direta em 482 e por uma volta em 771 (GV3, próprio), e em 313 e 924
  (GV3b, próprio) (`M1_proprio.viu_as_duas`).
- Depois de uma decisão olhando uma TV, a decisão seguinte ficou na mesma TV em 0,178 dos pares, trocou em 0,123 e saiu em 0,699 (GV3,
  próprio), e 0,051, 0,085 e 0,864 (GV3b, próprio); nas saídas, as ações mais contadas foram dormir e chamar_atencao nas duas
  (`M2_proprio.pares`).
- No próprio, Spearman(Δ_I, dif_fica) = 0,823 [0,694; 0,886] na GV3 e 0,645 [0,485; 0,743] na GV3b (`M2_proprio.spearman_di_dif_fica`); o
  IC95 não contém 0 nas duas. Só nas réplicas em que viu as duas, 0,766 [0,598; 0,860] e 0,566 [0,379; 0,690]; o IC95 não contém 0. Leitura
  descritiva.
- No vazio, a média de dif_fica é −0,003 [−0,030; 0,027] na GV3 e 0,006 [−0,005; 0,018] na GV3b (`M2_vazio.media_dif_fica`).
- O termo `gosto` calculado do agrado gravado diferiu entre as duas TVs, em média, 0,189 S na GV3 e 0,217 S na GV3b (no próprio), contra o
  teto da ativação de 4 S (`M3_proprio.abs_d_g`); na GV3b, sem o tédio do enjoo, um teto do termo.
- A parte do peso da unidade de olhar não se lê nos `vidas.tar.gz`: a sonda não gravou os termos (`M4`).

**O que isso diz das H5 e H4 (só as frases da seção 4 do plano):**
- **H5.** Que a saída da TV seja a regra (0,699 e 0,864 dos pares saem para outra ação, `M2_proprio.pares.juntas.sai`) é o que a H5 prevê
  na seção 2 ("o pet sai da TV pelos drives"). Que a ordem de dif_fica acompanhe Δ_I, também nas réplicas em que o pet viu as duas
  (`M2_proprio.spearman_di_dif_fica_so_ambas`), não é o que a H5 prevê na seção 2 (que a diferença entre as duas TVs na chance de ficar
  seja pequena mesmo ali). O Spearman lê a ordem, não o tamanho: o tamanho de dif_fica por pet não é medida deste plano, e a parte do peso
  (a H5 como escrita) segue sem medida (`M4`, GVN-2b).
- **H4.** Que a olhada seja curta (cerca de 2,4 e 1,7 saídas por réplica válida, e 3,39 e 1,95 pares por réplica válida no próprio,
  `M1_proprio.saidas.media`, `M2_proprio.pares_por_replica_valida_medio`) é o que a H4 prevê na seção 2 ("as olhadas raras e curtas").

**As ressalvas:** a leitura foi escolhida depois dos dois resultados e não tem correção para comparações múltiplas; o "viu as duas"
condiciona num comportamento (a ressalva da seção 3); o M3 usa o agrado do início da janela e, na GV3b, não tem o tédio; os pares de um pet
vêm de réplicas do mesmo dia e não são independentes. **Nenhuma alegação de novidade.**
