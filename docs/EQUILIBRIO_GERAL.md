# Equilíbrio geral do combate — relatório por fase

Plano e metas: `docs/PLANO_EQUILIBRIO_GERAL.md` (registrado antes da rodada). Fases 1–3 só nas sementes de calibração
(3101…3505); a fase 4 é a validação única (4101…4505). Branch `equilibrio-geral`; o PR é no fim da fase 4.

## Fase 1 — as formas (M-A1…M-A5)

Status: **calibração fechada** (2026-09-30). As quatro metas das formas passam na calibração com as 8 formas, **o furioso
incluído**; M-A5 no quadro da seção 1.4. A validação é a da fase 4.

- **Script:** `python experiments/calibrar_equilibrio_geral.py --etapa todas` (~15 min com 8 processos).
- **Artefatos:** `artifacts_equilibrio_geral/fase1/` (`matriz.json`, `painel.json`, `metas.json`, `e3.json`, `s1.json`,
  `mecanismo.json`) e as baterias `bateria_v21e/`, `bateria_v21d/` e `bateria_v2c/`. Todo número abaixo vem deles.
- **Regras:** as da validação V21C (`experiments/configs/v21c/validacao.json`) mais as chaves de cada variante. A variante
  escolhida está registrada em `experiments/configs/v21e/calibracao.json`.
- **Conferências que falham alto:** a V21D (`a_c_e2v_v`) sai igual, byte a byte, à rodada 2
  (`artifacts_combate_v21c/equilibrio_rodada2/`: matriz com ε 0,05 e 0,15, painel, E3 e S1).
- **Método** (o das rodadas 1 e 2): 100 partidas por par por semente e espécie, os dois lados da mesma espécie, lados trocados
  na metade; força = média contra as outras 7 (média das 4 espécies), ε dos bots 0,05. Painel B: o bot canônico da forma como
  pet contra os 32 bots, 50 partidas por bot por semente. O limite de turnos é o do Python (fração de vida). Diferenças abaixo
  de ~0,01 não devem ser lidas (o erro padrão entre sementes não foi estimado).

### 1.1 O que mudou

**A base não mudou.** O diagnóstico apontava o golpe rápido barato e a C3 como a causa do furioso, e o plano dava a base como a
alavanca. Medidas sobre a V21D (`matriz.json`, `metas.json`), nenhuma tira o furioso de ~0,72:

| base (sobre a V21D) | furioso | painel do furioso | amplitude |
|---|---|---|---|
| V21D (golpe 10, parry 5, C3) | 0,725 | 0,672 | 0,319 |
| golpe rápido 12 / 15 / 20 | 0,721 / 0,749 / 0,718 | 0,685 / 0,706 / 0,682 | 0,315 / 0,350 / 0,339 |
| parry 8 / 12 | 0,723 / 0,719 | 0,667 / 0,660 | 0,324 / 0,351 |
| sem a C3 | 0,724 | 0,672 | 0,321 |

O parry maior só pega quem defende, e quase nenhuma forma que o furioso esmagava defendia do golpe: 0,05, 0,06 e 0,04 golpes
defendidos por partida pelo duelista, pelo titã e pela sentinela (`mecanismo.json`, V21D). O golpe mais caro pesa também para
quem o usa contra o furioso (o duelista cai de 0,477 para 0,391 com o golpe a 20).
Sem a C3 o furioso ainda faz 0,999 e 1,000 contra a sentinela e o emboscador: a investida acerta na média de qualquer jeito.

**O que fecha são as listas** (chaves da `ConfigCombateV21E`, subclasse da V21D, todas desligadas por padrão; edições em
`bots._lista_v21e`, por cima das listas da V21D). O parry que já existe (C2 da V2C: defender contra golpe rápido devolve 5)
passa a ser usado por quem o golpe repetido esmagava:

| chave | forma | edição |
|---|---|---|
| `duelista_defende_do_golpe` | duelista | "de perto, oponente insiste no golpe rápido → defender" logo depois da leitura do preparo; sai "guts < 20 → carregar" |
| `tita_defende_do_golpe` | titã | a mesma regra, depois das duas leituras do preparo; sai "guts < 20 → carregar" |
| `espelho_sem_carregar` | espelho | sai "guts < 40 → carregar" (carregar recebe dano ×1,5; a final defender recupera guts) |
| `muralha_sem_carregar` | muralha | idem (pede `muralha_lista_espelho`) |
| `muralha_contra_golpe_na_pele` | muralha | "oponente usa pele dura com frequência → contra-golpe" em segundo (o preparo sob pele ela não vê, candidato A; e não tem o contra-golpe à distância do espelho) |

