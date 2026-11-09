# PLANO DE ANÁLISE V3 — PET_VIVO, etapa 1: o PV-2, a quimiotaxia pela variação do cheiro, e as seis lacunas (2026-11-09, Claude Code, Opus 5.5)

**Status: PROPOSTO.** Nenhuma vida, nenhuma faixa de sementes e nenhum código nesta etapa. Todo número novo é PROPOSTO, e as decisões
PV2-1 a PV2-10 (seção 10) ficam com o Matheus.

**De onde vem:**
- **A frente:** o PV-2 primeiro, pela regra da auditoria. É a D-PV0R-7, DECIDIDA pelo Matheus em 2026-11-09 com "Faça as
  recomendações", repassada pelo Gerente da V3.
- **As seis lacunas:** o Matheus as trouxe em 2026-11-09 e decidiu "Sim, leve ao plano", também repassado pelo Gerente.
- **O mecanismo:** é o M2 da revisão I, a quimiotaxia por dC/dt com varredura curta (vault DigiLab Research, `DigiLab — Revisão de
  escopo/REVISAO_I_PET_VIVO_2026-11-07.md`, seção "M2").
- **A medida de estado:** é a SE-C da 0b e da 0c (`docs/PLANO_ANALISE_V3_PET_VIVO.md`, seção 7; `docs/RESULTADO_V3_PET_VIVO.md`).

**Esta sessão não ouviu o Matheus diretamente.** As duas decisões chegaram pelo Gerente.

## 0. O que existe hoje (os fatos do código que o desenho usa)

Conferidos na `main` `cf13206b`.

- **O cérebro não lê a direção nem a variação do cheiro.**
  - **O M-SENS** (`digilab/digibrain/sens.py`) lê a falta de cada receptor do protótipo, e só o nível (linhas 1 a 18 da docstring). Do
    mundo, lê só se há cheiro: `"ha_cheiro": pm.direcao_cheiro != 0` (linha 108). Esse é o G-SEM-DIRECAO.
  - **Os órgãos ficam fora do protótipo:** o Olfato, a Audição, o paladar e o banheiro. Um receptor de órgão presente falha alto.
- **Quem leva o pet ao cheiro hoje é o motor, com a direção que o mundo entrega.**
  - Nas células da pesquisa (a C4 e a AN0), o candidato `cheiro` é um passo na `direcao_cheiro` (0 a 8) da `PercepcaoMundo`
    (`digilab/mundo.py`, `_alvo_cheiro`).
  - O cérebro escolhe a unidade `comer/cheiro` ou `explorar/cheiro` sem saber para onde ela vai, e o motor anda na direção certa.
  - **Na prática, o pet sabe para onde está a comida sem precisar sentir:** essa direção é um oráculo.
- **O órgão do Olfato já existe e já faz uma parte do M2, mas está desligado** (o DP-13 da V2, `ConfigOlfato` em `digilab/config.py`;
  o corpo em `digilab/corpo.py`).
  - **Ligado,** o mundo deixa de entregar a direção: o `cheiro` e a `direcao_cheiro` vão a 0. O cheiro chega pelos receptores das
    narinas, que têm limiar, adaptação com meia-vida e saturação.
  - **O motor oferece dois candidatos** (`alvos_do_olfato`, `digilab/mundo.py`, linha 407): seguir na direção do último passo, ou virar.
  - **Com duas narinas** (o DP-13 decidiu duas), ele vira 45 graus para o lado mais forte. É a tropotaxia, o "viés lateral" do M2.
  - **Com uma narina,** ele prefere virar quando a leitura caiu desde a decisão anterior (linha 431). É o sinal de dC/dt, mas sem
    acumulador e sem limiar.
  - **Nenhuma célula do modular liga o órgão.** O `ConfigOlfato(ligada=True)` só aparece em `experiments/custo_orgaos.py`.
- **Ligar o órgão no modular hoje cegaria o cérebro para o cheiro.** O `ha_cheiro` sai da `direcao_cheiro`, que o órgão zera. O M-SENS
  falha alto com o receptor do órgão presente.
- **A busca pelo cheiro já é uma intenção, e o motor a executa.** A DX-4 (`intencao_cheiro`, `digilab/digibrain/estado.py`) faz a unidade
  `comer/cheiro` abrir uma busca, que acaba em "meta", "achou", "sumiu" ou "desistiu".
  - A DX-3 (`cheiro_inato`) dá ao cheiro o peso de comida.
  - O gabarito do REL liga as duas (`experiments/exportar_gabarito_digibrain_modular.py`, linha 6).
