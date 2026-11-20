# Descritivo — o platô de ~1/3: o aprendiz apaga a preferência inata ou aprende qual fruta faz mal?

**PÓS HOC DESCRITIVO, rotulado como tal** (decisão V-3 e pergunta Q-1 de `docs/LEITURA_V2_VALIDACAO_UNICA.md`; tarefa
`docs/TAREFA_V2_DESCRITIVO_PLATO.md`).
- Sem run nova, sem semente nova e sem gate.
- **Nenhuma leitura registrada muda:** nem as predições da validação única nem o M6 da comparação.
- Se algo aqui pedir desenho novo, vira plano próprio.

**Números de** `artifacts_v2_descritivo_plato/` (`validacao_unica.json`, `comparacao.json`, `meta.json`, `run.log`). Script:
`python experiments/descritivo_plato.py` (7 min).

## 1. O que foi feito

**As vidas foram regeneradas da config e do código.** Cada uma foi rejogada do próprio log, bit a bit, e conferida contra as medidas
gravadas: interações, consumos, contagem das frutas e a taxa da fruta ruim em toda janela. Uma divergência faria o script falhar; nenhuma
divergiu.

| fonte | bases | cérebros | vidas |
|---|---|---|---|
| validação única (`artifacts_v2_validacao_unica/frutas/medidas.json`) | 30101…30505, 30 unidades | A | 450 |
| validação da comparação (`artifacts_v2_comparacao_cerebros/validacao/medidas.json`) | 29101…29505, 5 unidades | A e C (P0 comum) | 135 |

**Recorte:** braços P0, P1, P2, P2e e P3 (as vidas fechadas), as três condições e o dono atencioso. A janela é a final (dias 8–14); no
mutável ela é o depois da troca. A janela inicial está nos artefatos.

**A classe da fruta** vem do efeito vigente no tick: boa > 0, neutra = 0, ruim < 0 no humor. A regra foi conferida contra o efeito de
cada consumo. Pelo F6:
- no casado, a ruim é a de **menor** preferência inata;
- no descasado, a ruim é a **preferida** de nascença;
- no mutável, depois da troca, vale a regra do descasado.

**As medidas** são médias sobre as unidades, com IC 95% por bootstrap das unidades:
1. **Consumo por fruta:** a fração de consumos de cada classe.
2. **Escolha com várias:** nas decisões de comer com duas frutas ou mais e a ruim presente, a fração em que a ruim foi a escolhida.
   Duas referências:
   - o **acaso**, 1/k;
   - o **herdado**, a escolha pelo incentivo do genoma, que é o sorteio do instinto.
3. **Comer com uma fruta só:** p(comer) quando a única fruta no cenário é a boa, a neutra ou a ruim, e a diferença "ruim − média das
   outras", por unidade.
4. **Pesos no fim da vida**, desvio do prior, com a classe da fruta no fim:
   - **A:** o peso da escolha de cada fruta e o termo de presença na decisão de comer;
   - **C:** apetitivo e aversivo da célula de identidade (escolha) e, para comer, a soma das células do objeto daquela fruta.

## 2. O cérebro A na validação única (30 unidades, janela final)

