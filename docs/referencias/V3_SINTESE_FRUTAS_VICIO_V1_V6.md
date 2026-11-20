# Digilab — frutas, gosto hedônico e vício: síntese bibliográfica (V1 a V6)

Busca de 2026-10-01. Tabela em `v3_referencias.csv` (38 linhas), BibTeX das verificadas em
`v3_referencias.bib` (35 entradas), registro bruto por DOI em `v3_verificacao.json`. 34 DOIs
conferidos no Crossref, nenhuma falha, nenhum com campo `update-to`; 25 com resumo lido no Crossref
ou no Europe PMC, e os 9 restantes marcados linha por linha como verificados só por título e
metadados. Nenhum desenho é proposto aqui.

**O achado que mais importa, dito primeiro:** a literatura de modelos computacionais de vício não é
um campo vizinho ao projeto — ela já passa pelo formalismo que o Digilab usa. Keramati, Durand e
Girardeau (`10.1037/rev0000046`) unem aprendizado de recompensa e **regulação homeostática** numa
teoria da adicção, e é exatamente o arcabouço de RL homeostático que o projeto já adotou para o
instinto. Se o vício do pet for definido, há um caminho em que ele sai de drives que já existem, com
equações publicadas, em vez de ser mecânica nova.

## V1 — Gostar × querer × aprender

A separação existe, é de fonte primária e é de neurociência de mamíferos — não de psicologia da
preferência nem de computação. Berridge e Robinson (`10.1016/s0165-0173(98)00019-8`) perguntam qual
dos três papéis a dopamina mesolímbica medeia — impacto hedônico, aprendizado de recompensa ou
saliência de incentivo — e concluem pela terceira; a revisão curta dos três componentes dissociáveis
está em Berridge, Robinson e Aldridge (`10.1016/j.coph.2008.12.014`), a circuitaria do prazer com
hotspots hedônicos em Berridge e Kringelbach (`10.1016/j.neuron.2015.02.018`), e o substrato
anatomicamente restrito do "gostar" em Peciña e Berridge (`10.1523/jneurosci.2329-05.2005`), que
mostram que não é toda a casca medial do accumbens que produz o aumento de impacto hedônico. Para
recompensa **alimentar** especificamente, a revisão atual é Morales e Berridge
(`10.1016/j.physbeh.2020.113152`).

O que não sustenta, e é a parte que protege o projeto de uma afirmação indefensável: Berridge
(`10.1016/0149-7634(95)00033-b`) pergunta explicitamente se recompensa e prazer são idênticos e se o
prazer gustativo **pode** ser avaliado em animais. A literatura trata "liking" como **reação
hedônica mensurável** (expressões faciais, padrões de consumo), não como experiência subjetiva
relatada. Nada aqui autoriza dizer que um agente sente prazer.

Implicação para as quatro variáveis: a literatura apoia separar **gosto** de **querer** como
construtos distintos com medidas distintas, e Finlayson e Dalton (`10.1016/j.appet.2011.10.011`) são
a referência de operacionalização — mostram que medir os dois exige instrumentos separados, o que no
simulador significa dois registros distintos no log, não um escalar só.

## V2 — Sensibilização de incentivo e dependência

A teoria está em Robinson e Berridge (`10.1016/0165-0173(93)90013-p`), com a revisão de questões
abertas em `10.1098/rstb.2008.0093`, a exposição mais recente em `10.1037/amp0000059` e o status
atual, pelos próprios autores, em `10.4324/9781315689197-29`. A predição central — o querer cresce
com a exposição enquanto o gostar não acompanha — tem **teste empírico em humanos** em Grigutsch,
Lewe e Rothermund (`10.1016/j.jbtep.2019.01.002`), que examinam querer implícito sem gostar
implícito.

A crítica também é verificável e precisa aparecer junto: Nutt et al. (`10.1038/nrn3939`) revisam que
décadas tratando a adicção como transtorno do sistema dopaminérgico **não produziram tratamentos
novos** e questionam o peso dado à dopamina. Separando os três níveis que o pedido pediu para
separar: o resultado experimental em animais é a sensibilização comportamental e neural à exposição
repetida; a teoria é a atribuição disso à saliência de incentivo como causa primária da adicção; e a
extrapolação para humanos é o elo mais fraco — Grigutsch et al. testam o desacoplamento em
laboratório, não a etiologia.

Implicação: a assimetria "querer sobe, gostar não" é a peça com melhor suporte para um mecanismo de
vício, e é justamente a que distingue vício de preferência forte. Se implementada, carrega a ressalva
de que a teoria é contestada quanto ao papel causal da dopamina.

## V3 — Modelos computacionais de vício

