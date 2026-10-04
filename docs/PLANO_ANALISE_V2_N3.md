# Plano de análise — V2, N3: a consequência da própria ação como sinal (braço P1)

Status: **registrado antes de qualquer run** (2026-10-04). Nada foi rodado para escrever este plano. Os números citados vêm de artefatos em
disco, cada um com o arquivo; o que não tem fonte é PROPOSTO. Tarefa: `docs/TAREFA_V2_N3_CONSEQUENCIA.md`; nó N3 de `docs/ROADMAP_V2.md`;
braço P1 de `docs/PLANO_V2_PESQUISA.md`, seção 2. Pela decisão do Matheus de 2026-10-01, uma falha é registrada e não para a V2.

## 1. Pergunta

O mesmo aprendiz da L1, recebendo como sinal **só a consequência da própria ação** (o valor homeostático, sem nada do dono), aprende a
cuidar de si melhor do que a predisposição herdada (P0)?

## 2. Ponto de partida (conferido nos artefatos)

| achado | número | artefato |
|---|---|---|
| o aprendiz da L1 aprende a tarefa do dono quando o sinal é o dono (P3) | G3-T atencioso 0,663 contra 0,577 do instinto | `artifacts_v2_l1/validacao/ponto/tarefa.json` |
| e o instinto decide a maior parte das decisões | o lobo de decisão decide 20,3% | `artifacts_v2_l1/validacao/ponto/legibilidade.json` |
| com o passo 512 e o teto 1024, 12 de 20 vidas prendem peso no teto | G6 falha | `artifacts_v2_l1/validacao/ponto/deriva.json` |
| a privação depende quase toda do dono | atencioso e incoerente sem privação; o aleatório 0,27–0,36 (no motor da educação) | `artifacts_v2_a1/validacao/` |
| a bancada monta P0 e P3 sobre o mesmo cérebro e o acoplado | G1, G2 e reprodução da L1 passam | `tests/test_bancada_v2.py` |

## 3. O sinal (desenho)

**Drives.** Fome, higiene e energia (`Estado.vetor`, índices 0, 1 e 2), cada uma com ponto de ajuste 1,0 (o estado vive em 0..1, com 1 =
satisfeito). O humor fica fora: é o canal da bola (A1) e o do efeito ruim das frutas (F6), e entra como canal próprio depois (H-R2). Saúde
fica fora: ela não muda pela ação em si, só pelo tempo em privação.

**Forma (Keramati e Gutkin, `10.7554/elife.04811`, VERIFICADA: recompensa = redução do desvio homeostático).** Em inteiros, com a escala
S = 2¹⁰ do aprendiz:

```
X_i = arred(h_i · S)            (h_i = fome, higiene, energia; arred = inteiro mais próximo, meio longe do zero)
D(h) = Σ_i (S − X_i)²           (distância ao ponto de ajuste: expoente 2, sem raiz)
f_S  = div_arred(ganho · (D(h_antes) − D(h_depois)), S)
```

- `f_S > 0` quando a ação reduziu o déficit, `< 0` quando o aumentou. O expoente 2 faz reduzir um déficit grande valer mais que um pequeno
  (a propriedade de priorização do drive de Keramati e Gutkin). Os expoentes (n = 2, sem a raiz m) são escolha do projeto, para ficar em
  inteiros sem raiz; isso fica dito em qualquer texto.
- `f_S` entra na **mesma regra de atualização da L1** (`lobos.atualizar_pesos`, via `Aprendiz._aplicar_sinal`), no lugar do sinal do dono.
  Nada mais muda: o passo 512, o teto 1024 e o piso da `ConfigLobos` são os da L1.
- `ganho` (inteiro) é a escala do sinal: o único parâmetro calibrado (seção 6). Ele não muda a regra; diz quanto "vale" uma redução de
  déficit perto de um elogio (S). Ordem de grandeza: comer com fome 0,4 dá D(antes) − D(depois) ≈ 0,058·S²; com ganho 16, f_S ≈ 0,9·S.

### 3.1 A janela de crédito (decidida aqui)

**Imediata.** O sinal de uma decisão é a diferença entre `transicao.observacao` e `transicao.observacao_seguinte` dessa mesma decisão, e
credita só ela. O motor mede essa transição logo depois do efeito da ação do pet, antes de o tempo passar e antes de qualquer ação do dono
(`engine._avancar`; validação V2 do roadmap). Por isso **nada do dono chega ao P1**: nem o sinal, nem o cuidado misturado na transição.

O que isso dá, ação por ação (`policy.efeito_da_acao_do_pet`, `state.py`):

| ação | efeito imediato nos drives | sinal |
|---|---|---|
| comer | fome +0,05 | positivo, maior quanto maior a fome |
| brincar | energia −0,02 (o humor sobe, mas está fora) | negativo |
| explorar | energia −0,015 (o humor sobe, fora) | negativo |
| dormir | nenhum: a energia sobe nos ticks seguintes | zero |
| ocioso, chamar atenção, emburrar | nenhum | zero |

- O aprendiz só aprende onde há sorteio (L1): na **fome moderada** (comer × chamar) e no **tempo livre** (ocioso, explorar, brincar,
  chamar). Dormir é regra determinista e nunca aprende, então o sinal zero do sono não muda nada aqui.
