# Predições da V2 com o apoio teórico de cada uma (2026-10-06)

**Base:**
- a síntese de literatura `docs/referencias/E_SINTESE_VALOR_APRENDIZADO.md` (cópia no repositório; o original está na pasta `v1`);
- as regras de citação de `docs/referencias/REGRAS_CITACAO_DIGILAB.md`;
- as predições 1 a 5 de `docs/PLANO_ANALISE_V2_EXPERIMENTO_MAIOR.md`, seção 5, no repositório da `main` (pasta `v2`), com os adendos 1 e 2.

**O que este documento é:** só texto. Não roda nada e não muda código, engine nem config. Ele não substitui o plano de análise. O que daqui
for adotado entra no plano como adendo, antes da validação.

## Vocabulário

**Apoio teórico** (exatamente estes rótulos):

| rótulo | significado |
|---|---|
| APOIADA | a fonte prevê o que a predição diz |
| APOIADA COM RESSALVA | a fonte concorda na direção e discorda num ponto que muda o desenho |
| SEM APOIO DIRETO | nenhuma fonte verificada mede o que a predição diz |
| CONTESTADA | uma fonte verificada sustenta o contrário da premissa |

**Estado de cada item:**

| estado | significado |
|---|---|
| EXECUTADO | há um artefato em disco que o produz |
| ESPECIFICADO | está escrito com detalhe para executar, mas não rodou |
| IDEIA | ainda não está especificado |

**Regras de citação:**
- Cada afirmação separa **"a fonte diz"** de **"leitura nossa"**.
- Para cada referência vai entre parênteses o que a síntese conferiu: texto completo, resumo, ou só título e metadados.
- Referência conferida só por título e metadados (Stephens 1991; DeWitt, Sih e Wilson 1998; Snell-Rood 2013; Laland 2004) **não** sustenta
  afirmação de conteúdo aqui. As pistas não resolvidas do fim da síntese também não.
- **Ressalva de cobertura** (da própria síntese): não houve varredura por código em Crossref, arXiv ou Europe PMC, nem a auditoria de lista
  de autores. A verificação foi item a item.

## Estado do experimento hoje

| item | estado | onde |
|---|---|---|
| predições 1 a 5 registradas | ESPECIFICADO | `PLANO_ANALISE_V2_EXPERIMENTO_MAIOR.md`, seção 5 |
| calibração conjunta do cérebro A | EXECUTADO | `artifacts_v2_calibracao_conjunta/` (escolha, piloto e adendo), PR #181 |
| N da validação (opção A: N = 30, K = 6 por base, cerca de 4,5 h) | ESPECIFICADO | adendo 2 do plano; números de `artifacts_v2_calibracao_conjunta/adendo_opcao_a.json` |
| config e orquestrador da validação | ESPECIFICADO (prontos, não rodados) | PR #183 |
| validação única | não rodada | espera os adendos deste documento |

Duração de vida da validação hoje: **14 dias**, a duração registrada no plano e nas configs da calibração conjunta
(`experiments/configs/v2_calibracao_conjunta/`).

---

## Predição 1 — no casado, P0 vence: aprender só custa

**Apoio teórico: APOIADA.** **Estado:** ESPECIFICADO.

**A fonte diz:**
- **Kozielska e Weissing (2024)**, `10.1371/journal.pcbi.1011840` (texto completo):
  - com mudança rara e pequena, as redes sem aprendizado chegam praticamente ao mesmo desempenho das que aprendem e têm vantagem de
    aptidão, porque não gastam tempo explorando;
  - quando a duração do aprendizado evolui, ela vai a zero nesse regime.
- **Mery e Kawecki (2003)**, `10.1098/rspb.2003.2548` (resumo): em *Drosophila* há um custo **constitutivo** da capacidade de aprender,
  pago mesmo quando o aprendizado não é usado.

**Leitura nossa:**
- A direção da predição está apoiada.
- Na V2 o custo do P1 só aparece quando ele explora e deriva. O custo constitutivo da biologia não tem análogo no motor, então o efeito
  esperado é pequeno: **empate ou leve vantagem do P0**.
- Isso pesa na leitura: um "refuta por empate" (IC 90% dentro de ±Δ) é um desfecho plausível, não um defeito do desenho.
- Não há seleção entre gerações neste experimento, então a "perda do aprendizado" do modelo não tem como acontecer aqui.

---

## Predição 2 — no descasado e no mutável, P1 vence P0 se a vida for longa

**Apoio teórico: APOIADA COM RESSALVA.** **Estado:** ESPECIFICADO.

