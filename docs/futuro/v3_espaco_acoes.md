# DigiBrain V3: o espaço de ações e as oportunidades de escolha do pet

Status (2026-10-19): **PROPOSTO.** É uma investigação de arquitetura (`docs/TAREFA_V2_V3.md`), com medições descritivas. Não muda o cérebro A,
o `digilab/`, o `AcaoPet`, o bandit, o v11 nem a web. Não é run de pesquisa: as vidas usam só as sementes dos testes (101…505), sem plano,
gate nem intervalo. O desenho do V3 do E0 (`docs/futuro/digibrain_v3_e0.md`) continua PROPOSTO, e as decisões V3-3 e V3-4 são do Matheus
(seção 8).

**As marcas deste documento:**
- **[IMPLEMENTADO]:** está no código da `main`, com teste;
- **[OBSERVADO]:** vem de uma medição descritiva com artefato em disco. Não é resultado de pesquisa nem prova de melhora;
- **[HIPÓTESE]:** é leitura nossa, SEM FONTE, a testar;
- **[PROPOSTA]:** é desenho, e cabe ao Matheus decidir.

**A medição:** `python experiments/medir_v3_espaco_acoes.py` grava `artifacts_v2_v3/espaco_acoes.json` (sha256 `ea30478b…`), igual em duas
execuções. O teste é `tests/test_medir_v3_espaco_acoes.py`. São três partes:
- **o v11:** as mesmas 20 vidas do E0 (4 donos × 5 sementes dos testes, 14 dias, 26.880 decisões; o braço `P1-c-tapa` do gabarito da web);
- **o mundo físico:** 20 vidas de 4 dias do `P1-alvo` do MUNDO-ALVO, na config da fumaça dele;
- **o J5:** 10 vidas do T1, o P1 e o P1-plan, com a config da fumaça do piloto do adendo 7, a duração do piloto (7 + 5 dias) e as
  sementes dos testes.

A medição só lê o que a política registra. Para o crédito, ela embrulha o `_aplicar_sinal` do cérebro durante a medida. O embrulho chama o
original, e a vida com ele é a mesma: o sha do estado interno é conferido contra a vida sem o embrulho.

## 0. Resumo

A hipótese do Matheus ("poucas ações atrapalham o aprendiz") separa-se em quatro limites diferentes. O E0 e esta medição mostram que eles
não pesam igual:

| limite | o que é | o que a medição mostra [OBSERVADO] |
|---|---|---|
| **falta de alternativa** | a ação só existe numa regra que não oferece outra | `dormir` só aparece nas três regras de sono, e `emburrar` só no abandono, que oferece um candidato por decisão. `comer` só aparece na fome moderada (2,2% das decisões) |
| **prioridade fixa** | outra regra também valia, mas a ordem do instinto fechou a decisão | em **34,5%** das decisões forçadas outra regra urgente também valia. Em 32,1% delas, a união dos candidatos urgentes teria mais de uma ação |
| **subdecisão (o alvo)** | o pet escolhe para onde ir dentro da ação | no mundo físico, comer tem 1,65 classes de alvo em média, com escolha em 55,6% das decisões, e explorar tem 2,75, com escolha em 100%. O alvo aprendido saiu do padrão do motor em 1,4% (comer) e 18,1% (explorar) |
| **limite do crédito** | a regra da L1 não aprende com um candidato só | **nenhuma das 2.658 aplicações de crédito em decisões forçadas mudou um peso**, e elas levam 45,9% do \|sinal\|. Nas decisões com escolha, 93,6% mudaram |

**A leitura** [HIPÓTESE]: o que mais limita é a arbitragem (a prioridade fixa e o crédito perdido nela), e não o número de verbos. Somar
ações ao enum sem abrir a arbitragem acrescentaria opções que o pet quase nunca chega a escolher. O J5 mostra um quinto limite, que não é de
ações: o crédito do "querer" soma canais que se compensam (seção 3).

## 1. O inventário: o que o cérebro A pode escolher hoje [IMPLEMENTADO]

