# Plano do multijogador: vários jogadores, ranking semanal e top tier diário (2026-11-10)

**Status:** APROVADO, sem código. O Matheus aprovou as decisões MMO-1 a MMO-19 (seção 14) pela recomendação em 2026-11-11, inclusive o
marco do nível 10 no primeiro Mega (MMO-13). Os números continuam **PROPOSTOS, SEM FONTE**, e se
acerta na rodada de equilíbrio do fim (a regra "equilíbrio só no fim").

**Origem:** o Matheus, em 2026-11-10: "planejamento de um sistema de MMO, no caso, aceitar múltiplos jogadores com pontuações de rankings,
né? Incorporando um possível sistema de moedas, rankings semanais e um top tier diário."

**Só no jogo.** A pesquisa em Python não muda, como nas medalhas e nos Bits. As referências de outros jogos, com os links, estão no vault
(`DigiLab Research/20 Temas/Multijogador e rankings.md`), e não aqui.

**A leitura de "MMO" deste plano (MMO-1):** cada jogador continua na sua ilha, com o seu pet. Os jogadores se encontram nas **tabelas**
(o ranking da semana e o desafio do dia), não num mundo dividido ao vivo. É o que o pedido descreve ("aceitar múltiplos jogadores com
pontuações de rankings"), e é o que o motor de hoje aguenta sem ser refeito.

## 1. O que existe hoje

| peça | onde está | o que pesa para o multijogador |
|---|---|---|
| **o save do pet** | `web/app/src/save.ts`: `{semente, log, versao}` no `localStorage` (chave `digilab-web-v21-sprites`) | o estado nunca é salvo, só o log. Um servidor que recebe o log refaz a vida inteira |
| **o replay** | `Motor.reproduzir` e `Motor.aplicarEvento` (`web/app/motor/`), sem DOM (o teste `motor_sem_dom`) | o mesmo código roda no Node. A paridade bit a bit só vale no mesmo runtime: o Chrome difere do Node no último bit de `exp` e `log` (`web/app/CLAUDE.md`) |
| **o custo do replay** | `web/app/scripts/medicoes/replay_lp2.json` | 0,3 ms por luta em média, e uma vida de 166 a 234 lutas refaz em 67 a 76 ms (Node 24, um processo). Conferir cada envio no servidor é barato |
| **a luta** | `Motor.lutarPoc(rival, semente, mapa)` grava `["l", {r, s, m}]` | a luta é decidida inteira pelo motor: a mesma IA nos dois lados, nenhum botão durante a luta (LP-3, LP-10). O resultado sai só do log |
| **a semente da luta** | `TelaLugaresPoc.tsx`: `hashSemente("luta", m.semente, m.log.length)` | **sai da posição no log.** Uma ação a mais antes da luta muda a semente: quem joga sozinho pode tentar de novo até ganhar (seção 3) |
| **a semente do pet** | `jogo.ts`, `novoPet()`: `Date.now() ^ Math.random()` | **o jogador escolhe, sem querer, o ovo.** Para um ranking, quem quiser pode chocar até achar um bom |
| **o tempo** | `src/tempo.ts`: de 1x a 6 h/s, e o "pular uma hora" | **o tempo do pet não é o tempo do relógio, de propósito.** Nenhum limite do ranking pode ser contado no tick do pet (seção 3) |
| **o Tamer** | `web/app/src/tamer.ts`, registro próprio com event sourcing (versão 8 na `main`; 9 com os Bits no #765) | medalhas, itens, títulos, recordes da Fronteira, as tentativas da Fábrica e do Salão. É o registro do jogador, o que o servidor recebe junto com o pet |
| **a Fábrica** | `web/app/motor/fabrica.ts`: os 3 alugados, as lutas e a troca saem de `sementeFabrica(n)` | **nenhum pet do jogador luta:** todos começam iguais. É o melhor desafio do dia que o jogo já tem (seção 6) |
| **o nível do Tamer** | `src/nivel.ts` (marcos 1 a 9, `ULTIMO_MARCO`), só na vista (P-5, opção V) | a P-5 e a P-10 já decidiram: o multiplayer entra do nível 10 em diante, e aí o nível vai para o registro do Tamer (opção T) |
| **o servidor local** | `servidor/servidor_local.py`: o jogo e a fala; `--remoto` libera só as rotas do jogo pelo túnel | já serve o jogo pela rede, mas não guarda nada de jogador. Roda na máquina do Matheus (≤ 4 processos, V3-D8) |

O que **não** existe: conta, login, servidor com dados, envio de log, tabela de pontos, nenhuma rota de ranking.

## 2. O que falta para vários jogadores

1. **A conta.** Um jogador é uma conta com um apelido público. O login fica com um provedor (MMO-3): o jogo não guarda senha.
2. **O servidor.** Ele guarda a conta, os envios e as tabelas, entrega as sementes das lutas ranqueadas e confere cada envio (MMO-2).
3. **A conferência pelo replay** (seção 3). O cliente manda o log, nunca a pontuação. O servidor refaz o log no Node e calcula os pontos. O
   número que o cliente mostra é só uma prévia, até o servidor confirmar.
4. **A privacidade** (seção 11). Entrar no ranking é escolha do jogador, o apelido não é o nome, e o log é apagado depois da conferência.
5. **O nível do Tamer no registro** (P-5, opção T): o servidor precisa conferir que o jogador chegou ao nível 10.

## 3. A conferência contra trapaça

**A regra:** a pontuação é o que o servidor calcula do log. O cliente pode estar adulterado, e o log pode ter sido escrito à mão. O replay
garante que o log é **possível** (o motor aceita cada evento, e um evento inválido falha alto). Ele não garante que foi **jogado com
honestidade**. Por isso há quatro travas, uma para cada brecha:

| brecha | como alguém trapaceia | a trava |
|---|---|---|
| **o log inventado** | escreve um log com uma vitória que o motor não daria | o servidor refaz o log; o que não reproduz é recusado, com o motivo |
| **a luta repetida até ganhar** | joga a luta sozinho, vê que perde, muda uma ação antes e tenta de novo | **a semente da luta ranqueada vem do servidor (MMO-6).** O cliente pede a luta com o hash do log até ali; o servidor devolve a semente, e **a semente pedida conta como luta feita** (sem o envio, conta como derrota). O cliente não sabe a semente antes de se comprometer |
| **o ovo escolhido** | choca até achar um ovo forte | só conta a luta ranqueada, e o rival e a semente vêm do servidor. O ovo escolhido ainda ajuda, mas o pet cresce do mesmo jeito para todos |
| **o tempo acelerado e o robô** | acelera o tempo ou usa um script que joga perfeito | **os limites contam pelo relógio do servidor** (MMO-8): no máximo 10 lutas ranqueadas por dia de relógio (PROPOSTO, SEM FONTE). O robô continua possível; o teto o deixa no mesmo ritmo de quem joga bem |

**A semente do servidor, por dentro (PROPOSTO):** semente = HMAC(segredo da semana, conta, número da luta). O segredo da semana é
publicado quando a semana fecha, e aí qualquer pessoa pode refazer as lutas da tabela. O motor não muda: `lutarPoc` já recebe a semente por
parâmetro. O que muda é quem a escolhe.

**A divergência Chrome × Node:** o pet de um jogador honesto é jogado no Chrome, e o servidor confere no Node. Os dois diferem no último bit de
`exp` e `log`, e uma diferença no corpo ou no cérebro pode, um dia, mudar uma decisão do pet e o resultado de uma luta. Antes de qualquer
servidor, a **MMO0** mede quantos logs gravados no Chrome o Node refaz igual (seção 12). Se algum divergir, a conta do servidor vale e o
jogador vê o resultado do servidor, com o aviso; a regra está na MMO-5.

**A versão do motor:** a conferência roda com o motor de uma versão fixa, e o motor só muda na virada da semana (MMO-14). Um cliente de
outra versão recebe "atualize o jogo" e não envia.

## 4. O que vale ponto

**Só a luta ranqueada vale ponto (MMO-7).** A vitória é o feito que o motor decide sozinho, que o servidor confere e que a semente do
servidor protege. O cuidado fica fora do ranking, pela mesma razão que tirou o XP por ação (a P-2 e a regra "o treino nunca vem de clicar
carinho"): um ranking de cuidado ensina a clicar, e um robô cuida melhor do que gente.

| o quê | pontos (PROPOSTO, SEM FONTE) | a regra |
|---|---|---|
| **vitória ranqueada** | pela faixa do rival: Rookie 10, Champion 20, Ultimate 40, Mega 80 | o rival vem da Arena, dentro do nível do portão (MO2). A faixa vale, não o estágio do pet |
| **repetir o mesmo rival na semana** | a metade da anterior | como a novidade dos Bits (M-3), mas na semana de relógio, não no dia do pet |
| **derrota** | 0 | nada a farmar perdendo; a semente pedida e não enviada também é 0 |
| **o limite** | 10 lutas ranqueadas por dia de relógio | a luta fora do ranking continua livre, como hoje |
| **a Fronteira** (Liga, Torre, Fábrica, Salão) | não soma na semana | os recordes vão para o **mural** de todos os tempos (seção 7), e a Fábrica vira o desafio do dia (seção 6) |

**Como entra no ranking:** a cada envio, o servidor refaz o log, acha as lutas ranqueadas (as que usam uma semente entregue por ele, na
ordem), e soma os pontos na semana daquela luta, pela hora em que o servidor entregou a semente.

## 5. O ranking semanal

| ponto | proposta (PROPOSTO) |
|---|---|
| **a janela** | de segunda 00:00 a domingo 23:59, no horário de Brasília (UTC−3, sem horário de verão), pelo relógio do servidor. A luta conta na semana em que a semente foi entregue |
| **as tabelas** | **uma por estágio do pet na hora da luta** (Rookie, Champion, Ultimate, Mega), para um pet novo não disputar com um Mega. Um jogador aparece em cada tabela em que lutou |
| **o desempate** | 1) mais pontos; 2) mais rivais diferentes vencidos; 3) menos lutas ranqueadas usadas; 4) quem chegou primeiro aos pontos, pela hora do servidor |
| **as divisões** | com poucos jogadores, uma tabela só por estágio. Com 60 jogadores ativos ou mais (PROPOSTO), grupos de 30 com subida e descida, como nas ligas semanais do Duolingo (MMO-9) |
| **o fim da semana** | a tabela congela, o segredo da semana é publicado, e a recompensa entra (seção 7). A semana seguinte começa do zero |

