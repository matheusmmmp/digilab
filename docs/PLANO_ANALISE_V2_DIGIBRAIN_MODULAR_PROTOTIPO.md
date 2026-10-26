# Plano de análise — o protótipo do DigiBrain modular, etapa 1

Data: 2026-10-25. Status: **revisto pelo Matheus em 2026-10-25** (relato do Gerente): as PPM-1 a PPM-9 e os AF DECIDIDOS (seção 13),
com quatro correções pedidas e feitas nesta versão (o poder com o Holm, a regra operacional do Holm, a ordem dos gates, o G-MVP como
condição necessária). **Sem vidas e sem merge até o Matheus revisar esta versão corrigida.** Os números continuam PROPOSTOS e SEM FONTE.
Tarefa: `docs/TAREFA_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md` (seções 3, 4 e 10). Especificação: `docs/ESPEC_DIGIBRAIN_MODULAR.md` (a direção
aprovada, as PE "antes" decididas, a PE-14 revista, as D-0 a D-2). Critérios do baseline e do fallback:
`docs/TAREFA_V2_CEREBRO_A_BASELINE.md` (D1 a D6; os AF-1 a AF-6 DECIDIDOS em 2026-10-25, seção 13).

**As regras deste documento:**
- **Todo número novo é PROPOSTO e SEM FONTE,** mesmo onde a marca não se repete a cada linha. Os limiares estão na seção 13, com a
  recomendação, o custo de errar e a decisão do Matheus.
- **Nenhuma alegação de novidade.** As referências são as da espec (seção 14 dela), todas verificadas, lidas em metadados e resumo.
- **O A não muda.** Ele entra só como baseline (`docs/TAREFA_V2_CEREBRO_A_BASELINE.md`, seção 1), uma vez, na avaliação única.
- **Nenhuma vida roda nesta tarefa.** Os números de contexto abaixo vêm de documentos; nenhum entra como evidência.

**Os números de contexto** (só para desenhar):
- **O diagnóstico do A no MVP** (registro "2026-10-24 — MVP-ETAPA2"): o pet v12 comeu 1 ou 2 vezes por vida, em 20 vidas de 2 dias,
  com o dono pondo a ração perto a cada 2 h; numa vida com fome, a ração a 2 células não foi comida em 10 h. **É diagnóstico, não
  resultado:** rodou no TS, com um dono feito para o diagnóstico, sem artefato de pesquisa. Serve de referência de ordem de grandeza, nunca
  de gate do A nem de margem.
- **A leitura do código** (espec, seção 0): com a fome abaixo de 0,25, o instinto do A só oferece `chamar_atencao`. O T-CADEIA-0
  confere isso sem mudar o A.

## 1. A pergunta, as hipóteses e o que a etapa 1 implementa

**A pergunta** (tarefa, seção 1): o cérebro modular mínimo faz o que o MVP pede (perceber a comida, ir, comer e aprender com a
consequência) por meio dos próprios módulos, e cada módulo pesa como a especificação diz?

**O que a etapa 1 implementa** (a DM-3 e a espec, seções 4 e 11):
- **os módulos,** no pacote `digilab/digibrain/`, atrás da `ConfigDigibrain`:
  - o M-ADAPT, completo, inclusive o `receber_acao_dono` (hoje `NotImplementedError`, etapa 0);
  - o M-SENS, o M-AFETO, o M-ESTADO, o M-IMPULSO, o M-ARB e o M-PLAST (P1 e P2);
  - o **M-MEM mínimo:** os episódios de alimentação e de visita, a recuperação pela fome sem comida à vista, o termo no "explorar o
    lugar" (espec, seções 4.6 e 9);
  - os ganchos vazios M-PERS, M-GEN e M-EXPR (espec, seção 4.9);
- **o lugar lembrado pelo `Alvo.ponto`** que o motor Python já aceita, só em EXPLORAR (a PE-14 revista; espec, seções 4.1 e 11);
- **as subchaves que os braços pedem** (seção 2): a de hoje (`modula_g_apr`, `p2`, `m_mem`, `persistencia`) e duas que faltam na
  `ConfigDigibrain` da etapa 0, **PROPOSTAS para a etapa 1a**: uma subchave `p1` (o braço "inato só" precisa do P1 desligado) e o modo do
  `g_apr` (constante em g₀, modulado pela excitação, embaralhado, constante na média).

**O que só se avalia** (não se implementa nada para isso): a ablação por módulo, a cadeia do MVP, a comparação com o A e o custo.

**Fora da etapa 1:** a memória autobiográfica consolidada (tarefa própria; DM-3), a fala e o T-MOTIVO-2 (o M-EXPR é gancho vazio; o teste
entra com o verificador da fala), o genoma, dois pets, as frutas, a forma II (PE-8), o acumulador da PE-5 e a web, salvo a etapa 1b
(seção 10).

**As hipóteses, uma por mecanismo,** cada uma ligada a um teste da seção 10 da espec ou a uma ablação deste plano. É o que a espec prevê,
não um resultado:

| # | mecanismo | a hipótese | o teste de mecanismo (espec, seção 10) | a ablação ou a leitura (este plano) |
|---|---|---|---|---|
| H-SENS | M-SENS | a proximidade e a novidade saem da Observação, sem tocar o corpo | T-SENS-1 a 3 | só mecanismo |
| H-AFETO | M-AFETO | a urgência sobe com a falta; o r é o `sinal_corpo` do A | T-AFETO-1 e 2 | só mecanismo |
| H-IMPULSO | M-IMPULSO | todas as unidades concorrem; com fome e comida à vista, comer vence chamar | T-IMPULSO-1; T-CADEIA-1 (o oráculo, D3) | G-MVP (seção 5.2); o contraste com o A é descritivo (seção 7) |
| H-ARB | M-ARB | o sorteio inteiro é o do A; o reflexo do sono fica fora | T-ARB-1 e 2 | só mecanismo |
| H-P1 | M-PLAST, P1 | depois das primeiras refeições, o pet vai à ração com menos fome do que o inato pedia (espec, seção 2.5, passo 2) | T-PLAST-1; T-IMPULSO-2; T-CADEIA-2 | **G-ABLA-P1** (M1 × M0) |
| H-P2 | M-PLAST, P2 | o comportamento seguido de melhora do corpo se repete no mesmo contexto (passo 5) | T-PLAST-2 e 3 | **G-ABLA-P2** (M2 × M1) |
| H-MEM | M-MEM | com fome e sem comida à vista, o pet vai ao lugar onde o dono costuma pôr a ração; a visita vazia apaga o lugar (passos 3 e 4) | T-MEM-1 a 4; T-PONTO-1 a 3 | **G-ABLA-MEM** (M3 × M2) |
| H-ESTADO | M-ESTADO | a intenção persiste até a meta e acaba quando o alvo some | T-ESTADO-1 e 2 | **G-ABLA-PERS** (M3 × M3-sp) |
| H-MOD | M-AFETO → M-PLAST | a excitação no `g_apr` separa "modular" de "aprender mais depressa em média". **HIPÓTESE EXPERIMENTAL, não conclusão da literatura** (D-1) | T-AFETO-3; T-PLAST-3 | **G-MOD** (M4 × M4-con e M4 × M4-emb), secundário |
| H-MOTIVO | o registro | a sonda "quem decidiu" mede cada módulo com o mesmo `u` | T-MOTIVO-1 | a premissa G-PESA (seção 6) e a leitura D-2 (seção 8) |

## 2. Os braços

**O mesmo pet, o mesmo mundo e as mesmas sementes entre os braços.** O cérebro só consome a rng de política que o motor passa ao `agir`
(espec, seção 1). O dono, o lugar da ração e o mundo têm as rngs deles, e trocar o cérebro não muda o mundo (CLAUDE.md).

A escada é cumulativa, como a da espec (seção 13):

| braço | `ConfigDigibrain` | papel |
|---|---|---|
| **M0** | ligada; `p1`, `p2`, `m_mem` desligados; `persistencia` ligada; `g_apr` = g₀ | o inato sozinho (d̂ = 0, H = 0, memória vazia a vida inteira) |
| **M1** | M0 + `p1` | o inato com o modelo do desfecho |
| **M2** | M1 + `p2` | com o hábito |
| **M3** | M2 + `m_mem` | **o braço principal:** a etapa 1 inteira, com a modulação desligada (PE-4, D-1) |
| **M3-sp** | M3 − `persistencia` | a ablação da persistência (a subchave que a espec manda a avaliação desligar, seção 11) |
| **M4** | M3 + `modula_g_apr` (a excitação modula o `g_apr`) | a modulação, secundária |
| **M4-emb** | M4 com a excitação de outra vida: a série E, decisão a decisão, da vida M4 da unidade seguinte da mesma base, na mesma célula (a última unidade usa a primeira) | o controle embaralhado do V3 (`docs/futuro/digibrain_v3_e0.md`, seção 4.3) |
| **M4-con** | M3 com o `g_apr` fixo na média do `g_apr` das vidas M4 do piloto (congelada no adendo 2) | o controle constante do V3 |
| **A11** | o A v11 (`P1-c-tapa`, o ponto do corpo do adendo 4), o alvo padrão do motor, sem as chaves do mundo (a MV-2) | **o baseline** (a função "baseline" da seção 1 de `TAREFA_V2_CEREBRO_A_BASELINE`). Só na avaliação única |

- **A série E do M4-emb tem o mesmo comprimento:** as decisões vêm a cada 15 ticks, com ou sem sono, e as vidas têm os mesmos dias.
- **O A11 não entra na calibração nem no piloto.** Nenhum número deste plano lê o A antes da avaliação; ele não tem gate (seção 7).
- **A L1 como braço de comparação do P2** (a PE-2 deixava aberto) **não entra:** ela aprende dentro da cascata, e a pergunta da etapa 1 é
  se os módulos pesam, não qual regra de hábito é melhor.

## 3. Os cenários

O cenário é o do MVP (`docs/TAREFA_V2_MVP_MUNDO_PRODUTO.md`), na bancada Python:
- **o corpo químico do v11** (`com_corpo(MotorMundo)`, a `ConfigCorpo` do braço `P1-c-tapa`, o ponto do adendo 4), igual em todos os
  braços, como no gabarito do MVP (`experiments/exportar_gabarito_mvp_produto.py`);
- **o mundo do produto:** o `CONFIG_MUNDO_MVP`, o layout padrão sem árvores, só a ração do dono. **Sem frutas** (a MV-3);
- **o contrato da P4 desligado,** como no jogo (`web/app/motor/motor.ts:674`, "o contrato da P4 fica desligado no jogo"). A pergunta é a
  do produto, e o G-PAR compara o laço do v12. O contrato ligado fica para um adendo, se o Matheus quiser (PPM-3);
- **o pet sozinho;**
- **os donos:** os quatro da v1 (atencioso, relapso, aleatório e incoerente), só com o cuidado (o filtro `sem_ensino`, sem elogiar nem
  repreender; o v12 recusa os dois). O carinho e o tapa chegam ao pet como eventos diretos (`receber_acao_dono`; a MV-7);
- **o lugar da ração** (o `DonoComLugar`): comedouro, perto e longe, um fator fixo por vida, como no plano do mundo
  (`docs/PLANO_ANALISE_V2_MUNDO_FISICO.md`, seção 2);
- **14 dias,** 16 interações do dono por dia (224), morte desligada: a convenção do mundo e da competição.

