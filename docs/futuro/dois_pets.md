# Dois pets de verdade no mesmo mundo: o desenho

Status (2026-10-07):
- **DECIDIDO pelo Matheus:** dois pets de verdade no mesmo mundo, e não um pet sintético informante. A decisão substitui o primeiro passo
  recomendado em `docs/futuro/convivencia_mundo_fisico.md` (CV-1) e na `docs/futuro/cognicao_social.md` (seção 11).
- **DP-1 a DP-10 DECIDIDAS pelo Matheus em 2026-10-07** (seção 14): oito pela recomendação; a DP-4 (os sentidos) e a DP-7 (os donos)
  com mudança. A DP-11 e a DP-12, que saem da DP-4, foram DECIDIDAS pela recomendação em 2026-10-07.
- **PROPOSTO:** o como, neste documento.

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
| **percepção** | o mapa, os objetos a até 6 células e o cheiro | mais **os sentidos sobre o outro**: visão e toque no degrau 1, audição e cheiro depois (seção 5) |
| **interação** | nenhuma | **disputa pela comida** (quem pega primeiro) e **observação** (seção 6) |
| **cérebro A** | o alvo padrão do motor | **alvo aprendido** e entradas sociais nas regras de tempo livre (seção 8) |
| **dono** | um dono, um orçamento | **um dono com orçamento por pet** na validação inicial; **um dono por pet** como objetivo (seção 9) |
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
- **O cabeçalho** diz a composição do grupo: as sementes, o cérebro e o dono de cada pet (um dono para os dois ou um por pet, DP-7), a semente do mundo e o tick em que cada pet entrou.
  Um pet pode entrar depois: o "experiente" da seção 11 vive dias sozinho antes de o outro chegar.
- **Os eventos** são os de hoje (o avanço do tempo e as ações e gestos do dono), cada um com o **destino**: `mundo` (o `deixar_comida`, o
  `deixar_bola`) ou `pet:<id>` (o limpar, o acariciar, o tapa). Com dois donos, também a **origem** (`dono:<id>`). O avanço é um só, do
  grupo.
- **O replay** é o `reproduzir_grupo`: refaz o grupo do cabeçalho e rejoga os eventos no mesmo relógio, com a mesma ordem sorteada. O G1 do
  grupo confere bit a bit.
- **A projeção:** o registro do grupo com um pet só, sem o destino, é o log de hoje evento a evento. É o que liga o G2 ao registro.

**O que não entra no registro:** o que um pet faz, vê, ouve, cheira, toca ou diz ao outro. Tudo isso sai do replay, como hoje sai a ação do pet. Só as causas
de fora entram.

## 5. Os sentidos sobre o outro (DP-4, DECIDIDA com mudança)

**A decisão do Matheus (2026-10-07):** o pet tem sentidos sobre o outro pet, como **toque, cheiro e audição**, além da visão.

**A regra que vale para os quatro:**
- **Nenhum acesso ao estado interno do outro.** Os sentidos só leem o que é **físico** (posição, contato, o som de uma ação) ou o que o
  corpo do outro **emite** por um emissor declarado no grafo do corpo (`docs/TAREFA_V2_CORPO_DRIVES.md`, seção 18).
- **Cada sentido entra como receptor** no campo novo e opcional `Observacao.social` (`PercepcaoSocial | None = None`), como o `mundo` e o
  `corpo` entraram.
- **Sem o grupo, ou com um pet só,** o campo é `None`, e o mundo não guarda nada dos sentidos (nem rastro, nem som). É a vida de hoje,
  byte a byte (G2).

**Quando cada sentido entra** (DP-11 e DP-12, DECIDIDAS pela recomendação, seção 14; os números novos são PROPOSTOS, SEM FONTE):

