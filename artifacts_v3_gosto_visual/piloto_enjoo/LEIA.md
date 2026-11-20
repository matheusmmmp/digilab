# O piloto da GV3b do adendo 1: registro da falha, não resultado

Esta pasta é o piloto do `docs/PLANO_ANALISE_V3_GOSTO_VISUAL_ADENDO1.md` (90101…90202, 24 vidas). Ele passou na conferência da GVP-7, e a
run que veio depois parou por um erro do código (D-GV-GV3B-12, em `docs/registro/2026-11.md`). A pasta não foi commitada antes da run, e
por isso o `meta.json` da run gravou `git_limpo: false`.

- `meta.json`, `medidas.json`, `analise.json` e `custo.json`: como o piloto os gravou;
- `vidas.tar.gz`: as 24 vidas e as 24 sondas.

**Nada disto é resultado, e nada disto é lido como resultado.** O piloto só serviu à conferência da GVP-7 do adendo 1; as medidas dele
não são lidas nem comparadas com nada (`docs/PLANO_ANALISE_V3_GOSTO_VISUAL_ADENDO2.md`, seção 3). A faixa 90101…90505 está em
`FAIXAS_QUEIMADAS` e não volta.
