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

---

## P1 — o plano da prancha da B (2026-11-06, `ux-designer`)

Status: **DECIDIDO** (Matheus, 2026-11-06, "Siga com a sua recomendação."; a prancha e as P1-1 a P1-6, tarefa seção 8.1). A prancha está em `docs/pranchas/ux-pet/`
(`gerar.py`, `pet.css`, `capturar.sh`); as capturas vão para `D:\Trab\digilab\capturas_ux_pet_aprovar\`, fora do git (UX-8). A skill
`frontend-design` não foi achada nesta sessão; o método é o da seção 0, com o guia acima de tudo.

### P1.0 O que a leitura do motor mudou na B

A B foi escrita lendo a tela (`Causa`, `CausaIcones`, `refsDoMotivo`). Lendo o motor, **o chip "elogio · evento #41" não existe para os
pets que o jogo abre hoje**:

- os pets que abrem são os v13, v14, v15 e v17 (`VERSOES_PET`, `web/app/motor/constantes.ts:70`), todos decididos pelo cérebro A (ou
  pelo modular, no v17 com o evento `cb`);
- o `Motor.motivo` (`MotivoVida`, `motor/tipos.ts:104-107`) **só é gravado pelo treino** (`motor/motor.ts:869-881`: `forcar_treino` e
  `treinar_cansado`, com o fator `fadiga_treino` e `refsOrd: []`). A decisão de vida do A não passa por ele (`motor.ts:830-845`, o
  `_decisaoV11`; o registro de 2026-10, linha 4631: "Não há motivo do Bandit no v11"; a auditoria `docs/AUDITORIA_V2_PRODUTO_MODULAR.md:56-58`);
- sem elogio nem bronca nos v11+ (`motor/lobos.ts:61-63`, `FEEDBACK` fora), as categorias de memória do chip (`CAUSA_MEMORIA`,
  `TelaPet.tsx:58`) nunca chegam; `refsOrd` sai vazio, então o "evento #N" nunca aparece;
- **o porquê registrado da decisão de agora é o do cérebro A**: `Motor.digibrain().decisao` (`motor.ts:319-336`), a `leituraDecisao`
  (`motor/digibrain.ts:35-84`) sobre o `CerebroA.ultimoMotivo` (`motor/lobos.ts:476`, gravado em `registrar`, `lobos.ts:601-624`). Ela
  diz a regra do instinto que disparou (`regra`), se havia escolha (`quem_decidiu.escolha`) e **se o aprendido mudou a escolha**
  (`quem_decidiu.mudou`: o sorteio só com os impulsos e o mesmo `u` daria outra ação, `digibrain.ts:58-65`). É o dado que o painel
  DigiBrain já mostra na seção "Agora" (`src/componentes/DigiBrain.tsx:77-84`).

**A B refinada:** a linha do agora lê o porquê do cérebro A (sempre visível) e é ela que carrega a marca de aprendido; o balão continua
com as fontes de hoje (o motivo do treino e a fala livre) e ganha o chip só quando há `MotivoVida`. O "evento #N", o emote da categoria e
os ícones de `CausaIcones` saem da prancha (perguntas P1-3 e P1-4).

**Três defeitos de hoje achados na leitura** (sem execução; nenhum é corrigido nesta etapa, vão para o implementador):

1. `Causa` (`TelaPet.tsx:80-87`) devolve um fragmento **vazio** quando há fator mas nenhum é de memória: o `fadiga_treino` do treino
   não mostra nem o chip nem o "?";
2. `CausaIcones` (`TelaPet.tsx:118-129`) com `fadiga_treino` desenha o "?" (sem ícone no `ICONE_CAUSA`), mas o `aria-label` diz
   "causa: treino puxado": a forma diz "sem registro" e o nome acessível diz o contrário;
3. o `Motor.motivo` nunca é limpo: depois de um treino com pausa, o "Por que ele disse isso" (`DetalheFala`, `TelaPet.tsx:144-155`)
   mostra a ação de agora (`pet-status`) ao lado da causa do treino antigo.

E um risco: com o modular ativo (`Motor.lab`, `motor.ts:218`), `Motor.digibrain()` continua lendo o `ultimoMotivo` do A, que parou de
decidir (`motor.ts:323-328` não olha o `modularAtivo`). O painel já desvia para o `ConteudoDigiBrainLab` (`TelaPet.tsx:485-489`); a linha
do agora tem de fazer o mesmo.

### O objetivo do jogador

Saber, de relance e sem abrir nada, o que o pet está fazendo e se foi o que ele aprendeu que decidiu, e não só o instinto (guia,
princípio 2). Sem registro, ver o vazio honesto (princípio 1).

### A hierarquia

1. o pet e a ilha, como hoje;
2. **a linha do agora**, na fileira do topo, logo depois da plaquinha (1920) ou logo abaixo do topo (390): a ação de agora e o porquê do
   cérebro A;
3. o balão (15 s, `AVISO_MS`), como hoje, com o chip de causa embaixo da fala quando ela vem de um `MotivoVida`;
4. a pilha da direita e o dock, sem mudança;
5. o detalhe: tocar na linha abre o painel DigiBrain (o "Agora", o mapa dos pesos, os lobos); tocar no balão abre o "Por que ele disse
   isso", como hoje.

### Sempre visível: a linha do agora

Um `<button>` numa caixa da HUD (`hud-caixa`), uma linha, 48 px de altura a 1920 (a do relógio, `casca.css:63`) e 44 px a 390. Some com o
ovo chocando e com o pet morto (como o `EstadoConfianca`, `TelaPet.tsx:172`). Os estados, pela ordem em que a tela testa:

| caso no motor | a linha (1920) | a 390 | marca (guia 3) |
|---|---|---|---|
| `Motor.lab !== null` (o modular decide) | `AGORA brincando · cérebro modular ›` | igual | nenhuma (texto `--hx-texto-2`); pergunta P1-2 |
| `digibrain() === null` ou `decisao === null` (antes da primeira decisão) | `AGORA à toa · ? sem motivo registrado ›` | igual | cinza tracejado + "?" |
| `quem_decidiu.mudou` | `AGORA brincando · [▦ aprendido · sem ele: à toa] ›` | `AGORA brincando · [▦ aprendido] ›` | malha ciano tracejada |
| `escolha && !mudou` | `AGORA explorando · Tempo livre · o instinto faria o mesmo ›` | `AGORA explorando · instinto ›` | nenhuma: neutro é silêncio (princípio 3) |
| `!escolha` | `AGORA dormindo · Exausto · só havia uma opção ›` | `AGORA dormindo · uma opção ›` | nenhuma |

Os textos da regra e da ação são os do painel DigiBrain (`REGRA_TXT`, `ACAO_CURTA`, `DigiBrain.tsx:15-26`), e as frases "o instinto
faria o mesmo" e "só havia uma opção" são as dele (`DigiBrain.tsx:80-82`): a linha não inventa texto novo. O nome acessível junta tudo:
"Agora: brincando. Aprendido: sem ele, à toa. Abrir o porquê no DigiBrain."

### Por gesto

- **A linha do agora** (clique, toque, `Enter` ou `Espaço`) abre o painel DigiBrain, o mesmo da etiqueta `◇ DigiBrain`, com
  `aria-controls="pet-painel"` e `aria-pressed`; o foco volta à linha ao fechar (o `fechar` de hoje, `TelaPet.tsx:528`). Com "Exibir
  detalhes do pet" desligado (que tira o DigiBrain, `TelaPet.tsx:522`), a linha fica, mas vira texto sem botão (pergunta P1-5).
- **O balão** aparece quando aparece hoje (o motivo do treino que muda, a fala livre) e some em 15 s. Com `MotivoVida`, o chip vai embaixo
  da fala, dentro do mesmo botão (o toque continua abrindo o "Por que ele disse isso"):
  - fator de memória (`CAUSA_MEMORIA`): malha ciano, como a `Causa` de hoje (nos pets de hoje, não acontece);
  - `fadiga_treino`: `vem do corpo · treino puxado` (o marcador do `FATORES_TXT`, `expressao.ts:78`), na caixa sólida de necessidade
    (pergunta P1-1);
  - outro fator: o marcador do `FATORES_TXT` em texto neutro, nunca o fragmento vazio de hoje;
  - exploração ou nenhum fator: `? sem motivo registrado`, cinza tracejado.
  A fala livre não ganha chip: o texto é da LLM e o porquê dela são os fatos citados, no painel (guia 7.7: nunca a causa por texto livre).

### O estágio (guia 9)

A fala do balão segue o estágio como hoje (`TextoFala`, `TelaPet.tsx:64-79`; `expressar`, `expressao.ts:214-230`). A linha do agora e o
chip são a interface explicando com dado registrado, o que o guia permite em qualquer estágio: vão também no In-Training. A linha não usa
frase do pet (nada em primeira pessoa), só os rótulos do painel.

### As cores pelos tokens

| peça | token (arquivo) |
|---|---|
| caixa da linha do agora | `--hud-fundo-1`, `--hud-fundo-2`, `--hx-borda`, `--hud-ch-p`, `--hud-brilho`, `--hud-desfoque` (`tokens.css:129-133`, `:168-170`); no Militar a linha de topo `--hx-borda-topo` (`pele-xcom.css:15-21`) |
| rótulo `AGORA` | `--hx-rotulo`, `--hx-f`, 12 px, caixa alta (como `.hud-painel__tit`, `pet_hud.css:37`) |
| a ação | `--hx-texto`, `--hx-f`, 600 16 px |
| regra e frases neutras | `--hx-texto-2` |
| chip aprendido | malha `--dl-learned-bg` com a grade `rgba(111,227,255,.38)` do `.dl-malha` (`pet.css:3`), borda tracejada `--hx-aprendido` (`--dl-learned`), texto `--dl-learned-ink` (`tokens.css:28`) |
| chip sem registro | borda tracejada `--hx-sec`, texto `--hx-texto-2`, fundo transparente, o "?" em 900 |
| chip vem do corpo (treino) | fundo `--hx-necessidade` (`tokens.css:117`), texto `--dl-need-ink` (`tokens.css:16`), borda sólida |
| foco | `outline: 2px solid var(--hx-foco)`, `outline-offset: -4px` (o da HUD, `pet_hud.css:34`) |
| a seta `›` | `--hx-sec` |

Nenhuma cor nova. Nada em amarelo (o destaque continua sendo um só por tela). As fontes são as da pele (`--hx-f`, `--hx-f-num`:
Saira Condensed no Militar, Barlow e Rajdhani no Vidro; `tokens.css:119-120`, `:157-158`), como toda a HUD desde a `TAREFA_V3_LAYOUT_HUD`.

### Wireframes

```
1920×950
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│[◉ Gabumon ][AGORA brincando · ▦aprendido · sem ele: à toa ›]   DIGILAB      [Dia 3 07:42 ● salvo]│
│ ┌────┐ Rookie                                                        ┌ Estado atual ─────────┐│
│ │Pet │                                                               │ com ▮▮▮▮▮▮▯▯▯▯ 64 %   ││
│ │Cre │                                                               │ ene ▮▮▮▮▮▮▮▮▯▯ 81 %   ││
│ │Lut │                                    ╭ balão (15 s) ─────────╮  │ hig ▮▮▮▮▯▯▯▯▯▯ 40 %   ││
│ │Diá │                                    │ [sem pausa] treino    │  │ hum …   saú …         ││
│ │Con │                                    │ ■ vem do corpo · treino│ │ Detalhes ›            ││
│ │Aju │                                    │ toque para ver o porquê│ ├ Evolução ─────────────┤│
│ └────┘                                    ╰───────────────────────╯  ├ Últimas ações ────────┤│
│                                  (pet)                               └───────────────────────┘│
│ ┌ quadro da prancha: os estados ┐                                                             │
│ │ ▦ aprendido · ? sem motivo …  │     fundo neutro no lugar da ilha 3D          [◇ DigiBrain]  │
│ └───────────────────────────────┘ [Alimentar][Brincar][Limpar][Carinho][Tapa][Tratar][Mais]    │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
  a linha do agora fica na fileira do topo: não desce sobre o trilho (que começa em 86 px, casca.css:96) nem
  sobre o cartão do chamado (no alto ao centro, a partir de 78 px, pet_hud.css:66); o quadro é só da prancha
```

```
390×844
┌───────────────────────────────────────┐
│[◉ Gabumon]        [07:42] [Con][Aju]  │
│┌ AGORA à toa · ? sem motivo reg. › ┐ [Est]│
│└───────────────────────────────────┘ [Evo]│
│ ┌ chamado / resumo (15 s), 50 px abaixo┐[Últ]│
│ └──────────────────────────────────────┘[DB]│
│        ╭ balão (15 s) ─────────╮      │
│        │ [sem pausa] treino    │      │
│        │ ■ vem do corpo · treino│     │
│        ╰───────────────────────╯      │
│               (pet)                   │
│[Alimentar][Brincar][Limpar][Carinho][…]│
│[  Pet  ][ Crescer ][ Lutar ][ Diário ]│
└───────────────────────────────────────┘
  a linha entra a 70 px (o topo tem 64), de 10 px até 64 px da direita (a coluna da borda); o cartão do chamado
  desce para 120 px. Sem o "sem ele: …" a 390 (fica no DigiBrain)