**A cadeia comida → corpo** é a que o E2E-COMIDA mostra no jogo: o dono põe a ração, o pet a percebe, anda, come, e o receptor da fome cai.
Aqui ela se mede vida a vida (seção 5.2), nas vidas comuns, e não num save preparado (a ressalva do Matheus no #404).

**Um achado que toca o cenário:** `tests/test_gabarito_mvp_produto_web.py` (`test_o_layout_do_mvp_nao_vaza_para_a_pesquisa`) confere que
só o `config.py`, o exportador do produto e esse teste citam o `CONFIG_MUNDO_MVP`, porque a MV-10 limitou o layout ao produto. Rodar a
avaliação no layout do MVP pede que o orquestrador desta avaliação entre na lista permitida do teste. Os cenários de pesquisa de antes não
mudam. É a PPM-3.

**Unidade, pareamento e células:**
- **a unidade:** a semente de `unidades_derivadas(bases, K, prefixo="digibrain_prototipo")`. O prefixo é PROPOSTO e entra no
  `PREFIXOS_UNIDADES` com o código do orquestrador, não nesta tarefa;
- **a célula:** dono × lugar, 4 × 3 = 12;
- **as vidas por unidade:** 12 células × 8 braços do modular = 96 no piloto; com o A11, 108 na avaliação;
- **o pareamento:** por unidade e célula. A rng `dono-lugar` não depende do braço, e os desvios do lugar são os mesmos;
- **a estatística por unidade:** a média das 12 células da diferença entre braços (como no plano do mundo). As exceções, restritas a uma
  parte das células, estão escritas em cada medida.

## 4. As medidas

**Já existem em `digilab/metrics.py`** (nenhuma muda):
- `deficit_fome_energia` (o `D_FE`, dias 8 a 14, `JANELA_8_14`);
- `privacao_nas_decisoes` (o limiar 0,15 do plano do corpo);
- `exaustao_nas_decisoes`;
- `taxa_agregada`, para somar os contadores por unidade (a conta é genérica: n e quantos);
- `contraste_pareado`, `holm`, `bootstrap_ic`, `ic_percentil`, `dentro_da_margem` e `tamanho_amostra`.

**Faltam, e entram em `digilab/metrics.py` com teste, no código da avaliação, antes da calibração** (PROPOSTAS; nenhuma implementada
aqui). Todas leem o registro da decisão (espec, seção 7), que o orquestrador coleta durante a vida (o registro é derivado e não vai ao
log), e as listas do motor (os `lugares` do `DonoComLugar`, os consumos do mundo, o corpo antes e depois de cada decisão):

| medida | a definição PROPOSTA |
|---|---|
| `cadeia_comida_corpo` | para cada ração posta pelo dono no tick t₀ com a fome do pet (o estado, 0–1) abaixo de 0,5 (a ração **elegível**): **fechada** se o pet come essa ração até t₀ + W, com W = 8 decisões (120 ticks), e o receptor da fome cai na decisão do consumo (o `corpo_depois` contra o `corpo_antes`, como no gabarito do MVP). Sai, por vida: as elegíveis, as fechadas, a taxa de fechamento (None sem elegível), a latência de cada fechada e as refeições por dia (todo consumo de ração, elegível ou não) |
| `influencia_por_modulo` | a fração das decisões com `<modulo>_decidiu` verdadeiro, para incentivo, hábito, memória, persistência e afeto, na vida e por dia. Generaliza o `competicao_nas_decisoes` para as seis sondas |
| `falta_ao_comer` | a média da falta da fome (a interocepção do M-SENS, na escala 0–1) nas decisões que escolheram comer a ração, dias 8 a 14. None sem decisão de comer |
| `repeticao_apos_alivio` | o índice de "ganhou, fica": em cada contexto (o drive de maior urgência, comida à vista sim ou não, noite sim ou não), P(a mesma ação na próxima decisão naquele contexto \| o r da última consequência dela ali > 0) − P(\| r ≤ 0). Dias 8 a 14; None sem os dois lados |
| `intencoes_com_meta` | a fração das intenções de comer (o `I*` com b = comer) que acabam com a meta (comeu), dias 8 a 14 |
| `pesos_no_teto` | a fração dos H em ±H_max no fim da vida (o G6 da V2, espec, seção 2.4; a PE-10) |
| `centro_temporal` | o dia médio de uma série diária de frações, ponderado pela fração (None com a série toda em 0). Serve à leitura D-2 |

- **As medidas acima entraram no `digilab/metrics.py` na etapa 1a (#414, worker D), antes de qualquer vida,** com leituras PROPOSTAS
  onde o texto deste plano deixava margem. **Elas estão escritas na seção da etapa 1a de `docs/registro/2026-10.md` e valem como parte
  deste plano:** não mudam depois de olhar as vidas. As três que mudam o que se mede: a **intenção** só existe nas unidades com alvo de
  identidade fixa (a comida `id`, a bola, o lugar lembrado), e o cheiro e o vagar não geram compromisso nem frustração (afeta
  `intencoes_com_meta` e a persistência do G-ABLA); a **sonda sem u** (decisão com um candidato só) fica com o candidato de maior peso
  (afeta `influencia_por_modulo`); "o **receptor da fome cai**" na E2E-COMIDA é lido como a falta do M-SENS cair. Também: o contexto z
  tem 23 características (`CARACTERISTICAS_DIGIBRAIN`), não ~20, e duas conjunções com a urgência ficam no M-IMPULSO, não no M-SENS.
  Nenhuma dessas leituras foi ajustada olhando para uma vida das faixas: nenhuma rodou.
- **O índice de "ganhou, fica" é medida nossa, SEM FONTE.** Ele mede o que o P2 faz por construção (reforça a ação escolhida no contexto
  em que o corpo melhorou), e não uma teoria do hábito.
- **O custo** (seção 5.4) não é medida do `metrics.py`: é o cronômetro do navegador e a contagem do `estado_interno`, na etapa 1b.

## 5. Os gates

### 5.1 Os de engenharia (pré-condição, não evidência; DM-2)

Nenhum deles diz nada sobre a aprendizagem nem sobre a qualidade do comportamento (espec, seção 11). **Cada um bloqueia uma coisa só,**
e a tabela diz qual (a correção 3 da revisão):

| gate | o que confere | o que ele bloqueia | o que ele **não** bloqueia |
|---|---|---|---|
| **G1** | o replay bit a bit | **a calibração Python** (e toda vida depois) | — |
| **G2** | com a chave desligada, as vidas de hoje byte a byte: as 196 de `tests/gabaritos/digibrain_vidas_de_hoje.json` e os gabaritos do MVP | **a calibração Python** | — |
| **G-INT, G-RECEPTOR, G-SEM-DIRECAO** | sem float, sem `/` e sem `math` no pacote; o cérebro só lê a Observação; sem a direção do cheiro fora do motor | **a calibração Python** | — |
| **T-PONTO-1 a 3** | o `ponto` só em EXPLORAR e só com o M-MEM; o `raise` fora do mapa; o G2 das 196 vidas | **a calibração Python** | — |
| **G-MECANISMO** (seção 5.2) | os testes de mecanismo | **a calibração Python** | — |
| **T-PONTO-4** | o gabarito das vidas v12 em TS, depois o gancho do `ponto` no laço do TS (a validação do `Mundo` TS já existia; #413) | a mudança no espelho TS (etapa 1b) | **as vidas da pesquisa Python** |
| **G-PAR** | o espelho TS refaz os gabaritos do Python decisão a decisão | a integração TS (etapa 1b) e o gate de compatibilidade do produto (a MV-2, i) | **as vidas da pesquisa Python** |
| **G-CUSTO** (seção 5.4) | o orçamento no navegador | o gate de prontidão do produto (seção 5.6) | **as vidas da pesquisa Python** |

**Em uma frase:** a calibração, o piloto e a avaliação Python esperam só os cinco primeiros; o TS anda ao lado e só segura a integração
no jogo.

### 5.2 Os de avaliação

Todos os limiares são PROPOSTOS e SEM FONTE; o custo de errar de cada um está na seção 13.

| gate | o que confere | a regra | papel | o critério do baseline |
|---|---|---|---|---|
| **G-MECANISMO** | os testes de mecanismo da seção 10 da espec que a etapa 1 cobre: T-SENS-1 a 3, T-AFETO-1 a 3, T-ESTADO-1 e 2, T-IMPULSO-1 e 2, T-MEM-1 a 4, T-ARB-1 e 2, T-PLAST-1 a 3, T-ADAPT-1 e 2, T-MOTIVO-1, T-CADEIA-1 e 2 | todos passam (binário) | **pré-condição da calibração.** Com um falhando, nenhuma vida roda | D1; o T-CADEIA-1 é o D3 (o oráculo) |
| **G-MVP** | a cadeia comida → corpo no M3 | a fração das vidas do M3 com a taxa de fechamento ≥ 0,5: o limite inferior do IC95 ≥ 0,8. As vidas sem ração elegível ficam fora e são contadas | **o primário da pesquisa;** condição **necessária, não suficiente,** do gate de prontidão do produto (a MV-2, ii; seção 5.6) | D4 |
| **G-ABLA-P1** | `falta_ao_comer`(M0) − `falta_ao_comer`(M1) | o Holm da família G-ABLA (seção 5.2.1) | a família G-ABLA | D2 |
| **G-ABLA-P2** | `repeticao_apos_alivio`(M2) − idem(M1) | o Holm da família G-ABLA (seção 5.2.1) | a família G-ABLA | D2 |
| **G-ABLA-MEM** | taxa de fechamento(M3) − idem(M2), **só nas células do comedouro** (4 por unidade) | o Holm da família G-ABLA (seção 5.2.1) | a família G-ABLA | D2 |
| **G-ABLA-PERS** | `intencoes_com_meta`(M3) − idem(M3-sp) | o Holm da família G-ABLA (seção 5.2.1) | a família G-ABLA | D2 |
| **G-MOD-CON** | `D_FE`(M4-con) − `D_FE`(M4) | o Holm da família G-MOD (seção 5.2.1) | secundário: a hipótese experimental da D-1 | — |
| **G-MOD-EMB** | `D_FE`(M4-emb) − `D_FE`(M4) | o Holm da família G-MOD (seção 5.2.1) | secundário | — |
| **G-CUSTO** | o orçamento da seção 12 da espec | os quatro itens dentro (seção 5.4) | gate de produto, na etapa 1b; não bloqueia as vidas Python | D5 |

**Por que a G-ABLA-MEM só no comedouro:** a espec prevê o efeito no lugar "onde o dono costuma pôr a ração" (o T-MEM-2). Perto e longe, o
lugar sorteado muda a cada ração, e o M-MEM pode até atrapalhar (a visita vazia). Os dois ficam como leitura descritiva da mesma medida.
A restrição está escrita antes de qualquer vida.

#### 5.2.1 A regra operacional do Holm (uma só, escrita antes de qualquer vida)

A correção 2 da revisão. **Os gates das duas famílias decidem pelo p do bootstrap, e não pelo IC95:**
1. **o p de cada contraste:** o `p_unilateral` do `contraste_pareado` (`digilab/metrics.py`), a fração das médias reamostradas ≤ 0, com
   o contraste orientado para a direção prevista (positivo = a direção da espec). O bootstrap é o da convenção: sobre as unidades,
   agrupado por base, 10 000 reamostragens, semente 4242;
2. **o Holm:** o `holm` do `digilab/metrics.py`, com α = 0,05 sobre a família inteira. Os p em ordem crescente; o do posto i (i = 1…m)
   comparado a 0,05/(m − i + 1); rejeita até o primeiro que não passa, e dali em diante nenhum rejeita;
   - **a família G-ABLA:** m = 4 (P1, P2, MEM, PERS), os limiares 0,0125, 0,0167, 0,025 e 0,05;
   - **a família G-MOD:** m = 2 (CON, EMB), os limiares 0,025 e 0,05;
3. **o gate passa** quando o Holm rejeita a hipótese nula daquele contraste (`rejeita` verdadeiro);
4. **a família não encolhe:** um contraste inconclusivo por premissa (a G-PESA, seção 5.3) entra no Holm com o p que tiver, mas a leitura
   dele é "inconclusivo por premissa", qualquer que seja o p. Um contraste sem p (menos de 2 bases com valor) entra com p = 1, como o
   `holm` já faz;
5. **o IC95 percentil** de cada contraste sai no relato como **descritivo** do tamanho do efeito. Ele não decide gate nenhum das duas
   famílias.

**O G-MVP** é um gate único, fora das famílias, e fica com a regra da tabela: o limite inferior do IC95 percentil (bilateral, logo a
0,025 unilateral) da fração de vidas ≥ 0,8. A fração por unidade é a média das 12 células, e o bootstrap é o mesmo do item 1.

**As premissas** (seção 5.3) também ficam pelo IC95: elas não testam a direção prevista, só se a medida existe.

### 5.3 As premissas

| premissa | regra (PROPOSTA) | se falha |
|---|---|---|
| **G-PESA** (por módulo) | no braço em que o módulo entra (o incentivo no M1, o hábito no M2, a memória no M3, a persistência no M3), a fração de decisões com `<modulo>_decidiu`: limite inferior do IC95 > 0,01 | a G-ABLA daquele módulo é **inconclusiva por premissa: o módulo não pesa.** É o caso "a ligação está errada ou o módulo não pesa" do D2: diagnosticar a fiação antes de culpar a arquitetura |
| **G-ELEGIVEL** | ao menos 80% das vidas do M3 com 3 rações elegíveis ou mais | o G-MVP é **inconclusivo por premissa:** os donos quase não deram ração com o pet com fome |

### 5.4 O G-CUSTO

O orçamento é o da seção 12 da espec, sem número novo:
- **o CPU por decisão no navegador:** o cérebro da v13 ≤ 2× o cérebro do A v11, no mesmo aparelho e no mesmo navegador, medido com e sem
  as sondas. **O A é medido uma vez, só em desempenho** (o tempo por decisão e por replay), **sem campanha comportamental** (Matheus,
  2026-10-25);
- **o log:** +0 B por dia (nenhum evento novo);
- **o replay de 14 dias da v13** ≤ 1,5× o da v12, no mesmo aparelho;
- **o estado aprendível** ≤ 1 000 inteiros, contados no `estado_interno`.

O custo em Python (s de CPU por vida) sai da calibração e do piloto como relato, para o tamanho da avaliação; não é gate.

### 5.5 A leitura

Os critérios D1 a D6 são os de `docs/TAREFA_V2_CEREBRO_A_BASELINE.md`, seção 3; a decisão do fallback é do Matheus (AF-1).

| G-MECANISMO | G-MVP | G-ABLA | leitura |
|---|---|---|---|
| falha | — | — | falha de implementação (D1): conserta o módulo; nenhuma vida roda |
| passa | passa | os 4 passam | **o modular vai à comida pelos próprios módulos, e cada um pesa no sentido previsto** (na pesquisa Python; o produto pronto pede também a seção 5.6) |
| passa | passa | algum falha ou é inconclusivo por premissa | o produto funciona; o módulo que não pesou vai ao diagnóstico da fiação (D2), não ao fallback |
| passa | falha | qualquer | com o oráculo (o T-CADEIA-1, D3) passando, a aprendizagem não chega lá: falha de implementação ou de calibração (D4), não da arquitetura |
| passa | inconclusivo por premissa | qualquer | registrado; os donos e a elegibilidade dizem por quê |

- **O G-MOD é lido à parte.** Passar não muda a leitura da etapa 1 (a modulação está desligada no principal); falhar é o resultado da
  hipótese experimental, registrado como está.
- **Por dono e por lugar, só descritivo.**
- **Gate que falha não para a V2.** O resultado negativo fica registrado como está.

### 5.6 O G-MVP é necessário, não suficiente, para o produto

A correção 4 da revisão. **O G-MVP passar na pesquisa Python não declara o produto pronto.** O A só deixa de ser o cérebro do MVP com os
dois gates da MV-2 (`docs/TAREFA_V2_MVP_MUNDO_PRODUTO.md`, seção 8):
- **(i) o gate de compatibilidade:** o cérebro modular cumpre o `Protocol` `Politica`, passa o **G-PAR** Python/TS e o **E2E-COMIDA** no
  jogo, na v13 (o laço do pet não muda; só a política);
- **(ii) o gate de prontidão:** o **G-MVP** deste plano, **e** o **G-CUSTO** medido na web (seção 5.4), **e** o **E2E-COMIDA** no jogo
  com o cérebro modular, numa vida comum e não só num save preparado (a ressalva do Matheus no #404).

| o que passou | o que se pode dizer |
|---|---|
| só o G-MVP (Python) | o cérebro modular faz a cadeia na pesquisa Python. **O produto não está pronto** |
| o G-MVP e o G-PAR | a mesma cadeia vale no TS, conta por conta. Falta o custo e o jogo |
| o G-MVP, o G-PAR, o G-CUSTO na web e o E2E-COMIDA no jogo | os dois gates da MV-2 fechados: a troca do A pelo modular no MVP pode ir ao Matheus |

**O E2E-COMIDA com a v13** é teste da integração (a tarefa do produto do modular), não deste plano. Aqui ele aparece só como condição.

## 6. A calibração, o piloto e o poder

A faixa **63101…63505** serve às duas coisas, com as bases separadas. **A avaliação (64101…64505) roda uma vez, e nada se ajusta olhando
para ela.**

### 6.1 A calibração dos valores de partida (bases 63101 e 63202)

Os valores de partida (o `ParametrosInatos`, espec, seção 4.9) são postos à mão; a espec deixa a calibração para o protótipo. Ela segue o
M10 (montar, calibrar junto, validar uma vez): **só no M3,** com todos os módulos juntos, nunca módulo a módulo.
- **O que pode mudar:** a magnitude dos `W⁰` (os sinais da tabela da seção 4.5 da espec ficam), as curvas `a_r`, `b_r` e `λ_r`, os τ,
  os η, o `w_mem`, o `w_pers`, o `N_desiste` (a regra da PE-6: o alcance mais uma decisão), o `H_max` e o g₀.
- **O que não pode:** as equações, as subchaves e qualquer número do motor, do corpo ou do mundo. Uma equação errada é falha de
  implementação (D1 ou D4) e volta à etapa 1a.
- **O critério, nesta ordem:** o T-CADEIA-1 passa com os valores; a taxa de fechamento do M3 nas bases da calibração ≥ 0,5 na mediana
  das vidas; nenhum H no teto (`pesos_no_teto` = 0); a G-PESA de cada módulo do M3 com a fração ≥ 0,01.
- **No máximo três rodadas,** cada uma registrada (o que mudou e por quê). **Os braços M0, M1, M2, M3-sp e M4 não são olhados na
  calibração:** eles herdam os valores do M3.
- **Se o critério não fecha em três rodadas,** os valores da melhor rodada ficam, e o que não fechou vai ao registro. A faixa que não fecha
  não bloqueia (a regra da calibração no fim).

**O adendo 1** congela os valores, num commit antes do piloto.

### 6.2 O piloto do N (bases 63303, 63404 e 63505)

- **K = 2 por base,** 6 unidades, os 8 braços do modular nas 12 células: 576 vidas. **Sem o A11.**
- **Serve para:**
  - o tamanho de efeito de cada contraste da seção 5.2 (G-MVP, G-ABLA, G-MOD);
  - as premissas G-PESA e G-ELEGIVEL;
  - a média do `g_apr` das vidas M4, que vira o valor fixo do M4-con;
  - o custo em Python por vida.
- **Os números dele não entram como evidência.**

### 6.3 O poder e o K

- **O efeito de planejamento:** a metade do efeito médio observado no piloto, para cada contraste. A metade porque o piloto é pequeno e
  tende a superestimar o efeito.
- **O K:** o menor de 4 a 10 por base com poder simulado ≥ 0,8 **em cada um** dos quatro contrastes da família G-ABLA e no G-MVP.
- **O método** (a correção 1 da revisão), sobre o da A1.9 (o plano da competição, seção 7):
  - **a réplica:** um bootstrap das unidades do piloto, com as quatro diferenças de cada unidade juntas (a correlação entre os contrastes
    fica), cada diferença centrada e deslocada para o efeito de planejamento dela; K × 5 unidades por réplica; 2 000 réplicas por K; a
    semente 4242;
  - **o teste em cada réplica** é o mesmo do gate: o p unilateral do bootstrap agrupado por base (seção 5.2.1), com 1 000 reamostragens
    internas, para o custo da simulação caber (a avaliação usa 10 000);
  - **o α de cada contraste da G-ABLA é 0,0125** (= 0,05/4), nos quatro;
  - **o poder é por contraste:** a fração das réplicas em que aquele contraste tem p ≤ 0,0125.
- **Por que 0,0125, e não o Holm completo na simulação:** o Holm rejeita toda hipótese que o limiar fixo de 0,05/4 rejeita (o limiar do
  primeiro posto é o menor dos quatro). Então o poder por contraste no Holm é **no mínimo** o poder a 0,0125. Simular a 0,0125 dá um K
  conservador, nunca otimista, e com uma conta só por contraste. Simular o Holm completo daria um K menor ou igual, à custa de fazer o
  poder de um contraste depender do efeito dos outros três no piloto.
- **O poder conjunto** (as quatro rejeitam na mesma réplica, a 0,0125) sai no adendo 2 só como relato. Ele não entra no critério do K.
- **O G-MVP,** gate único, fora do Holm:
  - **o valor de planejamento:** 0,8 + ½ × (a fração de vidas do M3 com a cadeia no piloto − 0,8);
  - **o teste em cada réplica:** o limite inferior do IC95 percentil ≥ 0,8 (logo 0,025 unilateral);
  - **se a fração do piloto for ≤ 0,8,** não há poder a calcular; o G-MVP sai da conta do K, e o relato diz isso.
- **A família G-MOD:** o poder de cada contraste a 0,025 (= 0,05/2), pelo mesmo argumento. É só relato e não entra no K.
- **Se nem K = 10 chega a 0,8,** a avaliação roda com 10, e o poder sai declarado. **Se o efeito do piloto tiver o sinal contrário ao
  previsto,** aquele contraste não entra na conta do K, e o relato diz isso.

**O adendo 2** guarda o K, o poder de cada gate, as premissas do piloto, o valor do M4-con e o custo, num commit antes da avaliação.

**O custo esperado:** uma vida do v11 de 14 dias leva cerca de 2 s com o replay (o plano da competição, adendo 1). O modular faz sete
somas por decisão em vez de uma (espec, seção 12); com 2 a 6 s por vida, o piloto fica em 20 a 60 min de CPU, e a avaliação com K = 10
(50 unidades, 5 400 vidas), em 3 a 9 h. É estimativa, sem artefato; o número real vai ao adendo 2.

### 6.4 A avaliação (uma vez) e o depois

- **As bases:** 64101, 64202, 64303, 64404 e 64505, com o K do adendo 2, os 9 braços e as 12 células.
- **O replay:** toda vida é rejogada do disco e comparada bit a bit (G1). Uma divergência para tudo.
- **As falhas altas em toda vida:** com uma subchave desligada, o termo do módulo é 0 em toda decisão; o M0 fica com d̂ = 0, H = 0 e
  memória vazia; o M4-emb lê a série E inteira do doador; o reflexo do sono nunca sorteia.
- **Depois da avaliação, o conserto (AF-3):** se a leitura apontar falha de implementação (D1, D2 ou D4), a rodada de diagnóstico e
  conserto ajusta o código. **A reavaliação usa uma faixa nova,** pedida ao coordenador, num adendo commitado antes. O resultado nas
  64101…64505 fica registrado como está, e essas sementes não voltam.

## 7. A comparação com o A (descritiva; o D6)

O A11 roda **uma vez, na avaliação,** com a função "baseline" (`docs/TAREFA_V2_CEREBRO_A_BASELINE.md`, seção 1). **Não há gate do A, nem
margem tirada do A, nem piloto do A.**

| contraste | as medidas |
|---|---|
| M3 − A11 | o `D_FE` dos dias 8 a 14; a privação; as refeições por dia; a taxa de fechamento; a fração de vidas com a cadeia |
| M0 − A11 | as mesmas: o inato modular contra a cascata do A, sem aprendizado de nenhum dos lados do modular |

- **Cada um com o IC95 do `contraste_pareado`,** sem Holm e sem margem de equivalência. É o "registrar" do D6.
- **O D6 sozinho não é limitação:** o modular pode perder para o A e continuar sendo o alvo (`TAREFA_V2_CEREBRO_A_BASELINE`, seção 3).
- **O diagnóstico do MVP** (1 ou 2 refeições por vida em 2 dias) fica como referência de ordem de grandeza, no relato, ao lado das refeições
  por dia do A11 na avaliação. Os dois não se comparam: o dono, o motor (TS × Python) e o horizonte são outros.

## 8. As leituras descritivas, sem gate

**D-2, "memória cedo, hábito depois"** (Lengyel e Dayan 2007, NIPS 20, VERIFICADA sem DOI, resumo; espec, seção 2.5, passo 3):
- **a fonte afirma:** um controle episódico ao lado do modelo do mundo e do hábito, útil sobretudo no começo do aprendizado, antes de o
  hábito se formar;
- **leitura do Digilab, [HIPÓTESE]:** no M3, o termo M decide mais nas primeiras refeições, e o hábito H depois;
- **a medida:** as séries diárias de `influencia_por_modulo` para a memória e para o hábito, no M3, dias 1 a 14, e a diferença
  `centro_temporal`(hábito) − `centro_temporal`(memória), com o IC95 por unidade. Positiva é a ordem prevista;
- **sem gate.** O relato mostra as duas curvas por dia, por lugar (o comedouro é onde a memória pode pesar), e a diferença.

**D-1, se a excitação mexe mais na exploração que na taxa de aprendizado** (Doya 2002, `10.1016/s0893-6080(02)00044-8`, VERIFICADA,
resumo: associa a velocidade de aprendizagem à acetilcolina e a aleatoriedade da escolha à noradrenalina; a excitação no `g_apr` é
HIPÓTESE EXPERIMENTAL do Digilab):
- **a exploração:** a fração das decisões de explorar e a entropia das ações escolhidas por dia (bits, sobre as sete ações), M4 − M4-con;
- **a taxa de aprendizado:** a média de |Δd̂| por consumo e de |ΔH| por consequência, M4 − M4-con;
- **a leitura:** cada diferença dividida pelo desvio padrão das unidades do M4-con (o efeito padronizado), com o IC95. "Mexe mais na
  exploração" se o efeito padronizado da exploração passa o da taxa e os ICs não se cruzam. Sem gate;
- **a ressalva:** no protótipo, a excitação age só pelo `g_apr` (espec, seção 4.3). Um efeito na exploração viria pelo comportamento
  aprendido, não por um `g_exp` modulado.

**As PE "no protótipo" que a avaliação informa** (espec, seção 15), todas descritivas:
- **PE-6** (`N_desiste`): a calibração; a `intencoes_com_meta` e o fim das intenções por motivo;
- **PE-10** (o decaimento do H): `pesos_no_teto` no fim de cada vida;
- **PE-16** (N_ep = 16): quantos episódios saem por vida, e quantos com r > 0;
- **PE-5, PE-8 e PE-11:** não se testam na etapa 1 (nenhum braço as muda).

**Os outros descritivos:** o motivo por módulo (as seis sondas) por braço e por dia; as ações; a exaustão; o fim das intenções por motivo;
as visitas ao lugar lembrado e quantas foram vazias (o T-MEM-4 na vida).

## 9. As faixas de sementes

| uso | faixa | bases |
|---|---|---|
| calibração dos valores de partida | **63101…63505** | 63101, 63202 (K = 2: 4 unidades, 48 vidas do M3 por rodada) |
| piloto do N | **63101…63505** | 63303, 63404, 63505 (K = 2) |
| avaliação única | **64101…64505** | 64101, 64202, 64303, 64404, 64505 (K do adendo 2) |

- **Reservadas pelo Gerente e aprovadas pelo Matheus em 2026-10-25** (PPM-1). As duas linhas estão em
  `experiments/bancada/faixas.py` (`FAIXAS_RESERVADAS`) neste PR, com a fonte. É a única mudança de código desta tarefa.
- **O prefixo** `"digibrain_prototipo"` entra no `PREFIXOS_UNIDADES` com o orquestrador (seção 10), com o teste de colisão.
- **As sementes dos testes** (101…505) servem à fumaça do orquestrador e aos testes de mecanismo.

## 10. A ordem das etapas que este plano pressupõe

**Os gates de engenharia são pré-condição, não evidência de aprendizagem (DM-2).** Nenhum deles entra na leitura da seção 5.5. **Há dois
trilhos, e o TS não bloqueia o Python** (a correção 3 da revisão; a tabela da seção 5.1):

| trilho | os passos, em ordem | o que precisa passar antes | o que sai |
|---|---|---|---|
| **Python (a pesquisa)** | 1. etapa 1a (feita, #414); 2. o código da avaliação (feito, #414); 3. a calibração; 4. o piloto; 5. a avaliação única | antes do passo 3: G1, G2, G-INT, G-RECEPTOR, G-SEM-DIRECAO, T-PONTO-1 a 3 e o G-MECANISMO | o G-MVP, as G-ABLA, as G-MOD, os descritivos |
| **TS (a integração, etapa 1b)** | 6. o gabarito v12 em TS (feito, #413); 7. o gancho do `ponto` no laço do TS (feito, #413); 8. o cérebro em TS e o G-PAR; 9. a medição do custo (a do A feita, #413; a da v13 no passo 8) | antes do passo 7: a primeira parte do T-PONTO-4 (o gabarito v12 em TS) | o G-PAR, o G-CUSTO e, com a tarefa do produto, o E2E-COMIDA na v13 |

**O trilho Python:**
1. **Etapa 1a:**
   - os módulos (seção 1), com as subchaves `p1` e o modo do `g_apr` (PROPOSTAS), cada mudança atrás da chave, com o G2;
   - os testes de mecanismo (G-MECANISMO), o T-CADEIA-0 (o A só lido), o T-CADEIA-1 (o oráculo, D3) e o T-CADEIA-2;
   - os T-PONTO-1 a 3 (o `ponto` em EXPLORAR; o `raise` fora do mapa; o G2 das 196 vidas);
   - os G1, G-INT, G-RECEPTOR e G-SEM-DIRECAO.
2. **O código da avaliação, ainda sem vida de pesquisa:** as medidas da seção 4 em `digilab/metrics.py`, com teste; o orquestrador
   `experiments/run_v2_digibrain_prototipo.py` e a config em `experiments/configs/`; o prefixo; a lista permitida do teste do layout
   (PPM-3); a fumaça nas sementes dos testes.
3. **A calibração** (63101, 63202) → o adendo 1.
4. **O piloto** (63303 a 63505) → o adendo 2.
5. **A avaliação única** (64101 a 64505) → `docs/RESULTADO_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md`.

**O trilho TS (etapa 1b):**

6. **o gabarito das vidas v12 do jogo em TS primeiro,** gravado e conferido contra a versão atual (a primeira parte do T-PONTO-4).
   **Feito no #413** (`web/app/test/gabaritos/v12_jogo_ts.json`, 5 vidas, byte a byte antes da mudança);
7. **o gancho do `ponto` no laço do TS,** atrás da opção `digibrain` da v13, desligada por padrão (o resto do T-PONTO-4). **Feito no
   #413:** o `Mundo` do TS já validava o `ponto` como o Python; o que faltava era o laço perguntar o alvo ao cérebro;
8. **o cérebro modular em TS e o G-PAR** decisão a decisão, contra os gabaritos do Python com os valores do adendo 1. **Recomendação:** o
   porte do cérebro só depois do adendo 1, para não portar duas vezes; os passos 6 e 7 podem andar antes;
9. **a medição pontual do A v11 no navegador** (só desempenho), depois a da v13: o G-CUSTO.

- **O G-PAR e o T-PONTO-4 não bloqueiam nenhuma vida da pesquisa Python.** Eles bloqueiam a integração TS e o gate de compatibilidade
  da MV-2 (i).
- **O produto pronto** pede os dois trilhos: o G-MVP do Python **e** o G-PAR, o G-CUSTO na web e o E2E-COMIDA no jogo (seção 5.6).
- **Os critérios do baseline** (AF-1 a AF-6) foram decididos em 2026-10-25 (seção 13); a condição "decididos antes da avaliação"
  (`TAREFA_V2_CEREBRO_A_BASELINE`, seção 7) está cumprida.

## 11. Riscos

| # | risco | o que o plano faz |
|---|---|---|
| R-1 | **o M0 já come bem:** com o inato à mão, a cadeia acontece sem aprender, e a G-ABLA-P1 fica pequena | o G-MVP e a G-ABLA são lidos separados (seção 5.5); a `falta_ao_comer` mede o "com menos fome", não o "comeu" |
| R-2 | **a calibração vira ajuste ao resultado** | só o M3, só critérios de funcionamento, três rodadas, bases próprias; os braços da ablação não são olhados (seção 6.1) |
| R-3 | **um módulo não pesa** (a sonda quase nunca decide) | a G-PESA torna o contraste inconclusivo por premissa, e o D2 manda olhar a fiação |
| R-4 | **o efeito pequeno e o K no teto** | o poder declarado; a metade do efeito do piloto como planejamento |
| R-5 | **os donos dão pouca ração com o pet com fome** | a G-ELEGIVEL; os donos ficam como células, só descritivas |
| R-6 | **o layout do MVP vaza para a pesquisa** | só o orquestrador desta avaliação entra na lista do teste (PPM-3); os cenários de antes não mudam |
| R-7 | **o M4-emb muda a contagem da rng** | a excitação de outra vida só muda o `g_apr`; o sorteio continua uma chamada por decisão com dois candidatos ou mais, e a rng de política é só do cérebro |
| R-8 | **a tentação de olhar o A** | o A11 só na avaliação, sem gate nem margem (seção 7) |

## 12. Artefatos e reprodução

- `artifacts_v2_digibrain_prototipo/calibracao/`, `.../piloto/` e `.../avaliacao/`: as medidas por vida, o `meta.json` (o sha do pacote,
  a config, as sementes, a `ConfigDigibrain` de cada braço) e o resumo. As vidas ficam fora do git; os artefatos, num commit próprio.
- O orquestrador e a config entram num PR de código antes da calibração, com a fumaça (seção 10, passo 2).

## 13. Decisões do Matheus

**DECIDIDAS em 2026-10-25 (Matheus, por relato do Gerente),** na revisão do #412:
- **as PPM-1 a PPM-7 e a PPM-9: aprovadas pelas recomendações** (a coluna "recomendação" é o que vale);
- **a PPM-8: aprovada depois de corrigir o cálculo de poder.** A correção está na seção 6.3 desta versão (o α de 0,0125 por contraste, o
  poder por contraste), e esta versão volta à revisão dele;
- **as quatro correções pedidas,** feitas nesta versão: o poder com o Holm (seção 6.3), a regra operacional do Holm (seção 5.2.1), a ordem
  dos gates (seções 5.1 e 10) e o G-MVP como condição necessária, não suficiente (seção 5.6).

**Sem vidas e sem merge até o Matheus revisar a versão corrigida.** Os números das decisões continuam SEM FONTE.

| # | decisão | recomendação (o que vale) | custo de errar |
|---|---|---|---|
| **PPM-1** (DECIDIDA) | as faixas | **63101…63505 para a calibração e o piloto; 64101…64505 para a avaliação única,** como o Gerente reservou | sem faixa aprovada, nenhuma vida pode rodar; faixas trocadas depois deixam linhas órfãs na tabela |
| **PPM-2** (DECIDIDA) | os braços | **os 9 da seção 2:** a escada M0 a M3, o M3-sp (a persistência, que a espec manda desligar), o M4 com os dois controles do V3 e o A11 só na avaliação | sem o M3-sp: a persistência não tem ablação, e o D2 fica sem ela; com o A no piloto: o A volta a ser medido além do baseline |
| **PPM-3** (DECIDIDA) | o cenário | **o MVP como o jogo roda:** o `CONFIG_MUNDO_MVP`, o contrato desligado, os 4 donos sem ensino × 3 lugares, 14 dias; e **a permissão para o orquestrador desta avaliação usar o layout do MVP** (a lista do teste do layout; a MV-10 limitou o layout ao produto) | o layout padrão: as árvores voltam, e a pergunta deixa de ser a do produto; o contrato ligado: a visão em cone muda o que o pet vê, e o G-PAR com o v12 deixa de valer para o mesmo cenário |
| **PPM-4** (DECIDIDA) | o G-MVP | **W = 8 decisões (2 h); a ração elegível com a fome abaixo de 0,5; a vida com a cadeia com a taxa ≥ 0,5; o limite inferior do IC95 da fração de vidas ≥ 0,8;** a G-ELEGIVEL com 80% das vidas e 3 rações | mais frouxo: um pet que come metade das vezes passa como pronto para o produto; mais apertado: o gate mede a paciência do dono, não o cérebro |
| **PPM-5** (DECIDIDA) | as G-ABLA | **as quatro medidas e direções da seção 5.2,** a do M-MEM só no comedouro, o Holm a 0,05 (pelo p do bootstrap, seção 5.2.1); a G-PESA com 0,01 | sem a G-PESA: um módulo que não decide nunca lê como "não ajuda"; todas as células na G-ABLA-MEM: o perto e o longe diluem o único lugar em que a espec prevê efeito |
| **PPM-6** (DECIDIDA) | o G-CUSTO | **o orçamento da seção 12 da espec,** sem número novo; o A medido uma vez, só em desempenho | sem orçamento decidido, o D5 vira impressão (AF-4) |
| **PPM-7** (DECIDIDA) | a calibração | **só o M3, as constantes do `ParametrosInatos`, os quatro critérios da seção 6.1, três rodadas,** nas bases 63101 e 63202 | calibrar cada braço: a ablação mede a calibração, não o módulo; sem limite de rodadas: a calibração vira busca pelo resultado |
| **PPM-8** (DECIDIDA depois da correção do poder) | o piloto e o N | **K = 2 nas bases 63303 a 63505 (6 unidades, 576 vidas); o efeito de planejamento na metade do piloto; o K de 4 a 10 com poder ≥ 0,8 por contraste, a 0,0125 (seção 6.3)** | piloto maior: mais CPU antes de saber se o módulo pesa; o efeito do piloto inteiro: a avaliação fica subpotenciada se o piloto exagerou |
| **PPM-9** (DECIDIDA) | a reavaliação depois do conserto (AF-3) | **numa faixa nova, por adendo,** com o resultado das 64101…64505 registrado como está | reusar as 64101…64505: a avaliação deixa de rodar uma vez só |

**Os critérios do baseline e do fallback** (`docs/TAREFA_V2_CEREBRO_A_BASELINE.md`, seção 8), DECIDIDOS em 2026-10-25 (Matheus, por
relato do Gerente):
- **AF-1, AF-2, AF-3 e AF-6:** aprovados pelas recomendações;
- **AF-4:** usa o orçamento já definido na espec (seção 12), o mesmo do G-CUSTO (seção 5.4);
- **AF-5:** já está decidida pela DM-8, sem reabertura.

**Pressuposto deste plano, não decisão dele:** as subchaves `p1` e o modo do `g_apr`. A etapa 1a as propõe e as implementa atrás da
chave.

## Adendo 1: os valores calibrados (2026-10-25, worker D, Claude Code, Opus 5.5)

**O que é:** a calibração da seção 6.1, autorizada pelo Matheus em 2026-10-25 ("Siga o recomendado"), despachada pelo Gerente.
- **Escopo:** só o M3, nas bases 63101 e 63202, com K = 2, 14 dias e as 12 células (48 vidas por rodada), pelo
  `experiments/run_v2_digibrain_prototipo.py`.
- **Rodadas:** três, o máximo.
- **Os outros braços** não foram rodados nem olhados.
- **Nenhuma vida** da faixa 64101…64505 nem das bases do piloto.
- **O critério não fechou em nenhuma rodada.** Pela seção 6.1, ficam os valores da melhor rodada, a 3, e o que não fechou vai ao
  registro, sem bloquear.
- **A decisão do Matheus (2026-10-26), registrada como ele pediu:** **a calibração não atingiu os critérios de fechamento** (a mediana do
  fechamento do M3 ficou em 0,412 contra ≥ 0,5; a G-PESA do incentivo em 0,0077 e a da persistência em 0,0014 contra ≥ 0,01). **Os
  valores da rodada 3 são a melhor rodada disponível, não uma calibração bem-sucedida.** O piloto (seção 6.2) roda com eles, conforme o
  plano; **só o piloto:** a avaliação única (seção 6.4) não começa automaticamente. Depois do piloto, os resultados e as premissas
  (G-PESA e G-ELEGIVEL) vão ao Matheus para revisão antes de qualquer decisão sobre a avaliação. Toda leitura do G-MVP, do G-ABLA-P1 e do
  G-ABLA-PERS nas fases seguintes carrega esta nota.

**Os valores congelados** (`ConfigDigibrainInatos`, `digilab/config.py`; continuam PROPOSTOS, e o Matheus decide). Só mudou o que a
seção 6.1 permite, e os sinais da tabela 4.5 da espec ficam; nenhuma equação, subchave nem número do motor, do corpo ou do mundo mudou:

| valor | partida (rodada 1) | congelado (rodada 3) | rodada da mudança | por quê |
|---|---|---|---|---|
| `eta_h` (o passo do P2) | S/16 | S/128 | 2 | na rodada 1, 283 dos 7 728 pesos de hábito acabaram no teto; o hábito de comer saturava (`pesos_no_teto` máximo 0,0745) |
| `w_pers` | S/2 | 2S | 2 | a persistência quase não decidia (0,0002): na segunda decisão de uma intenção, h = mul(S/2, 256) = 128 |
| `tau_c` (ticks) | 60 | 30 | 2 | o mesmo motivo: o C da intenção nova sobe de 256 para 512 |
| `W⁰[dormir, u_energia]` | 2S | 3S | 2 | nas rações elegíveis que não fecharam, 43,6% das decisões da janela estavam sob o reflexo do sono, e a exaustão era 0,3114 |
| `W⁰[explorar, u_energia]` | −S | −2S | 2 | o mesmo: o pet cansado explorava e chegava ao reflexo |
| `W⁰[comer, u_fome]` | 2S | 3S | 3 | na rodada 2, o hábito menor tirou a vontade de comer com fome moderada (3,53 refeições por dia, contra 4,44) |
| `W⁰[comer, vies]` | −S | −17S/16 | 3 | mantém o ponto do T-CADEIA-2 (a falta da fome 307) abaixo do limiar inato, com o peso maior da fome |
| `W⁰[dormir, u_fome]` | −S/2 | −S | 3 | na rodada 2, dormir passou a ganhar do comer: cerca de metade das decisões nas janelas que não fecharam era dormir |

**Os critérios, rodada a rodada** (a ordem da seção 6.1; o T-CADEIA-1 passa nas três, em `tests/test_digibrain_vidas.py`):

| critério | rodada 1 | rodada 2 | rodada 3 |
|---|---|---|---|
| o fechamento do M3, a mediana das vidas (≥ 0,5) | 0,4000 | 0,3350 | **0,4123** |
| `pesos_no_teto` (= 0 em toda vida; o máximo) | 0,0745 | **0** | **0** |
| G-PESA, o incentivo (≥ 0,01) | 0,0006 | 0,0089 | 0,0077 |
| G-PESA, o hábito | **0,3061** | **0,1657** | **0,1659** |
| G-PESA, a memória | **0,1139** | **0,1351** | **0,1228** |
| G-PESA, a persistência | 0,0002 | 0,0016 | 0,0014 |
| fecha | não | não | não |

- **Os artefatos de cada número:** `artifacts_v2_digibrain_prototipo/calibracao/rodada_<n>/`. O `resultado.json` traz os critérios; o
  `medidas.json`, as 48 vidas; o `meta.json`, os valores, o commit e as sementes; o `diagnostico.json` (de
  `experiments/diagnostico_calibracao_digibrain.py`, que rejoga as vidas do disco com os valores da rodada e confere que as medidas
  refeitas são as gravadas) traz o reflexo, as ações e a ração nas janelas que não fecharam, o hábito no teto e as intenções. As vidas
  ficam fora do git; os commits das rodadas são o 659cd70, o c9db542 e o 4924863.
- **A melhor rodada é a 3:** na ordem dos critérios, as três passam o T-CADEIA-1, e a rodada 3 tem a maior mediana. Ela e a 2 são as
  únicas com o teto em 0.
- **O que não fechou** (o registro, seção "DIGIBRAIN-MODULAR-CALIBRACAO"):
  - a mediana do fechamento: 0,4123;
  - a G-PESA do incentivo (0,0077) e da persistência (0,0014).

  O G-MVP e as G-ABLA-P1 e G-ABLA-PERS do piloto e da avaliação ficam sujeitos a isso; a seção 5.3 já lê um contraste com a G-PESA
  falhando como inconclusivo por premissa.

## Adendo 2: o piloto do N (2026-10-26, worker D, Claude Code, Opus 5.5)

**A nota antes de tudo** (a decisão do Matheus de 2026-10-26, a mesma do adendo 1):
- **A calibração não atingiu os critérios de fechamento.** A mediana do fechamento do M3 ficou em 0,412, contra ≥ 0,5. A G-PESA do
  incentivo ficou em 0,0077, e a da persistência em 0,0014, contra ≥ 0,01.
- **Os valores da rodada 3 são a melhor rodada disponível, não uma calibração bem-sucedida.**
- O piloto rodou com eles, conforme o plano. **Rodou só o piloto.**
- Este adendo vai ao Matheus para revisão antes de qualquer decisão sobre a avaliação (seção 6.4). A avaliação não começa
  automaticamente.
- Toda leitura do G-MVP, do G-ABLA-P1 e do G-ABLA-PERS carrega esta nota.

**O que é:** o piloto da seção 6.2, autorizado pelo Matheus em 2026-10-26 e despachado pelo Gerente.
- **Escopo:** as bases 63303, 63404 e 63505, com K = 2 (6 unidades), os 8 braços do modular (M0, M1, M2, M3, M3-sp, M4, M4-emb e M4-con)
  nas 12 células e 14 dias. São **576 vidas, sem o A11.**
- **Como rodou:** pela `experiments/configs/v2_digibrain_prototipo/piloto.json` e o `experiments/run_v2_digibrain_prototipo.py`, no
  commit `c3a4d82`, com a árvore limpa.
- **Os valores:** os do `config.py` (a rodada 3). Nenhum valor mudou no piloto.
- **O que não rodou:** nenhuma vida da faixa 64101…64505 e nenhuma preparação da avaliação.
- **As conferências:**
  - toda vida foi rejogada do disco e conferida bit a bit (G1), com as falhas altas de cada braço;
  - antes da run, passaram o G2 (as 196 vidas e o gabarito do MVP), o G1, o G-MECANISMO e os T-PONTO (59 testes).
- **Os números do piloto não entram como evidência.** Nenhum gate é lido aqui; o p sai só como descrição.

**Os artefatos** ficam em `artifacts_v2_digibrain_prototipo/piloto/`; as vidas ficam fora do git.
- **`meta.json`:** o commit, as sementes, os valores e o g_apr do M4-con;
- **`medidas.json`:** as 576 vidas;
- **`resultado.json`:** a análise do orquestrador (os contrastes, as premissas, o K e o custo);
- **`relato.json`:** o IC do G-MVP e as premissas por braço e por célula. Sai de `experiments/relato_piloto_digibrain.py`, que só lê os
  outros três.

**A ordem do M4-con:** o orquestrador resolve em duas passadas, na mesma run.
- **Primeiro** rodam os seis braços que não dependem do M4.
- **Depois** rodam o M4-emb (com a série E do doador) e o M4-con.
- **O g_apr fixo do M4-con** é a média das vidas M4 da própria run: **1 918,54, arredondado para 1 919** (PROPOSTO). É o valor que o
  `adendo_do_piloto()` entrega à avaliação.

**O tamanho de efeito de cada contraste,** sem leitura de gate:
- positivo = a direção da espec;
- 6 unidades em 3 bases;
- o IC95 percentil vem do bootstrap agrupado por base, com 10 000 reamostragens e a semente 4242.

| contraste | a medida | média | IC95 | p unilateral (descritivo) |
|---|---|---|---|---|
| G-MVP | a fração de vidas do M3 com a taxa de fechamento ≥ 0,5 | 0,5000 | [0,5000; 0,5000] | — (o limiar é 0,8) |
| G-ABLA-P1 | `falta_ao_comer`(M0) − (M1) | 0,0429 | [0,0362; 0,0551] | 0,0000 |
| G-ABLA-P2 | `repeticao_apos_alivio`(M2) − (M1) | −0,0155 | [−0,0275; 0,0024] | 0,9644 |
| G-ABLA-MEM | a taxa de fechamento(M3) − (M2), só no comedouro | 0,0872 | [−0,0049; 0,1995] | 0,0360 |
| G-ABLA-PERS | `intencoes_com_meta`(M3) − (M3-sp) | 0,0204 | [0,0038; 0,0320] | 0,0000 |
| G-MOD-CON | `D_FE`(M4-con) − (M4) | −0,0172 | [−0,0262; −0,0086] | 1,0000 |
| G-MOD-EMB | `D_FE`(M4-emb) − (M4) | −0,0039 | [−0,0077; 0,0024] | 0,9640 |

- **O G-MVP não varia entre as unidades.** Em toda unidade, as mesmas 6 das 12 células fecham a cadeia: o comedouro do aleatório e do
  relapso, e o perto dos quatro donos. As outras 6 não fecham.
  - A fração é 0,5 nas seis unidades.
  - A mediana da taxa de fechamento do M3 é 0,390.
- **Os sinais contrários:** o G-ABLA-P2 e os dois G-MOD saem com o sinal oposto ao previsto. Nos G-MOD, o M4 tem mais déficit que o M4-con
  e que o M4-emb.

**As premissas** (seção 5.3). O IC95 decide a premissa, mas aqui ela só é relatada:

| premissa | braço | média | IC95 | o limiar |
|---|---|---|---|---|
| G-PESA, o incentivo | M1 | 0,0190 | [0,0181; 0,0205] | limite inferior > 0,01 |
| G-PESA, o hábito | M2 | 0,1724 | [0,1661; 0,1784] | idem |
| G-PESA, a memória | M3 | 0,1163 | [0,1062; 0,1279] | idem |
| G-PESA, a persistência | M3 | 0,0017 | [0,0012; 0,0022] | idem |
| G-ELEGIVEL | M3 | 1,0 (as 72 vidas têm 3 rações elegíveis ou mais) | — | ≥ 0,8 |

- **Por braço e por célula:** o `relato.json` traz a fração de cada módulo em cada um dos 8 braços e em cada célula, e a G-ELEGIVEL de
  cada braço e célula.
- **A G-ELEGIVEL** é 1,0 em todos os braços e em todas as células: nenhuma vida ficou sem ração elegível.
- **A premissa do incentivo no M1, por lugar:**
  - no longe, de 0,0072 a 0,0109;
  - no comedouro e no perto, de 0,0141 a 0,0367.
- **A premissa da persistência no M3** fica de 0,0005 a 0,0032 em todas as células; nenhuma passa de 0,01.

**O que o piloto sugere sobre o incentivo e a persistência,** os dois que quase não pesaram na calibração (leitura minha, sem gate):
- **O incentivo:**
  - a calibração mediu a G-PESA dele no M3 (0,0077), mas o plano mede a premissa no M1, onde o incentivo entra sozinho;
  - no M1 do piloto, ela fica em 0,0190, com o IC inteiro acima de 0,01;
  - no M3 do piloto, continua em 0,0089. O hábito e a memória tomam as decisões que o incentivo decidiria;
  - o contraste do P1 tem o IC inteiro positivo;
  - se a avaliação repetir isso, a premissa do G-ABLA-P1 passa.
- **A persistência:**
  - a premissa fica em 0,0017 no M3, longe de 0,01, em todas as células;
  - o contraste `intencoes_com_meta` sai positivo (0,0204);
  - com a premissa assim, a seção 5.3 lê o G-ABLA-PERS como **inconclusivo por premissa,** qualquer que seja o p. É o que se espera da
    avaliação com os valores de hoje;
  - a explicação provável continua a do diagnóstico da calibração: só 2,28% das decisões têm uma intenção em curso.

**O K pela seção 6.3:**
- o efeito de planejamento é a metade do efeito do piloto;
- 2 000 réplicas por K, 1 000 reamostragens internas, a semente 4242;
- α = 0,0125 nos G-ABLA.

| K por base | G-ABLA-P1 | G-ABLA-MEM | G-ABLA-PERS | os três juntos (só relato) |
|---|---|---|---|---|
| 4 | 1,000 | 0,599 | 0,525 | 0,337 |
| 5 | 1,000 | 0,680 | 0,578 | 0,408 |
| 6 | 1,000 | 0,731 | 0,664 | 0,487 |
| 7 | 1,000 | 0,806 | 0,693 | 0,564 |
| 8 | 1,000 | 0,857 | 0,736 | 0,636 |
| 9 | 1,000 | 0,859 | 0,767 | 0,669 |
| 10 | 1,000 | 0,893 | **0,800** | 0,716 |

- **O K PROPOSTO: 10 por base** (50 unidades). É o menor K com poder ≥ 0,8 nos três contrastes que entram na conta. Quem decide é o
  G-ABLA-PERS, que chega a 0,800 justo no K = 10.
- **Ficam fora da conta, como a seção 6.3 manda:**
  - o G-ABLA-P2: o sinal do piloto é o contrário do previsto;
  - o G-MVP: a fração do piloto (0,5) não passa de 0,8, e não há poder a calcular;
  - os dois G-MOD: o sinal é o contrário, e nenhum poder foi calculado para eles.
- **O custo de errar o K:**
  - com K = 10, a avaliação tem 5 400 vidas;
  - um K menor, por exemplo 7, já cobre o P1 e o MEM. Mas deixaria o poder do PERS em 0,69, num contraste que deve sair inconclusivo por
    premissa de qualquer jeito;
  - a regra da seção 6.3 não abre essa exceção, e por isso a proposta é 10.

**O custo em Python** (do `resultado.json`: a CPU de cada vida, com a gravação, o replay e as conferências):
- **por vida:** de 2,27 a 2,40 s, conforme o braço; o M3 é o mais caro;
- **o piloto:** as 576 vidas levaram 233 s de parede em 8 processos, e a run inteira, 269 s;
- **a avaliação com K = 10** (5 400 vidas, com o A11): estimada em 12 553 s de CPU. São cerca de 3,5 h, ou cerca de meia hora em 8
  processos. A estimativa supõe que o A11 custa a média dos braços do modular; ele não rodou no piloto.

**Um achado nas células** (o registro, seção "DIGIBRAIN-MODULAR-PILOTO"):
- **No comedouro, a vida do dono incoerente é byte a byte a mesma do atencioso.** Isso vale nos 8 braços e nas 6 unidades (48 de 48
  pares), e também nas 4 vidas da rodada 3 da calibração.
- **No perto e no longe,** as vidas dos dois diferem.
- **O porquê (leitura minha):** com o filtro `sem_ensino`, o incoerente fica sem o elogio e a repreensão, e o que sobra dele é o cuidado
  do atencioso.
- **Na prática,** há 11 células distintas, e o comedouro do atencioso pesa duas vezes. Isso vale também no G-ABLA-MEM: 2 das 4 células
  dele são iguais.
- Nada foi mudado; é pergunta para o Matheus.

**Para o Matheus decidir, antes da avaliação** (o PR deste adendo leva as opções):
- o K (PROPOSTO: 10);
- o g_apr do M4-con (PROPOSTO: 1 919);
- se a avaliação roda assim, com o G-ABLA-PERS esperado inconclusivo por premissa e o G-MVP esperado abaixo do limiar;
- o que fazer com as células iguais do comedouro.

**As decisões do Matheus (2026-10-26), DECIDIDAS, registradas pelo Gerente antes da primeira vida da faixa 64101…64505:**
- **K = 10 por base** (50 unidades; 5 400 vidas com o A11).
- **O g_apr do M4-con = 1 919** (a média das vidas M4 do piloto, arredondada).
- **As 12 células são a análise principal.** A duplicação do comedouro fica registrada: no comedouro, com o filtro `sem_ensino`, a vida
  do dono incoerente é byte a byte a do atencioso, em todo braço; há 11 células distintas e o comedouro do atencioso pesa duas vezes na
  média por unidade, inclusive no G-ABLA-MEM. **A leitura com 11 células entra só como análise descritiva, sem gate** (seção 8), ao lado
  da principal.
- **A avaliação única roda com os valores atuais, sem novos ajustes.** Fica explícito, antes de rodar: **o G-MVP pode falhar** (no piloto,
  a fração ficou em 0,5 contra o limiar 0,8, com as mesmas 6 células fechando em toda unidade), e **o contraste da persistência
  (G-ABLA-PERS) será inconclusivo por premissa se a G-PESA da persistência falhar** (no piloto, 0,0017 contra ≥ 0,01). Os dois saem
  registrados como estão, sem ajuste depois de olhar a faixa.
- **Nada disto declara o produto pronto** (seção 5.6): o G-MVP é necessário, não suficiente, e o gate de compatibilidade do produto
  (G-PAR, G-CUSTO, E2E-COMIDA na web) é outro.
- A avaliação é despachada pelo Gerente só depois de haver disco para as vidas (o D: estava com 1 GB livre em 2026-10-26).

## Adendo 3: o conserto depois do diagnóstico (2026-10-26, Gerente; PROPOSTO, revisão 3, para a revisão do Matheus)

**Status: PROPOSTO, revisão 3. Nada deste adendo está decidido, implementado ou executado.** Ele segue o pedido do Matheus de
2026-10-26, depois do merge do diagnóstico (#422): preparar o adendo 3 para revisão, sem implementar mudança, sem rodar vida nem
simulação nova antes da aprovação dele, preservando o resultado do #420 e sem reutilizar a faixa 64xxx. As fontes são a proposta aprovada
(`docs/PROPOSTA_DIAGNOSTICO_DIGIBRAIN_MODULAR.md`), o resultado do diagnóstico (`docs/RESULTADO_V2_DIGIBRAIN_MODULAR_DIAGNOSTICO.md`),
os artefatos `artifacts_v2_digibrain_prototipo/avaliacao/` e `artifacts_v2_digibrain_prototipo/diagnostico/`, e a leitura do código
citada linha a linha. Toda conta de alcance abaixo sai das constantes do motor, não de vidas.

**A revisão 2 (2026-10-26)** atende aos pedidos do Matheus sobre a revisão 1, sem aprovar o adendo nem autorizar a implementação:
- **DX-1:** o "achou" fica ligado à comida no lugar visitado; uma refeição em outro lugar não conta (A3.1);
- **DX-2:** a medida por episódio é a primária recomendada pelo Matheus, com a por ração como secundária obrigatória. O episódio foi
  redefinido: um por fome, sem episódio novo a cada janela vencida, sem sobreposição, e uma refeição fecha no máximo um episódio. Os
  limiares ficam explícitos, com a justificativa para a nova unidade (A3.3);
- **revisão 3 (2026-10-26), pedida pelo Matheus:** as saídas do denominador saíram. "Saciado por outra comida" é falha e fica no
  denominador. A oferta que apodrece ou some pela idade é condição normal do mundo e não exclui nada. No cenário da avaliação não há
  causa externa ao pet que invalide a oferta, nem outra comida, e o T-CENARIO-1 confirma (A3.3, A3.7 e A3.8);
- **W(d):** a fórmula com o `max(0, …)`, a convenção da decisão da posta, o T-ALCANCE-1 para validá-la e a aplicação igual a todos os
  braços e lugares (A3.2);
- **DX-4:** o crédito da refeição chega à busca pelo cheiro pela opção composta, com testes para a busca que come e a que não come (A3.4);
- **DX-5:** a classificação das ações é definida pela regra de recompensa do modelo, não pelos resultados (A3.5);
- **os testes e os critérios de parada** refletem essas definições (A3.7 e A3.8).

### A3.0 O que não muda

- **O resultado do #420 fica como está:** o G-MVP falhou (0,485), o G-ABLA-MEM e o G-ABLA-P1 passaram, o G-ABLA-PERS ficou inconclusivo
  por premissa, o G-ABLA-P2 saiu ao contrário, nenhum G-MOD passou. Nenhum artefato da `avaliacao/` é refeito, e nenhuma medida nova
  (nem a W(d), nem o episódio, nem a DX-1, nem a DX-5) é aplicada a ele.
- **A faixa 64101…64505 está usada e não volta.** Nada deste adendo lê ou rejoga as vidas dela.
- **O motor, o corpo, o mundo, o `engine.py`, o A e a v12 não mudam.** As mudanças de mecanismo (DX-3 e DX-4) ficam no pacote
  `digilab/digibrain/`, atrás de subchaves desligadas, com o G2 antes.
- **O G-ABLA-P2 e o índice "ganhou, fica" de hoje continuam como estão,** inclusive na reavaliação.
- **A DX-6 (o crédito pela última consequência) e a DX-7 (o limiar do sono, `lambda_sono`) não entram nesta etapa.**

### A3.1 DX-1: a correção da medida `visitas_vazias`

- **O defeito:** a medida conta como vazia toda visita cuja própria decisão não come
  (`experiments/run_v2_digibrain_prototipo.py:372`). A visita é a decisão de explorar até o lugar lembrado; o comer, quando há, costuma vir
  numa decisão seguinte. Por isso as 32,2 visitas por vida do M3 da avaliação saíram todas vazias (`diagnostico/avaliacao.json`, 1.6).
- **A medida antiga fica, com o nome `visitas_vazias_v1`,** calculada como hoje, em toda run nova, ao lado da corrigida.
- **A definição corrigida (PROPOSTA), `visitas_vazias`:**
  - **a visita:** uma opção que começa com a unidade `explorar/ponto` e termina com `chegou` no ponto P, na decisão k;
  - **o lugar visitado:** o disco de raio R_lugar = 60 + 16 = 76 subunidades em torno de P. É o que o pet alcança e pega a partir de P
    numa decisão, pela regra do motor (o passo de uma decisão mais o raio de pegar, A3.2). O raio não sai de vida nenhuma;
  - **"achou":** a visita achou se, na decisão k ou na k + 1, o pet consome uma comida que, no tick da chegada, estava madura no chão
    dentro do lugar visitado. O consumo na própria chegada (o ramo "achou" do explorar, `mundo.py:1506-1509`, que só come a até 16
    subunidades do pet em P) já cumpre isso;
  - **"a comida que motivou a chegada":** o alvo da visita é um lugar, não uma comida (a memória guarda o ponto de um consumo antigo,
    `adapt.py:292-296`). A única comida que pode ter motivado a chegada é a que está no lugar. Por isso as duas leituras do pedido do
    Matheus dão a mesma condição: a comida dentro do lugar visitado;
  - **não conta:** uma refeição na decisão k ou k + 1 de comida fora do lugar visitado (outra comida vista no caminho, uma ração posta em
    outro lugar), nem uma refeição depois da k + 1. A visita fica vazia;
  - **o que a medida lê:** as posições das comidas no tick da chegada e os consumos, do motor (`deixadas`, `consumos_mundo`), no
    orquestrador; o cérebro não muda.
- **O que muda no código:** só a medida, em `digilab/metrics.py` (as métricas existem uma vez só), e a chamada no orquestrador. A
  codificação do episódio na memória (`adapt.py`, o ramo `nao_havia`) é comportamento e não muda.
- **O resultado registrado fica intacto:** o `medidas.json` da avaliação continua com a medida antiga; o RESULTADO do #420 ganha só uma
  nota apontando para este adendo.

### A3.2 A janela da cadeia e o alcance pela regra do motor (pré-requisito da DX-2, da DX-3 e da DX-4)

**As constantes** (`digilab/config.py`, `Config` e `ConfigMundo`):

| o quê | valor | linha |
|---|---|---|
| o intervalo entre decisões | 15 ticks | `config.py:55` |
| a velocidade | 4 subunidades por tick, logo 60 por decisão (3,75 células) | `config.py:1744` |
| a célula | 16 subunidades | `config.py:1742` |
| o raio de pegar | 1 célula (16 subunidades) | `config.py:1746` |
| o raio da visão | 6 células | `config.py:1748` |
| o raio do cheiro | 24 células | `config.py:1752` |
| o passo do alvo `cheiro` | 8 células na direção do cheiro | `config.py:1755` |
| o "longe" | sorteado a 20 a 30 células do pet, na posta, cortado ao mapa | `config.py:1785-1786`; `mundo.py:1957-1970` |

**A regra do movimento** (`mundo.py:1462-1507`): numa decisão com alvo, o pet anda até 60 subunidades na direção do alvo (`passo_ate`),
e come se termina a até 16 subunidades da comida, na mesma decisão. Andar só acontece nas decisões de comer, explorar e brincar; dormir,
ocioso, chamar a atenção e emburrar não andam.

**O mínimo de decisões andando,** em linha reta e sem desvio, com d em subunidades:

  **n_min(d) = max(0, ⌈(d − raio_de_pegar) / passo_por_decisão⌉)**, com raio_de_pegar = 16 e passo_por_decisão = 60.

O `max(0, …)` cobre a comida já ao alcance (d ≤ 16): n_min = 0, e o pet a pega sem andar.

| distância | subunidades | n_min |
|---|---|---|
| ao alcance (até 1 célula) | ≤ 16 | 0 |
| 6 células (o raio da visão) | 96 | 2 |
| 20 células (o mínimo do longe) | 320 | 6 |
| 24 células (o raio do cheiro) | 384 | 7 |
| 30 células (o máximo do longe) | 480 | 8 |

**A convenção da janela (a decisão da posta conta):**
- **k₀** é a primeira decisão do pet no tick da posta ou depois dele: a decisão k₀ = ⌈t₀ / 15⌉ (`run_v2_digibrain_prototipo.py:315-319`).
  Pelo log, a posta cai no tick de uma decisão, e o `deixar_comida` vem antes do `avanco` do mesmo tick; então k₀ é a decisão do próprio
  tick da posta, e o pet já decide com a ração no chão.
- **A janela de W decisões** são as decisões k₀, k₀ + 1, …, k₀ + W: **a da posta conta, e anda**, e W conta as decisões depois dela.
  São W + 1 decisões com deslocamento possível.
- **É a convenção da medida de hoje:** o `cadeia_comida_corpo` aceita o consumo em t₀ ≤ t ≤ t₀ + 120 (`metrics.py:2070`), as decisões k₀
  a k₀ + 8 quando t₀ cai no tick de uma decisão. O diagnóstico (#422) descreveu a janela como "8 decisões"; a contagem acima, 9 com a
  da posta, é leitura de código, e o **T-ALCANCE-1** a valida antes de qualquer vida (A3.7).
- **Com essa convenção,** um pet que anda reto desde a decisão da posta pega a ração na decisão k₀ + n_min(d₀) − 1 (para n_min ≥ 1) ou
  na k₀ (para n_min = 0). O T-ALCANCE-1 confere exatamente isso.

**A conclusão para a janela de hoje (W = 8): suficiente só no limite, e não na prática.**
- **No limite, sim:** um pet acordado que anda reto para a ração em 6 a 8 das 9 decisões a alcança.
- **Na prática, não:**
  - **o sono:** no replay do piloto, dormir ocupa 0,525 da janela nas rações que não fecham e 0,510 nas que fecham (M3, todas as
    células; `diagnostico/replay_piloto.json`). Com 4 decisões de sono na janela, sobram no máximo 5 andando: 18,75 células mais o raio
    de pegar, menos que as 20 células do mínimo do longe. **Nenhuma ração longe fecha com 4 decisões de sono na janela, qualquer que
    seja o cérebro;**
  - **a percepção:** antes de a ração entrar na visão (6 células), o único alvo dirigido é o `cheiro`, que aponta para o cheiro mais forte
    (pode ser de uma fruta), e além de 24 células a ração não tem cheiro. Um quarto das rações longe que não fecharam estava além de 24
    células na posta (`replay_piloto.json`, M3, longe);
  - **o que aconteceu:** as rações longe que fecharam estavam a 4,7 células na mediana, já perto do pet; as que não fecharam, a 20,5.
- **A janela fixa mistura duas coisas:** a latência do cérebro (perceber, decidir, ir) e o tempo de viagem, que é física.

**A regra de medição PROPOSTA, W(d):**
- **W(d₀) = 8 + n_min(d₀) decisões depois da decisão k₀**, com d₀ a distância do pet à ração (ou à ração mais próxima, no episódio) na
  decisão k₀, lida do estado do motor (não do cérebro). As 8 são a folga da PPM-4, sem mudança; o n_min é o tempo mínimo de viagem pela
  regra do motor, e não depende de vida nenhuma.
- **O que ela faz:** no longe, W vai a 14 a 16; com a comida ao alcance, fica em 8. A latência do cérebro tem a mesma folga em todo lugar.
- **Aplicação igual:** a mesma W(d) vale para **todos os braços** (o A11, os modulares e os três novos de A3.4) e **todos os lugares**
  (comedouro, perto, longe), em toda medida de cadeia nova deste adendo. Ela só depende de d₀ e das constantes do motor, nunca do braço.
- **O #420 não muda:** a W(d) não é aplicada às vidas da 64xxx; o G-MVP de hoje, com a janela fixa de 120 ticks, continua calculado
  como está nas runs novas, como secundária.
- **As alternativas, e por que não:**
  - **contar só as decisões acordado:** desculparia o sono com fome e com comida, que é parte da cadeia que o gate testa; e o diagnóstico
    mostra que o sono não separa as rações que fecham das que não fecham;
  - **uma janela fixa maior para todos:** um número sem regra, que infla o fechamento no perto e no comedouro;
  - **tirar as rações além do cheiro:** a memória (M-MEM) pode levar o pet a um lugar sem cheiro, e tirá-las esconderia isso. Em vez
    disso, o fechamento sai **estratificado** pela distância d₀ (até 24 células e além), como leitura descritiva.

### A3.3 DX-2: a medida primária da próxima avaliação

**A recomendação, agora também do Matheus:** a medida por episódio como primária; a medida pré-registrada por ração como secundária
obrigatória; o #420 sem alteração. A decisão final vem com a aprovação do adendo.

**As duas medidas.**

| | **(a) o G-MVP pré-registrado, por ração (secundária obrigatória)** | **(b) o G-MVP por episódio de fome (primária recomendada)** |
|---|---|---|
| a unidade | cada ração posta pelo dono com o pet com fome | cada episódio de fome com oferta (abaixo) |
| fecha se | **esta** ração é comida em t₀ ≤ t ≤ t₀ + 120 e a falta da fome cai | uma ração do dono é comida na janela W(d₀) e a falta da fome cai |
| a vida com a cadeia | a taxa de fechamento ≥ 0,5 | a taxa de fechamento dos episódios ≥ 0,5 |
| o gate | o limite inferior do IC95 da fração de vidas do M3 com a cadeia (a média das células por unidade) ≥ 0,8 | o mesmo |
| o denominador | todas as rações elegíveis | **todos os episódios**, sem exclusão: todo episódio que não fecha é falha (A3.3, "os desfechos") |
| a premissa | G-ELEGIVEL: ≥ 80 % das vidas do M3 com 3 rações elegíveis ou mais | G-ELEGIVEL-EP: ≥ 80 % das vidas do M3 com 3 episódios ou mais |

**O episódio de fome, redefinido (PROPOSTO, em `digilab/metrics.py`).** Em cada decisão k, duas condições, lidas do estado do motor:
- **F(k), a fome:** a fome (o estado, 0 a 1, o mesmo `_escala01("fome")` de hoje) abaixo de 0,5;
- **O(k), a oferta:** ao menos uma ração posta pelo dono, madura e não comida, no chão.

**A fome contínua** é um trecho máximo de decisões seguidas com F(k). **Cada fome contínua tem no máximo um episódio.**

**Os eventos:**
- **Início:** a primeira decisão k_i de uma fome contínua em que O(k_i) vale. Isso cobre os dois casos: a fome começa com ração no chão,
  ou o dono põe a primeira ração durante uma fome que estava sem oferta. Guarda d₀ = a distância do pet à ração mais próxima em k_i.
- **Encerramento, o primeiro que acontecer:**
  - **"fechou":** numa decisão k em k_i ≤ k ≤ k_i + W(d₀), o pet come uma ração do dono (madura ou podre, como na medida de hoje) e a
    falta da fome cai na decisão do consumo (a condição de hoje). É o **sucesso**;
  - **"não fechou":** qualquer outro fim. É **falha da cadeia da ração** e fica no denominador. O motivo vai ao registro do episódio, só
    como leitura descritiva, e nunca o tira da conta:
    - **"janela vencida":** a decisão k_i + W(d₀) passa sem o "fechou";
    - **"saciado por outra comida":** a fome contínua acaba (F deixa de valer) dentro da janela sem consumo de ração do dono. O episódio
      acaba ali, como falha;
    - **a oferta muda dentro da janela** (a ração apodrece ou some pela idade): não encerra o episódio. A janela segue até o "fechou"
      ou até vencer, e a ração podre ainda pode fechar.

**Os desfechos, sem exclusão do denominador (a regra pedida pelo Matheus em 2026-10-26):**
- **Comer outra comida no lugar da ração não facilita o G-MVP:** "saciado por outra comida" é falha e conta no denominador.
- **Nenhum episódio sai do denominador por perda da oferta.** Uma exclusão só seria possível com a oferta invalidada por uma causa
  **externa ao pet**, definida antes da avaliação. No cenário da avaliação essa causa não existe, então **não há exclusão nenhuma**:
  - **o cenário** (o orquestrador, `run_v2_digibrain_prototipo.py:1-5`): o layout do produto **sem árvores, só a ração do dono**, o
    **pet sozinho**, os quatro donos só com o cuidado; o `alimentar` do dono vira a ração no chão (`DonoComLugar`, `mundo.py:1942`);
  - **a ração sai do chão de dois modos só:** o pet a come (é a cadeia: sucesso ou falha pela regra acima), ou ela some pela idade,
    depois de 1 440 min madura e 720 min podre (`mundo.py:826-834` e `850-854`; `config.py:1776-1777`). A idade é **uma condição normal
    do mundo**, não uma causa externa: conta como falha se a janela acaba sem o "fechou";
  - **não há** outro pet que coma a ração, nem gesto do dono que a tire do chão;
  - **outra comida é impossível no cenário:** sem árvores não cai fruta, e os donos não oferecem fruta (o `oferecer_fruta` é só do
    `MotorFrutas`, fora desta composição; `events.py:50-54`). No replay do piloto, as únicas comidas consumidas foram a ração e a ração
    podre (`diagnostico/replay_piloto.json`, `comeu_por_escolha`);
  - **a fome só sobe comendo:** a digestão do cenário é a taxa C, tudo no mesmo tick (DECIDIDO, CD-3; `corpo.py:191`), a digestão lenta
    está desligada, e com o mundo o comer só dá fome com comida (MF-2). Então "saciado por outra comida" não pode acontecer aqui.
- **Os testes confirmam o cenário** (T-CENARIO-1 e T-EPISODIO-4, A3.7): se algum desses casos ocorrer numa vida de teste do cenário, a
  implementação para e volta ao Matheus (A3.8). A regra de falha vale de todo modo; nenhuma exclusão fica aberta para mudar o gate.
- **Se um cenário futuro tiver frutas, outro pet ou um gesto que tire a ração,** a regra deste adendo continua: comer outra comida é
  falha. Uma exclusão por causa externa precisaria de um adendo novo, antes da avaliação desse cenário.

**Sem episódios repetidos nem sobrepostos:**
- **Depois de "janela vencida",** nenhum episódio novo abre enquanto a mesma fome contínua dura, mesmo que a oferta continue e mesmo que
  o dono ponha mais ração. Um episódio novo só abre numa **nova fome contínua**: depois de F deixar de valer em ao menos uma decisão.
- **Depois de "fechou",** o mesmo: se o pet continua com fome depois de comer (uma ração não basta), isso é a mesma fome contínua, e não
  abre episódio novo.
- **Há no máximo um episódio aberto por vez,** e os episódios de uma vida são disjuntos no tempo.

**Uma refeição só conta uma vez:**
- uma refeição de ração fecha **no máximo um episódio**, o aberto na decisão dela;
- uma refeição fora de episódio aberto (fora da janela, ou numa fome contínua cujo episódio já acabou, ou sem fome) **não conta** para a
  taxa; ela sai contada à parte (as refeições fora de episódio e a latência das que fecham depois da janela, descritivas);
- duas refeições na mesma janela fecham um episódio só (a primeira); a segunda é uma refeição fora de episódio.

**Os limiares, explícitos (PROPOSTOS; os mesmos números da PPM-4), e por que valem para a nova unidade:**
- **o corte da fome, 0,5:** define "com fome" pelo estado do pet, não pela unidade de análise; é o mesmo corte que tornava a ração
  elegível, então a medida (a) e a (b) partem do mesmo estado de fome;
- **a taxa por vida, 0,5:** a vida "tem a cadeia" se resolve pela ração **a maioria** das fomes com oferta. Na unidade nova, cada episódio
  é uma oportunidade distinta (uma fome contínua), sem repetição pela oferta abundante; a maioria simples é o mesmo critério da PPM-4 e
  agora conta oportunidades independentes, não rações repetidas;
- **o limiar do gate, 0,8 no limite inferior do IC95:** é sobre a fração de **vidas**, e a unidade de vida não muda; o bootstrap é o
  mesmo (10 000 reamostragens, semente 4242, a média das células por unidade);
- **o denominador, todos os episódios:** a taxa por vida é fechados / episódios, com todo episódio que não fecha contado como falha. Na
  unidade nova, isso é o que a ração elegível era na medida (a): toda oportunidade conta;
- **o mínimo de 3 episódios por vida e os 80 % da premissa:** os mesmos da G-ELEGIVEL. Com um episódio por fome contínua, as vidas terão
  menos episódios que rações elegíveis; o mínimo de 3 continua sendo o menor número com que uma taxa por vida (0, 1/3, 2/3, 1) separa
  "a maioria" de "a minoria". Se menos de 80 % das vidas do M3 tiverem 3 episódios, o G-MVP (b) é **inconclusivo por premissa**, como
  hoje. Quantos episódios as vidas terão não foi calculado (seria simulação nova); o piloto da 65xxx mostra, e o
  adendo 4 traz.

**A validade de cada uma.**
- **(a) por ração:**
  - **a favor:** foi pré-registrada antes de qualquer dado; compara direto com o #420; liga a cadeia à ração que o dono pôs, como o gesto
    do produto;
  - **contra, a oferta abundante:** cada ração conta. No comedouro do atencioso, o pet é o mais bem alimentado das 12 células (6,47
    refeições por dia, privação 0,087) e tem 0 % das vidas com a cadeia, porque o dono põe 109,6 rações elegíveis por vida e o pet já
    comeu outra (`diagnostico/avaliacao.json`, 1.1). No longe do atencioso e do incoerente, são 166 rações elegíveis por vida;
  - **contra, a janela fixa:** ela não cabe a viagem do longe com o sono observado;
  - **o efeito no gate:** no #420, o comedouro do atencioso e o do incoerente ficaram em 0 % por um motivo que nenhum cérebro conserta (o
    pet já saciado). Com essas 2 células em 0 %, a fração por unidade fica em 10/12 = 0,83 no máximo, mesmo com as outras 10 perfeitas,
    e o limite inferior do IC95 ≥ 0,8 fica quase impossível. Como primária, a reavaliação tenderia a falhar por construção.
- **(b) por episódio:**
  - **a favor:** mede a cadeia "com fome e com comida, o pet come e o corpo responde", uma vez por fome; a oferta abundante não multiplica
    o denominador; a viagem entra pela regra do motor;
  - **contra, foi definida depois de ver os dados:** um grau de liberdade a mais. A mitigação: a definição e os limiares ficam fixos antes
    de qualquer vida da 65xxx; os motivos são dois defeitos de validade mostrados nos artefatos do #420, não o valor do gate; os números
    são os da PPM-4; o #420 não muda; (a) sai sempre ao lado;
  - **contra, perde a ração específica:** comer outra ração do dono conta. A ligação com o gesto do jogador fica para o gate do produto,
    que já a testa no jogo (o E2E-COMIDA, seção 5.6);
  - **sem saída do denominador:** todo episódio conta, e todo fim que não é o "fechou" é falha (acima). Os motivos das falhas saem
    contados por braço e célula, só como leitura.

**O custo de errar:**
- **(b) primária e ela estar errada:** um gate que passa por uma medida mais branda; mitigado porque (a) sai sempre ao lado e porque o
  produto ainda exige o G-PAR, o G-CUSTO e o E2E-COMIDA;
- **(a) primária:** a reavaliação gasta a faixa 66xxx num gate que quase não pode passar, e a decisão sobre o produto fica sem informação.

**As leituras descritivas, sem gate:** a medida por ração com a janela W(d) (para separar o efeito da janela do efeito da unidade); o
fechamento estratificado por d₀; os motivos das falhas (janela vencida, saciado por outra comida, a ração apodrecida ou sumida na
janela); as refeições fora de episódio.

### A3.4 DX-3 e DX-4: o cheiro, em duas subchaves separadas

**DX-3, o peso inato do cheiro (subchave `cheiro_inato` da `ConfigDigibrain`, desligada por padrão):**
- **O que muda:** a linha `("cheiro", w)` entra no `w0_tipo` do comer (`config.py:2429`), e o termo inato da unidade `comer/cheiro`
  passa a somar w (`impulso.py:102`). Hoje a unidade `comer/cheiro` fica S/4 abaixo da `comer/racao` com a mesma fome, porque não tem o
  peso do tipo nem a proximidade.
- **O valor de partida (PROPOSTO, SEM FONTE):** w = S/4, o mesmo da ração (o cheiro de comida vale como comida, sem a proximidade). Na
  calibração da 65xxx, ele pode ir a S/8 ou S/2, e o sinal fica.
- **O que não muda:** o cérebro continua lendo só se há cheiro (`ha_cheiro`); a intensidade e a direção não entram (G-SEM-DIRECAO).

**DX-4, a intenção no cheiro (subchave `intencao_cheiro`, desligada por padrão):**
- **O que muda:** a unidade `comer/cheiro` passa a abrir intenção (`estado.py:24`, `TIPOS_INTENCAO`), com a meta "comer uma comida".
  Com a persistência ligada, a intenção soma o termo h = w_pers × C (`estado.py:47-52`), como as outras.
- **Como a intenção acaba, sem ler a distância nem a direção do cheiro** (a proposta dizia "sem a distância do cheiro cair", mas o cérebro
  não lê essa distância, e lê-la quebraria o G-SEM-DIRECAO):
  - **"meta":** o pet come uma comida numa decisão da busca;
  - **"achou":** uma comida entra nos `vistos` (o que o cérebro já lê); a intenção de busca acaba, e o crédito segue pela opção composta
    (abaixo);
  - **"sumiu":** sem cheiro e sem comida vista;
  - **"desistiu":** depois de N_desiste_cheiro decisões sem "meta" nem "achou".
- **O N_desiste_cheiro (PROPOSTO), pela regra da PE-6** (a mesma que deu o `n_desiste` = 3, `config.py:2442`: o raio da visão pelo
  alcance, mais uma decisão): do raio do cheiro ao raio da visão, ⌈(384 − 96) / 60⌉ + 1 = **6 decisões**. Na calibração, 5 a 8.

**O crédito da refeição chega à busca: a opção composta.** Hoje, cada opção guarda a elegibilidade e = z da decisão que a começou, soma o
r_n de cada consequência dela, e é entregue ao P2 quando acaba (`estado.py:63-107`; `plast.py:creditar`). Com a DX-4:
- **No "achou",** a opção da busca **não é entregue**. Ela fica guardada por uma decisão.
- **Se a decisão seguinte escolhe uma unidade `comer/comida`** (uma das comidas vistas), a opção dessa intenção **herda a busca:** a
  mesma elegibilidade e (o z do começo da busca), o mesmo início, e o r já somado na busca. As consequências da ida à comida e da
  refeição somam nesse mesmo r. **A opção composta é entregue ao P2 uma vez só,** quando a intenção na comida acaba ("meta" ao comer,
  ou "trocou", "sumiu", "desistiu" sem comer).
- **Se a decisão seguinte escolhe outra unidade,** a busca é entregue nesse momento, com o r só das decisões dela (a caminhada, sem
  refeição).
- **Na "meta" dentro da própria busca** (o pet come na decisão da busca, com a comida já ao alcance), a busca é entregue com a refeição
  no r, como as outras intenções.
- **O que isso garante:**
  - **a busca que termina em consumo** recebe, na linha do comer e com o z do começo da busca, a consequência da refeição somada ao custo
    da caminhada;
  - **a busca sem consumo** recebe só o r das próprias decisões: o andar custa energia e o comer sem comida não dá fome (MF-2), então
    esse r não tem parte positiva vinda de refeição;
  - **a refeição é creditada uma vez:** a opção da comida que herdou a busca não é entregue separada.
- **Onde fica:** só no M-ESTADO (`digilab/digibrain/estado.py`) e na chamada dele no M-ADAPT (`digilab/digibrain/adapt.py`), que já
  recebe os `vistos` e o `ha_cheiro`. Nada no motor, no corpo, no mundo ou no M-PLAST muda; o `creditar` recebe a opção como hoje.
  **Se a implementação mostrar que precisa de mudança fora do pacote modular, ou de ler a distância ou a direção do cheiro, ela para e
  volta ao Matheus antes de seguir** (A3.8).
- **Uma nota:** a opção composta muda o crédito do P2 nos braços com P2 (M2 e acima). Então o G-DX-INTENCAO mede a intenção inteira:
  a persistência na busca e o crédito composto. A separação das duas partes é descritiva: no M3-sp com a DX-4 (sem persistência, com o
  crédito composto) e no M1 com a DX-4 (com persistência, sem P2).

**Os braços, para separar as duas contribuições (o desenho fatorial):**
- **M3\*** = o M3 com as duas subchaves ligadas. **Todos os braços modulares da reavaliação** (M0, M1, M2, M3-sp, M4, M4-con, M4-emb)
  ligam as duas, para que os contrastes de hoje continuem com o mesmo sentido.
- **Três braços novos:** M3\*−inato (só a `intencao_cheiro`), M3\*−intencao (só o `cheiro_inato`) e M3-420 (as duas desligadas, o M3 do
  #420 com os valores calibrados da 65xxx). Com o M3\*, são as quatro células de um 2 × 2.
- **Os contrastes (família G-DX, secundária, Holm com 2):**
  - **G-DX-INATO:** M3\* − M3\*−inato;
  - **G-DX-INTENCAO:** M3\* − M3\*−intencao;
  - na medida primária decidida em A3.3, nas células do longe (a leitura principal da família) e em todas as células;
  - **a interação** (M3\* − M3\*−inato − M3\*−intencao + M3-420) e os quatro braços lado a lado ficam descritivos.
- **As medidas de mecanismo, por braço e lugar (descritivas):** as decisões ao cheiro por episódio, a fração das rações que entram na visão
  dentro da janela, a menor distância na janela, os fins das buscas (meta, achou, sumiu, desistiu), a fração das buscas "achou" que
  terminam em refeição pela opção composta, e a fração de decisões de sono na janela.
- **A persistência:** o G-ABLA-PERS continua com a premissa G-PESA da persistência.
- **O custo:** 12 braços em vez de 9, um terço a mais de vidas por unidade.

### A3.5 DX-5: o índice do hábito pelas ações com recompensa possível (secundária exploratória)

- **O resultado original do P2 fica:** o G-ABLA-P2 da reavaliação usa o índice de hoje, sem mudança, e o −0,011 do #420 não é revisto
  nem recalculado.
- **A classificação das ações é definida pela regra de recompensa do modelo, não pelos resultados observados.** O r de uma decisão é o
  `sinal_corpo` entre o corpo na decisão e o corpo logo depois do gancho `consequencia_corpo` (`afeto.py:97-107`; `adapt.py:265-266`). O
  gancho vem logo depois dos estímulos da própria ação e antes do tempo e do dono (`motor_corpo.py:30-33` e `341-368`). Então o r só vê o
  estímulo imediato da ação (`policy.py:168-198`, `efeito_da_acao_do_pet`, mais o andar, a comida e a bola do mundo). Nenhum número de
  vida entrou na classificação.
- **O "ganhou, fica" só tem sentido nas ações em que r > 0 e r ≤ 0 são ambos possíveis por essa regra.** Pela leitura do código:

| ação | o estímulo imediato | r > 0 possível? | no índice da DX-5 |
|---|---|---|---|
| comer | a fome, com comida do mapa | sim | **entra** |
| brincar | o humor (e a bola), menos energia | sim | **entra** |
| explorar | o humor (+0,01), menos energia, e a comida achada | sim | **entra** |
| aliviar (só com o banheiro) | a necessidade | sim | **entra**, quando existe |
| dormir | só marca `dormindo`; a energia volta nos ticks, depois do gancho | não, r = 0 sempre | fica fora |
| ocioso | nenhum | não, r = 0 sempre | fica fora |
| chamar a atenção | nenhum; a resposta do dono vem depois | não, r = 0 sempre | fica fora |
| emburrar | o humor (−0,01) | não, r ≤ 0 sempre | fica fora |

- **A diferença para a proposta:** a proposta tirava o comer e o dormir ("sem consumo"). A regra acima tira as ações em que o r não pode
  ser positivo e mantém o comer, que pode. O valor dela no piloto **não foi calculado** (seria simulação nova).
- **Um teste fixa a classificação** (T-HABITO-1, A3.7) pela regra do motor, não por vidas de pesquisa. Se o teste discordar da tabela, a
  tabela muda pelo teste, antes de qualquer vida, e a mudança vai ao registro.
- **Exploratória:** sem gate, sem Holm, sem sinal esperado pré-registrado; sai por ação, por lugar e no total, ao lado do índice de hoje.

### A3.6 O que fica fora desta etapa e a questão aberta

- **DX-6, o crédito pela última consequência:** não. O diagnóstico mostrou opções de uma decisão; a hipótese H-P2b não se sustentou como
  escrita. A opção composta da DX-4 (A3.4) é só a da busca pelo cheiro, não a DX-6.
- **DX-7, o limiar do sono:** não. O sono não separa as rações que fecham das que não fecham (0,510 contra 0,525).
- **Questão aberta, registrada para revisão depois da reavaliação: o retorno zero do dormir.** Dormir dá r = 0 em toda decisão, porque
  a energia volta nos ticks, depois do gancho de consequência, e o r não vê o tempo que passa. O mesmo vale para chamar a atenção (a
  resposta do dono vem depois). Mexer nisso é mexer no momento do gancho, no motor ou no corpo; pelo critério de parada da proposta
  (seção 5), volta ao Matheus. Nenhuma mudança agora.

### A3.7 Os testes, antes de qualquer vida

Todos com as sementes dos testes (101…505) ou sequências sintéticas; nenhum usa as faixas 64xxx, 65xxx ou 66xxx.

| teste | o que confere |
|---|---|
| **G2** | com as subchaves `cheiro_inato` e `intencao_cheiro` desligadas, as 196 vidas do gabarito do protótipo e as do MVP saem byte a byte; o gabarito é o de hoje, já commitado |
| **G2-SEPARADO** | cada subchave ligada sozinha muda só as vidas dos braços que a ligam, e nada fora do pacote `digibrain` e do orquestrador lê a chave (o teste de hoje, estendido) |
| **G1** | o replay refaz cada vida, com as subchaves ligadas |
| **G-MECANISMO, G-SEM-DIRECAO, G-INT, G-RECEPTOR** | os de hoje passam, com as duas subchaves ligadas; o G-SEM-DIRECAO confere pela AST que a DX-4 (inclusive a opção composta) não lê a distância nem a direção do cheiro |
| **T-CADEIA-1** | o oráculo passa com as duas ligadas; se falhar com uma delas, ela volta ao desenho |
| **T-ALCANCE-1** | vidas de teste com uma ração posta a d subunidades (d ≤ 16, 96, 320, 384 e 480) e um pet que anda reto para ela desde a decisão da posta: (i) a decisão k₀ é a do tick da posta e já vê a ração; (ii) o consumo sai na decisão k₀ + n_min(d) − 1 (k₀ se n_min = 0); (iii) a medida de hoje aceita consumos de k₀ a k₀ + 8, e a W(d) de k₀ a k₀ + 8 + n_min(d). Se qualquer um discordar da convenção de A3.2, para e volta ao Matheus antes de fixar a W(d) |
| **T-JANELA-IGUAL** | a W(d) é a mesma função de d₀ e das constantes do motor em todo braço e lugar: o mesmo d₀ dá a mesma W com qualquer braço |
| **T-VISITA-1** | a DX-1 em sequências sintéticas: comer, na chegada ou na decisão seguinte, uma comida que estava dentro do lugar visitado (76 subunidades de P) conta como "achou"; comer na decisão seguinte uma comida fora do lugar visitado conta como vazia; comer depois da k + 1, vazia; a `visitas_vazias_v1` dá o número de hoje |
| **T-EPISODIO-1** | o episódio em sequências sintéticas: abre na primeira decisão de uma fome contínua com oferta; fecha com a primeira refeição de ração na janela; três rações postas e uma comida dão um episódio fechado (a medida (a) dá 1 de 3) |
| **T-EPISODIO-2** | sem repetição: com a mesma fome contínua e a oferta continuando (e com o dono pondo mais ração), a janela vencida não abre episódio novo; depois de "fechou" com a fome continuando, também não; um episódio novo só abre depois de F deixar de valer em ao menos uma decisão; nunca há dois episódios abertos |
| **T-EPISODIO-3** | a refeição conta uma vez: duas refeições na mesma janela fecham um episódio só; uma refeição fora de episódio não entra na taxa e sai contada à parte |
| **T-EPISODIO-4** | sem exclusão: em sequências sintéticas, a fome que acaba por outra comida dentro da janela encerra o episódio como falha e conta no denominador; a ração que apodrece ou some pela idade dentro da janela não encerra o episódio, e a janela vencida conta como falha no denominador; a ração podre comida na janela com a falta caindo fecha; o denominador é sempre o número de episódios |
| **T-CENARIO-1** | o cenário da avaliação, nas vidas de teste do orquestrador (as sementes dos testes, todos os braços e células): (i) toda comida consumida é ração do dono, e nenhuma fruta existe no mundo; (ii) a fome nunca sobe numa decisão sem consumo; (iii) toda ração sai do chão só por consumo do pet ou pela regra da idade; (iv) há um pet só. Se qualquer item falhar, para e volta ao Matheus |
| **T-EPISODIO-5** | a W(d) sai das constantes do motor; uma constante diferente falha alto |
| **T-CHEIRO-1** | a DX-3: a ativação do `comer/cheiro` é a de hoje mais w, só com a subchave |
| **T-PERS-CHEIRO-1** | a DX-4: a intenção abre no `comer/cheiro`; acaba em "meta" ao comer, em "achou" ao ver comida, em "sumiu" sem cheiro e sem comida, em "desistiu" depois de N_desiste_cheiro decisões |
| **T-PERS-CHEIRO-2, a busca que come** | busca, "achou", `comer/comida` na decisão seguinte, consumo: o P2 recebe **uma** opção, com a elegibilidade do começo da busca e o r = a soma das consequências da busca, da ida e da refeição; a opção da comida não é entregue separada; a refeição aparece uma vez no crédito |
| **T-PERS-CHEIRO-3, a busca que não come** | busca que acaba em "desistiu" ou "sumiu", e busca "achou" seguida de outra unidade, ou de `comer/comida` que acaba sem comer: o r entregue é só a soma das consequências das próprias decisões, sem parte vinda de refeição, e não é positivo quando nenhuma decisão da opção consumiu comida |
| **T-HABITO-1** | a classificação da DX-5 (A3.5) pela regra do motor: em estados de teste, dormir, ocioso e chamar a atenção dão r = 0, emburrar r ≤ 0, e comer, brincar e explorar dão r > 0 em algum |
| **o artefato do #420** | o sha256 do `avaliacao/medidas.json` e do `avaliacao/resultado.json` não muda em nenhum commit desta etapa |

### A3.8 Os critérios de parada

- **Na implementação:**
  - qualquer quebra do G2 ou do G1 para tudo, e se conserta antes de seguir;
  - se uma mudança exigir mexer no motor, no corpo, no mundo, no `engine.py` ou no A, para e volta ao Matheus;
  - **se a DX-4, inclusive a opção composta, precisar de mudança fora do pacote `digilab/digibrain/`** (o orquestrador e as medidas à
    parte), **ou de ler a distância ou a direção do cheiro, para e volta ao Matheus antes de implementar;**
  - se o T-PERS-CHEIRO-2 ou o 3 não passarem com o desenho de A3.4, para e volta ao Matheus;
  - se o T-CENARIO-1 mostrar outra comida, fome subindo sem consumo, ração saindo do chão por outra via ou outro pet, para e volta ao
    Matheus. Nenhuma exclusão do denominador é criada para isso;
  - se o T-ALCANCE-1 discordar da convenção de A3.2, para e volta ao Matheus antes de fixar a W(d);
  - se o T-HABITO-1 discordar da tabela de A3.5, a tabela muda pelo teste e vai ao registro antes de qualquer vida;
  - se o T-CADEIA-1 falhar com uma subchave ligada, ela volta ao desenho.
- **Na calibração (65101 e 65202):** só no M3\*; só o peso do cheiro (S/8 a S/2), o N_desiste_cheiro (5 a 8) e os valores da lista da
  seção 6.1; no máximo três rodadas; o critério de fechamento da seção 6.1, com a medida primária decidida em A3.3 no lugar da taxa de
  hoje; se não fechar, fica a melhor rodada, registrada como não fechada.
- **No piloto (65303, 65404 e 65505):** os 12 braços (os 9 de hoje com as subchaves ligadas, mais os três de A3.4), K = 2, sem leitura de
  gate; o adendo 4 traz o efeito, as premissas (inclusive quantos episódios as vidas têm), os motivos das falhas, o g_apr do
  M4-con, o K e o custo, e vai ao Matheus antes da reavaliação.
- **Na reavaliação (66101 a 66505):** roda uma vez, com as regras deste adendo e do adendo 4. Se o G-MVP primário falhar de novo, o
  resultado é registrado e o protótipo da etapa 1 para aí; o próximo passo vai ao Matheus, sem rodada de conserto automática.

### A3.9 As faixas (reservadas em `experiments/bancada/faixas.py` pelo #421; nenhuma vida delas rodou)

| faixa | uso | bases |
|---|---|---|
| **65101…65505** | a calibração do conserto e o piloto | calibração 65101 e 65202 (K = 2); piloto 65303, 65404 e 65505 (K = 2) |
| **66101…66505** | a reavaliação, uma vez | 66101, 66202, 66303, 66404 e 66505 (K do adendo 4) |
| 64101…64505 | a avaliação do #420 | **usada; não volta** |

### A3.10 Para o Matheus decidir, na revisão 2

1. **A definição do episódio** (A3.3): uma por fome contínua; o sucesso é o "fechou"; todo outro fim é falha e fica no denominador,
   sem exclusão; a oferta que apodrece ou some pela idade não encerra o episódio.
2. **A medida primária:** (b) por episódio, com (a) por ração como secundária obrigatória, como o Matheus recomendou.
3. **A convenção da janela e a W(d)** (A3.2): a decisão da posta conta e anda; W(d₀) = 8 + n_min(d₀) depois dela, igual em todo braço
   e lugar.
4. **O lugar visitado da DX-1** (A3.1): R_lugar = 76 subunidades, o alcance de uma decisão mais o raio de pegar.
5. **A opção composta da DX-4** (A3.4), e a regra de fim com "achou" e N_desiste_cheiro = 6.
6. **O adendo inteiro,** para que a implementação comece. Nada é implementado nem executado antes disso.
