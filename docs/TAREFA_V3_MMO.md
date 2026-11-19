# TAREFA V3 — MMO (2026-11-10)

Coordenador: o Gerente da V3. Worker: o Gerente da frente MMO (Claude Code, Opus 5.5). Worktree e branch: `v3-mmo`. Status: ABERTA
(o plano entregue; as decisões MMO-1 a MMO-19 APROVADAS pela recomendação em 2026-11-11; as etapas de código seguem a
seção 12 do plano, cada uma com a sua prancha quando tiver tela).

Categoria: implementacao. Origem: Matheus, 2026-11-10: planejar um sistema multijogador com pontuação, ranking semanal, top tier diário e a ligação com os Bits.

O pedido, nas palavras dele: "planejamento de um sistema de MMO, no caso, aceitar múltiplos jogadores com pontuações de rankings, né?
Incorporando um possível sistema de moedas, rankings semanais e um top tier diário."

## 1. Pergunta

Como o jogo web, que hoje é de um jogador só, com o save no navegador, passa a aceitar vários jogadores num ranking semanal e num top tier
diário, com as pontuações conferidas pelo replay do log e sem desfazer as decisões dos Bits (M-1 a M-10)?

Não vem de uma hipótese do `docs/PLANO_V2_PESQUISA.md`: é do produto (`docs/PRODUTO_VISAO.md`, seção 4, as fases posteriores) e da P-10
do `docs/PLANO_V3_PROGRESSAO_TUTORIAL.md` (o multiplayer do nível 10 em diante). A pesquisa em Python não muda.

## 2. Depende de