```

### A tabela de proveniência

| dado na tela | de onde vem (campo) | arquivo:linha |
|---|---|---|
| a ação atual ("brincando") | `Motor.acao`, gravada em `_decisaoV11`; o texto em `NOME_PET` | `motor/motor.ts:139`, `:833`; `motor/nomes.ts:18` |
| o porquê da linha (regra, escolha, aprendido mudou) | `Motor.digibrain().decisao` = `leituraDecisao(ultimoMotivo, …)`: `regra`, `quem_decidiu.{escolha, acao_instinto, mudou}` | `motor/motor.ts:319-336`; `motor/digibrain.ts:14-24`, `:58-65`; `motor/lobos.ts:476`, `:601-624` |
| "sem ele: à toa" | `quem_decidiu.acao_instinto` com o texto `ACAO_CURTA` | `motor/digibrain.ts:21`, `:63-64`; `src/componentes/DigiBrain.tsx:24-26` |
| "Tempo livre", "Exausto"… | `decisao.regra` com o texto `REGRA_TXT` | `motor/digibrain.ts:15`; `src/componentes/DigiBrain.tsx:15-18` |
| "o instinto faria o mesmo", "só havia uma opção" | os mesmos ramos do painel | `src/componentes/DigiBrain.tsx:80-82` |
| "cérebro modular" | `Motor.lab !== null` | `motor/motor.ts:218`, `:1035` |
| "? sem motivo registrado" (linha) | `digibrain() === null` (sem cérebro A) ou `decisao === null` (antes da primeira) | `motor/motor.ts:324`, `:328`; o texto de `TelaPet.tsx:81` |
| a fala do balão | `Motor.motivo` (só o treino o grava) → `falaDe` → `expressar`; ou a fala livre (`useFalaLivre`) | `motor/motor.ts:163`, `:869-881`; `src/fala.ts:87-91`; `motor/expressao.ts:214-230`; `src/falaLivre.ts:149-159` |
| "[sem pausa]" e "treino puxado" (Rookie) | `ACOES_VIDA_TXT.treinar_cansado` e `FATORES_TXT.fadiga_treino.marcador` | `motor/expressao.ts:87`, `:78` |
| o chip do balão | `MotivoVida.fatores` e `exploracao` | `motor/tipos.ts:105-106`; `TelaPet.tsx:80-87` |
| "vem do corpo" | o texto do card de desejo de necessidade; o motor classifica o pedido de pausa como `tipo: "necessidade"`, `causa: "fadiga_treino"` | `TelaPet.tsx:259`; `motor/motor.ts:887` |
| o emote no In-Training | `EMOTE_HUMOR` pelo `MotivoVida.humor` | `motor/expressao.ts:104`, `:219` |
| as medidas da pilha (64 %, 81 %…) | `Motor.e` × 100, sem mudança | `TelaPet.tsx:207-217` |
| **"evento #N"** | `refsDoMotivo` sobre `refsOrd`, que sai `[]` no treino; o `MotivoLobos` não tem referência a evento | `src/fala.ts:80-85`; `motor/motor.ts:869`; `motor/lobos.ts:620-624` → **fora da prancha** |
| **o emote da categoria** | `EMOTE_CAUSA` só para `elogio` e `carinho` de `CAUSA_MEMORIA`, que os v13+ não produzem | `TelaPet.tsx:58-59` → **fora da prancha** |
| **os ícones de `CausaIcones`** | leem `Motor.motivo`; nos v13+, nada ou o "?" | `TelaPet.tsx:114-129` → **fora da prancha** (pergunta P1-4) |

Os números da prancha (64 %, `07:42`, `Dia 3`) são exemplo de layout, como na seção 0.

### O que muda na leitura do estado do pet

- **Hoje**, nos pets que abrem, o porquê da ação de agora só existe no painel DigiBrain (um toque na etiqueta a 1920, um toque no botão da
  borda a 390, e depois a leitura da seção "Agora"). O balão quase nunca aparece (só depois de um treino com pausa ou com a fala livre), e
  o "Por que ele disse isso" fica sem a causa da vida.
- **Ganha:** a ação e o porquê ficam sempre visíveis; a malha de aprendido aparece no instante em que o aprendido mudou a escolha, que é o
  "isso fui eu que ensinei" do guia. Referência de frequência: no E0, o aprendido decide 15,6 % de todas as decisões e 55,3 % delas têm um
  candidato só (`docs/futuro/digibrain_v3_e0.md` §1, citado em `AUDITORIA_V2_PRODUTO_MODULAR.md:54`); **é uma medida do Python, não dos
  saves do jogo**, e vale olhar na prancha com um save real.
- **Muda a leitura da B:** quase sempre a linha vai dizer "o instinto faria o mesmo" ou "só havia uma opção". É honesto; a malha fica rara
  e por isso pesa. O `?` só aparece antes da primeira decisão, não "tanto quanto a exploração", como a B temia.
- **Não ganha:** a causa ligada a uma ação do dono ("você me elogiou", "evento #41"): o A não registra isso. Ligar a decisão às ações do
  dono seria mudança no motor (fora, seção 6 da tarefa).
- A pilha, o dock, o chamado (a 1920) e o painel DigiBrain não mudam.

### O custo em determinismo

Nenhum: `Motor.digibrain()` "só lê: não muda o cérebro nem a rng" (`motor.ts:316-318`), e a linha não grava nada nem tem relógio próprio
(muda com a `revisao` do `useJogo`). O balão e a fala livre continuam como hoje. **Custo de desempenho, para o `rev-cena`:** o
`digibrain()` também monta o mapa dos pesos inteiro (`mapaPesos`, `digibrain.ts:109-140`) e o "o que aprendeu" a cada chamada; a linha
precisa só da `decisao`. O implementador deve chamar a `leituraDecisao` direto sobre o `cerebro.ultimoMotivo` (as mesmas entradas de
`motor.ts:328`), sem tocar o motor, ou memorizar pela `revisao`.

### O custo em e2e

- **Mais capturas mudam do que a B dizia:** a linha é sempre visível, então **todas** as capturas da tela Pet de um pet vivo mudam, a 1920
  e a 390, nas duas peles (`pet-estado`, `pet-v11`, `pet-v12`, as do `vida_pet_cena` e do `sprites_comer` que mostram o topo). A 390, o
  cartão do chamado desce 50 px, e as capturas com chamado mudam também ali. O ovo chocando e o pet morto não mudam (a linha some).
- **Fecha a pendência do porquê** (`PAINEL_V3.md` 2.1): a linha é um caminho até o porquê que não depende de fala registrada.
- **Testes novos:** um de componente para cada linha da tabela de estados (o texto, a malha só no `mudou`, o "?" no `null`, o nome
  acessível); um para o chip do balão com `fadiga_treino` (o defeito 1); um e2e que abre o DigiBrain pela linha e volta o foco ao fechar.
- O `hx_pele.test.ts` ganha o contraste do texto da linha e dos três chips sobre o pior pixel da cena.

### A prancha

`python docs/pranchas/ux-pet/gerar.py` escreve `pet_1920.html` e `pet_390.html` (`?pele=vidro|xcom`; `?sem` tira as notas amarelas).
`sh docs/pranchas/ux-pet/capturar.sh`, com `python -m http.server 8765 --bind 127.0.0.1` em `D:\Trab\digilab`, grava
`pet_1920_vidro.png`, `pet_1920_militar.png`, `pet_390_vidro.png` e `pet_390_militar.png` em `D:\Trab\digilab\capturas_ux_pet_aprovar\`.
O sprite é o Gabumon de `D:\Trab\digilab\Assets\arena_up` (fora do git, como na B3); o fundo é o hexagonal do guia no lugar da ilha.

- **1920:** a linha com o aprendido; o balão do treino com o chip "vem do corpo"; a pilha, o trilho, o dock e a etiqueta como hoje; um
  quadro só da prancha com os cinco estados da linha e os três chips do balão lado a lado.
- **390:** a linha com o "? sem motivo registrado" (o caso mais largo), o cartão do chamado na posição nova, o balão com o chip, os botões
  da borda, o dock e a barra.

### Perguntas ao Matheus

| # | pergunta | recomendação | custo de errar |
|---|---|---|---|
| P1-1 | o chip do balão no treino com pausa (`fadiga_treino`) usa a caixa sólida de necessidade ("vem do corpo") | **sim**: o próprio motor chama o pedido de pausa de necessidade com essa causa (`motor.ts:887`) | sim e errado: o rosa passa a cobrir cansaço de treino, que o dono provocou; não: o chip fica neutro e o defeito 1 se resolve do mesmo jeito |
| P1-2 | com o modular ativo, o que a linha diz | **"cérebro modular" sem marca nesta etapa**, e o porquê do modular (`leituraLab`) numa etapa própria | mostrar o motivo do A com o modular decidindo afirma uma causa falsa (princípio 1); o "?" também seria falso (há motivo, só noutro formato) |
| P1-3 | a linha abre o painel DigiBrain, e não o "Por que ele disse isso" como a B dizia | **o DigiBrain**: é onde está o porquê desta decisão; o "Por que ele disse isso" fica para o balão | o painel da fala não tem a causa da vida nos v13+ (o motivo dele é o do treino), e abrir por ali mostraria o defeito 3 |
| P1-4 | a 1920, a linha mostra também "o que mais pesou" (`percepcao[0]`, com o ícone da medida) no lugar dos ícones de `CausaIcones` | **não nesta etapa**: a linha fica com a ação e o aprendido; o "o que mais pesou" já está no DigiBrain | sim: a linha cresce ~160 px e a malha perde o peso; não: a B perde os "ícones da causa" que prometia, e a tela diz menos sem abrir nada |
| P1-5 | com "Exibir detalhes do pet" desligado, a linha fica | **fica, como texto sem botão** (o porquê de agora é a leitura principal da B; o detalhe é que sai) | some: quem desliga os detalhes perde o porquê; fica como botão: abriria um painel que a preferência tirou |
| P1-6 | o rótulo do chip é "aprendido", e não "aprendido com você" | **"aprendido"**: o A aprende pela consequência no corpo, que vem dos cuidados do dono e também do que o pet vive sozinho (`lobos.ts:19-21`) | "com você" afirma uma origem que o motor não separa; "aprendido" pode ler menos pessoal do que o princípio 2 quer |

---

## Mobile mínimo (M1, 2026-11-06)

Status: **PROPOSTO**. A M1 é só a tela Pet abaixo de 900 px. As folhas (M2) e a luta e o treino no celular (M3) ficam fora. Nada muda no
motor, no save, no log, nas rotas nem a partir de 900 px.

### A Digivice, reprovada (2026-11-06)

A primeira prancha da M1 (a direção "Digivice", commit `08b3dff8`: paleta `--dl-*`, DotGothic16 e Rubik, cinco cartões de vitais sempre
visíveis, barra de abas de 78 px) foi reprovada pelo Matheus:

> "ela tá com um estilo completamente anterior, de versões muito antigas. Não tá com as versões atualizadas. E também tem muito botão,
> muita informação. Tem que tirar todas essas informações. O usuário não precisa de tanta informação assim jogada na tela. Deixa tudo com
> ícones minimalistas."
>
> "o menu ali embaixo, eu não preciso estar ali embaixo, ele pode estar em alguma outra área da interface, e daí embaixo só fica os botões
> de ações mesmo. Porque a ideia é o jogador interagir com o jogo diretamente."

**O que se aproveita:** nada do visual (a paleta, as fontes, os cartões, a barra, os botões gordos com sombra). Do texto, só a leitura do
código que continua valendo: a lista dos seletores do e2e a 360 e 390 (refeita abaixo para o mínimo), a regra de "Exibir detalhes do pet"
desligado (agora M1-11), o "salvo" e o erro de gravação (agora M1-12), o achado do pedido de carinho que o dock não sugere (agora dentro da
M1-13) e a escolha entre fixo e seguir o pet (agora M1-5). As antigas M1-1 (a cor da aba), M1-2 (o pulso), M1-3 (a coluna de cinco),
M1-7 (o rótulo "agora"), M1-8 (a cor da saúde no cartão), M1-9 (o rosa do cartão) e M1-11 (o tema claro/escuro) caem com a direção.

### A direção nova e a prancha

A direção que o Matheus aprovou é o desenho `minimo.html` (fora do repositório): as peles de hoje (Vidro e Militar), a cena 3D atrás de
tudo, quase nada na tela, os destinos num canto de cima e, embaixo, só as ações.

**A prancha** fica em `docs/pranchas/ux-mobile/` e substitui a da Digivice (o designer a escreveu em `docs/pranchas/ux-pet/minimo/`,
porque o hook H8 só o deixa escrever em `docs/pranchas/ux-pet/`; o gerente a move, e os caminhos já estão escritos para a pasta final):
- `gerar.py` escreve sete páginas, cada uma o próprio celular: `pet_normal.html`, `pet_fome.html`, `pet_retrato.html`, `pet_mais.html`,
  `pet_dormindo.html`, `pet_chamado.html` e `pet_segurar.html`; `?pele=vidro|xcom` troca a pele (o `data-pele` do `<html>`, como no app)
  e `?notas` põe por cima as notas de fonte;
- `minimo.css` tem só cópias dos tokens `--hx-*` e `--hud-*` de `web/app/src/estilo/tokens.css` (Militar nas linhas 105-133, Vidro nas
  147-170, a transparência reduzida nas 173-180), os cantos em L de `pele-xcom.css:9-14` e os dois literais que o app já usa (o
  `#0A1316` sobre o rosa no Vidro, `pele-vidro.css:92`); nenhuma cor nova;
