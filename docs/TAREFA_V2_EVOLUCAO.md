# TAREFA V2 — EVOLUCAO (2026-10-21)

Coordenador: Gerente. Worker: A. Worktree e branch: `v2-evolucao`, a partir da `main` (30500c3). Status: ENTREGUE (PR, espera o ok visual e o merge).

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

## 9. Entregue (2026-10-21)

**O que mudou.**
- **`src/componentes/Revelacao.tsx`:** o momento recomposto.
  - **A tela:** cheia e azul, com a grade e os estilhaços em CSS. No alto, "Rookie → Champion" e "EVOLUÇÃO!".
  - **A cena:** o raio e a plataforma de luz são próprios; o glow e o anel do Digivice do UP entram só com a decoração local. O pet fica
    grande em escala inteira (`PetGrande`: o idle do atlas, ou a grade de reserva com a cor do pet).
  - **O cartão:** o NOME, o estágio, o arquétipo e o brasão.
  - **Embaixo:**
    - "de → para", com os dois pets pequenos. A forma de antes sai do registro (`formaAntes`);
    - "O que decidiu": o `Porque` de antes;
    - nos v6 em diante, "Esta evolução pediu N medalhas do Tamer". Quando a derivação é exata, vem também "Foi liberada pela Medalha da X"
      (`medalhasDaEvolucao`: a evolução cai no tick de um "u" que levou o pet de N-1 para N medalhas, e a medalha é a de número N do Tamer).
  - **O Continuar:** amarelo e largo. No celular fica no pé da tela enquanto os detalhes rolam, e leva a Crescer › Evolução como antes.
  - **A partir de 900 px:** o pet à esquerda e os detalhes à direita, por cima da moldura.
  - **Movimento:** o pet surge com um brilho de 0,7 s, parado com `prefers-reduced-motion`.
  - **Rever:** `reverEvolucao(i)` reabre o momento de qualquer evolução do pet.
  - A linha evolutiva de antes saiu: o "de → para" e a árvore da aba dizem o mesmo.
- **`src/telas/crescer/TelaEvolucao.tsx`:** a aba recomposta.
  - **O destaque:** a forma atual no mesmo azul do momento, com o pet na plataforma, o nome, o estágio, o arquétipo, o brasão e quanto falta.
  - **Próxima evolução:** os selos das medalhas (k de N), a frase das medalhas que faltam (a mesma de antes), a experiência de combate, as
    vitórias do estágio e o "se evoluísse agora".
  - **A árvore:** a de antes, num painel com título.
  - **O resto:** o porquê da forma atual; o histórico em linha do tempo, com "Ver a revelação de novo" em cada evolução; o brasão e o "Como
    funciona".
  - **No celular:** destaque, próxima evolução, árvore, porquê, histórico e "Como funciona", nessa ordem.
- **`src/estilo/evolucao.css` (novo)** e **`src/estilo/pet.css`** (sem as regras antigas da revelação).
- **`e2e/gerar_save_evolucao.mjs` e `e2e/save_evolucao.json` (novos):** um Agumon v11 no Rookie, a 4 min do fim do estágio, que já conhece
  a Medalha da Campina. Quando o relógio da página anda, ele vira Greymon e o momento abre, sem rota de depuração.

**Gate.**

| conferência | resultado |
|---|---|
| `npm run tipos` | passa |
| `npm test` (Vitest) | 45 arquivos, 547 testes, todos passam |
| `npm run e2e` | 80 de 80: os 77 de antes e os 3 novos (o momento em 390 e em 1280 com a aba e o rever; a reserva sem o atlas); o teste das medalhas confere também "Foi liberada pela Medalha da Campina". Os 4 testes da evolução e das medalhas rodaram de novo depois do último ajuste de CSS e passam |
| `npm run capturas`, 390 e 1280 px (referência: o build da `main` 30500c3) | 15 telas iguais, pixel a pixel; muda `crescer-evolucao` (o pedido); `evolucao-momento` e `crescer-evolucao-v6` são novas, sem referência |
| `npm run capturas`, 360 px (mesma referência) | o mesmo: 15 iguais, muda `crescer-evolucao` |
| determinismo do branch | 54 capturas gravadas e conferidas duas vezes, sem nova tentativa: todas iguais |

Notas do gate:
- O momento é capturado com movimento reduzido. O anel do Digivice (decoração local) gira sem parar, e duas fotos seguidas da mesma página
  variavam 2 pixels na borda dele.
- O glow e o anel ficaram sem `mix-blend-mode`, que também variava 1/255 entre capturas.

**As capturas** (em `docs/estilo_up/pranchas/capturas/`, sem o atlas e sem a decoração do UP: o pet é a grade de reserva):
- `Evolucao_momento_390.png`, `Evolucao_momento_360.png` e `Evolucao_momento_1280.png`: o momento do Agumon que vira Greymon;
- `Evolucao_aba_390.png`, `Evolucao_aba_360.png` e `Evolucao_aba_1280.png`: a aba com o pet v6 das arenas (DinoBeemon, 3 medalhas);
- `Evolucao_aba_390_inteira.png`: a aba inteira em 390.

A comparação com a quinta tela da referência fica fora do repositório, porque a referência não é versionada.

**Diferenças para a referência.**
- O "EVOLUTION SYSTEM" do canto não entra.
- Embaixo do cartão há os detalhes (de → para, o que decidiu, as medalhas), que a referência não tem.
- O Continuar é amarelo e largo, como lá, mas fica fixo no pé do celular.

**O que ficou para depois.**
- Algumas regras antigas da aba no `crescer.css` (`.evo-resumo`, o cartão da `.evo-principal`) ficaram sem uso ou sobrescritas pelo
  `evolucao.css`. Saem numa limpeza, sem mudar a tela.
