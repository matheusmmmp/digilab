# Plano de análise — N6: memória de episódios no mundo das frutas (quatro marcos)

> **V2, congelado em 2026-10-30** (tag `v2-final`). O estado em que este documento fica na V3 está em `docs/FECHAMENTO_V2.md`; o
> plano da V3, em `docs/PLANO_V3.md`.

Status: **registrado antes de qualquer dado** (2026-10-04). Tarefa `docs/TAREFA_V2_N6_PLANO.md`; nó N6 do `docs/ROADMAP_V2.md` (R6.2) e
de `docs/ARQUITETURA_V2_VALIDACAO.md` (seção 5); hipóteses H-MEM-001 e H-MEM-02 de `docs/research/digibrain/mechanisms/episodic_memory.md`.
**Só papel:** nenhuma run, nenhum código. Todo número citado aponta o artefato; os números de desenho sem fonte estão marcados PROPOSTO; o
resto é decisão do Matheus (seção 16).

**A pergunta.** Um episódio do mundo das frutas ("comi a fruta X e o humor caiu"), **recuperado** quando a fruta X volta ao cenário, muda a
escolha do pet **com o estado atual igual**, e faz isso **além de uma janela de recência**?

**Os quatro marcos não se provam uns pelos outros** (`episodic_memory.md`):
1. **registrado:** o evento está no log;
2. **codificado:** virou um episódio segmentado;
3. **recuperado:** volta quando é relevante;
4. **causal:** muda a decisão com o estado atual igual.

Cada marco tem o seu gate (seção 7). Passar os três primeiros não diz nada sobre o quarto: hoje a v1 já cumpre 1 a 3 pela história da voz
(`digilab/historia.py`), e a história não decide nada.

**O que sustenta ter o nó, e o que não sustenta:**
- **O precedente (VERIFICADA):** Castro e Gudwin 2013 (`10.4018/jse.2013010102`) acoplam um módulo de memória episódica baseada em cenas à
  arquitetura cognitiva de uma criatura virtual autônoma.
- **O que é só pista:** o corpus do DigiBrain (por exemplo, Sakabe et al. 2025, detecção, codificação e consulta de episódios) fica como
  pista, sem citação como evidência.
- **A regra dos espaços** é regra de engenharia, não modelo de esquecimento (D7 de `docs/DEFINICOES_V2.md`). A explicação do esquecimento
  por competição é contestada (Raaijmakers e Jakab 2011, `10.3758/s13421-011-0131-y`, VERIFICADA).
- **Hipóteses do Digilab:** nada na literatura verificada diz que este pet, com este aprendiz, vai usar um episódio para decidir.
- **Nenhuma alegação de novidade.**

**Não reabre nada.** A memória por espaços da v1 e o resultado dela ficam como estão (`artifacts_v1_memoria_espacos/`).

---

## 1. Pré-requisitos (nada roda antes de estarem na `main`)

| # | o quê | quem | estado em 2026-10-04 |
|---|---|---|---|
| R1 | os lobos veem as frutas e escolhem a fruta pelo lobo de decisão; a E2 | chat B, LOBOS-MUNDO | #141 na `main` |
| R2 | os mundos das frutas na bancada (`casado_frutas`, `descasado`, `mutavel`), o `CalendarioFrutas`, as unidades derivadas, a `taxa_fruta_ruim` por janela | chat D, BANCADA-FRUTAS | #144 na `main` |
| R3 | a bancada cria os lobos vendo o mundo | chat D, `docs/TAREFA_V2_BANCADA_N5.md` | aberta (rodada 6) |
| R4 | a revisão do aprendiz (teto, janela, exposição) | chat B, `docs/TAREFA_V2_REVISAO_APRENDIZ.md` | aberta; só pesa no braço secundário com aprendizado (seção 4.3) |
| R5 | a implementação do N6, descrita nas seções 2 a 4 | a definir | depois deste plano |

A implementação (R5) inclui três peças:
- o episódio das frutas no lobo `memoria_emocao`, em `digilab/policies/lobos.py`, que é do chat B;
- os braços M0, MR, MT e ME na bancada;
- as medidas da seção 6 em `metrics.py`.

---

## 2. O que é um episódio

