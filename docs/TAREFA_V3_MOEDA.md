# TAREFA V3 — MOEDA (2026-11-10)

Coordenador: Matheus. Worker: Claude Code (Gerente da V3, Opus 5.5). Worktree e branch: `v3-moeda-plano` (o plano); as etapas MO1 a MO5 em `v3-moeda`. Status: ABERTA. O plano está aprovado: as M-1 a M-10 DECIDIDAS pelo Matheus em 2026-11-10 ("Aprovo as 10"); a próxima etapa é a MO1.

Categoria: documentacao. Origem: Matheus, 2026-11-10: o Matheus pediu em 2026-11-10 uma rodada de planejamento da moeda do jogo (os Bits) e das melhorias da ilha, para aprovar.

## 1. Pergunta

Não é pesquisa: é o produto. Como pôr no jogo web uma moeda (os Bits) que se ganha pelo feito, e não pelo clique, e que se gasta em melhorias dos lugares da ilha, numa loja e em enfeites, sem comprar força nem mexer no pet? O desenho está em `docs/PLANO_V3_MOEDA.md`.

## 2. Depende de

- As decisões M-1 a M-10 do `docs/PLANO_V3_MOEDA.md` (seção 9).
- Na `main` já estão o Tamer (`web/app/src/tamer.ts`), o nível do Tamer (`docs/PLANO_V3_PROGRESSAO_TUTORIAL.md`), a campanha v6 e os chips de stat com os tetos.

## 3. Mudança mínima

- Este PR: só o plano, `docs/PLANO_V3_MOEDA.md`, e esta tarefa.
- As etapas (seção 7 do plano): o registro do Tamer 9 com os eventos `"bits"` e `"compra"`, a trava do portão, a loja, as melhorias e os enfeites. Só em `web/app/`.
- **Não muda:** o motor do pet e as versões de pet, o Python, o `engine.py`, a pesquisa.

## 4. Experimento e gate (se houver run)

Não há run. A conta do equilíbrio (o 1º pet junta o ★★ do portão antes de ficar pronto para o Champion) é feita numa vida gravada, na rodada de equilíbrio.

## 5. Entrega

- Testes: `python -m pytest tests/ -q`; em `web/app`: `npm test`, `npm run tipos`, `npm run e2e` (se a frente toca a web).
- Registro: seção própria no fim do arquivo do mês, `docs/registro/AAAA-MM.md` (rodada de saúde, etapa 2). **Não edite o índice
  `docs/REGISTRO_DESVIOS.md`:** ele é gerado (`python tools/gerar_indice_desvios.py`) por quem faz o merge. Um conflito nele se resolve
  rodando o gerador, nunca à mão (`docs/TAREFA_V3_INDICE_DESVIOS.md`). O resumo da etapa vai no corpo do PR e numa seção no fim do documento da
  frente (o `RESULTADO_V3_*.md` da run ou o `TAREFA_V3_*.md` da etapa), nunca no `CLAUDE.md` (rodada de saúde, etapa 1).
- PR contra a `main` com resumo e números (cada um com o artefato). Aviso ao coordenador. Merge só pelo Matheus.
- O corpo do PR segue `.github/pull_request_template.md`; o CI (`tools/verificar_relato.py`) confere os campos e a evidência da categoria.

## 6. Fora desta tarefa

Moeda por dinheiro real, gacha, uma segunda moeda da Fronteira, a troca de Bits entre jogadores, o equilíbrio dos preços (fica para a rodada de equilíbrio do fim).

## 7. Critérios de aceitação

- Do plano: `docs/PLANO_V3_MOEDA.md` existe, com as decisões M-1 a M-10 marcadas DECIDIDAS pelo Matheus.
- De cada etapa: os testes do Vitest do saldo derivado (saldo negativo falha alto), da novidade e do teto do cuidado; o e2e do portão trancado; as capturas no desktop e no celular.

