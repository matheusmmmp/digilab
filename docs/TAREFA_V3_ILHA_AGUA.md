# TAREFA V3: a ilha onde só a água barra (ILHA_AGUA)

**Estado: APROVADO** pelo Matheus em 2026-11-10 ("Eu aprovo"): as IA-1 a IA-5 da seção 6 ficam decididas pela recomendação.

**Pedido do Matheus (2026-11-10):** "Eu não quero que tenha uma área que o pet não acesse. Eu quero que o pet consiga andar pela ilha
inteira, só não atravesse a água. As barreiras têm que ser delimitadas pela água." Entre os dois caminhos apresentados, ele escolheu o B:
"faz o B. O interessante seria o B".

**O levantamento que veio antes:** a nota `20 Temas/Ilha fechada.md` do vault DigiLab Research (a ilha de hoje, a comparação com o Animal
Crossing e a primeira proposta, que caiu por ter terra onde o pet não entra).

## 1. O que muda, em uma frase

A ilha passa a ser uma só: toda a terra que aparece na tela é terra onde o pet pisa, e o que limita o pet é a água (o mar em volta, o
rio e as lagoas), que ele contorna e atravessa pelas pontes.

## 2. O que já existe (FATO VERIFICADO, lido na main bfc44a5f)

- **O mundo do pet é um retângulo sem obstáculo.** `ConfigMundo` tem `celulas_x = 64`, `celulas_y = 30` e `sub = 16`
  (`web/app/motor/constantes.ts`, `CMU`; o espelho de `digilab/config.py`). O pet anda em linha reta até o alvo (`passoAte`,
  `web/app/motor/mundo.ts:218`) e para na borda do retângulo.
- **O desenho da ilha é maior que o mundo.** A grade da vista tem 88 × 52 células (`web/app/src/telas/pet/ilha/grade.ts`, `MOLDURA`). O
  rio, a lagoa, o platô, o morro e a mata ficam na moldura, fora do retângulo: o pet não entra neles porque o motor nem sabe que existem.
- **O motor já tem colisão e desvio, desligados.** O contrato da P4 (`digilab/contrato.py` e `web/app/motor/contrato.ts`, com paridade
  conferida por gabarito) tem sólidos retangulares (`Solido`, com `colide` e `alto` separados), o movimento com deslize (`mover`), a
  grade de células livres (`grade`) e o caminho A* (`caminho`, usado pelo `controlar`). A chave `ConfigContrato.controlador` liga o
  desvio. Hoje os únicos sólidos que colidem são as quatro paredes da borda (chave `paredes`), e o jogo não liga nada disso
  (`CONFIG_CONTRATO`, tudo `false`).
- **O que escolhe um ponto do mapa não conhece a água:** a queda das frutas, a bola que rola (`rolarBola`), o alvo de vagar e de
  explorar (`candidatos`), a ração e a bola que o dono põe (`_validarComida`, `deixarBola`) e o ponto onde o dono solta o pet
  (`levar_pet`, v19).

**Consequência:** o caminho B é menor do que eu disse ao Matheus ao apresentá-lo. O desvio não precisa ser escrito do zero: ele existe,
está nos dois lados e tem paridade. Falta dizer ao mundo onde é água e impedir que as coisas caiam nela.

## 3. O desenho proposto

A figura é um protótipo da regra, feito por script (fora do git, em `D:\Trab\digilab\capturas_objetos3d\ilha\ilha_b.png`). Todos os
números são **PROPOSTO, SEM FONTE**.

- A ilha inteira fica dentro do mundo de 64 × 30. A costa é arredondada e encosta na borda do mundo; os cantos viram mar.
- Das 1 920 células do mundo, cerca de 1 470 são terra (77 %). O script confere que todas são alcançadas a pé a partir do ninho.
- Um rio nasce numa lagoa ao norte, desce com uma curva e sai no mar do sul. Duas pontes o atravessam.
- Uma lagoa a sudoeste.
- A praia dá a volta na ilha, mais larga ao sul, onde fica o cais (a chegada).
- Os marcos e os lugares que hoje ficam na moldura (o portão, o carro, o trilho, a lata, a geladeira, o cais) vêm para dentro.
- Não há morro, platô nem mata fechada: eram terra onde o pet não entra. Relevo baixo onde o pet anda pode voltar depois, como desenho.

