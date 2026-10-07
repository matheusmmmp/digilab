# Tarefa — V2: o corpo mínimo e os drives de tédio, curiosidade e solidão (W-TAREFA-CORPO, rodada 16)

Status (2026-10-07): **PROPOSTO**. Só papel. Esta tarefa não autoriza run de pesquisa: o efeito dos drives novos é medido por um plano
próprio, `docs/PLANO_ANALISE_V2_CORPO_DRIVES.md`, commitado antes de qualquer run (seção 13).

**Parte de:**
- `docs/futuro/ego_existencia.md`:
  - seção 2, o corpo do Creatures 3 (2.1, os conceitos do manual; 2.2, o corpo do Digilab nesses conceitos);
  - seção 9, etapas 1 (corpo químico mínimo) e 1b (órgãos e dano: fica fora, seção 1).
- `docs/DECISAO_PRODUTO_SEM_ELOGIO_BRONCA.md`:
  - seção 4: acariciar e o tapa como estímulos no corpo;
  - seção 5: sem drives que recompensem brincar, explorar e o contato, a consequência ensina o pet a ficar parado.
- As seções "V2, N3", "V2, LOBOS-MUNDO" e "V2, CANAIS-REFORCO" do `CLAUDE.md`: o sinal homeostático, a E2 e os canais.
- `docs/TAREFA_V2_MUNDO_FISICO.md`, seção 8: o gancho `consequencia_mundo`, que o corpo precisa alimentar.

**Já decidido** (`docs/V2_RODADA_16.md`, seção 4; não se reabre aqui):
- **S-1:** só os pets novos ficam sem elogiar e repreender.
- **S-3:** a consequência só liga no produto depois destes drives. Esta tarefa é o pré-requisito.
- **S-4:** a base nova do vínculo é tarefa própria.
- **E-9:** a química entra por baixo dos drives de hoje, um órgão por vez.
- **E-10:** o tamanho é o mínimo que reproduz os drives de hoje, mais a digestão e a Vida.

**Revisto pelo Matheus (2026-10-07, depois da primeira versão desta tarefa): o tapa também manda sinal direto ao cérebro** (seção 8).
- Isso muda a S-2 e o #203, seção 4, que diziam "um estímulo no corpo, e não uma nota direta ao cérebro".
- O tapa continua sendo estímulo no corpo (dor, susto, estresse). Agora ele é estímulo **e** sinal.
- O carinho segue só pelo corpo.
- O registro da decisão (`docs/DECISAO_PRODUTO_SEM_ELOGIO_BRONCA.md`, seções 4 e 8) fica para o coordenador atualizar.

**Vale para qualquer cérebro.** O porte do v11 está pausado (`docs/V2_RODADA_16.md`, seção 6): o Matheus quer um pet que planeja, e o
corpo é o que esse cérebro vai precisar prever. O corpo expõe receptores e ganchos (seções 10 e 11); um cérebro que não os lê vive como hoje.

## 1. A pergunta, o que entra e o que fica fora

**Pergunta (para o plano, não para esta tarefa):** com a química mínima por baixo dos drives, a consequência pelo corpo deixa de ensinar o
pet a ficar parado? Isto é: brincar, explorar e o contato passam a render sinal positivo, e o cuidado não piora?

**Entra:**
- a química dos drives de hoje (fome, higiene, energia, humor, saúde), em inteiros, sem órgão (seção 4);
- o **órgão 1, a digestão**, com a composição de cada comida (seção 5);
- o **órgão 2, a Vida**, o relógio que decai e muda o estágio por receptor (seção 6);
- os **drives novos** (seção 7):
  - **tédio**, que brincar com a bola reduz;
  - **curiosidade**, que explorar e achar coisa nova reduz;
  - **solidão**, que acariciar reduz. A seção 5 do #203 pede a solidão ("o contato"), então ela entra;
  - **estresse**, que se acumula com drives altos e que acariciar reduz;
- o **carinho e o tapa** como estímulos no corpo, com a dor leve e o susto, e o **sinal direto do tapa ao cérebro** (seção 8);
- o **sinal da consequência** tirado da redução dos drives pelo corpo, com os canais por drive como opção (seção 9);
- os **receptores**: o pet sente só por eles (seção 10).

**Fica fora:**
- os órgãos com força vital, dano, cura e morte; as lesões como dano de órgão; os genes que ligam por estágio; o genoma de fisiologia
  (tudo da etapa 1b do `ego_existencia.md`);
- a doença (toxinas, antígenos, anticorpos, remédios);
- o ATP como químico próprio: o cansaço de hoje faz esse papel;
- o estresse mudando outras funções (saúde, obediência, fertilidade): aqui ele é só medido e entra no sinal;
- a morte pela Vida;
- a rede de si (etapa 2 do `ego_existencia.md`);
- a base nova do vínculo (S-4, tarefa própria) e a disciplina das travessuras;
- a tela, os botões e qualquer versão de pet nova (seção 15).

## 2. A chave e o lugar no motor

