# PLANO_ANALISE_V3_EQUILIBRIO_CUIDADO: o plano de análise da rodada de equilíbrio do cuidado

Fase: V3. Frente: EQUILIBRIO_CUIDADO. Data: 2026-11-12. Worker: Claude Code (Opus 5.5), branch `v3-equilibrio-e0`.
Estado: **registrado antes de qualquer vida.** O plano da rodada é o `docs/PLANO_V3_EQUILIBRIO_CUIDADO.md` (EQ-1 a EQ-8 DECIDIDAS,
2026-11-12). Este documento cobre o **E0, o retrato de hoje**. As metas da seção 6 são **PROPOSTAS, SEM FONTE**: o Matheus as aprova
junto com o retrato (EQ-3), antes da calibração (E1).

**Nenhum número do jogo muda no E0.** A bancada só lê o motor.

## 1. Os pets

Os dois ovos novos de hoje, os dois com o DigiBrain modular (o padrão dos ovos novos, `src/cerebro.ts`):

| pet | constante | versão hoje | o que é |
|---|---|---|---|
| o grupo do ovo do brasão | `VERSAO_GRUPO` | **v36** | a v31 (o grupo de dois, o sono que segura, a luta da LP6, o lance do dono) com a TV no cérebro e no jogo |
| o ovo de um pet | `VERSAO_PET` | **v35** | a v30 (um pet, o sono que segura, o lance do dono) com a TV no cérebro e no jogo |

O pedido falava da v31 e da v32. A main andou: o `VERSAO_GRUPO` é a v36 e o `VERSAO_PET` é a v35 desde a TV no jogo (D-GV-TVJOGO-10).
A bancada usa as constantes, que são o que o jogador choca hoje. As duas têm o lance do dono (`nasceComLance`). Desvio D-EQ0-1.

**A montagem do ovo** é a do jogo (`src/jornada.ts`, `src/produto.ts`, `src/cerebro.ts`), refeita na bancada com as chamadas do motor,
porque o `src/produto.ts` puxa o `src/cerebro.ts`, que lê o `localStorage`:
- o pet: `new Motor(s, VERSAO_PET)`; o grupo: `new GrupoDoJogo(s, VERSAO_GRUPO)`, e cada pet dele pelo `g.agir`;
- em cada pet, na ordem: `ligarProduto({ chamadoPelaFome: true, decisaoNaComida: true, chamadosPeloCorpo: true })`,
  `trocarCerebro("modular")` e `ligarPonteLuta(true)`;
- o ritmo "rapida", o padrão: nenhum `configurar`.

**A TV:** a bancada não manda o evento `st`. A TV fica sem imagem a vida inteira (a fonte "evento" antes do primeiro evento). O dono
roteirizado não usa a TV, que não está entre as quatro ações do EQ-4.

## 2. Os donos roteirizados (EQ-4)

Só as ações do jogador: **alimentar** (`observar("alimentar")`, que põe uma ração no comedouro), **limpar**, **carinho**
(`acariciar`) e **brincar** (o lance do dono). Nenhum dono luta, treina, sacode árvore, deixa bola ou leva o pet.

**O limiar de cada estágio** (os números são os do jogo, nada novo):
- no In-Training (o `bebe` do motor): os do chamado do bebê, `CHAMADO_BEBE_CORPO` = fome 0,7, higiene 0,9, humor 0,8;
- do Rookie em diante: os do cuidado na hora certa, `CUIDADO_NA_HORA` = fome 0,45, higiene 0,25, humor 0,25. Do Rookie em diante o jogo
  não abre chamado, e esse é o único limiar com que o jogo reconhece o cuidado que faz falta (é o que paga Bits).

**A ação de cada falta:** fome abaixo do limiar → alimentar (uma ração); higiene abaixo → limpar; humor abaixo (o chamado de carinho) →
brincar se o pet está acordado, carinho se está dormindo. O brincar também atende o chamado de carinho (`ACAO_CHAMADO`).

**As regras exatas.** Em cada tick `t` da vida (`t` = minutos desde o ovo), o dono age **antes** do avanço de 1 tick:

