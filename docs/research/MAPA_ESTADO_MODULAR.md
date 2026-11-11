# Mapa do estado interno do DigiBrain modular (pets v17), para o decodificador de conceitos

Levantamento só de leitura sobre `origin/main` em 2026-11-06 (agente Explore a pedido do Gerente da CONVERSA_PET, Opus 5.5). Base da
[ESPEC_DECODIFICADOR_FALA.md](ESPEC_DECODIFICADOR_FALA.md). Os arquivo:linha são de 2026-11-06 e podem ter andado.

## 0. Contexto

- O v17 é o "cérebro trocável" (`web/app/motor/constantes.ts:62-67`); os ovos novos nascem com o modular (`src/cerebro.ts:31-33`), na
  `CONFIG_DIGIBRAIN_LAB` (braço REL da C4): ligados `m_mem`, `memoria_autobio`, `p1`, `p2`, `persistencia`, `cheiro_inato`, `intencao_cheiro`;
  desligados `modula_g_apr` (g_apr constante em 1024), `facetas_mem`, `credito_corrida`, `redecidir_evento`, `intencao_suspensa`, `passeio`.
- A ponte da luta vem ligada nos ovos novos (`src/produto.ts:20`, `motor.ts:406-424`; entrada em `motor.ts:680`).
- Em Python não há "v17": o padrão `ConfigDigibrain()` é todo desligado (`digilab/config.py:2417-2479`); o equivalente do jogo é o braço REL.
- Tudo inteiro na escala S = 1024; uma decisão a cada 15 ticks; nenhuma rng salvo um `rng.random()` no M-ARB.
- No v17 o desejo (`motor.ts:939-942`, `lobos.ts:834-845`) e o caráter (`motor.ts:1150-1151`, `carater.ts:95`) vêm do cérebro A parado; o
  vínculo (`vinculo.ts:51`) e a memória-emoção do Bandit (`m.pol.mem`, `memoria.ts:63-130`) são do jogo; o temperamento não entra no modular.
- Replay: os `motivos` são derivados, nunca no log (`adapt.py:52-53`); a vida se refaz bit a bit, logo todo sinal é recalculável. Custo:
  **M** já está no `motivo`; **E** está no `estadoInterno()` (só o valor atual); **T** é transitório (instrumentar o replay ou refazer a conta).

## 1. Sinais a cada `agir` (ordem: SENS → AFETO → reflexo → ESTADO.contexto → MEM → IMPULSO → ARB → ESTADO.escolhida)

| módulo | sinal | o que é | faixa | onde | persiste |
|---|---|---|---|---|---|
| SENS | `falta[r]`, `leitura[r]` | déficit e nível de 11 receptores (fome, higiene, energia, humor, saude, tedio, curiosidade, solidao, estresse, dor, susto) | 11 × [0, S] | `sens.py:84-85`, `sens.ts:114-115` | T (só `falta_fome` no motivo) |
| SENS | `contexto` noite, dormindo, sem_cuidado | hora, sono, tempo sem cuidado | 0/S; [0, S] | `sens.py:91-92`, `sens.ts:120-123` | só `noite` no motivo |
| SENS | `objetos[i]` id, classe, prox, nov; `hab[c]` | até 8 objetos vistos; habituação por classe | [0, S] | `sens.py:97-103`, `sens.ts:127-132` | T; hab em E |
| SENS | `lutas` | resumos de luta desde a decisão anterior | lista | `sens.py:68-79,109-110`, `sens.ts:98-107,140` | M |
| AFETO | `urgencias[r]`, `contexto.drive` | urgência inata por receptor e o drive dominante | 11 × [0, S] | `afeto.py:63-75`, `afeto.ts:66-81` | M |
| AFETO | `V`, `E` | valência (τ 240) e excitação (τ 120) | [−S, S]; [0, S] | `afeto.py:103-105`, `afeto.ts:115-117` | M e E |
| AFETO | `g_apr`, `g_exp` | ganho de aprendizagem (constante no jogo) e de exploração | [0, 1024] | `afeto.py:76-89`, `afeto.ts:83-98` | M |
| AFETO | `r`, `r_n`, `canais` | sinal homeostático da consequência e a parte de cada drive | [−S, S] | `afeto.py:97-107`, `afeto.ts:108-120` | M (decisão seguinte) |
| ESTADO | `F` | frustração | [0, S] | `estado.py:146-160`, `estado.ts:70,78` | M e E |
| ESTADO | `I*`, `C`, `n_sp`, persistência, `fins` | intenção em curso, compromisso, decisões sem progresso, motivos de fim | chave; [0, S] | `estado.py:144-169`, `estado.ts:52-133` | M e E |
| IMPULSO | `z` | contexto com 23 características nomeadas | 23 inteiros | `impulso.py:58-68`, `impulso.ts:67-74`; nomes em `config.py:2495-2497` | T |
| IMPULSO | unidades e `termos` (inato, prox, nov, incentivo, habito, memoria, persistencia, lembranca), `a` | cada opção com a contribuição de cada módulo | inteiros | `impulso.py:71-148`, `impulso.ts:77-141` | M |
| ARB | `pesos` w, `u`, `reflexo`, `escolha`, `acao` | sorteio e escolhida | inteiros | `arb.py:67-130`, `arb.ts:66-135` | M |
| ARB | chances e margem | w/Σw (já em `leitura.ts:84-87`); margem e entropia não existem | derivado | — | derivável |
| ARB | `sondas` (sem_incentivo, sem_habito, sem_memoria, sem_persistencia, sem_afeto, so_inato, sem_lembranca, `*_decidiu`) | contrafactual com o mesmo u | chave e booleano | `arb.py:117-128`, `arb.ts:112-133` | M |
| MEM | `recuperar` pista, recuperado, lugar, valor | "sei onde tem comida" | inteiros | `mem.py:364-394`, `mem.ts:332-362` | M |
| MEM | `lembrar` recuperado, sim, memoria, sigma; `termo_lembranca` L | lembrança ativa (sim ≥ 768) e o termo que ela soma às opções | id; [0, S] | `mem.py:247-328`, `mem.ts:241-299` | M |
| MEM | episódio autobiográfico | ponto, vista, ação, objeto, dono, corpo antes e depois, V e E, sigma, classe | dicionário | `mem.py:86-119`, `mem.ts:70-106` | E (recente 16, duradoura 32, central 8) |
| MEM | consolidação | uma vez por dia: subiram, esquecidos, voltaram | registro | `mem.py:396-446`, `mem.ts:368-416` | M e E |
| MEM | lutas | episódio de origem `luta` se o corpo mudou o bastante | lista | `adapt.py:256-269`, `mem.py:121-143`, `adapt.ts:236-248` | M e E |
| PLAST | H (hábito P2) | 7 comportamentos × 23 características | [−512, 512] | `plast.py:63-126`, `plast.ts:75-134` | E |
| PLAST | `desfecho` (P1) | efeito previsto de cada classe sobre cada receptor | 6 × 11 | `plast.py:77-108`, `plast.ts:88-116` | E |
| DONO | `gestos` | gestos do dono; nenhum módulo os lê (só o corpo) | lista | `adapt.py:340-343`, `adapt.ts:251-254` | M e E |

