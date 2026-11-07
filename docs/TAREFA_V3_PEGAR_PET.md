# TAREFA V3 — PEGAR_PET (2026-11-07)

Coordenador: a sessão de planejamento do Claude Code. Worker: Claude Code (Opus 5.5), uma sessão por etapa. Worktree e branch:
`v3-pegar-pet` (a P1 no branch `v3-pegar-pet-p1`). Status: EM ANDAMENTO (a P1 e a P2 entregues, nos PRs).

Categoria: implementacao. Origem: Matheus, 2026-11-07: o dono pega o pet com o mouse, o pet se balança agoniado e com careta, e cai onde
for solto.

O pedido, nas palavras do Matheus:

> o usuário vai pegar com o mouse e quando ele clicar no patch [pet] e segurar, ele vai agarrar o patch. E daí é onde o usuário soltar o
> patch vai cair. E quando o usuário segura o patch, ele vai fazer uma animação dele se balançando, agoniado [...] E fazendo uma careta.

## 1. Pergunta

Nenhuma hipótese de pesquisa: é uma mecânica do produto jogável (a direção de 2026-10-24, `docs/PRODUTO_VISAO.md`). O dono ganha o
primeiro gesto que move o pet no habitat. Até aqui, o pet só anda por decisão própria (`Mundo.consequencia`), e as únicas ações do dono
no mundo são deixar a comida (`dc`) e deixar a bola (`db`).

## 2. Depende de

- Na `main`: o habitat 3D (`docs/TAREFA_V3_HABITAT_ILHA.md` e seguintes), o arrasto da bola (`src/telas/pet/PorBola.tsx`, o `ArrastoBola`)
  e as reações de rosto (as poses `Medo` e `Stun`).
- As decisões PP-1 a PP-5 do Matheus (seção 3.1), aprovadas em 2026-11-07 ("Aprovo as recomendações").
- A P2 depende da P1 na `main`.

## 3. Mudança mínima

### 3.1 As decisões (Matheus, 2026-11-07)

- **PP-1:** nesta versão, pegar o pet muda só a posição. Não mexe no humor, na química nem no aprendizado, e não conta como contato nem
  como cuidado.
- **PP-2:** um pet dormindo não pode ser pego.
- **PP-3:** a careta usa poses que já existem: `Medo` nas formas que têm reações de rosto, `Stun` nas outras. Custo zero, nenhum sprite
  novo.
- **PP-4:** se o pet for solto fora do mapa, cai na borda mais próxima.
- **PP-5:** o gesto de pegar começa ao arrastar mais de 6 px a partir do pet, sem precisar segurar parado. O toque rápido continua sendo
  carinho.

### 3.2 As etapas

**P1, o motor** (esta entrega): um evento novo do dono no log, "levar pet", com a posição `{x, y}` em subunidades inteiras do mundo.

- **No TS** (`web/app/motor/`):
  - `tipos.ts`: o `EventoLevarPet`, `[tick, "lp", { x, y }]`, no `EventoRegistro`; a `VersaoPet` até 19;
  - `mundo.ts`: o `eventoLevarPet` e o `lerLevarPet` (o formato do log do Python, `x|y`, inteiros com sinal) e o `Mundo.levarPet`, que põe
    o pet em `noMapa(x, y)`, limpa o destino `pendente` e grava a levada em `levadas` (no `resumo()` só quando houver alguma);
  - `motor_corpo_mundo.ts`: o `levarPet` (com o log do laço) e o `petDoDono` (sem o log, para o Motor do jogo) e o `levar_pet` no
    `aplicarEvento`; levanta erro com o pet dormindo; não chama gancho do cérebro nem do corpo;
  - `motor.ts`: o `Motor.levarPet(x, y)` do dono e o `_levarPet`, e o `"lp"` no `aplicarEvento`, com a conferência das chaves (`x,y`);
    levanta erro com o pet dormindo, morto ou de versão anterior à v19.
- **A versão do pet:** a v19 (a v18 com o "levar pet"). `VERSAO_PET` e `VERSOES_PET` em `motor/constantes.ts`. A v19 luta como a v18 e é
  de cérebro trocável. Os pets v13 a v18 não mudam, e o evento numa versão anterior levanta erro.
- **No Python, a paridade:** `digilab/events.py` (`levar_pet`, `ler_levar_pet`) e `digilab/mundo.py` (`MotorMundo.levar_pet`,
  `_aplicar_levar_pet` e o `reproduzir_mundo`), no padrão do `deixar_bola`.
- **Os testes:** `tests/test_levar_pet.py` e `web/app/test/levar_pet.test.ts`, espelhados; o gabarito
  `web/app/test/gabaritos/levar_pet_python.json`, exportado por `experiments/exportar_gabarito_levar_pet.py` e conferido pelo laço
  gravado do G-PAR do MVP (`web/app/test/laco_gravado.ts`).

**P2, a tela e a animação** (outra sessão, depois da P1 na `main`):

