# I — Revisão: pet que age pelo estado interno (modulação, crédito, planejamento curto, seleção)

Data: 2026-11-07. Pergunta: que referências ajudam a atacar as falhas medidas do cérebro modular
(1) busca distante, (2) hábito que piora, (3) crédito com atraso, (4) troca de meta demais,
(5) memória de lugar sem achado — e a deixar o pet mais vivo (estado interno, repertório,
química que modula, planejamento curto).

## Método e limites

- Seis buscas paralelas, uma por grupo de eixos (1–2, 3, 4, 5–6, 7–8, 9). Só entrou o que foi aberto.
- Coluna `lido`: **completo** = texto completo (ou a maior parte, indicada); **resumo** = resumo/abstract
  (PubMed, Crossref, arXiv); **metadados** = só o registro bibliográfico. Item com `metadados` não
  sustenta afirmação de conteúdo.
- DOIs conferidos no Crossref ou no PubMed pelas buscas. Oito DOIs críticos foram reconferidos no
  Crossref na consolidação: 10.1145/267658.267663, 10.1037/rev0000120, 10.1371/journal.pcbi.1000437,
  10.1016/j.neuron.2019.07.028, 10.1038/ncomms1455, 10.1016/j.cell.2013.08.001,
  10.1016/j.neunet.2005.06.049, 10.1145/566570.566597. Todos resolveram, com título e ano corretos.
