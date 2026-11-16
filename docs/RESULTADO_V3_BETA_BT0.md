# RESULTADO V3 — BETA, BT0: o tempo de relógio do ovo ao primeiro Mega (2026-11-16, Claude Code, Opus 5.5)

**A etapa:** a BT0 do [PLANO_V3_BETA.md](PLANO_V3_BETA.md) (seções 3 e 7; BT-3 DECIDIDA). Mede quanto tempo de relógio um jogador novo
leva do ovo ao primeiro Mega, o marco 10 do Tamer (`web/app/src/nivel.ts`, `ULTIMO_MARCO = 10`), onde o multijogador abre (MMO-13). É uma
medida de engenharia: o motor, o save e as versões de pet não mudam, e nenhuma chave de beta é implementada. As sementes saem de
`hashSemente("bt0", ...)`, fora das faixas reservadas. Os perfis, as sessões e os tempos fixos são **PROPOSTOS, SEM FONTE**. O desvio está
no `docs/registro/2026-11.md`, seção "BETA: a BT0" (D-CONTA-60 a D-CONTA-65).

**Para refazer:**

```bash
cd web/app && node scripts/medir_bt0_mega.ts
```

O comando grava `web/app/scripts/medicoes/bt0_mega.json` (versão da medida 1, commit `f1a53288`, 526 s). O teste fica em
`web/app/test/medir_bt0_mega.test.ts`.

## 1. Como foi medido

**A vida, em tempo de jogo.** O jogador novo recebe os dois ovos (`DOIS_OVOS_LIGADO`, o `GrupoDoJogo` da `VERSAO_GRUPO`, como o
`chocarDoisOvos`): o primeiro do brasão escolhido, um brasão por espécie, no ritmo "rápida" e com o produto ligado. O dono é o de cada
perfil da CN0 (`PERFIS` do `medir_cn0_save.ts`): ele cuida, treina, luta na arena e tenta um líder por pet e por dia de jogo. No fim de
cada dia, o Tamer confere as medalhas e os pets as recebem (como a CN0). A vida acaba no primeiro Mega ou em 60 dias de jogo. São 3 vidas
por perfil e espécie, 72 vidas ao todo, em duas variantes do dono:
- **cn0:** o dono da CN0 como está;
- **chips:** o mesmo dono, que também equipa os chips das medalhas nas vagas livres (o cartão do marco 5).

"Chegar" a um estágio quer dizer que o primeiro dos dois pets chegou: o marco é do jogador.

**O relógio.** O tempo do pet só anda com a aba aberta (D-CONTA-38, `src/tempo.ts`). O tempo **aberto** até um estágio é a soma de:
- os minutos de jogo divididos pela velocidade;
- o palco das lutas (o relógio da arena, medido luta a luta; o tempo não anda durante a luta);
- 8 s de Resultado por luta;
- o atendimento de cada chamado do bebê (com o tempo em 1x): 10 s para o dedicado, 60 s para o casual.

Os dias de relógio são esse tempo dividido pelos minutos abertos por dia. A TV não muda a velocidade. O treino e o cuidado não seguram o
tempo.

**As hipóteses** (`hipoteses` do JSON, PROPOSTAS, SEM FONTE):

| perfil | o dono (CN0) | por dia de jogo | sessões por dia de relógio |
|---|---|---|---|
| **dedicado** | atencioso, a cada 15 min de jogo | 3 treinos, 4 lutas, 30 min de TV | 4 × 30 min (2 h) |
| **casual** | relapso, 3 visitas | 1 treino, 1 luta, sem TV | 2 × 15 min (30 min) |
| **TV longa** | atencioso | 3 treinos, 4 lutas, 2 h de TV | 4 × 30 min (2 h) |

A velocidade principal é a de 10 min/s, a do jogo ao abrir. O JSON também dá 1x, 1 h/s e 6 h/s, e uma grade de 15 a 240 min abertos por
dia (`gradeMega`).

## 2. O tempo até cada estágio

A mediana entre as vidas que chegaram, a 10 min/s, com as sessões do perfil (`tabela[]`, `brasao: "todas"`, variante cn0):

| perfil | estágio | chegaram | dias de jogo | dias de relógio | dias de relógio a 1x |
|---|---|---|---|---|---|
| dedicado | Rookie | 12/12 | 0,13 | 0,02 | 1,5 |
| | Champion | 11/12 | 1,02 | 0,07 | 12,3 |
| | Ultimate | 10/12 | 5,61 | 0,33 | 67,6 |
| | **Mega** | **2/12** | 13,17 | **0,77** | 158,6 |
| casual | Rookie | 12/12 | 0,13 | 0,46 | 6,5 |
| | Champion | 12/12 | 1,00 | 0,58 | 48,5 |
| | Ultimate | **0/12** | — | — | — |
| | **Mega** | **0/12** | — | — | — |
| TV longa | Rookie | 12/12 | 0,13 | 0,02 | 1,5 |
| | Champion | 11/12 | 1,08 | 0,08 | 13,1 |
| | Ultimate | 9/12 | 6,58 | 0,37 | 79,2 |
| | **Mega** | **1/12** | 10,92 | **0,61** | 131,4 |

