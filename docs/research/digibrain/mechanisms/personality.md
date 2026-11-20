# Personalidade e fenótipo comportamental

## A ideia (HIPÓTESE DIGILAB, Matheus 2026-10-01)

Personalidade como **sensibilidade herdada × história**, não como número configurado. Em vez de `agressivo = 0.8`, o genoma
diz quanto cada canal de reforço pesa (`reinforcement.md`), e o comportamento estável sai do que a vida ensinou.

## Nas fontes

- **VERIFICADA:** Dwarf Fortress torna personalidade e história legíveis (Adams 2021): precedente de desenho.
- **VERIFICADA:** ~52% da variação de personalidade animal é genética aditiva (Dochtermann, Schwab e Sih 2015,
  `10.1098/rspb.2014.2201`); a raça explica só 9% da variação comportamental individual em cães (Morrill et al. 2022,
  `10.1126/science.abk0639`); traços vêm em síndromes correlacionadas (Sih, Bell e Johnson 2004, `10.1016/j.tree.2004.04.009`);
  normas de reação (Dingemanse et al. 2010).
- **INTERPRETAÇÃO:** parâmetros configurados não são personalidade emergente. Um fenótipo plausível reflete genoma × estado ×
  experiência × aprendizado × memória × história.

## No DigiLab hoje (REPOSITÓRIO)

- Temperamento: 4 eixos **independentes**, uniformes em [−amplitude, amplitude] (`temperamento.sortear`). Contraria as
  síndromes correlacionadas de Sih et al.
- Caráter aprendido: pelo desvio da política nas sondas (`evolucao.py`), decide a forma adulta.
- Achados: no E1 o ambiente decidiu a forma mais que o dono ou o genoma (κ de Fleiss perto de 0); a forma explica 96% da taxa
  no painel (`artifacts_linhagem/dono_ambiente/resultado.json`).

## Hipóteses

| ID | pergunta | teste mínimo |
|---|---|---|
| H-PERS-001 | diferenças individuais persistentes emergem de genoma × história com oportunidades e estados controlados | sondas repetidas em contextos pareados; estabilidade dentro do pet, variância entre pets, predição pelo genoma × pela história, mudança depois de intervir na experiência |
| H-PERS-02 | sensibilidade por canal (H-GEN-01) gera personalidade mais estável que eixos configurados | mesma vida, genomas diferentes; consistência entre situações |

Não inferir personalidade de uma luta só nem dos parâmetros.