| sentido | o que lê | entra | por quê |
|---|---|---|---|
| **visão** | posição, ação visível, onde o outro comeu | **degrau 1** | é o canal da observação (DP-5) |
| **toque** | o contato na mesma célula ou na vizinha | **degrau 1** | o contato já acontece na disputa pela comida: é físico e sai de graça do mundo |
| **audição** | os sons das ações e o chamado, com direção e distância | **degrau 1b**, depois de o 1 ter resposta | ouvir o outro comer fora da vista é um canal de informação a mais. Entrando depois, o quanto ele acrescenta é medido sozinho |
| **cheiro** (rastro e cheiro próprio) | a intensidade e a direção do cheiro do outro e do rastro que ele deixou | **degrau 1b**, junto com a audição | o rastro é outro canal de "onde o outro foi" (deixar marca no mundo), e misturá-lo à visão no degrau 1 tira a leitura de qual canal ensinou |
| **cheiro de estado** (estresse, medo) | um cheiro que o corpo do outro emite conforme um químico dele | **degrau 3**, com a solidão e a aglomeração (CV-5) | abre um canal emocional entre corpos, e o grafo do corpo passa a ter laço entre dois pets (seção 5.3) |

### 5.1 Visão (degrau 1)

| campo | o que é |
|---|---|
| `outros` | os pets a até `raio_visao` (as 6 células do mundo): `(id, dx, dy, d, acao_visivel)`, com a posição relativa, em ordem de `d` e de id |
| `acao_visivel` | a ação que o outro escolheu na última decisão (comer, brincar, dormir, explorar, ocioso, chamar, emburrar). É o que se vê de fora |
| `onde_comeu` | o último ponto em que este pet **viu** o outro comer (dentro do raio, no momento do consumo), com há quanto tempo. Nada, se nunca viu |

O pet sabe **onde** o outro comeu e **o que** ele estava fazendo, porque viu. Não sabe se fez bem a ele.

### 5.2 Toque (degrau 1)

**O que gera o evento de contato.** É uma conta do mundo, no fim de cada tick com decisão, depois de os pets agirem na ordem sorteada. Há
contato quando os dois estão **na mesma célula ou em células vizinhas**: a distância de Chebyshev entre as células, `max(|cx_A − cx_B|,
|cy_A − cy_B|)`, é no máximo 1, com a célula `(x // 16, y // 16)`.

**O tipo do contato** sai do que aconteceu no tick, e não de uma intenção:
- **disputa:** os dois tinham como alvo a mesma comida nesse tick, e só um comeu. O que comeu sente `disputa_ganhou`; o outro,
  `disputa_perdeu` (a comida sumiu debaixo dele);
- **encostar:** um dos dois tinha como alvo o candidato `seguir` e terminou vizinho do outro. Quem foi sente `encostou`, e o outro sente
  `encostaram`;
- **esbarrar:** qualquer outro contato.

**O que o receptor lê:** `toque = (id do outro, tipo, direção)`, com a direção em 8 (a mesma tabela do cheiro da comida) ou 0 na mesma
célula. Um contato por par e por tick com decisão.

**O que o toque não faz no degrau 1:** não mexe no corpo. O efeito do contato no corpo (a solidão, a aglomeração) é do degrau 3 (CV-5).

### 5.3 Cheiro (degrau 1b; o de estado, no degrau 3)

**O cheiro próprio e o rastro.** Cada pet emite um cheiro na posição em que está e deixa um **rastro**: a cada decisão, uma marca na posição
dele.
- **As fontes** ficam no `Mundo` compartilhado, por pet: a posição atual, com a intensidade `A_pet`, e as marcas, até `max_marcas` por pet
  (as mais antigas saem). Cada marca perde intensidade em inteiros, `A_marca × (T − idade) // T`, e some com a idade `T`.
- **A soma** é a mesma conta do cheiro da comida (`mundo.cheiro_em`, `A × (R − d) // R` com `d < R`), por outro pet, num canal separado do
  da comida.
- **O que o receptor lê:** por pet conhecido, a intensidade e a direção (`direcao_do_cheiro`, com a mesma ordem de desempate do cheiro da
  comida).
- **Os números** (`A_pet`, `A_marca`, `R`, `T`, `max_marcas`) são PROPOSTOS, SEM FONTE, e o plano do degrau 1b os fixa.

