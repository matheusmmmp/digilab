# RESULTADO_V3_EQUILIBRIO_CUIDADO_E0: o retrato do dia a dia do pet, hoje

Fase: V3. Frente: EQUILIBRIO_CUIDADO, etapa E0. Data: 2026-11-12. Worker: Claude Code (Opus 5.5), branch `v3-equilibrio-e0`.
Plano de análise: `docs/PLANO_ANALISE_V3_EQUILIBRIO_CUIDADO.md`, commitado antes de qualquer vida. **Nenhum número do jogo mudou.**

**Os artefatos** (todo número abaixo sai deles):
- as 30 vidas: `web/app/scripts/medicoes/equilibrio_cuidado_e0/<versao>_<dono>_<semente>.json`, da `node scripts/equilibrio_cuidado/e0_rodar.ts`
  (em `web/app`);
- o resumo e estas tabelas: `web/app/scripts/medicoes/equilibrio_cuidado_e0/resumo.json` e `tabelas.md`, da
  `node scripts/equilibrio_cuidado/e0_resumo.ts`.

**O que rodou:** os ovos novos de hoje, o de um pet (`VERSAO_PET`, a **v35**) e o grupo do brasão (`VERSAO_GRUPO`, a **v36**), com o
DigiBrain modular e as chaves do produto, no ritmo "rapida", 3 dias de jogo, com os três donos do EQ-4 (seção 2 do plano), nas 5 sementes da
calibração 93101, 93202, 93303, 93404 e 93505. A validação (94101…94505) não foi tocada. Um processo só: as 30 vidas levam uns 10 s.

**Como ler:** cada célula é a média das 5 sementes, com o mínimo e o máximo entre colchetes. No grupo, as razões somam os dois pets e as
contagens são a média dos dois. O Champion não aparece: sem luta não há medalha, e o pet fica no Rookie (D-EQ0-2). "—" é sem dado (nenhuma
ração posta, nenhum lance ou nenhum despertar na célula).

## 1. As tabelas

### O ovo de um pet (v35), o atento

| estágio, dia | ração comida | rações postas | fome < 0,25 (min) | fome < 0,45 (fração) | cochilos | energia ao acordar | explorar | brincar | lances | chutes por lance |
|---|---|---|---|---|---|---|---|---|---|---|
| In-Training, 1 | 0.80 [0.25; 1.00] | 4.0 [4.0; 4.0] | 0 [0; 0] | 0.00 [0.00; 0.00] | 0.2 [0.0; 1.0] | — | 0.06 [0.00; 0.15] | 0.277 [0.077; 0.692] | 1.0 [1.0; 1.0] | 1.00 [1.00; 1.00] |
| Rookie, 1 | 0.90 [0.50; 1.00] | 2.6 [1.0; 6.0] | 0 [0; 0] | 0.04 [0.00; 0.13] | 6.4 [5.0; 9.0] | 0.93 [0.91; 0.95] | 0.31 [0.30; 0.33] | 0.033 [0.024; 0.036] | 0.2 [0.0; 1.0] | 1.00 [1.00; 1.00] |
| Rookie, 2 | 0.83 [0.67; 1.00] | 5.6 [5.0; 6.0] | 0 [0; 0] | 0.09 [0.08; 0.10] | 5.0 [5.0; 5.0] | 0.93 [0.92; 0.95] | 0.32 [0.28; 0.39] | 0.043 [0.021; 0.061] | 0.4 [0.0; 1.0] | 0.50 [0.00; 1.00] |
| Rookie, 3 | 0.33 [0.20; 0.40] | 3.0 [0.0; 5.0] | 0 [0; 0] | 0.05 [0.00; 0.09] | 5.6 [4.0; 9.0] | 0.92 [0.92; 0.94] | 0.35 [0.33; 0.39] | 0.058 [0.031; 0.094] | 0.4 [0.0; 1.0] | 1.50 [1.00; 2.00] |

| dia | fome < 0,25 (min) | cochilos | saúde no fim | Bits do Tamer |
|---|---|---|---|---|
| 1 | 0 [0; 0] | 6.6 [6.0; 9.0] | 1.00 [1.00; 1.00] | 156 [154; 159] |
| 2 | 0 [0; 0] | 5.0 [5.0; 5.0] | 1.00 [1.00; 1.00] | 10 [8; 12] |
| 3 | 0 [0; 0] | 5.6 [4.0; 9.0] | 1.00 [1.00; 1.00] | 6 [3; 8] |

