# Definições do corpo digital da V2

Escrito pelo coordenador em 2026-10-07, a partir da terceira revisão de literatura (`docs/referencias/G_REVISAO_CORPO_QUIMICO.md`), das
regras de `docs/referencias/REGRAS_CITACAO_DIGILAB.md`, da `docs/TAREFA_V2_CORPO_DRIVES.md` (CD-1 a CD-10), da `docs/TAREFA_V2_BANHEIRO.md`
e da `docs/futuro/ego_existencia.md`. **Só texto:** nenhum código, run, engine ou config mudou.

## Regras deste documento

- **Números:** nenhum número sem artefato. Os números do corpo citados aqui são parâmetros de `digilab/config.py` (`ConfigCorpo`), não
  resultados.
- **Referências:** nenhuma inventada. **SEM FONTE** marca o que é desenho nosso.
- **Quanto se pode citar:** depende de quanto foi lido. Só sustenta conteúdo o que a revisão leu em resumo ou texto. Os itens abaixo
  ficaram em "só metadados" ou "PDF obtido, não lido" e **não sustentam nenhuma afirmação de conteúdo** aqui:
  - `10.1023/A:1010042522104` (Grand & Cliff 1998);
  - `10.1007/s11538-006-9130-8` (Dittrich & Speroni di Fenizio 2007);
  - `10.1109/TCDS.2017.2775620` (Lones, Lewis & Cañamero 2018);
  - `10.1016/j.plrev.2019.07.005` (Hulme, Morville & Gutkin 2019);
  - `10.1016/j.neunet.2005.03.003` (Cañamero 2005);
  - `10.1631/jzus.C1000044` (Xu & Wang 2011);
  - `10.1162/978-0-262-32621-6-ch031` (Lones, Lewis & Cañamero 2014);
  - `10.1016/j.tics.2019.07.012` (Juechems & Summerfield 2019);
  - `10.1109/LRA.2016.2536360` (Kuehn & Haddadin 2016).
- **Fontes de fã:** Creatures Wiki, CDN e openc2e são pista, nunca evidência.
- **Novidade:** nada aqui afirma novidade.

**Uma contradição no pedido, declarada.** O item 2 pede o critério "fechado e automantido" com `10.1007/s11538-006-9130-8`. Esse PDF não
foi lido. Esta versão segue a regra mais restrita:
- o critério entra como **desenho nosso**, com a nota de que a sessão o atribuiu a essa referência;
- a referência não sustenta afirmação de conteúdo até alguém ler o artigo (decisão D-1, no fim).

---

## 1. Creatures: o que é fonte primária e o que é desenho nosso

### 1.1 O que a fonte primária sustenta (só os resumos)

- **Grand, Cliff e Malhotra 1997** (`10.1145/267658.267663`, resumo):
  - uma bioquímica artificial modela um metabolismo energético simples;
  - um sistema hormonal modula a atividade da rede neural e o desenvolvimento por estágios.
- **Cliff e Grand 1999** (`10.1162/106454699568683`, resumo):
  - a rede neural é recorrente e modular, com aprendizado hebbiano;
  - um sistema "hormonal" da bioquímica a modula de forma difusa;
  - a rede e a bioquímica são especificadas geneticamente.

A síntese da revisão também diz que receptores, emissores e drives como químicos estão confirmados. As frases de sustentação da tabela,
porém, não dizem isso explicitamente. Por isso eles ficam aqui como **a confirmar no texto**, e não como fonte (decisão D-2).

### 1.2 O que é desenho nosso (SEM FONTE primária)

| peça | onde está | status |
|---|---|---|
| drives como químicos de "falta" em inteiros, C = 450000 | `ConfigCorpo`, CD-1 | desenho nosso; o conceito vem do manual do Creatures 3, que não é fonte primária revisada |
| a digestão (estômago → reação limitada pela taxa) | `corpo.py`, seção 5 da tarefa | desenho nosso; o "metabolismo energético simples" de 1997 é o parente mais próximo, sem detalhe |
| a Vida como relógio químico com receptores de estágio | `corpo.py`, seção 6 | desenho nosso; "desenvolvimento por estágios modulado por hormônio" (1997, resumo) é compatível, mas não é a mesma peça |
| **força vital, dano, cura, energia de reparo e morte por órgão** | não existe | **SEM FONTE.** Só documentação de fã. Se entrar, entra como desenho nosso "inspirado no Creatures", nunca como "o que o Creatures faz" |

**Regra de texto:** em qualquer relato, só se escreve "o Creatures faz X" quando X está nas duas frases da seção 1.1. O resto é "nosso
corpo, inspirado no conceito do Creatures".

