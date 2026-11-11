# Resumo das metas, lp5_3, calibracao

commit `d23145062409b8021f7304f44dbd89c716bc2806`, candidato `f01`, 13243 lutas, 14.031 s somados nos processos.

**Passam (1):** D1. **Falham (5):** D2, G1, G2, G3, G4.

| # | a meta | o criterio | passa | os valores (resumo; o inteiro no resumo.json) |
|---|---|---|---|---|
| D1 | a duracao | mediana de cada estagio de 15 a 40 s; p90 <= 60 s; nenhuma forma com mediana < 8 s | sim | {por_estagio:{crianca:{mediana_s:20.25,p90_s:27.25,lutas:1200},adolescente:{mediana_s:21.15,p90_s:27.95,lutas:1200},adulto:{mediana_s:20.35,p90_s:24.25,lutas:1200},mega:{mediana_s:17.45,p90_s:23.65,lutas:9643}},formas_cu |
| D2 | sem fim e empate | lutas no limite <= 0,5 %; empates <= 2 % em cada forma | **nao** | {sem_fim:0,lutas:13243,empate_total:0.005,empate_max_forma:0.03,formas_acima_de_2pc:[limo_adulto_sentinela (0.03)]} |
| G1 | a Liga | o Mega tipico ganha o titulo em >= 0,25 das tentativas; nenhuma forma acima de 0,85 | **nao** | {titulos:0,max_forma:0,por_forma:{limo_adulto_emboscador:0,brasa_adulto_emboscador:0,limo_adulto_furioso:0,cirro_adulto_muralha:0,limo_adulto_tita:0,limo_adulto_muralha:0,brasa_adulto_tita:0,cirro_adulto_emboscador:0,cir |
| G2 | a Torre de Batalha | recorde mediano de 3 a 30; o teto de 100 em <= 5 % das tentativas | **nao** | {recorde_mediano:1,no_teto:0,recorde_min:1,recorde_max:2} |
| G3 | a Fabrica | uma serie de 3 vencida em >= 0,25 das tentativas | **nao** | {ao_menos_uma_serie:0.024,series:{0:1171,1:28,2:1},tentativas:1200} |
| G4 | o Salao | o pet tipico vence o rival do Salao de 0,70 a 0,95 em cada estagio | **nao** | {taxa:{crianca:0.816,adolescente:0.912,adulto:0.967,mega:0.921}} |
