# Ego do pet — automodelo e indagação sobre a própria existência

Status: **DECIDIDO o objetivo, PROPOSTO o como** (2026-10-07). Decisão do Matheus: o pet deve ter ego, questionar a própria existência,
falar sobre isso e indagar sobre isso. Este documento transforma a decisão num desenho que respeita as regras do projeto. Ele **não
autoriza código**: cada etapa abre com tarefa e plano de análise, como sempre. Base: o plano "DigiBrain — automodelo e indagação sobre a
própria existência", versão 1, do Matheus, e a análise de aplicabilidade feita na mesma conversa.

## 1. O que "ego" quer dizer aqui

Ego é a definição operacional abaixo, e não uma alegação de consciência. Dizer "eu" ou fazer uma pergunta existencial não prova
experiência subjetiva; o Digilab mede mecanismos.

O ego do pet tem quatro partes:

| parte | o que o pet mantém sobre si | de onde vem |
|---|---|---|
| **Origem** | "nasci de um ovo, com este jeito" | o temperamento do ovo e a herança (`digilab/temperamento.py`, `digilab/heranca.py`) |
| **Autoria** | quem decidiu cada coisa: eu aprendi, já nasci assim, ou alguém pediu | as sondas dos cérebros: a decisão refeita sem o aprendido e sem o pedido |
| **Continuidade** | o que vivi, o que lembro e o que perdi | a memória de episódios (N6) e a memória por espaços (`digilab/memoria_espacos.py`) |
| **Relação** | o dono, os irmãos, os outros pets | o vínculo, o cruzamento em Meus pets, os rivais |

A ideia central: **a autoria é a pergunta da própria pesquisa, feita pelo pet sobre si.** A V2 pergunta quanto do comportamento vem do
herdado, do vivido e do instruído. O pet com ego pergunta a mesma coisa sobre ele mesmo e, como as sondas existem, pode receber uma
resposta honesta.

## 2. As cinco situações e o que as sustenta

Todas têm antecedente real no jogo de hoje. Nenhuma precisa de corpo novo.

| situação | pergunta que o pet pode fazer | gatilho no jogo | evidência que o pet pode ter | resposta honesta possível |
|---|---|---|---|---|
| encontra um pet parecido | "Se somos tão parecidos, o que faz eu ser eu?" | um irmão do mesmo cruzamento em Meus pets; um rival da mesma forma na arena | a forma e o brasão do outro, o que viu dele; a própria história | "somos parecidos no corpo, mas eu vivi outras coisas", citando um fato da própria história |
| descobre a origem no ovo | "Sou assim porque nasci assim ou porque aprendi com você?" | um traço de temperamento extremo; o dono perguntando; um marco da evolução | a fração das próprias decisões em que o aprendido mudou a escolha | hoje, quase sempre "nasci assim": na L1 o instinto decidia cerca de 80% das decisões, e isso é um resultado que o pet pode dizer |
| percebe que esqueceu | "Se eu esquecer o que vivi, continuo sendo eu?" | o dono ou outro pet cita um momento que o pet não guarda mais; uma pista que antes recuperava um episódio e agora não recupera nada | a ausência do episódio na própria memória, sem saber o conteúdo perdido | "você lembra disso, mas eu não", sem inventar o que foi esquecido |
| pedido contra preferência | "Eu quero isso ou estou fazendo porque você pediu?" | o pedido "deixe a fruta X" (N7); um comando pelo chat; a obediência com recusa | a sonda "quem decidiu" do N7: a decisão sem o pedido teria sido outra? | "sozinho eu teria comido; deixei porque você pediu", ou "eu já ia deixar" |
| aprende sobre reprodução | "Meu filho vai ter alguma parte de mim?" | o cruzamento em Meus pets; o nascimento de um filhote | o que o dono contou sobre herança (relato); o que observar no filhote | "pelo que você me contou, ele herda o meu jeito de nascer, não o que eu aprendi", com a fonte |

Duas regras valem em todas:
- **Sem acesso privilegiado ao mundo.** O motor sabe a verdade; o pet só sabe o que percebeu, lembrou ou ouviu, com a fonte. O pet não
  descobre a regra da herança lendo o código: alguém conta, ou ele observa.
