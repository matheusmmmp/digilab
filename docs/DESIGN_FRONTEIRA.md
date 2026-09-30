# Design — a Fronteira de Batalha (parte 4 das medalhas)

Status: **Fronteira completa no jogo web:** partes 4a, 4b e 4c implementadas (branches `fronteira-4a`, `fronteira-4b` e `fronteira-4c`, 2026-09-30; seções 7, 8 e 9; a Fronteira inteira na seção 10). Especificação pedida pelo Matheus (2026-09-30: "segue com a parte 4 da fronteira"). Detalha a seção 7 do `docs/DESIGN_MEDALHAS_ARENAS.md`. Só o jogo web e só os pets v6; a pesquisa em Python não muda.

- Todo número é PROPOSTO, sem fonte.
- **Sem rodada de equilíbrio nesta parte** (decisão do Matheus: o equilíbrio fica para uma rodada geral, depois das próximas mecânicas do combate). Os números abaixo só precisam deixar o jogo jogável.

## 1. O que é

O final do jogo. Depois das 6 medalhas, o Tamer desafia a **Liga dos Líderes**: os 6 líderes, em sequência, cada um lutando com um dos **melhores Digimons** do jogo. Vencer a Liga faz do jogador o **Campeão** e fecha a jornada. Depois do título, a Fronteira abre **instalações** com regras próprias, para rejogar por recordes e títulos, nunca por força.

## 2. A Liga dos Líderes

- **Acesso:** as 6 medalhas.
- **Formato:** 6 lutas seguidas, na ordem das arenas: Campina, Torre, Floresta, Cidadela, Lago, Espiral.
- **Sem cura entre as lutas:** a vida e o guts do pet passam de uma luta para a outra, como na série da Cidadela.
- **O que vale:** os chips equipados valem; **as cartas não valem na Liga**. Perder uma luta encerra a tentativa. Tentar de novo não tem custo.
- **Os melhores Digimons:** cada líder luta com um Mega do jogo, cada um de um **arquétipo adulto diferente** e com a lista de regras canônica dele (V21D), para a Liga testar o conhecimento do jogador sobre os arquétipos, não só a força. A sugestão, que o implementador pode ajustar só se um sprite faltar:

  | líder | luta com (Mega da cadeia · arquétipo) | espécie |
  |---|---|---|
  | Gazimon (Campina) | WarGreymon · Furioso | brasa |
  | Guardromon (Torre) | Seraphimon · Espelho | cirro |
  | Youkomon (Floresta) | MegaGargomon · Sentinela | ferrugem |
  | Myotismon (Cidadela) | Vikemon · Titã | limo |
  | MarinBullmon (Lago) | Rosemon · Muralha | limo |
  | Piedmon (Espiral) | Imperialdramon Dragon Mode · Duelista | ferrugem |

  (Na evolução canônica o Mega de cada linha é o mesmo Digimon para as duas formas adultas; o arquétipo é que muda. Os
  sprites já estão no atlas.)

  Regra: 6 arquétipos distintos entre os 8 e as 4 espécies presentes. O implementador só troca uma linha da tabela se algo faltar, e registra a troca.
- **A força dos rivais:** estágio Mega na escala v6, com um fator de rival igual ao do Piedmon da Espiral (o líder mais forte hoje). Sem calibração: só conferir que um Mega bem treinado, com a forma certa, consegue vencer uma luta da Liga (o jogo precisa ser completável).
- **O limite de turnos:** vence quem foi desafiado, ou seja, o líder da Liga.
- **O título:** vencer as 6 dá o evento `campeao` no registro do Tamer (com o pet e a forma), a **medalha de ouro** na tela de Medalhas e a **tela de conclusão da jornada**. A conclusão deixa de ser a vitória sobre o Piedmon na Espiral e passa a ser a Liga.

## 3. As instalações (depois do título)

Cada uma com o recorde guardado no registro do Tamer. **Nada delas deixa o pet mais forte fora da Fronteira.**