## 2. O `motivo` hoje (`adapt.ts` ~143–166 e 345–350)

`k`, `acao`, `escolha`, `tipo_escolha`, `reflexo`, `nada_a_fazer`, `u`; `unidades[]` {chave, termos, a, w}; `afeto` {urgencias, V, E, e_usada,
g_apr, g_exp}; `estado` {I, C, n_sp, F}; `memoria` {pista, recuperado, lugar, valor}; `sondas`; `falta_fome`; `contexto` {drive,
comida_vista, noite}; `fins`; `creditos`; `gestos`; `lembranca` {recuperado, sim, memoria, sigma, L, unidades}; `consolidacao`; `lutas`;
depois `alvo` e, na decisão seguinte, `consequencia` {r, r_n, canais, comeu, chegou, p1, creditos, episodio, autobio}. Falta: o z completo,
faltas e leituras de todos os receptores, prox e nov por objeto, o incentivo por classe, as lembranças perdedoras, V e E depois da consequência.

## 3. O que a fala usa hoje: nada do modular

`estadoDoPet` (`web/app/src/falaLivre.ts:59-89`) lê `m.motivos`, que desde o v11 só recebe motivos do treino (`motor.ts:934`); as decisões do
modular nunca entram ali, e o gatilho "acabei de decidir" não dispara com elas. A emoção e as memórias vêm do Bandit; o desejo e o caráter, do
A parado; a memória autobiográfica nunca é mandada (o servidor aceitaria `memoria_autobio`). Só o painel lê o motivo do modular
(`digibrain/leitura.ts:54-96`).

## 4. Conceitos que os sinais já sustentam (sem treino)

Fome, sono, bem-estar ou mal-estar, agitação, aversão aprendida, frustração, determinação, indecisão, lembrança ativa, solidão, curiosidade;
mais hábito, gosto aprendido e "fiz por acaso" (chance baixa e nenhuma sonda decidindo). Sinais de cada um na espec, seção 2.

## 5. Lacunas

Não há intenção de comunicar (`chamar_atencao` sem conteúdo), afeto pelo dono (a faceta `apego_dono` está desligada e falha alto em TS),
medo de punição ligado ao dono, emoção com nome no modular, modulação química da aprendizagem no jogo, modelo de mundo além do `desfecho`, nem
incerteza calibrada. **Achado:** a lembrança de luta pode ser recuperada, mas nunca casa com uma opção (`mem.ts:284`): é registro, não causa.

## 6. Legibilidade

Quase tudo é nomeado e inteiro (z com 23 nomes, 7 comportamentos, W0 por pares nomeados, H 7 × 23, desfecho 6 × 11, termos e sondas
nomeados): um gargalo de conceitos é quase trivial, com o risco de só redescobrir as entradas. Menos legíveis: o clamp em 4096, o sorteio u,
as lembranças perdedoras, a mistura de sentidos nas leituras e o crédito P2 com elegibilidade fora do `estadoInterno`. Docstrings
desatualizadas: `mem.py:46-47` e `adapt.py:16-17` dizem que nenhuma decisão lê a lembrança, mas o termo entra em `impulso.py:137-138`.