- **o atento** olha todo tick:
  - no In-Training, atende cada chamado aberto (`chamadosAbertos()`) no tick em que ele aparece, com a ação do tipo dele;
  - do Rookie em diante, age em cada falta pelo limiar do Rookie, com no máximo uma ação de cada tipo a cada intervalo do chamado
    (`CHAMADO_BEBE`: fome 30 min, higiene 60 min, carinho 45 min), o mesmo espaçamento que o jogo dá aos chamados do bebê. Sem o
    espaçamento, o atento poria uma ração por minuto enquanto a fome está abaixo de 0,45;
- **o médio** olha nos ticks `t` múltiplos de 120 (2 h de jogo), a partir de `t = 120`, e faz o que estiver faltando pelo limiar do
  estágio, uma ação de cada tipo por visita;
- **o relapso** faz o mesmo nos ticks `t` múltiplos de 360 (6 h de jogo).

O médio e o relapso leem só o corpo: eles não sabem se o chamado ainda está aberto, e não olham se já há ração no comedouro.
No grupo, o dono faz a mesma conta para cada pet, primeiro o `A` e depois o `B`, cada um pelo `g.agir`.

## 3. A janela

Do ovo até o fim do 3º dia de jogo: 3 × 1 440 = **4 320 ticks** (minutos), no ritmo "rapida". O ovo nasce no `TICK_INICIAL` (8 h).
O dia `d` do pet (1, 2 ou 3) é `floor(t / 1 440) + 1`.

**Os estágios no ritmo "rapida"** (`DUR_EVO`): o In-Training dura 180 min (3 h); o Rookie dura 720 min (12 h) até cumprir o tempo do
Champion (o tick 900 do pet, no dia 1). A passagem para o Champion pede também **1 medalha do Tamer** (`CMD.adolescente`), e a medalha
só sai de luta. **Nenhum dono do EQ-4 luta**: o pet fica no Rookie até o fim da janela. Por isso as medidas saem por estágio e por dia nas
células que existem: (In-Training, dia 1), (Rookie, dia 1), (Rookie, dia 2), (Rookie, dia 3). O Champion não entra no retrato. Desvio
D-EQ0-2.

Os nomes: o pedido fala de "bebê, In-Training, Rookie". Na tela, o `bebe` do motor é o In-Training, o `crianca` é o Rookie e o
`adolescente` é o Champion (`NOME_ESTAGIO_FALA`). O retrato usa os nomes da tela.

## 4. As medidas

Por (versão, dono, semente, pet) e por célula (estágio, dia):

| medida | como |
|---|---|
| fração da ração comida | as rações postas pelo dono na célula (o registro `deixadas` do mundo do pet) que algum pet comeu até o fim da vida (os `consumos` de todos os pets do mundo, pelo id), sobre as postas. No grupo, também a fração comida pelo próprio pet |
| tempo com fome alta | minutos com `fome < 0,25` na célula; e minutos com `fome < 0,45` |
| saúde no fim do dia | a `saude` do pet no último tick de cada dia |
| cochilos e energia ao acordar | os cochilos que começam na célula (a passagem de acordado para dormindo) e a mediana da `energia` no tick antes de acordar |
| explorar e brincar | a fração das decisões do cérebro na célula (o `acoesPet` do laço) que são `explorar` e as que são `brincar` |
| chutes por lance | para cada Brincar do dono na célula (o registro `lances` do mundo, do pet), as rolagens da bola no mundo entre o lance e o fim da janela do convite (`janela_convite_ticks`); a média por lance. No grupo, a rolagem pode ser do irmão (o registro não diz quem chutou) |
| Bits | os feitos do pet que valem Bits (`feitosDoPet`, `src/bits.ts`: o chamado do bebê, o cuidado na hora certa, as evoluções, com o teto do dia do jogo) por dia do pet, e os Bits dos níveis do Tamer (30 por nível, `BITS.nivel`) pelos marcos 1, 2 e 3 (`marcosDoPet`, `src/nivel.ts`: chocou, 3 chamados, Rookie), uma vez por Tamer |
| o ★★ contra o Champion | o tick (e o dia) em que o Tamer junta 150 Bits (o preço do portão ★★, `PLANO_V3_MOEDA.md`, seção 3) contra o tick em que o Rookie cumpre o tempo do Champion (`requisitosEvolucao().tempo`); o pet pronto de fato precisa da medalha, que não vem |
| mortes | `m.morte` e o tick. O motor só mata por lesão de luta: sem luta, a morte não acontece; a bancada confere e falha alto se acontecer |

