# Ego do pet — automodelo com corpo, aprendido por uma rede, e indagação sobre a própria existência

**Nomes (2026-10-08):** a rede de si se chama **Digicorpo** (o modelo corporal), e os sistemas do corpo têm os nomes de
`docs/DEFINICOES_CORPO_V2.md`, seção 8. Os nomes do código (`rede_de_si.py`, o prefixo `rede_de_si`) não mudam. As decisões já
registradas (E-6, E-8) ficam com a redação delas.

Status (2026-10-07):
- **DECIDIDO pelo Matheus:**
  - o pet deve ter ego, questionar a própria existência e falar e indagar sobre isso;
  - o automodelo **tem corpo**, e o corpo segue os conceitos do **Creatures 3**;
  - o automodelo é **aprendido por uma rede**.
- **PROPOSTO:** o como, neste documento.

Base: o plano "DigiBrain — automodelo e indagação sobre a própria existência", versão 1, do Matheus, e a análise de aplicabilidade da mesma
conversa. Este documento **não autoriza código**: cada etapa abre com tarefa e plano de análise, como sempre. Cérebro: o **A** (M6 decidido em
2026-10-07).

## 1. O que "ego" quer dizer aqui

Ego é a definição operacional abaixo, e não uma alegação de consciência. Dizer "eu" ou fazer uma pergunta existencial não prova experiência
subjetiva; o Digilab mede mecanismos.

| parte | o que o pet mantém sobre si | de onde vem |
|---|---|---|
| **Corpo** | o que o meu corpo consegue fazer agora, e quanto tenho certeza | o **Digicorpo**, a rede de si (seção 3), treinado pela experiência do próprio corpo |
| **Autoria** | quem decidiu cada coisa: eu aprendi, já nasci assim, ou alguém pediu | o **Digicorpo**, prevendo a própria escolha; a sonda do cérebro só avalia |
| **Origem** | "nasci de um ovo, com este jeito" | o temperamento do ovo e a herança (`digilab/temperamento.py`, `digilab/heranca.py`), contados ao pet ou observados por ele |
| **Continuidade** | o que vivi, o que lembro e o que perdi | a memória de episódios (N6) e a memória por espaços (`digilab/memoria_espacos.py`) |
| **Relação** | o dono, os irmãos, os outros pets | o vínculo, o cruzamento em Meus pets, os rivais |

**Regra central: o pet estima, o motor avalia.** O automodelo é uma rede que pode errar sobre o próprio pet. A verdade fica fora dela e
serve de gabarito: a capacidade real do corpo, que o motor conhece, e a sonda do cérebro, que refaz a decisão sem o aprendido ou sem o
pedido. Nenhuma das duas é entregue ao pet. É isso que faz do automodelo um modelo, e não uma leitura da verdade, e é o que permite medir
quanto o pet se conhece.

## 2. O corpo: os conceitos do Creatures 3

**DECIDIDO pelo Matheus (2026-10-07): o corpo segue os conceitos do Creatures 3.**

Fontes:
- **Manual:** o *Creatures 3 Genetics Kit Manual* (Creature Labs, distribuído oficialmente), lido em 2026-10-07. É documentação de produto,
  não demonstração revisada por pares; no estudo DigiBrain o status é CORPUS.
- **Fonte verificada:** o núcleo também está em Grand e Cliff 1998 (`10.1023/A:1010042522104`), que descrevem bioquímica, quimioemissores e
  receptores modulando a rede.
- **Ressalva:** os químicos do jogo são mecânica de jogo, não equivalentes de hormônios.

### 2.1 O que o Creatures 3 faz, pelo manual