| instalação | regra | recorde |
|---|---|---|
| **Torre de Batalha** | sequência de lutas contra Megas sorteados (bots canônicos das 8 formas, espécies variadas), sem cura entre elas; perdeu, acabou | maior sequência de vitórias |
| **Palácio** | o pet decide sozinho: travas, vetos e chips de regra não valem | maior sequência |
| **Fábrica** | o jogador não usa o próprio pet: escolhe 1 de 3 Digimon **alugados** (Mega, formas e espécies sorteadas, lista canônica), luta 3 lutas; ao vencer, pode trocar o alugado pelo rival derrotado | maior sequência de séries vencidas |
| **Salão** | o jogador luta com um pet de **cada estágio** (Rookie, Champion, Ultimate, Mega), escolhidos entre os pets guardados, cada um contra um rival do mesmo estágio | quantos estágios venceu seguidos |

- **O sorteio dos rivais** vem de uma semente derivada do registro do Tamer (número da tentativa), gravada no evento da tentativa. O replay confere.
- **As lutas da Fábrica não envolvem o pet do jogador**, então vão só para o registro do Tamer, com a semente de cada luta, e são reproduzíveis sozinhas.
- **O Salão** usa pets guardados. Cada luta vai para o registro do pet que lutou, como qualquer luta; o recorde vai para o Tamer.

## 4. Registro e replay

- **Registro do pet:** as lutas da Liga, da Torre, do Palácio e do Salão entram como o evento de luta `l` de sempre. A regra da instalação sai do rival e do tipo da tentativa, gravado num evento novo `f` (início da tentativa na Fronteira) quando for preciso.
- **Registro do Tamer:** `campeao`, `recorde` (instalação e valor) e as tentativas da Fábrica.
- **Pets v1–v5:** não entram na Fronteira.

## 5. Telas

- Uma ilha nova no mapa, a **Fronteira**, depois da Espiral, com a Liga e, depois do título, as quatro instalações.
- **Tela da Liga:** os 6 líderes com os Megas deles, a luta atual ("luta 3 de 6") e a vida que sobrou.
- **Tela de cada instalação:** a regra em uma frase, o recorde e "tentar".
- **Medalhas:** a medalha de ouro e os recordes.
- **Conclusão da jornada:** passa a vir da Liga.

## 6. Partes (um PR cada)

1. **4a — a Liga e o fim do jogo:** a ilha da Fronteira, a Liga, o título, a medalha de ouro e a conclusão.
2. **4b — Torre de Batalha e Palácio:** as duas instalações que usam o pet do jogador.
3. **4c — Fábrica e Salão:** o aluguel (lutas só no registro do Tamer) e o pet por estágio.

## 7. O que a parte 4a implementou (2026-09-30): a Liga e o fim do jogo

Só `web/app/`, só pets v6; a pesquisa em Python não muda (`docs/REGISTRO_DESVIOS.md`, 2026-09-30). Sem rodada de equilíbrio.

**A Liga** (`web/app/motor/liga.ts`, tabela `LIGA`): os 6 líderes da tabela da seção 2, sem troca (todos os sprites estão no atlas).

| luta | líder | Mega | arquétipo | brasão | fator |
|---|---|---|---|---|---|
| 1 | Gazimon (Campina) | WarGreymon | Furioso | Coragem | 1 |
| 2 | Guardromon (Torre de pedra) | Seraphimon | Espelho | Amizade | 1 |
| 3 | Youkomon (Floresta) | MegaGargomon | Sentinela | Conhecimento | 1 |
| 4 | Myotismon (Cidadela) | Vikemon | Titã | Sinceridade | 1 |
| 5 | MarinBullmon (Lago) | Rosemon | Muralha | Sinceridade | 1 |
| 6 | Piedmon (Montanha Espiral) | Imperialdramon Dragon Mode | Duelista | Conhecimento | 1 |

- **O rival:** a forma Mega do arquétipo na espécie da tabela, com a técnica da linha, a passiva da forma, o caráter canônico e a lista
  canônica sob as regras V21D (a Rosemon, muralha, luta com a lista do espelho, como todo muralha V21D); ε dos bots canônicos (0,05).
  E = vida do Mega na escala dos pets v6 (23000) × fator, sem treino.
