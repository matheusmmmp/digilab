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
- **As decisões UX-CA-1 a 7 esperam o Matheus** (seção 7 do plano). A tela não foi feita.
- **Desvios:** D-UXCA-1 a 7, no registro.