## 4. A mecânica

Tudo atrás de uma chave nova, desligada por padrão. Com a chave desligada, o mundo de hoje sai byte a byte.

1. **A água no layout.** `LayoutMundo` ganha `agua`: uma lista de retângulos em células. Um layout novo (`LAYOUT_MUNDO_ILHA`) traz a
   costa, o rio e as lagoas; as pontes são os vãos sem retângulo. Os layouts de hoje ficam com a lista vazia.
2. **A categoria `agua` no contrato.** Um sólido que colide e não tapa a visão (`colide = true`, `alto = false`): o pet vê a outra
   margem, mas não atravessa. Entra nos sólidos com a chave nova `ConfigContrato.agua`, que exige o `controlador`.
3. **O pet contorna.** Com o `controlador` ligado, o pet segue o caminho A* até o alvo e passa pela ponte. Alvo na água vale a célula
   seca mais perto (`livreMaisPerto`, que já existe).
4. **Nada cai na água.** A fruta que cairia na água cai na célula seca mais perto; a bola quica na margem (o `passoBola` do contrato, já
   portado); o alvo de vagar e de explorar é sorteado só entre as células secas; a ração, a bola e o pet que o dono solta na água vão para
   a célula seca mais perto.
5. **A versão do pet.** Uma versão nova (a próxima livre) liga a chave. Os pets de antes continuam valendo no replay.
6. **A vista.** A grade da ilha passa a ler a água do layout, em vez de desenhá-la na moldura. A moldura vira só mar. A ponte é um
   objeto em cartoon, feito por script (o padrão de 2026-11-10).

## 5. As etapas

| Etapa | O que entrega | Onde |
|---|---|---|
| IA0 | Este plano e a figura | docs |
| IA1 | O gabarito com a chave desligada (commit próprio), depois a água no Python: o layout, a categoria, a chave, as regras do item 4, os testes | `digilab/config.py`, `digilab/contrato.py`, `digilab/mundo.py` (o `digilab/engine.py` não muda) |
| IA2 | O espelho na web, com a paridade contra o gabarito do Python | `web/app/motor/` |
| IA3 | A vista: a ilha desenhada a partir do layout, os lugares e os marcos nos pontos novos, a ponte | `web/app/src/telas/pet/ilha/` |
| IA4 | A versão nova ligada no jogo, a passagem dos pets vivos, as capturas no desktop e no celular | motor e vista |

Cada etapa é um PR. A IA1 e a IA2 são mecânica (Python primeiro, depois a web); a IA3 é só vista e pode andar junto com a IA2.

**Os gates (o que cada etapa prova):**

- **G-AG-1:** com a chave desligada, o gabarito sai byte a byte, no Python e na web.
- **G-AG-2:** com a chave ligada, em nenhum tick o pet, uma comida ou a bola está numa célula de água (vidas inteiras, com dono e sem dono).
- **G-AG-3:** toda célula seca do layout é alcançada a pé a partir do ninho.
- **G-AG-4:** a paridade entre o Python e a web com a chave ligada.
- **G-AG-5:** o pet chega à comida que está do outro lado do rio (ele usa a ponte).

Não há calibração nesta tarefa (o equilíbrio fica para a rodada geral). Se a ilha nova mudar quanto o pet come ou anda, isso é medido e
relatado, não ajustado.

## 6. As decisões do Matheus