## 6. O top tier diário: o desafio do dia

**A proposta (MMO-10): a Fábrica do dia.** Todo jogador recebe os mesmos 3 alugados e os mesmos rivais, e tem **uma tentativa por dia**.
Começar a tentativa já gasta a do dia, como no desafio diário do Spelunky. Como nenhum pet do jogador luta, quem começou ontem disputa com
quem joga há um mês.

| ponto | proposta (PROPOSTO) |
|---|---|
| **a janela** | de 00:00 a 23:59, no horário de Brasília, pelo relógio do servidor |
| **o mesmo para todos** | os alugados e os rivais saem do segredo do dia |
| **o que é de cada um** | **a semente de cada luta é por conta e só sai depois da escolha** (o alugado, a troca). Com a semente igual para todos, quem tem duas contas, ou quem lê a dica de outro jogador, sabe o resultado antes de escolher. Assim, sabe-se a escolha, mas não a sorte |
| **a pontuação** | as lutas vencidas seguidas na tentativa |
| **o desempate** | 1) mais vitórias; 2) mais vida somada no fim da última luta vencida; 3) quem terminou primeiro, pela hora do servidor |
| **o top tier** | os **10 primeiros do dia** (ou o 1 % de cima, quando houver mais de 1 000 jogadores; PROPOSTO) ganham o selo "Top do dia" com a data, que fica no perfil. O perfil conta os selos |

