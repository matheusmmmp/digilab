# TAREFA V3 — UX_TELA_PET (2026-11-05)

Coordenador: Gerente da frente UX_TELA_PET (Claude Code, Opus 5.5). Worker: o mesmo, na etapa de papel. Worktree e branch:
`v3-ux-tela-pet`. Status: etapa 0 (papel) ENTREGUE. **UX-1 e UX-2 DECIDIDAS** pelo Matheus em 2026-11-05 (proposta B; os hooks
antes, seção 8.1); o resto continua **PROPOSTO** até ele decidir (seção 8).

Categoria: arquitetura. Origem: Matheus, 2026-11-05: arquitetura de agentes para a interface do jogo (designer, implementador, testador
no navegador, revisores por lente, hooks como gate) e propostas de layout e UX de jogo para a tela Pet.

## 1. Pergunta

Sem hipótese de pesquisa: é trilha L (layout) da V3. Duas perguntas:

1. **Que arquitetura de agentes deixa a tela Pet mudar de desenho sem que o replay, o e2e pixel a pixel e a autoridade do Matheus sobre o
   visual dependam da boa vontade do modelo?** (a regra sem exceção vira hook; o resto fica no papel de cada agente)
2. **Qual dos três desenhos da tela Pet (`docs/PROPOSTAS_V3_UX_TELA_PET.md`) dá ao jogador a melhor leitura do estado do pet**, sem
   tocar o motor, o save ou as rotas?

## 2. Depende de

- **Os hooks H1 a H4 de volta.** O commit `2586b0e` (a H2 da ilha, 2026-10-30) apagou `.claude/settings.json` e `.claude/hooks/`
  (`_comum.py`, `h1_engine.py`, `h1b_engine_sha.py`, `h2_testes.py`, `h3_main.py`, `h4_autorizo.py`); o `tests/test_hooks.py` ficou e
  falha (o `PAINEL_V3.md`, seção 2, conta 43 falhas na suíte; há um card proposto para restaurar). Os hooks novos desta tarefa usam o
  mesmo `_comum.py` e o mesmo arquivo de teste: **a restauração vem antes** da etapa A1 (seção 3.4).
- **As ferramentas instaladas pelo Matheus** (configuração persistente é dele, SA-5 da `docs/TAREFA_V2_SAUDE.md`): o plugin
  `frontend-design` (`/plugin install frontend-design@claude-plugins-official`), o shadcn MCP (`npx shadcn@latest mcp init --client claude`)
  e o Playwright MCP (`npx @playwright/mcp@latest`, declarado só no frontmatter do testador). Nesta sessão nenhum dos três foi conferido
  como instalado.
- **As decisões UX-1 a UX-8** (seção 8).

## 3. Mudança mínima

Esta etapa é só papel: este documento e `docs/PROPOSTAS_V3_UX_TELA_PET.md`. **Nada em `web/app/`, `.claude/`, `digilab/` ou
`experiments/` muda neste PR.** As seções abaixo descrevem o que as etapas seguintes criam.

### 3.1 O fluxo

```
Matheus ─ pedido ─▶ Gerente da frente (sessão principal, Opus; a única que fala com o Matheus e abre o PR)
                         │
       ┌─────────────────┼──────────────────────────────┬──────────────────────────┐
       ▼                 ▼                              ▼                          ▼
  ux-designer      ux-implementador               ux-browser-tester          rev-replay · rev-a11y · rev-cena
  (plano em        (código só com os              (sobe o servidor, roda     (só leitura, uma lente cada,
   texto, depois    componentes do projeto)        e2e e capturas; devolve    sem ver a conversa)
   a prancha)                                      só falhas e diffs)
       │                 │                              │                          │
       └── Matheus aprova o plano e a prancha ──▶ código ──▶ hooks no Stop ──▶ testador ──▶ revisores ──▶ PR
                                                                                     │
                                       capturas novas ─▶ D:\Trab\digilab\capturas_ux_pet_aprovar\ ─▶ Matheus aprova ─▶ --update-snapshots
```

A ordem é a da B3 e do HUD: **plano → prancha → ok do Matheus → código**. Um escritor por vez em `web/app/src/` (o implementador); os
outros só leem ou só rodam comandos.

### 3.2 Os papéis (os arquivos `.claude/agents/*.md`, criados na etapa A2)

O limite de cada papel é imposto pelo harness (o campo `tools` do frontmatter e os hooks do agente), não pedido no prompt. O frontmatter
segue a documentação dos subagentes (`name`, `description`, `tools`, `disallowedTools`, `model`, `mcpServers`, `hooks`, `maxTurns`).

#### `ux-designer` — o plano de design em texto, antes de qualquer código

- **Modelo:** Opus (desenho é incerteza; CLAUDE.md, "Escolha de modelo").
- **Ferramentas:** `Read, Grep, Glob, Write, Skill` (a skill `frontend-design`). Sem `Edit` em código, sem `Bash`.
- **Hook do agente:** `PreToolUse` em `Write` com o `h8_escopo.py designer`: só escreve em `docs/pranchas/ux-pet/` e em
  `docs/PROPOSTAS_V3_UX_TELA_PET.md`; fora disso, código 2.
- **Entrega:** para cada proposta, o plano em texto no formato da seção 0 do `docs/PROPOSTAS_V3_UX_TELA_PET.md` (o objetivo do jogador,
  a hierarquia, o que fica sempre visível, o que aparece por gesto, as cores pelos tokens, o wireframe ASCII a 1920×950 e a 390, o custo
  em determinismo e em e2e). Depois do ok do plano, a prancha HTML em `docs/pranchas/ux-pet/` no padrão de `docs/pranchas/b3/`
  (`gerar.py`, `capturar.sh`, `*.css`, capturas nas duas peles).
- **Como o plugin entra:** o `frontend-design` pede um plano com 4 a 6 cores hex, tipografia, wireframe ASCII e uma revisão contra o
  pedido antes de codar. **Aqui o `UI_GUIDELINES.md` vence o plugin** (o guia diz que vale sobre a prancha, seção 0): nenhuma cor hex
  nova, só os tokens `--dl-*`, `--hx-*` e a paleta `--hud-*` do HUD-5; nenhuma fonte fora da seção 4.2; a semântica fixa da seção 3. A lista
  de anti-padrões do plugin vira checklist do revisor, somada à seção 14 do guia.
- **Proibido:** dado que o motor não tem (princípio 1 do guia; a prancha do HUD tinha "3 dias" de idade, que saiu); número de jogo novo.

#### `ux-implementador` — o código, só com os componentes do projeto

- **Modelo:** Sonnet (escopo claro depois da prancha aprovada).
- **Ferramentas:** `Read, Grep, Glob, Edit, Write, Bash` e o shadcn MCP.
- **O registro de componentes:** o `web/app/components.json` (shadcn, estilo new-york, ícones lucide) só tem `ui/button.tsx`; o kit de
  verdade da tela Pet é o `src/componentes/hx/` (`PainelHx`, `MedidorHx`…) e as classes `hx-*`, `hud-*` e `dl-*`. Para o shadcn MCP
  enxergar esse kit, a etapa A2 cria um registro local (`web/app/registry.json`, com os `hx/*` e o `ui/button`) e o `components.json`
  fica sem registro público. **Componente novo de registro público só com o ok do Matheus** (UX-4).