**Chave:** `ConfigCorpo` em `digilab/config.py`, desligada por padrão.
- **Uma sub-chave por etapa** (E-9, um órgão por vez): `digestao`, `vida`, `drives_novos`, `gestos`.
  - `ConfigCorpo.ligada` sozinha liga a química dos drives de hoje (seção 4).
  - Cada sub-chave exige a anterior e falha alto sem ela.
- **Com a chave desligada:** nenhuma chave nova em `estado()`, nenhum campo novo preenchido, nenhuma chamada de rng a mais. É a vida de hoje
  byte a byte (G2).

**O motor:** `MotorCorpo`, por subclasse (dono: o A). **`engine.py` não muda.**
- **Por baixo:** com a chave ligada, os drives do `Estado` (fome, higiene, energia, humor, saúde) passam a ser **a leitura** da química a
  cada tick. A dinâmica float de `state.avancar_um_tick` e dos efeitos de ação deixa de valer para eles.
- **O caminho recomendado:** o motor mais derivado refaz o laço do tick (o corpo de `Motor._avancar`) numa subclasse, chamando o passo do
  corpo no lugar de `avancar_um_tick`.
  - Os efeitos por avanço das classes do meio precisam ficar: o contador de eventos do `MotorPersonalidade` e a morte conferida do
    `MotorEducacao`. O G2 pega o que se perder.
  - **Se a química não couber por baixo sem tocar o `engine.py`, o A para e relata.** Um corpo "em sombra", que roda ao lado sem decidir
    nada, não cumpre a E-9.
- **Auditoria primeiro (etapa 0 do `ego_existencia.md`).** O A lista todo lugar que escreve um drive do `Estado`, e cada um vira um
  estímulo no corpo:
  - `state.aplicar_acao_usuario`;
  - `policy.efeito_da_acao_do_pet`;
  - a bola do `MotorAmbiente`;
  - a nutrição e o humor da fruta no `MotorFrutas`;
  - o gasto de energia do mundo físico.

  Com a chave ligada, um drive mudado por fora do corpo falha alto (G-BYPASS).
- **O corpo não sorteia nada.** As chamadas de rng de hoje continuam as mesmas, na mesma ordem: a sujeira por tick e a sujeira depois de
  alimentar. Nenhuma rng nova, como a bola da A1.
- **Onde vale:**
  - o corpo vale nos motores dos mundos da pesquisa: `padrao` (`MotorComFeedback`), `bola` (`MotorAmbiente`), os mundos das frutas
    (`MotorFrutasMundo`) e o mundo físico (`MotorMundo`, quando entrar);
  - com educação, lesões, treino ou obediência ligados, **falha alto**: lesão como dano de órgão é da 1b;
  - a **curiosidade exige o mundo físico** (CD-8): sem ele não há o que achar, e `drives_novos` sem o mundo liga só o tédio, a solidão e o
    estresse.

## 3. Unidades e regras inteiras

**A escala:** uma concentração é um inteiro em `[0, C]`, com **C = 450000** (decisão CD-1).
- **Por que 450000:** é o mínimo múltiplo comum dos denominadores de todas as taxas e ganhos de hoje. Com ele, toda taxa por tick e todo
  efeito de ação de hoje vira um inteiro exato (tabela da seção 4).
- A conta foi feita com as frações de `digilab/config.py`. A lista é a da tabela; o mínimo múltiplo comum dos denominadores dá 450000.
- **Corte:** como o `_limitar` de hoje, toda concentração fica em `[0, C]` depois de cada passo.

**A leitura de um drive de hoje:** o químico guarda a falta, e o drive é a satisfação: `fome = (C − q_fome) / C`. A divisão de ponto
flutuante é exata pela norma IEEE, igual no Python e no TypeScript.

**Meia-vida** (dos químicos novos que decaem). Para uma meia-vida de h ticks, a constante é `k_h = arred(2¹⁶ · (1 − 2^(−1/h)))`.
- **A constante é calculada uma vez e gravada como inteiro na `ConfigCorpo`.** Nenhuma função transcendental roda no tick, no Python ou
  na web. Um teste confere a derivação.
- **O passo:** `q ← q − max(1, div_arred(q · k_h, 2¹⁶))` enquanto `q > 0`. O mínimo de 1 impede que uma concentração pequena fique
  presa (com k = 32, abaixo de ~1024 o decremento arredondaria a 0).
- **Valores de referência:**

  | h (min) | k_h | meia-vida efetiva |
  |---|---|---|
  | 30 | 1497 | 30,0 |
  | 60 | 753 | 60,0 |
  | 1440 | 32 | 1419 |

**Receptor para o cérebro:** a leitura na escala S = 1024 do cérebro A é `div_arred(q · S, C)`, a falta em inteiros, sem passar por
float. O drive de hoje lido pelo cérebro é `S − div_arred(q · S, C)`.

**Por que "dentro da tolerância", e não byte a byte, com a química ligada.** As regras de hoje somam floats, e a química soma inteiros
exatos. Os limiares de hoje caem exatamente sobre pontos da grade inteira, então uma comparação pode virar.
- **Exemplo**, com a fome inicial 0,80 e o decaimento 1/1200 por tick:
  - em inteiros, a fome chega a 0,25 exato no tick 660, e `fome < 0,25` é falso;
  - no float de hoje, `x = 0.8; x -= 1/1200` repetido 660 vezes dá 0,24999999999998737, e a comparação é verdadeira (conferido no
    Python).
