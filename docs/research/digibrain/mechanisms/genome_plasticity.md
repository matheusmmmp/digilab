# Genoma × plasticidade

**Pergunta:** a seleção pode agir sobre **como** o indivíduo aprende, separado do comportamento inicial herdado e do conteúdo
aprendido? É a pergunta maior do estudo vista pelo lado do genoma (`README.md`).

## Nas fontes

- **VERIFICADA:** efeito Baldwin computacional: Hinton e Nowlan 1987 (sem DOI); Fernando et al. 2018 (`10.1145/3205651.3205763`,
  a evolução produz um prior/inicialização para aprender). Partição instinto × aprendido no mesmo agente: Hallawa et al.
  (`10.1145/3449726.3459475`). **Herdar o prior e separar instinto de aprendido não são novidade do Digilab.**
- **VERIFICADA:** Creatures codifica no genoma o substrato neural e de desenvolvimento e tem aprendizado na vida (Grand et al. 1997).
- **CORPUS:** em Avida, ambientes evolutivos selecionam capacidade de aprendizado associativo (Pontes et al. 2020,
  `10.1086/706252`); plasticidade fenotípica de organismo digital (Fortuna 2022, `10.1098/rsos.220852`).
- **VERIFICADA:** aprendizado e evolução em agentes corporificados (Gupta et al. 2021, `10.1038/s41467-021-25874-z`).
- **VERIFICADA:** normas de reação (intercepto = nível, inclinação = plasticidade; Dingemanse et al. 2010,
  `10.1016/j.tree.2009.07.013`); canalização e assimilação genética (Pigliucci, Murren e Schlichting 2006, `10.1242/jeb.02070`).
- A.L.I.V.E. e ALGA **não** mostram controladores herdado + adquirido nem herança da capacidade de aprender
  (`sources/brazilian_alife.md`).

## No DigiLab hoje (REPOSITÓRIO)

- Genoma = espécie + 4 eixos de temperamento (curiosidade, teimosia, sensibilidade, rancor), sorteados por `rng_ovo`
  (`digilab/temperamento.py`). O temperamento **já muda como o pet aprende, nunca o quê** (escala exploração, peso de elogio e
  de bronca, decaimento da memória). É um genoma de plasticidade mínimo.
- No E1 o genoma explicou 4,9% da variância, IC95 [−0,0007; +0,0032]: gate FALHOU; a linhagem parou como pesquisa
  (`artifacts_linhagem/natureza_criacao/especie_fixa/resultado.json`).
- Decisão de 2026-09-29: um genoma ajustado só para passar o gate viciaria o teste. Genoma novo só com plano próprio.
- O prior dos lobos (L0) é o mesmo para todos: não vem do genoma.

## Hipóteses

| ID | pergunta | teste mínimo |
|---|---|---|
| H-PLAST-001 | parâmetros de aprendizado herdáveis afetam a adaptação sem copiar memórias ou pesos dos pais | linhagens pareadas com o mesmo desempenho inicial e um parâmetro de aprendizado variando; curva de aprendizado, transferência, retenção e aptidão da linhagem |
| H-GEN-01 | o genoma modula a sensibilidade por canal de reforço (`reinforcement.md`, H-R4) | aprendizado desligado = vidas idênticas entre genomas; experiência acoplada = divergência por genoma |
| H-GEN-02 | o genoma define a fisiologia (taxas dos drives) e o cérebro inicial (prior) | fase 3; depois de H-GEN-01 |

Confundidores: variância inicial do genoma, exposição desigual, efeito de geração, estado herdado por acidente. Tudo aqui é
fase 3 (`docs/ROADMAP_V2.md`), exceto H-GEN-01, que pode rodar na fase 1 sem evolução (genomas fixados por desenho).