**Quem decide o que o corpo emite é o corpo.**
- **O cheiro próprio e o rastro** são **emissores externos** declarados no grafo do corpo: um tipo novo de emissor, com destino `mundo`,
  que não produz químico em corpo nenhum. O emissor do degrau 1b tem intensidade constante: não lê químico, então o cheiro não carrega
  nada do estado.
- **O cheiro de estado** (degrau 3) é um emissor externo cuja intensidade **lê um químico do próprio corpo** (o estresse, o susto), com o
  ganho declarado no grafo. O outro pet lê só a intensidade do cheiro no mundo, nunca o químico.
- **As checagens da seção 18 do corpo** passam a ver os dois corpos no degrau 3: um laço receptor → emissor que passe pelo cheiro de um pet
  e volte pelo do outro entra na conta do "laço de ganho" (produto de ganhos < 1). No degrau 1b, sem leitura de químico, não há laço.

### 5.4 Audição (degrau 1b)

**O som não é mensagem.** É o barulho que uma ação faz. O vocabulário fechado (`COMIDA(lugar)`) continua sendo o degrau 2 (DP-6).

**Os sons:** cada um é um evento do mundo, emitido na posição do pet na decisão em que ele age:

| som | quando |
|---|---|
| `comendo` | o pet comeu (comer, ou o achou e comeu do explorar) |
| `bola` | o pet brincou com a bola |
| `chamado` | o pet escolheu `chamar_atencao` |
| `emburrado` | o pet escolheu `emburrar` |

**O alcance** é `R_som` (PROPOSTO: 16 células, além das 6 da visão), com a intensidade caindo pela mesma conta inteira do cheiro.

**O que o receptor lê:** os sons ouvidos desde a decisão anterior, cada um `(id do emissor, som, direção em 8, distância)`. Os sons do
próprio pet não entram.

**O que fica de fora:** o som não diz o que o outro comeu nem se fez bem. Ouvir `comendo` diz só que ali alguém comeu.

### 5.5 O que fica de fora (G-RECEPTOR-SOCIAL)

- o estado interno do outro: drives, receptores, químicos, pesos, memória e o alvo que ele escolheu;
- o que o outro comeu e não foi visto nem ouvido, e o efeito da fruta no corpo dele;
- qualquer cheiro que não saia de um emissor declarado no grafo do corpo.

## 6. A interação mínima: os degraus 1 e 2

**O degrau 1, sem sinal: competir e observar.**
- **Competir:** a comida no chão é uma só para os dois. Quem pega primeiro come (seção 3), e não há agressão entre pets (CV-3).
- **Observar:** ver o outro comer e ir lá. O mundo oferece, no explorar, dois candidatos a alvo a mais:
  - `seguir`: ir até onde o outro está, se visto;
  - `onde_comeu`: ir ao último ponto em que se viu o outro comer.
- **O padrão do motor e o instinto nunca escolhem esses candidatos.** Se o pet vai lá, é porque o cérebro aprendeu a ir (seção 8). Não há
  regra escrita de imitação.

**Aprender observando (5.2) já é o primeiro degrau medível, e é mais barato que a comunicação (DP-5).**
- **O mais barato:** não pede ação nova, evento novo nem vocabulário; só a visão e o toque da seção 5 e os dois candidatos.
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
- **as entradas sociais:** "outro à vista", "viu o outro comer" (recente), a ação visível do outro e o toque (o tipo do último contato),
  nas regras de tempo livre, com prior 0 (no prior, a vida de hoje). A audição e o cheiro entram como entradas no degrau 1b, do mesmo jeito.

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

## 9. O dono (DP-7, DECIDIDA com mudança)

**A decisão do Matheus (2026-10-07):** o objetivo são **donos separados, um por pet**. A validação inicial é com **um dono para os dois**, com
orçamento por pet. O segundo dono entra depois, numa etapa própria (seção 12), com gate próprio.

**A validação inicial: um dono, orçamento por pet.**
- **O dono** é o mesmo dono sintético (por exemplo, o atencioso), com **um orçamento de 16 interações por dia para cada pet** e a rng
  própria de cada pet (`dono`, `dono-lugar`, com o rótulo do pet).