- o arrasto segue o modelo do `ArrastoBola` (`src/telas/pet/PorBola.tsx`), com Pointer Events, e grava o `Motor.levarPet(x, y)` por
  `mudarMotor()` ao soltar;
- uma marca `CENA.petNaMao` impede a câmera livre (`orbita.ts`) de girar e faz a câmera parar de seguir o pet enquanto ele está na mão
  (`vista.ts`);
- o papel do sprite balança como um pêndulo, com um tremor, e mostra a careta (PP-3);
- uma sombra no chão mostra onde o pet vai cair (já limitada ao mapa, PP-4);
- ao soltar, um quique pequeno;
- com `prefers-reduced-motion`, sem balanço, só a careta;
- o pet dormindo não é pego (PP-2): o arrasto não começa;
- capturas em 390 e 1280 px, aprovadas pelo Matheus antes do PR.

### 3.3 O que não muda

- O `digilab/engine.py`.
- Os pets v13 a v18, as assinaturas e os gabaritos, byte a byte: os testes `mvp_mundo`, `mundo`, `v12_jogo_ts`, `v13_vidas_ts` e
  `contrato` passam sem mudança.
- O humor, a química, o aprendizado, o contato e o cuidado (PP-1): o evento não passa pelo estado, pelo corpo nem pelo cérebro.
- O `grupo.Grupo` (dois pets): fica sem o "levar pet" nesta versão.

## 4. Experimento e gate (se houver run)

Não há run. O gate é de código:

- em `web/app`: `npm test` e `npm run tipos`;
- no Python: `tests/test_levar_pet.py` e os testes de mundo e replay;
- `python tools/conferir_saude.py`.

## 5. Entrega

- Testes: `python -m pytest tests/ -q`; em `web/app`: `npm test`, `npm run tipos`, `npm run e2e` (se a frente toca a web).
- Registro: seção própria no fim do arquivo do mês, `docs/registro/AAAA-MM.md` (rodada de saúde, etapa 2). **Não edite o índice
  `docs/REGISTRO_DESVIOS.md`:** ele é gerado (`python tools/gerar_indice_desvios.py`) por quem faz o merge. Um conflito nele se resolve
  rodando o gerador, nunca à mão (`docs/TAREFA_V3_INDICE_DESVIOS.md`). O resumo da etapa vai no corpo do PR e numa seção no fim do documento da
  frente (o `RESULTADO_V3_*.md` da run ou o `TAREFA_V3_*.md` da etapa), nunca no `CLAUDE.md` (rodada de saúde, etapa 1).
- PR contra a `main` com resumo e números (cada um com o artefato). Aviso ao coordenador. Merge só pelo Matheus.
- O corpo do PR segue `.github/pull_request_template.md`; o CI (`tools/verificar_relato.py`) confere os campos e a evidência da categoria.

## 6. Fora desta tarefa

- Qualquer efeito de pegar o pet no humor, no corpo, no vínculo ou no aprendizado (PP-1). Se um dia o pet sentir o colo, é uma tarefa e uma
  versão de pet novas.
- Sprites novos para a careta (PP-3).
- O "levar pet" no `grupo.Grupo` e no dono sintético da bancada.
- Pegar outros objetos além do pet e da bola.

## 7. Critérios de aceitação

- P1:
  - `tests/test_levar_pet.py` e `web/app/test/levar_pet.test.ts` passam;
  - o TS refaz o gabarito `web/app/test/gabaritos/levar_pet_python.json` decisão a decisão e bit a bit no Node (o log, o mundo, o corpo e o
    estado no fim);
  - o "lp" vai ao registro, refaz no replay bit a bit e levanta erro com o pet dormindo, numa versão anterior à v19 e com as chaves erradas;
  - os testes `mvp_mundo`, `mundo`, `v12_jogo_ts`, `v13_vidas_ts` e `contrato` passam sem mudança no arquivo;
  - `npm run tipos` e `python tools/conferir_saude.py` passam.
- P2: as capturas em 390 e 1280 px aprovadas pelo Matheus; o toque rápido segue sendo carinho; o pet dormindo não é pego.

## 8. Precisa do Matheus

Nenhuma decisão nova na P1. A P2 leva as capturas para a aprovação dele antes do PR.

## 9. Resumo da P1, o motor (2026-11-07)

Worker: Claude Code (Opus 5.5), branch `v3-pegar-pet-p1`, de `origin/main` em `3d790725`.

- **O evento.** No jogo, `[tick, "lp", { x, y }]` (`Motor.levarPet`); no laço e no Python, `levar_pet` com o valor `x|y` (inteiros com
  sinal, na forma canônica). O log guarda o ponto onde o dono soltou; o motor põe o pet em `noMapa(x, y)` (PP-4) e limpa o `pendente`.
- **A v19.** `VERSAO_PET = 19`, `VERSOES_PET = [13, 14, 15, 17, 18, 19]`, `VERSAO_V19`. A v19 luta como a v18 (`CV21E_TR18`) e é de cérebro
  trocável (`ehCerebroTrocavel`). O "lp" numa v13 a v18 falha alto, no método do dono e no replay.
