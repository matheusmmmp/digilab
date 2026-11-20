# Digilab V2 — síntese bibliográfica por pergunta (Q1 a Q7)

Busca de 2026-10-01. Tabela em `v2_referencias.csv` (58 linhas), BibTeX das verificadas em
`v2_referencias.bib` (53 entradas), registro bruto de verificação em `v2_verificacao.json`.
Nenhuma decisão de desenho é tomada aqui: o que segue é o que a literatura sustenta, o que ela não
sustenta, e o que isso implica para os gates PROPOSTOS da V2.

Limitação de cobertura, declarada de saída: nesta sessão o OpenAlex ficou inacessível (a provisão da
credencial travou) e o conector de literatura caiu. A descoberta foi feita só por Crossref, arXiv e
Europe PMC, o que enviesa o resultado para trabalhos que eu consegui nomear. A cobertura é mais
estreita que a da revisão de setembro; trate ausências como não investigadas, não como inexistentes.

## Q1 — Aprendizes em que o feedback humano pesa

A premissa central do aprendiz da V2 já está publicada e validada: o feedback humano depende da
política atual do agente, comportando-se como vantagem e não como recompensa fixa, o que muda qual
algoritmo é o correto (MacGlashan et al., arXiv:1701.06049; versão profunda em Arumugam et al.,
arXiv:1902.04257). A família TAMER dá a alternativa — tratar o reforço humano como sinal de valor a
ser modelado (Knox e Stone, `10.1145/1597735.1597738`;
extensão de alta dimensão em Warnell et al., `10.1609/aaai.v32i1.11485`; combinação com recompensa do
MDP em `10.65109/pajo3896`). Dois achados restringem o desenho mais do que parece: Knox e Stone
(`10.1016/j.artint.2015.03.009`) mostram que a positividade do reforço e o desconto temporal **alteram
o resultado**, logo são parâmetros a declarar e não defaults; e Loftin et al.
(`10.1007/s10458-015-9283-7`) modelam a estratégia do treinador incluindo o significado da **ausência**
de feedback. O perfil empírico do treinador real continua sendo Thomaz e Breazeal
(`10.1016/j.artint.2007.09.009`): recompensa antecipatória, tentativa de guiar, inconsistência.

O que a literatura **não** sustenta, e isso é relevante para dois gates. Primeiro, não localizei nada
sobre aprendizes interativos com menos de mil parâmetros; a literatura caminha na direção oposta
(Deep TAMER, Deep COACH aumentam capacidade). O limite de pesos da V2 é consequência do requisito de
determinismo, não uma escolha com precedente. Segundo, e mais importante: as métricas que essa
literatura usa para "o treinador deixou marca" são **sucesso na tarefa, eficiência amostral e
comparação contra o desempenho do próprio treinador**. Não encontrei precedente para divergência de
política entre treinadores (JSD) como métrica primária. O gate de ≥ 0,10 bit, portanto, **não tem
referente externo**: o limiar é decisão do projeto e nenhum revisor terá com o que compará-lo. Vale
reportar, ao lado dele, uma métrica comparável à literatura.

## Q2 — Arquiteturas modulares com aprendizado localizado e explicável

A decomposição em módulos nomeados é disciplina de desenho estabelecida, de Brooks
(`10.1109/jra.1986.1087032`; `10.1016/0004-3702(91)90053-m`) a Bryson
(`10.1007/3-540-36559-1_7`), com o formalismo de granularidade mista em options (Sutton, Precup e
Singh, `10.1016/s0004-3702(99)00052-1`) e um exemplo de arquitetura de nível de sistema integrando
emoção em LIDA (Franklin et al., `10.1109/tamd.2013.2277589`). Para "só um módulo aprende", o
precedente formal é Jacobs et al. (`10.1162/neco.1991.3.1.79`): redes separadas aprendem subconjuntos
dos casos sob um gate. No domínio, Creatures é o precedente direto (`10.1023/A:1010042522104`) e
Castro e Gudwin mostram um módulo de memória episódica acoplado a uma criatura virtual
(`10.4018/jse.2013010102`). Para explicabilidade **por componente**, o achado mais forte é Concept
Bottleneck Models (Koh et al., arXiv:2007.04612): a predição passa obrigatoriamente por conceitos
nomeados e intervencionáveis — e o trabalho **mede o custo de desempenho** do gargalo.