**As ações:**
- `ACOES_PET_HOJE` (`digilab/events.py`) tem sete: `ocioso`, `dormir`, `comer`, `brincar`, `chamar_atencao`, `explorar` e `emburrar`;
- o `aliviar` (`AcaoPet.ALIVIAR`) só existe com o banheiro (`ConfigBanheiro`), no mundo físico;
- **a tarefa não deixa acrescentar membros ao `AcaoPet`:** o bandit congelado e a reprodução da v1 dependem dele.

**As regras do instinto** (`PoliticaInstinto.agir`, `digilab/policy.py`), na ordem; a primeira que vale decide:

| regra | condição | candidatos | no v11 (fração das decisões, E0) |
|---|---|---|---|
| `sono_exaustao` | energia < 0,25 | dormir | 2,2% |
| `sono_continuar` | dormindo e energia < 0,85 | dormir | **34,6%** |
| `sono_noite` | noite e energia < 0,55 | dormir | 2,7% |
| `pedido_necessidade` | fome ou higiene < 0,25 | chamar | 7,0% |
| `abandono` | sem cuidado há mais de 240 ticks | emburrar (humor < 0,35) **ou** chamar: um por decisão | 8,8% |
| `fome_moderada` | fome < 0,45 | comer, chamar | 2,2% |
| `tempo_livre` | o resto | ocioso, explorar, brincar, chamar | 42,5% |

- **O prior do cérebro** (`PoliticaLobos._prior`) tem uma linha por (regra, ação). As linhas com algum peso não nulo são as ações que a
  regra pode oferecer. No abandono são duas linhas, mas o instinto oferece uma por decisão, pelo humor.
- **No mundo físico** entram mais duas regras, `bola_no_cenario` e `fruta_no_cenario`. Nele, `pedido_necessidade` também oferece comer
  quando há para onde ir, e o banheiro acrescenta o `alivio_urgente` e o `aliviar` no tempo livre (o inventário completo está no artefato,
  `inventario`).
- **As ações com alvo** (`ACOES_COM_ALVO_MUNDO` e o aliviar):
  - **explorar:** cheiro, vagar, casa, continuar, seguir, onde comeu e, no J5, as árvores;
  - **comer:** comida, comida podre, cheiro, continuar e, com o paladar, `comida:<tipo>`;
  - **brincar:** bola, continuar;
  - **aliviar:** banheiro, aqui.
- **O alvo** é aprendido por classe (`alvo_aprendido`), nas regras de `REGRAS_ALVO`, com prior w0 e +1 na classe do padrão do motor. É
  uma subdecisão que já existe.

## 2. Os quatro limites, separados

### 2.1 A falta de alternativa

- **[IMPLEMENTADO]:** `dormir` só é candidato nas regras de sono. `emburrar` só no abandono, e só com o humor abaixo de 0,35. `comer` só na
  fome moderada (no mundo físico, também com a fruta no cenário e no pedido com para onde ir).
- **[OBSERVADO]** (`acoes_por_frequencia`): 10.604 `dormir`, todas forçadas, e 157 `emburrar`, todas forçadas.
- **O que isto significa:** em nenhum momento o v11 escolhe dormir contra outra coisa, ou emburrar contra outra coisa. Para essas ações, o
  aprendiz não tem como aprender quando fazê-las. O problema não é a quantidade de ações: elas existem, mas só aparecem sozinhas.

### 2.2 A prioridade fixa

**[OBSERVADO]:** em cada decisão, a medição refaz todas as regras cuja condição vale, pela mesma conta do instinto. A primeira na ordem é
sempre a regra registrada (conferido nas 26.880 decisões e em 20.000 observações aleatórias contra o `PoliticaInstinto`).