**A fonte diz:**
- **Kozielska e Weissing (2024)** (texto completo):
  - com mudança frequente ou grande, o aprendizado corrige um prior herdado muito errado;
  - a aptidão é máxima num número **intermediário** de episódios de aprendizado, com retornos que caem até ficar desprezíveis;
  - um período de aprendizado mais longo **nem sempre** dá melhor desempenho.
- **Dunlap e Stephens (2009)**, `10.1098/rspb.2009.0602` (resumo): em evolução experimental com *Drosophila*, a mudança ambiental se
  decompõe em **confiabilidade da experiência** e **previsibilidade da melhor ação**. Alguns tipos de mudança favorecem o aprendizado, e
  outros selecionam contra ele.

**Leitura nossa:**
- A direção (P1 > P0 no descasado) está apoiada.
- A forma "quanto mais vida, melhor" não está: pode haver platô ou ótimo interior. Com uma ou duas durações, um "inconclusivo por duração"
  não distingue entre "precisa de mais vida" e "já está no platô".
- Daí o **adendo (a)**, abaixo.
- **O mutável fica sem teoria direta.** Daí o **adendo (b)**, abaixo.

---

## Predição 3 — P2 chega à metade do caminho com menos consequências que P1

**Apoio teórico: APOIADA**, por uma via diferente da que a predição supõe. **Estado:** ESPECIFICADO.

**A fonte diz:**
- **Rendell et al. (2010)**, `10.1126/science.1184719` (resumo): estratégias baseadas em informação social venceram mesmo quando a
  informação individual não custava mais. O motivo é que os demonstradores exibiam o comportamento de maior retorno, e isso filtrava a
  informação para quem copiava.
- **Kendal et al. (2018)**, `10.1016/j.tics.2018.04.003` (resumo): os indivíduos alternam e combinam estratégias com flexibilidade, sem
  correspondência um a um entre heurística e padrão observado.

**Leitura nossa:**
- A vantagem esperada do P2 vem de a informação **já chegar filtrada** (o informante conhece o efeito real), não de "economizar
  tentativas".
- O desenho já tem o controle que separa as duas coisas: o **P2a** (a mesma informação verdadeira, fora do momento da oferta) e o
  **P2e** (a informação descorrelacionada da qualidade, no extremo oposto).
- Kendal et al. pesa sobre a **ablação da arbitragem** (N7), não sobre esta predição: um peso fixo entre a necessidade do pet e o pedido
  do dono é mais rígido que o descrito. Fica como limitação do N7.

---

## Predição 4 — P2e piora no começo e se recupera quando a consequência refuta a informação

**Apoio teórico: SEM APOIO DIRETO.** **Estado:** ESPECIFICADO.

**A fonte diz:**
- Nenhuma fonte verificada mede a trajetória de recuperação depois de informação errada num agente que também tem a consequência.
- O mais próximo é **Rendell et al. (2010)** (resumo): a informação social vale **porque** vem filtrada.
- Também há **Kozielska e Weissing (2024)** (texto completo): quando o aprendizado eficiente evolui, o agente passa a depender inteiramente
  dele.

**Leitura nossa:**
- A parte (a), "piora no começo", é plausível: a informação errada tira justamente a filtragem que dá valor à informação.
- A parte (b), "recupera", não tem expectativa de magnitude nem de prazo na literatura verificada.
- O plano já registra, ao lado, o dia em que a curva do P2e cruza a do P0. Esse dia é a quantidade descritiva mais útil aqui, e o
  relatório deve trazê-la mesmo quando (b) sair inconclusiva.

---

## Predição 5 — P3 fica perto de P0

**Apoio teórico: CONTESTADA.** **Estado:** ESPECIFICADO.

**A fonte diz:**
- **Ho, MacGlashan, Littman e Cushman (2017)**, `10.1016/j.cognition.2017.03.006` (resumo):
  - a suposição de que o feedback avaliativo age pelos mecanismos comuns de aprendizado por contingência teve sucesso limitado nos
    programas de pesquisa que a adotaram;
  - o feedback de um parceiro social funciona melhor tratado como **comunicação sobre o valor de uma ação**, não como recompensa.

**Leitura nossa:**
- No cérebro A, o P3 trata elogio e bronca como **sinal de vantagem** no crédito da decisão: a regra da L1, da família COACH. Desde o K4,
  esse sinal inclui o julgamento da fruta pelo efeito real, dado no primeiro passo do dono depois do consumo e creditado à decisão de
  comer.
