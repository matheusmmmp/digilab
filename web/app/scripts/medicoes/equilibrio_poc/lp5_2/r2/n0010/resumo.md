# Resumo das metas, lp5_2, calibracao

commit `516511d93c7c2e6f351f72b18acf82c4cb75ac3a`, candidato `n0010`, 18078 lutas, 23.944 s somados nos processos.

**Passam (2):** D1, D3. **Falham (4):** P1, P2, P3, D2.

| # | a meta | o criterio | passa | os valores (resumo; o inteiro no resumo.json) |
|---|---|---|---|---|
| P1 | o Gazimon | sem treino <= 0,20; tipico >= 0,70; pior especie >= 0,50 | **nao** | {nome:Gazimon,estagio:crianca,mapa:campo,sem_treino:0.611,ic_sem:[0.577,0.644],tipico:0.664,ic_tipico:[0.63,0.696],pior_especie:0.157,por_especie:{brasa:1,cirro:0.157,limo:0.461,ferrugem:1}} |
| P2 | os 6 lideres | cada um: sem treino <= 0,20; tipico >= 0,70; pior especie >= 0,50 (a Cidadela, a serie de 3) | **nao** | {Gazimon:{nome:Gazimon,estagio:crianca,mapa:campo,sem_treino:0.611,ic_sem:[0.577,0.644],tipico:0.664,ic_tipico:[0.63,0.696],pior_especie:0.157,por_especie:{brasa:1,cirro:0.157,limo:0.461,ferrugem:1},passa:false},Guardrom |
| P3 | os 4 desafiantes | cada um: sem treino <= 0,35; tipico >= 0,75 | **nao** | {Tortomon:{nome:Tortomon,estagio:adolescente,mapa:coliseu,sem_treino:0.916,ic_sem:[0.895,0.934],tipico:0.94,ic_tipico:[0.921,0.954],pior_especie:0.7,por_especie:{brasa:0.7,limo:1,ferrugem:1,cirro:1},passa:false},Devidram |
| D1 | a duracao | mediana de cada estagio de 15 a 40 s; p90 <= 60 s; nenhuma forma com mediana < 8 s | sim | {por_estagio:{crianca:{mediana_s:20.55,p90_s:25.45,lutas:1600},adolescente:{mediana_s:20.85,p90_s:28.75,lutas:6400},adulto:{mediana_s:17.35,p90_s:25.45,lutas:5278},mega:{mediana_s:17.65,p90_s:26.25,lutas:4800}},formas_cu |
| D2 | sem fim e empate | lutas no limite <= 0,5 %; empates <= 2 % em cada forma | **nao** | {sem_fim:0,lutas:18078,empate_total:0.002,empate_max_forma:0.025,formas_acima_de_2pc:[brasa_adulto_muralha (0.025)]} |
| D3 | a Cidadela cabe | a serie de 3 (pet tipico) no p90 <= 180 s | sim | {p90_s:50.85,mediana_s:42.55} |
