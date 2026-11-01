# A espec da C3: a escolha só é refeita quando o corpo ou o mundo muda (DigiBrain modular, v13)

**O que é:** a especificação da subchave `redecidir_evento` da `docs/TAREFA_V3_REDECIDIR_EVENTO.md` (a etapa 2, seções 3 e 7), exatamente
como as RD-1 a RD-9 decidiram. Espec e código no mesmo PR, a pedido do Gerente; nenhuma vida de pesquisa, nenhuma faixa reservada, nenhum
adendo ao plano.

**Quem e quando:** Claude Code, Opus 5.5, em 2026-10-31, na worktree `v3-redecidir-evento-espec`, a pedido do Gerente da V3.

**O status:** PROPOSTA. Todo valor novo é PROPOSTO e SEM FONTE salvo onde a linha diz. As RD-1 a RD-9 são DECIDIDAS (o Matheus,
2026-10-31). As leituras que esta espec teve de fazer sobre o que as RD não fixam estão na seção 9 (RE-1 a RE-4), com a recomendação e o
custo de errar; o código segue a recomendação de cada uma.

**Os rótulos:** [DADO] é número de artefato no git; [EXISTE] é o que o código da `main` (`22cc251`) já faz (o [CÓDIGO] da tarefa);
[MECANISMO] é o que uma fonte verificada diz de um mecanismo; [HIPÓTESE] é o que falta medir.

## 0. Em uma página

- **A pergunta** (a tarefa, seção 1): no longe, o modular quebra as idas e as buscas a cada poucas decisões. Parte disso vem de o M-ARB
  refazer o sorteio a cada decisão, mesmo quando nada mudou no corpo nem no mundo?
- **O que o código faz hoje** [EXISTE]: a cada decisão (15 ticks), o M-IMPULSO refaz as ativações e o M-ARB sorteia entre as unidades com
  peso, salvo o reflexo do sono. A intenção em curso entra no sorteio com a persistência `h`, já no teto (`a_max`), mas não é garantida.
- **A mudança:** com a subchave, a unidade escolhida na decisão anterior **fica**, sem sorteio e sem gastar a rng de política, enquanto não
  houver um evento: o reflexo do sono, uma urgência que muda de quarto de S, uma mudança no mundo (a comida boa à vista, o cheiro, o alvo,
  o dono), o fim da opção, ou o teto de 6 decisões seguradas. Com evento, o sorteio de hoje, sem mudança.
- **O que fica igual:** o M-SENS, o M-AFETO, o contexto do M-ESTADO, o M-MEM, o M-IMPULSO e o registro rodam em toda decisão; a escolha
  segurada entra no M-ESTADO e no crédito (o PE-3) como a mesma escolha sorteada. O P1, o P2, a persistência, os inatos e o reflexo não
  mudam.
- **Onde entra:** só no pacote `digilab/digibrain/` (o M-ESTADO, o M-ARB e o M-ADAPT), atrás de `ConfigDigibrain.redecidir_evento`,
  desligada. O `engine.py`, o motor, o mundo, o corpo, o A, a v12 e o jogo web não mudam.
