# O jogo web: evolução, medalhas, arenas, Fronteira, escala, a versão web e os assets

Seções movidas inteiras do CLAUDE.md da raiz na etapa 1 da rodada de saúde (`docs/TAREFA_V2_SAUDE.md`, 2026-10-13). As regras do jogo
web que valem hoje estão em `web/app/CLAUDE.md`; a regra dos assets da Bandai continua resumida no `CLAUDE.md` da raiz.

> **Nota (2026-10-24):** a frase acima e a seção dos assets abaixo estão desatualizadas. A seção "Assets da Bandai" saiu do
> `CLAUDE.md` em 2026-10-13 (rodada de saúde), e a regra de uso pessoal, de não publicar e do repositório privado foi retirada pelo
> Matheus em 2026-10-22 e 2026-10-24 (relatado pelo Gerente). Vale a regra de procedência de `docs/UI_GUIDELINES.md`, seção 5.1. O
> repositório já é público (`.github/workflows/verificar-pr.yml`). O texto abaixo fica como registro.

## Evolução canônica no jogo (2026-09-29, `docs/DESIGN_EVOLUCAO_CANONICA.md`)

Pedido do Matheus ("tem que seguir o cânone"), só no jogo web; o Python da pesquisa segue com 4 estágios.
- **Pets v5** (`VERSAO_PET = 5`, ovos novos e filhos da herança): Champion → Ultimate → Mega. O Mega é um estágio próprio
  (`"mega"`): a forma adulta, a passiva e o caráter vêm do Ultimate; vida e guts ×1,15, E 3000 na campanha, treino com teto 16
  no estágio e 40 na vida. Ultimate → Mega pede 24 h (48 h no clássico), 10 lutas com ≥ 80% de vitória e vínculo ≥ 0,4; a
  sombria nunca chega (regra explícita). Constantes em `CMG` (`baseDe` leva o Mega às tabelas do adulto); `Motor.requisitosMega()`.
- **Nomes no cânone para todos os pets:** as duas formas adultas da linha são o mesmo Ultimate (o arquétipo as distingue) e o
  Mega é o da cadeia (Greymon → MetalGreymon → WarGreymon); a sombria usa o Ultimate. Pets v1–v4 param no Ultimate; o motor
  deles não muda (`nomeFormaLegado` na assinatura dos gambits).
- **Campanha v5:** Cidadela com o Myotismon; Montanha Espiral (Mega) com Puppetmon, Machinedramon e o Piedmon (chefe). Os
  pets v1–v4 seguem na campanha de sempre. Fatores calibrados no motor web (`web/app/test/calibrar_mega.mjs`,
  `artifacts_campanha/mega/`): validação nas metas de sempre.
- **Limiar do vínculo 0,4** (baixado de 0,7 pelo Matheus): com 0,7 os donos simulados coerentes não chegavam ao Mega e o
  aleatório chegava; com 0,4 o atencioso chega em 3 de 6 vidas, o aleatório em 5 de 6 (`artifacts_campanha/mega/limiar_vinculo.json`).
  O defeito do vínculo continua (pendência abaixo).

## Medalhas do Tamer no jogo, parte 1 (2026-09-29, `docs/DESIGN_MEDALHAS_ARENAS.md`)

Só no jogo web; a pesquisa em Python não tem Tamer (`docs/REGISTRO_DESVIOS.md`, 2026-09-29).
- **Tamer:** o jogador. Registro próprio (event sourcing) em `…-tamer` (`src/tamer.ts`): eventos `medalha` (id, contador,
  hora de parede, pet, forma, tick). Medalha na primeira vitória contra o líder, com qualquer pet v6; é do Tamer e sobrevive ao pet.
- **Trava (pets v6, `VERSAO_PET = 6`):** Rookie → Champion pede 1 medalha, Champion → Ultimate 3, Ultimate → Mega 5 (`CMD`), além
  dos requisitos de sempre. O motor nunca lê o Tamer: o app grava no registro do pet o evento `u` ("o Tamer tem N medalhas",
  `Motor.liberar`), e o pet pronto evolui nesse tick. Pet guardado recebe o `u` ao voltar a ser o ativo. Assinatura dos v1–v5 igual.
- **Medalhas** (`motor/medalhas.ts`, tabela única): uma por arena, do líder dela (parte 2, seção abaixo). Na parte 1 a 3ª e a 5ª
  tinham fonte provisória (Devidramon e Tortomon, na Torre de pedra) até a Floresta e o Lago existirem.
- **Tempo dos estágios nos v6:** conta desde a evolução anterior (`Motor.tickLimiteEstagio`), para um Rookie que esperou a
  medalha não ganhar um Champion curto; nos v1–v5 continua desde o nascimento.
- **Saves:** na primeira abertura os pets v1–v5 (ativo e guardados) são apagados com aviso e o jogo começa num ovo novo (decisão do
  Matheus). Os Cenários seguem com pets v5 (sem Tamer). Telas: Lutar · Medalhas, requisito na Evolução, líder na Campanha.

