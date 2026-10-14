# TAREFA V2 — RODADA DE SAÚDE: o backup, o CLAUDE.md enxuto, o registro por mês, a bancada em módulos, os hooks e o painel (2026-10-13)

**Equipe:**
- **coordenador:** Gerente;
- **workers:** A, B, C e D, com os donos de cada etapa na seção 3.

Worktree e branch de cada etapa: `v2-saude-<etapa>`.

**Status: EM CURSO desde 2026-10-13.** A **etapa 0 (o backup)** está feita e mergeada (#297), com a tag `pre-saude` na
`main` `8ae3ff7` e as cópias em `docs/historico/` (`docs/historico/LEIA.md`). Respostas do Matheus (2026-10-13): SA-1 aprovada, SA-2 = um
`CLAUDE.md` por pasta, G-PROVA com as 8 perguntas sem troca, e ok para a etapa 1. A **etapa 1 (o CLAUDE.md enxuto)** está mergeada (#300,
`main` `086296f`). A **etapa 2 (o registro por mês)** está mergeada (#307,
`main` `7f28e59`), com o `merge=union` ligado. A **etapa 3 (a bancada em módulos)** está no PR dela, esperando o checklist; o resumo
está na seção 9.
Cada etapa é um PR próprio, e o merge é do Matheus. As decisões que sobram (SA-1 a SA-8) estão na seção 6.

## 1. Por que agora

Os números são de hoje, na `main` `3f69e80`:

| arquivo | linhas | bytes | seções | como medi |
|---|---|---|---|---|
| `CLAUDE.md` | 4.042 | 402.702 | 130 seções `## ` | `wc -l -c`; `grep -c "^## "` |
| `docs/REGISTRO_DESVIOS.md` | 4.863 | 463.731 | 206 seções `## ` | idem |
| `experiments/bancada_v2.py` | 3.293 | 220.060 | 81 classes e funções de topo; a classe `Bancada` sozinha tem ~1.100 linhas (913 a 2030) | `grep -n "^class \|^def "` |

**O que isso custa:**
- **O CLAUDE.md é carregado em toda sessão.** A documentação do Claude Code recomenda menos de 200 linhas por arquivo
  (<https://code.claude.com/docs/en/memory>, seção do tamanho). Com arquivos longos, o modelo segue pior as instruções, e as regras
  importantes se perdem no meio (<https://code.claude.com/docs/en/best-practices>, "Write an effective CLAUDE.md"). Hoje o arquivo tem
  ~20 vezes isso, e a maior parte é histórico de resultados, não instrução.
- **Os conflitos de merge caem nos dois arquivos que todo worker acrescenta no fim.** Nos últimos 200 merges da `main`, 44 tiveram
  conflito. O `REGISTRO_DESVIOS.md` aparece em 43 deles e o `CLAUDE.md` em 30.
  - O comando: `git log -200 --format=%B | grep -A3 "Conflicts:"`, contando as linhas de cada arquivo.
- **A bancada é um arquivo só.** 99 arquivos de `tests/` e `experiments/` a importam, e toda frente mexe nela. Cada PR da bancada toca o
  mesmo arquivo de 3.293 linhas.

## 2. As regras da rodada

1. **Nada se apaga.** Todo texto e todo código só **move** ou **divide**, e deixa um ponteiro no lugar de onde saiu.
2. **Nenhuma vida muda.** Antes e depois de cada etapa, a suíte inteira passa sem mudar nenhum teste, e os gabaritos saem byte a byte. O
   `engine.py` não muda (o sha256 do `protocol.py`).
3. **Uma etapa por PR,** com o relato no corpo. O merge é do Matheus.
4. **O checklist da etapa (seção 5) é respondido pelo Matheus antes da etapa seguinte.**
5. **O backup (etapa 0) vem antes de qualquer outra.**

## 3. As etapas e os donos

| etapa | dono | entrega | gate |
|---|---|---|---|
| **0. backup** | coordenador | a tag e as cópias integrais | **G-BACKUP** |
| **1. o CLAUDE.md enxuto** | C | o CLAUDE.md da raiz com menos de 200 linhas, o resto movido | **G-NADA-PERDIDO**, **G-PROVA** |
| **2. o registro por mês** | C | o `REGISTRO_DESVIOS.md` dividido, com o índice | **G-CONCAT** |
| **3. a bancada em módulos** | D | o pacote `experiments/bancada/`, com o `bancada_v2.py` como fachada | **G-SUITE**, **G-FUMACAS**, **G-NOMES** |
| **4. os hooks** | A | a proposta dos hooks, com os scripts e os testes, desligada até o sim do Matheus | **G-HOOKS** |
| **5. o painel** | coordenador | o `docs/PAINEL_V2.md` atualizado no fim de cada rodada | — |

**A ordem:** 0 → 1 → 2 → 3 → 4. A etapa 5 começa já (a primeira versão vai neste PR) e segue em toda rodada.

### Etapa 0: o backup

- **A tag:** `pre-saude`, anotada, no commit da `main` em que a rodada começa, e enviada ao GitHub (`git tag -a pre-saude -m ...` e `git push
  origin pre-saude`). As tags que já existem (`v1-final`, `v1-antes-fala-livre`) seguem o mesmo uso.
- **As cópias integrais, em `docs/historico/`:**
  - `CLAUDE_pre_saude.md`, do `CLAUDE.md`;
  - `REGISTRO_DESVIOS_pre_saude.md`, do `docs/REGISTRO_DESVIOS.md`;
  - `bancada_v2_pre_saude.py.txt`, do `experiments/bancada_v2.py`.
- **Por que esses nomes** (SA-1):
  - **a cópia não pode se chamar `CLAUDE.md`.** Um `CLAUDE.md` num subdiretório é carregado sob demanda quando o Claude lê arquivos ali
    (<https://code.claude.com/docs/en/memory>, "How CLAUDE.md files load"). A cópia antiga viraria instrução de novo;
  - **a cópia da bancada não pode ser um `.py`** que algo importe ou colete. Com o `.txt`, nenhum teste, preflight ou linter a lê.
- **O índice:** `docs/historico/LEIA.md`, com, para cada cópia, a origem, o commit, o sha256 e a data. A regra "nada se apaga" fica escrita
  lá.
- **G-BACKUP:**
  - a tag existe no `origin` e aponta para o commit declarado;
  - o sha256 de cada cópia é o do arquivo no commit da tag;
  - o `git show pre-saude:<arquivo>` dá o mesmo conteúdo.

### Etapa 1: o CLAUDE.md enxuto

**O critério de cada linha** é a pergunta da documentação, *"Would removing this cause Claude to make mistakes?"*
(<https://code.claude.com/docs/en/best-practices>). Em português: **"se tirar, o Claude erra?"** Se não, a linha sai do arquivo da raiz e vai
para outro lugar.

**O que fica na raiz** (o alvo é menos de 200 linhas):
- o que é o projeto, em poucas linhas, e que **não é o mestrado**;
- as regras não negociáveis (escopo, falhar alto, determinismo e o modo livre gravado, as rngs separadas, as métricas num lugar só,
  nenhum número sem artefato, parâmetros no `config.py`, o `engine.py` congelado, português sem acentos nos identificadores, só biblioteca
  padrão no `digilab/`);
- o trabalho em paralelo (as worktrees, a pasta `v2` só de referência, um PR por etapa, o merge do Matheus);
- os comandos que o Claude não adivinha;
- a regra dos assets da Bandai (o repositório privado);
- **onde está o quê:** um mapa de ponteiros para o painel, o roadmap, as tarefas, os planos, os resultados e o registro.

**Para onde vai o resto:**

| hoje no CLAUDE.md | vai para | por quê |
|---|---|---|
| as ~120 seções de resultado ("V2, X — ... GATES PASSAM", "Combate V2.1 ...") | o `RESULTADO_*` ou o `TAREFA_*` de cada frente, que já existem; uma seção sem documento próprio vai inteira para `docs/historico/claude/<frente>.md` | é histórico. O Claude não erra sem ele na sessão; ele lê o arquivo quando a tarefa toca a frente |
| o estado de cada marco | `docs/PAINEL_V2.md` e a seção 8 do `docs/ROADMAP_V2.md` | muda toda rodada; a documentação manda tirar do CLAUDE.md o que muda com frequência |
| as regras que só valem numa parte do repositório (o jogo web, a fala por LLM, o servidor) | um `CLAUDE.md` no diretório (`web/app/CLAUDE.md`, `servidor/CLAUDE.md`) ou uma regra com `paths:` em `.claude/rules/` (SA-2) | carregam só quando o Claude trabalha ali (<https://code.claude.com/docs/en/large-codebases>, "Layer CLAUDE.md files by directory") |
| a tabela "Mapa do repositório" linha a linha | um `docs/MAPA_REPOSITORIO.md`, com ponteiro na raiz | a documentação manda tirar a descrição arquivo a arquivo |

**O que não resolve:** dividir em `@imports`. O arquivo importado também carrega no começo da sessão, então o custo de contexto não cai
(<https://code.claude.com/docs/en/memory>, "Import additional files").

**G-NADA-PERDIDO:**
- um script (`tools/conferir_saude.py`, fora do `digilab/`) parte cada seção `## ` da cópia `pre_saude` em parágrafos e acha cada parágrafo,
  igual, em algum arquivo de destino. Uma exceção só entra no mapa com o motivo ("duplicado de X, linha N");
- o mapa "para onde foi" fica em `docs/historico/LEIA.md`.

**G-PROVA:**
- uma sessão nova, só com o CLAUDE.md novo, responde a 8 perguntas, escritas antes da etapa, sobre o que um worker precisa saber. Exemplos:
  - posso mudar o `engine.py`?
  - onde ponho um parâmetro novo?
  - que faixa de sementes está livre?
  - como nomeio a worktree?
  - quem faz o merge?
  - um teste de replay quebrou: o que faço?
  - posso salvar o estado do pet num arquivo para retomar a vida depois? (a pergunta 7, trocada em 2026-10-13: a original, sobre o
    sprite da Bandai, saiu junto com a parte dos assets do CLAUDE.md, pedido do Matheus)
  - onde escrevo o desvio desta etapa?
- a mesma sessão com o CLAUDE.md antigo dá a referência;
- passa se o novo acerta tudo o que o antigo acerta.

### Etapa 2: o registro por mês

- **A divisão:**
  - cada seção `## AAAA-MM-DD — ...` vai, inteira e na ordem, para `docs/registro/AAAA-MM.md`, pelo mês da data (SA-3, decidida em
    2026-10-13: por mês);
  - o que vier antes da primeira seção datada fica no começo do arquivo do mês dessa seção.
- **O `docs/REGISTRO_DESVIOS.md` continua existindo, como índice:** uma linha por seção, com o título e o arquivo. Os 9 textos de código e
  os artefatos que citam o `docs/REGISTRO_DESVIOS.md` (por exemplo `experiments/run_bateria_v21.py`) continuam achando o caminho.
- **A regra nova para os workers:** cada um acrescenta a própria seção no fim do **arquivo do mês corrente**, e uma linha no índice. O
  CLAUDE.md e o modelo de tarefa passam a dizer isso.
- **G-CONCAT:** a concatenação das partes, na ordem do índice, dá o arquivo `pre_saude` byte a byte, sem o cabeçalho do índice. O sha256 vai
  no PR.

### Etapa 3: a bancada em módulos

- **O pacote** `experiments/bancada/`, um módulo por assunto, com os cortes que o arquivo já marca nos comentários:
  - `faixas.py`: as faixas, as queimadas, os prefixos, `unidades_derivadas`;
  - `mundos.py`: as condições, os mundos, `MotorFrutasMundo`, `CalendarioFrutas`;
  - `bracos.py`: `Braco`, `BRACOS`, os filtros, a montagem, a `PoliticaDoBraco`;
  - `vida.py`: `EspecVida`, `VidaBancada`, as contagens, `resumo_motor`;
  - `regras_mundo.py`: as regras e os informantes do mundo, `simular_vida_mundo`, `simular_vida_fisico`, o `_Registro`;
  - `medidas.py`: as medidas e as tabelas;
  - `config.py`: `validar_config`, o teto, `bancada_da_config`;
  - `grupo.py`: a bancada do grupo;
  - `passo0.py`: o passo 0 do corpo;
  - `rodar.py`: `rodar`, `meta`, `main`.
- **A classe `Bancada`** (~1.100 linhas) fica inteira num módulo na primeira passada. Parti-la em mixins é uma segunda passada, só com o
  SA-4.
- **O `experiments/bancada_v2.py` vira fachada:** reexporta todo nome público de antes. `from experiments.bancada_v2 import X` continua
  valendo nos 99 arquivos, e nenhum teste muda. A linha de comando (`python experiments/bancada_v2.py ...`) também.
- **Só mover:** nenhuma linha de lógica muda. O PR mostra, por função, que o corpo movido é igual ao de antes (pela AST, com o nome do
  módulo de origem e o de destino).
- **G-SUITE:** a suíte inteira passa, com a mesma contagem de testes.
- **G-FUMACAS:** cada fumaça de `experiments/configs/` roda antes e depois e dá o mesmo `medidas.json` (sha256).
- **G-NOMES:** o conjunto de nomes públicos do `bancada_v2` é o mesmo antes e depois.

### Etapa 4: os hooks

**Por que hooks.** Uma instrução no CLAUDE.md é conselho; um hook roda sempre e decide sozinho
(<https://code.claude.com/docs/en/best-practices>, "Set up hooks"; <https://code.claude.com/docs/en/memory>: para bloquear uma ação, a
documentação manda usar um `PreToolUse`).

**Os três propostos.** Os scripts são em Python, só com a biblioteca padrão, para não depender do `jq` dos exemplos nem do shell do Windows:

| hook | evento e matcher | o que faz | o detalhe |
|---|---|---|---|
| **H1, o `engine.py`** | `PreToolUse`, `Edit\|Write` | nega a edição de `digilab/engine.py`: sai com o código 2 e o motivo no stderr | o `Edit\|Write` não vê um arquivo mudado por comando de shell (<https://code.claude.com/docs/en/hooks-guide>, a nota do matcher). Por isso entra também um H1b no `Stop`, que confere o sha256 do `engine.py` contra o `ENGINE_SHA256_V0`. O teste do sha continua sendo o gate de verdade |
| **H2, testes antes de encerrar** | `Stop` | com mudança em `digilab/`, `experiments/` ou `tests/` (`git status --porcelain`), roda um conjunto rápido: o sha do engine, os testes dos arquivos mudados e os gabaritos tocados | a suíte inteira leva ~36 min (`docs/RESULTADO_V2_VALIDACAO_MUNDO.md`, seção 8), longa demais para cada fim de turno. Ela continua no PR. O `Stop` tem limite de bloqueios seguidos (<https://code.claude.com/docs/en/best-practices>, "Give Claude a way to verify its work"); o script não bloqueia de novo pelo mesmo motivo |
| **H3, merge só com autorização** | `PreToolUse`, `Bash\|PowerShell` | para `gh pr merge` e para `git push` na `main`, devolve a decisão **"ask"**: o Matheus aprova na hora | o merge da `origin/main` **num branch de worker** (o que os workers fazem para resolver conflito) não é afetado |

- **Onde ficam:** `.claude/settings.json` (o do projeto, no git) e os scripts em `.claude/hooks/`. Na entrega, a seção `hooks` vai num
  arquivo à parte (`docs/propostas/hooks_settings.json`), e **só o Matheus a liga** (SA-5). Uma config persistente é dele.
- **G-HOOKS:** `tests/test_hooks.py` dá a cada script a entrada do evento (o JSON no stdin, com os campos da documentação) e confere o código
  de saída e o texto:
  - o H1 nega `digilab/engine.py` e deixa passar os outros arquivos;
  - o H2 roda só com mudança e não bloqueia duas vezes;
  - o H3 pergunta no merge e no push na `main`, e não no merge num branch.
  - Depois do sim, o Matheus faz uma conferência ao vivo de cada um.

### Etapa 5: o painel e o protocolo

- **`docs/PAINEL_V2.md`:** uma página, com os marcos J1 a J10, as runs com resultado em uma linha cada, as decisões abertas e os riscos. A
  primeira versão vai neste PR.
- **A regra:** o coordenador o atualiza no fim de cada rodada, e cada linha cita o PR e o documento de onde veio. O painel não tem número
  novo: só o que já está num resultado.
- **O checklist** de cada etapa está na seção 5.

## 4. Fronteiras

- **Não muda:** `digilab/`, o motor, os cérebros, as medidas, os gabaritos, os artefatos e a web.
- **O CLAUDE.md da raiz só muda na etapa 1,** e só pelo critério e pelo mapa dela.
- **Nenhuma etapa reabre decisão de pesquisa,** nem reescreve o que um resultado diz. Ela só move o texto.
- **A memória automática do Claude** (`MEMORY.md` da sessão) fica fora: é por máquina, não do repositório.

## 5. O protocolo do Matheus: o checklist de cada etapa

O Matheus responde antes da etapa seguinte começar. Uma resposta "não" para a etapa e volta ao dono.

**Depois da etapa 0 (o backup):**
1. A tag `pre-saude` aparece no GitHub, no commit certo?
2. As três cópias em `docs/historico/` abrem e têm o tamanho do original?
3. Os nomes sem `CLAUDE.md` e com o `.txt` estão bons para você?

**Depois da etapa 1 (o CLAUDE.md):**
1. Você leu o CLAUDE.md novo inteiro? Ele tem menos de 200 linhas?
2. Tem alguma coisa que você sempre precisa repetir ao Claude e que não está lá?
3. Tem alguma linha lá que nunca muda o que o Claude faz?
4. O mapa "para onde foi" acha três seções que você lembra de cabeça?
5. A prova das 8 perguntas passou? Quer trocar alguma pergunta antes da próxima rodada?

**Depois da etapa 2 (o registro):**
1. O índice acha o desvio de uma run que você lembra?
2. Está claro em que arquivo o próximo worker escreve?
3. A divisão por mês serve para você?

**Depois da etapa 3 (a bancada):**
1. A suíte passou com a mesma contagem e as fumaças com o mesmo sha256?
2. Os módulos têm nomes que você acharia sem procurar?
3. Quer a segunda passada, que parte a classe `Bancada` (SA-4)?

**Depois da etapa 4 (os hooks):**
1. Liga o H1 (o `engine.py`)? Sim ou não.
2. Liga o H2 (testes no fim do turno)? O tempo dele é aceitável na sua máquina?
3. Liga o H3? No merge, prefere "perguntar" (a proposta) ou "negar sempre"?
4. A conferência ao vivo de cada hook funcionou?

**A cada rodada (o painel):**
1. O painel diz em um minuto onde a V2 está?
2. Alguma decisão aberta que não está lá?
3. Algum risco que mudou?

## 6. Decisões do Matheus

**Decididas pelo Matheus em 2026-10-13:** SA-1 (os nomes das cópias, como recomendado), SA-2 (um `CLAUDE.md` por pasta) e SA-3 (o registro **por mês**, não pela
recomendação). **Abertas: SA-4 a SA-8.**

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| SA-1 | Os nomes das cópias do backup | **`CLAUDE_pre_saude.md`, `REGISTRO_DESVIOS_pre_saude.md` e `bancada_v2_pre_saude.py.txt`** | uma cópia chamada `CLAUDE.md` num subdiretório volta a ser instrução; um `.py` pode ser importado ou coletado |
| SA-2 | Onde vão as regras de uma parte do repositório | **`CLAUDE.md` por diretório** (`web/app/`, `servidor/`), que fica junto do código | `.claude/rules/` com `paths:` junta tudo num lugar, mas afasta a regra do código que ela rege; vale se as regras forem espalhadas |
| SA-3 | Como dividir o registro (**decidida em 2026-10-13: por mês**) | **por rodada, ou pela semana quando a seção não cita rodada** | por mês: arquivos grandes de novo; por seção: mais de 200 arquivos |
| SA-4 | Partir a classe `Bancada` | **não na primeira passada:** só mover o resto; os mixins depois, se o Matheus quiser | partir já: o PR mistura mover com reorganizar, e a prova de "só mover" fica mais difícil |
| SA-5 | Quem liga os hooks | **o Matheus, depois do G-HOOKS;** o PR traz a proposta desligada | ligar no PR: muda a configuração de todos os workers sem o sim dele |
| SA-6 | O H3 no merge | **"ask"** (o Matheus aprova na hora) | "deny" sempre: o próprio Matheus, numa sessão, teria de mexer na config para fazer um merge |
| SA-7 | O H2 no fim do turno | **o conjunto rápido**, com a suíte inteira no PR | a suíte inteira no `Stop`: ~36 min por turno |
| SA-8 | Quando a rodada começa | **depois da rodada atual,** com a tag no commit em que ela fecha | começar com runs em curso: o backup não pega o estado de uma rodada fechada, e os PRs de saúde conflitam com os das frentes |

## 7. Fontes

As páginas da documentação do Claude Code, lidas em 2026-10-13:
- <https://code.claude.com/docs/en/best-practices>: o critério de cada linha, o que entra e o que sai do CLAUDE.md, e hooks contra
  instruções;
- <https://code.claude.com/docs/en/large-codebases>: o `CLAUDE.md` por diretório e as regras com `paths:`;
- <https://code.claude.com/docs/en/memory>: o alvo de menos de 200 linhas, o carregamento sob demanda dos subdiretórios, os `@imports` que
  não reduzem o contexto, e o `PreToolUse` para bloquear;
- <https://code.claude.com/docs/en/hooks-guide>: os eventos, o código 2 que bloqueia, o matcher `Edit|Write` e o que ele não vê, a decisão
  "ask" e o exemplo de arquivo protegido.

Não é literatura de pesquisa: nada disto entra num artigo.

## 8. Etapa 2: o que foi feito (2026-10-13, worker C)

- **A divisão:** as 219 seções do `docs/REGISTRO_DESVIOS.md` da `main` `086296f` foram, inteiras e na ordem, para
  `docs/registro/2026-09.md` (o título do arquivo e as 53 seções de setembro) e `docs/registro/2026-10.md` (as 166 de outubro). Nenhum
  byte mudou: a concatenação dos dois é o arquivo antigo, sha256 `25bd1ca4fd32813b2447ff5cf862815e73e55115f6b866c9657721693583c7a4`.
- **O índice:** o `docs/REGISTRO_DESVIOS.md` continua no mesmo caminho (os textos de código que o citam seguem certos). Ele traz a regra
  de onde escrever e uma linha por seção, `- [<título>](registro/AAAA-MM.md)`, na ordem.
- **A ferramenta:** `tools/registro_por_mes.py`, com `dividir --base <commit>` (rodou uma vez) e `absorver <commit>`, que traz para o
  arquivo do mês as seções que um PR ainda escreveu no formato antigo e registra o lote. Ensaiado nos 5 PRs abertos (#201, #303, #304,
  #305, #306): os 5 absorvem sem erro e a conferência passa.
- **G-CONCAT** (`python tools/conferir_saude.py`, ao lado do G-NADA-PERDIDO):
  - a concatenação dos meses começa pelo registro do commit de base, byte a byte, e pela cópia da etapa 0;
  - o índice lista as seções dos arquivos do mês, na ordem, e não tem seção datada;
  - cada seção está no arquivo do mês da data dela, e a pasta só tem arquivos `AAAA-MM.md`;
  - as seções dos lotes são iguais às do registro do commit do lote.
- **A regra nova** está no índice, no `docs/modelos/TAREFA_V2_MODELO.md`, no `docs/V2_TRABALHO_PARALELO.md` e em duas linhas do
  `CLAUDE.md` (a regra do desvio e a tabela "Onde está o quê"), trocadas com o ok do Matheus (2026-10-13). O `CLAUDE.md` segue com 105
  linhas.
- **Testes:** `tests/test_conferir_saude.py`, 22 (12 novos).

## 9. Etapa 3: o que foi feito (2026-10-14, worker C)

- **O pacote** `experiments/bancada/`, com 12 módulos na ordem de importação: `faixas`, `mundos`, `bracos`, `vida`, `regras_mundo`,
  `medidas`, `nucleo` (a classe `Bancada`, inteira, SA-4), `config`, `rodar`, `grupo`, `passo0` e `pet_que_pensa`.
- **A fachada:** o `experiments/bancada_v2.py` ficou com a docstring e as importações de antes, iguais, e com o `if __name__`. Todo nome
  de topo do pacote é posto nela. A atribuição na fachada (o monkeypatch dos testes) troca o nome também nos módulos.
- **A ferramenta:** `tools/dividir_bancada.py`, com três comandos:
  - `analisar`, as dependências entre os módulos;
  - `dividir`, que gera o pacote do arquivo de um só;
  - `conferir --base <commit>`, a prova.
- **G-AST:** 188 nós de topo, 187 com a AST igual à de antes e 1 com a troca declarada (o sha256 da bancada no `meta`).
- **G-NOMES:** os 385 nomes do módulo de antes, importado de verdade, são os da fachada.
- **G-SUITE** e **G-FUMACAS:** os números estão no PR e no `docs/registro/2026-10.md`.
- **Testes:** `tests/test_bancada_modulos.py`, 19. Nenhum teste de antes mudou.
- **O CLAUDE.md:** duas linhas trocadas com o ok do Matheus (2026-10-14), a da faixa reservada e a da bancada.
