# Revisão curta: olfato e audição em outros trabalhos, e onde o desenho dos dois pets se encaixa

Pedido do Gerente ao worker C (2026-10-08), só papel. A pergunta é como cada sistema modela o sinal de cheiro e de som, o que o agente
recebe, e onde ficam as decisões DP-4, DP-11 e DP-12 de `docs/futuro/dois_pets.md` (seção 5).

**Regras:**
- só as referências da tabela, com o status de `docs/referencias/REGRAS_CITACAO_DIGILAB.md`;
- o Creatures Wiki e o openc2e são **pista**, nunca evidência;
- **SEM FONTE** onde não houver fonte;
- nenhuma alegação de novidade: um pet que cheira e ouve o outro já existe em jogos e em vida artificial (seções 2 a 6).

## 1. Método e limites

- **Busca em 2026-10-08:** web; Crossref e OpenAlex para metadados e resumos; o código do openc2e no GitHub (commit `6a4396c`).
- **Nenhum DOI de memória.** Todo DOI da tabela foi resolvido no Crossref nesta sessão, sem `update-to`.
- **"Quanto foi lido" limita o que se cita.** Um item com "só título" não sustenta afirmação de conteúdo.
- **O que ficou de fora, sem fonte localizada:**
  - o texto do Gamasutra de Tom Leonard sobre o sistema sensorial do Thief (2003). Ele aparece em listas de leitura, mas o texto não foi
    obtido. Do Thief, cita-se só o postmortem;
  - o manual do SimAnt;
  - o capítulo do PolyWorld fora das páginas 1 a 10;
  - qualquer medida de desempenho dos sistemas. A revisão é sobre o **modelo do sinal**, não sobre resultados.

## 2. Três modelos de sinal

Os trabalhos caem em três famílias pelo que o mundo guarda entre a emissão e a recepção:

| família | o que o mundo guarda | como chega ao agente | exemplos (seção 3) |
|---|---|---|---|
| **A. campo difundido** | um valor por lugar (célula, sala), atualizado a cada passo por emissão, perda e difusão para os vizinhos | o agente lê o valor onde está (e às vezes em volta) | Creatures (pista), o modelo Ants do NetLogo, o sistema de formigas |
| **B. evento com raio** | nada: o som ou o cheiro é um evento, com origem, intensidade e alcance | quem está dentro do raio recebe o evento (origem, intensidade, idade) | Unreal AI Perception; o "cheiro" do Framsticks |
| **C. propagação pela topologia** | um grafo de salas e passagens (portas, janelas) | a distância do evento é medida pelo caminho entre as salas, não em linha reta | Thief (a "room database"); Splinter Cell Blacklist |

**Uma quarta via fica de fora do mundo:**
- **a visão desenhada:** o agente recebe uma imagem do ponto de vista dele (PolyWorld);
- **o sensor físico:** o robô mede o químico ou o som com dois ou mais sensores e o gradiente sai da diferença entre eles (Beer e
  Gallagher; Webb; Ishida et al.).

Nessas duas, o mundo não calcula a direção: quem a tira é o agente.

## 3. Sistema a sistema

### 3.1 Creatures (cheiro por difusão entre salas) — pista

- **A fonte primária não descreve o cheiro.** Os resumos de Grand, Cliff e Malhotra (1997) e de Cliff e Grand (1999) falam da rede neural
  e da bioquímica. Nenhum dos dois menciona os campos de cheiro (os "CA"): é a mesma lacuna da revisão G (`G_REVISAO_CORPO_QUIMICO.md`).
- **Pelo Creatures Wiki** (pista):
  - **o mundo:** os CA são campos invisíveis, um valor por sala, emitidos por objetos;
  - **as regras:** cada tipo de sala tem ganho, perda e difusão por canal (o comando `RATE`), e a porta entre duas salas tem uma
    permeabilidade (`DOOR`);
  - **o agente:** a criatura sente o CA pelo pé e o leva ao lobo do olfato.
