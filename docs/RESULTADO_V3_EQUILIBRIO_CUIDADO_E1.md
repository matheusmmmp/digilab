# RESULTADO_V3_EQUILIBRIO_CUIDADO_E1: a calibração do dia a dia do pet

Fase: V3. Frente: EQUILIBRIO_CUIDADO, etapa E1. Data: 2026-11-12. Worker: Claude Code (Opus 5.5), branch `v3-equilibrio-e1`.
Plano: `docs/PLANO_V3_EQUILIBRIO_CUIDADO.md` (EQ-1 a EQ-8 DECIDIDAS). Metas: seção 6 do `docs/PLANO_ANALISE_V3_EQUILIBRIO_CUIDADO.md`,
APROVADAS pelo Matheus em 2026-11-12. O retrato de antes: `docs/RESULTADO_V3_EQUILIBRIO_CUIDADO_E0.md`.

**Os valores da rodada F2 foram APROVADOS pelo Matheus em 2026-11-12 ("Aprovo, siga").** Eles seguem SEM FONTE e passam à validação única (E2) e à versão nova (E3).

**Tudo o que o E1 mudou está atrás de chave desligada.** Os pets de hoje (todas as versões) saem byte a byte, e nenhuma versão de pet liga
as chaves: a versão nova, com os valores daqui, é o E3 (EQ-6).

**As sementes:** só as da calibração, 93101, 93202, 93303, 93404 e 93505, nas mesmas 30 vidas do E0 (o ovo de um pet v35 e o grupo do brasão
v36, os três donos, 3 dias, ritmo "rapida"). A validação (94101…94505) não foi tocada: a bancada falha alto fora da faixa de calibração.

**Os artefatos** (todo número abaixo sai deles), em `web/app/scripts/medicoes/equilibrio_cuidado_e1/`:
- uma pasta por rodada da grade, com as 30 vidas, o `resumo.json`, o `tabelas.md` e o `rodada.json` (as chaves daquela rodada);
- a `grade.md`, com as metas de cada rodada, na ordem em que rodaram;
- o comando: `node scripts/equilibrio_cuidado/e1.ts --rodada <nome>` (ou `--bloco`, ou `--grade`), em `web/app`. Uma rodada leva uns 30 s,
  num processo só.

A rodada `base` (nenhuma chave) sai igual ao E0, as 30 vidas byte a byte. A rodada `E1_escolhido` (as constantes `AJUSTE_E1_PROPOSTO` e
`BITS_V2`) sai igual à `F2_todas_urg640`, byte a byte.

## 1. As metas antes e depois

As metas que falham no E0 ou com as chaves ligadas (a rodada `E1_escolhido`). Média das 5 sementes, com o mínimo e o máximo; "passa" é a
regra do E0 (D-EQ0-6).

