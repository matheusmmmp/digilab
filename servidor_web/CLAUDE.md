# CLAUDE.md — o servidor do jogo web (`servidor_web/`)

Vale junto com o `CLAUDE.md` da raiz e o `servidor/CLAUDE.md`. É a CN1 do `docs/PLANO_V3_CONTA.md` (seção 10): Node 24 + Hono em
TypeScript, por ora só local, com a `/saude` e a fala por LLM portada do `servidor/servidor_local.py`. A conta do lado do servidor é a CN2
(`src/conta/`, a parte local: sem os apps OAuth reais e sem nuvem); as telas da conta são do app, depois; o deploy e o Litestream, a CN5.
O `servidor/` continua para o jogo local e a pesquisa.

## Regras

- **O mesmo contrato do servidor Python:** `GET /api/fala/status` e `POST /api/fala`, nos mesmos caminhos e com os mesmos campos
  (`web/app/src/fala.ts`). Rota nova do jogo entra aqui só com o porte da regra que a acompanha.
- **O catálogo fechado tem uma fonte só, o Python.** `catalogo_fala.json` e `test/gabarito_fala.json` são gerados por
  `python tools/gerar_catalogo_fala_web.py` de `digilab/expressao.py` e `servidor/fala_llm.py`; não se editam à mão. Mudou a tabela ou o
  prompt no Python: regerar, e o `tests/test_catalogo_fala_web.py` (no CI) reprova se esquecer.
- **Entrada da página não é confiável:** só ação, fator e parâmetro do catálogo chegam ao prompt; o resto leva 400.
- **A chave da API** só no ambiente do servidor (`ANTHROPIC_API_KEY`), nunca na página. Sem chave, a fala cai no template.
- **Teto de gasto TOTAL** (`--limite-usd`, padrão US$ 2), no mesmo arquivo do servidor Python (`servidor/gasto_fala.json`, fora do git):
  não zera ao reiniciar, e os dois servidores somam um teto só. `DIGILAB_GASTO_FALA` troca o arquivo. Modelo sem preço na tabela não sobe.
- **Só escuta em `127.0.0.1`,** e pedido com cabeçalho de túnel ou proxy (`Cf-Ray`, `Cf-Connecting-Ip`, `X-Forwarded-For`) leva 403.
  **A exceção é a VPS (CN5, `docs/infra/DEPLOY_CN5.md`):** com `--borda cloudflare` (ou `DIGILAB_BORDA=cloudflare`), o servidor continua
  em `127.0.0.1`, mas só aceita o pedido que passou pelo Cloudflare Tunnel (com o `Cf-Ray` e o `Cf-Connecting-Ip`), e não sobe com a conta
  local. Os arquivos da VPS (systemd, Litestream, instalar, publicar, restaurar) ficam em `deploy/`; o deploy é o `.github/workflows/publicar.yml`.
  O Worker dos assets (`deploy/worker_assets/worker.ts`) confere a URL assinada da CN4 na frente do bucket privado; o teste
  `test/worker_assets.test.ts` reprova se a conta dele se separar da do `assinatura.ts`.
- **Testes sem custo:** o cliente da Anthropic nos testes é sempre o falso (`test/rotas.test.ts`); o Google e o GitHub, um `fetch` falso
  (`test/conta.test.ts`). O job `servidor-web` do CI roda `npm run tipos` e `npm test` quando o PR muda `servidor_web/`.
- **Dependências** com versão exata, só o Hono (`hono`, `@hono/node-server`), o SDK `@anthropic-ai/sdk`, e no dev o Vitest, o
  TypeScript e os tipos. O banco é o `node:sqlite` do Node 24 (sem dependência).

## A conta (CN2, `src/conta/`)

- **O banco** (`banco.ts`) é um arquivo SQLite fora do git (`servidor_web/dados/conta.sqlite`, ou `DIGILAB_BANCO`), em WAL para o Litestream
  da CN5. **A migração é versionada** pelo `PRAGMA user_version`: a lista `MIGRACOES` só cresce, nunca se edita uma que saiu; banco mais novo
  que o código não abre. As chaves estrangeiras com `ON DELETE CASCADE` fazem o "apagar a conta" levar tudo.
- **Nada do provedor além do provedor e do id** (seção 9 do plano): o login (GitHub) e o e-mail verificado (Google) só servem para conferir a
  lista de convidados, na memória. A lista por e-mail guarda só o SHA-256. O nome e o e-mail não entram em tabela, log nem "baixar os dados".
- **Os provedores ficam atrás da interface `Provedor`** (`provedores.ts`), com `state` e PKCE (S256). Sem `GOOGLE_CLIENT_ID`/`_SECRET` ou
  `GITHUB_CLIENT_ID`/`_SECRET` no ambiente, o provedor fica desligado e diz por quê (`GET /auth/provedores`). **Nenhuma chave no repositório.**
- **O provedor falso só liga no local** (a API em `http://` num loopback); fora dele, `configDoAmbiente` levanta. É o dos testes e do
  `npm run dev`, com a lista padrão `falso:ana` (a `bia` fica fora da lista).
