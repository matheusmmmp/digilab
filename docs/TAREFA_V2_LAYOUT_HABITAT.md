# Tarefa V2 — layout "habitat em tela cheia" com menus XCOM

Gerente: sessão "Gerente do layout habitat" (2026-10-30). Merge só do Matheus. Base: `origin/main` e3c3fdd.

## 1. Referência

- Canvas com todas as pranchas (privado, do Matheus): https://claude.ai/artifact/1TUruea9gFXPVFdesJw1fj — série **D**
  (tela Pet, Crescer/Lutar/Diário com todas as abas, Conversar, Ajustes, telas que abrem sozinhas, coluna Celular).
- Página navegável (privada): https://claude.ai/artifact/EappPCe7iwrXJLQH4ukeym — desktop a partir de 900 px, celular abaixo.
- **Nada das pranchas entra no git** (têm sprites embutidos). A referência no repo é este texto (decisão do Matheus, 2026-10-30).
- Substitui, para o layout, as pranchas `*Desktop` e de 390 px de `docs/estilo_up/pranchas/` e a moldura DIGILAB
  (`docs/TAREFA_V2_MOLDURA_DESKTOP.md`, `docs/TAREFA_V2_PET_QUADRO.md`). Cores semânticas, sprites, textos e acessibilidade
  continuam no `docs/UI_GUIDELINES.md`.

## 2. Decisões do Matheus (2026-10-30)

| # | pergunta | decisão |
|---|---|---|
| D1 | o layout novo substitui o §8 do UI_GUIDELINES? | **sim**: o §8 é reescrito com as regras da seção 3; a ordem fixa antiga da tela Pet e a coluna de 480 px saem |
| D2 | como registrar as pranchas D no repo? | **texto + link** (este documento); nenhuma imagem com sprite no git |
| D3 | pele XCOM e tema | a pele XCOM é **só escura e só nos menus**; o tema claro continua no resto (habitat, balão, retrato, relógio); **Saira Condensed** entra só nos menus, as fontes atuais ficam |
| D4 | Quadro modular | **sai** (`Quadro.tsx` e o arranjo em localStorage), na M3 |
| D5 | portão de capturas (`e2e_capturas`) | fica fora de M2–M6 (vai quebrar e não bloqueia o PR); o Matheus aprova o visual e as referências são regeneradas **na M7** |
| D6 | ordem | M0 → M1 → M2 → M3–M6 em paralelo (sem arquivos em comum) → M7 |
| D7 | pele por CSS ou por componentes `hx-*` (M4/M6, 2026-10-30) | **CSS** sobre as classes `dl-*` dentro do painel e das telas abertas (`.ab-hx`); reescrever as telas em componentes `hx-*` fica como M4b, só se o visual derivar |
| D8 | DigiBrain e "Por que ele disse isso" (M3) | ganham a pele na **M7** |
| D9 | painel aberto no celular (M3, 300 px) | **fica** como está: aberto por quem joga, fecha com um toque |
| D10 | alvo do polimento (2026-10-30) | **só o desktop, no monitor do Matheus: 1920×1080 a 100 %** (janela útil do Chrome ~1920×950). Celular e outras larguras não recebem polimento agora; só não podem quebrar o e2e. O painel das telas fica em 840 px a partir de 1600 px de largura (760 px abaixo) |

## 3. Regras do layout

1. **O habitat ocupa a tela inteira em todas as larguras.** A cena (`CenarioPet`/`PalcoPet`, 3D ou reserva) fica sempre
   montada como camada de fundo; nada cobre o pet na tela Pet.
2. **Ações dentro do habitat:** dock flutuante no rodapé. Desktop: Alimentar, Brincar, Limpar, Carinho, Tapa, Tratar, Mais.
   Celular: 4 + Mais. Mais abre um menu pequeno com o que a versão do pet tiver (Petisco, Banheiro, Pôr ração).
3. **Informação secundária em painéis pequenos recolhíveis** sobre o habitat: Estado atual, Evolução (tempo até a próxima
   forma), Últimas ações. Um aberto por vez. No celular: três botões quadrados na borda direita que abrem um painel compacto.
4. **Chamado do pet** (Atender), **balão de fala** ("toque para ver o porquê") e **DigiBrain** flutuam sobre a cena.
5. **Navegação:** desktop = trilho estreito de ícones à esquerda (Pet, Crescer, Lutar, Diário, Conversar, Ajustes);
   celular = barra embaixo (Pet, Crescer, Lutar, Diário) e Conversar/Ajustes no cabeçalho.
6. **As outras telas abrem sobre o habitat:** desktop = painel grande à direita, habitat escurecido e o pet visível à
   esquerda; celular = modal centralizado sobre o habitat escurecido (não é folha de baixo). O "×" volta ao habitat. As abas
   de cada tela ficam no cabeçalho do painel.
