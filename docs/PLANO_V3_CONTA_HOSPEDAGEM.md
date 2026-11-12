# Plano da hospedagem: os provedores, os preços e a escolha (2026-11-12)

**Status:** PROPOSTO, sem código. É a parte "os custos conferidos com os preços do dia" da etapa **CN5** do `docs/PLANO_V3_CONTA.md`, dentro
da pilha já decidida na **CN-7** (Node 24 + Hono numa VPS, SQLite com a cópia no R2, o login no próprio servidor, a Cloudflare na
frente). As decisões CH-1 a CH-7 (seção 7) vão ao Matheus, cada uma com a recomendação e o custo de errar.

**Origem:** o Matheus, em 2026-11-12: "Eu quero uma análise comparativa de quais clouds a gente vai utilizar, tanto precificação quanto as
features que cada uma apresenta e que sejam interessantes para o projeto."

**Os preços:** lidos nas páginas oficiais em 2026-11-12, cada um com a URL. Onde a página não abriu ou não mostrou o número, a célula diz
**"não conferido"**; onde o número veio de outra fonte, diz **"secundário"**. Preço de nuvem muda sem aviso: **conferir de novo no dia de
contratar.** Os valores em euro não têm IVA. Nada aqui é contrato nem orçamento.

## 1. O que o projeto precisa de uma nuvem

O jogo roda no navegador: o cérebro, o corpo, o mundo e a luta ficam no cliente (seção 1 do `docs/PLANO_V3_CONTA.md`). O servidor só
guarda e confere. Isso deixa a conta pequena:

| peça | o que faz | o que pesa na escolha |
|---|---|---|
| **o servidor Node** | o login, a sincronização do save por eventos, a vez por pet, a conferência pelo replay (uns 70 ms por vida), a `/api/fala` e a confirmação dos vídeos | 1 a 2 vCPU e 2 GB de RAM sobram para 1 000 jogadores por dia (a conta da seção 7 do plano da conta); um disco persistente para o SQLite |
| **o banco** | contas, sessões, apoios, metadados dos pets | SQLite no disco do servidor, com a cópia contínua para o R2 (CN-7) |
| **os logs dos pets e as cópias** | o save na nuvem, as cópias diárias | armazenamento de objetos barato e com a saída grátis |
| **o jogo e os assets** | o build do Vite e os sprites, os sons, os pacotes | servidos pela borda, perto do Brasil; a pasta inteira tem 7,6 GB, mas só uma parte é servida |
| **a proteção** | a seção 6 do plano da conta | a borda da Cloudflare, o Turnstile, o limite de pedidos |
| **a observabilidade** | erros, o servidor de pé, o gasto da fala | cota grátis basta no começo |

**A latência importa pouco.** Como o pet roda no cliente, o jogador não espera o servidor a cada passo: só na sincronização, no login e
na fala. A fala já vai a um servidor da Anthropic, fora do Brasil. Uma VPS nos Estados Unidos (uns 120 a 150 ms de São Paulo, SEM FONTE)
funcionaria; uma em São Paulo responde mais rápido e é a escolha natural se o preço for parecido.

**A LGPD não obriga o dado a ficar no Brasil:** a transferência internacional é permitida com as salvaguardas da lei. Isso entra na revisão
da CN-10, e este plano não é parecer jurídico.

## 2. A computação: a VPS

Plano de 2 GB de RAM, o tamanho que serve para os convidados e para os 100 jogadores por dia.

