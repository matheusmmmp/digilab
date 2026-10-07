# Automodelo: o que a neurociência oferece

**NENHUMA ARQUITETURA ESCOLHIDA.** Este arquivo junta ideias da neurociência que podem orientar a rede de si e o ego do pet
(`docs/futuro/ego_existencia.md`), liga cada uma a uma peça do DigiBrain e registra hipóteses. Pedido do Matheus, 2026-10-07. Não
autoriza mecânica: tudo aqui entra com tarefa e plano de análise, como o resto da pasta.

**Neurociência como inspiração, não como fidelidade.** Nenhuma peça do DigiBrain afirma reproduzir um circuito do cérebro, e os
nomes daqui (modelo direto, interocepção, esquema de atenção) descrevem papéis no nosso cérebro, não estruturas biológicas. Vale a
regra 3 da pasta (canal artificial não é neurotransmissor) e a regra 4 (vocabulário operacional: nada afirma que o pet sente).

## Nas fontes

Todas as referências desta seção são **pistas**: os metadados (autores, ano, título, veículo) foram conferidos no Crossref em
2026-10-07, mas **nenhum texto foi lido** e nenhuma está na tabela verificada. As descrições abaixo são **INTERPRETAÇÃO** a partir do
título e do conhecimento geral da área; ler antes de citar qualquer uma em texto de resultado. A exceção é Keramati e Gutkin 2014,
VERIFICADA.

| ideia | fontes | o que a ideia diz (INTERPRETAÇÃO) |
|---|---|---|
| **modelo direto e cópia eferente** | Wolpert, Ghahramani e Jordan 1995; Blakemore, Wolpert e Frith 1998 | o cérebro usa uma cópia do comando motor para prever a consequência sensorial da própria ação; o previsto é descontado do sentido, e por isso não sentimos cócegas em nós mesmos |
| **senso de agência** | Haggard 2017 | a sensação de ser o autor de uma ação depende de a consequência casar com o previsto |
| **interocepção** | Craig 2002 | há uma representação do estado fisiológico do próprio corpo, separada dos sentidos voltados ao mundo |
| **inferência interoceptiva** | Seth 2013; Barrett e Simmons 2015 | o cérebro prevê o estado do corpo; o erro dessas previsões compõe a emoção e o senso de si corporificado; prever necessidades antes que apareçam é a alostase |
| **sentimentos e homeostase** | Damasio e Carvalho 2013 | sentimentos são a expressão mental de estados homeostáticos, com origem evolutiva antiga |
| **reforço homeostático** | Keramati e Gutkin 2014 (VERIFICADA) | a redução do desvio homeostático funciona como recompensa |
| **eu mínimo e eu narrativo** | Gallagher 2000 | distinção entre o senso imediato de agência e posse do corpo e o eu que se estende no tempo pela história contada |
| **esquema de atenção** | Graziano e Webb 2015 | o cérebro mantém um modelo simplificado da própria atenção, e o relato de consciência subjetiva viria desse modelo |
| **planejar contra hábito** | Daw, Niv e Dayan 2005 | dois sistemas de controle, um que planeja com um modelo do mundo e um de hábito, arbitrados pela incerteza de cada um |
| **mapa cognitivo** | Behrens et al. 2018 | as mesmas estruturas que mapeiam o espaço organizam conhecimento abstrato para comportamento flexível |
| **comportamento de doença** | Hart 1988; Dantzer et al. 2008 | o letargo, a falta de apetite e o isolamento do animal doente são uma estratégia do organismo, comandada pelo sistema imune através do cérebro |
| **energia livre** | Friston 2010 | uma proposta unificadora em que percepção, ação e aprendizado reduzem erro de previsão |

## No DigiLab hoje (REPOSITÓRIO)

- **Corpo químico:** existe. `digilab/corpo.py` guarda os drives como químicos em inteiros, com receptores na escala S, digestão e
  Vida; `digilab/motor_corpo.py` põe o corpo por baixo dos drives do `Estado`, com a percepção em `Observacao.corpo` e o gancho
  `consequencia_corpo`. É o substrato da interocepção.
- **Reforço homeostático:** existe. O sinal da consequência do P1 é a redução do déficit (`lobos.sinal_homeostatico`, e
  `lobos.sinal_corpo` sobre os receptores), com canais por drive e o peso pela janela (A2.4).
- **Emoção:** na v1 é uma tabela de categoria × temperamento (`digilab/emocao.py`), só leitura; na V2 não há emoção derivada do corpo.
- **Rede de si:** **não existe.** Está PROPOSTA no `docs/futuro/ego_existencia.md`, seção 3: uma cabeça do corpo (modelo direto) e uma
  cabeça de autoria, aprendidas por erro de previsão, com o motor e as sondas como gabarito.
- **Legibilidade:** a sonda do aprendido de cada cérebro dá o contrafactual "sem o aprendido, o que teria feito"; é o gabarito que a
  cabeça de autoria tentaria estimar sem acesso direto.
