# Seleção de ação

**NENHUMA ARQUITETURA ESCOLHIDA.**

## A proposta: circuitos especializados (HIPÓTESE DIGILAB, Matheus 2026-10-01, inspirada na *Drosophila*)

```
                 PERCEPTION
                     ↓
        ┌────────────┼────────────┐
      threat       social       object
      circuit      circuit      circuit
        └────────────┼────────────┘
                INTEGRATION
                     ↓
              ACTION SELECTION
                     ↓
             descending command
                     ↓
                    BODY
                     ↓
             ascending feedback
```

## Nas fontes

- **CORPUS:** a diversidade de circuitos da mosca é anatômica; a função varia (Dorkenwald et al. 2024; Shiu et al. 2024). Isso
  mostra heterogeneidade, **não** que controle modular vence uma política única.
- **CORPUS:** o CST favorece urgência por subsunção dinâmica numa tarefa estreita (Fróes e Gudwin 2017); Rossi et al. 2024
  comparam drives × impulsos, não política global × modular.
- **VERIFICADA (precedente de bloqueio):** a separação instinto × aprendido no mesmo agente já foi publicada (Hallawa et al.).

## No DigiLab hoje (REPOSITÓRIO)

- A `PoliticaLobos` (L0) já é seleção em estágios: **percepção** (10 entradas) → **impulsos** (as regras do instinto
  propõem candidatos) → **decisão** (pesos inteiros escolhem entre eles). Os "sistemas de comportamento" de hoje são as
  regras do instinto, organizadas **por necessidade** (sono, fome, abandono), não por classe de estímulo.
- Não há circuito de ameaça (não há ameaça no mundo da pesquisa; lesões vêm do sparring da educação-v1), nem social além do
  dono, nem de objeto (a bola é o primeiro objeto, PR #113).
- A luta é **outro sistema** (gambits do combate V2.1, com lista ordenada de regras): não passa pela política da vida.
- "Comando descendente → corpo → retorno ascendente": não há corpo; a ação muda o estado (`policy.efeito_da_acao_do_pet`).

## Hipóteses

| ID | pergunta | teste mínimo |
|---|---|---|
| H-ACT-001 | um seletor modular difere da política atual em estabilidade, diversidade ou eficiência amostral, com capacidade igual | mesma observação, mesmas ações, mesmo número de parâmetros e mesmo treino |
| H-ACT-02 | circuitos por classe de estímulo (ameaça, social, objeto) em vez de por necessidade mudam o que é aprendido | só depois de o mundo ter estímulos das três classes; sem isso os circuitos ficam vazios |
| H-ACT-03 | "duas prioridades" (necessidade × pedido do dono) — nó L3 | G5 continua valendo |

Confundidores: capacidade diferente, impasse de arbitragem, afinação das prioridades, composição da tarefa. Métricas:
sucesso, oscilação da política, diversidade, latência, custo.
