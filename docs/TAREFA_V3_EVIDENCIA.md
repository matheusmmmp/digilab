# TAREFA V3 — EVIDENCIA (2026-11-16)

Coordenador: o Matheus, direto (o prompt de 2026-11-16). Worker: Claude Code, Opus 5.5. Worktree e branch: `v3-auditoria-evidencia` (a
fase A0); cada fase seguinte num branch `v3-evidencia-<fase>`. Status: ABERTA, na fase A0.

Categoria: implementacao (a A0 traz uma ferramenta só de leitura e o teste dela; as fases A1 e A2 são experimentos). Origem: Matheus,
2026-11-16, o prompt das fases A0 a A4, com os checkpoints A1 a A4.

## 1. Pergunta

O modular vence um baseline trivial nas mesmas células? O aprendizado em vida (P1/P2, `plast.ts`) muda o comportamento no jogo? O que já
foi rodado se reproduz a partir do repositório? A A0 só responde a terceira em parte: o que existe, o que está versionado e o que falta.

## 2. Depende de

- O snapshot `f8fa9ad2647ad9d4164dced1aeeec8d6697de611` da `main` (a base de toda a frente).
- A A1 depende do ok do Matheus à auditoria (CHECKPOINT A1). A A2, do CHECKPOINT A2. A A3 e a A4, dos anteriores.

## 3. Mudança mínima

- **A0:** `tools/auditar_evidencia.py` (lê só o git), `tests/test_auditar_evidencia.py`, o artefato
  `artifacts_v3_auditoria_evidencia/auditoria.json` e o `docs/AUDITORIA_EVIDENCIA.md`.
- **Não muda:** nenhum código de produto, nenhum mecanismo, o `engine.py`, as runs e os artefatos que já existem. Nenhuma vida nova na A0.

## 4. Experimento e gate (se houver run)

- A0: nenhuma run.
- A1 e A2: cada uma com o `docs/PLANO_ANALISE_V3_BASELINE_TRIVIAL.md` / `docs/PLANO_ANALISE_V3_ABLACAO_APRENDIZADO.md` commitado antes da
  primeira vida, a faixa nova em `experiments/bancada/faixas.py` e a regra de leitura escrita antes.

## 5. Entrega

- Testes: `python -m pytest tests/test_auditar_evidencia.py -q`; a suíte inteira antes de qualquer run (as falhas conhecidas vão no PR).
- Registro: seção própria no fim de `docs/registro/2026-11.md`. O índice `docs/REGISTRO_DESVIOS.md` é gerado por quem faz o merge.
- Um PR por fase, no template; o merge é do Matheus.

## 6. Fora desta tarefa

A limpeza do código de produto (outra sessão), mecanismo novo, os sprites de terceiros, a poda (L5).

## 7. Critérios de aceitação (A0)

- A tabela de `docs/AUDITORIA_EVIDENCIA.md` cobre C1, C2, C3, C4, AN4, GVN2, PET_VIVO e COOP A1, cada linha com o commit completo do plano e
  do código, o caminho e o sha256 de cada artefato, tirados do `auditoria.json`.
- `python tools/auditar_evidencia.py f8fa9ad2647ad9d4164dced1aeeec8d6697de611 <saida>` reproduz o `auditoria.json` byte a byte.
- As lacunas (a) binários não abertos, (b) meta sem SHA do código, (c) plano depois da primeira vida estão escritas, uma a uma.

## 8. Precisa do Matheus

- CHECKPOINT A1: aprovar a auditoria antes da A1. As decisões abertas estão na seção 6 do `docs/AUDITORIA_EVIDENCIA.md`.
