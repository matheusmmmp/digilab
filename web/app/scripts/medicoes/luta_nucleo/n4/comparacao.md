# A N4: os contrafactuais contra a base (faixa investigacao)

Le os resumo.json de scripts/medicoes/equilibrio_poc/n4_*/investigacao/. As regras sao as da secao 8.2 do plano: **move** = entra na faixa ou chega 0,05 mais perto dela; **quebra** = passava na base e falha; **nao age** = toda diferenca abaixo de 0,02. O G1 conta titulos (0 na base).

## Quantas metas passam

| medida | passam | as que passam |
|---|---|---|
| n4_base_v23 | 9 | P1, P4, T1, T3, E1, D1, D3, A2, G4 |
| n4_atr100 | 8 | P1, P3, P4, P5, T1, D1, D3, A2 |
| n4_atr115 | 6 | P1, P4, T1, D1, D3, A2 |
| n4_atr125 | 7 | P1, P4, T1, T3, D1, D3, A2 |
| n4_morto | 10 | P1, P4, T1, T3, E1, D1, D2, D3, A2, G4 |
| n4_pulo | 7 | P1, T3, E1, D1, D3, A2, G4 |
| n4_borda | 8 | P1, P4, T3, E1, D1, D3, A2, G4 |
| n4_juntas_v23 | 7 | P1, P4, D1, D2, D3, A2, S1 |
| n4_base_v29 | 9 | P1, P4, T1, T3, E1, D1, D3, A2, G4 |
| n4_juntas_v29 | 7 | P1, P4, D1, D2, D3, A2, S1 |

## n4_atr100 contra n4_base_v23

| meta | base | com a chave | o que muda (a leitura: base -> chave) |
|---|---|---|---|
| P1 | passa | passa (muda sem chegar) | sem 0.355 -> 0.24; tip 0.605 -> 0.831 |
| P2 | falha | falha (move) | Gazimon_sem 0.355 -> 0.24; Gazimon_tip 0.605 -> 0.831; Guardromon_sem 0.678 -> 0.343; Guardromon_tip 0.836 -> 0.959; Youkomon_sem 0.196 -> 0.296; Youkomon_tip 0.473 -> 0.944; Myotismon_tip 0.248 -> 0.002; Piedmon_sem 0.543 -> 0.224 |
| P3 | falha | passa (passa a passar) | Tortomon_sem 0.422 -> 0.356; Tortomon_tip 0.906 -> 0.983; Devidramon_sem 0.608 -> 0.214; Devidramon_tip 0.765 -> 0.726; Puppetmon_sem 0.579 -> 0.395; Puppetmon_tip 0.677 -> 0.883; Machinedramon_sem 0.564 -> 0.319; Machinedramon_tip 0.727 -> 0.974 |
| P4 | passa | passa (muda sem chegar) | adolescente 0.83 -> 1 |
| P5 | falha | passa (passa a passar) | mega 0.24 -> 0.85 |
| T1 | passa | passa (nao age) | — |
| T2 | falha | falha (nao age) | — |
| T3 | passa | falha (quebra) | teto_crianca 0.743 -> 0.888; teto_adolescente 0.834 -> 0.977; teto_adulto 0.903 -> 0.97; teto_mega 0.85 -> 0.993; degrau_crianca 0.153 -> 0.231; degrau_adolescente 0.176 -> 0.245; degrau_adulto 0.198 -> 0.225; degrau_mega 0.157 -> 0.24 |
| E1 | passa | falha (quebra) | crianca_tipico_contra_adolescente 0.194 -> 0.021; crianca_teto_contra_adolescente 0.203 -> 0.018; adolescente_tipico_contra_adulto 0.189 -> 0.119; adolescente_teto_contra_adulto 0.187 -> 0.118; adolescente_tipico_contra_mega 0.023 -> 0; adulto_tipico_contra_mega 0.214 -> 0.186; adulto_teto_contra_mega 0.218 -> 0.189 |
| D1 | passa | passa (muda sem chegar) | crianca 22.45 -> 24.55; adolescente 24.85 -> 26.25; adulto 25.05 -> 25.75; mega 24.35 -> 25.85 |
| D2 | falha | falha (nao age) | — |
| D3 | passa | passa (muda sem chegar) | p90_s 55.15 -> 52.05 |
| A1 | falha | falha (move) | crianca_soma 0.471 -> 0.514; crianca_ringue 0.086 -> 0.05; crianca_castelo 0.17 -> 0.137; adolescente_ringue 0.127 -> 0.083; adolescente_castelo 0.244 -> 0.208; adulto_soma 0.581 -> 0.533; adulto_ringue 0.144 -> 0.073; adulto_castelo 0.388 -> 0.325 |
| A2 | passa | passa (nao age) | — |
| V1 | falha | falha (move) | crianca 0.305 -> 0.181; adolescente 0.398 -> 0.205; adulto 0.438 -> 0.192; mega 0.39 -> 0.118 |
| V2 | falha | falha (move) | crianca 0.257 -> 0.164; adolescente 0.159 -> 0.033; mega 0.093 -> 0.007 |
| G1 | falha | falha (nao age) | — |
| G2 | falha | falha (nao age) | — |
| G3 | falha | falha (nao age) | — |
| G4 | passa | falha (quebra) | crianca 0.727 -> 0.874; adolescente 0.848 -> 0.983; adulto 0.927 -> 0.985; mega 0.859 -> 0.996 |
| S1 | falha | falha (nao age) | — |