## Arenas com líderes, medalhas parte 2 (2026-09-30, `docs/DESIGN_MEDALHAS_ARENAS.md`, seção 12)

Só no jogo web e só pets v6; a pesquisa não tem arenas (`docs/REGISTRO_DESVIOS.md`, 2026-09-30).
- **Seis arenas** (`motor/arenas.ts`, `ARENAS`; campanha v6 em `bots.LUGARES_V6`/`CAMPANHA_V6`, na ordem do nível): Campina (Gazimon,
  sem regra), Torre de pedra (Guardromon com o contra-golpe: paciência), **Floresta** (Youkomon, muda de padrão no turno 10: leitura),
  Cidadela (Myotismon, três lutas seguidas sem cura: resistência), **Lago** (MarinBullmon; as travas e vetos do dono não valem:
  vínculo) e Montanha Espiral (Piedmon, chefe). Os NPCs de antes seguem como desafiantes, com as mesmas chaves. A 3ª medalha vem da
  Floresta e a 5ª do Lago (fim das provisórias).
- **Replay:** a regra depende só do rival e da versão do pet; o evento `l` continua `{r, s}` (a série da Cidadela é um evento só, com
  sementes derivadas). `Motor.montarLuta`/`lutadores` montam a luta para o motor e para a tela; `Motor.lugarDe(k)` dá o lugar do NPC
  na campanha do pet (os índices mudam da v5 para a v6). Pets v1–v5 e gabaritos iguais.
- **Calibração** (`web/app/test/calibrar_arenas.mjs`, `artifacts_campanha/arenas/`, na escala dos pets v6, seção abaixo; sementes de
  validação, com a regra do limite do desafiado): os seis líderes nas metas novas (sem treino ≤ 0,05; com o treino típico ≥ 0,80;
  nenhuma forma < 0,5). Sem treino 0,0006–0,0213, com treino 0,8125–0,9063, pior forma 0,535 (sentinela na Cidadela). Fatores só na luta de arena: Gazimon 1,3,
  Guardromon 1,6, Myotismon 0,9 (série), Piedmon 1,6; Youkomon e MarinBullmon 1,5. Na Torre o Guardromon ganhou lista própria de arena
  (`GAMBITS_ARENA.torre`: contra quem atira com frequência ele avança, no lugar do contra-golpe); com a de antes nenhum fator passava.
- **Telas:** cartão da arena (líder, regra, medalha), mapa de seis ilhas (atlas: `WorldMap_04` Floresta e `WorldMap_02` Lago, fora do
  repo), "luta k de 3" na Cidadela, aviso do Lago na luta e no Resultado, Medalhas com a regra de cada arena.
- **Correção do vigia:** nos pets v6 as duas regras novas do vigia V21D voltam como candidatas de troca (`candidatasDoVigia`).
- **Saves v6:** descarte único versão 3 (arenas), 4 (escala v6) e 5 (limite do desafiado): os v6 de antes saem, com o mesmo aviso.
- **Limite de turnos (decisão do Matheus, 2026-09-30):** nas lutas dos pets v6 (campanha, arenas, arena contra bots) a luta que chega ao
  limite sem nocaute é de quem foi desafiado, o rival (o pet sempre desafia); na Cidadela ela quebra a série. `combate.fimV2`/`jogarV2`
  com o desafiado (na Liga da Fronteira, o líder), `desafiadoDaVersao`; nada novo no registro. Pets v1–v5, cenários e o Python: a fração
  de vida, como sempre.

## Itens do Tamer, medalhas parte 3 (2026-09-30, `docs/DESIGN_MEDALHAS_ARENAS.md`, seção 13) — SEM EQUILÍBRIO

Só no jogo web e só pets v6; a pesquisa não tem itens (`docs/REGISTRO_DESVIOS.md`, 2026-09-30). **Sem equilíbrio** (decisão do Matheus,
2026-09-30): ainda entram outras mecânicas no combate, e o equilíbrio será uma rodada só, depois; os números são os PROPOSTOS da seção 13 e
os gates G-I1–G-I4 (13.7) ficam para essa rodada (`web/app/test/medir_itens.mjs` pronto, não rodado; sem artefato).
- **Catálogo** (`motor/itens.ts`, `CIT` em `constantes.ts`): Chip de Força e Chip de Guarda (stat: +2 pontos de treino, só no espaço que
  falta no teto do estágio e da vida, todos juntos ≤ 25% do treino típico); Chip Recuo e Chip Oportunista (regra, do Champion), Chip
  Perseguidor e Chip Aparo (regra, do Ultimate); Carta de Fôlego (+20 guts), de Cura (20% da vida na primeira vez abaixo de 30%) e de Foco
  (ε 0).
