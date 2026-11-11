# Resumo das metas, lp5_3, calibracao

commit `d23145062409b8021f7304f44dbd89c716bc2806`, candidato `f08`, 11961 lutas, 12.722 s somados nos processos.

**Passam (2):** D1, G4. **Falham (4):** D2, G1, G2, G3.

| # | a meta | o criterio | passa | os valores (resumo; o inteiro no resumo.json) |
|---|---|---|---|---|
| D1 | a duracao | mediana de cada estagio de 15 a 40 s; p90 <= 60 s; nenhuma forma com mediana < 8 s | sim | {por_estagio:{crianca:{mediana_s:20.35,p90_s:28.25,lutas:1200},adolescente:{mediana_s:22.95,p90_s:28.15,lutas:1200},adulto:{mediana_s:22.25,p90_s:28.15,lutas:1200},mega:{mediana_s:18.95,p90_s:27.35,lutas:8361}},formas_cu |
| D2 | sem fim e empate | lutas no limite <= 0,5 %; empates <= 2 % em cada forma | **nao** | {sem_fim:0,lutas:11961,empate_total:0.011,empate_max_forma:0.042,formas_acima_de_2pc:[limo_adulto_tita (0.023),cirro_adulto_emboscador (0.042),ferrugem_adulto_furioso (0.037),cirro_adulto_tita (0.03),ferrugem_adulto_mura |
| G1 | a Liga | o Mega tipico ganha o titulo em >= 0,25 das tentativas; nenhuma forma acima de 0,85 | **nao** | {titulos:0,max_forma:0,por_forma:{limo_adulto_emboscador:0,brasa_adulto_emboscador:0,limo_adulto_furioso:0,cirro_adulto_muralha:0,limo_adulto_tita:0,limo_adulto_muralha:0,brasa_adulto_tita:0,cirro_adulto_emboscador:0,cir |
| G2 | a Torre de Batalha | recorde mediano de 3 a 30; o teto de 100 em <= 5 % das tentativas | **nao** | {recorde_mediano:1,no_teto:0,recorde_min:1,recorde_max:2} |
| G3 | a Fabrica | uma serie de 3 vencida em >= 0,25 das tentativas | **nao** | {ao_menos_uma_serie:0.003,series:{0:1196,1:4},tentativas:1200} |
| G4 | o Salao | o pet tipico vence o rival do Salao de 0,70 a 0,95 em cada estagio | sim | {taxa:{crianca:0.737,adolescente:0.853,adulto:0.935,mega:0.846}} |
