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
