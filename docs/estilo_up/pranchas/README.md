# Pranchas versionadas (placeholders)

Pranchas novas desenhadas fora do canvas e guardadas no repositório **sem imagens de terceiros**:
- o pet, os ícones da barra e o brasão são placeholders originais (vetor);
- o fundo hexagonal fica de fora (`--dl-img-hex: none`).

A cópia com os sprites e as imagens de `img/` fica em `D:\Trab\digilab\Assets\Pranchas_UP\`, fora do repositório (uso pessoal, regra dos
assets do `CLAUDE.md`), listada no `index.html` de lá.

Tokens e componentes: `../dl-up.css` (`--dl-*`, `dl-*`). Medidas e casca: `docs/estilo_up/DIRETRIZES_REPLICAR.md`. Para abrir com o CSS,
sirva a pasta por HTTP, por exemplo pelo `servidor_local.py`.

| prancha | tamanho | o quê |
|---|---|---|
| `MapaDesktop.html` | 1280×720 | mapa do mundo físico em vista inclinada; a câmera segue o pet, e a bandeja e a bola ficam na lateral (`docs/futuro/mundo_fisico.md`, 2.3 e 2.6) |
| `Mapa390.html` | 390×844 | o mesmo no celular: o mapa na tela inteira e a bandeja aberta embaixo; o arrasto começa na bandeja, e um dedo no mapa move a câmera |

A cena usa a projeção do protótipo `docs/futuro/mundo_fisico_vistas.html`: escala s(y) = 0,5 + 0,5·y/300 e a altura com expoente 1,25. Os
números e os textos são exemplo de layout, não dado.
| `DigiBrainDesktop.html` | 1280×720 | o painel DigiBrain dos pets v11 (etapa 5 do W-PORTE, `docs/TAREFA_V2_W_PORTE_CEREBRO_A.md`, seção 4) na casca da UI-DESKTOP (#328): uma coluna entre o habitat e a coluna de sempre, com o "agora", as barras por lobo, a percepção em lista (PW-5), a emoção como selo à parte (PW-6), as chances, o "o que aprendeu" e as últimas ações; a coluna rola sozinha |
| `DigiBrain390.html` | 390×844 | o mesmo no celular, numa folha que sobe de baixo, aberta pelo botão "DigiBrain" no canto do palco; o cabeçalho do Pet, com Conversar e Ajustes, não muda |

As duas pranchas do DigiBrain usam as cores pelos tokens `--dl-*` (o app usa os `--ui-*` equivalentes do #328 no desktop). O desenho do
cérebro é um ícone estático com uma cor por lobo: o connectome (#321) é ferramenta de pesquisa até o J5 (CN-1) e não vai ao jogo, e nada
no painel anima para fingir atividade. As capturas estão em `capturas/`.
