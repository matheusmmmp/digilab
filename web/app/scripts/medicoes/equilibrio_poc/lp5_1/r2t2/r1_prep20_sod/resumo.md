# Resumo das metas, lp5_1, calibracao

commit `4336bf43dd6908ef4a994850129527fb6cc11e7e`, candidato `r1_prep20_sod`, 42880 lutas, 180.904 s somados nos processos.

**Passam (2):** D1, A2. **Falham (4):** D2, A1, V1, S1.

| # | a meta | o criterio | passa | os valores (resumo; o inteiro no resumo.json) |
|---|---|---|---|---|
| D1 | a duracao | mediana de cada estagio de 15 a 40 s; p90 <= 60 s; nenhuma forma com mediana < 8 s | sim | {por_estagio:{crianca:{mediana_s:17.75,p90_s:21.85,lutas:2560},adolescente:{mediana_s:17.75,p90_s:21.75,lutas:10240},adulto:{mediana_s:18.85,p90_s:22.35,lutas:10240},mega:{mediana_s:17.95,p90_s:21.85,lutas:10240}},formas |
| D2 | sem fim e empate | lutas no limite <= 0,5 %; empates <= 2 % em cada forma | **nao** | {sem_fim:0,lutas:33280,empate_total:0.048,empate_max_forma:0.169,formas_acima_de_2pc:[brasa_crianca_sereno (0.043),cirro_crianca_sereno (0.023),cirro_crianca_arisco (0.03),limo_crianca_arisco (0.047),brasa_adolescente_br |
| A1 | de longe x de perto | as que atiram contra as de perto: de 0,45 a 0,55 na soma dos 8 mapas; de 0,30 a 0,70 em cada mapa | **nao** | {crianca:{longe:5,perto:3,soma_8_mapas:0.788,por_mapa:{campo:0.82,coliseu:0.76,floresta:0.7,praia:0.813,deserto:0.813,castelo:0.753,caverna:0.853,ringue:0.787}},adolescente:{longe:13,perto:3,soma_8_mapas:0.894,por_mapa:{ |
| A2 | a distancia do tiro | contra quem luta de perto: a mediana da distancia no tiro >= 90 px; <= 15 % dos tiros a 48 px ou menos, em cada estagio (D-LP5-12) | sim | {crianca:{mediana_px:100,ate_48px:0.06,tiros:2450,leitura_contra_quem_atira:{mediana_px:132}},adolescente:{mediana_px:100,ate_48px:0.053,tiros:6331,leitura_contra_quem_atira:{mediana_px:132}},adulto:{mediana_px:96,ate_48 |
| V1 | a variedade no estagio | cada forma contra as outras de 0,35 a 0,65; amplitude <= 0,30; toda forma vence >= 2 outras | **nao** | {crianca:{amplitude:0.629,taxa:{brasa_crianca_sereno:0.48,brasa_crianca_arisco:0.684,cirro_crianca_sereno:0.754,cirro_crianca_arisco:0.705,ferrugem_crianca_sereno:0.125,ferrugem_crianca_arisco:0.271,limo_crianca_sereno:0 |
| S1 | o espelho | o mesmo lutador dos dois lados: o lado A de 0,45 a 0,55 em cada mapa, so nas lutas com vencedor (D-LP5-11) | **nao** | {crianca:{lado_a_com_vencedor:{campo:0.5,coliseu:0.5,floresta:0.543,praia:0.282,deserto:0.371,castelo:0.553,caverna:0.5,ringue:0.588},leitura:{a:0.431,b:0.472,empate:0.097,a_sem_empates:0.478}},adolescente:{lado_a_com_ve |
