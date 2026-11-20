# Resumo das metas, lp5_2, calibracao

commit `516511d93c7c2e6f351f72b18acf82c4cb75ac3a`, candidato `n0500`, 17255 lutas, 24.375 s somados nos processos.

**Passam (2):** D1, D3. **Falham (4):** P1, P2, P3, D2.

| # | a meta | o criterio | passa | os valores (resumo; o inteiro no resumo.json) |
|---|---|---|---|---|
| P1 | o Gazimon | sem treino <= 0,20; tipico >= 0,70; pior especie >= 0,50 | **nao** | {nome:Gazimon,estagio:crianca,mapa:campo,sem_treino:0.243,ic_sem:[0.214,0.273],tipico:0.328,ic_tipico:[0.296,0.361],pior_especie:0,por_especie:{brasa:0.371,cirro:0,limo:0.425,ferrugem:0.386}} |
| P2 | os 6 lideres | cada um: sem treino <= 0,20; tipico >= 0,70; pior especie >= 0,50 (a Cidadela, a serie de 3) | **nao** | {Gazimon:{nome:Gazimon,estagio:crianca,mapa:campo,sem_treino:0.243,ic_sem:[0.214,0.273],tipico:0.328,ic_tipico:[0.296,0.361],pior_especie:0,por_especie:{brasa:0.371,cirro:0,limo:0.425,ferrugem:0.386},passa:false},Guardro |
| P3 | os 4 desafiantes | cada um: sem treino <= 0,35; tipico >= 0,75 | **nao** | {Tortomon:{nome:Tortomon,estagio:adolescente,mapa:coliseu,sem_treino:0.288,ic_sem:[0.257,0.32],tipico:0.584,ic_tipico:[0.549,0.617],pior_especie:0.4,por_especie:{brasa:0.488,limo:0.82,ferrugem:0.435,cirro:0.4},passa:fals |
| D1 | a duracao | mediana de cada estagio de 15 a 40 s; p90 <= 60 s; nenhuma forma com mediana < 8 s | sim | {por_estagio:{crianca:{mediana_s:20.65,p90_s:28.75,lutas:1600},adolescente:{mediana_s:22.05,p90_s:29.55,lutas:6400},adulto:{mediana_s:18.85,p90_s:30.75,lutas:4455},mega:{mediana_s:21.45,p90_s:33.95,lutas:4800}},formas_cu |
| D2 | sem fim e empate | lutas no limite <= 0,5 %; empates <= 2 % em cada forma | **nao** | {sem_fim:0,lutas:17255,empate_total:0.018,empate_max_forma:0.119,formas_acima_de_2pc:[brasa_adolescente_colosso (0.031),npc_tier2_carcereiro (0.028),limo_adolescente_cacador (0.025),ferrugem_adolescente_brigao (0.097),li |
| D3 | a Cidadela cabe | a serie de 3 (pet tipico) no p90 <= 180 s | sim | {p90_s:58.35,mediana_s:37.45} |