O que não se sustenta: não encontrei nenhum estudo mostrando que modularidade melhora legibilidade ou
estabilidade **sob capacidade igual**. O confundidor de capacidade que a especificação da V2 já
suspeitava continua sem tratamento na literatura que localizei. CBM é o que mais se aproxima de medir
o preço da arquitetura interpretável, mas em classificação de imagem, não em agente. Implicação para o
gate de "fator explicável em ≥ 50% das decisões": ele mede o esquema de atribuição do próprio
projeto; se a intenção é defender que a modularidade compra legibilidade, o desenho precisa de um
braço de capacidade equivalente sem módulos, e o custo de desempenho precisa ser reportado junto.

## Q3 — Separar o efeito do cuidado do efeito do ensino

Existe um molde conceitual pronto e é bom: Darling e Steinberg (`10.1037/0033-2909.113.3.487`)
separam **estilo** parental, o contexto emocional em que a criação acontece, de **prática** parental, o
conteúdo ensinado, com o estilo moderando o efeito da prática. É exatamente a separação que a V2
quer. Que o canal "cuidado" sozinho tem efeito mensurável e duradouro está demonstrado em Weaver et
al. (`10.1038/nn1276`): variação natural no cuidado materno altera o epigenoma do filhote no promotor
do receptor de glicocorticoide. Do lado dos desenhos, a literatura canina oferece comparações de
método diretamente transferíveis: China et al. (`10.3389/fvets.2020.00508`) com 63 cães em três
grupos de 21 e até 150 min de treino; Casey et al. (`10.1038/s41598-021-97743-0`), que mede o método
do dono por um **desfecho no animal** (viés cognitivo) em vez de autorrelato; Hiby et al.
(`10.1017/s0962728600026683`) relacionando método relatado, obediência e problemas; e as revisões de
Ziv (`10.1016/j.jveb.2017.02.004`) e Guilherme Fernandes et al.
(`10.1016/j.applanim.2017.07.001`), a segunda questionando a inferência direta de método para dano.

O que não se sustenta, e é a boa notícia: **nenhum desses estudos separa cuidado de ensino**. Método
aversivo é simultaneamente sinal de ensino e agressão ao bem-estar, que é precisamente o confundidor
que a V2 quer quebrar; nenhum deles tem braço "só cuidado". Ou seja, o braço de controle "só cuidado"
e o gate de "a divergência se mantém sem mortes e sem lesão" não estão preenchendo uma lacuna de
citação — são a operacionalização de algo que a literatura de treino animal não consegue fazer. O
formalismo de análise é a norma de reação de Dingemanse et al. (`10.1016/j.tree.2009.07.013`), com a
referência de magnitude de Dochtermann et al. (`10.1098/rspb.2014.2201`).

## Q4 — Ambiente mínimo com consequência

A metade "o pet aprende pela consequência" é solidamente estabelecida. Sclafani
(`10.1006/appe.2000.0370`) estabelece que existem controles pós-ingestivos **positivos**, não apenas
os negativos de saciação; de Araujo et al. (`10.1016/j.neuron.2008.04.003`) mostram recompensa
alimentar sem sinalização de receptor de gosto; e Blusk, Ackroff e Sclafani
(`10.1016/0195-6663(92)90038-8`) produzem preferência por infusão intragástrica, separando o sinal
oral do sinal de consequência. A revisão de substratos está em `10.1016/j.appet.2016.12.015`. Para
chamar um laço sensório-motor simples de decisão cognitiva, van Duijn et al.
(`10.1177/105971230601400207`) dão a licença teórica; para formalizar quais ações são aplicáveis em
quais estados, Khetarpal et al. (arXiv:2006.15085) formalizam affordances em RL.