- **O fator: 1, não o do Piedmon (1,6).** Com o fator do desenho cada luta sozinha é vencível pela forma certa, mas **a Liga inteira não**:
  nenhuma das 8 formas, em nenhuma espécie, venceu as 6 seguidas (conferência abaixo). O jogo tem de ser completável, e ajustar só uma
  luta não resolvia (o dreno vem das quatro primeiras: com a Liga a 1,6 e a 5ª e a 6ª a 0,3, a melhor forma ainda vence 0,03 nas
  sementes de calibração). A Liga ficou sem fator: o Mega na escala, como ele é. O Piedmon da Espiral precisava do 1,6 porque é um NPC de
  perfil neutro, sem técnica nem passiva e com ε 0,2; os Megas da Liga lutam com a técnica, a passiva e a lista canônica. Não é
  calibração: a grade abaixo é relato, e o 1 não foi escolhido por uma meta (desvio registrado).
- **Regras:** 6 lutas seguidas num evento só (`arenas.jogarSerie`, a generalização da série da Cidadela: a vida e o guts do pet passam; cada
  líder começa inteiro; para na primeira que não for vitória; as lutas 2 a 6 com sementes derivadas). Os chips valem (estão no pet);
  **as cartas não valem**: o motor recusa a carta antes da luta da Liga, e o replay falha se um `k` vier logo antes dela. O limite de
  turnos é do desafiado, o líder (`desafiadoDaVersao`). Perder encerra a tentativa; tentar de novo não custa nada (as lesões da derrota
  seguem a regra de toda luta).
- **Entrada:** as 6 medalhas, pelo que o pet conhece (evento `u`; o motor não lê o Tamer); o In-Training não luta.
  `Motor.porqueNaoLiga`.

**Registro e replay (seção 4):** a tentativa é um evento `l` de sempre, `{r: "liga", s}`; a regra sai do rival, então **não foi preciso
o evento `f`**. O motor conta `liga = {tentativas, titulos}` do registro; isso entra na assinatura só depois da primeira tentativa (a dos
pets v6 que nunca entraram não muda). Replay com a Liga, com a carta proibida e sem as medalhas: `web/app/test/liga.test.ts`.

**O título:** a primeira vitória de um pet na Liga grava no registro do Tamer `["campeao", {n, quando, pet, forma, tick}]` (registro
versão 3, lê a 1 e a 2; só depois das 6 medalhas; um por pet; o primeiro é o título do Tamer). A **conclusão da jornada** dos pets v6 vem
da Liga (`jornada.concluiuJornada`, chave própria de "conclusão vista"; os marcos ganham "Venceu a Liga dos Líderes"); nos v1–v5 continua
o chefe da campanha.

**Telas:** a ilha da **Fronteira** no alto do mapa da campanha v6 (atlas: `WorldMap_05`, peça `ilha_fronteira`, fora do repo; mapa de
390 × 864), trancada até as 6 medalhas, que leva à aba nova **Lutar · Fronteira** (a Liga: as regras, os 6 líderes com os Megas, a última
tentativa refeita do registro com a vida no fim de cada luta, o título e o botão). A luta em tela cheia com "Liga dos Líderes · luta k de 6"
(o rival muda a cada luta, sem a escolha da carta); o Resultado com as 6 lutas (vida no fim de cada uma) e o título; a medalha de ouro
em **Medalhas**; a conclusão "Campeão!".

**Conferência (sem calibração)** (`web/app/test/conferir_liga.mjs` → `artifacts_campanha/liga/conferencia.json`; motor web, escala v6,
V21D, limite do desafiado; pet de referência = as 8 formas no Mega × 4 espécies com o treino típico do Mega (40), sem item; sementes de
validação 4101…4505, 20 partidas por semente, espécie e forma):

