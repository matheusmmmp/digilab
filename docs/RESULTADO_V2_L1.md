# Resultado — V2, L1: o lobo de decisão aprende com o feedback como vantagem (validação, 2026-10-01)

Plano: `docs/PLANO_ANALISE_V2_L1.md` (rev. 2, registrado antes da calibração válida). Tarefa: `docs/TAREFA_V2_L1_DECISAO.md`.
Validação **única** nas sementes 4101…4505, no ponto escolhido pela calibração (passo 512, teto 1024; a calibração **não fechou**:
`artifacts_v2_l1/calibracao/escolha.json`), liberada pela decisão do Matheus de 2026-10-01 (PR #120: falhar não para a V2).
**Nada foi reajustado olhando a validação.** Números de `artifacts_v2_l1/validacao/` (`escolha.json`, `meta.json`,
`ponto/{resultado,divergence,tarefa,legibilidade,deriva,custo_gargalo,so_cuidado,norma_de_reacao}.json`, `ponto/educacao/resultado.json`,
`base/{instinto,bandit}/`). Os `vidas/*.politica.json` ficam fora do git (regeneráveis por replay dos `.jsonl`; o orquestrador confere o
replay bit a bit antes de medir). Windows, Python 3.13.0; sha256 de `lobos.py` `16a2d7b85a71…`, `config.py` `a900cfe5d9d0…` (`meta.json`).

## 1. Gates (PROPOSTOS, plano seção 4)

| gate | definição | validação (4101…4505) | calibração (3101…3505) | resultado |
|---|---|---|---|---|
| **G3** divergência | JSD atencioso × relapso por semente, média e IC95 | **0,041 bit** [0,026; 0,062] | 0,029 [0,023; 0,038] | **FALHA** (alvo ≥ 0,10; o IC > 0,02 passa) |
| **G4** legibilidade do aprendido | o lobo de decisão decidiu **e** há fator | **0,182** [0,145; 0,236] | 0,188 [0,159; 0,216] | **FALHA** (alvo ≥ 0,50) |
| G4 bruto (sem gate) | com os fatores do impulso | 0,703 | 0,705 | — |
| **G5(a)** | = G3 (sem morte nem lesão no desenho) | falha | falha | **FALHA** |
| **G5(c)** acima do acoplado | JSD(atencioso, relapso) − JSD(acoplado, relapso) | **+0,0099** [−0,010; +0,025] | +0,0196 [+0,0146; +0,0256] | **FALHA** (o IC cruza zero; na calibração passava) |
| G5(b) educação, sem lesão nem morte | pares limpos | 1 semente (4303): **insuficiente** | 2 sementes: insuficiente | — |
| **G6(a)** deriva | JSD(14) ≤ 1,5 × JSD(7) | razão 1,45 (0,0230 / 0,0159) | 1,19 | passa |
| **G6(b)** | nenhum peso no teto | **12 de 20 vidas** com peso no teto | 12 de 20 | **FALHA** |

Pela regra de parada do plano, **G3, G4 e G5 falhando = resultado negativo registrado**. Pela decisão do Matheus (PR #120), a V2 segue;
as validações iniciais serão revistas quando o escopo mudar.

## 2. O que o aprendiz faz (sem gate)

| medida | lobos | instinto | bandit (v1) | controle sem lobos | acoplado só cuidado | artefato |
|---|---|---|---|---|---|---|
| G3-T, acerto na tarefa ensinada, atencioso, 7 últimos dias | **0,663** | 0,577 | 0,607 | 0,349 | 0,446 | `ponto/tarefa.json`, `custo_gargalo.json`, `so_cuidado.json` |
| G3-T relapso / aleatório / incoerente | 0,524 / 0,644 / 0,520 | 0,513 / 0,663 / 0,586 | 0,496 / 0,637 / 0,566 | — | — | idem |
| eficiência amostral (sinais até a metade do caminho), atencioso | 44 de 125 (5/5 chegam) | 39 de 134 | 24 de 139 | — | — | idem |
| teto do dono (política ótima nos mesmos estados) | 1,0 | | | | | idem |
| JSD atencioso × relapso | 0,041 | 0,0 | 0,012 | 0,113 [0,094; 0,132] | — | `ponto/divergence.json` |
| JSD coerentes × aleatório | 0,052 / 0,052 | 0,0 | 0,021 / 0,018 | — | — | idem |
| conta da v1: entre braços / dentro do braço | 0,040 / 0,026 | 0,0 / 0,0 | 0,018 / 0,013 | — | — | idem |
| G4 do aprendido / bruto | 0,182 / 0,703 | 0,0 / 0,525 | 0,159 / 0,159 | 0,283 / 0,283 | — | `ponto/legibilidade.json`, `custo_gargalo.json` |
| o lobo de decisão decidiu | 20,3% | — | — | — | — | `ponto/legibilidade.json` |
| JSD ao instinto, dias 1 / 7 / 14 | 0,0054 / 0,0159 / 0,0230 | 0 | — | — | — | `ponto/deriva.json` |

- **O aprendiz aprende a tarefa ensinada** (D1): +0,086 de acerto sobre o instinto no atencioso (calibração: +0,145), com o relapso
  quase parado (+0,011) e o incoerente abaixo do instinto (−0,066: feedback de polaridade sorteada desaprende). O bandit da v1 sobe
  +0,030. É ensino, não cuidado: o acoplado (as mesmas ações de cuidado, sem sinal) **cai** para 0,446, abaixo do instinto, porque o
  único canal que lhe resta (o chamado pago pela latência) ensina a chamar mais.
- **Mas o que se aprende quase não muda a distribuição de ações nas sondas** (G3 0,041 bit, ~3× o bandit, 40% do alvo) **e decide pouco**:
  o impulso (as regras do instinto) decide 80% das decisões; só 18% têm fator aprendido.
- **Controle de capacidade equivalente sem lobos (D2):** diverge mais (0,113 bit, passaria o G3) e é mais "legível" pelo aprendido
  (0,283 contra 0,182; lobos − controle **−0,101** [−0,136; −0,049]): **a modularidade não compra legibilidade** por esta medida. O custo
  do gargalo é a favor dos lobos: **+0,314** [+0,177; +0,422] de acerto, porque o controle, sem regra de sono, cuida mal de si e o dono
  tem pouco a elogiar. Sem os lobos a legibilidade é maior porque toda decisão é aprendida; com eles a maior parte é instinto, e a
  regra de honestidade a conta como fator bruto, não aprendido.
- **"Só cuidado" acoplado (D4):** 85–144 interações contra 224 (os sinais são ~60% do atencioso; uma semente, 4505, ficou com 144);
  JSD acoplado × ensino 0,022, acoplado × relapso 0,031. A variante sem acariciar sai igual (o atencioso quase não acaricia).
  **G5(c)**: na validação a diferença ensino − acoplado (+0,0099) fica com IC [−0,010; +0,025]; na calibração era +0,0196 [+0,0146;
  +0,0256]. Com 5 sementes o sinal é frágil.
- **Norma de reação (3.2):** Δα ensino − só cuidado **+0,238** [+0,211; +0,258] no acerto e +0,024 [+0,021; +0,026] na JSD ao
  instinto (o nível sobe com o ensino, consistente nas duas rodadas). **A inclinação é mal condicionada**: os 4 ambientes (sementes de
  rng) mudam a média do acerto em 0,02 (índice de ambiente de −0,012 a +0,007), e os IC de Δβ cobrem dezenas; não se lê sensibilidade
  ao ambiente neste desenho. `ponto/norma_de_reacao.json`.
- **Educação com lesões (3.1):** 1 morte (aleatório) e 8 pets com lesão em 20; JSD atencioso × relapso com todos 0,087; só 1 semente
  sem lesão nem morte nos dois pets: G5(b) insuficiente. `ponto/educacao/resultado.json`.
- **G6:** a deriva ao instinto cresce ainda no segundo semana (razão 1,45, abaixo do 1,5 por pouco) e 12 vidas têm pesos no teto
  (1·S): o freio duro é quem limita, não a dinâmica. Na grade da calibração nenhum passo evitava isso (passo 32: razão 2,33, sem teto).

## 3. Leitura

1. **Resultado negativo registrado para H1 com este aprendiz e este ambiente.** Donos coerentes produzem políticas distinguíveis entre
   si e do aleatório **um pouco mais** que o bandit (0,041 contra 0,012 bit), mas longe da convenção de 0,10 bit, e menos de um quinto
   das decisões é explicável pelo aprendido. O ensino chega (G3-T e Δα), mas a arquitetura deixa o instinto decidir 80% das vezes:
   regras com um candidato (sono, pedido, abandono) nunca aprendem, e nas duas regras com sorteio o teto de 1·S limita o quanto o
   aprendido pode pesar.
2. O que a L1 mostra de positivo e reprodutível nas duas rodadas: acerto na tarefa sobe só no dono coerente, cai no incoerente e no
   acoplado; o nível (Δα) separa ensino de cuidado com IC fora de zero; o controle sem lobos aprende mais e cuida pior.
3. O que fica para a revisão das validações (decisão do Matheus): os alvos 0,10 bit e 50% foram escritos antes de se ver o aprendiz;
   o teto 1·S e o passo S/2 vieram de uma calibração que não fechou; as regras determinísticas fora do aprendizado são escolha do L0.
   Nada disso se ajusta neste PR.

## 4. Reprodução

```bash
python experiments/run_v2_l1.py --config experiments/configs/v2_l1/validacao.json   # recusa rodar se a pasta ja existir
```
