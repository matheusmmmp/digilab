# Mundo 3D, anexo 1: a auditoria técnica do repositório (WORLD-POC-001, investigação A)

Status: **RASCUNHO, PROPOSTO** (2026-10-18, worker A, pela especificação WORLD-POC-001 do Matheus). Anexo de `docs/futuro/mundo_3d.md`.
Só leitura: nada no código mudou. Base: `main` `533ee9b`.

**Legenda:**
- **Implementado:** está no código da `main` e tem teste.
- **Parcial:** existe uma parte.
- **Proposto:** só em documento.
- **Ausente:** nem código nem documento.
- **Não verificado:** não conferi.

Um documento de tarefa ou plano não conta como evidência de código.

**O que a seção 2 da especificação pede ler:** o `AGENTS.md` e o `docs/INDICE.md` ainda não estão na `main`; existem no PR #326, ainda
aberto, e foram lidos lá. O branch de referência é a `main`, e as convenções são as do `CLAUDE.md`. A documentação do DigiBrain V2 está
em `digilab/policies/lobos.py`, `docs/TAREFA_V2_W_PORTE_CEREBRO_A.md` e `docs/futuro/digibrain_v3_e0.md`.

**Trabalhos em andamento que tocam o mundo 3D (2026-10-18):**
- a etapa 4, parte 3, do porte (o v11 no `Motor` da web);
- o #326 e o #331 (a infraestrutura multiagente);
- o J5 com a fruta ao lado (a bancada do D);
- nenhum PR aberto mexe no mundo físico nem na renderização.

## 1. Frontend e renderização

| sistema | estado | evidência | observação |
|---|---|---|---|
| framework | Implementado | `web/app/package.json`: **Preact 10.29.8** com `@preact/preset-vite`, Vite 8.3.1, TypeScript 7.0.2, Vitest 5.0.2, Playwright 1.63.0 | **não é React**: é Preact, sem `preact/compat` no `package.json`. Uma biblioteca do ecossistema React (react-three-fiber) pediria o `compat` ou ficaria fora |
| biblioteca de renderização | Ausente | a única dependência de produção é `preact` | nenhuma engine 2D ou 3D: nem three, pixi, babylon nem WebGL |
| renderizador do pet | Implementado | `web/app/src/telas/pet/PalcoPet.tsx`: um `<canvas>` 2D (`getContext("2d")`, linha 138), com `imageSmoothingEnabled = false`, e o sprite em escala inteira (até 3x no celular e 4x no desktop) | é uma cena única de "LCD", com o pet no anel da plataforma. Não existe mapa |
| sprites e animação | Implementado | `web/app/src/atlas.ts`: o atlas do Digimon UP (`digilab_atlas_up.json` e `.png`), com quadros `[x, y, w, h, dx, dy]` e `ms_por_quadro` | **o atlas fica fora do repositório** (`D:\Trab\digilab\Assets`), por ser arte da Bandai **só para uso pessoal e local** (comentário em `atlas.ts`). O `vite.config.ts` só o serve no dev. **Risco para o POC (seção 6):** a "sprite real" é arte de terceiros |
| loop de renderização | Implementado (simples) | `PalcoPet.tsx:142`: `setInterval(desenha, 120)`; não há `requestAnimationFrame` no `src/` | cerca de 8 quadros por segundo, ligados ao quadro da animação, e não um loop de jogo |
| relógio do jogo | Implementado | `web/app/src/tempo.ts`: um `setInterval` de 100 ms avança o motor em ticks inteiros (1 tick = 1 minuto de jogo, `VEL_1X = 1/60`) pelo tempo real decorrido, na velocidade escolhida | o tempo da simulação é discreto, separado do desenho |
| estrutura de cenas e estado | Implementado | as telas em `src/telas/*`, o estado em `src/jogo.ts` (`jogoAtual`, `mudarMotor`); o motor entra por `useJogo()` | não há um grafo de cena: são componentes Preact e canvases independentes |
| interface front ↔ simulação | Implementado | `web/app/CLAUDE.md`: o motor fica em `motor/`, sem DOM (o teste `motor_sem_dom` confere); `Motor.aplicarEvento` é o passo do replay; as telas leem por `useJogo()` | esta é a fronteira que um mundo 3D tem de respeitar: o 3D é tela, e o motor não conhece a engine |
| vista do mapa e câmera | Proposto | `docs/futuro/mundo_fisico.md`, seção 2.6 (M-2, **DECIDIDO: vista inclinada como a do Animal Crossing**); o protótipo `docs/futuro/mundo_fisico_vistas.html`; as pranchas `docs/estilo_up/pranchas/MapaDesktop.html` e `Mapa390.html` (rodada 16) | **nenhuma tela do mapa no app.** O `motor/mundo.ts` não é usado por nenhum arquivo de `src/` |

