# Plano da calibração conjunta do cérebro A e adendo de tamanho de amostra (K1)

Status: **registrado antes de qualquer dado** (2026-10-05). Tarefa `docs/TAREFA_V2_PLANO_CALIBRACAO_CONJUNTA.md`; etapa K1 do
`docs/ROADMAP_V2.md` (revisão 3, decisão M10: montar tudo, calibrar junto, validar uma vez); adendo 1 de
`docs/PLANO_ANALISE_V2_EXPERIMENTO_MAIOR.md`. **Só papel:** nenhuma run, nenhum código. Não usa sementes de validação. Todo número aponta
o artefato; os números de desenho sem fonte estão marcados PROPOSTO; o resto é decisão do Matheus (seção 9).

**O que este plano faz:**
- **calibra uma vez** o cérebro A montado (N5, N6, N7 e os canais, cada um atrás de chave), nas sementes **14101…14505**, com regras de
  escolha registradas antes;
- **fixa como sai o N** da validação única (15101…15505);
- **diz onde se mede** cada contraste de ablação.

As predições 1–5 e a estatística do experimento maior (seções 5 e 6) não mudam (adendo 1).

**O que este plano substitui:**
- **A seção 8.2 do experimento maior** dizia que nada do aprendiz se calibrava ali. A revisão 3 trouxe para cá a calibração que antes era
  de cada nó, e este plano a define.
- **As regras de calibração dos planos do N6 (N6-10) e do N7 (N7-4)** valem como estão.
- **A do N5** (N5-1) é trocada, porque lia uma predição primária (seção 3.4; decisão K-3).

---

## 1. O cérebro A montado: o que fica ligado em cada braço

| peça | chave / parâmetro | P0 | P1 | P2, P2e, P2a | P3 | fonte |
|---|---|---|---|---|---|---|
| teto | `teto` = 16·S (T3) | — (sem aprendizado) | T3 | T3 | T3 | R1, `docs/RESULTADO_V2_REVISAO_APRENDIZ.md` |
| consequência + E2 | `ConfigConsequencia.ganho` | desligado | **ligado** | **ligado** | desligado (o sinal é o dono) | N3, E2 |
| comer vê a fruta | pesos por fruta, prior 0 | prior (= instinto) | aprende | aprende | não aprende (só a consequência mexe) | FRUTA-NO-CENARIO B |
| informação (N5) | `w0_info` | 0 | 0 | **calibrado** | 0 | N5-1 a N5-3 |
| memória (N6) | ganho `g` | 0 | **calibrado** | **calibrado** | **calibrado** | N6-1 a N6-10 |
| pedido (N7) | `w0_pedido` | 0 | **calibrado** | **calibrado** | **calibrado** | N7-1 a N7-10 (só age onde há pedido: o bloco N7) |
| canais (H-R2) | chave dos canais (C4) | desligado | ligado | ligado | desligado (age no sinal de consequência) | C4, ainda não desenhado |

**P0 fica com tudo desligado** (decisão K-1): é o instinto byte a byte, pelo contrato K1 do experimento maior. A memória, a informação, o
pedido e os canais são plasticidade ou entrada aprendida. Ligá-los no P0 tiraria dele o papel de "herdado sem aprender".

**Consequência para as predições:** a plasticidade dos braços P1–P3 passa a incluir a memória e, nos que aprendem pela consequência, os
canais. O que é da memória e o que é dos canais sai das ablações (seção 5), não das predições.

---

## 2. Parâmetros livres

