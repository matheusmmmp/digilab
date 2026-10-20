# TAREFA V2 — TELA-PET (2026-10-19)

Coordenador: Gerente. Worker: A. Worktree e branch: `v2-tela-pet-home`. Status: EM ANDAMENTO.

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

**Por que o cenário em CSS e SVG, e não a vista do POC 3D.** O habitat vira o mundo 3D depois do Gate C (P4).
- Um componente de cenário isolado, atrás do canvas do pet, é trocado inteiro por essa vista quando ela chegar, sem tocar no resto da
  tela.
- Trazer o Three.js agora poria cerca de 600 KB no jogo e uma cena 3D sem física nem pet, só para servir de fundo.

## 4. Experimento e gate

Sem run. O gate:
- `npm run tipos`, `npm run build`, `npm test` e `npm run e2e` passam;
- `npm run capturas`: só as 4 capturas da tela Pet mudam (`pet-estado` e `pet-v11`, em 390 e 1280), e as outras 26 ficam iguais.

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
