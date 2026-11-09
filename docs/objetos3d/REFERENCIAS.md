# Retrabalho dos objetos do mapa: as referências (2026-11-07)

**O pedido:** o Matheus quer retrabalhar os objetos de 01 a 09 da vitrine, menos a lata (08), e também o barranco e o chão. Os nove
são o portão, a barraca, o cais, o poste, o carro, a geladeira, o trem e a bola. Antes de desenhar, ele pediu referências, primeiro
de modelos 3D e depois de jogos, partindo dos jogos que o projeto já usou de base.

**Como as referências são usadas:** só como estilo, forma e técnica. Nada é copiado (nenhum modelo, textura, mapa ou nome). Nenhuma
imagem de terceiros vai para gerador nenhum; o prompt leva só a descrição do estilo, em palavras.

## 1. Por que os objetos estão sem textura (o que nós fizemos)

- **O nosso processo apagou a textura.** Para deixar as cores lisas, o achatamento de cores das frentes LUGARES_3D, MUNDO_ENFEITES e
  ITENS_3D deixou cada textura da Meshy com poucas cores lisas:

  | objeto | cores na textura |
  |---|---|
  | portão | 7 |
  | barraca | 12 |
  | cais | 8 |
  | carro | 7 |
  | geladeira | 7 |
  | trem | 7 |
  | bola | 3 |

  O detalhe saiu junto: a pedra, as costuras, as portas, as rodas.
- **O prompt dos esboços pedia "cores chapadas, áreas lisas".** O ponto de partida já vinha pobre.
- **O toon de dois tons em malha facetada dá manchas.** A luz cai em cada face separadamente, e é isso que faz o trem parecer esquisito.
  O conserto das referências é suavizar as normais.
- **A bola:** a textura de 3 cores não bate com a malha nas emendas, e as falhas aparecem como manchas brancas.

## 2. Os jogos-base do projeto e o que tirar de cada um

