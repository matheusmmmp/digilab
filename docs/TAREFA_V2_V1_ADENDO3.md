# TAREFA V2 — V1-ADENDO3: o orquestrador da validação com o adendo 3 (2026-10-06)

Coordenador: chat "Principais jogos Digimon com diálogo". Worker: chat B. Worktree e branch: `v2-v1-adendo3`. Status: ABERTA. Continua
`docs/TAREFA_V2_V1_VALIDACAO_UNICA.md`, cuja config e orquestrador entraram no #183, sem rodar.

## 1. O que fazer, sem rodar nas sementes de validação

**O bloco de durações** (adendo 3, seção 3.1):
- P0 e P1, no descasado e no mutável, nas unidades da validação;
- durações de 7 dias e da maior entre 28 e 21 dias, além dos 14 dias de sempre;
- secundário e descritivo: a forma da curva com IC por bootstrap, fora do Holm.

**O custo:** calcule o tempo total da validação com o bloco, pelo tempo por vida da calibração conjunta
(`artifacts_v2_calibracao_conjunta/`), escolha a duração maior pela regra do adendo e grave o cálculo num artefato. Se nem 21 dias couber
no teto de 12 h, pare e pergunte pelo PR.

**Os braços secundários P2d e P3i** (adendo 3, seção 3.3):
- os contrastes P2 − P2d e P3 − P3i, com IC 95%, sem Holm;
- a contagem e o multiconjunto das informações por braço.

Eles dependem do PR da bancada (chat D, `docs/TAREFA_V2_P2D_P3I.md`). Deixe o lugar pronto; depois do merge desse PR, atualize o branch e
ligue os dois braços.

**O relatório:**
- a limitação do mutável (adendo 3, seção 3.2);
- o apoio teórico de cada predição, na leitura, sem mudar a regra de decisão.

**Testes:** só com fumaça nas sementes dos testes.

## 2. A run

Uma vez, nas sementes 15101…15505, **só com o sinal verde do coordenador**, depois do merge da bancada do P2d e do P3i. O resultado vai em
`docs/RESULTADO_V2_VALIDACAO_UNICA.md`.

## 3. Entrega

Um PR com a preparação; a run vai no mesmo PR ou num seguinte, como preferir, com o relato no corpo. A suíte inteira roda, e há uma seção
no fim do `CLAUDE.md` e outra no fim do `REGISTRO_DESVIOS.md`. Merge só pelo Matheus.