- **A unidade do cheiro é uma só por comportamento, qualquer que seja o candidato do motor** (`digilab/digibrain/impulso.py`, linhas 102
  e 117). Então trocar a direção do motor não muda o número de unidades. **A conferir no PR do código** com o órgão ligado.

**O que a 0b mediu e o PV-2 herda** (`artifacts_v3_pet_vivo/auditoria/auditoria.json`):
- **A leitura da C4:** indeterminado nos seis grupos.
- **A SE-C:** de 0,103 a 0,121 por unidade, com o σ por unidade de 0,0065 (C4 REL `comedouro`) a 0,0191 (C4 REL `longe_fixo`).
- **A RV:** de 0,32 a 0,41.
- **O reflexo do sono:** decide de 0,15 a 0,24 das decisões.

## 1. As seis lacunas: o que este plano cobre

| # | a lacuna (nas palavras do Matheus, resumidas) | aqui | o mecanismo e a etapa propostos |
|---|---|---|---|
| **1** | **corpo → cérebro:** uma interface explícita para os sinais do corpo, com o nível e a mudança recente | **em parte** | **Coberto aqui:** o cheiro entra no M-SENS como receptor do órgão, com o nível e a variação desde a decisão anterior (dC/dt), em todos os braços com o órgão (seção 3). **Fica para depois:** a variação dos receptores de dentro, como o estresse que acabou de subir. Ela entra pela frente "o corpo modula" (seção 9, item 2), com a mesma conta de variação, a ser reusada |
| **2** | **bioquímica → atividade neural:** estados duradouros mudam a resposta da rede, com regras testáveis | **em parte** | **Coberto aqui:** a primeira regra estado → ganho, a fome aumentando o peso do cheiro de comida (o braço OLF-G; pela pista do Root et al. 2011). **Fica para depois:** a saciedade como freio, a dor como interrupção e a tabela geral químico → parâmetro (seção 9, itens 2 e 3) |
| **3** | **órgãos → percepção e ação:** saídas dos órgãos que o cérebro use, como o olfato com intensidade e adaptação, e o intestino com digestão e saciedade | **em parte** | **Coberto aqui:** o olfato inteiro. O corpo já tem a intensidade e a adaptação; o cérebro passa a ler o receptor, e a ação passa a usar a variação. **Fica para depois:** o intestino, a digestão, a saciedade e o paladar no cérebro (seção 9, item 3) |
| **4** | **comportamento × alvo:** separar "o que fazer" de "para onde"; hoje um comportamento ganha por ter mais alvos | **fica para depois**, com uma guarda aqui | **Fica para depois:** a normalização do sorteio por comportamento (seção 9, item 1). **A guarda aqui:** o PV-2 não pode criar unidades. O cérebro escolhe "buscar o cheiro", e o sistema de ações escolhe a direção (seção 3). O G-UNIDADES (seção 6) confere, e a A-2 da 0b sai por braço, descritiva |
| **5** | **sequências:** a rede escolhe a intenção, e o sistema de ações executa ações curtas compostas | **em parte**, só a busca | **Coberto aqui:** a busca pelo cheiro já é uma intenção (a DX-4). O PV-2 só troca o executor, do oráculo pela quimiotaxia. **Fica para depois:** as opções compostas (procurar, aproximar, comer), pelo PV-5, e o GOAP de profundidade ≤ 3 (seção 9, item 4) |
| **6** | **aprendizado:** os sinais certos recebem o crédito, com estados moduladores e resultados atrasados | **fica para depois** | O P2 já credita pela opção. A HC não pôde ser testada (D-PV0R-6), e uma regra nova entra só por adendo. Ficam para depois o PV-3 (o terceiro fator com a linha de base) e o teste "o sinal certo recebe o crédito" (seção 9, item 5) |

**O G-SEM-DIRECAO continua valendo,** com uma leitura escrita aqui (PV2-3). O cérebro passa a ler o nível e a variação no tempo do
cheiro que sente, e nunca a direção. Quem vira para um lado é o sistema de ações, pela regra da seção 3, com o que as narinas sentem.

## 2. A pergunta e as hipóteses, escritas antes

- **Q-PV2:** um pet que só sente o cheiro, e vira quando ele cai, acha a comida longe tão bem quanto o pet que recebe a direção, e melhor
  que um pet que vira na mesma taxa em hora qualquer?
- **Q-PV2-G:** quando a fome aumenta o peso do cheiro de comida, a escolha fica mais sensível ao corpo (a SE-C e a RV)?

