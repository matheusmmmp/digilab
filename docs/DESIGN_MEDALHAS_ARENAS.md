# Design — medalhas, arenas, itens e a Fronteira de Batalha

Status: **aprovado** (Matheus, 2026-09-29). **Partes 1 e 2 implementadas no jogo web**: parte 1 (branch `medalhas-parte1`, 2026-09-29; seção 11) e parte 2, as arenas com líderes (branch `medalhas-parte2`, 2026-09-30; seção 12). Parte 3 (itens) implementada no jogo web **sem equilíbrio** (branch `medalhas-parte3`, 2026-09-30; seção 13); parte 4 detalhada em `docs/DESIGN_FRONTEIRA.md`, com a 4a (a Liga dos Líderes e o fim do jogo) implementada (branch `fronteira-4a`, 2026-09-30). Todo número é PROPOSTO; os fatores dos líderes têm artefato (seção 12).

**Decisões do Matheus (2026-09-29):**
1. Trava na evolução: **1, 3 e 5 medalhas** para Champion, Ultimate e Mega.
2. **6 arenas.**
3. O final é a **Fronteira de Batalha com os melhores Digimons**.
4. Começar **depois do diagnóstico** dos arquétipos.
5. **Os pets salvos de hoje podem ser descartados** ("pode matar e regerar os pets que já tem hoje"): quando a trava entrar, os saves do jogador (o pet ativo e os guardados) são apagados e o jogo começa de um ovo novo. Não é preciso manter os pets v5 funcionando sem a trava.

**O que ele junta.** Transforma em desenho concreto o passo M2 e as fases seguintes do `PESQUISA_VIDA_LINHAGEM_PROGRESSAO.md` (seções 13, 14, 16, 17 e 24).

**Inspiração, não evidência.** A ideia vem do Digimon Championship (medalhas de chefes liberando fases e evoluções) e dos líderes de ginásio do Pokémon. Pela revisão bibliográfica de 2026-09-29, essas mecânicas não estão verificadas em fonte primária: servem de inspiração de design, não de precedente citado.

## 1. A ideia em uma frase

O jogador (Tamer) coleciona **medalhas** vencendo os **líderes** de cada arena. As medalhas são dele, não do pet, e sobrevivem à morte do pet. O número de medalhas é o **potencial do Tamer**: libera as próximas fases, as evoluções mais altas e os itens. No fim, a **Fronteira de Batalha** reúne os líderes na versão mais forte, e vencer todos faz do jogador o campeão.

## 2. O que já existe e como encaixa

- **A campanha v5** tem quatro lugares: Campina (Rookie), Torre de pedra (Champion), Cidadela (Ultimate) e Montanha Espiral (Mega). Os NPCs estão calibrados na escala da campanha.
- **A evolução** para Ultimate pede tempo, 10 lutas com 80% de vitória e o caráter. Para Mega pede tempo, lutas e vínculo ≥ 0,4.
- **O que não existe:** Tamer, medalhas, itens e Fronteira. Hoje tudo é do pet, e quando ele morre sobra só a herança.

## 3. Medalhas e arenas

Uma **arena por lugar** da campanha, cada uma com um **líder** que testa uma capacidade de criação diferente, não só números maiores (seção 16 da pesquisa). Os NPCs de hoje viram os desafiantes de cada lugar, e o líder é a luta que dá a medalha.

| # | arena (lugar) | nível | líder (sugestão) | o que ele testa | regra da arena |
|---|---|---|---|---|---|
| 1 | Campina | Rookie | Gazimon | o básico: cuidado e treino | nenhuma |
| 2 | Torre de pedra | Champion | Guardromon | paciência: pune regras impulsivas | o líder devolve golpe forte |
| 3 | Floresta (nova) | Champion | Kyubimon ou similar | leitura: o líder muda de padrão no meio da luta | vence quem tem regras condicionais |
| 4 | Cidadela | Ultimate | Myotismon | resistência: três lutas seguidas | sem cura entre as lutas |
| 5 | Lago (novo) | Ultimate | a definir | vínculo: o pet decide sozinho | travar e vetar regras não valem |
| 6 | Montanha Espiral | Mega | Piedmon | tudo junto | chefe final da campanha |

- **Os nomes dos líderes são sugestão.** Só entram Digimon que já estão no atlas; os lugares novos precisam de fundo no atlas.
- **Cada líder se calibra como a campanha de hoje:** sem treino vence ≤ 0,30, com o treino típico do estágio ≥ 0,80. Isso depende do **equilíbrio entre arquétipos** (diagnóstico em curso): com as formas como estão, um líder pode ficar impossível para um arquétipo inteiro.
- **Revanche liberada, sem punição por perder.** Perder de um líder não custa medalha nem dinheiro.

## 4. As medalhas liberam a evolução (o potencial do Tamer)

A regra fica **"o pet pode evoluir quando cumpre os requisitos dele E o Tamer tem medalhas suficientes"**:

| evolução | requisito do pet (hoje) | medalhas do Tamer (PROPOSTO) |
|---|---|---|
| In-Training → Rookie | cuidado do bebê | nenhuma |
| Rookie → Champion | tempo, caráter | **1** (Campina) |
| Champion → Ultimate | tempo, 10 lutas, 80% de vitória | **3** |
| Ultimate → Mega | tempo, lutas, vínculo ≥ 0,4 | **5** |