As quatro chaves da V21D validada continuam ligadas; as sombrias, as listas canônicas (`ADULTOS`) e as respostas do E3 não
mudam. **Passivas e a pele dura não mudaram.** A única passiva medida, o espelho devolvendo 0,8 do disparo (para o E3 do
contra-golpe, seção 1.4), empurra a sentinela para 0,605 e não conserta o E3: não adotada.

Cada chave sozinha e acumulada (força, ε 0,05):

| variante | duelista | furioso | espelho | muralha | sentinela | emboscador | vigia | titã | amplitude |
|---|---|---|---|---|---|---|---|---|---|
| V21D | 0,477 | 0,725 | 0,416 | 0,422 | 0,564 | 0,544 | 0,446 | 0,406 | 0,319 |
| + duelista | 0,578 | 0,674 | 0,381 | 0,401 | 0,562 | 0,544 | 0,457 | 0,404 | 0,294 |
| + titã | 0,475 | 0,632 | 0,414 | 0,431 | 0,564 | 0,544 | 0,495 | 0,444 | 0,218 |
| + duelista + titã | 0,571 | 0,581 | 0,379 | 0,411 | 0,562 | 0,544 | 0,505 | 0,447 | 0,202 |
| + guardiãs sem carregar | 0,517 | 0,527 | 0,455 | 0,425 | 0,579 | 0,544 | 0,506 | 0,448 | 0,153 |
| **+ muralha: contra-golpe na pele (V21E)** | **0,517** | **0,527** | **0,455** | **0,450** | **0,579** | **0,544** | **0,477** | **0,452** | **0,129** |

**Por que funciona** (`mecanismo.json`, por partida):
- furioso × titã 0,943 → 0,291: o titã defende 9,5 golpes e devolve 47,7 de parry; os preparos interrompidos caem de 2,24 para 1,05;
- furioso × duelista 0,923 → 0,566: 8,0 golpes defendidos, 40,0 de parry;
- furioso × espelho 0,318 → 0,030 e × muralha 0,118 → 0,025: sem carregar (o espelho carregava 1,78 vez por partida, agora
  0,19), a guardiã recebe menos (87,6 → 65,5 no espelho) e o contra-golpe decide;
- muralha × vigia 0,654 → 0,852: o contra-golpe na pele dispara 4,7 vezes por partida (é o que puxa o vigia de 0,506 para
  0,477 e a muralha de 0,425 para 0,450);
- furioso × caçadores continua 1,00 (a investida na média e o avanço que prende o recuo não mudaram): o furioso cai pelo resto
  do ciclo, não pelos caçadores.

### 1.2 Tabela das formas (V21D × V21E, calibração)

| forma | força V21D | força V21E | painel V21D | painel V21E | vence (V21E) | força ε 0,15 V21D → V21E |
|---|---|---|---|---|---|---|
| duelista | 0,477 | 0,517 | 0,494 | 0,518 | 3: emboscador, sentinela, vigia | 0,484 → 0,515 |
| furioso | **0,725** | **0,527** | **0,672** | **0,532** | 4: duelista, emboscador, sentinela, vigia | 0,765 → 0,663 |
| espelho | 0,416 | 0,455 | 0,430 | 0,468 | 3: duelista, furioso, vigia | 0,340 → 0,383 |
| muralha | 0,422 | 0,450 | 0,427 | 0,449 | 4: duelista, espelho, furioso, vigia | 0,372 → 0,395 |
| sentinela | 0,564 | 0,579 | 0,545 | 0,554 | 4: emboscador, espelho, muralha, titã | 0,598 → 0,603 |
| emboscador | 0,544 | 0,544 | 0,552 | 0,552 | 3: espelho, muralha, titã | 0,620 → 0,620 |
| vigia | 0,446 | 0,477 | 0,449 | 0,488 | 3: emboscador, sentinela, titã | 0,400 → 0,415 |
| titã | 0,406 | 0,452 | 0,437 | 0,446 | 4: duelista, espelho, furioso, muralha | 0,421 → 0,407 |

Matriz da V21E (ε 0,05, pontos da linha contra a coluna):

