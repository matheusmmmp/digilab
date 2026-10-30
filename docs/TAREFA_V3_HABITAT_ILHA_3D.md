# Tarefa V3 — o habitat como ilha 3D no estilo Animal Crossing, com o pet em papel (2026-10-30)

Gerente: a sessão que abrir esta tarefa. Worktree: `D:\Trab\digilab\v3-habitat-ilha` (V3-D2), de `origin/main`, com um branch por
missão, `v3-habitat-ilha-<missão>`, cada um a partir do anterior (H0 → H1 → H1b → H2 → H3/H4 → H5), e um PR por missão.
Status: EM ANDAMENTO desde 2026-10-30 (o Matheus pediu para começar já, com os commits caindo na V3). Merge só do Matheus.

Categoria: implementacao. Trilha: **L (layout)**, missão proposta **L4**, depois da L1 (a M7 do layout).
Origem: Matheus, 2026-10-30: implementar o mapa 3D do POC `poc/mapa_ac` (PR #480) como o habitat do pet no layout do site, com o
pet 2D pixelado dentro do mundo 3D, como no Paper Mario. No mesmo dia, o Matheus decidiu que a frente vai para a V3 e respondeu as
decisões H-1, H-2, H-4 e H-6 (seção 8).

## 0. Prompt mestre (colar numa sessão nova do Claude Code, em `D:\Trab\digilab`)

> Você é o Gerente da frente **habitat ilha 3D** do Digilab, missão L4 da trilha L da V3. Leia, nesta ordem: `CLAUDE.md`,
> `web/app/CLAUDE.md`, `docs/PLANO_V3.md`, este documento (`docs/TAREFA_V3_HABITAT_ILHA_3D.md`), `docs/TAREFA_V2_LAYOUT_HABITAT.md`
> (as regras do habitat em tela cheia), o POC em `web/app/poc/mapa_ac/` e o habitat de hoje: `src/componentes/Habitat.tsx`,
> `src/telas/pet/CenarioPet.tsx`, `cena3d.ts`, `vistaMundo.ts`, `cenaEstado.ts`, `MundoReserva.tsx`, `PalcoPet.tsx`, `PorRacao.tsx`
> e `src/atlas.ts`.
>
> **O objetivo:** a cena do modo mundo (pets v12) passa a ser uma ilha 3D com a cara do Animal Crossing, como no POC. O pet aparece
> como um recorte de papel em pé no mundo. Tudo isso é **só vista**: o motor, o log, o replay e a paridade não mudam.
>
> **Antes de qualquer código:** confirme que o PR #480 (o POC) e a L1 (a M7 do layout, PR #477) estão na `main`. As decisões H-1,
> H-2, H-4 e H-6 já foram tomadas (seção 8): não pergunte de novo. Leve ao Matheus só a H-3 e a H-5, se ainda quiser confirmá-las,
> e o plano da missão H1b (ligar o `CLIPES_UP`), que muda o jogo fora do habitat.
>
> **Depois:** despache as missões da seção 6 na ordem da seção 6.1, uma worktree e um PR por missão. Confira cada PR contra os
> critérios da seção 7. O relato vai no corpo do PR, e a linha do painel vai no painel da V3.
>
> **Pare e avise** se um teste de replay, de paridade ou o G-FRONTEIRA quebrar, ou se alguma missão precisar mudar o motor.

## 1. Pergunta

**A pergunta:** o habitat do produto ganha a cara de uma ilha do Animal Crossing sem mudar o jogo?
- É uma tarefa de produto (`docs/PRODUTO_VISAO.md`), sem hipótese de pesquisa. É a P3 do `docs/futuro/mundo_3d.md` levada ao jogo.
- A física continua no motor, em inteiros, e o three só desenha (W-1, decidida em 2026-10-18).
- A exceção é a H1b: ligar o `CLIPES_UP` (decisão H-4) muda a animação do Digimon em todo o jogo, não só no habitat. Continua sendo
  vista (o motor não muda), mas tem missão, PR e capturas próprios.

## 2. Depende de

- O PR #480 (o POC `poc/mapa_ac`) na `main`. Em 2026-10-30 ele estava **aberto**.
- A L1 da V3 (a M7 do layout habitat, PR #477) na `main`. Em 2026-10-30 ela estava **aberta**. Esta frente não mexe em `App.tsx`,
  `Nav.tsx`, `PainelTela.tsx`, `tokens.css` nem nos menus. Se a L2 (o tema dos menus) estiver aberta, combinar com ela quem regenera
  as capturas.
- As decisões da seção 8 (H-1, H-2, H-4 e H-6 respondidas; H-3 e H-5 com a recomendação valendo).

## 3. O que já existe

### 3.1 O POC (PR #480), a referência visual

`web/app/poc/mapa_ac.html` e `poc/mapa_ac/{mapa,cena,heroi,pagina}.ts`. Roda com `npm run poc` e o endereço `/mapa_ac.html`.

**O que ele mostra (validado a 60 fps no Chrome do desktop, com ~56 draw calls):**

| peça | onde está no POC | o que leva para o habitat |
|---|---|---|
| mundo curvo | `cena.ts`, `curvar()` e `GLSL_PROJETAR` | a dobra em z centrada no foco, num uniform global, em todos os materiais (inclusive a água e as sombras) |
| terreno com degraus | `cena.ts`, `terreno()` e `parede()` | o tampo por célula, as paredes com faixas de estrato e a borda de grama, a rampa por alturas de canto |
| água | `cena.ts`, `agua()` | a margem por busca em largura, a espuma, a cachoeira e o mar além do mapa |
| modelos dos kits | `cena.ts`, `MODELOS` e `objetos()` | o `InstancedMesh` por peça, o material toon de 3 tons, o vento nas folhagens, a altura alvo por modelo |
| sombras redondas | `cena.ts`, `materialSombra()` | as "bolhas" do AC, instanciadas |
| céu | `cena.ts`, `ceu()`, `nuvens()` e a névoa | o degradê, as nuvens e a névoa da cor do horizonte |
| pet em papel | `heroi.ts` | a borda branca de 1 texel, a virada de folha, o pulinho, a silhueta atrás das árvores, a sombra semitransparente do export que sai |

**O que o POC não tem e o habitat precisa:**
- **O pet é do motor:** no POC o personagem anda pelo teclado; no produto, quem anda é o motor.
- **A grade vem do layout do motor:** o mapa do POC é inventado; o do habitat sai do `LayoutMundo`.
- **O contrato `CENA`:** passar da tela ao mapa (o "Pôr ração") e do mapa à tela (o `PalcoPet`).
- **Dia e noite.**
- **Os itens do mundo:** ração, fruta, bola, ninho e comedouro.
- **A reserva sem WebGL.**
- **Os testes e2e.**

### 3.2 Os kits 3D (CC0)

Estão em `D:\Trab\digilab\Assets\kits3d\`, fora do git. Hoje só o dev do POC os serve.

| kit | fonte | o POC usa | nesta frente |
|---|---|---|---|
| Quaternius, Stylized Nature MegaKit (Standard, grátis) | quaternius.itch.io/stylized-nature-megakit | `CommonTree_1..5`, `Pine_1/2/3/5`, `Bush_Common(_Flowers)`, `Flower_3/4_*`, `Clover_1/2`, `Grass_*` | entra |
| KayKit, Forest Nature Pack (FREE) | kaylousberg.itch.io/kaykit-forest | `Rock_1/2/3_A`, `Bush_1/2_A` (as árvores dele parecem cogumelos: não usar) | entra |
| Kenney, Nature Kit 2.1 | opengameart.org/content/nature-kit | `stump_round`, `stump_oldTall`, `log_large` (saem rosados) | **sai** (H-6) |

**O tamanho (medido em 2026-10-30):** os modelos que o POC usa somam ~15 MB crus, com os `.bin` e as texturas. A maior parte são
texturas do Quaternius:
- `Bark_NormalTree_Normal.png`, com 4,4 MB: o material toon do POC passa só o `map`, então o mapa normal não é usado e não entra;
- `Bark_NormalTree.png`, com 3,9 MB, e `Leaves.png`, com 2,6 MB: precisam ser reduzidas (por exemplo a 512 px) para caber no
  orçamento de 8 MB da H-1.

### 3.3 O habitat de hoje (o que muda e o que fica)

- **A casca** (`Habitat.tsx`): fica montada em todas as rotas menos a luta; `CenaPet` (3D, ou a reserva) e `PalcoPet` por cima.
- **O modo mundo** (`cena3d.ts`, `montarMundo` e `sincronizarMundo`):
  - câmera ortográfica a 50°;
  - uma janela de 16 × 12 células que segue o pet (`vistaMundo.ts`, `janelaEm` e `Seguidor`);
  - chão por região em caixas sem luz;
  - pet em `THREE.Sprite` com um número inteiro de pixels por texel.

  **É isto que a ilha substitui.**
- **O mapa do motor** (`motor/constantes.ts`, `CMU`/`CMU_MVP` e `LAYOUT_MUNDO_PADRAO`/`LAYOUT_MUNDO_MVP`):
  - 64 × 30 células de 16 subunidades;
  - regiões por faixa de x: casa 0–15, jardim 16–33, campo 34–47, mata 48–63;
  - o ninho em (4, 15), o comedouro em (10, 15) e a bola no início em (40, 15);
  - as árvores do layout (o MVP não tem nenhuma).

  **O chão é plano e o motor não sabe de penhasco nem de água.**
- **O contrato `CENA`** (`cenaEstado.ts`), que fica igual:
  - `modo3d`, `modoMundo` e `ret` (o retângulo do pet na tela, para o `PalcoPet`);
  - `medir` (a M3, em `?medir3d=1`);
  - `mundo.paraMundo`, `mundo.paraTela` e `mundo.pet`;
  - os e2e o leem por `window.__digilab.cena()` e `cenaPara()` (`src/main.tsx`).
- **A sala (pets v1–v11):** fica como está (H-2).
- **O atlas de clipes:** `src/atlas.ts` tem `CLIPES_UP = false` (linha 10). Com a chave ligada, `carregarAtlas` carrega também o
  atlas de clipes (`ATLAS_CLIPES_URL`), e `evolucaoUp.ts` passa a ter mais que o Idle. A H1b liga a chave (H-4).

## 4. Regras desta frente (além das do `CLAUDE.md` e das regras de todas as missões da V3)

1. **O motor não muda.** Nada em `web/app/motor/` nem no Python. Replay, paridade e gabaritos intactos. Se uma missão concluir que
   precisa de terreno com altura ou água no motor, isso é pesquisa (P4, com plano), não esta frente: parar e avisar.
2. **A vista só lê o motor**, como hoje (`useJogo()` e `jogoAtual()`). Câmera, interpolação, vento e animações ficam fora do log.
3. **G-FRONTEIRA:** as telas não importam `poc/`. O código do POC é copiado e adaptado para `src/telas/pet/ilha/`. O POC fica
   como está, como referência.
4. **O three só entra por import dinâmico**, num chunk próprio, como hoje. O bundle inicial do app não cresce.
5. **A área andável é plana e livre.**
   - O retângulo de 64 × 30 células do motor é o chão da ilha no nível 0, e nada dentro dele bloqueia a vista do caminho.
   - Dentro dele só entra decoração baixa que o pet atravessa sem estranheza: flor, trevo, tufo de grama, caminho de terra pintado
     no chão, e nada mais alto que ~0,5 célula.
   - Árvores, pedras, tocos e cercas dentro da área só onde o motor tem um objeto (as `arvores` do layout).
   - Penhascos, rio, lagoas, mar, cachoeira e mata densa ficam **na moldura fora da área andável**. O pet nunca aparece andando
     sobre a água nem atravessando um tronco.
6. **O mundo curvo não pode quebrar o contrato.**
   - `paraTela` aplica a mesma dobra do shader.
   - `paraMundo` inverte a dobra: a interseção do raio da câmera com a superfície `y = -k(z - foco)²` é uma equação do segundo
     grau em t, sem iteração. Devolve subunidades inteiras dentro do mapa, ou `null`.
   - `ret` é o retângulo do papel do pet, já dobrado.
   - Um teste de unidade confere a ida e volta: `paraMundo(paraTela(p)) == p`, com até 1 subunidade de diferença, em pontos do
     mapa todo.
7. **O pet em papel usa o atlas do jogo** (`src/atlas.ts`: `desenharSprite`, `quadroAgora`, `chaveSprite`, `OVO`), com o que o
   sprite de hoje já respeita: o ovo ao nascer, a forma sombria, o olho fechado ao dormir, a grade de reserva sem o atlas (e2e e
   capturas).
   - **O atlas do UP desenha os Digimon olhando para a direita:** confira pelo rabo, não pela cabeça (foi o erro do POC, corrigido
     no #480).
   - O lado do papel vem da direção em que a posição interpolada do pet anda em x na tela.
   - "Andando" quer dizer que a posição do motor mudou nos últimos ticks; andando, o papel usa o clipe Run (H-4); parado, o Idle.
   - Um sprite sem o clipe Run usa o Idle com o pulinho. Sem o atlas de clipes, com a chave ligada, vale o `atlas.ts`: o aviso visível do
     atlas, nunca a queda calada, e o papel usa a grade de reserva, como as outras telas.
8. **O tamanho do pet na tela continua um número inteiro de pixels por texel.** A câmera segue o pet a uma distância fixa, então
   o tamanho dele na tela é constante. Escolha o tamanho do texel no mundo para que, na distância do foco, um texel dê um número
   inteiro de pixels do canvas, e recalcule ao redimensionar. A M2 do POC-01 conferia isso pixel a pixel; a regra continua.
9. **O layout habitat continua valendo** (`TAREFA_V2_LAYOUT_HABITAT.md`, seção 3):
   - o habitat ocupa a tela inteira e nada cobre o pet;
   - com um painel aberto à direita (≥ 900 px), o enquadramento desloca o foco para o pet ficar na parte visível, à esquerda;
   - o véu (`habitat-veu`) continua;
   - dock, painéis, chamado, balão e DigiBrain continuam por cima, sem mudança.
10. **Acessibilidade e desempenho:**
    - com `prefers-reduced-motion`, sem vento, sem a ondulação da água, sem o pulinho e sem a virada animada (a troca de lado é
      instantânea); o clipe Run continua, como no resto do jogo;
    - a cena continua `aria-hidden`;
    - a meta é 60 fps no desktop e ≥ 30 fps num celular médio, medidos pela M3 (`?medir3d=1`);
    - se a média ficar abaixo de 30 fps por 3 s, a qualidade cai sozinha: sem vento, menos grama e `pixelRatio` 1 (PROPOSTO).
11. **Sem WebGL, ou se a cena falhar:** fica a `MundoReserva` de hoje, sem mudança.
12. **Os números da vista** (dobra, câmera, alturas, cores, tamanhos dos modelos) são do desenho: PROPOSTO, SEM FONTE. Ficam num
    só módulo de constantes da ilha, comentados.
13. **Nomes Digimon na tela,** português do Brasil e sem caractere japonês. Nenhum texto novo na tela, salvo o crédito dos kits.

## 5. A ilha a partir do layout do motor

A grade da ilha é uma função pura do `LayoutMundo` e da `ConfigMundo`, sem three e sem DOM (`ilha/grade.ts`). Mesmo layout, mesma
ilha; a semente da decoração sai do nome do layout. Uma célula do motor vale uma unidade do mundo 3D, e uma subunidade vale `1 / sub`.

**A área andável (nível 0), por região:**

| região | a cara | o que entra |
|---|---|---|
| casa (0–15) | o quintal | grama aparada, um caminho de terra até o ninho e o comedouro; o ninho como um ninho de folhas no chão; o comedouro como uma tigela; uma cerca baixa só na moldura |
| jardim (16–33) | o canteiro | flores em grupos e trevos; as árvores frutíferas do layout (`arvores` com id `J*`), com as frutas que o motor diz |
| campo (34–47) | o gramado aberto | grama alta esparsa; nenhum objeto alto (é onde a bola corre) |
| mata (48–63) | a borda da floresta | a grama mais escura, samambaias e cogumelos baixos; as árvores do layout (`M*`) onde o motor as tem |

**A moldura (fora da área andável, só desenho), pelo menos 8 células em cada lado:**

- **Norte** (o fundo da tela): o penhasco sobe para um platô (nível 1) e para um morro (nível 2) atrás, com pinheiros e árvores
  redondas. Uma cachoeira desce do platô para um rio que corre pela moldura leste.
- **Leste:** o rio e a mata densa.
- **Oeste:** o platô com a lagoa. Sem casa do jogador (H-5).
- **Sul** (a frente da câmera): uma faixa de areia e o mar, que continua até o horizonte.
- **Na borda do mapa do motor:** o pé do penhasco ou a margem da areia. O pet para ali porque o motor o prende, e a vista mostra
  um limite que faz sentido.
- **Sem o Kenney** (H-6): tocos e tronco deitado saem do Quaternius; o tronco deitado só entra se ficar bom.

**Os itens do mundo** (`sincronizarMundo`, com o mesmo trabalho de hoje):
- **Ração:** um montinho, madura e podre com cores diferentes.
- **Fruta no chão:** o modelo da fruta do tipo `a`, `b` ou `c`.
- **Bola:** a bola.
- **Todos** entram e saem como hoje e ganham a sombra redonda.

**Dia e noite:**
- `eNoite(tick % TPD)` escurece o céu, a névoa e a luz.
- Uma luz fraca no ninho à noite (PROPOSTO).
- Sem ciclo contínuo nesta frente.

## 6. Missões

Um PR por missão, cada uma na worktree `D:\Trab\digilab\v3-habitat-ilha-<missão>`, de `origin/main`.

- **H0 · Tarefa (Gerente):** este documento em `docs/TAREFA_V3_HABITAT_ILHA_3D.md`, com as decisões da seção 8; a L4 no
  `docs/PLANO_V3.md` e uma linha no painel da V3. Sem código.
- **H1 · Kits no produto:**
  - os modelos escolhidos (só os usados, sem o Kenney) em `web/app/public/kits3d/`, com as licenças de cada kit ao lado (H-1);
  - um script `scripts/kits3d_copiar.py` (Python com o Pillow, como os geradores do `Assets/`) que copia de `Assets/kits3d/`, deixa de fora os mapas normais, reduz as texturas grandes
    e falha se o total passar de **8 MB**;
  - o crédito em Ajustes › Sobre, junto do crédito dos sprites;
  - `ilha/modelos.ts` (a tabela `MODELOS` do POC sem o Kenney, o carregador e a normalização da altura) com teste de unidade da
    tabela;
  - sem mudança na cena.
- **H1b · Ligar o `CLIPES_UP` (H-4):**
  - antes do código, o Gerente confere com o Matheus onde o atlas de clipes mora (fora do git, como o atlas do UP) e o que acontece
    no build público e nos e2e sem ele;
  - `CLIPES_UP = true` em `src/atlas.ts`; nenhuma outra mudança de comportamento;
  - conferir cada lugar que usa os clipes (`evolucaoUp.ts`, a sala, a luta, a evolução) e o aviso visível sem o atlas de clipes (o `atlas.ts` nunca cai calado no atlas atual);
  - `npm run tipos`, `npm test` e `npm run e2e` passando; replay e paridade intactos (a chave é só vista);
  - capturas 390 e 1280, claro e escuro, das telas que mudam, para o Matheus aprovar; as referências de `e2e_capturas` regeneradas
    só depois da aprovação, combinando com a L2 se ela estiver aberta.
- **H2 · A ilha:**
  - `ilha/grade.ts` (a seção 5, com testes de unidade: mesma entrada, mesma grade; nada que bloqueie dentro da área andável; a
    borda do mapa casa com o pé do penhasco e com a areia);
  - `ilha/curva.ts` (a dobra, `paraTela`, `paraMundo` e a ida e volta da regra 6, com testes);
  - `ilha/cena.ts` (terreno, água, céu, objetos instanciados, dia e noite);
  - em `cena3d.ts`, o modo mundo passa a montar a ilha, com câmera em perspectiva, foco no pet pelo `Seguidor`, e a dobra
    centrada nele (os números da H-3);
  - o contrato `CENA` igual;
  - a sala dos v1–v11 sem mudança (H-2).
- **H3 · O pet em papel:**
  - `ilha/papel.ts` (o `heroi.ts` do POC adaptado à regra 7 e à regra 8): o papel com borda, a virada, o pulinho, a silhueta atrás
    das árvores, a sombra;
  - o clipe Run quando o pet anda e o Idle quando para (H-4, com a H1b na `main`); um sprite sem o Run, o Idle com o pulinho;
  - o `ret` e os extras do `PalcoPet` (sujeira, ícone rápido, saúde) no lugar certo.
- **H4 · Itens, interação e enquadramento:**
  - ração, fruta, bola, ninho e comedouro (seção 5);
  - o "Pôr ração" (arrastar e soltar) pelo `paraMundo` dobrado;
  - o enquadramento com o painel aberto (regra 9);
  - `prefers-reduced-motion` e a queda de qualidade (regra 10).
- **H5 · Fechamento:**
  - os e2e de hoje passando (`.cena3d canvas`, `__digilab.cena()`, `cenaPara`, a reserva sem WebGL), mais um e2e novo: soltar a
    ração num ponto da tela e conferir no motor a posição dentro de 1 célula;
  - a medida M3 em 1280 px e em 390 px, com o resultado no PR;
  - capturas 390 e 1280 nos temas claro e escuro, para o Matheus aprovar (inclusive a H-3 e a H-5);
  - só depois da aprovação, as referências de `e2e_capturas` regeneradas.

### 6.1 Ordem e arquivos

**A ordem:** H0 → H1 e H1b em paralelo → H2 → H3 e H4 em paralelo → H5. A H3 só começa com a H1b na `main`.

**Quem toca o quê:**
- H1 é dona de `public/kits3d/`, `scripts/kits3d_copiar.py`, `ilha/modelos.ts` e do crédito em Ajustes › Sobre.
- H1b é dona de `src/atlas.ts` e das capturas que a chave muda. Não toca em `cena3d.ts` nem em `ilha/`.
- H2 é dona de `cena3d.ts` e de `ilha/{grade,curva,cena}.ts`.
- H3 é dona de `ilha/papel.ts` e só chama o papel de dentro de `cena3d.ts` numa função combinada com a H2.
- H4 é dona de `PorRacao.tsx`, `vistaMundo.ts` e do enquadramento.
- Arquivos de uma missão por vez: `cena3d.ts`, `cenaEstado.ts`, `PalcoPet.tsx`, e as referências de `e2e_capturas` (H1b, H5 e a L2).

## 7. Critérios de aceitação (no fim da H5)

- Com um pet v12, a tela Pet em 360, 390 e 1280 px mostra a ilha:
  - chão curvo, penhascos com estrato, água com espuma, céu e névoa;
  - o pet em papel sobre a área andável, seguido pela câmera;
  - nada cobrindo o pet;
  - dock, painéis, balão, chamado e DigiBrain por cima, como hoje.
- Com um painel aberto (≥ 900 px), o pet fica visível à esquerda.
- O pet olha para o lado em que anda, com o clipe Run andando e o Idle parado; dorme de olho fechado; aparece como ovo ao nascer;
  a forma sombria aparece.
- Ração, fruta, bola, ninho e comedouro aparecem onde o motor diz. Soltar a ração cai no ponto (e2e, 1 célula de folga).
- Nenhuma árvore, pedra, tronco ou água dentro da área andável, salvo os objetos do layout do motor (teste de unidade da grade).
- Nenhum modelo do Kenney.
- `paraMundo(paraTela(p)) == p` com até 1 subunidade de diferença (teste de unidade).
- Sem WebGL: a `MundoReserva`. Pets v1–v11: a sala.
- Desempenho: M3 com ≥ 55 fps em 1280 px no desktop e ≥ 30 fps em 390 px num celular, com a medida colada no PR.
- Com `prefers-reduced-motion`: nada balança nem ondula.
- `npm run tipos`, `npm test` (com o G-FRONTEIRA e a paridade) e `npm run e2e` passando; `e2e_capturas` regenerado depois da
  aprovação do Matheus.
- O crédito dos kits em Ajustes › Sobre. As licenças ao lado dos arquivos em `public/kits3d/`, e o total em ≤ 8 MB.
- O bundle inicial do app sem o three (o chunk da cena continua separado).
- O `CLIPES_UP` ligado na `main` (H1b), sem quebrar replay, paridade nem os e2e.

## 8. Decisões do Matheus

| # | decisão | resposta | data | o que muda |
|---|---|---|---|---|
| H-1 | os kits CC0 entram no git? | **sim**, só os modelos usados, em `web/app/public/kits3d/`, com as licenças, em **≤ 8 MB**; o crédito em Ajustes › Sobre | 2026-10-30 | a H1 versiona os modelos; sem o mapa normal e com as texturas grandes reduzidas (seção 3.2) |
| H-2 | os pets v1–v11 (a sala) também ganham a ilha? | **não**: a ilha é só do modo mundo (v12) | 2026-10-30 | a sala fica como está |
| H-3 | a força da dobra e o ângulo da câmera | não perguntada; vale a recomendação: o do POC (dobra 0,011; câmera 8,4 acima e 14,5 atrás; FOV 32°), aprovado pelas capturas da H5 | — | só visual; ajuste barato depois |
| H-4 | o clipe Run (o atlas de clipes, a chave `CLIPES_UP`) no papel | **ligar o `CLIPES_UP`** (a recomendação era o Idle com o pulinho) | 2026-10-30 | a chave muda o jogo todo (evolução, luta, sala e capturas), então ganha a missão própria H1b antes da H3 |
| H-5 | uma casa do jogador na moldura oeste | não perguntada; vale a recomendação: **não** agora (nenhum kit grátis tem uma com a cara do AC) | — | a moldura oeste é o platô com a lagoa |
| H-6 | o Kenney (tocos e tronco) | **sair**: trocar por modelos do Quaternius; o tronco deitado só se ficar bom | 2026-10-30 | o Kenney não entra em `public/kits3d/` nem no crédito |

## 9. Fora desta tarefa

- **Mudar o motor:** terreno com altura, água ou obstáculos de verdade. Isso é a P4 da pesquisa, com plano próprio.
- **O jogador controlar o pet:** o teclado e o arrastar do POC não vão para o produto; o pet é autônomo.
- **Os outros 3D:** o mapa da Exploração (`src/telas/lutar/mapa3d.ts`), a luta e a cena de evolução. A H1b liga os clipes nelas,
  mas não muda o desenho delas.
- **Câmera e ciclo:** câmera giratória, zoom do jogador e ciclo dia/noite contínuo.
- **Outras artes e efeitos:** som novo, casa do jogador (H-5) e vizinhos e NPCs na ilha.
- **O POC `poc/mapa_ac`:** continua como referência e não muda.

## 10. Resultado (2026-10-30, Gerente e worker na mesma sessão, Claude Code, Opus 5.5)

Um branch por missão na worktree `v3-habitat-ilha`, cada um a partir do anterior: `v3-habitat-ilha-h0`, `-h1`, `-h1b`, `-h2`, `-h3`,
`-h4` e `-h5`. Nenhum foi enviado ao GitHub ainda; os PRs esperam o ok do Matheus. Os desvios e os números escolhidos estão em
`docs/registro/2026-10.md` (HABITAT-ILHA, H0 a H5).

| critério (seção 7) | estado |
|---|---|
| a ilha em 360, 390 e 1280 px, com o pet em papel seguido pela câmera e nada cobrindo o pet | feito; capturas 390 e 1280 (claro, escuro e noite) fora do git, em `D:\Trab\digilab\capturas_ilha_h5\`, para a aprovação |
| painel aberto (≥ 900 px): o pet visível à esquerda | feito: o habitat encolhe à direita e a câmera segue o pet no que sobra |
| o lado, o Run ao andar, o olho fechado (reserva) ao dormir, o ovo, a forma sombria | feito no `ilha/papel.ts`; o andar e a virada não foram vistos na tela (o pet do save estava parado) |
| ração, fruta, bola, ninho e comedouro onde o motor diz; soltar a ração cai no ponto | feito; e2e novo em 390 e 1280, com 1 célula de folga |
| nada alto dentro da área andável, salvo as árvores do motor | teste de unidade (`test/ilha_grade.test.ts`) |
| `paraMundo(paraTela(p)) == p` com até 1 subunidade | teste de unidade (`test/ilha_curva.test.ts`), até o horizonte da dobra |
| sem WebGL, a `MundoReserva`; os v1 a v11, a sala | os e2e de antes passam |
| M3 ≥ 55 fps (1280, desktop) e ≥ 30 fps (390, celular) | **não medida**: o navegador do app limita a 30 Hz. Falta o Matheus medir com `?medir3d=1` |
| movimento reduzido: nada balança nem ondula | feito (o tempo do shader parado, sem pulinho e sem virada animada); não conferido na tela |
| `npm run tipos`, `npm test`, `npm run e2e` | passam: 617 testes de unidade e 99 e2e (os 97 de antes e os 2 novos) |
| `e2e_capturas` regenerado | **não**: só depois da aprovação das capturas (H1b e H5) |
| o crédito dos kits em Ajustes › Sobre, as licenças ao lado, ≤ 8 MB | feito; 6,67 MB |
| o bundle inicial sem o three | conferido no build: o three fica em `three.module-*.js`, carregado só pelo `cena3d` |
| o `CLIPES_UP` ligado sem quebrar replay, paridade nem e2e | feito na H1b (97 e2e e 606 testes de unidade passaram nela) |