- **Introspecção declarada.** As sondas leem o próprio cérebro do pet, e não o mundo. Deixar o pet consultar a diferença entre os próprios
  pesos e o prior é uma escolha de desenho: a introspecção. Ela fica explícita e é decisão do Matheus (seção 7).

## 3. Como uma pergunta nasce, vira ação e vira fala

1. **Questão como objeto interno**, antes da fala: tema, situação de origem, lacuna ou discrepância, evidências, respostas candidatas,
   forma de investigar, prioridade, estado (aberta, selecionada, investigando, respondida sob critério, suspensa) e revisões.
2. **Seleção pela decisão.** A pergunta só vira ação quando os impulsos a propõem e a decisão a escolhe. Fome, sono, lesão e ameaça vêm
   antes. Cada tema tem intervalo mínimo e não se repete à toa.
3. **Ação sem enum novo.** `AcaoPet` não ganha membro (V5 do roadmap). Falar de si entra como **sub-decisão de `chamar_atencao`**, do mesmo
   jeito que as frutas entraram como sub-decisão de comer.
4. **Investigar.** Pelas formas que existem: perguntar ao dono, consultar a própria memória, observar o outro pet, ou esperar a próxima
   ocorrência. A resposta do dono, dada pelo Conversar, entra como **relato com autor**, nunca como verdade nem como recompensa.
5. **Fala.** A LLM recebe a questão selecionada, as evidências autorizadas, a incerteza e o nível de linguagem do estágio. Ela só
   verbaliza. O verificador barra fala sem fato. O texto vai para o log, e o replay reaproveita o texto gravado.

O nível de linguagem cresce com o estágio: o bebê só reage com emote; a criança faz a pergunta concreta ("você pediu ou eu quis?"); o adulto
pode chegar à pergunta ampla ("o que faz eu ser eu?"). A pergunta filosófica pode ficar aberta para sempre: o pet conversa sobre ela sem
fingir resolvê-la.

## 4. O que muda no que existe

- **Voz própria.** Hoje o extrator de história lê o registro inteiro: é um narrador com acesso privilegiado. Com o ego, os fatos "meus" que
  o pet afirma em primeira pessoa passam a vir só do que ele percebeu ou guardou. O narrador antigo pode continuar como fala de outro tipo,
  marcada como tal, e não como autoconhecimento.
- **Motivo e honestidade do fator.** Continuam valendo e passam a ser a base da autoria: só se diz "eu aprendi" quando o aprendido mudou a
  escolha.
- **Decodificador de conceitos** (`docs/futuro/decodificador_conceitos.md`). Dá à fala os conceitos com incerteza; o ego dá o "sobre quem".
- **Cognição social** (`docs/futuro/cognicao_social.md`). Os relatos de outros pets entram no ego pelas mesmas regras de fonte; a autoimagem
  social (orgulho, reputação) fica para depois dela.
- **Web.** É mecânica de jogo: vai para a web numa versão de pet própria, com o número reservado pelo coordenador (hoje `VERSAO_PET = 10`
  no motor da web). As medidas de pesquisa rodam no Python, com o cérebro A (M6 decidido em 2026-10-07).

## 5. Medidas (PROPOSTO, sem número)

- **Calibração da autoria:** quando o pet diz "eu quis", "nasci assim" ou "você pediu", a sonda confirma? É a medida principal, e ela é
  exata, porque a sonda refaz a decisão com o mesmo sorteio.
- **Perguntas com lastro:** toda pergunta aponta a situação e a evidência que a dispararam; contar as sem lastro, as repetidas e as sem
  chance de resposta.
- **Fala fiel:** o texto não afirma nada além das evidências; nada de dor, medo de morrer ou consciência inventados.
- **Cuidado preservado:** perguntar não pode piorar a privação nem a saúde.
- **Controle de exposição:** um pet que recebe as mesmas respostas sem ter perguntado, pelo modo acoplado da bancada, separa o efeito da
  informação do efeito de perguntar.
- **Humanos (fase 2):** se o jogador entende melhor o pet e como ele reage às perguntas existenciais.

## 6. Riscos