- **Planejador:** não existe. Todos os cérebros (A, B, C) são de hábito no sentido de Daw, Niv e Dayan: escolhem pelo que foi
  reforçado, sem simular o futuro.
- **Mapa:** o mundo físico tem posições e um mapa (`digilab/mundo.py`), mas o pet só vê o que está perto e sente o cheiro; não
  guarda um mapa próprio.

## Ideias → peças do DigiBrain (INTERPRETAÇÃO)

| ideia | peça | o que muda em relação ao que está proposto |
|---|---|---|
| modelo direto e cópia eferente | **cabeça do corpo** da rede de si | a entrada inclui a ação escolhida (a cópia eferente), e a saída é o que os receptores vão mostrar depois; o ego já propõe isso |
| senso de agência | **cabeça de autoria** | a autoria pode sair da comparação entre o previsto para a própria ação e o observado, em vez de uma cabeça separada: o que casou com o previsto "fui eu"; o que não casou veio do mundo ou do dono |
| interocepção e inferência interoceptiva | **receptores do corpo** e o erro da cabeça do corpo | o erro de previsão do corpo vira um sinal próprio, separado do reforço: "algo mudou em mim" |
| alostase | **decisão** | a previsão do corpo entra na decisão (etapa 3 do ego): o pet antecipa a fome em vez de só reagir a ela |
| sentimentos como leitura da homeostase | **emoção** | a emoção sairia do estado do corpo e do erro de previsão dele, e não de uma tabela; uma mesma química daria o reforço e o sentimento |
| eu mínimo e eu narrativo | **ordem das etapas do ego** | o eu mínimo (corpo e autoria, a rede de si) vem antes; o narrativo (memória de episódios e voz própria) se apoia nele; as perguntas existenciais são do narrativo e só têm lastro com o mínimo pronto |
| esquema de atenção | **decodificador de conceitos** (`docs/futuro/decodificador_conceitos.md`) | um modelo simples de "no que estou prestando atenção" (que entrada pesou na decisão) que o pet pode relatar |
| planejar contra hábito | **o pet que pensa** (pedido do Matheus de 2026-10-07: o pet planejando consequências) | os cérebros de hoje ficam como o hábito; um planejador que usa o modelo direto simula ações antes de escolher; um árbitro pela incerteza de cada um decide quem manda |
| mapa cognitivo | **mundo físico** | o pet guardaria um mapa próprio de onde achou comida, separado do mapa do motor, e o planejador o usaria |
| comportamento de doença | **doença de órgão** (`docs/futuro/doenca_remedio.md`) | a doença mexe também nos impulsos (cansaço, apetite), o que dá ao pet uma pista interna de que está doente, além do sentido mais fraco |
| energia livre | moldura | serve para pensar o conjunto como redução de erro de previsão; como mecanismo é difícil de testar e não entra como peça |

## Uma arquitetura de referência (HIPÓTESE DIGILAB)

```
                 percepção do mundo (visão, cheiro)        receptores do corpo (interocepção)
                                 │                                      │
                                 ▼                                      ▼
   ┌──────────────── rede de si (aprende por erro de previsão) ─────────────────┐
   │  cabeça do corpo: dado o estado e a AÇÃO escolhida (cópia eferente),       │
   │  prevê os receptores depois                                                 │
   │  comparador: previsto × observado → erro do corpo  → "algo mudou em mim"    │
   │                                     → autoria      → "fui eu" / "não fui"   │
   └────────────────────────────────────────────────────────────────────────────┘
            │ previsão do corpo (alostase)            │ erro e autoria
            ▼                                         ▼
   ┌──── decisão ────┐                        emoção e eu mínimo
   │ hábito (A/B/C)  │◄── árbitro pela ──┐            │
   │ planejador      │    incerteza      │            ▼
   └─────────────────┘                   │     memória de episódios + voz → eu narrativo
            │                            │            (as perguntas existenciais)
            ▼                            │
          ação ──────── cópia eferente ──┘
```

O que está fora da caixa já existe ou está registrado em outro documento; a rede de si, o comparador, a emoção pelo corpo, o
planejador e o árbitro são o que esta pasta propõe estudar.

## Hipóteses

