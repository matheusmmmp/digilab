# PLANO DE ANÁLISE V3 — INDIVIDUALIDADE, I5: o hábito como trejeito (2026-11-09, Claude Code, Opus 5.5)

**Status: PROPOSTO.** As decisões IH-1 a IH-7 (seção 10) esperam o Matheus. **Nenhuma conta do I5 roda antes de quatro coisas:**
1. este cabeçalho com a marca "APROVADO pelo Matheus";
2. o código do I5a na `main` (seção 8): as medidas em `digilab/metrics.py` com os testes delas e o orquestrador
   `experiments/run_v3_individualidade_i5.py` com a trava;
3. a fumaça do orquestrador com as sementes dos testes (101…505);
4. o registro da análise (seção 9), num commit empurrado antes da primeira vida rejogada.

**De onde vem:** o I5 da `docs/futuro/individualidade_pet.md` (seção 5) e a `docs/TAREFA_V3_INDIVIDUALIDADE.md`.
- **A ordem:** o Matheus escolheu o I5 como a etapa seguinte em 2026-11-09 (D-IND-I2c-1), porque ele não depende do Gate I.
- **A regra da IN-7 e da D-C2-4-2:** o hábito entra só como medida. Nenhum mecanismo novo no P2.

**Este plano é descritivo.** Não há gate nem contraste que decida. Ele mede se cada pet repete, de um dia para o outro, sequências, lugares
e horários próprios, acima do que o dono e o mundo da semente explicam.

**O que este plano não afirma:** que o pet "tem hábitos" no sentido da psicologia, que a medida é um trejeito, nem que o modular supera o A.
"Hábito" é o nome da medida. **Nenhuma alegação de novidade.** As contas abaixo são SEM FONTE como escolha deste plano.

## 0. O que existe hoje (os fatos que o desenho usa)