| parâmetro | onde age | grade (PROPOSTA) | fica fixo | origem |
|---|---|---|---|---|
| teto | todos os pesos aprendidos | — | **16·S** | R1 (não se calibra de novo) |
| ganho do P1 | o sinal de consequência (P1, P2) | **{4, 8, 16}** | — | N3 (4, calibrado com teto 1·S, mundo padrão) |
| `g`, ganho da memória | a escolha da fruta | {S/4, S/2, 3S/4} | — | N6-10 |
| `w0_pedido` | a decisão de comer e a escolha da fruta, com pedido | {S/4, S/2, 3S/4} | — | N7-4 |
| `w0_info` | a escolha da fruta, com informação | {S/4, S/2, 3S/4} | — | N5-1 |
| canais | o sinal de consequência | nenhuma, se o C4 respeitar "mesmo total de sinal" (H-R2) | — | seção 2.1 |
| o resto | passo 512, janela de crédito da v1 (traço desligado, R3), `w_fruta` 6, 4 ofertas/dia (R4), espaços da memória 4 + 2, janela de 240 min (informação e pedido), 14 dias, dono atencioso | — | como está na `main` | decisões anteriores |

**Por que a grade do ganho sobe e não desce.** No ponto T3, com ganho 4, o P1 não tem nenhuma vida no teto, mas a deriva ainda cresce no
fim da vida: a razão 14/7 é 2,92 no descasado e 2,64 no casado (`artifacts_v2_revisao/calibracao/T3/resultado.json`,
`celulas.<condição>/P1.razao_deriva_14_7`). Um ganho menor só atrasaria mais. O 16 estava na grade do N3.

### 2.1 Canais (C4, H-R2)

O C4 ainda não está desenhado (rodada 9, chat B). Este plano fixa o que ele precisa cumprir para entrar na calibração:
- **o mesmo total de sinal** que o escalar (H-R2, `docs/research/digibrain/mechanisms/reinforcement.md`): só a representação muda;
- **canais desligados = escalar byte a byte.**

**Se o C4 trouxer um parâmetro livre** (por exemplo, a partilha entre canais):
- ele entra por um **adendo 2 a este plano**, commitado antes da K2;
- é varrido **junto com o ganho**, porque os dois disputam o mesmo sinal;
- a regra de escolha é a mesma do ganho.

**Se o C4 não estiver na `main` quando a K2 começar:** a calibração roda sem canais, e a ablação dos canais fica **não testável**, como o
K2 do experimento maior fazia com a predição 2 (decisão K-6).

---

## 3. Ordem da varredura e regras de escolha (registradas agora)

**Princípio** (o pedido da tarefa):
- **Separados:** parâmetros que agem em decisões diferentes, ou em braços em que os outros estão desligados.
- **Encadeados:** os que disputam a mesma decisão, com o anterior fixado. O segundo é então escolhido com o primeiro já no lugar.

**Por que encadeado e não uma grade cruzada.** Cada regra é uma verificação de manipulação de um parâmetro só. Numa grade cruzada, cada
ponto precisaria de uma regra conjunta, e as vidas se multiplicam: 3⁴ = 81 pontos contra 12 na ordem abaixo.

```
Etapa A (em paralelo; nenhum depende do outro)      Etapa B                Etapa C                      Etapa D
──────────────────────────────────────────────      ───────                ───────                      ───────
A1  g          (bloco N6, aprendizado desligado) ─┐
                                                  ├─► ganho do P1 ───────► w0_info ───────────────────► piloto no ponto escolhido
A2  w0_pedido  (bloco N7, mundo iguais_frutas)   ─┘   (P1 completo,         (P2 completo, com g           (todos os braços, blocos
                                                       com g)                e ganho)                      e ablações) → adendo
```

### 3.1 A1, o ganho da memória `g` (regra N6-10)

- **Onde:** bloco N6, braço MR (memória relevante, aprendizado do lobo de decisão desligado), mundo `descasado`.
- **Por que sozinho:** nesse braço não há sinal de consequência, informação nem pedido, então nada mais disputa a escolha.
- **Regra:** o **menor** `g` em que a fração das sub-decisões com duas frutas ou mais decididas pela memória (sonda contrafactual) tem
  limite inferior do IC 95% > 0,069. O 0,069 é a fração de motivos que citavam memória na v1
  (`artifacts_v1_memoria_espacos/espacos.json`, `fracao_motivos_citam_memoria_total`).
- **Se nenhum passa:** o de maior limite inferior, e o relatório diz que não fechou.