## n4_atr115 contra n4_base_v23

| meta | base | com a chave | o que muda (a leitura: base -> chave) |
|---|---|---|---|
| P1 | passa | passa (muda sem chegar) | sem 0.355 -> 0.333; tip 0.605 -> 0.662 |
| P2 | falha | falha (move) | Gazimon_sem 0.355 -> 0.333; Gazimon_tip 0.605 -> 0.662; Guardromon_sem 0.678 -> 0.642; Guardromon_tip 0.836 -> 0.891; Youkomon_tip 0.473 -> 0.771; Myotismon_tip 0.248 -> 0.03; Piedmon_sem 0.543 -> 0.448; Piedmon_tip 0.706 -> 0.859 |
| P3 | falha | falha (move) | Tortomon_tip 0.906 -> 0.951; Devidramon_sem 0.608 -> 0.522; Puppetmon_sem 0.579 -> 0.542; Puppetmon_tip 0.677 -> 0.792; Machinedramon_sem 0.564 -> 0.505; Machinedramon_tip 0.727 -> 0.939 |
| P4 | passa | passa (muda sem chegar) | adolescente 0.83 -> 0.99 |
| P5 | falha | falha (move) | mega 0.24 -> 0.56 |
| T1 | passa | passa (nao age) | — |
| T2 | falha | falha (nao age) | — |
| T3 | passa | falha (quebra) | teto_crianca 0.743 -> 0.795; teto_adolescente 0.834 -> 0.917; teto_adulto 0.903 -> 0.963; teto_mega 0.85 -> 0.96; degrau_mega 0.157 -> 0.19 |
| E1 | passa | falha (quebra) | crianca_tipico_contra_adolescente 0.194 -> 0.032; crianca_teto_contra_adolescente 0.203 -> 0.039; adolescente_tipico_contra_adulto 0.189 -> 0.134; adolescente_teto_contra_adulto 0.187 -> 0.132; adolescente_tipico_contra_mega 0.023 -> 0.001; adulto_tipico_contra_mega 0.214 -> 0.191; adulto_teto_contra_mega 0.218 -> 0.197 |
| D1 | passa | passa (muda sem chegar) | crianca 22.45 -> 23.45; adolescente 24.85 -> 25.45; adulto 25.05 -> 25.45; mega 24.35 -> 25.25 |
| D2 | falha | falha (nao age) | — |
| D3 | passa | passa (nao age) | p90_s 55.15 -> 56.05 |
| A1 | falha | falha (muda sem chegar) | crianca_soma 0.471 -> 0.493; crianca_ringue 0.086 -> 0.048; crianca_castelo 0.17 -> 0.15; adolescente_ringue 0.127 -> 0.09; adulto_ringue 0.144 -> 0.09; mega_soma 0.479 -> 0.522; mega_ringue 0.207 -> 0.13 |
| A2 | passa | passa (nao age) | — |
| V1 | falha | falha (move) | crianca 0.305 -> 0.259; adolescente 0.398 -> 0.367; adulto 0.438 -> 0.406 |
| V2 | falha | falha (move) | crianca 0.257 -> 0.277; adolescente 0.159 -> 0.066; mega 0.093 -> 0.03 |
| G1 | falha | falha (nao age) | — |
| G2 | falha | falha (nao age) | — |
| G3 | falha | falha (nao age) | — |
| G4 | passa | falha (quebra) | crianca 0.727 -> 0.796; adolescente 0.848 -> 0.936; adulto 0.927 -> 0.978; mega 0.859 -> 0.97 |
| S1 | falha | falha (nao age) | — |

