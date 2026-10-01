# V2 — A1-BOLA: desenho da interação mínima da fase 1a (2026-10-01)

Status: **PROPOSTO, para aprovação do Matheus** (tarefa `docs/TAREFA_V2_A1_BOLA.md`). Só desenho: **nenhum código muda nesta tarefa**; a
implementação vira tarefa própria depois da aprovação. Decisão de partida: a bola como interação mínima com consequência da fase 1a
(Matheus, 2026-10-01, a partir de `docs/V2_INVENTARIO_JOGO.md`, seções 3 e 4; mantida como 1a na decisão D10 de
`docs/DEFINICOES_V2.md`, com as frutas como alavanca seguinte). Hipótese H1, alavanca 1a do `docs/PLANO_V2_PESQUISA.md`. As definições dos gates
e as duas perguntas por alavanca (1a-pet e 1a-dono) são as de `docs/DEFINICOES_V2.md`, seções 3, 4 e 6 (PROPOSTAS, até o referendo).

Todo número aqui é PROPOSTO e sem fonte, salvo quando aponta um artefato ou um símbolo de `digilab/config.py`. Nada do que o desenho diz
sobre o Championship ou outro jogo é evidência (`literatura-digilab`, regra 4).

---

## 0. Em uma página

- **O dono põe uma bola** (ação do dono, no orçamento, no log). Ela fica no cenário por um tempo fixo ou até o dono tirar.
- **O pet percebe a bola** como uma entrada a mais da percepção (presente ou não), e nada mais: sem posição, sem distância.
- **O pet decide, a cada 15 min, como sempre:** escolher `brincar` com a bola no cenário é brincar **com a bola**; qualquer outra ação é
  ignorá-la por enquanto. Nenhuma ação nova entra em `events.AcaoPet`.
- **Consequência:** brincar com a bola dá um ganho de humor maior que o do `brincar` sozinho e consome a bola; o custo de energia é o
  de sempre. Humor não entra em `Estado.em_privacao` (`digilab/state.py:43`), então a bola não encosta na cadeia fome/higiene/energia →
  saúde → morte.
- **O dono muda quando a bola aparece** (e por quanto tempo), e julga a decisão com o elogio e a bronca de sempre
  (`donos.julgar_acao` já diz que brincar cansado, com necessidade baixa ou à noite é errado).
- **Sem sorteio novo, sem rng nova:** a bola é determinística; o replay a reconstrói do log.
- **Camada por cima:** `MotorAmbiente`, subclasse do `MotorEducacao`, como o `MotorPersonalidade` é do `MotorComFeedback`. `engine.py`
  intocado; sem bola no log, a vida é byte a byte a de hoje.
- **A 1a roda sozinha, com duas perguntas separadas** (`docs/DEFINICOES_V2.md`, seção 4): **1a-pet**, o pet aprende pela própria
  consequência, sem dono no laço; **1a-dono**, a bola aumenta o efeito do dono (hipótese do projeto, sem apoio na literatura). Sem
  aprendizado a `PoliticaLobos` responde à bola por um coeficiente de prior igual para todos os donos, e o que separa os donos é só
  **quando** cada um põe a bola. Depois, com a L1, o coeficiente aprende e o desenho 2 × 2 (bola × dono) responde a 1a-dono.
- **Web:** pets v12; um botão "Bola" e o sprite dela no palco; o motivo "porque a bola estava lá".

---

## 1. O que o pet percebe, decide e sofre; o que o dono muda

### 1.1 A bola no mundo

Um objeto só, com dois campos, fora do `Estado` da camada 1 (que não muda):

| campo | o que é |
|---|---|
| `tick_posta` | o tick em que o dono pôs a bola (do evento no log) |
| `prazo` | `tick_posta + ConfigBola.duracao_min`; ao chegar, a bola some sozinha ("o pet perdeu o interesse") |

Uma bola por vez: pôr com uma já no cenário renova o prazo (não cria outra). Tirar antes do prazo também é ação do dono. Sem posição,
sem distância, sem física: o corpo 2D fica fora (tarefa, seção 6).

### 1.2 O que o pet percebe

