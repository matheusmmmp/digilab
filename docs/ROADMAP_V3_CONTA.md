# Roadmap da conta, da nuvem e do multijogador (2026-11-12)

**Status:** PROPOSTO. Junta numa ordem só as etapas dos planos já decididos; não decide nada novo de produto. A ordem, os prazos e os custos
são **PROPOSTOS, SEM FONTE**; os prazos são em semanas de trabalho do projeto, não em datas. As decisões RC-1 a RC-4 (seção 7) são só
sobre a ordem.

**Origem:** o Matheus, em 2026-11-12: "Como começar essa estrutura toda, monte um roadmap para projeção dessa arquitetura".

**Os planos que este roadmap ordena:**
- `docs/PLANO_V3_CONTA.md`: a conta, o save na nuvem, a proteção do site, a infraestrutura e a monetização (CN-1 a CN-18, DECIDIDAS;
  etapas CN0 a CN7);
- `docs/PLANO_V3_CONTA_HOSPEDAGEM.md`: os provedores (CH-1 a CH-7, DECIDIDAS: Lightsail em São Paulo, Cloudflare Pages e R2, SQLite com
  o Litestream);
- `docs/PLANO_V3_CONTA_PROTECAO.md`: a propriedade intelectual (PI-1 a PI-9, DECIDIDAS; a PI0 na `main`, #897);
- `docs/PLANO_V3_MMO.md`: o ranking, a luta ranqueada e o desafio do dia (MMO-1 a MMO-19, APROVADAS; a MMO0 e a MMO1 na `main`);
- `docs/PLANO_UX_CONTA.md`: as pranchas da conta (UX-CN-1 a 6, APROVADAS, #882) e a prancha da página de entrada.

## 1. Onde estamos (2026-11-12)

| peça | situação |
|---|---|
| o jogo | pronto para um jogador, no navegador; o save no `localStorage` |
| as decisões | todas tomadas: CN-1 a 18, CH-1 a 7, PI-1 a 9, MMO-1 a 19, UX-CN-1 a 6 |
| o que já tem código | a MMO0 (a paridade Chrome × Node), a MMO1 (a conta dos pontos), a PI0 (o CI enxuto) |
| as pranchas | a conta (entrar, primeiro acesso, ajustes, apagar) e a página de entrada, aprovadas; faltam as do save na nuvem (a tela 3, levar o pet, e a tela 5, os estados) |
| o servidor | só o `servidor/servidor_local.py`, na máquina do Matheus |
| o repositório | **público**; a troca para privado (PI1) espera o Matheus |

## 2. As fases

Cada fase termina num **portão**: o critério que precisa valer antes da próxima. Um PR por etapa, como sempre; o merge é do Matheus.

```mermaid
flowchart LR
  F0["F0 · A base<br/>PI1 · PI2 · CN0 · MMO2"] --> F1["F1 · O servidor<br/>CN1 · CN5"]
  F1 --> F2["F2 · A conta<br/>CN2 · CN4 · PI3"]
  F2 --> F3["F3 · O save na nuvem<br/>CN3"]
  F3 --> F4["F4 · Os convidados<br/>a medida"]
  F2 --> F5["F5 · O multijogador<br/>MMO3 a MMO8"]
  F4 --> F6["F6 · A abertura<br/>CN6 · PI4"]
  F5 --> F6
  F6 --> F7["F7 · O apoio<br/>CN7"]
```

### F0 · A base (sem servidor, sem custo novo) · 1 a 2 semanas

| etapa | o que entrega | quem | depende de |
|---|---|---|---|
| **PI1** | o repositório privado e o teto de gasto do Actions (PI-2: US$ 20 por mês) | **o Matheus**, nas configurações do GitHub | a PI0 (na `main`) |
| **PI2** | o `LICENSE` "todos os direitos reservados", o aviso de autoria no bundle, os canários, o teste que falha com um `.map` no `dist/` | uma sessão | nada |
| **CN0** | a medida dos saves do jogo web: o tamanho do log por dia de jogo, comprimido e não; a passada chave a chave do `localStorage` (a seção 5.4 do plano da conta); o que o tempo faz entre fechar e abrir | uma sessão | nada |
| **MMO2** | o marco do nível 10 e o nível no registro do Tamer (a versão nova do Tamer) | a frente MMO | os Bits na `main` (#765) |
| as pranchas que faltam | a tela 3 (levar o pet para a conta) e a tela 5 (os estados: sincronizado, offline, "aberto no outro aparelho", a escolha da história) | a frente UX | nada |

**Portão F0:** o repositório privado com o CI andando; a CN0 diz o tamanho do log e fecha a lista do que sincroniza; as pranchas das telas 3
e 5 aprovadas. **As quatro etapas correm em paralelo**, cada uma na sua sessão.

### F1 · O servidor · 2 a 3 semanas

| etapa | o que entrega | quem | depende de |
|---|---|---|---|
| **CN1** | o servidor Node 24 + Hono (em `servidor_web/`, PROPOSTO), com as rotas do jogo e a `/api/fala` portada para o SDK TS, com as regras do `servidor/CLAUDE.md` (o catálogo fechado, o teto de gasto); roda local e na VPS | uma sessão | F0 |
| **CN5, a parte da conta da AWS** | a conta da AWS, o Lightsail de 2 GB em São Paulo, o domínio, a Cloudflare na frente (o DNS, o Pages para o build, o R2 para os assets), o Sentry e o Better Stack; os preços da seção 8 do plano da hospedagem conferidos no dia | **o Matheus** contrata; uma sessão monta o deploy pelo CI | a CN1 rodando local |

**Portão F1:** o jogo abre pelo domínio, servido pela Cloudflare; a fala responde pela VPS; o deploy sai da `main` pelo CI; o Better Stack
avisa se a VPS cair. **Custo a partir daqui: uns US$ 14 a 15 por mês, mais a fala** (seção 6 do plano da hospedagem).

### F2 · A conta · 2 a 3 semanas

| etapa | o que entrega | quem | depende de |
|---|---|---|---|
| **CN2** | o OAuth com Google e GitHub, a sessão no cookie, o SQLite com o Litestream para o R2, o apelido, o aceite, a idade, a lista de convidados, apagar e baixar os dados; as telas pelas pranchas aprovadas (#882) | uma sessão | F1; **o Matheus** cria os apps OAuth no Google e no GitHub |
| **CN4** | a cota da fala por conta (CN-8, CN-16), o Turnstile, os assets por URL assinada | uma sessão | a CN2 (a cota precisa da conta) |
| **PI3** | o `robots.txt`, o aviso de mineração reservada, as políticas de robôs de IA da Cloudflare | uma sessão | a CN5 (a Cloudflare na frente) |

**Portão F2:** um convidado entra com Google ou GitHub, escolhe o apelido, aceita e apaga a conta; a fala só responde com sessão e para na
cota; um robô sem sessão não baixa o atlas.

### F3 · O save na nuvem · 3 a 4 semanas

| etapa | o que entrega | quem | depende de |
|---|---|---|---|
| **CN3** | a sincronização por eventos com o hash encadeado, a vez por pet, a divergência com a outra história em Gerações, as cópias diárias de 30 dias, o replay na sincronização; atrás de uma chave desligada no app (desligada, o save de hoje não muda) | uma sessão (a etapa mais longa) | F2, a CN0, as pranchas das telas 3 e 5 |

**Portão F3:** o mesmo pet abre no PC e no celular; jogar offline num aparelho e voltar não perde nada; a divergência mostra a escolha;
restaurar uma cópia funciona. O e2e cobre os quatro casos.

### F4 · Os convidados · 2 a 4 semanas de uso

Não é uma etapa de código: é o tempo de os convidados jogarem com a conta e o save na nuvem, no ambiente único (CH-7). **O que se mede:**
os minutos do CI depois da PI0, o uso da VPS (a CPU contra a linha de 20 % do Lightsail), o tamanho dos logs no R2, o gasto da fala por
conta, os erros no Sentry.

**Portão F4:** duas semanas sem perder save; a CPU da VPS abaixo da linha na maior parte do tempo; o gasto da fala por jogador conhecido,
para a cota da CN-16 e o modelo da voz.

### F5 · O multijogador · 6 a 10 semanas, em paralelo com F3 e F4

As etapas do `docs/PLANO_V3_MMO.md`, sobre a conta da F2. Cada uma com a sua prancha.

| etapa | o que entrega | depende de |
|---|---|---|
| **MMO3** | o envio dos logs e a conferência pelo replay no Node (a conta e o servidor já existem) | a CN2, a MMO1 |
| **MMO4** | a luta ranqueada: a semente do servidor, a semente pedida contando como luta, o limite por dia | a MMO3; a luta equilibrada (a LP5 na `main`) |
| **MMO5** | o ranking da semana, por estágio, com o segredo publicado no fim | a MMO4 |
| **MMO6** | o desafio do dia (a Fábrica com as sementes de fora, atrás de chave) | a MMO3 |
| **MMO7** | os títulos, os selos, o enfeite da temporada, o mural | a MMO5, a MMO6 |
| **MMO8** | as duas pontuações e o reset com bônus | a MMO2, a MMO5 |

**Portão F5:** uma semana inteira de ranking com os convidados, sem divergência entre o que o cliente mostra e o que o servidor conta.

### F6 · A abertura · 2 a 4 semanas (boa parte fora do código)

| etapa | o que entrega | quem |
|---|---|---|
| **CN6** | as páginas públicas (a página de entrada, a prancha já aprovada), os termos de uso e a política de privacidade | uma sessão escreve; **o Matheus** aprova |
| **a revisão da LGPD** | o consentimento, os menores (CN-10), a transferência internacional | **quem entende da lei**; o Matheus contrata |
| **PI4** | o registro no INPI (R$ 210, o certificado ICP-Brasil); os termos contra a raspagem | **o Matheus** |
| **os ambientes** | o de produção separado do de teste (CH-7 previa um só até aqui); uma segunda VPS ou o mesmo Lightsail maior | **o Matheus** contrata; uma sessão monta |

**Portão F6:** a revisão da LGPD feita; o INPI pedido; os termos publicados. **Só então o jogo sai da lista de convidados.**

### F7 · O apoio · depois da abertura

| etapa | o que entrega | quando |
|---|---|---|
| **a doação** | um link (Apoia.se, Ko-fi ou Catarse), sem código | na abertura (CN-13) |
| **CN7** | a assinatura "Apoiador" (o processador com Pix e cartão, o webhook, a tabela `apoios`) e o anúncio que destrava a voz (o recompensado, a rede da CN-17), com a medida do eCPM real | com o número de jogadores medido (CN-13: uns 300 por dia) e o contador antes do primeiro real (CN-14) |

## 3. O que só o Matheus faz

Em ordem de quando aparece:
1. **F0:** trocar o repositório para privado e pôr o teto de gasto do Actions (PI1).
2. **F1:** abrir a conta da AWS (o Lightsail), comprar o domínio, abrir a conta da Cloudflare, criar a chave da API da Anthropic do servidor.
3. **F2:** criar os apps OAuth no Google Cloud e no GitHub (as chaves vão só para o ambiente do servidor).
4. **F2:** a lista de convidados.
5. **F6:** contratar a revisão da LGPD; pedir o certificado digital e o registro no INPI; aprovar os termos.
6. **F7:** falar com o contador; abrir o processador de pagamento e pedir a rede de anúncios.

## 4. O custo por fase (estimado, PROPOSTO)

| fase | o que entra no custo | por mês |
|---|---|---|
| F0 | o teto do CI | até US$ 20 (o uso real depois da PI0 ainda não foi medido) |
| F1 a F4 | o Lightsail, o snapshot, o domínio, a Cloudflare e o R2 grátis, o monitoramento grátis, mais a fala | uns US$ 14 a 15 + a fala + o CI |
| F5 | o mesmo (o replay cabe na mesma VPS) | o mesmo |
| F6 | a segunda VPS ou o Lightsail de 4 GB; a revisão jurídica e o INPI são custos únicos | uns US$ 26 a 40 + a fala + o CI; R$ 210 do INPI e o certificado, uma vez |
| F7 | as taxas do processador (uns 10 %); a receita da seção 13 do plano da conta | — |

## 5. O que corre em paralelo

- **Agora:** a PI1 (o Matheus), a PI2, a CN0, a MMO2 e as pranchas das telas 3 e 5: cinco coisas independentes.
- **Depois da F2:** a F3 (o save) e a F5 (o MMO) correm juntas, em sessões separadas: tocam arquivos diferentes (o save no app e no
  servidor; o ranking no `web/app/src/ranking/` e nas rotas do ranking).
- **A F6 começa cedo no que não é código:** a revisão da LGPD e o certificado do INPI levam semanas para sair; pedir durante a F3 encurta
  o caminho até a abertura.

## 6. Os riscos do caminho

| risco | o que se vê | o que segura |
|---|---|---|
| **o CI no privado** | o teto acaba antes do fim do mês e os merges travam | a PI0 já cortou as repetições; medir na F0; subir o teto se precisar |
| **a CN3 é a mais difícil** | a divergência entre aparelhos perde eventos | a chave desligada, o e2e dos quatro casos, as cópias de 30 dias, a F4 inteira de uso antes de abrir |
| **a paridade Chrome × Node** | o ranking conta diferente do que o jogador viu | a MMO0 mediu; o servidor manda e explica (MMO-5) |
| **o custo da fala** | o gasto cresce mais que o previsto | a cota da CN-16, o teto total, o painel na F4 |
| **o tempo do projeto** | a infraestrutura come o tempo da pesquisa e do jogo | uma fase por vez; o jogo sem conta continua igual em todas as fases |

## 7. Decisões para o Matheus

Só sobre a ordem; o resto já está decidido nos planos.

- **RC-1. Começar pela F0 agora, com as cinco frentes em paralelo.** A outra opção é ir direto à CN1 (o servidor). Custo de errar: baixo.
  Sem a CN0, a CN3 desenha a sincronização sem saber o tamanho do log; sem a PI1, o código do servidor nasce num repositório público.
- **RC-2. A F5 (o MMO) em paralelo com a F3 (o save),** depois da F2. A outra opção é uma depois da outra. Custo de errar: médio. Em série,
  o caminho até o ranking fica umas 6 a 10 semanas mais longo; em paralelo, duas frentes grandes ao mesmo tempo pedem mais revisão.
- **RC-3. A F6 começa no papel durante a F3** (pedir a revisão da LGPD e o certificado do INPI). Custo de errar: baixo.
- **RC-4. Abrir para fora só depois do portão F6,** mesmo que o código esteja pronto antes. Custo de errar: alto, se abrir sem a revisão
  da LGPD e sem os termos (a CN-10 e a MMO-4 já pediam isso).
