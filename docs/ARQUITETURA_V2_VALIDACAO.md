# Arquitetura do Matheus para a V2 — validação e plano de implementação

Status: **PROPOSTO** (coordenador, 2026-10-01). Objeto: a arquitetura desenhada pelo Matheus (genoma → fisiologia, cérebro
inicial e plasticidade → estado interno → percepção com retorno do corpo → contexto e memória → sistemas de comportamento →
arbitragem → ação → corpo → consequência → valor homeostático, hedônico e instrumental → reforço → aprendizado local →
memória associativa, mudança do controlador e codificação de episódio; e, por fora, **o dono dá informação de contexto ao pet
e o mundo valida ou refuta**). Este documento não propõe código, equação nem número: diz o que já existe, o que a literatura
sustenta, onde o desenho precisa de definição, e em que ordem dá para construir sem quebrar as regras do projeto.

## 1. Veredito

**É implementável, e é coerente com o que a v1 mostrou.** A v1 concluiu que o dono pesa pelo cuidado, isto é, pela
consequência no corpo, e não pelo feedback avaliativo (`docs/LEITURA_CONSOLIDADA_DONO.md`). A sua arquitetura tira o dono
do papel de recompensa e o põe como fonte de informação que o mundo confirma ou não. Isso não reabre a refutação: é outro
mecanismo e outra pergunta, e precisa de plano próprio.

Três condições para dar certo:
1. **Construir por partes**, uma peça por versão, cada uma com gate. Montar tudo de uma vez seria a "arquitetura
   Frankenstein" contra a qual o próprio corpus DigiBrain alerta (`docs/digibrain/integration/03_GAPS_AND_CONFLICTS.md`, C4).
2. **Definir três coisas que o diagrama deixa abertas** (seção 4): por onde a informação do dono entra, o que é o valor
   instrumental, e como os três valores viram um reforço.
3. **Corrigir quatro leituras das fontes** (seção 3) antes de qualquer texto que cite a arquitetura.

## 2. Cada bloco contra o que existe