- Previsão registrada: o P1 come mais na fome moderada e, no tempo livre, troca brincar e explorar por ocioso e chamar. O primeiro deve
  reduzir a privação de fome; o segundo poupa energia. Como o humor está fora, o P1 aprende a brincar menos, e isso **não** é medido como
  custo aqui: é a consequência declarada de deixar o humor fora.
- **Variante declarada, não rodada nesta tarefa: consequência atrasada.** Creditar a mudança dos drives ao longo do intervalo até a decisão
  seguinte (15 ticks) pegaria o efeito do sono e o decaimento, mas mistura o cuidado do dono (que age entre as decisões) e pede separar o
  efeito da ação do efeito do dono. Fica para quando houver um motivo, com plano próprio.

**Sem o canal do chamado.** O P1 não recebe nada do dono, então também não recebe o crédito do chamado atendido nem a penalidade do
chamado ignorado (ambos dependem do dono). O gancho novo em `lobos.py` credita a consequência à decisão observada e não passa pelo relógio
de cuidado nem pelos pendentes.

## 4. Desenho

- **Bancada** (`experiments/bancada_v2.py`), mundo `padrao`, sem genoma (`MotorComFeedback`, como a L1), 14 dias, orçamento 224, os
  quatro donos da L1 (atencioso, relapso, aleatório, incoerente), a mesma rng do dono em todos os braços.
- **Braços:** **P0** (herdado: aprendizado desligado), **P1** (consequência), **P3** (o dono, referência da L1).
- **Acoplados (malha aberta):**
  - **P1 ← P0, filtro `nenhum`**: o cérebro do P1 rejoga o registro de eventos do P0 (o mesmo cuidado, nos mesmos ticks). É o **cuidado
    controlado** do N3: na vida fechada o dono reage ao pet, e um pet que muda de comportamento muda o cuidado que recebe;
  - **P3 ← P3, filtro `sem_sinais`**: o "só cuidado" acoplado da L1 (H0 permanente), como referência.
- **Sementes:** calibração **8101, 8202, 8303, 8404, 8505**; validação **9101, 9202, 9303, 9404, 9505**, uma vez. Nenhuma outra.
- **Sondas** (deriva e G4): as da L1 (64 estados, 200 amostras, `semente_sonda` 9001). **Bootstrap:** 10 000 reamostras, semente
  20261004, nível 0,95, sobre as 5 sementes.
- **Replay:** toda vida e todo acoplado rejogados do disco bit a bit pela bancada (G1); divergência para tudo.
- **Meta da run:** sha256 de `lobos.py`, `config.py`, `bancada_v2.py`, `metrics.py` e do `engine.py`; Python e plataforma.

## 5. Medidas e gates (PROPOSTOS)

Privação = 1 − `fracao_fora_de_privacao` (`metrics.desempenho_no_ambiente`, pela regra `Estado.em_privacao`, amostrada em cada decisão).

| gate | definição | passa se |
|---|---|---|
| **G-P1 privação** | por semente, média nos 4 donos de (privação do P0 − privação do P1), vidas fechadas; IC95 bootstrap sobre as 5 sementes | limite inferior do IC **> 0** |
| **sem mortes novas** | mortes do P1 − mortes do P0 | 0. No mundo `padrao` (`MotorComFeedback`, sem lesões) não há morte: o gate vale por construção, e fica registrado; a saúde média é relatada |
| **G6** | nenhuma vida do P1 com peso no teto (`Aprendiz.pesos_no_teto`) | 0 vidas |
| **G1** | toda vida rejogada do log bit a bit | teste e a bancada |
| **G2** | com a fonte desligada (P1 com o aprendizado desligado, ou ganho 0), a vida é a do P0 byte a byte | teste |

Relatados, sem gate: a mesma diferença por dono; o acoplado P1 ← P0 contra o P0 (o efeito das ações do próprio pet com o cuidado igual);
saúde média; G4 do aprendido (`motivo.motivo_lobos`, a regra de honestidade da L1); a deriva ao prior por dia e a razão dia 14 / dia 7;
`custo_da_plasticidade`; o acerto na tarefa do dono (o P1 não é ensinado: serve de contraste com o P3); a fração de comer na fome moderada
e de cada ação no tempo livre (a previsão da seção 3.1).

## 6. Calibração (sementes 8101…8505)

- Grade do `ganho`: {4, 8, 16, 32, 64}. P0 e P3 não dependem do ganho e rodam uma vez.
- **Escolha, decidida aqui:** entre os ganhos com G6 passando, o de maior limite inferior do IC do G-P1; empate → o menor ganho. Se nenhum
  passa G6, o de menos vidas com peso no teto e, no empate, o de maior limite inferior do G-P1; e o relatório diz que a calibração não
  fechou.
- O ganho escolhido vai para a `ConfigConsequencia` (padrão) e para `experiments/configs/v2_n3/validacao.json`, commitados antes da
  validação.

## 7. Validação (sementes 9101…9505, uma vez)

O mesmo script com o config de validação; todos os braços e o acoplado; `artifacts_v2_n3/validacao/`. Nada muda depois dela. Relatório em
`docs/RESULTADO_V2_N3.md` e seção no fim do `CLAUDE.md`.

## 8. O que não entra

A consequência atrasada (variante declarada); o humor e a saúde como drives; outros canais de reforço (H-R2); P2 e P2e (N5); frutas (N4);
outros mundos; a web.
