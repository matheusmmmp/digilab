# Dois pets de verdade no mesmo mundo: o desenho

Status (2026-10-07):
- **DECIDIDO pelo Matheus:** dois pets de verdade no mesmo mundo, e não um pet sintético informante. A decisão substitui o primeiro passo
  recomendado em `docs/futuro/convivencia_mundo_fisico.md` (CV-1) e na `docs/futuro/cognicao_social.md` (seção 11).
- **PROPOSTO:** o resto deste documento. As decisões abertas estão na seção 14, cada uma com recomendação e custo de errar.

A tarefa é `docs/TAREFA_V2_DOIS_PETS.md`. Um plano de análise vem depois, antes de qualquer run.

**Parte de:**
- `docs/futuro/cognicao_social.md`: a escada (seção 1), o experimento mínimo (2), o modelo dos outros (3) e as seções 5 a 10;
- `docs/futuro/convivencia_mundo_fisico.md`: o que falta no motor (seção 2) e a escada no mapa (seção 3);
- `docs/TAREFA_V2_MUNDO_FISICO.md` e o `MotorMundo` da `main` (`digilab/mundo.py`), com o instinto do mundo, os cérebros, o corpo, a bancada
  e o motor em TypeScript;
- `docs/futuro/ego_existencia.md`: a etapa 7, o ego social, depende desta frente;
- E-3: o cérebro do projeto é o A.

**O que este documento não faz:**
- não escreve rótulo à mão para nenhum degrau: seguir, dividir, enganar, amigo e reputação só valem como medida com critério definido
  antes (`cognicao_social.md`, seção 10);
- não faz alegação de novidade;
- não autoriza run.

## 1. O que muda, em uma frase por camada

| camada | hoje | com dois pets |
|---|---|---|
| **motor** | um `MotorMundo` por vida, dono do mundo | um motor por pet, como hoje, sobre um **mundo compartilhado** (seção 2) |
| **ordem** | um pet só, sem conflito | a vez de cada pet na decisão sorteada num fluxo do mundo (seção 3) |
| **registro** | um log por vida | **um registro do grupo**, com o destino de cada evento (seção 4) |
| **percepção** | o mapa, os objetos a até 6 células e o cheiro | mais **o outro à vista**: posição, ação visível e onde ele comeu (seção 5) |
| **interação** | nenhuma | **disputa pela comida** (quem pega primeiro) e **observação** (seção 6) |
| **cérebro A** | o alvo padrão do motor | **alvo aprendido** e entradas sociais nas regras de tempo livre (seção 8) |
| **dono** | um dono, um orçamento | **um dono com orçamento por pet** (seção 9) |
| **bancada** | uma vida por célula | um **grupo** por célula, com o pet sozinho como referência (seção 11) |

## 2. O motor de N pets

**A proposta: dois motores sobre um mundo compartilhado (DP-1).**
- **Cada pet continua com o próprio motor:** a mesma cadeia de hoje (`MotorMundo`, com o `MotorCorpo` por cima quando ligado), o próprio
  `Estado`, a própria rng de ambiente e de política (`engine.py` não muda) e o próprio cérebro.
- **O mundo sai do motor e vira um componente** (`Mundo`): as árvores, as comidas, a bola, os fluxos do mundo e os registros do mundo. É a
  forma que o motor em TypeScript já tem (`web/app/motor/mundo.ts`: o mundo recebe o estado do pet e devolve o estado depois).
  - **Com um pet,** o `MotorMundo` é dono do próprio `Mundo`: é a vida de hoje, byte a byte (G2).
  - **Com dois,** os dois motores apontam para o mesmo `Mundo`.
- **Um orquestrador** (`Grupo`) avança os motores no mesmo relógio, um tick por vez. Ele não decide nada: só chama cada motor na vez sorteada
  (seção 3) e grava o registro do grupo (seção 4).

**A atualização do mundo é uma vez por tick.** Hoje o `MotorMundo` atualiza o mundo (quedas, apodrecer, sumir) na decisão do pet. Com dois
pets, quem decide primeiro no tick dispara a atualização, e ela não roda de novo no mesmo tick. O resultado não depende de quem chegou
primeiro: a atualização só lê o tick e o fluxo `mundo-arvores`.

