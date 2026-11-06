# Três propostas de layout para a tela Pet (UX_TELA_PET, 2026-11-05)

Tarefa: `docs/TAREFA_V3_UX_TELA_PET.md`. Status: **PROPOSTO**; a escolha é a UX-1 (seção 8 da tarefa). Nenhuma proposta toca o motor
(`web/app/motor/`), o save, as rotas ou o hash, nem cria número de jogo; todas leem só o que a tela já lê hoje por `useJogo()`.

## 0. O formato e o ponto de partida

Cada proposta é um plano de design em texto, no formato que o `ux-designer` vai usar (tarefa, seção 3.2): o objetivo do jogador nesta
tela, a hierarquia, o que fica sempre visível, o que aparece por gesto, as cores pelos tokens (`docs/UI_GUIDELINES.md` seção 4, os
`--hx-*` de `src/estilo/tokens.css` e a paleta `--hud-*` da HUD-5; **nenhuma cor hex nova**), os wireframes a 1920×950 (o monitor do
Matheus, D10) e a 390×844, o que muda na leitura do estado do pet e o custo em determinismo e em e2e.

Nos wireframes, uma coluna vale ~20 px a 1920 e ~10 px a 390; os números (`64`, `D3 07:42`) são exemplo de layout, nunca dado. `com`,
`ene`, `hig`, `hum` e `saú` são os ícones de comida, energia, higiene, humor e saúde (lucide `Drumstick`, `Zap`, `Droplet`, `Smile`,
`HeartPulse`, os de hoje).

**A tela de hoje** (`TelaPet.tsx`, HUD-1 a HUD-5, o HUD transitório de 2026-11-04), para comparar:

```
1920×950
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│ [◉ Agumon  ROOKIE]          ┌ chamado / resumo (15 s) ┐             [D3 07:42]  [● salvo]    │
│ ┌────┐                      └─────────────────────────┘           ┌ Estado atual ───────┐    │
│ │Pet │                                                            │ com ▮▮▮▮▮▮▯▯▯ 64 %  │    │
│ │Cre │                                                            │ ene ▮▮▮▮▮▮▮▮▯ 81 %  │    │
│ │Lut │                                                            │ hig ▮▮▮▮▯▯▯▯▯ 40 %  │    │
│ │Diá │                ╭ balão (15 s) ─────────╮                   │ hum …   saú …       │    │
│ ├────┤                │ fome. você demorou.   │                   │ Detalhes ›          │    │
│ │Con │                │ toque para ver o porquê                   ├ Evolução · 2 h ─────┤    │
│ │Aju │                ╰──────────╮────────────╯                   ├ Últimas ações ──────┤    │
│ └────┘                           ▼                                └─────────────────────┘    │
│                                (pet)                                                         │
│                         ilha 3D (tela inteira)                                [◇ DigiBrain]  │
│            [Alimentar][Brincar][Limpar][Carinho][Tapa][Tratar][Mais]                         │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
```

O porquê de uma fala está a dois toques (o balão, que some em 15 s, e depois o painel "Por que ele disse isso"); as necessidades ficam na
pilha da direita, que cobre ~300 px da cena (o custo aceito na HUD-2).

---

## Proposta A — A ilha na frente

### O objetivo do jogador

Estar com o pet: olhar a vida dele na ilha e intervir quando ele precisa. A tela é a janela para a ilha; a informação fica na borda e só
cresce quando o jogador pede.

### A hierarquia

1. o pet e a ilha (a tela inteira, nada cobrindo o centro nem a direita);
2. a **faixa dos vitais** no alto ao centro: as cinco medidas numa linha, ícone e número;
3. o dock de ações no rodapé;
4. a plaquinha e o trilho, como hoje;
5. a pilha (Estado em detalhe, Evolução, Últimas ações) e o DigiBrain, só por gesto.

**"Recuar" quer dizer ocupar menos área, nunca perder contraste:** nada fica translúcido a ponto de ler abaixo de 4,5:1 (guia 4.1), e
nada some por inatividade (guia, princípio 5 e seção 11).

### Sempre visível

- A faixa dos vitais: `com 64 · ene 81 · hig 40 · hum 72 · saú 95`, com o ícone de cada uma e o % do motor (`Math.round(valor × 100)`,
  HUD-3). Abaixo de 50 %, a medida ganha a caixa sólida de necessidade (`--hx-necessidade`, a marca "vem do corpo" do guia 3) **e** um
  traço embaixo, para funcionar sem cor; a saúde abaixo de 30 % usa `--hx-perigo`, como hoje.
