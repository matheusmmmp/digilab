# RESULTADO_V3_EQUILIBRIO_CUIDADO_E2: a validação única do dia a dia do pet

Fase: V3. Frente: EQUILIBRIO_CUIDADO, etapa E2. Data: 2026-11-12. Worker: Claude Code (Opus 5.5), branch `v3-equilibrio-e2`.
Plano: `docs/PLANO_V3_EQUILIBRIO_CUIDADO.md`. Gates e conta: o adendo 1 (seção 9) do `docs/PLANO_ANALISE_V3_EQUILIBRIO_CUIDADO.md`,
commitado antes da primeira vida da validação (`f46c7a4c`); o modo de validação da bancada entrou no commit seguinte (`0e1a6918`), também
antes da run. O E0 e o E1: `docs/RESULTADO_V3_EQUILIBRIO_CUIDADO_E0.md` e `_E1.md`.

**O que rodou, uma vez:** a F2 do E1 com as chaves ligadas (o `AJUSTE_E1_PROPOSTO` e a `BITS_V2`, APROVADOS pelo Matheus em 2026-11-12,
"Aprovo, siga"), nas 30 vidas da validação: o ovo de um pet **v35** e o grupo do brasão **v37** (o `VERSAO_GRUPO` depois do merge da
`main`; a calibração foi na v36, D-EQ2-1), os três donos do EQ-4, as sementes **94101, 94202, 94303, 94404 e 94505**, 3 dias no ritmo
"rapida", um processo só (uns 12 s). Nada foi ajustado depois. As réguas são as de hoje: a M-A1 e a M-C1 não mudaram.

**Os artefatos** (todo número abaixo sai deles), em `web/app/scripts/medicoes/equilibrio_cuidado_e2/`:
- as 30 vidas `<versao>_<dono>_<semente>.json`, o `rodada.json`, o `resumo.json` e o `tabelas.md` (as tabelas por dono, estágio e dia);
- o `comparacao.md`: as 52 linhas de meta no E0, no E1 (a rodada `E1_escolhido`, na calibração) e no E2;
- o comando: `node scripts/equilibrio_cuidado/e2.ts` (em `web/app`); ele recusa rodar de novo numa pasta com vidas. O
  `node scripts/equilibrio_cuidado/e2.ts --tabela` só refaz o `comparacao.md`.

## 1. As metas: o E0, o E1 e o E2

A conta é a do D-EQ0-6: média das 5 sementes, com o mínimo e o máximo; na M-E1 e na M-D1, as 5 sementes. **Das 52 linhas de meta, 16 falham
no E0, 6 no E1 (calibração) e 10 no E2 (validação).** Nenhuma linha fica sem dado. A tabela traz as 17 linhas que falham em alguma das três;
as outras 35 passam nas três (a tabela inteira está no `comparacao.md`).

| id | dono | versão | E0 (calibração, sem chave) | E1 (calibração, F2) | E2 (validação, F2) | E0 | E1 | E2 |
|---|---|---|---|---|---|---|---|---|
| M-A1 | atento | pet | IT 0.80; R1 0.90; R2 0.83; R3 0.33 | IT 1.00; R1 0.89; R2 0.77; R3 0.78 | IT 0.85 [0.50; 1.00]; R1 0.70 [0.40; 1.00]; R2 0.74 [0.60; 0.80]; R3 0.57 [0.00; 1.00] | não | não | **não** |
| M-B4 | atento | pet | 0.033; 0.043; 0.058 | 0.054; 0.066; 0.060 | 0.082; 0.072; 0.076 | não | sim | sim |
| M-E2 | atento | pet | 156; 10; 6 | 173; 34; 28 | 185; 34 [15; 40]; 29 [15; 55] | não | sim | sim |
| M-B1 | médio | pet | d2 6.8; d3 6.2 | d2 4.2; d3 4.4 | d2 4.4; d3 4.4 | não | sim | sim |
| M-B2 | médio | pet | 0.89; 0.76; 0.84 | 0.93; 0.94; 0.94 | 0.93; 0.93; 0.93 | não | sim | sim |
| M-E1 | médio | pet | 0/5 | 5/5 | 5/5 | não | sim | sim |
| M-B1 | relapso | pet | d2 10.0; d3 8.2 | d2 4.8; d3 4.4 | d2 4.6 [4; 6]; d3 7.6 [3; 15] | não | sim | **não** |
| M-B2 | relapso | pet | 0.47; 0.46; 0.54 | 0.43; 0.92; 0.90 | 0.57; 0.89; 0.67 | não | não | **não** |
| M-C1 | relapso | pet | 0.30 | 0.88 | 0.63 [0.00; 1.00] (1.8 lance por pet) | não | sim | **não** |
| M-A1 | atento | grupo | IT 0.80; R1 0.91; R2 1.00; R3 0.82 | IT 1.00; R1 0.97; R2 0.89; R3 0.83 | IT 1.00; R1 1.00; R2 0.98; R3 0.72 [0.47; 1.00] | sim | sim | **não** |
| M-B4 | atento | grupo | 0.044; 0.057; 0.048 | 0.089; 0.075; 0.062 | 0.073; 0.0496; 0.068 | não | sim | **não** |
| M-E2 | atento | grupo | 220; 14; 15 | 267; 54; 56 | 265; 57; 57 | não | sim | sim |
| M-B1 | médio | grupo | d2 6.5; d3 4.8 | d2 4.6; d3 4.4 | d2 4.5; d3 4.7 | não | sim | sim |
| M-B2 | médio | grupo | 0.90; 0.84; 0.91 | 0.87; 0.93; 0.93 | 0.81 [0.63; 0.94]; 0.93; 0.92 | não | não | **não** |
| M-B1 | relapso | grupo | d2 11.8; d3 12.8 | d2 6.1; d3 8.6 | d2 6.8; d3 7.4 | não | não | **não** |
| M-B2 | relapso | grupo | 0.55; 0.44; 0.57 | 0.49; 0.85; 0.67 | 0.60; 0.74; 0.64 | não | não | **não** |
| M-C1 | relapso | grupo | 0.55 | 0.52 | 0.47 [0.17; 1.00] (2.3 lances por pet) | não | não | **não** |