**As rngs, por pet e por fluxo.** Trocar o cérebro de um pet não pode mudar nenhum sorteio do outro nem do mundo.

| fluxo | de quem | semente | depende do comportamento? |
|---|---|---|---|
| ambiente e política do engine | do pet | a semente do pet | só do próprio pet |
| `alvo` | do pet | `derivar_semente("alvo", semente do pet)` | não: sorteado sempre nas três ações com alvo |
| `mundo-sujeira` | do pet | `derivar_semente("mundo-sujeira", semente do pet)` | só de quando ele come ração |
| `dono-lugar` | do dono de cada pet | `derivar_semente("dono-lugar", semente do pet, rótulo do dono)` | não |
| `mundo-arvores` | do mundo | a semente do mundo | **não** (G-NUMS) |
| `mundo-bola` | do mundo | a semente do mundo | sim: rola quando alguém brinca |
| **`mundo-ordem`** (novo) | do mundo | `derivar_semente("mundo-ordem", semente do mundo)` | **não:** um sorteio por tick com duas ou mais decisões, qualquer que seja o cérebro |

**As sementes do grupo.**
- a semente do mundo é a semente do grupo, s;
- o pet A usa s, então **o pet A sozinho no mesmo mapa é a vida de hoje de semente s**. É a referência natural;
- o pet B usa `derivar_semente("segundo-pet", s)`.

**O que não se separa.** O mundo de um pet muda pelo que o outro faz fisicamente: a fruta que o outro comeu some, e a bola que o outro chutou
rola. É a interação, não um vazamento de rng. O teste G-NUMS-GRUPO (seção 10) confere que tudo o mais fica igual.

## 3. A ordem dentro do tick

Os dois pets nascem no mesmo tick e decidem nos mesmos ticks (a cada 15). Se os dois querem a mesma fruta na mesma decisão, alguém come
primeiro.

**A proposta: a vez sorteada no fluxo `mundo-ordem` (DP-2).**
- Em cada tick em que dois ou mais pets decidem, o mundo sorteia a ordem.
- O primeiro age inteiro: decide, anda e come. O segundo percebe o mundo como ficou e age depois.
- Se a fruta que o segundo queria já sumiu, ele chega e não acha: é o "comer sem comida" de hoje (MF-2).
- **A ordem nunca é a ordem em que o código chama os pets.** Os pets ficam numa lista ordenada pelo identificador, e o sorteio escolhe
  dessa lista.
- **Com um pet,** não há sorteio, e o fluxo nem é criado. A vida de hoje não muda.

**Por que não "quem está mais perto".** Seria preciso conhecer o alvo dos dois antes de agir, o que pede decidir em duas fases. O engine faz
decidir, aplicar e observar numa só chamada, e o `engine.py` não muda. Duas fases mudariam o laço do `MotorMundo` e a ordem de hoje entre a
consequência e o tick.

**O custo declarado.** Com o sorteio, ser o primeiro é sorte, e não velocidade. Numa disputa, o mais perto pode perder. Isso fica medido (a
fração das disputas que o primeiro ganhou e a distância de cada um) e não vira regra.

## 4. O registro (event sourcing)

**A proposta: um registro do grupo (DP-3).**
- **O cabeçalho** diz a composição do grupo: as sementes, o cérebro e o dono de cada pet, a semente do mundo e o tick em que cada pet entrou.
  Um pet pode entrar depois: o "experiente" da seção 11 vive dias sozinho antes de o outro chegar.
- **Os eventos** são os de hoje (o avanço do tempo e as ações e gestos do dono), cada um com o **destino**: `mundo` (o `deixar_comida`, o
  `deixar_bola`) ou `pet:<id>` (o limpar, o acariciar, o tapa). O avanço é um só, do grupo.
- **O replay** é o `reproduzir_grupo`: refaz o grupo do cabeçalho e rejoga os eventos no mesmo relógio, com a mesma ordem sorteada. O G1 do
  grupo confere bit a bit.
- **A projeção:** o registro do grupo com um pet só, sem o destino, é o log de hoje evento a evento. É o que liga o G2 ao registro.

