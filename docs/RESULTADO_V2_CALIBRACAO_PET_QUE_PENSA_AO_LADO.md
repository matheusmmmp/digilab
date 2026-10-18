# Resultado — V2: a calibração do pet que pensa com a fruta ao lado da ração (J5, adendo 5)

Data: 2026-10-18. Plano: `docs/PLANO_ANALISE_V2_PET_QUE_PENSA.md`, adendo 5 (A5.3 a A5.8), com os números congelados no adendo 6.
Autorizada pelo Matheus em 2026-10-18.

**Fonte dos números:** `artifacts_v2_pet_que_pensa/calibracao_ao_lado/`:
- `ganho_gosto/ganho_gosto.json`, `ganho_gosto/ganho_<g>/{medidas,meta}.json` e o `meta.json` do passo;
- `g_plano/g_plano.json`, `g_plano/g_plano_<g>/{medidas,meta}.json` e o `meta.json` do passo;
- `reval.json`;
- `g_plano/piloto/piloto.json` e `g_plano/piloto/<braço>/{medidas,meta}.json`.

As vidas (`vidas/*.jsonl`) ficam fora do git e saem de novo da config e do código.

- **O comando,** um por passo: `python experiments/run_v2_calibracao_pet_que_pensa_paladar.py --config
  experiments/configs/v2_pet_que_pensa/calibracao_ao_lado.json --saida artifacts_v2_pet_que_pensa/calibracao_ao_lado --passo <passo>
  --processos 4`.
- **A run:** a `main` `0896219`, com a árvore limpa, numa worktree própria; Python 3.13.0, Windows. O `meta.json` de cada passo traz o
  sha256 do pacote da bancada.
- **O tempo:** o `ganho_gosto` levou 55 s, o `g_plano` 56 s e o piloto 149 s. A run inteira levou cerca de 5 min.
- **As sementes:** as bases 51101…51505 (K_u = 4, prefixo `pet_que_pensa`, 20 unidades). A validação (46101…) não rodou.
- **O replay:** toda vida foi gravada e rejogada do texto do disco, bit a bit, e o replay da medição também foi conferido. Os gates de
  mecanismo (G-SEM-CREDITO, o congelamento, o G2) passaram em toda vida.

## Resumo

- **O `ganho_gosto` = S/2 (512), fechou** (fração lado a lado 0,654, em [0,25; 0,75]).
- **O `g_plano` = S (1024), fechou** (0,152).
- **A G-REVAL-POSSIVEL passa:** nenhuma unidade falha.
- **O T1 ganhou espaço, pela primeira vez no J5.** A G-APRENDEU passa nos quatro braços, com `f_antes` de 0,43 a 0,55 contra o limiar de
  1/4. `Δ_T1` = 0,217.
- **O T2 continua sem medida:** nenhuma unidade de nenhum braço teve busca da x depois da mudança. A G-OPORTUNIDADE do T2 falha em 20 de
  20 unidades. `Δ_T2` = 0,286 sai das 7 unidades com busca antes.
- **A regra da seção 6:**
  - as duas margens passam de 0,05, então a validação **pode** rodar;
  - nem K_u = 10 chega a 0,8 no G-T1 (0,687);
  - o poder do G-T2 não sai: nenhuma unidade com valor;
  - pela seção 6, a validação rodaria com K_u = 10 (N = 50), com o poder declarado.
- **Ela não roda aqui:** fica para o sim do Matheus (seção 6 deste relatório).

## 1. O `ganho_gosto` (o P1, só a fase 1)

| `ganho_gosto` | média da fração lado a lado (dias 4 a 6) | por unidade | decisões lado a lado | com fruta | unidades sem decisão | CPU por vida |
|---|---|---|---|---|---|---|
| **S/2 (512)** | **0,654** | 0,35 a 1,00 | 274 | 163 | 0 | 0,52 s |
| S (1024) | 0,679 | 0,35 a 1,00 | 279 | 176 | 0 | 0,53 s |
| 2S (2048) | 0,685 | 0,30 a 1,00 | 265 | 171 | 1 | 0,53 s |
| 4S (4096) | 0,634 | 0,33 a 1,00 | 263 | 162 | 2 | 0,51 s |

- Todos os pontos caem na faixa, e a regra pega o menor.
- A grade de novo muda pouco a vida: 17 das 20 unidades têm a mesma fração em S/2 e em S.

## 2. O `g_plano` (o P1-plan, só a fase 1, no `ganho_gosto` = S/2)

| `g_plano` | média da fração da sonda (dias 4 a 6) | por unidade | decisões com alvo | o plano mudou a escolha |
|---|---|---|---|---|
| S/4 (256) | 0,067 | 0,017 a 0,160 | 1.225 | 81 |
| S/2 (512) | 0,098 | 0,048 a 0,147 | 1.267 | 125 |
| **S (1024)** | **0,152** | 0,056 a 0,264 | 1.175 | 176 |

É o mesmo ponto dos adendos 1 e 4.

## 3. A G-REVAL-POSSIVEL (sem vida, no `ganho_gosto` = S/2)

- **Passa:** 0 de 20 unidades falham. A x sorteou `c` em 9 unidades, `a` em 7 e `b` em 4.
- **A x depois da mudança** fica abaixo das três alternativas em 19 unidades, e de duas na outra. A menor folga é 45.

