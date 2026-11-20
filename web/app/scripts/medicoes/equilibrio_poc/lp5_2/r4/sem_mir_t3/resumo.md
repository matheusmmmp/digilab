# Resumo das metas, lp5_2, calibracao

commit `544c2768449b235df05f199f72095c5a45d0ebee+sujo`, candidato `sem_mir_t3`, 27546 lutas, 21.457 s somados nos processos.

**Passam (3):** P1, D1, D3. **Falham (3):** P2, P3, D2.

| # | a meta | o criterio | passa | os valores (resumo; o inteiro no resumo.json) |
|---|---|---|---|---|
| P1 | o Gazimon | sem treino <= 0,41; tipico >= 0,59 (a D-LP5-17); a pior especie so na leitura | sim | {nome:Gazimon,estagio:crianca,mapa:campo,limite_sem:0.41,limite_tipico:0.59,sem_treino:0.373,ic_sem:[0.346,0.4],tipico:0.615,ic_tipico:[0.587,0.642],pior_especie:0.033,por_especie:{brasa:0.868,cirro:0.033,limo:0.476,ferr |
| P2 | os 6 lideres | cada um, no estagio dele: sem treino <= 0,41/0,35/0,30/0,27; tipico >= 0,59/0,65/0,70/0,73 (a D-LP5-17; a Cidadela, a serie de 3) | **nao** | {Gazimon:{nome:Gazimon,estagio:crianca,mapa:campo,limite_sem:0.41,limite_tipico:0.59,sem_treino:0.373,ic_sem:[0.346,0.4],tipico:0.615,ic_tipico:[0.587,0.642],pior_especie:0.033,por_especie:{brasa:0.868,cirro:0.033,limo:0 |
| P3 | os 4 desafiantes | cada um: o limite do lider do estagio, +0,15 no sem treino e +0,05 no tipico (a D-LP5-17) | **nao** | {Tortomon:{nome:Tortomon,estagio:adolescente,mapa:coliseu,limite_sem:0.5,limite_tipico:0.7,sem_treino:0.463,ic_sem:[0.434,0.491],tipico:0.896,ic_tipico:[0.877,0.912],pior_especie:0.607,por_especie:{brasa:0.607,limo:0.994 |
| D1 | a duracao | mediana de cada estagio de 15 a 40 s; p90 <= 60 s; nenhuma forma com mediana < 8 s | sim | {por_estagio:{crianca:{mediana_s:19.65,p90_s:27.95,lutas:2400},adolescente:{mediana_s:21.85,p90_s:28.55,lutas:9600},adulto:{mediana_s:17.15,p90_s:28.05,lutas:8346},mega:{mediana_s:18.45,p90_s:28.15,lutas:7200}},formas_cu |
| D2 | sem fim e empate | lutas no limite <= 0,5 %; empates <= 2 % em cada forma | **nao** | {sem_fim:0,lutas:27546,empate_total:0.013,empate_max_forma:0.09,formas_acima_de_2pc:[brasa_crianca_arisco (0.08),brasa_adolescente_colosso (0.026),npc_tier2_carcereiro (0.033),ferrugem_adolescente_brigao (0.069),limo_ado |
| D3 | a Cidadela cabe | a serie de 3 (pet tipico) no p90 <= 180 s | sim | {p90_s:51.85,mediana_s:43.25} |
