# TAREFA V3 — COOPERACAO (2026-11-11)

Coordenador: o Gerente da V3 (Claude Code, Opus 5.5). Worker: um por etapa, a definir. Worktree e branch: `v3-cooperacao` (esta etapa,
CO0); cada etapa de código terá a sua, `v3-cooperacao-co<n>`. Status: **ABERTA**, só o papel. As decisões CO-1 a CO-9 da seção 8
foram DECIDIDAS em 2026-11-11, pela recomendação.

Categoria: arquitetura. Origem: o Matheus, em 2026-11-11, a partir do levantamento "moral, mitologia e felicidade", feito no vault
(`20 Temas/Síntese — moral, mitologia e felicidade.md`, fora do repositório).

## 0. O que já está decidido

**O que o Matheus decidiu em 2026-11-11:**

- **D-MM-1 a D-MM-17:** "Aprovo as 17", pela recomendação da Síntese. As que esta tarefa usa:
  - **D-MM-1:** a moral é híbrida. A felicidade do corpo escolhe entre as ações permitidas, e os deveres entram como restrição. Os deveres
    crescem até a lei kantiana no Mega.
  - **D-MM-2:** a moral só entra **depois** da luta. Nenhuma escolha do pet dentro da luta (a LP-3 continua).
  - **D-MM-8:** a pontuação pró-social é o **efeito medido pelo motor**. A intenção passa a pesar mais com a idade. Não há número na tela
    nem nota do dono. Há meia-vida, e a novidade cai pela metade na repetição.
  - **D-MM-10:** nenhuma correção mexe nos stats da luta nem no corpo.
  - **D-MM-14:** a felicidade é lexicográfica: o piso de cada pet, depois a média, nunca a soma.
  - **D-MM-17:** a pergunta do dono não reabre.
- **D-MM-18:** "Aprovo". A disposição para a hybris é inata, e a história de lutas do par a desperta. Ela fica para uma etapa
  própria.
- **"faça a cooperação no web primeiro":** a cooperação aparece **primeiro jogável no web**.
  - Ela vem contra a recomendação de fazer o Python antes.
  - A leitura do coordenador (desvio D-CO0-1): a paridade continua. A mecânica é escrita no Python e no TS no mesmo PR, e o gabarito sai
    do Python. A run de pesquisa na bancada vem depois.
- **"Um segundo pet meu":** os outros pets são **um segundo pet do mesmo dono, na mesma ilha**.
- **"o chamado se dobra e o segundo pet não é opcional":** o segundo pet é obrigatório, e cada pet tem os próprios chamados.
- **"Dois ovos no início":** os dois pets nascem juntos.

**O que já existe e serve (FATO, `main` em `95b90b2e`):**

- **O `Grupo` do Python** (`digilab/grupo.py`; `docs/TAREFA_V2_DOIS_PETS.md`; o desenho em `docs/futuro/dois_pets.md`, DP-1 a DP-14):
  - N pets no mesmo `Mundo`, cada um com o seu motor, a sua rng e o seu cérebro;
  - a vez sorteada no fluxo `mundo-ordem`, com Fisher-Yates por `randrange`, "para o TS repetir os mesmos números";
  - a semente do segundo pet é `derivar_semente("segundo-pet", s)`;
  - o registro do grupo, com o destino de cada evento (DP-3);
  - a percepção social, só com o que é físico: a visão e o toque;
  - a disputa (quem pega primeiro come; não há agressão, CV-3);
  - o replay que falha alto.
- **No web não existe grupo.**
  - `web/app/motor/` tem um `Motor` por pet. O mundo (`motor/mundo.ts`) recebe o estado de **um** pet.
  - O save (`src/save.ts`, `CHAVE = "digilab-web-v21-sprites"`) guarda um pet. A versão é `VERSAO_PET = 21`.
  - O `dois_pets.md` (seção 12) já punha "o grupo em TypeScript" para "quando o produto voltar".
- **A regra dos dois pets que esta tarefa herda** (`dois_pets.md`, seção 7):
  - nenhum sinal de reforço sai do outro pet;
  - nenhum parâmetro passa de um cérebro ao outro;
  - só a consequência da própria ação atualiza o valor.

## 1. Pergunta

O jogo web pode ter dois pets do mesmo dono, nascidos de dois ovos, vivendo na mesma ilha? E a cooperação entre eles pode ficar
**visível e jogável**? Ela é feita do que eles já fazem um com o outro (a disputa pela comida, a contenção, o encostar), medida pelo motor
como pontuação pró-social e reputação. Tudo com o replay e a paridade com o Python intactos.