- **A sessão** é um cookie `httpOnly`, `SameSite=Lax`, `Secure` fora do local; o banco guarda só o SHA-256 do token. **O que muda algo**
  (POST e DELETE em `/conta` e `/auth/sair`) pede o `X-CSRF-Token` (o csrf da sessão, que o `GET /conta` entrega, ou o do acesso pendente)
  e, se houver `Origin`, a do jogo ou a da API. **O CORS** abre só para a origem de `DIGILAB_URL_JOGO`, com credenciais (RC-6).
- **Só convidados adultos (CN-10):** só cria conta quem está em `DIGILAB_CONVIDADOS` ou na tabela `convidados`; "menos de 18" não guarda nada.
- **A página `/dev/conta`** (só local) percorre o fluxo pela API; não é tela do jogo.

## O envio dos logs (MMO3, `src/envio/`)

- **`POST /envios`** recebe `{pet: {semente, log, versao}, tamer: {versao, log}}` com a sessão e o `X-CSRF-Token` da conta, até 5 MiB
  (`LIMITE_ENVIO`, PROPOSTO). **A pontuação nunca vem do cliente:** campo a mais leva 400. `GET /envios` lista os envios da conta.
- **A conferência** (`conferir.ts`) refaz o pet e as lutas num passe só, pela conta da MMO1 (`refazerComLutas` de
  `web/app/src/ranking/pontos.ts`, o mesmo pet do `Motor.reproduzir`), o Tamer com o `lerTamer` de `web/app/src/tamer.ts`, e confere o marco
  10 por `marcoConfere` (MMO2). Roda num worker (`conferidor.ts`, `trabalhador.ts`), fora do laço de eventos; os testes da rota usam o
  `conferirAqui`, no processo. O
  código do jogo é importado como está: o motor e o `engine.py` não mudam. O que se importa do `web/app` não pode chegar ao React (o CI do
  servidor não instala o `node_modules` do jogo); por isso o `tamer.ts` lê a chave do `src/chave.ts`, e não do `save.ts`.
- **Recusa com o motivo, em 422:** `versao_pet_desconhecida` (fora de `VERSOES_PET`; o pet do laboratório não se envia),
  `versao_tamer_desconhecida` (só a 10 e a 11, `VERSOES_TAMER_CONFERIDAS`: atualize o jogo, MMO-14), `pet_nao_reproduz` e `tamer_nao_reproduz` (o texto do
  erro do motor), `marco_nao_confere`. Nunca pela assinatura do pet, que difere entre o Chrome e o Node no último bit (MMO0).
- **O que fica (MMO-4):** a linha de cada envio conferido (os hashes SHA-256 dos dois registros, o resultado e o motivo, o marco, os pontos,
  o tempo); os registros, só do envio aceito, até 30 dias depois do fim da semana de Brasília (`LOG_DIAS_DEPOIS_DA_SEMANA`, PROPOSTO). A
  limpeza roda em cada envio e em cada `GET /envios`. O mesmo envio de novo devolve a conferência guardada. Apagar a conta leva os envios.
- **A luta ranqueada (MMO4, `sementes.ts`):** `POST /sementes` `{pet: {semente, versao}, indice, hash, rival, mapa}` entrega a semente (HMAC do
  segredo da semana com a conta e o número da luta; o segredo nasce no banco, um por semana, fora do git e fora da cascata da conta). A
  semente pedida conta como luta. Travas: o nível (`DIGILAB_MARCO_RANQUEADA`, o 10 conferido por padrão, o 7 no beta), `LUTAS_POR_DIA` por
  conta por dia de Brasília (429), e a ordem (409). O envio confere o hash do registro até o `indice` de cada semente (`hash_nao_confere`)
  e conta as lutas pela conta da MMO1. O hash do jogo é o `hashAte` de `web/app/src/ranking/pedido.ts`.
- **O rival e o mapa vão no pedido** (D-CONTA-116, a migração 5): a escolha é de antes da semente, e a luta do `indice` com outro rival
  ou outro mapa não conta (fica não enviada). A semente sem rival guardado é de antes da regra.
- **O ranking da semana (MMO5, `semanas.ts`):** cada semente guarda o que a conferência achou dela (a migração 4), e **a primeira
  conferência vale**. As tabelas saem daí, uma por estágio, com os pontos refeitos pelo `pontuar` da MMO1. A semana congela
  `FOLGA_DO_FECHAMENTO_MS` depois do fim (PROPOSTA): a pendente vira não enviada, as tabelas vão para `tabelas_semana` e o segredo é
  publicado. O fechamento roda na primeira chamada depois da hora. As tabelas pedem a sessão; o segredo publicado, não.
