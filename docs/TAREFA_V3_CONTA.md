# TAREFA V3 — CONTA (2026-11-11)

Coordenador: o Matheus, nesta sessão. Worker: Claude Code (Opus 5.5). Worktree e branch: `v3-conta`. Status: ABERTA (o plano entregue;
as CN-1 a CN-12 DECIDIDAS em 2026-11-11, a CN-12 revista e a CN-13 e a CN-14 DECIDIDAS em 2026-11-12; e as CN-15 a
CN-18 DECIDIDAS em 2026-11-12: todas as CN-n decididas).

Categoria: arquitetura. Origem: Matheus, 2026-11-11: planejar a conta (login, primeiro acesso, perfil), o save na nuvem entre aparelhos, a proteção contra raspagem e a infraestrutura de servidor.

O pedido, nas palavras dele: "o que a gente vai ter que adicionar em UX Design e também em infraestrutura do estado atual do projeto,
para, por exemplo, ter página de login, página de cadastro, essas coisas assim, que é padrão", e, sobre o save na nuvem entre aparelhos,
"Sim, entra".

## 1. Pergunta

O que o jogo web, que hoje é de um jogador e guarda o save no navegador, precisa ganhar em telas e em servidor para ter uma conta com
login, o mesmo pet em mais de um aparelho e uma proteção razoável contra a raspagem por robôs e agentes de IA, a um custo de projeto
pessoal?

Não vem de uma hipótese do `docs/PLANO_V2_PESQUISA.md`: é do produto (`docs/PRODUTO_VISAO.md`) e é a base do `docs/PLANO_V3_MMO.md`.
A pesquisa em Python não muda.

## 2. Depende de

- **Para o plano (esta entrega):** nada.
- **Para as etapas de código:** as decisões CN-1 a CN-14 (seção 12 do `docs/PLANO_V3_CONTA.md`); a CN-5 e a CN-6 mudam a MMO-4 e a
  MMO-2 aprovadas, e precisam do ok explícito do Matheus.

## 3. Mudança mínima

**Nesta entrega, só documentos:**
- `docs/PLANO_V3_CONTA.md`, o plano;
- esta tarefa;
- a seção do desvio em `docs/registro/2026-11.md`.

**O que não muda,** nesta entrega e em nenhuma etapa sem decisão própria: o `engine.py` e o Python; o motor do pet (`web/app/motor/`) e
o formato do save; as versões de pet antigas e os gabaritos; o `servidor/servidor_local.py` e as rotas dele.

## 4. Experimento e gate (se houver run)

Não há run. A etapa CN0 é uma medida de engenharia (o tamanho dos saves), não de pesquisa, e não usa faixa de sementes reservada.

## 5. Entrega

- Testes: nenhum nesta entrega (só documento). Cada etapa de código traz os seus.
- Registro: `docs/registro/2026-11.md`, seção "2026-11-11 — CONTA: o plano da conta e do save na nuvem". O índice
  `docs/REGISTRO_DESVIOS.md` fica com quem faz o merge (`python tools/gerar_indice_desvios.py`).
- PR contra a `main`, com o plano PROPOSTO e as decisões CN-n. Merge só pelo Matheus.

## 6. Fora desta tarefa

- **O código** de qualquer etapa: começa depois das decisões e das pranchas.
- **O ranking**, as sementes e as tabelas: são do `docs/PLANO_V3_MMO.md`.
- **Contratar** domínio, VPS ou qualquer serviço: é do Matheus, na CN5.
- **O parecer jurídico** sobre a LGPD.

## 7. Critérios de aceitação

- O `docs/PLANO_V3_CONTA.md` existe e tem: o que existe hoje; a conta e o login; as telas; a sessão e o banco; o save na nuvem (a
  sincronização, os dois aparelhos, a divergência, o que sincroniza, as versões, as cópias); a proteção; a infraestrutura com o custo
  estimado; o que muda no plano MMO; a privacidade; as etapas; os riscos; a monetização (os modelos, a receita e o lucro com 100 e 1 000 jogadores por dia); as decisões CN-n com a recomendação e o custo de errar.
- Cada número novo do plano está marcado PROPOSTO, SEM FONTE, ou tem a fonte dita.
- O corpo do PR passa em `python tools/verificar_relato.py --arquivo F --base origin/main`.

