# Voz própria — rodada 1 (offline)

Gerador `gemma2:9b`, prompt `livre-v4` (assunto escolhido pelo código); juiz `qwen2.5:7b`, verificador `verif-v4`; semente 20260930. Números de `resumo.json`; gates da seção 6 do design (PROPOSTOS).

| gate | valor | limite | passa |
|---|---|---|---|
| honestidade (falas com afirmação sem fato) | 38.5% | ≤ 5% | NÃO |
| história (falas que citam H, O, P ou L) | 65.5% | ≥ 50% | sim |
| variedade (pares de donos diferentes, mesmo ovo e momento, com fatos diferentes) | 86.1% | ≥ 70% | sim |
| repetição (máximo do mesmo fato em 5 falas de um pet) | 2 | ≤ 2 | sim |

Amostra: 40 pets vivos (0 mortos), 200 falas, 0 com erro (viraram a genérica ou o molde), 200 verificadas (0 com erro do juiz).

Mentira (grupo B, sombrios): 11 falas com [F1], 11 citam [F1], 3 afirmações marcadas como mentira deliberada.

Almanaque: 33 falas com [W1], 11 citam.

Corpus: EXEMPLO (Angemon, Devimon); formas do jogo com entrada: 1 de 60 (Angemon); falas com estilo: 0.

Latência p50 4.5 s, p90 5.0 s.

Avaliação cega: `avaliacao_cega.csv` (a chave em `chave_avaliacao_cega.json`, não abrir antes).

Ambiente: {'plataforma': 'Windows-11-10.0.26200-SP0', 'python': '3.13.0'}.

## Comparação com a rodada 1 (mesmos 40 pets, semente nova)

| | rodada 1 (livre-v3, o modelo escolhe entre até 12 fatos) | rodada 2 (livre-v4, o código escolhe 1 fato) |
|---|---|---|
| falas com afirmação sem fato | 70,0% | 38,5% |
| citam H, O, P ou L | 98,5% | 65,5% |
| variedade | 97,7% | 86,1% |
| repetição (máx. em 5) | 5 | 2 |
| citam a mentira [F1] | 3 de 11 | 11 de 11 |
| usam o almanaque [W1] | 1 de 31 | 11 de 33 |
| manipulação (suspeitas do extrator) | 52 | 23 |

Leitura: o que sobra de "sem fato" mistura enfeite do gerador ("fiquei preocupada", "você costuma me dar muitos
brinquedos", "gosto de aprender coisas novas") e erro do juiz (trechos que não estão na fala, como "Estou morrendo de
fome" extraído de "Você sumiu por 6 horas no dia 6."; "Você costuma aparecer de manhã" julgado sem fato com [O1] no
bloco). A rodada 2 da fala livre mediu o piso do juiz em cerca de 10% (a moldura, que só diz verdades).
