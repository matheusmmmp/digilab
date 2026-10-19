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

As duas pranchas do DigiBrain usam as cores pelos tokens `--dl-*` (o app usa os `--ui-*` equivalentes do #328 no desktop). Desde
2026-10-19 o ícone estático do cabeçalho deu lugar ao **mapa dos pesos**, logo abaixo do "agora": o desenho do connectome do #321
(`docs/futuro/connectome_cerebro_a.md`, seção 2) em colunas fixas, geradas da estrutura do cérebro A. As regiões são os lobos (percepção,
impulsos, decisão; a memória e emoção, sem pesos). Cada traço é um peso `w[regra][acao][entrada]`, da entrada à ação, passando pela
regra: a espessura é √|w|/S, e a cor separa o instinto (cinza) do aprendido a mais (vermelho) e a menos (azul). A cada decisão acendem,
em laranja, a regra que disparou, os candidatos com a chance, as entradas que mais pesaram e os termos da ação escolhida; a ação
escolhida e o lobo que pesou mais ficam destacados. Entre duas decisões o mapa fica parado: nada anima para fingir atividade. Os números
das duas pranchas são os do gabarito (a vida v11 da semente 101, a decisão 262), desenhados pela mesma conta do componente `MapaPesos`.
No celular o mapa ocupa a largura da folha. As capturas estão em `capturas/`.

**A tela Pet em módulos** (2026-10-19, pedido do Matheus; **PROPOSTA, espera o ok dele antes do código**, CP-T1). A linguagem visual é a de um
protótipo externo (cards com ícone e título, as ações em blocos), sem a arquitetura nem os dados dele. Vale a ordem do `UI_GUIDELINES` §8 e
só o que o motor tem para um pet v11:

| prancha | tamanho | o quê |
|---|---|---|
| `PetModulos390.html` | 390×844 (fluida até 360) | cabeçalho de sempre; os módulos Meu parceiro (o palco, com a emoção e o botão DigiBrain), Estado atual (as necessidades em grade de 4 com a barra segmentada de 5 e a saúde), o chamado, o par necessidade × vontade aprendida e Cuidar (as seis ações do v11 em blocos, o carinho em destaque); a navegação embaixo. O registro recente não entra no celular (CP-T2: fica em Crescer), e não há "Próxima evolução" (CP-T3) |
| `PetModulosDesktop.html` | 1280×720 | os mesmos módulos na casca da UI-DESKTOP (#328): Meu parceiro no centro com o "agora", Cuidar embaixo dele, a coluna do DigiBrain sem mudança e, à direita, Estado atual, o chamado, o desejo e as Últimas ações, do registro |

As capturas estão em `capturas/`: `PetModulos390.png` (a dobra de 844 px), `PetModulos390_inteira.png` (a página inteira), `PetModulos360.png` e
`PetModulosDesktop.png`. Os números e os textos são exemplo de layout.
