# Plano de análise — V2, N4: frutas no mundo, sem aprendizado de política

Status: **registrado antes de qualquer run** (2026-10-04). Nada foi rodado para escrever este plano. Tarefa `docs/TAREFA_V2_N4_FRUTAS.md`;
definições `docs/DEFINICOES_FRUTAS_V2.md` (F1–F11 decididas em 2026-10-01, todas como recomendadas; F4 = gene próprio); decisões da bola
B1 e B2 (`docs/V2_RODADA_3.md`). Todo número abaixo é PROPOSTO, sem fonte, salvo quando aponta um artefato ou um símbolo de `digilab/config.py`.

**Pergunta.** Frutas no mundo, com nutrição e valor hedônico separados, criam escolhas do pet que a necessidade sozinha não explica, sem
passar pelo canal de cuidado? Nó N4 do `docs/ROADMAP_V2.md`: a condição **descasado** da pergunta maior. **O aprendiz da política fica
desligado** (como a bola sozinha): a política é o instinto, que passa a ler a presença das frutas; o que muda com a experiência são só os
dois registros hedônicos de cada fruta (incentivo e avaliação), que são registros derivados do ambiente, não pesos da política. Aprender
preferência pela **consequência** (o efeito no corpo) fica fora: é o N3.

## 1. O que entra no código (sem mudar nenhuma vida de antes)

| peça | onde | regra |
|---|---|---|
| três frutas `a`, `b`, `c`; ações do dono `oferecer_fruta_a/_b/_c` | fim de `events.AcaoUsuario`; `ACOES_FRUTAS` | só o motor das frutas aceita; os outros motores levantam erro (como a bola). Os donos da v1 sorteiam de `ACOES_V1`, então a canônica não muda |
| `MotorFrutas` | `digilab/frutas.py` (módulo novo), subclasse do `MotorAmbiente` (`digilab/ambiente.py`, que não muda) | frutas no cenário `{fruta: prazo}` fora do `Estado`; oferecer põe a fruta (ou renova o prazo); **oferecer não é contato**; a fruta some quando comida ou no prazo |
| entrada `fruta` na percepção | `policy.Observacao.fruta: float = 0.0` (campo com padrão, como `bola`) | o motor injeta o **maior incentivo** entre as frutas no cenário (0 sem fruta); o bandit e as sondas não o leem |
| instinto com as frutas | `frutas.PoliticaInstintoFrutas` (subclasse de `ambiente.PoliticaInstintoBola`), pelo gancho `_pesos_tempo_livre` | com a chave e fruta no cenário, na regra de tempo livre `comer` entra como candidato com peso `w_fruta × fruta` (a mesma chamada de `rng.choices`) e a regra se chama `fruta_no_cenario`. As regras de necessidade (sono, pedido, abandono, fome moderada) vêm antes, como hoje |
| sub-decisão de `comer` (F3) | `MotorFrutas._decisao_observada` | a política escolheu `comer` com frutas no cenário: o pet **escolhe uma** com probabilidade proporcional ao **incentivo** (sorteio na `rng_fruta`, derivada de `("fruta", semente)`, **uma chamada em toda decisão `comer`**, haja fruta ou não: números comuns entre braços), come, aplica o efeito, atualiza os registros; a fruta sai do cenário. Qualquer outra ação: ignora |
| genoma das frutas (F4, F5) | `frutas.genoma_frutas(semente)`, rng `derivar_semente("frutas-ovo", semente)`, fora do `Temperamento` | `neofobia` ~ U[0; 1] e `preferencia_inata[f]` ~ U[0,2; 1,0], nessa ordem (neofobia, depois a, b, c) |
| registros derivados (F1) | `MotorFrutas` | `incentivo[f]`, `avaliacao[f]`, `consumo_recente[f]`, `primeiro_contato[f]`, linhas `oferta` e `consumo` (definições, seção 1.3); o replay reconstrói tudo |
| `ConfigFrutas` | `digilab/config.py`; registro `protocol.PARAMETROS_FRUTAS_N4` (fora de todo hash) | `ligada` False por padrão: desligada, o `MotorFrutas` é o `MotorAmbiente` byte a byte e as ofertas no log levantam erro |
| métricas | `digilab/metrics.py`: `escolha_por_incentivo`, `comer_por_incentivo`, `saciedade_especifica` | seção 2 |
| não muda | `engine.py` (sha256), `AcaoPet`, o bandit, `policies/lobos.py` (chat B), `ambiente.py`, a bola, a web, `heranca.py` | — |

