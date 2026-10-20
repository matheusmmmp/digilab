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

**A tela Pet com o visual do protótipo** (2026-10-19, decisão do Matheus; **PROPOSTA, espera o ok dele antes do código**). O visual do
protótipo externo da tela Pet vence o `UI_GUIDELINES` nesta tela (o desvio aprovado está no `UI_GUIDELINES`, §8.1): as cores, a tipografia,
os cards de módulo, as barras, os ícones de traço, a ordem e o espaço vêm do código do protótipo, com as classes do Tailwind traduzidas em
px. Não vêm a arquitetura (no app é Preact, com os tokens, sem Next, Tailwind, shadcn nem dependência nova), o fundo do quarto (o habitat é
o de hoje) e nada que o motor não tenha: Próxima evolução, nível e XP, Treinar, Inventário, Mais/Descansar, o rótulo de humor, os tipos de
registro inventados, os módulos arrastáveis, o card do pesquisador, o "DigiLab OS" e o sino. As pranchas `PetModulos*`, recusadas, saíram.

| prancha | tamanho | o quê |
|---|---|---|
| `PetPrototipoDesktop.html` | 1280×720 | a barra lateral do protótipo (o logo, Pet, Crescer, Lutar e Diário; Conversar e Ajustes no pé), o topo (o relógio do jogo e o pet), o módulo Habitat (o palco de hoje com a emoção, a fala, a causa e o "agora" na pílula do protótipo), Ações (as seis do v11 em blocos, Alimentar no azul de canto cortado) e, na coluna de 370 px, Estado atual (as cinco necessidades com ícone, barra contínua e "x/100"), o chamado, o desejo, o DigiBrain (módulo recolhido) e Últimas ações, do registro |
| `PetPrototipo390.html` | 390×844 (fluida até 360) | o celular, derivado do mesmo visual: o topo com o retrato, o relógio e o Conversar; Habitat, Ações e Estado atual empilhados na ordem do protótipo; o chamado e o desejo; a barra de baixo no azul da lateral. O DigiBrain fica no palco, como hoje, e o registro não entra (CP-T2: fica em Crescer) |

As capturas estão em `capturas/`: `PetPrototipoDesktop.png`, `PetPrototipo390.png` (a dobra de 844 px), `PetPrototipo390_inteira.png` (a
página inteira) e `PetPrototipo360.png`. Os números e os textos são exemplo de layout. O protótipo não foi renderizado (rodar o Next dele
pediria instalar e executar as dependências do ZIP, e a permissão foi negada); a comparação foi feita pelo código, classe a classe.

**Todas as telas no layout novo** (2026-10-19, pedido do Matheus; **PROPOSTA, espera o ok dele**). `TelasLayoutDesktop.html` é uma prancha-mapa
com as 19 telas do desktop (1280×800, reduzidas à metade; `?tela=N` abre uma em tamanho real). A casca se aproxima da imagem de referência
que ele mandou: a lateral escura com o logo e os destinos, as abas da tela no topo, o relógio e o pet à direita,
o painel central de cantos cortados e a coluna de cards à direita, que se recolhe (no Pet, recolhida, o habitat e as ações crescem). As
telas: Pet (normal, colunas recolhidas, DigiBrain aberto), Meus pets, Crescer (Treinar, Aprendizado, Evolução, Itens), Lutar (Arena,
Campanha, Fronteira, Medalhas, a luta em tela cheia), Diário (Registro, Catálogo, Gerações, Cenários), Conversar e Ajustes. O conteúdo é o
que cada tela tem hoje, só o que o motor registra; ficam fora o nível e o XP, a Próxima evolução, o clima, o humor "Feliz", o card do
pesquisador, o "DigiLab OS", o sino e as abas da imagem que o jogo não tem. As capturas estão em `capturas/TelasLayout_mapa.png` e
`capturas/TelasLayout_00.png` a `_18.png`, na ordem do mapa. Só português: os subtítulos em japonês da primeira versão saíram (pedido do Matheus, 2026-10-19), e os nomes de exercícios, atributos, itens, líderes, lugares, medalhas e formas são os do motor (`web/app/motor/nomes.ts`, `itens.ts`, `medalhas.ts`, `bots.ts`).
