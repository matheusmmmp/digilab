# V2 — marco da rodada 6 (2026-10-05)

Coordenador: chat "Principais jogos Digimon com diálogo". Divisão da rodada 6 em `docs/V2_RODADA_5.md`.

## O que a rodada entregou (tudo na `main`)

| chat | frente | PR | resultado |
|---|---|---|---|
| D | BANCADA-N5 | #148 | a bancada cria os lobos vendo o mundo; fonte `informacao` (P2, P2e, P2a) |
| B | N5-CEREBRO | #147 | entrada `info` dos lobos só na escolha da fruta, peso compartilhado, `w0_info` (0 = vida de antes) |
| A | N5-ACOPLADO | #149 | informante acoplado (P2a, rng própria); motivo das regras novas; correção do `PoliticaComMotivo`, que não repassava a escolha da fruta nem a E2 |
| C | N6-PLANO | #146 | plano da memória (quatro marcos); N6-1 a N6-10 aprovadas; faixas 19101…19505 / 20101…20505 |
| B | REVISAO-APRENDIZ | #151 | diagnóstico (só calibração, 18101…18505): o teto segura no P3; a janela de crédito e a exposição não ajudam. Achado pós hoc: o P1 aprende qual fruta evitar, mas a decisão de comer não sabe qual fruta está no cenário (55% dos consumos com uma fruta só). `docs/RESULTADO_V2_REVISAO_APRENDIZ.md` |

Suíte depois dos merges: 886 passados, 1 pulado (#151).

## Decisões do Matheus

N6-1 a N6-10 e R1–R4, todas como recomendadas:
- R1: o ponto de partida das calibrações é o T3 (teto 16·S);
- R2: a decisão de comer passa a ver qual fruta está no cenário;
- R3: o traço de elegibilidade fica desligado;
- R4: a exposição fica como está.

## Rodada 7 (divisão)

| chat | frente | tarefa | ordem |
|---|---|---|---|
| A | o mundo diz qual fruta está no cenário | `docs/TAREFA_V2_FRUTA_NO_CENARIO.md`, parte A | primeiro |
| B | a decisão de comer lê isso; depois, calibração e validação do N5 no ponto T3 | `docs/TAREFA_V2_FRUTA_NO_CENARIO.md`, parte B | depois do A |
| D | faixas reservadas, ponto T3 na bancada, orquestrador do experimento maior | `docs/TAREFA_V2_BANCADA_EXPERIMENTO.md` | em paralelo |
| C | plano do N7 (arbitragem) | `docs/TAREFA_V2_N7_PLANO.md` | em paralelo |

O N6 (memória) é implementado depois do N5, pelo chat B (o lobo de memória fica em `lobos.py`).
