# DEFINIÇÕES DAS FRUTAS NA V2 — necessidade, gosto, efeito e vício

Status: **PROPOSTO, para revisão do Matheus** (2026-10-01). Tarefa `docs/TAREFA_V2_FRUTAS_DEFINICOES.md`, nó N4 do `docs/ROADMAP_V2.md`.
**Só papel:** nenhum código, nenhuma equação final, nenhum número de balanceamento e nenhuma run. O desenho é do Matheus; aqui ficam as
definições operacionais que o desenho precisa respeitar, cada uma com a justificativa e o lugar onde ela é registrada.

**Por que as frutas importam para a pergunta maior.** A pergunta da V2 (`docs/ARQUITETURA_V2_VALIDACAO.md`, seção 6; adotada pelo Matheus,
decisão M3 do roadmap) pede um ambiente que **contradiga a predisposição herdada**: o mundo "descasado". A bola não contradiz nada do
instinto. As frutas contradizem se uma fruta preferida de nascença tiver efeito ruim. Sem as frutas, a condição descasada não existe.

**Fontes.** Busca V1–V6 (2026-10-01), agora no repositório: `docs/referencias/V3_SINTESE_FRUTAS_VICIO_V1_V6.md` e
`docs/referencias/v3_referencias_verificadas.csv` (38 linhas). Para consequência pós-ingestiva, a busca da V2: `docs/referencias/V2_SINTESE_Q1_Q7.md`
e `v2_referencias_verificadas.csv`. Para RL homeostático e traços, a revisão de 2026-09-29: `docs/referencias/referencias_verificadas.csv`.
Regras de citação: `docs/referencias/REGRAS_CITACAO_DIGILAB.md`. O rótulo da coluna `verificada` é vinculante. Toda referência citada aqui é
**VERIFICADA**; quando a verificação foi só por título e metadados (sem resumo lido), isso vem marcado ao lado. Nada NÃO LOCALIZADA é citado.

**Não reabre nada.** A hipótese central da v1 segue refutada, a linhagem segue encerrada como pesquisa e a pergunta do efeito do dono neste
motor segue encerrada (`docs/LEITURA_CONSOLIDADA_DONO.md`). As frutas são uma alavanca de ambiente para o aprendiz novo.

---

## 0. Em uma página

| variável | o que é, operacionalmente | onde mora | quando muda |
|---|---|---|---|
| **necessidade** | o déficit de fome que já existe (`Estado.fome`, 1 = saciado; `digilab/state.py`) | estado (camada 1) | como hoje; nenhuma regra nova |
| **querer** | o **incentivo** do pet por uma fruta: a tendência de escolhê-la e de se aproximar **antes** de comer | registro derivado, por fruta | quando o pet escolhe, ignora ou come |
| **gostar** | a **avaliação** de uma fruta: a resposta registrada **depois** de comer, por fruta | registro derivado, por fruta | só depois de um consumo, e pelo consumo recente daquela fruta |
| **efeito** | a consequência da fruta no corpo (drives), separada do gosto | parâmetro por fruta, aplicado pelo motor | a cada consumo |
| **vício** | não é um terceiro registro: é a **assimetria** em que o incentivo de uma fruta cresce com a exposição enquanto a avaliação não acompanha | dinâmica entre os dois registros | só no nó N9, depois das frutas sem vício |
| **neofobia** | relutância diante de uma fruta nunca comida | genoma (traço do ovo) | nunca durante a vida |
| **preferência inata** | o ponto de partida da avaliação de cada fruta | genoma (traço do ovo) | nunca durante a vida; a avaliação aprendida parte dele |

As frutas entram como **sub-decisão de `comer`**, como a bola entrou em `brincar` (`docs/V2_A1_BOLA_DESENHO.md`, opção A): nenhum membro novo
em `events.AcaoPet`. O dono **oferece** frutas; quem escolhe e come é o pet. Comida é canal de cuidado, então todo braço com frutas tem o "só
cuidado" acoplado com **as mesmas ofertas**.