**O que não entra no registro:** o que um pet faz, vê ou diz ao outro. Tudo isso sai do replay, como hoje sai a ação do pet. Só as causas
de fora entram.

## 5. A percepção do outro

Um campo novo e opcional, `Observacao.social` (`PercepcaoSocial | None = None`), como o `mundo` e o `corpo` entraram. Sem o grupo, ele fica
`None`, e nenhum cérebro de hoje o lê.

| campo | o que é |
|---|---|
| `outros` | os pets a até `raio_visao` (as 6 células do mundo): `(id, dx, dy, d, acao_visivel)`, com a posição relativa, em ordem de `d` e de id |
| `acao_visivel` | a ação que o outro escolheu na última decisão (comer, brincar, dormir, explorar, ocioso, chamar, emburrar). É o que se vê de fora |
| `onde_comeu` | o último ponto em que este pet **viu** o outro comer (dentro do raio, no momento do consumo), com há quanto tempo. Nada, se nunca viu |

**O que fica de fora** (G-RECEPTOR-SOCIAL):
- o estado interno do outro: drives, receptores, pesos, memória e o alvo que ele escolheu;
- **o que o outro comeu e não foi visto** e o efeito da fruta no corpo dele;
- **o cheiro do outro:** fica para o degrau 3, com a solidão (CV-5).

O pet sabe **onde** o outro comeu e **o que** ele estava fazendo, porque viu. Não sabe se fez bem a ele.

## 6. A interação mínima: os degraus 1 e 2

**O degrau 1, sem sinal: competir e observar.**
- **Competir:** a comida no chão é uma só para os dois. Quem pega primeiro come (seção 3), e não há agressão entre pets (CV-3).
- **Observar:** ver o outro comer e ir lá. O mundo oferece, no explorar, dois candidatos a alvo a mais:
  - `seguir`: ir até onde o outro está, se visto;
  - `onde_comeu`: ir ao último ponto em que se viu o outro comer.
- **O padrão do motor e o instinto nunca escolhem esses candidatos.** Se o pet vai lá, é porque o cérebro aprendeu a ir (seção 8). Não há
  regra escrita de imitação.

**Aprender observando (5.2) já é o primeiro degrau medível, e é mais barato que a comunicação (DP-5).**
- **O mais barato:** não pede ação nova, evento novo nem vocabulário; só a percepção da seção 5 e os dois candidatos.
- **O mensurável:** a pergunta "B aprende algo que só A viveu?" já tem resposta no degrau 1 (seção 11).
- **O que o separa da comunicação:** a observação passa pelo que o outro **faz**, e a mensagem pelo que ele **diz**. O degrau 2 só entra
  quando o 1 tiver resposta.

**O degrau 2, comunicação (só depois do 1; DP-6).**
- **Como entra:** como **sub-decisão do `chamar_atencao`**, sem membro novo no `AcaoPet`. O alvo é o outro pet; o conteúdo é do vocabulário
  fechado (`COMIDA(lugar)`, com o lugar no conjunto de pontos que o pet conhece). O motor entrega a mensagem na percepção do outro, com o
  autor.
- **Na v1,** o `chamar_atencao` é a ação de pedir ao dono, e a reprodução da v1 não muda: a sub-decisão só existe com o grupo e um outro à
  vista.
- **A mensagem não entra no registro:** é saída do pet, refeita pelo replay.
- **A LLM fica fora da decisão** (`cognicao_social.md`, seção 10). Se entrar, só fala.
- O engano operacional (crença ≠ mensagem) é só medida, nunca regra (`cognicao_social.md`, seção 2).

## 7. O que é herdado, vivido e aprendido de outros

| origem | o que é | onde está no código |
|---|---|---|
| **herdado** | o instinto e o prior: as regras, os pesos de partida, o genoma | `PoliticaInstintoMundo`, o prior dos lobos, o genoma das frutas |
| **vivido** | o que a consequência da própria ação ensinou | o sinal do P1 (corpo ou N3), creditado à decisão do próprio pet |
| **aprendido de outros** | a mudança no pet que vem de experiências que a percepção do outro guiou | **não é um canal à parte:** a percepção social só oferece possibilidade (os candidatos) e evidência (as entradas). Quem atualiza o valor é a consequência da própria tentativa |

