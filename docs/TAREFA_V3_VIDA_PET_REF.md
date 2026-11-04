# TAREFA V3 — VIDA_PET_REF (2026-11-04)

Coordenador: o Gerente da V3 (Claude Code). Worker: Claude Code, Opus 5.5, sessão da pesquisa de referências. Worktree e branch: `v3-vida-pet-ref`. Status: ENTREGUE (PR aberto, aguarda o Matheus).

Categoria: literatura. Origem: Matheus, 2026-11-04: pedido do Matheus de 2026-11-04, repassado pelo Gerente da V3: referencias de pets virtuais e jogos de criacao para o pet nao ficar parado.

## 1. Pergunta

O que pets virtuais e jogos de criação fazem para o jogador se entusiasmar e criar vínculo, e não ficar só olhando um pet parado? Não vem de hipótese do
`PLANO_V2_PESQUISA.md`: é a frente de produto "Vida do pet" (passo 1, o pet se move na vista; passo 2, cada ação com uma cena e a reação ao toque, só na
vista; passo 3, ações novas no cérebro), e esta pesquisa alimenta os passos 2 e 3.

## 2. Depende de

Nada. Lê a `main` em `ddf1ef0` (depois do #557).

## 3. Mudança mínima

Só documento: `docs/futuro/vida_do_pet_referencias.md` (novo), este arquivo, o registro do mês e o índice de desvios. Nenhum código, nenhuma tela, nenhum
número de jogo.

## 4. Experimento e gate (se houver run)

Não há run.

## 5. Entrega

- Testes: `python -m pytest tests/ -q`; em `web/app`: `npm test`, `npm run tipos`, `npm run e2e` (se a frente toca a web).
- Registro: seção própria no fim do arquivo do mês, `docs/registro/AAAA-MM.md`, e uma linha no fim do índice `docs/REGISTRO_DESVIOS.md`
  (rodada de saúde, etapa 2). O resumo da etapa vai no corpo do PR e numa seção no fim do documento da
  frente (o `RESULTADO_V3_*.md` da run ou o `TAREFA_V3_*.md` da etapa), nunca no `CLAUDE.md` (rodada de saúde, etapa 1).
- PR contra a `main` com resumo e números (cada um com o artefato). Aviso ao coordenador. Merge só pelo Matheus.
- O corpo do PR segue `.github/pull_request_template.md`; o CI (`tools/verificar_relato.py`) confere os campos e a evidência da categoria.

## 6. Fora desta tarefa

O desenho das cenas, as pranchas, qualquer ação nova no `AcaoPet`, qualquer número.

## 7. Critérios de aceitação

- `docs/futuro/vida_do_pet_referencias.md` existe, com o catálogo por jogo, os padrões, a tabela padrão × Digilab e a recomendação com o custo de errar.
- Toda mecânica de jogo traz o link aberto e o nível (oficial, imprensa, fã, SEM FONTE); todo DOI está em `docs/referencias/`.
- `python tools/verificar_relato.py --arquivo <corpo> --base origin/main` sem falha.

## 8. Precisa do Matheus

A ordem da recomendação (seção 5 do documento): é do Matheus.

## 9. Resumo da entrega (2026-11-04)

- `docs/futuro/vida_do_pet_referencias.md`: 17 jogos ou sistemas no catálogo, 12 padrões, a tabela padrão × Digilab (só vista, cérebro, não serve) e a
  recomendação em três frentes, com o custo de errar.
- A recomendação do passo 2: uma cena por ação do `ACOES_PET`, o toque no pet como o mesmo `acariciar` do botão com a reação tirada do corpo, a expressão
  pelo corpo químico, as intenções do v16 como cena e um diário tirado do log.
- A do passo 3: partir do modular (investigar e brincar sozinho já são intenções com alvo no v16), depois vaguear; seguir o dono espera um evento de
  presença do dono, que não existe.
- Desvios: `docs/registro/2026-11.md`, seção de 2026-11-04 "VIDA DO PET, as referências".
