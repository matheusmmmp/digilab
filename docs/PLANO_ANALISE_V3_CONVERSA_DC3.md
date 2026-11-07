# PLANO DE ANÁLISE V3 — CONVERSA_PET, DC3: a rede escolhendo falar (2026-11-07, Gerente da CONVERSA_PET, Claude Code, Opus 5.5)

**Status: APROVADO pelo Matheus em 2026-11-07 ("Aprovo todas").** **O adendo 1 (no fim do documento) foi APROVADO pelo Matheus em 2026-11-07 ("Aprovo todas")** e muda o crédito da fala e o gate antes da primeira vida. As decisões DC3-1 a DC3-9 (seção 12) DECIDIDAS, todas pela recomendação. **Nenhuma vida da faixa 79101…79505 roda antes de quatro
coisas:** este cabeçalho com a marca "APROVADO pelo Matheus"; o código da DC3a na `main` (seção 10), desligado e byte a byte; a medida da
fala em `digilab/metrics.py` com os testes dela; e o registro da run (seção 11), num commit empurrado antes da primeira vida.

**De onde vem:** a decisão DR-1 do Matheus (2026-11-06: a fala nasce da rede, a LLM só como voz), a DC-B (a intenção por regra primeiro,
a I-a, que está na `main` pela DC1; a rede escolhendo falar, a I-b, como pesquisa em seguida) e a espec
[docs/research/ESPEC_DECODIFICADOR_FALA.md](research/ESPEC_DECODIFICADOR_FALA.md), seções 3 e 6. **Este plano reusa, sem mudar,** do
[PLANO_ANALISE_V3_ACOES_NOVAS.md](PLANO_ANALISE_V3_ACOES_NOVAS.md) (APROVADO em 2026-11-05): o cenário (seção 2, o da C4), a taxa por
episódio de fome, a unidade (base, semente) e o IC95 do t, a classe de cada contraste com a margem, a G-ELEGIVEL-EP, o prefixo das unidades
e a conta de poder da guarda (seção 6 de lá, com o artefato `artifacts_v3_acoes_novas/plano_an3_poder.json`).

**O que este plano não afirma:** que o pet "quer se comunicar", que entende linguagem, que a fala parece viva ao jogador (SEM FONTE; é do
Matheus, jogando) nem que o modular supera o A. O que se mede é se unidades de fala que competem com as outras ações e aprendem pela
consequência no corpo passam a falar do que o pet precisa quando alguém escuta, e se calam quando ninguém escuta. **Nenhuma alegação de
novidade.**

## 0. O que existe hoje (os fatos que o desenho usa)

- **O `chamar_atencao`** é um dos 7 comportamentos do modular (`COMPORTAMENTOS_DIGIBRAIN`, `digilab/config.py:2500`), com uma unidade só,
  sem conteúdo (`impulso.py:102-103`). **No corpo não faz nada** (`corpo.py:387`); no mundo só emite o som "chamado" para outro pet
  (`mundo.py:1573`). O W0 inato dele puxa pela fome sem comida, pela higiene, pela solidão e pelo estresse (`config.py:2548-2549`).
- **O crédito:** o P1 só aprende com comer e brincar (`plast.py:77-94`); o P2 (hábito) dá à linha H[chamar_atencao] a soma do r_n das
  consequências no corpo da opção (`estado.py:355`, `plast.py:110-125`). **Nenhum dono reage ao chamado nas runs do modular:** os donos
  leem as necessidades (`donos.py:64-73`), e o elogio e a bronca do `julgar_acao` são tirados pelo `CanalSemEnsino`
  (`regras_mundo.py:278-293`). Os cérebros antigos davam recompensa implícita ao pedido atendido (`bandit.py:286-323`); o modular não.
- **Logo, hoje, chamar não serve para nada no corpo do modular,** e o hábito de chamar só pode cair ou ficar. Um teste de "a rede aprende a
  falar" precisa de um dono que escute.