| regra forçada | fração do total | outra regra urgente também vale | quais | união dos candidatos urgentes (média) |
|---|---|---|---|---|
| `sono_continuar` | 34,6% | 27,3% | fome moderada 17,2%, pedido 10,6%, abandono 10,4%, noite 4,4% | 1,43 |
| `abandono` | 8,8% | 40,2% | fome moderada | 1,44 |
| `pedido_necessidade` | 7,0% | 70,9% | fome moderada 69,3%, abandono 35,9% | 1,83 |
| `sono_noite` | 2,7% | 23,1% | abandono 13,1%, fome moderada 12,5%, pedido 9,6% | 1,37 |
| `sono_exaustao` | 2,2% | 22,5% | fome moderada, pedido, abandono, continuar | 1,31 |

- **No total das decisões forçadas,** outra regra urgente também valia em **34,5%**. A união dos candidatos urgentes teria mais de uma
  ação em **32,1%**, e, contando o tempo livre, teria 5,0 ações em média.
- **A leitura** [HIPÓTESE]: um terço das decisões forçadas tem uma competição real entre necessidades (por exemplo, dormindo e com fome
  moderada), que a ordem fixa esconde. Os outros dois terços são forçados porque só uma necessidade está ativa. Abri-los significaria
  deixar o tempo livre competir com a regra urgente, o que é outra decisão de desenho (seção 5, a forma do R1).

### 2.3 Os objetivos e as subdecisões

- **[IMPLEMENTADO]:** no mundo físico, comer, explorar e brincar têm alvo, e o alvo aprendido escolhe a classe. Na pesquisa, isto é o J1
  (o mundo físico) e o #296 (o alvo aprendido).
- **[OBSERVADO]** (`mundo_fisico.subdecisoes`; 4 dias, P1-alvo, as sementes dos testes):
  - **comer:** 3,29 candidatos e 1,65 classes em média; mais de uma classe em 55,6% das decisões; o alvo fora do padrão em 1,4%;
  - **explorar:** 2,75 classes; mais de uma em 100%; o alvo fora do padrão em 18,1%;
  - **brincar:** sem a bola no mapa, quase nunca tem alvo.
- **O que já se sabe:** o alvo aprendido **atrapalhou** na validação do MUNDO-ALVO (−0,0063 em `D_FE`, `docs/RESULTADO_V2_VALIDACAO_MUNDO_ALVO.md`).
  Subdecisão existe e é usada; o que ela não fez foi melhorar o desempenho.

### 2.4 O limite do crédito

- **[IMPLEMENTADO]:** a regra da L1 (`atualizar_pesos`, `lobos.py`) multiplica cada passo por `S·1[a = a*] − P_a`. Com um candidato só, `P` é
  S e o fator é zero.
- **[OBSERVADO]** (`v11.credito`):
  - **as decisões forçadas:** 2.658 aplicações de crédito e **0** com algum peso mudado. Elas levam **45,9% do |sinal|**;
  - **as decisões com escolha:** 19.402 aplicações, com o peso mudado em 93,6% (o resto tem sinal zero).
- **Por regra:**
  - o tempo livre e a fome moderada mudam o peso em 93,3% e 99,8% das aplicações;
  - todas as regras de um candidato, em 0%.
- **Por dono:** a fração do |sinal| perdida nas forçadas é 35% (incoerente), 45% (atencioso), 46% (aleatório) e **54% (relapso)**. O pet
  negligenciado perde mais da metade da consequência que sente.
- **A diversidade por contexto** (`por_regra`):
  - no tempo livre, a entropia da política na decisão cai de 1,87 bit (o prior) para 1,46 bit, e a das ações feitas é 1,78 bit;
  - na fome moderada, de 1,00 para 0,27 (o aprendido concentra no comer).

  O aprendiz deixa a escolha **menos** diversa onde aprende, como se espera de quem aprende. Diversidade bruta não é a meta (seção 6).

## 3. A ligação com o J5

**O que se sabe** (`docs/RESULTADO_V2_PILOTO_PET_QUE_PENSA_ADENDO7.md`, 20 unidades, só descritivo):
- o pet aprende a preferir a x: `f_antes` 0,55 no P1 e 0,67 nos braços com o planejador;
- no P1 a escolha não cai depois que a x passa a fazer mal (0,55 → 0,62);
- com o planejador cai: 0,67 → 0,46.

