# TAREFA V3 — CEREBRO_PRIMARIO (2026-11-04)

Coordenador: a sessão que abriu a frente (Claude Code). Worker: Claude Code, Opus 5.5. Worktree e branch: `v3-cerebro-primario`. Status: ENTREGUE (PR aberto; merge só do Matheus).

Categoria: implementacao. Origem: Matheus, 2026-11-04: pedido do Matheus de 2026-11-04: o DigiBrain modular como cérebro primário do pet do jogo, com o cérebro A selecionável.

## 1. Pergunta

Produto, sem hipótese de pesquisa: o pet do jogo decide pelo DigiBrain modular por padrão, e o jogador pode trocar para o cérebro A (a linha de base),
inclusive no pet que já está vivo.

## 2. Depende de

- O laboratório do modular (L3, LM0–LM5b) na `main`: o `DigiBrain` de `web/app/motor/digibrain/` e o pet de teste v16.
- As decisões do Matheus de 2026-11-04 (nesta sessão, pelas perguntas do worker):
  - **CP-1:** a troca vale também para o pet atual, não só para os ovos novos (a recomendação era só os ovos novos; o custo, um evento novo no registro);
  - **CP-2:** uma versão nova, a v17 = a v15 com o cérebro trocável (a v16 fica só do laboratório);
  - **CP-3:** a opção fica em Ajustes › Laboratório.

## 3. Mudança mínima

- `motor/constantes.ts`: `VERSAO_PET = 17`, `VERSOES_PET = [13, 14, 15, 17]`, `VERSAO_V17`, `CEREBROS`.
- `motor/tipos.ts`: o evento `["cb", { cerebro: "modular" | "a" }]` (`EventoCerebro`).
- `motor/motor.ts`: na v17, a política que vai ao laço manda cada gancho ao cérebro ativo; `trocarCerebro(c)` (o evento), `cerebroAtual`,
  `Motor.promoverV17(m)` (o v15 vivo refeito na v17, conferido pela assinatura); a assinatura ganha o `["cb", …]` só depois do primeiro `cb`.
  `lab` passa a ser o modular só enquanto ele decide.
- `motor/motor_corpo_mundo.ts`: a chave `digibrain` do laço deixa de ser `readonly` (a v17 a vira na troca).
- `motor/combate.ts`: a v17 luta como a v14 (como a v15).
- `src/cerebro.ts` (novo): a preferência dos ovos novos (`CHAVE-cerebro`, fora do save, modular por padrão) e `nascerComCerebro`.
- `src/produto.ts`: o `ligarProduto` grava o `cb` do ovo novo logo depois das chaves do produto (ovo novo, jornada, nova geração, pet de exemplo).
- `src/jogo.ts`: `trocarCerebroDoPet(c)` (o pet ativo; o v15 é promovido antes).
- `src/telas/config/Laboratorio.tsx` e `src/estilo/lab.css`: a seção "Cérebro" no topo de Ajustes › Laboratório, sempre visível.
- **Não muda:** os pets v13, v14, v15 e v16 (as assinaturas, o replay, os gabaritos); a pesquisa no Python; a escada de exemplo dos guardados
  (v17 sem `cb`, isto é, o A).

## 4. Experimento e gate (se houver run)

Sem run: só código do jogo. Os testes usam as sementes 101 a 707.

## 5. Entrega

- Testes: `python -m pytest tests/ -q`; em `web/app`: `npm test`, `npm run tipos`, `npm run e2e` (se a frente toca a web).
- Registro: seção própria no fim do arquivo do mês, `docs/registro/AAAA-MM.md`, e uma linha no fim do índice `docs/REGISTRO_DESVIOS.md`
  (rodada de saúde, etapa 2). O resumo da etapa vai no corpo do PR e numa seção no fim do documento da
  frente (o `RESULTADO_V3_*.md` da run ou o `TAREFA_V3_*.md` da etapa), nunca no `CLAUDE.md` (rodada de saúde, etapa 1).
- PR contra a `main` com resumo e números (cada um com o artefato). Aviso ao coordenador. Merge só pelo Matheus.
- O corpo do PR segue `.github/pull_request_template.md`; o CI (`tools/verificar_relato.py`) confere os campos e a evidência da categoria.

## 6. Fora desta tarefa

- O selo "experimental" e o rótulo "cérebro modular" do painel DigiBrain da tela Pet (`TelaPet.tsx`, que outra sessão está mexendo): o pet principal
  com o modular ainda mostra o painel do laboratório com o selo. Fica para depois do merge do HUD temporário.
- A fala, o caráter e o desejo seguem lendo o cérebro A (como no pet de teste): o modular só decide.
- Os pets v13 e v14 não trocam de cérebro (a luta e a bola deles são outras; promovê-los mudaria a vida).
- Nenhuma calibração do modular no jogo (a rodada de equilíbrio fica no fim).

## 7. Critérios de aceitação

- `web/app/test/cerebro_primario.test.ts` passa: a v17 sem `cb` assina igual à v15 evento a evento; a promoção; o ovo modular por padrão e o A pela
  preferência; a troca no meio da vida com o cérebro que sai parado e o replay bit a bit; os erros altos; a troca no app grava o registro.
- `npm run tipos`, `npm test` e `npm run e2e` passam em `web/app`.
- Em Ajustes › Laboratório, a seção "Cérebro" mostra o cérebro do pet e o dos ovos novos, e trocar muda o registro do pet (conferido no navegador).

## 8. Precisa do Matheus

Nenhuma pendente: CP-1 a CP-3 decididas. As interpretações do worker estão em `docs/registro/2026-11.md` (2026-11-04, CÉREBRO PRIMÁRIO).
