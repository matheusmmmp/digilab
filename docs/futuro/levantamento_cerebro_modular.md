# Levantamento do DigiBrain modular e o prompt da busca de referências (2026-11-07)

Estado: **IDEIA**, um levantamento sem tarefa. Feito pelo Gerente da V3 (Claude Code, Opus 5.5), a pedido do Matheus em 2026-11-07: "faça um levantamento de tudo que foi feito e os achados presentes no cérebro modular e as falhas, e daí gere um prompt para a gente efetuar uma busca por referências tanto acadêmicas quanto não".

A leitura foi feita na `main` `f866be29`. Cada afirmação cita o documento ou o arquivo de onde veio. Nenhum número é novo: todos estão nos `RESULTADO_*` citados. Onde há uma conta feita só neste levantamento, ela vem marcada.

O incômodo do Matheus, nas palavras dele, é o ponto de partida: o cérebro "ainda é muito simplista, tem poucas ações", "não representa ainda artificial life", "não sinto que tem órgãos", "não sinto que é um pet que está realmente pensando e agindo conforme os estímulos que ele tem dentro da rede neural dele".

## 1. O que o cérebro é hoje

### 1.1 Em uma frase

O modular é **uma rede de taxa pequena, em aritmética inteira (S = 1024), com os pesos inatos escritos à mão, três regras locais de aprendizado e um sorteio proporcional na escolha**.
- A própria espec diz que ele "não é uma rede treinada de ponta a ponta" e que as populações foram "desenhadas à mão" (`docs/ESPEC_DIGIBRAIN_MODULAR.md`, §2.6).
- Ele não tem camada oculta nem pulsos. A recorrência é uma só, pelo estado.

### 1.2 Os módulos (`digilab/digibrain/*.py`; o espelho em `web/app/motor/digibrain/*.ts`)

| módulo | o que faz | o que aprende |
|---|---|---|
| **M-SENS** | lê os receptores do corpo, a visão (até 8 objetos, raio de 6 células), a hora, o sono e o tempo sem cuidado | a habituação por classe de objeto (a novidade cai com a exposição) |
| **M-AFETO** | a urgência de cada receptor (a mesma curva para os 11); o sinal de recompensa `r` = a redução de Σ falta²; a valência V e a excitação E | V e E são médias móveis. A modulação do aprendizado pelo afeto (`modula_g_apr`) existe e está **desligada** |
| **M-ESTADO** | a intenção corrente, o compromisso C, a frustração F e a persistência | integradores simples |
| **M-IMPULSO** | soma, para cada unidade (comportamento, alvo), o inato + a proximidade + a novidade + o incentivo + o hábito + a memória + a persistência + a lembrança | nada; só soma |
| **M-ARB** | o peso de cada unidade mais a exploração (`g_exp`·ε), e um sorteio proporcional; o reflexo do sono com energia baixa | nada |
| **M-PLAST** | **P1:** um modelo do desfecho por classe × receptor (6 × 11). **P2:** hábito hebbiano de três fatores (7 × 23) | os dois aprendem pelo `r` |
| **M-MEM** | episódios de consumo e de visita; com a `memoria_autobio` (ligada no jogo): memórias recente (16), duradoura (32) e central (8), consolidadas uma vez por dia, e a lembrança na decisão | os episódios e a consolidação |
| **M-PERS** | três facetas de personalidade (cautela com a comida, apego ao dono, ousadia longe) | atrás de `facetas_mem`, **desligada** |
| **M-GEN / M-EXPR** | o registro dos 60 parâmetros inatos | o M-EXPR levanta `NotImplementedError`: o genoma não exprime nada ainda |

A ordem de cada decisão é SENS → AFETO → ESTADO → MEM → IMPULSO → ARB → ESTADO (`adapt.py`).

### 1.3 O tamanho (conta deste levantamento, pela config; não há contagem gravada, `docs/futuro/individualidade_pet.md`, §1)

