# TAREFA V2 — DESCRITIVO-PLATO: o aprendiz apaga a preferência ou aprende qual fruta faz mal? (2026-10-07)

Coordenador: chat "Principais jogos Digimon com diálogo". Worker: chat D. Worktree e branch: `v2-descritivo-plato`. Status: ABERTA.

**Origem:** decisão V-3 de `docs/LEITURA_V2_VALIDACAO_UNICA.md` (pergunta Q-1), aprovada pelo Matheus em 2026-10-07. A escolha do cérebro
da web (M6) espera este descritivo.

## 1. Pergunta

Todo braço que aprende termina perto de 1/3 de fruta ruim em todo mundo e em toda duração. Isso é compatível com duas explicações:
- **(a) apagar:** o aprendiz apaga a preferência inata e passa a comer as três frutas por igual;
- **(b) aprender:** o aprendiz aprende qual fruta faz mal, mas fica limitado pela exposição ou pelo teto.

O mesmo vale para o C? E no P3, onde o C generaliza a bronca?

## 2. O que fazer: pós hoc descritivo, rotulado como tal

**Nenhuma run nova, nenhuma semente nova.** As vidas são **regeneradas** das configs e do código, por replay determinístico, e conferidas
contra as medidas gravadas:
- as da validação única: `artifacts_v2_validacao_unica/`, bases 30101…30505;
- as da validação da comparação A × C: bases 29101…29505.

**As medidas,** por cérebro (A; C onde houver), braço (P0, P1, P2, P3) e condição, nas janelas inicial e final:
1. **Consumo por fruta:** a fração de consumo da fruta boa, da neutra e da ruim. Comer por igual dá cerca de 1/3 em cada uma.
2. **Escolha com várias frutas:** nas ofertas com duas frutas ou mais, a fração de vezes em que a fruta ruim é escolhida, contra o
   esperado ao acaso.
3. **Comer com uma fruta só:** nas ofertas com uma fruta só, a probabilidade de comer quando ela é a boa, a neutra e a ruim. Se a da ruim
   cai mais que a das outras, há aprendizado do efeito.
4. **Pesos no fim da vida:**
   - no A, o peso de cada fruta na escolha e o termo de presença na decisão de comer;
   - no C, os compartimentos apetitivo e aversivo das células da fruta e do objeto;
   - em cada um, comparar a fruta ruim com as outras.

**Saída:** `artifacts_v2_descritivo_plato/` e `docs/DESCRITIVO_V2_PLATO.md`.
- Tabelas com IC por bootstrap das unidades.
- No fim, uma leitura curta: o padrão é de (a), de (b) ou misto, por cérebro e braço.
- **Sem gate e sem mudar nenhuma leitura registrada.** É um descritivo pós hoc, rotulado como tal. Se pedir desenho novo, vira plano
  próprio.

## 3. Regras

- Só `experiments/` (um script novo) e, se precisar, `digilab/metrics.py`.
- `lobos.py`, `cerebro_c.py`, `frutas.py` e a bancada não mudam.
- As vidas regeneradas conferem com as medidas gravadas; se divergirem, o script falha alto.
- Nenhuma alegação de novidade.

## 4. Entrega

Um PR com o relato no corpo e a suíte inteira, mais uma seção no fim do `CLAUDE.md` e outra no fim do `REGISTRO_DESVIOS.md`. Merge só pelo
Matheus.