- **Pelo openc2e** (pista: uma reimplementação, não o motor original):
  - **o código:** `Room.cpp`, linhas 81 a 136 no commit `6a4396c`. Por canal e por sala, há uma perda proporcional ao valor e um ganho
    em direção ao que os objetos emitem;
  - **a difusão:** a sala recebe o maior entre o próprio valor e o do vizinho × difusão × permeabilidade da porta. É uma propagação pelo
    máximo, não uma soma;
  - **o lobo do olfato:** a entrada dele está como `TODO` (`CreatureAI.cpp`, linha 150). Como a criatura usa o campo fica **SEM
    FONTE**.
- **Família:** A, com a passagem pelas portas da C.

### 3.2 O modelo Ants do NetLogo e o sistema de formigas (campo difundido, rastro)

- **O NetLogo Ants** (Wilensky 1997, documentação do modelo, cinza, lida em 2026-10-08):
  - **o sinal:** a formiga que acha comida volta ao ninho deixando um químico;
  - **o mundo:** o químico **difunde e evapora** por célula, com as duas taxas como parâmetro;
  - **o agente:** a formiga "fareja" em três direções e vira para a mais forte. A direção sai do agente, por amostra;
  - **o mesmo mecanismo** dá o "cheiro do ninho" para voltar.
- **O sistema de formigas** (Dorigo, Maniezzo e Colorni 1996, resumo): um paradigma de otimização inspirado em colônias de formigas, com
  realimentação positiva e comunicação distribuída. O feromônio fica numa estrutura global de dados, não no espaço.
- **A estigmergia** (Theraulaz e Bonabeau 1999, resumo): o nome da classe de mecanismos em que os animais interagem pelo que deixam no
  ambiente, desde Grassé.
- **O SimAnt** (Maxis, 1991): a formiga do jogador deixa um rastro de cheiro que a colônia segue. Só fontes enciclopédicas, então é **NÃO
  VERIFICADA EM FONTE PRIMÁRIA**. Se o rastro evapora, fica SEM FONTE.
- **Família:** A. O rastro é uma marca no mundo que outro agente lê depois.

### 3.3 Unreal AI Perception (evento com raio)

Documentação oficial da Epic (cinza, lida em 2026-10-08).
- **A audição:** reage a eventos de ruído que o código do jogo dispara. O sentido tem um alcance de audição, e cada evento pode ser
  filtrado por afiliação (inimigo, neutro, amigo).
- **O que não está na página:** a queda com a distância e se o som contorna paredes. Ali só há um teste por raio.
- **A visão:** raio, raio de perda e meio ângulo periférico.
- **O tato:** o encontrão.
- **O que o agente recebe:** um estímulo com idade, prazo de validade, intensidade, o lugar de origem, o lugar onde foi registrado, uma
  etiqueta e se foi percebido.
- **Família:** B. O agente recebe a **origem** do evento, e não só a direção.

### 3.4 Thief e Splinter Cell Blacklist (propagação pela topologia)

- **Thief** (Leonard, postmortem, Game Developer, 1999, republicado em 2013):
  - **o mundo:** o nível tinha uma base de dados de salas que permitia a propagação do som pelos espaços em tempo real;
  - **o agente:** os guardas "raramente trapaceiam" e decidem pelo mundo como o percebem.
  - **O que fica SEM FONTE:** como o som atravessa portas, que o postmortem não detalha.
- **Splinter Cell Blacklist** (Walsh 2015, Game AI Pro 2, cap. 28, texto lido):
  - **por que não a linha reta:** a distância euclidiana deixaria o jogador ser ouvido através das paredes. O motor de som saiu por ser
    caro e frágil;
  - **a distância do som:** é medida pelo caminho de áreas ligadas por pontos de passagem (o grafo de conectividade do jogo). Na mesma
    área, usa-se a linha reta; entre áreas, a soma dos trechos de passagem em passagem;
  - **a visão:** raios para oito partes do corpo do jogador, com um número mínimo de partes visíveis por postura.