## 2. O grafo de reações como artefato validado antes da run

**A ideia:** o conjunto dos químicos, reações, receptores e emissores vira um **artefato declarado**, em código ou tabela. Uma checagem
estática o confere antes de qualquer run, como hoje se confere o sha256 do `engine.py`. A revisão diz que validar o grafo antes da run é a
salvaguarda transversal; a leitura é dela, e a recomendação, nossa.

**Os quatro riscos** são a leitura da sessão, **SEM FONTE** lida. Cada um ganha a checagem que lhe corresponde:

| risco | checagem estática proposta |
|---|---|
| 1. acúmulo sem sumidouro | todo químico tem pelo menos um caminho de consumo: uma reação que o gasta, uma meia-vida ou um teto explícito com descarte (o corte da digestão é um) |
| 2. laço de ganho ≥ 1 entre receptor e emissor | o grafo receptor → emissor não pode ter ciclo cujo produto de ganhos (em inteiros) seja ≥ 1; ciclos assim são recusados |
| 3. oscilação por meias-vidas próximas entre químicos acoplados | aviso, não recusa: pares acoplados com meias-vidas na mesma ordem são listados no relato da tarefa |
| 4. saturação em inteiro (o químico no teto deixa de responder) | todo químico com receptor de drive tem caminho de saída do teto; a run conta os ticks no teto por químico (medida, não gate) |

**O critério "fechado e automantido".** Fechado: nenhuma reação produz químico fora do conjunto declarado. Automantido: nenhum químico
consumido fica sem reposição ou sem teto declarado. Entra como **desenho nosso**, checável por inspeção do grafo. A sessão o atribuiu a
Dittrich & Speroni di Fenizio 2007 (`10.1007/s11538-006-9130-8`), mas o PDF não foi lido: não se cita o artigo como sustentação até a
leitura (D-1). Dittrich, Ziegler & Banzhaf 2001 (`10.1162/106454601753238636`, resumo) sustenta só que existe uma revisão do campo de
química artificial.

**Quando entra:** antes dos drives novos (etapa 6 da tarefa do corpo), que são o primeiro ponto em que o corpo ganha laços (estresse lê
os outros drives; o carinho reduz estresse e solidão).

## 3. Pesos dos drives que variam com o estado

**O que a literatura sustenta:**
- **Roijers et al. 2013** (`10.1613/jair.3987`, resumo): há cenários em que converter vários objetivos num escalar é impossível, inviável
  ou indesejável, e a taxonomia depende da função de escalarização.
- **Keramati e Gutkin 2014** (`10.7554/eLife.04811`, já verificado no projeto): a recompensa é a redução da distância do estado interno ao
  ponto de ajuste, o reforço homeostático em que o sinal do N3 se baseia.

**Leitura nossa (sem fonte nova):** o sinal da seção 9 da tarefa do corpo já é quadrático, `D = Σ w_d · falta_d²`. Nessa forma, o efeito
marginal de cada drive cresce com a própria falta (a derivada é `2 · w_d · falta_d`): um drive saciado já pesa menos que um drive em
falta, mesmo com os `w_d` fixos. Os pesos `w_d` (todos 1, PROPOSTOS) só dão a escala de cada drive; a dependência do estado vem da forma.

**O que muda a partir daqui:**
- **Não** se acrescenta um peso dinâmico por cima da forma quadrática antes de medir. O risco de "um drive dominar" deve ser medido,
  não presumido.
- **A medida (proposta para o plano do corpo):** em cada decisão com sinal, a fração de `D_antes − D_depois` que vem de cada drive. Um
  drive com essa fração alta na maior parte das decisões **domina**. O limiar entra no plano, escrito antes da run.
- **Se dominar:** a alternativa é um peso que depende de uma janela recente do drive. Ela entra como braço do plano, não como ajuste.

## 4. Três mecanismos hormonais e a ablação no basal

**A fonte:** sustenta só que um sistema hormonal da bioquímica modula a rede de forma difusa (Cliff e Grand 1999, resumo) e o
desenvolvimento (Grand, Cliff e Malhotra 1997, resumo). Lones, Lewis e Cañamero 2018 trata de hormônio modulando o desenvolvimento, mas o
PDF não foi lido e o artigo não sustenta conteúdo aqui. Maroto-Gómez et al. 2023 (`10.1002/aisy.202200288`, resumo) mostra substâncias
neuroendócrinas simuladas regulando processos autonômicos por longos períodos: é evidência de estabilidade num robô, não de efeito sobre
o aprendizado.