| braço/condição | fração boa / neutra / ruim | várias: ruim | ruim − acaso | ruim − herdado | uma só: p(comer) boa / neutra / ruim | ruim − outras |
|---|---|---|---|---|---|---|
| P0 casado | 0,434 / 0,326 / 0,239 | 0,243 | −0,204 [−0,270; −0,139] | −0,051 [−0,106; +0,006] | 0,190 / 0,136 / 0,114 | −0,049 [−0,082; −0,013] |
| P0 descasado | 0,260 / 0,338 / 0,402 | 0,534 | +0,079 [+0,015; +0,142] | −0,063 [−0,124; −0,002] | 0,101 / 0,144 / 0,200 | +0,078 [+0,042; +0,120] |
| P0 mutável | 0,248 / 0,322 / 0,430 | 0,602 | +0,149 [+0,088; +0,207] | +0,001 [−0,055; +0,055] | 0,120 / 0,144 / 0,215 | +0,083 [+0,049; +0,118] |
| P1 casado | 0,345 / 0,336 / 0,319 | 0,039 | −0,418 [−0,433; −0,402] | −0,254 [−0,283; −0,223] | 0,452 / 0,505 / 0,518 | +0,040 [−0,035; +0,118] |
| P1 descasado | 0,338 / 0,336 / 0,326 | 0,107 | −0,349 [−0,376; −0,321] | −0,537 [−0,574; −0,501] | 0,450 / 0,470 / 0,593 | +0,133 [+0,060; +0,211] |
| P1 mutável | 0,333 / 0,337 / 0,330 | 0,244 | −0,212 [−0,248; −0,176] | −0,388 [−0,420; −0,357] | 0,442 / 0,418 / 0,539 | +0,109 [+0,027; +0,188] |
| P2 descasado | 0,338 / 0,339 / 0,323 | 0,033 | −0,424 [−0,437; −0,410] | −0,613 [−0,650; −0,576] | 0,447 / 0,489 / 0,549 | +0,082 [+0,014; +0,151] |
| P2e descasado | 0,339 / 0,341 / 0,320 | 0,021 | −0,437 [−0,449; −0,423] | −0,632 [−0,669; −0,594] | 0,451 / 0,497 / 0,576 | +0,101 [+0,007; +0,197] |
| P3 casado | 0,352 / 0,350 / 0,298 | 0,128 | −0,331 [−0,405; −0,233] | −0,220 [−0,301; −0,126] | 0,198 / 0,194 / 0,180 | −0,016 [−0,069; +0,032] |
| P3 descasado | 0,305 / 0,370 / 0,325 | 0,182 | −0,270 [−0,360; −0,152] | −0,447 [−0,529; −0,348] | 0,190 / 0,186 / 0,218 | +0,030 [−0,019; +0,076] |
| P3 mutável | 0,263 / 0,350 / 0,388 | 0,526 | +0,086 [−0,013; +0,183] | −0,054 [−0,142; +0,034] | 0,167 / 0,179 / 0,215 | +0,042 [−0,005; +0,097] |

P2 e P2e no casado e no mutável seguem o mesmo padrão: na escolha, a ruim sai entre 0,02 e 0,04. As linhas completas estão em
`validacao_unica.json`.

**Pesos no fim, ruim − média das outras** (escala S = 1024):

| braço | condição | escolha da fruta | presença na decisão de comer |
|---|---|---|---|
| P1 | casado | −1529 [−2212; −983] | −368 [−400; −334] |
| P1 | descasado | −7049 [−8314; −5778] | −290 [−318; −264] |
| P1 | mutável | −4136 | +11 [−15; +37] |
| P2 e P2e | casado e descasado | −600 a −1500 | −270 a −370 |
| P2 e P2e | mutável | | ~+20 |
| P3 | casado, descasado e mutável | −7696; −10973; −1909 | 0 (o dono não mexe nesse termo, por desenho) |

**Consumos por vida** (janela final): P0 ~24, P1 e P2 ~42, P3 ~23.

## 3. Os cérebros A e C na validação da comparação (5 unidades, janela final)

O A dessas unidades repete o padrão da seção 2, com ICs mais largos (`comparacao.json`).

| C | fração boa / neutra / ruim | várias: ruim | ruim − acaso | ruim − herdado | uma só: p(comer) boa / neutra / ruim | ruim − outras |
|---|---|---|---|---|---|---|
| P1 casado | 0,332 / 0,359 / 0,309 | 0,274 | −0,176 [−0,261; −0,092] | −0,064 [−0,147; +0,018] | 0,282 / 0,401 / 0,230 | −0,111 [−0,212; −0,040] |
| P1 descasado | 0,323 / 0,343 / 0,334 | 0,556 | +0,109 [+0,015; +0,204] | −0,060 [−0,181; +0,052] | 0,355 / 0,402 / 0,348 | −0,030 [−0,077; +0,034] |
| P1 mutável | 0,295 / 0,346 / 0,359 | 0,652 | +0,204 [−0,032; +0,437] | +0,045 [−0,112; +0,202] | 0,189 / 0,316 / 0,362 | +0,110 [+0,007; +0,213] |
| P2 descasado | 0,350 / 0,333 / 0,317 | 0,111 | −0,345 [−0,410; −0,279] | −0,528 [−0,647; −0,412] | 0,310 / 0,268 / 0,365 | +0,076 [+0,030; +0,117] |
| P2e descasado | 0,302 / 0,339 / 0,359 | 0,772 | +0,320 [+0,136; +0,503] | +0,167 [+0,047; +0,331] | 0,304 / 0,326 / 0,470 | +0,156 [−0,084; +0,418] |
| P3 descasado | 0,183 / 0,383 / 0,433 (2 consumos por vida) | 0,350 | −0,058 [−0,417; +0,417] | −0,202 [−0,408; +0,032] | 0,000 / 0,006 / 0,006 | +0,002 [+0,000; +0,007] |

