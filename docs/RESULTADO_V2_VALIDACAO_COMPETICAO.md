# Resultado — V2/V3: a validação da competição entre as regras urgentes (V3-3/V3-4)

> **V2, congelado em 2026-10-30** (tag `v2-final`). O estado em que este documento fica na V3 está em `docs/FECHAMENTO_V2.md`; o
> plano da V3, em `docs/PLANO_V3.md`.

Data: 2026-10-22. Plano: `docs/PLANO_ANALISE_V2_V3_COMPETICAO.md` (PC-1 a PC-6 DECIDIDAS em 2026-10-21), seções 8 e 9 e adendo 1.
Tarefa: `docs/TAREFA_V2_V3_COMPETICAO.md`. Piloto: `docs/RESULTADO_V2_PILOTO_COMPETICAO.md`.

**A autorização:** o Matheus, em 2026-10-22: "sim para a validacao de competicao". O sim foi repassado pelo Gerente.

**Fonte dos números:** `artifacts_v2_v3_competicao/validacao/`:
- `resultado.json`;
- `medidas.json` (uma linha por vida);
- `meta.json`.

As vidas ficam fora do git.

- **O comando:** `python experiments/run_v2_competicao.py --config experiments/configs/v2_competicao/validacao.json --processos 4`,
  **uma vez**.
- **A config:** escrita pelo adendo 1 (K = 10, as bases 59101…59505) e commitada antes da run (`7edddc3`, sobre a `main` `61336e7`).
- **A run:**
  - a árvore limpa (`git_limpo` no meta); Python 3.13.0, Windows, 4 processos, 615 s de parede;
  - o meta traz o sha256 do plano, da config, do orquestrador, do resultado do piloto e de `config.py`, `engine.py`, `metrics.py`,
    `motivo.py` e `lobos.py`;
  - o pacote é o mesmo do piloto (os mesmos sha256).
- **As sementes:** as bases 59101…59505, K = 10, prefixo `competicao`: 50 unidades, 800 vidas de 14 dias.
- **As conferências, em toda vida:** a vida foi rejogada do disco bit a bit (G1), e os gates de mecanismo passaram.
- **As margens:** as do adendo 1, congeladas no piloto.
- **Nada foi ajustado** olhando para a validação.

## Resumo

**Todos os gates do plano passam. A leitura da seção 9 é "a disputa ajuda, e o aprendido usa a abertura".**

| gate | contraste (por unidade, a média dos 4 donos) | média | IC95 | regra | veredito |
|---|---|---|---|---|---|
| **G-ABRE** (premissa, PC-4) | a fração de abertas no R1 | 0,118 | [0,112; 0,125] | limite inferior > 0,05 | **passa** |
| **G-R1** (primário) | `D_FE`(R0) − `D_FE`(R1) | **0,0124** | **[0,0093; 0,0156]** | as categorias da seção 9, `Δ_R1` = 0,0022 | **"a disputa ajuda"** (IC90 [0,0097; 0,0151]: o superior passa do `Δ_R1`, sem o rótulo "abaixo de Δ") |
| G-R1-CONG (Holm) | `D_FE`(R1-cong) − `D_FE`(R1) | 0,0113 | [0,0086; 0,0140] | limite inferior > 0 | **passa** |
| G-NI-PRIV (Holm) | privação(R1) − privação(R0) | −0,0216 | [−0,0291; −0,0149] | superior < `Δ_priv` = 0,0281 | **passa** |
| G-NI-SAUDE (Holm) | saúde(R0) − saúde(R1) | −0,0317 | [−0,0423; −0,0226] | superior < `Δ_saude` = 0,0219 | **passa** |

- **O Holm** (α 0,05, família de três): os três p unilaterais do bootstrap são < 0,0001 (nenhuma das 10.000 reamostragens contra). Os
  três rejeitam.
