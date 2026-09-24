# Especificação — combate V2 e bateria de bots

Leia o `CLAUDE.md` inteiro antes de começar. Todas as regras de lá valem,
com uma exceção autorizada pelo pesquisador: **esta tarefa cria um sistema
de combate novo.** A regra de não aumentar escopo continua valendo para
todo o resto.

## Objetivo

Substituir o ciclo de 5 ações (pedra-papel-tesoura) por um combate com
profundidade real, e **provar essa profundidade com bots escritos à mão
antes de plugar qualquer pet.** Se o combate não passar na bateria de bots,
ele não vai medir nada com pets também.

Base de desenho:

- **Monster Rancher:** HP, recurso que regenera (guts), distância.
- **Final Fantasy XII (gambits):** a política de combate é uma lista
  priorizada de regras "condição → ação", legível e inspecionável.
- **Into the Breach:** resolução 100% determinística; ataques fortes são
  telegrafados um turno antes.

## Fora de escopo nesta tarefa

- Plugar pets, traços ou bandit no combate (fica para a arena V2).
- Técnicas por linha evolutiva, tabela de tipos/afinidades.
- Comandos do dono durante a luta.
- Alterar `arena.py`, `engine.py`, `protocol.py` V1 ou `web/digilab.html`.

A run canônica V1 precisa continuar reproduzindo `artifacts/` idêntico.

---

## 1. Separação condição × estilo

Um lutador tem duas entradas independentes. Isso existe para atacar o
confundidor atual (vitória vinda do cuidado e não do treino):

- `CondicaoFisica` (frozen): `hp_max`, `guts_inicial`, `regen_guts`.
  No futuro virá do **cuidado** (estado de vida).
- `Estilo` (frozen): `ListaGambits` + `epsilon` (exploração).
  No futuro virá do **comportamento aprendido**.

`Lutador = (CondicaoFisica, Estilo)`. Nenhum campo de um pode depender do
outro. Na bateria de bots, todos usam a condição neutra de `ConfigCombateV2`.

## 2. Regras

Todos os números abaixo são **ponto de partida PROPOSTO** e ficam em
`ConfigCombateV2`. Só podem ser ajustados pelo procedimento de calibração
da seção 6.

### Estado

Público e completo (os dois lados veem tudo; a única informação oculta é a
escolha do turno, revelada simultaneamente):

- `distancia` ∈ {`perto`, `medio`, `longe`}; começa em `medio`
- por lutador: `hp`, `guts` (0–100), `preparando` (bool), histórico de ações

Inicial: HP 100, guts 50. Regeneração: +8 guts por turno.

### Ações

| ação | custo guts | alcance | efeito |
|---|---|---|---|
| `avancar` | 0 | — | distância −1 |
| `recuar` | 0 | — | distância +1 |
| `golpe_rapido` | 10 | perto | 8 de dano; **interrompe** quem está usando `preparar_pesado` neste turno |
| `preparar_pesado` | 15 | perto | fica `preparando`; no turno seguinte executa o pesado automaticamente (25 de dano), com armadura (não é interrompido). Telegrafado: o oponente vê no próximo turno |
| `disparo` | 15 | medio, longe | 6 de dano |
| `defender` | 0 | — | dano recebido ×0,3 (pesado ×0,6: quebra guarda); +5 guts extra |
| `esquivar` | 20 | — | anula pesado e disparo; **falha** contra golpe rápido |
| `carregar` | 0 | — | +25 guts; dano recebido ×1,5 neste turno |

No turno de execução do pesado o lutador não escolhe ação.

### Ordem de resolução de um turno

1. Revelação simultânea das escolhas.
2. Custos de guts. Ação ilegal (sem guts ou fora de alcance) **levanta
   erro**: a camada de decisão nunca pode emitir ação ilegal.
3. Ataques, usando a distância do **início** do turno. O pesado executa se
   a distância no início do turno de execução for `perto`; senão erra.
4. Dano simultâneo.
5. Movimento (distância limitada a `perto`..`longe`).
6. Regeneração de guts.

