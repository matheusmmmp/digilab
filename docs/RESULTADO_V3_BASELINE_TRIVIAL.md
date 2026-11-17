# RESULTADO V3 — EVIDENCIA A1: o modular contra uma baseline trivial (2026-11-16, Claude Code, Opus 5.5)

**O plano:** [PLANO_ANALISE_V3_BASELINE_TRIVIAL.md](PLANO_ANALISE_V3_BASELINE_TRIVIAL.md), APROVADO pelo Matheus em 2026-11-16 ("Aprovo,
pode rodar"), commitado antes da primeira vida. A ordem dos commits no branch `v3-evidencia-a1`:

| commit | o quê |
|---|---|
| `25f0a5f3` | o plano (PROPOSTO), a baseline, o orquestrador, as configs, os testes e as faixas |
| `da842240` | o plano e as faixas APROVADOS |
| `4f658d68` | a docstring do orquestrador sem o nome `CONFIG_MUNDO_MVP` (D-EV-A1-3); nenhum número muda |
| `98dde8b1` | os artefatos da calibração |
| `af1a52e5` | os artefatos da validação |

**A leitura, pela regra da seção 5.3: "< 0", a baseline vence o modular. H refutada.**

## 1. As runs

| etapa | comando (o do `meta.json`) | commit, árvore | vidas | sementes |
|---|---|---|---|---|
| calibração | `python experiments/run_v3_baseline_trivial.py --config experiments/configs/v3_baseline_trivial/calibracao.json --processos 4` | `4f658d68`, limpa | 9 600 (96 pontos × 25 unidades × 4 donos, só TRIV, `longe_fixo`) | 96101…96505 |
| validação | `python experiments/run_v3_baseline_trivial.py --config experiments/configs/v3_baseline_trivial/validacao.json --processos 4` | `98dde8b1`, limpa | 4 800 (REL e TRIV × 12 células × 200 unidades) | 97101…97505 |

Python 3.13.0; Node v24.19.0 (gravado, a run não o usa). As duas saíram com o código 0, sem falha alta (replay, T-CENARIO-1, conferências
da C4). A validação rodou **uma vez**.

**Os artefatos** (o sha256 no disco é igual ao do git; todo número abaixo sai deles):
- `artifacts_v3_baseline_trivial/calibracao/`: `resultado.json` `a7e71bd3…`, `medidas.json` `f08f376b…`, `meta.json`.
- `artifacts_v3_baseline_trivial/validacao/`: `resultado.json` `706a687a…`, `medidas.json` `cdaa5170…` (33,7 MB, sem `.gz`: abaixo de
  100 MB), `vidas.tar.gz` `7e0a7028…` (22,5 MB, determinístico), `meta.json`.

## 2. A calibração (seção 4)

O ponto escolhido pela regra 4.3 (a maior média da taxa por episódio no `longe_fixo`, n = 25 unidades): **fome < 0,4, energia < 0,1,
tédio > 0,5 × S**, média 0,747. Os quatro seguintes: (0,4; 0,1; 0,9) 0,740, (0,4; 0,1; 0,7) 0,740, (0,4; 0,1; 1,0) 0,732 e
(0,4; 0,2; 1,0) 0,707.

**O ponto cai na borda da grade** em dois eixos: a energia (0,1) e o tédio (0,5) são os menores valores da grade. Pela seção 4, isso fica
registrado e não muda a validação. Uma grade mais larga poderia dar uma baseline ainda mais forte (o que só reforça a leitura abaixo; não
foi testado).

## 3. O primário (seção 5.1)

REL − TRIV na taxa de fechamento por episódio de fome, nas 4 células do `longe_fixo`, unidade (base, semente):

| n | média | IC95 (t, gl 199) | p unilateral (H: > 0) | t | classe |
|---|---|---|---|---|---|
| 200 | **−0,083** | **[−0,128; −0,038]** | 0,9998 | −3,63 | **< 0** |

- Ao lado, rotulados, sem mudar a decisão: o IC95 percentil do bootstrap [−0,127; −0,050] (anticonservador com 5 bases, A4.4); o g1 0,82.
- **A margem efetiva** (o menor efeito com poder 0,8 pelo dp observado) saiu **0,064**, acima da δ = 0,032 e da 0,019 que a C4 dava para
  REL − SEM: o dp de REL − TRIV é maior, como a seção 5.2 previa que poderia ser. Isso enfraquece só a leitura de "≈ 0"; o "< 0" não
  depende dela, porque o IC inteiro fica abaixo do 0.

## 4. As secundárias (seção 5.4, sem gate)

| lugar | n | REL − TRIV | IC95 | classe |
|---|---|---|---|---|
| comedouro | 200 | −0,074 | [−0,100; −0,049] | < 0 |
| longe sorteado | 200 | −0,362 | [−0,373; −0,351] | < 0 |

## 5. O descritivo (seção 5.4, sem gate)

Os níveis, média por braço e lugar (n = 200 unidades em cada):

| medida | REL comedouro | REL longe | REL `longe_fixo` | TRIV comedouro | TRIV longe | TRIV `longe_fixo` |
|---|---|---|---|---|---|---|
| taxa por episódio | 0,879 | 0,444 | 0,562 | 0,953 | 0,806 | 0,645 |
| episódios de fome por vida | 17,0 | 11,8 | 12,9 | 27,9 | 21,4 | 18,0 |
| privação (fração das decisões com min(fome, higiene, energia) < 0,15) | 0,157 | 0,530 | 0,382 | 0,981 | 0,975 | 0,986 |
| exaustão (fração das decisões dos dias 8–14 com energia < 0,25) | 0,167 | 0,305 | 0,239 | 1,000 | 1,000 | 1,000 |
| d_fe | 0,519 | 0,680 | 0,607 | 0,818 | 0,807 | 0,883 |

As ações somadas no `longe_fixo`: a TRIV come 614 820 vezes e dorme 241 858; o REL come 59 925 e dorme 498 745 (o resto no
`resultado.json`, `descritivo.acoes`).

**O que o descritivo mostra, sem mudar a classe:** a baseline vence o primário vivendo no limite. Ela fica em privação em ~98 % das
decisões e exausta em todas as decisões da segunda semana, entra em mais episódios de fome (18 contra 13 por vida no `longe_fixo`) e come
dez vezes mais. O REL tem a privação e a exaustão muito menores. A taxa por episódio não pune o pet que vive com fome e sem energia, só
conta se cada episódio fecha. Isto é uma observação pós hoc sobre a medida, não um resultado com gate; o plano não previa ler o bem-estar
como critério e esta leitura não o vira em critério.

## 6. O que este resultado não demonstra

(do `resultado.json`, `nao_demonstra`, e da seção 0 do plano)
- que a baseline é a melhor política trivial possível (só a grade da seção 4, com o ponto na borda);
- o resultado fora das 12 células da C4, do mundo do MVP e dos 14 dias;
- algo sobre o jogo web (as vidas são do Python);
- que o modular é pior ou melhor em outra medida (a privação e a exaustão acima são descritivas).

## 7. CHECKPOINT A2

A classe vai ao Matheus como saiu: **"< 0", a baseline vence**. Pelo pedido, "se o baseline vencer ou empatar, a definição do JOGO muda e
a poda (limpeza, Fase L5) é obrigatória". Esta run não decide isso, nem o que muda na definição do jogo; a decisão é do Matheus. A A2
(ablação do aprendizado no TS) não começa antes dela.

Os desvios estão em `docs/registro/2026-11.md`, seção "EVIDENCIA A1" (D-EV-A1-1 a D-EV-A1-6).
