# NORNBRAIN

## O que é (FONTE, software)

Projeto público no GitHub (`thechimpmatrix/nornbrain`, motor `thechimpmatrix/openc2e-nb`), **não revisado por pares** e em
mudança rápida. O README descreve a troca do lobo de combinação do Creatures 3 por um módulo CfC (*closed-form continuous-
depth*) organizado como NCP (*neural circuit policy*), mantendo boa parte da percepção, da atenção, das ações e da química de
recompensa originais. O próprio README diz que o cérebro está em andamento e ainda não reproduz o comportamento normal.
Fixar o commit antes de citar qualquer estado técnico.

Peças distintas que o corpus original juntava (não são intercambiáveis):
- CfC: modelo recorrente de tempo contínuo com atualização em forma fechada (Hasani et al. 2022, `10.1038/s42256-022-00556-7`, CORPUS);
- NCP: conectividade esparsa e estruturada (Lechner et al. 2020, `10.1038/s42256-020-00237-3`, CORPUS);
- A2C: aprendiz ator-crítico;
- traços de elegibilidade: atribuição de crédito no tempo;
- química: fonte de recompensa e punição **escalar** no desenho descrito.

## O que não mostra

Eficácia (nenhum resultado de comportamento validado), escala para muitos pets persistentes, nem superioridade do CfC sobre
uma rede simples (o artigo do CfC compara com modelos baseados em EDO, não com MLP). A troca proposta muda representação,
conectividade, aprendiz e lobo alvo ao mesmo tempo: sem ablação, não diz qual peça fez efeito.

## O que serve ao DigiBrain

Estudo de caso de engenharia (trocar o substrato de aprendizado preservando o resto) e **hipótese concorrente**: é a família
do **DigiBrain B (CfC/A2C)** em `synthesis/brain_comparison.md`.

**No projeto:** a comparação roda no Python (decisão do Matheus, 2026-10-01: a web roda um DigiBrain só, o do produto).
O B entra como braço de pesquisa, em ponto flutuante, com replay bit a bit no mesmo runtime. Só se ele fosse o escolhido
para o produto o porte para a web viraria problema (o `exp`/`tanh` do V8 e o do CPython diferem no último bit). Um
resultado do nosso B fala do nosso B, não do NORNBRAIN.


## Revisão de 2026-10-07 (pedido do Matheus)

Conferido no repositório (`gh api` e README, 2026-10-07):
- **Estado:** 5 estrelas, 15 commits, último push em 2026-04-28. O autor se descreve como terapeuta ocupacional, "not a coder" por ofício.
- **Licença:** código em PolyForm Noncommercial 1.0.0; documentação em CC BY-NC 4.0. **O código não pode entrar no produto** sem licença
  própria; ideias e desenho podem ser estudados.
- **O que faz:** troca só o lobo de combinação ("comb") do Creatures 3 por um CfC ligado como NCP, num openc2e de 64 bits modificado
  (`thechimpmatrix/openc2e-nb`). Entrada de 107 dimensões, estado oculto de 440 neurônios, saída de 51. Aprende por ator-crítico (A2C) com
  traço de elegibilidade de 20 ticks e γ = 0,95. A recompensa é o químico de recompensa (204) e o de punição (205) do próprio jogo, lidos a
  cada tick.
- **Estado declarado:** "o cérebro ainda não funciona a ponto de reproduzir o comportamento normal do cérebro SVRule". A fase ativa é um
  desenho travado em 2026-04-26, com implementação pendente. Nenhum resultado, benchmark ou artigo.

**As técnicas que ele usa são atuais e estão publicadas** (metadados conferidos em 2026-10-07):
- CfC: Hasani et al. 2022, *Nature Machine Intelligence*, `10.1038/s42256-022-00556-7` (Crossref).
- NCP: Lechner et al. 2020, *Nature Machine Intelligence*, `10.1038/s42256-020-00237-3` (Crossref).
- A2C: Mnih et al. 2016, arXiv:1602.01783 (API do arXiv).

**Leitura.** "Mais atual" fala da idade da técnica (2016–2022, contra as SVRules de 1999), não de evidência de que funciona melhor. O próprio
NORNBRAIN não mostra isso, e o Digilab já testou a mesma família: o **DigiBrain B** (CfC, ator-crítico e elegibilidade) **não aprendeu** na
calibração (`docs/RESULTADO_V2_CALIBRACAO_CEREBRO_B.md`: a parte aprendida mudou 0,77% das decisões). O valor do NORNBRAIN para o Digilab é
outro: a análise dos arquivos do Creatures 3 que o autor fez (`docs/reference/game-files-analysis.md` no repositório dele), útil para
entender o reforço químico do jogo (`creatures3.md`, revisão de 2026-10-07). Essa análise é secundária: pista, não fonte primária.