## 1. A pergunta e as previsões, escritas antes

**A pergunta:** com a chamada dividida em unidades de fala com conteúdo (pedir comida, pedir limpeza, pedir companhia), que competem com
as outras opções e aprendem pelo P2 de hoje, **o pet passa a falar mais do que de fato precisa quando o dono atende, e menos quando o dono
não atende, sem cuidar pior de si quando ninguém escuta?**

| contraste | o que é | a previsão | o papel |
|---|---|---|---|
| **G-ESCUTA: atende − ignora, no LAB+F** | a fala pertinente por dia nos dias 8 a 14 (4.2), com o dono que atende contra o que não atende | **"> 0"** | **o gate principal** (7.2) |
| **G-COMEDOURO-DC3: LAB+F − LAB, com o dono que ignora** | a taxa por episódio de fome, no comedouro | **não "< 0"** | **a guarda** (7.3) |
| **EXT: dias 8–14 − dias 1–3, no LAB+F com o dono que ignora** | a fala por dia | **"< 0"** (a fala se apaga) | secundária, sem gate |
| **PERT: pertinência, no LAB+F** | a fração das falas cujo conteúdo é o da maior urgência | sem limiar; o inato já acopla | descritiva |

- **Por que o gate é o contraste entre os donos e não a pertinência sozinha:** o inato de cada unidade já puxa pela urgência do conteúdo
  (3.1), então a fala "acerta" a necessidade desde o primeiro dia sem aprender nada. O que só o aprendizado explica é a diferença entre um
  dono que atende e um que não: com o mesmo cérebro, a mesma semente e o mesmo inato, só a consequência muda.
- **A guarda é com o dono que ignora** porque é ali que a fala custa: cada decisão de falar tira uma decisão de comer. Com o dono que
  atende, a comida vem de fora, e uma guarda ali seria vazia.
- **O nulo plausível, escrito antes:** o P2 de hoje credita o r_n do intervalo da opção. Se o cuidado do dono cair fora do intervalo em que
  a opção de fala ainda está aberta, o crédito vai para outra opção, e o G-ESCUTA sai "≈ 0" ou "indeterminado". Isso é um resultado: diz que
  o crédito do P2 não alcança a resposta do dono, não que a ideia falhou. A conferência do crédito (seção 11) conta quantos atendimentos
  caem dentro do intervalo.

## 2. O desenho

- **O cenário:** o da AN4 (o da C4), sem mudança: o `CONFIG_MUNDO_MVP`, o corpo do v11, o pet sozinho, **14 dias, orçamento de 16 por dia,**
  morte desligada, só o **comedouro** (4 donos). O `longe_fixo` não roda (DC3-1): a pergunta é da fala, e a guarda é perto da ração.
- **Os braços (DC3-2):**

| braço | o que é | o papel |
|---|---|---|
| **LAB** | `config_do_braco("REL", conserto=True)`, o pet de teste de hoje | o controle |
| **LAB+F** | o LAB com a subchave nova `fala_unidades` ligada (3.1) | o braço novo |

- **O dono (DC3-3), cruzado com os 4 donos sem ensino:**
  - **ignora:** o dono de hoje, como está;
  - **atende:** o mesmo dono, mais uma regra: quando a ação do pet na decisão é uma unidade de fala e há orçamento no passo, o dono dá,
    no mesmo passo, o cuidado do conteúdo (comida → deixar comida no comedouro; limpeza → limpar; companhia → carinho), **descontado do
    mesmo orçamento** de 16 por dia. Sem rng nova: a resposta é determinística. No LAB (sem unidades de fala), o "atende" responde ao
    `chamar_atencao` pelo receptor de maior urgência entre fome, higiene e solidão, para os dois braços terem o mesmo dono.