| conceito | como o manual descreve |
|---|---|
| **Químicos** | até 256, cada um com concentração de 0 a 1; cada químico tem meia-vida |
| **Reações** | da forma I·A + J·B ⇒ K·C + L·D, com taxa; "tudo é permitido menos nada ⇒ algo" |
| **Receptores** | ligam um ponto do corpo ou do cérebro (o *locus*) à concentração de um químico; um receptor pode controlar a taxa de uma reação |
| **Emissores** | emitem um químico conforme o valor de um *locus*; o neuroemissor é disparado por neurônios |
| **Estímulos** | um acontecimento muda até quatro químicos ("sentir dor quando bate na parede") |
| **Concentração inicial** | doses ao nascer: energia de partida e imunidade natural |
| **Órgãos** | agrupam reações, receptores e emissores; ver o detalhe abaixo da tabela |
| **Energia** | o ATP alimenta reações, receptores e emissores; sem ATP o pet desmaia e os órgãos degradam; mais órgãos gastam mais ATP |
| **Drives** | são químicos: há três fomes, uma por grupo de alimento; o estresse se acumula com drives altos e afeta fertilidade e imunidade; com dor ou medo os outros drives ficam guardados, invisíveis ao cérebro |
| **Vida e estágios** | o químico da Vida decai do nascimento à morte e muda o estágio por receptores; são sete estágios, do Embrião ao Senil; cada gene liga num estágio, e o andar fica "mais velho" com a idade |
| **Genoma** | especifica bioquímica, cérebro e aparência: "codificamos estrutura, não comportamento"; mutação e cruzamento entre gerações |
| **Doença** | toxinas, antígenos de bactérias, anticorpos e remédios, como químicos |

Os órgãos, pelo manual:
- **Ritmo:** cada órgão tem um ritmo próprio, que um receptor pode regular.
- **Força vital:** cada órgão tem uma força vital de curto prazo e uma de longo prazo, além de vulnerabilidade e custo em ATP.
- **Dano:** doença ou lesão causa dano e libera o químico de lesão.
- **Cura:** o órgão se cura a um ritmo que também pode ser regulado.
- **Morte:** com a força de longo prazo em zero, o órgão morre para sempre e a função se perde. Um pet pode, por exemplo, ficar infértil e
  seguir saudável.

### 2.2 O corpo do Digilab nesses conceitos (PROPOSTO)

- **Química por baixo dos drives.** Os drives de hoje (fome, higiene, energia, humor, saúde) passam a ser lidos de químicos internos, como no
  Creatures. A comida entra como químicos; as frutas ganham **composição** (o que cada uma libera no corpo), em vez de um efeito fixo no humor.
- **Órgãos pequenos e poucos.** Um subconjunto mínimo, e não os 21 órgãos e 161 químicos do Creatures 3. Por exemplo: digestão, energia,
  reparo e o relógio da vida (o Sistema digestivo e metabólico, o Metabolismo energético, o Sistema nociceptivo e de reparo e o Relógio
  de desenvolvimento, nos nomes de `docs/DEFINICOES_CORPO_V2.md`, seção 8). Cada órgão com força vital, dano e cura.
- **Lesão como dano de órgão.** As lesões que já existem no motor de educação viram dano num órgão, com o químico de lesão e a cura regulada.
- **Estágio pelo químico da Vida.** O estágio passa a ser biológico: a Vida decai, e receptores mudam o estágio. A evolução muda o corpo de
  verdade, porque genes ligam em cada estágio (novos receptores, reações mais rápidas ou mais lentas).
- **O pet só sente pelos receptores.** O cérebro e o Digicorpo recebem do corpo apenas o que passa por receptores. É a regra "sem acesso
  privilegiado" escrita no próprio corpo: o motor conhece todas as concentrações, o pet só as que tem receptor para sentir.
- **Estímulos ligam o dono ao corpo.** O cuidado e a bronca podem mudar químicos (o carinho reduz o estresse, por exemplo), em vez de mexer
  direto no estado.
