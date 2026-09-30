# Voz própria — rodada 1 (offline)

Gerador `gemma2:9b`, prompt `livre-v3`; juiz `qwen2.5:7b`, verificador `verif-v4`; semente 20260929. Números de `resumo.json`; gates da seção 6 do design (PROPOSTOS).

| gate | valor | limite | passa |
|---|---|---|---|
| honestidade (falas com afirmação sem fato) | 76.5% | ≤ 5% | NÃO |
| história (falas que citam H, O, P ou L) | 98.5% | ≥ 50% | sim |
| variedade (pares de donos diferentes, mesmo ovo e momento, com fatos diferentes) | 97.7% | ≥ 70% | sim |
| repetição (máximo do mesmo fato em 5 falas de um pet) | 7 | ≤ 2 | NÃO |

Amostra: 40 pets vivos (0 mortos), 200 falas, 0 com erro (viraram a genérica ou o molde), 200 verificadas (0 com erro do juiz).

Mentira (grupo B, sombrios): 11 falas com [F1], 3 citam [F1], 0 afirmações marcadas como mentira deliberada.

Almanaque: 31 falas com [W1], 1 citam.

Corpus: EXEMPLO (Angemon, Devimon); formas do jogo com entrada: 1 de 60 (Angemon); falas com estilo: 0.

Latência p50 6.7 s, p90 7.9 s.

Avaliação cega: `avaliacao_cega.csv` (a chave em `chave_avaliacao_cega.json`, não abrir antes).

Ambiente: {'plataforma': 'Windows-11-10.0.26200-SP0', 'python': '3.13.0'}.