## 2. DigiBrain (o cérebro A)

| sistema | estado | evidência | observação |
|---|---|---|---|
| a política e os ganchos | Implementado | `digilab/policy.py` (`Politica`, `Observacao`, `Transicao`); `digilab/policies/lobos.py` (`PoliticaLobos`) | os ganchos são `agir`, `observar`, `observar_consequencia`, `receber_acao_dono`, `consequencia_mundo`, `consequencia_corpo` e `mudanca_no_corpo` |
| percepção | Implementado | `lobos.percepcao`: `x = (1, Estado.vetor, ticks sem cuidado)`. Com o corpo, os receptores novos / S; no mundo físico, `PercepcaoMundo` (`digilab/mundo.py:279`): `vistos` (id, tipo, dx, dy, d) até `max_vistos` 8 dentro de `raio_visao_celulas` 6, mais o cheiro e a direção dele | a percepção é **relativa ao pet** (dx, dy), sem acesso ao mapa. A regra G-RECEPTOR (o cérebro só lê receptores e percepção) e o G-SEM-DIRECAO (`tests/test_cheiro_orgao.py`, conferido por AST) já guardam isso |
| memória | Parcial | `MemoriaEmocao` (só contadores, contribuição zero); `MemoriaEpisodios` (N6, atrás de chave); `ModeloOutros` (dois pets, só registra); `ModeloMundo` (J5, os troncos vistos e as árvores lembradas, atrás de `g_plano`) | no v11 só a `MemoriaEmocao` está ligada |
| impulsos e decisão | Implementado | a sonda do instinto (`impulsos`), pesos inteiros na escala S = 2^10 (`lobos.py:713`, `Aprendiz`), um sorteio por decisão | a ação é uma **`AcaoPet` discreta** (7 de hoje, mais `aliviar` com o banheiro) |
| aprendizado | Implementado | a regra da L1 (`atualizar_pesos`), o sinal homeostático pelo corpo (`sinal_corpo`), os canais (K-6), o tapa e o carinho; o alvo aprendido por classe (`_alvo_aprendido`, dois pets etapa 4) | **o resultado é negativo no mundo físico:** o P1 perde do instinto (#285), e o alvo aprendido atrapalha (#296), como diz a seção 8 do `ROADMAP_V2.md` |
| entradas sensoriais | Implementado | `PercepcaoCorpo` (`digilab/motor_corpo.py:92`): os receptores inteiros em [0, S], o olfato e o ouvido com lado (DP-13, DP-14), o paladar; `PercepcaoSocial` | não há sensor de contato, colisão ou empurrão: não existe física para medir |
| saídas motoras | Parcial | o cérebro devolve a ação e, no mundo físico, escolhe **um alvo entre candidatos** (`Alvo`, `mundo.py:297`: comida, bola, cheiro, vagar, casa, continuar, ponto, seguir, onde_comeu). Quem anda é o motor (`mundo_fisico.md` 2.1, `passo_ate`) | **intenção e execução já são separadas** (o cérebro escolhe para onde, o motor leva). Não há controle contínuo nem intenções como empurrar ou tocar |
| frequência | Implementado | `Config.intervalo_decisao_ticks = 15` (`digilab/config.py:55`): uma decisão a cada 15 minutos de jogo | um mundo físico em tempo real roda o passo da física a 60 Hz ou mais; o cérebro continua decidindo a cada 15 ticks (seção 4 do principal) |
| instrumentação | Implementado | o motivo de cada decisão (`_registrar`), o `estado_interno`, o connectome (`tools/connectome_cerebro_a.py`, #321) e a sonda E0 (`docs/futuro/digibrain_v3_e0.md`) | a E0 mostra que **mais da metade das decisões do v11 não tem escolha** (`sono_continuar` 34,6%, `abandono` 8,8%) |
| porte TS | Parcial | `web/app/motor/lobos.ts`: as etapas 2, 3 e 4 parte 1 na `main` (#323, #327, #335; `docs/TAREFA_V2_W_PORTE_CEREBRO_A.md`, seções 10, 13 e 14) | só o v11: o mundo físico, as frutas e o plano não foram portados e falham alto |

## 3. Fisiologia (o corpo químico)

| sistema | estado | evidência | observação |
|---|---|---|---|
| químicos, emissores e receptores | Implementado | `digilab/corpo.py`, `digilab/motor_corpo.py`; TS `web/app/motor/corpo.ts` com paridade | testes: `tests/test_corpo*.py`, `web/app/test/corpo.test.ts` |
| fome e digestão | Implementado | o órgão 1 (o estômago `alimento`), `TAREFA_V2_CORPO_DRIVES` | — |
| energia, fadiga e metabolismo | Implementado | o `cansaco`; o metabolismo energético (combustível e reserva, sem receptor, ME-2): Python #271 e TS #333 | a calibração fecha só com o passo 0 (`m_gasto` 4/5, #293); a validação do corpo não rodou |
| tédio, curiosidade, solidão, estresse | Implementado | os drives novos (etapa 6); a curiosidade só com o mundo físico (CD-8) | — |
| dor e susto | Implementado | os gestos (o tapa), `tests/test_corpo_gestos.py` | a dor vem **só do tapa**: não há dor de colisão nem de queda |
| dano e reparo | Ausente (adiado) | J10 adiado (D-5, D-6); o `dano` do corpo é o químico da saúde de hoje | sem dano físico, sem cura e sem morte |
| banheiro e paladar | Implementado (Python) | `TAREFA_V2_BANHEIRO`, `docs/futuro/paladar.md`; no TS, o `configCorpo` falha alto com o banheiro e com o paladar | — |
| consequências das ações | Implementado | `consequencia_corpo` (`ocorrido` = a ação e os estímulos); `consequencia_mundo` (deslocamento, comida, bola) | são estímulos discretos por ação, sem nenhuma consequência de contato físico |
| persistência | Implementado | event sourcing: o estado nunca é salvo, e a vida se refaz pelo log (`CLAUDE.md`, arquitetura) | — |

## 4. O mundo de hoje (2D)

| sistema | estado | evidência | observação |
|---|---|---|---|
| mapa | Implementado | `ConfigMundo` (`digilab/config.py:1737`): 64 × 30 células de 16 subunidades, posições inteiras, quatro regiões (M-1, M-4) | **sem paredes nem obstáculos** ("sem áreas fechadas", `mundo_fisico.md` 2.1; o banheiro é um retângulo "sem parede", `mundo.py:50`) |
| movimento | Implementado | `passo_ate` em linha reta, a `velocidade` de 4 subunidades por tick, com custo de energia por subunidade | sem desvio de obstáculo e sem pathfinding (não há obstáculo) |
| bola | Implementado (sem física) | `ConfigMundo.bola_*` e `atrito`: depois de brincar, a bola rola uma distância sorteada pela rng do ambiente, com `atrito` em subunidades por tick | **a bola não tem massa, velocidade nem colisão**: o resultado é sorteado, não vem de um empurrão |
| visão | Implementado | o raio de 6 células, sem ângulo e **sem oclusão** | sem parede não há o que ocultar |
| olfato e audição | Implementado | `campo_em`, os órgãos com lado (`leitura_do_olfato`, `som_ouvido`) | — |
| dois pets | Implementado | `digilab/grupo.py` (o `Mundo` como componente, a vez, o toque, a disputa) | o degrau 1 fica inconclusivo por premissa (`PAINEL_V2.md`) |
| mundo em TS | Parcial | `web/app/motor/mundo.ts` (etapa 5 do mundo físico): o mapa, a percepção, os alvos, a bola que rola, o `RandomPy` (o MT do CPython) e o `sha256`; teste `web/app/test/mundo.test.ts` | sem tela e sem versão de pet: nenhum arquivo de `src/` o usa |
| determinismo | Implementado | as rng separadas (`derivar_semente`), o replay pelo log, o `engine.py` congelado, a paridade bit a bit no Node (`web/app/CLAUDE.md`) | **é o requisito que mais pesa** na escolha da física (seção 2 do principal) |

## 5. Infraestrutura

| sistema | estado | evidência | observação |
|---|---|---|---|
| armazenamento | Implementado | `web/app/src/save.ts`: só o registro `{semente, log, versao}` no `localStorage`; o estado é refeito por `Motor.reproduzir` | um log de 60 dias do v11 tem 294 KB (`artifacts_v2_w_porte/replay_v11.json`) |
| navegador × servidor | Implementado | o jogo roda **inteiro no navegador**; o `servidor/servidor_local.py` serve o build e a fala por LLM (`servidor/CLAUDE.md`). A fala nunca entra no registro | a simulação não depende do servidor |
| sincronização | Ausente | não há multijogador nem sincronização entre aparelhos | — |
| Web Workers, WebAssembly | Ausente | nenhum `new Worker`, `WebAssembly`, `SharedArrayBuffer` ou `OffscreenCanvas` no `src/` nem no `motor/`, e nenhum cabeçalho COOP/COEP no `vite.config.ts` | uma física em wasm (Rapier, Havok) seria a primeira dependência wasm; o Godot com threads pede isolamento de origem (anexo 2) |
| desempenho | Parcial | o replay de 60 dias leva 217 ms no Node (i7-14700KF; `docs/TAREFA_V2_W_PORTE_CEREBRO_A.md`, seção 14) | **Não verificado:** o tamanho do bundle, os quadros por segundo e o celular (o e2e da etapa 5 do porte) |
| e2e | Implementado | `web/app/playwright.config.*`: o Chrome instalado, headless, `pt-BR` | não há teste de WebGL |

## 6. Lacunas e riscos que pesam no mundo 3D

1. **A física não existe e mexe numa decisão tomada.** A M-1 decidiu um mapa 2D de posições inteiras, e a seção 2.6 diz que "a vista é só
   desenho". Trazer física de verdade (massa, colisão, empurrão) para o motor reabre a M-1. Também quebra o determinismo bit a bit e a
   paridade Python/TS (seção 2 do principal). **É decisão do Matheus.**
2. **O aprendizado no mundo físico ainda não funciona:** o P1 perde do instinto (#285), e o alvo aprendido atrapalha (#296). Um mundo
   mais rico não resolve isso sozinho e pode esconder o problema (o P2 do roadmap reconciliado).
3. **A arte:** o "sprite real" do POC seria o atlas do Digimon UP, de uso pessoal e fora do repositório. Um POC que só existe com a arte
   de terceiros não vira produto. Para o POC dá, mas é preciso registrar isso.
4. **A stack é Preact**, não React. O ecossistema React do 3D (react-three-fiber, @react-three/rapier) pede o `preact/compat` ou uma
   integração imperativa (anexo 2).
5. **Não há sensor de contato.** As intenções "tocar" e "empurrar" da especificação precisam de um receptor novo no corpo (o
   proprioceptivo, listado como ideia em `DEFINICOES_CORPO_V2.md`, seção 8.1).
6. **O desempenho no celular não foi medido**, nem o do replay nem o de qualquer renderização.
