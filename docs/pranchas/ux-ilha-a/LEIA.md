# Prancha da ilha A, "Objetos que falam"

Esta é a direção A da ilha interativa (UX_TELA_PET, 2026-11-07). Referências: The Sims e Creatures. O jogador toca no mundo, e o objeto
diz o seu estado. O pedido do Matheus foi "Siga com as recomendações". A prancha é só desenho, sem código do jogo, sobre capturas reais da
Tela Pet. As perguntas e as decisões estão no [PERGUNTAS.md](PERGUNTAS.md).

**Rodada 2 (a resposta do Matheus está no PERGUNTAS.md):**
- não há fio nenhum;
- clicar no pet é carinho, e segurar o pega e o leva para qualquer lugar do mapa (a PEGAR_PET, que já está no jogo);
- tocar na árvore a sacode e faz cair uma fruta, o que pede motor novo;
- as outras perguntas seguem a recomendação.

As capturas da rodada 1 ficaram em `capturas_ux_ilha_aprovar/prancha_a/antes/`. As da rodada 2 foram refeitas sobre a main com o #689 (os
modelos 3D do portão e da barraca e o pegar o pet), com pets v19.

## As imagens

Ficam em `D:\Trab\digilab\capturas_ux_ilha_aprovar\prancha_a\`, fora do git (UX-8). São 30 imagens:
- `ilha_a_<estado>_<1920|390>_<vidro|militar>.png`, as telas;
- `ilha_a_<estado>_<1920|390>_vidro_notas.png`, com o número de cada elemento e, ao lado, a legenda da fonte. Em vermelho, o que pede motor
  novo.

| estado | o que mostra | quadro real (pet v19) |
|---|---|---|
| `nada_tocado` | a ilha limpa: só os selos dos lugares (o saco e a barraca) | semente 6503, 15:37, dormindo |
| `etiqueta_aberta` | o cartão da tigela aberto (1 ração, o aprendido, "Servir ração"); a etiqueta curta da bola no hover (só desktop) | o mesmo |
| `segurar_pet` | o pet na mão, como o jogo já o desenha (PEGAR_PET); a prancha só marca o dedo ao lado | semente 6503, de 13:33 a 13:38, brincando |
| `indo_tigela` | o pet indo até a tigela, sem fio; a tigela é o alvo atual e mostra a etiqueta "7 rações" | semente 6521, de 00:39 a 00:43, comendo |
| `toque_arvore` | o toque na árvore: ela sacode e cai uma fruta (pede motor novo) | semente 6503, 15:37 |

O `indo_tigela` é de outro momento real, à noite. Nas sementes testadas, o pet com a rotina do Alimentar a cada 2 h não estava longe da
tigela com fome durante o dia (`fonte/sonda_noite.mjs`).

## Os pontos e a fonte de cada um no motor

| ponto | o que a prancha mostra | fonte no motor (TS do jogo) | situação |
|---|---|---|---|
| 1. Etiquetas nos objetos | a tigela com o número de rações maduras; a bola pelo nome | `Motor.mundo.comidas` e `situacao(c, tick)`; `bolaEm(tick)` (`web/app/motor/mundo.ts`) | já existe |
| 1. A etiqueta do alvo atual | a tigela quando o pet vai até ela | o tipo do alvo pendente da percepção (`alvo_pendente`) e a ração na tigela | já existe, sem getter novo |
| 2. Tocar faz o gesto | "Servir ração" no cartão da tigela | `Motor.observar("alimentar")`, o mesmo do botão (`acoes.ts`); a bola pelo `deixarBola` | já existe; a barra continua |
| 2. Clicar e segurar o pet | clicar = carinho; segurar = levar o pet | `acariciar` (`ToquePet.tsx`); `Motor.levarPet`, o evento `lp` (`PegarPet.tsx`) | já está no jogo (I1-1) |
| 2. Sacudir a árvore | a copa sacode e cai uma fruta | o jogo roda o `CMU_MVP`, sem frutas no TS; o Python tem as frutas, mas não o sacudir | **pede motor novo** (I1-3) |
| 3. O fio da intenção | nada | — | **saiu** (o Matheus: "Não tem fio nenhum") |
| 4. O progresso dos lugares (o saco) | "0 hoje" e o visto | os eventos `tr` do registro no dia; `TreinoPet.podeTocar(tick)` (`motor/treino.ts`) | já existe |
| 4. O diário novo (a barraca) | o ponto rosa | a última abertura do Diário, guardada só na vista (`localStorage`) | decidido (I1-5) |
| 5. O que aprendeu | "Nada novo sobre comer" (no cartão da tigela) | `Motor.digibrain().aprendido`, o desvio aprendido por ação; a vista liga a ação ao objeto | já existe; o paladar vem com a I1-3 |

Nesta etapa nada muda o motor. A árvore que dá fruta é uma tarefa de motor própria, descrita na I1-3 do PERGUNTAS.md.

## O desenho

- **A etiqueta curta** tem ícone, número e rótulo curto, presa ao topo do objeto por uma ponta. Aparece no hover, no toque e quando o objeto
  é o alvo atual. No alvo atual, a borda fica na cor do escolhido.
- **O cartão do toque** traz o nome, o número, uma linha do que o pet aprendeu e o gesto do motor. Fecha no ×. A 1920, abre ao lado do
  objeto; a 390, embaixo dele, acima da barra de ações.
- **O pet na mão** é o desenho de hoje do jogo: suspenso, balançando, com a sombra onde vai cair. A prancha só põe o ícone de agarrar ao
  lado do sprite. Nada se acrescenta ao sprite.
- **A árvore sacudida** tem um anel no toque, traços curtos dos dois lados da copa, um tracejado da queda e a fruta no chão com a etiqueta
  "Fruta". No jogo, a fruta seria o modelo que a vista já tem (`ilha/itens.ts`).
- **Os selos dos lugares** são pequenos e ficam sempre à vista. Saem quando ficam sob o balão do pet (I1-6).
- **As cores** são só os tokens `--hx-*` e `--hud-*`, lidos direto de `web/app/src/estilo/tokens.css` e `pele-xcom.css`. Não há cor hex
  nova. As medidas (a altura de 34 px da etiqueta, a largura de 300 px do cartão, o tremor da copa, os 6 s) são de layout: PROPOSTO, SEM
  FONTE.

## O que a direção C vai precisar depois (para a A não a impedir)

A C é "Ilha que cresce": as áreas trancadas pelo nível do Tamer, em malha e sem cor, o achado do dia, os rastros e a nota da ilha.
- **As áreas trancadas não ganham etiqueta, e o pet não pode ser solto nelas.** Hoje o `levarPet` põe o pet na borda mais próxima do mapa
  (PP-4), e a C vai precisar da mesma regra para a área trancada. A camada da C (a malha) fica por baixo das etiquetas e dos selos da A.
- **Os selos dos lugares viram uma família.** A C precisa de um selo para a área trancada ("Nv 5", o cadeado de hoje, `CadeadosDaIlha.tsx`)
  e de outro para o achado do dia. O componente do selo da A tem de aceitar ícone, número e estado (aberto, trancado, novo).
- **O achado do dia é um objeto que fala.** Ele usa a mesma etiqueta e o mesmo cartão da A, e por isso o cartão não pode servir só à tigela.
  O conteúdo vem de uma tabela da vista: o objeto, o ícone, a leitura do motor e o gesto.
- **A árvore que dá fruta (I1-3) é a primeira fonte de achados.** Se a C quiser um achado por dia, ele pode sair do mesmo motor das frutas, e
  não de uma mecânica à parte.
- **Os rastros** são traços no chão. Usam outro token (o aprendido ou o rótulo), para não parecerem um caminho a seguir.
- **A nota da ilha** disputa espaço com o cartão da A no celular. Fica a regra de um cartão aberto por vez.
- **O "lido" do diário (I1-5)** é a mesma marca que a nota da ilha vai usar. Como a A guarda a última abertura só na vista, a C pode
  reaproveitar.
- **A A não muda o save nem o replay.** A C pede o mesmo: o que for novo no jogo (o achado do dia, se tiver efeito no pet) vira tarefa de
  motor própria, atrás de uma chave.

## Refazer

**Os arquivos.** Os fundos saem do spec `fonte/capturar_fundo.spec.ts`, copiado para `web/app/e2e/_cap_ilha_a.spec.ts`. Os saves vão junto:
- `fonte/save_dia.json` como `e2e/_save_dia.json`;
- `fonte/save_noite.json` como `e2e/_save_ilha_a.json` (o `fonte/sonda_noite.mjs` com o argumento 1400 o refaz).

**Os comandos.** Rode o build e depois estes comandos, em `web/app`:

```bash
CAP_ESPERA=3500 CAP_N=40 CAP_PASSO=150 DIGILAB_PORTA_E2E=8811 npx playwright test e2e/_cap_ilha_a.spec.ts --workers=2
```

```bash
CAP_SAVE=./_save_dia.json CAP_PREF=d CAP_N=12 CAP_PASSO=1500 DIGILAB_PORTA_E2E=8811 npx playwright test e2e/_cap_ilha_a.spec.ts --workers=2
```

```bash
CAP_PEGAR=1 CAP_ESPERA=300 CAP_SAVE=./_save_dia.json CAP_PREF=p CAP_N=2 CAP_PASSO=200 DIGILAB_PORTA_E2E=8811 npx playwright test e2e/_cap_ilha_a.spec.ts --workers=1
```

- O primeiro comando faz a noite, com o prefixo `q`. O Vidro a 390 saiu de uma segunda passada, com `CAP_PREF=r`, `CAP_PASSO=100` e
  `-g "vidro 390"`.
- O pegar roda um teste por vez. O pet tem de estar acordado quando é pego, e com dois testes juntos a carga atrasa e ele dorme antes.
- No fim, o spec temporário sai de `e2e/`.

**O que a máquina precisa.** A worktree precisa da pasta `Assets` ao lado (uma junção para `D:\Trab\digilab\Assets`), senão o atlas dá 404.
O servidor `python -m http.server 8766 --bind 127.0.0.1` fica de pé em `D:\Trab\digilab`. Com ele no ar, rode nesta pasta
`python gerar_dados.py` e `sh capturar.sh`.

**O que conferir.** O tempo do jogo anda em tempo real, então os quadros podem cair alguns ticks diferentes. As posições marcadas à mão (o
`MAO` do `gerar_dados.py`) precisam ser conferidas. O `gerar_dados.py` falha alto se o quadro escolhido faltar.
