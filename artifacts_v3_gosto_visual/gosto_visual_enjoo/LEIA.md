# A run parcial da GV3b do adendo 1: registro da falha, não resultado

Esta pasta é a run do `docs/PLANO_ANALISE_V3_GOSTO_VISUAL_ADENDO1.md` (90303…90505), que parou na vida 213 de 216 com o erro alto da
D-GV-P1e-3 (as duas TVs da sonda sem lugar, o pet em (25, 478)). O fato está na D-GV-GV3B-12, em `docs/registro/2026-11.md`.

- `meta.json`: como a run o gravou no começo, sem `fim` e com `git_limpo: false`;
- `vidas.tar.gz`: as 213 vidas e as 212 sondas que ficaram em disco. Não há `medidas.json`, `analise.json` nem `custo.json`.

**Nada disto é resultado, e nada disto é lido como resultado.** As vidas não são abertas para medir nada, nem para escrever o adendo 2,
nem para comparar com a run dele (`docs/PLANO_ANALISE_V3_GOSTO_VISUAL_ADENDO2.md`, seção 3). A faixa 90101…90505 está em
`FAIXAS_QUEIMADAS` e não volta.