- **Consequência:** uma decisão muda, a rng da política desalinha e a vida segue outra.
- **Por isso o G-HOJE tem duas partes** (seção 12):
  - **malha aberta, por tick:** com as mesmas ações forçadas, um teste de unidade com os números desta tarefa;
  - **malha fechada:** a distribuição das vidas, com a margem do plano.

## 4. A química dos drives de hoje (sem órgão)

Cinco químicos guardam a falta de cada drive de hoje. Os números abaixo são **os de hoje, convertidos**: não há valor novo nesta seção.

| químico | drive lido | por tick | estímulos de hoje (em C) |
|---|---|---|---|
| `fome` | fome | +375 | alimentar −202500; comer (fora do mundo) −22500; dono brincar +22500; fruta: pela digestão (seção 5) |
| `desconforto` | higiene | +300 + 36 × sujeira | limpar −270000 |
| `cansaco` | energia | acordado +500 (noite +900); dormindo −1875 | dono brincar +36000; pet brincar +9000; explorar +6750; andar no mundo: o custo do mundo convertido |
| `tristeza` | humor | +375 | dono brincar −112500; acariciar −27000 (seção 8); elogiar −45000; repreender +54000; pet brincar −56250; explorar −4500; emburrar +4500; bola −67500; fruta ±45000 (E2) |
| `dano` | saúde | privação: +225; sem privação: −150 | — |

- **Na ordem de hoje,** dentro do tick:
  1. fome, desconforto (com a sujeira do estado anterior), tristeza e cansaço (dormindo ou acordado, com a noite pelo tick do estado anterior);
  2. o sorteio da sujeira, se acordado;
  3. o corte;
  4. o dano.

  O efeito da ação do pet entra na decisão, antes do tick, como hoje.
- **O dano é uma reação com a taxa controlada por receptor** (o conceito do manual: "um receptor pode controlar a taxa de uma reação"):
  - o receptor de privação lê `fome`, `desconforto` e `cansaco`;
  - privação é algum deles acima de `C − 67500`, o limiar 0,15 de hoje;
  - com privação o dano sobe 225; sem, desce 150.
- **Sujeira e dormindo** continuam estados do `Estado`, não químicos: a sujeira é da pele, e o sono é a ação.
- **O custo de andar do mundo físico** (`custo_energia_por_subunidade`, PROPOSTO na tarefa do mundo) precisa virar um inteiro de C por
  subunidade. Se não virar, o A propõe o arredondamento na tarefa do mundo, antes da integração.

## 5. Órgão 1: a digestão

- **O estômago:** a comida entra como o químico `alimento`, e não direto na fome. A reação da digestão tira `alimento` e a mesma
  quantidade de `fome` a uma taxa por tick: `t = min(alimento, fome, taxa_digestao)`.
- **A composição de cada comida** (a "composição" da seção 2.2): quanto `alimento` ela põe e o efeito dela na `tristeza`.

  | comida | `alimento` | `tristeza` |
  |---|---|---|
  | ração (alimentar) | 202500 | — |
  | comer sem mundo | 22500 | — |
  | fruta madura | 67500 (os 0,05 do comer mais os 0,10 do N4) | o efeito da condição: −45000 boa, +45000 ruim, 0 neutra |

  Com o mundo físico, a ração deixada é 202500 e a fruta 67500, como na tabela da tarefa do mundo.
- **A taxa de hoje** (CD-3): com `taxa_digestao = C`, tudo passa no mesmo tick, e a fome lida é a de hoje (G-HOJE).
  - A **digestão lenta** (uma taxa menor) fica atrás do parâmetro, PROPOSTA, sem valor nesta tarefa.
  - Ela muda os drives de hoje de propósito e entra só com o plano.
- **Sem receptor para o cérebro:** o pet sente a fome, não o estômago. O `alimento` fica com o motor.
- **Força vital, dano e cura do órgão** ficam para a 1b. Aqui a digestão sempre funciona.

## 6. Órgão 2: a Vida

- **O químico `vida`** começa em C (concentração inicial) e decai `v` por tick, um inteiro. O valor de `v` sai da duração máxima de vida
  da pesquisa e não muda nada nesta tarefa.
- **O estágio por receptor:**
  - receptores sobre a `vida` mudam o estágio nos limiares `C − v · tick_do_estagio`, os ticks de estágio de hoje;
  - nos motores que têm estágio, o estágio pela Vida é o de hoje, tick a tick (G-HOJE, exato: é contagem inteira);
  - nos motores sem estágio (o `MotorComFeedback` do mundo `padrao`), a Vida decai e fica registrada.
- **Sem receptor para o cérebro:** o pet não sabe quanto de Vida tem (sem acesso privilegiado). Saber o próprio estágio por observação é
  da rede de si.
- **A Vida não mata nesta tarefa.** Com `vida = 0`, ela fica em 0. A morte pela Vida e os genes por estágio ficam para a 1b.

## 7. Os drives novos