| | duelista | furioso | espelho | muralha | sentinela | emboscador | vigia | titã |
|---|---|---|---|---|---|---|---|---|
| duelista | — | 0,434 | 0,126 | 0,331 | 0,801 | 0,884 | 0,591 | 0,453 |
| furioso | 0,566 | — | 0,030 | 0,025 | 1,000 | 1,000 | 0,775 | 0,291 |
| espelho | 0,874 | 0,970 | — | 0,497 | 0,202 | 0,003 | 0,525 | 0,117 |
| muralha | 0,669 | 0,975 | 0,503 | — | 0,000 | 0,000 | 0,852 | 0,148 |
| sentinela | 0,199 | 0,000 | 0,798 | 1,000 | — | 0,704 | 0,369 | 0,979 |
| emboscador | 0,116 | 0,000 | 0,997 | 1,000 | 0,296 | — | 0,412 | 0,986 |
| vigia | 0,409 | 0,225 | 0,475 | 0,148 | 0,631 | 0,588 | — | 0,866 |
| titã | 0,547 | 0,709 | 0,883 | 0,852 | 0,021 | 0,014 | 0,135 | — |

O ciclo: o furioso vence os caçadores (1,000 e 1,000), os caçadores vencem as guardiãs e o titã (0,798–1,000), e as guardiãs e
o titã vencem o furioso (0,970, 0,975 e 0,709). Por dentro dele, o titã vence as guardiãs (0,883 e 0,852), o vigia vence o titã
e os caçadores (0,866, 0,631, 0,588), e o duelista vence os caçadores e o vigia. Os extremos que restam (furioso × caçadores,
caçadores × muralha e × titã, espelho × emboscador) são os da V21D; nenhum é meta desta rodada.

### 1.3 As metas M-A1…M-A4 (calibração; `metas.json`)

| meta | critério | V21D | V21E |
|---|---|---|---|
| **M-A1** força contra as outras 7 | as 8 em [0,40; 0,60] | 7 de 8 (furioso 0,725) | **passa**: 0,450 (muralha) a 0,579 (sentinela); margem até a borda 0,021 |
| **M-A2** força contra o painel B | as 8 em [0,40; 0,60] | 7 de 8 (furioso 0,672) | **passa**: 0,446 (titã) a 0,554 (sentinela); margem 0,046 |
| **M-A3** mais forte − mais fraca | ≤ 0,20 | 0,319 | **passa**: 0,129 (sentinela − muralha) |
| **M-A4** lugar no ciclo | toda forma vence ≥ 2 das outras 7 | passa (mínimo 3) | **passa** (mínimo 3: duelista, espelho, emboscador, vigia) |

Informativo (não é meta): suporte do equilíbrio 3 → 5 (espelho, furioso, sentinela, titã, vigia); pares fora de [0,1; 0,9]
9 → 9 com ε 0,05 e 7 → 7 com ε 0,15; com ε 0,15 a amplitude cai de 0,425 para 0,280, mas o furioso (0,663), o emboscador
(0,620) e a sentinela (0,603) ficam acima de 0,60 e o espelho (0,383) e a muralha (0,395) abaixo de 0,40 (o ruído continua
ajudando o agressivo e derrubando as reativas, como no diagnóstico). 18,0% das partidas da matriz chegam ao limite de turnos
(V21D 17,8%).

### 1.4 M-A5: a base continua de pé

As baterias de sempre, nas sementes de calibração, com a chave ligada (`experiments/configs/v21e/bateria_*_calibracao.json`); a
V21D rodou junto, nas mesmas sementes, para comparar. Exceções já aceitas: E2, G6b e G8 (e o E4 sem escala, redefinido na escala).

| gate | critério | V21D (calibração) | V21E (calibração) | |
|---|---|---|---|---|
| G1–G9 da V2C | a bateria da base (`bateria_v2c/`) | — | igual, byte a byte, à etapa c7 (`artifacts_combate_v2c/calibracao/c7`): G1–G5, G7, G8 (1,000) e G9 (0,286) passam; G6b 0,778 (atirador) | passa (G6b aceito) |
| **E1** | nenhuma forma vence todas; suporte ≥ 4 | **falha**: suporte 3 (furioso, muralha, sentinela) | suporte 5 (espelho, furioso, sentinela, titã, vigia) | **passa** |
| **E3** técnica usada | toda técnica ≥ 5% das decisões | passa (17,5–36,7%) | passa (17,7–36,7%) | passa |
| **E3** resposta declarada | a resposta reduz a taxa dos usuários | **falha**: contra-golpe 0,428 → 0,495 | **falha**: contra-golpe 0,460 → 0,481; investida 0,514 → 0,503, marcar 0,552 → 0,521, pele dura 0,474 → 0,096 | **não fecha** (seção 1.6) |
| **E5** robustez | E1 mantido na maioria das 36 perturbações de ±10% | **falha**: 4 de 36 | 35 de 36 (cai só `turnos_pele_dura−`) | **passa** |
| G8 (V2.1) | E1 em ≥ 80% das perturbações | falha: 0,111 | 0,972 | passa (era exceção aceita) |
| G9 (V2.1) | ≤ 50% de pares decisivos com ε 0,2 | 0,250 | 0,286 | passa |
| guardião no limite | ≤ 0,20 dos confrontos com guardiã no limite de turnos | 0,188 | 0,191 | passa (margem 0,009) |
| G6b (V2.1) | favorecido ≤ 0,65 | 0,717 | 0,692 | falha (exceção aceita) |
| E2 | nenhuma espécie vence todas | ferrugem | ferrugem | falha (exceção aceita) |

