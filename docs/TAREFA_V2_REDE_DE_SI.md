# TAREFA V2 — DIGICORPO (a rede de si): o automodelo em observação (etapa 2 do ego) (2026-10-08)

> **V2, congelado em 2026-10-30** (tag `v2-final`). O estado em que este documento fica na V3 está em `docs/FECHAMENTO_V2.md`; o
> plano da V3, em `docs/PLANO_V3.md`.

**Nome (2026-10-08):** a rede de si se chama **Digicorpo** (`docs/DEFINICOES_CORPO_V2.md`, seção 8). O código, o arquivo desta tarefa e
o prefixo das sementes continuam `rede_de_si`. As decisões já registradas (E-6, RS-7) ficam com a redação delas.

Coordenador: Gerente. Workers: B (a rede e o embrulho), D (a bancada e as medidas), A (a troca da digestão e, se o G-OBS pedir, o motor) e C (o plano).
Worktree e branch de cada etapa: `v2-rede-de-si-<etapa>`. Status: **ABERTA.** **RS-1 a RS-7 DECIDIDAS pelo Matheus em 2026-10-08, todas pela
recomendação** (seção 8).

**O que já está decidido:**
- **E-1:** o automodelo tem corpo e é aprendido por uma rede. O pet não lê a sonda; a sonda avalia;
- **E-3:** o cérebro é o A;
- **E-6:** a Decisão aprende por reforço, a rede de si por erro de previsão, e nenhuma outra peça aprende. A recomendação da redação está
  em `docs/futuro/ego_existencia.md`, seção 3;
- **E-8:** a rede em inteiros, como o cérebro A;
- **E-11:** sem catálogo de perguntas. A questão interna é a etapa 4 do ego e fica fora daqui;
- **D-7** de `docs/DEFINICOES_CORPO_V2.md`: o automodelo é avaliado contra a persistência, a linha de base obrigatória, e contra a média
  histórica.

**Fontes:** `docs/futuro/ego_existencia.md`, seções 3, 7 e 9 (a etapa 2); `docs/DEFINICOES_CORPO_V2.md`, seção 6; `docs/TAREFA_V2_CORPO_DRIVES.md`
(os receptores). O plano é `docs/PLANO_ANALISE_V2_REDE_DE_SI.md`, commitado antes de qualquer run.

## 1. Pergunta

**O Digicorpo aprende o próprio pet?**
- **O corpo:** ela prevê as leituras dos receptores do corpo, a n decisões, melhor que copiar o presente (a persistência) e que a média
  histórica.
- **A mudança:** ela se adapta quando o corpo muda.
- **A autoria:** ela estima a própria escolha em situações alteradas ("sem o pedido, eu teria comido?", "eu faria isso ao nascer?") de
  forma calibrada contra a sonda.

**Tudo em observação:** a rede não influencia a escolha nem a fala. É o degrau 2 da seção 9 do ego. Entrar na decisão é a etapa 3.

## 2. A rede do Digicorpo (desenho, PROPOSTO)

**Onde fica.** Num módulo novo, `digilab/rede_de_si.py`, separado do cérebro. Ela observa por um **embrulho somente leitura** da política
(`PoliticaComRede`, como o `PoliticaComMotivo`):
- o embrulho repassa ao cérebro tudo, sem mudar nada;
- ele entrega à rede só o que o pet tem: a observação da decisão (`obs.corpo`, os receptores; o contexto do mundo que a observação já
  traz), a ação que o próprio pet escolheu e as observações seguintes.

O embrulho não muda o motor. O A entra só com a troca da digestão do plano (etapa 2b) e, se o G-OBS mostrar que o embrulho muda a vida, no motor.

**As entradas (sem acesso privilegiado):**
- os receptores do corpo, na escala S (os drives de hoje, os novos e os gestos que existirem: `PercepcaoCorpo`);
- a ação escolhida;
- o contexto que a observação já mostra (as frutas no cenário, o pedido vigente);
- a idade em faixas (o pet sabe há quanto vive pelo próprio relógio: as decisões que já viveu).

**O que fica de fora:** o químico, o `Estado`, os pesos do cérebro, a regra do instinto que decidiu e a sonda.

**A cabeça do corpo:** para cada receptor r e cada horizonte n (RS-1: n ∈ {1, 4, 16} decisões, ou seja, 15 min, 1 h e 4 h; PROPOSTO), a
previsão é `p = corte(div_arred(Σ w_j · x_j, S), 0, S)`.
- `x` reúne os receptores de agora, a ação em um-quente × S, o contexto × S e o viés S;
- o prior é a **persistência** (RS-2): o peso do próprio receptor é S e os outros são 0. A rede nasce prevendo "o depois é como agora";
- o aprendizado é o LMS em inteiros, depois de n decisões, quando a leitura real chega: `w_j += div_arred(passo · (real − p) · x_j, S · S)`,
  cortado num teto.