---

## 1. Onde cada coisa é registrada: log × registro derivado

A regra do projeto fixa o que pode entrar no log (`digilab/events.py`): só o que vem de fora do pet (ações do dono, avanço do tempo e, desde a
educação-v1, `luta`, `origem`, `decisao_externa` e `fala`). **As ações do pet não entram no log:** são o que a política produz ao reprocessar
o log. Por isso "o campo do log" de cada restrição é de um destes três tipos, e o tipo é dito em cada uma:

| tipo | o que é | exemplo nas frutas |
|---|---|---|
| **evento** | entra no log de eventos; é causa externa | o dono oferece a fruta *f* (`acao_usuario`) |
| **registro derivado** | reconstruído pelo replay, nunca escrito à mão; exposto em `estado_interno()` e nos artefatos | o incentivo e a avaliação de cada fruta; cada consumo |
| **genoma** | sai da semente do ovo (sem evento) ou do evento `origem` (filhos) | neofobia; preferência inata por fruta |

O replay reconstrói os registros derivados bit a bit (G1). Nenhum número desses registros é gravado como dado de entrada.

### 1.1 Eventos (só o que o dono faz)

- **Oferecer uma fruta:** um membro novo **no fim** de `events.AcaoUsuario` por fruta (`oferecer_fruta_<id>`), entrando no log como
  `acao_usuario` de sempre (`tick`, `tipo`, `valor`). Precedentes: os seis `treinar_*` (um botão por exercício) e o `por_bola` da A1. Nenhum
  tipo de evento novo. Os donos da v1 sorteiam de `ACOES_V1` (tupla explícita), então o enum crescer não muda a canônica.
- **A fruta fica no cenário** até ser comida ou até um prazo, como a bola. Oferecer a mesma fruta com ela já no cenário renova o prazo.
- **Oferecer não é cuidado e não é contato** (não zera `tick_ultimo_cuidado`, não conta em `total_cuidados`), como o `por_bola`. Assim o
  relógio do instinto é o mesmo em todos os braços, e o canal de cuidado continua sendo `alimentar`.
- **`alimentar` não muda:** é a ração do cuidado, sem fruta, sem escolha. As frutas nunca entram pela boca do pet por ação do dono; entram
  pela escolha do pet. Sem escolha não há o que medir no querer.
- **Modo livre gravado:** se a escolha entre frutas vier de LLM ou de acaso real, ela entra como `decisao_externa` com `ponto: "fruta"`, como
  as outras decisões externas.

### 1.2 A sub-decisão de `comer`

| a política escolheu | com frutas no cenário | sem fruta |
|---|---|---|
| `comer` | o pet **escolhe uma das frutas** e a come: aplica o efeito dela, atualiza os registros, a fruta sai do cenário | come como hoje |
| qualquer outra | ignora as frutas nesta decisão; elas ficam até o prazo | como hoje |

- A escolha **entre frutas** é da política (o aprendiz da V2), não de uma regra fixa: é ela que expressa o querer.
- Se a escolha usar sorteio, ele vem de uma **rng própria**, `derivar_semente("fruta", semente)`, consumida em **toda** decisão `comer` de
  todos os braços, haja fruta ou não (números comuns, como a `rng_travessura`). Nunca a rng de ambiente nem a de política.
- Para a escolha medir alguma coisa, o desenho precisa de **pelo menos duas frutas no cenário ao mesmo tempo** em parte das ofertas: com uma
  só, "comer" e "querer aquela fruta" se confundem.

### 1.3 Registros derivados (nomes PROPOSTOS, sem acento)