A base V2C não mudou (nem `combate_v2/*.py` nem a `ConfigCombateV2C`): a bateria dela sai igual à da etapa c7, e o gate
`G1_G9_base_v2c` da bateria V2.1 continua lendo a validação gravada. **S1** (colateral, `s1.json`): nenhuma sombria vence as 8;
devastador 0,319 (vence duelista, titã e vigia), predador 0,281, colosso partido 0,225, bastião rachado 0,073 (V21D: 0,371,
0,332, 0,234 e 0,147).

### 1.5 Web: pets v9

- **Versão de pet:** `VERSAO_PET = 9` = v8 + combate equilibrado (`constantes.ts`). Nenhum evento novo; ovos novos e filhos do
  cruzamento nascem v9. Os v6–v8 continuam na V21D e os v1–v5 na V21C: assinaturas, gabaritos com o HTML e a paridade V21D
  iguais, nenhum save descartado.
- **Regras:** `CV21E` (as quatro chaves da V21D e as cinco da V21E, `versaoPet: 9`); `regrasDaVersao(v)` dá `CV21E` do v9 em
  diante e `Motor.regras` segue dela. `bots.gambitsAdulto(f, CV21E)` dá as listas novas (`BOTS_V21E`: duelista, titã, espelho e
  muralha), para o pet v9 (a semente dos gambits na evolução para adulto) e para os bots, NPCs de estilo `v21`, líderes da Liga,
  rivais das instalações e do Salão que lutam contra ele. A resolução do turno não muda.
- **Gambits híbridos:** as duas regras novas ficam fora do repertório (as candidatas dos pets v1–v8 não mudam); `regraDe` as acha
  nas listas V21E, e nos pets v9 elas voltam como candidatas de troca só para a forma que as tem (`candidatasV21E`, como
  `candidatasDoVigia`).
- **A Fábrica** (sem pet; lutas no registro do Tamer) continua na V21D (`VERSAO_FABRICA = 6`): mudar as regras dela mudaria o
  replay das tentativas gravadas. Fica para a fase 3 (M-C2) decidir.
- **Paridade:** `experiments/exportar_gabarito_v21e.py` → `web/app/test/gabaritos/combate_v21e_python.json` (136 partidas, os
  confrontos e as sementes do gabarito da V21D; 80 mudam da V21D para a V21E); `test/paridade_v21e.test.ts` refaz cada uma no TS
  (perfil, sha dos turnos, fim iguais) e confere as listas, as regras por versão, a semente dos gambits, as candidatas e a luta do
  motor v8 × v9. As chaves booleanas do `CV21E` estão no `mapa_constantes.json` (`chaves_v21e`), conferidas contra a config da
  variante e os campos da `ConfigCombateV21E` (`constantes.test.mjs`).
- **O v9 herda o v8:** medalhas, itens, Fronteira, voz própria e confiança usam testes `>=` de versão; `paridade_v21e.test.ts`
  confere que um v9 sem luta vive igual a um v8 (mesma assinatura) e que Liga, instalações, chips, fala e medalhas respondem igual.

### 1.6 O que não fechou

- **E3 do contra-golpe (M-A5).** A resposta declarada ("de perto, recuar; com guts, disparo") não reduz a taxa dos usuários do
  contra-golpe: 0,460 → 0,481 na V21E. Por usuário, a muralha cai de 0,454 para 0,000, mas o **espelho sobe de 0,466 para
  0,962**, porque a passiva dele devolve o disparo inteiro (`fracao_espelho_disparo` 1,0). A falha vem do candidato A da V21D
  (0,428 → 0,495 nas mesmas sementes; relatada na validação da V21D) e a V21E a diminui (+0,067 → +0,021), sem fechar.
  - Medido: a passiva do espelho devolvendo 0,8 do disparo (`v21e_espelho_disparo_08`) ainda falha (0,448 → 0,456) e tira a
    sentinela da faixa (0,605): baixar a devolução do disparo ajuda a sentinela contra o espelho mais do que fecha o E3. Não há
    folga para as duas coisas com as alavancas permitidas.
  - A resposta declarada (`RESPOSTAS_V21C`, a árvore de evolução) é o teste, não uma lista de forma: mudá-la está fora das
    alavancas da seção 3. **Decisão do Matheus:** aceitar o E3 do contra-golpe como exceção (como a V21D já fazia na prática)
    ou mudar a resposta declarada ao contra-golpe do espelho.
