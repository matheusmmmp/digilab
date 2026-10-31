# Tarefa V2 — o habitat como ilha 3D no estilo Animal Crossing, com o pet em papel (2026-10-30)

Gerente: a sessão que abrir esta tarefa. Worker: um por missão. Worktree e branch: `v2-habitat-ilha-<missão>`, de `origin/main`.
Status: ABERTA. Merge só do Matheus.

Categoria: implementacao. Origem: Matheus, 2026-10-30: implementar o mapa 3D do POC `poc/mapa_ac` (PR #480) como o habitat do pet
no layout do site, com o pet 2D pixelado dentro do mundo 3D, como no Paper Mario.

## 0. Prompt mestre (colar numa sessão nova do Claude Code, em `D:\Trab\digilab`)

> Você é o Gerente da frente **habitat ilha 3D** do Digilab. Leia, nesta ordem: `CLAUDE.md`, `web/app/CLAUDE.md`, este documento
> (`docs/TAREFA_V2_HABITAT_ILHA_3D.md`), `docs/TAREFA_V2_LAYOUT_HABITAT.md` (as regras do habitat em tela cheia), o POC em
> `web/app/poc/mapa_ac/` e o habitat de hoje: `src/componentes/Habitat.tsx`, `src/telas/pet/CenarioPet.tsx`, `cena3d.ts`,
> `vistaMundo.ts`, `cenaEstado.ts`, `MundoReserva.tsx`, `PalcoPet.tsx` e `PorRacao.tsx`.
>
> **O objetivo:** a cena do modo mundo (pets v12) passa a ser uma ilha 3D com a cara do Animal Crossing, como no POC. O pet aparece
> como um recorte de papel em pé no mundo. Tudo isso é **só vista**: o motor, o log, o replay e a paridade não mudam.
>
> **Antes de qualquer código:** confirme que o PR #480 está na `main`. Leve ao Matheus as decisões da seção 8 que ainda estiverem
> abertas, cada uma com a recomendação e o custo de errar, e espere a resposta.
>
> **Depois:** despache as missões da seção 6 na ordem da seção 6.1, uma worktree e um PR por missão. Confira cada PR contra os
> critérios da seção 7. O relato vai no corpo do PR, e a linha do painel vai no `docs/PAINEL_V2.md`.
>
> **Pare e avise** se um teste de replay, de paridade ou o G-FRONTEIRA quebrar, ou se alguma missão precisar mudar o motor.

## 1. Pergunta

**A pergunta:** o habitat do produto ganha a cara de uma ilha do Animal Crossing sem mudar o jogo?
- É uma tarefa de produto (`docs/PRODUTO_VISAO.md`), sem hipótese de pesquisa. É a P3 do `docs/futuro/mundo_3d.md` levada ao jogo.
- A física continua no motor, em inteiros, e o three só desenha (W-1, decidida em 2026-10-18).

## 2. Depende de

- O PR #480 (o POC `poc/mapa_ac`) na `main`.
- O layout habitat (`docs/TAREFA_V2_LAYOUT_HABITAT.md`) até a M3 na `main`. Esta frente não mexe em `App.tsx`, `Nav.tsx`,
  `PainelTela.tsx`, `tokens.css` nem nos menus. Se a M7 do layout estiver aberta, combinar com ela quem regenera as capturas.
- As decisões H-1 a H-6 da seção 8.

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

| kit | fonte | o POC usa |
|---|---|---|
| Quaternius, Stylized Nature MegaKit (Standard, grátis) | quaternius.itch.io/stylized-nature-megakit | `CommonTree_1..5`, `Pine_1/2/3/5`, `Bush_Common(_Flowers)`, `Flower_3/4_*`, `Clover_1/2`, `Grass_*` |
| KayKit, Forest Nature Pack (FREE) | kaylousberg.itch.io/kaykit-forest | `Rock_1/2/3_A`, `Bush_1/2_A` (as árvores dele parecem cogumelos: não usar) |
| Kenney, Nature Kit 2.1 | opengameart.org/content/nature-kit | `stump_round`, `stump_oldTall`, `log_large` (saem rosados: trocar ou recolorir) |

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
- **A sala (pets v1–v11):** fica como está, salvo decisão H-2.

## 4. Regras desta frente (além das do `CLAUDE.md`)

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
   - "Andando" quer dizer que a posição do motor mudou nos últimos ticks.
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
      instantânea);
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
- **Oeste:** o platô com a lagoa e a casa do jogador, se a H-5 a aprovar.
- **Sul** (a frente da câmera): uma faixa de areia e o mar, que continua até o horizonte.
- **Na borda do mapa do motor:** o pé do penhasco ou a margem da areia. O pet para ali porque o motor o prende, e a vista mostra
  um limite que faz sentido.

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

