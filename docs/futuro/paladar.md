# Paladar — o gosto separado da nutrição (desenho)

Status (2026-10-13): **PROPOSTO**. Pedido do Matheus depois do #301 (o J5 voltou a ele porque o pet come a ração 72 a 82 vezes por vida e
quase nunca a fruta x). Não autoriza implementação sozinho: as decisões PL-1 a PL-9 (seção 9) são dele. O adendo do plano do J5 que usa
este desenho é o adendo 3 de `docs/PLANO_ANALISE_V2_PET_QUE_PENSA.md`.

**O pedido, nas palavras dele:** as frutas diferentes têm gostos diferentes, que atraem pets diferentes; a ração tem um gosto básico e
serve mais para a nutrição; o pet se sente mais atraído pela fruta de que gosta, como um animal se sente atraído por uma comida diferente
posta ao lado da sua ração.

**Regras deste desenho:**
- os números novos são PROPOSTOS, SEM FONTE, salvo onde citam um artefato ou o código;
- nada aqui diz que o pet sente prazer (F2, `docs/DEFINICOES_FRUTAS_V2.md`, seção 2.2): os nomes são de estímulo, de receptor, de
  escolha e de medida;
- nenhuma alegação de novidade.

## 1. Por que o pet só come ração (o diagnóstico do #301)

Tudo abaixo está no código da `main` (`digilab/config.py`, `digilab/mundo.py`, `digilab/policies/lobos.py`); nenhum número novo.

| peça | ração | fruta madura | o efeito |
|---|---|---|---|
| nutrição | `Config.ganho_alimentar` 0,45 | `ConfigMundo.nutricao_fruta` 0,15 | a ração mata 3 vezes mais fome |
| cheiro | `cheiro_racao` 64 | `cheiro_fruta` 32 | o cheiro puxa para a ração |
| onde está | no comedouro, deixada pelo dono todo dia, perto de onde o pet passa o dia | nas árvores, fora da casa | a ração está sempre perto |
| o que difere entre os tipos | — | só o efeito no humor (`efeito_frutas`) | a fruta só se distingue depois de comer, e pouco |
| a classe do alvo de comer | `comida` | `comida` | o hábito não distingue ração de fruta: o alvo padrão é a comida boa mais perto |

**O sinal da consequência** (`lobos.sinal_corpo`, o D = Σ falta² do N3) com a fome em 0,4 e o ganho 4: comer a ração leva a falta de
0,6 a 0,15, e a fruta de 0,6 a 0,45. A ração dá cerca do dobro do sinal da fruta, mesmo somando o humor que a fruta boa sobe. Não há
nada no mundo que torne uma fruta atraente antes de comê-la, nem depois, além do humor.

**O que o J5 precisa e não tem:** a G-APRENDEU pede que o pet escolha a x em mais de 1/3 das oportunidades antes da mudança. No piloto
foi 0 em todo braço (`docs/RESULTADO_V2_CALIBRACAO_PET_QUE_PENSA.md`). O pet come fruta (no piloto dos dois pets, o A sozinho comeu em
média 15 frutas maduras e 83 rações em 10 dias, `artifacts_v2_dois_pets/calibracao/`), mas nada o puxa para uma fruta específica.

## 2. O que já existe e o que não serve

- **O N4** (`digilab/frutas.py`) já separa gostar e querer: dois registros por fruta (`avaliacao`, `incentivo`), a preferência inata no
  genoma (`GenomaFrutas`, rng `frutas-ovo`, F5), a neofobia (F4) e a saciedade específica pelo consumo recente (2.3). Mas tudo em float,
  no motor (o motor escolhe a fruta pelo incentivo), no cenário de ofertas e fora do mundo físico. O `MotorMundo` não lê nada disso.
- **As restrições de `docs/DEFINICOES_FRUTAS_V2.md` continuam valendo** e este desenho as segue:
  - 2.1: gostar e querer são dois registros, e o gostar só chega à escolha por uma atualização declarada do querer;
  - 2.2: vocabulário de comportamento e medida;
  - 2.3: o gosto não lê a fome, e a saciedade de uma comida não mexe nas outras;
  - 2.4: a preferência inata é do genoma; o aprendido é estado e nunca é herdado.
