# TAREFA V3 — URGENCIAS (2026-11-17)

Coordenador: a Gerente das cinco frentes (sessão `gerente-cinco-frentes`). Worker: a sessão da F3 (Claude Code, Opus 5.5). Worktree e
branch: `v3-urgencias`. Status: ABERTA (etapa de papel entregue; espera as decisões D-UR-1 a D-UR-9).

Categoria: arquitetura. Origem: Claude Code, 2026-11-17: frente F3 das cinco frentes da síntese de literatura de 2026-11-16, aberta pela
Gerente das cinco: prioridade e escalonamento entre urgências do DigiBrain modular. O prompt está no vault,
`30 Decisões e protocolo/PROMPT_CINCO_FRENTES_2026-11-16`, seção F3.

## 1. Pergunta

A do Matheus: cada urgência é calculada sozinha, mas o pet só faz uma ação. A prioridade entre urgências deve ser explícita, e como? É uma
pergunta da trilha C (o cérebro modular), não de uma hipótese do `PLANO_V2_PESQUISA`.

## 2. Depende de

- A limpeza (`docs/TAREFA_V3_LIMPEZA.md`): o código dos desenhos (a) e (d) entra depois da LZ2 (Python) e da LZ3 (TS), combinado com a sessão
  da limpeza (D-UR-7). A etapa de papel não depende dela.
- As decisões D-UR-1 a D-UR-9 do Matheus (a espec, seção 8).

## 3. Mudança mínima

- **Etapa de papel (este PR):** `docs/ESPEC_V3_URGENCIAS.md` e esta tarefa. O levantamento fica no vault
  (`DigiLab — Revisão de escopo/LEVANTAMENTO_URGENCIAS_PRIORIDADE_2026-11-17`).
- **Não muda:** nada em `digilab/`, `experiments/` ou `web/app/`; nada no `lobos.py`; o `engine.py`; nenhuma versão de pet.

## 4. Experimento e gate (se houver run)

Nenhuma run nesta etapa. A parte em vidas (a espec, 2.4 e D-UR-9) pede um plano de análise próprio, `docs/PLANO_ANALISE_V3_URGENCIAS.md`,
e uma faixa pedida ao coordenador, só depois dos testes de uma decisão.

## 5. Entrega

- Testes: não se aplicam à etapa de papel.
- PR contra a `main` com o relato; merge só pelo Matheus.
- O corpo do PR segue `.github/pull_request_template.md`, conferido pelo `tools/verificar_relato.py`.

## 6. Fora desta tarefa

Código, testes, gabaritos e vidas; a calibração de qualquer número; a troca das três guardas do M-ARB por uma tabela; o acumulador da PE-5.

## 7. Critérios de aceitação

- `docs/ESPEC_V3_URGENCIAS.md` existe, com a previsão (seção 2), a sonda (seção 3), os desenhos (a) a (d) com o que muda no código e no
  registro (seção 4) e as D-UR-1 a D-UR-9 com a pergunta, a recomendação e o custo de errar (seção 8).
- O levantamento está no vault, com uma linha no `00 Início/Índice.md`.
- O relato passa no `python tools/verificar_relato.py`.

## 8. Precisa do Matheus

As D-UR-1 a D-UR-9 (a espec, seção 8), cada uma com a recomendação e o custo de errar.
