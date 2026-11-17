# Dreyfus e o corpo situado: as referências conferidas (2026-11-16)

Rodada pedida pelo Matheus em 2026-11-16, depois da conversa sobre *What Computers Can't Do*. São 18 referências: a crítica de
Dreyfus, o contraponto publicado e as linhas teóricas que ela toca no Digilab (corpo, aterramento do símbolo, modelo de mundo,
conhecimento social). A tabela é a [`v3_dreyfus_referencias_verificadas.csv`](v3_dreyfus_referencias_verificadas.csv), o registro bruto
é o [`v3_dreyfus_verificacao_crossref.json`](v3_dreyfus_verificacao_crossref.json) e o `.bib` é o
[`v3_dreyfus_referencias.bib`](v3_dreyfus_referencias.bib).

## Método

- **Existência:** o DOI resolveu no `api.crossref.org/works` (status 200). Título, autores, ano, veículo, volume e páginas foram
  conferidos, e nenhum registro tem `update-to`. Os dois livros sem DOI (Dreyfus 1972 e Dreyfus e Dreyfus 1986) foram confirmados
  por uma resenha com DOI.
- **Conteúdo:** o resumo veio do OpenAlex (`abstract_inverted_index`), do Semantic Scholar ou do Crossref. Nenhum texto completo
  foi lido.
- **O status segue o vocabulário da skill `literatura-digilab`:** VERIFICADA só quando o título ou o resumo sustentam o que a coluna
  `o_que_sustenta` diz.
  - Quando só havia o TLDR gerado pelo Semantic Scholar, ele não contou como resumo: a linha ficou (até a leitura do texto completo) EXISTÊNCIA CONFIRMADA; CONTEÚDO
    NÃO LIDO, exceto onde o próprio título já sustenta a tese (Brooks 1991, Friston 2010).
  - Nesses dois casos, a coluna se limita ao título e diz que o resumo do autor não foi obtido.

## O que fica

| status | n | referências |
|---|---|---|
| VERIFICADA | 16 | Dreyfus 2007 e Dreyfus 2002 (texto completo, 2026-11-16), Haugeland 1996, Collins 1996 e Koschmann 1996 (texto completo, 2026-11-17), McCarthy 1996, Brooks 1991, Varela et al. 1991, Pfeifer e Bongard 2006, Harnad 1990, Searle 1980, Damasio 1996, Friston 2010, Clark 2013, Lake et al. 2017, Collins 1990 |
| VERIFICADA (sem DOI) | 2 | Dreyfus 1972/1992 (pela resenha `10.2307/1575958`), Dreyfus e Dreyfus 1986 (pela resenha `10.1109/mex.1987.4307079`) |

O **Dreyfus 2007**, o texto mais próximo do Digilab, subiu a VERIFICADA no mesmo dia, depois da leitura do texto completo (pedido do
Matheus, D-LIT-DR-3). O Dreyfus 2002 seguiu o mesmo caminho (D-LIT-DR-5). São as duas referências desta rodada lidas por inteiro.

## O Dreyfus 2007, lido

Ensaio-resenha do livro de Wheeler (2005), na *Philosophical Psychology* 20(2), pp. 247-268. O argumento, com as páginas:

- **A relevância é o problema.** O que derrubou a IA simbólica foi saber quais fatos importam numa situação (o frame problem). Os
  frames de Minsky caem num regresso, porque é preciso um frame para reconhecer o frame (pp. 248-249).
- **Três IAs "heideggerianas" que contornam o problema em vez de resolvê-lo:**
  - os robôs de Brooks respondem a traços fixos e não aprendem (p. 250);
  - o Pengi de Agre objetifica as funções e a relevância, e também não aprende (p. 253);
  - as representações orientadas à ação de Wheeler e a mente estendida ainda carregam o problema (pp. 254-255, 262-263).
- **O que falta:** responder a um mundo organizado pelas necessidades, interesses e capacidades do corpo, sem que a mente imponha
  sentido a um dado sem sentido (p. 251).