- Correções de citação feitas pelas buscas:
  - Creatures (AGENTS '97) é **10.1145/267658.267663**. O 10.1145/267658.267727 dá 404.
  - Miller, Shenhav & Ludvig 2019 é **10.1037/rev0000120**. O 10.1037/rev0000117 é de outro artigo.
  - Zhang, Berridge et al. 2009 saiu na **PLoS Comput Biol**, não na PNAS.
- Coluna `evid.`: **C** = experimento ou comparação com controle; **S** = simulação ou teoria
  comparada com dados publicados; **D** = desenho, relato ou teoria sem teste.
- Muitos sites de editora devolveram 403 ou login. Vários itens ficaram em `resumo` por isso, não por
  escolha.
- **Não abertos (ficaram fora):**
  - Eixos 1–2: Krichmar 2008 (só metadados), GasNets, Lones (hormônio artificial).
  - Eixo 3: Sutton & Barto cap. 12, Dayan 1993, Stachenfeld 2017, Dickinson 1985, Dezfouli & Balleine.
  - Eixo 4: Pritzel NEC, Banino 2018, TEM, RatSLAM, Louis 2008, Gershow 2012.
  - Eixos 5–6: Mark & Dill GDC 2010, IAUS 2015, Spier & McFarland, Kaplan 2000, Arkin/Fujita 2003.
  - Eixos 7–8: Framsticks, Yaeger 2008, ALIEN, Wilson/Meyer/Beer 1990 (animats), Grand 2000 (livro).
  - Eixo 9: Hopkins "Soul of The Sims", capítulo de Tarn Adams, Evans em AI Game Programming Wisdom,
    GDC de Rain World 2016, Spore, Nintendogs, Tamagotchi, Petz.

---

## Eixo 1 — Neuromodulação e hormônios

| referencia | tipo | lido | o_que_mostra | evid. | falha_ou_eixo | como_caberia | doi_ou_id |
|---|---|---|---|---|---|---|---|
| Doya, K. (2002). Metalearning and neuromodulation. *Neural Networks* 15(4–6):495–506 | artigo revisado (teoria) | resumo | Divide os papéis assim: DA = erro de previsão da recompensa, 5-HT = horizonte de desconto, NA = temperatura da escolha, ACh = taxa de atualização da memória. | D | 2, 3, 4 | Quatro inteiros globais dirigidos pelos químicos do corpo. NA (susto/dor) dá o expoente ou divisor do sorteio. 5-HT dá a meia-vida do traço (shift). ACh dá a taxa do hábito. São ganhos sobre o que já existe. | 10.1016/S0893-6080(02)00044-8 |
| Daw, N. D., Kakade, S., Dayan, P. (2002). Opponent interactions between serotonin and dopamine. *Neural Networks* 15(4–6):603–616 | artigo revisado (teoria) | resumo | A 5-HT tônica reportaria a taxa média de recompensa e a DA, a de punição. O sinal de aprendizado é medido contra essa linha de base. | D | 2, 3 | EMA inteira do alívio como linha de base. O hábito só reforça quando o alívio fica acima da média. | 10.1016/S0893-6080(02)00052-7 |
| Krichmar, J. L. (2013). A neurorobotic platform to test the influence of neuromodulatory signaling on anxious and curious behavior. *Front. Neurorobot.* 7:1 | artigo revisado (robô) | completo (~80 %) | Rede de taxa pequena, pesos à mão. DA, 5-HT e ACh/NA vêm de eventos. O neurônio mais ativo escolhe 1 de 4 comportamentos e só troca acima do limiar 0,67. Com 5-HT longa o robô fica "ansioso". A lesão OFC→DA faz perseverar em ~50 % dos ensaios. | C (fraco: braços intacto/τ/lesão, 5 sementes, sem estatística) | 4, 1, eixo 1 | Quase direto: limiar de troca (histerese), químicos tônicos com τ por shift e porta de novidade por depressão sináptica inteira. | 10.3389/fnbot.2013.00001 |
| Zhang, J., Berridge, K. C., Tindell, A. J., Smith, K. S., Aldridge, J. W. (2009). A neural computational model of incentive salience. *PLoS Comput Biol* 5(7):e1000437 | artigo revisado (modelo + ratos) | completo (~65 %) | O "querer" = V + log κ, com κ do estado fisiológico. Uma deixa antes ligada a sal aversivo passou a disparar o pálido ventral na primeira vez com fome de sal, **sem reaprender**. As deixas de sacarose e de controle não mudaram. | C | 1, 5, 2 | Valor efetivo = V_classe + κ[necessidade], com κ tabelado. A fome revaloriza no ato a comida e o lugar lembrados. | 10.1371/journal.pcbi.1000437 |
| Root, C. M., Ko, K. I., Jafari, A., Wang, J. W. (2011). Presynaptic facilitation by neuropeptide signaling mediates odor-driven food search. *Cell* 145(1):133–144 | artigo revisado (Drosophila) | resumo | A fome aumenta, via sNPF, o ganho pré-sináptico de neurônios olfativos específicos; a insulina reprime. Esse ramo é necessário para a busca faminta. Facilitá-lo numa mosca alimentada basta para imitar a busca. | C (necessidade e suficiência genéticas) | 1, eixo 1 | O ganho do canal de cheiro de comida vira `cheiro*(64+fome)>>6`, freado pela saciedade. A fome muda o que o pet **percebe**. | 10.1016/j.cell.2011.02.008 |
| Sayin, S. et al. (2019). A neural circuit arbitrates between persistence and withdrawal in hungry Drosophila. *Neuron* 104(3):544–558 | artigo revisado (Drosophila) | resumo | Moscas famintas persistem no rastreio do odor mesmo sem recompensa. A persistência depende de DA e Dop1R2 em dois MBONs. Um neurônio octopaminérgico ligado ao comer (VPM4) freia o rastreio. | C | 1, 4 | Persistência inteira = f(fome) somada à busca em curso; ela sobe o limiar que o sono precisa vencer. Comer zera. | 10.1016/j.neuron.2019.07.028 |
| Avila-García, O., Cañamero, L. (2005). Hormonal modulation of perception in motivation-based action selection architectures. AISB'05, "Agents that Want and Like" | anais de simpósio | resumo | Modela hormônios como mecanismo de 2ª ordem que modula a percepção no produto drive × estímulo; testado em robôs. O resumo não traz números. | D (controle não visto) | 1, 4 | Multiplicador hormonal inteiro sobre a parcela do estímulo da soma ponderada. Detalhes não verificados. | uhra.herts.ac.uk/handle/2299/9886 |

## Eixo 2 — Interocepção e alostase

| referencia | tipo | lido | o_que_mostra | evid. | falha_ou_eixo | como_caberia | doi_ou_id |
|---|---|---|---|---|---|---|---|
| Keramati, M., Gutkin, B. (2014). Homeostatic reinforcement learning for integrating reward collection and physiological stability. *eLife* 3:e04811 | artigo revisado (teoria + simulação) | completo (~60 %) | Recompensa = D(H_t) − D(H_t+K), com drive D convexo. Prova que maximizar a recompensa descontada equivale a minimizar o desvio homeostático. A deixa oral estima K antes da digestão. Reproduz a tolerância antecipatória e a aversão à variância. | S | 2, 3, 4 | Terceiro fator do hebbiano = queda do drive convexo inteiro (Σ falta² >> s) no lugar do alívio bruto. Comer saciado dá ~0. O gosto na boca dá crédito imediato. | 10.7554/eLife.04811 |
| Sterling, P. (2012). Allostasis: a model of predictive regulation. *Physiol. Behav.* 106(1):5–15 | artigo revisado (revisão) | resumo | A regulação eficiente antecipa. O "bastão" (ansiedade que não adapta) empurra e a "cenoura" (prazer breve, adapta rápido) solta. | D | 1, 4 | Sinal de necessidade que **não** habitua (mantém a meta) + bônus pós-consumo que decai rápido (libera a próxima vontade). | 10.1016/j.physbeh.2011.06.004 |
| Barrett, L. F., Simmons, W. K. (2015). Interoceptive predictions in the brain. *Nat Rev Neurosci* 16(7):419–429 | artigo revisado (opinião) | resumo | Modelo EPIC: o córtex visceromotor prevê o estado do corpo, e as sensações viscerais corrigem. | D | eixo 2 | "Esperado" inteiro (EMA) por químico de falta; o cérebro lê o erro lido − esperado. É uma leitura barata dos órgãos, sem resultado medido. | 10.1038/nrn3950 |
| Buckley, C. L., Kim, C. S., McGregor, S., Seth, A. K. (2017). The free energy principle for action and perception: a mathematical review. *J Math Psychol* 81:55–79 | artigo revisado (tutorial) | resumo | Expõe a inferência ativa por codificação preditiva com gradiente e deixa as suposições explícitas. | D | eixo 2 | A forma completa pede ponto flutuante e precisões. Só "erro × precisão → reflexo" cabe em inteiros. | 10.1016/j.jmp.2017.09.004 |
| Tschantz, A., Barca, L., Maisto, D., Buckley, C. L., Seth, A. K., Pezzulo, G. (2022). Simulating homeostatic, allostatic and goal-directed forms of interoceptive control using active inference. *Biol. Psychol.* 169:108266 | artigo revisado (simulação) | completo (preprint, ~80 %) | Quatro simulações ilustrativas: uma deixa baixa o ponto ideal e antecipa a resposta; precisão interoceptiva baixa faz o controle falhar; um nível discreto com 2 políticas × 20 passos escolhe pela divergência prevista. | D (ilustrativo, sem estatística) | 3, 1, eixo 2 | Deixa (hora do relógio, cheiro) desloca o ponto ideal inteiro e manda ao comedouro antes da fome. Rollout de 2 opções × N passos sobre o corpo simulado. | 10.1016/j.biopsycho.2022.108266 |
| Morville, T., Friston, K., Burdakov, D., Siebner, H. R., Hulme, O. J. (2018). The homeostatic logic of reward. bioRxiv 242974 | preprint (revisão) | resumo | Critica o drive ad hoc do RL homeostático. Aponta neurônios do arqueado que projetam para a DA como interface homeostase-recompensa. | D | eixo 2 | Terceiro fator = alívio − alívio previsto (EMA). | 10.1101/242974 |
| Yoshida, N., Daikoku, T., Nagai, Y., Kuniyoshi, Y. (2024). Emergence of integrated behaviors through direct optimization for homeostasis. *Neural Networks* 177:106379 | artigo revisado (deep RL) | resumo | Entre as recompensas homeostáticas comparadas, a **diferença do drive** foi a melhor. O comportamento passa a depender do estado interno. | C (comparação interna entre definições de recompensa) | 2, 3 | O treino de ponta a ponta não cabe. Fica o achado: usar a diferença do drive como 3º fator. | 10.1016/j.neunet.2024.106379 |

## Eixo 3 — Crédito com atraso numa vida só

| referencia | tipo | lido | o_que_mostra | evid. | falha_ou_eixo | como_caberia | doi_ou_id |
|---|---|---|---|---|---|---|---|
| Izhikevich, E. M. (2007). Solving the distal reward problem through linkage of STDP and dopamine signaling. *Cereb. Cortex* 17(10):2443–2452 | artigo revisado | resumo | A coincidência pré-pós deixa uma marca de poucos segundos. A DA que chega dentro da janela converte a marca em peso. A atividade aleatória durante a espera não atrapalha. | S | 3 | Traço inteiro e[classe][comp], ligado no ato e decaindo por shift. ΔW = (alívio × e) >> s. | 10.1093/cercor/bhl152 |
| Gerstner, W., Lehmann, M., Liakoni, V., Corneil, D., Brea, J. (2018). Eligibility traces and plasticity on behavioral time scales. *Front. Neural Circuits* 12:53 | revisão revisada | completo (~50 %) | Constantes medidas do traço: ~1 s no estriado, 3–10 s no córtex, ~1 min no hipocampo com DA, tagging ~1 h. O **sinal** do 3º fator decide potenciar ou deprimir. | revisão de C | 3, 2 | Duas meias-vidas: curta para o ato, longa para hábito e lugar. Alívio negativo enfraquece, o que corta "reforça ganhe ou não". | 10.3389/fncir.2018.00053 |
| Yagishita, S. et al. (2014). A critical time window for dopamine actions on the structural plasticity of dendritic spines. *Science* 345(6204):1616–1620 | artigo revisado | completo (PMC) | No estriado, a DA só aumenta a espinha se chegar 0,3–2 s **depois** do glutamato. Antes ou 5 s depois, pouco efeito. | C (antagonistas, PKI, papaverina) | 3 | Janela assimétrica justificada. Segundos não cobrem minutos: o traço sináptico sozinho não resolve a (3) e precisa de ponte (opção, buffer). | 10.1126/science.1255514 |
| Shindou, T., Shindou, M., Watanabe, S., Wickens, J. (2019). A silent eligibility trace enables dopamine-dependent synaptic plasticity for reinforcement learning in the mouse striatum. *Eur J Neurosci* 49(5):726–736 | artigo revisado | resumo | Em neurônios D1, DA 2 s após a atividade potencia; o traço é "silencioso", sem mexer no peso até chegar a DA. | C | 3 | Traço num vetor separado dos pesos; só o alívio o converte. | 10.1111/ejn.13921 |
| Bittner, K. C. et al. (2017). Behavioral time scale synaptic plasticity underlies CA1 place fields. *Science* 357(6355):1033–1036 | artigo revisado | resumo | Um único platô potencia entradas de segundos antes ou depois e cria um campo de lugar numa passagem. | C | 5, 3 | Ao comer, reforçar as células de lugar dos últimos N tiques (buffer circular inteiro, peso por distância temporal). | 10.1126/science.aan3846 |
| Miller, K. J., Shenhav, A., Ludvig, E. A. (2019). Habits without values. *Psychol. Rev.* 126(2):292–311 | artigo revisado | completo (~55 %) | O hábito é força **sem valor** (H ← H + α(a − H)). Um árbitro mistura w·H + (1−w)·Q, e w cai quando a contingência ação→desfecho é alta. Reproduz a insensibilidade à desvalorização, a degradação de contingência e a perseveração. | S | **2** | Explica a (2): o hábito atual é o hábito deles sem o árbitro. w inteiro = clamp(w0 − k·contingência + …), α_H por shift. | 10.1037/rev0000120 |
| Daw, N. D., Niv, Y., Dayan, P. (2005). Uncertainty-based competition between prefrontal and dorsolateral striatal systems for behavioral control. *Nat Neurosci* 8(12):1704–1711 | artigo revisado | resumo | Dois controladores (modelo e hábito); manda o de menor incerteza. Explica quando o hábito domina. | S | 2, 4 | Erro de previsão médio (shift) por controlador; manda o de menor erro. | 10.1038/nn1560 |
| Momennejad, I. et al. (2017). The successor representation in human reinforcement learning. *Nat Hum Behav* 1(9):680–692 | artigo revisado | resumo | Humanos se ajustam rápido quando muda a recompensa e mal quando muda a transição, como prevê a representação de sucessores. | C (humanos, revalorização de recompensa vs de transição) | 3, 5 | Matriz pequena M[classe][classe_futura] em inteiros, com TD por shift. "Pedir comida" herda o valor de "comida" futura. | 10.1038/s41562-017-0180-8 |
| Sutton, R. S., Precup, D., Singh, S. (1999). Between MDPs and semi-MDPs: a framework for temporal abstraction in RL. *Artif. Intell.* 112(1–2):181–211 | artigo revisado | metadados | Resultado não lido. É o enquadramento de "opções" (política + término). | — | 3, 4 | "Buscar comida" vira opção que só termina ao comer, saciar ou estourar o tempo; o crédito vai à opção inteira. | 10.1016/S0004-3702(99)00052-1 |

## Eixo 4 — Planejamento curto e barato

| referencia | tipo | lido | o_que_mostra | evid. | falha_ou_eixo | como_caberia | doi_ou_id |
|---|---|---|---|---|---|---|---|
| Pierce-Shimomura, J. T., Morse, T. M., Lockery, S. R. (1999). The fundamental role of pirouettes in *C. elegans* chemotaxis. *J Neurosci* 19(21):9557–9569 | artigo revisado | resumo | A pirueta é disparada por dC/dt < 0 (cheiro caindo no tempo), não pela concentração. Um modelo que só usa essa regra basta para a quimiotaxia. | C (rastreio) + S | **1** | `d = C_t − C_{t−1}`; se d < −L, girar; se d > 0, seguir reto. Dois inteiros, sem ler direção. | 10.1523/JNEUROSCI.19-21-09557.1999 |
| Iino, Y., Yoshida, K. (2009). Parallel use of two behavioral mechanisms for chemotaxis in *C. elegans*. *J Neurosci* 29(17):5370–5380 | artigo revisado | resumo | Além da pirueta, o "cata-vento" curva aos poucos para o lado mais concentrado. A eficiência só aparece com os dois juntos. A ablação de ASE e AIZ elimina ambos. | C (ablação) + S | 1 | Viés lateral inteiro ∝ C_esq − C_dir somado à direção, junto com a regra de dC/dt. | 10.1523/JNEUROSCI.3633-08.2009 |
| Gomez-Marin, A., Stephens, G. J., Louis, M. (2011). Active sampling and decision making in *Drosophila* chemotaxis. *Nat Commun* 2:441 | artigo revisado | completo (PMC) | Larva: 81,6 % dos giros começam apontando gradiente abaixo, e 73,9 % reorientam para cima. A queda acumulada decide **quando** girar; varreduras da cabeça decidem **para onde**. Com olfato de um lado só, navega pior. | C (genético) | 1, 4 | Máquina de 3 estados: CORRER (acumula queda até −L), VARRER (cheira esquerda e direita em 1–3 tiques), GIRAR para o maior. | 10.1038/ncomms1455 |
| Izquierdo, E. J., Lockery, S. R. (2010). Evolution and analysis of minimal neural circuits for klinotaxis in *C. elegans*. *J Neurosci* 30(39):12908–12917 | artigo revisado | resumo | Um par sensorial ON/OFF + um par motor do pescoço basta para a klinotaxia (77 redes evoluídas analisadas) e reproduz observações não ajustadas. | S | 1 | ON = max(d,0) e OFF = max(−d,0), escritos à mão. Cabe em 4 neurônios inteiros. | 10.1523/JNEUROSCI.2606-10.2010 |
| Mattar, M. G., Daw, N. D. (2018). Prioritized memory access explains planning and hippocampal replay. *Nat Neurosci* 21(11):1609–1617 | artigo revisado | resumo | Replay priorizado por ganho × necessidade explica vários padrões de replay das células de lugar e une planejamento e consolidação. | S | 5, 3 | Dyna com orçamento fixo: após um desfecho grande, N=3 atualizações retroativas ordenadas por \|erro\| × visitas, com desempate fixo. Pode rodar no sono. | 10.1038/s41593-018-0232-z |
| Blundell, C. et al. (2016). Model-free episodic control. arXiv:1606.04460 | preprint | completo | Tabela do **maior** retorno por (estado, ação) + vizinhos. Aprende muito mais rápido no início que DQN e A3C; depois é alcançada. Os autores admitem otimismo em ambiente estocástico. | C (vs. linhas de base, sem estatística entre sementes) | 5, 3 | `melhor[célula][classe]` inteiro com máximo amortecido (`max(v·7/8, R)`). "Explorar" é puxado para a melhor célula. | 10.48550/arXiv.1606.04460 |
| Lengyel, M., Dayan, P. (2007). Hippocampal contributions to control: the third way. NIPS 20:889–896 | artigo de conferência | resumo | O controle episódico é mais útil **no começo** do aprendizado, antes do hábito; isso explicaria a passagem do hipocampo ao estriado. | S | 2, 5 | Peso do hábito = min(n/N0, 1) pela contagem de experiências da classe; o episódico domina cedo. | proceedings.neurips.cc/paper/2007/hash/1f4477bad7af3616c1f933a02bfabe4e |
| Foster, D. J., Morris, R. G., Dayan, P. (2000). A model of hippocampally dependent navigation, using the TD learning rule. *Hippocampus* 10(1):1–16 | artigo revisado | resumo | Ator-crítico sobre células de lugar aprende uma plataforma fixa, mas não uma nova por dia. Para ir direto ao lugar lembrado em uma tentativa, foi preciso um mapa de **coordenadas** independente da meta. | S | **5** | "Lembra mas não acha" pode ser valor de lugar sem vetor. Guardar (x,y) do último achado por classe e seguir `meta − posição`. | 10.1002/(SICI)1098-1063(2000)10:1<1::AID-HIPO1>3.0.CO;2-1 |
| Gershman, S. J., Daw, N. D. (2017). Reinforcement learning and episodic memory in humans and animals. *Annu Rev Psychol* 68:101–128 | revisão revisada | resumo | Defende a memória episódica para aprender com poucos dados e ligar desfechos distantes. | D | 3, 5 | Apoio teórico ao que a memória autobiográfica já faz. | 10.1146/annurev-psych-122414-033625 |

## Eixo 5 — Seleção de ação com vontades em conflito

| referencia | tipo | lido | o_que_mostra | evid. | falha_ou_eixo | como_caberia | doi_ou_id |
|---|---|---|---|---|---|---|---|
| Redgrave, P., Prescott, T. J., Gurney, K. (1999). The basal ganglia: a vertebrate solution to the selection problem? *Neuroscience* 89(4):1009–1023 | artigo revisado (teórico) | completo (preprint) | Lista os requisitos de um seletor: troca limpa, sem vazamento dos perdedores, sem oscilar. A oscilação vem da queda da saliência do vencedor à medida que a meta é cumprida. Propõe histerese por realimentação positiva. | D | **4** | Vencedor leva tudo em inteiros: +F ao vencedor, −I aos perdedores, saída só do vencedor. | 10.1016/S0306-4522(98)00319-4 |
| Prescott, T. J., Montes González, F. M., Gurney, K., Humphries, M. D., Redgrave, P. (2006). A robot model of the basal ganglia: behavior and intrinsic processing. *Neural Networks* 19(1):31–61 | artigo revisado (robô) | completo (preprint) | Modelo dos gânglios da base num robô: 84,4 % de seleções limpas e persistência em 10,1 % dos passos. Um **busy signal** somado à ação até o fim do padrão evitou abandono no meio. Com muitas opções salientes, o comportamento se desintegra. | D (medida descritiva, sem braço sem o busy) | 4, 1, eixo 6 | Busy inteiro B_k somado enquanto a ação não termina (buscar até chegar, comer ou estourar o tempo). | 10.1016/j.neunet.2005.06.049 |
| Gurney, K., Prescott, T. J., Redgrave, P. (2001). A computational model of action selection in the basal ganglia. I. *Biol Cybern* 84(6):401–410 | artigo revisado | metadados | Origem do modelo; resultado não lido. | — | 4 | Usar via Prescott 2006. | 10.1007/PL00007984 |
| Blumberg, B. M. (1996). *Old Tricks, New Dogs: Ethology and Interactive Creatures*. Tese PhD, MIT Media Lab | tese | completo (cap. 4–6) | Inibição mútua com ganho I: o ativo só perde se rival > I × ativo. Com ganho ~1,5 o hamster oscila entre comer e beber e demora a saciar; com ganho alto, sacia antes. Um "nível de interesse" cai quando a ação não progride e impede perseguir meta impossível. | D (variação de parâmetro, sem estatística) | 4, 1 | Troca se `rival*16 > ativo*G` (G=32). LoI ∈ [0,1024] cai −d por tique sem progresso. Valor = (LoI × soma) >> 10. | characters.media.mit.edu/Theses/blumberg_phd.pdf |
| Isla, D., Burke, R., Downie, M., Blumberg, B. (2001). A layered brain architecture for synthetic creatures. IJCAI-01, 1051–1057 | artigo de conferência | completo (§3.5, 3.7) | C4 (cão Duncan): cada ação tem gatilho, alvo, **DoUntil** e valor. A lista Startle (susto) compete por argmax; a Default, por sorteio. A ação ativa fica até o DoUntil e só reabre se um rival "mais que dobrou". | D | 4, 1 | Startle = dano, susto, fome crítica (argmax); Default = sorteio atual; reabrir só se rival_agora ≥ 2 × rival_na_escolha. | ijcai.org/proceedings/2001/0141.pdf |
| Bryson, J. J. (2000). Hierarchy and sequence vs. full parallelism in action selection. SAB 2000 (*From Animals to Animats 6*) | artigo de conferência | completo | No ambiente do Tyrrell, a hierarquia POSH (drives com prioridade, sequências fixas, habituação) acasalou mais que a melhor arquitetura paralela em 3 de 4 mundos (ex.: 8,17 contra 4,77 com comida escassa) e perdeu num. Usou ~10× menos nós. Prioridade alta demais a predador quebrou a coerência. | **C** (>6 600 ensaios, EP e F; compara arquiteturas inteiras) | 4, 1, eixo 6 | Drives com prioridade fixa e gatilho inteiro; contador de habituação que bloqueia a prioridade alta por n tiques; só o plano ativo concorre. | joannajbryson.org/s/hierarchy-and-sequence-vs-full-parallelism-in-action-selection.pdf |
| Graham, D. "Rez" (2013). An introduction to utility theory. In Rabin, S. (ed.), *Game AI Pro*, cap. 9. CRC Press | capítulo técnico | completo | Notas parecidas oscilam a cada quadro. Remédios: peso extra para a ação em curso, recarga que decai, decidir só quando a ação acaba (The Sims Medieval) e sortear só entre as melhores (≥ 90 %). | D (prática) | 4 | Bônus de compromisso C que decai em k tiques; sortear só ≥ 90 % do melhor. | ISBN 9781466565968; gameaipro.com/GameAIPro/GameAIPro_Chapter09_An_Introduction_to_Utility_Theory.pdf |
| Dill, K. (2015). Dual-utility reasoning. In Rabin, S. (ed.), *Game AI Pro 2*, cap. 3. CRC Press | capítulo técnico | completo | O sorteio proporcional (o do pet) às vezes pega a opção ruim. Solução: **posto** (rank) + peso — fica só o posto máximo, corta quem está muito abaixo do melhor e sorteia o resto. Usado em Zoo Tycoon 2. | D (prática) | **4** (passear tirou o pet da comida) | Posto inteiro por contexto (comida vista e fome > L dão posto 2 a comer e aproximar, passear fica em 0); sorteio só no posto máximo. | ISBN 9781482254792; gameaipro.com/GameAIPro2/GameAIPro2_Chapter03_Dual-Utility_Reasoning.pdf |
| Maes, P. (1989). How to do the right thing. *Connection Science* 1(3):291–323 | artigo revisado | resumo | Viés para o plano em curso via ativação residual; parâmetros globais trocam adaptação por "consideração". | D | 4 | Ativação residual decaindo por shift. | 10.1080/09540098908915643 (DOI não reconferido) |

## Eixo 6 — Repertório e padrões fixos de ação

| referencia | tipo | lido | o_que_mostra | evid. | falha_ou_eixo | como_caberia | doi_ou_id |
|---|---|---|---|---|---|---|---|
| Bryson 2000 (eixo 5) | artigo de conferência | completo | O repertório cresce como sequências fixas e competências aninhadas sob poucos drives (7 competências, 23 sequências), sem aumentar os candidatos no topo. | C (vs. ERP) | eixo 6, 4 | Vetor de primitivas por sequência + índice de passo. O topo segue com 7 opções e passear vira passo de explorar. | ver eixo 5 |
| Isla et al. 2001 (eixo 5): Verb Graph e camadas motoras | artigo de conferência | completo | O motor é um grafo de verbos (animações) com transições permitidas; "advérbios" interpolam o estilo. Camadas não conflitantes (cabeça, cauda) tocam juntas. | D | eixo 6 | Separar a ação escolhida (7) do gesto. O advérbio é um inteiro tirado de um químico (cansaço → andar lento). Cauda e olhos ficam fora da arbitragem. | ijcai.org/proceedings/2001/0141.pdf |
| Blumberg, B., Downie, M., Ivanov, Y., Berlin, M., Johnson, M. P., Tomlinson, B. (2002). Integrated learning for interactive synthetic characters. SIGGRAPH 2002, 417–426 | artigo de conferência | completo | Uma trajetória nova obtida por isca e recompensa entra no espaço de ações; a árvore de percepções cresce sob demanda; crédito numa janela antes do evento. Limitação admitida: não aprende sequências longas. | D (demonstração) | eixo 6, 3 | Gesto novo entra por inclusão discreta após k recompensas; cabe na lista de gestos, não na rede. | 10.1145/566570.566597 |
| Prescott et al. 2006 (eixo 5) | artigo revisado | completo | O padrão fixo "pegar o cilindro" só termina inteiro (recolher o braço) porque o busy sustenta a saliência depois de cumprida a meta. | D | eixo 6, 1 | Sequência com saliência própria até o último passo. | 10.1016/j.neunet.2005.06.049 |
| Ijspeert, A. J. (2008). Central pattern generators for locomotion control in animals and robots: a review. *Neural Networks* 21(4):642–653 | revisão revisada | resumo | CPGs dão saída rítmica coordenada a partir de sinais simples. | D | eixo 6 | Andar, mastigar e respirar como contador de fase inteiro, com amplitude e frequência vindas de 1–2 químicos. O cérebro só liga e modula. | 10.1016/j.neunet.2008.03.014 |
| Ijspeert, A. J., Crespi, A., Ryczko, D., Cabelguen, J.-M. (2007). From swimming to walking with a salamander robot driven by a spinal cord model. *Science* 315(5817):1416–1420 | artigo revisado | resumo | Só a intensidade do comando descendente muda nado ↔ marcha (previsão confirmada em dado biológico). | C (robô + dado biológico) | eixo 6 | Um escalar inteiro de "impulso" escolhe o modo do gesto por limiar. O espaço de escolha não cresce. | 10.1126/science.1138353 |
| Fujita, M. (2001). AIBO: toward the era of digital creatures. *IJRR* 20(10):781–794 | artigo revisado | resumo | Discute aumentar a complexidade de respostas para parecer vivo; arquitetura não lida. | — | eixo 6 | Sem conteúdo lido para encaixe. | 10.1177/02783640122068092 |

## Eixo 7 — Órgãos, metabolismo, ciclo de vida, química, genoma

| referencia | tipo | lido | o_que_mostra | evid. | falha_ou_eixo | como_caberia | doi_ou_id |
|---|---|---|---|---|---|---|---|
| Grand, S., Cliff, D., Malhotra, A. (1997). Creatures: artificial life autonomous software agents for home entertainment. AGENTS '97, 22–29 (relatório: Sussex CSRP434, 1996) | artigo de conferência + relatório | completo (relatório) | **Química:** bytes; emissores e receptores ligam qualquer químico a qualquer parâmetro (inclusive de neurônio). **Recompensa:** DriveReducer + Drive → Reward, então reduzir um drive ausente não recompensa. **Pesos:** "susceptibility" com meia-vida dá crédito com atraso; STW relaxa para LTW. **Vida:** genes de senescência e genes com hora de ligar. | D (os autores dizem que não há "resultados") | 2, 3; corpo modulando o cérebro | Tudo já é byte determinístico. Receptor = (químico, limiar, ganho) → parâmetro do neurônio. Recompensa = queda do químico de falta. Traço por shift. | 10.1145/267658.267663 |
| Grand, S., Cliff, D. (1998). Creatures: entertainment software agents with artificial life. *AAMAS* 1(1):39–57 | artigo revisado | metadados | Versão de periódico do mesmo sistema. | — | — | Só para citar o periódico. | 10.1023/A:1010042522104 |
| Yaeger, L. (1994). Computational genetics, physiology, metabolism, neural systems, learning, vision, and behavior or PolyWorld: life in a new context. In Langton (ed.), *Artificial Life III*, 263–298 | capítulo de anais | completo | Toda ação e a própria **atividade neural** gastam energia. Duas reservas: saúde e valor alimentar. O genoma codifica fisiologia e arquitetura neural, com hebbiano. Surgem "espécies" de estratégia. | D (observação) | metabolismo limita a ação; 4 | Custo inteiro por ação e por neurônio ativo, debitado da energia. Torna trocar de meta caro. | sem DOI; shinyverse.org/larryy/Yaeger.ALife3.pdf |
| Sims, K. (1994). Evolving virtual creatures. SIGGRAPH '94, 15–22 | artigo de conferência | completo | Um grafo genotípico codifica morfologia e neurônios locais; recursão gera segmentos repetidos com seus circuitos. | D (evolução por aptidão) | eixo genoma (codificação indireta) | Em parte: o grafo discreto com reaproveitamento serve para copiar um módulo fixo (olfato) por órgão. O cérebro evoluído não cabe. | 10.1145/192161.192167 |
| Stanley, K. O., Miikkulainen, R. (2003). A taxonomy for artificial embryogeny. *Artificial Life* 9(2):93–130 | artigo revisado | resumo | Taxonomia de codificações indiretas com reuso de genes. | D | eixo genoma | Vocabulário para descrever genoma → parâmetros. | 10.1162/106454603322221487 |
| Stanley, K. O., D'Ambrosio, D. B., Gauci, J. (2009). A hypercube-based encoding for evolving large-scale neural networks. *Artificial Life* 15(2):185–212 | artigo revisado | resumo | Uma CPPN gera pesos pela geometria (conectividade regular; redes com mais de 8 milhões de conexões). | C (pelo resumo; controle não visto) | eixo genoma | Pouco. Fica a ideia de pesos inatos como função inteira da posição (sensor esquerdo → motor direito). | 10.1162/artl.2009.15.2.15202 |
| Lenski, R. E., Ofria, C., Pennock, R. T., Adami, C. (2003). The evolutionary origin of complex features. *Nature* 423:139–144 | artigo revisado | resumo | Funções complexas só evoluem se as intermediárias também são recompensadas. | **C** | 3 (indireto: recompensas intermediárias) | Não como mecanismo. A lição de método cabe: comparar com e sem recompensa intermediária. | 10.1038/nature01568 |
| Ofria, C., Wilke, C. O. (2004). Avida: a software platform for research in computational evolutionary biology. *Artificial Life* 10(2):191–229 | artigo revisado | resumo | Plataforma de evolução digital de programas. | D | eixo 7 | Não cabe no cérebro. | 10.1162/106454604773563612 |
| Chan, B. W.-C. (2019). Lenia — biology of artificial life. *Complex Systems* 28(3):251–286 | artigo revisado | resumo | AC contínuo com mais de 400 "espécies" em 18 famílias. | D | marginal | Não cabe (campo contínuo sem órgãos). | 10.25088/ComplexSystems.28.3.251 |
| Randazzo, E., Mordvintsev, A. (2023). Biomaker CA: a biome maker project using cellular automata. arXiv:2307.09320 | preprint + código | resumo | Plantas de AC num ambiente pobre em nutrientes formam biomas estáveis e instáveis. | D | metabolismo | Não cabe (otimização em JAX). | 10.48550/arXiv.2307.09320 |

## Eixo 8 — Cérebros pequenos que parecem "pensar"

| referencia | tipo | lido | o_que_mostra | evid. | falha_ou_eixo | como_caberia | doi_ou_id |
|---|---|---|---|---|---|---|---|
| Flavell, S. W., Pokala, N., Macosko, E. Z., Albrecht, D. R., Larsch, J., Bargmann, C. I. (2013). Serotonin and the neuropeptide PDF initiate and extend opposing behavioral states in *C. elegans*. *Cell* 154(5):1023–1035 | artigo revisado | resumo | Dois neuromoduladores opostos iniciam e **prolongam** estados: 5-HT → "dwelling" (ficar), PDF → "roaming" (percorrer). A optogenética dos alvos induz estados longos. A dinâmica lenta organiza estados duradouros sobre circuitos motores rápidos. | **C** (mutantes, optogenética) | 4, 1; eixo hormônios | Dois acumuladores inteiros M_fica e M_sai, com inibição mútua e decaimento lento. Comida → M_fica; fome sem comida → M_sai. Escalam os ganhos dos 7 comportamentos e o limiar do sono. | 10.1016/j.cell.2013.08.001 |
| Gray, J. M., Hill, J. J., Bargmann, C. I. (2005). A circuit for navigation in *Caenorhabditis elegans*. *PNAS* 102(9):3184–3191 | artigo revisado | resumo | Logo após perder a comida, o verme faz **busca local** (muitas reversões e curvas); depois de ~30 min se dispersa. Neurônios identificados por ablação. | **C** (ablação) | **5**, 1 | Contador inteiro "tiques desde a última comida ou desde chegar ao lugar lembrado" controla a taxa de virada: alta no começo, caindo em degraus. | 10.1073/pnas.0409009101 |
| White, J. G., Southgate, E., Thomson, J. N., Brenner, S. (1986). The structure of the nervous system of the nematode *C. elegans*. *Phil Trans R Soc B* 314:1–340 | artigo revisado | resumo | 302 neurônios, fiação essencialmente invariante entre indivíduos. | D (anatomia) | eixo 8 | Argumento de escala: comportamento rico com fiação inata. Não dá pesos funcionais. | 10.1098/rstb.1986.0056 |
| Cook, S. J. et al. (2019). Whole-animal connectomes of both *C. elegans* sexes. *Nature* 571:63–71 | artigo revisado | resumo | Matrizes quantitativas do sensor ao efetor nos dois sexos. | D (anatomia) | eixo 8 | Idem. | 10.1038/s41586-019-1352-7 |
| Winding, M. et al. (2023). The connectome of an insect brain. *Science* 379(6636):eadd9330 | artigo revisado | resumo | Larva de Drosophila: 3 016 neurônios. Os circuitos mais recorrentes estão nas entradas e saídas do centro de aprendizado, com muita realimentação dos descendentes. | D (anatomia) | 3, 2 | Cópia eferente da ação escolhida para o módulo de valor, para o crédito saber o que foi feito. | 10.1126/science.add9330 |
| Beer, R. D. (1995). On the dynamics of small continuous-time recurrent neural networks. *Adaptive Behavior* 3(4):469–509 | artigo revisado | resumo | Analisa CTRNNs de 1–2 neurônios: já mostram biestabilidade, oscilação e caos. | D (análise) | 4 | Neurônio com autoexcitação acima do limiar = trinco que mantém a meta. Euler inteiro com τ potência de 2. | 10.1177/105971239500300405 |
| Hasani, R., Lechner, M., Amini, A., Rus, D., Grosu, R. (2021). Liquid time-constant networks. AAAI-35 (arXiv:2006.04439); Hasani, R. et al. (2022). Closed-form continuous-time neural networks. *Nat Mach Intell* 4:992–1003 | artigo de conferência + revisado | resumo | τ que depende do estado, dinâmica estável; a forma fechada (CfC) é muito mais rápida. Vencem RNNs em séries temporais. | C (comparação com redes de referência) | 4; corpo modula cérebro | Só a ideia: τ do neurônio controlado por químico (cansaço ↑ τ). O treino por gradiente não cabe. | arXiv:2006.04439; 10.1038/s42256-022-00556-7 |
| Lechner, M. et al. (2020). Neural circuit policies enabling auditable autonomy. *Nat Mach Intell* 2(10):642–652 | artigo revisado | metadados (+ imprensa) | Pela imprensa, só 19 neurônios de controle, com fiação inspirada no *C. elegans*. | — | eixo 8 | Topologia sensor → inter → comando → motor como molde para pesos à mão. | 10.1038/s42256-020-00237-3 |

## Eixo 9 — Não acadêmica (jogos, palestras, código)

Nenhuma fonte deste eixo traz comparação controlada; todas são relato ou desenho (D).

| referencia | tipo | lido | o_que_mostra | evid. | falha_ou_eixo | como_caberia | doi_ou_id |
|---|---|---|---|---|---|---|---|
| openc2e (motor livre de Creatures): `Biochemistry.cpp`, `CreatureAI.cpp`, `c2eBrain.cpp`, branch main, acesso 2026-11 | código | arquivos abertos (sem conferência linha a linha) | 256 químicos com meia-vida. Receptores escrevem nos "loci" do cérebro (limiar, vazamento, ganho) e nos drives. O cérebro roda a cada 4 tiques e recebe os 20 drives. Os instintos rodam só no sonho. Recompensa/punição, persistência e winner-takes-all **não** estão implementados: é engenharia reversa ("guesswork"). | D | 3, 4; química → cérebro | Tabela inteira "químico X → parâmetro Y do neurônio" (cansaço sobe o limiar de explorar, dor sobe o ganho de fugir). Serve de referência da bioquímica, não do aprendizado. | github.com/openc2e/openc2e |
| Forbus, K., Wright, W. (2001). Some notes on programming objects in The Sims. Notas de curso, Northwestern | documentação técnica | completo | Objetos **anunciam** valor por motivo, com atenuação por distância e escala por personalidade. O Sim escolhe entre todas as interações de todos os objetos. Anúncio alto vicia ("until they collapsed"). O exercício "Skeptical Sims" reescala o anúncio pelo que o objeto entregou. | D | 1, 5, 2; repertório | Cada objeto: {químico: ganho} inteiro. Pontuação = (falta × ganho) >> atenuação(dist). O repertório cresce com objetos, sem mexer no cérebro. Ganho por (pet, objeto) ajustado pela entrega. | qrg.northwestern.edu/papers/Files/Programming_Objects_in_The_Sims.pdf |
| Orkin, J. (2006). Three states and a plan: the A.I. of F.E.A.R. GDC 2006 | palestra (texto dos anais) | completo | Só 3 estados de máquina mais GOAP (A* sobre um vetor de estado fixo, custo por ação). Metas competem por prioridade; sem plano, cai na próxima. Memória de trabalho grava falhas (porta bloqueada) e força replanejar. | D | 1, 4, 5; planejamento | Vetor de ~8 inteiros, ~10 ações com pré-condição, efeito e custo; busca em largura de profundidade ≤ 3, desempate por índice. "Lugar L vazio" invalida o plano. | gamedevs.org/uploads/three-states-plan-ai-of-fear.pdf |
| Isla, D. (2005). Handling complexity in the Halo 2 AI. GDC 2005 (Game Developer) | palestra (texto) | resumo da página | DAG de ~50 comportamentos com listas priorizadas; tags em bitvector podam candidatos. A ativação analógica com mais de 2–3 opções ficou "almost impossible" de calibrar; o vencedor anterior tinha bônus contra o "dithering". Memória por objeto, inclusive "busquei e não achei". | D | 4, 5 | Bônus +B à ação atual; máscaras de bits (dormindo, dono perto); estímulos temporários com TTL. | gamedeveloper.com/programming/gdc-2005-proceeding-handling-complexity-in-the-i-halo-2-i-ai |
| Jakobsson, J. (JLJac), James Primate. Devlog de Rain World, TIGSource 2012–2014 (espelho candlesign.github.io/Rain-World-Devlog, pp. 001 e 033) | blog de desenvolvedor (espelho de fã de texto de 1ª mão) | 2 páginas, resumo | Cada criatura guarda o jogador como **em vista / último lugar visto / sem ideia**; o lugar é apagado ao revisitar e não achar, e expira. Paciência e memória variam por indivíduo. "Fake events" tiram do ócio. | D | 5, 1; aparência de pensar | Três estados por comida (vista, lembrada em L com idade, sem ideia); apagar ao chegar e não achar; paciência e TTL como genes inteiros. | candlesign.github.io/Rain-World-Devlog/Pages/001 |
| Priestman, C. (2017). Crafting the complex, chaotic ecosystem of Rain World. Game Developer, 28/03/2017 | jornalismo com entrevista | completo | As criaturas existem "for themselves": buscam comida e voltam à toca antes da chuva. Querem ser espertas o bastante para serem enganadas. | D | aparência de pensar | Voltar à cama antes do limiar de cansaço é intenção visível. | gamedeveloper.com/design/crafting-the-complex-chaotic-ecosystem-of-i-rain-world-i- |
| Molyneux, P. (2001). Postmortem: Lionhead Studios' Black & White. Game Developer, 13/06/2001 | postmortem | completo | A criatura parece um "clever puppy"; o estúdio diz ter evitado elementos aleatórios. **Não** fala de BDI nem de perceptrons; isso segue sem fonte aberta. | D | 4 | Apoio fraco a argmax com inércia no lugar do sorteio. | gamedeveloper.com/design/postmortem-lionhead-studios-i-black-white-i- |

---

## O que tem evidência com controle e o que é só desenho

**Com controle**

Biologia:
- Root 2011 — a fome sobe o ganho olfativo.
- Sayin 2019 — persistência faminta e freio no consumo.
- Zhang 2009 — revalorização pelo estado, sem reaprender.
- Pierce-Shimomura 1999, Iino & Yoshida 2009 e Gomez-Marin 2011 — quimiotaxia por dC/dt e por varredura.
- Gray 2005 — busca local após perder a comida.
- Flavell 2013 — dois estados persistentes por neuromodulador.
- Yagishita 2014 e Shindou 2019 — janela do traço.
- Bittner 2017 — lugar aprendido em uma passagem.
- Momennejad 2017 — representação de sucessores em humanos.

Agentes:
- Bryson 2000 — hierarquia vs. paralelo, com estatística.
- Krichmar 2013 — braços com lesão e τ, sem estatística.
- Blundell 2016 — comparação com linhas de base, sem estatística entre sementes.
- Yoshida 2024 — comparação entre definições de recompensa.
- Lenski 2003 — recompensa intermediária.

Uma ressalva vale para tudo isso: nenhum desses controles foi feito num pet como o do Digilab. As provas com animais mostram que o mecanismo existe e basta no animal, não que ele vai funcionar no pet.

**Simulação ou teoria comparada com dados publicados:** Keramati & Gutkin 2014, Miller et al. 2019, Daw et al. 2005, Izhikevich 2007, Mattar & Daw 2018, Foster et al. 2000, Lengyel & Dayan 2007, Izquierdo & Lockery 2010.

**Só desenho ou relato:**
- Creatures (artigo e openc2e), PolyWorld, Sims 1994.
- Blumberg 1996, Isla 2001, Blumberg 2002 e Prescott 2006 (este com medida descritiva sem braço de controle).
- Todo o eixo 9.
- Doya 2002, Sterling 2012, Barrett & Simmons 2015, Tschantz 2022.

---

## Cinco mecanismos, do maior para o menor retorno por custo

Ordem pelo que mais provavelmente ataca as falhas (1)–(5) com menor custo. Cada um cabe em inteiros, é determinístico e não pede treino de ponta a ponta.

### M1. Compromisso com histerese e término, modulado pela fome — ataca (4) e (1)

**De onde vem:** Blumberg 1996, Isla 2001, Prescott 2006, Sayin 2019, Flavell 2013, Dill 2015.

**Como funciona:**
- O comportamento ativo ganha um bônus `P = base + (fome >> k)` até o **DoUntil** (comeu, saciou ou estourou o tempo T).
- Um rival, o sono inclusive, só toma o lugar se `rival*16 > ativo*G`.
- Uma lista Startle (dano, susto, fome crítica) interrompe por argmax.
- Comer zera P, como o freio VPM4.
- "Passear" recebe posto 0 quando há comida percebida e fome > L.
- Um nível de interesse que cai sem progresso evita prender o pet numa meta impossível.

**Teste com controle:**
- Mesmas sementes e mundos da L0.
- Braços:
  - (a) sorteio atual;
  - (b) P ligado à fome;
  - (c) P = margem **fixa** com a mesma média de (b), o que separa histerese pura de modulação pelo corpo;
  - (d) dose G ∈ {16, 24, 32, 48}.
- Medidas:
  - fração de buscas distantes cortadas pelo sono (hoje 80 %);
  - achado no longe (hoje 41 %);
  - trocas de meta por hora;
  - comida ingerida.
- Medida de não regressão: latência de reação a dano ou susto, que não pode piorar.
- Critério: (b) > (a) e (b) > (c), com IC pareado por semente.

### M2. Quimiotaxia por dC/dt + varredura curta — ataca (1)

**De onde vem:** Pierce-Shimomura 1999, Iino & Yoshida 2009, Gomez-Marin 2011, Izquierdo & Lockery 2010.

**Como funciona:**
- Guarda `C_ant` e um acumulador de queda.
- Enquanto d ≥ 0, segue reto.
- Quando a queda acumulada passa de L, faz uma varredura: cheira em 2 orientações por 1–2 tiques e vira para a maior.
- Soma um viés lateral pequeno ∝ C_esq − C_dir.
- Entra como entrada nova de "comer/explorar", sem a rede precisar representar a direção.

**Teste com controle:**
- Braços:
  - (a) base;
  - (b) só dC/dt;
  - (c) dC/dt + varredura;
  - (d) **giros na mesma taxa de (c), mas desacoplados de d**, o que separa "girar mais" de "girar na hora certa".
- Medidas:
  - achado no longe;
  - tiques até comer;
  - fração de giros que começam com o cheiro em queda (a larva chega a 81,6 %).
- Cruzar 2×2 com o M1 para separar o efeito do sono do efeito da direção.

### M3. Terceiro fator com sinal = queda do drive convexo, menos a linha de base, mais um árbitro hábito × modelo — ataca (2)

**De onde vem:** Keramati & Gutkin 2014, Yoshida 2024, Gerstner 2018, Daw et al. 2002, Miller et al. 2019, Lengyel & Dayan 2007, a regra DriveReducer+Drive→Reward do Creatures.

**Como funciona:**
- `r = D(H_t) − D(H_{t+1})`, com `D = Σ falta² >> s`.
- O hebbiano usa `r − EMA(r)`, com sinal: piorar enfraquece.
- O peso do hábito na soma é `w = min(n/N0, 1) × (1 − contingência)`. "Contingência" é o acerto do modelo do desfecho, que já existe e já funciona.

**Teste com controle:**
- Braços:
  - (a) hábito atual;
  - (b) M3;
  - (c) sem hábito;
  - (d) M3 com r **embaralhado no tempo**, mesma média e variância.
- Medidas:
  - desempenho homeostático médio;
  - **teste de desvalorização**: trocar de uma vez a comida de uma classe por uma que não alivia e contar as escolhas dessa classe nos K tiques seguintes.
- Critério:
  - (b) ≥ (c) na fase estável;
  - (b) cai tão rápido quanto (c) depois da desvalorização;
  - (d) cai abaixo de (b).

### M4. Alvo de lugar com coordenada, memória em três estados e busca local que decai — ataca (5)

**De onde vem:** Foster, Morris & Dayan 2000, Gray, Hill & Bargmann 2005, o devlog de Rain World, Blundell 2016, Zhang 2009.

**Como funciona:**
- Cada classe de comida tem um estado: vista, lembrada em (x,y) com idade, ou sem ideia.
- O valor do lugar lembrado passa por κ(necessidade) no ato.
- Quando a fome vence, explorar recebe o vetor `meta − posição`.
- Ao chegar, começa a busca local: a taxa de virada fica alta e cai em degraus por um contador de tiques.
- Se não achar em T tiques, o lugar é apagado e a idade expira.

**Teste com controle:**
- Arena com comida que reaparece no mesmo ponto, e outra em que a comida se desloca a uma distância conhecida.
- Braços:
  - (a) memória autobiográfica atual;
  - (b) com vetor;
  - (c) vetor para uma célula **ao acaso à mesma distância**;
  - (d) com vetor + busca local, contra (e) busca local com taxa constante igual à média de (d).
- Medidas:
  - chegadas ao lugar lembrado com achado;
  - revisitas inúteis a lugar vazio;
  - tiques até comer.

### M5. Ponte de crédito por opção + buffer de eventos — ataca (3)

**De onde vem:** Sutton, Precup & Singh 1999, Bittner 2017, Izhikevich 2007, Yagishita 2014, Momennejad 2017. O Yagishita mostra que o traço de segundos não cobre minutos; daí a ponte.

**Como funciona:**
- "Chamar o dono → andar → comer" vira uma opção com término.
- Um buffer circular inteiro guarda os últimos N pares (ato, lugar).
- No alívio (o r do M3), o crédito vai ao ato que **abriu** a opção e aos lugares do buffer, com peso por posição.
- Variante opcional: uma matriz pequena de sucessores M[classe][classe_futura].

**Teste com controle:**
- Atraso ato → alívio manipulado: 0, 30 s, 2 min e 5 min de jogo.
- Braços:
  - (a) sem ponte;
  - (b) traço exponencial curto;
  - (c) opção + buffer;
  - (d) **placebo**: alívio dado em hora aleatória, onde nenhum braço deve aprender.
- Medida: probabilidade de repetir o ato inicial quando a fome volta.
- Previsão: (b) só funciona com atraso perto de 0; (c) se mantém com atraso longo; (d) fica na base.

### Fora da lista, mas baratos e com apoio

- Ganho olfativo pela fome (Root 2011). Amplifica a intensidade, mas não dá direção.
- Par de estados M_fica/M_sai (Flavell 2013).
- Anúncios de objeto ao estilo The Sims, para crescer o repertório sem mexer no topo.
- GOAP de profundidade ≤ 3 (Orkin 2006), para o planejamento curto visível. Faz sentido depois do M1 e do M4.
- Custo energético por ação (Yaeger 1994).
- CPG e "advérbio" químico para os gestos (Ijspeert, Isla).