- **O pet pronto não perde nada.** Se ele já cumpre os requisitos e falta medalha, ele fica "pronto para evoluir" e a tela diz qual medalha falta. Quando o Tamer ganha a medalha, a evolução acontece na hora.
- **A medalha é do Tamer, não do pet.** Um pet novo, de um Tamer com 5 medalhas, evolui só pelos requisitos dele. As conquistas passadas encurtam o caminho das próximas gerações. É o que dá ritmo ao jogo: o primeiro pet aprende e abre caminho, e os seguintes vão mais longe.
- **As medalhas liberam mais coisas (seção 14 da pesquisa):**
  - mais regras de luta editáveis (hoje a capacidade é fixa por estágio);
  - os lugares seguintes do mapa;
  - espaços de item (seção 6);
  - a entrada na Fronteira.

**A decisão aberta mais importante:** a trava na evolução pode frustrar. O pet está pronto e não evolui porque o jogador ainda não venceu um líder. A alternativa mais branda é a medalha travar **só o Mega**, e as demais só liberarem lugares e itens. Recomendo a versão da tabela (1, 3, 5), porque é o que você pediu e dá ritmo, mas **com a mensagem clara do que falta**, e com o pet não perdendo nada enquanto espera.

## 5. Como isso entra no motor sem quebrar o replay

Este é o ponto técnico que decide a implementação.

- **O Tamer ganha um registro próprio**, como o pet, com os eventos `medalha` (qual, quando, com que pet) e, depois, `item`. Fica numa chave nova do save; o registro do pet não muda de formato.
- **O motor do pet não pode ler o Tamer por fora**, porque o replay do pet tem de dar o mesmo resultado sozinho. Então, quando o Tamer ganha a medalha que libera uma evolução, **entra um evento `u` (liberação) no registro do pet**: "o Tamer tem N medalhas a partir deste tick". O replay do pet lê esse evento, como já lê a luta e a origem.
- **Pets salvos de hoje: descartados** (decisão do Matheus). A versão do pet sobe para v6 mesmo assim, porque é o que diz ao replay que o registro tem o evento `u`; mas, em vez de manter os v5 jogáveis, o app apaga os saves antigos na primeira abertura depois da atualização, com um aviso, e começa num ovo novo. Os **gabaritos de paridade** dos testes (pets v1–v3 e as vidas de referência) continuam: são fixtures de teste, não saves do jogador.
- **A pesquisa em Python não muda.** Medalhas e Tamer são só do jogo, como os gambits híbridos. O desvio vai para o `REGISTRO_DESVIOS`.

## 6. Itens e cartas

Três tipos, cada um com teto próprio, para o equipamento **complementar** a criatura e não substituí-la:

| tipo | o que faz | teto (PROPOSTO) | de onde vem |
|---|---|---|---|
| **chip de stat** | + pontos num stat | até metade da diferença entre dois estágios; conta dentro do teto de treino da vida | medalhas e líderes |
| **chip de regra** | dá ao pet uma condição ou regra de luta nova (ex.: "não prepare o pesado se o rival defende") | 1 por pet; não pode ser a regra que define outro arquétipo | arenas específicas |
| **carta** | efeito de uma luta só (ex.: +20 guts no início, cura no meio) | 1 por luta; proibida na Fronteira, salvo regra da instalação | loja e líderes |

- **Sobre o desequilíbrio:** chips de stat ajudam pouco se a diferença entre as formas vier do comportamento, e o furioso equipado continua vencendo o titã equipado. O diagnóstico em curso mede quanto os stats pesam. **O chip de regra é o que mais pode compensar uma forma fraca**, porque mexe no que decide o confronto.
- **Sem economia no começo:** os itens vêm de medalhas e líderes. Dinheiro e loja ficam para depois; eles pedem fontes e escoadouros (seção 11 da pesquisa).

## 7. A Fronteira de Batalha (o final)

Liberada com as 6 medalhas. O objetivo: **vencer todos os líderes na versão mais forte e se tornar o campeão**.

- **A Liga dos Líderes, com os melhores Digimons** (decisão do Matheus): os 6 líderes em sequência, na versão de revanche, todos no estágio Mega e com os times mais fortes do jogo, sem cura entre as lutas. Vencer todos = **campeão**, com uma medalha de ouro e a mensagem de conclusão (a jornada de hoje termina no Piedmon; passaria a terminar aqui).
- **Depois do título**, instalações com regras próprias (seção 24 da pesquisa), para rejogar:
  - **Torre:** sequência de lutas, com recorde;
  - **Fábrica:** Digimon alugados, que testa o conhecimento do Tamer;
  - **Palácio:** o pet decide sozinho;
  - **Salão:** um pet por nível, que dá sentido a criar Rookies e Champions.
- **Contra o grind:** a recompensa da Fronteira é prestígio (títulos, recordes, a versão dourada da medalha), não força. Nada da Fronteira deixa o pet mais forte fora dela.

## 8. O ritmo esperado (a curva)

- **1º pet:** Campina e talvez a Torre (1–2 medalhas); aprende o jogo. Pode morrer ou envelhecer sem passar do Champion, e isso é esperado.
- **2º e 3º pets:** chegam a Ultimate mais rápido (as medalhas já estão com o Tamer), abrem a Cidadela e o Lago.
- **Pets seguintes:** Mega e Montanha Espiral; depois a Fronteira.
- **Nada fixo:** a curva sai da calibração dos líderes e do tempo de cada estágio (rápido ou clássico).

## 9. Ordem de implementação (um PR por parte)