### 1.1 As contas (todas PROPOSTAS; as marcadas com * são calibradas)

- **Incentivo de partida** de uma fruta nunca comida: `preferencia_inata[f] × (1 − neofobia)`. A neofobia só age antes do primeiro consumo
  daquela fruta (F4).
- **Consumo recente** de `f`: começa em 0; a cada decisão do pet é multiplicado por `2^(−1/meia_vida_recente)` (`meia_vida_recente` = 16
  decisões = 4 h); cada consumo de `f` soma 1. Não depende da fome.
- **Avaliação** registrada no consumo de `f`: `max(0, preferencia_inata[f] − k_saciedade* × consumo_recente_antes[f])`. **A fome não entra**
  (F1, definição 2.3); comer `f` não mexe na avaliação das outras frutas.
- **Incentivo** depois do consumo: `incentivo[f] += taxa_incentivo × (avaliacao − incentivo[f])` (`taxa_incentivo` = 0,3). É o único caminho
  da avaliação até a escolha (definição 2.1). O **efeito** não entra no incentivo (seria aprender pela consequência: N3).
- **Efeito** de cada fruta comida, além do `comer` de sempre: `fome + nutricao` (0,10, igual em todas: a nutrição separada do gosto) e
  `humor + efeito_humor[f]`. Mundo **descasado** (o braço principal): a fruta de maior preferência inata do genoma tem `efeito_humor_ruim`
  (−0,10); as outras, `efeito_humor_neutro` (0,0). Variante **efeito igual** (F7): todas com 0,0. O efeito ruim fica no humor, fora de
  `Estado.em_privacao` (F6); só o efeito imediato.
- **Prazo** de uma fruta no cenário: `duracao_min`* desde a oferta (renovar reinicia).
- **Peso** de `comer` no tempo livre com fruta: `w_fruta`* × (maior incentivo entre as frutas no cenário).

### 1.2 As ofertas (B1, B2, F3)

O dono oferece por um **cronograma igual para os quatro donos**, fora do sorteio do dono aleatório (B1) e **fora do orçamento** (B2): a vida
gasta as 224 interações da arena v1 como sempre, e as ofertas vão direto ao motor, sem passar pelo `CanalDeInteracao`. Nos passos do dono das
**9h, 12h, 15h e 18h**, se o pet está acordado, o dono oferece o próximo conjunto de uma rotação fixa de 7:
`(a) (b, c) (a, b, c) (c) (a, b) (b) (a, c)`, que repete (4 de 7 ofertas com pelo menos duas frutas ao mesmo tempo). Como o cronograma não lê
o dono, a exposição às frutas só muda entre donos pelo sono do pet. Ninguém usa "tirar".

## 2. Gates (PROPOSTOS)

| gate | definição operacional | passa se |
|---|---|---|
| **G1 replay** | toda vida rejogada do log: estado, ações, rngs (ambiente, política, fruta), frutas no cenário e todos os registros derivados iguais | igualdade exata (teste e orquestrador) |
| **G2 equivalência** | (a) `MotorFrutas` desligado = `MotorEducacao` numa vida da V3 com lutas; (b) desligado com o instinto das frutas = `MotorComFeedback` com o `PoliticaInstinto`, 4 donos × 3 sementes; (c) ligado sem oferta no log = desligado; (d) a vida da A1 com a bola, pelo `MotorFrutas` com as frutas desligadas, é a da A1 | byte a byte nas quatro (teste) |
| **G-SEP (a escolha não é função só da fome)** | (i) **comer ou não**: nas decisões de tempo livre com fruta no cenário (todas com fome ≥ 0,45 pela regra do instinto), p(comer \| maior incentivo ≥ mediana da vida) − p(comer \| < mediana); (ii) **qual fruta**: nas decisões `comer` com ≥ 2 frutas no cenário, a fração em que o pet escolheu a de maior incentivo menos a esperada sem incentivo (a média de 1/n). Por semente, média dos 4 donos (dono sem a medida definida fica de fora e é listado); IC95 bootstrap sobre sementes | limite inferior do IC **> 0** em (i) **e** em (ii) |
| **G-SSE (saciedade específica sem a fome)** | sobre todos os `consumo` de uma semente (4 donos juntos), mínimos quadrados de `avaliacao ~ 1 + consumo_recente_antes + fome_antes`; por semente, β_recente e β_fome; IC sobre sementes | IC de β_recente todo **< 0** **e** IC de β_fome contém 0 |
| **G-F7 ensino × cuidado** | para cada vida do braço principal, o **acoplado**: o mesmo log sem `elogiar` e `repreender` (as mesmas ações de cuidado e **as mesmas ofertas** nos mesmos ticks; acariciar fica, D4), rejogado. Por semente, média dos donos de (saúde final do braço − saúde final do acoplado); mortes nos dois | IC da diferença de saúde **contém 0** **e** mortes iguais nos dois |
| descritivos | frutas − sem frutas: privação (`metrics.privacao_nas_decisoes`), humor, saúde final, mortes; custo do descasado (humor, descasado − efeito igual); escolhas por fruta; fração das escolhas na fruta que faz mal; trajetórias de incentivo × avaliação; neofobia × tempo até o primeiro consumo; a variante sem carinho do acoplado | — |