Os números são **PROPOSTOS, sem fonte**: a ordem de grandeza segue os drives de hoje. O plano calibra (seção 13). O manual do Creatures 3
dá só os conceitos: drives como químicos e estresse que se acumula com drives altos.

| químico | sobe | o que reduz | meia-vida | receptor |
|---|---|---|---|---|
| `tedio` | +450 por tick acordado (cheio em ~17 h) | pet brinca com a bola −135000; pet brinca sem bola −45000; dono brinca −90000 | — | sim |
| `curiosidade` (só com o mundo físico) | +300 por tick acordado (cheia em 25 h) | explorar e achar coisa nova: −90000 por novidade, até 2 por decisão | — | sim |
| `solidao` | +225 por tick acordado (cheia em ~33 h) | acariciar −180000 (seção 8) | — | sim |
| `estresse` | `div_arred(Σ max(0, q_d − 337500), 256)` por tick, sobre `fome`, `desconforto`, `cansaco`, `tedio`, `curiosidade`, `solidao` e `dor` | acariciar −90000; a meia-vida | 1440 | sim |

- **A novidade:** um objeto de `vistos` que o pet não viu nas últimas `janela_novidade` (1440) ticks, achado numa decisão de explorar.
  - Contam só a comida e a bola: árvores, ninho e comedouro são cenário.
  - O motor guarda o registro do que o pet viu e quando. É o que o pet viu, não o mapa inteiro.
  - O `ocorrido` do mundo ganha os `vistos_novos` (dono: o A, na tarefa do mundo).
- **Estresse:**
  - acumula com drives altos, acima de 0,75 de falta (o 337500);
  - a meia-vida o desfaz devagar, e acariciar o reduz;
  - não muda outra função nesta tarefa (CD-7).
- **Dormindo:** tédio, curiosidade e solidão não sobem.
- **O instinto não lê os drives novos** (CD-2).
  - O P0 continua o instinto de hoje, e o que muda o comportamento é o aprendizado pelo sinal (seção 9).
  - Sem isso, um P0 diferente mudaria a referência de todos os contrastes.

## 8. O carinho e o tapa no corpo, e o sinal do tapa

**Acariciar** (`AcaoUsuario.ACARICIAR`, de hoje) vira estímulo:
- `solidao` −180000;
- `estresse` −90000;
- `tristeza` −27000, o 0,06 de hoje.

**O tapa** (`AcaoUsuario.TAPA`, novo no **fim do enum**, `ACOES_CORPO`, como as frutas entraram) vira estímulo:
- `dor` +90000: dor leve, meia-vida 60;
- `susto` +180000: meia-vida 30;
- `estresse` +45000.

Regras do tapa:
- **Só o `MotorCorpo` com `gestos` ligado aceita;** no `reproduzir` de hoje, ele levanta erro, como todo evento desconhecido.
- **O tapa gasta uma interação do orçamento e conta como contato**, como o repreender de hoje (CD-6).
- **`dor` e `susto` têm receptor.**

**O carinho chega ao cérebro só pelo corpo.**
- O motor **não** repassa `acariciar` por `receber_acao_dono` nos pets com `gestos` ligado (espião no G-MEC).
- O cérebro vê só o que os receptores mostram, antes e depois do carinho, pelo gancho `mudanca_no_corpo(obs_antes, obs_depois)`. O gancho
  não diz que gesto foi.
- **Crédito** (CD-4): o cérebro calcula o sinal pelo corpo (seção 9) e o credita à última decisão, pela janela da v1 (a do elogio e da
  bronca).
- **Do cuidado, só o carinho é creditado assim.** Alimentar, limpar e o dono brincar mudam o corpo, mas não viram sinal de aprendizado,
  como no N3: a consequência é da própria ação do pet.

**O tapa manda sinal direto ao cérebro** (revisão do Matheus, 2026-10-07):
- **O caminho:** o motor repassa o `tapa` por `receber_acao_dono`. O cérebro o credita à última decisão pela janela da v1, como a bronca.
- **O valor:** `f = arred(recompensa_tapa · S)`, com `ConfigLobos.recompensa_tapa` (PROPOSTO: o mesmo valor da `recompensa_repreensao`;
  CD-10).
- **Em toda fonte que aprende** (CD-10): o sinal chega ao P1, ao P2 e ao P3 e às variantes deles, e não só à fonte dono, porque o tapa é o
  gesto que o pet do produto, que aprende pela consequência, vai receber.
  - No P0 nada aprende.
  - A `PoliticaDoBraco` deixa passar o tapa nas fontes que hoje bloqueiam o dono (dono do arquivo: o D). O resto do dono continua
    bloqueado como hoje.
- **Escalar:** como o sinal do dono, os canais não o dividem.
- **Sem dupla contagem** (CD-9): o tapa não chama o `mudanca_no_corpo`. A mudança no corpo que ele causa não é creditada de novo.
  - A dor, o susto e o estresse ficam no corpo.
  - A dor e o estresse pesam nas decisões seguintes pelo D da própria ação (seção 9).

**Diferença do repreender.** O sinal é o mesmo da bronca. O que o tapa tem a mais é o corpo:
- a dor, o susto e o estresse;
- o medo da mão e o estresse acumulado, que o jogador vê.