7. **Pele XCOM só nos menus** (painéis, trilho, dock, chamado, modais): painel quase preto, borda fina cinza-petróleo com
   linha mais clara no topo, título condensado em caixa alta com faixa de hachura diagonal, item escolhido em ciano pálido
   com texto escuro, linhas de lista em caixas com borda fina, botão principal no estilo "CONTINUE" (fundo escuro, borda
   verde, hachura no topo), botão de voltar quadrado. O habitat, o retrato do pet, o relógio e o balão mantêm o visual atual.
8. **Telas que abrem sozinhas** no mesmo estilo: Boas-vindas, Como jogar, Escolha seu brasão, Revelação da evolução
   (mantém a `CenaEvolucao`), Medalha, Jornada concluída, Luta em tela cheia (HUD de vida/guts, turno, intenção do rival,
   regra em uso, Pausar/×2/Desistir), Resultado da luta, Dica do Professor Agumon.

Rotas e hash não mudam (`#/destino/aba`, `#/config/<parte>`, `#/lutar/luta`).

### 3.1 Valores da pele (lidos da página navegável; a M1 transforma em tokens `--hx-*`)

| papel | valor nas pranchas |
|---|---|
| chão / fundo da página | `#0B1118` |
| miolo do painel | `#0A1316` a `#16191E`, quase opaco |
| borda fina | `rgba(118,170,175,.38)`; linha de topo mais clara `#5E7C80` |
| texto do menu | `#D6E5E6` / `#BFD6D8`; secundário `#8EA9AB` |
| rótulo pequeno | `#7FE3FF`, 12 px, caixa alta |
| item escolhido | fundo `#BFE5E7`, texto `#0A1316` |
| hachura do título | `repeating-linear-gradient(-60deg, rgba(150,195,200,.38) 0 4px, transparent 4px 9px)` |
| botão principal (CONTINUE) | fundo `rgba(14,30,22,.92)`, texto `#A6E8BC`, borda verde `#6CC58A`, faixa de hachura verde de 6 px no topo |
| medidor segmentado | barra `#9FD5D9` com máscara `repeating-linear-gradient(90deg,#000 0 7px,transparent 7px 9px)` |
| alerta / perigo | `#FFB020` / `#D46A6A` (conferir contra `--dl-*` semânticos; a semântica do §3 vale) |
| fonte | Saira Condensed 400–700 (fallback Rajdhani) só dentro dos menus |

Contraste: todo par texto/fundo da tabela precisa de 4,5:1 (a M1 confere e ajusta se preciso).

## 4. O que é exemplo nas pranchas (não copiar sem o motor)

Os números e nomes das pranchas são de layout (UI_GUIDELINES §1). Itens que **não** devem entrar sem conferir no motor;
o que o motor não tem fica fora ou aparece como "sem dado no motor":

- ganhos e "aptidão" dos exercícios (Levantar pedra, Corrida, Alvo, Esquiva, Meditar, Resistência), limites de fadiga e sobrecarga;
- nomes de bots ("Bot de treino 1/2"), líderes da Liga, regras do Palácio/Fábrica/Salão, contadores atual/melhor;
- regras de luta de exemplo ("se vida < 30% então defender") e os botões Travar/Vetar/Liberar;
- chips e cartas, efeitos e quantidades, número de espaços de equipamento;
- pesos dos lobos do DigiBrain em números, "Instinto × aprendido" em %, lembranças, polos do Jeito;
- "Por que até aqui" (Cuidado/Caráter/Vínculo), linhagem e herança, números de Cenários;
- ilhas e medalhas além das que o motor tem;
- molduras, palavras e limite de caracteres do Conversar (modos Frases prontas / Moldura / Livre);
- opções extras de Ajustes ("Mostrar o porquê no balão", "Verificar o replay ao abrir").

## 5. Mapa tela → componente