1. **Tamer e medalhas:** o registro do Tamer, as medalhas dos lugares de hoje, a trava da evolução (pets v6, evento `u`), a tela de medalhas. Não depende do equilíbrio.
2. **Líderes das arenas:** as regras de arena, os dois lugares novos, a calibração. **Depende do equilíbrio entre arquétipos.**
3. **Itens:** chips e cartas com os tetos. Os números **dependem do diagnóstico**.
4. **Fronteira:** a Liga dos Líderes e o fim do jogo; as instalações depois.

## 10. O que você precisa decidir

1. **A trava na evolução:** 1/3/5 medalhas para Champion/Ultimate/Mega (a sua ideia), ou a medalha travando só o Mega.
2. **Número de arenas:** 6 (os 4 lugares de hoje mais 2 novos), ou só os 4 que existem.
3. **Pets v6** para a trava, deixando os v5 como estão.
4. **O fim do jogo passa a ser a Fronteira**, e não mais o Piedmon.
5. **A ordem:** Tamer e medalhas primeiro (não dependem do equilíbrio), com os líderes e os itens esperando o diagnóstico.

## 11. O que a parte 1 implementou (2026-09-29) e o que ficou para a parte 2

**Implementado (só `web/app/`):**
- **Pets v6** (`VERSAO_PET = 6`): a trava 1/3/5 (`CMD` em `motor/constantes.ts`). O pet que cumpre os próprios requisitos e não tem
  as medalhas fica pronto e evolui no tick do evento `u` (`Motor.liberar`, `esperandoMedalha`, `requisitoMedalhas`,
  `requisitosEvolucao`; `requisitosMega` expõe `medalhas: {tem, precisa, ok}`). O caráter e o resto da evolução são medidos na hora
  em que ela acontece. A assinatura dos v6 inclui as medalhas; a dos v1–v5 não mudou.
- **A tabela das medalhas** (`motor/medalhas.ts`, única): Campina/Gazimon, Torre de pedra/Guardromon, **provisória**
  Devidramon (Torre de pedra, no lugar da Floresta), Cidadela/Myotismon, **provisória** Tortomon (Torre de pedra, no lugar do
  Lago), Montanha Espiral/Piedmon. A parte 2 troca só esta tabela (os ids já são os das arenas: `floresta`, `lago`).
- **O Tamer** (`src/tamer.ts`): registro próprio na chave `digilab-web-v21-sprites-tamer` (`{versao: 1, log}`, eventos
  `["medalha", {id, n, quando, pet, forma, tick}]`), reproduzido como o pet; evento desconhecido falha alto. Medalha na primeira
  vitória contra o líder, com qualquer pet **v6**. O app grava a medalha e põe o `u` no pet ativo; um pet guardado recebe o `u`
  quando volta a ser o ativo (e a revelação mostra a evolução).
- **Saves de antes descartados** na primeira abertura, com aviso, e ovo novo pela escolha do brasão (seção 5).
- **Telas:** Lutar · Medalhas; o requisito de medalha na Evolução ("Falta a Medalha da Campina: vença o Gazimon na Campina."); o
  líder marcado na Campanha, com o selo; a medalha nova no Resultado da luta.

**Ficou para a parte 2 (e depois):**
- as arenas com regra própria, os lugares novos (Floresta e Lago) e a calibração dos líderes (seção 3), que dependem do equilíbrio
  entre arquétipos;
- as outras coisas que as medalhas liberam (seção 4): regras de luta editáveis, lugares do mapa, espaços de item, a Fronteira;
- itens (seção 6) e a Fronteira (seção 7).

**Onde o código não batia com o desenho, e o que foi corrigido:**
- A 5ª medalha provisória vinha do Machinedramon, calibrado para Mega: um Ultimate treinado o vencia 0,28 em média, e 5 das 8
  formas quase nunca (`docs/REGISTRO_DESVIOS.md`). Trocada pelo **Tortomon** (Torre de pedra), que o pet treinado vence.
- O tempo de cada estágio contava desde o nascimento: um Rookie que esperou a medalha virava um Champion curto. Nos v6 ele
  conta desde a evolução anterior.

## 12. O que a parte 2 implementou (2026-09-30): as arenas com líderes

Só `web/app/`, só pets v6 (as lutas deles usam a V21D). A pesquisa em Python não tem arenas (`docs/REGISTRO_DESVIOS.md`, 2026-09-30).

**As seis arenas** (`motor/arenas.ts`, tabela `ARENAS`; campanha v6 em `motor/bots.ts`, `LUGARES_V6`/`CAMPANHA_V6`). A ordem do mapa
segue o nível; vencer qualquer rival de um lugar abre o próximo, como antes. Os NPCs de antes seguem como desafiantes, com as mesmas
chaves.

| # | arena | nível | líder | regra (como foi feita) |
|---|---|---|---|---|
| 1 | Campina | Rookie | Gazimon | nenhuma |
| 2 | Torre de pedra | Champion | Guardromon | **paciência**: o líder ganha a técnica do guardião (contra-golpe) e a lista do espelho com as regras dela; quem prepara o pesado de perto ou insiste no golpe rápido leva o golpe de volta |
| 3 | Floresta (nova) | Champion | **Youkomon** | **leitura**: o líder muda de padrão no turno 10, pela condição `turno_execucao` que a linguagem já tinha (`GAMBITS_ARENA.floresta`): atirador até o 10, brigão depois |
| 4 | Cidadela | Ultimate | Myotismon | **resistência**: três lutas seguidas num evento só; o pet leva a vida e o guts de uma para a outra, o líder volta inteiro; a série para na primeira que não for vitória, e a medalha (e o lugar vencido) só vêm com as três |
| 5 | Lago (novo) | Ultimate | **MarinBullmon** | **vínculo**: as travas e os vetos do dono não valem; o pet luta com a lista que ele mesmo faria (`GambitsPet.listaSozinho`: sem trava, só a nota ordena, e as regras vetadas que ele conhece voltam) |
| 6 | Montanha Espiral | Mega | Piedmon | chefe da campanha, sem regra a mais |