- **O corpo** (`digilab/corpo.py`) já tem a forma que o paladar pede: químicos em [0, C], estímulos, meias-vidas, receptores na escala S e
  os órgãos com adaptação do #299 (o Olfato e a Audição). O cérebro só lê receptores.
- **O cérebro A** já tem os canais da consequência (CANAIS-REFORCO): o humor da fruta vai aos pesos que leem a identidade da fruta. O
  paladar acrescenta um canal ao lado.

## 3. Desenho proposto

### 3.1 O mundo: um perfil de gosto por tipo de comida

Cada tipo de comida do mapa ganha um **perfil de gosto**: um inteiro em [0, C] por **qualidade**. São quatro qualidades (PL-3): `doce`,
`azedo`, `amargo` e `salgado`. São nomes do estímulo, não da sensação do pet.

| tipo | doce | azedo | amargo | salgado | por quê |
|---|---|---|---|---|---|
| `a` | 3C/4 | C/4 | 0 | 0 | |
| `b` | 0 | 3C/4 | C/4 | 0 | as três frutas são a mesma forma girada: nenhuma é "a melhor" no mundo, só para um pet |
| `c` | C/4 | 0 | 3C/4 | 0 | |
| `racao` | 0 | 0 | 0 | C/4 | o gosto básico, numa qualidade só dela, fraca |

Todos os números são PROPOSTOS. A podre não tem perfil (o efeito dela segue o de hoje).

**O que não muda no mundo:** a nutrição (a ração continua 0,45 e a fruta 0,15), o cheiro, as árvores, as quedas, o apodrecer e o efeito
de cada fruta no humor (`efeito_frutas`). **O gosto não se vê nem se cheira:** o perfil só chega ao corpo quando o pet come (pelo `comer`,
pelo "achou e comeu" e pela fruta na mão). Antes de provar, o pet não sabe o gosto de nada.

**Como chega ao corpo:** o `estimulo_consumo_mundo` passa a levar o perfil do tipo comido. O motor do mundo não interpreta o perfil.

### 3.2 O corpo: o órgão do Paladar

