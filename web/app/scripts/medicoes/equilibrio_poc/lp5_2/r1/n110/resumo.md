# Resumo das metas, lp5_2, calibracao

commit `5e3c01f0c113fb6379b018aeea206458fd65df65`, candidato `n110`, 17697 lutas, 24.323 s somados nos processos.

**Passam (2):** D1, D3. **Falham (4):** P1, P2, P3, D2.

| # | a meta | o criterio | passa | os valores (resumo; o inteiro no resumo.json) |
|---|---|---|---|---|
| P1 | o Gazimon | sem treino <= 0,20; tipico >= 0,70; pior especie >= 0,50 | **nao** | {nome:Gazimon,estagio:crianca,mapa:campo,sem_treino:0.326,ic_sem:[0.295,0.36],tipico:0.515,ic_tipico:[0.48,0.549],pior_especie:0.014,por_especie:{brasa:0.758,cirro:0.014,limo:0.429,ferrugem:0.771}} |
| P2 | os 6 lideres | cada um: sem treino <= 0,20; tipico >= 0,70; pior especie >= 0,50 (a Cidadela, a serie de 3) | **nao** | {Gazimon:{nome:Gazimon,estagio:crianca,mapa:campo,sem_treino:0.326,ic_sem:[0.295,0.36],tipico:0.515,ic_tipico:[0.48,0.549],pior_especie:0.014,por_especie:{brasa:0.758,cirro:0.014,limo:0.429,ferrugem:0.771},passa:false},G |
| P3 | os 4 desafiantes | cada um: sem treino <= 0,35; tipico >= 0,75 | **nao** | {Tortomon:{nome:Tortomon,estagio:adolescente,mapa:coliseu,sem_treino:0.474,ic_sem:[0.439,0.508],tipico:0.921,ic_tipico:[0.901,0.938],pior_especie:0.638,por_especie:{brasa:0.638,limo:0.997,ferrugem:0.995,cirro:0.979},pass |
| D1 | a duracao | mediana de cada estagio de 15 a 40 s; p90 <= 60 s; nenhuma forma com mediana < 8 s | sim | {por_estagio:{crianca:{mediana_s:20.05,p90_s:27.85,lutas:1600},adolescente:{mediana_s:20.75,p90_s:28.55,lutas:6400},adulto:{mediana_s:18.85,p90_s:28.45,lutas:4897},mega:{mediana_s:19.05,p90_s:28.45,lutas:4800}},formas_cu |
| D2 | sem fim e empate | lutas no limite <= 0,5 %; empates <= 2 % em cada forma | **nao** | {sem_fim:0,lutas:17697,empate_total:0.012,empate_max_forma:0.106,formas_acima_de_2pc:[npc_tier1_brutamontes (0.023),brasa_crianca_arisco (0.106),ferrugem_crianca_sereno (0.025),limo_adolescente_cacador (0.023),ferrugem_a |
| D3 | a Cidadela cabe | a serie de 3 (pet tipico) no p90 <= 180 s | sim | {p90_s:54.85,mediana_s:41.85} |
