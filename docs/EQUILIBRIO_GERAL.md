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

## Fase 3 — o fim de jogo e os itens (M-C1…M-C3, M-D1…M-D3, M-E1)

Status: **calibração feita** (2026-09-30). Passam M-C2, M-C3, M-D1, M-D2, M-D3 e M-E1; **M-C1 não fecha** (a muralha). A validação é a da fase 4.

- **Scripts** (em `web/app`, `npx tsx`):
  - `test/conferir_liga.mjs` (e `--calibrar`);
  - `test/conferir_instalacoes.mjs`;
  - `test/conferir_fabrica_salao.mjs` (e `--calibrar`);
  - `test/medir_itens.mjs` (e `--itens-v6`).

  Todos medem os pets v9 por padrão; `--v6` refaz a medição de antes. `test/itens_ref.mjs` recebe a versão; `test/pool.mjs` é o pool de
  workers da Liga e da Fábrica.
- **Artefatos** em `artifacts_equilibrio_geral/fase3/`; todo número abaixo vem deles:
  - `liga_calibracao.json`, `liga_conferencia.json`;
  - `instalacoes_conferencia.json`;
  - `fabrica_calibracao.json`, `salao_calibracao.json`, `fabrica_salao_conferencia.json`;
  - `itens_calibracao.json` e `itens_calibracao_itens_v6.json` (os itens de antes nas regras dos v9, para comparar);
  - `conferencia_v6.json`.
- **Método:** o das partes 4a–4c e 3, com as regras dos pets v9 (V21E), a escala da versão 9 (`CESC_V9`, a mesma vida do Mega), os fatores
  dos líderes da fase 2 e o limite do desafiado. Pet de referência: as formas do estágio × 4 espécies, com treino uniforme. Só as sementes de
  calibração (3101…3505). A Fábrica tira as sementes das tentativas delas (`hashSemente("conferir-fabrica", semente, i)`, 400 por semente):
  as do jogo saem do número da tentativa. Diferenças abaixo de ~0,01 não devem ser lidas.

### 3.1 Os scripts medem os pets v9

- **Por padrão, os pets v9:** regras `CV21E`, `CESC_V9`, `FATOR_LIDER_V9`, e os números novos desta fase (Liga, Fábrica, Salão, itens) pelo
  motor.
- **`--v6`** refaz a medição de antes (V21D, `CESC_V6`, os fatores e os itens de antes). Conferência gravada em `conferencia_v6.json` (sha256):
  - iguais byte a byte: `artifacts_campanha/liga/conferencia.json`, `fronteira/conferencia.json` e `fronteira/conferencia_4c.json` (sementes de
    validação, como foram gerados; só refazem os artefatos dos v6);
  - `medir_itens.mjs` nunca tinha rodado. `--v6 --gates gi1,gi2,gi4` gravou `artifacts_campanha/itens/calibracao.json`; a linha sem item dele
    é igual à dos v6 da fase 2 nas mesmas sementes (12 de 12);
  - nos v9, a linha sem item de `itens_calibracao.json` é igual à conferência da fase 2 (17 de 17: líderes sem e com o treino típico, metas
    de estágio).
- `calibrar_mega.mjs` mede a campanha dos pets v5 e não muda: os desafiantes da Espiral dos v9 são os de `calibrar_desafiantes_v6.mjs` (fase 2).

### 3.2 O que mudou (só nos pets v9)

| o quê | pets v6–v8 (não muda) | pets v9 | onde |
|---|---|---|---|
| Liga: fator dos Megas | 1 nos 6 | WarGreymon 0,4; Seraphimon 0,3; MegaGargomon 0,1; Vikemon 1; Rosemon 1,7; Imperialdramon 0,9 | `liga.FATOR_LIGA_V9` |
| Liga: cura entre as lutas | sem cura | **sem cura** (medida, não adotada) | `liga.CURA_LIGA_V9 = 0` |
| Torre de Batalha e Palácio | fator 1 | **o mesmo** | `instalacoes.ts` |
| Fábrica: regras | V21D, fator 1, a troca não cura | V21E, rivais × 0,6 (alugados × 1), **a troca entra com a vida cheia** | `fabrica.regraFabrica(9)` |
| Salão: fator do rival | 1 | Rookie 1,15; Champion 1; Ultimate 1,05; Mega 1,05 | `salao.FATOR_SALAO_V9` |
| itens: quando valem | sempre | com o treino ≥ **metade do típico** do nível | `CIT_V9.treinoMinimo` |
| itens: onde vale a carta | campanha, arenas e arena contra bots | **só contra os NPCs da campanha** (desafiantes e líderes) | `CIT_V9.cartaSoContraNpc` |
| chip de regra | no topo da lista (sai a de nota mais baixa) | **no fim da lista**, sem tirar regra; o pet não a reordena nem troca | `itens.listaComChips`, `GambitsPet.comChips` |
| chip de stat | +2 pontos | **+1** (o ponto vale 0,5) | `CIT_V9.fatorChipStat` |

- **Separação por versão.** Liga, Salão e instalações escolhem o fator pelas regras da luta (`R.versaoPet >= 9`); os itens pela versão do pet
  (`itens.itensDosV9`; `GambitsPet.chipsNoFim` é ligado pelo motor nos v9). Assinaturas, gabaritos e replays dos v1–v8 iguais (suíte).
- **A Fábrica: a regra nova vai na tentativa.** Decisão registrada: a versão das regras é gravada no próprio evento de começo da tentativa no
  registro do Tamer (campo `v` do `fabrica`; registro versão 6, lê 1 a 5). Motivos: a Fábrica não tem pet, e o Tamer é um só para pets de
  várias versões.
  - Sem `v`: a tentativa é da Fábrica de antes e se refaz igual (teste).
  - As tentativas novas gravam `v: 9`.
  - `v` desconhecida falha alto.
- **Telas:**
  - a oferta de troca diz "entra com a vida cheia" nas tentativas dos v9;
  - a frase da Fábrica diz a regra nova;
  - Crescer · Itens diz quando os itens não fazem efeito e explica as regras dos v9;
  - a escolha da carta some fora da campanha e sem o treino mínimo, com o porquê.

### 3.3 M-C1: a Liga (`liga_calibracao.json`, `liga_conferencia.json`)

Meta: com o treino típico do Mega (40), toda forma com chance de título ≥ 0,25 e nenhuma > 0,85 (400 tentativas por forma).

