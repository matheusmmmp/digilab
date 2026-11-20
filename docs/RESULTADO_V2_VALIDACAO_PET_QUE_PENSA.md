# Resultado — V2: a validação do pet que pensa (J5)

> **V2, congelado em 2026-10-30** (tag `v2-final`). O estado em que este documento fica na V3 está em `docs/FECHAMENTO_V2.md`; o
> plano da V3, em `docs/PLANO_V3.md`.

Data: 2026-10-18. Plano: `docs/PLANO_ANALISE_V2_PET_QUE_PENSA.md`, seções 6 e 7, com o desenho do adendo 5 (a fruta ao lado da ração) e os
números congelados do adendo 6. Autorizada pelo Matheus em 2026-10-18. **Rodou uma vez.**

**Fonte dos números:** `artifacts_v2_pet_que_pensa/validacao_ao_lado/`, com estes arquivos:
- `validacao.json` (as premissas, os contrastes, o Holm, as categorias e a leitura);
- `meta.json`;
- `<braço>/{medidas,meta}.json`.

As vidas (`vidas/*.jsonl`) ficam fora do git e saem de novo da config e do código.

- **O comando:** `python experiments/run_v2_validacao_pet_que_pensa.py --config experiments/configs/v2_pet_que_pensa/validacao_ao_lado.json
  --saida artifacts_v2_pet_que_pensa/validacao_ao_lado --processos 4`.
- **O código:** o orquestrador da validação entrou num commit próprio antes da run (`f54853f`, sobre a `main` `49ff035`). Ele confere os
  números da config contra os artefatos da calibração e se recusa a rodar duas vezes.
- **A run:** a árvore limpa, numa worktree própria; Python 3.13.0, Windows. O `meta.json` traz o sha256 do pacote da bancada.
- **As sementes:** as bases 46101…46505 com K_u = 10, 50 unidades. São 400 vidas: 4 braços × T1 e T2. A run levou 330 s com 4
  processos.
- **O replay:** toda vida foi gravada e rejogada do texto do disco, bit a bit, e o replay da medição também foi conferido. Os gates de
  mecanismo (G-SEM-CREDITO, o congelamento, o G2) passaram em toda vida.
- **Os números congelados** (adendo 6): `ganho_gosto` = S/2, `g_plano` = S, `Δ_T1` = 0,217, `Δ_T2` = 0,286 e a G-APRENDEU a 1/4. O
  bootstrap tem 10.000 reamostragens, semente 4242, agrupado por base.

## Resumo

- **O G-T1 é inconclusivo por premissa:** a G-OPORTUNIDADE do T1 falha por pouco nos quatro braços (de 14 a 16 das 50 unidades sem
  oportunidade, 28% a 32%, contra o limite de 25%).
  - O número sozinho cairia em **equivalente**: média −0,017, IC90 [−0,087; 0,062], dentro de ± 0,217.
- **O G-T2 é inconclusivo por premissa:** nenhuma unidade de nenhum braço teve busca da x depois da mudança. A G-OPORTUNIDADE do T2 falha
  em 50 de 50 unidades, e a G-EXPOSICAO também falha.
- **A G-APRENDEU passa nos quatro braços:** `f_antes` 0,54 [0,46; 0,63] no P1 e 0,53 [0,46; 0,61] nos três com o planejador.
- **Nenhum secundário passa.** O G-T1-CONG passaria pelo número (IC95 [0,015; 0,172], o Holm rejeita), mas as premissas dele também
  falham.
- **A leitura da seção 7:** nenhum primário passa, e os dois não mediram (as premissas). Não é o caso "nenhum passa" da seção 7, que
  lê o planejador; é um J5 sem teste válido. Fica registrado como está.

## 1. As premissas

| premissa | P1 | P1-plan | P1-plan-desfecho | P1-plan-cong |
|---|---|---|---|---|
| G-APRENDEU (`f_antes`, IC95; limiar 1/4) | 0,54 [0,46; 0,63], passa | 0,53 [0,46; 0,61], passa | 0,53 [0,46; 0,61], passa | 0,53 [0,46; 0,61], passa |
| G-OPORTUNIDADE, T1 (sem oportunidade) | 14 de 50, **falha** | 14 de 50, **falha** | 14 de 50, **falha** | 16 de 50, **falha** |
| G-OPORTUNIDADE, T2 | 50 de 50, **falha** | 50 de 50, **falha** | 50 de 50, **falha** | 50 de 50, **falha** |
| G-EXPOSICAO (sem exposição) | 21 de 50, **falha** | 21 de 50, **falha** | 20 de 50, **falha** | 23 de 50, **falha** |

