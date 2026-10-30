# TAREFA V2 — TELA-PET (2026-10-19)

> **V2, congelado em 2026-10-30** (tag `v2-final`). O estado em que este documento fica na V3 está em `docs/FECHAMENTO_V2.md`; o
> plano da V3, em `docs/PLANO_V3.md`.

Coordenador: Gerente. Worker: A. Worktree e branch: `v2-tela-pet-home`. Status: ENTREGUE (PR, espera o ok visual e o merge).

Categoria: implementacao. Origem: Matheus, 2026-10-19: refazer a tela Pet para se aproximar da primeira tela (Home) da imagem de
referência que ele mandou: o pet pixelado dentro de um cenário 2.5D claro, com a interface apoiando a experiência de jogo, e não um
painel de cards. É a etapa 3 de `docs/TAREFA_V2_FRONT_REACT.md`.

## 1. Pergunta

A tela Pet consegue dar ao cenário a maior área visual, com o sprite real em escala nítida e pouca informação de cada vez, sem perder
nenhum dado nem rota que o jogo tem hoje? Não vem de uma hipótese da pesquisa: é a interface do jogo.

## 2. Depende de

- Etapas 1 e 2 da troca do front (React, Tailwind, shadcn e lucide), mergeadas em #368 e #372.
- A decisão do Matheus de 2026-10-19:
  - a Home da imagem de referência substitui, na tela Pet, a composição de cards das pranchas `PetPrototipo*`, `TelasLayout*` e
    `TelasCelular390`;
  - o menu superior fica no desktop;
  - nenhum caractere japonês;
  - só o que o motor registra.

## 3. Mudança mínima

**O que muda:** só a tela Pet (`web/app/src/telas/pet/TelaPet.tsx`, `PalcoPet.tsx` e um componente novo do cenário), o CSS dela e os
testes de ponta a ponta que leem a tela Pet.

1. **O cenário:**
   - um quarto 2.5D claro (parede, janela, chão em perspectiva, plataforma) em CSS e SVG, feito para o app, num componente próprio
     (`CenarioPet`);
   - o pet continua no canvas por cima, com o sprite real do atlas em escala inteira (`image-rendering: pixelated`). Sem o atlas, o sprite
     de reserva.
2. **A hierarquia:**
   - o cenário fica com a maior área;
   - embaixo dele, só a necessidade prioritária, num card, e três ações em destaque. As outras ações ficam a um toque ("Mais ações");
   - o resto (as necessidades, o desejo, a confiança, a fonte da fala, as atividades recentes e o DigiBrain) fica em painéis sob demanda:
     uma folha no celular e uma coluna recolhível no desktop.
3. **Nada do que a referência ilustra e o motor não tem:** nem nível, XP ou número de exemplo, nem o fundo de hexágonos, nem o avatar
   circular no lugar do sprite.

**O que não muda:**
- o motor (`web/app/motor/`), o save, o replay, a paridade, as rotas e as outras telas;
- a casca do desktop (o topo e a barra lateral);
- as capturas das outras 26 telas do roteiro `npm run capturas`, que têm de sair iguais.

**O cenário: a vista 3D do POC (decisão do Matheus de 2026-10-19, opção b).**
- O cenário é a vista ortográfica inclinada do WORLD-POC (Three.js só como vista, o arranjo V), carregada por import dinâmico ao abrir a
  tela Pet, num chunk à parte.
- Sem WebGL, ou se a cena falhar, fica a reserva: o quarto em CSS e SVG (`CenarioPet`).
- A cena só desenha a sala, os objetos e o pet como sprite em escala inteira. Nada da física do POC nem o cérebro de teste decidem algo
  do jogo; o jogo continua com o motor de hoje.
- A cena é decorativa (`aria-hidden`), e a necessidade e as ações continuam em controles reais.

## 4. Experimento e gate

Sem run. O gate:
- `npm run tipos`, `npm run build`, `npm test` e `npm run e2e` passam;
- `npm run capturas`: só as 4 capturas da tela Pet mudam (`pet-estado` e `pet-v11`, em 390 e 1280), e as outras 26 ficam iguais;
- o chunk da cena 3D (gzip) e o tempo de abrir a tela Pet medidos;
- a M3 no celular, pela página do jogo (as instruções na seção 9; o Matheus mede).

## 5. Entrega

- PR com as capturas individuais da tela Pet em 390×844, 360 e desktop, com o atlas local e com o sprite de reserva, e a comparação com a
  referência (o que foi ajustado em hierarquia, escala do pet, proporção do cenário e densidade). Depois, parar nesta tela.
- O relato no corpo do PR e na seção 9 deste documento.

## 6. Fora desta tarefa

- As outras telas (Treino, Exploração e Evolução têm composição própria quando chegar a vez de cada uma).
- O mundo 3D.
- A casca do desktop.
- A imagem de referência não é versionada.

## 7. Critérios de aceitação

