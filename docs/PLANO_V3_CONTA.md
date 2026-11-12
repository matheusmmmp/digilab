# Plano da conta: login, save na nuvem, proteção e servidor (2026-11-11)

**Status:** PROPOSTO, sem código. As decisões CN-1 a CN-14 (seção 12) vão ao Matheus, cada uma com a recomendação e o custo de errar.
Todo número deste plano é **PROPOSTO, SEM FONTE**, salvo onde a fonte está dita. Os custos são **estimativas**: saem da tabela de preços
do `servidor/fala_llm.py` e de preços públicos que este plano não conferiu, e se conferem na etapa CN5, antes de contratar qualquer coisa.

**Origem:** o Matheus, em 2026-11-11, em três pedidos na mesma conversa:
- o levantamento da arquitetura para "diversas pessoas, diversos pets, tudo rodando em cloud", com "a questão de segurança,
  principalmente contra agentes e LLM roubando conteúdo do site", e "a melhor infraestrutura de servidor tanto questão de custo quanto
  também de desenvolvimento", "desde a LLM de fala quanto o processamento dos cérebros e as batalhas";
- o que falta em UX e em infraestrutura "para, por exemplo, ter página de login, página de cadastro, essas coisas assim, que é padrão";
- o save na nuvem entre aparelhos: "Sim, entra".

**Só no jogo.** A pesquisa em Python não muda, nem o `engine.py`, nem o motor do pet (`web/app/motor/`), nem o formato do save.

**A relação com o plano MMO** (`docs/PLANO_V3_MMO.md`, MMO-1 a MMO-19 aprovadas): este plano é a base que o MMO usa. Ele faz a conta,
o servidor e o save; o MMO faz a conferência dos pontos, as sementes ranqueadas e as tabelas. Duas decisões aprovadas do MMO mudam se este
plano for aprovado, e por isso vão de novo ao Matheus (CN-6 e CN-5): a **MMO-2** (começar no servidor local) e a parte da **MMO-4** que
apaga o log em 30 dias.

## 1. O que existe hoje

