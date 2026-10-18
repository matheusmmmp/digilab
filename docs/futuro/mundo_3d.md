# Mundo 3D: o mundo físico com câmera diagonal, sprites sobre corpos invisíveis e o contrato com o DigiBrain

Status: **RASCUNHO, PROPOSTO** (2026-10-18, worker A, pela especificação WORLD-POC-001 do Matheus). Só investigação: nada no código
mudou, e nenhum PR foi aberto. O Matheus confirma a localização antes de qualquer PR. Números, pesos e nomes novos são PROPOSTOS.
Nenhuma alegação de novidade.

**Os anexos:**
- `docs/futuro/mundo_3d/auditoria.md`: o anexo 1, o estado real do repositório (investigação A);
- `docs/futuro/mundo_3d/tecnologias.md`: o anexo 2, as engines e a matriz (investigação B);
- `docs/futuro/mundo_3d/poc_01.md`: o anexo 3, o WORLD-POC-01. Vira `docs/TAREFA_V2_WORLD_POC_01.md` só se for aprovado.

**O que já existe e não se repete aqui:**
- **a vista:** `docs/futuro/mundo_fisico.md`, com a M-1 (o mapa 2D contínuo, DECIDIDO), a M-2 (a vista inclinada como a do Animal
  Crossing, DECIDIDA), a seção 2.5 (a percepção sem acesso privilegiado) e a seção 2.6 ("a vista é só desenho");
- **o protótipo da vista:** `docs/futuro/mundo_fisico_vistas.html`, com as pranchas `docs/estilo_up/pranchas/MapaDesktop.html` e
  `Mapa390.html`;
- **dois pets:** `docs/futuro/dois_pets.md` (os órgãos com lado e a `PercepcaoSocial`) e `docs/futuro/convivencia_mundo_fisico.md`.

## 1. Resumo

- **Hoje não existe mundo 3D, nem física, nem tela do mapa.** Existe um mundo 2D de posições inteiras, sem paredes, no Python e no TS,
  com paridade. A bola "rola" uma distância sorteada (anexo 1).
- **O requisito que decide** não é gráfico: é o **determinismo com paridade Python/TS**. Uma física de engine em float (Rapier, Havok)
  só é determinística entre aparelhos no JS, não com o Python (anexo 2, seção 2).
- **A recomendação (PROPOSTA):**
  - **Three.js como renderizador**, num canvas dentro do Preact;
  - **a física no motor, em inteiros:** paredes, colisão do círculo do pet, empurrão da bola com velocidade e atrito inteiros. A vista 3D
    continua sendo só desenho, como a M-2 manda;
  - **o Rapier como experimento contido** (o POC-01b);
  - **não ao Godot.**