Uma entrada a mais na percepção: `bola = 1.0` se há bola no cenário, senão `0.0`. Opcionalmente uma segunda, `bola_idade =
(tick − tick_posta) / duracao`, para a política poder distinguir "acabou de chegar" de "está para sumir"; o desenho mínimo fica com a
primeira só. A entrada vai na percepção da `PoliticaLobos` (`lobos.ENTRADAS`, hoje 10 entradas) e **não** na `Observacao` do
`PoliticaInstinto` nem nas `features` do bandit (que ficam como estão: é o que mantém a canônica).

### 1.3 O que o pet decide

Nada novo na lista de ações: a cada decisão (96 por dia, `Config.intervalo_decisao_ticks`) a política escolhe entre as 7 ações de sempre.
A interpretação é da camada:

| a política escolheu | com bola no cenário | sem bola |
|---|---|---|
| `brincar` | **brinca com a bola**: consequência da seção 1.4, a bola some | brinca como hoje |
| qualquer outra | **ignora a bola** por esta decisão; ela continua lá até o prazo | como hoje |

"Perseguir" e "ignorar" da tarefa são, portanto, `brincar` e "qualquer outra" enquanto a bola está lá. Com `duracao_min = 60` o pet tem
4 decisões para se decidir. A escolha é genuinamente da política porque a entrada `bola` muda o peso efetivo de `brincar` na
`PoliticaLobos` (seção 2); no instinto, que não lê a entrada, o pet brinca com a bola na taxa de sempre do `brincar` (é o controle).

### 1.4 A consequência

| para quem | o quê | onde fica |
|---|---|---|
| o pet | humor `+ ganho_humor_bola` (PROPOSTO 0,15, além do `humor_por_tick_brincando × 15` que o `brincar` já dá); energia `−0,02` (a de `efeito_da_acao_do_pet`, sem custo extra); a bola some | `MotorAmbiente`, depois de `efeito_da_acao_do_pet` |
| o mundo | a bola some ao ser usada ou no prazo | idem |
| o dono | vê que o pet brincou com a bola ou a ignorou (histórico e motivo); julga com elogio ou bronca | `donos.julgar_acao` (sem mudança: `brincar` cansado, com necessidade baixa ou à noite já é −1) |
| o aprendiz | elogio ou bronca creditados à decisão, como hoje; na L1, o peso da entrada `bola` em `brincar` aprende | `PoliticaLobos.receber_acao_dono` |

Por que o humor: é a única necessidade que **não** entra em `Estado.em_privacao` (`min(fome, higiene, energia) < 0,15`); ganhar ou perder
humor não move a saúde nem a morte. A energia cai o mesmo 0,02 de um `brincar` comum, já presente em todas as runs. Brincar à noite
ou cansado tem o custo de sempre (dorme depois) e a bronca do dono coerente.

Por que não a fome: comida posta é o eixo do cuidado (`docs/V2_INVENTARIO_JOGO.md`, candidata B). Fica fora.

### 1.5 O que o dono muda

| o que | como | custo |
|---|---|---|
| **quando** a bola aparece | ação do dono `por_bola` (seção 3), a qualquer hora, inclusive dormindo (o pet não acorda por ela) | 1 interação do orçamento, como qualquer outra: pôr a bola troca um cuidado por uma oportunidade |
| **por quanto tempo** | `tirar_bola` antes do prazo | 1 interação |
| o julgamento | elogiar ou repreender a decisão seguinte, como hoje | 1 interação |

"Onde" não existe neste desenho (sem espaço). Pôr a bola **não** é contato: não zera `tick_ultimo_cuidado` nem conta em `total_cuidados`
(a bola não é cuidado; isso mantém o relógio do instinto e do bandit iguais em todos os braços).

Donos sintéticos (PROPOSTO, `digilab/donos.py` sem mudar os de hoje; um `DonoComBola` que embrulha, como o `DonoComEducacao`):

| dono | quando põe a bola |
|---|---|
| atencioso, incoerente | só com o pet acordado, fora da noite, sem necessidade abaixo do limiar de cuidado e sem bola no cenário; no máximo `bolas_por_dia` (PROPOSTO 4) |
| relapso | igual, mas só nos passos de visita |
| aleatório | `por_bola` entra no sorteio uniforme das ações dele (as 6 da v1 + `por_bola`): bola em horas aleatórias |
| **só cuidado (H0)** | nunca põe a bola: é o braço de controle permanente do plano da V2 |

