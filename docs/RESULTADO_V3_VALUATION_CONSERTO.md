# RESULTADO V3 — VALUATION, a V3: o conserto do reflexo do sono (2026-11-17, Claude Code, Opus 5.5)

**O plano:** [PLANO_ANALISE_V3_VALUATION_CONSERTO.md](PLANO_ANALISE_V3_VALUATION_CONSERTO.md), APROVADO pelo Matheus em 2026-11-17
("Aprovo, siga"), commitado antes do código e da primeira vida. A V2: [RESULTADO_V3_VALUATION.md](RESULTADO_V3_VALUATION.md).

**A leitura, pela regra da seção 5: falha.** O conserto fecha mais episódios de fome (a P passa) e não piora a privação nem a taxa do
comedouro e do longe (G1 e G3 passam). Mas a exaustão sobe em "> 0", no `longe_fixo` e nas 12 células, e a G2 reprova. **A fase para
com este relato** (a regra do pedido). O conserto não vai à V4.

## 1. A run

| comando (o do `meta.json`) | commit, árvore | vidas | sementes | duração |
|---|---|---|---|---|
| `python experiments/run_v3_valuation_conserto.py --config experiments/configs/v3_valuation/conserto.json --processos 4` | `c560894b`, limpa | 4 800 (REL e CON × 12 células × 200 unidades) | 73101…73505, K = 40, derivação `digibrain_prototipo` | 1 h (12:00–13:00 de 2026-11-17) |

- **O ambiente:** Python 3.13.0 e Node v24.19.0, este só gravado.
- **A saída:** código 0, sem falha alta (o replay, o T-CENARIO-1, as conferências da C4 e a do conserto, decisão a decisão). A run rodou **uma vez**.
- **O D, "desliga não muda":** o gabarito `tests/gabaritos/valuation_conserto_de_hoje.json`, gravado antes do código, passa byte a byte.

**Os artefatos** em `artifacts_v3_valuation/conserto/`, com o sha256 no disco igual ao do `meta.json`:

| arquivo | sha256 | tamanho e observação |
|---|---|---|
| `resultado.json` | `c4e57b52…` | |
| `medidas.json` | `3e6724e9…` | 48,4 MB |
| `vidas.tar.gz` | `124b145b…` | 22,4 MB, determinístico |
| `meta.json` | | |

## 2. Os critérios (seção 5)

O contraste é CON − REL, pareado por unidade (n = 200), com o IC95 pelo t e as classes da A6.6 com δ = 0,032.

| critério | medida | CON − REL | IC95 | classe | **passa** |
|---|---|---|---|---|---|
| **P** | a taxa por episódio, `longe_fixo` (REL 0,564; CON 0,671) | **+0,106** | [+0,094; +0,118] | > 0, p = 5 × 10⁻⁴¹ | **sim** |
| G1 | a privação, `longe_fixo` | +0,021 | [+0,012; +0,030] | ≈ 0 | sim |
| G1 | a privação, 12 células | +0,009 | [+0,003; +0,015] | ≈ 0 | sim |
| **G2** | a exaustão, `longe_fixo` (REL 0,228; CON 0,423) | **+0,195** | [+0,181; +0,208] | **> 0** | **não** |
| **G2** | a exaustão, 12 células (REL 0,234; CON 0,408) | **+0,174** | [+0,168; +0,181] | **> 0** | **não** |
| G3 | a taxa por episódio, comedouro | +0,076 | [+0,068; +0,084] | > 0 | sim |
| G3 | a taxa por episódio, longe | +0,080 | [+0,069; +0,092] | > 0 | sim |
| D | o gabarito, chave desligada | byte a byte | | | sim |

- **A P em detalhe:** a margem efetiva é 0,018. O IC95 do bootstrap, rotulado, é [+0,095; +0,116], e o g1 é 0,52.
- **A fração do gap da A1 que o conserto cobre** é 1,28, só descritiva.
- **As duas privações saem "≈ 0", mas com o sinal +:** o IC exclui o 0 e cabe em δ. Pela D-VAL-20, isso não reprova.
- **O veredito do `resultado.json`:** `falha`, com as falhas `G2 (longe_fixo)` e `G2 (12_celulas)`.

## 3. Os descritivos (sem classe)

| medida, `longe_fixo` | REL | CON | CON − REL [IC95] |
|---|---|---|---|
| **decisões com a energia abaixo de `lambda_sono`, por vida** | 265 | **505** | +239 [+225; +254] |
| **fração delas com a fome urgente** | **0,635** | 0,618 | −0,017 |
| reflexos por vida | 265 | 97 | −168 |
| intenções de comer trocadas num reflexo, por vida | 13,2 | 1,9 | −11,3 |
| fração de `dormir` no episódio | 0,419 | 0,330 | −0,089 |
| fração de `comer` no episódio | 0,164 | 0,207 | +0,044 |
| `janela_vencida` | 0,432 | 0,326 | −0,106 |
| refeições de ração por dia | 3,02 | 3,10 | +0,08 |
| episódios de fome por vida | 13,2 | 15,0 | +1,8 |
| latência média do fechamento (ticks) | 50,6 | 47,0 | −3,6 |

Nas 12 células, o padrão é o mesmo: a energia baixa passa de 266 para 477 decisões por vida, com a fome urgente em 0,62 delas no REL.
Os outros números estão no `resultado.json`.

## 4. O que isso diz

- **A guarda abriu demais, um dos dois riscos que a D-VAL-16 nomeou.** No REL, 63 % das decisões com a energia abaixo de S/4 têm a fome urgente: energia baixa e fome urgente andam juntas. O conserto tirou 64 % dos reflexos (de 265 para 97 por vida), perto da R da V2, que tirava todos.
- **O mecanismo da exaustão:** sem o reflexo durante a fome, o pet sai para comer com a energia abaixo de S/4. Ele come, mas fica quase o dobro do tempo com a energia baixa (505 decisões contra 265). A exaustão vai de 0,23 a 0,42, abaixo dos 0,50 da R, mas muito acima de δ.
- **O que melhora é real e se espalha:**
  - a taxa sobe nos três lugares (+0,106 no `longe_fixo`, +0,076 no comedouro e +0,080 no longe);
  - a `janela_vencida` cai de 43 % para 33 %;
  - a privação quase não muda.

  O custo é a energia.
- **Uma comparação entre runs, só descritiva:** na A1 (97xxx), a TRIV fechava 0,645 no `longe_fixo`, com exaustão 1,000. O CON fecha 0,671 com exaustão 0,423. Não é um contraste do plano, e a V4 não roda.
- **O que a run não demonstra** (o `nao_demonstra` do `resultado.json`):
  - nada contra a TRIV;
  - nada sobre o jogo web;
  - nada sobre outro limiar além do `urgencia_lambda` de hoje;
  - nada com o sono que segura ligado;
  - nada fora dos 14 dias e do mundo do MVP.

## 5. O CHECKPOINT V3

**O conserto não passa, e a fase para.** O resultado fica registrado como está, e a chave continua no código, desligada. Ligada, ela não
entra em nenhum pet. O que vier depois é decisão do Matheus. As opções estão no PR, cada uma com o custo de errar.
