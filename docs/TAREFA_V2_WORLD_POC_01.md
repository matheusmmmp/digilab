# TAREFA V2 — WORLD_POC_01 (2026-10-19)

Coordenador: Gerente. Worker: A. Worktree e branch: `v2-world-poc-01`. Status: ENTREGUE (falta só a M3 no celular, do Matheus).

Categoria: implementacao. Origem: Matheus, 2026-10-19: o WORLD-POC-01a da investigação WORLD-POC-001 (docs/futuro/mundo_3d.md), aprovado em 2026-10-19 para avançar em paralelo ao Gate C.

## 1. Pergunta

**O WORLD-POC-01a responde:** a arquitetura decidida para o mundo 3D funciona no navegador? É a do `docs/futuro/mundo_3d.md`:
- W-1: a física no motor, em inteiros (o arranjo V);
- W-2: o Three.js imperativo só como vista;
- o contrato sensório-motor da seção 4, sem o DigiBrain conhecer a engine.

**É um protótipo técnico, não pesquisa.** Ele não vem de hipótese do `docs/PLANO_V2_PESQUISA.md`, não tem run nem semente reservada e
fecha o **Gate A** (a viabilidade técnica; `docs/futuro/mundo_3d.md`, seção 7). É a fase P3 da especificação, que **avança em paralelo**
ao Gate C (a W-5, como o Matheus esclareceu em 2026-10-19, trata do cérebro de verdade no mundo novo, a P4, e não da P3).

A especificação inteira (o escopo, os componentes, os testes, as métricas e a estimativa) está em `docs/futuro/mundo_3d/poc_01.md`.
Esta tarefa a põe em etapas com gates e diz o que não entra.

## 2. Depende de