**O custo:** a Fábrica de hoje tira tudo de `sementeFabrica(n)`. Receber as sementes de fora pede uma mudança no motor
(`motor/fabrica.ts`), atrás de chave desligada, com o gabarito antes. É a única etapa do plano que toca o motor (MMO5), e a decisão dela é a
MMO-10. A outra opção, sem mudar o motor, é "a luta do dia": um rival fixo do dia contra o pet de cada um. É mais simples, mas o pet mais
velho ganha sempre, e o top tier vira o ranking semanal de novo.

## 7. As recompensas e os Bits

**A regra dos Bits fica como está (M-1 a M-10):**
- os Bits pagam o **feito do próprio pet** (M-2), e a Fronteira não paga (M-2);
- nada de dinheiro real (seção 10 do plano dos Bits);
- a troca de Bits entre jogadores fica fora, como o plano dos Bits deixou ("com o multiplayer, se vier");
- **os Bits não entram no ranking nem são conferidos pelo servidor.** Eles continuam no registro do Tamer, na máquina do jogador. Quem
  adulterar os próprios Bits compra enfeites para a própria ilha e não muda a tabela de ninguém.

**A recomendação (MMO-12): o ranking paga prestígio, não Bits.** É a mesma separação que o plano dos Bits fez para a Fronteira: os Bits
compram (o portão, a loja, as melhorias), e o ranking mostra (títulos, selos, o mural). Se o ranking pagasse Bits, o melhor jogador
compraria o portão mais cedo e ganharia mais lutas: uma espiral.

| recompensa (PROPOSTO) | quem ganha | o que é |
|---|---|---|
| **o selo "Top do dia"** | os 10 primeiros do desafio do dia | um selo com a data no perfil |
| **o título da semana** | o 1º de cada tabela de estágio | "Campeão Rookie da semana 46", no perfil por uma semana e no mural para sempre |
| **o enfeite da temporada** | quem fica entre os 10 primeiros de uma tabela da semana | um enfeite da ilha que **não se vende na loja** (o padrão cartoon), um por temporada de 4 semanas |
| **o mural** | todos | os recordes de todos os tempos da Torre, da Fábrica e do Salão, e os títulos das semanas. É o lugar da Fronteira no multijogador |