**A busca** (regra registrada no script antes de rodar):
- para cada cura (0 a 0,5 da vida máxima), busca por coordenadas nos 6 fatores (0,1 a 3,0), com 8 pontos de partida;
- ordem: 1) mais formas na faixa; 2) a menor soma do que falta até a faixa; 3) a menor cura; 4) fatores mais perto de 1;
- a melhor de cada cura, medida de novo com 20 partidas:

| cura entre as lutas | formas na faixa | falta até a faixa | pior | melhor |
|---|---|---|---|---|
| **0 (escolhida)** | **7** | **0,165** | muralha 0,085 | furioso 0,725 |
| 0,1 | 6 | 0,198 | muralha 0,070 | furioso 0,830 |
| 0,2 | 6 | 0,320 | muralha 0,048 | furioso 0,840 |
| 0,3 | 5 | 0,265 | muralha 0,048 | furioso 0,883 |
| 0,4 | 6 | 0,230 | muralha 0,060 | vigia 0,800 |
| 0,5 | 6 | 0,228 | muralha 0,060 | vigia 0,805 |

Com cura a Liga fica pior: o dreno sem cura é o que segura o furioso e o vigia.

**Títulos por forma** (a Liga dos v9, `liga_conferencia.json`):

| forma | fator de antes (1, sem cura) | Liga dos v9 | |
|---|---|---|---|
| duelista | 0,315 | 0,485 | na faixa |
| furioso | 0,628 | 0,725 | na faixa |
| espelho | 0,310 | 0,255 | na faixa (folga 0,005) |
| muralha | 0,000 | **0,085** | **fora** |
| sentinela | 0,053 | 0,273 | na faixa (folga 0,023) |
| emboscador | 0,083 | 0,435 | na faixa |
| vigia | 0,428 | 0,398 | na faixa |
| titã | 0,008 | 0,263 | na faixa (folga 0,013) |

**Por luta** (o pet inteiro contra cada líder, com o fator dos v9): as travas que sobram são de estilo, no limite de turnos (que é do líder):

| luta | Mega (fator) | as formas que perdem |
|---|---|---|
| 1 | WarGreymon (0,4) | sentinela 0,675 |
| 2 | Seraphimon (0,3) | espelho 0,638, muralha 0,698 |
| 3 | MegaGargomon (0,1) | titã 0,275, muralha 0,475, vigia 0,885 |
| 4 | Vikemon (1) | sentinela 0,278, emboscador 0,520 |
| 5 | Rosemon (1,7) | espelho 0,403, muralha 0,430, duelista 0,570 |
| 6 | Imperialdramon Dragon Mode (0,9) | muralha 0,753 |

**Não fecha pela muralha.**
- Ela perde para os guardiões no limite de turnos, que é do líder (0,698 contra o Seraphimon mesmo com 0,3, 0,430 contra a Rosemon), e não
  alcança a sentinela: 0,475 contra o MegaGargomon mesmo com 0,1, o piso da grade.
- O produto das lutas dela fica perto de 0,1 (0,698 × 0,475 × 0,430 × 0,753 ≈ 0,107; com o dreno, 0,085).
- O titã só entra na faixa com o MegaGargomon no piso (0,275 contra ele).
- Nenhuma alavanca desta fase mexe nisso. As que mexeriam estão fora das permitidas:
  - o limite do desafiado (decisão do Matheus);
  - os Megas da Liga (a tabela do desenho);
  - deixar perder uma luta.

**Atenção a três números da escolha:**
- **MegaGargomon com 0,1** (o piso da grade): um Mega com um décimo da vida, para a muralha e o titã terem chance;
- **Seraphimon 0,3 e WarGreymon 0,4:** a Liga fica mais fácil para quem já vencia;
- **espelho, titã e sentinela** passam com folga de 0,005 a 0,023: a fase 4 pode reprová-los.

### 3.4 M-C2: a Fábrica (`fabrica_calibracao.json`, `fabrica_salao_conferencia.json`)

Meta: escolhendo o melhor alugado, vencer ao menos uma série em ≥ 0,25 das tentativas. Política da meta: alugar o de melhor arquétipo e
trocar pelo rival derrotado quando ele é de arquétipo melhor. A ordem dos arquétipos é a de antes, que também é a da Torre de Batalha dos v9.

- **A troca entrando inteira foi adotada** (era a variante medida e não adotada na 4c): a troca vira uma escolha de verdade, e com ela o fator
  dos rivais fica mais perto de 1.
- **A cura entre séries não mudou:** a série seguinte já começava inteira.
- **O fator dos rivais** (regra registrada: o maior fator com folga ≥ 0,05, a Fábrica mais difícil que passa), com a troca inteira:

| fator dos rivais | 1,0 | 0,9 | 0,8 | 0,7 | 0,65 | **0,6** | 0,55 | 0,5 |
|---|---|---|---|---|---|---|---|---|
| vence a 1ª luta | 0,419 | 0,593 | 0,758 | 0,858 | 0,880 | **0,895** | 0,903 | 0,913 |
| ≥ 1 série | 0,029 | 0,048 | 0,094 | 0,174 | 0,252 | **0,367** | 0,512 | 0,668 |

- **Com 0,6: passa, ≥ 1 série 0,367 (folga 0,117).**
- Relato: sem troca 0,275; alugando sempre o primeiro 0,206; média de 0,67 séries; máximo 8 séries; nenhuma tentativa no teto de 120 lutas.
- Por luta da série: 0,927, 0,769 e 0,564 (o dreno sem cura dentro da série continua).
- Com 0,45 ou menos a tentativa passa a ir longe (com 0,45, 395 de 2000 chegam ao teto).

### 3.5 M-C3: o Salão (`salao_calibracao.json`, `fabrica_salao_conferencia.json`)

Meta: cada nível, com o treino típico, entre 0,70 e 0,95 (média das formas e espécies).

**Regra** (registrada):
- só fatores ≥ 1: o rival não fica mais fraco que o de antes, e sem treino o pet não vence mais que hoje;
- entre eles, a maior folga robusta: a menor folga entre o fator e os dois vizinhos da grade (passos de 0,05).

**Por que a restrição:** a maior folga pura levava o Champion a 0,5, e aí o pet **sem treino** vencia 0,75 (a meta não olha o sem treino). O
Rookie tem um degrau: 1,2 → 0,855, 1,25 → 0,738, 1,3 → 0,591.

