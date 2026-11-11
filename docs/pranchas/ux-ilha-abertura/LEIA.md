# Prancha: a câmera do primeiro dia (2026-11-10)

Esta prancha cuida da regra 6 de "guiar o olhar sem texto" (a lista das seis regras está em `docs/pranchas/ux-ilha-planta-a/LEIA.md`).
O pedido do Matheus, de 2026-11-08, foi: "regras de game design para instruir o player a observar o mundo [...] Tem que ser algo mais
natural". A regra diz: na primeira vez que a ilha abre, a câmera mostra o lugar devagar e volta ao pet, sem texto e sem seta. O
levantamento está no Obsidian, em `20 Temas/Ensinar a olhar.md`. O Matheus disse "Sim, a prancha" em 2026-11-10.

**Por que a regra 6:** a regra 1, a luz, já está na main (#745). A 2, a ilha limpa, e a 3, um sinal só, já valem. A 4, esconder e revelar,
já acontece com a mata do leste tapando o trilho. A 5, os pássaros, precisa da árvore madura do motor. A 6 é a próxima que é só vista.

**Como foi feito:** as imagens saem do jogo de verdade, com um protótipo atrás de `?abertura=a|b|c` (`web/app/src/telas/pet/ilha/aberturaConta.ts`
e um gancho em `vista.ts`). Sem o parâmetro, nada muda. Isso vale também na main depois do merge, até a etapa de código.

## Como a abertura funciona (o protótipo)

- **Uma lista de quadros-chave:** cada um tem o tempo, o ponto olhado, o zoom e a inclinação somada. Entre dois quadros, a câmera anda
  pela curva suave, que começa e chega devagar.
- **Os pontos:**
  - os do mapa: o ninho, a praça (o centro da planta A), o portão e a barraca;
  - o pet;
  - o meio, que é o ponto entre o pet e a praça.
- **No fim,** a câmera chega ao pet no zoom e na inclinação de sempre. A volta não dá salto.
- **Fica de fora:** a abertura não toca com o pet na mão, com um lugar aberto, com a cena coberta pelo véu nem com "reduzir movimento".
- **Os números** estão em `ABERTURAS` (`aberturaConta.ts`) e são PROPOSTO, SEM FONTE.

## As propostas

| | dura | o caminho | como fica |
|---|---|---|---|
| **A, o passeio** | 7 s | perto do ninho, a praça, o portão, o pet | mostra mais, mas começa sem o pet no quadro e é a mais longa. |
| **B, o afastar** | 5,2 s | perto do pet, recua e sobe até a praça e o portão caberem, volta | o pet fica no quadro o tempo todo, e a ilha aparece em volta dele. |
| **C, de cima** | 4 s | a ilha de longe sobre a praça, desce até o pet | é a mais curta, mas o pet começa pequeno e no canto. |

Na primeira versão da B, o meio do recuo olhava a praça, e o pet saía pela borda esquerda. Agora olha o meio entre o pet e a praça.

## Os arquivos

Os quadros estão na pele Vidro, no mapa Ilha, com o mesmo save e o relógio parado às 13:00. A câmera não depende da pele. No save
de captura, o pet está perto do comedouro e não no ninho, como estaria logo depois de chocar.
- `quadros_a.jpg`, `quadros_b.jpg` e `quadros_c.jpg`: a 1920 × 950, seis quadros (0, 20, 40, 60, 80 e 100 % do tempo), da esquerda para
  a direita e de cima para baixo.
- `celular_a.jpg`, `celular_b.jpg` e `celular_c.jpg`: os mesmos seis tempos a 390 × 844, lado a lado.
- **Os vídeos** (`abertura_a.mp4`, `abertura_b.mp4` e `abertura_c.mp4`, a 960 px, cada um com mais 1 s parado no fim) ficam fora do git,
  em `D:\Trab\digilab\capturas_ux_ilha_abertura\`, e na página da prancha.
- `fonte/capturar.spec.ts` refaz tudo:
  1. Copie o arquivo para `web/app/e2e_capturas/abertura.spec.ts`.
  2. Rode `npx vite build` e depois `npx playwright test -c playwright.capturas.config.ts e2e_capturas/abertura.spec.ts --project gpu`.
  3. Junte cada vídeo com `ffmpeg -framerate 15 -i video_<p>/%04d.png -vf scale=960:-2 -c:v libx264 -pix_fmt yuv420p -crf 24 -r 30 abertura_<p>.mp4`.
  4. Apague a cópia.
- **Os vídeos são montados quadro a quadro:** o relógio da abertura fica parado a cada 1/15 s. A gravação de vídeo do Playwright não acertava o
  tempo da abertura no corte.

## O achado

No zoom de perto (0,55 a 0,6), o fundo fica enevoado, porque a névoa acompanha o afastamento da câmera. A câmera livre de hoje faz o
mesmo quando aproxima. A prancha não mexe nisso.

## As decisões (APROVADAS)

O Matheus aprovou as cinco em 2026-11-10: "siga a recomendação." Os números (tempos, zooms e inclinações) continuam PROPOSTO, SEM FONTE.


- **AB-1, a proposta.** APROVADA: **B, o afastar**. O pet fica no quadro o tempo todo, e em 5 s a praça e o portão aparecem em volta
  dele. A A começa longe do pet e dura mais. A C começa com o pet pequeno. Custo de errar: baixo, porque é trocar uma tabela em
  `aberturaConta.ts`.
- **AB-2, quando toca.** APROVADA: **uma vez por save**, na primeira vez que a ilha fica à vista depois que o ovo choca. O registro fica
  numa chave da página (`<chave>-abertura`), fora do save, do log e do replay, como o nível do Tamer. A alternativa é tocar no começo de
  cada dia do jogo, que cansa. Custo de errar: baixo.
- **AB-3, interromper.** APROVADA: **sim**. Qualquer toque, tecla ou roda encerra a abertura, e a câmera volta ao pet na transição
  curta da câmera solta (`TRANSICAO_MS`, 0,4 s). Custo de errar: baixo.
- **AB-4, a HUD durante a abertura.** APROVADA: **fica como está**. Nos quadros, a câmera guia o olhar mesmo com os painéis, e
  esconder a HUD pede mexer no layout. A alternativa é esmaecer os painéis enquanto a câmera anda. Custo de errar: baixo.
- **AB-5, onde vale.** APROVADA: **em todas as larguras**. No celular, os quadros leem bem (`celular_*.jpg`). Com "reduzir movimento",
  a abertura não toca. Custo de errar: baixo.
