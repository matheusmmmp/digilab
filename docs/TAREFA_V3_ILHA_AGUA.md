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

### 12.11 IG4: o que foi construído (2026-11-11)

**Esta etapa muda o jogo de hoje.** Todo pet que abrir passa a viver na ilha grande.

- **A v23:** os ovos novos nascem v23, a v22 no mundo de 128 × 60, com as árvores e os marcos que o pet contorna. A v21 e a v22 seguem
  abrindo.
- **Os pets vivos migram por evento:** o pet v21 ou v22 ganha, uma vez, o evento `mi` para a ilha grande ao abrir (o save, um pet
  guardado, um arquivo importado). São três caminhos: o v21 que nunca tinha passado para a água, o v21 que já tinha passado, e o v22,
  que nasceu nela.
- **A ida (IG-7, "deslocados junto com o lar"):** o lar de lá vira o lar de cá. O pet, a comida e a bola andam o mesmo deslocamento
  (16 células para o leste e 15 para o sul); o que cair em água, árvore, marco ou fora do mapa vai para a terra mais perto. A bola para
  onde está. Nada do pet muda além do mundo: não é contato nem cuidado.
- **No Python e na web:** o mesmo `mudar_ilha`, agora com um destino de outro tamanho (`ILHAS_MAIORES`). A paridade é conferida por um
  gabarito próprio, com os três caminhos (um deles com o pet dormindo).
- **A ração e a bola do jogador** valem até o tamanho do mapa de cada pet; fora dele o jogo falha alto antes do registro.
- **O pet de teste (v16)** e o pet morto ficam como estão.

**O que a ida faz com o que o pet sabia:**

- **As regiões mudam de lugar para o que estava longe do lar.** O deslocamento é o mesmo para tudo, e as faixas das regiões dobraram:
  o que estava na casa ou no jardim de hoje continua na casa ou no jardim; o que estava no campo ou na mata de hoje (da coluna 34 em
  diante) cai no jardim ou no campo da ilha grande.
- **A orientação do pet volta ao começo e o registro das decisões do controlador começa vazio,** como na troca para a água.
- **O que o pet lembrava vai junto.** O DigiBrain modular, que é o cérebro padrão dos ovos, guarda o ponto de cada episódio (onde
  comeu, onde foi e não achou). Na ida, cada ponto lembrado anda o mesmo deslocamento do lar e, se cair em célula fechada, vai para a
  terra mais perto; o lugar e a região do episódio são refeitos do ponto novo. Vale mesmo com o cérebro A decidindo no momento.
- **O cérebro A não guarda posição nem tamanho de mapa** (fora do grupo de dois pets, que não troca de ilha).

**Visto no jogo** (medida única desta sessão; capturas fora do git por mostrarem o pet): um pet v21 de verdade, que já tinha o `mi`
para a água, ganhou o `mi` para a ilha grande ao recarregar e apareceu perto do lar, entre o carro e a lata; o botão Alimentar pôs a
ração no comedouro novo. Desktop 1440 × 800 e celular 375 × 812, no mapa Digital.

**O que não foi verificado:** a suíte inteira do Python; a ida até um lugar (a barraca, pela ponte) no jogo; o pet de teste e o mapa
Ilha na tela depois da mudança; o custo no celular de verdade; uma aba antiga do jogo aberta ao mesmo tempo passa a ver "save que não
abre" (o destino novo do evento), como na IA4.

**A revisão separada da IG4** (um agente de leitura, sobre `8c07aea7..d71c6787`) conferiu que as vidas dos pets que não recebem o evento
saem byte a byte (cinco vidas, comparando o motor de antes com o de agora) e que a ida tem a mesma ordem no Python e na web. Achou dois
defeitos e dois riscos, todos corrigidos antes do PR:

- **A memória de lugar do DigiBrain modular ficava nas coordenadas do mapa velho.** A primeira versão desta seção dizia que não havia
  memória para deslocar, olhando só o cérebro A; o cérebro padrão dos ovos é o modular. Corrigido como descrito acima, no Python
  (`Memoria.deslocar`, o gancho `mundo_deslocado`) e na web, antes de existir qualquer save com o evento.
- **O pet de exemplo de uma versão anterior, nunca tocado, passaria a pagar Bits ao abrir** (já acontecia com o v21 desde a IA4). O jogo
  agora compara com o exemplo da versão do pet.
- **Importar de novo um arquivo exportado antes da ida** dava conflito falso; a comparação agora ignora o evento da ilha.
- **A migração feita ao ouvir outra aba** não ficava marcada para gravar; agora fica.

Fica registrado, sem correção: nenhuma vida do gabarito da paridade usa o modular (o caso do deslocamento da memória é conferido por
um caso fixo igual nos dois lados e por vidas no jogo, só na web); a bola rolando no instante da ida não tem teste; os lugares
"perto" e "longe" da tela de alimentar não têm teste no mapa grande.

### 12.12 A junção com a `main` de 2026-11-11: a ilha grande é a v24, e a TV entra no mapa