| peça | onde está | o que pesa para a conta |
|---|---|---|
| **o cérebro, o corpo, o mundo e a luta** | o motor TS (`web/app/motor/`), **no navegador do jogador** | o servidor não precisa simular nada. Ele só guarda e, para o ranking, confere pelo replay |
| **o save** | `web/app/src/save.ts`: `{semente, log, versao}` (e `grupo`, `foco` com os dois pets, v26) na chave `digilab-web-v21-sprites` do `localStorage` | o estado nunca é salvo, só o log. O log só cresce: sincronizar é mandar os eventos novos |
| **as outras chaves do navegador** | 37 chaves `CHAVE + "-..."` em `web/app/src/` (Tamer, guardados, Gerações, nível, tema, som, HUD, fala, lab…) | cada uma precisa de um destino: vai para a nuvem, fica no aparelho ou não sai (seção 5.4) |
| **o tempo** | `web/app/src/tempo.ts`: anda pelo relógio real com a aba aberta, na velocidade escolhida, com salto máximo de 1 h real por passo | **a conferir na CN0:** o que acontece com o pet entre fechar num aparelho e abrir no outro |
| **o replay** | `Motor.reproduzir`, sem DOM; uma vida de 166 a 234 lutas refaz em 67 a 76 ms no Node 24 (`web/app/scripts/medicoes/replay_lp2.json`, citado no plano MMO) | conferir no servidor é barato |
| **o MMO** | MMO0 (paridade Chrome × Node, #818) e MMO1 (a conta dos pontos, #824) na `main` | a conta e o servidor ainda não existem |
| **o servidor** | `servidor/servidor_local.py` (Python, biblioteca padrão e o SDK `anthropic`), na máquina do Matheus, só em `127.0.0.1`; `--remoto` para o túnel da Cloudflare com a senha HTTP Basic | entrega o jogo e a `/api/fala`; não guarda nada de jogador |
| **a fala** | a fala nasce da rede no cliente; a LLM é só a voz. `/api/fala` com o `claude-haiku-4-5` (padrão do `fala_llm.py`), o catálogo fechado e o teto de gasto total (`--limite-usd`, US$ 2) | numa conta pública, a rota vira alvo: um agente pode usá-la como LLM de graça |
| **os assets** | fora do git em `D:\Trab\digilab\Assets` (7,6 GB a pasta inteira); só uma parte é servida (a lista do `--remoto`) | é o conteúdo que um robô baixa em lote |

O que **não** existe: conta, login, sessão, banco, armazenamento de save, rota de sincronização, domínio próprio, ambiente de teste
separado, termos de uso e política de privacidade.

## 2. A conta e o login

- **Jogo primeiro, conta depois (CN-1).** O jogo abre direto na ilha, como hoje, e o save fica no navegador. A conta é para quem quer o
  pet em outro aparelho ou o ranking. É a regra do plano MMO ("sem conta, nada muda"), estendida ao save na nuvem.
- **Login só por provedor (CN-2), como a MMO-3:** "Entrar com Google" e "Entrar com GitHub". O jogo não guarda senha.
- **Não há "cadastro" tradicional.** Sem formulário de e-mail e senha, sem "esqueci a senha", sem confirmação de e-mail. O cadastro é o
  **primeiro acesso**: o apelido e o aceite (seção 3, tela 2).
- **Onde se entra:** pelo cais, o lugar que a progressão e o plano MMO deixaram para o multijogador, e por um item em Ajustes ("Conta"),
  porque o save na nuvem não depende do nível 10 do Tamer. O ranking continua do nível 10 em diante (MMO-13).

## 3. As telas (UX)

Cada tela começa pela prancha, que o Matheus aprova antes do código: desktop e celular juntos (a regra dos lugares da ilha), na pele dos
menus (Vidro por padrão, `--hx-*`), com pouco texto e os nomes do Digimon na tela.

| tela | o que tem | etapa |
|---|---|---|
| **1. Entrar** | o que vai para o servidor, em três linhas; "Entrar com Google", "Entrar com GitHub"; "agora não" | CN2 |
| **2. Primeiro acesso** | o apelido gerado (um nome de Digimon e um número, como no plano MMO), com a troca por uma lista fechada; o aceite dos termos e da privacidade, com a versão; a pergunta da idade (seção 9) | CN2 |
| **3. Levar o pet para a conta** | os pets deste aparelho (o ativo, os guardados, Gerações); se a conta já tem pets: "ficar com os deste aparelho", "ficar com os da nuvem" ou "guardar os dois" | CN3 |
| **4. Perfil e conta** | o apelido; os aparelhos ligados, com "desconectar"; as cópias do save, com "restaurar"; "baixar os meus dados"; "apagar a conta", com a confirmação e o aviso de que não volta; "sair". Com o MMO, as duas pontuações e os selos | CN2 e CN3 |
| **5. Os estados** | no HUD, um ícone discreto: sincronizado, enviando, offline (com a hora da última sincronização); o aviso "este pet está aberto em outro aparelho", com "jogar aqui"; a escolha da história quando divergir (seção 5.3); "atualize o jogo"; "servidor fora do ar, o jogo continua neste aparelho"; a sessão expirada | CN3 |
| **6. As páginas públicas** | uma página inicial curta, os termos, a privacidade e os créditos (a regra 5.1 das `docs/UI_GUIDELINES.md`) | CN6 |

**As rotas:** o app usa só rotas de hash (`#/pet/estado`, `src/rotas.ts`). O provedor do login precisa de um caminho real
(`/auth/callback`): o servidor trata esse caminho e devolve o jogador ao hash em que ele estava. As rotas do jogo não mudam.

## 4. A sessão e o banco

- **A sessão** num cookie `httpOnly`, `Secure`, `SameSite=Lax`, com a proteção contra CSRF nas rotas que mudam algo. Nada da sessão no
  `localStorage`.
- **O banco** (PROPOSTO): as tabelas `contas` (id, apelido, criada em, idade declarada), `identidades` (o provedor e o id dele),
  `consentimentos` (a versão dos termos e a data), `sessoes`, `aparelhos`, `pets` (o metadado da seção 5), `copias` e, com o MMO, os
  envios, as sementes entregues e as tabelas.
- **O log do pet não fica no banco:** fica no armazenamento de objetos (seção 7), comprimido, e o banco guarda o caminho, o tamanho e o
  hash.

## 5. O save na nuvem

### 5.1 Como sincroniza

O log só cresce, e o estado sai dele. Por isso a sincronização é **por eventos**, não por arquivo:
1. O aparelho guarda a posição do último evento que a nuvem confirmou e o hash encadeado até ali.
2. Ao sincronizar, manda só os eventos depois dessa posição, com o hash da posição.
3. O servidor confere que o hash bate com o dele, junta os eventos e devolve a posição nova.
4. Se o hash não bate, o log divergiu (seção 5.3).

O `localStorage` continua sendo a fonte do aparelho: o jogo funciona offline, e uma fila manda os eventos quando a conexão volta. O
servidor **pode** refazer o replay a cada sincronização, para recusar um log impossível. Para o save não é obrigatório (é o pet do
próprio jogador), mas é o mesmo código do ranking e acha um save corrompido cedo (CN-4).

### 5.2 Dois aparelhos: a vez

Um log que só cresce não se junta: dois aparelhos jogando ao mesmo tempo criam **duas histórias** do mesmo pet. A proposta (CN-3) é
**um aparelho com a vez por pet**:
- abrir o pet pede a vez ao servidor; quem tem a vez joga e sincroniza;
- os outros aparelhos abrem o pet só para ver, com "jogar aqui", que toma a vez;
- a vez expira sozinha depois de um tempo sem sinal (PROPOSTO: 10 min), para um aparelho que caiu não prender o pet;
- **offline**, o aparelho que tinha a vez continua jogando e sincroniza depois.

### 5.3 Quando as histórias divergem

Acontece quando dois aparelhos jogaram offline, ou quando um tomou a vez enquanto o outro estava sem rede. O jogador escolhe qual
história fica. **A outra não some:** vai para Gerações como uma cópia, só para ver, com a data e o aparelho. Nenhum evento é apagado sem
o jogador ver. A outra opção, "o último a enviar ganha", apaga a história de um aparelho em silêncio, e o plano não a recomenda.

### 5.4 O que sincroniza (CN-4)

| vai para a nuvem | fica no aparelho | não sai do aparelho |
|---|---|---|
| o save (`CHAVE`), os guardados (`-guardados`), Gerações (`-geracoes`), o registro do Tamer (`-tamer`: medalhas, Bits, itens), o nível (`-nivel`), a conclusão da Liga (`-conclusao-liga`), a mitologia (`-mitologia`, `-mitologia-ouvidas`), os descartados (`-descartados`, `-descarte`) | os ajustes de tela e som (`-tema`, `-pele`, `-som*`, `-hud*`), a aba, as dicas e os avisos já vistos | a fala e a conversa (`-fala-llm`, `-fala-rede`, `-modo-fala`, `-conversa-nova`), o pet do laboratório (`-lab*`) |

A lista é PROPOSTA e precisa de uma passada chave a chave na CN0 (por exemplo, `-habitat`, `-viagem` e `-anterior`). **A fala não sobe**
pela regra do `servidor/CLAUDE.md` (a fala nunca entra no registro do pet) e porque é o dado mais pessoal do jogo. **Os ajustes ficam no
aparelho** porque o celular e o PC pedem ajustes diferentes; a outra opção é subir também, com a troca por aparelho.

### 5.5 As versões

Um aparelho com o jogo desatualizado não pode mandar eventos de uma versão de pet que o servidor não conhece, nem abrir um pet de uma
versão que ele não tem. A regra "atualize o jogo" da MMO-14 vale também para a sincronização. As versões antigas de pet continuam
abrindo (a regra do `web/app/CLAUDE.md`).

### 5.6 As cópias

Uma cópia diária de cada save, guardada por 30 dias (PROPOSTO), para restaurar depois de um erro (o jogador escolheu a história errada,
um bug apagou o pet). Restaurar não apaga a versão de agora: ela vira uma cópia também.

## 6. A proteção contra raspagem e abuso

**O limite, dito antes:** o que chega ao navegador pode ser copiado. O código JS é sempre legível, e um agente que controla um navegador de
verdade tira uma captura de tela. A proteção encarece a cópia em lote; não a impede. O que é protegido de verdade fica no servidor.

| camada | o quê | contra o quê | etapa |
|---|---|---|---|
| **não publicar** | o servidor público entrega só as rotas do jogo, como o `--remoto` de hoje; a pesquisa, os docs, o Python, os artefatos e o vault nunca vão | o vazamento do que não é jogo | CN1 |
| **os segredos** | a chave da API, o segredo HMAC das sementes (MMO-6) e as chaves do OAuth só no ambiente do servidor; nada no JS | o roubo de chave, a trapaça | CN1 |
| **a borda** | na Cloudflare: o bloqueio de robôs de IA e o Bot Fight Mode, o limite de pedidos por IP, a regra contra as faixas de datacenter nas rotas de assets | a raspagem em lote | CN4 |
| **o `robots.txt`** | recusa os robôs de IA declarados (GPTBot, ClaudeBot, CCBot, Google-Extended…) | só os honestos, mas os grandes respeitam | CN4 |
| **os assets atrás da sessão** | o atlas, os sons e os pacotes por URL assinada e de vida curta, ligada à sessão ou a um visitante com o Turnstile; nada num caminho fixo que se baixa de uma vez | o download do atlas inteiro por um robô anônimo | CN4 |
| **a `/api/fala`** | só com sessão; uma cota de falas por conta e por dia (PROPOSTO: 30); o template quando a cota acaba; o teto de gasto total que já existe | o agente que usa a rota como LLM de graça | CN4 |
| **o Turnstile** | na entrada da conta e no primeiro pedido de assets de um visitante | as contas em massa, o robô sem navegador | CN4 |
| **a ofuscação** (CN-9, depois) | os atlas em pacote binário cifrado com a chave da sessão; uma marca d'água invisível por conta | a cópia por quem já entrou; saber de onde um vazamento saiu | depois |

O robô que joga dentro de um navegador real não se separa de uma pessoa. O que o segura são os limites pelo relógio do servidor
(MMO-8) e a cota da fala.

## 7. A infraestrutura

**A regra:** o servidor é **TypeScript no Node.** A conferência do ranking precisa do Node, porque a paridade medida na MMO0 é Chrome ×
Node; outro runtime (Workers, Deno, Bun) pede a medida de novo. E o motor já é TS: o servidor importa o mesmo `web/app/motor/`.

| papel | proposta (CN-7) | por quê |
|---|---|---|
| **o jogo e as páginas públicas** | Cloudflare Pages (arquivos estáticos do `npm run build`) | a borda da seção 6 vem junto |
| **os assets e os logs** | Cloudflare R2 | não cobra a saída de dados, e os assets são o grosso do tráfego |
| **a API** | Node 24 com Hono, numa VPS pequena (Hetzner ou equivalente), atrás da Cloudflare | um processo só para a conta, o save, a fala e, depois, o ranking; o Hono também roda em outros runtimes, se um dia valer |
| **o banco** | SQLite na VPS, com a cópia contínua para o R2 (Litestream) | um arquivo, sem serviço a mais; troca para Postgres gerenciado se um dia passar de uma máquina |
| **o login** | uma biblioteca de OAuth no próprio servidor (Arctic ou Auth.js) | nenhum serviço a mais; a outra opção é o Supabase (login, Postgres e arquivos juntos), mais rápido de montar e com mais dependência |
| **a fala** | a `/api/fala` portada para o SDK TS da Anthropic, no mesmo servidor, com as mesmas regras do `servidor/CLAUDE.md` | um servidor só. O Python continua para a pesquisa e para o jogo local |
| **o servidor local de hoje** | continua como está, para o desenvolvimento e o jogo na máquina do Matheus | nada dele muda |
| **os ambientes** | o de teste (convidados) e o de produção, separados, cada um com os seus segredos | a regra "o motor só muda na virada da semana" (MMO-14) pede um lugar para testar antes |
| **o deploy** | pelo CI, a partir da `main`, com o teste e o build antes | sem deploy à mão |
| **a observabilidade** | o log de erros do servidor e um painel de uso e de gasto da LLM | o alerta de gasto por e-mail (`servidor/alerta.py`) já existe e vem junto |

**O custo estimado por mês (PROPOSTO, SEM FONTE; conferir na CN5):**

| | 100 jogadores por dia | 1 000 jogadores por dia |
|---|---|---|
| Cloudflare (Pages, R2, Turnstile) | 0 a US$ 5 | US$ 5 a 15 |
| VPS | uns € 5 | € 10 a 20 |
| domínio | uns US$ 1 | uns US$ 1 |
| **a fala, com o `claude-haiku-4-5`** | uns US$ 60 (20 falas por jogador por dia, uns US$ 0,001 por fala) | uns US$ 600 |
| **a fala, com o `claude-haiku-5-5`** | uns US$ 6 | uns US$ 60 |

Os preços por token saem da tabela do `servidor/fala_llm.py` (`PRECOS_USD_POR_MTOK`); o tamanho de uma fala é estimado, não medido. **O
custo cresce pela fala, não pelo servidor.** Por isso a cota por conta da seção 6, o cache do prompt de sistema e o template quando a cota
acaba. Uma GPU própria para o Ollama custa da ordem de centenas de dólares por mês e não compensa nessa escala.

**Os cérebros e as lutas continuam no cliente.** O servidor só confere: com 70 ms por vida, uma VPS de 2 núcleos refaz, na conta crua, uns 2,4
milhões de vidas por dia (2 × 86 400 s / 0,07 s). Com uma folga larga para o resto do servidor, 100 mil por dia é seguro. Nada disso foi
medido na VPS.

## 8. O que muda no plano MMO

- **MMO-2 (onde fica o servidor):** a aprovada é começar no servidor local. Com o save na nuvem, a máquina do Matheus cair (WHEA 19, a
  regra dos 4 processos) deixa de ser só "o ranking fora do ar" e vira "o pet do jogador sem a nuvem". A proposta (CN-6) é começar
  numa VPS de teste, só com convidados.
- **MMO-3 (o login por provedor):** não muda.
- **MMO-4 (a privacidade):** o log do ranking continua apagado em 30 dias. O log do **save** passa a ficar enquanto a conta existir,
  porque é o próprio pet do jogador (CN-5).
- **MMO3 (a etapa "o servidor e a conta"):** passa a ser só a conferência e o envio para o ranking, sobre a conta e o servidor deste plano.

## 9. A privacidade

- **Entrar é escolha:** o jogo funciona sem conta. A tela 1 diz o que vai para o servidor.
- **O que vai:** o id da conta, o provedor e o id dele, o apelido, a idade declarada, os logs dos pets e do Tamer, os aparelhos (um nome
  e a última vez), as horas das sincronizações. **Não vão:** o nome, o e-mail (se o provedor o entregar, não se guarda; PROPOSTO), o lugar,
  a fala.
- **Quanto tempo fica (CN-5):** o save, enquanto a conta existir; as cópias, 30 dias; o log do ranking, 30 dias depois da semana (MMO-4);
  a conta apagada some com tudo em até 30 dias, com as cópias.
- **Os direitos:** baixar os dados e apagar a conta ficam na tela 4, sem pedido por e-mail.
- **Cifra:** os logs cifrados no armazenamento, e o tráfego só por HTTPS.
- **Os menores (CN-10):** um jogo de pet com Digimon atrai criança. A LGPD (art. 14) pede o consentimento de um dos pais para a criança
  e só o dado estritamente necessário (§ 4º). A proposta é **abrir só para convidados adultos até a revisão** por quem entende da lei,
  como a MMO-4 já pedia. **Este plano não é parecer jurídico.**

## 10. As etapas (um PR por etapa)

| etapa | o que entrega | depende de |
|---|---|---|
| **CN0: a medida** | um script que mede os saves do jogo web: o tamanho do log por dia de jogo, comprimido e não; a passada chave a chave da seção 5.4; o que o tempo faz entre fechar e abrir. Sem servidor e sem tela | nada |
| **CN1: o servidor** | o servidor Node + Hono em `servidor_web/` (PROPOSTO), com as rotas do jogo e a `/api/fala` portada, as mesmas regras do `servidor/CLAUDE.md`; roda local e na VPS de teste; sem conta ainda | CN-6, CN-7 |
| **CN2: a conta** | as pranchas das telas 1, 2 e 4; o OAuth, a sessão, o banco, o apelido, o aceite, apagar e baixar os dados | CN1, CN-1, CN-2, CN-10 |
| **CN3: o save na nuvem** | as pranchas das telas 3 e 5; a sincronização por eventos, a vez, a divergência, as cópias; atrás de uma chave desligada no app (desligada, o save de hoje não muda) | CN2, CN0, CN-3, CN-4, CN-5 |
| **CN4: a proteção** | o `robots.txt`, a borda na Cloudflare, os assets por URL assinada, a cota da fala, o Turnstile | CN1 (a cota da fala, CN2) |
| **CN5: a hospedagem de teste** | o domínio, a VPS, o R2, o deploy pelo CI, o backup, o painel; os custos da seção 7 conferidos com os preços do dia | CN1 a CN4; o Matheus contrata |
| **CN6: abrir** | as páginas públicas (tela 6), os termos e a privacidade; a revisão da LGPD; só depois, fora dos convidados | CN5, a revisão |
| **CN7: o apoio** (só se a CN-11 for aprovada) | a seção 13.4: o processador, a tabela `apoios`, as telas do apoio e as páginas de venda; a doação pode vir antes, sem código, por um link | CN6, CN-11 a CN-14 |

O MMO segue as etapas dele sobre esta base: a MMO3 (o envio e a conferência) depois da CN2.

## 11. Os riscos

| risco | o que se vê | o que segura |
|---|---|---|
| **a divergência entre aparelhos** | o jogador perde o que fez num aparelho | a vez por pet; a outra história vai para Gerações; as cópias de 30 dias |
| **o save corrompido na nuvem** | o pet não abre em nenhum aparelho | o replay na sincronização acha cedo; as cópias; o `localStorage` do aparelho continua |
| **uma versão nova do motor** | um aparelho desatualizado manda eventos que o servidor não lê | "atualize o jogo" antes de sincronizar; as versões antigas continuam abrindo |
| **o gasto da fala** | um robô ou um jogador gasta o crédito | a sessão obrigatória, a cota por conta, o teto total, o alerta por e-mail |
| **a raspagem dos assets** | o atlas baixado em lote | a borda, as URLs assinadas, o Turnstile; não some de todo (seção 6) |
| **o custo de manter** | conta, backup, deploy e suporte tomam o tempo da pesquisa | etapas pequenas, um servidor só, SQLite, o jogo sem conta seguindo igual |
| **a privacidade e os menores** | dado de comportamento e de criança num servidor | entrada por escolha, o mínimo de dados, só convidados adultos até a revisão |
| **a dependência de provedores** | a Cloudflare ou a VPS mudam de preço ou caem | o servidor em Node padrão e o SQLite com cópia: mudar de provedor é um deploy, não uma reescrita |

## 12. Decisões para o Matheus

Cada uma com a recomendação e o custo de errar. **Todas PROPOSTAS.**

- **CN-1. Quando a conta aparece:** **o jogo primeiro, a conta depois** (pelo cais e por Ajustes). A outra opção é o login na entrada.
  Custo de errar: alto. O login obrigatório espanta quem quer só experimentar e quebra o jogo de hoje, que funciona sem servidor.
- **CN-2. Como se entra:** **Google e GitHub, sem senha**, como a MMO-3. A outra opção é acrescentar o link por e-mail, para quem não tem
  uma das duas contas. Custo de errar: baixo a médio. O link por e-mail pede um serviço de envio e a entrega dos e-mails; a senha guardada
  é o pior caso.
- **CN-3. Dois aparelhos:** **a vez por pet**, com a vez que expira e a escolha da história quando divergir, e a outra em Gerações. A
  outra opção é "o último a enviar ganha". Custo de errar: alto. O último a enviar apaga a história de um aparelho sem avisar.
- **CN-4. O que sincroniza:** a tabela da seção 5.4: o save, o Tamer e os pets sobem; os ajustes ficam no aparelho; a fala e o lab não
  saem. E **o replay na sincronização**, recomendado. Custo de errar: médio. Subir a fala põe o dado mais pessoal num servidor; não subir o
  Tamer separa as medalhas do pet.
- **CN-5. Quanto tempo guardar:** o save enquanto a conta existir; as cópias por 30 dias; o log do ranking 30 dias depois da semana; a
  conta apagada some em até 30 dias. **Muda a MMO-4** só no log do save. Custo de errar: médio. Apagar o save em 30 dias desfaz o save na
  nuvem; guardar tudo para sempre guarda dado de comportamento sem razão.
- **CN-6. Onde começa:** **numa VPS de teste, só com convidados**, no lugar do servidor local. **Muda a MMO-2.** A outra opção é a MMO-2
  como foi aprovada. Custo de errar: médio. Em casa, a máquina instável leva o save junto; fora, há um custo pequeno por mês antes de
  saber se a conta pega.
- **CN-7. A pilha:** **Node 24 + Hono numa VPS, SQLite com a cópia no R2, o login no próprio servidor, a Cloudflare na frente.** A
  outra opção é o Supabase para o login, o banco e os arquivos, com a VPS só para a conferência. Custo de errar: médio. O Supabase monta
  mais rápido e prende mais; a pilha própria é mais barata e pede mais código no começo.
- **CN-8. A fala na nuvem:** a `/api/fala` portada para TS, só com sessão, **30 falas pela LLM por conta e por dia** (PROPOSTO) e o
  template depois; o modelo é o de hoje (`claude-haiku-4-5`) até uma decisão própria de voz. Custo de errar: médio. Sem cota, um robô
  gasta o teto; com a cota baixa demais, a voz some cedo.
- **CN-9. A proteção:** **as camadas da seção 6 até o Turnstile, na CN4**; a ofuscação dos atlas e a marca d'água por conta ficam para
  depois, se a cópia aparecer. Custo de errar: baixo a médio. Sem a borda, o atlas sai em lote; a ofuscação cedo gasta tempo contra quem
  ainda não apareceu.
- **CN-10. Os menores:** **só convidados adultos até a revisão da LGPD**, com a pergunta da idade no primeiro acesso. Custo de errar:
  alto, se abrir para crianças sem a revisão.

- **CN-11. Reabrir o "sem dinheiro real, nunca":** a regra está no `docs/PLANO_V3_MOEDA.md` (seção 5 e "fora do plano"), no
  `docs/PLANO_V3_MMO.md` (seções 7 e 15) e na primeira versão deste plano. **Recomendo reabrir só para o apoio e o cosmético** (seção
  13.1), mantendo no "nunca" a venda de Bits, de stats, de chips, de tempo e de vantagem no ranking, e o gacha e a caixa de prêmio. A outra
  opção é manter a regra como está. Custo de errar: alto. Vender vantagem desfaz a M-2 e o ranking (MMO-7); manter o "nunca" deixa o
  custo da seção 7 todo com o Matheus.
- **CN-12. O modelo:** **o híbrido apoio + cosméticos** (a assinatura "Apoiador" e os enfeites avulsos, seção 13.2, linha E), **sem
  anúncios**. A outra opção mais simples é só a doação (linha D). Custo de errar: médio. Os anúncios rendem pouco nesta escala, pioram a
  ilha e trazem a questão dos menores; a assinatura sem nada que se veja vende pouco.
- **CN-13. Quando começa:** **a doação logo que a CN6 abrir para os convidados; a assinatura e os cosméticos só depois**, com o
  número de jogadores por dia medido (PROPOSTO: a partir de 300 por dia). Custo de errar: médio. Cobrar cedo demais monta um caixa, a nota
  fiscal e o suporte para dez pessoas.
- **CN-14. A formalização:** o recebimento por um processador com Pix e cartão (Mercado Pago ou Stripe) e **a conversa com um contador
  antes do primeiro real** (pessoa física ou CNPJ, o imposto). Custo de errar: alto, se receber sem ver o imposto.

## 13. A monetização

**Origem:** o Matheus, em 2026-11-11: "um módulo referente a modelos de monetização em sistemas de jogos assim e quanto seria baseado em
100 jogadores por dia e 1000 jogadores por dia [...] Quanto que geraria de lucro?"

**Status:** PROPOSTO, e **reabre uma regra decidida.** Os Bits foram aprovados com "sem dinheiro real, nunca" (M-1 a M-10), e o plano MMO
repetiu a regra. Nada desta seção vale sem a CN-11. **Todos os números são PROPOSTOS, SEM FONTE:** as taxas de conversão, os valores
por jogador e os preços dos anúncios saem de blogs de fornecedores e de guias de mercado (seção 13.5), que discordam entre si e não são
referências verificadas. Servem para a ordem de grandeza, não para um orçamento.

### 13.1 O que pode e o que nunca pode ser vendido

| pode (se a CN-11 for aprovada) | nunca |
|---|---|
| **o apoio:** a assinatura "Apoiador" e a doação avulsa | os **Bits** (continuam só jogando, M-1 a M-10) |
| **os enfeites da ilha** só do apoio (o padrão cartoon, só objetos da ilha) | **stats, chips, itens de luta, tempo** (pular espera, acelerar além do de hoje) |
| **a voz:** uma cota maior de falas pela LLM (a CN-8 dá 30 por dia; o apoiador, mais) | **vantagem no ranking**: o MMO-7 continua; quem paga e quem não paga lutam igual |
| **o selo de apoiador** no perfil | **o gacha, a caixa de prêmio**, qualquer sorteio pago |
| | **acréscimo no desenho do Digimon** (a regra "poses sem acréscimos") |
| | **cobrança de criança**: só adultos pagam (a CN-10) |

**A voz no apoio** casa a receita com o custo: a fala é o que mais pesa na conta da seção 7, e quem fala mais é quem paga por ela.

### 13.2 Os modelos e a receita por mês

As premissas (PROPOSTAS, SEM FONTE):
- **jogadores no mês = 5 × jogadores por dia** (a razão DAU/MAU de 0,2, comum nos guias de mercado). 100 por dia são uns 500 no mês; 1
  000 por dia, uns 5 000;
- **o mês tem 30 dias**; o dólar fica em dólar (a conversão para real muda todo dia);
- **as taxas:** uns 10 % para o processador nos pagamentos pequenos (a parte fixa por cobrança pesa num valor de US$ 4) e uns 10 % de
  imposto. **O imposto real depende da forma de receber (CN-14) e é do contador, não deste plano.** Nos anúncios, só o imposto.

| | o modelo | a premissa | receita bruta: 100 por dia | receita bruta: 1 000 por dia |
|---|---|---|---|---|
| **A** | **anúncios recompensados** (o jogador escolhe ver, por um enfeite ou falas) | 2 por jogador por dia, US$ 2 a 4 por mil vistos (eCPM da web) | US$ 12 a 24 | US$ 120 a 240 |
| **B** | **assinatura "Apoiador"** | US$ 4 por mês, 1 % a 3 % dos jogadores do mês | US$ 20 a 60 | US$ 200 a 600 |
| **C** | **enfeites avulsos** | US$ 0,01 a 0,03 por jogador por dia (bem abaixo da faixa dos jogos casuais, que compram tráfego e têm uma loja inteira) | US$ 30 a 90 | US$ 300 a 900 |
| **D** | **doação** (Apoia.se, Ko-fi, Catarse) | 0,5 % a 1 % dos jogadores do mês, US$ 5 por mês | US$ 12 a 25 | US$ 125 a 250 |
| **E** | **híbrido B + C** (recomendado, CN-12) | as duas linhas juntas | US$ 50 a 150 | US$ 500 a 1 500 |
| **F** | **jogo pago** (compra única) | não se compara por jogadores por dia: depende de quantos chegam novos por mês | — | — |
| **G** | **um portal** (Poki, CrazyGames) | o portal traz jogadores e paga uma parte dos anúncios (40 % a 60 %, sem número público confiável) | muda o número de jogadores, não a conta por jogador | |

### 13.3 O lucro por mês

A receita líquida tira as taxas de 13.2. Os custos são os da seção 7: a infraestrutura (a Cloudflare, a VPS, o domínio) mais a fala.

| | 100 por dia | 1 000 por dia |
|---|---|---|
| **custo**, com a fala no `claude-haiku-5-5` | US$ 13 a 18 | US$ 77 a 98 |
| **custo**, com a fala no `claude-haiku-4-5` (o padrão de hoje) | US$ 67 a 72 | US$ 617 a 638 |
| **E (híbrido)**, a receita líquida | US$ 40 a 120 | US$ 400 a 1 200 |
| **E, o lucro**, fala no Haiku 5.5 | **uns US$ 22 a 107** | **uns US$ 300 a 1 120** |
| **E, o lucro**, fala no Haiku 4.5 | **uns −US$ 32 a +US$ 53** | **uns −US$ 240 a +US$ 580** |
| **A (só anúncios)**, o lucro, fala no Haiku 5.5 | **uns −US$ 7 a +US$ 9** | **uns US$ 10 a 140** |
| **D (só doação)**, o lucro, fala no Haiku 5.5 | **uns −US$ 8 a +US$ 7** | **uns US$ 2 a 123** |

**A leitura:**
- **Com 100 jogadores por dia, nenhum modelo dá renda.** No melhor caso, paga o servidor e sobra pouco. A doação e os
  anúncios mal empatam.
- **Com 1 000 por dia, o híbrido paga tudo e sobra de umas centenas até uns mil dólares por mês**, se a conversão ficar na faixa de cima.
- **O modelo da voz decide se dá lucro ou prejuízo.** Com o Haiku 4.5, o custo da fala come o híbrido nos dois tamanhos, e o resultado pode
  ser negativo. Por isso a cota da CN-8 e a voz maior só para o apoiador.
- **O lucro não conta o tempo do Matheus** (o suporte, a loja, a contabilidade) nem a aquisição de jogadores: os 100 ou 1 000 por dia
  têm de chegar de algum lugar, e os jogos casuais que chegam a esses números costumam pagar por eles.

### 13.4 O que entra no código e na infraestrutura (a etapa CN7, depois da CN6)

- **O processador:** o checkout do Mercado Pago ou do Stripe (Pix e cartão), com a confirmação por webhook no servidor. **O jogo nunca
  vê o cartão.**
- **No banco:** a tabela `apoios` (a conta, o plano, a validade, o id do processador). O apoio é do Tamer, não do pet, e não entra no log
  do pet nem no do Tamer: **o motor não sabe quem pagou** (o replay e o ranking ficam iguais para todos).
- **As telas** (com a prancha antes): "Apoiar" no perfil (tela 4); a vitrine dos enfeites do apoio na loja do carro, marcada à parte dos
  Bits; o recibo; "cancelar", com um clique.
- **As páginas públicas:** os termos de venda, o reembolso e o arrependimento de 7 dias (Código de Defesa do Consumidor, art. 49, na compra
  pela internet).

### 13.5 As fontes de mercado (não verificadas)

São blogs de fornecedores e guias; os números discordam entre si, e nenhum é uma referência verificada (a regra do `CLAUDE.md`). Lidas
em 2026-11-11:
- valor por jogador por dia (ARPDAU) por gênero: <https://www.juegostudio.com/blog/arpdau-benchmarks-by-game-genre>,
  <https://blog.playio.co/arpdau-benchmarks-mobile-games>, <https://metricstree.vercel.app/en/blog/arpdau-mobile-games>;
- a conversão de pagantes: <https://blog.playio.co/arppu-mobile-games>, <https://appfollow.io/blog/mobile-game-kpis>;
- os anúncios na web e os portais: <https://docs.crazygames.com/resources/ad-monetization-guide/>,
  <https://www.applixir.com/?p=4428>, <https://app.cinevva.com/guides/web-game-monetization>,
  <https://app.cinevva.com/guides/publish-game-poki>.

### 13.6 Os riscos próprios

| risco | o que se vê | o que segura |
|---|---|---|
| **pagar para ganhar por um atalho** | um enfeite ou uma fala paga muda o pet | o apoio fica fora dos logs; o motor não sabe quem pagou; a tabela 13.1 |
| **a voz paga sai mais cara do que rende** | o apoiador fala muito no modelo caro | a cota do apoiador também tem teto; o teto total de gasto continua |
| **os sprites e os nomes do Digimon** | o jogo usa o desenho do Digimon UP com o crédito (a regra 5.1 das `docs/UI_GUIDELINES.md`); cobrar por um jogo com uma marca de outra empresa muda o tamanho do risco, mesmo que só os enfeites próprios sejam vendidos | **vai na conversa da CN-14**, com quem entende de direito autoral, antes do primeiro real. Este plano não é parecer jurídico |
| **a criança paga** | uma compra sem o responsável | só adultos pagam (a CN-10); o processador pede o titular |
| **o imposto e o reembolso** | uma cobrança sem nota, um pedido de reembolso sem regra | a CN-14; os termos de venda; o arrependimento de 7 dias |

## 14. Fora deste plano

- O ranking, as sementes e as tabelas: são do `docs/PLANO_V3_MMO.md`.
- A troca entre jogadores, o chat livre e a luta ao vivo (como no plano MMO).
- A venda de Bits, de stats, de tempo ou de vantagem, o gacha e a caixa de prêmio: nunca. O dinheiro real só entra pela seção 13, se a
  CN-11 for aprovada.
- O aplicativo de loja (Android ou iOS): o jogo segue no navegador.
- Qualquer mudança no Python, no `engine.py`, no motor do pet ou no formato do save.
