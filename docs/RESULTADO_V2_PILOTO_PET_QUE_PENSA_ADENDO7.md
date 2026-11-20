# Resultado — V2: o piloto do adendo 7 do pet que pensa (J5)

> **V2, congelado em 2026-10-30** (tag `v2-final`). O estado em que este documento fica na V3 está em `docs/FECHAMENTO_V2.md`; o
> plano da V3, em `docs/PLANO_V3.md`.

Data: 2026-10-19. Plano: `docs/PLANO_ANALISE_V2_PET_QUE_PENSA.md`, seção 6 e adendo 7 (A7.2 a A7.8). Autorizado pelo Matheus em
2026-10-19.

**Fonte dos números:** `artifacts_v2_pet_que_pensa/piloto_adendo7/`:
- `reval.json`;
- `piloto/piloto.json`;
- `piloto/<braço>/{medidas,meta}.json` e `piloto/meta.json`.

As vidas (`vidas/*.jsonl`) ficam fora do git e saem de novo da config e do código.

- **Os comandos:** `python experiments/run_v2_piloto_pet_que_pensa_adendo7.py --config experiments/configs/v2_pet_que_pensa/piloto_adendo7.json
  --saida artifacts_v2_pet_que_pensa/piloto_adendo7 --passo reval`, e depois `--passo piloto --processos 4`.
- **A run:** a `main` `ec0530e`, com a árvore limpa, numa worktree própria; Python 3.13.0, Windows.
  - O `meta.json` traz o sha256 do pacote da bancada.
  - Os artefatos estão num commit próprio (`f03dcf3`).
- **As sementes:** as bases 52101…52505 (K_u = 4, 20 unidades), com vidas de 12 dias (`D_a` = 7 e a janela de 5).
- **Os números do adendo 6, sem recalibrar** (PJ7-5): o `ganho_gosto` = S/2 e o `g_plano` = S.
- **O replay:** toda vida foi rejogada do disco bit a bit, e os gates de mecanismo passaram em toda vida. O piloto levou 308 s com 4
  processos.

## Resumo

- **A G-REVAL-POSSIVEL passa:** 0 de 20 unidades falham.
- **A G-APRENDEU passa nos quatro braços,** pelo acaso médio. O P1 tem `f_antes` 0,55 [0,42; 0,68] contra o limiar 0,346; os três com o
  planejador, 0,67 [0,57; 0,77] contra 0,318.
- **A G-EXPOSICAO passa agora:** de 1 a 5 das 20 unidades sem exposição.
- **A G-OPORTUNIDADE falha:**
  - **no T1, só no P1:** 6 das 20 unidades sem oportunidade, 30% contra 25%. Nos três com o planejador passa (1 de 20);
  - **no T2, em todos os braços:** 19 ou 20 das 20 unidades sem busca depois da mudança.
- **As margens têm espaço:** `Δ_T1` = 0,333 e `Δ_T2` = 0,163. O N fica em K_u = 10 (N = 50): o G-T1 chega a 0,83, e o poder do G-T2 não
  sai.
- **Pela ordem do Gerente** (se a G-OPORTUNIDADE falhar, parar e relatar), **o adendo 8 e a config da validação não foram escritos.** O
  plano volta ao Matheus.

## 1. As premissas

| premissa | P1 | P1-plan | P1-plan-desfecho | P1-plan-cong |
|---|---|---|---|---|
| G-APRENDEU (`f_antes`, IC95; limiar = o acaso médio) | 0,55 [0,42; 0,68] > 0,346, passa | 0,67 [0,57; 0,77] > 0,318, passa | 0,67 [0,57; 0,77] > 0,318, passa | 0,67 [0,57; 0,77] > 0,318, passa |
| G-OPORTUNIDADE, T1 | 6 de 20, **falha** | 1 de 20, passa | 1 de 20, passa | 1 de 20, passa |
| G-OPORTUNIDADE, T2 | 19 de 20, **falha** | 19 de 20, **falha** | 20 de 20, **falha** | 20 de 20, **falha** |
| G-EXPOSICAO | 5 de 20, passa | 4 de 20, passa | 1 de 20, passa | 2 de 20, passa |

## 2. Por que faltou oportunidade (o descritivo do A7.6)

**T1:**