| nível | fator de antes → v9 | com o treino típico (fator 1 → v9) | pior forma | sem treino | folga |
|---|---|---|---|---|---|
| Rookie | 1 → **1,15** | 0,916 → 0,894 | sereno 0,80 | 0,025 | 0,056 |
| Champion | 1 → 1 | 0,754 | guardião 0,54 | 0,341 | 0,054 |
| Ultimate | 1 → **1,05** | 0,832 → 0,826 | muralha 0,625 | 0,320 | 0,124 |
| Mega | 1 → **1,05** | 0,830 → 0,826 | muralha 0,62 | 0,309 | 0,124 |

- **Passa nos 4.** A meta já passava com o fator 1; a mudança só aumenta a folga do Rookie, do Ultimate e do Mega.
- Vencer os 4 com o time médio: 0,478; sem treino, 0,0005.

### 3.6 M-E1: a Torre de Batalha e o Palácio (`instalacoes_conferencia.json`)

Meta: a melhor forma vence a 1ª luta ≥ 0,70 e a pior ≥ 0,40. **Passa sem mudar nada** (fator 1):

| instalação | melhor (vence a 1ª) | pior (vence a 1ª) | folga | média de vitórias |
|---|---|---|---|---|
| Torre de Batalha | furioso 1,000 | muralha 0,608 | 0,208 | 1,5 (muralha) a 7,6 (furioso) |
| Palácio | furioso 1,000 | muralha 0,608 | 0,208 | 1,4 (muralha) a 7,6 (furioso) |

Com a lista canônica o Palácio do pet de referência é a Torre (outras sementes).

### 3.7 M-D1…M-D3: os itens (`itens_calibracao.json`; antes: `itens_calibracao_itens_v6.json`)

"Melhor combinação": o máximo, por forma, entre todas as combinações de até 3 chips permitidos no estágio (um Tamer com as 6 medalhas) e
nenhuma carta ou uma das 3 cartas permitidas. O método é o da seção 13.7 do `DESIGN_MEDALHAS_ARENAS.md`.

**M-D1** (pet sem treino × cada líder ≤ 0,05):

| arena | sem item | itens de antes | itens dos v9 |
|---|---|---|---|
| Campina | 0,0025 | 0,425 | 0,0025 |
| Torre | 0,0063 | 0,325 | 0,0063 |
| Floresta | 0,0163 | 0,269 | 0,0163 |
| Cidadela | 0,0016 | 0,307 | 0,0016 |
| Lago | 0,0075 | 0,262 | 0,0075 |
| Espiral | 0,0359 | 0,530 | 0,0359 |

- Os itens de antes quebravam a meta nos 6 líderes, sobretudo pelos chips de stat (sozinho, o de Força leva a Espiral a 0,169) e pela Carta
  de Cura (0,123).
- Na Espiral o pet sem item já está em 0,036 (fase 2): qualquer ajuda passa do teto. Baixar os valores não resolvia (só as regras de chip, no
  topo, já davam 0,075 na Espiral; exploração sem artefato).
- **Nos v9 passa pela trava do treino mínimo:** sem treino, nenhum item faz efeito.
- **Relato no limiar** (o pet com metade do treino típico e a melhor combinação): Campina 0,199 → **0,934**, Torre 0,471 → 0,752, Floresta
  0,383 → 0,708, Cidadela 0,704 → 0,782, Lago 0,736 → 0,797, Espiral 0,818 → 0,848. Nos Rookies, os itens no limiar levam o pet além do pet
  com o treino típico sem item (0,829). A trava de 0,5 é uma escolha: não há meta para o limiar.

**M-D2** (o de baixo com o treino típico e a melhor combinação × o de cima sem treino): **passa**:

| par | meta | sem item | itens de antes | itens dos v9 |
|---|---|---|---|---|
| Rookie × Champion | ≤ 0,10 (pontos) | 0,0014 | 0,0209 | 0,0122 |
| Champion × Ultimate | ≤ 0,10 (pontos) | 0,0104 | 0,0670 | 0,0206 |
| Ultimate × Mega | ≤ 0,10 (pontos) | 0,0041 | 0,0065 | 0,0063 |
| Rookie × Ultimate | 0,00 (vitórias) | 0 | 0 | 0 |
| Champion × Mega | 0,00 (vitórias) | 0 | 0 | 0 |

**M-D3** (a matriz das 8 formas, a forma medida com a melhor combinação, as outras sem item; ≤ 0,60, **sem a exceção do furioso**). Medida sem
a trava do treino (a matriz é sem treino: mede o efeito do item em si); nos v9 sem carta, que não vale na arena contra bots:

| forma | sem item | itens de antes (com carta) | itens dos v9 | a melhor combinação dos v9 |
|---|---|---|---|---|
| duelista | 0,508 | **0,740** | 0,569 | Força + Guarda + Perseguidor |
| furioso | 0,528 | **0,812** | 0,561 | Força |
| espelho | 0,455 | **0,670** | 0,493 | Força + Aparo + Recuo |
| muralha | 0,449 | 0,571 | 0,465 | Força + Perseguidor |
| sentinela | 0,580 | **0,670** | 0,580 | nenhum |
| emboscador | 0,545 | **0,677** | **0,594** | Recuo + Oportunista + Perseguidor |
| vigia | 0,476 | **0,833** | 0,478 | Força + Guarda + Oportunista |
| titã | 0,459 | 0,594 | 0,478 | Força + Oportunista |

- Com os itens de antes 6 das 8 passavam de 0,60.
- O chip de regra no topo tira uma regra da forma e muda o ciclo (`itens_calibracao_itens_v6.json`, G-I4): o Aparo leva o vigia de 0,476 a
  0,631 e o Oportunista leva o furioso a 0,621.
- Numa exploração sem artefato (só chips, nas regras dos v9): Oportunista + Perseguidor no topo levavam o duelista a 0,630, o chip de stat
  inteiro a 0,616, e a Carta de Cura sozinha somava de +0,07 a +0,16 em todas as formas.
- **Nos v9 passa**, com a menor folga no emboscador (0,006).

**G-I4 (relato): o custo.** No fim da lista, as regras dos chips quase nunca disparam (as listas das formas têm regras que valem antes da ação
final):
- ganho de força de −0,021 a +0,048 (só o Perseguidor no emboscador passa de 0,01);
- contra os líderes, com o treino típico, nenhum chip muda a taxa em mais de 0,005.