**A regra que atravessa tudo** (`cognicao_social.md`, seção 5): relato e observação oferecem possibilidade e evidência; só a consequência
da própria ação atualiza o valor.
- **Nenhum sinal de reforço sai do outro pet.** Vê-lo comer não credita nada.
- **Nenhum parâmetro passa de um pet ao outro** (5.3). Os dois cérebros nunca se leem.

**Como se mede a fronteira:** o "aprendido de outros" é a diferença entre o B com um companheiro **informativo** e o B com um companheiro
**de presença igual e informação sem valor** (seção 11). O herdado e o vivido são iguais nos dois braços; o que sobra é do outro.

## 8. O modelo dos outros no cérebro A (DP-8)

**No degrau 1, o mínimo para aprender observando:**
- **o alvo aprendido:** hoje o `escolher_alvo` do A devolve `None`, e vale o padrão do motor. Com o grupo, ele passa a escolher entre as
  **classes** de candidato (`cheiro`, `vagar`, `casa`, `continuar`, `seguir`, `onde_comeu`), com um peso por classe e por regra:
  - **o prior** é o padrão do motor (as classes que o padrão usaria) com um peso pequeno nas outras (PROPOSTO, SEM FONTE). É o herdado: sem
    ele, o pet nunca tentaria `seguir`;
  - **o aprendizado** é pela consequência da decisão, pela regra de sempre do cérebro (a da L1);
  - era o "alvo aprendido" de adendo que o plano do mundo deixou para depois (seção 3 dele);
- **as entradas sociais:** "outro à vista", "viu o outro comer" (recente) e a ação visível do outro, nas regras de tempo livre, com prior 0
  (no prior, a vida de hoje).

**O modelo dos outros fica registrado, e não decide, até o degrau 3.** Por pet conhecido, três variáveis separadas
(`cognicao_social.md`, seção 3):

| variável | o que guarda | a evidência |
|---|---|---|
| **familiaridade** | quanto tempo o outro esteve à vista, com decaimento | direta |
| **confiança, por atividade** | na comida: a fração das idas a `onde_comeu` dele que acharam comida boa | direta. A indireta (o que outro contou) só existe no degrau 2 |
| **afinidade** | o saldo dos encontros: comida que os dois dividiram (comeram perto, sem disputa) contra comida perdida para ele | direta |

- **Reputação ≠ relacionamento:** confiança e afinidade nunca se somam.
- **Nenhuma variável tem rótulo** ("amigo", "rival"). O que se lê é o número e o critério.
- **No degrau 3,** elas entram na decisão por adendo, com plano próprio.

**Os cérebros B e C:** opcionais, como no corpo. A interface é a mesma: `obs.social`, o `escolher_alvo` e a consequência.

## 9. O dono (DP-7)

**A proposta: um dono com orçamento por pet.**
- **O dono** é o mesmo dono sintético (por exemplo, o atencioso), com **um orçamento de 16 interações por dia para cada pet** e a rng
  própria de cada pet (`dono`, `dono-lugar`, com o rótulo do pet).
- **O cuidado dirigido** (limpar, acariciar) vai ao pet do orçamento.
- **A comida** sai do orçamento do pet para quem o dono a solta, e cai no **mapa compartilhado**. O outro pode comer: é a competição. Onde
  o dono a solta (perto de quem, no comedouro) já é a variável do cuidado do mundo físico (PMF-4).
- **Por quê:** é o jogo (CV-2: dois pets do mesmo jogador), e o orçamento por pet impede que um pet ganhe cuidado só por ter companhia.

**Donos diferentes por pet** fica como alternativa: separa melhor o dono do companheiro, mas não é o caso do produto e dobra as células.

## 10. Os gates

