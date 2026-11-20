# Resumo das metas, lp5_1, calibracao

commit `4336bf43dd6908ef4a994850129527fb6cc11e7e`, candidato `r1_prep12`, 42880 lutas, 248.849 s somados nos processos.

**Passam (1):** D1. **Falham (5):** D2, A1, A2, V1, S1.

| # | a meta | o criterio | passa | os valores (resumo; o inteiro no resumo.json) |
|---|---|---|---|---|
| D1 | a duracao | mediana de cada estagio de 15 a 40 s; p90 <= 60 s; nenhuma forma com mediana < 8 s | sim | {por_estagio:{crianca:{mediana_s:18.45,p90_s:22.05,lutas:2560},adolescente:{mediana_s:18.35,p90_s:22.05,lutas:10240},adulto:{mediana_s:19.05,p90_s:22.55,lutas:10240},mega:{mediana_s:18.25,p90_s:21.95,lutas:10240}},formas |
| D2 | sem fim e empate | lutas no limite <= 0,5 %; empates <= 2 % em cada forma | **nao** | {sem_fim:0,lutas:33280,empate_total:0.048,empate_max_forma:0.167,formas_acima_de_2pc:[brasa_crianca_sereno (0.045),cirro_crianca_sereno (0.027),cirro_crianca_arisco (0.035),limo_crianca_arisco (0.045),brasa_adolescente_b |
| A1 | de longe x de perto | as que atiram contra as de perto: de 0,45 a 0,55 na soma dos 8 mapas; de 0,30 a 0,70 em cada mapa | **nao** | {crianca:{longe:5,perto:3,soma_8_mapas:0.688,por_mapa:{campo:0.813,coliseu:0.633,floresta:0.66,praia:0.8,deserto:0.767,castelo:0.66,caverna:0.82,ringue:0.353}},adolescente:{longe:13,perto:3,soma_8_mapas:0.793,por_mapa:{c |
| A2 | a distancia do tiro | contra quem luta de perto: a mediana da distancia no tiro >= 90 px; <= 15 % dos tiros a 48 px ou menos, em cada estagio (D-LP5-12) | **nao** | {crianca:{mediana_px:88,ate_48px:0.104,tiros:2251,leitura_contra_quem_atira:{mediana_px:132}},adolescente:{mediana_px:88,ate_48px:0.107,tiros:5849,leitura_contra_quem_atira:{mediana_px:132}},adulto:{mediana_px:84,ate_48p |
| V1 | a variedade no estagio | cada forma contra as outras de 0,35 a 0,65; amplitude <= 0,30; toda forma vence >= 2 outras | **nao** | {crianca:{amplitude:0.504,taxa:{brasa_crianca_sereno:0.455,brasa_crianca_arisco:0.659,cirro_crianca_sereno:0.7,cirro_crianca_arisco:0.65,ferrugem_crianca_sereno:0.196,ferrugem_crianca_arisco:0.368,limo_crianca_sereno:0.5 |
| S1 | o espelho | o mesmo lutador dos dois lados: o lado A de 0,45 a 0,55 em cada mapa, so nas lutas com vencedor (D-LP5-11) | **nao** | {crianca:{lado_a_com_vencedor:{campo:0.471,coliseu:0.471,floresta:0.514,praia:0.325,deserto:0.371,castelo:0.59,caverna:0.6,ringue:0.588},leitura:{a:0.447,b:0.463,empate:0.091,a_sem_empates:0.491}},adolescente:{lado_a_com |
