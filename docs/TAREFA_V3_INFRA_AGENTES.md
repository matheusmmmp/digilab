# TAREFA V3 — INFRA_AGENTES (2026-11-06)

Coordenador: Matheus. Worker: Claude Code (sessão do especificador, worktree `v3-infra-agentes`, Opus 5.5). Worktree e branch:
`v3-infra-agentes`. Status: ABERTA (a especificação; nenhuma etapa implementada).

Categoria: arquitetura. Origem: Matheus, 2026-11-06: gates impostos pelo harness e revisores novos por lente para o desenvolvimento do
cérebro e do jogo: hooks restaurados, agentes somente leitura, gate de pré-run, testador de navegador isolado, CI do web.

Tudo aqui é **PROPOSTO** até o Matheus decidir (seção 8). As D-IA-1 a D-IA-7 estão **DECIDIDAS** (seção 8.1).

## 1. Pergunta

As regras não negociáveis do `CLAUDE.md` e as do método (sementes, plano antes da run, V3-D8) podem ser impostas pela ferramenta (hooks,
scripts, CI) em vez de pedidas ao modelo, e os revisores podem ser agentes somente leitura com lente fixa? Não vem de uma hipótese do
`docs/PLANO_V2_PESQUISA.md`: é infraestrutura do processo, para as três trilhas da V3.

**Por que vale o custo (a escada):** um erro pego na tarefa custa zero; no código, uma revisão; no teste, a suíte de ~36 min; numa run, uma
faixa de sementes queimada que não volta (`FAIXAS_QUEIMADAS`); depois do merge, a `main`. Cada etapa abaixo empurra um tipo de erro para um
degrau mais barato.

### 1.1 O que a sessão conferiu no código antes de escrever

- **O que os hooks antigos faziam** (lidos com `git show 2586b0e~1:.claude/hooks/<arquivo>`; o `2586b0e` é o commit da H2 do habitat, que os
  apagou junto com a ilha 3D):

  | hook | evento e matcher | o que faz | ligado em 2026-10-14 (`fd62d39`) |
  |---|---|---|---|
  | `_comum.py` | — | lê o evento do stdin, acha a raiz (`CLAUDE_PROJECT_DIR`, senão o `cwd`), `bloquear` (código 2, motivo em UTF-8 no stderr), `perguntar` (o `ask` em JSON), `sha_do_engine` lido como texto | — |
  | H1 `h1_engine.py` | `PreToolUse`, `Edit\|Write\|MultiEdit\|NotebookEdit` | nega editar `digilab/engine.py` (caminho relativo, absoluto ou com `..`) | sim |
  | H1b `h1b_engine_sha.py` | `Stop` | o sha256 do `engine.py` contra o `ENGINE_SHA256_V0`; pega a mudança feita por shell; não bloqueia duas vezes (`stop_hook_active`) | sim |
  | H2 `h2_testes.py` | `Stop` | com mudança em `digilab/`, `experiments/` ou `tests/`: roda os testes mudados, o `tests/test_<x>.py` de cada módulo mudado e os testes que citam um gabarito mudado; limite de 600 s; não bloqueia duas vezes pela mesma assinatura de falha | **não** (só na proposta) |
  | H3 `h3_main.py` | `PreToolUse`, `Bash\|PowerShell` | `ask` no `gh pr merge` e no `git push` que manda para a `main` | sim |
  | H4 `h4_autorizo.py` | `PreToolUse`, `Bash\|PowerShell` | código 2 no comando (ou arquivo de corpo do `gh`) com "AUTORIZO IMPLEMENTAÇÃO" (IM-8) | **não** (só na proposta, `docs/propostas/hooks_settings.json`) |

- **Por que a suíte acusa 43 falhas:** os testes `tests/test_hooks.py` (15 funções, 32 casos com os parâmetros) e `tests/test_hook_h4.py`
  (5 funções, 14 casos) rodam os scripts de `.claude/hooks/` direto, como o Claude Code rodaria. Sem os arquivos, o Python sai com "can't
  open file", código 2. Medido nesta sessão: `python -m pytest tests/test_hooks.py tests/test_hook_h4.py -q -p no:cacheprovider` →
  **43 failed, 3 passed**. Os 3 que passam são os `test_h1_nega_o_engine[...]`, por acaso: esperam código 2, e o "arquivo não existe"
  também dá 2. O `test_proposta_e_os_hooks_ligados` falha porque o `.claude/settings.json` não existe.
- **A restauração já existe noutra frente:** o PR #590 (UX_TELA_PET A0, branch `v3-hooks-a0`, empilhado sobre o #589, aberto) traz os
  sete arquivos iguais aos de `2586b0e~1` (`git diff 2586b0e~1 origin/v3-hooks-a0 -- .claude/` vazio) e registra a decisão do Matheus de
  religar H1, H1b e H3. O #589 (UX_TELA_PET etapa 0, aberto) já desenha hooks e agentes que cruzam com esta frente: **H5** `h5_web.py`
  (Stop do web), **H6** `h6_capturas.py` (nega `*-snapshots/` e a pasta das referências), **H8** `h8_escopo.py` (escopo de escrita por
  agente), o `ux-browser-tester` (o mesmo papel da E4) e o `rev-replay` (parte da lente da E2). O número H7 ficou livre de propósito. A
  divisão entre as duas frentes é a D-IA-5.
