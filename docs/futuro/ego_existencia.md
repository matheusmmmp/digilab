# Ego do pet — automodelo com corpo, aprendido por uma rede, e indagação sobre a própria existência

Status (2026-10-07):
- **DECIDIDO pelo Matheus:**
  - o pet deve ter ego, questionar a própria existência e falar e indagar sobre isso;
  - o automodelo **tem corpo**;
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
| **Corpo** | o que o meu corpo consegue fazer agora, e quanto tenho certeza | a **rede de si** (seção 3), treinada pela experiência do próprio corpo |
| **Autoria** | quem decidiu cada coisa: eu aprendi, já nasci assim, ou alguém pediu | a **rede de si**, prevendo a própria escolha; a sonda do cérebro só avalia |
| **Origem** | "nasci de um ovo, com este jeito" | o temperamento do ovo e a herança (`digilab/temperamento.py`, `digilab/heranca.py`), contados ao pet ou observados por ele |
| **Continuidade** | o que vivi, o que lembro e o que perdi | a memória de episódios (N6) e a memória por espaços (`digilab/memoria_espacos.py`) |
| **Relação** | o dono, os irmãos, os outros pets | o vínculo, o cruzamento em Meus pets, os rivais |

**Regra central: o pet estima, o motor avalia.** O automodelo é uma rede que pode errar sobre o próprio pet. A verdade fica fora dela e
serve de gabarito: a capacidade real do corpo, que o motor conhece, e a sonda do cérebro, que refaz a decisão sem o aprendido ou sem o
pedido. Nenhuma das duas é entregue ao pet. É isso que faz do automodelo um modelo, e não uma leitura da verdade, e é o que permite medir
quanto o pet se conhece.

## 2. O corpo

**O que existe hoje.** O motor da vida tem estado de corpo, mas nenhuma capacidade com resultado incerto:
- **drives:** fome, higiene, energia, humor e saúde (`digilab/state.py`);
- **lesões:** existem no motor de educação (`ConfigLesoes`);
- **ações com efeito fixo:** as sete ações têm efeito determinístico; `explorar`, por exemplo, só gasta energia e dá um pouco de humor;
- **evolução fora da vida:** a evolução muda a forma usada na arena e não mexe na vida;
- **combate fora do cérebro:** o combate tem corpo e técnicas, mas fica fora do cérebro (decisão A9).

Sem capacidade incerta, a rede de si não tem o que aprender.

**O que o corpo precisa ter.** Pelo menos uma capacidade cujo resultado:
- depende de propriedades do corpo;
- é incerto;
- muda durante a vida.

O pet tenta, observa o resultado e aprende o que o próprio corpo consegue.

| opção | o que é | a favor | contra |
|---|---|---|---|
| **(a) Alcance da fruta** (recomendada) | a fruta pode cair perto ou longe (no chão, no galho); pegar a fruta longe tem chance de sucesso que depende do **alcance** do corpo, da **energia** e de **lesão**; o alcance cresce com o **estágio** | cabe no mundo das frutas, que o cérebro A já vê, e entra como sub-decisão de comer, sem ação nova; a evolução, a fadiga e a lesão mudam o corpo de verdade; o "por que não alcanço mais?" ganha base | mecânica de jogo nova (Python e web); o motor da vida passa a conhecer o estágio, por uma subclasse, sem tocar `engine.py` |
| (b) Corpo 2D completo | o ambiente manipulável de `docs/TODO_INTERACAO_CORPO.md` | o mais rico | em espera; muda o motor inteiro |
| (c) O corpo do combate | as formas, stats e técnicas da arena | já existe | junta luta e vida num cérebro só, o que a decisão A9 deixou de fora |

**Três mudanças de corpo** que a opção (a) dá, cada uma um teste do automodelo:
- **Evolução:** mudança grande e permanente; o alcance cresce de uma vez.
- **Fadiga:** mudança pequena e passageira, que volta com o sono.
- **Lesão:** mudança que piora e depois se recupera com o tratamento.

## 3. A rede de si

Uma rede separada do lobo de decisão. Não é um "controlador de ego" acima dos lobos: é uma peça que **prevê** e cuja saída a decisão pode
consultar.

- **Entrada:** só o que o pet sente: a percepção do corpo (energia, saúde, lesão, os drives), o contexto (a fruta, a distância) e a ação
  considerada. O estágio entra só como o pet o percebe, sem o número do motor.
- **Cabeça do corpo:** prevê o resultado da própria ação, com incerteza: "se eu tentar pegar a fruta longe, consigo?". É um modelo direto
  (*forward model*) do corpo, no sentido de Wolpert et al.
- **Cabeça da autoria:** prevê a própria escolha em situações alteradas: "sem o pedido, eu teria comido?" e "eu faria isso ao nascer?".
  Aprende observando as próprias escolhas ao longo da vida; a sonda do cérebro dá o gabarito, que o pet não vê.
