# Decodificador de conceitos do DigiBrain — do estado interno à fala, passando por conceitos

Status: **IDEIA / CONTEXTO** (2026-10-04). Proposta do Matheus. Este documento registra a ideia, o que ela toca no que já existe e a
literatura que a cerca. Ele **não autoriza implementação**, não é um desenho fechado e não muda nenhum experimento.

## 1. A ideia

Os lobos do DigiBrain continuam decidindo numericamente. Uma camada intermediária lê o estado interno deles e extrai **conceitos
interpretáveis** (desejo, medo, conflito, confiança no dono, intenção de esconder). Só depois uma LLM transforma esses conceitos em fala.

```
rede (lobos) → estado latente z_t → conceitos C_t (com incerteza) → LLM → texto
```

e **nunca**

```
rede → LLM → história
```

- `z_t` junta as ativações internas de cada lobo no instante t: percepção, memória e emoção, impulsos e decisão (e, se fizer sentido,
  personalidade e genoma como contexto).
- `C_t` é um vetor de conceitos, cada um com valor e incerteza. Um conceito com incerteza alta não vira afirmação na fala: o pet diz "acho
  que você ficaria bravo" em vez de "vou mentir para você".
- A LLM só faz `conceitos + contexto → linguagem`. Ela não decide nada e não inventa estado que o decodificador não mostrou.

Exemplo do Matheus (números ilustrativos, não do Digilab): desejo de comida 0,91, medo de punição 0,62, afeição pelo dono 0,83, intenção de
desobedecer 0,69 e intenção de enganar 0,54 ± 0,21. Com a incerteza alta no último, a fala fica no desejo e no medo, sem afirmar mentira.

## 2. Onde encosta no que já existe

| peça | o que é hoje | relação |
|---|---|---|
| **Motivo e honestidade do fator** (`digilab/motivo.py`, `CLAUDE.md`, "Honestidade do fator do bandit") | a fala do pet sai de um motivo estruturado; só vira fator uma contribuição positiva acima do limiar e só quando o termo aprendido mudou a escolha; senão o pet diz "não sei" | é a versão manual, de um conceito só, desta ideia; o decodificador generaliza o motivo para um vetor de conceitos com incerteza |
| **Fala por LLM** (`servidor/fala_llm.py`, voz própria, fala livre) | a LLM recebe o motivo e escreve; a saída é conferida e, no modo livre, gravada no log | a parte "conceitos → linguagem" já existe; muda a entrada |
| **G4, fator explicável** (`docs/DEFINICOES_V2.md`, seção 2) | mede a fração de decisões com fator atribuível ao aprendido, contra um controle de capacidade igual sem lobos; cita o CBM de Koh et al. como precedente do custo do gargalo | o decodificador daria um G4 por conceito, e não só por lobo |
| **Mentira** (`ConfigMentira`, `digilab_fala_livre/mentira.py`, `web/app/motor/mentira.ts`, voz própria) | o pet já pode mentir, por regra, na janela de fala | "intenção de enganar" como conceito só vale se o teste causal da seção 4 passar; senão a fala não pode afirmar intenção |
| **Comparação de cérebros** (N11, `docs/research/digibrain/synthesis/brain_comparison.md`) | DigiBrain A e C têm lobos nomeados; o B (CfC/A2C) é opaco | é onde a ideia rende mais: um decodificador de conceitos é uma régua de legibilidade comum aos três |
| **Event sourcing e replay** | toda vida se reconstrói pelo log, bit a bit | `z_t` pode ser recalculado do log a qualquer momento, sem guardar ativações, e o decodificador pode ser treinado depois sobre vidas antigas |

## 3. Dois caminhos (para decidir depois)

1. **Conceitos definidos antes (CBM clássico).** O projeto escolhe a lista de conceitos e treina o decodificador para eles, ou põe o gargalo
   dentro do cérebro. Nos lobos atuais isso é quase trivial: as entradas já têm nome e os pesos são poucos (menos de mil, em inteiros). O
   risco é medir o próprio rótulo, como o G4 da L1 mostrou com o instinto.
2. **Conceitos descobertos depois (M-CBM, Discover-then-Name).** Um autoencoder esparso aprende direções no estado interno, e só depois cada
   uma recebe um nome, por uma LLM ou por um humano, olhando os momentos da vida em que ela acende. Rende mais em cérebro opaco (o B).

E dois lugares para a camada:

- **Por fora (post-hoc):** só lê o estado; a decisão não muda. G1 e G2 continuam valendo sem esforço.
- **Por dentro (ante-hoc):** a decisão passa pelos conceitos. Muda o cérebro, pede um braço próprio com controle de capacidade igual (como o
  D2) e o custo de desempenho reportado, como no CBM.

## 4. O que precisaria ser medido (PROPOSTO, sem número)

- **Fidelidade causal:** mexer num conceito (intervenção, como no CBM) muda a decisão do jeito que o nome dele prevê. Sem isso o conceito é
  rótulo. É o mesmo espírito dos quatro marcos da memória no N6 (registrado, codificado, recuperado, causal).