- **A proposta: a neurodinâmica de Walter Freeman.**
  - O coelho com fome procura, e as conexões se reforçam na medida em que o resultado satisfez a necessidade (p. 258).
  - Cada experiência significativa refaz a paisagem de atratores inteira, sem representação fixa (pp. 258-261).
  - As transições entre atratores são discretas, então dá para modelá-las num computador (p. 261).
  - Na nota 11 (p. 267), Dreyfus propõe somar ao modelo um aprendizado por diferença temporal ator-crítico para a perícia.
- **A conclusão é pessimista (p. 265).** Mesmo essa IA precisaria de um modelo de um corpo como o nosso, com necessidades, desejos,
  prazeres, dores, modos de mover e cultura, e ele julga isso irrealizável.
- **A nota 7 (p. 266)** restringe o artigo à significância que partilhamos com os animais, e não ao sentido unicamente humano.

**O que autoriza dizer no Digilab:** que a relevância vir das necessidades do corpo, e o aprendizado por consequência que reorganiza
o todo, são o desenho que Dreyfus aponta como o caminho certo.

**O que não autoriza:**
- dizer que o Digilab resolve o frame problem;
- dizer que o corpo químico é "um corpo como o nosso";
- atribuir a Dreyfus a leitura de que, para um pet, basta a significância animal. Essa leitura é nossa, construída a partir da
  nota 7.

## O Dreyfus 2002, lido

*Phenomenology and the Cognitive Sciences* 1, pp. 367-383, também lido no texto completo no mesmo dia (D-LIT-DR-5). O argumento:

- **A tese (pp. 367-368):** aprender e agir com perícia não exigem representação mental nem cerebral. Os conceitos são o arco
  intencional e a pega máxima, de Merleau-Ponty.
- **Os cinco estágios da perícia (pp. 368-372):** a perícia é discriminar situações cada vez mais finas, cada uma pareada com a sua
  resposta. No estágio proficiente, as experiências boas e ruins reforçam o que dá certo (p. 370).
- **As redes neurais (pp. 374-375):** servem de modelo de um passado que muda a percepção sem guardar memórias. Mas o que conta como
  "o mesmo tipo" quem define é o projetista.
- **Três restrições do corpo à generalização (p. 376):**
  - a arquitetura do cérebro;
  - a ordem e a frequência das experiências, que dependem do corpo e do mundo;
  - o sucesso medido pela satisfação do agente. No aprendizado por reforço, quem define o sucesso é o pesquisador.

  Por isso, redes sem corpo ficam em desvantagem (pp. 376-377).
- **Agir sem representar o objetivo (pp. 377-383):** é a pega máxima, contra Searle. Os atratores de Freeman explicam o movimento:
  o estado do cérebro tende ao mínimo de energia mais próximo, sem representar o alvo.

**O que autoriza dizer no Digilab:** que medir o sucesso pela satisfação do corpo, e não por uma recompensa escolhida pelo projetista,
e deixar a ordem das experiências pesar são as restrições que Dreyfus aponta. A segunda faz par com a anedota da ordem de apresentação
em Lehman et al. (2020).

**O que não autoriza:** dizer que o pet tem arco intencional ou pega máxima, ou que o corpo químico satisfaz as três restrições.

## As resenhas de 1996, lidas

As três resenhas de *Artificial Intelligence* 80 foram lidas no texto completo em 2026-11-17 (D-LIT-DR-6), no PDF do editor, aberto no
Chrome do Matheus.

- **Haugeland, "Body and world" (pp. 119-128):** a resenha é simpática e se concentra na Parte III do livro.
  - As três teses que ele atribui a Dreyfus: a inteligência é corporificada, situada e humana. As três dizem a mesma coisa: a
    inteligência mora no corpo, no mundo (pp. 119-120, 128).
  - Não há "instrução" independente do corpo: o padrão que produz uma ação depende do corpo particular e da situação concreta
    (pp. 121-123).
  - O que tem significado é o próprio mundo, não só as representações (pp. 123-125).
  - A ciência cognitiva deveria olhar para a neurobiologia e para a antropologia (p. 128).