**Os três mecanismos (SEM FONTE; a lista é da sessão, como proposta),** do mais legível ao menos:

| mecanismo | onde age no nosso cérebro | o que um teste confere |
|---|---|---|
| H1. ganho sobre a leitura de um receptor | multiplica a entrada do receptor antes da decisão | com o hormônio no basal, a entrada é a de hoje byte a byte |
| H2. ganho sobre a taxa de aprendizado | multiplica o `passo` do aprendiz na atualização | com o hormônio no basal, os pesos aprendidos são os de hoje |
| H3. deslocamento do limiar de disparo | soma ao limiar de uma regra ou de um receptor de estágio | com o hormônio no basal, os limiares são os de hoje |

**Regra:** cada mecanismo entra sozinho, atrás de chave, com o hormônio no basal igual à vida de hoje (o G2 de sempre).

**A ablação "hormônio fixo no basal"** é obrigatória em todo plano que ligue um hormônio. Três medidas, contra o braço com o hormônio
livre:
1. a latência até a ação que reduz o drive afetado;
2. a taxa de aquisição: os sinais até a metade do caminho, pela `metrics.eficiencia_amostral`;
3. a variância entre episódios idênticos: a mesma unidade e o mesmo estado de partida, comparando sondas.

**Um hormônio que não move nenhuma das três** com IC fora de zero é **parâmetro morto** e sai. A regra é da sessão, adotada como nossa.

## 5. O modelo mínimo de órgão — SEM FONTE

**Nenhuma fonte primária localizada** descreve força vital, dano, cura e morte por órgão num agente que aprende. Bongard, Zykov e Lipson
2006 (`10.1126/science.1133687`, resumo) tem dano com consequência funcional e adaptação do automodelo, mas o dano é permanente: sem cura,
dor nem morte. Kuehn e Haddadin (só metadados) não sustenta nada. **Todo o modelo abaixo é desenho nosso**, por analogia com o conceito do
Creatures 3.

**O modelo (proposta, todos os números PROPOSTOS e em inteiros na escala C):**
- **Força vital:** cada órgão tem uma, `fv ∈ [0, C]`. O processo do órgão (a taxa da reação dele) é multiplicado por `fv / C`, pela
  aritmética inteira de sempre.
- **Dano:** subtrai de `fv`, vindo de um químico ou evento declarado no grafo (seção 2).
- **Cura:** soma a `fv` a uma taxa fixa por tick e consome energia (um químico declarado), para que curar custe.
- **Falência:** com `fv = 0` o processo para.
- **Morte:** a falência de um órgão declarado essencial.
- **Dor:** um químico emitido em proporção ao dano recente, com receptor.

**Regra:** com a chave dos órgãos desligada, ou com `fv = C` e sem dano, a vida é a de hoje byte a byte.

**As quatro medidas**, para separar "o dano ensinou" de "o dano matou" (do plano, escritas antes da run):
1. **Sobrevivência contra evitação aprendida.** Se a sobrevivência sobe sem cair a frequência da ação danosa, houve seleção (morreram
   os que faziam), não aprendizado.
2. **Latência até a primeira evitação,** medida em episódios de dano, comparada a quantos danos o pet suporta antes da falência.
3. **Generalização da evitação** para ações não punidas: quanto o pet passa a evitar ações vizinhas que nunca o feriram. É a medida do
   "medo excessivo".
4. **Custo de oportunidade da cura:** a fração da vida gasta curando, e o que o pet deixou de fazer nesse tempo.

## 6. O automodelo prevê as leituras dos receptores

**A fonte:**
- **Seth e Friston 2016** (`10.1098/rstb.2016.0007`, resumo): os estados corporais são regulados por reflexos subordinados a predições
  de modelos generativos do meio interno e externo. Dá o enquadramento.
- **Bongard, Zykov e Lipson 2006** (resumo): um robô infere a própria estrutura pelas relações entre atuação e sensação e revisa o
  automodelo depois do dano.

**A definição (desenho nosso, coerente com a E-1 de `docs/futuro/ego_existencia.md`):** o automodelo **prevê as leituras dos receptores**
que o pet recebe, na escala S. Ele não prevê o químico nem o `Estado` interno, que ficam com o motor e as sondas, como verdade fora da
rede.

**As três avaliações:**
1. **Predição a n passos:** o erro da rede, para cada n, contra duas linhas de base escritas antes:
   - a **persistência** (a leitura de agora prevê a de daqui a n);
   - a **média histórica** do receptor.

   Um automodelo que não bate a persistência **não sabe de si**: copia o presente. Essa é a linha de base obrigatória, e a regra é nossa.