- **Líderes novos:** o Kyubimon é forma de pet (Champion guardião do brasão Coragem), então a Floresta ficou com o **Youkomon**, outra
  raposa Champion do atlas. No Lago, o **MarinBullmon** (Ultimate aquático do atlas, não é forma de pet), com a lista do adaptativo
  (lê o que o rival repete). Os dois e as duas ilhas (Floresta = `WorldMap_04`, Lago = `WorldMap_02`) entraram no atlas, fora do repo
  (`Assets/catalogo_sprites_up.json`, `Assets/gerar_atlas_up.py`), no padrão da `WorldMap_07` da evolução canônica.
- **Replay:** a regra depende só do rival e da versão do pet, que o registro já tem. O evento `l` continua `{r, s}` (as lutas 2 e 3 da
  Cidadela usam sementes derivadas da do evento); os eventos antigos se leem como antes. `Motor.montarLuta`/`lutadores` montam a luta
  do mesmo jeito para o motor e para a tela (replay no Diário, lutas do registro).
- **Medalhas** (`motor/medalhas.ts`): a 3ª vem do Youkomon (Floresta) e a 5ª do MarinBullmon (Lago); acabaram as fontes provisórias
  (Devidramon e Tortomon seguem na Torre como desafiantes).
- **Telas:** o cartão da arena (líder, a regra em uma frase, a medalha) na Campanha; o mapa de seis ilhas (390 × 760); "luta k de 3"
  na luta da Cidadela e o bloco da resistência no Resultado; o aviso do Lago na luta (sem os botões de travar e vetar) e no Resultado;
  a tela de Medalhas com a regra de cada arena, sem "provisória".
- **Correção junto:** as duas regras novas do vigia V21D voltam como candidatas de troca nos pets v6 (`candidatasDoVigia`).

**Calibração dos líderes** (`web/app/test/calibrar_arenas.mjs`, método do `calibrar_mega.mjs`: motor web, escala ligada, regras dos
pets v6, a regra de cada arena; pets de referência = as formas do estágio da arena nas 4 espécies, com treino uniforme; o pet é o lado A,
como no jogo). Fator escolhido nas sementes de calibração (3101…3505) pela maior folga; validação uma vez nas sementes 4101…4505
(`artifacts_campanha/arenas/calibracao.json` e `validacao.json`).

**Recalibração na escala dos pets v6 (2026-09-30, decisão do Matheus: "o treino tem que decidir" e "o estágio tem que pesar").** As
metas dos líderes ficaram mais duras: o pet do estágio da arena **sem treino vence ≤ 0,05** (era ≤ 0,30), **com o treino típico ≥ 0,80**
(Rookie 8, Champion 22, Ultimate 36, Mega 40) e nenhuma forma abaixo de 0,5. Com o peso do treino de antes (β 0,03) só o Lago passava as
três, sem folga (o treino pesava pouco: +8 pontos no Rookie davam só ×1,24), e a Torre não passava com fator nenhum. Por isso os pets v6 ganharam uma escala própria, `CESC_V6`
(`web/app/motor/constantes.ts`; só nas lutas de escala dos pets v6, campanha e arenas): vida Rookie 200, Champion 700, Ultimate 2500,
Mega 23000 e peso do ponto de treino **β = 0,045** (antes 0,03). Escolha em `web/app/test/calibrar_escala_v6.mjs`
(`artifacts_campanha/escala_v6/`): o β é o menor da grade em que todos os líderes (menos a Torre) têm um fator com folga ≥ 0,01; as vidas
saem das metas de estágio abaixo.

**Regra do limite de turnos (decisão do Matheus, 2026-09-30):** quando a luta chega ao limite de turnos sem nocaute, **vence quem foi
desafiado**. No jogo o pet sempre desafia (NPC da campanha, líder da arena, bot da arena), então nos pets v6 a luta que chega ao limite
é derrota do pet; na Cidadela ela quebra a série. `combate.fimV2`/`jogarV2` recebem o desafiado (lado A, lado B ou ninguém, que é a
fração de vida de sempre); `desafiadoDaVersao` dá o rival nos pets v6 e ninguém nos v1–v5; o `Motor.montarLuta` passa o desafiado.
Nada novo no registro (deriva da versão do pet); cenários, pets v1–v5 e a paridade V21D com o Python não mudam. Parametrizada para a
Fronteira, onde o desafiado será o campeão. Descarte único versão 5 (os v6 de antes decidiriam lutas de outro jeito no replay).

Metas de estágio (PROPOSTAS a partir da decisão; os bots canônicos de cada forma, as 4 espécies de cada lado, lados trocados na metade):
o de baixo **com o treino típico** contra o de cima **sem treino**. Nas medidas com a regra do limite, o desafiado é o de cima. A escala
foi escolhida antes da regra (coluna "calibração"); com a regra só se validou de novo, sem mudar número.

