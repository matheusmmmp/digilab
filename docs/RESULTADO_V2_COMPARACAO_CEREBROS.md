# Resultado — comparação dos DigiBrains A × C (K3/V2)

> **Nota (2026-10-24), a direção nova:** o Matheus decidiu, no PROMPT MESTRE, que o produto jogável vem primeiro, que o DigiBrain
> caminha para um cérebro **modular**, e que o cérebro A fica como linha de base, controle e fallback condicionado, e não como o cérebro
> final da web. As decisões "a web roda um DigiBrain, o A" (2026-10-01) e o M6 (rodada 15) estão **SUPERADAS** desde 2026-10-24; o
> texto abaixo fica como estava, como registro. Ver `docs/ARQUITETURA_DIGIBRAIN_MODULAR.md` e `docs/AUDITORIA_V2_PRODUTO_MODULAR.md`.
>
> "A escolha do DigiBrain da web é do Matheus": ela foi feita no M6 (o A) e está superada pela direção modular. O resultado (o
> empate A × C) continua valendo como está.

Tarefa `docs/TAREFA_V2_COMPARACAO_A_C.md` (rodada 13, worker D). Plano: `docs/PLANO_ANALISE_V2_COMPARACAO_CEREBROS.md`, seções 2 a 8 e
adendos 1 e 2. O adendo 2 foi commitado depois do piloto e antes da validação (`dcda45f`).

**Números de:**
- `artifacts_v2_comparacao_cerebros/validacao/`: `analise.json`, `resumo.json`, `medidas.json`, `meta.json`, `run.log`;
- `artifacts_v2_comparacao_cerebros/piloto/`: o mesmo conjunto.

As vidas ficam fora do git. Orquestrador: `experiments/run_v2_comparacao_cerebros.py`.

**A escolha do DigiBrain da web é do Matheus.** Este relatório preenche a tabela do M6 e recomenda.

## 1. Em uma frase

**Pela ordem do M6, o C é o recomendado, mas por pouco.**
- **Passo 1, desempenho:** empate.
- **Passo 2, legibilidade:** o C vence por +0,065 decisões, acima do limiar de 0,05.

**Um secundário pesa contra o C** (seção 4): no braço com o dono (P3), o C quase para de comer fruta, e o A aprende melhor qual fruta
evitar.

## 2. O que rodou

| | piloto | validação |
|---|---|---|
| unidades | 28101…28505, K = 4 (20) | 29101…29505, K = 1 (5), N do adendo 2 |
| vidas | 940 (47 por unidade) | 235 |
| tempo | 1 h 30 | 22 min (a estimativa do adendo era 23 min) |
| replay | toda vida rejogada do disco bit a bit, inclusive no replay das medidas | idem |

**O desenho**, igual nas duas runs, por unidade e condição (casado, descasado e mutável), com o dono atencioso em 14 dias:
- o P0 comum;
- A e C em P1, P2, P2e e P3;
- o só cuidado `sem_ensino` de P2, P2e e P3 de cada cérebro;
- o C no registro do P1 do A (descasado e mutável).

**O B não rodou:** não fecha, por "não aprende" (adendo 2.1).

**Os pontos** são o do A na K2 (T3, `g` 512, `w0_info` 256, `w0_pedido` 256, ganho 4, canais, K4, montagem completa) e o do C na
calibração dele (passo 128, teto 4096, `w0_info` 256). O mundo e o dono são os mesmos para os dois, incluído o K4.

## 3. A família primária (Holm de dois, bilateral, α = 0,05; Δ = 0,1986)

| | contraste | C − A | IC 95% | IC 90% | p bilateral | Holm | leitura |
|---|---|---|---|---|---|---|---|
| CC-1 | P1, descasado, `taxa_fruta_ruim` final | +0,016 | [−0,017; +0,046] | [−0,011; +0,042] | 0,34 | não rejeita | **empate** |
| CC-2 | P1, mutável, depois da troca | +0,036 | [−0,009; +0,078] | [+0,004; +0,067] | 0,079 (ajust. 0,159) | não rejeita | **empate** |
| CB-1, CB-2 | B − A | — | — | — | — | — | não testáveis: o B não fecha |

**Leitura:**
- **Os dois contrastes são empate.** O IC 90% fica dentro de ±Δ, e nenhum passa no Holm.
- **O sinal aponta para o A nos dois,** no piloto e na validação (C − A > 0: o C come um pouco mais a fruta ruim).
  - No piloto, com 20 unidades, o CC-2 passava no Holm: +0,033 [+0,018; +0,049].
  - Mesmo assim ficava muito dentro da margem.
  - As diferenças medidas (0,01 a 0,04) são uma ordem de grandeza menores que a margem de relevância do plano.

