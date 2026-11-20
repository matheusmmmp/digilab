# Valor evolutivo do aprendizado — apoio teórico das predições 1 a 5 da V2

Busca de 2026-10-06. Fundamenta as predições do experimento maior da V2
(braços P0, P1, P2, P2e, P3 × ambientes casado, descasado, mutável).

> Arquivo salvo pelo coordenador em 2026-10-06 a partir do texto que o Matheus colou na conversa (resultado de uma sessão do Claude
> Science). Conteúdo sem alteração.

## Limitação de infraestrutura, declarada de saída

Nesta sessão o ambiente de execução ficou indisponível (falha ao montar as pastas concedidas,
seis tentativas, ~160 s cada), então **não houve varredura por código** em Crossref, arXiv ou
Europe PMC. A verificação foi feita item a item pelo resolvedor de DOI e por repositórios de
acesso aberto; a descoberta, por busca web.

Consequências práticas, que valem para a leitura de todo o documento:

- a coluna "o que foi conferido" é precisa, mas a **cobertura é mais estreita** que o normal;
- não houve a auditoria Crossref × Europe PMC de lista de autores que é passo fixo do projeto;
- há um bloco de referências que aparecem em lista de referências revisada por pares e que
  **eu não resolvi** — estão separadas no fim, como pistas, e **não** podem ser citadas como
  se sustentassem afirmação de conteúdo.

## O achado que organiza tudo

**Kozielska, M. e Weissing, F. J. (2024).** *A neural network model for the evolution of
learning in changing environments.* PLOS Computational Biology 20(1):e1011840.
DOI `10.1371/journal.pcbi.1011840`. CC BY. **Texto completo lido**, mais o registro de
revisão por pares publicado com o artigo.

É quase um gêmeo teórico do desenho da V2, e por isso vale listar a correspondência antes das
predições:

- os pesos iniciais da rede são **herdados**, e o aprendizado modifica **apenas os quatro pesos
  ligados ao nó de saída** — o resto é geneticamente fixo. É a mesma arquitetura lógica de
  "só o lobo de decisão aprende";
- o aprendizado é por **erro de predição** (regra delta sobre a diferença entre predição e
  realidade), mesma família do feedback tratado como vantagem;
- os pesos modificados pelo aprendizado **não** são herdados, só os genes que especificam os
  pesos do início da vida. É Baldwin, não Lamarck, exatamente como no projeto;
- o ambiente é um perfil gaussiano de qualidade sobre pistas, e a mudança desloca o pico: a
  pista preferida deixa de ser a boa. É o casado/descasado da V2;
- há trade-off explícito entre explorar (aprender) e aproveitar o que já se sabe (forragear),
  com **duração de vida** como parâmetro (50 e 500 passos).

**O que ele não cobre.** A mudança ambiental acontece **entre gerações**, não dentro da vida.
Essa limitação está no próprio registro de revisão por pares publicado com o artigo, onde o
revisor 1 observa que a sabedoria recebida da área enfatiza variação **dentro** da geração e
cobra a discussão da relação com o modelo de Stephens (1991).

*Leitura nossa:* o braço **mutável** da V2 fica fora do escopo direto desse modelo e é onde a
teoria disponível é mais fraca.

## Predição 1 — no casado, P0 vence; aprender só custa

**Estado: APOIADA.**

Kozielska e Weissing mostram que, no regime de mudança rara e pequena, as redes sem aprendizado
alcançam praticamente o mesmo desempenho das que aprendem e **ainda têm vantagem de aptidão**,
porque não perdem tempo de forrageamento; e quando a duração do período de aprendizado é deixada
evoluir, ela **converge para zero** nesse regime — o aprendizado é perdido da população. O
mecanismo que o substitui é o rastreamento genético ("adaptive tracking"), que funciona bem
justamente quando a mudança é rara ou pequena.

O custo tem apoio empírico independente e mais severo do que "custo de exploração":
**Mery e Kawecki (2003)**, `10.1098/rspb.2003.2548`, demonstram em *Drosophila* um custo
**constitutivo** da capacidade de aprender — um trade-off com capacidade competitiva larval que é
pago independentemente de o aprendizado ser efetivamente usado.