- **Cada luta sozinha é vencível**, com os dois fatores (melhor forma, pet inteiro): fator 1,6: 1. Gazimon (WarGreymon): furioso 1,0000; 2. Guardromon (Seraphimon): duelista 1,0000; 3. Youkomon (MegaGargomon): duelista 1,0000; 4. Myotismon (Vikemon): duelista 1,0000; 5. MarinBullmon (Rosemon): furioso 1,0000; 6. Piedmon (Imperialdramon Dragon Mode): furioso 1,0000. Fator 1: 1. Gazimon: duelista 1,0000; 2. Guardromon: duelista 1,0000; 3. Youkomon: duelista 1,0000; 4. Myotismon: duelista 1,0000; 5. MarinBullmon: furioso 1,0000; 6. Piedmon: duelista 1,0000.
- **A Liga inteira (títulos por forma):** fator 1,6 (desenho): 0 nas 8 formas. Fator 1,4: melhor vigia 0,0025. Fator
  1,2: melhor vigia 0,0975. **Fator 1 (adotado): furioso 0,7850, vigia 0,4275, duelista 0,4075, espelho 0,2075, sentinela 0,0600, emboscador 0,0600, titã 0,0050, muralha 0,0000.** Com a forma certa a Liga é completável; a muralha
  não passa do MegaGargomon (sentinela).
- O pet do teste ponta a ponta (`e2e/save_liga.json`, um Valkyrimon, emboscador, de vida de verdade) vence a Liga com a semente do botão.

**Ficou de fora (4b, 4c):** as instalações (Torre de Batalha, Palácio, Fábrica, Salão), os recordes e o evento `f`.

## 8. O que a parte 4b implementou (2026-09-30): a Torre de Batalha e o Palácio

Só `web/app/`, só pets v6; a pesquisa em Python não muda (`docs/REGISTRO_DESVIOS.md`, 2026-09-30). Sem rodada de equilíbrio.

**As instalações** (`web/app/motor/instalacoes.ts`, `INSTALACOES`):

| instalação | id | regra | recorde |
|---|---|---|---|
| Torre de Batalha | `torre_batalha` | Megas sorteados, um depois do outro, sem cura (a vida e o guts do pet passam); perdeu, acabou; chips valem, cartas não | a maior sequência de vitórias |
| Palácio | `palacio` | a mesma sequência; o pet decide sozinho: travas, vetos e chips de regra não valem (chips de stat valem) | a maior sequência |

- **Os rivais:** em cada luta, uma das 8 formas adultas no Mega numa das 4 espécies, sorteadas de uma rng própria da luta
  (`hashSemente("fronteira-rival", s, k)`, `formaRivalInstalacao`), com a técnica da linha, a passiva da forma, o caráter canônico e a lista
  canônica V21D; ε dos bots canônicos. E = vida do Mega na escala dos pets v6 (23000) × `FATOR_INSTALACAO` = 1, o mesmo da Liga, sem
  calibração.
- **A sequência:** `arenas.jogarSequencia` (a série da Cidadela e da Liga com o rival dado na hora; `jogarSerie` passa por ela e dá as mesmas
  lutas): cada rival começa inteiro, o pet leva a vida e o guts; para na primeira luta que não for vitória. O limite de turnos é do desafiado,
  o rival. Teto de 100 lutas por tentativa (a tentativa é um evento só e precisa acabar); na conferência a maior sequência foi 19.
- **O Palácio:** `GambitsPet.listaPalacio` = a lista do Lago (`listaSozinho`: sem travas, com as vetadas de volta, ordenada pela nota) menos
  as regras que só estão no pet por um chip de regra. A regra de chip que o pet já tinha antes do chip fica (como fica ao desequipar).
- **Entrada:** depois do título do Tamer. O motor não lê o Tamer: o app grava no registro do pet o evento **`f`** `{campeao: true}` (um por
  pet, com as 6 medalhas conhecidas; `Motor.abrirFronteira`), como o `u` das medalhas. O In-Training não entra.

**Registro e replay (seção 4):** a tentativa é um evento `l` de sempre, `{r: id da instalação, s}`. A semente sai do registro do pet:
`s = sementeTentativa(semente do pet, instalação, número da tentativa dele ali)`; o motor recusa outra semente ao lutar e falha no replay
(ninguém escolhe os rivais). O `f` do desenho virou "a Fronteira abriu" (a regra da tentativa sai do rival, como na Liga). `Motor.instalacoes`
(tentativas, recorde, última) entra na assinatura só depois do `f`. O **recorde** vai ao Tamer como `["recorde", {inst, valor, quando, pet,
forma, tick}]` (registro versão 4, lê 1 a 3): só depois do título, só quando passa o recorde do Tamer naquela instalação
(`conferirRecordes`, a cada mudança do pet). Nada das instalações dá item, treino ou stat; as lutas fazem o que toda luta faz (o pet aprende
regras, conta lutas e vitórias, pode se machucar na derrota).

