# CN5: a hospedagem de teste, o roteiro (2026-11-20)

A etapa CN5 do `docs/PLANO_V3_CONTA.md` (seção 10) e do `docs/ROADMAP_V3_CONTA.md` (F1), na pilha das CH-1 a CH-7
(`docs/PLANO_V3_CONTA_HOSPEDAGEM.md`): o Lightsail em São Paulo, a Cloudflare na frente, o Pages, o R2, o SQLite com o Litestream.

**O código está pronto; nada foi contratado.** Contratar é do Matheus (TAREFA_V3_CONTA, seção 6). Este roteiro diz o que contratar, em que
ordem, e o que pôr em cada lugar. Nenhuma chave entra no repositório: os segredos ficam no ambiente "teste" do GitHub e nos
`/etc/digilab/*.env` da VPS.

**NÃO CONFERIDO:** nada disto rodou numa VPS, no Pages ou no R2. O que foi conferido aqui: o pacote do servidor sobe numa pasta limpa, a borda
recusa o pedido que não vem pelo túnel, o build leva o endereço dos assets, a assinatura do envio ao R2 confere com o exemplo da AWS.

## 1. As peças

| peça | onde | o que roda | no repositório |
|---|---|---|---|
| a API | o Lightsail de 2 GB em São Paulo (CH-2) | o `servidor_web` no systemd, só em `127.0.0.1:8766`, com `--borda cloudflare` | `servidor_web/deploy/digilab-api.service` |
| a entrada da API | o Cloudflare Tunnel (`cloudflared`), de dentro da VPS para a Cloudflare | `api.<domínio>` → `http://127.0.0.1:8766`; nenhuma porta aberta além do SSH (D-CONTA-197) | o `instalar.sh` instala; o túnel é criado no painel |
| o banco | `/var/lib/digilab/conta.sqlite` | o SQLite em WAL; a conta, o save na nuvem e o ranking | `servidor_web/src/conta/banco.ts` |
| a cópia do banco | o bucket privado `digilab-banco` no R2 | o Litestream, sem parar (CH-4) | `servidor_web/deploy/litestream.yml`, `litestream.service` |
| o jogo | o Cloudflare Pages: `<domínio>/jogo/` (RC-6) | o build do Vite, com a API e os assets do domínio | `.github/workflows/publicar.yml`, `servidor_web/deploy/montar_site.sh` |
| a raiz do domínio | o Pages | um aviso que leva a `/jogo/`, até a página de entrada (RC-5) existir em código (D-CONTA-202) | `montar_site.sh` |
| os assets | o bucket público `digilab-assets` no R2, em `assets.<domínio>` | o atlas, a decoração, os sons, a cena da evolução, os cenários da luta (478 arquivos, 108 MiB em 2026-11-20) | `web/app/scripts/publicar_assets.ts` |
| o aviso de queda | o Better Stack (CH-5) | um monitor em `https://api.<domínio>/saude` | — |

## 2. A ordem do que contratar (o Matheus)

Os preços do dia estão na seção 8. Em cada passo, anote o que está em **negrito**: vai para a seção 3.

1. **O domínio.** No Cloudflare Registrar (preço de custo, o DNS já na Cloudflare) ou no Registro.br (o `.com.br`, depois apontado para
   a Cloudflare). Anote o **domínio**.
2. **A Cloudflare, plano Free (CH-6).** Ponha o domínio na conta. Em *Security > Bots*, ligue o bloqueio dos robôs de IA (AI Crawl Control).
   Anote o **id da conta** (*Account ID*, no painel).
3. **O R2.** Dois buckets:
   - `digilab-banco`, **privado**: a cópia do SQLite;
   - `digilab-assets`, **público** pelo domínio próprio `assets.<domínio>` (*Settings > Custom Domains*), com o CORS da seção 6.
   Dois tokens do R2 (*R2 > Manage API Tokens*), cada um com **"Object Read & Write" só no seu bucket**: o do banco vai para a VPS; o dos
   assets fica na máquina do Matheus. Anote o **id e o segredo** de cada um.
