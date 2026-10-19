# Mundo 3D: o mundo físico com câmera diagonal, sprites sobre corpos invisíveis e o contrato com o DigiBrain

Status: **INVESTIGAÇÃO FEITA; as decisões W-1 a W-7 DECIDIDAS pelo Matheus em 2026-10-18, pela recomendação** (seção 8). Escrito pelo
worker A, pela especificação WORLD-POC-001 do Matheus. Só investigação: nada no código mudou. **O POC-01a (a P3) avança em paralelo ao
Gate C**, pela `docs/TAREFA_V2_WORLD_POC_01.md` (o Matheus, 2026-10-19: a W-5 trata do cérebro de verdade no mundo novo, a P4). **O Gate A foi APROVADO pelo Matheus em 2026-10-19** (o POC-01a, #355 e #358), com duas ressalvas: só um celular, recente, foi medido (testar num Android mais simples quando houver), e o cérebro de verdade no mundo novo (a P4) continua esperando o Gate C. **O Gate B foi APROVADO pelo Matheus em 2026-10-19** (o POC-02, #362 e #363), com a ressalva de que foi com o cérebro de teste e só em TS (CP-7). **O mundo 3D fica PAUSADO até o Gate C:** a P4, o cérebro de verdade no mundo novo, espera o J5. Os números, os pesos e os nomes novos (fora das W) seguem PROPOSTOS. Nenhuma alegação de novidade.

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
- **A decisão (W-1, W-2 e W-5, DECIDIDAS em 2026-10-18, pela recomendação):**
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

## 5. Investigação E: o aprendizado pelas consequências e os experimentos

### 5.1 O que se registra a cada decisão

O registro já existe quase todo, no motivo (`_registrar`) e no `estado_interno`. O contrato acrescenta o que faltava:

| o quê | onde fica | para quem |
|---|---|---|
| o estado anterior | a Observação da decisão (o que o pet sentiu) e, à parte, o estado do motor (a verdade) | o cérebro: a Observação; a análise: os dois |
| a ação escolhida | a Intenção (a ação, o alvo e o `u` do sorteio), já no motivo | os dois |
| o resultado | a ação executada e o resultado físico, inteiros, no log; o `resultado` percebido na Observação seguinte | a análise: a verdade; o cérebro: o percebido |
| o estado posterior | a Observação seguinte e o estado do motor | igual ao anterior |
| as alterações fisiológicas | os receptores antes e depois, e o `sinal_corpo` por drive, já no motivo (`sinal_corpo.drives`) | os dois |
| a mudança de comportamento | **não se registra por decisão:** é medida depois, entre blocos de decisões e entre braços (5.3) | a análise |

**A separação que impede o falso aprendizado:** o cérebro aprende só do que sentiu. A análise mede com a verdade do motor. Nenhuma
métrica lê o que o cérebro "acha" que aconteceu.

### 5.2 Por que um roteiro não conta

Um comportamento conta como aprendido quando **muda com a experiência e não muda sem ela**. A especificação proíbe tomar uma sequência
roteirizada como evidência, e o projeto já tem as ferramentas para isso:
- **o prior do comportamento é zero:** o instinto não contém a escolha medida. Por exemplo, empurrar a bola quando o tédio está alto não
  tem peso no prior; a sonda "quem decidiu" (a E0, `docs/futuro/digibrain_v3_e0.md`) mostra se foi o aprendido que decidiu;
- **o braço sem sinal (P0, o instinto)** vive o mesmo mundo e as mesmas sementes;
- **o braço com o sinal embaralhado** recebe sinais do mesmo tamanho, permutados entre decisões. Se ele aprende igual, o que aprendeu não
  foi a consequência (SEM FONTE para este controle no projeto; ele é PROPOSTO aqui);
- **a reversão:** muda-se a consequência no meio da vida (a bola deixa de reduzir o tédio). O comportamento aprendido tem de desfazer-se,
  e o roteiro não se desfaz. O J5 já mede algo parecido com a G-REVAL.

### 5.3 Os experimentos (PROPOSTOS; cada um com tarefa e plano de análise próprios antes de rodar)

| experimento | a pergunta | os braços | a métrica | depende de |
|---|---|---|---|---|
| **EXP-1 a bola e o tédio** | o pet passa a empurrar a bola quando o tédio está alto, porque empurrar reduz o tédio? | P0, P1, P1 com o sinal embaralhado; mais a reversão no meio | a fração de decisões de `brincar` com a bola entre as decisões com o tédio acima de um limiar, no último terço menos no primeiro terço, por braço, com IC por bootstrap como nas runs da V2 | o empurrão no motor (o POC-01a, no motor) e o tédio da bola (já existe: `ConfigCorpo.tedio_bola`) |
| **EXP-2 a comida atrás da parede** | o pet passa a ir aonde costuma achar comida que não vê? | P0, P1, P1 com a memória de episódios (N6) | a fração de explorar que chega à comida escondida; o tempo até comer | a oclusão no motor (o cone) |
| **EXP-3 o obstáculo que custa** | o pet evita um caminho que gasta mais energia (a lama)? | P0, P1 | a escolha entre dois alvos iguais com custos diferentes | um terreno com custo no controlador |

**O que vem antes deles, sem o 3D:** o J1 já mostrou que o P1 perde do instinto no mundo 2D (#285) e que o alvo aprendido atrapalha
(#296). Antes do EXP-1, o P2 da especificação pede **uma mudança de comportamento demonstrada num ambiente controlado**. O EXP-1 pode
rodar inteiro no Python, no mundo 2D com o empurrão em inteiros, **sem nenhuma vista 3D**. A vista não muda a ciência no arranjo V.

**As regras de sempre:** as sementes de uma faixa reservada em `experiments/bancada/faixas.py`, a calibração separada da validação, a
validação uma vez só, e o resultado negativo registrado como está.

## 6. A persistência

- **Event sourcing, como hoje:** o log guarda os gestos do dono (com a posição inteira) e os avanços de tempo. A física inteira, o corpo e
  o cérebro se refazem pelo log, no Python e no TS.
- **Nada da vista entra no save:** nem a câmera, nem a interpolação, nem os quadros de animação.
- **O tamanho:** a física não acrescenta evento, porque o empurrão e a colisão são consequências e não entram no log. O log de 60 dias do
  v11 tem 294 KB (anexo 1). O replay de uma vida com física fica mais caro, e isso é a métrica M5 do POC.
- **No arranjo F,** o estado da engine (o snapshot do Rapier) teria de entrar no save, ou o replay teria de rodar a física inteira desde o
  nascimento, com a mesma versão da engine.

## 7. O roadmap reconciliado: P0–P9 da especificação × o roadmap da V2

**Sem roadmap paralelo:** cada fase P da especificação é lida como **um agrupamento dos marcos que já existem**:
- os J1 a J10 e as ideias da seção 8 de `docs/ROADMAP_V2.md`;
- o porte W;
- as fases G do `docs/futuro/ecossistema_genetico.md`.

Só a P3 é frente nova (este documento). A numeração P é a prioridade da especificação, não uma dependência linear; o J continua sendo o
nome do marco.

| fase | o que a especificação pede | os marcos que já existem | o estado (2026-10-18) | entrada | saída |
|---|---|---|---|---|---|
| **P0** consolidação do DigiBrain V2 | auditoria, contratos, testes, observabilidade, estabilidade | a rodada de saúde (`TAREFA_V2_SAUDE`); a E0 e o desenho V3 (`digibrain_v3_e0.md`); o porte W (#320 a #335); o connectome (#321); a infraestrutura multiagente (#326, aberto) | em andamento: o v11 no `Motor` (W, etapa 4, parte 3); as V3-1 a V3-8 abertas | — | o v11 jogável na web com o painel DigiBrain; as decisões V3 tomadas |
| **P1** fisiologia e metabolismo | alimentação, gasto, atividade, repouso | **J2** (o metabolismo ME-1 a ME-7, também no TS, #333); **J4** (o banheiro); **J10** (o dano, adiado) | código pronto; a calibração fecha só com o passo 0; **a validação do corpo não rodou** | P0 | a validação do corpo (34101…34505), que pede o sim do Matheus |
| **P2** aprendizado por consequências, sem o 3D | mudança de comportamento em ambiente controlado | **J3** (feito na pesquisa); **J1** (negativo: #285, #296); **J5** (a fruta ao lado, #334: o T1 com margem; a validação N = 50 espera o sim); o N3 | o candidato mais perto do **Gate C** é a validação do J5 do adendo 5 | P0, P1 | **um resultado positivo validado** (plano antes, validação uma vez) |
| **P3** mundo físico 3D | o WORLD-POC-01 | **novo** (este documento); a M-2 e as pranchas do mapa (rodada 16) | proposto | esta investigação aprovada; a W-1 decidida | o **Gate A** |
| **P4** percepção espacial e autonomia corporificada | sensores, navegação, intenções, consequências físicas | o mundo físico (J1) com o contrato da seção 4 no motor, Python e TS; os órgãos com lado (DP-13, DP-14); o proprioceptivo (ideia, `DEFINICOES_CORPO_V2.md` 8.1); os experimentos EXP-1 a EXP-3 | proposto | P0, P2, P3 | o **Gate B**; e, com o EXP-1 validado, um segundo **Gate C**, já corporificado |
| **P5** genoma e hereditariedade | variações herdáveis | **G0, G1** (`ecossistema_genetico.md`, EG-1 a EG-8 decididas); a fisiologia por espécie (FE-3 aberta) | ideia decidida, sem tarefa | o organismo estável (P1) | o **Gate D** (a h² do G1, com plano) |
| **P6** memória e conhecimento avançados | fichas, consolidação, esquecimento, generalização | o **N6** (`MemoriaEpisodios`); o `ModeloMundo` do **J5**; o Digicorpo do **J6** | o código do N6 e do J5 na `main`; o J6 nas etapas 0 a 2 | a memória e o aprendizado validados (P2) | um plano próprio |
| **P7** reprodução e desenvolvimento | transmissão, variação, desenvolvimento | **G2, G3** (o ovo no `Grupo`; o fatorial criação × seleção); a Vida (o relógio de desenvolvimento do J2) | depende de **dois pets aprendendo de verdade** (J7, inconclusivo por premissa) | P5, J7 | o **Gate E** |
| **P8** Semantic Thought Decoder | interpretar estados internos | `docs/futuro/decodificador_conceitos.md` (ideia, 2026-10-04); o connectome; o motivo de cada decisão | ideia | os motivos rastreáveis (P0) | um plano próprio |
| **P9** ecossistema e dispositivos | vários organismos, ecologia, smartwatch | **J7, J8, J9**; **G4**; **o smartwatch e o Vital Bracelet: Ausentes** (nenhum documento no repositório) | J7 degrau 1 no código; o resto, ideia | P2 a P7 | — |

**Os gates da especificação × o que o projeto já usa:**

| gate | a especificação | como fica aqui |
|---|---|---|
| **A** viabilidade técnica | a engine, o modelo visual, a física, a integração | o POC-01 aprovado pelos critérios do anexo 3, mais a decisão W-1 (onde mora a física). **APROVADO em 2026-10-19**, com as ressalvas de um celular só e do cérebro real esperando o Gate C |
| **B** organismo corporificado | percepção, decisão, navegação, consequências físicas e fisiológicas | uma demonstração técnica do contrato, sem hipótese: não é resultado de pesquisa. Pela CP-7 (2026-10-19), fecha no POC, em TS; a paridade do mundo com o Python fica para a entrada da P4. **APROVADO em 2026-10-19** (o POC-02, #362 e #363), com a ressalva de que foi com o cérebro de teste e só em TS |
| **C** aprendizado demonstrável | mudança comportamental mensurável pela experiência | **só com plano de análise antes e validação uma vez**, com o controle do sinal embaralhado (seção 5.2). Um resultado negativo também fecha o gate como "medido" |
| **D** variabilidade biológica | o genótipo dá diferenças fenotípicas | o G1 do `ecossistema_genetico.md` |
| **E** reprodução e desenvolvimento | herança, variação e desenvolvimento não roteirizados | o G2 e o G3 |

**O paralelismo:**
- a P3 (o POC e a vista) é toda web e não espera a P2;
- a P4 espera a P2, porque mais mundo sem um aprendiz que aprenda repete o J1;
- da P5 à P8 dá para preparar em paralelo, como a especificação permite.

**O risco principal do roadmap:** pôr a P3 e a P4 na frente da P2. O mundo fica mais bonito e o aprendizado continua não funcionando,
como o J1 e o J7 já mostraram.

**A linha das "ideias registradas" da seção 8 do `ROADMAP_V2.md`** (aplicada em 2026-10-18, com a W-7):

> | **o mundo 3D** (a vista do mundo físico em Three.js, a física em inteiros no motor, o contrato sensório-motor e o WORLD-POC-01) |
> investigação feita (WORLD-POC-001, 2026-10-18), W-1 a W-7 decididas; o POC-01a em paralelo ao Gate C (`TAREFA_V2_WORLD_POC_01`); a P4 depois do Gate C | J1, M-2, Gate C | `docs/futuro/mundo_3d.md` |

## 8. As decisões do Matheus (com a recomendação e o custo de errar)

**Todas DECIDIDAS em 2026-10-18, pela recomendação** (o Matheus, pelo coordenador).

| # | decisão | DECIDIDO | o custo de errar |
|---|---|---|---|
| W-1 | **onde mora a física:** V (no motor, em inteiros; a vista só desenha) ou F (a engine, o Rapier, como fonte da verdade) | **V**, a física no motor, em inteiros. Mantém a M-1, a seção 2.6 do `mundo_fisico.md`, o determinismo bit a bit e a pesquisa no Python | com V, se a pergunta de pesquisa um dia pedir corpos rígidos de verdade, a física inteira terá de crescer, ou se troca para F depois. Com F, a pesquisa do mundo sai do Python e toda versão da engine muda as vidas |
| W-2 | a engine de renderização | **Three.js**, imperativo, sem react-three-fiber, só como vista | trocar de renderizador custa a pasta da vista; o motor não muda (a vista só lê) |
| W-3 | o pet sabe a própria posição absoluta? (hoje sabe: `PercepcaoMundo.x`, `y` e o `ocorrido`) | **manter**, marcada como acesso privilegiado; trocar por um lugar integrado pelos passos só com uma pergunta que precise disso | mexer agora muda os gabaritos do mundo e o alvo `ponto` sem uma pergunta |
| W-4 | as paredes e os obstáculos | **atrás de chave desligada**, como mecânica nova; a M-1 ("sem áreas fechadas") fica valendo para o mapa de hoje | se entrarem sem chave, as vidas do mundo de hoje mudam |
| W-5 | a ordem P2 antes de P4 | **sim**: o Gate C (o J5 ou o EXP-1 no 2D) antes de pôr o cérebro no mundo novo (a P4). O POC-01a (a P3) não espera: avança em paralelo (o Matheus, 2026-10-19) | inverter repete o J1 num mundo mais caro |
| W-6 | a arte do POC | **o atlas do UP só local**, sem versionar, com um sprite de reserva | um POC que dependa de arte de terceiros não vira produto |
| W-7 | a localização destes documentos | **`docs/futuro/mundo_3d.md` com a pasta `docs/futuro/mundo_3d/`** (o precedente do connectome) e uma linha no `ROADMAP_V2.md` | baixo |

## 9. A próxima tarefa

1. **O POC-01a (a P3), em paralelo ao Gate C:** a `docs/TAREFA_V2_WORLD_POC_01.md` (2026-10-19), **entregue** (#355, #358). O
   **Gate A foi APROVADO** em 2026-10-19, com as duas ressalvas do status.
1b. **O Gate B no POC, ainda com o cérebro de teste:** a `docs/TAREFA_V2_WORLD_POC_02.md`, **entregue** (#362, #363). O **Gate B foi
   APROVADO** em 2026-10-19, com a ressalva de que foi com o cérebro de teste e só em TS. **Daqui em diante, o mundo 3D fica PAUSADO
   até o Gate C.**
2. **O Gate C** (W-5): a validação do J5 com a fruta ao lado, ou o EXP-1 no mundo 2D.
3. **Só depois do Gate C:** o cérebro de verdade no mundo novo (a P4), com tarefa própria.
4. A linha das "ideias registradas" da seção 8 do `ROADMAP_V2.md` e a linha do `PAINEL_V2.md` foram aplicadas com este documento.