| par | meta | razão de vida | calibração (limite pela fração) | validação (limite pela fração, commit `0008f00`) | **validação (limite do desafiado)** |
|---|---|---|---|---|---|
| Rookie × Champion | ≤ 0,10 (pontos) | ×3,5 | 0,0888 | 0,0905 | **0,0008** |
| Champion × Ultimate | ≤ 0,10 (pontos) | ×3,57 | 0,0891 | 0,0886 | **0,0108** |
| Ultimate × Mega | ≤ 0,10 (pontos) | ×9,2 | 0,0906 | 0,0909 | **0,0041** |
| Rookie × Ultimate | 0,00 (vitórias) | ×12,5 | 0,0391 (piso 0,039) | 0,0372 | **0,00** |
| Champion × Mega | 0,00 (vitórias) | ×32,9 | 0,0497 (piso 0,0497) | 0,0509 | **0,00** |

- **Com a regra do limite as cinco metas passam.** Pela fração de vida os dois estágios de distância não chegavam a 0,00: sobravam
  vitórias por estilo (em alguns pares o de cima nunca acertava o de baixo, como o caçador contra o titã e a muralha, e o limite decidia
  pela fração de vida; o "piso" é a taxa com razão de E 0,01). Com a regra essas lutas são do desafiado.
- **Distância das razões do Digimon World** (Rookie → Champion ×2, Champion → Ultimate ×2,5; Mega ×2, o de hoje): a escala v6 se afasta
  sobretudo pelo **peso do treino**. Cada razão de vida = (1 + β × treino típico de baixo) ÷ (razão de E que a meta pedia na calibração):
  1,36 × 2,57; 1,99 × 1,80; 2,62 × 3,51. A parte da razão de E fica perto do DW1 nos dois primeiros degraus; no Mega ela é 3,51 (a curva
  do Ultimate treinado contra o Mega tinha uma cauda longa de vitórias por estilo, a que a regra do limite tirou). Com a regra as metas
  passam com folga, então a escala poderia ficar mais perto do DW1; ela não foi recalibrada (só validada de novo).

Líderes na escala v6 (fatores da calibração; números da validação com a regra do limite, `artifacts_campanha/arenas/validacao.json`;
nenhum saiu das metas, nenhum fator mudou):

| arena | líder | fator | sem treino | com o treino típico | pior forma |
|---|---|---|---|---|---|
| Campina | Gazimon | 1,3 (era 1,1) | 0,0075 | 0,8575 | 0,800 (sereno) |
| Torre de pedra | Guardromon | 1,6 (era 1,4) | 0,005 | 0,8125 | 0,665 (guardião) |
| Floresta | Youkomon | 1,5 (era 1,2) | 0,0213 | 0,8675 | 0,605 (colosso) |
| Cidadela (série de 3) | Myotismon | 0,9 (era 0,7) | 0,0006 | 0,9063 | 0,535 (sentinela) |
| Lago | MarinBullmon | 1,5 (era 1,2) | 0,0072 | 0,8959 | 0,56 (sentinela) |
| Montanha Espiral | Piedmon | 1,6 (era 1,2) | 0,0009 | 0,8931 | 0,555 (sentinela) |

- Os seis passam nas três metas. Os mais apertados com a regra: a Torre com o treino típico (0,8125) e a pior forma na Cidadela (0,535).
- **Guardromon (Torre, paciência):** com a lista de antes (a do espelho com o contra-golpe) nenhum fator de 0,5 a 4,0 passava: o caçador
  sem treino vencia atirando de longe, porque o líder respondia ao disparo frequente com o contra-golpe, que não devolve disparo. A lista
  da arena (`bots.GAMBITS_ARENA.torre`) troca só essa regra por "oponente atira com frequência → avançar" (a resposta da muralha); o
  contra-golpe contra quem prepara o pesado, insiste no golpe rápido ou na investida fica. Escolhida entre 4 variantes só nas sementes
  de calibração, antes da regra do limite (`web/app/test/explorar_torre.mjs`, `artifacts_campanha/arenas/torre_variantes.json`). A
  frase da arena diz isso.
- No Lago a regra não mexe nos pets de referência (não têm dono): a calibração mede o líder, não o efeito de tirar as travas.
- O fator da arena vale só na luta de arena dos pets v6; os pets v1–v5 lutam com os NPCs de sempre.

**Desafiantes da campanha v6** (os NPCs que não são líderes; `web/app/test/calibrar_desafiantes_v6.mjs`, metas de sempre: sem treino ≤
0,30, com o treino típico ≥ 0,80, nenhuma forma < 0,5; fatores em `CESC_V6.fatorNpc`, só nos pets v6). Na validação com a regra do limite
o Tortomon (1,6) e o Machinedramon (2,7) ficaram com uma forma abaixo de 0,5; os dois foram recalibrados nas sementes de calibração com a
regra (`desafiantes_calibracao.json`) e validados de novo (`desafiantes_validacao.json`); Devidramon e Puppetmon ficaram:

| desafiante | lugar | fator | sem treino | com o treino típico | pior forma |
|---|---|---|---|---|---|
| Tortomon | Torre de pedra | 1,5 (era 1,6) | 0,3087 | 0,8912 | 0,5775 (colosso) — **não fecha** (sem treino > 0,30) |
| Devidramon | Torre de pedra | 1,1 | 0,1862 | 0,905 | 0,62 (caçador) |
| Puppetmon | Montanha Espiral | 2,5 | 0,0413 | 0,8628 | 0,605 (muralha) |
| Machinedramon | Montanha Espiral | 2,2 (era 2,7) | 0,1247 | 0,9566 | 0,7775 (duelista) |