Esta é a trilha mais forte, e a que tem equações. Redish (`10.1126/science.1102384`) é o modelo
canônico: a droga acessa os mesmos mecanismos dos sistemas naturais de aprendizado, formalizados por
diferença temporal, e o comportamento de dependência emerge disso — a predição testável sendo um
sinal de erro de predição que **não se extingue**. Redish, Jensen e Johnson
(`10.1017/s0140525x0800472x`) generalizam para vulnerabilidades em múltiplos sistemas de decisão
interagentes, e não num mecanismo único. Dezfouli, Piray e Keramati
(`10.1162/neco.2009.10-08-882`) constroem o modelo de cocaína sobre a hipótese dopaminérgica mais
decremento de sensibilidade do sistema de recompensa após exposição longa. Keramati e Gutkin
(`10.1371/journal.pone.0061489`) explicam a inconsistência entre querer parar e continuar buscando
por desequilíbrio na hierarquia de decisão. Piray, Keramati e Dezfouli (`10.1162/neco_a_00009`) dão
vulnerabilidade variando por indivíduo. O panorama de dopamina como quantidade computacional está em
Montague, Hyman e Cohen (`10.1038/nature03015`).

E o elo direto com o projeto: Keramati, Durand e Girardeau (`10.1037/rev0000046`) tratam a adicção
como **transtorno de aprendizado por reforço homeostático**, unindo recompensa e regulação de
necessidade. O projeto já usa esse formalismo para o instinto.

O que não sustenta: tudo isso é modelo de droga, calibrado contra dados de roedor e humano, não
modelo de preferência por comida. A separação entre modelo e evidência biológica está explícita nos
próprios artigos, e deve ficar explícita em qualquer uso: Redish e Dezfouli são **modelos que
reproduzem fenômenos**, não demonstrações de que o mecanismo proposto é o que ocorre.

## V4 — Preferência alimentar aprendida × inata

Além do que o projeto já tinha verificado sobre consequência pós-ingestiva, três mecanismos dão
variáveis operacionais distintas. **Neofobia como traço:** Pliner e Hobden
(`10.1016/0195-6663(92)90014-w`) constroem e validam uma escala de relutância a comer ou evitar
alimentos novos — trata a neofobia como diferença individual estável, o que a torna candidata a
temperamento inato em vez de estado. **Saciedade sensório-específica:** Rolls et al.
(`10.1016/0031-9384(81)90310-3`; e `10.1016/0031-9384(83)90003-3`, que mostra a queda do agradável
ser maior para o alimento comido até a saciedade do que para os outros) dão um mecanismo de
"enjoar de um sabor" que é específico, reversível e independente da fome geral. **Aversão
condicionada:** Garcia, Kimeldorf e Koelling (`10.1126/science.122.3160.157`) fundam o paradigma, com
a revisão de características próprias em Bernstein (`10.1016/s0899-9007(98)00192-0`) e a ligação com
codificação de valor de desfecho em Balleine (`10.1093/oso/9780195326581.003.0013`). Para preferência
inata modulada por exposição, Beauchamp e Moran (`10.1016/s0195-6663(82)80007-x`).

Implicação direta para as quatro variáveis do desenho provisório: a literatura dá mecanismos
**separáveis** para cada uma — neofobia e preferência inata para "gosto" de partida, saciedade
sensório-específica para gosto que varia com o consumo recente, aversão condicionada e consequência
pós-ingestiva para "efeito", e sensibilização de incentivo para "vício". O risco que o projeto já
identificou fica mais nítido aqui: saciedade sensório-específica e fome são canais distintos na
literatura, e tratá-los como um só colapsa "gosto" em "necessidade".

## V5 — Creatures em fonte primária

**Não existe.** Busquei artigos de Grand, Cliff e equipe, manual oficial e documentação do kit
genético, e nada que descreva vício foi localizado. As duas fontes primárias verificadas
(`10.1023/A:1010042522104` e `10.1162/106454699568683`) descrevem bioquímica artificial,
quimioemissores e receptores modulando a rede neural — mas não vício. Buscas combinando Creatures com
vício ou droga retornam farmacologia não relacionada.

O candidato mais provável a conter a descrição é o livro do próprio Grand, *Creation: Life and How to
Make It* (2001), cuja existência está confirmada por registro de resenha indexado
(`10.5860/choice.39-4009`) mas cujo **conteúdo não foi verificado** — não tive acesso ao texto, e
nada sobre vício pode ser atribuído a ele até alguém ler. Até lá, qualquer afirmação sobre "vício
como no Creatures" é NÃO VERIFICADA EM FONTE PRIMÁRIA e vale como pista de desenho, nunca como
evidência ou precedente.