Com os itens de antes o chip de regra mais atrapalhava do que ajudava: na matriz, de −0,25 a +0,15; o Aparo levava a Cidadela e a Espiral a
0,995 e 0,988, com a pior forma a 0,97 e 0,92. **Os chips de regra dos v9 ficam equilibrados porque quase não fazem nada.**

### 3.8 As metas (calibração)

| meta | critério | resultado |
|---|---|---|
| **M-C1** Liga | toda forma ≥ 0,25; nenhuma > 0,85 | **não fecha**: 7 de 8 na faixa; muralha 0,085 (com o fator de antes: 4 de 8, muralha 0, titã 0,008) |
| **M-C2** Fábrica | ≥ 1 série em ≥ 0,25 | **passa**: 0,367 (nas regras dos v9 com fator 1 e a troca inteira: 0,029) |
| **M-C3** Salão | cada nível em [0,70; 0,95] | **passa**: 0,894 / 0,754 / 0,826 / 0,826; menor folga 0,054 (Champion) |
| **M-E1** Torre e Palácio | melhor ≥ 0,70; pior ≥ 0,40 na 1ª luta | **passa** sem mudança: 1,000 e 0,608 nas duas |
| **M-D1** itens × treino | sem treino × cada líder ≤ 0,05 | **passa** pela trava: 0,0016–0,0359 (itens de antes: 0,262–0,530) |
| **M-D2** itens × estágio | vizinhos ≤ 0,10; dois estágios = 0 | **passa**: 0,0122 / 0,0206 / 0,0063; 0 e 0 |
| **M-D3** itens × formas | força ≤ 0,60 | **passa**: 0,465–0,594 (itens de antes: 6 de 8 acima, até 0,833) |

### 3.9 O que não fechou e o que fica

- **M-C1, a muralha** (seção 3.3). Com as alavancas permitidas a muralha não chega a 0,25. Para o Matheus decidir:
  - aceitar como exceção;
  - mudar uma regra da Liga fora das alavancas (os Megas da tabela, deixar perder uma luta);
  - medir a Liga com chips (a Liga os permite). Com os chips de antes a sentinela vencia o WarGreymon com o Aparo, e a muralha ia de 0,04 a
    0,28 contra o MegaGargomon com o Perseguidor (fator 0,5; exploração sem artefato). Com os chips dos v9 no fim da lista isso não vale mais.
- **A Liga escolhida é esquisita:** o MegaGargomon com um décimo da vida, o Seraphimon com 0,3. É o que a regra da busca dá. Com os Megas mais
  fortes a meta fica pior (com o fator 1: 4 de 8).
- **Os chips de regra dos v9 quase não fazem efeito** (seção 3.7, G-I4). É o preço de M-D3 com o chip no fim da lista. As alternativas (no
  topo com um chip de regra só, ou vetos por forma: o Aparo no vigia, o Oportunista no furioso) não foram medidas até o fim.
- **A trava do treino mínimo é uma escolha:** com metade do treino, os itens levam os Rookies além do treino típico (0,934 × 0,829 na Campina).
- **Riscos para a validação da fase 4** (folgas estreitas):
  - M-C1: o espelho (0,005), o titã (0,013), a sentinela (0,023);
  - M-D3: o emboscador (0,006);
  - M-C3: o Champion (0,054) e o Rookie (0,056, perto do degrau).
- **Os pets v6–v8 ficam como estavam:** a Liga, a Fábrica das tentativas antigas, o Salão e os itens de antes. Os itens de antes quebram G-I1
  também nos v6 (`artifacts_campanha/itens/calibracao.json`: Espiral 0,274).

### 3.10 Testes

- `test/fronteira_itens_v9.test.ts` (12 testes):
  - Liga: o fator pela versão, `jogarLiga` sem cura = a série de sempre, a cura entre as lutas, o motor v8 × v9;
  - Torre e Palácio sem mudança; Salão com o fator por nível;
  - Fábrica: as regras de cada versão, a tentativa sem versão igual à de antes, o rival × 0,6, a troca inteira, o Tamer gravando `v: 9` e
    refazendo as duas, a versão desconhecida;
  - itens: a trava, o chip de stat pela metade, o chip de regra no fim (fora da lista; no fim da lista de luta só com o treino mínimo; o
    replay), a carta só contra NPC (e o replay que falha com ela), e o v8 sem mudança.
- `progressao_v9.test.ts`: a Liga dos v9 com o fator novo. Os testes do Tamer passam a gravar a versão 6 (lê 1 a 5).
- `constantes.test.mjs`: `CIT_V9`, `FATOR_LIGA_V9`, `CURA_LIGA_V9`, `FATOR_SALAO_V9` e `FATOR_RIVAL_FABRICA_V9` na tabela (`so_web`).
- e2e da Fábrica: a tentativa nova nas regras dos v9 (três lutas, a troca com a vida cheia, `v: 9` no registro); o Tamer grava a versão 6.
- Suíte da web: `npm run tipos` limpo; `npm test` com 297 testes em 28 arquivos; `npm run e2e` com 65 testes. Python: nada mudou.

### 3.11 Reprodução

```bash
cd web/app
npx tsx test/conferir_liga.mjs --calibrar && npx tsx test/conferir_liga.mjs                     # M-C1
npx tsx test/conferir_fabrica_salao.mjs --calibrar && npx tsx test/conferir_fabrica_salao.mjs   # M-C2, M-C3
npx tsx test/conferir_instalacoes.mjs                                                           # M-E1
npx tsx test/medir_itens.mjs && npx tsx test/medir_itens.mjs --itens-v6                         # M-D1 a M-D3 (~10 e ~20 min)
npx tsx test/conferir_liga.mjs --v6; npx tsx test/conferir_instalacoes.mjs --v6; npx tsx test/conferir_fabrica_salao.mjs --v6   # os v6
npx tsx test/medir_itens.mjs --v6 --gates gi1,gi2,gi4                                           # os itens dos v6 (artifacts_campanha/itens/)
```

## Fase 4 — validação única (sementes 4101…4505)