- A plaquinha, o relógio, o trilho e o dock, como hoje.
- O chamado urgente, a morte e a fome crítica (as regras do HUD transitório não mudam).

### Por gesto

- **A pilha** abre por um botão `≡ Painéis` no fim da faixa dos vitais (alvo de 44 px), por tocar numa medida (abre o Estado já rolado
  nela) ou pela tecla `E`; fecha pelo `×`, pelo `Esc` ou pelo mesmo botão. A escolha fica no `-hud` (a chave de hoje), com o padrão
  mudando de "Estado aberto" para "tudo fechado".
- **No celular**, os quatro botões da borda direita (Estado, Evolução, Últimas ações, DigiBrain) saem da cena e entram no `≡` da faixa,
  que abre o painel compacto de hoje com os quatro como abas.
- O balão e o resumo, como hoje (15 s, arrastáveis).

### As cores

A faixa e os botões: `--hud-fundo-1`/`--hud-fundo-2`, `--hud-risca` e o ciano da HUD-5, texto em `--hx-texto`;
necessidade `--hx-necessidade`; perigo `--hx-perigo`; o ok da saúde `--hx-ok`. O vidro (`--hud-desfoque`) só na faixa, que é estreita.

### Wireframes

```
1920×950
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│ [◉ Agumon  ROOKIE]   ┌──────────────────────────────────────────────────┐ [D3 07:42][● salvo]│
│ ┌────┐               │ com 64 · ene 81 · hig 40 · hum 72 · saú 95  [≡]  │                    │
│ │Pet │               └──────────────────────────────▔▔▔▔▔───────────────┘                    │
│ │Cre │                     ┌ chamado / resumo (15 s) ┐                                        │
│ │Lut │                     └─────────────────────────┘                                        │
│ │Diá │                                                                                        │
│ ├────┤                         ╭ balão (15 s) ────────╮                                       │
│ │Con │                         ╰──────────╮───────────╯                                       │
│ │Aju │                                    ▼                                                   │
│ └────┘                                  (pet)                                                 │
│                                                                                               │
│                ilha 3D: a tela inteira, nada cobrindo a direita                [◇ DigiBrain]  │
│            [Alimentar][Brincar][Limpar][Carinho][Tapa][Tratar][Mais]                          │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
  [≡], tocar numa medida ou a tecla E: a pilha de hoje abre à direita (e fecha pelo ×)
```

```
390×844
┌───────────────────────────────────────┐
│[◉ Agumon ROOKIE]  D3 07:42 [Con][Aju] │
│┌─────────────────────────────────────┐│
││com 64 ene 81 hig 40 hum 72 saú 95 ≡ ││
│└───────────────────▔▔▔▔──────────────┘│
│   ┌ chamado / resumo (15 s) ┐         │
│   └─────────────────────────┘         │
│                                       │
│        ╭ balão (15 s) ───╮            │
│        ╰──────╮──────────╯            │
│               ▼                       │
│             (pet)                     │
│        ilha 3D, sem botões            │
│        na borda direita               │
│                                       │
│[Alimentar][Brincar][Limpar][Carinho]… │
│[ Pet ][ Crescer ][ Lutar ][ Diário ]  │
└───────────────────────────────────────┘
  ≡: o painel compacto com Estado, Evolução, Últimas ações e DigiBrain em abas
```

### O que muda na leitura do estado do pet

- **Ganha:** a cena fica inteira (os ~300 px da direita voltam ao pet, a 1280 e a 1920); as cinco medidas ficam visíveis o tempo todo,
  também no celular, onde hoje estão atrás de um botão.
- **Perde:** a barra de cada medida (fica o número e a marca de alerta); o resumo de Evolução e de Últimas ações que a pilha fechada
  mostra hoje; os Detalhes (emoção, mundo, desejo, confiança) ficam a dois toques em vez de um.
- **Desfaz a HUD-2** (pilha aberta por padrão), decidida em 2026-10-30.

### O custo em determinismo

Nenhum no motor nem no replay: tudo continua derivado de `m.e` na hora de desenhar. A preferência fica no `-hud` (fora do save); quem já
tem a chave gravada mantém a escolha (o `lerHud` de hoje). A câmera e a cena (`cena3d.ts`, `ilha/`) não mudam; só deixam de ser cobertas.

