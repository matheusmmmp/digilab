# Tarefa — personalidade, obediência e desejo

Leia o `CLAUDE.md`, `docs/ESPEC_COMBATE_V2.md` e
`docs/TAREFA_MEMORIA_EXPRESSAO.md` antes de começar. Todas as regras do
`CLAUDE.md` valem: `engine.py` não muda, determinismo bit a bit, só stdlib
em `digilab/`, parâmetros em `config.py`, falhar alto.

## Pré-condições (conferir em disco antes de qualquer código)

- Bateria do combate V2 APROVADA (`artifacts_combate_v2/gates.json`).
- Ablação instinto × bandit registrada.
- `TAREFA_MEMORIA_EXPRESSAO` concluída, Partes A e B
  (`artifacts_v1_memoria/` existe). Esta tarefa usa `Motivo`, a camada de
  expressão e as features de memória.

Se alguma faltar, não comece: reporte o que falta.

## Objetivo

1. **Temperamento inato** que muda *como* o pet aprende, não *o que* ele
   aprende.
2. **Vínculo e obediência:** o pet pode recusar ações do dono, com motivo.
3. **Registro de desejo:** o que o pet quer agora, calculado (nunca
   inventado), exposto pela camada de expressão, com métrica de
   cumprimento.

## Decisões do pesquisador que esta tarefa autoriza

- A **ação de recusa** do pet, que a `TAREFA_MEMORIA_EXPRESSAO` (B2) deixou
  pendente.

A regra de não aumentar escopo continua valendo para todo o resto.

## Fora de escopo

- Obediência ou táticas do dono no combate (modo produto).
- Temperamento afetando o combate V2 (fica para a arena V2).
- Desejo pós-batalha ("quero treinar esquiva") — depende de pets no
  combate V2.
- LLM. Só templates.
- Temperamento que muda ao longo da vida.
- `web/digilab.html`.

## Três barreiras de pesquisa — não negociáveis

1. **Ovos pareados.** O temperamento vem de uma semente de ovo, e o mesmo
   ovo é usado em todos os braços. A comparação passa a ser "mesmo pet,
   donos diferentes".
2. **Vínculo fora do combate.** Vínculo e obediência nunca entram em
   `CondicaoFisica`, em `Estilo` nem em nada de `digilab/combate_v2/`.
   O vínculo mede coerência do dono, que é a própria hipótese; se afetar a
   arena, o confundidor volta.
3. **Recusa não corta aprendizado.** Quando o pet recusa, o feedback do dono
   continua chegando à política normalmente.

---

## 1. Temperamento

### 1.1 Modelo

`Temperamento` (frozen), em `digilab/temperamento.py`. Quatro eixos em
[−1, 1]; **0 é neutro** e reproduz o comportamento atual exatamente.

| eixo | efeito (só no *como*) |
|---|---|
| `curiosidade` | escala a exploração do bandit (variância da posterior usada na amostragem) |
| `teimosia` | reduz o peso das repreensões no aprendizado; reduz obediência |
| `sensibilidade` | assimetria: > 0 responde mais a elogio, < 0 mais a repreensão |
| `rancor` | escala o decaimento das features de memória ligadas a demora e repreensão |

Funções de efeito com parâmetros em `ConfigTemperamento`, todos PROPOSTO.
Nenhum eixo pode alterar o prior do instinto, o espaço de ações ou a
recompensa em si, só a escala com que ela é usada.

### 1.2 Sorteio

- Stream de rng própria, `rng_ovo`, derivada da semente do ovo. Não
  compartilha estado com rng de ambiente, de política ou de combate.
- Distribuição PROPOSTA: uniforme em [−1, 1] por eixo, independente.
- Config `temperamento_neutro: true` fixa todos os eixos em 0 (usado nas
  ablações e no teste de equivalência).

### 1.3 Visível ao jogador

O temperamento entra na camada de expressão como tom, com tabela
declarativa por eixo e estágio (cobertura obrigatória, como na tarefa de
memória). O bebê já mostra temperamento por emote; o caráter aprendido
(traços) só fica nítido com o tempo. O contraste "nasceu X, virou Y" é
lido dos dois registros, nunca inventado.

## 2. Vínculo e obediência

### 2.1 Vínculo

`digilab/vinculo.py`: função pura dos eventos do log, valor em [0, 1],
atualização por média móvel. Componentes (pesos em `ConfigVinculo`,
PROPOSTO):

- **atendimento:** latência do dono em pedidos do pet (reusar features de
  memória);
- **coerência:** por ação do pet, consistência do sinal do feedback do dono
  em janela recente (elogiar e repreender o mesmo comportamento derruba);
- **desejos respeitados:** fração de desejos do tipo `vontade` atendidos
  pelo dono (seção 3).

Cada atualização registra quais eventos a moveram (`evento_ref`), para a
expressão poder explicar.

### 2.2 Recusa

Implementar via subclasse do motor com feedback (o `MotorComFeedback` já
sobrescreve `_aplicar_acao_usuario`), **sem alterar `engine.py`**. Se for
impossível, pare e reporte o ponto exato.

Probabilidade de obedecer uma ação do dono:

`p = logistica(b0 + b_vinculo * vinculo - b_teimosia * teimosia - b_conflito * conflito)`