## n4_atr125 contra n4_base_v23

| meta | base | com a chave | o que muda (a leitura: base -> chave) |
|---|---|---|---|
| P1 | passa | passa (muda sem chegar) | tip 0.605 -> 0.629 |
| P2 | falha | falha (move) | Gazimon_tip 0.605 -> 0.629; Guardromon_tip 0.836 -> 0.858; Youkomon_tip 0.473 -> 0.627; Myotismon_tip 0.248 -> 0.079; Piedmon_sem 0.543 -> 0.502; Piedmon_tip 0.706 -> 0.795 |
| P3 | falha | falha (move) | Tortomon_tip 0.906 -> 0.93; Puppetmon_tip 0.677 -> 0.722; Machinedramon_sem 0.564 -> 0.531; Machinedramon_tip 0.727 -> 0.856 |
| P4 | passa | passa (muda sem chegar) | adolescente 0.83 -> 0.92 |
| P5 | falha | falha (move) | mega 0.24 -> 0.42 |
| T1 | passa | passa (nao age) | — |
| T2 | falha | falha (nao age) | — |
| T3 | passa | passa (muda sem chegar) | teto_crianca 0.743 -> 0.768; teto_adolescente 0.834 -> 0.882; teto_adulto 0.903 -> 0.944; teto_mega 0.85 -> 0.93; degrau_mega 0.157 -> 0.179 |
| E1 | passa | falha (quebra) | crianca_tipico_contra_adolescente 0.194 -> 0.052; crianca_teto_contra_adolescente 0.203 -> 0.073; adolescente_tipico_contra_adulto 0.189 -> 0.156; adolescente_teto_contra_adulto 0.187 -> 0.152; adolescente_tipico_contra_mega 0.023 -> 0.003 |
| D1 | passa | passa (muda sem chegar) | crianca 22.45 -> 22.95; adolescente 24.85 -> 25.15; adulto 25.05 -> 25.25; mega 24.35 -> 25.05 |
| D2 | falha | falha (nao age) | — |
| D3 | passa | passa (nao age) | p90_s 55.15 -> 56.25 |
| A1 | falha | falha (muda sem chegar) | crianca_ringue 0.086 -> 0.058; adolescente_ringue 0.127 -> 0.101; adulto_ringue 0.144 -> 0.106; mega_ringue 0.207 -> 0.154 |
| A2 | passa | passa (nao age) | — |
| V1 | falha | falha (move) | — |
| V2 | falha | falha (move) | crianca 0.257 -> 0.285; adolescente 0.159 -> 0.112; mega 0.093 -> 0.052 |
| G1 | falha | falha (nao age) | — |
| G2 | falha | falha (nao age) | — |
| G3 | falha | falha (nao age) | — |
| G4 | passa | falha (quebra) | crianca 0.727 -> 0.756; adolescente 0.848 -> 0.901; adulto 0.927 -> 0.971; mega 0.859 -> 0.939 |
| S1 | falha | falha (nao age) | — |

## n4_morto contra n4_base_v23