*Leitura nossa:* isso é mais forte do que a predição 1 supõe. No modelo da V2 o custo de P1
aparece só quando ele explora; na biologia há um custo que existe mesmo quando o aprendiz não é
usado. E como a V2 não tem seleção entre gerações neste experimento, o esperado é empate ou
pequena vantagem de P0 — **não** a extinção do aprendiz.

## Predição 2 — no descasado e no mutável, P1 vence P0 se a vida for longa

**Estado: APOIADA COM RESSALVA.** Concorda na direção, discorda na forma.

Direção. Com mudança frequente ou de grande magnitude, o aprendizado melhora muito o casamento
entre a qualidade real do ambiente e a predita. O ponto mais útil para o descasado é que **o prior
herdado pode ser muito ruim sem prejuízo**, porque o aprendizado o corrige: no artigo, o perfil
innato fica "way off target" e o desempenho pós-aprendizado ainda é bom.

Suporte experimental: **Dunlap e Stephens (2009)**, `10.1098/rspb.2009.0602`, em 30 gerações de
*Drosophila*, decompõem a mudança ambiental em **confiabilidade da experiência** e
**previsibilidade da melhor ação**, e mostram que alguns tipos de mudança favorecem o aprendizado
enquanto outros selecionam contra ele. O desenho mapeia diretamente nos três ambientes da V2.

A condição de vida longa também tem apoio: o aprendizado é menos provável em organismos de vida
curta que não podem gastar muito da vida explorando, e com vida de 50 em vez de 500 passos o
período de aprendizado evoluído encolhe em termos absolutos.

**Onde discorda — ressalva de registro obrigatório.** A relação não é monotônica. A aptidão é
maximizada num **número intermediário** de episódios de aprendizado; os retornos de mais episódios
diminuem até virarem negligenciáveis; e, explicitamente, um período de aprendizado mais longo
**nem sempre** leva a melhor desempenho. Existe ótimo interior e platô.

*Leitura nossa:* "se a vida for longa o bastante" está certo como direção, mas não implica que mais
vida seja sempre melhor. Medir só duas durações de vida não distingue monotonicidade de platô.

## Predição 3 — P2 chega lá com menos consequências experimentadas que P1

**Estado: APOIADA, por via diferente da que a predição supõe.**

O apoio forte não é "informação economiza amostragem" e sim **por que copiar funciona**:
**Rendell et al. (2010)**, `10.1126/science.1184719`, num torneio aberto de estratégias de
aprendizado social, acharam que estratégias fortemente baseadas em informação social venceram
**mesmo quando a informação associal não era mais custosa**. A razão: os demonstradores exibiam o
comportamento de maior retorno do próprio repertório, filtrando informação para quem copiava sem
qualquer intenção de ensinar.

*Leitura nossa:* a vantagem de P2 vem de a informação já chegar filtrada, não de economia de
tentativas. Isso muda o que medir — o ganho deveria desaparecer se o professor emitir informação
não correlacionada com a qualidade.

**Kendal et al. (2018)**, `10.1016/j.tics.2018.04.003`, acrescentam um ponto que afeta a ablação
de arbitragem: indivíduos alternam entre estratégias com flexibilidade e usam várias ao mesmo
tempo, e não há correspondência um-para-um entre a heurística psicológica e o padrão observado.

*Leitura nossa:* um agente com arbitragem fixa entre necessidade própria e pedido do professor é
mais rígido do que o que a literatura descreve.

## Predição 4 — P2e piora no começo e se recupera quando a consequência refuta a informação

**Estado: SEM APOIO DIRETO.**

Não localizei trabalho que meça a trajetória de recuperação depois de informação social errada num
agente que também tem acesso à consequência.

O mais próximo é o resultado de Rendell et al.: informação social é valiosa **porque** vem filtrada
por quem já escolheu bem. Isso implica que informação social **errada** remove exatamente a
propriedade que a torna valiosa, e não apenas adiciona ruído.

Há um motivo teórico para esperar recuperação lenta, que vem de Kozielska e Weissing: quando o
aprendizado eficiente evolui, as redes deixam de rastrear o ambiente geneticamente e passam a
**depender inteiramente** do aprendizado, com o perfil innato estável ao longo do tempo.

