# CLAUDE.md — o servidor do jogo web (`servidor_web/`)

Vale junto com o `CLAUDE.md` da raiz e o `servidor/CLAUDE.md`. É a CN1 do `docs/PLANO_V3_CONTA.md` (seção 10): Node 24 + Hono em
TypeScript, por ora só local, com a `/saude` e a fala por LLM portada do `servidor/servidor_local.py`. A conta é a CN2; o deploy, a CN5.
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
- **Testes sem custo:** o cliente da Anthropic nos testes é sempre o falso (`test/rotas.test.ts`). O CI do repositório ainda não roda os
  testes daqui: rodar `npm test` antes de cada commit e colar a contagem no PR.
- **Dependências** com versão exata, só o Hono (`hono`, `@hono/node-server`), o SDK `@anthropic-ai/sdk`, e no dev o Vitest, o
  TypeScript e os tipos.

## Comandos

```bash
cd servidor_web && npm install
npm run dev                         # http://127.0.0.1:8766 (provedor auto: Claude se houver chave, senão só template)
npm run dev -- --porta 8765         # na porta do servidor Python: o npm run dev do web/app fala por aqui (proxy /api)
npm run dev -- --provedor nenhum    # só template
npm test                            # Vitest: rotas com o cliente falso e a paridade com o Python
npm run tipos                       # tsc --noEmit
python tools/gerar_catalogo_fala_web.py   # (da raiz) regera o catálogo e o gabarito
```