- **Animal Crossing**, a ilha e a vista inclinada (`docs/TAREFA_V3_HABITAT_ILHA_3D.md`; `docs/futuro/mundo_fisico.md`, M-2):
  - **O que se sabe da direção de arte:** o diretor de arte disse na CEDEC 2020 que o detalhe foi distribuído pelo papel de cada objeto
    no jogo. O estilo simples deixa um "espaço imaginário" para o jogador completar
    ([VGC](https://videogameschronicle.com/news/animal-crossings-developers-say-the-series-must-continue-to-evolve),
    [GoNintendo](https://gonintendo.com/stories/368281-animal-crossing-new-horizons-dev-team-talks-about-series-innovat)).
  - **Para nós:** o detalhe vai para o objeto que importa (o portão, a barraca), e o fundo fica mais simples.
  - **Os penhascos** em camadas foram vistos em capturas de pré-lançamento ([TCRF](https://tcrf.net/Prerelease:Animal_Crossing:_New_Horizons)).
- **Paper Mario**, o pet em papel: não muda. O pet fica fora do cel shading (D-MD-23).
- **Cassette Beasts**, o visual GBA HD:
  - **Como é feito:** o mundo 3D tem texturas de pixel na mesma densidade dos sprites, e as peças de terreno foram feitas num editor de
    voxel ([Godot showcase](https://godotengine.org/article/godot-showcase-cassette-beasts/)). Na sequência, os personagens viram sprites
    de frente para a câmera ([Creative Bloq](https://www.creativebloq.com/features/cassette-beasts-2002-is-pokemon-in-a-zone-6-suburb-with-no-paddington-and-not-a-wizard-in-sight)).
  - **Para nós:** a mesma densidade de textura em todos os objetos, para nenhum parecer mais "liso" que o vizinho.
- **HD-2D:** é o visual com tilt-shift. Não muda.
- **Digimon World: Next Order e os animes de monstros digitais:** são a referência de clima da maquete B (`docs/TAREFA_V3_MAPA_DIGITAL.md`).
  Não achei fonte sobre a arte dos cenários dele ([galeria RPGFan](https://www.rpgfan.com/gallery/digimon-world-next-order-artwork/)).

## 3. Outros jogos com cel shading em objetos e cenário

- **Zelda: Breath of the Wild:**
  - **A arte:** pictórica, com materiais quase reais sob o cel shading. O diretor de arte fala em juntar o realismo do mundo com a
    jogabilidade ([Nintendo Everything](https://nintendoeverything.com/art-director-on-why-zeldas-art-style-constantly-changes-and-how-breath-of-the-wilds-look-was-made/)).
  - **Para nós:** pedra, madeira e lona com cara de material, não de plástico.
- **Zelda: The Wind Waker:**
  - **A arte:** bordas suaves, paleta clara, dois tons (luz e sombra) com uma máscara pintada na textura
    ([GamesRadar](https://gamesradar.com/the-making-of-the-legend-of-zelda-the-wind-waker), [análise](https://www.zeldadungeon.net/?p=51097),
    [cel shading](https://en.wikipedia.org/wiki/Cel_shading)).
  - **Para nós:** os dois tons de hoje ficam, mas a textura carrega o desenho.
- **Ni no Kuni** (Level-5 com o Studio Ghibli):
  - **A arte:** levou o desenho à mão para o 3D, e o cel shading foi o mais difícil
    ([exclaim](https://exclaim.ca/music/article/handmade_tale-ni_no_kuni_life_of_artisanal_animation)).
  - **Em projetos no estilo Ghibli:** uma camada pintada por cima da textura base ([80.lv](https://80.lv/articles/giant-s-end-village-making-an-environment-in-the-ghibli-stlye)),
    um borrão inclinado para dar cara de pincel ([80.lv](https://80.lv/articles/how-to-create-a-ghibli-style-warm-environment-with-hand-painted-texture))
    e o traço e o cel "tremidos" por ruído ([Unreal: Orbitals](https://www.unrealengine.com/tech-blog/stepping-inside-a-retro-anime-inspired-game-a-look-into-the-rendering-of-orbitals)).
- **Genshin e afins:** a folhagem simples com riqueza pintada, a base procedural com retoques à mão, e o traço grosso nos objetos e
  fino na folhagem ([80.lv: teapot house](https://80.lv/articles/001agt-002mrs-004adk-embellishing-a-teapot-house-with-cel-shading),
  [80.lv: props](https://80.lv/articles/how-to-sculpt-and-texture-props-and-foliage-for-a-stylized-3d-scene)).

## 4. Referências por objeto (modelos 3D, só estilo)

- **Portão:** [Fantasy Stone Gate](https://forums.unrealengine.com/t/terdpongdesign-stylized-fantasy-stone-gate-hand-painted-low-poly-portal/2721354),
  [Magic Stone Portal](https://forums.unrealengine.com/t/terdpongdesign-stylized-magic-stone-portal-low-poly-game-ready-low-poly-3d-model/2721630),
  [The Gate](https://gamesartist.co.uk/the-gate/), [Fantasy Gate](https://mattjwood.artstation.com/projects/2ezEK).
- **Barraca:** [Camping Tent](https://flowerpecker.womp.com/assets/camping-tent-1-ykb28asb63/),
  [Stylized Low-Poly Tent](https://www.cgtrader.com/3d-models/exterior/other/stylized-low-poly-tent),
  [Stylized Camping Pack](https://www.cgtrader.com/3d-models/exterior/other/stylized-camping-pack).
- **Cais:** [Boat and Modular Pier](https://www.cgtrader.com/3d-models/exterior/other/stylized-boat-and-modular-pier),
  [Handpainted Pier Set](https://www.cgtrader.com/3d-models/watercraft/other/lowpoly-handpainted-pier-set),
  [Cozy Wooden Dock](https://benevarts.artstation.com/projects/qJvoAD).
- **Poste:** [Stylized Streetlamps](https://www.cgtrader.com/3d-models/architectural/lighting/stylized-streetlamps-set-1),
  [Low Poly Streetlamps](https://corvussg.itch.io/low-poly-3d-streetlamps).
- **Carro:** [Mossy SUV](https://www.cgtrader.com/3d-models/car/suv/stylized-jungle-mossy-suv-scout),
  [Abandoned Beetle](https://ansonweese.artstation.com/projects/mqgZmY),
  [80.lv: Volkswagen abandonado](https://80.lv/articles/abandoned-volkswagen-creation-detailed-guide),
  [Moss Valley](https://alinagoman.artstation.com/projects/RKQYXD).
- **Geladeira:** [Retro Fridge](https://www.cgtrader.com/3d-models/interior/kitchen/stylized-retro-refrigerator-3d-model),
  [Retro Fridge (KabDevCG)](https://forums.unrealengine.com/t/kabdevcg-stylized-retro-fridge/2738574).
- **Trem:** [Train Pack com traço toon](https://www.cgtrader.com/3d-models/vehicle/train/stylized-train-pack-toon-outline),
  [Wagon pintado à mão](https://www.cgtrader.com/3d-models/vehicle/other/wagon-hand-painted),
  [Train Engine](https://downerdisaster.artstation.com/projects/aooQGq).
- **Barranco:** [Ghibli/Anime Rocks](https://sketchfab.com/3d-models/ghiblianime-style-rocks-smart-material-7cd29c1e388f4f17b95465e00e89fa17),
  [Anime NPR rock wall](https://www.cgtrader.com/3d-models/textures/architectural-textures/for-anime-npr-rock-wall),
  [80.lv: montanha estilizada](https://80.lv/articles/how-to-model-texture-a-vibrant-storytelling-mountainous-environment).
- **Chão e caminho:** [Codrops: grama em three.js](https://tympanus.net/codrops/2025/02/04/how-to-make-the-fluffiest-grass-with-three-js/),
  [grama anime no Blender](https://trungduyng.substack.com/p/anime-grass-tutorial-blender),
  [terra e grama misturadas (CC0)](https://opengameart.org/content/blended-textures-of-dirt-and-grass),
  [4 chãos pintados (CC0)](https://opengameart.org/content/4-hand-painted-ground-textures).
- **As normais para o toon:** [80.lv: normais limpas](https://80.lv/articles/get-clean-normals-for-stylized-shading-with-this-free-blender-tool),
  [Custom Normals](https://80.lv/articles/achieve-clean-stylized-rendering-with-custom-normals-add-on-for-blender).

## 5. O que muda nos esboços e na produção

1. **O prompt** pede o detalhe pintado: material, desgaste, musgo, um brilho na borda, o detalhe no elemento principal e o traço. Ele
   não pede mais "cores chapadas".
2. **A textura** fica com 3 ou 4 tons por material e com as pinceladas e o traço. Nada de reduzir a 7 cores.
3. **As normais** são suavizadas antes do toon.
4. **A mesma densidade de textura** em todos os objetos.
5. **O barranco** vira peças de rocha de verdade, com faces grandes e quinas com luz. O caminho ganha uma borda irregular que entra na
   grama.
