# Plano de análise V3: a validação do teto baixo (CORPO C4)

**Status: PROPOSTO. Espera a decisão da medida primária de bem-estar.** A direção é do Matheus ("Levar o DTB à C4", o CHECKPOINT da C3,
repassada pelo coordenador em 2026-11-20). Em 2026-11-20 ele respondeu "Aprovo todas" a este plano na sessão da CORPO e, na Gerência,
"Sim, decidir antes" à pergunta de decidir a medida primária de bem-estar antes de aprovar o plano da C4. Perguntado qual valia, respondeu
**"Decidir a medida antes"**. Por isso a aprovação está suspensa: a D-C4-1 fica DECIDIDA, e as D-C4-2 a D-C4-10 ficam ABERTAS até a medida
ser decidida e a seção 6 ser conferida contra ela. Nenhuma vida desta run existe, e a faixa não foi reservada.

**O que a decisão da medida pode mudar aqui:** a seção 6 (o que é o primário e o que é guarda), a D-C4-2 (a leitura por célula) e, se a
medida nova tiver outro desvio-padrão, a conta da precisão da seção 5.3. O resto do plano não depende dela.

## 0. A trava e o que já foi visto

**A trava:** o orquestrador recusa a run sem a palavra APROVADO neste status, como na C2 e na C3.

