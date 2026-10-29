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

## Adendo 3: o conserto depois do diagnóstico (2026-10-26, Gerente; revisão 3, APROVADO pelo Matheus em 2026-10-26)

**Status: APROVADO pelo Matheus em 2026-10-26, na revisão 3 ("Aprovo o adendo 3 e autorizo o merge do #423"). As decisões de
A3.10 valem como DECIDIDAS; os números novos (o peso do cheiro, o N_desiste_cheiro, o R_lugar) seguem PROPOSTOS até a calibração. Nada
implementado nem executado no momento da aprovação; nenhuma vida das faixas 65xxx e 66xxx rodou.** O adendo seguiu o pedido do Matheus de
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
  - **"fechou":** numa decisão k em k_i ≤ k ≤ k_i + W(d₀), o pet come uma ração do dono **que reduz a fome**: a falta da fome cai na
    decisão do consumo (a condição de hoje). É o **sucesso**. **Comer ração podre não fecha** (correção de 2026-10-26, abaixo);
  - **"não fechou":** qualquer outro fim. É **falha da cadeia da ração** e fica no denominador. O motivo vai ao registro do episódio, só
    como leitura descritiva, e nunca o tira da conta:
    - **"janela vencida":** a decisão k_i + W(d₀) passa sem o "fechou";
    - **"saciado por outra comida":** a fome contínua acaba (F deixa de valer) dentro da janela sem consumo de ração do dono. O episódio
      acaba ali, como falha;
    - **a oferta muda dentro da janela** (a ração apodrece ou some pela idade): não encerra o episódio, que fica no denominador. A
      janela segue até o "fechou" ou até vencer. Se até o fim da janela o pet não comer nenhuma ração que efetivamente reduza a fome, o
      episódio é **falha**, mesmo que tenha comido ração podre.

**Correção de 2026-10-26, a ração podre (pedida pelo Matheus depois da aprovação; a regra do gate não muda de sentido):**
- **No código, comer ração podre não alimenta:** só baixa o humor em 0,10, e a fome fica igual (`digilab/mundo.py:1431-1439`). Só a ração
  madura soma o ganho de alimentar.
- **Por isso o consumo de ração podre não fecha o episódio:** o sucesso exige a redução da fome. A versão aprovada dizia que "a ração
  podre ainda pode fechar"; isso estava errado e foi corrigido aqui.
- **Comer ração podre na janela** não encerra o episódio nem o tira do denominador; a janela segue, e o episódio só fecha com uma ração
  que reduza a fome.