Status: **validação feita** (2026-09-30), com **tudo congelado**: nenhum fator, lista, escala ou item mudou por causa do resultado.
Passam M-A1…M-A4, M-B1…M-B3, M-C2, M-C3, M-D1…M-D3 e M-E1; **reprovam M-C1** (a muralha, exceção aceita pelo Matheus, e o espelho,
0,010 abaixo da faixa) e, dentro de M-A5, **o E3 do contra-golpe** (como na calibração). O que reprovou está relatado na seção 4.3 e
as exceções na 4.4. As sementes de validação (4101…4505) não tinham sido usadas em nada dos pets v9 até aqui (fases 1–3 só com
3101…3505; os artefatos dos v6 nas sementes de validação são de antes da rodada).

- **Scripts:** os das fases 1–3 com a opção `--validar` (sementes de validação, os números do motor, sem escolher nada; a opção não
  muda o padrão nem os artefatos das fases 1–3): `experiments/calibrar_equilibrio_geral.py --validar` (só as variantes `v21d` e
  `v21e`; a conferência que falha alto passa a ser a validação da V21D, `artifacts_combate_v21c/validacao_v21d/`, nas mesmas
  sementes: matriz, painel, E3 e S1 da `a_c_e2v_v` saíram iguais), `experiments/configs/v21e/bateria_v21e_validacao.json` e
  `bateria_v2c_validacao.json` (M-A5), e, em `web/app`, `calibrar_escala_v6.mjs`, `calibrar_arenas.mjs`, `calibrar_desafiantes_v6.mjs`,
  `conferir_liga.mjs`, `conferir_fabrica_salao.mjs`, `conferir_instalacoes.mjs` e `medir_itens.mjs`, todos com `--validar`
  (`SEM_VALIDACAO = [4101, 4202, 4303, 4404, 4505]`, artefato `*_validacao.json`).
- **Artefatos** em `artifacts_equilibrio_geral/fase4/`; todo número abaixo vem deles: `matriz.json`, `painel.json`, `metas.json`,
  `e3.json`, `s1.json`, `mecanismo.json` (fase 1); `bateria_v21e/` e `bateria_v2c/` (M-A5); `escala_validacao.json`,
  `arenas_validacao.json`, `desafiantes_validacao.json` (fase 2); `liga_validacao.json`, `fabrica_salao_validacao.json`,
  `instalacoes_validacao.json`, `itens_validacao.json` (fase 3).
- **Método:** o de cada fase, sem mudança (N, pets de referência, regras, limite do desafiado, fatores do motor). Diferenças abaixo
  de ~0,01 não devem ser lidas como mudança: o erro padrão entre sementes não foi estimado.

### 4.1 Todas as metas: calibração × validação

| meta | alvo | calibração (fases 1–3) | validação (fase 4) | |
|---|---|---|---|---|
| **M-A1** força contra as outras 7 | as 8 em [0,40; 0,60] | 0,450 (muralha) a 0,579 (sentinela); margem 0,021 | 0,451 (muralha) a 0,576 (sentinela); margem 0,024 | **passa** |
| **M-A2** força contra o painel B | as 8 em [0,40; 0,60] | 0,446 (titã) a 0,554 (sentinela); margem 0,046 | 0,449 (titã) a 0,551 (sentinela); margem 0,049 | **passa** |
| **M-A3** mais forte − mais fraca | ≤ 0,20 | 0,129 | 0,125 (sentinela − muralha) | **passa** |
| **M-A4** lugar no ciclo | toda forma vence ≥ 2 das outras 7 | mínimo 3 | mínimo 3 (duelista, emboscador, muralha, vigia) | **passa** |
| **M-A5** a base de pé | G1–G9 da V2C e E1/E3/E5 da V21C (exceções aceitas: E2, G6b, G8) | E1 suporte 5; E3 técnica 17,7–36,7%; E3 resposta: **contra-golpe 0,460 → 0,481**; E5 35/36; G8 0,972; G9 0,286; guardião 0,191; G6b 0,692, E2 (ferrugem) e E4 (0,887–0,994) como exceções; G1–G9 da base = etapa c7 | E1 suporte 5 (espelho, furioso, sentinela, titã, vigia); E3 técnica 17,7–36,8%; **contra-golpe 0,458 → 0,480**; E5 35/36 (cai `custo_pele_dura−`); G8 0,972; G9 0,286; guardião 0,190; G6b 0,693 (sentinela 0,919), E2 (ferrugem) e E4 (0,886–0,998) como exceções; G1–G9 da base = `validacao_bots` byte a byte (só G6b do atirador, exceção) | **passa com as exceções aceitas, menos o E3 do contra-golpe** (pendente, como na fase 1) |
| **M-B1** estágio | vizinhos ≤ 0,10 (pontos); dois estágios = 0,00 (vitórias) | 0,0014 / 0,0104 / 0,0041; 0 e 0 | 0,0008 / 0,0110 / 0,0041; 0 e 0 | **passa** |
| **M-B2** líderes das 6 arenas | sem treino ≤ 0,05; com o típico ≥ 0,80; pior forma ≥ 0,50 | sem 0,0016–0,0359; com 0,8288–0,9144; pior 0,515 (Lago); menor folga 0,0141 (Espiral) | sem 0,0006–0,0284; com 0,8575–0,9188; pior 0,535 (Cidadela); menor folga 0,0216 (Espiral) | **passa** nos 6 |
| **M-B3** desafiantes | sem ≤ 0,30; com ≥ 0,80; pior ≥ 0,50 | Tortomon 0,2825 / 0,8762 / 0,525 (folga 0,0175); os outros 3 com folga ≥ 0,12 | Tortomon 0,2938 / 0,8794 / 0,535 (folga 0,0062); Devidramon 0,1862 / 0,9050 / 0,620; Puppetmon 0,1484 / 0,9306 / 0,745; Machinedramon 0,1100 / 0,9753 / 0,870 | **passa** nos 4 |
| **M-C1** Liga | toda forma ≥ 0,25 e nenhuma > 0,85 | 7 de 8; muralha 0,085; espelho 0,255 | 6 de 8; **muralha 0,085**, **espelho 0,240**; titã 0,260, sentinela 0,2675; máximo furioso 0,725 | **reprova** (muralha: exceção aceita; espelho: pendente) |
| **M-C2** Fábrica | ≥ 1 série em ≥ 0,25 das tentativas | 0,367 | 0,390 (folga 0,140) | **passa** |
| **M-C3** Salão | cada nível em [0,70; 0,95] | 0,894 / 0,754 / 0,826 / 0,826; menor folga 0,054 | 0,8725 / 0,760 / 0,8078 / 0,8194; menor folga 0,060 (Champion) | **passa** |
| **M-D1** itens × treino | sem treino, com os melhores itens, × cada líder ≤ 0,05 | 0,0016–0,0359 (= sem item, pela trava) | 0,0006–0,0284 (= sem item, pela trava) | **passa** |
| **M-D2** itens × estágio | vizinhos ≤ 0,10; dois estágios = 0 | 0,0122 / 0,0206 / 0,0063; 0 e 0 | 0,0122 / 0,0215 / 0,0064; 0 e 0 | **passa** |
| **M-D3** itens × formas | força com o melhor item ≤ 0,60 | 0,465–0,594 (emboscador, folga 0,006) | 0,463–0,595 (emboscador, folga 0,005) | **passa** |
| **M-E1** Torre e Palácio | melhor forma ≥ 0,70 e pior ≥ 0,40 na 1ª luta | 1,000 e 0,608 (as duas) | Torre 1,000 (furioso) e 0,6475 (muralha); Palácio 1,000 e 0,580 | **passa** |