2. **Transferência sob perturbação:** dano a um órgão (seção 5), quando existir. Mede o tempo até o erro de predição voltar ao nível de
   antes.
3. **Braço de utilidade:** a política que consulta o automodelo contra a mesma política sem ele, com a mesma capacidade. É o
   contraste que diz se o automodelo serve à decisão.

## 7. Estado de cada item

`EXECUTADO` = código na `main` com gates. `ESPECIFICADO` = escrito numa tarefa com decisões, sem código ou com código em curso.
`IDEIA` = só neste documento ou num `docs/futuro/`.

### 7.1 O inventário de 2026-10-24 (pela auditoria do código)

Feito na `main` `a06e19d` para o PROMPT MESTRE (`docs/AUDITORIA_V2_PRODUTO_MODULAR.md`, seção 5). É o estado que vale; a tabela da seção
7.2 fica como registro.

**Os estados:**
- **LIGADO-JOGO:** implementado e ligado ao comportamento no jogo (o pet v11, o `CCO_V11` em `web/app/motor/constantes.ts:468-472`) e na
  pesquisa;
- **LIGADO-PESQUISA:** implementado e ligado, só no Python;
- **NÃO INTEGRADO:** implementado, sem cérebro que o leia, ou fora do produto;
- **PROPOSTO** e **FUTURO.**

**A coluna "MVP"** diz se o sistema entra no primeiro produto jogável (`docs/TAREFA_V2_MVP_MUNDO_PRODUTO.md`). O MVP prioriza perceber a
comida, buscá-la, comê-la e refletir a consequência no corpo.