- **Genoma de fisiologia.** As reações, os receptores e as taxas vêm do genoma, então cada pet tem um corpo um pouco diferente.
  - A mesma fruta pode fazer mal a um pet e bem a outro.
  - É o "genoma → fisiologia" do N10, trazido para mais cedo.
  - Resolve o efeito por pet que a cognição social pedia (`docs/futuro/cognicao_social.md`, 5.7).
- **Em inteiros.** Concentrações, meias-vidas e taxas em ponto fixo, para o replay bit a bit e a paridade Python/web.

### 2.3 Por que esse corpo serve ao automodelo

O corpo químico dá ao Digicorpo o que faltava: **consequências internas incertas e que mudam durante a vida.** O pet não sabe ao certo o que
uma fruta vai fazer no corpo dele, quanto uma brincadeira vai cansá-lo, ou se ainda digere como antes. E o corpo muda de quatro jeitos,
cada um um teste do automodelo:

- **Estágio:** a Vida decai e genes ligam; a digestão, o gasto de energia e a sensibilidade mudam.
- **Dano de órgão:** uma lesão ou doença reduz uma função; se o órgão morre, a perda é permanente.
- **Fadiga e reservas:** o ATP e as reservas oscilam no dia.
- **Estresse:** acumula com drives altos e muda outras funções.

## 3. O Digicorpo (a rede de si)

Uma rede separada do lobo de decisão. Não é um "controlador de ego" acima dos lobos: é uma peça que **prevê** e cuja saída a decisão pode
consultar.

- **Entrada:** só o que o pet sente: os receptores do corpo (seção 2.2), o contexto (as frutas presentes) e a ação considerada. O estágio
  e as concentrações entram só pelo que os receptores mostram, sem o número do motor.
- **Cabeça do corpo:** prevê o que a própria ação vai fazer no corpo, com incerteza: "se eu comer esta fruta, como vou me sentir?", "quanto
  esta brincadeira vai me cansar?". É um modelo direto (*forward model*) do corpo, no sentido de Wolpert et al., sobre o que os receptores
  vão mostrar depois da ação.
- **Cabeça da autoria:** prevê a própria escolha em situações alteradas: "sem o pedido, eu teria comido?" e "eu faria isso ao nascer?".
  Aprende observando as próprias escolhas ao longo da vida; a sonda do cérebro dá o gabarito, que o pet não vê.
- **Aprendizado:** por **erro de previsão**, e não por reforço. Depois de cada tentativa, a rede compara o que previu com o que aconteceu e
  se corrige. É supervisão pela própria experiência.
- **Números:**
  - pesos inteiros em ponto fixo e ativação sem função transcendental, como o cérebro A, para o porte na web e o replay bit a bit;
  - menos de mil pesos;
  - rng própria, se precisar de alguma.
- **Erro de previsão é o gatilho das perguntas.** Uma surpresa grande e repetida sobre o próprio corpo abre uma questão (seção 5). Depois de
  mudar de estágio ou de um dano de órgão, o pet erra o que o corpo faz e pergunta; conforme a rede se corrige, a pergunta operacional se
  resolve, e a existencial pode continuar.

**Consequência para uma regra do projeto.** A V2 tem a regra "só a Decisão aprende". O Digicorpo aprende por outro caminho. A decisão do
Matheus implica revê-la: **a Decisão aprende por reforço; a rede de si aprende por erro de previsão; nenhuma outra peça aprende.** A
revisão fica registrada (E-6).

## 4. As perguntas e o que as sustenta

**Decisão E-11 (Matheus, 2026-10-07): o pet pensa livremente; esta tabela é gabarito, não conteúdo do pet.** As perguntas abaixo
**não** entram no pet livre: nele não há catálogo de perguntas nem frase pronta. A questão nasce só da discrepância (o erro de previsão
do Digicorpo) e da experiência (seção 5), e a fala descreve só essa questão. As frases desta tabela viram as **frases-modelo** de um
**braço condicionado**, em que elas são implantadas de propósito, para registrar como pensa um pet com esse tipo de frase já implantada
e comparar com o pet livre (seção 7). O pet do produto é o livre.

