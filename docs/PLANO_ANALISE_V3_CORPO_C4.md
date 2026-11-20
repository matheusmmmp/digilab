# Plano de análise V3: a validação do teto baixo (CORPO C4)

**Status: APROVADO pelo Matheus em 2026-11-20** ("Aprovo todas", na sessão da CORPO, sobre as D-C4-2 a D-C4-12 desta versão, com as
recomendações). Esta é a versão com a primária de bem-estar que ele decidiu, o "Tempo bem". A direção é dele ("Levar o DTB à C4", o
CHECKPOINT da C3). **As D-C4-1 a D-C4-12 estão DECIDIDAS.** Nenhuma vida desta run existe. A faixa 107001…107800 foi aprovada pela
coordenadora, e a entrada dela no `faixas.py` vai com o código.

**O que aconteceu com a primeira versão:** em 2026-11-20 o Matheus respondeu "Aprovo todas" à versão que tinha a taxa por episódio como
primária. No mesmo dia, respondeu na Gerência "Sim, decidir antes" (a medida primária antes do plano da C4) e, perguntado na sessão da
CORPO qual das duas valia, "Decidir a medida antes". Aquela aprovação não valeu para esta versão; a que vale é a de cima, dada
depois do replay do "Tempo bem" e do plano reescrito.

## 0. A trava e o que já foi visto

**A trava:** o orquestrador recusa a run sem a palavra APROVADO neste status, como na C2 e na C3.

