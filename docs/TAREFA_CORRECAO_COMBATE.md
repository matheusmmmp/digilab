# Tarefa — correção do combate V2 e V2.1

Texto como recebido do pesquisador (2026-09-25).

Leia o `CLAUDE.md`, `docs/ESPEC_COMBATE_V2.md`,
`docs/ESPEC_EVOLUCAO_COMBATE.md` e os relatórios em
`artifacts_combate_v2/` e `artifacts_combate_v21/` antes de começar. Todas
as regras do `CLAUDE.md` valem.

## Pré-condição

- `TAREFA_TREINO_SOMBRIO` com merge na `main`. Se não estiver, pare e
  reporte.

## Situação

- **V2 REPROVADO:** G4 (muitas lutas acabam no limite de turnos) e G5
  (quase ninguém usa esquiva).
- **V2.1 REPROVADO em E1–E5:** a Ferrugem domina as outras espécies; a
  resposta declarada ao `marcar` não funciona.

A pesquisa V2.1 e a personalidade rodaram sobre esse combate, e os
resultados saíram inconclusivos. Esta tarefa corrige a base antes de
qualquer run de pesquisa nova.

## Princípio

**Uma mudança por vez, com a bateria rodada depois de cada uma.** O
relatório final precisa dizer qual mudança corrigiu (ou quebrou) qual
gate. Nada de aplicar tudo junto.

Todas as rodadas intermediárias usam as sementes de **calibração**. Só a
run final usa as de **validação**.

## Fora de escopo

- Arena V1 e seus artefatos.
- Ações novas além da `fintar`.
- Runs de pesquisa com pets (ficam para depois desta tarefa).
- `web/digilab_sprites.html` (registrar como pendência o que mudar).

## Preservação

- `artifacts_combate_v2/` e `artifacts_combate_v21/` não são alterados.
- Novo protocolo `COMBATE_V2C` (base corrigida) e `COMBATE_V21C`
  (evolução corrigida). Artefatos em `artifacts_combate_v2c/` e
  `artifacts_combate_v21c/`.
- As versões antigas continuam reproduzíveis.

---

## Etapa 0 — diagnóstico (antes de mudar qualquer regra)

Reportar, a partir dos artefatos existentes e de runs de diagnóstico:

1. **G4:** quais pares de bots terminam por limite de turnos, e com que
   frequência.
2. **G5:** em que situações a esquiva é legal e não é escolhida; qual
   ação é escolhida no lugar.
3. **Ferrugem:** ablação por stat. Para cada stat da Ferrugem, trocar só
   ele pelo valor neutro (10), mantendo o resto, e medir a taxa contra as
   outras espécies com o mesmo arquétipo e estilo. Dizer qual stat (ou
   qual fórmula de conversão) explica a dominância.
4. **`marcar`:** por que a resposta declarada (avançar e pressionar) não
   reduz a taxa do caçador. Rastrear 3 partidas representativas.

Se o diagnóstico contradisser alguma mudança abaixo, pare e reporte antes
de aplicar.

## Etapa 1 — base V2 (uma mudança por vez)

Origem: simulação de protótipo (`docs/sim_combate_v2/`), que reproduziu
os mesmos sintomas de G1, G4 e G5.

| # | mudança | alvo |
|---|---|---|
| C1 | **Finta:** no turno de execução do pesado, o lutador escolhe `executar` ou `fintar`. `fintar` = golpe rápido de 8 que acerta quem esquivou e não quebra guarda. Nova condição de gambit `turno_execucao` para essa escolha. | G5, G1 |
| C2 | **Parry:** `defender` contra golpe rápido devolve 5 de dano ao atacante. | spam de golpe rápido, G1 |
| C3 | **Fuga condicionada:** `recuar` só aumenta a distância se o oponente não avançar no mesmo turno. `avancar` é ilegal em `perto`; `recuar` é ilegal em `longe`. | kiting, G1 |
| C4 | **Morte súbita:** a partir do turno 25, todo dano × 1,5. | G4 |

Depois de C1–C4, se G5 ainda falhar: testar custo da esquiva 20 → 15
(C5). Se G4 ainda falhar: testar remover o bônus de guts do `defender`
(C6). **Atenção:** na simulação, C6 junto com fadiga de guarda devolveu a
dominância ao contragolpe. Aplicar C6 isolado e checar G1 e G8.

## Etapa 2 — gates novos na bateria

Acrescentar aos G1–G7:

- **G6b — espelho:** mesmo estilo, condição física no extremo da faixa
  atual (±5%): a taxa do lado favorecido fica **≤ 0,65**. Na simulação,
  ±10% levava a 0,80 em média, e isso faria a arena medir cuidado.
- **G8 — robustez:** perturbar cada parâmetro numérico do combate em
  ±10%, um de cada vez; G1 precisa continuar valendo em **≥ 80%** das
  perturbações.
- **G9 — decisividade:** rodar a bateria com ε = 0,05 e ε = 0,2; com
  ε = 0,2, no máximo **50%** dos confrontos com taxa < 0,1 ou > 0,9.
- **Oráculo:** trocar a busca de 1 passo por busca de 2 passos. Na
  simulação, o oráculo de 1 passo perdia para o adaptativo e não servia de
  teto.

## Etapa 3 — V2.1

Aplicar só depois de a base V2C estar APROVADA na validação.

- **Ferrugem:** corrigir pela causa apontada na Etapa 0. Ordem de
  preferência: (1) ajustar a **fórmula de conversão** do stat responsável
  (vale para todas as espécies); (2) só se não bastar, redistribuir o
  vetor da espécie, mantendo o orçamento de 60 e a soma zero dos
  modificadores. Registrar em `docs/REGISTRO_DESVIOS.md`.
- **`marcar`:** a marca se perde se o caçador receber dano corpo a corpo
  ou terminar um turno em `perto`. Assim, pressionar de perto passa a ser
  resposta de fato.
- **Guardião:** bloquear em 53% dos turnos é esperado; conferir que não
  causa limite de turnos acima do G4 nos confrontos com guardião.
- Rodar E1–E5 + S1 + os gates novos da Etapa 2.

## Poder da bateria

Com taxa perto de 0,5, meia-largura de IC95 de 0,05 exige ~400 partidas
por par. A run de **validação** usa **N = 400** por par. As rodadas de
calibração podem usar menos, declarado no artefato.

## Testes

- Cada mudança C1–C6 tem teste de regra próprio (tabela de interação).
- `fintar` só é legal no turno de execução.
- Replay bit a bit das versões C e das antigas.
- Artefatos antigos intactos.

## O que reportar

Sem rodeios, nesta ordem:

1. **Base V2C e V21C passaram na validação?** Se não, quais gates e por
   quê. Diga primeiro.
2. Tabela **mudança × gate**: para cada etapa (C1, C2, …, correções da
   V2.1), quais gates passaram a passar ou a falhar.
3. Resultado do diagnóstico da Etapa 0, em especial a causa da Ferrugem.
4. G6b, G8 e G9 com os números.
5. Números ajustados na calibração, de quanto para quanto, também em
   `docs/REGISTRO_DESVIOS.md`.
6. O que precisa mudar na versão web.

Nenhum número sem o artefato que o gerou.