- **De onde:** o líder dá o chip da arena com a medalha (um Tamer com medalhas de antes recebe na abertura); a revanche vencida, com um
  pet do nível da arena, dá a carta da arena, uma por líder a cada 24 h do relógio do pet. Chips por pet pelas medalhas: 1/2/3 com 1/3/5;
  uma carta por luta.
- **Registro:** inventário no Tamer (registro versão 2, lê a 1: `item`, `carta_usada`); no pet, `i` (equipar/desequipar) e `k` (a carta,
  logo antes da luta `l`; outro evento depois dela falha alto). O motor não lê o Tamer; o app confere o inventário. A assinatura dos v6 só
  muda com item; v1–v5, gabaritos, paridade V21D e os artefatos de validação da parte 2 saem iguais. Descarte único não subiu.
- **Telas:** Crescer · Itens; a carta antes da luta (Campanha e Arena); o item novo e a carta usada no Resultado; o item de cada medalha
  em Medalhas; a regra de chip marcada nas regras de combate (não se veta).

## Fronteira de Batalha, parte 4a: a Liga dos Líderes e o fim do jogo (2026-09-30, `docs/DESIGN_FRONTEIRA.md`, seção 7) — SEM EQUILÍBRIO

Só no jogo web e só pets v6; a pesquisa não tem Liga (`docs/REGISTRO_DESVIOS.md`, 2026-09-30). As instalações: 4b e 4c nas seções seguintes
(a Fronteira completa: `docs/DESIGN_FRONTEIRA.md`, seção 10).
- **A Liga** (`motor/liga.ts`, `LIGA`): com as 6 medalhas (as que o pet conhece pelo `u`), os 6 líderes em sequência, cada um com um Mega de
  arquétipo diferente e lista canônica V21D: Gazimon/WarGreymon (furioso), Guardromon/Seraphimon (espelho), Youkomon/MegaGargomon
  (sentinela), Myotismon/Vikemon (titã), MarinBullmon/Rosemon (muralha), Piedmon/Imperialdramon Dragon Mode (duelista). Sem cura
  (`arenas.jogarSerie`, a série da Cidadela generalizada), chips valem, **cartas não** (o motor recusa; `k` antes da luta da Liga falha no
  replay), limite de turnos do líder, perder encerra a tentativa.
- **Fator 1 (desvio do desenho, que pedia o do Piedmon, 1,6):** com 1,6 cada luta sozinha é vencível, mas nenhuma forma vence as 6 seguidas
  (0 títulos nas 8); com 1 o furioso de referência (treino 40) vence 0,785, e 7 das 8 formas vencem às vezes
  (`test/conferir_liga.mjs` → `artifacts_campanha/liga/conferencia.json`). Para o Matheus decidir na rodada de equilíbrio.
- **Registro:** a tentativa é um evento `l` do pet, `{r: "liga", s}` (sem o evento `f`); `Motor.liga = {tentativas, titulos}` entra na
  assinatura só depois da primeira. O título vai ao Tamer como `campeao` (registro versão 3; um por pet; o primeiro é o do Tamer). A
  conclusão da jornada dos v6 vem da Liga (`jornada.concluiuJornada`); nos v1–v5, o chefe como antes.
- **Telas:** ilha da Fronteira no alto do mapa v6 (atlas `WorldMap_05`, fora do repo; mapa 390 × 864), aba **Lutar · Fronteira** (regras,
  os 6 líderes com os Megas, a última tentativa com a vida no fim de cada luta, o título), "Liga dos Líderes · luta k de 6" na luta, as 6
  lutas e o título no Resultado, a medalha de ouro em Medalhas, a conclusão "Campeão!". Testes: `test/liga.test.ts`, e2e com
  `e2e/save_liga.json` (`e2e/gerar_save_liga.mjs`).

## Fronteira de Batalha, parte 4b: a Torre de Batalha e o Palácio (2026-09-30, `docs/DESIGN_FRONTEIRA.md`, seção 8) — SEM EQUILÍBRIO

Só no jogo web e só pets v6; a pesquisa não tem instalações (`docs/REGISTRO_DESVIOS.md`, 2026-09-30). A Fábrica e o Salão (4c): seção seguinte.
- **As instalações** (`motor/instalacoes.ts`, `INSTALACOES`), abertas depois do título da Liga: a **Torre de Batalha** (Megas sorteados, sem
  cura, perdeu acabou; chips valem, cartas não) e o **Palácio** (a mesma sequência; travas, vetos e chips de regra não valem:
  `GambitsPet.listaPalacio`, a lista do Lago sem as regras que só estão no pet por um chip; chips de stat valem). Limite de turnos do rival;
  teto de 100 lutas por tentativa (nunca alcançado na conferência).
- **Rivais:** as 8 formas adultas no Mega × 4 espécies, sorteadas por luta de `hashSemente("fronteira-rival", s, k)`, com técnica,
  passiva, caráter e lista canônica V21D; E = vida do Mega na escala v6 × 1 (o fator da Liga, sem calibração).