**Telas:** em Lutar · Fronteira, depois da Liga, as duas instalações (a regra em uma frase, o recorde do Tamer, as tentativas do pet e
"Tentar"; trancadas até o título); a luta com "Torre de Batalha · vitória N", o rival (arquétipo e brasão), as vitórias até ali e a vida
com que o pet começou; no Palácio o aviso das travas; o Resultado com as vitórias seguidas, as lutas (vida no fim de cada uma) e o recorde
novo; os recordes em **Medalhas**.

**Conferência (sem calibração)** (`web/app/test/conferir_instalacoes.mjs` → `artifacts_campanha/fronteira/conferencia.json`; motor web,
escala v6, V21D, limite do desafiado; o Mega de referência de cada forma × 4 espécies com o treino típico (40), sem item; sementes
4101…4505, 20 tentativas por semente, espécie e forma):

| forma | Torre: vence a 1ª | média | máx | Palácio: vence a 1ª | média | máx |
|---|---|---|---|---|---|---|
| furioso | 1,0000 | 7,98 | 15 | 1,0000 | 7,99 | 16 |
| duelista | 0,9750 | 5,52 | 11 | 0,9600 | 5,62 | 11 |
| espelho | 0,9025 | 3,55 | 7 | 0,8875 | 3,61 | 9 |
| emboscador | 0,8625 | 3,41 | 16 | 0,8350 | 3,50 | 16 |
| vigia | 0,8000 | 3,43 | 11 | 0,7950 | 3,24 | 11 |
| sentinela | 0,7750 | 3,57 | 14 | 0,7600 | 3,41 | 19 |
| titã | 0,7725 | 2,35 | 7 | 0,7625 | 2,38 | 7 |
| muralha | 0,6475 | 1,45 | 7 | 0,5775 | 1,48 | 9 |

- As duas são jogáveis: a melhor forma vence a primeira luta sempre, e nenhuma tentativa chegou perto do teto. Com a lista canônica (sem
  trava, veto nem chip) o Palácio do pet de referência é a Torre; as diferenças vêm só das sementes.
- O pet do teste ponta a ponta (Valkyrimon, emboscador, treino 40) vence a primeira luta nas 50 primeiras tentativas; média 7,64 na Torre e
  8,04 no Palácio. No e2e a primeira tentativa dá 7 vitórias na Torre e 9 no Palácio.

**Ficou de fora (4c, seção 9):** a Fábrica e o Salão. O tempo do jogo corria durante a animação (uma lesão da derrota que fechava uma
sequência longa matava o pet antes do Resultado na velocidade de teste); corrigido na interface: o relógio para durante a luta no palco e
com o Resultado aberto (Liga incluída).

## 9. O que a parte 4c implementou (2026-09-30): a Fábrica e o Salão

Só `web/app/`, só pets v6 em diante (v6 e v7, os da voz própria, que são v6 + voz; a Fábrica nem usa pet; o Salão mistura guardados v6 e v7); a pesquisa em Python não muda (`docs/REGISTRO_DESVIOS.md`, 2026-09-30). Sem rodada de
equilíbrio: fator 1 nas duas, como na Liga e nas outras instalações.

| instalação | módulo | regra | recorde |
|---|---|---|---|
| Fábrica | `web/app/motor/fabrica.ts` | o jogador não usa o pet: aluga 1 de 3 Megas sorteados e luta séries de 3 lutas sem cura; ao vencer, pode trocar o alugado pelo rival derrotado; perdeu, acabou | a maior sequência de séries vencidas |
| Salão | `web/app/motor/salao.ts` | um pet de cada nível (Rookie, Champion, Ultimate, Mega), entre o ativo e os guardados, cada um contra um rival sorteado do mesmo nível, na ordem; perdeu, acabou | quantos níveis venceu seguidos (até 4) |

