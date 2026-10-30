# TAREFA — Terceira revisão de literatura para a V2: o corpo digital (Claude Science)

> **V2, congelado em 2026-10-30** (tag `v2-final`). O estado em que este documento fica na V3 está em `docs/FECHAMENTO_V2.md`; o
> plano da V3, em `docs/PLANO_V3.md`.

Este é o prompt para colar numa sessão do Claude Science. A sessão não tem acesso ao repositório, que é privado, então o contexto vai
abaixo. **Só literatura:** sem código, sem simulação e sem números do projeto.

---

## Quem pede e para quê

É um projeto pessoal de pesquisa em vida artificial. Não é trabalho acadêmico de pós-graduação; não associe a nenhum programa.

O projeto simula um pet virtual que aprende durante a vida. Ele é determinístico, as predições são registradas antes de rodar, e cada
pergunta tem calibração e validação separadas.

Estamos dando ao pet um **corpo químico** inspirado no Creatures 3:
- químicos;
- órgãos;
- receptores e emissores;
- os drives lidos como químicos.

Esta revisão serve para desenhar **a próxima etapa do corpo**: órgãos com força vital, dano, cura e morte. Também serve para saber o que
a literatura diz sobre um corpo químico ajudar ou atrapalhar o aprendizado.

## O que já temos no desenho (contexto, sem números)

- **Os químicos.** Cada drive (fome, higiene, energia, humor, saúde) é a leitura de um químico de "falta", em aritmética inteira. Isso vale
  também para os drives novos: tédio, curiosidade, solidão, estresse, a vontade de fazer as necessidades e um conforto que o carinho dá.
- **Os dois órgãos que já existem:**
  - **a digestão:** a comida entra num estômago e é convertida a uma taxa;
  - **a Vida:** um relógio químico que decai e muda o estágio de desenvolvimento por receptores.

  Os dois sempre funcionam: ainda não há dano nem morte por órgão.
- **O sinal de aprendizado** sai do corpo. A recompensa é a redução dos drives, uma formalização de reforço homeostático (Keramati e Gutkin
  2014, `10.7554/eLife.04811`, já verificado no projeto).
- **O pet sente o corpo só por receptores.** Ele não lê o estado interno inteiro.
- **O tédio** é medido pela variedade recente de atividades, e não pelo tempo parado. Isso veio da revisão anterior: Burn 2017,
  `10.1016/j.anbehav.2017.06.006`.
- **A etapa seguinte, ainda não desenhada:**
  - órgãos com força vital, dano, cura e falência;
  - lesões como dano de órgão;
  - genes que ligam por estágio;
  - um genoma de fisiologia.
- **Mais adiante:** um automodelo aprendido por uma rede, que prevê o próprio corpo, para o pet "saber de si".

## As seis perguntas, em ordem de prioridade

### 1. Os órgãos do Creatures: o que a fonte primária diz

- O que Grand e Cliff 1998 (`10.1023/A:1010042522104`) e Cliff e Grand 1999 (`10.1162/106454699568683`) dizem sobre:
  - a bioquímica: químicos, reações, receptores, emissores e meia-vida;
  - os órgãos: força vital, dano, cura, energia de reparo e morte;
  - como o corpo alimenta o aprendizado do cérebro (o reforço por químicos de recompensa e punição).
- Que outras fontes primárias existem, com registro bibliográfico conferível? Pistas: o livro de Steve Grand, *Creation: Life and How to
  Make It* (2000); outros textos dele ou de Cliff sobre a bioquímica.
- **Separe sempre** o que é fonte primária do que é documentação de fã (Creatures Wiki, CDN) ou código de reimplementação (openc2e). Esses
  servem só como pista.
- **Entregue:** o modelo de órgão do Creatures descrito pela fonte primária, com o que for detalhe só de fã marcado.

### 2. Química artificial estável

- A literatura de química artificial (artificial chemistries): que revisões existem? Pista: uma revisão na revista *Artificial Life*,
  por volta de 2001.
- **Como evitar** que um sistema de reações com receptores e emissores exploda, oscile ou trave? Que propriedades garantem um ponto de
  equilíbrio?