4. **O Pages.** Crie um projeto "Direct Upload" (sem ligar ao GitHub), por exemplo `digilab`, e ligue o domínio próprio `<domínio>`.
   Crie um token da API (*My Profile > API Tokens*) com só **"Cloudflare Pages: Edit"**. Anote o **nome do projeto** e o **token**.
5. **A AWS e o Lightsail (CH-2).** Uma instância Linux **Ubuntu 24.04 LTS**, 2 GB, em **São Paulo**, com um IP estático. No *Networking*
   da instância, feche o 80 e o 443 (fica só o 22). Ligue os **snapshots automáticos** (cobrados como snapshot, seção 8). Anote o **IP**.
6. **A VPS:** a seção 4 (o `instalar.sh`).
7. **O túnel.** Em *Zero Trust > Networks > Tunnels*, crie um túnel "cloudflared", copie o comando `sudo cloudflared service install
   <token>` e rode na VPS. No túnel, um *Public Hostname*: `api.<domínio>` → `HTTP` → `127.0.0.1:8766`.
8. **Os apps OAuth** (CN2), com o callback `https://api.<domínio>/auth/callback`: no Google (*APIs & Services > Credentials*) e no GitHub
   (*Settings > Developer settings > OAuth Apps*). Os quatro valores vão no `/etc/digilab/api.env` (seção 3).
9. **O Better Stack:** um monitor HTTP em `https://api.<domínio>/saude`, com o aviso por e-mail.
10. **O GitHub:** o ambiente `teste` com os segredos e as variáveis da seção 3. Por último, a variável `DIGILAB_PUBLICAR = sim` liga o
    deploy.

## 3. Os segredos e as variáveis

**No GitHub, ambiente `teste`** (*Settings > Environments > teste*; os segredos nunca aparecem no log):

| nome | tipo | o quê |
|---|---|---|
| `DIGILAB_SSH_CHAVE` | segredo | a chave privada do usuário `publicador` na VPS (seção 4), só para o deploy |
| `DIGILAB_SSH_HOST_CHAVE` | segredo | a linha do `known_hosts` da VPS (`ssh-keyscan -t ed25519 <IP>`, conferida com a impressão que o Lightsail mostra) |
| `DIGILAB_SSH_DESTINO` | segredo | `publicador@<IP>` |
| `CLOUDFLARE_API_TOKEN` | segredo | o token "Pages: Edit" |
| `CLOUDFLARE_ACCOUNT_ID` | segredo | o id da conta |
| `DIGILAB_DOMINIO` | variável | o domínio, sem `https://` |
| `DIGILAB_PAGES_PROJETO` | variável | o nome do projeto do Pages |
| `DIGILAB_NUVEM` | variável | `1` liga o save na nuvem no build (CN3); vazio, desligado |
| `DIGILAB_MARCO_RANQUEADA` | variável | o marco da luta ranqueada no jogo (`7` no beta, D-CONTA-76); vazio, o padrão |
| `DIGILAB_PUBLICAR` | variável **do repositório** | `sim` liga o workflow `publicar`; sem ela, ele não roda |

**Na VPS:** `/etc/digilab/api.env` e `/etc/digilab/litestream.env`, pelos modelos `servidor_web/deploy/*.env.exemplo` (o `instalar.sh` copia
os modelos vazios, com o modo 640). O `DIGILAB_URL_API` é `https://api.<domínio>`; o `DIGILAB_URL_JOGO`, `https://<domínio>/jogo/`.

**Na máquina do Matheus:** `DIGILAB_R2_CONTA`, `DIGILAB_R2_BUCKET_ASSETS`, `DIGILAB_R2_CHAVE_ID` e `DIGILAB_R2_CHAVE_SEGREDO` (o token dos
assets), só no ambiente da sessão que publica os assets (seção 6).

## 4. Preparar a VPS (uma vez)

