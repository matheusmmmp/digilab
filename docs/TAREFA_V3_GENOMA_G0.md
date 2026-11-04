# TAREFA V3 — GENOMA_G0 (2026-11-04)

Coordenador: Gerente da V3 (Claude Code). Worker: Claude Code, Opus 5.5, worktree `v3-genoma-g0`. Worktree e branch: `v3-genoma-g0`. Status: ENTREGUE (só o papel); as G0-1 a G0-7 DECIDIDAS em 2026-11-04 pela recomendação; o código (E0 a E3) liberado.

Categoria: arquitetura. Origem: Matheus, 2026-11-04: o Matheus seguiu a recomendação de 2026-11-03: depois da B3, começar a genética pelo G0, só infraestrutura e antes do Gate I.

**Esta etapa é só papel.** Nenhum código, nenhuma vida e nenhum número de jogo. O código vem depois, etapa a etapa (seção 3.2), quando o
Matheus decidir as G0-1 a G0-7 (seção 8). Os nomes de arquivo, de evento e de campo abaixo são PROPOSTOS.

## 1. Pergunta

**O genoma de um pet pode entrar no log e no replay, atrás de uma chave desligada, de modo que o genoma vazio dê a vida de hoje byte a
byte?** É o passo G0 de `docs/futuro/ecossistema_genetico.md` (seção 6), a infraestrutura da fase 3 (genoma e gerações) do
`docs/PLANO_V2_PESQUISA.md`. O G0 **não mede nada**: não tem hipótese, run, plano de análise nem gate estatístico. Ele só prepara o
objeto que o G1 (a h² de cada seção) vai medir.

O que já vale e não se reabre aqui:
- **EG-1 a EG-8** (DECIDIDAS em 2026-10-14): um registro único com seções, cada uma com a sua rng e a sua chave (EG-1); codificação direta
  (EG-3); o aprendido nunca entra no genoma (EG-5); a espécie fixa por linhagem na pesquisa (EG-8).
- **GI-5** (2026-10-21): o genoma muda valores; a topologia do cérebro fica fora.
- **A nota de 2026-10-24** (topo do `ecossistema_genetico.md`) e a `docs/ARQUITETURA_DIGIBRAIN_MODULAR.md`, seção 9: a seção `prior`
  passa a ler-se como **os parâmetros inatos de cada módulo do modular** (os ganhos do M-AFETO, as constantes de tempo do M-ESTADO, as
  taxas do M-PLAST, os traços do M-PERS e o prior do M-IMPULSO), não mais presa ao cérebro A.
- **GI-4:** o G1 e o G2 só medem sobre um pet que passou no Gate I; **o G0 pode vir antes**, porque é só infraestrutura.

**Sem alegação de novidade.** Herdar o ponto de partida do aprendizado sem herdar o aprendido é o efeito Baldwin computacional (Hinton e
Nowlan 1987, sem DOI; Whitley, Gordon e Mathias 1994, `10.1007/3-540-58484-6_245`; Fernando et al. 2018, `10.1145/3205651.3205763`).
Um genoma que especifica rede e bioquímica de uma criatura de jogo já existiu no Creatures (Grand e Cliff 1998,
`10.1023/a:1010042522104`). Todas estão verificadas (`docs/referencias/referencias_verificadas.csv`). O formato do evento, as seções e a
regra do genoma vazio deste documento são SEM FONTE.

## 2. Depende de

