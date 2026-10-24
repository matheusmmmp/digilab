# Pranchas versionadas (placeholders)

Pranchas novas desenhadas fora do canvas e guardadas no repositório **sem imagens de terceiros**:
- o pet, os ícones da barra e o brasão são placeholders originais (vetor);
- o fundo hexagonal fica de fora (`--dl-img-hex: none`).

A cópia com os sprites e as imagens de `img/` fica em `D:\Trab\digilab\Assets\Pranchas_UP\`, fora do repositório (a regra dos
assets: `docs/UI_GUIDELINES.md`, seção 5.1), listada no `index.html` de lá.

Tokens e componentes: `../dl-up.css` (`--dl-*`, `dl-*`). Medidas e casca: `docs/estilo_up/DIRETRIZES_REPLICAR.md`. Para abrir com o CSS,
sirva a pasta por HTTP, por exemplo pelo `servidor_local.py`.

| prancha | tamanho | o quê |
|---|---|---|
| `MapaDesktop.html` | 1280×720 | mapa do mundo físico em vista inclinada; a câmera segue o pet, e a bandeja e a bola ficam na lateral (`docs/futuro/mundo_fisico.md`, 2.3 e 2.6) |
| `Mapa390.html` | 390×844 | o mesmo no celular: o mapa na tela inteira e a bandeja aberta embaixo; o arrasto começa na bandeja, e um dedo no mapa move a câmera |
| `MundoComida390.html` | 2 × 390×844 | o MVP do mundo no jogo, etapa 2 (`docs/TAREFA_V2_MVP_MUNDO_PRODUTO.md`): o gesto (arrastar a ração da barra de ações e soltar no chão da cena) e o caminho acessível (tocar em "Pôr ração" e depois no chão, ou escolher o comedouro, perto do pet ou longe pelo teclado); só o que o motor do v12 tem, com o Alimentar descrito como reserva |

A cena usa a projeção do protótipo `docs/futuro/mundo_fisico_vistas.html`: escala s(y) = 0,5 + 0,5·y/300 e a altura com expoente 1,25. Os
números e os textos são exemplo de layout, não dado.
| `DigiBrainDesktop.html` | 1280×720 | o painel DigiBrain dos pets v11 (etapa 5 do W-PORTE, `docs/TAREFA_V2_W_PORTE_CEREBRO_A.md`, seção 4) na casca da UI-DESKTOP (#328): uma coluna entre o habitat e a coluna de sempre, com o "agora", as barras por lobo, a percepção em lista (PW-5), a emoção como selo à parte (PW-6), as chances, o "o que aprendeu" e as últimas ações; a coluna rola sozinha |
| `DigiBrain390.html` | 390×844 | o mesmo no celular, numa folha que sobe de baixo, aberta pelo botão "DigiBrain" no canto do palco; o cabeçalho do Pet, com Conversar e Ajustes, não muda |

As duas pranchas do DigiBrain usam as cores pelos tokens `--dl-*` (o app usa os `--ui-*` equivalentes do #328 no desktop). Desde
2026-10-19 o ícone estático do cabeçalho deu lugar ao **mapa dos pesos**, logo abaixo do "agora": o desenho do connectome do #321
(`docs/futuro/connectome_cerebro_a.md`, seção 2) em colunas fixas, geradas da estrutura do cérebro A. As regiões são os lobos (percepção,
impulsos, decisão; a memória e emoção, sem pesos). Cada traço é um peso `w[regra][acao][entrada]`, da entrada à ação, passando pela
regra: a espessura é √|w|/S, e a cor separa o instinto (cinza) do aprendido a mais (vermelho) e a menos (azul). A cada decisão acendem,
em laranja, a regra que disparou, os candidatos com a chance, as entradas que mais pesaram e os termos da ação escolhida; a ação
escolhida e o lobo que pesou mais ficam destacados. Entre duas decisões o mapa fica parado: nada anima para fingir atividade. Os números
das duas pranchas são os do gabarito (a vida v11 da semente 101, a decisão 262), desenhados pela mesma conta do componente `MapaPesos`.
No celular o mapa ocupa a largura da folha. As capturas estão em `capturas/`.

## As telas do celular no modelo novo (2026-10-19)

| prancha | tamanho | o quê |
|---|---|---|
| `TelasCelular390.html` | 390×844 e 360×800 | as 22 telas do celular no modelo novo (`docs/TAREFA_V2_PRANCHAS_CELULAR.md`), com o conteúdo que cada tela do app tem hoje; com `?tela=N` (0 a 21) mostra uma tela só, na largura do aparelho |

Os tokens, os ícones e o pet de reserva são os da `TelasLayoutDesktop.html` (branch `v2-tela-pet`). O que a referência mostra e o motor não
tem fica marcado na tela como "sem dado no motor". As capturas estão em `capturas/TelasCelular390_NN.png`, `capturas/TelasCelular360_NN.png`
e `capturas/TelasCelular_mapa.png`.

**A tela Pet como a Home da referência** (2026-10-19, `docs/TAREFA_V2_TELA_PET.md`): capturas do app, não prancha. O cenário é a vista 3D do POC. Elas foram tiradas com o
sprite de reserva, sem o atlas e sem a decoração do Digimon UP (só locais), e com os avisos de "não carregou" escondidos só na captura.
As capturas com o atlas ficam fora do repositório.

| captura | o quê |
|---|---|
| `capturas/PetHome390.png` | celular, 390×844 |
| `capturas/PetHome360.png` | celular, 360×800 |
| `capturas/PetHome390_mais.png` | celular, com "Mais" aberto |
| `capturas/PetHome390_detalhes.png` | celular, com a folha "Como ele está" aberta |
| `capturas/PetHomeDesktop.png` | desktop, 1280×800 |
| `capturas/PetHomeDesktop_detalhes.png` | desktop, com a coluna de detalhes aberta |
| `capturas/PetHome390_semwebgl.png`, `capturas/PetHomeDesktop_semwebgl.png` | sem WebGL: o cenário de reserva, em CSS e SVG |

Todas mostram o pet v11 do e2e.

**A moldura nova do desktop** (2026-10-20, `docs/TAREFA_V2_MOLDURA_DESKTOP.md`): `capturas/Moldura_<tela>.png` põe, para cada uma das 15
telas do roteiro de capturas em 1280 px, o antes (a `main`) e o depois (a moldura da `TelasLayoutDesktop`) lado a lado. Foram tiradas sem o
atlas e sem a decoração do Digimon UP.

**O quadro modular da tela Pet no desktop** (2026-10-20, `docs/TAREFA_V2_PET_QUADRO.md`): `capturas/Quadro_pet-v11.png` e
`capturas/Quadro_pet-estado.png` põem lado a lado o antes (a moldura do #374) e o depois (o quadro). `capturas/Quadro_pet-v11_recolhida.png`
mostra o quadro e a coluna lateral recolhida. Foram tiradas em 1280 px, sem o atlas e sem a decoração do Digimon UP.

**A Exploração** (2026-10-21, `docs/TAREFA_V2_EXPLORACAO.md`): a aba que era a Campanha, com o mapa 3D de ilhas de voxels.
`capturas/Exploracao_390.png`, `capturas/Exploracao_360.png` e `capturas/Exploracao_1280.png` são o celular (rolado até o marcador) e o
desktop. `capturas/Exploracao_390_folha.png` é a folha de um lugar, e `capturas/Exploracao_390_inteira.png`, a página inteira. Foram tiradas
sem o atlas e sem a decoração do Digimon UP, com o pet v6 do e2e das arenas.

**A Evolução** (2026-10-21, `docs/TAREFA_V2_EVOLUCAO.md`): `capturas/Evolucao_momento_<largura>.png` é o momento da evolução em 390, 360 e
1280 px (um Agumon que vira Greymon). `capturas/Evolucao_aba_<largura>.png` é a aba Crescer › Evolução recomposta, com o pet v6 das arenas,
e `capturas/Evolucao_aba_390_inteira.png`, a aba inteira. Foram tiradas sem o atlas e sem a decoração do Digimon UP: o pet é a grade de
reserva.

**O Treino** (2026-10-22, `docs/TAREFA_V2_TREINO.md`): `capturas/Treino_pausa_<largura>.png` é a aba Crescer › Treinar recomposta, em 390, 360
e 1280 px, com um pet que pede pausa. `capturas/Treino_forcar_*.png` mostra o pet que só pode Forçar, com a folha de confirmação, e
`capturas/Treino_pausa_390_inteira.png`, a página inteira. Foram tiradas sem o atlas e sem a decoração do Digimon UP.