O repreender fica nos pets antigos e na fonte dono (S-1); o tapa chega também ao pet que aprende pela consequência.

**O medo da mão** (CD-5). O receptor do `susto` controla a taxa da reação do carinho, o conceito do manual: com susto, o carinho alivia
menos. O efeito do carinho na solidão e no estresse é multiplicado por `(C − q_susto) / C`, em inteiros. Com o parâmetro em 0, a variante
sem medo.

**Os efeitos medidos** (as medidas são da bancada e o braço é do plano):
- **medo da mão:**
  - a redução média da solidão por carinho nas 6 h depois de um tapa, contra a mesma medida sem tapa antes;
  - a fração de `chamar_atencao` nas decisões das 6 h depois de um tapa;
- **estresse acumulado:** o estresse médio no fim de cada dia e a fração do tempo acima de 0,75;
- **vínculo:** o da base nova (S-4), quando ela entrar. Antes disso, a medida sai "não disponível" (dependência declarada).

## 9. O sinal da consequência pelo corpo

**A conta** é o sinal homeostático do N3 sobre os receptores. Com `falta_d = div_arred(q_d · S, C)`:
- `D = Σ w_d · falta_d²`;
- `f = div_arred(ganho · (D_antes − D_depois), S)`.

**Os drives do sinal:**
- `fome`, `desconforto` e `cansaco`, os do N3;
- `tristeza`, só no consumo de fruta, como a E2;
- com `drives_novos`: `tedio`, `curiosidade`, `solidao`, `estresse` e `dor`;
- o `susto` fica fora do sinal: é rápido e já pesa pela dor e pelo estresse.

**Os pesos** `w_d` são inteiros, todos 1, PROPOSTOS. O plano pode calibrá-los.

**As janelas de crédito:**
- **a própria ação** é a janela imediata do N3: o "antes" é a decisão, e o "depois" vem logo depois dos estímulos da ação (andar, comer,
  brincar, achar), antes do tempo e do dono. A consequência atrasada (o tédio que volta a subir) segue declarada e sem crédito;
- **o carinho** é a seção 8: o "antes" e o "depois" são do carinho, creditados à última decisão;
- **o tapa** não entra nesta conta: ele manda o sinal direto da seção 8, na mesma janela.

**Os ganchos:**
- **com o mundo físico:** o corpo aplica os estímulos do `ocorrido` antes de o mundo chamar `consequencia_mundo(acao, ocorrido,
  obs_depois)`. O `obs_depois` já traz `obs.corpo` com o tédio, a curiosidade e o cansaço da ação. É assim que o corpo alimenta o gancho
  do mundo;
- **sem o mundo físico:** o motor chama `consequencia_corpo(acao, ocorrido, obs_depois)`, com a mesma assinatura;
- **uma chamada por decisão,** sempre, e o teste confere;
- com a chave do corpo, o sinal dos cérebros que aprendem pela consequência passa a esperar esse gancho. A `Transicao.observacao_seguinte`
  do engine traz o `Estado` sem os estímulos dos motores filhos.

**Os canais** (opção, `ConfigConsequencia.canais_ligados`, como hoje):
- **os canais novos:** um por drive novo, com a mesma soma telescópica (o total é o escalar, conferido em toda decisão);
- **as rotas:** `tedio`, `curiosidade`, `solidao`, `estresse` e `dor` vão ao **corpo** (a tabela do lobo de decisão); a `tristeza` da
  fruta continua indo à **fruta**;
- **desligados,** é o escalar.

**Conta de exemplo** (números PROPOSTOS, ganho 4; conferida em Python). O pet brinca com a bola com o tédio em 0,75 e o cansaço em 0,20.
- **O tédio:** de 337500 vai a 202500; a falta, de 768 a 461.
- **O cansaço:** de 90000 vai a 99000; a falta, de 205 a 225.
- **A soma:** `D_antes − D_depois` = (768² − 461²) + (205² − 225²) = 368703.
- **O sinal:** `f` = div_arred(4 · 368703, 1024) = **+1440**.
- **Hoje (N3):** o mesmo brincar dá só a parte do cansaço, **−34**.

## 10. O que o pet sente: os receptores

**Campo novo e opcional** da `Observacao` (dono: o A, só o campo, com padrão, como `mundo`): `corpo: PercepcaoCorpo | None = None`. A
`de_estado`, o bandit e as sondas de hoje não o leem.

| receptor | leitura (escala S) | existe com |
|---|---|---|
| fome, higiene, energia, humor, saúde | a de hoje, `S − div_arred(q · S, C)` | `ligada` |
| tédio, solidão, estresse | a falta, `div_arred(q · S, C)` | `drives_novos` |
| curiosidade | a falta | `drives_novos` e o mundo físico |
| dor, susto | a concentração | `gestos` |

**Sem receptor, só com o motor:**
- `alimento` e `vida`;
- as taxas, as meias-vidas e os limiares;
- o registro de novidade (o pet sabe o que viu, não a tabela).

**Os drives de hoje na `Observacao`** (os campos de sempre) passam a ser a leitura dos receptores, o mesmo número.