**Passo 1 do M6: empate** (os dois contrastes dentro da margem).

## 4. Secundários (descritivos, sem Holm; 5 unidades)

C − A na janela da primária de cada condição: final no casado e no descasado, depois da troca no mutável.

| braço | casado | descasado | mutável |
|---|---|---|---|
| P1 | +0,008 [−0,019; +0,037] | (CC-1) | (CC-2) |
| P2 | −0,037 [−0,075; −0,005] | −0,000 [−0,041; +0,037] | +0,030 [−0,000; +0,057] |
| P2e | −0,022 [−0,034; −0,012] | +0,044 [+0,012; +0,085] | +0,062 [+0,030; +0,089] |
| P3 | +0,091 [−0,150; +0,339] (4 unidades) | **+0,199 [+0,017; +0,515]** (4) | **+0,206 [+0,174; +0,250]** (4) |

**Leitura dos secundários:**
- Pela regra (IC 90% dentro de ±Δ) tudo é empate, exceto o P3. No P3, o descasado e o mutável saem "A melhor" e o casado, inconclusivo.
- **No P3, o C quase para de comer fruta.** Consumos médios por vida na validação (no piloto, a mesma ordem):

  | | casado | descasado | mutável |
  |---|---|---|---|
  | P0 | 46 | 46 | 46 |
  | A no P3 | 46 | 38 | 38 |
  | C no P3 | 17 | 9 | 14 |

  - No P3, o dono elogia a fruta boa e repreende a ruim (K4).
  - Na arquitetura do C, a bronca vai ao compartimento aversivo de comer nas células do objeto, que todas as frutas compartilham: a bronca
    generaliza para comer qualquer fruta.
  - No A, a escolha da fruta tem um peso por fruta, e o P3 aprende qual evitar. A equivalência da predição 5 do A sai com P3 − P0 de
    −0,18, IC 90% [−0,30; −0,07].
  - Com tão poucos consumos, a taxa do C no P3 fica com n pequeno, e 1 das 5 unidades não tem consumo na janela.
  - **É o braço do produto:** na web, quem ensina é o dono.
- **Consumos até a metade, no descasado:**
  - P1 +5,6 [−5,4; +21,8];
  - P2 +2,2 [−6,0; +13,0];
  - P2e −7,0 [−24,4; +7,6];
  - P3 −0,8 [−2,4; +0,8].

## 5. Legibilidade, deriva, custo e divergência acoplada

**Legibilidade** é a fração das decisões em que a sonda do aprendido muda a escolha: a parte aprendida zerada, com o mesmo `u`, e a
mesma regra nos dois (adendo 2.6).

| | P1 descasado (M6) | P1 casado / mutável | P2, P2e | P3 (casado / descasado / mutável) | P1 descasado, só decisões com escolha |
|---|---|---|---|---|---|
| A | **0,262 [0,248; 0,277]** | 0,263 / 0,261 | 0,261–0,265 | 0,298 / 0,274 / 0,292 | 0,383 |
| C | **0,327 [0,319; 0,334]** | 0,330 / 0,326 | 0,324–0,327 | 0,253 / 0,270 / 0,262 | 0,477 |

- **C − A no P1 descasado: +0,065 [+0,057; +0,072].** Passa do limiar de 0,05 e o IC 95% não contém 0: **o C vence o passo 2.** No
  piloto: +0,068 [+0,062; +0,074].
- **No A, 0,236 das decisões têm fator** (o G4 da L1, descritivo). O C não tem a expressão do motivo; a legibilidade dele é só a da sonda.
- **No P3 a ordem inverte:** o A tem o aprendido decidindo mais vezes que o C nas três condições.

**Deriva** (JSD ao instinto, P1, as três condições, bits):

| | dia 7 | dia 14 | razão 14/7 |
|---|---|---|---|
| A | 0,0138 | 0,0335 [0,032; 0,035] | 2,43 |
| C | 0,0143 | 0,0224 [0,022; 0,023] | 1,57 |

O C deriva menos e se estabiliza mais (a razão mais perto de 1).

**Custo** (vidas fechadas, P1 a P3, média por unidade; mesma máquina, nada rodando junto; detalhes no `meta.json`):

| | µs por decisão | bytes de log por dia | estado sem os motivos (bytes JSON) | parâmetros aprendíveis |
|---|---|---|---|---|
| A | 339,5 [337,3; 341,9] | 6168 | 13 509 | 762–763 |
| C | 325,0 [322,8; 327,0] | 6148 | 5 210 | 752 |
| C / A − 1 | −4,3% | −0,3% | −61% | — |

O tempo por decisão é quase todo do motor e do mundo, que são comuns.

