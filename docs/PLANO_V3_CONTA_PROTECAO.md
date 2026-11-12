# Plano da proteção da propriedade intelectual contra cópia e raspagem (2026-11-12)

**Status:** PROPOSTO, sem código. Aprofunda a seção 6 do `docs/PLANO_V3_CONTA.md` (a proteção do site, decidida na CN-9) para o
**projeto inteiro**: o repositório, o jogo publicado, a borda, a lei e o rastreio. As decisões PI-1 a PI-9 (seção 7) vão ao Matheus, cada
uma com a recomendação e o custo de errar.

**Origem:** o Matheus, em 2026-11-12: "Sobre a questão de proteger a propriedade intelectual de agentes externos e LLMs que podem fazer a
extração dos dados e copiar o projeto, tem algum tipo de proteção que a gente consegue instaurar para evitar esse tipo de coisa?"

**O limite, dito antes:** nenhuma proteção impede um copiador decidido. O que roda no navegador sempre pode ser lido, e o que já foi
público pode já estar numa coleta antiga. O plano faz duas coisas: **encarecer a cópia** e **deixar a autoria provável**, para que uma
cópia possa ser contestada. **Este plano não é parecer jurídico.**

## 1. O que está exposto hoje (conferido em 2026-11-12)

| peça | situação | o que um robô ou uma LLM leva |
|---|---|---|
| **o repositório `matheusmmmp/digilab`** | **PÚBLICO** no GitHub (`gh repo view`) | tudo: o motor TS com o DigiBrain modular, o Python da pesquisa, os gabaritos, os documentos, os planos (inclusive a monetização), o registro e o histórico inteiro do git |
| **a licença** | **não há arquivo LICENSE** | sem licença, a lei reserva os direitos ao autor; mas nada no repositório diz isso, e quem copia alega que não sabia |
| **o jogo publicado** | o build sai minificado e **sem source map** (`sourcemap: false` em `web/app/vite.config.ts`) | o motor e o cérebro em JS minificado: legível com paciência, sem os nomes e comentários originais |
| **o `robots.txt`** | **não há** em `web/app/public/` | nenhum aviso aos robôs de IA |
| **os assets** | servidos por caminho fixo; a CN-9 já decidiu as URLs assinadas e o Turnstile | o atlas e os sons, baixáveis em lote |
| **a pesquisa e o vault** | o vault fica na máquina do Matheus, fora do git | nada, enquanto ficar fora |

**O maior vazamento é o repositório público, não o site:** o site entrega o jogo minificado; o repositório entrega o código-fonte, a
pesquisa e o raciocínio do projeto, com comentários.

## 2. O repositório: privado

**A proposta (PI-1):** mudar o `matheusmmmp/digilab` para privado. É a medida que mais protege, e é reversível (volta a público quando
quiser). O que muda:

- **O que já foi público não volta.** O código e os documentos que estiveram públicos podem já estar em coletas e treinos antigos. A partir
  da troca, não entram mais.
