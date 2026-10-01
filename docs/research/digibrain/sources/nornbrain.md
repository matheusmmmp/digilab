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

**Restrição do projeto:** CfC usa funções transcendentais e pesos em ponto flutuante; a V2 pede pesos inteiros para a
paridade Python/web (D8). O B só cabe como braço de pesquisa em Python (determinístico no mesmo runtime), sem porte para a
web. Um resultado do nosso B fala do nosso B, não do NORNBRAIN.
