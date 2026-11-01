# TAREFA V3 — LUTA_LAYOUT: a luta dentro do layout habitat, a B3 (2026-11-01)

Coordenador: Gerente da V3 (Claude Code). Worker: Claude Code, Sonnet 5.5 (a etapa de papel). Worktree e branch: `v3-luta-layout`. Status: etapa 1 (papel) ENTREGUE e aprovada pelo Matheus em 2026-11-01 (pranchas e B3-1 a B3-5); a etapa 2 (código) está liberada e ainda não começou.

Categoria: implementacao. Origem: Claude Code, 2026-11-01: B3 do `docs/PLANO_V3.md` (seção 4), pedida pelo Gerente da V3 depois da B2 (#504) e da L2, com a regra de o Matheus aprovar as pranchas antes do código.

## 1. Pergunta

Sem hipótese de pesquisa: é trilha B (batalha) com a trilha L (layout). **A luta em tempo real chega ao mesmo sistema visual da tela Pet (HUD em caixas de vidro ou militares, cena a tela cheia, dock de ações), nas duas peles, sem mudar uma linha do motor da luta e sem mostrar nada que o motor não registre?**

## 2. Depende de

- A L1 (layout habitat, HUD) e a L2 (as peles Vidro e Militar) na `main`: ambas estão (`f69befa`).
- A B2 (#504): a luta que a tela mostra é a da v14; a B3 não muda fator, relógio, lista nem regra.
- O ok do Matheus nas pranchas (`docs/pranchas/b3/`) e nas decisões B3-1 a B3-5 (seção 8): **dado em 2026-11-01, "Aprovo todas"**.

## 3. Mudança mínima

### 3.1 O que a tela da luta tem hoje (a única coisa que as pranchas mostram)

Lido de `TelaLuta.tsx`, `palcoTR/PalcoTR.tsx` e `palcoTR/desenhoTR.ts` (só leitura nesta etapa):

| item | origem no motor/tela |
|---|---|
| nome Digimon dos dois lutadores, retrato, vida e guts de cada um | `LutadorTela`, `HudLado` |
| relógio da luta (`m:ss`), o limite ("até 1:20") ou "morte súbita" | `p.segundos`, `CTR_TR.limite`, `p.morteSubita` |
| o modo e o contexto: Arena (treino), Fronteira, Campanha; "luta k de n", "vitória k", Liga, Cidadela, Lago, instalação, Salão, carta em jogo | `p.serie`, `p.sequencia`, `p.liga`, `p.arena`, `p.carta`, `sparringTexto` |
| os números que sobem sobre quem levou: dano, cura, "errou", "interrompido!"; o grito (`callout`) | `VisualTR`, `p.callout` |
| a regra em uso e a frase "o que <pet> faz" (só leitura) e o texto do último evento | `textoRegra`, `p.regra`, `p.texto` |
| Pausar, ×2 e Desistir (que pede confirmação); no replay, "Sair do replay" e o "Fim do replay" | `alternarPausa`, `alternarRapido`, `ConfirmarDesistir`, `FimReplay` |
| avisos de falha: atlas ou mapa que não carregou | `luta-aviso-asset` |

O que **não** existe e as pranchas não inventam: idade do pet, ataque nomeado em cartão, barra de combo, minimapa, histórico de golpes, dica ou placar entre as lutas. O modal Resultado (`ModalResultado.tsx`) e a prévia da Arena ficam fora desta tarefa (ver a seção 6).

### 3.2 O desenho (as pranchas, `docs/pranchas/b3/`)

390 px e 1280 px, nas peles Vidro (padrão) e Militar; as capturas estão em `docs/pranchas/b3/capturas/`. A decisão D10 do tema fixa as capturas finais em 1920×950 (monitor do Matheus); as pranchas ficam em 1280 px, a largura que a tarefa pediu, e a 1920×950 só muda a escala do palco (B3-2).

- **A cena** (o mapa do UP do lugar e os dois lutadores) ocupa a **tela inteira**, atrás de tudo, como o habitat na tela Pet. O chão com os lutadores fica no terço de baixo. A faixa "Luta · Arena" e a moldura da cena de hoje saem.
- **O HUD do topo** é a mesma linguagem da tela Pet (`.hud-caixa`, tokens `--hud-*` e `--hx-*`): uma plaquinha por lutador (retrato, nome, vida, guts; a do rival espelhada e com a borda em `--hx-perigo`), com o relógio entre elas (TEMPO, `m:ss`, "até 1:20" ou "morte súbita"). Logo abaixo do relógio, uma etiqueta com o modo ("Arena · treino", "Campanha · Luta 2 de 3"…), no lugar do título de hoje.
- **A regra em uso** é um cartão de vidro (ou militar) com a frase "o que <pet> faz": no desktop, à direita, sob o HUD (a pilha da direita da tela Pet); no celular, uma faixa de uma ou duas linhas acima do dock. Só leitura.
- **O dock da luta**, no rodapé central, como o da tela Pet: Pausar e ×2 juntos (o escolhido no tom de "escolhido" da pele), um separador, e Desistir à parte, com o texto e a borda em `--hx-perigo`. Alvos de 48 px. Desistir continua pedindo confirmação.
- **Avisos de contexto** (série, Liga, carta, Lago, instalação): ficam no lugar da etiqueta do modo, num cartão compacto no alto ao centro, sob o relógio, como o chamado da tela Pet (HUD-4); no celular, abaixo do HUD, uma linha. O texto é o de hoje.
- **As duas peles** vêm dos tokens que já existem (`tokens.css`, `pele-vidro.css`, `pele-xcom.css`): Vidro com chanfro, reflexo, trecho de luz e desfoque; Militar reta, com a linha de topo e os cantos em L. **Nenhum token novo.**

### 3.3 O que muda quando vier o código (etapa 2, depois do ok)

| arquivo | mudança | disputado (L)? |
|---|---|---|
| `web/app/src/telas/lutar/TelaLuta.tsx` | a estrutura do topo: some a faixa do título, entra a etiqueta do modo e o cartão de contexto; o dock (Pausar, ×2, Desistir) sobe do `PalcoTR` e do cabeçalho para um só lugar | não |
| `web/app/src/telas/lutar/palcoTR/PalcoTR.tsx` | o HUD vira as plaquinhas e o relógio; a regra em uso vira o cartão; o dock; mesmos `data-testid` (`luta-relogio`, `luta-regra`, `luta-carta`) e mesmos `aria-label` | não |
| `web/app/src/telas/lutar/palcoTR/desenhoTR.ts` | só a apresentação do canvas (o fundo a "cobrir" a tela, a escala inteira dos sprites no chão novo); **a simulação e o motor não são tocados** | não |
| `web/app/src/estilo/luta_hud.css` (novo) | as caixas da luta e o dock; os regimes 390 e ≥ 900 px | não |
| `web/app/src/estilo/abertas.css`, `lutar.css`, `pele-vidro.css`, `pele-xcom.css` | tirar ou trocar as regras `.luta-tela.ab-hx …` que o CSS novo substitui | não |
| `web/app/src/App.tsx` | **só se a B3-1 for "com trilho"**; com a recomendação ("sem trilho"), nada | **sim** |
| `web/app/src/componentes/Nav.tsx` | idem: só se a B3-1 mudar | **sim** |
| `web/app/src/estilo/tokens.css`, `pet.css` | **nenhuma mudança prevista**; se aparecer necessidade, parar e avisar o Gerente | **sim** |
| `web/app/e2e/` e `web/app/e2e_capturas/` | o e2e da luta confere a estrutura nova; as capturas do portão não são regeneradas aqui (como na B2): a T3 as refaz | não |

**O que NÃO muda:** `web/app/motor/` (a luta, o relógio, os fatores, as listas da v14, o aprendizado), o Python, `digilab/engine.py`, os eventos do log, o replay e todos os gabaritos; a lógica de `luta.ts` (relógio da animação, pausar, ×2, pular); o modal Resultado; as outras telas de Lutar; as rotas (`#/lutar/luta`); os nomes Digimon e os ids internos. **Nenhum número novo de jogo.**

## 4. Experimento e gate (se houver run)

Não há run de pesquisa. O gate é visual e de regressão: nenhum gabarito muda, e a luta refeita do registro dá o mesmo resultado quadro a quadro.

## 5. Entrega

**Etapa 1 (esta, só papel):** esta tarefa, as pranchas (`docs/pranchas/b3/luta_390.html`, `luta_1280.html`, `luta.css`, `gerar.py`, `capturar.sh`), as quatro capturas (390 e 1280 px × Vidro e Militar) no PR e no corpo dele. Nada em `web/app/src/` muda. Um PR contra a `main`, no modelo `.github/pull_request_template.md`, conferido com `python tools/verificar_relato.py`. O merge é só do Matheus.

**Etapa 2 (código, só depois do ok):**

- Testes planejados, em `web/app` (no máximo 4 processos):
  1. `npm run tipos` e `npm test`: o `motor_sem_dom`, a paridade e os gabaritos passam **sem regravar nenhum** (`git diff origin/main -- web/app/test/gabaritos/` vazio);
  2. teste de componente da `TelaLuta`: os `data-testid` e os `aria-label` de hoje existem; o relógio mostra `m:ss`, "até 1:20" e "morte súbita" nos casos certos; o cartão de contexto mostra o texto de série, Liga, carta e Lago;
  3. o replay de uma luta v14 e de uma v13 dá o mesmo estado quadro a quadro, antes e depois (o desenho não pode mexer na simulação);
  4. `hx_pele.test.ts` estendido: o contraste do texto das caixas da luta nas duas peles, sobre o pior caso dos mapas (o coliseu e o ringue claros);
  5. `npm run e2e` (Chrome, porta 8799): a luta de ponta a ponta nas duas peles em 390, 1280 e 1920×950: alvos ≥ 44 px, sem rolagem horizontal, Pausar/×2/Desistir funcionam, Desistir pede confirmação, o Voltar do navegador continua pedindo Desistir, o foco volta ao botão de origem, o fim vai ao Resultado;
  6. o e2e de `prefers-reduced-transparency` e `prefers-reduced-motion` (o vidro fica opaco; sem animação nova).
- Registro: se houver desvio, uma seção no fim de `docs/registro/2026-11.md` e uma linha no fim de `docs/REGISTRO_DESVIOS.md`, com o mesmo título e LF.
- O resumo da etapa 2 numa seção "Resultado" no fim deste documento e no corpo do PR; o Gerente põe a linha no `docs/PAINEL_V3.md`.

## 6. Fora desta tarefa

- O motor da luta e tudo o que a B2 ligou; qualquer número de equilíbrio (a rodada 3 é outra missão).
- O modal **Resultado**, a **prévia** da Arena (a cena parada com "escolha um rival"), as abas da Arena, Campanha, Fronteira e Medalhas, o mapa de Exploração.
- Elementos de HUD que o motor não tem (ver a seção 3.1).
- A regeneração das capturas do portão (a T3 da trilha L).
- A luta 3D ou a troca do cenário pela ilha 3D (L4); o canvas continua 2D.

## 7. Critérios de aceitação

Da etapa 1:

- `docs/TAREFA_V3_LUTA_LAYOUT.md` existe, com as decisões B3-1 a B3-5 (recomendação e custo de errar).
- As pranchas existem em `docs/pranchas/b3/` e as quatro capturas (390 e 1280 px × Vidro e Militar) estão no PR; `git diff --stat origin/main` não toca em `web/app/`.
- A prancha mostra só o que a seção 3.1 lista, com nomes Digimon (Gabumon e Monochromon, os do jogo) e os sprites do projeto.

Da etapa 2 (para depois):

- A luta é desenhada como nas pranchas aprovadas, nas duas peles, a 390, 1280 e 1920×950.
- Nenhum arquivo de `web/app/motor/` e nenhum gabarito muda; `npm test`, `npm run tipos` e `npm run e2e` passam, com as contagens no PR.
- `App.tsx`, `Nav.tsx`, `tokens.css` e `pet.css` ficam como estão (com a B3-1 recomendada).

## 8. Precisa do Matheus

Cada uma com a recomendação e o custo de errar. Nenhuma é número de jogo.

| # | decisão | recomendação | custo de errar | estado |
|---|---|---|---|---|
| **B3-1** | a navegação durante a luta: **sem trilho nem barra** (hoje é assim, `body.tela-cheia`) ou com o trilho do desktop e a barra do celular visíveis sobre a cena | **sem.** A luta é um momento fechado: Desistir é o único jeito de sair, com confirmação, e o Voltar do navegador já vira esse pedido | com o trilho, sair por outro destino no meio da luta vira um segundo caminho de desistência (precisa de confirmação própria) e mexe em `App.tsx` e `Nav.tsx` (arquivos disputados); no celular a barra tira 64 px do palco | **DECIDIDA, 2026-11-01: pela recomendação** ("Aprovo todas") |
| **B3-2** | o palco: a cena a **tela inteira** atrás do HUD (as pranchas) ou a moldura de hoje, só trocando a pele | **tela inteira.** É o que o habitat faz na tela Pet e dá o palco que o monitor de 1920×950 pede | o mapa do UP é mais largo que alto e é recortado nas bordas (a "cobrir"); a escala inteira dos sprites no chão novo precisa ser refeita e conferida a 1920×950. Se o recorte feio aparecer, a moldura volta com pouco retrabalho | **DECIDIDA, 2026-11-01: pela recomendação** ("Aprovo todas") |
| **B3-3** | a regra em uso: cartão à direita no desktop e faixa embaixo no celular (as pranchas), ou sempre embaixo, ou recolhível | **à direita no desktop, faixa no celular, sempre visível** (a regra é o que explica a luta; é o ensino do aprendiz) | à direita o cartão cobre ~300 px da cena em 1280 (como a pilha da tela Pet, HUD-2); no celular a faixa tira ~70 px do palco. Recolhível esconderia justamente a leitura que o jogo quer dar | **DECIDIDA, 2026-11-01: pela recomendação** ("Aprovo todas") |
| **B3-4** | os controles: dock no rodapé central (as pranchas) ou no cabeçalho, como hoje | **dock no rodapé.** Alinha com o dock da tela Pet e leva Desistir para longe do relógio e do HUD | o polegar no celular chega bem ao rodapé; no desktop o mouse anda mais. Desistir à parte, com a cor de perigo e a confirmação, não é toque acidental | **DECIDIDA, 2026-11-01: pela recomendação** ("Aprovo todas") |
| **B3-5** | os avisos de contexto (série, Liga, carta, Lago, instalação): um cartão compacto sob o relógio (as pranchas), ou em linhas largas sobre a cena como hoje | **cartão compacto no alto ao centro**, com o mesmo texto de hoje; no celular, uma linha sob o HUD | o texto de série e de Liga é longo (duas frases): em 390 px ele vira duas ou três linhas e cobre o céu da cena; se incomodar, vai para dentro do cartão da regra (troca barata) | **DECIDIDA, 2026-11-01: pela recomendação** ("Aprovo todas") |

Já decididas e que esta tarefa só aplica: as duas peles e o padrão Vidro (TM1 a TM5), o layout habitat e o HUD (HUD-1 a HUD-4), a v14 (B2, CV14-1), as capturas em 1920×950 (D10).
