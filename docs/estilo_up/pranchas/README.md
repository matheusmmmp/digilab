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
