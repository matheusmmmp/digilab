# Resumo das metas, lp5_2, calibracao

commit `5e3c01f0c113fb6379b018aeea206458fd65df65`, candidato `n050`, 17867 lutas, 24.201 s somados nos processos.

**Passam (2):** D1, D3. **Falham (4):** P1, P2, P3, D2.

| # | a meta | o criterio | passa | os valores (resumo; o inteiro no resumo.json) |
|---|---|---|---|---|
| P1 | o Gazimon | sem treino <= 0,20; tipico >= 0,70; pior especie >= 0,50 | **nao** | {nome:Gazimon,estagio:crianca,mapa:campo,sem_treino:0.434,ic_sem:[0.4,0.468],tipico:0.61,ic_tipico:[0.576,0.643],pior_especie:0.029,por_especie:{brasa:0.971,cirro:0.029,limo:0.429,ferrugem:0.936}} |
| P2 | os 6 lideres | cada um: sem treino <= 0,20; tipico >= 0,70; pior especie >= 0,50 (a Cidadela, a serie de 3) | **nao** | {Gazimon:{nome:Gazimon,estagio:crianca,mapa:campo,sem_treino:0.434,ic_sem:[0.4,0.468],tipico:0.61,ic_tipico:[0.576,0.643],pior_especie:0.029,por_especie:{brasa:0.971,cirro:0.029,limo:0.429,ferrugem:0.936},passa:false},Gu |
| P3 | os 4 desafiantes | cada um: sem treino <= 0,35; tipico >= 0,75 | **nao** | {Tortomon:{nome:Tortomon,estagio:adolescente,mapa:coliseu,sem_treino:0.728,ic_sem:[0.696,0.757],tipico:0.93,ic_tipico:[0.91,0.946],pior_especie:0.656,por_especie:{brasa:0.656,limo:1,ferrugem:0.995,cirro:1},passa:false},D |
| D1 | a duracao | mediana de cada estagio de 15 a 40 s; p90 <= 60 s; nenhuma forma com mediana < 8 s | sim | {por_estagio:{crianca:{mediana_s:19.85,p90_s:27.15,lutas:1600},adolescente:{mediana_s:21.25,p90_s:28.95,lutas:6400},adulto:{mediana_s:18.35,p90_s:27.75,lutas:5067},mega:{mediana_s:18.75,p90_s:27.65,lutas:4800}},formas_cu |
| D2 | sem fim e empate | lutas no limite <= 0,5 %; empates <= 2 % em cada forma | **nao** | {sem_fim:0,lutas:17867,empate_total:0.009,empate_max_forma:0.091,formas_acima_de_2pc:[brasa_crianca_arisco (0.091),brasa_adolescente_guardiao (0.023),ferrugem_adolescente_colosso (0.028),cirro_adolescente_cacador (0.04), |
| D3 | a Cidadela cabe | a serie de 3 (pet tipico) no p90 <= 180 s | sim | {p90_s:54.15,mediana_s:42.15} |