| gate | o que confere |
|---|---|
| **G2** | **chave do grupo desligada, ou um pet só no grupo** = as vidas de hoje byte a byte: o mundo físico com e sem o corpo, contra os gabaritos de hoje (`mundo_vidas_de_hoje.json`, `corpo_mundo_vidas_de_hoje.json`) e um gabarito novo, gravado antes da extração do `Mundo` |
| **G1-GRUPO** | o grupo inteiro, rejogado do registro, dá os mesmos estados, posições, objetos, ordens sorteadas e estados internos, bit a bit |
| **G-ORDEM** | trocar a ordem em que o código guarda os motores não muda nada |
| **G-NUMS-GRUPO** | trocar o cérebro de B não muda as rngs de A, as quedas, a ordem sorteada nem os sorteios do dono de A. Só muda o que passa pela interação física (a fruta que sumiu, a bola que rolou), e cada diferença do A é explicada por um evento do B |
| **G-RECEPTOR-SOCIAL** | nenhum cérebro importa o motor nem o mundo; a `PercepcaoSocial` não tem campo de estado interno; mudar o estado interno do outro sem mudar o que ele faz não muda a percepção |
| **G-MEC-SOCIAL** | a disputa (o primeiro come, o segundo não acha), o `onde_comeu` só com o consumo à vista, os candidatos sociais só no explorar com o outro visto, o padrão do motor nunca os escolhendo |
| **G-PAR** | o grupo em TypeScript, com os mesmos números, quando o produto voltar (o v11 está pausado) |
| **G-ENGINE** | `engine.py` com o sha256 de sempre |

## 11. A medida do primeiro degrau (para o plano de análise)

**A pergunta:** o B aprende algo que só o A viveu?

**O desenho que o plano vai detalhar:**
- **O mundo:** o físico, com o efeito da fruta **por árvore** (as árvores de um tipo fazem mal). O A só sabe isso porque comeu lá.
- **O A experiente:** vive K dias sozinho (PROPOSTO, o plano fixa), aprende pela consequência a evitar as árvores ruins, e o B nasce no dia
  K.
- **Os braços do B** (todos P1, com o mesmo dono e as mesmas sementes):

  | braço | o companheiro | para quê |
  |---|---|---|
  | **B só** | nenhum | a referência: o mesmo mapa e as mesmas sementes |
  | **B + A informativo** | o A que viveu os K dias no mapa com o efeito verdadeiro | o braço que pode transmitir |
  | **B + A embaralhado** | o A que viveu os K dias com o efeito **desarranjado** entre os tipos de árvore (como o ME do N6). No dia K o mundo passa ao efeito verdadeiro para os dois | **o acoplado no estilo P2a:** a mesma presença, a mesma competência e a mesma disputa, com informação sem valor para o mundo do B |
  | **B + A ingênuo** | um A recém-nascido (P0) | a presença sem experiência nenhuma |

- **A medida:** a taxa de fruta ruim do B (ou o dia até evitá-la) nos dias depois de K, e a fração das idas do B a `onde_comeu`.
- **O contraste primário:** B + informativo contra B + embaralhado. A diferença é o que o B aprendeu do que o A viveu, com a presença e a
  disputa iguais.
- **O B só e o B + ingênuo** separam "ter companhia" de "ter companhia que sabe".

**O controle segue a regra do projeto:** nenhum braço de malha aberta contra malha fechada. Todos os B vivem com o mesmo dono reagindo.

## 12. A ordem com o resto (DP-10)

| peça | espera o quê | pode correr em paralelo com |
|---|---|---|
| extrair o `Mundo` do `MotorMundo` (A) | nada; o G2 com os gabaritos de hoje | o corpo, etapas 6 a 8 |
| o `Grupo`, a ordem, o registro (A) | a extração | o corpo |
| a percepção social e os candidatos (A) | o `Grupo` | o corpo |
| o alvo aprendido e as entradas sociais no A (B) | a etapa 6 do corpo (o B está nela) e a percepção social | a bancada do corpo (D) |
| a bancada do grupo (D) | o cérebro | — |
| o plano de análise (C) | o desenho e a tarefa | tudo; commitado antes de qualquer run |
| as runs | a validação do mundo físico (a referência do pet só) e o plano | — |
| o grupo em TypeScript (A) | o produto voltar (o v11 está pausado) | — |
| a solidão e a aglomeração no corpo (degrau 3, CV-5) | o degrau 1 ter resposta | — |
| o ego social (`ego_existencia.md`, etapa 7) | esta frente e a rede de si | — |

## 13. Riscos

