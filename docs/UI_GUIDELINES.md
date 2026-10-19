# Digilab — UI guidelines

Guia de interface do jogo web (`web/digilab_sprites.html`). Vale para qualquer tela nova ou
alterada. A referência visual é o canvas "Digilab — Direções visuais", página **Direção
Digimon UP** (https://claude.ai/artifact/2XHKuofCpCfZeA1N6iVy9g); a prancha
`UpComponentes` é a versão desenhada deste guia.

**Quando o guia e uma prancha divergirem, vale o guia.** Números e textos das pranchas são
exemplos de layout, nunca dados.

---

## 1. Princípios

1. **Honestidade acima de fofura.** Nada na tela afirma algo sobre o pet que o motor não
   registrou. Sem registro, a interface mostra o vazio ("não sei", "sem motivo registrado"),
   nunca um texto plausível.
2. **O aprendizado tem que ser visível.** É o diferencial do jogo. Toda informação que vem do
   que o dono ensinou usa a marca do aprendido (seção 3), para o jogador reconhecer de relance
   "isso foi eu que ensinei".
3. **Só descrever o que é extremo.** Traço, temperamento e caráter dentro da faixa comum não
   ganham texto. Neutro é silêncio.
4. **Menos texto, mais leitura visual.** Barra, ícone e cor semântica antes de frase. Frase só
   onde o estágio do pet permite (seção 9).
5. **Sem culpa e sem retenção.** O pet pode mostrar que sentiu uma demora. A interface nunca usa
   isso para prender: sem "ele vai ficar triste se você sair", sem contagem regressiva em
   destaque, sem notificação insistente, sem sequência diária.
6. **Celular primeiro.** Desenhar em 390×844 e conferir em 360 px. Desktop é adaptação.
7. **O layout não depende da arte.** Os sprites são trocáveis. O espaço vem do tamanho nativo do
   quadro em escala inteira; trocar um Digimon não pode mover a tela.
8. **Falhar alto.** Sprite, emote ou texto faltando aparece como erro visível em
   desenvolvimento, nunca como placeholder silencioso.

---

## 2. Linguagem visual

Duas camadas, sempre juntas:

- **Mundo de jogo claro (Digimon UP):** fundo azul-gelo com padrão hexagonal, cards brancos com
  borda grossa, plaquinhas azul-marinho com nome, números em itálico pesado com contorno,
  faixa quadriculada azul no topo das telas.
- **Rede digital (Tamers):** malha ciano, brilho, dado sendo digitalizado. **Não é decoração:**
  é reservada para o que foi aprendido e para o palco de luta.

Nada de degradê decorativo, sombra difusa de app genérico, emoji do sistema ou ilustração que
não seja pixel art. Sombras são duras (deslocamento de 3–5 px, sem desfoque), como em jogo.

---

## 3. Semântica fixa

Cada marca abaixo tem **um** significado. Não reutilizar para enfeite.

| marca | significa | onde aparece |
|---|---|---|
| **rosa sólido** (`--dl-need`) | vem do corpo: necessidade física | desejo "necessidade", fome/energia baixas, chamado de cuidado |
| **malha ciano tracejada** (`--dl-learned` sobre `--dl-learned-bg`) | aprendido com o dono | vontade aprendida, regra de combate usada, chip de causa, regra reforçada |
| **amarelo** (`--dl-highlight`) | momento de destaque, um por tela | elogiar, continuar a revelação, seleção de pet |
| **listras de perigo** (`--dl-force` / `--dl-force-ink`) | tentação com custo | botão Forçar e nada mais |
| **roxo** (`--dl-dark`) | caminho sombrio | sobrecarga, aviso de forma sombria, fala fria |
| **vidro azul congelado** | em espera, congelado | slot de pet em espera |
| **cinza tracejado + "?"** | sem registro, o pet não sabe | motivo ausente, fala marcada "sem base" |
| **verde** (`--dl-ok`) | vida, ok, sincronizado | barra de vida, janela de chamado aberta, status online |

Toda marca carrega sentido também pela **forma** (sólido × tracejado × listrado × "?"), para
funcionar sem cor.

---

## 4. Tokens

Implementar como variáveis CSS em `:root`, com tema escuro em
`@media (prefers-color-scheme: dark)` e em `[data-tema="escuro"]`.

### 4.1 Cores

| token | claro | escuro | uso |
|---|---|---|---|
| `--dl-bg` | `#E8F0FB` | `#0B1636` | fundo da tela |
| `--dl-hex` | `#D4E3F7` | `#1B3163` | linhas do padrão hexagonal, trilho de barra vazia |
| `--dl-surface` | `#FFFFFF` | `#152A5C` | card |
| `--dl-surface-2` | `#F4F8FE` | `#1B3470` | fundo interno de card (palco) |
| `--dl-border` | `#9FC2EF` | `#2C5BBD` | contorno de card |
| `--dl-border-shadow` | `#7FA6DC` | `#0F2A66` | sombra dura de card |
| `--dl-navy` | `#173A8A` | `#173A8A` | plaquinha, barra de navegação, contorno de botão |
| `--dl-navy-deep` | `#0F2A66` | `#0A1D4A` | borda de plaquinha, sombra de texto |
| `--dl-action` | `#2C73E0` | `#4F93F2` | botão primário |
| `--dl-action-press` | `#1B54B4` | `#2C73E0` | botão primário pressionado |
| `--dl-text` | `#13244D` | `#E6EEFF` | texto |
| `--dl-text-2` | `#3A5288` | `#B4C6EC` | texto de apoio |
| `--dl-need` | `#E5489F` | `#FF7FC0` | necessidade |
| `--dl-learned` | `#6FE3FF` | `#6FE3FF` | aprendido (linha, borda, texto de rótulo) |
| `--dl-learned-bg` | `#0F3A86` | `#0F3A86` | aprendido (fundo da malha) |
| `--dl-highlight` | `#FFD23F` | `#FFD23F` | destaque |
| `--dl-ok` | `#3FCF6A` | `#4BE07E` | vida, ok |
| `--dl-force` / `--dl-force-ink` | `#FFCC33` / `#1A1A1A` | iguais | listras do Forçar |
| `--dl-dark` | `#7B3FB8` | `#A56BE0` | sombrio |
| `--dl-disabled` | `#C7D3E6` | `#2A3A60` | fundo desativado |
| `--dl-disabled-ink` | `#56657F` | `#8795B3` | texto desativado |

Contraste mínimo: 4,5:1 para texto até 23 px, 3:1 acima. Texto branco só sobre `--dl-action`,
`--dl-navy`, `--dl-need` ou `--dl-learned-bg`. Texto sobre amarelo é `#3B2A00`.

### 4.2 Tipografia

| papel | fonte | peso | tamanhos |
|---|---|---|---|
| números, títulos de tela | Rubik itálico | 900, com contorno `--dl-navy` de 2–3 px e sombra de 4 px embaixo | 26–44 |
| títulos de card, rótulos fortes | M PLUS Rounded 1c | 900 | 15–22 |
| texto | M PLUS Rounded 1c | 700 | 15 (mínimo 13) |
| apoio, legenda | M PLUS Rounded 1c | 700–800 | 11–13 |
| detalhes de LCD (relógio, turno, nível) | DotGothic16 | 400 | 13–18 |

Carregar pelo Google Fonts com fallback (`system-ui`, `sans-serif`). Nunca abaixo de 11 px.
Respeitar o zoom do navegador: tamanhos em `rem`, sem `maximum-scale`.

### 4.3 Espaço, cantos, bordas

- Escala de espaço: **4, 8, 12, 14, 16, 24, 40** px. Margem lateral no celular: **14 px**.
- Cantos: **6** plaquinha e etiqueta, **10** tile e slot, **12** botão e card pequeno,
  **16** card de palco. Círculo para botão de ícone redondo e retrato.
- Card: borda branca de 3 px (ou `padding` branco de 4 px) + contorno `--dl-border` de 2 px +
  sombra dura `--dl-border-shadow` de 3 px para baixo.
- Botão: borda branca de 3 px + contorno `--dl-navy` de 2 px + sombra interna de 4 px embaixo
  (`--dl-action-press`), que some ao pressionar.

---

## 5. Sprites

- **Escala inteira, sempre:** 1× listas e retratos, 2× cards, 3× palco e luta, 4× revelação de
  evolução. `image-rendering: pixelated` no CSS e `imageSmoothingEnabled = false` no canvas.
  Nunca redimensionar para caber: escolher a escala menor.
- **Âncora nos pés.** O sprite é alinhado pela base do quadro sobre o anel de plataforma ou a
  sombra elíptica; quadros de alturas diferentes não "pulam".
- **Direção:** o pet do jogador olha para a direita na luta (espelhar se preciso), o oponente
  para a esquerda. Fora da luta, sem espelhar.
- **Animação:** idle a 120 ms por quadro (grupo `A` dos quadros extraídos, salvo quando o mapa de
  sprites disser outro). Ataque e dano só na luta. Com `prefers-reduced-motion`, mostrar o
  primeiro quadro parado.
- **Forma sombria:** mesmo espaço da forma base, com a marca roxa (contorno ou filtro de paleta
  aprovado no mapa de sprites) e a etiqueta "sombria". Nunca só a cor.
- **Em espera:** sprite dessaturado sob vidro azul congelado, com a etiqueta "EM ESPERA".
- **Forma futura desconhecida:** silhueta preta a 45% de opacidade com "?". Não revelar forma que
  o motor ainda não decidiu.
- **Ovo:** mesmo tratamento de escala; o ovo representa a espécie antes de chocar.
- Sprites de terceiros são de uso pessoal e local: ficam fora do repositório, com o crédito e o
  aviso no rodapé.

---

## 6. Ícones

- **Estado do pet** (fome, carinho, humor, "!", elogio): emotes pixel `CustomEmoji_Digimon_*`, em
  16, 24 ou 32 px (múltiplos do grid do emote).
- **Controles de interface** (voltar, pausar, enviar): ícone de traço, 2,5–3 px, cantos
  arredondados, na cor do texto do botão. Nunca emoji do sistema.
- **Treino:** os hexágonos de treino do jogo, 54×61 px no botão.
- Todo botão só com ícone tem `aria-label`. Ícone decorativo ao lado de texto tem `alt=""`.

---

## 7. Componentes

Anatomia e estados. Tudo que é clicável é `<button>` ou `<a href>` de verdade, com alvo de
toque mínimo de **44×44 px**.

### 7.1 Botões

| tipo | aparência | quando usar |
|---|---|---|
| **primário** | fundo `--dl-action`, texto branco 900 | a ação principal da tela (Atender, Tornar ativo, Descansar). Um por área. |
| **secundário** | fundo branco, contorno `--dl-navy` 3 px, texto marinho | ações de apoio (Exportar, Importar, Repreender) |
| **destaque** | fundo `--dl-highlight`, texto `#3B2A00` | elogiar, continuar a revelação. Um por tela. |
| **forçar** | moldura listrada `--dl-force`, miolo `--dl-force-ink`, "FORÇAR" + "+ sobrecarga" | só quando a fadiga passa do limite. O custo fica escrito no próprio botão. |
| **ícone** | 44 px, quadrado (canto 12) ou redondo | pausar, voltar, álbum, trocar de pet |

Estados obrigatórios: **normal**, **pressionado** (fundo `--dl-action-press`, sombra interna
invertida, desce 2 px), **foco** (anel `--dl-highlight` de 3 px por fora, visível no teclado),
**desativado** (`--dl-disabled`, sem sombra, `disabled` de verdade, com o motivo em texto perto
quando não for óbvio).

### 7.2 Card

Contêiner padrão (seção 4.3). O **card de palco** tem cabeçalho translúcido com o título, fundo
hexagonal e o sprite sobre o anel de plataforma. Não aninhar card dentro de card; dentro de um
card, separar por espaço ou tile.

### 7.3 Plaquinha de nome

Fundo `--dl-navy`, borda `--dl-navy-deep`, brilho de 3 px no topo, texto branco 900. Variante
**inclinada** (cantos cortados em paralelogramo, Rubik itálico) para rótulos de recompensa.
Sempre abaixo ou acima do sprite, centralizada.

### 7.4 Etiquetas

Pílula de canto 4–6, texto 11–12 px 900 em caixa alta: **estágio** (amarelo), **ATIVO**
(verde), **EM ESPERA** (azul), **sombria** (roxo). Nunca mais de duas juntas.

### 7.5 Barras

- **Segmentada:** 5 ou 10 blocos com 2–3 px de espaço. Para necessidades, fadiga, sobrecarga e
  janela de chamado. `aria-label` com "N de M". Um marcador vertical `--dl-navy` indica limite
  (fadiga) ou início da faixa de aviso (sobrecarga).
- **Relativa ao pet comum:** trilho contínuo com um traço vertical no meio ("pet comum"). Rótulo
  textual ("muito acima", "abaixo") **só** fora da faixa comum.
- **Vida:** contínua, `--dl-ok`, canto arredondado, nome e valor acima.

### 7.6 Card de desejo

Par lado a lado, sempre juntos quando houver os dois:
- **necessidade:** cabeçalho rosa sólido, emote, verbo curto ("comer"), "vem do corpo";
- **vontade aprendida:** fundo de malha ciano, borda tracejada, brilho, cabeçalho ciano, ícone,
  verbo ("lutar de perto"), "aprendida com você".

Se o motor só tiver um dos dois, mostrar só um. Se não tiver desejo, não mostrar o par.

### 7.7 Chip de causa

Liga uma decisão, fala ou recusa à memória que o motor registrou como causa.
- **com registro:** malha ciano, emote da categoria (elogio, bronca, demora, carinho) + texto
  curto com a origem ("elogio · luta, turno 7");
- **sem registro:** tracejado cinza, "? sem motivo registrado".

Nunca gerar a causa por texto livre.

### 7.8 Balão de fala

Contorno marinho 3 px, sombra dura, rabinho do lado do pet. O conteúdo segue o estágio
(seção 9). Variantes:
- **sem base** (verificador marcou): fundo cinza claro, borda tracejada, texto riscado,
  seguido da nota "Sem base: nada registrado sobre X" e, se houver, a fala corrigida;
- **frase pronta** (LLM indisponível): igual ao normal, com a etiqueta discreta "frase pronta";
- **sombria:** fundo roxo escuro `#2A1440`, borda `--dl-dark`, texto claro, frases frias.

### 7.9 Chamado

Faixa com ícone do pedido num tile marinho, título ("Chamado: fome"), barra segmentada da janela
e botão primário "Atender". A janela é uma barra, **nunca um cronômetro em segundos**. Chamado
perdido: a faixa some e o evento vai para o Diário; sem alarme vermelho.

### 7.10 Slot de pet

Tile de 76 px em grade de 4 colunas: **ativo** (cantos amarelos em L), **em espera** (vidro
congelado + etiqueta), **ovo novo** (tracejado, ovo + "novo ovo"), **vazio** (tile escuro sem
conteúdo, não clicável).

### 7.11 Cabeçalho de tela

Faixa quadriculada azul com borda marinho embaixo, botão voltar (44 px) e título em Rubik
itálico com contorno. A tela Pet usa, no lugar, retrato redondo (abre Meus pets) + plaquinha do
nome + etiqueta de estágio + relógio + status de sincronização.

### 7.12 Navegação

Barra inferior marinho com 4 destinos: **Pet, Crescer, Lutar, Diário**. Ícone num círculo de
44 px + rótulo sempre visível. O ativo tem círculo `--dl-action`, anel ciano e
`aria-current="page"`. No desktop (≥ 900 px) a barra vira coluna lateral à esquerda.

---

## 8. Layout

- **Tela Pet (ordem fixa):** cabeçalho → palco (pet, emoção, balão) → necessidades → chamado
  aberto (se houver) → desejo → navegação. O resto (traços, memórias, temperamento × caráter,
  vínculo, obediência) fica a um toque, em Crescer.
- Largura útil no celular: 100% menos 14 px de cada lado. Conteúdo rola; cabeçalho e navegação
  ficam fixos. Respeitar `env(safe-area-inset-*)`.
- **Desktop:** coluna central de até 480 px para as telas de pet; telas de dados (Crescer,
  Diário) podem abrir em duas colunas até 1100 px. Nunca esticar sprite para ocupar espaço.
- Grades: 2 colunas para pares (desejo, recompensa), 3 para exercícios, 4 para necessidades e
  slots. Sempre com `gap`, nunca com margem solta.

### 8.1 Desvio aprovado: a tela Pet com o visual do protótipo (2026-10-19)

Decisão do Matheus: na tela Pet, o visual do protótipo externo vence este guia. Vale só para a
tela Pet (com a barra lateral e a barra de baixo que ela usa); as outras telas seguem o guia. As
pranchas são `PetPrototipoDesktop.html` e `PetPrototipo390.html`. O que muda em relação ao guia:

| assunto | o guia | a tela Pet |
|---|---|---|
| cores (§4.1) | `--dl-bg` `#E8F0FB`, borda `#9FC2EF`, ação `#2C73E0`, texto `#13244D` | fundo `#eef3fa`, borda `#dbe6f5`, primário `#1677ff`, texto `#0d2147`, apoio `#6a7b9c`, trilho `#e8f0fc`; lateral `#0b2556`; necessidades fome `#f43f5e`, energia `#fbbf24`, humor `#1d8bf1`, saúde `#2dd4a7` (a higiene, que o protótipo não tem, usa `#6366f1`, da paleta dele) |
| tipografia (§4.2) | Rubik itálico com contorno, M PLUS Rounded 1c, DotGothic16 | Nunito (400 a 800) em tudo; Pixelify Sans 700 só no logo; títulos de módulo em 16 px 800 |
| card (§4.3, §7.2) | borda branca de 3 px, contorno de 2 px, sombra dura de 3 px | o módulo do protótipo: canto 16,8 px, borda de 1 px `#dbe6f5`, fundo branco a 80 %, sombra leve, cabeçalho com tracinho azul de 4×24 px, ícone de 20 px e título |
| botões (§7.1) | contorno marinho, sombra interna | ação em bloco (canto 12, borda de 1 px, ícone de 36 px e rótulo); o primário (Alimentar) em azul cheio de cantos cortados |
| barras (§7.5) | segmentadas de 5 blocos para necessidades | contínuas de 10 px, cantos redondos, na cor da necessidade, com "x/100" ao lado |
| ícones (§6) | emotes pixel para estado do pet | ícones de traço de 2 px (o desenho do protótipo, redesenhado em SVG inline); os sprites do pet não mudam |
| navegação (§7.12) | barra marinho, ícone em círculo de 44 px, ativo com anel ciano | lateral de 240 px `#0b2556` com grade e estilhaços, ativo em azul cheio de canto cortado; no celular, a barra de baixo no mesmo azul e o mesmo ativo |
| layout (§8) | coluna central de até 480 px no desktop; ordem palco → necessidades → chamado → desejo | desktop: lateral, coluna principal (Habitat e Ações) e coluna de 370 px (Estado atual, chamado, desejo, DigiBrain, Últimas ações); celular: Habitat → Ações → Estado atual → chamado → desejo |
| fundo | padrão hexagonal | a grade de 48 px e os estilhaços azuis do protótipo; o palco continua o card hexagonal de hoje |

Continua valendo o guia em: só o que o motor registra, os nomes Digimon, o alvo de toque de
44 px, o foco visível, o `aria-label` dos botões só com ícone, o par necessidade × vontade
aprendida (§7.6) e o chip de causa (§7.7), a fala por estágio (§9) e os estados especiais (§10).

---

## 9. O pet fala conforme o estágio

| estágio | forma da fala | exemplo |
|---|---|---|
| In-Training | só emote, sem causa | emote de coração |
| Rookie | ícones com a causa | carne + ampulheta |
| Champion | palavras soltas, frases curtas, minúsculas | "fome. você demorou." |
| Ultimate e Mega | frase completa que explica o que fez e por quê | "Recuei porque ele ia investir, e você me elogiou da última vez." |

Uma tela nunca mostra ao jogador uma explicação mais rica do que o estágio permite. Quem
explica no lugar do pet é a interface, e só com dado registrado (chip de causa, Crescer).

---

## 10. Estados especiais

| estado | tratamento |
|---|---|
| chamado aberto | faixa de chamado com barra da janela; balão do pet no palco |
| chamado perdido | faixa some; evento no Diário; o pet pode mostrar a emoção registrada |
| recusa | balão do pet + chip de causa (ou "sem motivo registrado") |
| em espera / troca de pet | vidro congelado no slot; frase fixa "fome, sono e vínculo não mudam até voltar" |
| sobrecarga subindo | barra roxa com faixa de aviso marcada; texto curto sobre a forma sombria **antes** de acontecer |
| forma sombria | marca roxa no sprite, etiqueta, fala sombria |
| evolução | tela cheia de revelação: listras azuis, sprite 4× com brilho, linha evolutiva, card "por quê" com os traços reais; botão Continuar; pode pular |
| LLM baixando | barra de progresso com tamanho em MB e opção de cancelar; o pet fala por frases prontas enquanto isso |
| LLM indisponível | faixa discreta "falando por frases prontas"; sem erro assustador |
| fala sem base | variante do balão (7.8) |
| offline | ponto cinza + "offline"; tudo continua jogável |
| sincronizando | ponto azul pulsando (parado com reduced-motion) + "sincronizando" |
| conflito de save | modal com as duas versões lado a lado (data, pet, estágio) e escolha explícita; nunca sobrescrever sozinho |
| luta | palco com fundo de arena, barras de vida, turno em hexágono, intenção do oponente em balão com "!" e texto, efeito "FINTA!" em amarelo, regra usada em card de malha |
| primeira vez | escolher ovo (grade de ovos no molde "Escolher parceiro"), uma dica curta por tela na primeira visita, sempre dispensável |

---

## 11. Movimento

- Quadro de sprite: 120 ms. Pressionar botão: 80 ms. Card entrando: 180 ms, `ease-out`.
  Revelação de evolução: até 2 s, pulável.
- Nada pisca em loop para chamar atenção. O chamado se destaca por posição e cor, não por
  piscar.
- `prefers-reduced-motion`: sem animação de sprite, sem pulsar, transições trocadas por corte.

---

## 12. Texto

- Português do Brasil, frases curtas, verbo na frente nos botões ("Atender", "Tornar ativo",
  "Elogiar"). Sem ponto de exclamação em texto de interface; a empolgação fica com o pet.
- Números concretos em vez de adjetivos quando o motor tiver o número.
- Estágios na tela sempre com os níveis do Digimon: **Digi-Egg, In-Training, Rookie, Champion,
  Ultimate, Mega** (o adulto é Ultimate ou Mega conforme a forma; quando a forma ainda não foi
  decidida, "Ultimate ou Mega"). Formas pelo nome do Digimon do mapa de sprites; espécies pelo
  brasão (Coragem, Amizade, Conhecimento, Sinceridade). Os nomes internos do motor (bebe, crianca,
  adolescente, adulto; brasa, cirro, ferrugem, limo) não aparecem na tela.

| faça | não faça |
|---|---|
| "Chamado: fome · janela aberta" | "Rápido! Seu pet está morrendo de fome!" |
| "Pets em espera ficam congelados." | "Não abandone seus pets!" |
| "Sem motivo registrado." | inventar um motivo plausível |
| "Forçar · + sobrecarga" | esconder o custo num texto de ajuda |

---

## 13. Acessibilidade

- Contraste da seção 4.1; foco visível em tudo; ordem de tabulação igual à visual.
- Nada comunicado só por cor (seção 3). Nada importante só no hover.
- Barras com `aria-label` "N de M"; imagens de sprite com `alt` do nome da forma; decorativas
  com `alt=""`.
- Tamanho de texto ajustável pelo navegador sem quebrar layout até 200%.
- Campos de texto com `<label>` (pode ser visualmente oculto).

---

## 14. Checklist antes de fechar uma tela

- [ ] Todo dado exibido tem origem no motor; o resto foi omitido e listado como lacuna.
- [ ] Marcas semânticas usadas só com o seu significado (seção 3).
- [ ] Sprites em escala inteira, ancorados nos pés, sem suavização.
- [ ] Alvos ≥ 44 px; foco visível; contraste conferido.
- [ ] Funciona em 360 px, 390 px e desktop; temas claro e escuro.
- [ ] Sem culpa, sem contagem ansiosa, sem piscar em loop.
- [ ] Um botão primário e no máximo um de destaque por área.
- [ ] Fala do pet respeita o estágio.
