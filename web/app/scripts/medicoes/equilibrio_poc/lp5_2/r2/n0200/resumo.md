# Resumo das metas, lp5_2, calibracao

commit `516511d93c7c2e6f351f72b18acf82c4cb75ac3a`, candidato `n0200`, 17459 lutas, 26.203 s somados nos processos.

**Passam (2):** D1, D3. **Falham (4):** P1, P2, P3, D2.

| # | a meta | o criterio | passa | os valores (resumo; o inteiro no resumo.json) |
|---|---|---|---|---|
| P1 | o Gazimon | sem treino <= 0,20; tipico >= 0,70; pior especie >= 0,50 | **nao** | {nome:Gazimon,estagio:crianca,mapa:campo,sem_treino:0.264,ic_sem:[0.234,0.295],tipico:0.434,ic_tipico:[0.4,0.468],pior_especie:0.014,por_especie:{brasa:0.608,cirro:0.014,limo:0.429,ferrugem:0.564}} |
| P2 | os 6 lideres | cada um: sem treino <= 0,20; tipico >= 0,70; pior especie >= 0,50 (a Cidadela, a serie de 3) | **nao** | {Gazimon:{nome:Gazimon,estagio:crianca,mapa:campo,sem_treino:0.264,ic_sem:[0.234,0.295],tipico:0.434,ic_tipico:[0.4,0.468],pior_especie:0.014,por_especie:{brasa:0.608,cirro:0.014,limo:0.429,ferrugem:0.564},passa:false},G |
| P3 | os 4 desafiantes | cada um: sem treino <= 0,35; tipico >= 0,75 | **nao** | {Tortomon:{nome:Tortomon,estagio:adolescente,mapa:coliseu,sem_treino:0.384,ic_sem:[0.351,0.418],tipico:0.82,ic_tipico:[0.792,0.845],pior_especie:0.594,por_especie:{brasa:0.594,limo:0.92,ferrugem:0.86,cirro:0.807},passa:f |
| D1 | a duracao | mediana de cada estagio de 15 a 40 s; p90 <= 60 s; nenhuma forma com mediana < 8 s | sim | {por_estagio:{crianca:{mediana_s:20.15,p90_s:28.55,lutas:1600},adolescente:{mediana_s:20.85,p90_s:29.05,lutas:6400},adulto:{mediana_s:18.95,p90_s:30.45,lutas:4659},mega:{mediana_s:20.25,p90_s:30.15,lutas:4800}},formas_cu |
| D2 | sem fim e empate | lutas no limite <= 0,5 %; empates <= 2 % em cada forma | **nao** | {sem_fim:0,lutas:17459,empate_total:0.007,empate_max_forma:0.047,formas_acima_de_2pc:[cirro_adolescente_cacador (0.033),cirro_adulto_sentinela (0.047),ferrugem_adulto_sentinela (0.021),cirro_adulto_emboscador (0.028),npc |
| D3 | a Cidadela cabe | a serie de 3 (pet tipico) no p90 <= 180 s | sim | {p90_s:57.25,mediana_s:39.35} |