| registro | conteúdo por entrada | quando entra uma linha |
|---|---|---|
| `oferta` | tick, frutas no cenário, fruta escolhida (ou nenhuma), ação do pet | a cada decisão do pet com fruta no cenário |
| `consumo` | tick, fruta, fome antes, incentivo antes, avaliação antes e depois, efeito aplicado, consumo recente daquela fruta | a cada fruta comida |
| `incentivo[fruta]` | o valor do querer daquela fruta | atualizado em `oferta` e `consumo` |
| `avaliacao[fruta]` | o valor do gostar daquela fruta | atualizado só em `consumo` |
| `primeiro_contato[fruta]` | o tick do primeiro consumo, ou vazio | no primeiro `consumo` |

Esses registros são do motor da camada de ambiente (a mesma família do `MotorAmbiente` da bola), não da `Observacao` (congelada) nem do
bandit (congelado).

---

## 2. As sete restrições

### 2.1 Gostar e querer são dois registros, não um escalar

**Definição.** O pet tem, por fruta, **dois** valores separados: `incentivo` (querer: tendência de escolher e de se aproximar, medida antes de
comer) e `avaliacao` (gostar: resposta medida depois de comer). Nenhum dos dois é calculado a partir do outro. A escolha do pet lê o incentivo;
a avaliação só alcança a escolha **através** de uma atualização do incentivo, que o desenho tem de declarar.

**Justificativa.** Gostar, querer e aprender são componentes dissociáveis da recompensa (Berridge e Robinson 1998,
`10.1016/s0165-0173(98)00019-8`; Berridge, Robinson e Aldridge 2009, `10.1016/j.coph.2008.12.014`; para comida, Morales e Berridge 2020,
`10.1016/j.physbeh.2020.113152`; todos VERIFICADA). Medir os dois exige **instrumentos separados** (Finlayson e Dalton 2012,
`10.1016/j.appet.2011.10.011`, VERIFICADA): no simulador, dois registros. É neurociência de mamíferos, não de agentes; o projeto adota a
separação como desenho, não como afirmação sobre o pet.

**O que a separação proíbe.** Usar a **taxa de escolha** como medida do gostar. A escolha mistura fome, acesso, novidade, incentivo aprendido,
hábito e efeito (`docs/research/digibrain/mechanisms/hedonic_system.md`, riscos). As medidas são quatro, separadas: aproximação (escolher a
fruta numa `oferta`), consumo, avaliação depois do consumo e escolha posterior com o mesmo estado.

**Registro.** `incentivo[fruta]` e `avaliacao[fruta]` (registros derivados); `oferta` e `consumo` (seção 1.3). Nenhum evento novo.

### 2.2 Vocabulário operacional: nada afirma que o pet sente prazer

