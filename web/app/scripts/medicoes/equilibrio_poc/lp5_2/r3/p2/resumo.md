# Resumo das metas, lp5_2, calibracao

commit `fe04f1b1d1c28282d78bd38677e6daf34bcb1955`, candidato `p2`, 27718 lutas, 37.581 s somados nos processos.

**Passam (2):** D1, D3. **Falham (4):** P1, P2, P3, D2.

| # | a meta | o criterio | passa | os valores (resumo; o inteiro no resumo.json) |
|---|---|---|---|---|
| P1 | o Gazimon | sem treino <= 0,41; tipico >= 0,59 (a D-LP5-17); a pior especie so na leitura | **nao** | {nome:Gazimon,estagio:crianca,mapa:campo,limite_sem:0.41,limite_tipico:0.59,sem_treino:0.429,ic_sem:[0.401,0.457],tipico:0.64,ic_tipico:[0.612,0.667],pior_especie:0.028,por_especie:{brasa:0.974,cirro:0.028,limo:0.476,fer |
| P2 | os 6 lideres | cada um, no estagio dele: sem treino <= 0,41/0,35/0,30/0,27; tipico >= 0,59/0,65/0,70/0,73 (a D-LP5-17; a Cidadela, a serie de 3) | **nao** | {Gazimon:{nome:Gazimon,estagio:crianca,mapa:campo,limite_sem:0.41,limite_tipico:0.59,sem_treino:0.429,ic_sem:[0.401,0.457],tipico:0.64,ic_tipico:[0.612,0.667],pior_especie:0.028,por_especie:{brasa:0.974,cirro:0.028,limo: |
| P3 | os 4 desafiantes | cada um: o limite do lider do estagio, +0,15 no sem treino e +0,05 no tipico (a D-LP5-17) | **nao** | {Tortomon:{nome:Tortomon,estagio:adolescente,mapa:coliseu,limite_sem:0.5,limite_tipico:0.7,sem_treino:0.468,ic_sem:[0.439,0.496],tipico:0.899,ic_tipico:[0.881,0.915],pior_especie:0.603,por_especie:{brasa:0.603,limo:1,fer |
| D1 | a duracao | mediana de cada estagio de 15 a 40 s; p90 <= 60 s; nenhuma forma com mediana < 8 s | sim | {por_estagio:{crianca:{mediana_s:19.85,p90_s:27.75,lutas:2400},adolescente:{mediana_s:22.15,p90_s:28.95,lutas:9600},adulto:{mediana_s:16.25,p90_s:27.95,lutas:8518},mega:{mediana_s:17.45,p90_s:27.75,lutas:7200}},formas_cu |
| D2 | sem fim e empate | lutas no limite <= 0,5 %; empates <= 2 % em cada forma | **nao** | {sem_fim:0,lutas:27718,empate_total:0.01,empate_max_forma:0.066,formas_acima_de_2pc:[brasa_crianca_arisco (0.03),ferrugem_adolescente_brigao (0.021),limo_adolescente_colosso (0.033),brasa_adolescente_brigao (0.034),ferru |
| D3 | a Cidadela cabe | a serie de 3 (pet tipico) no p90 <= 180 s | sim | {p90_s:51.65,mediana_s:42.55} |