```bash
# na sua máquina: copiar a pasta do deploy para a VPS
scp -r servidor_web/deploy ubuntu@<IP>:/tmp/deploy
# na VPS
sudo LITESTREAM_SHA256=<o sha256 do litestream-v0.3.13-linux-amd64.deb, da página do release> bash /tmp/deploy/instalar.sh
sudo nano /etc/digilab/api.env          # seção 3
sudo nano /etc/digilab/litestream.env   # o token do banco
sudo systemctl start litestream.service
```

O `instalar.sh` instala o Node 24.19.0 (conferido pelo `SHASUMS256.txt` do nodejs.org), o Litestream 0.3.13 (conferido pelo sha256 dado: o
script não anda sem ele) e o `cloudflared` (pelo apt da Cloudflare). Também cria o usuário `digilab` e as pastas, liga as unidades do
systemd e fecha o `ufw` em tudo menos o SSH.

**O usuário do deploy:** um `publicador` sem senha, que só pode rodar o script de publicar como root:

```bash
sudo adduser --disabled-password --gecos "" publicador
sudo install -d -o publicador -m 700 /home/publicador/.ssh
echo "<a chave pública do par gerado para o CI>" | sudo tee /home/publicador/.ssh/authorized_keys
echo "publicador ALL=(root) NOPASSWD: /usr/local/sbin/digilab-publicar" | sudo tee /etc/sudoers.d/digilab-publicar
sudo chmod 440 /etc/sudoers.d/digilab-publicar
```

## 5. O backup e o ensaio da restauração

- **O Litestream** manda o WAL ao R2 a cada 10 s, uma cópia inteira por dia, e guarda 30 dias (PROPOSTO, SEM FONTE; `litestream.yml`).
- **O snapshot automático do Lightsail** guarda o disco inteiro, por dia.
- **O ensaio, antes do primeiro convidado:** `sudo bash /tmp/deploy/restaurar.sh ensaio` restaura a cópia do R2 numa pasta ao lado e
  mostra o `integrity_check`, a versão das migrações e o número de contas. Se o ensaio não bater com o banco de agora, o deploy não está
  pronto.
- **A restauração de verdade:** `restaurar.sh valer` para o servidor e o Litestream, guarda o banco de agora ao lado com a hora no nome,
  restaura no lugar e religa.

## 6. Os assets

O CI não tem a pasta Assets (fica fora do git). Os assets sobem da máquina do Matheus, quando mudam:

```powershell
cd D:\Trab\digilab\v3\web\app
node scripts/publicar_assets.ts            # só a lista: nada sai da máquina
node scripts/publicar_assets.ts --enviar   # manda o que mudou (o MD5 contra o ETag do R2)
```

A lista é a mesma que o dev do Vite serve (`web/app/scripts/assets_publicos.ts`). Os kits do habitat que não se redistribuem (o Tiny Fantasy
Forest e o Cassette Beasts) não sobem. **Até a CN4, os assets ficam num caminho fixo e público** (D-CONTA-199): quem souber o endereço baixa
o atlas.

**O CORS do bucket `digilab-assets`** (*R2 > digilab-assets > Settings > CORS Policy*): o jogo lê os JSON por `fetch` e as imagens como
textura, então a origem do jogo precisa estar liberada.

```json
[{ "AllowedOrigins": ["https://<domínio>"], "AllowedMethods": ["GET", "HEAD"], "AllowedHeaders": ["*"], "MaxAgeSeconds": 3600 }]
```

## 7. O deploy pelo CI

O workflow `.github/workflows/publicar.yml` roda a cada push na `main` que muda `servidor_web/` ou `web/app/`, e à mão
(*Actions > publicar > Run workflow*). Só roda com `DIGILAB_PUBLICAR = sim`.

1. **O servidor:** os tipos e o Vitest; o pacote (`montar_pacote.sh`: o `git archive` do commit com o `servidor_web`, o motor e as regras do
   jogo que ele importa), conferido numa pasta limpa (`conferir_pacote.sh`); o envio por `scp` com a chave do host fixada; o
   `digilab-publicar`, que troca a versão e **volta para a de antes se a `/saude` não responder em 30 s**. Guarda as 5 últimas versões.
