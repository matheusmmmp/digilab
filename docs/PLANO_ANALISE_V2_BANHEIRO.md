# Plano de análise — V2: o banheiro, o carinho e o limpador (W-PLANO-BANHEIRO)

Status (2026-10-07): **PROPOSTO**, registrado **antes de qualquer run**. **PB-1 a PB-5 DECIDIDAS pelo Matheus em 2026-10-07, todas pela
recomendação** (seção 12). Tarefa: `docs/TAREFA_V2_BANHEIRO.md` (#219), com BN-1 a BN-6
DECIDIDAS. É a etapa 0 da tarefa.

**Regras deste plano:**
- Os números novos são PROPOSTOS, SEM FONTE, salvo onde citam um artefato.
- O que não está aqui é descritivo pós hoc.
- Nada se ajusta olhando a validação, que roda uma vez só.
- Nenhuma alegação de novidade.

## 1. A pergunta

**Em quantos dias o pet passa a fazer as necessidades no banheiro em cada braço do 2 × 2** (carinho depois do banheiro × limpador)?

| braço | limpador | carinho depois do banheiro |
|---|---|---|
| B00 | não | não |
| B0C | não | sim |
| BL0 | sim | não |
| BLC | sim | sim |

- **O cérebro:** o A no **P1**, no ponto da K2 com a montagem completa.
- **A referência:** o **P0** (o instinto, sem aprender) nos quatro braços. Ele mostra quanto o pet acerta sem aprender.

**Declarado agora, pela seção 5b da tarefa: "o carinho ensina mais que o limpador" é requisito de desenho.**
- Ele é garantido pelo **G-CAR**, um gate de mecanismo da tarefa (o sinal do carinho vale pelo menos 3 vezes o do limpador nos estados de
  referência).
- Por isso, **B0C chegar ao critério antes de BL0 não conta como achado.** O plano não testa essa ordem; só a relata, com o rótulo
  "por desenho".
- **O que se mede:**
  - quantos dias cada braço leva;
  - se o carinho ensina alguma coisa (B0C contra B00) e se o limpador ensina alguma coisa (BL0 contra B00);
  - se o carinho perde força com o uso.

**O que se espera do B00, por construção, e não como predição testada:** sem limpador e sem carinho, o lugar não muda a consequência
imediata (tarefa, seção 3). A diferença que sobra é atrasada e fica sem crédito na janela imediata. O B00 é o piso.

## 2. O mundo, o corpo e o dono

| item | valor | fonte |
|---|---|---|
| mundo | o físico (`MotorMundo`) com o banheiro (células x 0 a 3, y 0 a 5 da casa), no `m` escolhido pela calibração do plano do mundo | `docs/TAREFA_V2_BANHEIRO.md`, seção 3; `docs/PLANO_ANALISE_V2_MUNDO_FISICO.md`, seção 6 |
| corpo | com os gestos (`ConfigCorpo.gestos`) e os drives novos, no ponto do adendo 1 do plano do corpo. A curiosidade segue o que esse plano decidir para o mundo físico (seção 3.4 dele) | `docs/PLANO_ANALISE_V2_CORPO_DRIVES.md` |
| o conforto (BN-6) | o químico novo do carinho, com os números da calibração (seção 6) | tarefa, seção 10 |
| dono | o **atencioso**, com o `DonoComLugar` do mundo, nos quatro braços, sem bronca nem tapa | tarefa, seção 6 |
| carinho | o `DonoCarinhoBanheiro`: um `acariciar` no primeiro passo do dono depois de cada alívio dentro do banheiro, **fora do orçamento** (BN-2) | tarefa, seção 5 |
| limpador | a chave `ConfigBanheiro.limpador` | tarefa, seção 3 |
| orçamento | 16 interações por dia (o 224 em 14 dias da V2), igual em toda duração | o de toda a V2 |
| morte | desligada | — |

**O acoplado não entra.** O contraste é entre braços com o mesmo dono reagindo, em malha fechada. O carinho fica fora do orçamento, então
o cuidado de base é o mesmo nos quatro. É a regra dos planos do mundo e do corpo (nenhum acoplado contra malha fechada), e aqui não é
preciso nenhum: nenhum braço tira o cuidado do outro.

**As dependências:** este plano só roda depois de quatro coisas:
- o mundo e o corpo na `main`, com os adendos deles;
- as etapas 1 a 3 e 5 da tarefa do banheiro;
- o G-CAR passando (seção 6).

## 3. Unidades e vidas

- **A unidade:** a semente derivada por `unidades_derivadas(bases, K, prefixo="banheiro")`. O prefixo novo é registrado pelo D.
- **Por unidade:** 2 cérebros (P0, P1) × 4 braços = **8 vidas**, todas pareadas: mesma semente, mesmo mundo e mesmas quedas de fruta.
- **A estatística:** por unidade, com bootstrap sobre as unidades (10.000 reamostragens, semente 4242, IC95).

## 4. A medida primária: o dia até o critério

**O critério (BN-4):** o primeiro dia d em que a fração dos alívios dentro do banheiro é ≥ 0,80 e continua ≥ 0,80 nos dias d + 1 e d + 2.
- Um dia sem alívio não conta como acerto nem como erro: ele quebra a sequência.
- O P0 e o P1 seguem a mesma regra.

**Tempo até evento, com censura.** T é o dia d do critério. Quem não chega até o último dia possível (d ≤ D − 2, numa vida de D dias) é
censurado.

**O método: a média restrita (RMST) até o horizonte τ = D − 1, com contraste pareado por unidade.**
- **O valor por vida:** T* = min(T, τ). Quem é censurado vale τ.
- **A estimativa por braço:** a média de T* sobre as unidades. O contraste é a diferença de T* por unidade, com bootstrap.
- **Por que este método:**
  - a censura aqui é só administrativa: o fim da vida, igual para todas as vidas e conhecido antes. Com essa censura, a média restrita é
    exatamente a média de T*, sem nenhuma suposição sobre quem não chegou;
  - o pareamento por unidade é o do desenho (mesma semente nos 8 braços), e a diferença por unidade o usa direto;
  - **a mediana de Kaplan–Meier fica indefinida** quando mais da metade é censurada, o que é provável no B00 e em todo P0. A RMST sempre
    existe e se lê em dias.
- **As curvas de Kaplan–Meier** por braço saem como descritivo, com a mediana quando existir e a fração censurada.

## 5. Os contrastes, os gates e a regra de leitura

**Na família de Holm (α = 0,05), no P1:**

| gate | contraste | regra | o que diz |
|---|---|---|---|
| **G-CARINHO** | RMST(B00) − RMST(B0C), em dias | limite inferior do IC95 > 0 | o carinho ensina o banheiro: o pet chega antes com ele |
| **G-LIMPADOR** | RMST(B00) − RMST(BL0), em dias | limite inferior do IC95 > 0 | o limpador sozinho ensina, pela consequência no corpo |

**Fora da família, só relatados com IC:**
- **B0C contra BL0:** "por desenho" (G-CAR). Não conta como achado, qualquer que seja o resultado;
- **a interação:** [RMST(BL0) − RMST(BLC)] − [RMST(B00) − RMST(B0C)]. Ela diz se os dois juntos somam;
- **o aprendizado em cada braço:** RMST(P0) − RMST(P1). O P0 deve ficar perto do censurado em todos os braços (ele nasce preferindo
  `aqui` 4 a 1, tarefa seção 4).

**A leitura:**
- **G-CARINHO passa:** o carinho depois do banheiro ensina. Os dias do B0C são o número que o produto pode usar.
- **G-CARINHO falha:** o carinho, mesmo mais forte que o limpador por desenho, não ensina o lugar no tempo da vida. Isso aponta para o
  crédito (o carinho chega no passo seguinte) ou para o carinho que perde força (seção 7, R-3).
- **G-LIMPADOR passa:** a consequência no corpo sozinha ensina. É o caminho do produto sem botões.
- **G-LIMPADOR falha:** o limpador sozinho não basta no tempo da vida.

## 6. A calibração (só no P0, sem ler o primário)

**A pré-condição: o G-CAR.** A tarefa o define (seção 5b): o sinal do carinho depois do banheiro é pelo menos 3 vezes o do limpador, com a
solidão em 0,2, 0,5 e 0,8 e o desconforto em 0,3.
- É uma conta determinística sobre o corpo, sem vida.
- **Ele roda antes de qualquer vida da calibração.** Se não passa, nada roda.

**6.1 O conforto (BN-6), por conta, sem vida.** O químico de conforto tem dois números: o aumento por carinho e a meia-vida.
- **A grade:** o aumento em {45000, 90000, 180000} e a meia-vida em {60, 240} ticks. PROPOSTOS, SEM FONTE; a ordem de grandeza é a do
  estresse da tarefa do corpo.
- **A regra:** o **menor** aumento que passa o G-CAR nos três estados. No empate, a meia-vida menor.
- **Se nenhum passa:** para tudo e volta ao Matheus (a BN-6).

**6.2 A vontade e o desconforto, em vidas do P0.**
- **Onde roda:** só o P0, no braço B00. O instinto não aprende, e o B00 não tem carinho nem limpador. A escolha não tem como olhar o
  primário, que é do P1.
- **A grade** (multiplicadores sobre os valores PROPOSTOS que o B fixar na etapa 2 da tarefa):
  - `m_w` sobre o `w_vontade`: {½, 1, 2};
  - `m_v` sobre a subida da vontade (+150 por tick e a fração 1/3 da digestão, juntas): {½, 1, 2};
  - `m_d` sobre o desconforto da vontade (+150 por tick acima de 0,75): {½, 1, 2}.

  São 27 pontos × 1 vida por unidade × 20 unidades = **540 vidas**, de 28 dias.
- **A faixa** (PROPOSTA, SEM FONTE), nas vidas do P0:
  - entre **2 e 5 alívios por dia acordado**, em média. Com menos de 2, a fração diária é ruidosa demais para o critério de 0,80;
  - **acidentes** (alívios urgentes) em **no máximo 25%** dos alívios. O resto é decisão, onde o lugar pode ser aprendido.
- **A regra de escolha:**
  - entre os pontos que passam a faixa, fica o mais perto de (1, 1, 1) pela soma de |log₂|. No empate, o de menos acidentes;
  - se nenhum passa, fica o mais perto do centro das duas faixas, com o registro "não fechou". Não há segunda rodada.

**O ponto do A não se recalibra** (M10): ele é o da K2.

## 7. A duração, as margens e o N (pelo piloto)

**O piloto:** no ponto escolhido, os 8 braços em vidas de **28 dias**, nas mesmas 20 unidades da calibração. Ele serve só para a duração,
a margem, o N e o custo. **Não entra como evidência.**
- **O que torna o piloto possível:** o critério do dia d só depende dos dias 1 a d + 2. A vida até o dia D é a mesma, numa vida de D dias
  ou de 28, com o orçamento por dia igual.
- **A consequência:** o piloto de 28 dias, cortado em 14 ou 21, dá exatamente as vidas de 14 e 21 dias.

**A margem `Δ_B`, na escala da medida (dias):** metade da distância entre o P0 e o P1 no braço B0C, a convenção de "metade" da regra 6.3 do
experimento maior: `Δ_B = ½ × [RMST_P0(B0C) − RMST_P1(B0C)]`.
- É a distância do aprendizado no braço desenhado para ensinar mais.
- **Se a distância do piloto for ≤ 1 dia,** o P1 não aprende nem no B0C: a validação não roda, e o plano volta ao Matheus.

**A duração, na grade {14, 21, 28} dias:** fica a **menor** com estas duas condições, no piloto cortado nela:
- no **P1-B0C**, no máximo 25% das vidas censuradas;
- poder simulado ≥ 0,8 para o G-CARINHO detectar `Δ_B` com algum K ≤ 10 por base.

Se nenhuma passa, ficam 28 dias e o poder sai declarado.

**O N:** o menor K de 4 a 10 por base, com poder simulado ≥ 0,8 para o G-CARINHO e o G-LIMPADOR detectarem `Δ_B`, na duração escolhida.
- **O método:** bootstrap das diferenças por unidade do piloto, deslocadas para `Δ_B`, com 2.000 réplicas por K.
- **Se o G-LIMPADOR não chega a 0,8,** ele sai declarado subpotenciado. O K vem do G-CARINHO.

**O adendo 1:** os pontos (6.1 e 6.2), a duração, a `Δ_B`, o K, o poder e o custo entram num commit antes da validação.

**Nota de 2026-10-12 (registro, sem decisão): poucos carinhos no 2 × 2.** O Matheus confirmou em 2026-10-12 que as saídas abaixo seguem **sem
decisão** até haver dado além da fumaça.

**Os números da fumaça.** Vêm da fumaça descritiva do #272: o banheiro perto, P0 e P1, sementes dos testes 101…505, 7 dias, o atencioso
no comedouro, antes de qualquer calibração. Estão no relato do PR, sem artefato no repositório.
- **Alívios dentro:** 5 em 35 no P0 (14%) e 8 em 39 no P1 (21%).
- **Carinhos:** um por alívio dentro, o que dá **1 a 2 por vida em 7 dias**.
- **Ritmo:** cerca de **1 alívio por dia**: 35 e 39 alívios em 5 vidas de 7 dias.

**O que isso implica para a duração, a margem e o K**, na ordem em que o plano os escolhe:
- **A calibração da 6.2 deve se mover:**
  - a faixa pede de 2 a 5 alívios por dia acordado, e a fumaça está perto de 1;
  - com os números de hoje, o ponto escolhido tende a subir a vontade (`m_v`, `m_w`);
  - se nenhum ponto chegar a 2 por dia, a 6.2 sai "não fechou", e o critério de 0,80 fica medido sobre poucos alívios por dia (R-5).
- **O critério da BN-4 fica longe:** sair de ~0,2 dentro para 0,80 por 3 dias seguidos pede muito aprendizado em poucos carinhos. É de
  esperar muita censura no P1-B0C.
- **A duração tende a 28 dias** com o poder declarado: a regra da duração pede no máximo 25% de censura no P1-B0C.
- **A margem `Δ_B` pode ficar ≤ 1 dia,** e então a validação não roda e o plano volta ao Matheus. A regra não muda por esta nota.
- **O K pode não bastar:** o teto do K é 10 por base (até 50 unidades). Com a censura alta, o poder do G-CARINHO pode não chegar a 0,8 nem
  com K = 10, e aí sai declarado subpotenciado. O G-LIMPADOR, com menos sinal, quase certamente fica subpotenciado.

**As saídas, se o piloto confirmar isso** (todas para o Matheus decidir; nenhuma está decidida aqui):
- uma vida mais longa que 28 dias;
- um K acima de 10;
- um critério menos estrito que o da BN-4, que já está decidida e só muda por decisão nova;
- a fração diária de alívios dentro (a inclinação ao longo da vida) como medida primária no lugar do dia até o critério.

Escolher qualquer uma antes do piloto seria ajustar o desenho a uma fumaça de 5 vidas.

## 8. As medidas secundárias (fora do Holm, todas com IC)

| medida | definição |
|---|---|
| fração diária no banheiro | por dia, a fração dos alívios dentro do banheiro, em cada braço e cérebro |
| alívios até o critério | o número de alívios do nascimento ao dia do critério. Censurado, o total da vida |
| acidentes | os alívios urgentes por dia, e a fração deles |
| o cuidado preservado | a privação e a saúde (as definições do N3), em cada braço. Se a privação do P1 num braço passar a do P1-B00 por mais de um quarto da privação do P0 (a margem do plano do corpo, PCD-2), fica registrado |
| a solidão e o sinal do carinho | a solidão no momento de cada carinho e o sinal que ele dá, por dia. **Mostra se o carinho perde força com o uso** (R-3) |
| o sinal do limpador | o sinal de cada alívio no banheiro com o limpador, por dia |
| o peso aprendido do alvo | o peso de `banheiro` contra o de `aqui`, no fim de cada dia |
| chegou tarde | a fração das escolhas do alvo `banheiro` que terminam fora dele (o banheiro além do alcance, R-2), e a distância do pet ao banheiro na decisão |

## 9. Riscos

| # | risco | o que o plano faz |
|---|---|---|
| R-1 | **O pet que segura demais e vira acidente.** O P1 pode aprender a não escolher `aliviar` no tempo livre e esperar a regra urgente, que alivia `aqui` | os acidentes saem por braço e por dia. A calibração prende os acidentes do P0 em no máximo 25%. Se o P1 tiver mais acidentes que o P0 no mesmo braço, fica registrado ao lado do G-CARINHO |
| R-2 | **O banheiro longe demais para o alcance de uma decisão.** O alcance é de 7,5 células (a tarefa do mundo). Da mata, o banheiro fica a mais de 40 células; o pet anda o que dá e alivia onde parou (tarefa, seção 4). Conta como fora, e o carinho não vem | a medida "chegou tarde" separa a escolha certa que chegou tarde da escolha errada |
| R-3 | **O carinho que perde força.** Com carinho a cada alívio, a solidão fica baixa e o sinal cai (tarefa, 5b) | a BN-6 pôs o conforto. A solidão e o sinal de cada carinho saem por dia, e o G-CAR é pré-condição |
| R-4 | **O acoplado, que não entra** | o contraste é entre braços com o mesmo dono reagindo. O carinho fica fora do orçamento, e o cuidado de base é o mesmo (seção 2) |
| R-5 | **O critério estreito com poucos alívios** | a faixa da calibração pede pelo menos 2 alívios por dia, e o dia sem alívio quebra a sequência. O critério é o da BN-4, sem troca |
| R-6 | **A ordem B0C antes de BL0 é por desenho** | é declarada como requisito e não conta como achado (seção 1) |
| R-7 | **As dependências** (o mundo, o corpo e os adendos deles) | o plano só roda com tudo na `main`. Se um ponto daqueles planos mudar, este plano ganha um adendo antes da calibração |
| R-8 | **O B00 como piso** | sem diferença imediata entre os lugares, o P1 no B00 deve ficar censurado. Isso não é testado, só relatado |

## 10. Sementes

| uso | faixa | bases |
|---|---|---|
| calibração e piloto | **37101…37505** | 37101, 37202, 37303, 37404, 37505 (K = 4) |
| validação | **38101…38505** | 38101, 38202, 38303, 38404, 38505 (K do adendo) |

**Conferências feitas em 2026-10-07 no `origin/main` (`789c8ec`) e em todos os branches remotos:**
- as duas faixas estão fora de `FAIXAS_RESERVADAS` e da `FAIXAS_QUEIMADAS`;
- elas também ficam fora das faixas dos planos em curso: mundo 31101…32505, corpo 33101…34505, transferência 35101…36505 (#221) e a
  23101…27505;
- `git grep` das dez bases não acha uso fora dos gabaritos.

**Quem registra:** o D, na etapa 5 da tarefa, põe as duas faixas em `FAIXAS_RESERVADAS` com a fonte deste plano, mais o prefixo
`"banheiro"`.

## 11. Artefatos e reprodução

- **As pastas:** `artifacts_v2_banheiro/calibracao/` (`gcar.json`, `conforto.json`, `grade.jsonl`, `escolha.json`, `piloto/`) e
  `artifacts_v2_banheiro/validacao/`. Cada uma traz `meta.json`, com o sha256 de `mundo.py`, `corpo.py`, `lobos.py`, `config.py` e
  `engine.py`, e as vidas.
- **As configs:** `experiments/configs/v2_banheiro/{calibracao,validacao}.json`, com o campo `"plano"`.
- **A recusa:** a run se recusa a rodar se a pasta de saída já existe.

## 12. Decisões do Matheus

**DECIDIDAS em 2026-10-07: PB-1 a PB-5, todas como recomendado.**

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| PB-1 | O método da medida primária | **a média restrita (RMST) até o fim da vida**, com contraste pareado por unidade; Kaplan–Meier só descritivo | a mediana de Kaplan–Meier: indefinida quando mais da metade é censurada, o que é provável no B00 e no P0 |
| PB-2 | O que se testa | **G-CARINHO (B00 − B0C) e G-LIMPADOR (B00 − BL0), com Holm.** A ordem B0C × BL0 só se relata, como "por desenho" | testar a ordem: o resultado que o G-CAR garante viraria um achado |
| PB-3 | A duração | **a menor de {14, 21, 28}** com no máximo 25% de censura no P1-B0C e poder ≥ 0,8, pelo piloto de 28 dias cortado | fixar 14: se o aprendizado for lento, quase tudo censura e o teste não diz nada |
| PB-4 | A calibração | **só no P0-B00**, pela faixa de alívios (2 a 5 por dia) e de acidentes (≤ 25%); o conforto pela conta do G-CAR, sem vida | calibrar com o P1: ajusta o banheiro a favor do primário |
| PB-5 | As faixas de sementes | **37101…37505** (calibração e piloto) e **38101…38505** (validação) | uma colisão tira o "novo" das unidades |