**A Fábrica:**
- **Os alugados:** a cada tentativa, 3 formas adultas **distintas** (arquétipos diferentes) no Mega, cada uma numa espécie sorteada, de
  `hashSemente("fabrica-aluguel", s)`, com `s = sementeFabrica(n) = hashSemente("fronteira", "fabrica", n)` e `n` = o número da tentativa
  no registro do Tamer. Técnica da linha, passiva da forma, caráter canônico, lista canônica V21D, ε dos bots canônicos, **sem treino e sem
  itens**; E = vida do Mega na escala dos pets v6 (23000) × `FATOR_FABRICA` = 1.
- **Os rivais:** a luta k (0 = a primeira) é contra uma das 8 formas numa das 4 espécies, de `hashSemente("fabrica-rival", s, k)`, com a
  mesma montagem; a semente da luta é `hashSemente("fabrica-luta", s, k)`.
- **A série:** 3 lutas; dentro dela o alugado leva a vida e o guts de uma luta para a outra e cada rival começa inteiro; a série seguinte
  começa com o alugado inteiro. O limite de turnos é do desafiado, o rival. A primeira luta que não for vitória encerra a tentativa.
- **A troca:** depois de cada vitória (uma vez), o jogador pode trocar o alugado pelo rival que acabou de derrotar. O novo alugado entra com a
  **mesma fração da vida** e o mesmo guts (até o máximo dele) com que o anterior terminou a luta: **a troca não cura** (interpretação
  registrada; a variante "entra inteiro" foi medida e não adotada, abaixo).
- **Registro e replay:** nenhum pet luta, então a tentativa vai **só para o registro do Tamer** (versão 5): `["fabrica", {n, s, alugado,
  quando}]` (o começo, com a escolha), `["fabrica_luta", {n, k, s, quando}]` (cada luta, com a semente) e `["fabrica_troca", {n, k,
  quando}]`. O replay do Tamer joga as lutas de novo (`TentativaFabrica`) e confere a semente da tentativa, a de cada luta, a ordem, a troca
  só depois de vitória e uma tentativa por vez. A escala vale sempre ali (`perfilDe(..., comEscala)`): o replay não depende da chave do app.
  O recorde sai das tentativas (`Tamer.recordeFabrica`).

**O Salão:**
- **O rival:** o bot canônico do nível, sorteado de `hashSemente("salao-rival", s, estágio)`: a espécie e, pelo nível, o ramo (Rookie, com a
  semente de 3 regras da web), a linha (Champion, lista do adolescente) ou a forma adulta (Ultimate e Mega, lista canônica V21D, técnica e
  passiva), com o caráter canônico (os bots de referência das metas de estágio). E = vida do nível na escala dos pets v6 × `FATOR_SALAO` = 1.
- **O pet:** como na Liga e nas outras instalações (treino absoluto na escala, a lista dele, chips valem, cartas não); limite do rival.
- **Registro e replay:** a luta de cada pet é um evento `l` do registro **dele**, `{r: "salao", s}`, com `s = sementeSalao(semente do pet,
  número da luta dele no Salão)`; o motor confere a semente, a entrada (o título, evento `f`) e a carta, ao lutar e no replay. `Motor.salao`
  (tentativas, vitórias) entra na assinatura só depois da primeira luta ali. O Tamer grava a tentativa, `["salao", {n, quando, lutas: [{est,
  pet, forma, k, s, tick, venceu}]}]`, e confere a ordem dos níveis, a semente de cada luta pela conta do pet, um pet por nível, e que a
  tentativa só para numa derrota. O recorde sai das tentativas (`Tamer.recordeSalao`).
- **Os guardados:** um guardado escolhido recebe no registro dele, na hora parada em que está, o que o ativo receberia (o `u` das medalhas e o
  `f`, `tamer.sincronizarPet`) e a luta; ele continua guardado. O app (`src/fronteira.ts`) joga a tentativa antes em cópias e só então grava,
  pet por pet e por fim no Tamer; se a gravação der outro resultado, falha alto.

**Telas:** em Lutar · Fronteira, depois da Torre de Batalha e do Palácio, a **Fábrica** (a regra, o recorde do Tamer, "Tentar"; a escolha
entre os 3 alugados com o Digimon, o arquétipo, o nível e o brasão; a tentativa em andamento com o alugado e a vida, a série e a luta, a
última luta e, depois de cada vitória, a oferta de troca; as lutas da tentativa) e o **Salão** (a regra, o recorde, o pet de cada nível numa
lista com o ativo e os guardados, o aviso de qual nível falta, "Tentar" e a última tentativa). As lutas das duas **não são animadas**: o
resultado aparece no próprio card (a luta do Salão fica no registro do pet e pode ser revista no Diário). Os quatro recordes em **Medalhas**.