### 3.2 A2, a confiança no pedido `w0_pedido` (regra N7-4)

- **Onde:** bloco N7, braço P0+ped, mundo `iguais_frutas`.
- **Por que sozinho:** o pedido só existe nesse mundo; nos mundos das predições o atencioso não pede.
- **Regra:** o **menor** `w0_pedido` em que o pedido decide decisões de conflito na zona `fome_moderada` com limite inferior do IC 95%
  > 0.
- **Se nenhum passa:** o de maior limite inferior da deferência nessa zona.

### 3.3 B, o ganho do P1

- **Onde:** P1 completo (com `g` de A1 e os canais, se houver), nas três condições (`casado_frutas`, `descasado`, `mutavel`), juntas.
- **Por que depois de A1:** a memória e os pesos aprendidos disputam a escolha da fruta no P1.
- **Regra (o G6 da L1 e do N3):** entre os ganhos com **nenhuma vida no teto**, o que tem a **menor razão da deriva** (dia 14 / dia 7),
  média das três condições. Em empate, o menor ganho.
- **O que não entra:** a `taxa_fruta_ruim` e qualquer contraste com o P0. A razão da deriva diz se o aprendizado assenta dentro da vida;
  não é medida de predição.

### 3.4 C, a confiança na informação `w0_info` (regra nova; decisão K-3)

**Por que trocar a regra do N5.** A regra decidida no plano do N5 (N5-1) escolhia o menor `w0_info` com P2e − P1 na `taxa_fruta_ruim`
inicial acima de 0. Esse contraste é a **predição 4(a)**, primária e dentro da família de Holm do experimento maior. Escolher o ponto pelo
contraste que a validação vai testar puxa a validação a favor dele, mesmo em sementes disjuntas.

**A troca:**
- **Onde:** P2 completo (`g` de A1, ganho de B), mundo `descasado`, dias 1–7.
- **Por que depois de A1 e de B:** a informação disputa a escolha da fruta com a memória e com os pesos aprendidos, e o peso dela aprende
  pela consequência com o ganho escolhido.
- **Regra:** o **menor** `w0_info` em que a fração das sub-decisões com informação vigente decididas pela informação (sonda
  contrafactual: o mesmo `u`, com o termo `w_info` zerado) tem limite inferior do IC 95% > 0,069. É o mesmo piso da memória (A1), para as
  duas entradas não aprendidas da escolha da fruta serem medidas pela mesma régua.
- **Se nenhum passa:** o de maior limite inferior.
- **O que não entra:** nenhum contraste entre braços.

### 3.5 D, o piloto no ponto escolhido

- **Ponto:** fixo pela A, B e C.
- **O que roda:** tudo o que a validação vai rodar (seção 4), nas mesmas unidades de calibração.
- **O que sai daqui:**
  - os contratos K1–K9 conferidos em vida real;
  - o **Δ** (regra 6.3 do experimento maior);
  - os Δ dos blocos N6 e N7 (pelas regras dos planos deles);
  - o **σ²_d** de cada contraste.
- **Nenhum resultado de predição** é lido para decidir algo além disso. Os contrastes do piloto ficam no artefato, como piloto.

---

## 4. O que roda: braços, blocos e ablações

Mesma unidade (genoma, semente) em todos os braços, condições e blocos: o pareamento atravessa os blocos (decisão K-9).

| bloco | braços | mundo | vidas por unidade |
|---|---|---|---|
| **principal** (predições 1–5) | P0, P1, P2, P2e, P2a, P3 | `casado_frutas`, `descasado`, `mutavel` | 18 |
| **só cuidado acoplado** | `P0<P2:sem_ensino`, `P0<P2e:sem_ensino`, `P0<P3:sem_ensino` | os três | 9 |
| **ablações no principal** | P1 sem memória (`g` = 0); P1 escalar (sem canais) | `descasado`, `mutavel` | 4 |
| **bloco N6** (`PLANO_ANALISE_V2_N6.md`) | MR, `M0<MR`, `MT<MR`, `ME<MR` (o M0 em malha fechada é o P0 do principal) | `descasado` | 4 |
| **bloco N7** (`PLANO_ANALISE_V2_N7.md`) | P0, P0+ped, P1+ped, P3+ped, P3, `P0<P3+ped:sem_ensino` | `iguais_frutas` | 6 |
| **referência** (descritiva) | P0, P1, P3 | `padrao` | 3 |
| **total** | | | **44** |

