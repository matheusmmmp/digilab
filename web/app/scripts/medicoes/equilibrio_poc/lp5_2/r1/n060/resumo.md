# Resumo das metas, lp5_2, calibracao

commit `5e3c01f0c113fb6379b018aeea206458fd65df65`, candidato `n060`, 17822 lutas, 23.915 s somados nos processos.

**Passam (2):** D1, D3. **Falham (4):** P1, P2, P3, D2.

| # | a meta | o criterio | passa | os valores (resumo; o inteiro no resumo.json) |
|---|---|---|---|---|
| P1 | o Gazimon | sem treino <= 0,20; tipico >= 0,70; pior especie >= 0,50 | **nao** | {nome:Gazimon,estagio:crianca,mapa:campo,sem_treino:0.398,ic_sem:[0.364,0.432],tipico:0.603,ic_tipico:[0.568,0.636],pior_especie:0.036,por_especie:{brasa:0.933,cirro:0.036,limo:0.429,ferrugem:0.95}} |
| P2 | os 6 lideres | cada um: sem treino <= 0,20; tipico >= 0,70; pior especie >= 0,50 (a Cidadela, a serie de 3) | **nao** | {Gazimon:{nome:Gazimon,estagio:crianca,mapa:campo,sem_treino:0.398,ic_sem:[0.364,0.432],tipico:0.603,ic_tipico:[0.568,0.636],pior_especie:0.036,por_especie:{brasa:0.933,cirro:0.036,limo:0.429,ferrugem:0.95},passa:false}, |
| P3 | os 4 desafiantes | cada um: sem treino <= 0,35; tipico >= 0,75 | **nao** | {Tortomon:{nome:Tortomon,estagio:adolescente,mapa:coliseu,sem_treino:0.659,ic_sem:[0.625,0.691],tipico:0.928,ic_tipico:[0.907,0.943],pior_especie:0.638,por_especie:{brasa:0.638,limo:1,ferrugem:1,cirro:1},passa:false},Dev |
| D1 | a duracao | mediana de cada estagio de 15 a 40 s; p90 <= 60 s; nenhuma forma com mediana < 8 s | sim | {por_estagio:{crianca:{mediana_s:19.55,p90_s:27.25,lutas:1600},adolescente:{mediana_s:21.25,p90_s:29.05,lutas:6400},adulto:{mediana_s:18.55,p90_s:27.75,lutas:5022},mega:{mediana_s:18.75,p90_s:27.65,lutas:4800}},formas_cu |
| D2 | sem fim e empate | lutas no limite <= 0,5 %; empates <= 2 % em cada forma | **nao** | {sem_fim:0,lutas:17822,empate_total:0.01,empate_max_forma:0.096,formas_acima_de_2pc:[brasa_crianca_arisco (0.028),ferrugem_adolescente_brigao (0.034),brasa_adolescente_guardiao (0.021),ferrugem_adolescente_cacador (0.028 |
| D3 | a Cidadela cabe | a serie de 3 (pet tipico) no p90 <= 180 s | sim | {p90_s:53.45,mediana_s:42.05} |