**Sem acesso privilegiado**, verificado pelo G-RECEPTOR:
- mudar um químico sem receptor não muda a observação;
- nenhum cérebro importa `digilab/corpo.py`, conferido por AST;
- a política não tem referência ao objeto do corpo.

## 11. Para qualquer cérebro

**A interface:**
- `obs.corpo`, os receptores;
- `consequencia_mundo` ou `consequencia_corpo`, a própria ação;
- `mudanca_no_corpo`, o carinho;
- `receber_acao_dono` com o `tapa`, o sinal direto.

Um cérebro sem esses ganchos vive como hoje: o instinto e o P0 não mudam.

**O cérebro A** (dono: o B):
- **O sinal:** `lobos.sinal_corpo` substitui o `sinal_homeostatico` com a chave.
- **O tapa:** o `Aprendiz` trata o `tapa` como a bronca, com `recompensa_tapa`, em toda fonte que aprende.
- **As entradas novas:** as leituras dos drives novos entram como entradas da percepção, **só nas regras de tempo livre** (`tempo_livre`,
  `bola_no_cenario`, `fruta_no_cenario`), com prior 0.
  - No prior, a vida é a de hoje.
  - São 3 regras × 7 ações × 6 entradas = 126 pesos a mais (~890 no total, contra os 763 da K2). A comparação de capacidade da C-3 fica
    registrada com esse número.
  - **Por quê só ali:** nas regras urgentes o instinto decide por um candidato só.
- **O embrulho:** o `PoliticaComMotivo` repassa `consequencia_corpo` e `mudanca_no_corpo`. A lição do N5-ACOPLADO: um gancho não repassado
  muda a vida.

**Os cérebros B e C:** opcionais. O C ganharia células do circuito do corpo por faixa dos drives novos. Nenhum dos dois é pré-requisito.

**Um cérebro que planeja:**
- o corpo é determinístico dado o estímulo: a mesma concentração e o mesmo estímulo dão a mesma leitura;
- um modelo direto pode aprendê-lo pelos receptores;
- as taxas não são entregues: prever o corpo é trabalho do cérebro.

## 12. Gates

| gate | o que confere | onde |
|---|---|---|
| **G1** | toda vida com o corpo, rejogada do log, dá as mesmas concentrações, o mesmo `estado()` e o mesmo estado interno, bit a bit | `tests/test_corpo.py` e a bancada |
| **G2** | chave desligada = as vidas de hoje byte a byte, contra os gabaritos da etapa 0 (P0, P1, P2, P3; `padrao`, `bola`, `descasado`, `mutavel`, `iguais_frutas`; montagem simples e completa) | `tests/test_corpo.py` |
| **G-HOJE (a)** | química ligada sem os drives novos (com a digestão na taxa C e a Vida), em **malha aberta**. Detalhe abaixo da tabela | `tests/test_corpo.py` |
| **G-HOJE (b)** | química ligada sem os drives novos, em **malha fechada**: P0, P1 e P3 com e sem o corpo dentro da margem e do N do plano (seção 13), na privação, na saúde e na distribuição das ações no tempo livre | só pelo plano |
| **G-V1-V10** | os pets v1 a v10 iguais: os testes de reprodução da web e do Python passam sem mudança | a suíte de sempre |
| **G-PAR** | Python × TS **exatos**, só inteiros: o tick, as reações, as meias-vidas, os receptores, os estímulos e o sinal, numa grade de casos e em 3 vidas inteiras | `web/app/motor/__tests__/corpo.test.ts` e o gabarito do Python |
| **G-ENGINE** | `engine.py` com o sha256 de sempre | `tests/test_corpo.py` |
| **G-RECEPTOR** | sem acesso privilegiado (seção 10) | `tests/test_corpo.py` |
| **G-BYPASS** | com a chave, nenhum drive do `Estado` muda por fora do corpo: entre os passos, o `Estado` é a leitura da química, senão falha alto | `tests/test_corpo.py` |
| **G-MEC** | testes de mecanismo, contas exatas. Lista abaixo da tabela | `tests/test_corpo.py`, `tests/test_corpo_cerebros.py` |
| **G-RISCO** | o risco do #203, seção 5 (seção 13) | `tests/test_corpo_cerebros.py` |

**G-HOJE (a), malha aberta:** o registro de uma vida de hoje, rejogado com as mesmas ações do pet forçadas.
- **Fome, higiene, energia e humor:** |drive do corpo − drive de hoje| ≤ 1e−9 em todo tick.
- **Saúde:** o erro fica em ≤ 1e−9 mais as viradas de privação no limiar, contadas e listadas.
- **Sujeira, dormindo, estágio e as rngs:** iguais.
- **O sinal do N3:** igual em ≥ 99% das decisões; nas outras, a diferença fica em ≤ 3 · div_arred(ganho · (2S + 1), S).

**G-MEC, a lista:**
- brincar com a bola reduz o tédio, e sem bola reduz menos;
- explorar com novidade reduz a curiosidade, e rever o mesmo objeto dentro da janela não reduz;
- acariciar reduz a solidão e o estresse;
- o tapa sobe a dor, o susto e o estresse; passa uma vez por `receber_acao_dono`; credita `recompensa_tapa` à última decisão em toda fonte
  que aprende (P1, P2, P3) e em nenhuma no P0; e não chama o `mudanca_no_corpo`;