- **As células:** 4 donos × 2 (ignora, atende) = 8 por braço; **16 vidas por unidade.** Pareamento por unidade e célula: a mesma semente,
  o mesmo genoma, o mesmo dono; só a subchave e a regra de atender mudam. A célula repetida do incoerente com o atencioso no comedouro
  (`CELULA_DUPLICADA`) fica, como na C4 e na AN4.

## 3. A mecânica, só o que a análise precisa (o código é a DC3a)

### 3.1 As unidades de fala (subchave `fala_unidades`, desligada por padrão)

- O `chamar_atencao` passa de uma unidade `(chamar_atencao,)` a três: **`(chamar_atencao, "fome")`, `(chamar_atencao, "higiene")`,
  `(chamar_atencao, "solidao")`** (DC3-4). A lembrança como conteúdo ("contar uma lembrança") fica fora: ela não tem cuidado que a
  responda, então não tem consequência que ensine.
- **O inato de cada uma:** o W0[chamar_atencao]·z de hoje, com o termo do receptor do conteúdo multiplicado por `ganho_conteudo` e os dos
  outros dois por zero (PROPOSTO, SEM FONTE; o número sai na DC3a, com a condição de que a soma das três unidades no dia 1 do LAB+F fique
  perto da do `chamar_atencao` do LAB, conferida nas sementes dos testes, sem a faixa).
- **O hábito:** uma linha de H por unidade de fala (três em vez de uma), creditada pelo P2 de hoje (o r_n do corpo no intervalo da opção).
  Nenhuma regra de aprendizado nova.
- **O mundo e o corpo:** iguais ao `chamar_atencao` (o som, nenhum efeito no corpo). O que muda o corpo é só o dono que atende.
- **Desligada,** a vida sai byte a byte (o gabarito das vidas de hoje é gravado num commit próprio antes da mudança).

### 3.2 O decodificador e a voz

Nada muda neles nesta etapa. No descritivo (seção 8), a fração das falas cujo conteúdo coincide com a intenção do `dec-v2` na mesma decisão
mostra se a fala ante-hoc (I-b) e a post-hoc (I-a) dizem a mesma coisa.

## 4. As medidas

**Nenhuma métrica fora do `digilab/metrics.py`.** A taxa por episódio, a privação e as medidas do corpo já estão lá (as da AN4). A da fala
é nova e entra antes da run:

- **4.1 `fala_nas_decisoes(decisoes, dias)`**, com `decisoes` = (ação, conteúdo ou None, urgências de fome, higiene e solidão) por decisão.
  Devolve, por janela (dias 1–3 e 8–14) e na vida: as falas por dia, a pertinência e a fala pertinente por dia.
- **4.2 A fala pertinente:** uma decisão de fala cujo conteúdo é o receptor de maior urgência entre fome, higiene e solidão naquela decisão
  (empate: a ordem fome, higiene, solidão), **e** com essa urgência acima do `urgencia_lambda` (S/2, como na AN4). Falar de fome sem fome
  não conta.
- **4.3 A unidade:** a (base, semente). O G-ESCUTA é a média, nas 4 células de dono, da diferença atende − ignora da fala pertinente por
  dia (dias 8–14), no LAB+F. A guarda é a média, nas 4 células, de LAB+F − LAB da taxa por episódio, com o dono que ignora. Célula com a
  taxa `None` num dos lados fica fora da média daquela unidade (a regra da AN4).
- **4.4 A conferência do crédito:** por vida do LAB+F com o dono que atende, a fração dos atendimentos que caem dentro do intervalo da
  opção de fala que os provocou. Não é medida: entra no relato para ler o nulo da seção 1.

## 5. O que a run grava

Por vida: as medidas da AN4 (as de `orq.medidas`, `conserto=True`, e as do corpo), a fala da 4.1, a conferência da 4.4 e as linhas de H das
três unidades nos dias 1, 3, 8 e 14. Os artefatos `meta.json`, `medidas.json` (`.gz` se passar de 100 MB) e `resultado.json`, com
`git add -f`; as vidas num `vidas.tar.gz`.