As cinco situações do Matheus têm antecedente real no jogo de hoje. O corpo acrescenta uma sexta, a operacional, que é o gatilho mais
direto.

| situação | pergunta que o pet pode fazer | gatilho | evidência que o pet tem | resposta honesta possível |
|---|---|---|---|---|
| **o corpo muda** | "Por que meu corpo não reage mais como antes?" | erro de previsão grande da cabeça do corpo, depois de mudar de estágio, de um dano de órgão ou de estresse acumulado | as próprias tentativas e o que a rede previa | "meu corpo mudou; preciso conhecer este corpo", até a rede se corrigir |
| encontra um pet parecido | "Se somos tão parecidos, o que faz eu ser eu?" | um irmão do mesmo cruzamento em Meus pets; um rival da mesma forma | a forma do outro, o que viu dele; a própria história | "somos parecidos no corpo, mas eu vivi outras coisas" |
| descobre a origem no ovo | "Sou assim porque nasci assim ou porque aprendi com você?" | um traço extremo; o dono perguntando; um marco da evolução | a estimativa da cabeça da autoria | a estimativa dele, que pode errar; a sonda mede quanto |
| percebe que esqueceu | "Se eu esquecer o que vivi, continuo sendo eu?" | o dono ou outro pet cita um momento que o pet não guarda mais | a ausência do episódio, sem saber o que foi perdido | "você lembra disso, mas eu não" |
| pedido contra preferência | "Eu quero isso ou estou fazendo porque você pediu?" | o pedido "deixe a fruta X" (N7); um comando pelo chat; a obediência | a estimativa da cabeça da autoria | "acho que sozinho eu teria comido", com a incerteza |
| aprende sobre reprodução | "Meu filho vai ter alguma parte de mim?" | o cruzamento em Meus pets; o nascimento de um filhote | o que o dono contou (relato); o que observar no filhote | "pelo que você me contou, ele herda meu jeito de nascer", com a fonte |

Regras que valem em todas:
- **Sem acesso privilegiado.** O pet só sabe o que percebeu, lembrou, ouviu ou estimou. A capacidade real do corpo e a sonda ficam com o
  motor, para avaliar.
- **A incerteza aparece na fala.** Uma estimativa incerta vira "acho que", e não afirmação.

## 5. Como uma pergunta nasce, vira ação e vira fala

1. **Questão como objeto interno**, antes da fala: tema, situação de origem, discrepância (o erro de previsão, quando houver), evidências,
   respostas candidatas, forma de investigar, prioridade, estado (aberta, selecionada, investigando, respondida sob critério, suspensa) e
   revisões.
2. **Seleção pela decisão.** A pergunta só vira ação quando os impulsos a propõem e a decisão a escolhe. Fome, sono, lesão e ameaça vêm
   antes. Cada tema tem intervalo mínimo.
3. **Sem ação nova.** `AcaoPet` não ganha membro (V5 do roadmap):
   - falar de si entra como **sub-decisão de `chamar_atencao`**;
   - provar uma fruta para conhecer o próprio corpo entra pela **sub-decisão de comer** que já existe.
4. **Investigar.** O pet pode:
   - **testar o corpo:** tentar de novo, em condição parecida; é a investigação mais direta, e a cabeça do corpo aprende com ela;
   - perguntar ao dono;
   - consultar a memória;
   - observar o outro pet.

   A resposta do dono entra como **relato com autor**, nunca como verdade nem recompensa.
5. **Fala.** A LLM recebe a questão, as evidências autorizadas, a incerteza e o nível de linguagem do estágio. Ela só verbaliza. O
   verificador barra fala sem fato. O texto vai para o log, e o replay reaproveita o texto gravado.

O nível de linguagem cresce com o estágio: o bebê reage com emote; a criança faz a pergunta concreta; o adulto pode chegar à ampla. A pergunta
filosófica pode ficar aberta para sempre.