**O que já foi visto antes deste plano:**
- **A run da C3** (#1035, faixa 106001…106400, o `docs/RESULTADO_V3_CORPO_C3.md`): o DTB, a ponte da D com teto em C/2, saiu em "ganho"
  (F +0,120 [+0,105; +0,135], nenhuma das oito guardas reprova, o S2 passa). O DTL, o teto no limiar, saiu em "perda", quase igual à D.
- **A célula que sobra:** com o aleatório no comedouro, a saúde do DTB ainda cai −0,048 [−0,058; −0,037]. A guarda da saúde dos donos que
  deixam faltar comida passa porque é a média de seis células.
- **O diagnóstico da bola** (o replay R-b, #1038, aberto): nos pares, a bola nunca entra no raio da visão do pet. A guarda S1 não mede
  nada ali. Nas vidas de um pet no `longe_fixo`, a bola é chutada (96 chutes em 40 vidas do CTRL da C3).
- **O incoerente no comedouro** sai igual ao atencioso em 799 de 800 vidas da C3: as 12 células têm 11 distintas.

**A C3 escolheu o braço olhando os dois tetos. Por isso ela não vale como validação.** Este plano não calibra nenhum número nela: o teto é
o mesmo T_B, os tamanhos são os mesmos, e a regra de leitura é a da C3. O que a C3 dá a este plano é a escolha do braço, a pergunta da
célula do aleatório e os desvios-padrão para a conta da precisão (seção 5.3).

## 1. A pergunta e as hipóteses, escritas antes

**A pergunta:** em sementes novas, o DTB repete o "ganho" da C3?

**Hipóteses:**
- **H1, o forrageio:** DTB − CTRL na taxa por episódio de fome no `longe_fixo` é "> 0".
- **H2, o bem-estar:** nenhuma das oito guardas da C3 reprova, e o S2 passa.
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
| faixa | **não reservada; o pedido espera a aprovação** (D-C4-7): 200 bases para o bloco I e 500 para o bloco II (prefixo `corpo_par`) |
| custo | cerca de 1 h a 1 h 40 min com 4 processos: a C2 fez 9 600 vidas em 2 h 6 min, e a C3, com a máquina dividida, em 3 h 4 min. Os 1 000 pares somam cerca de 9 min (400 pares levaram 3 min 29 s na C3) |
| processos | no máximo 4, uma run de pesquisa por vez |
| disco | o worker confere o espaço livre no `D:` antes de soltar a run (piso de 10 GB, SEM FONTE; a pasta crua da C3 ocupou 0,7 GB). No fim, empacota, confere os `.tar.gz` contra as pastas e apaga as pastas |

A run roda **uma vez**. Nada se ajusta olhando para ela. A fumaça usa as sementes dos testes.

## 5. A ficha da run (os quatro itens do planejamento de 2026-11-19)

### 5.1 O que as vidas gravadas já respondem, e por que não bastam

- **Já respondem:** qual teto escolher (a C3), por que a D reprova (o diagnóstico da C2.5), o que o teto muda em cada dono (a seção 3.2 do
  resultado da C3) e por que a bola não é chutada nos pares (o R-b).
- **Não respondem:** se o "ganho" do DTB se repete fora das sementes em que ele foi escolhido. A C3 comparou dois tetos e ficou com o que
  passou; a leitura da célula do aleatório foi escrita depois de olhar. Nenhum replay das vidas da C3 tira isso: a validação pede
  sementes que a escolha não viu.
- **O que ainda cabe em replay, sem vida nova, e não bloqueia a C4:** os episódios de fome a mais do DTB (17,5 por vida contra 14,8 da D) e
  a causa de o incoerente sair igual ao atencioso no comedouro (o R-c).

### 5.2 A contagem dos eventos da premissa, nas sementes dos testes

Contados em 2026-11-20, antes da run, com o código da C3 no modo de fumaça: as bases 101, 202, 303, 404 e 505 (k = 1), 14 dias, as 12
células, 20 vidas por braço e lugar; os pares, 5 por braço, 5 dias. Os chutes foram contados à parte, nas mesmas sementes (a soma do
`brincou_com_bola` das decisões do motor). São sementes de teste: nada aqui é resultado, e nenhuma leitura de braço sai daqui.

| evento | de que medida é a premissa | CTRL | DTB | o piso na run (PROPOSTO, SEM FONTE; D-C4-10) |
|---|---|---|---|---|
| episódios de fome por vida, `longe_fixo` | o F | 13,3 (mínimo 1; nenhuma vida sem episódio) | 15,8 (mínimo 1; nenhuma sem) | média ≥ 8 por vida em cada braço, e no máximo 2 % das vidas sem episódio |
| fração dos ticks com a ponte cortada pelo teto | o braço ser diferente do CTRL e da D | 0 | comedouro 0,25; longe 0,47; `longe_fixo` 0,42 (mínimo numa vida 0,06) | média ≥ 0,10 em cada lugar |
| pares em que a janela do reencontro cabe | o S2 | 5 de 5 | 5 de 5 | ≥ 90 % dos pares em cada braço |
| chutes por vida, `longe_fixo` | o descritivo dos chutes | 3,2 (64 em 20 vidas; 16 vidas com chute) | 2,25 (45 em 20 vidas; 14 com chute) | no CTRL, média ≥ 1 por vida e ≥ 50 % das vidas com chute |
| chutes por vida, comedouro | o descritivo dos chutes | 0 em 20 vidas | 0 em 20 vidas | nenhum: ali o descritivo sai vazio, e o resultado diz isso |

- **Os números da C3, ao lado** (sementes de pesquisa, já lidas): a ponte cortada em 0,27 dos ticks no comedouro, 0,47 no longe e 0,37 no
  `longe_fixo`; a janela do reencontro coube em 100 de 100 pares por braço; 96 chutes em 40 vidas do CTRL no `longe_fixo` (o R-b).
- **Uma premissa que não se cumpre** deixa a medida dela "inconclusiva por premissa". No F, isso faz a leitura da C4 "indeterminado".
- **Visto nesta contagem, antes da run:** nas 20 vidas do `longe_fixo`, o DTB chutou menos que o CTRL (45 contra 64). Por unidade, a
  diferença é −0,95 chute por vida, com dp 2,3 em 5 unidades, e uma base (a 101) carrega quase tudo. Com 5 unidades isso não é teste. Fica
  escrito porque é o que o descritivo dos chutes vai mostrar ou desmentir. Por esse dp, a meia largura com 200 unidades ficaria perto
  de 0,3 chute por vida; a conta é grosseira, por vir de 5 unidades.

### 5.3 A precisão, calculada antes

A meia largura do IC95 de DTB − CTRL, pelo desvio-padrão do mesmo contraste na C3 (`artifacts_v3_corpo/c3/resultado.json` e
`medidas.json`), com n = 200 unidades:

| medida | dp na C3 | meia largura com n = 200 | δ | cabe em δ? |
|---|---|---|---|---|
| F, a taxa por episódio no `longe_fixo` | 0,107 | 0,015 | 0,032 | sim |
| privação, comedouro | 0,022 | 0,003 | 0,032 | sim |
| privação, longe | 0,103 | 0,014 | 0,032 | sim |
| privação, `longe_fixo` | 0,091 | 0,013 | 0,032 | sim |
| privação, 12 células | 0,046 | 0,006 | 0,032 | sim |
| exaustão, `longe_fixo` | 0,047 | 0,007 | 0,032 | sim |
| exaustão, 12 células | 0,023 | 0,003 | 0,032 | sim |
| saúde, 12 células | 0,053 | 0,007 | 0,032 | sim |
| saúde, o relapso e o aleatório | 0,060 | 0,008 | 0,032 | sim |
| saúde, o aleatório no comedouro (a célula da H3) | 0,075 | 0,010 | 0,032 | sim |
| saúde, o relapso no longe (a célula mais larga) | 0,261 | 0,036 | 0,032 | **não** |
| S2, o tempo até o reencontro (100 pares) | 11,02 | 2,19 | 1,069 | **não** |

- **O bloco I cabe com 200 unidades,** como na C3. Só a célula do relapso no longe tem a meia largura acima de δ; ali a leitura por célula
  pode sair "indeterminado", e isso não decide nada (seção 6).
- **O S2 não cabe com 100 pares.** Com o dp da C3, a meia largura só desce abaixo de δ (10 % do nível do CTRL, 1,069 decisão na C3) com
  cerca de 420 pares. **Por isso o plano propõe 500 pares** (meia largura esperada de 0,97), ao custo de uns 9 min (D-C4-5). Com 100
  pares, o desfecho provável do S2 seria "indeterminado", que passa sem mostrar nada.
- **Os chutes por vida** não têm desvio-padrão de DTB − CTRL em nenhuma run anterior. Por isso eles entram como descritivo, e não como
  guarda (D-C4-4).

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

A leitura oficial usa as 12 células, como a C3, para a regra da validação ser a da escolha. As 11 células distintas vão ao lado, como
sensibilidade (D-C4-9).

## 6. As medidas e a regra de leitura, escritas antes

**O contraste:** DTB − CTRL, pareado por unidade, com o t (`orq.contraste_t`) e as classes da A6.6, com δ = 0,032 (SEM FONTE, o da C2 e da
C3).

**F, o primário:** a taxa de fechamento por episódio de fome no `longe_fixo`. O p é unilateral para DTB − CTRL > 0, com α = 0,025. Não há
Holm: só um braço é testado.

**B, o bem-estar, vinculante** (as oito guardas da C3, sem mudança):
- **a privação:** no comedouro, no longe, no `longe_fixo` e nas 12 células; reprova com "> 0";
- **a exaustão:** no `longe_fixo` e nas 12 células; reprova com "> 0";
- **a saúde:** a saúde média na janela dos dias 8 a 14, nas 12 células e nas 6 células do relapso e do aleatório; reprova com "< 0".

**S2, o substrato social, vinculante:** o tempo até o reencontro nos pares; reprova com "> 0".

**A saúde por célula (nova, D-C4-2):** DTB − CTRL na saúde média, em cada uma das 6 células do relapso e do aleatório, com a mesma classe.
Uma célula em "< 0" **não reprova o braço**, mas muda a leitura para "confirma com ressalva" e vai nomeada ao Matheus.

**A leitura da C4:**

| leitura | F | as oito guardas e o S2 | a saúde por célula |
|---|---|---|---|
| **confirma** | "> 0", p ≤ 0,025 | nenhuma reprova | nenhuma das 6 células em "< 0" |
| **confirma com ressalva** | "> 0", p ≤ 0,025 | nenhuma reprova | alguma célula em "< 0" |
| **não confirma** | "> 0", p ≤ 0,025 | alguma reprova | qualquer |
| **não confirma** | "≈ 0", "< 0", ou "> 0" com p > 0,025 | qualquer | qualquer |
| **indeterminado** | "indeterminado" | qualquer | qualquer |

**As premissas** (seção 5.2): se alguma não se cumpre na run, a medida que depende dela sai "inconclusiva por premissa", e não "passa".

**O descritivo, sem teste:**
- **por dono,** a saúde, a privação, a exaustão e as refeições por dia, como na seção 3.2 do resultado da C3;
- **a decomposição da privação** e **a fração dos ticks com a ponte no teto;**
- **os chutes por vida** (D-C4-4): nas vidas de um pet do bloco I, por lugar, com DTB − CTRL e o IC95. Não é guarda. Nos pares, a bola
  sai da leitura;
- **as 11 células distintas,** com as guardas refeitas, ao lado das oficiais;
- **a comparação com a C3,** medida a medida: o número da C4 ao lado do da C3.

## 7. Os artefatos

Em `artifacts_v3_corpo/c4/`: `resultado.json`, `medidas.json` (em `.gz` se passar de 100 MB), `pares.json`, `vidas.tar.gz`,
`pares.tar.gz` e `meta.json`, com o sha256 de cada um, do plano, do orquestrador e das configs.

**As medidas sem o relógio (D-C4-8):** o tempo de cada vida (`vida_cpu` e `vida_parede`) sai do `medidas.json` e vai para um arquivo
próprio, o `custos.json`. Assim o `medidas.json` de uma réplica sai igual byte a byte.

## 8. A implementação, depois da aprovação

- **Nenhuma mudança no `digilab/` nem no web.** As chaves da D e do teto já existem (#1024), desligadas no jogo.
- **O orquestrador:** um arquivo próprio, o `experiments/run_v3_corpo_c4.py`, que importa as peças da C3, para o `run_v3_corpo_c3.py`
  ficar intacto (o sha256 dele está no `meta.json` da C3). Muda: os dois braços, a saúde por célula, os chutes por vida (a soma do
  `brincou_com_bola` das decisões do motor, o evento que o R-b contou), as premissas da seção 5.2, a leitura da seção 6 e o `custos.json`.
- **O pré-registro:** a seção `PR-CORPO-C4` do `docs/PREREGISTRO.md` entra antes da run, com o link para este plano no commit aprovado.
- **A ordem:** este plano na `main`, a faixa reservada, o código num PR próprio, a fumaça, o `pre_run`, e só então a run. Nenhuma vida
  antes disso.

## 9. A ordem do programa

- **"Confirma":** segue a C5, a síntese e a especificação. Ligar o DTB no jogo é uma decisão à parte, do Matheus, depois da C5.
- **"Confirma com ressalva":** volta ao Matheus com a célula nomeada. Ele decide se a ressalva é aceitável, se pede outra mudança, ou se o
  corpo fica como está.
- **"Não confirma" ou "indeterminado":** o resultado negativo fica registrado, e o corpo fica o de hoje. A run não se repete.

## 10. As decisões

Cada uma com a recomendação e o custo de errar.

- **D-C4-1 (DECIDIDA pelo Matheus em 2026-11-20: "Levar o DTB à C4", repassada pelo coordenador), a direção:** levar o DTB à C4.
- **D-C4-2 (ABERTA; o "Aprovo todas" de 2026-11-20 está suspenso até a medida primária), como ler a célula do aleatório no comedouro.** As três opções eram:
  1. **a ressalva (recomendada):** a regra vinculante continua a da C3 (a média das seis células), e a saúde por célula entra como uma
     leitura à parte, que não reprova mas muda o veredito para "confirma com ressalva";
  2. **a guarda por célula:** qualquer das 6 células em "< 0" reprova. Se a C3 se repetir (−0,048, além de δ), o desfecho previsto é
     "não confirma", e a run quase não teria o que decidir;
  3. **uma tolerância por célula:** reprova só abaixo de um corte. Qualquer corte seria escolhido já sabendo o −0,048 da C3.
  - **Por que a 1:** a validação fica com a mesma regra da run que escolheu o braço, e a célula não some na média.
  - **O custo de errar:** com a 1, um "confirma com ressalva" ainda pede uma decisão sua depois da run. Com a 2, o DTB cai por uma célula
    em que o pet já vive mal no CTRL (saúde 0,419). Com a 3, o número não tem fonte e foi visto antes.
- **D-C4-3 (ABERTA; o "Aprovo todas" de 2026-11-20 está suspenso até a medida primária), a D e o DTL fora da run.** Recomendação: fora. Só o CTRL e o DTB, e a run custa a metade.
  - **O custo de errar:** a C4 não mostra, nas mesmas sementes, o DTB contra a D. Essa comparação fica só na C3 (descritiva).
- **D-C4-4 (ABERTA; o "Aprovo todas" de 2026-11-20 está suspenso até a medida primária), a bola.** Recomendação: tirar o S1 dos pares, como recomenda o R-b (#1038), e levar os chutes por vida de um pet,
  por lugar, como descritivo.
  - **Por que não como guarda:** não há desvio-padrão de DTB − CTRL para os chutes em nenhuma run anterior, e uma guarda nova decidiria a
    validação sem ter sido vista na escolha.
  - **O custo de errar:** se o DTB reduzir o brincar com a bola, isso aparece no descritivo e vai a você, mas não muda o veredito.
- **D-C4-5 (ABERTA; o "Aprovo todas" de 2026-11-20 está suspenso até a medida primária), 500 pares no bloco II.** Recomendação: 500. Com 100, o S2 tende a sair "indeterminado" (seção 5.3).
  - **O custo de errar:** cerca de 9 min de máquina e 400 bases a mais na faixa.
- **D-C4-6 (ABERTA; o "Aprovo todas" de 2026-11-20 está suspenso até a medida primária), os tamanhos do bloco I:** os da C3, com 200 unidades, 14 dias e δ = 0,032 (SEM FONTE). A precisão cabe (seção 5.3).
  - **O custo de errar:** nenhum previsto; a célula do relapso no longe pode sair "indeterminado" na leitura por célula.
- **D-C4-7 (ABERTA; o "Aprovo todas" de 2026-11-20 está suspenso até a medida primária), a faixa:** 700 bases novas (200 e 500), pedidas ao coordenador, e na tabela antes da run.
- **D-C4-8 (ABERTA; o "Aprovo todas" de 2026-11-20 está suspenso até a medida primária), o relógio fora do `medidas.json`.** Recomendação: sim, num `custos.json`.
  - **O custo de errar:** sem isso, toda réplica "diverge" pelos tempos, como a da C4 do modular.
- **D-C4-9 (ABERTA; o "Aprovo todas" de 2026-11-20 está suspenso até a medida primária), as 12 células oficiais, com as 11 distintas ao lado.** Recomendação: manter as 12, pela mesma regra da C3.
  - **O custo de errar:** o atencioso pesa duas vezes nas médias do comedouro. A sensibilidade mostra se isso muda a leitura.

- **D-C4-10 (ABERTA; escrita depois do "Aprovo todas", nunca aprovada), os pisos das premissas** da seção 5.2: 8 episódios por vida, 2 % de vidas sem
  episódio, 0,10 dos ticks no teto, 90 % dos pares com a janela e, para os chutes, 1 por vida e 50 % das vidas. Todos PROPOSTOS e SEM
  FONTE, escolhidos abaixo do que a contagem e a C3 mostraram. Recomendação: aceitar.
  - **O custo de errar:** um piso alto demais deixa "inconclusiva por premissa" uma medida que estava boa; um baixo demais deixa passar
    uma medida que quase não tem evento. O código da run só entra depois desta decisão.

**O que este plano não afirma:** nada sobre o jogo web; nada sobre outro teto; nada sobre a E e a C5 com o teto; nada sobre o social além
do substrato.