| meta | base | com a chave | o que muda (a leitura: base -> chave) |
|---|---|---|---|
| P1 | passa | passa (nao age) | — |
| P2 | falha | falha (muda sem chegar) | Myotismon_tip 0.248 -> 0.277 |
| P3 | falha | falha (muda sem chegar) | Tortomon_sem 0.422 -> 0.46 |
| P4 | passa | passa (nao age) | — |
| P5 | falha | falha (nao age) | — |
| T1 | passa | passa (nao age) | — |
| T2 | falha | falha (move) | crianca_folego 0.471 -> 0.519; adulto_folego 0.456 -> 0.526 |
| T3 | passa | passa (muda sem chegar) | rookie_teto_tipico 0.55 -> 0.613 |
| E1 | passa | passa (nao age) | — |
| D1 | passa | passa (nao age) | — |
| D2 | falha | passa (passa a passar) | empate_total 0.04 -> 0; empate_max_forma 0.113 -> 0 |
| D3 | passa | passa (nao age) | p90_s 55.15 -> 55.35 |
| A1 | falha | falha (nao age) | — |
| A2 | passa | passa (nao age) | — |
| V1 | falha | falha (move) | crianca 0.305 -> 0.284 |
| V2 | falha | falha (nao age) | — |
| G1 | falha | falha (nao age) | — |
| G2 | falha | falha (nao age) | — |
| G3 | falha | falha (nao age) | — |
| G4 | passa | passa (nao age) | — |
| S1 | falha | falha (move) | crianca_min 0.459 -> 0.483 |

## n4_pulo contra n4_base_v23

| meta | base | com a chave | o que muda (a leitura: base -> chave) |
|---|---|---|---|
| P1 | passa | passa (nao age) | — |
| P2 | falha | falha (move) | Myotismon_tip 0.248 -> 0.3; MarinBullmon_tip 0.782 -> 0.807 |
| P3 | falha | falha (nao age) | — |
| P4 | passa | falha (quebra) | adolescente 0.83 -> 0.77; adulto 1 -> 0.97 |
| P5 | falha | falha (muda sem chegar) | mega 0.24 -> 0.14 |
| T1 | passa | falha (quebra) | crianca 0.832 -> 0.856; adolescente 0.906 -> 0.957; adulto 0.94 -> 0.979; mega 0.948 -> 0.985 |
| T2 | falha | falha (nao age) | — |
| T3 | passa | passa (nao age) | — |
| E1 | passa | passa (muda sem chegar) | adolescente_tipico_contra_adulto 0.189 -> 0.15; adolescente_teto_contra_adulto 0.187 -> 0.15; adulto_tipico_contra_mega 0.214 -> 0.153; adulto_teto_contra_mega 0.218 -> 0.155 |
| D1 | passa | passa (nao age) | adolescente 24.85 -> 24.95; adulto 25.05 -> 25.15; mega 24.35 -> 24.45 |
| D2 | falha | falha (nao age) | — |
| D3 | passa | passa (muda sem chegar) | p90_s 55.15 -> 51.45 |
| A1 | falha | falha (nao age) | — |
| A2 | passa | passa (nao age) | — |
| V1 | falha | falha (nao age) | — |
| V2 | falha | falha (nao age) | — |
| G1 | falha | falha (nao age) | — |
| G2 | falha | falha (muda sem chegar) | recorde_mediano 1 -> 2 |
| G3 | falha | falha (nao age) | — |
| G4 | passa | passa (muda sem chegar) | adolescente 0.848 -> 0.828; adulto 0.927 -> 0.907 |
| S1 | falha | falha (move) | — |

## n4_borda contra n4_base_v23

| meta | base | com a chave | o que muda (a leitura: base -> chave) |
|---|---|---|---|
| P1 | passa | passa (nao age) | — |
| P2 | falha | falha (nao age) | — |
| P3 | falha | falha (nao age) | — |
| P4 | passa | passa (nao age) | — |
| P5 | falha | falha (nao age) | — |
| T1 | passa | falha (quebra) | crianca 0.832 -> 0.864; adolescente 0.906 -> 0.976; adulto 0.94 -> 0.983; mega 0.948 -> 0.991 |
| T2 | falha | falha (nao age) | — |
| T3 | passa | passa (nao age) | — |
| E1 | passa | passa (nao age) | — |
| D1 | passa | passa (nao age) | adulto 25.05 -> 24.95; mega 24.35 -> 24.15 |
| D2 | falha | falha (nao age) | — |
| D3 | passa | passa (nao age) | — |
| A1 | falha | falha (move) | crianca_ringue 0.086 -> 0.143; adolescente_ringue 0.127 -> 0.155; adulto_ringue 0.144 -> 0.217 |
| A2 | passa | passa (muda sem chegar) | crianca 108 -> 100; adolescente 108 -> 104; adulto 104 -> 100; mega 100 -> 96 |
| V1 | falha | falha (nao age) | — |
| V2 | falha | falha (nao age) | — |
| G1 | falha | falha (nao age) | — |
| G2 | falha | falha (muda sem chegar) | recorde_mediano 1 -> 2 |
| G3 | falha | falha (nao age) | — |
| G4 | passa | passa (nao age) | — |
| S1 | falha | falha (nao age) | — |