**Conferência (sem calibração)** (`web/app/test/conferir_fabrica_salao.mjs` → `artifacts_campanha/fronteira/conferencia_4c.json`; motor web,
escala v6, V21D, limite do desafiado):

- **Fábrica** (as 2000 primeiras tentativas do jogo): o jogador que aluga o de melhor arquétipo (a ordem da conferência da 4b) vence a 1ª
  luta em 0,4420 das tentativas e **vence uma série em 0,0180** (sem troca) ou **0,0190** (trocando quando o rival derrotado é de arquétipo
  melhor); máximo 2 séries. Por luta da série: 0,4443 / 0,2141 / 0,2010 (o dreno sem cura). Alugando sempre o primeiro: 0,3625 e 0,008. É
  jogável, mas difícil: são lutas de espelho (Megas iguais, sem treino) com o limite de turnos do rival e sem cura. Variantes **não adotadas**
  (relato para a rodada de equilíbrio): a troca entrando inteira, trocando por arquétipo melhor 0,028; trocando sempre, para curar, 0,054.
- **Salão** (o pet de referência de cada nível com o treino típico, as formas de referência × 4 espécies, sementes 4101…4505): Rookie 0,8950
  (sereno 0,79, arisco 1,00), Champion 0,7600 (guardião 0,5625 a brigão 0,9925), Ultimate 0,8153 (muralha 0,5925 a furioso 1,00), Mega
  0,8309 (muralha 0,61 a furioso 1,00). As lutas são independentes: vencer os 4 com o time médio 0,4608, com as melhores formas 0,9925, com
  as piores 0,1606; **sem treino** cada nível fica em 0,35–0,38 e os 4 em 0,0187 (o treino decide). Os pets do e2e (50 primeiras lutas de
  cada um): Patamon 0,86, Growlmon 0,76, MegaSeadramon 1,00, Valkyrimon 1,00.

## 10. A Fronteira completa

| parte | o que | onde vive | registro |
|---|---|---|---|
| 4a | a Liga dos Líderes (6 líderes com Megas, sem cura), o título, a medalha de ouro, a conclusão da jornada | `motor/liga.ts` | pet: `l` `{r: "liga"}`; Tamer: `campeao` |
| 4b | Torre de Batalha e Palácio (Megas sorteados até perder; no Palácio o pet decide sozinho) | `motor/instalacoes.ts` | pet: `f` e `l` `{r: "torre_batalha"}` ou `{r: "palacio"}`; Tamer: `recorde` |
| 4c | Fábrica (alugados, séries de 3, troca) e Salão (um pet por nível) | `motor/fabrica.ts`, `motor/salao.ts` | Fábrica: só o Tamer (`fabrica`, `fabrica_luta`, `fabrica_troca`); Salão: pet `l` `{r: "salao"}` e Tamer `salao` |

- **Entrada:** a Liga com as 6 medalhas (evento `u` do pet); as quatro instalações depois do título do Tamer (evento `f` do pet; a Fábrica
  confere o título no próprio registro do Tamer).
- **Nada da Fronteira deixa o pet mais forte fora dela:** nenhuma dá item, treino ou stat; as lutas do pet fazem o que toda luta faz (aprender
  regras, contar lutas e vitórias, lesão na derrota). A Fábrica não toca pet nenhum.
- **Força:** fator 1 em tudo (o Mega, ou o nível, na escala dos pets v6), sem calibração; as conferências (`artifacts_campanha/liga/`,
  `fronteira/conferencia.json` e `fronteira/conferencia_4c.json`) só mostram que é jogável. A decisão dos fatores fica para a rodada de
  equilíbrio.
- **Registro do Tamer:** versão 5 (lê 1 a 4). Os recordes: `recorde` (Torre, Palácio) e os tirados das tentativas (Fábrica, Salão).
- **Aberto:** a Fábrica é difícil com fator 1 (acima);
  as lutas da Fábrica e do Salão não têm animação no palco.
