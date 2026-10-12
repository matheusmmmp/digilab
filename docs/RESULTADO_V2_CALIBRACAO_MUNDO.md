# Resultado — V2: a calibração do mundo físico

Data: 2026-10-12. Plano: `docs/PLANO_ANALISE_V2_MUNDO_FISICO.md`, seção 6, adendo 1 (A1.4) e A1.9, o adendo com os números desta run.
Autorizada pelo Matheus em 2026-10-12.

**Fonte dos números:** `artifacts_v2_mundo/calibracao/`. Lá ficam `resultado.json`, `medidas.json` (o registro compacto de cada vida),
`grade/m_*/medidas.json` e `piloto/medidas.json` (as medidas completas) e `meta.json`. As vidas (`vidas/*.jsonl`) ficam fora do git e
saem de novo da config e do código.
- **Comando:** `python experiments/run_v2_calibracao_mundo.py --config experiments/configs/v2_mundo/calibracao.json --processos 8`.
- **A run:** código em `1a748cd` (árvore limpa), Python 3.13.0, Windows, de 06:28 a 06:58.
- **Os sha256** de `mundo.py`, `config.py`, `lobos.py`, `engine.py`, do plano e da config estão no `meta.json`.
- **O replay:** cada vida foi gravada e rejogada a partir do texto do disco, bit a bit, e o replay da medição também foi conferido.
  Nenhuma divergência.

## Resumo

- **O mundo: `m` = 1.** O `p_queda` do jardim e da mata fica o da tarefa.
  - Em `m` = ½, explorar não compensa nem para o instinto: P0z − P0 em `D_FE` dá −0,00006 [−0,0085; +0,0087].
  - Em `m` = 1 compensa: +0,0154 [+0,0093; +0,0209].
  - Em `m` = 2 também: +0,0196 [+0,0127; +0,0264].
- **`Δ_MF` = 0,00768**, metade do que explorar vale para o instinto em `m` = 1.
- **O N da validação: K = 8 por base, N = 40**, com poder simulado de 0,80 no G-MF1r.
  - O G-MF2r tem poder de 0,92 a 0,99.
  - O G-MF3r, na privação, fica subpotenciado (0,03 a 0,11).
- **O custo da validação com K = 8:** 4,3 h de CPU, ou 6,3 h com o bloco do layout afastado. Com 8 processos são ~0,8 h de parede.
- **A validação não rodou.** Ela precisa de outro sim do Matheus.

## 1. O que rodou

| etapa | braços | vidas | por unidade |
|---|---|---|---|
| grade | P0 e P0z, em `m` ∈ {½, 1, 2} | 1.440 | 3 × 12 × 2 = 72 |
| piloto (no `m` escolhido) | P1, P0^ac e P1^ac (acoplados ao P0z da mesma célula, filtro `nenhum`) | 720 | 12 × 3 = 36 |

**As condições:**
- 20 unidades das bases 31101…31505 (K = 4, prefixo `mundo`);
- 12 células: os 4 donos da v1 × comedouro, perto e longe;
- 14 dias, orçamento de 224;
- o mundo `fisico` (as frutas "iguais", PMF-7);
- os donos só com o cuidado (PMF-3).

**O P1** é o do plano (seção 3): o cérebro A na montagem completa, ponto T3, ganho 4, canais ligados e `memoria_ganho` 512 (que não
existe no mundo físico), com os alvos padrão do motor.

**As chaves que o plano não pede, desligadas e conferidas em código** (`conferir_desligadas`, gravado no `meta.json`):
- o banheiro, o corpo, o metabolismo, os gestos e o grupo;
- o alvo aprendido, as entradas sociais, o modelo dos outros e a presença da fruta no mundo;
- os pesos pela janela, a rede de si, o julgamento da fruta, o calendário, a informação e o pedido.

## 2. A calibração do mundo (seção 6)

**A premissa:** P0z − P0 em `D_FE` (dias 8 a 14), por unidade, a média das 12 células. O bootstrap reamostra as 20 unidades, com 10.000
reamostragens e a semente 4242.

| `m` | média | IC95 | t pareado (gl 19) | passa |
|---|---|---|---|---|
| ½ | −0,00006 | [−0,0085; +0,0087] | — | não |
| **1** | **+0,0154** | **[+0,0093; +0,0209]** | t = 5,12, p unilateral 3 × 10⁻⁵ | **sim** |
| 2 | +0,0196 | [+0,0127; +0,0264] | — | sim |

A regra pega o **menor** `m` que passa: **`m` = 1**. Nada do mundo muda depois disto.

**Descritivo** (a média das 240 vidas de cada braço; não entra na regra):

| `m` | quedas por vida | `D_FE` P0 | `D_FE` P0z | privação P0 | privação P0z | consumos P0 | consumos P0z |
|---|---|---|---|---|---|---|---|
| ½ | 71,8 | 0,407 | 0,407 | 0,203 | 0,175 | 89,5 | 74,9 |
| 1 | 113,8 | 0,385 | 0,401 | 0,153 | 0,161 | 101,3 | 81,4 |
| 2 | 157,9 | 0,370 | 0,390 | 0,132 | 0,141 | 110,5 | 88,5 |

- **O P0 come mais que o P0z em todo `m`** (explorar acha comida). Em `m` = ½, porém, o que ele acha não paga a energia que gasta.
  - Na privação, o P0 fica até pior que o P0z em `m` = ½ (0,203 contra 0,175).
- **P0z − P0 em `D_FE` por lugar,** em `m` = 1:
  - comedouro −0,011;
  - perto +0,018;
  - longe +0,040.

  Com a ração no comedouro, explorar não compensa; com ela longe, compensa mais.