**O que esta medição acrescenta** [OBSERVADO] (`j5`; 5 vidas por braço, as sementes dos testes):

| | P1 | P1-plan |
|---|---|---|
| x comida pela própria decisão, antes / depois da mudança | 39 / 36 | 54 / 31 |
| x recebida na mão (não credita a política: G-SEM-CREDITO) | 10 | 10 |
| o sinal das decisões em que comeu a x depois da mudança: os drives / o gosto (média) | −87 / +66 | +111 / +83 |
| a soma das classes `comida:x` do alvo desceu (vidas) | 4 de 5, pouco: de −594 a −607, de 2694 a 2547, e numa subiu de 212 a 1520 | 3 de 5 |
| o humor previsto da x no modelo do desfecho desceu | — | 5 de 5 (de +10 a −32, de +9 a −88…) |

**A leitura** [HIPÓTESE]:
- **Não falta oportunidade de crédito ao P1.** Ele come a x por conta própria 36 vezes depois da mudança.
- **Falta a forma do crédito:**
  - a classe do alvo aprende com o sinal inteiro da decisão. Nele, o gosto da x (+66) compensa boa parte da perda no humor e nos drives
    (−87);
  - cada consumo move a classe pouco perto do que ela acumulou antes. O "querer" aprendido é lento para desaprender.
- **O planejador revaloriza por outro caminho:** o modelo do desfecho guarda o humor por tipo, separado do gosto, e aprende também com a
  mão. O termo do plano entra na escolha. **O limite do J5 não é de número de ações.** É de onde o crédito vai: um canal só por decisão,
  somado, num peso que só a própria escolha move.
- **Para o V3,** isto pesa a favor de um crédito por canal até o alvo (o humor separado do gosto). Não pesa a favor de mais verbos.

**Correção (2026-10-19, o desenho da V3-9, `docs/TAREFA_V2_V3_CREDITO_CANAL.md`, seção 0):**
- **As 36 vezes depois da mudança são reexperiência.** Ficam fora da janela que o T1 conta, que para no primeiro consumo da x no mapa. A
  x na mão não credita o A. Por isso, no T1 como está, um crédito que só aprende com a própria escolha não muda nada; o teste da V3-9 é o
  da reexperiência.
- **Separar por canal e ler pela soma dá o peso de hoje,** porque a regra da L1 é linear no sinal. É preciso uma peça a mais (a decisão
  CC-1).
- **"O planejador revaloriza" vale para o piloto do adendo 7.** No do adendo 8, a escolha da x não cai com o planejador (0,52 → 0,55 a
  0,68).

**Correção (2026-10-21, a etapa 0 da V3-9, `docs/TAREFA_V2_V3_CREDITO_CANAL.md`, seção 10):** no crédito à x depois da mudança, quem
compensa a queda do humor (−364 por crédito) é a nutrição (+281), e não o gosto (+56) (`artifacts_v2_v3/credito_canal_etapa0.json`, o J5
do adendo 8). Nenhum peso de comer chega ao teto do J5 (16·S).

## 4. As três direções, comparadas [PROPOSTA]

| direção | o que muda | que limite ataca | o que fica de fora | risco |
|---|---|---|---|---|
| **(a) mais ações primitivas** | verbos novos | a falta de alternativa (2.1), só se o verbo novo aparecer junto com outros | não pode ser membro novo do `AcaoPet` (a tarefa e o roadmap). Exigiria um espaço de ações do V3 à parte, com tradução para o motor | verbos que só aparecem numa regra forçada repetem o `dormir`: existem e nunca são escolhidos |
| **(b) abrir a competição** (R1 do E0) | as regras urgentes que valem viram candidatos num sorteio comum, com o termo do instinto como prior forte; o `sono_exaustao` fica forçado | a prioridade fixa (2.2) e o crédito perdido (2.4) | não cria ação nova | o pet perde a segurança do instinto (o R1-congelado separa); muda o sono, 34,6% da vida |
| **(c) objetivos e subdecisões** | a escolha parametrizada: o alvo de comer, de explorar, o objeto, o outro pet | a subdecisão (2.3) e, com crédito por canal até o alvo, o J5 (seção 3) | depende do mundo físico (J1), que deu negativo duas vezes | um terceiro negativo no J1; variedade de alvo sem consequência |

