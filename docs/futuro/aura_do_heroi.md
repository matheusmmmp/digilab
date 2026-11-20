# Aura do herói — conhecimento de batalha emprestado por tempo limitado

Status: **IDEIA / CONTEXTO** (2026-10-03). Proposta do Matheus. Este documento registra a ideia e o que ela toca no jogo que
existe. Ele **não autoriza implementação**, não é um desenho fechado e não muda nenhum experimento. Os números de jogo
citados são do `CLAUDE.md` da `main` em 2026-10-03.

## 1. A ideia

Um pet que lutou muito acumula conhecimento de batalha. Tira-se um retrato (snapshot) desse conhecimento num momento e
ele vira um item na loja, por exemplo a **Aura do herói**. Comprar o item dá a outro pet acesso a essa rede de
conhecimento por pouco tempo: um item usável que vale por **duas batalhas**, depois se esgota.

## 2. Onde a ideia encosta no que já existe

| peça | o que é hoje | relação com a aura |
|---|---|---|
| **Gambits híbridos** (web) | o conhecimento de batalha de um pet é a lista de gambits: regras, ordem e a nota de cada regra, aprendidas nas lutas contra bot; o dono só trava ou veta; tudo no registro, o replay reconstrói | é o que o retrato copiaria |
| **Chips de regra** (web, `motor/itens.ts`) | um chip põe uma regra de um catálogo fechado na lista do pet; 1 por pet; vale na Liga e na Torre, não no Palácio | a aura é um "chip de lista inteira", com prazo |
| **Confiança M1** (Python e web, chave) | estado por rival derivado das lutas do registro | decidir se entra no retrato (seção 4) |
| **PvP com ghost** (`docs/TODO_INTERACAO_CORPO.md`) | uma das alternativas é a "cópia congelada do controlador e do estado relevante" | é a mesma peça técnica: um controlador congelado que reage numa luta nova |
| **Equipamento** (`docs/PESQUISA_VIDA_LINHAGEM_PROGRESSAO.md`, seções 17 e 29) | regra de desenho: o bônus fica bem abaixo da diferença entre estágios, de preferência muda comportamento, e o raro vem de feitos | a aura cumpre "muda comportamento"; o prazo de duas lutas ajuda no teto |
| **Loja e moeda** | **não existem** no jogo | a aura depende da economia, que também é ideia (seção 29, item 1) |

## 3. Desenho mínimo possível (para discutir, não decidido)

- **Retrato:** congelar a lista de gambits do herói (regras, ordem e notas) num instante, com o identificador do herói, a
  data do relógio do pet e um hash do conteúdo.
- **Item:** "Aura de \<nome do herói\>", com **2 cargas**. Cada luta com a aura ligada gasta uma carga.
- **Durante a aura:** o pet luta com a lista do herói no lugar da dele. Corpo, stats, forma e técnicas continuam os dele.
- **Compatibilidade:** a lista emprestada passa pelo mesmo filtro da semente de evolução: cabe na capacidade do estágio
  (3/5/8) e só usa condições do estágio e a técnica da própria linha. Regra que não cabe cai.
- **Registro:** eventos novos (comprar, ativar, gastar carga), com o retrato inteiro no log ou referenciado pelo hash e
  guardado junto. Sem isso o replay bit a bit quebra.
- **Versão:** uma versão de pet própria na web, como toda mecânica nova.

## 4. Decisões em aberto

| # | pergunta | opções |
|---|---|---|
| 1 | De quem vem o retrato? | pets do próprio jogador (inclusive mortos ou aposentados); heróis e líderes do jogo; pets de outros jogadores (pede servidor) |
| 2 | Substitui ou soma? | lista do herói no lugar da do pet; ou a lista do pet com as regras do herói na frente |
| 3 | O pet aprende durante a aura? | não aprende (as lutas com aura não ensinam, como as lutas contra pet de cenário); ou aprende só a própria lista, guardada de lado |
| 4 | Onde vale? | Liga e Torre, como os chips; provavelmente **não** no Palácio, onde o pet decide sozinho |
| 5 | Entra a confiança M1 do herói? | só a lista de gambits; ou lista e confiança |
| 6 | Como se compra? | moeda da economia futura; ou recompensa de feito (regra da seção 17: o raro vem de feitos) |
| 7 | O herói perde algo ao ser retratado? | nada; ou o retrato só existe depois da morte ou da aposentadoria, como legado da linhagem |

## 5. Riscos

- **Substituir a criatura.** É o risco que a seção 17 da pesquisa de progressão já aponta para equipamento. O prazo curto
  e o filtro de compatibilidade são os freios.
- **Pode valer pouco.** No E1 a forma final explicou 96% da taxa no painel (`artifacts_linhagem/dono_ambiente/resultado.json`).
  Se a forma domina, emprestar a lista muda pouco a vitória. Isso é medível antes de construir.
- **Equilíbrio.** Pela regra do projeto, nada de calibrar agora; o efeito entra na rodada de equilíbrio geral.
- **Exploração.** Com retratos de outros jogadores, uma lista forte pode virar a "aura de todos". Seria a espécie
  dominante do E2, só que em comportamento.

## 6. Leitura de pesquisa

A aura é um transplante: a mesma lista aprendida em corpos diferentes. Isso separa quanto do desempenho vem do que foi
aprendido e quanto vem da forma, o que conversa com a pergunta maior da V2 (plasticidade durante a vida × predisposição
herdada). É uma medida possível, não um experimento planejado.

Limites de alegação (skill `literatura-digilab`): não houve busca bibliográfica sobre transferir conhecimento aprendido entre
agentes de jogo, então **nada aqui pode ser dito como novo**. O precedente verificado mais próximo é a troca de criaturas
inteiras entre jogadores no Creatures (Cliff e Grand 1999, `10.1162/106454699568683`), que troca o indivíduo, não um
retrato emprestado do comportamento dele.

## 7. Onde entra

Mecânica de **produto** (web), não da fase 1 de pesquisa. Depende de: loja e moeda (ideia), chips (executado) e, se o
retrato vier de outros jogadores, do servidor (fase 4 do plano da V2). Divide a peça técnica com o PvP com ghost; se um
dos dois for adiante, o outro aproveita o retrato congelado. Próximo passo, se aprovado: uma tarefa que responda às
decisões da seção 4 e meça, nas sementes de calibração, quanto uma lista emprestada muda a vitória por forma, antes de
qualquer código.
