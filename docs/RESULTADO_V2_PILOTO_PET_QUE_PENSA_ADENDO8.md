# Resultado — V2: o piloto do adendo 8 do pet que pensa (J5)

Data: 2026-10-19. Plano: `docs/PLANO_ANALISE_V2_PET_QUE_PENSA.md`, seção 6 e adendo 8 (A8.3 a A8.9). Autorizado pelo Matheus em
2026-10-19.

**Fonte dos números:** `artifacts_v2_pet_que_pensa/piloto_adendo8/`:
- `reval.json`;
- `piloto/piloto.json`;
- `piloto/<braço>/{medidas,meta}.json` e `piloto/meta.json`.

As vidas ficam fora do git.

- **Os comandos:** `python experiments/run_v2_piloto_pet_que_pensa_adendo7.py --config experiments/configs/v2_pet_que_pensa/piloto_adendo8.json
  --saida artifacts_v2_pet_que_pensa/piloto_adendo8 --passo reval`, e depois `--passo piloto --processos 4`.
- **A run:** a `main` `cf8581a`, com a árvore limpa, numa worktree própria; Python 3.13.0, Windows.
  - O `meta.json` traz o sha256 do pacote.
  - Os artefatos estão num commit próprio (`6ba0b69`).
- **As sementes:** as bases 54101…54505 (K_u = 4, 20 unidades), com vidas de 12 dias.
- **Os números do adendo 6, sem recalibrar:** o `ganho_gosto` = S/2 e o `g_plano` = S.
- **O replay:** toda vida foi rejogada do disco bit a bit, e os gates de mecanismo passaram. O piloto levou 186 s com 4 processos.
- **O texto da linha de comando** ("piloto do adendo 7") é o rótulo fixo do orquestrador. Os números são do adendo 8.

## Resumo

- **O T1 passou em todas as premissas, pela primeira vez no J5.**
  - A G-OPORTUNIDADE do T1 tem de 0 a 1 das 20 unidades sem oportunidade, nos quatro braços.
  - A G-APRENDEU passa nos quatro: `f_antes` 0,62 no P1 e 0,52 nos três com o planejador, contra o acaso médio de 0,35 e 0,32.
  - A G-REVAL-POSSIVEL passa (0 de 20).
- **O T2 falha:**
  - **a G-EXPOSICAO** tem de 8 a 10 das 20 unidades sem exposição;
  - **a G-OPORTUNIDADE do T2** tem de 9 a 12 das 20 unidades sem busca contável;
  - nos dois casos, o limite é 25%.
- **As margens têm espaço:** `Δ_T1` = 0,258 e `Δ_T2` = 0,323.
  - O poder do G-T2 é 0,99 já a K_u = 4.
  - O do G-T1 vai de 0,34 (K_u = 4) a 0,74 (K_u = 10), sem chegar a 0,8. Fica K_u = 10 (N = 50).
- **Pela ordem do Gerente** (se uma premissa falhar, parar e relatar), **o adendo 9 e a config da validação não foram escritos.** O plano
  volta ao Matheus.

## 1. As premissas

| premissa | P1 | P1-plan | P1-plan-desfecho | P1-plan-cong |
|---|---|---|---|---|
| G-REVAL-POSSIVEL (por unidade) | 0 de 20 falham | | | |
| G-APRENDEU (`f_antes`, IC95; limiar = o acaso médio) | 0,62 [0,48; 0,73] > 0,351, passa | 0,52 [0,40; 0,63] > 0,319, passa | 0,52 [0,40; 0,63] > 0,319, passa | 0,52 [0,40; 0,63] > 0,319, passa |
| G-OPORTUNIDADE, T1 | 1 de 20, passa | 0 de 20, passa | 0 de 20, passa | 0 de 20, passa |
| G-OPORTUNIDADE, T2 | 9 de 20, **falha** | 10 de 20, **falha** | 12 de 20, **falha** | 10 de 20, **falha** |
| G-EXPOSICAO | 9 de 20, **falha** | 8 de 20, **falha** | 10 de 20, **falha** | 9 de 20, **falha** |

## 2. Por que o T2 falhou (os motivos por unidade)