- **Desligada,** as vidas de hoje saem byte a byte: o gabarito do M3\* foi gravado antes, num commit próprio
  (`tests/gabaritos/redecidir_evento_de_hoje.json`), e o do M2 já existia (`tests/gabaritos/habito_intencao_de_hoje.json`, do #513).
- **O que esta espec não afirma:** que segurar a escolha conserta o longe, que o modular supera o A, ou que o mecanismo é novo.

## 1. De onde vem

### 1.1 As quebras no longe [DADO]

Os números são os da tarefa (seção 1.1), que cita os artefatos:
- **o longe sorteado, a L0** (`docs/ESPEC_LONGE_L2_DIGIBRAIN_MODULAR.md`, 1.1): das 5 142 buscas pelo cheiro trocadas do M3\*, 4 096
  (80 %) pelo reflexo do sono e 1 042 (20 %) por outra unidade;
- **o `longe_fixo`, a C1** (`docs/RESULTADO_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md`, 13.4, item 3): a ida ao lugar lembrado termina 12 704 vezes
  em `meta` e 17 603 em `trocou`; destas, 14 023 pelo reflexo, 1 026 pelo dormir sorteado e 2 554 por outra unidade;
- **a C2** (o mesmo RESULTADO, 14): a corrida do comportamento durou 1,50 decisão em média.

**O espaço do mecanismo:** o reflexo continua sendo evento (seção 3), então continua quebrando. O que a subchave alcança é a parte que não
é o reflexo (cerca de 20 % das quebras nos dois lugares) e as escolhas de uma decisão (o explorar pelo vagar e pelo cheiro, o chamar) que
hoje podem trocar a cada sorteio. Um nulo é plausível e está escrito antes (a tarefa, 1.5).

### 1.2 Como o código decide hoje [EXISTE]

- **A ordem** (`digilab/digibrain/adapt.py`, `DigiBrain.agir`): M-SENS, M-AFETO, o reflexo (`Arbitragem.reflexo`, uma conta só), M-ESTADO
  (o contexto), M-MEM, M-IMPULSO, M-ARB (`Arbitragem.escolher`) e M-ESTADO (`escolhida`).
- **O sorteio** (`digilab/digibrain/arb.py`): com dois candidatos de peso positivo ou mais, uma chamada `rng.random()` (a de política, a
  única do cérebro) e o `sortear_inteiro`; com um, ele; com nenhum, o ocioso. A unidade de ativação 0 não concorre.
- **A intenção** (`digilab/digibrain/estado.py`): só as unidades com alvo fixo e a busca pelo cheiro (com `intencao_cheiro`) abrem uma I\*;
  as outras são opções de uma decisão, que acabam na própria consequência com o motivo `unica`.
- **O gesto do dono** (`DigiBrain.receber_acao_dono`): o M-ADAPT só o registra em `_gestos`, que zera a cada decisão.

### 1.3 A fonte

- [MECANISMO] **Gadanho e Hallam (2001),** *Adaptive Behavior* 9(1), `10.1177/105971230200900102`, VERIFICADA na C0
  (`docs/referencias/v3c0_referencias_verificadas.csv`, a linha das trilhas C2 e C3). A fonte afirma, pelo resumo do Crossref: um robô
  simulado numa tarefa de energia, com um modelo de emoção que, dentro de um aprendizado por reforço, tem três papéis, um deles **decidir
  quando reavaliar a decisão**. Pela triagem (lida pela tese de 1999, a versão-irmã, não o artigo): o gatilho de reavaliação explica a maior
  parte do ganho. **O que autoriza:** a direção (refazer a escolha só quando o estado interno muda pode ajudar um agente com corpo). **Não
  autoriza:** o tamanho, nem que os eventos daqui sejam os da fonte (lá o gatilho vem do modelo de emoção; aqui, das urgências, do reflexo
  e do mundo).
- [MECANISMO] **Sutton, Precup e Singh (1999),** *Artificial Intelligence* 112, `10.1016/s0004-3702(99)00052-1`, VERIFICADA por título e
  metadados (`docs/referencias/v2_referencias_verificadas.csv`): o formalismo das opções, a ação estendida no tempo com início e término. A
  escolha segurada até um evento é uma opção cuja condição de término é o evento; a fonte dá o formalismo, não esta regra.
- **SEM FONTE:** a lista de eventos, as faixas em quartos de S, o teto de 6, as leituras RE-1 a RE-4 e todos os números novos.
- **Nenhuma alegação de novidade.** Redecidir por evento num agente com corpo já está na primeira fonte; o que o projeto faz é o teste com
  braço de controle, num pet persistente, com replay determinístico.

## 2. O mecanismo

### 2.1 A escolha segurada

Numa decisão k > 0, sem o reflexo:
- **o candidato:** a unidade escolhida na decisão k − 1 (a mesma `chave`), se a k − 1 não foi o reflexo (RE-1);
- **segura** se não há evento (seção 3) e o candidato está na lista de unidades da decisão k **com peso positivo** (RE-2): o M-ARB o
  escolhe sem sorteio e **sem chamar a rng de política**;
- **senão,** o sorteio de hoje, sem mudança (inclusive o caso de um candidato só e o ocioso).

Na decisão 0 e em toda decisão com o reflexo, o de hoje.

### 2.2 O que roda numa decisão segurada

- **Igual:** o M-SENS, o M-AFETO, o contexto do M-ESTADO, o M-MEM e o M-IMPULSO. O z, as ativações, os pesos e o registro saem iguais em
  forma.
- **O M-ARB:** o `u` fica `None` (nenhum sorteio), o contador `sorteios` não sobe. **As sondas** (o G-PESA): numa decisão segurada, como no
  reflexo, nenhum módulo "decidiu": cada sonda registra a unidade escolhida e `*_decidiu` falso. O plano (o adendo 8, etapa 3) diz como o
  G-PESA lê essas decisões; esta espec só fixa o registro.
- **O M-ESTADO (`escolhida`):** a escolha segurada é uma escolha. A I\* de novo sobe o C e o `n`; uma unidade sem alvo fixo abre uma opção de
  uma decisão. Os fins, o F e o crédito ao P2 são os da mesma escolha sorteada (o T-RD-4).

### 2.3 A ordem dentro da decisão

A ordem de hoje (1.2) ganha dois passos, só com a subchave:
1. M-SENS, M-AFETO e o reflexo, como hoje;
2. **novo: os eventos** (`EstadoDinamico.eventos(sens, afeto, reflexo, dono_agiu)`): o M-ESTADO compara o corpo e o mundo da decisão k com os
   da k − 1, devolve a lista dos eventos que valeram e o candidato a segurar (ou nenhum), e guarda o retrato da decisão k. Sem rng;
3. o contexto, o M-MEM e o M-IMPULSO, como hoje;
4. **o M-ARB com o candidato** (`Arbitragem.escolher(..., segurar=chave)`): segura (2.1) ou sorteia; se o candidato não está na lista com
   peso positivo, o M-ADAPT acrescenta o E-FIM à lista;
5. o M-ESTADO (`escolhida`), como hoje, e o registro da escolha segurada (`registrar_redecisao`: o candidato da decisão seguinte e o
   contador do teto).

### 2.4 O estado novo no M-ESTADO

Só com a subchave: o candidato (a última escolha fora do reflexo, ou nenhum), `n_seg` (as decisões seguradas seguidas), o retrato da
decisão anterior (as faixas das urgências, os ids das comidas boas à vista, se há cheiro), se a opção da decisão anterior acabou na
consequência, e as contagens (decisões seguradas, decisões com cada evento, sequências que acabaram no teto). Nada disso entra no estado
interno com a subchave desligada.

## 3. Os eventos (RD-3 e RD-4)

Conferidos no começo da decisão k, sem rng, contra a decisão k − 1. Todos os que valem entram na lista; um basta para o sorteio.

| evento | vale quando | o que o cérebro lê |
|---|---|---|
| **E-REFLEXO** | o reflexo do sono vale na decisão k **ou valeu na k − 1** (RE-1) | a leitura da energia (`Arbitragem.reflexo`), a conta de hoje |
| **E-RECEPTOR** | alguma urgência (`afeto["urgencias"]`) muda de faixa; as faixas em quartos de S, com os limites S/4, S/2 e 3S/4 (a faixa de u é o número de limites ≤ u) | as urgências que o M-AFETO já calcula |
| **E-MUNDO** | o conjunto dos ids das comidas boas (`COMIDAS_BOAS`) à vista muda; o cheiro aparece ou some (`ha_cheiro`); o alvo do candidato (comida ou bola) sai dos objetos à vista; o dono agiu desde a decisão anterior (algum `receber_acao_dono`) | os `objetos` e o `ha_cheiro` do M-SENS; os gestos que o M-ADAPT já registra |
| **E-FIM** | a opção da decisão k − 1 acabou na consequência com um motivo que não é `unica` (meta, sumiu, desistiu, achou; RE-3); ou o candidato não está na lista da decisão k com peso positivo (RE-2) | os fins que o `consequencia` já devolve; a lista e os pesos do M-ARB |
| **E-TETO** | o candidato já foi segurado `n_seg_max` decisões seguidas | o `n_seg` |

- **`n_seg_max` = 6** (RD-4, DECIDIDA): PROPOSTO como número, o valor do `n_desiste_cheiro` e do `n_suspensa_max`, sem calibração, SEM
  FONTE. Fica na `ConfigDigibrainInatos`, no módulo `estado` do `CAMPOS_POR_MODULO` (`digilab/digibrain/ganchos.py`).
- **O teto:** depois de 6 decisões seguradas, a sétima sorteia e o `n_seg` volta a 0. Se o sorteio escolher a mesma unidade, ela pode ser
  segurada de novo.
- **O G-SEM-DIRECAO continua valendo:** o cérebro só lê se há cheiro, nunca a direção.

## 4. O registro

- **A decisão,** só com a subchave, ganha `segurada` (verdadeiro ou falso) e `evento` (a lista dos que valeram, na ordem da tabela da seção
  3). Na decisão 0, `segurada` é falso e a lista é vazia; em toda outra decisão sorteada a lista tem pelo menos um evento.
- **O estado interno do M-ESTADO,** só com a subchave, ganha `redecidir`: o candidato, o `n_seg`, as decisões seguradas, as decisões com
  cada evento e as sequências que acabaram no teto.
- **A contagem das trocas da LP-2** (a tarefa, 1.4): uma troca é uma decisão sem o reflexo cuja unidade escolhida difere da última unidade
  escolhida sem o reflexo; a sequência busca, reflexo, reflexo, a mesma busca dá zero. A função (`trocas_por_decisao`, no orquestrador do
  protótipo) existe para o T-RD-3; ela só entra nas medidas no orquestrador da etapa 3, para as medidas de hoje não mudarem.

## 5. Onde entra e o que não muda

**Onde entra:**
- **a subchave:** `ConfigDigibrain.redecidir_evento: bool = False`, PROPOSTA, SEM FONTE como valor (a direção vem de Gadanho e Hallam).
  **Erro alto (`ValueError`)** se ligada com a `credito_corrida` ou a `intencao_suspensa` (a D-C2-4 e a LP-3), ou sem as duas subchaves do
  cheiro (RE-4: os braços previstos são o M3\* e o M2 do conserto);
- **o campo:** `ConfigDigibrainInatos.n_seg_max = 6`;
- **os módulos:** o M-ESTADO (`eventos`, `registrar_redecisao`, o retrato e o E-FIM na `consequencia`), o M-ARB (`escolher` com o
  `segurar`) e o M-ADAPT (a ordem da seção 2.3 e o registro);
- **o orquestrador do protótipo:** só a conferência que a tarefa pede em toda vida com a subchave (seção 6) e a contagem da LP-2 do
  T-RD-3. Os braços `M3*R` e `M2R` ao lado do `SUBCHAVES_CONSERTO` ficam para a etapa 3, com o orquestrador da run (como o `M2c` da C2).

**O que não muda:** o `engine.py` (o sha em `ENGINE_SHA256_V0`), o motor, o mundo, o corpo, o cheiro, o `longe_fixo`, o A, a v12; o P1, o
P2 e o crédito; a persistência e o `w_pers`; o reflexo e o `lambda_sono`; os inatos do #428 (RD-9); as medidas por vida do orquestrador.

**A web:** é pesquisa de cérebro atrás de chave desligada; fica só no Python (a decisão "pesquisa no Python, um DigiBrain na web"). O
modular ainda não está no jogo, e nada muda em `web/app/`.

## 6. Os testes (antes de qualquer vida; sementes 101…505)

| teste | o que confere |
|---|---|
| **o gabarito antes** | `tests/gabaritos/redecidir_evento_de_hoje.json`, o M3\* no `longe_fixo` e no comedouro, gravado num commit próprio antes do código; o M2 está no gabarito do #513 |
| **G2** | com a subchave desligada, os gabaritos do M3\*, do M2 (#513), do conserto e do modular saem byte a byte; o estado e o motivo sem campo novo |
| **G2-SEPARADO** | ligada, ela muda só a vida do braço que a liga; fora do pacote `digibrain` e do orquestrador, nada a lê |
| **G1** | o replay de cada vida com a subchave ligada, nas cinco sementes, com o M3\* e o M2 |
| **T-RD-1** | sem nenhum evento, a escolha fica por 6 decisões e a rng de política não é chamada; na sétima, o E-TETO devolve o sorteio |
| **T-RD-2** | cada evento (E-REFLEXO, E-RECEPTOR, E-MUNDO, E-FIM) devolve o sorteio na decisão em que aparece, um por um, com sequências sintéticas |
| **T-RD-3** | a busca, o reflexo, o reflexo e a mesma busca: zero trocas na contagem da LP-2, nos dois braços |
| **T-RD-4** | a escolha segurada de uma I\* sobe o C e o `n` como a mesma escolha sorteada; os fins, o F e o crédito são os de sem a subchave |
| **as conferências do orquestrador** | a do crédito e a dos fins seguem falhando alto; a nova (`conferir_redecidir`): toda decisão segurada tem a mesma `chave` da anterior, a anterior não é o reflexo, nenhum evento, `n_seg` ≤ 6, e toda outra decisão depois da 0 tem um evento |
| **G-MECANISMO, G-INT, G-SEM-DIRECAO, G-RECEPTOR** | os de hoje passam com a subchave ligada |
| **a rng** | numa decisão segurada o M-ARB não chama a rng; o M-ESTADO não recebe rng |

## 7. A avaliação (só a referência; o plano é o adendo 8, na etapa 3)

Fixada pela tarefa (seção 4) e pelas RD, sem mudança aqui: os braços M3\*, M3\*R, M2 e M2R; o primário P-R (M3\*R − M3\* na taxa por
episódio de fome, nas 4 células do `longe_fixo`); a guarda no comedouro; as premissas P-SEGURA (≥ 0,10 das decisões sem o reflexo
seguradas) e P-EVENTO (≤ 0,25 das sequências pelo teto); a faixa 76101…76505 (RD-7), ainda não reservada. O registro da seção 4 dá o que
as premissas e os descritivos leem.

## 8. O que esta espec não afirma

- **Que segurar a escolha conserta o longe.** O espaço do mecanismo é cerca de 20 % das quebras (1.1).
- **Que o modular supera o A.** O A11 não está na avaliação.
- **Que algum cérebro está pronto.**
- **Que o mecanismo é novo** (1.3).

## 9. O que esta espec leu além das RD (para o Matheus)

As RD-1 a RD-9 não fixam estes quatro pontos; o código segue a recomendação de cada um. **As RE-1 a RE-4 foram DECIDIDAS pelo Matheus em 2026-11-01, pela recomendação.** Todos SEM FONTE.

| # | a leitura | a recomendação | o custo de errar |
|---|---|---|---|
| **RE-1** | a decisão logo depois do reflexo sorteia (o E-REFLEXO vale na decisão do reflexo e na seguinte)(DECIDIDA) | **sim:** o dormir do reflexo não é uma escolha a segurar, e a tarefa (1.3) diz que ao acordar o sorteio roda como hoje | a alternativa (segurar a escolha de antes do reflexo ao acordar) é a retomada forçada que a L-2 recusou (LS-3) e mistura a C3 com a `intencao_suspensa` |
| **RE-2** | o candidato com peso 0 conta como fora da lista (E-FIM)(DECIDIDA) | **sim:** no M-ARB a unidade a 0 não concorre; segurá-la faria o pet escolher o que o sorteio de hoje nunca escolheria | sem isso, uma unidade sem ativação (a fome que passou sem mudar de quarto) ficaria até o teto |
| **RE-3** | o E-FIM não conta o fim `unica` das opções de uma decisão(DECIDIDA) | **sim:** toda opção de uma decisão acaba na própria consequência; contar esse fim tornaria impossível segurar o explorar, o chamar e o dormir, contra a RD-2 | contando, o braço só seguraria as intenções, a alternativa (b) da RD-2, que o Matheus recusou |
| **RE-4** | a subchave recusa, além da `credito_corrida` e da `intencao_suspensa`, a falta das duas subchaves do cheiro(DECIDIDA) | **sim:** os braços previstos (RD-1) são o M3\* e o M2 do conserto; outra combinação não tem plano | recusar demais só pede tirar a linha quando houver um braço novo com plano; aceitar demais deixa rodar um braço sem pergunta |