- o carinho nunca passa por `receber_acao_dono`;
- o susto corta o efeito do carinho na medida;
- a meia-vida chega à metade no prazo (±1 tick);
- a digestão na taxa C é instantânea;
- a Vida dá os ticks de estágio de hoje;
- há um sinal de consequência por decisão;
- o corpo não chama rng.

**Nenhuma run de pesquisa nesta tarefa.** Os testes usam só as sementes dos testes (11, 22, 33 e 101…505).

## 13. O risco do #203, seção 5, e o plano

**O risco:** hoje, brincar e explorar só dão sinal negativo (gastam energia), e o P1 aprende a ficar parado. A validação do N3 mostrou isso:
ocioso 47% e chamar 27% no tempo livre (`docs/RESULTADO_V2_N3.md`). Com o corpo ligado, isso precisa deixar de ser verdade **no mecanismo**
antes de se medir o efeito.

**O teste de mecanismo (G-RISCO),** em estados controlados, com os números PROPOSTOS:
- com o tédio alto e a energia alta, o sinal de brincar com a bola é positivo (a conta da seção 9: +1440);
- com a curiosidade alta, explorar e achar uma novidade dá sinal positivo; explorar sem achar nada dá o sinal de hoje (só o cansaço);
- com a solidão alta, o carinho dá sinal positivo à última decisão; o tapa dá o sinal direto, negativo, à última decisão;
- **numa vida curta do P1 com o corpo** (sementes dos testes, 4 dias, mundo da bola): p(brincar | tédio > 0,5, bola vista) no fim é maior
  que no começo. Só a direção, sem IC e sem gate de efeito.

**O efeito se mede por plano próprio:** `docs/PLANO_ANALISE_V2_CORPO_DRIVES.md`, commitado antes de qualquer run. O coordenador indica quem
o escreve. O que esta tarefa pede ao plano:
- **a pergunta:** o P1 com o corpo (drives novos ligados) deixa de ficar parado, sem piorar o cuidado, contra o P1 com a química de hoje;
- **a medida:**
  - a fração do tempo livre em brincar e explorar e a fração em ocioso e chamar;
  - os drives novos médios;
  - a privação e a saúde, o cuidado preservado;
- **os braços:** P0 e P1 com e sem os drives novos; o "só cuidado" acoplado; os donos com e sem tapa, pelo `DonoComGestos` (seção 14);
- **as margens e o N do G-HOJE (b);**
- **sementes:** de calibração e de validação, em faixas novas fora de `FAIXAS_RESERVADAS`. As do mundo físico (31101…32505) já estão
  tomadas;
- **a calibração** dos números da seção 7 e dos pesos do sinal, com regra escrita antes.

**O risco do outro lado:** o pet pode aprender a só brincar e descuidar da fome. É por isso que o cuidado preservado entra na medida.

## 14. Quem faz o quê (donos de arquivo)

| etapa | dono | arquivos | entrega |
|---|---|---|---|
| 0. gabaritos e auditoria | **A** | `tests/gabaritos/corpo_vidas_de_hoje.json`; a lista dos escritores de drive (no PR) | as vidas de hoje gravadas **antes** de qualquer mudança, para o G2; a auditoria da seção 2 |
| 1. a química dos drives de hoje | **B** | `digilab/corpo.py` (novo: `Corpo`, os químicos, o tick, os estímulos, os receptores, em inteiros, sem motor), `ConfigCorpo` em `config.py`, `tests/test_corpo_quimica.py` | seções 3 e 4 como componente puro; o exportador do gabarito para a paridade |
| 2. o corpo no motor | **A** | `MotorCorpo` (num arquivo do A), o campo `corpo` da `Observacao` em `policy.py`, o gancho `consequencia_corpo`, `tests/test_corpo.py` | o corpo por baixo dos drives; G2, G-HOJE (a), G-BYPASS, G-RECEPTOR, G-ENGINE |
| 3. órgão 1, digestão | **B** | `corpo.py`, `config.py` | a seção 5; G-HOJE (a) de novo |
| 4. órgão 2, Vida | **B** | `corpo.py`, `config.py` | a seção 6; G-HOJE (a) de novo |
| 5. o cérebro A no corpo | **B** | `lobos.py`, `motivo.py` (o embrulho), `tests/test_corpo_cerebros.py` | `sinal_corpo`, as entradas novas, os canais novos; G-HOJE (a) do sinal |
| 6. os drives novos e os gestos | **B** (química e cérebro) e **A** (motor) | B: `corpo.py`, `lobos.py` (com `recompensa_tapa`). A: `AcaoUsuario.TAPA` em `events.py` (fim do enum), o repasse do tapa, `mudanca_no_corpo`, os `vistos_novos` do mundo, o `DonoComGestos` | as seções 7 a 9; G-MEC, G-RISCO |
| 7. a web (motor) | **A** | `web/app/motor/corpo.ts`, a paridade em `web/app/motor/__tests__/` | o corpo em TS e o G-PAR; nenhuma tela e nenhuma versão de pet |
| 8. a bancada | **D** | `experiments/bancada_v2.py`, `digilab/metrics.py`, `experiments/configs/v2_corpo/` | a chave `corpo` na config, o tapa passando pela `PoliticaDoBraco` em toda fonte que aprende, o filtro `sem_gestos` do acoplado, as medidas das seções 8 e 13, as faixas do plano |