- **Margens estreitas** (calibração; o erro padrão entre sementes não foi estimado): a sentinela passa o M-A1 por 0,021
  (0,579), o guardião no limite de turnos por 0,009 (0,191) e o E5 por 35 de 36. A validação é a da fase 4.
- **Com ε 0,15** (não é meta): o furioso (0,663), o emboscador (0,620) e a sentinela (0,603) ficam acima de 0,60, e o espelho
  (0,383) e a muralha (0,395) abaixo de 0,40. Os pets reais têm ε acima do dos bots quando a disciplina é baixa (V4) e quando a
  confiança é negativa (M1, v8 em diante).
- **O furioso ainda esmaga os caçadores** (1,000 × sentinela e × emboscador) e os caçadores a muralha e o titã (0,979–1,000). É
  a C3 do diagnóstico; nenhuma alavanca da base mexeu nisso, e o M-A1 fechou sem mexer. Não é meta desta rodada.
- **Fora desta fase:** E2 (espécies) e G6b seguem como exceções; os scripts de calibração da web (`test/calibrar_*.mjs`,
  `conferir_*.mjs`, `medir_itens.mjs`) ainda medem os pets v6 (`CV21D`) e passam para os v9 (`CV21E`) nas fases 2 e 3; a
  Fábrica fica na V21D até a fase 3.

### 1.7 Testes

- Python: `python -m pytest tests/ -q` → 519 passaram e 1 foi pulado, com 7 novos em `tests/test_equilibrio_v21e.py` (chaves
  desligadas = V21D, configs V21C/V21D com a mesma classe e hash, as edições de cada chave, a muralha pedindo a lista do espelho,
  o registro da calibração e o gabarito da web). Com a chave desligada, a V3, o E1,
  a confirmatória, a voz, o M1 e as baterias V2/V2C/V21C/V21D reproduzem (os testes de sempre).
- Web: `npm run tipos` limpo; `npm test` com 280 testes em 26 arquivos (o novo `paridade_v21e.test.ts` com 8); `npm run e2e`
  com 65 testes (o ovo novo nasce v9).

### 1.8 Reprodução

```bash
python experiments/calibrar_equilibrio_geral.py --etapa todas                                            # ~15 min, 8 processos
python experiments/run_bateria_v21.py --config experiments/configs/v21e/bateria_v21e_calibracao.json     # M-A5, ~40 min
python experiments/run_bateria_v21.py --config experiments/configs/v21e/bateria_v21d_calibracao.json     # a V21D, para comparar
python experiments/run_bateria_combate.py --config experiments/configs/v21e/bateria_v2c_calibracao.json  # G1-G9 da base
python experiments/exportar_gabarito_v21e.py                                                             # gabarito da web
```

## Fase 2 — a progressão (M-B1…M-B3)

Status: **calibração fechada** (2026-09-30). As três metas passam nas sementes de calibração, **o Tortomon incluído** (com uma
grade mais fina do fator, margem estreita). A validação é a da fase 4.

- **Scripts** (em `web/app`, `npx tsx`, de 10 s a 40 s cada): `test/calibrar_escala_v6.mjs --conferir`, `test/calibrar_arenas.mjs`
  (e `--conferir`), `test/calibrar_desafiantes_v6.mjs` (e `--conferir`, `--npc npc_tier2_sentinela --grade 1.4,1.7,0.01`) e
  `test/explorar_torre.mjs`.
- **Artefatos** em `artifacts_equilibrio_geral/fase2/`; todo número abaixo vem deles:
  - `escala_conferencia.json`;
  - `arenas_calibracao.json`, `arenas_conferencia.json`;
  - `desafiantes_calibracao.json`, `desafiantes_calibracao_npc_tier2_sentinela_grade.json`, `desafiantes_conferencia.json`;
  - `torre_variantes.json`;
  - `conferencia_v6.json`;
  - `v6_arenas_conferencia.json` e `v6_desafiantes_conferencia.json`: os pets v6 com os fatores deles, nas mesmas sementes, para
    comparar.
- **Método:** o das partes 2 e 3 das medalhas, sem mudança:
  - pets de referência: as formas do estágio nas 4 espécies, com treino uniforme, no lado A;
  - a regra de cada arena e o limite de turnos do desafiado;
  - 10 partidas por semente por confronto;
  - o fator escolhido é o de maior folga entre os que passam.

  Diferenças abaixo de ~0,01 não devem ser lidas: o erro padrão entre sementes não foi estimado.