**Por espécie** (o Mega, variante cn0): o dedicado chega com Coragem (brasa, 1/3, 1,01 dia de relógio) e Amizade (cirro, 1/3, 0,54 dia),
e nunca com Conhecimento (ferrugem, 0/3) nem com Sinceridade (limo, 0/3). O TV longa só chega com Amizade (1/3). O casual não chega com
nenhuma. Com a variante **chips**, o dedicado também faz 2/12, mais cedo (mediana de 9,29 dias de jogo e 0,55 de relógio); o casual
continua em 0/12.

## 3. Quantos chegam ao Mega em 3 e em 7 dias de relógio

A 10 min/s, com as sessões do perfil (`megaNaVelocidadePadrao`):

| perfil | variante | até 3 dias | até 7 dias |
|---|---|---|---|
| dedicado | cn0 | 2/12 | 2/12 |
| dedicado | chips | 2/12 | 2/12 |
| casual | cn0 e chips | 0/12 | 0/12 |
| TV longa | cn0 e chips | 1/12 | 1/12 |

**A 1x, ninguém chega em 7 dias:** o Mega pede de 110 a 207 dias de relógio. Pela grade, a 10 min/s, os dedicados que chegam ao Mega chegam
em 3 dias com 30 min abertos por dia ou mais (os 2, nas duas variantes). Com 15 min por dia, chega 1 dos 2 em 7 dias na variante cn0, e os
2 na chips.

## 4. A leitura

- **O relógio não é a trava na velocidade padrão.** Quem chega ao Mega chega com 1 a 2 horas abertas, em menos de um dia de relógio. A
  maior parte desse tempo é o palco: 136 lutas e 59 min de palco na vida mais longa (o dedicado de Coragem, `vidas[]`).
- **A trava é a 4ª medalha, a Cidadela.** O Myotismon pede uma série de três vitórias. Contra ele, o dedicado venceu 2 de 778 tentativas (cada tentativa é uma série de três lutas);
  o casual, 0 de 969 (`tabela[].porLider`, `npc_v5_myotismon`). A Floresta (Youkomon) já é difícil: o dedicado ganhou 20 de 184. Quase
  todas as vidas param em 3 medalhas, no marco 7, e o dedicado, no Ultimate. O casual não passa do Champion: o Ultimate pede as 3 medalhas
  **e** 80 % de vitórias (`CLE.limiarTaxa`).
- **O marco 9 vem depois do Mega.** O 9 é o título da Liga (6 medalhas); o Mega pede 5. Nenhuma vida chegou ao marco 8 nem ao 9. **A chave
  "o cais a partir do nível 9" da seção 3 do plano não adianta nada:** quem chegasse ao 9 já teria passado pelo 10.
- **Os marcos de antes chegam cedo** (`tabela[].marcos`, variante cn0):

| perfil | o marco 6 (Champion) | o marco 7 (3 medalhas) | até 3 dias de relógio | até 7 dias |
|---|---|---|---|---|
| dedicado | 11/12, 0,07 dia | 11/12, 0,31 dia | 11/12 no 7 | 11/12 no 7 |
| casual | 12/12, 0,58 dia | 12/12, 1,07 dia | 12/12 no 7 | 12/12 no 7 |
| TV longa | 11/12, 0,08 dia | 11/12, 0,38 dia | 11/12 no 7 | 11/12 no 7 |

**O que a medida não diz:**
- o dono simulado não usa as cartas de revanche, não escolhe o líder nem o exercício, e não usa o Forçar. Um jogador de verdade pode ir
  melhor contra o Myotismon (ou pior, se cuidar menos);
- 3 vidas por perfil e espécie bastam para ver a trava, não para estimar uma taxa;
- **achado fora do escopo:** em 6 das 12 vidas do dedicado, um dos pets morre entre os dias 44 e 58 de jogo (`vidas[].morreu`, `dias`).
  A 10 min/s, isso cabe na semana do beta. A causa não foi investigada.

## 5. Decisão para o Matheus

**BT0-1 (DECIDIDA pelo Matheus em 2026-11-16, pela recomendação: "Sim, aceita e mergeia"). A chave do beta abre o cais no marco 7 (3 medalhas), não no 9 nem no 10, só no ambiente do beta.**
- **A recomendação:** no beta, o multijogador abre com as 3 medalhas. Pela medida, 11 dos 12 dedicados e os 12 casuais chegam lá antes do
  3º dia de relógio; no marco 10, chegam 2 de 12 e 0 de 12. A MMO-13 não muda no jogo, e a chave sai depois do beta (BT-3).
- **As outras opções:**
  - **o marco 6** (o Champion): chega mais cedo, mas leva ao ranking pets que ainda não lutaram contra líder nenhum;
  - **o save inicial com um pet crescido:** é a outra opção da seção 3; o beta perde a evolução do ovo ao Mega;
  - **mexer na Cidadela:** é equilíbrio, fica para a rodada de equilíbrio geral, e o motor não muda durante o beta (MMO-14).
- **O custo de errar: alto.**
  - Manter o marco 10 deixa o ranking quase vazio: o critério "15 ou mais dos 20 no ranking" (seção 6) cai pela trava da Cidadela, e não
    pelo relógio.
  - Abrir no marco 7 faz o beta não testar o "Mega abre o multijogador", e põe Champions e Ultimates nas tabelas por estágio (MMO-9). Isso é
    o que o beta mediria da evolução, não um defeito.
- **Junto, uma pergunta para a rodada de equilíbrio (não para o beta):** a Cidadela é uma trava de propósito? Se não for, o jogo aberto (a
  F6) também fica sem ranking.
