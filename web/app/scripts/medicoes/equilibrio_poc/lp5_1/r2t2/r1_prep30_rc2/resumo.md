# Resumo das metas, lp5_1, calibracao

commit `4336bf43dd6908ef4a994850129527fb6cc11e7e`, candidato `r1_prep30_rc2`, 42880 lutas, 270.371 s somados nos processos.

**Passam (2):** D1, A2. **Falham (4):** D2, A1, V1, S1.

| # | a meta | o criterio | passa | os valores (resumo; o inteiro no resumo.json) |
|---|---|---|---|---|
| D1 | a duracao | mediana de cada estagio de 15 a 40 s; p90 <= 60 s; nenhuma forma com mediana < 8 s | sim | {por_estagio:{crianca:{mediana_s:19.45,p90_s:28.25,lutas:2560},adolescente:{mediana_s:18.85,p90_s:26.55,lutas:10240},adulto:{mediana_s:19.55,p90_s:28.05,lutas:10240},mega:{mediana_s:19.15,p90_s:27.75,lutas:10240}},formas |
| D2 | sem fim e empate | lutas no limite <= 0,5 %; empates <= 2 % em cada forma | **nao** | {sem_fim:0,lutas:33280,empate_total:0.053,empate_max_forma:0.177,formas_acima_de_2pc:[brasa_crianca_sereno (0.06),cirro_crianca_sereno (0.027),cirro_crianca_arisco (0.027),limo_crianca_arisco (0.063),brasa_adolescente_br |
| A1 | de longe x de perto | as que atiram contra as de perto: de 0,45 a 0,55 na soma dos 8 mapas; de 0,30 a 0,70 em cada mapa | **nao** | {crianca:{longe:5,perto:3,soma_8_mapas:0.706,por_mapa:{campo:0.753,coliseu:0.78,floresta:0.587,praia:0.84,deserto:0.88,castelo:0.713,caverna:0.833,ringue:0.26}},adolescente:{longe:13,perto:3,soma_8_mapas:0.797,por_mapa:{ |
| A2 | a distancia do tiro | contra quem luta de perto: a mediana da distancia no tiro >= 90 px; <= 15 % dos tiros a 48 px ou menos, em cada estagio (D-LP5-12) | sim | {crianca:{mediana_px:132,ate_48px:0.02,tiros:2316,leitura_contra_quem_atira:{mediana_px:136}},adolescente:{mediana_px:132,ate_48px:0.02,tiros:6024,leitura_contra_quem_atira:{mediana_px:136}},adulto:{mediana_px:132,ate_48 |
| V1 | a variedade no estagio | cada forma contra as outras de 0,35 a 0,65; amplitude <= 0,30; toda forma vence >= 2 outras | **nao** | {crianca:{amplitude:0.493,taxa:{brasa_crianca_sereno:0.445,brasa_crianca_arisco:0.643,cirro_crianca_sereno:0.695,cirro_crianca_arisco:0.668,ferrugem_crianca_sereno:0.202,ferrugem_crianca_arisco:0.341,limo_crianca_sereno: |
| S1 | o espelho | o mesmo lutador dos dois lados: o lado A de 0,45 a 0,55 em cada mapa, so nas lutas com vencedor (D-LP5-11) | **nao** | {crianca:{lado_a_com_vencedor:{campo:0.618,coliseu:0.647,floresta:0.618,praia:0.375,deserto:0.424,castelo:0.641,caverna:0.675,ringue:0.515},leitura:{a:0.506,b:0.391,empate:0.103,a_sem_empates:0.564}},adolescente:{lado_a_ |
