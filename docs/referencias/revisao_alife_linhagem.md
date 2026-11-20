# Fundamentação bibliográfica: pet virtual com aprendizado online, temperamento inato e linhagem por procriação

Busca realizada em 29/09/2026. Escopo: oito trilhas definidas na especificação, mais o núcleo
técnico (bandit contextual) e a literatura de feedback humano que a especificação não listava mas
que a arquitetura exige. Tabela completa em `referencias_verificadas.csv`; entradas BibTeX em
`referencias.bib`. Nota de método e limites no fim do documento.

## Panorama

### Resumo da evidência

O projeto tem precedente técnico forte em quase todos os seus componentes isolados e nenhum
precedente na combinação que o define. Creatures (1996) já entregou genoma herdável, aprendizado
dentro da vida e linhagem entre jogadores num produto comercial; Black & White (2001) já entregou
treino por recompensa e punição do dono; Evo-RL (2021) já separou formalmente comportamento
instintivo de comportamento aprendido dentro de um mesmo agente; Fernando et al. (2018) já mostraram
evolução herdando o *prior* de aprendizado sem herdar o aprendido. O que não existe na literatura
localizada é um trabalho que **separe o efeito da criação pelo usuário do efeito da seleção pelo
usuário** — a pergunta que a especificação marcou como a lacuna mais importante a checar. Ela é
real, e a razão é estrutural: as duas literaturas relevantes são disjuntas.

## Trilhas

### Trilha 1. Agentes ALife em jogos

