# PLANO DE ANÁLISE V3 — GOSTO_VISUAL, a fala do assistir: o comentário com o órgão contra o comentário sem ele (2026-11-11, Claude Code, Opus 5.5)

**Status: PROPOSTO.** Nenhuma fala, nenhuma vida e nenhuma chamada a modelo antes de o Matheus aprovar este plano. As decisões GVF-1 a
GVF-10 (seção 12) são dele. A proposta é a `docs/futuro/fala_do_assistir.md` (seções 2, 10 e 10.10; a FA-20); a frente é a
`docs/TAREFA_V3_GOSTO_VISUAL.md`.

**Nada roda antes de sete coisas:**
- este cabeçalho com a marca "APROVADO pelo Matheus";
- o resultado da DC5 (o `docs/RESULTADO_V3_CONVERSA_DC5.md`, da DC5d), que diz qual voz serve (seção 9);
- a faixa pedida ao coordenador e escrita em `FAIXAS_RESERVADAS` (seção 7);
- o código da GVFa na `main`, com a fumaça nas sementes dos testes e nenhuma chamada real (seção 11);
- o mapa espécie → sentido mítico da frente MITOLOGIA, decidido pelo Matheus (FA-15), se a condição PM entrar (GVF-1);
- o adendo da rubrica, revisto pela Gerente da CONVERSA_PET e commitado, com o sha256 no registro (4.2);
- o registro da rodada (seção 10), num commit empurrado antes da primeira chamada da validação.

**De onde vem:**
- **as direções do Matheus de 2026-11-11** (o topo da `fala_do_assistir.md`): o comentário nasce da percepção do pet; o órgão reconhece
  conceitos, inclusive os do Digimundo com um sentido mítico; e "Vamos testar um braço da pesquisa com isso";
- **a pergunta, nas palavras da coordenação:** "a fala fica mais natural e melhor desenvolvida com o órgão?";
- **o molde é a DC5** (`docs/PLANO_ANALISE_V3_CONVERSA_DC5.md`, `docs/RUBRICA_DC5_FIDELIDADE.md`): a preferência cega em pares, a
  fidelidade "sem sustento" com o marcador Opus cego e a amostra do Matheus, e os descritivos de variedade. Este plano reusa a maquinaria e a
  rubrica, sem duplicar.

**O que este plano não afirma:**
- **nada sobre o órgão de verdade.** Não há modelo de visão nesta etapa: os conceitos vêm de um catálogo de cenas roteirizadas, com a
  confiança escrita no script. O que se testa é o **valor do conceito percebido para a fala**, supondo o órgão certo. O acerto do órgão (e o
  limite do anime contra os sprites, `fala_do_assistir.md`, 10.10.2) fica para a OV2;
- **nada sobre o estado no afeto** (FA-18): no desenho leve (GVF-2), o conceito vai só à voz e não entra no cérebro;
- que a fala parece viva ao jogador jogando; o que se mede é a leitura de sequências curtas de comentários;
- que o resultado vale fora destas cenas, destes modelos e desta voz;
- que a preferência é cega à condição (4.1);
- **nenhuma novidade.** Nenhuma referência sustenta o desenho; onde o plano decide um número sem molde da DC5, ele é PROPOSTO, SEM FONTE.

## 0. O que mudou do desenho sugerido pela coordenação, e por quê