- **Família:** C.

### 3.5 Framsticks e PolyWorld (vida artificial)

- **Framsticks** (Komosiński e Ulatowski 1999; Komosiński 2003, resumo; site oficial, cinza):
  - **os sentidos:** as criaturas têm receptores de toque, equilíbrio e **cheiro**;
  - **o que o cheiro sente:** fontes de energia. Um outro organismo por perto "cheira como energia" e vira o alvo de interesse.
  - **Família:** B. O cheiro não distingue quem emite.
  - **O que fica SEM FONTE:** a fórmula da queda com a distância.
- **PolyWorld** (Yaeger 1994, texto lido, pp. 1 a 10):
  - **as entradas:** a visão, o nível de energia e um valor aleatório;
  - **a visão:** a cena desenhada do ponto de vista do organismo, numa faixa de uma linha de pixels em vermelho, verde e azul, com o
    campo horizontal sob controle de um neurônio;
  - **os outros sentidos:** não há cheiro nem audição;
  - **o sinal emitido:** um dos sete comportamentos é **acender** (controlar o brilho de partes do próprio corpo). É um emissor que o
    organismo controla e que os outros só veem.
- **Família:** a quarta via (a visão desenhada).

### 3.6 Robótica e o veículo de Braitenberg (sensor físico)

- **Braitenberg** (1984, livro, existência confirmada por resenha; o texto não foi lido). Pela descrição de Yaeger (1994, p. 2), os
  veículos ligam sensores simples a motores simples.
- **Beer e Gallagher** (1992, resumo): controladores neurais evoluídos, entre eles um de **quimiotaxia** que troca de estratégia conforme o
  ambiente.
- **Webb** (1995): um robô como modelo de animal, num teste com o grilo. Só o título foi conferido: o texto não foi obtido, então o
  mecanismo fica SEM FONTE aqui.
- **Ishida, Wada e Matsukura** (2012, resumo): o histórico do olfato em robôs móveis, que seguem trilhas químicas no chão, rastreiam
  plumas até a fonte e mapeiam a distribuição de substâncias.
- **Família:** a quarta via. Num corpo físico, o gradiente não vem pronto: é medido.

## 4. O que o agente recebe, lado a lado

| sistema | sentido | o que chega ao agente | quem calcula a direção | identidade de quem emitiu |
|---|---|---|---|---|
| Creatures (pista) | cheiro | o valor do CA na sala | SEM FONTE | não: canal por tipo de coisa |
| NetLogo Ants | cheiro | o valor em três pontos à frente | o agente, por amostra | não |
| Unreal | ouvir | o estímulo com a origem, a intensidade e a idade | o mundo (dá a origem) | sim: o ator que emitiu |
| Splinter Cell | ouvir | o evento, com a distância pelo caminho | o mundo | SEM FONTE |
| Framsticks | cheiro | a intensidade do cheiro de energia | SEM FONTE | não: o outro cheira como energia |
| PolyWorld | ver | uma faixa de pixels | o agente | só pela cor (o gene da cor verde) |
| robôs | cheiro, som | a leitura de cada sensor | o agente, pela diferença | não |
| **digilab, a comida** | cheiro | a intensidade e a direção em 8, somadas em inteiros, `A × (R − d) // R` por fonte | o mundo (`direcao_do_cheiro`) | não: um canal só |
| **digilab, DP-4 (1b)** | cheiro | por pet conhecido, a intensidade e a direção do cheiro e do rastro | o mundo | sim: um canal por pet |
| **digilab, DP-4 (1b)** | ouvir | `(id, som, direção em 8, distância)` dos sons desde a decisão anterior | o mundo | sim |

## 5. Onde o desenho do digilab se encaixa