- **Registro:** o pet conhece o título pelo evento **`f`** `{campeao: true}` (o app grava, como o `u`; um por pet). A tentativa é um `l`
  `{r: "torre_batalha" | "palacio", s}`, com `s = sementeTentativa(semente do pet, instalação, nº da tentativa dele ali)`: o motor confere a
  semente ao lutar e no replay. `Motor.instalacoes` (tentativas, recorde, última) entra na assinatura só depois do `f`. O recorde vai ao
  Tamer como **`recorde`** `{inst, valor, quando, pet, forma, tick}` (registro versão 4; só depois do título e só quando passa o anterior).
  `arenas.jogarSequencia` generaliza a série (a `jogarSerie` passa por ela, as mesmas lutas). Nada das instalações dá item, treino ou stat.
- **Conferência** (`test/conferir_instalacoes.mjs` → `artifacts_campanha/fronteira/conferencia.json`; Mega de referência, treino 40, sementes
  4101…4505): jogáveis. Vence a 1ª luta: furioso 1,00, duelista 0,97, espelho 0,90, emboscador 0,86, vigia 0,80, sentinela 0,78, titã 0,77,
  muralha 0,65 (Torre); média de vitórias de 1,5 (muralha) a 8,0 (furioso), máximo 16 (Palácio: 19). O pet do e2e (Valkyrimon) vence a 1ª
  em todas as 50 tentativas, média 7,6 (Torre) e 8,0 (Palácio). Com a lista canônica o Palácio é a Torre (outras sementes).
- **Telas:** as duas instalações em Lutar · Fronteira (regra, recorde do Tamer, tentativas do pet, "Tentar"), "Torre de Batalha · vitória N"
  na luta com a vida com que o pet começou, o Resultado (vitórias seguidas, as lutas, o recorde novo), os recordes em Medalhas. Testes:
  `test/instalacoes.test.ts`, e2e com `e2e/save_liga.json` e um Tamer campeão.

## Fronteira de Batalha, parte 4c: a Fábrica e o Salão (2026-09-30, `docs/DESIGN_FRONTEIRA.md`, seções 9 e 10) — SEM EQUILÍBRIO

Só no jogo web e só pets v6 em diante (v6, v7 com a voz própria e v8 com a confiança do M1; a Fábrica nem usa pet; o Salão mistura guardados v6 em diante); a pesquisa não tem instalações (`docs/REGISTRO_DESVIOS.md`, 2026-09-30). Com ela a
Fronteira está completa. Abrem depois do título do Tamer; fator 1 nas duas, sem calibração.
- **Fábrica** (`motor/fabrica.ts`, `TentativaFabrica`): 3 alugados (Megas de arquétipos distintos, espécies sorteadas, lista canônica V21D,
  sem treino e sem itens) sorteados de `sementeFabrica(n)` (n = o número da tentativa no registro do Tamer); o jogador escolhe 1 e luta
  séries de 3 contra Megas sorteados, sem cura dentro da série (a série seguinte começa inteira), limite do rival, perdeu acabou; depois de
  cada vitória pode trocar o alugado pelo rival derrotado, que entra com a mesma fração da vida (**a troca não cura**). Recorde: as séries
  vencidas. **As lutas vão só para o registro do Tamer** (versão 5: `fabrica`, `fabrica_luta`, `fabrica_troca`; o replay joga as lutas de
  novo e confere as sementes); a escala vale sempre ali (`perfilDe(..., comEscala)`), sem depender da chave do app.
- **Salão** (`motor/salao.ts`): um pet de cada nível (Rookie a Mega) entre o ativo e os guardados v6, cada um contra o bot canônico sorteado
  do nível (escala v6, fator 1), na ordem; perdeu acabou. A luta é um `l` `{r: "salao", s}` do registro de cada pet, com a semente do
  registro dele (`sementeSalao`), conferida pelo motor; `Motor.salao` entra na assinatura só depois da primeira. O guardado recebe `u`, `f` e
  a luta na hora parada dele e continua guardado (`src/fronteira.ts`: joga em cópias e só então grava; `pets.atualizarGuardado`). O Tamer
  grava a tentativa (`salao`: pets, sementes, quem venceu); o recorde (níveis seguidos, até 4) sai das tentativas.
- **Conferência** (`test/conferir_fabrica_salao.mjs` → `artifacts_campanha/fronteira/conferencia_4c.json`): jogáveis. Fábrica (2000
  tentativas do jogo): alugando o melhor arquétipo, vence a 1ª luta 0,442 e uma série só em 0,018–0,019 (lutas de espelho sem cura e com o
  limite do rival; máximo 2 séries); a troca entrando inteira (não adotada) daria 0,028–0,054. Salão com o treino típico: Rookie 0,895,
  Champion 0,760, Ultimate 0,815, Mega 0,831; os 4 com o time médio 0,461 (sem treino 0,019).
