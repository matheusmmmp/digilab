# A borda na Cloudflare: o checklist da CN4 para o deploy da CN5 (2026-11-20)

**Status:** PROPOSTO. É a parte "a borda na Cloudflare" da etapa **CN4** do `docs/PLANO_V3_CONTA.md` (seção 6), escrita como lista para
quem fizer o deploy da **CN5** (`docs/PLANO_V3_CONTA_HOSPEDAGEM.md`, CH-1 a CH-7). **Nada aqui foi configurado em conta real:** a conta da
Cloudflare, o domínio e as chaves são do Matheus. Os nomes dos menus e dos campos são os da documentação pública da Cloudflare lida de
memória, **NÃO CONFERIDOS** no painel; os números são **PROPOSTOS, SEM FONTE**. Confere-se tudo no dia do deploy, com o plano da conta
(o Free pela CH-6) aberto: o que o Free não tiver fica marcado e vai ao Matheus antes de pagar o Pro.

**O que o código já faz (este PR, `servidor_web/src/protecao/`):** o `robots.txt` do jogo e o da API; as URLs assinadas dos assets (o
formato do token da Cloudflare, `verify=<hora>-<mac>`); o visitante pelo Turnstile; o Turnstile na criação da conta; a cota da fala por
conta. As variáveis estão no cabeçalho de `servidor_web/src/protecao/config.ts`. A borda é o que segura **antes** do servidor.

## 1. Os nomes (os de exemplo; o domínio é da CN5)

| papel | exemplo | quem serve |
|---|---|---|
| o jogo (o build do Vite e as páginas públicas) | `digilab.exemplo` | Cloudflare Pages |
| a API (o `servidor_web`) | `api.digilab.exemplo` | a VPS (Lightsail, CH-2), atrás do proxy da Cloudflare (a nuvem laranja) |
| os assets (o atlas, os sons, os pacotes) | `assets.digilab.exemplo` | o R2, por um domínio próprio do bucket |

## 2. Antes de abrir

- [ ] **Os segredos só no ambiente da VPS** (nunca no repositório, nunca no build): `DIGILAB_SEGREDO_ASSETS` (32 caracteres ou mais,
  aleatório: `node -e "console.log(require('crypto').randomBytes(32).toString('base64url'))"`), `TURNSTILE_SECRET_KEY`,
  `TURNSTILE_SITE_KEY`, `ANTHROPIC_API_KEY`, as chaves do OAuth. O `DIGILAB_URL_ASSETS` é `https://assets.digilab.exemplo`.
- [ ] **O servidor de hoje recusa pedido com `Cf-Ray`, `Cf-Connecting-Ip` e `X-Forwarded-For`** (403, a regra da CN1). Atrás da
  Cloudflare, todo pedido traz esses cabeçalhos: a CN5 troca essa regra pela origem fechada da seção 6 (só a Cloudflare chega à VPS) e
  passa a ler o IP do `Cf-Connecting-Ip`. **Sem essa troca, a API não responde atrás da borda.**
- [ ] O widget do Turnstile no painel: o domínio do jogo na lista de domínios do widget; modo "Managed". A chave do site vai no ambiente do
  servidor (a página a recebe do `GET /conta/primeiro-acesso` e do `GET /assets/estado`); o segredo, só no servidor.
- [ ] Os testes do CI seguem com as chaves de teste oficiais e o fetch falso (`servidor_web/test/protecao.test.ts`); nenhuma chave real
  entra em teste.

## 3. Os robôs

- [ ] **Bloquear os robôs de IA** (Security › Bots: "Block AI Scrapers and Crawlers"; no Free, a disponibilidade **não conferida**, a
  pendência da seção 8 do plano da hospedagem).
- [ ] **Bot Fight Mode** ligado (Free). No Pro, o **Super Bot Fight Mode**: "Definitely automated" bloqueado, "Likely automated" com
  desafio gerenciado, só nos domínios do jogo e dos assets. **Não** na API: o jogo chama a API por `fetch`, e o desafio quebraria a
  chamada (ela não mostra a página do desafio).
- [ ] **O `robots.txt` gerenciado da Cloudflare desligado** (ou conferido contra o nosso): o do jogo sai do build
  (`web/app/public/robots.txt`, gerado de `servidor_web/src/protecao/robots.ts`); o da API é o `GET /robots.txt` do servidor. Dois
  `robots.txt` diferentes no mesmo domínio confundem o robô honesto.