| # | Decisão | Recomendação | Custo de errar |
|---|---|---|---|
| IA-1 | O tamanho do mundo | **Manter 64 × 30** e recortar a água dentro dele | Com o mundo maior, a ilha ganha espaço, mas mudam as distâncias de tudo (o cheiro, o longe, a bola), e o que foi medido até hoje deixa de valer. Mantendo, a ilha fica mais apertada: 1 470 células de terra para todos os lugares |
| IA-2 | O desenho da seção 3 (a costa, um rio com duas pontes, uma lagoa) | **Sim, como ponto de partida**; o desenho é uma lista de retângulos e muda sem mexer no código | Um rio no meio separa a barraca e o trilho do ninho: o pet anda mais para chegar lá |
| IA-3 | O morro, o platô e a mata | **Saem agora.** Relevo baixo onde o pet anda fica para depois | Sem eles a ilha fica plana; com eles agora, a vista teria de subir e descer o pet no terreno, que é outro trabalho |
| IA-4 | Os pets que já estão vivos | **Passam para a ilha nova** por um evento no log (o pet que estiver na água vai para a célula seca mais perto) | Se só os pets novos ganharem a ilha, o pet de hoje do Matheus fica no retângulo e a vista tem de manter as duas ilhas. A forma do evento eu confirmo na IA1, lendo como as versões trocam hoje |
| IA-5 | Quem constrói a mecânica (IA1 e IA2) | **Esta sessão**, com um revisor separado antes de cada PR | O motor é de outra frente. Se houver uma sessão dona do motor trabalhando nele agora, dois PRs podem bater; nesse caso a IA1 vai para ela e eu fico com a IA3 |

## 7. O que esta tarefa não faz

- Não muda o `digilab/engine.py`.
- Não calibra nada.
- Não põe nado, barco nem pesca: a água só barra.
- Não mexe nos objetos da ilha além de mudar o ponto de cada um e fazer a ponte.
- Não decide o relevo (IA-3).

## 8. O que não foi verificado

- **NÃO CONFIRMADO:** o custo do A* a cada tick no celular. O `controlar` recalcula o caminho a cada tick da decisão; no mundo de 64 × 30
  a grade tem 1 920 células. Mede-se na IA2.
- **NÃO CONFIRMADO:** como o pet de laboratório (v16), a luta (v21) e o segundo pet usam o mundo. Lê-se na IA1, antes do gabarito.
- **NÃO CONFIRMADO:** o `ConfigContrato` no Python só vale "com um pet (fora do grupo)" (`digilab/mundo.py`, cabeçalho). Se o jogo tiver
  mais de um pet no mundo, a IA1 trata disso antes.

## 9. IA1: o que foi construído (2026-11-10)

A água no mundo do Python, sem mudar nenhuma vida de antes.

- **O mapa:** `AGUA_ILHA` em `digilab/config.py`, 30 linhas de 64 caracteres (`~` mar, `r` água doce, `.` terra, `=` ponte), na tabela
  `AGUA_POR_LAYOUT` pelo nome do layout. Dois mundos a usam: `CONFIG_MUNDO_ILHA_AGUA` (a ilha com árvores) e `CONFIG_MUNDO_MVP_AGUA` (o
  mundo do produto que o jogo web roda hoje).
- **A barreira:** `solidos_da_agua` vira os sólidos que o controlador do contrato contorna (`CONFIG_CONTRATO_AGUA`). O layout com água
  exige o controlador.
- **Nada cai na água:** a comida, a bola e a necessidade postas na água vão para a célula de terra mais perto; a bola que rola para na
  margem; o alvo sem objeto escolhido na água vale a terra mais perto; o pet solto na água, ou rente a ela, cai no centro da célula.
- **Diferenças para a seção 4:** não há chave `ConfigContrato.agua` nem categoria `agua`; a água vai pelo nome do layout e usa a
  categoria `obstaculo`; a bola para na margem em vez de quicar. Os motivos estão em `docs/registro/2026-11.md`.
- **Os gates:** G-AG-1 (os gabaritos de antes byte a byte), G-AG-2 (nada na água, tick a tick, em duas vidas de 2 dias do gabarito e uma
  na ilha com árvores), G-AG-3 (o layout ilhado falha alto) e G-AG-5 (o pet cruza pela ponte) em `tests/test_ilha_agua.py`.

## 10. IA2 e IA3: o que foi construído (2026-11-10)

- **IA2, a web:** o espelho da água no motor TypeScript (`web/app/motor/`), com a paridade contra o gabarito do Python decisão a decisão
  (`web/app/test/ilha_agua.test.ts`). O jogo de hoje não muda.
