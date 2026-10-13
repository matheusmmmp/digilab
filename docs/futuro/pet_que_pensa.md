# O pet que pensa (J5): planejar com um modelo do mundo aprendido — desenho no papel

Status (2026-10-12): **IDEIA, desenho PROPOSTO.** Pedido do Gerente ao worker C, só papel. **PQ-1 a PQ-7 DECIDIDAS pelo Matheus em
2026-10-13, todas pela recomendação** (seção 9). A tarefa é `docs/TAREFA_V2_PET_QUE_PENSA.md`, e o plano é `docs/PLANO_ANALISE_V2_PET_QUE_PENSA.md`. Nenhum código e nenhuma run antes de uma tarefa e de um plano de análise registrados.

**O que já está decidido:**
- **o objetivo (2026-10-07):** o Matheus quer o pet que **pensa**, isto é, que prevê as consequências ("se eu fizer X, acontece Y") e
  planeja, e não só o instinto com reforço por cima (o caminho E). O porte do cérebro A para a web (v11, #201) fica **pausado** até ele
  existir;
- **a medida (DS-1, `docs/DEFINICOES_V2_SEIS_PERGUNTAS.md`, seção 1):** o pet "planeja" quando muda a escolha depois de uma mudança no
  mundo **sem ter reexperimentado a consequência**. Ela é um par de testes:
  - **teste 1, revalorização:** só ele passa → representação de sucessor (SR) ou modelo só de recompensa;
  - **teste 2, mudança de transição:** os dois passam → planejamento com modelo de transição;
  - nenhum passa → hábito.

**Regras deste documento:**
- referências só verificadas (`docs/referencias/REGRAS_CITACAO_DIGILAB.md`), com quanto foi lido;
- SEM FONTE onde não houver;
- números novos PROPOSTOS;
- **nenhuma alegação de novidade.** Planejar com um modelo aprendido é o tema de Dyna (Sutton 1990) e de MuZero (Schrittwieser et al.
  2020), ambos com o título conferido (seção 10). O que este desenho pode ter de próprio é a medida com controle no mesmo pet, e não o
  mecanismo.

## 1. O ponto de partida

- **Nenhum cérebro da V2 planeja.** O A, o B e o C aprendem pesos por reforço por cima do instinto (`docs/RESULTADO_V2_L1.md`; a
  comparação A × C). No sentido de Daw, Niv e Dayan (2005, só o título conferido, pista), os três são de hábito: escolhem pelo que foi
  reforçado, não pelo que preveem.
- **No mundo `padrao`, o instinto decide cerca de 80% das decisões do A** (L1, G4 0,182 do aprendido; `artifacts_v2_l1/validacao/`).
- **O que já existe e serve ao planejar:**
  - **o mundo físico (J1):** árvores com tipo de fruta, a comida que cai e apodrece, a visão, a posição e o custo de andar. O alvo do
    explorar e do comer é uma escolha entre candidatos (`mundo.py`), e o cérebro A já aprende o alvo por classe (`alvo_aprendido`, #255);
  - **o corpo (J2):** os receptores e o sinal pelo corpo (`lobos.sinal_corpo`). O valor de um desfecho pode ser calculado do corpo **de
    agora**;
  - **o Digicorpo (a rede de si):** já prevê os receptores a n decisões, dada a ação (`rede_de_si.py`, etapa 2 do ego, em observação). É
    um modelo direto do corpo, mas genérico: a entrada é a ação, não o tipo de comida.

## 2. O que "planejar" quer dizer aqui

Três peças, todas aprendidas pelo pet só do que ele percebe (sem acesso ao químico, ao `Estado` nem ao registro do mundo):

1. **O modelo do desfecho** (o que cada coisa faz no meu corpo):
   - para cada tipo de comida (a ração, cada fruta madura, a podre), a mudança esperada de cada receptor ao comê-la;
   - é aprendido em qualquer contexto em que o pet come, inclusive fora do mapa (a seção 6 usa isso no teste 1);
   - é uma média em inteiros pela diferença dos receptores antes e depois do consumo.
2. **O mapa da comida** (o que cai onde):
   - para cada árvore (e para o comedouro), a contagem do que o pet **viu** lá, por tipo;
   - o pet atualiza pelo que vê, não só pelo que come (a seção 6 usa isso no teste 2);
   - com um esquecimento lento: uma média móvel em inteiros, para acompanhar a troca.
3. **O planejador de um alvo:** antes de escolher o alvo do comer ou do explorar, para cada candidato k o valor previsto é
   `V(k) = Σ_tipo P(tipo | k) · valor(Δ_tipo, receptores de agora) − custo(distância até k)`.
   - **`valor(·)`** é a mesma conta do sinal pelo corpo (a falta antes contra a falta prevista depois). O valor muda com o estado: a mesma
     fruta vale mais com fome. Isso também é uma revalorização, pelo estado;
   - **o custo** é o gasto de andar, que o pet conhece pelo próprio corpo (a mudança do cansaço por subunidade, aprendida como no
     desfecho);
   - **o horizonte é um alvo:** até a chegada, e não H decisões nem uma árvore de busca (PQ-2).

O planejador **não substitui** o instinto nem o hábito. Ele soma um termo, com ganho `g_plano` (0 = o cérebro de hoje, G2), ao peso
efetivo dos candidatos de alvo e da decisão de comer ou explorar. Arbitrar por incerteza entre os sistemas é a pista de Daw, Niv e Dayan
(2005) e fica para depois (seção 8).

**O que não é planejar, neste desenho:**
- escolher pelo maior peso aprendido (hábito);
- seguir o cheiro mais forte (o instinto do mundo);
- ir onde o outro pet comeu sem ter modelo do lugar: é uma pista social, não um plano.

## 3. Como encaixa

- **No cérebro A (os lobos):** um lobo novo, `planejamento`, entre a memória e a decisão.
  - Ele lê a percepção (o corpo, o mundo) e os dois modelos, e devolve um termo por candidato.
  - O termo vai ao peso efetivo, como as entradas do corpo. No alvo, vai ao `escolher_alvo`, em cima dos pesos do alvo aprendido.
  - **O motivo e a honestidade:** a sonda "quem decidiu" sorteia com o mesmo u, sem o termo do plano. Se a ação mudaria, o fator é o
    plano, e o motivo pode dizer "fui à árvore b porque lá cai a fruta x, e a x me faz bem". O texto só nomeia o que o modelo tem.
- **No corpo:** nada muda. O valor sai dos receptores, e o metabolismo já está por baixo deles.
- **No Digicorpo (PQ-5):**
  - **o modelo do desfecho é um modelo do corpo,** como o Digicorpo, só que por tipo de comida;
  - **a recomendação é mantê-los separados por ora:** o Digicorpo segue em observação até a validação dele (o plano da rede de si), e o
    planejador usa o modelo próprio;
  - **a junção é a etapa 3 do ego,** "o automodelo na decisão" (`docs/futuro/ego_existencia.md`, seção 9), que o roadmap já liga ao J5.
- **Nos dois pets:** o mapa da comida pode aprender também do que o pet vê o outro comer (`onde_comeu`). Fica fora da primeira versão,
  para o teste 2 medir só o modelo próprio.
- **Na web:** o desenho é todo em inteiros e cabe no navegador (leitura nossa, SEM FONTE). O porte é do A, depois da validação.

## 4. O tamanho

- **O modelo do desfecho:** 5 tipos de comida × os receptores do corpo (10 a 13) dá 50 a 65 números.
- **O mapa:** o número de árvores do layout + o comedouro, × 5 tipos.
- **O planejador:** nenhum peso aprendido; ele só soma, com o `g_plano`.
- **Os modelos não são pesos da decisão:** ficam num módulo próprio, com teto próprio, como a rede de si (PQ-6). O cérebro A ganha 0 pesos
  (o termo entra com o ganho), e o teto de 1000 (`docs/DECISAO_V2_TETO_PESOS.md`) não é tocado.

## 5. O que se mede, contra o pet de instinto e reforço

**Os braços** (o mesmo cérebro A, o mesmo mundo e o mesmo dono; muda só o planejador):

| braço | o que é | o que a DS-1 prevê |
|---|---|---|
| **P1** | o A de hoje: instinto e reforço (hábito) | nenhum teste passa |
| **P1-plan** | o A com o planejador e os dois modelos | os dois passam |
| **P1-plan-desfecho** | o A com o planejador e só o modelo do desfecho (o mapa congelado no nascimento) | só o teste 1 passa |
| **P1-plan-cong** (controle) | o planejador com os dois modelos congelados antes da mudança | nenhum passa: separa "o modelo aprendeu" de "o planejador decide diferente" |

**A medida primária é a da DS-1,** na primeira oportunidade depois da mudança, por unidade:
- **teste 1:** a probabilidade de escolher o alvo da árvore da fruta revalorizada, antes e depois;
- **teste 2:** a primeira busca da fruta x depois da troca de onde ela cai: a árvore nova ou a antiga.

**Os descritivos:** o desempenho (o `D_FE`, a privação); quanto o termo do plano decide (a sonda); a deriva; o custo por decisão; e a
legibilidade do motivo.

**Por que não a tarefa de dois passos:** Akam, Costa e Dayan (2015, só o resumo) mostram que estratégias sem modelo produzem a
assinatura atribuída ao controle com modelo nessa tarefa. O par da DS-1 evita isso.

## 6. Os dois testes no mundo físico

**Teste 1: revalorização sem reexperiência na escolha (PQ-4).** Tem de haver um caminho para o efeito novo chegar ao pet sem ele escolher
a fruta no mapa. Recomendação: a forma de Adams e Dickinson (1981, resumo).
- **Lá:** ratos treinados a apertar a alavanca por uma comida receberam uma aversão condicionada a essa comida **fora** do contexto da
  alavanca. Os que tinham aversão ao reforçador responderam menos no teste em extinção.
- **Aqui, em três fases:**
  1. o pet aprende no mapa que a árvore b dá a fruta x, e que a x faz bem;
  2. o efeito da x muda, e **o dono dá a x na mão**, no ninho, longe da árvore. É um evento do registro, fora do orçamento; o pet come
     sem escolher a árvore;
  3. **o teste:** a primeira vez que o pet escolhe para onde ir com fome e a b à vista ou lembrada. O hábito escolhe a b como antes; o
     planejador, com o desfecho novo, não.
- **Uma segunda forma, pelo estado:** a mesma fruta com o corpo saciado (a saciedade específica). É descritiva, e a seção 8 diz por quê.

**Teste 2: mudança de transição sem reexperiência.**
1. **A troca:** num tick gravado no registro, a fruta x passa a cair na árvore c, e a b passa a dar outra (os efeitos ficam iguais).
2. **O pet vê, sem comer:** o pet passa pela c e **vê** a x no chão, ou a vê cair, sem comê-la.
3. **O teste:** a primeira busca da x com fome. O planejador com o mapa vai à c; o hábito e o modelo só do desfecho vão à b.

**Quem precisa da mudança no motor:** a troca de tipo por árvore num tick (o A, como a troca do mutável) e o evento "o dono dá a fruta na
mão" (o A). O que o pet vê já está na percepção (`vistos`).

## 7. O que precisa existir antes

- **J1 validado,** com os números do mundo (a validação está em curso, segundo o coordenador).
- **J2 com o metabolismo e a calibração do corpo.** O valor do desfecho lê os receptores; com o corpo calibrado, o "faz bem" e o "faz mal"
  têm escala.
- **O desempate do cheiro no motor** (achado do #278: ainda a ordem fixa). Não bloqueia o planejador, mas o hábito e o instinto que ele
  enfrenta dependem do cheiro.
- **A decisão do teto de pesos** (TP-1), só se a PQ-6 sair diferente da recomendação.

## 8. Riscos

| # | risco | o que o desenho faz |
|---|---|---|
| R-1 | **A assinatura falsa:** um hábito sofisticado passa no teste | o par da DS-1, com o braço P1-plan-cong e o P1-plan-desfecho, que prevêem resultados diferentes |
| R-2 | **A primeira oportunidade não chega,** ou chega sem fome | a janela do teste é fixada no plano, e as unidades sem oportunidade saem contadas, não excluídas em silêncio |
| R-3 | **O planejador domina** e o pet vira um otimizador frio, que só vai à melhor árvore | o `g_plano` se calibra pela regra do plano, sem ler o primário. O instinto e o hábito continuam somando |
| R-4 | **O teste 1 pela saciedade** confunde a revalorização com a saciedade específica, que o pet já tem nas frutas (`k_saciedade`) | a forma pelo estado fica só descritiva, e a primária é a de Adams e Dickinson |
| R-5 | **O mapa aprende do que vê cair,** e o hábito também muda pelo que vê (o cheiro, a visão no instinto) | o teste 2 mede a primeira busca **fora** da vista da x (lembrada, não vista) |
| R-6 | **A arbitragem:** somar o termo não é arbitrar por incerteza | registrado. A arbitragem por incerteza (Daw, Niv e Dayan, pista) entra só com outra tarefa |
| R-7 | **O rótulo "pensa"** | só vale pela medida da DS-1. A tela não diz "pensou" sem o fator do plano no motivo |
| R-8 | **O custo:** o planejador avalia todo candidato em toda decisão com alvo | os candidatos são poucos (os do motor). O custo por decisão sai medido no piloto |

## 9. Decisões do Matheus

**DECIDIDAS em 2026-10-13: PQ-1 a PQ-7, todas como recomendado.**

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| PQ-1 | A arquitetura | **(c) o modelo do desfecho + o mapa da comida + o planejador de um alvo**, somado ao A. As outras opções: **(a)** a camada de SR da DS-1; **(b)** um modelo de transição com simulação de H passos (Dyna); **(d)** busca em árvore | **(a):** pela DS-1, a SR não passa no teste 2, e o pet não "pensa" no sentido pedido. **(b):** um modelo de estado inteiro do mundo, caro e difícil de pôr em inteiros, para um ganho que o teste não pede. **(d):** o custo por decisão e o porte para a web |
| PQ-2 | O horizonte | **um alvo** (até a chegada) | H decisões: pede o modelo de transição do corpo inteiro e multiplica o custo. Sem horizonte: o planejador vira o hábito |
| PQ-3 | Onde entra | **um lobo novo no cérebro A, com o termo somado pelo `g_plano`** (0 = o de hoje), na decisão e no alvo | substituir o instinto e o hábito: perde o G2 e a comparação no mesmo cérebro. Um cérebro novo: a comparação deixa de ser "o mesmo pet com e sem pensar" |
| PQ-4 | Como fazer o teste 1 | **o dono dá a fruta revalorizada na mão, fora do mapa** (a forma de Adams e Dickinson); a forma pelo estado só descritiva | pelo estado: confunde com a saciedade específica que o pet já tem. Sem um caminho fora do mapa: o teste 1 vira reexperiência, e nada se mede |
| PQ-5 | O Digicorpo e o modelo do desfecho | **separados por ora;** a junção é a etapa 3 do ego | juntar já: mexe no Digicorpo antes da validação dele, e o plano da rede de si perde a base |
| PQ-6 | O tamanho e o teto | **os modelos num módulo próprio, com teto próprio**, e 0 pesos a mais no cérebro A | contar no cérebro: o planejador esbarra no teto de 1000 nos regimes que já estão perto (998, 990) |
| PQ-7 | A web | **o porte v11 segue pausado** até a validação do J5; depois o A porta o cérebro com o planejador | portar antes: a tela diria "foi instinto" quase sempre, o motivo da pausa |

## 10. Referências

| referência | DOI | quanto foi lido | o que sustenta aqui |
|---|---|---|---|
| Adams e Dickinson (1981). Instrumental Responding following Reinforcer Devaluation. Q. J. Exp. Psychol. B | `10.1080/14640748108400816` | resumo (OpenAlex) | a aversão condicionada à comida fora do contexto da alavanca reduz a resposta em extinção: o desenho do teste 1 |
| Akam, Costa e Dayan (2015). Simple Plans or Sophisticated Habits? PLoS Comput Biol | `10.1371/journal.pcbi.1004648` | resumo (revisão F) | a tarefa de dois passos sozinha não separa o hábito do modelo |
| Dayan (1993). The Successor Representation. Neural Computation | `10.1162/neco.1993.5.4.613` | resumo (revisão F) | a SR, a opção (a) |
| Momennejad et al. (2017). Nat Hum Behav | `10.1038/s41562-017-0180-8` | resumo (revisão F) | a SR é flexível à recompensa e insensível à transição |
| Pfeiffer e Foster (2013). Nature | `10.1038/nature12112` | resumo (revisão F) | sequências hipocampais antes do movimento traçam o caminho até a meta lembrada (o animal simula antes de agir) |
| Daw, Niv e Dayan (2005). Nat Neurosci | `10.1038/nn1560` | só o título (revisão F) | pista: a arbitragem por incerteza entre os dois sistemas |
| Dolan e Dayan (2013). Goals and Habits in the Brain. Neuron | `10.1016/j.neuron.2013.09.007` | resumo (revisão F) | metas e hábitos como espectro, não dicotomia |
| Sutton (1990). Integrated Architectures for Learning, Planning, and Reacting Based on Approximating Dynamic Programming. ML Proceedings 1990 | `10.1016/b978-1-55860-141-3.50030-4` | só o título (Crossref, 2026-10-12) | a existência da linha (Dyna); nenhuma afirmação de conteúdo |
| Schrittwieser et al. (2020). Mastering Atari, Go, chess and shogi by planning with a learned model. Nature 588 | `10.1038/s41586-020-03051-4` | só o título (Crossref, 2026-10-12) | que planejar com um modelo aprendido já existe; nenhuma afirmação de conteúdo |