### 4.2 Detalhes por fase

**Fase 1, as formas** (`matriz.json`, `painel.json`, `metas.json`; V21E, ε 0,05):

| forma | força (cal → val) | painel (cal → val) | vence (val) |
|---|---|---|---|
| duelista | 0,517 → 0,506 | 0,518 → 0,515 | 3: emboscador, sentinela, vigia |
| furioso | 0,527 → 0,527 | 0,532 → 0,532 | 4: duelista, emboscador, sentinela, vigia |
| espelho | 0,455 → 0,462 | 0,468 → 0,474 | 4: duelista, furioso, muralha, vigia |
| muralha | 0,450 → 0,451 | 0,449 → 0,453 | 3: duelista, furioso, vigia |
| sentinela | 0,579 → 0,576 | 0,554 → 0,551 | 4: emboscador, espelho, muralha, titã |
| emboscador | 0,544 → 0,543 | 0,552 → 0,549 | 3: espelho, muralha, titã |
| vigia | 0,477 → 0,480 | 0,488 → 0,482 | 3: emboscador, sentinela, titã |
| titã | 0,452 → 0,455 | 0,446 → 0,449 | 4: duelista, espelho, furioso, muralha |

- Nenhuma forma mudou mais de 0,011 da calibração para a validação; a V21D nas mesmas sementes reproduz a validação da V21D
  (furioso 0,722, as 7 outras em [0,407; 0,562]), como o `validacao_v21d/` já dizia.
- Espelho × muralha virou 0,506/0,494 (na calibração 0,497/0,503): o espelho passa a "vencer" a muralha e ela deixa de vencê-lo; os
  dois continuam com ≥ 3 vitórias, e a diferença está abaixo do ruído.
- Informativo (não é meta): suporte 5 (espelho, furioso, sentinela, titã, vigia); 9 pares fora de [0,1; 0,9] com ε 0,05 e 7 com
  ε 0,15; com ε 0,15 o furioso 0,666, o emboscador 0,620 e a sentinela 0,597 (na calibração 0,603) ficam acima de 0,60 e o espelho
  0,384 e a muralha 0,397 abaixo de 0,40; amplitude 0,282; 18,0% das partidas no limite de turnos.
- **S1** (`s1.json`): nenhuma sombria vence as 8; devastador 0,321 (duelista, titã, vigia), predador 0,277, colosso partido 0,226,
  bastião rachado 0,077.
- **E3 da resposta declarada** (`e3.json`, V21E): investida 0,518 → 0,499, marcar 0,549 → 0,524 e pele dura 0,471 → 0,097 reduzem;
  **contra-golpe 0,458 → 0,480 não reduz** (muralha 0,456 → 0,000; espelho 0,461 → 0,961, pela passiva que devolve o disparo),
  como na calibração (0,460 → 0,481) e na V21D nas mesmas sementes (0,431 → 0,496).

**Fase 2, a progressão** (`escala_validacao.json`, `arenas_validacao.json`, `desafiantes_validacao.json`):

| líder / desafiante | fator | sem treino | com o treino típico | pior forma | folga (cal → val) |
|---|---|---|---|---|---|
| Gazimon (Campina) | 1,3 | 0,0075 | 0,8575 | 0,800 (sereno) | 0,0288 → 0,0425 |
| Guardromon (Torre de pedra) | 1,5 | 0,0081 | 0,8656 | 0,715 (guardião) | 0,0337 → 0,0419 |
| Youkomon (Floresta) | 1,5 | 0,0213 | 0,8675 | 0,605 (colosso) | 0,0338 → 0,0288 |
| Myotismon (Cidadela, série de 3) | 0,9 | 0,0006 | 0,9063 | 0,535 (sentinela) | 0,0450 → 0,0350 |
| MarinBullmon (Lago) | 1,5 | 0,0088 | 0,8972 | 0,560 (sentinela) | 0,0150 → 0,0413 |
| Piedmon (Montanha Espiral) | 1,4 | 0,0284 | 0,9188 | 0,655 (sentinela) | 0,0141 → 0,0216 |
| Tortomon (Torre de pedra) | 1,53 | **0,2938** | 0,8794 | 0,535 (colosso) | 0,0175 → **0,0062** |
| Devidramon (Torre de pedra) | 1,1 | 0,1862 | 0,9050 | 0,620 (caçador) | 0,1200 → 0,1050 |
| Puppetmon (Montanha Espiral) | 1,8 | 0,1484 | 0,9306 | 0,745 (muralha) | 0,1400 → 0,1306 |
| Machinedramon (Montanha Espiral) | 2,3 | 0,1100 | 0,9753 | 0,870 (vigia) | 0,1806 → 0,1753 |

- As três metas passam; os riscos apontados na fase 2 (a Espiral sem treino, o Lago e a Cidadela com a sentinela) ficaram com mais
  folga, não menos. **O Tortomon passa por 0,0062** (sem treino 0,2938 contra o teto 0,30): é a folga mais estreita da rodada e está
  abaixo do ruído; a janela de 1,51–1,54 da calibração se confirma estreita.