- **O desafio do dia (MMO6, `src/desafio/desafio.ts`):** a Fábrica do dia, uma tentativa por conta por dia de Brasília. `POST
  /desafio/tentativa` `{v}` entrega a semente do dia (HMAC do segredo do dia, a mesma para todos: os alugados e os rivais) e já gasta a
  tentativa (409 `tentativa_usada`); `POST /desafio/lutas` `{dia, k, escolha, trocas}` entrega a semente da luta k, da conta (HMAC com a
  conta e o k), e guarda a escolha e as trocas prometidas; `POST /desafio/envios` `{dia, registro}` refaz a tentativa pelo motor
  (`TentativaFabrica.doDia`, a conta pura de `web/app/src/ranking/desafio.ts`), no processo. O segredo do dia nasce no banco, um por dia, e
  é publicado quando o dia congela (a mesma folga da semana); a tabela congela em `tabelas_dia`, com o selo do Top do dia (MMO-11). A
  trava do nível é a da luta ranqueada. Apagar a conta leva a tentativa, as sementes, os envios e as linhas da tabela.
- **As recompensas e o mural (MMO7, `src/premios/premios.ts`):** o ranking paga prestígio, não Bits (MMO-12). Os recordes da Torre, da
  Fábrica e do Salão vêm só do que a conferência do envio aceito refaz (a migração 7; o Salão junta as lutas vistas no replay de cada pet);
  o título da semana, o selo e o enfeite da temporada saem das tabelas congeladas da semana e do dia; o Respeito conferido soma só o título
  e o selo (o resto é da MMO8). `GET /premios` e `GET /mural` pedem a sessão.
- **As duas pontuações e o reset (MMO8, `src/premios/rankings.ts`):** a conferência diz o Digimon (os pontos da vida), os feitos do Tamer que
  o replay do pet mostra (a medalha e a Liga) e o reset no registro final do pet (o registro do Tamer na versão 11; `reset_nao_confere`).
  O envio aceito grava o máximo histórico dos Digimon, os resets e os feitos (a migração 8). O Respeito conferido soma os feitos, os resets
  (só com 200 pontos do Digimon conferidos) e os títulos e selos da MMO7. `GET /digimons` e `GET /tamers` pedem a sessão.
- **A vida dos testes** é o gabarito `test/gabaritos/vida_101.json`, gravado por `node scripts/gerar_vida_teste.ts` (precisa do
  `node_modules` do `web/app`, porque o roteiro da MMO0 nasce o ovo pelo `src/produto.ts`).

## A proteção (CN4, `src/protecao/`)

- **O `robots.txt`:** o do jogo (`web/app/public/robots.txt`) é gerado da lista `ROBOS_DE_IA` de `robots.ts` por
  `node scripts/gerar_robots.ts`, e o teste reprova se divergir; o da API (`GET /robots.txt`) recusa tudo.
- **As URLs assinadas dos assets** (`assinatura.ts`): o formato do token da Cloudflare (`?verify=<hora>-<mac>`, o HMAC-SHA256 do caminho
  mais a hora), para a borda conferir sem o servidor. `POST /assets/assinar` com a sessão ou o cookie do visitante (`POST /assets/visitante`,
  pelo Turnstile); no local, `GET /assets/*` serve `DIGILAB_DIR_ASSETS` depois de conferir. Sem `DIGILAB_SEGREDO_ASSETS`, desligadas (503).
- **O Turnstile** (`turnstile.ts`): na criação da conta e no visitante. Fora do local, sem `TURNSTILE_SECRET_KEY`/`TURNSTILE_SITE_KEY` o
  servidor não sobe, a não ser com `DIGILAB_TURNSTILE=0`. **Nos testes, só as chaves de teste oficiais com o fetch falso** (`siteverifyDeTeste`).
- **A cota da fala** (`cota.ts`, a migração 10): `DIGILAB_COTA_FALA_DIA` falas pela LLM por conta por dia de Brasília (30, PROPOSTO); só a
  chamada que vai à LLM conta. Fora do local, a fala sem a sessão é só o template (`DIGILAB_FALA_SO_COM_CONTA`).
- **A borda** (o WAF, o limite por IP, o cache, o R2) é configuração da Cloudflare, não código: o checklist está em
  `docs/PLANO_V3_CONTA_BORDA.md`, para a CN5.

## Comandos

```bash
cd servidor_web && npm install
npm run dev                         # http://127.0.0.1:8766 (provedor auto: Claude se houver chave, senão só template)
npm run dev -- --porta 8765         # na porta do servidor Python: o npm run dev do web/app fala por aqui (proxy /api)
npm run dev -- --provedor nenhum    # só template
npm run dev -- --sem-conta          # sem as rotas da conta (a CN1)
# o fluxo da conta com o provedor falso: http://127.0.0.1:8766/dev/conta
npm test                            # Vitest: rotas com o cliente falso e a paridade com o Python
npm run tipos                       # tsc --noEmit
node scripts/gerar_robots.ts        # regrava o web/app/public/robots.txt da lista dos robôs de IA (CN4)
node scripts/gerar_vida_teste.ts    # regrava a vida dos testes do envio (com o node_modules do web/app)
node scripts/medir_conferencia.ts   # o tempo da conferência de 13 vidas -> medicoes/mmo3_conferencia.json
python tools/gerar_catalogo_fala_web.py   # (da raiz) regera o catálogo e o gabarito
```