O julgamento não muda: `julgar_acao` já cobre `brincar`.

---

## 2. A restrição do inventário: como a decisão entra sem mexer em `AcaoPet`

O inventário mostrou que uma ação nova em `events.AcaoPet` muda a canônica: o bandit tem um braço por ação, `tracos.ORDEM_TRACOS =
tuple(AcaoPet)`, o desejo e as sondas da divergência iteram o enum, e a arena v1 mapeia traços em stats. Três jeitos de entrar:

| opção | como | prós | contras |
|---|---|---|---|
| **A. Alvo de `brincar`, interpretado na camada** (recomendada) | a política escolhe `brincar`; o `MotorAmbiente` vê a bola e aplica a consequência | zero mudança em `AcaoPet`, no bandit, nos traços, nas sondas e na expressão; o instinto vira controle sem código; o motivo cita a entrada `bola` quando ela pesou; a web espelha com uma linha | "ignorar" não é uma ação, é a ausência de `brincar`; o pet não distingue "brincar com a bola" de "brincar sem ela" fora do contexto (a política distingue pela entrada, o enum não) |
| B. Ação interna da `PoliticaLobos`, traduzida para `brincar` na saída | os lobos têm o candidato `perseguir_bola`; `agir` devolve `AcaoPet.BRINCAR` ao motor | o motivo nomeia a ação; o prior da bola é uma regra própria dos impulsos | dois nomes para a mesma ação no motor; a tradução é um ponto a mais de paridade; os traços continuam vendo `brincar` |
| C. Novo membro em `AcaoPet` | `AcaoPet.PERSEGUIR_BOLA` | o mais direto | quebra a canônica e todos os replays antigos; descartada pelo inventário |

**Recomendação: A**, com a regra de prior da seção 2.1 dentro do lobo de impulsos. Se a L1 mostrar que a política precisa separar "brincar
com a bola" de "brincar" como ações distintas, B é o passo seguinte, sem tocar no enum.

### 2.1 A bola nos lobos (`digilab/policies/lobos.py`, PR #108)

- **Percepção:** `ENTRADAS` ganha `"bola"` (11 entradas). Com coeficiente **zero** no prior, `0 × x` soma `0.0` exato à ativação linear, e
  a vida sem bola continua byte a byte a do instinto (gate G2 do L0 continua valendo; teste).
- **Impulsos:** uma regra nova, **`bola_no_cenario`**, testada logo antes de `tempo_livre` (depois de sono, pedido de necessidade,
  abandono e fome moderada: as necessidades continuam na frente, como o DF das "duas prioridades" e como o instinto). Candidatos: os de
  `tempo_livre` (`ocioso`, `explorar`, `brincar`, `chamar_atencao`), com os **mesmos pesos** de `tempo_livre` **mais** um coeficiente da
  entrada `bola` em `brincar`: `w_bola` (PROPOSTO 3, em unidades do prior: `brincar` passa de `1 + 3 × humor` para `1 + 3 × humor + 3 ×
  bola`). Sem bola a regra não dispara (x_bola = 0) e `tempo_livre` decide como sempre.
- **Decisão:** o único peso que a L1 aprende para a bola é esse coeficiente (e os demais de `brincar` nessa regra). Continua abaixo de
  mil pesos (`ConfigLobos.maximo_pesos`): 490 + 4 ações × 11 entradas = 534.
