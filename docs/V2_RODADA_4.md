# V2 — marco da rodada 4 (2026-10-04)

Coordenador: chat "Principais jogos Digimon com diálogo". Divisão da rodada 4 em `docs/V2_RODADA_3.md` e `docs/V2_RODADA_4_PROMPTS.md`.

## O que a rodada entregou (tudo na `main`)

| chat | frente | PR | resultado (artefato) |
|---|---|---|---|
| B | N3, consequência como sinal (P1) | #135, #136 | **Negativo**: G-P1 privação P0 − P1 +0,0008 [−0,0067; +0,0077] na validação (+0,0051 [+0,0008; +0,0091] na calibração); G6 com 20 de 20 vidas no teto. O P1 aprende a comer na fome moderada (50% → 94%) e a poupar energia, mas a privação depende do cuidado do dono; acerto na tarefa do dono 0,593 → 0,444. `artifacts_v2_n3/validacao/`, `docs/RESULTADO_V2_N3.md` |
| A | N4, frutas no mundo | #132, #133 | **G-F7 passa** (saúde frutas − acoplado −0,004 [−0,008; 0,000], sem mortes); **G-SEP falha** pela (ii), qual fruta, +0,110 [−0,007; +0,213]; **G-SSE falha** pela medida (a regressão não tinha a preferência inata). No descasado o pet come a fruta ruim em 39% dos consumos. `artifacts_v2_n4/validacao/`, `docs/RESULTADO_V2_N4.md` |
| C | plano do experimento maior | #134 | `docs/PLANO_ANALISE_V2_EXPERIMENTO_MAIOR.md` com as cinco predições registradas antes; E1–E8 aprovadas; prompt 11 (decomposição da plasticidade) fora do repositório |
| D | bancada: mundos | #137 | mundos `padrao`, `bola` (B1, B2) e `bola_a1`; contrato das condições (descasado e mutável esperando as frutas); acoplado com mundo |

## Decisões do Matheus na rodada

- E1–E8 do plano do experimento maior, como recomendadas. A E2 põe o humor no sinal do P1 quando a mudança vem de comer fruta.
- N1–N4 das frutas, como recomendadas (`docs/RESULTADO_V2_N4.md`):
  - trocar a medida da saciedade no próximo plano;
  - ampliar a grade de `w_fruta`;
  - manter a nutrição;
  - herança dos genes das frutas na fase 3.

## O que a rodada ensinou

1. **O aprendiz ainda não vê o mundo novo.** Os lobos não percebem a bola nem as frutas (as regras `bola_no_cenario` e
   `fruta_no_cenario` são do instinto), e a escolha da fruta não passa pelo lobo de decisão. Sem isso, P1, P2 e P3 ficam cegos à
   condição descasado, e o experimento maior não testa nada. É o pré-requisito da rodada 5.
2. O P1 no mundo padrão aprende o que a consequência imediata mostra (comer, descansar), mas a privação é decidida pelo cuidado do dono.
   No mundo das frutas, com o humor no sinal (E2), a consequência passa a ter onde aparecer.
3. Teto dos pesos: 20 de 20 vidas no N3 e 12 de 20 na L1. O teto 1·S segura o aprendiz nas duas fontes e entra na revisão das
   validações.

## Rodada 5 (divisão)

A prévia em `V2_RODADA_4_PROMPTS.md` (B no N5, A apoiando, C no N6, D no N7) muda por causa do achado 1: o N5 precisa de um aprendiz que
veja as frutas.

| chat | frente | tarefa |
|---|---|---|
| B | lobos que veem o mundo + E2 | `docs/TAREFA_V2_LOBOS_MUNDO.md` |
| A | eventos de informação do dono no mundo das frutas (N5, lado do mundo) + a medida nova da saciedade (N1) | `docs/TAREFA_V2_N5_MUNDO.md` |
| C | desenho e plano de análise do N5 | `docs/TAREFA_V2_N5_PLANO.md` |
| D | bancada: mundos das frutas (casado com frutas, descasado, mutável) e unidades derivadas (E3) | `docs/TAREFA_V2_BANCADA_FRUTAS.md` |

Reservas: N5 12101…12505 / 13101…13505 (só depois do plano do C). Nenhuma run de validação nesta rodada; o N6 e o N7 ficam para a
rodada 6, junto com a calibração do experimento maior.