A outra opção da MMO-12: uma quantia fixa e pequena de Bits por participar da semana (por exemplo, 50 por semana com 5 lutas ranqueadas;
PROPOSTO), igual para todos, sem depender da colocação. É uma fonte nova, e por isso vai ao Matheus: não desfaz a M-2, mas acrescenta uma
linha à tabela dela.

## 8. As duas pontuações: a do Digimon e a do Tamer

O Matheus pediu em 2026-11-10, depois da primeira versão deste plano: "A ideia é que o jogador ele tenha um Digimon com uma pontuação
grande, mas o Tamer em si ele também tem uma pontuação de respeito, uma pontuação máxima também. Então tem tanto o Digimon quanto o Tamer."

| | **os pontos do Digimon** | **o Respeito do Tamer** |
|---|---|---|
| **de quem é** | de um pet, a vida dele | do jogador, todos os pets dele |
| **de onde vem** | os pontos das lutas ranqueadas da seção 4, somados em todas as semanas da vida do pet | os feitos únicos do Tamer e os resets com bônus (tabela abaixo) |
| **zera?** | não: é o total da vida. O pet novo começa em 0 | nunca: só sobe |
| **o ranking** | **o máximo histórico dos Digimon:** uma linha por pet, pelo total dele. O pet aposentado continua na tabela, com o total que tinha | **o ranking dos Tamers:** uma linha por conta, pelo Respeito |
| **a semana e o dia** | a tabela da semana (seção 5) é a fatia da semana destes pontos | não entra na semana nem no dia |

**De onde vem o Respeito (PROPOSTO, SEM FONTE):**

| feito | Respeito | quantas vezes |
|---|---|---|
| a 1ª medalha de cada líder | 100 | uma por líder (6) |
| o título da Liga (o evento `campeao`) | 500 | uma |
| o reset com bônus (seção 9) | pelo nível do reset: 300, 600 ou 1 000 | um por pet |
| o título da semana (o 1º de uma tabela de estágio) | 100 | um por semana e tabela |
| o selo "Top do dia" | 20 | um por dia |

**O que o servidor confere:** o Respeito do ranking conta só o que o servidor viu. São as medalhas e o título refeitos dos logs que o
jogador mandou, os resets dos pets cujo log ele mandou e os selos e títulos que ele mesmo deu. A tela pode mostrar um Respeito local maior,
com pets que nunca foram enviados, mas só o conferido vai para a tabela.

**O Respeito e o nível do Tamer:** hoje o nível é a contagem dos marcos 1 a 9 (`src/nivel.ts`). Ele não tem XP, e a P-2 recusou o XP
por ação. A proposta (MMO-15) mantém os marcos 1 a 9 como estão: são o tutorial e abrem os lugares. **O nível 10 é o marco da MMO-13, e do 11 em
diante o nível passa a ser lido no Respeito:** um nível a cada 1 000 de Respeito (PROPOSTO). O Respeito não vem de clique, vem de feito, então a P-2 fica
de pé.

**"Uma pontuação máxima" tem duas leituras (MMO-16):**
- **(a) recomendada:** o recorde, a maior pontuação já feita. O Respeito só sobe, e a tabela dos Tamers é ordenada por ele;
- **(b):** um teto. O Respeito para num máximo (por exemplo, 10 000), e quem chega lá vira "Tamer Lendário".

Com o teto, o topo da tabela empata, e o desempate vira só a data. Por isso a recomendação é a (a), com os títulos de faixa (Lendário a
partir de 10 000; PROPOSTO) como marcos, sem parar a conta.

## 9. O reset: recomeçar com bônus

O pedido: "E daí tem a questão do reset, né? Se quando ele reseta, ele chega a certo nível, quando ele reseta, ele vai ter algum tipo de
bonificação."

**A leitura (MMO-17): o reset é do pet, não do Tamer.** O jogador aposenta o Digimon e recomeça de um ovo. Se o pet chegou a um nível,
ganha o bônus. É como o Digimon World: o pet acaba, e um ovo novo começa. A outra leitura é o Tamer recomeçar do zero, como o "prestígio"
dos jogos incrementais. Ela apagaria as medalhas, que o Tamer guarda para sempre (`tamer.ts`, "sobrevivem ao pet"), e o portão e as
melhorias comprados com Bits (M-4, M-8). Por isso não é a recomendada.

**O que já existe, e o reset reaproveita:**
- **o ovo novo da conclusão** (`src/jornada.ts`, `novoOvoGuardandoAtivo` e `chocarDoBrasao(esp, guardarAtivo)`): depois da Liga, o jogo
  oferece um ovo novo e guarda o campeão;