- **As referências visuais não estão no git:** não há nenhuma pasta `*-snapshots/` versionada em `web/app/`; as capturas do portão ficam em
  `DIGILAB_CAPTURAS` (padrão `../../artifacts_v2_front_react/capturas/`, o `snapshotPathTemplate` do `playwright.capturas.config.ts`).
  E os sete specs de `web/app/e2e/` leem `/Assets/...` (o atlas dos sprites), que fica em `D:\Trab\digilab\Assets`, fora do git
  (`git ls-files Assets` vazio). Isso decide a E5 (D-IA-3).
- **Os orquestradores:** 26 `experiments/run_v2_*.py` e já um `experiments/run_v3_acoes_novas.py`. Só 4 declaram uma constante `FAIXA`;
  6 chamam o `exigir_adendo_aprovado`; o limite de 4 processos está escrito à mão em alguns (`run_v2_habito_intencao.py`,
  `run_v2_digibrain_l2.py`, `longe_l0_digibrain.py`). As configs novas (`experiments/configs/v3_acoes_novas/*.json`) já trazem `plano` e
  `unidades.bases`, e a varredura usa as bases 101…505 dos testes.

## 2. Depende de

- **A E1 depende do #590 na `main`** (ou da D-IA-5 dizer outra coisa): a restauração dos H1–H4 não se refaz aqui.
- As decisões D-IA-1 a D-IA-7 (seção 8). Cada etapa diz quais precisa.
- A E4 e a E5 não dependem da E1–E3 entre si; a ordem pedida é E1 → E5, um PR por etapa.

## 3. Mudança mínima

**Fronteiras de todas as etapas:** `digilab/engine.py` não muda; nenhuma vida, gabarito, versão de pet ou run antiga muda; o `CLAUDE.md`
não muda; os orquestradores `run_v2_*` da V2 congelada não mudam. Todo hook novo é Python só com a biblioteca padrão, usa o `_comum.py`,
falha alto (evento sem stdin levanta) e entra **desligado**, como proposta em `docs/propostas/hooks_settings.json`; só o Matheus o liga
em `.claude/settings.json` (SA-5; D-IA-7). Este PR só muda este documento e o registro do mês.

### 3.1 E1 — os hooks restaurados e dois novos

**Mudança mínima**

1. Os sete arquivos apagados pelo `2586b0e` voltam (`git show 2586b0e~1:<caminho>`), **pelo #590**: se ele estiver na `main`, a E1 parte
   dele; se não, a E1 traz os mesmos bytes e o #590 é fechado sem merge (D-IA-5).
2. **O Stop dos testes: o H2 estendido** (`.claude/hooks/h2_testes.py`), em vez de um hook novo, porque o H2 já tem o conjunto rápido, o
   limite de tempo e a guarda contra prender a sessão. Acrescenta ao conjunto que ele já monta:
   - **os testes de replay**, uma lista fixa no próprio hook (D-IA-1): `tests/test_engine.py`, `tests/test_gabarito_*.py`,
     `tests/test_gabaritos_*.py`, `tests/test_p4_gabaritos.py`, `tests/test_passeio_gabarito.py` (22 arquivos hoje; medido nesta
     sessão: 108 passed in 424.91s, ~7 min, os quatro mais lentos os `byte_a_byte` do DigiBrain, de 37 a 58 s), **só quando o turno mudou
     `digilab/` ou `experiments/bancada/`** (o código que pode mudar uma vida);
   - **os testes da frente:** `tests/test_<frente>*.py`, com a frente tirada do branch `v3-<frente>` (hífen vira sublinhado), se existir;
   - continua só rodando quando o `git status` mostra mudança em `digilab/`, `experiments/` ou `tests/` (sem isso, nenhum teste no Stop de
     uma sessão que só escreveu documento).
   Em falha, código 2 com o resumo do pytest (as últimas 15 linhas), como hoje. O `stop_hook_active` e a assinatura repetida continuam
   deixando encerrar. O limite `DIGILAB_H2_LIMITE_S` continua 600 s; **estourado, hoje o H2 deixa passar em silêncio** (`except
   TimeoutExpired: return`): a E1 troca por código 2 com "o Stop passou de N s; rode a suíte da frente antes do PR", uma vez por sessão
   (falhar alto).