- [ ] Os robôs bons verificados (a busca) **seguem entrando** no domínio do jogo: as páginas públicas da CN6 precisam ser achadas.
- [ ] **O aviso de mineração reservada (PI-6, o TDMRep; D-CONTA-231 a 234) chega intacto nos três nomes.** O código já o põe: o
  arquivo `/.well-known/tdmrep.json` (`[{"location": "/", "tdm-reservation": 1}]`) e o cabeçalho `tdm-reservation: 1` no jogo (o
  `_headers` e o `.well-known/` que o `montar_site.sh` leva para a raiz do Pages; a meta `tdm-reservation` no HTML), na API (toda
  resposta) e no Worker dos assets (o arquivo sem assinatura; o cabeçalho em toda resposta). A fonte é
  `servidor_web/src/protecao/tdmrep.ts`, e o protocolo é o relatório final do grupo do W3C de 2024-05-10
  (https://www.w3.org/community/reports/tdmrep/CG-FINAL-tdmrep-20240510/). **Na Cloudflare:** nenhuma Transform Rule de cabeçalho de
  resposta remove nem troca o `tdm-reservation` (as regras do `X-Robots-Tag` da seção 6 e as da seção 8 **acrescentam**, com "Set" só
  no cabeçalho delas); nenhuma regra de cache, redirecionamento ou página gerenciada cobre o `/.well-known/tdmrep.json`; o `robots.txt`
  gerenciado da Cloudflare, se ligado, não substitui o arquivo. **Depois do deploy:** `curl -sI https://digilab.exemplo/jogo/`,
  `https://api.digilab.exemplo/saude` e um asset assinado mostram `tdm-reservation: 1`, e `curl -s https://<cada nome>/.well-known/tdmrep.json`
  devolve o arquivo com 200 (os três nomes são origens diferentes, e o protocolo lê o arquivo de cada uma). Se a Cloudflare tirar o
  cabeçalho, a volta é uma Transform Rule "Set static" `tdm-reservation` = `1` nos três nomes.

## 4. As regras de WAF (Security › WAF › Custom rules)

O Free dá poucas regras (5, **não conferido**); a ordem abaixo é a da prioridade.

| # | onde | expressão (a linguagem de regras da Cloudflare) | ação | por quê |
|---|---|---|---|---|
| W1 | assets | `http.host eq "assets.digilab.exemplo" and http.request.uri.path ne "/.well-known/tdmrep.json" and not is_timed_hmac_valid_v0("<DIGILAB_SEGREDO_ASSETS>", http.request.uri, 600, http.request.timestamp.sec, 8)` | Block | a URL sem a assinatura certa, ou vencida, não baixa. O 600 é o `DIGILAB_VALIDADE_ASSETS_S`; o 8 é o tamanho de `?verify=`. **A função é de plano pago (não conferido):** no Free, a opção é um Worker na frente do R2 com o `verificar` de `servidor_web/src/protecao/assinatura.ts` (seção 6) |
| W2 | assets | `http.host eq "assets.digilab.exemplo" and ip.src.asnum in {<os ASN de datacenter: AWS, Google Cloud, Azure, OVH, Hetzner, DigitalOcean…>}` | Managed Challenge | a regra contra as faixas de datacenter da seção 6 do plano: o robô em nuvem leva o desafio; o jogador em casa, não. A lista de ASN se monta no dia (**SEM FONTE**) |
| W3 | API | `http.host eq "api.digilab.exemplo" and not http.request.uri.path in {"/saude" "/robots.txt" "/.well-known/tdmrep.json"} and not starts_with(http.request.uri.path, "/auth/") and http.request.method eq "GET" and not any(http.request.headers["origin"][*] eq "https://digilab.exemplo") and not http.cookie contains "dl_sessao="` | Block | o `GET` sem a origem do jogo e sem a sessão não tem nada a fazer na API (o login passa, porque vai por navegação) |
| W4 | tudo | `cf.threat_score gt 30` (ou o campo que o plano tiver; **não conferido** no Free) | Managed Challenge, só no jogo e nos assets | o IP com fama ruim |

**O segredo dentro da regra W1** fica no painel da Cloudflare, não no repositório; trocar o segredo pede trocar a regra e o ambiente da
VPS na mesma hora (as URLs já entregues param de valer, e o jogo pede outras).

## 5. O limite de pedidos (Security › WAF › Rate limiting rules)

O servidor já tem os limites por conta (a cota da fala, as lutas por dia, o teto de assinaturas por hora). **O limite por IP fica na borda**
(D-CONTA-220): o servidor não vê o IP de verdade até a troca da seção 2. No Free, uma regra (**não conferido**), com a janela de 10 s.

| # | onde | contagem | limite (PROPOSTO, SEM FONTE) | ação |
|---|---|---|---|---|
| R1 | `api.` (tudo) | por IP | 100 pedidos em 10 s | Block por 60 s |
| R2 | `api.` `/auth/*` e `/conta/primeiro-acesso` | por IP | 10 em 10 s | Block por 600 s (só com regra a mais, no Pro) |
| R3 | `api.` `/api/fala` | por IP | 20 em 10 s | Block por 60 s (só com regra a mais; a cota por conta já segura o gasto) |
| R4 | `assets.` | por IP | 300 em 10 s | Managed Challenge (só com regra a mais) |

Com uma regra só, vale a R1. O jogo inteiro, ao abrir, pede umas dezenas de assets e uma dezena de rotas da API (**não medido**: medir no
navegador antes de fechar o número, para não barrar o jogador que abre a ilha).

## 6. Os assets: o R2 e o Worker

- [ ] O bucket do R2 **sem acesso público pelo `r2.dev`** (desligado); só pelo domínio próprio `assets.`, onde as regras valem.
- [ ] **O CORS do bucket:** `GET` e `HEAD` só da origem `https://digilab.exemplo`, sem credenciais (a URL assinada não leva cookie).
- [ ] **O cache:** a assinatura muda a cada URL, então a regra de cache (Caching › Cache Rules) **ignora a query `verify` na chave do
  cache** ("Cache key: query string: ignore", ou excluir `verify`) e guarda o arquivo pelo caminho; o W1 confere a assinatura antes do
  cache. Assim o R2 é lido uma vez por arquivo, não uma vez por jogador. `Cache-Control` do arquivo: `public, max-age=86400` (PROPOSTO).
- [ ] **Se o W1 não estiver no plano:** um Worker na rota `assets.digilab.exemplo/*` que confere o `verify` com o mesmo código do
  `verificar` (`servidor_web/src/protecao/assinatura.ts`, só `node:crypto` → WebCrypto) e lê o R2 pelo binding. O Workers grátis tem
  limite de pedidos por dia (**não conferido**); o jogo tem poucas centenas de peças por jogador por dia (a conta da seção 6 do plano da
  hospedagem). O Worker é código novo: entra num PR próprio da CN5, com teste. O Worker entrega o `/.well-known/tdmrep.json` sem
  assinatura (PI-6, D-CONTA-234): é o único caminho aberto, e o W1 tem a mesma exceção.
- [ ] O `X-Robots-Tag: noindex` nos assets (Rules › Transform Rules › Response headers), para o arquivo que vazar não ir para a busca.

## 7. A API atrás da borda

- [ ] O proxy ligado (nuvem laranja) em `api.`; **o SSL "Full (strict)"** com o certificado de origem da Cloudflare na VPS.
- [ ] **A origem fechada:** o firewall da VPS só aceita o 443 das faixas de IP da Cloudflare (a lista pública dela), ou o Cloudflare Tunnel
  (sem porta aberta). Sem isso, o robô fala direto com a VPS e pula a borda.
- [ ] **O cache desligado na API** (Cache Rules: `api.` → Bypass). As respostas já levam `Cache-Control: no-store`.
- [ ] O `Always Use HTTPS` e o HSTS (com cuidado: o HSTS com `preload` não se desfaz rápido).

## 8. O jogo (Pages)

- [ ] O `robots.txt` do build na raiz (o Vite copia `web/app/public/`; o `montar_site.sh` o leva do `/jogo/` para a raiz, com o
  `.well-known/` e o `_headers`, D-CONTA-233).
- [ ] O `_headers` já existe (PI-6): `/*` com o `tdm-reservation: 1`, gerado de `servidor_web/src/protecao/tdmrep.ts` por
  `node servidor_web/scripts/gerar_robots.ts`. Os cabeçalhos de segurança abaixo entram **no mesmo arquivo gerado** (o Pages lê um
  `_headers` só), sem tirar a linha do TDMRep; o `conferir_build.ts` do jogo e o `test/tdmrep.test.ts` do servidor reprovam se ela sumir.
- [ ] Os cabeçalhos (`_headers` do Pages, um arquivo no build, PR da CN5): `X-Content-Type-Options: nosniff`, `Referrer-Policy:
  strict-origin-when-cross-origin`, o `Content-Security-Policy` com o `challenges.cloudflare.com` no `script-src` e no `frame-src` (o
  widget do Turnstile) e a `api.` e a `assets.` no `connect-src` e no `img-src`.

## 9. Depois de abrir: o que olhar

- Security › Events: os bloqueios do W1 (URL vencida demais? a validade curta pode estar barrando quem joga com a rede lenta) e do R1.
- O painel do Turnstile: a taxa de desafio resolvido; se muita gente falha, o modo do widget está duro demais.
- O gasto da fala (o teto total e a cota por conta) no `GET /api/fala/status` e no alerta por e-mail.
- **O Pro (CH-6) só se os robôs aparecerem nos registros.**
