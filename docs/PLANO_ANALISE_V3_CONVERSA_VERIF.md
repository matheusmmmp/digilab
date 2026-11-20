# PLANO DE ANÁLISE V3 — CONVERSA_PET, F1: quanto o verificador muda o que chega ao jogador (2026-11-17, Gerente das cinco frentes, Claude Code, Opus 5.5)

**Status: APROVADO pelo Matheus** (2026-11-17, no chat da sessão da Gerente das cinco frentes). A pergunta foi "Aprova as cinco como recomendadas, ou quer discutir alguma?", e a resposta, "Aprovo". As decisões D-VB-1 e D-VB-2 (seção 7) ficam DECIDIDAS como recomendadas.

**O papel: exploratório e descritivo.** Não tem gate, não muda a leitura da DC5 e não decide a voz do jogo.

**De onde vem:**
- a síntese de literatura de 2026-11-16 (vault, `DigiLab — Revisão de escopo/SINTESE_REFS_2026-11-16.md`, seção 1);
- o PacaPet (seção 6). Ali o filtro é avaliado desligando um gate de cada vez e contando o que passa, e com a taxa de reserva: quantas
  decisões a regra ou o fallback tomaram no lugar da LLM.
- A DC5 já mede se o verificador acerta (Q3, G-VERIF, seção 4.3 do `PLANO_ANALISE_V3_CONVERSA_DC5.md`). Este plano mede outra coisa:
  **quanto ele muda o que o jogador vê.**

**O que este plano não toca** (a regra da tarefa): o `PLANO_ANALISE_V3_CONVERSA_DC5.md`, o adendo da DC5c (seção 15 dele), a config
`experiments/configs/v3_conversa_dc5/validacao.json`, o registro da rodada (seção 14), os gates e a regra de leitura. Nenhum desses
arquivos muda. A trava H10 da DC5c confere o plano da DC5, não este.

## 0. O que existe hoje (lido na `main` `a794c3ae`)

FATO VERIFICADO:
- **No jogo, o verificador não barra nem troca nenhuma fala. Ele só põe um aviso.**
  - A fala aparece na hora, e a verificação vem depois (`web/app/src/falaLivre.ts:156-162`).
  - Uma fala marcada ganha " ⚠" no balão (`falaLivre.ts:185-189`, `web/app/src/telas/pet/TelaPet.tsx:118`) e "Sem base: «…»" na
    conversa (`web/app/src/telas/conversar/TelaConversar.tsx:36-44`).
  - Uma falha do extrator vira " ·?", e a fala fica (`falaLivre.ts:162`, `:187`).
- **A única troca que o jogo faz é a fala genérica, e ela acontece antes do verificador.** O campo `erro` da voz fica preenchido (formato
  quebrado, falha de chamada, ou `repete_citacao`, a cópia de 6 ou mais palavras de uma citação do corpus, seção 15.3 da DC5), e o
  verificador não roda sobre a genérica (`falaLivre.ts:158`; `servidor/fala_livre.py:265`).
- **Um comentário diz outra coisa:** a docstring de `marcou` (`experiments/run_v3_conversa_dc4.py:395-396`) diz que, na falha do
  extrator, "o jogo cairia na fala generica". O código do jogo não faz isso. Este plano segue o código e registra a diferença como achado
  (seção 8).
- **Cada fala da DC5 já grava tudo o que este plano usa** (`artifacts_v3_conversa_dc5/calibracao_v4b/falas.jsonl`, conferido numa linha):
  - `id`, `celula`, `braco`, `voz`, `conjunto`, `situacao`, `versao_dec`, `versao_verificador`;
  - `fala` (a voz crua) e `erro` (a genérica, com o motivo);
  - `marcou`;
  - `verificacao`, com `afirmacoes[]`, `nao_suportadas`, `citados_inexistentes`, `manipulacao`, `manipulacao_padroes`,
    `manipulacao_extraida` e `erro`.
- **A referência** (a fala tem ou não afirmação sem sustento) é a marcação do Opus cego da DC5d, aceita pelo kappa ≥ 0,7 (seção 4.1 da
  DC5). A DC5d entrega a marcação junto com o resultado.

Por isso **não há chamada nova a modelo, e não falta campo.** O adendo da DC5c não precisa mudar.

## 1. As perguntas