| bloco | tamanho |
|---|---|
| os pesos inatos W0 | 7 × 23 = 161 posições, 33 não nulas |
| o hábito H (aprendido) | 7 × 23 = 161 |
| o modelo do desfecho P1 (aprendido) | 6 × 11 + 1 = 67 |
| a memória | 16 + 32 + 8 episódios |
| as facetas | 3 |
| os parâmetros inatos | 60 |

Para comparar: o cérebro A tem 54 nós e 831 posições de peso, das quais 203 não nulas no fim (`docs/futuro/connectome_cerebro_a.md`, §5). O #676 (`docs/TAREFA_V3_INDIVIDUALIDADE.md`) descartou escalar a rede, porque "o pet não usa a capacidade que já tem".

### 1.4 O repertório: 7 comportamentos

- **Os comportamentos:** `ocioso`, `dormir`, `comer`, `brincar`, `chamar_atencao`, `explorar` e `emburrar` (`COMPORTAMENTOS_DIGIBRAIN`, `digilab/config.py`). O `aliviar` (banheiro) existe no `AcaoPet`, mas o modular não o tem.
- **As unidades:** de 11 a 18 unidades (comportamento, alvo) por decisão, como comer a comida *id*, comer pelo cheiro, explorar o ponto lembrado e brincar com a bola.
- **Onde o tempo vai** (conta deste levantamento, sobre `artifacts_v3_acoes_novas/hoje.json`, 5 376 decisões do REL): dormir 43,9 %, explorar 29,0 %, chamar 17,2 %, comer 5,4 %, emburrar 1,8 %, brincar 1,4 % e ocioso 1,2 %.
- **A única ação nova tentada** foi o passeio, e ela falhou na guarda do comedouro (§2.2). Nenhuma ação nova chegou ao jogo.

### 1.5 O que o pet percebe

- **O corpo:** 11 receptores (fome, higiene, energia, humor, saúde, tédio, curiosidade, solidão, estresse, dor, susto), lidos a cada 15 ticks (96 decisões por dia).
  - O olfato, a audição, o paladar, a vontade e o conforto ficam **fora**: o M-SENS falha alto se algum deles aparecer (`sens.py`).
- **A visão:** até 8 objetos de 6 classes, com a proximidade linear e a novidade.
- **O cheiro:** o mundo tem intensidade e direção (`mundo.py`), mas o modular lê **só se há cheiro**, sem direção (regra G-SEM-DIRECAO).
- **O dono:** os gestos não entram como sinal; só chegam pelo efeito no corpo.

### 1.6 O corpo e os "órgãos" (`digilab/corpo.py`, `docs/DEFINICOES_CORPO_V2.md`, `docs/AUDITORIA_V2_PRODUTO_MODULAR.md`)

O corpo químico é bem mais rico que o que chega ao cérebro:
- **Os químicos:** cinco de falta, mais a digestão (o "órgão 1"), o relógio da Vida (o "órgão 2"), os drives novos, a dor e o susto, o metabolismo e o banheiro.
- **Os órgãos dos sentidos:** o Olfato e a Audição, com duas narinas e dois ouvidos, adaptação e saturação. Também há o Paladar.
- **Implementado, mas nenhum cérebro lê:** o órgão do Olfato, a Audição, a Vida e o **Digicorpo** (a rede de si, `digilab/rede_de_si.py`, um automodelo que só observa; a calibração deu margem negativa).
- **Não há hormônio no corpo.** "Hormônio" é só a inspiração dos ganhos `g_apr` e `g_exp` (espec §2.1, Cliff e Grand 1999).
  - A própria arquitetura registra: **"não existe a modulação da aprendizagem pela química"** (`docs/ARQUITETURA_DIGIBRAIN_MODULAR.md`, seção 2).