| ID | pergunta | teste mínimo | depende de |
|---|---|---|---|
| H-SELF-01 | uma rede pequena, em inteiros, aprende a prever os receptores do corpo depois da própria ação e se readapta depois de uma mudança do corpo (estágio, dano de órgão) | erro de previsão contra a rede congelada, a ausente e o oráculo do motor; quantas experiências até o erro voltar ao nível de antes | etapa 2 do ego; corpo com órgãos |
| H-SELF-02 | a autoria estimada pela comparação previsto × observado separa o que o pet causou do que o tempo, o mundo ou o dono causaram | acurácia contra o registro do motor, que sabe quem mudou cada drive; comparar com uma cabeça de autoria separada | H-SELF-01 |
| H-SELF-03 | a previsão do corpo como entrada da decisão (alostase) reduz a privação em relação ao mesmo cérebro sem ela | privação e desempenho contra a rede ausente e a congelada, na bancada, por condição | H-SELF-01; etapa 3 do ego |
| H-SELF-04 | uma emoção derivada do corpo e do erro de previsão é mais coerente com os eventos da vida do que a tabela da v1 | coerência da emoção com o evento que a causou, medida no registro; legibilidade da fala | H-SELF-01; decodificador |
| H-SELF-05 | um planejador sobre o modelo direto, arbitrado pela incerteza, vence o hábito quando o mundo muda (o mutável) e perde para ele quando o mundo é estável | desempenho por condição (casado, descasado, mutável) contra o hábito sozinho e o planejador sozinho | H-SELF-01; o pet que pensa |
| H-SELF-06 | a doença que mexe também nos impulsos encurta o tempo até o pet perceber que algo mudou | tempo até a mudança de comportamento e até o erro da rede de si passar do limiar, com e sem o efeito nos impulsos | H-SELF-01; doença de órgão |

Todas são **IDEIA**: nenhuma tem tarefa, plano nem versão de pet.

## Confundidores e riscos

- **Fidelidade biológica.** Nenhum resultado aqui diz algo sobre cérebros. "Inspirado em" fala do nosso cérebro.
- **Energia livre não falsificável.** Usar como moldura, nunca como hipótese testada.
- **Antropomorfismo.** "Sente", "percebe", "é o autor" só com critério operacional definido antes e medido contra o motor; o motor e
  o log usam nomes de variáveis.
- **Gabarito escondido.** A rede de si não pode ler o estado do motor nem a sonda; só os receptores e as próprias ações. Senão a
  autoria vira leitura, não estimativa.
- **Determinismo e porte.** A rede de si em inteiros, sem função transcendental, como o cérebro A (decisão E-8 do ego), para o replay
  bit a bit e a web.
- **Escopo.** Rede de si, emoção pelo corpo, planejador e árbitro são quatro peças grandes. Uma por vez, cada uma com o próprio gate,
  na ordem das etapas do ego.

## Literatura

| referência | id | status | o que pode sustentar |
|---|---|---|---|
| Wolpert, Ghahramani e Jordan 1995, *Science* | `10.1126/science.7569931` | pista | modelo interno que prevê o resultado do movimento |
| Blakemore, Wolpert e Frith 1998, *Nature Neuroscience* | `10.1038/2870` | pista | cancelamento central da sensação produzida pela própria ação |
| Haggard 2017, *Nature Reviews Neuroscience* | `10.1038/nrn.2017.14` | pista | senso de agência |
| Craig 2002, *Nature Reviews Neuroscience* | `10.1038/nrn894` | pista | interocepção |
| Seth 2013, *Trends in Cognitive Sciences* | `10.1016/j.tics.2013.09.007` | pista | inferência interoceptiva, emoção e o eu corporificado |
| Barrett e Simmons 2015, *Nature Reviews Neuroscience* | `10.1038/nrn3950` | pista | previsões interoceptivas no cérebro |
| Damasio e Carvalho 2013, *Nature Reviews Neuroscience* | `10.1038/nrn3403` | pista | sentimentos e suas origens evolutivas e neurobiológicas |
| Keramati e Gutkin 2014, *eLife* | `10.7554/elife.04811` | VERIFICADA | RL homeostático |
| Gallagher 2000, *Trends in Cognitive Sciences* | `10.1016/s1364-6613(99)01417-5` | pista | eu mínimo e eu narrativo |
| Graziano e Webb 2015, *Frontiers in Psychology* | `10.3389/fpsyg.2015.00500` | pista | teoria do esquema de atenção |
| Daw, Niv e Dayan 2005, *Nature Neuroscience* | `10.1038/nn1560` | pista | competição entre controle por modelo e por hábito, pela incerteza |
| Behrens et al. 2018, *Neuron* | `10.1016/j.neuron.2018.10.002` | pista | mapa cognitivo para comportamento flexível |
| Hart 1988, *Neuroscience & Biobehavioral Reviews* | `10.1016/s0149-7634(88)80004-6` | pista | base biológica do comportamento do animal doente |
| Dantzer et al. 2008, *Nature Reviews Neuroscience* | `10.1038/nrn2297` | pista | da inflamação ao comportamento de doença |
| Friston 2010, *Nature Reviews Neuroscience* | `10.1038/nrn2787` | pista | princípio da energia livre |

As referências de automodelo em robôs e agentes (Bongard et al. 2006, Kwiatkowski e Lipson 2019, Chen et al. 2022, Metzinger 2007)
ficam na seção 10 do `docs/futuro/ego_existencia.md`.

**Limite de alegação.** Modelos diretos, inferência interoceptiva, arbitragem modelo × hábito e automodelos aprendidos já estão
publicados, em neurociência e em robótica. Nada aqui pode ser dito como novo. O que talvez seja contribuição, só depois de busca
própria: um pet que aprende, durante a vida e em inteiros, um modelo do próprio corpo e da própria autoria, com as estimativas
calibradas contra a verdade do motor.
