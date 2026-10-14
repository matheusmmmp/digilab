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
| 1 (CLAUDE.md enxuto) | as 135 seções do `CLAUDE.md`, inteiras e na ordem de antes dentro de cada destino | a tabela abaixo; seção a seção em `docs/historico/mapa_claude.json` |

**Etapa 1: os destinos das seções do CLAUDE.md.** A conferência é `python tools/conferir_saude.py` (G-NADA-PERDIDO): cada seção da cópia
`CLAUDE_pre_saude.md` está inteira no destino que o mapa dá a ela.

| destino | seções | o que tem |
|---|---|---|
| `docs/historico/claude/fundacao.md` | 5 | o preâmbulo, "O que é", as regras, o trabalho em paralelo e a arquitetura, como eram |
| `docs/MAPA_REPOSITORIO.md` | 2 | o mapa do repositório arquivo a arquivo e a lista de comandos |
| `docs/historico/claude/v1_pesquisa.md` | 14 | a arena v1, a ablação, a reprodutibilidade, o poder, a confirmatória, a linhagem, a pergunta do dono e a personalidade |
| `docs/historico/claude/combate.md` | 10 | o combate V2 e V2.1, a campanha, as correções, o reequilíbrio, o equilíbrio geral, o M1, o treino e a escala |
| `docs/historico/claude/jogo_web.md` | 10 | a evolução canônica, as medalhas, as arenas, os itens, a Fronteira, a escala v6, a versão web e os assets |
| `docs/historico/claude/fala.md` | 2 | a fala por LLM e a fala livre |
| `docs/historico/claude/pendencias.md` | 1 | as pendências e ideias registradas até 2026-10-13 |
| `docs/historico/claude/v2_aprendiz.md` | 39 | a V2 da L0 ao descritivo do platô (2026-10-01 a 2026-10-07) |
| `docs/historico/claude/v2_mundo_corpo.md` | 52 + 4 | a V2 da prancha do mapa à rede de si na bancada (2026-10-07 a 2026-10-13); as 4 a mais vieram depois da cópia |

**As seções que entraram no CLAUDE.md antigo depois da cópia** (#298, #299, #301 e #302, na `main` `f23ba37`) foram movidas no merge para
o fim do `v2_mundo_corpo.md`. O mapa delas fica em `docs/historico/mapa_claude_posteriores.json`, por lote (o commit e as seções). A
conferência lê o CLAUDE.md do commit pelo git: ele só pode ter as seções da cópia, iguais, e as do lote, cada uma inteira no destino.
Um PR aberto que ainda traga seção para o CLAUDE.md ganha um lote novo no merge.

O `CLAUDE.md` novo da raiz e os de `web/app/` e `servidor/` são texto novo, escrito pelo critério "se tirar, o Claude erra?".