| tela / peça | hoje | missão |
|---|---|---|
| casca (camadas habitat + menus) | `App.tsx`, `.moldura` em `estilo/desktop.css`, `Topo.tsx`, `escala.ts` | M2 |
| trilho (desktop) / barra (celular) | `componentes/Nav.tsx` | M2 |
| topo flutuante (retrato → Meus pets, logo, relógio, salvo) | `Topo.tsx`, `CabecalhoPet` em `TelaPet.tsx` | M2 |
| painel das telas sobre o habitat | novo `PainelTela` (desktop: direita; celular: `abrirModal` centralizado) | M2 |
| cena sempre montada | `telas/pet/CenarioPet.tsx`, `PalcoPet.tsx`, `MundoReserva.tsx`, `cenaEstado.ts` | M2 |
| dock de ações + Mais | `AcoesPet`, `IconeAcao`, `BarraRacao`, `PorRacao.tsx` | M3 |
| painéis Estado / Evolução / Últimas ações | `Necessidades`, `EstadoConfianca`, `Emocao`, `Desejo`, `ProximaEvolucao`, `UltimasAcoes` | M3 |
| chamado (Atender) | `Prioridade`, `Chamados` | M3 |
| balão + porquê | `BalaoFala`, `BalaoCausa`, `DetalheFala`, `PainelDetalhes` | M3 |
| DigiBrain | `componentes/DigiBrain.tsx` | M3 |
| sai | `componentes/Quadro.tsx`, `TelaPetDesktop`, arranjo em localStorage | M3 |
| Crescer (Treinar, Aprendizado, Evolução, Itens) | `telas/crescer/*` | M4 |
| Lutar (Arena, Exploração, Fronteira, Medalhas) | `telas/lutar/TelaArena`, `TelaCampanha`, `MapaExploracao`, `TelaFronteira`, `FabricaSalao`, `TelaMedalhas`, `EditorRegras` | M4 |
| Diário (Registro, Catálogo, Gerações, Cenários) | `telas/diario/*` | M4 |
| Conversar | `telas/conversar/TelaConversar.tsx` | M5 |
| Ajustes (principal, aparência, dados, fala, sobre) | `telas/config/TelaConfig.tsx` | M5 |
| Meus pets | `telas/pet/MeusPets.tsx`, `MeusPetsDesktop.tsx` | M5 |
| Boas-vindas, Como jogar, Brasão, Conclusão | `BoasVindas.tsx`, `Jornada.tsx` (`ComoJogar`, `EscolherBrasao`, `Conclusao`) | M6 |
| Revelação | `Revelacao.tsx` (mantém `CenaEvolucao.tsx`) | M6 |
| Medalha, Dica do Professor Agumon | `Medalha.tsx`, `Bit.tsx` (`DicaBit`) | M6 |
| luta em tela cheia e resultado | `telas/lutar/TelaLuta.tsx`, `palcoTR/*`, `ModalResultado.tsx` | M6 |

## 6. Missões

Um PR por missão, cada uma numa worktree `D:\Trab\digilab\v2-layout-<frente>` a partir de `origin/main`.

- **M0 · Tarefa e regras (Gerente):** este documento; §8 do UI_GUIDELINES e `web/app/CLAUDE.md` atualizados. Sem código.
- **M1 · Pele XCOM:** tokens `--hx-*` em `tokens.css` (só escuros; valem nos menus em qualquer `data-tema`);
  `estilo/hud.css` com classes `hx-*` (registrar no PR a escolha CSS × Tailwind); componentes `PainelHx` (título hachurado e
  "×"), `AbasHx`, `LinhaHx`, `BotaoHx`/`BotaoContinuar`, `ChipHx`, `MedidorHx`; Saira Condensed no `index.html`; testes
  de unidade. Nenhuma tela muda.
- **M2 · Casca:** regras 1, 5 e 6; `.moldura` sai; `PainelTela`; revisar `escala.ts`.
- **M3 · Tela Pet:** regras 2, 3 e 4; Quadro sai.
- **M4 · Crescer, Lutar, Diário** dentro do `PainelTela` com a pele (pode virar M4a/b/c).
- **M5 · Conversar, Ajustes e Meus pets** no painel; o crédito dos sprites continua em Ajustes › Sobre.
- **M6 · Telas que abrem sozinhas e luta** (regra 8).
- **M7 · Fechamento (só desktop 1920×950, D10):** e2e com os seletores novos e um caso de viewport 1920×950, capturas
  1920×950 regeneradas depois da aprovação do Matheus, claro/escuro (o tema claro vale fora dos menus), checklist §13/§14.
  A conferência em 360/390/1280 fica fora (só não pode quebrar o e2e).
  Também na M7 (2026-10-30): pele do DigiBrain e do "Por que ele disse isso" (D8); dock flutuante, não faixa de largura
  inteira; faixa de título das Boas-vindas junto do conteúdo; o `.aviso` fixo da M2 não cobre botões nem o cabeçalho do
  painel; remover o CSS morto listado nos PRs #467–#470 e `.pet-quadro`/`--quadro-larg` do `casca.css`.

Dependências: M1 antes de tudo; M2 depende de M1; M3–M6 dependem de M2. Arquivos de uma missão por vez: `App.tsx`,
`tokens.css`, `pet.css`, `Nav.tsx`.

## 7. Regras para todas as missões

- Worktree própria; nunca trocar o branch de `D:\Trab\digilab\v2`.
- Telas só leem o motor por `useJogo()`; só `mudarMotor()` altera. **Nenhuma mudança no motor.** Se um teste de replay ou
  de paridade quebrar, parar e avisar.