- o fundo são as capturas reais do jogo, fora do git, em `D:\Trab\digilab\capturas_ux_mobile_aprovar\minimo\_fundo\` (`cena_dia.png`,
  `cena_noite.png`, `retrato.png`), pelo caminho relativo `../../../../capturas_ux_mobile_aprovar/minimo/_fundo/`; a cena cobre a tela
  (`cover`), e o corte tira da vista os dois botões do HUD de hoje que a `cena_dia.png` tem gravados no canto de cima à direita;
- `capturar.sh` (servidor `python -m http.server 8765` com raiz em `D:\Trab\digilab`) grava em
  `D:\Trab\digilab\capturas_ux_mobile_aprovar\minimo\` os sete estados a 390×844 e o normal, a fome e o retrato a 360×800, nas duas peles
  (`minimo_<estado>_<largura>_<vidro|militar>.png`), e os sete a 390 no Vidro com as notas (`..._vidro_notas.png`);
- os ícones são os do lucide (o app usa o `lucide-react`), carregados da rede; as fontes são as das peles (`--hx-f`: Barlow e Rajdhani no
  Vidro, Saira Condensed no Militar). Sem o lucide a página mostra um erro na tela, não fica muda.

**Limites honestos da prancha:** a `cena_noite.png` é de outro pet, acordado (no jogo o pet que dorme fica achatado e com o "zz",
`sono.ts`); o chamado usa um ícone de traço no lugar do emote do UP (`emoji_exclam`, `TelaPet.tsx:238`); os números são exemplo de layout.

### O objetivo do jogador

Abrir o celular e ver o pet na ilha, quase sem nada por cima, e mexer nele com o polegar: as ações embaixo, ao alcance do dedo. Saber que
algo falta só quando falta (um aviso, um ponto e a ação certa crescendo), e ler o resto (os vitais, o porquê, a evolução) com um toque,
não de olho.

### A hierarquia

1. A cena 3D com o pet (a tela inteira, atrás de tudo).
2. As ações embaixo: Alimentar, Brincar, Limpar e o Mais, quatro círculos só com ícone.
3. O que falta, só quando falta: o aviso (o ícone e o %), o ponto rosa no retrato e a ação ligada rosa e maior.
4. O que ele faz: um ícone sobre o pet (a linha do agora sem texto); o toque abre o porquê no DigiBrain.
5. Os cantos de cima: à esquerda o retrato e a hora; à direita a coluna Conversar, Crescer, Lutar e Diário.
6. Por toque: o retrato abre os vitais e os painéis; o Mais abre as ações raras.

### Sempre visível, só quando existe, por gesto

| quando | o quê |
|---|---|
| sempre | o retrato (56 px; redondo no Vidro, reto no Militar), a hora ("D3 07:42"), a coluna de quatro ícones (48 px), o ícone do agora (48 px) e as quatro ações (62 px) |
| só quando existe | o aviso da necessidade (ícone e %, rosa cheio), o ponto rosa no retrato, a ação ligada rosa e com 74 px; o chamado urgente e a morte (os cartões de hoje, com texto); o balão da fala (15 s, como hoje, M1-15) |
| por gesto | o toque no retrato abre o leque: os cinco vitais (um botão só, o "Estado atual", que abre o painel com os Detalhes) e Evolução, Últimas ações, DigiBrain, Configurações e Meus pets; o toque no Mais abre Carinho, Tapa, Tratar, Pôr ração e Pôr a bola; o toque no ícone do agora abre o DigiBrain; segurar o dedo num botão mostra o nome dele |

Um leque por vez: abrir o retrato fecha o Mais e o contrário. Esc, o toque fora e um segundo toque no mesmo botão fecham, como o Mais de
hoje (`TelaPet.tsx:359-366`), e o foco volta ao botão que abriu.

### O que muda em cada elemento (hoje → mínimo)

| elemento | hoje (< 900 px) | mínimo | fonte do dado |
|---|---|---|---|
| plaquinha | caixa `hx` com o retrato, o nome e o estágio (o estágio some abaixo de 720 px, `casca.css:76`); o retrato abre Meus pets | só o retrato, que abre o leque (M1-1); o nome e o estágio saem da vista (ficam em Meus pets e na Evolução) | `Retrato` (`TelaPet.tsx:50-55`), sprite de `chaveSprite(m.forma)` |
| relógio | caixa com `hh:mm`; o dia, o sol e o "salvo" somem abaixo de 480 px (`casca.css:77`) | uma pílula com o dia e a hora; sem o sol; o "salvo" escondido e o erro como ícone (M1-12) | `diaDe`, `hhmm` de `m.e.tick` (`TelaPet.tsx:46-47`), o grupo de `Topo.tsx:29`; `erroSave` (`Topo.tsx:32`) |
| Conversar | `.topo-bt` de 44 px no topo (`Topo.tsx:35`) | o primeiro da coluna da direita, a mesma classe e o mesmo nome | — |
| Configurações | `.topo-bt` no topo (`Topo.tsx:36`) | no leque do retrato, o mesmo nome | — |
| barra de abas | `.dl-nav` embaixo com Pet, Crescer, Lutar e Diário, ícone e rótulo (`Nav.tsx`, `casca.css:88-91`) | **sai**; Crescer, Lutar e Diário viram a coluna da direita, só ícone (o rótulo fica para o leitor de tela); sem Pet, porque a tela Pet é a casa | `NOME_DESTINO` (`rotas.ts:12`), ícones de `Nav.tsx:9` |
| linha do agora | barra de texto no topo, "AGORA · brincando · aprendido ›" (`pet_hud.css:162-166`) | um ícone de 48 px sobre o pet, com um bico; ciano tracejado quando o aprendido mudou a escolha, um "?" quando não há motivo; o mesmo nome acessível e o mesmo toque (abre o DigiBrain) | `vistaAgora`, `rotuloAgora` (`LinhaAgora.tsx:30-51`); a ação de `m.acao` (`NOME_PET`, `motor/nomes.ts:18`); o ícone por ação é PROPOSTO (M1-5) |
| cartão do alto | `Prioridade`: o resumo de 15 s em texto ("está com fome", "quer brincar", "agora: à toa") ou o pedido com o Atender (`TelaPet.tsx:305-321`) | o ramo da necessidade vira o aviso (ícone e %); o "agora: …" e o desejo saem da vista (o ícone do agora já diz o que ele faz); o pedido urgente e a morte ficam como hoje (M1-6) | `resumoAgora`, `temPedido`, `Chamados`, `Morte` (`TelaPet.tsx:223-302`) |
| botões do lado | `.pet-lado`: Estado atual, Evolução, Últimas ações e DigiBrain, quadrados de 44 px sempre visíveis (`TelaPet.tsx:566-572`) | **saem**; os quatro vão para o leque do retrato, com os mesmos nomes | `TITULO_PAINEL`, `ICONE_PAINEL` (`TelaPet.tsx:441-442`) |
| vitais | só no painel Estado, em barras | no leque, cinco ícones com o número; abaixo do limiar, o número numa caixa rosa cheia (a forma e a cor, M1-14) | `Math.round(m.e[k] * 100)` (`TelaPet.tsx:216-217`), ícones de `ICONE_NEC` e `HeartPulse` (`TelaPet.tsx:209`, `:217`) |
| ações | dock com Alimentar, Brincar, Limpar, Carinho e Mais, ícone de pixel e texto, 52 px (`pet_dock.css:36`); a sugerida em `--hx-escolhido` (`pet_dock.css:43`) | Alimentar, Brincar, Limpar e Mais em círculos de 62 px só com ícone (lucide, M1-4), no `--hx-btn-*` da pele; a sugerida cresce para 74 px e fica rosa (`--hx-necessidade`); o texto fica para o leitor de tela | `ROTULO_DONO` (`acoes.ts:11-14`); a sugerida é `resumoAgora(...).acao` (`TelaPet.tsx:356`); a reserva do Alimentar (`TelaPet.tsx:370-373`) |
| Mais | coluna de 220 px com texto: Tapa, Tratar, Pôr ração e Pôr a bola (`pet_dock.css:46-49`) | uma fileira de círculos de 52 px acima das ações: Carinho, Tapa, Tratar, Pôr ração e Pôr a bola (M1-2, M1-3); o Mais aberto vira um × | `ORDEM_DOCK` (`TelaPet.tsx:327`); `BarraRacao` e `BarraBola` (`PorRacao.tsx:83`, `PorBola.tsx:132`) |
| chamado urgente | o cartão com o texto e o Atender, 56 px abaixo do topo | o mesmo cartão, abaixo do retrato e à esquerda da coluna (top 84 px, de 14 px à esquerda até 76 px da direita) | `temPedido` (`TelaPet.tsx:299-302`), `URGENTE_RESTA` (`:298`) |
| morte | o cartão "… se foi" com o "Chocar um ovo novo", sem o dock (`TelaPet.tsx:223-233`, `:587`) | igual, no mesmo lugar do chamado | `m.morte` |
| dormindo | o pet achatado e com o "zz" (`sono.ts`) | igual; o ícone do agora é a lua; sem aviso de energia enquanto ele dorme (M1-8) | `m.acao === "dormir"` |

### Os limiares (nenhum número novo)

O aviso, o ponto rosa e a ação rosa seguem **a mesma regra de hoje**, a da ação sugerida (`resumoAgora`, `TelaPet.tsx:284-295`), para que
os três nunca discordem:
- a fome abaixo de `FOME_FALA` = 0,15 (`web/app/src/hudPet.ts:14`);
- a energia, a higiene e o humor abaixo de `LIMIAR_NEC` = 0,5 (`TelaPet.tsx:279`);
- vence a mais baixa; a ação ligada é `ACAO_NEC` (`TelaPet.tsx:276`): a energia não tem ação (`null`), então o aviso aparece e nada
  cresce.

Esses dois limiares são da tela, PROPOSTO e SEM FONTE (`hudPet.ts:5`). O limiar do motor para a necessidade é outro,
`CDJ.limiarNecessidade` = 0,3 (`web/app/motor/constantes.ts:29`), e só entra no desejo (`m.desejoAtual`). A M1 não troca um pelo outro
(M1-6). O emoji da carne que a cena desenha sobre o pet abaixo de `FOME_EMOTE` = 0,5 (`hudPet.ts:15`, `PalcoPet.tsx:150`) não muda.

### A volta (as folhas, M2)

Sem a barra, cada folha (Crescer, Lutar, Diário, Conversar, Configurações) volta para a casa pelo × que já existe, "Fechar e voltar ao
Pet" (`PainelTela.tsx:19`), pelo Esc e pelo toque fora do modal (`PainelTela.tsx:45-46`). Trocar de folha passa pela casa (dois toques).
A M1 tira a barra de dentro do modal (hoje ela vai junto, `App.tsx:188-191`, `PainelTela.tsx:48`); o desenho do cabeçalho da folha é da
M2 (M1-10).

### Wireframes a 390×844 e a 360×800 (a 1920×950 nada muda)

O normal, a 390 (a 360 é o mesmo desenho, 30 px mais estreito: as quatro ações somam 296 px e cabem):

```
┌──────────────────────────────────────┐
│ (◉)•[D3 07:42]                  [Con]│  y 14–70: retrato e hora; o • rosa só com necessidade
│                                 [Cre]│  a coluna, 48 px, gap 10, até y 236
│                                 [Lut]│
│                                 [Diá]│
│                                      │
│             [ ali 12 % ]             │  y ~300: o aviso, só quando existe
│                 (♪)                  │  y ~367: o ícone do agora (toque: DigiBrain)
│                  ▾                   │
│                (pet)                 │  a cena 3D atrás de tudo
│                                      │
│       (Ali)  (Bri)  (Lim)  (⋯)       │  y ~752–814: as ações; a ligada com 74 px
└──────────────────────────────────────┘
```

O retrato aberto e o Mais aberto (um por vez; aqui juntos só para caber):

```
┌──────────────────────────────────────┐
│ (◉)[D3 07:42]                   [Con]│
│ [com 64|ene 41|hig 70|hum 72|saú 95] │  y 84: o botão "Estado atual" (o 41 em caixa rosa)
│ [Evo]                           [Cre]│  y 156: o leque dos painéis, 48 px
│ [Últ]                           [Lut]│
│ [DgB]                           [Diá]│
│ [Cfg]                                │
│ [Meu]                                │
│                 (♪)                  │
│   (Car) (Tap) (Tra) (Raç) (Bol)      │  o Mais aberto, 52 px, acima das ações
│       (Ali)  (Bri)  (Lim)  (×)       │
└──────────────────────────────────────┘
```

O chamado urgente: o cartão "Chamando você · um carinho atende · ATENDER" ocupa de y 84 até ~200, entre o retrato e a coluna; o resto é
igual ao normal.

### O que muda na leitura do estado do pet

- **Zero número e zero texto fixos na casa.** Os vitais passam de "um toque no botão da borda" para "um toque no retrato"; o que ele faz
  passa de uma frase no topo para um ícone sobre o pet (o porquê inteiro continua a um toque, no DigiBrain, e inteiro no leitor de tela).
- **O que falta se lê por três sinais que concordam:** o aviso (ícone e %), o ponto rosa no retrato e a ação que resolve, rosa e maior.
  Os três saem da mesma regra (`resumoAgora`), então não há ponto sem ação nem ação sem aviso, salvo a energia, que não tem ação do dono.
- **O aprendido continua à vista:** o ícone do agora fica ciano e tracejado só quando o aprendido mudou a escolha
  (`quem_decidiu.mudou`, `LinhaAgora.tsx:36`), a forma do chip aprendido (`hud.css:74`); o neutro é silêncio, como na P1.
- **O que some da vista** (e fica a um toque): o nome e o estágio do pet, o "agora: …" e o desejo do resumo, o rótulo das ações e dos
  destinos. O cartão do chamado urgente e o da morte continuam com texto, porque pedem uma decisão.

### Tokens usados

Só cópias dos valores de `web/app/src/estilo/tokens.css`, nas duas peles: `--hx-miolo`, `--hx-miolo-2`, `--hx-borda`, `--hx-borda-topo`,
`--hx-texto`, `--hx-texto-2`, `--hx-sec`, `--hx-rotulo`, `--hx-escolhido`, `--hx-escolhido-ink`, `--hx-escolhido-borda`,
`--hx-escolhido-brilho`, `--hx-btn-bg`, `--hx-btn-ink`, `--hx-btn-borda`, `--hx-alerta`, `--hx-perigo`, `--hx-ok`, `--hx-necessidade`,
`--hx-aprendido`, `--hx-foco`, `--hx-f`, `--hx-f-num`, `--hx-num`, `--hx-vidro`, `--hx-sombra`, `--hx-luz`, `--hud-fundo-1`,
`--hud-fundo-2`, `--hud-desfoque`, `--hud-brilho`; os cantos em L `--xcom-cantos` (`pele-xcom.css:9-14`). A semântica fixa (guia 3):
`--hx-necessidade` no aviso, no ponto, na ação ligada e no vital baixo; `--hx-aprendido` no ícone do agora; `--hx-alerta` só no ícone do
chamado (como `pet_hud.css:70`) e no traço das notas da prancha; `--hx-perigo` no erro de gravação. Os brilhos rosa do Vidro são
`color-mix` do próprio `--hx-necessidade`, sem valor novo. Nenhum `--dl-*` na tela Pet do celular.

### Os nomes acessíveis (o e2e depende)

Todos os botões que existem hoje ficam com o mesmo nome; o texto que sai da vista fica num `sr-only` dentro do botão (o `hasText` do
Playwright e o nome acessível continuam casando). A prancha mostra o nome num balão ao segurar o dedo (`pet_segurar.html`); no jogo o
mesmo balão aparece no foco do teclado, e o `title` fica para o mouse.

| botão | nome de hoje (fonte) | no mínimo |
|---|---|---|
| retrato | "Meus pets" (`Topo.tsx:18`) | **muda no celular**: abre o leque, "Painéis do pet" (o nome da nav que ele substitui, `TelaPet.tsx:566`); o "Meus pets" vira um item do leque com o mesmo nome (M1-1). No desktop não muda |
| Conversar, Configurações | `aria-label` (`Topo.tsx:35-36`) | iguais; o Conversar na coluna, o Configurações no leque |
| Crescer, Lutar, Diário | o rótulo `NOME_DESTINO` (`Nav.tsx:18`) | iguais, em `sr-only` |
| Estado atual, Evolução, Últimas ações, DigiBrain | `TITULO_PAINEL` (`TelaPet.tsx:441`, `:569`) | iguais; o "Estado atual" é o botão dos vitais, com os valores em `aria-describedby` ("comida 64 %; energia 41 %, baixa; …") |
| o agora | `rotuloAgora(v, true)` (`LinhaAgora.tsx:44-51`) | igual |
| as ações | `ROTULO_DONO` (`acoes.ts:11-14`); o Alimentar com mundo, "Alimentar (reserva: põe a ração no comedouro)" (`TelaPet.tsx:372`); "Mais" (`:378`) | iguais |
| Pôr ração, Pôr a bola | `PorRacao.tsx:83`, `PorBola.tsx:132` | iguais |
| o aviso | o texto do resumo, "está com fome" e "Estado" (`TelaPet.tsx:316-318`) | igual, em `sr-only`; o % fica `aria-hidden` |

### O custo em determinismo

Zero. Só CSS, a ordem dos elementos e a visibilidade; o motor, o log, o save e o replay não mudam. O leque e o Mais abertos são estado de
tela (`useState`), fora do save, como o Mais de hoje.

### O custo em e2e

- **O desktop não muda:** as regras novas ficam em `@media (max-width:899px)`, e o DOM só difere onde a tela já se divide por `useLargo`
  (`TelaPet.tsx:343-351`). Os testes que rodam no viewport padrão de desktop (`jogo.spec.ts:69`, `:75`, `:84`, `:104`, `:146`, `:195`,
  `:213`, `:615`, `:1732`, `:1738`, `:1753`; `lab_modular.spec.ts:29`, `:52`; `conferencia_pele.spec.ts:153-184`, `:262`) e as capturas a
  1280 e 1920 têm de dar diff zero.
- **O que quebra a 360 e 390 e o que muda no teste:**
  - `jogo.spec.ts:1172` e `:1203` (o "DigiBrain" pelo nome exato) e `e2e_capturas/lab.spec.ts:92` (a 390): o botão passa a morar no leque;
    o teste abre o retrato antes (um `abrirLeque` como o `abrirMais` de `:1501`). O ícone do agora não serve: o nome dele não casa com o
    exato;
  - `jogo.spec.ts:1303-1308` (Estado atual, Evolução, Últimas ações abaixo de 900): abrir o leque antes de cada um, porque o leque fecha
    ao escolher; o `#pet-painel .necessidades4` continua (o painel Estado não muda);
  - `jogo.spec.ts:1504-1516` (`infoMundoNoEstado`, chamado a 390 pelos testes do mundo): abrir o leque antes do "Estado atual"; o
    fechamento da linha 1515 (um segundo clique no mesmo botão) passa para o "Fechar Estado atual" ou o Esc;
  - `jogo.spec.ts:1272` e `:1275`: no celular, 3 `.acao-destaque` (eram 4) e 3 `.acao-extra` (eram 2), com o Carinho no Mais;
  - `vida_pet_cena.spec.ts:70` (o "Carinho" a 390): abrir o Mais antes;
  - `jogo.spec.ts:285-288` ("layout em 390"): o `.dl-nav` sai de dentro do modal (M1-10), e o `querySelector(".dl-nav")` nas rotas
    `crescer/evolucao` e `lutar/campanha` dá `null`; o teste passa a esperar nenhuma barra abaixo de 900 (ou a coluna, se M1-10 ficar com
    ela no modal, que é mais alta que larga e daria `navLateral` errado).
- **O que precisa continuar valendo (e o desenho já respeita):**
  - `jogo.spec.ts:1171`: `.topo-bt[aria-label="Conversar"]` visível; o Conversar da coluna fica com a classe;
  - `jogo.spec.ts:157-178` (o guia 14 a 360 e 390): nenhum botão visível abaixo de 44 px (o menor é 48) e sem rolagem lateral (a fileira
    do Mais soma 308 px, as ações 296);
  - `jogo.spec.ts:1268`: a cena com mais que o dobro da área do `.pet-dock` (sem a barra, o dock fica menor);
  - `jogo.spec.ts:1274-1278`, `:1501`, `:1620`: `.acoes-pet .acao-mais`, `#acoes-mais` e `.racao-bt:not(.bola-bt)` ficam;
  - `jogo.spec.ts:1280`: nenhum `.pet-retrato` (o retrato continua `.topo-retrato`);
  - `jogo.spec.ts:1683`: o nome da reserva do Alimentar; `:1315`: `.cena-fala` com 0;
  - `vida_pet_cena.spec.ts:55`: o toque em (12, 130) da cena cai fora do retrato (14 a 70 px) e do leque fechado; o ícone do agora não
    pode ficar sobre o pet (o toque no pet é o carinho, `:63`), e por isso fica acima dele (M1-5).
- **Capturas que mudam:** todas as da tela Pet a 360 e 390 (`e2e_capturas/telas.spec.ts` com 390 na lista, `conferencia_pele.spec.ts:229-236`,
  `sprites_comer.spec.ts:15`, `vida_pet_cena.spec.ts:13`, e o `digibrain-390.png` de `jogo.spec.ts:1188`). Sem a barra, o `--casca-barra`
  vai a 0 abaixo de 900 (`casca.css:9`), o que muda a reserva do habitat (`--hab-baixo`, `TelaPet.tsx:513`) e o lugar do modal das
  folhas (`casca.css:119-120`).
- **Testes novos:** o leque abre e fecha (Esc, toque fora, foco de volta ao retrato); o aviso, o ponto e a ação rosa aparecem juntos e
  somem juntos; o vital baixo com a caixa cheia e o "baixa" no nome; o ícone do agora tracejado só no caso "aprendido"; o rótulo ao
  segurar e no foco; o foco visível nos botões novos nas duas peles (o `jogo.spec.ts:247` só roda no desktop).

### Perguntas ao Matheus