- **Aprendizado:** por **erro de previsão**, e não por reforço. Depois de cada tentativa, a rede compara o que previu com o que aconteceu e
  se corrige. É supervisão pela própria experiência.
- **Números:**
  - pesos inteiros em ponto fixo e ativação sem função transcendental, como o cérebro A, para o porte na web e o replay bit a bit;
  - menos de mil pesos;
  - rng própria, se precisar de alguma.
- **Erro de previsão é o gatilho das perguntas.** Uma surpresa grande e repetida sobre o próprio corpo abre uma questão (seção 5). Depois da
  evolução, o pet erra o alcance e pergunta; conforme a rede se corrige, a pergunta operacional se resolve, e a existencial pode continuar.

**Consequência para uma regra do projeto.** A V2 tem a regra "só a Decisão aprende". A rede de si aprende por outro caminho. A decisão do
Matheus implica revê-la: **a Decisão aprende por reforço; a rede de si aprende por erro de previsão; nenhuma outra peça aprende.** A
revisão fica registrada (E-6).

## 4. As perguntas e o que as sustenta

As cinco situações do Matheus têm antecedente real no jogo de hoje. O corpo acrescenta uma sexta, a operacional, que é o gatilho mais
direto.

| situação | pergunta que o pet pode fazer | gatilho | evidência que o pet tem | resposta honesta possível |
|---|---|---|---|---|
| **o corpo muda** | "Por que não consigo mais alcançar como antes?" | erro de previsão grande da cabeça do corpo, depois da evolução, da fadiga ou de uma lesão | as próprias tentativas e o que a rede previa | "meu corpo mudou; preciso conhecer este corpo", até a rede se corrigir |
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
   - tentar a fruta longe entra como **sub-decisão de comer**.
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
- **Mundo das frutas:** ganha a distância da fruta e a tentativa de alcance (opção a), atrás de chave, numa subclasse do motor.
- **Motor da vida:** passa a conhecer o estágio do corpo, por subclasse; `engine.py` não muda.
- **Voz própria:**
  - hoje o extrator de história lê o registro inteiro, como um narrador com acesso privilegiado;
  - com o ego, o "eu" vem do automodelo e da memória do pet;
  - o narrador antigo continua como fala marcada.
- **Motivo e honestidade do fator:** continuam valendo para o que o pet diz da decisão.
- **Decodificador de conceitos** (`docs/futuro/decodificador_conceitos.md`): a rede de si é um dos estados que ele pode ler.
- **Cognição social** (`docs/futuro/cognicao_social.md`): os relatos de outros pets entram pelas mesmas regras de fonte.
- **Web:** é mecânica de jogo e vai para a web, numa versão de pet própria, depois do porte do cérebro A. A rede de si também precisa de
  paridade Python/web.

## 7. Medidas (PROPOSTO, sem número)

- **Erro de previsão do próprio corpo:** quanto a cabeça do corpo erra, e quanto ela se calibra (a confiança declarada bate com a taxa de
  acerto).
- **Adaptação depois da mudança:** quantas tentativas até o erro voltar ao nível de antes, na evolução, na fadiga e na lesão.
- **Calibração da autoria:** a estimativa do pet ("você pediu", "eu quis", "nasci assim") contra a sonda, que é o gabarito exato.
- **O automodelo serve à decisão?** O desempenho no ambiente com a rede de si consultada contra três controles:
  - a rede congelada, que não aprende;
  - a rede ausente;
  - o **oráculo**: a capacidade real dada de graça, que é o teto.
- **Perguntas com lastro:** toda pergunta aponta a discrepância e a evidência que a dispararam; contar as sem lastro e as repetidas.
- **Fala fiel:** nada além das evidências; nada de dor, medo de morrer ou consciência inventados.
- **Cuidado preservado:** investigar não pode piorar a privação nem a saúde.
- **Controle de exposição:** o mesmo pet recebendo as mesmas tentativas e respostas sem tê-las escolhido, pelo modo acoplado da bancada.
- **Humanos (fase 2):** se o jogador entende melhor o pet.

## 8. Riscos

- **Escopo.** São três peças novas, cada uma uma versão de pet com gates: um corpo com capacidade incerta, uma rede de si e a revisão de uma
  regra. Nada de montar tudo de uma vez.
- **Rede que não aprende.** O cérebro B "não aprendeu" na calibração. A rede de si pode ter o mesmo problema; o controle congelado mostra
  isso cedo.
- **Ética do produto.** Um pet que pergunta "continuo sendo eu?" pode gerar apego forte ou angústia, e o pet pode morrer no jogo.
  - Nenhuma fala sobre morte, abandono ou sofrimento como pressão sobre o jogador.
  - Nenhuma pergunta usada para prender o jogador no jogo (padrões obscuros: Veiga et al. 2025, `10.5220/0013365800003929`, VERIFICADA).
  - Entra na avaliação de ética da fase 2.