| | a hipótese | aponta se |
|---|---|---|
| **H-TEMPO** | girar na hora certa ajuda: a queda do cheiro diz quando virar | o OLF-DCV ganha do OLF-PLA na taxa por episódio no longe (G-PV2-HORA) |
| **H-VARR** | a varredura curta soma ao dC/dt | o OLF-DCV ganha do OLF-DC (descritivo, sem gate) |
| **H-GANHO** | a fome no ganho do cheiro deixa a escolha mais sensível ao estado | o OLF-G ganha do OLF-DCV na SE-C por mais que δ_E (o G-ESTADO) |
| **H-CUSTO** | tirar o oráculo custa caro | o HOJE fica acima de todos os braços com o órgão (descritivo) |

As hipóteses são deste plano e SEM FONTE como previsão para o Digilab. A literatura (seção 8) só diz que o mecanismo existe no animal.

## 3. O mecanismo, por braço (o que o PR do código implementa, atrás de chave)

As subchaves são PROPOSTAS. Elas ficam numa chave nova do modular, desligada, e a vida de hoje sai byte a byte (o gabarito num commit
próprio antes da mudança, como manda o CLAUDE.md).

| braço | o órgão do Olfato | o M-SENS lê | o sistema de ações vira | papel |
|---|---|---|---|---|
| **HOJE** | desligado | `ha_cheiro` pela `direcao_cheiro` | na direção do mundo (o oráculo) | referência descritiva, sem gate |
| **OLF-0** | ligado, 2 narinas (DP-13) | o receptor do cheiro: `ha_cheiro` = leitura acima do limiar; o nível; a variação (dC/dt) | o `alvos_do_olfato` de hoje (a tropotaxia) | **o controle** |
| **OLF-DC** | ligado | igual | OLF-0 + a pirueta: um acumulador da queda; passando de L, vira | o dC/dt |
| **OLF-DCV** | ligado | igual | OLF-DC + a varredura: na pirueta, compara as duas narinas por 1 ou 2 decisões e vira para a maior | **o braço principal** |
| **OLF-PLA** | ligado | igual | as viradas do OLF-DCV na mesma taxa, mas em hora sorteada, sem ligação com a queda | **o placebo** da hora certa |
| **OLF-G** | ligado | OLF-DCV, com o nível do cheiro multiplicado pelo ganho da fome: `div_arred(c × (G0 + u_fome), G0)` | igual ao OLF-DCV | **o braço separável** do ganho |

- **Onde a conta mora:** a variação e o acumulador ficam no estado do M-SENS. A pirueta, a varredura e o placebo ficam na escolha do
  alvo do motor, ao lado do `alvos_do_olfato`. O cérebro escolhe a unidade, e o sistema de ações escolhe a direção (lacunas 4 e 5).
- **A variação no M-SENS** entra como uma característica nova do `z`, `dC = clamp(c_t − c_{t−1}, −S, S)`. Ela leva um peso inato
  PROPOSTO só na unidade do cheiro (seguir quando sobe), e o P1 e o P2 a leem como qualquer característica.
  - **Ela não entra no HOJE:** lá não há receptor.
  - **Um braço sem ela está fora do desenho.** Ele separaria "o cérebro lê a variação" de "o sistema de ações vira pela variação", mas
    custaria um braço. Fica como alternativa na PV2-4.
- **O placebo** sorteia a hora de virar numa rng própria, derivada por `derivar_semente`. Isso segue a regra da rng separada: o placebo
  não pode mudar o mundo nem a política dos outros braços.
- **O ganho do OLF-G** é a forma da revisão I (`cheiro*(64+fome)>>6`), escrita com a urgência da fome do M-AFETO (`u_fome`, em [0, S]).
  - **O G0** é PROPOSTO: S/16 = 64, pela forma da revisão.
  - **O freio pela saciedade fica de fora:** o protótipo não tem o receptor da saciedade (lacuna 3, seção 9).
- **O L da pirueta e o número de decisões da varredura** são PROPOSTOS e SEM FONTE. O PR do código mede nas sementes dos testes e
  propõe por adendo, antes da run.
- **O nível do cheiro e o z:** no OLF-0, o nível entra como a proximidade do cheiro (`prox` da unidade do cheiro). Hoje o `ha_cheiro`
  liga ou desliga a unidade sem nível. A troca é a mesma em todos os braços com o órgão, então o contraste com o OLF-0 não a mede.

## 4. As vidas, o tamanho e o custo