- **IA3, a vista:** com água no layout, a grade da ilha (`web/app/src/telas/pet/ilha/grade.ts`) desenha a terra do motor célula a célula,
  com a praia em volta, o rio, a lagoa e o mar na moldura. Os lugares e os marcos ficam dentro da ilha (`PLANTA_ILHA_AGUA`), e as pontes
  são feitas por código (`ponte.ts`). A prévia é `?ilha=agua`; o jogo só passa a usá-la na IA4.
- **O mapa mudou na IA3:** o rio ficou reto debaixo das duas pontes (6 células). A terra tem 1 321 células.
- **Fica para a IA4:** ligar no jogo (a versão do pet e a passagem dos pets vivos), o pet que hoje atravessa os marcos, e a ida do pet
  até um lugar aberto, que é em linha reta e cruzaria o rio.


## 10b. IA4: o que foi construído (2026-11-10)

- **Decidido pelo Matheus:** a versão que liga a água é a **v22**, e os pets vivos **migram por evento**.
- **A v22** nasce na ilha com água. A v21 segue abrindo e passa para a mesma ilha pelo evento `mudar_ilha` (o `mi` do registro do jogo),
  uma vez, ao abrir: o que estiver na água vai para a terra mais perto.
- **O evento** existe no Python (`MotorMundo.mudar_ilha`) e na web, com a paridade conferida por um gabarito próprio
  (`web/app/test/gabaritos/mudar_ilha_python.json`): duas vidas, uma troca com o pet acordado e outra com ele dormindo.
- **A ida do pet a um lugar aberto** contorna a água pelo caminho em terra.
- **O pet de teste (v16)** fica na ilha sem água.

## 11. Depois da IA4: os ajustes do desenho (planejamento futuro)

**Estado: PROPOSTO.** O Matheus confirmou em 2026-11-10 que o desenho da ilha ainda vai ser ajustado e que entram mais árvores
("você vai ajustar o desenho e botar mais árvores, né? Tá no plano. Planejamento futuro."). Nada desta seção está construído nem tem
data; a ordem e a forma de cada item ele decide quando a IA4 estiver pronta.

| Etapa | O que entrega | O que precisa ser decidido antes |
|---|---|---|
| IA5 | **Árvores na ilha.** Hoje a ilha com água não tem nenhuma: a regra é que nada alto fica onde o pet anda, e a moldura virou mar | Como a árvore convive com o pet. Recomendação: a árvore ocupa a célula dela e o pet a contorna, pelo mesmo desvio da água (o motor já sabe contornar um obstáculo). A outra forma é a árvore só de enfeite, que o pet atravessa |
| IA6 | **O desenho da costa, do rio e das lagoas revisto** na tela (a forma, a largura da praia, mais uma lagoa ou um braço de rio). O mapa é uma lista de linhas de texto e muda sem mexer no código | Só o desenho novo. Cada mudança do mapa refaz o gabarito da paridade |
| IA7 | **Relevo baixo onde o pet anda** (a IA-3 deixou para depois): colinas suaves, sem penhasco que barre | Se a vista sobe e desce o pet no terreno; é trabalho só de vista |
| IA8 | **Os marcos como obstáculos:** o pet contorna o carro, o trilho, a geladeira e o portão em vez de atravessá-los | Junto com a IA5: é a mesma mecânica |

O que **não** entra aqui: nado, barco, pesca e mata fechada onde o pet não entra (seções 1 e 7).

## 12. A ilha grande (a v23): o plano

**Estado: APROVADO** pelo Matheus em 2026-11-11 ("Aprovo, começa a IG1"): as IG-4 a IG-9 da seção 12.6 ficam decididas pela
recomendação. A IG1 está construída (seção 12.8); as outras etapas, não.

O pedido, em 2026-11-11: "A ilha, ela é muito pequena. Eu quero que aumente ela pra parecer uma ilha de verdade."

### 12.1 O que já está decidido (pergunta desta sessão, 2026-11-11, com a recomendação e o custo de errar)

