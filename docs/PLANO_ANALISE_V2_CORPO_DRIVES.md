# Plano de análise — V2: o P1 com o corpo e os drives novos

Status (2026-10-07): **PROPOSTO**, registrado **antes de qualquer run**. **PCD-1 a PCD-7 DECIDIDAS pelo Matheus em 2026-10-07, todas
pela recomendação** (seção 12). Tarefa: `docs/TAREFA_V2_CORPO_DRIVES.md` (#209), com as CD-1 a
CD-10 DECIDIDAS (#210). É o plano que a seção 13 da tarefa pede.

**Regras deste plano:**
- Os números que ainda não existem saem da calibração e entram num adendo commitado antes da validação.
- Os números de antes citam o artefato.
- O que não está aqui é **descritivo pós hoc** e é declarado assim no resultado.
- Nada se reajusta olhando a validação, que roda uma vez só. Pela decisão do Matheus de 2026-10-01, um gate que falha é registrado e não
  para a V2.

## 1. A pergunta

**O P1 com o corpo (drives novos ligados) deixa de ficar parado, sem piorar o cuidado, contra o P1 com a química de hoje?**

**O ponto de partida.** No mundo `padrao`, o P1 aprendeu a ficar parado (`docs/RESULTADO_V2_N3.md`, de
`artifacts_v2_n3/validacao/ganho4/resultado.json`):

| tempo livre | P0 | P1 |
|---|---|---|
| brincar | 35% | 11% |
| explorar | 29% | 15% |
| ocioso | 28% | 47% |
| chamar | 9% | 27% |

Brincar e explorar só davam sinal negativo, porque gastam energia. Com o corpo, brincar reduz o tédio e o carinho reduz a solidão. A
conta de exemplo da tarefa (seção 9) dá +1440 ao brincar com a bola com o tédio em 0,75, contra −34 hoje.
- **O sinal** é o homeostático do N3, sobre os receptores (Keramati e Gutkin 2014, `10.7554/elife.04811`, VERIFICADA; o expoente 2 sem raiz
  é escolha do projeto).
- **A pergunta é se isso vira comportamento** na vida inteira, e sem um pet que só brinca e descuida da fome.

**Os nomes dos regimes do corpo:**
- **hoje:** a chave do corpo desligada (os drives em float, como sempre);
- **química:** `ConfigCorpo.ligada`, com a digestão na taxa C e a Vida, **sem** os drives novos. É a "química de hoje" da pergunta (CD-3);
- **corpo:** a química mais `drives_novos` e `gestos`, com tédio, solidão, estresse, dor e susto. **A curiosidade fica fora** (seção 3.4,
  CD-8).

**Predições** (sentido fixado agora):

| # | predição | contraste | papel |
|---|---|---|---|
| PR-H | a química não muda as vidas de hoje além da margem | {química − hoje} em P0, P1 e P3 | pré-condição (G-HOJE (b)) |
| PR-1 | o P1 com o corpo passa mais tempo livre brincando e explorando | P1-corpo − P1-química > 0 | **primária** (G-PARADO) |
| PR-2 | sem piorar o cuidado | privação e saúde do P1-corpo não piores que as do P1-química, além da margem | **co-primária** (G-CUIDADO) |
| PR-3 | o efeito aparece com o mesmo cuidado | P1-corpo^ac − P1-química^ac > 0, os dois acoplados à mesma fonte | secundária (Holm) |
| PR-4 | o efeito aparece também sem a bola | o mesmo contraste da PR-1 no mundo `padrao` | secundária (Holm) |
| PR-5 | o aprendiz baixa o próprio tédio mais que o instinto | P0-corpo − P1-corpo no tédio médio > 0 | secundária (Holm) |

## 2. O mundo e os donos

| item | valor | fonte |
|---|---|---|
| mundos | **`bola`** (o primário: brincar com a bola é o que mais reduz o tédio, tarefa seção 7) e **`padrao`** (o do N3, onde brincar não tem bola) | a bancada (BANCADA-MUNDOS, B1 e B2) |
| motor | o `MotorCorpo` da tarefa (seção 2), por baixo da cadeia de cada mundo | tarefa, seção 2 |
| duração e orçamento | 14 dias, 224 interações | os de toda a V2 (`experiments/configs/v2_experimento_maior/validacao.json`) |
| cérebro do P1 | o A da montagem completa, no ponto da validação única: T3, ganho 4, canais ligados. Fora dos mundos das frutas, sem memória | o mesmo arquivo; tarefa, seção 11 |
| o que o A ganha com o corpo | o `sinal_corpo`, as entradas dos drives novos nas regras de tempo livre (prior 0) e o tapa como a bronca | tarefa, seções 9 e 11 |
| morte | desligada, como no N3 | — |

**O ponto do A não se recalibra** (M10). A calibração deste plano é do corpo (seção 6).

**Os donos.** São os quatro da v1: aleatório, relapso, atencioso e incoerente.
- **No bloco G-HOJE:** os donos de sempre, com elogiar e repreender. Isso compara a química com as vidas de hoje.
- **Nos blocos do corpo e do tapa:** os mesmos donos dentro do `DonoComGestos` (tarefa, seção 14). O `elogiar` vira `acariciar`, e o
  `repreender` vira `tapa` (modo **tapa**) ou nada (modo **sem tapa**). O resto do dono e o orçamento ficam iguais.
- **O contraste primário usa o modo sem tapa nos dois lados.** O `tapa` só existe com `gestos`, que exige os drives novos, então o P1-química
  não pode recebê-lo. Com o modo sem tapa, o dono é o mesmo nos dois braços, e a diferença é o corpo: os drives novos e o carinho creditado
  pelo corpo (CD-4).

## 3. Os braços

### 3.1 Bloco G-HOJE (a química contra hoje, malha fechada)

| braço | regime | cuidado |
|---|---|---|
| P0-hoje, P1-hoje, P3-hoje | hoje | os donos de sempre, reagindo ao pet |
| P0-química, P1-química, P3-química | química | idem |

### 3.2 Bloco do corpo (a pergunta)

| braço | regime | dono | para quê |
|---|---|---|---|
| **P0-q** | química | `DonoComGestos`, sem tapa | a referência do instinto |
| **P1-q** | química | idem | o "P1 com a química de hoje" |
| **P0-c** | corpo | idem | os drives novos medidos num pet que não aprende |
| **P1-c** | corpo | idem | o "P1 com o corpo" |
| **P1-q^ac** | química | **acoplado ao P0-q da mesma célula** (o registro dele, sem filtro) | PR-3 |
| **P1-c^ac** | corpo | **acoplado ao mesmo P0-q** | PR-3 |

**O P0 continua o instinto de hoje** (CD-2), e o P0-c tem de decidir igual ao P0-q:
- o instinto não lê os drives novos, e o estresse não muda outra função (CD-7);
- por isso o P0-c é o P0-q com os químicos novos acompanhados;
- é um teste de mecanismo na validação (G-P0C, seção 8): as mesmas ações, decisão a decisão.

**A variante P0c ("instinto do corpo")**, o P0 lendo os drives novos por regras fixas, **não entra**. Fica pendente, como na seção 16 da
tarefa.

### 3.3 Bloco do tapa (só no mundo `bola`)

| braço | regime | dono |
|---|---|---|
| **P0-c-tapa** | corpo | `DonoComGestos`, modo tapa |
| **P1-c-tapa** | corpo | idem |

Os pares sem tapa são o P0-c e o P1-c do bloco do corpo, nas mesmas células.

### 3.4 A curiosidade (CD-8): fora deste plano

A curiosidade exige o mundo físico (`MotorMundo`). Sem ele, `drives_novos` liga só o tédio, a solidão e o estresse, e é assim que os braços
acima rodam.

**Um braço com curiosidade** (P0-c+cur e P1-c+cur, no mundo físico) só entra por **adendo antes da calibração**, e só se o `MotorMundo`
estiver na `main` nesse momento:
- usa o ponto do mundo físico (`docs/PLANO_ANALISE_V2_MUNDO_FISICO.md`, adendo 1);
- usa as unidades deste plano.

Se não entrar, vira plano próprio. **Nunca entra depois de a calibração ter começado.**

### 3.5 O acoplado e o achado da validação única

**O achado.** Na validação única, o "só cuidado" acoplado cuidou **pior** que o braço original. Em todo braço com dono, os braços em malha
fechada tiveram menos privação e mais saúde que o acoplado deles: fora de privação +0,042 a +0,075, saúde +0,020 a +0,037
(`docs/RESULTADO_V2_VALIDACAO_UNICA.md`, seção 1). O cuidado rejogado foi dado a outro pet.

**Como este plano lida com isso:**
1. **Nunca compara um acoplado com um braço de malha fechada.** A desvantagem da malha aberta entraria no contraste como se fosse efeito.
2. **Acopla os dois lados à mesma fonte.** O P1-q^ac e o P1-c^ac recebem o mesmo registro, o do P0-q da célula: mesmo cuidado, mesmos
   ticks, mesma desvantagem de malha aberta.
   - A diferença entre os dois isola o corpo, com o cuidado fixo (PR-3).
   - O registro mantém o carinho, porque o carinho é estímulo do corpo e é parte do que se testa.
   - O modo sem tapa não tem tapa a tirar.
3. **O cuidado preservado (PR-2) só se lê em malha fechada.** No acoplado o cuidado não reage ao pet, então a privação ali não mede se o pet
   novo é mais fácil ou mais difícil de cuidar.
4. **O primário é a malha fechada (PR-1).** É o pet do produto, com o dono reagindo. A PR-3 diz se o efeito sobrevive com o cuidado fixo.

## 4. Unidades, pareamento e células

- **Unidade:** a semente derivada por `unidades_derivadas(bases, K, prefixo="corpo")`. O prefixo novo entra em `PREFIXOS_UNIDADES`
  (etapa 8 da tarefa, chat D).
- **Célula:** dono × mundo (4 × 2), e no bloco do tapa só o mundo `bola` (4).
- **Pareamento:** por unidade e por célula. A rng do dono não depende do braço (a regra da bancada).
- **Estatística por unidade:** a média das células da diferença entre braços.

**Vidas por unidade:**

| bloco | vidas |
|---|---|
| G-HOJE | 3 cérebros × 2 regimes × 8 células = 48 |
| corpo | 4 braços × 8 + 2 acoplados × 8 = 48 |
| tapa | 2 × 4 = 8 |
| **total** | **104** |

## 5. As medidas

Todas são amostradas em cada decisão dos **dias 8 a 14**. A vida toda entra como descritivo. O P1 começa no prior do instinto, então os
primeiros dias são iguais em esperança e só somam ruído.

### 5.1 Comportamento

- **`BE`, a primária:** a fração das decisões de tempo livre (regras `tempo_livre` e `bola_no_cenario`) em que o pet escolhe brincar ou
  explorar.
- **`OC`:** a fração em ocioso ou chamar, relatada ao lado. Não é gate, porque é quase o complemento da `BE`.
- **As quatro ações** do tempo livre, uma a uma, e comer na fome moderada: como no N3, descritivo.

### 5.2 O cuidado preservado

- **privação:** 1 − `fracao_fora_de_privacao`, pela `Estado.em_privacao` (a definição do N3);
- **saúde média;**
- **fome média,** só descritiva: é o lado do "pet que só brinca" (R-1).

### 5.3 Os drives novos

- **tédio, solidão e estresse médios:** a falta lida pelo receptor, na escala 0–1;
- **a fração do tempo acordado com cada um acima de 0,75.**

O tédio entra na PR-5. Os outros são descritivos.

### 5.4 Os efeitos do tapa (tarefa, seção 8)

**Medo da mão:**
- a redução média da solidão por carinho nas 6 h depois de um tapa, contra a mesma medida sem tapa nas 6 h anteriores;
- a fração de `chamar_atencao` nas decisões das 6 h depois de um tapa.

**Estresse acumulado:**
- o estresse médio no fim de cada dia;
- a fração do tempo acima de 0,75.

**Vínculo: "não disponível"** até a base nova do vínculo (S-4) entrar. A medida sai assim no resultado, como dependência declarada.

**O carinho depois do tapa:** o sinal médio que o carinho credita nas 6 h depois de um tapa, contra sem tapa antes. É a medida do R-3.

**Por que tudo isso é descritivo, com IC e sem gate.** O que o tapa faz no corpo (dor, susto, estresse, o carinho que alivia menos) é
construído pelas regras da tarefa. O plano mede o tamanho, não testa a existência. A parte aprendida é o chamar depois do tapa no P1 contra o
P0, e também entra só como descritivo: a decisão do tapa já foi tomada (S-2).

## 6. A calibração conjunta (sementes de calibração)

**É uma calibração só (M10),** dos números PROPOSTOS do corpo, numa grade conjunta. Não é uma calibração por nó.
- **As bases:** 33101, 33202, 33303, 33404 e 33505, com K = 4 (N = 20 unidades).
- **O que fica de fora da escolha:** o P1 e qualquer contraste entre braços. A grade roda **só o P0-c**: o instinto não aprende, e o corpo
  não muda as decisões dele (CD-2, CD-7). A escolha não tem como favorecer o P1.

### 6.1 O que varia

| parâmetro | grade | o que escala |
|---|---|---|
| `m_sobe` | {½, 1, 2} | as subidas por tick do tédio (+450), da solidão (+225) e do estresse (o divisor 256), juntas |
| `m_reduz` | {½, 1, 2} | as reduções: brincar com a bola −135000, sem bola −45000, dono brinca −90000, acariciar −180000 na solidão e −90000 no estresse |
| `w_novos` | {1, 2, 4} | o peso inteiro dos drives novos no sinal (seção 9 da tarefa). Os de hoje ficam em 1 |

**O que fica fixo:**
- o limiar do estresse (337500, 0,75), as meias-vidas e o tapa (dor +90000, susto +180000, estresse +45000);
- o `recompensa_tapa`: a CD-10 decidiu que ele vale o mesmo que a `recompensa_repreensao` (−1,0). A calibração só o **mede** em ½× e 2×,
  como sensibilidade descritiva (6.4). Mudar o valor é decisão do Matheus (PCD-6).

Os pontos: 3 × 3 = 9 valores do corpo × 8 células × P0-c = **72 vidas por unidade**, 1.440 no total. O `w_novos` não precisa de vida nova:
o sinal é recalculado sobre as vidas do P0-c (6.2, passo 3).

### 6.2 A regra de escolha (escrita agora)

1. **A faixa dos drives**, nas vidas do P0-c, com os dois mundos juntos:
   - no tédio e na solidão, a fração do tempo acordado com falta ≥ 0,75 fica em **[0,10; 0,50]**;
   - no estresse, essa fração fica **≤ 0,20**.

   A faixa é PROPOSTA, SEM FONTE. A ideia é que o drive varie: nem preso no cheio, nem sempre vazio.
2. **Entre os pontos que passam,** fica o mais perto de (`m_sobe`, `m_reduz`) = (1, 1), pela soma de |log₂|. Isso preserva os números da
   tarefa. No empate, o menor `m_sobe`.
3. **O peso `w_novos`:** o menor de {1, 2, 4} em que a mediana da parcela dos drives novos em |D_antes − D_depois| fica em **[0,25; 0,75]**.
   - a parcela é calculada nas decisões de tempo livre das vidas do P0-c, com os receptores antes e depois de cada ação. É uma sonda: o
     P0 não aprende;
   - a ideia é que nenhum dos dois grupos de drives cale o outro no sinal.

**A parada:** a grade roda uma vez.
- **Se nenhum ponto passa o passo 1:** fica o ponto de menor distância das frações ao centro das faixas, com o registro "não fechou".
- **Se nenhum `w_novos` passa o passo 3:** fica o de parcela mais perto de 0,5, com o mesmo registro.

Não há segunda rodada, e nada volta à grade depois do piloto.

### 6.3 O piloto (só para o N e as margens)

No ponto escolhido, e só nele, rodam todos os blocos da seção 4 nas mesmas 20 unidades. O piloto serve só para três coisas:
- as **margens** (seção 7);
- o **N** (seção 7);
- o custo medido.

Os números dele são relatados como piloto e não entram como evidência.

### 6.4 Sensibilidade do tapa (descritiva)

No ponto escolhido, o P1-c-tapa roda também com `recompensa_tapa` em −0,5 e −2,0. Saem as medidas da 5.4 e as vidas com peso no teto. Só
relato, para a PCD-6.

### 6.5 O adendo

Entram no `docs/PLANO_ANALISE_V2_CORPO_DRIVES.md`, adendo 1, num commit **antes** da validação:
- o ponto (`m_sobe`, `m_reduz`, `w_novos`) e se fechou;
- as margens e o N;
- o poder simulado de cada gate;
- o custo.

## 7. As margens e o N (como no adendo da opção A)

**Cada margem fica na escala da sua medida** (`docs/PLANO_ANALISE_V2_EXPERIMENTO_MAIOR.md`, adendo 2). Os valores saem do piloto e ficam
congelados no adendo.

| margem | regra (registrada agora) | o que se espera, sem valor de gate |
|---|---|---|
| `Δ_BE` (o efeito do corpo, PR-1, PR-3 e PR-4) | **metade** da distância \|`BE`(P0-q) − `BE`(P1-q)\| no mundo `bola`: metade do "pet parado" nesta montagem, a convenção de "metade" da regra 6.3 | no N3 a distância foi 0,64 − 0,26 = 0,38 (padrão); daria ~0,19 |
| `Δ_priv` (cuidado, PR-2) | **um quarto** da privação média do P0-q | no N3 a privação do P0 foi 0,105; daria ~0,026 |
| `Δ_saude` (cuidado, PR-2) | **um quarto** de (1 − saúde média do P0-q) | no N3, 1 − 0,916 = 0,084; daria ~0,021 |
| `Δ_TED` (PR-5) | **metade** do tédio médio do P0-c (nota abaixo) | sem referência anterior: o tédio não existe hoje |
| G-HOJE (b) | **metade** da margem correspondente: `Δ_BE/2`, `Δ_priv/2`, `Δ_saude/2` | a química não pode mover a vida de hoje em mais que metade da menor mudança que os gates do corpo contam |

**A nota sobre o tédio:** no P0-q o tédio não existe como químico, então a referência é o P0-c. A margem é usada só no cálculo do N da PR-5
(o poder para detectar uma queda de metade do tédio que o instinto carrega). O gate da PR-5 é o IC95 acima de 0.

**A margem do cuidado é mais apertada que a do efeito** (um quarto, contra metade). A PR-2 é de não inferioridade: aceitar metade da
privação do P0 a mais seria aceitar um pet bem pior de cuidar (PCD-2).

**O N, pela simulação de poder:**
- **o método:** bootstrap das diferenças por unidade do piloto, com 2.000 réplicas por K;
- **os efeitos (PR-1, PR-3, PR-4, PR-5):** poder ≥ 0,8 para detectar a margem, com as diferenças centradas e deslocadas para ela;
- **a não inferioridade e as equivalências (PR-2 e G-HOJE (b)):** poder ≥ 0,8 para declarar não inferior ou equivalente quando a diferença
  verdadeira é zero, com as diferenças centradas em zero;
- **a escolha:** o N é o maior entre os gates, com K de 4 a 10 por base (N de 20 a 50). Se nem K = 10 chega a 0,8 num gate, a validação roda
  com K = 10, e o gate sai declarado subpotenciado, com o poder;
- **o G-HOJE (b) tem N próprio na mesma regra,** mas roda nas mesmas unidades: o N da validação é o maior de todos.

## 8. A validação (uma vez)

- **As bases:** 34101, 34202, 34303, 34404 e 34505, com o K do adendo.
- **O que roda:** os três blocos, uma vez.
- **O replay:** toda vida é rejogada e comparada bit a bit (G1). Divergência para tudo.
- **O bootstrap:** sobre as unidades, com 10.000 reamostragens, semente 4242 e IC95. O IC90 entra só nas equivalências.

| gate | contraste (por unidade, média das células) | regra | papel |
|---|---|---|---|
| **G-P0C** | P0-c contra P0-q | as mesmas ações, decisão a decisão, em toda vida | mecanismo: se falha, o corpo vazou para o instinto, e a run para |
| **G-HOJE (b)** | química − hoje, em P0, P1 e P3, nas medidas `BE`, privação e saúde | **todas** as nove com o IC90 dentro de ± a margem do G-HOJE | pré-condição (interseção-união, sem correção) |
| **G-PARADO** | P1-c − P1-q em `BE`, mundo `bola` | as categorias abaixo | **primário** |
| **G-CUIDADO** | P1-c − P1-q em privação e P1-q − P1-c em saúde, mundo `bola` | **as duas** com o limite superior do IC95 < a margem | **co-primário** (interseção-união) |
| G-SEP | P1-c^ac − P1-q^ac em `BE`, mundo `bola` | limite inferior do IC95 > 0, Holm | PR-3 |
| G-PADRAO | P1-c − P1-q em `BE`, mundo `padrao` | limite inferior do IC95 > 0, Holm | PR-4 |
| G-TED | P0-c − P1-c no tédio médio, mundo `bola` | limite inferior do IC95 > 0, Holm | PR-5 |

**As categorias do G-PARADO** são exclusivas e lidas nesta ordem; vale a primeira que se aplica (a ordem da leitura do PR #196):
1. **ganha:** o limite inferior do IC95 > 0. Se o limite superior do IC90 < `Δ_BE`, leva o rótulo **"ganha, abaixo de Δ"**;
2. **perde:** o limite superior do IC95 < 0;
3. **equivalente:** o IC90 dentro de ±`Δ_BE`;
4. **inconclusivo:** o resto.

**O Holm** cobre {G-SEP, G-PADRAO, G-TED}, com α = 0,05.

**A regra de decisão:**
- **"Deixa de ficar parado sem piorar o cuidado"** só quando o G-PARADO ganha **e** o G-CUIDADO passa:
  - com o G-HOJE (b) passando, a leitura vale contra a vida de hoje;
  - com ele falhando, vale só contra a química: a química sozinha já muda as vidas além da margem, e o próximo passo do corpo (S-3, ligar no
    produto) espera a explicação.
- **O G-PARADO ganha e o G-CUIDADO falha:** o corpo tira o pet do parado, mas o cuidado piora. É o R-1, o pet que só brinca. Resultado
  registrado; o corpo não liga no produto como está.
- **O G-PARADO empata, perde ou fica inconclusivo:** os drives novos, nesta montagem, não bastam para o aprendiz sair do parado. Isso aponta
  para o crédito entre decisões e para o pet que planeja (`docs/V2_RODADA_16.md`, seção 6).
- **O G-SEP falha com o G-PARADO ganhando:** o efeito depende do dono reagir ao pet (mais carinho para quem brinca), e não só do corpo. Fica
  registrado ao lado da leitura do primário.

## 9. Riscos

| # | risco | o que o plano faz |
|---|---|---|
| R-1 | **O pet que só brinca e descuida da fome.** Com o tédio pesando no sinal, brincar pode render mais que comer na hora | o G-CUIDADO é co-primário, e a fome média e comer na fome moderada saem ao lado. A faixa da 6.2 impede um tédio sempre cheio |
| R-2 | **A curiosidade exige o mundo físico** (CD-8). Sem o `MotorMundo`, explorar não acha nada, e uma curiosidade que só sobe seria castigo constante | os braços rodam sem a curiosidade (só tédio, solidão e estresse). O braço com curiosidade só entra por adendo antes da calibração (3.4). Explorar continua sem drive que o pague, e a `BE` pode subir só pelo brincar: as ações saem separadas |
| R-3 | **A dupla contagem do tapa** (CD-9). O tapa manda o sinal direto e não chama o `mudanca_no_corpo`. Mas o estresse que ele deixa pode ser tirado por um carinho depois, e esse carinho credita a redução à última decisão: um caminho indireto | o sinal do carinho depois de um tapa é medido (5.4). O medo da mão (CD-5) corta o carinho e puxa para o outro lado. Os dois efeitos saem juntos, e nenhum vira gate |
| R-4 | **O acoplado cuida pior** (achado da validação única) | a 3.5: os acoplados nunca se comparam com malha fechada, os dois lados vão à mesma fonte, e o cuidado só se lê em malha fechada |
| R-5 | **As viradas de limiar da química.** Inteiros exatos contra floats de hoje mudam uma comparação, a rng da política desalinha e a vida segue outra (tarefa, seção 3) | é o G-HOJE (b), por distribuição, com margem e N próprios. O G-HOJE (a), por tick, é teste da tarefa |
| R-6 | **A calibração tocar o primário** | a grade roda só o P0-c, e a regra não lê a `BE` do P1 nem contraste. O piloto só dá margens e N |
| R-7 | **O teto.** No N3 os pesos foram ao teto em 20 de 20 vidas, com o sinal de sentido fixo | com o corpo o sinal de brincar muda de sentido conforme o tédio, o que pode aliviar o teto. As vidas no teto saem relatadas. O ponto não se recalibra |
| R-8 | **O dono muda com os gestos.** O `DonoComGestos` troca elogio por carinho, e o carinho tem efeito no corpo e no humor | o primário compara braços com o mesmo dono. O G-HOJE usa os donos de sempre, para falar da vida de hoje |
| R-9 | **A capacidade do A cresce.** São 126 pesos a mais (~890, contra 763) | é registrado. A comparação de capacidade da C-3 não é refeita aqui |
| R-10 | **A consequência atrasada fica sem crédito.** O tédio que volta a subir não pesa em nenhuma decisão | é o desenho da tarefa (seção 9), declarado. Um pet que planeja é a resposta, fora deste plano |
| R-11 | **O custo.** São 104 vidas por unidade, até 5.200 na validação com N = 50 | o custo medido no piloto vai no adendo. Se passar do teto de tempo que o Matheus der, o K cai e o poder sai declarado |
| R-12 | **A tentação pós hoc.** Há muitas medidas por dono, mundo e drive | só os gates da seção 8 decidem |

## 10. Sementes

| uso | faixa | bases |
|---|---|---|
| calibração e piloto | **33101…33505** | 33101, 33202, 33303, 33404, 33505 (K = 4) |
| validação | **34101…34505** | 34101, 34202, 34303, 34404, 34505 (K do adendo) |

**Conferências feitas em 2026-10-07 no `origin/main` (`d630632`) e em todos os branches remotos:**
- as duas faixas estão fora de `FAIXAS_RESERVADAS` e da `FAIXAS_QUEIMADAS` (`experiments/bancada_v2.py`);
- elas também ficam fora da 23101…27505 (leitura parcial) e da 31101…32505 (mundo físico, ainda não registrada lá);
- `git grep` das dez bases em `docs/`, `experiments/`, `tests/` (fora os gabaritos), `digilab/`, `web/app/` e `CLAUDE.md` não acha nenhum
  uso.

**Quem registra:** a bancada (etapa 8 da tarefa, chat D) põe as duas faixas em `FAIXAS_RESERVADAS` com a fonte deste plano, e o teste de
colisão das unidades passa a cobrir o prefixo `"corpo"`.

## 11. Artefatos e reprodução

- **As pastas:** `artifacts_v2_corpo/calibracao/` (`grade.jsonl`, `escolha.json`, `piloto/`, `sensibilidade_tapa.json`) e
  `artifacts_v2_corpo/validacao/`. Cada uma traz:
  - `meta.json`, com o sha256 de `corpo.py`, `config.py`, `lobos.py` e `engine.py` e a versão do Python;
  - `medidas.json`, `resultado.json` e as vidas em `vidas/*.jsonl`.
- **As configs:** `experiments/configs/v2_corpo/{calibracao,validacao}.json`, com o campo `"plano"` apontando para este arquivo.
- **A recusa:** a run se recusa a rodar se a pasta de saída já existe.

## 12. Decisões do Matheus

**DECIDIDAS em 2026-10-07: PCD-1 a PCD-7, todas como recomendado** (a coluna "recomendação" é o que vale).

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| PCD-1 | A medida primária e o mundo dela | **`BE` nos dias 8 a 14, no mundo `bola`**, com o `padrao` como secundário | só o `padrao`: brincar sem bola reduz pouco o tédio (−45000), e o teste fica fraco no lugar onde o corpo foi desenhado para agir |
| PCD-2 | As margens | **metade** da distância do pet parado para o efeito; **um quarto** do que o P0 deixa para o cuidado; **metade** delas no G-HOJE (b) | margens largas no cuidado deixam passar um pet pior de cuidar; margens estreitas pedem N acima do teto |
| PCD-3 | O primário em malha fechada, e o acoplado duplo à mesma fonte como secundário | **sim** (3.5) | primário acoplado: o pet do produto tem dono reagindo. Acoplado contra malha fechada: repete o erro do achado da validação única |
| PCD-4 | A calibração só com o P0-c, pela faixa dos drives e pelo equilíbrio do sinal | **sim** (6.2) | calibrar com o P1 ajusta o corpo a favor do primário |
| PCD-5 | O bloco do tapa só no mundo `bola`, e os efeitos do tapa sem gate | **sim**: os efeitos no corpo são construídos pelas regras, e a decisão do tapa já foi tomada (S-2) | com gate: testa-se o que a regra garante. Nos dois mundos: dobra o custo sem pergunta nova |
| PCD-6 | O `recompensa_tapa` | **fica no valor da bronca** (CD-10). A calibração só mede ½× e 2× como sensibilidade | mudar pelo resultado da calibração tira a comparação com a bronca da pesquisa, que a CD-10 quis manter |
| PCD-7 | As faixas de sementes | **33101…33505** (calibração e piloto) e **34101…34505** (validação) | uma colisão tira o "novo" das unidades |

## Adendo 1 (2026-10-07, antes de qualquer run): a DS-6 (a generalização do tapa) e a DS-4 (o tédio pela variedade)

As duas foram decididas pelo Matheus em 2026-10-07 (`docs/DEFINICOES_V2_SEIS_PERGUNTAS.md`, seção 9). Fontes:
- a seção 6 das definições (a DS-6);
- a seção 17 de `docs/TAREFA_V2_CORPO_DRIVES.md` (a DS-4).

Nenhuma run foi feita. O adendo só acrescenta e ajusta. As predições PR-H a PR-5, os gates da seção 8, as margens e as PCD-1 a PCD-7 não
mudam.

### A1.1 A inclinação da generalização do tapa (DS-6, só descritiva)

**A pergunta.** Quando o tapa pune uma fruta só, ele afasta o pet só dela ou de todas? É a quarta medida do tapa (definições, seção 6), ao
lado do medo, do estresse e do vínculo. Ela diagnostica o achado 3: no cérebro C, a bronca numa fruta valeu para todas
(`docs/RESULTADO_V2_COMPARACAO_CEREBROS.md`).
- **Rótulo:** SEM APOIO DIRETO.
- Ghirlanda e Enquist 2003 e Dymond et al. 2015 só têm o título conferido e não sustentam o conteúdo.
- Que um estímulo no corpo permita um gradiente não plano é leitura da revisão, SEM FONTE.

**O bloco novo (G, generalização):**

| braço | regime | mundo | dono |
|---|---|---|---|
| **P1-c-tapaX** | corpo | `iguais_frutas` | `DonoComGestos` sem tapa, mais o **tapa na fruta X**: um `tapa` no primeiro passo do dono depois de cada consumo de X, dentro do orçamento e contando como contato (CD-6) |
| **P1-c-frutas** | corpo | `iguais_frutas` | `DonoComGestos` sem tapa |

- **A fruta X:** sorteada uma vez por vida por `derivar_semente("tapa-fruta", semente)`, uniforme entre as três, sem olhar a preferência
  inata. É a regra do N7-6 com outra rng.
- **O mundo `iguais_frutas`:** as três frutas têm o mesmo efeito, então o único sinal aversivo ligado a uma fruta é o tapa.
- **O cérebro:** o A da montagem completa, com a memória das frutas no ganho do ponto da K2.
- **O sinal:** o tapa chega pelo sinal direto (CD-10). A dor, o susto e o estresse ficam no corpo (CD-9).
- **O cérebro C** entra só se tiver os ganchos do corpo (tarefa, seção 11: "opcionais"). Sem eles, fica fora, com o registro.
- **O custo:** 2 braços × 4 donos = **8 vidas por unidade** (o total vai de 104 a 112).

**As medidas,** nos dias 8 a 14, por unidade e com IC por bootstrap:

| medida | definição |
|---|---|
| queda de p(comer \| só f) | p(comer \| só a fruta f no cenário) no P1-c-frutas menos no P1-c-tapaX, para f = X e para cada f ≠ X |
| queda do peso da escolha | o peso aprendido da escolha de f no fim da vida, no P1-c-frutas menos no P1-c-tapaX, para f = X e f ≠ X |
| **inclinação** | (queda média nas não punidas) / (queda na punida), para cada uma das duas medidas acima. **0 é específico; 1 generaliza tudo.** Sai a inclinação, e não o valor numa fruta (definições, seção 6) |

- **Sem gate e fora do Holm.**
- **Quando a queda na punida não é positiva,** a inclinação sai "indefinida" naquela unidade e é contada à parte: o tapa não pegou nem na
  fruta punida.

### A1.2 O tédio pela variedade recente (DS-4)

**A regra nova da tarefa (seção 17):**
- o corpo guarda as últimas `janela_tedio` atividades: bola, brincar, explorar e dono brinca;
- a redução da atividade a é `div_arred(base_a × (J − r_a), J)`, com r_a as repetições dela na janela antes desta;
- **explorar passa a reduzir o tédio,** com a base −90000.

**A decisão sobre a `janela_tedio`: fica fixa em 8, fora da grade.**

**A regra (escrita agora):** um parâmetro só entra na grade da 6.1 se o objetivo da calibração conseguir identificá-lo separado dos outros.
- O objetivo é a faixa dos drives no **P0-c**, e o P0 escolhe as atividades pela mistura fixa do instinto. A variedade dele não muda com
  a janela.
- No P0-c, a janela e o `m_reduz` mexem do mesmo jeito no tédio médio: os dois escalam a redução média por atividade. A faixa não separa um
  do outro.
- Calibrar a janela pelo efeito na variedade pediria olhar o P1, que a 6.2 proíbe (PCD-4).
- Então a janela fica em 8 (o PROPOSTO da tarefa), e o `m_reduz` absorve a escala.

**Sensibilidade (descritiva):** no ponto escolhido, o P0-c roda também com a janela em 4 e em 16. São 2 × 8 = 16 vidas por unidade, só na
calibração. Sai a fração do tempo acordado com o tédio ≥ 0,75 em cada janela. Nada é escolhido por ela.

**O que muda na grade (6.1):**
- **o `m_reduz`** passa a multiplicar as bases da regra nova: bola −135000, brincar −45000, explorar −90000 e dono brinca −90000. Ele também
  multiplica as do carinho, como antes;
- **as subidas** não mudam (+450 por tick acordado).

**O que muda na faixa (6.2):**
- **a faixa do tédio continua [0,10; 0,50]** (a fração do tempo acordado com falta ≥ 0,75 no P0-c);
- **com a regra nova, o tédio do P0-c deve ficar mais alto** que pela regra por tempo, porque o instinto repete atividades. SEM FONTE para
  quanto: a calibração mede. Se a faixa só fechar no `m_reduz` = 2, a regra de escolha já resolve, porque não muda;
- **nada mais muda** na regra de escolha, nem no passo 3 (o `w_novos`).

**A conta de exemplo (seção 9 da tarefa), com a regra nova.** O pet brinca com a bola com o tédio em 0,75 e o cansaço em 0,20, ganho 4. A
conta foi conferida em Python, com o `div_arred` da tarefa:

| repetições da bola na janela antes desta (r) | redução do tédio | sinal f |
|---|---|---|
| 0 | 135000 | **+1440** (a conta da tarefa) |
| 1 | 118125 | +1298 |
| 4 | 67500 | +798 |
| 7 | 16875 | +189 |
| 8 | 0 | **−34** (só o cansaço, o de hoje) |

Repetir a bola leva o sinal de brincar de volta ao N3. Alternar devolve a base.

**O que muda no texto do plano:**
- **o R-2** dizia "explorar continua sem drive que o pague". Com a DS-4, explorar reduz o tédio pela variedade, e a `BE` pode subir pelos
  dois lados. As ações continuam saindo separadas (5.1);
- **um descritivo novo (5.3):** a **variedade** das atividades de tempo livre do P1-c e do P0-c, como o número de atividades distintas na
  janela, médio por decisão. Sem gate. Mostra se o pet que aprende varia mais que o instinto;
- **a PR-5 e o G-TED** seguem iguais (o tédio médio).
- **um risco novo, R-13:** com a variedade pagando, o pet pode aprender a alternar só por alternar. A `BE` subiria sem o pet "querer"
  brincar. O descritivo da variedade e as ações separadas mostram isso, sem gate.

### A1.3 O que fica igual

Ficam como estão:
- as sementes (33101…33505 e 34101…34505);
- as margens e o N da seção 7;
- os gates e a regra de decisão da seção 8;
- as PCD-1 a PCD-7.

O bloco G entra na validação e no piloto, este só para medir o custo. O custo da calibração sobe 16 vidas por unidade (a sensibilidade da
janela), e o da validação, 8 vidas por unidade (o bloco G).

## Adendo 2 (2026-10-07, antes de qualquer run): a dominância de um drive no sinal (D-4)

Decisão D-4 de `docs/DEFINICOES_CORPO_V2.md` (seção 3, #227 e #228): os `w_d` ficam fixos em 1, e o risco de um drive dominar o sinal é
**medido antes** de pôr qualquer peso dinâmico.

**Status:** PROPOSTO. Nenhuma run foi feita. Este adendo não muda:
- as predições PR-H a PR-5 nem os gates da seção 8;
- as margens nem o N;
- as sementes;
- as PCD-1 a PCD-7 nem o adendo 1.

**O que se cita, e em que nível:**
- **Keramati e Gutkin 2014** (`10.7554/eLife.04811`), só pelo resumo: a recompensa é a redução da distância do estado interno ao ponto de
  ajuste.
- **Roijers et al. 2013** (`10.1613/jair.3987`), só pelo resumo: converter vários objetivos num escalar pode ser impossível, inviável ou
  indesejável, conforme a função de escalarização.
- **Nada mais sustenta o que segue.** Os limiares e a janela são PROPOSTOS, SEM FONTE.

### A2.1 Por que medir, e não presumir

O sinal (tarefa do corpo, seção 9) é `D = Σ w_d · falta_d²`, com o `w_d` de cada drive (1 nos de hoje, `w_novos` nos novos, pela 6.2).
- O efeito marginal de cada drive é `2 · w_d · falta_d`: ele cresce com a própria falta. Então um drive saciado já pesa menos, mesmo com os
  pesos fixos. A leitura é nossa, das definições, seção 3.
- O que a forma quadrática não garante é o equilíbrio na vida: um drive que fica em falta alta a vida toda (o tédio de um pet que não
  brinca, por exemplo) pode tomar quase todo o sinal. Aí o aprendiz otimiza um drive só.
- **A D-4 decidiu medir isso antes de pôr um peso dinâmico,** que seria mais um parâmetro livre.

**A diferença para a 6.2, passo 3.** Lá o `w_novos` é escolhido pela parcela do **grupo** dos drives novos no sinal, nas vidas do P0-c.
Aqui a medida é **por drive**, por decisão, nas vidas de todos os braços, e o P1 entra. A 6.2 não muda.

### A2.2 A medida

**Em cada decisão com sinal**, isto é, com `D_antes ≠ D_depois` na janela da própria ação (seção 9 da tarefa):
- a contribuição de cada drive é `c_d = w_d · (falta_d,antes² − falta_d,depois²)`, em inteiros na escala S (a mesma conta dos canais);
- **a parcela do drive** é `p_d = |c_d| / Σ_e |c_e|`.

**Por que o valor absoluto.** Numa mesma ação, um drive pode subir e outro descer: brincar reduz o tédio e aumenta o cansaço. Com o sinal,
a soma `D_antes − D_depois` pode ficar perto de 0 e a fração explodir. Com o valor absoluto, `p_d` fica entre 0 e 1 e soma 1 por decisão.
A contribuição com o sinal (`c_d`) também sai, ao lado.

**Os drives:** os que estão no sinal da decisão.
- `fome`, `desconforto` e `cansaco` sempre;
- `tedio`, `solidao`, `estresse` e `dor` com os drives novos;
- `tristeza` só no consumo de fruta (bloco G).

**Os cortes:**
- **por braço:** P1-c, P1-q, P1-c-tapa, P1-c-tapaX e P1-c-frutas;
- **por condição:** mundo `bola` e `padrao`;
- **por tipo de decisão:**
  - **tempo livre** (regras `tempo_livre` e `bola_no_cenario`): onde o aprendiz escolhe entre vários candidatos;
  - **o resto** (as regras urgentes e a fome moderada): relatado à parte;
- nos dias 8 a 14, como as outras medidas, e na vida toda como descritivo.

**A mesma conta como sonda no P0-c e no P0-q.**
- O P0 não aprende, mas o sinal pode ser recalculado sobre os receptores antes e depois de cada ação, como na 6.2, passo 3.
- Ele mostra a dominância **que o corpo traz**, sem o comportamento aprendido. A diferença P1 − P0 mostra a que o aprendizado acrescenta (um
  pet que aprende a brincar mais muda as faltas).

**A referência de hoje:** o P1-q (a química sem drives novos) dá a dominância entre fome, desconforto e cansaço. É o pet do N3, para
comparar.

### A2.3 O critério de "domina" (escrito agora)

**Por decisão:** o drive d **lidera** a decisão se `p_d ≥ 0,80`, isto é, se os outros juntos dão no máximo um quarto do que ele dá.

**Por unidade:** `f_d` é a fração das decisões de tempo livre com sinal em que d lidera, nos dias 8 a 14.

**Na condição:** o drive d **domina** se o limite inferior do IC95 de `f_d` (bootstrap sobre as unidades, 10.000 reamostragens, semente
4242) passa de **0,50**. Ou seja: com confiança, um drive só responde por mais da metade das decisões de tempo livre.

**A justificativa** (SEM FONTE; é a leitura do desenho):
- **Por que olhar a decisão inteira.** Cada ação mexe em poucos drives: comer na fome, brincar no tédio e no cansaço. Então é normal um
  drive liderar uma decisão. Isso não é dominância. Num corpo equilibrado, drives diferentes lideram decisões diferentes, conforme a ação, e
  nenhum passa da metade.
- **Por que 0,50.** Com cinco a sete drives no sinal, um passar da metade das decisões de tempo livre quer dizer que o aprendiz, ali,
  aprende quase só por ele.
- **Por que 0,80.** Liderar exige que o drive valha quatro vezes o resto da decisão. Um corte de 0,50 contaria decisões divididas entre
  dois drives.
- **O critério vale no P1-c, no mundo `bola`,** o braço e a condição do primário. Nos outros braços e no `padrao`, a mesma conta sai como
  descritivo.

**Fixos antes da run:** os dois limiares (0,80 e 0,50) e a regra do IC. Não mudam no piloto.

### A2.4 Se dominar: o braço P1-cw (peso pela janela recente)

**O braço:** P1-cw, o P1-c com o peso de cada drive dependendo da falta recente dele. É braço do plano, não um ajuste: roda sempre na
validação (A2.5) e não muda o P1-c.
- **A janela:** as últimas `J` decisões (PROPOSTO: 32, 8 h acordado). Nela, `m_d` é a média da `falta_d` lida pelo receptor, na escala S,
  em inteiros (`div_arred`).
- **O peso:** `w_d,janela = max(div_arred(S, 4), S − div_arred(3 · m_d, 4))`, multiplicado pelo `w_d` fixo (`div_arred(w_d · w_d,janela,
  S)`):
  - com o drive sempre saciado na janela (`m_d` = 0), o peso é o de hoje;
  - com o drive sempre em falta total (`m_d` = S), cai a um quarto;
  - o piso de um quarto impede que um drive suma do sinal.
- **O peso fica fixo dentro da decisão:** o mesmo `w_d,janela` entra no `D_antes` e no `D_depois`, e o sinal continua uma diferença. A
  janela anda depois da decisão.
- **As urgências não se perdem.** Um drive em falta alta tem o peso reduzido no aprendizado. Mas as regras urgentes do instinto (fome ou
  higiene abaixo de 0,25, exaustão) decidem por um candidato só, e não passam pelo aprendizado. O risco R-1 continua medido pela privação.
- **O que precisa existir:**
  - no cérebro A (B): uma chave em `ConfigConsequencia`, por exemplo `pesos_janela`, desligada por padrão; desligada, é o P1-c byte a byte;
  - na bancada (D): o braço P1-cw.

### A2.5 O lugar no desenho

**A medida de dominância é só descritiva:** fora do Holm e sem gate. O critério da A2.3 é uma **regra de leitura**, escrita antes, e não
um teste do plano.

**O braço P1-cw:** na validação, nas mesmas 8 células do P1-c (4 donos × 2 mundos), modo sem tapa. São **8 vidas por unidade** a mais (o
total vai a 120 com o bloco G do adendo 1). Roda sempre, para o desenho não depender de dado.
- **Com dominância no P1-c (A2.3):** os contrastes P1-cw − P1-c em `BE`, privação e saúde, no mundo `bola`, saem com IC95 como
  **descritivo qualificado**: a resposta à pergunta "o peso pela janela desfaz a dominância sem piorar o cuidado?". Não entram no Holm.
- **Sem dominância:** os mesmos contrastes saem só como descritivo, com a nota "sem dominância a corrigir".
- **No piloto,** o P1-cw roda só para medir o custo.

**O que muda na leitura das predições:**

| caso | leitura |
|---|---|
| **G-PARADO ganha, sem dominância** | a leitura da seção 8 vale como está: o corpo tira o pet do parado com o sinal repartido entre os drives |
| **G-PARADO ganha, com o tédio dominando** | o pet sai do parado porque aprende **quase só pelo tédio**. A leitura fica qualificada: o corpo funciona como um drive só, e o P1-cw diz se o equilíbrio volta sem perder a `BE` |
| **G-CUIDADO falha, com tédio ou solidão dominando** | é o mecanismo do R-1 (o pet que só brinca), agora identificado no sinal. Fica registrado ao lado da leitura da seção 8 |
| **G-PARADO empata ou perde, com o cansaço dominando** | o pet continua parado porque o gasto de energia de brincar e explorar ainda pesa mais que o tédio no sinal. Isso aponta para o `w_novos` da 6.2, e não para o aprendiz |
| **a dominância aparece no P0-c (a sonda) e não no P1-c** | ela vem do corpo, e o aprendizado a desfaz. O inverso (só no P1-c) quer dizer que o comportamento aprendido a criou |

**A dominância também entra nos riscos:**
- o **R-1** (o pet que só brinca) ganha a medida de mecanismo;
- **R-14 (novo):** o peso pela janela pode criar oscilação (o drive em falta perde peso, sobe mais, perde mais peso). O piso de um quarto
  limita isso, e a fração de dias com `f_d` acima de 0,50 no P1-cw sai como descritivo.

### A2.6 Donos de arquivo e artefatos

| peça | dono | o quê |
|---|---|---|
| `c_d` e `p_d` por decisão | **D** (`digilab/metrics.py`, a bancada) | lidos do registro do sinal do cérebro (os canais já separam por drive) ou recalculados dos receptores antes e depois. Os dois têm de bater (teste) |
| a sonda no P0 | **D** | a mesma conta sobre as vidas do P0-c e do P0-q |
| `pesos_janela` | **B** (`lobos.py`, a `ConfigConsequencia`) | o peso da A2.4, desligado por padrão; desligado, o P1-c byte a byte (G2) |
| o braço P1-cw | **D** | na bancada e nas configs da validação |

**As saídas:** `dominancia.json`, ao lado do `resultado.json` da validação e do piloto, com:
- `f_d` por drive, braço, mundo e tipo de decisão;
- a parcela agregada `Σ|c_d| / ΣΣ|c|`;
- a sonda do P0;
- a leitura pela A2.3.

### A2.7 Decisão do Matheus

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| PCD-8 | O critério de dominância e o braço P1-cw | **o critério da A2.3** (lidera com `p_d` ≥ 0,80; domina com o IC95 inferior de `f_d` acima de 0,50, no P1-c do mundo `bola`), **e o P1-cw sempre na validação**, como descritivo qualificado | **critério frouxo:** acha dominância onde há só ações que mexem em poucos drives. **Rígido:** não vê o tédio tomar o sinal. **O P1-cw só se dominar no piloto:** o desenho passaria a depender do dado do P1, que a PCD-4 evita. **Sem o P1-cw:** com dominância, não há como saber se o peso pela janela resolve |

## Adendo 3 (2026-10-08, antes de qualquer run): o Metabolismo energético antes da calibração — ME-1 a ME-7 DECIDIDAS em 2026-10-11

**A decisão do Matheus (2026-10-08):** o Metabolismo energético entra agora, e **a calibração deste plano (seção 6, sementes 33101…33505)
só roda depois dele.** O desenho está em `docs/TAREFA_V2_METABOLISMO.md`. Este adendo segue as recomendações de lá (ME-1 a ME-7), que o
Matheus decidiu em 2026-10-11, todas pela recomendação. Conferido no mesmo dia: a A3.1 é a ME-6, a A3.2 é a ME-7, e o adendo não dá receptor
novo ao cérebro (ME-2), não muda a fome (ME-5) nem o descarte do estômago (ME-4).

### A3.1 Onde o metabolismo entra

- **O bloco G-HOJE (3.1) fica sem o metabolismo.** O regime "química" desse bloco é o de antes: o bloco mede a química dos drives contra
  hoje, e o metabolismo é outra pergunta.
- **O bloco do corpo (3.2), o do tapa (3.3) e os acoplados ganham o metabolismo em todos os braços,** pela ME-6: P0-q, P1-q, P0-c, P1-c,
  P1-q^ac, P1-c^ac, P0-c-tapa, P1-c-tapa, P1-c-tapaX, P1-c-frutas e P1-cw.
- **O G-P0C (seção 8) continua valendo:** o P0-q e o P0-c têm o mesmo metabolismo. O instinto não lê os químicos novos, e o combustível
  depende só das ações e da comida, que são as mesmas. Se o G-P0C falhar com o metabolismo, a run para, como antes.
- **A pergunta, os gates e as margens não mudam.** O metabolismo muda o mundo do bloco do corpo, não o contraste.

### A3.2 O passo 0 da calibração (ME-7), antes da grade da 6.1

- **O que roda:** só o P0-q, com o metabolismo, nas 20 unidades da calibração (bases 33101…33505, K = 4), nas 8 células.
- **A grade:** o gasto (basal e das atividades sobre o combustível) × {½, 1, 2}, partindo dos PROPOSTOS da tarefa (375 por tick
  acordado, 187 dormindo). Uma run por ponto: 3 × 8 × 20 = **480 vidas**. **Substituída pela A3.2b (PCD-9): {¼, ½, 1}, com as mesmas
  480 vidas.**
- **A regra (escrita agora):**
  - fica o ponto mais perto de 1 (pela |log₂|) em que a fração do tempo acordado com a falta de combustível (abaixo de C/4) cai em
    **[0,05; 0,30]**, nas 8 células juntas;
  - a faixa é PROPOSTA, SEM FONTE. A ideia é que a falta aconteça, mas não o tempo todo;
  - **se nenhum ponto passa:** fica o de fração mais perto do centro da faixa, com o registro "não fechou".
- **O que o passo 0 não lê:** o P1, os drives novos e qualquer contraste. Ele roda antes da grade da 6.1, e a grade roda com o gasto
  escolhido fixo.
- **O passo 0 entra no adendo 1 da 6.5,** junto do ponto da grade.

**A3.2b, a grade revista (PCD-9, DECIDIDA pelo Matheus em 2026-10-12, pela recomendação: o mesmo `m_gasto` em {¼, ½, 1}). Ela substitui a
grade {½, 1, 2} da A3.2:**
- **Por que rever:**
  - **a montagem escalou só o basal:** a A3.2 diz "o gasto (basal e das atividades sobre o combustível)", mas a montagem do passo 0
    (#273, `pontos_passo0`) escala só o basal. A `ConfigCorpo` não tinha o fator das atividades, e a falta dele é o nó `gasto_atividades`;
  - **as atividades pesam tanto quanto o basal:** o B mediu (#271, descritivo, sementes dos testes, vidas de 3 dias, sem artefato no
    repositório) que elas gastam ~240 por tick contra os 375 do basal, e que, com os números PROPOSTOS, a falta fica ligada em **18% a 58%
    dos ticks**. Escalar só o basal deixa de fora quase 40% do gasto;
  - **a fumaça do D bate com isso** (#273, semente 202, 2 dias): a fração do tempo acordado com falta foi de 0,30 a 0,39.
- **A proposta:**
  - **um multiplicador `m_gasto`**, o mesmo nos dois gastos sobre o combustível: o basal (375 acordado, 187 dormindo) e o de cada atividade
    (o fator novo, o `gasto_atividades` da `ConfigCorpo`, do B);
  - **a grade:** `m_gasto` ∈ **{¼, ½, 1}**. São 3 pontos e 480 vidas, como antes. O ponto 2 sai e o ¼ entra, porque em 1 a falta já
    passa do teto da faixa nas medidas descritivas, e o 2 só aumenta a falta;
  - **o arredondamento:** os gastos escalados são arredondados por `div_arred`, e o resto é guardado onde a conta não fecha (como a
    vontade). O ½ do basal fica como o D montou (188 e 94); o ¼ fica 94 e 47;
  - **o cansaço não muda:** as atividades continuam somando ao cansaço o número de hoje. O multiplicador mexe só no combustível (ME-1,
    ME-3).
- **A regra não muda:** a faixa [0,05; 0,30], o ponto mais perto de 1 pela |log₂|, o empate pelo menor gasto e o "não fechou" pelo centro
  da faixa.
- **O uso das medidas descritivas para escolher a grade** não lê o primário nem as sementes da calibração. Elas só mostram onde a grade
  tem de estar.

**A3.2c, o passo 0 rodado (2026-10-12/13, autorizado pelo Matheus; antes da grade da 6.1): `m_gasto` = ½, "não fechou".**
- **A run:** `python experiments/bancada_v2.py --passo0 --config experiments/configs/v2_corpo/calibracao_passo0.json --saida
  artifacts_v2_corpo/calibracao/passo0`, no commit `d68f64b`: o P0-q, as 20 unidades (bases 33101…33505, K = 4, prefixo `corpo`), as 8
  células, 14 dias; 480 vidas, todas gravadas e rejogadas do disco bit a bit; 57 min num processo. Os números saem de
  `artifacts_v2_corpo/calibracao/passo0/passo0.json` (e o `meta.json` de cada ponto, com os sha256).
- **A fração do tempo acordado com a falta de combustível, nas 8 células juntas:**

  | `m_gasto` | basal (acordado/dormindo) | atividades | ticks acordado | com falta | fração |
  |---|---|---|---|---|---|
  | ¼ | 94 / 47 | ¼ | 2.187.300 | 0 | 0,0000 |
  | ½ | 188 / 94 | ½ | 2.187.090 | 832 | 0,0004 |
  | 1 | 375 / 187 | 1 | 1.846.605 | 905.331 | 0,4903 |

- **A regra (A3.2, sem mudança):** nenhum ponto cai em [0,05; 0,30]. Fica o de fração mais perto do centro da faixa (0,175): o ½
  (distância 0,1746, contra 0,1750 do ¼ e 0,3153 do 1), com o registro **"não fechou"**.
- **O gasto fixo da grade da 6.1 em diante:** `gasto_basal_acordado` 188, `gasto_basal_dormindo` 94, `gasto_atividades_num/den` 1/2.
- **O que isso quer dizer, só como leitura:** com o gasto pela metade, a falta quase não acontece (0,04% do tempo acordado); com o gasto
  inteiro, ela fica ligada em metade do tempo. A grade salta por cima da faixa, e o metabolismo, no ponto escolhido, quase não pesa no
  cansaço. Nada foi reajustado olhando o resultado; uma grade mais fina entre ½ e 1 seria decisão do Matheus.

### A3.3 O que sai a mais (descritivo)

Por braço e célula:
- a fração do tempo acordado com a falta;
- o combustível e a reserva no fim de cada dia;
- as vezes em que a falta disparou;
- no P1-c, o tempo entre comer e brincar.

Só relato. Nenhum gate novo.

### A3.4 O custo

O passo 0 soma 480 vidas às 1.440 da grade. O piloto e a validação não mudam de tamanho.

### A3.5 Decisões

São as ME-1 a ME-7 da tarefa, mais a PCD-9, **DECIDIDA em 2026-10-12, como recomendado:**

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| PCD-9 | A grade do passo 0 (A3.2b) | **DECIDIDA em 2026-10-12: o mesmo `m_gasto` no basal e nas atividades, em {¼, ½, 1}**, com a regra da A3.2 sem mudança. As outras opções: **(b)** {½, 1, 2}, o exemplo do coordenador; **(c)** {¼, ½, 1, 2}, com 4 pontos e 640 vidas; **(d)** duas grades, uma por gasto, com 9 pontos e 1.440 vidas | **(b):** se o ½ ainda passar de 0,30, o passo 0 sai "não fechou" e o pet vive boa parte do tempo em falta. O ponto 2 quase certamente não serve. **(c):** custa 160 vidas a mais por um ponto que as medidas já descartam. **(d):** o triplo do custo, para separar duas fontes que a pergunta do plano não separa. **Só o basal, como está montado:** com ~240 de atividades fora da grade, o ponto escolhido não controla a falta |