| # | pergunta | recomendação | custo de errar |
|---|---|---|---|
| M1-1 | no celular o retrato abre o leque (vitais e painéis), e não mais Meus pets; ele se chama "Painéis do pet", e o Meus pets vira o último item do leque | **sim**: é a direção, e o nome novo diz o que o botão faz; o desktop continua "Meus pets" | manter "Meus pets" no retrato: o nome mente para o leitor de tela; tirar Meus pets do celular: não há outro caminho para trocar de pet |
| M1-2 | o Carinho sai das fixas e vai para o Mais (a direção) | **sim**: o toque no pet já é o carinho (`vida_pet_cena.spec.ts:63`), e o polegar fica com as três que resolvem uma necessidade | o "Chamando você · um carinho atende" pede uma ação que está escondida (o Atender do cartão resolve); dois testes mudam |
| M1-3 | o Pôr ração fica no Mais, com a bola (a direção cita só a bola) | **fica**: é a interação planejada da comida (`TelaPet.tsx:369`) e o e2e do mundo a usa (`jogo.spec.ts:1276`, `:1520`, `:1613`) | tirar: o dono do v12 perde o gesto de pôr a ração e cinco testes quebram; ficar: o Mais tem cinco itens (308 px, cabe a 360) |
| M1-4 | os ícones das ações viram os de traço do lucide (o mesmo das telas), no lugar do pixel art de hoje (`IconeAcao`, `TelaPet.tsx:333-340`) | **lucide**, e o ícone da ação igual ao da necessidade que ela resolve (a coxa da comida no Alimentar, a gota da higiene no Limpar) | pixel art: destoa dos ícones de traço da coluna e do leque; lucide: a tela perde o pixel do UP, que fica só no pet e nos emotes da cena |
| M1-5 | o ícone do agora: um por ação (à toa = xícara, dormindo = lua, comendo = coxa, brincando = nota, chamando você = megafone, explorando = bússola, emburrado = cara brava), fixo acima do lugar do pet, e não seguindo o pet | **fixo na M1**, com esse mapa (PROPOSTO, desenho meu; a nota e a carne repetem os emotes da cena, `cenaAcao.ts:41-43`) | seguir: ler a posição projetada da cena (`cenaPara`) a cada quadro, o custo maior da etapa; fixo: com o pet na borda da ilha o ícone fica longe dele, e o emote da cena e o ícone dizem a mesma coisa duas vezes |
| M1-6 | o aviso usa a regra da ação sugerida de hoje (`FOME_FALA` 0,15 na fome, `LIMIAR_NEC` 0,5 nas outras, `TelaPet.tsx:279-291`), e não o limiar do motor (`CDJ.limiarNecessidade` 0,3, `constantes.ts:29`); o "agora: …" e o desejo saem do resumo; o chamado aberto ainda não urgente vira um aviso com o ícone do chamado, sem % | **a regra de hoje**: aviso, ponto e ação concordam, e nenhum número muda | com 35 % de comida o leque mostra o vital rosa (0,5) e não há aviso (0,15): a incoerência da antiga M1-9 continua, só que escondida no leque; trocar pelo 0,3 do motor muda o que o dock sugere hoje |
| M1-7 | o aviso dura como o resumo de hoje (15 s, `AVISO_MS`, `hudPet.ts:12`; fixo com a fome abaixo de `FOME_FALA`), e o ponto rosa e a ação rosa ficam enquanto a necessidade valer | **sim** | o aviso sempre: volta o texto fixo que a direção tirou; o ponto também por 15 s: depois disso nada diz que falta algo |
| M1-8 | dormindo, a energia baixa não mostra aviso (o ponto fica); é uma regra de tela nova, sem número | **sim**: dormir já é o pet resolvendo, e a energia não tem ação do dono (`ACAO_NEC.energia` é `null`) | com aviso: toda noite um aviso que o dono não pode atender; sem: quem abre o app de noite só vê o ponto |
| M1-9 | o tempo do toque longo que mostra o nome: **PROPOSTO 500 ms, SEM FONTE** (o costume dos celulares, não verificado); o balão some ao soltar | decidir o número; o balão também no foco do teclado | curto: o toque normal mostra o balão sem querer; longo: ninguém descobre o nome |
| M1-10 | as folhas no celular perdem a barra de dentro do modal (`PainelTela.tsx:48`); voltar é o × "Fechar e voltar ao Pet", o Esc ou o toque fora; trocar de folha passa pela casa | **sim na M1**, e o cabeçalho da folha fica para a M2 | manter a barra no modal: a barra que a direção tirou volta em toda folha; tirar: ir de Crescer a Lutar custa dois toques, e o teste "layout em 390" muda |
| M1-11 | com "Exibir detalhes do pet" desligado (`hudPet.ts:4-5`, `TelaPet.tsx:533`), o leque só tem Configurações e Meus pets, e o ícone do agora vira só desenho, sem toque (`LinhaAgora.tsx:71`) | **sim**, como hoje | os vitais ficam: a opção perde metade do efeito; somem: quem desliga perde os números, como hoje perde o Estado |
| M1-12 | o "salvo" continua escondido no celular, e o erro "não salva" vira um ícone (`CloudOff`, `Topo.tsx:32`) em `--hx-perigo` ao lado da hora | **mostrar só o erro** | esconder o erro: o dono perde progresso sem saber; mostrar sempre: mais um ícone fixo |
| M1-13 | a sugerida que não vem de uma necessidade (o desejo aprendido, `TelaPet.tsx:292-293`) e a que mora no Mais (o Carinho): o rosa só vale para a necessidade (a baixa, o chamado, o desejo "necessidade"); a vontade aprendida ganha só o contorno ciano tracejado; se a sugerida está no Mais, o Mais leva a marca | **sim**; e o achado da Digivice segue: com o "Chamando você" o dock sugere a necessidade mais baixa, não o Carinho, e a M1 não mexe no `resumoAgora` | rosa para tudo: o rosa deixa de dizer "vem do corpo" (guia 3); sem marca no Mais: a sugestão do Carinho some |
| M1-14 | no leque, o vital abaixo do limiar fica rosa (`--hx-necessidade`) e com o número em caixa cheia; o painel Estado continua com o `--hx-alerta` de hoje (`TelaPet.tsx:216`) até a M2 | **sim**: o leque é a necessidade, e a forma (a caixa) não depende da cor | mesma cor do painel: o amarelo de destaque vira necessidade só no celular; trocar o painel agora: a M1 entra na M2 |
| M1-15 | o balão da fala (15 s depois de cada reação, arrastável, `TelaPet.tsx:137-146`) continua como hoje, com texto | **continua**: é o pet falando e some sozinho; ele fica acima do ícone do agora | tirar: o pet perde a voz no celular; ficar: por 15 s há um texto na tela |

---

## Lugares da ilha (L1) — a câmera solta e o minimapa, no desktop (2026-11-06)

A direção escolhida pelo Matheus em 2026-11-06 é a **B, "Lugares da ilha"** (página de direção, seção "Minimapa e câmera livre"): cada menu
vira um lugar da ilha, e abrir o menu leva a câmera até lá. A **L1** é o primeiro passo e só vale **a partir de 900 px**: soltar a câmera do
pet e pôr o minimapa. A L2 (Treinar no saco), a L3 (a arena e o diário) e o celular (junto da M2 do mobile) ficam fora. **O celular não
muda nesta etapa.**

### O objetivo do jogador

Olhar outras partes da ilha sem perder o pet: saber onde a câmera está, onde ele está, e voltar a ele com um gesto. Hoje a câmera livre
(`orbita.ts`, Ajustes > Visual > Controle "Livre") gira e aproxima, mas fica presa ao pet: `vista.ts` põe a câmera em `petCel + desloc` a
cada quadro (`desenhar`, "a camera atras dele").

### A hierarquia

1. a ilha (a cena 3D inteira), que passa a poder ser percorrida;
2. o minimapa, no canto de baixo à direita: onde a câmera olha, onde o pet está e os lugares que já existem;
3. o "seguir o pet" e o aviso de borda, que só aparecem quando a câmera está longe dele;
4. a HUD de hoje (topo, trilho, pilha, dock), sem mudança, menos a etiqueta do DigiBrain, que sai do canto.

### Sempre visível (≥ 900 px)

| peça | onde | o que mostra |
|---|---|---|
| **minimapa** | círculo de 232 px (PROPOSTO, SEM FONTE), a 16 px da direita e de baixo, no lugar da etiqueta do DigiBrain | a ilha vista de cima, norte para cima; o pet (ponto rosa); o cone da vista; os ícones dos lugares e objetos (tabela abaixo); um "N" pequeno no alto |

Com o controle "Fixa" não há câmera solta; o minimapa fica (serve para se localizar), sem mover a câmera ao clicar (pergunta L1-3).

### Por gesto

| gesto | efeito | teclado |
|---|---|---|
| <kbd>W</kbd><kbd>A</kbd><kbd>S</kbd><kbd>D</kbd> e as setas | a câmera anda no chão, na direção em que olha (W é a frente da vista) | o próprio |
| arrastar com o botão **direito** ou o **do meio** na cena | a câmera anda junto (o chão acompanha o cursor) | WASD |
| arrastar com o **esquerdo**, a roda, Shift + roda | como hoje: gira e inclina, aproxima, gira | <kbd>Q</kbd>/<kbd>E</kbd> giram, <kbd>+</kbd>/<kbd>−</kbd> aproximam (pergunta L1-5) |
| <kbd>F</kbd>, um toque no retrato, o botão "seguir o pet" | a câmera volta ao pet e passa a segui-lo (transição curta; sem transição com "reduzir movimento") | <kbd>F</kbd> |
| clique no minimapa | a câmera vai até o ponto (a mesma transição) | com o foco no minimapa, as setas andam e <kbd>Enter</kbd> = <kbd>F</kbd> (pergunta L1-5) |
| segurar e arrastar no minimapa | a câmera vai junto, sem transição | — |
| **o pet chama** e está fora da tela | um aviso na borda da tela, do lado em que ele está, com a seta; clicar nele = <kbd>F</kbd> | <kbd>F</kbd> |

- **Quando solta:** WASD, as setas, o arrasto direito ou do meio e o minimapa trocam a câmera de "seguindo" para "solta". O giro, a
  inclinação e o zoom de hoje **não** soltam: continuam em volta do ponto olhado, que é o pet enquanto ela segue.
- **O "seguir o pet"** (botão só com o ícone `LocateFixed` e a tecla <kbd>F</kbd> ao lado, nome acessível "Seguir o pet") aparece em cima
  do minimapa quando o ponto olhado está a mais de **6 células** do pet (PROPOSTO, SEM FONTE).
- **"Quando o pet chama":** os chamados visíveis do In-Training (`chamadosVisiveis`, `hudPet.ts`) ou o pet chamando você
  (`Motor.acao === "chamar_atencao"`), os mesmos casos do cartão do chamado (`TelaPet.tsx:301`).
- **A câmera fica dentro da ilha:** o ponto olhado não sai da grade (`Ilha.x0 … x0 + larg`, `z0 … z0 + prof`, `grade.ts`, classe `Ilha`).
- **As teclas valem só com a cena livre:** nenhum painel por cima (`CENA.coberto`) e nenhum campo de texto em foco, para não roubar o WASD
  do Conversar nem de um formulário.

### Os ícones do minimapa e a fonte de cada um

Só o que o motor (ou a vista que já existe) tem. Os lugares da L2/L3 (o portão da arena e a barraca do diário) **não entram** até existirem.

| marca | o que é | fonte |
|---|---|---|
| ponto rosa | o pet desenhado (a posição do motor, interpolada) | `Mundo.pet` (`motor/mundo.ts`, campo `pet`), pelo `Seguidor` (`vista.ts`, `petDesenhado`) |
| cone | a vista: o ponto olhado e a direção da câmera no chão | `ORBITA` e a câmera do habitat (`orbita.ts`, `CAMERAS` em `ilha/constantes.ts`); nada do motor |
| `Bed` | o ninho | `LayoutMundo.ninho` (`motor/constantes.ts:406`, `[4, 15]`), por `ninhoDe` (`vistaMundo.ts`) |
| `Utensils` | o comedouro | `Mundo.comedouro` (`motor/mundo.ts`), `LayoutMundo.comedouro` `[10, 15]` (`motor/constantes.ts:406`) |
| `Dumbbell` | o saco de pancada | **só da vista**: `Itens.sacoEm` = ninho + `SACO_DESDE_NINHO` (`ilha/itens.ts:217`, `ilha/constantes.ts:56`); é o lugar da L2 |
| `Volleyball` | a bola | `Mundo.bola` (`motor/mundo.ts`), a desenhada (`Itens.bolaDesenhada`) |
| ponto verde-escuro | as árvores de fruta do motor (J1–J3, M1–M6 no layout padrão; o layout MVP dos pets v13+ não tem nenhuma, `motor/constantes.ts:450`) | `Mundo.arvores` (`motor/mundo.ts`), `LayoutMundo.arvores` (`motor/constantes.ts:407-409`) |
| ponto da cor da comida | ração e fruta no chão | `Mundo.comidas` (`motor/mundo.ts`); as cores são as da cena (`COR_RACAO`, `COR_FRUTA`, `ilha/itens.ts:22-24`) |
| — | o cocô e o kit médico | **fora**: são enfeites da vista (`cocos.ts`, `itens.ts`), e encheriam a casa de pontos (pergunta L1-4) |

O fundo do minimapa sai da **grade que a cena já lê** (`ilhaDe(mu.cm)`, `grade.ts:230`): uma célula por pixel de um canvas pequeno, nas
cores da própria ilha (`PALETA_ILHA`, `cena.ts:83-86`: a grama por região, o caminho e a areia; a água do shader, `cena.ts:206`), com o
planalto e o morro um pouco mais escuros, para ler o relevo. **Nenhuma cor nova**: são as que a cena já pinta. Nos mapas Voxel, Floresta
e Cassette, a mesma grade com a paleta do estilo (`estilos.ts`).

**A escala:** o círculo mostra a área andável inteira (64 × 30 células, `CMU`, `motor/constantes.ts:437`) e um pouco da moldura, a ~3,3 px
por célula, norte para cima e fixo (a lição do Scarlet e Violet, na página de direção). Pergunta L1-1.

### O estágio (guia 9)

Nada muda por estágio: o minimapa e a câmera são do dono, não do pet. Com o ovo chocando o minimapa também aparece (a ilha existe).

### As cores pelos tokens

| peça | token |
|---|---|
| a moldura do círculo | `--hx-borda` e `--hud-brilho`; no Vidro, a luz `--hx-luz` (como o `.hud-painel::before`) |
| o fundo em volta da ilha (fora da grade) | `--hud-fundo-2` |
| o pet | `--hx-necessidade` (o rosa), com o anel `--hx-foco` (pergunta L1-2) |
| o cone | `--hx-foco` com 30 % de opacidade |
| os ícones | uma caixinha `--hx-miolo` com `--hx-borda`, o traço em `--hx-texto` |
| o "N" | `--hx-rotulo`, `--hx-f`, 11 px |
| o "seguir o pet" e a tecla | a caixa da HUD (`.hud-caixa`, `--hud-ch-p`), a tecla com `--hx-tecla` |
| o aviso de borda | a caixa da HUD com a borda `--hx-necessidade` (é um chamado de cuidado, guia 3) |
| o foco | `outline: 2px solid var(--hx-foco)` |

### O DigiBrain sai do canto

A etiqueta do DigiBrain (`TelaPet.tsx:575`) ocupa hoje o canto do minimapa. **Recomendação: ela vira a quarta linha da pilha da direita**,
"DigiBrain", no formato de "Evolução" e "Últimas ações" (o ícone `Brain`, o título e a risca), e abre o mesmo painel. A linha do agora
(P1-3) continua abrindo o DigiBrain. A página de direção sugeria o retrato, mas o retrato já abre "Meus pets" e passa a voltar a câmera
ao pet (<kbd>F</kbd>); um terceiro uso nele confundiria. Pergunta L1-6.

### Wireframes

```
1920×950, a câmera seguindo (o normal)
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│[◉ Gomamon][AGORA dormindo · Exausto · só havia uma opção ›]  DIGILAB      [Dia 1 14:10 ● salvo]│
│ ┌────┐                                                              ┌ Estado atual ─────────┐│
│ │Pet │                                                              │ com ▮▮▮▮▮▯▯▯▯ 49 %    ││
│ │Cre │                                                              │ …                     ││
│ │Lut │                                                              ├ Evolução ─────────────┤│
│ │Diá │                                                              ├ Últimas ações ────────┤│
│ │Con │                                                              ├ DigiBrain (NOVA) ─────┤│
│ │Aju │                                                              └───────────────────────┘│
│ └────┘                           (pet)                                                       │
│                         ilha 3D (tela inteira)                                  ╭────────╮   │
│                                                                                 │   N    │   │
│                                                                                 │ ▲◉     │   │
│            [Alimentar][Brincar][Limpar][Carinho][Tapa][Tratar][Mais]            ╰────────╯   │
└──────────────────────────────────────────────────────────────────────────────────────────────┘

1920×950, a câmera solta, longe do pet, com o pet chamando
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│ (topo igual)                                                                                 │
│ trilho                                                                 pilha                 │
│ ┌───────┐                                                                                    │
│ │◂ ! ◉  │ ← aviso na borda, do lado em que o pet está (só quando ele chama)                   │
│ └───────┘                                                                                    │
│                       a mata, a leste (sem o pet na tela)                       [⌖ F]        │
│                                                                                ╭────────╮    │
│                                                                                │ ◉    ▲ │    │
│            [Alimentar][Brincar][Limpar][Carinho][Tapa][Tratar][Mais]           ╰────────╯    │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
```

Até 899 px **nada muda**: sem minimapa, sem WASD, e a etiqueta e os botões da borda como hoje.

### O que muda na leitura do estado do pet

- **Ganha:** onde o pet está na ilha, de relance, e onde ficam o ninho, o comedouro, a bola e as árvores com fruta; dá para ver o pet ir
  até uma fruta que caiu longe.
- **Risco:** com a câmera longe, o pet sai da tela e o dono pode perder um chamado. O aviso de borda e o ponto rosa cobrem isso; o
  cartão do chamado (no alto, ao centro) continua igual.
- A HUD não muda, menos a etiqueta do DigiBrain.

### O custo em determinismo

Nenhum: tudo é vista, como a `ORBITA` (`orbita.ts`, cabeçalho). O ponto olhado, o modo "seguindo/solta" e o minimapa ficam só nesta
página, fora do save, do registro e do replay; o minimapa só lê o `Motor.mundo` (pet, bola, comidas, árvores) e a grade. O `paraMundo`
e o `paraTela` (o arrasto da comida e da bola) passam a usar a dobra centrada no ponto olhado, e não no pet: é uma pergunta para o
`rev-cena` (o mundo curvo centrado longe do pet).

### O custo em e2e

- **Capturas:** o minimapa entra em toda captura da tela Pet a 1920 (nas duas peles), e a etiqueta do DigiBrain sai do canto; essas
  referências mudam e precisam do ok do Matheus antes do `--update-snapshots`. **As de 390 e 360 não podem mudar** (portão: o DOM e a
  captura com o canvas escondido, base × branch).
- **Testes novos:** a câmera solta, pura (o WASD no plano da vista, o limite da grade, o "seguir" volta ao pet, a distância do botão); o
  minimapa (célula ↔ px, o clique leva o ponto olhado); um e2e a 1920 que aperta D, vê o botão aparecer, aperta F e o vê sumir; o nome
  acessível do minimapa.

### A prancha

