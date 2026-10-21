# TAREFA V2 — EVOLUCAO (2026-10-21)

Coordenador: Gerente. Worker: A. Worktree e branch: `v2-evolucao`, a partir da `main` (30500c3). Status: EM ANDAMENTO.

Categoria: implementacao. Origem: Matheus, 2026-10-21, pelo Gerente. A referência é a quinta tela de
`D:\Trab\digilab\_ref\referencia_mobile_2026-10-19.png` (local, não versionada): a tela azul cheia "EVOLUÇÃO!", o pet evoluído grande
sobre a plataforma de luz, o nome e o estágio no cartão e o botão "Continuar".

## 1. Pergunta

O momento da evolução e a aba Crescer › Evolução podem ganhar composição própria, só com o que o motor registra, sem mudar o motor, o save
nem o replay? Não vem de uma hipótese da pesquisa: é a interface do jogo.

## 2. Depende de

- A moldura nova do desktop (#374) e a Exploração (#389), mergeadas.
- O mapeamento enviado ao Gerente em 2026-10-21 e as decisões do Matheus no mesmo dia:
  1. a composição do momento, como proposta;
  2. a aba Crescer › Evolução recomposta no mesmo PR;
  3. o botão "Ver a revelação de novo" no histórico.

## 3. Mudança mínima

**O momento da evolução (`src/componentes/Revelacao.tsx`).**
- **A tela:** cheia e azul, com a grade e os estilhaços em CSS, sem asset. No alto, "EVOLUÇÃO!" grande (sem caractere japonês) e
  "Rookie → Champion" pequeno.
- **O pet:** grande e nítido, em escala inteira, sobre uma plataforma de luz própria (CSS). Sem o atlas do UP, entra a grade de pixels de
  reserva. O glow e o anel do Digivice do UP aparecem só se a decoração local carregar.
- **O cartão:** o NOME em caixa alta e o estágio, com o arquétipo e o brasão.
- **Abaixo:**
  - "de → para": a forma de antes e a nova. A de antes sai do registro (a evolução anterior, ou o In-Training);
  - "o que decidiu": o motivo que o motor registrou (cuidado, caráter, eixo complementar e lutas, vínculo);
  - nos pets v6 em diante, as medalhas do Tamer que a evolução pediu (`CMD`). A medalha que liberou aparece só quando a derivação é exata:
    a evolução cai no tick de um evento "u" que levou o pet de uma medalha a menos para o número pedido.
- **O botão:** Continuar, amarelo e largo, leva a Crescer › Evolução.
- **Desktop:** a mesma tela cheia, por cima da moldura, com o pet à esquerda e os detalhes à direita.
- **Movimento:** o pet surge com um brilho curto, parado com `prefers-reduced-motion`.

**A aba Crescer › Evolução (`src/telas/crescer/TelaEvolucao.tsx`).** Composição própria na linguagem da moldura nova e da referência:
- a forma atual em destaque, com o pet na plataforma, o nome, o estágio e quanto falta;
- a próxima evolução e as medalhas que faltam;
- a árvore;
- o porquê da forma atual;
- o histórico em linha do tempo, com "Ver a revelação de novo" em cada evolução, que reabre o momento dela.

Só dado do motor: nada de nível nem XP.

**O teste.** Um save de teste novo (`e2e/save_evolucao.json`, gerado por `e2e/gerar_save_evolucao.mjs`): um pet v11 no Rookie, a poucos
minutos do fim do estágio e com a medalha que a evolução pede. Ele evolui quando o relógio da página anda, e a revelação abre sem rota de
depuração.

**O que não muda:** o motor, o save, o replay e as rotas; as outras telas.

## 4. Gate

- `npm run tipos`, `npm test` e `npm run e2e` passam. O e2e soma:
  - a revelação com o save novo (o "de → para", o motivo, o Continuar);
  - a reserva sem o atlas;
  - o "Ver a revelação de novo".
- `npm run capturas`:
  - `crescer-evolucao` muda (é o pedido), e entram as capturas novas do momento e da aba com um pet v6;
  - as outras telas ficam iguais em 390, 360 e 1280.
- Capturas individuais em 390×844, 360 e 1280 do momento e da aba.

## 5. Entrega

- PR com as capturas e o relato no corpo. Depois, parar. Sem merge.
- O relato também na seção 9 deste documento.

## 6. Fora desta tarefa

- O motor e as regras de evolução.
- As outras abas de Crescer.

## 7. Critérios de aceitação

- O pet que evolui abre o momento novo, no celular e no desktop, com o pet nítido mesmo sem o atlas.
- A aba Evolução tem a composição nova, com a árvore, o resumo, as medalhas, o porquê e o histórico.
- O histórico reabre a revelação de cada evolução.
- Nada na tela que o motor não tenha; nenhum caractere japonês.
- O gate da seção 4 passa.

## 8. Precisa do Matheus

O ok visual nas capturas.
