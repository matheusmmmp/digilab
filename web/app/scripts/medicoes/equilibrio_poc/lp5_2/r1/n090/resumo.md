# Resumo das metas, lp5_2, calibracao

commit `5e3c01f0c113fb6379b018aeea206458fd65df65`, candidato `n090`, 17736 lutas, 23.957 s somados nos processos.

**Passam (2):** D1, D3. **Falham (4):** P1, P2, P3, D2.

| # | a meta | o criterio | passa | os valores (resumo; o inteiro no resumo.json) |
|---|---|---|---|---|
| P1 | o Gazimon | sem treino <= 0,20; tipico >= 0,70; pior especie >= 0,50 | **nao** | {nome:Gazimon,estagio:crianca,mapa:campo,sem_treino:0.35,ic_sem:[0.318,0.384],tipico:0.558,ic_tipico:[0.523,0.592],pior_especie:0.014,por_especie:{brasa:0.829,cirro:0.014,limo:0.429,ferrugem:0.893}} |
| P2 | os 6 lideres | cada um: sem treino <= 0,20; tipico >= 0,70; pior especie >= 0,50 (a Cidadela, a serie de 3) | **nao** | {Gazimon:{nome:Gazimon,estagio:crianca,mapa:campo,sem_treino:0.35,ic_sem:[0.318,0.384],tipico:0.558,ic_tipico:[0.523,0.592],pior_especie:0.014,por_especie:{brasa:0.829,cirro:0.014,limo:0.429,ferrugem:0.893},passa:false}, |
| P3 | os 4 desafiantes | cada um: sem treino <= 0,35; tipico >= 0,75 | **nao** | {Tortomon:{nome:Tortomon,estagio:adolescente,mapa:coliseu,sem_treino:0.496,ic_sem:[0.462,0.531],tipico:0.926,ic_tipico:[0.906,0.942],pior_especie:0.631,por_especie:{brasa:0.631,limo:1,ferrugem:1,cirro:1},passa:false},Dev |
| D1 | a duracao | mediana de cada estagio de 15 a 40 s; p90 <= 60 s; nenhuma forma com mediana < 8 s | sim | {por_estagio:{crianca:{mediana_s:20.05,p90_s:27.55,lutas:1600},adolescente:{mediana_s:20.75,p90_s:28.45,lutas:6400},adulto:{mediana_s:18.85,p90_s:28.25,lutas:4936},mega:{mediana_s:19.15,p90_s:27.85,lutas:4800}},formas_cu |
| D2 | sem fim e empate | lutas no limite <= 0,5 %; empates <= 2 % em cada forma | **nao** | {sem_fim:0,lutas:17736,empate_total:0.015,empate_max_forma:0.119,formas_acima_de_2pc:[brasa_crianca_arisco (0.088),npc_tier2_carcereiro (0.022),ferrugem_adolescente_brigao (0.063),limo_adolescente_colosso (0.033),brasa_a |
| D3 | a Cidadela cabe | a serie de 3 (pet tipico) no p90 <= 180 s | sim | {p90_s:54.05,mediana_s:41.75} |