- **a aposentadoria do cruzamento** (`src/heranca.ts`, `cruzar`): o pai ativo sai do jogo e vai para Diário › Gerações (`CHAVE_GERACOES`),
  só para ver, com a geração contada (`geracao`).

O reset é a soma dos dois: aposentar o pet ativo em Gerações, sem cruzar, e chocar um ovo do brasão escolhido. Nenhum dos dois toca o
motor nem o formato do save: o ovo novo é um `Motor` novo. **O cruzamento também conta como reset:** o pai que se aposenta ganha o bônus
pelo nível dele.

**O que zera e o que fica:**

| zera (é do pet) | fica (é do Tamer) |
|---|---|
| o pet ativo, que vai para Gerações com o log inteiro | as medalhas, os itens, o título, os recordes da Fronteira |
| os pontos do Digimon (o pet novo começa em 0; o aposentado fica no máximo histórico) | os Bits, o portão ★ e as melhorias (MO2 a MO4) |
| a trava da campanha (já é por pet: cada ovo sobe de novo) | o nível do Tamer, o Respeito, os selos e os títulos |
| os chips equipados no pet (o chip é do Tamer e se equipa de novo) | os pets guardados |

**Em que nível o reset dá bônus (PROPOSTO, SEM FONTE):**

| nível do reset | o pet chegou a | Respeito | Bits |
|---|---|---|---|
| **sem bônus** | antes do Ultimate | 0 | 0 (o recomeço de hoje, sem mudança) |
| **1** | Ultimate | 300 | 150 |
| **2** | Mega | 600 | 400 |
| **3** | Mega e o título da Liga com este pet | 1 000 | 800 |

**A trava contra o reset de farm:** o pet novo recebe as medalhas que o Tamer já tem (o evento `"u"`), então chega ao Ultimate mais
depressa do que o primeiro. Sem trava, recomeçar viraria a fonte mais rápida de Respeito e de Bits. Duas travas (MMO-18):
- **para o Respeito (o ranking):** o reset só dá Respeito se o pet tiver um mínimo de pontos do Digimon conferidos (por exemplo, 200;
  PROPOSTO). Esses pontos saem das lutas ranqueadas, que o relógio do servidor limita (MMO-8);
- **para os Bits (a economia local):** um reset pago por semana de relógio (PROPOSTO). Os Bits não são conferidos pelo servidor (seção 7),
  então a trava só segura o equilíbrio, não a trapaça.

**Qual é o bônus (MMO-18):** a recomendação é **Respeito e Bits, sem herança de stats no motor.** Os Bits compram chips na loja, dentro do
teto de hoje (M-9). Assim, o bônus ajuda o pet novo sem passar do teto do estágio. A outra opção é a herança do Digimon World: o ovo novo
nasce com uma parte dos stats do anterior. Ela pede uma versão de pet nova e um evento de origem no motor, e dá ao veterano uma vantagem que
o teto não segura.

**Como o reset entra nos rankings:**
- **a semana:** as lutas do pet aposentado já contadas ficam na tabela da semana. O pet novo entra na tabela do estágio dele (o Rookie),
  e os pontos dos dois somam, porque a tabela é por estágio e o jogador aparece em cada uma em que lutou;
- **o desafio do dia:** não muda. A Fábrica não usa o pet do jogador;
- **o máximo histórico dos Digimon:** o aposentado fica com o total que tinha, e o pet novo entra como uma linha nova;
- **o ranking dos Tamers:** sobe pelo Respeito do reset.

**Como conversa com os Bits (M-1 a M-10):** os Bits do reset são uma linha nova na tabela da M-2, como os marcos de evolução. Não
desfazem nenhuma decisão: a derrota e a Fronteira continuam sem pagar; o kit continua de graça (M-7); o chip continua no teto (M-9); e o
dinheiro real segue fora. Como é uma fonte nova, vai ao Matheus (MMO-19), com a outra opção: o reset só dá Respeito, e os Bits ficam como
a M-2 deixou.

**O que o registro precisa:** um evento novo no registro do Tamer, `"reset"`: o pet (semente), o hash do log dele, o estágio, o nível do
reset e a hora. É a mesma versão nova do Tamer da MMO2. O servidor confere o nível do reset refazendo o log do pet aposentado.

## 10. Onde o multijogador entra no jogo

- **O nível:** do nível 10 do Tamer em diante (a P-10). Hoje os marcos vão até o 9 (`ULTIMO_MARCO`). O marco do 10 fica com o Matheus
  (MMO-13; a P-10 sugeria o primeiro Mega ou o segundo pet guardado).
- **O lugar:** **o cais**, o lugar que a progressão (o nível 10+) e o plano dos Bits (a tabela da seção 4) já deixaram para o multiplayer.
  O cais abre o ranking da semana, o desafio do dia, o perfil e o mural.
