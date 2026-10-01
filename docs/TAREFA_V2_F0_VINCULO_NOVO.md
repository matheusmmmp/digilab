# TAREFA V2 — F0-VINCULO-NOVO (2026-10-01)

Coordenador: chat "Principais jogos Digimon com diálogo" (coordenação da V2). Worker: o mesmo da F0-VINCULO (chat C). Worktree e branch:
`v2-f0-vinculo-novo`. Status: ABERTA (começa com o PR #109 na `main`).

## 1. Pergunta

O vínculo redesenhado pela **alternativa B** (previsibilidade + desejo), decidida pelo Matheus em 2026-10-01, deixa de premiar o dono aleatório em vidas novas?
Fase 0, item 3 do `docs/PLANO_V2_PESQUISA.md` (pré-condição da fase 2).

## 2. Depende de

PR #109 (`docs/V2_VINCULO_PROPOSTA.md`) na `main`. Decisão do Matheus registrada: **alternativa B**.

## 3. Mudança mínima

- **Python:** o vínculo B (coerência do feedback por ação **e situação do pet** + desejo atendido; o atendimento sai) como variante de `digilab/vinculo.py`
  atrás de chave desligada por padrão (`ConfigVinculo`, campos novos PROPOSTOS). Desligada, todas as vidas da v1 saem byte a byte iguais (teste).
- **Web:** pets **v10** (`VERSAO_PET = 10`, reservado pelo coordenador para esta frente) usam o vínculo B; v1–v9 iguais (assinaturas e gabaritos).
  Paridade Python → web por gabarito, como na M1 (`confianca.test.ts`); constantes no `mapa_constantes.json`.
- **Limiar do Mega (0,4):** foi calibrado com o vínculo antigo. **Não muda nesta tarefa**: medir e relatar o que acontece com o limiar de hoje no vínculo B.
- Não muda: `engine.py`, obediência, as runs da v1.

## 4. Experimento e gate

- Plano `docs/PLANO_ANALISE_V2_VINCULO.md` commitado antes da run.
- Vidas **novas** (não os contrafactuais do #109): os donos sintéticos da personalidade (atencioso, aleatório, relapso, incoerente) e o exigente; sementes
  reservadas: **calibração 3101…3505** (se houver ajuste), **validação 5101…5505** (faixa nova desta frente, uma vez).
- Métricas: atencioso − aleatório no vínculo final (IC por bootstrap sobre sementes); obediência; Megas por dono com o limiar 0,4 (jogo web, como em
  `artifacts_campanha/mega/limiar_vinculo.json`).
- Gate PROPOSTO: atencioso − aleatório > 0 com IC fora de zero. Sem GPU.
- Artefatos em `artifacts_v2_vinculo_novo/`.

## 5. Entrega

- Testes: `python -m pytest tests/ -q`; em `web/app`: `npm test`, `npm run tipos`, `npm run e2e`.
- Registro: seção no fim do `CLAUDE.md` e do `docs/REGISTRO_DESVIOS.md`.
- PR contra a `main` com números e artefatos. Aviso ao coordenador. Merge só pelo Matheus.

## 6. Fora desta tarefa

Mudar o limiar do Mega; obediência; alternativa A.