Um órgão no grafo do corpo (como os do #299), atrás da sub-chave `paladar`. Por qualidade q:
- **`sabor_q`** (químico): ao comer, recebe e_q = max(0, perfil_q − `saciedade_q`), a parte do estímulo que a saciedade ainda deixa passar.
  Meia-vida curta (PROPOSTO 4 ticks): é o sinal na boca, que acaba antes da decisão seguinte;
- **`saciedade_q`** (químico): sobe a cada vez que o pet come, `k_sac` × perfil_q (PROPOSTO `k_sac` = ½, cortado em C), e cai com meia-vida
  longa (PROPOSTO 720 ticks, 12 h);
- **o receptor `paladar_q`** lê o `sabor_q` na escala S, como todo receptor.

É a saciedade sensório-específica por qualidade (2.3; Rolls, Rolls e Rowe 1983): comer muita ração satura o `salgado` e baixa a resposta
à ração, e não mexe na resposta ao `doce` de uma fruta. **É isto que põe a fruta "ao lado da ração" em vantagem:** a ração comida 8 vezes
por dia responde cada vez menos, e a fruta que o pet provou pouco responde inteira.

As qualidades compartilhadas generalizam: a `a` e a `c` dividem um pouco de `doce`, então comer muito `c` baixa um pouco a resposta à `a`.

As checagens do grafo valem como hoje (fechado, sumidouro, automantido, laço de ganho < 1). O estímulo da ingestão é um emissor externo,
e as meias-vidas são os sumidouros.

### 3.3 O genoma: o quanto cada pet gosta de cada qualidade

O gostar inato é um peso por qualidade, `h_q` em [−S, S], no genoma (PL-1, PL-2):
- **as frutas:** `h_doce`, `h_azedo` e `h_amargo` são sorteados por pet, com rng própria (`paladar-ovo`, derivada da semente do ovo; não
  toca o temperamento, o `GenomaFrutas` do N4 nem nenhuma outra rng), uniformes e independentes em [−S/2, S] (PROPOSTO);
- **a ração:** `h_salgado` é o mesmo para todos (PROPOSTO S/4): "o gosto básico";
- **o valor inato de um tipo para um pet** é Σ_q h_q × perfil_q / C. Como as frutas são a mesma forma girada e os h são independentes
  e de mesma distribuição, a fruta de maior valor inato é uniforme entre `a`, `b` e `c` sobre os pets.

Isso é a "fruta de que o pet gosta": pets diferentes gostam de frutas diferentes, e o mundo não tem uma fruta melhor.

**Herança e espécie:** o genoma do paladar é do indivíduo, como a preferência inata do N4 (F5). Quando a herança entrar na V2, o
`Genitor` leva os `h_q`. Quando o FE-3 decidir o perfil de cada brasão, a espécie dá a média dos `h_q` e a sensibilidade de cada receptor
(a camada 2 de `docs/futuro/fisiologia_especies.md`), e o indivíduo varia em volta (PL-2). O aprendido nunca é herdado (2.4).

### 3.4 O cérebro A: o gostar entra no sinal, o querer é aprendido

**O gostar é um canal novo do sinal, `gosto`**, ao lado dos drives (CANAIS-REFORCO):
- só nas decisões em que o pet comeu, f_gosto = div_arred(`ganho_gosto` × Σ_q div_arred(h_q × leitura de `paladar_q` depois, S), S);
- **não é homeostático:** não é a redução de uma falta, é a leitura do receptor depois de comer. Com isso, o gosto não lê a fome (2.3).
  A forma do Keramati e Gutkin (2014) cobre os drives; o termo do gosto fica fora dela, por desenho, SEM FONTE;
- a soma dos canais continua sendo o escalar, pela mesma soma telescópica (o contrato K-6), agora com o gosto como uma parcela a mais;
- o `ganho_gosto` é o único número do paladar que o plano do J5 calibra (PL-8).

**A rota do canal `gosto`:** aos pesos que leem a identidade da comida, os mesmos do canal do humor (a presença da fruta no mundo, #269)
e as classes novas abaixo. Nunca à tabela do corpo.

**O querer:** as classes de alvo do comer passam a distinguir o tipo (PL-5): `comida:racao`, `comida:a`, `comida:b` e `comida:c` no lugar
de `comida`, nas três regras em que o comer tem alvo (`pedido_necessidade`, `fome_moderada`, `fruta_no_cenario`). O prior é o de hoje: 0
em todas, e o alvo padrão do motor (a comida boa mais perto) tem o +1 do herdado. Aprendem pela consequência, como as classes de hoje,
agora com o canal do gosto. **É a atualização declarada que a 2.1 pede:** o gostar (a leitura do paladar pesada pelo genoma) só chega à
escolha por estes pesos e pelos de presença.

Assim, com a ração e uma fruta de que ele gosta à vista, o pet aprende a ir à fruta. Com fome alta, a nutrição da ração ainda pesa mais.
Com a fome baixa, o gosto decide.

**O que o cérebro não tem:** nenhum acesso ao perfil do mundo, ao genoma do paladar fora dos `h_q` do próprio sinal, à saciedade (só ao
receptor) nem ao tipo da comida antes de comer (o tipo da comida vista já vem na percepção de hoje; o gosto dela não).

### 3.5 O planejador

O modelo do desfecho (`digilab/modelo_mundo.py`) já aprende, por tipo, a mudança esperada de cada receptor ao comer. Com o paladar ligado,
os quatro `paladar_q` entram na lista de receptores, e o desfecho aprende o gosto de cada tipo do mesmo jeito que aprende a fome e o humor.
O valor de um tipo (o `valor_tipo` do planejador) passa a somar o termo do gosto com os mesmos `h_q` e o mesmo `ganho_gosto`. Nada mais
muda no planejador.

Na fruta na mão, o gosto chega ao corpo e ao modelo do desfecho, e nunca ao crédito do cérebro (a G-SEM-CREDITO de sempre).

### 3.6 A fala e o motivo

O fator do motivo que cita uma comida pelo tipo usa os nomes de escolha de hoje (`escolha_aprendida_fruta`, `plano_comida(b)`). Nenhum
texto novo diz que o pet acha gostoso. A F2 continua: "escolhi a vermelha de novo", nunca "adoro a vermelha".

## 4. A chave desligada é a vida de hoje

Três chaves, todas desligadas por padrão:
- **no mundo:** `ConfigPaladar.ligada` (os perfis e o estímulo com o perfil);
- **no corpo:** a sub-chave `paladar` da `ConfigCorpo` (o órgão; exige a do mundo);
- **no cérebro:** `ConfigLobos.paladar` (o canal e as classes por tipo; exige o corpo com o paladar).

Desligadas, nada existe: nenhum químico, receptor, peso, rng ou chave em `estado()`. O gabarito das vidas de hoje (o mundo físico com e sem
o corpo, os braços do J5, o metabolismo) é gravado num commit próprio **antes** de mudar o código, e um teste confere byte a byte.

**Os gates de mecanismo** (testes, só as sementes dos testes):
- **G2:** desligado, o gabarito byte a byte;
- **G1:** o replay refaz o corpo, os pesos e os modelos bit a bit;
- **G-INT:** tudo em inteiros (a AST, como no corpo);
- **G-GRAFO:** as checagens do grafo com o órgão, e tabelas feitas para falhar;
- **G-SSS:** comer a ração n vezes baixa a resposta ao `salgado` e não muda a do `doce`; sem comer, volta pela meia-vida;
- **G-FOME:** mesma saciedade e fome diferente dão o mesmo f_gosto;
- **G-RECEPTOR-PALADAR:** o cérebro só lê os receptores; mudar o perfil de um tipo que o pet não comeu não muda nada no cérebro;
- **a conta exata:** um consumo, um f_gosto e um passo nas classes por tipo, à mão;
- **G-SEM-CREDITO:** a fruta na mão não mexe nos pesos do cérebro.

## 5. As contagens

| o quê | sem o paladar | com o paladar | teto |
|---|---|---|---|
| pesos do cérebro A no P1 do J5 | 822 | 831 (+3 classes × 3 regras) | 1000 |
| inteiros do modelo do mundo (regime química) | 76 | 96 (+4 receptores × 5 tipos) | 200 |
| números no genoma por pet | — | 3 sorteados (`h_q` das frutas) | — |

Os `h_q` não são pesos aprendidos: são parâmetros do sinal, como os `pesos_drives_corpo`. **A rede de si** lê todos os receptores, e
quatro a mais podem passar do teto dela (como com os órgãos do #299); o B confere a contagem antes de ligar os dois juntos.

## 6. Quem faz cada etapa

| etapa | dono | o quê |
|---|---|---|
| 0 | cada dono, antes do código | o gabarito das vidas de hoje que a etapa toca, num commit próprio |
| 1, o mundo | **A** | `ConfigPaladar` (os perfis por tipo), o perfil no estímulo do consumo (`comer`, "achou e comeu" e a mão), os registros do consumo com o tipo; a chave e o G2 do mundo |
| 2, o corpo | **B** | o órgão do Paladar no grafo (`sabor_q`, `saciedade_q`, os receptores), o `GenomaPaladar` (rng `paladar-ovo`), a paridade do corpo (o gabarito do TS ganha a seção) |
| 3, o cérebro | **B** | o canal `gosto` no sinal e nos canais, as classes `comida:<tipo>`, os receptores no modelo do desfecho e no planejador, o motivo |
| 4, a bancada | **D** | o paladar nos braços do J5 (a chave, o genoma, a x como a favorita), as medidas descritivas da seção 7, as faixas de sementes do adendo 3 |
| 5, a web | **A** | o porte para o TS (mundo e corpo, como `mundo.ts` e `corpo.ts`), só motor e paridade, depois que a pesquisa usar o paladar |

## 7. O que medir (descritivo, para a bancada)

- os consumos por tipo e por dia, e a fração de fruta entre os consumos no mundo;
- a leitura de cada `paladar_q` em cada consumo, e o f_gosto;
- a saciedade da ração contra o número de rações nas últimas 12 h (o G-SSS numa vida);
- os pesos das classes `comida:<tipo>` no fim de cada dia;
- o valor inato de cada tipo para o pet (do genoma) contra o que ele mais come.

## 8. Riscos

| # | risco | o que o desenho faz |
|---|---|---|
| RP-1 | **o gosto vira o novo vício:** o pet come só a fruta favorita e passa fome | a ração continua 3× mais nutritiva; com fome alta o sinal da nutrição domina; a saciedade sensório-específica derruba a fruta comida demais. A privação é medida, e o `ganho_gosto` se calibra por uma faixa (PL-8) |
| RP-2 | **o pet nunca prova a fruta** e o gosto não age | ele já come cerca de 15 frutas em 10 dias; o "achou e comeu" do explorar continua. Se não bastar, o dono pôr a fruta ao lado da ração é uma peça a mais, fora deste desenho (seção 10) |
| RP-3 | **a x ganha por gosto e o T1 não reverte:** a fruta continua gostosa depois de fazer mal | a premissa mecânica G-REVAL-POSSIVEL do adendo 3 confere nos números que o valor verdadeiro da x depois da mudança fica abaixo da melhor alternativa |
| RP-4 | **gostar e querer se confundem na medida** | as medidas ficam separadas (Finlayson e Dalton 2012): a leitura do receptor no consumo (o gostar) e a escolha numa oportunidade (o querer) |
| RP-5 | **os `h_q` independentes** contradizem traços correlacionados (Sih, Bell e Johnson 2004) | é uma simplificação declarada; a espécie (FE-3) pode pôr a correlação depois |
| RP-6 | **a palavra "paladar" ou "gosto" na tela** faz o jogador ler sensação | a F2 continua: os textos falam de escolha |

## 9. Decisões do Matheus

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| PL-1 | Onde mora o gostar | **receptores do paladar no corpo, e o peso de cada qualidade (`h_q`) no sinal do cérebro**, como os pesos dos drives. Sem químico de prazer | um químico "hedônico" no corpo (o caminho do Creatures) põe o gostar numa quantidade que a rede de si e o planejador tratam como drive, e pede um nome que a F2 proíbe. Sem receptor nenhum, o cérebro teria de ler o perfil do mundo, que é estado de fora |
| PL-2 | A preferência é por indivíduo ou por espécie | **por indivíduo**, no genoma com rng própria (como a F5 do N4); a espécie dá a média quando o FE-3 for decidido; herdável quando a herança entrar na V2 | só por espécie: no J5 sem genoma todo pet gosta da mesma fruta, e a x deixa de ser sorteada; o FE-4 (variação individual na fase 3) fala da fisiologia, e a preferência já é individual desde a F5 |
| PL-3 | Qualidades ou um número por fruta | **quatro qualidades** (doce, azedo, amargo, salgado), a ração numa só, as frutas como a mesma forma girada | um número por tipo é mais simples, mas o corpo teria de saber o nome da fruta (um estado do mundo), a saciedade não generaliza e a espécie não tem onde mexer |
| PL-4 | A saciedade sensório-específica | **sim, por qualidade**, com meia-vida de 12 h | sem ela, o pet que gosta da fruta come só ela (RP-1), e a ração "ao lado" nunca perde atração por ser repetida |
| PL-5 | O querer | **aprendido**: as classes `comida:<tipo>` com prior 0, pelo canal do gosto. Nenhuma atração inata antes de provar | atração inata pela fruta vista: o pet "gosta" sem nunca ter provado, e o gostar e o querer viram o mesmo número (contra a 2.1) |
| PL-6 | O gosto lê a fome | **não** (2.3) | lendo a fome, o gosto vira mais um drive e a saciedade específica se confunde com a fome geral |
| PL-7 | A neofobia (F4) no paladar | **não agora**; entra com chave própria se o J5 pedir | com ela agora, o primeiro contato com a fruta atrasa e o J5 perde exposição |
| PL-8 | Que número se calibra | **só o `ganho_gosto`**, no J5, por uma faixa da fração de fruta entre os consumos, sem ler a x nem as primárias (adendo 3); os perfis, os `h_q`, o `k_sac` e as meias-vidas ficam PROPOSTOS | calibrar tudo: muitos pontos e o risco de ajustar a favor da premissa |
| PL-9 | A ordem | **o paladar inteiro (etapas 1 a 4) antes de qualquer run do J5**; a web depois | ligar só o mundo e o corpo: o cérebro não lê o gosto, e o J5 falha pela mesma razão do #301 |

## 10. Fora deste desenho

- **O dono pôr a fruta ao lado da ração** (um gesto novo, `deixar_fruta_<f>`): muda o orçamento e o dono. Só se o RP-2 acontecer.
- **A aversão gustativa aprendida** (Bernstein 1999): comer algo e passar mal mudaria o gosto (o receptor) daquele tipo. Aqui, o mal-estar
  muda só o humor, e o desfecho aprende o humor. Fica para um desenho próprio, com a doença e o remédio (`docs/futuro/doenca_remedio.md`).
- **O gosto mudado pela exposição longa** (Beauchamp e Moran 1982): aqui a exposição só mexe na saciedade, de horas.
- **O cheiro por tipo** (o Olfato do #299 cheira "comida", sem tipo): a atração pelo cheiro da fruta favorita fica para depois.
- **O combate e o jogo web:** o combate não muda (FE-5); a web recebe o porte só depois da pesquisa.

## 11. Referências

Só as verificadas em `docs/referencias/*.csv`. A verificação foi sobre metadados e resumo; nenhuma foi lida em texto completo.

| referência | DOI | quanto foi lido | o que sustenta aqui |
|---|---|---|---|
| Berridge e Robinson (1998). Brain Res Rev | `10.1016/s0165-0173(98)00019-8` | resumo | gostar, querer e aprender são componentes separados: o receptor e o canal (gostar) longe das classes (querer) |
| Berridge, Robinson e Aldridge (2009). Curr Opin Pharmacol | `10.1016/j.coph.2008.12.014` | resumo | idem, revisão curta |
| Morales e Berridge (2020). Physiol Behav | `10.1016/j.physbeh.2020.113152` | resumo | a separação vale para a comida em particular |
| Berridge (1996). Neurosci Biobehav Rev | `10.1016/0149-7634(95)00033-b` | resumo | não inferir prazer do comportamento (F2) |
| Finlayson e Dalton (2012). Appetite | `10.1016/j.appet.2011.10.011` | resumo | medir gostar e querer com instrumentos separados (seção 7, RP-4) |
| Rolls, Rolls e Rowe (1983). Physiol Behav | `10.1016/0031-9384(83)90003-3` | resumo | o quanto uma comida agrada cai mais para a comida comida do que para as outras: a saciedade por qualidade (3.2) |
| Rolls et al. (1981). Physiol Behav | `10.1016/0031-9384(81)90310-3` | título e metadados | que o fenômeno foi estabelecido em humanos |
| Beauchamp e Moran (1982). Appetite | `10.1016/s0195-6663(82)80007-x` | título e metadados | preferência inata modulada pela exposição (só a parte inata é usada) |
| Sclafani (2001). Appetite | `10.1006/appe.2000.0370` | resumo | há controles pós-ingestivos positivos: a nutrição da ração continua ensinando, pelo canal de sempre |
| Blusk, Ackroff e Sclafani (1992). Appetite | `10.1016/0195-6663(92)90038-8` | título e metadados | o sinal oral e o da consequência se separam: os dois canais, gosto e nutrição |
| de Araujo et al. (2008). Neuron | `10.1016/j.neuron.2008.04.003` | título e metadados | a consequência sozinha basta para condicionar preferência: a ração pode continuar preferida com fome |
| Balleine (2008). Conditioned Taste Aversion, cap. | `10.1093/oso/9780195326581.003.0013` | resumo | o valor do desfecho é aprendido e ligado ao gosto: o desfecho do planejador aprende o gosto por tipo |
| Bernstein (1999). Nutrition | `10.1016/s0899-9007(98)00192-0` | resumo | a aversão gustativa é aprendizado próprio: fica fora (seção 10) |
| Keramati e Gutkin (2014). eLife | `10.7554/elife.04811` | resumo | a recompensa dos drives como redução de desvio; o termo do gosto fica fora dessa forma (3.4) |
| Grand e Cliff (1998). Auton Agents Multi-Agent Syst | `10.1023/a:1010042522104` | título e metadados | um pet com bioquímica artificial, emissores e receptores; nenhuma afirmação sobre gosto |
| Sih, Bell e Johnson (2004). Trends Ecol Evol | `10.1016/j.tree.2004.04.009` | resumo | traços vêm correlacionados (RP-5) |

**SEM FONTE:** as quatro qualidades, os perfis, a forma girada das frutas, os `h_q` e a distribuição deles, o `k_sac`, as meias-vidas, o
`ganho_gosto`, o gosto como canal não homeostático e qualquer precedente de preferência alimentar em vida artificial (nenhum verificado).

## 12. Etapas 0 e 2 feitas: o corpo (2026-10-14, worker B) — GATES PASSAM

PL-1 a PL-9 pela recomendação (Matheus, 2026-10-13). Sem run; só as sementes dos testes. Não há `TAREFA_V2_PALADAR.md`; o resumo fica
aqui. Interpretações em `docs/REGISTRO_DESVIOS.md`.

- **O gabarito antes do código** (commit próprio): `tests/gabarito_paladar.py` → `tests/gabaritos/paladar_vidas_de_hoje.json`, gravado com
  a `main` d0755c8. Contém o mundo físico com e sem o corpo (as vidas, os grupos e o corpo sozinho do gabarito dos órgãos) e os braços do
  J5 (P1 e P1-plan, T1 e T2, sementes 101 e 202).
- **A sub-chave `ConfigCorpo.paladar`** (desligada; exige `ligada` e o mundo físico). Os números são PROPOSTOS e estão no registro
  `PARAMETROS_CORPO`:
  - as meias-vidas: `meia_vida_sabor` 4 e `meia_vida_saciedade` 720, com as k da regra da seção 3;
  - o `k_sac`: `saciedade_num`/`saciedade_den` = ½;
  - o genoma: `paladar_h_min` −S/2, `paladar_h_max` S e `paladar_h_salgado` S/4.
- **O órgão (seção 3.2):**
  - os químicos: por qualidade, `sabor_q` (receptor `paladar_q`, a concentração) e `saciedade_q` (sem receptor);
  - no grafo: um emissor de estímulo `paladar:q` por qualidade, que lê a saciedade com sinal −1 (nenhum laço);
  - ao comer (`Corpo.estimulo_gosto`): o sabor recebe max(0, perfil_q − saciedade_q), e a saciedade sobe div_arred(perfil_q · num, den);
  - `estimulo_consumo_mundo(..., perfil=)` leva o perfil da comida madura; a podre não tem perfil. Um perfil sem a sub-chave falha alto, e
    a madura sem perfil também.
- **O genoma** (`digilab/genoma_paladar.py`): `GenomaPaladar` e `genoma_paladar(semente)`, com a rng `paladar-ovo` e um `randint` por
  qualidade das frutas (doce, azedo, amargo). O `h_salgado` é fixo. Ele dá o `valor_inato` e a `favorita` (o PJ-1).
- **O motor do corpo:**
  - no mapa, o perfil vem do `ocorrido["comeu"]["perfil"]` do mundo; na fruta na mão, do `cpal.perfis`. É o contrato combinado com o A
    (o lado do mundo dele, `ConfigPaladar` e `MotorMundo.cpal`, entrou na `main` pelo #309);
  - o corpo com o paladar exige o `cpal.ligada`; os receptores vão à `PercepcaoCorpo`.
- **A paridade:** o gabarito do corpo ganhou a seção `paladar`, e as outras saíram idênticas. A `config` ganhou os campos novos, com o
  espelho em `web/app/motor/constantes.ts`. O `configCorpo` do TS falha alto com o paladar ligado: o órgão em TS é a etapa 5, do A.
- **Gates** (`tests/test_paladar_corpo.py`, 30):
  - **G2;**
  - **a conta exata** de um consumo e das meias-vidas;
  - **G-SSS;**
  - **a generalização** pelas qualidades compartilhadas;
  - **G-FOME;**
  - **G-GRAFO,** com as tabelas feitas para falhar;
  - **G-INT;**
  - **o genoma:** a rng própria, a faixa e a favorita uniforme em 900 pets;
  - **as falhas altas do motor;**
  - **a fruta na mão;**
  - **G1,** com um lado do mundo de teste.
- **Achado (só nos números PROPOSTOS):** com o perfil C/4 e o `k_sac` ½, a ração satura rápido.
  - Da 4ª ração seguida (uma por decisão) em diante, o `salgado` quase não responde.
  - Com 8 rações, a saciedade passa de 3C/4, e a ração só volta a responder perto de duas meias-vidas depois (~24 h).
- **As contagens:**
  - **a rede de si** lê os 4 receptores a mais: com a química vai de 359 a 703 pesos, com a etapa 6 de 911 a 1399 e com o banheiro de
    1143 a 1679. Nos dois últimos casos passa do teto dela;
  - **o cérebro A** ainda não lê o paladar (a etapa 3).