- **Collins, "Embedded or embodied?" (pp. 99-117):** a resenha vê três falhas no livro.
  - O **erro profissional:** tratar a ciência e os domínios formais como fora da situação (pp. 99-103).
  - A **elisão filosófica:** confundir o corpo do indivíduo com a forma de vida do coletivo. O indivíduo partilha a forma de vida
    pela socialização linguística, e cães não se socializam assim (pp. 103-106).
  - O **erro sociológico:** quem usa o computador conserta as deficiências dele sem notar (ELIZA, a calculadora) (pp. 106-108).
  - Além disso: as máquinas reproduzem as ações "mimeomórficas" (pp. 108-110); as redes neurais aprendem por estímulo-resposta, e isso
    não é socialização (pp. 113-115); a questão de fundo é a socializabilidade (p. 116).
- **Koschmann, "Of Hubert Dreyfus and dead horses" (pp. 129-141):**
  - resume os três argumentos de Dreyfus: o filosófico, o psicológico e o fenomenológico (pp. 129-133);
  - critica a omissão da literatura de raciocínio não monotônico (p. 133);
  - contesta o privilégio do especialista intuitivo: diante do problema novo, o especialista volta à análise (p. 134);
  - defende o papel da representação no ensino (pp. 136-138).

**O que autorizam dizer no Digilab:**
- o **erro sociológico** de Collins é o enquadramento para não atribuir ao pet o que o dono completa ao interpretar o comportamento;
- o ponto de Collins sobre estímulo-resposta é o enquadramento para não chamar o treino pelo dono de socialização;
- Koschmann dá o contraponto publicado aos cinco estágios.

**O que não autorizam:** nenhuma das três diz nada sobre pets virtuais nem valida mecânica do projeto.

## O que as verificadas autorizam dizer (e o que não)

- **A crítica existe e tem tese própria.** Dreyfus (1972; 2ª ed. 1992) sustenta que as máquinas sem corpo não imitam as funções mentais
  superiores, e a 2ª edição estende a avaliação ao conexionismo. As quatro suposições do livro não foram conferidas. O argumento da
  relevância está conferido no Dreyfus 2007 (pp. 248-249, e p. 264 para o exemplo da aposta de corrida do livro).
- **Há contraponto publicado.** McCarthy (1996) responde no mesmo número da *Artificial Intelligence*.
- **O corpo molda o comportamento.** Pfeifer e Bongard (2006) e Varela et al. (1991) sustentam o enquadramento, e Damasio (1996) o
  peso do estado do corpo na decisão. Nada disso valida o corpo químico do Digilab: são enquadramento, não evidência sobre o pet.
- **A fala precisa de chão.** Harnad (1990) sustenta o enquadramento da fala pelo decodificador de conceitos, e Searle (1980) o limite
  do que se diz da fala por LLM. Nunca escrever que o pet entende, nem que o decodificador resolve o aterramento.
- **O pet que planeja.** Clark (2013), Friston (2010) e Lake et al. (2017) dão o vocabulário do modelo de mundo, e Brooks (1991) o
  da posição contrária, sem representação central.
- **O conhecimento é social.** Collins (1990) enquadra o que o pet aprende com o dono. A pergunta do efeito do dono continua
  encerrada (`docs/LEITURA_CONSOLIDADA_DONO.md`).

**Nenhuma dessas fontes sustenta afirmação de novidade.** Valem as regras da skill: a regra 3 ("ensinado, não roteirizado" não é
diferencial) e a regra 9 (corpo com homeostase, aprendizado em vida e memória num agente já foi publicado).

## Limites

- Cinco referências foram lidas no texto completo: os dois artigos de Dreyfus, em cópias de terceiros da versão do editor, e as três resenhas de
  1996, no PDF do editor. As outras, só pelos resumos.
- O regex de DOI do `tools/verificar_relato.py` para no `(`. Os DOIs da Elsevier dos anos 1990, como `10.1016/0004-3702(91)90053-M`,
  entram cortados no `10.1016/0004-3702(91`. E já colide: as três resenhas de 1996 (McCarthy, Haugeland, Koschmann) viram
  `10.1016/0004-3702(95`, e o verificador trata o McCarthy, VERIFICADA aqui, como não citável. Até o regex mudar, cite o McCarthy num
  relato de PR sem o DOI (D-LIT-DR-4).
