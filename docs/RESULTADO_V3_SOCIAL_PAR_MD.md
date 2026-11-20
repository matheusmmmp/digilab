# RESULTADO V3 — SOCIAL_PAR MD2: a medida do M1 e do M2

- **Plano:** `docs/PLANO_ANALISE_V3_SOCIAL_PAR_MD.md`, APROVADO pelo Matheus em 2026-11-19 ("Aprovado", MD-1 a MD-8). O código da
  medida (MD1, #1034) foi aprovado em 2026-11-20 ("Aprovado"), com a D-SP-74.
- **A run:** `python experiments/run_v3_social_par_md.py --config experiments/configs/v3_social_par_md/run.json --processos 4`, uma vez.
  - Rodou em 2026-11-20, das 13:58:19 às 15:12:53, sobre o commit 3ed5fdd6 da `main` (o merge do #1045).
  - O `pre_run` aceitou a run. A run esperou o fim da run CORPO C4 (uma run por vez, V3-D8).
  - **O git não estava limpo (`git_limpo: false` no `meta.json`).** A única mudança era a linha `"plano"` que faltava no `run.json` (a
    D-SP-75). Nenhum parâmetro do experimento mudou. A mudança entra neste PR, e o `config_sha256` do `meta.json` (`807e504a…`) é o
    do `run.json` commitado aqui.
  - **Com o `git_limpo: false`, o `tools/replicar_run.py` recusa replicar esta run.** Ou se aceita o resultado com essa ressalva, ou
    se roda a mesma config de novo com a árvore limpa e se confere que o `medidas.json` e o `resultado.json` têm os mesmos sha256. A
    run é determinística, e a segunda rodada não seria uma segunda amostra. A decisão é do Matheus.
  - São 2.000 pares: 4 mecanismos × 2 braços × (200 bases, 105001…105200, k = 1, mais 50 pares do G-DET, 105301…105350).
- **Artefatos:** `artifacts_v3_social_par_md/run/`, com o `meta.json`, o `medidas.json` (sha256 `c6b61b90…`), o `resultado.json`
  (sha256 `604bc9ce…`) e os 2.000 pares em `vidas/`. A pasta fica fora do git (`.gitignore`, `artifacts_*/`), como a da S3.
- **Os gates de cada par:** o G-INSTR e o G1 passaram nos 2.000 pares. A run para no primeiro par que falha, e não parou.

## O controle positivo: G-DET (seção 3), por célula

O `SeguidorPuro` entra no lugar de P. O gate passa se o IC95 do D_A ficar todo abaixo de −4 decisões.

| célula | n | média | IC95 | passa |
|---|---|---|---|---|
| M1 \| B1 | 50 | −43,46 | [−56,44; −30,48] | **sim** |
| M1-inc0 \| B1 | 50 | −50,40 | [−63,54; −37,26] | **sim** |
| M1+M2 \| B1 | 50 | −30,78 | [−42,69; −18,87] | **sim** |
| M1-inc0+M2 \| B1 | 50 | −28,70 | [−40,39; −17,01] | **sim** |
| M1 \| C | 49 | −3,61 | [−7,67; +0,45] | não |
| M1-inc0 \| C | 49 | −4,59 | [−8,71; −0,48] | não |
| M1+M2 \| C | 49 | −3,65 | [−8,57; +1,27] | não |
| M1-inc0+M2 \| C | 49 | −4,35 | [−9,83; +1,13] | não |

- **No B1, o instrumento vê nas quatro células.**
- **No C, o G-DET falha nas quatro.** Pela seção 7, as quatro células do C são "o substrato não deixa ver" e não dizem nada sobre o
  mecanismo.
  - Na S3, o G-DET do C passou (−20,06, IC95 [−27,78; −12,34]). Com as unidades sociais, o seguidor separa só ~4 decisões no C.
  - O tempo até o contato na GRAV do C é curto, 6,8 a 7,3 decisões, e deixa pouco espaço para separar.
  - Não se investigou por que o G-DET caiu. Não se mexeu em nada depois de ver o número.

## A premissa do M2: PM-1 (seção 5)

| célula | pares com o desfecho do `seguir` na solidão < 0 no t0 | média do desfecho | passa (≥ 50 %) |
|---|---|---|---|
| M1+M2 \| B1 | 196/200 (0,98) | −10,09 | **sim** |
| M1-inc0+M2 \| B1 | 196/200 (0,98) | −9,97 | **sim** |
| M1+M2 \| C | 196/200 (0,98) | −9,99 | **sim** |
| M1-inc0+M2 \| C | 196/200 (0,98) | −9,86 | **sim** |

- **O P1 aprende antes do t0 que seguir o outro alivia a solidão,** com e sem o incentivo.
- Sem o M2, o mesmo desfecho é positivo (+4,9 a +5,1, descritivo): o `seguir` não alivia nada sem a companhia no corpo.
- A solidão de P no t0 cai de ~449 mil (sem o M2) para ~127 mil (com o M2). É descritivo.

As premissas da S (PA-1 a PA-3) passam em todas as células. A PB-1 não passa em nenhuma: o B (a bola) não se lê, como na S3.

## O primário: D_A por célula

**D_A = T\*c_VIVO − T\*c_GRAV,** o tempo até o contato, em decisões. Um valor negativo quer dizer que F e P se tocam mais depressa
quando P responde. A margem é δ_A = 4.

| célula | n | média | dp | IC95 | classe | leitura (seção 7) |
|---|---|---|---|---|---|---|
| M1 \| B1 | 200 | −9,16 | 24,12 | [−12,52; −5,79] | **< 0** | o parceiro responde: aproxima o contato |
| M1-inc0 \| B1 | 200 | −8,66 | 23,90 | [−11,99; −5,33] | **< 0** | o parceiro responde: aproxima o contato |
| M1+M2 \| B1 | 200 | −6,79 | 18,15 | [−9,32; −4,26] | **< 0** | o parceiro responde: aproxima o contato |
| M1-inc0+M2 \| B1 | 200 | −6,53 | 17,52 | [−8,97; −4,08] | **< 0** | o parceiro responde: aproxima o contato |
| M1 \| C | 200 | −1,72 | 6,89 | [−2,68; −0,76] | ≈ 0 | cego (o G-DET falhou) |
| M1-inc0 \| C | 200 | −1,77 | 6,54 | [−2,68; −0,85] | ≈ 0 | cego |
| M1+M2 \| C | 200 | −1,36 | 5,74 | [−2,16; −0,56] | ≈ 0 | cego |
| M1-inc0+M2 \| C | 200 | −1,72 | 6,12 | [−2,57; −0,86] | ≈ 0 | cego |

- **No B1, as quatro células saem de ±δ_A, para baixo.** O pet com as unidades sociais chega ao outro 6,5 a 9,2 decisões mais
  depressa quando o outro responde. Na S3, o pet de hoje deu −0,82 [−1,78; +0,15] no mesmo braço.
- **No C, as quatro dão ≈ 0, mas a célula não se lê,** porque o G-DET falhou.

## A atribuição: C-APR e C-APR1 (seção 5)

| contraste | braço | n | média | IC95 | classe |
|---|---|---|---|---|---|
| C-APR = D_A(M1+M2) − D_A(M1-inc0+M2) | B1 | 200 | −0,27 | [−1,38; +0,85] | **≈ 0** |
| C-APR | C | 200 | +0,36 | [−0,17; +0,88] | ≈ 0 |
| C-APR1 = D_A(M1) − D_A(M1-inc0) | B1 | 200 | −0,50 | [−2,38; +1,39] | **≈ 0** |
| C-APR1 | C | 200 | +0,05 | [−0,37; +0,46] | ≈ 0 |

**Zerar o incentivo das unidades sociais não muda a resposta,** com ou sem o M2.

## O conjunto (seção 7)

O M1+M2 \| B1 dá < 0 e o C-APR \| B1 dá ≈ 0. A linha escrita antes:

> a resposta vem das unidades a mais ou da companhia no corpo, não do aprendizado (o D-SP-62).

**O M1 sozinho já dá a resposta no B1, e com o incentivo zerado também.** A resposta, portanto, não vem da companhia no corpo (o M2),
nem do valor aprendido do outro. Vem das unidades a mais do M1: o pet passa a ter alvos sociais na decisão, e isso basta para ele
chegar mais depressa ao outro que se mexe. A run não diz qual parte das unidades faz isso.

## As previsões (PROPOSTO, seção 7 do plano) e o que saiu

| previsão | o que saiu |
|---|---|
| M1 e M1-inc0: D_A ≈ 0 no C e no B1 ("no B1, o M1 pode sair de ≈ 0 pelo `onde_comeu`") | **não se confirmou no B1:** −9,16 e −8,66, os dois < 0. No C, não se lê |
| M1+M2: a PM-1 passa, D_A < 0 no B1, C-APR < 0 | a PM-1 passa (0,98) e o D_A < 0 no B1 (−6,79); **o C-APR dá ≈ 0** (−0,27) |
| M1-inc0+M2: D_A ≈ 0 | **não se confirmou:** −6,53 no B1, < 0 |

Nada se ajustou depois de ver os números.

## Os descritivos (não decidem nada)

| célula | fração social de P antes do t0 | na janela (VIVO) | T\*c_GRAV | T\*c_VIVO | contato fora da casa (VIVO) |
|---|---|---|---|---|---|
| M1 \| B1 | 0,220 | 0,161 | 28,4 | 19,3 | 0,765 |
| M1-inc0 \| B1 | 0,219 | 0,160 | 27,5 | 18,8 | 0,770 |
| M1+M2 \| B1 | 0,244 | 0,193 | 22,8 | 16,0 | 0,780 |
| M1-inc0+M2 \| B1 | 0,242 | 0,192 | 22,2 | 15,7 | 0,780 |
| M1 \| C | 0,221 | 0,207 | 7,3 | 5,6 | 0,025 |
| M1+M2 \| C | 0,245 | 0,237 | 6,8 | 5,4 | 0,020 |

O M2 deixa o T\*c_GRAV do B1 mais curto (de ~28 para ~22) e aumenta um pouco a fração social de P. A secundária, a riqueza e o resto
estão em `resultado.json`, em `celulas.<mecanismo>|<braço>`.

## O que isto não diz

- **Que o pet aprendeu o outro:** o C-APR e o C-APR1 dão ≈ 0. O incentivo não faz diferença.
- **Nada sobre o C:** o G-DET falhou nas quatro células.
- **Nada sobre o B (a bola):** a PB-1 falhou em todas as células.
- **Qual parte do M1 dá a resposta:** a run tem só o M1 inteiro e o M1 com o incentivo zerado.

## Próximo passo

A seção 7 manda descrever e levar ao Matheus. Fica para ele decidir, com um plano novo, se se quer saber qual parte das unidades dá a
resposta e por que o G-DET do C caiu. Nenhum mecanismo entra sem plano.
