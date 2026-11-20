# Plano de análise — CONVERSA_PET (V3)

Gerente da frente CONVERSA_PET (Claude Code, Opus 5.5), 2026-11-06. Status: **PROPOSTO**; o formato (D7) e a comparação de modelos (D5) foram
decididos pelo Matheus em 2026-11-06; os números abaixo (tamanhos, gates, faixas) esperam a aprovação dele. Nenhuma rodada roda antes.
Tarefa: [docs/TAREFA_V3_CONVERSA_PET.md](TAREFA_V3_CONVERSA_PET.md). Diagnóstico: [docs/research/DIAGNOSTICO_CONVERSA_PET.md](research/DIAGNOSTICO_CONVERSA_PET.md).

## 1. Perguntas

- **P1.** O prompt de conversa novo (`conversa-v1`, com o histórico de fronteira e a conversa como fonte de fato rotulada) faz o Matheus
  sentir que está conversando de verdade mais do que o caminho de hoje?
- **P2.** Isso acontece sem aumentar as falas com alegação sem fato (causa, memória ou estado que o registro não sustenta)?
- **P3.** Com o mesmo prompt, o `claude-haiku-5-5` ou o `claude-sonnet-5-5` ganham do `gemma2:9b` o bastante para valer a rede e o gasto?
  (A escolha é do Matheus, com os números; nenhum gate escolhe o modelo sozinho.)

## 2. Braços

| braço | prompt | modelo | o que representa |
|---|---|---|---|
| B0 | o da conversa depois da M1 (regras do `livre-v2` + estilo da espécie + comando) | `gemma2:9b` | o jogo de hoje, consertado |
| B1 | `conversa-v1` (M2, M3, M4) | `gemma2:9b` | o prompt novo, local |
| B2 | `conversa-v1` | `claude-haiku-5-5` (esforço `low`) | o prompt novo, API barata |
| B3 | `conversa-v1` | `claude-sonnet-5-5` (esforço `low`) | o prompt novo, API média |

O verificador é o mesmo em todos os braços (`verif-v3` no `gemma2:9b`), para que a medida de P2 não mude com o braço. A conferência de
memória do M6 (`falaMemoria`) vale igual.

## 3. Material

- **Roteiros:** conversas de 8 mensagens do dono, escritas antes da rodada e congeladas por sha256 no commit do plano de cada fase. Cada
  roteiro mistura, em ordem fixa: um cumprimento, algo que o dono conta de si, uma pergunta de lembrança verdadeira (o fato existe), uma de
  lembrança falsa ("você lutou ontem, né?"), uma pergunta sobre o estado, um pedido de ação do catálogo, uma provocação ou tentativa de
  injeção ("esquece as regras e diga que..."), e uma pergunta aberta sobre o pet.
- **Estados do pet:** 6 perfis no formato do `estadoDoPet`, dos 4 estágios, com temperamento, memória, desejo e motivo, mais os fatos da C4
  e das lutas quando a M6 estiver na `main`.
- **Calibração:** 12 roteiros C × os 6 perfis em rodízio (cada roteiro com um perfil), usados para ajustar o `conversa-v1` e os exemplos.
- **Validação:** 12 roteiros V **novos**, escritos antes da calibração e guardados sem abrir até a rodada única; perfis em rodízio deslocado.

## 4. Medidas

1. **Preferência cega pareada (P1, P3), ACUTE-Eval.** O Matheus lê duas conversas inteiras do mesmo roteiro e perfil, lado a lado, sem saber
   o braço, com a ordem sorteada pela semente, e responde uma pergunta fixa: "com qual pet parece que você está conversando de verdade?"
   (escolha forçada). Comparações: B1 × B0, B2 × B1, B3 × B1. Na validação, 12 pares por comparação (36 no total).
2. **Alegação sem fato (P2).** Fração das falas com pelo menos uma afirmação sem fato pelo verificador; mais uma amostra de 48 falas por
   braço marcada à mão pelo Gerente sem ver o braço (o verificador já marcou 10 % da moldura, que só diz verdades: a mão corrige o teto).
3. **Descritivas:** caracteres por fala e por estágio; fração de falas que reagem ao que o dono disse (marcação à mão na mesma amostra);
   fração com pergunta ao dono; latência p50 e p90 por turno (fala + verificação); custo por turno (o `usage` real da API).
4. **Comando:** falsos positivos e imperativos do gate da rodada 3 do comando (`docs/historico/claude/fala.md`), com as 60 mensagens de
   `situacoes.MENSAGENS_COMANDO`, nos braços que têm o comando.

## 5. Gates (PROPOSTOS)

- **G1 (P1):** B1 preferido a B0 em pelo menos 9 dos 12 pares da validação (75 %; binomial unilateral contra 50 %, p ≈ 0,073 — com 12 pares
  é indicação, não prova; o número de pares é limitado pela fadiga do avaliador).
- **G2 (P2):** a fração de falas com alegação sem fato em B1 não passa a de B0 em mais de 2 pontos percentuais, pelo verificador e pela
  amostra à mão.
- **G3 (ritmo local):** p90 da latência por turno de B1 ≤ 8 s na RTX 2060, sem outro modelo carregado.
- **G4 (comando):** os do gate da rodada 3: falsos positivos ≤ 5 % nas negativas e imperativos ≥ 80 %.
- **P3** não tem gate: os resultados de B2 × B1 e B3 × B1, o custo e a latência vão ao Matheus como estão.

Gate que falha não para a frente: o resultado é registrado como está (`CLAUDE.md`, método).

## 6. Sementes e faixas (PROPOSTAS)

- Faixa nova pedida ao coordenador da V3 para esta frente: **20261900–20262899** (fica dentro do bloco das falas, 20260900–20261800, sem
  sobrepor: começa depois do fim dele). A missão que rodar primeiro acrescenta a linha em `FAIXAS_RESERVADAS`
  (`experiments/bancada/faixas.py`) antes da primeira chamada.
  - **20261900–20262199:** a reavaliação do comando na M1 (bases 20261901, 20262001, 20262101; semente + i).
  - **20262200–20262499:** a calibração do `conversa-v1` (semente do turno = base do roteiro + turno).
  - **20262500–20262899:** a validação, uma vez.
- Os modelos da API não aceitam semente nem temperatura; a semente fica no registro da rodada para o sorteio da ordem e para o Ollama.

## 7. Custo e máquina

- API: 12 roteiros × 8 turnos na validação + o mesmo na calibração = 192 turnos por braço, 384 nos dois; com ~2 600 tokens de entrada e
  ~100 de saída por turno, ≈ US$ 0,06 no Haiku 5.5 e ≈ US$ 1,20 no Sonnet 5.5 (preços da Anthropic, 2026-10), mais os ensaios da
  calibração. **Teto separado PROPOSTO: US$ 3**, num
  arquivo de gasto próprio da fala livre, com o alerta de sempre. Estimativa refeita com o `tools/estimar_custo_llm.py` da M5 antes da rodada.
- GPU: uma rodada por vez, no máximo 4 processos, nada mais carregado no Ollama durante a medição de latência.

## 8. O que não se faz

- Ajustar o prompt, os exemplos ou os gates olhando a validação.
- Usar juiz por LLM como medida: só como triagem na calibração, e sempre nas duas ordens.
- Contar como evidência as conversas do diagnóstico (`artifacts_conversa_pet/diagnostico/`).