### 2.1 Os scripts medem os pets v9

- **Por padrão, os pets v9:**
  - regras `CV21E`: as listas V21E nas formas de referência do Ultimate e do Mega e nos NPCs de estilo `v21` (o Puppetmon);
  - a escala da versão 9 (`escalaDaVersao(9)`, a `CESC_V9`);
  - os fatores dos v9: `FATOR_LIDER_V9`, pela arena da luta de um pet v9, e `CESC_V9.fatorNpc`;
  - gravam em `artifacts_equilibrio_geral/fase2/`.
- **`--v6`** refaz a medição de antes (pets v6, `CV21D`, `CESC_V6`, os fatores de `ARENAS`), nas pastas de antes.
- **Opções novas:**
  - `--conferir`: sementes de calibração, os números do motor, sem escolher;
  - `--arena` e `--npc`: uma parte só;
  - `--grade`: outra grade de fatores;
  - `--lista-torre`: outra lista do líder da Torre.
- **Conferência da opção antiga** (`conferencia_v6.json`, com o sha256 de cada artefato):
  - **iguais byte a byte:** `desafiantes_calibracao.json`, `torre_variantes.json` e as três validações gravadas
    (`escala_v6/validacao.json`, `arenas/validacao.json` e `escala_v6/desafiantes_validacao.json`);
  - **`arenas/calibracao.json` e `escala_v6/calibracao.json`**, com `--limite-fracao` (a regra com que foram gerados): iguais byte a
    byte menos a linha `"limite": "fracao"`, que o cabeçalho ganhou depois;
  - a da escala só sai assim com a Torre na lista de antes, porque o artefato é do commit `28ea9f1`, anterior à lista da Torre
    (`61afaf6`). Com a lista de hoje só mudam as entradas da Torre em `lideres_por_beta`, e a Torre fica fora da escolha de β;
  - as execuções com `--validar` só refizeram artefatos dos v6 já gravados. **Nada dos pets v9 foi medido nas sementes de
    validação.**

### 2.2 O que mudou para os pets v9 (só eles)

| o quê | pets v6–v8 (não muda) | pets v9 | onde |
|---|---|---|---|
| escala: vida Rookie/Champion/Ultimate/Mega, β | 200/700/2500/23000, 0,045 (`CESC_V6`) | **os mesmos** (`CESC_V9`, objeto próprio) | `constantes.ts` |
| Guardromon (Torre) | 1,6 | **1,5** | `arenas.FATOR_LIDER_V9` |
| Piedmon (Montanha Espiral) | 1,6 | **1,4** | idem |
| Gazimon, Youkomon, Myotismon (série), MarinBullmon | 1,3; 1,5; 0,9; 1,5 | os mesmos | idem |
| Tortomon | 1,5 | **1,53** | `CESC_V9.fatorNpc` |
| Devidramon | 1,1 | 1,1 | idem |
| Puppetmon | 2,5 | **1,8** | idem |
| Machinedramon | 2,2 | **2,3** | idem |

- **Escala.** `escalaDaVersao(v)` dá a `CESC_V9` do v9 em diante, a `CESC_V6` nos v6–v8 e `null` nos v1–v5 (a `CESC`); `escalaDe` e
  `lutadorBot` passam por ela.
- **Arenas.** `arenaDaLuta(rival, v)` dá, do v9 em diante, a arena de `ARENAS_V9`: a mesma regra, lista, técnica e lutas, com o
  fator de `FATOR_LIDER_V9`. Nos v6–v8 dá a de `ARENAS`, o mesmo objeto de antes.
- **A lista do Guardromon não mudou.** Com ela a Torre fecha nos v9. `torre_variantes.json` refaz as 4 variantes da parte 2 nas
  regras v9 com o limite do desafiado: a escolhida continua a de hoje (`t1_avanca_no_disparo`, folga 0,0337), e a de antes (`t0`)
  não passa.
- **A Fronteira não muda.** Liga, instalações, Salão e Fábrica usam a vida do Mega da `CESC_V6`, que é a mesma nos v9; nenhum rival
  delas muda (fase 3).
- **Registro e saves.** Nenhum evento novo; os v1–v8 não mudam de assinatura nem de gabarito. Os v9 já salvos mudam só nas lutas
  contra o Guardromon, o Piedmon e os desafiantes com fator novo; o ramo ainda não foi publicado, então não há descarte.

### 2.3 M-B1: estágio (`escala_conferencia.json`; a escala do motor, sem mudar número)