## 4. O piloto (os 4 braços, T1 e T2, no `ganho_gosto` = S/2 e no `g_plano` = S)

**As premissas (só relato):**

| premissa | P1 | P1-plan | P1-plan-desfecho | P1-plan-cong |
|---|---|---|---|---|
| G-APRENDEU (`f_antes`, IC95; limiar 1/4) | **0,55 [0,43; 0,67]**, passa | **0,43 [0,33; 0,52]**, passa | **0,43 [0,33; 0,52]**, passa | **0,43 [0,33; 0,52]**, passa |
| G-OPORTUNIDADE, T1 (sem oportunidade) | 3 de 20, passa | 4 de 20, passa | 4 de 20, passa | 5 de 20, passa |
| G-OPORTUNIDADE, T2 | 20 de 20, falha | 20 de 20, falha | 20 de 20, falha | 20 de 20, falha |
| G-EXPOSICAO (sem exposição) | 11 de 20, falha | 8 de 20, falha | 9 de 20, falha | 10 de 20, falha |

**As margens:** `Δ_T1` = 0,217 (as 20 unidades com oportunidade antes) e `Δ_T2` = 0,286 (7 unidades com busca antes). As duas têm espaço.

**O N** (o menor K_u com poder ≥ 0,8 nos dois primários):

| K_u | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|
| poder do G-T1 | 0,276 | 0,352 | 0,436 | 0,518 | 0,589 | 0,637 | 0,687 |

- O poder do G-T2 não sai: nenhuma unidade com busca depois da mudança.
- Pela seção 6, sem chegar, fica K_u = 10 (N = 50).
- **Os secundários** a K_u = 10:
  - o G-T1-CONG tem poder 0,83 (a α 0,0125) e 0,96 (a 0,05);
  - o G-T1-DESF, 0,56 e 0,78;
  - os do T2 não saem.

**Os contrastes** (descritivo, não é evidência):
- **o G-T1:** média 0,033, IC95 [−0,26; 0,37], 15 unidades;
- **o G-T1-CONG e o G-T1-DESF:** média 0,10;
- **o G-T2 e os secundários dele:** nenhuma unidade com valor.

**O descritivo da fruta ao lado** (T1):

| | P1 | P1-plan |
|---|---|---|
| oportunidades do T1 | 575 | 605 |
| em que o alvo padrão (a comida boa mais perto) seria a x | 33,7% | 27,3% |
| `f_antes` (média) | 0,55 | 0,43 |
| `f_depois` (média, unidades com valor) | 0,62 (17) | 0,39 (16) |
| frutas maduras comidas que vieram da regra | 732 de 985 | 661 de 934 |
| fração de fruta entre os consumos (a vida toda) | 0,395 | 0,405 |

- **A escolha da x passa a geometria:** o pet escolhe a x em 43% a 55% das oportunidades antes da mudança, e o alvo padrão seria a x em
  27% a 34% delas. É leitura do descritivo (R-15).
- **O querer aprendido no P1** vai à x: no fim da fase 1, `comida:<x>` vale em média 226 na `fome_moderada`, contra −177 de
  `comida:racao`. No P1-plan, não: na `fome_moderada`, `comida:<x>` vale 0 e `comida:racao` 279, e na `fruta_no_cenario` os dois
  ficam perto (529 e 510).
- **A ração** continua sendo o tipo mais comido nas 20 unidades.
- **O T2:** a x da regra foi comida depois da mudança 75 vezes no P1 e 55 no P1-plan, somadas as 20 unidades. O pet não precisa buscar a x nas árvores, que é o R-16 do adendo.

**O custo:** 0,74 s de CPU por vida no P1 e cerca de 0,90 s nos braços com o planejador (0,86 s em média). A validação com N = 50 daria
400 vidas, cerca de 6 min de CPU.

## 5. Leitura

- **A fruta ao lado da ração fez o que o adendo 5 pedia no T1.** O pet aprende a x e a escolhe acima do acaso entre os quatro alvos, e
  acima do que a geometria daria.
- **O T2 ficou sem buscas:** a x está no comedouro, então o pet não a procura nas árvores. Era o R-16, e o PJ5-4 escolheu manter a regra
  igual nos dois protocolos. Com isso, o T2 da validação sai inconclusivo por premissa (G-OPORTUNIDADE).
- **O G-T1 está subpotenciado a K_u = 10** (0,687): a regra roda assim mesmo, com o poder declarado.

## 6. O que fica para o Matheus

- **A validação (46101…46505, K_u = 10, N = 50)** pode rodar pela seção 6 e pede o sim dele. O que se espera dela:
  - **o T1:** o primário com poder 0,69 e os secundários do T1 com poder razoável;
  - **o T2:** inconclusivo por premissa, pela G-OPORTUNIDADE.
- **Antes de rodar, uma opção** (não aplicada): parar a fruta ao lado no T2 depois de `T_m`. É a alternativa do R-16 e o custo de errar
  da PJ5-4: dá ao T2 a chance de medir, ao preço de o T1 e o T2 deixarem de ter o mesmo mundo depois da mudança. Pediria um adendo antes
  da validação.
- **Nada foi recalibrado olhando o piloto.**
