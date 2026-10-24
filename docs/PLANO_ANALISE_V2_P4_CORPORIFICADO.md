# Plano de análise — V2: a P4, a revalorização do J5 no mundo com o contrato sensório-motor (a replicação do T1)

> **Nota (2026-10-24), a direção nova:** o Matheus decidiu, no PROMPT MESTRE, que o produto jogável vem primeiro, que o DigiBrain
> caminha para um cérebro **modular**, e que o cérebro A fica como linha de base, controle e fallback condicionado, e não como o cérebro
> final da web. As decisões "a web roda um DigiBrain, o A" (2026-10-01) e o M6 (rodada 15) estão **SUPERADAS** desde 2026-10-24; o
> texto abaixo fica como estava, como registro. Ver `docs/ARQUITETURA_DIGIBRAIN_MODULAR.md` e `docs/AUDITORIA_V2_PRODUTO_MODULAR.md`.
>
> Com a direção nova, este plano lê o A como baseline, e não como o cérebro final; a execução está pausada pela recomendação DM-8,
> até o Matheus decidir.

Status (2026-10-21): **PROPOSTO**, registrado **antes de qualquer run** e antes do código das etapas 1 a 3. É a etapa 4 de
`docs/TAREFA_V2_P4_CEREBRO_MUNDO.md`, com as P4-1 a P4-8 DECIDIDAS pelo Matheus em 2026-10-21. As decisões deste plano (PC-1 a PC-7,
seção 12) estão abertas.

**Regras deste plano:**
- Os números novos são PROPOSTOS, SEM FONTE, salvo onde citam um artefato.
- O que não está aqui é descritivo pós hoc.
- Nada se ajusta olhando a validação, que roda uma vez só.
- **Nenhuma alegação de novidade.** O teste é o T1 do J5 (`docs/PLANO_ANALISE_V2_PET_QUE_PENSA.md`), e o que este plano pergunta é se
  **este** pet, com **este** planejador, ainda passa nele quando percebe e anda pelo contrato.

**A base:** o desenho do T1 é o do plano do J5 com os adendos 5, 7 e 8, e os números são os do adendo 9. Este plano repete o que precisa
para ser lido sozinho, e diz só o que muda. Onde não diz nada, vale o do J5.

## 1. A pergunta e as predições

**A pergunta:** o pet com o planejador ainda deixa de escolher a fruta que passou a fazer mal, e o pet só com o hábito ainda não deixa,
quando os dois percebem pelo cone com oclusão e andam pelo controlador do contrato?