**No T1, as unidades sem oportunidade** são todas do "depois": toda unidade tem oportunidade antes da mudança. 14 a 16 não têm nenhuma
depois da última fruta na mão e até o corte da reexperiência. No piloto (adendo 6) eram de 3 a 5 de 20 (15% a 25%), no limite.

## 2. Os contrastes

| gate | contraste | unidades com valor | média | IC95 | IC90 | p (Holm) | categoria |
|---|---|---|---|---|---|---|---|
| **G-T1** | `q`(P1-plan) − `q`(P1) | 29 | −0,017 | [−0,095; 0,080] | [−0,087; 0,062] | 0,684 (não rejeita) | **inconclusivo por premissa** (pelo número: equivalente) |
| **G-T2** | `m`(P1-plan) − `m`(P1-plan-desfecho) | 0 | — | — | — | — | **inconclusivo por premissa** |
| G-T1-DESF | `q`(P1-plan-desfecho) − `q`(P1) | 29 | −0,052 | [−0,140; 0,074] | | 0,836 (não rejeita) | não passa |
| G-T1-CONG | `q`(P1-plan) − `q`(P1-plan-cong) | 34 | 0,093 | [0,015; 0,172] | | 0,011 (rejeita, limiar 0,0125) | não passa (as premissas falham) |
| G-T2-HAB | `m`(P1-plan) − `m`(P1) | 0 | — | — | — | — | não passa |
| G-T2-CONG | `m`(P1-plan) − `m`(P1-plan-cong) | 0 | — | — | — | — | não passa |

O Holm é de 2 nos primários e de 4 nos secundários, com α 0,05. As unidades com valor são as que têm `q` (ou `m`) nos dois braços do
contraste.

## 3. O descritivo do T1 (não é teste)

| | P1 | P1-plan | P1-plan-desfecho | P1-plan-cong |
|---|---|---|---|---|
| `f_antes` (média, 50 unidades) | 0,540 | 0,533 | 0,533 | 0,533 |
| `f_depois` (média, unidades com valor) | 0,500 (36) | 0,509 (36) | 0,528 (36) | 0,603 (34) |
| `q` (média) | 0,028 | 0,019 | 0,000 | −0,064 |
| oportunidades em que o alvo padrão seria a x | 33,5% | 33,1% | 33,1% | 33,2% |

- **A escolha da x antes da mudança** fica em 53% a 54%, acima do acaso entre os quatro alvos (25%) e acima do que a geometria daria (cerca
  de 33%). É o que a fruta ao lado da ração pedia (adendo 5).
- **Depois da mudança, a escolha quase não cai** em nenhum braço: o `q` vai de −0,06 a 0,03. O pet continua escolhendo a x depois que ela
  passa a fazer mal, com ou sem o planejador.
- O P1-plan-cong, com os dois modelos congelados, tem o `q` mais baixo. É de onde vem o G-T1-CONG positivo.

## 4. O custo

O CPU por vida de 10 dias foi 0,65 s no P1 e de 0,78 a 0,80 s nos braços com o planejador.

## 5. Leitura (seção 7 do plano, com as premissas)

- **Nenhum primário mediu.** O T1 perdeu a G-OPORTUNIDADE por pouco (28% contra 25%). O T2 não teve nenhuma busca, pelo R-16 do adendo
  5: com a x no comedouro, o pet não a procura nas árvores. Pela seção 7, os dois são inconclusivos por premissa, e nada se ajusta olhando
  a validação.
- **O descritivo do T1** mostra o pet escolhendo a favorita bem acima do acaso, sem deixar de escolhê-la depois da mudança, em todos os
  braços. Se o T1 tivesse medido, o número cairia em **equivalente**: o planejador não muda a queda da escolha da x além de ± 0,217. É
  leitura do número, não do gate.
- **Não é evidência para o rótulo "pensa"** (R-7): nenhum primário passa.

## 6. O que fica para o Matheus

- **O J5, como está, termina sem teste válido.** As duas premissas que falharam são de oportunidade, não do planejador.
- **As opções** ficam para decisão. Nenhuma foi aplicada, e qualquer uma pede plano e sementes novos, porque esta validação já rodou:
  - **aceitar e registrar o J5 como inconclusivo por premissa,** com o descritivo do T1 (o pet não revaloriza pela mão em nenhum braço);
  - **um J5 novo para o T2,** com a fruta ao lado parando depois de `T_m`. É a alternativa do R-16 e da PJ5-4;
  - **mais oportunidades depois da mudança no T1,** com uma janela maior ou uma regra de corte da reexperiência diferente.