## 6. O tamanho

- **A guarda:** a mesma medida, o mesmo cenário, o mesmo lugar e a mesma unidade da AN4. A conta de poder de lá vale como está: **K = 200
  (40 por base), margem δ = 0,018** (o σ de planejamento 0,0915; poder 0,8 contra um dano de 0,018; DC3-5). Não há conta nova nem
  vida nova para isso.
- **O G-ESCUTA:** não há dado de hoje para a variância (nenhum dono atende hoje). **Ele é lido pela classe do IC95 do t sem margem**
  ("> 0" se o limite inferior passa de 0; "< 0" se o superior fica abaixo; senão "indeterminado"), como o MOV da AN4. Não há "≈ 0" para
  ele (DC3-6). Com K = 200, o efeito detectado com poder 0,8 é ≈ 0,20 dp da diferença entre as unidades; o relato dá esse número em fala
  por dia, pelo dp observado.
- **As vidas:** 200 unidades × 16 = **3 200 vidas.** Pela AN4 (4,3 s de CPU por vida, 1 h 39 min com 4 processos para 3 200 vidas), cerca de
  **1 h 40 min com 4 processos** (V3-D8: no máximo 4 processos, uma run por vez).

## 7. A análise e a regra de leitura

### 7.1 As premissas (DECIDIDAS na DC3-7; SEM FONTE)

Se uma falha, o gate e a guarda são **inconclusivos por premissa**.
- **P-FALA:** no LAB+F com o dono que ignora, a fração das decisões fora do dormir que são fala tem o limite inferior do IC95 > 0,01 (o
  limiar da P-PASSEIO da AN4). Sem fala, não há o que aprender nem o que custar.
- **P-ATENDE:** no LAB+F com o dono que atende, ao menos 1 atendimento por dia em média nos dias 1–3 (o limite inferior do IC95 > 1). Sem
  atendimento, o "atende" é o "ignora".
- **G-ELEGIVEL-EP** (a da AN4): ao menos 80 % das vidas com 3 episódios de fome ou mais, no LAB e no LAB+F com o dono que ignora.

### 7.2 O gate G-ESCUTA

"> 0" passa; "indeterminado" ou "< 0" não passa. O resultado negativo fica como está.

### 7.3 A guarda G-COMEDOURO-DC3

A classe de A6.6 com δ = 0,018, como na AN4: "< 0" falha; "≈ 0", "> 0" ou "indeterminado" não falha.

### 7.4 A leitura, uma linha só

| premissas | G-ESCUTA | guarda | a leitura | o que segue |
|---|---|---|---|---|
| falha | — | — | inconclusiva por premissa | volta ao Matheus |
| passam | "> 0" | não "< 0" | **a rede aprende a falar pela consequência sem cuidar pior de si** | a DC3d (o porte ao jogo, atrás de chave) |
| passam | "> 0" | "< 0" | aprende, mas falar tira o pet da comida quando ninguém escuta | a subchave fica desligada; volta ao Matheus |
| passam | não "> 0" | qualquer | o P2 de hoje não liga a fala à resposta do dono | a subchave fica desligada; a leitura do crédito (4.4) diz por quê |

## 8. O descritivo (sem gate)

1. A fala por dia ao longo dos 14 dias, por braço, dono e célula; a EXT da seção 1.
2. As linhas de H das três unidades nos dias 1, 3, 8 e 14.
3. A pertinência por janela; o conteúdo das falas quando a maior urgência está abaixo do limiar.
4. A coincidência entre o conteúdo da fala e a intenção do `dec-v2` (3.2).
5. O corpo e a privação (as medidas da C5), só "pior ou não".

## 9. O que não muda

