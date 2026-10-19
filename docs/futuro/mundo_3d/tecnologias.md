# Mundo 3D, anexo 2: o estudo de tecnologias (WORLD-POC-001, investigação B)

Status: **INVESTIGAÇÃO FEITA; W-1 a W-7 DECIDIDAS em 2026-10-18** (worker A). Anexo de `docs/futuro/mundo_3d.md`. Pesos e notas são **PROPOSTOS**, sem fonte; o
Matheus decide.

**Regra das fontes:**
- cada fato técnico cita a página que foi aberta em 2026-10-18 (documentação oficial ou o registro do npm);
- onde a fonte não foi aberta, o texto diz **SEM FONTE** ou **(conhecimento do modelo, não verificado)**;
- nenhuma destas fontes é literatura científica; elas não entram em `docs/referencias/`.

## 1. A pergunta que decide antes da engine: onde mora a física

A auditoria (anexo 1, seção 6) mostra que o requisito mais forte não é gráfico. É o **determinismo com paridade Python/TS**: a pesquisa
roda no Python, e o jogo repete a mesma vida bit a bit no Node. Daí saem três arranjos:

| arranjo | o que é | o que acontece com a paridade |
|---|---|---|
| **V: vista 3D sobre o motor 2D** | a engine só desenha: a câmera, os sprites, as sombras e a oclusão. A física (colisão com parede, empurrão da bola) é **geometria inteira no motor** (`mundo.py` e `mundo.ts`), como o resto | mantida: nada de float novo no motor |
| **F: física da engine no TS** | um motor de física (Rapier) passa a ser a fonte da verdade do mundo, só no TS | **perdida para o Python:** a pesquisa do mundo teria de rodar no Node, ou o Python teria de carregar o mesmo wasm (SEM FONTE de que isso funcione bit a bit) |
| **G: a engine inteira (Godot)** | o mundo e o loop vão para outro runtime | perdida, e o motor TS também deixa de ser o do jogo |

O arranjo V é o que o `mundo_fisico.md` já decidiu (M-1 e a seção 2.6, "a vista é só desenho"). F e G reabrem a M-1 (seção 6 do
documento principal).

## 2. Os fatos, por opção

### 2.1 Three.js + Rapier

