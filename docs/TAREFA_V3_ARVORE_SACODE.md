# TAREFA V3 — ARVORE_SACODE (2026-11-07)

Coordenador: a sessão da frente UX_TELA_PET (ilha interativa) do Claude Code. Worker: Claude Code (Opus 5.5), uma sessão por etapa.
Worktree e branch: `v3-arvore-sacode` (as etapas em `v3-arvore-sacode-s1`, `-s2`, `-s3`). Status: EM ANDAMENTO (o plano
aprovado em 2026-11-08; a S1 começa).

Categoria: arquitetura. Origem: Matheus, 2026-11-07, na prancha A da ilha (PR #691, a pergunta I1-3):

> Acredito que a ideia de clicar na árvore, ela sacudir, é interessante para cair a flor, né? A fruta

Esta etapa (S0) é só o plano. Não tem código, run nem gabarito. As perguntas AS-1 a AS-10 (seção 8) foram APROVADAS pelo Matheus em
2026-11-08, todas pela recomendação; as etapas S1 a S3 seguem o plano da seção 3 como está.

## 1. Pergunta

Nenhuma hipótese de pesquisa: é uma mecânica do produto jogável (a direção de 2026-10-24, `docs/PRODUTO_VISAO.md`) e a primeira peça da
ilha interativa (direção A, "objetos que falam"). O dono ganha um gesto novo no mundo, **sacudir a árvore X**: a árvore balança e, se tiver
fruta no galho, cai uma no chão perto do tronco. O pet a percebe e come como qualquer comida do chão. Hoje o jogo não tem árvore com fruta.

### 1.1 O que existe hoje (lido em 2026-11-07, `origin/main` a29424db)

- **No Python:** `digilab/mundo.py`, a classe `Mundo`, tem as árvores do layout (`ConfigMundo.layout.arvores`, `(id, x, y, fruta)`), a
  queda natural (`Mundo.atualizar`: a cada `passo_mundo_ticks` = 15 ticks, cada árvore fora da recarga sorteia a queda com
  `p_queda_jardim` = 1/96 ou `p_queda_mata` = 2/96 no fluxo `mundo-arvores`; caem de 1 a 3 frutas a até `raio_queda_celulas` = 2 células,
  com teto de `max_frutas_por_arvore` = 4 no chão por árvore, e a árvore entra em recarga por `recarga_min` = 720 ticks). A fruta caída é
  uma comida com `origem` = o id da árvore, madura por `maduro_fruta_min` = 720 ticks e podre por mais `prazo_podre_min` = 720. Os
  números são da `ConfigMundo`, todos PROPOSTOS, SEM FONTE.
- **Os gestos do dono sobre as árvores e as frutas no Python:** só os do J5 (o pet que pensa, `docs/TAREFA_V2_PET_QUE_PENSA*.md`):
  `dar_fruta_<f>` (a fruta na mão, comida na hora) e `trocar_arvores_<x>_<y>` (a troca de tipo), ambos `AcaoUsuario`, fora do orçamento e
  só com a `ConfigPetQuePensaMundo`; e o `parar_arvores` do adendo 8. Nenhum gesto faz cair fruta. O `deixar_fruta` do RP-2
  (`ConfigFrutaAoLado`) põe a fruta ao lado da ração. `digilab/frutas.py` (o N4) é o cenário antigo, sem posição, que o mundo substitui.
- **No TS:** `web/app/motor/mundo.ts` é o porte do `Mundo` (a mesma queda, a mesma recarga, os mesmos sorteios do CPython), com paridade
  pelo `test/mundo.test.ts`. A percepção (`perceber`: os vistos a até 6 células, o cheiro da fruta, `cheiro_fruta` = 32), o alvo padrão do
  comer (a comida boa vista mais próxima, `alvo_padrao_de`) e o "achou e comeu" do explorar (com a fome abaixo de `fome_max_comer_achado`)
  já tratam a fruta. Comer a fruta dá `nutricao_fruta` = 0,15 de fome e `efeitoFrutas[tipo]` de humor (0 por padrão). O modular vê as
  classes `a`, `b` e `c` (`motor/digibrain/sens.ts`, `CLASSES_OBJETO`).
- **O jogo:** os pets v12 a v19 rodam o `CMU_MVP` (`motor/constantes.ts`: `LAYOUT_MUNDO_MVP`, o padrão com `arvores: []`; a opção 1 do
  Matheus de 2026-10-24), espelho do `CONFIG_MUNDO_MVP` de `digilab/config.py`. Então o `atualizar` nunca sorteia nada e nenhuma fruta
  existe. Só a ração do dono vai ao chão (`Motor._validarComida`: "só a ração vai ao chão nos pets v12").
- **O paladar no TS:** não existe. `corpo.ts` falha alto com `ConfigCorpo.paladar` ligada (a etapa 5 do paladar, `docs/futuro/paladar.md`).
  O cérebro A do TS não tem o gancho `fruta_comida` (`motor_corpo_mundo.ts`).
- **A vista:** a ilha já põe as árvores do layout na área andável (`src/telas/pet/ilha/grade.ts`; o `test/ilha_grade.test.ts` confere os
  dois layouts, `CMU_MVP` e `CMU`), o minimapa já desenha `Mundo.arvores` (`Minimapa.tsx`) e a câmera livre já as conhece
  (`cameraLivre.ts`). A fruta no chão já tem cor (`COR_FRUTA`, `ilha/itens.ts`). As árvores que se veem hoje na ilha são enfeites dos kits
  (Quaternius, Kay), sem motor.
- **O modelo do gesto:** o `levar_pet` da v19 (`docs/TAREFA_V3_PEGAR_PET.md`): um evento tipado do mundo (`events.levar_pet`, o
  `[tick, "lp", { x, y }]` do registro do TS), que muda só o mundo, não é contato nem cuidado, falha alto com o pet dormindo ou de versão
  anterior, e tem gabarito do Python (`experiments/exportar_gabarito_levar_pet.py`).

## 2. Depende de

- Na `main`: o mundo no TS com paridade (`motor/mundo.ts`), a v19 (PEGAR_PET P1, #673) e a ilha com as árvores do layout (`ilha/grade.ts`).
- A prancha A da ilha (PR #691) para a vista: o cartão do objeto e o "toque faz o gesto" (a S3 só começa com ela aprovada).
- As respostas do Matheus às perguntas AS-1 a AS-10 (seção 8). A S2 depende da S1 na `main`; a S3, da S2.

## 3. Mudança mínima

O plano, com as recomendações das perguntas da seção 8 já aplicadas. Onde a resposta mudar, a etapa muda junto.

### 3.1 O evento do dono: "sacudir a árvore X" (AS-1, AS-2)

- **Evento novo, tipado, do mundo:** `events.sacudir_arvore(tick, arvore)` (tipo `sacudir_arvore`, valor = o id da árvore, por exemplo
  `"J1"`). No TS, `eventoSacudirArvore` e `lerSacudirArvore` em `motor/mundo.ts` e o `[tick, "sa", { arvore }]` no `EventoRegistro`
  (`motor/tipos.ts`). Um id que não é de árvore do layout falha alto.
- **O que ele é:** só um gesto sobre o mundo, como o `levar_pet` e o `deixar_bola`. Não é contato nem cuidado: não zera o tempo sem
  cuidado, não passa por `receber_acao_dono` (o cérebro não recebe o gesto), não mexe no corpo, no vínculo nem no histórico, e não atende o
  chamado da fome do bebê (os chamados do bebê pelo corpo, #465). No Python, fica fora do orçamento do `CanalMundo`, como o
  `deixar_bola` (o dono sintético da pesquisa não o usa).
- **Quando vale:** com o pet acordado ou dormindo (a árvore não depende do pet), nunca com o pet morto ou no ovo (falha alto, como os outros
  gestos). Só na versão nova (seção 3.5); numa anterior, falha alto.

### 3.2 O galho: o que cai, a recarga e o limite por dia (AS-2, AS-3)

- **O galho:** com a chave, cada árvore ganha `no_galho`, um inteiro de 0 a `galho_max`. Nasce cheio. Cada sacudida com fruta no galho e
  lugar no chão tira **uma** fruta do galho e a põe no chão; o galho repõe uma fruta a cada `recarga_galho_min` ticks (um relógio por árvore
  que só anda com o galho abaixo do máximo). O limite por dia sai do galho: no máximo `galho_max` frutas seguidas, e depois uma a cada
  `recarga_galho_min`. Com os números propostos, até 3 + 6 = 9 frutas por árvore por dia, com o dono sacudindo sem parar.
- **Números PROPOSTOS, SEM FONTE:** `galho_max` = 3, `recarga_galho_min` = 240 (4 h de jogo). Vão para a rodada de equilíbrio do fim
  (memória `equilibrio-no-fim`), não se calibram nesta frente.
- **Sem fruta no galho:** a árvore balança (a vista mostra) e nada cai. O registro guarda a sacudida com `caiu: null`.
- **Com o chão cheio:** o teto de hoje, `max_frutas_por_arvore` = 4 frutas da árvore no chão (maduras ou podres), vale também para a
  sacudida: com 4 no chão, nada cai e o galho não muda (`caiu: null`, `motivo: "chao_cheio"`).
- **A queda natural:** fica como hoje e independente do galho (AS-4). O fluxo `mundo-arvores` não muda, então as quedas naturais de uma
  semente são as mesmas com ou sem sacudidas, como o G-NUMS das quedas.

### 3.3 Onde a fruta cai e como o pet a percebe e come (AS-5, AS-6)

- **Onde:** um ponto sorteado como o da queda natural, `deslocar(x_tronco, y_tronco, randrange(16), randrange(raio_queda_celulas × sub +
  1))`, preso no mapa pelo `deslocar` de hoje. O sorteio é de uma rng própria do mundo, `derivar_semente("arvore-sacode", semente)`, que
  só anda quando cai uma fruta (dois sorteios por fruta). Nenhuma outra rng muda: nem `mundo-arvores`, nem `mundo-bola`, nem `alvo`, nem as
  do pet e do engine.
- **O que cai:** uma comida comum do `Mundo`, do tipo da árvore (`a`, `b` ou `c`), com `origem` = o id da árvore (conta no teto do chão como
  as naturais), madura na hora, com o mesmo prazo de maduro e podre das naturais.
- **Como o pet percebe:** nada novo. A fruta entra nos vistos a até `raio_visao_celulas` = 6 células, no cheiro (`cheiro_fruta` = 32, a
  até `raio_cheiro_celulas` = 24) e nos candidatos do comer e do explorar. O gesto em si não é percebido: não há som nem visão do dono
  sacudindo. O pet longe só acha a fruta pelo cheiro ou ao passar perto.
- **Como o pet come:** nada novo. O cérebro escolhe `comer` (ou acha no `explorar`), anda até a fruta e come: +0,15 de fome
  (`nutricao_fruta`) e o efeito de humor da fruta. No produto, o efeito de humor fica 0 para as três (`efeitoFrutas` padrão) e não há
  paladar: as três frutas só diferem na cor (AS-6). O consumo vai ao `consumos_mundo` como hoje.
- **O cérebro A e a fruta do mundo (AS-11):** o A v11 com o corpo falha alto ao comer uma fruta do mundo, no Python
  (`digilab/policies/lobos.py`, `fruta_comida` e `consequencia_corpo`) e no TS (`motor/lobos.ts`, "a fruta (E2) não existe no cérebro A
  em TS"); é o achado do MV-10 de 2026-10-24. Medido em 2026-11-08 no `CMU_MVP` com J1, J2 e J3, só com a queda natural, 3 dias, sementes
  101 a 505: 3 de 10 vidas quebram. A saída é uma subchave do A no produto, **a fruta do mundo como comida**: com ela, a fruta comida no
  mundo entra no A como a ração, sem a E2 do humor e sem a sub-decisão de fruta. Desligada, o A sai byte a byte. Entra no Python na S1 e
  no TS na S2.

### 3.4 Como o jogo passa a ter árvores com fruta (AS-7)

- **Um mundo novo, não o `CMU_MVP` mudado.** O `CMU_MVP` é parte da vida gravada dos pets v12 a v19: dar árvores a ele mudaria o replay de
  todo pet salvo. O novo é `LAYOUT_MUNDO_ILHA` = o `LAYOUT_MUNDO_MVP` com as três árvores do jardim do layout padrão (`J1` (22, 6) `a`,
  `J2` (29, 20) `b`, `J3` (19, 14) `c`), e `CONFIG_MUNDO_ILHA` / `CMU_ILHA` = o `CMU_MVP` com esse layout. Os números da `ConfigMundo`
  ficam os mesmos. Espelho campo a campo no TS, conferido pelo gabarito.
- **Só a versão nova roda o `CMU_ILHA`.** Os pets v12 a v19 seguem no `CMU_MVP`, sem árvores, para sempre. O pet atual do Matheus só
  ganha árvores com um ovo novo (AS-8).

### 3.5 A chave, o gabarito e o porte para o TS (AS-9)

- **A chave (Python):** `ConfigSacudir` em `digilab/config.py` (`ligada` = False, `galho_max`, `recarga_galho_min`), passada ao
  `MotorMundo` por `cfg_sacudir` e ao `Mundo` por `ligar_sacudir()`, como `ligar_trocas` e `ligar_necessidades`. Desligada (o padrão):
  nenhuma rng nova, nenhum registro, nenhuma chave nova em `estado()` nem no `resumo()`, e o `sacudir_arvore` falha alto
  (`SacudirSemChave`). Ligada: o `Mundo` guarda `no_galho` e o relógio de cada árvore e o registro `sacudidas` (tick, árvore, `no_galho`
  antes, `caiu` = o id da comida ou null, o motivo); o `reproduzir_mundo` refaz tudo pelo log. `engine.py` não muda.
- **A vida de hoje byte a byte:** com a chave desligada, todos os gabaritos de hoje saem iguais, reexportados (o `mundo`, o do produto
  `mvp_produto`, `decisao_na_comida` e `levar_pet`), e os testes do Python passam sem mudança.
- **O gabarito, gravado antes do TS:** `experiments/exportar_gabarito_arvore_sacode.py` →
  `web/app/test/gabaritos/arvore_sacode_python.json`: duas vidas (sementes 101 e 202, as dos gabaritos do produto) de 2 dias do A v11 com o
  corpo no `CONFIG_MUNDO_ILHA`, com um dono que alimenta como o do gabarito do produto e sacode nos casos de borda: galho cheio, galho vazio,
  chão cheio, pet dormindo, a mesma árvore várias vezes no mesmo tick, e as três árvores. O gabarito traz o log, os registros do mundo
  (`quedas`, `sacudidas`, `consumos`) e o estado a cada decisão.
- **O porte (TS):** `Mundo.sacudir(arvore, tick)` em `motor/mundo.ts` com a rng `arvore-sacode` no `RandomPy` (o mesmo Mersenne Twister do
  CPython); `CMU_ILHA` e `ConfigSacudir` em `motor/constantes.ts`; `MotorCorpoMundo.sacudirDoDono` e `Motor.sacudirArvore(id)` em
  `motor/motor.ts`, gravando `[tick, "sa", { arvore }]` e refeito no replay. O `test/arvore_sacode.test.ts` confere o gabarito campo a campo
  e bit a bit (o G-PAR).
- **A versão de pet:** a **v20** = a v19 com o mundo da ilha (`CMU_ILHA`) e o sacudir. `VERSAO_PET` = 20, `VERSAO_V20`, `VERSOES_PET` com o
  20. A v20 luta como a v19 e tem o cérebro da v19. O `Motor.sacudirArvore` falha alto antes da v20.

### 3.6 O que a vista mostra (AS-10)

Pela prancha A (PR #691): o toque no objeto abre o cartão, e o cartão faz o gesto (como a tigela, "Servir ração").

- **O cartão da árvore:** o nome da fruta e quantas há no galho ("2 no galho"; "galho vazio, volta em 3 h"), com o botão **Sacudir**.
  Fecha a lacuna I1-3 da prancha ("o número de frutas na árvore"). Mobile e desktop juntos, pouco texto.
- **O sacudir:** a árvore balança por cerca de 0,6 s (rotação da copa em torno do pé, só na vista). Com fruta, a fruta sai da copa e cai
  num arco curto até o ponto do motor, com um quique; daí em diante é a fruta no chão de hoje. Sem fruta, só o balanço.
- **As árvores do motor na ilha:** um modelo dos kits já usados (Quaternius), com as frutas do galho visíveis na copa como esferas na cor da
  fruta (`COR_FRUTA`): 3, 2, 1 ou nenhuma. Os enfeites continuam mudos. Nenhum asset novo pago (Meshy).
- **Fora da vista:** a animação não entra no save, no registro nem no replay; só o evento `sa` entra.

### 3.7 As etapas (um PR cada)

- **S1 (Python):** `ConfigSacudir`, `CONFIG_MUNDO_ILHA`, o evento, o `Mundo.sacudir`, o replay, os testes e o gabarito. Os gabaritos de hoje
  reexportados iguais.
- **S2 (TS, motor):** o porte, o `CMU_ILHA`, a v20, o `sa` no registro e no replay, os testes de paridade. Sem tela.
- **S3 (vista):** o cartão, o balanço, a fruta caindo e as frutas na copa; as capturas em 1920 × 950 e no celular, nas peles Vidro e
  Militar (memória `tema-menus-vidro`); o e2e do gesto.

### 3.8 O que NÃO muda

`engine.py`; `digilab/frutas.py` (o N4); o `CMU_MVP` e os pets v12 a v19; a queda natural e o fluxo `mundo-arvores`; os gestos do J5
(`dar_fruta`, `trocar_arvores`, `parar_arvores`); o cérebro A e o modular (nenhuma entrada nova); o corpo (nenhum órgão novo); as runs da
pesquisa.

## 4. Experimento e gate (se houver run)

Nenhuma run. O gate é a paridade (o G-PAR do gabarito na S2) e o byte a byte da chave desligada na S1. Nenhuma semente nova: os gabaritos
usam as sementes 101 e 202 dos gabaritos do produto.

## 5. Entrega

- Testes: `python -m pytest tests/ -q`; em `web/app`: `npm test`, `npm run tipos`, `npm run e2e` (a S2 e a S3 tocam a web).
- Registro: seção própria no fim do arquivo do mês, `docs/registro/AAAA-MM.md` (rodada de saúde, etapa 2). **Não edite o índice
  `docs/REGISTRO_DESVIOS.md`:** ele é gerado (`python tools/gerar_indice_desvios.py`) por quem faz o merge. Um conflito nele se resolve
  rodando o gerador, nunca à mão (`docs/TAREFA_V3_INDICE_DESVIOS.md`). O resumo da etapa vai no corpo do PR e numa seção no fim do documento da
  frente (o `RESULTADO_V3_*.md` da run ou o `TAREFA_V3_*.md` da etapa), nunca no `CLAUDE.md` (rodada de saúde, etapa 1).
- PR contra a `main` com resumo e números (cada um com o artefato). Aviso ao coordenador. Merge só pelo Matheus.
- O corpo do PR segue `.github/pull_request_template.md`; o CI (`tools/verificar_relato.py`) confere os campos e a evidência da categoria.

## 6. Fora desta tarefa

- O paladar das frutas no jogo (os gostos e a preferência por pet do J5): espera o órgão do paladar no TS (a etapa 5 do paladar).
- O efeito no humor por fruta, a fruta que faz mal e o dono que julga (N4, K4, J5): são da pesquisa.
- Um som ou um sinal do gesto para o pet (o pet que corre quando ouve a árvore): fica para a direção C (a ilha que cresce).
- Plantar árvores, árvores que crescem, mais tipos de fruta e árvores na mata: direção C.
- O dono sintético que sacode, na pesquisa.
- A calibração dos números do galho e da queda natural: a rodada de equilíbrio do fim.

## 7. Critérios de aceitação

Desta etapa (S0):

- Este arquivo na `main` e as perguntas AS-1 a AS-10 respondidas pelo Matheus (no PR ou na sessão), com as respostas copiadas para a seção 8.

Das etapas seguintes (para quem as fizer):

- **S1:** os testes do Python passam; com a `ConfigSacudir` desligada, os gabaritos `mundo`, `mvp_produto`, `decisao_na_comida` e
  `levar_pet` reexportados saem iguais byte a byte (`git diff --exit-code` neles); um teste mostra que as quedas naturais de uma semente
  são as mesmas com e sem sacudidas; outro, que `reproduzir_mundo` refaz `sacudidas` e o estado final; o `arvore_sacode_python.json` está
  commitado com os casos de borda da seção 3.5.
- **S2:** `test/arvore_sacode.test.ts` confere o gabarito bit a bit; um pet v19 rejeita o `sacudirArvore`; um save v20 com `sa` refaz igual
  no replay; os testes de hoje passam sem mudança.
- **S3:** o e2e toca a árvore, sacode e vê a fruta no chão no ponto do motor; as capturas estão na pasta da prancha.

## 8. Precisa do Matheus

**AS-11 APROVADA (Matheus, 2026-11-08), a opção 1:** "Fruta como ração". Repassada pela mesma sessão.

**AS-1 a AS-10 APROVADAS (Matheus, 2026-11-08), todas pela recomendação:** "segue com a recomendação ali". A frase chegou repassada pela
sessão da frente UX_TELA_PET (a coordenadora desta tarefa). O que ficou decidido: sacudir não é cuidado; cai uma fruta por sacudida; o
limite é pelo galho (3 frutas, uma reposta a cada 4 h, até 9 por árvore por dia); a queda natural continua; a fruta cai a até 2 células
do tronco; por enquanto as frutas são iguais para o pet; o mundo novo é o `CMU_ILHA`; só os ovos v20, com tudo na v20; e tocar na árvore
abre o cartão com o botão Sacudir. Os números novos (`galho_max`, `recarga_galho_min`) continuam PROPOSTOS, SEM FONTE: a aprovação é do
modelo, e os valores vão para o equilíbrio do fim.

Cada pergunta traz a recomendação (que o plano da seção 3 já usa), a alternativa e o custo de errar.

**AS-1 (APROVADA, recomendação). Sacudir a árvore é cuidado?**
- **Recomendação:** não. É um gesto sobre o mundo, como levar o pet e deixar a bola: não conta como contato nem cuidado, não chega ao
  cérebro e não atende o chamado de fome do bebê. O pet se alimenta porque escolhe comer a fruta.
- **Alternativa:** conta como o `alimentar` (contato, cuidado, o chamado atendido), como deixar a ração.
- **Custo de errar:** se for cuidado, o dono pode cuidar só sacudindo árvores e a ração perde a função. Se não for e o Matheus quisesse que
  fosse, trocar depois é uma versão de pet nova (o evento muda de efeito).

**AS-2 (APROVADA, recomendação). Quantas frutas caem por sacudida?**
- **Recomendação:** uma, se houver fruta no galho e lugar no chão. Sem fruta, a árvore só balança.
- **Alternativa:** de 1 a 3, como na queda natural (`frutas_por_queda_min` e `_max`).
- **Custo de errar:** baixo. É um número da `ConfigSacudir` atrás da chave. Uma por toque é o gesto mais legível: cada toque, uma fruta.

**AS-3 (APROVADA, recomendação). Como fica o limite por dia?**
- **Recomendação:** pelo galho. Cada árvore guarda até `galho_max` = 3 frutas e repõe uma a cada `recarga_galho_min` = 240 ticks (4 h de
  jogo): até 9 frutas por árvore por dia, sacudindo sem parar. O cartão mostra quantas há no galho. PROPOSTOS, SEM FONTE.
- **Alternativa:** um limite fixo por dia de jogo (por exemplo, 2 sacudidas com fruta por árvore entre 0 h e 24 h), sem galho.
- **Custo de errar:** o galho dá ao dono o que ver na árvore (as frutas na copa) e um ritmo; o limite fixo é mais simples, mas o dono não
  sabe por que a árvore parou de dar. Os números vão ao equilíbrio do fim, então errar o valor custa pouco; errar o modelo custa a S1 de
  novo.

**AS-4 (APROVADA, recomendação). A queda natural das árvores continua no jogo?**
- **Recomendação:** sim, como no Python (de 1 a 3 frutas cerca de uma vez por dia por árvore, com a recarga de 12 h), independente do
  galho. A ilha tem fruta mesmo sem o dono, e o pet que explora a acha.
- **Alternativa:** desligada no produto (`mult_queda` = 0): só cai fruta quando o dono sacode.
- **Custo de errar:** com a queda natural, o pet acha comida sozinho e sente menos fome entre as rações; isso mexe no equilíbrio da fome,
  que fica para o fim. Sem ela, a árvore é só um botão do dono. Trocar depois é uma versão de pet nova.

**AS-5 (APROVADA, recomendação). Onde a fruta cai?**
- **Recomendação:** num ponto sorteado a até 2 células do tronco (`raio_queda_celulas`), como a natural, com uma rng própria
  (`arvore-sacode`) que não toca nenhuma outra.
- **Alternativa:** sempre no pé da árvore, num ponto fixo, sem sorteio.
- **Custo de errar:** baixo. O ponto fixo empilha as frutas no mesmo lugar e fica estranho na vista; o sorteio custa dois números por
  fruta, gravados no gabarito.

**AS-6 (APROVADA, recomendação). As três frutas são diferentes para o pet no jogo?**
- **Recomendação:** não, por enquanto. Todas dão 0,15 de fome e nenhum efeito no humor; só a cor muda. O paladar (os gostos e a preferência
  de cada pet) entra quando o órgão do paladar existir no TS.
- **Alternativa:** um efeito de humor por fruta (`efeitoFrutas`) já nesta versão.
- **Custo de errar:** com efeito no humor sem paladar, a fruta "boa" seria a mesma para todo pet, o contrário do J5 (cada pet tem a sua).
  Esperar custa só que as frutas pareçam iguais por um tempo.

**AS-7 (APROVADA, recomendação). As árvores entram num mundo novo ou no `CMU_MVP`?**
- **Recomendação:** num mundo novo, `CMU_ILHA` = o `CMU_MVP` com as três árvores do jardim do layout padrão (J1, J2 e J3, uma de cada fruta).
- **Alternativa:** mudar o `CMU_MVP`.
- **Custo de errar:** mudar o `CMU_MVP` quebra o replay de todo pet v12 a v19 salvo, porque a vida gravada é com o mundo sem árvores. É o
  pior caso. Quais e quantas árvores é barato de mudar até a S1.

**AS-8 (APROVADA, recomendação). O pet de hoje ganha as árvores?**
- **Recomendação:** não. Só os pets v20 (um ovo novo) nascem na ilha com árvores. Os v19 seguem sem árvores e abrem como hoje.
- **Alternativa:** migrar o pet v19 para v20 a partir de um tick, com o mundo trocando no meio da vida.
- **Custo de errar:** a migração é uma mecânica nova de motor (trocar o mundo no meio da vida com replay), com risco na paridade; fica para
  uma tarefa própria se o Matheus quiser.

**AS-9 (APROVADA, recomendação). A versão nova é a v20, com tudo junto?**
- **Recomendação:** sim. A v20 = a v19 com o `CMU_ILHA` e o sacudir, numa versão só, na S2. A S1 é só o Python, sem versão.
- **Alternativa:** duas versões (v20 com o mundo da ilha, v21 com o sacudir).
- **Custo de errar:** baixo. Duas versões só servem se o mundo da ilha for ao jogo antes do gesto, e sem o gesto a árvore só dá fruta pela
  queda natural.

**AS-10 (APROVADA, recomendação). A vista: o toque abre o cartão ou já sacode?**
- **Recomendação:** abre o cartão, com o número de frutas no galho e o botão Sacudir, como a tigela na prancha A. A S3 começa por uma prancha
  curta (o cartão e três quadros do balanço) para o ok antes do código.
- **Alternativa:** o toque na árvore já sacode, sem cartão; o número fica nas frutas da copa.
- **Custo de errar:** o toque direto é mais rápido, mas sacode sem querer quando o dono só queria ver. Sem a prancha antes, a S3 pode
  precisar de uma segunda rodada de vista.

**AS-11 (APROVADA, opção 1). O cérebro A quebra ao comer uma fruta do mundo. O que fazer?** (achada em 2026-11-08, no começo da S1)
- **Opção 1 (a recomendada, aprovada):** uma subchave do A no produto, "a fruta do mundo como comida": a fruta entra no A como a ração,
  sem a E2 do humor e sem a sub-decisão. Desligada, o A sai byte a byte. Python e TS juntos (S1 e S2).
- **Opção 2:** portar a E2 (o `fruta_comida` e o sinal do humor) para o A do TS e ligar as chaves do mundo do A.
- **Opção 3:** só os pets com o modular têm árvores.
- **Opção 4:** parar a frente.
- **Custo de errar:** a opção 1 mexe no código do A (a linha de base), mas atrás de uma chave, e para o A as frutas ficam iguais, o que já
  é a AS-6. A opção 2 muda o A do jogo e custa mais. A 3 deixa o A trocável sem a ilha com frutas.

## 9. S1 entregue (2026-11-08, branch `v3-arvore-sacode-s1`)

O Python, atrás de duas chaves desligadas. Os desvios D-AS-S1-1 a 8 estão em `docs/registro/2026-11.md`, na seção "ARVORE_SACODE, S1".

- **O gabarito de hoje, num commit próprio antes da mudança:** são 30 vidas, o A do v11 com o corpo e o instinto, sementes 101 a 505,
  3 dias, no `CONFIG_MUNDO_MVP` e no MVP com J1, J2 e J3 montado com o código de hoje. Três delas quebram (a AS-11). O gerador está em
  `tests/gabarito_arvore_sacode.py`, a conferência em `tests/test_gabarito_arvore_sacode.py` e o arquivo em
  `tests/gabaritos/arvore_sacode_de_hoje.json`. Com as chaves desligadas, as 30 saem iguais, inclusive as quebras.
- **Na `digilab/config.py`:**
  - a `ConfigSacudir`, com `galho_max` = 3 e `recarga_galho_min` = 240, PROPOSTOS, SEM FONTE;
  - a `ConfigFrutaComoComida`;
  - o `LAYOUT_MUNDO_ILHA` e o `CONFIG_MUNDO_ILHA`, na planta A da ilha (PR #724). As frutíferas ficam no bosque do lar, na casa, e por
    isso o `Mundo` só as aceita com o sacudir ligado (D-AS-S1-7).
- **Na `digilab/events.py`:** o `sacudir_arvore(tick, arvore)` e o `ler_sacudir_arvore`, com o id em letras e dígitos ASCII, de 1 a 16.
- **Na `digilab/mundo.py`:**
  - o `Mundo` ganha `ligar_sacudir`, `galho_em` e `sacudir`, com o fluxo `arvore-sacode` e o registro `sacudidas`, cujos motivos são
    `caiu`, `galho_vazio`, `chao_cheio` e `parada`;
  - o `MotorMundo` ganha `cfg_sacudir`, `cfg_fruta_comida`, `sacudir_arvore` e `no_galho`, e o `estado()["sacudir"]` com a chave
    ligada;
  - o `reproduzir_mundo` refaz o evento;
  - com a fruta como comida, o laço não entrega o `fruta_comida`. Isso fica no laço, não no A (D-AS-S1-2).
- **O gabarito do G-PAR para a S2:** o gerador é `experiments/exportar_gabarito_arvore_sacode.py`, e o arquivo,
  `web/app/test/gabaritos/arvore_sacode_python.json`.
  - São duas vidas de 2 dias, sementes 202 e 505, no `CONFIG_MUNDO_ILHA`, com as chaves dos ovos v20 ligadas.
  - Cada vida tem 126 sacudidas, todas as que caem, as que acham o galho vazio e o chão cheio, as sacudidas com o pet dormindo, as
    reposições do galho e as frutas comidas.
- **Os testes:** `tests/test_arvore_sacode.py`, com 23 testes.
- **Para a S2 (TS):**
  - o porte do `Mundo.sacudir` e do `galho_em`, com o `RandomPy` no fluxo `arvore-sacode`;
  - o `CMU_ILHA` e o `ConfigSacudir` em `constantes.ts`;
  - o `[tick, "sa", { arvore }]` no registro;
  - a v20;
  - o `arvores_na_casa` no `Mundo` do TS;
  - o laço sem o `fruta_comida`, que ele já não tem: conferir que o A do TS com o corpo aceita o estímulo `comida` de uma fruta.

## 10. S2 (2026-11-11, branch `v3-arvore-sacode-s2`)

O porte do sacudir para o motor em TS, sem tela e **sem versão de pet** (D-AS-S2-1). Os desvios D-AS-S2-1 a 5 estão em
`docs/registro/2026-11.md`, na seção "ARVORE_SACODE, S2".

- **Em `web/app/motor/constantes.ts`:** o `LAYOUT_MUNDO_ILHA` e o `CMU_ILHA` (a planta A, espelho do `CONFIG_MUNDO_ILHA`), a
  `ConfigSacudir` (`CONFIG_SACUDIR`, `CONFIG_SACUDIR_LIGADA` e o `validarSacudir`), a `ConfigFrutaComoComida` e o
  `VERSOES_COM_SACUDIR`, vazio. O `VERSAO_PET` segue 23 e o `CMU_MVP` não muda.
- **Em `web/app/motor/mundo.ts`:**
  - o `eventoSacudirArvore` e o `lerSacudirArvore`, com o id em letras e dígitos ASCII, de 1 a 16, como no Python;
  - no `MundoPartilhado`: o `arvoresNaCasa` no construtor, o `ligarSacudir`, o `galhoEm`, o `sacudir`, os registros `galhos` e
    `sacudidas` e o fluxo `arvore-sacode`, `derivarSemente("arvore-sacode", semente)` no `RandomPy`, que só anda quando cai uma
    fruta (dois sorteios por fruta);
  - no `Mundo` do pet: a opção `sacudir` (só fora do grupo), o `sacudirArvore(tick, arvore)`, que atualiza o mundo até o tick antes de
    sacudir (D-AS-S1-4), e o `noGalho(tick)`;
  - o `RandomPy.estado()`, só leitura: as 624 palavras e a posição, o `getstate()[1]` do Python.
- **Em `web/app/motor/motor_corpo_mundo.ts`:** as opções `sacudir` e `frutaComoComida`, o `sacudirArvore` (com o log) e o
  `sacudirDoDono` (sem ele), o evento `sacudir_arvore` no `aplicarEvento`, o `estadoDict().sacudir` com a chave ligada e o gancho
  opcional `frutaComida` da AS-11 (D-AS-S2-2).
- **Em `web/app/motor/motor.ts` e `tipos.ts`:** o `[tick, "sa", { arvore }]` no `EventoRegistro`, o `Motor.sacudirArvore(id)` e o
  `"sa"` no `aplicarEvento`. Como nenhuma versão tem o sacudir, os dois falham alto em todo pet de hoje, antes do registro.
- **O G-PAR (`web/app/test/arvore_sacode.test.ts`):** as duas vidas do `arvore_sacode_python.json` (sementes 202 e 505) saem iguais
  bit a bit no Node: o log, o traço de cada decisão (o estado, a percepção, os candidatos, o ocorrido e o corpo), o resumo do mundo
  inteiro (`quedas`, `sacudidas`, `galhos`, `consumos`, `comidas`, `sumidas`), o estado do fluxo `arvore-sacode`, o corpo e o estado no
  fim, os próximos sorteios dos cinco fluxos, o galho no fim e as sacudidas com o pet dormindo. O arquivo tem 14 testes, e a suíte do
  `web/app` passa com 1 341 testes em 135 arquivos.
- **Para a S3 e para o Matheus:** em que mundo as árvores vão para os ovos novos (a v23 está na ilha com água, `mvp_agua`, e o
  `CMU_ILHA` não tem água) e qual versão de pet liga o sacudir. Quando isso for decidido, basta pôr a versão em `VERSOES_COM_SACUDIR` e
  dar a ela o mundo e as chaves do gabarito; o teste do Motor passa a conferir o replay de um save com `sa`.