- **PP-1.** O evento não passa pelo estado, pelo corpo nem pelo cérebro (nenhum gancho). O teste do TS confere a assinatura inteira do
  Motor, menos o mundo, antes e depois; o do Python, o `_estado` e um espião dos ganchos.
- **PP-2.** O pet dormindo (o `estado.dormindo` do laço, o mesmo nos dois lados) falha alto antes do log, no Motor, no laço e no Python.
- **O registro das levadas.** `levadas` (tick, de, pedido, para) no mundo; a chave só aparece no resumo quando houver alguma.
- **A paridade.** O gabarito `web/app/test/gabaritos/levar_pet_python.json` (`experiments/exportar_gabarito_levar_pet.py`): duas vidas
  (sementes 101 e 202) de 2 dias do A v11 com o corpo no mundo do MVP, com 28 e 27 levadas (14 delas fora do mapa em cada vida) e 19 e 20
  recusas com o pet dormindo. O TS refaz as duas decisão a decisão (208 cada), com o log, o mundo, o corpo e o estado no fim, e recusa em
  cada tick de `dormindo_em` (`web/app/test/levar_pet.test.ts`).
- **O gate.** `npx vitest run --maxWorkers=4`: 106 arquivos, 1 041 testes; `npm run tipos` passa. Python: `tests/test_levar_pet.py` (10) e
  os de mundo, gabaritos e replay em dois lotes (285 e 223 testes). `python tools/conferir_saude.py` passa. A suíte Python inteira não
  rodou (~36 min).
- **Os desvios:** `docs/registro/2026-11.md`, seção "PEGAR_PET, P1" (D-PP-P1-1 a 7).
- **Para a P2:** só a v19 é levada; um pet v18 vivo não (D-PP-P1-7). A tela grava `Motor.levarPet(x, y)` ao soltar, com `x` e `y`
  inteiros, e não precisa limitar o ponto ao mapa (o motor limita); a sombra do pouso usa o mesmo `noMapa`.

## 10. Resumo da P2, a tela e a animação (2026-11-07)

Worker: Claude Code (Opus 5.5), branch `v3-pegar-pet-p2`, de `origin/v3-pegar-pet-p1` em `695a0d12` (depende do #673).

- **O gesto** (`web/app/src/telas/pet/PegarPet.tsx`, no modelo do `ArrastoBola`): um pointerdown no sprite e um arrasto de mais de 6 px
  pegam o pet (PP-5), com o mouse e com o dedo. O toque rápido segue sendo carinho: o `ToquePet` larga o toque quando o pet está na mão
  (ele fica ligado antes do `PegarPet` no mesmo alvo). Não pega: o pet dormindo (PP-2), no ovo, morto, de versão anterior à v19, com um
  painel por cima ou com a bola na mão.
- **A câmera:** a marca `CENA.petNaMao` (`cenaEstado.ts`) para a câmera livre (`orbita.ts`: não gira nem aproxima) e prende a câmera e o
  foco da dobra (`ilha/vista.ts`), então o `paraMundo` não muda sob o dedo.
- **Na mão** (`ilha/mao.ts` e `ilha/papel.ts`): o papel sobe do chão, segue o ponteiro, balança como um pêndulo preso pelo alto, com um
  tremor de 1 texel, e faz careta (PP-3): o `Medo` com a gota nas formas com reações de rosto, o `Stun` nas outras. Nenhuma parte nem
  sprite novo. A sombra fica no chão onde ele vai cair, já no mapa (PP-4).
- **Ao soltar:** o `Motor.levarPet(x, y)` por `mudarMotor()`, no ponto do chão sob o pé; a queda e um quique pequeno; o desenho começa onde
  o motor o pôs (`Seguidor.pular`), sem correr de volta. Com movimento reduzido, só a careta.
- **PP-1:** a tela só grava o "lp"; nada no humor, na química, no aprendizado, no contato ou no cuidado. O motor não mudou além da P1.
- **O gate:** `npx vitest run --maxWorkers=4`: 107 arquivos, 1 052 testes (os 11 novos em `web/app/test/pegar_pet.test.ts`: o arrasto
  acima de 6 px pega, o toque curto é carinho, o pet dormindo não é pego, as contas do pêndulo, do tremor e do quique); `npm run tipos`
  passa; o e2e `web/app/e2e/pegar_pet.spec.ts` (1280 e 390 px: o "lp" gravado e o pet do motor no lugar novo) passa com o
  `vida_pet_cena` e o `sprites_comer`.
- **As capturas** (aprovadas pelo Matheus): `web/app/e2e_capturas/pegar_pet_p2.spec.ts`; os GIFs do bebê (Stun) e do Rookie (Medo) em 390
  px (com o dedo) e 1280 px, e as folhas nas peles vidro e militar, fora do repositório (na pasta de notas das sessões).
- **Os desvios:** `docs/registro/2026-11.md`, seção "PEGAR_PET, P2" (D-PP-P2-1 a 7).
