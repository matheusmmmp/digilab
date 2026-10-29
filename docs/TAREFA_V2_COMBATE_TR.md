# TAREFA V2 — COMBATE-TR: a batalha em tempo real como o combate do jogo inteiro (2026-10-29)

Coordenador: sessão de coordenação da integração UP (Claude Code). Worker: a definir. Worktree e branch: `v2-combate-tr`. Status: ABERTA
(etapa R0 entregue no #449; D-1 a D-9 DECIDIDAS e etapa R1 liberada pelo Matheus em 2026-10-29).

Categoria: arquitetura (R0) e implementacao (R1–R4). Origem: Matheus, 2026-10-29, no chat da coordenação: "a ideia é a batalha em tempo
real ser a mecânica de batalha do jogo inteiro. Então todas as sessões onde tem batalha, arena e qualquer coisa do gênero, é a batalha
em tempo real", com o pet lutando sozinho ("não é para pressionar botão nenhum") e com as mecânicas da batalha atual (o Guts e o resto).

## 1. Pergunta

O combate por turnos V2.1 (`web/app/motor/combate.ts`) pode ser trocado, em todo lugar do jogo onde há batalha, pela simulação em tempo
real de `web/app/arena/` (UP-ARENA, #446), com o pet lutando sozinho pelas regras dele e com as mecânicas de hoje adaptadas, mantendo o
replay determinístico e tudo o que o resultado da luta alimenta? Nó do produto: batalha (`docs/PRODUTO_VISAO.md`, seção 3).

## 2. Depende de

- UP-ARENA na `main` (#446) e a correção "o pet luta sozinho, sem botões" (PR da UP-ARENA em andamento, branch `v2-up-arena-pet`):
  a R1 parte dela quando estiver na `main`. A R0 não espera.
- UP-ATLAS na `main` (#441): os clipes `Run`, `Attack_1`, `Stun`, `Die`.

## 3. O que já se sabe (o levantamento do coordenador, 2026-10-29)

- **Uma porta só:** toda luta de pet passa por `Motor.lutar(rival, semente, carta)` → `_lutar` → `montarLuta` (`motor.ts`, ~377–583). O
  log grava `[tick, "l", {r, s}]` (e `"k"` para a carta), e o replay **refaz** a luta (`aplicarEvento` "l"). Nada do resultado é guardado.
- **Os lugares:** Arena (bots e formas adultas), Melhor de 10, Campanha e Exploração, líderes das medalhas (arenas v6, com regras por lugar),
  Liga, Torre de Batalha e Palácio (`instalacoes.ts`), Salão, Fábrica (Megas alugados, log do Tamer), sparring dos pets de exemplo,
  Cenário pet e Lab (`jogarV2` fora do log).
- **O que o resultado alimenta:** aprendizado das regras (`GambitsPet.aprender`), `sparring`, `lutas` (vitórias, derrotas, empates),
  `vitoriasVida`, lesão e morte (`hashSemente("lesao")`), confiança M1, `campanha`, `liga`, `salao`, `instalacoes`, `vida5.lutas`, a
  história; a evolução (adulto: sparring ≥ 10 e taxa ≥ 0,8; Mega: ≥ 10 lutas, ≥ 0,8 e vínculo ≥ 0,4; medalhas do Tamer na v6+); as
  medalhas, a revanche, o campeão e os recordes (`src/tamer.ts`).
- **As mecânicas por turnos:** Guts (custo por ação, regeneração, +5 defender, +25 carregar); ações avançar, recuar, golpe rápido,
  preparar pesado → pesado, disparo, defender, esquivar, carregar, fintar; 3 distâncias; interações (aparar, interromper o preparo,
  fuga); 4 técnicas por linha (investida, contra_golpe, marcar, pele_dura); passivas das formas adultas e sombrias; 6 atributos →
  `perfilDe` (hpMax, guts, regen, mPerto, mDisparo, mGuarda) com o multiplicador de estágio; regras SE/ENTÃO (3/5/8 por estágio,
  condições por estágio) com aprendizado; Travar/Vetar do dono; ε (base, sombria, disciplina, experiência, confiança); condição;
  pontos de treino; itens e cartas (Fôlego, Foco, Cura); escala da campanha; limite de 40 turnos e morte súbita a partir do 25.
- **A simulação em tempo real:** sem DOM, passo fixo de 16 ms, limite de 300 s, 4 fluxos de RNG com semente (`derivarSemente("arena",
  …)`), atributos próprios (`hp, atk, def, vel, cad, crit, …`) vindos do `status.json` do UP; IA da CPU fixa em `sim.ts`; nenhuma
  ligação com o `Perfil`, as regras ou o pet; `medicao.lutarAteOFim` já roda em Node. Lutas medidas de ~90–108 s (3 × 3).

## 4. Decisões do Matheus (2026-10-29)

- **E1:** a batalha em tempo real fica só no TypeScript; o determinismo é testado lá (mesma semente e mesmo log, mesmo resultado no
  Node). Sem porte nem paridade Python. O `digilab/combate_v2/` do Python fica como está (pesquisa da v1, congelada).
- **E2 (troca a recomendação):** **os pets e saves anteriores podem ser descartados.** Não precisam continuar válidos nesta etapa de
  desenvolvimento. A versão nova de pet não carrega o combate por turnos. Pela regra do `web/app/CLAUDE.md`, o descarte aparece com
  **aviso na tela** (o save antigo não abre calado como pet novo). Os gabaritos e testes que só existem para as versões antigas podem sair
  junto, com a lista no relato.
- **E3:** a batalha em tempo real pega a próxima versão de pet livre quando entrar na `main` (hoje a v13, reservada no papel para o
  cérebro modular, que ainda é pesquisa); o `docs/ARQUITETURA_DIGIBRAIN_MODULAR.md` registra a troca.
- **E4:** ensinar as regras (Travar, Vetar) fica entre as lutas, na tela Crescer. Durante a luta, nenhum controle.
- **E5:** os atributos da luta são os do DigiLab (treino, caráter, forma, estágio: `statsDe` / `perfilDe`). Do Digimon UP vêm só a
  animação, o instante do golpe, o projétil e o efeito.
- **E6:** sempre 1 contra 1. Liga, Torre, Palácio, Fábrica e Salão continuam como sequências de 1 contra 1.
- **E7:** os mapas da arena do UP viram o cenário de cada lugar, com as regras de ambiente (maré, lava, ringue…) **desligadas** até a
  rodada de equilíbrio.
- **Valem também:** a pilha do jogo não muda (nenhuma versão, nenhuma dependência nova); os assets do UP pela regra 5.1; números novos
  PROPOSTOS, e o equilíbrio só numa rodada no fim (a memória "equilíbrio só no fim").

## 5. Etapas (cada uma um PR; parar e mostrar ao fim de cada uma)

### R0 — a especificação (arquitetura; sem código de jogo)

`docs/ESPEC_COMBATE_TR.md`, com:
1. **A tabela mecânica por mecânica** da seção 3: como cada uma vira tempo real (o Guts como barra que gasta por ação e volta por
   segundo; as ações como movimento, golpe, projétil, preparo interrompível, reação; as 3 distâncias como faixas de distância real; as
   técnicas como habilidades com recarga; as passivas como modificadores; o limite e a morte súbita por tempo), com os números PROPOSTOS
   de partida e a fonte de cada um (o valor por turnos convertido, ou SEM FONTE).
2. **O pet como controlador:** as regras SE/ENTÃO avaliadas num ritmo de decisão fixo (proposta: um número de passos), a primeira válida
   decide; o ε com a RNG de política própria; as condições do catálogo reescritas para o tempo real (distância, Guts, vida, intenção do
   rival…). O rival (bot, NPC, líder, Mega) usa o mesmo controlador com a lista dele.
3. **O aprendizado e os efeitos:** o que `GambitsPet.aprender` recebe da luta em tempo real (o saldo de dano por regra disparada), e a
   lista de tudo o que o resultado alimenta (seção 3), igual a hoje.
4. **O log e o replay:** o evento da luta (proposta: o mesmo `"l"`), a semente, as RNG separadas (ambiente/combate × política), e **a
   medida do custo:** refazer uma vida com N lutas de ~100 s (~6 000 passos cada) no Node e no Chrome. Se o custo não couber, a proposta
   (luta mais curta, passo maior só no replay não serve porque muda o resultado, cache do resultado por evento…), com a recomendação.
5. **Onde a simulação mora:** hoje em `web/app/arena/`, fora do `motor/`; o motor precisa chamá-la no replay. Propor mover o núcleo para
   `motor/` (sem DOM) ou o motor importar `arena/`, e o que sai da UP-ARENA (os 3 × 3, a troca, o modo jogador).
6. **O descarte (E2):** a versão nova, o aviso na tela, o que sai do motor e dos testes (o combate por turnos, os gabaritos v21d/v21e,
   as vidas v1–v12), em que etapa sai, e o que fica (o Python, congelado).
7. **As telas (R3) e os modos (R4):** cada lugar da seção 3 → qual tela desenha a luta, qual cenário do UP (E7), o que a Fábrica (Megas
   alugados, log do Tamer) e o Salão precisam.
8. **As decisões abertas** para o Matheus, cada uma com a recomendação e o custo de errar.

### R1 — o núcleo

A luta 1 × 1 sem tela, comandada pelas regras do pet e do rival, com os atributos do DigiLab (E5), o Guts e as técnicas, determinística
(teste de semente no Node), atrás de chave desligada. Um script mede a duração e o custo por luta.

### R2 — o motor

A versão nova de pet (E3): `Motor.lutar` usa o tempo real; o aprendizado, a evolução e todos os contadores da seção 3 funcionam; o replay
refaz igual; o descarte dos saves antigos com aviso (E2).

### R3 — as telas

Todo lugar de batalha desenha a luta em tempo real com os clipes do UP e o cenário do lugar (E7); saem o `PalcoLuta` por turnos e a tela
separada da arena do UP; sem controles durante a luta; o resultado e o "por quê" (as regras que dispararam) depois.

### R4 — os modos especiais e as cartas

Liga, Torre, Palácio, Fábrica, Salão; as cartas (Fôlego, Foco, Cura) e os chips escolhidos antes da luta.

### Depois — a rodada de equilíbrio

Fora desta tarefa: depois da R4, com plano próprio.

## 6. Mudança mínima e fronteiras

- **Não muda:** `digilab/engine.py`, o pacote Python (inclusive `combate_v2`), a pilha do jogo (`package.json` e lockfile iguais).
- **Muda só a partir da R1**, cada etapa no seu PR. A R0 só escreve a espec e mede o custo do replay (o script de medida pode entrar).

## 7. Entrega

- R0: `docs/ESPEC_COMBATE_TR.md`, a medida do custo com o script e a saída em disco, a seção no fim desta tarefa, o registro em
  `docs/registro/2026-10.md` e a linha no índice `docs/REGISTRO_DESVIOS.md` com o **mesmo título** da seção (o job `testes` roda
  `python tools/conferir_saude.py`).
- R1–R4: `npm test`, `npm run tipos`, `npm run e2e`; o teste de determinismo; capturas das telas.
- PR contra a `main` por etapa, com o relato no corpo pelo `.github/pull_request_template.md`. Merge só pelo Matheus.

## 8. Fora desta tarefa

A paridade Python (E1); a rodada de equilíbrio; equipes de 3 (E6); as regras de ambiente das arenas (E7); o cérebro modular; ligar a
luta ao corpo químico além do que o combate já faz hoje.

## 9. Critérios de aceitação da R0

1. A espec cobre cada mecânica e cada lugar da seção 3, sem buraco (uma linha por item, com "como fica" ou "sai, porque…").
2. Cada número tem PROPOSTO e a fonte (ou SEM FONTE).
3. O custo do replay está medido no Node e no Chrome, com o script e a saída em disco, e a recomendação é coerente com o número.
4. As decisões abertas vêm com a recomendação e o custo de errar.
5. Nenhum código de jogo mudou.

## 10. R0: o resultado (worker, Claude Code, Opus 5.5, 2026-10-29)

A especificação está em `docs/ESPEC_COMBATE_TR.md`, toda PROPOSTA. Nenhum código de jogo mudou.

- **A luta continua sendo do DigiLab, com outro relógio.** O turno vira um tempo de ação T = 2 s (o ciclo de ataque padrão do protótipo).
  - Cada ação ocupa o lutador por T, e os dois lados agem sem se esperar.
  - As 3 distâncias viram faixas de distância real: perto até 62 px, médio até 150 px.
  - O limite é de 80 s, e a morte súbita começa aos 50 s.
  - O Guts, as técnicas e as passivas mantêm os números de hoje, convertidos por T.
- **O controlador** é o `decidirV2` de hoje, com as condições reescritas para o tempo real. Ele decide quando o lutador fica livre, num
  ritmo de 16 passos (256 ms), e dá uma decisão por ação, com o ε uma vez por decisão. O rival usa o mesmo controlador.
- **O aprendizado** recebe o saldo de dano por ação, no lugar do saldo por turno. Tudo o que o resultado alimenta continua igual (a tabela
  da seção 3 da espec).
- **O log** guarda o mesmo `"l"`, e o replay refaz a luta. Só o ε sorteia, numa RNG de política por lado, e fica reservado um fluxo de
  combate vazio.
  - **Risco novo:** a aritmética entre navegadores. A proposta é usar no núcleo só + − × ÷ e `sqrt` (D-7).
- **O custo**, medido sobre a simulação de hoje (`web/app/scripts/medir_replay_tr.ts`, a saída em
  `web/app/scripts/medicoes/replay_tr.json`):
  - a luta de 100 s custa 4,66 ms no Node e 3,08 ms no Chrome, cerca de 50 vezes a luta por turnos;
  - 500 lutas custam 2,3 s e 1,5 s, e 1 000 lutas, 4,7 s e 3,1 s;
  - o Node e o Chrome deram as mesmas lutas;
  - **a recomendação é refazer sempre, sem cache** (D-2).
- **A simulação mora num núcleo novo, em `motor/combate_tr/`,** sem os dados do UP. Assim, o replay não depende da pasta `Assets/`. A
  `arena/` sai na R3.
- **O descarte:**
  - a v13 entra na R2, com o aviso na tela e a opção de baixar o arquivo do pet;
  - os ramos das versões antigas saem na R2, e o combate por turnos sai na R3;
  - a paridade do cérebro A, do corpo e do mundo fica, e o Python fica congelado.
- **As decisões abertas são nove, de D-1 a D-9**, cada uma com a recomendação e o custo de errar (a seção 8 da espec). A principal é a D-1:
  o tempo das ações vem do DigiLab, e não do UP.

O desvio e as interpretações estão em `docs/registro/2026-10.md`. A R1 espera a resposta do Matheus.

## 11. R1: o resultado (worker, Claude Code, Opus 5.5, 2026-10-29)

O núcleo da luta em tempo real está em `web/app/motor/combate_tr/`, sem tela e atrás da chave `COMBATE_TR`, desligada. Nenhuma luta do
jogo passa por ele: o `Motor.lutar` só o liga na R2. As decisões D-1 a D-9 foram aceitas pelo Matheus como recomendadas (seção 8 da
espec).

- **O que entrou:**
  - `constantes_tr.ts` traz o relógio e o espaço. O T de 2 s (125 passos), o limite de 80 s e a morte súbita aos 50 s são DECIDIDOS
    (D-5); o resto é PROPOSTO, com a fonte ou SEM FONTE.
  - `controlador.ts` traz a legalidade, as condições do catálogo em tempo real e a decisão (o `decidirV2` de hoje).
  - `luta.ts` traz o estado, o passo de 16 ms e o `jogarTR`, com as mesmas opções do `jogarV2`: as regras V21E, o começo dado, o
    desafiado e a carta de Cura.
  - O `motor/index.ts` exporta o núcleo.
- **A luta é a do DigiLab:**
  - o perfil é o do `perfilDe` (E5);
  - o Guts tem custo, regeneração por T e os bônus da defesa e do carregar;
  - as ações, as quatro técnicas e as passivas usam os números de hoje (`CV`, `CV21`, `CSO`);
  - as interações de hoje ficam: o parry, a interrupção do preparo, a esquiva, o contra-golpe, a marca, a pele dura, a sentinela e o
    vigia.
  - Os dados do UP não entram (D-1).
- **O controlador:** o lutador livre decide no passo múltiplo de 16, e há uma decisão por ação. O ε usa uma RNG de política por lado,
  e o oráculo falha alto (D-6).
- **O saldo de cada ação** (o causado menos o recebido, sobre a vida do começo) sai no resultado, para o `aprender` da R2.
- **Os testes:**
  - `web/app/test/combate_tr.test.ts` cobre a chave, o determinismo por semente nas 64 lutas das formas adultas e a semente que não muda
    nada sem ε;
  - cobre também as RNG separadas e as mecânicas (o parry, a interrupção, a esquiva, o Guts, o limite e o desafiado, a cura e o começo
    dado, a escala e o oráculo), o saldo que fecha com o dano e o motivo de cada ação;
  - `web/app/test/combate_tr_sem_dom.test.mjs` confere o núcleo sem DOM, sem relógio e sem `Math.random`, a aritmética da D-7 e as
    importações.
- **A medida:** `web/app/scripts/medir_combate_tr.ts`, com a saída em `web/app/scripts/medicoes/combate_tr.json`. Foram 560 lutas: as
  8 formas adultas umas contra as outras e os 6 bots clássicos contra elas, cada par em 5 sementes.
  - **A duração:** média de 46,9 s, mediana de 45,1 s e p90 de 80 s; 483 lutas acabaram por KO e 77 no limite.
  - **O custo:** 0,86 ms por luta e 1,47 ms por luta no limite, no Node 24. Refazer 1 000 lutas leva 0,86 s. Uma luta por turnos, nos
    mesmos pares, leva 0,094 ms.
  - É menos que a estimativa da R0 (4,7 ms por luta de 100 s, sobre a simulação do UP), porque a luta é mais curta e não tem a IA nem a
    geometria do UP.
  - Nada foi calibrado.

As interpretações do worker estão em `docs/registro/2026-10.md`. A R2 (o `Motor.lutar`, a v13, o descarte com aviso) espera o Matheus.