- **Hook do agente:** `PreToolUse` em `Edit|Write|MultiEdit` com o `h8_escopo.py implementador`: nega `web/app/motor/`,
  `web/app/test/gabaritos/`, `web/app/src/save.ts`, as rotas e o hash (`web/app/src/rotas.ts`), `digilab/`, `experiments/`, `servidor/` e qualquer pasta de capturas (seção 3.3, H6).
- **Entrega:** o diff e a lista dos arquivos tocados; roda `npm run tipos` e `npm test` antes de devolver (o hook H5 confere de novo).

#### `ux-browser-tester` — o navegador isolado, sem escrita

- **Modelo:** Haiku ou Sonnet: rodar é mecânico; a triagem do diff (abaixo) é a parte que pensa. Se a triagem errar duas vezes no mesmo
  PR, escala para Sonnet (CLAUDE.md, "Escalar o modelo").
- **Ferramentas:** `Read, Grep, Glob, Bash`. **`disallowedTools: Edit, Write, MultiEdit, NotebookEdit`.**
- **`mcpServers`:** o Playwright MCP declarado no próprio frontmatter, de modo que as ferramentas de navegador só existem dentro dele; a
  sessão principal nunca as carrega.
- **Hook do agente:** `PreToolUse` em `Bash|PowerShell` com o `h8_escopo.py testador`: só a lista `npm run build`, `npm run e2e`,
  `npm run capturas`, `npx playwright test …` **sem** `--update-snapshots`/`-u`, e leitura (`ls`, `cat`, `git diff`). Qualquer outro
  comando, código 2. Isso fecha o buraco do `Bash` escrevendo arquivo.
- **O que faz:** sobe o servidor pelo `webServer` do `playwright.config.ts` (o `servidor/servidor_local.py --provedor nenhum`, porta
  `DIGILAB_PORTA_E2E`, uma por worktree para não brigar com outra frente na 8799), roda o e2e e as capturas (`DIGILAB_CAPTURAS_LARGURAS`
  com 390 e 1920, as duas peles por `DIGILAB_CAPTURAS_PELE`), com o relógio falso de sempre (`page.clock.install` + `pauseAt` + `runFor`,
  como o `e2e_capturas/telas.spec.ts`). Três workers mais o servidor: quatro processos (V3-D8).
- **O que devolve, e só isso:** os testes que falharam (nome, largura, pele), o caminho de cada `*-actual.png`, `*-expected.png` e
  `*-diff.png`, o número de pixels diferentes, os trechos de console e `pageerror`, e **a classificação de cada diff** em uma de três:
  `provável bug` (texto sobreposto, sprite esticado ou fora da escala inteira, alvo menor que 44 px, elemento cortado), `mudança
  pretendida` (bate com a prancha aprovada) ou `ruído` (o caso da GPU já documentado, que vai para o projeto `software`). **A
  classificação não aprova nada:** o diff continua reprovando o teste.

#### Os revisores, só leitura, uma lente cada

`tools: Read, Grep, Glob`. Cada um recebe o diff, a prancha aprovada e o plano de design; **não recebe a conversa** (o "revisor virgem").
Instrução comum: sem estilo; cada achado com arquivo:linha, o cenário que falha e a evidência (comando e saída, ou captura); achado sem
isso o Gerente descarta (o filtro do `/code-review`). Rodam em paralelo depois do testador.

| agente | modelo | a lente | o que confere, no mínimo |
|---|---|---|---|
| `rev-replay` | Opus | o determinismo do replay | nada em `src/` altera o motor fora de `mudarMotor()`; nenhum `Math.random`, `Date.now` ou `performance.now` chega ao estado do pet (hoje eles existem só na apresentação: `PalcoPet.tsx`, `MundoReserva.tsx`, e o `Math.random` de `jogo.ts`, `lab.ts`, `heranca.ts`, `jornada.ts`, `som.ts`, que este revisor lê e diz se é vista ou estado); preferência de tela em chave própria do `localStorage` (como `-hud`, `-hud-arraste`, `-detalhes-pet`), nunca no save; `git diff origin/main -- web/app/test/gabaritos/ web/app/motor/` vazio; o `motor_sem_dom` passa |
| `rev-a11y` | Sonnet | a acessibilidade | a seção 13 e a 7 do guia: alvo ≥ 44×44, foco visível com o anel, ordem de tabulação igual à visual, `aria-label` em botão só com ícone, `aria-expanded`/`aria-controls` nos que abrem, nada importante só no hover nem só num gesto sem equivalente de teclado, `prefers-reduced-motion` e `prefers-reduced-transparency`, contraste medido (o padrão do `hx_pele.test.ts`, sobre o pior pixel da cena), zoom a 200 % |
| `rev-cena` | Sonnet | o desempenho da cena | o three.js só entra pelo `cena3d.ts` por `import()` (`ilha_fronteira.test.ts`); o `Habitat` não remonta ao trocar de rota; o `CENA.coberto` segue o véu; o HUD não re-renderiza a cada quadro; `backdrop-filter` do Vidro sobre o canvas WebGL (custo por área); a medida da M3 com `?medir3d=1` antes e depois, no desktop e num celular |

### 3.3 Os hooks (o gate que não depende do modelo)

Ficam em `.claude/hooks/` no padrão dos H1 a H4 (Python, só biblioteca padrão, o `_comum.py` para ler o evento e bloquear) e entram como
proposta em `docs/propostas/hooks_ux_settings.json`; **só o Matheus os liga** em `.claude/settings.json` (SA-5).

| hook | evento e matcher | o que faz | código |
|---|---|---|---|
| **H5 `h5_web.py`** | `Stop` | se o diff da worktree (contra o `merge-base` com `origin/main`, mais o não commitado) toca `web/app/src/`, `web/app/e2e*/`, `web/app/test/` ou `web/app/motor/`: roda `npm run tipos`, `npm test` e `npm run e2e` em `web/app`. Em falha, devolve o turno com o resumo (os nomes dos testes que falharam, não o log inteiro) | 2 em falha. Como o H2: **não bloqueia duas vezes pelo mesmo motivo** (`stop_hook_active` ou a mesma assinatura de falha, guardada na pasta temporária, por sessão), senão um teste quebrado prende a sessão |
| **H6 `h6_capturas.py`** | `PreToolUse`, `Edit\|Write\|MultiEdit\|NotebookEdit` e `Bash\|PowerShell` | nega escrever, mover ou apagar em qualquer pasta `*-snapshots/` **e na pasta das referências do portão**, que fica fora do git (`DIGILAB_CAPTURAS`, padrão `artifacts_v2_front_react/capturas/`, o `snapshotPathTemplate` do `playwright.capturas.config.ts`). Num comando de shell com `--update-snapshots` ou `-u` do Playwright, pede a aprovação na hora (a decisão `ask`, como o H3): é o único caminho para trocar uma referência | 2 (negar) nas edições; `ask` no `--update-snapshots` |
| **H8 `h8_escopo.py <papel>`** | `PreToolUse`, no frontmatter de cada agente (não no `settings.json`) | o escopo de escrita de cada papel (seção 3.2) | 2 fora do escopo |

