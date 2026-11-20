# Corpo e retorno do corpo

## Nas fontes

- **CORPUS:** a biologia sustenta acoplamento sensório-motor recíproco: fisiologia interna e informação ascendente moldam o
  comportamento; a ação muda o corpo e as oportunidades seguintes. FlyWire é anatômico; Shiu et al. é modelo simplificado; os
  estudos de fome dão evidência causal em circuitos específicos (Tsao et al. 2018). Nenhuma fonte descobriu um "módulo de
  retorno do corpo" abstrato.
- **VERIFICADA:** DERL integra aprendizado e evolução em agentes corporificados (Gupta et al. 2021).

## No DigiLab hoje (REPOSITÓRIO)

Não há corpo. O "retorno" é a mudança dos drives pela ação (`policy.efeito_da_acao_do_pet`) e pelo tempo (`state.py`). Corpo
2D manipulável (comida, bola, obstáculo, áreas) é IDEIA em `docs/TODO_INTERACAO_CORPO.md`; combate em tempo real está em
stand-by (`CLAUDE.md`, pendências).

## Hipótese

| ID | pergunta | teste mínimo |
|---|---|---|
| H-BODY-01 | simular o corpo em baixo nível é desnecessário se as consequências relevantes para a decisão (energia, cansaço, lesão, sucesso da ação, posição) forem representadas com fidelidade | comparar só depois do inventário; calibração ação → resultado, predição de estado, desempenho, custo |

Recomendação: o corpo entra pelo menor passo que gera consequência (a bola, depois as frutas), não como simulação física.
