# Dwarf Fortress como referência para o Digilab — contexto para a V2

Status: **CONTEXTO / POSSIBILIDADE FUTURA** (2026-10-01). Decisão do Matheus: as mecânicas de Dwarf Fortress que ainda
não entraram **ficam para a V2**; a v1 não recebe nada disto. Este documento junta o contexto para o planejamento da V2
(`docs/PLANO_V2_PESQUISA.md`). Ele **não autoriza implementação**, não é um desenho e não muda nenhum experimento. O
desenho, se vier, é o `docs/futuro/proposta_df.md` da tarefa descrita na seção 7, e só depois do gatilho dela.

## 1. Status das afirmações sobre o Dwarf Fortress

Tudo o que este documento diz sobre o Dwarf Fortress (Bay 12 Games; versões 0.42 em diante e a edição Steam) vem do
conhecimento do jogo, dos arquivos de dados dele e de verbetes de fã (a wiki do jogo). Pelo vocabulário da skill
`literatura-digilab`, é **NÃO VERIFICADA EM FONTE PRIMÁRIA**: serve de **pista de desenho, nunca de evidência**. Nada
aqui pode ser citado como precedência, como resultado, nem para alegar que algo do Digilab é novo (regras duras 1–4 da
skill). Onde a descrição do jogo diverge entre fontes de fã, o texto diz "aproximadamente".

Nenhum número desta seção e da seguinte é do Digilab; os do Digilab, na seção 3, apontam o artefato que os produz.

## 2. O que o Dwarf Fortress faz (resumo do que interessa)

Cada anão é um agente com personalidade fixa de nascença, necessidades, emoções por evento, memórias que se relembram e
um estresse acumulado que decide se ele continua funcional. O que importa para o Digilab é o **desenho do indivíduo**,
não o mundo.

### 2.1 Personalidade: facetas e valores

- **Facetas** (aproximadamente 50: ansiedade, raiva, alegria, teimosia, curiosidade, assertividade, etc.): cada uma vale
  0–100, sorteada na criação em torno da média da espécie/cultura. **Só os extremos geram texto**: a faixa central não é
  descrita. (A v1 já usa essa regra: adendo DF, Parte 2.2, limiar 0,2.)
- **Valores** (aproximadamente 32: família, lealdade, tradição, perseverança, competição, lazer, natureza, etc.): cada um
  em −50…+50, com o padrão vindo da cultura e variação individual.
- As facetas e os valores **filtram a emoção** de cada evento e **geram as necessidades** do indivíduo (quem valoriza
  família precisa de família; quem tem faceta de combate alta precisa lutar).
- Facetas e valores são quase fixos; mudam só por **memória nuclear** (2.4).

### 2.2 Necessidades e foco

- O anão tem um conjunto pequeno de necessidades derivadas da personalidade (rezar, ficar com amigos, adquirir algo,
  lutar, beber, criar, aprender…), cada uma com um nível que decai com o tempo sem satisfação.
- O agregado das necessidades é o **foco**: necessidades atendidas deixam o anão "focado" (trabalha melhor);
  necessidades ignoradas o deixam "distraído". É um canal lento, separado do humor.

### 2.3 Emoções por evento

- Cada evento (viu um amigo morrer, comeu bem, dormiu no chão, fez uma obra-prima, ouviu discurso) gera uma **emoção**
  escolhida de um catálogo grande (mais de cem: raiva, alegria, luto, orgulho, vergonha, euforia…). **Qual** emoção sai
  depende da circunstância e das facetas/valores: o mesmo evento irrita um, entristece outro, não afeta um terceiro.
- Cada emoção carrega um valor de **estresse** (positivo ou negativo), ponderado pela facetas.
- A emoção é texto ("se sentiu furioso depois de…") e entra na memória; não mexe nos atributos.

### 2.4 Memórias: curto e longo prazo, relembrar, memória nuclear

- O evento vira uma **memória** com a emoção e a força dela. Há **aproximadamente 8 espaços de curto prazo e 8 de longo
  prazo** (os "slots 8+8"); a memória mais forte vence a disputa, as fracas são esquecidas.
- As memórias são **relembradas** de tempos em tempos (no DF, por sorteio), e relembrar **reaplica a emoção e o
  estresse**: um trauma antigo volta a doer; uma alegria antiga volta a animar.
- Uma memória muito forte pode virar **memória nuclear** (core memory): ela **altera permanentemente facetas e valores**
  do anão (depois de um luto, fica mais ansioso ou mais estoico; depois de ser roubado, valoriza menos a confiança). É o
  único canal pelo qual a vida muda a personalidade.