**O que já foi visto antes deste plano:**
- **A run da C3** (#1035, faixa 106001…106400, o `docs/RESULTADO_V3_CORPO_C3.md`): o DTB, a ponte da D com teto em C/2, saiu em "ganho"
  pela regra de lá (a taxa por episódio +0,120 [+0,105; +0,135], nenhuma das oito guardas reprova, o S2 passa). O DTL, o teto no limiar,
  saiu em "perda", quase igual à D.
- **A célula que sobra:** com o aleatório no comedouro, a saúde do DTB ainda cai −0,048 [−0,058; −0,037]. A guarda da saúde dos donos que
  deixam faltar comida passa porque é a média de seis células.
- **O replay do "Tempo bem"** (2026-11-20, `artifacts_v3_corpo/c3_tempo_bem/`, sem vida nova): as 4 800 vidas do CTRL e do DTB da C3
  refeitas e conferidas contra o log gravado. A fração é calculável em todas, e nenhuma vida fica em 0 ou em 1. Nas 12 células, DTB − CTRL
  dá +0,062 [+0,058; +0,066] (seção 5.3).
- **O diagnóstico da bola** (o replay R-b, #1038): nos pares, a bola nunca entra no raio da visão do pet. A guarda S1 não mede nada ali.
  Nas vidas de um pet no `longe_fixo`, a bola é chutada (96 chutes em 40 vidas do CTRL da C3).
- **O incoerente no comedouro** sai igual ao atencioso em 799 de 800 vidas da C3: as 12 células têm 11 distintas.

**A C3 escolheu o braço olhando os dois tetos, e o replay do "Tempo bem" foi feito sobre as mesmas vidas. Nenhum dos dois vale como
validação.** Este plano não calibra nenhum número neles: o teto é o mesmo T_B, os tamanhos são os mesmos, e os limiares do "Tempo bem" são
os das duas medidas que já existiam. O que eles dão a este plano é a escolha do braço, a pergunta da célula do aleatório e os
desvios-padrão para a conta da precisão.

## 1. A pergunta e as hipóteses, escritas antes

**A pergunta:** em sementes novas, o pet com o DTB passa mais tempo bem do que o pet de hoje, sem perder saúde nem forrageio?

**Hipóteses:**
- **H1, a primária:** DTB − CTRL no "Tempo bem" é "> 0", nas 12 células e nas 11 distintas.
- **H2, as guardas:** nenhuma reprova (seção 6).
- **H3, a célula do aleatório no comedouro:** a saúde do DTB continua abaixo da do CTRL nessa célula ("< 0"), como na C3. A previsão do
  plano é, portanto, **"confirma com ressalva"** (seção 6).

## 2. Os braços

| braço | a ponte da falta de combustível (abaixo de C/4) |
|---|---|
| **CTRL** | sobe o cansaço em 500 por tick, como hoje |
| **DTB** | sobe a fome em até 500 por tick, só até a fome química chegar a T_B = 225 000 (C/2); a regra é a da C3: `min(500, max(0, T_B − fome))` |

- **O T_B = 225 000 não muda.** Continua PROPOSTO e SEM FONTE. Se a C4 confirmar, passar a DECIDIDO é do Matheus.
- **A D e o DTL ficam fora** (D-C4-3). A D já saiu igual em três runs (#1002, #1012 e #1035), e o DTL saiu em "perda".
- **Nenhum teto novo entra.** Uma validação não explora.

## 3. As células e as unidades

As da C3: as 12 células da C4 do modular (os 4 donos × o comedouro, o longe e o `longe_fixo`), 200 sementes independentes (200 bases,
k = 1, derivação `digibrain_prototipo`), 14 dias e orçamento 16. Cada unidade dá o mesmo pet e o mesmo mundo aos dois braços.

## 4. A run

| item | valor |
|---|---|
| bloco I | 2 braços × 12 células × 200 unidades = **4 800 vidas** |
| bloco II | 2 braços × 500 pares, o instrumento da C3 (SOCIAL_PAR A0, só VIVO, 5 dias); 500 pares pela conta da seção 5.3 (D-C4-5) |
| faixa | **107001…107800, aprovada pela coordenadora em 2026-11-20** (D-C4-7): as bases 107001…107200 para o bloco I e as 107301…107800 (prefixo `corpo_par`) para o bloco II. A entrada no `faixas.py` vai no PR do código |
| custo | cerca de 1 h a 1 h 40 min com 4 processos: a C2 fez 9 600 vidas em 2 h 6 min, e a C3, com a máquina dividida, em 3 h 4 min. Os 1 000 pares somam cerca de 9 min (400 pares levaram 3 min 29 s na C3) |
| processos | no máximo 4, uma run de pesquisa por vez |
| disco | o worker confere o espaço livre no `D:` antes de soltar a run (piso de 10 GB, SEM FONTE; a pasta crua da C3 ocupou 0,7 GB). No fim, empacota, confere os `.tar.gz` contra as pastas e apaga as pastas |

A run roda **uma vez**. Nada se ajusta olhando para ela. A fumaça usa as sementes dos testes.

## 5. A ficha da run (os quatro itens do planejamento de 2026-11-19)

### 5.1 O que as vidas gravadas já respondem, e por que não bastam

- **Já respondem:** qual teto escolher (a C3), por que a D reprova (o diagnóstico da C2.5), o que o teto muda em cada dono (a seção 3.2 do
  resultado da C3), por que a bola não é chutada nos pares (o R-b), e que o "Tempo bem" é calculável e separa os dois braços (o replay).
- **Não respondem:** se o DTB é melhor fora das sementes em que ele foi escolhido. A C3 comparou dois tetos e ficou com o que passou; a
  leitura da célula do aleatório e o número do "Tempo bem" foram vistos depois, nas mesmas vidas. Nenhum replay tira isso: a validação
  pede sementes que a escolha não viu.
- **O que ainda cabe em replay, sem vida nova, e não bloqueia a C4:** os episódios de fome a mais do DTB (17,5 por vida contra 14,8 da D) e
  a causa de o incoerente sair igual ao atencioso no comedouro (o R-c).

### 5.2 A contagem dos eventos da premissa

**Nas vidas da C3** (o replay do "Tempo bem", 4 800 vidas): cada vida tem 1 344 decisões nos dias 1 a 14, e o "Tempo bem" sai em todas.
Nenhuma vida fica em 0 nem em 1 (o piso e o teto da medida). O nível mais alto é o do atencioso no comedouro (CTRL 0,899; DTB 0,949).

**Nas sementes dos testes,** contados em 2026-11-20, antes da run, com o código da C3 no modo de fumaça: as bases 101, 202, 303, 404 e
505 (k = 1), 14 dias, as 12 células, 20 vidas por braço e lugar; os pares, 5 por braço, 5 dias. Os chutes foram contados à parte, nas
mesmas sementes (a soma do `brincou_com_bola` das decisões do motor). São sementes de teste: nada aqui é resultado.

| evento | de que medida é a premissa | CTRL | DTB | o piso na run (SEM FONTE; D-C4-10, aceito em 2026-11-20) |
|---|---|---|---|---|
| vidas com o "Tempo bem" em 0 ou em 1 | a primária | 0 de 2 400 (na C3) | 0 de 2 400 (na C3) | no máximo 5 % das vidas em cada braço |
| episódios de fome por vida, `longe_fixo` | a guarda da taxa por episódio | 13,3 (mínimo 1; nenhuma vida sem episódio) | 15,8 (mínimo 1; nenhuma sem) | média ≥ 8 por vida em cada braço, e no máximo 2 % das vidas sem episódio |
| fração dos ticks com a ponte cortada pelo teto | o braço ser diferente do CTRL e da D | 0 | comedouro 0,25; longe 0,47; `longe_fixo` 0,42 (mínimo numa vida 0,06) | média ≥ 0,10 em cada lugar |
| pares em que a janela do reencontro cabe | o S2 | 5 de 5 | 5 de 5 | ≥ 90 % dos pares em cada braço |
| chutes por vida, `longe_fixo` | o descritivo dos chutes | 3,2 (64 em 20 vidas; 16 vidas com chute) | 2,25 (45 em 20 vidas; 14 com chute) | no CTRL, média ≥ 1 por vida e ≥ 50 % das vidas com chute |
| chutes por vida, comedouro | o descritivo dos chutes | 0 em 20 vidas | 0 em 20 vidas | nenhum: ali o descritivo sai vazio, e o resultado diz isso |

- **Os números da C3, ao lado** (sementes de pesquisa, já lidas): a ponte cortada em 0,27 dos ticks no comedouro, 0,47 no longe e 0,37 no
  `longe_fixo`; a janela do reencontro coube em 100 de 100 pares por braço; 96 chutes em 40 vidas do CTRL no `longe_fixo` (o R-b).
- **Uma premissa que não se cumpre** deixa a medida dela "inconclusiva por premissa". Na primária, isso faz a leitura da C4
  "indeterminado".
- **Visto nesta contagem, antes da run:** nas 20 vidas do `longe_fixo`, o DTB chutou menos que o CTRL (45 contra 64). Por unidade, a
  diferença é −0,95 chute por vida, com dp 2,3 em 5 unidades, e uma base (a 101) carrega quase tudo. Com 5 unidades isso não é teste. Fica
  escrito porque é o que o descritivo dos chutes vai mostrar ou desmentir.

### 5.3 A precisão, calculada antes

A meia largura do IC95 de DTB − CTRL com n = 200 unidades, pelo desvio-padrão do mesmo contraste nas vidas da C3. O "Tempo bem" vem do
replay (`artifacts_v3_corpo/c3_tempo_bem/resumo.json`); as outras, do `artifacts_v3_corpo/c3/resultado.json` e do `medidas.json`.

| medida | DTB − CTRL na C3 | dp | meia largura com n = 200 | δ | cabe em δ? |
|---|---|---|---|---|---|
| **"Tempo bem", 12 células (a primária)** | +0,062 [+0,058; +0,066] | 0,030 | 0,004 | 0,032 | sim |
| **"Tempo bem", 11 células distintas** | +0,063 [+0,059; +0,068] | 0,033 | 0,005 | 0,032 | sim |
| "Tempo bem", comedouro | +0,030 [+0,028; +0,032] | 0,015 | 0,002 | 0,032 | sim |
| "Tempo bem", longe | +0,073 [+0,065; +0,081] | 0,057 | 0,008 | 0,032 | sim |
| "Tempo bem", `longe_fixo` | +0,083 [+0,074; +0,093] | 0,068 | 0,009 | 0,032 | sim |
| a taxa por episódio, `longe_fixo` | +0,120 [+0,105; +0,135] | 0,107 | 0,015 | 0,032 | sim |
| saúde, 12 células | +0,051 [+0,044; +0,058] | 0,053 | 0,007 | 0,032 | sim |
| saúde, o relapso e o aleatório | +0,007 [−0,002; +0,015] | 0,060 | 0,008 | 0,032 | sim |
| saúde, o aleatório no comedouro (a célula da H3) | −0,048 [−0,058; −0,037] | 0,075 | 0,010 | 0,032 | sim |
| saúde, o relapso no longe (a célula mais larga) | +0,096 [+0,060; +0,133] | 0,261 | 0,036 | 0,032 | **não** |
| S2, o tempo até o reencontro (100 pares) | −2,34 [−4,53; −0,15] | 11,02 | 2,19 | 1,069 | **não** |

- **A primária cabe com folga.** Com 200 unidades, a meia largura esperada é 0,004, um oitavo de δ.
- **O que pede as 200 unidades são as guardas** (a taxa por episódio e a saúde por célula), não a primária.
- **O comedouro é o lugar em que o DTB ganha menos** (+0,030). Na C3 a diferença ficou dentro de δ: a classe ali foi "≈ 0", com o sinal
  positivo.
- **O S2 não cabe com 100 pares.** A meia largura só desce abaixo de δ (10 % do nível do CTRL, 1,069 decisão na C3) com cerca de 420
  pares. **Por isso o plano propõe 500 pares** (meia largura esperada de 0,97), ao custo de uns 9 min (D-C4-5).
- **A célula do relapso no longe** tem a meia largura acima de δ; ali a leitura por célula pode sair "indeterminado", o que não decide nada.
- **Os chutes por vida** não têm desvio-padrão de DTB − CTRL em nenhuma run anterior. Por isso entram como descritivo (D-C4-4).

### 5.4 O corpo e os donos

- **O corpo:** o CTRL é o corpo de hoje (a ponte no cansaço). O DTB é o corpo de hoje com a `CONFIG_ACOPLAMENTO_CORPO_LIGADA` (a D) e a
  `CONFIG_TETO_FOME_BAIXO` (o teto em C/2). O resto é igual: o reflexo do sono, a digestão e o metabolismo não mudam.
- **O cérebro:** o modular com a memória (o REL da C4 do modular), o das runs da C2 e da C3.
- **Os donos distintos em cada lugar, de fato:**

| lugar | donos nominais | donos distintos | por quê |
|---|---|---|---|
| comedouro | 4 | **3** | o incoerente sai igual ao atencioso (799 de 800 vidas na C3) |
| longe | 4 | 4 | as vidas do incoerente diferem das do atencioso; a rng do lugar leva o nome do dono na semente |
| `longe_fixo` | 4 | 4 | idem |

## 6. As medidas e a regra de leitura, escritas antes

**O contraste:** DTB − CTRL, pareado por unidade, com o t (`orq.contraste_t`) e as classes da A6.6.

**A primária, o "Tempo bem"** (a D-MP-1 do `docs/registro/2026-11.md`, decidida pelo Matheus em 2026-11-20; a forma exata é a D-C4-11):
- **O que é:** a fração das decisões da vida, nos dias 1 a 14, em que o pet está sem privação e sem exaustão
  (`digilab.metrics.tempo_bem_nas_decisoes`).
- **As duas regras são as das medidas de hoje:** sem privação é fome, higiene e energia em 0,15 ou mais (a do
  `privacao_nas_decisoes`); sem exaustão é energia em 0,25 ou mais (a do `exaustao_nas_decisoes`). Nenhum limiar novo entra.
- **Por unidade:** a média do "Tempo bem" nas células, e DTB − CTRL dessa média.
- **O teste:** p unilateral para DTB − CTRL > 0, com α = 0,025, e a classe com δ = 0,032 (SEM FONTE; é o δ das runs anteriores, levado
  da taxa por episódio para esta fração).
- **Onde:** nas 12 células e nas 11 distintas. **A primária só passa se sair "> 0" nas duas** (D-C4-9).

**As guardas, vinculantes** (D-C4-12):
- **a saúde,** as duas da C3: a saúde média dos dias 8 a 14, nas 12 células e nas 6 células do relapso e do aleatório; reprova com "< 0";
- **a taxa por episódio de fome no `longe_fixo`,** que era a primária e agora não pode piorar; reprova com "< 0";
- **o "Tempo bem" por lugar** (comedouro, longe e `longe_fixo`); reprova com "< 0". É o que impede a média das 12 células de esconder
  uma piora num lugar, como a da D no comedouro;
- **o S2,** o tempo até o reencontro nos pares; reprova com "> 0".

**A saúde por célula (D-C4-2):** DTB − CTRL na saúde média, em cada uma das 6 células do relapso e do aleatório, com a mesma classe.
Uma célula em "< 0" **não reprova o braço**, mas muda a leitura para "confirma com ressalva" e vai nomeada ao Matheus.

**A leitura da C4:**

| leitura | a primária (12 e 11 células) | as guardas | a saúde por célula |
|---|---|---|---|
| **confirma** | "> 0" nas duas, p ≤ 0,025 | nenhuma reprova | nenhuma das 6 células em "< 0" |
| **confirma com ressalva** | "> 0" nas duas, p ≤ 0,025 | nenhuma reprova | alguma célula em "< 0" |
| **não confirma** | "> 0" nas duas, p ≤ 0,025 | alguma reprova | qualquer |
| **não confirma** | "≈ 0" ou "< 0" em alguma das duas, ou "> 0" com p > 0,025 | qualquer | qualquer |
| **indeterminado** | "indeterminado" em alguma das duas, sem "≈ 0" nem "< 0" na outra | qualquer | qualquer |

**As premissas** (seção 5.2): se alguma não se cumpre na run, a medida que depende dela sai "inconclusiva por premissa", e não "passa".

**O descritivo, sem teste:**
- **a privação e a exaustão** dos dias 8 a 14, por lugar: as seis guardas da C3, agora ao lado, para comparar com ela;
- **o "Tempo bem" dos dias 8 a 14** e **por célula;**
- **por dono,** a saúde, a privação, a exaustão e as refeições por dia, como na seção 3.2 do resultado da C3;
- **a decomposição da privação** e **a fração dos ticks com a ponte no teto;**
- **os chutes por vida** (D-C4-4): nas vidas de um pet do bloco I, por lugar, com DTB − CTRL e o IC95. Não é guarda. Nos pares, a bola
  sai da leitura;
- **a comparação com a C3,** medida a medida: o número da C4 ao lado do da C3.

## 7. Os artefatos

Em `artifacts_v3_corpo/c4/`: `resultado.json`, `medidas.json` (em `.gz` se passar de 100 MB), `pares.json`, `vidas.tar.gz`,
`pares.tar.gz` e `meta.json`, com o sha256 de cada um, do plano, do orquestrador e das configs.

**As medidas sem o relógio (D-C4-8):** o tempo de cada vida (`vida_cpu` e `vida_parede`) sai do `medidas.json` e vai para um arquivo
próprio, o `custos.json`. Assim o `medidas.json` de uma réplica sai igual byte a byte.

## 8. A implementação, depois da aprovação

- **Nenhuma mudança no corpo nem no web.** As chaves da D e do teto já existem (#1024), desligadas no jogo. A métrica do "Tempo bem" já
  está no `digilab/metrics.py`, com teste (veio com o replay).
- **O orquestrador:** um arquivo próprio, o `experiments/run_v3_corpo_c4.py`, que importa as peças da C3, para o `run_v3_corpo_c3.py`
  ficar intacto (o sha256 dele está no `meta.json` da C3). Muda: os dois braços, a primária e as guardas da seção 6, a saúde por célula,
  os chutes por vida (a soma do `brincou_com_bola` das decisões do motor, o evento que o R-b contou), as premissas da seção 5.2 e o
  `custos.json`.
- **O pré-registro:** a seção `PR-CORPO-C4` do `docs/PREREGISTRO.md` entra antes da run, com o link para este plano no commit aprovado.
- **A ordem:** este plano aprovado na `main`, a faixa reservada, o código num PR próprio, a fumaça, o `pre_run`, e só então a run. Nenhuma
  vida antes disso.

## 9. A ordem do programa

- **"Confirma":** segue a C5, a síntese e a especificação. Ligar o DTB no jogo é uma decisão à parte, do Matheus, depois da C5.
- **"Confirma com ressalva":** volta ao Matheus com a célula nomeada. Ele decide se a ressalva é aceitável, se pede outra mudança, ou se o
  corpo fica como está.
- **"Não confirma" ou "indeterminado":** o resultado negativo fica registrado, e o corpo fica o de hoje. A run não se repete.

## 10. As decisões

Cada uma com a recomendação e o custo de errar.

- **D-C4-1 (DECIDIDA pelo Matheus em 2026-11-20: "Levar o DTB à C4", repassada pelo coordenador), a direção:** levar o DTB à C4.
- **D-C4-2 (DECIDIDA pelo Matheus em 2026-11-20, "Aprovo todas": a opção 1, a ressalva), como ler a célula do aleatório no comedouro.** As três opções eram:
  1. **a ressalva (recomendada):** a guarda da saúde continua a média das seis células, e a saúde por célula entra como uma leitura à
     parte, que não reprova mas muda o veredito para "confirma com ressalva";
  2. **a guarda por célula:** qualquer das 6 células em "< 0" reprova. Se a C3 se repetir (−0,048, além de δ), o desfecho previsto é
     "não confirma", e a run quase não teria o que decidir;
  3. **uma tolerância por célula:** reprova só abaixo de um corte. Qualquer corte seria escolhido já sabendo o −0,048 da C3.
  - **Por que a 1:** a célula não some na média, e nenhum número é escolhido depois de olhar.
  - **O custo de errar:** com a 1, um "confirma com ressalva" ainda pede uma decisão sua depois da run. Com a 2, o DTB cai por uma célula
    em que o pet já vive mal no CTRL (saúde 0,419). Com a 3, o número não tem fonte e foi visto antes.
  - **Um dado novo do replay:** nessa célula o "Tempo bem" do DTB é igual ao do CTRL (−0,001 [−0,004; +0,002]). A saúde cai sem o tempo em
    privação subir. Por isso a primária sozinha não enxerga essa célula, e a leitura por célula continua necessária.
- **D-C4-3 (DECIDIDA pelo Matheus em 2026-11-20, "Aprovo todas", com a recomendação), a D e o DTL fora da run.** Recomendação: fora. Só o CTRL e o DTB, e a run custa a metade.
  - **O custo de errar:** a C4 não mostra, nas mesmas sementes, o DTB contra a D. Essa comparação fica só na C3 (descritiva).
- **D-C4-4 (DECIDIDA pelo Matheus em 2026-11-20, "Aprovo todas", com a recomendação), a bola.** Recomendação: tirar o S1 dos pares, como recomenda o R-b (#1038), e levar os chutes por vida de um pet,
  por lugar, como descritivo.
  - **Por que não como guarda:** não há desvio-padrão de DTB − CTRL para os chutes em nenhuma run anterior.
  - **O custo de errar:** se o DTB reduzir o brincar com a bola, isso aparece no descritivo e vai a você, mas não muda o veredito.
- **D-C4-5 (DECIDIDA pelo Matheus em 2026-11-20, "Aprovo todas", com a recomendação), 500 pares no bloco II.** Recomendação: 500. Com 100, o S2 tende a sair "indeterminado" (seção 5.3).
  - **O custo de errar:** cerca de 9 min de máquina e 400 bases a mais na faixa.
- **D-C4-6 (DECIDIDA pelo Matheus em 2026-11-20, "Aprovo todas", com a recomendação), os tamanhos do bloco I:** os da C3, com 200 unidades, 14 dias e δ = 0,032 (SEM FONTE). A precisão cabe (seção 5.3).
  - **O custo de errar:** a primária caberia com menos unidades; as 200 ficam pelas guardas. A célula do relapso no longe pode sair
    "indeterminado" na leitura por célula.
- **D-C4-7 (DECIDIDA pelo Matheus em 2026-11-20, "Aprovo todas", com a recomendação), a faixa:** 700 bases novas (200 e 500), pedidas ao coordenador depois da aprovação, e na tabela antes da run.
- **D-C4-8 (DECIDIDA pelo Matheus em 2026-11-20, "Aprovo todas", com a recomendação), o relógio fora do `medidas.json`.** Recomendação: sim, num `custos.json`.
  - **O custo de errar:** sem isso, toda réplica "diverge" pelos tempos, como a da C4 do modular.
- **D-C4-9 (DECIDIDA pelo Matheus em 2026-11-20, "Aprovo todas", com a recomendação), as 12 células e as 11 distintas.** Recomendação: a primária tem de sair "> 0" nas duas; as guardas usam as 12, com
  as 11 ao lado.
  - **O custo de errar:** exigir as duas é mais duro que exigir só as 12. Na C3 as duas saíram quase iguais (+0,062 e +0,063).
- **D-C4-10 (DECIDIDA pelo Matheus em 2026-11-20, "Aprovo todas", com a recomendação), os pisos das premissas** da seção 5.2: 5 % de vidas no piso ou no teto do "Tempo bem", 8 episódios por vida, 2 % de
  vidas sem episódio, 0,10 dos ticks no teto, 90 % dos pares com a janela e, para os chutes, 1 por vida e 50 % das vidas. Todos
  SEM FONTE, escolhidos abaixo do que a contagem e a C3 mostraram. Recomendação: aceitar.
  - **O custo de errar:** um piso alto demais deixa "inconclusiva por premissa" uma medida que estava boa; um baixo demais deixa passar
    uma medida que quase não tem evento.
- **D-C4-11 (DECIDIDA pelo Matheus em 2026-11-20, "Aprovo todas", com a recomendação), a forma exata do "Tempo bem".** A decisão diz "a fração das decisões sem privação e sem exaustão, nos dias 1 a
  14". Este plano a escreve assim: os limiares de hoje (0,15 e 0,25), a média das células por unidade, δ = 0,032 e α = 0,025 unilateral.
  Recomendação: aceitar.
  - **O custo de errar:** o δ foi pensado para a taxa por episódio e não tem fonte para esta fração. Na C3, o efeito (+0,062) é quase o
    dobro dele, e o IC é estreito; um δ menor não mudaria a classe das 12 células, mas mudaria a do comedouro (+0,030, hoje "≈ 0").
- **D-C4-12 (DECIDIDA pelo Matheus em 2026-11-20, "Aprovo todas", com a recomendação), as guardas.** A decisão nomeia duas: a saúde dos dias 8 a 14 e a taxa por episódio. Este plano propõe mais duas: o
  "Tempo bem" por lugar e o S2. Recomendação: as quatro.
  - **Por quê:** a D reprovou por um lugar só, o comedouro, e a média das 12 células esconderia isso. O S2 é a única medida do substrato
    social.
  - **O custo de errar:** mais guardas dão mais chances de "não confirma" por acaso. Com menos, uma piora localizada passa.

**O que este plano não afirma:** nada sobre o jogo web; nada sobre outro teto; nada sobre a E e a C5 com o teto; nada sobre o social além
do substrato.