Sem aprendizado, G-SEP e G-SSE conferem que o **mecanismo** separa os registros e a necessidade como o desenho diz (com o tamanho do efeito);
não testam aprendizado. O G-F7 aqui só pode encontrar diferença por estado (elogio e bronca mexem no humor), não por ensino: é a linha de
base do critério para quando a política aprender. A pergunta 1a-dono continua **sem apoio na literatura** (D6) e fora desta tarefa.

Parada: um gate falhando na validação = **resultado negativo registrado**; nada se reajusta olhando a validação; a V2 segue (decisão de
2026-10-01).

## 3. Desenho

- **Vidas:** o da arena v1 (`PROTOCOLO_ARENA_V1`: 4 donos — atencioso, relapso, aleatório, incoerente —, 224 interações, 14 dias), pelo
  `MotorFrutas` com obediência, educação, lesões e bola desligadas, temperamento neutro, espécie `brasa`; o mesmo dono com a mesma rng em
  todos os braços. Braços: **`frutas`** (descasado, o principal), **`iguais`** (efeito igual), **`semfrutas`** (chave ligada, nenhuma oferta) e
  o **`acoplado`** (seção 2) de cada vida `frutas`, com a variante sem carinho.
- **Medidas** por um gravador no replay (como na A1): por decisão, regra, ação, fome, higiene, energia, humor, o valor `fruta` visto e as
  frutas no cenário; e os registros `oferta` e `consumo` do motor.
- **Sementes:** calibração **10101, 10202, 10303, 10404, 10505**; validação **11101, 11202, 11303, 11404, 11505**, uma vez. Nenhuma outra.
  Bootstrap percentil sobre sementes: 10 000 reamostras, semente 20261001, nível 0,95.
- **Replay:** toda vida gravada e reconstruída do disco antes de medir; divergência para tudo.
- **Meta:** sha256 de `digilab/frutas.py`, `ambiente.py`, `policy.py`, `config.py`, `metrics.py`, `events.py`, `engine.py` e do orquestrador;
  Python e plataforma; a `ConfigFrutas` usada.

## 4. Calibração (10101…10505)

Grade: `w_fruta` {1, 3, 6} × `k_saciedade` {0,2; 0,5; 1,0} × `duracao_min` {60, 120} = 18 pontos, só o braço `frutas` (o `semfrutas` não
depende do ponto). **Escolha, decidida aqui:** entre os pontos com p(comer | fruta no cenário, tempo livre) médio em **[0,30; 0,80]** e os três
gates G-SEP, G-SSE e G-F7 passando, o de **maior limite inferior do G-SEP(i)**; empate → menor `w_fruta`, depois menor `k_saciedade`, depois
menor `duracao_min`. Sem ponto que passe: o de maior limite inferior do G-SEP(i), e o relatório diz que a calibração não fechou. O ponto vai
para `experiments/configs/v2_n4/validacao.json` e para os padrões da `ConfigFrutas`. Só nele rodam a variante `iguais` e o acoplado.

## 5. Validação (11101…11505, uma vez)

`python experiments/run_v2_n4.py --config experiments/configs/v2_n4/validacao.json`: todos os braços, todos os gates e descritivos em
`artifacts_v2_n4/validacao/` (`resultado.json`, `vidas.json`, `so_cuidado.json`, `meta.json`, `vidas/`). Resultado em
`docs/RESULTADO_V2_N4.md` e seção própria no `CLAUDE.md`.

## 6. O que não entra

Aprender a preferência pela consequência (N3), vício (N9, F9), a regra das frutas nos lobos (`lobos.py`, chat B), a herança dos genes das
frutas (os filhos não entram nesta run; o `Genitor` não muda), modo livre gravado na escolha da fruta, números de balanceamento do produto,
a web, o mundo mutável.