## 8. Precisa do Matheus

As M-1 a M-10 do `docs/PLANO_V3_MOEDA.md`, seção 9, cada uma com a recomendação e o custo de errar.

## MO1: ganhar (2026-11-10, Gerente da V3, Claude Code, Opus 5.5, branch `v3-moeda`)

**O que entrou.** Os Bits se ganham; ainda não há nada em que gastar (MO2 e MO3).

- **A conta** (`web/app/src/bits.ts`, pura). Os feitos do pet e o valor de cada um, com os números da seção 2 do plano, PROPOSTOS:
  - a vitória paga pela faixa do rival: o lugar da campanha do NPC ou, na Arena, o estágio do pet na hora;
  - a novidade (M-3): a repetição contra o mesmo rival no mesmo dia do pet paga a metade da anterior;
  - a Liga, a Torre e o Salão não pagam;
  - o chamado e o cuidado na hora certa juntos têm o teto de 20 Bits por dia do pet; a pausa fica fora do teto;
  - as evoluções, a 1ª medalha de cada líder (5× a faixa do lugar) e cada nível do Tamer.
- **O motor** (`web/app/motor/motor.ts`): `Motor.feitosCuidado` guarda o chamado do bebê atendido, a pausa atendida e o cuidado na hora
  certa do Rookie em diante (`_cuidadoNaHora`, com os limiares `CUIDADO_NA_HORA` em `motor/constantes.ts`).
  - A lista é derivada do replay e fica fora do save, do registro e da assinatura. Nenhum pet muda de versão.
  - O teste confere que o replay refaz a mesma lista e a mesma assinatura.
- **O registro do Tamer 9** (`web/app/src/tamer.ts`), que lê os registros 1 a 8:
  - o evento `"bits"` traz o id do feito, o pet, o valor, a origem, o tick e a hora;
  - o mesmo feito pago duas vezes, a origem desconhecida, o valor que não é inteiro positivo e um campo faltando falham alto;
  - o saldo é a soma dos `"bits"`;
  - `conferirBits` (os feitos do pet e as medalhas) e `conferirBitsDoNivel` pagam o que falta. Conferir de novo não paga nada.
- **O app:**
  - `web/app/src/jogo.ts` confere os Bits depois de toda mudança do pet, junto com as medalhas. O pet de exemplo das boas-vindas não
    paga enquanto não é do jogador;
  - `web/app/src/nivelTela.ts` paga os níveis do Tamer quando o nível confirmado sobe (`pagarNivel`).
- **A tela** (`web/app/src/componentes/Topo.tsx`): o saldo aparece com a moeda e o número.
  - No desktop fica numa caixa logo depois do relógio, no estilo dele (as duas peles).
  - No celular fica dentro da pílula do relógio, depois da hora. Numa pílula própria embaixo, ela encostava no cartão do chamado.
  - Não aparece antes do primeiro Bit, nem com o registro do Tamer que não abriu.
- **As capturas:** `docs/pranchas/moeda-mo1/` (desktop 1920 × 950 e celular 375 × 812), com um save de teste: um Rookie treinado que
  vence o Gazimon duas vezes. O saldo dele:
  - 395 Bits na abertura: as lutas 10 e 5, a evolução para Rookie 50, a medalha da Campina 50, a evolução para Champion 100 e os níveis
    1 a 6 a 30 cada;
  - 396 depois de um carinho com o humor em 9 %, o cuidado na hora.

**Os desvios e as interpretações** estão no registro (`docs/registro/2026-11.md`, "MOEDA, MO1"):
- os limiares do cuidado na hora da higiene e do humor: 25 %, DECIDIDO pelo Matheus em 2026-11-11 (a etapa propunha 0,5);
- a faixa do rival da Arena;
- o teto do cuidado contado em Bits;
- o Salão fora;
- o pet de exemplo não paga;
- os níveis pagos a partir do piso.