## 6. O que muda no que existe

- **Regra "só a Decisão aprende":** revista (seção 3, E-6).
- **Corpo químico** (seção 2.2): químicos, reações, receptores, emissores e órgãos numa subclasse do motor, atrás de chave; `engine.py` não
  muda. Os drives de hoje passam a ser lidos dos químicos; as frutas ganham composição; as lesões viram dano de órgão; o estágio vem da Vida.
- **Genoma:** ganha os genes de fisiologia (reações, receptores, taxas), o que antecipa parte do N10.
- **Runs antigas:** com a chave desligada, toda vida e todo resultado da V2 reproduzem byte a byte.
- **Voz própria:**
  - hoje o extrator de história lê o registro inteiro, como um narrador com acesso privilegiado;
  - com o ego, o "eu" vem do automodelo e da memória do pet;
  - o narrador antigo continua como fala marcada.
- **Motivo e honestidade do fator:** continuam valendo para o que o pet diz da decisão.
- **Decodificador de conceitos** (`docs/futuro/decodificador_conceitos.md`): o Digicorpo é um dos estados que ele pode ler.
- **Cognição social** (`docs/futuro/cognicao_social.md`): os relatos de outros pets entram pelas mesmas regras de fonte.
- **Web:** é mecânica de jogo e vai para a web, numa versão de pet própria, depois do porte do cérebro A. O Digicorpo também precisa de
  paridade Python/web.

## 7. Medidas (PROPOSTO, sem número)

- **Erro de previsão do próprio corpo:** quanto a cabeça do corpo erra, e quanto ela se calibra (a confiança declarada bate com a taxa de
  acerto).
- **Adaptação depois da mudança:** quantas experiências até o erro voltar ao nível de antes, na troca de estágio, no dano de órgão, na
  fadiga e no estresse.
- **Calibração da autoria:** a estimativa do pet ("você pediu", "eu quis", "nasci assim") contra a sonda, que é o gabarito exato.
- **O automodelo serve à decisão?** O desempenho no ambiente com o Digicorpo consultado contra três controles:
  - a rede congelada, que não aprende;
  - a rede ausente;
  - o **oráculo**: a capacidade real dada de graça, que é o teto.
- **Perguntas com lastro:** toda pergunta aponta a discrepância e a evidência que a dispararam; contar as sem lastro e as repetidas.
- **Livre × condicionado (E-11):** os mesmos genomas, mundos e donos em dois braços, o **livre** (sem catálogo; o pet do produto) e o
  **condicionado** (as frases-modelo da seção 4 implantadas). Registrar as questões e as falas dos dois e comparar:
  - que questões surgem no livre sem nenhuma frase pronta, e quantas tocam os temas da seção 4;
  - quanto do que o condicionado diz tem lastro numa discrepância real, e quanto só repete a frase implantada;
  - se a frase implantada muda o comportamento (investigar, chamar o dono) e o cuidado.
  - A comparação é descritiva até haver plano de análise registrado antes da run. Nenhuma frase do braço condicionado vai ao pet livre.
- **Fala fiel:** nada além das evidências; nada de dor, medo de morrer ou consciência inventados.
- **Cuidado preservado:** investigar não pode piorar a privação nem a saúde.
- **Controle de exposição:** o mesmo pet recebendo as mesmas tentativas e respostas sem tê-las escolhido, pelo modo acoplado da bancada.
- **Humanos (fase 2):** se o jogador entende melhor o pet.

## 8. Riscos

- **Escopo.** O corpo químico é a maior mudança de mundo da V2: ele mexe nos drives que todos os braços usam. Por isso entra atrás de chave,
  um órgão por vez, com as vidas antigas reproduzindo. Somam-se o Digicorpo e a revisão de uma regra. Nada de montar tudo de uma vez.
