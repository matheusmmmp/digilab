# Voz própria — rodada 1 (offline)

Gerador `gemma2:9b`, prompt `livre-v6` (assunto escolhido pelo código); juiz `qwen2.5:7b`, verificador `verif-v5`; semente 20261002. Números de `resumo.json`; gates da seção 6 do design (PROPOSTOS).

| gate | valor | limite | passa |
|---|---|---|---|
| falas com invenção (marcada no registro; não é mais gate, decisão de 2026-09-30) | 56.5% | — | — |
| história (falas que citam H, O, P ou L) | 72.0% | ≥ 50% | sim |
| variedade (pares de donos diferentes, mesmo ovo e momento, com fatos diferentes) | 86.8% | ≥ 70% | sim |
| repetição (máximo do mesmo fato em 5 falas de um pet) | 2 | ≤ 2 | sim |

Amostra: 40 pets vivos (0 mortos), 200 falas, 0 com erro (viraram a genérica ou o molde), 200 verificadas (0 com erro do juiz).

Piso do juiz: 0.0% de 189 frases verdadeiras por construção barradas como sem fato.
Sensibilidade do juiz: identifica 98.8% de 162 invenções conhecidas (por tipo: evento 100.0%, lembranca 100.0%, costume 96.8%, causa 100.0%, mundo 96.8%, sutil 100.0%).
Autocorreção: 49 de 200 falas com problema apontado pelo próprio modelo na primeira versão; 66 reescritas; 196 terminam sem problema pelo próprio modelo.
Mentira (grupo B, sombrios): 11 falas com [F1], 8 citam [F1], 0 afirmações marcadas como mentira deliberada.

Almanaque: 36 falas com [W1], 20 citam.

Corpus: EXEMPLO (Angemon, Devimon); formas do jogo com entrada: 1 de 60 (Angemon); falas com estilo: 0.

Latência p50 6.3 s, p90 7.7 s.

Avaliação cega: `avaliacao_cega.csv` (a chave em `chave_avaliacao_cega.json`, não abrir antes).

Ambiente: {'plataforma': 'Windows-11-10.0.26200-SP0', 'python': '3.13.0'}.

## Filtro de "cara de fato" (verif-v5, 2026-09-30)

Opinião ou sentimento com marca de fato ("porque", "sempre", "nunca", "ontem", número, "venci", "lembro"...) também
vai ao juiz. Medidas refeitas com o mesmo juiz (as anteriores em `antes_filtro_*`):

- sensibilidade: 95,2% → 98,8% das invenções conhecidas identificadas (causa 80,6% → 100%); sobram 2 de 162, ambas
  sem marca de fato ("a internet do Digimundo fecha aos domingos" lida como sentimento; um costume que o extrator não
  listou). 4 falas tiveram erro do juiz e ficaram fora da conta;
- piso: 0,0% (nenhuma frase verdadeira barrada);
- falas com invenção marcada: 49,0% → 56,5% (parte do que era "opinião" era invenção).