- **As vidas do I2** (#718), em `artifacts_v3_individualidade/vidas.tar.gz`:
  - o log de cada uma das 480 vidas (REL e REL+F × 4 donos × 60 sementes da faixa 85101…85505), 14 dias no `comedouro`;
  - cada vida já passou pelo G1, o replay do disco igual à vida.
- **O registro de cada decisão no motor:** o `MotorMundo` grava em `decisoes_mundo` (`digilab/mundo.py`) o tick, a ação, a posição
  (`x`, `y`) e a região (casa, jardim, campo, mata) de cada decisão. O replay do log refaz o motor e, com ele, essa lista. Nada no
  `engine.py`, no cérebro nem no motor muda.
- **O ritmo:** uma decisão a cada 15 ticks (`intervalo_decisao_ticks`), 96 por dia (`TICKS_POR_DIA` = 1440).
  - As ações são oito: `ocioso`, `dormir`, `comer`, `brincar`, `chamar_atencao`, `explorar`, `emburrar` e `aliviar`.
  - O mapa tem 64 × 30 células de 16 subunidades.
- **Os donos:** o atencioso, o relapso e o aleatório (D-IND-I2c-2). O incoerente sai, porque no `comedouro` as vidas dele são as do
  atencioso (D-IND-I2b-1).
- **O pareamento do I2:** a mesma semente dá o mesmo ambiente e a mesma rng de política de partida, nos três donos e nos dois braços.
- **O que já se sabe do I2:** o R_pet dos traços das sondas é baixo (0,02 a 0,28), e o η² do dono é alto
  (`docs/RESULTADO_V3_INDIVIDUALIDADE.md`). O I5 não lê as sondas; ele lê a vida real.

## 1. A pergunta, escrita antes

**Q-I5: com o genoma vazio, cada pet do modular repete de um dia para o outro sequências, lugares e horários próprios, mais parecidos
com os dele mesmo em outro dia do que com os de outro pet no mesmo dia, com o mesmo dono ou no mesmo mundo?**

As expectativas não são previsões com gate. Ficam escritas para a leitura não se ajustar ao resultado:
- **E1:** o lugar tem hábito além do dono (o H_dono do LUGAR é positivo). A memória de lugar e as comidas achadas puxam cada pet para os
  cantos dele.
- **E2:** o mundo da semente explica parte do lugar. O H_mundo do LUGAR é menor que o H_dono, porque o mesmo mundo põe as frutas nos
  mesmos pontos.
- **E3:** a sequência quase não tem hábito (o H_dono da SEQ perto de 0). As sequências vêm do corpo e do relógio, iguais para todos.

## 2. O desenho

- **Os dados (IH-1):** as vidas do I2, rejogadas do log. Nenhuma vida nova, nenhuma semente nova.
- **Os pets:** 2 braços × 3 donos × 60 sementes = 360. Um "pet" é a tripla (braço, dono, semente), como no I2.
- **As decisões que entram:** as acordadas (ação diferente de `dormir`). Um dia com menos de 16 decisões acordadas fica fora daquele pet
  e é contado à parte.
- **A janela (IH-5):** os dias 8 a 14 são a primária (`JANELA_8_14`). Os dias 1 a 7 entram só no descritivo, para ver se a medida cresce
  com a vida.

## 3. Os perfis (por pet p e dia d; IH-3)

| perfil | as caixas | o que conta |
|---|---|---|
| **SEQ** | os pares (aₜ, aₜ₊₁) das sete ações acordadas: 49 caixas | cada par de decisões acordadas seguidas do dia |
| **LUGAR** | os blocos de 4 × 4 células: 16 × 8 = 128 caixas | o bloco do pet em cada decisão acordada |
| **HORA** | a faixa de 2 h × a ação acordada: 12 × 7 = 84 caixas | a hora do dia e a ação de cada decisão acordada |

A região (quatro, do motor) entra só no descritivo.

## 4. As medidas

### 4.1 A distância (IH-4)

A distância de variação total entre duas contagens (`distancia_tv`, `digilab/metrics.py`): metade da soma das diferenças absolutas das
frações. Vai de 0 (iguais) a 1 (sem caixa em comum).

### 4.2 A distintividade (IH-6)

Para o pet p, num perfil e nos dias da janela:
- **D_si:** a média da distância entre os dias d e d′ do próprio pet, sobre os pares d < d′;
- **D_dono:** a média da distância entre o dia d de p e o dia d dos outros pets do mesmo braço e do mesmo dono (59 sementes), sobre os
  dias;
- **D_mundo:** a média da distância entre o dia d de p e o dia d dos pets do mesmo braço e da mesma semente, com os outros dois donos;
- **H_dono = D_dono − D_si** e **H_mundo = D_mundo − D_si.** Um H positivo quer dizer que o pet se parece mais com ele mesmo em outro
  dia do que com o outro pet no mesmo dia.

**A direção da medida é conservadora:** o D_si compara dias diferentes, e o D_dono e o D_mundo comparam o mesmo dia. O relógio e o dia do
dono são comuns no mesmo dia, o que abaixa o D_dono e o D_mundo e puxa o H para baixo.

### 4.3 Por braço

- A média do H_dono e a do H_mundo sobre os 180 pets, por perfil.
- **O IC95:** o bootstrap percentil sobre as sementes, 2 000 reamostras. A semente leva os três donos juntos, e a rng é
  `derivar_semente("individualidade-i5-boot", braço, perfil, medida)`.
- **Por dono:** as mesmas médias, só no descritivo.

### 4.4 O par dos braços (só descritivo)

**D_braço:** a distância entre o dia d de p e o dia d do pet do outro braço, com a mesma semente e o mesmo dono. É o par mais perto de um
clone: o mesmo mundo, o mesmo dono e a mesma rng de partida, com as facetas como diferença. Entra só no descritivo, sem frase de leitura.

### 4.5 Onde as contas moram (IH-7)

Os três perfis de um dia, a distintividade de um pet e as médias vão para o `digilab/metrics.py`, com teste contra casos feitos à mão. O
`distancia_tv` já está lá. O bootstrap, o replay e a leitura ficam no orquestrador.

## 5. O que a análise grava

`artifacts_v3_individualidade_i5/`:
- `meta.json`: o commit, os sha256 (o orquestrador, o `metrics.py`, o `vidas.tar.gz` lido) e o comando;
- `perfis.jsonl`: uma linha por (pet, dia, perfil), com as contagens;
- `analise.json`: os H com os IC, os D, o descritivo por dono, os dias 1 a 7, o D_braço e os dias fora;
- `custo.json`: o tempo por vida rejogada.

**A conferência de cada vida:** o log refeito sai igual ao log do `vidas.tar.gz` (o G1, de novo), e o número de decisões do
`decisoes_mundo` é 96 por dia.

## 6. A leitura (descritiva)

### 6.1 A tabela

Por braço e por perfil: o H_dono e o H_mundo com o IC95, o D_si, o D_dono e o D_mundo médios e os dias fora.

### 6.2 As frases que a leitura pode escrever

- "o pet tem hábito próprio em X além do dono" só se o IC95 do H_dono de X ficar inteiro acima de 0;
- "além do mundo da semente" só se o IC95 do H_mundo de X ficar inteiro acima de 0;
- fora disso, "não se distingue de zero nesta análise". Um H negativo se descreve como está. Nada vira "o pet não tem hábito".

### 6.3 As expectativas E1 a E3

Elas são relidas contra a tabela, sem nenhum ajuste.

## 7. O custo

Não há poder a calcular, porque não há gate. O custo é o replay de 360 vidas, sem a bateria, com 4 processos e uma run por vez
(V3-D8). Ele é medido na fumaça do I5a e escrito no registro (seção 9). Estimativa SEM FONTE: menos que a vida do I2, porque não há
sondas.

## 8. As missões (cada uma num PR)

| missão | o quê |
|---|---|
| **I5-plano** | este documento (PROPOSTO) e as IH-1 a IH-7 |
| **I5a** | os perfis e a distintividade no `digilab/metrics.py`, com testes; o orquestrador `run_v3_individualidade_i5.py`, que lê o `vidas.tar.gz`, rejoga cada vida, confere o log e grava os perfis, com a trava (o cabeçalho APROVADO, o registro, no máximo 4 processos, nada por cima de uma pasta); a fumaça com as sementes dos testes |
| **I5b** | o registro, a análise uma vez e a seção do I5 no `docs/RESULTADO_V3_INDIVIDUALIDADE.md` |

## 9. O registro da análise

Antes da primeira vida rejogada, numa seção nova no fim deste plano, ficam:
- o commit e os sha256 do orquestrador, do `metrics.py` e do `vidas.tar.gz`;
- o comando e a contagem da suíte do dia.

## 10. As decisões (PROPOSTAS; cada uma com a recomendação e o custo de errar)

| | a decisão | a recomendação | o custo de errar |
|---|---|---|---|
| **IH-1** | os dados | **as vidas do I2, rejogadas do log**, sem vidas novas nem faixa nova | vidas novas gastam uma faixa e horas sem ganho, porque o I2 já tem 14 dias por pet; o custo de reusar é a dependência do I2: um erro nele contamina o I5 |
| **IH-2** | os donos | **os três da D-IND-I2c-2** (o incoerente sai) | com o incoerente, 60 pets se repetem, e o D_dono do atencioso compara o pet com uma cópia dele |
| **IH-3** | os perfis | **SEQ, LUGAR e HORA, com as caixas da seção 3** | caixas finas demais para 60 a 90 decisões acordadas por dia fazem toda distância ficar perto de 1; grossas demais apagam o hábito |
| **IH-4** | a distância | **a variação total** (já no `metrics.py`) | a Jensen-Shannon pesa diferente as caixas raras e pede um segundo teste; a TV é a mais simples de ler |
| **IH-5** | a janela | **os dias 8 a 14**, com os dias 1 a 7 no descritivo | a vida inteira mistura o bebê com o pet formado; só o fim deixa de fora o hábito que nasce cedo |
| **IH-6** | as comparações | **o H_dono e o H_mundo, no mesmo dia**, com o D_braço só no descritivo | comparar com outros dias mistura o hábito com a mudança da vida; o par dos braços como leitura misturaria o hábito com o efeito das facetas |
| **IH-7** | onde as contas moram | **os perfis e a distintividade no `digilab/metrics.py`**; o bootstrap no orquestrador | as contas no orquestrador ficam duplicadas quando o I6 (a ficha) precisar delas |