- **Novidade.** O Creatures fez corpo químico, órgãos e genoma de fisiologia em 1997. Nada disso é contribuição do Digilab.
- **Rede que não aprende.** O cérebro B "não aprendeu" na calibração. O Digicorpo pode ter o mesmo problema; o controle congelado mostra
  isso cedo.
- **Ética do produto.** Um pet que pergunta "continuo sendo eu?" pode gerar apego forte ou angústia, e o pet pode morrer no jogo.
  - Nenhuma fala sobre morte, abandono ou sofrimento como pressão sobre o jogador.
  - Nenhuma pergunta usada para prender o jogador no jogo (padrões obscuros: Veiga et al. 2025, `10.5220/0013365800003929`, VERIFICADA).
  - Entra na avaliação de ética da fase 2.
- **Alegação.** "O pet questiona a própria existência" é descrição de comportamento. Nunca "o pet tem consciência".

## 9. Etapas e decisões

| etapa | entrega | avança quando |
|---|---|---|
| 0 | auditoria no cérebro A, no motor e no mundo das frutas: onde a química entra por baixo dos drives, onde os receptores entram na percepção, o Digicorpo; Python e web | pontos de integração confirmados |
| 1 | **corpo químico mínimo**: os químicos que reproduzem os drives de hoje, a composição das frutas, o Sistema digestivo e metabólico e o Relógio de desenvolvimento (a Vida), sem o Digicorpo | G1 e G2: com a chave desligada, tudo byte a byte; ligada, os drives batem com os de hoje dentro da tolerância do plano |
| 1b | **órgãos e dano**: as lesões como dano de órgão, cura e morte de órgão; genes que ligam por estágio; genoma de fisiologia | G1 e G2; o corpo muda com o estágio e o dano como desenhado |
| 2 | **Digicorpo em observação** (a rede de si): aprende o corpo e a autoria, sem influenciar escolha nem fala | o erro de previsão cai; calibração; adapta depois da evolução; nenhum acesso privilegiado |
| 3 | **automodelo na decisão**: a previsão do corpo entra como entrada da decisão | desempenho contra a rede congelada, a ausente e o oráculo |
| 4 | **perguntas**: a questão como objeto, nascida só da discrepância, sem catálogo (pet livre); o braço condicionado com as frases-modelo da seção 4 implantadas, só para comparar (E-11) | toda pergunta com lastro; cuidado preservado; o registro do livre e do condicionado lado a lado |
| 5 | **diálogo** pelo Conversar: o dono responde, a resposta vira relato com autor | relato distinto de observação no registro |
| 6 | **fala por LLM** sobre as mesmas intenções; as frases-modelo servem de gabarito do braço condicionado, não de molde da fala livre | fala fiel; nada inventado |
| 7 | **ego social**: orgulho, reputação, comparação com outros pets | depois da cognição social; autorização própria |

| # | decisão | estado |
|---|---|---|
| E-1 | O automodelo tem corpo e é aprendido por uma rede | **DECIDIDO** pelo Matheus (2026-10-07); substitui a introspecção direta: o pet não lê a sonda, a sonda avalia |
| E-2 | Falar de si como sub-decisão de `chamar_atencao`; provar uma fruta pela sub-decisão de comer que já existe | recomendado: sim; ação nova quebraria a reprodução da v1 |
| E-3 | Cérebro | **DECIDIDO: o A** (M6, 2026-10-07). O A tem a sonda do aprendido, a memória de episódios (N6) e a sonda do pedido (N7); o C recusa o N6 e o N7 |
| E-4 | Voz própria: o narrador antigo vira fala marcada, e o "eu" vem do automodelo | recomendado: sim |
| E-5 | Guarda ética da seção 8 como regra do jogo | recomendado: sim, antes da etapa 4 |
| E-6 | Revisão da regra "só a Decisão aprende": a rede de si aprende por erro de previsão | consequência da E-1; recomendado registrar a redação da seção 3 |
| E-7 | O corpo | **DECIDIDO: os conceitos do Creatures 3** (2026-10-07), seção 2 |
| E-9 | Química por baixo dos drives de hoje, um órgão por vez, ou trocar os drives pela química de uma vez | recomendado: por baixo e um órgão por vez; trocar de uma vez muda todos os braços juntos |
| E-10 | Tamanho do corpo: quantos químicos e órgãos na primeira versão | recomendado: o mínimo que reproduz os drives de hoje mais a digestão e a Vida; o Creatures 3 tem 21 órgãos e 811 genes |
| E-8 | Rede de si em inteiros, para ir à web, ou em ponto flutuante, só na pesquisa | recomendado: inteiros, como o cérebro A |
| E-11 | As perguntas da seção 4: conteúdo do pet ou gabarito | **DECIDIDO** pelo Matheus (2026-10-07): o pet pensa livremente, sem catálogo de perguntas nem frase pronta; as frases-modelo da seção 4 só existem num **braço condicionado**, implantadas de propósito, para registrar e comparar com o livre |

