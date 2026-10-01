# Plano de análise — V2, L1: o lobo de decisão aprende com o feedback como vantagem

Status: **registrado antes de qualquer run** (2026-10-01; revisão 2 no mesmo dia, antes da calibração válida: ver seção 8). Nada foi
rodado para escrever este plano. Os números citados vêm de artefatos em disco, e cada um aponta o arquivo; os valores sem fonte estão
marcados PROPOSTO. Os gates G3–G6 são os do `docs/PLANO_V2_PESQUISA.md` (fase 1) com as definições D1–D4 de `docs/DEFINICOES_V2.md`
(aprovadas pelo Matheus em 2026-10-01); as definições operacionais ficam fixadas aqui. **A validação só roda depois do referendo do
Matheus** sobre os gates (`docs/TAREFA_V2_L1_DECISAO.md`, seção 2).

**Natureza.** Nó L1 da fase 1b (hipótese H1). A L0 (`PoliticaLobos`, PR #108) mostrou que a política com lobos, com o aprendizado
desligado, é o instinto byte a byte. A L1 liga o aprendizado **só no lobo de decisão**, com uma atualização que depende da política atual
(o feedback do dono no lugar da vantagem: MacGlashan et al., COACH, `arXiv:1701.06049`, VERIFICADA na skill `literatura-digilab`), e
pergunta se donos coerentes produzem políticas distinguíveis entre si e do aleatório, com decisões explicáveis, **e se o que se aprende é
a tarefa ensinada** (G3-T), **separado do cuidado** (só cuidado acoplado) e **legível por causa dos lobos** (controle sem lobos).

## 1. Ponto de partida (conferido nos artefatos)

| achado | número | artefato |
|---|---|---|
| a L0 reproduz o instinto byte a byte (G2) e rejoga bit a bit (G1) | 23 testes | `tests/test_lobos.py` (PR #108) |
| divergência entre donos com o bandit da v1 | JSD média entre braços 0,020406 bit; dentro do braço 0,01306 | `artifacts_ablacao/divergence.json` |
| divergência entre donos sem aprendizado (instinto) | exatamente 0,0 nos 150 pares | `artifacts_ablacao/divergence.json` |
| legibilidade do bandit na vida (regra de honestidade) | 13,3% (relapso) a 18,5% (atencioso) das decisões com fator | `artifacts_expressao/legibilidade.json` |
| legibilidade do instinto na vida | 34% (atencioso) a 76% (relapso) | `artifacts_expressao/legibilidade.json` |
| o dono pesa pelo cuidado, não pelo ensino (v1) | pergunta encerrada | `docs/LEITURA_CONSOLIDADA_DONO.md` |

## 2. A mudança testada: a regra de atualização

A `PoliticaLobos` da L0 decide assim: o lobo de impulsos (as regras do instinto) dá a regra `r` e os candidatos; o lobo de
decisão dá a cada candidato `a` o peso efetivo `w_eff(a) = Σ_j (w[r][a][j] / S) · x_j`, com pesos inteiros `w` em escala
`S = 2^10` e entradas `x` da percepção (viés, `Estado.vetor`, tempo sem cuidado normalizado); a ação sai por sorteio
proporcional, `p(a) = w_eff(a) / Σ_b w_eff(b)`.

**L1, só o lobo de decisão muda** (`ConfigLobos.aprendizado_ligado = True`). A cada sinal `f` do dono creditado a uma decisão
(regra `r`, entradas `x`, probabilidades `p` **da política no momento da decisão**, ação escolhida `a*`):

```
Δw[r][a][j] = arred( f_S · passo · X_j · (S·1[a = a*] − P_a) / (S · S · W_a) )   para cada candidato a e entrada j
```

- `f_S = f · S` (elogio +S, bronca −S; chamado atendido com latência L: `(1 − L/janela)·S`; chamado ignorado:
  `recompensa_pedido_ignorado · S`), `X_j = arred(x_j · S)`, `P_a = arred(p(a) · S)`, `W_a = max(1, arred(w_eff(a) · S))`.
  Tudo inteiro; `arred` arredonda para o inteiro mais próximo, meio longe do zero (simétrico, sem viés de sinal).
- Em unidades de 1,0: `Δw ≈ f · passo · x_j · (1[a = a*] − p(a)) / w_eff(a)`. É a direção do gradiente de
  `log p(a*)` da política proporcional (`∂ log p(a*)/∂w[a][j] = (x_j/S)·(1[a = a*] − p(a)) / w_eff(a)`), com o sinal do dono
  no lugar da vantagem (COACH). **A dependência da política atual está no termo `(1 − p(a*))`:** um elogio a uma ação já
  provável mexe pouco; uma bronca numa ação improvável mexe pouco. O bandit da v1 somava recompensa fixa.
- **Um sinal escalar** (`f ∈ {+1, −1}` e o chamado como hoje). Sem recompensa multidimensional (H-REINF-001 fica fora).
- **Janela de crédito igual à da v1:** elogio e bronca creditam a última decisão; cada `chamar_atencao` fica pendente e o
  primeiro cuidado do dono dentro da `janela_latencia_ticks` paga `1 − L/janela`; pendente que expira paga
  `recompensa_pedido_ignorado`. Os valores são os da `ConfigBandit` (120 ticks; −0,5), copiados para a `ConfigLobos`.
- **Teto:** `|w − w0| ≤ teto` por peso (corte simétrico em torno do prior). **Piso:** com o aprendizado ligado,
  `w_eff(a) = max(piso_peso / S, Σ…)` nos candidatos, para o sorteio e o gradiente nunca encontrarem peso ≤ 0. Com o
  aprendizado desligado nada disso roda: a L0 continua byte a byte o instinto (os testes G1/G2 da L0 ficam).
- Regras com um candidato só (sono, pedido, abandono) não têm o que aprender: `1[a = a*] − p(a) = 0`. O aprendizado age
  na fome moderada e no tempo livre, as duas regras com sorteio.

**Parâmetros** (`ConfigLobos`, todos PROPOSTOS; registro em `lobos.PARAMETROS_LOBOS_L1`):

| parâmetro | valor | origem | calibrado? |
|---|---|---|---|
| `passo` | grade {32, 64, 128, 256, 512} = S/32 … S/2 | sem fonte | **sim** |
| `teto` | grade {1024, 2048, 4096} = 1·S, 2·S, 4·S | sem fonte | **sim** |
| `piso_peso` | 64 = S/16 | sem fonte; da ordem do `piso_prior` do bandit (0,05) | não |
| `janela_latencia_ticks` | 120 | `ConfigBandit.janela_latencia_ticks` | não |
| `recompensa_pedido_ignorado` | −0,5 | `ConfigBandit.recompensa_pedido_ignorado` | não |
| `recompensa_elogio`, `recompensa_repreensao` | +1, −1 | `ConfigBandit` | não |

### 2.1 O controle de capacidade equivalente sem lobos (D2)

`digilab/policies/camada_unica.py`, `PoliticaCamadaUnica`: **os mesmos 490 pesos inteiros, as mesmas 10 entradas, a mesma regra de
atualização (a função é a mesma, `lobos.atualizar_pesos`), o mesmo piso e teto, a mesma janela de crédito e as mesmas sementes**, numa
única camada de decisão sobre as 7 ações, sem impulsos: toda ação é candidata em toda decisão, e nenhuma regra do instinto existe.
- Para ter 490 pesos sem lobos, a tabela é `w[c][a][j]` com `c` = **sétimo do dia** (7 fatias de 1440/7 ticks pela hora do dia; é um
  índice de contexto sem semântica de regra, só para igualar a contagem; a L0 tem 7 regras × 7 ações × 10 entradas).
- **Prior:** em todo contexto, os coeficientes do tempo livre do instinto (ocioso 3; explorar 2 + 2·energia; brincar 1 + 3·humor;
  chamar 1) e **1,0** para dormir, comer e emburrar (as ações que o instinto só toma por regra). O controle não conhece sono, pedido nem
  abandono: começa com um pet que não dorme por regra. É o preço de não ter lobos; está registrado e é o que D2 pede ("sem módulos").
- **Atribuição por pseudo-lobos:** o motivo do controle usa a mesma regra de honestidade (seção 4.1) com a mesma decomposição por
  entrada (os "grupos de entrada" são as 10 entradas nomeadas); "o impulso decidiu" vira "o prior decidiu".

## 3. Desenho

- **Vidas:** o da arena v1 (`PROTOCOLO_ARENA_V1`: 4 donos sintéticos — atencioso, relapso, aleatório, incoerente —,
  orçamento 224 = 16/dia × 14 dias, 14 dias, `MotorComFeedback`, passo do dono da `ConfigDonos`), com as políticas por
  dono, **o mesmo dono com a mesma rng em todas** (`rotulo_dono`, como na ablação):
  - **lobos** — a `PoliticaLobos` com o aprendizado ligado (o braço testado);
  - **instinto** — a `PoliticaInstinto`: controle sem aprendizado (piso do G3-T);
  - **bandit** — a `PoliticaBandit` da v1 nas mesmas sementes: referência da v1, não é braço de pesquisa;
  - **controle** — a `PoliticaCamadaUnica` (seção 2.1), só no ponto escolhido da calibração e na validação.
  Rótulo `<dono>-<política>@<semente>`.
- **"Só cuidado" acoplado (D4, V2-H0):** para cada vida `atencioso-lobos@s`, a vida **`atencioso-cuidado@s`** = o **mesmo log** sem os
  eventos `elogiar` e `repreender` (as mesmas ações de cuidado — alimentar, limpar, brincar, acariciar e, onde existirem, levar ao
  banheiro e tratar lesão — nos mesmos ticks; os avanços de tempo iguais), rejogado com uma `PoliticaLobos` aprendiz nova e a mesma
  semente. Variante de sensibilidade `atencioso-cuidado-semcarinho@s`: também sem `acariciar`. O volume de interações de cada um é
  relatado (o acoplado tem menos: os sinais somem). O acoplado só aprende pelo canal implícito do chamado.
- **Sem torneio.** Os gates são todos sobre a política; a luta na arena v1 media "pet melhor", pergunta encerrada em
  `docs/LEITURA_CONSOLIDADA_DONO.md`. O torneio e as métricas de vitória da arena v1 **não rodam** (`docs/REGISTRO_DESVIOS.md`).
- **Sondas de divergência:** as da arena v1: 64 estados, 200 amostras por estado, `semente_sonda` 9001, números aleatórios
  comuns (`metrics.estados_sonda`, `distribuicoes_de_acao`, `divergencia_politicas`, `jsd_bits`). Métricas só em `digilab/metrics.py`.
- **Sementes:** calibração **3101, 3202, 3303, 3404, 3505**; validação **4101, 4202, 4303, 4404, 4505**, uma vez só, depois do
  referendo. Nenhuma outra. Bootstrap percentil sobre sementes: 10 000 reamostras, semente 20261001, nível 0,95.
- **Replay:** toda vida é gravada (`vidas/*.jsonl`, `*.politica.json`) e **reconstruída do disco** antes de qualquer medida;
  divergência no replay para tudo. O `politica.json` é gravado **antes** das sondas (a sonda chama `agir` e acrescenta
  motivos ao registro da política; nada de decisão ou aprendizado muda com a sonda).
- **Meta da run:** sha256 de `digilab/policies/lobos.py`, `camada_unica.py`, `digilab/config.py`, `digilab/motivo.py`,
  `digilab/metrics.py` e do `engine.py`; versão do Python e plataforma; os parâmetros da `ConfigLobos` usados.

### 3.1 Braço próprio do G5: o motor de educação com lesões

No desenho da arena v1 **não há morte nem lesão** (nem luta): o G5(a) vale ali por construção, e isso fica registrado. Para
medir o que a tarefa pede, um braço à parte, **só com os parâmetros escolhidos na calibração** (não entra na grade):
- 4 donos × 5 sementes, `MotorEducacao` com educação e lesões ligadas, duração "teste", orçamento de
  `treino_vida.orcamento_treino` (o da V3), sparring da V3 (`run_educacao.ticks_sparring`, `PetDaVida`, rival da mesma linha),
  espécie e temperamento do ovo (`evolucao.ovo`, `temperamento.sortear`). A política é a `PoliticaLobos` aprendiz
  (`fabricas_educacao` ganha um parâmetro opcional `politica_fabrica`; o padrão continua o bandit da personalidade, bit a bit).
- Medida: a mesma divergência do G3, com a política **final** de cada pet (morto: a política no tick da morte), em duas
  leituras: (i) todos os pets; (ii) só os pares em que **nenhum** dos dois pets teve lesão nem morte. O acoplado não roda aqui (as
  ações de cuidado copiadas incluem "tratar lesão" num pet que pode não estar lesionado: o motor recusaria; fica registrado).

### 3.2 Norma de reação (D4): ovo × ambiente × condição

Sub-desenho para separar nível de sensibilidade ao ambiente (Dingemanse et al., `10.1016/j.tree.2009.07.013`), nos moldes do E1:
- **Ovos:** as 5 sementes do conjunto (a rng da política e a rng do dono acoplado vêm delas). **Ambientes:** 4 sementes derivadas,
  `derivar_semente("ambiente-v2-l1", conjunto, k)`, k = 1…4, que alimentam a **rng de ambiente do motor** e a rng do dono (`MotorComFeedback`
  com a rng de ambiente trocada depois da construção; `engine.py` intocado; `rotulo_dono = "atencioso#<k>"`).
- **Condições:** **ensino** (`atencioso-lobos`), **só cuidado** (o acoplado do mesmo log, seção 3) e **instinto** (referência). 5 × 4 × 3 =
  60 vidas (20 delas são replays do log filtrado).
- **Medidas y por pet:** G3-T (acerto na tarefa, média dos 7 últimos dias) e JSD contra o instinto.
- **Modelo (regressão conjunta, Finlay–Wilkinson):** o índice do ambiente `z_r` é a média de `y` de todos os pets (todas as condições e
  ovos) no ambiente `r`, centrada; para cada (ovo, condição) ajusta-se `y = α + β·z_r` por mínimos quadrados sobre os 4 ambientes.
  **Intercepto `α` = nível; inclinação `β` = sensibilidade ao ambiente.** Efeito do ensino: `Δα = média_ovo(α_ensino − α_cuidado)` e
  `Δβ = média_ovo(β_ensino − β_cuidado)`, IC bootstrap sobre os 5 ovos (10 000, semente 20261001). Função nova `metrics.norma_de_reacao`,
  biblioteca padrão, com teste. Sem gate: é a leitura que D4 pede; `Δβ > 0` com IC fora de zero diria que o ensino deixa o pet mais
  dependente do ambiente, `Δβ < 0` menos.

## 4. Métricas e gates (PROPOSTOS)

"Donos coerentes" = **atencioso e relapso**: são os dois que aplicam a regra de feedback coerente (`donos.julgar_acao`); o incoerente
sorteia a polaridade e o aleatório sorteia a ação. Interpretação registrada e sujeita ao referendo.

| gate | definição operacional | passa se |
|---|---|---|
| **G3 divergência** (D1: convenção do projeto, sem referente externo) | por semente, JSD (bit) entre `atencioso-lobos` e `relapso-lobos` nas sondas; média e IC95 bootstrap sobre as 5 sementes | média **≥ 0,10** e limite inferior do IC **> 0,02** |
| G3 secundário (relatado) | por semente, JSD de cada dono coerente contra `aleatorio-lobos`; média dos 6 pares de donos distintos; a conta da v1 (todos os pares entre braços e o piso dentro do braço); as mesmas contas em bandit, instinto e controle | — |
| **G3-T tarefa ensinada** (D1, sem gate) | seção 4.2: acerto por dia, eficiência amostral, teto do dono e piso do instinto; por dono coerente, mais aleatório, controle e acoplado; IC sobre sementes | — (reportado sempre) |
| **G4 legibilidade do aprendido** (D3) | fração das decisões das 20 vidas lobos em que **o lobo de decisão decidiu** (a diferença entre os pesos atuais e o prior muda a escolha, seção 4.1) **e** há fator nomeado; IC bootstrap sobre sementes | fração **≥ 0,50** |
| G4 bruto (relatado, sem gate) | fração com fator contando o impulso (o que o instinto já dá); bandit e instinto pela mesma regra | — |
| G4 lobos × controle (D2) | G4 do aprendido nos lobos menos no controle, pareado por semente, IC | "a modularidade compra legibilidade" só se o limite inferior do IC > 0 (afirmação, não gate) |
| custo do gargalo (D2) | G3-T (acerto médio dos 7 últimos dias, atencioso) dos lobos menos o do controle, pareado por semente, IC | — (reportado sempre) |
| **G5 separação do cuidado** (D4) | (a) no desenho da arena v1 não há morte nem lesão: G5(a) = G3; (b) o braço da seção 3.1, leitura (ii); (c) **acima do acoplado**: por semente, JSD(`atencioso-lobos`, `relapso-lobos`) − JSD(`atencioso-cuidado`, `relapso-lobos`), IC sobre sementes | (a) G3 passa **e** (c) limite inferior do IC **> 0**; (b) relatado: limite inferior do IC > 0,02 com pelo menos 3 sementes, senão "insuficiente" |
| **G6 sem deriva** | por vida lobos, JSD(política no fim do dia d, instinto) para d = 1…14 (replay do log até o tick d·1440; mesmas sondas); e a fração de pesos no teto no dia 14 | (a) média de JSD(14) ≤ **1,5** × média de JSD(7); (b) **nenhum** peso no teto em nenhuma vida |

Parada: G3, G4 ou G5 falhando na validação = **resultado negativo registrado**; nada se reajusta olhando a validação.
G6 falhando é relatado e vai ao Matheus (é freio, não a hipótese).

### 4.1 Regra de honestidade do motivo para a `PoliticaLobos` e o controle

`motivo.PoliticaComMotivo` passa a aceitar as duas (`motivo_lobos`, função pura do registro da decisão):
- **o impulso (ou o prior) decidiu** quando a regra tem um candidato só, ou quando o sorteio com os **pesos do prior** e o **mesmo u**
  dá a mesma ação (o termo aprendido não mudou a escolha). Nos lobos os fatores são os da regra do instinto (`motivo_instinto`: sono
  cita energia e hora; pedido cita fome e higiene; abandono cita o tempo sem cuidado; fome moderada cita fome; tempo livre não cita
  nada); no controle não há regra: sem fator. Isto é o **G4 bruto**.
- **o lobo de decisão decidiu** quando o sorteio com os pesos do prior daria outra ação. Contribuição da entrada `j`:
  `x_j · (δ[a*][j] − média dos δ[b][j] dos outros candidatos) / S`, com `δ = w − w0`. Só vira fator uma contribuição
  **positiva** e ≥ `ConfigExpressao.limiar_motivo`; no máximo 2; `viés` vira `habito`, `ticks_sem_cuidado` vira
  `tempo_sem_cuidado` (os nomes do bandit). Sem contribuição acima do limiar: sem fator ("não sei"). É a regra do bandit. **O G4
  (gate) é a fração de decisões nesta classe com fator**, sobre todas as decisões.

### 4.2 G3-T: acerto na tarefa ensinada

A tarefa do dono coerente está escrita em `donos.julgar_acao(estado, cfg)`: +1 elogia, −1 repreende, 0 nada a dizer, dado o estado
(fome, higiene, energia, hora do dia) e a ação do pet. Para cada vida, o replay regista o estado observado e a ação de cada decisão.
- **Acerto por dia** `A(d)`: fração das decisões do dia `d` com julgamento +1 (as de julgamento 0 contam como não elogiadas).
- **Teto por dia**: fração das decisões do dia em que **alguma** das 7 ações teria julgamento +1 nos mesmos estados (a política ótima do
  dono, avaliada nos estados que o pet de fato visitou). **Piso**: o acerto da vida `<dono>-instinto` da mesma semente (média dos 14
  dias).
- **Eficiência amostral**: número de sinais do dono (elogios + broncas) recebidos até o fim do primeiro dia em que `A(d) ≥ (piso +
  máx_d A(d)) / 2`; "nunca" se a curva não chega lá.
- Resumos por braço: `A` média dos 7 últimos dias, teto, piso, eficiência; IC bootstrap sobre sementes. Para o aleatório e o
  incoerente a tarefa julgada é a mesma regra coerente (é a tarefa, não o dono). Funções novas em `digilab/metrics.py`:
  `acerto_na_tarefa`, `eficiencia_amostral`.

## 5. Calibração (sementes 3101…3505)

- Grade: 5 valores de `passo` × 3 de `teto` = 15 pontos; em cada ponto, as 20 vidas lobos (instinto e bandit não dependem da grade e
  rodam uma vez), G3, G3-T, G4 (aprendido e bruto) e G6. Tudo em `artifacts_v2_l1/calibracao/varredura.jsonl` e `<ponto>/`.
- **Escolha, decidida aqui:** entre os pontos com G6 (a) e (b) e **G4 do aprendido** passando, o de **maior limite inferior do IC do
  G3**; empate → menor `passo`, depois menor `teto`. Se nenhum ponto passa G6 e G4, o de maior limite inferior do G3 entre os que
  passam G6; se nenhum passa G6, o de menor JSD(14)/JSD(7) — e o relatório diz que a calibração não fechou.
- O ponto escolhido vai para `experiments/configs/v2_l1/validacao.json` (commitado antes da validação) e para `ConfigLobos` como padrão
  de `passo` e `teto`. Só no ponto escolhido rodam, nas sementes de calibração: o controle sem lobos, o acoplado (e a variante sem
  carinho), a norma de reação e o braço de educação.

## 6. Validação (sementes 4101…4505, uma vez, depois do referendo)

Os mesmos scripts com o config de validação: todos os braços, G3–G6, G3-T, custo do gargalo, acoplado, norma de reação e o braço
de educação, em `artifacts_v2_l1/validacao/` (`resultado.json`, `divergence.json`, `tarefa.json`, `legibilidade.json`,
`custo_gargalo.json`, `so_cuidado.json`, `norma_de_reacao.json`, `deriva.json`, `educacao/`). Nenhum número muda depois dela. Resultado em
`docs/RESULTADO_V2_L1.md`, com a tabela de gates, e seção própria no `CLAUDE.md`.

## 7. O que não entra

Recompensa multidimensional; janela de crédito maior; aprendizado fora do lobo de decisão; L2/L3 (peças do DF); A1; o
porte para a web (`VERSAO_PET = 11` reservado, só depois do G3–G5); torneio e métricas de vitória da arena v1.

## 8. Histórico do plano

- **Revisão 1** (2026-10-01, commit `ab53d00`): G3–G6 como no plano da V2, sem G3-T, sem controle, sem acoplado, G4 sobre o total.
  Uma calibração começou sob essa revisão e foi **interrompida e descartada** (nenhum artefato guardado) quando o coordenador
  trouxe as decisões D1–D4 (`docs/DEFINICOES_V2.md`, PR #110; tarefa revisada no PR #111).
- **Revisão 2** (2026-10-01, este texto): G3-T, G4 só do aprendido (o bruto sem gate), controle de capacidade equivalente, "só
  cuidado" acoplado com G5(c), norma de reação, e a regra de escolha da calibração pelo G4 do aprendido. Registrada antes da
  calibração válida.