- **O resultado do #420 não muda,** e a medida por ração de hoje (a secundária) também não: ela já exigia a falta caindo.

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
- **A frustração nos fins da busca (DECIDIDO pelo Matheus, 2026-10-26, depois do #425 e antes da primeira vida da 65xxx):** o
  "achou" **não sobe o F**. Nas palavras dele: "Altere a regra para que o resultado 'achou' não aumente a frustração." O "achou"
  continua sendo um fim sem a meta, com o motivo "achou", a contagem em `fins` e a opção composta como estão. O "sumiu", o "desistiu"
  e o "trocou" continuam subindo o F. Só com a subchave `intencao_cheiro` ligada; desligada, nada muda.
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
| **T-EPISODIO-4** | sem exclusão: em sequências sintéticas, a fome que acaba por outra comida dentro da janela encerra o episódio como falha e conta no denominador; a ração que apodrece ou some pela idade dentro da janela não encerra o episódio, e a janela vencida conta como falha no denominador; **a ração podre comida na janela não fecha** (a falta da fome não cai), não encerra o episódio e, sem outra ração que reduza a fome até o fim da janela, o episódio é falha no denominador; uma ração madura comida depois da podre, ainda na janela, fecha; o denominador é sempre o número de episódios |
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

### A3.10 As decisões (DECIDIDAS pelo Matheus em 2026-10-26, com a aprovação do adendo na revisão 3)

1. **A definição do episódio** (A3.3): uma por fome contínua; o sucesso é o "fechou"; todo outro fim é falha e fica no denominador,
   sem exclusão; a oferta que apodrece ou some pela idade não encerra o episódio; **comer ração podre não fecha** (correção de
   2026-10-26).
2. **A medida primária:** (b) por episódio, com (a) por ração como secundária obrigatória, como o Matheus recomendou.
3. **A convenção da janela e a W(d)** (A3.2): a decisão da posta conta e anda; W(d₀) = 8 + n_min(d₀) depois dela, igual em todo braço
   e lugar.
4. **O lugar visitado da DX-1** (A3.1): R_lugar = 76 subunidades, o alcance de uma decisão mais o raio de pegar.
5. **A opção composta da DX-4** (A3.4), e a regra de fim com "achou" e N_desiste_cheiro = 6.
6. **O adendo inteiro,** para que a implementação comece. **APROVADO.** A implementação segue a ordem de A3.7 e A3.8 e para antes de
   qualquer vida da 65xxx: a calibração e o piloto voltam ao Matheus antes de rodar.

### A3.11 A calibração do conserto (65101 e 65202): o registro de cada rodada, antes da primeira vida dela (worker D, Claude Code, Opus 5.5)

**A autorização do Matheus (2026-10-26, pelo Gerente):** "Depois que o PR for integrado e o M3 estiver completo, calibrem nas bases
65101 e 65202, começando com peso do cheiro S/4 e limite de 6 decisões de busca, com no máximo três rodadas. Antes de cada rodada,
registre a configuração e os critérios de avaliação. Não ultrapasse três rodadas." O PR é o #426 (o "achou" sem frustração), na `main` em
`7e34fab`.

**O que vale para as três rodadas:**
- **Escopo:** só o M3\* (o M3 com as subchaves `cheiro_inato` e `intencao_cheiro` ligadas, e o "achou" sem F do #426). As bases são 65101
  e 65202, com K = 2, 14 dias, 16 interações por dia e as 12 células: **48 vidas por rodada**.
  - Pelo `experiments/run_v2_digibrain_prototipo.py`, com a config `experiments/configs/v2_digibrain_prototipo/calibracao_conserto.json`
    (o campo `rodada`) e 8 processos.
  - Nenhum outro braço, nenhuma outra base, nenhum piloto, nenhuma reavaliação.
- **O que pode mudar entre as rodadas (A3.8):**
  - o peso do cheiro `w0_tipo_cheiro`, de S/8 a S/2;
  - o `n_desiste_cheiro`, de 5 a 8;
  - os valores da lista da seção 6.1 (a magnitude dos W⁰ com os sinais da tabela 4.5, as curvas a_r, b_r e λ_r, os τ, os η, o `w_mem`, o
    `w_pers`, o `N_desiste` pela regra da PE-6, o `H_max` e o g₀).
  - Cada mudança é justificada pelo resultado da rodada anterior e registrada aqui antes da primeira vida da rodada.
  - Nenhuma equação, subchave nem número do motor, do corpo ou do mundo muda.
- **Os critérios de fechamento, nesta ordem** (a seção 6.1, com a medida primária de A3.3 no lugar da taxa de hoje; o
  `analisar_calibracao(..., conserto=True)` do orquestrador):
  1. o T-CADEIA-1 passa com os valores da rodada e as duas subchaves (`tests/test_digibrain_vidas.py` e o T-CADEIA-1 de
     `tests/test_digibrain_conserto.py`), conferido antes da run;
  2. **a taxa de fechamento por episódio de fome do M3\*** (o `episodios_fome`, A3.3: os episódios que fecharam sobre todos os
     episódios, sem exclusão, com a W(d) e a regra da ração podre do #424), **na mediana das 48 vidas, ≥ 0,5**;
  3. nenhum H no teto: o `pesos_no_teto` = 0 em toda vida (o máximo das 48);
  4. a G-PESA de cada módulo do M3\* (incentivo, hábito, memória e persistência), a média das 48 vidas, com a fração ≥ 0,01.
  - **Fecha** se os quatro passam.
- **Descritivos, sem critério:** os do `descritivos_conserto` (os fins das buscas, as decisões ao cheiro, a fração das rações na visão e o
  sono na janela) e a taxa por ração com a W(d), lidos para justificar a rodada seguinte.
- **A melhor rodada,** se nenhuma fechar: na ordem dos critérios, primeiro a que passa o T-CADEIA-1, depois a de maior mediana do
  fechamento por episódio. Ela fica registrada como não fechada, e a faixa que não fecha não bloqueia (seção 6.1).
- **Os artefatos:** `artifacts_v2_digibrain_prototipo/conserto/calibracao/rodada_<n>/`:
  - o `meta.json` (os valores, o commit, a config com o sha e as sementes);
  - o `medidas.json` (as 48 vidas);
  - o `resultado.json` (os critérios).
  - As vidas ficam fora do git.

**Rodada 1 (registrada antes da primeira vida):**
- **Os valores:** os de `digilab/config.py` em `7e34fab`, sem mudança. O `w0_tipo_cheiro` = S/4 = 256 e o `n_desiste_cheiro` = 6, o
  pedido pelo Matheus. O resto é o congelado do adendo 1 (por exemplo `eta_h` = S/128, `w_pers` = 2S, `tau_c` = 30, `n_desiste` = 3), com
  S = 1024.
- **Os sha256:**
  - `digilab/config.py` = `6ae53605114aa7e3186b1bf8ed5ecd7d055438e0d320636a7a33fe3d5da8b97f`;
  - `digilab/engine.py` = `48ba51ce6426eb98a726c05e07f3a57992ae0f328f517740ec36f1c3db153630` (o congelado);
  - `digilab/metrics.py` = `9e5218a75464567315778c83fa3da8e3e6e61e39decb67c65d64e308be75449f`;
  - a config `calibracao_conserto.json` (`rodada` = 1) = `25521336430a1fc76b98bfa8d538fbd69068212e7bd45c6902ba4b0c7b85337d`.
- **O commit:** este registro é o commit da run. O `meta.json` grava o `git_head` e se a árvore estava limpa (`git_limpo`), e a run roda com a árvore limpa.
- **Os critérios:** os quatro acima, sem mudança.

**Rodada 1, o resultado** (`artifacts_v2_digibrain_prototipo/conserto/calibracao/rodada_1/`; a run no commit `38e5015`, com a árvore
limpa e o sha da config igual ao registrado; 48 vidas, 3 min com 8 processos). **Não fecha:**

| critério | rodada 1 |
|---|---|
| T-CADEIA-1 (as duas subchaves) | passa |
| o fechamento por episódio do M3\*, a mediana das vidas (≥ 0,5) | **0,8209** |
| `pesos_no_teto` (o máximo; = 0) | **0** |
| G-PESA, o incentivo (≥ 0,01) | 0,0086 |
| G-PESA, o hábito | **0,1572** |
| G-PESA, a memória | **0,1202** |
| G-PESA, a persistência | 0,0022 |

- **O que o diagnóstico mostra** (o `diagnostico.json` da rodada, de `experiments/diagnostico_calibracao_conserto_digibrain.py`, que
  rejoga as 48 vidas do disco com os valores da rodada e confere que as medidas refeitas são as gravadas):
  - **o incentivo é empurrado pelo hábito ao longo da vida.** Na unidade escolhida, o termo do hábito sobe de 29 para 127 e depois para
    234 nos três terços da vida; o do incentivo fica em 12 a 14 (o incentivo da ração antes da proximidade tem mediana 159, e 20% das
    17 010 amostras batem no G_max). A influência do incentivo por dia cai de 0,026 (dia 4) para 0,005 (dia 14), e a G-PESA lê os dias
    8 a 14;
  - **a persistência só pode decidir em 3,3% das decisões,** as que têm uma intenção em curso (explorar/ponto 1 381, comer/cheiro 611,
    comer/comida 151 e brincar/bola 9, de 64 512 decisões). Na unidade escolhida o termo dela fica em 3 a 7;
  - **o cheiro:** a busca acaba quase sempre em "achou" (727 de 1 297 fins), "trocou" (546) ou "sumiu" (24); nenhuma "desistiu" com 6.
    O fechamento por episódio já passa com folga (0,82), então o peso do cheiro e o N_desiste_cheiro não mudam.

**Rodada 2 (registrada antes da primeira vida):**
- **O que muda e por quê** (só valores da lista da seção 6.1; o peso do cheiro S/4 e o N_desiste_cheiro 6 ficam):
  - **`eta_h` (o passo do P2): S/128 → S/256 (8 → 4).** O hábito cresce pela metade e deixa ao incentivo mais decisões na janela dos
    dias 8 a 14, onde a influência dele caiu abaixo de 0,01. A G-PESA do hábito (0,157) tem folga para cair;
  - **`w_pers`: 2S → 4S (2 048 → 4 096).** Na segunda decisão de uma intenção, h = mul(4S, 512) = 2 048 em vez de 1 024. A fração das
    decisões com intenção não muda (é estrutural), mas a persistência passa a decidir mais vezes nelas. Foi a mesma alavanca da
    rodada 2 do adendo 1 (S/2 → 2S levou a persistência de 0,0002 a 0,0016).
- **Como os valores entram:** pelo campo `inatos` da config (`{"w_pers": 4096, "eta_h": 4}`). O orquestrador ganhou o
  `inatos_da_config` (`FAIXAS_INATOS_CONSERTO`: só na calibração do conserto, só nos campos e nas faixas de A3.8; fora disso, falha alto).
  O `digilab/config.py` não muda na calibração: os padrões, as vidas dos outros braços e o gabarito G2 ficam os de hoje. O `meta.json`
  grava os valores usados, e o diagnóstico e o replay os leem de lá.
- **Os critérios:** os quatro de A3.11, sem mudança.
- **Os valores da rodada:** `w_pers` = 4 096 e `eta_h` = 4. O resto é o de `digilab/config.py`, com o mesmo sha256 da rodada 1
  (`6ae53605114aa7e3186b1bf8ed5ecd7d055438e0d320636a7a33fe3d5da8b97f`): o `w0_tipo_cheiro` = 256, o `n_desiste_cheiro` = 6, o `tau_c` = 30
  e o `n_desiste` = 3.
- **Os sha256:**
  - a config `calibracao_conserto.json` (`rodada` = 2, `inatos` = `{"w_pers": 4096, "eta_h": 4}`) =
    `c2d5d5681dc8ab61346d1a4c859f1eb8cfeeb27c948edf3e264d8dc86ab369bd`;
  - o orquestrador `experiments/run_v2_digibrain_prototipo.py` = `aedec21ccf07f1eaa6ac95a19558d3a4129de440e10091251043c41280d4cbc8`;
  - o `engine.py` e o `metrics.py` são os da rodada 1.
- **O commit:** este registro é o commit da run.

**Rodada 2, o resultado** (`artifacts_v2_digibrain_prototipo/conserto/calibracao/rodada_2/`; a run no commit `5c748c3`, com a árvore
limpa e o sha da config igual ao registrado; 48 vidas, 27 s com 8 processos). **Não fecha:**

| critério | rodada 1 | rodada 2 |
|---|---|---|
| T-CADEIA-1 (as duas subchaves) | passa | passa |
| o fechamento por episódio do M3\*, a mediana das vidas (≥ 0,5) | **0,8209** | **0,7857** |
| `pesos_no_teto` (o máximo; = 0) | **0** | **0** |
| G-PESA, o incentivo (≥ 0,01) | 0,0086 | **0,0147** |
| G-PESA, o hábito | **0,1572** | **0,0728** |
| G-PESA, a memória | **0,1202** | **0,1143** |
| G-PESA, a persistência | 0,0022 | 0,0023 |

- **O incentivo passa:** com o hábito mais lento (o termo dele na unidade escolhida, de 11 a 88 nos três terços, contra 29 a 234), a
  influência do incentivo por dia fica entre 0,010 e 0,024 até o dia 14.
- **A persistência não sai do lugar, e o diagnóstico mostra por quê** (o `diagnostico.json` ganhou a contagem da persistência; o da
  rodada 1 foi refeito com ela, e os outros campos não mudaram):
  - o termo h só existe da segunda decisão de uma intenção em diante. As decisões com h > 0 são 2 045 na rodada 1 e 1 867 na rodada 2,
    de 64 512 (cerca de 3%), e isso é estrutural: as intenções acabam quase sempre na primeira consequência;
  - nessas decisões, a persistência decidiu 159 vezes na rodada 1 (7,8%) e 202 na rodada 2 (10,8%). Dobrar o `w_pers` subiu a fração,
    mas a G-PESA lê a fração de todas as decisões dos dias 8 a 14;
  - a ativação de cada unidade é cortada em A_max = 4S (`phi`, M-IMPULSO). Com o `w_pers` = 4S, um C perto de S já leva a unidade da
    intenção ao teto, e um `w_pers` maior só satura. O A_max não está na lista da seção 6.1.
- **A regra da melhor rodada, registrada antes da rodada 1, fica como está:** entre as que não fecham, a de maior mediana do fechamento
  por episódio. Por ela, a rodada 1 (0,8209) fica à frente da rodada 2 (0,7857), embora a rodada 2 passe um critério a mais (o
  incentivo). O relato leva as duas leituras ao Matheus, sem mudar a regra depois de ver os números.

**Rodada 3, a última (registrada antes da primeira vida):**
- **O que muda e por quê:** a rodada 2 com **`tau_c` 30 → 15 ticks**, o mínimo (τ ≥ Δ = 15). O ganho do compromisso vai a k_C = S, então
  C = S já na primeira decisão da intenção, e h = mul(4S, S) = 4S na segunda (antes, h = 2 048 na segunda e 3 072 na terceira). É o
  máximo que a persistência pode somar dentro da lista da 6.1, com a ativação no teto A_max.
  - O `eta_h` S/256 e o `w_pers` 4S ficam, porque o incentivo passou com eles.
  - O peso do cheiro (S/4) e o N_desiste_cheiro (6) ficam, porque o fechamento passa com folga.
- **O que se espera, sem ser critério:** pela contagem acima, é provável que a persistência continue abaixo de 0,01. A rodada mede o teto
  dela com as alavancas permitidas.
- **Os valores da rodada:** `inatos` = `{"w_pers": 4096, "eta_h": 4, "tau_c": 15}`. O resto é o de `digilab/config.py`, com o mesmo sha
  das rodadas 1 e 2.
- **Os sha256:**
  - a config `calibracao_conserto.json` (`rodada` = 3) = `80a64615d65c8b0c5ca6275681eac5137174dba21055951e8a1ad3c3dbaf0ed8`;
  - o orquestrador, o `engine.py` e o `metrics.py` são os da rodada 2 (o orquestrador =
    `aedec21ccf07f1eaa6ac95a19558d3a4129de440e10091251043c41280d4cbc8`).
- **Os critérios:** os quatro de A3.11, sem mudança. **Depois desta rodada a calibração para,** com a melhor rodada pela regra acima.
- **O commit:** este registro é o commit da run.

**Rodada 3, o resultado, e o fim da calibração do conserto** (`artifacts_v2_digibrain_prototipo/conserto/calibracao/rodada_3/`; a run
no commit `9c04ecf`, com a árvore limpa e o sha da config igual ao registrado; 48 vidas, 27 s com 8 processos). **O critério não fechou em
nenhuma das três rodadas.**

| critério | rodada 1 | rodada 2 | rodada 3 |
|---|---|---|---|
| T-CADEIA-1 (as duas subchaves) | passa | passa | passa |
| o fechamento por episódio do M3\*, a mediana das vidas (≥ 0,5) | **0,8209** | **0,7857** | **0,8397** |
| `pesos_no_teto` (o máximo; = 0) | **0** | **0** | **0** |
| G-PESA, o incentivo (≥ 0,01) | 0,0086 | **0,0147** | **0,0149** |
| G-PESA, o hábito | **0,1572** | **0,0728** | **0,0758** |
| G-PESA, a memória | **0,1202** | **0,1143** | **0,1117** |
| G-PESA, a persistência | 0,0022 | 0,0023 | 0,0027 |
| decisões com h > 0 (de 64 512) | 2 045 | 1 867 | 1 792 |
| a persistência decidiu, dado h > 0 | 7,8% | 10,8% | 12,8% |
| fecha | não | não | não |

- **A melhor rodada é a 3,** pela regra registrada antes da rodada 1: as três passam o T-CADEIA-1, e ela tem a maior mediana do
  fechamento por episódio. É também a que passa mais critérios (cinco de seis, como a rodada 2).
- **O que não fechou:** só a G-PESA da persistência (0,0027 contra ≥ 0,01). Com o `tau_c` no mínimo e o h no teto da ativação, a
  persistência decide 12,8% das decisões em que ela existe, mas essas decisões são só cerca de 3% da vida, e o resto é estrutural (A3.11,
  rodada 2). Com as alavancas da lista da seção 6.1, a persistência não chega a 0,01. Pela seção 5.3, um contraste com a G-PESA falhando
  é lido como inconclusivo por premissa (o G-ABLA-PERS, como no #420).
- **Os valores da melhor rodada** (todos PROPOSTOS; o Matheus decide):

| valor | hoje (`digilab/config.py`) | a rodada 3 | por quê |
|---|---|---|---|
| `w0_tipo_cheiro` | S/4 | S/4 | o pedido pelo Matheus; o fechamento passou nas três rodadas |
| `n_desiste_cheiro` | 6 | 6 | o pedido pelo Matheus; nenhuma busca acabou em "desistiu" |
| `eta_h` | S/128 | **S/256** | rodada 2: o hábito empurrava o incentivo para baixo de 0,01 na janela dos dias 8 a 14 |
| `w_pers` | 2S | **4S** | rodada 2: a persistência decidia pouco nas decisões em que existe |
| `tau_c` (ticks) | 30 | **15** | rodada 3: C = S na primeira decisão, h no teto na segunda |

- **Os valores não foram escritos no `digilab/config.py`.** As rodadas os passaram pelo campo `inatos` da config da calibração. Escrevê-los
  como padrão muda as vidas de todos os braços modulares (o `eta_h`, o `w_pers` e o `tau_c` valem para todos) e o gabarito G2 do #425.
  Isso vai ao Matheus junto com o piloto (65303 a 65505), que não começou.

### A3.12 O congelamento dos valores da rodada 3 do #427 (2026-10-27, autorizado pelo Matheus; worker D, Claude Code, Opus 5.5)

- **O merge do #427 não aprova todos os critérios:** a G-PESA da persistência falhou nas três rodadas (A3.11). O que o Matheus autorizou
  foi gravar os valores da melhor rodada como os padrões do modular, antes do piloto.
- **O que muda, só em `digilab/config.py` (`ConfigDigibrainInatos`):**

| valor | antes (o #425 e o #427) | agora |
|---|---|---|
| `eta_h` | S/128 (8) | **S/256 (4)** |
| `w_pers` | 2S (2 048) | **4S (4 096)** |
| `tau_c` (ticks) | 30 | **15** |
| `w0_tipo_cheiro` | S/4 | S/4 (não muda) |
| `n_desiste_cheiro` | 6 | 6 (não muda) |

  - Nada mais muda: o motor, o corpo, o mundo, o pacote do cérebro, o orquestrador e os critérios são os do #427.
  - Os três valores continuam PROPOSTOS, SEM FONTE no `config.py`, com a origem (o #427, rodada 3) no comentário de cada campo.
  - Eles valem para **todos os braços modulares** (M0 a M4-con e os três de A3.4), com ou sem as subchaves do cheiro.
  - O commit dos valores é o `7e44e9f`. Com o `tau_c` = Δ = 15, o ganho do compromisso é k_C = S: o C chega a S na primeira decisão
    da intenção, e o integrador não tem meia-vida. O T-ESTADO-1 e o T-ESTADO-2 pressupunham τ > Δ e agora cobrem esse caso.
- **O gabarito G2 regravado** (`tests/gabaritos/digibrain_modular_de_hoje.json`): é o gabarito regravado pelos valores calibrados da
  rodada 3 do #427, num commit próprio, separado do commit dos valores.
  - **O anterior** é o do #425 (o commit `5f7e986`, sha256 `c45f0c8083da32090c84bfdd75976b683840b82c48970ce9fc817837bdbc669d`), gravado
    antes das subchaves, com `eta_h` S/128, `w_pers` 2S e `tau_c` 30.
  - **O novo** (o commit `6cf9927`) tem o sha256 `ca07b0a81b201f9d833ec799babc690f1c659482896cfa642c401f99b51a2daf`. O G2 passa a
    dizer: com as duas subchaves desligadas, as vidas do modular são as do #420 **com os valores calibrados**.
  - **O que mudou, das 24 vidas de cada braço do gabarito:** o log mudou em 17 a 20 vidas do M2 em diante e em nenhuma do M0 e do M1; o
    estado interno mudou em todas do M2 em diante, em 13 do M0 e em 7 do M1; as medidas, em todas do M2 em diante e em 3 do M0. O número de
    decisões não mudou em nenhuma.
- **O M3-420 passa a ser "o M3 do #420 com os valores calibrados"** (A3.4). Ele não é mais o M3 do #420 byte a byte.
- **A persistência segue como ablação inconclusiva por premissa** (seção 5.3): o G-ABLA-PERS do piloto e da reavaliação é lido assim se
  a G-PESA dela falhar, como no #420 e nas três rodadas. **O congelamento não muda isso.**
- **As vidas já gravadas** (o #420 e as rodadas do #427) foram vividas com os valores de antes. As do #427 se refazem do disco com o
  `inatos` do `meta.json` de cada rodada (`inatos_do_meta`).

### A3.13 O piloto do conserto (65303, 65404 e 65505): o registro, antes da primeira vida (2026-10-27, worker D, Claude Code, Opus 5.5)

**O que é:** o piloto do conserto de A3.8, autorizado pelo Matheus em 2026-10-27 (pelo Gerente, depois do #428 na `main` em `57aa3a2`)
como **avaliação exploratória dos braços.** Ele roda com os valores calibrados do #428 (A3.12), que seguem PROPOSTOS até a avaliação do
piloto; nada aqui os torna definitivos.

**O que o piloto não é:**
- **ele não prova superioridade do cérebro modular,** nem sobre o A11 nem em absoluto. Pela seção 6.2, os números dele não são
  evidência;
- **ele não demonstra a contribuição da persistência.** O G-ABLA-PERS é lido como **inconclusivo por premissa** (seção 5.3), porque a
  G-PESA da persistência falhou nas três rodadas do #427 (0,0027 na melhor, a rodada 3) e o congelamento não mudou isso (A3.12). O
  contraste sai no relato com o número que tiver, e a leitura dele continua "inconclusivo por premissa", qualquer que seja o valor;
- **nenhuma vida das faixas 64xxx, 65101/65202 ou 66xxx roda.** Só as bases 65303, 65404 e 65505.

**A configuração exata:**
- **o arquivo:** `experiments/configs/v2_digibrain_prototipo/piloto_conserto.json`, com o sha256
  `bdffc2af32c31b056252ad30f83e8f514c66542c1f6819322b1c76827e974735`. Em relação à `main`, só a `descricao` mudou (ela dizia "não
  rodado"); os números são os de A3.8;
- **o commit:** este registro é o commit da run, a partir de `57aa3a2`; a run sai dele com a árvore limpa, e o `meta.json` grava o
  `git_head`, o `git_limpo` e o sha da config;
- **os outros sha256** (os de `57aa3a2`, que este commit não toca):
  - o orquestrador `experiments/run_v2_digibrain_prototipo.py` = `aedec21ccf07f1eaa6ac95a19558d3a4129de440e10091251043c41280d4cbc8`;
  - `digilab/config.py` (com os valores do #428) = `a370c02422e83195651644a526217c5dd42b0cc2606e1cb807157c531c6c5dc8`;
  - `digilab/engine.py` = `48ba51ce6426eb98a726c05e07f3a57992ae0f328f517740ec36f1c3db153630`;
  - `digilab/metrics.py` = `9e5218a75464567315778c83fa3da8e3e6e61e39decb67c65d64e308be75449f`;
- **as bases:** 65303, 65404 e 65505, com **K = 2** por base: 6 unidades (as sementes e os genomas saem de
  `bancada_v2.unidades_derivadas` com o prefixo `digibrain_prototipo`, e o `meta.json` os grava);
- **as células:** os 4 donos × os 3 lugares (12), **14 dias**, orçamento de 16 por dia;
- **os processos:** 8;
- **o comando:** `python experiments/run_v2_digibrain_prototipo.py --config experiments/configs/v2_digibrain_prototipo/piloto_conserto.json
  --processos 8`;
- **as vidas:** 12 braços × 12 células × 6 unidades = **864**. Cada vida é rejogada do disco bit a bit dentro da run (o G1).

**Os braços** (os 12 de A3.4 e A3.8; os 8 modulares de hoje com as duas subchaves do cheiro ligadas, mais os três novos e o A11):

| braço | o que é |
|---|---|
| M0 | sem P1, sem P2 e sem M-MEM, com o `cheiro_inato` e a `intencao_cheiro` |
| M1 | sem P2 e sem M-MEM, com as duas subchaves |
| M2 | sem M-MEM, com as duas subchaves |
| M3 (o M3\*) | completo, com as duas subchaves |
| M3-sp | o M3\* sem a persistência |
| M4 | o M3\* com a modulação do `g_apr` |
| M4-emb | o M4 com a série E embaralhada, lida da vida M4 da outra unidade da mesma base, na mesma célula |
| M4-con | o M3\* com o `g_apr` fixo na média do `g_apr` das vidas M4 desta run, arredondada (o `meta.json` grava o valor) |
| M3-sem-inato | o M3 só com a `intencao_cheiro` |
| M3-sem-intencao | o M3 só com o `cheiro_inato` |
| M3-420 | o M3 com as duas desligadas: o M3 do #420 com os valores calibrados (A3.4, A3.12) |
| A11 | o cérebro A, só para a comparação descritiva (seção 7) |

**Os critérios, e o que cada um decide no piloto** (os do plano, sem critério novo e sem mudar limiar; pela A3.8, **o piloto não tem
leitura de gate**):
- **o efeito de cada contraste** (seções 5.2 e 6.2; A3.4): as famílias G-ABLA (P1, P2, MEM, PERS) e G-MOD (CON, EMB), e a G-DX (INATO e
  INTENCAO, nas células do longe), com o p, o Holm e o IC95 **só como relato.** O efeito serve para o K;
- **o G-MVP:** a medida primária é a por episódio (A3.3; a fração de vidas do M3\* com o fechamento ≥ 0,5, limiar 0,8). A por ração (a de
  hoje) sai ao lado, como secundária obrigatória. No piloto, a primária só entra no poder;
- **as premissas** (seção 5.3; A3.3): a G-PESA de cada módulo (no braço dele: o incentivo no M1, o hábito no M2, a memória e a
  persistência no M3; limite inferior do IC95 > 0,01), a G-ELEGIVEL, a G-ELEGIVEL-EP (≥ 80% das vidas do M3 com 3 episódios ou mais) e
  quantos episódios as vidas têm. No piloto elas são relatadas e dizem o que a reavaliação vai ler como inconclusivo por premissa;
- **o K** (seção 6.3): o menor de 4 a 10 por base com poder simulado ≥ 0,8 em cada contraste da G-ABLA que entra na conta e no G-MVP. O
  efeito de planejamento é a metade do efeito do piloto, com α = 0,0125 na G-ABLA. O G-MVP entra com 0,8 + ½ × (a fração − 0,8) e sai da
  conta se a fração for ≤ 0,8. Um contraste com o efeito do piloto de sinal contrário (ou 0) sai da conta, e o relato diz isso. A G-MOD (α
  = 0,025) e a G-DX ficam só no relato do poder, fora do K. Se nem K = 10 chegar a 0,8, o K é 10 e o poder sai declarado;
- **o valor do M4-con da reavaliação:** a média do `g_apr` das vidas M4 do piloto (seção 6.2);
- **o custo:** o CPU por vida, e a estimativa da reavaliação com o K e os 12 braços;
- **os descritivos:** as medidas de mecanismo do cheiro por braço e lugar (A3.4), a DX-5 (A3.5, exploratória) e a comparação com o A11
  (seção 7). Nenhum tem gate.

**Os artefatos esperados** (`artifacts_v2_digibrain_prototipo/conserto/piloto/`):
- `meta.json`: a config, os sha256, o commit, a árvore limpa, as unidades, os braços, os valores inatos, o `g_apr_m4_con` e o tempo;
- `medidas.json`: as medidas de cada vida;
- `resultado.json`: o que a seção 6.2 e a A3.8 pedem (`contrastes_so_relato`, `premissas`, `G-MVP_piloto`, `G-MVP_racao_piloto`, `n`,
  `g_apr_m4`, `custo`, `descritivos`, `descritivos_conserto`, `DX-5`, `comparacao_com_o_a`). É o arquivo que a reavaliação lê, depois do
  adendo 4;
- `vidas/<braço>/<dono>_<lugar>_<semente>.jsonl`: o log de cada vida, **fora do git**, na worktree `v2-modular-piloto-conserto`.
Os três `.json` entram no git. O RESULTADO ganha uma seção com os números deles, e a leitura vai ao Matheus. O adendo 4 (A3.8) não é
escrito neste PR: ele vem depois da leitura do Matheus.

**O piloto rodou** do commit `4adce20`, com a árvore limpa e o sha da config igual ao registrado: 864 vidas, 375 s, 8 processos. Os
números estão na seção 7 do `docs/RESULTADO_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md`, todos tirados dos artefatos. Em resumo, sem leitura de
gate:
- **o G-MVP por episódio:** 0,8056;
- **a G-PESA da persistência:** 0,0033, falhando de novo; o G-ABLA-PERS segue inconclusivo por premissa;
- **o K:** 10, sem chegar ao alvo, porque o poder do G-MVP fica em 0,1085;
- **o M4-con:** 1 923.
O adendo 4 vem depois da leitura do Matheus.

## Adendo 4: a reavaliação por estimativa (2026-10-27, Gerente; APROVADO pelo Matheus em 2026-10-27, com a A4.4 completada)

**Status: APROVADO pelo Matheus em 2026-10-27.**
- **As palavras dele:** "Aprovo a opção 2: a 66xxx será uma avaliação por estimativa; o G-MVP será relatado com intervalo de confiança, sem
  'passa' ou 'falha'. O limiar de 0,8 permanece como referência."
- **Sobre o teste:** "A proposta de usar o teste t pareado sobre as 50 unidades me parece adequada", com a condição de completar a A4.4
  antes do merge (a independência e o pareamento, o Holm no nível da família, a incerteza das simulações e as seis unidades), e de integrar
  "se essa verificação sustentar o método e os checks estiverem verdes".
- **A A4.4 foi completada.** A verificação sustenta o t contra o teste do plano em todos os contrastes, famílias e formas testados, com os
  limites registrados em A4.4.6: a ressalva da assimetria negativa, a G-MOD com 5,9 % de erro de família e o G-MOD-EMB pelas médias de
  base.

**Nenhuma vida da faixa 66xxx foi registrada nem rodou. Nenhuma roda antes de dois passos:**
1. **a implementação das mudanças de A4.7,** com os testes, num PR próprio, na `main`;
2. **o registro da run num commit empurrado,** antes da primeira vida, com o escopo conferido pelo Gerente.

**A decisão que este adendo cumpre** (Matheus, 2026-10-27, sobre a proposta do Gerente): "seguir a opção 2, como avaliação por
estimativa." Pedidos dele para o adendo:
- **o G-MVP:** manter o limiar de 0,8 registrado, mas tratá-lo só como estimativa com intervalo de confiança, sem "passa" nem "falha";
- **o que não se afirma:** deixar explícito que a avaliação não demonstra prontidão do protótipo nem superioridade modular;
- **a persistência:** mantê-la como inconclusiva por premissa;
- **o poder:** diferenciar o cálculo para 0,8028 (13,1 % com K = 10) do cálculo para 0,8056 (21,4 % com K = 10), e apresentar os dois como
  aproximações;
- **o bootstrap com cinco bases:** investigar se o problema afeta também os intervalos e os testes das ablações, e propor como corrigir ou
  limitar essa interpretação antes de qualquer execução.

**As fontes:**
- **o piloto do conserto:** `artifacts_v2_digibrain_prototipo/conserto/piloto/` (o #429, na `main` em `1a16678`);
- **as contas novas deste adendo:** o `experiments/adendo4_poder_digibrain_modular.py`, que só reamostra as unidades do piloto. Nenhuma
  vida roda. Ele grava `artifacts_v2_digibrain_prototipo/conserto/adendo4/poder.json` (sha256 `47ca4cd1…7b69`), e rodado duas vezes sai
  igual, byte a byte.

### A4.0 O que não muda

- **O limiar do G-MVP:** 0,8, como na seção 5.2 e em A3.3. O número fica escrito no plano e é a referência da leitura em A4.2. Ele não é
  reduzido nem alterado por causa do piloto.
- **O desenho:** os 12 braços de A3.4 e A3.8, as 12 células, os 14 dias e as bases 66101, 66202, 66303, 66404 e 66505.
- **As medidas:** a primária é por episódio (A3.3), e a por ração é a secundária obrigatória.
- **Os valores calibrados do #428:** seguem PROPOSTOS.
- **O G-ABLA-PERS é inconclusivo por premissa** (seção 5.3). A G-PESA da persistência falhou nas três rodadas do #427 (0,0027 na melhor) e
  no piloto (0,0033). A reavaliação não demonstra a contribuição da persistência, qualquer que seja o p.
- **Os resultados anteriores:** nada aqui muda o #420, a 64xxx (queimada) nem os artefatos dele.

### A4.1 A pergunta muda

- **A pergunta registrada era confirmatória:** o protótipo atinge o critério (o limite inferior do IC95 da fração ≥ 0,8)?
- **A pergunta desta reavaliação é de estimativa:** quanto o protótipo fecha, com que incerteza?
- **Por que mudou** (a proposta do Gerente, 2026-10-27, com as contas de A4.3):
  - o piloto deu 0,8056, praticamente no limiar;
  - para o teste confirmatório ter poder de 0,8, o K precisaria ser cerca de 70 vezes o orçamento registrado (K = 10, seção 6.3);
  - com K = 10, o teste falharia na maior parte das vezes mesmo com o protótipo um pouco acima de 0,8.
- **É uma mudança de pergunta, registrada antes de qualquer vida, e não uma correção do critério.** Nada se ajusta depois de ver a 66xxx.
- **A 66xxx roda uma vez.** Usada para estimar, ela não serve depois como confirmatória. Um teste confirmatório futuro do G-MVP precisa de
  faixa nova e de adendo novo.

### A4.2 O G-MVP como estimativa

- **O que sai:** a fração de vidas do M3\* com o fechamento por episódio ≥ 0,5 (A3.3), com o IC95 de A4.4. **Sem "passa" e sem "falha".**
  O G-MVP por ração (o secundário obrigatório) sai do mesmo jeito.
- **Onde fica o 0,8:** ao lado do IC, como referência. O relato diz em que posição o IC fica em relação a ele, numa destas três frases:
  - "o IC95 inteiro acima de 0,8";
  - "o IC95 contém 0,8";
  - "o IC95 inteiro abaixo de 0,8".
  Nenhuma das três é aprovação ou reprovação do gate.
- **O que a avaliação não demonstra,** explícito em todo relato e resultado dela:
  - **a prontidão do protótipo.** O G-MVP é parte do gate de prontidão (seção 5.6, ii), e sem "passa" esse gate não é cumprido. O A segue
    como o cérebro do MVP;
  - **a superioridade modular.** A comparação com o A11 (seção 7) segue descritiva. Os contrastes são entre os braços do próprio modular e
    medem módulos, não arquiteturas.
- **A precisão esperada com K = 10:** a largura mediana do IC95 do G-MVP por episódio é 0,035 pelo t sobre as unidades (A4.4). Uma
  aproximação, pela reamostragem das 6 unidades do piloto. Pelo bootstrap do plano daria 0,028, estreito demais (A4.4).

### A4.3 O poder do G-MVP confirmatório (aproximações)

- **O que é:** só a justificativa de A4.1. A reavaliação não usa o poder.
- **O método:** o `poder_por_k` do orquestrador, sem mudança: 2 000 réplicas, 1 000 reamostragens internas, 5 bases, o limite inferior do
  IC95 ≥ 0,8.
- **A base:** as 6 unidades do piloto, cada uma a média das 12 células: 0,75; 0,917; 0,833; 0,75; 0,75; 0,833. O desvio padrão é 0,068.
- **Os dois valores verdadeiros supostos:**
  - **0,8028:** a regra do plano (seção 6.3), o limiar mais metade da margem do piloto;
  - **0,8056:** o observado no piloto, mais otimista.
- **São aproximações, por três razões:**
  - as 6 unidades estimam mal a variabilidade, e os valores saem em múltiplos de 1/12;
  - o teste do plano tem o defeito de A4.4, então o poder dele está superestimado;
  - o valor verdadeiro não é conhecido.

| K por base | 4 | 10 | 20 | 40 | 80 | 150 | 250 | 400 | 600 | 800 | 1 000 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| poder com 0,8028 (a regra do plano) | 0,105 | **0,131** | 0,146 | 0,192 | 0,255 | 0,375 | 0,497 | 0,623 | 0,772 | 0,851 | 0,892 |
| poder com 0,8056 (o observado) | 0,136 | **0,214** | 0,279 | 0,386 | 0,569 | 0,796 | 0,900 | 0,974 | 0,997 | 1,000 | 1,000 |
| passa com o valor no limiar exato, 0,80 | 0,054 | 0,075 | 0,074 | 0,072 | 0,075 | 0,086 | 0,086 | 0,073 | 0,086 | 0,079 | 0,075 |

- **Com 0,8028:** o poder de 0,8 exige K entre 600 e 800 por base, cerca de 3 500 unidades e 300 h de CPU com os 12 braços.
- **Com 0,8056:** exige K ≈ 150.
- **Nos dois casos, o orçamento registrado (K = 10) fica muito abaixo.**
- **A última linha mostra o defeito de A4.4:** com o valor verdadeiro exatamente no limiar, o gate passaria em 5 % a 9 % das réplicas, e não
  nos 2,5 % nominais.

### A4.4 O bootstrap com cinco bases: o que afeta e a correção

**Completada a pedido do Matheus (2026-10-27), antes do merge.** Ele pediu quatro pontos:
- explicar a independência e o pareamento;
- avaliar o t e o Holm no nível da família;
- dar a incerteza das simulações;
- ressaltar que a variabilidade vem de só seis unidades.

Todas as contas saem do `poder.json`, pelo `experiments/adendo4_poder_digibrain_modular.py`. São reamostragens das unidades do piloto ou
distribuições fixas, e nenhuma vida roda.

#### A4.4.1 O achado

O bootstrap da convenção (seção 5.2.1) reamostra as 5 bases, e não as unidades. Com só 5 grupos, o bootstrap percentil:
- subestima a variabilidade da média, porque a variância das médias das 5 somas reamostradas tem o fator (n − 1)/n = 0,8;
- não tem a cauda da t com 4 graus de liberdade.

O IC95 dele fica estreito demais e o p fica pequeno demais, nos contrastes e no G-MVP.

#### A4.4.2 As unidades e o pareamento

**O que é uma unidade.** Cada unidade é um par (base b, réplica k), com semente `derivar_semente("digibrain_prototipo", b, k)` e genoma
`derivar_semente("digibrain_prototipo-genoma", b, k)`. Os dois saem do sha256 dos rótulos (`experiments/bancada/faixas.py:109-121`, a
regra E3; `digilab/protocol.py:189`).
- A base é só o primeiro rótulo do hash. As unidades da mesma base não têm semente, genoma, mundo, dono nem estado em comum.
- Cada vida é montada do zero, com o motor, o mundo, o corpo e o cérebro novos (`viver` e `fabricas`, `run_v2_digibrain_prototipo.py:310-339`).
- Por isso as 50 unidades são independentes, com uma exceção, adiante.

**O pareamento.** Dentro de cada unidade, todos os braços vivem as mesmas 12 células (4 donos × 3 lugares), com a mesma semente, o mesmo
genoma e o mesmo motor. Só o cérebro muda.
- A rng do mundo é separada da rng de política (CLAUDE.md), então a parte do mundo que não depende do pet é a mesma em todos os braços.
- A diferença de um contraste numa unidade é feita célula a célula: a medida do braço a menos a do braço b, na mesma (semente, dono,
  lugar). Depois tira-se a média das células (`por_unidade`, `run_v2_digibrain_prototipo.py:745`).
- Cada unidade dá uma diferença por contraste. O teste é sobre as 50 diferenças.
- **O G-MVP não é contraste:** a fração do M3\* por unidade é o nível do próprio braço, e o IC é sobre as 50 frações.

**A exceção: o G-MOD-EMB.**
- O M4-emb de uma unidade usa a série de excitação do M4 da unidade seguinte da mesma base, e a última usa a primeira (seção 2;
  `doadores`, `run_v2_digibrain_prototipo.py:715-725`). As 10 diferenças do G-MOD-EMB de uma base formam um anel e dependem umas das outras.
- Para esse contraste, a base é o grupo independente. Ele passa a usar o t sobre as 5 médias de base (D), com 4 graus de liberdade.
- O piloto (2 unidades por base) não permite medir essa dependência. Então o EMB não usa o t sobre as unidades.
- **O M4-con usa um valor fixo,** o `g_apr` médio do piloto, igual para todas as unidades. Isso não cria dependência entre elas.

#### A4.4.3 Cada contraste, sob a nula

- **Como se calcula:** as diferenças por unidade do piloto, centradas em zero (a nula verdadeira), sorteadas em 5 bases × 10 unidades.
- **A incerteza Monte Carlo:** 2 000 réplicas, com 1 000 reamostragens do bootstrap em cada uma. O erro padrão de cada taxa vai de 0,2 a 0,3
  ponto percentual nas taxas perto de 1 %, e de cerca de 0,5 a 0,6 ponto nas de 6 %.
- **A coluna da assimetria** é a do piloto, com 6 unidades. Ela é muito ruidosa e só indica a forma.

| contraste | A, o do plano: α 0,0125 / 0,025 / 0,05 | C, t sobre as 50 unidades | D, t sobre as 5 médias de base | cobertura do IC95, A / C | assimetria no piloto (6 unidades) |
|---|---|---|---|---|---|
| G-ABLA-MEM | 0,063 / 0,075 / 0,107 | 0,016 / 0,027 / 0,051 | 0,010 / 0,024 / 0,046 | 0,852 / 0,953 | −0,36 |
| G-ABLA-P1 | 0,062 / 0,082 / 0,106 | 0,011 / 0,025 / 0,048 | 0,013 / 0,022 / 0,048 | 0,831 / 0,946 | 0,18 |
| G-ABLA-P2 | 0,061 / 0,074 / 0,098 | 0,009 / 0,019 / 0,045 | 0,011 / 0,021 / 0,044 | 0,851 / 0,953 | 0,48 |
| G-ABLA-PERS | 0,068 / 0,084 / 0,108 | 0,011 / 0,021 / 0,040 | 0,011 / 0,022 / 0,050 | 0,833 / 0,950 | 0,47 |
| G-DX-INATO | 0,072 / 0,089 / 0,117 | 0,017 / 0,028 / 0,058 | 0,014 / 0,024 / 0,056 | 0,825 / 0,953 | −0,60 |
| G-DX-INTENCAO | 0,059 / 0,075 / 0,103 | 0,015 / 0,029 / 0,051 | 0,016 / 0,026 / 0,045 | 0,845 / 0,952 | −0,20 |
| G-MOD-CON | 0,080 / 0,098 / 0,129 | 0,023 / 0,038 / 0,069 | 0,019 / 0,034 / 0,065 | 0,831 / 0,945 | −0,88 |
| G-MOD-EMB | 0,066 / 0,082 / 0,105 | 0,011 / 0,024 / 0,053 | 0,015 / 0,026 / 0,047 | 0,841 / 0,954 | 0,03 |
| G-MVP-EP (a fração − 0,8) | 0,053 / 0,071 / 0,094 | 0,009 / 0,019 / 0,045 | 0,012 / 0,022 / 0,041 | 0,835 / 0,945 | 0,63 |

**O que a tabela diz:**
- **O teste do plano (A) erra cerca de 5 vezes o nominal** no α = 0,0125: de 0,053 a 0,080, contra 0,0125. O IC95 dele cobre de 0,825 a
  0,852.
- **O t sobre as unidades (C) fica perto do nominal** e cobre de 0,945 a 0,954.
- **A exceção é o G-MOD-CON,** com 0,023 no α = 0,0125. É o contraste com a assimetria mais negativa no piloto (A4.4.5).
- **O EMB está na linha da tabela,** mas a dependência do anel não está nessa simulação (A4.4.2).

#### A4.4.4 O Holm no nível da família

- **Como se calcula:** o erro da família (FWER) é a chance de o Holm (α = 0,05) rejeitar algum contraste cuja nula é verdadeira.
- **O sorteio:** as unidades do piloto sorteadas inteiras. Assim fica a correlação entre os contrastes da mesma unidade.
- **A incerteza Monte Carlo:** 4 000 réplicas, com o intervalo de Wilson de 95 % entre colchetes.
- **Os dois cenários:**
  - **nula global:** todos os contrastes da família com efeito zero;
  - **nula parcial:** o P1, a MEM e os dois G-DX com o efeito de planejamento do plano (a metade do piloto), e os outros com efeito zero.

  Na nula parcial, o G-DX não tem contraste nulo, então o erro da família não se aplica.

| família (m) | cenário | A, o do plano | C, o t sobre as unidades | a proposta (C; o G-MOD-EMB pelo D) |
|---|---|---|---|---|
| G-ABLA (4) | nula global | 21,4 % [20,2 %; 22,7 %] | 4,0 % [3,4 %; 4,6 %] | 4,0 % [3,4 %; 4,6 %] |
| G-DX (2) | nula global | 12,7 % [11,7 %; 13,8 %] | 4,9 % [4,3 %; 5,6 %] | 4,9 % [4,3 %; 5,6 %] |
| G-MOD (2) | nula global | 16,3 % [15,2 %; 17,5 %] | 6,2 % [5,5 %; 7,0 %] | 5,9 % [5,2 %; 6,7 %] |
| G-ABLA (4) | nula parcial (o P2 e a PERS nulos) | 11,9 % [10,9 %; 12,9 %] | 3,0 % [2,5 %; 3,6 %] | 3,0 % [2,5 %; 3,6 %] |
| G-MOD (2) | nula parcial (os dois nulos) | 16,1 % [14,9 %; 17,2 %] | 5,3 % [4,6 %; 6,0 %] | 5,1 % [4,5 %; 5,9 %] |

**O que a tabela diz:**
- **Com o teste do plano,** o Holm erra a família 1 vez em 5 na G-ABLA (21,4 %) e passa de 12 % nas outras.
- **Com a proposta,** o Holm fica em 4,0 % na G-ABLA e 4,9 % na G-DX, dentro dos 5 %. A G-MOD fica um pouco acima: 5,9 % [5,2 %; 6,7 %]
  na nula global, puxada pelo G-MOD-CON.
- **O poder, na nula parcial, dentro do Holm e com a proposta:**
  - o P1 e a MEM: 1,000;
  - o G-DX-INATO: 0,280;
  - o G-DX-INTENCAO: 0,141.

  O teste do plano dava 0,438 e 0,242 nos dois do cheiro, porque rejeita demais.

#### A4.4.5 A sensibilidade à forma, porque a variabilidade vem de seis unidades

- **O problema:** todas as contas acima sorteiam as 6 unidades do piloto. Elas estimam mal a variabilidade e quase nada informam sobre a
  forma (assimetria e caudas). Os valores ainda saem em poucos níveis.
- **O que dá para medir sem isso:** o t não depende da escala, só da forma. Então o erro dele pode ser medido com formas fixas de média
  zero, sem usar o piloto.
- **O cálculo:** 2 000 réplicas, 50 valores em 5 bases. O erro padrão Monte Carlo vai de 0,2 a 0,6 ponto percentual.
- **O sinal da assimetria:** é o da diferença orientada (positivo = a direção prevista). A assimetria negativa é a cauda longa contra a
  previsão.

| forma (média 0) | A: α 0,0125 / 0,025 / 0,05 | C: α 0,0125 / 0,025 / 0,05 |
|---|---|---|
| normal | 0,059 / 0,080 / 0,108 | 0,012 / 0,029 / 0,055 |
| t com 3 gl (cauda pesada) | 0,069 / 0,087 / 0,115 | 0,009 / 0,017 / 0,045 |
| exponencial (assimetria +2) | 0,037 / 0,049 / 0,072 | 0,004 / 0,005 / 0,022 |
| lognormal σ 1 (assimetria ~+6) | 0,025 / 0,037 / 0,057 | 0,001 / 0,004 / 0,013 |
| gama k 16 invertida (assimetria −0,5) | 0,084 / 0,099 / 0,130 | 0,015 / 0,034 / 0,061 |
| gama k 4 invertida (assimetria −1) | 0,074 / 0,089 / 0,113 | 0,022 / 0,040 / 0,061 |
| exponencial invertida (assimetria −2) | 0,092 / 0,107 / 0,132 | 0,038 / 0,059 / 0,089 |
| lognormal invertida (assimetria ~−6) | 0,131 / 0,145 / 0,181 | 0,073 / 0,102 / 0,136 |

**O que a tabela diz:**
- **O t sobre as unidades fica perto do nominal** com a forma normal, com cauda pesada e com assimetria positiva (onde fica conservador).
- **Com a assimetria negativa, ele passa do nominal:**

  | assimetria | erro do t no α = 0,0125 | vezes o nominal |
  |---|---|---|
  | −0,5 | 0,015 | cerca de 1,2 |
  | −1 | 0,022 | cerca de 1,8 |
  | −2 | 0,038 | cerca de 3 |

- **O teste do plano erra mais em todas as formas.** Só fica abaixo do nominal com a assimetria positiva forte.
- **Conclusão:** o t sobre as unidades é melhor que o teste do plano em toda forma testada, mas não garante o nominal com a assimetria
  negativa forte. No piloto, o G-MOD-CON (−0,88) e o G-DX-INATO (−0,60) têm assimetria negativa, mas 6 unidades não estimam a assimetria
  de forma confiável.

#### A4.4.6 A correção e o limite da leitura

1. **As famílias G-ABLA, G-MOD e G-DX** decidem pelo t, com o Holm sem mudança: as mesmas famílias, a mesma ordem, os mesmos α.
   - **Em todos os contrastes, exceto o G-MOD-EMB:** o p é o `t_pareado.p_unilateral` que o `contraste_pareado` (`digilab/metrics.py`) já
     calcula sobre as 50 unidades.
   - **No G-MOD-EMB:** o t sobre as 5 médias de base, com 4 graus de liberdade (A4.4.2).
   - **O p do bootstrap** sai ao lado, rotulado "a convenção da seção 5.2.1, anticonservadora com 5 bases (A4.4)".
2. **Os IC95,** inclusive o do G-MVP (A4.2) e o da G-PESA: pelo t sobre as unidades (média ± t₀,₉₇₅;n−1 × dp/√n). No G-MOD-EMB, pelo t
   sobre as médias de base.
   - O cálculo entra em `digilab/metrics.py`, com teste.
   - O IC percentil do bootstrap sai ao lado, como descritivo.
3. **O limite da leitura, pela assimetria, registrado antes de qualquer vida:**
   - **A medida:** a reavaliação calcula a assimetria amostral (g1) das 50 diferenças orientadas de cada contraste. O cálculo entra em
     `digilab/metrics.py`.
   - **A ressalva:** se g1 ≤ −0,5, o contraste sai com esta frase: "assimetria negativa: o erro do tipo I do t pode passar do nominal
     (A4.4.5; com g1 = −1, cerca de 1,8 vez)". Uma rejeição do Holm nesse contraste não é lida como confirmação.
   - **O limiar −0,5** é a forma mais branda da tabela em que o erro já passa do nominal (0,015 contra 0,0125). É PROPOSTO, sem fonte
     externa, e o g1 de 50 valores também é ruidoso.
   - **A ressalva não muda o p, o Holm nem a decisão gravada.** Ela só limita o que se afirma.
4. **A G-MOD com o erro de família um pouco acima de 5 %** (5,9 % na nula global, pela simulação com as 6 unidades): é registrada como
   ressalva da família. A G-MOD é secundária (seção 5.2), e a leitura dela já é à parte (seção 5.5).
5. **A G-PESA também usa o bootstrap** (o limite inferior do IC95 > 0,01) e herda o defeito: ela passa com mais facilidade do que deveria.
   - Com o IC pelo t, a premissa fica mais exigente.
   - A persistência falha de qualquer forma (0,0033), e a leitura dela não muda: inconclusiva por premissa.
6. **Por que o t e não a convenção com uma ressalva:**
   - o erro de família do teste do plano (21,4 % na G-ABLA) deixaria o Holm sem controle;
   - o t é o teste que o `contraste_pareado` já calcula;
   - a correção é decidida antes de qualquer vida da 66xxx e sem olhar para ela. Ela não muda limiar, α, família nem medida.

**As validações anteriores com a mesma convenção** (o #420 e outras da V2 com 5 bases) ficam como estão. Este adendo não reabre nenhum
resultado. Se e como revisá-las é uma questão aberta do Matheus (A4.9).

### A4.5 O K, o M4-con e o custo

- **K = 10 por base** (seção 6.3: "Se nem K = 10 chega a 0,8, a avaliação roda com 10, e o poder sai declarado"). São 50 unidades e
  7 200 vidas com o A11.
- **O `g_apr` do M4-con:** 1 923, a média do `g_apr` das vidas M4 do piloto (seção 6.2).
- **O custo estimado:** 15 273 s de CPU (cerca de 4,2 h), pelo `resultado.json` do piloto. Com 8 processos, perto de uma hora de parede.

### A4.6 A leitura da reavaliação (no lugar da tabela da seção 5.5)

- **A tabela da seção 5.5 não se aplica.** Ela condiciona a leitura do G-ABLA ao G-MVP passar, e aqui o G-MVP não tem passa nem falha.
- **O G-MECANISMO** (os testes de mecanismo, a pré-condição) continua binário: com um falhando, nenhuma vida roda.
- **As famílias G-ABLA, G-MOD e G-DX** saem com o Holm de A4.4. Um contraste rejeitado lê-se: "o módulo pesa no sentido previsto dentro do
  M3\*, nestas condições". Não se lê como "o modular vai à comida pelos próprios módulos", que exige o G-MVP passar (seção 5.5), nem como
  superioridade da arquitetura.
- **O G-ABLA-PERS:** inconclusivo por premissa (A4.0), qualquer que seja o p.
- **As premissas** (G-PESA, G-ELEGIVEL e G-ELEGIVEL-EP) e os descritivos (a DX-5, as medidas do cheiro e o A11) seguem como no plano, com
  os IC de A4.4.

### A4.7 O que precisa mudar no código antes de qualquer vida (o PR de implementação, depois da aprovação)

- **No `experiments/run_v2_digibrain_prototipo.py`:**
  - a análise da reavaliação deixa de calcular "passa" para o G-MVP por episódio e para o por ração. Ela grava a estimativa, o IC de A4.4 e
    a posição do IC em relação a 0,8;
  - o p do Holm passa a ser o do t sobre as unidades, nas três famílias, e o do t sobre as médias de base no G-MOD-EMB (A4.4.6);
  - cada contraste grava a assimetria g1 das diferenças por unidade e, com g1 ≤ −0,5, a ressalva de A4.4.6;
  - o p do bootstrap e o IC percentil ficam ao lado, rotulados;
  - a leitura de A4.6 substitui a da seção 5.5.
- **No `digilab/metrics.py`:**
  - o IC95 pelo t sobre as unidades e o t sobre as médias de base, ao lado do `contraste_pareado`, com teste;
  - a assimetria g1, com teste;
  - a conta do `contraste_pareado` de hoje não muda.
- **Os testes:**
  - o G-MVP da reavaliação não tem chave "passa";
  - o Holm usa o p do t (o das médias de base no G-MOD-EMB);
  - a ressalva da assimetria sai com g1 ≤ −0,5 e não muda o p nem a decisão gravada;
  - o IC t confere com uma conta à mão;
  - o G2, o G1 e o G-MECANISMO seguem passando. As vidas não mudam, só a análise.
- **A trava:** hoje o orquestrador aceita a reavaliação assim que o texto "## Adendo 4" existe no plano. A implementação faz a reavaliação
  exigir também a marca de aprovação deste adendo (o status "APROVADO pelo Matheus"), para um adendo só PROPOSTO não liberar vidas.
- **Se alguma dessas mudanças exigir mexer no motor, no corpo, no mundo, no `engine.py`, no cérebro ou nas medidas por vida:** para e volta
  ao Matheus.

### A4.8 Os critérios de parada

- **Antes da reavaliação:**
  - sem a aprovação deste adendo e o PR de A4.7 na `main`, nenhuma vida da 66xxx;
  - qualquer quebra do G2, do G1 ou do G-MECANISMO para tudo.
- **O registro da run,** num commit empurrado antes da primeira vida: o commit, a config com o sha, as bases, o K, os braços e a leitura
  deste adendo. O Gerente confere o escopo antes das vidas.
- **A reavaliação roda uma vez.** O resultado é registrado como está, e nada se ajusta olhando para ele. O próximo passo vai ao Matheus.

### A4.9 As decisões

1. **DECIDIDO pelo Matheus em 2026-10-27:** a opção 2, a pergunta de estimativa (A4.1), o G-MVP com IC e sem passa/falha (A4.2) e o
   limiar de 0,8 como referência.
2. **DECIDIDO, com a verificação de A4.4:** o t pareado sobre as 50 unidades decide o Holm. O G-MOD-EMB usa o t sobre as médias de base, e
   o bootstrap fica descritivo.
   - **PROPOSTO, dentro dessa decisão:** o limiar de assimetria −0,5 da ressalva (A4.4.6).
3. **Em aberto, para o Matheus:**
   - as validações anteriores com a mesma convenção (A4.4): ficam como estão, ou se abre uma revisão à parte?
   - o retorno zero do dormir (A3.6).

### A4.10 A reavaliação (66101 a 66505): o registro, antes da primeira vida (2026-10-28, worker D, Claude Code, Opus 5.5)

**O que é:** o registro de A4.8, depois do PR de A4.7 (o #431) na `main` em `93523e3`, com o merge autorizado pelo Matheus em 2026-10-28.
- **Nenhuma vida roda neste registro.** O Gerente confere o escopo, e a run só começa depois de ele liberar por mensagem.
- **A reavaliação roda uma vez.** O resultado é registrado como está, e nada se ajusta olhando para ele (A4.8).
- **Os valores calibrados do #428 seguem PROPOSTOS.** Nada aqui os torna definitivos.

**1. As sementes e as unidades:**
- **as bases:** 66101, 66202, 66303, 66404 e 66505, da faixa 66101 a 66505, já reservada em `experiments/bancada/faixas.py` (a fonte é a
  PROPOSTA_DIAGNOSTICO_DIGIBRAIN_MODULAR, seção 6);
- **K = 10 por base** (A4.5): o `n.k` do `resultado.json` do piloto do conserto, que o orquestrador lê (`adendo_do_piloto_conserto`).
  São **50 unidades**;
- **a derivação** (a regra E3; `bancada_v2.unidades_derivadas`, com o prefixo `digibrain_prototipo`). A unidade k da base b, com
  k = 0 a 9, tem:
  - a semente `derivar_semente("digibrain_prototipo", b, k)`;
  - o genoma `derivar_semente("digibrain_prototipo-genoma", b, k)`.

  A função falha alto com colisão, e o `meta.json` grava as 50 unidades:
  - **a primeira** (66101, k = 0): a semente 17726104078491772386 e o genoma 16814212922965156843;
  - **a última** (66505, k = 9): a semente 12622119303600028215 e o genoma 11028243305523479797;
- **nenhuma vida da faixa existe em disco.** Em 2026-10-28 foram conferidas as 13 worktrees com `artifacts_v2_digibrain_prototipo/`:
  - nenhuma tem a pasta `reavaliacao/`;
  - nenhum dos 7 320 logs de vida (`.jsonl`) tem no nome uma das 50 sementes.

**2. Os braços e as células:**
- **a configuração de cada braço:**
  - as subchaves estão em `SUBCHAVES_CONSERTO` (`experiments/run_v2_digibrain_prototipo.py`), e o `meta.json` as grava;
  - os valores dos inatos são os padrões de `digilab/config.py` (`ConfigDigibrainInatos`), com os do #428: `eta_h` S/256, `w_pers` 4S e
    `tau_c` 15. Todos seguem PROPOSTOS;
  - a config da reavaliação não tem o campo `inatos`, que só a calibração do conserto pode ter (A3.8).

| braço | o que é |
|---|---|
| M0 | sem P1, sem P2 e sem M-MEM, com o `cheiro_inato` e a `intencao_cheiro` |
| M1 | sem P2 e sem M-MEM, com as duas subchaves |
| M2 | sem M-MEM, com as duas subchaves |
| M3 (o M3\*) | completo, com as duas subchaves |
| M3-sp | o M3\* sem a persistência |
| M4 | o M3\* com a modulação do `g_apr` |
| M4-emb | o M4 com a série E embaralhada, lida da vida M4 da unidade seguinte da mesma base, na mesma célula (a última usa a primeira: o anel de A4.4.2) |
| M4-con | o M3\* com o `g_apr` fixo em **1 923**, a média do piloto do conserto (A4.5) |
| M3-sem-inato | o M3 só com a `intencao_cheiro` |
| M3-sem-intencao | o M3 só com o `cheiro_inato` |
| M3-420 | o M3 com as duas subchaves desligadas: o M3 do #420 com os valores calibrados |
| A11 | o cérebro A, só para a comparação descritiva (seção 7) |

- **as células:** os 4 donos (atencioso, relapso, aleatório, incoerente) × os 3 lugares (comedouro, perto, longe), 12 por unidade;
- **o tempo:** 14 dias, com orçamento de 16 por dia;
- **as vidas:** 12 braços × 12 células × 50 unidades = **7 200**. O M4-emb e o M4-con rodam numa segunda passada, depois das vidas M4.

**3. As métricas:**
- **O que cada vida grava** (`medidas.json`, uma entrada por vida; as funções de `digilab/metrics.py`, como no piloto):
  - **as medidas de hoje** (seção 4): `d_fe`, `d_fe_vida`, `privacao`, `exaustao`, a `cadeia` por ração, `com_cadeia`, `latencia_media` e
    as `acoes`;
  - **as do conserto** (A3.1 a A3.5):
    - `episodios_fome`, com a taxa por episódio, o n e o `com_cadeia`;
    - `cadeia_w` e `racao_na_janela`;
  - **as do cérebro**, nos 11 braços modulares:
    - a `influencia`, para a G-PESA;
    - `falta_ao_comer`, `repeticao` e `intencoes_com_meta`;
    - `pesos_no_teto` e `g_apr_media`;
    - a DX-1 (`visitas_vazias`, com a v1 ao lado), a DX-5 (`repeticao_r_possivel`) e o mecanismo do `cheiro`;
  - **o custo** da vida, em CPU e em parede.
- **As conferências durante a run:**
  - cada vida é rejogada do disco bit a bit (o G1);
  - o cenário e o mecanismo do braço são conferidos (o G-MECANISMO por vida);
  - qualquer falha levanta erro e para a run.
- **A medida por unidade:**
  - **num contraste:** a diferença célula a célula (braço a − braço b), na mesma semente, no mesmo dono e no mesmo lugar, com a média
    tirada nas células do contraste (`por_unidade`);
  - **no G-MVP:** o nível do próprio M3\*.

  Cada unidade dá um valor por contraste.
- **Os contrastes** (a diferença é a − b; as famílias, as ordens e os α são os do plano, A4.4.6):

| família | contraste | a − b | medida | células | o teste (A4.4.6) |
|---|---|---|---|---|---|
| G-ABLA (Holm, m = 4, α 0,05) | G-ABLA-P1 | M0 − M1 | `falta_ao_comer` | as 12 | t pareado sobre as 50 unidades |
| | G-ABLA-P2 | M2 − M1 | `repeticao.indice` | as 12 | t sobre as 50 unidades |
| | G-ABLA-MEM | M3 − M2 | a taxa da `cadeia` | as 4 do comedouro | t sobre as 50 unidades |
| | G-ABLA-PERS | M3 − M3-sp | `intencoes_com_meta` | as 12 | t sobre as 50 unidades; **inconclusivo por premissa** |
| G-MOD (Holm, m = 2, α 0,05) | G-MOD-CON | M4-con − M4 | `d_fe` | as 12 | t sobre as 50 unidades |
| | G-MOD-EMB | M4-emb − M4 | `d_fe` | as 12 | **t sobre as 5 médias de base** (4 gl), por causa do anel |
| G-DX (Holm, m = 2, α 0,05) | G-DX-INATO | M3 − M3-sem-inato | a taxa por episódio | as 4 do longe (a leitura principal; as 12 saem ao lado, com o seu Holm) | t sobre as 50 unidades |
| | G-DX-INTENCAO | M3 − M3-sem-intencao | a taxa por episódio | as 4 do longe (idem) | t sobre as 50 unidades |

- **As saídas do `resultado.json`** (`analisar_conserto`, A4.7):
  - **a pergunta e a primária:** `pergunta` (a de estimativa de A4.1) e `primaria` = `G-MVP-EP`;
  - **os dois G-MVP** (sem "passa"):
    - **`G-MVP-EP`:** a fração de vidas do M3\* com a taxa de fechamento por episódio ≥ 0,5, por unidade. Saem a estimativa, o **IC95
      pelo t** sobre as 50 frações, o IC percentil do bootstrap ao lado (descritivo e rotulado) e a posição do IC em relação a 0,8, numa
      das três frases de A4.2;
    - **`G-MVP`:** o mesmo, por ração (o secundário obrigatório);
  - **as famílias `G-ABLA`, `G-MOD` e `G-DX`**, cada contraste com:
    - a estimativa, o IC95 e o p unilateral do t; no G-MOD-EMB, pelo t sobre as 5 médias de base;
    - o `holm`, com a ordem, o limiar, o `rejeita` e o p ajustado;
    - o **g1** das 50 diferenças por unidade, com a ressalva quando g1 ≤ −0,5;
    - o p e o IC do bootstrap, sob a chave `bootstrap`, rotulados "a convenção da seção 5.2.1, anticonservadora com 5 bases (A4.4)";
  - **as premissas:**
    - a `G-PESA`: o limite inferior do IC95 pelo t > 0,01, no braço de cada módulo;
    - a `G-ELEGIVEL` e a `G-ELEGIVEL-EP`;
    - os `episodios_por_vida`;
  - **o `metodo`:** o teste do Holm, o IC, o rótulo do bootstrap, o limiar do g1 e a ressalva;
  - **a `leitura`:** a de A4.6, com `nao_demonstra`;
  - **os descritivos, sem gate:**
    - a `D-1`, a `D-2` e a `DX-5`;
    - os `descritivos`, os `descritivos_conserto` e o `descritivo_11_celulas`;
    - a `comparacao_com_o_a`, com o A11;
  - **o `custo`:** o CPU por vida.

**4. Os critérios e a leitura** (os de A4.2, A4.4.6 e A4.6, sem critério novo e sem mudar limiar):
- **O G-MVP é só estimativa, sem "passa" nem "falha".** O limiar de 0,8 fica como referência e não muda. A posição do IC sai numa das três
  frases de A4.2, e nenhuma delas aprova ou reprova o gate.
- **A avaliação não demonstra a prontidão do protótipo:** sem "passa", o gate de prontidão da seção 5.6 não é cumprido, e o A segue como
  o cérebro do MVP.
- **Ela também não demonstra a superioridade modular:** a comparação com o A11 segue descritiva, e os contrastes medem módulos, não
  arquiteturas.
- **O G-ABLA-PERS é inconclusivo por premissa,** qualquer que seja o p. A G-PESA da persistência falhou nas três rodadas do #427 e no
  piloto (0,0033).
- **Um contraste rejeitado pelo Holm** lê-se: "o módulo pesa no sentido previsto dentro do M3\*, nestas condições". Não se lê como "o
  modular vai à comida pelos próprios módulos" nem como superioridade da arquitetura.
- **A ressalva do g1:**
  - com g1 ≤ −0,5, o contraste sai com a frase de A4.4.6, e uma rejeição nele não é lida como confirmação;
  - a ressalva não muda o p, o Holm nem a decisão gravada;
  - **o limiar −0,5 segue PROPOSTO** (A4.9).
- **A G-MOD tem o erro de família a 5,9 % sob a nula global** (A4.4.4, pela simulação com as 6 unidades do piloto), registrado como
  ressalva da família. A G-MOD é secundária (seção 5.2).
- **O G-MECANISMO continua binário:** com um teste de mecanismo falhando, nenhuma vida roda. Antes da run, rodam:
  - o `tests/test_digibrain_mecanismo.py` e o `tests/test_digibrain_vidas.py`;
  - os gabaritos (o G2);
  - os testes da reavaliação.

**5. A configuração, o comando e os artefatos:**
- **a config:** `experiments/configs/v2_digibrain_prototipo/reavaliacao.json`, com o sha256
  `d1d99106929b873ac86d4e55c4689f877df021af876c156f12113eaa69c5325e`. Em relação à do piloto do conserto, mudam só a `descricao`, a
  `fase` (`reavaliacao`), as bases e o K, e um teste confere isso;
- **o commit:** este registro é o commit da run, a partir de `93523e3`. A run sai dele, na worktree `v2-modular-reavaliacao`, com a
  árvore limpa, e o `meta.json` grava o `git_head`, o `git_limpo` e os sha da config e do plano;
- **os outros sha256** (os de `93523e3`, que este commit não toca):
  - o orquestrador, `experiments/run_v2_digibrain_prototipo.py`: `ef24a83bbcd78ef40dd08b9972a00b8768704d0cc9c6f9ee64369e3030faa446`;
  - `digilab/config.py`, com os valores do #428: `a370c02422e83195651644a526217c5dd42b0cc2606e1cb807157c531c6c5dc8`;
  - `digilab/engine.py`: `48ba51ce6426eb98a726c05e07f3a57992ae0f328f517740ec36f1c3db153630`;
  - `digilab/metrics.py`, com a A4.7: `abf142c4f8f1eca2f81922614a20cea994894b417e56fe9902873a9efb56bf98`;
  - o `resultado.json` do piloto do conserto, de onde saem o K e o `g_apr` do M4-con:
    `7824b337242435db264c26b50edfbc281fcc1a32b8a1eb55918ee4070834c294`;
- **o comando** (4 processos; trocado de 8 em 2026-10-28, pela decisão do Matheus sobre a máquina, no registro
  "DIGIBRAIN-MODULAR-REAVALIACAO-PROCESSOS"; o número de processos não muda nenhuma vida nem o resultado):
  `python experiments/run_v2_digibrain_prototipo.py --config experiments/configs/v2_digibrain_prototipo/reavaliacao.json --processos 4`;
- **o tempo estimado:**
  - pelo custo do piloto, 15 273 s de CPU (A4.5);
  - o piloto rodou as 864 vidas dele em 313 s de parede, com 8 processos. Na mesma proporção, as 7 200 levariam cerca de 45 min com
    8; com 4 processos, cerca do dobro;
  - com a análise, cerca de 1 h 30 min;
- **os artefatos** (`artifacts_v2_digibrain_prototipo/reavaliacao/`):
  - **`meta.json`:** a config, os sha256, o commit, a árvore limpa, as 50 unidades, os braços, os inatos, o `adendo_4` (o K e o `g_apr`),
    o sha do `resultado.json` do piloto, o `g_apr_m4_con` e o tempo;
  - **`medidas.json`:** as medidas de cada vida. Pelo piloto (7,5 kB por vida), cerca de 54 MB: acima do aviso de 50 MB do GitHub, abaixo
    do limite de 100 MB;
  - **`resultado.json`:** o item 3;
  - **`vidas/<braço>/<dono>_<lugar>_<semente>.jsonl`:** o log de cada vida, **fora do git**, na worktree `v2-modular-reavaliacao`. Pelo
    piloto, cerca de 0,5 GB;
- **o que vai para o git:** os três `.json`, com `git add -f` (a pasta `artifacts_*/` é ignorada), como no piloto. O RESULTADO ganha uma
  seção com os números deles, e a leitura vai ao Matheus;
- **se a pasta já existir,** a run se recusa a gravar por cima (seção 6.4).

**6. A trava** (em `tests/test_digibrain_reavaliacao.py`; nenhum destes testes roda vida):
- **`test_a_trava_exige_o_adendo_4_aprovado_no_cabecalho`:** o `exigir_adendo_aprovado` aceita o plano atual. Ele falha alto com o status
  PROPOSTO, sem a linha do status ou com o APROVADO numa subseção;
- **`test_a_trava_vale_na_config_da_reavaliacao`:** com o plano trocado por um PROPOSTO, o `modo_da_config` da reavaliação falha;
- **`test_a_config_registrada_da_reavaliacao_segue_o_plano`:**
  - a config registrada dá o modo `reavaliacao`;
  - o K e o `g_apr` do M4-con saem 10 e 1 923;
  - as unidades saem 50, nas cinco bases;
  - só a `descricao`, a `fase`, as bases e o K diferem da config do piloto;
- **`test_a_reavaliacao_recusa_sementes_fora_de_66101_a_66505`:** a run recusa, com `SementeSemPlano`:
  - as bases do piloto do conserto e as da 64xxx;
  - uma base a menos, uma a mais ou uma trocada;
  - uma semente dos testes misturada às da faixa;
- **`test_a_reavaliacao_recusa_outro_k_ou_outros_dias_e_nao_grava_por_cima`:** a run recusa K = 9 e 13 dias, e não grava numa pasta que
  já existe;
- **a única exceção:** as sementes dos testes, sozinhas (101 a 505), dão o modo `fumaca`. A fumaça exige `--saida` e não lê os adendos
  nem o K da reavaliação. É o encanamento dos testes, nunca resultado.

## Adendo 5: a avaliação da L-2, a intenção suspensa no cochilo (2026-10-29, worker D, Claude Code, Opus 5.5; APROVADO pelo Matheus em 2026-10-29)

**Status: APROVADO pelo Matheus em 2026-10-29,** com o piloto: a faixa 67101 a 67505; o piloto de 10 unidades em 67101 e 67202, com
K = 5, só para medir o rho; e a regra do K escrita antes do piloto (A5.8). Um K acima de 100 volta ao Matheus com o custo, e as margens
ficam como a LS-7 decidiu. Registrado antes de qualquer vida. O piloto roda depois de o Gerente conferir o orquestrador, e a avaliação
depois do K fixado (A5.9). No máximo 4 processos (a máquina), da `main` limpa, uma vez.

**De onde vem:** a seção 7 da `docs/ESPEC_LONGE_L2_DIGIBRAIN_MODULAR.md` (o #436). O Matheus aprovou as decisões LS-1 a LS-7 como
recomendadas em 2026-10-29. Este adendo repete o desenho e os critérios da seção 7 **sem mudá-los**, e acrescenta só o que a espec deixou
para o plano: a faixa, o número de unidades, as medidas na forma de medir e o que falta antes da primeira vida.

**O que este adendo não afirma:** que a L-2 conserta o longe, que o modular supera o A, ou que algum cérebro está pronto (a espec,
seção 8).

### A5.1 O desenho (a espec, seção 7.1, como está)

- **A pergunta:** a suspensão diminui as buscas quebradas no longe e aumenta o fechamento por episódio no longe, sem piorar o comedouro,
  o perto e o corpo?
- **Os braços:**
  - **o par primário:** o M3\* de hoje (o "M3" de `SUBCHAVES_CONSERTO`, com o `cheiro_inato` e a `intencao_cheiro`) e o **M3\*+S** (o
    mesmo, com a `intencao_suspensa`);
  - **o par descritivo** (LS-6): o M0 do conserto e o **M0+S**, sem critério;
  - **o A11 não entra.**
- **As células:** as 12 de hoje (4 donos × comedouro, perto e longe), 14 dias, orçamento de 16 por dia.
- **O pareamento:** as quatro vidas de cada unidade e célula têm a mesma semente e o mesmo genoma (a regra E3, como na reavaliação).
- **Os valores:** os inatos de hoje (os do #428, que seguem PROPOSTOS), e os dois da suspensão como a LS-4 decidiu (`n_suspensa_max` = 6 e
  `lambda_retomar` = S/4). **Nenhuma calibração** (LS-4).

### A5.2 As sementes

- **A faixa: 67101 a 67505,** reservada em `experiments/bancada/faixas.py`, a pedido do Gerente em 2026-10-29. A 64xxx e a 66xxx estão
  gastas para uso confirmatório e não entram em nada, nem na conta do poder.
- **O piloto** (A5.6): as bases **67101 e 67202,** com K = 5, 10 unidades. Ele só serve para medir o rho da A5.6 e não tem leitura de
  critério.
- **A avaliação:** as bases **67303, 67404 e 67505,** com o K da regra da A5.6, uma vez.
- **As unidades:** a regra E3 (`bancada_v2.unidades_derivadas`, o prefixo do protótipo), como na reavaliação.

### A5.3 As medidas (a espec, seção 7.2, como está, e a forma de medir)

| a medida | o lugar | o papel |
|---|---|---|
| as buscas trocadas por vida, com o motivo (o reflexo, outra unidade) | os três | o mecanismo (C-L2-1) |
| as buscas que acabam em "expirou", por vida | os três | o mecanismo (C-L2-1) e o pet preso (C-L2-4) |
| a taxa de fechamento **por episódio** (a do G-MVP-EP) | o longe | o efeito (C-L2-2) |
| a taxa de fechamento **por ração** | o longe | relatada, com o teto de cerca de 0,13; sem critério (PL-3) |
| as taxas por episódio e por ração | o comedouro e o perto | não pode piorar (C-L2-3) |
| a exaustão e a privação de fome (S-5) | os três | não pode piorar (C-L2-3) |
| as S-1 a S-4 e a S-6 | os três | o pet preso (C-L2-4) e a leitura |
| as M-L2 e M-L3 da L0, refeitas | o longe | descritivas |

**A forma de medir,** pelo registro da decisão, que com a subchave grava a `suspensa` e o `retomou` em cada motivo e o `n_susp` em cada
fim de uma intenção que já foi suspensa (o commit `f20618e`):
- **as buscas trocadas:** os fins `trocou` de `comer/cheiro`, com o motivo pelo `reflexo` da decisão (a forma do M-L2 da L0). No M3\*+S, o
  reflexo não troca uma busca, e a troca por ele deve cair a 0;
- **as expiradas:** os fins `expirou` de `comer/cheiro`;
- **a medida do C-L2-1:** por unidade, no longe, as buscas trocadas mais as expiradas, por vida;
- **S-1:** o `n_susp` de cada intenção suspensa ao acabar, e a fração dos fins dela em `expirou`;
- **S-2:** os fins das intenções com o `n_susp` (as que voltaram ou acabaram suspensas) contra os das sem ele (as nunca suspensas): a
  fração em `meta` ou `achou`;
- **S-3:** nas decisões com o `retomou`, o andado líquido até o fim da intenção, em direção à ração madura mais próxima na retomada (a
  forma do M-L3);
- **S-4:** a fração das retomadas com um reflexo nas 2 decisões seguintes;
- **S-5:** a `exaustao` e a `privacao` que o orquestrador já grava;
- **S-6:** nas decisões com o `retomou`, a fração com a sonda `persistencia_decidiu`.

### A5.4 Os critérios (a espec, seção 7.3, copiados como estão)

Os limiares são os da espec, **PROPOSTOS, SEM FONTE.** A LS-7 os aprovou para esta avaliação sem mudá-los, e nada aqui os ajusta.

| # | o critério | passa se |
|---|---|---|
| **C-L2-1** | o mecanismo age | no longe do par primário, as buscas trocadas mais as expiradas, por vida, caem pelo menos à metade da média do M3\*, e o IC95 da diferença pareada fica abaixo de 0 |
| **C-L2-2** | o longe por episódio | o limite inferior do IC95 da diferença pareada (M3\*+S − M3\*) na taxa por episódio do longe fica acima de 0 |
| **C-L2-3** | não piorar | no comedouro e no perto, por episódio e por ração, o limite inferior do IC95 da diferença pareada fica acima de −0,03; e, nos três lugares, o limite superior da diferença na exaustão e na privação (S-5) fica abaixo de +0,02 |
| **C-L2-4** | o pet não fica preso | no M3\*+S, no máximo 25 % das suspensões acabam em "expirou" (S-1), e a fração de retomadas que acaba em meta ou achou não fica mais de 0,10 abaixo da fração das buscas nunca suspensas (S-2) |

**Como se leem juntos** (a espec, como está):
- o C-L2-3 é uma conjunção: todas as comparações dele têm de passar, sem correção de multiplicidade (a regra da interseção-união; SEM FONTE
  verificada no repositório);
- a suspensão só segue para o jogo com o C-L2-1, o C-L2-3 e o C-L2-4. O C-L2-2 diz se o longe melhorou; sem ele, a leitura volta ao
  Matheus com a regra da parte (a) (a espec, seção 4).

**A análise:** a diferença pareada por unidade (a média das 4 células do lugar), com o IC95 pelo t sobre as unidades, como no adendo 4.
Estimativa com intervalo; nada além dos critérios.

### A5.5 A regra da parte (a), aplicada na leitura (a espec, seção 4, como está)

A parte (a) só volta ao Matheus, como espec própria, se:
- a (b) passa o C-L2-1 e o C-L2-3; **e**
- no longe do M3\*+S, as buscas trocadas por outra unidade, com ração a menos de R, ficam acima do dobro das do comedouro no mesmo braço;
  **e**
- o C-L2-2 não mostra melhora no longe.

### A5.6 O número de unidades e o poder

**O poder** sai de `experiments/poder_l2_digibrain.py`, gravado em `artifacts_v2_digibrain_prototipo/l2/poder.json` (sha256
`4cb10998…c504`). Ele só lê o `medidas.json` do piloto do conserto (as 6 unidades do M3\*, 65303 a 65505):
- **a dispersão** entre as unidades vem do piloto;
- **o desvio da diferença pareada** depende da correlação rho entre as duas vidas do par, que nenhum artefato mede: a tabela dá rho = 0;
  0,5 e 0,8;
- **a conta** é a aproximação normal do t não central, um pouco otimista com poucas unidades.

**O que a tabela mostra:**
- **o C-L2-2** depende do efeito, que não se conhece. Com K = 30 e rho = 0,5, o poder é 0,53 para +0,03, 0,93 para +0,05 e 1,0 para
  +0,10;
- **o C-L2-3 tem uma comparação que domina:** a privação no longe, com a margem +0,02 e o desvio de 0,092 entre as unidades. O poder dela,
  com K = 50, é 0,18 (rho = 0), 0,32 (rho = 0,5) e 0,67 (rho = 0,8). Com K = 100, é 0,33, 0,58 e 0,93;
- **a conjunção do C-L2-3,** pelo produto das 10 comparações tratadas como independentes (uma aproximação): com K = 50, de 0,04 a 0,67;
  com K = 100, de 0,27 a 0,93.

**A regra do K** (PROPOSTA, SEM FONTE):
1. **o piloto** (A5.2) roda os quatro braços nas 12 células. O rho de cada medida do C-L2-3 é a correlação, entre as unidades, do M3\* e
   do M3\*+S no lugar. Ele só serve para esta conta;
2. **o K da avaliação** é o menor da grade (10, 20, 30, 50, 100 e 200 unidades) em que o poder da conjunção do C-L2-3, com os rho do
   piloto, chega a 0,8, arredondado para cima ao múltiplo de 3: as unidades se dividem por igual entre as três bases da avaliação;
3. **se nenhum K da grade chega a 0,8,** ou o K passa de 100, o K volta ao Matheus com o custo em vidas antes de rodar. As margens não
   mudam: a LS-7 as fixou.

**O custo:** cerca de 3,2 s de CPU por vida (a reavaliação). O piloto tem 480 vidas (4 braços × 12 células × 10 unidades), cerca de 7 min
com 4 processos. A avaliação tem 48 × K vidas: com K = 50, 2 400, cerca de 35 min; com K = 100, 4 800, cerca de 70 min.

### A5.7 O que falta antes da primeira vida

- **O orquestrador:**
  - os braços M3\*+S e M0+S;
  - as fases `l2_piloto` e `l2_avaliacao`, com as bases da A5.2;
  - a trava, que exige o adendo 5 APROVADO pelo Matheus no cabeçalho (a `exigir_adendo_aprovado` de A4.7);
  - as medidas da A5.3;
  - a análise da A5.4 e a regra do K da A5.6.
  Isso vai num commit próprio, com testes nas sementes dos testes, antes do piloto, para o Gerente conferir.
- **A autorização do Matheus** para o piloto e, depois do K, para a avaliação, uma vez.
- **Os testes de mecanismo,** de vidas, os gabaritos (o do modular e o do conserto) e a suíte, antes de cada run.

### A5.8 A regra do K, por extenso (2026-10-29, worker D; escrita antes do piloto)

A regra da A5.6, sem mudá-la, na forma que o orquestrador aplica (`experiments/run_v2_digibrain_l2.py`). Os números são PROPOSTOS, SEM
FONTE, e não mudam depois do piloto.

**O piloto** (a fase `l2_piloto`):
- as bases 67101 e 67202, com K = 5 por base: 10 unidades;
- os quatro braços (M3\*, M3\*+S, M0 e M0+S) nas 12 células, 14 dias: 480 vidas;
- ele só serve para esta regra. Nenhum critério é lido nele, e os números dele não são evidência;
- ele recusa as sementes da avaliação (67303 a 67505) e as de qualquer outra fase.

**As 10 comparações do C-L2-3,** do par primário (M3\*+S − M3\*):
- a taxa por episódio e a por ração, no comedouro e no perto (4 comparações), com a margem −0,03;
- a exaustão e a privação, nos três lugares (6 comparações), com a margem +0,02.

**A conta, comparação por comparação:**
1. **O valor da unidade:** a média das 4 vidas do lugar (uma por dono), em cada braço, como na A5.4.
2. **Do piloto:**
   - o desvio entre as unidades em cada braço, σ(M3\*) e σ(M3\*+S);
   - o rho, a correlação de Pearson entre os valores das 10 unidades nos dois braços;
   - o desvio da diferença pareada, σ_d = raiz(σ(M3\*)² + σ(M3\*+S)² − 2 · rho · σ(M3\*) · σ(M3\*+S)). É o desvio das 10 diferenças pareadas,
     e o orquestrador confere que as duas contas dão o mesmo.
   - Se um dos σ é 0, o rho fica sem valor, e vale o σ_d das diferenças.
3. **O poder,** com o efeito verdadeiro 0 (não piorar): 1 − Φ(t(K − 1; 0,975) − (|margem| / σ_d) · raiz(K)). É a função `poder` de
   `experiments/poder_l2_digibrain.py`, a aproximação normal do t não central. Com σ_d = 0, o poder é 1.
4. **A conjunção:** o produto dos 10 poderes (as comparações tratadas como independentes; uma aproximação, como na A5.6).

**O K:**
- **a grade,** em unidades: 12, 21, 30, 51, 102 e 201 (a da A5.6, arredondada para cima ao múltiplo de 3, as três bases da avaliação);
- **o K é o menor da grade com a conjunção ≥ 0,8.** Por base, K / 3: 4, 7, 10, 17, 34 ou 67;
- **se o K é 102 ou 201, ou se nenhum K da grade chega a 0,8,** o K volta ao Matheus com o custo em vidas (48 por unidade) e em tempo,
  antes de rodar. A avaliação não roda;
- **as margens não mudam** (a LS-7).

**O que o piloto grava** (`artifacts_v2_digibrain_prototipo/l2/piloto/`): o `meta.json`, o `medidas.json` e o `resultado.json`. Este
último traz, por comparação, o σ dos dois braços, o rho, o σ_d e o poder em cada K da grade; e traz a conjunção e o K da regra (ou "volta
ao Matheus").

**A5.9, o K fixado:** depois do piloto, o K da regra entra no plano numa subseção "### A5.9 O K da avaliação", num commit próprio, antes da
avaliação. A fase `l2_avaliacao` recusa rodar:
- sem o `resultado.json` do piloto;
- sem a A5.9;
- com a A5.9 diferente do K do piloto;
- com o K da config diferente do da A5.9;
- ou com o piloto dizendo "volta ao Matheus", a não ser que a A5.9 traga o K aprovado por ele.

### A5.9 O K da avaliação (2026-10-29; o Matheus, com o worker D)

**K fixado: 450 unidades** (150 por base, nas bases 67303, 67404 e 67505), aprovado pelo Matheus em 2026-10-29.

**O porquê:**
- **o piloto** (a seção 11 do RESULTADO) não dá um K na grade da A5.8. A conjunção do C-L2-3 chega a 0,634 com K = 201, e o K volta ao
  Matheus;
- **o K = 450 está fora da grade.** Com os σ_d do piloto, a conjunção é **0,93**. O menor múltiplo de 3 com 0,8 seria o 297 (0,80);
- **a folga:** o σ_d da privação no longe, que domina a conjunção, vem de 10 unidades. Com ele 20 % maior, a conjunção cai a 0,82 com
  K = 450, e a 0,65 com K = 297. O Matheus escolheu o 450 por essa folga;
- **as margens ficam como a LS-7 decidiu** (−0,03 nas taxas, +0,02 no corpo).

**O custo:** 21 600 vidas (48 por unidade). Pelo tempo de parede do piloto (0,61 s por vida com 4 processos), são cerca de 3,7 h.
- **As vidas** (cerca de 1,6 GB) ficam fora do git, como na reavaliação.
- **O `medidas.json`** inteiro teria cerca de 203 MB, acima do limite do GitHub. A avaliação o grava em 12 partes (por braço e lugar),
  com o sha256 de cada parte num índice (`medidas_indice.json`).

**A fonte dos números:** `experiments/k_fixado_l2_digibrain.py`, gravado em `artifacts_v2_digibrain_prototipo/l2/k_fixado.json`. Ele só lê
o piloto e refaz a conjunção da grade, conferida contra a do `resultado.json` dele.

**A trava:** a fase `l2_avaliacao` só aceita este K porque esta subseção diz "aprovado pelo Matheus". Sem isso, um K fora da regra é
recusado.
