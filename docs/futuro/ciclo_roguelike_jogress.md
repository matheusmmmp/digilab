# O ciclo da vida como roguelike e a jogress entre dois pets (ideia, 2026-11-12)

**Status:** IDEIA para frente, sem tarefa e sem código. O Matheus a descreveu em 2026-11-12 e disse: "isso é uma feature para frente, que
daí a gente pode pensar em como aplicar isso mecanicamente". Nada aqui está decidido. Os números, quando houver, serão PROPOSTOS.

Liga-se ao desenho do parceiro ([`GDD_V3_PARCEIRO.md`](../GDD_V3_PARCEIRO.md), a PAR-11) e ao plano do multijogador
([`PLANO_V3_MMO.md`](../PLANO_V3_MMO.md), as MMO-17 e MMO-18).

## 1. A ideia, nas palavras do Matheus

- **A morte fecha um ciclo.** O pet chega a um estágio em que o jogador pode **herdar os stats** e recomeçar, "como se fosse num
  roguelike": o ciclo zera, e na rodada seguinte o pet começa com os stats melhorados e pode crescer mais.
- **Ou o jogador guarda.** Ele tem vários pets: deixa **um no banco e outro ativo**, e faz uma **jogress** entre os dois.

## 2. O que o jogo já tem (conferido na `main`, 2026-11-12)

| peça | onde | o que pesa |
|---|---|---|
| a nova geração | `web/app/src/heranca.ts`: o pai 1 é o pet ativo, adulto e vivo; o pai 2 é um pet em espera ou um arquivo importado; ao cruzar, o pai ativo se aposenta e o filho vira o ativo | já existe um "recomeçar com herança", por cruzamento |
| os pets guardados | `web/app/src/pets.ts` (`CHAVE_GUARDADOS`) | o banco já existe |
| a morte | definitiva para aquele pet; a lesão sem tratar e a saúde no chão matam | o fim do ciclo já existe |
| os chips e as medalhas do Tamer | valem para todos os pets do Tamer | parte do progresso já atravessa as vidas |

## 3. As tensões a resolver antes de virar tarefa

| tensão | o que está decidido hoje | o que a ideia pede |
|---|---|---|
| **a herança de stats** | a MMO-18 recomendou, e o Matheus aprovou, o reset com Respeito e Bits, **sem herança de stats no motor** | stats melhorados na rodada seguinte. Uma das duas tem de mudar, ou a herança vale só fora do ranking |
| **um parceiro só** | o pilar P1 do GDD do parceiro: um Digimon, um cérebro, um registro | um pet ativo e outro no banco. Cabe se o banco for de vidas passadas ou paradas, e só um viver por vez |
| **a jogress** | a PAR-11 propõe a jogress **temporária**, com um personagem da jornada, por afinidade | a jogress entre o pet ativo e o do banco. Falta decidir se o resultado é permanente e o que acontece com os dois |
| **o cérebro na herança** | os hábitos não passam ao herdeiro (proposta WD-1) | decidir se algo do cérebro passa junto com os stats, ou só os stats |
| **o ranking** | o servidor confere as lutas pelo registro | stats herdados mudam a força de partida; o ranking precisa saber a geração |

## 4. Perguntas para quando a feature abrir

1. O que dispara o fim do ciclo: a morte, uma escolha do jogador num estágio alto, ou os dois?
2. Quanto dos stats passa, e há teto por geração?
3. A jogress consome os dois pets, ou só um? A forma fundida é uma forma do Catálogo de hoje?
4. A jogress pede vínculo com os dois, como a evolução para o Mega pede vínculo com um?
5. O ciclo dá algo além de stats (um feito, uma página do caderno, o memorial)?
