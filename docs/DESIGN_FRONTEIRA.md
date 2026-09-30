# Design — a Fronteira de Batalha (parte 4 das medalhas)

Status: **especificação para implementar** (pedido do Matheus, 2026-09-30: "segue com a parte 4 da fronteira"). Detalha a seção 7 do `docs/DESIGN_MEDALHAS_ARENAS.md`. Só o jogo web e só os pets v6; a pesquisa em Python não muda.

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
