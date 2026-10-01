# Creatures e Creatures 3

## O que as fontes mostram

- **FONTE, VERIFICADA:** Grand, Cliff e Malhotra (1997, `10.1145/267658.267663`) descrevem o *Creatures* como sistema de vida
  artificial para entretenimento que combina arquitetura neural codificada no genoma, bioquímica artificial, controle
  sensório-motor e **aprendizado hebbiano durante a vida**. Grand e Cliff (1998, `10.1023/A:1010042522104`) descrevem
  bioquímica, quimioemissores e receptores modulando a rede. Cliff e Grand (1999, `10.1162/106454699568683`) descrevem o
  produto e o ecossistema de usuários. São do *Creatures* original: não atribuir cada detalhe ao Creatures 3.
- **FONTE, CORPUS (documentação de produto):** o *Creatures 3 Genetics Kit Manual* (Creature Labs, distribuído oficialmente)
  explica genes que especificam bioquímica, cérebro, morfologia e desenvolvimento, mutação e recombinação, e tratos e
  regras neurais configuráveis. É documentação técnica do produto, não demonstração revisada por pares.
- **NÃO VERIFICADA EM FONTE PRIMÁRIA:** a engenharia reversa da comunidade (Creatures Wiki) sobre lobos, químicos e
  versões. Pista de desenho, nunca evidência.

## O que as fontes não mostram

- **Vício:** nenhuma fonte primária descreve o mecanismo de vício do Creatures (busca V5, `V3_SINTESE_FRUTAS_VICIO_V1_V6.md`).
  O livro do Grand, *Creation: Life and How to Make It* (2001), tem existência confirmada (VERIFICADA sem DOI, resenha
  `10.5860/choice.39-4009`) e **conteúdo não lido**. Não escrever "como no Creatures" em nenhum desenho.
- **Herança do aprendido:** as fontes não mostram que pesos ou comportamentos aprendidos de uma norn passam aos filhos. Genoma
  (substrato) e plasticidade na vida são mecanismos distintos; não colapsar em herança lamarckiana.
- **Biologia:** os químicos do jogo são mecânica de jogo, não equivalentes de hormônios ou neurotransmissores.

## O que serve ao DigiBrain (INTERPRETAÇÃO)

A decomposição genoma → predisposição estrutural; química interna → drive; percepção → entradas; seleção → comportamento;
consequência → aprendizado local; reprodução → recombinação. Cada seta é uma relação causal a auditar, não a prescrição de
um módulo. É a família de origem do **DigiBrain A (C3-like)** em `synthesis/brain_comparison.md`.

## Ligação com o repositório

- REPOSITÓRIO: o genoma da v1 (espécie + temperamento de 4 eixos, `digilab/temperamento.py`, `heranca.py`) já separa
  substrato herdado de aprendido; no E1 explicou 4,9% da variância (`artifacts_linhagem/natureza_criacao/`).
- Precedente da revisão: Creatures é o único sistema em que criação e seleção pelo usuário aconteceram juntas e em
  escala, mas o registro é descritivo, não fatorial (`literatura-digilab`).