- `conflito`: quanto a ação do dono contraria a necessidade mais urgente
  (ex.: brincar com fome alta). Definição em config.
- Stream de rng própria, `rng_obediencia`, separada de todas as outras.
- Config `obediencia_desligada: true` faz `p = 1` sempre.

Tipos de desobediência na v1 (PROPOSTO): `recusar` (a ação do dono não
tem efeito) e `fazer_outra` (o pet executa a ação da própria política).

### 2.3 Regras de contabilidade

- Ação recusada **consome orçamento** de interação do dono igual a uma
  aceita. Sem isso, braços com mais recusas ganham interações extras.
- O `CanalDeInteracao` continua impondo orçamento exato; se a recusa
  exigir mudar o canal, mudar só a contagem, nunca o limite.
- Feedback do dono após uma recusa é observado pela política normalmente.

### 2.4 Motivo da desobediência

Toda recusa gera `Motivo` (origem `vida`) com fatores do conjunto:
`vinculo_baixo`, `teimosia`, `necessidade_<x>`, e features de memória
quando pesarem (com `evento_ref`). Mesma regra de honestidade: só cita o
que de fato entrou no cálculo de `p`. Fator = termo de maior contribuição
negativa na logística, se acima de `LIMIAR_MOTIVO`.

## 3. Desejo

### 3.1 Registro

`Desejo` (frozen), em `digilab/desejo.py`:

- `tick`, `tipo` ∈ {`necessidade`, `vontade`}, `alvo` (ação),
  `intensidade` em [0, 1], `origem_ref`

Cálculo, **sem consumir rng**:

- **necessidade:** vem do estado de vida — necessidades acima de
  `LIMIAR_NECESSIDADE`. É o lado *condição* (cuidado).
- **vontade:** vem da política — ação com maior recompensa esperada pela
  **média** da posterior do bandit (não pela amostra), emitida só se a
  margem para a segunda ação passar `LIMIAR_VONTADE`. É o lado *estilo*
  (aprendizado).

Emitir quando o desejo muda, não a cada tick.

### 3.2 Expressão

Entra na camada de expressão com as mesmas regras por estágio e a mesma
tabela declarativa (cobertura obrigatória). O jogador precisa conseguir
distinguir necessidade de vontade a partir do estágio criança.

### 3.3 Métrica de cumprimento

`cumprimento`: dado um desejo `vontade` com alvo X emitido em t, fração dos
casos em que o pet escolhe X nos próximos `K_CUMPRIMENTO` ticks, entre as
oportunidades em que X era possível. Vai para `metrics.py` (uma vez só).
Se for baixa, a fala está prometendo o que o pet não faz.

---

## 4. Protocolo e runs

- Novo protocolo `PROTOCOLO_ARENA_V1_PERSONALIDADE`, campos novos PROPOSTO.
  `ARENA_V2` segue reservado.
- Artefatos em `artifacts_v1_personalidade/`. Não sobrescrever nenhum
  diretório de artefatos anterior.
- Ovos pareados entre braços (barreira 1); número de ovos no JSON.
- Três runs com o mesmo conjunto de ovos:
  1. completa (temperamento sorteado + obediência ligada)
  2. `temperamento_neutro: true`
  3. `obediencia_desligada: true`

## 5. Testes

- **Equivalência:** `temperamento_neutro` + `obediencia_desligada`
  reproduz `artifacts_v1_memoria/` idêntico. Desejo é somente leitura e não
  pode mudar nada.
- `rng_ovo` e `rng_obediencia` não alteram o estado das outras streams.
- Mesmo ovo gera o mesmo temperamento em todos os braços.
- Recusa consome orçamento; total de interações idêntico entre braços.
- Feedback após recusa chega à política.
- Vínculo é função pura do log; replay reproduz a série inteira.
- Nada em `digilab/combate_v2/` nem em `CondicaoFisica`/`Estilo` importa
  ou lê `vinculo`, `temperamento` ou obediência (teste por AST).
- Cálculo de desejo não consome rng.
- Honestidade: motivos de recusa e desejos só citam fatores que de fato
  entraram no cálculo.
- Cobertura das tabelas de texto (temperamento, recusa, desejo).

## 6. Critério de pronto

- [x] três runs gravadas com gate rodado
- [x] todos os testes, antigos e novos, passando
- [x] `CLAUDE.md` atualizado (mapa, comandos, estado, pendências)

## 7. O que reportar

Sem rodeios, nesta ordem:

1. **O temperamento engole o efeito do dono?** Decomposição da variância
   do resultado principal entre ovo e braço (run completa). Se o ovo
   explicar mais que o braço, diga primeiro: a hipótese central fica
   mais difícil de detectar.
2. Efeito do dono com e sem temperamento (run 1 vs run 2).
3. **Vínculo e taxa de obediência por braço** (hipótese secundária:
   treino coerente → pet mais obediente). Atencioso vs aleatório com IC.
4. Efeito da obediência no resultado principal (run 1 vs run 3).
5. **Cumprimento de desejo** por braço, e fração de ticks com desejo
   `vontade` emitido (legibilidade do aprendizado).
6. Onde parou por exigir mudança em `engine.py`, no `Protocol`, no
   `CanalDeInteracao` além da contagem, ou em `combate_v2/`.

Nenhum número no relatório sem o artefato que o gerou.
