# Plano do beta fechado: 20 jogadores, 7 dias, com o multijogador (2026-11-16)

**Status:** sem código. **As BT-1 a BT-9 estão DECIDIDAS** pelo Matheus em 2026-11-16, pela recomendação e sem mudança ("Sim, segue e mergeia"). Todo
número é **PROPOSTO, SEM FONTE**: o jogo ainda não teve jogadores de fora, e os critérios do beta saem justamente dele.

**Origem:** o Matheus, em 2026-11-16: "Quero fazer também uma sessão de beta teste de ao menos 20 jogadores por 7 dias e mapear o desempenho
e evolução, porém já com todas as features de multiplayer funcionando, como planejar isso?"

**Onde entra no roadmap:** o beta **é a F4** do `docs/ROADMAP_V3_CONTA.md`, mudada de lugar. A F4 era "os convidados jogando com a conta e
o save", antes do multijogador; com o pedido, ela passa a vir **depois da F3 (o save na nuvem) e da F5 (o MMO3 ao MMO8)**, e antes da F6
(a abertura). O beta continua só com convidados adultos (CN-10, RC-4): não é a abertura.

## 1. O que o beta responde

| a pergunta | de onde sai a resposta |
|---|---|
| **o desempenho:** a infraestrutura aguenta 20 jogadores reais, com o ranking e o save na nuvem, sem perder nada? | as medidas do servidor e do cliente (seção 5.1) |
| **a evolução:** como os pets crescem nas mãos de pessoas de verdade: em quanto tempo chegam a cada estágio, que caminhos de evolução saem, como o cérebro modular aprende com donos diferentes | **os logs dos pets**, que o servidor já recebe pelo save na nuvem e refaz pelo replay (seção 5.2): nenhuma telemetria a mais |
| **o multijogador:** o ranking da semana, o desafio do dia e as duas pontuações funcionam e prendem o jogador? | os envios do ranking e os logs (seção 5.3) |
| **o jogador:** o que confunde, o que agrada, o que trava | os questionários e o botão "contar um problema" (seção 5.4) |

**A vantagem do projeto:** como o estado do pet nunca é salvo, só o log (event sourcing), o servidor tem, de cada pet do beta, a vida
inteira, evento por evento. A evolução se mede refazendo os logs depois, no Node ou no Python, sem pôr nenhum contador novo no jogo.

## 2. O que precisa estar pronto antes

"Todas as features de multijogador funcionando" é o roadmap quase inteiro. A lista do que o beta precisa:

| peça | etapa do roadmap | situação em 2026-11-16 |
|---|---|---|
| a página de entrada | F1 | a POC no #901, aberta |
| o servidor no Lightsail, o domínio, a Cloudflare, o deploy | CN1 e CN5 (F1) | o servidor local na `main` (#933); o deploy espera o domínio e as contas |
| a conta (o login, o primeiro acesso, apagar) | CN2 (F2) | as pranchas aprovadas (#882); o código não começou |
| a cota da fala, o Turnstile, a borda | CN4, PI3 (F2) | não começou |
| o save na nuvem | CN3 (F3) | as pranchas no #919, abertas |
| o nível 10 do Tamer | MMO2 | **na `main` (#925)** |
| o envio e a conferência pelo replay | MMO3 (F5) | não começou |
| a luta ranqueada | MMO4 | não começou |
| o ranking da semana | MMO5 | não começou |
| o desafio do dia | MMO6 | não começou |
| os títulos, os selos, o mural | MMO7 | não começou |
| as duas pontuações e o reset | MMO8 | não começou |
| **o que o beta pede a mais** | **as etapas BT0 a BT3** (seção 7) | este plano |

**A conta do prazo** (as estimativas do roadmap, PROPOSTAS): a F1 e a F2 levam umas 4 a 6 semanas; depois, a F3 (3 a 4) e a F5 (6 a 10)
correm em paralelo (RC-2). **O beta cabe daqui a umas 10 a 16 semanas**, se o domínio e as contas saírem logo. O caminho mais longo é o MMO.

## 3. O problema do nível 10

Pela MMO-13 (decidida), **o multijogador só abre no nível 10 do Tamer: o primeiro Mega**. Um jogador novo que começa no dia 1 do beta
talvez não chegue ao Mega em 7 dias de relógio: **ninguém mediu ainda** quanto tempo de relógio isso leva (a CN0 mediu o tamanho do save,
não o tempo até o Mega; o tempo do pet só anda com o jogo aberto, D-CONTA-38). Se não chegar, o beta não testa o multijogador.

**A proposta (BT-3):**
1. **Medir antes** (a etapa BT0): o tempo de relógio até o primeiro Mega, com os perfis de jogador da CN0, refazendo vidas no Node.
2. Se passar de uns 3 dias de jogo (PROPOSTO), **uma chave de beta** abre o cais a partir do nível 9 (ou de um marco mais cedo) só no
   ambiente do beta. A MMO-13 não muda no jogo; a chave sai depois.
3. A outra opção é **dar a cada jogador um pet já crescido** num save inicial. É mais rápido, mas o beta perde a evolução do ovo ao Mega,
   que é metade do que ele quer mapear.

## 4. Os jogadores

| ponto | proposta (PROPOSTO) |
|---|---|
| **quantos** | **30 convidados para ter 20 ativos** no dia 7: num teste de 7 dias, uma parte para de jogar (a perda é o que se mede, não um defeito) |
| **quem** | adultos (a CN-10), convidados pelo Matheus; uma mistura de quem joga no PC e no celular, e de quem conhece e não conhece Digimon |
| **o aceite** | um **termo de participação do beta**, curto: o que se coleta, para que, por quanto tempo, como apagar, que é um teste; a lista de convidados da CN2 |
| **o contato** | um canal só do beta (um grupo) para avisos e problemas; o botão "contar um problema" no jogo |
| **o começo** | **numa segunda-feira, 00:00 de Brasília**, para os 7 dias serem **exatamente uma semana do ranking** (a janela da MMO-9) e 7 desafios do dia |
| **as tabelas** | com 20 jogadores, uma tabela por estágio, sem divisões (as divisões da MMO-9 só começam com 60) |

## 5. O que se mede

### 5.1 O desempenho (técnico)

| o quê | como | sem coletar dado pessoal |
|---|---|---|
| a latência de cada rota (p50, p95), os erros por rota | o log do servidor e o Sentry | sim: só a rota, o tempo e o código |
| a CPU e a memória da VPS, contra a linha de 20 % do Lightsail | o painel do Lightsail e o Better Stack | sim |
| o tempo do replay por envio, o tamanho dos envios | o servidor, por envio | sim |
| as divergências: a sincronização recusada, a vez tomada, a história escolhida, o cliente × o servidor no ranking | o servidor, contadas por tipo | sim |
| o gasto da fala por jogador e por dia, e quantas vezes a cota acabou | o arquivo de gasto do servidor | sim |
| no cliente: o tempo de abrir o jogo, os quadros por segundo na ilha, o tipo de aparelho (celular ou PC, o navegador) | **um envio pequeno e opcional**, uma vez por sessão, com o aceite do termo | só o tipo de aparelho, nunca a impressão digital do navegador |

### 5.2 A evolução (dos logs dos pets)

Refeitos depois do beta, dos logs que o save na nuvem guardou:
- o tempo de relógio e de jogo até cada estágio, por jogador;
- os caminhos de evolução (que formas saíram) e a variedade entre os 20;
- o cuidado ao longo dos dias (os chamados atendidos e perdidos, o humor, o sono), pela medida comum da frente da individualidade;
- o cérebro modular: o que cada pet aprendeu do seu dono, pelas sondas que a pesquisa já tem;
- os resets e os cruzamentos, se houver.

**Isto é pesquisa sobre dado de pessoas:** a análise segue a regra do projeto e tem **um plano de análise registrado antes do beta**
(`docs/PLANO_ANALISE_V3_BETA.md`, a etapa BT1), com as perguntas e as medidas, só descritivas: com 20 jogadores não há comparação com
força estatística, e o plano diz isso. Os logs só entram na pesquisa com o aceite do termo, e saem do servidor no prazo da seção 8.

### 5.3 O multijogador

- quantos jogadores entraram no ranking, quantas lutas ranqueadas por dia, quantos tocaram o limite de 10 (MMO-8);
- quantos jogaram o desafio do dia, por dia;
- a tabela final da semana, por estágio; as duas pontuações; os títulos e os selos dados;
- **a divergência cliente × servidor** em cada luta ranqueada (a MMO0 mediu que o Chrome difere do Node no último bit; o beta mostra se isso
  muda algum resultado de verdade).

### 5.4 O jogador

- a retenção: quantos jogaram em cada um dos 7 dias, e o tempo de jogo por dia;
- **dois questionários curtos** (PROPOSTO: 5 a 8 perguntas), no dia 3 e no dia 7: o que entendeu, o que travou, o que mais gostou, se
  continuaria;
- o botão "contar um problema" no jogo, que manda o texto, a tela aberta e o hash do log (não o log);
- **sem ferramenta de análise de terceiros** (nada de Google Analytics nem de gravação de tela): o que se mede sai do próprio servidor.

## 6. Os critérios do beta (PROPOSTOS, SEM FONTE)

| o critério | a meta | se falhar |
|---|---|---|
| nenhum save perdido | **zero** | a F6 não abre até o conserto |
| a sincronização | p95 abaixo de 500 ms | revisar a VPS ou a rota |
| o ranking | **zero** luta em que o cliente e o servidor dão vencedores diferentes sem o aviso | revisar a MMO-5 antes de abrir |
| a VPS | a CPU abaixo da linha do Lightsail em 95 % do tempo | o Lightsail de 4 GB antes da F6 |
| a retenção | 10 ou mais dos 20 jogando no dia 7 | não trava a abertura; vai ao Matheus com os questionários |
| o multijogador alcançado | 15 ou mais dos 20 chegando ao ranking | revisar o nível 10 (seção 3) |

Os quatro primeiros são **técnicos** e travam a abertura; os dois últimos são **de produto** e vão ao Matheus.

## 7. As etapas próprias do beta

| etapa | o que entrega | quando |
|---|---|---|
| **BT0: o tempo até o Mega** | a medida da seção 3, com os perfis da CN0, refazendo vidas no Node; a decisão da chave de beta | já pode (não depende de servidor) |
| **BT1: o plano de análise** | o `docs/PLANO_ANALISE_V3_BETA.md`: as perguntas, as medidas, o que é descritivo; o termo de participação | antes de qualquer convite |
| **BT2: a medição** | as contagens do servidor (5.1, 5.3), o envio opcional do cliente, o botão "contar um problema", o painel do beta (o Grafana grátis ou uma página do próprio servidor) | junto com a F5 |
| **BT3: o ensaio** | **um beta zero**: 3 a 5 pessoas, 2 dias, uma semana antes, para achar o que quebra sem gastar os 20 | uma semana antes do beta |
| **o beta** | 7 dias, de segunda a domingo | depois da F3, da F5 e do BT3 |
| **BT4: o resultado** | o `docs/RESULTADO_V3_BETA.md`: os critérios, a evolução (do plano de análise), os questionários; a decisão de abrir (F6) ou consertar antes | na semana seguinte |

**Durante o beta, o motor não muda** (a MMO-14 já pede isso na semana do ranking): só consertos do servidor e do cliente que não mexem no
motor, cada um com o registro de quando entrou.

## 8. A privacidade e os dados

- o termo de participação diz tudo antes: o que se coleta (a seção 5), que os logs dos pets podem ir para a pesquisa, por quanto tempo;
- **os logs do beta saem do servidor 30 dias depois do fim** (PROPOSTO), salvo os de quem quiser continuar jogando com a conta; o que fica
  para a pesquisa é refeito em medidas agregadas, sem o identificador da conta;
- o apelido gerado (sem nome); nenhum e-mail guardado;
- só adultos; quem quiser sair apaga a conta pela tela de apagar (a CN2), a qualquer hora.

## 9. O custo do beta

| o quê | em 7 dias (PROPOSTO) |
|---|---|
| a VPS, o domínio, a Cloudflare | uns US$ 4 (a parte da semana dos uns US$ 14 a 15 por mês) |
| a fala | 20 jogadores × até 30 falas por dia × 7 dias: uns US$ 0,40 no `claude-haiku-5-5`, uns US$ 4 no `claude-haiku-4-5` (a tabela do `servidor/fala_llm.py`) |
| o CI | dentro do teto (PI-2) |
| **total** | **menos de US$ 10**, fora o tempo do Matheus |

## 10. Decisões para o Matheus

Cada uma com a recomendação e o custo de errar. **Todas DECIDIDAS** pelo Matheus em 2026-11-16, pela recomendação: "Sim, segue e mergeia".

- **BT-1 (DECIDIDA). O beta é a F4, depois da F3 e da F5,** com todo o multijogador (o pedido). A outra opção é um beta mais cedo, só com a conta e o
  save (a F4 de antes), e um segundo beta com o MMO. Custo de errar: médio. Esperar o MMO adia o primeiro contato com jogadores de fora em
  umas 6 a 10 semanas; dois betas gastam convidados duas vezes.
- **BT-2 (DECIDIDA). 30 convidados para ter 20 ativos,** adultos, PC e celular, com o termo de participação. Custo de errar: médio. Com 20 convites
  exatos, o dia 7 tem menos de 20.
- **BT-3 (DECIDIDA). A medida do tempo até o Mega antes (BT0),** e a chave de beta que abre o cais mais cedo se passar de uns 3 dias. A outra opção é
  o save inicial com um pet crescido. Custo de errar: alto. Sem isso, o beta pode acabar sem ninguém no ranking.
- **BT-4 (DECIDIDA). Começar numa segunda-feira, 00:00 de Brasília,** para o beta ser uma semana inteira do ranking. Custo de errar: baixo.
- **BT-5 (DECIDIDA). O que se mede é só o da seção 5, do próprio servidor,** com o envio do cliente opcional e sem ferramenta de terceiros. Custo de
  errar: médio. Uma ferramenta de terceiros coleta mais do que o termo diz.
- **BT-6 (DECIDIDA). O plano de análise registrado antes (BT1),** só descritivo, com os logs na pesquisa só com o aceite. Custo de errar: alto. A regra
  do projeto pede o plano antes, e o dado é de pessoas.
- **BT-7 (DECIDIDA). O ensaio de 3 a 5 pessoas, uma semana antes (BT3).** Custo de errar: médio. Sem o ensaio, o que quebra no primeiro dia gasta os 20.
- **BT-8 (DECIDIDA). Os critérios da seção 6,** com os quatro técnicos travando a abertura. Custo de errar: médio.
- **BT-9 (DECIDIDA). Sem cobrança e sem anúncio no beta.** A assinatura e o anúncio da voz (a F7) só depois da abertura, como a CN-13 já diz. Sem o vídeo, a
  cota da CN-16 (5 grátis e o resto por vídeo) deixaria o jogador com 5 falas por dia; **no beta, as 30 falas por dia da CN-8 saem de
  graça**, sem vídeo. Custo de errar: baixo. A conta da seção 9 já conta as 30.