O que não se sustenta: **não encontrei nada mostrando que mais decisões com consequência aumentam o
efeito do treinador.** Toda a literatura de sabor-nutriente é sobre o animal aprendendo das próprias
consequências, sem treinador no laço. A segunda alavanca da V2 está apoiada como mecanismo de
aprendizado do pet e **desapoiada** como mecanismo de amplificação do sinal do dono — o que é
consistente com a decisão já tomada de testar as duas alavancas em separado.

## Q5 — As peças do Dwarf Fortress, peça por peça

Cinco das seis peças têm análogo científico **na forma**; uma está contestada. Nenhuma tem validação
do que o jogo de fato implementa, e o capítulo acadêmico sobre o jogo (Adams,
`10.1515/9783839453452-007`) analisa caracterização e narrativa emergente sem validar mecanismo.

**Espaços de memória com disputa por força — CONTESTADA.** Raaijmakers e Jakab
(`10.3758/s13421-011-0131-y`) testam e contestam a explicação por inibição e competição do
esquecimento induzido por evocação. A peça não pode ser apresentada como mecanismo estabelecido.

**Relembrar reaplica a emoção e altera a memória — SUSTENTADA.** Nader, Schafe e LeDoux
(`10.1038/35021052`): a memória consolidada volta a ficar lábil após a evocação e exige síntese
proteica para reconsolidar. Modulação por excitação emocional em McGaugh (`10.1101/lm.93405`).

**Memória nuclear que altera a personalidade — PARCIAL.** Conway e Pleydell-Pearce
(`10.1037/0033-295x.107.2.261`) dão memórias autodefinidoras dentro de um sistema self-memory ligado
a metas; Specht et al. (`10.1037/a0024950`), com 14.718 participantes, dão mudança de traço ao longo
da vida e por eventos maiores. O que a literatura dá é mudança **gradual e ligada a metas**, não uma
memória única virando um traço.

**Estresse em duas escalas com recuperação assimétrica — SUSTENTADA na forma.** Carga alostática
(McEwen e Stellar, `10.1001/archinte.1993.00410180039004`) é explicitamente de duas escalas: o custo
crônico acumulado predispõe a resposta aguda. A assimetria entre proteção e dano está em McEwen
(`10.1056/nejm199801153380307`).

**Tarefa pedida × necessidade própria — SUSTENTADA como conflito motivacional.** Modelo hierárquico
de aproximação-evitação de Elliot (`10.1007/s11031-006-9028-7`).

**Facetas × valores filtrando a emoção — SUSTENTADA na forma.** Modelo de processo componencial de
Scherer (`10.1080/02699930902928969`), com os eixos de traço e as síndromes correlacionadas em
Réale et al. e Sih et al. (já no corpus verificado) e o desenvolvimento em Stamps e Groothuis
(`10.1111/j.1469-185x.2009.00103.x`).

Implicação: se uma peça for implementada, o análogo entra como **inspiração declarada**, nunca como
validação — e a peça de disputa por força precisa, além disso, de uma ressalva de que o mecanismo é
contestado na própria psicologia.

## Q6 — Aprendizado determinístico e reproduzível entre plataformas

Por que resultados divergem entre implementações está em Goldberg (`10.1145/103162.103163`), e existe
um trabalho quase sob medida para o requisito do projeto: Polhill, Izquierdo e Gotts
(`10.1016/j.envsoft.2004.10.011`), sobre o que modeladores baseados em agentes precisam saber de ponto
flutuante. O estado da arte de replay determinístico diante de fatores não determinísticos está no
survey de Chen, Zhang e Guo (`10.1145/2790077`). Que aritmética inteira basta para redes treináveis,
com custo de acurácia quantificado, está em Jacob et al. (`10.1109/cvpr.2018.00286`), com o panorama
em Gholami et al. (arXiv:2103.13630).

O que não se sustenta: **não localizei nenhum trabalho sobre paridade bit a bit entre uma
implementação em Python e uma em navegador do mesmo aprendiz**, que é o requisito real da V2. A
literatura de quantização trata de eficiência de inferência, não de determinismo entre plataformas; a
de replay trata de sistemas, não de aprendizes. O gate de replay e paridade é defensável como método e
**não tem benchmark**; Polhill et al. é a citação que faz um revisor entender por que o requisito
importa.

