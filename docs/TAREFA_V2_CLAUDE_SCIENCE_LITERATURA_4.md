# TAREFA: quarta passada de literatura da V2 — ler os PDFs que ficaram sem leitura (Claude Science)

> **V2, congelado em 2026-10-30** (tag `v2-final`). O estado em que este documento fica na V3 está em `docs/FECHAMENTO_V2.md`; o
> plano da V3, em `docs/PLANO_V3.md`.

Este é o prompt para colar numa sessão do Claude Science. Ele cumpre as decisões D-1 e D-2 de `docs/DEFINICOES_CORPO_V2.md`
(2026-10-07). **É só leitura:** nada de busca nova, código ou simulação.

---

## Quem pede e para quê

Este é um projeto pessoal de pesquisa em vida artificial. Não é trabalho acadêmico de pós-graduação, e não deve ser associado a nenhum
programa.

O projeto simula um pet virtual com um corpo químico inspirado no Creatures 3. Na terceira revisão (o corpo digital), vários itens ficaram
como "PDF obtido, não lido" ou "só metadados", e por isso não podem sustentar nenhuma afirmação no projeto. Esta passada lê esses itens
para decidir o que eles sustentam.

## O que ler, em ordem de prioridade

1. **Grand, Cliff e Malhotra 1997**, *Creatures: artificial life autonomous software agents for home entertainment*, Agents '97,
   `10.1145/267658.267663`. Na revisão anterior foi lido só o resumo. Agora, o texto completo. O que se quer saber:
   - se o artigo descreve **receptores e emissores**, a **meia-vida** dos químicos e os **drives como químicos**;
   - o que diz sobre os **órgãos**: força vital, dano, cura, energia de reparo e morte;
   - como os químicos de **recompensa e punição** chegam ao aprendizado da rede.
2. **Grand e Cliff 1998**, *Creatures: Entertainment Software Agents with Artificial Life*, Autonomous Agents and Multi-Agent Systems,
   `10.1023/A:1010042522104`. Na revisão anterior só os metadados foram conferidos. São as mesmas três perguntas do item 1.
3. **Dittrich e Speroni di Fenizio 2007**, *Chemical Organisation Theory*, Bulletin of Mathematical Biology, `10.1007/s11538-006-9130-8`.
   O PDF foi obtido e não foi lido. O que se quer saber:
   - as definições de conjunto **fechado** e **automantido**, e de organização;
   - se o artigo diz que uma organização tem a ver com estabilidade ou persistência da dinâmica (e com que condições);
   - se o critério pode ser checado por inspeção do grafo de reações, sem simular.
4. **Lones, Lewis e Cañamero 2018**, *A Hormone-Driven Epigenetic Mechanism for Adaptation in Autonomous Robots*, IEEE TCDS 10(2):445-454,
   `10.1109/TCDS.2017.2775620`. O PDF foi obtido e não foi lido. O que se quer saber:
   - como o hormônio age: no ganho de um sensor, na taxa de aprendizado, num limiar ou em outra coisa;
   - o que o artigo mede para mostrar que o hormônio teve efeito;
   - se há uma condição de controle com o hormônio fixo.
5. **Hulme, Morville e Gutkin 2019**, *Neurocomputational theories of homeostatic control*, Physics of Life Reviews,
   `10.1016/j.plrev.2019.07.005`. O PDF foi obtido e não foi lido. O que se quer saber: o que a revisão diz sobre **combinar vários drives**
   num sinal de recompensa, e sobre o peso de cada drive depender do estado interno.

Se algum item não puder ser acessado em texto completo, diga isso, e diga também até onde a leitura chegou.

## Regras

- **Só o que foi lido.** Para cada item, marque se leu o texto completo, o resumo ou só os metadados. Se leu só parte, diga quais
  páginas ou seções.
- **Separe sempre "a fonte diz" de "minha leitura".**
- **Nenhum trecho longo copiado.** No máximo uma frase curta entre aspas por fonte.
- **Nenhuma alegação de novidade** para o projeto.
- **Não use DOI de memória.** Os DOIs acima já foram resolvidos. Se algum não abrir, diga isso.
- **Fontes que são só pista:** Creatures Wiki, CDN e openc2e servem só como pista, nunca como evidência, e ficam numa lista à parte.

## Entrega

1. **Uma tabela,** uma linha por item, com estas colunas:
   - referência;
   - DOI;
   - quanto foi lido;
   - o que o item sustenta (uma a três frases);
   - o que ele **não** sustenta, dentre as perguntas acima.
2. **Uma síntese por item,** de meia página no máximo, respondendo às perguntas daquele item.
3. **Correções:** onde a leitura contradiz o que a terceira revisão dizia desse item.
4. **Um BibTeX** com o campo `note` atualizado para o quanto foi lido.
