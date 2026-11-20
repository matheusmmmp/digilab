# Plano de análise V3: o teto baixo no pet do jogo (CORPO V1-a)

**Status: PROPOSTO.** Nenhuma vida desta run existe, e nenhuma roda antes da aprovação do Matheus, da faixa e do código. A direção é
dele: no CHECKPOINT da C5, à D-EC-1 da [ESPEC_CORPO_V1.md](ESPEC_CORPO_V1.md), a resposta foi "Medir no v38 antes" (2026-11-20). As
D-V1A-1 a D-V1A-9 (seção 10) estão abertas.

Escrito em 2026-11-20 por Claude Code (Fable 5.2, sessão lateral da CORPO), no branch `v3-corpo-v1-plano`, empilhado no #1049. A tarefa
é a [TAREFA_V3_CORPO.md](TAREFA_V3_CORPO.md); a síntese que motiva a medida é a [SINTESE_CORPO.md](SINTESE_CORPO.md), seção 8.

## 0. A trava e o que já foi visto

**A trava:** o orquestrador recusa a run sem a palavra APROVADO neste status, como na C2, na C3 e na C4.

**O que já foi visto antes deste plano:**
- **A run da C4** (#1047, faixa 107001…107800, o `docs/RESULTADO_V3_CORPO_C4.md`): no pet da bancada, o DTB saiu em "confirma com
  ressalva". DTB − CTRL no "Tempo bem" deu +0,062 [+0,058; +0,067] nas 12 células, nenhuma guarda reprovou, e a saúde caiu na célula do
  aleatório no comedouro (−0,049).
- **O replay da fome** (#1053): na média o pet com o DTB tem menos fome; no comedouro, com o relapso e o aleatório, tem mais.
- **Uma contagem nas sementes dos testes,** feita para este plano em 2026-11-20 (seção 5.2): 120 vidas do pet v38, nas bases 101, 202,
  303, 404 e 505. São sementes de teste e 5 unidades: **nada dela é resultado.** Ela mostra que as premissas têm eventos e dá uma
  ideia do tamanho do efeito, e essa ideia está escrita na seção 1 como a previsão do plano.

**Este plano não calibra nenhum número na contagem.** O teto, os tamanhos, a margem e os pisos são os da C4. A regra de leitura é a
da C4, escrita antes de qualquer vida do pet v38 (D-V1A-5).

## 1. A pergunta e as hipóteses, escritas antes

**A pergunta:** no pet v38, o DTB ainda faz o pet passar mais tempo bem, sem perder saúde nem forrageio?

**Por que a pergunta existe:** o pet da bancada não tem o "sono que segura", o lance do dono nem o equilíbrio do cuidado. O "sono que
segura" mexe na exaustão, que é de onde veio a maior parte do ganho do DTB na C4.

**Hipóteses:**
- **H1, a primária:** DTB − CTRL no "Tempo bem" é "> 0", nas 12 células e nas 11 distintas.
- **H2, as guardas:** nenhuma reprova (seção 6).
- **H3, a célula do aleatório no comedouro:** a saúde do DTB continua abaixo da do CTRL nessa célula ("< 0"), como na C3 e na C4.

**A previsão do plano, escrita antes: "não confirma".** É o que a contagem das sementes dos testes sugere, com toda a incerteza de 5
unidades:
- **O ganho parece menor que a margem.** Nas 5 unidades, DTB − CTRL no "Tempo bem" deu +0,016 [−0,003; +0,035] nas 12 células. Com 200
  unidades, um efeito desse tamanho sai com o IC inteiro dentro de (−δ; +δ), com δ = 0,032: a classe é "≈ 0", e a regra lê "não
  confirma".
- **O pet v38 já parte de um lugar melhor.** O "Tempo bem" do CTRL foi 0,727 (0,633 na C4) e a exaustão, 0,132 (0,237 na C4). Com os
  donos que alimentam, no comedouro, o CTRL chega a 0,987: quase não há para onde subir.
- **No comedouro o sinal foi negativo:** −0,014 [−0,027; −0,001] no "Tempo bem", e −0,036 na célula do aleatório.
- **A saúde dos donos que deixam faltar comida** deu −0,042 [−0,135; +0,052]. O intervalo é largo demais para dizer algo.
- **O que as 5 unidades não excluem:** um efeito de até +0,035 nas 12 células, que sairia "> 0".

**Por que rodar mesmo assim:** a decisão foi medir. Cinco unidades de teste não são medida, e um "não confirma" com 200 unidades
encerra a V1 com um número, em vez de uma impressão.

## 2. Os braços

| braço | o pet | a ponte da falta de combustível (abaixo de C/4) |
|---|---|---|
| **CTRL38** | o pet v38 de hoje | sobe o cansaço em 500 por tick |
| **DTB38** | o pet v38 com as duas chaves do corpo | sobe a fome em até 500 por tick, só até T_B = 225 000 (C/2): `min(500, max(0, T_B − fome))` |

- **O pet v38, no Python,** é o da PET_VIVO (`experiments/pv2.py`, `fabricas(..., v38=True)`): o modular com a memória, os inatos do
  E1 (`inatos_e1()`), o "sono que segura" (`CONFIG_SONO_SEGURA_LIGADA`), o lance do dono (`CONFIG_LANCE_DONO_LIGADA`), o equilíbrio do
  cuidado (`EQUILIBRIO_V38`) e o estágio de bebê nas primeiras decisões.
- **O que esse pet não tem, e o do jogo tem** (D-V1A-2): a TV, a ilha grande e a memória de 128 células. O mundo é o da bancada. É uma
  aproximação do v38, a mesma que a PET_VIVO usou na checagem dela.
- **O T_B não muda,** e continua PROPOSTO e SEM FONTE. Nenhum teto novo entra.
- **Conferido antes, nas sementes dos testes:** o CTRL38 montado para a análise refaz, byte a byte, a vida do pet v38 da PET_VIVO
  (3 vidas de 3 dias; o sha256 do log e o estado de cada decisão).

## 3. As células e as unidades

As da C4: as 12 células (os 4 donos × o comedouro, o longe e o `longe_fixo`), 200 sementes independentes (200 bases, k = 1, derivação
`digibrain_prototipo`), 14 dias e orçamento 16. Cada unidade dá o mesmo pet e o mesmo mundo aos dois braços (D-V1A-3).

## 4. A run

| item | valor |
|---|---|
| bloco I | 2 braços × 12 células × 200 unidades = **4 800 vidas** |
| bloco II, os pares | **fora** (D-V1A-4): o pet dos pares não é o v38 |
| faixa | 200 bases novas, a pedir ao coordenador depois da aprovação (D-V1A-8). A entrada no `faixas.py` vai no PR do código |
| custo | cerca de 1 h a 1 h 30 min com 4 processos. A C4 fez as 4 800 vidas em 68 min; na contagem, a vida do pet v38 custou o mesmo que a da bancada, dentro do que deu para ver com a máquina dividida |
| processos | no máximo 4, uma run de pesquisa por vez |
| disco | o orquestrador confere 10 GB livres no `D:` antes da run (o piso da C4, SEM FONTE). No fim, empacota, confere o `.tar.gz` contra a pasta e apaga a pasta |

A run roda **uma vez**. Nada se ajusta olhando para ela. A fumaça usa as sementes dos testes.

## 5. A ficha da run (os quatro itens do planejamento de 2026-11-19)

### 5.1 O que as vidas gravadas já respondem, e por que não bastam

- **Já respondem:** que o DTB melhora o "Tempo bem" no pet da bancada (a C4), de onde vem o ganho (a exaustão e a privação), e onde
  ele não melhora (o comedouro, com o relapso e o aleatório).
- **Não respondem:** o que o DTB faz no pet v38. Nenhuma vida gravada tem o pet v38 com as chaves do corpo. As vidas do pet v38 da
  PET_VIVO têm o corpo de hoje, em sementes de outra faixa e com outras medidas.
- **Nenhum replay responde:** as chaves do corpo mudam a vida desde o primeiro tick com falta de combustível. É preciso viver de novo.

### 5.2 A contagem dos eventos da premissa

**Nas sementes dos testes,** contados em 2026-11-20, antes da run: as bases 101, 202, 303, 404 e 505 (k = 1), 14 dias, as 12 células,
60 vidas por braço, com o pet v38 e a análise da C4. São sementes de teste: nada aqui é resultado.

| evento | de que medida é a premissa | CTRL38 | DTB38 | o piso na run (os da C4, D-V1A-6; todos SEM FONTE) |
|---|---|---|---|---|
| vidas com o "Tempo bem" em 0 ou em 1 | a primária | 0 de 60 | 1 de 60 | no máximo 5 % das vidas em cada braço |
| episódios de fome por vida, `longe_fixo` | a guarda da taxa por episódio | 14,6 (mínimo 1; nenhuma vida sem episódio) | 17,2 (mínimo 1; nenhuma sem) | média ≥ 8 por vida em cada braço, e no máximo 2 % das vidas sem episódio |
| fração dos ticks com a ponte cortada pelo teto | o braço ser diferente do CTRL e da D | 0 | comedouro 0,24; longe 0,44; `longe_fixo` 0,39 | média ≥ 0,10 em cada lugar |
| chutes por vida, `longe_fixo` | o descritivo dos chutes | 21,4 (95 % das vidas com chute) | 18,5 | no CTRL38, média ≥ 1 por vida e ≥ 50 % das vidas com chute |

- **Uma premissa que não se cumpre** deixa a medida dela "inconclusiva por premissa". Na primária e na da ponte no teto, isso faz a
  leitura "indeterminado". Numa guarda, a guarda não reprova nem passa, e a leitura também fica "indeterminado" (a interpretação do
  código da C4, aceita pelo Matheus em 2026-11-20).
- **O teto do "Tempo bem" está perto, e o piso não o vê.** O piso conta só as vidas em exatamente 0 ou 1. Na contagem, 21 das 120
  vidas ficaram acima de 0,99, todas dos donos que alimentam (o atencioso e o incoerente). Por isso o descritivo ganha a fração das vidas acima de 0,99 por
  célula (seção 6). A regra não muda.
- **Os chutes mudaram de tamanho.** Com o lance do dono, o pet v38 chuta cerca de 21 vezes por vida no `longe_fixo`; o da bancada
  chutava 2,5. Nas 5 unidades, o DTB38 chutou menos nas 12 células (−3,9 [−7,6; −0,2] por vida). Com 5 unidades isso não é teste;
  fica escrito porque é o que o descritivo vai mostrar ou desmentir.
- **O incoerente no comedouro** saiu igual ao atencioso também no pet v38: as 12 células têm 11 distintas.

### 5.3 A precisão, calculada antes

A meia largura esperada do IC95 de DTB − CTRL com n = 200. O desvio-padrão do pet v38 não é conhecido: a tabela traz o da C4 (200
unidades, pet da bancada) e o da contagem (5 unidades, pet v38, muito incerto).

| medida | dp na C4 | dp na contagem (5 unidades) | meia largura com n = 200, pelos dois | δ | cabe em δ? |
|---|---|---|---|---|---|
| **"Tempo bem", 12 células (a primária)** | 0,031 | 0,015 | 0,004 e 0,002 | 0,032 | sim |
| **"Tempo bem", 11 células distintas** | 0,034 | 0,017 | 0,005 e 0,002 | 0,032 | sim |
| "Tempo bem", comedouro | 0,017 | 0,010 | 0,002 e 0,001 | 0,032 | sim |
| "Tempo bem", longe | 0,057 | 0,045 | 0,008 e 0,006 | 0,032 | sim |
| "Tempo bem", `longe_fixo` | 0,074 | 0,037 | 0,010 e 0,005 | 0,032 | sim |
| a taxa por episódio, `longe_fixo` | 0,100 | 0,085 | 0,014 e 0,012 | 0,032 | sim |
| saúde, 12 células | 0,055 | 0,019 | 0,008 e 0,003 | 0,032 | sim |
| saúde, o relapso e o aleatório | 0,061 | 0,075 | 0,008 e 0,010 | 0,032 | sim |
| saúde, o aleatório no comedouro (a célula da H3) | 0,081 | 0,086 | 0,011 e 0,012 | 0,032 | sim |
| saúde, o aleatório no `longe_fixo` (a mais larga na contagem) | 0,115 | 0,221 | 0,016 e 0,031 | 0,032 | no limite |

- **A primária cabe com folga.** A meia largura esperada fica entre 0,002 e 0,004, de um oitavo a um décimo sexto de δ.
- **Isso tem uma consequência, dita antes:** com o IC tão estreito, um efeito abaixo de cerca de 0,028 sai "≈ 0", e um acima de
  cerca de 0,030 sai "> 0". A leitura da primária vai depender de onde o efeito cai em relação a δ, e não do ruído.
- **O que pede as 200 unidades são a saúde por célula e a taxa por episódio,** como na C4.

### 5.4 O corpo e os donos

- **O corpo:** o CTRL38 é o corpo de hoje (a ponte no cansaço). O DTB38 é o corpo de hoje com a `CONFIG_ACOPLAMENTO_CORPO_LIGADA` e a
  `CONFIG_TETO_FOME_BAIXO`. O resto é igual.
- **O cérebro:** o do pet v38 (seção 2), igual nos dois braços.
- **Os donos distintos em cada lugar:**

| lugar | donos nominais | donos distintos | por quê |
|---|---|---|---|
| comedouro | 4 | **3** | o incoerente sai igual ao atencioso (5 de 5 unidades na contagem, nos dois braços; 200 de 200 na C4) |
| longe | 4 | 4 | a rng do lugar leva o nome do dono na semente |
| `longe_fixo` | 4 | 4 | idem |

## 6. As medidas e a regra de leitura, escritas antes

**A regra é a da seção 6 do plano da C4, sem o S2** (D-V1A-4 e D-V1A-5). O contraste é DTB38 − CTRL38, pareado por unidade, com o t e
as classes da A6.6, com δ = 0,032 (SEM FONTE).

**A primária, o "Tempo bem"** (D-MP-1): a fração das decisões dos dias 1 a 14 sem privação (fome, higiene e energia em 0,15 ou mais) e
sem exaustão (energia em 0,25 ou mais), pela `digilab.metrics.tempo_bem_nas_decisoes`. Por unidade, a média nas células. O p é
unilateral para DTB38 − CTRL38 > 0, com α = 0,025. **A primária só passa se sair "> 0" nas 12 células e nas 11 distintas,** com o p
nas duas.

**As guardas, vinculantes:**
- **a saúde** média dos dias 8 a 14, nas 12 células e nas 6 células do relapso e do aleatório; reprova com "< 0";
- **a taxa por episódio de fome no `longe_fixo`;** reprova com "< 0";
- **o "Tempo bem" por lugar** (comedouro, longe e `longe_fixo`); reprova com "< 0".

**A saúde por célula:** DTB38 − CTRL38 em cada uma das 6 células do relapso e do aleatório. Uma célula em "< 0" não reprova o braço,
mas muda a leitura para "confirma com ressalva" e vai nomeada ao Matheus.

**A leitura:**

| leitura | a primária (12 e 11 células) | as guardas | a saúde por célula |
|---|---|---|---|
| **confirma** | "> 0" nas duas, p ≤ 0,025 | nenhuma reprova | nenhuma das 6 células em "< 0" |
| **confirma com ressalva** | "> 0" nas duas, p ≤ 0,025 | nenhuma reprova | alguma célula em "< 0" |
| **não confirma** | "> 0" nas duas, p ≤ 0,025 | alguma reprova | qualquer |
| **não confirma** | "≈ 0" ou "< 0" em alguma das duas, ou "> 0" com p > 0,025 | qualquer | qualquer |
| **indeterminado** | "indeterminado" em alguma das duas, sem "≈ 0" nem "< 0" na outra | qualquer | qualquer |

**"≈ 0" com o sinal positivo é "não confirma".** Um ganho real, mas menor que δ, não leva o DTB ao jogo por esta regra. O resultado
traz o número e o intervalo, para o Matheus ver o tamanho.

**O descritivo, sem teste:**
- **a privação e a exaustão,** dos dias 8 a 14 e da vida toda, por lugar;
- **o "Tempo bem" dos dias 8 a 14, por célula,** e a fração das vidas acima de 0,99 por célula;
- **o sono:** a fração dos ticks dormindo e os reflexos por vida. O "sono que segura" muda o que essas duas medidas querem dizer, e o
  resultado diz isso;
- **por dono,** a saúde, a privação, a exaustão e as refeições por dia;
- **a fome,** pela `fome_nas_decisoes`: a média e a fração do tempo acima de 0,5, por lugar e por célula, medidas na própria run (sem
  replay);
- **os chutes por vida** (D-V1A-7), por lugar, com DTB38 − CTRL38 e o IC95;
- **a comparação com a C4,** medida a medida: o DTB − CTRL do pet da bancada ao lado do DTB38 − CTRL38. São sementes e pets
  diferentes; o par não é um contraste.

## 7. Os artefatos

Em `artifacts_v3_corpo/v1a/`: `resultado.json`, `medidas.json` (em `.gz` se passar de 100 MB), `custos.json` (o tempo de cada vida,
fora das medidas), `vidas.tar.gz` e `meta.json`, com o sha256 de cada um, do plano, do orquestrador e da config.

## 8. A implementação, depois da aprovação

- **Nenhuma mudança no `digilab/` nem no web.** As chaves do corpo, as do pet v38 e as métricas já existem.
- **O orquestrador:** um arquivo próprio, o `experiments/run_v3_corpo_v1.py`, que importa as peças da C4 e da PET_VIVO, para o
  `run_v3_corpo_c4.py` e o `pv2.py` ficarem intactos. Muda: as fábricas (o pet v38 no motor da sonda, com as chaves do braço), a
  regra sem o S2, a fome na própria run e a fração das vidas acima de 0,99.
- **As conferências de cada vida:** o replay, o T-CENARIO-1, as do mecanismo e as do corpo do braço (as da C3). **A conferência do
  reflexo da C3 não serve ao pet v38:** ela exige os inatos da bancada e o "sono que segura" desligado. O orquestrador a troca por
  uma do pet v38: o cérebro tem os inatos do E1, o "sono que segura" ligado, o lance e o equilíbrio do cuidado, nos dois braços.
- **Os testes:** a regra de leitura caso a caso; as premissas; a trava do plano APROVADO; o pacote; a fumaça duas vezes com o
  `medidas.json` igual byte a byte; e o CTRL38 igual, byte a byte, à vida do pet v38 da PET_VIVO.
- **O pré-registro:** a seção `PR-CORPO-V1` do `docs/PREREGISTRO.md` entra antes da run, com o link para este plano no commit aprovado.
- **A ordem:** este plano aprovado na `main`, a faixa reservada, o código num PR próprio, a fumaça, o `pre_run`, e só então a run.

## 9. A ordem do programa

Pela [ESPEC_CORPO_V1.md](ESPEC_CORPO_V1.md), seção 7:
- **"Confirma":** libera a V1-b, a versão nova do pet no jogo.
- **"Confirma com ressalva":** volta ao Matheus com a célula nomeada; se ele aceitar, libera a V1-b.
- **"Não confirma" ou "indeterminado":** o resultado fica registrado, a V1 para, e o pet do jogo fica como está. A run não se repete.

## 10. As decisões

Cada uma com a recomendação e o custo de errar.

- **D-V1A-1 (PROPOSTA), rodar com a previsão de "não confirma".** A contagem sugere um ganho menor que a margem (seção 1).
  1. **Rodar assim mesmo (recomendada):** a decisão de medir já foi tomada, e 5 unidades de teste não são medida.
  2. **Não rodar:** parar a V1 aqui, com a contagem como motivo.
  - **O custo de errar:** com a 1, cerca de 1 h 20 min de máquina para um resultado que pode ser o previsto. Com a 2, o DTB sai do
    caminho do jogo por 5 unidades de teste, cujo intervalo vai até +0,035.
- **D-V1A-2 (PROPOSTA), o pet v38 do Python como o pet da medida.** Ele não tem a TV, a ilha grande nem a memória de 128 células.
  - **A recomendação:** aceitar. É o que o Python tem hoje, e é o que a PET_VIVO usou.
  - **O custo de errar:** o resultado vale para essa aproximação. Se a TV ou a ilha grande mudarem o sono ou a fome do pet, a medida
    não vê.
- **D-V1A-3 (PROPOSTA), os tamanhos:** os da C4, com 12 células, 200 unidades, 14 dias e orçamento 16.
  - **A recomendação:** aceitar. A precisão cabe (seção 5.3).
  - **O custo de errar:** a primária caberia com menos unidades; as 200 ficam pela saúde por célula.
- **D-V1A-4 (PROPOSTA), os pares fora.** O pet dos pares (o da SOCIAL_PAR A0) não tem o "sono que segura" nem o equilíbrio do cuidado.
  1. **Fora (recomendada):** o S2 sai da regra. O substrato social fica com a medida da C4, no pet dos pares de lá.
  2. **Repetir os pares da C4:** 500 pares por braço, cerca de 9 min. Só repete a C4 em sementes novas.
  3. **Um par v39:** montar os dois pets com as mecânicas do jogo. É código novo no instrumento da SOCIAL_PAR.
  - **O custo de errar:** com a 1, a V1-a não diz nada sobre o reencontro no pet do jogo. Com a 3, a V1-a passa a depender de um
    instrumento que a frente do social ainda não validou.
- **D-V1A-5 (PROPOSTA), a regra de leitura e a margem.** A regra é a da C4, com δ = 0,032, sem o S2.
  - **A recomendação:** não mudar a margem. Ela foi escrita antes, e mudar agora seria mudar depois de ver a contagem.
  - **O custo de errar:** δ = 0,032 é SEM FONTE e veio da taxa por episódio. Um ganho real de 0,02 no "Tempo bem" sai "não confirma".
    Se você achar que um ganho desse tamanho vale o jogo, a margem tem de ser decidida agora, antes da run, e a decisão fica
    registrada como tomada depois da contagem.
- **D-V1A-6 (PROPOSTA), os pisos das premissas:** os da C4 (5 % de vidas em 0 ou 1, 8 episódios por vida, 2 % de vidas sem episódio,
  0,10 dos ticks no teto; para os chutes, 1 por vida e 50 % das vidas). O piso da janela dos pares sai com os pares.
  - **A recomendação:** aceitar. A contagem cumpre todos.
  - **O custo de errar:** o piso do "Tempo bem" não vê as vidas perto de 1 (seção 5.2); elas vão no descritivo.
- **D-V1A-7 (PROPOSTA), os chutes como descritivo.** No pet v38 a bola é chutada cerca de 21 vezes por vida, e na contagem o DTB38
  chutou menos.
  - **A recomendação:** descritivo, como na C4. Não há desvio-padrão de DTB − CTRL para os chutes no pet v38 em nenhuma run.
  - **O custo de errar:** se o DTB reduzir o brincar com a bola no jogo, isso aparece no resultado e vai a você, mas não muda o
    veredito.
- **D-V1A-8 (PROPOSTA), a faixa:** 200 bases novas, pedidas ao coordenador depois da aprovação, e na tabela antes da run.
- **D-V1A-9 (PROPOSTA), o que cada leitura faz:** a seção 9. "Não confirma" ou "indeterminado" param a V1.
  - **A recomendação:** aceitar.
  - **O custo de errar:** um "indeterminado" também para a V1, sem repetir a run.

**O que este plano não afirma:** nada sobre o jogo web; nada sobre o pet v38 com a TV, a ilha grande e a memória longa; nada sobre
outro teto; nada sobre os pares e o social. Nenhuma alegação de novidade.
