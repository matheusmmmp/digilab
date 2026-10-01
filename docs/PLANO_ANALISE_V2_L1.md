# Plano de análise — V2, L1: o lobo de decisão aprende com o feedback como vantagem

Status: **registrado antes de qualquer run** (2026-10-01). Nada foi rodado para escrever este plano. Os números citados
vêm de artefatos em disco, e cada um aponta o arquivo; os valores sem fonte estão marcados PROPOSTO. Os gates G3–G6 são
os do `docs/PLANO_V2_PESQUISA.md` (fase 1), com as definições operacionais fixadas aqui; **a validação só roda depois do
referendo do Matheus** sobre esses gates (`docs/TAREFA_V2_L1_DECISAO.md`, seção 2).

**Natureza.** Nó L1 da fase 1b (hipótese H1). A L0 (`PoliticaLobos`, PR #108) mostrou que a política com lobos, com o
aprendizado desligado, é o instinto byte a byte. A L1 liga o aprendizado **só no lobo de decisão**, com uma atualização
que depende da política atual (o feedback do dono no lugar da vantagem: MacGlashan et al., COACH, `arXiv:1701.06049`,
VERIFICADA na skill `literatura-digilab`), e pergunta se donos coerentes produzem políticas distinguíveis entre si e do
aleatório, com decisões explicáveis.

## 1. Ponto de partida (conferido nos artefatos)

| achado | número | artefato |
|---|---|---|
| a L0 reproduz o instinto byte a byte (G2) e rejoga bit a bit (G1) | 23 testes | `tests/test_lobos.py` |
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

## 3. Desenho

- **Vidas:** o da arena v1 (`PROTOCOLO_ARENA_V1`: 4 donos sintéticos — atencioso, relapso, aleatório, incoerente —,
  orçamento 224 = 16/dia × 14 dias, 14 dias, `MotorComFeedback`, passo do dono da `ConfigDonos`), com três políticas por
  dono, **o mesmo dono com a mesma rng nas três** (`rotulo_dono`, como na ablação):
  - **lobos** — a `PoliticaLobos` com o aprendizado ligado (o braço testado);
  - **instinto** — a `PoliticaInstinto`: o braço **"só cuidado"** (V2-H0), o controle permanente da V2;
  - **bandit** — a `PoliticaBandit` da v1 nas mesmas sementes: referência da v1, não é braço de pesquisa.
  12 braços × 5 sementes = 60 vidas por conjunto. Rótulo `<dono>-<política>@<semente>`.
- **Sem torneio.** Os gates G3–G6 são todos sobre a política; a luta na arena v1 media "pet melhor", pergunta encerrada em
  `docs/LEITURA_CONSOLIDADA_DONO.md`. O torneio e as métricas de vitória da arena v1 **não rodam** (registrado em
  `docs/REGISTRO_DESVIOS.md`).
- **Sondas de divergência:** as da arena v1: 64 estados, 200 amostras por estado, `semente_sonda` 9001, números aleatórios
  comuns (`metrics.estados_sonda`, `distribuicoes_de_acao`, `divergencia_politicas`, `jsd_bits`). Nenhuma função nova de
  métrica: `digilab/metrics.py` continua a única fonte.
- **Sementes:** calibração **3101, 3202, 3303, 3404, 3505**; validação **4101, 4202, 4303, 4404, 4505**, uma vez só, depois do
  referendo. Nenhuma outra. Bootstrap percentil sobre sementes: 10 000 reamostras, semente 20261001, nível 0,95.
- **Replay:** toda vida é gravada (`vidas/*.jsonl`, `*.politica.json`) e **reconstruída do disco** antes de qualquer medida;
  divergência no replay para tudo. O `politica.json` é gravado **antes** das sondas (a sonda chama `agir` e acrescenta
  motivos ao registro da política; nada de decisão ou aprendizado muda com a sonda).
- **Meta da run:** sha256 de `digilab/policies/lobos.py`, `digilab/config.py`, `digilab/motivo.py` e do `engine.py`; versão
  do Python e plataforma; os parâmetros da `ConfigLobos` usados.

### 3.1 Braço próprio do G5: o motor de educação com lesões

No desenho da arena v1 **não há morte nem lesão** (nem luta): o G5 vale ali por construção, e isso fica registrado. Para
medir o que a tarefa pede, um braço à parte, **só com os parâmetros escolhidos na calibração** (não entra na grade):
- 4 donos (atencioso, relapso, aleatório, incoerente) × 5 sementes, `MotorEducacao` com educação e lesões ligadas,
  duração "teste", orçamento de `treino_vida.orcamento_treino` (o da V3), sparring da V3 (`run_educacao.ticks_sparring`,
  `PetDaVida`, rival da mesma linha), espécie e temperamento do ovo (`evolucao.ovo`, `temperamento.sortear`). A política
  é a `PoliticaLobos` com o aprendizado ligado (`fabricas_educacao` ganha um parâmetro opcional `politica_fabrica`; o
  padrão continua o bandit da personalidade, bit a bit).
- Medida: a mesma divergência da seção 4 (G3), com a política **final** de cada pet (morto: a política no tick da morte),
  em duas leituras: (i) todos os pets; (ii) só os pares em que **nenhum** dos dois pets teve lesão nem morte.

## 4. Métricas e gates (PROPOSTOS)

Toda métrica sai de `digilab/metrics.py` ou de `digilab/motivo.py` (regra de honestidade). "Donos coerentes" =
**atencioso e relapso**: são os dois que aplicam a regra de feedback coerente (`donos.feedback_coerente`); o incoerente
sorteia a polaridade e o aleatório sorteia a ação. Interpretação registrada e sujeita ao referendo.

| gate | definição operacional | passa se |
|---|---|---|
| **G3 divergência** | por semente, JSD (bit) entre `atencioso-lobos` e `relapso-lobos` nas sondas; média e IC95 bootstrap sobre as 5 sementes | média **≥ 0,10** e limite inferior do IC **> 0,02** |
| G3 secundário (relatado) | por semente, JSD de cada dono coerente contra `aleatorio-lobos`; média dos 6 pares de donos distintos; a conta da v1 (todos os pares entre braços, inclusive sementes diferentes, e o piso dentro do braço); as mesmas contas nos braços bandit e instinto | — |
| **G4 legibilidade** | fração das decisões das 20 vidas lobos com **fator** sob a regra de honestidade (seção 4.1); relatadas em separado a fração em que o lobo de decisão decidiu com fator e a fração em que o impulso decidiu com fator; bandit e instinto reprocessados pela mesma regra | fração total **≥ 0,50** |
| **G5 separação do cuidado** | (a) no desenho da arena v1 não há morte nem lesão: G5 = G3, por construção; (b) no braço da seção 3.1, a leitura (ii) | (a) G3 passa; (b) relatado: limite inferior do IC **> 0,02** com pelo menos 3 sementes na leitura (ii), senão "insuficiente" |
| **G6 sem deriva** | por vida lobos, JSD(política no fim do dia d, instinto) para d = 1…14 (replay do log até o tick d·1440; mesmas sondas); e a fração de pesos no teto no dia 14 | (a) média de JSD(14) ≤ **1,5** × média de JSD(7) (crescimento sublinear: convergindo dá ≈ 1, linear dá 2); (b) **nenhum** peso no teto em nenhuma vida |

Parada: G3, G4 ou G5(a) falhando na validação = **resultado negativo registrado**; nada se reajusta olhando a validação.
G6 falhando é relatado e vai ao Matheus (é freio, não a hipótese).

### 4.1 Regra de honestidade do motivo para a `PoliticaLobos`

`motivo.PoliticaComMotivo` passa a aceitar a `PoliticaLobos` (`motivo_lobos`, função pura do registro da decisão):
- **o impulso decidiu** quando a regra tem um candidato só, ou quando o sorteio com os **pesos do prior** e o **mesmo u**
  dá a mesma ação (o termo aprendido não mudou a escolha). Fatores: os da regra do instinto (`motivo_instinto`: sono cita
  energia e hora; pedido cita fome e higiene; abandono cita o tempo sem cuidado; fome moderada cita fome; tempo livre não
  cita nada). É a regra que o braço instinto já usa.
- **o lobo de decisão decidiu** quando o sorteio com os pesos do prior daria outra ação. Contribuição da entrada `j`:
  `x_j · (δ[a*][j] − média dos δ[b][j] dos outros candidatos) / S`, com `δ = w − w0`. Só vira fator uma contribuição
  **positiva** e ≥ `ConfigExpressao.limiar_motivo`; no máximo 2; `viés` vira `habito`, `ticks_sem_cuidado` vira
  `tempo_sem_cuidado` (os nomes do bandit). Sem contribuição acima do limiar: sem fator ("não sei"). É a regra do bandit.
- Limites: a fração com fator do braço instinto é o **piso** do G4 (o que a L0 já daria); a fração "lobo de decisão com
  fator" é o número comparável aos 13–18% do bandit. O gate é sobre o total, porque a pergunta do G4 é se o pet consegue
  dizer por que agiu; a leitura estrita fica relatada ao lado.

## 5. Calibração (sementes 3101…3505)

- Grade: 5 valores de `passo` × 3 de `teto` = 15 pontos; em cada ponto, as 60 vidas (os braços instinto e bandit não
  dependem da grade e rodam uma vez), G3, G4 e G6 nas sementes de calibração. Tudo em
  `artifacts_v2_l1/calibracao/varredura.jsonl` e `<ponto>/`.
- **Escolha, decidida aqui:** entre os pontos com G6 (a) e (b) e G4 passando, o de **maior limite inferior do IC do G3**;
  empate → menor `passo`, depois menor `teto`. Se nenhum ponto passa G6 e G4, o de maior limite inferior do G3 entre os que
  passam G6; se nenhum passa G6, o de menor JSD(14)/JSD(7) — e o relatório diz que a calibração não fechou.
- O ponto escolhido vai para `experiments/configs/v2_l1/validacao.json` (commitado antes da validação) e para
  `ConfigLobos` como padrão de `passo` e `teto`. O braço da seção 3.1 roda nas sementes de calibração com esse ponto.

## 6. Validação (sementes 4101…4505, uma vez, depois do referendo)

Os mesmos scripts com `--validar`: 60 vidas, G3–G6 e o braço da seção 3.1, em `artifacts_v2_l1/validacao/`. Nenhum número
muda depois dela. Resultado em `docs/RESULTADO_V2_L1.md`, com a tabela de gates, e seção própria no `CLAUDE.md`.

## 7. O que não entra

Recompensa multidimensional; janela de crédito maior; aprendizado fora do lobo de decisão; L2/L3 (peças do DF); A1; o
porte para a web (`VERSAO_PET = 11` reservado, só depois do G3–G5); torneio e métricas de vitória da arena v1.
