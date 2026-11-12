# TAREFA V3 — SONO_SEGURA (2026-11-11)

Coordenador: o Gerente da V3. Worker: Claude Code (Opus 5.5), sessão lateral. Worktree e branch: `v3-sono-segura`. Status: CÓDIGO PRONTO (branch `v3-sono-segura`, sem PR aberto; o PR é do coordenador).

Categoria: implementacao. Origem: Matheus, 2026-11-11: o sono do modular segura ate a energia passar de 90%.

## 1. Pergunta

O sono do DigiBrain modular (o cérebro dos ovos novos) é picado: o reflexo do sono só força o dormir com a energia abaixo de
`lambda_sono` (S/4), e acima disso o dormir disputa com as outras opções a cada decisão (15 min de jogo) e perde assim que a energia sobe
um pouco. Medido na `main` em 2026-11-11 (sementes 101, 202 e 303, 4 dias, o pet alimentado): 37 a 39 % do tempo dormindo em ~80 cochilos de
15 a 45 min, e o pet nunca dorme até descansar. A decisão do Matheus (2026-11-11, aprovada): **a histerese do sono**. O pet que dormiu segue
dormindo até a energia passar de 90 %; só acorda antes pela fome urgente ou pelo dono que o acorda. Não é run de pesquisa: é uma regra do
produto, atrás de chave.

## 2. Depende de

