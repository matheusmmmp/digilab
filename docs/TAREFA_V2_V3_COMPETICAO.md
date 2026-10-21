# TAREFA V2 — V3_COMPETICAO: a competição entre as regras urgentes (V3-3 e V3-4) (2026-10-21)

Coordenador: Gerente (Claude Code). Worker do desenho: Claude Code (worker B). Worktree e branch: `v2-v3-competicao`. Status: ETAPA 0 (as decisões CR-1 a
CR-7 DECIDIDAS pelo Matheus em 2026-10-21, pela recomendação; o código não começou).

Categoria: implementacao (a tarefa); o PR deste desenho é `arquitetura`. Origem: Matheus, 2026-10-21: parar a V3-9 na G0-PODE-MUDAR
(#376) e seguir para a V3-3/V3-4, pela recomendação do `docs/futuro/v3_espaco_acoes.md` (seção 8) e do E0
(`docs/futuro/digibrain_v3_e0.md`, seções 3.1 e 4).

Todo o desenho é **PROPOSTO**. As marcas são as do `v3_espaco_acoes.md`: [IMPLEMENTADO], [OBSERVADO] (com artefato), [CONTA] (sai do
código ou da aritmética), [HIPÓTESE] e [PROPOSTA].

## 0. O que a conta permite prometer, antes de tudo

A V3-9 parou porque prometia mais do que a conta permitia (#376). Aqui a conta vem primeiro.

1. **A abertura alcança um terço das forçadas, não todas.** [OBSERVADO, `artifacts_v2_v3/espaco_acoes.json`, v11]
   - 55,3% das decisões têm um candidato só. Em 34,5% delas, outra regra urgente também valia.
   - **Mas só em 32,1% delas a união dos candidatos urgentes tem mais de uma ação.** O `sono_continuar` e o `sono_noite`, por exemplo,
     só propõem `dormir`.
   - Com o tempo livre fora (V3-4), o R1 abre cerca de 0,553 × 0,321 ≈ **17,8% das decisões**. As forçadas caem de 55,3% para cerca de
     **37,5%**, medido sobre a vida do R0. A vida do R1 é outra, e a etapa 0 não a vê.
   - **A predição V3-P1 do E0** ("as forçadas caem para perto dos 2,2% do `sono_exaustao`") **não vale para a forma decidida.** Ela
     exigiria o tempo livre na disputa. Fica corrigida aqui e no registro.
2. **Um prior forte trava o crédito na mesma medida em que protege o instinto.** [CONTA, `atualizar_pesos`]
   - A regra da L1 multiplica cada passo por `S·1[a = a*] − P_a`.
   - Numa decisão aberta em que o instinto fica com `P_inst`, a ação do instinto, quando sai, aprende com `(1 − P_inst)`, e as outras
     com `−P_a`. A massa de crédito da decisão é `2·(1 − P_a*)` do sinal.
   - **Com `P_inst` = 0,9, cada decisão aberta ensina cerca de um quinto** do que ensinaria uma decisão sem prior.
   - A segurança e o aprendizado são o mesmo número, e a escolha do κ (CR-2) é essa troca.
3. **Quanto do |sinal| perdido a abertura alcança não está medido.**
   - O E0 e o `espaco_acoes.json` contam decisões, não o |sinal| das decisões que abririam.
   - As forçadas levam 45,9% do |sinal|, e o `sono_continuar` sozinho 51% disso (1.686.060 de 3.320.804). Mas boa parte do
     `sono_continuar` vale sozinho.
   - **A etapa 0 mede esse alcance antes de qualquer linha em `digilab/`.**
4. **No começo da vida, o R1 é quase o R1-congelado.** [CONTA]
   - As tabelas das regras forçadas nunca aprenderam (0 de 2.658 créditos mudaram peso, `espaco_acoes.json`). No R1 elas partem do prior.
   - O efeito do aprendizado na abertura só aparece depois que essas tabelas acumulam. O R1-congelado (seção 6) separa isso.

## 1. Pergunta

Abrir a disputa entre as regras urgentes que valem faz o aprendido decidir mais e melhora a homeostase do pet sem mundo? A comparação é
contra o A (R0) e contra a mesma abertura sem aprender (R1-congelado). O `sono_exaustao` fica forçado, e o tempo livre só entra se nenhuma
urgente valer.

- **Vem da H1, fase 1:** a plasticidade durante a vida (`docs/PLANO_V2_PESQUISA.md`).
- **É a V3-3/V3-4** do `v3_espaco_acoes.md` (seção 7, a pergunta do experimento) e o braço R1 do E0 (seção 4.2).

## 2. Depende de

- **Na `main`:** o A v11 (`experiments/exportar_gabarito_lobos.py`, `bancada_v11`), o E0 (`experiments/medir_e0_influencia_aprendido.py`)
  e a medição do V3 (`experiments/medir_v3_espaco_acoes.py`, com o teste das regras refeitas contra o `PoliticaInstinto`).
- **As decisões do Matheus na seção 9:**
  - a CR-1 a CR-3 antes da etapa 0, que mede pela forma escolhida;
  - a CR-4 a CR-7 antes do código.
- **Nada da V3-9, do J5 nem do metabolismo.** É o v11 sem o mundo.

## 3. O desenho

### 3.1 Como o A decide hoje [IMPLEMENTADO]

- **A regra:** `impulsos` (`lobos.py`) roda o `PoliticaInstinto` com uma rng-sonda. Sai a primeira regra que vale, na ordem
  `sono_exaustao`, `sono_continuar`, `sono_noite`, `pedido_necessidade`, `abandono`, `fome_moderada`, `tempo_livre`, com os candidatos
  dela.
- **O peso:** `_pesos_efetivos(regra, candidatos, x)` soma, por candidato, o prior da regra (`impulsos`), o aprendido (`decisao`), a
  memória e o piso. Cada regra tem a sua tabela, com as sete ações (`_tabela_prior`).
  - **O R1 não precisa de peso novo:** as linhas das ações que uma regra propõe já existem na tabela dela.
- **A decisão:**
  - com um candidato, não há sorteio e a rng não é consumida;
  - com mais, `u = rng.random()` e o sorteio é proporcional (`sortear`).
- **O crédito:** `_aplicar_sinal` aplica a L1 à tabela da regra registrada. Com um candidato, o fator é zero.

### 3.2 O que muda [PROPOSTA]

**Atrás de uma chave nova, `ConfigLobos.competicao_regras` (bool, False; PROPOSTO, SEM FONTE), com `kappa_instinto` (inteiro, CR-2):**

1. **As regras que valem:**
   - uma função pura, `regras_que_valem(obs, cfg)`, num módulo novo (`digilab/competicao.py`), com os literais do `PoliticaInstinto.agir`;
   - conferida por teste contra o instinto em observações aleatórias, como o teste da medição do V3: a primeira regra que vale tem de ser
     a `ultima_regra` do instinto;
   - o `policy.py` não muda.
2. **Quem disputa:**
   - **se o `sono_exaustao` vale:** dormir, forçado, como hoje (a regra de segurança, V3-4);
   - **senão, as regras urgentes que valem** (todas menos o tempo livre e as suas variantes do mundo).
     - Se nenhuma urgente vale, a decisão de hoje (o tempo livre).
     - Se vale uma só, a decisão de hoje.
3. **As propostas (CR-3):** a união das ações candidatas das regras que valem. Cada ação vem da regra **mais urgente** que a propõe; o
   peso e o crédito são dessa tabela.
4. **O prior forte (CR-1):** o peso efetivo das propostas da regra do instinto (a primeira que vale) é multiplicado por κ
   (`kappa_instinto`). As outras ficam com o peso efetivo da sua tabela.
   - Com uma regra só, κ multiplica todos os candidatos, cancela no sorteio proporcional e o R1 é o A.
   - O piso entra antes do κ.
5. **O sorteio:** `u = rng.random()` e `sortear` sobre os pesos das propostas, na ordem do instinto.
   - A rng da política passa a ser consumida nas decisões abertas. A vida do R1 diverge da do R0 a partir da primeira abertura, como
     deve ser.

### 3.3 O crédito [PROPOSTA, CONTA]

- **A forma:** o sorteio é proporcional sobre `q_a = κ_a · w_a`. Logo `∂ log p(a*) / ∂w_a = (1[a = a*] − p_a) / w_a`, com κ ou sem ele.
  A L1 de hoje vale igual, com `P_a` a probabilidade da disputa e `W_a` o peso efetivo sem o κ.
- **A aplicação:** o registro da decisão aberta guarda as propostas por tabela. O `_aplicar_sinal` chama `atualizar_pesos` uma vez por
  tabela que propôs, com os candidatos dela e os `P` da disputa.
  - A tabela de onde saiu a ação escolhida tem o fator `S − P_a*` nela. As outras têm `−P_a`.
- **Os outros termos:** o corpo e as entradas sociais seguem a mesma divisão, por tabela.

### 3.4 O registro e a sonda [PROPOSTA]

- **O motivo da decisão aberta ganha `competicao`:**
  - as regras que valiam;
  - as propostas e as suas tabelas;
  - κ e os pesos antes e depois do κ;
  - `acao_do_instinto`, a ação que o A daria com o mesmo `u`;
  - `instinto_decidiu`, se a abertura mudou a ação.
- **A sonda do E0** ("o aprendido mudou") passa a ter duas leituras: a abertura mudou e o aprendido mudou. É o que a V3-1 pede.

### 3.5 O que não muda

- `engine.py`, `policy.py`, o motor, o corpo e o mundo;
- o tempo livre e as suas variantes, o banheiro e o J5;
- o bandit, o v11 da web e o porte. A web só recebe a chave se o Matheus decidir, depois da validação;
- com a chave desligada, tudo, byte a byte (G2).
- **A chave falha alto** com o banheiro (a `alivio_urgente` fica fora do desenho), com o planejador e com o mundo físico. A primeira
  versão é só o v11 sem o mundo (CR-4).

**Os arquivos:**
- `digilab/competicao.py`: as regras que valem e as propostas;
- `digilab/policies/lobos.py`: a disputa, o crédito por tabela e o registro;
- `digilab/config.py`: a chave e o κ, com status;
- os testes em `tests/test_competicao_regras.py`;
- os gabaritos em `tests/gabaritos/`.

## 4. A etapa 0: medir sem mexer (a porta)

**Uma medição em `experiments/`,** como a da V3-9. Embrulha só para ler e roda sobre as vidas do R0 de hoje: o v11, as 20 vidas do E0 (4
donos × as sementes dos testes, 14 dias). **Nenhuma vida muda;** o gabarito é gravado antes, e a medida o confere.

Em cada decisão, o embrulho:
1. **refaz as regras que valem e as propostas** pela forma da CR-3 (a função da seção 3.2, ainda em `experiments/`, conferida contra o
   instinto);
2. **monta a disputa** com os pesos de hoje das tabelas, para cada κ da grade `{1, 2, 4, 8, 16, 32}` (só descritivo);
3. **lê:**
   - `P_inst`, a probabilidade da ação do instinto;
   - a massa de crédito `2·(1 − P_a*)·|f|`, com o `|f|` do crédito que a decisão recebeu hoje (o embrulho do `_aplicar_sinal`, como na
     medição do V3);
   - com um `u` sombra de uma rng própria (`derivar_semente("sombra-r1", semente)`, que não toca a rng da política): se a disputa mudaria
     a ação. É o preço do instinto no nascimento.

**O que sai:**
- **o alcance:** a fração das decisões abertas e a fração do |sinal| das forçadas que cai nelas (o item 3 da seção 0);
- **por κ:**
  - a mediana de `P_inst` nas abertas;
  - a massa de crédito nova, contra a massa de crédito de hoje (`Σ 2·(1 − P_a*)·|f|` nas decisões com escolha);
  - a fração das abertas em que a ação mudaria;
- **por dono e por regra:** o relapso tem 74% de forçadas.

**A G0-R1-PODE-APRENDER** (PROPOSTA, SEM FONTE):
- **a regra:** no κ que a CR-2 fixar, a massa de crédito nova tem de ser **pelo menos 10% da massa de hoje**;
- **se não for:** a abertura, do jeito decidido, ensina pouco demais para valer o código. A tarefa para e relata, e a forma volta ao
  Matheus (o κ, ou abrir também o tempo livre).

A etapa 0 não escolhe o κ olhando desfecho nenhum. Ela lê só os pesos de nascimento, os estados e o sinal das vidas do R0. O R1 ainda
não existe.

## 5. As etapas e os gates

| etapa | o que | gate (falha para a tarefa) | onde |
|---|---|---|---|
| **0, medir sem mexer** | a seção 4 | **G0-R1-PODE-APRENDER**; o embrulho não muda a vida (o gabarito); as regras refeitas são as do instinto | PR próprio, `implementacao`; artefato `artifacts_v2_v3/competicao_etapa0.json` |
| **1, gabarito antes** | grava, num commit próprio, as vidas de hoje com a chave desligada: as 20 do v11 (o estado interno, o log e os motivos), e confere que os gabaritos que já existem continuam passando | **G2** | `tests/gabaritos/` |
| **2, o código** | a seção 3, atrás da chave | **G2**; **G-R1-SEGURANCA** (com o `sono_exaustao`, a decisão é a de hoje); **G-R1-UMA-REGRA** (com uma regra só, a decisão, o `u` e o crédito são os de hoje, porque o κ cancela); **G-R1-CREDITO** (com sinais sintéticos, a soma dos fatores de uma decisão aberta é zero, a menos do arredondamento, e cada tabela recebe só as suas propostas); **G-R1-REGRAS** (`regras_que_valem` contra o instinto em observações aleatórias); o replay bit a bit com a chave ligada; `n_pesos()` igual com e sem a chave | o mesmo PR da etapa 1, depois do commit do gabarito |
| **3, o plano** | `docs/PLANO_ANALISE_V2_V3_COMPETICAO.md` (a seção 6), commitado antes da primeira vida | — | PR próprio |
| **4, piloto e validação** | o piloto (as premissas, a margem, o N) e a validação **uma vez** | os do plano | runs nas faixas da CR-6 |

## 6. O experimento que mostraria o efeito (o plano próprio, na etapa 3)

**O mundo é o do v11** (`bancada_v11`: o corpo químico com os drives novos, o mundo `padrao`, o braço P1-c-tapa), com os 4 donos e vidas de
14 dias, como o E0 (CR-4).

| braço | o que é |
|---|---|
| **R0** | o A v11 como está |
| **R1** | R0 + a competição (a chave, o κ da CR-2) |
| **R1-congelado** | a competição com o aprendizado desligado (os pesos no prior). Separa "abrir muda o pet" de "o aprendido usa a abertura" |
| P0 | o instinto, sem aprender: o piso da homeostase no mesmo mundo |

**Os contrastes (CR-5):**
- **o primário:** `D_FE`(R0) − `D_FE`(R1) > 0 na janela dos dias 8 a 14 (`digilab/metrics.py`, `deficit_fome_energia`). O R1 cuida
  melhor do próprio corpo;
- **o secundário de mecanismo:** `D_FE`(R1-congelado) − `D_FE`(R1) > 0. O aprendido usa a abertura. É a V3-P4;
- **a segurança, por não inferioridade:** a saúde e a privação de sono do R1 não pioram contra o R0 além de uma margem do plano. Sem ela,
  um R1 "melhor" pode ser só um pet que dorme menos;
- **o descritivo:**
  - a fração de forçadas (a V3-P1 corrigida: perto de 37,5%, não de 2,2%);
  - a massa de crédito;
  - a sonda do E0 com as duas leituras (seção 3.4);
  - tudo por dono e por dia.

**O N, a margem e o poder:** saem do piloto, pelo poder simulado, como nos planos anteriores. Nenhum número aqui.

**As faixas (CR-6):** pedir **58101…58505** (o piloto e, se a CR-2 escolher calibrar o κ, a calibração) e **59101…59505** (a validação).
As duas estão livres em `experiments/bancada/faixas.py` e nas configs.

## 7. Fora desta tarefa

- **abrir o tempo livre na disputa:** só se a G0-R1-PODE-APRENDER falhar e o Matheus decidir;
- **o traço que pula as forçadas (R2) e a modulação pela química (R3):** o E0, seções 3.2 e 3.3;
- **o J1 e o mundo físico como benchmark** (a V3-5 do E0): depois da validação no v11, se o R1 der efeito;
- **as ações novas como ações com alvo** (V3-10);
- **a V3-9:** parada (#376). As tabelas sombra dela ficam como instrumento;
- **a web e o painel DigiBrain.**

## 8. Critérios de aceitação

- **Etapa 0:**
  - o artefato existe e se refaz igual;
  - um teste confere que o embrulho não muda a vida (o gabarito) e que as regras refeitas são as do instinto;
  - a G0-R1-PODE-APRENDER sai com o número e o veredito.
- **Etapas 1 e 2:**
  - o commit do gabarito vem antes do código;
  - `python -m pytest tests/test_competicao_regras.py -q` passa, e a suíte inteira passa, com a contagem no corpo do PR;
  - a chave e o κ têm status em `config.py`.
- **Etapa 3:** o plano está commitado antes de qualquer vida nas faixas novas.
- **Em toda etapa:** o desvio vai em `docs/registro/AAAA-MM.md` e no índice; o resumo vai no corpo do PR e numa seção no fim deste
  arquivo.

## 9. Precisa do Matheus

**Todas DECIDIDAS pelo Matheus em 2026-10-21, pela recomendação** (a primeira opção de cada linha). Os números delas (o
0,9 da CR-2 e os 10% da CR-7) continuam SEM FONTE.

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| **CR-1** (DECIDIDA) | a forma do prior forte | **multiplicar por κ o peso efetivo das propostas da regra do instinto.** Com uma regra só, o κ cancela e o R1 é o A, o que dá um gate exato (G-R1-UMA-REGRA), e a L1 vale igual (seção 3.3). As outras: **somar um bônus β** (achata as proporções dentro da regra, então o R1 deixa de ser o A até com uma regra só); **o vencedor leva tudo por urgência** (é o A de hoje, sem crédito) | com o β, toda decisão do fome moderada muda, e o efeito do R1 se mistura com uma mudança no comer que não é a abertura |
| **CR-2** (DECIDIDA) | quanto vale o κ | **fixado por uma regra só do prior, antes de qualquer desfecho: a menor potência de 2 com que, nos pesos de nascimento, a ação do instinto fica com pelo menos 0,9 na mediana das decisões abertas da etapa 0** (PROPOSTO, SEM FONTE). A outra: **calibrar o κ** nas sementes do piloto contra o `D_FE` (M10) | κ grande demais: o R1 fica igual ao R1-congelado, porque a massa de crédito some (seção 0, item 2). Pequeno demais: o pet perde o instinto no nascimento, e o efeito vira de sobrevivência. Calibrar custa uma run e, sem plano próprio, é ajustar olhando |
| **CR-3** (DECIDIDA) | como as propostas se juntam | **por ação, da regra mais urgente que a propõe** (uma tabela por ação na decisão) | por par (regra, ação): o `dormir` do `sono_continuar` e o do `sono_noite` contariam duas vezes, e o sono ganharia peso só por ter duas regras |
| **CR-4** (DECIDIDA) | onde o experimento roda | **no v11 sem o mundo** (o mundo do E0), como a V3-3 decidiu | no J1 primeiro: o mundo físico já deu negativo duas vezes, e um terceiro negativo não diria se foi a abertura ou o mundo |
| **CR-5** (DECIDIDA) | o primário | **o `D_FE`** (R0 − R1, dias 8 a 14), **com a saúde e a privação de sono por não inferioridade e o R1-congelado como secundário de mecanismo** | um primário de influência (a fração de forçadas, a TV do E0) passa por construção: a abertura muda essas medidas sem o pet ficar melhor |
| **CR-6** (DECIDIDA) | as faixas | **pedir 58101…58505 (piloto e calibração) e 59101…59505 (validação)** | usar uma faixa já usada compromete aquela frente; as queimadas não voltam |
| **CR-7** (DECIDIDA) | o limiar da G0-R1-PODE-APRENDER | **10% da massa de crédito de hoje,** no κ da CR-2 (PROPOSTO, SEM FONTE) | sem porta: o código entra e a validação gasta uma faixa para achar o R1 igual ao R1-congelado. Porta alta demais: pára uma peça que ensinaria um pouco |

## Referências

As do E0 (`docs/futuro/digibrain_v3_e0.md`, seção 3.1) continuam valendo, com o mesmo quanto foi lido:
- Daw, Niv e Dayan (2005): **só o título**. É pista para a arbitragem, não suporte;
- Singh et al. (2010): o instinto como prior evoluído;
- Hallawa et al. (2021): a partição instinto × aprendido não é diferencial.

**SEM FONTE:**
- o κ e a regra que o fixa;
- o limiar de 10%;
- a forma das propostas;
- a margem de não inferioridade.