| bloco | o que existe hoje | estado | distância |
|---|---|---|---|
| GENOMA | espécie e temperamento (4 eixos) sorteados do ovo; herança (`digilab/temperamento.py`, `heranca.py`) | EXECUTADO | o genoma não carrega fisiologia nem plasticidade; no E1 explicou 4,9% da variância e o gate falhou (`artifacts_linhagem/natureza_criacao/`) |
| FISIOLOGIA | drives fome, higiene, energia, humor, saúde; privação → perda de saúde → morte (`digilab/state.py`) | EXECUTADO, fixo em `config.py` | fisiologia por genoma é mecânica nova |
| CÉREBRO INICIAL | `PoliticaLobos` com pesos inteiros iniciados no prior do instinto (L0, `digilab/policies/lobos.py`) | EXECUTADO | o prior é o mesmo para todos, não vem do genoma |
| PARÂMETROS DE PLASTICIDADE | passo e teto dos pesos em `ConfigLobos` (L1, em calibração) | EM ANDAMENTO | por genoma = evolução da capacidade de aprender (efeito Baldwin; seção 3) |
| ESTADO INTERNO | o estado de `state.py` + memória por espaços e emoção (v1, ligadas ao bandit) | EXECUTADO | — |
| PERCEPÇÃO | lobo de percepção, 10 entradas (`Estado.vetor`) | EXECUTADO | entrada nova da bola no desenho A1 (#113) |
| RETORNO DO CORPO | não há corpo; o "retorno" é a mudança do estado | — | corpo 2D é IDEIA em stand-by (`docs/TODO_INTERACAO_CORPO.md`) |
| CONTEXTO ATUAL | o mesmo vetor de percepção | EXECUTADO | — |
| RECUPERAÇÃO DE MEMÓRIA | memória por espaços (v1): 6,9% dos motivos citam memória (`artifacts_v1_memoria_espacos/metrics.json`); a história da voz não decide nada (`historia.py`) | EXECUTADO na v1, fora dos lobos | nó L2 do roadmap |
| SISTEMAS DE COMPORTAMENTO | as regras do instinto, executadas pelo lobo de impulsos, propõem candidatos (`lobos.py`) | EXECUTADO (só vida) | **luta é outro sistema** (gambits do combate V2.1); juntar vida e luta num cérebro só é escopo grande |
| ARBITRAGEM | lobo de decisão escolhe entre os candidatos; a regra do instinto decide qual sistema fala | EXECUTADO | "duas prioridades" (necessidade × pedido) é o nó L3 |
| AÇÃO → CORPO → CONSEQUÊNCIA | `policy.efeito_da_acao_do_pet` e `state.py` | EXECUTADO | consequência só no estado; sem objetos no mundo até a bola |
| VALOR HOMEOSTÁTICO | drives existem; **nenhum aprendizado usa a redução de déficit como reforço** (o instinto são regras escritas à mão, `policy.py`) | NÃO EXISTE | mecânica nova (seção 3, item 4) |
| VALOR HEDÔNICO | não existe | NÃO EXISTE | as frutas (definições pendentes, `ROADMAP_V2.md`, P5) |
| VALOR INSTRUMENTAL | não definido | NÃO EXISTE | seção 4, D-B |
| REFORÇO | L1: sinal escalar do dono como vantagem (COACH, `arXiv:1701.06049`, VERIFICADA) | EM ANDAMENTO | a sua arquitetura tira o dono daqui (seção 4, D-A) |
| APRENDIZADO LOCAL | só o lobo de decisão aprende (L1) | EM ANDAMENTO | coerente com o desenho |
| MEMÓRIA ASSOCIATIVA, MUDANÇA DO CONTROLADOR, CODIFICAÇÃO DE EPISÓDIO | mudança do controlador = L1; episódio = a história da voz (registra, não decide) | parcial | as três saídas precisam de gates separados (seção 5, N6) |
| DONO → INFORMAÇÃO → PET; MUNDO VALIDA | o dono age no estado (cuidado) e dá elogio e bronca (avaliação) | NÃO EXISTE como informação | é a peça nova central (seção 4, D-A) |

## 3. O que as fontes sustentam, e quatro correções

Status pelas tabelas verificadas do projeto (`docs/referencias/`, `v1/docs/referencias/v3_referencias_verificadas.csv`) e pelo
índice do corpus DigiBrain (`D:\Trab\digilab\docs\digibrain\sources\SOURCE_INDEX.md`, URLs conferidas pelo corpus, **fora**
da tabela verificada do projeto: valem como pista até entrarem nela).

| princípio da sua síntese | fonte | status | o que sustenta de fato |
|---|---|---|---|
| Valor homeostático como reforço | Keramati e Gutkin 2014, `10.7554/elife.04811` | VERIFICADA | recompensa como redução de desvio homeostático |
| Gostar ≠ querer ≠ aprender | Berridge e Robinson 1998; Berridge, Robinson e Aldridge 2009; Finlayson e Dalton 2012 | VERIFICADA (busca V3) | dois registros separados; reação mensurável, não experiência |
| Feedback do dono depende da política | MacGlashan et al., `arXiv:1701.06049` | VERIFICADA | a base da L1 |
| Separar controlador herdado de adquirido | Hallawa et al., Evo-RL, `10.1145/3449726.3459475` | VERIFICADA | já publicado: **não é novidade** do Digilab (regra 1 da `literatura-digilab`) |
| Episódio armazenado ≠ recuperado ≠ causal | Castro e Gudwin 2013, `10.4018/jse.2013010102` | VERIFICADA | memória episódica por cenas numa criatura simulada; Sakabe et al. 2025 (`10.1016/j.cogsys.2025.101397`) é pista |
| História acumulada e consequência narrativa | Adams 2021, `10.1515/9783839453452-007` | VERIFICADA | precedente de desenho, **não** validação cognitiva |
| Organismo com bioquímica e aprendizado na vida | Grand, Cliff e Malhotra 1997, `10.1145/267658.267663`; Grand e Cliff 1998 | VERIFICADA | arquitetura geral; os detalhes do **Creatures 3** (genes, lobos, químicos) só existem em wiki de fã: NÃO VERIFICADA EM FONTE PRIMÁRIA |
| Modularidade e reforço distribuído (*Drosophila*) | Dorkenwald et al. 2024; Schlegel et al. 2024; Shiu et al. 2024; Aso e Rubin 2016; Otto et al. 2020 | pista (corpus) | conectoma ≠ dinâmica ≠ comportamento; o FlyWire é mapa, não prova de função |
| Drives concorrentes e motivação | Fróes e Gudwin 2017; Berto et al. 2024; Rossi et al. 2024 | pista (corpus) | — |
| CfC com RL (NORNBRAIN) | repositório `thechimpmatrix/nornbrain` | software, não evidência | trabalho em andamento, sem resultado de eficácia |

**As quatro correções:**
1. **A.L.I.V.E. não prova dois controladores nem herança da capacidade de aprender.** O corpus é explícito: A.L.I.V.E. é uma
   plataforma (dissertação, USP 2003) e o ALGA tem frentes separadas; não se deve fundir os dois nem atribuir a eles essa
   tese (`docs/digibrain/synthesis/contradictions.md`, item 2). A fonte verificada para controlador herdado × adquirido é
   Hallawa et al., e para herdar a capacidade de aprender é o efeito Baldwin (Hinton e Nowlan 1987; Fernando et al. 2018,
   `10.1145/3205651.3205763`), que já está publicado.
2. **ALGA não é um tutor dono.** O relatório sustenta transmissão social de informação entre peixes virtuais com
   autoavaliação (`SOURCE_INDEX.md`, nota final), não um tutor humano. A sua leitura "tutor informa, consequência valida"
   é próxima, mas a ponte até o dono é do Digilab, não do ALGA. A fonte "CST" isolada não foi identificada.
3. **FlyWire é mapa, não mecanismo.** Citar Dorkenwald et al. para o diagrama, Schlegel et al. para a anotação e Shiu et
   al. para o modelo computacional simplificado, separados (`SOURCE_INDEX.md`, nota de correção).
4. **"O projeto já usa RL homeostático" não é verdade.** O instinto são regras escritas à mão sobre drives homeostáticos,
   sem aprendizado; o RL homeostático é só a base teórica citada. Valor homeostático como reforço é mecânica nova.

**NORNBRAIN (CfC) fica como hipótese concorrente, não como peça.** O CfC usa funções transcendentais e pesos em ponto
flutuante, e a V2 exige ativação sem transcendental e pesos inteiros para o replay e a paridade Python/web (G1, D8). Trocar
por CfC quebraria o requisito central do projeto.

## 4. Três definições que o diagrama precisa antes de virar código

**D-A. Por onde a informação do dono entra.** O diagrama põe o dono fora do pet, mas não diz onde a informação chega.
Proposta: entra pela **percepção**, como um item de contexto (por exemplo, "o dono apontou a fruta X" ou "o dono avisou
perigo"), e **nunca** como reforço. Quem reforça é a consequência. Isso separa o dono informante do dono avaliador da L1.
- Controle obrigatório: o mesmo mundo com a informação do dono **acoplada** (a mesma quantidade de avisos, em momentos
  sorteados) e sem informação, além do "só cuidado" acoplado de sempre.
- Critério: o efeito da informação conta como ensino só se aparecer sem diferença de saúde e de mortes entre os braços (G5).
- Custo de errar: se a informação entrar como reforço, o desenho volta a ser o feedback avaliativo que a v1 refutou.

**D-B. O que é o valor instrumental.** Duas leituras possíveis: (1) o pet conseguiu o que a ação visava (pegar a fruta,
alcançar a bola), ou (2) o objetivo do dono. Recomendação: **(1)**, sem o dono. Pela (2) o dono volta como recompensa pela
porta dos fundos.

**D-C. Como três valores viram um reforço.** Somar num escalar ou manter canais separados é a pergunta aberta H-REINF-001
(`docs/digibrain/synthesis/contradictions.md`, item 5: a neuromodulação heterogênea da mosca não mostra que reforço em
vários canais vence o escalar). Recomendação: **começar com um canal só**, o homeostático, e acrescentar o hedônico como
segundo canal com comparação explícita contra o escalar somado.

## 5. Plano de implementação

Cada nó entra atrás de uma chave desligada, numa versão de pet própria na web e com tarefa e plano de análise commitados
antes da run. Uma peça por vez: cada uma passa sozinha antes de se juntar às outras.

| nó | peça da arquitetura | depende de | gate (PROPOSTO) | estado |
|---|---|---|---|---|
| N0 | estado interno, percepção, sistemas de comportamento (impulsos), arbitragem (decisão), cérebro inicial = prior | — | G1, G2 | **feito** (L0) |
| N1 | aprendizado local no lobo de decisão, reforço = dono avaliador (COACH) | N0 | G3–G6 da L1 | em calibração; **fica como braço de comparação** do dono avaliador |
| N2 | corpo e consequência num objeto do mundo: a bola | N0 | G1, G2; 1a-pet | desenho no PR #113 |
| N3 | **valor homeostático como reforço** (a consequência ensina, sem dono) | N1 (mesma regra de atualização), um ambiente em que a escolha mexa em drive | o pet aprende a reduzir déficit melhor que o instinto, com G6 (sem deriva) e sem mortes novas | novo |
| N4 | **valor hedônico** com gostar e querer separados (frutas, sem vício) | N3, `DEFINICOES_FRUTAS_V2.md` | os dois registros se separam; critério ensino × cuidado da P5 | definições pendentes |
| N5 | **dono informante, mundo valida** (D-A) | N3 ou N4 (precisa de consequência que valide) | informação × informação acoplada × sem informação; efeito sem diferença de saúde (G5); G3 entre donos que informam certo e errado | novo, peça central |
| N6 | memória: associativa, episódio codificado, recuperado e causal | N5 | quatro marcos separados (registrado, codificado, recuperado, muda a decisão), com controle de recência e de embaralhamento | L2 do roadmap |
| N7 | arbitragem entre sistemas que competem (necessidade × pedido) | N5 | G5 continua valendo | L3 do roadmap |
| N8 | valor instrumental (D-B) e comparação de canais (D-C) | N4, N5 | canais separados × escalar somado, com o mesmo orçamento | novo |
| N9 | vício (assimetria querer × gostar) | N4 | `ROADMAP_V2.md`, P8 | depois das frutas |
| N10 | genoma → fisiologia, cérebro inicial e plasticidade | fase 3 | genoma com variância herdável, com plano próprio (no E1 o genoma pesou 4,9%) | fase 3; Baldwin já publicado, não é novidade |
| — | corpo 2D, luta dentro do mesmo cérebro, CfC | — | — | **fora** da fase de experimentos (stand-by) |

**A pergunta de pesquisa que a arquitetura abre** (para o plano da V2, se o Matheus adotar): *um pet que aprende pela
consequência no mundo absorve informação do dono de um jeito que se separa do cuidado?* Ela troca a pergunta de hoje
("o dono avaliador separa políticas?", a L1) e, se o N5 passar, é a que vai para os humanos na fase 2: lá o dono humano
dá informação, e o desenho de gêmeos mede se o pet dele é reconhecível.

## 6. Decisões que só o Matheus pode tomar

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| A1 | Adotar esta arquitetura como alvo da V2 | Adotar como alvo, construída pela ordem N0 → N10 | Sem um alvo, cada nó vira mecânica solta; tudo de uma vez, nenhum gate isola o que funcionou |
| A2 | A L1 (dono avaliador, COACH) continua | Continuar até a validação, como braço de comparação do dono informante | Parar a L1 agora joga fora o único contraste direto com o resultado da v1 |
| A3 | Informação do dono entra pela percepção, nunca como reforço (D-A) | Sim | Como reforço, repete o desenho refutado |
| A4 | Valor instrumental sem o dono (D-B) | Sim, (1) | Com o objetivo do dono, o dono volta como recompensa |
| A5 | Um canal de reforço primeiro, o homeostático (D-C) | Sim | Três canais de uma vez impedem saber qual deles fez efeito |
| A6 | Pergunta de pesquisa nova (seção 5) no `PLANO_V2_PESQUISA.md` | Registrar como PROPOSTA ao lado da H1, decidir depois da validação da L1 | Trocar a pergunta antes da validação da L1 parece fuga de um possível negativo |
| A7 | CfC (NORNBRAIN) fora | Fora; registrar como hipótese concorrente | Adotar quebra o replay e a paridade |
| A8 | Pedir ao Claude Science a verificação das pistas (FlyWire, Fróes, Berto, Rossi, Sakabe, A.L.I.V.E., ALGA) | Sim, antes de qualquer texto que as cite | Citar pista como evidência é o erro que a revisão de literatura já bloqueou |
| A9 | Luta dentro do mesmo cérebro | Fora da fase de experimentos | Juntar os gambits do combate ao cérebro da vida muda o combate inteiro (gates V21C/V21D/V21E) |