| id | dono | versão | E0 | passa no E0? | E1 (chaves ligadas) | passa no E1? |
|---|---|---|---|---|---|---|
| M-A1 | atento | v35 | In-Training d1 0.80 [0.25; 1.00]; Rookie d1 0.90 [0.50; 1.00]; Rookie d2 0.83 [0.67; 1.00]; Rookie d3 0.33 [0.20; 0.40] | **não passa** | In-Training d1 1.00 [1.00; 1.00]; Rookie d1 0.89 [0.67; 1.00]; Rookie d2 0.77 [0.56; 1.00]; Rookie d3 0.78 [0.40; 1.00] | **não passa** |
| M-B1 | medio | v35 | d1 6.0 [4.0; 7.0]; d2 6.8 [5.0; 9.0]; d3 6.2 [6.0; 7.0] | **não passa** | d1 5.6 [4.0; 7.0]; d2 4.2 [3.0; 5.0]; d3 4.4 [4.0; 5.0] | passa |
| M-B1 | relapso | v35 | d1 9.0 [6.0; 15.0]; d2 10.0 [6.0; 14.0]; d3 8.2 [4.0; 12.0] | **não passa** | d1 9.4 [7.0; 12.0]; d2 4.8 [4.0; 6.0]; d3 4.4 [4.0; 5.0] | passa |
| M-B1 | medio | v36 | d1 6.9 [6.0; 8.5]; d2 6.5 [5.0; 7.5]; d3 4.8 [4.5; 5.0] | **não passa** | d1 6.8 [5.0; 9.5]; d2 4.6 [4.0; 5.0]; d3 4.4 [3.5; 5.0] | passa |
| M-B1 | relapso | v36 | d1 10.4 [7.0; 12.5]; d2 11.8 [8.0; 15.5]; d3 12.8 [6.5; 20.0] | **não passa** | d1 8.9 [7.0; 11.0]; d2 6.1 [4.0; 11.0]; d3 8.6 [4.5; 13.0] | **não passa** |
| M-B2 | medio | v35 | Rookie d1 0.89 [0.79; 0.93]; Rookie d2 0.76 [0.33; 0.93]; Rookie d3 0.84 [0.62; 0.92] | **não passa** | Rookie d1 0.93 [0.92; 0.96]; Rookie d2 0.94 [0.92; 0.96]; Rookie d3 0.94 [0.93; 0.95] | passa |
| M-B2 | relapso | v35 | Rookie d1 0.47 [0.27; 0.91]; Rookie d2 0.46 [0.26; 0.61]; Rookie d3 0.54 [0.29; 0.92] | **não passa** | Rookie d1 0.43 [0.28; 0.94]; Rookie d2 0.92 [0.86; 0.95]; Rookie d3 0.90 [0.83; 0.93] | **não passa** |
| M-B2 | medio | v36 | Rookie d1 0.90 [0.80; 0.93]; Rookie d2 0.84 [0.61; 0.92]; Rookie d3 0.91 [0.89; 0.92] | **não passa** | Rookie d1 0.87 [0.62; 0.93]; Rookie d2 0.93 [0.92; 0.93]; Rookie d3 0.93 [0.92; 0.94] | **não passa** |
| M-B2 | relapso | v36 | Rookie d1 0.55 [0.42; 0.65]; Rookie d2 0.44 [0.30; 0.68]; Rookie d3 0.57 [0.37; 0.69] | **não passa** | Rookie d1 0.49 [0.29; 0.65]; Rookie d2 0.85 [0.62; 0.92]; Rookie d3 0.67 [0.59; 0.92] | **não passa** |
| M-B4 | atento | v35 | Rookie d1 0.033 [0.024; 0.036]; Rookie d2 0.043 [0.021; 0.061]; Rookie d3 0.058 [0.031; 0.094] | **não passa** | Rookie d1 0.054 [0.035; 0.082]; Rookie d2 0.066 [0.041; 0.083]; Rookie d3 0.060 [0.052; 0.062] | passa |
| M-B4 | atento | v36 | Rookie d1 0.044 [0.030; 0.060]; Rookie d2 0.057 [0.036; 0.109]; Rookie d3 0.048 [0.031; 0.062] | **não passa** | Rookie d1 0.089 [0.060; 0.153]; Rookie d2 0.075 [0.062; 0.098]; Rookie d3 0.062 [0.036; 0.093] | passa |
| M-C1 | relapso | v35 | 0.30 [0.00; 0.67] (lances por pet 3.6 [3.0; 4.0]) | **não passa** | 0.88 [0.00; 2.00] (lances por pet 1.4 [0.0; 3.0]) | passa |
| M-C1 | relapso | v36 | 0.55 [0.33; 0.86] (lances por pet 3.8 [3.0; 4.5]) | **não passa** | 0.52 [0.20; 1.00] (lances por pet 2.1 [1.5; 2.5]) | **não passa** |
| M-E1 | medio | v35 | 150 no min 2832 [2520; 3120] do pet; o tempo do Champion no min 900; 0/5 | **não passa** | 150 no min 180 [180; 180] do pet; o tempo do Champion no min 900; 5/5 | passa |
| M-E2 | atento | v35 | d1 156 [154; 159]; d2 10 [8; 12]; d3 6 [3; 8] | **não passa** | d1 173 [167; 180]; d2 34 [25; 45]; d3 28 [20; 35] | passa |
| M-E2 | atento | v36 | d1 220 [216; 222]; d2 14 [13; 15]; d3 15 [13; 18] | **não passa** | d1 267 [257; 298]; d2 54 [35; 90]; d3 56 [20; 70] | passa |

**A conta:** das 52 linhas de meta, **16 falham no E0 e 6 com as chaves ligadas**; nenhuma meta que passava no E0 cai. As outras 36 passam
nas duas, entre elas a M-D1 (nenhuma morte), a M-A2 a M-A5 (a fome e a saúde) e a M-B3 (o explorar). A tabela inteira está no
`E1_escolhido/tabelas.md`.