O motor, o corpo, o mundo, o `engine.py`, o A, os pets v11 a v17, o decodificador, a voz e o jogo web. Os inatos do #428 e os valores da
memória da C4. A C2, a C3, a L-2 e o passeio ficam desligados nos dois braços. Nenhuma calibração e nenhum piloto: o `ganho_conteudo` é
fixado na DC3a pela condição da 3.1, nas sementes dos testes.

## 10. As missões

| missão | o que | entrega |
|---|---|---|
| **DC3a** | a subchave `fala_unidades` (Python), o dono que atende, a `fala_nas_decisoes` no `metrics.py`, o orquestrador `experiments/run_v3_conversa_dc3.py` e a config; o gabarito antes, byte a byte desligado; passar a DECIDIDO o `limiar_desfecho` (S/8) e o `limiar_valor` (S/2) da DC2b | PR de código, sem vidas da faixa |
| **DC3b** | o registro da run (seção 11) e a run única | os artefatos |
| **DC3c** | o resultado (`docs/RESULTADO_V3_CONVERSA_DC3.md`) | PR de resultado |
| **DC3d** | só se a linha 2 da 7.4: o espelho TS, a paridade e a fala no jogo (a unidade escolhida vira a intenção da voz) | PR do jogo |

## 11. O registro e as conferências da run

Antes da primeira vida, num commit empurrado: o comando, o sha256 da config, do orquestrador, deste plano e do `metrics.py`, e o
`git_head`. Em cada vida, falhando alto: o replay bit a bit do disco, o cenário, a conferência da memória da C4, os fins conhecidos de cada
braço, nenhuma unidade de fala no LAB e nenhum atendimento sem fala no passo (no LAB+F). Depois da run: os sha256 dos artefatos e a análise
refeita do `medidas.json`, byte a byte.

## 12. As decisões (DECIDIDAS pelo Matheus em 2026-11-07, todas pela recomendação; cada uma com o custo de errar)

| | decisão | recomendação | custo de errar |
|---|---|---|---|
| **DC3-1** | só o comedouro | sim: a guarda é perto da ração, e a fala não depende do lugar | não saber se a fala ajuda longe da ração |
| **DC3-2** | LAB contra LAB+F | sim: só a subchave muda | nenhum além do escopo |
| **DC3-3** | o dono que atende, no mesmo passo e no mesmo orçamento | sim: sem orçamento extra, o atender não dá cuidado de graça | o atender instantâneo é mais fácil de aprender que o de um jogador real |
| **DC3-4** | três conteúdos (fome, higiene, solidão), sem a lembrança | sim: só conteúdo com cuidado que responda | a lembrança fica sem fala ante-hoc nesta etapa |
| **DC3-5** | K = 200 e δ = 0,018, da AN4 | sim: a mesma medida e o mesmo cenário | se a fala mudar a variância, a margem efetiva muda (o relato dá) |
| **DC3-6** | o G-ESCUTA pelo IC95 sem margem | sim: não há dado para uma margem | um efeito pequeno demais para importar pode passar |
| **DC3-7** | as premissas P-FALA, P-ATENDE e G-ELEGIVEL-EP | sim | uma premissa frouxa deixa passar um gate vazio |
| **DC3-8** | a faixa 79101…79505 (bases 79101, 79202, 79303, 79404, 79505; prefixo `digibrain_prototipo`) | sim: conferida livre em 2026-11-07 | nenhum |
| **DC3-9** | a lembrança de luta e o texto do dono continuam fora da rede (DC-C, espec seção 4) | sim | nenhum novo |

## Adendo 1 — o crédito da fala até a decisão seguinte e o gate condicionado à necessidade (2026-11-07, Gerente da CONVERSA_PET, Opus 5.5)