Bits no total: 171 [168; 174] (chamado 12 [12; 12], cuidado na hora 19 [16; 22], evolução 50 [50; 50], nível do Tamer 90 [90; 90]); os 150 no minuto 180 [180; 180] do pet (dia 1 [1; 1]); o tempo do Champion no minuto 900 [900; 900]; mortes: 0.

### O ovo de um pet (v35), o medio

| estágio, dia | ração comida | rações postas | fome < 0,25 (min) | fome < 0,45 (fração) | cochilos | energia ao acordar | explorar | brincar | lances | chutes por lance |
|---|---|---|---|---|---|---|---|---|---|---|
| In-Training, 1 | — | 0.0 [0.0; 0.0] | 0 [0; 0] | 0.00 [0.00; 0.00] | 0.2 [0.0; 1.0] | — | 0.23 [0.17; 0.25] | 0.217 [0.167; 0.333] | 1.0 [1.0; 1.0] | 1.40 [1.00; 2.00] |
| Rookie, 1 | 1.00 [1.00; 1.00] | 2.2 [2.0; 3.0] | 9 [0; 30] | 0.25 [0.21; 0.29] | 5.8 [4.0; 7.0] | 0.89 [0.79; 0.93] | 0.20 [0.18; 0.24] | 0.043 [0.012; 0.095] | 0.0 [0.0; 0.0] | — |
| Rookie, 2 | 1.00 [1.00; 1.00] | 3.0 [3.0; 3.0] | 33 [0; 135] | 0.26 [0.25; 0.31] | 6.8 [5.0; 9.0] | 0.76 [0.33; 0.93] | 0.29 [0.24; 0.36] | 0.065 [0.052; 0.073] | 0.4 [0.0; 1.0] | 1.00 [1.00; 1.00] |
| Rookie, 3 | 1.00 [1.00; 1.00] | 2.8 [2.0; 3.0] | 0 [0; 0] | 0.28 [0.19; 0.36] | 6.2 [6.0; 7.0] | 0.84 [0.62; 0.92] | 0.29 [0.24; 0.33] | 0.060 [0.042; 0.094] | 0.8 [0.0; 1.0] | 1.00 [1.00; 1.00] |

| dia | fome < 0,25 (min) | cochilos | saúde no fim | Bits do Tamer |
|---|---|---|---|---|
| 1 | 9 [0; 30] | 6.0 [4.0; 7.0] | 1.00 [1.00; 1.00] | 143 [143; 144] |
| 2 | 33 [0; 135] | 6.8 [5.0; 9.0] | 1.00 [1.00; 1.00] | 6 [5; 8] |
| 3 | 0 [0; 0] | 6.2 [6.0; 7.0] | 1.00 [1.00; 1.00] | 6 [6; 7] |

Bits no total: 156 [154; 157] (chamado 0 [0; 0], cuidado na hora 16 [14; 17], evolução 50 [50; 50], nível do Tamer 90 [90; 90]); os 150 no minuto 2832 [2520; 3120] do pet (dia 3 [2; 3]); o tempo do Champion no minuto 900 [900; 900]; mortes: 0.

### O ovo de um pet (v35), o relapso

| estágio, dia | ração comida | rações postas | fome < 0,25 (min) | fome < 0,45 (fração) | cochilos | energia ao acordar | explorar | brincar | lances | chutes por lance |
|---|---|---|---|---|---|---|---|---|---|---|
| In-Training, 1 | — | 0.0 [0.0; 0.0] | 0 [0; 0] | 0.00 [0.00; 0.00] | 0.0 [0.0; 0.0] | — | 0.30 [0.25; 0.33] | 0.000 [0.000; 0.000] | 0.0 [0.0; 0.0] | — |
| Rookie, 1 | 1.00 [1.00; 1.00] | 2.0 [2.0; 2.0] | 273 [135; 495] | 0.57 [0.49; 0.69] | 9.0 [6.0; 15.0] | 0.47 [0.27; 0.91] | 0.15 [0.10; 0.21] | 0.012 [0.000; 0.024] | 2.0 [2.0; 2.0] | 0.20 [0.00; 0.50] |
| Rookie, 2 | 1.00 [1.00; 1.00] | 2.8 [2.0; 3.0] | 105 [15; 195] | 0.36 [0.24; 0.45] | 10.0 [6.0; 14.0] | 0.46 [0.26; 0.61] | 0.26 [0.23; 0.31] | 0.050 [0.031; 0.073] | 0.8 [0.0; 1.0] | 0.00 [0.00; 0.00] |
| Rookie, 3 | 1.00 [1.00; 1.00] | 2.2 [2.0; 3.0] | 140 [89; 224] | 0.49 [0.41; 0.57] | 8.2 [4.0; 12.0] | 0.54 [0.29; 0.92] | 0.30 [0.29; 0.31] | 0.040 [0.031; 0.042] | 0.8 [0.0; 1.0] | 0.75 [0.00; 1.00] |