- **Completude:** quanto da decisão se prevê a partir de `C_t` contra a partir de `z_t` inteiro. A diferença é o que os conceitos não cobrem.
- **Vazamento:** conceito que carrega informação além do nome (Mahinpei et al. 2021). Controle: decodificador sobre estados embaralhados.
- **Calibração da incerteza:** conceito declarado incerto erra mais que conceito declarado certo.
- **Fala fiel aos conceitos:** um juiz confere se o texto só afirma conceitos acima do limiar e não acrescenta estado. A LLM sozinha produz
  explicação plausível e infiel (Turpin et al. 2023).
- **Humanos (fase 2):** o jogador entende melhor o pet com a fala por conceitos do que com a fala de hoje (Anderson et al. 2019, VERIFICADA).

## 5. Literatura

Status pelo vocabulário da skill `literatura-digilab`. As marcadas **pista** tiveram título, autores e ano conferidos na API do arXiv em
2026-10-04 (e o resumo, nas duas mais próximas), mas **não estão na tabela verificada** do projeto: ler antes de citar.

| referência | id | status | o que sustenta |
|---|---|---|---|
| Koh et al. 2020, *Concept Bottleneck Models* | arXiv:2007.04612 | VERIFICADA | predição que passa por conceitos nomeados e intervencionáveis; mede o custo do gargalo |
| Kim et al. 2023, *Probabilistic Concept Bottleneck Models* (ICML) | arXiv:2306.01574 | pista | conceito com incerteza |
| Mahinpei et al. 2021, *Promises and Pitfalls of Black-Box Concept Learning Models* | arXiv:2106.13314 | pista | vazamento de informação pelos conceitos |
| Yuksekgonul et al. 2022, *Post-hoc Concept Bottleneck Models* | arXiv:2205.15480 | pista | gargalo de conceitos posto depois, num modelo pronto |
| Oikarinen et al. 2023, *Label-Free Concept Bottleneck Models* | arXiv:2304.06129 | pista | conceitos sem rótulo humano |
| Rao et al. 2024, *Discover-then-Name* (ECCV) | arXiv:2407.14499 | pista (resumo lido) | autoencoder esparso descobre conceitos, que depois são nomeados |
| De Santis et al. 2026, *Learning Concept Bottleneck Models from Mechanistic Explanations*, M-CBM (ICLR 2026) | arXiv:2603.07343 | pista (resumo lido) | gargalo montado com os conceitos que o próprio modelo aprendeu, extraídos por autoencoder esparso e nomeados por LLM multimodal; métrica de esparsidade por decisão (NCC) |
| Cunningham et al. 2023, *Sparse Autoencoders Find Highly Interpretable Features in Language Models* | arXiv:2309.08600 | pista | autoencoder esparso acha direções interpretáveis |
| Hernandez et al. 2022, *Natural Language Descriptions of Deep Visual Features* (MILAN) | arXiv:2201.11114 | pista | descrever em linguagem o que um neurônio representa |
| Bereska e Gavves 2024, *Mechanistic Interpretability for AI Safety — A Review* | arXiv:2404.14082 | pista | revisão da interpretabilidade mecanicista |
| Turpin et al. 2023, *Language Models Don't Always Say What They Think* | arXiv:2305.04388 | pista | explicação de LLM pode ser plausível e infiel |
| Anderson et al. 2019; Madumal et al. 2020 | `10.24963/ijcai.2019/184`; `10.1609/aaai.v34i03.5631` | VERIFICADA | medir compreensão de leigos; explicação ancorada em modelo causal |

**Limite de alegação.** "Descobrir conceitos internos e depois nomeá-los com uma LLM" já está publicado (Discover-then-Name 2024, M-CBM
2026), em classificação de imagem. Nada aqui pode ser dito como novo. O que talvez seja contribuição, e só depois de uma busca própria que
permita dizer "não localizamos": aplicar isso a um agente que aprende durante a vida, com teste causal contra as decisões dele e com a fala
obrigada a respeitar a incerteza de cada conceito.

## 6. Riscos

- **Cérebro pequeno demais.** Com menos de mil pesos e entradas já nomeadas, os conceitos descobertos podem só redescobrir as entradas. Seria
  um resultado, mas pobre. A ideia rende mais com o cérebro B ou com mundo mais rico (frutas, bola, memória).
- **Rótulo que parece causa.** "Intenção de enganar" é exatamente o tipo de conceito que impressiona e que o teste causal pode derrubar. A fala
  não afirma intenção sem esse teste.
- **Custo e determinismo.** A LLM fica fora do registro do pet, como hoje: o texto é gravado como saída, nunca realimenta a decisão
  (memória "LLM e modo livre gravado").
- **Paridade.** Pesquisa no Python primeiro; a web só recebe o decodificador do DigiBrain escolhido no fim da fase 1.

## 7. Onde entra

Pesquisa da fase 1, ao lado do N11 (comparação de cérebros) e como extensão do G4, depois que houver cérebro com mundo rico o bastante para
os conceitos serem diferentes das entradas. Não é da rodada atual. Próximo passo, se aprovado: uma tarefa que escolha o caminho da seção 3,
defina os testes da seção 4 com plano de análise antes da run, e peça ao Claude Science a verificação das pistas da seção 5.