- **Telas:** os dois cards em Lutar · Fronteira (a escolha dos alugados com Digimon, arquétipo e nível; a oferta de troca; o pet de cada
  nível e o aviso do que falta; o resultado no próprio card, sem animação), os quatro recordes em Medalhas. Testes:
  `test/fabrica_salao.test.ts`, e2e com `e2e/save_salao.json` (`e2e/gerar_save_salao.mjs`: Rookie, Champion e Ultimate guardados ao lado
  do Mega de `save_liga.json`).

## Escala dos pets v6 (2026-09-30, `CESC_V6`; `docs/DESIGN_MEDALHAS_ARENAS.md`, seção 12)

Decisão do Matheus: "o treino tem que decidir" contra cada líder e "o estágio tem que pesar". Só no jogo web e só nas lutas de escala dos
pets v6 (campanha e arenas; o pet pela versão, o NPC pelas regras V21D da luta); a `CESC`, os v1–v5 e a pesquisa não mudam
(`docs/REGISTRO_DESVIOS.md`, 2026-09-30).
- **Escala:** vida Rookie 200, Champion 700, Ultimate 2500, Mega 23000 (bebê 50) e β 0,045 por ponto de treino (era 600/1500/3000 e
  0,03). `web/app/test/calibrar_escala_v6.mjs` → `artifacts_campanha/escala_v6/`: β = o menor da grade com os líderes viáveis com folga
  0,01 (a vida cancela nas lutas de líder); vidas = as menores razões que passam as metas de estágio (margem 0,005).
- **Metas de estágio** (baixo com o treino típico × cima sem treino; bots canônicos, 4 espécies de cada lado), validação com a regra do
  limite do desafiado (o de cima): vizinhos ≤ 0,10 em pontos (Rookie × Champion 0,0008, Champion × Ultimate 0,0108, Ultimate × Mega
  0,0041) e **dois estágios = 0,00** (Rookie × Ultimate e Champion × Mega: nenhuma vitória). Pelo limite da fração de vida os dois
  estágios não fechavam (0,0372 e 0,0509: vitórias por estilo no limite, que a escala não tira). A escala foi escolhida antes da regra e
  não foi recalibrada.
- **DW1 como âncora** (×2, ×2,5; Mega ×2): a v6 tem ×3,5, ×3,57, ×9,2; o afastamento vem sobretudo do peso do treino (razão = (1 + β ×
  treino típico) ÷ razão de E pedida: 1,36 × 2,57; 1,99 × 1,80; 2,62 × 3,51).
- **Desafiantes v6** (`calibrar_desafiantes_v6.mjs`, `CESC_V6.fatorNpc`, metas de sempre ≤ 0,30 / ≥ 0,80, com a regra do limite):
  Devidramon 1,1, Puppetmon 2,5, Machinedramon 2,2 passam; **Tortomon não fecha** com nenhum fator (1,5: sem treino 0,3087), a exceção
  da Sentinela.

## Versão web (`web/digilab.html`)

Porte em JavaScript com as mesmas regras e parâmetros de `config.py` (motor, instinto, bandit,
donos, arena). Usa outro gerador aleatório (mulberry32), então **não reproduz os artefatos
Python bit a bit**; não usar para resultado de pesquisa. Replay interno do log funciona e tem
botão de verificação. Arte é placeholder original, desenhada em código a partir de grades de
pixels no próprio arquivo. Se mudar um parâmetro em `config.py`, espelhe no objeto `C`/`CB`/`CD`/`CA` do HTML.

Publicado também como artifact privado em claude.ai (link com o usuário).

`web/digilab_sprites.html` (o jogo com sprites) tem **versão de pet** no save (`versao`): 1 = pets salvos
antes de 2026-09-25 (memória curta antiga, sem vínculo nem obediência, seguem iguais); 2 = pets novos,
com o mesmo pacote do Python de pesquisa: memória por espaços, temperamento, vínculo, obediência com
recusa e motivo, desejo com métricas (cumprimento, tempo com vontade) e condição do cuidado no combate
(vida e guts × 0,95 a 1,05 pela saúde na hora da luta). Constantes espelhadas em `CME`, `CVI`, `COB`,
`CTP`, `CDJ`, `CCOND`. Fora da web: caráter pelo desvio da política (`evolucao.py`), que mudaria a
evolução; desde 2026-09-25 os pets **v3** usam o caráter pelo desvio da política (32 sondas × 100 amostras); v1/v2 seguem pelos traços.

Aba **Cenários**: monta dois pets com donos simulados (dono, dias de vida, interações/dia,
semente). O pet A vira o pet do jogador (o anterior fica guardado para "Voltar") e o B vira o
rival fixo da arena. Mostra lado a lado estado, sinal de aprendizado, JSD da política média ao
prior do bandit e 100 lutas A × B. É ferramenta de inspeção do porte JS, **não** resultado de
pesquisa: uma semente, outro RNG, sem IC.