## 8. Precisa do Matheus

As decisões CN-1 a CN-14, na seção 12 do plano, cada uma com a recomendação e o custo de errar.

## A PI0: o CI enxuto (2026-11-12)

A primeira etapa do `docs/PLANO_V3_CONTA_PROTECAO.md`, antes de o repositório ficar privado (PI-1, PI-2). O relato saiu para o
`.github/workflows/verificar-relato.yml`, que roda em todo evento do PR; o `.github/workflows/verificar-pr.yml` roda o `testes` e o `web` só
quando chega um commit, e o `web` só liga a máquina quando o PR muda `web/app/`. Nenhuma conferência saiu: o filtro "só quando o Python
muda" foi descartado porque o `testes` confere os documentos (D-CONTA-27). A medida: 20 % das execuções repetiam o mesmo commit
(D-CONTA-28). A economia é estimada e ainda não cabe na cota grátis (D-CONTA-30).

## A CN0: a medida do save (2026-11-12)

A primeira etapa da F0 do `docs/ROADMAP_V3_CONTA.md`. O script `web/app/scripts/medir_cn0_save.ts` grava 18 vidas típicas no Node e mede o
save por dia de jogo (`web/app/scripts/medicoes/cn0_save.json`). Um dia manda de 0,6 a 23 kB cru (de 0,2 a 1,6 kB em brotli), e a TV é o
que mais pesa. As 37 chaves e três fora do padrão têm destino; o `-habitat` e o `-viagem` ficam no aparelho, e o `-anterior` sobe como o
pet do jogador (D-CONTA-34 a 36). O pet não envelhece com o jogo fechado (D-CONTA-38). O resultado está em `docs/RESULTADO_V3_CONTA_CN0.md`.

## A PI2: a licença, o aviso no build e os canários (2026-11-12)

A etapa PI2 do `docs/PLANO_V3_CONTA_PROTECAO.md` (PI-4 e PI-9). O `LICENSE` da raiz é "todos os direitos reservados", em português e
em inglês, e deixa os sprites e os nomes do Digimon UP fora da licença, com o crédito da seção 5.1 das `docs/UI_GUIDELINES.md`
(D-CONTA-39). Cada JS do build começa pelo aviso de autoria, posto por um plugin do `web/app/vite.config.ts` depois da minificação
(D-CONTA-40), e o `npm run build` reprova um build com `.map` ou sem o aviso (`web/app/scripts/conferir_build.ts`, D-CONTA-41). Os seis
canários ficam fora do motor, e a lista só no vault (D-CONTA-42).

## A CN1 local: o esqueleto do servidor (2026-11-12)

O item 2 da seção 9.2 do `docs/ROADMAP_V3_CONTA.md`, sem conta, sem nuvem. A pasta `servidor_web/` tem o servidor Node 24 + Hono em
TypeScript, com a `/saude` e a fala por LLM portada do `servidor/` no mesmo contrato que o jogo usa (`GET /api/fala/status`,
`POST /api/fala`) e com as mesmas regras: o catálogo fechado, o teto TOTAL em arquivo (o mesmo do Python), o modelo sem preço que não sobe,
a chave só no ambiente e o template quando não dá (D-CONTA-47, 50, 51). O catálogo e o gabarito dos testes são gerados do Python, e o
Vitest confere a paridade (D-CONTA-49). Ficaram de fora o Ollama, o alerta por e-mail, a fala livre e o `--remoto`; o `servidor/` não muda.
Dois achados: o id datado do modelo cai no preço mais caro da tabela (D-CONTA-52), e o Mega nunca usa a LLM (D-CONTA-53).

## A CN2 local: a conta no servidor (2026-11-16)

A conta do lado do servidor em `servidor_web/src/conta/`, sem os apps OAuth reais e sem nuvem. O banco SQLite pelo `node:sqlite`, com as
tabelas da seção 4 e três de apoio, migração pelo `PRAGMA user_version` e o arquivo fora do git (D-CONTA-60). O login atrás da interface
`Provedor`: o Google e o GitHub com `state` e PKCE, prontos para as chaves no ambiente e desligados sem elas; o provedor falso só no local,
para os testes e o `npm run dev` (D-CONTA-68). A sessão em cookie `httpOnly`, `SameSite=Lax`, `Secure` fora do local, com o CSRF e o CORS só
para a origem do jogo. As rotas do primeiro acesso (o apelido de um Rookie, a idade em duas opções, o aceite com a versão do rascunho,
D-CONTA-62), da conta, dos aparelhos, de sair, de baixar os dados e de apagar (na hora, D-CONTA-63); a lista de convidados por variável ou
tabela, com o e-mail do Google só na memória (D-CONTA-61). Ficaram de fora as telas, a sessão na `/fala` e trocar o apelido depois
(D-CONTA-67).