| provedor | plano | preço por mês | tráfego incluído | Brasil | o que importa | conferido |
|---|---|---|---|---|---|---|
| **AWS Lightsail** | 2 GB, 2 vCPU | **US$ 12** (US$ 10 só com IPv6) | 3 TB; **em São Paulo, a metade (1,5 TB)** | **sim, São Paulo** | snapshot US$ 0,05/GB; preço fixo, sem surpresa; o ecossistema da AWS se um dia precisar | sim ([fonte](https://aws.amazon.com/lightsail/pricing/)); o preço exato em São Paulo, não |
| **Akamai (Linode)** | Linode 2 GB, 1 vCPU | **US$ 12** | 2 TB; excedente US$ 0,005/GB | a página mostra "South America", sem nomear São Paulo | o excedente mais barato da tabela | sim ([fonte](https://www.akamai.com/cloud/pricing/cpu)); a região, secundário |
| **Vultr** | vc2-1c-2gb / vc2-2c-2gb | US$ 10 / US$ 15; **em São Paulo, US$ 15 / US$ 22,50** | 2 TB / 3 TB | **sim, `sao`** | São Paulo custa 50 % a mais | sim, pela API oficial ([fonte](https://api.vultr.com/v2/plans?type=vc2&per_page=100)) |
| **DigitalOcean** | Basic 2 GiB, 1 vCPU | US$ 12 | 2 000 GiB | não (São Paulo não está na lista) | backup de 20 % a 30 % do preço; snapshot US$ 0,06/GB | sim ([fonte](https://www.digitalocean.com/pricing/droplets)) |
| **Azure** | B1s Linux, Brazil South | uns US$ 12,30 (US$ 0,0168/h × 730 h) | não conferido | **sim, Brazil South** | o IPv4 e o tráfego cobram à parte (não conferido) | sim, pela API de preços ([fonte](https://prices.azure.com/api/retail/prices?$filter=armRegionName%20eq%20%27brazilsouth%27%20and%20armSkuName%20eq%20%27Standard_B2ats_v2%27)) |
| **Hetzner** | CPX12, 1 vCPU, 2 GB | €11,99 (Nuremberg) / €9,99 (Helsinque) | 20 TB | não (Alemanha, Finlândia, EUA, Singapura) | **todos os planos marcados "currently unavailable"** na página; os planos baratos (CX) também; reajuste de preço em 2026 | sim ([fonte](https://www.hetzner.com/cloud/regular-performance/)) |
| **OVHcloud** | VPS-1, 2 vCPU, 4 GB | a partir de US$ 4,54 | ilimitado, 500 Mbps | a página não cita o Brasil | anti-DDoS e backup de 24 h incluídos | sim ([fonte](https://www.ovhcloud.com/en/vps/)); o Brasil, não |
| **Contabo** | Cloud VPS 4, 4 vCPU, 8 GB | uns €5,50 (com contrato de 24 meses) | "ilimitado" (uso justo), 200 Mbit/s | não | taxa de instalação no mensal; preço baixo com contrato longo | sim ([fonte](https://contabo.com/en/vps/)); o valor exato, só no checkout |
| **Oracle Cloud** | Always Free | US$ 0 | 10 TB de saída | São Paulo e Vinhedo existem; não conferido na página | 2 VMs de 1 GB ou A1 Ampere de 2 OCPU e 12 GB; **pode faltar capacidade, e a Oracle recupera a máquina ociosa** (uso abaixo de 20 % por 7 dias) | sim ([fonte](https://docs.oracle.com/en-us/iaas/Content/FreeTier/resourceref.htm)) |
| **Google Cloud** | e2-micro grátis | US$ 0 | 1 GB de saída por mês | não (só três regiões dos EUA) | 1 GB de saída não serve para um jogo | sim ([fonte](https://docs.cloud.google.com/free/docs/free-cloud-features)) |
| **Magalu Cloud** | VMs BV | não conferido (em R$) | não conferido | **sim, br-se1 e br-ne1** | brasileira, cobra em real, armazenamento compatível com S3 | não (a calculadora não abriu; [preços](https://magalu.cloud/precos/), [regiões](https://docs.magalu.cloud/docs/computing/virtual-machine/overview)) |

**O serviço gerenciado (PaaS), para comparar** (a CN-7 decidiu VPS; estes entram só como a outra opção da CH-2):

| provedor | plano | preço por mês | Brasil | o que importa | conferido |
|---|---|---|---|---|---|
| **Fly.io** | shared-cpu-1x, 1 GB | uns US$ 6,70 (em Ashburn; em São Paulo não conferido) + volume US$ 0,15/GB + IPv4 US$ 2 | **sim, `gru`** | cobra por segundo; o volume serve para o SQLite; saída para a América do Sul US$ 0,04/GB; sem cota grátis | sim ([preço](https://docs.fly.io/about/pricing), [regiões](https://docs.fly.io/reference/regions)) |
| **Railway** | Hobby | US$ 5 com US$ 5 de crédito; a memória sai uns US$ 10/GB-mês | não | uma API de 1 GB sempre ligada passa do crédito | sim ([fonte](https://railway.com/pricing)) |
| **Koyeb** | small, 1 vCPU, 1 GB | US$ 10,71 | não conferido | o grátis não aceita volume (não serve para o SQLite) | sim ([fonte](https://www.koyeb.com/docs/reference/instances)) |
| **Render** | — | não conferido | não conferido | a página não abriu | não |

## 3. A borda, o estático e o armazenamento

| provedor | serviço | preço | o que importa | conferido |
|---|---|---|---|---|
| **Cloudflare Pages / Workers** | o jogo estático | **US$ 0**: "Requests to static assets are free and unlimited"; o Workers pago é US$ 5 se precisar | serve o build do Vite pela borda, com PoPs no Brasil (não conferido na página) | sim ([fonte](https://developers.cloudflare.com/workers/platform/pricing/)) |
| **Cloudflare R2** | os assets, os logs dos pets, as cópias, a cópia do SQLite | **US$ 0,015/GB-mês; a saída é grátis**; grátis até 10 GB, 1 milhão de operações A e 10 milhões de operações B por mês | "There are no charges for egress bandwidth"; as operações cobram (A: US$ 4,50 por milhão) | sim ([fonte](https://developers.cloudflare.com/r2/pricing/)) |
| **Cloudflare Turnstile** | o desafio sem captcha | US$ 0, ilimitado | até 20 widgets | sim ([fonte](https://developers.cloudflare.com/turnstile/plans/)) |
| **Cloudflare, a proteção** | contra robôs | Free: DDoS e o Bot Fight Mode simples; **Pro** (uns US$ 25, não conferido): o Super Bot Fight Mode e as regras de WAF | se o bloqueio dos robôs de IA é grátis: não conferido | parcial ([Free](https://developers.cloudflare.com/bots/get-started/free/), [Pro](https://www.cloudflare.com/plans/pro/)) |
| **Backblaze B2** | armazenamento | US$ 6,95/TB-mês; saída grátis até 3 vezes o armazenado | mais barato que o R2 para guardar, mas a saída pode cobrar | sim ([fonte](https://www.backblaze.com/cloud-storage/pricing)) |
| **Bunny.net** | CDN e armazenamento | a CDN na América do Sul: **US$ 0,045/GB** (4,5 vezes a Europa); armazenamento em São Paulo, US$ 0,02/GB | a saída para o Brasil é o custo real | sim ([CDN](https://bunny.net/pricing/), [armazenamento](https://bunny.net/pricing/storage/)) |
| **AWS S3** | armazenamento em São Paulo | não conferido (só os 100 GB de saída grátis por mês) | a saída da AWS cobra | não ([fonte](https://aws.amazon.com/s3/pricing/)) |

## 4. O banco, o login e a observabilidade

| provedor | serviço | grátis | pago | Brasil | o que importa | conferido |
|---|---|---|---|---|---|---|
| **SQLite + Litestream** (a CN-7) | o banco no disco da VPS, copiado para o R2 | US$ 0 (só o R2) | — | onde a VPS estiver | um arquivo, sem serviço a mais | — |
| **Turso** | SQLite hospedado | 5 GB, 500 milhões de leituras | US$ 4,99 | não conferido | o plano B se o SQLite sair da VPS | sim ([fonte](https://turso.tech/pricing)) |
| **Neon** | Postgres | 1 GB por projeto, desliga em 5 min | por uso (US$ 0,106/CU-h) | **sim, sa-east-1** | se um dia trocar para Postgres | sim ([preço](https://neon.com/pricing), [regiões](https://neon.com/docs/introduction/regions)) |
| **Supabase** | Postgres + login + arquivos | 500 MB, 50 000 usuários; **pausa depois de 1 semana parado** | US$ 25 | não conferido | a outra opção da CN-7 | sim ([fonte](https://supabase.com/pricing)) |
| **Cloudflare D1** | SQLite na borda | 5 GB; **para de responder ao passar do limite do dia** | US$ 5 (o Workers) | sem região fixa | só se o servidor fosse para o Workers, e a CN-7 decidiu Node | sim ([fonte](https://developers.cloudflare.com/d1/platform/pricing/)) |
| **Auth.js / Arctic** (a CN-7) | o login no próprio servidor | US$ 0 (biblioteca) | — | — | nenhum serviço a mais | não consultado |
| **Clerk** | o login como serviço | 50 000 usuários retidos | US$ 25 | — | a outra opção, se o login próprio der trabalho | sim ([fonte](https://clerk.com/pricing)) |
| **Sentry** | os erros | 5 mil erros, 30 dias | US$ 29 | — | o erro do servidor e do jogo num lugar | sim ([fonte](https://sentry.io/pricing/)) |
| **Better Stack** | o servidor de pé | 10 monitores, 1 página de status | — | — | o aviso quando cai | sim ([fonte](https://betterstack.com/pricing)) |
| **Grafana Cloud** | métricas e logs | 10 mil séries, 50 GB de logs | US$ 19 | — | o painel de gasto da fala, se crescer | sim ([fonte](https://grafana.com/pricing/)) |

## 5. As pegadinhas

- **Quase ninguém barato tem São Paulo.** Hetzner, OVH, Contabo, DigitalOcean, Railway e Koyeb não mostram o Brasil. Têm: Lightsail,
  Vultr, Azure, Fly.io, Magalu, Oracle (não conferido) e, pela região "South America", a Akamai.
- **São Paulo custa mais ou dá menos.** A Vultr cobra 50 % a mais; o Lightsail dá a metade do tráfego. Para este jogo, a metade do tráfego
  não pesa: a API é pequena, e os assets saem pelo R2.
- **A Hetzner, que era a primeira ideia,** está com os planos "currently unavailable" e reajustou os preços em 2026; não tem região na
  América do Sul.
- **O grátis que some:** a Oracle recupera a máquina ociosa; o Supabase grátis pausa em uma semana; o D1 grátis para no limite do dia; o
  Neon grátis desliga em 5 minutos.
- **A cobrança por uso:** o Railway e o Fly.io cobram por segundo, e o volume do Fly cobra mesmo desligado.
- **A saída de dados:** o R2 não cobra; a Bunny cobra US$ 0,045/GB para a América do Sul; a AWS cobra a saída do S3.

## 6. A conta por cenário

Com a escolha recomendada (a seção 7), em US$ por mês, **sem a fala** (a fala está na seção 13 do plano da conta e cresce por jogador).
Os volumes são PROPOSTOS, SEM FONTE: os assets servidos ficam abaixo de 10 GB, e cada jogador pede umas 200 peças por dia ao R2.

| | convidados | 100 jogadores por dia | 1 000 jogadores por dia |
|---|---|---|---|
| **VPS** (Lightsail São Paulo, 2 GB) | 12 | 12 | 12 a 24 (o de 4 GB, se a CPU passar de 70 % por dias) |
| **snapshot semanal** (uns 20 GB a US$ 0,05) | 1 | 1 | 1 |
| **Cloudflare Pages, R2, Turnstile** | 0 | 0 (umas 600 mil leituras por mês, abaixo dos 10 milhões grátis) | 0 a 1 (umas 6 milhões de leituras) |
| **domínio** (.com.br ou .com; não conferido) | uns 1 a 2 | uns 1 a 2 | uns 1 a 2 |
| **Sentry, Better Stack** | 0 | 0 | 0 |
| **total sem a fala** | **uns 14 a 15** | **uns 14 a 15** | **uns 14 a 28** |

**A leitura:** a infraestrutura fica perto de US$ 15 por mês até mil jogadores por dia, porque o jogo roda no cliente e o R2 não cobra a
saída. A estimativa da seção 7 do plano da conta (US$ 7 a 12 de infraestrutura com 100 por dia) contava com a Hetzner; com São Paulo, a
conta sobe uns US$ 3 a 5. **O que decide o custo continua sendo a fala.**

## 7. Decisões para o Matheus

Cada uma com a recomendação e o custo de errar. **Todas PROPOSTAS.**

- **CH-1. A região: São Paulo.** O preço é parecido (o Lightsail custa o mesmo, com a metade do tráfego, que não pesa), e a sincronização e
  a fala respondem mais rápido. A outra opção são os Estados Unidos (mais provedores, mais baratos), que funcionam porque o jogo roda no
  cliente. Custo de errar: baixo. Mudar de região é um deploy e uma cópia do SQLite.
- **CH-2. A VPS: AWS Lightsail em São Paulo, 2 GB, US$ 12.** Tem São Paulo, preço fixo, snapshots baratos e o IPv4 incluído nesse preço.
  As outras opções: a Akamai na América do Sul (US$ 12, com o excedente mais barato, mas a região não foi confirmada na página); a Vultr em
  São Paulo (US$ 15 com 1 vCPU); e o Fly.io em `gru` (uns US$ 9 a 10, mais fácil de publicar, mas é um PaaS, e a CN-7 decidiu VPS).
  Custo de errar: baixo a médio. O servidor é Node padrão, então trocar de VPS é refazer o deploy.
- **CH-3. O jogo e os assets: Cloudflare Pages + R2,** como a CN-7. O estático é grátis e ilimitado, e o R2 não cobra a saída. A outra
  opção é a Bunny, que cobra US$ 0,045/GB para o Brasil. Custo de errar: médio. A saída paga para o Brasil é o maior custo escondido de um
  jogo com assets.
- **CH-4. O banco: SQLite + Litestream para o R2,** como a CN-7, com o **Turso** como o plano B se o banco precisar sair da VPS. Custo de
  errar: baixo.
- **CH-5. A observabilidade: Sentry Developer + Better Stack Free,** os dois grátis. Custo de errar: baixo.
- **CH-6. O plano da Cloudflare: o Free para começar;** o Pro (uns US$ 25, não conferido) só se os robôs aparecerem nos registros. Custo de
  errar: baixo. O Pro cedo paga uma proteção contra quem ainda não veio.
- **CH-7. Os ambientes:** **um só, o de teste com os convidados, na mesma VPS;** o de produção separado só quando a CN6 abrir para fora.
  Custo de errar: médio. Dois ambientes desde o começo dobram a VPS e o trabalho; um só deixa o teste de uma mudança cair em cima dos
  convidados, que aceitam isso.

## 8. O que falta conferir antes de contratar (na CN5)

- O preço exato do Lightsail em São Paulo e o do excedente de tráfego lá.
- A região da Akamai na América do Sul (se é São Paulo).
- O preço do domínio.
- O que o plano Free da Cloudflare dá contra os robôs de IA.
- Os preços da Magalu Cloud e do Render, que não abriram.