| # | Decisão | Resposta do Matheus |
|---|---|---|
| IG-1 | Como a ilha cresce | **"Mundo maior no motor (Recomendado)"**: o mapa do motor cresce e o pet anda por tudo |
| IG-2 | O tamanho | **"128 x 60"** (a recomendação era 96 × 48; o Matheus escolheu o maior, 4 vezes a área) |
| IG-3 | As árvores e os marcos como obstáculos (IA5 e IA8 da seção 11) | **"Sim, tudo na v23 (Recomendado)"**: uma versão e uma migração só |

Com isto a IA5 e a IA8 da seção 11 deixam de ser etapas à parte. A IA6 (o desenho da costa e do rio) é a figura desta seção. A IA7 (o
relevo baixo) continua para depois.

### 12.2 O que existe hoje (FATO VERIFICADO, lido na main de 2026-11-11)

- O tamanho do mundo é parâmetro: `ConfigMundo.celulas_x` e `celulas_y` (64 e 30), com 16 subunidades por célula.
- A água é uma linha de texto por linha de células (`AGUA_POR_LAYOUT`), com o mar, a água doce, a terra e a ponte. Hoje são 1 321
  células de terra.
- As **regiões** (casa, jardim, campo, mata) são faixas de x fixas no layout (0–15, 16–33, 34–47, 48–63). O corpo, a política e o
  DigiBrain modular (`sens`, `mem`, `adapt`) leem o nome da região.
- Os sentidos e o passo são em células: a visão 6, o cheiro 24, o passo do cheiro 8; a velocidade é 4 subunidades por tick.
- A troca de ilha por evento (`mudar_ilha`, o `mi` do jogo) já existe e leva o pet para a terra mais perto (IA4).

### 12.3 A figura do mapa proposto

`docs/pranchas/ilha-grande/mapa_proposto.png` (gerada por `gerar_figura.py`, na mesma pasta; o texto do mapa em `mapa_proposto.txt`).
128 × 60 células, 4 087 de terra livre (3,1 vezes a de hoje), um rio com três pontes, dois lagos e um laguinho, 79 árvores em oito
bosques e soltas, e os quatro marcos ocupando as células deles. A ilha de hoje aparece embaixo, na mesma escala. É um ponto de
partida: PROPOSTO, SEM FONTE.

### 12.4 A mecânica nova

- **A árvore e o marco são células fechadas**, como a água: o pet contorna pelo mesmo desvio. No mapa viram dois caracteres novos.
  Nenhuma regra de desvio nova.
- **A fruta não entra aqui.** A árvore desta seção é só obstáculo. A árvore que sacode e dá fruta é de outra frente
  (`docs/TAREFA_V3_ARVORE_SACODE.md`).
- **A v23** é a v22 no mundo de 128 × 60. Os ovos novos nascem v23; a v21 e a v22 seguem abrindo.

### 12.5 As etapas (um PR cada, com revisor separado antes do PR, como na IA-5)

| Etapa | O que entrega | Muda o jogo de hoje? |
|---|---|---|
| IG1 | **O mundo grande no Python:** o layout de 128 × 60, as células fechadas de árvore e de marco, as regiões novas, os testes e o gabarito. Atrás de chave: as vidas de hoje saem byte a byte | Não |
| IG2 | **O mesmo no motor da web,** com a paridade contra o gabarito do Python | Não |
| IG3 | **A vista:** a grade desenha a ilha grande (as árvores, os marcos no lugar das células deles, os lugares, as pontes, a praia), o minimapa e a câmera; página de pré-visualização | Não |
| IG4 | **Ligar:** a v23, e a migração dos pets v21 e v22 por evento | **Sim** |
| IG5 | **Medir e ajustar:** o custo do desvio num celular de verdade e o tempo que o pet leva para chegar na comida; os ajustes que a medida pedir | Depende |

### 12.6 As decisões IG-4 a IG-9 (DECIDIDAS pela recomendação em 2026-11-11)

