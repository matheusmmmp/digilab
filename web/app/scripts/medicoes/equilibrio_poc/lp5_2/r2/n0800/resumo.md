# Resumo das metas, lp5_2, calibracao

commit `516511d93c7c2e6f351f72b18acf82c4cb75ac3a`, candidato `n0800`, 17161 lutas, 24.37 s somados nos processos.

**Passam (2):** D1, D3. **Falham (4):** P1, P2, P3, D2.

| # | a meta | o criterio | passa | os valores (resumo; o inteiro no resumo.json) |
|---|---|---|---|---|
| P1 | o Gazimon | sem treino <= 0,20; tipico >= 0,70; pior especie >= 0,50 | **nao** | {nome:Gazimon,estagio:crianca,mapa:campo,sem_treino:0.209,ic_sem:[0.182,0.238],tipico:0.316,ic_tipico:[0.285,0.349],pior_especie:0,por_especie:{brasa:0.367,cirro:0,limo:0.429,ferrugem:0.321}} |
| P2 | os 6 lideres | cada um: sem treino <= 0,20; tipico >= 0,70; pior especie >= 0,50 (a Cidadela, a serie de 3) | **nao** | {Gazimon:{nome:Gazimon,estagio:crianca,mapa:campo,sem_treino:0.209,ic_sem:[0.182,0.238],tipico:0.316,ic_tipico:[0.285,0.349],pior_especie:0,por_especie:{brasa:0.367,cirro:0,limo:0.429,ferrugem:0.321},passa:false},Guardro |
| P3 | os 4 desafiantes | cada um: sem treino <= 0,35; tipico >= 0,75 | **nao** | {Tortomon:{nome:Tortomon,estagio:adolescente,mapa:coliseu,sem_treino:0.258,ic_sem:[0.228,0.289],tipico:0.478,ic_tipico:[0.443,0.512],pior_especie:0.193,por_especie:{brasa:0.419,limo:0.797,ferrugem:0.245,cirro:0.193},pass |
| D1 | a duracao | mediana de cada estagio de 15 a 40 s; p90 <= 60 s; nenhuma forma com mediana < 8 s | sim | {por_estagio:{crianca:{mediana_s:21.95,p90_s:30.05,lutas:1600},adolescente:{mediana_s:22.55,p90_s:30.55,lutas:6400},adulto:{mediana_s:18.95,p90_s:30.55,lutas:4361},mega:{mediana_s:21.95,p90_s:34.25,lutas:4800}},formas_cu |
| D2 | sem fim e empate | lutas no limite <= 0,5 %; empates <= 2 % em cada forma | **nao** | {sem_fim:0,lutas:17161,empate_total:0.011,empate_max_forma:0.067,formas_acima_de_2pc:[limo_adolescente_cacador (0.02),limo_adolescente_colosso (0.025),ferrugem_adolescente_cacador (0.025),cirro_adolescente_guardiao (0.02 |
| D3 | a Cidadela cabe | a serie de 3 (pet tipico) no p90 <= 180 s | sim | {p90_s:56.25,mediana_s:37.35} |