**Sobre (a):** o pedido de "mais ações" cabe melhor em (c). Um "verbo" novo, como investigar, aproximar-se ou carregar, é uma ação com
alvo, e o motor já tem esse formato (`Alvo`, `escolher_alvo`). Não precisa de membro novo no `AcaoPet`.

**Sobre (b) e o R2:**
- **o R1 abre o maior bloco:** 55% das decisões são forçadas, e 34,5% delas têm competição real;
- **o R2** (o traço que pula as forçadas e anda com os canais) ataca o crédito perdido sem abrir as regras. A medição mostra quanto ele
  teria para recuperar: 45,9% do |sinal|. Mas o traço da REVISAO-APRENDIZ piorou o P3, e o do B não aprendeu. Ele não deve ser presumido
  como solução.

## 5. As famílias candidatas [PROPOSTA]

Cada família é marcada como existente (E), proposta (P) ou dependente de validação (D).

| família | affordance no mundo | o que o pet percebe | a consequência que pode aprender | o teste contra variedade superficial | depende de |
|---|---|---|---|---|---|
| **comer com escolha de comida** (E: classes por tipo com o paladar; o alvo `comida`) | comidas de tipos diferentes à vista, a fruta ao lado da ração | `vistos` com o tipo; o paladar só depois de comer | a nutrição, o humor e o gosto, **por canal** | a escolha muda quando o efeito muda (o T1 do J5), não só a variedade de tipos | J5 (D); o crédito por canal até o alvo (P) |
| **dormir como escolha** (P: o sono competindo no R1) | nada novo | a energia, a hora, o dormindo | o cansaço e a privação | o R1 contra o R1-congelado; a privação e a saúde não pioram | R1 (P) |
| **investigar algo incerto** (P) | um objeto novo ou um cheiro sem fonte vista | a novidade (a curiosidade do corpo, E), o cheiro (o órgão, E atrás de chave) | a curiosidade reduzida; a comida achada | o pet investiga mais o que é novo, e menos o que já conhece (não só mais ações de explorar) | o mundo físico (J1, D); a curiosidade fora dos braços do plano dos drives |
| **objeto (a bola)** (E: o alvo `bola`) | a bola no mapa | a bola vista | o humor e o tédio | brincar com a bola vista aumenta só quando a bola reduz o tédio | J1 (D) |
| **interagir com o outro pet** (E: seguir, onde comeu; D: o degrau 1) | o outro pet, o toque, a disputa | a percepção social (E, atrás de chave) | a comida achada por seguir; a disputa perdida | seguir mais o pet que leva a comida, e não qualquer um | os dois pets (J7 inconclusivo por premissa, D) |
| **ações novas em 3D** (P) | o que o mundo 3D trouxer | — | — | — | o mundo 3D, só depois do Gate C (J5) |

## 6. A sequência mínima e os critérios mensuráveis [PROPOSTA]

**A sequência:**
1. **Medir antes** (feito aqui): o inventário, a prioridade, o crédito e o alvo, com artefato.
2. **O R1 no v11 sem o mundo** (V3-3): é o maior bloco e não depende do J1, do J5 nem do metabolismo. Com o R1-congelado e o
   `sono_exaustao` forçado (V3-4).
3. **O crédito por canal até o alvo**, antes de qualquer verbo novo: é o limite que o J5 mostra (seção 3), e ele vale também no mundo
   físico.
4. **As famílias da seção 5,** uma por vez, só onde há affordance, percepção e consequência, com o teste da coluna própria.

**Os critérios,** todos medidos por contexto (regra e dono), nunca a diversidade bruta sozinha:

| critério | a medida | onde está hoje [OBSERVADO] |
|---|---|---|
| as oportunidades de escolha | a distribuição do número de candidatos por regra; a fração de decisões forçadas | 55,3% forçadas |
| a prioridade | nas forçadas, a fração com outra regra que valia | 34,5% |
| o crédito que atualiza | a fração das aplicações de crédito que mudam um peso; a fração do \|sinal\| perdida | 0% nas forçadas; 45,9% do \|sinal\| perdido |
| a influência do aprendido | a sonda contrafactual do E0 (a TV, e "mudaria sem o aprendido") | 34,8% nas decisões com escolha |
| a diversidade condicionada | a entropia por regra, da política e das ações feitas, contra o prior | tempo livre: 1,46 contra 1,87 bit |
| o desempenho | `D_FE`, a privação e a saúde (o J1); no J5, a queda da escolha da x depois da mudança | o J1 negativo; o J5 inconclusivo por premissa |

**Uma mudança só conta como melhora** se mexer no desempenho ou na revalorização, e não só nas medidas de oportunidade.

## 7. Se houver um experimento (só a pergunta; o plano é uma tarefa à parte)

- **A pergunta:** abrir a competição entre as regras urgentes (R1) faz o aprendido decidir mais e melhora a homeostase do pet sem mundo,
  contra o A e contra o R1 sem aprender?
- **Os contrastes:** R1 − R0 e R1 − R1-congelado, em `D_FE`, na privação e na saúde. Como descritivo, a fração de forçadas e o crédito que
  atualiza.
- **As métricas candidatas:** as da seção 6.
- **Fora daqui:** o plano de análise, o Δ, o N e a faixa (CLAUDE.md, "Pesquisa: o método").

## 8. Decisões do Matheus (todas PROPOSTAS; a recomendação vem primeiro)

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| **V3-3** (do E0) | a primeira peça do V3 | **a competição entre regras (R1),** no v11 sem o mundo. Esta medição reforça: 55% das decisões são forçadas, 34,5% delas com competição real, e 45,9% do \|sinal\| se perde nelas | começar por verbos novos acrescenta ações que, como o `dormir`, aparecem sozinhas e nunca são escolhidas; começar pelo traço (R2) repete a REVISAO-APRENDIZ sem abrir as decisões |
| **V3-4** (do E0) | a forma da competição | **as regras urgentes que valem viram candidatos num sorteio comum, com o instinto como prior forte e o `sono_exaustao` forçado;** o tempo livre só entra se nenhuma urgente valer (a união média das urgentes é 1,47 ação, e o tempo livre a levaria a 5,0) | abrir também o tempo livre nas urgentes muda o sono de forma grande e confunde aprender com perder o instinto; sem o `sono_exaustao` forçado, a comparação vira de sobrevivência |
| **V3-9** (nova) | o crédito do "querer" | **por canal até o alvo:** o humor, o gosto e a nutrição creditados separados nas classes do alvo, antes de qualquer família nova da seção 5. É o limite que o J5 mostra | manter o sinal somado: o pet continua sem revalorizar a favorita sem o planejador, e cada família nova herda o mesmo problema |
| **V3-10** (nova) | onde entram as "ações novas" | **como ações com alvo (a forma do `Alvo` do motor),** e não como membros do `AcaoPet` | um espaço de ações paralelo ao `AcaoPet` pede tradução no motor, no log e na web, e arrisca a reprodução da v1 |

## 9. O que esta investigação não diz

- não mede se algum mecanismo melhora o pet: são medidas de oportunidade, de crédito e de influência;
- são as sementes dos testes, sem intervalo nem replicação; no J5, só 5 vidas por braço;
- o "34,5% com competição real" conta regras cuja condição vale; não diz que o pet ganharia em escolher entre elas;
- o mundo físico tem só 4 dias.

## 10. Referências

As do E0 (`docs/futuro/digibrain_v3_e0.md`, seção 7) continuam valendo, com o mesmo quanto foi lido. Este documento não acrescenta
nenhuma.

**SEM FONTE:**
- a separação dos quatro limites;
- a leitura do crédito do J5;
- a recomendação da ordem;
- toda leitura marcada [HIPÓTESE].