| # | risco | o que o desenho faz |
|---|---|---|
| R-1 | **Escopo:** é a primeira mudança que tira o motor de "um pet e um dono" | o mundo vira componente com o G2 de um pet só, antes de qualquer coisa de grupo |
| R-2 | **Determinismo:** muitas ordens possíveis no mesmo tick | a ordem é um sorteio de um fluxo do mundo, nunca a ordem do código (G-ORDEM) |
| R-3 | **O cérebro A não escolhe alvo hoje** | o alvo aprendido entra com o B (seção 8). Sem ele, o A nunca segue ninguém, e o degrau 1 não tem o que medir |
| R-4 | **O prior dos candidatos sociais:** um peso pequeno nas classes que o padrão não usa é escolha nossa | é o herdado declarado, PROPOSTO, SEM FONTE, igual nos braços; o contraste primário o cancela |
| R-5 | **Rótulos:** "seguiu", "dividiu", "amigo" | só como medida com critério definido antes, no plano |
| R-6 | **Agressão** | fica fora (CV-3). A disputa é só quem pega primeiro |
| R-7 | **O custo das runs:** um grupo é ao menos duas vidas, e o A experiente vive K dias a mais | o plano mede o custo no piloto e diz o teto |
| R-8 | **A sorte da ordem pesa na disputa** | a ordem é medida (seção 3); o contraste primário tem a mesma distribuição de ordens nos dois braços |

**Literatura.** Nenhuma referência sustenta este desenho: ele é de engenharia. As referências da `cognicao_social.md` (seção 9) e da
`convivencia_mundo_fisico.md` (seção 7) que estão como **pista** continuam pista e não são citadas pelo conteúdo. Não há alegação de
novidade: aprendizado social, forrageio em grupo e comunicação entre agentes artificiais já estão publicados.

## 14. Decisões do Matheus

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| DP-1 | O motor de N pets | **um motor por pet sobre um `Mundo` compartilhado**, com um orquestrador. É a forma do TS, e o `engine.py` não muda | um motor com dois pets: refaz o laço do engine (congelado) e perde o pet de hoje como caso particular |
| DP-2 | A ordem no tick | **a vez sorteada no fluxo `mundo-ordem`**, só com dois ou mais pets decidindo | "quem está mais perto": decidir em duas fases muda o laço e a ordem de hoje. Alternância fixa: viés sistemático para um dos pets |
| DP-3 | O registro | **um registro do grupo**, com o destino de cada evento e o cabeçalho da composição | um log por pet mais o do mundo: o replay junta três arquivos, e a ordem entre eles vira mais uma fonte de erro |
| DP-4 | A percepção do outro | **posição, ação visível e onde o viu comer**, dentro do raio de visão; sem cheiro do outro no degrau 1 | dar o estado interno ou o efeito no corpo do outro: acesso privilegiado, e o "aprendido de outros" vira leitura de memória |
| DP-5 | O primeiro degrau | **aprender observando**, antes de qualquer mensagem | começar pela comunicação: pede ação, vocabulário e evento, sem saber se a observação já bastava |
| DP-6 | A comunicação, quando entrar | **sub-decisão do `chamar_atencao`** com o outro como alvo e vocabulário fechado, sem membro no `AcaoPet` | uma ação nova: quebra a reprodução da v1 e muda o enum que a web lê |
| DP-7 | O dono | **um dono com orçamento por pet**, rng por pet, comida no mapa compartilhado | donos diferentes: dobra as células e não é o jogo. Orçamento único: o pet com companhia perde cuidado |
| DP-8 | O cérebro A no degrau 1 | **alvo aprendido e entradas sociais**; o modelo dos outros (familiaridade, confiança por atividade, afinidade) só registrado até o degrau 3 | o modelo dos outros decidindo já: mais pesos livres antes de saber se a observação funciona |
| DP-9 | O controle do primeiro degrau | **o A embaralhado** (mesma presença, informação sem valor), mais o B só e o B com um A ingênuo | só o B só: confunde "aprendeu do outro" com "teve companhia" |
| DP-10 | A ordem com o resto | **o motor (A) em paralelo com o corpo; o cérebro (B) depois da etapa 6 do corpo; a bancada (D) depois; as runs depois da validação do mundo físico e do plano** | esperar o corpo inteiro: atrasa sem motivo. Rodar antes da validação do mundo físico: o B só fica sem referência |
