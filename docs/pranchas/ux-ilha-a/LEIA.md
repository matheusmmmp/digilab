# Prancha da ilha A, "Objetos que falam"

Esta é a direção A da ilha interativa (UX_TELA_PET, 2026-11-07). Referências: The Sims e Creatures. O jogador toca no mundo, o objeto diz
o seu estado e o fio tracejado mostra para onde o cérebro levou o pet. O pedido do Matheus foi "Siga com as recomendações". A prancha é
só desenho, sem código do jogo, e foi desenhada sobre capturas reais da Tela Pet. As perguntas estão no [PERGUNTAS.md](PERGUNTAS.md).

## As imagens

Ficam em `D:\Trab\digilab\capturas_ux_ilha_aprovar\prancha_a\`, fora do git (UX-8). São 30 imagens:
- `ilha_a_<estado>_<1920|390>_<vidro|militar>.png`, as telas;
- `ilha_a_<estado>_<1920|390>_vidro_notas.png`, com o número sobre cada elemento e a legenda da fonte ao lado. Em vermelho, as lacunas.

| estado | o que mostra | quadro real |
|---|---|---|
| `nada_tocado` | a ilha limpa: só os selos dos lugares (o saco e a barraca) | semente 6503, 14:24, dormindo |
| `etiqueta_aberta` | o cartão da tigela aberto (1 ração, o aprendido, "Servir ração"); a etiqueta curta da bola no hover (só desktop) | o mesmo |
| `fio_toque_pet` | o toque no pet (anel no chão), o fio até a bola, "Brincar 36 %" e "Brinca menos" | semente 6503, 13:31, brincando |
| `indo_tigela` | o pet indo até a tigela: o fio aparece sozinho, com "Comer 97 %" | semente 6521, 00:37 a 00:44, comendo |
| `toque_arvore` | o toque na árvore: só o nome e "sem frutas nesta ilha" (lacuna) | semente 6503, 14:24 |

O `indo_tigela` é de outro momento real, à noite. Nas sementes testadas, o pet com a rotina do Alimentar a cada 2 h não estava longe da
tigela com fome durante o dia (`fonte/sonda_noite.mjs`).

## Os cinco pontos e a fonte de cada um no motor

| ponto | o que a prancha mostra | fonte no motor (TS do jogo) | situação |
|---|---|---|---|
| 1. Etiquetas nos objetos | a tigela com o número de rações maduras; a bola pelo nome | `Motor.mundo.comidas` e `situacao(c, tick)`; `bolaEm(tick)` (`web/app/motor/mundo.ts`) | tem |
| 1. O número de frutas na árvore | "sem frutas nesta ilha" | o jogo roda o `CMU_MVP`, sem árvores; as frutas só existem no Python | **lacuna** (I1-3) |
| 2. Tocar faz o gesto | "Servir ração" no cartão da tigela | `Motor.observar("alimentar")`, o mesmo do botão (`acoes.ts`); a bola pelo `deixarBola` | tem; a barra continua |
| 2. Sacudir a árvore | nada | não existe gesto de sacudir nem no Python | **fora** (I1-3) |
| 3. O fio com a chance | o fio do pet ao alvo, "Brincar 36 %" e "Comer 97 %" | a chance: `Motor.digibrain().decisao.chances`; o alvo: o `pendente` do `Mundo`, que é privado | chance tem; alvo pede um getter só de leitura (I1-2) |
| 4. O progresso dos lugares (o saco) | "0 hoje" e o visto | os eventos `tr` do registro no dia; `TreinoPet.podeTocar(tick)` (`motor/treino.ts`) | tem |
| 4. O diário novo (a barraca) | o ponto rosa | o jogo não guarda o que o dono já leu | **lacuna** (I1-5) |
| 5. O que aprendeu | "Brinca menos" (−0,11) e "Nada novo sobre comer" | `Motor.digibrain().aprendido`, o desvio aprendido por ação; a vista liga a ação ao objeto | tem; o paladar não existe no TS (I1-8) |

Nada aqui pede mudança no motor. A única coisa fora da vista é o getter só de leitura do alvo (I1-2), e ela depende do ok do Matheus.

## O desenho

- **A etiqueta curta** tem ícone, número e rótulo curto, e fica presa ao topo do objeto por uma ponta. Aparece no hover, no toque e quando o
  objeto é o alvo atual. No alvo atual, ela leva a chance no lugar do nome.
- **O cartão do toque** traz o nome, o número, uma linha do que o pet aprendeu e o gesto do motor. Fecha no ×. A 1920 abre ao lado do objeto;
  a 390, embaixo dele, acima da barra de ações.
- **O fio** é tracejado, na cor do escolhido (`--hx-escolhido-borda`), e termina num anel em volta do alvo. Faz uma curva que contorna o
  sprite e nunca passa por cima do pet. O toque no pet é um anel no chão, aos pés dele. Nada se acrescenta ao sprite.
- **Os selos dos lugares** são pequenos e ficam sempre à vista. Cedem ao balão do pet quando os dois se sobrepõem (I1-6).
- **As cores** são só os tokens `--hx-*` e `--hud-*`, lidos direto de `web/app/src/estilo/tokens.css` e `pele-xcom.css`. Não há cor hex
  nova. As medidas (a altura de 34 px da etiqueta, a largura de 300 px do cartão, o traço do fio, os 3 s e os 6 s) são de layout:
  PROPOSTO, SEM FONTE.

## O que a direção C vai precisar depois (para a A não a impedir)

A C é "Ilha que cresce": as áreas trancadas pelo nível do Tamer em malha e sem cor, o achado do dia, os rastros e a nota da ilha.
- **As áreas trancadas não ganham etiqueta nem fio.** O cérebro não escolhe alvo fora do mapa do motor. A camada da C (a malha) fica por
  baixo das etiquetas e dos selos da A, e a ordem de desenho tem de deixar isso possível.
- **Os selos dos lugares viram uma família.** A C precisa de um selo para a área trancada ("Nv 5", o cadeado de hoje, `CadeadosDaIlha.tsx`)
  e de outro para o achado do dia. O componente do selo da A tem de aceitar ícone, número e estado (aberto, trancado, novo).
- **O achado do dia é um objeto que fala.** Ele usa a mesma etiqueta e o mesmo cartão da A, e por isso o cartão não pode ser só da tigela.
  O conteúdo vem de uma tabela da vista: objeto, ícone, a leitura do motor e o gesto.
- **Os rastros reaproveitam o traço do fio,** mas noutra cor e sem anel. A C tem de usar outro token (o aprendido ou o rótulo), para o rastro
  não parecer intenção.
- **A nota da ilha** disputa espaço com o cartão da A no celular. Fica a regra de um cartão aberto por vez.
- **O "lido" do diário (I1-5)** é a mesma marca que a nota da ilha vai usar. Se a A guardar a última abertura só na vista, a C reaproveita.
- **Nada da A muda o motor, o save ou o replay.** A C pede o mesmo: o que for novo no jogo (o achado do dia, se tiver efeito no pet) vira
  tarefa de motor própria, atrás de uma chave.

## Refazer

Os fundos: copie `fonte/capturar_fundo.spec.ts` para `web/app/e2e/_cap_ilha_a.spec.ts`, com `fonte/save_dia.json` como
`e2e/_save_dia.json` e `fonte/save_noite.json` como `e2e/_save_ilha_a.json`. Rode o build e depois os quatro comandos, em `web/app`:

```bash
DIGILAB_PORTA_E2E=8811 npx playwright test e2e/_cap_ilha_a.spec.ts --workers=2   # a noite, prefixo q (CAP_N=36, CAP_PASSO=150)
CAP_SAVE=./_save_dia.json CAP_PREF=d CAP_N=12 CAP_PASSO=1500 DIGILAB_PORTA_E2E=8811 npx playwright test e2e/_cap_ilha_a.spec.ts --workers=2
CAP_SAVE=./_save_dia.json CAP_PREF=b CAP_N=30 CAP_PASSO=120 DIGILAB_PORTA_E2E=8811 npx playwright test e2e/_cap_ilha_a.spec.ts --workers=2
```

O spec temporário sai de `e2e/` depois. A worktree precisa da pasta `Assets` ao lado (uma junção para `D:\Trab\digilab\Assets`), senão o
atlas dá 404. Depois rode, nesta pasta, `python gerar_dados.py` e `sh capturar.sh`, com `python -m http.server 8766 --bind 127.0.0.1` de pé
em `D:\Trab\digilab`. O tempo do jogo anda em tempo real, então os quadros podem cair alguns ticks diferentes. O `gerar_dados.py` falha alto
se o quadro escolhido faltar.