**A cabeça da autoria:** a probabilidade de cada ação em S, por um modelo linear das entradas mais "pedido vigente" e as faixas de idade.
- o alvo é o um-quente da ação que o pet escolheu, aprendido pelo mesmo LMS;
- **as estimativas contrafactuais** são a mesma conta com o contexto alterado: sem o pedido (pedido = 0) ou ao nascer (idade = a primeira
  faixa).

**Os números:**
- **os pesos:** as duas cabeças somam **menos de mil** (o B fixa o layout e a contagem, e o teste confere);
- **a conta:** só inteiros, sem função transcendental (E-8);
- **o acaso:** nenhuma rng, porque a rede não sorteia.

**O erro exposto (E-11, para a etapa 4).** A rede guarda, por receptor e horizonte, o erro absoluto recente (uma média em inteiros) e a
**surpresa**: o erro de agora contra o recente. Ninguém lê isso nesta tarefa. É o gatilho que a questão interna vai usar.

## 3. Depende de

- Na `main`: o corpo com os drives novos e os gestos (etapa 6 do corpo), o `MotorCorpo` nos mundos e a sonda do pedido no cérebro A (N7).
- Nada do mundo físico é pré-requisito: o plano usa os mundos da bola e das frutas (RS-4).

## 4. Etapas e donos

| etapa | dono | arquivos | entrega | gates |
|---|---|---|---|---|
| **0. gabaritos** | B | `tests/gabaritos/rede_de_si_vidas_de_hoje.json` | as vidas do P1 com o corpo nos mundos do plano, gravadas **antes** | — |
| **1. a rede** | B | `digilab/rede_de_si.py`, a `ConfigRedeDeSi` no fim de `config.py` | as duas cabeças, o prior da persistência, o LMS em inteiros, as estimativas contrafactuais e o erro exposto | **G-INT** (AST: só inteiros, sem `math`); **G-PESOS** (< 1000); conta exata de um passo do LMS; com `passo` 0, a previsão é a persistência para sempre |
| **2. o embrulho** | B | `digilab/rede_de_si.py` (`PoliticaComRede`), `digilab/motivo.py` se precisar | a rede observando a vida pelo embrulho | **G-OBS:** com a rede ligada, a vida é byte a byte a de sem a rede (log, estado, ações, rngs, estado interno do cérebro), nos gabaritos da etapa 0. **G-RECEPTOR:** a rede só importa `config` e `events`; mudar um químico sem receptor não muda nada na rede. **G1-REDE:** o estado da rede é refeito bit a bit pelo replay da vida |
| **2b. a troca da digestão** | A | `digilab/motor_corpo.py` | a `taxa_digestao` trocada num tick e gravada no registro, como a troca do mutável (RS-3) | sem a troca, a vida de hoje byte a byte (os gabaritos do corpo); o replay refaz a troca (G1) |
| **3. a bancada** | D | `experiments/bancada_v2.py`, `digilab/metrics.py`, `experiments/configs/v2_rede_de_si/` | a chave `rede_de_si`; a rede congelada num tick e o oráculo, por replay e só na bancada; os braços novos do plano (P1-c-lenta, P1+ped-c); as medidas do plano (o erro por receptor e horizonte, as linhas de base, a adaptação, o Brier da autoria contra as sondas); as faixas e o prefixo `rede_de_si` | G1 de toda vida com a rede; as linhas de base conferidas em dados com resposta conhecida; a sonda lida do cérebro e nunca entregue à rede; o P1+ped-c monta (o corpo e o pedido juntos) |
| **4. o plano** | C | `docs/PLANO_ANALISE_V2_REDE_DE_SI.md` | — | commitado antes de qualquer run (vai neste PR) |
| **5. a web** | A | depois, com o porte do cérebro A (o v11 está pausado) | a rede em TypeScript | G-PAR |

**A ordem:** 0 → 1 → 2 → 3, com a 2b em paralelo à 1 e à 2. O plano já está pronto. A etapa 5 fica para quando o produto voltar.

Um PR por etapa, com o relato no corpo. **O merge é do Matheus.**

## 5. Experimento e gate

- **O plano:** `docs/PLANO_ANALISE_V2_REDE_DE_SI.md`.
- **As sementes propostas:** 43101…43505 (calibração e piloto) e 44101…44505 (validação), com o prefixo `rede_de_si`. O D as registra.
- **GPU:** não.

## 6. Fronteiras (o que não muda)

- **`engine.py`, o `AcaoPet`, o cérebro e o corpo:** não mudam. A rede é um módulo novo, e o embrulho só lê. A única mudança no motor é a troca da digestão (2b), atrás de chave.
- **A vida:** com a rede ligada, é byte a byte a de sem ela (G-OBS).
- **A sonda nunca entra na rede:** só a bancada a lê, para avaliar.
- **Nenhuma pergunta, fala ou catálogo** (E-11, etapa 4 do ego).
- **Os pets v1 a v10 e a web de hoje:** iguais.