- **O CI deixa de ser grátis e ilimitado.** No repositório público, os runners do GitHub são grátis. No privado, o GitHub Free inclui **US$ 12
  de computação por mês**, e o Linux de 2 núcleos custa **US$ 0,006 por minuto** (uns 2 000 minutos)
  ([fonte](https://docs.github.com/en/billing/concepts/product-billing/github-actions)).
- **O uso de hoje (medido em 2026-11-12):** **1 379 execuções do `verificar-pr` nos últimos 30 dias**, com **5,17 minutos cobráveis por
  execução em média** (amostra das 40 mais novas, cada job arredondado para cima, como o GitHub cobra). São **uns 7 100 minutos por mês**:
  uns US$ 43 no preço do Linux, e **uns US$ 31 por mês acima da cota**. O job `testes` roda no **Windows** (`windows-latest`), que custa
  mais por minuto que o Linux (o preço do Windows não foi conferido): a conta real é maior.
- **Sem pagar, o CI para no meio do mês:** com o limite de gasto em zero, as execuções param quando a cota acaba, e a regra "o merge espera o
  CI" trava os PRs.
- **O resto continua:** os apps do GitHub instalados no repositório (o Codex, o ChatGPT Work, o Claude) mantêm o acesso; as worktrees e os
  clones locais não mudam.

**O que fazer com o CI (PI-2):**
- **cortar os minutos antes da troca:** o job `testes` (Python, no Windows) só quando o Python muda, como o `web` já faz com o filtro de
  caminhos (`.github/workflows/verificar-pr.yml`); um PR só de documento roda só o `relato`. Boa parte das 1 379 execuções vem de
  repetições num mesmo PR (cada envio roda de novo);
- **pôr um teto de gasto** (PROPOSTO: US$ 20 por mês) em vez de zero, para o CI não travar o merge;
- **o runner na máquina do Matheus** (grátis) fica de fora: a máquina é instável sob carga (V3-D8).

## 3. O jogo publicado

| medida | o que faz | situação | a recomendação |
|---|---|---|---|
| **sem source map** | o JS sai sem o mapa para o TS original | **já está** (`sourcemap: false`) | manter, e um teste do build que falha se aparecer um `.map` no `dist/` |
| **minificação** | nomes curtos, sem comentários | **já está** (o Vite) | manter |
| **o aviso de autoria no bundle** | um comentário de licença no topo do JS ("© Matheus de Medeiros Pereira, todos os direitos reservados") | não há | **sim** (PI-4): custa nada e derruba o "não sabia" |
| **a ofuscação do motor** | embaralha o código do cérebro (por exemplo, o `javascript-obfuscator`) | não há | **não agora** (PI-7): deixa o jogo mais lento, e cada mudança no motor teria de provar que o replay sai igual com o código ofuscado; só se uma cópia aparecer |
| **o cérebro no servidor** | o cliente nunca recebe o DigiBrain | não há | **não**: desfaz a arquitetura (o pet roda no cliente; CN-7 e o plano MMO) e multiplica o custo do servidor |

## 4. A borda: os robôs

| medida | o que faz | a recomendação |
|---|---|---|
| **o `robots.txt`** | pede aos robôs de IA declarados que não coletem (GPTBot, ClaudeBot, CCBot, Google-Extended, Applebot-Extended, PerplexityBot, Bytespider…) | **sim** (PI-6), na CN4. Só os honestos obedecem, mas os grandes obedecem |
| **as políticas de robôs de IA da Cloudflare** | ações separadas para três comportamentos: **busca**, **agente** e **treino**, para os robôs verificados e os que se passam por eles; as ações são bloquear, permitir ou "não autorizar" o treino ([fonte](https://developers.cloudflare.com/bots/additional-configurations/block-ai-bots/)) | **sim** (PI-6): **bloquear o treino**; **bloquear o agente nas rotas da API** (um agente que joga pelo jogador gasta a fala e o ranking); **permitir a busca** nas páginas públicas, para o jogo ser achado. **Se isso existe no plano Free não foi conferido** (a página não diz) |
| **o aviso de "mineração de texto e dados" reservada** | um cabeçalho e um arquivo que dizem, de forma legível por máquina, que o conteúdo não pode ser minerado para treino (o protocolo TDMRep do grupo do W3C; pesa na União Europeia) | **sim**, junto com o `robots.txt` (PI-6). O protocolo não foi conferido nesta sessão |
| **os assets atrás da sessão** | URLs assinadas e de vida curta, o Turnstile | **já decidido** (CN-9), na CN4 |

## 5. A lei

| medida | o que faz | a recomendação |
|---|---|---|
| **o LICENSE "todos os direitos reservados"** | diz no repositório que o código, os documentos e as imagens próprias são do autor, sem permissão de cópia, uso ou treino de IA; os sprites do Digimon UP continuam com o crédito da regra 5.1 das `docs/UI_GUIDELINES.md` (não são do projeto, e a licença não fala por eles) | **sim** (PI-4), com o aviso no bundle |
| **os termos de uso do jogo** | proíbem a raspagem, a engenharia reversa, o uso de robôs e o uso do conteúdo para treinar IA | **sim** (PI-5), junto com os termos da CN6 |
| **o registro do programa de computador no INPI** | prova a autoria e a data do código (Lei 9.609/1998); o pedido é pelo e-Software, com o cadastro no e-INPI e um **certificado digital ICP-Brasil**; a taxa é **R$ 210,00** (código 730), **sem desconto** para programa de computador ([serviço](https://www.gov.br/pt-br/servicos/solicitar-o-registro-de-programa-de-computador), [cartilha do INPI](https://www.gov.br/inpi/pt-br/uso-estrategico-da-pi/inpi-para-empreender-e-inovar/pdfs-pi-em-novos-formatos/cartilha-inpi-abes-vf.pdf)) | **sim** (PI-8), antes da CN6 abrir para fora dos convidados. O preço do certificado digital não foi conferido. O registro não impede a cópia: é a prova numa disputa |

## 6. O rastreio

| medida | o que faz | a recomendação |
|---|---|---|
| **os canários** | frases e constantes únicas, sem função, espalhadas no código e nos documentos; uma busca por elas na web ou no GitHub acha a cópia | **sim** (PI-9): baratas; ficam fora do motor (o replay e os gabaritos não mudam) |
| **a marca d'água por conta** | uma marca invisível nos sprites entregues a cada conta | **depois** (já é a CN-9): só se um vazamento aparecer |
| **a busca periódica** | procurar os canários de tempos em tempos | **sim**, junto com a PI-9 (PROPOSTO: uma vez por mês) |

## 7. Decisões para o Matheus

Cada uma com a recomendação e o custo de errar. **Todas PROPOSTAS.**

- **PI-1. O repositório privado: sim, depois da PI-2.** É a medida que mais protege, e volta atrás quando quiser. Custo de errar: alto se
  ficar público (o código, a pesquisa e os planos seguem abertos a qualquer coleta); médio se fechar sem a PI-2 (o CI para no meio do mês e
  trava os merges).
- **PI-2. O CI no privado: cortar os minutos primeiro** (o `testes` só quando o Python muda; o PR de documento só com o `relato`) **e pôr um
  teto de gasto de US$ 20 por mês** (PROPOSTO). O runner na máquina do Matheus fica de fora. Custo de errar: médio. Sem o corte, a conta
  passa de US$ 31 por mês; com o teto em zero, o CI trava.
- **PI-3. O histórico público: não reescrever.** O que já foi público não volta com um `git filter-repo`, e reescrever o histórico quebra
  todas as worktrees e os PRs. Custo de errar: alto, se reescrever.
- **PI-4. O LICENSE "todos os direitos reservados" e o aviso de autoria no bundle: sim.** Custo de errar: baixo.
- **PI-5. Os termos de uso contra a raspagem e o treino: sim**, na CN6. Custo de errar: baixo.
- **PI-6. Os robôs: o `robots.txt`, as políticas de IA da Cloudflare (bloquear o treino, bloquear o agente na API, permitir a busca) e o
  aviso de mineração reservada: sim**, na CN4. Custo de errar: baixo. Bloquear a busca esconde o jogo; não bloquear o agente deixa um robô
  gastar a fala.
- **PI-7. A ofuscação do motor: não agora**, só se uma cópia aparecer. Custo de errar: médio. Ofuscar cedo deixa o jogo mais lento e põe
  em risco a paridade do replay, contra quem ainda não apareceu.
- **PI-8. O registro no INPI: sim**, antes de abrir para fora dos convidados (R$ 210, mais o certificado digital). Custo de errar: médio.
  Sem o registro, a autoria depende do histórico do git, que é mais fácil de contestar.
- **PI-9. Os canários e a busca mensal: sim**, fora do motor. Custo de errar: baixo.

## 8. As etapas

| etapa | o que entrega | depende de |
|---|---|---|
| **PI0: o CI enxuto** | o filtro de caminhos do `testes` e do PR de documento no `verificar-pr.yml`; a medida de novo dos minutos | PI-2 |
| **PI1: o repositório privado** | a troca no GitHub, feita pelo Matheus (é configuração da conta); o teto de gasto | PI0, PI-1 |
| **PI2: a licença e os canários** | o `LICENSE`, o aviso no bundle (o Vite), os canários, o teste que falha com um `.map` no `dist/` | PI-4, PI-9 |
| **PI3: a borda** | o `robots.txt`, o aviso de mineração, as políticas da Cloudflare | a CN4 |
| **PI4: os termos e o INPI** | os termos de uso; o pedido no INPI, feito pelo Matheus (o certificado digital é dele) | a CN6 |

## 9. O que falta conferir

- O preço do minuto do runner Windows do GitHub e a cota do GitHub Pro.
- Se as políticas de robôs de IA da Cloudflare existem no plano Free.
- O protocolo TDMRep (o formato do cabeçalho e do arquivo).
- O preço do certificado digital ICP-Brasil e o que o e-Software pede do código (o código inteiro ou um resumo dele).