- Que práticas existem para calibrar taxas e meias-vidas num sistema assim?
- **Entregue:** os riscos de estabilidade de um corpo químico com 10 a 20 químicos e uns poucos órgãos, e as salvaguardas que a literatura
  recomenda.

### 3. Sistemas endócrinos artificiais e hormônios em agentes

- Controle de comportamento por hormônios artificiais em agentes e robôs. Pistas:
  - os trabalhos de Lola Cañamero sobre motivação, emoção e hormônios em robôs autônomos;
  - a literatura de "artificial endocrine system" e "artificial hormone system".
- Como os hormônios modulam o aprendizado e não só a ação?
- **Entregue:** os mecanismos de modulação que podem entrar num corpo químico sem tornar o sistema opaco, e o que medir para saber se um
  hormônio está agindo.

### 4. O corpo químico ajuda ou atrapalha o aprendizado?

- Que evidência há, em agentes artificiais, de que um corpo com drives químicos melhora o aprendizado ou a adaptação, comparado com uma
  recompensa externa simples? Isso vale para o reforço homeostático além de Keramati e Gutkin, a interocepção e a alostase.
- **Como combinar vários drives sem que um domine.** Na revisão anterior isso ficou sem resposta.
- **Entregue:** os achados, com a força da evidência. Diga também onde a literatura sugere que o corpo químico vira só uma camada extra de
  parâmetros, sem ganho.

### 5. Dano, dor, cura e morte

- Como modelos de vida artificial representam:
  - o dano a partes do corpo;
  - a nocicepção e a dor;
  - a cura com custo de energia;
  - a morte por falência?
- O que acontece com o aprendizado quando o agente pode se ferir e morrer? Há trabalhos sobre um agente que aprende a evitar o dano, e
  sobre o risco de "medo" excessivo?
- **Entregue:** um modelo mínimo defensável de órgão com força vital, dano e cura, e as medidas que dizem se o dano está ensinando ou só
  matando.

### 6. Interocepção e um automodelo do corpo

- Que literatura trata um agente que aprende a **prever o próprio corpo** (interocepção, inferência interoceptiva, automodelo)?
- Que medidas mostram que um automodelo aprendido é preciso e útil, e não só uma cópia do estado?
- **Entregue:** o que um automodelo do corpo deveria prever, e como avaliar se ele "sabe de si" sem acesso privilegiado ao estado interno.

## Regras

- **Só referência verificada.** Para cada item:
  - o DOI ou o arXiv conferido, com autores, ano e veículo;
  - marque se leu o **texto completo**, o **resumo** ou **só os metadados**. Se leu só parte, diga quais páginas.

  O que não conseguir localizar vai numa lista à parte, como "não localizado", e não é citado.
- **Marque preprint ou revisado por pares,** e se há correção ou retratação.
- **Nenhum trecho longo copiado:** no máximo uma frase curta entre aspas por fonte.
- **Nenhuma alegação de novidade para o projeto.** Se algo parecer inédito, escreva "não localizado nas buscas X, Y, Z".
- **Fonte de fã, wiki, blog ou código de reimplementação é pista, nunca evidência.** Isso inclui a Creatures Wiki, a CDN e o openc2e.
- **Não use DOI de memória:** resolva cada um antes de citar. Na revisão anterior, três DOIs de memória estavam errados.
- **Separe sempre "a fonte diz" de "minha leitura".**
- **Declare as limitações de busca,** por exemplo se não houve varredura por código.

## Entrega

1. **Uma tabela,** uma linha por referência, com as colunas:
   - referência;
   - tipo (par ou cinza);
   - DOI ou id;
   - quanto foi lido;
   - o que sustenta (uma frase);
   - a qual pergunta (1 a 6) se liga.
2. **Uma síntese por pergunta,** de meia página a uma página, terminando com o "entregue" pedido em cada uma.
3. **Divergências e riscos:** onde a literatura contradiz o desenho descrito acima, com a força da evidência.
4. **Lacunas:** o que não foi achado e as buscas feitas.
5. **Um BibTeX** só com as referências verificadas.
6. **Pistas para a próxima passada,** separadas e marcadas como não verificadas.