- **Por dono,** em `m` = 1: aleatório +0,037, relapso +0,014, incoerente +0,007, atencioso +0,003.

  Explorar vale mais para o pet de quem cuida menos. É o R-3 do plano.

## 3. O Δ e o N (A1.4)

**`Δ_MF` = ½ × 0,015352 = 0,007675785900293976**, em `D_FE`. Fica congelado na A1.9.

**O poder simulado no G-MF1r** vem do bootstrap das diferenças P0 − P1 por unidade:
- o P0 é o da grade em `m` = 1, e o P1 é o do piloto;
- as diferenças são centradas e deslocadas para `Δ_MF`;
- são 2.000 réplicas por K, com o teste t unilateral a 0,025 (o "limite inferior do IC95 > 0"), na conta do adendo 2 da V1, semente 4242.

| K por base | 4 | 5 | 6 | 7 | **8** | 9 | 10 |
|---|---|---|---|---|---|---|---|
| N | 20 | 25 | 30 | 35 | **40** | 45 | 50 |
| poder | 0,495 | 0,577 | 0,668 | 0,747 | **0,802** | 0,850 | 0,889 |

**K = 8 (N = 40)**: o menor K com poder ≥ 0,8.

**Os secundários no N = 40, só relato:**

| gate | contraste | Δ | poder a α 0,01 | poder a α 0,05 |
|---|---|---|---|---|
| G-MF2r | P0^ac − P1^ac em `D_FE` | `Δ_MF` | 0,915 | 0,987 |
| G-MF3r | P0 − P1 em privação | 0,0044 (½ × P0z − P0 na privação, leitura registrada) | 0,027 (subpotenciado) | 0,114 (subpotenciado) |

- **Os alfas:** 0,01 é o primeiro passo do Holm com os cinco gates da A1.8, e 0,05 o último.
- **O G-MF3r é subpotenciado** porque a privação varia muito entre unidades (dp 0,061, contra 0,017 do `D_FE`) e o Δ dela é pequeno.
- **G-PERM, G-OPORT e G-DIST:** não calculados. O plano não dá o Δ das inclinações, e o layout afastado não roda no piloto.

## 4. O piloto (só para o N; não é evidência sobre o P1)

Pela seção 6, estes números não entram no resultado como evidência sobre o P1. Ficam aqui porque o N saiu deles.

| contraste (por unidade, `m` = 1) | média | dp entre unidades | IC95 |
|---|---|---|---|
| P0 − P1 em `D_FE` | −0,0124 | 0,0172 | [−0,0197; −0,0049] |
| P0^ac − P1^ac em `D_FE` | −0,0034 | 0,0139 | [−0,0090; +0,0029] |
| P0 − P1 em privação | −0,0292 | 0,0612 | [−0,0557; −0,0028] |

**O que não se lê daqui.** O sinal negativo não decide nada:
- o poder foi simulado com as diferenças deslocadas para `Δ_MF`, que só usa a variância delas;
- o que conta é o G-MF1r na validação.

## 5. O custo

**A CPU por vida,** com a gravação, o replay do disco e a medição (sonda de 64 estados × 200 amostras):

| braço | vidas | s de CPU por vida |
|---|---|---|
| P0 | 240 | 6,63 |
| P0z | 240 | 3,86 |
| P1 | 240 | 7,93 |
| P0^ac | 240 | 6,29 |
| P1^ac | 240 | 7,87 |

**Esta run:** 2.160 vidas e 2,17 h de CPU somadas, em 30 min de parede com 8 processos (grade 16,5 min, piloto 13,4 min).

**A validação estimada com K = 8:**

| desenho | vidas | CPU | parede com 8 processos |
|---|---|---|---|
| os 5 braços (A1.2) | 2.400 | 4,3 h | ~0,54 h |
| com o bloco do layout afastado (A1.8) | 3.360 | 6,3 h | ~0,79 h |

O bloco do afastado foi estimado pelo custo do P0 e do P1 no layout padrão. Ele sai primeiro só se passar do teto de tempo do Matheus
(A1.8).

## 6. Desvios e achados (detalhes em `docs/REGISTRO_DESVIOS.md`)

- **A dominância da bancada no mundo físico** (achada na fumaça; corrigida antes da run, `1a748cd`).
  - **O defeito:** o motor avisa `fruta_comida` também no "achou e comeu" do explorar. A medida descritiva da dominância punha o humor
    (a E2) nesse explorar, e o cérebro não põe: só no comer.
  - **O efeito:** com os canais ligados, a conferência falhava alto no P1, numa vida da fumaça.
  - **A correção:** a medida segue a regra do cérebro (`comeu_fruta_e2`).
  - **O que não muda:** nenhuma vida e nenhuma medida do plano (`D_FE`, privação, visitas). Muda só o descritivo da dominância nesses
    explorar.
- **O desempate do cheiro** recomendado no #232 (trocar no motor antes da calibração do mundo) **não está na main.** A calibração rodou
  com o motor de `2849712`, a ordem fixa no empate.
- **O pedido do Gerente e o plano diferem no piloto.**
  - O Gerente pediu "P1 e P1ac, 24 vidas por unidade". O P1ac saiu com a PMF-2r (adendo 1, decidido).
  - Rodou o piloto da A1.4: P1, P0^ac e P1^ac, 36 vidas por unidade, com o N sobre P0 − P1 (G-MF1r).
- **O Δ da privação** para o relato do G-MF3r foi uma leitura minha (o plano não o dá). Não decide nada.

## 7. O que vem depois

**A validação** roda nas bases 32101…32505, com K = 8:
- os 5 braços (A1.2) e o bloco do layout afastado (A1.8);
- os gates da A1.3 e da A1.8.

**Ela precisa de outro sim do Matheus.** A config dela ainda não existe.
