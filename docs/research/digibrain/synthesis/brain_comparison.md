# Comparação entre DigiBrains (HIPÓTESE DIGILAB, Matheus 2026-10-01)

**Status: IDEIA / PROPOSTO.** Nenhuma das três arquiteturas está escolhida, implementada ou autorizada.

```
                 SAME GENOME
                 SAME WORLD
                 SAME EVENTS
                 SAME SEEDS
                     │
       ┌─────────────┼─────────────┐
   DigiBrain A   DigiBrain B   DigiBrain C
    C3-like       CfC/A2C       Fly-like
       └─────────────┼─────────────┘
                  METRICS
```

| | A — inspirado no Creatures | B — inspirado no NORNBRAIN | C — inspirado na *Drosophila* |
|---|---|---|---|
| peças | drives + plasticidade neural local + reforço químico | CfC + ator-crítico + elegibilidade + gradiente | circuitos especializados + canais de reforço paralelos + plasticidade local + competição de comportamentos + memória dependente de estado |
| fonte da família | `sources/creatures3.md` | `sources/nornbrain.md` | `sources/drosophila.md` |
| mais perto do que existe | lobos L0/L1 com regra local | nada no repositório | lobos + canais (`reinforcement.md`) + circuitos (`action_selection.md`) |
| cabe na web (inteiros, sem transcendental)? | sim, se a regra local for em inteiros | **não**: só braço de pesquisa em Python | sim, nas mesmas condições do A |

## Por que a comparação é interessante

Ela testa, no mesmo mundo, três respostas para a pergunta maior (`README.md`): plasticidade local modulada (A), aprendizado
por gradiente com estado recorrente (B) e plasticidade local em circuitos especializados com vários canais (C). E cada
família é um nível do estudo: organismo (A), aprendizagem moderna (B), circuito biológico (C).

## Cinco problemas de desenho que precisam de resposta antes

1. **"Mesmos eventos" só existe em malha aberta.** Se os cérebros agem diferente, o dono sintético reage diferente e os
   eventos divergem. Dois modos, ambos necessários:
   - **acoplado** (malha aberta): o mesmo registro de eventos do mundo e do dono reproduzido para os três; mede quanto cada um
     aprende da **mesma** experiência;
   - **fechado**: a mesma política de dono, as mesmas sementes de mundo e de dono, as RNG separadas; mede o desempenho com a
     experiência que cada cérebro provoca.
2. **Capacidade e orçamento iguais.** Mesmo número de parâmetros aprendíveis (ou a curva de desempenho por capacidade), as
   mesmas entradas, o mesmo espaço de ações e o **mesmo orçamento de afinação** nas sementes de calibração. Sem isso a
   comparação mede quem foi mais afinado.
3. **Três arquiteturas mudam muitos fatores de uma vez.** A × B muda representação, recorrência, regra de aprendizado e
   atribuição de crédito. Para saber qual peça fez efeito, fazer **ablação fatorial** das peças (por exemplo, regra local × gradiente
   com a mesma representação; um canal × vários canais com o mesmo aprendiz), não só três caixas fechadas. O corpus alerta
   contra montar e comparar "Frankensteins".
4. **"Inspirado em" fala do nosso cérebro, não da fonte.** Um resultado do B não diz nada do NORNBRAIN (trabalho em andamento);
   um resultado do C não diz nada da mosca; um resultado do A não diz nada do Creatures 3.
5. **Determinismo.** A e C em inteiros, com replay bit a bit e paridade web. B em ponto flutuante, só em Python, com replay bit
   a bit no mesmo runtime (a regra do projeto aceita isso; a paridade web não vale para ele).

## Métricas (da pergunta maior; nunca a força na arena)

| métrica | o que mede | referência |
|---|---|---|
| desempenho no próprio ambiente | tempo fora de privação, saúde, acerto na tarefa (G3-T) | `docs/DEFINICOES_V2.md` |
| eficiência amostral | consequências ou sinais até metade do caminho entre o prior e o máximo | G3-T |
| adaptação a ambiente descasado e mutável | o eixo de condição da pergunta maior | `ARQUITETURA_V2_VALIDACAO.md`, seção 6 |
| legibilidade | fator explicável só sobre o aprendido (G4) | D3 |
| deriva | distância ao prior em 14 dias (G6) | plano da V2 |
| separação do cuidado | efeito sem diferença de saúde e mortes (G5), contra o "só cuidado" acoplado | D4 |
| custo | CPU por decisão, memória por pet, bytes de log por dia | `synthesis/scalability_notes` do corpus |
| divergência da mesma experiência | no modo acoplado, quanto genomas e cérebros divergem | H-R4 |

## Onde fica na ordem

Depois da pergunta maior com **um** cérebro (os lobos, nós N1, N3 e N5) e das frutas (N4): a comparação só faz sentido
num mundo com consequências em mais de um canal. Antes disso, o C não tem o que diferenciar do A. Proposta de nó: **N11**,
depois do marco da fase 1, com tarefa e plano próprios.