| dia | fome < 0,25 (min) | cochilos | saúde no fim | Bits do Tamer |
|---|---|---|---|---|
| 1 | 273 [135; 495] | 9.0 [6.0; 15.0] | 0.96 [0.88; 1.00] | 145 [144; 145] |
| 2 | 105 [15; 195] | 10.0 [6.0; 14.0] | 1.00 [1.00; 1.00] | 6 [5; 7] |
| 3 | 140 [89; 224] | 8.2 [4.0; 12.0] | 0.99 [0.98; 1.00] | 5 [4; 6] |

Bits no total: 156 [154; 157] (chamado 0 [0; 0], cuidado na hora 16 [14; 17], evolução 50 [50; 50], nível do Tamer 90 [90; 90]); os 150 no minuto 2592 [2520; 2880] do pet (dia 2 [2; 3]); o tempo do Champion no minuto 900 [900; 900]; mortes: 0.

### O grupo do brasão (v36), o atento

| estágio, dia | ração comida | rações postas | fome < 0,25 (min) | fome < 0,45 (fração) | cochilos | energia ao acordar | explorar | brincar | lances | chutes por lance |
|---|---|---|---|---|---|---|---|---|---|---|
| In-Training, 1 | 0.80 [0.63; 1.00] | 4.0 [4.0; 4.0] | 0 [0; 0] | 0.00 [0.00; 0.00] | 0.7 [0.0; 1.0] | — | 0.07 [0.00; 0.15] | 0.477 [0.154; 0.731] | 1.0 [1.0; 1.0] | 1.80 [1.00; 2.00] |
| Rookie, 1 | 0.91 [0.80; 1.00] | 1.7 [0.0; 3.0] | 0 [0; 0] | 0.03 [0.00; 0.05] | 5.9 [5.5; 6.5] | 0.94 [0.92; 0.95] | 0.34 [0.30; 0.37] | 0.044 [0.030; 0.060] | 0.0 [0.0; 0.0] | — |
| Rookie, 2 | 1.00 [1.00; 1.00] | 3.0 [2.5; 4.0] | 0 [0; 0] | 0.05 [0.04; 0.05] | 5.7 [5.0; 6.5] | 0.93 [0.92; 0.94] | 0.29 [0.24; 0.34] | 0.057 [0.036; 0.109] | 0.5 [0.0; 1.0] | 0.88 [0.00; 2.00] |
| Rookie, 3 | 0.82 [0.45; 1.00] | 4.3 [3.5; 5.5] | 0 [0; 0] | 0.07 [0.03; 0.09] | 5.2 [4.5; 6.0] | 0.93 [0.91; 0.94] | 0.32 [0.27; 0.36] | 0.048 [0.031; 0.062] | 0.5 [0.0; 1.0] | 0.83 [0.50; 1.00] |

| dia | fome < 0,25 (min) | cochilos | saúde no fim | Bits do Tamer |
|---|---|---|---|---|
| 1 | 0 [0; 0] | 6.6 [6.0; 7.0] | 1.00 [1.00; 1.00] | 220 [216; 222] |
| 2 | 0 [0; 0] | 5.7 [5.0; 6.5] | 1.00 [1.00; 1.00] | 14 [13; 15] |
| 3 | 0 [0; 0] | 5.2 [4.5; 6.0] | 1.00 [1.00; 1.00] | 15 [13; 18] |

Bits no total: 249 [244; 253] (chamado 24 [24; 24], cuidado na hora 35 [30; 39], evolução 100 [100; 100], nível do Tamer 90 [90; 90]); os 150 no minuto 180 [180; 180] do pet (dia 1 [1; 1]); o tempo do Champion no minuto 900 [900; 900]; mortes: 0.