- Logo, se a predição 5 se confirmar, ela pode estar confirmando **a arquitetura** (o sinal tratado como recompensa), e não um fato sobre
  o canal de ensino. Este é o risco do item 4 abaixo.

---

## Adendos de registro obrigatório antes da run

### Adendo (a) — duração de vida: pelo menos três durações

**Estado:** ESPECIFICADO neste documento. Ainda não está no plano.

**O que registrar:** o desempenho do P0 e do P1 em **pelo menos três durações de vida**, não duas. A relação entre a duração e o desempenho
do aprendiz não é monotônica (Kozielska e Weissing 2024, texto completo). Com duas durações não se separa monotonicidade de platô.

**Desenho proposto (PROPOSTO, decisão do Matheus):**
- **Durações:**
  - a principal, de 14 dias, onde ficam os seis contrastes primários e o Holm, sem mudança;
  - mais duas, uma menor e uma maior, como bloco secundário e descritivo, fora da família de Holm.
- **Braços:** P0 e P1, onde está a predição 2.
- **Mundos:** descasado e mutável.
- **Unidades:** as mesmas bases e unidades da validação.
- **Leitura:** forma da curva (crescente, platô ou ótimo interior) por braço e mundo, com IC por bootstrap das unidades. Nenhum contraste
  novo entra na família primária.
- **Mutável:** a troca acontece na metade da vida (`Bancada.tick_troca` = fim do dia `dias // 2`). Mudar a duração muda também o momento
  da troca. A leitura do mutável no bloco de durações fica separada da do descasado, e essa confusão vai declarada.
- **Custo:** o tempo de máquina do bloco é calculado pelo worker B a partir do tempo por vida da calibração conjunta
  (`artifacts_v2_calibracao_conjunta/`) e conferido contra o teto de 12 h da K-10 **antes** da run. Se passar do teto, decide o Matheus.

### Adendo (b) — o mutável sem precedente teórico direto: limitação declarada

**Estado:** ESPECIFICADO.

- **O que registrar:** os modelos disponíveis tratam mudança **entre gerações**, não dentro da vida. Fonte: Kozielska e Weissing (2024),
  texto completo e o registro de revisão por pares publicado com o artigo, onde o revisor aponta exatamente isso.
- **Consequência:** a predição 2 no mutável e as leituras de "depois da troca" são testadas **sem expectativa teórica direta** de
  magnitude. Um resultado ali é descrição do que este motor faz, não confirmação ou refutação de teoria. Isso vai no relatório da
  validação como limitação.
- **O que não muda:** o contraste primário P0 − P1 no mutável continua na família e no Holm. A limitação muda a leitura, não o teste.

---

## Risco de interpretação do P3 e as variantes que isolam o momento e a interpretação

**Estado:** ESPECIFICADO (sem código).

**O risco.** P3 e P2 diferem em duas coisas ao mesmo tempo:

| | P2 | P3 |
|---|---|---|
| **momento** do sinal | antes da escolha: informa cada fruta logo depois da oferta | depois da escolha: julga o consumo no primeiro passo do dono |
| **interpretação** do sinal | **informação**: entra na percepção (`info_frutas`) e pesa a escolha da fruta pelo peso `w_info`, que só a consequência ajusta | **recompensa**: elogio e bronca pelo `receber_acao_dono`, como vantagem no crédito da decisão de comer e dos pesos da fruta |

Comparar P2 com P3 mistura os dois. A predição 5 pode sair "confirmada" só porque o P3 trata o sinal como recompensa.

**Correção (2026-10-06, antes de qualquer código).** A primeira versão deste documento propunha uma variante só, o P3i, e dizia que
P2 × P3i isolava o momento. Não isola. O P2 aprende pela **consequência** e não recebe sinal do dono. O P3 aprende pelo **dono** (a tarefa
de sempre mais o julgamento da fruta) e não pela consequência. Logo, P2 × P3i também difere na fonte do aprendizado. Uma variante só não
separa as duas coisas. São precisas duas.

**Variante 1, P2d, que isola só o momento:** é o P2, com a informação **depois** do consumo.
- **O que mantém do P2:**
  - a fonte `informacao`: aprende pela consequência, com a E2, e nada do dono chega como sinal;
  - o informante que conhece o efeito real (os mesmos `efeitos_reais`, com a troca do mutável);
  - o mesmo evento `informar_fruta_<f>_<bem|mal>`, fora do orçamento;
  - a mesma percepção `info_frutas`, com o `w_info` e a janela do ponto da K2.