3. **O H6 `h6_capturas.py`** (`PreToolUse`, `Edit|Write|MultiEdit|NotebookEdit` e `Bash|PowerShell`), com o desenho da seção 3.3 do
   `docs/TAREFA_V3_UX_TELA_PET.md` (#589): código 2 ao escrever, mover ou apagar em qualquer `*-snapshots/` e na pasta de
   `DIGILAB_CAPTURAS`; `ask` num comando com `--update-snapshots` ou `-u` do Playwright. Feito aqui uma vez só (D-IA-5).
4. **O H9 `h9_faixas.py`** (`PreToolUse`, `Edit|Write|MultiEdit`), só para `experiments/bancada/faixas.py`: aplica a edição pedida ao texto
   do arquivo em memória (o `old_string`/`new_string` do Edit, os pares do MultiEdit, o `content` do Write), lê a tupla
   `FAIXAS_QUEIMADAS` antes e depois pela AST (`ast.literal_eval` do valor) e:
   - código 2 se alguma entrada de antes sumiu ou mudou (faixa queimada não volta);
   - `ask` se só entraram entradas novas no fim (queimar uma faixa é legítimo, mas pede o Matheus; D-IA-4);
   - deixa passar se a tupla não mudou (as `FAIXAS_RESERVADAS` continuam editáveis: o coordenador reserva faixa nova).
   O H9 não vê `sed` pelo shell; o que pega esse caso é o **H1b estendido**: no Stop, a tupla do disco tem de conter, na ordem, a do
   `origin/main` (`git show origin/main:experiments/bancada/faixas.py`), senão código 2.
5. Os casos novos em `tests/test_hooks.py` (o evento no stdin, o código de saída, no repositório pequeno da fixture `projeto`) e o
   `test_proposta_e_os_hooks_ligados` atualizado para a proposta com H6 e H9 e para o que o Matheus ligar.

**Critério de aceitação**

```bash
python -m pytest tests/test_hooks.py tests/test_hook_h4.py -q -p no:cacheprovider   # 0 failed (hoje 43 failed, 3 passed), com os casos novos
python -m pytest tests/test_hooks.py -q -k "h2_replay or h2_frente or h2_estouro"   # o H2 roda a lista de replay, a da frente e falha alto no limite
python -m pytest tests/test_hooks.py -q -k "h6 or h9"                               # snapshots negados, --update-snapshots pergunta, queimada removida nega, queimada nova pergunta, reservada passa
python -m pytest tests/test_engine.py -q                                            # o sha do engine intacto
```

e, à mão, uma vez, o registro no relato do PR: um evento simulado de Edit que apaga uma linha de `FAIXAS_QUEIMADAS` sai com código 2.

**Fica fora:** o H5 (o Stop do web) e o H8 (o escopo por agente), que são da UX_TELA_PET A1; ligar qualquer hook (D-IA-7); impedir um
`git commit` que mexa nos protegidos (a proteção de verdade continua nos testes e no CI).

### 3.2 E2 — três agentes revisores, somente leitura

**Mudança mínima.** Três arquivos novos em `.claude/agents/`, no formato de subagente do Claude Code (frontmatter `name`, `description`,
`tools`, `disallowedTools`, `model`). Todos com `tools: Read, Grep, Glob` (o `Bash` só onde está dito, e então só leitura, imposto pelo
`h8_escopo.py <papel>` da UX quando ele existir; até lá, sem `Bash`) e `disallowedTools: Edit, Write, MultiEdit, NotebookEdit`. Cada um
recebe o diff ou o arquivo, não a conversa; cada achado sai com arquivo:linha, o cenário que falha e a evidência; achado sem isso o
coordenador descarta. Nenhum aprova nada: o gate continua nos testes.

| agente | modelo | a lente fixa | o que confere, no mínimo |
|---|---|---|---|
| `revisor-metodo.md` | Opus | o método | sementes: só as de teste (101…505 e as pequenas) ou de uma faixa em `FAIXAS_RESERVADAS`, nunca de `FAIXAS_QUEIMADAS`; calibração só nas sementes dela, separada da validação, e a validação uma vez; o plano de análise (`docs/PLANO_ANALISE_V3_*.md` ou o adendo) commitado antes da primeira vida (`git log` do plano contra o da run); todo número novo PROPOSTO, todo parâmetro com fonte ou SEM FONTE; nenhuma alegação de novidade; toda referência conferida pela skill `literatura-digilab` (o frontmatter carrega a skill) |
| `revisor-determinismo.md` | Opus | o determinismo | cada fluxo novo de acaso com a rng dele, por `derivar_semente`, e a de ambiente separada da de política; nenhum `random` global, `time`, `hash()` de string ou ordem de `set` chegando ao estado; mecânica nova atrás de chave desligada, com o gabarito gravado num commit anterior e um teste que confere byte a byte; paridade Python/web: a constante nova no `constantes.test.mjs`, o gabarito exportado por `experiments/exportar_*.py`, o teste de paridade no Node; `engine.py` intacto. Na web, a lente do `rev-replay` da UX (o motor só por `mudarMotor()`, nada de `Math.random`/`Date.now` no estado) entra aqui ou fica lá (D-IA-5) |
| `auditor-numeros.md` | Sonnet | os números | cada número de um `docs/RESULTADO_V3_*.md` (ou do corpo do PR) contra o artefato em disco que o produz (o `resumo.json`, o `.csv`, o log da run): classifica cada um como **VERIFICADO** (o artefato dá o mesmo valor no arredondamento do texto), **DIVERGENTE** (dá outro, com os dois valores) ou **SEM FONTE** (nenhum artefato achado); devolve a tabela número a número. Pode ler com `Bash` só para abrir JSON/CSV (`python -c` de leitura, imposto pelo H8 quando existir) |

**Critério de aceitação**

```bash
python -m pytest tests/test_agentes.py -q
```

um teste novo que lê os três frontmatters e confere: os três arquivos existem; `name` igual ao nome do arquivo; nenhum tem `Edit`, `Write`,
`MultiEdit` ou `NotebookEdit` em `tools`, e os quatro estão em `disallowedTools`; o `revisor-metodo` cita a skill `literatura-digilab`; o
`auditor-numeros` cita as três classes. E, uma vez, no relato: o `auditor-numeros` rodado sobre o `docs/RESULTADO_V3_ACOES_NOVAS.md`,
com a contagem de cada classe.

**Fica fora:** os agentes da UX (`ux-designer`, `ux-implementador`, `rev-a11y`, `rev-cena`); mudar o `/code-review`; rodar os revisores
automaticamente num hook (são chamados pelo coordenador).

### 3.3 E3 — `tools/pre_run.py`, o gate antes da run

**Mudança mínima.** Um script novo, só biblioteca padrão, `python tools/pre_run.py <orquestrador> --config <json> [--processos N]`,
que sai com código 0 ou com código 2 e o motivo. Recusa a run quando:

1. **o plano não está commitado:** o caminho do campo `plano` da config não está no `git ls-files`, tem mudança não commitada
   (`git status --porcelain -- <plano>` não vazio) ou (D-IA-6) o commit que o pôs não está no `origin/main`;
2. **a faixa não é reservada:** alguma base de `unidades.bases` fora de 101…505 que não cai numa faixa de `FAIXAS_RESERVADAS`, ou alguma
   base numa faixa de `FAIXAS_QUEIMADAS` (lidas pela AST de `experiments/bancada/faixas.py`, sem importar a bancada). Bases só de
   teste (a varredura e a fumaça) passam sem faixa;
3. **há outra run em andamento:** algum processo Python com `experiments/run_v[23]_*.py` na linha de comando (no Windows, pelo
   `Get-CimInstance Win32_Process` chamado pelo `subprocess`; sem trava em arquivo, que fica órfã quando a run cai);
4. **passam de 4 processos** (`--processos` > 4; V3-D8);
5. **a config não tem `plano` ou `unidades.bases`:** falha alto, em vez de deixar passar (as configs da V2 congelada não têm; elas não rodam
   mais).

O gancho: o **H10 `h10_pre_run.py`** (`PreToolUse`, `Bash|PowerShell`) acha no comando `python … experiments/run_v[23]_*.py` (o padrão
pedido era `run_v2_*`; o `run_v3_acoes_novas.py` já existe, então o hook pega os dois), tira o `--config` e o `--processos` e chama o
`pre_run.py`; código 2 com o motivo se ele recusar. O `pre_run.py` não roda nada da run. Se entra também nos orquestradores é a D-IA-2.

**Critério de aceitação**

```bash
python -m pytest tests/test_pre_run.py -q
```

com um caso por recusa (plano fora do git, plano sujo, base fora da faixa, base queimada, outra run simulada, 5 processos, config sem
`plano`) e dois que passam (a `varredura.json` das sementes de teste; a `acoes_novas.json` com a faixa 78xxx); e, no relato,
`python tools/pre_run.py experiments/run_v3_acoes_novas.py --config experiments/configs/v3_acoes_novas/varredura.json --processos 4` → 0, e
o mesmo com `--processos 5` → 2. Os casos do H10 entram em `tests/test_hooks.py`.

**Fica fora:** mexer nos `run_v2_*` (V2 congelada); a fila de runs; as medições do combate (`tools/medir_*`, que a V3-D8 também conta): o
padrão delas fica como questão aberta.

### 3.4 E4 — `testador-navegador.md`

**Mudança mínima.** `.claude/agents/testador-navegador.md`, modelo Sonnet (rodar é mecânico, a triagem do diff pensa; escala para Opus se
errar a triagem duas vezes no mesmo PR), `tools: Read, Grep, Glob, Bash`, `disallowedTools: Edit, Write, MultiEdit, NotebookEdit`. O
`Bash` limitado pelo `h8_escopo.py testador` da UX quando ele existir; até lá, pela lista no próprio prompt e pelo H6 (que já nega
`--update-snapshots` sem o Matheus). O que faz, pela receita de `web/app/CLAUDE.md` e do `playwright.config.ts`:

- `npm run tipos`, `npm test` (Vitest) e `npm run e2e` (o build e o `playwright test`, que sobe o `servidor/servidor_local.py --provedor
  nenhum` pelo `webServer`), com `DIGILAB_PORTA_E2E` próprio da worktree; três workers mais o servidor, quatro processos (V3-D8);
- as capturas (`npm run capturas`) só quando o pedido disser;
- **devolve só:** os testes que falharam (arquivo, nome, largura, pele), o caminho de cada `*-actual.png`, `*-expected.png` e
  `*-diff.png`, o número de pixels diferentes, e os trechos de `console` e `pageerror` dos testes que falharam. Nada do log que passou.

É o mesmo papel do `ux-browser-tester` do #589 (com a classificação de diff dele, que nunca aprova); fica um arquivo só (D-IA-5).

**Critério de aceitação:** o `tests/test_agentes.py` da E2 ganha o testador (sem ferramenta de escrita, cita `npm run e2e` e
`DIGILAB_PORTA_E2E`); e, uma vez, no relato: o testador chamado numa worktree com um e2e quebrado de propósito (num branch descartável)
devolve o nome do teste e o trecho do erro, e na `main` devolve "nenhuma falha".

**Fica fora:** o Playwright MCP (UX-6 é decisão da UX); escrever ou atualizar referência; o projeto `software` das capturas.

### 3.5 E5 — o job web no `verificar-pr.yml`

**Mudança mínima.** Um job `web` em `.github/workflows/verificar-pr.yml`, no `pull_request`, que só roda quando o PR muda `web/app/`
(um passo que olha o `git diff --name-only origin/$BASE_REF...HEAD -- web/app/` e sai cedo; o filtro `paths:` não serve porque vale para o
workflow inteiro e tiraria o job `relato`). Os passos: `actions/setup-node` com o Node 24 (o `engines` do `web/app/package.json`), `npm ci`,
`npm run tipos`, `npm test`, `npm run build`. **O e2e fica fora do CI** (D-IA-3): os sete specs leem o atlas de `D:\Trab\digilab\Assets`,
fora do git, e as referências das capturas também estão fora do git. Sem secrets, `permissions: contents: read`, como o resto do workflow.

**Critério de aceitação:** o job verde num PR que muda um arquivo de `web/app/` e ausente (pulado) num PR só de documentos, os dois
visíveis no `gh pr checks`; e o `npm test` sem o `Assets` passando (os testes que precisam dele pulam com aviso, como o
`atlas_acoes_real.test.ts`; se algum quebrar sem o `Assets`, a E5 o põe no mesmo padrão de `skipIf`, sem mudar o que ele confere).

**Fica fora:** o e2e e as capturas no CI; o runner Windows para o web (a paridade bit a bit é no Node, que é o mesmo V8 nos dois; se o
`npm test` divergir no Linux, isso vira achado no registro, não conserto aqui).

## 4. Experimento e gate (se houver run)

Nenhuma run. Nenhuma semente.

## 5. Entrega

- Este PR: só este documento e a seção do registro de 2026-11 (os achados da seção 1.1). Categoria arquitetura; o corpo pelo
  `.github/pull_request_template.md`, conferido com `python tools/verificar_relato.py`.
- Cada etapa E1 a E5: um PR próprio, nesta ordem, categoria implementacao, com os testes da seção da etapa no corpo e o resumo da etapa numa
  seção no fim deste documento. Merge só pelo Matheus.

## 6. Fora desta tarefa

- O `CLAUDE.md` (a regra continua escrita lá; o hook só a impõe).
- O H5, o H8 e os agentes da UX_TELA_PET, menos o que a D-IA-5 passar para cá.
- Ligar hooks em `.claude/settings.json`: é do Matheus (SA-5).
- Proteção de branch no GitHub e permissões do repositório.
- Retrofit dos orquestradores da V2.

## 7. Critérios de aceitação

- Desta especificação: este arquivo sem nenhum `<...>` do modelo; cada etapa com mudança mínima, critério por comando e o que fica fora; as
  decisões da seção 8 com recomendação e custo; `python tools/verificar_relato.py --arquivo <corpo>` sem erro.
- De cada etapa: os comandos da subseção dela.

## 8. Precisa do Matheus

| id | decisão | recomendação | custo de errar |
|---|---|---|---|
| **D-IA-1** (DECIDIDA) | quais testes o Stop roda | **sempre que `digilab/`, `experiments/` ou `tests/` mudou: os da frente e os dos arquivos mudados (o H2 de hoje); a lista fixa de replay (22 arquivos, seção 3.1) só quando mudou `digilab/` ou `experiments/bancada/`**; a suíte inteira continua no PR. Medido nesta sessão: os 22 de replay, `108 passed in 424.91s` (~7 min), abaixo do limite de 600 s do H2 | lista curta demais: um replay quebrado passa até a suíte do PR (36 min depois, ou na `main`); longa demais: cada turno que mexe em código espera minutos, e a sessão aprende a fugir do hook |
| **D-IA-2** (DECIDIDA) | o `pre_run` entra nos orquestradores ou só no hook | **no hook (E3) e, daqui para a frente, nos `run_v3_*` novos, numa linha no começo do `main()`; os `run_v2_*` não mudam** | só no hook: uma run lançada pelo terminal do Matheus ou por outra ferramenta pula o gate e pode queimar uma faixa; em todos os orquestradores: mexe em 26 arquivos da V2 congelada, cada um com teste |
| **D-IA-3** (DECIDIDA) | o e2e visual roda no Linux | **não; no CI só `tipos`, `npm test` e `build`**. O e2e nem roda no CI como está: os sete specs leem o atlas fora do git, e as referências das capturas também estão fora do git (não há `*-snapshots/` versionado). O e2e fica no Stop do web (H5) e no testador | rodar no Linux: referências novas por plataforma, dois conjuntos para aprovar, e o atlas teria de ir ao CI (não pode: arte fora do git); não rodar: uma quebra do e2e só aparece na junção, como hoje (o Gerente roda antes do merge) |
| **D-IA-4** (DECIDIDA) | o H9 diante de uma faixa queimada nova | **código 2 para remover ou alterar; `ask` para acrescentar no fim** | negar tudo: queimar uma faixa depois de uma run caída exige editar fora do Claude Code; deixar acrescentar sem perguntar: um agente pode queimar uma faixa reservada viva por engano |
| **D-IA-5** (DECIDIDA) | a divisão com a UX_TELA_PET (#589, #590) | **a A0 é o #590 (a E1 parte dele, sem refazer); o H6 é feito uma vez, aqui, com o desenho da UX; o H5 e o H8 ficam na UX A1; o `testador-navegador` é o `ux-browser-tester` (um arquivo, o daqui, que a UX A2 referencia); a lente do `rev-replay` na web fica na UX, e o `revisor-determinismo` cobre o Python e a paridade** | duas frentes escrevendo o mesmo hook ou o mesmo agente: dois H6 com regras diferentes, dois testadores, e um merge que apaga o outro (como o `2586b0e` apagou os hooks) |
| **D-IA-6** (DECIDIDA) | o que é "plano commitado" no `pre_run` | **o commit do plano alcançável do `origin/main`**, não só no branch | só no branch: uma run roda sobre um plano que o Matheus não aprovou na `main`; no `origin/main`: um `git fetch` velho recusa uma run legítima (o motivo diz "rode `git fetch`") |
| **D-IA-7** (DECIDIDA) | quais hooks ligar, e quando | **H6, H9 e H10 ao mergear a etapa (são baratos, só leem o evento); o H2 estendido depois da medida do Stop na E1; o H4 junto (está pronto desde o IM-8)** | ligar o Stop sem medir: turnos lentos; não ligar: a regra volta a ser só pedido no prompt, que é o problema desta frente |

### 8.1 Decididas

- **D-IA-1, D-IA-4, D-IA-5 e D-IA-7: DECIDIDAS pela recomendação** (Matheus, 2026-11-06, nesta sessão: "das suas recomendações", ao
  pedir o prompt da E1, e "Empilhar sobre o #590"). A E1 sai empilhada sobre o #590 (branch `v3-hooks-a0`), que ainda não está na `main`.
- **D-IA-2, D-IA-3 e D-IA-6: DECIDIDAS pela recomendação** (Matheus, 2026-11-06, "segue com as recomendações", depois da E1): o
  `pre_run` no hook e nos `run_v3_*` novos; no CI do web só `tipos`, `npm test` e `build`; o plano exigido no `origin/main`.

## 9. Resumo da etapa E1 (2026-11-06)

Worker: Claude Code, Opus 5.5, worktree `v3-infra-agentes-e1`, branch empilhado sobre o #590 (`v3-hooks-a0`) e o #601.

- **O H2 estendido** (`.claude/hooks/h2_testes.py`): a lista fixa de replay (só com mudança em `digilab/` ou `experiments/bancada/`), os
  testes da frente pelo branch (o prefixo mais longo do nome que acha um `tests/test_<prefixo>*.py`) e o estouro do limite com código 2,
  uma vez por sessão. **Ligado** pelo Matheus em 2026-11-06, depois da medida abaixo ("Sim, ligar o H2").
- **O H1b** confere também as `FAIXAS_QUEIMADAS` do disco contra as do `origin/main` (o `sed` que o H9 não vê); sem `origin/main`, código 2
  com "rode git fetch".
- **O H6** (`h6_capturas.py`): código 2 ao escrever em `*-snapshots/` e na pasta de `DIGILAB_CAPTURAS`, pela ferramenta ou pelo shell
  (`rm`, `mv`, `cp`, os cmdlets, o redirecionamento, o `git checkout`/`restore`/`rm`, o `sed -i`); `ask` no `--update-snapshots` e no `-u`
  do Playwright (o `git push -u` passa).
- **O H9** (`h9_faixas.py`): código 2 ao remover ou mudar uma faixa queimada, ou quando o texto depois não se lê; `ask` ao queimar uma
  nova no fim; as reservadas passam.
- **Ligados** em `.claude/settings.json`: H1, H1b, H2, H3, H4, H6 e H9, igual à proposta (`docs/propostas/hooks_settings.json`); o teste
  confere que os dois arquivos são iguais.
- **Testes:** `python -m pytest tests/test_hooks.py tests/test_hook_h4.py -q -p no:cacheprovider` → 77 passed (antes, 43 failed e 3
  passed sem os hooks).
- **A medida do Stop** (o H2 estendido nesta worktree, com um arquivo temporário não rastreado e o limite levantado para medir; outra
  sessão rodava testes ao mesmo tempo, a `ponte_luta_pe1`): mudança em `digilab/`, 341,8 s, 327,0 s e 323,8 s; só em `tests/`, 3,5 s,
  9,8 s e 3,9 s (a frente `infra_agentes_e1` cai no prefixo `infra`, os `tests/test_infra_*.py`). O limite de 600 s não estoura.
- **Conferido à mão:** um evento de Edit que apaga a linha da faixa 15101…15505 do `experiments/bancada/faixas.py` real sai com código 2.

## 10. Resumo da etapa E2 (2026-11-06)

Worker: Claude Code, Opus 5.5, worktree `v3-infra-agentes-e2`, branch empilhado sobre o #604 (E1).

- **Três agentes em `.claude/agents/`**, no formato de subagente do Claude Code (`name`, `description`, `tools`, `disallowedTools`, `model`;
  o `skills` no `revisor-metodo`):
  - `revisor-metodo` (Opus): `tools: Read, Grep, Glob, Skill`, com a skill `literatura-digilab` carregada no começo;
  - `revisor-determinismo` (Opus): `tools: Read, Grep, Glob`; a lente da interface web fica no `rev-replay` da UX (D-IA-5);
  - `auditor-numeros` (Sonnet): `tools: Read, Grep, Glob`, as classes VERIFICADO, DIVERGENTE e SEM FONTE.
  Os três negam `Edit`, `Write`, `MultiEdit`, `NotebookEdit`, `Bash` e `PowerShell` no `disallowedTools`.
- **Teste:** `python -m pytest tests/test_agentes.py -q -p no:cacheprovider` → 6 passed (o frontmatter lido à mão, sem PyYAML).
- **O auditor rodado uma vez** sobre o `docs/RESULTADO_V3_ACOES_NOVAS.md`, contra `artifacts_v3_acoes_novas/run/`: **0 DIVERGENTE, 9 SEM
  FONTE, cerca de 229 VERIFICADO** (a contagem dos VERIFICADO foi feita pelo agente, à mão). A sessão desta etapa não carregava o arquivo novo
  como tipo de agente (a pasta `.claude/agents/` nasceu nela), então rodou um agente geral, em Sonnet, com o corpo do `auditor-numeros.md`
  como instrução e só leitura. Conferido à mão: o `movimento.media` (0.023628) e o `vidas` (3200) do `resultado.json` batem com o texto.
- **Dos 9 SEM FONTE,** 4 são hashes ou tamanhos de arquivo que o auditor não calcula sem `Bash` (o sha256 do `meta.json`, do `run.log` e do
  `vidas.tar.gz`, e os tamanhos do `medidas.json` e do `vidas.tar.gz`): pelo menos um é falso SEM FONTE (o sha256 do `run.log` começa por
  `bde44a87`, como o texto). Os outros 5 são números que vêm de outro documento ou de outra run (o plano, a C4, a AN0) ou que o próprio
  texto marca como hipótese.

## 11. Resumo da etapa E3 (2026-11-06)

Worker: Claude Code, Opus 5.5, worktree `v3-infra-agentes-e3`, branch empilhado sobre o #610 (E2).

- **`tools/pre_run.py`** (só biblioteca padrão): `python tools/pre_run.py <orquestrador> --config <json> [--processos N]` sai com 0 ou com
  2 e todos os motivos. Recusa:
  - a config sem `plano` ou sem `unidades.bases`;
  - o plano fora do git, com mudança não commitada, ou com texto diferente do `origin/main` (D-IA-6); sem `origin/main`, pede `git fetch`;
  - a base fora de toda faixa reservada ou dentro de uma queimada (as faixas lidas pela AST);
  - outra run em andamento, pela lista de processos Python da máquina (o `Get-CimInstance` no Windows, o `ps` fora dele);
  - mais de 4 processos.
  Para os orquestradores novos, o `pre_run.exigir(...)` levanta `Recusa` com os mesmos motivos (D-IA-2).
- **O H10** (`.claude/hooks/h10_pre_run.py`), ligado: acha `python … experiments/run_v[23]_*.py` no comando, tira o `--config` e o
  `--processos` e chama o `pre_run.py`; código 2 se ele recusa ou se falta o `--config`; o `--help` passa.
- **Testes:**
  - `python -m pytest tests/test_pre_run.py -q -p no:cacheprovider` → 13 passed;
  - `python -m pytest tests/test_hooks.py tests/test_hook_h4.py tests/test_pre_run.py tests/test_agentes.py tests/test_infra_*.py -q -p no:cacheprovider`
    → 166 passed.
- **No repositório de verdade, com a lista real de processos:** a varredura da AN4 (`experiments/configs/v3_acoes_novas/varredura.json`)
  passa com `--processos 4` (código 0) e é recusada com `--processos 5` (código 2); a `acoes_novas.json` passa com 4.

## 12. Resumo da etapa E4 (2026-11-06)

Worker: Claude Code, Opus 5.5, worktree `v3-infra-agentes-e4`, branch empilhado sobre o #612 (E3) e o #593 (UX_TELA_PET A2, sobre o #592).

- **Um testador só (D-IA-5): o `ux-browser-tester` do #593,** e nenhum `testador-navegador.md`. Ele já cumpria a seção 3.4: sem escrita, a
  porta própria (`DIGILAB_PORTA_E2E`), os quatro processos e o retorno só com falhas, capturas, diff e console. **Faltava o `npm run tipos`
  e o `npm test`:** os dois entram antes do e2e, e uma falha neles já é a resposta. O `h8_escopo.py` do testador passa a deixar rodar os
  dois.
- **A junção com a UX:**
  - o #604 adota o `h6_capturas.py` do #592, byte a byte; os 20 casos do H6 desta frente passam com ele;
  - no `tests/test_hooks.py`, os dois lados acrescentaram casos; dois nomes repetidos ganharam o sufixo `_infra`;
  - o `test_proposta_ux_aponta_scripts_que_existem_e_nada_ligado` aceita o H6 ligado (D-IA-7);
  - o `test_os_seis_agentes_e_nenhum_outro` (UX) aceita os três revisores da E2.
- **Testes:** `python -m pytest tests/test_hooks.py tests/test_hook_h4.py tests/test_agentes.py tests/test_agentes_ux.py tests/test_pre_run.py tests/test_infra_*.py -q -p no:cacheprovider`
  → 258 passed. Antes dos ajustes da junção, os dois testes da UX acima falhavam.
- **O testador rodado uma vez** (num agente geral, em Sonnet, com o corpo do `ux-browser-tester.md`; a sessão não carrega a pasta de
  agentes): só o `npm run tipos` e o `npm test`, com um `test/_quebrado_e4.test.ts` temporário que espera `1 + 1` ser 3.
  - O tsc passou.
  - O Vitest: 1 falha, com o arquivo, a linha 5, o nome e "expected 2 to be 3"; 92 arquivos e 907 testes passaram.
  - Sem o arquivo, `npm test` → 92 arquivos e 907 testes passados, em 77 s.
  - O e2e não rodou nesta prova (8 a 12 min na medida do H5 da UX).

## 13. Resumo da etapa E5 (2026-11-06)

Worker: Claude Code, Opus 5.5, worktree `v3-infra-agentes-e5`, branch empilhado sobre o #615 (E4).

- **O job `web`** em `.github/workflows/verificar-pr.yml`, num runner Linux, no `pull_request`:
  - um passo olha `git diff --quiet origin/$BASE_REF...HEAD -- web/app/` e sai cedo, com uma linha no resumo do job, se o PR não muda `web/app/`;
  - senão roda em `web/app` o `npm ci`, o `npm run tipos`, o `npm test` (Vitest) e o `npm run build`, no Node 24 (o `engines` do
    `package.json`), com o cache do npm;
  - o e2e fica fora (D-IA-3).
  O filtro é um passo, e não o `paths:` do `on:`, para não tirar o job `relato` dos PRs de documento. Sem secrets, `permissions: contents: read`.
- **O `tools/verificar_relato.py`:** o alerta dos testes do `web/app` diz agora que o job `web` roda os tipos, o Vitest e o build, e que só o
  Playwright segue declarado. O `docs/infra/GUIA_OPERACIONAL.md` ganhou o job `web` na seção "O que o CI confere".
- **Testes:** `python -m pytest tests/test_infra_*.py -q -p no:cacheprovider` → 60 passed; o YAML do workflow lido sem erro.
- **A prova é o próprio PR:** este branch traz o `web/app/registry.json` do #593, então o diff contra a `main` muda `web/app/` e o job roda os
  passos todos. O resultado fica no relato do PR, pelo check do GitHub.

## 14. Resumo da etapa E6 (2026-11-06): o Bash do auditor

Worker: Claude Code, Opus 5.5, worktree `v3-infra-agentes-e5`, branch `v3-infra-agentes-e6`, de `origin/main`. A recomendação da E2
(seção 10, D-IA-E2-1), seguida pelo Matheus em 2026-11-06 ("siga com as recomendações").

- **O papel `auditor` no `.claude/hooks/h8_escopo.py`:** nenhuma escrita. No shell, só os comandos de leitura da lista do H6 (que tem o
  `sha256sum`, o `Get-FileHash`, o `stat` e o `du`), sem `find` e sem redirecionamento.
- **O `auditor-numeros`:** `tools: Read, Grep, Glob, Bash`, com o H8 do papel `auditor` no frontmatter, para `Edit|Write|MultiEdit|NotebookEdit|Bash|PowerShell`;
  o `PowerShell` segue negado. O corpo diz como tirar o sha256 e o tamanho de um arquivo.
- **Testes:** `python -m pytest tests/test_hooks.py tests/test_hook_h4.py tests/test_agentes.py tests/test_agentes_ux.py tests/test_pre_run.py tests/test_infra_*.py -q -p no:cacheprovider`
  → todos passam (a contagem no corpo do PR). Os casos novos: dez comandos do auditor (cinco de leitura passam; `python -c`, `rm`, o `>`,
  o `find -delete` e o `npm test` não) e a edição negada.
- **Não rodado:** uma segunda rodada do auditor sobre o `RESULTADO_V3_ACOES_NOVAS.md`, para ver os quatro SEM FONTE de hash e tamanho
  virarem VERIFICADO. Ela vale numa sessão aberta depois do merge, que carrega o agente pelo tipo.

## 15. Resumo da etapa E7 (2026-11-06): as medições do combate no gate

Worker: Claude Code, Opus 5.5, worktree `v3-infra-agentes-e5`, branch `v3-infra-agentes-e7`, empilhado sobre o #622 (E6). A questão
aberta da E3 (seção 11), seguida pelo Matheus em 2026-11-06 ("siga com as recomendações").

- **As medições do combate** são os scripts de `web/app/scripts/equilibrio_tr/`: os orquestradores em Python (`medir_tudo.py`, os
  `grade_*_r2.py`, rodados em `web/app`) e as bancadas em TypeScript (`fase1_relogio.ts` a `fase4_progressao.ts`, pelo `npx tsx`). Elas
  usam faixas por nome (`--faixa calibracao2`), não config com plano e bases; o `tools/medir_*` que a E3 citava não existe.
- **O `tools/pre_run.py`:**
  - `--medicao` confere só a regra de uma carga por vez;
  - a lista de processos inclui o Node;
  - uma medição em andamento conta como run para as outras, e uma run de pesquisa conta para a medição.
- **O H10:** acha `python … scripts/equilibrio_tr/*.py` e `npx tsx`/`node … scripts/equilibrio_tr/*.ts` no comando e chama o
  `pre_run.py --medicao`; ler os scripts (`cat`, `git diff`) e o `--help` passam.
- **Testes:** `python -m pytest tests/test_hooks.py tests/test_hook_h4.py tests/test_agentes.py tests/test_agentes_ux.py tests/test_pre_run.py tests/test_infra_*.py -q -p no:cacheprovider`
  → 278 passed. Na máquina real: `python tools/pre_run.py web/app/scripts/equilibrio_tr/medir_tudo.py --medicao` → código 0.

## 16. A prova ao vivo e a etapa E6b (2026-11-06)

- **A prova ao vivo,** numa sessão nova aberta em `D:\Trab\digilab\v3-infra-agentes-e5` (a `main` em `d9900a0`), em Sonnet:
  - editar o `digilab/engine.py`: bloqueado pelo H1;
  - trocar a `FAIXAS_QUEIMADAS` por uma tupla vazia: bloqueado pelo H9;
  - a varredura da AN4 com `--processos 5`: bloqueada pelo H10;
  - o `auditor-numeros`, chamado pelo tipo, nas linhas 40 a 45 do `docs/RESULTADO_V3_ACOES_NOVAS.md`: 14 VERIFICADO, 0 DIVERGENTE e 1 SEM
    FONTE. Os hashes e os tamanhos que na primeira rodada (seção 10) saíam SEM FONTE agora saem VERIFICADO.
  - O `git status --short` ficou vazio depois.
- **O SEM FONTE que sobrou** foram as "3 200 vidas" dentro do `vidas.tar.gz`: o H8 negou ao auditor o `tar -tzf`.
- **A E6b, a pedido do Matheus ("Sim, liberar"):** o papel `auditor` do H8 aceita o `tar` só no modo de listar (`-t`, `--list` ou o `t` no
  grupo de letras do começo). Nega o `-x`, o `-c`, o `-r`, o `-u`, o `-A`, o `-I`, o `--delete`, o `--to-command` e as outras opções que
  extraem, criam ou rodam programa, e o `tar` sem `-t`. O `auditor-numeros.md` diz como usar.
- **Testes:** oito casos novos do `tar` no `test_h8_shell_do_auditor`; o conjunto de hooks, agentes, `pre_run` e infra passa inteiro.