O H7 fica livre de propósito (o número não importa; a numeração seguiu a ordem em que os hooks foram pensados).

**O custo do H5:** o `npm run e2e` faz o build e roda todo o `e2e/` com três workers. A duração não foi medida nesta sessão (SEM MEDIDA);
a etapa A1 mede três vezes e grava no registro. Se passar de ~10 min por turno, a UX-3 decide entre o e2e inteiro e só os specs da tela
Pet (`jogo.spec.ts`, `vida_pet_cena.spec.ts`, `sprites_comer.spec.ts`) no `Stop`, com o inteiro só antes do PR. O CI do PR não roda o
`npm test` nem o e2e (`GUIA_OPERACIONAL.md`, seção 3): hoje é o Gerente que roda na junção; com o H5, o turno do agente também.

### 3.4 As etapas que vêm depois deste PR

| etapa | o quê | arquivos | categoria |
|---|---|---|---|
| A0 | restaurar H1 a H4 (o card que já existe) | `.claude/hooks/`, `docs/propostas/hooks_settings.json` | implementacao (outra tarefa) |
| A1 | H5, H6 e H8, desligados; casos novos no `tests/test_hooks.py` (o evento no stdin, o código de saída); a duração do H5 medida | `.claude/hooks/h5_web.py`, `h6_capturas.py`, `h8_escopo.py`, `docs/propostas/hooks_ux_settings.json`, `tests/test_hooks.py` | implementacao |
| A2 | os seis agentes e o registro local do shadcn | `.claude/agents/ux-designer.md`, `ux-implementador.md`, `ux-browser-tester.md`, `rev-replay.md`, `rev-a11y.md`, `rev-cena.md`; `web/app/registry.json` | implementacao |
| P1 | a proposta escolhida vira prancha (o designer) e, com o ok, código (o implementador), testada e revista pelos outros | `docs/pranchas/ux-pet/`, depois `web/app/src/telas/pet/`, `web/app/src/estilo/pet_hud.css`, `pet_dock.css`, `web/app/e2e/` | papel, depois implementacao |

A ordem entre A e P é a UX-2.

## 4. Experimento e gate (se houver run)

Não há run de pesquisa. Os gates são de regressão e visuais:

- **G-PIXEL:** o e2e pixel a pixel continua o gate (`toHaveScreenshot` com `threshold: 0` e `maxDiffPixels: 0`, o relógio pausado, uma
  nova tentativa só para o ruído de GPU já conhecido). Nenhum agente afrouxa esses números.
- **G-VISAO:** o modelo de visão só **classifica** o diff (provável bug, mudança pretendida, ruído) e escreve o resumo; nunca aprova,
  nunca troca uma referência e nunca transforma uma reprovação em aprovação.