**Pesos do C no fim, ruim − média das outras:**
- **P1:** comer (líquido) −2081 no casado e −1981 no descasado; escolha (líquido) −530 e −741.
- **P2:** comer −2022 a −2121.
- **P2e:** comer −2061 a −2136; escolha −773 a −844.
- **No mutável a diferença encolhe** (comer −396 a −631), porque os pesos somam as duas fases.

**Consumos por vida:** P1 do C ~36, contra ~42 do A. No P3 do C, 2 a 7 na janela final, contra ~23 do A.

## 4. Leitura curta (descritiva)

**Cérebro A, P1, P2 e P2e: misto.** Não é (a) apagar nem (b) aprender puro.

- **Na escolha entre frutas, (b): o A aprende qual faz mal.**
  - Com a ruim presente entre outras, ele a escolhe em 2% a 11% das vezes; o acaso dá ~46% e o herdado de 29% a 65%.
  - O peso da escolha da ruim fica muito abaixo do das outras.
  - No mutável o P1 reaprende só em parte depois da troca (0,24), e o P2, com a informação, reaprende inteiro (0,03).
- **Com uma fruta só, o A come o que houver.**
  - A ruim é comida tanto quanto as outras, ou mais (+0,08 a +0,15 no descasado e no mutável).
  - Nessas condições a ruim é a preferida de nascença. O P0 já come mais a ruim sozinha (+0,08), e o aprendiz não desfaz isso: a
    decisão de comer só vê o maior incentivo, e o termo de presença aprendido para a ruim é pequeno (−270 a −370 numa escala de 1024;
    ~0 no mutável).
  - Comer dá sinal positivo pela nutrição, então o aprendiz come muito mais fruta (24 → 42 por vida), e mais ainda nas ofertas de uma
    fruta só.
- **O ~1/3 é a soma dos dois.** O que o aprendiz deixa de comer na escolha volta nas ofertas de uma fruta só, que ele come mais (e, no
  descasado, mais a ruim). Por isso a fração por fruta parece "comer por igual" sem que a preferência tenha sido apagada.
  - **No casado** a ruim é a menos preferida. Comer tudo mais vezes sobe a ruim de 0,24 para 0,32: é o que a predição 1 mede ("o P1 come
    mais a fruta ruim que o P0 no casado"), sem que o aprendiz deixe de evitá-la na escolha (0,04).

**Cérebro A, P3:**
- **(b) pela escolha:** a bronca do dono derruba o peso da escolha da ruim (−7700 a −11000).
- **Na decisão de comer, nada:** o dono não mexe no termo de presença.
- **No mutável o P3 não reaprende depois da troca:** a ruim na escolha fica em 0,53, perto do herdado.

**Cérebro C** (5 unidades; ICs largos):
- **P1: o comportamento fica perto do herdado,** embora os pesos mostrem que o C aprendeu a aversão à ruim (comer ~−2000, escolha
  ~−500 a −740).
  - Na escolha, a ruim sai em 0,56 no descasado e 0,65 no mutável, com o herdado em ~0,61; com uma fruta só, não há diferença.
  - O ~1/3 do C vem mais de comer de tudo mais vezes, do lado de (a), do que de aprender qual evitar. Os pesos não chegam a mudar a
    escolha.
- **P2: com a informação certa, a escolha aprende** (ruim 0,11).
- **P2e: com a informação errada, a escolha piora:** a ruim sobe a 0,77–0,83, acima do herdado. O A, na mesma condição, fica em
  0,02–0,04.
- **P3: o C quase para de comer** (p(comer) com uma fruta só ~0 nas três classes), o mesmo que o #197 descreveu: a bronca generaliza para
  comer qualquer fruta.

**O que isso não muda.** As leituras registradas (predições 1 a 5, a separação do cuidado e o M6) ficam como estão. Isto é descrição
pós hoc.

**Pergunta que pode virar plano:** a decisão de comer com uma fruta só não aprende o efeito da fruta o bastante. O termo de presença existe
desde a FRUTA-NO-CENARIO, parte B, mas aprende pouco. Testar isso pede desenho novo, com plano próprio.

## 5. Limites

- **É pós hoc:** as medidas foram escolhidas depois dos resultados, para responder à Q-1.
- **5 unidades na comparação:** as tabelas do C são indicativas.
- **"Uma fruta só" conta toda decisão** com uma fruta no cenário, inclusive com o pet sem fome ou em regra urgente. É p(comer) bruto, sem
  controle de estado.
- **Os pesos do mutável** somam as duas fases e são lidos pela classe do fim.
- Nenhuma alegação de novidade.