O registro primário mais forte do gênero é o de Creatures, e ele é melhor do que a memória do campo
costuma sugerir. O artigo de [Grand, Cliff e Malhotra (1997)](https://doi.org/10.1145/267658.267663)
descreve, em primeira pessoa, uma arquitetura em que cada *norn* coordena percepção e ação por uma
rede neural recorrente modular com aprendizado hebbiano, modulada por uma "bioquímica artificial"
com metabolismo e hormônios, e em que tanto a rede quanto a bioquímica são especificadas por uma
codificação genética de tamanho variável, com reprodução sexuada — ou seja, genoma herdável,
aprendizado ao longo da vida e linhagem, tudo num produto de 1996. A versão em revista
([Grand e Cliff, 1998](https://doi.org/10.1023/A:1010042522104)) e o relato do ecossistema de
usuários ([Cliff e Grand, 1999](https://doi.org/10.1162/106454699568683)) completam o quadro: os
jogadores criavam, cruzavam e trocavam norns em escala global, e o artigo de 1999 registra seleção
artificial exercida por essa população de donos.

Black & White ocupa a outra metade do espaço (o dono que ensina), mas com qualidade de evidência
muito inferior. O que existe é literatura cinza: o postmortem do estúdio
([Molyneux, 2001](https://www.gamedeveloper.com/design/postmortem-lionhead-studios-i-black-white-i-)),
que atribui a arquitetura de aprendizado a Richard Evans e afirma que a personalidade da criatura se
forma no uso, sem elementos aleatórios; e o capítulo técnico do próprio Evans (*Varieties of
Learning*, em Rabin, 2002), cuja existência e paginação foram confirmadas em listas de referências
revisadas por pares, mas cujo texto não foi possível consultar. O elo acadêmico que fecha a trilha é
o NERO ([Stanley, Bryant e Miikkulainen, 2005](https://doi.org/10.1109/TEVC.2005.856210)): jogador
treina agentes em tempo real e depois os põe a competir, com neuroevolução rodando durante a
partida.

A lacuna da trilha é de método, não de mecânica. Nenhum dos três publicou uma medida de quanto do
comportamento resultante é explicado pelo que o jogador fez. Creatures documenta o ecossistema;
Black & White afirma o efeito em material promocional e de postmortem; o NERO avalia desempenho da
neuroevolução, não a atribuição causal ao treinador humano.

### Trilha 2. Homeostase e aprendizado

[Keramati e Gutkin (2014)](https://doi.org/10.7554/eLife.04811) dão o resultado que torna "instinto =
drives homeostáticos" uma escolha defensável em vez de arbitrária: definindo recompensa como redução
de desvio homeostático, maximizar recompensa e manter estabilidade fisiológica passam a coincidir.
A tipologia de [Oudeyer e Kaplan (2007)](https://doi.org/10.3389/neuro.12.006.2007) separa motivação
intrínseca (novidade, progresso de aprendizado, competência) de recompensa externa, o que é
exatamente a distinção entre o que o pet quer por conta própria e o que o dono reforça. E
[Singh, Lewis, Barto e Sorg (2010)](https://doi.org/10.1109/TAMD.2010.2051031) fazem a ponte para a
trilha 3 ao argumentar que a própria função de recompensa interna pode ser produto de seleção — o que
fundamenta tratar o instinto como *prior* evoluído, e não como constante de projeto.

A lacuna aqui é que essa literatura é de agente isolado. Nenhum dos trabalhos localizados compõe um
drive homeostático com um sinal de feedback fornecido por um dono e mede qual dos dois governou o
comportamento. O trabalho mais próximo dessa composição,
[Magrans de Abril e Kanai (2018)](https://arxiv.org/abs/1801.07440), junta curiosidade e regulação
homeostática num só agente, mas permanece preprint sem versão revisada por pares localizada e não
tem dono no circuito.

### Trilha 3. Herança e aprendizado

Hinton e Nowlan (1987, *Complex Systems* 1, 495–502; sem DOI) fundaram o efeito Baldwin
computacional: aprendizado individual suaviza a paisagem de aptidão e acelera a evolução mesmo
quando nada do que foi aprendido é herdado.
[Whitley, Gordon e Mathias (1994)](https://doi.org/10.1007/3-540-58484-6_245) compararam diretamente
herança lamarckiana e efeito Baldwin sob a mesma função de aptidão e mostraram que a escolha entre as
duas altera o resultado — portanto é uma decisão que precisa ser justificada, não assumida. O suporte
mais direto para o desenho do projeto é [Fernando et al.
(2018)](https://doi.org/10.1145/3205651.3205763), que mostram a evolução produzindo uma inicialização
que torna o aprendizado posterior rápido, sem herdar o aprendizado em si: é literalmente "o genoma
herda o *prior*, não o caráter". E [Hallawa et al. (2021)](https://doi.org/10.1145/3449726.3459475)
é o precedente arquitetural mais próximo que esta busca encontrou, porque separa explicitamente
comportamento evoluível ("instintivo") de comportamento aprendível dentro do mesmo agente e deixa a
fronteira entre os dois ser decidida pela evolução.

Dois avisos vêm de fora da lista original. [Gupta et al.
(2021)](https://doi.org/10.1038/s41467-021-25874-z) mostram em larga escala que o que é herdado
(morfologia) altera a velocidade do que é aprendido, o que significa que genoma e treino não são
canais independentes nem no caso mais simples. E [Griffiths e Kalish
(2007)](https://doi.org/10.1080/15326900701326576) provam que, em aprendizado iterado com agentes
bayesianos, a distribuição entre gerações converge para o *prior* dos aprendizes — um resultado que
prevê, para uma linhagem de muitas gerações, que o traço do dono tende a ser lavado e o do *prior* a
dominar. A lacuna da trilha: em todos esses trabalhos a pressão seletiva é uma função de aptidão
automática, nunca uma pessoa.

### Trilha 4. Seleção artificial interativa

O survey de [Takagi (2001)](https://doi.org/10.1109/5.949485) é a referência canônica e já nomeia a
restrição que qualquer linhagem dependente de escolha do jogador vai encontrar: com o humano como
função de aptidão, o gargalo é a fadiga do avaliador. O [Picbreeder
(Secretan et al., 2011)](https://doi.org/10.1162/EVCO_a_00030) é o caso mais forte em escala real —
uma população evoluída exclusivamente por seleção humana colaborativa, com linhagens ramificadas e
usuários retomando o trabalho uns dos outros. O [Galactic Arms Race
(Hastings, Guha e Stanley, 2009)](https://doi.org/10.1109/TCIAIG.2009.2038365) mostra a saída para o
problema da fadiga: extrair a seleção do comportamento de uso, sem pedir avaliação explícita. O
antecedente conceitual são os biomorphs, descritos pelo próprio autor em
[Dawkins (1995)](https://doi.org/10.1142/9789812832061_0004), e a evolução interativa de imagens de
[Sims (1991)](https://doi.org/10.1145/127719.122752).

A lacuna é nítida e é a mesma em todos eles: o humano apenas *escolhe*. Em nenhum trabalho de
computação evolutiva interativa o humano treina o indivíduo dentro da vida dele. A função de
seleção humana e o ensino humano nunca aparecem no mesmo sistema avaliado.

### Trilha 5. Operadores e quality diversity

[Eshelman e Schaffer (1993)](https://doi.org/10.1016/B978-0-08-094832-4.50018-0) é a fonte primária
correta do cruzamento por mistura BLX-α; a alternativa com dispersão controlada por um índice é o SBX
de Deb e Agrawal (1995, *Complex Systems* 9, 115–148; sem DOI, versão autoadaptativa em
[Deb e Beyer, 2001](https://doi.org/10.1162/106365601750190406)). Para populações de NPCs, a
literatura relevante não é a de otimização e sim a de *quality diversity*:
[Mouret e Clune (2015)](https://arxiv.org/abs/1504.04909) definem o MAP-Elites, que mantém o melhor
indivíduo por célula de um espaço de características em vez de um ótimo único;
[Lehman e Stanley (2011)](https://doi.org/10.1162/EVCO_a_00025) mostram que buscar apenas novidade
comportamental pode superar a busca pelo objetivo em domínios enganosos; e
[Cully et al. (2015)](https://doi.org/10.1038/nature14422) dão a evidência revisada por pares de que
um arquivo de diversidade comportamental tem valor funcional, não apenas estético. Os mapas do
subcampo são [Pugh, Soros e Stanley (2016)](https://doi.org/10.3389/frobt.2016.00040),
[Cully e Demiris (2018)](https://doi.org/10.1109/TEVC.2017.2704781) e
[Chatzilygeroudis et al. (2021)](https://doi.org/10.1007/978-3-030-66515-9_4).

A lacuna: em toda a literatura de QD o espaço de características que define "diferente" é escolhido
pelo projetista. Nenhum trabalho localizado usa diferença *percebida pelo jogador* como descritor
comportamental, que é o que importa se a diversidade da população de pets tem de ser legível.

### Trilha 6. Personalidade e variância

Esta é a trilha com o ferramental quantitativo mais pronto para uso, e o projeto ainda não o usa.
[Réale et al. (2007)](https://doi.org/10.1111/j.1469-185X.2007.00010.x) estabelecem temperamento
animal como diferenças individuais consistentes entre contextos e no tempo, com eixos definidos
(audácia, exploração, atividade, agressividade, sociabilidade) — ou seja, "temperamento inato" é um
construto mensurável e não uma metáfora. [Sih, Bell e Johnson
(2004)](https://doi.org/10.1016/j.tree.2004.04.009) mostram que traços comportamentais vêm em
síndromes correlacionadas, o que implica que os traços de um pet não deveriam ser sorteados
independentemente uns dos outros. E [Dingemanse et al.
(2010)](https://doi.org/10.1016/j.tree.2009.07.013) dão o formalismo de normas de reação, intercepto
como nível médio do indivíduo, inclinação como plasticidade, que é exatamente a decomposição
necessária para separar temperamento de resposta ao treino.

Dois números servem de âncora. A meta-análise de [Dochtermann, Schwab e Sih
(2015)](https://doi.org/10.1098/rspb.2014.2201) estima que cerca de 52% da variação de personalidade
animal é atribuível a variação genética aditiva, com o restante em efeitos ambientais permanentes,
inclusive parentais e epigenéticos. E [Morrill et al. (2022)](https://doi.org/10.1126/science.abk0639),
com 18.385 cães por questionário e 2.155 genotipados, encontram que a maioria dos traços
comportamentais é herdável (h² > 25%) mas a raça explica apenas 9% da variação comportamental entre
indivíduos. Para um projeto que quer um genoma herdável e um caráter aprendido, esses dois valores
delimitam o alvo: linhagem restringe pouco, indivíduo e criação explicam muito.

A lacuna é que essa decomposição nunca foi aplicada a agentes artificiais. Nos animais ela é possível
porque existe repetibilidade e herdabilidade estimadas nos mesmos dados; num simulador ela seria mais
fácil, porque o experimentador controla a criação — e ninguém fez.

### Trilha 7. Vida artificial clássica

[Bedau (2003)](https://doi.org/10.1016/j.tics.2003.09.012) dá o vocabulário preciso, separando ALife
*soft* (simulação), *hard* (robótica) e *wet* (bioquímica); usar "soft ALife" com essa referência
evita a confusão com modelagem baseada em agentes, cuja definição de referência é
[Bonabeau (2002)](https://doi.org/10.1073/pnas.082080899). O valor metodológico da trilha está em
Tierra e Avida: [Ray (1993)](https://doi.org/10.1162/artl.1993.1.1_2.179) para a ideia de evolução
aberta em programas autorreplicantes, [Ofria e Wilke
(2004)](https://doi.org/10.1162/106454604773563612) para a plataforma, e sobretudo
[Lenski et al. (2003)](https://doi.org/10.1038/nature01568) como demonstração de que resultado
científico em ALife se obtém com tratamento e braço de controle. Karl Sims fecha o enquadramento com
a coevolução de morfologia e controle ([1994a](https://doi.org/10.1145/192161.192167)) e com a
competição direta como pressão seletiva ([1994b](https://doi.org/10.1162/artl.1994.1.4.353)); os
boids de [Reynolds (1987)](https://doi.org/10.1145/37401.37406) permanecem a referência padrão para
emergência a partir de regras locais.

A lacuna, aqui, é a ausência do humano: a ALife clássica fornece o enquadramento e a disciplina
experimental, não o dono. Usá-la como lente teórica é legítimo para o vocabulário e para o desenho de
experimento; não é uma fonte de suporte para afirmações sobre jogador.

### Trilha 8. Game design, apego, legibilidade

Aqui a qualidade da evidência cai muito, e vale separar os três assuntos. Sobre mecânicas de
*breeding* e linhagem, o único item com fonte primária é o postmortem de Black & White. As mecânicas
de Monster Rancher (combinação de dois monstros retirados, com o filho herdando traços dos dois) e
de Digimon World Championship (reversão a ovo no fim da vida, exigida como pré-requisito de
digievoluções posteriores) aparecem de forma consistente em verbetes enciclopédicos, guias e fóruns
de fã — inclusive com tabelas de herança de técnicas e listas de evoluções que exigem *egg-revert* —
mas nenhuma fonte primária (manual oficial, entrevista de desenvolvedor, postmortem) foi localizada,
e os relatos de fã divergem sobre o efeito da reversão nos *stats*. Pela hierarquia de fontes do
projeto, isso é pista, não evidência. A herança de atributos em Pokémon não foi buscada nesta revisão
e segue sem fonte.

Sobre apego, a literatura revisada por pares é fina: [Dodd, Fowler e Lottridge
(2025)](https://doi.org/10.1016/j.entcom.2025.100958) é uma revisão narrativa e serve de porta de
entrada; [Chesney e Lawson (2007)](https://doi.org/10.1075/is.8.2.09che) mediram companhia percebida
comparando pet virtual e pet real; [Rault (2015)](https://doi.org/10.3389/fvets.2015.00011) compara
pets vivos, robóticos e virtuais e serve de freio contra superestimar o vínculo com software. O
mecanismo mais plausível para apego a um pet treinado pelo próprio dono é o efeito IKEA
([Norton, Mochon e Ariely, 2012](https://doi.org/10.1016/j.jcps.2011.08.002)), mas com a
qualificação de [Marsh, Kanngiesser e Hood (2018)](https://doi.org/10.1016/j.cognition.2017.10.012):
o efeito depende de a tarefa ser concluída com sucesso. Um pet que o dono treina mal pode, por esse
mecanismo, valer menos e não mais.

Sobre legibilidade, a trilha existe e é utilizável. [Anderson et al.
(2019)](https://doi.org/10.24963/ijcai.2019/184) é o desenho que a hipótese de legibilidade do
projeto exige, porque mede compreensão de leigos em vez de assumi-la;
[Madumal et al. (2020)](https://doi.org/10.1609/aaai.v34i03.5631) mostram que ancorar a explicação
num modelo causal produz ganho mensurável sobre narrativa livre — o que é o argumento a favor de
restringir a fala ao registro do motivo; e [Milani et al. (2024)](https://doi.org/10.1145/3616864) é
o mapa atual do subcampo. A lacuna dupla: nada foi localizado sobre apego *entre gerações* de um pet
virtual, e nada sobre se o jogador atribui a causa correta a um comportamento emergente.

### Núcleo técnico e feedback humano

Nenhum dos dois estava nas trilhas da especificação, mas a arquitetura os exige.

A garantia de arrependimento para o algoritmo efetivamente usado no motor está em
[Agrawal e Goyal (2013)](https://arxiv.org/abs/1209.3352); a formulação de contexto-ação com payoff
linear e sua avaliação offline em [Li, Chu, Langford e Schapire
(2010)](https://doi.org/10.1145/1772690.1772758); a evidência empírica de competitividade do Thompson
sampling em Chapelle e Li (2011, NIPS 24; sem DOI); e as armadilhas práticas que atingem em cheio um
pet treinado por meses (não estacionariedade, *priors* mal calibrados) em
[Russo et al. (2018)](https://doi.org/10.1561/2200000070).

Do lado do dono, três resultados restringem o desenho. [Knox e Stone
(2009)](https://doi.org/10.1145/1597735.1597738) tratam o feedback humano como sinal de valor a ser
modelado, e não como recompensa de MDP. [MacGlashan et al.
(2017)](https://arxiv.org/abs/1701.06049) mostram que o feedback humano depende da política atual do
agente — é mais parecido com *advantage* do que com recompensa fixa —, o que muda qual algoritmo é o
correto. E [Thomaz e Breazeal (2008)](https://doi.org/10.1016/j.artint.2007.09.009) documentam
empiricamente como pessoas reais ensinam agentes: dão recompensa antecipatória, tentam guiar em vez
de só avaliar, e são inconsistentes. Isso tem consequência direta para os donos sintéticos do
projeto: o contraste realista para "dono coerente" não é ruído uniforme, é o dono humano típico, que
não é nenhum dos dois. [Amershi et al. (2014)](https://doi.org/10.1609/aimag.v35i4.2513) acrescentam
o requisito de que o usuário perceba o efeito do que fez, que é a formulação existente mais próxima
da hipótese de legibilidade.

## Síntese

### A lacuna central

Não foi localizado nenhum trabalho que separe o efeito da criação pelo usuário do efeito da seleção
pelo usuário em agentes artificiais, e a razão é
que as duas literaturas não se encontram. De um lado, a computação evolutiva interativa
(Takagi; Picbreeder; Galactic Arms Race; Sims; biomorphs) tem o humano **apenas como operador de
seleção**: não há treino dentro da vida do indivíduo. Do outro, o aprendizado interativo a partir de
feedback humano (TAMER; MacGlashan et al.; Thomaz e Breazeal; Christiano et al.; BASALT) tem o humano
**apenas como treinador**: não há reprodução nem linhagem. Creatures é o único sistema em que as duas
coisas aconteceram simultaneamente e em escala, e o registro publicado sobre ele é descritivo —
Cliff e Grand relatam o ecossistema e a seleção artificial exercida pelos jogadores, não um desenho
fatorial que isole os dois canais.

Existem, porém, quatro moldes metodológicos prontos. Whitley et al. mostram como manter uma função de
aptidão fixa e variar apenas o canal de herança, que é o mesmo movimento necessário aqui. Evo-RL
mostra como particionar comportamento instintivo e aprendido dentro de um agente, o que dá o ponto de
corte para medir cada canal. Dingemanse et al. e Dochtermann et al. fornecem o vocabulário de
partição de variância (intercepto versus inclinação; genético aditivo versus ambiental permanente).
E Morrill et al. são o único estudo grande que põe número na comparação linhagem versus indivíduo —
9% para raça — mas justamente com a criação fora de controle experimental, que é o problema que um
simulador elimina.

O desenho que fecha a lacuna é, portanto, um fatorial 2×2 em simulação pura: dono coerente versus
dono aleatório, cruzado com linhagem selecionada versus linhagem não selecionada, com o mesmo volume
de interação em todos os braços. Pelo que esta busca encontrou, isso não foi publicado.

Registro de estado do projeto, para não confundir literatura com trabalho próprio: o experimento E1
(plano congelado em `docs/PLANO_ANALISE_LINHAGEM.md`, rodada 1 em execução em 2026-09-29) já
implementa esse desenho, e com um fator a mais — 40 genomas × 4 donos × 4 ambientes, com semente de
genoma separada da semente de ambiente e ANOVA de três fatores cruzados. Os dois valores da trilha 6
servem de expectativa de magnitude para o gate de σ²_genoma: ~52% de variância genética aditiva em
personalidade animal, e apenas 9% de variância comportamental explicada pela raça em cães.

Uma ressalva honesta sobre essa conclusão: ela é um resultado negativo de busca por palavras-chave.
Seis consultas construídas especificamente para essa separação ("disentangling selection and shaping",
"human selection versus human training of artificial agents", "separating genetic and learned
contributions", "artificial selection by users of behaviour of learning agents", entre outras) não
retornaram nada pertinente no OpenAlex, e consultas equivalentes no arXiv também não. Ausência de
resultado em busca lexical é evidência fraca; o campo pode ter o trabalho sob vocabulário que não
tentei.

### Afirmações sem suporte

1. **"Treino por um dono coerente produz um pet melhor que feedback aleatório com o mesmo volume de
   interação."** Nenhum precedente publicado localizado. Além disso, Thomaz e Breazeal sugerem que o
   contraste está mal escolhido: o dono humano real não é coerente nem aleatório.
2. **"O comportamento do pet é ensinado pelo dono, não roteirizado" como diferencial.** O postmortem
   de Black & White já afirma exatamente isso em 2001, incluindo a ausência de elementos aleatórios
   na formação da personalidade. A afirmação de novidade não se sustenta; o que pode se sustentar é o
   teste falsificável com braço de controle, que é outra coisa.
3. **"Herdar o *prior* de aprendizado e não o caráter é um desenho novo."** Sem suporte como
   novidade: é precisamente o efeito Baldwin computacional (Hinton e Nowlan; Whitley et al.) e o
   resultado de Fernando et al. (2018).
4. **"Explicações ancoradas no motivo real aumentam a percepção de aprendizado."** Parcialmente
   apoiada no mecanismo (Madumal et al.; Anderson et al.), mas sem nenhum estudo localizado que
   ligue compreensão da explicação a percepção de aprendizado ou a apego, e nenhum em pet ou
   companion. Como enunciada, sem suporte.
5. **"O jogador se apega ao pet entre gerações."** Nenhuma evidência revisada por pares localizada
   sobre apego atravessando gerações de pet virtual. O efeito IKEA é sobre objetos construídos pelo
   próprio usuário e, por Marsh et al., depende de conclusão bem-sucedida.
6. **Precedentes de mecânica em Monster Rancher, Digimon World Championship e Pokémon.** Nenhum
   verificado em fonte primária. Hoje são nível de fã e não podem sustentar afirmação de precedência
   ou de desenho.
7. **"Artificial Life como lente teórica" acrescentando poder explicativo.** Bedau sustenta o
   vocabulário e Lenski et al. sustentam a disciplina experimental; nada na literatura localizada
   sustenta que o enquadramento ALife acrescente poder explicativo a um pet comercial. É escolha
   retórica, não afirmação apoiada.
8. **Competição entre pets treinados por donos diferentes como diferencial.** Sims (1994b) já usa
   competição direta como pressão seletiva e o NERO já põe agentes treinados por pessoas a competir.
   A parte nova possível é a atribuição causal do resultado ao treino, que ninguém mediu.
9. **"Juntar corpo com homeostase, aprendizado em vida e memória episódica num agente é novo."**
   Acrescentada pela C0 da V3 em 2026-10-30. Sem suporte como novidade: a combinação já está em
   Creatures (Grand e Cliff), Gadanho e Hallam (2001), na linha de Ho, Dautenhahn e Nehaniv
   (2003–2008) e em Goertzel et al. (2008), verificados em `v3c0_referencias_verificadas.csv`; a
   triagem de 2026-10-30 também a acha em Zamin e no Rity (SEM FONTE). O que pode se sustentar é o
   método: teste causal com braço de controle, num pet persistente, com replay determinístico, e
   mesmo isso sem alegar que ninguém o fez (`V3C0_SINTESE_TRIAGEM_2026-10-30.md`).

### Método e limites

Busca programática em 29/09/2026 sobre a API do OpenAlex (106 consultas em seis lotes), a API do arXiv
e a API do Crossref, complementada por busca web para literatura cinza de jogos. Cada referência
selecionada passou por duas checagens: resolução do DOI no Crossref com conferência de autores, ano,
tipo e veículo (60 DOIs no registro, cobrindo os 59 DOIs Crossref-checáveis citados na tabela; todos
resolveram, nenhum com campo `update-to` indicando retratação ou
errata), e leitura de título e resumo para confirmar que a fonte sustenta a afirmação que lhe foi
atribuída. Os quatro itens com DOI `10.48550/arXiv.*` não passam pelo Crossref (são registrados no
DataCite) e foram conferidos contra a API do arXiv, com título, autores e data de submissão;
`referencias_verificadas.csv` os marca como preprint quando não há versão revisada por pares.
Referências sem DOI foram classificadas como `VERIFICADA (sem DOI)` somente quando havia
registro bibliográfico independente; duas ficaram como `NÃO LOCALIZADA` e três itens de mecânica de
jogo como `NÃO VERIFICADA EM FONTE PRIMÁRIA`.

Três limites importam. Primeiro, a verificação de conteúdo foi feita sobre metadados e resumos, não
sobre texto completo: a coluna "o que sustenta" descreve o que título e resumo autorizam afirmar, e
qualquer uso de um desses trabalhos em texto de dissertação exige ler o artigo. Segundo, o capítulo
de Evans (2002), que é a fonte técnica de primeira mão sobre o aprendizado em Black & White, teve
existência confirmada mas não foi consultado — é a lacuna de fonte mais relevante desta revisão.
Terceiro, a conclusão sobre a lacuna central é um resultado negativo de busca lexical e deve ser
tratada como tal.