## n4_juntas_v23 contra n4_base_v23

| meta | base | com a chave | o que muda (a leitura: base -> chave) |
|---|---|---|---|
| P1 | passa | passa (muda sem chegar) | tip 0.605 -> 0.655 |
| P2 | falha | falha (move) | Gazimon_tip 0.605 -> 0.655; Guardromon_sem 0.678 -> 0.658; Guardromon_tip 0.836 -> 0.905; Youkomon_sem 0.196 -> 0.226; Youkomon_tip 0.473 -> 0.781; Myotismon_tip 0.248 -> 0.028; MarinBullmon_tip 0.782 -> 0.807; Piedmon_sem 0.543 -> 0.48 |
| P3 | falha | falha (move) | Tortomon_sem 0.422 -> 0.457; Tortomon_tip 0.906 -> 0.951; Devidramon_sem 0.608 -> 0.534; Devidramon_tip 0.765 -> 0.798; Puppetmon_sem 0.579 -> 0.554; Puppetmon_tip 0.677 -> 0.801; Machinedramon_sem 0.564 -> 0.507; Machinedramon_tip 0.727 -> 0.913 |
| P4 | passa | passa (muda sem chegar) | adolescente 0.83 -> 0.91 |
| P5 | falha | falha (move) | mega 0.24 -> 0.46 |
| T1 | passa | falha (quebra) | crianca 0.832 -> 0.865; adolescente 0.906 -> 0.972; adulto 0.94 -> 0.984; mega 0.948 -> 0.992 |
| T2 | falha | falha (move) | crianca_folego 0.471 -> 0.517; adulto_folego 0.456 -> 0.532 |
| T3 | passa | falha (quebra) | teto_crianca 0.743 -> 0.779; teto_adolescente 0.834 -> 0.904; teto_adulto 0.903 -> 0.962; teto_mega 0.85 -> 0.956; rookie_teto_tipico 0.55 -> 0.603 |
| E1 | passa | falha (quebra) | crianca_tipico_contra_adolescente 0.194 -> 0.022; crianca_teto_contra_adolescente 0.203 -> 0.022; adolescente_tipico_contra_adulto 0.189 -> 0.082; adolescente_teto_contra_adulto 0.187 -> 0.085; adolescente_tipico_contra_mega 0.023 -> 0.001; adulto_tipico_contra_mega 0.214 -> 0.126; adulto_teto_contra_mega 0.218 -> 0.129 |
| D1 | passa | passa (muda sem chegar) | crianca 22.45 -> 23.35; adolescente 24.85 -> 25.55; adulto 25.05 -> 25.45; mega 24.35 -> 25.25 |
| D2 | falha | passa (passa a passar) | empate_total 0.04 -> 0; empate_max_forma 0.113 -> 0 |
| D3 | passa | passa (muda sem chegar) | p90_s 55.15 -> 50.55 |
| A1 | falha | falha (muda sem chegar) | crianca_soma 0.471 -> 0.503; crianca_ringue 0.086 -> 0.122; crianca_castelo 0.17 -> 0.15; mega_soma 0.479 -> 0.526; mega_ringue 0.207 -> 0.119 |
| A2 | passa | passa (muda sem chegar) | crianca 108 -> 100; adolescente 108 -> 104; adulto 104 -> 100; mega 100 -> 96 |
| V1 | falha | falha (move) | crianca 0.305 -> 0.239 |
| V2 | falha | falha (move) | adolescente 0.159 -> 0.089; mega 0.093 -> 0.048 |
| G1 | falha | falha (nao age) | — |
| G2 | falha | falha (muda sem chegar) | recorde_mediano 1 -> 2 |
| G3 | falha | falha (nao age) | — |
| G4 | passa | falha (quebra) | crianca 0.727 -> 0.786; adolescente 0.848 -> 0.927; adulto 0.927 -> 0.979; mega 0.859 -> 0.968 |
| S1 | falha | passa (passa a passar) | crianca_min 0.459 -> 0.485 |