## 7. Fora desta tarefa

- **A rede na decisão** (a etapa 3 do ego).
- **As perguntas e a questão interna** (a etapa 4, E-11).
- **O diálogo e a fala** (as etapas 5 e 6).
- **O dano de órgão e a troca de estágio que muda o corpo:** esperam a 1b. Até lá, a mudança do corpo do plano é a da RS-3.
- **A web.**

## 8. Decisões do Matheus

**DECIDIDAS em 2026-10-08: RS-1 a RS-7, todas como recomendado.**

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| RS-1 | Os horizontes da cabeça do corpo | **n ∈ {1, 4, 16} decisões** (15 min, 1 h, 4 h) | um horizonte só: n = 1 é quase a persistência, e um n longo sozinho mistura o efeito da ação com o do dono |
| RS-2 | O prior da cabeça do corpo | **a persistência** (o peso do próprio receptor em S) | prior zero: a rede começa pior que a linha de base, e "bater a persistência" passa a medir também o tempo até alcançá-la |
| RS-3 | A mudança do corpo para medir a adaptação, até a 1b | **a digestão lenta ligada na metade da vida** (a `taxa_digestao` da `ConfigCorpo`, CD-3, trocada num tick como a troca do mutável; etapa 2b), mais os **tapas** do `DonoComGestos` como perturbação do estresse | esperar a 1b: a adaptação fica sem medida até o dano de órgão existir. A troca de estágio de hoje não muda o corpo, e não haveria o que adaptar |
| RS-4 | Os mundos | **a bola com o corpo** (os receptores novos e o brincar) para a cabeça do corpo, e **o `iguais_frutas` com o pedido do N7** para a autoria (a sonda do pedido existe ali) | um mundo só: sem o pedido não há a sonda "sem o pedido, eu teria comido?" |
| RS-5 | Como a rede observa | **um embrulho somente leitura da política**, sem mudar o motor | ganchos no motor: tocam o `MotorCorpo` e o `MotorMundo`, com mais risco no G-OBS |
| RS-6 | As faixas de sementes | **43101…43505** e **44101…44505** | uma colisão tira o "novo" das unidades |
| RS-7 | A redação da E-6 | registrar no `CLAUDE.md`, na seção da etapa 2, quando o código entrar: "a Decisão aprende por reforço, a rede de si por erro de previsão, nenhuma outra peça aprende" | sem registro, a regra antiga ("só a Decisão aprende") fica escrita e contradita pelo código |

## Etapa 2b, a troca da digestão (A, 2026-10-13) — GATES PASSAM

RS-3 do plano (seção 3): a digestão lenta do P1-c-lenta a partir do fim do dia 7, gravada no registro como a troca do mutável. Sem run; só
as sementes dos testes. Mudaram `digilab/motor_corpo.py`, a `ConfigTrocaDigestao` no fim de `config.py`, a bancada (o nó saiu) e três
testes. `engine.py`, `corpo.py`, os cérebros, a rede e a web não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **No motor:** `MotorCorpo(..., troca_digestao=(tick, taxa))`, só com o corpo e a digestão. No começo do primeiro tick em ou depois do
  pedido (antes da decisão e do passo daquele tick), a `taxa_digestao` do motor e do corpo passa à nova; o grafo do corpo é refeito com
  ela e conferido de novo. A troca fica em `troca_digestao` (o tick, o pedido, a taxa antes e depois) e no `estado()`; o replay a refaz
  pela mesma fábrica. Sem o pedido, nada muda.
- **A taxa lenta:** `ConfigTrocaDigestao.taxa_lenta` = C // 8 (PROPOSTA, a do plano; o adendo 1 escolhe da grade). Na config da bancada, a
  chave `"digestao_lenta": {"taxa_lenta": ...}`.
- **Na bancada:** o `NOS_PENDENTES` ficou vazio. O P1-c-lenta recebe a troca no `tick_troca_digestao` (o fim do dia `dias // 2`), e a
  medida da rede confere que a troca foi a pedida (e que nenhum outro braço trocou), falhando alto se não.
- **Gates** (`tests/test_troca_digestao.py`): sem a troca, nenhuma chave nova (e os gabaritos do corpo, na suíte); a troca no tick, com o
  grafo refeito; antes do tick, a vida é a do P1-c (o log e as ações); depois, a digestão por tick não passa da lenta e a lenta morde; G1
  pelo `conferir_replay`; as falhas altas; o P1-c-lenta na bancada e a chave da config. O teste do braço em `test_bancada_rede_de_si.py`
  passou de "espera o nó" a "roda e mede a adaptação".