- Metas de estágio: Rookie × Champion 0,0008, Champion × Ultimate 0,0110, Ultimate × Mega 0,0041 (pontos); Rookie × Ultimate e
  Champion × Mega sem vitória (12.800 e 25.600 partidas).

**Fase 3, o fim de jogo** (`liga_validacao.json`, `fabrica_salao_validacao.json`, `instalacoes_validacao.json`):

| forma | títulos na Liga (cal → val) | | forma | títulos (cal → val) | |
|---|---|---|---|---|---|
| duelista | 0,485 → 0,455 | na faixa | sentinela | 0,2725 → 0,2675 | na faixa (folga 0,0175) |
| furioso | 0,725 → 0,725 | na faixa | emboscador | 0,435 → 0,490 | na faixa |
| espelho | 0,255 → **0,240** | **fora** (0,010 abaixo) | vigia | 0,3975 → 0,4075 | na faixa |
| muralha | 0,085 → **0,085** | **fora** (exceção aceita) | titã | 0,2625 → 0,260 | na faixa (folga 0,010) |

- Por luta, as travas de estilo são as da calibração: sentinela 0,71 contra o WarGreymon; espelho 0,595 e muralha 0,7025 contra o
  Seraphimon; muralha 0,3775 e titã 0,3025 contra o MegaGargomon; sentinela 0,2675 e emboscador 0,5175 contra o Vikemon; espelho
  0,430, muralha 0,440 e duelista 0,600 contra a Rosemon; muralha 0,7625 contra o Imperialdramon. O espelho cai nas lutas 2 e 5
  (chega à 6ª em 0,2425 e vence 0,240).
- Com o fator de antes (1 nos 6, relato): 4 de 8 na faixa, muralha 0,000, titã 0,0125.
- Fábrica (política da meta, 2.000 tentativas): vence a 1ª luta 0,8965, ≥ 1 série **0,390**, média de 0,702 séries, máximo 10,
  nenhuma no teto; por luta da série 0,929 / 0,782 / 0,568. Sem troca 0,2865; alugando o primeiro 0,205.
- Salão (treino típico): Rookie 0,8725 (pior sereno 0,755), Champion 0,760 (guardião 0,5625), Ultimate 0,8078 (muralha 0,590),
  Mega 0,8194 (muralha 0,600); sem treino 0,0175 / 0,3481 / 0,3272 / 0,3066; vencer os 4 com o time médio 0,4389 (sem treino 0,0006).
- Torre de Batalha: vence a 1ª de 0,6475 (muralha) a 1,000 (furioso), média de vitórias 1,5 (muralha) a 7,6 (furioso); Palácio
  0,580 (muralha) a 1,000, média 1,5 a 7,5. Folga da meta 0,2475 e 0,180.

**Fase 3, os itens** (`itens_validacao.json`; 775 s com 6 workers):

| meta | o quê | calibração | validação |
|---|---|---|---|
| M-D1 | sem treino + os melhores itens × cada líder | 0,0025 / 0,0063 / 0,0163 / 0,0016 / 0,0075 / 0,0359 | 0,0075 / 0,0081 / 0,0213 / 0,0006 / 0,0088 / 0,0284 (Campina, Torre, Floresta, Cidadela, Lago, Espiral) |
| M-D2 | o de baixo com o típico + os melhores itens × o de cima | 0,0122 / 0,0206 / 0,0063; 0 e 0 | 0,0122 / 0,0215 / 0,0064; 0 e 0 |
| M-D3 | força com a melhor combinação | duelista 0,569, furioso 0,561, espelho 0,493, muralha 0,465, sentinela 0,580, emboscador 0,594, vigia 0,478, titã 0,478 | duelista 0,570, furioso 0,560, espelho 0,494, muralha 0,463, sentinela 0,584, **emboscador 0,595**, vigia 0,476, titã 0,475 |

- M-D1 continua passando **pela trava do treino mínimo**: sem treino nenhum item faz efeito, e a linha "com os melhores itens" é a
  linha sem item da fase 2 nas mesmas sementes (as 6 iguais a `arenas_validacao.json`).
- Relato no limiar (metade do treino típico + a melhor combinação): Campina 0,2075 → 0,9387, Torre 0,4738 → 0,7406, Floresta 0,3831
  → 0,7225, Cidadela 0,7228 → 0,7991, Lago 0,7284 → 0,8113, Espiral 0,8209 → 0,845 (na calibração 0,934 / 0,752 / 0,708 / 0,782 /
  0,797 / 0,848): nos Rookies os itens no limiar continuam levando o pet além do treino típico sem item (0,8575).
- M-D3: a melhor combinação de cada forma é a mesma da calibração (sentinela e vigia sem item); o emboscador passa por 0,005
  (0,5953, com Recuo + Oportunista + Perseguidor), abaixo do ruído. Com a regra do limite do desafiado (relato) todas ficam ≤ 0,54.
- G-I4 (relato): os chips de regra no fim da lista seguem quase sem efeito: ganho de força de −0,022 a +0,050 (só o Perseguidor no
  emboscador, +0,0495, passa de 0,01; o Aparo é 0 nas 8); contra os líderes com o treino típico, nenhum chip muda a taxa em mais de
  0,0013.

### 4.3 O que reprovou e por quê

- **M-C1, a muralha (0,085; exceção aceita, seção 4.4).** O mesmo da calibração: ela perde para os guardiões no limite de turnos,
  que é do líder (0,7025 contra o Seraphimon mesmo com 0,3; 0,440 contra a Rosemon; 0,7625 contra o Imperialdramon), e não alcança
  a sentinela (0,3775 contra o MegaGargomon com 0,1, o piso da grade). O produto das lutas dela fica perto de 0,1. Nenhuma alavanca
  permitida mexe nisso (o limite do desafiado e os Megas da tabela são decisões do Matheus).
- **M-C1, o espelho (0,240; pendente).** Na calibração passava por 0,005 (0,255) e a fase 3 já o apontava como risco. Na validação
  perde 0,010 a mais: cai nas lutas 2 (Seraphimon, espelho × espelho, 0,595) e 5 (Rosemon, 0,430), e chega à 6ª em 0,2425. A
  diferença para a faixa (0,010) está no tamanho do ruído entre sementes (~0,01, não estimado): não dá para dizer que o espelho
  "piorou", só que a folga de 0,005 não aguentou a troca de sementes. O titã (0,260) e a sentinela (0,2675) passam por 0,010 e
  0,0175: as três formas reativas estão na borda da Liga.
