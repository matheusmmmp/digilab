# TAREFA V2 — F0-LIMPEZA (2026-10-01)

Coordenador: chat "Principais jogos Digimon com diálogo" (coordenação da V2). Worker: o mesmo da F0-INVENTARIO (chat A). Worktree e branch:
`v2-f0-limpeza`. Status: ABERTA (começa com os PRs #102, #104, #105, #106 e #107 na `main`).

## 1. Pergunta

As divergências entre documento e código achadas no inventário (PR #106) e na auditoria da Fase 1 podem ser corrigidas sem mudar nenhum resultado?
Fecha a fase 0 (limpeza).

## 2. Depende de

Os PRs acima na `main` (o texto a corrigir está neles).

## 3. Mudança mínima

1. Textos: `CLAUDE.md` (contagem de testes: usar a da suíte no fim da tarefa, sem número fixo onde ele envelhece; "pasta v1" → `v2`); comentários de
   `web/app/motor/confianca.ts` e `web/app/motor/donos.ts`; a frase "o aprendido muda a política em cerca de 0,02 bit" no `docs/TODO_INTERACAO_CORPO.md` e
   no `docs/PLANO_V2_PESQUISA.md` (0,02 é a JSD entre braços; ao instinto é 0,03–0,05: citar o artefato).
2. `Config.limiar_privacao` (0,15) não é lido: `Estado.em_privacao` (`digilab/state.py`) usa o literal 0,15. Trocar o literal pelo parâmetro, **com o mesmo
   valor**. `Config.saciedade_maxima` e `saciedade_minima` também não são lidos: listar onde deveriam valer e **não** mudar (só registrar).
3. Nenhuma outra mudança. `engine.py` intocado.

## 4. Experimento e gate

Sem run. Gate: a suíte inteira passa, inclusive os testes de reprodução byte a byte (`test_canonico_intacto.py`, `test_reproducao_v3_confirmatoria.py`,
`test_natureza_criacao.py`, `test_confianca.py`) e os de hash de protocolo (o valor de `limiar_privacao` não muda, então o hash também não).

## 5. Entrega

- Testes: `python -m pytest tests/ -q`; em `web/app`: `npm test` e `npm run tipos` (só comentários mudam lá).
- Registro: seção no fim do `docs/REGISTRO_DESVIOS.md`.
- PR contra a `main`. Aviso ao coordenador. Merge só pelo Matheus.

## 6. Fora desta tarefa

Qualquer mudança de comportamento; o vínculo; a interação da 1a.
