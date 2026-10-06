# TAREFA V2 — P2D-P3I: os braços que separam momento e interpretação (2026-10-06)

Coordenador: chat "Principais jogos Digimon com diálogo". Rodada 12 do `docs/ROADMAP_V2.md`. Fonte: adendo 3, seção 3.3, de
`docs/PLANO_ANALISE_V2_EXPERIMENTO_MAIOR.md`, e `docs/PREDICOES_V2.md`.

Duas partes, uma por dono de arquivo: **A primeiro** (o mundo), **D depois** (a bancada). O cérebro não muda.

## 1. Os braços

| braço | parte do | o que muda | contraste (secundário) |
|---|---|---|---|
| **P2d** | P2 (fonte `informacao`) | o informante fala da fruta **consumida**, no primeiro passo do dono depois do consumo, em vez de logo depois da oferta | P2 × P2d: o momento |
| **P3i** | P3 com K4 (fonte `dono`) | o julgamento da fruta sai como `informar_fruta_<f>_<bem\|mal>`, não como elogio ou bronca; o `w0_info` do ponto da K2 | P3 × P3i: a interpretação |

O conhecimento é o mesmo nos dois: o efeito real vigente, os `efeitos_reais` da bancada e a troca do mutável. Os eventos ficam fora do
orçamento.

## 2. Parte A, o mundo (chat A; branch `v2-p2d-p3i-mundo`; só `frutas.py` e `config.py`, se precisar de chave)

- Um modo de saída do `JulgadorFruta` (ou um informante novo; escolha e registre) que, em vez de `elogiar`/`repreender`, emite
  `informar_fruta_<f>_<bem|mal>` sobre a fruta consumida:
  - "bem" se o efeito vigente é ≥ 0, como no `DonoInformante`;
  - a neutra também é informada, para o conteúdo seguir o do P2. Confirme essa leitura e registre.
- Mesmo momento do K4: o primeiro passo do dono depois do consumo, fora do orçamento.
- **Gates:**
  - G1;
  - modo desligado = o de hoje, byte a byte, por gabarito gravado antes;
  - uma informação por consumo, no passo seguinte, com o conteúdo do efeito vigente (dos dois lados da troca);
  - não chega ao aprendiz como sinal (espião no `receber_acao_dono`).

## 3. Parte D, a bancada (chat D; branch `v2-p2d-p3i-bancada`; só `experiments/` e `digilab/metrics.py`)

- Os braços `P2d` e `P3i` na bancada.
  - Na `"montagem": "completa"`:
    - o P2d tem as peças do P2 (memória, canais, `w0_info`);
    - o P3i tem as do P3 mais o `w0_info` da config.
  - O K4 do P3i usa o modo informação da parte A.
- `contar_informacoes` e o multiconjunto (fruta, conteúdo) por vida, nas medidas.
- O `sem_ensino` tira essas informações.
- **Gates:**
  - os braços de antes byte a byte (gabarito antes);
  - o P2d sem informante = o P1 completo; o P3i com o julgamento desligado = o P3;
  - P2 e P2d com o mesmo conhecimento; P3 e P3i com os mesmos ticks de julgamento;
  - G1 dos braços novos e dos acoplados;
  - fumaça não canônica.

## 4. Entrega

Um PR por parte, com o relato no corpo e a suíte inteira, mais uma seção no fim do `CLAUDE.md` e outra no fim do `REGISTRO_DESVIOS.md`. Sem
run com faixa reservada. Merge só pelo Matheus.
