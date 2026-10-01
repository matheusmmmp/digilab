# *Drosophila* e FlyWire

Separar sempre três camadas: **biologia observada** (anatomia, comportamento, manipulação), **modelo computacional**
(simplificação especificada) e **abstração DigiLab** (mecanismo de software proposto). Todas as fontes abaixo são
**CORPUS**: DOI conferido pelo corpus, fora da tabela verificada do projeto.

## Biologia observada (FONTE)

- O FlyWire reconstruiu o cérebro de uma fêmea adulta, com cerca de 139 mil neurônios e 54,5 milhões de sinapses (Dorkenwald et
  al. 2024, `10.1038/s41586-024-07558-y`), com anotação e tipagem celular (Schlegel et al. 2024, `10.1038/s41586-024-07686-5`).
  É **mapa de conexões**, não controlador funcional pronto.
- O corpo de cogumelo sustenta memória associativa com plasticidade modulada por dopamina. Os tipos de neurônio
  dopaminérgico e as regras de aprendizado são **heterogêneos e específicos de compartimento** (Aso e Rubin 2016,
  `10.7554/eLife.16135`; Otto et al. 2020, `10.1016/j.cub.2020.05.077`; revisão de Cognigni, Felsenberg e Waddell 2019,
  `10.1016/j.conb.2018.09.002`).
- Fome e saciedade modulam a busca por comida e a **expressão** de memória apetitiva aprendida (Tsao et al. 2018,
  `10.7554/eLife.35264`; Li et al. 2009, `10.1016/j.cell.2009.08.035`).

## Modelo computacional (FONTE, modelo)

- Shiu et al. 2024 (`10.1038/s41586-024-07763-9`): modelo de disparo derivado do conectoma, simplificado, para estudar
  processamento sensório-motor e gerar hipóteses testáveis. Não é uma mosca autônoma com aprendizado na vida.
- Jiang e Litwin-Kumar 2021 (`10.1371/journal.pcbi.1009205`): modelo unificado de aprendizado com plasticidade modulada por
  dopamina no corpo de cogumelo. As propriedades de erro de predição são resultado do modelo, não prova do algoritmo da
  mosca.

## O que não mostra

- Que a dopamina do inseto é um erro de predição escalar universal.
- Que um circuito biológico heterogêneo prova que reforço escalar é inadequado num agente de jogo
  (`synthesis/cross_reference.md`; contradição 5 do corpus).
- Que vale emular 140 mil neurônios. Conectoma ≠ dinâmica ≠ comportamento.

## O que serve ao DigiBrain (HIPÓTESE DIGILAB)

Circuitos especializados por classe de estímulo (ameaça, social, objeto), integração, seleção de ação, comando
descendente, corpo e retorno ascendente (`mechanisms/action_selection.md`, `body_feedback.md`); canais de reforço
paralelos com plasticidade local (`mechanisms/reinforcement.md`); memória dependente de estado. É a família do
**DigiBrain C (Fly-like)** em `synthesis/brain_comparison.md`. Nada disso tem correspondência literal com a mosca.