- O cenário ocupa a maior área da tela Pet em 390, 360 e desktop.
- O sprite sai em escala inteira e nítida.
- Ficam visíveis só a necessidade prioritária e três ações; o resto abre sob demanda.
- Nenhum dado nem rota da tela de antes se perde.
- O gate da seção 4 passa.

## 8. Precisa do Matheus

O ok visual nas capturas antes do merge.

## 9. Entregue (2026-10-19)

**O que mudou na tela Pet** (`web/app/src/telas/pet/`, `src/estilo/pet_home.css`).

- **`cena3d.ts`, novo:** o cenário, a vista do POC só como vista. Carrega por import dinâmico e é o único módulo do app que importa o
  three.
  - **É uma cópia adaptada de `poc/mundo3d/vista.ts`, e não um import.** O G-FRONTEIRA (`test/poc_mundo3d.test.ts`, dos Gates A e B)
    segura que as telas do jogo não importam o POC, e ele continua passando sem mudança. As duas vistas se juntam quando o mundo 3D
    entrar no jogo (P4).
  - **Vem do POC:** a câmera ortográfica inclinada (50°), a sala de 16 × 12 células com as paredes e os dois obstáculos (o alto e o
    baixo), as caixas coloridas por face sem luz, o pet como `THREE.Sprite` com filtro nearest num número inteiro de pixels por texel e
    o canto alinhado ao pixel, e a sombra.
  - **Muda para o Pet:**
    - as cores claras;
    - as paredes altas e a janela na do fundo;
    - uma plataforma sob o pet;
    - o pet desenhado por cima de tudo (o sprite, de frente para a câmera, entraria no obstáculo alto de trás);
    - sem bola, sem comida e sem oclusão;
    - o enquadramento: o chão em até 68% da altura e encostado embaixo, e a parede no resto;
    - o pet parado no meio da sala, que só balança quando brinca ou explora;
    - um quadro a cada 120 ms, como o palco 2D.
  - **A textura do pet:** o quadro do idle do atlas (local), pelo `desenharSprite` (a forma sombria inclusive), ou a grade de reserva.
- **`CenarioPet.tsx`, novo:**
  - o `CenaPet` liga a cena 3D por import dinâmico ou, sem WebGL ou com falha, a reserva;
  - a reserva (`CenarioPet`) é o quarto 2.5D em CSS e SVG;
  - com `?medir3d=1` no endereço, aparece o botão da M3.
  - A parede e a janela (céu, nuvens, colinas), as paredes laterais em fuga e o chão em perspectiva (uma grade em `rotateX`).
  - Uma planta e um móvel baixo em grade de pixels.
  - A noite vem do motor (`eNoite`): céu escuro com estrelas e penumbra.
- **`PalcoPet.tsx`:** o canvas ficou transparente, por cima do cenário. Com a cena 3D ligada, desenha só os extras (a sujeira, o ícone
  rápido e a marca de saúde), em volta do retângulo do sprite que a cena informa (`cenaEstado.ts`). Com a reserva:
  - Desenha a plataforma (a peça do atlas, ou um aro sem ele), a sujeira, o pet ou o ovo e o ícone rápido.
  - O pet sai na maior escala inteira que cabe em 42% da altura e 60% da largura da cena, até 6x, com os pés a 86% da altura.
  - Sem o atlas, o sprite de reserva também sai em escala inteira e com o mesmo movimento.
- **`TelaPet.tsx`:**
  - **Cabeçalho do celular:** o nome do pet virou o botão de Meus pets, no lugar do retrato redondo.
  - **Cenário:** a emoção e o DigiBrain ficam por cima dele, e a fala vira um balão que abre o porquê.
  - **Embaixo do cenário:** a necessidade prioritária e as ações. A prioridade é, nesta ordem: a morte; um pedido aberto (o card de
    sempre, com o Atender); a necessidade mais baixa abaixo da metade da barra (o mesmo limite da cor de necessidade das barras); o
    desejo; ou o que ele faz agora.
  - **Ações:** três em destaque (a que atende a prioridade e, depois, Alimentar, Brincar e Carinho); as outras ficam em "Mais".
  - **Painel de detalhes, sob demanda:** necessidades, desejo, confiança, o porquê e a fonte da fala, as atividades recentes (no
    desktop) e o DigiBrain (no desktop). No celular é uma folha; no desktop, uma coluna recolhível à direita do cenário, fechada ao abrir
    a tela.
- **CSS morto removido:** as regras do layout de cards (`pet-corpo`, `palco-card`, `lado-cards`, `pet-retrato`, `db-coluna`...), sem uso
  em nenhuma outra tela.
- **`docs/UI_GUIDELINES.md` §8:** a ordem nova da tela Pet.

**Comparação com a referência (a Home).**