**Um episódio = um consumo de fruta e o que ele fez ao humor.** Os campos são:

| campo | conteúdo | de onde vem |
|---|---|---|
| `tick` | o tick em que o pet comeu | o registro derivado do `MotorFrutas` |
| `fruta` | `a`, `b` ou `c` | idem |
| `valencia` | humor logo depois de comer − humor logo antes, em unidades inteiras de S: `arred(Δhumor / |efeito_humor_ruim| × S)`, cortada em [−S, S] | os mesmos `antes` e `depois` do `sinal_homeostatico_fruta` (E2) |
| `intensidade` | `|valencia|` | idem |

**Escolhas e por quê:**
- **Só o humor, não a fome.** No mundo das frutas, a nutrição é igual em todas as frutas (`ConfigFrutas.nutricao`). A
  diferença entre as frutas está só no humor (F6), então um episódio com a fome seria ruído igual em todas.
- **O pet não escreve no log.** O log tem só a oferta, que é ação do dono. O consumo e o episódio são registro derivado, refeito pelo
  replay. É a regra de event sourcing de sempre: o marco 1 é "reconstruível do log", não "uma linha nova no log".
- **Fruta neutra:** valência 0. O episódio é codificado, mas não contribui para a escolha.

### 2.1 Onde mora: o lobo `memoria_emocao`

Hoje o lobo `memoria_emocao` só conta eventos e contribui com zero (`MemoriaEmocao.contribuicao`, `digilab/policies/lobos.py`). No N6 ele
guarda os episódios das frutas em **espaços** (D7: só como regra de capacidade de engenharia), com a regra da v1
(`digilab/memoria_espacos.py`):
- **Categoria = a fruta:** no máximo um episódio por fruta em cada prazo.
- **Curto prazo:** `n_curto` 4 espaços, por `d_curto` 12 h; depois o episódio tenta o longo prazo.
- **Longo prazo:** `n_longo` 2 espaços, permanente até ser substituído.
- **Os três números** vêm da `ConfigMemoriaEspacos` da v1, que os registra como PROPOSTO. O N6 os herda sem calibrar.

**Desempate explícito** (sempre pela intensidade original, como na v1):
- **Mesma fruta já no espaço:** a nova substitui a antiga se for mais forte ou igual. Em empate, vence a mais recente.
- **Fruta ausente com os espaços cheios:** a nova substitui a mais fraca se for mais forte ou igual a ela. Em empate entre as mais fracas,
  sai a mais antiga.
- **Senão,** a nova é descartada.

**Consequência do desenho:** no descasado, os efeitos por fruta são constantes (±0,10 ou 0), então o episódio mais recente de cada fruta
substitui o anterior. As ofertas caem às 9 h, 12 h, 15 h e 18 h (`ConfigFrutas.horarios_oferta`). Um episódio das 18 h sai do curto às 6 h
do dia seguinte, antes da primeira oferta. Entre um dia e outro, quem leva a memória é o longo prazo:
- os 2 espaços ficam com os episódios mais fortes, o bom e o ruim;
- a neutra perde a disputa.

**Sem decaimento contínuo:** a ativação da v1 usa `exp`, e os lobos não usam função transcendental (paridade com a web). O esquecimento no
N6 vem só da regra dos espaços. Relembrar, que na v1 reaplica a ativação (candidato da L2 pela D7), fica **desligado** neste nó (decisão
N6-4).

### 2.2 Como chega à decisão

**Só na sub-decisão da fruta** (qual fruta comer), como a informação do N5 (decisão N5-2). Não entra em comer ou não (decisão N6-1).

**Recuperação:** numa sub-decisão com as frutas `presentes`, a pista é cada fruta presente. A recuperação devolve, para cada fruta f, o
episódio de f mais forte entre os dois prazos (em empate, o mais recente) ou nada.

**Contribuição:**
- `m_f = div_arred(g × valencia_f, S)`, inteiro, com `g` o **ganho da memória**, calibrado na seção 9;
- o peso de f na sub-decisão passa a `((w_f + m_f) / S) × incentivo_f`, com o piso de hoje no coeficiente (que só vale com o aprendizado ligado);
- sem episódio de f, `m_f` = 0.

