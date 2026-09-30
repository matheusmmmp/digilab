# Validação da variante `a_c_e2v_v` do reequilíbrio (V21D)

Status: **registro** (2026-09-30), escrito e commitado **antes** de rodar qualquer coisa nas sementes de validação.
A seção "Resultado" entra num commit posterior, depois da run única.

Decisão do Matheus (2026-09-30): fixar o ganho da rodada 2 (`docs/EQUILIBRIO_RODADA2.md`) com o furioso como
**exceção conhecida** (o problema dele é da base do combate; rodada 3, tarefa futura), validar nas sementes de
validação e levar ao jogo nos pets v6.

## 1. A variante (exata)

Regras da validação V21C (`experiments/configs/v21c/validacao.json`) mais estas chaves da `ConfigCombateV21D`
(`experiments/configs/v21d/validacao.json`):

| chave | valor | o que faz |
|---|---|---|
| `preparo_sob_pele_oculto` | **ligada** | A: o preparo do pesado feito sob `pele_dura` não aparece em `oponente_preparando` |
| `muralha_lista_espelho` | **ligada** | C: a muralha luta com a lista do espelho (`bots.GAMBITS_MURALHA_V21D`) |
| `vigia_bate_em_quem_recua` | **ligada** | E2 no vigia: `se(perto, oponente_frequente(recuar)) → golpe_rapido` antes do preparar; sai `oponente_preparando → esquivar` |
| `vigia_recua_do_preparo_sob_pele` | **ligada** | V: `se(oponente_vai_preparar, oponente_frequente(pele_dura)) → recuar` no topo do vigia; sai `guts < 20 → carregar` |
| `investida_erra_contra_recuo` | desligada | D2 |
| `preparo_prende` | desligada | E1 |
| `tita_bate_em_quem_recua` | desligada | E2 no titã |

A base V2C não muda (`dano_parry` 5, sem D1). No Python as chaves continuam **desligadas por padrão**: a V21C, a
pesquisa (V3, E1, confirmatória) e o `engine.py` não mudam.

## 2. Método

`python experiments/validar_v21d.py --conjunto validacao`, uma vez. Os métodos são os da rodada 2
(`experiments/calibrar_equilibrio.py`), com as sementes como parâmetro, e rodam a V21C e a variante nas mesmas sementes:

- **Sementes de validação:** 4101, 4202, 4303, 4404, 4505. Nenhuma delas foi usada na calibração.
- **Matriz:** as 8 formas adultas, os dois lados da mesma espécie, 100 partidas por par por semente e espécie, lados
  trocados na metade, ε dos bots 0,05 e 0,15. Força = média dos pontos contra as outras 7 (média das 4 espécies).
- **Painel B:** pet = bot canônico da forma (ε 0,05, sem treino, condição 1,0) contra os 32 bots do painel (8 formas ×
  4 espécies), 50 partidas por bot por semente, sob as regras e listas da variante.
- **S1:** 12 formas (8 normais + 4 sombrias), 100 partidas por par por semente e espécie.
- **E4 na escala:** adulto sem treino × adolescente da linha sem treino e com +22 (uniforme), como `run_bateria_v21`
  com a escala.
- **Campanha na escala:** o pet do estágio sugerido × cada NPC, sem treino e com o treino típico, 10 partidas por
  semente, fatores de `ConfigEscala.fator_npc` (como `calibrar_escala.py --validar`), regras
  `campanha.REGRAS_CAMPANHA` mais as chaves.
- **E3:** resposta declarada de cada técnica (`RESPOSTAS_V21C`), como a bateria.

Antes da validação, o script foi conferido nas sementes de **calibração**: com `--conjunto calibracao` ele refaz a
rodada 2 byte a byte (matriz, painel e colaterais da `a_c_e2v_v` e da V21C;
`artifacts_combate_v21c/validacao_v21d/conferencia_calibracao.json`). Na validação, a parte V21C é conferida contra os
artefatos de validação já gravados (matriz, E3, E4, campanha); as conferências são registradas e não interrompem a run.

Artefatos: `artifacts_combate_v21c/validacao_v21d/` (`matriz.json`, `painel.json`, `colaterais.json`,
`criterios.json`).

## 3. Critérios (o que conta como passar)

A validação **passa** se todos os itens abaixo passarem, com a variante, nas sementes de validação:

| item | critério |
|---|---|
| **A1** força entre formas | as 7 formas que não são o furioso com força (ε 0,05) em [0,40; 0,60] |
| **A2** força contra o painel B | as 7 formas que não são o furioso com taxa no painel em [0,40; 0,60] |
| **A6** lugar no ciclo | toda forma (as 8) vence (> 0,5) pelo menos 2 das outras 7 (ε 0,05) |
| **S1** | nenhuma sombria vence (> 0,5) as 8 formas normais |
| **E4 na escala** | o adulto sem treino vence o Champion (sem treino e com +22) em ≥ 0,60, nas 8 formas |
| **campanha na escala** | Brutamontes, Carcereiro, Porteiro e Soberano com ≤ 0,30 sem treino e ≥ 0,80 com o treino típico; a Sentinela segue exceção aceita |
| **E3 da pele dura** | a resposta declarada ("ficar longe") reduz a taxa dos usuários da pele dura (redução > 0) |

**Relatados, não reprovam** (exceção declarada):
- o furioso (força, painel, vitórias);
- A3 (suporte do equilíbrio ≥ 6), A4 (no máximo 7 pares fora de [0,1; 0,9] com ε 0,05 e 4 com ε 0,15), A5 (amplitude
  ≤ 0,20 com ε 0,05 e 0,15);
- A1 e A2 com as 8 formas;
- o E3 das outras técnicas (o do contra-golpe já falhava na calibração com A + C);
- a Sentinela na campanha.

**Depois da run não se mexe em número nenhum por causa do resultado.** Se reprovar, a reprovação é relatada, e a
decisão (aceitar outra exceção, rodada 3, voltar) é do Matheus.

Não medidos nesta validação: E2 (espécies), E5, G6b, G8, G9 e as runs de pesquisa com pets reais (a pesquisa não lê as
chaves).

## 4. Resultado

(preenchido depois da run)