- **Memória e emoção:** conta bolas postas, usadas e ignoradas (L2 decide o que fazer com isso; aqui contribuição zero).
- **Motivo:** quando o termo `w_bola × x_bola` foi o que mudou a escolha (regra de honestidade de hoje: `CLAUDE.md`, "Honestidade do
  fator"), o fator é `bola_no_cenario` e a expressão diz "porque a bola estava lá"; senão, "foi instinto" ou "não sei", como hoje.

### 2.2 Instinto e bandit

Não mudam. O `PoliticaInstinto` não lê a entrada e brinca com a bola na taxa de sempre: é o braço de controle "ambiente sem aprendiz que
veja a bola". O bandit está congelado (decisão do Matheus, 2026-10-01) e não ganha a entrada.

---

## 3. Log, determinismo e replay

### 3.1 Eventos

Duas ações do dono novas no **fim** de `events.AcaoUsuario` (como as de treino e educação): `POR_BOLA = "por_bola"` e `TIRAR_BOLA =
"tirar_bola"`. Entram no log como `acao_usuario` de sempre (`tick`, `tipo`, `valor`): **nenhum tipo de evento novo**. Os donos da v1
sorteiam de `ACOES_V1` (tupla explícita), então o enum crescer não muda a canônica (foi assim com `petisco`). Só o `MotorAmbiente` aceita
as duas; nos motores anteriores levantam erro (o padrão de `ACOES_EDUCACAO`).

Nada do pet entra no log (as ações do pet continuam derivadas, `events.py`), e o estado da bola é função pura dos eventos: `reproduzir_ambiente`
(espelho de `reproduzir_educacao`) reconstrói a bola, as brincadeiras e os motivos.

### 3.2 Determinismo e rng

- Sem sorteio novo: pôr, usar e expirar são determinísticos. **Nenhuma rng nova** e nenhuma chamada a mais nas existentes: a
  decisão do pet continua uma chamada de `rng_politica` por decisão, como o L0 garante.
- Se o desenho ganhar um sorteio um dia (a bola "rola para longe"), ele usa uma `rng_bola` derivada da semente (`protocol.derivar_semente("bola", semente)`),
  nunca a de ambiente nem a de política, e o sorteio é consumido em todos os braços nos mesmos ticks (números comuns, como a
  `rng_travessura`). Fora do mínimo.
- `engine.py` intocado: a bola vive no `MotorAmbiente` (gancho `_aplicar_acao_usuario` para `por_bola`/`tirar_bola`; gancho
  `_decisao_observada` para a consequência e o prazo).
- **Equivalência (teste):** sem `por_bola` no log, `MotorAmbiente` = `MotorEducacao` byte a byte (vidas da V3 e da confirmatória rejogadas,
  como `tests/test_reproducao_v3_confirmatoria.py`); com `PoliticaLobos` sem aprendizado e sem bola, = instinto (G2 do L0).

### 3.3 Config

`ConfigBola` em `digilab/config.py`, com `ligada = False` por padrão (desligada: `MotorAmbiente` = `MotorEducacao`, e `por_bola` no log
levanta erro, como a luta sem `ConfigLesoes.ligada`): `duracao_min` (60), `ganho_humor_bola` (0,15), `w_bola` (3, em unidades do prior dos
lobos), `bolas_por_dia` dos donos (4). Status e fonte em `protocol.PARAMETROS_BOLA_A1`, à parte dos hashes de educação e de confiança.
Tudo PROPOSTO, nada referendado.

---

## 4. Como a 1a roda sozinha, e depois com a L1

Regra do plano (`docs/V2_TRABALHO_PARALELO.md`, seção 4): duas alavancas novas nunca no mesmo braço antes de cada uma passar sozinha. E a regra
de `docs/DEFINICOES_V2.md` (seção 4, decisão D6): cada alavanca responde **duas perguntas com status diferentes**, e passar a primeira não é
evidência para a segunda.

| pergunta | o que testa | apoio | como se mede com a bola |
|---|---|---|---|
| **1a-pet** | com a bola, o pet aprende pela própria consequência | literatura de consequência (`DEFINICOES_V2`, seção 4; para a bola só o apoio geral de cognição mínima e affordances) | sem dono no laço: só cuidado mínimo e nenhum elogio ou bronca; a bola aparece em horários fixos iguais para todos. Métrica: fração das decisões com bola em que o pet escolhe `brincar`, por dia, contra o instinto (que não vê a bola), com IC sobre sementes. Só faz sentido **com a L1** (sem aprendizado a fração é a do prior) |
| **1a-dono** | a bola aumenta o efeito do dono | **nenhum** (hipótese do projeto) | desenho 2 × 2: bola (com, sem) × dono (coerente, aleatório), sobre G3 e G3-T; a interação é o efeito. Só com a L1 |

### 4.1 Sozinha (A1, sem aprendizado)

| braço | política | bola | o que mede |
|---|---|---|---|
| instinto + bola | `PoliticaInstinto` (não vê a bola) | donos põem | o efeito do **ambiente** na vida sem nenhuma política reagir: humor, brincadeiras, orçamento gasto |
| lobos + bola | `PoliticaLobos`, aprendizado desligado, `w_bola` no prior | donos põem | o efeito de uma política **que vê a bola** mas não aprende: os donos diferem só por quando põem |
| **só cuidado acoplado (H0)** | as duas políticas | nunca | o controle permanente da V2, na forma de `docs/DEFINICOES_V2.md`, seção 3: as mesmas ações de cuidado do atencioso nos mesmos ticks, sem elogio, bronca nem bola |

Com `w_bola` fixo e igual em todos os donos, a política é a mesma em todos os braços; o que a 1a sozinha e sem aprendizado testa é se **as
situações criadas pelo dono** já separam as vidas (decisões com a bola, humor, brincadeiras à noite). Os gates aqui são G1, G2 e G5
(seção 6) mais o descritivo: fração das decisões com bola no cenário e das brincadeiras com bola por dono, e o braço acoplado ao lado.
As perguntas 1a-pet e 1a-dono precisam de aprendizado e ficam para 4.2.

### 4.2 Junto com a L1 (A1 + L1)

Só depois de a 1a passar G1, G2 e G5 sozinha e de a L1 passar G3–G5 sozinha (na arena v1, sem bola; `docs/TAREFA_V2_L1_DECISAO.md`).
Aí a `PoliticaLobos` com aprendizado ligado recebe a entrada `bola`, e respondem-se as duas perguntas: **1a-pet** (sem dono no laço) e
**1a-dono** (2 × 2 bola × dono sobre G3, em sondas **com e sem** bola, e sobre G3-T, o acerto na tarefa ensinada de `DEFINICOES_V2`, seção 1).
É o teste da H1 inteira: aprendiz novo **e** ambiente onde o dono importa. O plano escreve que 1a-pet passar não é evidência para 1a-dono.

---

## 5. Web: pets v12

Versão reservada pelo coordenador (`docs/V2_RODADA_1.md`): **`VERSAO_PET = 12`** = v11 (lobos na web) + bola. Como as versões são cumulativas,
a bola na web só entra depois do porte dos lobos (v11, depois do L1). Ordem: Python primeiro (A1 sozinha), web depois.

O mínimo na tela (`web/app/src/`), sem mudar o motor dos v1–v11:

| onde | o quê |
|---|---|
| registro | o evento `d` de sempre com `por_bola` e `tirar_bola` (como `petisco` nos v4); pets v1–v11 recusam |
| motor (`motor.ts`) | a bola (`tick_posta`, `prazo`), a entrada na percepção dos lobos, a consequência em `brincar`; constantes `CBO` conferidas contra o Python (`constantes.test.mjs`) |
| tela do Pet | botão **Bola** ao lado de Brincar (põe; com bola no palco, vira Tirar); o sprite da bola no palco enquanto ela está lá; "brincou com a bola" no histórico |
| fala | o motivo "porque a bola estava lá" (fator `bola_no_cenario`, marcador único na tabela de expressão) |
| Cenários | os donos simulados com a regra da seção 1.5 (opcional na primeira entrega) |
| paridade | gabarito Python × TS de vidas com bola (`experiments/exportar_gabarito_bola.py`), como os da V21D e da confiança |

Nada no Tamer, nas arenas, nos itens ou na Fronteira.

---

## 6. Gates da 1a e o que o plano de análise vai precisar

Gates do plano da V2 (PROPOSTOS, não referendados), lidos para a bola:

| gate | critério | como se mede com a bola |
|---|---|---|
| G1 replay | vida bit a bit pelo log, Python (e web, no v12) | `reproduzir_ambiente` das vidas gravadas; teste |
| G2 equivalência | sem bola no log, `MotorAmbiente` = `MotorEducacao` e lobos sem aprendizado = instinto, byte a byte | rejogar vidas da V3 e da confirmatória; teste |
| G3 divergência | JSD entre donos coerentes ≥ 0,10 bit, IC fora de 0,02 (convenção do projeto, `DEFINICOES_V2` seção 1) | **só com a L1** (4.2); sondas com e sem bola; G3-T (acerto na tarefa ensinada) reportado ao lado |
| G4 legibilidade | fator explicável em ≥ 50% das decisões **aprendidas** (`DEFINICOES_V2`, seção 2, D3) | o fator `bola_no_cenario` conta quando o peso aprendido da bola mudou a escolha; a fração bruta (prior incluído) ao lado, sem gate; **só com a L1** |
| G5 separação do cuidado | a divergência se mantém sem mortes e sem lesão **e acima do braço só cuidado acoplado** (`DEFINICOES_V2`, seção 3) | por construção o humor não mata; medir mesmo assim: mortes e episódios de privação com bola = sem bola, por dono, e o contraste com o acoplado (descritivo na 1a sozinha; gate na A1 + L1) |
| G6 sem deriva | distância ao instinto não cresce sem limite em 14 dias | só com a L1 |

O que o `docs/PLANO_ANALISE_V2_A1.md` (commitado antes da run) vai precisar:

1. **Desenho da run sozinha:** o da arena v1 (`PROTOCOLO_ARENA_V1`: donos sintéticos, 224 interações em 14 dias) com `MotorAmbiente`,
   `ConfigBola.ligada`, os braços da seção 4.1; e o mesmo no motor de educação com lesões (para o G5 com morte possível).
2. **Sondas da divergência com a bola:** `metrics.divergencia_politicas` usa estados de sonda sem bola; precisa de um conjunto de sondas
   **novo** (função nova em `digilab/metrics.py`, sem mudar a atual), com cada estado duplicado com `bola = 0` e `bola = 1`. O hash de
   protocolo não cobre `metrics.py` (`CLAUDE.md`, pendências): o sha256 do arquivo vai no meta da run.
3. **Sementes:** faixa própria reservada pelo coordenador (calibração separada da validação, como sempre: as da L1 são 3101…3505 e
   4101…4505; a A1 não pode usar as mesmas para calibrar `w_bola` e `ganho_humor_bola`).
4. **O que se calibra e o que não:** `duracao_min`, `ganho_humor_bola`, `w_bola` e `bolas_por_dia` só nas sementes de calibração; os gates
   não mudam depois de ver a validação.
5. **Métricas descritivas (sem gate):** decisões com bola presente por dono; brincadeiras com bola por dia; fração à noite ou cansado;
   humor médio; orçamento gasto em bolas; e o mesmo no braço H0.
6. **Artefatos:** `artifacts_v2_a1/{calibracao,validacao}/`, com `pet.json` (1a-pet) e `dono.json` (1a-dono) como em `DEFINICOES_V2`, seção 4, e
   `artifacts_v2_a1_l1/interacao.json` para o desenho combinado.
7. **O braço só cuidado acoplado:** copiar as ações de cuidado do atencioso nos mesmos ticks exige gravar a vida do atencioso primeiro e rejogar o
   acoplado a partir dela (um dono sintético que lê um log): entra no plano como peça de código própria, com teste de que o acoplado tem as
   mesmas ações de cuidado e nenhum sinal de ensino nem bola.

---

## 7. O que fica fora

Comida posta e frutas com gosto hedônico e vício (candidata B do inventário; alavanca seguinte, `DEFINICOES_V2` seção 7 e D10); corpo 2D (posição, distância, colisão); mais de um objeto; sorteio na bola; a bola na arena ou no
combate; o Tamer; qualquer run nesta tarefa.

---

## 8. Recomendação

Entrar com a bola como **alvo de `brincar` interpretado numa camada por cima** (`MotorAmbiente`), com duas ações do dono no fim de
`AcaoUsuario`, uma entrada a mais na percepção dos lobos e uma regra de prior `bola_no_cenario`, sem rng nova e sem tocar em `AcaoPet`,
`engine.py` ou no bandit. Rodar a 1a primeiro sozinha (instinto, lobos sem aprendizado e o braço só cuidado), com plano de análise e
sementes próprias, e só depois juntá-la à L1 para o G3. Os quatro números (duração 60 min, ganho de humor 0,15, `w_bola` 3, 4 bolas por
dia) são chutes a calibrar, não parâmetros do desenho.

**Pergunta ao Matheus:** aprova este desenho (opção A, humor como consequência, sem rng nova, 1a sozinha antes da L1) para virar a tarefa de
implementação, ou prefere a opção B (ação interna dos lobos) ou outra consequência além do humor?