| sistema | entradas | estado | sinais ao cérebro | decisões que influencia | MVP | evidência | estado e próxima etapa |
|---|---|---|---|---|---|---|---|
| **Visão** (ambiental e social) | as posições do `Mundo`, num raio de 6 células; com a P4, o cone e a oclusão (`PercepcaoContrato`) | o registro dos vistos no motor | `PercepcaoMundo.vistos` (as entradas `bola` e `fruta`), `PercepcaoSocial` | os candidatos a alvo, o alvo padrão, o planejador, a novidade | **sim** (perceber a comida) | `tests/test_mundo*.py`; J1 (#285); J5 (#370) | LIGADO-PESQUISA; no jogo, pelo MVP |
| **Olfato alimentar** (a leitura pronta) | a intensidade do cheiro no mundo | — | `cheiro`, `direcao_cheiro` | o candidato `cheiro`; o explorar com cheiro forte | **sim** (achar a comida fora da vista) | runs do J1 e do J5 | LIGADO-PESQUISA; no jogo, pelo MVP |
| **Órgão do Olfato** (as narinas, DP-13) | a intensidade em cada narina | `adaptacao_<receptor>` | `olfato_comida[_esq/_dir]`, `olfato_outro[...]` | só o alvo, pelo motor; nenhum cérebro lê o receptor | não | `tests/test_orgaos.py`, `test_cheiro_orgao.py`; só o custo medido | NÃO INTEGRADO; um módulo M-SENS que o leia |
| **Tato cutâneo** (carinho e tapa) | os gestos do dono | `dor`, `susto`, `estresse`, `solidao`, `conforto`; o medo da mão | os receptores; o tapa pelo `receber_acao_dono` | o crédito à última decisão; as entradas do tempo livre | sim (já no jogo) | `tests/test_corpo_gestos.py`; web `laco_v11.test.ts` | LIGADO-JOGO |
| **Tato social** (o toque) | o outro pet | — | `toque_<tipo>` | as entradas sociais | não | `tests/test_grupo_social.py` | LIGADO-PESQUISA (dois pets) |
| **Paladar** | o perfil do tipo comido | `sabor_q`, `saciedade_q` | `paladar_*`; o canal `gosto` | as classes `comida:<tipo>`; o planejador | não no MVP (MV-3); depois, com as frutas | `tests/test_paladar_*.py`; o J5 com o `ganho_gosto` S/2 | LIGADO-PESQUISA; o TS é a etapa 5 do corpo |
| **Sistema digestivo e metabólico** (a digestão) | o alimento (a ração, a fruta) | `alimento`; a reação da digestão | nenhum receptor direto | indireto: a fome, a vontade, o combustível | **sim** (a consequência de comer) | `tests/test_corpo_digestao.py`; web `corpo.test.ts` | LIGADO-JOGO (indireto) |
| **Metabolismo energético** | o digerido e as atividades | `combustivel`, `reserva` | só pelo `energia` (a falta sobe o cansaço) | indireto, pelo cansaço | sim (já no jogo) | `tests/test_metabolismo.py`; o `m_gasto` 4/5 fechou (#293) | LIGADO-JOGO (indireto) |
| **Sistema neuroquímico** (fome, desconforto, cansaço, tristeza, dano) | as reações e os emissores | 5 químicos de falta, C = 450000 | `fome`, `higiene`, `energia`, `humor`, `saude` | as entradas da percepção; o `sinal_corpo` | **sim** (a fome que cai ao comer) | `tests/test_corpo*.py`; web `corpo.test.ts` | LIGADO-JOGO; **a validação do corpo não rodou** |
| **Homeostase** (o `sinal_corpo` por canal) | os receptores | — | o sinal de reforço por drive | o aprendizado | **sim** | o piloto do J2 (não é evidência) | LIGADO-JOGO |
| **Hormônios** H1 a H3 | — | — | — | — | não | — | PROPOSTO (D-6); o M-AFETO do modular |
| **Dor** (nocicepção) | o tapa | `dor`, com meia-vida 60 | o receptor `dor` | o sinal e as entradas | não | `tests/test_corpo_risco.py` | LIGADO-JOGO; o sistema nociceptivo e de reparo é FUTURO |
| **Saúde e dano** | a privação | `dano` | o receptor `saude` (entrada) | só como entrada | não | `tests/test_corpo*.py` | LIGADO-JOGO (entrada); o reparo, a força vital e a morte por órgão são FUTURO (J10) |
| **Sono e cansaço** | o dia, a noite, o andar, as atividades | `cansaco`; `Estado.dormindo` | `energia` | as regras de sono; a ação `dormir` | sim (já no jogo) | `tests/test_corpo*.py` | LIGADO-JOGO |
| **Sistema excretor** (o banheiro) | o tempo e o digerido | `vontade`, `conforto`; a necessidade no chão | `vontade`, `conforto` | o instinto do alívio; o alvo aprendido | não | `tests/test_banheiro_*.py`; **nenhuma run com artefato** | LIGADO-PESQUISA; o TS é a etapa 4 |
| **Tédio, solidão, estresse, susto** | o tempo, a variedade, os gestos | os químicos dos drives novos | os receptores novos (o susto fica fora do sinal) | o aprendizado | não (já no jogo) | `tests/test_corpo_drives.py`, `test_corpo_risco.py` | LIGADO-JOGO |
| **Curiosidade** | a novidade no mundo | o químico | o receptor | o aprendizado | não | `tests/test_corpo_drives.py` | LIGADO-PESQUISA (exige o mundo) |
| **Audição** (a leitura e os ouvidos, DP-14) | os sons do `Grupo` | `adaptacao_*` | `ouvido_<som>[...]` | nenhuma: nenhum cérebro lê | não | `tests/test_orgaos.py`, `test_sentidos_mundo.py` | NÃO INTEGRADO |
| **Relógio de desenvolvimento** (a Vida) | o tempo | `vida` | nenhum receptor | nenhuma: o motor só confere o estágio | não | `tests/test_corpo_vida.py` | NÃO INTEGRADO (por desenho) |
| **Digicorpo** (a rede de si) | todos os receptores | a rede que prevê | nenhum: só observa | nenhuma | não | `docs/RESULTADO_V2_CALIBRACAO_REDE_DE_SI.md` (margem negativa) | em desenvolvimento |
| **Proprioceptivo** | a direção do último passo (o gancho) | — | — | só põe as narinas e os ouvidos | não | — | PROPOSTO |
| **Termorregulação**; **imune e toxicológico** | — | — | — | — | não | — | FUTURO |

**O que o cérebro modular precisa receber, de forma explícita** (`docs/ARQUITETURA_DIGIBRAIN_MODULAR.md`, seção 2):
- **o M-SENS:** a visão e o olfato;
- **o M-AFETO:** os receptores do Sistema neuroquímico, dos drives novos, da dor e do susto;
- **o M-PLAST:** o sinal da homeostase.

A G-RECEPTOR continua: o cérebro só lê receptores e a percepção.

**A genética** poderá especificar os parâmetros da fisiologia no futuro (a seção `corpo` do `docs/futuro/ecossistema_genetico.md`). Hoje
nenhum gene muda as taxas do corpo.

### 7.2 A tabela de antes (até 2026-10-23), como registro

Ela ficou atrás do código: o Tato cutâneo, os drives novos, o Sistema excretor, o `MotorCorpo` e o sinal aparecem como ESPECIFICADO, mas
estão implementados.

| item | estado | onde |
|---|---|---|
| **Sistema neuroquímico:** a química dos drives de hoje (5 químicos, C = 450000, receptores na escala S) | **EXECUTADO** | W-CORPO-QUIMICA, `digilab/corpo.py`, `tests/test_corpo_quimica.py` |
| **Sistema digestivo e metabólico** (o órgão 1, a digestão) | **EXECUTADO** | W-CORPO-DIGESTAO (#225), `tests/test_corpo_digestao.py` |
| **Relógio de desenvolvimento** (o órgão 2, a Vida: relógio, estágio por receptor, sem morte) | **EXECUTADO** | #225, `tests/test_corpo_vida.py` |
| o corpo no motor (`MotorCorpo`, `consequencia_corpo`) | **ESPECIFICADO**, em curso (chat A, etapa 2) | `TAREFA_V2_CORPO_DRIVES.md`, seção 14 |
| o sinal pelo corpo (quadrático, `w_d` = 1) e os receptores do Sistema neuroquímico | **ESPECIFICADO** | seções 9 e 10 da tarefa do corpo |
| drives novos do Sistema neuroquímico (tédio pela variedade, curiosidade, solidão, estresse) | **ESPECIFICADO** | seções 7 e 17 (DS-4) |
| **Tato cutâneo:** carinho e tapa no corpo, sinal direto do tapa | **ESPECIFICADO** | seção 8, CD-4 a CD-10 |
| **Sistema excretor** (a vontade, o `aliviar`, a necessidade no chão) e o conforto do carinho (efeito do Tato cutâneo sobre o Sistema neuroquímico) | **ESPECIFICADO** | `TAREFA_V2_BANHEIRO.md` (BN-1 a BN-6) |
| a medida da dominância de um drive (seção 3) | **IDEIA** | este documento |
| o validador estático do grafo de reações (seção 2) | **IDEIA** | este documento |
| os três mecanismos hormonais e a ablação no basal (seção 4) | **IDEIA** | este documento |
| órgãos com força vital, dano, cura, dor e morte (seção 5) | **IDEIA**, SEM FONTE | este documento |
| o automodelo que prevê os receptores, o **Digicorpo** (seção 6) | **IDEIA** (objetivo DECIDIDO, E-1; o como é PROPOSTO) | `docs/futuro/ego_existencia.md` e este documento |
| o órgão receptor do **Olfato** (alimentar e social): receptor com limiar, adaptação e saturação, só a intensidade local, uma ou duas narinas (DP-13) | **ESPECIFICADO**: DP-13 DECIDIDA em 2026-10-11, duas narinas, atrás de chave desligada | `docs/futuro/dois_pets.md`, seção 5.6; `docs/TAREFA_V2_DOIS_PETS.md`, etapa 8b |
| o órgão receptor da **Audição social**, o mesmo desenho (DP-14) | **ESPECIFICADO**: DP-14 DECIDIDA em 2026-10-11, dois ouvidos, atrás de chave desligada | idem |
| os sistemas a acrescentar: Metabolismo energético, proprioceptivo, Termorregulação, nociceptivo e de reparo, imune e toxicológico, reprodutivo | **IDEIA**, cada um com a condição de entrada | seção 8.1 |

**Um apoio que já existe:** o conforto do carinho (BN-6) é o item que a literatura lida mais apoia. Lewis e Cañamero 2016
(`10.1177/1059712316666331`, resumo) mostram que um prazer não ligado à satisfação de uma necessidade melhorou a viabilidade e a
flexibilidade de um robô. É um estudo, num robô.

## 8. Nomes dos sistemas do corpo

**Os nomes de trabalho** foram dados pelo Matheus em 2026-10-08. Eles valem nos documentos.

**O código não muda:** identificadores, eventos, campos do registro, chaves de config, nomes de arquivo e prefixos de sementes continuam os
de antes, porque mudá-los quebraria os gabaritos e o G2. Este glossário faz a ponte entre o nome do documento e o nome do código.

**Os sistemas que existem ou estão desenhados:**

| nome de trabalho | o que é hoje no código | estado |
|---|---|---|
| **Sistema neuroquímico** | a química dos drives: os químicos `fome`, `desconforto`, `cansaco`, `tristeza` e `dano` (`corpo.QUIMICOS`) e, com a etapa 6, `tedio`, `curiosidade`, `solidao`, `estresse`, os receptores na escala S e o grafo de reações (`corpo.grafo_do_corpo`) | **EXECUTADO** (a química e o grafo); os drives novos ESPECIFICADOS e em código na etapa 6 |
| **Sistema digestivo e metabólico** | o órgão 1, a digestão: o químico `alimento`, a reação com a fome limitada por `taxa_digestao`, o descarte, `digerido_no_tick` (sub-chave `digestao`) | **EXECUTADO** |
| **Relógio de desenvolvimento** | o órgão 2, a Vida: o químico `vida`, que decai e dá o estágio por receptor, sem morte (sub-chave `vida`) | **EXECUTADO** |
| **Visão ambiental** | a visão do mundo físico: `PercepcaoMundo` (os objetos vistos a até 6 células, a região, a posição) | **EXECUTADO** |
| **Olfato alimentar** | o cheiro da comida: `mundo.cheiro_em` e `direcao_do_cheiro`, em `PercepcaoMundo.cheiro` e `direcao_cheiro`; com a DP-13, o receptor com a sub-chave `comida` | a leitura pronta **EXECUTADA**; o órgão é ESPECIFICADO (DP-13 DECIDIDA em 2026-10-11: duas narinas, atrás de chave desligada) |
| **Tato cutâneo** | o carinho e o tapa no corpo: `acao_dono(ACARICIAR)` e `acao_dono(TAPA)`, os químicos `dor` e `susto` e o medo da mão (sub-chave `gestos`) | **ESPECIFICADO**, em código na etapa 6 |
| **Visão social** e **Tato social** | a visão e o toque do outro pet: `Observacao.social` (`PercepcaoSocial`, os campos `outros`, `onde_comeu` e `toque`) | **ESPECIFICADO** (`docs/futuro/dois_pets.md`, seções 5.1 e 5.2; etapa 3 da tarefa) |
| **Audição social** e **Olfato social** | a audição e o cheiro do outro pet, no degrau 1b. **O rastro é um sinal olfativo social:** as marcas que o corpo emite no mundo por um emissor externo | **ESPECIFICADO** (seções 5.3 e 5.4; etapa 8) |
| **Quimiossinal de estado** | o cheiro de estresse e de medo: um emissor externo que lê um químico do próprio corpo, com ganho declarado no grafo | **ESPECIFICADO** para o degrau 3 (DP-12) |
| **Sistema excretor** | o banheiro: o químico `vontade`, a ação `aliviar` (`AcaoPet.ALIVIAR`), a necessidade no chão e o desconforto dela (`estimulo_necessidade`, o `passo(..., necessidades=n)`) (sub-chave `banheiro`) | **ESPECIFICADO**; etapa 2 em código (`TAREFA_V2_BANHEIRO.md`) |
| **Digicorpo** | a rede de si: o modelo corporal que prevê os receptores (`digilab/rede_de_si.py`, `PoliticaComRede`, o prefixo `rede_de_si`) | **ESPECIFICADO** (`TAREFA_V2_REDE_DE_SI.md`; RS-1 a RS-7 decididas) |

**Duas notas:**
- **O conforto do carinho (BN-6)** é o químico `conforto`, que o carinho sobe. Ele é descrito como **efeito do Tato cutâneo sobre o
  Sistema neuroquímico**, e não do Sistema excretor, embora tenha entrado com a tarefa do banheiro.
- **O nariz e o ouvido da DP-13 e da DP-14** (`docs/futuro/dois_pets.md`, seção 5.6) são os **órgãos receptores** do Olfato (alimentar e
  social) e da Audição social. Com a chave desligada, o Olfato alimentar segue sendo a leitura pronta de hoje.

**A cabeça da autoria.** O Digicorpo é o modelo corporal. A rede de si da tarefa tem também a cabeça da autoria, que prevê a própria
escolha. Neste documento, as duas cabeças ficam no Digicorpo, porque são o mesmo módulo e o mesmo aprendizado. Se a autoria pede nome
próprio fica para o Matheus (N-1, nas decisões abaixo).

### 8.1 Sistemas a acrescentar (IDEIA, nesta ordem)

Cada um só entra quando a condição de entrada valer, com tarefa e gate próprios. Tudo é SEM FONTE, salvo onde a revisão conferir, e não há
alegação de novidade: o Creatures modelou corpo químico e órgãos em 1997 (seção 1).

| # | sistema | o que faria | condição de entrada | o que já existe |
|---|---|---|---|---|
| 1 | **Metabolismo energético** (conversão, armazenamento, mobilização; **implementado e ligado no jogo desde o J2**, nota de 2026-10-24, seção 7.1) | a energia como químico: o alimento digerido vira reserva, e a reserva é mobilizada quando o corpo gasta | **avaliar antes** se entra como reações novas no grafo **sem duplicar o cansaço** | **A verificação do Gerente, conferida em `corpo.py` (2026-10-08):** não há químico de energia. A digestão consome `alimento` e `fome` (e, com o banheiro, produz `vontade`). O `cansaco` sobe por emissores (acordado de dia, acordado à noite, o andar) e cai dormindo. Não há conversão nem reserva |
| 2 | **Sistema proprioceptivo** (postura, orientação, movimento) | o pet sente a própria posição e o próprio movimento | quando houver movimento corporal relevante | a direção do último passo, que a opção (b) da DP-13 usa para pôr as narinas |
| 3 | **Termorregulação** | o calor e o frio do corpo | só se o mundo tiver temperatura | nada |
| 4 | **Sistema nociceptivo e de reparo** | a dor, o dano e a cura do corpo como um sistema | unir à seção 5 (os órgãos com força vital, dano e cura), **depois da D-5** | os químicos `dano`, `dor` e `susto`; os emissores `dano_privacao` e `dano_cura`; o tapa |
| 5 | **Sistema imune e toxicológico** | o corpo que reage a toxina ou a patógeno | depois de haver toxina ou patógeno no mundo | a comida podre (o efeito no humor) é o gancho |
| 6 | **Sistema reprodutivo** | o ciclo reprodutivo no corpo | quando o ciclo de vida e a herança forem trabalhados | a herança da v4 no jogo, fora do corpo |

**Os nomes da seção 7** são os deste glossário; a seção 7 os usa desde 2026-10-08.

---

## Decisões que só o Matheus pode tomar

**D-1 a D-7: DECIDIDAS pelo Matheus em 2026-10-07, todas pela recomendação** ("faz o merge e segue as recomendações").
**N-1: DECIDIDA em 2026-10-11, pela recomendação:** a cabeça da autoria fica no Digicorpo.
- D-1 e D-2: a quarta passada do Claude Science (`docs/TAREFA_V2_CLAUDE_SCIENCE_LITERATURA_4.md`).
- D-3: a seção 18 da `docs/TAREFA_V2_CORPO_DRIVES.md`.
- D-4: a medida de dominância vai a um adendo do plano do corpo (chat C) e às medidas da bancada (chat D).
- D-5 e D-6: só ordem, sem tarefa agora.
- D-7: regra para o plano do automodelo, quando ele existir.

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| D-1 | Ler o PDF de Dittrich & Speroni di Fenizio 2007 (e o de Lones et al. 2018) antes de citá-los, ou seguir sem eles | **ler antes.** Até lá, o critério "fechado e automantido" fica como desenho nosso, sem citação | citar sem ler põe na boca do artigo algo que ele talvez não diga; não citar só custa a atribuição |
| D-2 | Pedir a leitura do texto completo de Grand, Cliff e Malhotra 1997 para confirmar receptores, emissores, meias-vidas e drives como químicos | **sim**, numa próxima passada do Claude Science (DECIDIDO) | sem isso, "nosso corpo segue o Creatures" fica sustentado só por duas frases de resumo e pelo manual |
| D-3 | Adotar o grafo de reações como artefato validado antes da run (seção 2), antes da etapa 6 | **sim**, como tarefa curta do B junto com a etapa 6 | sem ele, um laço de ganho ≥ 1 ou um químico sem sumidouro aparece só na run, e a calibração tenta compensar um defeito de estrutura |
| D-4 | Manter os `w_d` fixos e medir a dominância (seção 3), em vez de pôr peso dinâmico já | **manter fixos e medir** | peso dinâmico sem medida é mais um parâmetro livre; se a dominância existir e não for medida, o corpo vira um drive só |
| D-5 | Abrir a frente dos órgãos com dano, cura e morte (seção 5) agora ou depois dos drives novos | **depois** dos drives novos, do banheiro e do mundo na bancada, com plano próprio e as quatro medidas | abrir agora mistura três mecânicas novas na mesma run, e um "aprendeu a evitar" não se separa de "morreram os que não evitavam" |
| D-6 | Hormônios (seção 4): quando e qual mecanismo primeiro | **depois** dos órgãos, começando pelo H1 (ganho no receptor), sempre com a ablação no basal | ligar os três juntos torna o sistema opaco, e um hormônio morto fica no código como parâmetro sem efeito |
| D-7 | O automodelo (seção 6) avaliado contra a persistência como linha de base obrigatória | **sim**, escrito no plano antes da run | sem a persistência, um modelo que copia o presente parece "saber de si" |
| N-1 | A cabeça da autoria da rede de si: fica no Digicorpo ou ganha nome próprio (seção 8) | **fica no Digicorpo** enquanto as duas cabeças forem o mesmo módulo e o mesmo aprendizado | um nome próprio cedo demais separa nos documentos o que o código não separa, e o glossário passa a apontar dois nomes para um arquivo |