- **O cuidado dirigido** (limpar, acariciar) vai ao pet do orçamento.
- **A comida** sai do orçamento do pet para quem o dono a solta, e cai no **mapa compartilhado**. O outro pode comer: é a competição. Onde
  o dono a solta (perto de quem, no comedouro) já é a variável do cuidado do mundo físico (PMF-4).
- **Por pet, sem decisão conjunta:** nesta fase, o dono decide o cuidado de cada pet só pelo que vê daquele pet, como se fossem dois donos
  com a mesma política. Uma decisão que olhe os dois juntos (soltar a comida "entre os dois", por exemplo) fica fora, porque dois donos
  separados não a reproduziriam.

**O objetivo: donos separados.**
- **Cada pet tem o próprio dono,** com a própria política, o próprio orçamento e as próprias rngs (`dono`, `dono-lugar`, com o rótulo do
  dono).
- **No registro do grupo,** cada evento do dono leva a **origem** (`dono:<id>`) além do destino (seção 4).
- **O gate da etapa (G-DONOS):** a vida com dois donos **de mesmo comportamento** (a mesma política, cada um com o rótulo de rng igual ao
  do pet que o dono único usava) reproduz byte a byte a vida com um dono só. Só depois disso os dois donos podem diferir (um atencioso, um
  relapso).
- **O que se ganha:** o dono de um pet passa a ser separável do companheiro. É o desenho do produto que o Matheus quer, e as células de dois
  donos diferentes entram por plano próprio.

## 10. Os gates

| gate | o que confere |
|---|---|
| **G2** | **chave do grupo desligada, ou um pet só no grupo** = as vidas de hoje byte a byte: o mundo físico com e sem o corpo, contra os gabaritos de hoje (`mundo_vidas_de_hoje.json`, `corpo_mundo_vidas_de_hoje.json`) e um gabarito novo, gravado antes da extração do `Mundo` |
| **G1-GRUPO** | o grupo inteiro, rejogado do registro, dá os mesmos estados, posições, objetos, ordens sorteadas e estados internos, bit a bit |
| **G-ORDEM** | trocar a ordem em que o código guarda os motores não muda nada |
| **G-NUMS-GRUPO** | trocar o cérebro de B não muda as rngs de A, as quedas, a ordem sorteada nem os sorteios do dono de A. Só muda o que passa pela interação física (a fruta que sumiu, a bola que rolou), e cada diferença do A é explicada por um evento do B |
| **G-RECEPTOR-SOCIAL** | nenhum cérebro importa o motor nem o mundo; a `PercepcaoSocial` não tem campo de estado interno; mudar o estado interno do outro sem mudar o que ele faz, onde está e o que o corpo dele emite não muda nenhum sentido |
| **G-SENTIDOS** | o toque nos casos da seção 5.2 (disputa, encostar, esbarrar, nenhum contato a duas células); no degrau 1b, o rastro e o cheiro próprio na conta inteira do cheiro da comida e o som no alcance e na direção; no degrau 3, o cheiro de estado só por emissor do grafo, com a checagem de laço entre os dois corpos |
| **G-DONOS** | na etapa do segundo dono: dois donos de mesmo comportamento reproduzem byte a byte a vida com um dono só (seção 9) |
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
| a audição e o cheiro do degrau 1b (A; o emissor externo no grafo, B) | o degrau 1 ter resposta (DP-11) | — |
| o segundo dono (A e D) | a validação do degrau 1 com um dono; o G-DONOS | a audição e o cheiro do 1b |
| o cheiro de estado (B, no grafo; A, no mundo) | o degrau 3 (DP-12) | — |
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
| R-9 | **Um sentido vazar o estado interno:** o cheiro de estado é, por desenho, uma função de um químico do outro | só por emissor declarado no grafo do corpo, com ganho declarado, e só no degrau 3 (DP-12) |
| R-10 | **Muitos canais de uma vez:** com quatro sentidos, não se sabe qual ensinou | visão e toque no degrau 1; a audição e o cheiro entram depois, cada um medido como acréscimo (DP-11) |
| R-11 | **O dono único que olha os dois:** uma decisão conjunta não teria par com dois donos | na validação inicial o dono decide por pet; o G-DONOS confere a passagem para dois |

