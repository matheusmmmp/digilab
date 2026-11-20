# Resumo das metas, lp5_2, calibracao

commit `5e3c01f0c113fb6379b018aeea206458fd65df65`, candidato `n080`, 17782 lutas, 23.762 s somados nos processos.

**Passam (2):** D1, D3. **Falham (4):** P1, P2, P3, D2.

| # | a meta | o criterio | passa | os valores (resumo; o inteiro no resumo.json) |
|---|---|---|---|---|
| P1 | o Gazimon | sem treino <= 0,20; tipico >= 0,70; pior especie >= 0,50 | **nao** | {nome:Gazimon,estagio:crianca,mapa:campo,sem_treino:0.353,ic_sem:[0.32,0.386],tipico:0.576,ic_tipico:[0.542,0.61],pior_especie:0.029,por_especie:{brasa:0.85,cirro:0.029,limo:0.429,ferrugem:0.95}} |
| P2 | os 6 lideres | cada um: sem treino <= 0,20; tipico >= 0,70; pior especie >= 0,50 (a Cidadela, a serie de 3) | **nao** | {Gazimon:{nome:Gazimon,estagio:crianca,mapa:campo,sem_treino:0.353,ic_sem:[0.32,0.386],tipico:0.576,ic_tipico:[0.542,0.61],pior_especie:0.029,por_especie:{brasa:0.85,cirro:0.029,limo:0.429,ferrugem:0.95},passa:false},Gua |
| P3 | os 4 desafiantes | cada um: sem treino <= 0,35; tipico >= 0,75 | **nao** | {Tortomon:{nome:Tortomon,estagio:adolescente,mapa:coliseu,sem_treino:0.54,ic_sem:[0.505,0.574],tipico:0.929,ic_tipico:[0.909,0.945],pior_especie:0.644,por_especie:{brasa:0.644,limo:1,ferrugem:1,cirro:1},passa:false},Devi |
| D1 | a duracao | mediana de cada estagio de 15 a 40 s; p90 <= 60 s; nenhuma forma com mediana < 8 s | sim | {por_estagio:{crianca:{mediana_s:19.55,p90_s:27.45,lutas:1600},adolescente:{mediana_s:20.85,p90_s:28.75,lutas:6400},adulto:{mediana_s:18.75,p90_s:28.15,lutas:4982},mega:{mediana_s:18.85,p90_s:27.75,lutas:4800}},formas_cu |
| D2 | sem fim e empate | lutas no limite <= 0,5 %; empates <= 2 % em cada forma | **nao** | {sem_fim:0,lutas:17782,empate_total:0.014,empate_max_forma:0.09,formas_acima_de_2pc:[brasa_crianca_arisco (0.084),ferrugem_adolescente_brigao (0.053),limo_adolescente_colosso (0.031),brasa_adolescente_guardiao (0.021),fe |
| D3 | a Cidadela cabe | a serie de 3 (pet tipico) no p90 <= 180 s | sim | {p90_s:54.35,mediana_s:42.15} |
