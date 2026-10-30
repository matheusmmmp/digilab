# CLAUDE.md — o jogo web (`web/app/`)

Vale junto com o `CLAUDE.md` da raiz. O que o jogo já tem, seção a seção, está em `docs/historico/claude/jogo_web.md` e
`docs/historico/claude/combate.md`.

## Regras

- **O motor** fica em `motor/` e não tem DOM: a lib ES não tem "dom", e o teste `motor_sem_dom` confere. `index.ts` exporta tudo, e
  `Motor.aplicarEvento` é o passo do replay. **As telas** ficam em `src/` e leem o motor por `useJogo()`; só `mudarMotor()` altera e grava.
- **Toda mudança de jogo vai também para cá.** A pesquisa fica no Python, mas uma regra de jogo nova entra no motor TS, com paridade.
- **Uma versão de pet por mecânica** (`VERSAO_PET` em `motor/constantes.ts`). Os pets das versões antigas, as assinaturas e os gabaritos
  não mudam. Apagar ou descartar saves só com decisão do Matheus, e com aviso na tela.
- **Paridade com o Python:**
  - os gabaritos saem dos exportadores `experiments/exportar_*.py` e ficam em `test/gabaritos/`;
  - a paridade é bit a bit só no mesmo runtime (o Node; o Chrome difere no último bit de `exp` e `log`);
  - uma constante nova do Python é conferida por `constantes.test.mjs`.
- **Na tela, os nomes são os do Digimon:** as formas, os NPCs, os níveis (In-Training, Rookie, Champion, Ultimate, Mega) e os brasões
  das espécies (brasa Coragem, cirro Amizade, ferrugem Conhecimento, limo Sinceridade). Os ids internos, o log e o save não mudam.
- **Layout (2026-10-30, `docs/TAREFA_V2_LAYOUT_HABITAT.md` e `docs/UI_GUIDELINES.md` §8):**
  - o habitat ocupa a tela inteira em todas as larguras; as outras telas abrem sobre ele (painel à direita a partir de 900 px,
    modal centralizado abaixo); a referência são as pranchas D descritas na tarefa, não as `*Desktop` de `docs/estilo_up/pranchas/`;
  - o botão **Conversar** fica no cabeçalho no celular e no trilho de ícones no desktop;
  - menus com a pele XCOM (tokens `--hx-*`, componentes `hx-*`, sempre escura); habitat com `--dl-*`/`dl-*` e o tema claro/escuro;
    desde o HUD (`docs/TAREFA_V3_LAYOUT_HUD.md`, 2026-10-30) a plaquinha do pet, o relógio do topo e o balão da fala também ficam no
    sistema dos menus, e Estado, Evolução e Últimas ações ficam empilhados à direita a partir de 900 px.
- **Semear um save em teste:** por uma página da mesma origem que não seja o app, senão o app grava o pet dele por cima ao fechar.

## Comandos

```bash
npm install
npm run dev      # http://localhost:5173
npm run build    # sai em web/dist/ (não versionado); o servidor local serve em /v1/web/dist/
npm run tipos    # tsc estrito: o motor sem DOM e o app
npm test         # Vitest: paridade, motor e telas
npm run e2e      # build e Playwright no Chrome instalado, porta 8799
```