**Ordem:** 0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 e 8 em paralelo. Um PR por etapa, com o relato no corpo. **O merge é do Matheus.**
- O **órgão 1** só entra depois da química base passar o G-HOJE (a).
- O **órgão 2** só entra depois do órgão 1 passar (E-9).
- A **curiosidade** espera o mundo físico na `main` (a etapa 2 da `TAREFA_V2_MUNDO_FISICO.md`). Tédio, solidão e estresse não esperam.

**O `DonoComGestos`** (embrulho do A, para a bancada e o plano):
- troca o `elogiar` do dono sintético por `acariciar` e o `repreender` por `tapa` ou por nada, conforme o modo;
- mantém o resto do dono e o orçamento;
- é a forma mais direta de comparar "com tapa" e "sem tapa" sobre o mesmo dono.

## 15. Pesquisa e produto

| peça | pesquisa (Python) | produto (web) |
|---|---|---|
| química, digestão, Vida, drives novos | atrás da `ConfigCorpo`, nas runs do plano | **pausado** com o porte do v11: entra numa versão de pet nova quando o produto voltar (S-1: os v1 a v10 ficam iguais, com os botões) |
| carinho e tapa no corpo; o sinal direto do tapa | o `DonoComGestos` nos braços do plano | o gesto na tela, que deve ler como desaprovação, não como violência (#203, seção 4); a tela é tarefa própria |
| sinal pelo corpo | o P1 e os braços que aprendem pela consequência | o aprendizado do pet novo (S-3), só depois do plano |
| receptores | a entrada dos cérebros | a mesma regra; o que a tela mostra ao jogador é outra coisa (o jogador pode ver o motor) |
| o corpo em TypeScript | o G-PAR desta tarefa | o mesmo motor, sem tela até o produto voltar |
| medo, estresse, vínculo | medidos pela bancada | consequências que o jogador vê, depois da S-4 e da tela |

## 16. Decisões abertas

S-1, S-3, S-4, E-9 e E-10 estão decididos. Fica aberto (CD-9 e CD-10 vêm da revisão do tapa):

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| CD-1 | A escala da concentração | **C = 450000**, o mínimo múltiplo comum das taxas de hoje: todo número de hoje vira inteiro exato | uma potência de 2 pede acumuladores de resto em toda taxa: mais código e mais risco na paridade |
| CD-2 | O instinto (o P0) lê os drives novos? | **não**: os drives novos agem pelo sinal e pelas entradas do aprendiz; o P0 continua o instinto de hoje | lendo, o P0 muda e todo contraste muda de referência; e não se separa o que vem do corpo do que vem do aprendizado |
| CD-3 | A digestão entra na taxa C (instantânea) | **sim** no gate; a digestão lenta fica atrás do parâmetro, para o plano | lenta desde já: os drives de hoje mudam e o G-HOJE perde o sentido |
| CD-4 | O carinho vira sinal pelo corpo à última decisão; o cuidado do dono (alimentar, limpar, brincar) não | **sim**, como no N3 | creditar o cuidado ensina "o que eu fazia antes de comer é bom" (superstição) e mistura cuidado com ensino na medida; no Creatures toda redução reforça, e essa é a alternativa |
| CD-5 | O medo da mão como receptor do susto sobre a taxa do carinho | **sim**, com o parâmetro podendo ser 0 (a variante sem medo) | sem ele, o "medo da mão" só pode aparecer como aprendizado, e o #203 o descreve como efeito do corpo |
| CD-6 | O tapa gasta orçamento e conta como contato | **sim**, como o repreender de hoje | fora do orçamento, o dono que bate ganha interações de graça e os braços deixam de ser comparáveis |
| CD-7 | O estresse muda outra função (saúde, obediência) nesta tarefa | **não**: só é medido e entra no sinal; os efeitos ficam para a 1b | ligado já: o efeito do tapa no cuidado fica confundido com o mecanismo novo |
| CD-8 | A curiosidade exige o mundo físico | **sim**; sem ele, falha alto | sem o mundo, explorar não acha nada, e uma curiosidade que só sobe vira um castigo constante no sinal |
| CD-9 | O tapa credita só o sinal direto, sem somar a mudança que ele causa no corpo | **sim**: a dor e o estresse ficam no corpo e pesam depois | somando, o tapa pune duas vezes, e a força dele passa a depender do corpo de um jeito que nenhum número controla |
| CD-10 | O valor e o alcance do sinal do tapa | **o valor da bronca** (`recompensa_tapa` = `recompensa_repreensao`), **em toda fonte que aprende** | só na fonte dono: o pet do produto, que aprende pela consequência, não aprenderia nada com o tapa; com outro valor, o tapa deixa de ser comparável com a bronca da pesquisa |
