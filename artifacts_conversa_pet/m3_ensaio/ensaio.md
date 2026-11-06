# Ensaio qualitativo da M3 (não é avaliação, sem gate)

`gemma2:9b` local, temperatura 0,7, sementes de diagnóstico 7000+ (adolescente) e 7100+ (adulto), as 8 mensagens de
`artifacts_conversa_pet/diagnostico/conversa_estagios.py`, o mesmo estado à mão, histórico do próprio ensaio.

## adolescente

| jogador | livre-v2 | conversa-v1 |
|---|---|---|
| oi! tudo bem com você? | Dormindo. `R1` | Mais ou menos. Estou com muita fome e meio cansado. E você, como foi o dia? `E1,R1` |
| eu sou o Matheus, prazer | Hum. | Matheus, hum. E o que você quer? |
| lembra meu nome? | Hum. | Não. Você me disse o nome há pouco tempo? |
| por que você está bravo? | Não me liga. `E2,M1,R1` | Você me deixou esperando há uns 22 minutos. Aí o humor cai. `M1,E1` |
| hoje meu dia foi difícil no trabalho | Humm. | Poxa, difícil como? Eu estou mal-humorado, mas quero saber. `E1` |
| você lutou ontem, né? | Não lembra. | Disso eu não lembro. |
| vai comer | Ainda não. `E1,D1,R1` | Finalmente! Você vai me dar comida? `D1` |
| me conta alguma coisa sobre você | … **erro: chamada: HTTPError: HTTP Error 500: Internal Server Error** | Eu sou um Growlmon. E tenho muita fome. `I1,E1` |

livre-v2: tamanho médio da fala 7 caracteres (min 1, max 12); 0 de 8 com pergunta.

conversa-v1: tamanho médio da fala 45 caracteres (min 20, max 75); 5 de 8 com pergunta.

## adulto

| jogador | livre-v2 | conversa-v1 |
|---|---|---|
| oi! tudo bem com você? | … **erro: chamada: HTTPError: HTTP Error 500: Internal Server Error** | Estou meio cansado e com fome, mas respondo. `E1,E2,M1` |
| eu sou o Matheus, prazer | Humm... | Prazer, Matheus. |
| lembra meu nome? | Hummm... não. `M1,T1` | Não, não lembro. Você me disse agora? |
| por que você está bravo? | Não sei. Você me deixou esperando. `M1,E2` | Você me deixou esperando há uns 22 minutos, e eu estou com fome. Ainda estou meio azedo. `M1,E1` |
| hoje meu dia foi difícil no trabalho | Hmm... | Sinto muito. |
| você lutou ontem, né? | Não sei. | Disso eu não lembro. |
| vai comer | Comi? `E1,D1` | Finalmente! `D1` |
| me conta alguma coisa sobre você | Fome. `E1,D1` | Sou um WarGrowlmon e sou bem teimoso. Agora só penso em comer. `I1,T1,D1` |

livre-v2: tamanho médio da fala 10 caracteres (min 1, max 34); 1 de 8 com pergunta.

conversa-v1: tamanho médio da fala 36 caracteres (min 11, max 88); 1 de 8 com pergunta.