- **O poder declarado** (adendo 1): o G-R1 tinha poder de 0,49 para detectar o `Δ_R1` com K = 10.
  - A ressalva pesava sobre um "equivalente" ou um "inconclusivo".
  - O G-R1 saiu "ajuda", com a média em cerca de 5,7 vezes o `Δ_R1` e o IC95 inteiro acima dele.
  - O poder baixo no `Δ_R1` não enfraquece esta categoria. Ele fica declarado como o plano manda.
- **A segurança:** o R1 não piora. Ele tem menos privação (−0,022) e mais saúde (+0,032) que o R0, com os ICs inteiros do lado bom.

## 1. Os descritivos (sem gate)

| braço | `D_FE` | privação | saúde | exaustão | forçadas | abertas | a abertura decidiu (nas abertas) | o aprendido decidiu (nas abertas) |
|---|---|---|---|---|---|---|---|---|
| R0 | 0,382 | 0,101 | 0,911 | 0,022 | 0,571 | 0 | — | — |
| R1 | 0,370 | 0,079 | 0,943 | 0,031 | 0,454 | 0,118 | 0,257 | 0,227 |
| R1-cong | 0,381 | 0,095 | 0,922 | 0,023 | 0,391 | 0,163 | 0,063 | 0 |
| P0 | 0,382 | 0,101 | 0,912 | 0,021 | 0,552 | 0 | — | — |

As médias são das 200 vidas de cada braço, nos dias 8 a 14.

**Por dono:**

| dono | abertas no R1 | `D_FE`(R0) − `D_FE`(R1) |
|---|---|---|
| relapso | 24,4% | 0,0355 |
| aleatório | 22,3% | 0,0146 |
| atencioso | 0,21% | −0,0001 |
| incoerente | 0,34% | −0,0004 |

**Leituras descritivas** (não são gate):
- **Onde está o ganho:** no relapso e no aleatório, onde a disputa abre. No atencioso e no incoerente, R0 e R1 ficam praticamente iguais.
  O primário é a média dos 4 donos (PC-1), e o ganho vem de metade deles.
- **O A e o instinto empatam neste mundo:** o R0 e o P0 ficam iguais em `D_FE` (0,382 e 0,382), em privação e em saúde. No piloto, o
  R0 ganhava por 0,0044. O ganho que a validação mede é o da abertura, não o do A sobre o instinto.
- **Abrir sem aprender** (o R1-cong) fica perto do R0 e do P0. O ganho do R1 sobre ele (o G-R1-CONG) é quase o mesmo que sobre o R0.
  [HIPÓTESE] O ganho vem do aprendido usando a abertura, não da abertura sozinha. É a V3-P4 do plano.
- **Quem decidiu, nas abertas do R1:** a abertura mudou a ação do instinto em 25,7%, e o aprendido decidiu em 22,7%. No R1-cong, a
  abertura muda 6,3%, pelo sorteio com o κ, sem aprender.
- **A exaustão sobe no R1** (3,1% contra 2,2%) **e a privação cai.** [HIPÓTESE] O pet troca um pouco de sono por comida e cuidado. A
  privação inclui a energia abaixo de 0,15 e passa na não inferioridade.
- **As forçadas no R1 ficam em 45,4%,** acima dos ~38% que a etapa 0 previu sobre a vida do R0 (a V3-P1 corrigida). A vida do R1 é outra.

## 2. O que esta validação não diz

- **É o v11 sem o mundo físico** (CR-4), em 14 dias, com os 4 donos da v1. O J1 (o mundo físico) não foi testado com a competição.
- **O ganho é o da competição sobre o A de hoje,** e mora nos donos que negligenciam. Nos que cuidam, a disputa quase não abre.
- **O κ = 16** vem da regra da CR-2, SEM FONTE. Outro κ daria outra troca entre a segurança e o crédito, e não foi testado.
- **A web** continua com o v11 sem a chave. Levar a competição ao jogo é decisão do Matheus.