## V6 — Bem-estar e ética do desenho

Aqui há uma assimetria que muda o enquadramento. A literatura verificada e robusta trata de
mecânicas dirigidas **ao jogador**: loot boxes associadas a jogo problemático (Zendle e Cairns,
`10.1371/journal.pone.0206767`), loot boxes como psicologicamente análogas a jogo de azar (Drummond e
Sauer, `10.1038/s41562-018-0360-1`), monetização predatória (King e Delfabbro,
`10.1111/add.14286`) e padrões de desenho exploratórios (Karlsen,
`10.7551/mitpress/11550.003.0019`; Veiga et al., `10.5220/0013365800003929`).

O que **não** encontrei: literatura sobre representar dependência **num personagem cuidado pelo
jogador**, nem sobre o risco de o jogador explorar o vício do personagem como recurso. Tentei
representação de vício em jogos, análise crítica de desenho e bem-estar do jogador. É lacuna de
literatura, não falha de termo único.

Implicação: o risco que a literatura documenta é o de mecânica que explora o jogador, e ela não
cobre o caso do Digilab. A analogia é imperfeita de um jeito que convém declarar: um pet que fica
viciado não cobra do jogador. Se o projeto quiser falar de ética aqui, o apoio existente é por
analogia e precisa ser rotulado como tal.

## Afirmações a evitar sobre o pet

1. "O pet sente prazer." A literatura mede reação hedônica, não experiência subjetiva, e Berridge
   (`10.1016/0149-7634(95)00033-b`) levanta a questão em vez de resolvê-la.
2. "O vício do pet é realista." Os modelos computacionais (Redish, Dezfouli) reproduzem fenômenos de
   droga em roedor e humano; não validam vício em agente de jogo.
3. "O pet quer mas não gosta, como um adicto." A assimetria tem suporte, mas a teoria é contestada
   quanto ao papel causal da dopamina (Nutt et al., `10.1038/nrn3939`).
4. "O Creatures já fazia vício assim." Sem fonte primária. Pista de fã, nunca precedente.
5. "Gosto e fome são a mesma variável." Saciedade sensório-específica é um canal distinto da fome
   geral (Rolls et al.).
6. "Representar vício no pet é eticamente neutro porque a literatura só critica monetização."
   A literatura não cobre o caso; ausência de crítica não é aval.
7. "O efeito da fruta no pet mede ensino." Comida é canal de cuidado — o risco que o projeto já
   identificou, e a literatura de V4 reforça: a consequência pós-ingestiva ensina o **animal**, sem
   treinador no laço.

## Pendências

**Conteúdo não verificado:** *Creation* (Grand, 2001) — existência confirmada, texto inacessível
nesta busca; é a única via plausível para o mecanismo do Creatures em fonte primária.

**Não localizadas:** Zagal, Björk e Lewis (2013), *Dark patterns in the design of games*, FDG — muito
citada, sem registro no Crossref nesta busca; substitutos verificados são Karlsen e Veiga et al.
E a literatura de representar dependência em personagem cuidado pelo jogador, que parece não existir.

**Defeito de metadados no Crossref, encontrado e corrigido.** O registro do Crossref para
`10.1016/0165-0173(93)90013-p` lista **apenas um autor** (Robinson), enquanto o Europe PMC, PMID
8401595, dá "Robinson TE, Berridge KC". A tabela e o BibTeX foram gerados a partir do campo do
Crossref e por isso traziam um autor só; estão corrigidos, com a fonte da lista de autores
registrada na própria linha. Auditei os 34 DOIs deste conjunto comparando a contagem de autores do
Crossref com a do Europe PMC e **esta foi a única divergência**. A mesma auditoria no conjunto Q1-Q7
encontrou um caso equivalente (`10.1001/archinte.1993.00410180039004`, McEwen e Stellar), também
corrigido. Lição operacional: o campo `author` do Crossref não é confiável para artigos antigos, e
contagem de autores precisa de segunda fonte.

**Verificação parcial:** 9 dos 34 DOIs não têm resumo disponível nem no Crossref nem no Europe PMC
(incluindo Rolls et al. 1981, Garcia et al. 1955, Drummond e Sauer, King e Delfabbro); nesses, a
coluna `o_que_sustenta` está limitada ao que título e metadados autorizam e isso está marcado linha
por linha. Para Rolls, o artigo de 1983 com resumo lido cobre a mesma afirmação.

**Cobertura:** OpenAlex e o conector de literatura seguem indisponíveis nesta instalação; a busca saiu
por Crossref, arXiv e Europe PMC. V6 é a trilha mais afetada, porque é a que mais dependeria de busca
por tema em vez de por nome.