## Assets — importante

A pasta `D:\Trab\digilab\Assets` (fora deste repo) contém sprites da Bandai: Digimon UP (usados pela
versão web desde a TAREFA_INTERFACE_UP) e o atlas antigo do Digimon World (não é mais usado). É arte e personagens protegidos, **sem licença**. Regra revisada pelo Matheus em
2026-09-24:

- **Permitido**: usar esses sprites na versão web (`web/`) para uso pessoal e local, como
  protótipo de jogo.
- **Proibido**: usar no pacote `digilab/`, em `experiments/`, em `artifacts*/`, em figuras ou
  textos de publicação acadêmica, ou em qualquer build distribuído como produto. Não publicar
  a versão com sprites (artifact, site, repositório **público**). Revisado em 2026-09-24:
  `web/digilab_sprites.html` é versionado, mas o repositório GitHub (`matheusmmmp/digilab`)
  tem que continuar **privado**. Tornar o repo público exige tirar esse arquivo antes, inclusive
  do histórico. O atlas com os pixels da Bandai continua fora do repo.
- **Acesso remoto** (decisão do Matheus, 2026-09-24): pode abrir por túnel (Cloudflare) para
  testar de outros computadores, **só** com `servidor_local.py --remoto` — senha obrigatória
  (`DIGILAB_SENHA`, 12+ caracteres, só no ambiente), só as rotas do jogo (página, atlas, API de
  fala; o resto da pasta dá 404), API paga do Claude desligada salvo `--claude-remoto`. Sem
  `--remoto`, pedido vindo por túnel (cabeçalhos `Cf-Ray`/`X-Forwarded-For`) leva 403. O link é de
  uso pessoal: não compartilhar nem divulgar. Revisado no mesmo dia: o Matheus dispensou a senha
  (`--remoto --sem-senha`, só ele acessa); aí o link aleatório do túnel é a única proteção e as
  outras travas (rotas, Claude desligado) continuam. Túnel sempre para `http://127.0.0.1:<porta>`
  (com `localhost` o cloudflared tenta IPv6 e não acha o servidor).
- Manter a versão com placeholders originais funcionando: antes de publicar ou distribuir
  qualquer coisa, trocar por arte original ou licenciada.

Versão com sprites: `web/digilab_sprites.html` (versionado; repo privado), derivada de `digilab.html`, que
lê `D:\Trab\digilab\Assets\digilab_atlas_up.json` e `.png` (Digimon UP). O atlas e os scripts ficam fora
do repo: `Assets\gerar_atlas_up.py` (atlas, a partir de `Assets\catalogo_sprites_up.json` e da pasta
`Digimon Up Assets\Animacoes`) e `Assets\gerar_sprites_html.py` (não usar mais: a cópia é editada direto).
**Interface UP (2026-09-27/28, `docs/TAREFA_INTERFACE_UP.md`, `docs/UI_GUIDELINES.md`)**: tokens `--dl-*` e
componentes `dl-*`; navegação em 4 destinos (Pet, Crescer = Treinar + Aprendizado + Evolução, Lutar = Arena +
Campanha, Diário = Registro + Catálogo + Cenários; aba lembrada em `destino/aba`); na tela os nomes são os do
Digimon do mapa aprovado, as espécies são brasões (brasa Coragem, cirro Amizade, ferrugem Conhecimento, limo
Sinceridade) e os estágios são níveis (In-Training, Rookie, Champion, Ultimate/Mega); ids internos, log e save
não mudam. Páginas de conferência: `#palco-up` (sprites) e `#componentes-up` (componentes). Precisa de servidor local, porque o caminho é
relativo: `python -m http.server 8765 --directory D:/Trab/digilab` e abrir
`http://localhost:8765/v1/web/digilab_sprites.html`. A linha evolutiva segue o traço de combate
dominante no momento da evolução. Se o atlas não carregar, a página mostra um aviso em
vermelho e cai nos placeholders.

**Desde 2026-09-28 o jogo web é o app em `web/app/` (TAREFA_FRONT_TS, Etapa 6)**: mudança de jogo vai em
`web/app/motor/` (e nos gabaritos, se mudar a regra) e a tela em `web/app/src/`. O `digilab_sprites.html` ficou como
versão antiga (`?antigo=1`) e referência dos gabaritos; o texto abaixo descreve o jogo como era nele.

