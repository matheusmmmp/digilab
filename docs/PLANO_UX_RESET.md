# Plano de UX do reset e das duas pontuações (2026-11-19)

**Status: APROVADO** pelo Matheus em 2026-11-19 ("Aprovo as UX-RS pelas recomendações, segue para as telas"): UX-RS-1 a 7 valem como
recomendadas. As telas vêm no PR das telas da MMO8. A prancha está em `docs/pranchas/ux-reset/`. As regras vêm do `docs/PLANO_V3_MMO.md` (seções 8 e
9; MMO-15 a MMO-19 APROVADAS pelo Matheus em 2026-11-11 pela recomendação). Os tamanhos e os textos de interface são **PROPOSTO, SEM
FONTE**.
Autor: Claude Code (Opus 5.5), sessão lateral da conta, branch `v3-mmo8-prancha`, worktree `D:\Trab\digilab\v3-mmo8`.

**O pedido:** a etapa MMO8 da seção 12 do `docs/PLANO_V3_MMO.md` pede "a prancha do reset (aposentar, o bônus, o ovo novo) e do perfil com
as duas pontuações" antes das telas. O modelo é a prancha da luta ranqueada (#967), que veio antes da tela (#972).

## 1. O que foi lido

- `docs/PLANO_V3_MMO.md`, seções 7, 8, 9 e 12, e as decisões MMO-12 a MMO-19; as seções 10 a 23 do `docs/TAREFA_V3_MMO.md`;
- o reset que já existe aos pedaços: `web/app/src/jornada.ts` (`chocarDoBrasao`, `novoOvoGuardandoAtivo`) e `web/app/src/heranca.ts`
  (`cruzar`, `CHAVE_GERACOES`, `Aposentado`); Meus pets (`src/telas/pet/MeusPets.tsx` e `MeusPetsDesktop.tsx`: "Novo ovo", "Nova geração");
- o Respeito parcial da MMO7 (`servidor_web/src/premios/premios.ts`: `RESPEITO`, `respeitoConferido`, `GET /premios`);
- as pranchas `docs/pranchas/ux-conta/` (o perfil, "Apagar a conta", o aceite), `ux-cais/` (a tabela, os estados) e `ux-lugares-menus/`.

## 2. O que as decisões já fixam

| a regra | o que ela põe na tela |
|---|---|
| **MMO-17:** o reset é do pet; aposenta em Gerações e choca um ovo | "Aposentar" no pet ativo; o fim leva à escolha do brasão de hoje |
| **MMO-17:** o Tamer fica com tudo; o cruzamento também conta | "Vai para Gerações" e "Fica com você" em texto; a linha do bônus na Nova geração |
| **MMO-18:** os níveis Ultimate, Mega e Mega com a Liga; 300/600/1 000 de Respeito; 150/400/800 Bits (PROPOSTO) | a escada dos três níveis, com o do pet marcado |
| **MMO-18:** sem herança de stats | uma frase no "Como o reset funciona" |
| **MMO-18:** o Respeito pede 200 pontos do Digimon conferidos; um reset pago em Bits por semana (PROPOSTO) | cada linha do bônus diz a trava dela; os estados 4d e 4e |
| **MMO-15:** duas pontuações, cada uma com o seu ranking | os dois cartões do perfil; as abas "Tamers" e "Digimon" |
| **MMO-15:** o nível do 11 em diante, um a cada 1 000 de Respeito (PROPOSTO) | "Nv 12" no perfil e na tabela dos Tamers |
| **MMO-16:** o recorde sem teto; "Tamer Lendário" a partir de 10 000 (PROPOSTO) | a barra até 10 000 e "a conta não para"; a etiqueta "Lendário" |
| **seção 8:** o ranking conta só o que o servidor viu; a tela pode mostrar um local maior | o conferido grande, o do jogo menor ao lado |

## 3. As telas

Todas na pele dos menus (`--hx-*`, Vidro por padrão e Militar), sem cor nova.

| # | a tela | o objetivo do jogador | o que tem |
|---|---|---|---|
| 1 | **Aposentar** | saber o que ganha e o que perde antes de decidir | o pet; a escada do nível; o bônus com as travas; o que vai e o que fica; "Aposentar e chocar um ovo" |
| 2 | **Confirmar** | não aposentar sem querer | a caixa de perigo, o aceite "Entendi que não volta", "Manter" como principal |
| 3 | **Feito** | ver o que entrou e seguir | "foi para Gerações", +Respeito e +Bits, "Escolher o brasão" |
| 4 | **Os níveis e os estados** | entender por que deu menos | sem bônus; nível 2; nível 3; sem os 200 pontos; Bits da semana já pagos; sem conta |
| 5 | **O perfil com as duas pontuações** | ver onde está | o Respeito conferido e o do jogo, o nível, a barra até Lendário; os pontos do melhor Digimon e a posição; de onde vem o Respeito |
| 6 | **Os rankings no cais** | comparar | as abas Semana, Tamers, Digimon e Mural; a tabela dos Tamers pelo Respeito; o máximo histórico dos Digimon |
| 7 | **Os estados do perfil** | não ficar perdido | sem conta; sem resposta; o Tamer novo; o ranking dos Digimon vazio |