IT = In-Training dia 1; R1 a R3 = Rookie dias 1 a 3; nas metas de dia (M-B1, M-E2), os dias. O E0 e o E1 do grupo são da v36; o E2 é da v37.

## 2. O que passa e o que falha

**Passam na validação (42 de 52):** a fome e a saúde de todos (M-A2 a M-A5), o explorar (M-B3), o ★★ antes do Champion (M-E1, 5 de 5 em
todo Tamer), os Bits por dia do atento (M-E2, nas duas versões), nenhuma morte (M-D1), o sono do médio do ovo de um pet (M-B1 e M-B2), os
cochilos do médio do grupo (M-B1), o brincar do atento do ovo de um pet (M-B4) e os chutes do atento e do médio (M-C1).

**Das 6 que falhavam no E1, as 6 falham também no E2**, como estão: a ração do Rookie do atento do ovo de um pet (M-A1; a medida e o dono,
D-EQ1-6), o sono do relapso (M-B2 no ovo de um pet; M-B1 e M-B2 no grupo), a energia ao acordar do médio do grupo no dia 1 (M-B2: 0,81) e
os chutes do relapso do grupo (M-C1; a guarda, D-EQ1-7).

**Falham na validação e passavam na calibração (4):**
- **M-B1 do relapso do ovo de um pet:** o 3º dia tem 7,6 cochilos em média, com uma semente em 15; o 2º dia fica em 4,6. É o sono do relapso
  de novo, o mesmo achado da seção 4 do E1: a fome do dono que some 6 h acorda o pet.
- **M-C1 do relapso do ovo de um pet:** 0,63 chute por lance, com 1,8 lance por pet. No E1 eram 0,88 com 1,4 lance. Com tão poucos lances, a
  meta mexe muito de semente para semente (de 0 a 1); a guarda recusa o lance com o pet faminto (D-EQ1-7).
- **M-A1 do atento do grupo:** o 3º dia do Rookie fica em 0,72 (de 0,47 a 1,00). É o mesmo mecanismo da M-A1 do ovo de um pet (D-EQ1-6): as
  rações postas no fim do 3º dia, com o pet dormindo, não têm tempo de ser comidas. No E0 e no E1 o grupo passava por pouco (0,82 e 0,83).
  Esta é a única linha que passava no E0 e cai no E2.
- **M-B4 do atento do grupo:** o 2º dia do Rookie fica em 0,0496, contra a meta de 0,05; o 1º e o 3º dias passam (0,073 e 0,068). É a meta
  na borda.

**O que pesa na leitura:** o grupo da validação é a v37, com a CO6 e a CO7 (a reputação do irmão e os deveres no modular), e não a v36 da
calibração. Parte da diferença do grupo entre o E1 e o E2 pode vir disso e não das sementes; esta rodada não separa as duas coisas
(D-EQ2-1). O ovo de um pet é a mesma v35 nas três etapas.

**Em uma linha:** a validação confirma o ganho grande do E1 (de 16 para 10 linhas falhando, com 7 das 16 do E0 consertadas e mantidas), mas
não o número da calibração (6): as metas do relapso e as que ficam na borda (a ração do 3º dia, o brincar de 0,05) entram e saem com as
sementes. Nenhum gate que falha para a rodada (adendo 1): segue o E3.

## 3. O que vem

O E3 (a versão nova do pet, EQ-6) entra no mesmo branch, com os números da F2 como estão. As propostas ao Matheus seguem as do E1 (D-EQ1-6 a
D-EQ1-8: a régua da M-A1, a da M-C1 e uma fonte de Bits que pague o cuidado bom), agora com os números da validação ao lado.