### O grupo do brasão (v36), o medio

| estágio, dia | ração comida | rações postas | fome < 0,25 (min) | fome < 0,45 (fração) | cochilos | energia ao acordar | explorar | brincar | lances | chutes por lance |
|---|---|---|---|---|---|---|---|---|---|---|
| In-Training, 1 | — | 0.0 [0.0; 0.0] | 0 [0; 0] | 0.00 [0.00; 0.00] | 0.6 [0.0; 1.0] | — | 0.23 [0.17; 0.25] | 0.233 [0.167; 0.292] | 1.0 [1.0; 1.0] | 2.40 [2.00; 4.00] |
| Rookie, 1 | 1.00 [1.00; 1.00] | 2.4 [2.0; 3.0] | 35 [0; 83] | 0.26 [0.23; 0.32] | 6.3 [5.0; 8.0] | 0.90 [0.80; 0.93] | 0.20 [0.17; 0.24] | 0.061 [0.042; 0.077] | 0.0 [0.0; 0.0] | — |
| Rookie, 2 | 1.00 [1.00; 1.00] | 3.0 [2.5; 3.5] | 9 [0; 38] | 0.23 [0.20; 0.27] | 6.5 [5.0; 7.5] | 0.84 [0.61; 0.92] | 0.25 [0.22; 0.27] | 0.045 [0.031; 0.057] | 0.8 [0.5; 1.5] | 0.73 [0.00; 1.00] |
| Rookie, 3 | 1.00 [1.00; 1.00] | 3.1 [2.5; 3.5] | 15 [0; 60] | 0.25 [0.21; 0.31] | 4.8 [4.5; 5.0] | 0.91 [0.89; 0.92] | 0.27 [0.26; 0.29] | 0.045 [0.026; 0.068] | 0.9 [0.0; 1.5] | 1.04 [0.33; 2.00] |

| dia | fome < 0,25 (min) | cochilos | saúde no fim | Bits do Tamer |
|---|---|---|---|---|
| 1 | 35 [0; 83] | 6.9 [6.0; 8.5] | 1.00 [1.00; 1.00] | 197 [196; 198] |
| 2 | 9 [0; 38] | 6.5 [5.0; 7.5] | 1.00 [1.00; 1.00] | 12 [9; 14] |
| 3 | 15 [0; 60] | 4.8 [4.5; 5.0] | 1.00 [1.00; 1.00] | 13 [10; 16] |

Bits no total: 222 [219; 224] (chamado 0 [0; 0], cuidado na hora 32 [29; 34], evolução 100 [100; 100], nível do Tamer 90 [90; 90]); os 150 no minuto 180 [180; 180] do pet (dia 1 [1; 1]); o tempo do Champion no minuto 900 [900; 900]; mortes: 0.

### O grupo do brasão (v36), o relapso

| estágio, dia | ração comida | rações postas | fome < 0,25 (min) | fome < 0,45 (fração) | cochilos | energia ao acordar | explorar | brincar | lances | chutes por lance |
|---|---|---|---|---|---|---|---|---|---|---|
| In-Training, 1 | — | 0.0 [0.0; 0.0] | 0 [0; 0] | 0.00 [0.00; 0.00] | 0.0 [0.0; 0.0] | — | 0.28 [0.25; 0.29] | 0.000 [0.000; 0.000] | 0.0 [0.0; 0.0] | — |
| Rookie, 1 | 1.00 [1.00; 1.00] | 1.6 [1.5; 2.0] | 397 [218; 487] | 0.58 [0.52; 0.62] | 10.4 [7.0; 12.5] | 0.55 [0.42; 0.65] | 0.13 [0.10; 0.14] | 0.031 [0.024; 0.048] | 1.6 [1.0; 2.0] | 0.27 [0.00; 0.50] |
| Rookie, 2 | 1.00 [1.00; 1.00] | 2.6 [2.5; 3.0] | 281 [75; 428] | 0.44 [0.32; 0.51] | 11.8 [8.0; 15.5] | 0.44 [0.30; 0.68] | 0.28 [0.23; 0.34] | 0.027 [0.016; 0.036] | 1.0 [0.5; 1.5] | 0.50 [0.00; 1.00] |
| Rookie, 3 | 1.00 [1.00; 1.00] | 2.6 [2.5; 3.0] | 271 [23; 488] | 0.45 [0.28; 0.57] | 12.8 [6.5; 20.0] | 0.57 [0.37; 0.69] | 0.29 [0.26; 0.31] | 0.041 [0.031; 0.057] | 1.2 [1.0; 1.5] | 0.80 [0.50; 1.33] |