### 2.5 Estresse em duas escalas

- **Curto prazo:** a soma das emoções recentes, que decai depressa; oscila com o dia.
- **Longo prazo:** uma média lenta do curto prazo, que só anda quando o curto prazo fica fora da faixa por muito tempo.
  Passa por **limiares** que mudam o comportamento (de "contente" até "estressado", "sofrendo" e os colapsos: acesso de
  raiva, catatonia, violência). A recuperação é lenta e **assimétrica**: cair é mais fácil que subir.
- É o mecanismo do "espiral": memórias ruins relembradas sustentam o estresse, que gera eventos ruins, que geram
  memórias ruins.

### 2.6 Duas prioridades

- O anão divide o tempo entre **o trabalho** (as tarefas que o jogador libera) e **as necessidades próprias** (2.2).
  Normalmente o trabalho vem primeiro; quando uma necessidade fica forte, ela **toma a prioridade** e o anão larga a
  tarefa para atendê-la (faz uma pausa, vai rezar, procura um amigo). O jogador não dá ordem direta ao indivíduo: só
  muda o ambiente e as tarefas disponíveis, e o anão decide.
- **A ler com o Matheus:** "duas prioridades" foi o nome que ele deu a esta peça na tarefa de referência (seção 7);
  confirmar se é esta a leitura antes de qualquer desenho.

### 2.7 O que o DF tem e **não interessa** ao Digilab

Geração de mundo e história procedural, lendas, economia de tarefas, relações entre dezenas de agentes, facções e
guerras. Pelo `CLAUDE.md` (não aumentar escopo) e pela tarefa da seção 7 (lista do que fica fora), nada disso entra.

## 3. O que a v1 já tirou do Dwarf Fortress

