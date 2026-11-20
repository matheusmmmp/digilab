# Resumo das metas, lp5_3, calibracao

commit `6b9389a845958f88506823130a2f17ce12cad989`, candidato `t10`, 11261 lutas, 16.611 s somados nos processos.

**Passam (1):** D1. **Falham (5):** D2, G1, G2, G3, G4.

| # | a meta | o criterio | passa | os valores (resumo; o inteiro no resumo.json) |
|---|---|---|---|---|
| D1 | a duracao | mediana de cada estagio de 15 a 40 s; p90 <= 60 s; nenhuma forma com mediana < 8 s | sim | {por_estagio:{crianca:{mediana_s:21.05,p90_s:28.35,lutas:1200},adolescente:{mediana_s:24.05,p90_s:32.25,lutas:1200},adulto:{mediana_s:24.05,p90_s:31.85,lutas:1200},mega:{mediana_s:18.65,p90_s:27.75,lutas:7661}},formas_cu |
| D2 | sem fim e empate | lutas no limite <= 0,5 %; empates <= 2 % em cada forma | **nao** | {sem_fim:0,lutas:11261,empate_total:0.026,empate_max_forma:0.132,formas_acima_de_2pc:[brasa_adulto_furioso (0.028),cirro_adulto_muralha (0.02),ferrugem_adulto_emboscador (0.029),limo_adulto_tita (0.035),cirro_adulto_embo |
| G1 | a Liga | o Mega tipico ganha o titulo em >= 0,25 das tentativas; nenhuma forma acima de 0,85 | **nao** | {titulos:0,max_forma:0,por_forma:{limo_adulto_emboscador:0,brasa_adulto_emboscador:0,limo_adulto_furioso:0,cirro_adulto_muralha:0,limo_adulto_tita:0,limo_adulto_muralha:0,brasa_adulto_tita:0,cirro_adulto_emboscador:0,cir |
| G2 | a Torre de Batalha | recorde mediano de 3 a 30; o teto de 100 em <= 5 % das tentativas | **nao** | {recorde_mediano:2,no_teto:0,recorde_min:1,recorde_max:5} |
| G3 | a Fabrica | uma serie de 3 vencida em >= 0,25 das tentativas | **nao** | {ao_menos_uma_serie:0.003,series:{0:1197,1:3},tentativas:1200} |
| G4 | o Salao | o pet tipico vence o rival do Salao de 0,70 a 0,95 em cada estagio | **nao** | {taxa:{crianca:0.414,adolescente:0.617,adulto:0.753,mega:0.735}} |