**Status: APROVADO pelo Matheus em 2026-11-07 ("Aprovo todas"), DC3-A1 a DC3-A4 pela recomendação.** O Matheus pediu o adendo em
2026-11-07 ("Fazer o adendo"), depois do achado D-CP-DC3a-1. Nenhuma vida da faixa 79101…79505 rodou. **O adendo vale antes da primeira vida.** Ele muda as seções 3.1, 4, 7.2, 7.4 e 11,
e o resto do plano fica como está. Quando aprovado, ele entra no sha256 do plano no registro da run (seção 11).

### A1.0 Por que (o achado da DC3a)

- **O pet decide a cada 15 ticks** (`intervalo_decisao_ticks`).
- **O r_n de cada decisão** é a valência do corpo entre a percepção ao decidir e a percepção logo depois da ação, no mesmo tick. O
  `motor_corpo._decidir` chama o `consequencia_corpo` antes de o relógio andar, e o `adapt._fechar` lê os dois corpos assim.
- **O dono age no fim do passo,** entre uma decisão e a seguinte. O cuidado que ele dá não cai no r_n de decisão nenhuma.
- **Na varredura** (as sementes dos testes; `artifacts_v3_conversa_dc3/varredura/resultado.json`), 0 de 2 059 atendimentos caíram dentro
  do intervalo da opção de fala.
- **A run como estava** cairia na linha 4 da 7.4 por construção. O G-ESCUTA de lá também confunde o aprendizado com o estado: quem atende
  tira a necessidade, e o pet tem menos do que pedir. Na varredura ele saiu "< 0".

### A1.1 O crédito da opção de fala (muda a 3.1, "O hábito")

- **Com a `fala_unidades` ligada,** o r_n de uma opção de fala (as três unidades do `chamar_atencao`) é o do corpo entre a percepção ao
  decidir a fala e a percepção ao decidir a decisão seguinte, antes da ação seguinte. É a mesma função de hoje (`afeto.consequencia`),
  com o corpo de depois lido 15 ticks mais tarde.
- **Esse intervalo contém o passo inteiro:** a deriva das necessidades, o cuidado do dono de hoje e o do dono que atende. O P2 credita
  esse r_n na linha da unidade, como hoje. Nenhuma regra de aprendizado nova e nenhum número novo.
- **As outras opções não mudam;** o r_n delas continua o do tick da ação.
- **A assimetria é conhecida e escrita antes:** só a fala vê a deriva do passo. Quando ninguém atende, a deriva (a fome que sobe) pesa
  contra a fala, e isso empurra a fala para baixo nos dois donos.
  - **No G-ESCUTA** ela se anula em boa parte, porque o contraste é pareado entre os donos, com o mesmo cérebro e a mesma deriva.
  - **Na guarda** ela favorece o "não < 0" (menos fala, menos decisões tiradas do comer). O relato dá a fala por dia do LAB+F com o
    dono que ignora contra o `chamar_atencao` do LAB, para ver o tamanho disso.
- **Desligada a `fala_unidades`,** nada muda: as vidas de hoje saem byte a byte (o gabarito da DC3a confere).
- **No LAB não muda nada:** o `chamar_atencao` segue de uma decisão só.
- **Por que até a decisão seguinte, e não só o gesto do dono:** creditar só o efeito do gesto exigiria que o cérebro separasse o cuidado
  da deriva, coisa que ele não lê no corpo. O intervalo até a próxima decisão é a forma mais simples de deixar a consequência chegar, sem
  dar ao cérebro informação que ele não tem.

### A1.2 O gate G-ESCUTA condicionado à necessidade (muda a 4.3 e a 7.2)

- **A medida:** nas decisões fora do dormir dos dias 8 a 14 em que a maior urgência entre fome, higiene e solidão passa do
  `urgencia_lambda` (S/2, estrito, D-CP-DC3a-5), a fração que é fala pertinente (4.2). Chamo essas decisões de "decisões com
  necessidade" e a fração de **P(fala pertinente | necessidade)**. Ela entra no `digilab/metrics.py`, pela `fala_nas_decisoes`, antes
  da run.