### O custo em e2e

- O teste "Pet (Home) … 1280 px" (a pilha à direita, Estado aberto, a escolha guardada) muda de expectativa; o "monitor" (nada cobre o
  centro a 1920) continua e fica mais forte.
- Todas as capturas da tela Pet trocam de referência: `pet-estado`, `pet-v11` e `pet-v12` a 1920 e a 390, nas duas peles, mais as do
  `vida_pet_cena` e do `sprites_comer` que mostram o HUD.
- **Risco novo:** mais pixels da ilha WebGL na captura a 1920. A Exploração já precisou ir para o projeto `software` (SwiftShader) porque a
  GPU variou alguns pixels no mesmo quadro; com a pilha fora, a tela Pet fica mais exposta a isso e pode ter de ir junto (as referências
  delas mudam outra vez).
- O seletor dos botões da borda no celular (`.pet-lado__bt`) some; os e2e que abrem um painel no celular passam pelo `≡`.

---

## Proposta B — O porquê no balão

### O objetivo do jogador

Entender o que o pet decidiu e por quê, e reconhecer de relance "isso fui eu que ensinei" (guia, princípio 2: o aprendizado visível é o
diferencial do jogo).

### A hierarquia

1. o pet e o balão, que passa a levar **o chip de causa** (guia 7.7) colado embaixo da fala;
2. a **linha do agora**, sob a plaquinha: o que o pet está fazendo e os ícones da causa registrada, sempre visível;
3. a pilha da direita, como hoje (HUD-2);
4. o dock, como hoje;
5. o painel "Por que ele disse isso", que deixa de ser o caminho principal e vira o detalhe (a fonte da fala, a LLM, o verificador).

### Sempre visível

- **A linha do agora:** `agora: brincando · [nota] + [joinha]`, com os ícones de `CausaIcones` (os de hoje, que estão dentro do painel);
  sem causa registrada, `agora: brincando · ? sem causa registrada` em tracejado cinza. Uma linha, ~32 px de altura.
- A plaquinha, o relógio, o trilho, a pilha e o dock, como hoje.

### Por gesto

- **O balão** continua aparecendo quando o pet reage e some em 15 s (`AVISO_MS`); agora ele traz o chip embaixo da fala:
  - com registro: a malha ciano de aprendido, o emote da categoria e a origem (`elogio · evento #41`), o que `Causa` e `refsDoMotivo` já
    calculam;
  - sem registro: o tracejado cinza com `? sem motivo registrado`.
- **Tocar no balão ou na linha do agora** abre o painel "Por que ele disse isso" de hoje, para quem quer a fonte da fala.
- A recusa (guia 10) já é "balão + chip": vira o caso comum, não um caso especial.

### O estágio (guia 9)