`python docs/pranchas/ux-lugares/gerar.py` escreve `lugares_normal.html`, `lugares_longe.html` e `lugares_mapa.html` (`?pele=vidro|xcom`;
`?sem` tira as notas). `sh docs/pranchas/ux-lugares/capturar.sh`, com `python -m http.server 8765 --bind 127.0.0.1` em `D:\Trab\digilab`,
grava as seis capturas em `D:\Trab\digilab\capturas_ux_lugares_aprovar\`. O fundo é uma captura real da ilha a 1920 (o Gomamon, o sprite
do jogo), e o minimapa é a ilha de verdade, gerada da grade (`ilha_json.mts` e `ilha_png.py`, ao lado); as imagens ficam fora do git, em
`capturas_ux_lugares_aprovar\fundo\` (UI_GUIDELINES 5.1).

- **normal:** a tela de hoje com o minimapa no canto e a linha "DigiBrain" na pilha.
- **longe:** a câmera solta sobre a mata, o pet fora da tela chamando: o aviso na borda, o "seguir o pet" com o <kbd>F</kbd>, o cone longe
  do ponto rosa.
- **mapa:** num quadro da prancha (não é tela), as duas escalas da pergunta L1-1 ampliadas e a legenda de cada marca, com a fonte.

### Perguntas ao Matheus

| # | pergunta | recomendação | custo de errar |
|---|---|---|---|
| L1-1 | a escala do minimapa: **A**, a ilha inteira, fixa, norte para cima (~3,3 px por célula); ou **B**, a janela de ~27 × 27 células em volta do ponto olhado (9 px por célula) | **A, e a roda sobre o minimapa aproxima até a B** (as duas na prancha `lugares_mapa`) | só a A: na casa o ninho, o saco, o comedouro e o pet se encostam (a prancha mostra); só a B: não mostra os lugares longe, que é o que o minimapa veio resolver |
| L1-2 | o pet é o ponto rosa (`--hx-necessidade`), como na página de direção | **sim, com o anel branco** | o guia 3 reserva o rosa sólido para "vem do corpo"; um ponto pequeno no mapa dificilmente confunde, e a alternativa é o retrato do pet num círculo |
| L1-3 | com o controle "Fixa", o minimapa aparece | **aparece, sem mover a câmera** | some: quem usa a câmera fixa perde o "onde está"; aparece e move: a "Fixa" deixa de ser fixa |
| L1-4 | o cocô e o kit médico ficam fora do minimapa | **fora** nesta etapa | dentro: mais pontos na casa, onde já está apertado |
| L1-5 | os atalhos a mais: Q/E giram, +/− aproximam, as setas e o Enter no minimapa com foco | **sim**: o guia 13 pede teclado para tudo, e hoje o giro e o zoom só têm mouse | conflito com algum atalho: Q, E, + e − não têm uso no app hoje |
| L1-6 | a etiqueta do DigiBrain vira a 4ª linha da pilha da direita | **sim** | só a linha do agora: uma peça a menos, mas o DigiBrain fica escondido para quem não sabe que a linha abre |
| L1-7 | os números: o círculo de 232 px, a câmera a 12 células/s no WASD, o "seguir" a partir de 6 células, a transição de 400 ms | **PROPOSTO, SEM FONTE**, para ajustar depois, na mão | só vista; nenhum número de jogo |

### As decisões (o Matheus, 2026-11-06)

A prancha e as sete recomendações foram aprovadas ("Aprovado, seguir"): **L1-1** a ilha inteira, com a roda sobre o minimapa aproximando
até a janela em volta da câmera; **L1-2** o pet rosa com o anel claro; **L1-3** com a câmera "Fixa" o minimapa aparece, sem mover a
câmera; **L1-4** o cocô e o kit médico fora; **L1-5** Q/E, +/− e as setas e o Enter no minimapa; **L1-6** o DigiBrain como a 4ª linha da
pilha; **L1-7** os números como PROPOSTO, SEM FONTE.

## Lugares da ilha: menus (L2/L3) (2026-11-06, `ux-designer`; rodada 3)

Direção B, escolhida pelo Matheus em 2026-11-06: **cada menu é um lugar da ilha**. Abrir Crescer, Lutar ou Diário leva a câmera até o
lugar, o pet anda até lá e o painel aparece ancorado ao lado do objeto (no celular, numa folha que sobe da base), com a ilha visível e
viva em volta. Status: **PROPOSTO**. Só vista: o motor, o save, as rotas (`#/crescer/treinar` etc.) e o hash não mudam, e nenhum
número de jogo é criado (os níveis vêm do plano de progressão, abaixo). A prancha está em `docs/pranchas/ux-lugares-menus/`:
- `gerar.py` (o desktop; chama o `gerar_movel.py`, o celular, com os mesmos ajudantes), `lugares.css`, `movel.css`, `capturar.sh`;
- o antes em `img/antes/` e `antes_palavras.json`, medido pelo `medir_antes.mjs`;
- as capturas em `D:\Trab\digilab\capturas_ux_lugares_menus_aprovar\`: `<tela>_<1920|390|360>_<vidro|militar>.png`, e
  `<tela>_390_vidro_notas.png` (no celular, as notas só aparecem com `?notas`).

**O que o Matheus decidiu (2026-11-06).**
- Rodada 1: "ainda tem muito texto, principalmente em itens e evolução". Daí a **regra do texto**, abaixo.
- **O portão da arena e a barraca do Tamer entram na ilha 3D** como objetos low-poly CC0 do mesmo kit, nos pontos da prancha
  (DECIDIDO). Na prancha continuam como desenho provisório.
- **Os lugares têm trava de progresso**, com o nível do Tamer: o plano está DECIDIDO em `docs/PLANO_V3_PROGRESSAO_TUTORIAL.md` (branch
  `v3-progressao`, PR #634), com as P-1 a P-11 aceitas. A trilha e a vista dela estão abaixo, em "A trava de progresso".
- Rodada 3: "baseado nas alterações que foram propostas para todas as telas do desktop, vai ter que ser revisto para o mobile também".
  Daí "No celular", abaixo: cada tela do desktop tem a sua versão a 390, e o Itens também a 360.

**A regra do texto (vale para todas as abas, nas duas larguras).** À vista ficam só ícone, número e um rótulo de 1 a 3 palavras. Frase,
só no "Como funciona" fechado ou num balão no foco ou no hover (e no `aria-label`/`aria-describedby`, para o leitor de tela). A exceção
é o cartão de destrave, que tem uma frase de até 8 palavras (plano, 4.1). Os exemplos que saíram da vista: "último: Corrida · 07:31 · um
treino por vez, 10 min de intervalo" (fica "Pronto" e "Corrida 07:31"; o intervalo vai para o balão), "a campanha fica na Exploração",
"Nenhuma luta ainda. A primeira aparece aqui." (a linha some até haver luta), "abre a Exploração", "a câmera vai ao portão", os resumos
das linhas dos Ajustes, as etiquetas de tipo do Registro (viram ícone).

**Objetivo do jogador.** Ir fazer uma coisa num lugar ("vou treinar no saco") e ver de relance o que importa agora, sem ler.

**Os lugares.**

| menu | lugar | objeto | abas (ícones) | abre no (plano 3.3) |
|---|---|---|---|---|
| Diário | a barraca do Tamer | nova, junto ao barranco (DECIDIDO: entra na ilha 3D) | Registro, Catálogo, Gerações, Cenários | Nv 2, atendeu 3 chamados |
| Crescer | o saco de pancada | existe (o `CENA.treino` de hoje já leva o pet até ele) | Treinar, Aprendizado, Evolução, Itens | Nv 3, virou Rookie (o Itens no Nv 5) |
| Conversar | não é lugar | o ícone de hoje | — | Nv 3, virou Rookie |
| Lutar | o portão da arena | novo, no fim do caminho de terra (DECIDIDO: entra na ilha 3D) | Arena, Exploração, Fronteira, Medalhas | Nv 4, o primeiro treino (a Fronteira no Nv 8) |
| Ajustes | não é lugar | o leque do retrato (o nível do Tamer, Meus pets, DigiBrain, Ajustes) | uma lista só | sempre |

**Hierarquia, dentro do painel.** (1) O destaque, um por tela (borda `--hx-alerta`): "Pronto" no Treinar, o próximo item nos Itens, o
que o nível pede na Evolução, as lutas de treino na Arena, a próxima medalha, a semente no Registro, "3/19" no Catálogo. (2) A ação da
aba. (3) O que recua, em ícone e número. (4) O "Como funciona", fechado (aberto só no quadro do Registro).

**Sempre visível × por gesto.** Dentro de um lugar: o topo, o trilho (Pet, Crescer, Lutar, Diário, Conversar; Ajustes sai para o
retrato), o minimapa, a placa do lugar e o conector. Recolhem: a pilha, o dock e a linha do agora. Por gesto: o rótulo das abas
inativas, os balões, o "Como funciona", as listas fechadas, a ficha de uma forma. O atalho direto (PROPOSTO): `C`, `L`, `D` abrem com
corte seco; `1`–`4` trocam de aba; `Esc` volta; clicar ou `Esc` na viagem pula; "Viagem da câmera" nos Ajustes a desliga.

**A transição** (`transicao_1`, `_2`, `_3`, nas duas larguras): a ilha e o clique; a câmera a caminho com o pet andando; o painel ao
lado do saco (no celular, a folha subindo da base). Durações PROPOSTAS, SEM FONTE: câmera 700 ms; o painel em 180 ms (o "card entrando"
do guia, seção 11). Reduzir movimento: corte seco.

**A trava de progresso** (o plano decidido: `docs/PLANO_V3_PROGRESSAO_TUTORIAL.md`, P-1 a P-11).
- **O nível** é do Tamer (P-1) e é a quantidade de marcos (3.2, P-2). A trilha (3.3, P-3):
  - Nv 2, atendeu 3 chamados: o Diário;
  - Nv 3, virou Rookie: Crescer e Conversar;
  - Nv 4, o primeiro treino: Lutar;
  - Nv 5, a primeira medalha: o Itens;
  - Nv 6, virou Champion: as regras de luta e o Forçar (P-4: só esconder o editor e o cartão, sem tocar no motor);
  - Nv 8, 6 medalhas: a Fronteira.
- **Na tela** (P-8): "Tamer Nv N" no leque do retrato, e o cadeado com "Nv N" nos lugares.
- **Trancado** (3.4, P-11): o lugar fica visível na ilha desde o Nv 1, apagado, com o cadeado e "Nv N".
  - A dica (no foco ou no hover) e o `aria-label` dizem o marco: "Abre quando ele virar Rookie" (o exemplo da 3.4). Os outros textos de
    marco são da prancha, montados da coluna "marco" da 3.3: "Abre com 3 chamados atendidos", "Abre com o primeiro treino", "Abre com a
    primeira medalha", "Abre quando ele virar Champion", "Abre com 6 medalhas".
  - No trilho do desktop, o ícone fica igual, só apagado. Na coluna do celular, apagado e com o cadeado e o "Nv N" ao lado.
  - A tecla e a rota de um lugar trancado abrem o cartão do motivo, não o painel.
- **Destravado** (3.4, 4.1 e 4.2): o cadeado se abre na ilha e o lugar brilha uma vez em `--hx-alerta` (com reduzir movimento, sem
  brilho: só o cartão). Aparece o cartão de destrave: o ícone do lugar, o título de até 3 palavras, a frase de até 8 palavras (o texto da
  4.2) e **Ir** (a câmera vai ao lugar) e **Depois**. O Diário: `tent`, "Diário", "Veja o que ele fez e por quê." (4.2, linha do Nv 2).
- **`lugar_trancado`:** Tamer Nv 1, o pet é o Koromon (In-Training). A barraca mostra Nv 2, o saco Nv 3 e o portão Nv 4, apagados na
  ilha, no trilho e no minimapa; Conversar fica apagado no trilho. A dica do saco aparece aberta como demonstração. **`lugar_destravado`:**
  Tamer Nv 2 (o Koromon atendeu 3 chamados). A barraca abre, com o cadeado aberto e o brilho; o saco e o portão continuam trancados; e
  aparece o cartão.
- **O nível do save do antes** (o das outras telas: Growlmon Champion, o Tamer sem medalha), pela contagem de marcos: chocou (1), atendeu
  3 chamados (2; o histórico do antes diz "virou Agumon (cuidado 100%)"), virou Rookie (3), o primeiro treino (4; o save tem treino, "o
  seu pet tem 10"), virou Champion (5); a primeira medalha falta. **Tamer Nv 5.** Por isso:
  - o leque mostra "Tamer Nv 5";
  - as regras de luta (o cartão "Regras" na Arena) e o Forçar (no Treinar) aparecem trancados com "Nv 6";
  - a Fronteira (a aba em Lutar e o botão do minimapa) aparece com "Nv 8" e a dica "Abre com 6 medalhas";
  - o Itens (Nv 5) fica aberto pela contagem. Ver a pergunta 11: pelo marco (a primeira medalha), ele estaria trancado.

**No celular (390×844; o Itens também a 360×800).** Segue o mobile mínimo aprovado (#619, `docs/pranchas/ux-mobile/`):
- **o que vem do mínimo:** o retrato e a hora no canto de cima à esquerda; a coluna Conversar, Crescer, Lutar e Diário no canto de cima à
  direita; as quatro ações em círculos embaixo; o leque no retrato; nenhuma barra de abas.
- **O lugar:** tocar no ícone da coluna leva a câmera ao lugar, com a mesma viagem do desktop (com reduzir movimento, corte seco). Os 3
  quadros estão em `transicao_1_390` a `_3_390`.
  - O painel vira uma **folha que sobe da base e cobre só a parte de baixo**; em cima ficam o lugar e o pet. Isso substitui a faixa no
    topo da folha da rodada 2.
  - A folha tem a alça, o ícone e o nome do destino, o lugar (3 palavras) e o × "Fechar e voltar ao Pet"; embaixo vêm as abas em
    ícones e o corpo, que é o mesmo do desktop e rola. O Esc e o toque fora também fecham.
  - **A altura:** a folha começa em y 400 a 390×844 e em y 380 a 360×800. PROPOSTO, SEM FONTE.
- **As travas:** os ícones da coluna mostram o cadeado com "Nv N" ao lado quando o lugar está trancado; o cartão de destrave aparece no
  alto da tela; o "Tamer Nv N" fica no leque do retrato.
- **O minimapa** (a L1 é só do desktop): no celular vira o botão **Mapa** no leque do retrato, que abre o mapa por cima, com os lugares
  tocáveis e a Fronteira trancada. Nenhum círculo fixo na tela (tela `mapa_390`). A alternativa é a pergunta 12.
- **Ajustes:** sobe como folha sobre a ilha de sempre, sem viagem; o leque se fecha quando ela abre.

```
390×844, Crescer · Itens
┌──────────────────────────────────────┐
│ (◉)[D3 07:42]                   [Con]│  o retrato, a hora; a coluna (48 px)
│                                 [Cre]│  a atual em destaque
│        ┌┐                       [Lut]│
│        ││ saco         (Growlmon)[Diá]│  o lugar e o pet, no terço de cima
│        ██                            │  (Nv N + cadeado ao lado do ícone, se trancado)
│       ═══                            │
├────────────────────────────────────── ┤  y 400: a folha sobe da base (PROPOSTO, SEM FONTE)
│               ────                   │  a alça
│ ▦ CRESCER  saco de pancada       [×] │  "Fechar e voltar ao Pet", Esc, toque fora
│ [tr][ap][ev][▦ ITENS]                │  as abas em ícones
│ ▦ 0 chips ▭ 0 cartas △ 10/11 (c1)(c3)(c5)│
│ ┃Força  ┊ ┊Guarda ┊ ┊Recuo  ┊          │  o corpo do desktop, que rola
│ ┊Oport. ┊ ┊Persegu┊ ┊Aparo  ┊          │
└──────────────────────────────────────┘

