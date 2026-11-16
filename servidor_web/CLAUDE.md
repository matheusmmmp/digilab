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
python tools/gerar_catalogo_fala_web.py   # (da raiz) regera o catálogo e o gabarito
```