**Definição.** No motor, no log, nos artefatos e na fala, as frutas só têm nomes de **comportamento** ou de **medida**: `incentivo`,
`avaliacao`, `consumo`, `escolha`, `efeito`. Ficam fora dos identificadores, dos fatores do motivo e dos textos de fala: "prazer", "delícia",
"gostoso", "saboroso", "sente", "adora" e equivalentes. A fala descreve escolha e conduta ("escolhi a vermelha de novo", "deixei a amarela de
lado"), nunca sensação. Os nomes informais "gostar" e "querer" ficam só nos documentos de estudo, como aqui.

**Justificativa.** Berridge (1996, `10.1016/0149-7634(95)00033-b`, VERIFICADA) pergunta se recompensa e prazer são idênticos e se o prazer
gustativo **pode** ser avaliado em animais; a literatura mede **reação hedônica**, não experiência relatada (`V3_SINTESE_FRUTAS_VICIO_V1_V6.md`,
V1). Nada autoriza dizer que um agente sente prazer.

**Ponto cinzento, para decisão (F2):** a palavra "gosto" na boca do pet ("gosto da vermelha") é preferência ou sensação? A recomendação é tirá-la
dos textos de fala das frutas, porque o jogador lê sensação.

**Registro.** Nomes dos registros (seção 1.3); fatores do motivo das frutas (`fruta_no_cenario`, `incentivo_<fruta>`, nomes PROPOSTOS), com a
mesma regra de honestidade de hoje (só vira fator o que mudou a escolha). Na fala livre, a regra entra no verificador da implementação.

### 2.3 Gosto não deriva de necessidade

**Definição.** A avaliação de **uma** fruta cai com o **consumo recente daquela fruta** e não com a fome. A fome não entra na atualização da
avaliação. Comer a fruta *f* não mexe na avaliação das outras frutas. A queda é reversível com o tempo sem consumo de *f*. A fome continua
mexendo no que já mexe (prioridade de comer, privação, saúde), e pode mexer no **incentivo** se o desenho quiser; nunca na avaliação.

**Justificativa.** Saciedade sensório-específica: o quanto um alimento é agradável cai mais para o alimento comido até a saciedade do que para os
outros (Rolls, Rolls e Rowe 1983, `10.1016/0031-9384(83)90003-3`, VERIFICADA com resumo lido); o artigo de 1981 que estabelece o fenômeno em
humanos (Rolls et al., `10.1016/0031-9384(81)90310-3`) está **VERIFICADA só por título e metadados**, e a afirmação usada aqui é a do de 1983.
Saciedade sensório-específica e fome são canais distintos; tratá-los como um só colapsa gosto em necessidade (`V3_SINTESE_FRUTAS_VICIO_V1_V6.md`,
V4).

**Teste que a implementação deve permitir (H-HED-03).** Mesma fome, consumo recente diferente de *f*: a avaliação de *f* difere; a das outras
frutas não.

**Registro.** No `consumo`: `fome_antes` e `consumo_recente` de *f* lado a lado, para que a análise mostre que a avaliação segue o segundo e não o
primeiro. `consumo_recente[fruta]` é registro derivado (função dos consumos passados no log reconstruído).

### 2.4 Neofobia é traço do ovo; gosto aprendido é estado

**Definição.**
- **Neofobia:** um valor por pet, do **genoma**, fixo na vida. Age só sobre frutas **nunca comidas** (`primeiro_contato` vazio): reduz o
  incentivo de partida delas. Depois do primeiro consumo, ela não age mais sobre aquela fruta.
- **Preferência inata:** um valor por fruta, do **genoma**, fixo na vida: o ponto de partida da avaliação daquela fruta. É a "predisposição
  herdada" que o mundo descasado contradiz.
- **Gosto aprendido:** o que a avaliação e o incentivo viraram depois da experiência; é **estado**, reconstruído pelo replay, nunca herdado
  (`digilab/heranca.py` já não herda nada aprendido).

**Justificativa.** Neofobia alimentar é **traço** individual mensurável (Pliner e Hobden 1992, `10.1016/0195-6663(92)90014-w`, VERIFICADA).
Preferência inata modulada por exposição (Beauchamp e Moran 1982, `10.1016/s0195-6663(82)80007-x`, **VERIFICADA só por título e metadados**).
Traços vêm em síndromes correlacionadas, não independentes (Sih, Bell e Johnson 2004, `10.1016/j.tree.2004.04.009`, VERIFICADA): é o argumento
contra e a favor de amarrar a neofobia ao eixo `curiosidade` que já existe (decisão F4).

**Onde mora no genoma (proposta).** Fora do `Temperamento` de 4 eixos (`digilab/temperamento.py`), com **rng própria** derivada da semente do
ovo (`derivar_semente("frutas-ovo", semente)`), para que o sorteio dos 4 eixos, os artefatos da v1 e a paridade da web não mudem. Nos filhos, o
`Genitor` do evento `origem` passa a levar os genes das frutas, como já leva o temperamento (`heranca.Genitor.para_dict`).

**Teste que a implementação deve permitir (H-HED-04).** Com o aprendizado desligado, genomas com neofobia diferente diferem só antes do primeiro
contato com cada fruta.

**Registro.** Genoma: `neofobia` e `preferencia_inata[fruta]` (sem evento no ovo; no `origem` dos filhos). Estado: `primeiro_contato[fruta]`,
`incentivo` e `avaliacao` (registros derivados).

### 2.5 Vício como assimetria

**Definição.** Vício é uma **dinâmica entre os dois registros**, não um terceiro registro: sob exposição repetida a uma fruta, o **incentivo**
dela cresce enquanto a **avaliação** não acompanha (fica igual ou cai). É o que distingue vício de preferência forte, em que os dois andam juntos.
A medida é a divergência entre a trajetória do incentivo e a da avaliação da mesma fruta, com o **efeito nutricional fixo** (para não confundir
vício com a fruta simplesmente alimentar mais).

**Justificativa.**
- A teoria: sensibilização de incentivo (Robinson e Berridge 1993, `10.1016/0165-0173(93)90013-p`, VERIFICADA; a lista de autores foi conferida
  no Europe PMC porque o Crossref traz um autor só); questões abertas em 2008 (`10.1098/rstb.2008.0093`) e exposição recente em 2016
  (`10.1037/amp0000059`), ambas VERIFICADA.
- O teste empírico do desacoplamento em humanos: querer implícito sem gostar implícito (Grigutsch et al. 2019, `10.1016/j.jbtep.2019.01.002`,
  VERIFICADA). É teste em laboratório, não etiologia.
- **A ressalva, sempre junto:** décadas tratando a adicção como transtorno dopaminérgico não produziram tratamentos novos, e o papel causal da
  dopamina é contestado (Nutt et al. 2015, `10.1038/nrn3939`, VERIFICADA). A assimetria tem o melhor suporte entre as peças de um mecanismo de
  vício; a atribuição causal, não.

**Derivar do RL homeostático ou mecânica nova: avaliação.**
- Keramati, Durand e Girardeau (2017, `10.1037/rev0000046`, VERIFICADA) tratam a adicção como **transtorno de aprendizado por reforço
  homeostático**, unindo recompensa e regulação de necessidade; a base é recompensa como redução de desvio homeostático (Keramati e Gutkin 2014,
  `10.7554/elife.04811`, VERIFICADA).
- **O projeto não tem do que derivar hoje.** O instinto são regras escritas à mão sobre os drives, sem aprendizado (`digilab/policy.py`); o
  único aprendiz da V2 aprende com o sinal do dono (L1). Valor homeostático como reforço é o nó **N3**, que ainda não existe
  (`docs/ARQUITETURA_V2_VALIDACAO.md`, seção 3, correção 4). "Derivar do que já existe" seria, na prática, aprendizado **novo** sobre os drives.
- O que já existe e serve de precedente é só a **vulnerabilidade por genoma**: o temperamento escala a resposta ao reforço (validação V8 do
  roadmap), e um modelo computacional dá vulnerabilidade variando por indivíduo (Piray et al. 2010, `10.1162/neco_a_00009`, VERIFICADA). No E1
  esse genoma explicou 4,9% da variância (`artifacts_linhagem/natureza_criacao/especie_fixa/resultado.json`).
- **Recomendação: mecânica nova e explícita no canal hedônico, que entra no nó N9, depois do N3 e das frutas sem vício.** Com o N3 pronto, a
  derivação de Keramati et al. vira um braço possível do plano do N9, não um atalho. A forma funcional, se o plano precisar, vem de Redish (2004,
  `10.1126/science.1102384`, VERIFICADA: um sinal de erro de predição que não se extingue) ou de Keramati et al., **como forma, nunca como
  validação**: são modelos de droga, calibrados em roedor e humano, que reproduzem fenômenos e não demonstram mecanismo, e nenhum é de comida.
- A pergunta maior (decisão A6 da arquitetura) não depende do vício: P0–P3 × casado/descasado/mutável roda com as frutas sem vício.

**Registro.** As trajetórias de `incentivo[fruta]` e `avaliacao[fruta]` ao longo dos `consumo` daquela fruta (registros derivados); o efeito
aplicado em cada `consumo`, para provar que ficou fixo.

### 2.6 Confundidor de canal: comida é cuidado

**O problema.** Fome → privação → saúde → morte (`digilab/state.py`). Um efeito que passe por aí é **cuidado**, não ensino: é a leitura
consolidada da v1 (`docs/LEITURA_CONSOLIDADA_DONO.md`). E a consequência pós-ingestiva ensina **o animal**, sem treinador no laço (Sclafani 2001,
`10.1006/appe.2000.0370`; de Araujo et al. 2008, `10.1016/j.neuron.2008.04.003`, **VERIFICADA só por título e metadados**; Bodnar 2018,
`10.1016/j.appet.2016.12.015`, VERIFICADA, com a autoria corrigida no `REGISTRO_DESVIOS.md`): um efeito das frutas no pet é, por padrão, do pet.

**Definição: dois controles e um critério.**
1. **"Só cuidado" acoplado com as mesmas ofertas.** Para cada vida de um braço que ensina, um braço com a mesma semente, **as mesmas ações de
   cuidado e as mesmas ofertas de fruta nos mesmos ticks**, copiadas do registro (o modo acoplado da bancada, `docs/TAREFA_V2_BANCADA.md`;
   `log_so_cuidado`/`vidas_acopladas` da L1, validação V3 do roadmap), **sem nenhum sinal de ensino** (elogio, bronca e, quando existir, a
   informação do dono do N5). Acariciar segue a decisão D4 de `docs/DEFINICOES_V2.md` (cuidado no braço principal, sem acariciar como
   sensibilidade). Assim a exposição às frutas e a nutrição são as mesmas; só o ensino some.
2. **Variante de efeito igual.** Uma variante em que todas as frutas têm **o mesmo efeito** no corpo e diferem só na preferência inata. Nela,
   qualquer diferença de escolha entre donos não pode vir da nutrição.
3. **Critério.** Um efeito das frutas conta como **ensino** só se: (a) aparecer acima do "só cuidado" acoplado com as mesmas ofertas, com IC por
   bootstrap sobre sementes; **e** (b) não vier acompanhado de diferença de saúde e de mortes entre os braços (o G5 de `docs/DEFINICOES_V2.md`).
   Se só (a) valer, é ensino misturado com cuidado e se reporta assim. A análise por norma de reação (intercepto e inclinação por ambiente;
   Dingemanse et al. 2010, `10.1016/j.tree.2009.07.013`, VERIFICADA) é a mesma da seção 3 de `DEFINICOES_V2.md`.

**O efeito ruim fora da cadeia da morte (decisão F6).** O mundo descasado precisa de uma fruta com efeito ruim. Se o efeito ruim for na saúde
ou na fome, ele entra na cadeia de privação e morte, e todo resultado vira cuidado. A recomendação é o efeito ruim no **humor**, que não entra em
`Estado.em_privacao` (como a bola), e o efeito na saúde só como variante declarada.

**Efeito imediato antes do atrasado.** A transição que a política recebe é medida logo depois do efeito da ação do pet (validação V2 do roadmap):
o efeito imediato é limpo; o efeito atrasado (o pós-ingestivo da literatura) precisa de janela de crédito, que é decisão do plano do N3. Até lá,
o efeito das frutas é imediato.

**Registro.** Evento: as `acao_usuario` de oferta (são elas que o acoplado copia). Artefato da run: `braco`, `acoplado_de` (a vida de origem) e
`sinais_retirados` (a lista do que saiu), como o acoplado da L1. Derivado: o `efeito` de cada `consumo`, a saúde e as mortes por braço.

### 2.7 Creatures não é precedente

**Definição.** Nenhum documento, código, fala, comentário ou commit das frutas cita aquele jogo como precedente, referência de desenho ou
justificativa do vício. A comparação com ele não é usada nem para explicar a ideia.

**Justificativa.** Não há fonte primária do mecanismo de vício dele. As duas fontes primárias verificadas descrevem bioquímica artificial,
quimioemissores e receptores modulando a rede neural, **sem vício** (Grand e Cliff 1998, `10.1023/A:1010042522104`, **VERIFICADA só por título e
metadados**; Cliff e Grand 1999, `10.1162/106454699568683`, VERIFICADA). O livro do próprio autor (Grand 2001, *Creation: Life and How to Make
It*) está **VERIFICADA (sem DOI)** quanto à existência, mas o conteúdo não foi lido. O mecanismo de vício atribuído ao jogo só tem fonte de fã:
**NÃO VERIFICADA EM FONTE PRIMÁRIA** (`v3_referencias_verificadas.csv`, trilha V5). O desenho do vício sai da literatura de sensibilização de
incentivo (seção 2.5), e só dela.

**Registro.** Nenhum campo. Regra de redação, conferida na revisão de cada PR das frutas. Observação: o pedido original do Matheus, citado em
`docs/DEFINICOES_V2.md`, seção 7, ainda compara o vício àquele jogo; a troca do texto é decisão F10.

---

## 3. Ressalva de ética (por analogia)

**O que existe.** A literatura verificada de ética de desenho em jogos trata de mecânicas dirigidas **ao jogador**: loot boxes associadas a jogo
problemático (Zendle e Cairns 2018, `10.1371/journal.pone.0206767`, VERIFICADA); loot boxes como psicologicamente análogas a jogo de azar
(Drummond e Sauer 2018, `10.1038/s41562-018-0360-1`); monetização predatória (King e Delfabbro 2018, `10.1111/add.14286`); padrões de desenho
exploratórios (Karlsen 2019, `10.7551/mitpress/11550.003.0019`; Veiga et al. 2025, `10.5220/0013365800003929`). Estas quatro últimas estão
**VERIFICADA só por título e metadados**.

**O que não existe.** Não foi localizada literatura sobre representar dependência **num personagem cuidado pelo jogador**, nem sobre o risco de o
jogador explorar o vício do personagem como recurso (`v3_referencias_verificadas.csv`, V6: resultado negativo de busca, com cobertura limitada,
sem OpenAlex). Diz-se "não localizamos", nunca "ninguém estudou".

**Rótulo obrigatório.** Todo apoio ético do vício nas frutas é **por analogia**, e o texto tem de dizer isso. A analogia é imperfeita de um jeito
que convém declarar: um pet viciado não cobra do jogador. **Ausência de crítica não é aval.**

**O que a analogia sugere para o desenho (recomendação, decisão F8).** No produto, nenhuma mecânica recompensa o jogador por manter o pet
dependente (nenhum item, stat, medalha ou atalho ligado a dar a fruta que vicia), e o custo do vício para o pet é visível na tela. Na pesquisa
(Python), o vício é uma condição experimental com braço de controle, sem jogador.

---

## 4. A restrição de engenharia (validação V5 do roadmap)

- `events.AcaoPet` **não ganha membros**: o bandit da v1 usa `tuple(AcaoPet)` (e os traços, as sondas da divergência e o desejo iteram o enum).
  As frutas são sub-decisão de `comer` (seção 1.2), aprovada como M5 do roadmap.
- Os eventos do dono crescem só **no fim** de `AcaoUsuario` (seção 1.1), e só a camada de ambiente aceita os novos; nos motores anteriores eles
  levantam erro (o padrão de `ACOES_EDUCACAO` e da bola).
- Nenhum campo do log carrega a fruta escolhida pelo pet: a escolha é derivada, como toda ação do pet. No modo livre gravado, ela entra como
  `decisao_externa` (seção 1.1).
- `Observacao` e `engine.py` não mudam. A presença de frutas entra como entrada da percepção do aprendiz da V2, como a bola (validação V6).
- Sem frutas no log, a vida é byte a byte a de hoje (o teste de equivalência da bola, estendido).

---

## 5. Decisões que só o Matheus pode tomar

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| F1 | Gostar e querer como **dois registros por fruta** (`avaliacao`, `incentivo`), e o vício como dinâmica entre eles, não um terceiro registro | Sim | Com um escalar só, o vício não tem como aparecer (não há o que desacoplar) e a taxa de escolha passa a valer como gosto, que ela não mede |
| F2 | Vocabulário: identificadores, fatores do motivo e fala só com nomes de comportamento ou medida; tirar "gosto" dos textos de fala das frutas | Sim, as duas partes | O jogador lê sensação onde o motor só tem um número, e o projeto passa a afirmar o que a literatura não autoriza |
| F3 | As frutas entram por **oferta** do dono (um botão por fruta, no fim de `AcaoUsuario`), o pet escolhe ao `comer`, e `alimentar` continua a ração de cuidado; parte das ofertas com pelo menos duas frutas ao mesmo tempo | Sim | Se o dono der a fruta direto na boca, não há escolha do pet e o querer não é medido; com uma fruta por vez, "comer" e "querer aquela fruta" se confundem |
| F4 | Onde mora a neofobia: gene próprio do genoma, com rng própria, **ou** o eixo `curiosidade` do temperamento | Gene próprio | No eixo `curiosidade`, neofobia alimentar e exploração ficam idênticas por construção e a análise não separa as duas; como 5º eixo do `Temperamento`, mexe no objeto que a v1, a herança e a web usam |
| F5 | Preferência inata por fruta no genoma, como ponto de partida da avaliação | Sim | Sem predisposição herdada não existe o mundo descasado, e a pergunta maior perde a condição que a justifica |
| F6 | O efeito ruim de uma fruta no **humor** (fora de `em_privacao`), com efeito na saúde só como variante; efeito imediato antes do atrasado | Sim | Na saúde ou na fome, todo efeito entra na cadeia privação → morte e o resultado vira cuidado, como na v1 |
| F7 | Controle de canal: "só cuidado" acoplado **com as mesmas ofertas de fruta**, mais a variante de efeito igual entre frutas; ensino só acima do acoplado e sem diferença de saúde e mortes | Sim | Sem copiar as ofertas, o acoplado tem outra exposição às frutas e o contraste mede exposição, não ensino |
| F8 | Vício no produto (web): não antes de o N9 passar na pesquisa; se for, sem recompensa ao jogador por manter o pet dependente e com o custo visível | Não por ora | Um jogo que recompense explorar a dependência de um personagem cuidado não tem literatura que o cubra, e o apoio ético seria só por analogia |
| F9 | Vício: mecânica nova no nó N9, depois do N3 e das frutas sem vício; a derivação do RL homeostático como braço do plano do N9, não como atalho | Sim | Antes do N3 não existe aprendizado sobre os drives de onde derivar; escrito à mão agora, o vício seria uma regra nossa testando a si mesma |
| F10 | Trocar, na seção 7 de `docs/DEFINICOES_V2.md`, a frase do pedido original que compara o vício àquele jogo por "vício, a partir da literatura de sensibilização de incentivo" (trabalho do coordenador) | Sim | Alguém copia a comparação como precedente, que é a afirmação sem fonte primária que a revisão já bloqueou |
| F11 | Pedir a leitura do livro *Creation* (Grand 2001) para fechar a pendência de fonte primária | Não agora | Baixo: nenhuma definição aqui depende dele; ler só se um texto público for falar daquele jogo |

---

## 6. Fora deste documento

A implementação das frutas (N4, rodada 4), qualquer número (quantas frutas, prazos, ganhos, efeitos), equações, o vício implementado (N9), o
porte para a web e as versões de pet, e reabrir a v1 ou a pergunta do dono.
