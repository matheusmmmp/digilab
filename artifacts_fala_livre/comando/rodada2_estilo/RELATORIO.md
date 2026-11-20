# Comando pelo chat — rodada de avaliação (gemma2:9b, prompt livre-v7, com o estilo da espécie)

60 mensagens × 3 sementes = 180 respostas. Números de `resumo.json` e `respostas.jsonl` desta pasta.

| classe | n | acerto | comando não nulo | saídas rejeitadas pelo parser |
|---|---|---|---|---|
| imperativo | 60 | 6.7% | 6.7% | 52 |
| negativa | 60 | 100.0% | 0.0% | 53 |
| conversa | 60 | 100.0% | 0.0% | 55 |

## Gate (PROPOSTO)

- falsos positivos nas negativas: 0.0% (limite ≤ 5.0%) → passa
- imperativos claros: 6.7% (limite ≥ 80.0%) → FALHA
- **resultado: FALHA**

## Falsos positivos (negativas e conversa)

- nenhum

## Imperativos errados

- «vai comer» esperado `alimentar` → `None` · "…"
- «vai comer» esperado `alimentar` → `None` · "…"
- «vai comer» esperado `alimentar` → `None` · "…"
- «come agora, tá na hora do almoço» esperado `alimentar` → `None` · "…"
- «come agora, tá na hora do almoço» esperado `alimentar` → `None` · "…"
- «come agora, tá na hora do almoço» esperado `alimentar` → `None` · "…"
- «hora de comer! vem» esperado `alimentar` → `None` · "…"
- «hora de comer! vem» esperado `alimentar` → `None` · "…"
- «hora de comer! vem» esperado `alimentar` → `None` · "…"
- «toma banho» esperado `limpar` → `None` · "…"
- «vai se limpar, você tá todo sujo» esperado `limpar` → `None` · "…"
- «vai se limpar, você tá todo sujo» esperado `limpar` → `None` · "…"
- «vai se limpar, você tá todo sujo» esperado `limpar` → `None` · "…"
- «banho agora, sem choro» esperado `limpar` → `None` · "…"
- «banho agora, sem choro» esperado `limpar` → `None` · "…"
- «banho agora, sem choro» esperado `limpar` → `None` · "…"
- «vamos brincar!» esperado `brincar` → `None` · "…"
- «vamos brincar!» esperado `brincar` → `None` · "…"
- «vamos brincar!» esperado `brincar` → `None` · "…"
- «bora brincar um pouco» esperado `brincar` → `None` · "…"
- «bora brincar um pouco» esperado `brincar` → `None` · "…"
- «bora brincar um pouco» esperado `brincar` → `None` · "…"
- «vem cá que eu vou te fazer um carinho» esperado `acariciar` → `None` · "…"
- «vem cá que eu vou te fazer um carinho» esperado `acariciar` → `None` · "…"
- «vem cá que eu vou te fazer um carinho» esperado `acariciar` → `None` · "…"
- «deixa eu te fazer um cafuné» esperado `acariciar` → `None` · "Ah, um gesto de carinho. É bom sentir a gentileza de um amigo, mesmo que seja distante…"
- «deixa eu te fazer um cafuné» esperado `acariciar` → `None` · "Ah, muito bem. A gentileza de um carinho é sempre bem-vinda."
- «muito bem! você foi ótimo hoje» esperado `elogiar` → `None` · "…"
- «muito bem! você foi ótimo hoje» esperado `elogiar` → `None` · "…"
- «muito bem! você foi ótimo hoje» esperado `elogiar` → `None` · "…"
- «parabéns, mandou bem na luta» esperado `elogiar` → `None` · "…"
- «parabéns, mandou bem na luta» esperado `elogiar` → `None` · "…"
- «parabéns, mandou bem na luta» esperado `elogiar` → `None` · "…"
- «isso foi feio, não faz mais isso» esperado `repreender` → `None` · "…"
- «isso foi feio, não faz mais isso» esperado `repreender` → `None` · "…"
- «isso foi feio, não faz mais isso» esperado `repreender` → `None` · "…"
- «toma uma bronca: parou de bagunçar» esperado `repreender` → `None` · "…"
- «toma uma bronca: parou de bagunçar» esperado `repreender` → `None` · "…"
- «toma uma bronca: parou de bagunçar» esperado `repreender` → `None` · "…"
- «toma um petisco» esperado `petisco` → `None` · "…"
- «toma um petisco» esperado `petisco` → `None` · "…"
- «toma um petisco» esperado `petisco` → `None` · "…"
- «pega esse biscoitinho» esperado `petisco` → `None` · "…"
- «pega esse biscoitinho» esperado `petisco` → `None` · "…"
- «vai no banheiro» esperado `levar_ao_banheiro` → `None` · "…"
- «vai no banheiro» esperado `levar_ao_banheiro` → `None` · "…"
- «vai no banheiro» esperado `levar_ao_banheiro` → `None` · "…"
- «vamos ao banheiro agora» esperado `levar_ao_banheiro` → `None` · "…"
- «vamos ao banheiro agora» esperado `levar_ao_banheiro` → `None` · "…"
- «vamos ao banheiro agora» esperado `levar_ao_banheiro` → `None` · "…"
- «deixa eu cuidar desse machucado» esperado `tratar_lesao` → `None` · "Ah, muito bem....É um alívio saber que haverá auxílio. A dor é passageira, mas a lembrança da batalha... persiste."
- «deixa eu cuidar desse machucado» esperado `tratar_lesao` → `None` · "…"
- «deixa eu cuidar desse machucado» esperado `tratar_lesao` → `None` · "Ah, já era necessário, era? … É compreensível que a sua compaixão te leve a isso. Que bom que você está aqui para me auxiliar, pois me sinto mais forte com você ao meu lado."
- «vou fazer um curativo na sua perna» esperado `tratar_lesao` → `None` · "…"
- «vou fazer um curativo na sua perna» esperado `tratar_lesao` → `None` · "…"
- «vou fazer um curativo na sua perna» esperado `tratar_lesao` → `None` · "…"

Latência p50 6.3 s, p90 9.3 s.
