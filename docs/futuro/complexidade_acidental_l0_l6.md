# Complexidade acidental: as fases L0 a L6 (para depois da LIMPEZA)

Status: **ESPERA a LIMPEZA** (`docs/TAREFA_V3_LIMPEZA.md`, LZ0 a LZ5). Origem: um prompt colado pelo Matheus em 2026-11-16, escrito para o
snapshot `f8fa9ad2`. Nesta sessão, ele decidiu:
- **"Limpeza antes":** as fases abaixo começam da `main` depois da LZ5, não do `f8fa9ad2`;
- **"Vale a D-LZ-1":** a regra de replay dos saves muda (adaptação 1).

Este arquivo guarda o pedido com as adaptações. A sessão que for executá-lo escreve antes a `docs/TAREFA_V3_<FRENTE>.md` dela.

## As adaptações (valem sobre o texto do pedido)

1. **Os saves.** O pedido exige que os saves v21 a v37 abram e reproduzam a assinatura. Pela D-LZ-1, essas versões fecham com aviso na
   LZ3 (a versão nova sem o `Bandit` e sem o A). A garantia de replay vale **da versão da LZ3 em diante**. O teste da L3 abre os saves de
   exemplo dessas versões, e o "JOGO reproduz a v37" passa a ser "o JOGO reproduz a versão da LZ3".
2. **O cérebro trocável.** O `ehCerebroTrocavel`, o `src/cerebro.ts` com o "a" e o fallback para o A saem na LZ3. A L0 mapeia o que
   sobrar.
3. **O índice de desvios.** O pedido manda rodar o `tools/gerar_indice_desvios.py`. Pelo `CLAUDE.md`, o worker não edita o
   `docs/REGISTRO_DESVIOS.md`: quem faz o merge o gera. Vale o `CLAUDE.md`.
4. **A L5 (poda).** O "fica no LAB e no Python" vale para os mecanismos do modular. O que é do A, do bandit e da v1 já terá saído na
   LZ4, e está na tag `antes-limpeza`.
5. **A pesquisa.** Nenhuma fase roda experimento. A LONGE_GEOMETRIA segue na sessão dela.

## O pedido (resumo fiel; as regras e os checkpoints valem como estão)

**Escopo:** só a complexidade acidental: versões, chaves, constantes duplicadas, núcleo acoplado, CI que não cobre o que promete. Sem
experimento de pesquisa e sem mecanismo novo. As fontes de custo citadas:
1. a eclosão de versões em `web/app/motor/constantes.ts` (`VERSOES_PET` e uns 10 predicados `nasceCom*`, `eh*`);
2. as chaves aninhadas (`produto.ts`, `cerebro.ts`, `ConfigDigibrain`, `ConfigCooperacao`, `ConfigSonoSegura`, `ConfigLanceDono`,
   `ConfigEnjooTela`);
3. a dupla implementação Python ↔ TS do DigiBrain, com os PRs só de paridade;
4. a TV e o grupo espalhados no caminho de decisão (`motor_corpo_mundo.ts`, `motor.ts`);
5. o CI que roda só os testes mudados, com a suíte inteira só manual.

**As regras:**
- não quebrar o replay (com a adaptação 1);
- nenhum mecanismo novo;
- não confundir paridade com correção;
- não tratar "CI verde" como "suíte verde": rodar a suíte inteira e registrar as falhas conhecidas;
- produto é decisão do Matheus;
- nada de reescrever em outra linguagem;
- um critério que falha para a fase, com o relato.

**As fases:**
- **L0, o mapa de comportamento** (documento): `docs/MAPA_COMPORTAMENTO.md`, com:
  - as chaves;
  - os predicados de versão;
  - os pontos onde a TV e o grupo tocam a decisão;
  - três perfis propostos: LAB, JOGO e MIN (pet único, sem TV, grupo, luta, cooperação nem lance).
  - **CHECKPOINT L1:** o Matheus aprova o mapa e os perfis.
- **L1, a fonte única de constantes:** um `tools/gerar_constantes_web.py`, no padrão do `gerar_catalogo_fala_web.py`, que emite um JSON
  que o TS lê, com o `--conferir`; o `tests/test_constantes_web.py`; e a suíte inteira do web.
- **L2, a decisão sobre a dupla implementação** (documento): três opções com o custo de cada uma: (a) paridade bit a bit, (b) o Python
  congelado como referência, (c) contrato de dados.
  - **CHECKPOINT L2:** a decisão do Matheus.
- **L3, os perfis LAB, JOGO e MIN:**
  - o evento de save `["pf", {perfil}]`, e as versões antigas mapeadas para o perfil;
  - o teste dos saves (com a adaptação 1);
  - a suíte inteira e o e2e.
  - **CHECKPOINT L3:** aprovação antes do merge.
- **L4, o `core/` sem DOM:** os módulos do DigiBrain vão para `web/app/motor/core/`, a TV e o grupo viram os plugins `PluginTela` e
  `PluginGrupo` injetados, e um teste de 1 000 decisões sem Three, React, DOM, TV e grupo, com a paridade dos G-PAR mantida.
- **L5, a poda por evidência** (condicionada ao CHECKPOINT L2): o C2, o AN4 e o C3 saem do JOGO; a CO7 no JOGO é decisão do Matheus.
- **L6, um CI que bloqueia:** (a) a suíte inteira com gates bloqueantes, ou (b) gates advisory, com o README e o template declarando o que o
  CI cobre.
  - **CHECKPOINT L4:** a escolha entre (a) e (b).

**A ordem:** L0 → CHECKPOINT L1 → L1 → L2 → CHECKPOINT L2 → L3 → CHECKPOINT L3 → L4 → L5 → L6 → CHECKPOINT L4. Um PR por fase, no
template, sem merge.
