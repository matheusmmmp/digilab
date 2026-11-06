# TAREFA V3 — SPRITES_REACOES (2026-11-06)

Coordenador: o Gerente da missão SPRITES_GERACAO (Claude Code, Opus 5.5). Worker: a definir por etapa. Worktree e branch: `v3-sprites-reacoes`.
Status: ABERTA. D-RE-1 a D-RE-4 DECIDIDAS em 2026-11-06; a R1 (o Dormir) gerada para os 60, falta levá-la ao jogo (seção 9).

Categoria: arquitetura. Origem: Matheus, 2026-11-06. O pedido foi listar as reações, as ações e os emotes que faltam ao pet, com base em
jogos do gênero e nas folhas do Digimon Battle Spirit, antes de desenhar. Depois ele acrescentou que o **dormir vem primeiro, para todos os
pets**: "Nem que seja só ele de olho fechado, com um ZZZ passando na cabeça".

## 1. Pergunta

Quais reações, ações e emotes faltam ao pet para que o estado dele se leia na tela, e em que ordem e a que custo entram para os 60 Digimon
das formas?

A tarefa é de produto (a trilha L, layout e vista), não uma hipótese de pesquisa. Nada muda no motor, no log nem no replay: tudo é vista.

## 2. Depende de

- **O pipeline da SPRITES_GERACAO** (`docs/TAREFA_V3_SPRITES_GERACAO.md`, G1 na `main` pelo #591, G2 no #594):
  - o still mestre por Digimon;
  - a edição de pose (`master_still.py edit`, o Nano Banana 2 edit no fal.ai, US$ 0,08 por imagem, preço lido em 2026-11-06);
  - a limpeza na grade do UP (`limpar.py`) e os gates.
- **A regra de custo do Matheus (2026-11-06):** cada reação nova é a **pose-chave da emoção** e no máximo um movimento simples feito na
  vista. Vídeo só se a pose sozinha não ler. As palavras dele: "Apenas os braços e o olho já de brabo já tinha bastado"; "como são muitos
  Digimons, a gente quer manter um número ok, sem altos gastos".
- **A decisão D-SG-6 (b) da SPRITES_GERACAO:** o Matheus envia os quadros do UP ao fal.ai sob a responsabilidade dele. Ela vale para estas
  poses, que partem dos mesmos quadros.
- **O lote 1 da SPRITES_ACOES** (#597) e a etapa "Emburrar no jogo" (branch `v3-sprites-emburrar`): o caminho de um clipe novo até o jogo
  (o atlas e o `papel.ts`) que as reações seguem.

## 3. Mudança mínima

### 3.1 O que o jogo já tem (levantado em 2026-11-06 na `main`)

| tipo | o que há | onde |
|---|---|---|
| clipes do UP | Idle, Run, Attack_1, Stun, Die, Evol | `web/app/src/atlas.ts` |
| clipes de ação | o Comer no jogo; o Feliz, o Sacudir, o Chamar e o Emburrar no export (lote 1) | `remaster/acoes/export` |
| emotes do atlas | carne, nota, exclamação, coração, surpresa | `cenaAcao.ts` (`EMOTE_ATLAS`) |
| emotes em grade | zz, raiva, pergunta, brilho, gota | `grades.ts` |
| o dormir | o Idle parado, **de olho aberto**, achatado, respirando devagar, com o tom apagado e o "zz" subindo | `telas/pet/sono.ts` |
| o que o motor sinaliza | as 7 ações do pet (à toa, dormir, comer, brincar, chamar, explorar, emburrar); as ações do dono (alimentar, limpar, brincar, acariciar, tapa, tratar); a sujeira subindo (o cocô, que a vista já vigia em `vigiarCoco`); a vitória e a derrota no combate; a lesão, o cansaço, a evolução e a morte | `web/app/motor` |

### 3.2 As referências

- **As folhas do Digimon Battle Spirit** (GBA e WonderSwan Color, ripadas por Ploaj e por A.J. Nitro; o Matheus as passou na sessão de
  2026-11-06) para o Agumon, o Gabumon, o Veemon e o WarGreymon. Elas têm Idle, Walk/Run, Jump, Bounce, Stop, Guard, Hurt, Knockback,
  Recover, Burned, Shocked, Stunned, Taunt, **Win** e **Lose**. O que serve aqui:
  - o Win tem personalidade (o Agumon de peruca afro, o Veemon de punho para cima), não é só um pulo;
  - o Lose afunda e encolhe;
  - o Taunt do Agumon na versão de WonderSwan Color tem um **cocô** roxo.

  Elas servem **só de referência de ideia e de leitura**. Os desenhos saem do nosso pipeline, a partir do still de cada Digimon, e nenhum
  quadro das folhas entra no jogo.
- **Jogos do gênero, da memória do Gerente, SEM FONTE verificada:** Tamagotchi (cocô, doença com caveira, recusa de comida, bronca);
  os V-Pet de Digimon (cocô, doente, lesionado, pose de vitória e de derrota); Digimon World 1 (cocô, sono, doença, reação ao elogio e à
  bronca); os retratos de emoção do Pokémon Mystery Dungeon (feliz, dor, bravo, preocupado, triste, chorando, surpreso, tonto, suspiro);
  Nintendogs e Pokémon Amie (carinho, sono, sujeira).

### 3.3 A lista proposta

Todos os custos são PROPOSTOS e usam a regra de custo da seção 2. A pose custa US$ 0,08 por take, com 1 a 3 takes por Digimon, o que dá
de US$ 5 a 14 para os 60 por reação. A conversão usa US$ 1 = R$ 5,50, A CONFIRMAR. O emote custa zero: é desenhado uma vez, em grade de
pixel, e serve para todos.

**Prioridade 1, o dormir (pedido do Matheus):**

| reação | gatilho (já existe) | a pose | o movimento e o emote |
|---|---|---|---|
| **Dormir** | `m.acao === "dormir"` | os **olhos fechados**, de preferência sentado ou deitado e encolhido; a pose de cada Digimon sai do still dele por edição | a respiração do `sono.ts` (o achatamento devagar) e o "zz" que já existe; nada de vídeo |

**Prioridade 2, o que o motor já sinaliza e todo jogo do gênero tem:**

| ação | gatilho | como |
|---|---|---|
| Fazer cocô | a sujeira sobe (`vigiarCoco`) | a pose agachada e o cocô no chão, desenhado uma vez para todos |
| Vitória | a vitória no combate | uma pose de comemoração e o brilho; um adereço por Digimon ficaria caro |
| Derrota | a derrota no combate | a pose sentada e afundada, com a gota |

**Prioridade 3, a leitura do corpo:**

| reação | gatilho | a pose | o emote |
|---|---|---|---|
| Triste ou choro | humor baixo, repreensão ou tapa | a cabeça baixa e o olho úmido | lágrima (novo) |
| Cansado ou bocejo | energia baixa, antes de dormir | a boca aberta e o olho fechando | "..." (novo) |
| Doente ou enjoado | lesão ou saúde baixa | curvado, com a cor apagada | espiral ou caveira (novo) |

**Prioridade 4, o resto:**

| reação | gatilho | a pose | o emote |
|---|---|---|---|
| Com medo | tapa repetido ou lesão | encolhido, de olhos arregalados | gota de suor |
| Sujo ou fedido | higiene baixa | coçando | moscas (novo) |
| Carinho | acariciar | os olhos fechados e o sorriso | corações |
| Envergonhado | elogio | o rosto de lado e a bochecha vermelha | — |
| Susto | algo novo no mapa (a bola ou outro pet) | um pulo para trás | exclamação |
| Recusa a comida | alimentar sem fome | vira a cara | "não" ou X (novo) |
| Acordar ou espreguiçar | o fim do sono | uma pose | — |
| Acenar ao dono | abrir o jogo | uma pose | — |
| Ser tratado | tratar a lesão | o Idle | curativo (novo) |

**Emotes novos, de custo zero:** lágrima, "...", espiral, caveira, moscas, estrelas de tontura, X, lâmpada, "!?" e curativo.

**O que não entra:** os golpes, o grab, o knockback e os efeitos de fogo e de choque das folhas. São de jogo de luta, e cada um seria um
vídeo por Digimon.

### 3.4 O que muda, por etapa

- **R1, o Dormir:**
  - uma pose de olhos fechados por Digimon, gerada por edição do still mestre;
  - a limpeza na grade do UP, os gates de paleta, caixa, pé e alfa, e o clipe de um quadro `Dormir` no export (fora do git);
  - o atlas gerado de novo;
  - no `sono.ts`, o pet dormindo usa o quadro `Dormir` quando a forma o tem e mantém a respiração e o "zz". Sem o quadro, fica como hoje.
- **R2, o cocô, a vitória e a derrota.**
- **R3, os emotes novos.**
- **R4 em diante, as reações das prioridades 3 e 4.** Cada etapa é uma sessão e um PR, com o merge pelo Matheus.

**O que não muda:**
- o motor (`web/app/motor`), os gabaritos, `digilab/` e o `engine.py`;
- o log e o replay;
- o `gerar_atlas_up_clipes.py`, salvo a tag nova em `CLIPES_ACOES`.

## 4. Experimento e gate

Não há run de pesquisa. O gate de cada reação tem duas partes:
- os gates numéricos da SPRITES_GERACAO, seção 4.1: paleta, caixa, pé, alfa até 2 px e área na faixa do Idle (o Dormir deitado pode sair
  da faixa; a faixa dele é decidida na R1);
- a leitura do Matheus numa folha de contato dos 60.

## 5. Entrega

- **Testes:** `python -m pytest tests/test_sprites_geracao.py -q`, e em `web/app` o `npm test`, o `npm run tipos` e o e2e de capturas da
  reação.
- **Registro:** uma seção no fim de `docs/registro/2026-11.md` e uma linha no fim do índice `docs/REGISTRO_DESVIOS.md`. O resumo de cada
  etapa vai no corpo do PR e numa seção no fim deste documento.
- **PR:** contra a `main`, com o corpo no modelo de `.github/pull_request_template.md`. O merge é só do Matheus.

## 6. Fora desta tarefa

- os golpes e os efeitos de luta das folhas;
- vídeo por Digimon, salvo uma decisão do Matheus caso a caso;
- mudar o motor para criar gatilhos novos, porque todos os gatilhos da lista já existem;
- os Digimon de fora das 60 formas (NPCs e bots).

## 7. Critérios de aceitação

- **Desta proposta:** este documento na `main`, com a lista, a ordem e o custo, e a seção 8 respondida pelo Matheus.
- **De cada etapa** (R1 em diante):
  - os gates numéricos passam nos 60, com o `gates.json` de cada um;
  - a folha de contato dos 60 foi aprovada pelo Matheus;
  - o jogo carrega o atlas sem cair na reserva;
  - `npm test` e `npm run tipos` passam;
  - `git diff origin/main -- web/app/motor digilab` sai vazio;
  - o gasto real vem do ledger e fica dentro do teto da etapa.

## 8. Precisa do Matheus

- **D-RE-1, a pose do Dormir:** sentado de olhos fechados, ou deitado encolhido?
  - **Recomendação:** **sentado de olhos fechados.** A silhueta do Idle muda pouco, então a pose passa nos gates de caixa e de área e
    funciona nos 60, inclusive nos grandes e nos alados.
  - **Custo de errar:** deitado lê melhor como sono, mas quebra a caixa e a área em muitos Digimon, e cada retake custa US$ 0,08.
- **D-RE-2, a ordem da lista (seção 3.3).**
  - **Recomendação:** a da seção: o Dormir, depois o cocô, a vitória e a derrota, depois os emotes novos.
  - **Custo de errar:** só a ordem; nada se perde.
- **D-RE-3, o teto da R1.**
  - **Recomendação:** **US$ 15** para os 60, até 3 takes cada, com um ledger próprio.
  - **Custo de errar:** um teto baixo para o lote no meio; um teto alto não muda nada, porque cada take passa pelo revisor e o gasto
    esperado é de US$ 5 a 14.
- **D-RE-4, o Digimon de prova da R1.**
  - **Recomendação:** o **Agumon** primeiro, depois um grande (o WarGreymon) e um alado (o Birdramon), antes dos outros 57.
  - **Custo de errar:** sem a prova, um defeito da pose se repete nos 60 e custa até US$ 14 para refazer.

## 9. As decisões do Matheus e a R1, o Dormir (2026-11-06)

- **D-RE-1 a D-RE-4, DECIDIDAS pelo Matheus em 2026-11-06** ("Sim, começar o Dormir"): a pose sentada, a ordem da seção 3.3, o teto de
  US$ 15 para a R1 e a prova no Agumon, num grande e num alado. O Birdramon deu lugar ao Aquilamon na prova, porque a ficha do Birdramon
  recusa: o Idle dele flutua acima do pé da âncora.
- **A R1 gerada (fora do git, em `remaster/geracao/reacoes/dormir/`):**
  - os 60 Digimon das formas têm o quadro de dormir: `final/<Nome>.png`, na caixa do UP, com o pé no `pe_idle` e as cores só do Idle de
    cada um. As escolhas e as rotas estão em `escolhas.json`, e o resumo do lote em `lote.json`;
  - as rotas: 37 pela edição do sprite (2 takes), 20 pela geração do zero com o sprite como referência (mais 2 takes) e 3 só com o olho
    fechado (Tsunomon, Veemon e Koromon);
  - o gasto, pelo ledger `forge/.forge/ledger.jsonl`: **US$ 14,16**, dentro do teto;
  - os bots e os NPCs (16) ficam sem o Dormir. Eles não são pet; o Matheus confirmou: "Não precisa".
- **O que a R1 ensinou:**
  - **A geração do zero inventa partes.** O Tsunomon e o Koromon ganharam braços, e o Veemon ganhou uma asa. A regra do Matheus: o
    personagem nunca ganha nada, e, onde o olho aparece, a reação é **só mexer no rosto** ("O Tsunomon era literalmente só fechar o olho
    dele"). A geração do zero fica só para quando a edição não muda nada e o olho não aparece (o WarGreymon, de capacete).
  - **As cores do Idle.** O snap na paleta da ficha (todas as cores do export, 3 684 no Agumon) deixava passar os degradês da IA. O quadro
    final usa só as cores do Idle 0 de cada Digimon.
  - **O `snap` do `limpar.py` estoura a memória** em paletas grandes (o WarGreymon, com 10 465 cores). O lote usou uma árvore k-d com o
    mesmo resultado.
  - **Uma regra de "não mudou":** a silhueta muda menos de 15 % em relação ao Idle (PROPOSTO, SEM FONTE). Ela separa o WarGreymon parado
    (no máximo 7 %) dos que mudaram (25 % ou mais), mas não vale para as reações só de rosto.
  - **A galeria** local (`remaster/geracao/galeria.html`, servida pelo `galeria-acoes` do `.claude/launch.json`) mostra cada par em escala
    inteira, sem filtro, com o "zz" saindo da cabeça.
- **O que falta para o jogo** (a etapa de código, numa sessão própria): o quadro `Dormir` nos exports, o atlas gerado de novo e o
  `sono.ts`, que, com o quadro, não achata nem escurece o sprite e põe o "zz" na cabeça.

## 10. O custo das próximas reações (PROPOSTO, 2026-11-06)

Os preços vêm do ledger da R1: US$ 0,08 por imagem (Nano Banana 2 edit). O câmbio de US$ 1 = R$ 5,50 está A CONFIRMAR. A coluna "esperado"
soma 30 % de retakes, a taxa observada na R1 (SEM FONTE além dela).

| reação | o que muda | takes por Digimon | US$ para os 60 | esperado |
|---|---|---|---|---|
| Triste, Cansado, Carinho, Medo, Envergonhado, Recusa | só o rosto (olho, boca); o emote por cima | 1 | 4,80 | ~6,25 (R$ 34) |
| Doente | o rosto e a cor apagada (a cor sai na vista, de graça) | 1 | 4,80 | ~6,25 |
| Cocô | a pose agachada; o cocô desenhado uma vez para todos | 2 | 9,60 | ~12,50 (R$ 69) |
| Vitória | a pose de comemoração | 2 | 9,60 | ~12,50 |
| Derrota | a pose sentada e caída | 2 | 9,60 | ~12,50 |
| Acordar ou acenar | uma pose | 2 | 9,60 | ~12,50 |
| Emotes novos (lágrima, "...", caveira, moscas, estrelas, X, curativo) | desenhados uma vez em grade | 0 | 0 | 0 |

Tudo junto, as 11 reações dos 60 custam perto de **US$ 95**, cerca de R$ 520. Começando pelas três da prioridade 2 (o cocô, a vitória e a
derrota), são cerca de US$ 37,50.

## 11. R1-jogo: o Dormir no jogo (2026-11-06)

O quadro de dormir dos 60 Digimon (seção 9) entrou no jogo pelo mesmo caminho do Emburrar (#609). Os exports ganharam a tag `Dormir` (1 quadro), o atlas de clipes foi regenerado com `Dormir` em
`CLIPES_ACOES` (em laço), e `papel.ts` desenha o quadro quando o pet dorme e a forma tem o clipe: sem achatar, sem escurecer, sem escala fracionária. O "zz" sai do topo da cabeça do quadro
(`CENA.zzX`). Sem o clipe, o sono é o de hoje (`sono.ts`). O desvio está em `docs/registro/2026-11.md`, seção "SPRITES_REACOES, o Dormir no jogo". Nada mudou em `web/app/motor`, nos gabaritos nem
em `digilab/`. Testes: `npm test` 94 arquivos, 937 passam; `npm run tipos` limpo; o e2e de capturas (Agumon e WarGreymon, 390 e 1280 px) passa, com o quadro no corpo e o atlas carregado.
