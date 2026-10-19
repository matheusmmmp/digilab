# Plano de análise — V2: o pet que pensa (J5), o planejador de um alvo passa nos dois testes da DS-1?

Status (2026-10-13): **PROPOSTO**, registrado **antes de qualquer run**. É a etapa 5 de `docs/TAREFA_V2_PET_QUE_PENSA.md`. O desenho é
`docs/futuro/pet_que_pensa.md`, com **PQ-1 a PQ-7 DECIDIDAS** (2026-10-13). **PP-1 a PP-9 DECIDIDAS pelo Matheus
em 2026-10-13, todas pela recomendação** (seção 12).

**Regras deste plano:**
- Os números novos são PROPOSTOS, SEM FONTE, salvo onde citam um artefato.
- O que não está aqui é descritivo pós hoc.
- Nada se ajusta olhando a validação, que roda uma vez só.
- **Nenhuma alegação de novidade.** Planejar com um modelo aprendido já existe: a linha do Dyna (Sutton 1990) e o MuZero (Schrittwieser
  et al. 2020), as duas lidas só pelo título. Os testes vêm da psicologia animal (Adams e Dickinson 1981) e da comparação entre SR e
  modelo (Momennejad et al. 2017). O que este plano testa é se **este** pet, com **este** planejador, passa neles.

## 1. A pergunta e as predições

**A pergunta (DS-1):** o pet com o planejador muda a escolha depois de uma mudança no mundo que ele não reexperimentou, e o A de hoje não?

O par de testes separa as peças:
- **o teste 1, a revalorização (T1):** o efeito de uma fruta muda, e o pet fica sabendo **fora do mapa**, comendo-a na mão do dono;
- **o teste 2, a mudança de transição (T2):** a fruta passa a cair em outras árvores, e o pet vê isso **sem comer**.

**As predições** (sentido fixado agora; seção 3 para os braços):

| braço | T1 | T2 | por quê |
|---|---|---|---|
| P1 | não passa | não passa | o hábito só muda pela consequência no mapa, e o teste vem antes dela |
| P1-plan | passa | passa | o modelo do desfecho aprende pela mão, e o mapa pelo que o pet vê |
| P1-plan-desfecho | passa | não passa | o desfecho aprende, mas o mapa fica congelado na mudança |
| P1-plan-cong | não passa | não passa | os dois modelos congelados na mudança: o planejador decide pelo que já sabia |

O padrão "passa no T1, falha no T2" é o da SR em Momennejad et al. (2017, resumo): flexível à recompensa, insensível à transição. O
P1-plan-desfecho é o braço que imita esse padrão por construção.

**Por que não a tarefa de dois passos:** Akam, Costa e Dayan (2015, resumo) mostram que estratégias sem modelo produzem nela a assinatura
atribuída ao controle com modelo. O par T1 + T2, com os dois braços de controle, é o que o desenho põe no lugar (R-1).

## 2. O mundo, o pet e o dono