**Literatura.** Nenhuma referência sustenta este desenho: ele é de engenharia. As referências da `cognicao_social.md` (seção 9) e da
`convivencia_mundo_fisico.md` (seção 7) que estão como **pista** continuam pista e não são citadas pelo conteúdo. Não há alegação de
novidade: aprendizado social, forrageio em grupo e comunicação entre agentes artificiais já estão publicados.

## 14. Decisões do Matheus

**DECIDIDAS em 2026-10-07:**
- **pela recomendação:** DP-1, DP-2, DP-3, DP-5, DP-6, DP-8, DP-9 e DP-10;
- **com mudança:** DP-4 (os sentidos: toque, cheiro e audição, além da visão; seção 5) e DP-7 (donos separados como objetivo, validação
  inicial com um dono para os dois; seção 9).

**Também DECIDIDAS pela recomendação, em 2026-10-07:** DP-11 e DP-12, que saem da DP-4.

| # | decisão | estado ou recomendação | custo de errar |
|---|---|---|---|
| DP-1 | O motor de N pets | **DECIDIDA:** um motor por pet sobre um `Mundo` compartilhado, com um orquestrador | — |
| DP-2 | A ordem no tick | **DECIDIDA:** a vez sorteada no fluxo `mundo-ordem`, só com dois ou mais pets decidindo | — |
| DP-3 | O registro | **DECIDIDA:** um registro do grupo, com o destino (e, com dois donos, a origem) de cada evento e o cabeçalho da composição | — |
| DP-4 | A percepção do outro | **DECIDIDA com mudança:** visão, toque, cheiro e audição, cada um como receptor, sem acesso ao estado interno; o cheiro de estado só por emissor declarado no grafo do corpo (seção 5) | — |
| DP-5 | O primeiro degrau | **DECIDIDA:** aprender observando, antes de qualquer mensagem | — |
| DP-6 | A comunicação, quando entrar | **DECIDIDA:** sub-decisão do `chamar_atencao`, com o outro como alvo e vocabulário fechado | — |
| DP-7 | O dono | **DECIDIDA com mudança:** donos separados como objetivo; a validação inicial com um dono, orçamento por pet; o segundo dono numa etapa própria com o G-DONOS (seção 9) | — |
| DP-8 | O cérebro A no degrau 1 | **DECIDIDA:** alvo aprendido e entradas sociais; o modelo dos outros só registrado até o degrau 3 | — |
| DP-9 | O controle do primeiro degrau | **DECIDIDA:** o A embaralhado, mais o B só e o B com um A ingênuo | — |
| DP-10 | A ordem com o resto | **DECIDIDA:** o motor em paralelo com o corpo; o cérebro depois da etapa 6 do corpo; a bancada depois; as runs depois da validação do mundo físico e do plano. Com a DP-7, o segundo dono entra depois da validação do degrau 1 (seção 12) | — |
| **DP-11** | Quais sentidos no primeiro degrau | **DECIDIDA:** **visão e toque no degrau 1; audição e cheiro (rastro e cheiro próprio) no degrau 1b**, depois de o 1 ter resposta, cada um medido como acréscimo | **tudo no degrau 1:** se o B aprende, não se sabe por qual canal, e a primeira medida fica mais cara (quatro receptores a calibrar). **Visão só, sem toque:** a disputa acontece do mesmo jeito, e o pet perde a única pista física dela. **Audição e cheiro só no degrau 3:** atrasa canais baratos, que não dependem do corpo |
| **DP-12** | O cheiro de estado (estresse, medo) | **DECIDIDA:** **no degrau 3, com a solidão e a aglomeração (CV-5)**, por um emissor externo declarado no grafo do corpo, com o laço entre os dois corpos na checagem de ganho | **no degrau 1 ou 1b:** um canal emocional entre corpos entra antes de se saber se a observação funciona, e o "aprendido de outros" passa a misturar contágio com informação. **Sem passar pelo grafo:** o cheiro vira leitura direta do estado do outro, que a regra proíbe |