**Por que só na sub-decisão:** escolher entre frutas não mexe na fome, porque a nutrição é igual. A memória fica fora do canal de cuidado
por desenho (a razão da D7 e da D10). Pôr a memória em comer ou não mudaria quanto o pet come, e o G5 deixaria de ser satisfazível.

**Teto do ganho:** `g` < S. Assim um episódio ruim reduz o coeficiente da fruta, mas não o zera: a memória inclina a escolha, não a proíbe,
e a fruta continua amostrável.

**Motivo:** a contribuição `m_f` entra no motivo da sub-decisão como `memoria_emocao`, ao lado do peso, com o episódio recuperado (tick,
fruta, valência). Isso é a base do marco 4 por decisão (seção 6) e da pergunta H-MEM-02 (seção 14).

---

## 3. A recência que já existe no mundo (não é memória do pet)

O `MotorFrutas` já tem duas recências do lado do mundo, iguais em todos os braços:
- a avaliação de uma fruta cai com o consumo recente dela (`meia_vida_recente` 16 decisões = 4 h, `k_saciedade`);
- o incentivo acompanha a avaliação (`taxa_incentivo`).

As duas tratam do gosto, não do efeito no humor (o efeito no corpo é separado do gosto, docstring da `ConfigFrutas`). Como estão em todos os braços, elas se cancelam
nos contrastes. A recência que o N6 controla é a do episódio (seção 4.1, MT).

---

## 4. Braços e controles

### 4.1 Os quatro braços de memória (H-MEM-001)

Todos com o aprendizado do lobo de decisão **desligado** (pesos no prior: `w_f` = S, o P0 da bancada). Assim a memória é a única plasticidade
do braço (decisão N6-2).

| braço | memória | o que controla |
|---|---|---|
| **M0, nenhuma** | registra e codifica (marcos 1 e 2), contribuição zero | é o P0 byte a byte nas decisões (G2) |
| **MR, relevante** | recupera pela pista certa: o episódio da própria fruta, em qualquer prazo | o braço de teste |
| **MT, só recência** | a mesma recuperação, mas só de episódios com idade ≤ `janela_recencia` (240 min, PROPOSTO) | separa "lembrar de ontem" de "lembrar da última refeição" |
| **ME, embaralhada** | os mesmos episódios, recuperados pela pista trocada π(f) | separa o conteúdo do episódio de ter um termo de memória qualquer |

Detalhes de MT e ME:
- **A janela de MT:** 240 min é a janela da informação do N5 (`ConfigInformacao.janela_min`) e a meia-vida do consumo recente do mundo
  (16 × 15 min). Ofertas a cada 3 h: dentro da janela cabe no máximo a oferta anterior do mesmo dia. Tudo o que MR tem a mais que MT vem de
  episódios de outras ofertas ou de outros dias.
- **A permutação de ME:** π é um desarranjo de {a, b, c}, isto é, nenhuma fruta mapeada em si mesma. Ela é sorteada uma vez por vida, por
  uma rng própria: `derivar_semente("n6-embaralha", semente)`. Há dois desarranjos de três elementos, um por cada sentido do ciclo. Com um
  desarranjo, ME nunca recupera o episódio certo por acaso.
- **O que ME preserva:** a capacidade, os ticks, o número de recuperações e a distribuição das valências. Só a ligação entre a pista e o
  conteúdo muda.

### 4.2 O "só cuidado" acoplado (D4)

O dono é o **atencioso**, o dono de cuidado, como no N5. As ofertas vêm do `CalendarioFrutas`, iguais em todos os braços e fora do
orçamento (B1, B2). Não há sinal de ensino no N6: a memória vem da consequência. Ainda assim, o pet que escolhe outra fruta muda o humor, e o
dono atencioso pode responder a isso com cuidado diferente.

O controle:
- **Acoplados:** para cada unidade, o registro da vida do MR (malha fechada) é rejogado em malha aberta com os cérebros M0, MT e ME. São os
  modos acoplados da bancada, aqui com o filtro vazio, porque não há sinal de ensino a tirar. Nomes: `M0<MR`, `MT<MR`, `ME<MR`.
- **Por que funciona:** os quatro têm o mesmo cuidado, as mesmas ofertas nos mesmos ticks e o mesmo genoma. Só a memória muda. Esse é o
  "estado atual igual" no nível da vida.