- **M-A5, o E3 do contra-golpe (0,458 → 0,480; pendente desde a fase 1).** A resposta declarada ("de perto, recuar; com guts,
  disparo") zera a muralha (0,456 → 0,000) e dispara o espelho (0,461 → 0,961), porque a passiva dele devolve o disparo inteiro. Vem
  da V21D (0,431 → 0,496 nas mesmas sementes); a V21E diminui a diferença (+0,065 → +0,022) sem fechar. A decisão continua a da
  fase 1: aceitar como exceção ou mudar a resposta declarada do espelho (fora das alavancas).
- **M-A5, o resto (`bateria_v21e/gates.json`, `bateria_v2c/`).** A bateria V2.1 com a V21E nas sementes de validação sai como na
  calibração: E1 passa (suporte 5), E5 35 de 36 (a perturbação que cai mudou: `turnos_pele_dura−` na calibração, `custo_pele_dura−`
  na validação; o E1 continua valendo em 0,972, G8), G9 0,286, o guardião no limite de turnos 0,190 (margem 0,010, como os 0,009 da
  calibração). Reprovam só as exceções já aceitas: E2 (ferrugem), G6b (0,693; a sentinela 0,919) e E4 (o adulto esmaga o adolescente
  da mesma linha, 0,886–0,998: redefinido na escala, que é o M-B1). A bateria da base V2C sai **byte a byte igual** à validação
  gravada da V2C (`artifacts_combate_v2c/validacao_bots/`, os 5 artefatos): a V21E não tocou na base.
- **Folgas que ficaram estreitas (passam, mas abaixo do ruído):** o Tortomon em M-B3 (0,2938 contra 0,30, folga 0,0062; na
  calibração 0,0175), o emboscador em M-D3 (0,5953, folga 0,005; 0,006), o titã (0,010) e a sentinela (0,0175) em M-C1. As folgas da
  fase 2 que preocupavam (Espiral, Lago, Cidadela) cresceram na validação; a do Champion no Salão (0,060) e a do Rookie (0,0775) também.

### 4.4 Exceções

**Aceitas pelo Matheus:**
- **E2** (ferrugem vence as outras espécies), **G6b** (o atirador nos espelhos com condição) e **G8** (V2.1): aceitas na V21C/V2C;
  continuam valendo (seção 4.1, M-A5).
- **M-C1, a muralha na Liga (0,085 na calibração e na validação): aceita como exceção em 2026-09-30.** Motivo: perde para os
  guardiões pelo limite do desafiado (que é do líder) e não alcança o MegaGargomon com nenhuma alavanca permitida (o fator já está no
  piso da grade, 0,1). Nenhum número muda.

**Pendentes de aceite do Matheus:**
- **E3 do contra-golpe** (M-A5): a resposta declarada não reduz os usuários (0,458 → 0,480), pelo espelho. Opções: aceitar como
  exceção (como a V21D fazia na prática) ou mudar a resposta declarada ao contra-golpe do espelho.
- **M-C1, o espelho na Liga** (0,240, 0,010 abaixo da faixa; na calibração 0,255). Opções: aceitar como exceção (a diferença está
  no ruído), ou reabrir a calibração da Liga (fora desta rodada: a fase 4 é única e nada muda por causa do resultado).
- **E4 da V21C** (o adulto esmaga o adolescente): aceito na V21C e redefinido na escala (M-B1, que passa); a bateria V2.1 continua
  a medi-lo sem escala e a reprová-lo (0,886–0,998), só como relato.

### 4.5 Testes

- **O merge com a main** (commit `76643fb`: a voz/revanche e o comando pelo chat, PR #91; conflitos em `TelaArena.tsx`,
  `TelaCampanha.tsx` e `docs/REGISTRO_DESVIOS.md`): nada quebrou. Em `web/app`, `npm ci`, `npm run tipos` limpo e `npm test` com
  **306 testes em 29 arquivos**, todos passando (85 s). Na raiz, `python -m pytest tests/ -q`: **545 passaram, 1 pulado** (15 min).
- Os scripts com `--validar` não mudam o padrão: a opção só troca as sementes, a pasta (`fase4/`) e o nome do artefato; as fases
  1–3 não foram rodadas de novo e os artefatos delas estão intactos (`git status`).
- A conferência que falha alto do Python (`calibrar_equilibrio_geral.py --validar`): matriz, painel, E3 e S1 da V21D nas sementes de
  validação saem iguais a `artifacts_combate_v21c/validacao_v21d/` (`v21d_igual_validacao_v21d*: true` nos artefatos).
- Tempos: `calibrar_equilibrio_geral.py --validar` 8 min com 6 processos; a bateria V21E 19 min e a da base 1 min (um processo
  cada); os `.mjs` de 10 s a 13 min (`medir_itens`, 6 workers). Nenhum processo além de 8 ao mesmo tempo.
- As duas baterias terminam com rc 2 (REPROVADA) pelas exceções aceitas e pelo E3 do contra-golpe; é o esperado e está na tabela.

### 4.6 Reprodução

```bash
cd web/app && npm ci && npm run tipos && npm test                                                     # o merge com a main
python -m pytest tests/ -q
python experiments/calibrar_equilibrio_geral.py --validar --etapa todas --processos 6                  # M-A1 a M-A4, E3, S1 (~8 min)
python experiments/run_bateria_v21.py --config experiments/configs/v21e/bateria_v21e_validacao.json     # M-A5 (~20 min)
python experiments/run_bateria_combate.py --config experiments/configs/v21e/bateria_v2c_validacao.json  # G1-G9 da base
cd web/app
npx tsx test/calibrar_escala_v6.mjs --validar                                                           # M-B1
npx tsx test/calibrar_arenas.mjs --validar                                                              # M-B2
npx tsx test/calibrar_desafiantes_v6.mjs --validar                                                      # M-B3
npx tsx test/conferir_instalacoes.mjs --validar                                                         # M-E1
DIGILAB_WORKERS=6 npx tsx test/conferir_liga.mjs --validar                                              # M-C1
DIGILAB_WORKERS=6 npx tsx test/conferir_fabrica_salao.mjs --validar                                     # M-C2, M-C3
DIGILAB_WORKERS=6 npx tsx test/medir_itens.mjs --validar                                                # M-D1 a M-D3 (~15 min)
```
