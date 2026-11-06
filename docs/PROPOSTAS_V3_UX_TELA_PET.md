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