O adendo `docs/ADENDO_MEMORIA_EMOCAO_DF.md` (2026-09-25) já levou para a v1, de forma determinística (sem o sorteio do
DF), as peças abaixo. Números de `artifacts_v1_memoria_espacos/metrics.json`, `espacos.json` e
`artifacts_v1_habituacao/{com,sem}/metrics.json` (seções do `CLAUDE.md` "Memória por espaços" e "Emoção, extremos e
habituação").

| peça do DF | o que a v1 tem | resultado medido |
|---|---|---|
| espaços de memória (8+8) | **4 de curto prazo + 2 de longo**, uma por categoria, a mais forte vence; promoção ao fim de 12 h; relembrar a cada 4 h acordado em cronograma fixo (`digilab/memoria_espacos.py`) | a memória muda o comportamento, mas pouco: **6,9%** dos motivos citam uma memória (6,3% atencioso a 7,8% aleatório); JSD entre braços 0,0228 bit com espaços × 0,0204 sem (diferença da ordem de 0,001, sem IC) |
| emoção filtrada pela personalidade | tabela `categoria × temperamento → emoção` (`digilab/emocao.py`), valência multiplica a intensidade da memória; só leitura | aleatório e relapso dominados por `demora` (raiva 52% e 42%); atencioso e incoerente orgulho/euforia; a emoção não muda nenhum artefato (equivalência testada) |
| só os extremos são descritos | limiar `|eixo| ≥ 0,2` em `ConfigExpressao` | com o sorteio uniforme em [−1, 1], os 10 ovos têm pelo menos um eixo descrito (1,0): o limiar quase nunca cala |
| habituação a eventos repetidos | `intensidade × 0,8^repetições` nas últimas 12 h, teimosia acelera; reduz também a recompensa do bandit (chave `habituacao_ligada`) | não muda o resultado central (0,615 com e sem), mas **encolhe a separação entre donos**: JSD entre braços 0,0212 com × 0,0262 sem |

**O que o adendo deixou fora, de propósito:** memórias mudando o temperamento ao longo da vida (a memória nuclear) e
preferências individuais (comida e brincadeira favoritas). São exatamente as peças que ficam para a V2.

## 4. Encaixe no Digilab: as peças para a V2

As cinco peças abaixo são as da tarefa de referência (seção 7, item a). Para cada uma: o que é, o que já existe, onde
entraria na V2 e o risco. Tudo ABERTO; nada decidido.

A V2 (`docs/PLANO_V2_PESQUISA.md`, fase 1b) propõe um **aprendiz com lobos nomeados**: percepção, **memória e emoção**,
**impulsos**, decisão; aprendizado só no lobo de decisão, prior do instinto como pesos iniciais, traços como média lenta
por fora. As peças do DF cabem nos lobos de memória e emoção (espaços, memória nuclear, estresse) e de impulsos
(necessidades, as duas prioridades). A personalidade (faceta × valor) é o que alimenta os dois.

| peça | o que é no DF | o que a v1 já tem | onde entraria na V2 | risco principal |
|---|---|---|---|---|
| **slots 8+8** | 8 memórias de curto e 8 de longo prazo, a mais forte vence, relembrar reaplica | 4+2 por categoria (seção 3); relembrar em cronograma | lobo de memória e emoção; a pergunta é se **mais espaços e categorias novas** (do ambiente mínimo da fase 1a: comida posta, objeto, área) fazem a memória ser citada em mais que 6,9% dos motivos | memória que não muda decisão é custo sem efeito (o número da v1 diz isso); regra de desempate de slot tem de ser explícita (empate → a mais recente, como hoje) |
| **memória nuclear** | memória forte altera facetas e valores para sempre | nada: o adendo deixou fora; o temperamento é fixo do ovo (`temperamento.py`) e o caráter é média lenta | lobo de memória e emoção → escreve nos **traços** (a média lenta), não no temperamento; ou um terceiro nível, "cicatrizes", com teto de quantas por vida | **reabre o confundidor cuidado × ensino**: quem deixa o pet sofrer (morte evitada, lesão, demora) marca a personalidade mais que quem ensina. Na v1 o dono já pesa pelo cuidado (`docs/LEITURA_CONSOLIDADA_DONO.md`); a peça pode amplificar isso. Exige braço de controle "só cuidado" (o H0 permanente da V2) |
| **faceta × valor** | ~50 facetas 0–100 e ~32 valores −50…+50, que filtram a emoção e geram necessidades | 4 eixos de temperamento (rng do ovo) + 4 de caráter; a tabela de emoção lê o temperamento | o genoma da V2 (fase 3, criação × seleção): **poucas** facetas (não 50), sorteadas **correlacionadas** e não independentes | a literatura verificada restringe: traços vêm em **síndromes correlacionadas** (Sih, Bell e Johnson 2004, `10.1016/j.tree.2004.04.009`; skill `literatura-digilab`, "restrições de desenho"); e ~52% da variação de personalidade animal é genética aditiva (Dochtermann, Schwab e Sih 2015, `10.1098/rspb.2014.2201`) — serve de calibração do quanto o ovo deve pesar. A v1 mediu σ²_genoma 4,9% com o genoma atual |
| **duas prioridades** | trabalho × necessidade própria; a necessidade forte toma a frente; o jogador muda o ambiente, não dá ordem | obediência com recusa e motivo (`obediencia.py`), desejo (`desejo.py`: `preciso` × `queria`); a recusa B2 **não existe** (o dono age direto no estado) | lobo de impulsos: a necessidade (fome, descanso, vontade) × o pedido do dono (comando pelo catálogo, já na web) decidem **quem fala mais alto**, e o pet pode largar o que o dono pediu | é a peça que mais cria "decisão em que o dono importa" (o que a V2 procura), e a que mais mexe no motor (`engine.py` intocado: tem de ser uma camada por cima, como o `MotorPersonalidade`) |
| **estresse em duas escalas** | curto prazo rápido, longo prazo lento com limiares e colapsos; recuperação assimétrica | humor (estado), saúde, lesão e morte (educação-v1); vínculo; habituação | lobo de memória e emoção: o curto prazo já é o humor; o **longo prazo** seria novo, com limiares que mudam a política (ex.: o pet estressado explora menos) e com teto para não haver espiral sem saída | a v1 mostrou que o efeito do dono vem das **mortes**; um estresse de longo prazo é outro canal de "cuidado", não de ensino. O gate G5 da V2 (a divergência se mantém sem mortes e sem lesão) tem de valer também sem estresse |

## 5. Restrições que qualquer encaixe tem de respeitar

Do `CLAUDE.md` e do plano da V2:

- **Determinismo bit a bit** com replay do log; o DF sorteia quando relembra, o Digilab usa cronograma (como o adendo).
- **RNG de ambiente separada da de política**; qualquer sorteio novo (faceta, memória nuclear) tem a própria rng.
- **Event sourcing:** nada salvo além do log; os espaços, o estresse e as cicatrizes são função pura dos eventos.
- **`engine.py` intocado;** peças novas entram como camada (`MotorComFeedback` → `MotorPersonalidade` → …).
- **Uma versão de pet por mecânica** no jogo web; paridade Python/web com gabarito.
- **Literatura:** nunca alegar que separar instinto de aprendido, herdar o prior ou "ensinado, não roteirizado" é novo
  (regras 1–3); DF, Monster Rancher, Championship e Pokémon não são evidência (regra 4). Os únicos números da
  literatura usados aqui são os três de calibração da skill (Dochtermann 2015, Morrill 2022, Dingemanse 2010) e a
  restrição das síndromes (Sih 2004), todos VERIFICADA.
- **Nenhum número sem artefato em disco que o produza.** Os do DF não existem aqui; os do Digilab apontam o artefato.

## 6. Perguntas abertas para o planejamento da V2

1. **Memória nuclear:** escreve nos traços (média lenta), no temperamento (fixo hoje) ou num nível próprio com teto? E
   como separar a marca do cuidado da marca do ensino (o braço "só cuidado" basta?).
2. **Faceta × valor:** quantos eixos a V2 quer (4 + 4 de hoje, ou mais) e com que correlação entre eles? A fase 3
   (criação × seleção) precisa decidir isso antes, porque é o genoma herdado.
3. **Duas prioridades:** é a leitura certa da peça (2.6)? Ela entra na fase 1a (ambiente mínimo: o pet larga o que o dono
   pediu para atender a necessidade) ou só na 1b (política com lobos)?
4. **Estresse de longo prazo:** vale a pena um canal lento a mais, dado que o humor, a saúde e as mortes já carregam o
   efeito do cuidado? Qual limiar de colapso é aceitável num pet (o DF deixa o anão enlouquecer; o pet, no máximo, a
   forma sombria)?
5. **Slots:** mais espaços só valem com categorias novas do ambiente; quais, vindas do inventário da fase 0?

## 7. A tarefa de referência (quando e como vira desenho)

A tarefa recebida em 2026-09-30 ("avaliar e, se o gatilho passar, desenhar a incorporação das mecânicas de Dwarf
Fortress") pede, antes de qualquer desenho, a leitura do `CLAUDE.md`, deste documento, da skill `literatura-digilab`,
do `digilab/protocol.py` e de `artifacts/metrics.json`, e um **gatilho** verificado no repositório (código, testes,
artefatos), não em texto:

- [ ] combate V2 implementado, testes passando, bateria de bots rodada;
- [ ] memória/expressão implementada, testes de replay passando;
- [ ] personalidade/obediência implementada, testes de replay passando;
- [ ] ablação instinto × bandit sob os mesmos donos rodada, com artefato em disco;
- [ ] campos PROPOSTOS de `protocol.py` referendados pelo Matheus;
- [ ] `python -m pytest tests/ -q` sem falhas.

Se passar, a entrega é **só** `docs/futuro/proposta_df.md` (sem código): o desenho adaptado de cada peça da seção 4, o
módulo e os parâmetros novos em `config.py` (PROPOSTO), como preserva determinismo, rng separada, event sourcing e
`engine.py`, a regra de desempate de slot, a análise do confundidor (com a ablação já rodada), a análise de variância
(JSD dentro e entre braços; temperamento fixo entre braços por números aleatórios comuns), os testes novos, a lista do
que fica fora e uma recomendação em 3 frases; e termina perguntando ao Matheus quais peças ele aprova.

**Decisão de 2026-10-01:** essa tarefa **não roda na v1**. Ela entra no planejamento da V2, depois da fase 0 (inventário
do jogo) e junto com a fase 1b (o aprendiz com lobos), porque as peças da seção 4 são partes desse aprendiz.

## 8. Relacionados

- `docs/PLANO_V2_PESQUISA.md` — o plano da V2 (fases, gates, o aprendiz com lobos).
- `docs/ADENDO_MEMORIA_EMOCAO_DF.md` — o que já entrou (Partes 1 e 2) e o que ficou fora.
- `docs/TODO_INTERACAO_CORPO.md` — o ambiente mínimo (fase 1a), de onde viriam categorias novas de memória.
- `docs/LEITURA_CONSOLIDADA_DONO.md` — por que o cuidado pesa e o ensino não: o confundidor que a memória nuclear e o
  estresse podem amplificar.
- `docs/referencias/REGRAS_CITACAO_DIGILAB.md` (skill `literatura-digilab`) — rótulos de status e regras duras.
