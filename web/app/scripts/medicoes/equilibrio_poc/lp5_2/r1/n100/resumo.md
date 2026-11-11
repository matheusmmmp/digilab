# Resumo das metas, lp5_2, calibracao

commit `5e3c01f0c113fb6379b018aeea206458fd65df65`, candidato `n100`, 17726 lutas, 24.026 s somados nos processos.

**Passam (2):** D1, D3. **Falham (4):** P1, P2, P3, D2.

| # | a meta | o criterio | passa | os valores (resumo; o inteiro no resumo.json) |
|---|---|---|---|---|
| P1 | o Gazimon | sem treino <= 0,20; tipico >= 0,70; pior especie >= 0,50 | **nao** | {nome:Gazimon,estagio:crianca,mapa:campo,sem_treino:0.341,ic_sem:[0.309,0.375],tipico:0.544,ic_tipico:[0.509,0.578],pior_especie:0.029,por_especie:{brasa:0.8,cirro:0.029,limo:0.429,ferrugem:0.85}} |
| P2 | os 6 lideres | cada um: sem treino <= 0,20; tipico >= 0,70; pior especie >= 0,50 (a Cidadela, a serie de 3) | **nao** | {Gazimon:{nome:Gazimon,estagio:crianca,mapa:campo,sem_treino:0.341,ic_sem:[0.309,0.375],tipico:0.544,ic_tipico:[0.509,0.578],pior_especie:0.029,por_especie:{brasa:0.8,cirro:0.029,limo:0.429,ferrugem:0.85},passa:false},Gu |
| P3 | os 4 desafiantes | cada um: sem treino <= 0,35; tipico >= 0,75 | **nao** | {Tortomon:{nome:Tortomon,estagio:adolescente,mapa:coliseu,sem_treino:0.493,ic_sem:[0.458,0.527],tipico:0.92,ic_tipico:[0.899,0.937],pior_especie:0.631,por_especie:{brasa:0.631,limo:0.993,ferrugem:0.99,cirro:0.993},passa: |
| D1 | a duracao | mediana de cada estagio de 15 a 40 s; p90 <= 60 s; nenhuma forma com mediana < 8 s | sim | {por_estagio:{crianca:{mediana_s:19.95,p90_s:27.75,lutas:1600},adolescente:{mediana_s:20.65,p90_s:28.25,lutas:6400},adulto:{mediana_s:18.75,p90_s:28.25,lutas:4926},mega:{mediana_s:19.05,p90_s:27.75,lutas:4800}},formas_cu |
| D2 | sem fim e empate | lutas no limite <= 0,5 %; empates <= 2 % em cada forma | **nao** | {sem_fim:0,lutas:17726,empate_total:0.012,empate_max_forma:0.098,formas_acima_de_2pc:[brasa_crianca_arisco (0.069),limo_adolescente_cacador (0.02),ferrugem_adolescente_brigao (0.047),limo_adolescente_colosso (0.04),ferru |
| D3 | a Cidadela cabe | a serie de 3 (pet tipico) no p90 <= 180 s | sim | {p90_s:54.45,mediana_s:41.85} |
