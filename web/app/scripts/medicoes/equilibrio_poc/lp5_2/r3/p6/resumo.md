# Resumo das metas, lp5_2, calibracao

commit `fe04f1b1d1c28282d78bd38677e6daf34bcb1955`, candidato `p6`, 27441 lutas, 37.518 s somados nos processos.

**Passam (3):** P1, D1, D3. **Falham (3):** P2, P3, D2.

| # | a meta | o criterio | passa | os valores (resumo; o inteiro no resumo.json) |
|---|---|---|---|---|
| P1 | o Gazimon | sem treino <= 0,41; tipico >= 0,59 (a D-LP5-17); a pior especie so na leitura | sim | {nome:Gazimon,estagio:crianca,mapa:campo,limite_sem:0.41,limite_tipico:0.59,sem_treino:0.378,ic_sem:[0.351,0.406],tipico:0.608,ic_tipico:[0.58,0.635],pior_especie:0.022,por_especie:{brasa:0.876,cirro:0.022,limo:0.476,fer |
| P2 | os 6 lideres | cada um, no estagio dele: sem treino <= 0,41/0,35/0,30/0,27; tipico >= 0,59/0,65/0,70/0,73 (a D-LP5-17; a Cidadela, a serie de 3) | **nao** | {Gazimon:{nome:Gazimon,estagio:crianca,mapa:campo,limite_sem:0.41,limite_tipico:0.59,sem_treino:0.378,ic_sem:[0.351,0.406],tipico:0.608,ic_tipico:[0.58,0.635],pior_especie:0.022,por_especie:{brasa:0.876,cirro:0.022,limo: |
| P3 | os 4 desafiantes | cada um: o limite do lider do estagio, +0,15 no sem treino e +0,05 no tipico (a D-LP5-17) | **nao** | {Tortomon:{nome:Tortomon,estagio:adolescente,mapa:coliseu,limite_sem:0.5,limite_tipico:0.7,sem_treino:0.357,ic_sem:[0.33,0.384],tipico:0.819,ic_tipico:[0.796,0.84],pior_especie:0.563,por_especie:{brasa:0.563,limo:0.953,f |
| D1 | a duracao | mediana de cada estagio de 15 a 40 s; p90 <= 60 s; nenhuma forma com mediana < 8 s | sim | {por_estagio:{crianca:{mediana_s:19.95,p90_s:28.15,lutas:2400},adolescente:{mediana_s:22.15,p90_s:29.55,lutas:9600},adulto:{mediana_s:17.25,p90_s:28.45,lutas:8241},mega:{mediana_s:18.85,p90_s:30.45,lutas:7200}},formas_cu |
| D2 | sem fim e empate | lutas no limite <= 0,5 %; empates <= 2 % em cada forma | **nao** | {sem_fim:0,lutas:27441,empate_total:0.012,empate_max_forma:0.078,formas_acima_de_2pc:[brasa_crianca_arisco (0.078),brasa_adolescente_colosso (0.028),npc_tier2_carcereiro (0.034),ferrugem_adolescente_brigao (0.054),limo_a |
| D3 | a Cidadela cabe | a serie de 3 (pet tipico) no p90 <= 180 s | sim | {p90_s:51.15,mediana_s:43.15} |