- **O cheiro do digilab é um campo calculado, não difundido.**
  - **Como é feito:** o mundo não guarda um valor por célula. A intensidade num ponto é a soma das fontes que ainda existem, com a queda
    linear até o raio. É a família A sem a difusão e sem a perda por passo: o valor num ponto é uma função das fontes de agora.
  - **O ganho:** é exato em inteiros e barato, e não depende da ordem de atualização das células. Isso importa para o replay bit a bit e
    para a paridade com o TypeScript.
  - **A perda:** não há atraso nem acúmulo. O cheiro aparece e some com a fonte. O NetLogo e o Creatures (pista) têm as duas coisas.
- **O rastro do DP-4 é a estigmergia mais simples.** Cada marca decai linearmente com a idade e some em `T`, e há um limite de marcas por pet.
  - **O que tem do feromônio do NetLogo:** a evaporação, por idade.
  - **O que não tem:** a difusão e o reforço. Uma marca nova não soma à antiga no mesmo lugar: é outra fonte, somada na conta.
  - **Isso basta para** o degrau 1b ("por onde o outro andou"). Um rastro que se reforça pelo uso (a trilha das formigas) seria outro
    desenho.
- **O som do DP-4 é um evento com raio (família B).**
  - **O que é igual ao Unreal:** o evento sai de uma ação, tem origem e alcance, e o receptor o recebe com quem emitiu.
  - **O que é diferente:** o digilab dá a **direção em 8 e a distância**, e não a origem exata. É menos que o Unreal.
  - **Por que a linha reta serve:** o mapa do mundo físico não tem parede nem porta entre as regiões (M-1). O problema que levou o Splinter
    Cell e o Thief à família C não existe aqui.
- **A direção vem pronta do mundo.** No NetLogo e nos robôs, a direção sai do agente, por amostra ou pela diferença entre sensores. No
  digilab ela é calculada pelo mundo (`direcao_do_cheiro`) e entregue pronta.
  - Isso não lê o estado do outro (a regra do G-RECEPTOR-SOCIAL vale), mas é um **pré-processamento** que o corpo do pet não faz.
  - Se a pergunta um dia for "o pet aprende a seguir um gradiente", a direção teria de sair do pet (OA-2, seção 6).
- **A identidade no cheiro é uma escolha do digilab.**
  - **O que o DP-4 faz:** um canal por pet, então o pet sabe de quem é o cheiro.
  - **Os outros:** no Framsticks o outro "cheira como energia", e no Creatures (pista) o canal é por tipo de coisa. No Unreal e no Splinter
    Cell, o evento traz quem o emitiu.
  - **O custo:** o B sabe de quem é o rastro sem ter aprendido. Para a pergunta do degrau 1 ("o B aprende o que o A viveu") isso não muda
    nada, mas é declarado.
- **O cheiro de estado (DP-12) tem análogo no emissor que o próprio corpo controla:**
  - no PolyWorld, o organismo acende partes do corpo pela saída de um neurônio, e os outros só veem a luz;
  - no Creatures (pista), objetos emitem CA por comando.
  - **No digilab,** o emissor externo do degrau 3 lê um químico do próprio corpo com ganho declarado no grafo, e o outro lê só a
    intensidade no mundo. É a mesma separação: quem emite controla o sinal, e quem recebe só lê o mundo.
  - O laço entre dois corpos que a checagem do grafo passa a ver (seção 5.3 do desenho) não tem paralelo descrito nas fontes lidas: SEM
    FONTE.
- **A regra "nenhum sentido lê o estado do outro"** é a mesma que o Thief declara para os guardas ("raramente trapaceiam"). No digilab ela
  é um gate (G-RECEPTOR-SOCIAL), e não uma intenção.
- **A ordem do DP-11 (visão e toque no 1; audição e cheiro no 1b)** não tem paralelo nas fontes: nenhum dos sistemas lidos mede o
  acréscimo de um sentido sobre outro. SEM FONTE.