- **A única diferença:** o informante não fala logo depois da oferta. Fala sobre a fruta **consumida**, no primeiro passo do dono depois
  do consumo: o mesmo momento do julgamento do K4.
- **Contraste:** **P2 × P2d** = só o **momento** (antes × depois da escolha).

**Variante 2, P3i, que isola só a interpretação:** é o P3, com o julgamento da fruta como informação.
- **O que mantém do P3 com K4:**
  - a fonte `dono`;
  - o mesmo atencioso, com o feedback da tarefa de sempre;
  - o mesmo julgador da fruta e o mesmo momento: o primeiro passo do dono depois do consumo, fora do orçamento.
- **A única diferença:** o julgamento da fruta sai como `informar_fruta_<f>_<bem|mal>`, e não como `elogiar`/`repreender`. Entra na
  percepção `info_frutas` com o `w0_info` do ponto da K2.
- **Contraste:** **P3 × P3i** = só a **interpretação** (recompensa × informação).
- **Efeito colateral declarado:** no P3i o peso `w_info` não aprende, porque só a consequência o ajusta e o P3 não aprende pela
  consequência. A informação entra com o peso de partida fixo. Isso é parte de "tratar como informação" neste cérebro, e vai declarado.

**O que fica sem par, declarado:** P2d × P3i difere na fonte do aprendizado (consequência × dono) e no feedback da tarefa. Esse par não
entra em contraste nenhum.

**Diferença residual do P2d:** o P2 informa sobre toda fruta **oferecida**; o P2d, sobre toda fruta **consumida**. A quantidade e a
composição dos itens diferem. O número de informações e o multiconjunto (fruta, conteúdo) vão medidos e reportados por braço. O P2a (a
mesma informação do P2, fora do momento da oferta) é a referência descritiva.

**Onde entram:** como braços **secundários**, fora da família de Holm dos seis primários, no descasado e no mutável. Precisam de código no
mundo (chat A) e na bancada (chat D), com gates de mecanismo antes da validação. O cérebro não muda: a percepção da informação já existe.

---

## Decisões que só o Matheus pode tomar

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| P-1 | Adotar o **adendo (a)** (três durações, P0 e P1, descasado e mutável, bloco secundário) antes da validação | **Sim**, com a duração principal de 14 dias intacta e o custo conferido contra as 12 h antes da run | sem ele, um "inconclusivo por duração" na predição 2 não tem leitura; com ele na família primária, o Holm perde poder |
| P-2 | As duas durações extras | uma menor e uma maior que 14 dias, escolhidas pelo custo calculado (P-1), sem olhar dado da validação | duas durações perto de 14 dias não mostram a forma da curva; uma muito longa estoura o teto de tempo |
| P-3 | Adotar o **adendo (b)** (mutável como limitação declarada) | **Sim**, só no texto da leitura; o teste não muda | sem ele, um resultado no mutável seria lido como confirmação de teoria que não existe para esse caso |
| P-4 | Criar os braços **P2d** e **P3i** antes da validação | **Sim**, como secundários: são o único jeito de saber se a predição 5 mede o canal ou a arquitetura. A validação espera o código (uma rodada de construção) | sem eles, qualquer desfecho da predição 5 fica ambíguo; como primários, a família cresce e o N também |
| P-5 | Manter a predição 5 como está, mesmo CONTESTADA | **Sim**: ela foi registrada antes e é falsificável; a contestação vai na leitura e o P2d e o P3i separam as causas | trocar a predição agora seria ajustá-la à literatura depois do registro, sem dado novo |
| P-6 | Rodar a validação **antes** do P2d e do P3i, para não esperar | **Não**: a validação é única, e as variantes só servem se rodarem nas mesmas unidades | rodar antes obriga uma segunda validação ou deixa as variantes sem par |
| P-7 | Próxima passada de literatura (as pistas de prioridade 1: Dunlap, Austin e Figueiredo 2019; Liedtke e Fromhage 2019; Eliassen et al. 2009) | **Sim**, antes da leitura dos resultados, não antes da run. Uma delas pode contrariar a condição de vida longa, mas é pista não verificada e não muda o desenho agora | sem ela, a discussão da predição 2 fica sem a revisão mais próxima do tema |

## Decisões tomadas (2026-10-06)

O Matheus aprovou P-1 a P-7 como recomendado, com a correção das duas variantes (P2d e P3i). Elas entram como adendo 3 de
`docs/PLANO_ANALISE_V2_EXPERIMENTO_MAIOR.md`, no repositório da V2.