**O que muda para quem joga** (das tabelas do `E1_escolhido` e do E0):
- o bebê do atento come toda a ração posta (1,00 no In-Training, contra 0,80);
- o médio e o relapso dormem de 4 a 5 cochilos nos dias 2 e 3 (no ovo de um pet), contra 6 a 10, e acordam acima de 0,9 com o médio;
- o Rookie do atento brinca de 5 % a 9 % das decisões, contra 3 % a 6 %;
- os Bits seguem depois do dia 1: o atento junta de 28 a 56 por dia nos dias 2 e 3, contra 6 a 15; o ★★ sai no Rookie para todo Tamer;
- o preço: a fome < 0,25 do médio sobe para 33 a 45 min por dia no ovo de um pet (era 0 a 33) e para 33 a 101 no grupo (era 9 a 35),
  dentro da M-A3 (≤ 180).

## 2. Os valores escolhidos

Todos PROPOSTOS, SEM FONTE, com a medida que os justifica (a rodada F2, igual à `E1_escolhido`).

| o quê | hoje | o E1 propõe | onde | a medida |
|---|---|---|---|---|
| a guarda da fome urgente no brincar (EQ-7) | não existe | ligada | `ConfigEquilibrioCuidado.guarda_fome_brincar` (Python e TS) | nenhuma decisão com a fome urgente brinca (a paridade e o `tests/test_equilibrio_cuidado.py`); o pet faminto não vai jogar bola (D-BB2-3) |
| o bebê come com a fome dele (EQ-7) | não existe | ligada, `w_comer_bebe` = 512 (S/2) | `ConfigEquilibrioCuidado.comer_bebe`, `w_comer_bebe` | a ração comida no In-Training do atento: 0,95 só com ela (rodada A, w = 512) e 1,00 com tudo; o menor peso da grade que passa a M-A1 sozinho |
| a fome urgente (`urgencia_lambda`) | 512 | 640 | `config.INATOS_E1_PROPOSTOS`; `AJUSTE_E1_PROPOSTO` no TS | a M-B1 e a M-B2 do médio passam, e a M-B1 do relapso do ovo de um pet; o 640 é o que menos metas deixa falhar com as outras chaves (F2: 6; o 768 do F1: 8; o 576 do F4: 10; o 704 do F5: 8) |
| o vies do brincar no W0 | −256 | 0 | `config.INATOS_E1_PROPOSTOS` (`vies_brincar`) | a M-B4 nas duas versões; o menor valor da grade que passa as duas (o −128 só passa o grupo) |
| o cuidado na hora certa (Bits) | 1 | 5 | `BITS_V2` (`src/bits.ts`) | a M-E2 do atento nas duas versões; com 4 e o teto 40, o 3º dia do ovo de um pet fica em 19 |
| o teto do cuidado por dia (Bits) | 20 | 40 | `BITS_V2` | com o teto 20 ou 30, o atento do ovo de um pet não passa de 15 no 3º dia |
| a evolução para o Rookie (Bits) | 50 | 60 | `BITS_V2` | a M-E1 do médio do ovo de um pet: ele só cuida uma vez antes do minuto 900 (o 480), e 60 + 90 do Tamer = 150 já no Rookie |
| o `lambda_acordar` do sono que segura | 922 | 922 (não muda) | — | o 870 e o 1 000 pioram ou não ajudam (rodadas B_acordar) |
| o `w_bola_do_dono` | 4 096 | 4 096 (não muda) | — | o 2 048 não muda nenhuma meta (rodada B4_bola2048) |

**As chaves criadas:**
- no Python: `ConfigEquilibrioCuidado` (`guarda_fome_brincar`, `comer_bebe`, `w_comer_bebe`; `PARAMETROS_EQUILIBRIO_CUIDADO`) e os números
  `INATOS_E1_PROPOSTOS` com o `inatos_e1()` (`PARAMETROS_E1`), em `digilab/config.py`; o gancho `estagio_bebe(bool)` do `DigiBrain`;
- no TS: a mesma `ConfigEquilibrioCuidado` (`motor/digibrain/constantes.ts`), o gancho `estagioBebe`, o `AjusteEquilibrioE1` com o
  `AJUSTE_E1_PROPOSTO` (`motor/equilibrio_e1.ts`), o `Motor.ligarEquilibrioE1` (só a bancada; não entra no registro) e a tabela `BITS_V2`
  (`src/bits.ts`, com o `feitosDoPet(m, tabela)`).

## 3. A grade

A ordem é a do `GRADE` em `scripts/equilibrio_cuidado/e1.ts`; o número é de linhas de meta que não passam (de 52; o E0 tem 16).