- **Na `main`:** a investigação (#340: `docs/futuro/mundo_3d.md` e os anexos em `docs/futuro/mundo_3d/`).
- **Decisões do Matheus que já existem:**
  - W-1 a W-7 (2026-10-18, pela recomendação; `docs/futuro/mundo_3d.md`, seção 8);
  - a liberação do POC em paralelo ao Gate C (2026-10-19).
- **Nenhuma frente de código precisa entrar antes:** o POC não usa o `motor/` do jogo, o `lobos.ts` nem o `corpo.ts`.

## 3. Mudança mínima

**O que muda** (todos os caminhos PROPOSTOS; o worker pode ajustar nomes, sem mudar as fronteiras):

| arquivo | papel | conhece o Three.js? |
|---|---|---|
| `web/app/poc/mundo3d/mundo.ts` | o estado inteiro da sala (o piso de 16 × 12 células de 16 subunidades, as paredes, os obstáculos, a bola, a comida e o pet) e o `passo()` de um tick | não |
| `web/app/poc/mundo3d/fisica.ts` | a física inteira: o círculo contra o retângulo, o deslize, a bola (atrito, reflexão na parede com restituição em fração inteira, o empurrão) e os sub-passos | não |
| `web/app/poc/mundo3d/controlador.ts` | o A* inteiro na grade e a execução da Intenção até chegar, bloquear, o alvo sumir ou dar a hora | não |
| `web/app/poc/mundo3d/sensores.ts` | a Observação do contrato (`mundo_3d.md`, 4.2): o cone com raio na grade e oclusão (o obstáculo alto tapa, o baixo não), os bigodes em 8 setores e o contato. Nenhuma posição absoluta de objeto na Observação | não |
| `web/app/poc/mundo3d/cerebro.ts` | o cérebro de teste: um decisor de regras (a fome leva à comida, o tédio leva à bola) que lê só a Observação e devolve só a Intenção (`mundo_3d.md`, 4.3). **Não é o cérebro A** | não, e um teste confere |
| `web/app/poc/mundo3d/registro.ts` | o registro por decisão: a Observação, a Intenção, a ação executada e o resultado físico (`mundo_3d.md`, 4.1), exportável em JSON | não |
| `web/app/poc/mundo3d/vista.ts` | o Three.js: a câmera ortográfica inclinada (M-2), as caixas do piso e das paredes, o pet como `THREE.Sprite` com filtro nearest e escala inteira, a sombra como disco, a parede da frente semitransparente quando cobre o pet e a interpolação entre ticks | **sim, e só ele** |
| `web/app/poc/mundo3d.html` e `web/app/poc/vite.config.ts` | a página e uma config do Vite própria, **fora do build do app** (o `npm run build` do jogo sai igual) | — |
| `web/app/test/poc_mundo3d*.test.ts` | os testes da seção 7 | — |
| `web/app/package.json` | a dependência `three` em versão exata (a 0.186.1 foi a conferida em 2026-10-18, `docs/futuro/mundo_3d/tecnologias.md`), mais um script `poc` para abrir a página | — |

**O sprite (W-6):** o pet usa um quadro do atlas do Digimon UP, **só local e sem versionar**, carregado como o `src/atlas.ts` faz. Sem
o atlas, entra um sprite de reserva desenhado à mão, que vai no repositório.

**O que NÃO muda:**
- o jogo: `web/app/src/` e o `npm run build` do app;
- o motor do jogo (`web/app/motor/`) e as versões de pet;
- o motor da pesquisa (`digilab/`, inclusive `mundo.py` e o `engine.py`, congelado);
- o cérebro A (`digilab/policies/lobos.py`, `web/app/motor/lobos.ts`);
- os gabaritos, os experimentos e as runs.

O POC não importa nada de `web/app/motor/` nem de `src/`, e nada de lá o importa.

## 4. Experimento e gate (se houver run)

Não há run de pesquisa nem plano de análise: é um protótipo técnico, sem semente reservada. Os gates são técnicos, por etapa:

| etapa | o quê | gate (o teste ou a medida) | PR |
|---|---|---|---|
| **E0** | a página, a config própria do Vite, a dependência `three` e o sprite de reserva | **G-FRONTEIRA:** um teste lê o fonte; só o `vista.ts` importa `three`; nada de `poc/` importa `motor/` ou `src/`, e o contrário também não; o `npm run build` do app não muda de conteúdo | PR 1 |
| **E1** | a física inteira e o controlador | **G-COLISAO:** o círculo não atravessa a parede nem o canto, desliza, e a bola rápida não atravessa com os sub-passos. **G-BOLA:** o empurrão dá velocidade na direção do contato, o atrito para a bola e a reflexão troca a componente normal. **G-NAVEGA (M4):** o pet chega ao alvo em todos os cenários com os dois obstáculos | PR 1 |
| **E2** | os sensores, o contrato, o cérebro de teste e o registro | **G-SENSOR:** o obstáculo alto tapa e o baixo não; nada fora do cone aparece; a Observação não traz posição absoluta de objeto. **G-CONTRATO:** o `cerebro.ts` só importa os tipos do contrato. **G-DET (a primeira metade da M5):** a mesma semente e o mesmo log dão o mesmo hash do estado, duas vezes no Node | PR 1 |
| **E3** | a vista | **M1:** a página abre e o WebGL desenha (o screenshot do e2e não é vazio). **M2:** os pixels do sprite na tela batem com os do quadro na escala inteira, sem borrar, nos quatro cantos da sala | PR 2 |
| **E4** | as medições e o relato | **M3:** os quadros por segundo e o tempo de quadro, no desktop e num celular real (PROPOSTO: 30 quadros por segundo no celular; a emulação do Playwright não vale). **M5:** o mesmo hash no Node e no Chrome (o e2e), e o tempo do replay de 1 dia de sala, só descritivo. **M6:** o bundle da página em gzip, só descritivo. Os números vão para `artifacts_v2_world_poc/` | PR 2 |

Se um gate falhar, o worker registra o resultado como está e não ajusta o critério olhando para ele.

## 5. Entrega

- Testes: `python -m pytest tests/ -q`; em `web/app`: `npm test`, `npm run tipos`, `npm run e2e` (se a frente toca a web).
- Registro: seção própria no fim do arquivo do mês, `docs/registro/AAAA-MM.md`, e uma linha no fim do índice `docs/REGISTRO_DESVIOS.md`
  (rodada de saúde, etapa 2). O resumo da etapa vai no corpo do PR e numa seção no fim do documento da
  frente (o `RESULTADO_V2_*.md` da run ou o `TAREFA_V2_*.md` da etapa), nunca no `CLAUDE.md` (rodada de saúde, etapa 1).
- PR contra a `main` com resumo e números (cada um com o artefato). Aviso ao coordenador. Merge só pelo Matheus.
- O corpo do PR segue `.github/pull_request_template.md`; o CI (`tools/verificar_relato.py`) confere os campos e a evidência da categoria.
- **Dois PRs, na ordem:**
  - o PR 1, com as etapas E0 a E2, é o mundo do POC sem a vista: tudo testável no Node;
  - o PR 2, com as etapas E3 e E4, traz a vista, as medições e a seção do resultado no fim deste documento.

## 6. Fora desta tarefa

- **O POC-01b** (o Rapier, `@dimforge/rapier3d-deterministic-compat`): fica opcional e separado, com tarefa própria, e só se o Matheus
  quiser medir antes de rever a W-1.
- **O Python e a paridade:** o POC é só TS. A física inteira só vai para `mundo.py` e `mundo.ts` com paridade na P4, com tarefa própria,
  atrás de chave desligada (W-4).
- **O cérebro A no mundo novo** (a P4): espera o Gate C (W-5).
- **O jogo:** nenhuma tela, versão de pet, save ou prancha nova.
- **O corpo químico:** o cérebro de teste usa uma fome e um tédio de brinquedo, sem os receptores.
- **Dois pets, o som, o cheiro e a curiosidade.**
- **Sprites direcionais:** o POC usa um quadro de frente, espelhado para os lados; se o atlas tem outras direções, isso fica Não
  verificado e anotado.

## 7. Critérios de aceitação

| critério da especificação (seção 8) | o que confere |
|---|---|
| o navegador renderiza o ambiente adequadamente | M1 no e2e e M3 com o artefato em `artifacts_v2_world_poc/` |
| o sprite permanece visualmente correto | M2, teste do e2e; a oclusão vista no screenshot do artefato |
| o corpo físico colide com objetos | G-COLISAO e G-BOLA, testes em `web/app/test/` |
| o pet consegue navegar até um alvo | G-NAVEGA (M4), teste |
| a física produz resultados observáveis | G-BOLA e o registro exportado: a bola empurrada se move, e o registro mostra quanto |
| o DigiBrain recebe observações sem depender da engine | G-FRONTEIRA e G-CONTRATO, testes que leem o fonte |
| a arquitetura atual continua funcionando | `npm test`, `npm run tipos`, `npm run e2e` e `python -m pytest tests/ -q` passam, com a contagem no PR; o build do app sai igual (G-FRONTEIRA) |

**A estimativa** (`docs/futuro/mundo_3d/poc_01.md`, seção 7; PROPOSTA, sem histórico para calibrar): de 5,5 a 8,5 dias de sessão para o
POC-01a, com estas hipóteses:
- um worker;
- o atlas na máquina;
- sem Python;
- um celular real para a M3.

## 8. Precisa do Matheus

**As três DECIDIDAS em 2026-10-19, pela recomendação** (o Matheus, pelo coordenador):

- **O celular da M3: DECIDIDO.** O Matheus faz a M3 abrindo a página num celular real. A página mostra os quadros por segundo na tela e
  os copia em JSON. O worker deixa as instruções prontas no PR 2. Sem a medida, a M3 fica Não verificada e o Gate A, parcial.
- **O limite da M3: DECIDIDO.** Os 30 quadros por segundo no celular são **referência, não gate duro**. O número segue sem fonte.
- **A dependência `three`: DECIDIDO.** Ela entra no `package.json` do app, **com a versão exata e sem faixa**: a `0.186.1`, publicada
  em 2026-09-24 (o registro do npm, `docs/futuro/mundo_3d/tecnologias.md`). A G-FRONTEIRA garante que o app não a importa.

## 9. Execução

As etapas entregues entram aqui, cada uma numa seção no fim deste documento.

## 10. Etapas E0 a E2, entregues (2026-10-19, PR 1)

**O mundo do POC, sem a vista**, em `web/app/poc/mundo3d/`. Nenhum arquivo importa o jogo nem o motor do jogo, e o contrário também não.

| arquivo | o que faz |
|---|---|
| `config.ts` | as constantes, todas PROPOSTAS e SEM FONTE: a sala de 16 × 12 células de 16 subunidades, o pet de raio 6 a 4 por tick, a bola de raio 4, o impulso 10, o atrito 1, a restituição 3/4, o cone de 120 graus e raio de 6 células, os bigodes de 2 células, a decisão a cada 15 ticks |
| `tipos.ts` | o contrato: a Observação (vistos com `ref`, `distancia` e `setor` relativo; os 8 bigodes; o contato; o resultado percebido; o corpo de brinquedo) e a Intenção (os 7 tipos da especificação, por `ref` ou por setor). Não importa nada |
| `inteiros.ts` | a conta inteira: o `divArred`, a raiz inteira, as 16 direções em tabela (sem trigonometria), o xorshift32, o FNV-1a e a derivação das sementes |
| `fisica.ts` | o círculo contra o retângulo e contra o círculo; o movimento uma subunidade por vez em cada eixo (nada atravessa, e o deslize sai sozinho); a bola com reflexão, restituição e atrito |
| `mundo.ts` | a sala (4 paredes, um obstáculo alto, um baixo), a bola, a comida e o pet. O passo de um tick: o pet anda, empurra a bola se bater nela, come o que alcança, e a comida comida volta numa célula livre sorteada pela rng do ambiente |
| `controlador.ts` | o A* inteiro (custo 10 e 14, sem cortar canto de sólido, desempate fixo), refeito a cada tick, e a execução da Intenção até chegar, ficar bloqueado, o alvo sumir ou dar a hora |
| `sensores.ts` | a leitura: o cone com oclusão (a linha inteira do centro ao centro; o alto tapa, o baixo não), os bigodes e o contato. O mapa `ref` → objeto fica com o simulador |
| `cerebro.ts` | o cérebro de teste: um decisor de regras, que não aprende e não é o cérebro A |
| `registro.ts`, `simulacao.ts` | o laço do contrato, com as duas rng (a do ambiente e a da política), o log de eventos (`avancar`, `deixar_comida`; um evento desconhecido falha alto), o replay e o registro por decisão |
| `sprite_reserva.ts` | o sprite de reserva, 16 × 16 com paleta, desenhado à mão (W-6) |
| `poc/mundo3d.html`, `pagina.ts`, `poc/vite.config.ts` | a página (nesta etapa, só o resumo da vida e o registro em JSON) e a config própria do Vite, que sai em `web/dist_poc/` (não versionado) |

**Os gates** (`web/app/test/poc_mundo3d.test.ts`, 31 testes no Node):
- **G-FRONTEIRA:** nenhum arquivo do POC, tirando a vista, importa o `three`. O POC só importa a si mesmo, e `motor/` e `src/` não
  importam o POC. A `vite.config.ts` e o `index.html` do app não citam o POC. O `three` tem versão exata (`0.186.1`). O mundo não usa o
  DOM, e o `npm run tipos` o compila sem a lib DOM (`tsconfig.poc.json`). Fora do teste: **o build do app sai idêntico ao da `main`**, o
  mesmo sha256 dos 3 arquivos de `web/dist/`, conferido na sessão com o `package.json` do POC e com o da `main`;
- **G-COLISAO:** contra a parede e no canto, o pet para encostado (o centro a `r` da face) e nunca a invade. Em diagonal, desliza. A
  bola a 40 por tick não atravessa uma parede de 2;
- **G-BOLA:** o empurrão passa o impulso na direção do contato. Solta a 10, a bola anda 10 + 9 + … + 1 = 55 e para. Contra a parede,
  reflete perdendo velocidade e não a invade;
- **G-NAVEGA (M4):** o pet chega à comida e a come nos 6 cenários: atrás do alto, contornando o alto, atrás do baixo, de canto a canto, do
  fundo para a frente e colado na parede. O A* não corta canto e devolve `null` para a célula dentro do obstáculo;
- **G-SENSOR:** o alto tapa a comida atrás dele e o baixo não. Nada fora do cone aparece. A Observação não tem nenhuma chave `x`, `y`,
  `pos`, `posicao` ou `id`. Os bigodes e o contato dão os setores relativos certos, e a leitura consome o contato;
- **G-CONTRATO:** o `cerebro.ts` só importa `./tipos.ts`, e o `tipos.ts` não importa nada;
- **G-DET (a primeira metade da M5):**
  - a mesma semente dá o mesmo estado e os mesmos registros, duas vezes;
  - o replay pelo log refaz a vida;
  - outra semente dá outra vida (o controle negativo);
  - um evento desconhecido falha alto;
- **o laço inteiro:** em 1.500 ticks o pet come e empurra a bola, o registro mostra quanto a bola andou, e o resultado percebido chega na
  Observação seguinte.

**O que fica para o PR 2:**
- a vista (`vista.ts`, com o Three.js) e as métricas M1, M2, M3 e M6;
- a segunda metade da M5: o mesmo hash no Node e no Chrome, pelo e2e;
- as instruções para o Matheus medir a M3 num celular real.

## 11. Etapas E3 e E4, entregues (2026-10-19, PR 2)

**A vista** (`web/app/poc/mundo3d/vista.ts`, o único arquivo do POC que importa o `three`; W-2, imperativo, sem react-three-fiber):
- **a câmera:** ortográfica e inclinada (M-2), com a elevação de 50 graus (PROPOSTA, sem fonte). Um número inteiro de pixels por
  subunidade, escolhido pelo tamanho da tela;
- **a sala:** o chão, as paredes e os obstáculos como caixas de cor lisa por face, sem luz. A parede da frente é baixa, para a sala
  aparecer;
- **o pet:** um `THREE.Sprite` com filtro nearest e um número inteiro de pixels por texel, com o pé do sprite alinhado ao pixel da tela.
  A sombra é um disco no chão. A bola é uma esfera, e a comida, uma caixa;
- **a oclusão:** três raios na direção do olhar (pelos pés, pelo centro e pelo topo do sprite). O sólido que eles cruzam antes do pet fica
  semitransparente. É só desenho: a visão do pet é a do motor;
- **sem gestão de cor e sem antialias:** a cor do texel chega à tela como está.

**A página** (`poc/mundo3d.html`, `pagina.ts`):
- o mundo anda 10 ticks por segundo, e a vista interpola o pet e a bola entre dois ticks. A interpolação é só desenho;
- o contador de quadros, o "Medir 10 s" (a M3, em JSON) e o "Baixar o registro";
- os ganchos `window.__poc` que o e2e usa;
- **o sprite:** o atlas do Digimon UP só no modo dev e só se existir na máquina (W-6); no build e com `?sprite=reserva`, o sprite de
  reserva.

**O e2e próprio** (`web/app/playwright.poc.config.ts`, `web/app/e2e_poc/mundo3d.spec.ts`): roda no build da página, servido pelo `vite
preview` na porta 8800, no Chrome instalado. O e2e do jogo não muda. Os scripts novos são `npm run poc:e2e`, `poc:preview` e `poc:medir`.

**As medidas** (`artifacts_v2_world_poc/`; todas só descritivas, exceto os gates que o teste confere):

| # | o que deu | artefato |
|---|---|---|
| M1 | a página abre, o WebGL existe e 68,86% dos pixels do canvas são da sala (não do fundo). O screenshot mostra a sala inclinada, os obstáculos, a bola, a comida e o pet | `e2e.json` (M1), `m1_sala.png` |
| M2 | nos quatro cantos da sala (as células (2, 2), (13, 2), (2, 9) e (13, 9)), **os 1.107 pixels do sprite batem com os texels, 0 divergentes**, com 3 pixels por texel e nenhum sólido cobrindo. Os 123 texels opacos do sprite de reserva cobrem 9 pixels cada | `e2e.json` (M2) |
| oclusão | o pet na célula (6, 2), atrás do obstáculo alto: só esse obstáculo fica semitransparente. 603 dos 1.107 pixels do sprite chegam misturados com a cor dele, e o resto, a cabeça acima do obstáculo, bate com os texels | `e2e.json` (oclusao), `oclusao.png` |
| M3 desktop | no Chrome headless desta máquina, 60 quadros por segundo de média, com o quadro de 16,7 ms na mediana e 16,8 ms no p95 (canvas de 1100 × 558, 3 pixels por subunidade). É o limite do vsync, e o headless não é o celular | `e2e.json` (M3_desktop_headless) |
| M3 celular | **falta:** é a medida do Matheus (abaixo) | — |
| M5 | o mesmo hash do estado no Chrome e no Node para as sementes 101, 202 e 303, com 1.500 e 3.000 ticks. O replay de 1 "dia" de sala (1.440 ticks, 95 decisões fechadas) leva 7,8 ms no Node, a mediana de 5, num i7-14700KF | `e2e.json` (M5_chrome_node), `node.json` (M5_replay_node) |
| M6 | o build da página tem 559.066 bytes, 141.735 em gzip, quase todo o `three` | `node.json` (M6_build) |

**O atlas no modo dev** (conferido na sessão, sem artefato: a arte fica fora do repositório):
- o sprite `brasa_crianca_sereno` aparece na sala, com 1 pixel por texel (meia subunidade por texel, com 3 pixels por subunidade);
- a M2 dele dá 36 divergentes em 1.410 pixels, provavelmente nas bordas semitransparentes da arte. Não verificado.

**O app do jogo continua idêntico:** o sha256 dos 3 arquivos de `web/dist/` é o mesmo com o `package.json` deste PR e com o da `main`.

### A M3 no celular: as instruções para o Matheus

1. No PC, em `web/app`:

   ```bash
   npm run poc:build
   ```

   ```bash
   npm run poc:preview -- --host
   ```

   O Vite mostra um endereço "Network", como `http://192.168.0.10:8800/`. Se o Windows perguntar, permita o Node na rede privada.
2. No celular, **na mesma rede Wi-Fi**, abra `http://<o endereço Network>:8800/mundo3d.html`.
3. Espere uns 5 segundos com a página aberta e o pet andando. Toque em **"Medir 10 s"** e não mexa na tela até o botão voltar.
4. A medida aparece em JSON na caixa embaixo. No http do celular a cópia automática não funciona: segure o texto, selecione tudo e
   copie.
5. Cole o JSON num comentário do PR ou mande ao coordenador. O worker o grava como `artifacts_v2_world_poc/m3_celular.json`.

A referência é **30 quadros por segundo** no celular (DECIDIDO: referência, não gate duro). Se der menos, a medida é registrada como está.
