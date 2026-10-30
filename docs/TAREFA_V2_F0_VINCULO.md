# TAREFA V2 — F0-VINCULO (2026-10-01)

> **V2, congelado em 2026-10-30** (tag `v2-final`). O estado em que este documento fica na V3 está em `docs/FECHAMENTO_V2.md`; o
> plano da V3, em `docs/PLANO_V3.md`.

Coordenador: chat "Principais jogos Digimon com diálogo" (coordenação da V2). Worker: a abrir. Worktree e branch: `v2-f0-vinculo`.
Status: ABERTA.

## 1. Pergunta

Por que o vínculo premia o dono aleatório, e quais desenhos corrigiriam isso sem virar outro canal de cuidado?
Fase 0, item 3 do `docs/PLANO_V2_PESQUISA.md` (pré-condição da fase 2).

## 2. Depende de

Nada além da `main`. Leitura: `CLAUDE.md` (seções "Personalidade, obediência e desejo" e "Evolução canônica"), `docs/LEITURA_CONSOLIDADA_DONO.md` §6.

## 3. Mudança mínima

**Diagnóstico e proposta; nenhum código muda nesta tarefa.** Entrega `docs/V2_VINCULO_PROPOSTA.md`:
1. Como o vínculo é calculado hoje, no Python (`digilab/vinculo.py`) e na web (`web/app/motor/vinculo.ts`), componente por componente, e se os dois batem.
2. O defeito com números lidos dos artefatos (cada um com o caminho): `artifacts_campanha/mega/limiar_vinculo.json` (Mega 5 de 6 no aleatório × 3 de 6 no
   atencioso); `artifacts_linhagem/sinal_dono/resultado.json` (atencioso − aleatório no vínculo); `artifacts_v1_personalidade/completa/metrics.json`.
3. A causa, com a conta: qual componente favorece quem cuida com mais frequência sem coerência.
4. Duas ou três alternativas de desenho, cada uma com o que mede, o efeito esperado nos donos sintéticos, o risco de virar canal de cuidado, e o que mudaria
   no motor e na web (versão de pet nova).
5. Recomendação em até 3 frases e a pergunta ao Matheus sobre qual alternativa ele aprova.

## 4. Experimento e gate

Sem run nova. Se o diagnóstico precisar de uma conta sobre vidas já gravadas, ela vai num script em `experiments/` com artefato em pasta nova
(`artifacts_v2_vinculo/`), sem sementes novas e sem GPU.

## 5. Entrega

- Testes: `python -m pytest tests/ -q`.
- Registro: seção no fim do `docs/REGISTRO_DESVIOS.md` só se houver divergência entre Python e web.
- PR contra a `main` com resumo e números (cada um com o artefato). Aviso ao coordenador. Merge só pelo Matheus.

## 6. Fora desta tarefa

Implementar o vínculo novo (vira frente própria depois da aprovação); o limiar do Mega; obediência.