**O controle de capacidade sem lobos** (E6, só no P1 e no P3) **fica fora**: a bancada não tem o cérebro `camada_unica`, que é do N11
(`CLAUDE.md`, seção "V2, BANCADA-EXPERIMENTO"). Ele entra na comparação de cérebros (K3/V2 do roadmap).

### 4.1 Os contrastes de ablação e onde cada um se mede

Todos são **secundários** e ficam **fora** da família de Holm das predições primárias (E8, adendo 1). Cada bloco mantém a família própria
do plano dele, como secundária.

| peça | contraste | onde | medida | plano |
|---|---|---|---|---|
| **N5, informação** | já são as predições 3 e 4 (P1 − P2; P2e − P1; P0 − P2e); sem a peça, o P2 é o P1 byte a byte (G2) | principal, `descasado` | `consumos_ate_metade`, `taxa_fruta_ruim` inicial e final | N5; experimento maior |
| | P2 − P2a (a informação na hora × em momentos sorteados) | principal, `descasado` | idem | N5, seção 6 (descritivo) |
| **N6, memória** | P1 sem memória − P1 completo | principal, `descasado` e `mutavel` | `taxa_fruta_ruim` final (descasado) e depois da troca (mutável) | este plano |
| | `M0<MR` − MR, `MT<MR` − MR, `ME<MR` − MR; G-CITA; G-M1 a G-M3 | bloco N6 | as do plano do N6 (Holm de três, secundária) | N6 |
| **N7, arbitragem** | G-EROSAO, G-MARCA, G-MARCA-E; G-ARB, G-URG, G5 | bloco N7 | as do plano do N7 (Holm de três, secundária) | N7 |
| **canais** | P1 escalar − P1 completo | principal, `descasado` e `mutavel` | `taxa_fruta_ruim` final e depois da troca; a conferência do mesmo total de sinal | H-R2 |
| **teto** | não ablacionado | — | fixo em 16·S (R1) | — |

**Por que as ablações da memória e dos canais ficam só no P1, e não em P2 e P3:**
- no P1 a plasticidade vem de uma fonte só;
- nos outros braços a peça se mistura com a informação ou com o dono;
- dobrar as ablações para cada braço custaria 8 vidas a mais por unidade.

---

## 5. Adendo de tamanho de amostra (E3, seção 7 do experimento maior)

### 5.1 Unidades da calibração

- **Derivação:** `derivar_semente("experimento-maior", b, k)` e `derivar_semente("experimento-maior-genoma", b, k)`, bases 14101, 14202,
  14303, 14404 e 14505.
- **K da calibração = 4 por base, 20 unidades (PROPOSTO):** o mesmo da revisão do aprendiz.
- **Os blocos N6 e N7 usam essas mesmas unidades.** As derivações próprias dos planos deles (`"n6"`, `"n7"`) não são usadas (decisão
  K-9).

### 5.2 Custo estimado

**A conta.** Na revisão do aprendiz, 1 h 50 min rodaram 10 pontos × 120 vidas (`docs/RESULTADO_V2_REVISAO_APRENDIZ.md`, primeiro
parágrafo), cerca de **5,5 s por vida**, todas rejogadas do disco.

| etapa | vidas por unidade | vidas (20 unidades) | tempo estimado |
|---|---|---|---|
| A1 (`g`: 3 pontos) | 3 | 60 | ~6 min |
| A2 (`w0_pedido`: 3 pontos e a referência sem pedido) | 4 | 80 | ~7 min |
| B (ganho: 3 pontos × 3 condições) | 9 | 180 | ~17 min |
| C (`w0_info`: 3 pontos) | 3 | 60 | ~6 min |
| D (piloto: seção 4) | 44 | 880 | ~81 min |
| **calibração inteira** | | **1260** | **~2 h** |