**Os Bits por dia** usam o dia do pet; o teto de 20 Bits de cuidado é por dia do relógio do jogo (`floor(tick / 1 440)`, como no
`src/bits.ts`), que começa às 8 h do pet. A bancada não muda essa conta.

**O Tamer do grupo é um só:** os Bits do grupo são os dos dois pets mais os dos níveis, uma vez.

## 5. As sementes e as faixas (EQ-5)

- **calibração: 93101…93505** e **validação: 94101…94505**, gravadas em `experiments/bancada/faixas.py` (`FAIXAS_RESERVADAS`) com a fonte
  neste documento, antes da primeira vida. Conferidas livres na `origin/main` e nos 30 branches mais recentes em 2026-11-12.
- O E0 usa só a de calibração, com **5 sementes: 93101, 93202, 93303, 93404 e 93505**. A semente é a do ovo (o pet) ou a do grupo (o
  segundo pet sai dela, `sementeDoSegundoJogo`).
- **A de validação não é tocada** no E0 nem no E1.
- O teste da bancada usa uma semente de teste (101…505), 1 dia.

O E0 roda 2 versões × 3 donos × 5 sementes = **30 vidas** (o grupo tem dois pets por vida), em no máximo 4 processos.

## 6. As metas PROPOSTAS (EQ-3)

Todas **PROPOSTAS, SEM FONTE**. "Por dia" é por célula de estágio e dia; o In-Training (3 h) usa a conta proporcional.

| id | medida | meta PROPOSTA | dono |
|---|---|---|---|
| M-A1 | fração da ração comida | ≥ 0,8 em cada estágio | atento e médio |
| M-A2 | fome < 0,25 | no máximo 60 min por dia (0 min no In-Training) | atento |
| M-A3 | fome < 0,25 | no máximo 3 h por dia | médio |
| M-A4 | fome < 0,45 | no máximo 30 % do tempo da célula | atento |
| M-A5 | saúde no fim do dia | ≥ 0,9 (atento), ≥ 0,7 (médio), ≥ 0,3 (relapso: o castigo aparece, mas o pet não chega a 0 em 3 dias) | os três |
| M-B1 | cochilos por dia | de 2 a 6, nos dias 2 e 3 | os três |
| M-B2 | energia mediana ao acordar | ≥ 0,9 (o sono que segura) | os três |
| M-B3 | fração de explorar | ≥ 0,10 das decisões, no Rookie | atento e médio |
| M-B4 | fração de brincar | ≥ 0,05 das decisões, no Rookie | atento |
| M-C1 | chutes por lance | ≥ 0,8 (o G-BB-1) | os três, onde houver lance |
| M-E1 | o ★★ antes do Champion | o Tamer junta 150 Bits até o tick em que o Rookie cumpre o tempo do Champion | atento e médio |
| M-E2 | Bits por dia | ≥ 20 por dia nos três dias | atento |
| M-D1 | mortes | 0 | os três |

A tabela do retrato põe ao lado de cada meta a média das 5 sementes, o mínimo e o máximo e se passa hoje (passa = a média cumpre; o
mínimo vai ao lado para mostrar a pior semente).

## 7. O que sai

- os artefatos: um JSON por vida em `web/app/scripts/medicoes/equilibrio_cuidado_e0/` (o padrão das medidas do jogo, como a LP5), mais o
  `resumo.json` com as tabelas;
- o retrato: `docs/RESULTADO_V3_EQUILIBRIO_CUIDADO_E0.md`, com as tabelas por dono, estágio e versão, as metas ao lado e a seção "O que
  mais pesa para quem joga" (5 itens no máximo, pelos números). Nenhum número sem o artefato.

## 8. O que o E0 não faz

- não muda número nem regra do jogo; não cria versão de pet;
- não luta: o Champion, as vitórias (os Bits da luta) e as medalhas ficam fora do retrato;
- não mede a árvore (o bloco D): o mundo da ilha grande tem as árvores, mas os donos não sacodem; a fruta que o pet come sozinho entra só
  como consumo, fora da fração da ração.