| dia | fome < 0,25 (min) | cochilos | saúde no fim | Bits do Tamer |
|---|---|---|---|---|
| 1 | 397 [218; 487] | 10.4 [7.0; 12.5] | 0.85 [0.82; 0.95] | 198 [198; 199] |
| 2 | 281 [75; 428] | 11.8 [8.0; 15.5] | 0.88 [0.80; 0.98] | 11 [10; 13] |
| 3 | 271 [23; 488] | 12.8 [6.5; 20.0] | 0.92 [0.85; 0.99] | 13 [12; 13] |

Bits no total: 223 [221; 224] (chamado 0 [0; 0], cuidado na hora 33 [31; 34], evolução 100 [100; 100], nível do Tamer 90 [90; 90]); os 150 no minuto 180 [180; 180] do pet (dia 1 [1; 1]); o tempo do Champion no minuto 900 [900; 900]; mortes: 0.

## 2. As metas PROPOSTAS ao lado do retrato

Todas PROPOSTAS, SEM FONTE (seção 6 do plano). "Passa" = a média cumpre; M-E1 e M-D1, nas 5 sementes. As células sem dado não contam (D-EQ0-6).

| id | medida | meta PROPOSTA | dono | hoje: média [mín; máx] | passa hoje? |
|---|---|---|---|---|---|
| M-A1 | ração comida | ≥ 0,8 em cada estágio | atento | v35: In-Training d1 0.80 [0.25; 1.00]; Rookie d1 0.90 [0.50; 1.00]; Rookie d2 0.83 [0.67; 1.00]; Rookie d3 0.33 [0.20; 0.40] | **não passa** |
| M-A1 | ração comida | ≥ 0,8 em cada estágio | atento | v36: In-Training d1 0.80 [0.63; 1.00]; Rookie d1 0.91 [0.80; 1.00]; Rookie d2 1.00 [1.00; 1.00]; Rookie d3 0.82 [0.45; 1.00] | passa |
| M-A1 | ração comida | ≥ 0,8 em cada estágio | medio | v35: In-Training d1 —; Rookie d1 1.00 [1.00; 1.00]; Rookie d2 1.00 [1.00; 1.00]; Rookie d3 1.00 [1.00; 1.00] | passa |
| M-A1 | ração comida | ≥ 0,8 em cada estágio | medio | v36: In-Training d1 —; Rookie d1 1.00 [1.00; 1.00]; Rookie d2 1.00 [1.00; 1.00]; Rookie d3 1.00 [1.00; 1.00] | passa |
| M-A2 | fome < 0,25 (min) | ≤ 60 min/dia; 0 no In-Training | atento | v35: In-Training 0 [0; 0]; d1 0 [0; 0]; d2 0 [0; 0]; d3 0 [0; 0] | passa |
| M-A2 | fome < 0,25 (min) | ≤ 60 min/dia; 0 no In-Training | atento | v36: In-Training 0 [0; 0]; d1 0 [0; 0]; d2 0 [0; 0]; d3 0 [0; 0] | passa |
| M-A3 | fome < 0,25 (min) | ≤ 180 min/dia | medio | v35: d1 9 [0; 30]; d2 33 [0; 135]; d3 0 [0; 0] | passa |
| M-A3 | fome < 0,25 (min) | ≤ 180 min/dia | medio | v36: d1 35 [0; 83]; d2 9 [0; 38]; d3 15 [0; 60] | passa |
| M-A4 | fome < 0,45 (fração do tempo) | ≤ 0,30 | atento | v35: In-Training d1 0.00 [0.00; 0.00]; Rookie d1 0.04 [0.00; 0.13]; Rookie d2 0.09 [0.08; 0.10]; Rookie d3 0.05 [0.00; 0.09] | passa |
| M-A4 | fome < 0,45 (fração do tempo) | ≤ 0,30 | atento | v36: In-Training d1 0.00 [0.00; 0.00]; Rookie d1 0.03 [0.00; 0.05]; Rookie d2 0.05 [0.04; 0.05]; Rookie d3 0.07 [0.03; 0.09] | passa |
| M-A5 | saúde no fim do dia | ≥ 0,9 | atento | v35: d1 1.00 [1.00; 1.00]; d2 1.00 [1.00; 1.00]; d3 1.00 [1.00; 1.00] | passa |
| M-A5 | saúde no fim do dia | ≥ 0,9 | atento | v36: d1 1.00 [1.00; 1.00]; d2 1.00 [1.00; 1.00]; d3 1.00 [1.00; 1.00] | passa |
| M-A5 | saúde no fim do dia | ≥ 0,7 | medio | v35: d1 1.00 [1.00; 1.00]; d2 1.00 [1.00; 1.00]; d3 1.00 [1.00; 1.00] | passa |
| M-A5 | saúde no fim do dia | ≥ 0,7 | medio | v36: d1 1.00 [1.00; 1.00]; d2 1.00 [1.00; 1.00]; d3 1.00 [1.00; 1.00] | passa |
| M-A5 | saúde no fim do dia | ≥ 0,3 | relapso | v35: d1 0.96 [0.88; 1.00]; d2 1.00 [1.00; 1.00]; d3 0.99 [0.98; 1.00] | passa |
| M-A5 | saúde no fim do dia | ≥ 0,3 | relapso | v36: d1 0.85 [0.82; 0.95]; d2 0.88 [0.80; 0.98]; d3 0.92 [0.85; 0.99] | passa |
| M-B1 | cochilos por dia | de 2 a 6 nos dias 2 e 3 | atento | v35: d1 6.6 [6.0; 9.0]; d2 5.0 [5.0; 5.0]; d3 5.6 [4.0; 9.0] | passa |
| M-B1 | cochilos por dia | de 2 a 6 nos dias 2 e 3 | atento | v36: d1 6.6 [6.0; 7.0]; d2 5.7 [5.0; 6.5]; d3 5.2 [4.5; 6.0] | passa |
| M-B1 | cochilos por dia | de 2 a 6 nos dias 2 e 3 | medio | v35: d1 6.0 [4.0; 7.0]; d2 6.8 [5.0; 9.0]; d3 6.2 [6.0; 7.0] | **não passa** |
| M-B1 | cochilos por dia | de 2 a 6 nos dias 2 e 3 | medio | v36: d1 6.9 [6.0; 8.5]; d2 6.5 [5.0; 7.5]; d3 4.8 [4.5; 5.0] | **não passa** |
| M-B1 | cochilos por dia | de 2 a 6 nos dias 2 e 3 | relapso | v35: d1 9.0 [6.0; 15.0]; d2 10.0 [6.0; 14.0]; d3 8.2 [4.0; 12.0] | **não passa** |
| M-B1 | cochilos por dia | de 2 a 6 nos dias 2 e 3 | relapso | v36: d1 10.4 [7.0; 12.5]; d2 11.8 [8.0; 15.5]; d3 12.8 [6.5; 20.0] | **não passa** |
| M-B2 | energia mediana ao acordar | ≥ 0,9 | atento | v35: Rookie d1 0.93 [0.91; 0.95]; Rookie d2 0.93 [0.92; 0.95]; Rookie d3 0.92 [0.92; 0.94] | passa |
| M-B2 | energia mediana ao acordar | ≥ 0,9 | atento | v36: Rookie d1 0.94 [0.92; 0.95]; Rookie d2 0.93 [0.92; 0.94]; Rookie d3 0.93 [0.91; 0.94] | passa |
| M-B2 | energia mediana ao acordar | ≥ 0,9 | medio | v35: Rookie d1 0.89 [0.79; 0.93]; Rookie d2 0.76 [0.33; 0.93]; Rookie d3 0.84 [0.62; 0.92] | **não passa** |
| M-B2 | energia mediana ao acordar | ≥ 0,9 | medio | v36: Rookie d1 0.90 [0.80; 0.93]; Rookie d2 0.84 [0.61; 0.92]; Rookie d3 0.91 [0.89; 0.92] | **não passa** |
| M-B2 | energia mediana ao acordar | ≥ 0,9 | relapso | v35: Rookie d1 0.47 [0.27; 0.91]; Rookie d2 0.46 [0.26; 0.61]; Rookie d3 0.54 [0.29; 0.92] | **não passa** |
| M-B2 | energia mediana ao acordar | ≥ 0,9 | relapso | v36: Rookie d1 0.55 [0.42; 0.65]; Rookie d2 0.44 [0.30; 0.68]; Rookie d3 0.57 [0.37; 0.69] | **não passa** |
| M-B3 | explorar (fração das decisões) | ≥ 0,10 no Rookie | atento | v35: Rookie d1 0.31 [0.30; 0.33]; Rookie d2 0.32 [0.28; 0.39]; Rookie d3 0.35 [0.33; 0.39] | passa |
| M-B3 | explorar (fração das decisões) | ≥ 0,10 no Rookie | atento | v36: Rookie d1 0.34 [0.30; 0.37]; Rookie d2 0.29 [0.24; 0.34]; Rookie d3 0.32 [0.27; 0.36] | passa |
| M-B3 | explorar (fração das decisões) | ≥ 0,10 no Rookie | medio | v35: Rookie d1 0.20 [0.18; 0.24]; Rookie d2 0.29 [0.24; 0.36]; Rookie d3 0.29 [0.24; 0.33] | passa |
| M-B3 | explorar (fração das decisões) | ≥ 0,10 no Rookie | medio | v36: Rookie d1 0.20 [0.17; 0.24]; Rookie d2 0.25 [0.22; 0.27]; Rookie d3 0.27 [0.26; 0.29] | passa |
| M-B4 | brincar (fração das decisões) | ≥ 0,05 no Rookie | atento | v35: Rookie d1 0.033 [0.024; 0.036]; Rookie d2 0.043 [0.021; 0.061]; Rookie d3 0.058 [0.031; 0.094] | **não passa** |
| M-B4 | brincar (fração das decisões) | ≥ 0,05 no Rookie | atento | v36: Rookie d1 0.044 [0.030; 0.060]; Rookie d2 0.057 [0.036; 0.109]; Rookie d3 0.048 [0.031; 0.062] | **não passa** |
| M-C1 | chutes por lance (a vida) | ≥ 0,8 | atento | v35: 1.00 [0.50; 1.50] (lances por pet 2.0 [1.0; 3.0]) | passa |
| M-C1 | chutes por lance (a vida) | ≥ 0,8 | atento | v36: 1.42 [1.00; 2.00] (lances por pet 2.0 [1.0; 3.0]) | passa |
| M-C1 | chutes por lance (a vida) | ≥ 0,8 | medio | v35: 1.20 [1.00; 1.50] (lances por pet 2.2 [2.0; 3.0]) | passa |
| M-C1 | chutes por lance (a vida) | ≥ 0,8 | medio | v36: 1.42 [1.00; 1.67] (lances por pet 2.7 [1.5; 3.5]) | passa |
| M-C1 | chutes por lance (a vida) | ≥ 0,8 | relapso | v35: 0.30 [0.00; 0.67] (lances por pet 3.6 [3.0; 4.0]) | **não passa** |
| M-C1 | chutes por lance (a vida) | ≥ 0,8 | relapso | v36: 0.55 [0.33; 0.86] (lances por pet 3.8 [3.0; 4.5]) | **não passa** |
| M-D1 | mortes | 0 | atento | v35: 0 | passa |
| M-D1 | mortes | 0 | atento | v36: 0 | passa |
| M-D1 | mortes | 0 | medio | v35: 0 | passa |
| M-D1 | mortes | 0 | medio | v36: 0 | passa |
| M-D1 | mortes | 0 | relapso | v35: 0 | passa |
| M-D1 | mortes | 0 | relapso | v36: 0 | passa |
| M-E1 | ★★ (150 Bits) antes do Champion | nas 5 sementes | atento | v35: 150 no min 180 [180; 180] do pet; o tempo do Champion no min 900 [900; 900]; 5/5 | passa |
| M-E1 | ★★ (150 Bits) antes do Champion | nas 5 sementes | atento | v36: 150 no min 180 [180; 180] do pet; o tempo do Champion no min 900 [900; 900]; 5/5 | passa |
| M-E1 | ★★ (150 Bits) antes do Champion | nas 5 sementes | medio | v35: 150 no min 2832 [2520; 3120] do pet; o tempo do Champion no min 900 [900; 900]; 0/5 | **não passa** |
| M-E1 | ★★ (150 Bits) antes do Champion | nas 5 sementes | medio | v36: 150 no min 180 [180; 180] do pet; o tempo do Champion no min 900 [900; 900]; 5/5 | passa |
| M-E2 | Bits por dia | ≥ 20 nos três dias | atento | v35: d1 156 [154; 159]; d2 10 [8; 12]; d3 6 [3; 8] | **não passa** |
| M-E2 | Bits por dia | ≥ 20 nos três dias | atento | v36: d1 220 [216; 222]; d2 14 [13; 15]; d3 15 [13; 18] | **não passa** |

