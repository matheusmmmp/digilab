# Assets do Digimon UP: onde aplicar

Pasta: `D:\Trab\digilab\Assets\Digimon Up Assets\Digimon Up Assets\Sprite\`. Uso pessoal e
local, fora do repositório (entram no atlas, como os sprites). Referência visual: canvas, página
**Assets** (`AssetsGuia`, `AssetsDiario`, `AssetsEvolucao`) e página **Configurações**.

| arquivo | o que é | onde usar |
|---|---|---|
| `Crest_Combine_1.png` | placa do brasão Coragem (sol) | chips de brasão no Catálogo, selo da espécie no Pet e na Evolução |
| `Crest_Combine_2.png` | placa com onda azul | brasão Amizade (**conferir**: a cor bate com `Temp_Shop_Friendship_Crest`) |
| `Crest_Combine_4.png` | placa "oo" roxa | brasão Conhecimento |
| `Crest_Combine_5.png` | placa gota | brasão Sinceridade |
| `Crest_Left_1.png` + `Crest_Right_1.png` | metades da placa | revelação de evolução: as metades se juntam |
| `Digivice_Circle_01/02/03.png` | anéis de Digivice | fundo girando na evolução, na troca de pet e no ovo chocando (parar com reduced-motion) |
| `UI_Fx_Glow_Circle_01.png` | anel de luz | atrás do sprite na revelação e na vitória |
| `Fx_Sparkle_2.png` | brilho de 4 pontas | evolução, elogio, lugar aberto na campanha |
| `TopDeco_Earth2_0.png` | globo em malha | decoração discreta nos cabeçalhos (opacidade ~0,2) e nas boas-vindas |
| `Explore_Icon_Encyclopedia.png` | tile de enciclopédia | atalho do Catálogo no Diário |
| `Explore_Icon_Training.png` | tile de treino | atalho de Treinar |
| `Explore_Icon_DGame.png` | tile de videogame | atalho do Laboratório |
| `Growth_Guide_Icon_05/06/07/09/10/11.png` | silhueta, prato, haltere, chip, Digivice, despertador | ícones de lista: forma não vista, Alimentar, Treinar, Registro/Exportar, Meus pets/Aparência, Tempo e intervalo |
| `Profile_Outline_Arena_1..10.png` | molduras de retrato | retrato de rival e do chefe; moldura por faixa de vitórias |
| `Icon_Pattern_2.png` | padrão de ovos | fundo claro de Novo ovo e do ovo chocando |
| `Common_Icon_Setting.png` | engrenagem | entrada de Configurações (no cabeçalho do Diário) |

## Fundos das lutas da campanha

Os `Dungeon_Bg_*` (1015×279) trazem um chefe desenhado no lado direito. Nunca usar a faixa
inteira como palco (o jogador veria um personagem que não é o rival). Já estão **recortados sem
o chefe** em `D:\Trab\digilab\Assets\Digimon Up Assets\Fundos_Campanha\`:

| arquivo recortado | origem | usar em |
|---|---|---|
| `campina_gazimon.png` (520×279) | `Dungeon_Bg_09`, dojô | luta contra Gazimon (Campina) |
| `torre_tortomon.png` (1015×279) | `Dungeon_Bg_11`, caverna com raios de luz (sem chefe) | luta contra Tortomon (Torre, defensivo) |
| `torre_guardromon.png` (620×279) | `Dungeon_Bg_05`, fábrica com grades | luta contra Guardromon (Torre, espelho/carcereiro) |
| `torre_devidramon.png` (600×279) | `Dungeon_Bg_02`, cidade à noite | luta contra Devidramon (Torre, agressivo) |
| `cidadela_piedmon.png` (1015×504) | `Dungeon_Bg_08`, céu digital rachado (sem chefe) | luta contra Piedmon, o chefe (Cidadela) |
| `cidadela_faixa.png` (500×279) | `Dungeon_Bg_01`, fortaleza vermelha | faixa do lugar Cidadela no mapa/rivais |
| `extra_lava.png`, `extra_arvores.png`, `extra_digital.png` | `Dungeon_Bg_06`, `03`, `04` | reserva: forma sombria, lugares novos |

Como usar no palco (390 px de largura): `background-size: cover; background-position: left
center`, com uma película escura de 25–35% por baixo do HUD para o contraste do texto. Os
fundos são ilustração, não pixel art: aqui vale suavização normal (sem `pixelated`). Os sprites
por cima continuam em escala inteira e pixelados. A arena continua com `PVP_Bg_Octagon`.

**Evitar:** logos (`Login_logo_*`, `Login_Digimon_logo_*`), loja e gacha (`Shop_*`, `Gacha_*`,
moedas, `DigiEmerald`, `DigiDiamond`), os `Dungeon_Bg_*` inteiros (usar só os recortes acima),
`Equipment_*` (roupas de tamer; o jogo não tem tamer).

**Som:** `AudioClip/` tem BGM e efeitos (`button_cute_19.wav`, `IdleBGM.wav`, `SFX_BGM_EVO.wav`…).
O jogo não tem som hoje; se entrar, fica atrás da configuração "Som" (desligado por padrão).