O Matheus pediu o merge da pilha em 2026-11-11 ("mas ja faca o merge para evitar grandes problemas na frente, afinal foi adicionado uma
tv que nao estava no seu planejamento"). Entre a base da pilha e o merge entraram 87 commits de outras frentes na `main`. O que mudou
aqui por causa deles:

- **A versão é a v24, não a v23.** A luta da rodada de equilíbrio (LP5-5) entrou antes e ficou com o número 23 (a v22 com a tabela nova
  da luta, na ilha com água de 64 × 30). A ilha grande passa a ser a **v24: a v23 que nasce na ilha grande**, com a luta da v23. Onde as
  seções 12.1 a 12.11 dizem "v23", leia-se v24. Os pets que migram são os v21, os v22 e os v23.
- **O Mundo da web foi separado em dois** pela frente da cooperação (o mundo partilhado e a parte do pet, como no Python). A ida para a
  ilha grande foi reaplicada nessa estrutura: `MundoPartilhado.trocarParaMaior` e o ramo dela em `Mundo.mudarIlha`.
- **A TV** (o marco novo, #814) ganhou uma célula fechada no mapa da ilha grande, em (96, 17), do lado da barraca. O mapa, o
  `config.py`, o `constantes.ts` e os dois gabaritos da paridade foram regerados. A terra livre passou de 4 087 para 4 086 células.
- **O teste do lugar lembrado** (`cenario_lugar_lembrado.test.ts`, da auditoria da cadeia) usava o ovo de hoje com a ração num ponto
  do mapa de 64 × 30, que na ilha grande é mar. Passou a pedir a v23. Na ilha grande, com a ração no comedouro de lá, o modular faz o
  mesmo (26 e 25 escolhas do lugar lembrado em duas sementes, medida única da junção, sem artefato), mas o ponto lembrado fica a 16,5
  unidades do comedouro, fora do raio de 16 daquele teste.
- **O sacudir a árvore** (S2) está no motor da web, mas nenhuma versão de pet o tem ainda; a ida para a ilha grande recusa mundo com
  árvores do layout, e nenhum pet de hoje as tem.

### 12.13 IG5: o plano da medida (escrito antes de rodar, 2026-11-11)

**Para que serve:** decidir a IG-6 (a velocidade, o cheiro e o alcance da memória do pet na ilha grande) com números. A v24 já está no
jogo: qualquer mudança que sair daqui é outra versão de pet, e a decisão é do Matheus.

**O que roda:** o `Motor` do jogo (`web/app/motor/motor.ts`), que é o que o jogador joga, com as chaves do produto. Não é run de pesquisa
do Python: é uma medida descritiva do produto, sem hipótese científica, só com as sementes dos testes (101, 202, 303, 404, 505).

- **Os dois mundos:** a v23 (a ilha com água de 64 × 30) e a v24 (a ilha grande). As duas têm a mesma luta e o mesmo cérebro; só o
  mundo muda.
- **Os dois cérebros:** o DigiBrain modular (o padrão dos ovos) e o A (a escolha em Ajustes).
- **O dono:** a cada 30 ticks, com o pet acordado, com fome abaixo de 0,6 e sem comida no chão, põe uma ração no lugar do cenário;
  limpa quando o pet está sujo e faz carinho a cada 5 passos. Cinco dias por vida.
- **Os cenários** são os três lugares que a tela de alimentar oferece (`lugaresNomeados`): o **comedouro**, **perto** (2 células do
  pet) e **longe** (20 células do pet).
- **O retorno** (só descritivo): depois de 2 dias comendo no comedouro, o dono solta o pet a 20, 40 e 70 células a leste do comedouro
  (70 só cabe na ilha grande), com fome e sem comida no chão, e mede se em um dia ele chega a 3 células do comedouro.

**O que se mede, por vida:** as rações postas e comidas; a fração comida em até 240 ticks; a mediana de ticks até comer; a fração dos
passos com fome abaixo de 0,2; a fome média; a distância andada por dia; as células distintas visitadas sobre as livres; o tempo de
máquina por dia de jogo (no Node desta máquina).

**A regra da leitura (fixada antes de ver os números):** para cada cérebro e cenário, compara-se a média das cinco sementes da v24 com a
da v23.

- O pet está **pior na ilha grande** se a fração comida em 240 ticks cai mais de 0,10 ou a fração de passos com fome abaixo de 0,2 sobe
  mais de 0,10.
- **Nenhum cenário pior:** a recomendação é não mexer na velocidade nem no cheiro.
- **Pior só no "longe":** a recomendação é rever o cheiro (o alcance de 24 células), não a velocidade.
- **Pior no comedouro ou no "perto":** a recomendação é rever a velocidade, e o número sai de uma segunda medida.
- **O retorno** decide só a memória: se o pet volta de 40 e não de 70 células, a recomendação é levar o alcance da memória (64 células)
  para a proporção do mapa novo.

São cinco sementes: a leitura é descritiva, sem intervalo de confiança, e a diferença de 0,10 é um corte prático. PROPOSTO, SEM FONTE.
O artefato é o `docs/pranchas/ilha-grande/medida_ig5.json`, gravado pelo `web/app/test/medir_ilha_grande.test.ts` com `MEDIR_IG5=1`.

### 12.14 IG5: o resultado da medida (2026-11-11)

Artefato: `docs/pranchas/ilha-grande/medida_ig5.json` (`MEDIR_IG5=1 npx vitest run test/medir_ilha_grande.test.ts`, no commit `a59685d2`,
sobre a `main` `ec6aa985`). Médias de cinco sementes, cinco dias por vida.

| Cérebro | Lugar da ração | Comida em 240 ticks: hoje → grande | Passos com fome baixa: hoje → grande | Pior pela regra? |
|---|---|---|---|---|
| modular | comedouro | 0,800 → 0,815 | 0,008 → 0,005 | não |
| modular | perto | 0,899 → 0,896 | 0,013 → 0,002 | não |
| modular | longe | 0,183 → 0,139 | 0,375 → 0,462 | não (a fome baixa sobe 0,087, perto do corte de 0,10) |
| A | comedouro | 0,437 → 0,324 | 0,450 → 0,555 | **sim** (cai 0,113 e sobe 0,105) |
| A | perto | 0,443 → 0,452 | 0,465 → 0,465 | não |
| A | longe | 0,067 → 0,000 | 0,825 → 0,855 | não (é ruim nos dois mundos) |

**O retorno** (o pet solto com fome a uma distância do comedouro, sem comida no chão; quantos de 5 chegam a 3 células dele em um dia):

| Cérebro | 20 células | 40 células | 70 células (só na ilha grande) |
|---|---|---|---|
| modular, hoje | 5 de 5 | 5 de 5 | não cabe |
| modular, grande | 5 de 5 | 5 de 5 | **1 de 5** (a menor distância média foi 43,5 células) |
| A, nos dois mundos | 0 de 5 | 0 de 5 | 0 de 5 |

**Outros números:** o modular anda o mesmo por dia nos dois mundos (107 a 123 células no de hoje, 113 a 128 na ilha grande) e visita
22 a 30 % das células livres do mundo de hoje contra 7 a 10 % da ilha grande: ele usa a mesma área em volta do lar, e o resto da ilha
fica sem visita. O tempo de máquina por dia de jogo, no Node desta máquina, foi de 29 a 50 ms no mundo de hoje e de 50 a 62 ms na ilha
grande com o modular.

**A leitura pela regra fixada no plano (12.13):**

- **A velocidade:** a regra dispara no cérebro A com a ração no comedouro. Com o modular, que é o cérebro dos ovos, nenhum cenário
  piora no comedouro nem no "perto".
- **O cheiro:** a regra não dispara ("pior só no longe" não aconteceu), mas o modular no "longe" ficou a 0,013 do corte na fome baixa.
- **A memória:** a regra dispara. O modular volta de 40 células e não de 70.

**Interpretação desta sessão sobre o cérebro A no comedouro (NÃO CONFIRMADA):** no layout da ilha grande o comedouro fica a 8 células
do ninho; no mundo de hoje, a 6, que é o raio da visão. A piora do A pode vir dessa distância, que é escolha do layout da IG1, e não
da velocidade: no "perto" (2 células do pet) o A fica igual nos dois mundos. Não foi medido com o comedouro a 6 células.

**Limites:** cinco sementes, sem intervalo de confiança; o corte de 0,10 é prático. O dono da medida não é um jogador de verdade. O
custo no celular de verdade continua sem medida.

### 12.15 IG-6: as decisões do Matheus e o adendo da medida (2026-11-11)

**Decidido pelo Matheus em 2026-11-11** (pergunta desta sessão, com a recomendação e o custo de errar):

- **A memória do modular:** "Sim, para 128 células (Recomendado)".
- **O comedouro a 6 células do ninho:** "Sim, junto com a memória (Recomendado)", com a medida da hipótese antes de mudar.
- **A velocidade e o cheiro:** não mexer (a recomendação; a regra do plano não disparou para o modular).

As duas mudanças são uma versão nova de pet, a fazer numa etapa própria (a IG6), com plano, paridade e a decisão sobre os pets v24 que
já existem.

**Adendo da medida, escrito antes de rodar** (exploratório, fora do plano da 12.13): a hipótese de que o cérebro A piora no comedouro
da ilha grande por causa da distância ao ninho. Um cenário a mais, `comedouro6`, só na ilha grande: a ração num ponto a 6 células a
leste do ninho, no lugar do comedouro (que fica a 8). Com os dois cérebros, as mesmas sementes e o mesmo dono. **A leitura:** a
hipótese se sustenta se, no A, a fração comida em 240 ticks do `comedouro6` voltar para perto da do mundo de hoje (0,437; a menos de
0,10) e a do modular não piorar mais de 0,10 contra o comedouro de hoje da ilha grande (0,815).
