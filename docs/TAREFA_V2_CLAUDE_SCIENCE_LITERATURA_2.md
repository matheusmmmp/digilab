# TAREFA — Segunda revisão de literatura para a V2 (Claude Science)

Este é o prompt para colar numa sessão do Claude Science. A sessão não tem acesso ao repositório, que é privado, então o contexto vai
abaixo. **Só literatura:** sem código, sem simulação e sem números do projeto.

---

## Quem pede e para quê

É um projeto pessoal de pesquisa em vida artificial. Não é trabalho acadêmico de pós-graduação; não associe a nenhum programa.

O projeto simula um pet virtual que aprende durante a vida. Ele é determinístico, as predições são registradas antes de rodar e cada
pergunta tem calibração e validação separadas. Esta revisão serve a seis perguntas abertas. Para cada uma, preciso saber o que a
literatura sustenta **antes** de escrever os planos de análise.

## O que já sabemos do nosso agente (contexto, sem números)

- **O agente de hoje** tem um prior herdado (regras fixas, o "instinto") e um aprendiz por reforço que ajusta pesos por cima dele, com uma
  regra da família COACH (MacGlashan et al., arXiv:1701.06049). **Ele não planeja.** Não tem modelo do mundo nem simulação de
  consequências.
- **Comparamos três cérebros sob o mesmo protocolo:**
  - o de pesos por regra, descrito acima;
  - uma célula recorrente de tempo contínuo (CfC) com ator-crítico e traço de elegibilidade;
  - um cérebro de circuitos especializados com células esparsas fixas e sinapses apetitivas e aversivas (inspirado no corpo cogumelo da
    mosca).

  Nenhum dos três planeja. O ator-crítico quase não aprendeu com a pouca experiência disponível.
- **O mundo** tem três frutas com efeitos diferentes. Em algumas condições a fruta preferida de nascença é a que faz mal, e em uma delas
  o efeito troca no meio da vida.
- **Achado 1:** o aprendiz aprende qual fruta evitar quando **escolhe entre várias**. Quando há **uma fruta só**, ele come o que houver,
  inclusive a que faz mal. A decisão de comer quase não aprende o efeito da fruta.
- **Achado 2:** o controle que usamos para separar o ensino do dono do cuidado do dono é um "acoplado" em malha aberta: o mesmo cuidado
  rejogado em outro agente, sem reagir a ele. Esse controle acabou cuidando pior que o original, e a separação ficou ilegível.
- **Achado 3:** num dos cérebros, uma punição dada pelo dono sobre uma fruta passou a valer para **todas** as frutas.
- **O próximo mundo** é um mapa 2D contínuo com regiões, comida deixada pelo jogador, frutas que caem de árvores, uma bola, visão por raio e
  cheiro. O pet escolhe um alvo e anda até ele.
- **O próximo corpo** segue os conceitos do Creatures 3: químicos, órgãos, receptores, drives como químicos, com tédio e curiosidade
  novos.
- **Os botões de elogiar e repreender saem.** O pet aprende pela consequência no corpo, e o "tapa" é um estímulo no corpo, não uma nota.

## As seis perguntas, em ordem de prioridade

### 1. Planejamento com modelo do mundo × hábito (a mais importante)

Queremos um pet que **pense**: que preveja "se eu fizer X, acontece Y" e escolha pelo resultado previsto, e não só por hábito reforçado.

- Quando o controle por modelo vence o controle por hábito? Como os dois se arbitram? Pistas: Daw, Niv e Dayan 2005, arbitragem por
  incerteza; Dolan e Dayan 2013, sobre metas e hábitos.
- Que planejadores **baratos** existem para um agente pequeno? Precisam caber em aritmética inteira e rodar num navegador. Pistas: Dyna
  (Sutton 1990), representação de sucessor (Dayan 1993; Momennejad et al. 2017) e busca de horizonte curto num modelo aprendido.
- Que evidência há em animais de "simular antes de agir"? Pistas: o replay e a pré-ativação no hipocampo, e a hesitação no ponto de
  escolha ("vicarious trial and error").
- **Entregue:** a arquitetura mínima defensável para "o pet planeja" e, principalmente, **a medida que separa "planejou" de "aprendeu o
  hábito"**. Por exemplo, a desvalorização do resultado, a reavaliação depois de uma mudança, ou a tarefa de dois passos.

### 2. O controle acoplado ("yoked") e suas alternativas