- **A origem:** é a P4-3 (a replicação corporificada do G-T1 do J5). O G-T1 passou na validação do adendo 8 (#370): `q`(P1-plan) −
  `q`(P1) = 0,197, IC95 [0,075; 0,323] (`docs/RESULTADO_V2_VALIDACAO_PET_QUE_PENSA_ADENDO8.md`).
- **O que muda entre o J5 e este plano:** só o mundo. O cérebro, o corpo, o dono, a fruta ao lado e o protocolo T1 são os mesmos. O mundo
  ganha os sensores e o controlador do contrato (seção 2).
- **O que não se pergunta:**
  - o T2 (a busca, o mapa), que fica com o plano próprio do J5;
  - se o pet "pensa": o rótulo R-7 continua sem valer;
  - o EXP-1, que tem plano próprio, depois.

**As predições** (o sentido fixado agora; são as do T1 no J5):

| braço | T1 | por quê |
|---|---|---|
| P1 | não passa | o hábito só muda pela consequência no mapa, e o teste vem antes dela |
| P1-plan | passa | o modelo do desfecho aprende pela mão |
| P1-plan-desfecho | passa | o desfecho aprende; o mapa congelado não importa no T1 |
| P1-plan-cong | não passa | os dois modelos congelados: o planejador decide pelo que já sabia |

## 2. O mundo, o pet e o dono

**Igual ao J5 com o adendo 8** (o plano do J5, seção 2, A5.1, A7.2, A8.3):
- o mundo físico com o layout padrão, as 9 árvores, a x sorteada por unidade;
- o paladar com a x como a favorita, a fruta ao lado da ração (`ConfigFrutaAoLado`);
- o corpo no regime "química";
- o cérebro A com a montagem do J5;
- o dono atencioso com o `DonoComLugar` no comedouro;
- sem genoma, a morte desligada;
- `D_a` = 7, a janela de 5 dias, a vida de 12 dias.

**O que muda: o contrato, ligado em toda vida deste plano** (a seção 3 da tarefa; os números do POC, PROPOSTOS e SEM FONTE):

| peça | com o contrato | hoje, no J5 |
|---|---|---|
| a visão | o cone de 120° (o `COS_MEIO_CONE` = 512 do POC) com o raio de hoje, e a oclusão | o disco do raio de hoje, sem oclusão |
| o que tapa a visão | **os troncos, opacos e sem colisão** (P4-4). As paredes ficam desligadas (W-4) | nada |
| os `vistos` e os `troncos` da percepção | só o que passa pelo cone e pela oclusão | tudo no disco |
| o andar | o controlador: o A* inteiro na grade, o bloqueio e o deslize, nos 15 ticks da decisão | o `passo_ate` em linha reta |
| o registro | a percepção de hoje, mais o `resultado` percebido e o `contato` | a percepção de hoje |
| a posição do pet | **fica** (W-3: o acesso privilegiado, marcado) | igual |

- **O cérebro não ganha entrada** (P4-2): ele recebe a `PercepcaoMundo` de hoje, montada pelo adaptador a partir dos sensores.
- **Nenhum número se recalibra** (P4-6): o `ganho_gosto` = S/2 e o `g_plano` = S, do adendo 9.
- **A orientação do pet:** o cone olha para onde o pet aponta, num de 16 setores. Como no POC (`web/app/poc/mundo3d/mundo.ts`), ela
  vem do último deslocamento; parado, fica a última, e começa no setor 0. Se o código da etapa 1 fixar outra regra (por exemplo, virar
  para o alvo sem andar), ela entra no adendo 1, antes do piloto.

## 3. Os braços e o protocolo

**Os braços** (P4-5): os quatro do J5, com os mesmos `g_plano` e congelamentos (o plano do J5, seção 3).

| braço | `g_plano` | o modelo do desfecho | o mapa |
|---|---|---|---|
| **P1** | 0 | observa (sem efeito) | observa (sem efeito) |
| **P1-plan** | S | aprende sempre | aprende sempre |
| **P1-plan-desfecho** | S | aprende sempre | congelado em `T_m` |
| **P1-plan-cong** | S | congelado em `T_m` | congelado em `T_m` |

**O protocolo:** só o T1, como no adendo 8.
1. **Os dias 0 a `D_a` − 1:** a x faz bem.
2. **Em `T_m`** (o primeiro passo do dono depois das 8 h do dia `D_a` com o pet acordado):
   - a x passa a fazer mal;
   - o dono dá a x na mão `n_mao` = 2 vezes, fora do orçamento;
   - as árvores do tipo x param de dar x, e as x caídas delas saem do chão (A8.3).
3. **O teste:** as oportunidades depois da última fruta na mão, numa janela de 5 dias.

**Uma vida por unidade e braço.** O T2 não roda.

**Os descritivos com outras chaves** (sem gate; as decisões PC-2 e PC-3):
- **a ponte** (PC-2): o P1 e o P1-plan **sem o contrato**, nas mesmas unidades, na validação. É o J5 do adendo 8 nas sementes novas;
- **as chaves separadas** (PC-3): o P1 e o P1-plan só com os sensores e só com o controlador, **só no piloto**.

## 4. As medidas

**As mesmas do T1 no J5** (A7.2, pela `metrics.oportunidade_ao_lado`; a `mudanca_de_escolha`):
- **Uma oportunidade:** uma decisão de **comer**, depois da última fruta na mão, em que a x madura posta pela regra está à vista junto com
  pelo menos uma alternativa ao lado (a ração madura ou outra fruta madura da regra). A fome não entra.
- **"À vista" é a percepção do pet** (PC-7): os `vistos` da decisão, que com o contrato já passaram pelo cone e pela oclusão. É a regra
  do J5 ("tiradas só da percepção"), aplicada à percepção nova.
- **O pet escolhe x** quando o alvo do comer é essa x.
- **O corte da reexperiência:** contam só as oportunidades até o primeiro consumo da x no mapa depois de `T_m`.
- **A primária, por unidade e braço:** `q` = `f_antes` − `f_depois`, nas 3 últimas oportunidades antes de `T_m` e nas 3 primeiras
  depois. Com menos de 3, usa as que houver. A unidade sem nenhuma, antes ou depois, sai contada como **sem oportunidade**.

**Os descritivos (sem gate):**

| medida | definição |
|---|---|
| o que o cone escondeu | em cada decisão de comer depois de `T_m`: a x da regra e as alternativas que estavam no disco de hoje, mas fora do cone ou atrás de um tronco. Lido da verdade do motor, só pela análise |
| as oportunidades | quantas por unidade, a latência até a primeira, as unidades sem oportunidade e o motivo de cada uma (o corte ou a janela), por braço |
| o andar | as decisões que pararam bloqueadas, o caminho andado contra a linha reta, e o tempo até chegar ao alvo, por braço |
| quanto o plano decide | a sonda "quem decidiu", por dia |
| os modelos | o Δ̂ de cada tipo contra o efeito real, por dia |
| o nível | `f_antes` e `f_depois` sozinhos |
| a ponte (PC-2) | o `q` do P1 e do P1-plan sem o contrato, e a diferença dos dois `q`, nas mesmas unidades |
| as chaves separadas (PC-3, só no piloto) | o `f_antes`, as oportunidades e o `q` com só os sensores e com só o controlador |
| o custo | o CPU por vida, por braço, e os bytes de log por dia |

## 5. A calibração

**Nenhuma** (P4-6). O piloto não escolhe número do cérebro nem do contrato.

## 6. O piloto, a margem e o N

**O piloto:** os 4 braços, mais os descritivos da PC-3, nas 20 unidades do piloto (seção 8). Serve para as premissas, a margem, o N e o
custo, e os números dele não entram como evidência.

**A G-REVAL-POSSIVEL** (A3.2) é refeita nas sementes novas, antes do piloto. Ela não lê vida nenhuma, e o contrato não muda a conta.

**A margem:** `Δ_T1` = ½ × a média de `f_antes` do P1-plan no piloto (a regra do J5, seção 6). Se for ≤ 0,05, a validação não roda, e o
plano volta ao Matheus.

**O N:** o menor K_u de 4 a **15** (PC-4) com poder simulado ≥ 0,8 no G-T1, a α = 0,05 (um primário só, PC-6).
- **O método:** o do J5. É um bootstrap das diferenças por unidade do piloto, deslocadas para a margem, com 2.000 réplicas por K_u,
  descontadas as unidades sem oportunidade na taxa do piloto.
- **Os secundários:** o poder deles sai só como relato; abaixo de 0,5, o gate é lido como subpotenciado.
- **Se nem K_u = 15 chega a 0,8,** a validação roda com 15, e o poder sai declarado.

**Se uma premissa falhar no piloto,** o piloto para e relata, e o plano volta ao Matheus. Nada se ajusta para ela passar.

**O adendo 1** deste plano traz a G-REVAL-POSSIVEL, as premissas do piloto, a margem, o K_u, o poder e o custo, num commit antes da
validação. Traz também o que a etapa 1 tiver fixado no contrato (seção 2).

## 7. Gates e regra de decisão

**O bootstrap:** sobre as unidades, agrupado por base, com 10.000 reamostragens, semente 4242 e IC95; o IC90 só na equivalência. O
replay de toda vida é conferido bit a bit (G1).

**Os gates de mecanismo,** conferidos em toda vida; um que falha para a run (falhar alto):
- **G-SEM-CREDITO:** os pesos de decisão e de alvo do A são os mesmos imediatamente antes e depois de cada fruta na mão;
- **o congelamento:** os modelos congelados não mudam depois de `T_m`;
- **o G2:** no P1, o termo do plano é zero em toda decisão;
- **G-CONTRATO:** as chaves do contrato estão ligadas em toda vida do primário (e desligadas nas da ponte), e o `meta.json` registra cada
  uma;
- **os troncos:** a conferência do `ModeloMundo` (o tronco percebido contra a conta da visão, "diverge, falha alto") usa a conta do cone.

**As premissas:**

| premissa | regra | se falha |
|---|---|---|
| **G-APRENDEU** | em cada braço, `f_antes` com o limite inferior do IC95 acima do acaso médio das oportunidades do braço (1/k, A7.2) | o T1 daquele braço é inconclusivo por premissa |
| **G-OPORTUNIDADE** | no máximo 25% das unidades sem oportunidade, por braço | o T1 daquele braço é inconclusivo por premissa |
| **G-REVAL-POSSIVEL** | a do adendo 3 (no máximo 25% das unidades falhando) | o T1 é inconclusivo por desenho; o piloto não roda |

**Os contrastes:**

| gate | contraste (por unidade) | regra | papel |
|---|---|---|---|
| **G-T1-C** | `q`(P1-plan) − `q`(P1), com o contrato | as categorias abaixo, a α = 0,05 | **primário** |
| G-T1-C-DESF | `q`(P1-plan-desfecho) − `q`(P1) | limite inferior do IC95 > 0, Holm de 2 | secundário: o desfecho sozinho passa |
| G-T1-C-CONG | `q`(P1-plan) − `q`(P1-plan-cong) | limite inferior do IC95 > 0, Holm de 2 | secundário: quem muda a escolha é o modelo que aprendeu |

**As categorias do primário,** exclusivas e lidas nesta ordem, com a margem `Δ_T1` do adendo 1:
1. **passa:** o limite inferior do IC95 > 0. Se o limite superior do IC90 < a margem, leva o rótulo **"abaixo de Δ"**;
2. **oposto:** o limite superior do IC95 < 0;
3. **equivalente:** o IC90 dentro de ± a margem;
4. **inconclusivo:** o resto.

**A leitura:**
- **O G-T1-C passa:** a revalorização pelo planejador sobrevive ao contrato. É o segundo Gate C, corporificado, **só para o T1**. O mapa
  continua não testado, e a tela continua sem "pensou" (R-7).
- **Equivalente:** com o contrato, o planejador não muda a escolha mais que o hábito. A ponte e "o que o cone escondeu" dizem se foi a
  percepção ou o andar; a ponte não é teste.
- **Inconclusivo, ou inconclusivo por premissa:** registrado como está, com o motivo das unidades sem oportunidade.
- **Oposto:** registrado; o motivo e a sonda dizem por quê.
- **O P1 passa** (o G-T1-C-DESF ou o primário com o sinal trocado): o primário leva o aviso "a assinatura não separa", como no J5.
- **A ponte** (PC-2) é descritiva. Uma diferença entre o `q` com e sem o contrato não é teste, e não se lê como "o contrato atrapalha".

## 8. Sementes

| uso | faixa | bases |
|---|---|---|
| o piloto (as premissas, a margem, o N, as chaves separadas) | **61101…61505** (nova) | 61101, 61202, 61303, 61404, 61505 (K_u = 4) |
| a validação (o primário e a ponte) | **62101…62505** (nova) | 62101, 62202, 62303, 62404, 62505 (K_u do adendo 1) |

- **O prefixo das unidades:** `"pet_que_pensa"` (PC-5), o do J5: a x, a permutação da fruta ao lado e o resto das rngs saem pelas mesmas
  derivações, e as unidades são outras porque as bases são outras.
- **Conferências em 2026-10-21,** no `origin/main` (`b27e58f`):
  - as duas faixas estão fora de `FAIXAS_RESERVADAS` (as últimas são 56101…56505 e 57101…57505, do crédito por canal) e de `FAIXAS_QUEIMADAS`;
  - `git grep -w` das bases em `.py`, `.md` e `.json` (fora os artefatos e os gabaritos) não acha uso na `main`;
  - **as faixas 58101…58505 e 59101…59505 foram evitadas:** a tarefa da V3-3 (`docs/TAREFA_V2_V3_COMPETICAO.md`, no branch
    `v2-v3-competicao`, ainda sem merge) as pede na CR-6.
- **O registro na `FAIXAS_RESERVADAS`** vai no primeiro PR de código da P4, antes de qualquer run (PC-1). Este PR é só de documento.

## 9. Riscos

| # | risco | o que o plano faz |
|---|---|---|
| R-1 | **O cone tira oportunidades,** e a G-OPORTUNIDADE volta a falhar (R-P1 da tarefa) | o piloto mede; o descritivo "o que o cone escondeu" diz quanto. Se a premissa falhar, o plano volta ao Matheus |
| R-2 | **O cone tira o aprendizado:** o pet vê menos a x antes de `T_m`, e a G-APRENDEU falha | igual ao R-1; nada se recalibra (P4-6) |
| R-3 | **O andar muda a dinâmica do dia,** e não a percepção (R-P5 da tarefa) | as chaves separadas no piloto (PC-3), como descritivo |
| R-4 | **A oportunidade pela percepção** muda o que conta como oportunidade entre o J5 e este plano | é a regra do J5 aplicada à percepção nova (PC-7). "O que o cone escondeu" mostra as decisões que o disco contaria |
| R-5 | **A ponte é lida como teste** | ela é descritiva e está escrita como tal na leitura (seção 7) |
| R-6 | **O mapa entra sem ter sido testado** (R-P4 da tarefa) | o G-T1-C-DESF separa o desfecho, e o relato não credita o mapa |
| R-7 | **O rótulo "pensa"** | não vale: o T2 não roda aqui |
| R-8 | **O custo:** o A* a cada tick | a G-CUSTO da etapa 1; o custo do piloto entra no N |
| R-9 | **Os troncos opacos mudam o mapa:** o pet vê menos troncos, e o `ModeloMundo` guarda menos lugares | é o mundo novo. Os troncos vistos por dia saem nos descritivos dos modelos |

## 10. O lugar dos adendos

- **Adendo 1:** a G-REVAL-POSSIVEL, as premissas, a margem, o N, o custo e o que a etapa 1 fixou no contrato (seção 6). É obrigatório
  antes da validação.
- **Nenhum adendo muda o primário deste plano.**

## 11. Artefatos e reprodução

- **As pastas:** `artifacts_v2_p4/piloto/` e `artifacts_v2_p4/validacao/`. Cada uma traz:
  - o `meta.json`, com o sha256 do pacote (`sha256_do_pacote`) e de `mundo.py`, do módulo do contrato, `modelo_mundo.py`, `lobos.py`,
    `config.py` e `engine.py`;
  - as chaves do contrato ligadas;
  - as medidas por braço. As vidas ficam fora do git.
- **As configs:** `experiments/configs/v2_p4/{piloto,validacao}.json`, com o campo `"plano"`.
- **A recusa:** a run se recusa a rodar se a pasta de saída já existe, e o piloto recusa as sementes da validação.
- **O orquestrador** pode ser o do J5 (`experiments/run_v2_validacao_pet_que_pensa.py`) com as chaves do contrato e só o T1, ou um novo.
  Isso é do código das etapas 3 e 4, não do plano.

## 12. Decisões do Matheus

Todas PROPOSTAS, com a recomendação primeiro.

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| **PC-1** | as faixas | **61101…61505 (o piloto) e 62101…62505 (a validação)**, registradas na `FAIXAS_RESERVADAS` no primeiro PR de código da P4 | a 58101 e a 59101: colidem com a CR-6 da V3-3, ainda num branch. Uma faixa do J5: as unidades já foram vistas |
| **PC-2** | a ponte | **sim, como descritivo:** o P1 e o P1-plan sem o contrato, nas mesmas unidades da validação (2 vidas a mais por unidade) | sem a ponte: se o G-T1-C falhar, não se sabe se as unidades novas passariam sem o contrato. Como teste: um segundo contraste, sem margem nem poder, que muda a pergunta |
| **PC-3** | as chaves separadas | **só no piloto, como descritivo:** o P1 e o P1-plan só com os sensores e só com o controlador | na validação: quatro vidas a mais por unidade e a tentação de ler como teste. Em lugar nenhum: um resultado ruim não diz se foi a percepção ou o andar |
| **PC-4** | o teto do N | **K_u de 4 a 15** (N até 75) | até 10, como no J5: lá o G-T1 ficou em 0,74 de poder a α 0,025; um negativo subpotenciado não diz nada. Até 15 custa no máximo 1,5 vez o CPU |
| **PC-5** | o prefixo das unidades | **`"pet_que_pensa"`, o do J5,** com as bases novas | um prefixo novo: uma linha na `PREFIXOS_UNIDADES` e derivações que não se comparam com as do J5 |
| **PC-6** | os testes | **um primário só (o G-T1-C, a α = 0,05)** e os dois secundários do T1 com o Holm de 2 | o Holm de 2 e de 4 do J5: menos poder sem razão, porque o T2 não roda aqui |
| **PC-7** | o que é "à vista" na oportunidade | **a percepção do pet,** pelo cone e pela oclusão | o disco de hoje (a verdade): decisões em que o pet não viu a x contariam como "não escolheu x", e o `f_antes` cairia por construção |

## 13. Referências

Só a do T1, do plano do J5, com o mesmo status de leitura. Nenhuma referência nova.

| referência | DOI | quanto foi lido | o que sustenta aqui |
|---|---|---|---|
| Adams e Dickinson (1981). Instrumental Responding following Reinforcer Devaluation. Q. J. Exp. Psychol. B | `10.1080/14640748108400816` | resumo (OpenAlex) | o T1: a aversão à comida, feita fora do contexto da resposta, reduz a resposta em extinção |