- **O aprendizado no mundo físico ainda não funciona** (J1 negativo, #285 e #296). O mundo 3D não é o gargalo da pesquisa. O P2 da
  especificação (aprender por consequência sem o 3D) vem antes e pode ser feito no mundo 2D de hoje.

## 2. As peças e quem é dono de quê

```
                 PESQUISA (Python)                          JOGO (navegador)
  dono / bancada ──► motor (engine + mundo + corpo) ◄──── log ────► motor TS (paridade bit a bit)
                        │  ▲                                          │
             Observação │  │ Intenção                                 │ estado (só leitura)
                        ▼  │                                          ▼
                     DigiBrain (lobos)                       vista 3D (Three.js): câmera, sprites,
                                                             sombras, oclusão, interpolação
```

- **O motor é a fonte da verdade.** O mundo, o corpo, a física inteira e os sorteios moram nele. O DigiBrain só lê a Observação e só
  devolve a Intenção.
- **A vista só lê.** Ela desenha o estado do motor, interpolando entre ticks, e transforma um gesto na tela num evento do log (o
  `deixar_comida(tipo, x, y)` de hoje). Ela nunca escreve no estado.
- **O log é a persistência** (seção 7). A câmera, a interpolação e os quadros de animação não entram nele.

## 3. Investigação C: o modelo físico mínimo da criatura

Tudo em inteiros, nas **subunidades** do mapa de hoje (`ConfigMundo.sub` = 16 por célula). Os nomes e os números são PROPOSTOS.

| campo | representação | de onde vem hoje |
|---|---|---|
| posição | `(x, y)` inteiros no chão; altura `z` = 0 para o pet | `(x, y)` do `Mundo` |
| orientação | um setor de 16 (`direcao_em_16`) ou de 8 (`direcao_em_8`) | as funções já existem em `mundo.py`; hoje só o olfato usa a direção do último passo (a propriocepção, #308) |
| corpo de colisão | um **círculo de raio `r_pet`** no chão (PROPOSTO: 6 subunidades). Na vista, uma cápsula invisível de altura só visual | não existe: hoje o pet é um ponto |
| velocidade | `(vx, vy)` inteiros por tick, com `\|v\|` ≤ `velocidade` (4) | hoje é o `passo_ate` em linha reta, sem velocidade guardada |
| movimento | **cinemático**: o controlador escolhe a velocidade do tick por um caminho na grade de células (A* inteiro, para contornar as paredes); a colisão resolve o círculo contra os retângulos e **desliza** pela parede | não existe o caminho: hoje não há obstáculo |
| alcance de interação | um raio inteiro (`raio_pegar_celulas` × `sub`) a partir da borda do círculo | `raio_pegar_celulas` = 1 |
| estado de animação | **não fica no motor.** A vista o deriva do estado (a ação, a velocidade, o contato, dormindo) e do relógio da tela | — |
| sensores espaciais | a visão num **cone** com raio e ângulo, com oclusão por parede (um raio na grade, DDA ou Bresenham em inteiros); o **contato** (o pet bateu ou encostou, e em quê); o cheiro e o ouvido de hoje | a visão de hoje é um disco sem oclusão; não há contato |

**Os objetos**, no mesmo modelo:

| objeto | colisão | o que faz |
|---|---|---|
| parede | retângulo estático | bloqueia o pet, a bola e a visão |
| obstáculo | retângulo ou círculo estático | bloqueia o pet e a bola; a visão passa por cima de um obstáculo baixo (uma flag `alto`) |
| bola | círculo de raio `r_bola` | tem velocidade inteira; perde `atrito` por tick; **reflete** na parede trocando o sinal da componente normal, com uma restituição em fração inteira; o **empurrão** do pet lhe passa uma velocidade na direção do contato |
| comida | ponto, sem colisão | some ao ser consumida; apodrece como hoje |

**Por que cinemático, e não dinâmico:** o pet não precisa de massa nem de força para andar. O cérebro escolhe para onde, e o motor leva
(`mundo_fisico.md`, 2.1). Só a bola precisa de dinâmica, e uma dinâmica de um corpo com atrito e reflexão cabe em inteiros. Com isso, a
paridade bit a bit se mantém. Um motor de corpos rígidos (pilhas, rotação, atrito entre corpos) só vale a pena se houver uma pergunta
de pesquisa que dependa dele (a W-1, seção 8).

**O sprite sobre o corpo invisível (a vista, Three.js):**
- **billboard:** o `THREE.Sprite` sempre olha para a câmera e não faz sombra (anexo 2, 2.1). Com a câmera fixa na diagonal, o pet
  aparece sempre de frente. A sombra é um disco no chão, sob o centro do círculo, como no protótipo `mundo_fisico_vistas.html`;
- **sprites direcionais:** a direção do movimento pede quadros de lado (esquerda e direita espelhadas) ou de costas. **Não verificado:**
  quais direções o atlas do Digimon UP tem;
- **a ordem de profundidade:** com a câmera fixa, a ordem de desenho é o `y` do pé no chão (o mais perto da câmera por cima, como manda a
  M-2). O sprite transparente com corte de alfa escreve a profundidade e evita o problema da ordenação por transparência (conhecimento
  do modelo, não verificado; é a métrica M2 do POC);
- **a oclusão:** a parede que fica entre a câmera e o pet o esconde. A saída comum é desenhar o pet escondido como uma silhueta (uma
  segunda passada sem teste de profundidade) ou deixar a parede da frente semitransparente. **É só desenho:** a oclusão da visão do pet
  é a do motor, não a da câmera;
- **o pixel art:** filtro nearest, e o tamanho na tela em múltiplo inteiro do pixel do sprite, como o `PalcoPet` faz. Com a câmera
  ortográfica, o tamanho do sprite não varia com a distância; com perspectiva, varia, e o múltiplo inteiro se perde. **Recomendação
  PROPOSTA:** a câmera ortográfica inclinada.

## 4. Investigação D: o contrato sensório-motor

O fluxo da especificação, com quem calcula cada passo:

```
Mundo (motor) ─► Observação ─► DigiBrain ─► Intenção ─► Controlador (motor) ─► Mundo ─► Consequências
   estado          o que o        decide       o quê e      o caminho, os passos,    física     resultado físico percebido
   global          pet sente      a cada       sobre o      a colisão                inteira    + receptores do corpo
   (só o motor)    (relativo)     decisão      que viu                                          ─► registro p/ aprendizado
```

**A regra:** o DigiBrain não importa o motor, o mundo nem a engine. Ele recebe só a Observação e devolve só a Intenção. Isso já vale
hoje: a G-RECEPTOR (o cérebro só lê receptores e percepção) e o G-SEM-DIRECAO, que o teste `tests/test_cheiro_orgao.py` confere por AST.
O contrato abaixo **generaliza o de hoje, não o troca.**

### 4.1 As cinco coisas que a especificação manda separar

| # | o quê | quem produz | quem vê | hoje |
|---|---|---|---|---|
| 1 | **a Intenção** | o DigiBrain | o controlador | a `AcaoPet` e o `Alvo` escolhido entre os candidatos (`escolher_alvo`) |
| 2 | **a ação executada** | o controlador | o log e as métricas; o cérebro só a parte percebida | o `passo_ate`, o `ocorrido["de"]`, `["para"]` e `["deslocamento"]` |
| 3 | **o resultado físico** | a física do motor | o log e as métricas: a verdade inteira | o `ocorrido["chegou"]`, `["comeu"]` e `["brincou_com_bola"]`; a bola rolando |
| 4 | **a consequência fisiológica** | o corpo | o cérebro, **só pelos receptores** | a `PercepcaoCorpo` antes e depois, e o `sinal_corpo` (o `consequencia_corpo`) |
| 5 | **o registro para aprendizado** | o motor monta, o cérebro guarda | o cérebro | o `registro` da decisão (X, P, W) e o motivo; o `ocorrido` do gancho |

**O furo de hoje que o contrato fecha:** o `ocorrido` do `consequencia_mundo` (`digilab/mundo.py:1415`) leva ao cérebro as **posições
absolutas** `de`, `para` e `alvo.x`, `alvo.y`, e a `PercepcaoMundo` leva o `x`, `y` do próprio pet. O cérebro sabe onde está no mapa,
como se tivesse um GPS. A percepção dos objetos é relativa (`dx`, `dy`), mas a do próprio lugar não é. Dá para ler isso como um mapa
cognitivo, mas é acesso privilegiado. A W-3 (seção 8) decide se o contrato novo troca isso por um lugar que o pet integra pelos próprios
passos.

### 4.2 A Observação (o que o pet sente; PROPOSTA)

Toda distância e direção é **relativa ao pet** e já passou pelo sensor (o cone, a oclusão e o raio). Tudo em inteiros.

| campo | conteúdo | sensor | hoje |
|---|---|---|---|
| `vistos` | `(ref, categoria, distancia, setor)` de cada objeto visível, em ordem de distância, até `max_vistos`. O `ref` é um rótulo da percepção, válido enquanto o objeto é visto, e não o id do motor | o cone com oclusão | `vistos` (id, tipo, dx, dy, d) num disco, sem oclusão |
| `obstaculos` | a distância livre em cada um de 8 setores, até um raio curto (os "bigodes") | 8 raios inteiros | não existe |
| `contato` | `(categoria, setor)` do que encostou no círculo do pet desde a última decisão: uma parede, a bola, o outro pet | a colisão do motor | não existe; o toque dos dois pets é o mais perto disso |
| `resultado` | o que o pet percebeu da ação anterior: chegou, parou bloqueado, o alvo sumiu, a bola se afastou (e quanto), comeu | o controlador, filtrado pelo que o pet viu | o `ocorrido`, sem filtro |
| `corpo` | os receptores (`PercepcaoCorpo`), como hoje | os receptores | igual |
| `cheiro`, `sons` | os órgãos com lado, como hoje | as narinas e os ouvidos | igual |

### 4.3 A Intenção (o que o pet quer; PROPOSTA)

A Intenção é uma **sub-decisão das ações de hoje**: o `AcaoPet` não ganha membro, para não quebrar o replay da v1 (`mundo_fisico.md`,
2.1). As intenções da especificação, uma por uma:

| intenção | a ação de hoje | o alvo | o que o controlador faz |
|---|---|---|---|
| aproximar-se | `explorar` | um `ref` visto ou um setor | anda até o alcance de interação |
| investigar | `explorar` | um `ref` visto, ou um ponto lembrado | anda até ver de perto e para |
| tocar | `brincar` | o `ref` da bola ou do outro pet | anda até o contato e para |
| empurrar | `brincar` | o `ref` da bola | anda até o contato e continua, passando velocidade à bola |
| consumir | `comer` | o `ref` da comida | anda até o alcance e come |
| descansar | `dormir` ou `ocioso` | o ninho ou nenhum | anda até o ninho, ou fica |
| afastar-se | `explorar` | o setor oposto a um `ref` | anda para longe até uma distância |

A Intenção é discreta, e o cérebro escolhe entre candidatos que o motor oferece, como o `escolher_alvo` de hoje. O espaço contínuo não
aumenta o número de escolhas do cérebro.

### 4.4 O controlador (o motor)

- **A cada tick:** o caminho na grade (A* inteiro), a velocidade do tick, a colisão com deslize e o contato.
- **Para quando:** chegou, ficou bloqueado por N ticks, o alvo sumiu da vista, ou deu a hora da próxima decisão (`intervalo_decisao_ticks`
  = 15).
- **Devolve a ação executada** (a 2 da tabela 4.1) e o **resultado físico** (a 3). Os dois vão inteiros para o log e para as métricas;
  ao cérebro vai só a parte percebida (o campo `resultado`).

### 4.5 As frequências

| laço | frequência | onde |
|---|---|---|
| a vista | o quadro da tela (`requestAnimationFrame`), interpolando a posição entre dois ticks | navegador |
| a física | um tick (1 minuto de jogo), com `k` sub-passos inteiros se a bola rápida atravessar a parede (PROPOSTO: `k` = 4) | motor, Python e TS |
| o corpo | um tick, como hoje | motor |
| o DigiBrain | uma decisão a cada 15 ticks, como hoje; o controlador executa a Intenção nesses 15 | motor |

### 4.6 O determinismo, e o que uma engine de física faz com ele

- **No arranjo V (recomendado):** a física é a do motor, em inteiros, então a paridade Python/TS é bit a bit como hoje. Os testes de
  hoje servem de modelo (`web/app/test/mundo.test.ts`, os gabaritos do mundo). A vista não entra no log.
- **No arranjo F (o Rapier como fonte da verdade):**
  - o Rapier JS é determinístico entre aparelhos com a mesma versão e a mesma ordem de criação (anexo 2), mas é float, e o Python não o
    tem;
  - a pesquisa do mundo teria de rodar no Node, e com isso o método muda: a bancada, as sementes e as métricas, hoje no Python;
  - **toda troca de versão do Rapier muda as vidas**, e os gabaritos teriam de levar a versão junto;
  - os `Math.sin` e `Math.cos` que entrarem na física também saem do determinismo, como a página do Rapier avisa.
- **Em qualquer arranjo:** a câmera, a interpolação e a animação ficam fora do log e não mexem na simulação.
