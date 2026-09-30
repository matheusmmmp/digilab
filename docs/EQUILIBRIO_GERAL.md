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