A `main` em 0b319dd3 (a v26 do grupo, #837, e a v25 da memória longa, #843, já entraram). A decisão da histerese (Matheus, 2026-11-11).

## 3. Mudança mínima

- **Python:** `digilab/config.py` ganha a `ConfigSonoSegura` (`ligada`, desligada por padrão; `lambda_acordar` = 922, o primeiro inteiro
  acima de 0,9 S), com o status em `PARAMETROS_SONO_SEGURA`. Fica numa config própria, como a `ConfigLutaMemoria`, para o dump do modular
  (o gabarito `digibrain_modular_constantes.json`) não mudar. `digilab/digibrain/arb.py`: o `Arbitragem.reflexo(sens, urgencias)` com a
  chave ligada também vale com o pet dormindo (`sens["contexto"]["dormindo"]`, o `dormindo` do vetor de estado que o M-SENS já lê), a
  energia abaixo de `lambda_acordar` e a urgência da fome no máximo `urgencia_lambda` (a guarda do passeio, AN-4). Abaixo de
  `lambda_sono`, o reflexo de sempre, com fome ou sem. `digilab/digibrain/adapt.py`: o `DigiBrain(cfg_sono=...)` e a chamada do reflexo
  com as urgências do M-AFETO (só com a chave ligada; desligada, a chamada de hoje, para o gravador do exportador não mudar).
  `experiments/run_v2_digibrain_prototipo.py`: o `sono` opcional em `fabricas` e `viver`.
- **TS:** `web/app/motor/digibrain/constantes.ts` (`CONFIG_SONO_SEGURA`, `CONFIG_SONO_SEGURA_LIGADA`), `arb.ts` e `adapt.ts` (o espelho),
  `motor/constantes.ts` (a **v27**: `VERSAO_PET` = 27, `VERSAO_V27`, `nasceComSonoSegura`, e a v27 nas listas `VERSOES_PET`,
  `ehCerebroTrocavel`, `ehLutaPoc`, `ehLutaV23`, `nasceNaGrande` e `nasceComMemoriaLonga`: a v27 é a v25 com o sono que segura) e
  `motor/motor.ts` (o modular do pet v27 nasce com a chave ligada).
- **Não muda:** `digilab/engine.py`; o motor do corpo e do mundo; as versões de pet v21 a v26 e os gabaritos delas; o cérebro A; o pet do
  laboratório (v16); as ações do dono (o brincar do dono acorda o pet como hoje, tirando o `dormindo`).

## 4. Experimento e gate (se houver run)

Sem run de pesquisa e sem faixa de sementes: a medida antes/depois usa as sementes dos testes (101, 202 e 303) e roda num teste
(`web/app/test/sono_segura_medida.test.ts`). Sem gate: o teste só confere que a v27 tem menos cochilos depois do dia 1 e acorda mais
descansada que a v25 em cada semente.

## 5. Entrega

- Testes: `python -m pytest tests/ -q`; em `web/app`: `npm test`, `npm run tipos`, `npm run e2e` (se a frente toca a web).
- Registro: seção própria no fim do arquivo do mês, `docs/registro/AAAA-MM.md` (rodada de saúde, etapa 2). **Não edite o índice
  `docs/REGISTRO_DESVIOS.md`:** ele é gerado (`python tools/gerar_indice_desvios.py`) por quem faz o merge. Um conflito nele se resolve
  rodando o gerador, nunca à mão (`docs/TAREFA_V3_INDICE_DESVIOS.md`). O resumo da etapa vai no corpo do PR e numa seção no fim do documento da
  frente (o `RESULTADO_V3_*.md` da run ou o `TAREFA_V3_*.md` da etapa), nunca no `CLAUDE.md` (rodada de saúde, etapa 1).
- PR contra a `main` com resumo e números (cada um com o artefato). Aviso ao coordenador. Merge só pelo Matheus.
- O corpo do PR segue `.github/pull_request_template.md`; o CI (`tools/verificar_relato.py`) confere os campos e a evidência da categoria.

## 6. Fora desta tarefa

- O grupo de dois pets (a v26, o ovo do brasão desde a CO4d, com `DOIS_OVOS_LIGADO`): fica sem o sono que segura. Levar a histerese ao
  grupo pede uma versão nova do grupo (D-SONO-4 e a seção 8).
- A calibração do `lambda_acordar` e da fome urgente (a rodada de equilíbrio do fim).
- Nenhuma ação nova do dono.

## 7. Critérios de aceitação

- `tests/test_gabarito_sono_segura.py` (o gabarito de hoje, gravado num commit próprio antes da mudança) passa: a chave desligada dá as
  vidas de hoje byte a byte.
- `tests/test_sono_segura.py`: a config, o reflexo caso a caso, a vida em que o pet dormindo só acorda acima de `lambda_acordar`, pela fome
  urgente ou pelo brincar do dono, o replay e o gabarito do TS em dia.
- `web/app/test/digibrain_modular_sono_segura.test.ts`: o G-PAR das três vidas do Python com a chave ligada
  (`test/gabaritos/digibrain_modular_sono_segura.json.gz`), decisão a decisão, e a v27 com o modular ligado.
- `web/app/test/sono_segura_medida.test.ts`: a tabela da seção 9.

## 8. Precisa do Matheus

- **O grupo (v26) com o sono que segura?** Os ovos do brasão nascem hoje no grupo (v26), que fica com o sono de antes; só o ovo de um pet
  só (a herança, o pet de exemplo, o ovo novo com `DOIS_OVOS_LIGADO` desligado) nasce v27. Recomendação: uma v28 = a v26 com o sono que
  segura, numa etapa curta (o `GrupoDoJogo` monta os dois pets com a versão dele). Custo de errar: baixo; até lá, o pet que o jogador vê no
  ovo do brasão continua com o sono picado.
- Os números (`lambda_acordar` = 922, a fome urgente pelo `urgencia_lambda`) seguem PROPOSTOS.

## 9. Resultado da etapa de código (2026-11-11)

O sono que segura está no Python (`ConfigSonoSegura`, o reflexo do M-ARB) e no jogo (a v27), atrás da chave desligada; a vida de hoje sai
byte a byte (`tests/test_gabarito_sono_segura.py`, 64 vidas de quatro braços, gravadas no commit 26f7ad8f antes da mudança). O G-PAR das
três vidas do Python com a chave ligada passa no Node decisão a decisão (`web/app/test/digibrain_modular_sono_segura.test.ts`, 1 152
decisões).

A medida (o pet do jogo com o modular, 4 dias, um tick por vez, alimentado com a fome abaixo de 0,5 e limpo com a sujeira em 2 ou mais;
`web/app/test/sono_segura_medida.test.ts`, a tabela no console; a energia é a do estado do pet, `m.e.energia`):

| versão | semente | % dormindo | cochilos | cochilos depois do dia 1 | energia mediana no começo do sono | no fim |
|---|---|---|---|---|---|---|
| v25 | 101 | 39,8 | 85 | 70 | 0,35 | 0,45 |
| v25 | 202 | 39,6 | 86 | 72 | 0,31 | 0,42 |
| v25 | 303 | 39,8 | 94 | 78 | 0,33 | 0,43 |
| v27 | 101 | 43,5 | 21 | 16 | 0,48 | 0,93 |
| v27 | 202 | 42,7 | 20 | 15 | 0,48 | 0,94 |
| v27 | 303 | 43,5 | 18 | 14 | 0,44 | 0,93 |

O pet da v27 dorme em cerca de um quarto dos cochilos e acorda descansado (a mediana acima de 0,9); o tempo dormindo sobe de ~40 % para
~43 %. Os desvios estão em `docs/registro/2026-11.md` (D-SONO-1 a D-SONO-6).