Consequência intencional: para fugir de um pesado é preciso recuar no
turno da preparação (um palpite), ou esquivar no turno da execução
(que custa guts).

### Fim de partida

- KO: HP ≤ 0. KO duplo = empate.
- Limite de `T_MAX = 40` turnos: vence a maior fração de HP; igualdade
  exata = empate.
- Resultado: 1 / 0,5 / 0.

**A resolução não consome rng.** Não há dano variável nem chance de
acerto. Toda aleatoriedade da partida vem das decisões (ε).

## 3. Linguagem de gambits

`ListaGambits`: até `MAX_REGRAS = 8` regras ordenadas + uma regra final
obrigatória `sempre → defender` ou `sempre → carregar` (sempre legais).
Lista sem regra final válida levanta erro na construção.

Cada regra: até 2 condições (conjunção) + uma ação.

Catálogo fechado de condições, com parâmetros em conjuntos discretos (para
o futuro aprendizado ter espaço finito):

- `sempre`
- `distancia_eh(d)`
- `hp_proprio_abaixo(f)`, f ∈ {0,25; 0,5; 0,75}
- `guts_proprio_abaixo(g)` / `guts_proprio_acima(g)`, g ∈ {20, 40, 60}
- `oponente_preparando`
- `oponente_hp_abaixo(f)` / `oponente_guts_abaixo(g)`
- `oponente_repete(acao, k)`, k ∈ {2, 3}: as últimas k ações do oponente
  foram `acao`
- `oponente_frequente(acao)`: fração de `acao` nas últimas 5 ações do
  oponente ≥ 0,4

Decisão:

1. Com probabilidade `epsilon`, ação legal uniforme (rng de combate).
2. Senão, a primeira regra cujas condições valem **e** cuja ação é legal.

Cada decisão registra o **motivo**: índice da regra disparada ou
`exploracao`. É o gancho para a camada de expressão, depois.

`oponente_repete`/`oponente_frequente` são a adaptação dentro da partida.
Memória só da partida corrente; zera a cada partida.

## 4. Determinismo

- rng de combate própria, derivada da semente da partida. Não compartilha
  estado com rng de ambiente nem de política de vida.
- Log de partida (escolhas reveladas + motivos). Replay do log reproduz a
  partida bit a bit.
- Evento desconhecido no log levanta erro.
- Trocar os lados produz resultado espelhado (teste).

## 5. Bots

Em `digilab/combate_v2/bots.py`. **Todos os bots fixos devem ser escritos
como `ListaGambits`**: isso prova que a linguagem é expressiva. Se algum
comportamento abaixo não couber na linguagem, não amplie o catálogo por
conta própria: reporte o que faltou.

Bots fixos:

- `aleatorio`: ε = 1.
- `agressivo`: avança e ataca, prefere pesado quando tem guts.
- `tartaruga`: defende e carrega; ataca só quando o oponente está sem guts.
- `atirador`: mantém `medio`/`longe` e usa disparo; recua quando o
  oponente avança.
- `contragolpe`: esquiva quando `oponente_preparando`, pune com golpe
  rápido/pesado logo depois.

Bot adaptativo (também em gambits):

- `adaptativo`: usa `oponente_frequente`/`oponente_repete` para responder ao
  padrão do oponente (ex.: oponente repete defender → preparar pesado).

Bot de referência (**fora** da linguagem, marcado como tal):

- `oraculo`: melhor resposta de 1 passo contra a distribuição empírica das
  ações do oponente na partida. Serve de teto, nunca de alvo para pet.

ε padrão dos bots fixos: 0,05 (PROPOSTO), exceto `aleatorio`.

## 6. Bateria — o portão do combate V2

`experiments/run_bateria_combate.py --config experiments/configs/bateria_canonico.json`
→ `artifacts_combate_v2/`: `matriz.json`, `equilibrio.json`,
`gates.json`, `partidas.csv`, com hash das regras e da config.
Código de saída 0 APROVADA / 2 REPROVADA, com motivo por gate.

Round-robin completo, incluindo espelhos (bot contra si mesmo), N partidas
por par por semente (PROPOSTO: 200), lados trocados na metade.

