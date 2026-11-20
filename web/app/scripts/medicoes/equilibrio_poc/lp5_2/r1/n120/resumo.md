# Resumo das metas, lp5_2, calibracao

commit `5e3c01f0c113fb6379b018aeea206458fd65df65`, candidato `n120`, 17687 lutas, 24.098 s somados nos processos.

**Passam (2):** D1, D3. **Falham (4):** P1, P2, P3, D2.

| # | a meta | o criterio | passa | os valores (resumo; o inteiro no resumo.json) |
|---|---|---|---|---|
| P1 | o Gazimon | sem treino <= 0,20; tipico >= 0,70; pior especie >= 0,50 | **nao** | {nome:Gazimon,estagio:crianca,mapa:campo,sem_treino:0.309,ic_sem:[0.278,0.342],tipico:0.491,ic_tipico:[0.457,0.526],pior_especie:0,por_especie:{brasa:0.708,cirro:0,limo:0.429,ferrugem:0.736}} |
| P2 | os 6 lideres | cada um: sem treino <= 0,20; tipico >= 0,70; pior especie >= 0,50 (a Cidadela, a serie de 3) | **nao** | {Gazimon:{nome:Gazimon,estagio:crianca,mapa:campo,sem_treino:0.309,ic_sem:[0.278,0.342],tipico:0.491,ic_tipico:[0.457,0.526],pior_especie:0,por_especie:{brasa:0.708,cirro:0,limo:0.429,ferrugem:0.736},passa:false},Guardro |
| P3 | os 4 desafiantes | cada um: sem treino <= 0,35; tipico >= 0,75 | **nao** | {Tortomon:{nome:Tortomon,estagio:adolescente,mapa:coliseu,sem_treino:0.49,ic_sem:[0.455,0.525],tipico:0.916,ic_tipico:[0.895,0.934],pior_especie:0.625,por_especie:{brasa:0.625,limo:0.997,ferrugem:0.98,cirro:0.986},passa: |
| D1 | a duracao | mediana de cada estagio de 15 a 40 s; p90 <= 60 s; nenhuma forma com mediana < 8 s | sim | {por_estagio:{crianca:{mediana_s:20.05,p90_s:28.15,lutas:1600},adolescente:{mediana_s:20.65,p90_s:28.35,lutas:6400},adulto:{mediana_s:18.85,p90_s:28.45,lutas:4887},mega:{mediana_s:19.15,p90_s:28.15,lutas:4800}},formas_cu |
| D2 | sem fim e empate | lutas no limite <= 0,5 %; empates <= 2 % em cada forma | **nao** | {sem_fim:0,lutas:17687,empate_total:0.011,empate_max_forma:0.116,formas_acima_de_2pc:[npc_tier1_brutamontes (0.024),brasa_crianca_arisco (0.116),ferrugem_crianca_sereno (0.025),limo_adolescente_cacador (0.023),ferrugem_a |
| D3 | a Cidadela cabe | a serie de 3 (pet tipico) no p90 <= 180 s | sim | {p90_s:55.35,mediana_s:41.75} |
