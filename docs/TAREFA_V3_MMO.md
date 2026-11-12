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