Um PR por missão, cada uma na worktree `D:\Trab\digilab\v2-habitat-ilha-<missão>`, de `origin/main`.

- **H0 · Tarefa (Gerente):** este documento com as decisões da seção 8 preenchidas; uma linha no `docs/PAINEL_V2.md`. Sem código.
- **H1 · Kits no produto:**
  - os modelos escolhidos (só os usados) em `web/app/public/kits3d/` ou fora do git, conforme a H-1;
  - um script `scripts/kits3d_copiar.mjs` que copia de `Assets/kits3d/` e confere o orçamento de tamanho;
  - os arquivos de licença de cada kit ao lado;
  - o crédito em Ajustes › Sobre, junto do crédito dos sprites;
  - `ilha/modelos.ts` (a tabela `MODELOS` do POC, o carregador e a normalização da altura) com teste de unidade da tabela;
  - sem mudança na cena.
- **H2 · A ilha:**
  - `ilha/grade.ts` (a seção 5, com testes de unidade: mesma entrada, mesma grade; nada que bloqueie dentro da área andável; a
    borda do mapa casa com o pé do penhasco e com a areia);
  - `ilha/curva.ts` (a dobra, `paraTela`, `paraMundo` e a ida e volta da regra 6, com testes);
  - `ilha/cena.ts` (terreno, água, céu, objetos instanciados, dia e noite);
  - em `cena3d.ts`, o modo mundo passa a montar a ilha, com câmera em perspectiva, foco no pet pelo `Seguidor`, e a dobra
    centrada nele;
  - o contrato `CENA` igual;
  - a sala dos v1–v11 sem mudança.
- **H3 · O pet em papel:**
  - `ilha/papel.ts` (o `heroi.ts` do POC adaptado à regra 7 e à regra 8): o papel com borda, a virada, o pulinho, a silhueta atrás
    das árvores, a sombra;
  - o clipe Run do atlas de clipes só se a chave `CLIPES_UP` estiver ligada (decisão H-4); sem ela, o Idle com o pulinho;
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
  - capturas 390 e 1280 nos temas claro e escuro, para o Matheus aprovar;
  - só depois da aprovação, as referências de `e2e_capturas` regeneradas.

### 6.1 Ordem e arquivos

**A ordem:** H0 → H1 → H2 → H3 e H4 em paralelo → H5.

**Quem toca o quê:**
- H2 é dona de `cena3d.ts` e de `ilha/{grade,curva,cena}.ts`.
- H3 é dona de `ilha/papel.ts` e só chama o papel de dentro de `cena3d.ts` numa função combinada com a H2.
- H4 é dona de `PorRacao.tsx`, `vistaMundo.ts` e do enquadramento.
- Arquivos de uma missão por vez: `cena3d.ts`, `cenaEstado.ts`, `PalcoPet.tsx`.

## 7. Critérios de aceitação (no fim da H5)