- **Na `main`:** nada além do que já está (`d7ec740`, com a B3, #553). O G0 não depende do Gate I (GI-4) nem dos dois pets.
- **Do Matheus:** as G0-1 a G0-7 (seção 8), antes da etapa E0.
- **Arquivos compartilhados** (`docs/PLANO_V3.md`, seção 5): a etapa E2 toca `digilab/mundo.py`, que é "uma missão por vez". A E2 só
  começa quando nenhuma outra frente estiver com o `mundo.py` aberto (conferir no `PAINEL_V3.md` antes). Se a G0-1 levar o G0 à web, a E4 toca `web/app/motor/motor.ts`, que a L3 e o #525 também mexeram.

## 2.1 O que já existe (verificado no repositório em `d7ec740`)

**Não existe hoje um registro de genoma no log, nem em Python nem na web.** O que é inato está espalhado, cada pedaço sorteado da semente
na construção do motor, e o replay só o refaz porque recebe a mesma semente (e, na bancada, a mesma `EspecVida`).

| pedaço | o que é | onde | a rng (rótulo do `derivar_semente`) | no log hoje? |
|---|---|---|---|---|
| temperamento (v1) | 4 eixos do motor, `Temperamento` | `digilab/temperamento.py` (`sortear`, `rng_ovo`) | `"ovo"`, da semente do ovo | não: refeito da semente |
| espécie | o brasão | `digilab/evolucao.py`; na bancada é fixa: `"brasa"` (`experiments/bancada/nucleo.py`, as fábricas do mundo) | nenhuma na bancada (fixa) | não |
| frutas (N4) | `GenomaFrutas`: neofobia e preferência inata | `digilab/frutas.py` (`genoma_frutas`) | `"frutas-ovo"` | não; vai no resumo da vida (`nucleo.py`, `"genoma": m.genoma.para_dict()`) |
| paladar (#310) | `GenomaPaladar`: os `h_q` | `digilab/genoma_paladar.py` (`genoma_paladar`, `FLUXO = "paladar-ovo"`) | `"paladar-ovo"` | não |
| os inatos do modular | `ConfigDigibrainInatos` (tudo PROPOSTO, salvo a escala e os campos marcados DECIDIDO) | `digilab/config.py` (`CONFIG_DIGIBRAIN_INATOS`) | nenhuma: **igual em todo pet** | não |
| o M-GEN | `ParametrosInatos`: o registro único dos inatos, por módulo (`CAMPOS_POR_MODULO`: sens, afeto, impulso, arb, plast, estado, mem, pers), e confere que todo campo cai num módulo só | `digilab/digibrain/ganchos.py` | — | não; a docstring diz "o genoma futuro escreve esse registro" |
| o corpo químico | `ConfigCorpo` | `digilab/corpo.py`, `digilab/config.py` | nenhuma: igual em todo pet | não |
| a herança (v1) | o evento `origem` (tick 0, primeiro do log): os sha256 dos logs dos pais, os traços herdáveis, a semente da herança | `digilab/heranca.py` (`cruzar`, `ler_origem`, `conferir_pais`); `digilab/educacao.py` (`registrar_origem`) | `"heranca"` | **sim**, só nos filhos v1 |

**A semente do genoma na bancada:** a `EspecVida` (`experiments/bancada/vida.py`) tem `semente` e `genoma: int | None`. O temperamento e
as frutas saem de `espec.genoma` quando ele existe (`nucleo.py`); o paladar sai sempre de `espec.semente`
(`experiments/bancada/pet_que_pensa.py`, `genoma_paladar(espec.semente)`). **É um achado** (registrado no desvio): as seções de hoje não
usam todas a mesma semente. O G0 não muda isso (G0-6).

**O replay do mundo** (`digilab/mundo.py`, `reproduzir_mundo`) aceita `avanco`, `acao_usuario`, `deixar_comida`, `deixar_bola` e
`deixar_fruta`; qualquer outro evento, `origem` inclusive, levanta erro. O replay da educação (`reproduzir_educacao`) é o único que lê
`origem`.

**Na web** (`web/app/motor/`): o pet de hoje é a v15 (`VERSAO_PET = 15`, `VERSOES_PET = [13, 14, 15]`), e o pet de teste do laboratório
é a v16 (`VERSAO_PET_LAB = 16`, `motor/pet_lab.ts`), o modular no lugar do A. Os eventos do começo do registro são `"c"` (o ritmo),
`"p"` (as chaves do produto) e `"o"` (a origem v4, com a rng `hashSemente("heranca", o.s)`), cada um com a sua regra de posição
(`motor.ts`, `registrarOrigem`, `ligarProduto`). Os inatos do modular são copiados do gabarito do Python
(`web/app/motor/digibrain/constantes.ts`, `INATOS_MODULAR`, conferidos por `test/digibrain_modular_constantes.test.ts`). O paladar não
tem órgão em TS (`motor/corpo.ts`: ligado, falha alto).

**Os gabaritos de hoje** seguem o padrão `tests/gabarito_<frente>.py` + `tests/gabaritos/<frente>_vidas_de_hoje.json` (por exemplo
`gabarito_digibrain_modular.py`, `gabarito_paladar_mundo.py`, `gabarito_corpo_mundo.py`).

## 3. Mudança mínima

**O que muda (PROPOSTO, depende das G0-n):**
1. Um módulo novo, `digilab/genoma.py`: o registro `Genoma` com uma seção por sistema, o genoma vazio, a leitura e a escrita do evento,
   e a conferência. Só biblioteca padrão; só inteiros, textos e listas no evento.
2. Uma chave nova, `ConfigGenoma` em `digilab/config.py` (`ligado: bool = False`, com status e fonte), e nada mais lá.
3. O replay do mundo aceita o evento `genoma` **só** com a chave ligada e **só** como primeiro evento do log (G0-4); com a chave
   desligada, o evento `genoma` continua falhando alto, como hoje.
4. A bancada passa a poder gravar o genoma vazio da vida no log, com a chave.

**O que NÃO muda:**
- `digilab/engine.py` (o sha256 `ENGINE_SHA256_V0`);
- os sorteios de hoje: as rngs `"ovo"`, `"frutas-ovo"`, `"paladar-ovo"` e `"heranca"`, seus rótulos e a ordem dos sorteios (G0-6);
- o evento `origem`, o `heranca.py` e o replay da educação (a v1 e os pets v4 do jogo);
- a `ConfigDigibrainInatos` e os valores dela; o `ParametrosInatos` continua lendo dela;
- as versões de pet existentes, no Python e na web (v13 a v16);
- nenhuma vida de pesquisa já gravada; nenhuma faixa de sementes.

### 3.1 O desenho proposto do registro

- **Uma seção por sistema** (EG-1), com nome fixo e ordem fixa. As seções que o G0 reconhece são as da G0-2 (recomendação:
  `temperamento`, `especie`, `frutas`, `paladar` e `inatos`).
- **Cada seção tem uma forma** (G0-3): `"hoje"` (o genoma vazio: a seção sai como sai hoje, da semente e da config) ou, se o Matheus
  aceitar, `"valores"`, com os valores que a regra de hoje produziria, conferidos no replay (falha alto se divergirem).
- **A seção `inatos`** segue os módulos do `CAMPOS_POR_MODULO` do M-GEN (`ganchos.py`): no G0 ela só pode estar na forma `"hoje"` (a
  `CONFIG_DIGIBRAIN_INATOS` de sempre). Desviar um inato de um pet é G1, não G0.
- **O aprendido nunca entra** (EG-5): nenhum campo do registro lê o estado da política, da memória ou do caráter. O teste da E1 confere
  pela lista de campos.

### 3.2 As etapas de código (cada uma um PR, na ordem; nenhuma antes das G0-n)

| etapa | o quê | arquivos | testes (todos antes do PR da etapa) |
|---|---|---|---|
| **E0 · o gabarito antes** (commit próprio, sem nenhuma mudança de código do pacote) | grava as vidas de hoje nos caminhos que o G0 vai tocar: o mundo com o corpo e o cérebro A, o mundo com o modular (o braço REL da C4) e o mundo com o paladar ligado; sementes de teste (101…505), poucos dias. Grava o sha256 do log e da trajetória (as decisões, o estado por tick e o resumo da vida) | `tests/gabarito_genoma_g0.py`, `tests/gabaritos/genoma_g0_vidas_de_hoje.json` | o gabarito se regera igual duas vezes (determinismo do próprio gabarito) |
| **E1 · o registro** | `digilab/genoma.py` e a `ConfigGenoma` (desligada) | `digilab/genoma.py`, `digilab/config.py`, `tests/test_genoma_g0.py` | ida e volta evento ↔ `Genoma` igual; seção desconhecida, seção faltando, forma desconhecida, campo a mais e valor não inteiro falham alto; o JSON do evento é canônico (`sort_keys`, ASCII) e o sha256 dele é estável; nenhum campo do registro vem do aprendido; o `ParametrosInatos` segue cobrindo todo campo dos inatos; o preflight (só biblioteca padrão, `engine.py` intacto) passa |
| **E2 · o replay** | o `reproduzir_mundo` e o motor do mundo aceitam o evento `genoma` com a chave | `digilab/mundo.py`, `tests/test_genoma_g0.py` | **byte a byte, chave desligada:** as vidas da E0 saem iguais ao gabarito, log e trajetória; **chave ligada, genoma vazio:** a trajetória sai igual ao gabarito, e o log é o de hoje com um evento a mais, o `genoma`, na frente (G0-5); **replay:** o log com o `genoma` refeito dá a mesma vida, até o último inteiro; o `genoma` fora da primeira posição falha; o `genoma` com a chave desligada falha; dois `genoma` falham; na forma `"valores"` (se a G0-3 aceitar), um valor diferente do que a semente dá falha |
| **E3 · a bancada** | a `EspecVida` passa a carregar o registro (vazio por padrão) e a bancada o grava no log com a chave; o resumo da vida leva o sha256 do genoma | `experiments/bancada/` (`vida.py`, `nucleo.py`), `tests/test_genoma_g0.py` | os gabaritos de bancada de hoje (`tests/gabaritos/bancada_*_vidas_de_hoje.json`) saem byte a byte com a chave desligada; com a chave ligada e o genoma vazio, a trajetória é a mesma; o modo acoplado (`acoplar`) preserva o evento `genoma` |
| **E4 · a web** (só se a G0-1 levar o G0 ao jogo) | o evento `"g"` no registro, só numa versão de pet nova (PROPOSTO: v17), com a mesma regra de posição dos `"c"`, `"p"` e `"o"` | `web/app/motor/` (`motor.ts`, `tipos.ts`, `constantes.ts`), `web/app/test/` | **paridade:** o evento gerado pelo Python (um gabarito exportado) é lido pelo TS e o TS escreve o mesmo JSON; os replays das v13 a v16 seguem byte a byte; o `"g"` numa versão antiga falha alto; `npm test`, `npm run tipos`, `npm run e2e` |

## 4. Experimento e gate (se houver run)

**Não há run.** O G0 não mede nada (seção 1). Sem plano de análise, sem faixa de sementes, sem GPU. Os testes usam as sementes de teste
(101…505).

## 5. Entrega

- Testes: `python -m pytest tests/ -q`; em `web/app`: `npm test`, `npm run tipos`, `npm run e2e` (se a frente toca a web).
- Registro: seção própria no fim do arquivo do mês, `docs/registro/AAAA-MM.md`, e uma linha no fim do índice `docs/REGISTRO_DESVIOS.md`
  (rodada de saúde, etapa 2). O resumo da etapa vai no corpo do PR e numa seção no fim do documento da
  frente (o `RESULTADO_V3_*.md` da run ou o `TAREFA_V3_*.md` da etapa), nunca no `CLAUDE.md` (rodada de saúde, etapa 1).
- PR contra a `main` com resumo e números (cada um com o artefato). Aviso ao coordenador. Merge só pelo Matheus.
- O corpo do PR segue `.github/pull_request_template.md`; o CI (`tools/verificar_relato.py`) confere os campos e a evidência da categoria.
- **Esta etapa (o papel):** só este documento e o desvio. Cada etapa E0 a E4 é um PR próprio, com o resumo numa seção no fim deste
  documento.

## 6. Fora desta tarefa

- **O G1:** a variância herdável, a h² de cada seção, qualquer genoma não vazio que mude uma vida, e o sorteio de desvios dos inatos.
- **O G2 em diante:** a reprodução no `Grupo` (dois pets, um ovo), o fatorial criação × seleção, o ecossistema com donos e o projeto
  deliberado (EG-6).
- **A herança da v1:** o `origem`, o `heranca.py`, os pets v4 da web e a mistura entre o `origem` e o `genoma` (o G2 decide).
- **Os órgãos e o corpo:** a seção `corpo` (desvios da camada 2 do grafo do corpo), a fisiologia por espécie (FE-3) e os órgãos (o J10;
  a POC do #516 é só referência). Esperam fonte.
- **A topologia do cérebro** (GI-5) e a codificação indireta (EG-3).
- **Unificar a semente das seções** (o achado da seção 2.1): fica para o G1 (G0-6).
- **A tela:** nenhuma tela de genoma, nenhum editor no jogo.

## 7. Critérios de aceitação

**Desta etapa (o papel):**
- este documento existe, com as seções do modelo e as G0-1 a G0-7 em tabela, cada uma com a recomendação e o custo de errar;
- cada fato da seção 2.1 aponta um arquivo do repositório em `d7ec740`;
- o desvio está no fim de `docs/registro/2026-11.md`, com uma linha no fim de `docs/REGISTRO_DESVIOS.md`;
- nenhum arquivo fora de `docs/` mudou.

**Do G0 inteiro (as etapas de código):**
- a E0 está num commit anterior a qualquer mudança no pacote, e `tests/gabaritos/genoma_g0_vidas_de_hoje.json` existe;
- com a `ConfigGenoma` desligada, os gabaritos da E0 e os de bancada de hoje saem byte a byte (um teste confere);
- com a chave ligada e o genoma vazio, a trajetória sai igual ao gabarito e o log só ganha o evento `genoma` na frente (um teste confere);
- o replay de um log com o `genoma` dá a mesma vida, e cada forma inválida do evento falha alto (um teste por caso);
- `engine.py` intacto (o teste do `ENGINE_SHA256_V0` passa); o preflight passa;
- se a G0-1 levar à web: o teste de paridade do evento passa, e os replays das v13 a v16 seguem iguais.

## 8. Precisa do Matheus

As decisões que o worker não toma. Cada uma com a recomendação e o custo de errar. **DECIDIDAS pelo Matheus em 2026-11-04, todas pela recomendação** ("Aprovo e mescle", no chat com o Gerente da V3).

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| **G0-1** | O G0 vai só ao Python ou também ao jogo web, e com que versão de pet | **Só ao Python no G0** (E0 a E3), sem versão de pet nova. A web recebe o genoma quando ele mudar algo visível (o G1 no laboratório, ou o G2 nos ovos), numa versão própria (PROPOSTO: a v17, porque a v16 já é a do laboratório). Com o genoma vazio, a web ganharia um evento sem efeito nenhum | **Web já:** uma versão de pet (v17) para nenhuma mudança visível, mais um evento no `motor.ts` (o arquivo que a L3 e o #525 mexeram) e um teste de paridade a manter. **Só Python, e depois a web pede outro formato:** o evento do Python muda antes de existir jogo com ele; barato, porque nenhuma vida gravada usa o evento ainda |
| **G0-2** | Quais seções o genoma vazio cobre no G0 | **As cinco que já existem como inato:** `temperamento`, `especie`, `frutas`, `paladar` e `inatos` (o modular, pelos módulos do `CAMPOS_POR_MODULO`). Ficam **fora**: `corpo` (espera a camada 2 e a fonte dos órgãos) e `plasticidade` (no modular ela já é o módulo `plast` dentro de `inatos`; uma seção separada contaria o mesmo número duas vezes). Uma seção desconhecida no evento falha alto | **Menos seções:** o G1 precisa mudar o formato do evento para acrescentar a que faltou (um passo a mais, com outro gabarito). **Mais seções (corpo):** uma seção sem regra de hoje para reproduzir, que o G0 teria de inventar; e o `plasticidade` em dobro faria a h² do G1 medir o mesmo gene duas vezes |
| **G0-3** | O que uma seção vazia carrega | **A forma `"hoje"` só, no G0:** a seção diz "como hoje" e não carrega valores; o fenótipo sai da semente e da config, como hoje. A forma `"valores"` (os valores escritos, conferidos contra a semente) fica para o G1, quando os valores puderem ser outros | **`"valores"` já:** o G0 passa a duplicar no log o que a semente já dá, e cada mudança de config de uma seção (o paladar, as frutas) quebraria logs gravados; ganha-se só a leitura do genótipo no log. **Só `"hoje"` e o G1 precisar de `"valores"`:** uma forma nova no G1, com o teste dela; barato |
| **G0-4** | Como o genoma entra no log: o evento e o formato | **Um evento novo, `genoma`, no tick 0, o primeiro do log** (antes de qualquer avanço ou ação), com `valor` = `{"versao": 1, "secoes": {<nome>: {"forma": "hoje"}, ...}}`, as seções na ordem fixa da G0-2, em JSON canônico (`sort_keys`, ASCII, o mesmo do hash do `protocol.py`). Um só por log. O resumo da vida leva o sha256 desse JSON. **Não reusar o `origem`:** ele é da herança v1 e só o replay da educação o lê | **Reusar o `origem`:** mistura a herança v1 (sha dos pais, traços em float) com o genoma, e o G2 teria de separar os dois depois, com os pets v4 do jogo dependendo do formato antigo. **Evento em qualquer posição:** o replay precisaria aplicar o genoma no meio da vida, e o genoma deixaria de ser "o que o pet é ao nascer" |
| **G0-5** | O que "byte a byte" quer dizer com a chave ligada | **Chave desligada:** tudo byte a byte, o log inclusive (é a regra do `CLAUDE.md`). **Chave ligada com o genoma vazio:** a trajetória (as decisões, o estado por tick, o resumo da vida) byte a byte; o log é o de hoje com um evento a mais na frente. Um teste confere cada um | **Exigir o log igual com a chave ligada:** impossível, porque o evento é o próprio objeto do G0. **Não conferir a trajetória com a chave ligada:** um genoma vazio que muda a vida passaria despercebido até o G1, e a h² mediria esse erro |
| **G0-6** | A rng de cada seção | **No G0, as rngs de hoje, sem mudar nada:** `temperamento` em `derivar_semente("ovo", s)`, `frutas` em `derivar_semente("frutas-ovo", s)`, `paladar` em `derivar_semente("paladar-ovo", s)`, cada uma com a semente que usa hoje (o temperamento e as frutas, a `espec.genoma` quando existe; o paladar, a `espec.semente`); `especie` e `inatos` sem rng (fixas). **Reservar** o rótulo `derivar_semente("genoma", <seção>, s)` para as seções novas do G1, sem usá-lo no G0. Unificar a semente das seções fica para o G1 | **Trocar os rótulos ou a semente já:** os sorteios mudam, o genoma vazio deixa de ser a vida de hoje e os gabaritos de bancada quebram (a regra "se o replay quebrar, pare tudo"). **Não reservar o rótulo:** o G1 escolhe um que pode colidir com um fluxo de outra frente |
| **G0-7** | Quais caminhos de replay o G0 cobre | **Só o mundo** (`reproduzir_mundo`, o caminho do pet que o Gate I e o modular usam) e a bancada que o monta. O replay da educação, o do grupo (`reproduzir_grupo`) e os da v1 continuam sem o evento; nele, o `genoma` falha alto | **Todos os replays já:** o G0 toca a educação e o grupo (o `origem` e o registro do grupo) sem que nenhum deles precise do genoma antes do G2. **Só o mundo e o G2 precisar do grupo:** o evento do grupo é um passo do G2, com o formato já pronto |

## 9. Resumo da etapa (2026-11-04, o papel)

A tarefa do G0 está escrita, sem código, sem vida e sem número de jogo. O que existe de genoma hoje está na seção 2.1, com o caminho de
cada pedaço: cinco inatos espalhados, nenhum no log, e só o `origem` da v1 como evento de nascimento. O achado da semente (o paladar usa
`espec.semente`, o temperamento e as frutas usam `espec.genoma`) foi registrado como desvio e não muda no G0. O código (E0 a E3, e a E4
se a G0-1 levar à web) espera as G0-1 a G0-7.

## 10. Resumo da E0 (2026-11-04, o gabarito das vidas de hoje)

A E0 gravou `tests/gabaritos/genoma_g0_vidas_de_hoje.json` (40 vidas, sementes 101 a 505, sha256 do log e da trajetória de cada uma) com o gerador
`tests/gabarito_genoma_g0.py`, num commit anterior a qualquer mudança no pacote. Os três caminhos: o mundo com o corpo e o cérebro A (20), o modular REL da C4 (10) e o mundo
com o paladar (10). `tests/test_gabarito_genoma_g0.py` confere que o gabarito se regera igual duas vezes e está em dia. Nenhum arquivo de `digilab/`, de
`experiments/bancada/` nem o `engine.py` mudou. Desvios em `docs/registro/2026-11.md`. A E1 (o `genoma.py`) é outra etapa.

## 11. Resumo da E1 (2026-11-04, o registro)

A E1 criou `digilab/genoma.py` (o `Genoma` com as cinco seções na forma `"hoje"`, o evento `genoma` no tick 0 em JSON canônico, o sha256 e as falhas altas), a `ConfigGenoma`
desligada (`ligado=False`, PROPOSTO, SEM FONTE) em `digilab/config.py` e `tests/test_genoma_g0.py`. Nenhum arquivo do motor, do `mundo.py`, da bancada nem o `engine.py` mudou; o `genoma.py`
não cita o `ConfigDigibrain*`. A E2 (o replay do mundo aceita o evento) e a E3 (a bancada o grava) são outras etapas. Desvios em `docs/registro/2026-11.md`.