- **G-REFERENCIA:** uma referência só muda com a aprovação do Matheus: as capturas novas vão para `D:\Trab\digilab\capturas_ux_pet_aprovar\`
  (fora do git, como o `capturas_hud_aprovar`), o Matheus aprova no chat, e só então o `--update-snapshots` roda, pelo pedido `ask` do H6.
- **G-REPLAY:** `git diff origin/main -- web/app/motor/ web/app/test/gabaritos/` vazio; a paridade e o `motor_sem_dom` passam sem regravar
  nada.
- **G-HOOKS-UX:** cada hook novo tem caso no `tests/test_hooks.py` (o padrão do G-HOOKS da rodada de saúde).

## 5. Entrega

**Esta etapa (papel):** este documento e o `docs/PROPOSTAS_V3_UX_TELA_PET.md`. Um PR de categoria arquitetura contra a `main`, com o corpo
no modelo `.github/pull_request_template.md`, conferido por `python tools/verificar_relato.py`. O merge é só do Matheus.

**Nas etapas seguintes:** `npm run tipos`, `npm test` e `npm run e2e` em `web/app` (no máximo 4 processos); `python -m pytest
tests/test_hooks.py -q` na A1; o desvio, se houver, numa seção no fim de `docs/registro/2026-11.md` com a linha no índice
`docs/REGISTRO_DESVIOS.md`; o resumo da etapa no fim deste documento e no corpo do PR.

## 6. Fora desta tarefa

- O motor (`web/app/motor/`, `digilab/`), o save, as rotas e o hash, os eventos do log, os gabaritos, as versões de pet.
- Qualquer número de jogo, inclusive os limiares do HUD transitório (`AVISO_MS`, `FOME_FALA`, `FOME_EMOTE`, PROPOSTOS na `TAREFA_V3_LAYOUT_HUD.md`).
- A restauração dos H1 a H4 (A0, o card que já existe).
- As outras telas (Crescer, Lutar, Diário, Conversar, Ajustes) e a luta (B3, já na `main`).
- O histórico de motivos: o motor só guarda o motivo da decisão de agora (`Motor.motivo`, `MotivoVida`); o `historico` não tem causa. Uma
  fita de "por quês" passados precisaria de mudança no motor e fica fora.
- Os Playwright Test Agents: o planner e o generator podem ajudar a escrever e2e de interação numa etapa futura; **o healer fica proibido
  nos testes de captura** (consertar seletor ou espera num teste pixel a pixel esconde regressão).

## 7. Critérios de aceitação

Desta etapa:

- `docs/TAREFA_V3_UX_TELA_PET.md` e `docs/PROPOSTAS_V3_UX_TELA_PET.md` existem; `git diff --stat origin/main` só toca `docs/`.
- As três propostas têm, cada uma: o objetivo do jogador, a hierarquia, o sempre visível, o que vem por gesto, as cores por token, os
  wireframes a 1920×950 e a 390, o que muda na leitura do estado e o custo em determinismo e em e2e; uma trata a ilha como figura
  principal, outra mostra o porquê sem abrir painel.
- As decisões UX-1 a UX-8 estão na seção 8, cada uma com a recomendação e o custo de errar.
- O `tools/verificar_relato.py` aceita o corpo do PR.

Das etapas seguintes (para depois): os critérios de cada linha da seção 3.4 e os gates da seção 4.

## 8. Precisa do Matheus

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| **UX-1** | qual proposta vira prancha: **A** (a ilha na frente, o HUD recua), **B** (o porquê no balão, sem painel) ou **C** (as necessidades dentro dos botões) | **B, e depois o pedaço "faixa de vitais" da A.** A B é a que mais serve ao diferencial do jogo (princípio 2 do guia: o aprendizado visível), usa só dado que o motor já registra, muda pouco da tela de hoje (o balão e um chip) e fecha a pendência do e2e do porquê | B errada custa pouco: o balão volta ao de hoje. A errada desfaz a HUD-2 (a pilha aberta) e troca quase todas as capturas da tela Pet. C errada mexe no dock, que todo e2e de ação usa |
| **UX-2** | a arquitetura de agentes entra **antes** ou **depois** da proposta escolhida | **antes, mas só A0 e A1 (os hooks)**; os agentes (A2) entram junto com a P1, que é o primeiro uso deles. Os hooks protegem a P1 desde o primeiro commit; agente sem tarefa real é configuração que ninguém testou | antes demais: dias de configuração sem tela nova. Depois: a P1 roda sem o H5 e o H6, e uma referência pode mudar sem a aprovação (o que o G-REFERENCIA quer impedir) |
| **UX-3** | o H5 roda o e2e **inteiro** ou **só os specs da tela Pet** no `Stop` | **decidir depois da medida da A1**; se o inteiro passar de ~10 min, os da tela Pet no `Stop` e o inteiro antes do PR | inteiro e lento: cada fim de turno fica parado minutos, e a tentação é desligar o hook. Só os da Pet: uma regressão noutra tela passa até o PR |
| **UX-4** | o implementador pode instalar componente de registro público do shadcn | **não**; só o registro local (`web/app/registry.json` com os `hx/*`); um componente público novo vem como pergunta | sim: componentes "parecidos mas diferentes" do kit `hx-*`, e duas peles para manter. Não: algum componente pronto (um popover acessível) é escrito à mão |
| **UX-5** | ligar os hooks H5, H6 e H8 (configuração persistente, sua) | **ligar H6 e H8 assim que a A1 passar; o H5 depois da UX-3** | H6 desligado: a referência pode ser regravada por um agente. H5 ligado cedo demais: turnos lentos |
| **UX-6** | instalar o plugin `frontend-design`, o shadcn MCP e o Playwright MCP | **sim, os três**, o Playwright MCP só no frontmatter do testador | sem eles, os papéis caem para prompt puro, e o limite deixa de ser do harness |
| **UX-7** | o testador classifica o diff com o próprio modelo ou um agente separado para isso | **o próprio testador**, com a regra de que a classificação não aprova | separado: mais um agente e mais tokens; o próprio: o mesmo modelo que roda pode querer "explicar" a falha. A regra do G-VISAO segura os dois casos |
| **UX-8** | onde ficam as capturas para aprovar | **`D:\Trab\digilab\capturas_ux_pet_aprovar\`, fora do git**, como o HUD e a M7 | dentro do git: o repositório cresce com PNGs e o `.gitignore` do atlas fica ambíguo |

### 8.1 Decididas

Matheus, 2026-11-05, nesta sessão (resposta "B, hooks antes"):

- **UX-1: a proposta B** ("O porquê no balão") vira a prancha da P1. A faixa de vitais da A fica como passo seguinte possível, sem
  decisão; a C fica de fora por ora.
- **UX-2: os hooks antes.** A ordem é A0 (restaurar os H1–H4 apagados no `2586b0e`) → A1 (H5, H6 e H8, desligados, com testes) → P1
  (a prancha da B em `docs/pranchas/ux-pet/`, para o ok do Matheus antes de qualquer código), com os agentes (A2) entrando junto da P1.

- **UX-3: o e2e inteiro no `Stop`** (Matheus, 2026-11-06, "O e2e inteiro", depois da medida da A1: 10,8 a 13,7 min por turno).
  O H5 fica com os passos padrão (tipos, Vitest e `npm run e2e`); a `DIGILAB_H5_PASSOS` não é usada para reduzir o e2e.

- **A prancha da P1 e as P1-1 a P1-6** (Matheus, 2026-11-06, ao ler as sete perguntas do PR #596: "Siga com a sua recomendação."). As
  perguntas estão em `docs/PROPOSTAS_V3_UX_TELA_PET.md`, seção "P1":
  - **o ok à prancha** da B refinada (`docs/pranchas/ux-pet/`): a linha do agora lê `Motor.digibrain().decisao`, e o balão leva o chip
    só quando há `MotivoVida`;
  - **P1-1: sim**, o chip do treino com pausa (`fadiga_treino`) usa a caixa sólida de necessidade, "vem do corpo";
  - **P1-2:** com o modular decidindo, a linha diz **"cérebro modular", sem marca**; o porquê do modular fica para uma etapa própria;
  - **P1-3:** a linha **abre o DigiBrain**;
  - **P1-4: não**, a linha não mostra `percepcao[0]` nesta etapa;
  - **P1-5:** com "Exibir detalhes do pet" desligado, **a linha fica, como texto sem botão**;
  - **P1-6:** o rótulo é **"aprendido"**.

- **O mobile Digivice** (Matheus, 2026-11-06): reestruturar todo o mobile do jogo web (abaixo de 900 px), que hoje é o desktop
  espremido e "não parece um jogo", **sem alterar nada do desktop**. Entre as duas direções da prancha de direção
  (https://claude.ai/artifact/4kQh77wKGzbaijGb5H2qmB), ele escolheu a **Digivice** (as classes `.d2`): a paleta `--dl-*` e as fontes do
  guia 4.2, a placa no alto, os vitais em cartões, a linha do agora como balão preso ao pet, botões gordos que afundam ao toque e a barra
  de abas com círculos. São três etapas, um PR cada: **M1** (a tela Pet e as abas), **M2** (as folhas Crescer, Lutar e Diário) e **M3**
  (a luta e o treino).
- **A Digivice reprovada; o mobile mínimo no lugar** (Matheus, 2026-11-06, ao ver a prancha da M1 do commit `08b3dff8`): "ela tá com um
  estilo completamente anterior, de versões muito antigas [...] tem muito botão, muita informação [...] Deixa tudo com ícones
  minimalistas", e "o menu ali embaixo [...] pode estar em alguma outra área da interface, e daí embaixo só fica os botões de ações".
  Ele aprovou para virar prancha a direção **mínima** (https://claude.ai/artifact/HxEPJtmUXByNtDkMBaH5WE):
  - as peles atuais, Vidro e Militar (`--hx-*`, `--hud-*`), no lugar da paleta `--dl-*` e das fontes do guia 4.2;
  - a cena 3D visível atrás de tudo;
  - sempre na tela, só o retrato e a hora, a coluna de ícones (Conversar, Crescer, Lutar, Diário), o ícone do agora sobre o pet e quatro
    ações só com ícone;
  - sem a barra de abas e sem a aba Pet: a tela Pet é a casa, e cada folha volta pelo seu ×;
  - o resto aparece só quando há motivo (a necessidade, o retrato aberto, o ⋯ aberto).

  O plano da M1 está em `docs/PROPOSTAS_V3_UX_TELA_PET.md`, seção "Mobile mínimo (M1)".
- **A prancha mínima e as M1-1 a M1-15** (Matheus, 2026-11-06, ao ver a prancha do commit `1d04d92e`: "Aprovar e codar"). Valem as
  recomendações da seção "Mobile mínimo (M1)", sem comentário dele em nenhuma:
  - **M1-1:** no celular, o retrato chama-se "Painéis do pet" e abre o leque; "Meus pets" vira item do leque. É o único nome acessível que
    muda, e só abaixo de 900 px;
  - **M1-2:** o Carinho vai para o ⋯. **M1-3:** o Pôr ração fica no ⋯;
  - **M1-4:** ícones de traço do lucide nas ações. **M1-5:** um ícone por ação no agora, em posição fixa, fora do pet;
  - **M1-6:** o aviso usa a regra da sugerida de hoje (`resumoAgora`). **M1-7:** o aviso dura 15 s; o ponto e a ação ficam enquanto a
    necessidade vale. **M1-8:** dormindo, sem aviso de energia;
  - **M1-9:** o toque longo mostra o rótulo depois de **500 ms, PROPOSTO, SEM FONTE** (o Matheus não comentou o número);
  - **M1-10:** a volta das folhas é o × "Fechar e voltar ao Pet" (as folhas são da M2). **M1-11:** "Exibir detalhes do pet" desligado,
    como hoje. **M1-12:** o salvo mostra só o erro "não salva", como ícone;
  - **M1-13:** rosa só para a necessidade, a vontade aprendida em ciano, e uma marca no ⋯ quando a sugerida mora nele. **M1-14:** o vital
    baixo rosa no leque. **M1-15:** o balão da fala continua.

- **A direção "Lugares da ilha" e a prancha da L1, com as L1-1 a L1-7** (Matheus, 2026-11-06: escolheu a direção B, "Lugares da ilha";
  depois "Aprovado, seguir" e "Aprovar a L1" à prancha do commit `77fb11e2`). As perguntas estão em `docs/PROPOSTAS_V3_UX_TELA_PET.md`,
  seção "Lugares da ilha (L1)":
  - **L1-1:** o minimapa mostra **a ilha inteira** (a escala A), e **a roda sobre ele aproxima até a janela** em volta da câmera (a B);
  - **L1-2:** o pet é o **ponto rosa** (`--hx-necessidade`) com o anel claro;
  - **L1-3:** com a câmera "Fixa", **o minimapa aparece, sem mover a câmera**;
  - **L1-4:** o cocô e o kit médico **ficam fora** do minimapa;
  - **L1-5:** **sim** aos atalhos Q/E (girar), +/− (aproximar) e às setas e ao Enter no minimapa com foco;
  - **L1-6:** o DigiBrain vira **a 4ª linha da pilha** da direita;
  - **L1-7:** os números (o círculo de 232 px, 12 células/s no WASD, o "seguir o pet" a partir de 6 células, a transição de 400 ms)
    **ficam PROPOSTO, SEM FONTE**. O Matheus não comentou nenhum deles.

- **O DigiBrain "scan holográfico", a prancha D1 e as D1-1 a D1-11** (Matheus, 2026-11-07: escolheu a direção A, "scan holográfico", no
  protótipo https://claude.ai/artifact/5Yay8iVFaPv4kTE3r4Lhut; depois "Aprovar e codar" à prancha do commit `26285e7a`). As perguntas e as
  recomendações aceitas estão em `docs/PROPOSTAS_V3_UX_TELA_PET.md`, seção "DigiBrain scan (D1)", e a prancha em `docs/pranchas/ux-digibrain/`:
  - SVG; a varredura em 1,2 s, o pulso em 0,8 s e o giro de ±8° em 40 s, **PROPOSTO, SEM FONTE**; sem giro no celular; o plano inteiro
    balança, sem profundidade por nó;
  - as barras dos lobos com o eixo no zero; no replay, só o destaque troca; o mapa em texto com os inteiros `w` e `w0`;
  - o e2e "sem animação" com o reduzir movimento, mais um teste de que as animações terminam;
  - o `DigiBrainLab` fica no painel de hoje; o tempo do jogo segue andando, com o cartão do chamado por cima;
  - os números de layout ficam **PROPOSTO, SEM FONTE**.

UX-4 a UX-8 continuam PROPOSTAS.

## 9. Etapa A0: os hooks restaurados (2026-11-05)

Branch `v3-hooks-a0`, empilhada sobre a `v3-ux-tela-pet`. `.claude/hooks/` (seis arquivos) e `.claude/settings.json` voltam iguais aos de
`2586b0e^`, por `git checkout`, sem edição à mão. Com o merge, voltam a valer o H1, o H1b e o H3, que o Matheus ligou em 2026-10-14; o H2 e o
H4 seguem desligados. O Matheus decidiu religar os três (2026-11-05, "Sim, religar"). `python -m pytest tests/test_hooks.py tests/test_hook_h4.py tests/test_conferir_saude.py -q`: 68 passed (antes, 43
failed e 25 passed). Próxima: a A1.

## 10. Etapa A1: H5, H6 e H8, desligados (2026-11-06)

Branch `v3-hooks-a1`, empilhada sobre a `v3-hooks-a0`. Os três hooks da seção 3.3 existem em `.claude/hooks/` e a configuração proposta em
`docs/propostas/hooks_ux_settings.json`; **nada foi ligado** (o `.claude/settings.json` é o da A0, e um teste confere). O H8 não entra no
`settings.json`: a proposta traz, em `agentes_h8`, o matcher e o comando de cada papel para o frontmatter dos agentes da A2.

- **H5 `h5_web.py`** (`Stop`): roda tipos, Vitest e e2e em `web/app` quando o diff contra o `merge-base` com `origin/main`, mais o não
  commitado e os arquivos novos, toca `web/app/src/`, `web/app/e2e*`, `web/app/test/` ou `web/app/motor/`. Para no primeiro passo que
  falha e não bloqueia duas vezes pelo mesmo motivo. `DIGILAB_H5_PASSOS` troca os passos (a UX-3 e os testes); um passo além de
  `DIGILAB_H5_LIMITE_S` (padrão 1 800 s) não bloqueia.
- **H6 `h6_capturas.py`**: nega editar `*-snapshots/` e a pasta `DIGILAB_CAPTURAS`; no shell, `ask` no Playwright com
  `--update-snapshots`/`-u` e negação para comando que cita essas pastas e não é só leitura (ou que redireciona para lá).
- **H8 `h8_escopo.py <papel>`**: designer, implementador e testador como na seção 3.2; papel desconhecido bloqueia.

Testes: `python -m pytest tests/test_hooks.py -q` → 101 passed (32 de antes, 69 novos).

**A medida do H5** (`docs/propostas/medida_h5_2026-11-06.txt`, três rodadas sem nenhuma mudança em `web/app`): tipos 4–9 s, Vitest 110–169 s
(822 testes, todos passam), e2e 481–709 s. O total por turno fica entre **10,8 e 13,7 min**, acima dos ~10 min da UX-3. O e2e **oscilou no
mesmo código**: 3 falhas na rodada 1, 1 na rodada 2 (o treino com "Forçar levantar pedra?", nas duas), nenhuma na 3. Com o H5 ligado, uma
oscilação dessas devolveria o turno ao agente uma vez por assinatura. Isso pesa na UX-5. A UX-3 ficou decidida pelo e2e inteiro (seção 8.1), com o custo medido.

## 11. Etapa A2: os seis agentes e o registro local (2026-11-06)

Branch `v3-ux-a2`, empilhada sobre a `v3-hooks-a1`. Os seis agentes da seção 3.2 em `.claude/agents/`, no formato da documentação de
subagentes do Claude Code (frontmatter com `name`, `description`, `tools`, `disallowedTools`, `model`, `skills`, `mcpServers`, `hooks`):

| agente | modelo | ferramentas | limite do harness |
|---|---|---|---|
| `ux-designer` | opus | Read, Grep, Glob, Write, Edit, Skill; a skill `frontend-design` | H8 `designer`; sem shell |
| `ux-implementador` | sonnet | Read, Grep, Glob, Edit, Write, Bash; o shadcn MCP (`npx shadcn@latest mcp`) só nele | H8 `implementador` e H6 |
| `ux-browser-tester` | sonnet | Read, Grep, Glob, Bash; o Playwright MCP (`npx -y @playwright/mcp@latest`) só nele | sem escrita; H8 `testador` e H6 |
| `rev-replay` | opus | Read, Grep, Glob | sem escrita e sem shell |
| `rev-a11y` | sonnet | Read, Grep, Glob | sem escrita e sem shell |
| `rev-cena` | sonnet | Read, Grep, Glob | sem escrita e sem shell |

O `web/app/registry.json` é o índice local no formato de registro do shadcn: os seis `hx/*`, o `ui/button` e as peles (`tokens.css`,
`pele-xcom.css`, `pele-vidro.css`). O `components.json` não ganhou `registries` (UX-4). A documentação do shadcn só mostra registros por
URL https, então o MCP não lê este arquivo sozinho; ele serve de índice ao implementador.

Testes: `python -m pytest tests/test_agentes_ux.py -q` → 18 passed.

Não conferido: se o Claude Code carrega os seis agentes e se os MCPs sobem. Uma sessão só lê `.claude/agents/` do próprio projeto ao
abrir, e o `frontend-design` não está instalado nesta máquina (UX-6); sem ele, a skill é pulada com aviso.

## 12. Etapa P1: a prancha da B e o código (2026-11-06)

**A prancha.** Está no branch `v3-ux-p1` (PR #596). A B foi refeita a partir do que o motor registra: a linha do agora lê
`Motor.digibrain().decisao`, e o balão leva o chip só quando há `MotivoVida`. O Matheus aprovou a prancha e as P1-1 a P1-6 (seção 8.1).

**O código.** Está no branch `v3-ux-p1-codigo`, empilhado sobre o #596. Foi feito pelo `ux-implementador`, testado pelo
`ux-browser-tester` e revisto pelo `rev-a11y`, pelo `rev-cena` e pelo `rev-replay`.
- **Arquivos:** `LinhaAgora.tsx` é novo. A linha entra por portal num encaixe do `Topo.tsx`, logo depois da plaquinha. O chip mudou no
  `Causa` do `TelaPet.tsx`, e os estilos estão em `pet_hud.css`.
- **Testes:**
  - `npm run tipos`: ok;
  - `npm test`: 836 passed;
  - `npm run e2e`: 123 passed.
- **Capturas:**
  - A comparação foi feita contra uma linha de base capturada do `v3-ux-p1`, que é o app de antes da mudança. As referências de
    2026-10-31 estão defasadas do app de hoje em todas as telas.
  - Mudam só as telas Pet, na faixa do topo, que é a linha do agora. O resto é ruído do quadro do sprite e da cena 3D.
- **Achado de processo:** sem `DIGILAB_CAPTURAS`, o `npm run capturas` compara contra `../../artifacts_v2_front_react/capturas` da
  própria worktree. Numa worktree nova essa pasta não existe, e o Playwright grava as imagens como referências novas, em silêncio.
  - Não foi regravada nenhuma referência verdadeira. As de `D:\Trab\digilab\v3\artifacts_v2_front_react\capturas` estão intocadas.
  - O teste da pasta sem referência fica como pendência para o H6 ou o G-REFERENCIA.

## 13. Etapa M1: o mobile mínimo, a tela Pet sem a barra de abas (2026-11-06)

**A prancha.** A Digivice (commit `08b3dff8`) foi reprovada. A mínima (`docs/pranchas/ux-mobile/`, commit `1d04d92e`) foi aprovada com
as M1-1 a M1-15 (seção 8.1). O plano está em `docs/PROPOSTAS_V3_UX_TELA_PET.md`, seção "Mobile mínimo (M1)".

**O código.** Está no branch `v3-ux-mobile`, empilhado sobre o `v3-ux-p1-codigo`. Foi feito pelo `ux-implementador` e revisto pelo
`rev-a11y` e pelo `rev-cena`; os achados que bloqueavam e os que deviam estão corrigidos.
- **Abaixo de 900 px** ficam:
  - o retrato ("Painéis do pet") e a hora;
  - a coluna Conversar, Crescer, Lutar e Diário;
  - o ícone do agora;
  - as quatro ações só com ícone.

  O leque do retrato tem os vitais e os painéis, e o ⋯ tem as outras ações. A necessidade aparece no aviso, no ponto rosa e na ação rosa.
  A barra de abas sai, inclusive de dentro do modal.
- **Arquivos novos:** `src/movel.ts`, com o `SEGURAR_MS` e o estado do leque; `src/componentes/BotaoMovel.tsx`;
  `src/estilo/pet_movel.css`, todo dentro de `@media (max-width:899px)`; e `test/movel.test.ts`.
- **Arquivos alterados:** `TelaPet.tsx`, `LinhaAgora.tsx`, `Topo.tsx`, `App.tsx` e `PainelTela.tsx`. O desktop continua no corpo de
  antes, pelo `TopoLargo` e pelo `DockLargo`.
- **O desktop não muda:** os 42 DOM e as 42 capturas com a cena escondida (21 telas, nas duas peles, a 1920) são iguais à base. O
  portão foi trocado porque a base comparada com ela mesma já varia na cena 3D (desvio em `docs/registro/2026-11.md`).
- **Fica para a M2:**
  - nas folhas abaixo de 900 px, a faixa de 64 px que a barra reservava (o `--casca-barra`) continua vazia embaixo do modal;
  - a medida M3 da cena no celular, que agora é ~24 % maior, e do blur do Vidro (achados do `rev-cena`).

**A revisão do Matheus no #619 (2026-11-06): o sprite e o tamanho do pet.**
- **O sprite errado nas capturas** era a corrida do atlas de clipes com o relógio falso do `telas.spec.ts`, na base e no branch (desvio
  em `docs/registro/2026-11.md`). O spec agora espera o atlas e falha alto sem ele.
- **O pet.** Pelo `CENA.ret`, a 390 × 844 o pet tinha o mesmo tamanho em px (49 × 52 no v11 e 68 × 88 no v12), mas descia 109 px, centrado na
  caixa mais alta. Agora a câmera enquadra a altura antiga e estende o quadro para baixo:
  - na sala, `cena3d.ts`, pelo limite ortográfico;
  - na ilha, `ilha/vista.ts`, pelo `setViewOffset`.

  A diferença vem do `reservaDoPe()` em `cenaEstado.ts`: 157 px abaixo de 900 px, e 0 a partir daí. O número é PROPOSTO e SEM FONTE,
  medido como o dock de antes (69 px), mais a folga (24 px), mais a barra (64 px). O pet volta ao lugar de antes (171,424 no v11 e
  161,388 no v12).
- **O ícone do agora** fica preso logo acima da cabeça do pet, pelo `CENA.ret`.
- **Os portões de novo:**
  - o desktop (o DOM e a captura sem o canvas) dá 84 de 84 iguais;
  - a captura cheia a 1920 com o atlas carregado tem o mesmo perfil de ruído da base contra ela mesma;
  - o e2e inteiro dá 123 passed.

## 13. Etapa L1 de "Lugares da ilha": a câmera solta e o minimapa (2026-11-06)

**A direção.** O Matheus escolheu a B, "Lugares da ilha", entre as três da página de direção: cada menu vira um lugar da ilha. A L1 é o
primeiro passo e só vale a partir de 900 px. O plano, a prancha e as decisões L1-1 a L1-7 estão em `docs/PROPOSTAS_V3_UX_TELA_PET.md`,
seção "Lugares da ilha (L1)", e em `docs/pranchas/ux-lugares/`; as decisões, também na seção 8.1.

**O código.** Está no branch `v3-ux-lugares`, empilhado sobre o `v3-ux-p1-codigo`. É só vista: fora do save, do registro e do replay.
- `cameraLivre.ts` (novo): o ponto olhado, que solta do pet com WASD, as setas e o arrasto direito ou do meio; F, o retrato, o "seguir o
  pet" e o aviso de borda voltam; Q/E e +/− giram e aproximam. A vista (`ilha/vista.ts`) centra a câmera e a dobra no ponto olhado e
  publica a cada quadro o que o minimapa e a HUD leem (a versão só sobe quando algo mudou; abaixo de 900 px, nada).
- `Minimapa.tsx`, `minimapaGeo.ts` e `minimapa.css` (novos): o círculo de 232 px com a ilha da grade (`ilha/minimapa.ts`, nas cores da
  própria cena), o pet, o cone, os lugares e a comida; o clique, o arrasto, a roda (da ilha inteira até a janela em volta da câmera) e o
  teclado (setas e Enter).
- `CameraHud.tsx` (novo): o "seguir o pet" e o aviso de borda, com uma região viva para o leitor de tela.
- `TelaPet.tsx`: a etiqueta do DigiBrain virou a 4ª linha da pilha. `Topo.tsx`: com a câmera solta, o retrato vira "Seguir o pet".
- `ilha/papel.ts`: com o pet longe do ponto olhado, o papel desce com o chão dobrado e tem o tamanho da distância dele.
- **Testes:** `npm run tipos` ok; `npm test` 866 passed (93 arquivos); `npm run e2e` 125 passed (porta 8833), com o
  `e2e/camera_livre.spec.ts` novo (o D solta, o F volta, o minimapa leva a câmera, o DigiBrain pela pilha, nenhum evento novo no registro;
  no celular nada disso existe).
- **O celular sai igual:** o DOM e a captura com o canvas escondido, 22 telas × 390 e 360 × Vidro e Militar (88), base (`60f4f441`) ×
  branch: 0 diferenças de DOM e 0 de pixel. A única diferença de uma rodada, no `evolucao-momento` (a revelação animada), não se repetiu em
  quatro rodadas de cada lado. O sprite das capturas é o do Digimon (o Gomamon), não a reserva.
- **Revisores:** `rev-replay` sem achado; `rev-a11y` e `rev-cena` com achados, os de custo baixo corrigidos (a pilha não desce até o
  minimapa e ele sai com pouca altura; as teclas respeitam `defaultPrevented` e mais papéis; a região viva; o papel do pet na dobra; o
  minimapa só redesenha quando algo muda; nada publicado abaixo de 900 px). Os outros ficam como questões abertas no PR.
- **As referências de captura a 1920** (`npm run capturas`) mudam nas telas Pet: o minimapa entra e a etiqueta sai. Não foram regravadas;
  isso espera o ok do Matheus.

## 14. Etapa D1: o DigiBrain "scan holográfico" (2026-11-07)

Branch `v3-ux-digibrain`, empilhada sobre a `v3-ux-integra`. A prancha (`docs/pranchas/ux-digibrain/`) e o ok do Matheus às D1-1 a D1-11
estão na seção 8.1 e em `docs/PROPOSTAS_V3_UX_TELA_PET.md`, seção "DigiBrain scan (D1)".

**O que mudou:**
- O painel do cérebro A dos pets v11 abre como "modo scan":
  - no desktop, um `<dialog>` modal em tela cheia por cima da ilha;
  - no celular, a folha inteira.
- O mapa dos pesos é o da prancha. Cada ponto é um nó do motor e cada fio é um peso de `Motor.digibrain().mapa`.
- O movimento:
  - a varredura e o pulso só aparecem numa decisão nova, e terminam;
  - o giro lento só existe no desktop;
  - com "reduzir movimento", nada se move.
- O `DigiBrainLab` continua no painel de hoje.

**Os arquivos:**
- novos: `web/app/src/componentes/ScanDigiBrain.tsx`, `web/app/src/estilo/scan_digibrain.css` e `web/app/test/scan_digibrain.test.ts`;
- mudados: `TelaPet.tsx` (o scan no lugar do painel do A, o chamado sobre o scan e o foco de volta), `DigiBrain.tsx` e `MapaPesos.tsx` (só `export`), `digibrain.css` e `e2e/jogo.spec.ts`.

**Os portões:**
- `npm run tipos` está limpo e o Vitest deu 95 arquivos e 891 testes.
- No `npm run e2e` (porta 8831), 131 passaram e 1 falhou: o `camera_livre.spec.ts:74`, que falha igual na base `v3-ux-integra` (procura o `.topo-retrato` "Meus pets", que a M1 trocou). Os 11 testes do DigiBrain passam.
- O "nada fora do DigiBrain muda": o DOM e a captura com o canvas escondido, nas 21 telas do `telas.spec.ts`, a 1920 e a 390, nas duas peles, base × branch. Dá 84 DOM iguais e 84 capturas com 0 px de diferença. O ruído medido na base contra ela mesma é de no máximo 1 captura com 42 px por rodada.
- Revisaram o `rev-a11y`, o `rev-cena` e o `rev-replay`. Os achados que bloqueavam foram consertados: a cena coberta pelo scan, o vidro de tela cheia, o foco de volta à pilha, os 11 px do texto do desenho e o mapa em texto que cobria o botão.

**PROPOSTO, SEM FONTE:** a varredura em 1,2 s, o pulso em 0,8 s, o giro de ±8° em 40 s e os números de layout. O desvio está em
`docs/registro/2026-11.md`.

## 15. Etapa D1b: o DigiBrain como modal pequeno (2026-11-07)

O Matheus trocou a tela cheia da D1 por um modal pequeno, só com o mapa dos pesos. A prancha `docs/pranchas/ux-digibrain/modal.html` e o ok
dele às D1b-1 a D1b-7 ("Aprovar e codar") estão em `docs/PROPOSTAS_V3_UX_TELA_PET.md`, seção D1b. Fica no mesmo PR da D1.

**O que mudou:**
- **Desktop:** o `<dialog>` modal fica à direita, com até 720 px, sobre a pilha de painéis, e o pet fica à vista no meio.
- **Celular:** abaixo de 900 px, uma folha baixa presa embaixo.
- **Fechar:** pelo Esc, pelo X ou com um clique fora. O foco volta a quem abriu.
- **O que sai:**
  - os seis cartões, a legenda do rodapé e o parágrafo;
  - o "pesou mais" e a região da memória;
  - o `CENA.coberto` e o fundo opaco. A ilha fica a pleno ritmo sob um véu leve, sem desfoque, e o vidro da pele fica só na caixa.
- **O que fica:**
  - o selo, só como forma;
  - o "i", com a dica (a forma é só desenho, a legenda curta e o significado do selo);
  - o mapa em texto, como botão de ícone que troca o desenho;
  - as regiões "ações", "regras", "percepção" e "receptores do corpo".
- O movimento é o da D1.

**Os arquivos:** `ScanDigiBrain.tsx`, `scan_digibrain.css`, `test/scan_digibrain.test.ts` e `e2e/jogo.spec.ts`. O `TelaPet.tsx` não mudou.

**Os portões:**
- `npm run tipos` está limpo. O Vitest dá 95 arquivos e 893 testes, inclusive o contraste do desenho sobre a ilha nas duas peles.
- No e2e inteiro (porta 8831), 132 passaram e 1 falhou: o `camera_livre.spec.ts:74`, herdado da base. Depois dos consertos das revisões, os 12 e2e do DigiBrain passam.
- O portão "nada fora do DigiBrain muda": 21 telas, a 1920 e a 390, nas duas peles, base × branch.
  - Na primeira rodada, as 84 telas deram DOM igual e 0 px.
  - Na segunda, uma captura deu 310 px: a `evolucao-momento` a 390 no Militar. Rodada de novo duas vezes, deu 0 px e o mesmo DOM.
- O `rev-replay` e o `rev-cena` não acharam bloqueios. O `rev-a11y` achou dois, e os dois foram consertados:
  - o foco ao abrir caía no botão do chamado;
  - o contraste não era medido, e agora há um teste.

**Fica pendente:** a medida de quadros com `?medir3d=1`, com o modal aberto e fechado, nas duas peles, no desktop e no celular. O `rev-cena`
a pede antes da aprovação final do vidro na caixa.

**PROPOSTO, SEM FONTE:** os 720 px, a metade da direita com o piso de 560 px, a folha e o véu a 28 %. Os desvios estão em
`docs/registro/2026-11.md`, seção D1b.

## 16. Etapa D1c: o DigiBrain como campo pequeno (2026-11-07)

O Matheus achou o modal da D1b grande demais ("Ele tem que ser um campo pequeno"). Viu duas opções capturadas no jogo
(`D:\Trab\digilab\capturas_ux_digibrain_aprovar\modal_menor\`) e escolheu "(a) desk, (b) celular" (`docs/PROPOSTAS_V3_UX_TELA_PET.md`,
seção D1c). Fica no mesmo PR da D1.

**O que mudou:**
- **Desktop (900 px ou mais):** um painel de 420 px sob o relógio, no lugar da pilha de painéis. A altura acompanha o desenho (~312 px a
  1920).
- **Celular:** uma folha de 210 px na largura toda, com o ícone, o selo e os botões numa coluna à esquerda do desenho. Os nomes das regiões
  saem.
- **O título** é só o ícone do cérebro; o nome "DigiBrain" fica num `.sr-only`, e o diálogo continua com esse nome.
- **Os rótulos:** só o caminho aceso (as entradas das arestas acesas, a regra e a ação) e as candidatas, com a chance. O de outro ponto
  aparece ao passar o mouse ou ao tocar nele; tocar é só vista e não grava evento. A dica do "i" diz isso e aponta o mapa em texto.
- Os botões do topo continuam com 44 × 44 px.

**Os arquivos:** `ScanDigiBrain.tsx`, `scan_digibrain.css` e `e2e/jogo.spec.ts` (o tamanho e o lugar, o título só com o ícone e um teste novo
dos rótulos a 390 e a 1280).

**Os portões:**
- `npm run tipos` está limpo. O Vitest dá 95 arquivos e 893 testes; depois dos consertos do `rev-a11y`, o `scan_digibrain.test.ts` deu 14/14.
- No e2e inteiro (porta 8831), 134 passaram e 1 falhou: o `camera_livre.spec.ts:74`, herdado da base. Depois dos consertos, os 14 e2e do
  DigiBrain e o `lab_modular.spec.ts` passam.
- O portão "nada fora do DigiBrain muda": 21 telas, a 1920 e a 390, nas duas peles, base × branch.
  - Nas duas rodadas, o DOM das 84 telas ficou igual.
  - As capturas tiveram diferenças pequenas que trocam de tela de uma rodada para outra: 4 telas na primeira (26 a 698 px) e 1 na segunda
    (73 px). Três delas, rodadas de novo, deram 0 px. A que ainda variou, a `crescer-itens` a 390 no Vidro (42 px), varia no mesmo lugar
    entre duas capturas da própria base. É ruído.
- O `rev-a11y` barrou os botões de 36 px das capturas das opções. Eles voltaram a 44 px. Das ressalvas, foram aceitas a dica com altura
  máxima a 390, um alvo de toque maior no celular e a linha da dica sobre o mapa em texto.

**PROPOSTO, SEM FONTE:** os 420 px, a folha de 210 px e o corte em 900 px (o pedido falava em 768). Os desvios estão em
`docs/registro/2026-11.md`, seção D1c.

## 17. Etapa D1d: as pendências do DigiBrain depois do merge (2026-11-07)

O PR #668 (D1, D1b e D1c) foi mergeado na `v3-ux-integra`. Depois disso, o Matheus pediu "siga com as recomendações". Esta etapa fecha as
pendências que o relato do #668 deixou, num PR próprio (branch `v3-ux-digibrain-d1d`).

**O que foi feito:**
- **O movimento:** fica como está, só a 1x ou mais devagar, pela recomendação. Está registrado em `docs/PROPOSTAS_V3_UX_TELA_PET.md`, seção D1c.
- **A medida de quadros (M3, `?medir3d=1`):** feita no Chrome do PC, sem tela, nas duas peles, a 1280 × 800 e a 390 × 844, com o DigiBrain
  fechado e aberto.
  - Os oito casos deram 60 fps, com a mediana de 16,7 ms e o p95 de 16,8 ms por quadro.
  - O JSON de cada medida está em `D:\Trab\digilab\capturas_ux_digibrain_aprovar\m3\`.
  - Abrir o campo não derruba quadros no PC. Um celular de verdade continua sem medida.
- **O zoom de 200%:** não pediu código. Um e2e novo confere que o campo cabe inteiro, com os botões do topo dentro, a 960 × 400, 960 × 300 e
  640 × 360 em CSS.
- **O código sem uso saiu:**
  - o `ConteudoDigiBrain`, os selos antigos e o ícone, em `DigiBrain.tsx`;
  - o `MapaPesos` e a `LegendaMapa`, em `MapaPesos.tsx`;
  - as regras de `digibrain.css` que mais nada usa.

  O `PainelDigiBrain` só monta o do modular e levanta erro com o A v11.

**Os portões:**
- `npm run tipos` está limpo. O Vitest dá 95 arquivos e 893 testes.
- No e2e inteiro (porta 8831), 137 passaram e 1 falhou: o `camera_livre.spec.ts:74`, herdado da base.
- O portão "nada fora do DigiBrain muda": 21 telas, a 1920 e a 390, nas duas peles, base × branch.
  - O DOM das 84 telas ficou igual.
  - Duas capturas tiveram diferenças pequenas: a `crescer-itens` a 390 no Vidro (42 px) e a `lutar-fronteira` a 1920 no Militar (26 px).
    As duas já tinham variado na D1c, e a primeira varia no mesmo lugar entre duas capturas da própria base.
- As 6 capturas do DigiBrain aberto (duas peles, 1920 e 390, mais a dica a 1920) saíram iguais às da D1c, pixel a pixel.

**Fica com o Matheus:** a M3 num celular de verdade, com `?medir3d=1`. O porquê do cérebro modular no mesmo campo (D1-9) é a próxima etapa,
com prancha.