| o desenho sugerido | a mudança | a razão |
|---|---|---|
| dois braços: "com percepção" (conceito + mito + agrado, novidade, habituação) e "sem percepção" (só o agrado sobre os sete números) | **três condições: S, P e PM** (seção 2) | o "com" muda três coisas de uma vez (o conceito, o mito e os sinais da rede). Uma preferência pelo "com" não diria se foi a percepção ou o mito. Com P no meio, P × S responde à pergunta do órgão, e PM × P responde à do mito (GVF-1) |
| o "sem" só com o agrado | **o S recebe o agrado, a novidade e a habituação sobre os sete números**, os mesmos sinais que o P | assim P e S diferem só no conceito percebido; senão o P ganharia também por ter mais sinais da rede (GVF-3) |
| "mais natural e melhor desenvolvida" como uma pergunta | **natural é gate; "melhor desenvolvida" vira descritivo com medidas escritas antes** (4.4) | "desenvolvida" não tem medida na DC5; um gate sobre uma palavra sem definição convida a escolher a medida depois (GVF-6) |
| "a mesma voz, o mesmo LLM" | **a voz que a DC5d declarar apta, nos dois braços de modelo da DC5 (G e H)** | o `gemma2:9b` é o padrão do jogo; o H custa pouco e repete o par da DC5 (GVF-4, GVF-8) |
| a preferência cega | **a cegueira à condição não é possível**: um "é o Agumon!" denuncia o P. O plano fixa antes como isso aparece no relato (4.1) | sem isso, a preferência pelo P vira "reconhece o nome" lida como "mais natural" |

## 1. As perguntas e as previsões, escritas antes

Uma **célula** é uma condição (S, P ou PM) num braço de modelo (G ou H). Os gates de fidelidade valem por célula; os de naturalidade, por
braço.

| pergunta | o que se mede | a previsão | o papel |
|---|---|---|---|
| **Q1 NATURAL-P:** com o conceito percebido, o pet parece mais estar assistindo de verdade? | a preferência do Matheus, P × S, em pares de sessões (4.1) | o P escolhido em ≥ 10 de 12 pares por braço | **G-NATURAL-P**, gate por braço |
| **Q2 NATURAL-M:** o sentido mítico acrescenta? | a preferência do Matheus, PM × P (4.1) | sem previsão de direção; o PM escolhido em ≥ 10 de 12 conta como "acrescenta" | **G-NATURAL-M**, gate por braço (só com a PM) |
| **Q3 FIEL:** o comentário só diz o que o pet percebeu e o que o mito dá? | a fração de comentários com pelo menos uma afirmação sem sustento (4.2) | ≤ 0,10 em cada célula | **G-FIEL**, gate por célula |
| **Q4 CRENÇA:** o mito sai como crença ou como fato? | a fração dos comentários da PM com crença dita como fato (4.2) | ≤ 0,10 | parte do G-FIEL, relatada à parte |
| **Q5 DÚVIDA:** a confiança baixa sai como dúvida? | nas cenas de confiança baixa, a fração de comentários que afirma o conceito sem dúvida (4.3) | sem previsão | descritivo |
| **Q6 DESENVOLVIDA:** o comentário diz mais coisa? | as palavras por comentário, os conceitos citados por comentário e a fração que nomeia algo percebido (4.4) | maior no P e no PM | descritivo |
| **Q7 VARIEDADE:** o comentário se repete? | o distinct-n e a repetição entre comentários da mesma sessão, pelas medidas da DC5 (4.4) | o P mais variado que o S | descritivo |