**Validação:** 44 vidas por unidade × N. Com N = 100 seriam 4400 vidas, perto de 7 h; com N = 140 (a ordem de grandeza da v1, seção
7.1 do experimento maior), cerca de 9,5 h. O número real sai do adendo.

### 5.3 O N da validação

1. **σ²_d** de cada um dos seis contrastes primários no piloto (etapa D), com a unidade e o pareamento da seção 6.1 do experimento maior.
2. **N por contraste** = ((z₁₋α + z₀,₈) × σ_d / Δ)², unilateral, α/6 (o passo mais exigente de Holm sobre os seis), poder 0,8. A
   equivalência da predição 5 usa o IC de 90% com a mesma fórmula, α = 0,05 por lado.
3. **Conferência por simulação:** bootstrap das 20 unidades do piloto, como `artifacts_poder/curvas_poder.json`.
4. **N da validação = o maior N entre os seis**, arredondado para cima ao múltiplo de 5. K da validação = N / 5 por base.
5. **As ablações e os blocos N6 e N7 não puxam o N** (decisão K-8). O adendo traz, para cada contraste secundário, o poder que ele tem com
   o N escolhido. Abaixo de 0,5, o contraste é lido como **subpotenciado**, e um resultado nulo dele não refuta nada.
6. **Se o tempo passar do teto da decisão K-10:** o Matheus decide antes da validação, entre reduzir a família, aceitar poder menor
   declarado ou rodar assim mesmo. Nunca depois de ver a validação (regra 7.2.5 do experimento maior).

**Conteúdo do adendo** (commitado no experimento maior antes da validação):
- os parâmetros escolhidos nas etapas A, B e C, com a regra que os escolheu e se a regra fechou;
- Δ e os Δ dos blocos;
- σ²_d e N de cada contraste;
- o N escolhido e as unidades;
- o poder dos secundários;
- o tempo estimado.

**Por que o N é por unidades e não por vidas mais longas.** Na v1 a variância entre unidades dominou: ICC 0,745 e só 0,34% da variância
do estimador vinha das partidas (`artifacts_poder/variancia.json`). Na L1, o braço que aprende teve IC de [0,532; 0,734] com 5 sementes
(`artifacts_v2_l1/validacao/ponto/tarefa.json`).

---

## 6. Riscos registrados antes

1. **A regra do ganho pode não fechar.** No T3 com ganho 4 a razão da deriva do P1 é 2,92 e 2,64 (seção 2). Se nenhum ganho chega a uma
   razão baixa, a regra escolhe a menor mesmo assim. A predição 2 já prevê a leitura **inconclusivo por duração** para o caso de a
   diferença ainda crescer no fim da vida.
2. **Contrato K4 fora da `main`.** O dono do P3 não julga a fruta (`K4_DONO_JULGA_FRUTA = False`, `CLAUDE.md`, seção
   "V2, BANCADA-EXPERIMENTO"). Sem ele, a predição 5 mede só que o P3 não sabe das frutas (E7). Decisão K-11.
3. **Pré-requisitos ainda abertos:** C1 (memória e arbitragem no cérebro), C2 (mundo do pedido), C3 (bancada do N6 e do N7, com o
   `iguais_frutas`), C4 (canais). Sem C1 a C3, a calibração não começa. Sem C4, ela começa sem canais (K-6).
4. **Exposição.** As escolhas com duas frutas ou mais são poucas por vida (4 a 24 no N4, `docs/RESULTADO_V2_N4.md`). As leituras
   "inconclusivo por exposição" dos planos do N5, N6 e N7 continuam valendo nos blocos.
5. **A ordem encadeada pode deixar um ótimo de fora.** Escolher `g` sem a informação e depois `w0_info` com `g` fixo não procura o par
   ótimo. Isso é aceito de propósito: as regras são verificações de manipulação, não de desempenho, e o par ótimo exigiria olhar o
   desempenho.