| | P1 | P1-plan | P1-plan-desfecho | P1-plan-cong |
|---|---|---|---|---|
| unidades com oportunidade antes e depois | 14 | 19 | 19 | 19 |
| sem oportunidade, pelo corte da x de uma **árvore** | 6 | 1 | 1 | 1 |
| sem oportunidade, pela janela | 0 | 0 | 0 | 0 |
| o corte veio da regra (com oportunidade antes) | 14 | 19 | 19 | 19 |
| a latência mediana até o corte | 0,44 d | 0,44 d | 0,44 d | 0,44 d |
| `f_antes` / `f_depois` (média) | 0,55 / 0,62 | 0,67 / 0,46 | 0,67 / 0,46 | 0,67 / 0,49 |

A oportunidade nova (qualquer alternativa ao lado) resolveu o caso 1 do A7.1 nos braços com o planejador. No P1, o pet come a x numa
árvore antes de qualquer decisão lado a lado em 6 unidades: é o R-19.

**T2:**

| | P1 | P1-plan | P1-plan-desfecho | P1-plan-cong |
|---|---|---|---|---|
| unidades com busca antes da mudança | 20 | 20 | 20 | 20 |
| unidades com busca depois | 1 | 1 | 0 | 0 |
| sem busca depois, pelo corte (x de uma árvore / x da regra que sobrou) | 12 / 1 | 13 / 5 | 15 / 5 | 14 / 5 |
| sem busca depois, pela janela | 6 | 1 | 0 | 1 |
| decisões às árvores velhas / novas depois de `T_m` | 15 / 14 | 30 / 49 | 41 / 38 | 47 / 39 |

- **A busca existe antes** nas 20 unidades, agora com a fome fora dela (PJ7-4). Nos adendos 1 e 4 ela não existia.
- **Depois da mudança,** o pet vai às árvores, mas com a x já à vista: pela definição, a decisão com a x à vista não é busca. A primeira x
  que ele come encerra a medida (o corte). Em geral é a x de uma árvore nova, ou uma fruta da regra que ficou no chão.
- **É o R-19 no T2:** a janela maior não ajuda, porque o corte chega antes, com mediana de 1,3 a 1,4 dia.

## 3. As margens e o N (só relato; o adendo 8 não foi escrito)

- **`Δ_T1` = 0,333:** a média de `f_antes` do P1-plan é 0,667, nas 20 unidades.
- **`Δ_T2` = 0,163:** a média de 1 − `f_antes` do P1-plan no T2, nas 20 unidades.
- **O poder do G-T1:**

  | K_u | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
  |---|---|---|---|---|---|---|---|
  | poder | 0,43 | 0,52 | 0,60 | 0,67 | 0,75 | 0,77 | 0,83 |

  A regra pede os dois primários a 0,8. O do G-T2 não sai: nenhuma unidade com valor nos dois braços. Então fica K_u = 10.
- **Os secundários do T1** a K_u = 10 (a α 0,0125): o G-T1-CONG tem poder 1,00, e o G-T1-DESF, 0,75.
- **O descritivo dos contrastes** (não é evidência):
  - o G-T1 tem média 0,238, IC95 [0,042; 0,389], em 14 unidades;
  - o G-T1-DESF, a mesma;
  - o G-T1-CONG, 0,035;
  - os do T2 não têm valor.

## 4. O custo

O CPU por vida de 12 dias foi 1,25 s no P1 e cerca de 1,54 s nos braços com o planejador (1,47 s em média). Com N = 50, seriam 400 vidas,
cerca de 10 min de CPU.

## 5. O que fica para o Matheus

- **O que mudou desde a validação:**
  - o T1 tem oportunidade nos braços com o planejador, e o descritivo dele mostra a queda da escolha da x (0,67 para 0,46);
  - a exposição do T2 passa;
  - o que falta é a busca do T2 depois da mudança, e o T1 do P1, o braço de controle.
- **As opções** (nenhuma aplicada):
  - **tirar a x das árvores no T1 depois de `T_m`,** a próxima opção do R-19, fora do adendo 7. Mata o corte por árvore no P1 e
    salva a G-OPORTUNIDADE do T1. Não resolve o T2;
  - **no T2, contar a ida às árvores novas com a x à vista,** ou não cortar pela x de uma árvore nova. Muda a definição da busca, então
    pede um adendo;
  - **rodar a validação só do T1,** com o T2 registrado como inconclusivo por premissa. Pela seção 7, o G-T1 sozinho é um primário. O
    P1 falhando a G-OPORTUNIDADE do T1 deixa o G-T1 inconclusivo por premissa, a não ser que a opção acima entre antes;
  - **aceitar o J5 como está.**
- **Nada foi ajustado olhando o piloto.**
