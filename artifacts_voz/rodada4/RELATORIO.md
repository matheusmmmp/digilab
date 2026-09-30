# Voz própria — rodada 1 (offline)

Gerador `gemma2:9b`, prompt `livre-v6` (assunto escolhido pelo código); juiz `qwen2.5:7b`, verificador `verif-v5`; semente 20261002. Números de `resumo.json`; gates da seção 6 do design (PROPOSTOS).

| gate | valor | limite | passa |
|---|---|---|---|
| falas com invenção (marcada no registro; não é mais gate, decisão de 2026-09-30) | 49.0% | — | — |
| história (falas que citam H, O, P ou L) | 72.0% | ≥ 50% | sim |
| variedade (pares de donos diferentes, mesmo ovo e momento, com fatos diferentes) | 86.8% | ≥ 70% | sim |
| repetição (máximo do mesmo fato em 5 falas de um pet) | 2 | ≤ 2 | sim |

Amostra: 40 pets vivos (0 mortos), 200 falas, 0 com erro (viraram a genérica ou o molde), 200 verificadas (0 com erro do juiz).

Piso do juiz: 0.0% de 189 frases verdadeiras por construção barradas como sem fato.
Autocorreção: 49 de 200 falas com problema apontado pelo próprio modelo na primeira versão; 66 reescritas; 196 terminam sem problema pelo próprio modelo.
Mentira (grupo B, sombrios): 11 falas com [F1], 8 citam [F1], 0 afirmações marcadas como mentira deliberada.

Almanaque: 36 falas com [W1], 20 citam.

Corpus: EXEMPLO (Angemon, Devimon); formas do jogo com entrada: 1 de 60 (Angemon); falas com estilo: 0.

Latência p50 6.3 s, p90 7.7 s.

Avaliação cega: `avaliacao_cega.csv` (a chave em `chave_avaliacao_cega.json`, não abrir antes).

Ambiente: {'plataforma': 'Windows-11-10.0.26200-SP0', 'python': '3.13.0'}.

## Leitura (livre-v6: inventar pode, desde que a invenção seja identificada)

- A invenção deixou de ser erro: 49% das falas têm ao menos uma invenção, todas marcadas no registro pelo juiz
  independente. Nenhuma fala foi cortada por falta de verificação; o piso do juiz foi 0,0% em 189 frases verdadeiras.
- Limite da identificação: o piso mede falso positivo (verdade barrada), não falso negativo (invenção que o juiz
  deixou passar como sustentada). Isso não foi medido.
- Opinião e sentimento: 156 opiniões e 116 sentimentos em 170 das 200 falas.
- Manipulação (32 falas marcadas pelo extrator): a maioria é pergunta ou cobrança, que agora pode; há casos no limite
  da regra que continua valendo ("se eu fosse você, não ficaria tão tranquilo...").
- Defeitos de forma vistos: identificador escrito dentro da fala ("[W1]", "[L1]") e uma fala com caracteres chineses.