- **O G-ESCUTA passa a ser,** no LAB+F, a média nas 4 células de dono da diferença atende − ignora dessa fração, por unidade
  (base, semente).
  - Uma célula sem decisão com necessidade num dos lados fica com a medida `None` e sai da média daquela unidade (a regra da AN4).
  - A unidade sem célula válida sai do gate, e o relato conta quantas saíram.
- **A leitura é a de antes:** a classe do IC95 do t sem margem (DC3-6). "> 0" passa; "indeterminado" ou "< 0" não passa.
- **Por que condicionar:** entre decisões com necessidade, o "o dono já resolveu" deixa de baixar a medida. O que sobra é a escolha de
  falar quando há do que falar. Ainda pode sobrar uma diferença na intensidade da necessidade acima do limiar entre os donos. O relato
  dá a urgência média nas decisões com necessidade, por dono, para ver isso.
- **A fala pertinente por dia** (o G-ESCUTA de antes) vai para o descritivo (seção 8, item 1), sem gate.
- **Uma premissa nova (soma-se à 7.1), P-NECESSIDADE:** em ao menos 80 % das unidades do LAB+F, o G-ESCUTA está definido (ao menos uma
  célula válida). Sem decisões com necessidade, não há o que condicionar.

### A1.3 A leitura (muda a linha 4 da 7.4) e as conferências (muda a 4.4 e a 11)

- **A linha 4 da 7.4 passa a dizer:** "com o crédito até a decisão seguinte, o P2 não liga a fala à resposta do dono". O que segue é o
  mesmo (a subchave fica desligada e o caso volta ao Matheus).
- **A 4.4 vira conferência da run,** e falha alto: com a `fala_unidades` ligada, todo atendimento do dono que atende cai dentro do
  intervalo da opção de fala que o provocou. Por A1.1 isso vale por construção, e um caso fora indica bug.
- **O relato ainda dá** a fração dos cuidados do dono de hoje (o que não responde à fala) que caem dentro de intervalos de fala, nos dois
  donos.
- **Mais um item no descritivo:** a média do r_n creditado às opções de fala, por dono e por janela (dias 1–3 e 8–14).

### A1.4 O que não muda

O cenário, os braços, os donos, as células, K = 200 e δ = 0,018, a guarda G-COMEDOURO-DC3, a P-FALA, a P-ATENDE, a G-ELEGIVEL-EP, a faixa
e o prefixo, o `ganho_conteudo` (3S/2, D-CP-DC3a-2; ele condiciona a fala do dia 1, que não depende do crédito) e as decisões DC3-1 a
DC3-9.

**A varredura da DC3a** é refeita nas sementes dos testes só para conferir o código (A1.1 e a conferência da A1.3). Nada se ajusta
olhando para ela.

### A1.5 As decisões do adendo (DECIDIDAS pelo Matheus em 2026-11-07; cada uma com a recomendação e o custo de errar)

| | decisão | recomendação | custo de errar |
|---|---|---|---|
| **DC3-A1** | o r_n da opção de fala vai até a decisão seguinte (A1.1), atrás da `fala_unidades` | sim: é o menor passo que deixa o cuidado do dono chegar ao P2 | a deriva do passo pesa só contra a fala, o que favorece a guarda (o relato mede) |
| **DC3-A2** | o G-ESCUTA vira P(fala pertinente \| necessidade), atende − ignora, dias 8–14 (A1.2) | sim: tira o efeito de o dono já ter resolvido | se a intensidade da necessidade diferir entre os donos, sobra um resto do confundidor (o relato mede) |
| **DC3-A3** | a premissa P-NECESSIDADE (80 % das unidades com o gate definido) | sim | uma premissa frouxa deixa passar um gate de poucas decisões |
| **DC3-A4** | a 4.4 vira conferência que falha alto | sim: por A1.1 ela é certa por construção | nenhum |