**De 2026-09-24 a 2026-09-28 `digilab_sprites.html` foi a versão em que o Matheus trabalhava** e era
editada direto; `digilab.html` ficou parado. Só a versão com sprites tem as abas **Evolução** e
**Catálogo**, que desde 2026-09-24 seguem a **árvore do combate V2.1** (substituiu as 5 linhas por
traço; chave do localStorage `digilab-web-v21-sprites`, pets da árvore antiga ficam para trás):
- **4 espécies** (brasa, cirro, ferrugem, limo), sorteadas pela semente; ovo por espécie. 15 formas
  por espécie (1 bebê, 2 crianças, 4 adolescentes, 8 adultos), **cada forma com sprite próprio**:
  60 Digimon diferentes. Mapa forma → Digimon UP (idle de cada um) em `Assets\catalogo_sprites_up.json`
  (fora do repo); `gerar_atlas_up.py` empacota o ciclo idle; o HTML lê os recortes do JSON.
- Transições com o cronograma de `docs/cronograma_interacoes.json` (durações pela metade): bebê
  3 h, criança 12 h, adolescente 18 h. **Bebê → criança**: o bebê chama em horário fixo (fome 30 min,
  higiene 60, carinho 45); atender ≥ 80% em até 15 min dá Sereno, senão Arisco. **Criança →
  adolescente**: caráter dominante → linha. **Adolescente → adulto**: sinal do eixo complementar +
  10 lutas de sparring na arena. Contadores zeram a cada evolução.
- **Caráter PROVISÓRIO, só na web** (a medida certa é da tarefa de personalidade): por eixo, média
  de (afinidade − linha de base) dos traços do eixo / 0,1, cortada em [−1, 1]; impetuoso = golpe e
  carga, paciente = bloqueio, atento = finta, resistente = agarrão. `BASE_CARATER` medida em 60 pets
  simulados (4 donos × 15 sementes, 16/dia) aos 900 e 1980 min. Checagem no console (sem artefato,
  não citar como resultado): donos diferentes produzem ramos e formas diferentes, e o replay bate.
- Donos simulados da web atendem os chamados do bebê (atencioso e incoerente sempre, relapso nas
  visitas, aleatório por acaso) e fazem o sparring do adolescente contra o bot aleatório.
- Árvore em SVG: ovo → bebê → 2 crianças → 4 adolescentes → 8 adultos, caminho destacado,
  tracejado = forma se evoluísse agora (com o porquê), requisito no título de cada nó.
- Aba **Catálogo**: as 15 formas da espécie com sprite, stats (renormalizados), vida/guts/regen,
  técnica e passiva.

Desde 2026-09-24 a versão com sprites também tem (porte JS, **não** reproduz os artefatos Python):
- **Combate V2.1** na aba Arena (espelho de `combate_v2/v21/`: perfil da forma, técnicas, passivas,
  `turno_execucao`, `oponente_vai_preparar`). Rivais: os bots clássicos da V2 (stats neutros) e os 8
  bots canônicos da bateria V2.1 (cada forma com uma espécie fixa). O combate V1 saiu da interface.
  Cada evolução semeia os gambits do pet (crianças: semente de 3 regras só da web; adolescente e
  adulto: bots canônicos da linha/forma) e a lista cabe na capacidade do estágio (3/5/8), só com as
  condições do estágio e a técnica da própria linha. Bebê luta ao acaso (multiplicador 0,4; exceção
  da web).
- **Gambits híbridos** (substituiu o editor livre, 2026-09-24): o PET aprende a própria lista. A linha
  evolutiva semeia; após cada luta contra bot, a nota de cada regra que disparou vai em direção ao
  saldo de dano dos turnos em que ela agiu (+ bônus pelo resultado); a lista se reordena pela nota;
  uma regra livre com nota < limiar é trocada por uma candidata do repertório (regras de todos os
  estilos). O DONO só trava (posição fixa) ou veta (pet não usa). Lutas (`l`: rival + semente) e
  intervenções (`g`) entram no registro; o replay reconstrói o aprendizado e separa pet × dono.
  Lutas contra pet de cenário e as 100 lutas dos Cenários não ensinam. Parâmetros no objeto `GA`.
  PROVISÓRIO e só na web: o Python ainda não tem isso (é a arena V2 da pesquisa).
- **Aba Campanha** (2026-09-25): mapa em SVG (Campina → Torre de pedra → Cidadela) com um lugar por NPC
  (aberto, trancado, vencido), o pet no próximo desafio e cartão com a lição, os stats e o histórico de
  tentativas (contado do registro). A luta acontece na própria aba: o palco da Arena (canvas, barras,
  narração) é movido para a aba visível.
- **Fala** sob a tela (clique mostra o motivo) e na narração da luta; mesma tabela de textos e mesma
  regra de honestidade do Python. Na web, a criança sem causa mostra ação + humor (vida) ou reação
  (luta), que são estado e não causa; no Python a criança sem causa mostra só a ação. Estágio da fala
  é o estágio da evolução (bebê, criança, adolescente, adulto).
- **Memória curta** no bandit de todos os pets (inclusive rivais de cenário); aba Aprendizado mostra
  o que ele lembra e as últimas decisões com o porquê. Pets salvos antes são reinterpretados pelo
  replay com a política nova (o registro é o mesmo; o comportamento muda).