**Divergência da mesma experiência** (o C no registro do P1 do A, JSD entre as políticas):

| | dia 7 | dia 14 |
|---|---|---|
| descasado | 0,0068 [0,0057; 0,0080] | 0,0147 [0,0133; 0,0164] |
| mutável | 0,0070 | 0,0125 |

Com a mesma experiência, os dois cérebros se afastam aos poucos, e menos do que cada um se afasta do instinto.

**Canal de cuidado** (cada braço com dono menos o próprio só cuidado, fração fora de privação):
- **A:** +0,03 a +0,12, com o IC acima de 0 em P2, P2e e P3;
- **C:** ~0 (de 0,000 a 0,019).

O só cuidado em malha aberta cuida pior que o original no A, como na validação única (limitação já declarada em 2026-10-06), e quase não
muda no C.

**As predições do experimento maior, por cérebro** (descritivas; 5 unidades; Holm de seis só como leitura):

| cérebro | 1 (casado) | 2 (descasado / mutável) | 3 (consumos) | 4a / 4b | 5 (equivalência) |
|---|---|---|---|---|---|
| A | +0,037, não rejeita | +0,102 / +0,125, rejeitam | +2,8, rejeita | +0,014 não / +0,105 rejeita | fora: IC 90% [−0,30; −0,07] (o P3 come menos a ruim) |
| C | +0,045, rejeita | +0,086 / +0,089, rejeitam | +6,2, rejeita | +0,050 / +0,061, rejeitam | fora: IC 90% [−0,20; +0,24] |

## 6. A tabela do M6 (seção 5)

| passo | critério | A | C | resultado |
|---|---|---|---|---|
| 0 | admissão | fecha (K2) | fecha (calibração C; aprende no piloto) | A e C seguem; o B sai ("não aprende") |
| 1 | desempenho (CC-1, CC-2) | — | — | **empate**: os dois contrastes dentro de ±Δ, nenhum passa no Holm |
| 2 | legibilidade (P1 descasado) | 0,262 | 0,327 | **C vence**: +0,065 [+0,057; +0,072], acima de 0,05 e IC sem 0 |
| 3 | determinismo inteiro e porte | pesos inteiros, sem função transcendental | idem | empate (preenchido, não decide) |
| 4 | custo | 339,5 µs/decisão; 6168 B/dia | −4,3%; −0,3% | empate, abaixo de 20% (preenchido, não decide) |
| 5 | desempate final | o A | — | não chega |

**Recomendação pela regra: o C.** Se a legibilidade empatasse, os passos 3 e 4 também empatariam, e o A seria o escolhido pelo passo 5.

## 7. O que o Matheus pesa

1. **A margem do passo 2 é curta.** +0,065 contra um limiar de 0,05 (PROPOSTO), medido em 5 unidades. O piloto, com 20 unidades, dá o
   mesmo (+0,068). A medida é da sonda (do sistema), não de compreensão humana (seção 3, ressalva).
2. **O P3 é o braço do produto, e nele o A é melhor.**
   - O C generaliza a bronca do dono para toda fruta: come 9 a 17 frutas por vida, contra 38 a 46 do A.
   - O A aprende qual fruta evitar.
   - No P3, a legibilidade também é do A.
   - O plano põe o P3 nos secundários (seção 4), então isso não entra na regra. É o caso da "alternativa registrada" da seção 5: o produto
     pode pedir outra ordem.
3. **O desempenho no P1 empata pela margem, mas o sinal é do A** nas duas runs (+0,01 a +0,04 de fruta ruim para o C).
4. **O C deriva menos** (razão 1,57 contra 2,43) e guarda um estado menor; o custo por decisão é igual.
5. **O A já está montado, validado e com porte conhecido** (passo 5). O C precisaria do porte para a web e de uma expressão do motivo (o
   fator) para a fala.

**Leituras de risco registradas antes** (seção 9 do plano):
- O risco 1 ("o C parecido demais com o A neste mundo") se confirma no passo 1.
- O N = 5 do adendo 2 (seção 2.5) deixou o M6 decidir no passo 2, como o adendo previu.

## 8. Limites

- **N = 5 na validação:** os secundários e os descritivos têm ICs largos; o piloto (20 unidades) vai no mesmo sentido em tudo o que
  está acima.
- **A margem Δ é a do experimento maior:** metade da taxa do P0 no descasado. Com ela, só uma diferença enorme sairia do empate.
- **Legibilidade pelo sistema, não por pessoas:** fica para a fase 2.
- **O só cuidado em malha aberta** é a limitação já declarada na validação única.
- **Nenhuma alegação de novidade.** "Inspirado em" fala dos nossos cérebros, não das fontes.