## 9. Estado das etapas

### Etapa 3, a bancada (W-BANCADA-REDE, #302, 2026-10-13) — mergeada

O resumo da etapa está na seção "V2, W-BANCADA-REDE" do `CLAUDE.md`.

### A calibração e o piloto, preparados (REDE-DE-SI-CALIBRACAO, 2026-10-13) — PRONTOS, NÃO RODADOS

O plano é `docs/PLANO_ANALISE_V2_REDE_DE_SI.md`, seções 5, 6, 8 e 11, com PRS-1 a PRS-5 decididas. Só a fumaça rodou, nas sementes dos
testes. **A run nas bases 43101…43505 precisa do sim do Matheus.** As interpretações estão em `docs/REGISTRO_DESVIOS.md`.
- **O orquestrador** (`experiments/run_v2_calibracao_rede_de_si.py`), numa run só:
  - **a grade:** o P1-c no mundo da bola, com o atencioso e os gestos, 14 dias, nas 20 unidades (K_u = 4, prefixo `rede_de_si`), com o
    `passo` em {S/64, S/16, S/4}. As três vidas de uma unidade são a mesma vida byte a byte, porque a rede só observa (G-OBS, falha alto);
  - **a regra:** fica o menor MAE_rede(1) nos dias 1 a 7, sem o susto. Sai da grade o `passo` com peso no teto em mais da metade das vidas;
    sem nenhum que fique, vale o menor. A regra não lê a persistência, a média nem contraste nenhum;
  - **a taxa lenta e o P1-c-lenta:** ficam atrás do nó `digestao_lenta` (a etapa 2b, do A), declarados no resultado;
  - **o piloto:** no `passo` escolhido, roda P1-c, P0-c e P1-c-tapa na `bola` e P1+ped-c no `iguais_frutas`, gravados e rejogados do
    disco, e medidos;
  - **a margem:** `Δ_SI` = ½ × [MAE_pers(4) − MAE_oráculo(4)] no P1-c. Com a distância ≤ S/128, a validação não roda e o plano volta ao
    Matheus;
  - **o N:** o menor K_u de 4 a 10 com poder simulado ≥ 0,8 no G-SI. O poder do G-MEDIA, G-AUT-PED e G-AUT-NASC sai no N escolhido, só
    como relato; o do Brier usa o N efetivo;
  - **o custo** da validação.
  - Grava `escolha.json`, `grade/grade.json`, `piloto/medidas.json`, `resultado.json` e `meta.json` (com os sha256 de `rede_de_si.py`,
    `lobos.py`, `corpo.py`, `config.py` e `engine.py`). Recusa a pasta que já existe e as bases da validação.
- **A config** (`experiments/configs/v2_rede_de_si/calibracao.json`):
  - o cérebro A no ponto da K2, com a montagem completa;
  - o corpo do regime "corpo" com o gasto do passo 0 fino (adendo 5 do corpo, `m_gasto` 4/5) e os drives novos nos números PROPOSTOS.
  - A fumaça (`fumaca_calibracao.json`) é a mesma config, nas sementes dos testes, com 3 dias.
- **Comando** (depois do sim):
  `python experiments/run_v2_calibracao_rede_de_si.py --config experiments/configs/v2_rede_de_si/calibracao.json --processos 6`.
  - A grade tem 60 vidas e o piloto 80.
- **Achado nas sementes dos testes** (não é resultado; vidas de 14 dias, sementes 101 e 202, dias 8 a 14, n = 4):

  | | MAE | a distância persistência − oráculo |
  |---|---|---|
  | a persistência | 48 | |
  | a rede no `passo` 16 (S/64) | 41 a 43 | |
  | o oráculo no `passo` 16 (S/64) | 43 a 45 | positiva |
  | o oráculo no `passo` 64 (S/16) | 69 a 74 | negativa |

  - O oráculo tem 14 químicos a mais na entrada e o mesmo `passo` da rede. Com o `passo` 64 ele deixa de ser um teto, e a distância
    fica negativa.
  - Se a regra escolher o 64, a validação não roda pela seção 6 por causa do passo do oráculo, não porque a persistência seja o teto.
  - A decisão é do Matheus, antes da run: manter a letra, ou dar ao oráculo o próprio passo (o menor MAE numa grade dele).
- **Testes:** `tests/test_calibracao_rede_de_si.py`, 17:
  - a config contra o plano, a K2 e o passo 0, e as recusas;
  - a regra, a margem, o N efetivo e o poder em dados com a resposta conhecida;
  - a medida da grade numa vida real: com o `passo` 0, a rede é a persistência;
  - a fumaça inteira.
  - O teste das faixas da rede de si (`tests/test_bancada_dois_pets.py`) passou a aceitar a faixa de calibração nas configs do próprio
    plano.