O Tortomon não fecha com nenhum fator (a exceção da Sentinela de sempre); fica o de maior folga. Como vencer qualquer rival de um lugar
abre o próximo, um Champion sem treino ainda pode abrir a Floresta pelo Tortomon; as medalhas (e a evolução) continuam pedindo os líderes.

**Saves:** descarte único versão 3 (arenas), 4 (escala v6) e 5 (limite do desafiado): os pets v6 de antes saem, com o mesmo aviso.

**Ficou de fora (partes 3 e 4 e o resto da seção 4):** itens, a Fronteira, e o que mais as medalhas liberariam (regras editáveis, espaços
de item).

## 13. Parte 3: itens (chips e cartas) — especificação (2026-09-30)

Só `web/app/` e só pets v6. A pesquisa em Python não tem Tamer nem itens (`docs/REGISTRO_DESVIOS.md`). Todo número desta seção é
**PROPOSTO**; os gates (13.7) foram escritos antes de medir, e a medição só pode mudar um item nas sementes de calibração, dizendo o porquê
(13.8, depois da medição). Princípio (seção 6 e `docs/DIAGNOSTICO_ARQUETIPOS.md`): os stats da forma pesam pouco, a técnica e a lista de
regras decidem. Por isso o item **complementa, não substitui a criatura**: o catálogo tem mais chips que mudam comportamento (regra) do
que chips de número, e os números ficam presos aos tetos do treino.

**Sem equilíbrio (decisão do Matheus, 2026-09-30).** Ainda vão entrar outras mecânicas no combate, e o equilíbrio será feito numa rodada
só, depois delas. Os itens entraram com os números **PROPOSTOS** desta especificação, sem medição e sem ajuste: os gates G-I1–G-I4 (13.7)
ficam para a rodada de equilíbrio geral do combate, e nenhum item foi enfraquecido por medição.

### 13.1 Os três tipos e os tetos

- **Chip de stat.** +2 pontos de treino (1 em cada um de dois stats). Três tetos, nesta ordem:
  1. a soma dos chips de stat equipados vale no máximo **25% do treino típico do estágio atual** (Rookie 8 → 2; Champion 22 → 5,5;
     Ultimate 36 → 9; Mega 40 → 10; o típico é o da parte 2);
  2. **dentro dos tetos do treino:** o ponto de chip só ocupa o espaço que falta no estágio (teto do estágio − pontos treinados nele),
     na vida (teto da vida − total treinado) e no stat (10 − pontos do stat). O chip **adianta** treino: num pet que já treinou o
     estágio até o teto ele não soma nada;
  3. vale como ponto de treino na luta (no perfil e, na campanha e nas arenas, na escala E = vida × (1 + β × pontos) dos pets v6). Não
     entra no treino do registro, na fadiga nem na sobrecarga, e sai quando o chip sai.
- **Chip de regra.** Uma regra de um **catálogo fechado** entra na lista de gambits do pet:
  - ocupa uma vaga da lista (capacidade 3/5/8); com a lista cheia, sai a regra livre de nota mais baixa;
  - entra no topo (nota igual à maior da lista, na frente dela); depois o aprendizado muda a nota dela como a das outras, mas o pet **não a
    troca** enquanto o chip estiver equipado;
  - o dono pode **travar** a posição dela; **vetar** não (para tirar, desequipe o chip);
  - só com as condições do estágio (a regra que usa "o oponente insiste em…" pede um Ultimate);
  - nunca a regra que define outro arquétipo: nenhuma técnica (cada linha só usa a sua), nenhuma leitura da intenção (a passiva do vigia)
    e nenhuma das duas regras do vigia V21D;
  - ao desequipar, sai da lista, e a vaga volta para a melhor candidata (como no veto).
- **Carta.** Efeito de uma luta só. **Uma carta por luta**, escolhida antes; é **consumida** (sai do inventário do Tamer). Na Cidadela a série
  de três lutas é uma luta (um evento do registro): a carta vale para a série inteira, uma vez.

### 13.2 Catálogo (9 itens)

| id | item | tipo | efeito | pede | de onde vem | fraqueza medida que ataca |
|---|---|---|---|---|---|---|
| `chip_forca` | Chip de Força | chip de stat | +1 força, +1 vigor | Rookie | medalha da Campina (Gazimon) | o básico: adianta o treino de quem começa |
| `chip_guarda` | Chip de Guarda | chip de stat | +1 guarda, +1 recuperação | Rookie | medalha da Cidadela (Myotismon) | resistência |
| `chip_recuo` | Chip Recuo | chip de regra | "oponente preparando pesado → recuar" | Champion | medalha da Torre de pedra (Guardromon) | o pesado anunciado (diagnóstico, seção 2): quem responde a ele gastando guts (esquiva) ou com a pele |
| `chip_oportunista` | Chip Oportunista | chip de regra | "perto e guts do oponente < 20 → preparar pesado" | Champion | medalha da Floresta (Youkomon) | as linhas lentas (guardião e colosso), as piores formas contra os líderes do nível delas na parte 2 |
| `chip_perseguidor` | Chip Perseguidor | chip de regra | "oponente insiste em disparo → avançar" | Ultimate | medalha do Lago (MarinBullmon) | colossos e guardiãs contra os caçadores (titã 0,015; sentinela × muralha 1,00; espelho × emboscador 0,006) |
| `chip_aparo` | Chip Aparo | chip de regra | "oponente insiste em golpe rápido → defender" (o aparo devolve dano) | Ultimate | medalha da Montanha Espiral (Piedmon) | caçadores, titã e vigia contra o furioso e os líderes agressivos (o aparo é o único freio medido do furioso) |
| `carta_folego` | Carta de Fôlego | carta | +20 de guts no começo da luta (até o máximo) | — | revanche na Campina e na Floresta | — |
| `carta_cura` | Carta de Cura | carta | na primeira vez que a vida cai abaixo de 30%, cura 20% da vida máxima | — | revanche na Cidadela e na Montanha Espiral | — |
| `carta_foco` | Carta de Foco | carta | o pet não se distrai: segue as próprias regras em todos os turnos (ε = 0) | — | revanche na Torre de pedra e no Lago | — |