- **Alegação.** "O pet questiona a própria existência" é descrição de comportamento. Nunca "o pet tem consciência".

## 9. Etapas e decisões

| etapa | entrega | avança quando |
|---|---|---|
| 0 | auditoria no cérebro A e no mundo das frutas: onde entram a distância da fruta, o estágio na vida, a rede de si; Python e web | pontos de integração confirmados |
| 1 | **corpo**: a fruta perto e longe, o alcance por estágio, a energia e a lesão, sem rede de si (o instinto tenta pelo próprio jeito) | G1 e G2; a capacidade muda com o estágio, a fadiga e a lesão como desenhado |
| 2 | **rede de si em observação**: aprende o corpo e a autoria, sem influenciar escolha nem fala | o erro de previsão cai; calibração; adapta depois da evolução; nenhum acesso privilegiado |
| 3 | **automodelo na decisão**: a previsão do corpo entra como entrada da decisão | desempenho contra a rede congelada, a ausente e o oráculo |
| 4 | **perguntas**: a operacional e as cinco, como objetos, com frases-modelo, sem LLM | toda pergunta com lastro; cuidado preservado |
| 5 | **diálogo** pelo Conversar: o dono responde, a resposta vira relato com autor | relato distinto de observação no registro |
| 6 | **fala por LLM** sobre as mesmas intenções, comparada às frases-modelo | fala fiel; nada inventado |
| 7 | **ego social**: orgulho, reputação, comparação com outros pets | depois da cognição social; autorização própria |

| # | decisão | estado |
|---|---|---|
| E-1 | O automodelo tem corpo e é aprendido por uma rede | **DECIDIDO** pelo Matheus (2026-10-07); substitui a introspecção direta: o pet não lê a sonda, a sonda avalia |
| E-2 | Falar de si e tentar a fruta longe como sub-decisões (`chamar_atencao`, comer) | recomendado: sim; ação nova quebraria a reprodução da v1 |
| E-3 | Cérebro | **DECIDIDO: o A** (M6, 2026-10-07). O A tem a sonda do aprendido, a memória de episódios (N6) e a sonda do pedido (N7); o C recusa o N6 e o N7 |
| E-4 | Voz própria: o narrador antigo vira fala marcada, e o "eu" vem do automodelo | recomendado: sim |
| E-5 | Guarda ética da seção 8 como regra do jogo | recomendado: sim, antes da etapa 4 |
| E-6 | Revisão da regra "só a Decisão aprende": a rede de si aprende por erro de previsão | consequência da E-1; recomendado registrar a redação da seção 3 |
| E-7 | O corpo: alcance da fruta (a), corpo 2D (b) ou corpo do combate (c) | recomendado: (a) |
| E-8 | Rede de si em inteiros, para ir à web, ou em ponto flutuante, só na pesquisa | recomendado: inteiros, como o cérebro A |

## 10. Literatura

Status pela skill `literatura-digilab`. As marcadas **pista** tiveram metadados conferidos no Crossref em 2026-10-07; o conteúdo não foi
lido.

| referência | id | status | o que pode sustentar |
|---|---|---|---|
| Wolpert, Ghahramani e Jordan 1995, *Science* | `10.1126/science.7569931` | pista | modelo interno do corpo que prevê o resultado do movimento |
| Wolpert e Kawato 1998, *Neural Networks* | `10.1016/s0893-6080(98)00066-5` | pista | pares de modelos direto e inverso no controle motor |
| Bongard, Zykov e Lipson 2006, *Science* | `10.1126/science.1133687` | pista | automodelo corporal que se revisa depois de dano |
| Kwiatkowski e Lipson 2019, *Science Robotics* | `10.1126/scirobotics.aau9354` | pista | automodelo aprendido sem tarefa prévia |
| Chen et al. 2022, *Science Robotics* | `10.1126/scirobotics.abn1944` | pista | automodelo do corpo inteiro aprendido por uma rede |
| Wang, Li e Hammer 2018, *Frontiers in Robotics and AI* | `10.3389/frobt.2018.00020` | pista | conhecimento de si revisável numa arquitetura de IA |
| Metzinger 2007, *Scholarpedia* | `10.4249/scholarpedia.4174` | pista | conceito de modelo de si; não é protocolo nem prova de subjetividade |
| Gottlieb et al. 2013, *Trends in Cognitive Sciences* | `10.1016/j.tics.2013.09.001` | pista | busca de informação e curiosidade |
| Oudeyer e Kaplan 2007 | `10.3389/neuro.12.006.2007` | VERIFICADA | tipologia da motivação intrínseca |

**Limite de alegação.** Automodelos corporais aprendidos por redes, modelos diretos do corpo e agentes que buscam informação sobre si já
estão publicados. Nada aqui pode ser dito como novo. O que talvez seja contribuição, só depois de busca própria: um pet que aprende um
modelo do próprio corpo e da própria autoria durante a vida, com as estimativas calibradas contra a verdade do motor e das sondas.
