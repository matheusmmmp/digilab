# Resultado — V2, calibração do cérebro C (Fly-like) (2026-10-06)

Tarefa `docs/TAREFA_V2_CALIBRACAO_CEREBROS_B_C.md` (rodada 11). Grades e regras do **adendo 1, seção 1.2**, de
`docs/PLANO_ANALISE_V2_COMPARACAO_CEREBROS.md`, conferido pelo coordenador. Uma run, nesta worktree, depois do commit do orquestrador e da
config (`30892e2`).

- Orquestrador `experiments/run_v2_calibracao_cerebro_c.py`; config `experiments/configs/v2_calibracao_cerebro_c/calibracao.json`.
- Artefato `artifacts_v2_comparacao_cerebros/calibracao_C/`: `C-A/`, `C-B/` e `C-C/` com `resultado.json` e `medidas.json` por ponto,
  mais `piloto.json`, `escolha.json`, `meta.json` e `run.log`.
- As vidas (`*/vidas/*.jsonl`, 46 MB) ficam fora do git e se regeneram da config e do código.

## Desenho

- **Unidades:** as bases 28101…28505, K = 4, prefixo `comparacao-cerebros`, ou seja, 20 unidades.
- **Vida:** atencioso, 14 dias, orçamento 224, mundos `casado_frutas`, `descasado` e `mutavel`.
- **Peças comuns:** o ganho da consequência é o do ponto do A da K2 (4, `artifacts_v2_calibracao_conjunta/escolha.json`). O C não lê a
  montagem nem a chave dos canais, que são do A.
- **Rejogo:** toda vida foi gravada e rejogada do disco bit a bit, e o replay das medidas também confere.
- **Regras:** nenhuma regra leu a `taxa_fruta_ruim` nem um contraste entre braços ou cérebros.
- **Vidas: 540**, dentro do teto de 1260 (as da K2 do A). A grade foi contada antes de rodar.
- **Tempo: 3578 s (~1 h)**, dentro do teto de 4 × 15.093 s = 60.373 s.

## O ponto escolhido: passo 128, teto 4096, w0_info 256 — **o C fecha**

| etapa | parâmetro | escolhido | fechou | regra |
|---|---|---|---|---|
| C-A | `passo` | **128** (S/8) | sim | K-4: nenhuma vida no teto nos três pontos; menor razão da deriva |
| C-B | `teto` | **4096** (4S) | sim | K-4: 4S e 16S sem vida no teto e com a mesma razão; o empate fica com o menor |
| C-C | `w0_info` | **256** (S/4) | sim | K-3: o menor com IC95 inferior > 0,069 (os três passam) |
| piloto | "não aprende" (seção 7) | **não dispara** | — | deriva no dia 14 bem acima de 0; o aprendido muda 32% das decisões |

### C-A, o passo (P1, teto 4S, w0_info 0; 180 vidas)

| passo | vidas no teto | razão da deriva (média das 3 condições) | deriva dia 7 | deriva dia 14 | maior compartimento | aprendido decide |
|---|---|---|---|---|---|---|
| 32 | 0 | 3,00 | 0,0025 | 0,0076 | 519 | 0,162 |
| 64 | 0 | 1,89 | 0,0072 | 0,0136 | 1117 | 0,259 |
| **128** | 0 | **1,61** | 0,0138 | 0,0222 | 2369 | 0,324 |

As três condições ficam próximas em cada ponto. No passo 128, por exemplo: casado 1,66, descasado 1,58, mutável 1,61.

A razão cai com o passo, e o escolhido é **a ponta da grade**. Com razão 1,61 a deriva ainda cresce na segunda semana. A K-4 não pede uma
razão máxima, então isso fica registrado aqui e não muda a escolha. A grade não foi estendida: o adendo a fixa.

### C-B, o teto (P1, passo 128; 120 vidas novas e o 4S da C-A reusado)

| teto | vidas no teto | razão da deriva |
|---|---|---|
| 1024 | **60 de 60** | 1,53 |
| **4096** | 0 | 1,61 |
| 16384 | 0 | 1,61 |

Com o passo 128 nenhum compartimento passa de 2369. Por isso as vidas de 4S e de 16S são as mesmas, e o empate vai para o menor teto.

### C-C, a confiança inata na informação (P2, passo 128, teto 4096; 240 vidas)

A medida é a fração das sub-decisões da fruta com duas frutas ou mais e informação vigente, nos dias 1–7, que a informação decidiu (sonda
`info_decidiu`). A unidade é a semente, com as três condições juntas.

| w0_info | elegíveis | decididas | fração (IC 95%) |
|---|---|---|---|
| 0 (referência, descritiva) | 895 | 18 | 0,019 [0,010; 0,030] |
| **256** | 933 | 184 | **0,202 [0,164; 0,242]** |
| 512 | 936 | 262 | 0,282 [0,250; 0,315] |
| 768 | 927 | 282 | 0,304 [0,273; 0,336] |

Nenhuma vida da C-C chegou ao teto. Com `w0_info` 0 a informação só pesa pelo que o C aprende nas células `info_bem` e `info_mal`, e
decide 1,9% das escolhas.

### Piloto: o "não aprende" (seção 7 do plano)

O piloto usa o P1 no ponto escolhido: as 60 vidas da C-B no teto 4096. O `w0_info` não age no P1, que não tem informante. A unidade é a
semente, n = 20.

- **Deriva ao instinto no dia 14:** 0,0222 bit, IC 95% [0,0218; 0,0227]. O limite inferior está longe de 0.
- **Decisões em que a parte aprendida muda a escolha:** 0,324 [0,319; 0,329]. O limite do critério é 0,01.
- Só entre as decisões com dois candidatos ou mais (descritivo): 0,473.
- **Nenhum dos dois critérios dispara: o C aprende e entra no M6.**

## O que isto não diz

É calibração, não teste:
- nenhuma predição foi avaliada;
- nada compara o C com o A ou com o B (isso é da validação, sementes 29101…29505, não tocadas);
- a `taxa_fruta_ruim` está nos `medidas.json` como medida da bancada, mas nenhuma regra a lê.

Interpretações do adendo em `docs/REGISTRO_DESVIOS.md` (2026-10-06, CALIBRACAO-CEREBRO-C).
