# Plano — rodada de equilíbrio geral do combate

Status: **registrado antes da rodada** (pedido do Matheus, 2026-09-30: "segue com a rodada de equilíbrio geral"). Todo número é PROPOSTO, sem fonte, e só estas metas contam como "equilibrado".

**Por que agora.** As mecânicas do combate estão no `main` (V21D, escala v6, limite do desafiado, arenas, itens, Fronteira, confiança). A regra do Matheus foi não equilibrar a cada passo e fazer uma rodada só no fim (memória "equilíbrio só no fim").

## 1. Escopo e versão

- **Só o jogo web, para os ovos novos: pets v9** (`VERSAO_PET = 9` = v8 + combate equilibrado). Os pets v1–v8 não mudam de comportamento nem de assinatura. Nenhum save é descartado.
- **A pesquisa em Python** ganha as mudanças da base atrás de uma chave desligada por padrão (como a V21D). Com a chave desligada, tudo reproduz (V3, E1, confirmatória, V21C, V21D, voz, M1).
- **Paridade:** toda regra nova de combate existe no Python e na web, com gabarito de partidas Python → web.

## 2. As metas

| # | o quê | meta | como medir |
|---|---|---|---|
| **M-A1** | força de cada forma contra as outras 7 | todas as 8 entre 0,40 e 0,60, **incluindo o furioso** | matriz 8×8 dos bots canônicos com as regras dos pets v9, ε 0,05 |
| **M-A2** | força contra o painel B | todas as 8 entre 0,40 e 0,60 | painel B, bot da forma como pet |
| **M-A3** | distância entre a mais forte e a mais fraca | ≤ 0,20 | a partir de M-A1 |
| **M-A4** | lugar no ciclo | toda forma vence ≥ 2 das outras 7 | a partir de M-A1 |
| **M-A5** | a base continua de pé | gates G1–G9 da V2C e E1/E3/E5 da V21C passam (as exceções já aceitas continuam aceitas: E2, G6b, G8) | baterias de sempre com a chave ligada |
| **M-B1** | estágio | vizinhos ≤ 0,10; dois estágios = 0,00 | `calibrar_escala_v6.mjs` |
| **M-B2** | líderes das 6 arenas | sem treino ≤ 0,05; com treino típico ≥ 0,80; pior forma ≥ 0,50 | `calibrar_arenas.mjs` |
| **M-B3** | desafiantes da campanha | sem treino ≤ 0,30; com treino típico ≥ 0,80; pior forma ≥ 0,50 (a exceção do Tortomon só se continuar impossível) | `calibrar_desafiantes_v6.mjs` |
| **M-C1** | Liga dos Líderes | com o treino típico do Mega (40), **toda forma** tem chance de título ≥ 0,25, e nenhuma passa de 0,85 | `conferir_liga.mjs` |
| **M-C2** | Fábrica | escolhendo o melhor alugado, vencer ao menos uma série em ≥ 0,25 das tentativas | `conferir_fabrica_salao.mjs` |
| **M-C3** | Salão | cada nível, com o treino típico, entre 0,70 e 0,95 | idem |
| **M-D1** | itens não substituem o treino | com os melhores itens e carta permitida, pet sem treino × cada líder ≤ 0,05 | `medir_itens.mjs` |
| **M-D2** | itens não quebram o estágio | com os melhores itens, M-B1 continua | idem |
| **M-D3** | itens não desequilibram as formas | com o melhor item de cada forma, a força contra as outras 7 fica ≤ 0,60 | idem |
| **M-E1** | Palácio e Torre de Batalha | a melhor forma vence a 1ª luta ≥ 0,70 e a pior ≥ 0,40 | `conferir_instalacoes` (4b) |

## 3. Alavancas permitidas

- **Base do combate** (o furioso): o custo do golpe rápido, o dano do parry, a regra C3 (quem recua de quem avança), atrás de chave. É a alavanca do diagnóstico.
- **Listas de regras das formas** (variantes V21D/V21E), passivas e a técnica da pele dura.
- **Escala v6:** vida por estágio e peso do treino.
- **Fatores** de líderes, desafiantes, Liga e rivais das instalações.
- **Estrutura das instalações:** cura parcial entre lutas da Liga, a troca da Fábrica entrar com vida cheia, a cura entre séries.
- **Itens:** o valor de cada chip e carta, e restrições de uso.
- **Não pode:** mudar as regras das mecânicas já decididas pelo Matheus (a trava 1/3/5, o limite do desafiado, "Champion nunca vence Mega"), nem a pesquisa em Python com a chave desligada.

## 4. Ordem e sementes

1. **Fase 1, as formas** (M-A1…M-A5): base e listas, no Python e na web, com gabarito de paridade.
2. **Fase 2, a progressão** (M-B1…M-B3): escala, líderes e desafiantes, em cima da fase 1.
3. **Fase 3, o fim de jogo e os itens** (M-C1…M-C3, M-D1…M-D3, M-E1).
4. **Fase 4, validação única** de todas as metas nas sementes de validação (4101…4505), depois de congelar tudo. Nenhum número muda por causa do resultado. O que reprovar é relatado; se o Matheus aceitar como exceção, fica registrado.

Todas as fases 1–3 usam **só as sementes de calibração** (3101…3505). Cada fase grava os artefatos em `artifacts_equilibrio_geral/<fase>/` e um relatório curto em `docs/EQUILIBRIO_GERAL.md`.

## 5. Entrega

Um PR só no fim da fase 4, no branch `equilibrio-geral`, com a tabela de todas as metas (calibração e validação).