## A CN2 no jogo: as telas da conta (2026-11-17)

Pedido do Matheus: "Sim, as telas" (em resposta a "Começo as telas da conta no jogo?"). As telas seguem as pranchas aprovadas
(`docs/PLANO_UX_CONTA.md`, UX-CN-1 a 6) e falam com as rotas da CN2 local do `servidor_web`. Branch `v3-conta-telas`.

- **A chave:** só aparece no build com `VITE_DIGILAB_API` (a mesma da luta ranqueada). Sem ela, os Ajustes são os de sempre.
- **A porta:** a linha "Conta" no topo dos Ajustes ("sem conta" ou o apelido); a parte é `#/config/conta`. O "Entrar" do estado "só com
  a conta" da luta ranqueada leva a ela.
- **As telas:** Entrar (o que vai para o servidor, os provedores ligados, "Agora não"); os estados (abrindo a entrada, conferindo, não
  deu, fora da lista, menos de 18); o primeiro acesso (o apelido, a idade, o aceite com a versão); a troca do apelido (a lista fechada
  e o número sorteado); o perfil (o apelido, os aparelhos, baixar os dados, sair, apagar); apagar a conta ("Manter a conta" é o
  principal).
- **O código:** `web/app/src/conta/conta.ts` (o cliente, sem React), `web/app/src/conta/apiDoBuild.ts` (os endereços do build),
  `web/app/src/telas/config/TelaConta.tsx`, `web/app/src/estilo/conta.css` e `web/app/test/conta.test.ts` (24 testes com o servidor
  falso). A ida ao provedor é na mesma aba; a volta lê o `?conta=` do endereço uma vez e o tira.
- **O que não muda:** o motor, o registro e o save. A conta não guarda nada no navegador; a sessão é o cookie do servidor.
- **Conferido:** `npm run tipos`, `npm run build` e `npm test` (1 981 passaram, 3 pulados). No Chrome headless, com o `servidor_web`
  local e o provedor falso: sem conta, fora da lista, primeiro acesso, menos de 18, troca do apelido, conta criada, a linha dos Ajustes
  com o apelido, baixar os dados, sair, entrar de novo, apagar e "não deu"; a 1920, a 390 e a 360.
- **O que falta:** os Termos e a Privacidade não existem (CN6); a marca oficial dos provedores (UX-CN-3); a troca do apelido depois de
  criada a conta (UX-CN-6, sem rota no servidor); o Google e o GitHub de verdade; o e2e no repositório; o revisor de acessibilidade.
  Os desvios estão no registro (D-CONTA-104 a 113).

## A CN3 local: o save na nuvem (2026-11-20)

Pedido pela sessão da conta: a CN3, local e sem deploy, pela seção 5 e as telas 3 a 5 do plano, as CN-3 a CN-5, a medida da CN0 e a
prancha `docs/pranchas/ux-conta-nuvem/` (UX-NV-1 a 6 APROVADAS em 2026-11-20). Branch `v3-cn3`. Os desvios são D-CONTA-180 a 195.

- **A chave:** só com `VITE_DIGILAB_API` **e** `VITE_DIGILAB_NUVEM=1` no build. Desligada, o save sai byte a byte: o gabarito
  (`web/app/test/gabaritos/cn3_save_desligado.json`, o roteiro do `src/jogo.ts` com o SHA-256 de cada gravação) foi gravado no commit
  anterior ao código, e `test/nuvem_desligada.test.ts` confere.