- **O cérebro:** o REL da `main` (o dos ovos, #562), com as subchaves dele.
- **O mundo:** os 4 donos e os 3 lugares da C4 (`longe_fixo`, `comedouro` e `longe`), 14 dias.
- **O tamanho (PV2-6):** 5 bases × K = 40, isto é, 200 unidades, × 4 donos × 3 lugares × 6 braços = **14 400 vidas**. É o tamanho da
  C4, com os mesmos 6 braços dela, e cabe na mesma regra de IC por (braço, lugar).
- **O contrafactual da SE-C** roda numa subamostra, como na 0b: os k de 0 a 7 de cada base (40 unidades), nos braços OLF-0, OLF-DCV e
  OLF-G. São 1 440 vidas com o contrafactual.
- **As sementes:** uma faixa nova, pedida ao coordenador e posta em `FAIXAS_RESERVADAS` antes da run. **Nenhuma faixa é reservada
  nesta etapa.**
- **O custo é SEM MEDIDA.**
  - O órgão soma o custo do corpo; o `experiments/custo_orgaos.py` mede o órgão sozinho.
  - O PR do código mede 2 vidas por braço nas sementes dos testes e projeta a run com 4 processos.
  - Acima de umas 8 h, o PR propõe um K menor num adendo, antes da run.
- **A máquina (V3-D8):** no máximo 4 processos, e só quando o Gerente liberar a vez.

## 5. As medidas (todas no `digilab/metrics.py`, uma vez só)

- **O forrageio:**
  - **A taxa de fechamento por episódio de fome** é a do G-MVP-EP, a `episodios_de_fome` em `digilab/metrics.py`, a mesma das guardas da
    C4 e do AN4.
  - **O achado pelo cheiro** é a fração das buscas `comer/cheiro` da DX-4 que acabam em "achou" ou "meta".
  - **As decisões até comer**, desde a primeira com cheiro.
- **A hora da virada** (o que o placebo separa): a fração das viradas que começam com o cheiro em queda.
  - **Na larva, 81,6 %** dos giros começam apontando gradiente abaixo (Gomez-Marin et al. 2011, pista, a verificar). É só contexto, e
    não um alvo.
- **A SE-C e a RV** da 0c: as funções `sensibilidade_coerente` e `se_c`, a mesma conta da 0b, com a A_r fixada nas vidas de cada braço
  antes da medida (PV-0-7).
- **As unidades por decisão (a A-2 da 0b), por braço:** o número de unidades ativas por comportamento, a `TV(P, P¹)` e o ρ. Descritivas,
  e base do G-UNIDADES.
- **A entropia `H(P)`:** só descritiva (PV-0-10).

## 6. Os gates, escritos antes

Os contrastes são pareados por unidade (base, semente), com a média dos 4 donos e o IC95 pelo t, como na C4.

| gate | contraste | onde | passa se | o que guarda |
|---|---|---|---|---|
| **G-PV2-LONGE** (primário do PV-2) | OLF-DCV − OLF-0 na taxa por episódio | `longe` e `longe_fixo`, cada um | o limite de baixo > 0 nos dois | a quimiotaxia ajuda onde a comida está longe |
| **G-PV2-HORA** (o placebo) | OLF-DCV − OLF-PLA na taxa por episódio | `longe` e `longe_fixo` | o limite de baixo > 0 nos dois | girar na hora certa, e não girar mais |
| **G-FORR** (a guarda de forrageio, PV-0-10) | OLF-DCV − OLF-0 e OLF-G − OLF-DCV na taxa por episódio | `comedouro` | o IC não fica abaixo de −δ_F, com δ_F = 0,018 (a margem da G-COMEDOURO-AN) | o mecanismo não deixa o pet pior perto de casa |
| **G-ESTADO** (primário do OLF-G, PV-0-10) | OLF-G − OLF-DCV na SE-C | os 3 lugares, cada um | o limite de baixo > δ_E do lugar | o ganho pela fome deixa a escolha mais sensível ao estado |
| **G-ESTADO-NI** (a guarda de estado do OLF-DCV) | OLF-DCV − OLF-0 na SE-C | os 3 lugares | o limite de baixo > −δ_E do lugar | a quimiotaxia não tira o corpo da escolha |
| **G-UNIDADES** (conferência, falha alto) | o número de unidades por decisão | todos os braços com o órgão | igual ao OLF-0, decisão a decisão, nas sementes dos testes | o PV-2 não cria alvos (lacuna 4) |

- **O δ_E (PV2-7):** o menor efeito com poder 0,8 pelo σ da SE-C por unidade que a 0b mediu, `δ_E = 2,8 · σ / √40`, por lugar, no REL:
  - `comedouro` 0,0029;
  - `longe_fixo` 0,0085;
  - `longe` 0,0042.

  São PROPOSTOS. A conta é a regra da C4 (a margem efetiva), com o N da subamostra. A run não muda esses valores.
- **Por que o G-ESTADO não é o gate primário do OLF-DCV:**
  - a pirueta e a varredura agem no sistema de ações, depois da escolha. A SE-C mede a escolha, então ela quase não deve mudar ali;
  - pedir que o OLF-DCV ganhe na SE-C seria pedir o que o mecanismo não faz.
  - A PV-0-10 pede o G-ESTADO em cada plano: aqui ele é o primário onde o mecanismo mexe na escolha (o OLF-G) e a guarda onde não mexe.
    Essa leitura vai ao Matheus na PV2-8.
- **Sem correção de multiplicidade entre os gates:** cada gate responde a uma pergunta própria, e todos os resultados saem, passem ou não.
  O G-PV2-LONGE e o G-PV2-HORA pedem os dois lugares juntos, então cada um já é a interseção.

## 7. A regra de leitura, escrita antes

| G-PV2-LONGE | G-PV2-HORA | G-FORR | a leitura | o que se sugere |
|---|---|---|---|---|
| passa | passa | passa | **a quimiotaxia funciona e gira na hora certa** | levar o OLF-DCV ao cérebro padrão e à web, com a paridade, por tarefa própria |
| passa | não passa | passa | **ajuda, mas pelo número de viradas** | o placebo explica o ganho. Não levar a pirueta; rever a varredura |
| não passa | — | — | **sem ganho sobre a tropotaxia** | a pirueta não soma às duas narinas. O OLF-0 fica como a forma sem oráculo, se o H-CUSTO for pequeno |
| — | — | não passa | **custa perto de casa** | não levar, qualquer que seja o resto |

- **O OLF-G sai separado.** O G-ESTADO e o G-FORR dele dizem se o ganho entra, independentemente da quimiotaxia.
- **O HOJE é só descritivo.** A distância do HOJE aos braços com o órgão diz quanto o oráculo dá de graça. Trocar o oráculo no jogo é
  decisão do Matheus, à parte.
- **A leitura é da run única.** Nada se ajusta olhando o resultado; uma regra diferente entra por adendo, antes da run.

## 8. A literatura (todas pistas, a verificar)

A tabela `v3c5` (a 0a, PR #705) não está na `main`. Então toda referência deste plano é **pista, a verificar**, com a fonte de onde veio
(a revisão I e a nota `20 Temas/Pet vivo.md` do vault). Nenhuma referência nova entra neste plano; se entrar, vai para o vault.
- **Pierce-Shimomura, Morse e Lockery 1999** (`10.1523/JNEUROSCI.19-21-09557.1999`): a pirueta pelo dC/dt < 0.
- **Iino e Yoshida 2009** (`10.1523/JNEUROSCI.3633-08.2009`): a pirueta e o cata-vento em paralelo.
- **Gomez-Marin, Stephens e Louis 2011** (`10.1038/ncomms1455`): a queda acumulada decide quando, a varredura decide para onde.
- **Root et al. 2011** (`10.1016/j.cell.2011.02.008`): a fome aumenta o ganho olfativo.
- **Izquierdo e Lockery 2010:** um modelo, na lista da revisão I, sem o DOI nela.

Nenhuma delas mede um pet como o do Digilab. Elas só são o motivo do desenho.

## 9. O que fica para as etapas seguintes (RECOMENDAÇÃO, sem código; a ordem é do Matheus)

1. **A normalização do sorteio por comportamento** (lacuna 4): sortear o comportamento antes do alvo.
   - É o conserto mais barato da HA.
   - A HA não apontou, mas o ρ do `explorar` passa de 1,25 em quatro grupos da C4, e o do `comer` vai a 1,35–1,38 no `comedouro`.
   - O Dulberg et al. 2023 (argmax entre subagentes, pista, a verificar) é a alternativa maior.
2. **O corpo modula o cérebro** (lacunas 1 e 2):
   - a variação dos receptores de dentro, com a conta de variação deste plano reusada;
   - uma tabela químico → parâmetro, testável, com cada regra atrás de subchave. Por exemplo, a dor sobe a interrupção e a saciedade
     baixa o peso da comida;
   - os dois estados persistentes do Flavell et al. 2013 (pista, a verificar);
   - a regra de interrupção pela dor, que é a lista Startle do PV-1.
3. **Os órgãos de dentro na percepção** (lacuna 3): o intestino, com a digestão e a saciedade como receptores lidos pelo M-SENS, e o
   paladar, que o J5 já tem no corpo.
4. **As opções compostas** (lacuna 5): o PV-5, isto é, procurar, aproximar e comer como uma opção com término. Depois, o GOAP de
   profundidade ≤ 3 (Orkin 2006, pista, a verificar).
5. **O crédito** (lacuna 6):
   - o PV-3, o terceiro fator com a linha de base `r − EMA(r)`;
   - o teste "o sinal certo recebe o crédito", que pede antes um adendo à regra da 0b. Os cortes de "6 receptores" não se atingem com 4
     receptores com a A_r não vazia (D-PV0R-6).
6. **A web:** depois de cada mecanismo aprovado, por tarefa própria, com a paridade (a regra "sempre aplicar na web").

## 10. As decisões com o Matheus

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| **PV2-1** | o lugar do plano | **este arquivo novo**, ao lado do plano da etapa 0 | um adendo ao plano da 0b misturaria a auditoria, que é só leitura, com uma run de mecanismo |
| **PV2-2** | onde mora a quimiotaxia | **no sistema de ações** (a escolha do alvo do motor, ao lado do `alvos_do_olfato`), com o cérebro lendo o nível e a variação | no cérebro: ele teria de representar a direção, o que quebra o G-SEM-DIRECAO e cria unidades (lacuna 4) |
| **PV2-3** | a leitura do G-SEM-DIRECAO | **o cérebro lê o nível e a variação no tempo do cheiro que as narinas sentem, nunca a direção** | ler a diferença entre as narinas no cérebro daria a direção por outra porta |
| **PV2-4** | os braços | **HOJE, OLF-0, OLF-DC, OLF-DCV, OLF-PLA e OLF-G** (seção 3) | sem o placebo, girar mais e girar na hora certa se confundem. Sem o OLF-0, o ganho se mede contra o oráculo e mistura o órgão com o mecanismo. A alternativa é um braço sem a leitura da variação no cérebro: separa as duas portas, ao custo de mais 2 400 vidas |
| **PV2-5** | o ganho da fome | **`div_arred(c × (G0 + u_fome), G0)`, G0 = 64, sem o freio da saciedade** | um ganho alto pode transformar o pet num autômato do cheiro: a entropia e o G-FORR mostram isso |
| **PV2-6** | o tamanho | **200 unidades × 4 donos × 3 lugares × 6 braços = 14 400 vidas, com a SE-C em 40 unidades** | menos unidades alargam o IC além do δ_E do `longe_fixo` (σ 0,0191). O contrafactual em todas as vidas dos três braços seria cerca de 5 vezes o da subamostra (7 200 vidas contra 1 440) |
| **PV2-7** | o δ_E | **2,8 · σ / √40 por lugar, com o σ da 0b no REL** | um δ_E maior faria o G-ESTADO não passar nunca. Um menor faria passar ruído |
| **PV2-8** | o papel do G-ESTADO | **primário no OLF-G, guarda de não inferioridade no OLF-DCV** | primário nos dois pediria à quimiotaxia o que ela não faz, e o PV-2 falharia por construção (a lição do D-PV0R-6) |
| **PV2-9** | os números do mecanismo (o L da pirueta, as decisões da varredura e a taxa do placebo) | **o PR do código mede nas sementes dos testes e propõe por adendo, antes da run** | fixar agora seria escolher sem medida. Fixar depois da run seria ajustar olhando o resultado |
| **PV2-10** | a ordem das etapas seguintes | **a da seção 9**: o sorteio primeiro, depois o corpo modula, os órgãos, as opções e o crédito | começar pelo corpo modula deixaria a HA misturada em toda medida de sensibilidade. É o motivo de propor o sorteio antes |

## 11. O que fica de fora

- **Nesta etapa:** nenhuma vida, nenhuma faixa, nenhum código, nenhum número DECIDIDO.
- **No PV-2:** o intestino e a saciedade, a dor, as opções compostas, o crédito, a normalização do sorteio e a web (seção 9).
- **O Olfato social** (`outro_pet`) e a Audição: são de outra pergunta (os dois pets).
- **O `engine.py`** não muda.
- **Os arquivos da INDIVIDUALIDADE e da 0b:** ficam como estão.