| bloco | rodada | o que tenta | metas que falham | o que muda (das do E0) |
|---|---|---|---|---|
| — | base | nenhuma chave | 16 | igual ao E0, byte a byte |
| A | A_bebe_w256 | o bebê come, w = 256 | 18 | a ração do In-Training sobe a 0,85; o sono do atento v35 sai da faixa |
| A | A_bebe_w512 | w = 512 | 17 | **passa a M-A1 do atento v35** (In-Training 0,95, Rookie d3 0,80); a M-E1 do atento v35 cai (o bebê que come chama menos: menos Bits de chamado) |
| A | A_bebe_w768 | w = 768 | 17 | a M-A1 volta a falhar (o Rookie d3 0,78) |
| A | A_bebe_w1024 | w = 1 024 | 17 | idem (d3 0,67) |
| B | B_urg576 | `urgencia_lambda` = 576 | 14 | passam a M-B1 do médio (as duas versões), a M-B2 do médio v35 e a M-B1 do relapso v35 |
| B | B_urg640 | 640 | 14 | as mesmas |
| B | B_urg768 | 768 | 13 | e a M-B2 do médio v36 |
| B | B_urg896 | 896 | 9 | e o sono do relapso nas duas versões; mas a ração do atento v35 cai a 0,38 no 3º dia e o sono do atento sai da faixa |
| B | B_acordar870 | `lambda_acordar` = 870 | 20 | pior: o sono do atento sai da faixa |
| B | B_acordar1000 | 1 000 | 15 | só o médio v35 |
| B4 | B4_vies-128 | vies do brincar = −128 | 16 | a M-B4 do grupo |
| B4 | B4_vies0 | 0 | 14 | **a M-B4 nas duas versões** |
| B4 | B4_vies128 | 128 | 14 | idem, e o sono do atento v35 cai |
| B4 | B4_bola2048 | `w_bola_do_dono` = 2 048 | 16 | nada (o atento quase não lança: 0,2 a 0,5 lance por célula) |
| C | C_guarda | a guarda | 16 | nada passa; os chutes do relapso caem (0,15 no v35, 0,39 no v36) |
| E | E_cuidado2_teto20 … E_cuidado4_teto40 | o cuidado de 2 a 4, o teto de 20 a 40 | 15 | a M-E2 do grupo; a do ovo de um pet chega a 19 no 3º dia (4 e 40) |
| E | E_cuidado5_teto40_evo50 | cuidado 5, teto 40 | 15 | idem |
| E | E_cuidado4_teto40_evo60, E_cuidado5_teto40_evo60 | e a evolução do Rookie 60 | 14 | **a M-E1 do médio v35** |
| F | F1_todas_urg768 | tudo, com a fome urgente 768 | 8 | — |
| F | **F2_todas_urg640** | tudo, com 640 | **6** | o escolhido |
| F | F3_todas_bebe768_urg640 | o F2 com o bebê 768 | 7 | — |
| F | F4_todas_bebe512_urg576 | o F2 com a fome urgente 576 | 10 | — |
| F | F5_todas_bebe512_urg704 | o F2 com 704 | 8 | — |
| F | E1_escolhido | o F2 pelas constantes | 6 | igual ao F2, byte a byte |

Os valores de cada meta em cada rodada estão na `grade.md`. **As rodadas mexem umas nas outras:** uma regra que muda uma decisão muda a vida
dali em diante (o sorteio, o dono que reage ao corpo), e as metas na borda (o 0,80 da ração, os 6 cochilos, o 0,90 da energia) entram e saem.
Com 5 sementes, uma diferença de uma meta entre duas rodadas é ruído; a escolha olhou o total e as metas que cada bloco mira.

## 4. O que não fechou, e por quê

1. **M-A1, a ração do Rookie do atento no ovo de um pet (0,77 a 0,78 nos dias 2 e 3).** O problema do Rookie não é o do bebê (a pergunta do
   pedido): é a medida e o dono. O atento põe uma ração a cada 30 min enquanto a fome está abaixo de 0,45, e o pet que dorme (o sono que
   segura) não come; quando ele acorda, come uma, e as outras ficam. As rações postas nas últimas horas do 3º dia não têm tempo de ser comidas
   antes do fim da janela (no E0, a semente 93202 põe 5 rações entre os minutos 4 174 e 4 294, com o pet dormindo). Nenhum número do pet
   resolve isso sem mexer no dono (EQ-4) ou na medida. Proposta ao Matheus: medir a ração comida até o fim da vida mais um período sem dono, ou
   contar só as rações postas com a ração anterior já comida (D-EQ1-6).