Não é uma hipótese de pesquisa: é uma frente de produto. A pergunta de pesquisa ("a cooperação emerge e responde à reputação?") fica para
a run da bancada, com plano próprio, fora desta tarefa.

## 2. Depende de

- **Na `main` já:** o `Grupo` do Python (as etapas 2, 3 e 8 da DOIS_PETS); o mundo físico e o corpo em TS (`mundo.ts`,
  `motor_corpo_mundo.ts`); o modular como cérebro padrão (v17).
- **Antes da CO4 (o save e a tela):** o SOM_UP (#781), os Bits (o plano #762 e a MO1 #765) e as tarefas da ilha (IA1 a IA4, #766, #767,
  #771 e #777). Todas estão fora da `main` hoje e mexem nas telas da ilha, no save ou na `VERSAO_PET`.
- **As CO1 a CO3 não esperam ninguém:** só tocam o motor e os testes.
- **Arquivos disputados** (`docs/PLANO_V3.md`, seção 5): `App.tsx`, `pet.css`, `Nav.tsx` e `digilab/digibrain/`. Uma missão por vez.

## 3. Mudança mínima, por etapa

Um PR por etapa. Cada etapa de código entra atrás da `ConfigCooperacao` desligada (no Python, em `digilab/config.py`) e do espelho em
`motor/constantes.ts`. Desligada, as vidas de hoje saem byte a byte.

| etapa | o que faz | arquivos | o que NÃO muda |
|---|---|---|---|
| **CO0** (este PR) | a tarefa, só o papel | este arquivo; uma seção em `docs/registro/2026-11.md` | nada de código |
| **CO1, os gabaritos** | **em commit próprio, antes de qualquer mudança:** o gabarito das vidas de hoje (um pet, o v21) e o de vidas do `Grupo` com dois pets e um dono, a chave desligada | `experiments/exportar_grupo.py` (novo); `web/app/test/gabaritos/grupo_*.json` | o motor; o `Grupo` |
| **CO2, o grupo em TS** | o porte do `grupo.py` para `motor/grupo.ts`: o mundo partilhado, a ordem no tick, a percepção social (visão e toque), a disputa e o registro do grupo | `motor/grupo.ts` (novo); `motor/mundo.ts` (o mundo passa a ser partilhado, com o G2 de um pet só antes); `motor/index.ts`; os testes | as telas; a `VERSAO_PET`; o `engine.py`; o `grupo.py` |
| **CO3, a cooperação no motor** | Python e TS no mesmo PR: os **atos sociais derivados** e a **pontuação** (seção 3.1), mais a **reputação de cada pet vista pelo outro**. Tudo como função do log: nada é estado salvo. **Não muda a decisão de nenhum pet** | `digilab/cooperacao.py` (novo, só biblioteca padrão); `motor/cooperacao.ts` (novo); a `ConfigCooperacao`; os testes de paridade | o cérebro; o corpo; a luta |
| **CO4, os dois ovos** | uma `VERSAO_PET` nova (a próxima livre no merge). Com ela: o save com o registro do grupo; dois ovos no nascimento (semente `s` e `derivar_semente("segundo-pet", s)`); os chamados de cada um; a escolha de qual pet recebe a ação do dono | `src/save.ts`, as telas do ovo e da ilha, `motor/constantes.ts` | os pets das versões antigas, as assinaturas e os gabaritos (`web/app/CLAUDE.md`) |
| **CO5, o que se vê** | a cooperação na tela, **sem número** (D-MM-8): o pet que deixou a fruta, o que pegou, o que encostou no irmão; o gesto depois da luta (D-MM-2): o irmão que assistiu consola, comemora ou provoca | as telas da ilha e o fim da luta | o núcleo da luta (`motor/arena/`), a LP-3 |

Fica para depois desta tarefa, cada parte com a sua etapa e o seu ok: a reputação entrar na **percepção** do cérebro (CO6) e os deveres
como **escudo** por estágio (CO7). Ver CO-3.

### 3.1 Os atos e a pontuação (PROPOSTA)

**Os atos da primeira etapa.** Só atos que já acontecem no `Grupo`, lidos do replay. Não há ação nova no `AcaoPet` (CO-2).

| ato | como se reconhece no replay | sinal |
|---|---|---|
| **a disputa** (pegar a comida que o outro tinha como alvo) | o registro `disputas` do `Grupo` | **anti**, se o outro estava abaixo do piso de fome; **neutro**, se não |
| **a contenção** (deixar a única comida à vista para o outro) | o pet, com o outro à vista e a comida como candidata, não a come, e o outro a come em seguida | **pró**, pelo efeito no corpo do outro |
| **o encostar** | o contato do tipo `encostar` do `Grupo`, com o outro emburrado ou triste visto de fora (a ação que se vê) | **pró** |
| **o resto** (comer, brincar, dormir, explorar) | — | neutro |

**A pontuação** (a fórmula da nota *Moral do pet*, A3, em inteiros na escala S). Para o pet *i* e o ato *a*, com alvo *j*:

- **o valor do ato:** `valor(a) = sinal(a) · efeito(a)`, em que o `efeito` é a variação do bem-estar do corpo de *j*, medida pelo motor;
- **a novidade:** cai pela metade a cada repetição do mesmo ato com o mesmo alvo no dia;
- **o acúmulo:** `P_i` decai por meia-vida e acumula `novidade · valor`;
- **a reputação de *i* vista por *j*:** a mesma conta, só sobre os atos que *j* viu, pela visão do `Grupo`;
- **a intenção:** o `peso_int(idade)` da nota fica **zero nesta tarefa**. Ainda não há estimativa do pet registrada, e ela entra com a
  CO7.

**Os números:**

- todos PROPOSTOS, SEM FONTE: o piso de fome, a meia-vida, a janela do dia e o limiar do "triste visto de fora";
- cada um vai para a `ConfigCooperacao` com status e fonte;
- nenhum é calibrado nesta tarefa.

## 4. Experimento e gate

Não há run nesta tarefa. Os gates são de engenharia:

| gate | o que confere | etapa |
|---|---|---|
| **G-HOJE** | com a chave desligada, as vidas de hoje (um pet, v21) saem byte a byte contra o gabarito da CO1, no Python e no TS | CO1 a CO5 |
| **G-PAR-GRUPO** | o `grupo.ts` repete o `grupo.py`: a mesma ordem sorteada, as mesmas posições, os mesmos consumos, as mesmas disputas e o mesmo registro, bit a bit no Node | CO2 |
| **G-PAR-COOP** | os atos, a `P_i` e a reputação do TS iguais aos do Python, nos mesmos logs | CO3 |
| **G-REPLAY-2** | um save de dois pets refeito do registro dá a mesma assinatura, e um evento desconhecido levanta erro | CO4 |
| **G-SEM-DECISAO** | ligar a pontuação não muda nenhuma ação de nenhum pet nem o corpo deles: a moral desta tarefa só mede | CO3 |

- **O plano de análise e as sementes:** a run da bancada ("a contenção responde à reputação?") terá o seu
  `docs/PLANO_ANALISE_V3_COOPERACAO.md` e uma faixa pedida ao coordenador. Os dois ficam **fora** desta tarefa.
- **GPU:** não.

## 5. Entrega

- **Os testes:**
  - na raiz, `python -m pytest tests/test_grupo*.py tests/test_cooperacao*.py -q` em cada etapa, e a suíte inteira antes do PR;
  - em `web/app`, `npm test` e `npm run tipos`;
  - o `npm run e2e` na CO4 e na CO5, que mexem nas telas e na `VERSAO_PET`.
- **O registro:** uma seção própria no fim de `docs/registro/AAAA-MM.md`. **Não edite o índice `docs/REGISTRO_DESVIOS.md`:**
  - ele é gerado (`python tools/gerar_indice_desvios.py`) por quem faz o merge;
  - um conflito nele se resolve rodando o gerador, nunca à mão (`docs/TAREFA_V3_INDICE_DESVIOS.md`).
- **O resumo da etapa:** vai no corpo do PR e numa seção no fim deste arquivo, nunca no `CLAUDE.md`.
- **O PR:**
  - contra a `main`, com o resumo e os números, cada um com o artefato;
  - aviso ao coordenador; o merge é só pelo Matheus;
  - o corpo segue `.github/pull_request_template.md`, e o CI (`tools/verificar_relato.py`) confere os campos.

**A CO-bancada (2026-11-12):** o plano de análise de "a cooperação emerge e cresce com o `k`?" está em
`docs/PLANO_ANALISE_V3_COOPERACAO.md`, PROPOSTO (as CB-1 a CB-9 vão ao Matheus). Nenhuma vida roda antes da CO7 na `main` e da aprovação.

## 6. Fora desta tarefa

- **a reputação na percepção do cérebro e os deveres como escudo:** são as CO6 e CO7, cada uma com o ok do Matheus;
- **a hybris** (D-MM-18) e **a aura**;
- **o panteão, as lendas e o oráculo:** é a E0 da mitologia, com tarefa própria;
- **a run da bancada e o plano de análise dela;**
- **a visita entre donos** (D-MM-12, espera o MMO), **o segundo dono** (DP-7) e **a comunicação** (o degrau 2, DP-6);
- **a agressão entre pets** (CV-3) e **qualquer decisão do pet dentro da luta** (LP-3);
- **a mudança nos pets das versões antigas** (eles continuam com um pet só);
- **os sentidos do degrau 1b** (o cheiro e a audição do outro): a cooperação usa só a visão e o toque.

## 7. Critérios de aceitação

1. O G-HOJE passa no Python e no TS em todas as etapas, com o gabarito gravado no commit próprio da CO1, antes da mudança.
2. O G-PAR-GRUPO passa (CO2) nos gabaritos da CO1, bit a bit no Node.
3. O G-PAR-COOP e o G-SEM-DECISAO passam (CO3).
4. O G-REPLAY-2 passa (CO4), e um pet v21 abre igual a antes.
5. A CO5 tem as capturas a 390 e 1280 px nas duas peles, aprovadas pelo Matheus, e o e2e verde.
6. Cada número novo está na `ConfigCooperacao` (e no espelho TS, conferido por `constantes.test.mjs`) com PROPOSTO e SEM FONTE.

## 8. Precisa do Matheus

**As CO-1 a CO-9 foram DECIDIDAS pelo Matheus em 2026-11-11 ("Aprovo as 9"), pela recomendação.** Os números continuam PROPOSTOS.

| n.º | decisão | recomendação | custo de errar |
|---|---|---|---|
| **CO-1** | a ordem das etapas | o motor primeiro (CO1 a CO3, sem tela nem versão nova), depois o save e a tela (CO4 e CO5), quando o SOM_UP, os Bits e a ilha estiverem na `main` | baixo: o motor não colide com ninguém; a tela antes disso colide com quatro PRs abertos |
| **CO-2** | os atos da primeira etapa | **só os que já acontecem** (a disputa, a contenção, o encostar), sem ação nova no `AcaoPet`. "Dividir" de verdade (levar comida ao outro) é ação nova e fica para depois | médio: uma ação nova muda a decisão do cérebro, pede gabarito e mexe no `digibrain` disputado |
| **CO-3** | a cooperação muda o que os pets fazem já nesta tarefa? | **não.** A CO3 só mede e mostra (o G-SEM-DECISAO). A reputação entra na percepção (CO6) e os deveres como escudo (CO7) em etapas próprias. A regra dos dois pets vale: nenhum reforço sai do outro | alto, se entrar junto: não se sabe se a mudança veio da medida ou da decisão, e o replay muda em duas frentes ao mesmo tempo |
| **CO-4** | os saves de hoje (um pet) | **continuam como estão.** Os dois ovos valem para os jogos novos, na versão nova. Um pet antigo não ganha irmão (`web/app/CLAUDE.md`: as versões antigas não mudam) | alto, se migrar: um segundo pet inventado no meio de um log antigo quebra o replay dele |
| **CO-5** | a luta | **cada pet luta sozinho**, como hoje (a POC é um contra um). O irmão assiste, e o gesto dele depois do nocaute é o ato social da luta (D-MM-2) | alto, se for dois contra um: reabre a LP e a rodada de equilíbrio |
| **CO-6** | a ação do dono | **cada ação vai a um pet escolhido** (o pet em foco na tela). Deixar comida e bola no mundo serve aos dois, como no `Grupo` (o destino `mundo`) | médio: uma ação para os dois ao mesmo tempo não tem par no registro do grupo (DP-3) |
| **CO-7** | o cérebro do segundo pet | **o mesmo do primeiro** (o modular), cada um com o seu estado; nenhum parâmetro passa de um ao outro | baixo |
| **CO-8** | a herança entre os dois | **sem regra nova:** o jogo já cruza dois adultos do dono (`src/heranca.ts`); os irmãos podem ser pais, como hoje | baixo; se o Matheus quiser proibir, é uma linha na tela da herança |
| **CO-9** | o piso de fome que separa a disputa "anti" da "neutra" | o `fome_moderada` do instinto (o mesmo limiar do chamado de fome, `motor/constantes.ts`, `chamadoPelaFome`), para não criar número novo | baixo: é PROPOSTO e se ajusta na rodada de equilíbrio |

## CO1, os gabaritos (2026-11-11, Gerente da V3, Claude Code, Opus 5.5, branch `v3-cooperacao-co1`)

Gravados com o código da `main` (`9f72f060`) antes de qualquer mudança da frente, num commit só deles.

- **O Python:**
  - `experiments/exportar_gabarito_grupo.py` grava `web/app/test/gabaritos/grupo_python.json.gz` (613 724 bytes).
  - **A vez sorteada (DP-2):** 8 casos (4 sementes, listas de 2 e de 3 ids, 40 sorteios cada).
  - **As vidas:** 5 vidas de 3 dias de dois pets do mesmo dono sintético, com os sentidos do degrau 1b desligados (sementes 101 a 505).
    Cada vida guarda o registro do grupo, as vezes sorteadas, os contatos, as disputas e o resumo inteiro do grupo, com o sha256.
  - **O teste:** `tests/test_cooperacao_gabarito.py` refaz o gabarito e o compara byte a byte.
  - **O lado de um pet** continua sendo o `tests/gabaritos/dois_pets_vidas_de_hoje.json`, conferido pelo `tests/test_grupo.py`.
- **O TS:**
  - `web/app/test/coop_etapa0.test.ts` grava, com `GRAVAR_COOP=1`, o `web/app/test/gabaritos/coop_etapa0_ts.json`.
  - **As vidas:** três vidas do pet v21 com um dono de roteiro fixo (sementes 101, 202 e 303; 126, 177 e 83 eventos). Cada uma guarda o
    log, a assinatura a cada 25 eventos de um replay incremental e no fim, e a impressão do mundo.
  - **Os arquivos pinados:** o sha256 de `grupo_python.json.gz`, `mundo_python.json` e `mvp_mundo_python.json`.
- **O achado (D-CO1-1):** as disputas são raras. Há 2 em 5 vidas, mesmo com o comedouro comum em três delas (`n_disputas` no gabarito).

## CO2a, o traço do grupo (2026-11-11, Gerente da V3, Claude Code, Opus 5.5, branch `v3-cooperacao-co2`)

A CO2 foi dividida em três PRs, porque o porte é maior do que a seção 3 previa. Os motivos estão em D-CO2a-1, no registro de 2026-11.

- **As três etapas:**
  - **CO2a:** o traço do grupo no Python;
  - **CO2b:** separar o `Mundo` do TS em mundo partilhado e parte de cada pet;
  - **CO2c:** o `motor/grupo.ts` com o G-PAR-GRUPO.
- **O pedido do Matheus nesta etapa (2026-11-11):** "cada pet vai ter um mundo separado, porém primeiro quero simular o mundo junto deles,
  competindo pela comida".
  - A CO2 é o mundo junto, partilhado pelos dois.
  - O mundo de cada pet fica para uma etapa futura, sem desenho.
- **O que esta etapa entrega:**
  - **O exportador:** `experiments/exportar_gabarito_grupo_traco.py` grava `web/app/test/gabaritos/grupo_traco_python.json.gz`
    (190 530 bytes).
  - **O conteúdo:** as cinco vidas da CO1, com o traço por decisão de cada pet. O traço traz a percepção do mundo e a percepção social
    antes, a ação, os candidatos, o ocorrido, o estado depois e o `_tick_social`. É o que o TS precisa para rejogar o grupo sem o engine,
    a política e o dono do Python.
  - **O teste:** `tests/test_cooperacao_traco.py` refaz o traço byte a byte. Ele também confere que o motor que grava não muda a vida: o
    sha256 do resumo de cada vida é o mesmo da CO1.

## CO2b, o mundo partilhado no TS (2026-11-11, Claude Code, Opus 5.5, branch `v3-cooperacao-co2b`)

O `web/app/motor/mundo.ts` foi separado como o `digilab/mundo.py`, sem mudar o jogo de hoje.

- **O `MundoPartilhado` (novo):** o `Mundo` do Python. Guarda as árvores, as comidas, a bola, os fluxos do mundo e os registros do mundo.
  - A atualização é idempotente por tick e falha alto num tick para trás.
  - A percepção (`perceber(x, y, tick, pendente, ve)`), as maduras perto, retirar a comida, rolar a bola e o que o dono deixa.
- **O `Mundo` (o de hoje):** passa a ser a parte de um pet (o `MotorMundo` do Python), com a mesma interface.
  - Sem `partilhado`, ele é dono do próprio `MundoPartilhado`, com a semente do pet: a vida de hoje.
  - Com `partilhado` e `entrada` (um início de dia), ele vive no mundo do grupo, com o relógio dele.
- **O G2 de um pet só:** `web/app/test/mundo_partilhado.test.ts` rejoga as 4 vidas do `mundo_python.json` com o pet sobre um mundo dado e
  com o pet dono do próprio, e as duas dão a mesma vida. O G-HOJE (`coop_etapa0.test.ts`) e as paridades do mundo continuam passando.
- **Os desvios:** D-CO2b-1 a D-CO2b-4, no registro de 2026-11.

## CO2c, o grupo em TS (2026-11-11, Claude Code, Opus 5.5, branch `v3-cooperacao-co2c`)

O `web/app/motor/grupo.ts` é o porte do `digilab/grupo.py`, sem tela e sem versão de pet nova.

- **O `Grupo`:** dois pets no mesmo `MundoPartilhado`, no mesmo relógio.
  - **A vez no tick:** o fluxo `mundo-ordem`, com o Fisher-Yates do `random.shuffle` por `randrange`.
  - **As sementes:** o primeiro pet usa a do grupo; o segundo, `derivarSemente("segundo-pet", s)`.
  - **A percepção social:** só a visão e o toque, do que é físico.
  - **O toque e a disputa,** no fim de cada tick com decisão.
  - **O registro do grupo:** o JSONL do Python, byte a byte, e a projeção de cada pet. O `reproduzirGrupo` rejoga e falha alto.
- **O pet do grupo** (`PetDoGrupo`) é o engine, o corpo e o cérebro, de fora: o grupo não decide nada.
- **O G-PAR-GRUPO passa** (`web/app/test/grupo.test.ts`, bit a bit no Node):
  - os 8 casos da vez sorteada da CO1;
  - as 5 vidas de dois pets da CO1, rejogadas do registro com o traço da CO2a. Em cada decisão: a percepção, a social, os candidatos, o
    ocorrido, o estado e o `_tick_social`. No fim: as vezes, os contatos, as disputas, o mundo, o físico e o social de cada pet e a
    projeção. Só o estado das rngs fica fora (D-CO2c-5).
- **Fora:** o degrau 1b (D-CO2c-3) e a ligação com o `Motor` do jogo, que é a CO4.
- **Os desvios:** D-CO2c-1 a D-CO2c-5, no registro de 2026-11.

## CO3, os atos e a pontuação (2026-11-11, Claude Code, Opus 5.5, branch `v3-cooperacao-co3`)

A medida da cooperação, no Python (`digilab/cooperacao.py`) e no TS (`web/app/motor/cooperacao.ts`), atrás da `ConfigCooperacao`
desligada (o espelho é o `CCOOP` do `motor/constantes.ts`). Ela só mede: nenhuma ação e nenhum corpo muda.

- **Os atos:**
  - **a disputa:** do registro do Grupo. É "anti" se a fome do perdedor estava abaixo do piso, e neutra se não;
  - **a contenção:** a única comida madura à vista, deixada para o outro, que a come antes da próxima decisão de quem deixou;
  - **o encostar:** o contato de quem seguiu o outro, com o outro emburrado. Vale 0 (D-CO3-3).
- **A pontuação** de cada pet e a **reputação** dele vista pelo outro:
  - em inteiros na escala S;
  - a novidade cai pela metade no dia;
  - a meia-vida é de um dia;
  - a intenção pesa zero.
- **Os gates:**
  - **G-SEM-DECISAO:** no Python, as 7 vidas do gabarito com a medida ligada têm o mesmo sha256 do resumo que com ela desligada (as 5 da
    CO1 contra o gabarito da CO1). No TS, o traço inteiro de cada vida sai igual com a medida ligada, e o resumo sem a chave é o da
    medida desligada.
  - **G-PAR-COOP:** os atos, a pontuação e a reputação do TS são iguais aos do Python nas 7 vidas e nas chamadas sintéticas
    (`web/app/test/cooperacao.test.ts`, contra `cooperacao_python.json.gz` de `experiments/exportar_gabarito_cooperacao.py`).
- **O que as vidas mostram** (o gabarito; nenhuma run):
  - há de 1 a 6 contenções por vida de 3 dias, 2 disputas neutras e 1 encostar;
  - nenhuma disputa é "anti", então o sinal −1 só é conferido nas chamadas sintéticas.
- **Os desvios:** D-CO3-1 a D-CO3-8, no registro de 2026-11.

## CO4a, a água dentro do grupo (2026-11-11, Claude Code, Opus 5.5, branch `v3-cooperacao-co4a`)

A CO4 virou quatro PRs (D-CO4-1):
- **CO4a:** a água no grupo;
- **CO4b:** o `Motor` do jogo dentro do `Grupo`, um tick por vez, como o `_um_tick` do Python;
- **CO4c:** o save e os dois ovos, com a `VERSAO_PET` 24;
- **CO4d:** as telas.

Esta parte deixa os dois pets viverem na ilha com água, onde o jogo nasce:

- **No grupo, o controlador sozinho do contrato vale** (`digilab/mundo.py`, `MotorMundo`; `web/app/motor/mundo.ts`, `Mundo`). O cone e as
  paredes seguem de um pet só.
- **O gabarito:** `experiments/exportar_gabarito_grupo_agua.py` grava `web/app/test/gabaritos/grupo_agua_python.json.gz`, três vidas de dois
  pets no `mvp_agua`.
- **Os testes:**
  - `tests/test_cooperacao_agua.py` refaz o gabarito byte a byte, rejoga o registro e confere que nenhum pet fica na água;
  - `web/app/test/grupo_agua.test.ts` é o G-PAR-GRUPO nesse mundo, decisão a decisão, com o registro do contrato.
- **Os desvios:** D-CO4-1, D-CO4a-1 e D-CO4a-2, no registro de 2026-11.

## CO4b, o Motor do jogo dentro do Grupo (2026-11-11, Claude Code, Opus 5.5, branch `v3-cooperacao-co4b`)

- **O `GrupoDoJogo`** (`web/app/motor/grupo_jogo.ts`): dois `Motor`s inteiros (o corpo, o cérebro, os chamados, a evolução) no mesmo mundo.
  - **O tempo:** anda pelo `Grupo`, um tick por vez. Os que decidem andam na vez sorteada, depois os outros, e no fim vêm o toque e a
    disputa.
  - **O registro:** é um só, `[tick, tipo, valor, pet]`. O `reproduzir` rejoga e falha alto.
- **O Grupo** (`motor/grupo.ts`) aceita o `Motor` como membro (`entrarMotor`), o relógio que começa no nascimento e a semente do segundo
  pet nos 32 bits do jogo.
- **O `Motor`** (`motor/motor.ts`) e o laço (`motor/motor_corpo_mundo.ts`, `motor/motor_corpo.ts`):
  - recebem a parte do mundo do grupo;
  - ganham o passo de um tick;
  - o pet do grupo não anda sozinho.
  - Sem o grupo, nada muda.
- **O teste:** `web/app/test/grupo_jogo.test.ts`.
  - Dois dias de dois pets v23 na ilha com água, com um dono de roteiro.
  - O mundo é um só: um pet come a ração que o dono deixou pelo outro.
  - A vez sorteada, a percepção do outro e o toque.
  - O G-REPLAY-2 no motor: a mesma assinatura, o registro de cada pet como projeção, e o replay recusa o evento desconhecido, o pet de
    fora e o tick errado.
- **Os desvios:** D-CO4b-1 a D-CO4b-5, no registro de 2026-11.

## CO4c, o save e os dois ovos (2026-11-11, Claude Code, Opus 5.5, branch `v3-cooperacao-co4c`)

- **A v24** (`motor/constantes.ts`): a v23 que nasce no grupo. O pet v24 só existe no grupo. O `VERSAO_PET` (o ovo de um pet só) segue 23.
- **Os dois ovos** (`src/jornada.ts`, `chocarDoisOvos`): o primeiro é do brasão escolhido, e o segundo é surpresa ("Um brasão, o outro
  surpresa"). Ficam atrás da chave `DOIS_OVOS_LIGADO`, desligada até a CO4d.
- **O save do grupo** (`src/save.ts`): `{semente, log, versao, grupo: true, foco}`, na mesma chave. Abrir é refazer o registro do grupo.
- **O jogo** (`src/jogo.ts`):
  - o `Jogo` ganha o grupo e o pet em foco (`trocarGrupo`, `focar`);
  - o `mudarMotor` passa pelo grupo;
  - o `avancar` do pet em foco anda os dois.
- **O teste** (`web/app/test/dois_ovos.test.ts`):
  - os dois ovos;
  - o G-REPLAY-2 no save (a mesma assinatura e o mesmo foco ao abrir);
  - o save malformado como erro;
  - o jogo com os dois pets: o relógio, a ação no pet em foco, a troca do foco e o grupo gravado;
  - o pet de um pet só igual.
- **Os desvios:** D-CO4c-1 a D-CO4c-5, no registro de 2026-11.

## CO4d, as telas dos dois pets (2026-11-11, Claude Code, Opus 5.5, branch `v3-cooperacao-co4d`)

Os dois ovos ficam jogáveis: a chave `DOIS_OVOS_LIGADO` ligou.

- **Na ilha** (`src/telas/pet/ilha/vista.ts`, `papel.ts`): os dois pets aparecem. O pet em foco segue com a vista de hoje, e o irmão tem o
  próprio seguidor e papel. Trocar o foco desliza a câmera.
- **No topo** (`src/componentes/Topo.tsx`): o retrato do irmão troca o foco, com o ponto rosa quando ele chama.
- **O relógio** (`src/tempo.ts`) freia pelo chamado de qualquer um.
- **As medalhas:** os dois conhecem as do Tamer.
- **O save nas telas:**
  - a espera leva e traz o par inteiro;
  - Ajustes e o Registro conferem e exportam o grupo;
  - a herança, o importar do par e o Salão ficam para depois, com aviso (D-CO4d-5).
- **Os testes:**
  - `web/app/test/dois_pets_telas.test.ts`;
  - `web/app/e2e/dois_pets.spec.ts`, a 390 e 1280 px: o brasão choca os dois, o irmão fica no topo, o foco troca e volta ao reabrir, e a
    ação vai ao pet em foco.
- **Os desvios:** D-CO4d-1 a D-CO4d-7, no registro de 2026-11.

## CO5, a cooperação na tela (2026-11-11, Claude Code, Opus 5.5, branch `v3-cooperacao-co5`)

A cooperação aparece sem número (D-MM-8), em `web/app/src/telas/pet/AtosDoIrmao.tsx`.

- **Na ilha:** o ícone do ato, ao lado da cabeça do pet que o fez. O coração para deixar a comida e para encostar; a comida riscada para
  pegar a de quem tinha fome.
- **Em Últimas ações:** a linha do ato, do ponto de vista do pet em foco.
- **No fim da luta do pet em foco:** o gesto do irmão (consola, comemora ou provoca), pelo resultado e pela reputação (`gestoDepoisDaLuta`,
  `motor/grupo_jogo.ts`).
- **A medida da CO3 ligou no jogo,** e só mede (o G-SEM-DECISAO no jogo, `web/app/test/coop_tela.test.ts`).
- **As capturas,** a 390 e 1280 px, no Militar e no Sci-fi, ficam em `D:\Trab\digilab\capturas_coop_co5\`, fora do git: o ato na ilha e,
  no celular, a linha.
  - **Aprovadas pelo Matheus** em 2026-11-11 (D-CO5-7).
  - **A captura do gesto da luta espera um conserto da `main`:** a luta de todo pet v23 a v26 não termina no palco (D-CO5-5).
- **Os desvios:** D-CO5-1 a D-CO5-6, no registro de 2026-11.

## CO6a, o gabarito das vidas de hoje (2026-11-12, Claude Code, Opus 5.5, branch `v3-cooperacao-co6`)

Gravado com o código da `main` (`bf381ef9`) antes de qualquer mudança da CO6, num commit só dele (CO6-6).

- **O exportador:** `experiments/exportar_gabarito_co6.py` grava `tests/gabaritos/co6_vidas_de_hoje.json.gz`.
- **As vidas:** três vidas de 3 dias do `Grupo` com a cooperação ligada e o DigiBrain modular nos dois pets (D-CO6a-1), com as decisões, o
  sha256 do `estado_interno()` de cada cérebro, o dos logs e o do resumo do grupo.
- **O teste:** `tests/test_cooperacao_co6.py` refaz as vidas e as compara com o gabarito (o G2 da CO6).
- **Os desvios:** D-CO6a-1 e D-CO6a-2, no registro de 2026-11.