## 3. O que mais pesa para quem joga

1. **Os Bits param depois do 1º dia.** O Tamer ganha de 143 a 222 Bits no dia 1, quase tudo de uma vez só: a evolução para o Rookie (50 por
   pet) e os níveis 1 a 3 do Tamer (90). Nos dias 2 e 3, sem luta, o cuidado rende de 5 a 15 Bits por dia, longe do teto de 20. Nem o
   atento passa a M-E2 (≥ 20 por dia). O cuidado na hora certa do Rookie paga 1 Bit, e só quando o corpo cai abaixo de 0,45 (fome) ou 0,25 (higiene, humor), o que é raro.
2. **No ovo de um pet, o ★★ antes do Champion depende de 7 Bits e do In-Training.** O atento junta os 150 no minuto 180 (a evolução), mas o
   médio fica com 143 no dia 1 e só chega aos 150 entre os dias 2 e 3, depois do tempo do Champion (minuto 900): a M-E1 falha nas 5
   sementes. O médio não ganha nada no In-Training (0 Bits de chamado). E o relapso chega aos 150 antes do médio (dia 2,2 contra 2,6),
   porque o corpo dele cai mais e cada cuidado na hora paga 1 Bit. No grupo, as duas evoluções (100) fecham o ★★ no minuto 180 para todos.