O de baixo com o treino típico contra o de cima sem treino: bots canônicos, as 4 espécies de cada lado, regras V21E, limite do
desafiado (o de cima).

| par | meta | razão de E | pontos | vitórias | partidas | |
|---|---|---|---|---|---|---|
| Rookie (+8) × Champion | ≤ 0,10 (pontos) | 0,389 | 0,0014 | 0,0014 | 6.400 | passa |
| Champion (+22) × Ultimate | ≤ 0,10 (pontos) | 0,557 | 0,0104 | 0,0087 | 25.600 | passa |
| Ultimate (+36) × Mega | ≤ 0,10 (pontos) | 0,285 | 0,0041 | 0,0040 | 51.200 | passa |
| Rookie × Ultimate | 0,00 (vitórias) | 0,109 | 0 | 0 | 12.800 | passa |
| Champion × Mega | 0,00 (vitórias) | 0,061 | 0 | 0 | 25.600 | passa |

- **A escala dos v9 não precisou mudar.** A `CESC_V9` existe como objeto próprio por causa dos fatores dos desafiantes.
- A calibração completa da escala (a grade de β e de razões) não rodou para os v9: a meta fechou com a escala de hoje.
- Com a folga que sobra, a escala poderia chegar mais perto das razões do DW1. Fica para o Matheus decidir; não é meta.

### 2.4 M-B2: os 6 líderes (`arenas_calibracao.json`, conferido em `arenas_conferencia.json`)

Metas: sem treino ≤ 0,05; com o treino típico ≥ 0,80 (Rookie 8, Champion 22, Ultimate 36, Mega 40); pior forma ≥ 0,50. Fatores
de 0,5 a 4,0 em passos de 0,1.

| arena | líder | fator v9 (v6) | sem treino | com o treino típico | pior forma | folga |
|---|---|---|---|---|---|---|
| Campina | Gazimon | 1,3 (1,3) | 0,0025 | 0,8288 | 0,805 (sereno) | 0,0288 |
| Torre de pedra | Guardromon | **1,5** (1,6) | 0,0063 | 0,8337 | 0,675 (guardião) | 0,0337 |
| Floresta | Youkomon | 1,5 (1,5) | 0,0163 | 0,8381 | 0,560 (colosso) | 0,0338 |
| Cidadela (série de 3) | Myotismon | 0,9 (0,9) | 0,0016 | 0,9081 | 0,545 (sentinela) | 0,0450 |
| Lago | MarinBullmon | 1,5 (1,5) | 0,0075 | 0,8928 | 0,515 (sentinela) | 0,0150 |
| Montanha Espiral | Piedmon | **1,4** (1,6) | 0,0359 | 0,9144 | 0,565 (sentinela) | 0,0141 |

- **Os seis passam as três metas.**
- **Com os fatores dos v6, nas regras v9** (a primeira medida, `--conferir` antes da mudança), dois não passavam:
  - **Torre, 1,6:** com o treino 0,7925;
  - **Montanha Espiral, 1,6:** a sentinela Mega travada, 0,455.
- **A causa não é a V21E.** Os pets v6 nas mesmas sementes (`v6_arenas_conferencia.json`) dão os mesmos 0,7925 e 0,455:
  - as formas que decidem essas duas medidas (as linhas do Champion e a sentinela) têm a mesma lista na V21D e na V21E, e os
    líderes lutam igual;
  - o que pesa é a regra do limite do desafiado nas sementes de calibração: os fatores 1,6 foram calibrados antes dela e só
    validados depois (na validação dos v6: 0,8125 e 0,555).
  - Os fatores dos v6 não mudam (fora do escopo); nos v9 a recalibração, com a regra, os leva a 1,5 e 1,4.
- **Margens estreitas:**
  - a Montanha Espiral: sem treino 0,0359, folga 0,0141;
  - o Lago: a sentinela em 0,515, folga 0,015.

  A sentinela é a pior forma nos três líderes do Ultimate e do Mega.

### 2.5 M-B3: os desafiantes (`desafiantes_calibracao.json`, conferido em `desafiantes_conferencia.json`)

Metas: sem treino ≤ 0,30; com o treino típico ≥ 0,80; pior forma ≥ 0,50.

| desafiante | lugar | fator v9 (v6) | sem treino | com o treino típico | pior forma | folga |
|---|---|---|---|---|---|---|
| Tortomon | Torre de pedra | **1,53** (1,5) | 0,2825 | 0,8762 | 0,525 (colosso) | 0,0175 |
| Devidramon | Torre de pedra | 1,1 (1,1) | 0,1756 | 0,9200 | 0,680 (caçador) | 0,1200 |
| Puppetmon | Montanha Espiral | **1,8** (2,5) | 0,1519 | 0,9400 | 0,770 (espelho) | 0,1400 |
| Machinedramon | Montanha Espiral | **2,3** (2,2) | 0,1194 | 0,9819 | 0,930 (vigia) | 0,1806 |