- **Licença:** Three.js é MIT ([LICENSE](https://raw.githubusercontent.com/mrdoob/three.js/dev/LICENSE)); Rapier JS é Apache-2.0
  ([github.com/dimforge/rapier.js](https://github.com/dimforge/rapier.js)).
- **Versões (registro do npm, `npm view`):**
  - `three` 0.186.1, MIT, atualizado em 2026-09-24;
  - `@dimforge/rapier3d-compat` 0.21.0, Apache-2.0, 2026-09-25 ("inlined webassembly as base64");
  - há também os pacotes `@dimforge/rapier3d-deterministic-compat` e `@dimforge/rapier2d-deterministic-compat` 0.21.0;
  - o último release do Three.js no GitHub é o r186 ([releases](https://github.com/mrdoob/three.js/releases)).
- **Manutenção:** o repositório `rapier.js` está **arquivado**. O README diz que o código "has been merged into the main Rapier
  repository", no diretório `typescript` ([github.com/dimforge/rapier.js](https://github.com/dimforge/rapier.js)).
- **Determinismo:**
  - a documentação diz que a versão WASM/JS "is fully cross-platform deterministic", com a mesma versão, as mesmas condições iniciais
    e os corpos criados na mesma ordem;
  - a conferência é pelo hash do `world.takeSnapshot()`;
  - transcendentais como `Math.sin` e `Math.cos` "may give different results on different platforms"
    ([rapier.rs, determinism](https://rapier.rs/docs/user_guides/javascript/determinism/)).
  - **Isso é determinismo entre aparelhos no JS, não paridade com o Python.**
- **Sprites:** "A sprite is a plane that always faces towards the camera", e "Sprites do not cast shadows"
  ([threejs.org, Sprite](https://threejs.org/docs/pages/Sprite.html)). A sombra no chão teria de ser um disco à parte, como no
  protótipo `mundo_fisico_vistas.html`.
- **Câmera ortográfica, filtro nearest e debug render do Rapier:** existem (conhecimento do modelo, não verificado).
- **Com a stack:** o Three.js é imperativo e cabe num `<canvas>` de um componente Preact, como o `PalcoPet.tsx` faz com o 2D. O
  react-three-fiber pede React; com Preact, só pelo `preact/compat` (SEM FONTE de que funcione).

### 2.2 Babylon.js + Havok

- **Licença e versões:**
  - `@babylonjs/core` 9.31.0, Apache-2.0, 2026-10-15;
  - `@babylonjs/havok` 1.3.14, MIT, 2026-09-07 (registro do npm);
  - "Havok is available free to use under the MIT license"
    ([doc.babylonjs.com, Havok plugin](https://doc.babylonjs.com/features/featuresDeepDive/physics/havokPlugin)).
- **Celular:** o Havok "requires WebAssembly SIMD, which is not supported on iOS < 16.4" (mesma página).
- **Determinismo:**
  - **não está na documentação oficial do plugin** (mesma página);
  - num fórum, um desenvolvedor do Babylon diz que o Havok dá o mesmo resultado para as mesmas entradas, mas não garante corpos iguais em
    lugares diferentes do mundo ([forum.babylonjs.com, havok-determinism](https://forum.babylonjs.com/t/havok-determinism/55364));
  - **SEM FONTE** para o determinismo entre aparelhos.
- **Sprites:** o `SpriteManager` desenha sprites no espaço 3D, e a profundidade em z muda o tamanho na tela. A página não fala de filtro
  nearest nem de ordenação ([doc.babylonjs.com, sprite manager](https://doc.babylonjs.com/features/featuresDeepDive/sprites/sprite_manager)).
- **Debug:** o Inspector (conhecimento do modelo, não verificado).
- **Tamanho:** o `@babylonjs/core` tem 71,8 MB desempacotados no npm. Isso não é o tamanho baixado; o tamanho do bundle é **Não
  verificado** para as três opções.

### 2.3 Godot 4 com exportação web

- **Licença:** "Godot Engine is free and open source software released under the permissive MIT license"
  ([godotengine.org/license](https://godotengine.org/license/)).
- **A exportação web**, pela documentação do Godot 4.7
  ([docs.godotengine.org, exporting for web](https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_web.html)):
  - pede WebAssembly e WebGL 2.0, e na web só o renderizador Compatibility; o WebGPU ainda não;
  - as threads são opcionais e, com elas, o `SharedArrayBuffer` e os cabeçalhos COOP e COEP; desde o 4.3, o padrão é uma thread só;
  - **projetos em C# do Godot 4 não exportam para a web**;
  - no celular, o desempenho é limitado, porque o WebAssembly é mais lento que o nativo.
- **Sprites:** o `Sprite3D` mostra uma textura 2D num ambiente 3D, com o modo billboard no `SpriteBase3D`
  ([docs.godotengine.org, Sprite3D](https://docs.godotengine.org/en/stable/classes/class_sprite3d.html)).
- **Com a stack:** o motor do jogo é TS (`web/app/motor/`). No Godot, o mundo rodaria no runtime dele, conversando pelo
  `JavaScriptBridge` (a página só aponta para outra; não verificado), ou o motor seria reescrito em GDScript. **Isso desfaz a arquitetura
  do jogo:** o motor TS sem DOM, o replay e a paridade.

### 2.4 Física 2D determinística, se a física ficar no plano

- `planck` 1.5.1, MIT, 2026-10-12 (registro do npm), uma física 2D em JS/TS;
- `@dimforge/rapier2d-deterministic-compat` 0.21.0, Apache-2.0;
- **as duas são de float.** Nenhuma reproduz bit a bit no Python sem portar a própria engine (SEM FONTE de um porte).

## 3. A matriz de decisão ponderada

As notas vão de 1 (ruim) a 5 (bom) e são **PROPOSTAS**: o julgamento do worker sobre os fatos da seção 2. Os pesos também, sem fonte.

**Duas leituras de cada engine:**
- **V** (só desenho, a física no motor): a física da engine fica de fora, e então Rapier e Havok não pesam;
- **F** (a física da engine).

| critério | peso | Three.js V | Three.js + Rapier F | Babylon V | Babylon + Havok F | Godot G |
|---|---|---|---|---|---|---|
| a stack (Preact, motor TS sem DOM, Vite) | 20 | 5 | 4 | 4 | 3 | 1 |
| o determinismo e a paridade Python/TS | 20 | 5 | 2 (só entre aparelhos no JS) | 5 | 1 (SEM FONTE oficial) | 1 |
| sprites, câmera inclinada, oclusão | 15 | 4 (o sprite não faz sombra) | 4 | 4 | 4 | 5 |
| a física de corpos rígidos e a navegação | 10 | 2 (a geometria inteira é nossa) | 5 | 2 | 5 | 4 |
| o celular e o tamanho | 10 | 4 | 3 (o wasm) | 3 | 2 (iOS ≥ 16.4 por causa do SIMD) | 2 (a doc diz que é limitado) |
| o debug | 5 | 3 | 4 | 4 | 5 | 3 |
| a licença | 10 | 5 (MIT) | 5 (MIT, Apache) | 5 (Apache) | 5 (Apache, MIT) | 5 (MIT) |
| o risco da dependência | 10 | 4 | 3 (o `rapier.js` foi arquivado e fundido; equipe pequena, SEM FONTE) | 4 | 4 | 4 |
| **total** (Σ peso × nota / 5) | 100 | **85** | 72 | 80 | 65 | 56 |

**Sem o critério da paridade** (peso 0, como se a pesquisa do mundo saísse do Python; os outros pesos reescalados para 100), os totais
ficam:

| Three.js V | Three.js + Rapier F | Babylon V | Babylon + Havok F | Godot G |
|---|---|---|---|---|
| 81,2 | 80,0 | 75,0 | 76,2 | 65,0 |

Sem a paridade, V e F empatam na prática: a escolha passa a depender do valor de ter física de verdade. O Godot continua atrás, pela
stack. A escolha entre V e F é a decisão W-1 do documento principal.

## 4. Recomendação (DECIDIDA em 2026-10-18: W-1 = V, W-2 = Three.js)

1. **Three.js como renderizador**, imperativo, num canvas dentro do Preact, sem react-three-fiber. Ele ganha pela stack (MIT, sem
   wasm na renderização, imperativo como o `PalcoPet`) e pela leveza.
2. **A física no motor, em inteiros (o arranjo V)**: paredes e obstáculos como retângulos, a colisão do círculo do pet com eles e o
   empurrão da bola com velocidade inteira e atrito, tudo em `mundo.py` e `mundo.ts`, com paridade. É mais trabalho que usar o Rapier,
   mas é a única opção que **não reabre** a M-1, o determinismo e a pesquisa no Python.
3. **O Rapier fica como experimento contido**, num POC-01b opcional (anexo 3): mede se a física de verdade traz algo que a geometria
   inteira não traz. Só vira arquitetura com a decisão W-1.
4. **Não ao Godot** nesta fase: ele desfaz o motor TS e a paridade, e o C# não exporta para a web.

## 5. Incertezas e o que o POC tem de medir

- os quadros por segundo e o tamanho do bundle do Three.js num celular médio: **Não verificado**; é a métrica M3 do POC;
- o filtro nearest e a borda do sprite em escala não inteira com a câmera inclinada: a nitidez do pixel art, métrica M2;
- a oclusão do sprite atrás de uma parede: a silhueta ou a transparência da parede; ver o modelo físico no documento principal;
- se o Rapier deterministic dá o mesmo hash do snapshot no Chrome do desktop e no do celular, como a documentação diz (só no POC-01b);
- **SEM FONTE:** o tamanho do wasm do Rapier e do Havok baixado (o npm mostra só o tamanho desempacotado, que não é o do bundle).