- **Sem conta, nada muda:** o jogo de um jogador só segue igual, com o save no navegador. A conta é só para quem entra no ranking.

## 11. A privacidade

- **Entrar é escolha:** o jogador entra pelo cais, lê o que vai para o servidor e aceita. Sair apaga a conta e os envios.
- **O que vai para o servidor:** o identificador da conta, o apelido, os logs do pet e do Tamer de quem envia, e as horas dos envios. Não
  vão o nome, a idade, o lugar nem a fala do pet (a fala nunca entra no registro do pet, pelo `servidor/CLAUDE.md`).
- **O apelido:** gerado (um nome de Digimon e um número; PROPOSTO), com a troca por uma lista fechada de palavras. Sem texto livre na
  tabela, nada para moderar.
- **O log some:** depois da conferência e do fim da semana, o servidor apaga o log e guarda só os pontos, o hash do log e as sementes
  (PROPOSTO: 30 dias depois do fim da semana, para uma contestação). O log diz quando a pessoa joga, e isso é dado de comportamento.
- **Os menores de idade:** um jogo de pet com Digimon atrai criança. A LGPD (art. 14) pede o consentimento de um dos pais para a criança
  e proíbe pedir a ela dado que não seja estritamente necessário para o jogo (§ 4º). O desenho acima já pede o mínimo. Antes de abrir para
  fora do grupo de convidados, isso passa por quem entende da lei (MMO-4). **Este plano não é parecer jurídico.**

## 12. As etapas (um PR por etapa)

Cada etapa com tela começa pela prancha, que o Matheus aprova antes do código (desktop e celular juntos, a regra dos lugares da ilha).