### 13.3 De onde vêm (sem economia)

- **Medalha → item:** a primeira vitória contra um líder dá a medalha **e** o item daquela arena (tabela acima). Um Tamer que já tinha a
  medalha antes desta parte recebe o item na abertura (a regra é "tem a medalha e não tem o item dela").
- **Revanche → carta:** vitória contra um líder cuja medalha o Tamer já tinha antes da luta, com um pet **do nível da arena** (um Mega que
  volta à Campina não ganha carta), dá a carta daquela arena. **Espera:** cada pet ganha no máximo 1 carta por líder a cada **24 h do
  relógio dele** (1440 min de jogo). Na Cidadela, vitória = a série de três.
- Nada mais dá item. Sem dinheiro e sem loja (seção 6).

### 13.4 Espaços (seção 4)

- **Chips por pet:** pelas medalhas que o pet conhece (evento `u`): **0** sem medalha, **1** com 1–2, **2** com 3–4, **3** com 5–6.
- **Cartas:** 1 por luta.
- O chip não se gasta: o Tamer tem o chip, e qualquer pet dele pode ter uma cópia equipada (só o ativo luta).

### 13.5 Onde os itens valem

Nas lutas do pet v6 que entram no registro: campanha (desafiantes e líderes), arenas e arena contra bots. Os chips estão no pet (lista e
treino), então valem também contra o pet de cenário; a carta só em luta que entra no registro (a Melhor de 10 não usa carta). Não valem:
pets v1–v5, os Cenários (donos simulados), a pesquisa. Proibição na Fronteira (seção 6): parte 4.

### 13.6 Registro e replay

- **Tamer** (`src/tamer.ts`, registro versão 2; a versão 1, só com medalhas, continua abrindo): eventos novos `["item", {id, n, quando,
  origem: "medalha" | "revanche", lider, pet, forma, est, tick}]` e `["carta_usada", {id, quando, pet, tick}]`. O replay confere o item da
  medalha, a medalha antes da carta de revanche, o nível e a espera, e que a carta usada estava no inventário. Evento desconhecido falha alto.
- **Pet** (eventos novos, só v6): `["i", {op: "equipar" | "desequipar", id}]` e `["k", {id}]` (a carta vale para a luta seguinte: o
  próximo evento do registro tem de ser a luta `l`, senão o replay falha). O motor confere vagas (pelas medalhas que o pet conhece),
  tipo, estágio e vida; **não lê o Tamer**: o app confere o inventário antes de gravar.
- **Assinatura:** a dos v6 só muda quando há item no registro. Sem item, pets v1–v6, gabaritos de paridade, a paridade V21D (272 partidas)
  e as calibrações da parte 2 ficam iguais (testes e conferência no script de medição).
- **Descarte:** não sobe; nenhum registro que existe muda no replay.

### 13.7 Gates PROPOSTOS (para a rodada de equilíbrio geral; não medidos nesta parte)

A medição fica pronta em `web/app/test/medir_itens.mjs` (com `test/itens_ref.mjs`: os pets de referência e as sementes da parte 2, os
itens pelo motor), para a rodada de equilíbrio. Não foi rodada como etapa desta parte, e não há artefato dela.

Método: motor web, escala dos pets v6 ligada, regras V21D, regra do limite do desafiado, os pets de referência da parte 2 (as formas do
estágio × 4 espécies, bots canônicos) e as sementes de calibração 3101…3505 para ajustar; **uma** validação nas 4101…4505 depois de
fechar os itens. "Melhor combinação" = o máximo, **por forma**, entre todas as combinações de até **3 chips** permitidos no estágio (a
geração de um Tamer com as 6 medalhas) com nenhuma carta ou uma das 3 cartas. Os chips de regra entram como no pet recém-equipado: no
topo, na ordem em que são equipados, saindo a última regra da lista se ela estiver cheia.

| gate | critério |
|---|---|
| **G-I1** o item não substitui o treino | com a melhor combinação, o pet **sem treino** contra cada um dos 6 líderes vence ≤ **0,05** (média das formas e espécies, como na parte 2; relata a pior forma) |
| **G-I2** o estágio continua pesando | o de baixo com o treino típico **e a melhor combinação** (por forma de baixo, a que dá mais pontos contra as formas de cima) contra o de cima sem treino e sem item: vizinhos ≤ **0,10** (pontos), dois estágios = **0,00** (vitórias) |
| **G-I3** o item não desequilibra as formas | na matriz das 8 formas adultas (bots canônicos, V21D, mesma espécie dos dois lados, ε 0,05, 100 partidas por par por semente e espécie, lados trocados na metade, sem escala), a forma medida com a melhor combinação e as outras sem item: força contra as outras 7 ≤ **0,60**, exceto o furioso (exceção declarada) |
| **G-I4** o item ajuda quem precisa (relato) | para cada chip de regra: o ganho de força das formas-alvo contra as outras 7 (só aquele chip) e o ganho contra os líderes do nível (com o treino típico) |

