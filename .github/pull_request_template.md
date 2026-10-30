Tarefa: `docs/TAREFA_V2_<FRENTE>.md` ou `docs/TAREFA_V3_<FRENTE>.md`
Categoria: <implementacao | experimento | literatura | arquitetura | documentacao>
Executor: <Claude Code (sessão, worktree) | Codex | ChatGPT Work | Matheus>
Branch: `v2-<frente>` ou `v3-<frente>`. Commit base: `<sha curto da main de onde saiu>`

<!--
O relato de volta (docs/modelos/TAREFA_V2_MODELO.md, seção 5). O CI confere com tools/verificar_relato.py:
- campos acima e seções abaixo preenchidos (sem os <...> do modelo);
- a evidência da categoria (docs/infra/GUIA_OPERACIONAL.md, seção "O que o CI confere");
- o que você escreve em "Evidências declaradas" é DECLARADO: uma saída de teste colada aqui não conta como prova. Prova é o que o job do CI
  confere ou roda sozinho.
Escreva "nenhum" ou "nenhuma" onde não houver nada; não apague a seção.
-->

## O que é

<O que mudou e por quê, em poucas linhas, para quem não viu a sessão.>

## Arquivos

- **Novo:** <caminho>, <papel>.
- **Alterado:** <caminho>, <o que mudou>.

## Evidências declaradas

- Testes rodados: <comando exato> → <contagem>. Ou "não rodados", com o motivo.
- Números: <cada número com o caminho do artefato que o produz>.

## Desvios

<Link para a seção em `docs/registro/AAAA-MM.md`, ou "nenhum".>

## Decisões do Matheus

<Cada uma com a recomendação e o custo de errar, ou "nenhuma".>

## Questões abertas

<O que ficou sem resposta, ou "nenhuma".>

## Próximos passos

<O que vem depois deste PR, ou "nenhum".>

## Literatura

<Só na categoria literatura; nas outras, apague esta seção.>
Origem: <Claude Research | Claude Science | ChatGPT | outra>, <data>, <o que foi pedido>.
DOIs: <cada DOI citado; todos têm de estar num docs/referencias/*_verificadas.csv ou *_crossref.json>.
Resultados: <o que a literatura sustenta, com o link para a síntese em docs/referencias/>.
Limitações: <o que não foi conferido: texto completo, fonte cinza, SEM FONTE>.