| etapa | o que entrega | depende de |
|---|---|---|
| **MMO0: a medida Chrome × Node** | um script e um e2e que gravam vidas no Chrome e as refazem no Node, com a contagem de quantas dão o mesmo log, o mesmo resultado de cada luta e a mesma assinatura. Sem servidor e sem tela | nada; decide a MMO-5 |
| **MMO1: a conta dos pontos** | a pontuação como função pura (`web/app/src/ranking/`, fora do motor): do log do pet, do registro do Tamer e da lista de sementes entregues, os pontos de cada luta, a semana e o desempate. Vitest e um comando Node que confere um save | MMO0, MMO-7, MMO-9 |
| **MMO2: o nível 10 no registro do Tamer** | o marco do nível 10 e o nível no registro (P-5, opção T), com a versão nova do Tamer, que lê as de antes | os Bits na `main` (#765), MMO-13 |
| **MMO3: o servidor e a conta** | a prancha do cais, da entrada e do perfil; o servidor (MMO-2) com a conta, o apelido, a entrada, a saída que apaga tudo e o envio dos logs; a conferência rodando o motor no Node | MMO1, MMO-2, MMO-3, MMO-4 |
| **MMO4: a luta ranqueada** | a prancha; o pedido da semente com o hash do log; a semente pedida contada como luta; o limite por dia; a prévia no cliente e o resultado do servidor | MMO3, MMO-6, MMO-8, a LP5 na `main` |
| **MMO5: o ranking da semana** | a prancha; as tabelas por estágio, o desempate, o congelamento e o segredo publicado | MMO4, MMO-9, MMO-14 |
| **MMO6: o desafio do dia** | a Fábrica com as sementes de fora, atrás de chave desligada e com o gabarito antes; a tentativa única; o selo | MMO3, MMO-10, MMO-11 |
| **MMO7: as recompensas e o mural** | os títulos, os selos, o enfeite da temporada e o mural | MMO5, MMO6, MMO-12 |
| **MMO8: as duas pontuações e o reset** | a prancha do reset (aposentar, o bônus, o ovo novo) e do perfil com as duas pontuações; o evento `"reset"` no registro do Tamer; os pontos do Digimon e o Respeito na conta pura da MMO1; o máximo histórico dos Digimon e o ranking dos Tamers no servidor; os Bits do reset, se a MMO-19 os aprovar | MMO2, MMO5, MMO-15 a MMO-19 |

**Depois do plano, só se o Matheus quiser:** a luta assíncrona contra o pet de outro jogador. O servidor já tem o log dele, e a luta é IA
contra IA, então daria para lutar contra uma cópia do pet de outro jogador, sem os dois estarem jogando ao mesmo tempo. Fica fora das
etapas porque muda o catálogo de rivais e pede a sua própria decisão.

## 13. Os riscos

| risco | o que se vê | o que segura |
|---|---|---|
| **a divergência Chrome × Node** | um jogador honesto vê uma vitória que o servidor conta como derrota | a MMO0 mede antes; o servidor manda e explica; a conta do servidor aparece na tela |
| **o robô e as contas a mais** | um script joga perfeito, ou uma pessoa abre várias contas para o desafio do dia | o limite pelo relógio, a semente por conta revelada depois da escolha, o login por provedor. Não some de todo; é um ranking de um projeto pessoal, sem prêmio em dinheiro |
| **o equilíbrio da luta muda** | a LP5 está em andamento; um rival que trava o Rookie deixa a tabela Rookie injusta | a MMO4 espera a LP5; o motor só muda na virada da semana (MMO-14) |
| **o servidor na máquina do Matheus** | a máquina cai sob carga (WHEA 19, ≤ 4 processos), e o ranking fica fora do ar | começar com um grupo de convidados; a hospedagem de fora é a MMO-2 |
| **o custo de manter** | conta, servidor, backup e contestação pedem tempo que é da pesquisa | etapas pequenas; cada uma para no PR; o jogo de um jogador só não depende de nada disso |
| **a privacidade e os menores** | dado de comportamento e de criança num servidor | entrada por escolha, apelido gerado, sem texto livre, log apagado; a revisão antes de abrir (MMO-4) |
| **o ranking tomar o lugar do pet** | o jogo de cuidar vira um jogo de farmar luta | o cuidado fora do ranking, o limite diário, o prestígio no lugar dos Bits |
| **o reset de farm** | o pet novo herda as medalhas do Tamer e chega ao Ultimate depressa; recomeçar vira a fonte mais rápida de Respeito e de Bits | o Respeito do reset pede pontos do Digimon conferidos; os Bits do reset, um por semana de relógio (MMO-18) |
| **o segredo vazar** | quem tem o segredo da semana sabe as sementes antes | o segredo fica só no servidor, fora do git, como a chave da API (`servidor/CLAUDE.md`) |

## 14. Decisões para o Matheus

Cada uma com a recomendação e o custo de errar. **APROVADAS pelo Matheus em 2026-11-11, todas pela recomendação** ("Eu autorizo" e
"continue com as recomendacoes", nesta sessão). Aprovar a regra não fixa os números: eles seguem PROPOSTOS até a rodada de equilíbrio.

- **MMO-1. O que é o "MMO":** cada um na sua ilha, e os jogadores se encontram nas tabelas (assíncrono). A outra opção é um mundo dividido
  ao vivo. **Recomendo o assíncrono.** Custo de errar: alto. O mundo ao vivo pede um servidor que roda o motor o tempo todo e a
  sincronização de vários pets, e o motor de hoje é de um pet por vez.
- **MMO-2. Onde fica o servidor:** **começar no servidor local** (`servidor/`, atrás de uma chave nova), com o conferidor no Node e o
  acesso pelo túnel, só para convidados. A hospedagem de fora (um serviço que roda JavaScript, porque o motor é TS) vem depois, com uma
  decisão própria. Custo de errar: médio. Começar fora já obriga a pagar e a cuidar de um serviço antes de saber se o ranking pega;
  começar em casa deixa o ranking cair junto com a máquina.
- **MMO-3. O login:** **por um provedor** (entrar com Google ou com GitHub), sem senha guardada pelo jogo. A outra opção é o link por
  e-mail. Custo de errar: baixo a médio. Guardar senha é o pior caso; o provedor também segura um pouco as contas a mais.
- **MMO-4. A privacidade da seção 11,** com a entrada por escolha, o apelido gerado, sem texto livre, o log apagado em 30 dias
  (PROPOSTO) e **a revisão da LGPD antes de abrir para fora dos convidados.** Custo de errar: alto, se abrir sem a revisão.
- **MMO-5. Quem manda na pontuação:** **o servidor**, pelo replay no Node. O cliente mostra a prévia e, quando divergir, a conta do
  servidor com o aviso. Depende da MMO0. Custo de errar: confiar no cliente é deixar a tabela para quem edita o save.
- **MMO-6. A semente das lutas ranqueadas vem do servidor,** com o hash do log no pedido, e **a semente pedida conta como luta**.
  Custo de errar: sem isso, quem joga sozinho tenta a luta até ganhar, e o ranking mede paciência.
- **MMO-7. O que vale ponto: só a vitória ranqueada,** pela faixa do rival, com a metade para o mesmo rival na semana (seção 4). O cuidado
  fica fora. Custo de errar: pôr o cuidado no ranking ensina a clicar (a P-2), e um robô cuida melhor do que gente.
- **MMO-8. O limite pelo relógio do servidor:** 10 lutas ranqueadas por dia (PROPOSTO). Custo de errar: sem limite, ganha quem tem mais
  tempo ou um script; com o limite baixo demais, a semana acaba na terça.
- **MMO-9. O ranking semanal da seção 5:** de segunda a domingo, no horário de Brasília; uma tabela por estágio do pet; o desempate
  em quatro passos; as divisões de 30 só com 60 jogadores ativos (PROPOSTO). Custo de errar: médio. Uma tabela só deixa o pet novo sempre
  no fim; as divisões cedo demais deixam grupos vazios.
- **MMO-10. O top tier diário é a Fábrica do dia,** com uma tentativa, os mesmos alugados e rivais para todos, e a semente de cada luta
  por conta, revelada depois da escolha. Pede a mudança em `motor/fabrica.ts`, atrás de chave. A outra opção é a luta do dia contra um
  rival fixo, sem mudar o motor. Custo de errar: médio. A luta do dia dá sempre o mesmo vencedor da semana; a semente igual para todos
  deixa a resposta vazar entre contas.
- **MMO-11. O top tier são os 10 primeiros do dia** (ou o 1 % de cima, com mais de 1 000 jogadores; PROPOSTO), com o selo datado no
  perfil. Custo de errar: baixo, é só a linha de corte.
- **MMO-12. O ranking paga prestígio, não Bits:** selos, títulos, o enfeite da temporada que não se vende e o mural. A outra opção é uma
  quantia fixa de Bits por participar, igual para todos. Custo de errar: médio. Bits pela colocação viram a espiral do melhor jogador; os
  Bits por participar são uma fonte nova ao lado da M-2.
- **MMO-13. A entrada:** no cais, do nível 10 do Tamer em diante (P-10), com o nível no registro do Tamer (P-5, opção T). **O marco do
  nível 10 é do Matheus:** recomendo o primeiro Mega, a sugestão da P-10. Custo de errar: baixo. Um marco cedo demais põe no ranking quem
  ainda não conhece a luta.
- **MMO-14. A versão da conferência:** o motor do servidor só muda na virada da semana, e um cliente de outra versão não envia. Custo de
  errar: médio. Mudar o motor no meio da semana muda a régua da tabela com a semana aberta.

**As duas pontuações e o reset** (seções 8 e 9, pedido do Matheus de 2026-11-10):

- **MMO-15. Duas pontuações, cada uma com o seu ranking:**
  - os pontos do Digimon, o total da vida do pet, com o máximo histórico dos Digimon;
  - o Respeito do Tamer, pelos feitos únicos e pelos resets, com o ranking dos Tamers.
  O nível do Tamer fica nos marcos 1 a 9, e do 11 em diante sobe a cada 1 000 de Respeito (PROPOSTO). Custo de errar: médio. Uma pontuação
  só mistura o pet e o jogador, e o veterano com um pet novo some da tabela.
- **MMO-16. O que é a "pontuação máxima":** **o recorde, sem teto**, com o título "Tamer Lendário" a partir de 10 000 (PROPOSTO). A outra
  leitura é um teto que para a conta. Custo de errar: baixo a médio. Com o teto, o topo da tabela empata, e só a data desempata.
- **MMO-17. O reset é do pet:** aposenta o Digimon em Gerações e choca um ovo, reaproveitando o `jornada.ts` e o `heranca.ts`. O Tamer
  fica com tudo (a tabela da seção 9), e o cruzamento também conta como reset. A outra leitura é o Tamer recomeçar do zero. Custo de errar:
  alto, se for o do Tamer. Ele apaga as medalhas e as compras com Bits e vai contra a M-8.
- **MMO-18. O bônus do reset:** **Respeito e Bits, sem herança de stats no motor.** Os níveis são o Ultimate, o Mega e o Mega com a Liga
  (300, 600 e 1 000 de Respeito; 150, 400 e 800 Bits; PROPOSTO). As travas são o mínimo de 200 pontos do Digimon conferidos para o Respeito
  e um reset pago em Bits por semana de relógio (PROPOSTO). A outra opção é a herança de stats do Digimon World. Custo de errar: médio. Sem
  as travas, recomeçar vira farm; com a herança de stats, o motor muda de versão, e o teto do estágio deixa de segurar o veterano.
- **MMO-19. Os Bits do reset entram como uma linha nova da M-2?** Recomendo **sim**, como os marcos de evolução, sem mexer nas outras
  linhas. A outra opção é o reset dar só Respeito. Custo de errar: baixo a médio. É uma fonte nova de moeda, e a rodada de equilíbrio a
  acerta junto com as outras (M-10).

## 15. Fora deste plano

- A troca entre jogadores (Bits, itens, pets).
- O chat livre e a luta ao vivo entre dois jogadores ao mesmo tempo.
- O dinheiro real, a caixa de prêmio e o gacha: nunca.
- Qualquer mudança no Python, no `engine.py` ou na pesquisa.