| # | A pergunta | A recomendação | O custo de errar |
|---|---|---|---|
| IG-4 | A figura (12.3) serve como ponto de partida? | **Sim.** O mapa é texto e muda sem mexer no código até a IG4 | Depois da IG4, mudar o mapa é outra versão de pet |
| IG-5 | As regiões no mundo grande | **As mesmas quatro, com as faixas de x dobradas** (0–31, 32–67, 68–95, 96–127) | As regiões alimentam o cérebro. Com faixas diferentes, o que o pet aprendeu sobre "casa" e "mata" muda de lugar na migração |
| IG-6 | A velocidade e os sentidos (a visão 6, o cheiro 24) | **Não mexer agora.** Medir na IG5 e ajustar com número | Sem mexer, o pet pode demorar o dobro para cruzar a ilha e não sentir a comida longe. Mexendo sem medir, muda o comportamento do pet sem evidência. É o risco que a recomendação de 96 × 48 evitava |
| IG-7 | Onde ficam o pet, a comida e a bola dos pets vivos na migração | **Deslocados junto com o lar** (o lar de hoje vai para o lar novo), e o que cair em água, árvore ou marco vai para a terra mais perto | Se ficarem nas coordenadas de hoje, o pet acorda no canto noroeste do mar |
| IG-8 | O cérebro modular e a pesquisa | **Só o jogo usa o mundo grande.** A bancada e as runs de pesquisa ficam no mundo de hoje | Se a pesquisa trocar de mundo, os resultados já gravados deixam de ser comparáveis |
| IG-9 | Quem constrói | **Esta sessão,** com revisor separado a cada etapa | O motor é de outra frente; se houver sessão dona mexendo nele, os PRs colidem |

### 12.7 O que não foi verificado

- **O custo do desvio:** o mapa tem 7 680 células, 4 vezes o de hoje, e o custo no celular já não estava medido com 1 920.
- **O efeito no pet:** nenhuma vida rodou no mundo grande. Não sei se o pet acha a comida, nem quanto tempo leva.
- **A vista:** a grade, a câmera, o minimapa e a luz foram feitos para 64 × 30; o que quebra com 128 × 60 só aparece na IG3.
- **O DigiBrain modular** (`sens`, `mem`, `adapt`) com as regiões novas: lido por alto, não testado.

### 12.8 IG1: o que foi construído (2026-11-11)

- **O mundo grande no Python:** `CONFIG_MUNDO_GRANDE` (128 × 60 células), o layout `grande` e o mapa `AGUA_ILHA_GRANDE`, com dois
  caracteres novos, a árvore fechada (`T`) e o marco fechado (`#`). O motor os trata como a água: viram sólidos e o pet contorna.
  Nenhuma regra de desvio nova.
- **O `ConfigMundo` aceita dois tamanhos,** 64 × 30 e 128 × 60, com 16 subunidades por célula, e nenhum outro.
- **O banheiro no layout com água** tem de ficar inteiro em células em que o pet pisa; senão o motor falha alto. O retângulo de
  sempre do banheiro cai no mar da ilha grande, então a ilha grande ainda não combina com o banheiro (o jogo não o usa).
- **As posições dos eventos** (a ração, a fruta e a bola que o dono põe) valem até o tamanho do mapa de cada mundo. Antes o limite era
  fixo em 1024 × 480 subunidades. Quem não passa o tamanho (o grupo, os replays de antes) continua no limite de antes.
- **As regiões** são as quatro de sempre com as faixas dobradas (IG-5).
- **O gabarito da paridade** (`web/app/test/gabaritos/ilha_grande_python.json`): duas vidas de 2 dias com o roteiro da água nos pontos
  deste mapa, mais a ração e o pet soltos em cima de uma árvore e de um marco. O TS confere contra ele na IG2.
- **As vidas de hoje não mudaram:** os gabaritos da água e da troca de ilha, regerados, saem iguais.

**Desvio da figura aprovada (IG-4):** na primeira figura o lar ficava em (44, 30), que nas faixas aprovadas (IG-5) é o jardim. No MVP o
ninho fica na casa, e o cérebro lê o nome da região. O lar foi para (20, 30), na casa; o carro e o saco mudaram de lugar para dar
espaço, e as árvores foram sorteadas de novo (79 em vez de 84). A figura e o texto do mapa em `docs/pranchas/ilha-grande/` são os
novos. PROPOSTO, SEM FONTE.