| | P1 | P1-plan | P1-plan-desfecho | P1-plan-cong |
|---|---|---|---|---|
| unidades com busca antes e depois | 11 | 10 | 8 | 10 |
| **sem exposição** (as buscas depois não contam) | 9 | 4 | 6 | 5 |
| sem busca antes e sem depois | 0 | 4 | 4 | 4 |
| exposto, sem busca depois | 0 | 2 | 2 | 1 |
| as idas às árvores depois de `T_m` (velhas / novas, somadas) | 17 / 16 | 52 / 38 | 59 / 23 | 55 / 28 |
| x de árvore nova comidas depois de `T_m` (somadas) | 53 | 49 | 41 | 38 |

- **O motivo principal é a exposição.** Nas unidades sem exposição, o pet quase não vai às árvores depois de `T_m`: de 0 a 8 idas por
  unidade, e nenhuma x de árvore nova comida. Ele não chega perto das árvores novas, e a x delas nunca aparece à vista.
  - É o R-20 do adendo 7: sem a fruta ao lado depois de `T_m` (ela para no T2), parte dos pets volta a só comer a ração.
- **Onde há exposição, a busca existe e vai às novas:** o `f_depois` médio fica de 0,83 a 0,95, contra 0,35 antes.
- **A busca nova (A8.4) funcionou onde o pet saiu:**
  - a maior parte das buscas depois é com a x à vista (40 a 61 por braço, contra 3 a 35 sem ela);
  - o corte do T2 saiu, e nenhuma unidade foi cortada.
- **Nos três braços com o planejador, 4 unidades não têm busca antes da mudança.** Os três braços só diferem depois de `T_m`, então o "antes"
  deles é o mesmo.

## 3. O T1 (descritivo)

| | P1 | P1-plan | P1-plan-desfecho | P1-plan-cong |
|---|---|---|---|---|
| x retiradas em `T_m` (média por unidade) | 5,2 | 5,3 | 5,3 | 5,3 |
| sem oportunidade | 1 (pela janela) | 0 | 0 | 0 |
| `f_antes` / `f_depois` (média) | 0,62 / 0,54 | 0,52 / 0,60 | 0,52 / 0,55 | 0,52 / 0,68 |

- **A x sair das árvores tirou o corte por árvore:** nenhuma unidade foi cortada pela x de uma árvore. O T1 tem oportunidade em todos os
  braços.
- **A escolha da x não cai depois da mudança** nos braços com o planejador (0,52 para 0,55 a 0,68). No P1 cai um pouco (0,62 para 0,54). O
  descritivo dos contrastes do T1 (não é evidência): o G-T1 tem média −0,158, IC95 [−0,54; 0,21].

## 4. As margens, o N e o custo (só relato; o adendo 9 não foi escrito)

- **`Δ_T1` = 0,258** (o P1-plan, 20 unidades) e **`Δ_T2` = 0,323** (16 unidades).
- **O poder:**

  | K_u | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
  |---|---|---|---|---|---|---|---|
  | G-T1 | 0,34 | 0,41 | 0,49 | 0,57 | 0,63 | 0,69 | 0,74 |
  | G-T2 | 0,99 | 1,00 | 1,00 | 1,00 | 1,00 | 1,00 | 1,00 |

  Os secundários a K_u = 10 (α 0,0125):

  | secundário | poder |
  |---|---|
  | G-T1-CONG | 1,00 |
  | G-T1-DESF | 0,65 |
  | G-T2-CONG | 1,00 |
  | G-T2-HAB | 0,99 |

- **O custo:** 1,06 s de CPU por vida de 12 dias (0,91 no P1). N = 50 daria 400 vidas, cerca de 7 min de CPU.

## 5. O que fica para o Matheus

- **O T1 está pronto para a validação.** As premissas passam, e a margem tem espaço. O G-T1 sai subpotenciado (0,74 a K_u = 10).
- **O T2 falha pela exposição**, não pela definição da busca: a busca nova mede onde o pet sai de casa. As opções (nenhuma aplicada):
  - **rodar a validação com o T2 como inconclusivo por premissa,** se a G-OPORTUNIDADE e a G-EXPOSICAO falharem de novo. Pela seção 7,
    o G-T1 sozinho é um primário;
  - **manter a fruta ao lado no T2 até a exposição** (ou até um prazo depois de `T_m`). O pet continua saindo, e a x cai no lugar novo
    perto de onde ele passa. Pede um adendo; é o que o R-20 previa;
  - **aceitar o J5 só com o T1.**
- **Nada foi ajustado olhando o piloto.**
