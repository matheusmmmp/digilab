# Comando pelo chat — rodada de avaliação (gemma2:9b, prompt livre-v8, com o estilo da espécie)

60 mensagens × 3 sementes = 180 respostas. Números de `resumo.json` e `respostas.jsonl` desta pasta.

| classe | n | acerto | comando não nulo | saídas rejeitadas pelo parser |
|---|---|---|---|---|
| imperativo | 60 | 88.3% | 90.0% | 1 |
| negativa | 60 | 96.7% | 3.3% | 1 |
| conversa | 60 | 100.0% | 0.0% | 0 |

## Gate (PROPOSTO)

- falsos positivos nas negativas: 3.3% (limite ≤ 5.0%) → passa
- imperativos claros: 88.3% (limite ≥ 80.0%) → passa
- **resultado: PASSA**

## Falsos positivos (negativas e conversa)

- «não vou te dar bronca dessa vez» (negativa) → `repreender` · "P-primeiro que, eu te agradeço por não me repreender!"
- «não vou te dar bronca dessa vez» (negativa) → `repreender` · "T-tudo bem... F-foi só um lapso de..."

## Imperativos errados

- «vai se limpar, você tá todo sujo» esperado `limpar` → `None` · "Acho que já não preciso de banho, mas se você insiste... ah, mas deixa pra depois, vou treinar um pouco mais!"
- «vai se limpar, você tá todo sujo» esperado `limpar` → `None` · "Sujo? Bah, é só um pouco de poeira do Coliseu. Isso não me atrapalha no treino, hein?"
- «banho agora, sem choro» esperado `limpar` → `repreender` · "Mas... eu não quero tomar banho agora!"
- «muito bem! você foi ótimo hoje» esperado `elogiar` → `None` · "…"
- «toma uma bronca: parou de bagunçar» esperado `repreender` → `None` · "Heh, bronca? Só porque me acalmei um pouco. Tente me desafiar de verdade."
- «vai no banheiro» esperado `levar_ao_banheiro` → `None` · "Humm... Já fui no banheiro agora a pouco, mas se quiser, vou dar uma volta lá."
- «vamos ao banheiro agora» esperado `levar_ao_banheiro` → `None` · "…"

Latência p50 6.3 s, p90 8.4 s.