- **Os gates de memória** usam os acoplados (seção 7).
- **Os braços em malha fechada** (M0, MT e ME, cada um com o seu dono) rodam junto. Servem ao G5 e aos descritivos.

### 4.3 Secundário, descritivo: memória sobre a consequência

**P1 + memória relevante × P1**, com o aprendizado do N3 e a E2 ligados, no ponto que a revisão do aprendiz escolher (R4). Responde se a
memória acrescenta algo a um pet que já aprende a associação pelo peso `w_f`.

Sem gate: depende do teto e da janela, que estão em revisão, e o peso `w_f` já guarda a associação. Uma diferença ali não separa episódio
de associação.

### 4.4 Mundo

- **Os gates usam só o `descasado`** (decisão N6-8). É onde a preferência inata erra e um episódio tem o que corrigir: a fruta de maior
  preferência faz mal, a de menor faz bem (`efeitos_da_condicao`).
- **O `mutavel` roda como descritivo.** Começa casado e troca na metade da vida, no dia 7, um tick gravado. A predição dele, registrada sem
  gate: logo depois da troca, MR erra mais que MT por um ou dois dias, porque os episódios de antes da troca contradizem o mundo novo. Depois
  as substituições por empate atualizam os espaços.
- **O `casado_frutas`** fica para o experimento maior.

---

## 5. As predições (registradas antes)

- **P-N6-1 (marco 4 por decisão):** no MR, a memória muda a escolha em uma fração das sub-decisões com duas frutas ou mais **maior que a
  fração da v1** (6,9%, seção 8).
- **P-N6-2 (marco 4 no desfecho, com o estado igual):** MR tem `taxa_fruta_ruim` final **menor** que `M0<MR`.
- **P-N6-3 (além da recência):** MR tem `taxa_fruta_ruim` final **menor** que `MT<MR`.
- **P-N6-4 (o conteúdo importa):** MR tem `taxa_fruta_ruim` final **menor** que `ME<MR`.
- **P-N6-5 (fora do cuidado):** MR e `M0<MR` não diferem em saúde, privação e mortes.

---

## 6. Medidas

