# RESULTADO V3 — SOCIAL_PAR, A0 e B0

- **Plano:** `docs/PLANO_ANALISE_V3_SOCIAL_PAR_A0.md` (APROVADO pelo Matheus em 2026-11-17; o N e o K DECIDIDOS em 2026-11-18, D-SP-34).
- **A run:** `python experiments/run_v3_social_par_a0.py --config experiments/configs/v3_social_par_a0/run.json --processos 4`, uma vez.
  - Rodou em 2026-11-18, das 15:47:05 às 15:54:03, com 418 s de parede para as vidas.
  - O commit é o 4a2bf0ea da `main`, com o git limpo. O `pre_run` aceitou a run às 15:46, depois do fim da run do PV-2.
  - São 210 pares (as bases 101101…101505, K = 42) e 1.050 vidas, 5 por par.
- **Artefatos:** `artifacts_v3_social_par_a0/run/`, com o `meta.json`, o `medidas.json`, o `resultado.json` e as gravações de cada par em `vidas/`.
- **Os gates de cada par:** o G-INSTR (a VIVO e a GRAV iguais até o t0) e o G1 (as três condições refeitas com o mesmo sha256) passaram
  nos 210. A run para no primeiro par que falha.

## As premissas (seção 5)

| premissa | valor | mínimo | passa |
|---|---|---|---|
| PA-1, a janela cabe | 210 de 210 (1,00) | 0,95 | sim |
| PA-2, F longe no t0 | 201 de 210 (0,957) | 0,80 e n ≥ 100 | sim |
| PA-3, há reencontro na janela | 201 de 201 (1,00) | 0,20 | sim |
| PB-1, chutes dos dois | 0 pares elegíveis | n ≥ 100 | **não** |

O A0 é conclusivo. **O B0 é inconclusivo por premissa:** em nenhum par F e P chutam a bola ao menos 2 vezes cada um na janela.

## O A0: o primário

**D_A = T\*_VIVO − T\*_GRAV**, em decisões; negativo quer dizer que F volta mais depressa quando P responde.

| n | média | dp | IC95 | p bilateral | δ_A | classe |
|---|---|---|---|---|---|---|
| 201 | −0,119 | 1,298 | [−0,300; +0,061] | 0,194 | 4 | **≈ 0** |

**A leitura escrita antes (seção 7):** é o previsto. No pet de hoje, o parceiro que responde não muda o reencontro em mais de uma hora de
jogo, e o IC inteiro fica dentro de ±0,3 decisão. Isso não quer dizer que o pet ignora o outro: quer dizer que não há diferença acima
da δ. O instrumento só mostrou que detecta parceiros de regra pura (a E1).

## Os secundários (Holm, α = 0,05)

| | n | média | IC95 | p | p ajustado | rejeita |
|---|---|---|---|---|---|---|
| S1, T\*_GRAV − T\*_OUTRA | 201 | −0,159 | [−2,065; +1,746] | 0,869 | 1,000 | não |
| S2, a fração do tempo perto (VIVO − GRAV) | 201 | +0,0035 | [−0,0115; +0,0185] | 0,648 | 1,000 | não |
| S3, a contingência de F para P (VIVO − GRAV) | 201 | +0,0147 | [−0,0043; +0,0337] | 0,130 | 0,389 | não |

Nenhum secundário rejeita.

## O descritivo (seção 8, sem teste)

- **O reencontro é rápido nas três condições:** o tempo médio até o raio perto é de ~10 decisões na VIVO (10,10), na GRAV (10,22) e
  na OUTRA (10,38), contra a janela de 96. Até o contato, são 25,6, 26,1 e 29,6 decisões.
- **P no t0:** dormindo em 101 dos 201 pares, livre em 88 e comendo em 12. A média do D_A fica entre −0,42 e −0,09 nos três grupos.
- **A comida no t0:** 176 pares com comida no mapa e 25 sem. A média do D_A é −0,14 com comida e 0,00 sem.
- **Os desvios de P da gravação na janela:** 413 decisões com o alvo fora na GRAV e 1.145 na OUTRA, somadas nos 201 pares.
- **A CO7 de F na janela:** 96 decisões com dever em todas as condições; o escudo removeu em 0,5 % delas.
- **Os chutes:** 0 por dia de P com F passivo, e o excesso de alternância não existe na VIVO nem na GRAV. É a mesma falta que faz o
  B0 inconclusivo.

## O que fica

- **No pet de hoje,** o modular com a CO7, como o jogo v39, a resposta do parceiro não muda o reencontro dentro da margem.
- **O B0 não diz nada:** a bola quase não é chutada nas vidas de hoje.
- Os desvios do caminho estão em `docs/registro/2026-11.md`, de D-SP-31 a D-SP-36.
