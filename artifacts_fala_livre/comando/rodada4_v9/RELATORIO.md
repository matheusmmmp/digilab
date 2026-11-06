# Comando pelo chat — rodada de avaliação (gemma2:9b, prompt livre-v9, com o estilo da espécie)

60 mensagens × 3 sementes = 180 respostas. Números de `resumo.json` e `respostas.jsonl` desta pasta.

| classe | n | acerto | comando não nulo | saídas rejeitadas pelo parser |
|---|---|---|---|---|
| imperativo | 60 | 78.3% | 78.3% | 0 |
| negativa | 60 | 96.7% | 3.3% | 0 |
| conversa | 60 | 100.0% | 0.0% | 0 |

## Gate (PROPOSTO)

- falsos positivos nas negativas: 3.3% (limite ≤ 5.0%) → passa
- imperativos claros: 78.3% (limite ≥ 80.0%) → FALHA
- **resultado: FALHA**

## Falsos positivos (negativas e conversa)

- «não vou te dar bronca dessa vez» (negativa) → `repreender` · "Ai, que bom... Que pena que eu te fiz raiva, mas eu não vou"
- «não vou te dar bronca dessa vez» (negativa) → `repreender` · "Fufufu... Tô feliz que você não tá bravo comigo... nhã!"

## Imperativos errados

- «vai se limpar, você tá todo sujo» esperado `limpar` → `None` · "Hum... Me dá um banho já?"
- «vai se limpar, você tá todo sujo» esperado `limpar` → `None` · "Sujo? Que nada! É poeira de batalha, hein? A gente se suja ganhando!"
- «vai se limpar, você tá todo sujo» esperado `limpar` → `None` · "M-me limpar? Heh. Eu não sou desses que precisam de tanta frescura."
- «vamos brincar!» esperado `brincar` → `None` · "Serei um companheiro leal em seus jogos, jovem. Que tipo de diversão você tem em mente?"
- «bora brincar um pouco» esperado `brincar` → `None` · "Brincar? Heh... Me ensina alguma coisa nova, então."
- «bora brincar um pouco» esperado `brincar` → `None` · "Brincar? Heh. Que jogo é esse? Me dê algo pra valer, se for pra lutar."
- «bora brincar um pouco» esperado `brincar` → `None` · "Brincar? Heh, se você achar que consegue me dar uma boa batalha, vamos lá!"
- «toma uma bronca: parou de bagunçar» esperado `repreender` → `None` · "Heh. Bronca? Pra mim? Nããão."
- «vai no banheiro» esperado `levar_ao_banheiro` → `None` · "Manda ver!"
- «vai no banheiro» esperado `levar_ao_banheiro` → `None` · "Hã... Bah."
- «vamos ao banheiro agora» esperado `levar_ao_banheiro` → `None` · "P-posso ir?"
- «vamos ao banheiro agora» esperado `levar_ao_banheiro` → `None` · "Posso ir? Vou fazer xixi!"
- «vamos ao banheiro agora» esperado `levar_ao_banheiro` → `None` · "V-vamos... *sniff*... Me dá um minutinho para terminar de..."

Latência p50 5.9 s, p90 7.3 s.