| medida | o que é | onde |
|---|---|---|
| **`taxa_fruta_ruim`** (primária) | fração dos consumos na fruta de efeito ruim, por janela (inicial: dias 1–7; final: dias 8–14); unidade sem consumo na janela fica fora daquele contraste (número reportado) | `metrics.py` (#144) |
| **fração decidida pela memória** | entre as sub-decisões com duas frutas ou mais, a fração em que a memória mudou a escolha | sonda contrafactual, abaixo |
| **fração de motivos que citam memória** | a mesma contagem sobre **todas** as decisões do pet (o denominador da v1) | idem |
| **cobertura da recuperação** | entre as sub-decisões com duas frutas ou mais, a fração com pelo menos um episódio recuperado | estado interno |
| **ocupação dos espaços** | curto e longo prazo, média por decisão, e a fração do tempo de cada fruta na memória | como em `experiments/memoria_espacos.py` |
| saúde média, tempo fora de privação, mortes | o canal de cuidado (G5) | `desempenho_no_ambiente` |
| humor médio | o efeito agregado | como no N5 |

**A sonda contrafactual (o marco 4 com o estado igual, decisão a decisão).** Em toda sub-decisão da fruta com duas frutas ou mais, a escolha
é refeita com `m_f` = 0 para todas as frutas, com os mesmos pesos, incentivos e o mesmo `u` da `rng_fruta`. A memória "mudou a escolha"
quando a fruta sai outra.
- É a regra de honestidade do motivo de hoje: só vira fator o que mudou a escolha.
- Na v1, o termo aprendido do bandit só virava fator quando mudava o argmax (CLAUDE.md, seção "Motivo, expressão e memória").
- A sonda só lê: não muda a vida nem a `rng_fruta`, e o G1 confere.

---

## 7. Gates (PROPOSTOS)

Contrastes **pareados por unidade**: o mesmo pet, com a mesma semente e o mesmo genoma, no mesmo registro.

**Δ** = metade da `taxa_fruta_ruim` final do `M0<MR` na calibração, isto é, metade da distância entre o pet sem memória e o acerto total.
É a regra da decisão E4 do experimento maior.

**Os marcos 1 a 3 são verificações exatas**, sem estatística: valem em toda vida da validação, ou o gate falha.

| gate | marco | o que se confere | passa se |
|---|---|---|---|
| **G1** | — | replay de toda vida, de todos os braços e acoplados | bit a bit |
| **G2** | — | M0 contra o P0 (lobos sem memória) no mesmo mundo e na mesma semente | decisões, vida e registro byte a byte; só o estado do lobo de memória difere |
| **G-M1** registrado | 1 | todo episódio aponta para um consumo do registro derivado do `MotorFrutas`, refeito pelo replay, e toda oferta comida veio de um evento do log | 100% |
| **G-M2** codificado | 2 | todo consumo gera um episódio com `tick`, `fruta` e `valencia` iguais ao registro e ao Δhumor do E2; a ocupação respeita os espaços e o desempate da seção 2.1 | 100% |
| **G-M3** recuperado | 3 | no MR, todo episódio recuperado é da fruta da pista e é o mais forte dela nos espaços; no ME, nenhum é; no MT, nenhum tem idade acima da janela | 100% |

**O marco 4 é estatístico.** Família de **Holm** com {G-CAUSAL, G-REC, G-EMB}:

| gate | medida e contraste | passa se |
|---|---|---|
| **G-CITA** (verificação da manipulação, fora da família) | fração decidida pela memória no MR, sobre as sub-decisões com duas frutas ou mais | limite inferior do IC 95% > 0,069 |
| **G-CAUSAL** | `taxa_fruta_ruim` final: `M0<MR` − MR | positivo pelo teste da seção 10 |
| **G-REC** (além da recência) | `taxa_fruta_ruim` final: `MT<MR` − MR | positivo pelo teste da seção 10 |
| **G-EMB** (o conteúdo importa) | `taxa_fruta_ruim` final: `ME<MR` − MR | positivo pelo teste da seção 10 |
| **G5** | MR − M0, os dois em malha fechada, em saúde média e tempo fora de privação; mortes | IC 95% contém 0, e mortes iguais |

### 7.1 Confirmar, refutar, inconclusivo (registrado antes)

**Confirma H-MEM-001 neste motor** quando estas quatro condições valem juntas:
- G-M1, G-M2 e G-M3 passam;
- G-CITA passa;
- G-CAUSAL, G-REC e G-EMB passam por Holm;
- G5 passa.

O resultado diz então "o episódio recuperado muda a escolha com o estado igual, além da recência, e pelo conteúdo". Não diz nada sobre
animais nem pessoas.

**Refuta H-MEM-001 neste motor** quando G-M1 a G-M3 passam e o IC 90% de `M0<MR` − MR inteiro fica dentro de (−Δ, +Δ) (equivalência), com a
exposição suficiente (seção 13, risco 1). Leitura: o episódio é registrado, codificado e recuperado, e não decide.

**Inconclusivo** em qualquer outro caso. Com a exposição insuficiente, a leitura é **inconclusivo por exposição** (seção 13).

**Leituras parciais** (registradas agora, para não serem inventadas depois):

| G-CAUSAL | G-REC | G-EMB | leitura |
|---|---|---|---|
| passa | falha | passa | a memória decide, mas o que decide é a última refeição: o efeito cabe numa janela de recência |
| passa | passa | falha | um termo de memória mexe na escolha, mas o conteúdo do episódio não explica a melhora |
| passa | falha | falha | efeito de recência sem conteúdo |
| falha | — | — | os outros dois não se leem como memória |

**Gates dos marcos que falham:**
- **G-M1, G-M2 ou G-M3 falha:** é erro de implementação, não resultado. A run é refeita com sementes novas registradas antes (seção 11).
- **G-CITA falha com G-CAUSAL passando:** a memória decide poucas escolhas, mas as certas. Isso é registrado como está.

**Descritivos (sem gate):**
- MR − M0 em malha fechada na `taxa_fruta_ruim`;
- a janela inicial;
- o `mutavel` (seção 4.4);
- o secundário P1 + memória (seção 4.3);
- a ocupação dos espaços;
- a fração de motivos que citam memória sobre todas as decisões (seção 8).

---

## 8. A comparação com os 6,9% da v1

**O número da v1:** na memória por espaços da v1, 6,9% dos motivos citaram uma memória (0,0692; 6,3% no atencioso a 7,8% no aleatório).
Está em `artifacts_v1_memoria_espacos/espacos.json`, `fracao_motivos_citam_memoria_total` e `por_braco`. A tarefa aponta o `metrics.json`,
mas o número está no `espacos.json` da mesma pasta (registrado em `docs/REGISTRO_DESVIOS.md`).

**Os denominadores não são iguais.**
- **Na v1:** a memória entrava em toda decisão do bandit, então o denominador "todos os motivos" era o das decisões em que ela podia agir.
- **No N6:** a memória só age nas sub-decisões com duas frutas ou mais. Pelo N4 elas são de 4 a 24 por vida (`docs/RESULTADO_V2_N4.md`,
  sobre `artifacts_v2_n4/validacao/`). As decisões do pet são cerca de 96 por dia, uma a cada 15 min, por 14 dias. Mesmo que a memória
  decidisse todas as sub-decisões, a fração sobre todos os motivos ficaria em torno de 24 / 1344 ≈ 1,8%, abaixo de 6,9% **por construção**.

**Por isso:**
- o **G-CITA** compara as decisões em que a memória pode agir, nos dois casos (na v1, todas; no N6, as sub-decisões com duas frutas ou mais);
- a fração sobre todos os motivos sai como descritivo, com essa nota ao lado;
- comparar 6,9% com a fração sobre todos os motivos do N6 e concluir que "a memória da V2 decide menos" é uma **afirmação a evitar**.

---

## 9. Calibração (19101, 19202, 19303, 19404, 19505)

**Só o ganho `g` da memória** é calibrado.
- **Grade (PROPOSTA):** `g` ∈ {S/4, S/2, 3S/4}, todos abaixo de S (seção 2.2).
- **O resto fica fixo:** os espaços da v1, a janela de MT de 240 min, o descasado da bancada, a `ConfigFrutas` que estiver na `main`, o dono
  atencioso e o aprendizado desligado. O que estiver na `main` na hora da calibração vale para a validação.
- **Regra de escolha (registrada agora):** o **menor** `g` em que G-CITA passa, com o limite inferior do IC 95% da fração decidida pela
  memória no MR acima de 0,069.
- **Se nenhum passa:** o `g` de maior limite inferior, e o relatório diz que a calibração não fechou.
- **O que não entra na escolha:** G-CAUSAL, G-REC e G-EMB, que são o que a validação testa.
- **Δ** sai da calibração (seção 7).
- **O secundário** P1 + memória usa o mesmo `g`.

---

## 10. Estatística

- **Unidade:** a vida de um par (genoma, semente). Num mesmo registro de MR estão MR e os seus três acoplados. As unidades de uma mesma
  semente-base ficam juntas no bootstrap.
- **"Positivo pelo teste":** p unilateral na direção predita, pelo bootstrap sobre unidades (`metrics.bootstrap_ic`, com as reamostragens, a
  semente e o nível do `PROTOCOLO_ARENA_V1`). O limiar é o de **Holm** sobre {G-CAUSAL, G-REC, G-EMB}, α = 0,05. O teste t pareado é só
  conferência.
- **G-CITA** usa o IC 95% bootstrap da fração, sobre unidades. **G5** usa IC 95% bilateral, lido junto com as mortes.
- **Equivalência** (refutar, seção 7.1): IC 90% dentro de (−Δ, +Δ).
- Tudo fora da família é descritivo.

---

## 11. Validação (20101, 20202, 20303, 20404, 20505), uma vez

- Com o `g` escolhido, o Δ e o número de unidades do **adendo** (seção 12), commitados neste arquivo antes da run.
- Análise única, sem olhada intermediária. Refeita do zero, com sementes novas registradas antes, só por erro de execução (inclusive G-M1 a
  G-M3), nunca pelo resultado.
- Falha registrada não para a V2 (decisão de 2026-10-01).

---

## 12. Sementes, unidades e tamanho da amostra

### 12.1 Faixas propostas (o coordenador fecha)

| o quê | faixa | bases |
|---|---|---|
| N6, calibração | **19101…19505** | 19101, 19202, 19303, 19404, 19505 |
| N6, validação | **20101…20505** | 20101, 20202, 20303, 20404, 20505 |

**Por que estas faixas.** Elas estão fora de toda faixa reservada ou usada que encontrei:
- `FAIXAS_RESERVADAS` em `experiments/bancada_v2.py`: 101…15505, 50001…50020, 60001…60160, 69001, 80001…82004 e 20260900…20261800;
- a seção 6 do `docs/ROADMAP_V2.md`, que tem o N11 em 16101…17505;
- a revisão do aprendiz, 18101…18505 (`docs/V2_RODADA_5.md`).

**Busca feita** no repositório, fora de `artifacts`: 19101 e 20101 não aparecem como semente. As ocorrências de 19005, 19805 e 21405 são
ticks nos gabaritos da web.

**Ao fechar as faixas:** a implementação acrescenta 19101…19505 e 20101…20505 às `FAIXAS_RESERVADAS`. Faltam lá hoje o N11 (16101…17505) e
a revisão (18101…18505); registrado.

### 12.2 Unidades e N

- **Unidades derivadas** pela regra E3: semente da unidade k da base b = `derivar_semente("n6", b, k)`; genoma
  `derivar_semente("n6-genoma", b, k)`; o mesmo K em todas as bases. O teste de colisão da bancada se aplica.
- **K da calibração (PROPOSTO):** o mesmo do N5, isto é, o da calibração do experimento maior quando fixado, senão 4 por base (20
  unidades).
- **K da validação:** pela regra da seção 7.2 do plano do experimento maior: N = ((z₁₋α + z₀,₈) × σ_d / Δ)² por contraste da família, com α
  do passo mais exigente de Holm (α/3) e poder 0,8. Vale o maior N dos três, arredondado ao múltiplo de 5 e conferido por simulação com as
  unidades da calibração. Entra no adendo.
- **Por quê:** a variância entre unidades domina. Na análise de poder da v1, ICC 0,745 e só 0,34% da variância do estimador vinha das
  partidas (`artifacts_poder/variancia.json`). Mais unidades, não vidas mais longas.

---

## 13. Riscos registrados antes

1. **Poucas sub-decisões em que a memória pode agir.**
   - **Os números:** no N4 houve de 4 a 24 escolhas com duas frutas ou mais por vida (`docs/RESULTADO_V2_N4.md`), e o atencioso comeu 45,2
     frutas por vida em média (`artifacts_v2_n4/validacao/resultado.json`, `resumo.por_dono.atencioso.comidas`). O p(comer | fruta no
     cenário) médio da validação foi 0,208 (`resumo.p_comer`).
   - **O que isso quer dizer:** episódios não faltam; faltam escolhas em que eles possam pesar.
   - **A ressalva:** o descasado da bancada não é o do N4 (`docs/V2_RODADA_5.md`, ponto aberto 2), então esses números são só referência.
   - **A regra:** se a mediana de sub-decisões com duas frutas ou mais e episódio recuperado ficar abaixo de 5 por vida no MR (PROPOSTO),
     ou se mais de metade das unidades não tiver consumo na janela final, os gates do marco 4 são lidos como **inconclusivo por
     exposição**, não como refutados.
2. **O longo prazo guarda só dois episódios.** Com três frutas, a neutra perde a disputa e, de um dia para o outro, só a boa e a ruim
   ficam. Isso é desenho (D7), mas com um efeito: no MR, a memória de um dia para o outro é quase "a boa e a ruim de sempre", perto de uma
   associação. A ocupação por fruta é reportada. Se a fruta ruim passar menos de metade do tempo no longo prazo, a leitura de G-REC leva
   essa nota.
3. **A recência do mundo.** O consumo recente derruba a avaliação da fruta comida (seção 3) e empurra o pet a alternar, em todos os braços.
   Isso reduz o espaço para a memória mudar a escolha, mas não confunde os contrastes, que são pareados no mesmo registro.
4. **O acoplado e a malha.** Os gates usam MR em malha fechada contra os outros cérebros em malha aberta no registro do MR. Se o dono
   atencioso reagir ao humor, o cuidado do registro é o que serviu ao MR. O G5 em malha fechada (MR − M0) diz se isso pesou.

---

## 14. Ligação com a fala: H-MEM-02, só como pergunta registrada

**H-MEM-02:** a memória que o jogador vê (a autobiográfica: a história da voz, o que a fala cita) e a memória que decide podem ser a mesma
estrutura sem mentir?

**O N6 não testa isso** e não muda a fala. Ele deixa medida a pré-condição:
- **Episódios decisivos:** a fração de episódios recuperados que mudaram uma escolha, pela sonda da seção 6, contra os recuperados que não
  mudaram nada.
- **A frase honesta:** uma frase honesta sobre o passado ("não como a A, me fez mal") só poderia apontar para os episódios decisivos.
- **Pistas conceituais, sem validar desenho:** memórias autobiográficas como construções transitórias (Conway e Pleydell-Pearce 2000,
  `10.1037/0033-295x.107.2.261`, VERIFICADA); a história acumulada e legível do Dwarf Fortress como objeto de análise acadêmica (Adams 2021,
  `10.1515/9783839453452-007`, VERIFICADA, que não sustenta validade psicológica das mecânicas do jogo).

A pergunta fica para depois do N6 e do motivo das regras novas (chat A, `docs/TAREFA_V2_N5_ACOPLADO.md`).

---

## 15. Fora deste plano

- código e runs;
- o N7 (arbitragem);
- relembrar e reconsolidação (L2, decisão N6-4; os análogos verificados são Nader, Schafe e LeDoux 2000, `10.1038/35021052`, e McGaugh
  2005, `10.1101/lm.93405`, e ficam como análogos de forma, não modelo);
- a memória em comer ou não;
- a memória de outras fontes: as ações do dono, a bola, a informação do N5;
- a fala;
- a web.

---

## 16. Decisões que só o Matheus pode tomar

**Decididas pelo Matheus em 2026-10-04: todas como recomendadas (N6-1 a N6-10).** Faixas fechadas pelo coordenador: N6 calibração
19101…19505, validação 20101…20505 (não colidem com a revisão do aprendiz, 18101…18505).

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| N6-1 | onde a memória entra | só na sub-decisão da fruta, como a informação do N5 | em comer ou não, a memória muda quanto o pet come, entra no canal de cuidado e o G5 deixa de ser satisfazível por desenho |
| N6-2 | aprendizado do lobo de decisão nos braços de memória | desligado (memória sobre o P0); P1 + memória só como descritivo | com o P1 ligado, o peso `w_f` já guarda a associação e a diferença não separa episódio de associação; o teto e a janela ainda estão em revisão |
| N6-3 | o que é o episódio e onde mora | consumo de fruta com a valência do humor, nos espaços da v1 por fruta (4 + 2, 12 h, desempate da seção 2.1), sem decaimento contínuo | um episódio com a fome seria ruído igual entre frutas; o decaimento por `exp` quebra a paridade com a web |
| N6-4 | relembrar | desligado no N6 | relembrar mexe na força dos episódios e soma uma segunda pergunta (reconsolidação) à primeira |
| N6-5 | janela do controle de recência | 240 min | uma janela de um dia faria MT quase igual a MR e G-REC impossível; uma de 15 min faria MT quase igual a M0 |
| N6-6 | embaralhamento | desarranjo de {a, b, c} por vida, rng própria | uma permutação qualquer acerta a pista em 1/6 das vidas e dilui G-EMB |
| N6-7 | a comparação com 6,9% | sobre as decisões em que a memória pode agir (G-CITA); a fração sobre todos os motivos só descritiva | sobre todos os motivos o N6 fica abaixo de 6,9% por construção, e o resultado pareceria pior que o da v1 sem ser |
| N6-8 | mundos | gates só no `descasado`; `mutavel` descritivo | gates no `mutavel` misturam memória certa com memória vencida |
| N6-9 | faixas de sementes | 19101…19505 (calibração) e 20101…20505 (validação) | reusar uma faixa vicia o teste (M7 do roadmap) |
| N6-10 | calibração do ganho | `g` ∈ {S/4, S/2, 3S/4}, o menor que passa G-CITA | calibrar no G-CAUSAL testa na calibração o que a validação deveria testar |
