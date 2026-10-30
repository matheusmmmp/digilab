# Resultado — V2/V3: o piloto da competição entre as regras urgentes (V3-3/V3-4)

> **V2, congelado em 2026-10-30** (tag `v2-final`). O estado em que este documento fica na V3 está em `docs/FECHAMENTO_V2.md`; o
> plano da V3, em `docs/PLANO_V3.md`.

Data: 2026-10-22. Plano: `docs/PLANO_ANALISE_V2_V3_COMPETICAO.md` (PC-1 a PC-6 DECIDIDAS em 2026-10-21), seções 6 e 7. Tarefa:
`docs/TAREFA_V2_V3_COMPETICAO.md`.

**A autorização:** o Matheus, em 2026-10-22: "Pode fazer o piloto da competicao". O sim foi repassado pelo Gerente.

**Fonte dos números:** `artifacts_v2_v3_competicao/piloto/`:
- `resultado.json`;
- `medidas.json` (uma linha por vida);
- `meta.json`.

As vidas ficam fora do git.

- **O comando:** `python experiments/run_v2_competicao.py --config experiments/configs/v2_competicao/piloto.json --processos 4`, uma vez,
  sem mudar a config.
- **A run:**
  - a `main` `f0e07c9`, com a árvore limpa (`git_limpo` no meta), numa worktree própria;
  - Python 3.13.0, Windows, 4 processos, 222 s de parede;
  - o meta traz o sha256 do plano, da config, do orquestrador e de `config.py`, `engine.py`, `metrics.py`, `motivo.py` e `lobos.py`.
- **As sementes:** as bases 58101…58505, K = 4, prefixo `competicao`: 20 unidades, 16 vidas por unidade (4 braços × 4 donos), 320 vidas
  de 14 dias.
- **As conferências, em toda vida:**
  - a vida foi gravada e rejogada do disco bit a bit (G1);
  - os gates de mecanismo passaram (desligada, nenhuma aberta; ligada, o `sono_exaustao` forçado; o R1-cong com os pesos no prior).
- **Antes:** a fumaça (as sementes dos testes) rodou na mesma worktree, fora do repositório.

## Resumo

**O piloto não é evidência:** serve para as margens, o N, a G-ABRE e o custo (seção 6). Nada foi ajustado olhando para ele.

- **As margens** (seção 7; PC-2 e PC-3), pela regra registrada, sem ler o R1 nem o R1-cong:
  - **a escala:** o R0 ganha do P0 em `D_FE` por **0,0044** (IC95 [0,0016; 0,0073]). Passa do limiar de 0,001, então a margem tem escala,
    e o plano **não** volta ao Matheus;
  - **`Δ_R1` = ½ × 0,0044 = 0,0022;**
  - **`Δ_priv` = ¼ × 0,1126 = 0,0281** (a privação média do P0);
  - **`Δ_saude` = ¼ × (1 − 0,9125) = 0,0219** (a saúde média do P0).
- **O N:** o poder simulado do G-R1 no `Δ_R1` fica abaixo de 0,8 em todo K.

  | K | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
  |---|---|---|---|---|---|---|---|
  | N | 20 | 25 | 30 | 35 | 40 | 45 | 50 |
  | poder | 0,22 | 0,25 | 0,31 | 0,34 | 0,40 | 0,44 | **0,49** |

  - **Pela seção 7,** a validação roda com **K = 10 (N = 50)**, e o poder sai declarado: **0,49 no `Δ_R1`**.
  - **O G-R1-CONG no N = 50:** poder de 0,48 (α 0,025) e 0,41 (α 0,0167), subpotenciado.
- **A G-ABRE do piloto passa:** a fração de abertas no R1 é **0,121**, IC95 [0,110; 0,131], acima de 0,05.
- **O custo:** 39,7 s de CPU por unidade. A validação com K = 10 (800 vidas) fica em cerca de **33 min de CPU**.

## 1. Os contrastes (só relato, não são evidência)

| contraste | média | IC95 | dp das unidades |
|---|---|---|---|
| `D_FE`(R0) − `D_FE`(R1), o G-R1 | 0,0117 | [0,0083; 0,0152] | 0,0080 |
| `D_FE`(R1-cong) − `D_FE`(R1), o G-R1-CONG | 0,0133 | [0,0099; 0,0166] | 0,0079 |
| `D_FE`(P0) − `D_FE`(R0), a escala da margem | 0,0044 | [0,0016; 0,0073] | 0,0066 |
| privação(R1) − privação(R0) | −0,0202 | [−0,0272; −0,0132] | 0,0165 |
| saúde(R0) − saúde(R1) | −0,0203 | [−0,0291; −0,0125] | 0,0195 |

- **O poder é calculado no `Δ_R1`, a menor diferença que interessa** (seção 7), e não no que o piloto mostrou. No piloto, R0 − R1 ficou em
  cerca de 5 vezes o `Δ_R1`.
- **Não é resultado:** a validação roda em outras unidades.

## 2. Os descritivos

| braço | `D_FE` | privação | saúde | exaustão | forçadas | abertas | a abertura decidiu (nas abertas) | o aprendido decidiu (nas abertas) |
|---|---|---|---|---|---|---|---|---|
| R0 | 0,386 | 0,100 | 0,929 | 0,022 | 0,569 | 0 | — | — |
| R1 | 0,374 | 0,080 | 0,949 | 0,034 | 0,456 | 0,121 | 0,281 | 0,244 |
| R1-cong | 0,387 | 0,101 | 0,918 | 0,022 | 0,384 | 0,176 | 0,095 | 0 |
| P0 | 0,390 | 0,113 | 0,913 | 0,020 | 0,561 | 0 | — | — |

As médias são das 80 vidas de cada braço, nos dias 8 a 14.

**Por dono (R1):**

| dono | abertas | `D_FE`(R0) − `D_FE`(R1) |
|---|---|---|
| relapso | 27,9% | 0,0350 |
| aleatório | 20,0% | 0,0118 |
| atencioso | 0,19% | 0,0002 |
| incoerente | 0,13% | −0,00004 |

**Leituras descritivas** (não são gate):
- **Onde a disputa abre:** como a etapa 0 previa, quase só no relapso e no aleatório. Nos outros dois donos, R0 e R1 ficam quase iguais.
- **As forçadas no R1 ficam em 45,6%,** acima dos ~38% que a etapa 0 previu sobre a vida do R0. A vida do R1 é outra. [HIPÓTESE] Com menos
  fome e menos abandono, duas urgências valem juntas menos vezes.
- **O R1 se exaure mais** (3,4% das decisões com a energia abaixo de 0,25, contra 2,2%) **e tem menos privação.** [HIPÓTESE] Ele troca um
  pouco de sono por comida e cuidado. A segurança da validação (a privação e a saúde por não inferioridade) mede o lado que importa.
- **O R1-cong** abre mais que o R1 e fica perto do P0 em `D_FE` (0,387 contra 0,390) e em saúde (0,918 contra 0,913). Abrir sem aprender
  não aproxima o pet do R1. Só descritivo.

## 3. O que fica

- **A validação não rodou.** A ordem foi parar no piloto.
- **O adendo 1 do plano** registra as margens, o K = 10, o poder, a G-ABRE do piloto e o custo, num commit antes da validação.
- **A config da validação** (`experiments/configs/v2_competicao/validacao.json`, as bases 59101…59505, K = 10) entra quando a validação
  for autorizada.
- **Nada foi ajustado olhando o piloto.**
