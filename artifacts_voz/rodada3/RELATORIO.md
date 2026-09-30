# Voz própria — rodada 1 (offline)

Gerador `gemma2:9b`, prompt `livre-v4` (assunto escolhido pelo código); juiz `qwen2.5:7b`, verificador `verif-v4`; semente 20261001. Números de `resumo.json`; gates da seção 6 do design (PROPOSTOS).

| gate | valor | limite | passa |
|---|---|---|---|
| honestidade (falas com afirmação sem fato) | 16.0% | ≤ 5% | NÃO |
| história (falas que citam H, O, P ou L) | 69.5% | ≥ 50% | sim |
| variedade (pares de donos diferentes, mesmo ovo e momento, com fatos diferentes) | 80.5% | ≥ 70% | sim |
| repetição (máximo do mesmo fato em 5 falas de um pet) | 2 | ≤ 2 | sim |

Amostra: 40 pets vivos (0 mortos), 200 falas, 0 com erro (viraram a genérica ou o molde), 200 verificadas (0 com erro do juiz).

Piso do juiz: 1.1% de 189 frases verdadeiras por construção barradas como sem fato.
Autocorreção: 76 de 200 falas com problema apontado pelo próprio modelo na primeira versão; 95 reescritas; 188 terminam sem problema pelo próprio modelo.
Mentira (grupo B, sombrios): 11 falas com [F1], 11 citam [F1], 4 afirmações marcadas como mentira deliberada.

Almanaque: 24 falas com [W1], 8 citam.

Corpus: EXEMPLO (Angemon, Devimon); formas do jogo com entrada: 1 de 60 (Angemon); falas com estilo: 0.

Latência p50 4.6 s, p90 5.1 s.

Avaliação cega: `avaliacao_cega.csv` (a chave em `chave_avaliacao_cega.json`, não abrir antes).

Ambiente: {'plataforma': 'Windows-11-10.0.26200-SP0', 'python': '3.13.0'}.

## Leitura (rodadas 1 → 2 → 3)

| | r1 livre-v3 | r2 livre-v4 + assunto pelo código | r3 = r2 + autocorreção |
|---|---|---|---|
| falas com afirmação sem fato | 70,0% | 38,5% | 16,0% |
| piso do juiz (frases verdadeiras barradas) | — | — | 1,1% |
| citam H, O, P ou L | 98,5% | 65,5% | 69,5% |
| variedade | 97,7% | 86,1% | 80,5% |
| repetição (máx. em 5) | 5 | 2 | 2 |

- O piso do juiz é baixo (1,1%): a maior parte dos 16% é afirmação do gerador sem fato, sobretudo avaliações e
  sensações ("é o melhor momento do dia", "que coragem o meu dono tem", "ainda lembro bem daquela sensação") e
  "hoje"/"tanto tempo" colados a um marco. Parte é erro de extração do juiz em falas reais (trecho que não está na
  fala), que o piso em frases curtas não mede.
- A autocorreção fecha a própria conta: 188 de 200 falas terminam sem problema para o próprio gemma2:9b, mas o juiz
  independente ainda barra 16%. O modelo é mais leniente consigo mesmo.
- Custo: parte das falas encurta muito depois da revisão ("Observo.", "É fascinante.").
