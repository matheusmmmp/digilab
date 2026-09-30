# Design — medalhas, arenas, itens e a Fronteira de Batalha

Status: **aprovado** (Matheus, 2026-09-29). **Partes 1 e 2 implementadas no jogo web**: parte 1 (branch `medalhas-parte1`, 2026-09-29; seção 11) e parte 2, as arenas com líderes (branch `medalhas-parte2`, 2026-09-30; seção 12). Partes 3 e 4 não. Todo número é PROPOSTO; os fatores dos líderes têm artefato (seção 12).

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

Metas de estágio (PROPOSTAS a partir da decisão; os bots canônicos de cada forma, as 4 espécies de cada lado, lados trocados na metade):
o de baixo **com o treino típico** contra o de cima **sem treino**.

| par | meta | razão de vida | calibração | validação |
|---|---|---|---|---|
| Rookie × Champion | ≤ 0,10 (pontos) | ×3,5 | 0,0888 | 0,0905 |
| Champion × Ultimate | ≤ 0,10 (pontos) | ×3,57 | 0,0891 | 0,0886 |
| Ultimate × Mega | ≤ 0,10 (pontos) | ×9,2 | 0,0906 | 0,0909 |
| Rookie × Ultimate | 0,00 (vitórias) | ×12,5 | 0,0391 (piso 0,039) | 0,0372 — **não fecha** |
| Champion × Mega | 0,00 (vitórias) | ×32,9 | 0,0497 (piso 0,0497) | 0,0509 — **não fecha** |

- **Dois estágios de distância não chegam a 0,00:** as vitórias que sobram são por estilo. Em alguns pares o de cima nunca acerta o de
  baixo (o caçador contra o titã e a muralha, por exemplo) e o limite de turnos decide pela fração de vida; a escala não muda isso (o
  "piso" é a taxa com razão de E 0,01, e a da escala já é ela). Fechar pede uma regra de combate ou listas das formas: fora desta tarefa.
- **Distância das razões do Digimon World** (Rookie → Champion ×2, Champion → Ultimate ×2,5; Mega ×2, o de hoje): a escala v6 se afasta
  sobretudo pelo **peso do treino**. Cada razão de vida = (1 + β × treino típico de baixo) ÷ (razão de E que a meta pede): 1,36 × 2,57;
  1,99 × 1,80; 2,62 × 3,51. A parte da razão de E fica perto do DW1 nos dois primeiros degraus; no Mega ela é 3,51 (a curva do
  Ultimate treinado contra o Mega tem uma cauda longa de vitórias por estilo).

Líderes na escala v6 (fatores da calibração; números da validação):

| arena | líder | fator | sem treino | com o treino típico | pior forma |
|---|---|---|---|---|---|
| Campina | Gazimon | 1,3 (era 1,1) | 0,0075 | 0,8575 | 0,800 (sereno) |
| Torre de pedra | Guardromon | 1,6 (era 1,4) | 0,0125 | 0,9025 | 0,6925 (colosso) |
| Floresta | Youkomon | 1,5 (era 1,2) | 0,0213 | 0,8675 | 0,605 (colosso) |
| Cidadela (série de 3) | Myotismon | 0,9 (era 0,7) | 0,0006 | 0,9159 | 0,5925 (sentinela) |
| Lago | MarinBullmon | 1,5 (era 1,2) | 0,0072 | 0,9228 | 0,675 (sentinela) |
| Montanha Espiral | Piedmon | 1,6 (era 1,2) | 0,0009 | 0,9175 | 0,665 (emboscador) |

- Os seis passam nas três metas na validação.
- **Guardromon (Torre, paciência):** com a lista de antes (a do espelho com o contra-golpe) nenhum fator de 0,5 a 4,0 passava: o caçador
  sem treino vencia atirando de longe, porque o líder respondia ao disparo frequente com o contra-golpe, que não devolve disparo. A lista
  da arena (`bots.GAMBITS_ARENA.torre`) troca só essa regra por "oponente atira com frequência → avançar" (a resposta da muralha); o
  contra-golpe contra quem prepara o pesado, insiste no golpe rápido ou na investida fica. Escolhida entre 4 variantes só nas sementes
  de calibração (`web/app/test/explorar_torre.mjs`, `artifacts_campanha/arenas/torre_variantes.json`). A frase da arena diz isso.
- No Lago a regra não mexe nos pets de referência (não têm dono): a calibração mede o líder, não o efeito de tirar as travas.
- O fator da arena vale só na luta de arena dos pets v6; os pets v1–v5 lutam com os NPCs de sempre.

**Desafiantes da campanha v6** (os NPCs que não são líderes; `web/app/test/calibrar_desafiantes_v6.mjs`, metas de sempre: sem treino ≤
0,30, com o treino típico ≥ 0,80, nenhuma forma < 0,5; fatores em `CESC_V6.fatorNpc`, só nos pets v6), validação:

| desafiante | lugar | fator | sem treino | com o treino típico | pior forma |
|---|---|---|---|---|---|
| Tortomon | Torre de pedra | 1,6 | 0,3912 | 0,8644 | 0,485 (colosso) — **não fecha** |
| Devidramon | Torre de pedra | 1,1 | 0,1862 | 0,9363 | 0,745 (caçador) |
| Puppetmon | Montanha Espiral | 2,5 | 0,1919 | 0,9334 | 0,8025 (vigia) |
| Machinedramon | Montanha Espiral | 2,7 | 0,225 | 0,8641 | 0,5675 (duelista) |

O Tortomon não fecha com nenhum fator (a exceção da Sentinela de sempre); fica o de maior folga. Como vencer qualquer rival de um lugar
abre o próximo, um Champion sem treino ainda pode abrir a Floresta pelo Tortomon; as medalhas (e a evolução) continuam pedindo os líderes.

**Saves:** descarte único versão 3 (arenas) e versão 4 (escala v6): os pets v6 de antes saem, com o mesmo aviso.

**Ficou de fora (partes 3 e 4 e o resto da seção 4):** itens, a Fronteira, e o que mais as medalhas liberariam (regras editáveis, espaços
de item).
