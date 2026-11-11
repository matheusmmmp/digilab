# Resumo das metas, lp5_2, calibracao

commit `516511d93c7c2e6f351f72b18acf82c4cb75ac3a`, candidato `n0030`, 17917 lutas, 24.631 s somados nos processos.

**Passam (2):** D1, D3. **Falham (4):** P1, P2, P3, D2.

| # | a meta | o criterio | passa | os valores (resumo; o inteiro no resumo.json) |
|---|---|---|---|---|
| P1 | o Gazimon | sem treino <= 0,20; tipico >= 0,70; pior especie >= 0,50 | **nao** | {nome:Gazimon,estagio:crianca,mapa:campo,sem_treino:0.528,ic_sem:[0.493,0.562],tipico:0.625,ic_tipico:[0.591,0.658],pior_especie:0.064,por_especie:{brasa:0.996,cirro:0.064,limo:0.436,ferrugem:0.929}} |
| P2 | os 6 lideres | cada um: sem treino <= 0,20; tipico >= 0,70; pior especie >= 0,50 (a Cidadela, a serie de 3) | **nao** | {Gazimon:{nome:Gazimon,estagio:crianca,mapa:campo,sem_treino:0.528,ic_sem:[0.493,0.562],tipico:0.625,ic_tipico:[0.591,0.658],pior_especie:0.064,por_especie:{brasa:0.996,cirro:0.064,limo:0.436,ferrugem:0.929},passa:false} |
| P3 | os 4 desafiantes | cada um: sem treino <= 0,35; tipico >= 0,75 | **nao** | {Tortomon:{nome:Tortomon,estagio:adolescente,mapa:coliseu,sem_treino:0.836,ic_sem:[0.809,0.86],tipico:0.933,ic_tipico:[0.913,0.948],pior_especie:0.663,por_especie:{brasa:0.663,limo:1,ferrugem:1,cirro:1},passa:false},Devi |
| D1 | a duracao | mediana de cada estagio de 15 a 40 s; p90 <= 60 s; nenhuma forma com mediana < 8 s | sim | {por_estagio:{crianca:{mediana_s:19.95,p90_s:26.05,lutas:1600},adolescente:{mediana_s:21.35,p90_s:29.35,lutas:6400},adulto:{mediana_s:17.85,p90_s:27.55,lutas:5117},mega:{mediana_s:18.25,p90_s:27.25,lutas:4800}},formas_cu |
| D2 | sem fim e empate | lutas no limite <= 0,5 %; empates <= 2 % em cada forma | **nao** | {sem_fim:0,lutas:17917,empate_total:0.005,empate_max_forma:0.053,formas_acima_de_2pc:[brasa_crianca_arisco (0.053),cirro_adulto_sentinela (0.027)]} |
| D3 | a Cidadela cabe | a serie de 3 (pet tipico) no p90 <= 180 s | sim | {p90_s:52.65,mediana_s:42.15} |