2. **O In-Training do médio e do relapso continua sem ração.** É o dono, não o pet: o médio olha às 2 h e acha a fome acima de 0,7 (o limiar do
   chamado do bebê), e o relapso só chega no Rookie. O bebê não chega a ter fome no In-Training de 3 h. A regra do bebê não muda nada aqui (as
   vidas do médio e do relapso da rodada A_bebe_w512 saem iguais às do E0, byte a byte: sem ração à vista, o bebê não tem
   unidade do comer, e o termo novo não entra). A célula sem ração não conta
   (D-EQ0-6).
3. **M-B1 e M-B2 do relapso (e a M-B2 do médio do grupo no dia 1).** A fome urgente acorda o pet do relapso, que acha o comedouro vazio,
   gasta a energia e volta a dormir: os cochilos curtos vêm da fome, e a fome vem do dono que some 6 h. Com a fome urgente em 640, os dias 2
   e 3 do ovo de um pet já ficam na faixa (4,4 a 4,8 cochilos, 0,90 a 0,92 ao acordar), mas o dia 1 (0,43) e o grupo não. Subir mais (896)
   fecha o relapso, mas deixa o pet do atento com fome e com a ração parada. **O gate falho não para a rodada:** fica registrado como
   achado. O pet do dono relapso dormir mal é o castigo que a EQ-4 espera.
4. **M-C1 do relapso do grupo (0,52).** A guarda da fome urgente **baixa** os chutes do relapso (0,15 e 0,39 só com ela): o relapso brinca com
   o pet faminto, e a guarda diz não, como o G-BB-2 pede. A meta conta todo lance, inclusive o que a fome urgente recusa; o G-BB-1 da bola
   contava só os elegíveis. Com a guarda ligada, a M-C1 do relapso só passa se o relapso não deixar o pet com fome. No ovo de um pet ela passa
   (0,88), mas com 1,4 lance por pet (de 0 a 3): pouco. Proposta ao Matheus: contar a M-C1 como o G-BB-1, só nos lances elegíveis (D-EQ1-7).
5. **Os Bits pagam o corpo baixo, não o cuidado.** O cuidado na hora certa só paga quando a fome cai abaixo de 0,45 (ou a higiene e o humor
   abaixo de 0,25), e o atento evita isso: ele ganha menos eventos que o médio. Para o atento chegar a 20 por dia, o cuidado tem de pagar 5
   e o teto subir a 40, e então o relapso também ganha (220 Bits em 3 dias no ovo de um pet, contra 235 do atento e 225 do médio). Os números
   fecham a M-E2, mas não a ordem que o plano da moeda quer (o cuidado bom rende mais). Uma fonte nova (o chamado do Rookie, a M-2 do plano da
   moeda, ou um "dia bem cuidado") seria regra nova, fora da EQ-7: fica como proposta (D-EQ1-8). E o ★★ no Rookie (60 + 90) vale para todo
   Tamer, inclusive o relapso, porque a bancada não luta: com as lutas da Campina o ★★ chegaria antes de qualquer jeito.
6. **A regra do bebê mexe nos Bits do atento.** O bebê que come chama menos por fome, e o atento perde Bits de chamado antes do Rookie: só com
   a regra (rodada A), o ★★ do atento do ovo de um pet sai depois do minuto 180 em 3 de 5 sementes (M-E1). Com a `BITS_V2` volta a passar.
   As duas mudanças precisam ir juntas no E3.

## 5. Os testes

- os gabaritos de hoje byte a byte: `tests/test_gabarito_equilibrio_cuidado.py` (o gabarito novo `tests/gabaritos/equilibrio_cuidado_de_hoje.json`,
  gravado antes das regras, 33 vidas do REL com e sem o sono e o lance), o `test_gabarito_lance_dono.py` e o `test_gabarito_sono_segura.py`;
  no TS, os gabaritos e os replays de todas as versões no vitest inteiro, e a rodada `base` igual ao E0;
- a paridade Python × TS das regras novas: `web/app/test/equilibrio_cuidado_paridade.test.ts`, contra o
  `test/gabaritos/digibrain_modular_equilibrio_cuidado.json.gz` (3 vidas de 4 dias, com as duas regras, os inatos do E1 e o bebê nas 96
  primeiras decisões; a guarda dispara em 49 decisões);
- o Python das regras: `tests/test_equilibrio_cuidado.py`;
- a bancada: `web/app/test/equilibrio_cuidado_e1.test.ts` e o do E0.

As contagens estão no registro (D-EQ1-9) e na seção "Resultado do E1" da tarefa.

## 6. O que vem

O Matheus decide os valores da seção 2 e as propostas D-EQ1-6 a D-EQ1-8. Depois, o E2 (a validação única, em 94101…94505) e o E3 (a
versão nova do pet com as chaves ligadas).
