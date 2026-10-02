# V2 — marco da rodada 3 (2026-10-01)

Coordenador: chat "Principais jogos Digimon com diálogo". Divisão da rodada 3 em `docs/V2_RODADA_2.md`.

## O que a rodada entregou (tudo na `main`)

| chat | frente | PR | resultado (artefato) |
|---|---|---|---|
| A | A1-BOLA | #127, #128 | **1a-pet PASSA**: brincar com a bola +0,310 [+0,245; +0,375], controle com a bola que o pet não vê +0,036 [−0,025; +0,107]. **Cuidado controlado FALHA**: privação +0,017 [+0,009; +0,028], sem mortes, toda vinda do dono aleatório, que gasta orçamento com a bola. Nos donos coerentes a bola desloca o ensino (atencioso: elogios 93,0 → 61,4). `artifacts_v2_a1/validacao/resultado.json`, `docs/RESULTADO_V2_A1.md` |
| B | L1, validação | #123 | **Negativo** para o braço P3: G3 0,041 bit, G4 do aprendido 0,182, G5(c) +0,0099 [−0,010; +0,025], G6 com pesos no teto. O ensino chega (G3-T 0,663 × instinto 0,577), mas o instinto decide cerca de 80% das decisões. `artifacts_v2_l1/validacao/`, `docs/RESULTADO_V2_L1.md` |
| C | FRUTAS-DEFINICOES | #125 | as quatro variáveis (fome; `incentivo` e `avaliacao` por fruta; efeito no humor; vício como assimetria, no N9), neofobia e preferência inata no genoma, oferta pelo dono e escolha ao comer. `docs/DEFINICOES_FRUTAS_V2.md` |
| D | BANCADA | #126 | orquestrador P0–P3 sobre o mesmo aprendiz, modo acoplado, métricas da pergunta maior; P0 = instinto byte a byte, acoplado reproduz, G1. `experiments/bancada_v2.py` |

Coordenação: `PLANO_V2_PESQUISA.md` revisão 2 (#122: pergunta maior e arquitetura adotadas), decisão "seguir com gates falhando" (#120),
pendências fechadas (#121), remoção de elogiar/repreender adiada para a escolha do produto (#124).

## Decisões do Matheus na rodada

- Seguir mesmo com validações falhando (#120); pergunta maior e arquitetura adotadas (M3, #122); limiar do Mega 0,4 nos v10.
- **Bola:** B1 = tirar `por_bola` do sorteio do dono aleatório nas runs seguintes; B2 = bola fora do orçamento na A1 + L1; B3 = aceitar o relapso.
- **Frutas:** F1–F11 como recomendadas (F8 e F11 não por ora; F4 = gene próprio). F10 aplicada em `DEFINICOES_V2.md`.

## O que a rodada ensinou

1. O aprendiz da L1, com o feedback do dono, aprende pouco e quase nada explicável: o gargalo é o instinto decidindo quase tudo e o teto
   dos pesos. Isso põe peso nas outras fontes de plasticidade (P1, P2), que é a próxima rodada.
2. A bola mostra que um objeto do mundo muda o comportamento do pet sem mexer no cuidado, desde que o dono não troque cuidado por bola.
   O orçamento do dono é um canal de confusão próprio e entra no desenho de todo nó que acrescenta ações ao dono.

## Rodada 4 (divisão)

| chat | frente | tarefa |
|---|---|---|
| A | N4, frutas no mundo | `docs/TAREFA_V2_N4_FRUTAS.md` |
| B | N3, consequência como reforço (P1) | `docs/TAREFA_V2_N3_CONSEQUENCIA.md` |
| C | plano do experimento maior + busca da decomposição da plasticidade | `docs/TAREFA_V2_PLANO_EXPERIMENTO_MAIOR.md` |
| D | bancada: mundos e condições | `docs/TAREFA_V2_BANCADA_MUNDOS.md` |

Reservas (fechadas): N3 calibração 8101…8505, validação 9101…9505; N4 calibração 10101…10505, validação 11101…11505.
Experimento maior: 14101…14505 / 15101…15505 (reservadas; o C só escreve o plano).