*Leitura nossa:* a predição é plausível, mas o tempo de recuperação é a quantidade a registrar, e
não há referência que dê expectativa de magnitude. Um aprendiz que depende inteiramente do canal
aprendido é, por construção, mais exposto a canal ruim.

## Predição 5 — P3 fica perto de P0; reforço explícito ensina pouco além da consequência

**Estado: CONTESTADA.** Esta é a divergência mais séria do conjunto.

**Ho, M. K., MacGlashan, J., Littman, M. L. e Cushman, F. (2017).** *Social is special: A
normative framework for teaching with and learning from evaluative feedback.* Cognition
167:91-106. DOI `10.1016/j.cognition.2017.03.006`.

O artigo ataca precisamente a premissa da predição 5. O resumo registra que psicólogos
frequentemente supuseram que o "feedback avaliativo" influencia o comportamento pelos mecanismos
padrão de aprendizado a partir de contingências ambientais, e que — apesar da parcimônia dessa
suposição — programas de pesquisa construídos sobre ela, em psicologia do desenvolvimento,
comportamento animal e interação humano-robô, tiveram sucesso limitado. A tese dos autores é que
mecanismos especializados são favorecidos no caso de feedback avaliativo vindo de um parceiro
social, e que ele funciona melhor quando tratado como **comunicação sobre o valor de uma ação**,
não como recompensa.

**Risco de interpretação, a registrar antes da run.** Se o aprendiz de P3 tratar elogio e bronca
como sinal de recompensa, a predição 5 pode se confirmar **pelo motivo errado** — seria artefato da
arquitetura escolhida, não um fato sobre canais de ensino. Nesse desenho, P3 e P2 diferem em duas
coisas ao mesmo tempo:

1. o **momento** do sinal (antes × depois da ação), que é o que a predição quer testar;
2. a **interpretação** do sinal (informação × recompensa), que é confundidor.

É preciso uma variante de P3 que isole só o momento.

## Resumo por ambiente

| | casado | descasado | mutável |
|---|---|---|---|
| **P0 (só herdado)** | favorecido; rastreamento genético basta | prior "way off target"; pior | sem teoria direta (modelos tratam mudança entre gerações) |
| **P1 (consequência)** | custo sem benefício; pode ser constitutivo | favorecido; corrige prior ruim | esperado favorecido; braço com teoria mais fraca |
| **P2 (informação)** | sem ganho esperado | favorecido; vantagem vem de informação pré-filtrada | idem |
| **P2e (informação errada)** | dano esperado | dano maior que ruído: remove a filtragem | idem |
| **P3 (reforço)** | ≈ P0 | a teoria prevê que **pode** superar P1 se tratado como comunicação | idem |

## Precedente que cruze plasticidade × regularidade do ambiente × canal de professor

**Não encontrei.** O cruzamento se parte em dois blocos disjuntos — o mesmo padrão estrutural
encontrado na revisão de setembro sobre criação × seleção:

- Kozielska e Weissing cruzam plasticidade × regularidade do ambiente, **sem professor**;
- Ho et al. e a linha de ensino têm o professor, **sem manipulação de regularidade ambiental**;
- Rendell et al. têm informação social, **sem evolução do prior herdado**.

Isso é resultado negativo de busca lexical, com a cobertura estreitada por não ter havido varredura
por código. Vale como pista de lacuna, não como prova de inexistência.

## Referências verificadas nesta sessão

| referência | DOI | o que foi conferido |
|---|---|---|
| Kozielska e Weissing 2024, PLOS Comput Biol | `10.1371/journal.pcbi.1011840` | texto completo e registro de revisão |
| Dunlap e Stephens 2009, Proc R Soc B | `10.1098/rspb.2009.0602` | resumo |
| Dunlap e Stephens 2014, PNAS | `10.1073/pnas.1404176111` | resumo; o registro traz comentário publicado contestando o artigo |
| Mery e Kawecki 2002, PNAS | `10.1073/pnas.211451698` | resumo |
| Mery e Kawecki 2003, Proc R Soc B | `10.1098/rspb.2003.2548` | resumo |
| Rendell et al. 2010, Science | `10.1126/science.1184719` | resumo |
| Kendal et al. 2018, Trends Cogn Sci | `10.1016/j.tics.2018.04.003` | resumo |
| Ho et al. 2017, Cognition | `10.1016/j.cognition.2017.03.006` | resumo |
| Stephens 1991, Behav Ecol | `10.1093/beheco/2.1.77` | título e metadados |
| DeWitt, Sih e Wilson 1998, Trends Ecol Evol | `10.1016/S0169-5347(97)01274-3` | título e metadados |
| Snell-Rood 2013, Anim Behav | `10.1016/j.anbehav.2012.12.031` | título e metadados; conteúdo não usado nesta síntese |
| Laland 2004, Learn Behav | `10.3758/BF03196002` | título e metadados; conteúdo não usado nesta síntese |

