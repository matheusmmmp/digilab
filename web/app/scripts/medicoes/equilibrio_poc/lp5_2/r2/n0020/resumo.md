# Resumo das metas, lp5_2, calibracao

commit `516511d93c7c2e6f351f72b18acf82c4cb75ac3a`, candidato `n0020`, 17995 lutas, 24.466 s somados nos processos.

**Passam (3):** D1, D2, D3. **Falham (3):** P1, P2, P3.

| # | a meta | o criterio | passa | os valores (resumo; o inteiro no resumo.json) |
|---|---|---|---|---|
| P1 | o Gazimon | sem treino <= 0,20; tipico >= 0,70; pior especie >= 0,50 | **nao** | {nome:Gazimon,estagio:crianca,mapa:campo,sem_treino:0.579,ic_sem:[0.544,0.613],tipico:0.643,ic_tipico:[0.609,0.675],pior_especie:0.1,por_especie:{brasa:1,cirro:0.1,limo:0.439,ferrugem:0.979}} |
| P2 | os 6 lideres | cada um: sem treino <= 0,20; tipico >= 0,70; pior especie >= 0,50 (a Cidadela, a serie de 3) | **nao** | {Gazimon:{nome:Gazimon,estagio:crianca,mapa:campo,sem_treino:0.579,ic_sem:[0.544,0.613],tipico:0.643,ic_tipico:[0.609,0.675],pior_especie:0.1,por_especie:{brasa:1,cirro:0.1,limo:0.439,ferrugem:0.979},passa:false},Guardro |
| P3 | os 4 desafiantes | cada um: sem treino <= 0,35; tipico >= 0,75 | **nao** | {Tortomon:{nome:Tortomon,estagio:adolescente,mapa:coliseu,sem_treino:0.88,ic_sem:[0.856,0.901],tipico:0.935,ic_tipico:[0.916,0.95],pior_especie:0.675,por_especie:{brasa:0.675,limo:1,ferrugem:1,cirro:1},passa:false},Devid |
| D1 | a duracao | mediana de cada estagio de 15 a 40 s; p90 <= 60 s; nenhuma forma com mediana < 8 s | sim | {por_estagio:{crianca:{mediana_s:20.55,p90_s:26.15,lutas:1600},adolescente:{mediana_s:21.15,p90_s:29.05,lutas:6400},adulto:{mediana_s:17.65,p90_s:26.55,lutas:5195},mega:{mediana_s:17.95,p90_s:26.95,lutas:4800}},formas_cu |
| D2 | sem fim e empate | lutas no limite <= 0,5 %; empates <= 2 % em cada forma | sim | {sem_fim:0,lutas:17995,empate_total:0.005,empate_max_forma:0.02,formas_acima_de_2pc:[]} |
| D3 | a Cidadela cabe | a serie de 3 (pet tipico) no p90 <= 180 s | sim | {p90_s:51.25,mediana_s:42.05} |