- **Ética do produto.** Um pet que pergunta "continuo sendo eu?" ou fala do filho pode gerar apego forte ou angústia. O pet também pode
  morrer no jogo, por lesão sem tratar. Regra: nenhuma fala sobre morte, abandono ou sofrimento como pressão sobre o jogador; nenhuma
  pergunta usada para prender o jogador no jogo (padrões obscuros: Veiga et al. 2025, `10.5220/0013365800003929`, VERIFICADA). Entra na
  avaliação de ética da fase 2.
- **Alegação.** "O pet questiona a própria existência" é descrição de comportamento. Nunca "o pet tem consciência".
- **Narrador em vez de pet.** Com o aprendiz fraco de hoje, a resposta mais honesta à pergunta de origem é quase sempre "nasci assim". Isso
  é aceitável e até interessante, mas a fala não pode inflar o aprendido para parecer mais rica.
- **Escopo.** Cada etapa é uma versão de pet com gates. Nada de montar tudo de uma vez.

## 7. Etapas e decisões

| etapa | entrega | avança quando |
|---|---|---|
| 0 | auditoria no cérebro A: onde ficam a sonda do aprendido, a do pedido, a memória e o vínculo; Python e web | pontos de integração confirmados |
| 1 | ego em observação: origem, autoria e continuidade calculadas e registradas, sem mudar escolha nem fala | autoria calibrada contra a sonda; nenhum acesso privilegiado |
| 2 | as cinco perguntas como objetos, com frases-modelo, sem LLM | toda pergunta com lastro; cuidado preservado |
| 3 | diálogo pelo Conversar: o dono responde, a resposta vira relato com autor | relato distinto de observação no registro |
| 4 | fala por LLM sobre as mesmas intenções, comparada às frases-modelo | fala fiel; nada inventado |
| 5 | ego social: orgulho, reputação, comparação com outros pets | depois da cognição social; autorização própria |

| # | decisão do Matheus | recomendação | custo de errar |
|---|---|---|---|
| E-1 | Introspecção: o pet pode consultar a diferença entre os próprios pesos e o prior | sim, declarada como acesso ao próprio cérebro | sem ela, a pergunta de origem não tem resposta honesta |
| E-2 | Falar de si como sub-decisão de `chamar_atencao` | sim | ação nova quebra a reprodução da v1 |
| E-3 | Cérebro | **já decidido: o A** (M6, 2026-10-07, "pela regra seria o C; escolhido o A por evidência descritiva posterior"). O A tem as três peças que o ego usa: a sonda do aprendido, a memória de episódios (N6) e a sonda do pedido (N7); o C recusa o N6 e o N7 | — |
| E-4 | Voz própria: o narrador antigo vira fala marcada, e o "eu" passa a vir do ego | sim | o pet afirmaria sobre si o que não pode saber |
| E-5 | Guarda ética da seção 6 como regra do jogo | sim, antes da etapa 2 | perguntas existenciais virando pressão sobre o jogador |

## 8. Literatura

Status pela skill `literatura-digilab`. As marcadas **pista** tiveram metadados conferidos no Crossref em 2026-10-07; o conteúdo não foi
lido.

| referência | id | status | o que pode sustentar |
|---|---|---|---|
| Bongard, Zykov e Lipson 2006, *Science* | `10.1126/science.1133687` | pista | automodelo corporal que se revisa depois de dano |
| Kwiatkowski e Lipson 2019, *Science Robotics* | `10.1126/scirobotics.aau9354` | pista | automodelo aprendido sem tarefa prévia |
| Wang, Li e Hammer 2018, *Frontiers in Robotics and AI* | `10.3389/frobt.2018.00020` | pista | conhecimento de si revisável numa arquitetura de IA |
| Metzinger 2007, *Scholarpedia* | `10.4249/scholarpedia.4174` | pista | conceito de modelo de si; não é protocolo nem prova de subjetividade |
| Gottlieb et al. 2013, *Trends in Cognitive Sciences* | `10.1016/j.tics.2013.09.001` | pista | busca de informação e curiosidade |
| Oudeyer e Kaplan 2007 | `10.3389/neuro.12.006.2007` | VERIFICADA | tipologia da motivação intrínseca |

**Limite de alegação.** Automodelos e agentes que buscam informação sobre si já estão publicados. Nada aqui pode ser dito como novo. O que
talvez seja contribuição, só depois de busca própria: um pet que estima a origem do próprio comportamento (herdado, aprendido, instruído)
e cuja estimativa é calibrada contra a verdade das sondas.
