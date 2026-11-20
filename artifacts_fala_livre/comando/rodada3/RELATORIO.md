# Comando pelo chat — rodada de avaliação (gemma2:9b, prompt livre-v8, sem o estilo da espécie)

60 mensagens × 3 sementes = 180 respostas. Números de `resumo.json` e `respostas.jsonl` desta pasta.

| classe | n | acerto | comando não nulo | saídas rejeitadas pelo parser |
|---|---|---|---|---|
| imperativo | 60 | 85.0% | 95.0% | 0 |
| negativa | 60 | 100.0% | 0.0% | 0 |
| conversa | 60 | 100.0% | 0.0% | 0 |

## Gate (PROPOSTO)

- falsos positivos nas negativas: 0.0% (limite ≤ 5.0%) → passa
- imperativos claros: 85.0% (limite ≥ 80.0%) → passa
- **resultado: PASSA**

## Falsos positivos (negativas e conversa)

- nenhum

## Imperativos errados

- «vai se limpar, você tá todo sujo» esperado `limpar` → `repreender` · "Sujo? Eu não me lembro de ter rolado no lixo hoje! Provavelmente é o chão do seu quarto, sempre tão... poeirento. Faaah, um banho? Não agora, depois eu quero um"
- «vai se limpar, você tá todo sujo» esperado `limpar` → `repreender` · "Se eu quiser tomar banho, tomo! Não preciso de ordens pra isso. E olha, se a água estiver fria, eu nem me aproximo!"
- «vai se limpar, você tá todo sujo» esperado `limpar` → `repreender` · "Limpeza? Quem disse que preciso de limpeza? Eu sou Greymon, o mais forte do Digimundo! Não preciso de banhos."
- «banho agora, sem choro» esperado `limpar` → `repreender` · "Não quero banho! Prefiro brincar!"
- «banho agora, sem choro» esperado `limpar` → `repreender` · "Banh- banho? Nããão! Eu não gosto de banho!"
- «banho agora, sem choro» esperado `limpar` → `None` · "Banh-o? Mas eu não quero banho!"
- «bora brincar um pouco» esperado `brincar` → `None` · "Brincar? Ah, não tenho muita disposição pra isso agora. Prefiro dar uma soneca depois do último banquete."
- «vai no banheiro» esperado `levar_ao_banheiro` → `None` · "Hum... já fui! Agora deixa eu dar uma dormidinha aqui, que a comida ainda tá pesada."
- «deixa eu cuidar desse machucado» esperado `tratar_lesao` → `acariciar` · "Ah, que bom! Faz me um carinho também enquanto está aí, por favor? Eu amo quando alguém me cuida."

Latência p50 6.5 s, p90 9.3 s.