- A literatura de desenho com controle acoplado e as críticas a ele. Pista: Church 1964, sobre o problema do controle acoplado.
- Por que o acoplado em malha aberta pode enviesar a comparação?
- Que alternativas em malha fechada existem para separar "o que o treinador ensina" de "como ele cuida"?
- **Entregue:** um desenho de controle recomendado e o argumento que o sustenta.

### 3. Aprender o que faz mal sem alternativa (a fruta sozinha)

- A aversão condicionada ao gosto (o efeito Garcia): aprender a evitar uma comida com poucas experiências, com o mal-estar vindo depois.
- O que a literatura diz sobre aprender "não comer" quando não há alternativa no momento, contra aprender "escolher a outra"?
- Há explicação conhecida para um aprendiz por escolha relativa (que aprende preferências entre opções) falhar em aprender a rejeição
  absoluta?
- **Entregue:** os mecanismos candidatos e o que cada um prevê no nosso caso.

### 4. Tédio, curiosidade e o RL homeostático

- Motivação intrínseca e curiosidade em agentes artificiais. Pistas: Oudeyer e Kaplan 2007; Schmidhuber, sobre curiosidade e progresso de
  aprendizado.
- O tédio como estado em animais, ou o que mais se aproxima disso na literatura de bem-estar animal.
- O RL homeostático além de Keramati e Gutkin 2014 (`10.7554/eLife.04811`, que já usamos): como drives múltiplos viram recompensa sem um
  drive dominar os outros.
- **Entregue:** como desenhar drives de tédio e curiosidade cuja redução recompense brincar e explorar sem o agente ficar viciado nisso.

### 5. Forrageio em ambiente com manchas e mapa espacial

- O teorema do valor marginal: Charnov 1976, `10.1016/0040-5809(76)90040-x`. **Confirme o conteúdo:** só os metadados foram conferidos.
- Testes empíricos do teorema e onde ele falha.
- Aprender "onde costumo achar comida": mapas espaciais em forrageadores e a troca entre explorar e explorar o conhecido no espaço.
- **Entregue:** que medidas usar para "explorar compensou" num mapa 2D, e que previsões o teorema faz para o nosso mundo.

### 6. Punição e generalização do medo

- Por que uma punição ligada a uma opção se espalha para outras: a generalização do condicionamento aversivo e os gradientes de
  generalização.
- A punição dada por um parceiro social contra a consequência natural: o que muda no aprendizado e no bem-estar. Já temos Casey et al.
  2021 (`10.1038/s41598-021-97743-0`) e Vieira de Castro et al. 2020 (`10.1371/journal.pone.0225023`) sobre treino aversivo em cães;
  procure o que **estende ou contradiz** esses dois.
- **Entregue:** o que esperar de um "tapa" como estímulo no corpo, e o que medir (medo, estresse, vínculo, generalização).

## Regras

- **Só referência verificada.** Para cada item, o DOI ou o arXiv conferido, com autores, ano e veículo. Marque se leu o **texto completo** ou
  só o **resumo**. O que não conseguir localizar vai numa lista à parte, como "não localizado", e não é citado.
- **Marque preprint ou revisado por pares,** e se há correção ou retratação.
- **Nenhum trecho longo copiado:** no máximo uma frase curta entre aspas por fonte.
- **Nenhuma alegação de novidade para o projeto.** Se algo parecer inédito, escreva "não localizado nas buscas X, Y, Z".
- **Fonte de fã, wiki ou blog é pista, nunca evidência.** O Creatures 3 tem fonte primária no manual oficial e em Grand e Cliff 1998
  (`10.1023/A:1010042522104`).
- **Separe sempre "a fonte diz" de "minha leitura".**
- **Declare as limitações de busca,** por exemplo se não houve varredura por código.

## Entrega

1. **Uma tabela**, uma linha por referência, com as colunas: referência, tipo (par ou cinza), DOI ou id, texto lido (completo ou resumo), o
   que sustenta (uma frase) e a qual pergunta (1 a 6) se liga.
2. **Uma síntese por pergunta**, de meia página a uma página, terminando com o "entregue" pedido em cada uma.
3. **Divergências e riscos:** onde a literatura contradiz o desenho descrito acima, com a força da evidência.
4. **Lacunas:** o que não foi achado e as buscas feitas.
5. **Um BibTeX** só com as referências verificadas.
6. **Pistas para a próxima passada,** separadas e marcadas como não verificadas.