- **O servidor** (`servidor_web/src/nuvem/nuvem.ts`, a migração 9): `GET /nuvem`, `POST /nuvem/levar`, `/nuvem/vez`, `/nuvem/sync`,
  `/nuvem/divergencia`, `GET /nuvem/pacote`, `/nuvem/historias`, `/nuvem/copias` e `POST /nuvem/copias/:id/restaurar`, com a sessão e o
  CSRF da conta. A sincronização é por eventos, com o hash do registro até a ponta firme (D-CONTA-182) e o replay do registro inteiro a
  cada escrita (422 para o que não reproduz). A vez por pacote, que expira em 10 min; a divergência guarda a outra história inteira até a
  escolha, e a não escolhida vai para Gerações e para as cópias; as cópias diárias e as do que sai do lugar ficam 30 dias. O "baixar os
  meus dados" traz a nuvem sem o registro; apagar a conta leva tudo.
- **O jogo:** o cliente puro (`web/app/src/nuvem/cliente.ts`, o protocolo em `protocolo.ts`, dividido com o servidor), a trava do "só ver"
  em `src/jogo.ts` (`travarAcoes`, D-CONTA-188) e as telas (`src/nuvem/NuvemRaiz.tsx`, `src/estilo/nuvem.css`): levar o pet, a conta que
  já tem pets ("Guardar os dois" marcada), o outro aparelho ("Jogar aqui" e "Só ver"), as duas histórias ("Decidir depois"), atualize o
  jogo, o servidor fora do ar (uma vez), entre de novo, o estado no lugar do "salvo" do relógio, as cópias com "Restaurar" em Ajustes ›
  Conta e as outras histórias em Diário › Gerações.
- **Os testes:** `servidor_web/test/nuvem.test.ts` (as rotas e o e2e dos quatro casos com dois aparelhos, duas instâncias do cliente do
  jogo contra o servidor de verdade no processo); `web/app/test/nuvem_trava.test.ts` e `nuvem_desligada.test.ts`; e
  `web/app/e2e_conta/nuvem.spec.ts`, os quatro casos no Chrome com dois contextos e o servidor de verdade no `route` (no `npm run
  e2e:conta`, que agora monta também `web/dist_nuvem/`).
- **O que falta:** o registro no armazenamento de objetos e o deploy (CN5); o grupo dos dois pets sem teste próprio; o sprite e a abertura
  só-para-ver das histórias em Gerações; o revisor de acessibilidade; as capturas a 1920 e 390 das telas no jogo; a velocidade do tempo ao
  abrir noutro aparelho (D-CONTA-38).

## A CN5: a hospedagem de teste, a parte do código (2026-11-20)

O código e o roteiro, sem contratar nada (a seção 6: contratar é do Matheus). O roteiro, com a ordem do que contratar, os segredos, a VPS, o
backup, os assets, o deploy e os preços do dia, está em `docs/infra/DEPLOY_CN5.md`. As decisões D-CONTA-197 a 205 estão em
`docs/registro/2026-11.md`, DECIDIDAS pelo Matheus em 2026-11-20 pela recomendação ("Aprovo as recomendações").

- **O servidor:** a borda `cloudflare` (`--borda`, `DIGILAB_BORDA`): só em `127.0.0.1`, só o pedido que passou pelo Cloudflare Tunnel, e a
  conta local não sobe (`servidor_web/src/app.ts`, `test/borda.test.ts`). Sem a opção, a regra de sempre.
- **A VPS** (`servidor_web/deploy/`): o systemd do servidor e do Litestream, a `litestream.yml` para o R2, os modelos dos `.env` (só os
  nomes), o `instalar.sh` (o Node e o Litestream conferidos por sha256, o `cloudflared`, o `ufw`), o `publicar.sh` (volta a versão se a
  `/saude` não responder) e o `restaurar.sh` (o ensaio e a restauração de verdade).
- **O jogo:** os assets por `src/baseAssets.ts` (`VITE_DIGILAB_ASSETS`; sem ela, o de sempre) e o envio ao R2 pela máquina do Matheus
  (`web/app/scripts/publicar_assets.ts`, com a assinatura SigV4 em `scripts/r2.ts`, conferida com o exemplo da AWS).
- **O CI:** `.github/workflows/publicar.yml`, desligado até a variável `DIGILAB_PUBLICAR = sim`: o servidor pelo SSH, depois o jogo no Pages.
- **O que falta:** o Matheus contratar e configurar (seção 2 do roteiro); o ensaio da restauração antes do primeiro convidado; o aviso da
  RC-7; as URLs assinadas (CN4); o Sentry (D-CONTA-200).
