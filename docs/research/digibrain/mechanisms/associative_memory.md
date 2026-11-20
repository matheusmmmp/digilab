# Memória associativa e aprendizado consolidado

## Nas fontes

- **CORPUS:** no corpo de cogumelo da mosca, plasticidade local e compartimentalizada, modulada por dopamina, com vários
  componentes de memória e regras por tipo celular (Aso e Rubin 2016; Cognigni, Felsenberg e Waddell 2019).
- **VERIFICADA:** aprendizado hebbiano na vida no Creatures (Grand et al. 1997).
- **INTERPRETAÇÃO:** aprendizado associativo muda o mapa estímulo → ação/predição depois de coocorrência e consequência. É
  diferente de guardar um episódio narrativo e de estado oculto recorrente.

## No DigiLab hoje (REPOSITÓRIO)

| o que muda depois do feedback | onde | persiste? |
|---|---|---|
| pesos do bandit (v1, congelado) | `policies/bandit.py` | na vida; não passa aos filhos |
| memória curta e por espaços (latência do dono, bronca, elogio, com decaimento) | `memoria.py`, `memoria_espacos.py` | na vida, decai |
| traços (EMA lenta da distribuição de ações) | `tracos.py` | na vida |
| pesos dos lobos (L1, em calibração) | `policies/lobos.py` | na vida |
| gambits da luta (web) | `web/app/motor/gambits_pet.ts` | na vida |

Nada aprendido passa pela herança: os filhos herdam espécie e temperamento (`heranca.py`).

## Hipóteses

| ID | pergunta | teste mínimo |
|---|---|---|
| H-ASSOC-01 | o pet aprende uma associação estímulo → ação → consequência e a **inverte** quando a consequência inverte | reversão controlada e transferência depois de um intervalo, com exposição igual ao controle |
| H-ASSOC-02 | plasticidade local por canal (`reinforcement.md`) dá memórias separáveis por domínio | apagar um canal não apaga o aprendido de outro |

A reversão é o teste direto do braço P2e da pergunta maior (o mundo refuta a informação errada do dono).