## n4_juntas_v29 contra n4_base_v29

| meta | base | com a chave | o que muda (a leitura: base -> chave) |
|---|---|---|---|
| P1 | passa | passa (muda sem chegar) | tip 0.605 -> 0.655 |
| P2 | falha | falha (move) | Gazimon_tip 0.605 -> 0.655; Guardromon_sem 0.678 -> 0.658; Guardromon_tip 0.836 -> 0.905; Youkomon_sem 0.196 -> 0.226; Youkomon_tip 0.473 -> 0.781; Myotismon_tip 0.199 -> 0.001; MarinBullmon_tip 0.717 -> 0.77; Piedmon_sem 0.556 -> 0.508 |
| P3 | falha | falha (move) | Tortomon_sem 0.422 -> 0.457; Tortomon_tip 0.906 -> 0.951; Devidramon_sem 0.608 -> 0.534; Devidramon_tip 0.765 -> 0.798; Puppetmon_tip 0.692 -> 0.814; Machinedramon_tip 0.735 -> 0.918 |
| P4 | passa | passa (muda sem chegar) | adolescente 0.83 -> 0.91; adulto 0.95 -> 1 |
| P5 | falha | falha (move) | mega 0.21 -> 0.46 |
| T1 | passa | falha (quebra) | crianca 0.832 -> 0.865; adolescente 0.906 -> 0.972; adulto 0.931 -> 0.982; mega 0.911 -> 0.99 |
| T2 | falha | falha (move) | crianca_folego 0.471 -> 0.517; adulto_folego 0.477 -> 0.538 |
| T3 | passa | falha (quebra) | teto_crianca 0.743 -> 0.779; teto_adolescente 0.834 -> 0.904; teto_adulto 0.883 -> 0.959; teto_mega 0.834 -> 0.954; rookie_teto_tipico 0.55 -> 0.603 |
| E1 | passa | falha (quebra) | crianca_tipico_contra_adolescente 0.194 -> 0.022; crianca_teto_contra_adolescente 0.203 -> 0.022; adolescente_tipico_contra_adulto 0.111 -> 0.056; adolescente_teto_contra_adulto 0.111 -> 0.058; adulto_tipico_contra_mega 0.136 -> 0.104; adulto_teto_contra_mega 0.133 -> 0.1 |
| D1 | passa | passa (muda sem chegar) | crianca 22.45 -> 23.35; adolescente 24.85 -> 25.45; adulto 23.95 -> 24.55; mega 23.95 -> 24.85 |
| D2 | falha | passa (passa a passar) | empate_total 0.047 -> 0; empate_max_forma 0.115 -> 0 |
| D3 | passa | passa (muda sem chegar) | p90_s 56.35 -> 49.55 |
| A1 | falha | falha (move) | crianca_soma 0.471 -> 0.503; crianca_ringue 0.086 -> 0.122; crianca_castelo 0.17 -> 0.15; adulto_ringue 0.194 -> 0.352; mega_soma 0.468 -> 0.524; mega_ringue 0.243 -> 0.407 |
| A2 | passa | passa (muda sem chegar) | crianca 108 -> 100; adolescente 108 -> 104; adulto 112 -> 108 |
| V1 | falha | falha (move) | crianca 0.305 -> 0.239; adulto 0.463 -> 0.429 |
| V2 | falha | falha (move) | adolescente 0.159 -> 0.089; adulto 0.071 -> 0.036; mega 0.109 -> 0.059 |
| G1 | falha | falha (nao age) | — |
| G2 | falha | falha (muda sem chegar) | recorde_mediano 1 -> 2 |
| G3 | falha | falha (nao age) | — |
| G4 | passa | falha (quebra) | crianca 0.727 -> 0.786; adolescente 0.848 -> 0.927; adulto 0.895 -> 0.977; mega 0.845 -> 0.958 |
| S1 | falha | passa (passa a passar) | crianca_min 0.459 -> 0.485 |