## 6. Decisões do Matheus

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| OA-1 | Campo calculado ou difundido para o cheiro do 1b | **manter o campo calculado** (a soma das fontes, em inteiros), como o da comida | difundido: o valor por célula e a ordem da atualização entram no replay e na paridade TS, com custo por tick. O ganho seria o atraso e o acúmulo, que nenhuma pergunta do 1b pede |
| OA-2 | Quem calcula a direção do cheiro e do som | **o mundo, como hoje**, declarado como pré-processamento | pelo pet (amostra em pontos, como no NetLogo): mais fiel ao corpo, mas muda o cheiro da comida também e pede outro G2. Fica para uma pergunta sobre seguir gradiente |
| OA-3 | Som em linha reta ou pelo caminho | **linha reta**, enquanto o mapa não tiver parede nem porta (M-1) | pelo caminho sem obstáculo: o mesmo resultado, com mais código. Se entrarem obstáculos, a distância pelo caminho (Splinter Cell) é o desenho registrado |

## 7. Órgãos e anatomia no estado da arte

Acrescentada no mesmo dia, a pedido do Gerente, para a DP-13 e a DP-14 (`docs/futuro/dois_pets.md`, seção 5.6). A pergunta é que órgãos e
sentidos cada sistema modela, e como.

| sistema | órgãos e sentidos modelados | como | fonte e status |
|---|---|---|---|
| **Creatures** | bioquímica, hormônios, desenvolvimento por estágios; visão; olfato pelos CA | os hormônios modulam a rede neural e o desenvolvimento (resumos). Os órgãos com força vital, dano e morte e o olfato pelo pé são detalhe de fã (revisão G, P1; seção 3.1 aqui). A audição de palavras fica SEM FONTE | itens 1 e 2 (VERIFICADA, resumo) para a bioquímica; itens 3 e 4 (pista) para o olfato |
| **Dwarf Fortress** | corpo em partes ligadas umas às outras, com tecidos; partes com função de **ver, ouvir, cheirar, respirar**, centro nervoso e do pensamento | cada parte declara a função por uma marca nos dados do jogo. Sem toda parte de ver, a criatura não vê; sem as de respirar, sufoca. A marca de cheirar **não tem função conhecida**, segundo o próprio wiki | item 20 (Dwarf Fortress Wiki, pista); item 21 (Adams 2019, resumo) é sobre narrativa emergente e **não** descreve o corpo |
| **Framsticks** | corpo 3D de bastões e juntas, músculos; receptores de **toque, equilíbrio e cheiro** | o cheiro detecta fontes de energia, e o outro organismo "cheira como energia" | itens 12 a 14 (VERIFICADA; o site oficial, cinza) |
| **Sims (1994)** | morfologia e sistema neural evoluídos juntos | um grafo dirigido descreve o corpo e o circuito neural (resumo). Os sensores não estão no resumo: SEM FONTE | item 22 (VERIFICADA, resumo) |
| **PolyWorld** | visão; energia interna; tamanho, força e velocidade como fisiologia nos genes; um emissor de luz no próprio corpo | a visão é desenhada do ponto de vista do organismo; não há cheiro nem audição | item 15 (VERIFICADA sem DOI, texto lido) |
| **Robôs de Cañamero e colegas** | variáveis fisiológicas internas sob homeostase; hormônios que regulam os **próprios receptores** | o prazer, ligado ou não a uma necessidade, melhora a viabilidade e a flexibilidade (Lewis e Cañamero 2016). Num modelo epigenético, a concentração do hormônio regula o receptor dele, num robô Koala, em seis ambientes (Lones, Lewis e Cañamero 2018) | itens 23 e 24 (VERIFICADA, resumo) |
| **Bongard, Zykov e Lipson (2006)** | automodelo da própria morfologia | o robô infere a própria estrutura pelas relações entre atuação e sensação | item 25 (VERIFICADA, resumo; revisão G) |
| **Unreal, Thief, Splinter Cell** | sentidos como componentes (ver, ouvir, tato), **sem anatomia** | o sentido é um teste do mundo (raio, ângulo, raios até partes do corpo do alvo) | itens 9 a 11 |