**Migração para TypeScript (TAREFA_FRONT_TS, em andamento)**: o motor em TS fica em `web/app/motor/` (sem
DOM: lib ES sem "dom", teste `motor_sem_dom`; `index.ts` exporta tudo; `Motor.aplicarEvento` é o passo do
replay). App (Vite + Preact, Etapa 3): `web/app/src/` (um motor só, lido pelas telas via `useJogo()`; só
`mudarMotor()` altera e grava; save com a mesma chave e formato do HTML; save que não abre mostra erro e não é
regravado). `cd web/app && npm install`; `npm run dev` (http://localhost:5173, serve só o atlas de `Assets/`);
`npm run build` (sai em `web/dist/`, não versionado; o `servidor_local.py` serve em `/v1/web/dist/`, e no modo
remoto só o que fica dentro dessa pasta); `npm run tipos` (tsc estrito: motor sem DOM + app); `npm test`
(Vitest, ~1 min); `npm run e2e` (Etapa 5: build + Playwright no Chrome instalado, servidor local na porta 8799:
saves v1/v2/v3 em `e2e/saves.json` jogados pela interface, assinatura do app = `Motor.reproduzir` do HTML; checklist
da seção 14 do guia nas 9 abas em 360/390 px e nos dois temas; ~45 s). `window.__digilab` expõe só leitura
(assinatura e registro do pet vivo) para essa conferência. Etapa 4 (telas), feito: **Pet** (palco, fala, necessidades, chamado, desejo, ações, tempo,
Meus pets, revelação da evolução, conversa da fala livre com as mesmas chaves) **Crescer** (Treinar,
Aprendizado, Evolução) **Lutar** (Arena, Campanha, palco da luta: um estado só em `src/luta.ts`, o palco vai
para a aba visível) e **Diário** (Registro, Catálogo, Cenários; o pet B do cenário vira o rival fixo da arena). Navegação (DIRETRIZES_REPLICAR seções 6 e 7): no celular, barra de baixo com Pet, Crescer, Lutar e Diário, e **Conversar** e Configurações (tema, fala, registro, Tempo (teste)) no cabeçalho do Pet; de 900 px, barra lateral de 96 px com Conversar e Ajustes no pé; de 1100 px, topo com abas e mini-card do pet e as telas nas colunas das pranchas *Desktop. Luta em tela cheia (`#/lutar/luta`) com o modal Resultado; revelação (`#/evolucao`) e primeira vez (`#/inicio`) em tela cheia; folhas no celular viram o painel da direita no desktop. Tema (Auto/Claro/Escuro) em
Configurações, preferência na chave `…-tema` (o save não muda). O tempo anda e grava o save (ação
do dono na hora; tempo a cada 2 s; o pendente ao esconder/fechar a aba) e para durante a luta no palco e com o Resultado aberto (só a
interface, `luta.lutaSeguraTempo`: a luta já está no registro; o tempo parado não é compensado); se outra aba muda o save, o app relê em vez
de gravar por cima (o HTML não faz isso: não deixar o HTML e o app abertos juntos no mesmo pet). Semear save em
teste: por uma página da mesma origem que não seja o app (ex.: `/Assets/digilab_atlas_up.json`), senão o app grava
o pet dele por cima ao fechar.
O HTML continua sendo o jogo até a Etapa 6. `web/app/test/` tem a referência de
paridade. `motor_html.mjs` extrai o motor do HTML pelas marcas `@motor-inicio/@motor-fim` e roda em Node sem
DOM; `gerar_gabaritos.mjs` grava 60 vidas (3 versões de pet × 5 donos × 4 sementes, todos os estágios, tipos
de evento t/d/l/g/tr, NPCs, sombrias) com checkpoints (sha256 da assinatura + contadores) em
`gabaritos/vidas_*.json`; `constantes.test.mjs` confere cada folha numérica das constantes web contra
`gabaritos/constantes_python.json` (`python experiments/exportar_constantes_web.py`) pela tabela
`mapa_constantes.json`. `paridade_ts.test.mjs` passa os mesmos gabaritos no motor em TS (100% iguais, checkpoint a checkpoint). Gabaritos são do V8 do
Node: o Chrome difere no último bit de exp/log (libm) e o replay só é bit a bit no mesmo runtime.
**Devastador corrigido (2026-09-28)**: a semente de gambits dele tem a regra "perto e guts ≥ 60 → preparar
pesado", fora do `REPERTORIO`; a luta quebrava (TypeError). `regraDe(k)` procura no repertório e, fora dele,
nas sementes das sombrias. O repertório (candidatas da troca) não mudou, então nenhum pet existente muda.

`Assets\gerar_sprites_html.py` agora **recusa** sobrescrever o arquivo se ele tiver a aba
Evolução (`--forcar` para passar por cima e perder as edições).