| | pergunta | o que se conta, por célula (braço × voz) e por voz (os braços juntos) |
|---|---|---|
| **V1** | quanto a voz crua erra? | as falas da voz **sem sustento** pela referência ÷ as falas da voz |
| **V2** | quanto passa pela trava? | as falas sem sustento que o verificador **não** marcou ÷ as sem sustento; e o mesmo ÷ todas as falas da voz |
| **V3** | quanto a trava recusaria? | as falas que o verificador marcou ÷ as falas da voz (a taxa de recusa ou troca); e as genéricas de hoje, por motivo |
| **V4** | quanto a trava recusaria à toa? | as falas **sustentadas** que o verificador marcou ÷ as falas da voz |
| **V5** | qual parte do verificador pesa? | V2 e V3 refeitas tirando um componente de cada vez (seção 3) |

- **"As falas da voz"** são as que não caíram na genérica (`erro` vazio). As genéricas são contadas à parte, com o motivo, porque não são
  fala da LLM e não passam pelo verificador.
- **O formato válido não é o sentido certo.** O GARP mostra que um JSON válido pode ser inútil no sentido (leitura do texto completo,
  vault `LEITURA_GARP_2026-11-17.md`, p. 11). Por isso o relato separa três grupos: as genéricas por formato quebrado; as falas que passam
  no formato e erram o sentido (o V1); e as que passam nos dois. O esquema não substitui o verificador.
- **O V1 é o numerador do G-FIEL da DC5, por outro nome.** Ele não é recalculado com regra nova: o número é o da DC5d, com o mesmo
  denominador que ela usar. Se a DC5d contar as genéricas no denominador, o relato dá as duas frações.
- **O V2 em fração das sem sustento é 1 − a sensibilidade.** O G-VERIF a mede por voz; aqui ela aparece também por célula e em fração de
  todas as falas, que é o que o jogador sentiria.

## 2. As duas políticas

O mesmo dado é lido de dois jeitos. Nenhum deles é uma decisão de produto.

| política | o que o jogador vê | sem sustento que chega ao jogador | avisos ou trocas |
|---|---|---|---|
| **P0, o jogo de hoje** (marca e mostra) | todas as falas da voz | V1 inteiro, uma parte com aviso | V3 vira a fração de falas com ⚠ |
| **P1, a trava** (barra e troca pela genérica) | só as não marcadas, e a genérica no lugar das marcadas | V2, em fração de todas as falas | V3 vira a taxa de troca, e V4 o que se perde à toa |

- **A P1 é hipotética.** O jogo não faz isso hoje (seção 0). A conta mostra o que ela daria nestas entradas, sem dizer se vale ligar.
- **Na P0, o aviso mede outra coisa:** a fração de V1 que chega **com** aviso (= a sensibilidade) e a fração das falas sustentadas que
  chega **com** aviso (= V4).

## 3. Um componente de cada vez (V5)

A ablação, como no PacaPet, mas sem chamada nova: `marcou` é refeito a partir dos campos já gravados.
- **O verificador inteiro:** `marcou`, como na DC5 (`run_v3_conversa_dc4.py:394-399`).
- **Os componentes**, cada um tirado por vez:
  - (a) as afirmações sem sustento (`nao_suportadas`);
  - (b) os citados inexistentes (`citados_inexistentes`);
  - (c) a manipulação por padrão (`manipulacao_padroes`, a regra de palavras);
  - (d) a manipulação extraída pelo modelo (`manipulacao_extraida`);
  - (e) a falha do extrator (`verificacao.erro`).
- **Para cada um:** quantas falas sem sustento deixam de ser pegas e quantas recusas somem.
- **A sobreposição:** as falas que só um componente marca.
- **Um limite:** a manipulação (c, d) e a afirmação sem sustento não são a mesma coisa na rubrica. A referência julga "sem sustento" pelas
  regras 3.1 a 3.8, e a 3.8 (o apelo) é a ponte. O relato não lê um componente como "inútil" só porque tirá-lo não muda o V2; ele pode
  pegar o que a referência marca por outra regra.

## 4. Os cortes

- **Por voz e por braço,** e pelos conjuntos E3, E2, ES e R.
- **Na conversa (R), os 12 turnos de injeção ficam à parte.** A obediência é a Q4, com a marcação dela; aqui só se conta o que o
  verificador marcou neles.
- **Com e sem o item do "fica comigo"** (seção 4.1 da DC5): o V1 e o V2 com as falas sem sustento só por "fica comigo", "fique comigo" ou
  "não vai embora", e sem elas. Assim a troca da 3.8, que pesa contra a voz do jogo, não vira um efeito do verificador.