- **Os quatro passam.**
- **O Tortomon, a exceção de sempre, fecha na calibração** com uma grade mais fina (`…_grade.json`):
  - na grade de 0,1 nenhum fator passa, como antes: 1,5 dá sem treino 0,3106 e 1,6 dá a pior forma 0,445;
  - em passos de 0,01 passam 1,51, 1,52, 1,53 e 1,54. Escolhido o de maior folga, 1,53 (folga 0,0175);
  - a janela é estreita (0,03 de fator) e a folga pequena: a validação da fase 4 pode reprová-lo;
  - o Champion não muda da V21D para a V21E, então nos v6 o 1,53 daria o mesmo nestas sementes. Os fatores dos v6 não mudaram.
- **Puppetmon e Machinedramon**, recalibrados pelo método de sempre (o fator de maior folga):
  - com os fatores dos v6 os dois já passavam nas regras v9: 2,5 dá sem 0,0416, com 0,8488 e pior 0,635; 2,2 dá 0,1359, 0,99 e 0,95;
  - o de maior folga passou a 1,8 e 2,3.

### 2.6 As metas (calibração)

| meta | critério | resultado |
|---|---|---|
| **M-B1** estágio | vizinhos ≤ 0,10; dois estágios = 0,00 | **passa** sem mudar a escala: 0,0014, 0,0104 e 0,0041; 0 e 0 vitórias |
| **M-B2** líderes | sem ≤ 0,05; com ≥ 0,80; pior ≥ 0,50 | **passa** nos 6 (Torre 1,6 → 1,5; Espiral 1,6 → 1,4); menor folga 0,0141 (Espiral) |
| **M-B3** desafiantes | sem ≤ 0,30; com ≥ 0,80; pior ≥ 0,50 | **passa** nos 4, o Tortomon com 1,53 (folga 0,0175) |

### 2.7 O que não fechou e o que fica

- Nada ficou fora das metas na calibração.
- **Riscos para a validação da fase 4:**
  - o Tortomon: janela de 1,51 a 1,54;
  - a Montanha Espiral: sem treino 0,0359, contra o teto de 0,05;
  - o Lago: sentinela 0,515;
  - a Cidadela: sentinela 0,545.
- **Os pets v6–v8 ficam como estavam:**
  - fatores e escala sem mudança;
  - o Tortomon dos v6 continua a exceção registrada;
  - a Torre e a Espiral dos v6 ficam abaixo das metas nas sementes de calibração (0,7925 e 0,455), mas passaram na validação deles.
- **Fica para a fase 3:** `conferir_liga.mjs`, `conferir_instalacoes.mjs`, `conferir_fabrica_salao.mjs`, `medir_itens.mjs` e
  `calibrar_mega.mjs` ainda medem os pets v6.

### 2.8 Testes

- `test/progressao_v9.test.ts` (5 testes):
  - os números dos v6–v8, fixos no teste;
  - a escala e os fatores por versão: `escalaDaVersao`, `escalaDe`, `perfilDe`, `lutadorBot` com `CV21D` e com `CV21E`,
    `arenaDaLuta`, e o `Motor` v8 × v9 contra cada líder e cada desafiante;
  - na arena dos v9 só o fator muda;
  - os rivais da Liga não mudam.
- `constantes.test.mjs`: `CESC_V9` e `FATOR_LIDER_V9` entram na tabela (`mapa_constantes.json`, `so_web`).
- Suíte da web: `npm run tipos` limpo; `npm test` com 285 testes em 27 arquivos; `npm run e2e` com 65 testes. Python: nada mudou.

### 2.9 Reprodução

```bash
cd web/app
npx tsx test/calibrar_escala_v6.mjs --conferir                                                  # M-B1
npx tsx test/calibrar_arenas.mjs && npx tsx test/calibrar_arenas.mjs --conferir                 # M-B2
npx tsx test/calibrar_desafiantes_v6.mjs && npx tsx test/calibrar_desafiantes_v6.mjs --conferir # M-B3
npx tsx test/calibrar_desafiantes_v6.mjs --npc npc_tier2_sentinela --grade 1.4,1.7,0.01        # o Tortomon
npx tsx test/explorar_torre.mjs                                                                 # a lista da Torre nos v9
npx tsx test/calibrar_arenas.mjs --v6 --conferir                                                # os v6, para comparar (grava em artifacts_campanha/arenas/)
```