Na rodada de equilíbrio: se um item quebrar G-I1–G-I3 nas sementes de calibração, ele é enfraquecido ou restrito ali, com o motivo
registrado. Artefatos em `artifacts_campanha/itens/`.

### 13.8 O que a parte 3 implementou (2026-09-30)

Só `web/app/`, só pets v6, com os números de 13.1–13.4 como estão.

- **Motor:** `motor/itens.ts` (o catálogo, `ITEM_DA_MEDALHA`, `CARTA_DA_REVANCHE`, `vagasDeChip`, `chipServe`, `bonusChipsStat`,
  `listaComChips` para a medição); `CIT` em `constantes.ts` (vagas, teto dos chips de stat, típico, espera, Fôlego e Cura). As cartas na
  luta: `combate.EfeitoCarta`/`comCarta` (guts a mais no começo, ε 0) e a cura em `jogarV2` (parâmetro novo, por lado); `arenas.jogarArena`
  aplica a carta ao evento inteiro (na série da Cidadela a cura vale uma vez). Sem carta e sem chip, as funções dão a luta de sempre
  (teste de controle).
- **Pet:** eventos `i` (equipar/desequipar) e `k` (carta da próxima luta); `Motor.equipar`/`desequipar`/`porqueNaoEquipa`/`vagasChip`/
  `pontosDeLuta` e `lutar(rival, semente, carta)`. O `k` entra logo antes do `l`, e o replay falha se o evento seguinte não for a luta.
  Chip de regra em `GambitsPet` (`equiparRegra`/`desequiparRegra`, `chipsRegra`): entra no topo; o aprendizado não o troca; vetar falha;
  atravessa a evolução. Se a regra já estava na lista quando o chip entrou, ao desequipar ela fica (só perde a proteção); senão sai e a vaga
  volta para a melhor candidata. As regras dos chips que não estão no repertório não viram candidatas de troca (`regraDe` as acha).
- **Assinatura:** a do pet e a dos gambits ganham os itens só quando há evento de item (`comItens`, `usouChip`). Pets v1–v5, os
  gabaritos, a paridade V21D e os artefatos de validação da parte 2 (`calibrar_arenas.mjs --validar`, `calibrar_escala_v6.mjs
  --validar`) saem iguais byte a byte.
- **Tamer** (`src/tamer.ts`, registro versão 2, lê a 1): `item` e `carta_usada`; `conferirItensDasMedalhas` (na hora da medalha e,
  retroativo, na abertura), `conferirRevanche`/`porqueSemCarta` (medalha antes, nível da arena, espera no relógio do pet). O app muda o
  Tamer por `jogo.mudarTamer`. Descarte único: não subiu.
- **Telas:** **Crescer · Itens** (inventário, vagas do pet, equipar e desequipar com o porquê de não poder); a escolha da carta antes da
  luta na Campanha e na Arena (`componentes/EscolhaCarta.tsx`); no Resultado, o item novo (da medalha ou da revanche) e a carta usada;
  em Medalhas, o item de cada medalha e a carta da revanche; nas regras de combate, a marca "chip" e sem o botão de vetar.
- **Testes:** `test/itens.test.ts` (catálogo, tetos, cada item, vagas, replay, Tamer, v1–v5) e 8 e2e (ganhar o chip do líder, equipar,
  lutar com ele; a carta; a tela em 360/390/1280 px, claro e escuro).

**Uma passada de medição chegou a rodar antes da decisão** (só sementes de calibração), com o catálogo sendo mudado no meio dela. Os
artefatos foram apagados e nada dela entrou nos itens: o catálogo e os números são os de 13.2–13.4. Fica como pista qualitativa para a
rodada de equilíbrio: a luta contra o líder é um limiar estreito (um pouco de vida ou de treino a mais muda muito a taxa do pet sem
treino), e uma regra no topo da lista pode pesar contra a própria forma, porque passa na frente das regras dela e tira uma da lista.

**Ficou de fora:** a medição e o equilíbrio (rodada geral); dinheiro e loja; a proibição de cartas na Fronteira (parte 4).

### 13.9 A rodada de equilíbrio geral, fase 3 (pets v9)

Os gates G-I1–G-I3 viraram as metas M-D1–M-D3 da rodada de equilíbrio geral e foram medidos nos pets v9 (`test/medir_itens.mjs`,
`artifacts_equilibrio_geral/fase3/`; relatório em `docs/EQUILIBRIO_GERAL.md`, fase 3). Com os números desta seção, nas regras dos v9, G-I1 e
G-I3 não passavam. Nos pets v9 (`CIT_V9`, `itens.ts`; os v6–v8 não mudam):
- os itens pedem treino: com menos da metade do treino típico do nível, os chips não fazem efeito e a carta não pode ser usada;
- a carta só vale contra os NPCs da campanha (desafiantes e líderes), não na arena contra bots;
- o chip de regra vai para o fim da lista, sem tirar regra nenhuma;
- o ponto do chip de stat vale a metade.