| | referência | tela Pet |
|---|---|---|
| área do cenário | cerca de 60% da tela (estimativa visual) | 58% da tela em 390×844 (366×518 px), 55% em 360×800, 79% da área de conteúdo no desktop (1024×606 px) |
| o pet | pixelado, centrado sobre uma plataforma redonda, ~45% da largura da cena | o sprite do atlas em escala inteira, sobre a plataforma do UP, até 60% da largura e 42% da altura |
| fundo | quarto claro com janela e plantas | quarto claro com janela, planta e móvel, sem hexágonos |
| informação de uma vez | um card (nome e estado) | um card (nome e a necessidade prioritária) e três ações com "Mais", como a 2ª tela da referência |
| o resto | — | sob demanda |

Ajustado depois da primeira captura:
- o pet saía grande demais e cobria a janela (de 52% para 42% da altura);
- o balão da fala foi para o lado do pet;
- a cena ganhou altura até encostar na barra de baixo;
- no desktop, com os detalhes abertos, a prioridade e as ações empilham, para os rótulos caberem;
- ao abrir "Mais", as ações extras rolam para a tela.

Não copiado da referência, por não ter dado no motor ou por ser ilustração: o número "01 HOME", o logo com japonês, o sino, nível e
XP, o texto "Parece animado hoje!".

**A cena 3D: custo e tempo de abrir** (Chrome desta máquina, build servido pelo `servidor_local.py`, 3 rodadas cada; artefato: o roteiro
de medida descrito no PR).
- **Chunk `cena3d`:** 539 KB, 135 KB em gzip, à parte. O chunk principal ficou em 777 KB (238 KB em gzip), quase igual ao de antes.
- **Do clique no Pet até o primeiro quadro da cena:**

  | | 1ª vez (baixa o chunk) | depois (chunk em cache) |
  |---|---|---|
  | 390 px | 90 a 139 ms | 36 a 40 ms |
  | 390 px, com a CPU 4× mais lenta (estimativa de celular) | 221 a 250 ms | 80 a 100 ms |
  | 1280 px | 68 a 94 ms | 36 a 48 ms |

  Não há rede de verdade nessa medida: o servidor é local.

**A M3 no celular, pela página do jogo** (o Matheus mede; critério PROPOSTO, o mesmo da M3 do POC: `fps_media` de pelo menos 30).
1. No PC: `cd web/app && npm run dev -- --host`. O Vite mostra o endereço da rede (`http://<IP do PC>:5173/`) e serve o atlas local.
   Se o celular não abrir, libere a porta 5173 no firewall do Windows, como na M3 do POC.
2. No celular, na mesma rede: abra `http://<IP do PC>:5173/?medir3d=1#/pet/estado`. Na primeira visita o jogo pede o brasão e o ovo; o
   ovo já aparece na cena 3D.
3. Na tela Pet, toque em "Medir 10 s (M3)". Durante 10 s a cena desenha a cada quadro do navegador. No fim aparece o JSON da medida:
   `fps_media`, a mediana e o p95 do quadro, o tamanho do canvas e o aparelho. Ele vai para a área de transferência quando o navegador
   deixa; se não, copie o texto da caixa.
4. Cole o JSON no PR.

**Gate.**

| conferência | resultado |
|---|---|
| `npm run tipos` | passa |
| `npm test` (Vitest) | 43 arquivos, 507 testes, todos passam |
| `npm run e2e` | 74 de 74, em duas rodadas |
| `npm run capturas` (referência: a `main` em `b4a423c`) | 26 iguais, pixel a pixel; mudam só as 4 da tela Pet (`pet-estado` e `pet-v11`, em 390 e 1280), como pedido |

Sobre o e2e:
- passou de 70 para 74. Entrou o teste da cena: a cena 3D com WebGL (`aria-hidden`, o canvas desenhado, sem a reserva) e, com o WebGL
  desligado, a reserva sem erro.
- Mudou o teste de foco pelo teclado, que agora roda com movimento reduzido. Sob carga, com a cena 3D nos outros workers, a transição
  do `dl-btn` dava um falso "sem foco".
- Do teste "Pet (Home)": entrou o teste "Pet (Home)" em 360, 390 e 1280 (o cenário é a maior área, o canvas `pixelated`, três ações e
  "Mais", sem hexágono nem retrato redondo, os detalhes abrem e fecham, sem rolagem lateral);
- dois testes mudaram junto com a tela: o do jogo completo abre "Mais" antes de clicar Elogiar, e o do DigiBrain em 1280 abre o
  painel pelo botão do cenário.

Capturas:
- versionadas, com o sprite de reserva (na cena 3D) e sem WebGL (o cenário de reserva): `docs/estilo_up/pranchas/capturas/PetHome*.png` (lista no README das pranchas);
- com o atlas: só locais.

**Números escolhidos (PROPOSTOS, de layout):**
- a escala do pet (42% da altura, 60% da largura; até 12x na cena 3D, em pixels do canvas, e até 6x na reserva, em px de CSS);
- o chão da cena 3D em até 68% da altura;
- o pet em (meio, 68% da profundidade) da sala;
- os pés a 86% da cena;
- a altura da cena no celular (`100dvh - 326px`, entre 340 e 660 px).

O limite da necessidade (metade da barra) não é novo: é o mesmo da cor das barras.