Sobre o comentário ao PNAS 2014: a existência do comentário está no registro do artigo, mas **não
resolvi o DOI do comentário** nesta sessão. Não citar o comentário como fonte até resolver.

## Pistas para a próxima passada — NÃO verificadas

Os itens abaixo aparecem na lista de referências de Kozielska e Weissing (2024), que é fonte
revisada por pares, mas **não foram resolvidos por mim**. Não servem para sustentar afirmação de
conteúdo. Três deles podem mudar a leitura das predições:

**Prioridade 1**

- Dunlap, A. S., Austin, M. W. e Figueiredo, A. (2019). *Components of change and the evolution of
  learning in theory and experiment.* Anim Behav 147:157-166. `10.1016/j.anbehav.2018.05.024`.
  A revisão mais no alvo de tudo que apareceu.
- Liedtke, J. e Fromhage, L. (2019). *Need for speed: Short lifespan selects for increased learning
  ability.* Sci Rep 9. `10.1038/s41598-019-51652-5`. O título aponta na direção **oposta** à
  condição de vida longa da predição 2.
- Eliassen, S., Jørgensen, C., Mangel, M. e Giske, J. (2009). *Quantifying the adaptive value of
  learning in foraging behavior.* Am Nat 174:478-489. `10.1086/605370`.

**Prioridade 2**

- Dunlap, A. S. e Stephens, D. W. (2016). *Reliability, uncertainty, and costs in the evolution of
  animal learning.* Curr Opin Behav Sci 12:73-79. `10.1016/j.cobeha.2016.09.010`.
- Botero, C. A., Weissing, F. J., Wright, J. e Rubenstein, D. R. (2014). *Evolutionary tipping
  points in the capacity to adapt to environmental change.* PNAS. `10.1073/pnas.1408589111`.
- Ellefsen, K. O., Mouret, J.-B. e Clune, J. (2015). *Neural modularity helps organisms evolve to
  learn new skills without forgetting old skills.* PLoS Comput Biol 11. `10.1371/journal.pcbi.1004128`.
  Relevante à ablação de arquitetura modular.
- Dridi, S. e Lehmann, L. (2016). *Environmental complexity favors the evolution of learning.*
  Behav Ecol 27:842-850. `10.1093/beheco/arv184`.
- Kerr, B. e Feldman, M. W. (2003). *Carving the cognitive niche.* J Theor Biol 220:169-188.
  `10.1006/jtbi.2003.3146`.
- Aoki, K. e Feldman, M. W. (2014). Theor Popul Biol 91:3-19. `10.1016/j.tpb.2013.10.004`.
- Fawcett, T. W., Hamblin, S. e Giraldeau, L.-A. (2013). *Exposing the behavioral gambit.*
  Behav Ecol 24:2-11. `10.1093/beheco/ars085`.
- Nolfi, S. e Floreano, D. (1999). *Learning and evolution.* Auton Robots 7:89-113.
  `10.1023/A:1008973931182`.
- Méndez Salinas, E., Weissing, F. J. e Kozielska, M. (2023). *Neural network models for the
  evolution of associative learning.* bioRxiv. `10.1101/2023.07.21.549996`.
- Ackley, D. e Littman, M. (1992). *Interactions Between Learning and Evolution.* Em: Artificial
  Life II, SFI Studies in the Sciences of Complexity, pp. 487-509. Sem DOI, mas agora com registro
  bibliográfico independente — estava NÃO LOCALIZADA na revisão de setembro.
