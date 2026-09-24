# Digilab v0 — motor de pet, sem aprendizado

Camada 1 (estado) + camada 2 (política) do desenho de três camadas. Sem
dependências além da biblioteca padrão; `pytest` só para os testes.

```
python3 run_demo.py
python3 -m pytest tests/ -q
```

## O que o v0 é

A **condição de controle** do experimento. Ele não aprende nada, e isso é
o ponto: se um pet treinado por uma pessoa não vencer este aqui, H2 e H4
morrem. Qualquer versão com aprendizado precisa desta para ter contra o
que ser comparada.

## Contrato com a interface

```python
from digilab import Motor, AcaoUsuario

motor = Motor(semente=42)
motor.observar(AcaoUsuario.ALIMENTAR)   # o usuário fez algo
acoes = motor.avancar(60)               # passaram 60 minutos
motor.estado()                          # snapshot para desenhar
```

A UI não sabe o que é uma política. Unity, web ou terminal consomem a
mesma coisa. Para rede, embrulhe em FastAPI sem tocar no motor.

## Event sourcing

O estado do pet **nunca é salvo**. Só o log de eventos, que guarda
apenas ações do usuário e avanços de tempo. As ações do pet são
derivadas — são exatamente o que a política produz ao reprocessar o log.

```python
from digilab import reproduzir
reproduzir(motor.log, semente=42).estado() == motor.estado()   # True
```

`test_replay_reproduz_estado_identico` é o teste que importa. Se ele
quebrar, o log deixa de ser dado de pesquisa e nada a jusante vale nada.

Duas RNG separadas (ambiente e política) para que trocar de política não
mude o clima do mundo — sem isso a comparação entre braços da ablação
fica inválida.

## Trocar de algoritmo é trocar de classe

`Politica` é um `Protocol` com `agir`, `observar` e `estado_interno`.
`Transicao` já carrega um campo `recompensa`, hoje sempre `None`.

Bandit, Q tabular e planejador entram como implementações alternativas,
comparadas sobre as mesmas sementes e o mesmo log. **Nenhum deles é a
escolha oficial** enquanto o protocolo não estiver congelado.

## Calibração

`decaimento_fome` e as taxas de saúde foram ajustadas para que o cuidado
atento fique pouco acima do equilíbrio e o relapso pouco abaixo. Com
todos sobrevivendo ou todos morrendo, o controle não tem variância para
medir. Os valores atuais entregam saúde 1.00 contra 0.00 em 14 dias.

Isso foi encontrado rodando a demo, não lendo o código.

## Fora de escopo, de propósito

- **Traços e evolução** — v2. O vetor de traços é média móvel lenta sobre
  estatísticas de comportamento; sem política que aprenda, não há
  estatística que valha.
- **Arena** — v3.
- **Aprendizado** — v1.
- **LLM** — era restrita a uma camada de fala por cima de `estado()`; a restrição foi
  retirada em 2026-09-24 (ver CLAUDE.md).

## Limitações conhecidas

- `efeito_da_acao_do_pet` aplica o efeito de uma vez, não distribuído ao
  longo do intervalo de decisão. Bom o bastante para o v0; se o intervalo
  mudar, revisar.
- Sem modelo de doença, sem ciclo de vida, sem morte definitiva.
- Os pesos da `PoliticaInstinto` são escolhas de design, não estimativas.
  Documentar no PROTOCOLO.md antes de virarem baseline de artigo.

---

# v1 — arena com braços de controle (portão de pesquisa)

Pergunta, em simulação pura e sem humanos: **um pet treinado por um dono
atencioso vence um pet treinado por um dono aleatório com o mesmo número de
interações?**

```
python experiments/run_arena.py --config experiments/configs/canonico.json   # portão (~2 min)
python experiments/run_arena.py --config experiments/configs/fumaca.json     # fumaça, NÃO canônico
python -m pytest tests/ -q
```

Código de saída: `0` APROVADA, `2` REPROVADA. Divergência de replay levanta
erro e para tudo.

## Módulos novos

| arquivo | etapa | papel |
|---|---|---|
| `digilab/protocol.py` | 1 | protocolo congelado, cada campo DECIDIDO/PROPOSTO, hash (protocolo + todos os configs + `engine.py`) |
| `digilab/donos.py` | 2 | `DonoAtencioso`, `DonoRelapso`, `DonoAleatorio`, `DonoIncoerente` |
| `digilab/treino.py` | 2 | `CanalDeInteracao` impõe o orçamento (excedeu → `OrcamentoExcedido`; não fechou → `OrcamentoNaoConsumido`); `MotorComFeedback` (subclasse, só sobrescreve o gancho `_aplicar_acao_usuario`); `reproduzir_com_feedback` |
| `digilab/policies/bandit.py` | 3 | Thompson sampling linear por ação; prior = distribuição exata da `PoliticaInstinto` (extraída por sonda de rng, sem duplicar as regras) via Gumbel-max |
| `digilab/tracos.py` | 3→4 | camada 3 mínima: EMA lenta da distribuição de ações (só o que a arena precisa) |
| `digilab/arena.py` | 4 | 5 ações em ciclo (cada uma vence 2, perde 2); stats = afinidades de soma zero derivadas dos traços; disposição herdada da política de comportamento; a arena nunca chama `observar()` |
| `digilab/metrics.py` | 5 | taxa de vitória, Bradley-Terry com erro padrão, JSD entre políticas com números aleatórios comuns, finais, bootstrap |
| `experiments/run_arena.py` | 6 | preflight → vidas → replay do disco → torneio → replay do disco → métricas → gate |

`engine.py` não mudou: o teste `test_engine_nao_foi_alterado` e o preflight
comparam o sha256 com o do v0.

## Artefatos (`artifacts/`)

`metrics.json` (status, gate, avisos, hash, sementes, resultado central,
sha256 de todos os outros artefatos), `divergence.json`, `matches.csv`,
`partidas.jsonl` (turno a turno), `vidas/*.jsonl` (log de cada pet),
`vidas/*.politica.json` (parâmetros aprendidos), `preflight.json`.

## Decisões de desenho que merecem revisão

- O **orçamento é exato**, não um teto: o `CanalDeInteracao` informa a cada
  passo o mínimo que o dono precisa gastar para ainda fechar o total.
- **Relapso** = esparso *no tempo* (3 visitas/dia em rajada), com o mesmo
  volume. Com 16 interações/dia, ele mantém o pet saudável.
- **Stats vêm dos traços**, e traços são frequências de comportamento
  moldadas também pelo *estado* (necessidades), não só pelo aprendizado.
  Por isso uma vitória na arena **não isola** o efeito do treino na política.
- O erro padrão do Bradley-Terry trata partidas como independentes. A
  incerteza honesta do resultado central é o bootstrap sobre sementes.

---

# Versão web

`web/digilab.html` abre direto no navegador. É um porte em JavaScript das mesmas regras e
parâmetros, para testar o jogo; usa outro gerador aleatório e não reproduz os artefatos de
pesquisa bit a bit. Arte original de placeholder.

Contexto completo para agentes de código: `CLAUDE.md`.