## 4. De onde vem cada dado

| na tela | de onde |
|---|---|
| o nível do reset e o bônus | `nivelDoReset` e `bonusDoReset` (`web/app/src/ranking/pontos.ts`, PR do código da MMO8) |
| "este pet tem N pontos conferidos" | `GET /digimons` (a linha do pet) |
| "o reset desta semana já foi pago" | o registro do Tamer (os "bits" de origem `reset`, a semana de Brasília) |
| o Respeito conferido e o de cada feito | `GET /premios` (`respeito`) |
| o Respeito do jogo | `respeitoLocal` (`pontos.ts`), do registro do Tamer |
| a tabela dos Tamers | `GET /tamers` |
| a tabela dos Digimon | `GET /digimons` |

## 5. A hierarquia e o estilo

- **Um botão principal por caixa.** No Aposentar, o botão do reset é tracejado, na cor do perigo, à direita e longe de "Agora não", como
  "Apagar a conta". Na confirmação, o principal é manter o pet.
- **Tudo em texto:** o nível do pet ("este pet"), a trava de cada bônus, "aposentado", "Lendário", "você". A cor só repete o texto.
- **Os números:** o Respeito e os pontos em `--hx-num`; o bônus em verde (`--hx-ok`) quando entra inteiro, tracejado quando uma trava o
  segura.

## 6. O celular

- **Aposentar:** a folha alta, sem rolar: o pet, a escada, o bônus. "O que vai e o que fica" entra no "Como o reset funciona".
- **Confirmar:** a folha baixa, com a ilha à vista.
- **O perfil:** os dois cartões lado a lado, mais estreitos; "De onde vem o Respeito" fechado.
- **Os rankings:** a folha do cais com as abas; a coluna "Tamer" sai da tabela dos Digimon.

## 7. O custo

Só o que o motor e o servidor já têm (ou têm no PR do código da MMO8): nenhuma tela pede mecânica nova. A tela do reset usa o `cruzar` e o
`chocarDoBrasao` de hoje; o perfil e o cais leem três rotas. O que custa é o envio do registro do aposentado (UX-RS-4).

## 8. Decisões para o Matheus (APROVADAS em 2026-11-19, pela recomendação)

Cada uma com a recomendação em negrito e o custo de errar.

- **UX-RS-1. Por onde se aposenta:** **em Meus pets, no cartão do pet ativo, ao lado de "Novo ovo" e "Nova geração".** A outra opção é
  só pela conclusão da Liga (o ovo novo de hoje). Custo de errar: baixo. Na conclusão, quem quer recomeçar no Ultimate não acha o reset.
- **UX-RS-2. A confirmação:** **dois passos, no molde de "Apagar a conta" (a caixa de perigo e o aceite).** A outra opção é um passo só.
  Custo de errar: baixo. O reset não se desfaz.
- **UX-RS-3. Onde ficam os dois rankings:** **no cais, como abas ao lado de "Semana" e "Mural".** Isto revê a UX-CA-1 ("só a semana, sem
  abas"), que dizia que a aba trancada promete o que não tem data; agora o mural (MMO7) e os dois rankings existem. A outra opção é só no
  perfil. Custo de errar: baixo a médio. O cais é o lugar do ranking; no perfil, a tabela fica longe da semana.
- **UX-RS-4. O registro do aposentado vai ao servidor sozinho:** **sim, com a conta e o cais aberto, como o envio depois da luta
  ranqueada.** A outra opção é o jogador mandar à mão. Custo de errar: médio. Sem o envio, o servidor não vê o reset, e o Respeito dele não
  entra no ranking.
- **UX-RS-5. Qual Respeito é o grande:** **o conferido, com o do jogo menor ao lado.** A outra opção é o do jogo grande. Custo de errar:
  baixo. O grande é o da tabela; o do jogo serve para quem joga sem conta.
- **UX-RS-6. O nível do 11 em diante paga os Bits do nível?** Hoje cada nível paga 30 Bits (M-2). **Recomendo não pagar do 11 em diante**
  até a rodada de equilíbrio (M-10): o nível pelo Respeito é uma fonte nova de Bits que a MMO-19 não aprovou. A outra opção é pagar como os
  outros. Custo de errar: baixo a médio; muda só a conta dos Bits do nível.
- **UX-RS-7. A prancha inteira:** aprovar para a tela da MMO8 usá-la. Recomendo aprovar. Custo de errar: baixo; é desenho.

## 9. O que não foi feito

- Nenhum revisor (`rev-a11y`) viu a prancha, e o contraste não foi medido.
- A escolha do brasão depois do reset é a tela de hoje e não foi redesenhada; Gerações também não.
- A linha do bônus na Nova geração (o cruzamento) está só como estado, sem a tela do cruzamento inteira.
- "Ver todas" aberta nos dois rankings não está desenhada.
- A revisão CR-7/CR-8 do `docs/PLANO_V3_CICLO.md` (o legado de stats somado ao bônus) é outra etapa e não entra aqui.