- **Para o plano (esta entrega):** nada.
- **Para as etapas de código:**
  - as decisões MMO-1 a MMO-19 do Matheus (seção 14 do `docs/PLANO_V3_MMO.md`);
  - a moeda na `main`: o plano (#762) e a MO1 (#765), porque o registro do Tamer 9 é a base do registro que o servidor recebe;
  - a LP5 da luta (o equilíbrio, #759 e #763), porque a pontuação de luta não deve abrir sobre um equilíbrio que ainda vai mudar
    (o Gazimon trava o Rookie).

## 3. Mudança mínima

**Nesta entrega, só documentos:**
- `docs/PLANO_V3_MMO.md`, o plano;
- esta tarefa;
- a seção do desvio em `docs/registro/2026-11.md`.

As referências de outros jogos ficam no vault, em `20 Temas/Multijogador e rankings.md`.

**O que não muda,** nesta entrega e em nenhuma etapa sem decisão própria:
- o `engine.py` e o Python;
- o motor do pet (`web/app/motor/`) e o formato do save (`{semente, log, versao}`). A etapa MMO6, da Fábrica do dia, é a única que pede
  uma mudança no motor, atrás de chave, e leva a sua própria decisão (MMO-10);
- as versões de pet antigas e os gabaritos;
- as rotas do servidor local de hoje.

## 4. Experimento e gate (se houver run)

Não há run. A etapa MMO0 é uma medida de engenharia, não de pesquisa: quantos logs gravados no Chrome o Node refaz igual. Não usa faixa
de sementes reservada.

## 5. Entrega

- Testes: nenhum nesta entrega (só documento). Cada etapa de código traz os seus.
- Registro: `docs/registro/2026-11.md`, seção "2026-11-10 — MMO: o plano do multijogador". O índice `docs/REGISTRO_DESVIOS.md` fica com
  quem faz o merge (`python tools/gerar_indice_desvios.py`).
- PR contra a `main`, com o plano PROPOSTO e as decisões MMO-n. Merge só pelo Matheus.

## 6. Fora desta tarefa

- **O código** de qualquer etapa: ele só começa depois das decisões e das pranchas.
- **A troca entre jogadores:** os Bits, os itens e os pets.
- **O chat livre** entre jogadores e a luta ao vivo entre dois jogadores ao mesmo tempo.
- **O dinheiro real**, sempre (seção 10 do plano dos Bits).

## 7. Critérios de aceitação

- O `docs/PLANO_V3_MMO.md` existe e tem as seções pedidas:
  - o que existe hoje;
  - o que falta;
  - a pontuação;
  - o ranking semanal;
  - o top tier diário;
  - os Bits;
  - as duas pontuações, a do Digimon e o Respeito do Tamer, e o reset com bônus (pedido do Matheus de 2026-11-10, depois da primeira
    versão);
  - as etapas;
  - os riscos;
  - as decisões MMO-n, cada uma com a recomendação e o custo de errar.
- Cada número novo do plano está marcado PROPOSTO, SEM FONTE.
- O corpo do PR passa em `python tools/verificar_relato.py --arquivo F --base origin/main`.
- A página do vault existe, com as referências e os links.

## 8. Precisa do Matheus

As decisões MMO-1 a MMO-19, na seção 14 do `docs/PLANO_V3_MMO.md`, cada uma com a recomendação e o custo de errar.

## 9. MMO0: a medida Chrome × Node (2026-11-11)

Pedido do Matheus, pela sessão do Gerente UX_TELA_PET: "Segue a proxima etapa do mmo". Sem servidor e sem tela.

- **O que mede:** 20 vidas roteirizadas (`web/app/scripts/mmo0/vida.ts`), gravadas no Chrome instalado e conferidas no Node
  (`web/app/scripts/mmo0/conferir.ts`). As sementes são 101 a 110 com o DigiBrain modular e 111 a 120 com o cérebro A. O ovo nasce como
  no jogo (`src/produto.ts`, a `VERSAO_PET` 23).
- **O resultado** (`web/app/scripts/medicoes/mmo0_chrome_node.json`, commit `8095061a`, Chrome 156.0.8078.81, Node v24.19.0):
  - o Node aceita os 20 registros do Chrome, com 24 296 eventos;
  - as **4 561 lutas dão o mesmo resultado** nos dois: venceu, lesão, a vida que sobrou e os passos de cada luta da série;
  - o Node, vivendo o mesmo roteiro, grava **o mesmo registro** nas 20 vidas;
  - o estado do pet (`m.e`) sai igual nas 20;
  - **a assinatura sai diferente nas 20**, só no último bit: 48 números ao todo, com a maior diferença relativa de 6,4 × 10⁻¹⁵ e
    nenhum valor que não seja número. Os números ficam na confiança da luta (`conf.assinatura()`, nas 20) e no texto do cérebro
    (`pol.assinatura()`, em 6). A primeira divergência aparece entre o evento 34 e o 209.
- **O que isso diz à MMO-5:** a regra aprovada fica de pé. O servidor confere pelo replay e calcula os pontos pelas lutas, que saem
  iguais. Ele **não pode conferir pela assinatura**, que difere no último bit para um jogador honesto. Se uma luta um dia divergir, a conta
  do servidor vale, com o aviso.
- **A guarda:** `web/app/e2e/mmo0_chrome_node.spec.ts`, com duas vidas (101 modular e 111 A). Ela exige a mesma luta, o mesmo registro e
  a assinatura diferente só em número, abaixo de 10⁻¹² (PROPOSTO, SEM FONTE).
- **Os limites:** o roteiro não é um jogador. Ele não usa o tempo real, o "pular uma hora", a bola, levar o pet nem a troca de ilha. O
  celular não foi medido. Vinte vidas mostram que a divergência das lutas é rara, não que não existe.

## 10. MMO1: a conta dos pontos (2026-11-11)

Pedido do Matheus nesta sessão: "Faca o merge e siga para o proximo passo", depois do merge da MMO0 (#818). Sem tela e sem servidor.

- **O que entrega:**
  - `web/app/src/ranking/pontos.ts`, uma função pura fora do motor: do registro do pet e da lista das sementes que o servidor entregou,
    as lutas ranqueadas, os pontos, a semana e o dia de Brasília, e as linhas das tabelas da semana, com o desempate em quatro passos;
  - `web/app/scripts/conferir_ranking.ts`, o comando que confere um save exportado
    (`node scripts/conferir_ranking.ts --save F --entregues G`);
  - `web/app/test/ranking_pontos.test.ts`, 11 testes.
- **As regras, como o plano diz:**
  - a vitória pela faixa do rival (Rookie 10, Champion 20, Ultimate 40, Mega 80);
  - a repetida contra o mesmo rival na semana vale a metade da anterior;
  - a derrota, a semente não usada e a pendente valem 0 e contam como luta usada;
  - a 11ª semente do dia não conta;
  - a semente gasta fora da Arena não vale ponto;
  - a semana vai de segunda a domingo, no horário de Brasília (UTC−3).
- **A luta ranqueada é o evento "l" na posição pedida:** o pedido da semente leva o tamanho do registro naquela hora (`indice`), e a luta
  conta só se o evento nessa posição for a luta com essa semente. O hash do registro até ali fica para o servidor (MMO3 e MMO4).
- **Fora desta etapa:** o portão ★ (a MO2), o servidor e o registro do Tamer. O Tamer entra com o Respeito, na MMO8.

## 11. MMO2: o nível 10 no registro do Tamer (2026-11-12)

Pedido do Matheus: "segue para proxima etapa", depois do merge da MMO1 (#824). Na F0 do `docs/ROADMAP_V3_CONTA.md` (seção 9.1), ao lado
do servidor (CN1). O motor, o save do pet e as rotas não mudam.

- **O que entrega:**
  - **o marco 10, o primeiro Mega** (MMO-13): `ULTIMO_MARCO` passa a 10 em `web/app/src/nivel.ts`. O pet do jogador com a evolução a Mega
    cumpre o marco, e o registro do Tamer com o marco também;
  - **o registro do Tamer na versão 10** (P-5, opção T), em `web/app/src/tamer.ts`. Ela lê as versões 1 a 9 e traz o evento novo
    `"nivel"`: `{n: 10, quando, pet, forma, tick}`, com o pet que chegou ao Mega e o tick da evolução dele. O marco entra uma vez. Um registro
    de antes da 10 com o evento falha alto;
  - **a gravação:** o marco vai para o registro quando o nível é confirmado (`nivelTela.ts`, por `registrarMarcoMega` em `jogo.ts`), com os
    pets do jogador, o ativo e os guardados. O pet de exemplo intocado não conta, e o laboratório também não;
  - **a conferência do servidor:** `marcoConfere(marco, pet)`. O pet refeito do log dele (a semente do marco) tem a evolução a Mega no tick
    e na forma do marco. A MMO3 e a CN1 a usam no Node;
  - `web/app/test/tamer_nivel10.test.ts`, com 7 testes.
- **Os Bits do nível:** o nível 10 paga como os outros (`conferirBitsDoNivel`, a regra da M-2: cada nível do Tamer). Não é uma fonte nova.
  Como o nível é a contagem dos marcos, os Bits do nível 10 só saem com os dez marcos feitos.
- **Fora desta etapa:**
  - o cartão do marco 10 e o cais trancado e depois aberto: são a tela 1 das pranchas do MMO. Até a prancha ser aprovada, o marco conta em
    silêncio (sem cartão, só o som do nível novo e a contagem);
  - os marcos 1 a 9 continuam só na vista (MMO-15);
  - o nível do 11 em diante, pelo Respeito, fica para a MMO8.
- **O limite:** nenhum teste chega ao Mega pelo motor, porque leva dias de vida simulada. O teste põe a evolução a Mega à mão no registro
  das evoluções, que é a lista que o marco lê.

## 12. MMO3: o envio dos logs e a conferência no Node (2026-11-17)

Pedido do Matheus: "abre a MMO3 local" (2026-11-16), pela sessão que coordena a conta. A primeira etapa da F5 do
`docs/ROADMAP_V3_CONTA.md`, só a parte local, sobre a conta da CN2 (#948). Sem tela, sem prancha e sem deploy.

- **O que entrega:**
  - `POST /envios` e `GET /envios` no `servidor_web/` (`src/envio/rotas.ts`), com a sessão e o CSRF da conta: o envio
    `{pet: {semente, log, versao}, tamer: {versao, log}}`, até 5 MiB (PROPOSTO); recusa a versão desconhecida e falha alto com o motivo;
  - a conferência no Node (`src/envio/conferir.ts`): o pet e as lutas num passe só pela conta da MMO1 (`refazerComLutas`, o mesmo pet do
    `Motor.reproduzir`), o Tamer pelo `lerTamer` e o marco 10 por `marcoConfere` (MMO2), num worker (`src/envio/conferidor.ts`). Nunca pela
    assinatura, que difere no último bit (MMO0);
  - o banco (a migração 2): a linha de cada envio conferido (os hashes, o resultado, o marco, os pontos, o tempo) e os registros do envio
    aceito até 30 dias depois do fim da semana (MMO-4). Apagar a conta apaga os envios;
  - `servidor_web/test/envio.test.ts`, com 26 testes: o envio válido, o repetido, o log adulterado, o evento inventado, a versão do pet e a
    do Tamer, o Tamer que não reproduz, o marco que não confere e o de outro pet, a forma errada e a pontuação do cliente, sem sessão, sem
    CSRF, de outra origem, grande demais, sem JSON, a política do log, o "baixar os dados", apagar a conta, o mesmo pet nos dois replays e
    o worker (o mesmo resultado, o laço livre, a fila).
- **O tempo** (`servidor_web/medicoes/mmo3_conferencia.json`): na primeira versão, a conferência de uma vida da MMO0 levava de 0,58 a
  1,65 s com o DigiBrain modular (mediana 0,98 s), metade no replay e metade na conta dos pontos, que refazia o registro. Não são os 70 ms
  do plano (D-CONTA-84). Com o passe único (D-CONTA-85), ela leva de 0,26 a 0,68 s (mediana 0,43 s, 10 vidas; com o cérebro A, 0,25 s em
  3 vidas), e roda num worker, fora do laço de eventos (D-CONTA-86). Pedido do Matheus: "Segue com as recomendações".
- **No jogo:** o `src/chave.ts` (a chave do save e o armazenamento, sem dependências), para o `tamer.ts` rodar no servidor sem o React, e o
  `refazerComLutas` no `src/ranking/pontos.ts` (o `lutasRanqueadas` devolve o mesmo). O motor, o save e as telas não mudam.
- **Fora desta etapa:** a semente ranqueada, o limite por dia e a luta ranqueada (MMO4); as tabelas (MMO5); o save na nuvem (CN3); o cais,
  a entrada e o perfil (precisam de prancha); o deploy e os OAuth reais (CN5). Até a MMO4 não há semente entregue, e os pontos são 0.
- **Os limites:** o caminho do marco que confere não tem teste de ponta a ponta (nenhuma vida chega ao Mega no teste); a medida é da máquina
  do Matheus, não do Lightsail; um worker só, com os envios em fila.

## 13. MMO4: a luta ranqueada, a parte local (2026-11-17)

Pedido do Matheus: "Faz o merge e segue para a MMO4" (2026-11-17, depois do #960). Só o servidor e o protocolo do pedido no jogo. A
prancha, a prévia no cliente e o resultado na tela ficam para depois da prancha (seção 12 do `docs/PLANO_V3_MMO.md`).

- **O que entrega:**
  - `POST /sementes` e `GET /sementes` no `servidor_web/` (`src/envio/sementes.ts`), com a sessão e o CSRF da conta: o pedido
    `{pet: {semente, versao}, indice, hash}` devolve a semente da luta ranqueada, um HMAC do segredo da semana com a conta e o número da
    luta (MMO-6). A semente pedida conta como luta feita;
  - as travas do pedido: o nível (o marco 10 conferido, ou o 7 no beta, por `DIGILAB_MARCO_RANQUEADA`), o limite de 10 por conta por dia de
    Brasília pelo relógio do servidor (MMO-8), e a ordem (o `indice` não volta, não fica antes do registro já enviado, e o mesmo `indice`
    tem o mesmo hash);
  - no envio, a conferência confere o hash do registro até o `indice` de cada semente pedida (`hash_nao_confere`) e conta as lutas pela conta
    da MMO1 (vitória pela faixa, derrota, não enviada, pendente). Os pontos deixam de ser sempre 0;
  - o banco (a migração 3): `sementes` (pende da conta), `segredos_semana` (do servidor), e em `envios` as sementes usadas e os marcos do
    Tamer. Apagar a conta leva as sementes;
  - no jogo, `src/ranking/pedido.ts` (o hash do pedido, sem tela) e `src/marcosTamer.ts` (os marcos do Tamer, fora do `nivel.ts`);
  - `servidor_web/test/sementes.test.ts`, com 24 testes: a trava do nível (sem envio, poucas medalhas, o marco 10 do padrão, o marco
    inválido), a semente (a resposta, o pedido do jogo igual ao do servidor, o HMAC, um segredo por semana, sem sessão, sem CSRF,
    malformado, a versão), o limite do dia (a 11ª, o dia seguinte, a virada às 03:00 UTC), a ordem (fora de ordem, o hash diferente, o
    indice já enviado, o relógio que recua), o envio com a semente (a luta que conta, a pendente, a não enviada, o registro mudado, o
    worker, apagar a conta, o "baixar os dados") e o hash do prefixo.
- **Desvios:** D-CONTA-87 a 92.
- **Fora desta etapa:** a prancha e as telas da luta ranqueada (a prévia e o resultado do servidor); fechar as pendentes como derrota no fim
  da semana, as tabelas, o congelamento e o segredo publicado (MMO5); o deploy (CN5).
- **Os limites:** no beta, as medalhas do registro do Tamer não são conferidas contra o pet, e um registro escrito à mão abre o pedido (sem
  dar pontos; D-CONTA-89); o caminho do marco 10 que confere segue sem teste de ponta a ponta (nenhuma vida chega ao Mega no teste); a
  luta ranqueada do teste é uma só, a primeira da Arena da vida 101.

## 14. MMO4: a prancha da luta ranqueada (2026-11-17)

Pedido do Matheus: "Sim, a prancha" (2026-11-17). O plano de UX é o `docs/PLANO_UX_LUTA_RANQUEADA.md` (PROPOSTO), e a prancha está em
`docs/pranchas/ux-luta-ranqueada/`: a aba Arena com a escolha "Treino / Ranqueada", os seis estados do pedido e os cinco resultados, no
desktop (1920) e no celular (390 e 360), nas peles Vidro e Militar. Só desenho. Desvios: D-UXLR-1 a 8.

**As UX-LR-1 a 6 foram APROVADAS pelas recomendações** (Matheus, 2026-11-17: "Sim, aprovo"): a luta na aba Arena, o aviso acima do
botão, a prévia que vira "conferido", o reenvio sozinho e o rival escolhido pelo jogador. A tela ainda não foi feita.

## 15. MMO4: a tela da luta ranqueada (2026-11-17)

Pedido do Matheus: "Sim, merge e tela" (2026-11-17), depois do merge do #967. A tela segue a prancha aprovada
(`docs/PLANO_UX_LUTA_RANQUEADA.md`, UX-LR-1 a 6).

- **A chave:** a luta ranqueada só aparece no build com `VITE_DIGILAB_API` (o endereço do `servidor_web`), com um pet só na tela. Sem
  ela, a Arena é a de sempre.
- **O cliente (`web/app/src/ranking/ranqueada.ts`):** o pedido da semente e os estados dele, a prévia, o envio depois da luta e o
  reenvio; a lista das lutas pedidas fica no aparelho (`CHAVE-ranqueada`). Sem React; 15 testes com o servidor falso.
- **A tela (`web/app/src/telas/lutar/palcoPoc/TelaRanqueada.tsx`, `src/estilo/ranqueada.css`):** a escolha "Treino / Ranqueada", o
  placar, os rivais com o valor, o aviso e "Lutar valendo N"; os estados do pedido; o resultado ("prévia", "conferido", "o servidor").
- **O motor não muda:** a luta é o `lutarPoc` de sempre com a semente do servidor. O pedido segura o tempo do jogo até a luta entrar no
  registro (`segurarTempoDoPedido`, em `lutaPocTela.ts`).
- **O servidor:** o 403 `nivel_insuficiente` passa a dizer o `marco`.
- **Conferido no navegador** (Chrome headless, o `servidor_web` local com o provedor falso): sem conta, trancada, o pedido, a luta no
  palco, o envio, "conferido +20", o placar da semana e o mesmo rival valendo 10 em seguida.
- **Não feito:** as telas da conta (o Entrar só abre a página de teste no local), "Ver a semana" (MMO5), o e2e no repositório e a
  revisão de acessibilidade. Desvios: D-CONTA-93 a 103.

## 16. MMO5: o ranking da semana, a parte local (2026-11-17)

Pedido do Matheus: "Sim, a MMO5" (em resposta a "Começo a MMO5 (as tabelas e o cais)?"). Esta etapa é só o servidor; a tela (o cais e
"Ver a semana") pede a prancha antes. Branch `v3-mmo5-local`.

- **O que o servidor passa a guardar (a migração 4):** em cada semente entregue, o que a conferência do envio achou dela (a situação, o
  estágio do pet, o rival e a faixa); no segredo da semana, quando ele foi publicado; e as tabelas congeladas (`tabelas_semana`).
- **As tabelas (`servidor_web/src/envio/semanas.ts`):** uma por estágio (Rookie, Champion, Ultimate, Mega), na ordem do desempate da
  seção 5: os pontos, os rivais diferentes vencidos, menos lutas usadas, quem chegou antes aos pontos. Os pontos são refeitos pela conta
  da MMO1 (`pontuar`, agora exportada de `web/app/src/ranking/pontos.ts`), por pet, e os pets da conta somam.
- **A primeira conferência vale:** a semente que já tem vitória, derrota, não enviada, fora da Arena ou acima do limite não muda num
  envio seguinte. Só a pendente e a nunca conferida mudam.
- **O fechamento:** a semana congela uma hora depois do fim (segunda, 01:00 de Brasília). Numa transação: a pendente e a nunca
  conferida viram "não enviada", as tabelas são gravadas, e o segredo é publicado. Roda sozinho na primeira chamada depois da hora
  (as rotas das semanas, o envio e o pedido da semente).
- **As rotas:** `GET /semanas` (a semana aberta, quando fecha e as fechadas), `GET /semanas/:semana/tabelas` (com a sessão; as 100
  primeiras linhas de cada estágio e a de quem pede) e `GET /semanas/:semana/segredo` (sem sessão; 404 com a semana aberta).
- **O que não muda:** o motor e o `engine.py`. A conferência do envio devolve o mesmo de antes.
- **Testes:** `servidor_web/test/semanas.test.ts` (29): a migração, a semana, a regra da metade, o desempate passo a passo, o
  fechamento, as rotas e o caminho inteiro do pedido à tabela. `servidor_web`: 127 passaram; `web/app`: 1 981 passaram, 3 pulados.
- **Fora desta etapa:** a prancha e a tela (o cais, "Ver a semana"); as divisões de 30 (MMO-9, só com 60 jogadores); a recompensa
  (MMO7); o deploy (CN5). Os desvios e os achados estão no registro (D-CONTA-114 a 122).

## 17. MMO4: o rival e o mapa no pedido da semente (2026-11-17)

Decisão do Matheus: "Sim, levar" (em resposta a "O pedido da semente passa a levar o rival e o mapa?"; o achado D-CONTA-116).
Branch `v3-mmo4-rival`, por cima da `v3-mmo5-local` (#978).

- **A regra:** o jogador escolhe o rival e o mapa antes de a semente existir. O `POST /sementes` passa a pedir `rival` e `mapa`, o
  servidor os guarda na semente (a migração 5) e os devolve. No envio, a luta do indice só conta se é contra esse rival, nesse mapa;
  senão a semente fica "não enviada" (0 pontos, luta usada).
- **No servidor:** `servidor_web/src/envio/sementes.ts` (o pedido, a coluna, a resposta) e `conferir.ts` (passa o rival e o mapa à
  conta). O pedido sem `rival` ou sem `mapa` leva 400.
- **Na conta dos pontos:** `web/app/src/ranking/pontos.ts`: a semente entregue leva o rival e o mapa prometidos; a semente sem rival
  guardado (de antes da regra) não confere nada.
- **No jogo:** `pedido.ts`, `ranqueada.ts` e `TelaRanqueada.tsx` mandam o rival e o mapa escolhidos na Arena. A tela não muda.
- **O que não muda:** o motor e o `engine.py`.
- **Testes:** `servidor_web`: 134 passaram (7 novos em `test/sementes.test.ts`: o 400, o que se guarda, a luta que conta, o outro
  rival, o outro mapa, a semente de antes da regra). `web/app`: 1 981 passaram, 3 pulados; os tipos e o build.
- **O que fica:** o servidor não sabe se o rival está na Arena do pet na hora do pedido; o motor confere isso no envio, e a luta
  impossível recusa o envio inteiro. Os desvios estão no registro (D-CONTA-123 a 126).

## 18. MMO5: a prancha do cais e da semana (2026-11-17)

Pedido do Matheus: "Sim, a prancha" (em resposta a "Faço a prancha do cais e de 'Ver a semana' agora?"). Branch `v3-mmo5-prancha`. O
plano de UX é o `docs/PLANO_UX_CAIS.md` (PROPOSTO), e a prancha está em `docs/pranchas/ux-cais/`. Só desenho.

- **As telas:** a semana aberta (as datas, o estado, os quatro estágios, as primeiras linhas e a de quem olha), os seis estados, a
  semana fechada com o resultado de quem olha, "Conferir a semana" (o segredo publicado), o cais trancado e o cartão de destrave do
  nível 10. No desktop (1920) e no celular (390 e 360), nas peles Vidro e Militar.
- **De onde vem cada dado:** das três rotas de `servidor_web/src/envio/semanas.ts` (#978, na main).
- **As UX-CA-1 a 7 foram APROVADAS pelas recomendações** (Matheus, 2026-11-17: "Sim, aprovo"; seção 7 do plano). A tela não foi feita.
- **Desvios:** D-UXCA-1 a 8, no registro.

## 19. MMO5: a tela do cais (2026-11-17)

Pedido do Matheus: "Sim, os dois" (em resposta a "Faço o merge do #983 com o CI verde e começo a tela do cais?"). Branch `v3-mmo5-tela`.
A prancha é a `docs/pranchas/ux-cais/` (APROVADA, UX-CA-1 a 7).

- **A chave:** `VITE_DIGILAB_API` no build, a mesma da conta e da luta ranqueada. Sem ela, o cais continua sem menu, o marco 10 conta em
  silêncio e nada muda.
- **O cliente** (`web/app/src/cais/cais.ts`, sem React): as três rotas de `servidor_web/src/envio/semanas.ts`, os estados (buscando, sem
  resposta, sem conta, pronto), a troca de semana, "Ver todas" e o segredo. As contas da tela são puras: o texto da semana, quanto
  falta, "fechando" (deduzido do `fecha_em` e do `congela_em`) e as linhas de cima mais a de quem olha.
- **A tela** (`web/app/src/telas/cais/TelaCais.tsx`, `src/estilo/cais.css`): em `#/cais`, fora dos destinos, no painel dos Ajustes (sem
  abas e sem a viagem da câmera). 8 linhas a partir de 900 px e 6 abaixo; no celular a folha é mais alta e a coluna "Lutas" sai.
- **Por onde se entra:** o toque no cais na ilha (`ToqueLugar.tsx`), o cartão do nível 10, "Ver a semana" no limite de hoje da Arena
  (`TelaRanqueada.tsx`) e o endereço.
- **A trava:** o cais abre pelo marco do build (`VITE_DIGILAB_MARCO_RANQUEADA`; vazio, o 10). Trancado, o toque e o endereço abrem o
  cartão do motivo ("Nv 10 · Abre com o primeiro Mega").
- **O cartão de destrave** (`nivel.ts`, `CARTAO_DO_CAIS`): "Cais" e "Veja o ranking da semana.", só com o cais ligado e o marco 10.
- **O que não muda:** o motor, o `engine.py`, o registro e o save. O cais só lê o servidor.
- **Testes:** `web/app`: 2 002 passaram, 3 pulados (20 novos em `test/cais.test.ts` e 1 em `test/ilha_lugares.test.ts`); os tipos e o
  build.
- **No navegador** (Chrome, o servidor e o jogo locais): o cais trancado, o cartão de destrave, sem conta (o 401 do servidor de
  verdade), Entrar, as tabelas vazias do servidor de verdade, e, com respostas de exemplo, a semana aberta, "Ver todas", o estágio sem
  luta, a semana fechada, o segredo, o celular (390 e 360, sem rolar), "Ir para a Arena" e sem resposta.
- **Não feito:** o botão do cais no minimapa, o cadeado "Nv 10" sobre o cais na ilha e a luz do modelo quando abre (os três pedem a
  vista 3D); a viagem da câmera até o cais; o e2e no repositório. Os desvios estão no registro (D-CONTA-127 a 133).

## 20. MMO5: o cais na ilha 3D (2026-11-18)

Pedido do Matheus: "Sim, a ilha 3D" (em resposta a "Faço agora o cais na ilha 3D (minimapa, cadeado e luz)?"). Branch
`v3-mmo5-cais-3d`. São os três itens da prancha que a seção 19 deixou de fora.

- **A chave:** a mesma (`VITE_DIGILAB_API`). Sem ela, o cais fica como sempre foi: sem cadeado, sem marca no minimapa e com o modelo
  normal.
- **O estado para a vista** (`web/app/src/trancas.ts`, `CAIS`): ligado ou não, trancado ou não. Quem escreve é o `nivelTela.ts`, pelo
  marco do build.
- **O cadeado** (`web/app/src/componentes/CadeadoDoCais.tsx`): o mesmo desenho dos outros lugares, com "Nv 10"; tocar nele abre o cartão
  do motivo. Quando o nível abre o cais, o cadeado aberto e o brilho aparecem uma vez.
- **O minimapa** (`Minimapa.tsx`): a marca do cais (a âncora); trancado, tracejada, com o cadeado e o "Nv 10", e a frase na descrição
  para o leitor de tela. A marca não é botão, como as dos outros lugares.
- **O modelo** (`ilha/vista.ts`): trancado, o cais sai apagado como os outros lugares trancados; aberto, volta ao normal. O cais não tem
  parte que acende (`LUGARES_LUZ`), então não há máscara de luz para ligar.
- **O que não muda:** o motor, o `engine.py`, o registro e o save. É só vista.
- **Testes:** `web/app`: 2 003 passaram, 3 pulados (1 novo, o estado do cais em `test/cais.test.ts`); os tipos e o build.
- **No navegador** (Chrome, com a câmera de desenvolvimento no cais): com a chave e trancado, o cadeado, a marca tracejada e o modelo
  apagado, e o cadeado e o toque no modelo abrem o cartão do motivo; com a chave e aberto, sem cadeado, a marca cheia e o toque abre a
  tela; sem a chave, nada do cais.
- **Não feito:** o foco de luz no chão do cais aberto (a hierarquia de luz é montada uma vez, no carregamento); a viagem da câmera até
  o cais; o brilho de "acabou de abrir" não foi visto no navegador. Os desvios estão no registro (D-CONTA-134 a 137).

## 21. MMO5: o e2e do cais (2026-11-18)

Pedido do Matheus: "Sim, o e2e" (em resposta a "Faço agora o e2e do cais com o servidor falso?"). Branch `v3-mmo5-cais-e2e`. Só teste:
nenhum arquivo de `web/app/src` nem do motor muda.

- **Por que um e2e à parte:** o `npm run e2e` roda o build sem a chave do servidor, onde o cais não existe. O e2e novo monta outro build,
  com a `VITE_DIGILAB_API`, em `web/dist_conta/` (não versionado), e o serve pelo servidor local. O `web/dist/` e o e2e do jogo não mudam.
- **O comando:** `cd web/app && npm run e2e:conta` (`playwright.conta.config.ts`, pasta `e2e_conta/`, porta 8801 ou
  `DIGILAB_PORTA_E2E_CONTA`).
- **O servidor falso:** o `servidor_web` não sobe. Cada teste responde as rotas das semanas com o `page.route`, num caminho da mesma
  origem da página (`/api_falsa`). Nenhum endereço de servidor de verdade e nenhuma chave entram no repositório.
- **O que o `e2e_conta/cais.spec.ts` cobre** (6 testes, o Champion de `e2e/saves.json`, o relógio da página parado numa quarta-feira):
  - trancado, a 1920 px: a marca tracejada do minimapa, o cadeado "Nv 10" sobre o cais, e o cadeado e o endereço `#/cais` abrindo o
    cartão do motivo, sem nenhuma chamada ao servidor;
  - aberto, a 1920 px: a semana, a tabela do estágio do pet, a linha de quem olha depois do salto, "Ver todas", os outros estágios,
    "Atualizar", a semana fechada com o resultado, "Conferir a semana" (o segredo) e "Ir para a Arena";
  - sem a conta (401) e sem resposta (a rede fora), e a volta com "Tentar de novo";
  - a folha do celular (390 px): 6 linhas, sem a coluna das lutas, sem rolagem de lado;
  - trancado no celular: o endereço abre o cartão do motivo;
  - o cartão de destrave do nível 10 e o "Ir" dele.
- **Resultado:** os 6 passaram, em duas rodadas seguidas. `web/app`: os tipos e o `npm test` como antes (nenhum teste novo no Vitest).
- **Fora do e2e:** o brilho de "acabou de abrir" (pede um save de Mega, que o `e2e/saves.json` não tem), o toque no modelo 3D do cais,
  "Ver a semana" na Arena (pede o servidor falso da luta ranqueada), a tela da conta e a luta ranqueada. O e2e fica fora do CI, como o
  do jogo (D-IA-3). O desvio está no registro (D-CONTA-138).

## 22. MMO6: o desafio do dia, a parte local (2026-11-18)

Pedido do Matheus: "Sim, abre a MMO6". Branch `v3-mmo6`. Só o motor atrás da chave e o servidor; a prancha e a tela pedem a aprovação
antes do código.

- **No motor (`web/app/motor/fabrica.ts`):** a Fábrica do dia, `TentativaFabrica.doDia(escolha, semente do dia, sementes das lutas)`. Os
  3 alugados e os rivais saem da semente do dia; a semente de cada luta vem de fora, uma por vez (`receberSemente`), e `proximoRival`
  mostra o rival antes da semente. A chave é a ausência das sementes de fora: o construtor de sempre sai byte a byte igual ao gabarito de
  40 tentativas gravado antes (`test/gabaritos/mmo6_fabrica_hoje.json`, commit c45766d1). As regras da luta não mudam.
- **A conta pura (`web/app/src/ranking/desafio.ts`):** o registro `{v, escolha, lutas, trocas}`, o replay pelo motor, o desempate (mais
  vitórias, mais vida no fim da última vitória, quem terminou antes) e o número de selos.
- **No servidor (`servidor_web/src/desafio/desafio.ts`, a migração 6):**
  - a semente do dia, igual para todos, HMAC do segredo do dia (um por dia de Brasília, no banco, fora do git);
  - uma tentativa por conta por dia: `POST /desafio/tentativa` já a gasta, e a segunda leva 409;
  - as sementes das lutas, da conta, só depois da escolha: `POST /desafio/lutas` guarda a escolha e as trocas prometidas;
  - o envio conferido pelo replay (`POST /desafio/envios`), com o resultado e o motivo guardados;
  - a tabela do dia (`GET /desafio/:dia/tabela`), congelada uma hora depois do fim do dia com o selo dos primeiros (MMO-11), os selos da
    conta (`GET /desafio/selos`) e o segredo publicado (`GET /desafio/:dia/segredo`);
  - apagar a conta leva tudo dela, e o "baixar os meus dados" traz o desafio.
- **Testes:** `servidor_web`: 155 passaram (21 novos em `test/desafio.test.ts`). `web/app`: os 47 novos de `test/mmo6_fabrica_hoje.test.ts`
  e `test/mmo6_fabrica_do_dia.test.ts`, mais a suíte inteira (a contagem está no PR).
- **O achado (D-CONTA-150):** em 80,7 % dos pares (dia, alugado), a primeira luta dá o mesmo resultado com a semente de qualquer conta
  (`servidor_web/medicoes/mmo6_sorte_do_dia.json`). A dica de um jogador vale para os outros nesta luta. Vai ao Matheus.
- **O que não muda:** o `engine.py`, a Fábrica de sempre, o registro do Tamer e as telas.
- **Fora desta etapa:** a prancha e a tela; as recompensas e o mural (MMO7); o reset (MMO8); o deploy. Os desvios estão no registro
  (D-CONTA-139 a 151).

## 23. MMO7: as recompensas e o mural, a parte local (2026-11-19)

Pedido da sessão da conta (a linha da MMO7 na seção 12 do plano, a MMO-12 e a seção 7). Branch `v3-mmo7`. Local, sem deploy. O ranking
paga prestígio, não Bits: nada aqui toca os Bits, a loja, o motor, o registro do Tamer nem o save.

- **No servidor (`servidor_web/src/premios/premios.ts`, a migração 7):**
  - os recordes de todos os tempos da Torre, da Fábrica e do Salão, só do que a conferência do envio aceito refaz (D-CONTA-152): a Torre
    pelo replay do pet, a Fábrica pelo replay do Tamer, o Salão juntando as lutas vistas no replay de cada pet (`recordes`, `salao_vistas`);
  - o título da semana: o 1º com pontos de cada tabela congelada da MMO5, "Campeão Rookie da semana 46", no perfil por 7 dias depois do
    congelamento e no mural para sempre (D-CONTA-153 e 155);
  - o selo "Top do dia": o que o fechamento do dia da MMO6 já marca, lido daqui;
  - o enfeite da temporada: um por temporada de 4 semanas para quem ficou entre os 10 primeiros com pontos de uma tabela da semana
    (D-CONTA-154);
  - o Respeito conferido: só o título da semana (100) e o selo (20), os valores da seção 8; o resto é da MMO8 (D-CONTA-156);
  - `GET /premios` (o que a conta ganhou) e `GET /mural` (os recordes e os títulos), com a sessão; o "baixar os meus dados" traz os
    recordes; apagar a conta leva tudo.
- **No jogo:** "Mural e prêmios" no cais (`src/cais/premios.ts`, `TelaCais.tsx`), o mínimo nas peças do cais, sem prancha; e a taça da
  temporada em cartoon por script (`docs/objetos3d/cartoon/trofeu.py`, `public/enfeites/trofeu/`), posta perto do cais só quando o servidor
  diz que a conta a ganhou (`ilha/premiosConta.ts`, `ilha/premiosCena.ts`, `TACAS_DA_CONTA` em `trancas.ts`). Sem a chave do cais, nada
  disso existe; com o cais trancado, o jogo não chama o servidor (D-CONTA-157).
- **Testes:** `servidor_web`: 170 passaram (15 novos em `test/premios.test.ts`). `web/app`: a suíte inteira e os tipos (a contagem está
  no PR; 15 novos em `test/premios_cais.test.ts`); `npm run e2e:conta`: 9 passaram (3 novos em `e2e_conta/mural.spec.ts`, com as fotos da
  taça na ilha e do mural a 1920 e a 390 px).
- **Pendente com o Matheus:** a prancha do mural e dos selos no perfil; o desenho da taça de cada temporada; os números PROPOSTOS
  (D-CONTA-152 a 159).
- **Fora desta etapa:** o Respeito das medalhas, da Liga e do reset e o ranking dos Tamers (MMO8); as telas da conta; o deploy. Os
  desvios estão no registro (D-CONTA-152 a 160).

## 24. MMO8: a prancha do reset e das duas pontuações (2026-11-19)

Pedido da sessão da conta (a linha da MMO8 na seção 12 do plano, as seções 8 e 9, as MMO-15 a MMO-19). Branch `v3-mmo8-prancha`. O plano
de UX é o `docs/PLANO_UX_RESET.md` (PROPOSTO), e a prancha está em `docs/pranchas/ux-reset/`. Só desenho.

- **O reset:** Aposentar em Meus pets (o pet, a escada do nível do reset, o bônus com as duas travas, o que vai para Gerações e o que fica),
  a confirmação, o reset feito e os seis estados (sem bônus, nível 2, nível 3, sem os 200 pontos, Bits da semana já pagos, sem conta).
- **O perfil com as duas pontuações:** o Respeito do Tamer (o conferido e o do jogo, o nível, a barra até "Tamer Lendário"), os pontos do
  melhor Digimon e a posição, de onde vem o Respeito; os dois rankings como abas do cais; os quatro estados.
- **As capturas:** a 1920 × 950 e a 390 × 844, nas peles Vidro e Militar.
- **Desvios:** D-UXRS-1 a 6, no registro. **Decisões:** UX-RS-1 a 7, esperam o Matheus. A tela não foi feita.

## 25. MMO8: as duas pontuações e o reset, a parte local (2026-11-19)

Pedido da sessão da conta (a linha da MMO8 na seção 12 do plano, as seções 8 e 9, as MMO-15 a MMO-19). Branch `v3-mmo8`. Local, sem
tela e sem deploy; a prancha está num PR à parte (seção 24) e espera o Matheus.

- **No jogo:**
  - o evento `"reset"` no registro do Tamer (`src/tamer.ts`, versão 11), atrás da chave `RESET_LIGADO` (desligada; o gabarito dos
    registros de hoje veio num commit anterior, `test/gabaritos/mmo8_tamer_hoje.json`);
  - os Bits do reset, a origem nova `"reset"` (MMO-19), um reset pago por semana de relógio (`pagarReset`);
  - a conta pura em `src/ranking/pontos.ts`: o nível do reset (`nivelDoReset`), o bônus (`BONUS_RESET`), os pontos do Digimon
    (`pontosDoDigimon`), o Respeito (`respeito`, `respeitoDoReset`, `respeitoLocal`), o nível do 11 em diante (`nivelPeloRespeito`) e
    "Tamer Lendário" (`tituloDoRespeito`);
  - `src/reset.ts`: a prévia, o evento e o reset do pet ativo, reaproveitando o `heranca.ts` (`aposentar`) e o `jornada.ts`
    (`chocarDoBrasao`); o cruzamento registra o reset do pai. Nada chama o reset com a chave desligada.
- **No servidor (a migração 8, `src/premios/rankings.ts`):**
  - a conferência diz o Digimon (os pontos da vida, o estágio, a forma, o nível do reset), os feitos do Tamer vistos no replay do pet e o
    reset no registro final do pet (`reset_nao_confere`);
  - o envio aceito grava o máximo histórico dos Digimon (`digimons`), os resets (`resets`) e os feitos (`feitos_tamer`);
  - o Respeito conferido inteiro, ligado ao da MMO7 (os títulos e os selos), com a trava dos 200 pontos;
  - `GET /digimons` e `GET /tamers`, com a sessão; o "baixar os dados" traz as pontuações; apagar a conta leva tudo.
- **Desvios:** D-CONTA-161 a 170, no registro.
- **Fora desta etapa:** as telas (Aposentar, o perfil, as abas do cais), o envio sozinho do registro do aposentado (UX-RS-4), o nível na
  tela e os Bits do nível 11 em diante (UX-RS-6), o reset do par (D-CONTA-161), o legado de stats da revisão CR-7 e CR-8 do
  `docs/PLANO_V3_CICLO.md` e o deploy.