### Calibração sem overfitting

- Sementes de **calibração** e de **validação** disjuntas, fixadas no JSON.
- Ajuste de números só olhando as sementes de calibração.
- Depois de congelar os números, a run canônica usa **só** as de
  validação. O gate vale na validação.

### Gates (limiares PROPOSTOS)

- **G1 — sem estratégia dominante.** Nenhum bot fixo tem taxa > 0,5 contra
  todos os outros bots fixos. Equilíbrio da matriz simétrica dos bots fixos
  (fictitious play determinístico, stdlib) com suporte ≥ 3 bots.
- **G2 — existe habilidade.** `adaptativo` vence `aleatorio` com taxa
  ≥ 0,70 e IC95 (bootstrap sobre sementes) acima de 0,5. `oraculo` ≥
  `adaptativo` contra o conjunto de fixos.
- **G3 — sanidade.** Espelhos em 0,5 ± 0,03. Replay de amostra das
  partidas bate bit a bit.
- **G4 — ritmo.** Mediana de turnos entre 8 e 30; menos de 20% das
  partidas decididas por limite de turnos.
- **G5 — sem ação morta.** Toda ação aparece em ≥ 3% das decisões dos bots
  no suporte do equilíbrio.
- **G6 — condição não domina estilo.** Com o mesmo estilo, variar a
  condição pela faixa PROPOSTA (HP ±10%, guts inicial ±10) move a taxa de
  vitória **menos** que a diferença entre o melhor e o pior estilo com
  condição igual. Reportar os dois números.
- **G7 — a ordem dos gambits importa.** `adaptativo` com a ordem das regras
  embaralhada (várias permutações, semente fixa) perde para o original com
  taxa ≥ 0,6. É o que garante que o objeto a ser aprendido depois tem
  efeito.

## 7. Arquivos

- `digilab/combate_v2/regras.py` — estado, ações, resolução pura
- `digilab/combate_v2/gambits.py` — catálogo de condições, `ListaGambits`,
  decisão com motivo
- `digilab/combate_v2/lutador.py` — `CondicaoFisica`, `Estilo`, `Lutador`
- `digilab/combate_v2/partida.py` — laço, log, replay
- `digilab/combate_v2/bots.py`
- `digilab/config.py` — `ConfigCombateV2`
- `digilab/metrics.py` — equilíbrio e métricas novas entram aqui, uma vez só
- `experiments/run_bateria_combate.py`, `experiments/configs/bateria_canonico.json`
- `tests/test_combate_v2.py`

Tudo stdlib. Preflight verifica isso por AST, como hoje.

## 8. Testes mínimos

- Resolução é função pura e não consome rng.
- Cada linha da tabela de ações e a ordem de resolução (interrupção do
  pesado, armadura, esquiva falhando contra rápido, quebra de guarda,
  fuga no turno de preparação).
- Ação ilegal levanta erro.
- Primeira regra válida dispara; regra com ação ilegal é pulada; lista sem
  regra final levanta erro.
- Replay bit a bit; troca de lados espelha o resultado.
- V1 intacta: run canônica V1 reproduz `artifacts/` idêntico.

## 9. Critério de pronto

- [ ] testes novos e os 56 antigos passando
- [ ] bateria canônica rodada nas sementes de validação, artefatos gravados
- [ ] `gates.json` com todos os gates e motivos
- [ ] `CLAUDE.md` atualizado: mapa do repositório, comandos, estado do
      combate V2 e pendências

## 10. O que reportar

Sem rodeios, nesta ordem:

1. A bateria **passou ou não**, e quais gates falharam. Se G1 ou G2
   falhar, diga primeiro: é resultado sobre o desenho do combate.
2. Matriz de vitórias e equilíbrio (quais bots ficam no suporte).
3. G6: quanto a condição move o resultado vs quanto o estilo move.
4. Quais números foram ajustados na calibração, de quanto para quanto.
5. Comportamentos de bot que não couberam na linguagem de gambits.

Nenhum número no relatório sem o artefato que o gerou.
