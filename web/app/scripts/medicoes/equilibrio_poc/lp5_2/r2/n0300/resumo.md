# Resumo das metas, lp5_2, calibracao

commit `516511d93c7c2e6f351f72b18acf82c4cb75ac3a`, candidato `n0300`, 17369 lutas, 25.924 s somados nos processos.

**Passam (2):** D1, D3. **Falham (4):** P1, P2, P3, D2.

| # | a meta | o criterio | passa | os valores (resumo; o inteiro no resumo.json) |
|---|---|---|---|---|
| P1 | o Gazimon | sem treino <= 0,20; tipico >= 0,70; pior especie >= 0,50 | **nao** | {nome:Gazimon,estagio:crianca,mapa:campo,sem_treino:0.249,ic_sem:[0.22,0.28],tipico:0.383,ic_tipico:[0.349,0.417],pior_especie:0,por_especie:{brasa:0.504,cirro:0,limo:0.429,ferrugem:0.464}} |
| P2 | os 6 lideres | cada um: sem treino <= 0,20; tipico >= 0,70; pior especie >= 0,50 (a Cidadela, a serie de 3) | **nao** | {Gazimon:{nome:Gazimon,estagio:crianca,mapa:campo,sem_treino:0.249,ic_sem:[0.22,0.28],tipico:0.383,ic_tipico:[0.349,0.417],pior_especie:0,por_especie:{brasa:0.504,cirro:0,limo:0.429,ferrugem:0.464},passa:false},Guardromo |
| P3 | os 4 desafiantes | cada um: sem treino <= 0,35; tipico >= 0,75 | **nao** | {Tortomon:{nome:Tortomon,estagio:adolescente,mapa:coliseu,sem_treino:0.309,ic_sem:[0.278,0.342],tipico:0.765,ic_tipico:[0.734,0.793],pior_especie:0.506,por_especie:{brasa:0.506,limo:0.917,ferrugem:0.74,cirro:0.771},passa |
| D1 | a duracao | mediana de cada estagio de 15 a 40 s; p90 <= 60 s; nenhuma forma com mediana < 8 s | sim | {por_estagio:{crianca:{mediana_s:20.35,p90_s:28.85,lutas:1600},adolescente:{mediana_s:22.05,p90_s:29.55,lutas:6400},adulto:{mediana_s:18.95,p90_s:30.95,lutas:4569},mega:{mediana_s:21.15,p90_s:33.15,lutas:4800}},formas_cu |
| D2 | sem fim e empate | lutas no limite <= 0,5 %; empates <= 2 % em cada forma | **nao** | {sem_fim:0,lutas:17369,empate_total:0.009,empate_max_forma:0.06,formas_acima_de_2pc:[brasa_crianca_arisco (0.022),brasa_adolescente_colosso (0.04),npc_tier2_carcereiro (0.028),ferrugem_adolescente_brigao (0.034),brasa_ad |
| D3 | a Cidadela cabe | a serie de 3 (pet tipico) no p90 <= 180 s | sim | {p90_s:58.05,mediana_s:38.75} |
