# Histórico: as cópias de antes da rodada de saúde

Etapa 0 de `docs/TAREFA_V2_SAUDE.md` (o backup), feita em 2026-10-13, antes de qualquer outra etapa da rodada.

## A regra

**Nada se apaga.** Na rodada de saúde, todo texto e todo código só **move** ou **divide**, e deixa um ponteiro no lugar de onde saiu.
Estas cópias são a referência para conferir isso: cada etapa confere o resultado dela contra a cópia (`G-NADA-PERDIDO`, `G-CONCAT`,
`G-NOMES`). As cópias não se editam.

## A tag

`pre-saude`, anotada, no commit `8ae3ff77c020474e39da2658a19c6a0da79f9e7e` da `main` (merge do PR #295), enviada ao GitHub.
`git show pre-saude:<arquivo>` dá o arquivo inteiro de antes da rodada.

## As cópias

Cada cópia é o blob do commit da tag, byte a byte (`git show 8ae3ff7:<origem> > <cópia>`; o repositório grava tudo com LF).

| cópia | origem | linhas | bytes | sha256 |
|---|---|---|---|---|
| `CLAUDE_pre_saude.md` | `CLAUDE.md` | 4.169 | 414.717 | `a1f7f48164ef99fbcdbd05b52ddd0883b8ead25544c08ad76d80699f3839cec7` |
| `REGISTRO_DESVIOS_pre_saude.md` | `docs/REGISTRO_DESVIOS.md` | 5.055 | 481.667 | `18e10bca6603351b6faab61871429edc7aa013745bfd02ec4b7a169b898b9731` |
| `bancada_v2_pre_saude.py.txt` | `experiments/bancada_v2.py` | 4.038 | 265.900 | `ebe3bad416fc9bd2b83c289e56789a7fd9564e64a94b0fa541b5f494205b7983` |

**Por que estes nomes** (SA-1, a confirmar pelo Matheus):
- a cópia do CLAUDE.md não se chama `CLAUDE.md`: um `CLAUDE.md` numa subpasta é carregado pelo Claude Code quando ele lê arquivos ali, e
  as instruções antigas voltariam a valer;
- a cópia da bancada termina em `.txt`: assim nenhum teste, preflight ou import a lê como código.

**Para conferir:**

```bash
sha256sum docs/historico/CLAUDE_pre_saude.md docs/historico/REGISTRO_DESVIOS_pre_saude.md docs/historico/bancada_v2_pre_saude.py.txt
git show pre-saude:CLAUDE.md | sha256sum
```

## Para onde foi cada coisa

Este mapa cresce a cada etapa: a etapa que mover um trecho escreve aqui de onde saiu e para onde foi.

| etapa | o que saiu de onde | para onde |
|---|---|---|
| 0 (backup) | nada saiu | — |
