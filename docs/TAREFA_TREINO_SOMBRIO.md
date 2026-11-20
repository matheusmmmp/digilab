# Tarefa — treino, sobrecarga, formas sombrias e dono exigente

Leia o `CLAUDE.md`, `docs/ESPEC_EVOLUCAO_COMBATE.md` e os dados em
`docs/`: `catalogo_pets.json`, `arvore_evolucao.json`,
`cronograma_interacoes.json`, `pve_treino.json`. Todas as regras do
`CLAUDE.md` valem.

## Pré-condições (conferir em disco)

- Combate V2.1 (evolução, técnicas, passivas) com bateria APROVADA.
- `TAREFA_PERSONALIDADE_OBEDIENCIA` concluída (vínculo, obediência, desejo).

Se faltar alguma, pare e reporte.

## Objetivo

1. Treino por botão com fadiga, retorno decrescente e tetos.
2. **Forçar** acima do limite de fadiga, com ganho maior e custo em
   sobrecarga, estresse e vínculo.
3. **Sobrecarga** persistente que leva às **formas sombrias**.
4. Novo braço de dono simulado: **exigente**.
5. Campanha contra os três NPCs, separada da arena.

## Fora de escopo

- Minigames. É um botão.
- Itens de "respec", comida com bônus de treino, recompensa de stats por
  vencer NPC (ficam para depois).
- `web/digilab.html`.

## Barreiras de pesquisa — não negociáveis

1. **Normalização na arena.** Na arena e na pesquisa, o total de stats
   volta ao orçamento da espécie mantendo as proporções treinadas. O ganho
   absoluto só vale na campanha contra NPCs.
2. **Nada disso entra em `CondicaoFisica` pela porta do cuidado.** Treino
   e sobrecarga são estado próprio do pet, com módulo próprio.
3. **Orçamento idêntico.** Treino e "forçar" consomem interações do mesmo
   `CanalDeInteracao`; o total por braço continua igual.
4. **Sem rng no treino.** Ganho, fadiga e sobrecarga são contas
   determinísticas. A única aleatoriedade é a obediência, na stream
   `rng_obediencia` que já existe.

---

## 1. Treino

Dados em `pve_treino.json`. Módulo `digilab/treino_stats.py`, função pura
dos eventos do log.

- Seis exercícios; cada um sobe um stat principal (+2) e um secundário
  (+1), multiplicados pela aptidão da espécie e pelo retorno decrescente.
- Tetos: +10 por stat; +10 / +12 / +14 por estágio; +36 na vida.
- Fadiga +20 por sessão; ganho × (1 − fadiga/100); recupera acordado e
  zera ao dormir.
- Intervalo mínimo de 10 minutos entre sessões; toque antes disso é
  rejeitado (não consome orçamento).
- Falha por obediência: com a obediência sorteada contra, o pet "enrola",
  a sessão não rende e consome orçamento.
- **Pedido de pausa:** com fadiga ≥ 40 o pet emite um `Desejo` de
  descanso (tipo necessidade). Atender sobe vínculo; treinar por cima
  derruba.

## 2. Forçar e sobrecarga

- Com fadiga ≥ 60 a ação de treino vira `forcar_treino`: ganho × 1,5;
  sobrecarga +15, estresse +10, vínculo −0,05.
- Sobrecarga em [0, 100], **não zera na evolução**; decai 2 por hora
  acordado com necessidades atendidas e 10 por sono completo.
- Motivo registrado para cada forçada e para cada pedido de pausa
  ignorado, para a camada de expressão.

## 3. Formas sombrias

Dados em `arvore_evolucao.json` > `ramos_sombrios`.

- Criança → adolescente com sobrecarga ≥ 30: só marca visual e fala mais
  fria. Nada muda em forma ou stats.
- Adolescente → adulto com sobrecarga ≥ 60: a forma adulta vira a sombria
  da linha (devastador, bastião rachado, predador, colosso partido).
- Efeitos permanentes: ε mínimo 0,2 em combate, teto de vínculo 0,6, fala
  fria. Stats continuam somando zero.
- Passivas sombrias entram em `digilab/combate_v2/` como as demais:
  dados declarativos + resolução pura.

## 4. Dono exigente

Dados em `cronograma_interacoes.json` > `donos_simulados.exigente`:
mesmas janelas e latência do atencioso, feedback coerente, mesmo volume;
usa o teto diário de treino, força em 50% das sessões possíveis acima do
limite e ignora pedidos de pausa. O treino extra sai das interações de
carinho.

A comparação que interessa é **atencioso × exigente**: os dois são
coerentes e têm o mesmo volume, então a diferença isola o efeito de
forçar.

## 5. Campanha contra NPCs

- Três NPCs de `pve_treino.json`, com stats totais 72, 80 e 90 e estilos
  fixos em gambits.
- Usa stats **sem normalização**. Resultado separado da arena, em
  `artifacts_campanha/`.
- Corrigir antes o gambit do tier 3 (Soberano): na simulação, o estilo
  atirador vencia sem treino (0,67). O chefe precisa responder a luta de
  longe.

## 6. Gates

Bateria V2.1 com as quatro formas sombrias incluídas:

- **S1 — sombria não domina:** nenhuma forma sombria vence todos os
  arquétipos normais; atenção especial ao devastador contra estilos
  passivos.
- **S2 — atalho com custo:** na campanha, forma sombria vence o tier 1
  mais cedo que a normal da mesma linha, mas não vence o tier 2 com taxa
  maior que ela.
- Gates E1–E5 e G1–G7 continuam valendo.

## 7. Testes

- Treino, fadiga e sobrecarga reproduzem bit a bit pelo replay.
- Sobrecarga sobrevive à evolução; os demais contadores zeram.
- Forçar só fica disponível com fadiga ≥ limite.
- Toque dentro do intervalo mínimo é rejeitado e não consome orçamento.
- Orçamento total idêntico entre braços, incluindo o exigente.
- Normalização da arena preserva proporções e devolve o total ao
  orçamento da espécie.
- Nada em `CondicaoFisica` lê treino ou sobrecarga (teste por AST).

## 8. Runs

- Arena com os cinco braços (atencioso, relapso, aleatório, incoerente,
  exigente), ovos pareados, em `artifacts_treino/`.
- Campanha dos cinco braços contra os três NPCs em `artifacts_campanha/`.

## 9. O que reportar

Sem rodeios, nesta ordem:

1. **Exigente × atencioso:** fração de formas sombrias, vínculo final,
   obediência, arena (normalizada) e campanha. Forçar compensa ou não?
   Diga primeiro.
2. Gates S1 e S2; se o devastador dominar, diga.
3. Distribuição de formas adultas (normais e sombrias) por braço.
4. Números ajustados na calibração, de quanto para quanto.

Nenhum número sem o artefato que o gerou.