390×844, o leque do retrato com o mapa
┌──────────────────────────────────────┐
│ (◉)[D3 07:42]                   [Con]│
│ [Tamer Nv 5]                    [Cre]│  P-8
│ [ali 64 ene 81 hig 40 hum 72 saú 95] │  os vitais (o Estado atual)
│ [Evo] ┌────────── Mapa ───── [×] ┐   │
│ [Últ] │   ( círculo da ilha )     │   │  os lugares tocáveis; a Fronteira Nv 8
│ [Dgb] │   [saco] [portão] [barraca]   │
│ [Map]◀│                           │   │  o botão novo no leque
│ [Cfg] └───────────────────────────┘   │
│ [Pets]                               │
│       (Ali)  (Bri)  (Lim)  (⋯)       │  as ações
└──────────────────────────────────────┘
```

**As telas.**

| tela | 1920 | 390 | o que mostra |
|---|---|---|---|
| `transicao_1`, `_2`, `_3` | sim | sim | a viagem até o saco |
| `crescer_treinar` | sim | sim | "Pronto", os 6 exercícios, a fadiga e a sobrecarga em número; o Forçar trancado (Nv 6) |
| `crescer_itens` | sim | sim, e a 360 | cada item como ícone, nome curto e efeito em 2 a 4 palavras; tracejado e cadeado = ainda não é seu; as vagas como três encaixes trancados (1, 3, 5 medalhas, `CIT.vagas`); "treino 10/11" |
| `crescer_evolucao` | sim | sim | a forma, "15h 15min até Ultimate", os 3 selos apagados e "0/10 lutas", a árvore só da linha do pet |
| `lutar_arena`, `lutar_medalhas` | sim | sim | as lutas de treino em destaque; as Regras trancadas (Nv 6); a Fronteira com Nv 8 |
| `diario_registro`, `diario_catalogo` | sim | sim | a regra aplicada (o Registro com o "Como funciona" aberto) |
| `ajustes` | sim | sim | a lista só com ícone e nome; "Tamer Nv 5" no leque (desktop) |
| `mapa` | — | sim | o leque do retrato com "Tamer Nv 5" e o Mapa aberto |
| `lugar_trancado`, `lugar_destravado` | sim | sim | a trava (acima) |
| `antes_depois_itens`, `antes_depois_evolucao` | sim | sim (`_390`) | o jogo de hoje ao lado do depois, com a contagem |

**As contagens de palavras** (o `innerText` do painel inteiro, com a regex `/[\p{L}\p{N}]+(?:[-'’][\p{L}\p{N}]+)*/gu`; o antes no
`antes_palavras.json`, com o que só aparece rolando; o depois contado na própria página; o balão, o "Como funciona" fechado e a dica fora
do foco não entram, porque não estão à vista). A rodada 2, medida nas etiquetas da captura:

| tela | antes | depois (rodada 2, medido) | o que foi para o balão ou para o "Como funciona" |
|---|---|---|---|
| Itens, 1920 | 455 | **61** | o parágrafo "Os itens são seus…", a regra das vagas, o "Agora os itens não fazem efeito…", o efeito inteiro de cada item, o "Ainda não é seu: vença X em Y", a regra completa do chip de regra, o "Este chip fica coberto…", o "Nenhuma agora. Vem da revanche…" |
| Itens, 390 | 455 | **61** (rodada 2: 58; a folha de baixo da rodada 3) | o mesmo |
| Evolução, 1920 | 235 | **30** | "Faltam 3 medalhas: …" (o lugar vai ao balão de cada selo), "0 vitórias / experiência de combate…", "nenhuma luta / vitórias nas lutas deste estágio…", "se evoluísse agora…", "Toque num nó…", a legenda da árvore, os eixos e os arquétipos dos nós, "Por que Growlmon?", o histórico, as duas frases do pé |
| Evolução, 390 | 235 | **30** (rodada 3) | o mesmo |
| Treinar, Arena, Medalhas, Registro, Catálogo, Ajustes | não medido | ~54, ~42, ~37, ~87 (35 do "Como funciona" aberto), ~23, ~18 (estimativas) | os resumos, as frases de apoio e as regras longas |

A rodada 3 trocou a faixa da folha a 390 pela folha de baixo e pôs "Nv 6" e "Nv 8" em Arena e em Treinar; os números a 390 da tabela
são os das etiquetas da rodada 3 (lidos das páginas `antes_depois_*` em 2026-11-06).

**Tokens.** Só os das peles atuais (cópia de `src/estilo/tokens.css`): `--hx-chao`, `--hx-miolo`, `--hx-miolo-2`, `--hx-borda`,
`--hx-borda-topo`, `--hx-texto`, `--hx-texto-2`, `--hx-sec`, `--hx-rotulo`, `--hx-escolhido` (`-ink`, `-borda`, `-brilho`),
`--hx-hachura`, `--hx-btn-bg`/`-ink`/`-borda`, `--hx-medidor`, `--hx-medidor-trilho`, `--hx-medidor-alt`, `--hx-mascara`,
`--hx-alerta` (o destaque, o brilho do destrave, o cartão e o "Tamer Nv N"), `--hx-ok`, `--hx-aprendido`, `--hx-foco`, `--hx-f`,
`--hx-f-num`, `--hx-num`, `--hx-vidro`, `--hx-reflexo`, `--hx-luz`, `--hx-sombra`, `--hx-tecla`, `--hx-tecla-hover`, `--hud-fundo-1`,
`--hud-fundo-2`, `--hud-desfoque`, `--hud-ch`, `--hud-ch-p`, `--hud-brilho`, `--hud-risca`.
- **Nada de novo em cor:** nenhum `--dl-*` e nenhuma cor hex nova.
- **Literais:** a sombra `rgba(0,0,0,.4)` (B3), o fundo da marca (`casca.css`) e a nota amarela (B3, também nas etiquetas de contagem).
- **O trancado** usa `filter: grayscale`, que não é cor; o saco apagado é um recorte do próprio fundo, apagado.
- **Os objetos novos** são trechos do próprio fundo. Fontes: as das peles.

**Wireframe a 1920×950** (Crescer · Itens):

```
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│ [◉ Growlmon Champion]                         DIGILAB                    [Dia 3 07:42 ● salvo]│
│ ┌────┐                          ┌ Crescer · saco de pancada ───────────────── [×] ┐          │
│ │Pet │      [SACO DE PANCADA]   │ [tr][ap][ev][▦ ITENS]                           │          │
│ │Cre◀│            │             │ ▦ 0 chips  ▭ 0 cartas  △ treino 10/11  (c1)(c3)(c5) vagas│
│ │Lut │           ┌┴┐  ─ ─ ─ ─ ─ ┤ CHIPS                                           │          │
│ │Diá │           │█│            │ ┃Força      ┊ ┊Guarda     ┊ ┊Recuo  Champion  ┊│ ilha viva│
│ │Con │  (Growlmon│█│            │ ┃+1 força   ┊ ┊+1 guarda  ┊ ┊pesado → recuar ┊│          │
│ └────┘   no saco) │            │ ┊Oportunista┊ ┊Perseguidor┊ ┊Aparo  Ultimate ┊│          │
│                  ═╧═           │ CARTAS  ┊Fôlego ×0┊ ┊Cura ×0┊ ┊Foco ×0┊          │ (minimapa)│
│                                 │ ▸ Como funciona                                 │          │
│                                 └─────────────────────────────────────────────────┘          │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
```
(`(c1)` = o encaixe trancado, com o cadeado de traço e o nº de medalhas que o abre; `┊` = tracejado, ainda não é seu; `┃` = o destaque)

**O que muda na leitura do estado do pet.**
- O que importa vem primeiro e é o único destaque da tela; o resto se lê por ícone e número, e as frases ficam a um foco de distância.
- **Nos Itens,** o estado de cada item (tem ou não tem; vaga livre, ocupada ou trancada) é forma (sólido, tracejado, cadeado), não frase.
- **Na Evolução,** o que o nível pede são três selos e um número, e a árvore mostra só o caminho do pet.
- **A trava** diz onde o jogador está na jornada: o "Tamer Nv N" e o cadeado com o nível de cada lugar, e o marco na dica.
- Nenhum dado novo: cada número e texto vem do motor, da tela de hoje ou do plano de progressão (tabela abaixo).

**Custo em determinismo e em e2e.**
- **Determinismo: nenhum.** É só vista: a câmera, o pet andando, a trava, o cartão e a dica não entram no registro. A trava é a opção V
  do plano (P-5): uma função pura do registro do Tamer e dos pets. Com o mundo físico ligado, o pet que anda é só a vista e volta à
  posição do motor ao sair.
- **e2e:** as rotas ficam, mas os seletores por texto quebram: as abas viram ícones com `aria-label`, os textos de apoio saem da vista e
  as etiquetas do Registro viram ícones.
  - A viagem precisa de um modo sem animação nos testes.
  - Os testes que procuram frases ("Ainda não é seu", "Faltam 3 medalhas", "Nenhuma luta ainda") passam a procurar o `aria-label` ou o
    balão.
  - A trava pede o e2e do lugar trancado (o plano, seção 6).
  - No celular, a folha muda de forma (de modal cheio para folha de baixo), e os testes de foco da folha mudam com ela.
- Os efeitos curtos dos itens são texto novo de tela (um mapa na tela, não no `itens.ts`).

**Número ou texto → fonte.**

| na tela | fonte |
|---|---|
| Growlmon, Koromon, Agumon, Guilmon, Greymon, Kyubimon, Birdramon, MetalGreymon…; os níveis | `motor/nomes.ts` (`DIGIMON_DA_FORMA`, `NOME_EST`, `NOME_ARQ`) |
| os 6 chips e as 3 cartas, o efeito (inteiro no balão) | `motor/itens.ts` (`ITENS`) |
| de onde vem cada item | `itens.ts` (`ITEM_DA_MEDALHA`, `CARTA_DA_REVANCHE`); `TelaItens.tsx` (`deOnde`), `tamer.ts` (`comoGanhar`) |
| Champion/Ultimate no chip de regra | `TelaItens.tsx` ("pede um …", `estagioMinimo`) |
| vagas 1/3/5 | `constantes.ts` `CIT.vagas`; `itens.ts` `vagasDeChip` |
| +20 guts; 30% → +20% | `CIT.gutsFolego`, `CIT.curaAbaixo`, `CIT.curaFracao` |
| "treino 10/11" | `porqueItensNaoValem` do save (o texto do antes); `CIT_V9.treinoMinimo` × `CIT.tipico` |
| 3 medalhas para o Ultimate; Campina, Torre de pedra, Floresta | `CMD.adulto`; `tamer.ts` `medalhasQueFaltam`; `medalhas.ts` |
| 0/10 lutas; 80% | `CAT.sparring`, `CLE.limiarTaxa`; `luta.ts` `sparringTexto` |
| +2 x +1 y; a estrela da aptidão em Levantar pedra e Esquiva | `CTR`; `APTIDAO.brasa` |
| marcas 40/60 e 30/60 | `CTR.limiarPausa`, `CTR.limiteForcar`, `CSO.aviso`, `CSO.sombrio` |
| "5 regras" (Champion) | o "Como funciona" da Arena; no jogo, `m.gp.ativas.length` |
| os rivais e os estilos | `luta.ts`, `nomesRivais.ts` (`DIGIMON_BOT`), `bots.ts` (`NOME_BOT`) |
| as medalhas, os líderes, a regra, o item, o que libera | `medalhas.ts`, `bots.ts`, `arenas.ts`, `itens.ts`, `TelaMedalhas.tsx` |
| Nv 2, 3, 4, 5, 6 e 8 de cada lugar e peça; o marco de cada um | `docs/PLANO_V3_PROGRESSAO_TUTORIAL.md`, seção 3.3 (a tabela, uma linha por nível) |
| "Abre quando ele virar Rookie" | o plano, 3.4 (os outros textos de marco: a prancha, da coluna "marco" da 3.3) |
| "Tamer Nv 5" | o plano, 3.2 e P-8; a conta dos marcos do save (acima) |
| o cartão do Diário: `tent`, "Diário", "Veja o que ele fez e por quê.", Ir e Depois | o plano, 4.1 (tipo A) e 4.2 (linha do Nv 2) |
| a Fronteira "Nv 8 · Abre com 6 medalhas" | o plano, 3.3 (linha 8); `MapaExploracao.tsx`; `liga.ts` (`MEDALHAS_LIGA`) |
| as linhas do registro | `motor.ts` (`_hist`), `NOME_PET`, `TelaRegistro.tsx` |
| 19 formas, 3/19 | `TelaCatalogo.tsx` (`formasDoBrasao`) |
| a lista dos Ajustes; "Mostrar dicas" | `TelaConfig.tsx` |
| os vitais no leque do celular (64, 81, 40, 72, 95) | o mínimo (#619): os cinco vitais do Estado atual (`TelaPet.tsx`); os números são exemplo |
| **exemplo, nunca dado** | Dia 3, 07:42, 07:31, 15h 15min, fadiga 20, estágio 10/12, semente 7000, 76 eventos, as horas do registro, o rival escolhido, os vitais |
| **novo, de tela (PROPOSTO)** | "Portão da arena", "Barraca do Tamer", os efeitos curtos dos itens, os textos de marco que não estão na 3.4, "Viagem da câmera", o botão Mapa, as teclas, as durações, a altura da folha |

**Perguntas abertas ao Matheus** (a do portão e da barraca foi aprovada, e a da trava virou o plano decidido: saíram da lista).
1. **As teclas do atalho direto:** `C`/`L`/`D`, `1`–`4` nas abas e `Esc`? Recomendo as letras. Custo baixo (só fora de campo de texto).
2. **A Fronteira vira lugar próprio ou continua aba trancada?** Recomendo aba por agora (Nv 8). Custo baixo.
3. **O pet andando com o mundo físico ligado:** a vista anda e volta ao sair, como o `CENA.treino`? Recomendo que sim. Custo: vista e
   motor divergindo sem aviso.
4. **Câmera 700 ms (SEM FONTE) e painel 180 ms (do guia)?** Custo: viagem longa irrita; o atalho e a "Viagem da câmera" cobrem.
5. **Um `--hx-sombrio` nas duas peles** (o roxo era `--dl-dark`): recomendo criar, com o contraste conferido. Sem ele, a sobrecarga e
   a forma sombria ficam sem a cor própria (na prancha, a sombria da árvore é o listrado `--hx-hachura`).
6. **Abas só em ícone, com o rótulo na ativa e na dica:** recomendo manter. Custo: quem não reconhece o ícone precisa do foco ou do hover.
7. **As duas contas de medalha do save não batem.**
   - O pet sabe de 1 (evento "u", `m.medalhas`): é a conta que o motor usa na trava da evolução e nas vagas.
   - O Tamer tem 0 (`tamer.ts`): é dele que sai a lista do que falta.
   - O jogo de hoje mostra as duas lado a lado ("1 de 3" e "Faltam 3"). A prancha desenha só a do Tamer.
   - Recomendo uma conta só na tela, a do Tamer, e conferir o save: um Champion v6 precisa de 1 medalha, então o Tamer do save deveria ter
     a da Campina.
   - Custo de errar: a tela diz "1 de 3" e "faltam 3" ao mesmo tempo, como hoje.
8. **As lutas de treino ficaram na Evolução** como "0/10 lutas", com o 80% no balão. Recomendo manter (é o que mais demora). Custo de
   tirar: o jogador vê o tempo e as medalhas e não sabe que faltam lutas.
9. **No Catálogo, só as formas vistas mostram o nome;** as outras, a silhueta, com o nome no balão. Recomendo assim. Custo: quem quer o
   nome de todas precisa passar por cada uma.
10. **Os efeitos curtos dos itens** ("pesado → recuar", "guts < 20 → pesado", "não se distrai") são texto novo. Recomendo um mapa na tela
    (`TelaItens.tsx`), sem mexer no motor. Custo de errar: um resumo que diga menos do que a regra; a frase inteira continua no balão.
11. **(nova) A trava é pela contagem de marcos ou marco a marco?**
    - No save do antes, o pet já é Champion (o marco do Nv 6), mas a primeira medalha (o marco do Nv 5) falta: 5 marcos, Nv 5.
    - Pela contagem, o Itens (Nv 5) abre e as Regras e o Forçar (Nv 6) ficam trancados com "Abre quando ele virar Champion", num pet que
      já é Champion.
    - Marco a marco, seria o contrário: o Itens trancado e as Regras abertas.
    - Recomendo que cada peça abra pelo seu próprio marco (a vista nunca abre antes do motor, plano 3.3) e que o número do Tamer seja a
      contagem. Num save coerente (o Tamer com a medalha da Campina), as duas leituras dão o Nv 6 e tudo aberto.
    - A prancha seguiu a contagem, como pedido, e não mudou a tela de Itens.
    - Custo de errar: o jogador vê um cadeado que pede o que ele já fez.
12. **(nova) O minimapa no celular:** o botão **Mapa** no leque do retrato (recomendado; tela `mapa_390`), ou mais um ícone na coluna de
    cima, que abre o mesmo mapa por cima?
    - Recomendo o leque: a coluna fica com os quatro destinos do mínimo, e o mapa é consulta, não destino.
    - Custo de errar: no leque, o mapa fica a dois toques; na coluna, a coluna cresce para cinco ícones e ocupa mais do canto da cena.
13. **(nova) A altura da folha no celular:** de y 400 para baixo a 390×844 (e de y 380 a 360×800), uns 53% da tela, PROPOSTO, SEM
    FONTE.
    - Recomendo essa altura, com a folha rolando por dentro e um gesto de puxar a alça para cima para ver tudo.
    - Custo de errar: mais alta, esconde o lugar e o pet (perde a direção); mais baixa, o corpo das abas cabe pouco e quase tudo rola.

---

## DigiBrain scan (D1) — o painel do cérebro A como "scan holográfico" (2026-11-07)

**A direção é a A, "scan holográfico"**, escolhida pelo Matheus em 2026-11-07 na prancha de direção
(`D:\Trab\digilab\capturas_digibrain_direcao.html`): o cérebro em malha numa moldura de scanner, sobre uma grade, com as leituras nos dois
lados. O que ele já decidiu e não se reabre aqui: a paleta da pele Vidro (e a prancha funcionando na Militar); a silhueta de cérebro honesta
com o dado (cada ponto um nó do motor, cada fio uma aresta, nenhum enfeite que pareça nó, o rótulo "mapa dos pesos"); a varredura só numa
decisão; o pulso entrada → regra → ação; o giro lento da câmera como vista; tudo parado com "reduzir movimento"; no desktop em tela cheia por
cima da ilha (o "modo scan", com Fechar e Esc); no celular a folha inteira. **O `DigiBrainLab` (o cérebro modular) fica fora** desta etapa.

Esta seção é o plano e a prancha juntos, porque a direção já foi aprovada; **o código só depois do ok do Matheus à prancha**.

### O objetivo do jogador

Ver **por que o pet fez o que fez agora** e **o que ele já aprendeu com você**, num desenho que dá vontade de abrir: a decisão acende um
caminho de verdade (a entrada, a regra, a ação) no meio dos pesos dele. Hoje isso mora numa coluna de 296 px com um mapa de 284 unidades;
o scan dá ao mapa a tela inteira, sem acrescentar nenhum dado.

### A hierarquia

1. **O mapa dos pesos**, no centro, na moldura do scanner: a decisão acesa (a regra, as candidatas com a chance, a ação escolhida, as três
   entradas que mais pesaram e os fios dela) sobre todos os pesos do pet, e a região que "pesou mais".
2. **O agora**, no alto da coluna esquerda: a regra e a ação, e a frase "quem decidiu" (só uma opção / o instinto faria o mesmo / sem o
   aprendido teria decidido X, com a marca do aprendido).
3. **As opções e a chance**, no alto da coluna direita, a escolhida com o "escolhido" da pele.
4. **O peso de cada lobo** e **o que mais pesou** (esquerda); **o que aprendeu desde que nasceu** e **as últimas ações** (direita).
5. O topo: o título, o selo (ao vivo, pausado, replay) e o Fechar com o Esc.

### Sempre visível, só quando existe, por gesto

| peça | quando | de onde vem (o motor) |
|---|---|---|
| o título "DigiBrain · mapa dos pesos", o selo e o Fechar | sempre | o selo é `estadoSelo` (`src/seloDigiBrain.ts`), do app |
| a moldura com o mapa, a contagem ("29 pontos · 77 pesos"), a legenda e a nota honesta | sempre | `ENTRADAS_LOBOS`, `REGRAS_LOBOS`, `ACOES_LOBOS` (`motor/lobos.ts:34-43`), `mapa.receptores` e `mapa.arestas.length` (`Motor.digibrain`, `motor/motor.ts:319`) |
| o agora | sempre; sem decisão, "Ainda não decidiu nada." | `decisao.regra`, `.acao`, `.quem_decidiu` (`leituraDecisao`, `motor/digibrain.ts:14-35`) |
| o peso de cada lobo (com a emoção de hoje), o que mais pesou, as opções | só com uma decisão (como hoje) | `decisao.barras`, `.percepcao`, `.chances`; a emoção é a última de `pol.mem.emocoes` (`DigiBrain.tsx:65`) |
| o que aprendeu | sempre; vazio, "Ainda igual ao instinto." | `aprendido` (`leituraAprendido`, `motor/digibrain.ts:87`) |
| as últimas ações | sempre; vazio, "Nenhuma ação ainda." (texto novo; hoje a lista vazia não diz nada) | `m.historico`, `quem = pet`, as 5 últimas (`DigiBrain.tsx:74`), com `hhmm(t)` |
| a decisão acesa no mapa | só com `mapa.acesas` | `mapaDecisao` (`motor/digibrain.ts:101`): as arestas, a `forca`, o `lobo_decisivo` |
| a varredura e o pulso | **só numa decisão nova** (`mapa.acesas.n` mudou), com o selo "ao vivo" e sem "reduzir movimento" | nenhum dado novo: é o mesmo `acesas` |
| o giro lento da câmera | enquanto o scan está aberto, sem "reduzir movimento" (D1-3, D1-4) | nenhum: é vista |
| **o mapa em texto** | por gesto: o botão "O mapa em texto" | o mesmo `mapa`: a lista das acesas (a favor/contra e a força) e a tabela dos pesos (regra, ação, entrada, `w`, `w0`, a marca) |
| fechar | o botão "Fechar DigiBrain", o <kbd>Esc</kbd>; no celular, o × | — |

**"Últimas ações" ficou num ladrilho**, embaixo na coluna da direita (desktop) e por último na folha (celular), como no painel de hoje.

### O desenho: a silhueta honesta

- **Os pontos são os nós do motor, e só eles:** as 10 entradas de `ENTRADAS_LOBOS` e os receptores de `mapa.receptores` (5 no save do
  e2e: tédio, solidão, estresse, dor, susto, com o anel verde do corpo, como o `mp-corpo` de hoje), as 7 regras e as 7 ações. São 29 pontos
  no save do e2e. Nenhum ponto é enfeite.
- **Os fios são as arestas de `mapa.arestas`, e só elas,** cada uma da entrada à ação **passando pela regra** (CN-2), com a espessura
  `0,4 + 1,4·espessura` do `MapaPesos` (a `espessura` é √|w|/S, CN-3), a cor do aprendido de hoje (cinza onde `aprendido = 0`, `--mp-mais`
  acima, `--mp-menos` abaixo, mais forte quanto maior) e o tracejado no peso negativo.
- **A decisão acesa** é a de hoje: os fios de `mapa.acesas.arestas` na cor de "esta decisão" (`--mp-aceso`) com a espessura pela `forca`
  (o termo negativo tracejado), o resto dos pesos a 35 %; a regra que disparou, as três entradas de `decisao.percepcao`, as candidatas (com
  a chance) e a escolhida acesas; a região do `lobo_decisivo` com a caixa "pesou mais".
- **A forma de cérebro é só o desenho:** a silhueta (o hemisfério e o cerebelo; o tronco saiu depois do ok, porque os traços dele não eram nó nem peso) é preenchida por uma trama fina da malha, que não
  se lê como fio, e quatro rótulos de região, todos fora dos nós: **decisão** na frente (as ações, de cima para baixo na ordem de
  `ACOES_LOBOS`), **impulsos** no meio (as regras na ordem em que o instinto as testa), **percepção** atrás (as entradas num arco, na ordem do
  motor, com os receptores do corpo no fim, embaixo, sobre o cerebelo) e **memória e emoção · sem pesos** embaixo, **sem nenhum ponto**,
  porque o lobo não tem pesos (é o "memória e emoção: sem pesos" de hoje).
- **A nota fixa embaixo do mapa:** "Cada ponto é uma entrada, uma regra ou uma ação do pet; cada fio é um peso, da entrada à ação, passando
  pela regra. A espessura é o tamanho do peso. A forma de cérebro e as regiões são só o desenho."
- **Nenhum texto diz** "neurônio", "pensando", "sentindo", "conectoma" ou "connectome" (o e2e de hoje procura os quatro últimos).

### O movimento (descrito; a prancha é o quadro parado)

- **A varredura:** uma faixa horizontal da cor da malha desce a moldura uma vez quando chega uma decisão nova (`mapa.acesas.n` maior que a
  última vista pela tela). Sem decisão nova, nada passa. No replay, no pausado e sem decisão, não passa.
- **O pulso:** junto da varredura, um ponto claro (`--hx-foco`) corre ao mesmo tempo em cada fio aceso, da entrada até a regra e da regra até
  a ação, e para. É o mesmo caminho que fica aceso; não há ponto fora de um fio.
- **O destaque:** troca de uma vez (sem transição) quando a decisão muda, como hoje.
- **O giro lento:** a vista balança devagar em volta do eixo vertical, como uma câmera em volta do scan. É só vista (D1-3, D1-4).
- **"Reduzir movimento"** (`prefers-reduced-motion` ou o ajuste do jogo): sem varredura, sem pulso, sem giro; só o destaque troca.
- **Os números do movimento não estão decididos:** a duração da varredura e do pulso, a amplitude e o ciclo do giro vão como pergunta
  (D1-2), PROPOSTO, SEM FONTE. Nada pisca em loop (guia 11).

### As cores pelos tokens

Nenhuma cor hex nova. A prancha copia os tokens do app com a linha de origem (`digibrain.css` da prancha, cabeçalho).

| peça | token |
|---|---|
| o fundo do modo scan | `--hx-chao` com `--hx-vidro` (no Vidro a ilha transparece; na Militar é opaco) |
| a malha da silhueta, os cantos da moldura, a varredura | `--hx-medidor` (Vidro `#5FD4FF`, o ciano da direção; Militar `#AEB9A6`), apelidado **`--scan-malha`** |
| a grade da moldura | `--hx-medidor-trilho`, apelidado **`--scan-grade`** |
| as divisas e os rótulos das regiões | `--hx-borda` tracejado; `--hx-rotulo` |
| o fio do instinto | `--hx-sec` a 45 %, apelidado **`--scan-prior`** (hoje `--dl-muted`) |
| o aprendeu a mais, a menos, esta decisão | `--mp-mais`, `--mp-menos`, `--mp-aceso` (os literais de hoje, `src/estilo/digibrain.css:48`) |
| os pontos | o miolo `--hx-miolo` com o anel `--scan-malha`; o receptor do corpo com o anel `--hx-ok`; aceso e escolhida em `--mp-aceso`, a escolhida com o anel `--hx-foco`; a candidata com o anel `--hx-texto` |
| o pulso | `--hx-foco` |
| "pesou mais" | a caixa `--hud-fundo-2` com o contorno `--hx-foco` |
| os ladrilhos | a caixa da HUD (`--hud-fundo-1`/`-2`, `--hx-borda`, `--hud-brilho`, `--xcom-cantos`) |
| as barras dos lobos | impulsos `--hx-alerta` (o amarelo de hoje), aprendido `--hx-aprendido`, corpo `--hx-ok`, memória e emoção e piso `--hx-sec`; o trilho `--hx-medidor-trilho`, o eixo no zero `--hx-sec` |
| a opção escolhida | `--hx-escolhido` / `--hx-escolhido-ink`; a barra em `--mp-aceso` (a mesma cor do mapa) |
| a marca do aprendido (o agora que mudou, o ladrilho "o que aprendeu") | `--hx-aprendido` tracejado (guia 3) |
| a favor / contra | `--hx-ok` / `--hx-sec`, com a palavra |
| o selo | ao vivo: ponto `--hx-ok`; pausado: duas barras `--hx-sec`; replay: triângulo `--hx-rotulo` (a forma também diz) |
| os números | `--hx-f-num`, `--hx-num` |
| o Fechar e "O mapa em texto" | `--hx-btn-bg`, `--hx-btn-ink`, `--hx-btn-borda`; a tecla `--hx-tecla` |
| o foco | `outline: 2px solid var(--hx-foco)` |

**Os tokens PROPOSTOS** (só apelidos, nenhum valor novo; entram em `tokens.css` se o Matheus quiser o nome, ou ficam locais no CSS do
DigiBrain):
- `--scan-malha` = `var(--hx-medidor)` nas duas peles (o ciano `#5FD4FF` no Vidro). **Não** é o `--hx-aprendido` (`#6FE3FF`): o ciano do
  aprendido continua reservado à marca do aprendido (guia 3), e a malha usa o ciano do medidor da pele, que é o da moldura do Vidro;
- `--scan-grade` = `var(--hx-medidor-trilho)`;
- `--scan-prior` = `var(--hx-sec)`.

### Wireframes

Uma coluna vale ~20 px a 1920 e ~10 px a 390. Os números são os do estado `com_escolha` do `dados.json`.

```
1920×950, o modo scan por cima da ilha (com_escolha, ao vivo, logo depois da decisão)
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│ DigiBrain MAPA DOS PESOS   ● ao vivo                                              [× Esc]    │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│┌ AGORA ─────────────┐ ┌[MAPA DOS PESOS 29 pontos · 77 pesos]────────────┐ ┌ AS OPÇÕES ───────┐│
││Tempo livre: decidiu│ │   DECISÃO        IMPULSOS             PERCEPÇÃO   │ │à toa   ▮▮▯  27%  ││
││chamar você         │ │        ╭───────── pesou mais ──╮  ● viés         │ │explorar▮▮▯  27%  ││
││O instinto sozinho  │ │  à toa ◉ ╲     ● exausto       ╲ ● comida        │ │brincar ▮▮▮  37%  ││
││faria o mesmo.      │ │  dormir ●  ╲   ● sono          ╱ ◉ higiene       │ │█chamar você ·esc█││
│├ O PESO DE CADA LOBO┤ │   comer ●   ╲  ● noite        ╱  ● energia       │ └──────────────────┘│
││Impulsos   |▮▮▮ 105%│ │ brincar ◉ ══╪══● precisando  ╱   ● humor         │ ┌┄ O QUE APRENDEU ┄┐│
││Aprendido ▮|   −3,3%│ │ chamar  ◉═══╪══● sem cuidado     ● saúde         │ ┆mais explorar +0,28┆│
││Corpo     ▮|   −1,6%│ │  você 9%    ╲══◉ tempo livre ════◉ hora          │ ┆menos chamar −0,05 ┆│
││Memória e  |    0,0%│ │ explorar ◉  ═══ varredura (parada) ════════      │ ┆menos à toa  −0,05 ┆│
││emoção de hoje:     │ │ emburrar ●                       ◉ tédio ○ corpo │ └┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┘│
││alegria · memória   │ │        MEMÓRIA E EMOÇÃO · SEM PESOS  RECEPT. DO CORPO│ ┌ ÚLTIMAS AÇÕES ───┐│
│├ O QUE MAIS PESOU ──┤ └─────────────────────────────────────────────────┘ │20:45 chamando você││
││[hora do dia 86%    │  ─ instinto ─ a mais ─ a menos ━ esta decisão ┄ neg ○ │20:30 brincando    ││
││ contra][tédio 45%  │  Cada ponto é uma entrada, uma regra ou uma ação…     │20:15 explorando   ││
││ contra][higiene 48%│  A forma de cérebro e as regiões são só o desenho.    │20:00 brincando    ││
││ a favor]           │                               [≡ O mapa em texto]     │19:15 chamando você││
│└────────────────────┘                                                       └───────────────────┘│
└──────────────────────────────────────────────────────────────────────────────────────────────┘
  ◉ aceso/candidata · ● ponto · ═ fio aceso · ─ fios do instinto e do aprendido a 35 %

390×844, a folha inteira (com_escolha); a folha rola (a ordem é a do painel de hoje)
┌──────────────────────────────────────┐
│ DigiBrain   ● ao vivo          [ × ] │
├──────────────────────────────────────┤
│┌ AGORA ─────────────────────────────┐│
││Tempo livre: decidiu chamar você    ││
││O instinto sozinho faria o mesmo.   ││
│└────────────────────────────────────┘│
│┌[MAPA DOS PESOS 29 pontos · 77 pesos]┐│
││ DECISÃO   IMPULSOS     PERCEPÇÃO   ││
││  ◉ à toa 27%   ◉ tempo     ◉ hora  ││
││  ◉ brincar 37% livre       ◉ tédio ││
││  ◉ chamar você 9%          ◉ higiene││
││  ◉ explorar 27%   (só os rótulos   ││
││        acesos; o resto, no texto)  ││
│└────────────────────────────────────┘│
│ ─ instinto ─ a mais ─ a menos ━ esta │
│ Cada ponto é uma entrada, uma regra… │
│ [≡ O mapa em texto]                  │
│┌ O PESO DE CADA LOBO NESTA ESCOLHA ─┐│
││Impulsos     |▮▮▮▮▮  105%           ││
││…                                   ││
   (rola: o que mais pesou, as opções, o que aprendeu, as últimas ações)
```

**O mudou** (`mudou`, "o pet v11 com o aprendido"): o agora ganha a marca do aprendido (a borda tracejada `--hx-aprendido`, a etiqueta
"aprendido" e "Sem o aprendido, teria decidido chamar você."), a barra do aprendido cresce (+61,8 %) e a região **decisão** fica com o
"pesou mais" (`lobo_decisivo = decisao`). **O uma_opcao:** um fio aceso só (o viés de "sono" para "dormir"), "Nesta situação só havia uma
opção." e "Nada do que ele lê pesou nesta regra.". **O sem_decisao:** os 14 fios do instinto, nada aceso, sem varredura; à esquerda só o
agora. **O replay:** o `com_escolha` com o selo "replay" e sem a varredura e o pulso.

### O que muda na leitura do estado do pet

**Nada no que se lê.** A tela continua lendo só `Motor.digibrain()` (a decisão, o aprendido e o mapa), o histórico e a memória das emoções,
como o painel de hoje (`DigiBrain.tsx`, `MapaPesos.tsx`). Muda a apresentação:
- o mapa ganha a tela inteira e vira a peça principal; as colunas fixas viram a silhueta (as posições são só desenho, a ordem dos nós é a
  do motor);
- **a contagem** ("29 pontos · 77 pesos") sai do `aria-label` de hoje para a tela;
- **as barras dos lobos ganham o eixo no zero** (o positivo à direita, o negativo à esquerda) no lugar do rosa de hoje no negativo (D1-5);
- **"pesou mais"** passa da caixa da região de hoje para uma caixa no rótulo da região;
- **o mapa em texto** é novo: a mesma leitura em lista e tabela, para quem não lê o desenho;
- **"Nenhuma ação ainda."** quando o histórico está vazio (hoje, a lista vazia);
- **a 390, só os rótulos acesos e das candidatas** ficam no desenho; os outros nomes vão para o mapa em texto (o espaço não deixa 29
  rótulos a 11 px).

### A prancha

Em `docs/pranchas/ux-digibrain/`, ao lado do `dados.json` (escrita em `docs/pranchas/ux-pet/digibrain/` por causa do H8 e movida pelo Gerente): `digibrain.html`,
`digibrain.css`, `digibrain.js` e `capturar.sh`. **Uma página só, sem `gerar.py`:** o JS lê o `dados.json` no navegador (o `fetch`, que
pede o `python -m http.server 8765` em `D:\Trab\digilab`) e desenha os nós e os fios a partir dele; nenhum número foi copiado à mão. O
caminho dos dados é a constante `DADOS`, no alto do `digibrain.js` (hoje `../../ux-digibrain/dados.json`; depois do movimento,
`dados.json`). Os parâmetros:
- `?estado=com_escolha|uma_opcao|sem_decisao|replay|mudou` (e os extras `com_aprendido` e `save_e2e`); o padrão é `com_escolha`;
- `?pele=vidro|xcom`; `?largura=1920|390` (a página tem o tamanho exato; a 390 o `capturar.sh` a põe num iframe);
- `?notas`: a fonte de cada leitura por cima do desenho (o campo do `Motor.digibrain()` e o arquivo do motor);
- `?texto`: o mapa em texto aberto; `?rolar`: a folha de 390 rolada até o fim; `?reduzir`: o quadro de "reduzir movimento";
- `?selo=vivo|pausado`: o selo é do app (`estadoSelo`), não do `dados.json`; o replay força "replay".

Um estado, uma pele, uma largura ou um parâmetro desconhecido, um nó fora do mapa ou o `acesas` fora de par com a `decisao` **aparecem como
erro na tela** (a faixa vermelha embaixo), não como desenho vazio. `sh capturar.sh` grava em `D:\Trab\digilab\capturas_ux_digibrain_aprovar\`
os cinco estados nas duas larguras e nas duas peles, as notas no Vidro e os extras (o texto aberto, a folha rolada, o reduzir, o pausado).
A 1920, atrás do scan há uma cor neutra com "a ilha 3D continua por baixo do modo scan"; a constante `FUNDO_ILHA` aceita uma captura da ilha.

### SVG ou canvas, no código

**Recomendação: SVG**, como o `MapaPesos` de hoje, e a prancha já é SVG.
- **O tamanho cabe com folga:** 77 fios e 29 nós no save do e2e (o pior caso conhecido, os dois pets do `connectome_cerebro_a.md`, dá
  ~240 pesos); o SVG só pesa na casa dos milhares.
- **O e2e de hoje lê o DOM do mapa:** `svg.mp[data-n]`, `.mp-pesos path`, `.mp-acesas path`, `[data-regra].mp-lit`, `.mp-esc`, `.mp-cand`,
  `.mp-pct`, `[data-entrada].mp-lit`, `.mp-dest[data-lobo]`. A prancha mantém essas classes; em canvas, o teste inteiro teria de virar um
  gancho de leitura.
- **As peles entram pelo CSS** (`var(--hx-*)` direto no `stroke`), sem copiar cor para o JS.
- **A acessibilidade:** `role="img"` com o `aria-label` de hoje, e o mapa em texto ao lado.
- **O movimento é barato:** o pulso é um `stroke-dashoffset` animado em ≤ 15 caminhos (uma aresta acesa por entrada) com `pathLength="1"` (a Web Animations API, que o
  `getAnimations()` do e2e enxerga); a varredura, um elemento HTML por cima; o giro, um `transform` CSS na camada do desenho (D1-4), sem
  recalcular os 77 caminhos a cada quadro.

### O custo em determinismo

**Nenhum.** A tela só lê; nada vai ao log, ao save, à rng ou ao replay. A varredura, o pulso e o giro dependem só do relógio da vista
(`requestAnimationFrame`) e da troca de `mapa.acesas.n`, que o motor já expõe. O replay continua igual: o selo "replay" e o mapa da
decisão do passo.

### O custo em e2e

O e2e de hoje (`e2e/jogo.spec.ts:1166-1260`) usa, e a prancha mantém:
- **`#pet-painel`** e **`.digibrain`**: o scan é o `<div id="pet-painel" class="scan digibrain" role="dialog" aria-modal="true">` (a 1920)
  e a folha inteira a 390, com o mesmo `#pet-painel` e `.digibrain` que o e2e procura nas duas larguras (o seletor do mapa já aceita o
  `dialog.folha[open] svg.mp`). Fica também o `.digibrain` escondido antes de abrir;
- **`.db-selo`** com o texto exato "ao vivo" (a forma do selo é CSS, fora do texto);
- **`.db-barras li`** (4, ou 5 com o piso) e **`li[data-lobo='impulsos']`**; **`.db-opcoes li.esc`** (1); **`.db-emo`** com "memória do
  pet"; **`.db-ultimas li`**;
- **`svg.mp`** com as classes do mapa listadas acima (o pulso fica num grupo `.mp-pulso` à parte, fora da contagem de `.mp-acesas path`);
- **"Fechar DigiBrain"** (o nome do botão), e o `#pet-painel` some ao fechar;
- o texto sem "pensando", "sentindo", "conectoma" e "connectome".

**O que precisa mudar:**
- **O teste "sem animação"** (`getAnimations().length === 0` e a `transition` `0s`, `jogo.spec.ts:1246-1250`) quebra com o pulso e o giro.
  Recomendação (D1-8): ele passa a rodar com `page.emulateMedia({ reducedMotion: "reduce" })` (é o contrato do reduzir: zero animação), e um
  teste novo, sem o reduzir, confere que depois de uma decisão nova a varredura e o pulso existem e **terminam** (nenhuma animação infinita
  além do giro).
- **As capturas** `digibrain-<largura>.png` e `digibrain-mapa-*` mudam inteiras (as duas peles), e a da tela Pet a 1920 com o painel aberto
  também; precisam do ok do Matheus antes do `--update-snapshots`.
- **O `camera_livre.spec.ts`** ("o minimapa sai enquanto ele está aberto") continua valendo: o scan cobre a ilha e o minimapa.
- **O `lab_modular.spec.ts`** (`.db-barras--div`, "Fechar DigiBrain") não muda se o `DigiBrainLab` continuar no painel de hoje (D1-9).
- **Testes novos:** o Esc fecha o scan e devolve o foco à linha "DigiBrain" da pilha (ou à linha do agora, se foi ela que abriu); o mapa em
  texto abre, tem uma linha por `mapa.arestas` e o nome acessível; a 1920 o scan cobre a viewport inteira; nenhum rolamento horizontal a 390.

### A acessibilidade

- **O equivalente em texto:** o `aria-label` do `svg.mp` de hoje ("Mapa dos pesos do pet, 77 pesos. Nesta decisão: regra tempo livre,
  escolheu chamar você com 9% de chance.") e o botão **"O mapa em texto"** (`aria-expanded`, `aria-controls`), que abre a lista das arestas
  acesas (a entrada, a favor ou contra, a força) e a tabela dos pesos com `<caption>` e `<th scope="col">`. Os ladrilhos já são texto.
- **O foco:** ao abrir, o foco vai para o "Fechar DigiBrain"; o foco fica preso no scan (`aria-modal`); a ordem é a visual (Fechar, "O mapa
  em texto", os ladrilhos não têm foco); ao fechar, volta a quem abriu. Os nós do mapa **não** recebem foco (29 paradas de Tab; o texto cobre).
- **O Esc** fecha no desktop e no celular (com teclado); o × da folha tem o mesmo nome.
- **Os 44 px:** o Fechar e "O mapa em texto" têm 44 × 44 no mínimo; nada mais no scan é clicável.
- **Nada só pela cor:** o aprendido tem o tracejado e a palavra; o negativo, o tracejado; o selo, a forma; a escolhida, "· escolhida"; a
  favor e contra, a palavra; "pesou mais", a caixa e a palavra.
- **Reduzir movimento:** sem varredura, pulso nem giro; o `prefers-reduced-transparency` deixa o Vidro opaco, como no app.
- **O contraste:** o texto em `--hx-texto` e `--hx-sec` sobre o `--hx-chao`, como a HUD; os fios são objetos gráficos (3:1).

### Perguntas ao Matheus

| # | pergunta | recomendação | custo de errar |
|---|---|---|---|
| D1-1 | o desenho em SVG ou em canvas no código | **SVG** (a seção acima): cabe, mantém o e2e e as peles pelo CSS | canvas: o e2e do mapa vira um gancho de leitura e as cores passam pelo JS; SVG: só pesaria com milhares de fios, que o A não tem |
| D1-2 | os números do movimento | **PROPOSTO, SEM FONTE, para ajustar na mão:** a varredura em 1,2 s, o pulso em 0,8 s logo depois, o giro de ±8° num ciclo de 40 s | só vista; nenhum número de jogo. Rápido demais pisca; lento demais atrasa a leitura da decisão |
| D1-3 | o giro no celular | **desligado no celular**, só no desktop | ligado: bateria e os rótulos acesos, que já são poucos, balançando a 11 px; desligado: o celular perde um enfeite |
| D1-4 | como o giro gira | **o plano inteiro balança (`rotateY` em CSS)**, sem dar profundidade a cada nó | dar um z a cada região inventa uma profundidade que o motor não tem e pede recalcular os fios a cada quadro; o plano é "menos 3D" |
| D1-5 | as barras dos lobos com o eixo no zero | **sim**: o negativo à esquerda do eixo, na cor do lobo, no lugar do rosa de hoje | o rosa é "vem do corpo" (guia 3) e hoje marca qualquer negativo, inclusive o do aprendido; com o eixo, o cheio de um lado passa a ser 100 % (o impulsos de 105 % enche a metade) |
| D1-6 | o pulso e a varredura no replay | **não**: no replay só o destaque troca a cada passo, como no reduzir | com o pulso, o replay rápido vira um pisca-pisca; sem ele, o replay fica igual ao de hoje |
| D1-7 | o mapa em texto mostra os inteiros `w` e `w0` | **sim, na tabela**, com a marca em palavras (instinto, aprendeu a mais, a menos, negativo); a lista das acesas fica só com a palavra e a força | sem os inteiros, quem pesquisa perde o número; com eles, sem a escala S, um jogador pode estranhar "1024" |
| D1-8 | o e2e do "sem animação" | **roda com o reduzir emulado**, e um teste novo confere que a varredura e o pulso terminam | sem a troca, o teste quebra no primeiro pulso; trocá-lo sem o teste novo deixa passar uma animação em loop |
| D1-9 | o `DigiBrainLab` (o modular) | **continua no painel de hoje** até a etapa dele | abrir o modular no scan agora pede o desenho dos módulos, que é outra prancha; por um tempo, os dois cérebros abrem em lugares diferentes |
| D1-10 | o tempo do jogo com o scan aberto | **continua andando** (é uma vista; o selo diz "ao vivo"), e **o cartão do chamado do pet aparece por cima do scan**, no alto ao centro, como na tela Pet | pausar mudaria o selo e a varredura nunca passaria; andar sem o chamado por cima deixa o dono perder um pedido enquanto olha o mapa |
| D1-11 | os números de layout: as colunas de 420 px, o topo de 72 px (56 na folha), a moldura de 262 px de altura a 390 | **PROPOSTO, SEM FONTE**, só layout | nenhum número de jogo; a 1600 px as colunas pedem 360 px (a conferir no código) |

### Decididas (Matheus, 2026-11-07)

"Aprovar e codar": valem as recomendações D1-1 a D1-11 da tabela acima, como estão. Os números do movimento (D1-2) e os de layout (D1-11)
ficam PROPOSTO, SEM FONTE. Antes do código, a prancha corrigiu três defeitos que ela mesma apontava: o rótulo "receptores do corpo" cortado a
390, o rótulo "sem cuidado" sob a varredura a 1920 (agora a varredura passa por baixo dos rótulos) e os traços do "tronco", que saíram.

### D1b — o modal pequeno (Matheus, 2026-11-07, depois do PR #668)

O Matheus mudou a direção depois de ver o código: "A ideia, na verdade, é a tela do DigiBrain ela ser muito menor. Não ocupar a tela
inteira. Apenas um modalzinho com o cérebro, sem essa quantidade de texto." **A aprovação da tela cheia fica suspensa** até ele ver a prancha
nova: `docs/pranchas/ux-digibrain/modal.html` (mesmos dados, `dados.json`), com as capturas em
`D:\Trab\digilab\capturas_ux_digibrain_aprovar\modal\` (`capturar_modal.sh`; o fundo é a Tela Pet real do mesmo pet, tirada do jogo).

**O que sai do modal:**
- os cartões Agora, Peso dos lobos, O que mais pesou, Opções, Aprendido e Últimas ações;
- a legenda do rodapé e o parágrafo;
- o rótulo "pesou mais" e a região "memória e emoção · sem pesos".

**O que fica:**
- o título "DigiBrain";
- o selo só como forma (ponto, barras, triângulo), com a dica;
- o "i", que abre a dica "a forma é só desenho" com a legenda curta;
- "O mapa em texto" como botão de ícone, que troca o desenho pela tabela, no mesmo tamanho;
- o fechar (Esc, e um clique fora);
- o mapa, com a percepção, os receptores do corpo, as regras, as ações e o caminho aceso.

O movimento é o da D1, sem mudar.

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| D1b-1 | onde o modal fica a 1920 | **à direita, sobre a pilha de painéis** (de onde ele abre), 720 px de largura, a 72 px do alto: o pet fica à vista no meio. A alternativa é no centro (`?lugar=centro`) | no centro, o modal cobre o pet, e o dono não vê a ação que o mapa explica |
| D1b-2 | o tamanho | 720 px de largura (o desenho, 696 × 437) a 1920; a 390, uma folha baixa de ~320 px (o desenho, 374 × 235). **PROPOSTO, SEM FONTE** | maior, volta a ser tela; menor, os rótulos dos nós caem abaixo de 11 px a 1920 |
| D1b-3 | o fundo | **um véu leve, sem desfoque**: a ilha continua a pleno ritmo. Saem o `CENA.coberto` e o fundo opaco da D1; o vidro fica só no próprio modal, como num painel da HUD | com o desfoque, a cena inteira paga o vidro a cada quadro (o que a rev-cena barrou); sem o véu, o modal parece solto na tela |
| D1b-4 | a 390 | **folha baixa presa embaixo**, com o pet visível acima; só os rótulos acesos e das candidatas | o cartão central cobre o pet, e a folha inteira volta ao que o Matheus recusou |
| D1b-5 | o selo ao vivo, pausado ou replay | **só a forma, ao lado do título**, com a dica e o nome acessível | sem selo, o replay parece ao vivo; com o texto, volta texto que ele tirou |
| D1b-6 | os rótulos das regiões | **"ações", "regras" e "percepção"** (os nomes que o dono entende), mais "receptores do corpo" | "decisão" e "impulsos" são os nomes dos lobos e confundem quem não leu o motor; o `data-lobo` do e2e continua no código |
| D1b-7 | a legenda | **vai para a dica do "i"** | sem legenda nenhuma, o vermelho e o azul do aprendido ficam sem explicação |

**Decididas (Matheus, 2026-11-07):** "Aprovar e codar". Valem as recomendações D1b-1 a D1b-7 como estão na tabela, e os números de layout
ficam PROPOSTO, SEM FONTE. No código, o cabeçalho "AGORA" e o mapa vêm do mesmo pet (na prancha divergiam por causa dos dados de teste).

### D1c — o campo pequeno (Matheus, 2026-11-07, depois do código da D1b)

Depois de ver o código da D1b, o Matheus pediu: "Na verdade, faz esse modal menor, ele está muito grande. Ele tem que ser um campo pequeno."
Isso revoga o tamanho da D1b-2. Foram duas opções, tiradas do jogo real com o CSS de cada uma, em
`D:\Trab\digilab\capturas_ux_digibrain_aprovar\modal_menor\` (com um `LEIA.md`):
- **(a):** 420 px a 1920, no canto direito sob o relógio; a 390, um cartão de 264 × 210 px no canto de baixo.
- **(b):** 520 px a 1920; a 390, uma folha de 210 px com os botões numa coluna à esquerda do desenho.

**Decidida (Matheus, 2026-11-07):** "(a) desk, (b) celular". Fica assim:
- **Desktop:** o painel de 420 px sob o relógio, com a altura acompanhando o desenho (~306 px).
- **Celular:** a folha de 210 px na largura toda, com os botões numa coluna à esquerda e sem os nomes das regiões, que não cabem.
- **O título** é só o ícone do cérebro, ao lado do selo; o nome "DigiBrain" fica para o leitor de tela.
- **Os rótulos** ficam só no caminho aceso e nas opções; o de outro ponto aparece ao passar o mouse ou ao tocar nele. A legenda fica no "i".

Os tamanhos são PROPOSTO, SEM FONTE.

**Decidida também (Matheus, 2026-11-07, "siga com as recomendações"):** o movimento continua como na D1. A varredura e o pulso só passam
a 1x ou mais devagar; em avanço rápido, só o destaque troca.