**A biologia que sustenta o desenho do órgão** (só os resumos):
- **A adaptação no próprio receptor:** nos neurônios olfativos de vertebrados há duas formas rápidas e uma persistente de adaptação, com
  cursos de tempo diferentes (Zufall e Leinders-Zufall 2000, item 26).
- **Uma narina basta, duas ajudam:** na larva da drosófila, um só neurônio olfativo funcional basta para a quimiotaxia, e a entrada dos dois
  lados aumenta a precisão pela relação sinal-ruído (Louis et al. 2008, item 27).
- **O olfato estéreo:** ratos localizam o cheiro em uma ou duas fungadas. A amostra dos dois lados foi essencial, com a diferença de
  intensidade e de tempo entre as narinas como pista de direção (Rajan, Clement e Bhalla 2006, item 28).
- **A localização do som é calculada:** o espaço do som não está representado na membrana basilar da cóclea, e a localização depende da
  comparação entre os dois ouvidos (Grothe, Pecka e McAlpine 2010, item 29).

**O que se tira para o digilab:**
- **Nenhum dos sistemas de jogo e de vida artificial lidos** modela o olfato com limiar, adaptação e saturação no receptor:
  - no Dwarf Fortress (pista) o nariz existe e não tem função conhecida;
  - no Framsticks o cheiro é um receptor de energia, sem fórmula localizada;
  - no Creatures (pista) o cheiro é o valor da sala.
- **O mais perto é o robô de Lones, Lewis e Cañamero,** com um receptor que se regula. Mas é um receptor de hormônio, não de cheiro.
- **A adaptação, o limiar e a saturação da DP-13** vêm da biologia (itens 26 a 28), e não de um sistema de agentes. A forma exata (a conta
  em inteiros, a meia-vida, a meia-saturação) é desenho nosso: SEM FONTE.
- **Nenhuma alegação de novidade.** É resultado de uma busca curta, em que a ausência é evidência fraca.

## 8. Referências