A fala do pet segue o estágio como hoje (emote no In-Training, ícones da causa no Rookie, frase a partir do Champion). **O chip é a
interface explicando com dado registrado**, que o guia permite em qualquer estágio ("quem explica no lugar do pet é a interface, e só com
dado registrado"); por isso o chip vai também no In-Training, ao lado do emote. A fala nunca fica mais rica que o estágio.

### As cores

O chip com registro na malha de aprendido: `--hx-aprendido` sobre `--dl-learned-bg` (a marca "aprendido com o dono", guia 3), borda
tracejada; sem registro, tracejado em `--hx-texto-2` com o `?`. A linha do agora na caixa do HUD (`--hud-fundo-1`, `--hud-risca`). A
fala fria ou sombria troca o ciano pelo lilás, como hoje. Nada em amarelo: o destaque da tela continua sendo um só.

### Wireframes

```
1920×950
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│ [◉ Agumon  ROOKIE]          ┌ chamado / resumo (15 s) ┐             [D3 07:42]  [● salvo]    │
│ ┌ agora: brincando · ♪ + ▲ ›┐                                      ┌ Estado atual ───────┐    │
│ └───────────────────────────┘                                      │ com ▮▮▮▮▮▮▯▯▯ 64 %  │    │
│ ┌────┐                                                             │ ene …   hig …       │    │
│ │Pet │                                                             │ hum …   saú …       │    │
│ │Cre │             ╭ balão (15 s) ──────────────────╮              │ Detalhes ›          │    │
│ │Lut │             │ brincar. você me elogiou.      │              ├ Evolução · 2 h ─────┤    │
│ │Diá │             ├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤              ├ Últimas ações ──────┤    │
│ ├────┤             ┊▦ ▲ elogio · evento #41         ┊ ← chip       └─────────────────────┘    │
│ │Con │             ╰──────────╮─────────────────────╯                                         │
│ │Aju │                        ▼                                                               │
│ └────┘                      (pet)                                                             │
│                       ilha 3D (tela inteira)                                  [◇ DigiBrain]   │
│            [Alimentar][Brincar][Limpar][Carinho][Tapa][Tratar][Mais]                          │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
  ♪ ▲ = ícones da causa (nota, joinha); ▦ = malha de aprendido; › ou o balão abrem o painel do porquê
```

```
390×844
┌───────────────────────────────────────┐
│[◉ Agumon ROOKIE]  D3 07:42 [Con][Aju] │
│┌ agora: brincando · ♪ + ▲ ›──────────┐│
│└─────────────────────────────────────┘│
│   ┌ chamado / resumo (15 s) ┐   [Est] │
│   └─────────────────────────┘   [Evo] │
│                                 [Últ] │
│   ╭ balão (15 s) ──────────╮    [DB]  │
│   │ brincar. elogio.       │          │
│   ├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤          │
│   ┊▦ ▲ elogio · evento #41 ┊          │
│   ╰──────╮─────────────────╯          │
│          ▼                            │
│        (pet)                          │
│[Alimentar][Brincar][Limpar][Carinho]… │
│[ Pet ][ Crescer ][ Lutar ][ Diário ]  │
└───────────────────────────────────────┘
  sem causa registrada: ┊ ? sem motivo registrado ┊ em cinza tracejado, no balão e na linha
```

### O que muda na leitura do estado do pet

- **Ganha:** o motivo sai de dois toques para nenhum: a linha do agora o mostra sempre, e o balão o mostra junto da fala. O jogador vê a
  marca de "aprendido com você" no momento em que ela importa.
- **Expõe uma coisa que hoje fica escondida:** quantas vezes o pet age **sem** causa registrada (a exploração, `mot.exploracao`). O `?`
  vai aparecer tanto quanto o motor o produz. É honesto (guia, princípio 1), mas pode ler como "o pet não aprendeu nada" nos primeiros
  dias; vale olhar na prancha com um save real antes de decidir.
- **Limite do motor:** só a decisão de agora tem motivo (`Motor.motivo`); o `historico` não guarda causa. Uma fita com os porquês das
  últimas decisões precisaria de mudança no motor e fica fora (tarefa, seção 6).
- A pilha e o dock não mudam.

### O custo em determinismo

Nenhum: `Causa`, `CausaIcones`, `refsDoMotivo` e `detalheMotivo` já são funções do motor e do registro, e o chip nunca vem do texto da
LLM (guia 7.7: "nunca gerar a causa por texto livre"). A linha do agora muda a cada revisão do motor, sem relógio próprio. A fala livre
continua gravada no log, como hoje; o chip mostra a causa do motor, não a da fala livre.

### O custo em e2e

- Mudam as capturas da tela Pet que têm motivo (o save `SAVE_V11` tem carinho, tapa e alimentar; o `champion` também), a 1920 e a 390,
  nas duas peles. As de pet sem motivo (o ovo) quase não mudam.
- **Fecha uma pendência:** o e2e do caminho até o porquê (`PAINEL_V3.md` 2.1, quebrado desde o #566 porque o save do teste não tem fala)
  ganha um caminho que não depende do balão: a linha do agora é sempre visível e abre o mesmo painel. O caminho pelo balão continua
  precisando de um save com fala registrada.
- A 390, a linha do agora disputa o alto com o cartão do chamado (o mesmo custo da HUD-4); na prancha ela vai na fileira da plaquinha.
- Novo teste de componente: com causa, o chip tem a malha e o `evento #`; sem causa, o `?` e o texto; os dois com nome acessível.

---

## Proposta C — Os botões sabem o que falta

### O objetivo do jogador

Cuidar bem e rápido: ver o que falta e agir no mesmo lugar, como no pet de bolso. A medida mora no botão que a atende.

### A hierarquia

1. o pet e a ilha;
2. o **dock com as medidas**: cada botão de ação traz a barra da medida que essa ação mexe no motor;
3. a energia e a saúde ao lado do relógio (a energia não tem botão: o pet dorme sozinho);
4. a pilha da direita, sem o bloco das cinco necessidades (que foi para o dock): Evolução, Últimas ações e Detalhes;
5. o balão e o chamado, como hoje.

### Sempre visível

- **No dock**, na ordem de hoje (`ORDEM_DOCK`): Alimentar com a comida, Brincar com o humor, Limpar com a higiene, Tratar com a saúde
  (no desktop). Carinho e Tapa **sem barra**: são gestos no corpo, e o efeito deles não é uma medida só. Cada barra é segmentada (guia
  7.5, 10 blocos com o `aria-label` "N de 10") e tem o %.
- **A ação sugerida** (`acao-destaque--sugerida`, que já existe) continua sendo o único destaque; a barra abaixo de 50 % usa a cor e a
  forma de necessidade, sem segundo destaque.
- **Ao lado do relógio:** a energia (ícone de raio, barra curta e %) e, no celular, a saúde, porque o Tratar fica atrás do Mais.
- O nome acessível de cada botão continua sendo o nome da ação (o `ROTULO_DONO`); a medida entra por `aria-describedby`, para os
  seletores de hoje não quebrarem.

### Por gesto

- O Mais, como hoje (Tratar no celular, Pôr ração, a bola).
- A pilha: Evolução e Últimas ações como hoje; o antigo Estado vira "Detalhes" (emoção, mundo, desejo, confiança), fechado por padrão.

### A ligação entre a ação e a medida

**Hoje ela é uma tabela da tela** (`ACAO_NEC` em `TelaPet.tsx`), não um fato do motor. A proposta só fica honesta se a ligação sair do
efeito de cada ação no motor: a prancha lista, para cada ação, a medida que o motor muda e onde isso está no código do motor, e um teste
Vitest confere a tabela da tela contra o motor (aplicar a ação num motor de teste e ver qual medida sobe). Onde o efeito não é imediato,
o botão diz: no pet v12 com mundo, o Alimentar é a reserva que põe a ração no comedouro, e a comida só sobe quando o pet come; a barra
fica, com o "reserva" que o botão já mostra.

### As cores

O dock na pele dos menus (`--hx-btn-bg`, `--hx-btn-borda`, `--hx-btn-ink`; o escolhido em `--hx-escolhido`); a barra no trilho
`--hx-medidor-trilho` com o enchimento `--hx-medidor`, e abaixo de 50 % `--hx-necessidade`; a saúde baixa em `--hx-perigo`.

### Wireframes

```
1920×950
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│ [◉ Agumon  ROOKIE]          ┌ chamado / resumo (15 s) ┐   [D3 07:42 · ene ▮▮▮▮▯ 81 %][● salvo]│
│ ┌────┐                      └─────────────────────────┘           ┌ Evolução · 2 h ─────┐    │
│ │Pet │                                                            ├ Últimas ações ──────┤    │
│ │Cre │                                                            ├ Detalhes ───────────┤    │
│ │Lut │                ╭ balão (15 s) ─────────╮                   └─────────────────────┘    │
│ │Diá │                ╰──────────╮────────────╯                                              │
│ ├────┤                           ▼                                                           │
│ │Con │                         (pet)                                                         │
│ │Aju │                                                                                       │
│ └────┘                  ilha 3D (tela inteira)                                [◇ DigiBrain]  │
│   ┌───────────┐┌───────────┐┌───────────┐┌─────────┐┌────────┐┌───────────┐┌────────┐        │
│   │ Alimentar ││  Brincar  ││  Limpar   ││ Carinho ││  Tapa  ││  Tratar   ││  Mais  │        │
│   │ ▮▮▮▮▮▮▯▯▯▯││ ▮▮▮▮▮▮▮▯▯▯││ ▮▮▮▮▯▯▯▯▯▯││         ││        ││ ▮▮▮▮▮▮▮▮▮▯││        │        │
│   │ comida 64%││ humor 72% ││ higien 40%││         ││        ││ saúde 95% ││        │        │
│   └───────────┘└───────────┘└───────────┘└─────────┘└────────┘└───────────┘└────────┘        │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
```

```
390×844
┌───────────────────────────────────────┐
│[◉ Agumon ROOKIE]  D3 07:42 [Con][Aju] │
│ ene ▮▮▮▮▯ 81 %   saú ▮▮▮▮▮ 95 %       │
│   ┌ chamado / resumo (15 s) ┐   [Evo] │
│   └─────────────────────────┘   [Últ] │
│                                 [Det] │
│        ╭ balão (15 s) ──╮       [DB]  │
│        ╰──────╮─────────╯             │
│               ▼                       │
│             (pet)                     │
│                                       │
│┌───────┐┌───────┐┌───────┐┌───────┐┌─┐│
││Aliment││Brincar││Limpar ││Carinho││…││
││▮▮▮▮▮▯▯││▮▮▮▮▮▮▯││▮▮▮▯▯▯▯││       ││ ││
││ 64 %  ││ 72 %  ││ 40 %  ││       ││ ││
│└───────┘└───────┘└───────┘└───────┘└─┘│
│[ Pet ][ Crescer ][ Lutar ][ Diário ]  │
└───────────────────────────────────────┘
```

### O que muda na leitura do estado do pet

- **Ganha:** a leitura vira ação: o jogador vê "higiene 40 %" no próprio Limpar. As medidas ficam visíveis no celular sem abrir nada, e a
  pilha da direita encolhe (sai o bloco mais alto dela).
- **Perde:** a lista das cinco medidas juntas, que deixa comparar uma com a outra; a energia e a saúde (no celular) vão para longe das
  outras três; o humor fica preso ao Brincar, e se o carinho também mexer nele no motor (não conferido nesta sessão), a barra não diz isso.
- **Risco de leitura errada:** um botão com barra baixa parece "aperte-me". No v12 o Alimentar não enche a barra na hora; nos pets que
  recusam, apertar não garante o efeito. A prancha precisa mostrar esses dois casos.

### O custo em determinismo

Nenhum no motor: as barras são `m.e` na hora de desenhar. O teste novo que liga a ação à medida **lê** o motor (aplica a ação num motor de
teste), não muda nada nele.

### O custo em e2e

- **O dock fica mais alto** (de 52 px para ~72 px). O `useReservaDoHabitat` reserva o espaço do dock no pé do habitat (`--hab-baixo`):
  a cena encolhe, o pet sobe na tela e **todas** as capturas que mostram o habitat mudam, inclusive as do `vida_pet_cena` e do
  `sprites_comer`, e a posição do pet nas que medem a cena.
- Todo e2e de ação passa pelo dock. Os nomes acessíveis ficam iguais (a medida vai no `aria-describedby`), mas o histórico do #554 (o
  seletor da ração que achava também o botão da bola) mostra que mexer no dock quebra seletor; o custo é rever os seletores de `jogo.spec.ts`.
- O teste "Pet (Home) … 1280 px" muda (o Estado sai da pilha) e o `hx_pele.test.ts` ganha o contraste das barras dentro dos botões.

---

## Comparação

| | A — a ilha na frente | B — o porquê no balão | C — os botões sabem o que falta |
|---|---|---|---|
| a pergunta que a tela responde primeiro | o que ele está fazendo agora? | por que ele fez isso? | o que eu faço agora? |
| o que sai do caminho | a pilha da direita (por gesto) | nada; o painel do porquê vira detalhe | o bloco das necessidades da pilha |
| decisão anterior que desfaz | HUD-2 | nenhuma | HUD-2 em parte, e o dock da seção 8 do guia ganha barras |
| dado novo do motor | nenhum | nenhum | nenhum (a ligação ação → medida conferida contra o motor) |
| capturas que mudam | todas da tela Pet; risco de ir ao SwiftShader | só as com motivo | todas que mostram o habitat (o dock mais alto move a cena) |
| e2e de interação que muda | abrir painéis (pilha e celular) | nenhum quebra; um novo para o chip; fecha a pendência do porquê | os do dock e o da pilha |
| risco | o jogador não acha a pilha | o `?` frequente nos primeiros dias | a barra induz "aperte-me" onde o efeito não é imediato |

**Recomendação (UX-1):** a **B** primeiro, porque é a que serve ao diferencial do jogo com o menor custo e nenhuma decisão anterior
desfeita; depois, se o Matheus quiser a cena mais limpa, a **faixa dos vitais da A** como segunda etapa, que combina com a B (a linha do
agora e a faixa cabem na mesma fileira do alto). A C fica para quando o dock for revisto por outro motivo: é a que mais mexe no que o
e2e de ação usa.