- Com um pet v12, a tela Pet em 360, 390 e 1280 px mostra a ilha:
  - chão curvo, penhascos com estrato, água com espuma, céu e névoa;
  - o pet em papel sobre a área andável, seguido pela câmera;
  - nada cobrindo o pet;
  - dock, painéis, balão, chamado e DigiBrain por cima, como hoje.
- Com um painel aberto (≥ 900 px), o pet fica visível à esquerda.
- O pet olha para o lado em que anda; dorme de olho fechado; aparece como ovo ao nascer; a forma sombria aparece.
- Ração, fruta, bola, ninho e comedouro aparecem onde o motor diz. Soltar a ração cai no ponto (e2e, 1 célula de folga).
- Nenhuma árvore, pedra, tronco ou água dentro da área andável, salvo os objetos do layout do motor (teste de unidade da grade).
- `paraMundo(paraTela(p)) == p` com até 1 subunidade de diferença (teste de unidade).
- Sem WebGL: a `MundoReserva`. Pets v1–v11: a sala, salvo a H-2.
- Desempenho: M3 com ≥ 55 fps em 1280 px no desktop e ≥ 30 fps em 390 px num celular, com a medida colada no PR.
- Com `prefers-reduced-motion`: nada balança nem ondula.
- `npm run tipos`, `npm test` (com o G-FRONTEIRA e a paridade) e `npm run e2e` passando; `e2e_capturas` regenerado depois da
  aprovação do Matheus.
- O crédito dos kits em Ajustes › Sobre. As licenças ao lado dos arquivos, se versionados.
- O bundle inicial do app sem o three (o chunk da cena continua separado).

## 8. Precisa do Matheus

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| H-1 | os kits CC0 entram no git? | **sim**, só os modelos usados, em `web/app/public/kits3d/`, com as licenças, num orçamento de **≤ 8 MB** (a conferir na H1); o crédito em Ajustes › Sobre. São CC0, ao contrário do atlas do UP, e o build e os e2e ficam iguais em qualquer máquina | fora do git, o build público sai sem a ilha (só a reserva) e cada máquina precisa baixar os kits; dentro do git sem orçamento, o repositório incha |
| H-2 | os pets v1–v11 (a sala) também ganham a ilha? | **não** nesta frente: a sala fica, e a ilha é do modo mundo (v12) | levar a sala junto dobra o trabalho da H2 e mexe nas capturas dos pets antigos sem ganho para o MVP |
| H-3 | a força da dobra e o ângulo da câmera | o do POC (dobra 0,011; câmera 8,4 acima e 14,5 atrás; FOV 32°), aprovado pelas capturas da H5 | só visual; ajuste barato depois |
| H-4 | o clipe Run (o atlas de clipes, a chave `CLIPES_UP`) no papel | **sim** se a chave estiver ligada no jogo; senão, o Idle com o pulinho | ligar a chave só por isto mexe em todo o jogo; deixar sem o Run deixa o pet "deslizando" |
| H-5 | uma casa do jogador na moldura oeste | **não** agora (nenhum kit grátis tem uma com a cara do AC); fica para quando houver arte | inventar a casa em caixas destoa do resto |
| H-6 | o Kenney (tocos e tronco) | **sair**: recolorir ou trocar por modelos do Quaternius; o tronco deitado só se ficar bom | no POC eles saem rosados e chamam atenção |

## 9. Fora desta tarefa

- **Mudar o motor:** terreno com altura, água ou obstáculos de verdade. Isso é a P4 da pesquisa, com plano próprio.
- **O jogador controlar o pet:** o teclado e o arrastar do POC não vão para o produto; o pet é autônomo.
- **Os outros 3D:** o mapa da Exploração (`src/telas/lutar/mapa3d.ts`), a luta e a cena de evolução.
- **Câmera e ciclo:** câmera giratória, zoom do jogador e ciclo dia/noite contínuo.
- **Outras artes e efeitos:** som novo, casa do jogador (H-5) e vizinhos e NPCs na ilha.
- **O POC `poc/mapa_ac`:** continua como referência e não muda.