## Q7 — A lacuna criação × seleção

Refeita com termos novos — evolução interativa com aprendizado dentro da vida, criação e treino
guiados pelo usuário, agentes co-criativos, separar natureza de criação em agentes — e **nada
pertinente voltou**. A lacuna continua de pé, e continua sendo um resultado negativo de busca
lexical, agora com a cobertura mais estreita desta sessão (sem OpenAlex). Não reforcei nem derrubei:
mantive. Quanto a Evans (2002), a existência e a paginação seguem confirmadas por listas de
referências de terceiros, mas **o texto não foi localizado** — sem DOI, sem registro no Crossref e sem
cópia de acesso legítimo encontrada.

## Afirmações a evitar

1. "O Digilab é o primeiro a separar instinto de aprendido." Hallawa et al. já faz.
2. "Herdar o prior sem herdar o aprendido é desenho novo." É o efeito Baldwin.
3. "Comportamento ensinado e não roteirizado é o diferencial." Black & White (2001) já afirmava.
4. "Arquitetura modular torna o agente mais legível." Sem suporte sob capacidade igual; CBM sugere
   que há preço de desempenho a pagar e a medir.
5. "Feedback humano é recompensa." Contradito por COACH: depende da política atual.
6. "Divergência de política entre donos é a métrica estabelecida de efeito do treinador." Não é;
   não encontrei precedente, e o limiar de 0,10 bit não tem referente externo.
7. "A literatura de treino canino mostra que ensino e cuidado se separam." Mostra o contrário: nela
   os dois canais vêm colados, e é por isso que o braço "só cuidado" da V2 é a contribuição.
8. "Mais decisões com consequência aumentam o efeito do dono." Sem suporte; a literatura de
   consequência pós-ingestiva não tem treinador no laço.
9. "As peças do Dwarf Fortress são psicologicamente validadas." Cinco têm análogo na forma, uma está
   contestada, e nenhuma valida a implementação do jogo.
10. "Nosso replay bit a bit segue a prática estabelecida da área." Não há prática estabelecida para
    paridade Python-navegador de um aprendiz; é engenharia sem benchmark.

## Pendências e correções

**Correção no corpus do projeto.** O DOI `10.1016/j.appet.2016.12.015`, listado no corpus DigiBrain
como "Ackroff 2017", resolve no Crossref para Bodnar, R. J. (2018), *Conditioned flavor preferences in
animals: merging pharmacology, brain sites and genetic variance*, Appetite. Ou o DOI está errado, ou a
autoria atribuída está. Trabalhos reais de Ackroff e Sclafani existem com outros DOIs, por exemplo
`10.1016/j.appet.2010.04.011` e `10.1016/j.appet.2020.104793`.

**Não localizadas** (não citar até confirmar): Russell e Zimdars (2003), *Q-decomposition for
reinforcement learning agents*, ICML — sem registro no Crossref nesta busca; substituto verificado
para aprendizado localizado é Jacobs et al. (1991). Griffith et al. (2013), *Policy shaping*, NIPS —
sem registro no Crossref; é a alternativa bayesiana ao TAMER e vale uma segunda tentativa por outra
base. Gibson (1979), *The Ecological Approach to Visual Perception* — livro sem DOI, não confirmado
nesta busca; para affordance com registro verificado, usar Khetarpal et al.

**Verificação parcial.** Dos 47 DOIs conferidos no Crossref, 24 não têm resumo disponível nem no
Crossref nem no Europe PMC; para esses, a coluna `o_que_sustenta` está limitada ao que título e
metadados autorizam, e isso está marcado linha por linha. Os cinco itens de arXiv foram conferidos na
API do arXiv, porque DOIs `10.48550` não resolvem no Crossref.

**Infraestrutura.** OpenAlex e o conector de literatura indisponíveis nesta sessão. Uma segunda
passada com OpenAlex ativo deve ser feita antes de considerar Q5 e Q7 esgotadas, porque são as duas
perguntas em que a descoberta por nome é mais fraca.