| item | valor | fonte |
|---|---|---|
| mundo | o físico, layout padrão, com os números da calibração do mundo (`m` = 1) | `docs/RESULTADO_V2_CALIBRACAO_MUNDO.md`; PMF-6 |
| as árvores | as 9 do `LAYOUT_MUNDO_PADRAO`, 3 de cada tipo: `a` (J1, M1, M4), `b` (J2, M2, M5), `c` (J3, M3, M6) | `digilab/config.py` |
| **a fruta x** | sorteada por unidade, `derivar_semente("pet-que-pensa-x", s)`, uniforme entre `a`, `b` e `c` | PROPOSTO |
| **a fruta y** (só no T2) | sorteada entre as outras duas, `derivar_semente("pet-que-pensa-y", s)` | PROPOSTO |
| os efeitos antes da mudança | **a x faz bem** (o humor sobe `efeito_humor_ruim`, o "bem" do casado); as outras duas são neutras | PROPOSTO |
| o corpo | o regime "química" (PP-3) | `docs/TAREFA_V2_CORPO_DRIVES.md` |
| o cérebro | o A no P1 (a consequência com a E2), no ponto da K2, com a montagem completa, o alvo aprendido (#255), a presença da fruta no mundo (#269) e as classes por árvore (etapa 2b, PP-2). Sem recalibrar (M10) | tarefa, seção 3 |
| o dono | o atencioso, com orçamento de 16 interações por dia, só com o cuidado (PMF-3), com o `DonoComLugar` no comedouro | PMF-3 e PMF-4 do mundo |
| o genoma | sem genoma (temperamento neutro) | como os dois pets |
| morte | desligada | — |

**A vida** tem `D_a` dias de aprendizado e a janela do teste: `D_a` = 7 e a janela de 3 dias, 10 dias no total (PP-4).

## 3. Os braços e os protocolos

**Os braços.** Todos têm o mesmo cérebro A, com o mesmo hábito (o alvo aprendido com as classes por árvore). Muda só o planejador:

| braço | `g_plano` | o modelo do desfecho | o mapa |
|---|---|---|---|
| **P1** | 0 | observa (sem efeito) | observa (sem efeito) |
| **P1-plan** | o da calibração | aprende sempre | aprende sempre |
| **P1-plan-desfecho** | o da calibração | aprende sempre | **congelado no tick da mudança** |
| **P1-plan-cong** | o da calibração | **congelado no tick da mudança** | **congelado no tick da mudança** |

**Uma correção ao desenho.** A tabela da seção 5 de `docs/futuro/pet_que_pensa.md` diz "o mapa congelado no nascimento" para o
P1-plan-desfecho. Com o mapa no prior 0 o planejador não liga árvore a fruta, então o braço também falharia no T1. Com isso ele deixaria de
separar as duas peças. Este plano congela o mapa **no tick da mudança**, como no P1-plan-cong, que é o que a coluna da predição pede. Fica
registrado em `docs/REGISTRO_DESVIOS.md` e como PP-8.

**Os dois protocolos** são vidas separadas da mesma unidade. Antes do tick da mudança, as duas vidas são a mesma (o mesmo mundo e os
mesmos efeitos).

**O tick da mudança** é `T_m` = o primeiro passo do dono depois das 8 h do dia `D_a` em que o pet está acordado (PP-5).

**T1, a revalorização (PQ-4):**
1. **Os dias 0 a `D_a` − 1:** a x faz bem, e o pet aprende no mapa onde ela cai.
2. **Em `T_m`:** o efeito da x passa a **fazer mal** (`efeito_humor_ruim`), pela troca do efeito gravada no registro (a do mutável e do
   `MotorMundoTroca`). No mesmo passo, o dono dá a x **na mão** `n_mao` = 2 vezes, fora do orçamento (PP-5). Pela G-SEM-CREDITO, isso
   chega só ao modelo do desfecho.
3. **O teste:** as oportunidades depois da última fruta na mão (seção 4).

**T2, a mudança de transição:**
1. **Os dias 0 a `D_a` − 1:** os mesmos do T1.
2. **Em `T_m`:** as árvores da x passam a dar y, e as da y passam a dar x, pela troca de tipo por árvore da etapa 3. Os efeitos não
   mudam. O pet não recebe nada na mão.
3. **O teste:** as buscas da x de memória, depois que o pet **viu** a x perto de uma árvore nova (seção 4).

## 4. As medidas

**As oportunidades.** São tiradas só da percepção e do que o motor registra, iguais em todos os braços. Nunca leem os modelos.
- **Uma oportunidade do T1** é uma decisão do pet depois da última fruta na mão, com a fome (o receptor) ≤ S/2, em que há um alvo de x
  disponível (a x à vista, ou uma árvore do tipo x entre os troncos que o pet já viu) e ao menos um alvo que não é de x. O pet **escolhe
  x** quando a ação tem alvo e o alvo é a x ou uma árvore do tipo x. Comer outra coisa, explorar outro alvo ou ficar ocioso conta como
  não escolher x.
- **Uma busca do T2** é uma decisão com a fome ≤ S/2 e **sem a x à vista**, em que o alvo escolhido é uma árvore do tipo x de antes (as
  velhas) ou do tipo x de depois (as novas). A busca **vai às novas** quando o alvo é uma árvore nova.
- **A exposição do T2:** o primeiro tick depois de `T_m` em que uma x madura aparece nos `vistos` do pet a até `raio_ancora` de uma árvore
  nova. Só contam as buscas depois dela.
- **O corte da reexperiência:** em cada teste, contam só as oportunidades até o primeiro consumo de x no mapa depois de `T_m`. A
  oportunidade que leva a esse consumo conta, e as seguintes não.
- **Antes:** a mesma definição nas últimas 3 oportunidades (ou buscas) antes de `T_m`. No T2, "antes" as árvores novas ainda são as da y.

**As primárias, por unidade e braço** (PP-7: a mudança dentro da unidade, não o nível depois):
- **T1:** `q` = `f_antes` − `f_depois`, a queda na fração de oportunidades em que o pet escolhe x. São as 3 últimas antes e as 3
  primeiras depois.
- **T2:** `m` = `n_depois` − `n_antes`, a subida na fração de buscas que vão às árvores novas. São as 3 últimas antes e as 3 primeiras
  depois da exposição.
- Com menos de 3 oportunidades, usa as que houver. A unidade sem nenhuma, antes ou depois, sai contada como **sem oportunidade** (R-2) e
  fica fora do contraste daquele teste.

**Os descritivos (sem gate):**

| medida | definição |
|---|---|
| quanto o plano decide | a fração das decisões com alvo em que a sonda "quem decidiu" muda a escolha, por dia |
| os modelos | o Δ̂ de cada tipo contra o efeito real, e o mapa de cada árvore contra o tipo real, por dia |
| o desempenho | o `D_FE` e a privação (as medidas do plano do mundo), na fase 1 e na janela do teste |
| a deriva | a JSD ao prior herdado no fim de cada dia, como a da bancada |
| o custo | µs por decisão e bytes de log por dia, por braço |
| a legibilidade | a fração das decisões com o fator do plano no motivo, e os textos dele |
| as oportunidades | quantas por unidade, a latência até a primeira e as unidades sem oportunidade, por braço e teste |
| o nível | `f_depois` e `n_depois` sozinhos |
| a forma pelo estado (R-4) | não roda neste plano. Entra num adendo, só descritiva |

## 5. A calibração (só o `g_plano`, sem o primário)

**Só o `g_plano` se calibra** (PP-6). Os números dos modelos ficam PROPOSTOS e iguais em todos os braços.

- **A grade:** `g_plano` ∈ {S/4, S/2, S}.
- **O que roda:** o P1-plan só na fase 1 (os dias 0 a `D_a` − 1), nas 20 unidades de calibração (seção 8). A fase 1 é a mesma nos dois
  protocolos, então uma vida por unidade e ponto serve aos dois. Nenhuma calibração vê a mudança, então não tem como ler o primário.
- **A medida da regra:** a fração das decisões com alvo em que o termo do plano muda a escolha (a sonda), nos dias 4 a 6.
- **A regra:** o **menor** `g_plano` com a média dessa fração em [0,10; 0,40] (R-3: o planejador soma, não domina). Se nenhum ponto cai
  na faixa, fica o mais perto dela, com o desvio declarado.
- **A regra não lê** a escolha de x (`f_antes`), nem um contraste entre braços.

## 6. O piloto, a margem e o N

**O piloto:** no `g_plano` escolhido, os 4 braços × os 2 protocolos, nas mesmas 20 unidades. Serve para a premissa, a margem, o N e o
custo. Os números dele não entram como evidência.

**As margens, na escala de cada medida** (a convenção de "metade" da regra 6.3 do experimento maior):
- `Δ_T1` = ½ × a média de `f_antes` do P1-plan no piloto. É a metade da queda máxima, de `f_antes` a 0.
- `Δ_T2` = ½ × a média de (1 − `n_antes`) do P1-plan no piloto. É a metade da subida máxima, de `n_antes` a 1.
- Se uma margem for ≤ 0,05 (PROPOSTO), aquele teste não tem espaço para mostrar mudança, e a validação não roda: o plano volta ao Matheus.

**O N:** o menor K_u (unidades por base) de 4 a 10 com poder simulado ≥ 0,8 nos **dois** primários, a α/2 cada (o Holm de dois).
- **O método:** um bootstrap das diferenças por unidade do piloto, deslocadas para a margem, com 2.000 réplicas por K_u, descontadas as
  unidades sem oportunidade na taxa do piloto.
- **Os secundários:** o poder de cada um sai só como relato; abaixo de 0,5, o gate é lido como subpotenciado.
- **Se nem K_u = 10 chega a 0,8,** a validação roda com 10, e o poder sai declarado.

**O custo esperado,** antes do piloto: a calibração do mundo mediu de 3,86 a 7,93 s de CPU por vida de 14 dias, sem o planejador
(`docs/RESULTADO_V2_CALIBRACAO_MUNDO.md`, seção 5). Com vidas de 10 dias, 8 vidas por unidade e N = 50, seriam 400 vidas, menos de 1 h de
CPU. O custo real do planejador sai do piloto.

**O adendo 1:** o `g_plano`, as margens, o K_u, o poder e o custo entram num commit antes da validação.

## 7. Gates e regra de decisão

**O bootstrap:** sobre as unidades, com 10.000 reamostragens, semente 4242 e IC95; o IC90 só na equivalência. O replay de toda vida é
conferido bit a bit (G1).

**Os gates de mecanismo,** conferidos em toda vida da validação; um que falha para a run (falhar alto):
- **G-SEM-CREDITO:** no T1, os pesos de decisão e de alvo do A são os mesmos imediatamente antes e depois de cada fruta na mão;
- **o congelamento:** os modelos congelados não mudam depois de `T_m`, no P1-plan-desfecho (o mapa) e no P1-plan-cong (os dois);
- **o G2:** no P1, com `g_plano` 0, o termo do plano é zero em toda decisão.

**As premissas:**

| premissa | regra | se falha |
|---|---|---|
| **G-APRENDEU** | em cada braço, `f_antes` com o limite inferior do IC95 acima de 1/3 (a fração de x entre os 3 tipos). Vale para os dois testes, porque a fase 1 é a mesma | o primário daquele braço é **inconclusivo por premissa**: o pet não aprendeu a x, e não há o que revalorizar nem buscar |
| **G-OPORTUNIDADE** | no máximo 25% das unidades sem oportunidade, por braço e teste | o teste daquele braço é **inconclusivo por premissa** |
| **G-EXPOSICAO** (T2) | no máximo 25% das unidades sem exposição até o fim da janela | o T2 é **inconclusivo por premissa**: o pet não viu a x cair no lugar novo |

**Os contrastes:**

| gate | contraste (por unidade) | regra | papel |
|---|---|---|---|
| **G-T1** | `q`(P1-plan) − `q`(P1) | as categorias abaixo, com Holm de 2 | **primário** |
| **G-T2** | `m`(P1-plan) − `m`(P1-plan-desfecho) | as categorias abaixo, com Holm de 2 | **primário** |
| G-T1-DESF | `q`(P1-plan-desfecho) − `q`(P1) | limite inferior do IC95 > 0, Holm de 4 | secundário: o desfecho sozinho passa no T1 |
| G-T1-CONG | `q`(P1-plan) − `q`(P1-plan-cong) | limite inferior do IC95 > 0, Holm de 4 | secundário: no T1, quem muda a escolha é o modelo que aprendeu, não o planejador |
| G-T2-HAB | `m`(P1-plan) − `m`(P1) | limite inferior do IC95 > 0, Holm de 4 | secundário: o hábito não passa no T2 |
| G-T2-CONG | `m`(P1-plan) − `m`(P1-plan-cong) | limite inferior do IC95 > 0, Holm de 4 | secundário: no T2, quem muda a escolha é o mapa que aprendeu |

**O G-T2 é contra o P1-plan-desfecho, não contra o P1.** É o contraste que isola o mapa: os dois braços têm o mesmo planejador e o mesmo
desfecho, e só o mapa difere depois da mudança.

**As categorias dos primários** são exclusivas e lidas nesta ordem (a ordem do PR #196), com a margem do teste (`Δ_T1` ou `Δ_T2`):
1. **passa:** o limite inferior do IC95, ajustado pelo Holm, > 0. Se o limite superior do IC90 < a margem, leva o rótulo **"abaixo de Δ"**;
2. **oposto:** o limite superior do IC95 < 0;
3. **equivalente:** o IC90 dentro de ± a margem;
4. **inconclusivo:** o resto.

**A leitura:**
- **G-T1 e G-T2 passam:** o pet com o planejador planeja no sentido da DS-1. Só então a tela pode dizer "pensou", e só com o fator do plano
  no motivo (R-7). Os secundários dizem se cada peça faz o que o desenho diz.
- **Só o G-T1 passa:** o modelo do desfecho funciona e o mapa não. Os descritivos dizem se o mapa não aprendeu (o mapa contra o tipo
  real) ou se aprendeu e não decidiu (a sonda).
- **Só o G-T2 passa:** o mapa funciona e a revalorização pela mão não chega à escolha. Os descritivos dizem se o Δ̂ da x mudou depois da
  mão.
- **Nenhum passa:** o planejador, como está, não muda a escolha do pet nestes testes. Fica registrado como resultado negativo do J5,
  com a sonda e os modelos como diagnóstico. Nada se recalibra olhando a validação.
- **Um primário oposto:** registrado. O planejador muda a escolha no sentido contrário ao modelo; o motivo e a sonda dizem por quê.
- **O P1 passa num teste** (G-T1-DESF ou G-T2-HAB com o sinal trocado): o hábito sozinho mostra a assinatura, que é o R-1. O primário
  daquele teste fica com o aviso "a assinatura não separa".

## 8. Sementes

| uso | faixa | bases |
|---|---|---|
| calibração do `g_plano` e piloto | **45101…45505** | 45101, 45202, 45303, 45404, 45505 (K_u = 4) |
| validação | **46101…46505** | 46101, 46202, 46303, 46404, 46505 (K_u do adendo) |

- **O prefixo de unidades:** `"pet_que_pensa"`, para a semente e o genoma (o padrão da bancada).
- **Conferências em 2026-10-13,** no `origin/main` (`d1bca65`) e nos branches remotos:
  - as duas faixas estão fora de `FAIXAS_RESERVADAS` (a última é 44101…44505, da rede de si) e da `FAIXAS_QUEIMADAS`;
  - elas também ficam fora das faixas propostas e ainda não registradas: 23101…27505 (`docs/LEITURA_PARCIAL_V2_FASE1.md`) e 35101…36505
    (`docs/PLANO_ANALISE_V2_TRANSFERENCIA_REJEICAO.md`);
  - `git grep -w` das bases em `.py`, `.md` e nas configs não acha uso, na `main` nem nos branches remotos.
- **O D registra** as faixas e o prefixo, com a fonte deste plano (tarefa, etapa 4).

## 9. Riscos

| # | risco | o que o plano faz |
|---|---|---|
| R-1 | **A assinatura falsa:** um hábito sofisticado passa num teste | os dois braços de controle prevêem resultados diferentes, e o secundário do P1 diz se o hábito sozinho mostra a assinatura (seção 7) |
| R-2 | **A oportunidade não chega,** ou chega sem fome | a janela de 3 dias e a fome ≤ S/2 estão fixadas; as unidades sem oportunidade saem contadas, e a G-OPORTUNIDADE decide |
| R-3 | **O planejador domina** | o `g_plano` se calibra pela sonda, na faixa [0,10; 0,40], sem ler o primário |
| R-4 | **A forma pelo estado** confunde a revalorização com a saciedade específica | não roda aqui; a primária é a da mão |
| R-5 | **O mapa aprende do que vê**, e o hábito também muda pelo que vê | o T2 conta só as buscas **sem a x à vista** |
| R-6 | **O efeito ruim na mão mexe no humor** de todos os braços | é igual em todos, porque a mão vem no mesmo passo. O humor na janela sai como descritivo |
| R-7 | **O rótulo "pensa"** | só com os dois primários e o fator do plano no motivo |
| R-8 | **O custo** do planejador em toda decisão com alvo | medido no piloto; vai no adendo, com o teto de tempo do Matheus |
| R-9 | **A troca do T2 muda o que cai perto de onde o pet está** | é o mundo. A distância às árvores novas e às velhas, na exposição, sai como descritivo |
| R-10 | **O "antes" do T2 é baixo por construção** (a y é neutra e a x faz bem), e a subida fica grande | a margem `Δ_T2` vem do próprio `n_antes` do piloto, e o contraste é entre braços com o mesmo "antes" |

## 10. O lugar dos adendos

- **Adendo 1:** o `g_plano`, as margens, o N e o custo (seção 6). É obrigatório antes da validação.
- **Adendo 2, a forma pelo estado do T1 (R-4):** só descritiva, com a saciedade específica no lugar da mão. Fica depois da validação, se o
  Matheus quiser.
- **Nenhum adendo muda os primários deste plano.**

## 11. Artefatos e reprodução

- **As pastas:**
  - `artifacts_v2_pet_que_pensa/calibracao/`, com `g_plano.json` e o `piloto/`;
  - `artifacts_v2_pet_que_pensa/validacao/`.

  Cada uma traz `meta.json` (o sha256 de `mundo.py`, `modelo_mundo.py`, `lobos.py`, `config.py` e `engine.py`) e os registros das vidas.
- **As configs:** `experiments/configs/v2_pet_que_pensa/{calibracao,validacao}.json`, com o campo `"plano"`.
- **A recusa:** a run se recusa a rodar se a pasta de saída já existe, e a calibração recusa as sementes da validação.

## 12. Decisões do Matheus

**DECIDIDAS em 2026-10-13: PP-1 a PP-9, todas como recomendado** (a coluna "recomendação" é o que vale). As PQ-1 a PQ-7 do desenho e
a TP-1 e a TP-2 também estão decididas.

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| PP-1 | Os candidatos de árvore lembrada no motor | **sim:** no explorar, o motor oferece `arvore:<id>` de cada tronco que o pet já viu, depois dos candidatos de hoje. O padrão do motor e o instinto nunca os escolhem | sem eles: o pet só vai a uma árvore que está vendo, e o T2 (a busca de memória) não tem como acontecer |
| PP-2 | As classes de alvo por árvore no hábito | **sim:** uma classe por árvore nas regras em que o explorar é candidato (3 × 9 = 27 pesos), com o teto do plano em 1000 (o padrão da TP-1). Só sobe, até 2000, por adendo, se a contagem da etapa 2b passar de 1000 | sem elas: o hábito não sabe "ir ao J2", e o T1 compara o planejador com um hábito que não sabe ir a lugar nenhum. É um positivo falso |
| PP-3 | O regime do corpo | **o regime "química", com o metabolismo no ponto do passo 0 do corpo** (A3.2b), depois que a calibração do corpo rodar. É o que a seção 7 do desenho pede para o valor do desfecho ter escala | sem o metabolismo: o custo de andar fica sem a escala do combustível, e o J5 não é comparável com o J2. Com os drives novos: o tédio e a solidão mexem nas oportunidades, e a fome deixa de ser a única razão para buscar |
| PP-4 | A vida e a janela | **`D_a` = 7 dias de aprendizado, janela de 3 dias, as 3 primeiras oportunidades** | `D_a` menor: a G-APRENDEU falha, e o teste não tem o que medir. Janela maior: mais reexperiência e mais custo, sem mudar a primeira oportunidade |
| PP-5 | A fruta na mão | **`n_mao` = 2, no mesmo passo do dono da mudança (`T_m`)**, no primeiro passo depois das 8 h do dia `D_a` com o pet acordado | uma só: com um passo do desfecho de S/4, o Δ̂ anda só um quarto, e o planejador pode não virar. Mais: o humor de todos os braços cai mais, e o teste fica longe do desenho de Adams e Dickinson |
| PP-6 | O que se calibra | **só o `g_plano`**, na grade {S/4, S/2, S}, pela sonda. Os números dos modelos ficam PROPOSTOS: `passo_desfecho` S/4, `passo_mapa` S/8, `raio_ancora` 2 células, `teto_plano` 2S e `teto_modelo` 200 inteiros. Pela conta do desenho, no regime química são 76: 5 tipos × 5 receptores mais 1 do andar, e 10 lugares × 5 tipos. A etapa 1 confere a conta | calibrar tudo: muitos pontos e o risco de ajustar a favor do primário |
| PP-7 | A forma da primária | **a mudança dentro da unidade** (`q` e `m`), não o nível depois | o nível só: um planejador que nunca aprendeu a x "passa" no T1 por nunca ter ido a ela |
| PP-8 | O P1-plan-desfecho | **o mapa congelado no tick da mudança** (a correção da seção 3) | congelado no nascimento: o mapa vazio não liga árvore a fruta, o braço falha nos dois testes, e o G-T2 deixa de isolar o mapa |
| PP-9 | As faixas de sementes | **45101…45505** (calibração e piloto) e **46101…46505** (validação), com o prefixo `pet_que_pensa` | uma colisão tira o "novo" das unidades |

## 13. Referências

Todas da seção 10 de `docs/futuro/pet_que_pensa.md`, com o mesmo status de leitura. Nenhuma referência nova.

| referência | DOI | quanto foi lido | o que sustenta aqui |
|---|---|---|---|
| Adams e Dickinson (1981). Instrumental Responding following Reinforcer Devaluation. Q. J. Exp. Psychol. B | `10.1080/14640748108400816` | resumo (OpenAlex) | o T1: a aversão à comida, feita fora do contexto da resposta, reduz a resposta em extinção |
| Akam, Costa e Dayan (2015). Simple Plans or Sophisticated Habits? PLoS Comput Biol | `10.1371/journal.pcbi.1004648` | resumo | não usar a tarefa de dois passos sozinha |
| Momennejad et al. (2017). Nat Hum Behav | `10.1038/s41562-017-0180-8` | resumo | o padrão do P1-plan-desfecho: flexível à recompensa, insensível à transição |
| Dolan e Dayan (2013). Goals and Habits in the Brain. Neuron | `10.1016/j.neuron.2013.09.007` | resumo | metas e hábitos como espectro: o termo soma, não substitui |
| Sutton (1990). ML Proceedings 1990 | `10.1016/b978-1-55860-141-3.50030-4` | só o título | que a linha existe; nenhuma afirmação de conteúdo |
| Schrittwieser et al. (2020). Nature 588 | `10.1038/s41586-020-03051-4` | só o título | que planejar com um modelo aprendido já existe; nenhuma afirmação de conteúdo |

## Adendo 1 — o `g_plano`, as margens, o N e o custo (2026-10-13, números da calibração e do piloto, congelados)

Seção 10 do plano. A calibração e o piloto rodaram uma vez cada, nas bases 45101…45505 (K_u = 4, 20 unidades), com a config
`experiments/configs/v2_pet_que_pensa/calibracao.json` sem mudança. O código é o dos commits `61d0be4` (a calibração) e `0b1e226` (o
piloto). Os números vêm de `artifacts_v2_pet_que_pensa/calibracao/g_plano.json` e `piloto/piloto.json`, e o relatório está em
`docs/RESULTADO_V2_CALIBRACAO_PET_QUE_PENSA.md`. Nada deste adendo foi escolhido olhando o primário.

- **A1.1, o `g_plano` = S (1024), fechou.** A média da fração da sonda nos dias 4 a 6 foi 0,0518 (S/4), 0,0410 (S/2) e **0,1001** (S). O
  menor ponto em [0,10; 0,40] é S, a 0,0001 da borda.
- **A1.2, as margens:**
  - **`Δ_T1` = 0,000:** a média de `f_antes` do P1-plan no T1 é 0 (12 unidades com oportunidade antes, nenhuma escolha de x);
  - **`Δ_T2` = 0,214:** ½ × a média de 1 − `f_antes` do P1-plan no T2 (7 unidades com busca antes).
  - **O T1 fica sem espaço (`Δ_T1` ≤ 0,05):** pela seção 6, **a validação não roda, e o plano volta ao Matheus.**
- **A1.3, o N: não calculado.** A regra pede o poder nos dois primários, e o G-T1 não tem margem. No T2, nenhuma unidade de nenhum braço
  teve busca depois da mudança, então o G-T2 também não tem diferença por unidade para simular.
- **A1.4, as premissas no piloto (só relato):**
  - **G-APRENDEU falha nos quatro braços:** `f_antes` 0 [0; 0];
  - **G-OPORTUNIDADE falha em todos os braços e testes:** de 30% a 45% das unidades ficam sem oportunidade no T1, e 100% no T2;
  - **G-EXPOSICAO falha:** de 35% a 45% das unidades ficam sem exposição.
- **A1.5, o custo:** 0,62 s de CPU por vida de 10 dias (P1 0,55; com o planejador, 0,63 a 0,64). Com 8 vidas por unidade, N = 50 daria
  400 vidas, cerca de 4 min de CPU.

## Adendo 3 — o paladar: a premissa dos testes pelo gosto (2026-10-13, PROPOSTO, antes de qualquer run com ele)

Status: **PROPOSTO**, registrado antes de qualquer vida com o paladar. Depende das decisões PL-1 a PL-9 de `docs/futuro/paladar.md` e das
PJ-1 a PJ-6 abaixo, todas do Matheus. O adendo 2 da seção 10 (a forma pelo estado, R-4) continua reservado e ainda não existe; este é o 3.

**Por que existe.** O piloto (adendo 1) mostrou que o mundo não dá ao pet razão para escolher a x: nenhum braço a escolhe antes da mudança,
e o T1 fica sem margem. A causa está no mundo, não no planejador (`docs/futuro/paladar.md`, seção 1): a ração nutre 3 vezes mais, cheira 2
vezes mais, está sempre perto, e o hábito não distingue ração de fruta. O Matheus mudou o desenho (2026-10-13): **as frutas têm gostos
diferentes, que atraem pets diferentes, e a ração tem um gosto básico e serve mais para a nutrição.** Este adendo põe o paladar no J5 sem
mudar a pergunta, as primárias, os contrastes, as categorias nem o Holm.

**O que não muda:**
- a pergunta (DS-1), os quatro braços e o que os separa (o planejador e o congelamento), os dois protocolos;
- `D_a` = 7, a janela de 3 dias, `n_mao` = 2 e `T_m`;
- as oportunidades (com a fome ≤ S/2), as buscas, a exposição e o corte da reexperiência;
- `q` e `m`, o G-T1 e o G-T2, os secundários, as categorias e o bootstrap;
- os gates de mecanismo (G-SEM-CREDITO, o congelamento, o G2) e as premissas G-APRENDEU, G-OPORTUNIDADE e G-EXPOSICAO.

### A3.1 O que muda no mundo, no corpo e no cérebro

| item | antes (seção 2) | com o paladar |
|---|---|---|
| o paladar | não existe | as três chaves ligadas em **todos os braços**: os perfis do mundo, o órgão do corpo e o canal `gosto` com as classes `comida:<tipo>` no cérebro (`docs/futuro/paladar.md`, seção 3) |
| o genoma | sem genoma | **o genoma do paladar**, sorteado da semente da unidade (rng `paladar-ovo`); o temperamento continua neutro |
| **a fruta x** | sorteada (`pet-que-pensa-x`), uniforme entre `a`, `b` e `c` | **a fruta de maior valor inato para o pet** (Σ_q h_q × perfil_q / C); em empate, sorteada entre as empatadas pela mesma rng `pet-que-pensa-x`. Pela forma girada dos perfis, a x continua uniforme entre os tipos sobre as unidades |
| a fruta y (T2) | sorteada entre as outras duas (`pet-que-pensa-y`) | igual |
| os efeitos antes da mudança | a x faz bem no humor, as outras são neutras | igual (PJ-2) |
| o T1 | o efeito da x no humor passa a fazer mal, e o dono dá a x na mão 2 vezes | igual. **O gosto da x não muda:** a revalorização é pela consequência (o humor), e o desfecho aprende o humor e o gosto juntos |
| o corpo | o regime química com o metabolismo (PP-3) | o mesmo, mais o órgão do Paladar |
| o `g_plano` | S (adendo 1) | **recalibrado** pela regra da seção 5 (A3.3, PJ-4) |

### A3.2 Uma premissa nova, mecânica: G-REVAL-POSSIVEL

O T1 só pode passar se, depois da mudança, comer a x valer menos do que a melhor alternativa. Com o gosto, isso deixa de ser certo: a x
continua a fruta de que o pet mais gosta.

- **A conta,** por unidade, só com os números da config e o genoma da unidade, sem simular. É o sinal do próprio cérebro (os drives com o
  ganho da consequência, a E2 e o canal do gosto com o `ganho_gosto` escolhido) para comer cada tipo maduro, num estado de referência
  fixo: fome, humor e energia em S/2 e a saciedade do paladar em zero. A x usa o efeito **depois** da mudança.
- **A regra:** a unidade passa se o sinal da x depois da mudança for menor que o da ração **ou** que o de outra fruta. A premissa passa
  com no máximo 25% das unidades falhando (a mesma tolerância da G-OPORTUNIDADE).
- **Quando roda:** depois da calibração do `ganho_gosto` (A3.3) e antes do piloto. Não lê nenhuma vida.
- **Se falha:** o T1 é **inconclusivo por desenho**; o piloto não roda e o plano volta ao Matheus. Nada se ajusta para ela passar.

### A3.3 A calibração, agora em dois passos

Só dois números se calibram, um depois do outro, nas sementes novas (A3.5). Nenhuma regra lê a escolha da x, `f_antes`, `q`, `m` nem um
contraste entre braços.

1. **O `ganho_gosto`** (PL-8):
   - **a grade:** {S/2, S, 2S} (PROPOSTO). Com os perfis e os `h_q` do desenho, o termo do gosto da fruta favorita fica entre 200 e 800,
     na escala da diferença entre o sinal da ração e o da fruta com a fome em 0,4 (cerca de 735);
   - **o que roda:** o **P1** (sem o planejador), só na fase 1, nas 20 unidades;
   - **a medida:** a fração de fruta madura (os três tipos juntos) entre os consumos no mapa, nos dias 4 a 6;
   - **a regra:** o **menor** ponto com a média dessa fração em [0,25; 0,60] (PROPOSTO). Sem ponto na faixa, fica o mais perto dela, com
     o desvio declarado, e a calibração segue (a faixa que não fecha não bloqueia).
2. **O `g_plano`:** a regra da seção 5 sem mudança (a grade {S/4, S/2, S}, a sonda nos dias 4 a 6, a faixa [0,10; 0,40]), com o
   `ganho_gosto` do passo 1.

Os dois números, a G-REVAL-POSSIVEL, as margens, o N e o custo vão num **adendo 4**, num commit antes da validação.

### A3.4 O piloto

Igual à seção 6, no `ganho_gosto` e no `g_plano` escolhidos e nas mesmas 20 unidades: as margens `Δ_T1` e `Δ_T2`, a regra do ≤ 0,05, o N
pelo poder simulado e o custo. As premissas saem relatadas, como no adendo 1.

### A3.5 Sementes

| uso | faixa | bases |
|---|---|---|
| calibração do `ganho_gosto` e do `g_plano`, e o piloto, com o paladar | **49101…49505** (nova; pedida ao coordenador) | 49101, 49202, 49303, 49404, 49505 (K_u = 4) |
| validação | **46101…46505** (a da seção 8; nunca rodada) | as da seção 8 |

A faixa 45101…45505 já foi usada pelo desenho sem o paladar e não volta, porque as unidades dela já foram vistas.

### A3.6 Os descritivos novos (sem gate)

- os consumos por tipo e por dia, e a fração de fruta, na fase 1 e na janela;
- o lugar da x na ordem do valor inato (1 por construção) e quantas vezes o pet comeu a x antes de `T_m`;
- a leitura dos receptores do paladar em cada consumo, a saciedade da ração e os pesos das classes `comida:<tipo>`, por dia;
- o Δ̂ do gosto de cada tipo no modelo do desfecho contra o perfil real, por dia;
- o sinal da G-REVAL-POSSIVEL por unidade.

### A3.7 Os riscos novos

| # | risco | o que o adendo faz |
|---|---|---|
| R-11 | **O gosto prende o pet na x mesmo depois da mudança** | a G-REVAL-POSSIVEL, antes do piloto |
| R-12 | **A fruta vira a comida principal e o pet passa fome** | a faixa do `ganho_gosto` tem teto em 0,60; o `D_FE` e a privação já são descritivos (seção 4) |
| R-13 | **O hábito (P1) aprende a x pelo gosto e passa no T2 sozinho** | é o R-1; o G-T2-HAB e o aviso "a assinatura não separa" da seção 7 continuam |
| R-14 | **A oportunidade continua não chegando** (a fome ≤ S/2 é rara com o atencioso) | a definição não muda agora; a G-OPORTUNIDADE decide no piloto, e o que fazer depois é outra decisão |

### A3.8 Quando roda

Só com o paladar inteiro na `main` (as etapas 1 a 4 de `docs/futuro/paladar.md`, seção 6), a faixa nova na `FAIXAS_RESERVADAS` e o sim do
Matheus para a run.

### A3.9 Decisões do Matheus (este adendo)

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| PJ-1 | Quem é a x | **a fruta de maior valor inato para o pet**, com o empate pela rng de antes | a x sorteada sem olhar o genoma: em cerca de 2/3 das unidades o pet prefere outra fruta, e a G-APRENDEU volta a falhar pelo mesmo motivo do adendo 1 |
| PJ-2 | O efeito da x antes da mudança | **manter "faz bem"** (a seção 2) | neutro: o teste fica só no gosto, mas o pet aprende menos a x e a premissa fica mais fraca. A mudança do T1 continua no humor dos dois jeitos |
| PJ-3 | Como calibrar o `ganho_gosto` | **pela fração de fruta entre os consumos, em [0,25; 0,60], com o P1** | pela escolha da x: a calibração lê a premissa a favor de si mesma. Sem calibrar: um número escrito à mão decide se o pet come fruta |
| PJ-4 | O `g_plano` | **recalibrar** pela regra da seção 5, depois do `ganho_gosto` | reaproveitar o S do adendo 1: com o gosto a sonda muda, e o planejador pode dominar ou sumir |
| PJ-5 | As sementes | **49101…49505 para a calibração e o piloto; a validação continua em 46101…46505** | reusar 45101…45505: as unidades já foram vistas sem o paladar. Uma faixa de validação nova não é preciso, porque a 46101 nunca rodou |
| PJ-6 | A G-REVAL-POSSIVEL | **sim, antes do piloto, como premissa mecânica** | sem ela, um T1 que não passa pode ser só o gosto vencendo a consequência, e o resultado negativo seria lido como falha do planejador |

## Adendo 4 — o `ganho_gosto`, o `g_plano`, a G-REVAL-POSSIVEL e o piloto com o paladar (2026-10-14, números congelados)

O adendo 3 (A3.3) pede este adendo. A calibração e o piloto rodaram uma vez, nas bases 49101…49505 (K_u = 4, 20 unidades), com a config
`experiments/configs/v2_pet_que_pensa/calibracao_paladar.json` sem mudança e o código da `main` `9b1f5c6`. Os números vêm de
`artifacts_v2_pet_que_pensa/calibracao_paladar/` (o commit `98342da`), e o relatório está em
`docs/RESULTADO_V2_CALIBRACAO_PET_QUE_PENSA_PALADAR.md`. Nada foi escolhido olhando o primário.

- **A4.1, o `ganho_gosto` = S/2 (512), "não fechou".** A média da fração de fruta nos dias 4 a 6 foi 0,2024 (S/2), 0,1960 (S) e 0,1960
  (2S). Nenhum ponto cai em [0,25; 0,60], e fica o mais perto, a 0,048 abaixo da faixa (a faixa que não fecha não bloqueia).
- **A4.2, o `g_plano` = S (1024), fechou.** A média da sonda foi 0,0447 (S/4), 0,0801 (S/2) e **0,1155** (S).
- **A4.3, a G-REVAL-POSSIVEL passa:** 0 de 20 unidades falham. A x depois da mudança vale menos que a ração em todas.
- **A4.4, as margens:**
  - **`Δ_T1` = 0,000:** `f_antes` do P1-plan no T1 é 0 nas 15 unidades com oportunidade antes;
  - **`Δ_T2` = 0,300:** 10 unidades com busca antes.
  - **O T1 fica sem espaço (`Δ_T1` ≤ 0,05):** pela seção 6, **a validação não roda, e o plano volta ao Matheus.**
- **A4.5, o N: não calculado.** O G-T1 não tem margem, e o G-T2 não tem nenhuma unidade com busca depois da mudança.
- **A4.6, as premissas no piloto (só relato):**
  - **G-APRENDEU falha nos quatro braços:** `f_antes` 0 [0; 0];
  - **G-OPORTUNIDADE falha em todos os braços e testes:** de 6 a 7 das 20 unidades sem oportunidade no T1, e 20 de 20 no T2;
  - **G-EXPOSICAO falha:** de 10 a 12 das 20 unidades sem exposição.
- **A4.7, o custo:** 0,71 s de CPU por vida de 10 dias (P1 0,61; com o planejador, 0,74). A run inteira levou cerca de 5 min com 3 e 4
  processos.

## Adendo 5 — a fruta ao lado da ração (2026-10-14, PROPOSTO, antes de qualquer run com ela)

Status: registrado antes de qualquer vida com a fruta ao lado da ração. **As decisões PJ5-1 a PJ5-6 estão DECIDIDAS pelo Matheus em
2026-10-18, todas pela recomendação** (A5.10). A run ainda pede o sim dele (A5.9).

**Por que existe:**
- **O adendo 4 voltou ao Matheus,** com o T1 sem margem: nenhum braço escolhe a x antes da mudança, mesmo com o paladar.
- **O descritivo** (`docs/RESULTADO_V2_CALIBRACAO_PET_QUE_PENSA_PALADAR.md`, seção 4):
  - a ração é o tipo mais comido nas 20 unidades;
  - o querer aprendido (`comida:<tipo>`) vai à ração, e não à favorita;
  - a oportunidade do T1 pede a fome ≤ S/2, justamente onde a nutrição da ração domina.
- **A decisão do Matheus (2026-10-14):** o J5 segue pelo RP-2 do desenho do paladar (`docs/futuro/paladar.md`, seção 8). **O dono põe
  a fruta ao lado da ração.** É a imagem original dele: um animal atraído por uma comida diferente posta ao lado da sua ração.

**O que não muda:**
- a pergunta (DS-1), os quatro braços e o que os separa;
- os dois protocolos, `D_a` = 7, a janela de 3 dias, `n_mao` = 2 e `T_m`;
- o paladar do adendo 3 (os perfis, o órgão, o canal `gosto`, as classes `comida:<tipo>`, a x como a favorita);
- o T2 inteiro (a busca, a exposição, `m`);
- as categorias, o bootstrap, o Holm e os gates de mecanismo.

### A5.1 A fruta ao lado da ração

A proposta é do A, que implementa o lado do mundo e do dono, com uma troca de posição (abaixo).

| item | regra | status |
|---|---|---|
| quando | **toda vez que o dono deixa a ração no comedouro** (o `deixar_comida("racao", …)` do `DonoComLugar`, no estilo `comedouro`), no mesmo passo, logo depois dela | PROPOSTO |
| quais e quantas | **as três frutas, uma de cada, maduras.** No máximo uma de cada tipo "ao lado" no chão ao mesmo tempo: o dono só repõe a que foi comida, apodreceu ou sumiu. O chão não enche, e a ração e as três frutas ficam lado a lado | PROPOSTO (o A) |
| onde | **as três na coluna de células do lado de fora do comedouro,** longe do ninho: o comedouro é a célula (10, 15) e o ninho a (4, 15), então as frutas ficam nos centros das células (11, 14), (11, 15) e (11, 16). **Qual tipo vai em qual célula é sorteado uma vez por unidade** pela rng própria `fruta-ao-lado`, `derivar_semente("fruta-ao-lado", s)` (uma permutação de `a`, `b`, `c`), e fica fixo na vida. Vindo do ninho, a ração fica mais perto, e o alvo padrão do motor (a comida boa mais perto) tende à ração: escolher uma fruta pede preferência (A5.6) | PROPOSTO (troca sobre a proposta do A, que punha cada tipo numa direção fixa) |
| a fruta | madura ao ser posta (a regra de hoje do `Mundo.situacao`: madura até `maduro_fruta_min`, depois podre), com o efeito daquele tick (a x faz bem antes de `T_m` e faz mal depois, no T1) | DECIDIDO pelo motor de hoje |
| o orçamento e o contato | **fora do orçamento e sem contato** (o B2 das ofertas do N4): a fruta é parte do mesmo gesto da ração, e o J5 muda o mundo, não o cuidado. Não passa por `receber_acao_dono` | PROPOSTO |
| os braços | a mesma regra em todos os braços e nos dois protocolos, antes e depois de `T_m`: o mundo é o mesmo, e só o cérebro muda | PROPOSTO (PJ5-4) |

### A5.2 A interface com o A (o lado do mundo e do dono)

O A implementa em paralelo, com estes nomes (os dele, combinados com o C em 2026-10-14):
- **A chave:** `ConfigFrutaAoLado.ligada`, só no mundo físico. Desligada, a vida é a de hoje, byte a byte, com o gabarito num commit antes.
  Os braços do J5 a ligam na bancada (o D).
- **O gatilho:** o passo do dono em que o `DonoComLugar` deixa a ração no comedouro. As frutas que faltam entram no mesmo passo, logo
  depois da ração, fora do orçamento.
- **O registro:**
  - um evento novo no log, `deixar_fruta` (tipo, x, y), que o replay refaz;
  - a comida com a origem `dono_ao_lado`;
  - o depósito registrado (tick, tipo, x, y, a ração de referência);
  - o consumo com o tipo e a origem, para separar "comeu a fruta ao lado" de "achou na árvore".
- **A rng `fruta-ao-lado`:** uma permutação por vida (o tipo de cada célula), consumida na construção. Ela não toca a rng de ambiente, de
  política, do dono, do alvo nem do mundo.
- **O estilo do dono:** a regra exige o `DonoComLugar` no estilo `comedouro`, e falha alto com `perto` ou `longe`, em que a ração não fica no
  comedouro e "ao lado" não teria sentido.
- **A ração de referência:** o motor exige uma ração deixada no mesmo tick e grava o id dela. Uma fruta ao lado sem ração no tick falha
  alto.
- **A percepção:** nada novo. As frutas aparecem nos `vistos` como qualquer comida.
- **Os gates do A:**
  - o G2 (desligada = hoje) e o G1 com a regra;
  - a mecânica: no máximo uma de cada tipo ao lado, a reposição, as células, a permutação, fora do orçamento, sem contato.

### A5.3 A oportunidade do T1, agora lado a lado

A oportunidade do T1 da seção 4 é trocada por esta, e só no T1:
- **Uma oportunidade do T1** é uma decisão de **comer**, depois da última fruta na mão, em que **a x madura posta por esta regra e a ração
  madura estão as duas à vista** (as outras frutas ao lado, quando estão, também). A fome não entra na definição (PJ5-2).
- **O pet escolhe x** quando o alvo do comer é essa x. Comer a ração ou outra fruta conta como não escolher x.
- **O corte da reexperiência, `q`, as 3 primeiras e as 3 últimas** ficam como na seção 4.
- **O "antes"** usa a mesma definição, nas últimas 3 oportunidades antes de `T_m`.

**Por que só o comer:** a pergunta do T1 é "depois de saber que a x faz mal, o pet deixa de escolhê-la quando ela está ao lado da
ração?". Um pet ocioso não escolheu nada. Pela seção 4, o ocioso contava como "não escolheu x", e isso dilui a escolha.

### A5.4 As premissas

| premissa | regra nova | se falha |
|---|---|---|
| **G-APRENDEU** | em cada braço, `f_antes` com o limite inferior do IC95 **acima de 1/4** (PJ5-3): lado a lado com a ração e as outras duas frutas, o pet escolhe a x mais que o acaso entre os quatro alvos | o T1 daquele braço é inconclusivo por premissa |
| **G-OPORTUNIDADE** | igual (no máximo 25% das unidades sem oportunidade), com a oportunidade nova | igual |
| **G-EXPOSICAO** | igual (só o T2) | igual |
| **G-REVAL-POSSIVEL** | igual à do adendo 3, refeita com o `ganho_gosto` deste adendo | igual |

### A5.5 A calibração (dois números, nas sementes novas)

Nenhuma regra lê `f_antes`, `q`, `m` nem um contraste entre braços.

1. **O `ganho_gosto`:**
   - **a grade:** {S/2, S, 2S, 4S} (PROPOSTO). O adendo 4 mostrou que S e 2S quase não mudam a vida, e com a fruta ao lado o gosto passa
     a ter onde agir; o 4S cobre o caso de a grade ainda ser pequena;
   - **o que roda:** o P1, só na fase 1, nas 20 unidades;
   - **a medida:** nas decisões de comer com as frutas da regra e a ração à vista, a fração em que o pet come uma fruta (qualquer uma,
     não só a x), nos dias 4 a 6;
   - **a regra:** o **menor** ponto com a média em [0,25; 0,75] (PROPOSTO). Sem ponto na faixa, fica o mais perto, com o desvio
     declarado, e a calibração segue.
2. **O `g_plano`:** a regra da seção 5, sem mudança, com o `ganho_gosto` do passo 1.

Depois: a G-REVAL-POSSIVEL (A3.2) e o piloto da seção 6 (as margens, o ≤ 0,05, o N, o custo), nas mesmas unidades. Os números vão num
**adendo 6**, num commit antes da validação.

### A5.6 Os descritivos novos (sem gate)

- quantas frutas a regra pôs, por tipo e por dia, e quantas o pet comeu, pela origem `dono_ao_lado`;
- nas oportunidades do T1, a fração em que o **alvo padrão** do motor (a comida boa mais perto) seria a x. Assim se separa a escolha
  pela geometria da escolha pela preferência;
- os pesos `comida:racao` e `comida:<x>` por dia, como no adendo 4;
- a fração de fruta entre os consumos, toda a vida e a da regra;
- o T2 com a fruta ao lado: as buscas da x às árvores, sabendo que a x às vezes está no comedouro (R-16).

### A5.7 Os riscos novos

| # | risco | o que o adendo faz |
|---|---|---|
| R-15 | **A geometria decide, não a preferência:** o alvo padrão escolhe a comida mais perto | as frutas ficam do lado de fora, longe do ninho, e a geometria puxa para a ração; o tipo de cada célula é sorteado por unidade, então nenhum tipo fica sempre mais perto. O descritivo do alvo padrão (A5.6) mostra o quanto |
| R-16 | **O T2 perde buscas:** com a x às vezes no comedouro, o pet não precisa buscá-la nas árvores | a G-OPORTUNIDADE do T2 decide; a alternativa é parar a regra no T2 depois de `T_m` (PJ5-4) |
| R-17 | **O pet come fruta demais e passa fome** | a fruta não tira a ração; a faixa do `ganho_gosto` tem teto em 0,75; o `D_FE` e a privação já são descritivos |
| R-18 | **Quatro alvos lado a lado:** a escolha entre as frutas mistura o gosto e a saciedade por qualidade (comer muito a x baixa a resposta a ela) | é o paladar funcionando; o `q` compara o mesmo pet antes e depois, e a saciedade age nos dois lados. A leitura do receptor no consumo sai como descritivo (adendo 3, A3.6) |

### A5.8 Sementes

| uso | faixa | bases |
|---|---|---|
| calibração do `ganho_gosto` e do `g_plano`, e o piloto, com a fruta ao lado | **51101…51505** (nova; registrada na `FAIXAS_RESERVADAS` neste PR, sem colisão) | 51101, 51202, 51303, 51404, 51505 (K_u = 4) |
| validação | **46101…46505** (a da seção 8; nunca rodada) | as da seção 8 |

As faixas 45101…45505 (o desenho sem o paladar) e 49101…49505 (o paladar sem a fruta ao lado) não voltam: as unidades delas já foram
vistas.

### A5.9 Quando roda

Só com a regra do A na `main` (os gates dele passando), a faixa na `FAIXAS_RESERVADAS` e o sim do Matheus para a run.

### A5.10 Decisões do Matheus (este adendo)

**DECIDIDAS em 2026-10-18: PJ5-1 a PJ5-6, todas como recomendado** (a coluna "recomendação" é o que vale).

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| PJ5-1 | Quais frutas vão ao lado da ração | **DECIDIDO (Matheus, 2026-10-18): como recomendado.** **as três de uma vez, uma de cada, com reposição** (a proposta do A), na coluna do lado de fora, com o tipo de cada célula sorteado por unidade | uma por vez, em rodízio: a x só está lá em 1/3 do tempo, e o pet nunca vê duas frutas lado a lado. Só a x: o pet aprende o lugar, não o gosto. Posições fixas por tipo: um tipo fica sempre mais perto do ninho |
| PJ5-2 | A fome na oportunidade do T1 | **DECIDIDO (Matheus, 2026-10-18): como recomendado.** **sai:** a oportunidade é a decisão de comer com a x e a ração à vista | manter a fome ≤ S/2: o T1 olha de novo onde a nutrição domina, que é a razão de o adendo 4 ter voltado |
| PJ5-3 | O limiar da G-APRENDEU | **DECIDIDO (Matheus, 2026-10-18): como recomendado.** **1/4:** o acaso entre os quatro alvos (a ração e as três frutas), a mesma lógica do 1/3 de antes | 1/2: pede que a x ganhe de tudo junto, inclusive da ração com fome; a premissa pode falhar por nutrição, de novo |
| PJ5-4 | A regra no T2 depois de `T_m` | **DECIDIDO (Matheus, 2026-10-18): como recomendado.** **continua, igual nos dois protocolos:** um mundo só | parar no T2: a G-OPORTUNIDADE do T2 melhora, mas o mundo do T1 e o do T2 deixam de ser o mesmo depois da mudança |
| PJ5-5 | A grade do `ganho_gosto` | **DECIDIDO (Matheus, 2026-10-18): como recomendado.** **{S/2, S, 2S, 4S}**, pela fração de fruta nas decisões lado a lado, em [0,25; 0,75] | a grade do adendo 3: o adendo 4 mostrou que ela quase não muda a vida |
| PJ5-6 | As sementes | **DECIDIDO (Matheus, 2026-10-18): como recomendado.** **51101…51505 nova para a calibração e o piloto; a validação continua em 46101…46505** | reusar 49101…49505: as unidades já foram vistas com o paladar sem a fruta ao lado |

## Adendo 6 — o `ganho_gosto`, o `g_plano`, a G-REVAL-POSSIVEL, as margens e o N com a fruta ao lado (2026-10-18, números congelados)

O adendo 5 (A5.5) pede este adendo. A calibração e o piloto rodaram uma vez, nas bases 51101…51505 (K_u = 4, 20 unidades), com a config
`experiments/configs/v2_pet_que_pensa/calibracao_ao_lado.json` sem mudança e o código da `main` `0896219`. Os números vêm de
`artifacts_v2_pet_que_pensa/calibracao_ao_lado/` (o commit `4b42915`), e o relatório está em
`docs/RESULTADO_V2_CALIBRACAO_PET_QUE_PENSA_AO_LADO.md`. Nada foi escolhido olhando o primário.

- **A6.1, o `ganho_gosto` = S/2 (512), fechou.** A média da fração lado a lado nos dias 4 a 6 foi **0,654** (S/2), 0,679 (S), 0,685 (2S) e
  0,634 (4S). Todos caem em [0,25; 0,75], e fica o menor.
- **A6.2, o `g_plano` = S (1024), fechou.** A média da sonda foi 0,067 (S/4), 0,098 (S/2) e **0,152** (S).
- **A6.3, a G-REVAL-POSSIVEL passa:** 0 de 20 unidades falham. A menor folga é 45.
- **A6.4, as margens:**
  - **`Δ_T1` = 0,217:** a média de `f_antes` do P1-plan no T1 é 0,433, nas 20 unidades;
  - **`Δ_T2` = 0,286:** 7 unidades com busca antes.
  - As duas passam de 0,05.
- **A6.5, o N: K_u = 10 (N = 50), sem chegar a 0,8.** O poder do G-T1 vai de 0,276 (K_u = 4) a **0,687** (K_u = 10). O do G-T2 não sai,
  porque nenhuma unidade teve busca depois da mudança. Pela seção 6, a validação roda com K_u = 10 e o poder declarado.
  - **Os secundários** a K_u = 10 (a α 0,0125):
    - o G-T1-CONG, 0,83;
    - o G-T1-DESF, 0,56;
    - os do T2 não saem.
- **A6.6, as premissas no piloto (só relato):**
  - **G-APRENDEU passa nos quatro braços** (limiar 1/4): `f_antes` 0,55 [0,43; 0,67] no P1 e 0,43 [0,33; 0,52] nos três com o
    planejador;
  - **G-OPORTUNIDADE:** passa no T1 (de 3 a 5 das 20 unidades sem oportunidade) e falha no T2 (20 de 20);
  - **G-EXPOSICAO falha:** de 8 a 11 das 20 unidades sem exposição.
- **A6.7, o custo:** 0,86 s de CPU por vida de 10 dias (P1 0,74; com o planejador, cerca de 0,90). N = 50 daria 400 vidas, cerca de 6 min
  de CPU.
- **A6.8, a validação (46101…46505) não rodou.** Ela pede o sim do Matheus. Pelo piloto, o T2 dela sai inconclusivo por premissa (o R-16:
  com a x no comedouro, o pet não a busca nas árvores).

## A validação com a fruta ao lado (2026-10-18): inconclusiva por premissa

A validação rodou uma vez, nas bases 46101…46505 (K_u = 10, 50 unidades), com os números do adendo 6. O relatório está em
`docs/RESULTADO_V2_VALIDACAO_PET_QUE_PENSA.md`, e os artefatos em `artifacts_v2_pet_que_pensa/validacao_ao_lado/`. **Decisão do Matheus
(2026-10-18), pela recomendação:** o J5 fica registrado como **inconclusivo por premissa**, com o descritivo.

- **O G-T1 é inconclusivo por premissa:** a G-OPORTUNIDADE do T1 falha por pouco nos quatro braços. De 14 a 16 das 50 unidades (28% a 32%)
  ficam sem oportunidade depois da mudança, contra o limite de 25%.
- **O G-T2 é inconclusivo por premissa:** nenhuma busca da x nas árvores depois da mudança, em nenhuma unidade (o R-16), e a G-EXPOSICAO
  também falha.
- **O descritivo do T1** (não é teste):
  - antes da mudança, o pet escolhe a favorita em 53% a 54% das oportunidades, acima do acaso entre os quatro alvos (25%) e do que a
    geometria daria (cerca de 33%);
  - depois que ela passa a fazer mal, a escolha quase não cai (`q` de −0,06 a 0,03), com ou sem o planejador.
- **A faixa 46101…46505** foi usada por esta validação e não volta.

## Adendo 7 — os dois testes consertados numa run só (2026-10-18, PROPOSTO, antes de qualquer run)

Status: **PROPOSTO**, registrado antes de qualquer vida com ele. Depende das decisões PJ7-1 a PJ7-6 abaixo, do Matheus. Duas coisas já
estão **DECIDIDAS pelo Matheus (2026-10-18):** consertar os dois testes numa run só, e, no T2, a fruta ao lado **para** depois de `T_m` (o
R-16 e a alternativa da PJ5-4).

**O que não muda:**
- a pergunta (DS-1), os quatro braços e o que os separa (o planejador e o congelamento);
- a fase 1 inteira: `D_a` = 7, o paladar, a fruta ao lado da ração (adendo 5, A5.1), `n_mao` = 2 e `T_m`;
- o `q` e o `m`, as 3 primeiras e as 3 últimas, o corte da reexperiência (o primeiro consumo da x no mapa depois de `T_m`);
- os contrastes, as categorias, o Holm, o bootstrap e os gates de mecanismo;
- a G-OPORTUNIDADE (no máximo 25% das unidades sem oportunidade), a G-EXPOSICAO e a G-REVAL-POSSIVEL.

### A7.1 Por que as unidades ficaram sem oportunidade (o mecanismo, pelo código)

Pelo `metrics.mudanca_de_escolha`, o "depois" vai da última fruta na mão até o primeiro consumo da x no mapa, venha ele de onde vier. Pela
`metrics.oportunidade_lado_a_lado`, só conta a decisão de comer com a x da regra **e a ração** à vista. Então uma unidade fica sem
oportunidade de dois jeitos:
1. **o corte chega antes:** o pet come a x numa decisão que não conta. A ração já foi comida e só sobram as frutas ao lado, ou a x vem de
   uma árvore, ou do "achou e comeu" do explorar;
2. **a janela acaba:** os 3 dias passam sem nenhuma decisão lado a lado.

O relatório da validação não separa os dois casos, e este adendo não os separa olhando a validação: o piloto novo mede isso (A7.6).

### A7.2 O T1: a oportunidade aceita qualquer alternativa ao lado, e a janela cresce

- **A oportunidade** (troca a da A5.3): uma decisão de **comer**, depois da última fruta na mão, em que a x madura posta pela regra está à
  vista **junto com pelo menos uma alternativa ao lado: a ração madura ou outra fruta madura posta pela regra** (PJ7-1). A fome continua
  fora.
- **Escolher x:** o alvo do comer é essa x. Comer a ração ou outra fruta conta como não escolher x.
- **Por que resolve o caso 1:** o dono repõe as três frutas a cada ração. Depois que o pet come a ração, as outras duas frutas costumam
  continuar ali, e a decisão passa a contar antes do consumo da x.
- **A janela depois da mudança:** **5 dias** (era 3; PJ7-2). A vida passa a ter 12 dias, e os dois protocolos ficam com o mesmo tamanho.
- **A G-APRENDEU:** o limiar passa a ser **o acaso médio das oportunidades** (PJ7-3). Em cada oportunidade, o acaso é 1/k, com k os alvos
  à vista (a ração e as frutas da regra), e o limiar é a média de 1/k sobre as oportunidades do "antes" do braço. Com os quatro alvos à
  vista é 1/4, como antes; sem a ração, 1/3.

### A7.3 O T2: a fruta ao lado para em `T_m`, e a busca perde a fome

- **A regra da fruta ao lado no T2** (DECIDIDO): funciona como no adendo 5 até `T_m`. **No passo do dono de `T_m` e depois, o dono não
  põe mais fruta ao lado.** A ração continua igual, e as frutas ao lado que já estavam no chão seguem o tempo delas (amadurecer,
  apodrecer, sumir). No T1, a regra continua depois de `T_m`, como antes: é ela que dá a escolha lado a lado.
- **Os dois protocolos** são iguais até `T_m`; depois, diferem pela mudança de cada um e por esta parada.
- **A busca** (troca a da seção 4, só no T2): uma decisão **sem a x à vista** em que o alvo escolhido é uma árvore do tipo x de antes (as
  velhas) ou do de depois (as novas). **A fome sai** (PJ7-4), pela mesma razão da PJ5-2: com o paladar, o pet busca a x pelo gosto, e a
  fome ≤ S/2 olha onde a ração domina.
- **A exposição e o corte** ficam iguais.
- **A janela:** 5 dias, como no T1.

### A7.4 O que se recalibra

**Nada.** A fase 1 é a mesma do adendo 5: o `ganho_gosto` = S/2 e o `g_plano` = S do adendo 6 continuam (PJ7-5). As duas regras de
calibração leem só a fase 1, e ela não mudou.

O que é refeito, nas sementes novas, é o **piloto** da seção 6:
- a G-REVAL-POSSIVEL;
- as margens `Δ_T1` e `Δ_T2`, pela regra da seção 6, com as definições novas;
- o N pelo poder simulado nos dois primários (K_u de 4 a 10);
- o custo e as premissas, como relato.

Os números vão num **adendo 8**, num commit antes da validação. Se uma margem ficar ≤ 0,05, a validação não roda e o plano volta ao
Matheus (seção 6).

### A7.5 A interface com o código

O D (a bancada do J5) e, se for preciso, o A (o dono da fruta ao lado):
- **a parada no T2:** o `DonoFrutaAoLado` ganha um tick de parada (por exemplo `ate_tick`), ou a bancada deixa de passar a regra a partir
  de `T_m` no protocolo T2. Desligada (sem tick de parada), a vida é a de hoje, com o gabarito num commit antes;
- **a oportunidade nova do T1:** uma função nova em `digilab/metrics.py` (a de hoje fica, para o adendo 5 reproduzir), com o teste de
  resposta conhecida;
- **a busca sem a fome:** a `busca_transicao` com o limite da fome como argumento (sem limite = a regra nova);
- **a janela de 5 dias** e a vida de 12 dias, na config;
- **o limiar da G-APRENDEU** pelo acaso médio;
- **o motivo de cada unidade sem oportunidade** (A7.6).

### A7.6 Os descritivos novos (sem gate)

- **Por que cada unidade ficou sem oportunidade:** o corte chegou antes (com a origem do consumo da x: a regra, uma árvore, o "achou e
  comeu") ou a janela acabou;
- **a latência** até a primeira oportunidade e até o corte, por braço e teste;
- **no T2,** quantas vezes o pet foi às árvores velhas e às novas, por dia, depois de `T_m`, e quantas frutas ao lado ainda havia no chão;
- **o acaso médio** de cada braço (o limiar da G-APRENDEU).

### A7.7 Os riscos novos

| # | risco | o que o adendo faz |
|---|---|---|
| R-19 | **O corte continua chegando antes** (a x de uma árvore, o "achou e comeu") | a janela maior não ajuda nesse caso, e o descritivo da A7.6 diz quanto pesa. Se a G-OPORTUNIDADE falhar de novo por ele, a próxima opção é tirar a x das árvores no T1 depois de `T_m` (fora deste adendo) |
| R-20 | **No T2, sem a fruta ao lado, o pet volta a só comer a ração** e não busca árvore nenhuma, como nos adendos 1 e 4 (20 de 20 sem busca) | a busca perde a fome (PJ7-4). Mesmo assim, a premissa pode falhar: é o mesmo mundo dos adendos 1 e 4 depois de `T_m`, com um pet que gosta da x |
| R-21 | **A vida maior muda a fase 1** | não muda: a fase 1 tem os mesmos `D_a` = 7 dias, e só a janela cresce |
| R-22 | **O limiar pelo acaso médio é mais fácil** quando a ração some | o limiar acompanha os alvos de cada oportunidade; com os quatro à vista ele é o 1/4 de antes |

### A7.8 Sementes

| uso | faixa | bases |
|---|---|---|
| o piloto do adendo 7 (as margens, o N, as premissas) | **52101…52505** (nova; registrada na `FAIXAS_RESERVADAS` neste PR, sem colisão) | 52101, 52202, 52303, 52404, 52505 (K_u = 4) |
| a validação do adendo 7 | **53101…53505** (nova; registrada neste PR) | 53101, 53202, 53303, 53404, 53505 (K_u pelo adendo 8) |

**Nenhuma faixa velha volta:** nem a 45101 e a 46101 (o desenho sem o paladar, e a validação já rodada), nem a 49101 e a 51101 (o paladar e a
fruta ao lado).

### A7.9 Quando roda

Só com o código da A7.5 na `main` (com os gates), as faixas na `FAIXAS_RESERVADAS` e o sim do Matheus para o piloto, e depois outro sim
para a validação.

### A7.10 Decisões do Matheus (este adendo)

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| PJ7-1 | A alternativa na oportunidade do T1 | **qualquer alternativa ao lado:** a ração ou outra fruta da regra | só a ração (A5.3): o pet come a x quando a ração já acabou, o corte chega sem oportunidade, e a G-OPORTUNIDADE falha de novo |
| PJ7-2 | A janela depois da mudança | **5 dias,** nos dois protocolos (a vida de 12 dias) | 3 (a de hoje): no caso "a janela acaba", nada muda. 7 ou mais: mais custo, e mais tempo para o corte por uma árvore |
| PJ7-3 | O limiar da G-APRENDEU | **o acaso médio das oportunidades do braço** (1/k por oportunidade) | 1/4 fixo: com a ração fora, o acaso é 1/3, e 1/4 deixa passar um pet que escolhe a x ao acaso |
| PJ7-4 | A fome na busca do T2 | **sai** | manter a fome ≤ S/2: a busca olha onde a ração domina, e o T2 tende a ficar sem busca de novo |
| PJ7-5 | Recalibrar | **não:** a fase 1 é a mesma, e ficam o `ganho_gosto` = S/2 e o `g_plano` = S do adendo 6. Só o piloto é refeito | recalibrar: mais uma rodada que lê a mesma fase 1 e pode mudar o ponto sem razão |
| PJ7-6 | As sementes | **52101…52505 para o piloto e 53101…53505 para a validação,** as duas novas | reusar uma faixa velha: as unidades já foram vistas, e a 46101 já foi a validação |