2. **O jogo, depois do servidor:** os tipos, o Vitest, o build com `VITE_DIGILAB_API=https://api.<domínio>` e
   `VITE_DIGILAB_ASSETS=https://assets.<domínio>/`, e o `wrangler pages deploy` (versão fixa 4.158.0).

**Voltar uma versão:** rode o workflow à mão num commit anterior (*Run workflow* a partir de um branch com o commit), ou, na VPS, aponte
`/opt/digilab/atual` para uma pasta de `/opt/digilab/versoes/` e reinicie o `digilab-api`.

## 8. Os preços, conferidos em 2026-11-20

Lidos nas páginas oficiais por uma pesquisa desta sessão; os da seção 8 do plano da hospedagem. **Conferir de novo no dia de contratar.**

| item | o que a página diz | fonte |
|---|---|---|
| Lightsail Linux 2 GB, com IPv4 | US$ 12 por mês, 2 vCPU, 60 GB; a página não tem uma tabela própria para São Paulo | [preços](https://aws.amazon.com/lightsail/pricing/) |
| o tráfego em São Paulo | a metade do da tabela ("half the data transfer allowances"): 1,5 TB no plano de 2 GB, pela conta | [FAQ do tráfego](https://docs.aws.amazon.com/lightsail/latest/userguide/amazon-lightsail-faq-data-transfer-allowance.html) |
| o excedente em São Paulo | US$ 0,15 por GB, só a saída | idem |
| o snapshot | US$ 0,05 por GB-mês, **o automático também**; os seguidos cobram só o que mudou | [FAQ da cobrança](https://docs.aws.amazon.com/lightsail/latest/userguide/amazon-lightsail-frequently-asked-questions-faq-billing-and-account-management.html) |
| a Akamai na América do Sul | é São Paulo (`br-gru`), a única região lá | [regiões](https://api.linode.com/v4/regions) |
| o `.com` no Cloudflare Registrar | **não conferido** (a página diz "preço de custo", sem o número; a busca recusou o acesso automático) | [Registrar](https://www.cloudflare.com/application-services/products/registrar/buy-com-domains) |
| o `.com.br` no Registro.br | R$ 40 por ano, pelo resumo da página; a renovação **não conferida** | [valores](https://registro.br/dominio/valores/) |
| o bloqueio dos robôs de IA | "Available on all plans" (o Free não aparece pelo nome) | [AI Crawl Control](https://developers.cloudflare.com/ai-crawl-control/) |
| o Cloudflare Tunnel | "Available on all plans"; o preço **não conferido** na página | [Tunnel](https://developers.cloudflare.com/tunnel/) |
| o R2 | 10 GB-mês, 1 milhão de operações A e 10 milhões de B grátis por mês (só a classe Standard); a saída grátis | [preços do R2](https://developers.cloudflare.com/r2/pricing/) |
| o Pages Free | 20 000 arquivos por site, 25 MiB por arquivo (o build de 2026-11-20 tem 172) | [limites](https://developers.cloudflare.com/pages/platform/limits/) |

**A conta por mês, com os convidados:** uns US$ 12 do Lightsail, mais uns US$ 1 a 2 dos snapshots (dependem do quanto o disco muda), mais o
domínio, mais a fala. Os assets (108 MiB) cabem nos 10 GB grátis do R2.

## 9. O que fica para depois

- **As URLs assinadas e o Turnstile** (a CN4): até lá, os assets ficam num caminho fixo (D-CONTA-199).
- **O Sentry** (CH-5): o SDK é uma dependência nova no servidor, e o `servidor_web/CLAUDE.md` fecha a lista. Até o ok, os erros ficam no
  `journalctl -u digilab-api` (D-CONTA-200).
- **A página de entrada** (RC-5): é de outra sessão. Até lá, a raiz leva ao jogo (D-CONTA-202).
- **O aviso da RC-7** (o save do `localStorage` antigo, na primeira abertura no domínio novo): não está neste PR.