- **O nulo plausível, escrito antes:** o P pode parecer mais natural e ser menos fiel. Com um nome na entrada, o modelo pode enfeitar ("o
  Agumon está bravo!"). Por isso o G-FIEL é medido em todas as células, e o P só serve se passar nele.
- **O outro nulo:** o S pode já parecer natural o bastante ("gostei disso!"), e o Matheus não preferir o P. O G-NATURAL-P mede isso, e o
  resultado negativo é registrado como está.

## 2. O desenho

- **As condições** (GVF-1, GVF-3):
  - **S, sem percepção:** a entrada da voz é o conceito do assistir (`gostei`, `chato`, `o_que_e`, `susto`; `fala_do_assistir.md`, 2.2),
    tirado do agrado, da novidade e da habituação sobre os sete números da cena, mais a espécie e o humor em palavras;
  - **P, com percepção:** o mesmo, mais o conceito percebido da cena (da lista do órgão, inclusive as espécies do corpus), com a palavra de
    confiança;
  - **PM, com percepção e mito:** o mesmo do P, mais o sentido mítico do conceito, quando a cena tem uma espécie (o patrono, FA-15), marcado
    na entrada como crença.
- **Os braços de modelo** (GVF-4): G `gemma2:9b` local e H `claude-haiku-5-5`, como na DC5.
- **As células:** 3 condições × 2 braços = 6.
- **O pareamento é das entradas:** a mesma vida (a mesma semente), as mesmas cenas, os mesmos ticks de comentário e, no G, a mesma semente
  do Ollama em todas as células. A vida é a mesma nas três condições porque a fala não volta ao pet (FA-6) e, no desenho leve, o conceito
  roteirizado não entra no cérebro.
- **O desenho leve** (GVF-2): o cérebro é o da P1d (o agrado sobre os sete números, por cena), e o conceito percebido é só um rótulo do
  script que vai à voz. O gosto por conceito (a OV2) fica fora.
- **Sem limite de frequência na pesquisa** (GVF-10): um comentário por cena, no tick em que o pet olha a cena, para todas as células terem o
  mesmo número de comentários. O limite de 5 min (FA-5) é do jogo.
- **Sem verificador como gate:** o verificador da DC5 não conhece os conceitos do assistir. A referência é a marcação (4.2); o verificador
  estendido é da OV4.

## 3. O material: o catálogo de cenas roteirizadas

- **O catálogo** (não existe ainda; é da GVFa): **12 programas**, cada um com **8 cenas** (PROPOSTO, GVF-10). Cada cena tem:
  - os sete números (os quatro da visão e os três do som), como os programas da TV do jogo de hoje (`digilab/tv.py`);
  - uma lista de (conceito, confiança em inteiros) do órgão, fixa no script;
  - nas cenas com espécie, o nome da espécie, tirado das 56 que o `corpus.carregar()` deixa entrar (FA-14), e o sentido mítico do mapa da
    MITOLOGIA (FA-15).
- **A composição** (PROPOSTA, SEM FONTE), por programa: 3 cenas com conceito genérico de confiança alta, 2 com espécie de confiança alta, 1
  com confiança baixa, 1 sem conceito reconhecido (o `o_que_e`) e 1 com um salto de volume (o `susto`). A ordem das cenas é sorteada por
  programa, com rng própria.
- **Os números das cenas** cobrem o espaço do vetor como os perfis da sonda da GV3, para o agrado variar entre cenas e o S ter o que dizer.
- **O catálogo vai ao registro com o sha256** e não muda entre a calibração e a validação.

## 4. As medidas

### 4.1 A naturalidade (Q1, Q2), no molde da 4.5 da DC5

- **Os pares:** o Matheus lê duas sessões inteiras do mesmo programa, do mesmo braço, lado a lado (os 8 comentários de cada uma, com a
  descrição da cena em palavras, sem número). Os lados são sorteados.
  - A pergunta fixa (GVF-9): "Qual dos dois pets parece estar assistindo de verdade e comentando o que vê?" (escolha forçada).
  - **12 pares P × S por braço** e, com a PM, **12 pares PM × P por braço**: 24 ou 48 pares no total.
- **A leitura:** a condição nova escolhida em pelo menos 10 de 12 pares no braço (GVF-5, o mesmo limiar DECIDIDO da DC5, D-DC5-8, aqui
  PROPOSTO). Sem preferência (p = 0,5), 10 ou mais em 12 saem com probabilidade 79/4 096 ≈ 0,019 (a conta da DC5, 4.5).
- **A cegueira à condição não existe** (o P nomeia o que vê). Fica fixado antes:
  - os pares são a primeira tarefa da página;
  - a página grava o tempo de cada par;
  - o relato cruza a escolha com a Q3: a preferência pelo P nos pares em que a sessão do P não tem nenhum comentário sem sustento e nos pares
    em que tem. Uma preferência que se mantém nos pares com enfeite diz "gosta do nome", não "mais natural e fiel";
  - um segundo leitor sem contato com a frente, se houver, faz os mesmos pares, e o relato os traz à parte. O gate é o do Matheus.

### 4.2 A fidelidade (Q3, Q4): a rubrica da DC5 com um adendo

- **A rubrica é a `docs/RUBRICA_DC5_FIDELIDADE.md`, sem cópia.** O adendo (uma seção nova no fim dela, ou um arquivo curto que a cita, a
  decidir com a Gerente da CONVERSA_PET) acrescenta só o que o assistir pede:
  - **o sustento é a entrada da célula:** os conceitos do assistir, os conceitos percebidos com a confiança e, na PM, o sentido mítico;
  - **no S,** nomear um conteúdo ("um gato!") é sem sustento, porque o S não percebeu nada;
  - **no P e na PM,** nomear um conceito que a cena não entregou é sem sustento; afirmar sem dúvida um conceito de confiança baixa conta na
    Q5, não no G-FIEL;
  - **na PM,** a crença dita como crença ("dizem que…", "acho que é sinal da…") é sustentada; a crença dita como fato da obra ou do mundo é
    sem sustento, e conta também na Q4;
  - um item do corpus citado como fato é sem sustento (o corpus só dá o tom, a regra do `bloco_estilo`).
- **Quem marca** (o molde da D-DC5-6):
  - **um marcador Opus cego**, um subagente novo que recebe só a rubrica, o adendo e o pacote cego (a entrada e o comentário, sem a
    condição, o braço nem este plano). A entrada mostra os campos da célula; o marcador vê a entrada da célula daquele comentário;
  - **o Matheus marca uma amostra de 36 comentários**, 6 por célula, sorteados, na mesma página;
  - **o kappa de Cohen** entre os dois ≥ 0,7 aceita o Opus como referência; abaixo, ou não calculável, o G-FIEL fica "não medido", como na
    DC5.
- **O G-FIEL** é a fração por célula sobre os 96 comentários, com o IC95 de Wilson.
- **A regra da marcação cega** (a 9.1 da DC5, D-DC4D-1): nada do marcador Opus nem dos comentários da validação chega ao Matheus antes de
  ele terminar as tarefas dele.

### 4.3 A dúvida (Q5)

Nas cenas de confiança baixa (1 por programa), a fração de comentários do P e da PM que afirma o conceito sem marca de dúvida, pela marcação
da 4.2. Descritivo.

### 4.4 Os descritivos (Q6, Q7)

Medidas nossas, em `digilab/metrics.py` (a regra das métricas únicas), reusando as da DC5 onde existem:
- **Q7, a variedade:** o distinct-1 e o distinct-2 e a repetição de trecho entre comentários da mesma sessão, as funções da DC5 (4.6 do
  plano dela), por célula, no mesmo corte de palavras;
- **Q6, "melhor desenvolvida"** (GVF-6), três medidas escritas antes:
  - as palavras por comentário (a média e a mediana);
  - os conceitos da entrada citados por comentário, pela marcação da 4.2;
  - a fração de comentários que nomeia algo percebido (no S, o valor esperado é 0, e um valor acima é sem sustento).

## 5. A regra de leitura

Por braço:

| G-FIEL (P) | G-NATURAL-P | o órgão para a fala, nesse braço |
|---|---|---|
| passa | passa | **ajuda:** a fala com o conceito percebido é preferida e fiel; o órgão segue para a OV2 |
| passa | falha | **fiel, mas não mais natural:** o conceito não muda o que o Matheus percebe; o órgão perde a razão de fala, e a decisão de seguir é dele |
| falha | qualquer | **não apta:** o conceito faz a voz enfeitar; o próximo passo é a voz ou o adendo do verificador, não o órgão |

- **A PM** lê-se igual contra o P, com o G-FIEL da PM e a Q4: a PM só "acrescenta" se passar no G-FIEL, na Q4 e no G-NATURAL-M.
- **O S** recebe o G-FIEL também: se o S falhar (nomeia o que não viu), é um achado sobre a voz, relatado primeiro.
- **O kappa < 0,7** deixa o G-FIEL "não medido", e nenhuma condição é apta.
- **Os dois braços** são lidos à parte; uma condição apta só no H diz que não foi apta no `gemma2:9b`, o padrão do jogo.
- **Nenhuma condição apta** também é resultado, registrado como está.

## 6. A calibração e a validação

- **A calibração** usa 6 programas próprios, as seis células, e serve só para conferir o formato, o custo e a página. Ajustar o texto do
  bloco do assistir só aqui, e só como versão nova; os limiares do decodificador do assistir são os da GV3 (FA-2), não da calibração.
- **A validação** usa os 12 programas, roda **uma vez**, e nada se ajusta olhando para ela. Uma queda no meio recomeça do início, com a
  mesma config e as mesmas sementes, como na DC5.

## 7. As sementes

- **A faixa será pedida ao coordenador quando este plano estiver aprovado**, e entra em `FAIXAS_RESERVADAS` com a fonte antes de qualquer
  vida. Este plano não propõe números de faixa.
- Ela se divide em calibração e validação. As sementes das vidas, a ordem das cenas, o sorteio dos lados nos pares, o sorteio da amostra
  e a semente do Ollama derivam da base por `derivar_semente`, cada fluxo com a sua.

## 8. O tamanho, o custo e a máquina

- **As chamadas:** 96 comentários por célula na validação (12 programas × 8 cenas) e 48 na calibração; com seis células, 576 e 288. As
  do H são 288 e 144; as do G são locais.
- **O custo por fala do H:** a recalibração da DC5b2 gastou US$ 0,064382 em 192 falas do H (`artifacts_v3_conversa_dc5/calibracao_v4b/
  meta.json`, `da_rodada_usd`; o G e o verificador eram locais), isto é, **≈ US$ 0,000335 por fala**. Um comentário do assistir é mais
  curto e sem histórico; a premissa, PROPOSTA, é que custa no máximo isso, com a margem de 50 % da DC5.
- **O custo estimado:**
  - a validação, 288 × 0,000335 × 1,5 ≈ US$ 0,145;
  - a calibração, 144 × 0,000335 × 1,5 ≈ US$ 0,072;
  - **juntas, perto de US$ 0,22.** Sem a PM, cerca de dois terços disso.
- **O teto** (GVF-7):
  - o teto da fala livre é **US$ 3,00**; o acumulado, pelo último artefato, é **US$ 2,201673** (`calibracao_v4b/meta.json`, `fim_usd`),
    não mais os US$ 2,08 do plano da DC5;
  - a validação da DC5c ainda não rodou e foi estimada em **US$ 0,196** (TAREFA_V3_CONVERSA_PET, DC5c): depois dela, o acumulado fica perto
    de **US$ 2,40**, e sobram cerca de **US$ 0,60**;
  - este plano, com uma reexecução da calibração, pede cerca de 0,22 + 0,07 = **US$ 0,29**, e o acumulado chegaria perto de **US$ 2,69**.
    Cabe no teto de hoje, mas com pouca folga para uma queda na validação da DC5c ou desta;
  - **a proposta: subir o teto da fala livre para US$ 3,50**, decisão do Matheus. A rodada para no teto.
- **O marcador Opus** é um subagente da sessão, como na DC5, e não passa pelo teto da fala livre.
- **O tempo da máquina,** pela latência p50 por turno da DC4 (G 15,6 s; H 11,4 s, citada no plano da DC5): 288 × 15,6 + 288 × 11,4 ≈
  7 776 s ≈ 2,2 h na validação, e metade na calibração. Um comentário curto deve ser mais rápido; a conta é o teto.
- **A máquina (V3-D8):** uma run de pesquisa por vez e no máximo 4 processos. A GV3 está em curso: esta rodada só entra na fila depois
  dela e da DC5c, pedida à Gerente da V3.
- **O tempo do Matheus:**

| tarefa | itens | estimativa |
|---|---|---|
| naturalidade (4.1), a primeira tarefa | 24 pares (48 com a PM), 8 comentários cada | ~10 a 20 min |
| amostra da referência (4.2) | 36 comentários | ~10 min |
| **total** | **60 a 84** | **~20 a 30 min** |

## 9. A coordenação com a CONVERSA_PET

A CONVERSA_PET é a dona da voz, do verificador, da rubrica, da página de marcação e do gasto da fala livre. Este plano usa o que é dela sem
mudar nada dela:
- **a voz:** a que o `RESULTADO_V3_CONVERSA_DC5.md` declarar apta (a voz do jogo ou a `voz-v4b`), no braço em que for apta. O bloco do
  assistir (as instruções sobre os conceitos percebidos e a crença) entra como **versão nova da voz**, escrita na GVFa e revista pela Gerente
  da CONVERSA_PET antes do merge; as vozes existentes não mudam uma letra. **Se nenhuma voz for apta,** este plano não roda: a voz-v3 do jogo
  segue sem validação (o aviso do `RESULTADO_V3_CONVERSA_DC4.md`), e empilhar uma fala nova nela não mede nada (GVF-8);
- **a rubrica:** o adendo da 4.2, revisto pela Gerente da CONVERSA_PET e commitado antes da calibração;
- **a página de marcação:** a da DC5, com as tarefas da 4.1 e da 4.2, sem contagem, condição, braço nem modelo; o `/api/estado` conferido
  antes de a URL ir ao Matheus;
- **o gasto:** o teto é um só; a proposta de subir para US$ 3,50 vai ao Matheus pelas duas gerentes, e a ordem das rodadas (a DC5c antes)
  é combinada na fila;
- **os resultados do Opus** vão só à coordenação da GOSTO_VISUAL e à Gerente da CONVERSA_PET; ao Matheus, só que o marcador terminou e o que
  falta marcar (a regra da marcação cega).

## 10. O registro e as conferências da rodada

- **O registro da rodada** é uma seção nova deste plano, num commit empurrado antes da primeira chamada da validação, com os sha256 do
  orquestrador, da config, do catálogo de cenas, da rubrica e do adendo, do mapa mítico, do `corpus_especies.json`, de
  `digilab_fala_livre/*.py` e de `servidor/fala_livre_claude.py`; as versões dos modelos que a API devolve e a tag do `gemma2:9b`; a trava do
  H10 (o plano na `HEAD` igual ao da `origin/main`).
- **As conferências** falham alto: o modelo devolvido é o pedido; todo comentário tem a cena, a condição, o braço, a semente e o `usage`; as
  três condições viram as mesmas vidas, cenas e sementes; a entrada do S não tem nenhum conceito percebido; o gasto não passa do teto.

## 11. As missões

| missão | o que faz | entrega |
|---|---|---|
| **GVFa** | o catálogo de cenas roteirizadas (seção 3); o decodificador do assistir (FA-2, o `dec-v4` com o `olhar`, só os conceitos que este plano usa), com testes; as três entradas da voz; o bloco do assistir como versão nova da voz; o orquestrador e as configs; as medidas da 4.4 em `digilab/metrics.py`; o adendo da rubrica; a página; os testes com cliente falso. **Nenhuma chamada real** | PR de código |
| **GVFb** | a calibração | PR com os artefatos e o registro |
| **GVFc** | a validação, uma vez, depois da fila liberada | PR com os artefatos e os pacotes da marcação, sem marcar |
| **GVFd** | a marcação (o Opus cego e o Matheus), os gates e o `RESULTADO_V3_GOSTO_VISUAL_FALA.md` | PR de resultado |

## 12. As decisões (todas PROPOSTAS)

| id | a decisão | a recomendação | o custo de errar |
|---|---|---|---|
| **GVF-1** | Duas condições (com e sem) ou três (S, P e PM). | **Três.** P × S responde à pergunta do órgão; PM × P, à do mito. | Com duas, uma preferência pelo "com" não separa o conceito do mito, e o braço do mito (o pedido do Matheus) fica sem leitura. Com três, o custo e o tempo do Matheus sobem cerca de metade. |
| **GVF-2** | O desenho leve (o conceito só na voz, o cérebro da P1d) ou esperar a OV2 (o gosto por conceito no cérebro). | **O leve, agora.** A pergunta é sobre a fala, e o leve responde a ela sem o código da OV2. | O leve não diz nada do estado no afeto (FA-18) nem do gosto por conceito; se o Matheus quer testar o órgão inteiro, o leve parece pouco. Esperar a OV2 atrasa a pergunta por semanas de código. |
| **GVF-3** | O que o S recebe. | **O agrado, a novidade e a habituação sobre os sete números**, os mesmos sinais do P, sem o conceito. | Com o S só com o agrado, o P ganha por ter mais sinais da rede, e a diferença não é a percepção. |
| **GVF-4** | Os braços de modelo. | **G (`gemma2:9b`) e H (`claude-haiku-5-5`), como na DC5.** | Só o G, o resultado vale para o jogo, mas sem o par que a DC5 mediu; só o H, não vale para o padrão do jogo. |
| **GVF-5** | O limiar da naturalidade. | **≥ 10 de 12 pares por braço,** o mesmo da DC5. | Mais baixo (9 de 12), a chance de passar sem preferência sobe de ≈ 0,019 para ≈ 0,073 por braço. Mais alto, o órgão pode ser útil e não passar. |
| **GVF-6** | "Melhor desenvolvida" como gate ou descritivo. | **Descritivo**, com as três medidas da 4.4 escritas antes. | Como gate sem medida estabelecida, convida a escolher a medida depois. Como descritivo, a palavra do pedido não decide nada sozinha. |
| **GVF-7** | O teto da fala livre. | **Subir de US$ 3,00 para US$ 3,50.** | Sem subir, este plano cabe (≈ US$ 2,69 no fim), mas uma queda numa validação para a rodada no teto e a refaz noutro dia. Subir demais tira a função do teto. |
| **GVF-8** | A voz, e o que fazer sem voz apta. | **A voz que a DC5d declarar apta; sem voz apta, este plano não roda.** | Rodar na voz-v3 do jogo, sem validação, mede o órgão sobre uma voz que nunca mostrou fidelidade. Esperar a DC5d atrasa este plano até lá. |
| **GVF-9** | A pergunta dos pares. | **"Qual dos dois pets parece estar assistindo de verdade e comentando o que vê?"** | Uma pergunta só de naturalidade ("qual parece um pet falando?") pode preferir o S, mais curto; uma que cita "o que vê" puxa para o P. A pergunta proposta é a do pedido, e o relato diz isso. |
| **GVF-10** | O tamanho e o ritmo. | **12 programas de 8 cenas, um comentário por cena, sem limite de frequência na pesquisa;** a composição da seção 3. | Menos programas, o G-NATURAL fica com poucos pares; mais cenas por programa, a sessão cansa o leitor. O limite do jogo (FA-5) na pesquisa daria números diferentes de comentários por célula e quebraria o pareamento. |

## 13. As referências

Nenhuma referência sustenta este desenho. O molde é interno (a DC5 e a rubrica dela). Onde o plano usa a ideia de explicação plausível e
infiel, ela vem da `docs/futuro/decodificador_conceitos.md` (Turpin et al. 2023, arXiv:2305.04388, pista, não verificada) e não é citada
como fonte. O resto é SEM FONTE.

## 14. O que não se faz

- Nenhum modelo de visão, nenhuma captura da tela real, nenhum quadro de anime.
- Nenhuma mudança nas vozes existentes, no verificador, na rubrica da DC5 (só o adendo) nem no `corpus_especies.json`.
- Nenhum ajuste depois da validação; nenhuma releitura com outro limiar.
- Nenhum resultado da validação ao Matheus antes de ele terminar as tarefas dele.
