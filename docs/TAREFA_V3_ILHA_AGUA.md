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
