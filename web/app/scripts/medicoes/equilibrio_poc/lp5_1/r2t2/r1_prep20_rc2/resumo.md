# Resumo das metas, lp5_1, calibracao

commit `4336bf43dd6908ef4a994850129527fb6cc11e7e`, candidato `r1_prep20_rc2`, 42880 lutas, 250.866 s somados nos processos.

**Passam (2):** D1, A2. **Falham (4):** D2, A1, V1, S1.

| # | a meta | o criterio | passa | os valores (resumo; o inteiro no resumo.json) |
|---|---|---|---|---|
| D1 | a duracao | mediana de cada estagio de 15 a 40 s; p90 <= 60 s; nenhuma forma com mediana < 8 s | sim | {por_estagio:{crianca:{mediana_s:19.25,p90_s:24.25,lutas:2560},adolescente:{mediana_s:18.95,p90_s:23.15,lutas:10240},adulto:{mediana_s:19.55,p90_s:24.55,lutas:10240},mega:{mediana_s:19.05,p90_s:23.95,lutas:10240}},formas |
| D2 | sem fim e empate | lutas no limite <= 0,5 %; empates <= 2 % em cada forma | **nao** | {sem_fim:0,lutas:33280,empate_total:0.049,empate_max_forma:0.16,formas_acima_de_2pc:[brasa_crianca_sereno (0.047),cirro_crianca_sereno (0.027),cirro_crianca_arisco (0.027),limo_crianca_arisco (0.052),brasa_adolescente_br |
| A1 | de longe x de perto | as que atiram contra as de perto: de 0,45 a 0,55 na soma dos 8 mapas; de 0,30 a 0,70 em cada mapa | **nao** | {crianca:{longe:5,perto:3,soma_8_mapas:0.775,por_mapa:{campo:0.88,coliseu:0.847,floresta:0.76,praia:0.893,deserto:0.887,castelo:0.747,caverna:0.853,ringue:0.333}},adolescente:{longe:13,perto:3,soma_8_mapas:0.86,por_mapa: |
| A2 | a distancia do tiro | contra quem luta de perto: a mediana da distancia no tiro >= 90 px; <= 15 % dos tiros a 48 px ou menos, em cada estagio (D-LP5-12) | sim | {crianca:{mediana_px:116,ate_48px:0.052,tiros:2316,leitura_contra_quem_atira:{mediana_px:132}},adolescente:{mediana_px:116,ate_48px:0.051,tiros:5937,leitura_contra_quem_atira:{mediana_px:132}},adulto:{mediana_px:116,ate_ |
| V1 | a variedade no estagio | cada forma contra as outras de 0,35 a 0,65; amplitude <= 0,30; toda forma vence >= 2 outras | **nao** | {crianca:{amplitude:0.582,taxa:{brasa_crianca_sereno:0.471,brasa_crianca_arisco:0.657,cirro_crianca_sereno:0.743,cirro_crianca_arisco:0.698,ferrugem_crianca_sereno:0.161,ferrugem_crianca_arisco:0.271,limo_crianca_sereno: |
| S1 | o espelho | o mesmo lutador dos dois lados: o lado A de 0,45 a 0,55 em cada mapa, so nas lutas com vencedor (D-LP5-11) | **nao** | {crianca:{lado_a_com_vencedor:{campo:0.486,coliseu:0.486,floresta:0.471,praia:0.275,deserto:0.382,castelo:0.622,caverna:0.625,ringue:0.545},leitura:{a:0.438,b:0.463,empate:0.1,a_sem_empates:0.486}},adolescente:{lado_a_co |