3. **O médio e o relapso não alimentam o In-Training.** O médio olha às 2 h, com a fome ainda acima de 0,7, e o relapso só chega no Rookie:
   nenhuma ração posta no In-Training (as duas versões). O atento põe 4 rações no In-Training, e o bebê come de 25 % a 100 % delas
   (média 0,80); no ovo de um pet, no 3º dia do Rookie, o atento come só 0,33 do que põe (a ração acumula: ele come abaixo de 0,45).
4. **O relapso quebra o sono que segura.** Com o relapso, o pet acorda com a energia mediana de 0,44 a 0,57 e faz de 8 a 13 cochilos por
   dia, contra uns 5 e acima de 0,9 com o atento (M-B1 e M-B2). O médio fica na borda: de 4,8 a 6,9 cochilos e de 0,76 a 0,91 ao acordar.
   É a fome urgente que acorda o pet: a fome < 0,25 do relapso vai de 105 a 397 min por dia.
5. **Ninguém adoece de verdade em 3 dias.** A saúde no fim do dia fica em 1,00 com o atento e o médio e, com o relapso, a média do dia não desce de 0,85 (o pior pet chegou a 0,59: o
   B do grupo, semente 93101, dia 2), e ninguém morre (sem luta, o motor não mata). O castigo do relapso é o sono, a fome e os chutes (0,30 a 0,55 por lance, contra 1,0 a 1,4
   com o atento e o médio: ele brinca com o pet cansado ou com fome), não a saúde.

## 4. O que não deu para medir

- **o Champion e tudo da luta** (as vitórias, as medalhas, os Bits da luta): nenhum dono do EQ-4 luta, e o Champion pede 1 medalha. O
  "pronto para o Champion" é só o tempo (o minuto 900 do pet);
- **os chutes por lance têm poucos lances:** o dono só brinca quando o humor cai abaixo do limiar (0,8 no In-Training, 0,25 no Rookie):
  de 2 a 4 lances por pet na vida. No grupo, a rolagem pode ser do irmão (o registro do mundo não diz quem chutou);
- **o nível 4 do Tamer em diante** (o primeiro treino, as medalhas): o roteiro não treina;
- **a árvore** (o bloco D): os donos não sacodem.

## 5. O que vem

O Matheus aprova (ou troca) as metas da seção 2 (EQ-3). Depois, o E1 calibra na mesma faixa 93101…93505, na ordem do EQ-2.