- Só o que o motor registra; nomes Digimon na tela; nenhum id interno; nenhum caractere japonês; português do Brasil.
- Sprites Digimon UP autorizados; o atlas fica fora do git; e2e e capturas com o sprite de reserva; crédito em Ajustes › Sobre.
- Acessibilidade: alvos de 44 px, contraste 4,5:1, foco visível, nada só no hover, `prefers-reduced-motion`, modais com
  foco preso e retorno.
- Sem aumentar o escopo. `npm run tipos`, `npm test` e `npm run e2e` passando antes do PR (o e2e se adapta aos seletores
  novos na própria missão); `e2e_capturas` só na M7.
- O relato vai no corpo do PR: o que mudou, o que ficou de fora, decisões pendentes, capturas 390 e 1280 px (anexadas ao
  PR, sem sprite Digimon UP se for imagem versionada).

## 8. Critérios de aceite (no fim da M7)

- A 1920×950 a tela Pet mostra o habitat inteiro, sem nada cobrindo o pet; dock flutuante, painéis recolhíveis, chamado,
  balão e DigiBrain sobre a cena (D10: celular e outras larguras ficam sem polimento, sem quebrar o e2e).
- Toda tela secundária abre sobre o habitat (painel à direita ≥ 900 px; modal centralizado abaixo) e o "×" volta ao habitat;
  a 1920×950 o pet continua visível ao lado do painel.
- Os menus usam a pele `hx-*` (componentes ou CSS sobre `dl-*`, D7); o habitat, o retrato, o relógio e o balão mantêm o visual atual nos dois temas.
- Nenhum item da seção 4 aparece sem dado do motor.
- Rotas e hash iguais; replay e paridade intactos; `tipos`, `test`, `e2e` e o portão de capturas regenerado passando.

## M2 · Casca "habitat em tela cheia" (2026-10-30, worker M2)

- **Feito:** `Habitat.tsx` (cena e palco do Pet como camada de fundo, montada em todas as rotas menos `#/lutar/luta`), `Nav.tsx` (trilho >= 900 px, barra < 900 px, pele `hx-*`), `Topo.tsx` (`TopoHabitat`: retrato, logo, relogio, salvo; Conversar e Ajustes < 900 px), `PainelTela.tsx` (painel a direita >= 900 px; `<dialog>` modal com a barra de destinos dentro < 900 px; "x" e Esc voltam a `#/pet/estado`), `estilo/casca.css`. Saiu a `.moldura`, o topo e a barra lateral claros.
- **`escala.ts`:** o zoom do `<html>` saiu (`zoomAtual()` = 1). Sem prancha de 1280 px fixa, o habitat ocupa a janela.
- **Largura do painel:** >= 1100 px, `min(1000px, 100vw - 306px)`, porque as telas de Crescer/Lutar/Diario ainda usam os layouts desktop de duas colunas (a Exploracao nao cabe em 760 px). Reduzir isso e da M4/M5.
- **Tela Pet:** o conteudo de hoje sobre o habitat; no desktop o Quadro ocupa uma coluna de ~740 px a direita e o modulo "cenario" sai do `render` (o id fica no arranjo salvo). Recolher a coluna lateral nao aumenta mais o habitat: fica para a M3.
- **e2e:** seletores ajustados (Conversar no topo, coluna principal do Quadro sem "cenario", sem a checagem de largura do habitat ao recolher a coluna).

## M7 · Fechamento (2026-10-30, worker M7)

- **Tela Pet a 1920×950:** o habitat tem a altura toda (a reserva do dock só vale abaixo de 900 px) e o dock é uma barra
  flutuante de até 660 px, centrada. O DigiBrain e o "Por que ele disse isso" ganham a pele escura (tokens `--dl-*`
  remapeados também em `.pet-painel__folha`, D8).
- **Painel das telas:** 840 px a partir de 1600 px (o pet fica com ~1000 px de habitat); 760 px abaixo disso.
- **Avisos fixos** (`.avisos`): a partir de 900 px viram cartões pequenos no canto inferior esquerdo, fora do dock, dos botões
  da borda direita e do cabeçalho do painel; abaixo de 900 px seguem como faixa sob o topo.
- **Telas que abrem sozinhas:** a faixa de título das Boas-vindas fica na largura do conteúdo, centrada com ele; o número do
  Resultado perdeu o contorno claro.
- **CSS morto removido:** `.pet-quadro`/`--quadro-larg`, `.desk-*`, `.cfg-*` e `.cfg-desk*`, `.conv-*` (exceto `.conv-voltar`,
  usado por Nova geração), `.mpl-*`, `.imp-*` sem uso, `.mp-tela`, `.mp-*` de Meus pets, `.rc-*`, `.meus-pets .slot`,
  `.db-botao`, `.db-cab`, `.db-rola`, `estilo/desktop.css` e `RegrasCompactas`.
