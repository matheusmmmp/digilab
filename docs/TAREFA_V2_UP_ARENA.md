# TAREFA V2 — UP-ARENA: a arena em tempo real no jogo web (2026-10-29)

Coordenador: sessão de coordenação da integração UP (Claude Code). Worker: Claude Code, Opus 5.5. Worktree e branch: `v2-up-arena`.
Status: PORTE ENTREGUE, esperando a revisão e o merge do Matheus (etapa 0 na seção 10, porte na seção 11; D1–D5 e P1–P4 decididas;
a UP-ATLAS e a UP-SOM na `main`, #441 e #440).

Categoria: implementacao. Origem: Matheus, 2026-10-29: `D:\Trab\digilab\remaster\LEVANTAMENTO_INTEGRACAO.md`, seção 4,
`D:\Trab\digilab\remaster\arena_equilibrio.md` e o protótipo `remaster/fonte/site/arena.html` (publicado em
https://claude.ai/artifact/HHBLAp9HSa8uNFCqNjezmh, `arena.html`, versão 14).

## 1. Pergunta

A arena em tempo real do protótipo pode virar um modo separado do jogo web, com os dados fora do código, em TypeScript com testes, e com a
medição de equilíbrio reproduzível por semente, sem tocar o combate atual? Nó do produto: batalha local (`docs/PRODUTO_VISAO.md`,
seção 3); não vem de hipótese do `PLANO_V2_PESQUISA.md`.

## 2. Depende de

- **D1** (modo próprio no jogo ou protótipo fora dele): se for "fora", esta tarefa se reduz à etapa 0 abaixo.
- **D2** (Python e paridade, ou só web) e **D5** (os números do EQ até o Matheus jogar).
- UP-ATLAS na `main` (os clipes `Run`, `Attack_1`, `Stun`, `Die`). UP-SOM opcional (sem ela, a arena vai muda).

## 3. Mudança mínima

**A pilha do jogo não muda (Matheus, 2026-10-29):** tudo o que o DigiLab já usa de tecnologia fica como está (Vite 8.3.1, TypeScript
7.0.2, React 19.3.0, Tailwind 4.3.3, three 0.186.1, o Node do `engines` e as demais dependências de `web/app/package.json`, nas mesmas
versões; o Python e a biblioteca padrão no pacote `digilab/`). Nenhuma versão sobe ou desce e nenhuma ferramenta é trocada; as mudanças
desta tarefa são implementadas dentro dessa pilha. O `package.json` e o `package-lock.json` saem iguais, a não ser por dependência nova
aprovada pelo Matheus antes (seção 8).

**Fonte conferida em 2026-10-29:** `arena.html` (1 209 linhas, 77 kB), `const EQ` na linha 226 (raio 18, alcanceCorpo 44, investida 58,
recuo 1, peito 24, danoCorpo 1, danoDist 1, kGolpe 0,06, kProj 0,05, pesoEstagio 0,2, variacao 0,1; a "vida ÷ 6" é uma opção da tela,
fora do EQ), `site/ataques/` (`ataques.json` com 379 efeitos de 210 Digimon, `golpes.json` 270, `status.json` 241, `atributos.json`),
`site/arenas/` (16 arquivos). **Achado:** o `arena.html` usa `Math.random` em 18 lugares e não tem semente; o `arena_equilibrio.md` cita
"semente fixa" (7, 42, 1–3, 7–8). O harness com semente não está no arquivo (talvez em `lote*.json` ou fora da pasta durável): vai para o
registro de desvios, e a etapa 0 o procura.

0. **Etapa 0, separar e reproduzir (antes de portar):** localizar o harness das medições do `arena_equilibrio.md`; se não existir, a
   medição "depois" não é reproduzível e fica registrada assim. Separar os dados em JSON (arenas, golpes, efeitos, status, atributos,
   EQ) e listar o que é código. **Parar e mostrar.**
1. **Simulação sem DOM** em `web/app/arena/` (pasta nova, fora de `motor/`; a mesma regra de "sem DOM" do motor, com o seu teste): passo
   de tempo fixo (não o `dt` do quadro), RNG própria com semente (`derivar_semente` como no motor, um fluxo por uso: IA, dano, partículas
   de efeito só visual fora da RNG da simulação), entrada do jogador como evento.
2. **Tela própria** atrás da chave desligada `ARENA_TEMPO_REAL`, numa rota do destino Lutar (sem mexer em `TelaArena.tsx` nem no
   combate V2.1). Desligada, o jogo de hoje igual.
3. **Dados (fora do git):** os JSON de status, golpes e efeitos e a arte dos mapas são do jogo: vão para `D:\Trab\digilab\Assets\arena_up\`,
   servidos pela lista do `vite.config.ts` e do `servidor_local.py`. **Os números do EQ e das regras de arena entram como PROPOSTOS, com
   fonte** (`arena_equilibrio.md`, rodada de 2026-10-29), numa constante versionada do app (são números do DigiLab, não do jogo).
4. **Medição de equilíbrio reproduzível:** um script (`web/app/scripts/medir_arena.ts` ou equivalente em Node) que roda as lutas CPU × CPU
   do método do `arena_equilibrio.md` por semente e grava o resultado em disco; um teste curto confere que a mesma semente dá o mesmo
   resultado. A rodada inteira não roda no CI.
5. **Se D2 = Python com paridade:** a simulação vai também para o Python (fora de `combate_v2`), com gabaritos `experiments/exportar_*.py`
   e o teste de paridade. Se D2 = só web: a arena fica fora do protocolo de resultado e não entra em nenhuma run de pesquisa.

**Não muda:** `combate_v2` (rodadas encerradas), `TelaArena.tsx`, `TelaLuta.tsx`, `PalcoLuta.tsx`, o motor, o `engine.py`, o log e o save
do pet. O pet do jogador não ganha nem perde nada na arena nesta tarefa (sem efeito no motor).

## 4. Experimento e gate

Não há run de pesquisa. A medição de equilíbrio (item 4) é engenharia: a meta é reproduzir as tabelas "depois" do `arena_equilibrio.md`
na mesma semente, ou registrar a diferença. Sem calibração nova nesta tarefa (D5).

## 5. Entrega

`npm test`, `npm run tipos`, `npm run e2e` (a chave desligada e a tela da arena com dados sintéticos versionados); o teste de
determinismo da simulação; a saída do script de medição em disco, citada no relato. Se D2 = Python: os testes de paridade. Registro e
relato como o modelo manda.

## 6. Fora desta tarefa

Ligar a arena ao pet (ganho, treino, evolução); multiplayer; nova rodada de equilíbrio; a simulação de partículas do Unity; a skin
`Invision`; mexer no combate V2.1.

## 7. Critérios de aceitação

1. A etapa 0 diz onde está o harness com semente ou registra que não existe.
2. A simulação roda em Node sem DOM, e a mesma semente dá o mesmo resultado (teste).
3. Os dados do jogo não estão no git; os números do EQ estão numa constante com PROPOSTO e a fonte.
4. Com a chave desligada, nada muda no jogo (e2e e capturas).
5. O script de medição grava as tabelas por arena e por estágio e o relato as compara com o `arena_equilibrio.md`.

## 8. Precisa do Matheus

D1, D2 e D5 antes de começar (com a recomendação do coordenador). Depois da etapa 0: seguir sem o harness original, se ele não aparecer.

## 9. Decisões tomadas

- **D3 DECIDIDA (Matheus, 2026-10-29):** os assets novos seguem a regra dos sprites (`docs/UI_GUIDELINES.md`, seção 5.1).
- **D1 DECIDIDA (Matheus, 2026-10-29, "siga as recomendações"):** a arena em tempo real entra no jogo como modo próprio, atrás da chave
  desligada `ARENA_TEMPO_REAL`, numa rota do destino Lutar, sem tocar o combate V2.1 nem o pet.
- **D2 DECIDIDA (idem):** a arena fica só na web, fora do protocolo de resultado, sem versão Python nem paridade; a simulação em TS é
  determinística, com semente. O item 5 da seção 3 vale só no ramo "só web".
- **D5 DECIDIDA (idem):** os números do EQ e das arenas ficam PROPOSTOS como estão até o Matheus jogar; sem rodada de calibração.
- **A pilha não muda** (Matheus, 2026-10-29): seção 3.
- **P1 a P4 DECIDIDAS (Matheus, 2026-10-29, no chat da coordenação, "aceitou as recomendações P1 a P4 da etapa 0"):**
  - **P1:** o porte é validado primeiro pela paridade com o protótipo, com a RNG de sequência única só em teste; só depois os fluxos
    se separam;
  - **P2:** o elenco são os 280 Digimon do atlas da arena;
  - **P3:** o harness recuperado vai para `D:\Trab\digilab\remaster\fonte\scripts_arena\harness_equilibrio.js`, fora do git (copiado
    em 2026-10-29, com as saídas em `harness_equilibrio_resultados.txt`);
  - **P4:** o recuo da `Skill_1` para a `Attack_1` fica, agora explícito e com aviso.

## 10. Etapa 0: o resultado (worker, Claude Code, Opus 5.5, 2026-10-29)

### 10.1 O harness com semente existe, e reproduz as medições

- **Onde estava:** em nenhum arquivo. A sessão de origem ("Extração de assets de animação de APK (fork)", `local_f091469a`) colou o
  harness no console do navegador pelo `javascript_tool` e o guardou só no `sessionStorage` da aba. Ele foi recuperado do transcrito
  (`C:\Users\mathe\.claude\projects\D--Trab-digilab\f091469a-ca80-4b5a-83f0-d910b6af3857.jsonl`, chamadas nas linhas 2858, 3132 e 3279).
  Os `lote*.json` são só listas de arquivos para publicar, e o `scripts_arena/` não tem o harness.
- **Como funciona:** durante cada luta, troca o `Math.random` da página por um mulberry32 com semente (a mesma função de
  `web/app/motor/rng.ts`). A semente da luta é `semente + 1000 + k` na `medir` (arenas), `sd × 7919 + i × 131 + k` no `rodizio` (Digimon
  do mesmo estágio) e `n × 31 + 5` no `cruzar` (estágios). As equipes da `medir` saem do mesmo gerador, na semente da rodada. O passo é
  fixo, `passo(16)`, e o limite é de 300 s. Quedas, bloqueios, runas e erros são contados por expressão regular no texto do log.
- **Conferido hoje** no `arena.html` atual (sha256 `f3be1160…91fbeb`), no Chrome do painel do Claude Code, com o harness recuperado: dá
  **exatamente** os números do `arena_equilibrio.md`:
  - campo, sementes 42, 99 e 123: azul 11/20 em 92 s, 8/20 em 96 s, 11/20 em 99 s (a "azul 45% em 80 lutas", com a semente 7: 6/20);
  - as 8 arenas na semente 7: de 90 a 103 s, nenhuma luta sem fim, ambiente com 4,5–8,1% do dano, 2,8 quedas do ringue por luta (o
    último parágrafo do documento);
  - o rodízio por estágio nas sementes 7–8, a tabela inteira (à distância, corpo a corpo, faixa, desvio);
  - os estágios (73, 66, 82, 84, 95%) e os níveis (56, 40, 15%).
- **O que não se reproduz com o arquivo atual:** as tabelas "Antes" e "Depois" das arenas, medidas antes da rodada dos Digimon, quando o
  `EQ` ainda era outro. A saída daquelas rodadas está no transcrito e bate com o documento, mas o `arena.html` daquela hora não existe
  mais. Para o arquivo atual, a conferência das arenas que vale é o último parágrafo.
- **Condições para reproduzir:** som desligado (o `tocarSom` também consome o `Math.random`); força do atributo 1,5 na `medir` (o padrão da
  página) e 1 no `duelo` (o próprio harness ajusta); dificuldade normal; status do jogo; o Chrome (outro runtime pode mudar o último bit
  de `Math.pow`, `Math.hypot` e `Math.sin`, como já acontece com a paridade do motor).
- **A cópia:** o harness, pronto para colar no console, e as saídas recuperadas ficaram na pasta de notas da coordenação
  (`arena_harness_equilibrio.js`, `arena_resultados_recuperados.txt`). O lugar durável é `remaster/fonte/scripts_arena/`, fora da
  worktree; ver a pergunta P3.

### 10.2 Os achados

1. **O protótipo tem uma sequência aleatória só.** O `Math.random` serve ao jogo e também ao visual: a posição do número de dano (linha
   722) e o tom do som (linha 513). Com os fluxos separados que a seção 3 pede, o porte não reproduz as tabelas número a número, só em
   distribuição. Daí a proposta da seção 10.4.
2. **A habilidade `Skill_1` de 22 Digimon não tem a tag no atlas** (Apocalymon, Armageddemon, Bakemon, BlackWarGreymon, Datamon…). A
   `tag()` cai em silêncio para a primeira tag do atlas, que é a `Attack_1`. As medições incluem esse comportamento.
3. **Recuos silenciosos:** sem golpe, um golpe genérico (`Attack_1`, 0,4 s); sem atributo, `None`; `status.json` e `atributos.json` com
   `.catch(() => ({}))`; imagem com erro vira `null`. No porte, cada um vira erro com aviso visível, ou regra explícita (P4).
4. **A medição lê o texto do log** (por exemplo, `/caiu do ringue/`). No porte, a simulação emite eventos com tipo, e o texto em
   português fica só na tela.
5. **Uma rodada intermediária** do transcrito (linha 3313, semente 7) deu o azul vencendo de 2 a 5 em 20 em todas as arenas. O arquivo
   atual dá de 6 a 13 em 20. O documento não cita essa rodada; o registro anota para quem ler o transcrito não confundir as duas.
6. **No rodízio, o "sem fim" soma as lutas que chegam a 300 s e os empates** (de 3 a 6 por estágio, cerca de 1% das lutas). O documento
   fala em empates de ~2%.
7. **O nome "arena" já tem dono no app:** `web/app/motor/arenas.ts` (as arenas com líderes da campanha v6) e `TelaArena.tsx` (o
   combate). A pasta nova `web/app/arena/` e a chave `ARENA_TEMPO_REAL` não colidem com eles, mas os tipos novos levam o sufixo
   `TempoReal` onde houver ambiguidade.

### 10.3 Dados e código

**Dados do jogo** (fora do git, regra 5.1; vão para `D:\Trab\digilab\Assets\arena_up\`, servidos pela lista do `vite.config.ts` e do
`servidor_local.py`):

| dado | hoje | o que a simulação usa |
|---|---|---|
| `status.json` (241 Digimon: tipo, estágio, base, ganho por nível) | `site/ataques/` | vida, ataque, defesa, crítico, esquiva, atordoamento |
| `golpes.json` (270: animação, instante do golpe, projétil, impactos, habilidade) | `site/ataques/` | instante, projétil e velocidade, habilidade |
| `atributos.json` (280) | `site/ataques/` | o triângulo de atributos |
| a duração dos quadros por tag (`atlas/index.json`: `t` e o `ms` de `f`, 280 Digimon) | `site/atlas/` | o ciclo de ataque e da habilidade, o tempo da queda |
| `ataques.json` (379 efeitos de 210 Digimon) e as 210 folhas PNG | `site/ataques/` | nada: só a tela |
| as pranchas dos Digimon (PNG e JSON por Digimon, 87 MB) | `remaster/export/` | nada: só a tela |
| pisos, fundos e objetos das 7 arenas (16 imagens) | `site/arenas/` | nada: só a tela |

O atlas de clipes do jogo (#441) tem só as 76 formas do DigiLab e 6 clipes: não serve à arena. A proposta é um `tempos.json` derivado do
`atlas/index.json` (só os nomes das tags e o `ms` dos quadros), gerado por um script fora do git, como o `gerar_sons_up.py`. O som da
arena (`sons_arena.json`) fica para depois: a seção 6 não o pede, e a arena pode ir muda.

**Números do DigiLab** (versionados no app, cada um PROPOSTO, com a fonte `arena_equilibrio.md` ou SEM FONTE):
- o `EQ` (11 números) e a `DIFIC` (3 níveis × 4);
- a geometria: o mundo 480 × 280, a elipse da arena, a posição de entrada (±130 px);
- os tempos: troca 3 000 ms, entrada 450 ms, atordoamento 220 e 900 ms, recarga inicial 300–600 ms e da habilidade 2 500–4 000 ms;
- o movimento: investida rápida de 420 px/s (jogador) e 380 px/s (CPU), duração de 160 e 180 ms, recarga de 1 200 ms; o eixo y a 0,7;
  o empurrão de 6 px; o alcance à distância de 150 px;
- as opções da tela que entram na luta: vida ÷ 6 (`ritmo`), a força do atributo 1,5, a velocidade do projétil (`pvel`) e os status
  genéricos (`STATS`);
- as regras das 7 arenas: obstáculos e zonas (coordenadas), Coliseu (30 s, 50%, 5%/s), Praia (maré de 18 s, 70%, 72 px), Deserto
  (tempestade a cada 20 s por 6 s, 60%, mira ×3, puxão de 26 px/s), Castelo (runa de 1,2 s, +30% por 8 s, recarga de 12 s; pilar com 3
  golpes), Caverna (lava a 6%/s; erupção a cada 7 s, 1,2 s de aviso, 10%, 28 px), Ringue (empurrão 2× e 7×, 15%, 600 ms fora, medo da
  borda a 80%).

**Código** (vira TypeScript):
- *simulação, sem DOM:* `criarLutador`, `atualizar` (a IA), `passo`, `aplicarDano`, `soltarGolpe`, os projéteis, `colidir`, `bloqueio`,
  `obstaculoEm`, `prender`, `trocar`, `cpuTroca`, `desviar`, `statusDoJogo`, `multAtr`, `fatorRitmo` e as funções `tick`, `guia`, `mov`,
  `projVel` e `erro` de cada arena. O `controlarJogador` vira o leitor dos eventos de entrada.
- *só a tela:* `desenhar`, `chao`, `barra`, o `baixo` e o `cima` de cada arena, `desenharEf`, `quadroAtual`, as barras das equipes, as
  fichas, o som, o laço `requestAnimationFrame`, o teclado e o mouse.
- *o que hoje está misturado e o porte separa:* `statsDoMembro`, `multAtr` e `soltarGolpe` leem campos da página; `registrar` escreve
  na página; `aplicarDano` lê cores do CSS e sorteia a posição do número de dano; `sonsDe` é chamado de dentro da simulação.
- *a medição:* `medir`, `duelo`, `rodizio`, `cruzar` e `estagios` viram o script do item 4.

### 10.4 O desenho proposto para a simulação

- **A pasta `web/app/arena/`**, com a regra do motor: lib ES sem "dom" (o `tsconfig.json` passa a incluir `arena/**/*.ts`) e um teste
  `arena_sem_dom` com a lista de proibidos do `motor_sem_dom`, mais o `Math.random`. A arena pode importar do `motor/` (a RNG), e o motor
  nunca importa da arena.
- **Os módulos:**
  - `tipos.ts`: lutador, luta, arena, entrada e evento;
  - `constantes.ts`: os números da seção 10.3, cada um com o status e a fonte;
  - `cenas.ts`: as 8 arenas, só a geometria e as regras (o desenho fica em `src/`);
  - `dados.ts`: a validação dos JSON carregados, que falha alto se faltar um Digimon, um campo ou uma tag;
  - `sim.ts`: `criarLuta(config, dados, semente)` e `passo(luta, entradas)`, que devolve os eventos do passo.
- **O passo de tempo é fixo: 16 ms**, o da medição. A tela acumula o tempo do quadro e chama quantos passos couberem; o `dt` do quadro
  nunca entra na simulação.
- **A RNG tem um fluxo por uso.** Cada fluxo é um mulberry32 (`criarRng` do motor) semeado pelos 32 bits baixos de
  `derivarSemente("arena", semente, fluxo)`. Os fluxos: `ia` (desvio, mira, troca, recargas iniciais, fase), `combate` (esquiva,
  crítico, variação do dano, atordoamento), `cena` (erupções) e `sorteio` (as equipes da medição). O visual (o número de dano, as
  partículas) fica fora da simulação e não consome nenhum fluxo; o som continua no `Math.random` do app, como na UP-SOM.
- **A entrada do jogador é evento:** `{ passo, tipo: mover | atacar | habilidade | trocar | investida, mira }`. A simulação nunca lê
  teclado nem mouse, e a mesma semente com os mesmos eventos dá a mesma luta. Nada vai para o log nem para o save do pet.
- **A saída é evento com tipo:** dano, esquiva, queda, troca, queda do ringue, tiro bloqueado, pilar, runa, golpe no ar, fim. A tela
  escreve o log em português a partir deles, e o script de medição conta sem expressão regular.
- **A medição** (`web/app/scripts/medir_arena.ts`) roda no Node do `engines` (24, que já executa TypeScript sem dependência nova), lê os
  dados de `Assets/arena_up/` e grava as tabelas em disco.
- **A validação do porte, em dois passos (recomendação):**
  - **A, paridade com o protótipo:** um provedor de RNG de "sequência única", só para teste, que consome na ordem exata do `arena.html`
    (inclusive o sorteio do número de dano, descartado). Com ele, o script roda o harness recuperado em Node, e as tabelas têm de sair
    iguais às da seção 10.1. Se o último bit do Node e do Chrome mudar algum resultado, a diferença vai para o registro.
  - **B, os fluxos separados** (o padrão do jogo): a medição roda de novo e grava as tabelas novas, comparadas em distribuição com o
    documento, sem calibração (D5).
  - **Custo de errar:** sem o passo A, um erro de porte (uma regra trocada, uma ordem de checagem diferente) se esconde dentro da
    variação aleatória e só aparece quando o Matheus jogar. Com o passo A, o custo é um provedor de RNG a mais, usado só em teste.

### 10.5 Perguntas ao Matheus

- **P1. Validar o porte pela paridade com o protótipo (o passo A) antes de separar os fluxos?** Recomendo que sim (custo na seção 10.4).
- **P2. O elenco da arena no jogo:** os 280 Digimon do atlas da arena (os JSON somam cerca de 0,3 MB, e as pranchas, 87 MB, ficam fora do
  git) ou só os parceiros com status próprio (72, os medidos)? Recomendo os 280: os dados são pequenos, e o filtro é uma linha. Custo de
  errar: com os 280, entram Digimon sem status próprio (93 "estimados pelo estágio", e 39 sem registro, com status genéricos), nunca
  medidos.
- **P3. Copiar o harness recuperado para `remaster/fonte/scripts_arena/harness_equilibrio.js`?** A pasta é durável, mas fica fora desta
  worktree, por isso não copiei. Recomendo que sim: hoje ele existe só na pasta de notas e no transcrito.
- **P4. A `Skill_1` sem tag no atlas (22 Digimon):** manter a regra do protótipo (anima e conta o tempo do `Attack_1`), agora explícita e
  avisada uma vez, ou tratar como erro? Recomendo manter, porque é o que a medição mediu, e a paridade do passo A depende disso.

## 11. O porte: o resultado (worker, Claude Code, Opus 5.5, 2026-10-29)

Feito pelos itens 1 a 4 da seção 3, com o desenho da seção 10.4 e as decisões P1 a P4. O item 5 não se aplica (D2: só web).

### 11.1 O que entrou

- **A simulação, sem DOM** (`web/app/arena/`), com o `tsconfig.json` incluindo `arena/**/*.ts`:
  - `sim.ts` é o porte do `arena.html`, na mesma ordem de contas e de sorteios;
  - `cenas.ts` traz as 8 arenas, só a geometria e as regras;
  - `nucleo.ts` traz geometria, obstáculos e dano do ambiente;
  - `dados.ts` traz a conferência dos JSON, que falha alto, e os recuos explícitos;
  - `rng.ts` traz os fluxos `ia`, `combate`, `cena` e `visual`, cada um um mulberry32 semeado por `derivarSemente("arena", semente, fluxo)`.
    A sequência única fica só para teste e medição.
  - `medicao.ts` é o harness recuperado, sem DOM;
  - `constantes.ts` traz todos os números, PROPOSTOS, com a fonte.
- **O passo é fixo, de 16 ms.** A entrada do jogador é evento, e a saída são eventos com tipo. Nada toca no motor do pet, no log nem no save.
- **A tela:** `src/telas/lutar/arena_tr/` (`TelaArenaTempoReal.tsx`, `desenho.ts`, `log.ts`), mais `src/arenaTempoReal.ts` (a chave e os
  dados) e `src/estilo/arena_tr.css`.
  - Funciona atrás da chave desligada `ARENA_TEMPO_REAL`, com `?arena_tr=1` ligando só naquela aba, como o `?clipes_up=1`.
  - A rota é `#/lutar/tempo-real`, em tela cheia. Com a chave ligada, um botão "Arena em tempo real" aparece no destino Lutar.
  - Os modos são jogador × CPU e CPU × CPU, com a "Revanche (mesma semente)".
  - Avisos visíveis: dados que não carregaram, arte que não carregou e, numa caixa recolhida, os recuos da P4.
  - O `App.tsx` ganha 15 linhas, todas sob `arenaTrLigada()`. `TelaArena.tsx`, `TelaLuta.tsx`, `PalcoLuta.tsx` e `combate_v2` não mudam.
  - A arena vai muda: o som não entrou, porque a seção 6 não o pede.
- **Os dados ficam fora do git.** `D:\Trab\digilab\Assets\gerar_arena_up.py` gera `Assets\arena_up\` a partir de `remaster/`: 512
  arquivos, 73 MB, com `dados/manifesto.json` guardando o sha256 de cada um. São servidos pelo `vite.config.ts` e pelo
  `servidor_local.py`, no modo remoto só por nome simples (`tests/test_servidor_remoto.py`).
- **Os testes:**
  - `web/app/test/arena.test.ts` cobre o determinismo por semente nas 8 arenas, os fluxos independentes, a entrada do jogador refeita, a
    conferência que falha alto, os recuos, o status e a paridade nos dados reais (pulada se `Assets/arena_up` faltar);
  - `web/app/test/arena_sem_dom.test.mjs` confere a arena sem DOM, sem `Math.random` e sem importar nada de fora;
  - os dados sintéticos versionados ficam em `web/app/test/arena_sintetico.json`;
  - há 3 e2e em `e2e/jogo.spec.ts`: a chave desligada, a luta inteira com a revanche igual, e o aviso sem dados.
- **A medição:** `web/app/scripts/medir_arena.ts`, no Node 24, sem dependência nova. Ela grava `web/app/scripts/medicoes/arena_unico.json`
  e `arena_fluxos.json`; o gabarito do passo A é `web/app/scripts/arena_gabarito_prototipo.json`.

### 11.2 Passo A: a paridade com o protótipo

Com a sequência única, o porte em Node dá **exatamente** o que o harness deu no Chrome (`node scripts/medir_arena.ts --modo unico`, 17 s,
"tudo igual ao gabarito"):
- as 8 arenas na semente 7 (duração, p90, sem fim, ambiente, azul, quedas do ringue, tiros bloqueados, runas);
- o campo nas sementes 42, 99 e 123;
- o rodízio por estágio nas sementes 7–8 (à distância, corpo a corpo, desvio, faixa, tempo médio, sem fim);
- os estágios (73, 66, 82, 84, 95%) e os níveis (56, 40, 15%).

O Node e o Chrome não divergiram em nenhuma luta dessas rodadas.

### 11.3 Passo B: os fluxos do jogo, comparados em distribuição (sem calibrar, D5)

`node scripts/medir_arena.ts --modo fluxos` (`arena_fluxos.json`):

| medida | sequência única (o documento e o passo A) | porte com fluxos |
|---|---|---|
| arenas, semente 7: duração | 90–103 s | 92–103 s |
| arenas, semente 7: sem fim | 0 | 0 |
| arenas, semente 7: ambiente (Coliseu, Caverna, Ringue) | 4,5–8,1% | 5,8–8,7% |
| arenas, semente 7: quedas do ringue por luta | 2,8 | 2,4 |
| arenas, semente 42: duração; ambiente; quedas | — | 90–108 s; 4,8–8,0%; 1,9 |
| azul vence, por arena, sementes 7 e 42 | 6–13 de 20 | 6–11 de 20 |
| estágios: Champion>Rookie, Ultimate>Champion, Mega>Ultimate, Ultimate>Rookie, Mega>Rookie | 73, 66, 82, 84, 95% | 73, 71, 71, 88, 97% |
| níveis: Champion nv1 contra Rookie nv2, nv3, nv5 | 56, 40, 15% | 58, 40, 17% |
| rodízio: à distância / corpo a corpo, de Bebê II a Mega | 48/54, 52/47, 45/59, 50/51, 48/54% | 50/50, 49/51, 45/58, 52/47, 46/59% |
| rodízio: faixa de vitória | 34–68% | 30–79% (Mega 31–79%) |
| rodízio: desvio | 0,061–0,095 | 0,072–0,116 |

As arenas continuam dentro das metas do documento. No rodízio, a faixa e o desvio são maiores com os fluxos: a meta de "todos entre ~35%
e ~65%" não é atingida em nenhum estágio. Não medi se isso é ruído de amostra (4 lutas por par) ou efeito de separar os fluxos.
Registrado como está, sem ajuste (D5).

### 11.4 As entregas conferidas

- `npm test`: 638 passados (56 arquivos).
- `npm run tipos`: limpo.
- `npm run e2e`: 97 passados, os 94 de antes mais os 3 da arena.
- `pytest tests/test_servidor_remoto.py`: 14 passados.
- O `package.json` e o `package-lock.json` não mudaram.