| # | referência | tipo | status | DOI / onde | quanto foi lido | o que sustenta aqui |
|---|---|---|---|---|---|---|
| 1 | Grand, Cliff e Malhotra (1997). Creatures: artificial life autonomous software agents for home entertainment. Agents '97 | par | VERIFICADA | `10.1145/267658.267663` | resumo (revisão G) | a arquitetura do Creatures; **não** os campos de cheiro |
| 2 | Cliff e Grand (1999). The Creatures Global Digital Ecosystem. Artificial Life 5(1) | par | VERIFICADA | `10.1162/106454699568683` | resumo (revisões anteriores) | idem |
| 3 | Creatures Wiki, verbete "Cellular Automata", e o wikibook de CAOS (comandos de mapa) | cinza (fã) | NÃO VERIFICADA EM FONTE PRIMÁRIA | creatures.fandom.com; de.wikibooks.org | trechos por busca | **pista:** CA por sala, ganho, perda, difusão, permeabilidade da porta |
| 4 | openc2e, `src/openc2e/Room.cpp` e `creatures/CreatureAI.cpp`, commit `6a4396c` | cinza (reimplementação) | NÃO VERIFICADA EM FONTE PRIMÁRIA | github.com/openc2e/openc2e | código lido | **pista:** a regra da perda, do ganho e da difusão pelo máximo; o olfato sem entrada (`TODO`) |
| 5 | Wilensky, U. (1997). NetLogo Ants model. CCL, Northwestern University | cinza (documentação do modelo) | VERIFICADA (sem DOI) | ccl.northwestern.edu/netlogo/models/Ants | página lida | o químico que difunde e evapora por célula; a formiga que fareja em três direções |
| 6 | Dorigo, Maniezzo e Colorni (1996). Ant system: optimization by a colony of cooperating agents. IEEE Trans. SMC-B 26(1) | par | VERIFICADA | `10.1109/3477.484436` | resumo | o paradigma inspirado em colônias, com realimentação positiva e comunicação distribuída |
| 7 | Theraulaz e Bonabeau (1999). A Brief History of Stigmergy. Artificial Life 5(2), 97-116 | par | VERIFICADA | `10.1162/106454699568700` | resumo | o conceito de estigmergia (interação pelo ambiente) |
| 8 | SimAnt (Maxis, 1991) | jogo | NÃO VERIFICADA EM FONTE PRIMÁRIA | verbetes enciclopédicos | — | **pista:** o rastro de cheiro que a colônia segue |
| 9 | Epic Games. AI Perception in Unreal Engine (documentação) | cinza (documentação oficial) | VERIFICADA (sem DOI) | dev.epicgames.com | página lida | a audição por eventos de ruído com alcance; os campos do estímulo |
| 10 | Leonard, T. (1999). Postmortem: Thief: The Dark Project. Game Developer; republicado em *Postmortems from Game Developer* (2013) | cinza (postmortem) | VERIFICADA | `10.4324/9780080522159-21` (capítulo de 2013); gamedeveloper.com (1999) | o texto online, por ferramenta de leitura | a base de dados de salas para propagar o som; os guardas que decidem pelo que percebem |
| 11 | Walsh (2015). Modeling Perception and Awareness in Tom Clancy's Splinter Cell Blacklist. Game AI Pro 2, cap. 28 | cinza (capítulo técnico) | VERIFICADA | `10.1201/b18373-34` | texto lido (PDF do gameaipro.com) | a distância do som pelo caminho de áreas; a visão por raios a oito partes do corpo |
| 12 | Komosiński e Ulatowski (1999). Framsticks: Towards a Simulation of a Nature-Like World, Creatures and Evolution. ECAL'99, LNCS | par | VERIFICADA | `10.1007/3-540-48304-7_33` | só metadados | a existência do sistema |
| 13 | Komosiński (2003). The Framsticks system: versatile simulator of 3D agents and their evolution. Kybernetes 32(1/2), 156-173 | par | VERIFICADA | `10.1108/03684920310452382` | resumo | o simulador de agentes 3D com sistema de controle embutido |
| 14 | Framsticks, página de vídeos do site oficial | cinza (site oficial) | VERIFICADA (sem DOI) | framsticks.com/a/al_grafika.html | página lida | receptores de cheiro detectam energia; o outro organismo "cheira como energia" |
| 15 | Yaeger, L. (1994). Computational Genetics, Physiology, Metabolism, Neural Systems, Learning, Vision, and Behavior or PolyWorld: Life in a New Context. Artificial Life III, 263-298 | par (anais) | VERIFICADA (sem DOI) | PDF do autor (shinyverse.org) | texto lido, pp. 1 a 10 | as entradas (visão, energia, aleatório); a visão desenhada; o comportamento de acender |
| 16 | Braitenberg, V. (1984). Vehicles: Experiments in Synthetic Psychology. MIT Press | livro | VERIFICADA (sem DOI) | existência pela resenha de Dennett, `10.2307/2185146` | não lido | só a existência; o conteúdo vem pela descrição de Yaeger (1994) |
| 17 | Beer e Gallagher (1992). Evolving Dynamical Neural Networks for Adaptive Behavior. Adaptive Behavior 1(1), 91-122 | par | VERIFICADA | `10.1177/105971239200100105` | resumo | um controlador de quimiotaxia evoluído |
| 18 | Webb, B. (1995). Using robots to model animals: a cricket test. Robotics and Autonomous Systems 16, 117-134 | par | VERIFICADA | `10.1016/0921-8890(95)00044-5` | só título | só que existe um robô modelo do grilo; o mecanismo fica SEM FONTE |
| 19 | Ishida, Wada e Matsukura (2012). Chemical Sensing in Robotic Applications: A Review. IEEE Sensors J. 12(11), 3163-3173 | par | VERIFICADA | `10.1109/JSEN.2012.2208740` | resumo | robôs que seguem trilhas químicas, rastreiam plumas e mapeiam substâncias |
| 20 | Dwarf Fortress Wiki, verbete "DF2014:Body token" | cinza (fã) | NÃO VERIFICADA EM FONTE PRIMÁRIA | dwarffortresswiki.org | página lida | **pista:** as partes do corpo com função de ver, ouvir, cheirar, respirar; a de cheirar sem função conhecida |
| 21 | Adams, T. (2019). Emergent Narrative in Dwarf Fortress. In *Procedural Storytelling in Game Design* | cinza (capítulo do autor do jogo) | VERIFICADA | `10.1201/9780429488337-15` | resumo | só a narrativa emergente; **não** descreve o corpo |
| 22 | Sims, K. (1994). Evolving virtual creatures. SIGGRAPH '94, 15-22 | par | VERIFICADA | `10.1145/192161.192167` | resumo | morfologia e sistema neural gerados juntos por um grafo dirigido |
| 23 | Lewis e Cañamero (2016). Hedonic quality or reward? Adaptive Behavior | par | VERIFICADA | `10.1177/1059712316666331` | resumo | o prazer, ligado ou não a uma necessidade, melhora a viabilidade e a flexibilidade de um robô |
| 24 | Lones, Lewis e Cañamero (2018). A Hormone-Driven Epigenetic Mechanism for Adaptation in Autonomous Robots. IEEE TCDS 10(2) | par | VERIFICADA | `10.1109/TCDS.2017.2775620` | resumo | a concentração de um hormônio regula o próprio receptor; robô Koala em seis ambientes |
| 25 | Bongard, Zykov e Lipson (2006). Resilient Machines Through Continuous Self-Modeling. Science 314 | par | VERIFICADA | `10.1126/science.1133687` | resumo (revisão G) | o automodelo da própria morfologia |
| 26 | Zufall e Leinders-Zufall (2000). The Cellular and Molecular Basis of Odor Adaptation. Chemical Senses 25(4), 473-481 | par | VERIFICADA | `10.1093/chemse/25.4.473` | resumo | duas formas rápidas e uma persistente de adaptação no receptor olfativo |
| 27 | Louis, Huber, Benton, Sakmar e Vosshall (2008). Bilateral olfactory sensory input enhances chemotaxis behavior. Nature Neuroscience 11, 187-199 (online em 2007) | par | VERIFICADA | `10.1038/nn2031` | resumo (Europe PMC) | um neurônio olfativo basta para a quimiotaxia; os dois lados aumentam a precisão |
| 28 | Rajan, Clement e Bhalla (2006). Rats Smell in Stereo. Science 311, 666-670 | par | VERIFICADA | `10.1126/science.1122096` | resumo | a diferença de intensidade e de tempo entre as narinas como pista de direção |
| 29 | Grothe, Pecka e McAlpine (2010). Mechanisms of Sound Localization in Mammals. Physiological Reviews 90, 983-1012 | par | VERIFICADA | `10.1152/physrev.00026.2009` | resumo | o espaço do som não está na cóclea; a localização é binaural |

**Conferidos e não usados:**
- Deneubourg et al. (1990), `10.1007/BF01417909`, e Russell (1999), `10.1142/4042`: sem resumo obtido;
- Dorigo e Gambardella (1997), `10.1109/4235.585892`: redundante com o item 6;
- Berg e Brown (1972), `10.1038/239500a0` (a quimiotaxia da *E. coli*): sem resumo obtido.