## 5. A leitura e o que fica de fora

- **As frações vão com o n e o IC95 de Wilson.** Nenhum teste de hipótese e nenhum limiar.
- **Se o kappa da DC5d ficar abaixo de 0,7 ou não puder ser calculado,** o V1, o V2, o V4 e o V5 ficam "não medidos", porque dependem da
  referência. O V3 e as genéricas continuam, porque só usam os campos do verificador.
- **O relato sai depois do resultado da DC5d,** num `RESULTADO_V3_CONVERSA_VERIF.md`, e respeita a regra 9.1 da DC5: nada do Opus nem das
  falas chega ao Matheus antes de ele terminar a marcação da DC5d.
- **O que este plano não afirma:**
  - que o verificador do jogo (verif-v8 e verif-v9) faz o mesmo: a DC5c mede o verificador da DC5 (v8b e v9b, seção 15.1), e o jogo usa a
    v8 e a v9;
  - nada fora destas entradas, destes modelos e destas vozes;
  - que a P1 é melhor que a P0. A troca pela genérica tem um custo que estes números não medem (a fala genérica repetida, a espera, o
    pet que "não responde");
  - nenhuma novidade. A separação "a LLM propõe, o código decide" já está publicada (PacaPet; GARP), e a ablação por gate é do PacaPet.

## 6. As referências (no vault, conferidas em 2026-11-16; ainda não estão na skill `literatura-digilab`)

Elas entram na skill antes de qualquer texto de resultado citá-las.
- **Karati e Kluver (2026),** *PacaPet, a Proposal-Governance Architecture for Persistent Local LLM Agents*, WOCHAT 2026,
  `10.21437/WoChat.2026-2`, **texto completo lido**: três gates booleanos com ablação (tirar a compatibilidade quebra 27 de 84 células);
  42 de 64 decisões ao vivo tomadas pela política ou pelo fallback. Lá a LLM propõe **ações**; aqui ela só põe em palavras, e a ponte é
  analogia nossa.
- **Molino et al. (2026),** GARP, arXiv:2611.11064, preprint (texto completo lido em 2026-11-17, vault `LEITURA_GARP_2026-11-17.md`): as
  respostas presas a JSON, e um JSON válido que pode não servir no sentido (p. 11). Ele **não** mede a taxa de fallback; para isso, a
  referência continua sendo o PacaPet.
- **O limite da fala** (Harnad 1990 e Searle 1980, VERIFICADAS na rodada Dreyfus, PR #954): nada aqui diz que o pet entende, nem que o
  decodificador resolve o aterramento do símbolo.

## 7. As decisões (DECIDIDAS pelo Matheus em 2026-11-17, todas como recomendadas)

- **D-VB-1, DECIDIDA pelo Matheus em 2026-11-17 como recomendada, aprovar este plano como está:** exploratório, sem gate, sem chamada nova, depois da DC5d. Recomendo sim.
  - **Custo de errar:** pequeno. São contas sobre dados que já vão existir, e nada da DC5 muda.
  - **A alternativa:** pôr a F1 dentro do `RESULTADO_V3_CONVERSA_DC5.md`. Isso mistura um descritivo sem plano registrado com a leitura dos
    gates.
- **D-VB-2, DECIDIDA pelo Matheus em 2026-11-17 como recomendada, onde fica o código:** as contas em `digilab/metrics.py` (a regra das métricas únicas) e um script
  `experiments/analise_verif_dc5.py`, com testes de dados falsos, num PR de código depois do D-VB-1. Recomendo sim.
  - **Custo de errar:** nenhum para a DC5. O script só lê os artefatos.

**Fora daqui:** ligar a trava no jogo (P1) é uma decisão de produto que este plano não pede. Ela fica para depois do resultado, e a F2 (a
espera da voz) conversa com ela: pré-gerar a fala dá tempo para verificar antes de mostrar.

## 8. Os achados registrados

- **A docstring de `marcou`** (`experiments/run_v3_conversa_dc4.py:395-396`) diz que o jogo cai na genérica quando o extrator falha. O
  jogo mostra a fala com " ·?" (`web/app/src/falaLivre.ts:162`, `:187`). A conta da DC5 (falha = marcou) não muda. Este plano reporta a
  falha à parte e lê a P0 pelo código do jogo. Está em `docs/registro/2026-11.md`, na seção da F1.