- **Proposto e nunca feito:** os hormônios H1 a H3; o reparo, a força vital e a morte por órgão (o J10); a termorregulação; o sistema imune.
  - A POC dos órgãos e da genética (#516) ficou como referência: seis genes, um estômago e um hormônio de saciedade, sem cérebro.
- **O genoma:** ele existe como registro no log (G0), mas "hoje nenhum gene muda as taxas do corpo" (`DEFINICOES_CORPO_V2.md`, 7.1).

### 1.7 A fala

- **O que a rede faz:** o decodificador de conceitos (DC1 a DC3d) tira 12 conceitos do motivo da decisão, por média ponderada inteira, sem treino, com pesos PROPOSTOS e SEM FONTE.
- **O que a LLM faz:** só a voz e a verificação.
- **O que a DC3 testou:** a rede escolhendo pedir (§2.2).

### 1.8 O que está ligado no jogo (v17 a v19, `web/app/src/produto.ts`, `motor/constantes.ts`)

- **Ligado:** o P1, o P2, o M-MEM, a persistência, o cheiro inato, a intenção pelo cheiro, a `memoria_autobio` (REL) e a ponte da luta.
- **Desligado:** `modula_g_apr`, `credito_corrida`, `redecidir_evento`, `intencao_suspensa`, `facetas_mem`, `passeio` e `fala_unidades` (esta só existe no pet de teste v16).

## 2. O que já foi testado

Todos os IC são de 95%. "R§n" é a seção n do `docs/RESULTADO_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md`.

### 2.1 V2: o cérebro A e o modular

| experimento | pergunta | resultado | leitura | fonte |
|---|---|---|---|---|
| J1, o mundo físico | a consequência imediata ensina a forragear? | o instinto ganha do aprendiz do A: −0,0097 [−0,0149; −0,0046] | falha | `RESULTADO_V2_VALIDACAO_MUNDO.md` |
| J1 com o alvo aprendido | o alvo aprendido ajuda? | −0,0063 [−0,0105; −0,0022] | o alvo atrapalha | `RESULTADO_V2_VALIDACAO_MUNDO_ALVO.md` |
| a revisão do aprendiz (A) | o gargalo é o teto, o crédito ou a exposição? | a decisão de comer não sabe qual fruta está ali | é desenho, não calibração | `RESULTADO_V2_REVISAO_APRENDIZ.md`, §4 |
| A × C | qual cérebro? | empate (CC-1 +0,016 [−0,017; +0,046]) | o A fica | `RESULTADO_V2_COMPARACAO_CEREBROS.md` (#197) |
| J5, o pet que pensa (A + planejador) | o modelo do desfecho revaloriza a escolha? | G-T1 0,197 [0,075; 0,323]; G-T2 −0,036 [−0,120; 0,024] | a revalorização passa; a transição é inconclusiva por premissa | `RESULTADO_V2_VALIDACAO_PET_QUE_PENSA_ADENDO8.md` (#370) |
| G-MVP (#420) | o modular fecha a cadeia comida → corpo? | 0,485 [0,475; 0,495] contra a meta ≥ 0,8; P2 −0,011 [−0,016; −0,008] | falha; o hábito sai ao contrário | R§Resumo |
| a reavaliação (#432) | quanto o protótipo fecha | 0,8083 por episódio, 0,4050 por ração | só estimativa | R§8 |
| L0 do "longe" | é percepção ou decisão? | decisão em 99,9 %; o reflexo do sono corta 80 % das buscas | aponta a L-2 | R§10 |
| L-2, a busca suspensa no cochilo | a busca sobrevive ao sono? | C-L2-1 cai só 28 % (pedia a metade) | negativa | R§12 (#454, #455) |

### 2.2 V3

| experimento | pergunta | resultado | leitura | fonte |
|---|---|---|---|---|
| C1, o "longe" regular | a memória ajuda com lugares fixos? | +0,0489 [+0,0355; +0,0624] no fixo | passa no fixo; indeterminado no sorteado | R§13 (#510) |
| D-C1-3 | de onde vem o ganho? | menos episódios perdidos para o sono (H3); **0 das 12 704 visitas acharam ração** | descritiva | R§13.6 a §13.7 (#640, #655) |
| C2, o crédito na corrida | o hábito ao contrário vem do crédito no passo? | +0,0028 [−0,0003; +0,0060] | ≈ 0: não é essa a causa | R§14 (#517) |
| C3, redecidir por evento | refazer a escolha só num evento ajuda? | +0,0124 [−0,0060; +0,0308] | indeterminado | R§15 (#527) |
| **C4, a memória autobiográfica** | lembrar pelo contexto melhora o episódio? | **REL − SEM +0,0646 [+0,0515; +0,0778]**; no sorteado −0,0223 [−0,0347; −0,0098] | **passa** (Holm rejeita os três); é o maior ganho da V3; as facetas dão ≈ 0 | R§16 (#541) |
| o passeio (AN4) | um vagar com destino move o pet sem custo? | movimento +0,0236; guarda do comedouro −0,0263 [−0,0362; −0,0164] | falha a guarda | `RESULTADO_V3_ACOES_NOVAS.md` (#584) |
| DC3, a rede escolhe falar | a fala aprende pela consequência? | +0,0212 [+0,0125; +0,0300] | passa, com ressalvas: sem a célula duplicada, fica perto de +0,005; a fala de fome nunca compensa | `RESULTADO_V3_CONVERSA_DC3.md` (#683) |

## 3. As falhas que se repetem e o diagnóstico dos próprios documentos

1. **Achar comida longe (0,41 só pelo cheiro, contra 0,74 no comedouro).**
   - O sono corta 80 % das buscas, e a busca retomada é cortada de novo em 86 % das vezes, porque passa pelo sorteio.
   - O M-SENS lê o cheiro sem direção nem intensidade.
   - Na mesma distância, o comedouro fecha 0,81 e o "longe" 0,52 (R§10, R§12.5; `RESULTADO_V2_DIGIBRAIN_MODULAR_DIAGNOSTICO.md`, §2).
2. **O hábito ao contrário** (M2 − M1 < 0 em cinco runs, de −0,011 a −0,018).
   - O crédito no passo foi descartado pela C2.
   - Fica a H-P2a: o termo do hábito sobe com a repetição, ganhe ou não ganhe. A corrida média tem só 1,5 decisão (R§14.4 a §14.6).
3. **O crédito com atraso.**
   - O P2 recebe a caminhada pelo cheiro decisão a decisão, sempre negativa, separada da refeição (o diagnóstico, §3.2).
   - Na DC3, o pedido de comida nunca compensa: a fome só cai depois que o pet anda até a ração, e o crédito acaba antes.
   - No A, a janela de crédito piorou (`RESULTADO_V2_REVISAO_APRENDIZ.md`, §2).
4. **O conflito entre vontades.**
   - O sorteio troca de meta cerca de 28 vezes por vida a mais que o controle (R§13.4).
   - A C3 cortou um terço das trocas sem efeito claro.
   - O passeio tira o pet do comedouro.
   - No A, o instinto decide 80 % das vezes.
5. **A persistência sem peso:** a G-PESA fica entre 0,0014 e 0,0035, porque o termo só existe em cerca de 3 % das decisões (R§6).
6. **A memória não acha nada no lugar lembrado:** as visitas são vazias em todas as runs. O ganho da memória vem de caminhos indiretos, e lembrar custa no mundo sorteado.
7. **A calibração nunca fechou:** os valores do #428 seguem PROPOSTOS, e os limiares estão SEM FONTE externa.

## 4. A distância até a proposta: o que o Matheus sente e o que o código mostra

| o incômodo | o que o código mostra |
|---|---|
| "é simplista" | uma soma ponderada linear com clamp: cerca de 400 números aprendidos e os pesos inatos à mão (§1.3) |
| "tem poucas ações" | 7 comportamentos; quase metade do tempo dormindo e um terço explorando (§1.4); a única ação nova testada falhou (§2.2) |
| "não sinto que tem órgãos" | o corpo tem órgãos, mas o cérebro só lê 11 receptores; o olfato, a audição, o paladar, a Vida e o Digicorpo não chegam a nenhum cérebro, e não há hormônio (§1.6) |
| "não está pensando conforme os estímulos de dentro" | o corpo entra só como entrada e como recompensa, **não como modulador**: "não existe a modulação da aprendizagem pela química"; não há planejamento no modular (o planejador do J5 é do A); a escolha é um sorteio sobre somas (§1.2) |
| "não representa artificial life" | o genoma não exprime nada (o M-EXPR está vazio); não há reprodução, morte por órgão, metabolismo que limite a vida nem evolução em curso; a ALife aparece no repositório como "escolha retórica, não afirmação apoiada" (`docs/referencias/revisao_alife_linhagem.md`, item 7) |

## 5. O que já se sabe e o que não se pode dizer

- **As referências verificadas:**
  - estão na skill `literatura-digilab` (`referencias.bib`, 72 entradas) e em `docs/referencias/*.csv`;
  - para o corpo e a ALife, valem Grand, Cliff e Malhotra 1997, Cliff e Grand 1999, Lewis e Cañamero 2016, Keramati e Gutkin, Seth e Friston 2016 e Dittrich, Ziegler e Banzhaf 2001;
  - para a emoção e a memória (a C0), valem Gadanho e Hallam 2001, a linha de Ho, Dautenhahn e Nehaniv, Khan e Cañamero 2018, Strannegård et al. e Giannakakis et al.
- **As alegações de novidade proibidas** (as regras 1 a 9 da skill e o `PLANO_V3.md`, 2.2): entre elas, juntar corpo, homeostase, aprendizado na vida e memória episódica (o Creatures fez em 1997); o planejamento por modelo aprendido (Dyna, MuZero); o corpo químico com órgãos.
- **O que se pode dizer:** "teste causal com braço de controle, num pet persistente, com replay determinístico".
- **A lacuna declarada:** não se achou trabalho com dano de órgão, cura com custo e morte por falência num agente que aprende. Os hormônios modulando a aprendizagem (H1 a H3) estão só propostos.

## 6. O prompt da busca

O texto abaixo é para colar numa ferramenta de pesquisa profunda: um agente com busca na web e em bases acadêmicas, ou a ferramenta de pesquisa que o Matheus preferir. Ele é autocontido.

---

> **Contexto.** Estou construindo um pet virtual com vida artificial: um projeto de pesquisa pessoal, jogável na web, com uma parte de pesquisa em Python. O pet tem:
> - **um corpo químico:** químicos de falta (fome, cansaço, tristeza, dano), digestão, metabolismo, relógio de vida, dor e susto, e órgãos dos sentidos com adaptação;
> - **um cérebro "modular":** uma rede de taxa pequena em inteiros, com pesos inatos escritos à mão;
> - **7 comportamentos:** dormir, comer, brincar, chamar o dono, explorar, emburrar e ocioso;
> - **as regras de aprendizado:** um modelo do desfecho por classe de objeto, um hábito hebbiano de três fatores pelo alívio homeostático e uma memória autobiográfica consolidada;
> - **a escolha:** um sorteio proporcional à soma ponderada de cada opção.
>
> Tudo é determinístico e refeito pelo log de eventos (event sourcing). Qualquer mecanismo novo tem que caber nisso: inteiros, sem treino de ponta a ponta, com replay bit a bit, e barato o bastante para rodar no navegador.
>
> **O problema.** O pet parece simplista e não parece "pensar" a partir do que sente por dentro:
> - **o corpo entra no cérebro só como entrada e como recompensa, nunca como modulador;**
> - não há hormônios;
> - os órgãos existem no corpo, mas o cérebro não os lê;
> - não há planejamento;
> - tem poucas ações, e quase metade do tempo ele dorme.
>
> Os experimentos com controle mostraram estas falhas:
> - **(1) busca distante:** o pet acha comida longe só pelo cheiro em 41 % dos episódios, contra 74 % no comedouro. O sono interrompe 80 % das buscas, e o cérebro não lê a direção do cheiro;
> - **(2) hábito:** o hábito aprendido piora o desempenho, porque reforça a repetição ganhe ou não ganhe;
> - **(3) crédito com atraso:** o aprendizado não liga um ato a uma consequência que chega minutos depois, como pedir comida e só comer depois de andar até ela;
> - **(4) vontades em conflito:** a escolha por sorteio troca de meta demais, e uma ação nova de passear tirou o pet da comida;
> - **(5) memória de lugar:** a memória de lugares ajuda, mas o pet nunca acha nada no lugar lembrado.
>
> O que já deu certo:
> - uma memória autobiográfica consolidada (+0,065 na taxa de fechamento de episódios de fome, com controle);
> - um modelo do desfecho que revaloriza a escolha quando o corpo muda.
>
> **O que eu quero.** Referências que ajudem a resolver essas falhas e a deixar o pet mais vivo:
> - um pet que aja a partir do estado interno;
> - com um repertório maior;
> - com órgãos e química que de fato modulem o cérebro;
> - com algum planejamento curto.
>
> Busque tanto a literatura acadêmica quanto a não acadêmica: jogos, palestras de desenvolvedores (GDC, postmortems), código aberto, documentação técnica, livros e blogs de quem construiu criaturas artificiais.
>
> **Eixos da busca.** Para cada eixo, traga de 3 a 8 referências.
>
> 1. **A neuromodulação e os hormônios que mudam a aprendizagem e a escolha:**
>    - a modulação química difusa em agentes artificiais;
>    - a dopamina, a serotonina, a noradrenalina e a acetilcolina como ganhos do aprendizado e da exploração;
>    - os modelos neuroendócrinos em robôs e criaturas;
>    - o "estado de fome muda o que a criatura percebe e valoriza";
>    - por exemplo, as linhas de Doya, Cañamero, Krichmar e Avila-García, e o Creatures.
> 2. **A interocepção e a alostase:**
>    - o corpo como fonte de previsão e de valor;
>    - o reforço homeostático;
>    - a inferência ativa aplicada a agentes simples e corporificados, em versões computáveis e baratas.
> 3. **O crédito com atraso em agentes que aprendem numa vida só:**
>    - os traços de elegibilidade;
>    - o aprendizado de três fatores com atraso (o problema do crédito distal na biologia e em redes de taxa);
>    - a representação de sucessores;
>    - as opções e as macroações;
>    - o hábito contra o comportamento dirigido a metas (a sensibilidade à desvalorização).
> 4. **O planejamento curto e barato:**
>    - modelo do mundo simples, Dyna e rollouts curtos;
>    - a recuperação de episódios para decidir (o controle episódico);
>    - a navegação por mapa cognitivo e as células de lugar em agentes simples;
>    - a busca dirigida pelo gradiente do cheiro (quimiotaxia, como no *C. elegans* e na *Drosophila*).
> 5. **A seleção de ação com vontades em conflito:**
>    - a arbitragem e a histerese entre comportamentos;
>    - o compromisso com a meta;
>    - os modelos de seleção de ação dos gânglios da base em agentes;
>    - a escada de Brooks e Bryson atualizada;
>    - as árvores de comportamento e a IA por utilidade com inércia, nos jogos.
> 6. **O repertório e os padrões fixos de ação:**
>    - como as criaturas artificiais e os pets ganham muitas ações sem explodir o espaço de escolha;
>    - os geradores de padrão central;
>    - as sequências de comportamento (o *behavior chaining*);
>    - as ações compostas;
>    - a etologia aplicada a pets virtuais.
> 7. **Os órgãos, o metabolismo e o ciclo de vida:**
>    - órgãos simulados com dano, cura e falência num agente que aprende;
>    - o metabolismo que limita a ação;
>    - o envelhecimento;
>    - a química artificial;
>    - os genomas que exprimem corpo e cérebro (do genótipo ao fenótipo, a codificação indireta);
>    - Creatures, Framsticks, Polyworld, Avida e Lenia, além dos sistemas mais recentes.
> 8. **Os cérebros pequenos de criaturas reais e artificiais que parecem "pensar":**
>    - os conectomas pequenos (*C. elegans*, a larva de *Drosophila*) e o que um circuito pequeno faz;
>    - as redes de tempo contínuo baratas (CTRNN, CfC/LTC);
>    - os "animats".
> 9. **A não acadêmica:**
>    - o desenho de criaturas em jogos: Creatures e o CAOS, Black & White, Spore, The Sims (o *motive*), Rain World (a IA das criaturas), Nintendogs, Tamagotchi, Dwarf Fortress e outros que você ache;
>    - as palestras e os postmortems;
>    - o código aberto (openc2e e outros);
>    - os blogs técnicos.
>
> **Regras.**
> - Só cite o que você conseguiu abrir.
> - Para cada referência, dê:
>   - a citação completa;
>   - o DOI, o ISBN ou o link estável;
>   - o tipo (artigo revisado por pares, livro, tese, preprint, palestra, código, blog, documentação de fã);
>   - se você leu o texto completo, o resumo ou só os metadados;
>   - em uma ou duas frases, **o que a referência mostra de fato** (o resultado, não a promessa);
>   - qual das falhas (1) a (5), ou qual eixo, ela ataca;
>   - como o mecanismo caberia num cérebro em inteiros, determinístico e sem treino de ponta a ponta, ou por que não cabe.
> - Separe o que tem evidência experimental (com controle) do que é só desenho ou relato.
> - **Não diga que algo seria novo ou inédito no meu projeto.** Já sei que a combinação corpo + homeostase + aprendizado + memória existe desde o Creatures (1997), e que o planejamento por modelo aprendido (Dyna, MuZero) não é novo.
> - Fonte de fã ou wiki vale só como pista, marcada assim.
> - Termine com uma lista curta, de no máximo 5 mecanismos, ordenada pelo que mais provavelmente ataca as falhas (1) a (5) com o menor custo. Para cada um, dê o teste com controle que mostraria se ele funciona.
>
> **Formato da saída.** Uma tabela por eixo, com as colunas `referencia`, `tipo`, `lido`, `o_que_mostra`, `falha_ou_eixo`, `como_caberia` e `doi_ou_id`. Depois, a lista dos 5 mecanismos.

---

## 7. Como usar o resultado

- **A verificação:** cada referência que voltar passa pela skill `literatura-digilab` antes de entrar em qualquer documento. Ela entra com o estado VERIFICADA só se a existência e o conteúdo forem conferidos.
- **Onde registrar:** numa tabela nova `docs/referencias/v3c5_referencias_verificadas.csv`, com as colunas de sempre (`referencia`, `tipo`, `verificada`, `o_que_sustenta`, `trilha`, `relevancia`, `doi_ou_id`).
- **O próximo passo** é uma triagem no molde da de 2026-10-30 (a C0, `docs/TAREFA_V3_LITERATURA.md`). Ela escolhe de um a três mecanismos e dá a cada um uma tarefa com plano, chave desligada e run única com controle. O Matheus escolhe.
- **Duas divergências para consertar na mesma rodada:**
  - `docs/TAREFA_V3_GENOMA_G0.md` usa Grand e Cliff 1998 para uma alegação de conteúdo, mas essa referência só tem metadados verificados. A fonte certa seria Cliff e Grand 1999 ou Grand, Cliff e Malhotra 1997.
  - A regra 6 da skill e a cópia na `main` divergem sobre Ackley e Littman.
