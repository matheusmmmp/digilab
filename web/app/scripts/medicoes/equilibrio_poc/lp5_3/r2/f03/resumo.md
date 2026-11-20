# Resumo das metas, lp5_3, calibracao

commit `d23145062409b8021f7304f44dbd89c716bc2806`, candidato `f03`, 12601 lutas, 13.653 s somados nos processos.

**Passam (2):** D1, G4. **Falham (4):** D2, G1, G2, G3.

| # | a meta | o criterio | passa | os valores (resumo; o inteiro no resumo.json) |
|---|---|---|---|---|
| D1 | a duracao | mediana de cada estagio de 15 a 40 s; p90 <= 60 s; nenhuma forma com mediana < 8 s | sim | {por_estagio:{crianca:{mediana_s:20.45,p90_s:27.25,lutas:1200},adolescente:{mediana_s:22.45,p90_s:27.55,lutas:1200},adulto:{mediana_s:20.75,p90_s:26.05,lutas:1200},mega:{mediana_s:17.95,p90_s:25.35,lutas:9001}},formas_cu |
| D2 | sem fim e empate | lutas no limite <= 0,5 %; empates <= 2 % em cada forma | **nao** | {sem_fim:0,lutas:12601,empate_total:0.007,empate_max_forma:0.03,formas_acima_de_2pc:[cirro_adulto_emboscador (0.021),limo_adolescente_guardiao (0.03)]} |
| G1 | a Liga | o Mega tipico ganha o titulo em >= 0,25 das tentativas; nenhuma forma acima de 0,85 | **nao** | {titulos:0,max_forma:0,por_forma:{limo_adulto_emboscador:0,brasa_adulto_emboscador:0,limo_adulto_furioso:0,cirro_adulto_muralha:0,limo_adulto_tita:0,limo_adulto_muralha:0,brasa_adulto_tita:0,cirro_adulto_emboscador:0,cir |
| G2 | a Torre de Batalha | recorde mediano de 3 a 30; o teto de 100 em <= 5 % das tentativas | **nao** | {recorde_mediano:1,no_teto:0,recorde_min:1,recorde_max:2} |
| G3 | a Fabrica | uma serie de 3 vencida em >= 0,25 das tentativas | **nao** | {ao_menos_uma_serie:0.008,series:{0:1191,1:9},tentativas:1200} |
| G4 | o Salao | o pet tipico vence o rival do Salao de 0,70 a 0,95 em cada estagio | sim | {taxa:{crianca:0.793,adolescente:0.882,adulto:0.947,mega:0.879}} |