**A primeira medida** (`experiments/medir_ilha_grande.py`, artefato em `docs/pranchas/ilha-grande/medida_ig1.json`; cinco sementes
dos testes, 4 dias, uma ração a cada terço de dia a uma distância fixa a leste do ninho; descritiva, sem gate):

| Distância (células) | Hoje, 64 × 30: comidas no prazo | Ilha grande: comidas no prazo | Mediana até comer |
|---|---|---|---|
| 4 | 6 de 23 | 6 de 21 | 15 ticks nos dois |
| 12 | 6 de 24 | 5 de 22 | 60 ticks nos dois |
| 24 | 3 de 11 | 3 de 11 | 120 ticks nos dois |
| 36 | 0 de 26 | 0 de 26 | — |
| 48 e 56 | não cabe | 0 de 26 | — |

À mesma distância o pet se sai igual nos dois mundos. Além de 24 células (o alcance do cheiro) ele não comeu nenhuma ração no prazo, em
nenhum dos dois. O que muda na ilha grande é que essas distâncias passam a existir entre o lar e a maior parte da ilha. É o dado para a
IG-6; nada foi ajustado.

**Os limites da medida:** a ração nova é posta sem tirar a anterior, e conta ração com o pet sem fome (6 de 23 a 4 células). Serve
para "além de 24 células, nada"; não serve como taxa de alcance. A 24 células as rações postas são 11, contra 21 a 26 nas outras
distâncias; não investiguei o motivo.

**A revisão separada** (um agente de leitura, antes do PR) não achou defeito que mude a vida de hoje nem o replay. Apontou três riscos:
a validação do tamanho aceitava outras combinações de células e subunidades (corrigido), o banheiro de sempre cairia no mar da ilha
grande em silêncio (corrigido: falha alto), e a métrica do hábito (`digilab/metrics.py`, I5) é fixa em 64 × 30 e erraria numa vida
do mundo grande (não corrigido: a pesquisa não usa o mundo grande, IG-8; fica registrado como armadilha).

**O que não foi verificado:** a suíte inteira do Python não rodou; o custo no celular; o DigiBrain modular com as regiões novas (a
medida usa o A do v11); a fruta posta ao lado da ração no mundo grande (o caminho recebe o tamanho do mapa, mas não tem teste lá). A
árvore e o marco não tapam a visão do pet, como a água. O grupo de dois pets continua no limite de 64 × 30.

### 12.9 IG2: o que foi construído (2026-11-11)

- **O mundo grande no motor da web:** `CMU_GRANDE`, o layout `grande` e o `AGUA_ILHA_GRANDE` em `web/app/motor/constantes.ts`, com a
  árvore e o marco fechados. O `celulasSecas` aceita os dois caracteres novos.
- **As posições dos eventos** (`eventoDeixarComida`, `eventoDeixarBola` e as leituras) recebem o tamanho do mapa; o `Mundo` e o laço
  (`motor_corpo_mundo.ts`) passam o do mundo deles. Quem não passa fica no limite de 1024 × 480.
- **A paridade:** o TS refaz as duas vidas do gabarito do Python (`ilha_grande_python.json`) decisão a decisão, com o log, o mundo e o
  corpo iguais no fim, e os mesmos sólidos na mesma ordem.
- **O `Motor` do jogo (`motor/motor.ts`) não mudou:** ele ainda valida a ração e a bola do jogador no limite de 1024 × 480. Passar o
  tamanho do mapa ali é da IG4, que é quem põe um pet no mundo grande.
- **O tempo na web** (medida única desta sessão, no Node desta máquina, sem artefato): uma vida de 2 dias do gabarito levou 52 e 71 ms
  na ilha grande, contra 33 e 49 ms no mundo de hoje. No celular não foi medido.

**A revisão separada da IG2** (um agente de leitura, sobre o commit `c81aa747`) não achou defeito nem divergência entre o TS e o Python
no mundo grande, nem mudança para os pets de hoje. Dois riscos baixos, corrigidos: o TS não conferia o tamanho do mundo (o `Mundo`
agora só aceita os dois tamanhos, como o Python), e o teste de paridade não conferia os próximos sorteios de cada fluxo de acaso nem
o número de decisões (agora confere). Ficam registrados, sem correção:

- **A bola no mundo grande não tem paridade:** o roteiro do gabarito não põe bola, e as vidas têm uma rolagem e nenhuma.
- **A memória do cérebro modular** (`d_max = 1024`, em `motor/digibrain/mem.ts` e no `config.py`) vale a largura do mapa antigo: na
  ilha grande, um lugar lembrado a mais de 64 células não atrai. É assunto da IG-6, junto com o cheiro de 24 células.
- **A vista** (`src/telas/pet/ilha/grade.ts`) desenharia a árvore e o marco fechados como chão livre: é a IG3.
- **O `Motor` do jogo** recusaria a ração além de x = 1023 ou y = 479 num pet do mundo grande, falhando alto: é a IG4.

### 12.10 IG3: o que foi construído (2026-11-11)

- **A vista desenha a ilha grande** a partir do mapa do motor (`grade.ts`): a terra, o mar em volta, a praia, o rio, os lagos e as
  pontes. Cada árvore fechada do mapa vira uma árvore no centro da célula dela (pinheiro ou árvore redonda, pela célula, sem sorteio).
  Cada marco (o carro, a lata, a geladeira, o trilho) fica em cima do bloco de células fechadas dele.
- **A planta da ilha grande** (`PLANTA_ILHA_GRANDE`): a praça no meio, o lar a oeste, o portão na ponta norte, a barraca do outro lado
  do rio (o caminho passa pela ponte do meio), o cais na praia do sul e 13 postes. A praia é mais larga que a da ilha de hoje.
- **O mapa foi regerado** para nenhuma árvore cair nos caminhos nem na praça: o gerador da figura conhece os caminhos da planta. O
  número de árvores (79) e de células livres (4 087) ficou igual; as posições mudaram. O gabarito da paridade, o `config.py` e o
  `constantes.ts` foram regerados com ele (a pilha ainda não tinha sido mergeada).
- **A luz:** os focos dos caminhos passariam do máximo do shader (54 contra 48); na ilha grande o espaçamento cresce até caber. Nas
  ilhas de hoje o espaçamento é o de sempre.
- **A prévia:** `?ilha=grande` desenha a ilha grande sem mexer no motor, e `?foco=x,z` aponta a câmera para um ponto (só na prévia).
  O pet da prévia continua no mundo dele, então aparece no canto noroeste, no mar: é esperado até a IG4.
- **O jogo de hoje não muda:** sem o parâmetro, a vista desenha a ilha do mundo do pet, como antes.

**Visto na tela** (medida única desta sessão; capturas fora do git por mostrarem o pet): a praça com os postes e o caminho do portão,
o carro e a lata, a ponte do meio com o rio, e a praia do sul, em 1440 × 800; a praça em 375 × 812; nos mapas Digital e Ilha.

**O que não foi verificado:** o cais não apareceu em nenhuma captura (a câmera olha para o norte e ele fica atrás dela); a barraca, a
geladeira e o trilho não foram vistos; o custo num celular de verdade (a grade tem 11 840 células, contra 3 680 hoje); as nuvens
em anel e o portal do céu foram feitos para a ilha de hoje e não foram revistos para o tamanho novo.

**A revisão separada da IG3** (um agente de leitura, sobre os commits `93db73eb` e `f30e7a78`) não achou defeito que mude as ilhas de
hoje, o save ou o replay. Três riscos, corrigidos: nada ligava os caminhos do gerador do mapa aos da planta da vista (o gerador agora
grava o `planta_livre.json`, e o teste confere a planta contra ele); o entorno dos marcos, os lugares e os postes aceitavam uma célula
fechada como chão (agora recusam; só o próprio marco fica em cima do bloco dele); e a luz deixava de falhar alto nas ilhas antigas (o
espaçamento agora só cresce na ilha grande). Fica registrado, sem correção: treze árvores ficam na areia da praia, e a geladeira tem
uma árvore a 2 células. A tela não foi vista de novo depois dessas correções.
