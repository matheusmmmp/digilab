# Plano de UX da luta ranqueada (2026-11-17)

**Status: APROVADO** (UX-LR-1 a 6 pelas recomendações, Matheus, 2026-11-17: "Sim, aprovo"). Sem código de tela ainda. A prancha está em `docs/pranchas/ux-luta-ranqueada/`; o servidor e o
protocolo do pedido são da etapa MMO4 local (`docs/TAREFA_V3_MMO.md`, seção 13; PR #966). Os tamanhos e os textos de interface são
**PROPOSTO, SEM FONTE**.
Autor: Claude Code (Fable 5.2), sessão lateral da conta, branch `v3-mmo4-prancha`.

**O pedido do Matheus (2026-11-17):** "Sim, a prancha", em resposta a "Faço a prancha da luta ranqueada para você aprovar?"; e "gere no
fable". A seção 12 do `docs/PLANO_V3_MMO.md` pede a prancha antes de qualquer tela da MMO4.

## 1. O que foi lido

- `docs/PLANO_V3_MMO.md` (seções 3, 4, 5, 10 e 12; MMO-5 a MMO-9, MMO-13 e MMO-14 APROVADAS) e a seção 13 do `docs/TAREFA_V3_MMO.md`;
- o servidor da MMO4: `servidor_web/src/envio/sementes.ts` (as respostas do pedido) e `conferir.ts` (as situações da luta);
- a Arena de hoje (`web/app/src/telas/lutar/palcoPoc/TelaLugaresPoc.tsx`): o rival, o mapa e o botão Lutar;
- as pranchas `docs/pranchas/ux-lugares-menus/` (a aba Arena) e `docs/pranchas/ux-conta/` (os estados e a folha baixa), de onde vêm os
  tokens e os moldes; `docs/PLANO_UX_CONTA.md`.

## 2. O que as decisões e o servidor já fixam

| a regra | o que ela põe na tela |
|---|---|
| **MMO-6:** a semente vem do servidor, e a semente pedida conta como luta | o aviso antes do botão; o estado "pedindo"; "nada foi gasto" quando o pedido não sai |
| **MMO-7:** só a vitória vale, pela faixa do rival; o mesmo rival na semana vale a metade | cada rival mostra quanto vale; o já vencido diz "vale a metade" |
| **MMO-8:** 10 por dia, pelo relógio do servidor | "7/10" sempre à vista; o estado do limite, com a hora em que volta |
| **MMO-5:** o servidor manda na pontuação | o resultado nasce como "prévia" e vira "conferido"; o aviso quando o servidor conta outra coisa |
| **MMO-13** e a BT0-1: abre no primeiro Mega (no beta, com 3 medalhas) | a escolha "Ranqueada" com cadeado e o motivo |
| **CN-1:** a conta é escolha | sem conta, a tela leva a Entrar e não insiste |
| **MMO-14:** o cliente de outra versão não envia | o estado "Atualize o jogo" |
| a luta sem envio vale como derrota (a conta da MMO1) | o estado "ainda não enviada", com o reenvio |

## 3. As telas

Todas na pele dos menus (`--hx-*`, Vidro por padrão e Militar), sem cor nova.

| # | a tela | o objetivo do jogador | o que tem |
|---|---|---|---|
| 1 | **Arena, com a escolha Ranqueada** | escolher a luta sabendo o que está em jogo | "Treino / Ranqueada"; as lutas de hoje e os pontos da semana; os rivais com o valor da vitória; o mapa; o aviso; "Lutar valendo 20" |
| 2 | **Os estados do pedido** | não ficar perdido e saber se a luta foi gasta | pedindo; sem resposta; limite de hoje; trancada pelo nível; sem conta; versão antiga |
| 3 | **O resultado** | ver o que deu e o que o servidor contou | a prévia; conferido (vitória e derrota); o servidor viu outra luta; ainda não enviada |

**Fora desta prancha:** as tabelas da semana e o cais (MMO5), o perfil com as duas pontuações (MMO8) e o palco da luta, que não muda.

## 4. A hierarquia e o estilo

- **A luta ranqueada é a mesma Arena,** com uma escolha no topo. O rival, o mapa e o palco são os de hoje.
- **Sempre visível:** as lutas de hoje, os pontos da semana, o valor de cada rival e o aviso do que se gasta. Nada disso fica em balão.
- **Um botão principal por caixa.** No limite e no nível, o principal é "Lutar de treino": o jogador nunca fica sem o que fazer.
- **O estado em texto, nunca só em cor:** "prévia", "conferido" (com o ícone), "o servidor", "vale a metade". A derrota não usa vermelho.
- **O texto:** frases curtas, sem exclamação e sem culpa. Todo erro diz o que houve, se a luta foi gasta e o caminho.
- **O movimento:** os passos do pedido são três pontos parados; nada gira nem pisca (guia, seção 11).
- **A acessibilidade:** alvos de 44 px ou mais; o rival e o mapa como grupos de rádio; os estados em `role="status"` ou `role="alert"`;
  texto de 13 px ou mais.

## 5. O celular

A mesma folha da Arena, mais alta. A 390 e a 360 a escolha, o placar, os oito rivais, o aviso e o botão cabem sem rolar: o mapa vira um
botão ao lado do Lutar, e os textos encurtam ("vencido 1× · metade"; o rótulo inteiro fica no `aria-label`). A folha alta cobre os dois
últimos ícones da coluna da direita enquanto está aberta. Os estados e o resultado usam a folha baixa, com o portão e o pet à vista.

## 6. O custo

- **No determinismo:** nenhum para o treino. Na ranqueada, a luta entra no registro como hoje (`lutarPoc`), só com a semente do servidor.
- **No código:** o jogo já tem o pedido (`web/app/src/ranking/pedido.ts`); faltam a tela, o envio depois da luta e o reenvio.
- **No e2e:** testes próprios com o servidor falso; os de hoje não mudam, porque o treino não muda.

## 7. Decisões para o Matheus

**APROVADAS em 2026-11-17, todas pela recomendação (em negrito em cada item):** "Sim, aprovo", em resposta a "Você aprova a prancha
pelas seis recomendações, ou prefere o rival sorteado pelo servidor?". Na UX-LR-5 vale a escolha do jogador.

- **UX-LR-1. Onde mora:** **na aba Arena do portão, com a escolha "Treino / Ranqueada".** A outra opção é o cais. Custo de errar: baixo.
  No cais, a luta fica longe do rival e do mapa, e o jogador aprende duas telas de luta; o cais fica para as tabelas (MMO5).
- **UX-LR-2. A confirmação:** **o aviso acima do botão e o botão "Lutar valendo 20", sem segunda tela.** A outra opção é um "Tem
  certeza?" a cada luta. Custo de errar: baixo. Com 10 lutas por dia, a segunda tela vira um toque automático e deixa de avisar.
- **UX-LR-3. A prévia:** **mostrar na hora o que o jogo viu, com a etiqueta "prévia", e trocar por "conferido" quando o servidor
  responder.** A outra opção é esconder o resultado até o servidor responder (perto de meio segundo por vida, mais a rede). Custo de
  errar: baixo. A prévia nunca soma no placar da semana.
- **UX-LR-4. A luta não enviada:** **o jogo reenvia sozinho quando a conexão volta, e a tela tem "Enviar agora".** A outra opção é só o
  botão. Custo de errar: médio. Sem o reenvio, quem fecha o jogo sem rede perde a vitória no domingo sem saber.
- **UX-LR-5. Quem escolhe o rival:** **o jogador, como no treino.** É o que o servidor da MMO4 faz hoje: ele entrega só a semente. A
  seção 3 do plano MMO diz, numa linha, "o rival e a semente vêm do servidor", e a seção 4 diz "o rival vem da Arena". A outra opção é o
  servidor sortear o rival junto com a semente. Custo de errar: médio. Com a escolha, o jogador pode ir sempre no rival que o pet vence
  melhor; a regra da metade segura isso dentro da semana, e todos os rivais do estágio valem o mesmo. Com o sorteio, a prancha perde a
  lista, e o servidor e a conta dos pontos mudam.
- **UX-LR-6. A prancha inteira:** aprovar para a tela da MMO4 usá-la. Recomendo aprovar. Custo de errar: baixo; é desenho.

## 8. O que não foi feito

- Nenhum revisor (`rev-a11y`) viu a prancha, e o contraste não foi medido; os tokens são os de hoje.
- Os oito rivais, "7 de 10", "60 pontos" e as horas são exemplo de layout, nunca dado. A lista de verdade é a do `rivaisArenaPoc`.
- O retrato do rival não aparece na linha do resultado (a prancha só tem a folha do Growlmon).
- O estado trancado está desenhado só na caixa do estado, não na aba inteira.
- No celular, a folha da Arena ranqueada é mais alta que a de hoje e cobre parte da coluna de ícones; não foi testado em tela menor que
  360 × 800.
