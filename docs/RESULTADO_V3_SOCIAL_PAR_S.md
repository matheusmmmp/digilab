# RESULTADO V3 — SOCIAL_PAR S3: os braços C, B1 e B2

- **Plano:** `docs/PLANO_ANALISE_V3_SOCIAL_PAR_S.md`.
  - O plano foi APROVADO pelo Matheus em 2026-11-18 ("Aprovado"), e o adendo 1 também ("Aprovo o adendo 1").
  - O substrato foi aprovado no checkpoint S3, com "Aprovado, rodar como está" (D-SP-51).
- **A run:** `python experiments/run_v3_social_par_s.py --config experiments/configs/v3_social_par_s/run.json --processos 4`, uma vez.
  - Rodou em 2026-11-19, das 00:52:16 às 01:14:06.
  - Usou o commit e9f4368e da `main` (o merge do #1006), com o git limpo. O `pre_run` aceitou a run, sem nenhuma outra run ativa.
  - São 750 pares: 200 bases por braço (103001…103200, k = 1) e 50 pares do G-DET por braço (103301…103350).
- **Artefatos:** `artifacts_v3_social_par_s/run/`, com o `meta.json`, o `medidas.json`, o `resultado.json` e os 750 pares em `vidas/`.
- **Os gates de cada par:** o G-INSTR (a VIVO e a GRAV iguais até o t0) e o G1 (as condições refeitas com o mesmo sha256) passaram nos
  750 pares. A run para no primeiro par que falha, e não parou.

## O controle positivo: G-DET (seção 3)

O seguidor de regra (`SeguidorPuro`) entra no lugar de P. O gate passa se o IC95 do D_A ficar todo abaixo de −4 decisões.

| braço | n | média | IC95 | passa |
|---|---|---|---|---|
| C | 49 de 50 | −20,06 | [−27,78; −12,34] | **sim** |
| B1 | 50 de 50 | −69,58 | [−80,38; −58,78] | **sim** |
| B2 | 49 de 50 | −16,12 | [−21,89; −10,36] | **sim** |

- **O instrumento vê o social nos três braços.** O risco do D-SP-50 não se confirmou.
- No C e no B2, um dos 50 pares do G-DET não entra no D_A, porque os dois já estão em contato no t0 (`elegivel_a`).

## As premissas (seção 5)

| braço | PA-1, a janela cabe | PA-2, elegíveis no A | PA-3, há contato na janela | PB-1, elegíveis no B |
|---|---|---|---|---|
| C | 200/200 | 200/200 | 200/200 | **0** (mínimo de 100) |
| B1 | 200/200 | 200/200 | 180/200 (0,90) | **0** |
| B2 | 200/200 | 200/200 | 200/200 | **13** |

O A é conclusivo nos três braços. **O B é inconclusivo por premissa nos três.**

## O A: o primário

**D_A = T\*c_VIVO − T\*c_GRAV:** o tempo até o contato (1 célula), em decisões. Um valor negativo quer dizer que F e P se tocam mais
depressa quando P responde. A margem é δ_A = 4.

| braço | n | média | dp | IC95 | meia-largura | p bilateral | classe |
|---|---|---|---|---|---|---|---|
| C | 200 | +0,145 | 4,30 | [−0,454; +0,744] | 0,60 | 0,634 | **≈ 0** |
| B1 | 200 | −0,815 | 6,88 | [−1,775; +0,145] | 0,96 | 0,096 | **≈ 0** |
| B2 | 200 | +0,490 | 9,82 | [−0,880; +1,860] | 1,37 | 0,481 | **≈ 0** |

- **Nos três braços, o IC fica dentro de ±δ_A.** A meia-largura não passa de δ_A/2 = 2 em nenhum.
- **A leitura escrita antes (seção 7):** "nulo com um instrumento que vê". O pet de hoje não responde ao parceiro em nenhum dos três
  substratos.
  - O mesmo instrumento separa o seguidor de regra por 16 a 70 decisões.
  - O pet de hoje não sai de ±1,9 decisão.

**O conjunto (seção 7):** o G-DET passa no B1, e o D_A dá ≈ 0 no B1. Pela regra escrita antes, o social não existe no pet de hoje,
mesmo num substrato que o deixa ver, e o próximo passo é mecanismo (M1–M4), não mais substrato.

## O B: a bola

- **No C e no B1,** não houve nenhum par elegível.
- **No B2,** houve 13 pares elegíveis, abaixo do mínimo de 100. O D_B desses 13 é +0,120, com IC95 [−0,017; +0,257]. Ele **não se lê**,
  porque a premissa falhou.
- **O B2 deu mais chutes, mas não o bastante:**
  - na VIVO, A deu 0,505 chute por dia e B deu 0,604. No B1 foram 0,054 e 0,047; no C, nenhum;
  - o previsto era mais de 1 chute por dia de P e ao menos 100 elegíveis, e não se cumpriu;
  - o B segue sem leitura, e sem controle positivo (seção 3).

## Os secundários (Holm, α = 0,05)

Nenhum rejeita em nenhum braço.

| braço | S1, T\*c_GRAV − T\*c_OUTRA (IC95) | S2, fração perto VIVO − GRAV (IC95) | S3, contingência F→P (p ajustado) |
|---|---|---|---|
| C | −1,72 [−5,02; +1,59] | −0,0031 [−0,0174; +0,0112] | 1,000 |
| B1 | −2,75 [−8,86; +3,36] | +0,0058 [−0,0012; +0,0129] | 0,434 |
| B2 | −0,98 [−4,42; +2,46] | −0,0128 [−0,0316; +0,0060] | 0,543 |

## O substrato (descritivo; não decide nada)

| braço | distância no t0 (média) | T\*c_GRAV (média) | T\*c_VIVO (média) | contato fora da casa (VIVO) | chutes por dia (VIVO, A / B) |
|---|---|---|---|---|---|
| C | 4,53 | 16,6 | 16,8 | 0,005 | 0 / 0 |
| B1 | 4,75 | 52,2 | 51,3 | 0,428 | 0,054 / 0,047 |
| B2 | 4,53 | 16,0 | 16,5 | 0,020 | 0,505 / 0,604 |

- **O B1 fez o que o plano previa:** o T\*c_GRAV passou de 30 decisões, e 43 % dos contatos foram fora da casa.
- **Com o T\* longo, o pet de hoje continua igual:** o D_A do B1 é −0,8 decisão, contra um T\*c de ~52.
- A riqueza do que os dois fazem juntos, com as medidas da S0, está em `resultado.json`, em `bracos.<braço>.riqueza`.

## O que isto não diz

- **Que o pet ignora o outro:** a resposta mostrou só que não há diferença acima de δ_A no tempo até o contato.
- **Nada sobre o B:** a bola continua sem substrato que dê a premissa.
- **Nada sobre um pet com sentidos mais longos:** o olfato e a audição (`ConfigSentidos`) seguem desligados (adendo 1).

## Próximo passo (a S4, depois do "aprovado" deste resultado)

A síntese e a espec do M1, como o pedido manda. Nenhum mecanismo entra antes da S4.
