# Plano de UX do cais e da semana (2026-11-17)

**Status: PROPOSTO** (espera a aprovação do Matheus: UX-CA-1 a 7, seção 7). Sem código de tela. A prancha está em
`docs/pranchas/ux-cais/`; o servidor das tabelas é o da MMO5 local (`docs/TAREFA_V3_MMO.md`, seção 16; PR #978, na main). Os tamanhos e
os textos de interface são **PROPOSTO, SEM FONTE**.
Autor: Claude Code (Fable 5.2), sessão lateral da conta, branch `v3-mmo5-prancha`.

**O pedido do Matheus (2026-11-17):** "Sim, a prancha", em resposta a "Faço a prancha do cais e de 'Ver a semana' agora?". A seção 12 do
`docs/PLANO_V3_MMO.md` pede a prancha antes de qualquer tela da MMO5.

## 1. O que foi lido

- `docs/PLANO_V3_MMO.md` (seções 10, 11 e 12; MMO-9, MMO-13 e MMO-14 APROVADAS) e as seções 12, 16 e 17 do `docs/TAREFA_V3_MMO.md`;
- o servidor da MMO5: `servidor_web/src/envio/semanas.ts` (`GET /semanas`, `/semanas/:semana/tabelas` e `/semanas/:semana/segredo`);
- o cais de hoje no jogo: `web/app/src/telas/pet/lugaresIlha.ts` (trancado, sem menu) e `ilha/lugares.ts`;
- as pranchas `docs/pranchas/ux-lugares-menus/` (o lugar trancado, o cartão de destrave), `ux-conta/` (os estados, a folha baixa) e
  `ux-luta-ranqueada/` (o botão "Ver a semana" do limite de hoje); `docs/PLANO_UX_LUTA_RANQUEADA.md`.

## 2. O que as decisões e o servidor já fixam

| a regra | o que ela põe na tela |
|---|---|
| **MMO-9:** uma tabela por estágio, de segunda a domingo, no horário de Brasília | os quatro estágios como escolha; as datas e quanto falta |
| **MMO-9:** o desempate (pontos, rivais diferentes vencidos, menos lutas, quem chegou antes) | as colunas na ordem do desempate; a regra em "Como a tabela conta" |
| **MMO-5:** o servidor manda na pontuação | "parcial" em texto: só entra a luta conferida |
| a folga de 1 h do fechamento (PROPOSTA, D-CONTA-118) | o estado "fechando", com a hora |
| a resposta leva até 100 linhas, e a de quem pede vem sempre | a sua linha presa no fim, com "você" em texto; "Ver todas" |
| as tabelas pedem a sessão (D-CONTA-120) | sem conta, o cais explica e leva a Entrar |
| **MMO-14:** o segredo é publicado quando a semana congela | "Conferir a semana", só na semana fechada |
| **MMO-13** e a BT0-1: o cais abre no nível 10 (no beta, com 3 medalhas) | o cais trancado com "Nv 10" e o cartão de destrave |
| o apelido é gerado (um nome de Digimon e um número) | a tabela só mostra apelidos; nada para moderar |

## 3. As telas

Todas na pele dos menus (`--hx-*`, Vidro por padrão e Militar), sem cor nova.

| # | a tela | o objetivo do jogador | o que tem |
|---|---|---|---|
| 1 | **O cais, a semana aberta** | ver onde está e quanto falta | a semana e o estado; os estágios; as 8 primeiras e a sua linha; "parcial"; "Ir para a Arena" |
| 2 | **Os estados** | não ficar perdido | buscando; sem resposta; sem conta; tabela vazia; estágio em que não lutou; fechando |
| 3 | **A semana fechada** | ver o resultado final | "fechada" e a hora; o seu resultado em destaque; a tabela final; "Conferir a semana" |
| 4 | **Conferir a semana** | auditar, se quiser | o segredo para copiar e a regra em uma frase |
| 5 | **O cais trancado** | saber que existe e o que abre | o cadeado, "Nv 10" e o marco no balão |
| 6 | **O cais destravado** | saber que abriu | o cartão de destrave: "Cais", uma frase, "Ir" e "Depois" |

**Fora desta prancha:** o desafio do dia (MMO6), o mural e as recompensas (MMO7), o perfil com as duas pontuações e o ranking dos Tamers
(MMO8), e as divisões de 30 (MMO-9, só com 60 jogadores).

## 4. A hierarquia e o estilo

- **O cais é um lugar com uma tela só, por ora.** Sem abas: o desafio, o mural e o perfil entram quando existirem.
- **Sempre visível:** a semana, o estado dela em texto, o estágio escolhido e a linha de quem olha.
- **Um botão principal por caixa.** Na semana aberta, "Ir para a Arena": o cais mostra, a Arena luta.
- **O estado em texto, nunca só em cor:** "aberta", "fechando", "fechada", "parcial", "você".
- **A tabela é uma tabela de verdade** (`<table>`, com `<caption>`, `scope` e a linha de quem olha em `aria-current`).
- **O texto:** frases curtas, sem exclamação. Nenhuma linha compara o jogador com os outros em tom de cobrança.
- **O movimento:** nada gira nem pisca; a tabela troca de uma vez.
- **A acessibilidade:** alvos de 44 px ou mais; os estágios como grupo de rádio; texto de 13 px ou mais.

## 5. O celular

A folha alta, sem rolar: a semana, os estágios, 6 linhas e a sua. A coluna "Lutas" sai a 390 e a 360 e continua em "Ver todas". Os
estados usam a folha baixa, com a ilha e o pet à vista. O cais não ganha ícone na coluna do celular (UX-CA-2).

## 6. O custo

- **No determinismo:** nenhum. O cais só lê o servidor; nada entra no registro do pet.
- **No código:** um destino novo ("cais") nas rotas e em `lugaresIlha.ts`; a tela e o cliente das três rotas de `semanas.ts`; o cartão do
  marco 10, que hoje conta em silêncio.
- **No e2e:** testes próprios com o servidor falso; os de hoje não mudam.

## 7. Decisões para o Matheus

- **UX-CA-1. O que o cais abre agora:** **só a semana, sem abas.** A outra opção é mostrar já as abas do desafio, do mural e do perfil,
  trancadas. Custo de errar: baixo. A aba trancada promete o que ainda não tem data.
- **UX-CA-2. Por onde se entra:** **pelo lugar na ilha, pelo minimapa e por "Ver a semana" na Arena; sem ícone novo no trilho.** A outra
  opção é um ícone no trilho e na coluna do celular. Custo de errar: baixo. A coluna do celular já está cheia, e a folha da Arena cobre
  parte dela.
- **UX-CA-3. Quantas linhas:** **as 8 primeiras (6 no celular) e a sua, com "Ver todas".** A outra opção é a tabela inteira rolando.
  Custo de errar: baixo. Com 20 ativos no beta, as duas cabem; a diferença aparece com mais gente.
- **UX-CA-4. Quem vê as tabelas:** **só quem tem a conta, como o servidor faz hoje.** A outra opção é abrir as tabelas para todos. Custo
  de errar: médio. Aberta, a tabela mostra apelidos a quem não aceitou os termos; fechada, quem não tem conta não vê o que ganharia ao
  entrar. Mudar pede uma linha no servidor.
- **UX-CA-5. O segredo:** **uma linha fechada, "Conferir a semana", só na semana fechada, com o segredo para copiar.** A outra opção é o
  jogo conferir sozinho e mostrar "conferido". Custo de errar: baixo. A conferência no jogo é código novo, e quem desconfia do servidor
  não confia no jogo que ele entrega.
- **UX-CA-6. O cartão do nível 10:** **o cartão de destrave no molde dos outros lugares, com "Cais" e "Veja o ranking da semana."** A
  outra opção é o marco continuar em silêncio. Custo de errar: baixo.
- **UX-CA-7. A prancha inteira:** aprovar para a tela da MMO5 usá-la. Recomendo aprovar. Custo de errar: baixo; é desenho.

## 8. O que não foi feito

- Nenhum revisor (`rev-a11y`) viu a prancha, e o contraste não foi medido; os tokens são os de hoje.
- Os apelidos, os pontos, as posições, as datas e o segredo são exemplo de layout, nunca dado.
- O fundo é a captura de 2026-11-06, de antes do cais 3D (#670): o lugar do cais na ilha e a posição do cadeado são só de layout.
- "Ver todas" aberta (até 100 linhas) não está desenhada; nem a troca de semana pelas setas, além do estado da seta.
- O cais trancado e o destravado só estão a 1920; no celular valem os moldes da prancha dos lugares.
- Não foi testado em tela menor que 360 × 800.
