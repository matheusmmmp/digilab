# Resumo das metas, lp5_2, calibracao

commit `5e3c01f0c113fb6379b018aeea206458fd65df65`, candidato `n130`, 17647 lutas, 22.18 s somados nos processos.

**Passam (2):** D1, D3. **Falham (4):** P1, P2, P3, D2.

| # | a meta | o criterio | passa | os valores (resumo; o inteiro no resumo.json) |
|---|---|---|---|---|
| P1 | o Gazimon | sem treino <= 0,20; tipico >= 0,70; pior especie >= 0,50 | **nao** | {nome:Gazimon,estagio:crianca,mapa:campo,sem_treino:0.298,ic_sem:[0.267,0.33],tipico:0.498,ic_tipico:[0.463,0.532],pior_especie:0.007,por_especie:{brasa:0.704,cirro:0.007,limo:0.429,ferrugem:0.771}} |
| P2 | os 6 lideres | cada um: sem treino <= 0,20; tipico >= 0,70; pior especie >= 0,50 (a Cidadela, a serie de 3) | **nao** | {Gazimon:{nome:Gazimon,estagio:crianca,mapa:campo,sem_treino:0.298,ic_sem:[0.267,0.33],tipico:0.498,ic_tipico:[0.463,0.532],pior_especie:0.007,por_especie:{brasa:0.704,cirro:0.007,limo:0.429,ferrugem:0.771},passa:false}, |
| P3 | os 4 desafiantes | cada um: sem treino <= 0,35; tipico >= 0,75 | **nao** | {Tortomon:{nome:Tortomon,estagio:adolescente,mapa:coliseu,sem_treino:0.464,ic_sem:[0.429,0.498],tipico:0.906,ic_tipico:[0.884,0.925],pior_especie:0.613,por_especie:{brasa:0.613,limo:0.997,ferrugem:0.96,cirro:0.971},passa |
| D1 | a duracao | mediana de cada estagio de 15 a 40 s; p90 <= 60 s; nenhuma forma com mediana < 8 s | sim | {por_estagio:{crianca:{mediana_s:20.35,p90_s:28.05,lutas:1600},adolescente:{mediana_s:20.55,p90_s:28.55,lutas:6400},adulto:{mediana_s:18.95,p90_s:28.75,lutas:4847},mega:{mediana_s:19.25,p90_s:28.65,lutas:4800}},formas_cu |
| D2 | sem fim e empate | lutas no limite <= 0,5 %; empates <= 2 % em cada forma | **nao** | {sem_fim:0,lutas:17647,empate_total:0.011,empate_max_forma:0.125,formas_acima_de_2pc:[npc_tier1_brutamontes (0.025),brasa_crianca_arisco (0.125),limo_adolescente_cacador (0.021),ferrugem_adolescente_brigao (0.05),limo_ad |
| D3 | a Cidadela cabe | a serie de 3 (pet tipico) no p90 <= 180 s | sim | {p90_s:55.55,mediana_s:41.25} |
