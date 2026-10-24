# O produto DigiLab: visão, escopo e o primeiro produto jogável (2026-10-24)

**Status:**
- **A direção está DECIDIDA pelo Matheus em 2026-10-24** (o PROMPT MESTRE, repassado pelo Gerente; o texto integral fica fora do
  repositório, em `_ref/TAREFA_PROMPT_MESTRE_MODULAR.md`).
- **O detalhe é PROPOSTO:** os critérios, a ordem e o que entra em cada fase.
- Este documento é **a fonte da visão e do escopo do produto.** O estado real está em `docs/AUDITORIA_V2_PRODUTO_MODULAR.md`, e o cérebro em
  `docs/ARQUITETURA_DIGIBRAIN_MODULAR.md`.

## 1. A visão

O DigiLab é **um pet virtual afetivo, jogável e evolutivo**: um pet acompanhado ao longo da vida, num ambiente visual 2.5D/3D
isométrico.
- **O jogador** pode pôr ou arrastar comida e objetos no cenário.
- **O pet** os percebe, escolhe o que fazer, navega até eles e interage por iniciativa própria.
- **O produto prevê** treino, crescimento, batalha e evolução.
- **O cérebro** é o DigiBrain modular, com estado interno, memória e aprendizagem na vida, e com o corpo químico influenciando a
  atividade e a aprendizagem.

**O que não reabre** (decisões do Matheus que continuam, pela lista do Gerente):
- o determinismo e o replay;
- os nomes Digimon na tela, sem nenhum caractere japonês;
- só o que o motor registra aparece na tela;
- o front em Vite + React + Tailwind + shadcn + lucide;
- o menu superior no desktop;
- a cena 3D (a vista do POC em Three.js) como cenário do Pet, com a reserva CSS/SVG;
- a pergunta do efeito do dono, encerrada.

## 2. As prioridades

1. **O produto individual jogável vem primeiro:** um jogador e um pet.
2. **A pesquisa** serve para construí-lo e para entender os mecanismos do DigiBrain, sem virar uma rodada desconectada da experiência do
   pet.
3. **Toda tarefa ou experimento novo diz:**
   - qual capacidade do pet ou do cérebro desenvolve;
   - que marco do produto ou pergunta científica desbloqueia;
   - que evidência produz;
   - as dependências reais;
   - o que acontece se o gate falhar.
4. **Um gate que falha registra o resultado e orienta a próxima ação.** Ele não abre, por padrão, uma sequência de gates novos que
   continue validando o cérebro A e adie o modular ou o produto.

## 3. O primeiro produto jogável (o MVP)

Uma fatia de um jogador e um pet, no navegador. Os critérios observáveis estão em `docs/TAREFA_V2_MVP_MUNDO_PRODUTO.md`. Em uma linha
cada:

| critério | hoje (a auditoria) | o MVP pede |
|---|---|---|
| o pet e a cena no navegador, isométricos, com animação | a cena 3D é decoração; o pet fica parado no meio | a cena desenha o pet e os objetos **nas posições do motor** |
| o mundo físico é parte do que o pet percebe e decide | o mundo físico não está no jogo | o `Mundo` do motor TS no laço do pet do jogo |
| o jogador põe a comida num lugar, por gesto de arrastar **e** por uma alternativa acessível | alimentar é um botão sem posição | o arrastar e o caminho acessível, com o evento de comida com lugar no log |
| o pet detecta, decide, navega, alcança e come | só no POC, com o cérebro de teste | no jogo, com o cérebro do momento |
| a consequência muda o corpo e pode mudar o comportamento depois | o corpo químico já está no v11, mas sem posição | a comida com lugar chega ao corpo e ao aprendizado |
| treino, crescimento, batalha local e evolução | implementados, com testes (a auditoria, seção 3); o treino não toca o cérebro nem o corpo | descritos pelo que existe; nada novo no MVP |
| o save e o replay; os erros da experiência básica | event sourcing, falha alto em evento desconhecido | o evento novo com replay e gabarito; critérios claros de erro |
| a cena 3D e a reserva testadas por integração | um e2e só confere que o canvas desenha | um e2e que confere que a cena segue o motor, com e sem WebGL |

**O cérebro no MVP:** o MVP **não espera** o cérebro modular. Ele liga o mundo ao jogo com o cérebro do momento (o A v11) e deixa o
adaptador pronto para a troca (`docs/TAREFA_V2_DIGIBRAIN_MODULAR_PRODUTO.md`). **Alimentar por botão** pode ficar como reserva
temporária, mas não é a interação física planejada.

**O MVP não depende da P4.** A P4 é pesquisa (o A com o contrato nas vidas do J5). O contrato que ela levou ao motor serve ao MVP, mas
concluir a P4 não põe o mundo no jogo.

## 4. As fases posteriores

**Não bloqueiam o MVP:**
- multiplayer, interação entre jogadores, comparação social, batalhas online e ranking;
- reprodução e genética ampla;
- o decodificador conversacional avançado.

Elas estão em `docs/TAREFA_V2_FASES_POSTERIORES.md`.

## 5. Assets

**A regra de procedência e autorização** (`docs/UI_GUIDELINES.md`, seção 5.1) vale para todo asset.

**Os sprites do Digimon UP** são assets **autorizados pelo Matheus.** Ele decidiu, relatado pelo Gerente:
- em 2026-10-22, retirar a regra de uso pessoal e publicar uma versão pelo túnel Cloudflare;
- em 2026-10-24, confirmar: "EU AUTORIZO A POSTAR OS SPRITES, SEM PROBLEMAS".

**O que continua:**
- o atlas fica fora do git;
- o e2e roda com o sprite de reserva;
- o crédito continua no rodapé.