## 10. Literatura

Status pela skill `literatura-digilab`. As marcadas **pista** tiveram metadados conferidos no Crossref em 2026-10-07; o conteúdo não foi
lido.

| referência | id | status | o que pode sustentar |
|---|---|---|---|
| Grand e Cliff 1998, *Autonomous Agents and Multi-Agent Systems* | `10.1023/A:1010042522104` | VERIFICADA | bioquímica, quimioemissores e receptores modulando a rede |
| Creature Labs, *Creatures 3 Genetics Kit Manual* | manual oficial (Steam) | CORPUS, lido em 2026-10-07 | os conceitos do corpo da seção 2.1; documentação de produto |
| Wolpert, Ghahramani e Jordan 1995, *Science* | `10.1126/science.7569931` | pista | modelo interno do corpo que prevê o resultado do movimento |
| Wolpert e Kawato 1998, *Neural Networks* | `10.1016/s0893-6080(98)00066-5` | pista | pares de modelos direto e inverso no controle motor |
| Bongard, Zykov e Lipson 2006, *Science* | `10.1126/science.1133687` | pista | automodelo corporal que se revisa depois de dano |
| Kwiatkowski e Lipson 2019, *Science Robotics* | `10.1126/scirobotics.aau9354` | pista | automodelo aprendido sem tarefa prévia |
| Chen et al. 2022, *Science Robotics* | `10.1126/scirobotics.abn1944` | pista | automodelo do corpo inteiro aprendido por uma rede |
| Wang, Li e Hammer 2018, *Frontiers in Robotics and AI* | `10.3389/frobt.2018.00020` | pista | conhecimento de si revisável numa arquitetura de IA |
| Metzinger 2007, *Scholarpedia* | `10.4249/scholarpedia.4174` | pista | conceito de modelo de si; não é protocolo nem prova de subjetividade |
| Gottlieb et al. 2013, *Trends in Cognitive Sciences* | `10.1016/j.tics.2013.09.001` | pista | busca de informação e curiosidade |
| Oudeyer e Kaplan 2007 | `10.3389/neuro.12.006.2007` | VERIFICADA | tipologia da motivação intrínseca |

**Neurociência.** As ideias da neurociência que podem orientar o Digicorpo (modelo direto e cópia eferente, senso de agência,
interocepção, eu mínimo e narrativo, arbitragem modelo × hábito) estão ligadas a cada peça em
`docs/research/digibrain/mechanisms/self_model.md`, com as hipóteses H-SELF-01 a H-SELF-06.

**Limite de alegação.** Automodelos corporais aprendidos por redes, modelos diretos do corpo e agentes que buscam informação sobre si já
estão publicados. Nada aqui pode ser dito como novo. O que talvez seja contribuição, só depois de busca própria: um pet que aprende um
modelo do próprio corpo e da própria autoria durante a vida, com as estimativas calibradas contra a verdade do motor e das sondas.