---

## 7. Ordem e regra de parada

1. C1, C2 e C3 na `main` (e o C4, ou a decisão K-6 vale); o K4, se a decisão K-11 o pedir.
2. Etapas A → B → C → D nas sementes 14101…14505, cada uma pela regra registrada aqui. Um artefato por etapa, em
   `artifacts_v2_experimento_maior/calibracao/{A1,A2,B,C,D}/`.
3. Adendo commitado no experimento maior.
4. Validação (15101…15505), uma vez, pelo orquestrador do experimento maior com os blocos e as ablações da seção 4.
5. A run é refeita do zero, com sementes novas registradas antes, só por erro de execução; nunca pelo resultado. Falha registrada não
   para a V2.

---

## 8. Fora deste plano

- código e runs;
- o desenho dos canais (C4);
- os cérebros B e C (K3/V2);
- outros donos;
- a variedade de frutas (seção 2.1 do experimento maior, só por adendo próprio);
- humanos;
- a web.

---

## 9. Decisões do Matheus

**DECIDIDAS em 2026-10-05: K-1 a K-11 todas como recomendado** (rodada 9, `docs/ROADMAP_V2.md`). O K4 entra antes da K2 (tarefa
`docs/TAREFA_V2_K4_DONO_JULGA_FRUTA.md`); o limite de 12 h da validação vale.

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| K-1 | o que fica ligado no P0 | nada: o P0 é o instinto byte a byte; memória, informação, pedido e canais só nos braços que aprendem | com a memória no P0, ele deixa de ser "herdado sem aprender" e todo contraste com o P0 mede outra coisa |
| K-2 | ordem da varredura | A (`g` e `w0_pedido` em paralelo) → B (ganho) → C (`w0_info`) → D (piloto) | grade cruzada: 81 pontos e regras conjuntas; tudo separado: a informação seria calibrada sem a memória com que ela compete |
| K-3 | regra do `w0_info` | trocar a N5-1 pela fração decidida pela informação > 0,069 (sonda contrafactual), sem contraste entre braços | manter a N5-1 escolhe o ponto pela predição 4(a), que a validação testa |
| K-4 | grade e regra do ganho do P1 | {4, 8, 16}; nenhuma vida no teto e menor razão da deriva, nas três condições juntas | uma grade para baixo atrasa um aprendizado que ainda não assentou (razão 2,92 com 4); escolher pela `taxa_fruta_ruim` lê a predição 2 |
| K-5 | regras do `g` e do `w0_pedido` | as decididas (N6-10, N7-4), sem mudança | trocar agora reabre decisões fechadas sem dado novo |
| K-6 | canais | só entram com "mesmo total de sinal"; parâmetro novo só por adendo 2, varrido com o ganho; sem C4 na `main`, ablação não testável | canais com sinal total diferente confundem representação com escala (H-R2) |
| K-7 | ablações | memória e canais só no P1 (descasado e mutável); os blocos N6 e N7 com os gates dos planos deles; tudo fora do Holm primário | ablar em todos os braços custa 8 vidas a mais por unidade sem pergunta nova |
| K-8 | quem puxa o N | só os seis primários (α/6); os secundários com o poder declarado | os blocos puxando o N podem multiplicar o tempo da validação |
| K-9 | unidades | K = 4 por base na calibração; os blocos N6 e N7 nas mesmas unidades do experimento maior | derivações próprias por bloco quebram o pareamento entre blocos e gastam mais vidas |
| K-10 | teto de tempo da validação | até 12 h de máquina sem nova decisão (PROPOSTO); acima disso, o Matheus decide antes de rodar | sem teto, um N grande trava a máquina por dias; um teto baixo demais corta poder |
| K-11 | contrato K4 (o dono do P3 julga a fruta) | implementar antes da K2 (donos sintéticos, chat A) | sem ele, a predição 5 mede só que o P3 não sabe das frutas, e P2 × P3 mistura canal com conhecimento |
