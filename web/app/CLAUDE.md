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
- **Layout:**
  - em tela larga, seguir as pranchas `*Desktop` de `docs/estilo_up/pranchas/`; em tela estreita, as de 390 px;
  - o botão **Conversar** fica no cabeçalho do Pet no celular e no pé da barra lateral no desktop;
  - tokens `--dl-*` e componentes `dl-*` (`docs/UI_GUIDELINES.md`).
- **Sprites da Bandai:** só aqui, só para uso pessoal e local. O atlas fica fora do repositório (`D:\Trab\digilab\Assets`). Nunca publicar
  a versão com sprites.
- **Semear um save em teste:** por uma página da mesma origem que não seja o app (por exemplo `/Assets/digilab_atlas_up.json`), senão o app
  grava o pet dele por cima ao fechar.

## Comandos

```bash
npm install
npm run dev      # http://localhost:5173
npm run build    # sai em web/dist/ (não versionado); o servidor local serve em /v1/web/dist/
npm run tipos    # tsc estrito: o motor sem DOM e o app
npm test         # Vitest: paridade, motor e telas
npm run e2e      # build e Playwright no Chrome instalado, porta 8799
```
