# PLANO DE ANÁLISE V3 — GOSTO_VISUAL: a fidelidade da fala do assistir (2026-11-12, Claude Code, Opus 5.5, branch `v3-gosto-visual-fala`)

**Status: PROPOSTO.** Nada roda antes do cabeçalho com a marca "APROVADO pelo Matheus". **Nenhuma fala com LLM roda** antes disso, nem para
teste. É a FA-8 de `docs/futuro/fala_do_assistir.md` (DECIDIDA pelo Matheus em 2026-11-12, pela recomendação): o verificador da DC5
estendido aos conceitos do assistir e uma marcação cega curta do Matheus, com plano próprio antes da primeira fala.

**Não confundir:** o `docs/PLANO_ANALISE_V3_GOSTO_VISUAL_FALA.md` é outro plano (o braço dos conceitos do Digimundo, FA-20). Este cobre só os
quatro conceitos do assistir do `dec-v4` (FA-3), sem órgão da visão.

**O que já existe (o código desta etapa, sem nenhuma fala com LLM):**
- o `dec-v4` (`digilab/digibrain/decodificador.py`, `decodificar_v4`, e o espelho `decodificarV4` do TS, bit a bit): os conceitos `gostei`,
  `susto`, `chato` e `o_que_e`, com valor e confiança em [0, S], e a intenção do assistir;
- os limiares na `ConfigFalaAssistir` (`digilab/config.py`), PROPOSTOS, calibrados nas vidas **gravadas** da GV3 e da GV3b
  (`artifacts_v3_gosto_visual/fala_limiares/`, D-GV-FALA-4). A calibração já foi feita: **nada deste plano ajusta os limiares**;
- a fala por template no jogo (FA-7), atrás da chave "Fala do assistir (teste)", desligada por padrão, com o limite da FA-5 e a linha no log
  de apresentação (FA-6).

**O que este plano não afirma:**
- que o pet sente o que diz: "gostei" é o nome de um conceito com um limiar sobre o agrado efetivo (F2, `docs/DEFINICOES_FRUTAS_V2.md`, 2.2);
- que a fala do assistir parece viva a quem joga (a marcação é de falas soltas, fora do jogo);
- que o pet sabe o que passa na TV: sem o órgão (FA-9 a FA-13, de outra sessão), nenhum conceito fala do conteúdo;
- nenhuma novidade. Pets e personagens que comentam o que acontece existem em jogos há muito tempo, e nenhuma busca foi feita aqui.

## 1. As perguntas, escritas antes

- **Q1 (a fidelidade):** a fala que a voz dá a um conceito do assistir só afirma o que o conceito ativo sustenta? A referência é a marcação
  da seção 4, com a rubrica da seção 3.
- **Q2 (o verificador):** o verificador estendido (seção 5) marca as falas sem sustento e deixa passar as sustentadas? Sensibilidade e
  especificidade contra a referência.
- **Q3 (o template, descritivo):** o template da FA-7 é a linha de base. Ele é fiel por construção (uma frase fixa por conceito, a de dúvida
  com a confiança baixa); o que ele mostra é se o conceito acende na hora certa, e isso é descritivo, sem gate.
- **As previsões (escritas antes):** o template sai sem sustento em 0 falas (por construção; uma falha aqui é erro de código, não
  resultado); a voz com LLM sai pior que o template, e o risco maior é o enfeite ("adorei as cores!", "que filme bonito"), que fala do
  conteúdo ou de um canal que o conceito não diz.

## 2. O desenho

- **Os braços:**
  - **T**, o template da FA-7 (`src/falaAssistir.ts`, `FRASES_ASSISTIR`, `template-assistir-v1`);
  - **V**, a voz que a DC5c aprovar, com um bloco novo dos conceitos do assistir numa versão nova da voz (a etapa FA3 da proposta). **Se a
    DC5c não aprovar voz nenhuma, o braço V não existe** e este plano roda só o T e o verificador.
- **O modelo do braço V:** o `gemma2:9b` local, o único aprovado para a fala livre (`servidor/CLAUDE.md`). Nenhum Claude neste plano.
- **A entrada de cada fala:** o bloco `assistir` do `dec-v4` de uma decisão (a intenção, os quatro conceitos com valor e confiança), a
  espécie e o estágio do pet. **Nunca** o quadro, o áudio, os sete números, o agrado em número, o programa ou a fonte (GV-10; seção 2.3 da
  proposta).
- **O material (seção 6):** decisões com intenção do assistir não nula, sorteadas de vidas novas da TV do jogo, numa faixa nova.

## 3. A rubrica: o adendo do assistir à rubrica da DC5

- **A base é a `docs/RUBRICA_DC5_FIDELIDADE.md`,** sem mudança nas regras 3.1 a 3.8. Um conceito está ativo com valor ≥ 512 e tem confiança
  baixa abaixo de 512 (os mesmos números da DC; na `ConfigFalaAssistir`, `limiar_ativo` e `limiar_confianca`).
- **Um arquivo novo,** `docs/RUBRICA_FALA_ASSISTIR.md`, escrito e commitado com o sha256 no registro **antes** da primeira fala, só com o
  que muda:
  - **o sentido de cada conceito do assistir** (a tabela da seção 4 da rubrica ganha quatro linhas, PROPOSTAS):

    | conceito | sustenta |
    |---|---|
    | `gostei` | gosta do que está vendo agora, acha bom ver aquilo |
    | `susto` | levou um susto agora, com um som que subiu de repente |
    | `chato` | cansou de ver aquilo, está entediado com o que vê |
    | `o_que_e` | estranha o que vê, não sabe o que é aquilo |

  - **o conteúdo da tela é sem sustento sempre** (`sem_conceito`): o que passa na TV ("um gato", "um filme", "o jogo"), uma cor, o brilho,
    o movimento, a música e o nome do programa. Nenhum conceito do `dec-v4` diz isso (sem o órgão, FA-1 e seção 6 da proposta);
  - **o susto pelo som é sustentado, o susto pela imagem não** (FA-4: o corpo só tem o salto de volume). "Que barulho!" com o `susto`
    ativo é sustentado; "que clarão!" é sem sustento;
  - **o gosto como traço é sem sustento:** "eu adoro TV" ou "eu sempre gosto disso" afirmam um gosto duradouro; o `gostei` diz só o agora.
- **A rubrica do assistir não muda depois do registro.** Uma rubrica revista nunca dá gate sobre a rodada que já rodou (a regra da DC5, 4.1).

## 4. A referência: quem marca e a regra da marcação cega

- **O marcador Opus cego:** um subagente novo que recebe só a rubrica da DC5, a rubrica do assistir e o pacote cego (a entrada e a fala, sem
  o braço, a voz, o modelo, o verificador nem este plano). Ele marca todas as falas.
- **O Matheus marca uma amostra curta:** **24 falas** (PROPOSTO, SEM FONTE; FAA-3), sorteadas em igual número entre os braços que existirem
  e entre os quatro conceitos, na mesma página e com as mesmas rubricas. É a "marcação cega curta" da FA-8.
- **A regra da marcação cega (a D-DC4D-1 da DC5, seção 9.1, sem mudança):** nada do marcador Opus, do verificador nem das falas da rodada
  chega ao Matheus antes de ele terminar a amostra dele: nem contagem, nem leitura, nem dúvida do Opus, nem fala citada, em mensagem,
  relato, PR ou commit que ele leia. O worker passa os resultados do Opus só à sessão coordenadora; ao Matheus, diz só que o marcador terminou
  e o que falta marcar. A página não mostra braço, voz, modelo nem contagem.
- **O kappa de Cohen** entre o Opus e o Matheus na amostra ≥ 0,7 (o número da DC5) aceita o Opus como referência. Abaixo, ou não
  calculável, a Q1 e a Q2 ficam "não medidas", e o relato traz a concordância bruta e o número de positivos.

## 5. O verificador estendido

- **A versão nova do verificador** (`verif-v10`, nome PROPOSTO), em `digilab_fala_livre/verificador.py`, a partir da `verif-v8b` da DC5,
  com o formato novo `dec-v4` na entrada:
  - os quatro conceitos do assistir entram no `SIGNIFICADO` (`digilab_fala_livre/conceitos.py`), com os sentidos da seção 3;
  - uma regra nova, determinística, antes do extrator: a fala que nomeia conteúdo da tela, cor, brilho ou o programa é marcada (a lista de
    palavras é PROPOSTA e vai ao registro com o sha256);
  - o resto (o extrator e a regra da hesitação) é o da `verif-v8b`.
- **O que se mede:** a sensibilidade e a especificidade contra a referência (Q2), por braço e juntos. As falhas de chamada do extrator
  contam como "marcou" e saem à parte.
- **O código do verificador e da voz nova é a etapa FA3** da proposta, num PR próprio, antes do registro. Este plano não o escreve.

## 6. O material e as sementes

- **As vidas:** a TV do jogo (`tv-programas`, determinística) no pet da GV3b (o olhar com o enjoo), com os donos `nenhum`, `calmo` e
  `agitado` e o genoma próprio, como a GV3b; os dias e o número de vidas são os que dão as falas da seção 4 (a conta vai no registro).
- **A faixa:** uma faixa nova, **pedida ao coordenador** e posta em `FAIXAS_RESERVADAS` antes da primeira vida (FAA-4). As faixas da GV3
  (89101…89505) e da GV3b (91101…91505) não servem: os limiares foram calibrados nelas.
- **As falas:** de cada vida, as decisões com intenção do assistir não nula, sorteadas por uma rng própria (`derivar_semente`), em igual
  número por conceito (o `o_que_e` é o mais raro: 6% das decisões olhando na calibração, `limiares.json`); **96 entradas** (24 por
  conceito, PROPOSTO, SEM FONTE; FAA-2), cada uma falada uma vez por braço.
- **O tamanho e a máquina:** 96 falas do braço V no `gemma2:9b` local e 96 do T (sem modelo), o verificador nas 192, o marcador Opus nas 192
  (um subagente; o custo dele vai no registro). No máximo 4 processos e uma run de pesquisa por vez (V3-D8).

## 7. Os gates (PROPOSTOS, SEM FONTE) e a regra de leitura

- **G-FIEL-T:** o template sem sustento em 0 de 96 falas. Uma falha é erro de código (o template e as rubricas não batem) e para a rodada.
- **G-FIEL-V:** o braço V com no máximo 10% das falas sem sustento, com o IC95 de Wilson no relato (o número é PROPOSTO, FAA-5).
- **G-VERIF:** a sensibilidade do verificador ≥ 0,8 e a especificidade ≥ 0,8, os dois braços juntos (PROPOSTOS).
- **A leitura:** gate que falha não para a V3; o resultado negativo é registrado como está. Com o G-FIEL-V falho, a fala do assistir segue
  no template no jogo. Nada se ajusta olhando a validação: nem os limiares, nem as frases, nem a rubrica.

## 8. O registro e as conferências

- **O registro da rodada** é uma seção nova deste plano, num commit empurrado antes da primeira chamada ao modelo, com: os sha256 deste
  plano, das duas rubricas, do orquestrador, da config, do `prompt.py`, do `verificador.py`, do `conceitos.py`, da `ConfigFalaAssistir` e do
  `limiares.json`; a tag do `gemma2:9b`; a faixa; e a trava do plano na `HEAD` igual ao da `origin/main`.
- **As conferências falham alto:** o modelo é o pedido; toda fala tem a entrada, o braço, a semente e a versão; os dois braços viram as
  mesmas entradas; nenhuma entrada leva número, programa ou fonte (o pacote é conferido contra a lista da seção 2).

## 9. As decisões (todas PROPOSTAS; cada uma com a recomendação e o custo de errar)

| id | a decisão | a recomendação | o custo de errar |
|---|---|---|---|
| **FAA-1** | Os braços. | **O template (T) e a voz que a DC5c aprovar (V);** sem a DC5c, só o T e o verificador. | Rodar uma voz que não passou na DC5 mede a fala do assistir sobre uma voz sem fidelidade. Sem o T, não há linha de base para separar o erro da voz do erro do conceito. |
| **FAA-2** | O tamanho. | **96 entradas, 24 por conceito.** | Menos, o IC do G-FIEL-V fica largo demais para separar 10% de 25%. Mais, custa GPU e tempo do marcador por uma fala curta. |
| **FAA-3** | A amostra do Matheus. | **24 falas**, iguais por braço e por conceito, antes de qualquer resultado de outro marcador. | Menor, o kappa fica instável; maior, custa o tempo do Matheus que a FA-8 quis poupar. Mostrar um resultado antes contamina a referência. |
| **FAA-4** | A faixa. | **Uma faixa nova pedida ao coordenador**, fora das da GV3 e da GV3b. | Usar as sementes da calibração mede os limiares nos dados em que eles foram tirados. |
| **FAA-5** | O G-FIEL-V. | **No máximo 10% sem sustento.** | Mais frouxo, a voz enfeita e o gate passa; mais estrito, com 96 falas, um gate que falha por acaso. |
| **FAA-6** | O conteúdo da tela na rubrica. | **Sem sustento sempre**, enquanto não houver o órgão. | Aceitar "que gato!" sem órgão é o caminho B por dentro (a FA-1). Com o órgão, a regra muda num plano novo. |

## 10. O que não se faz

- Nenhuma fala com LLM antes da aprovação deste plano e do registro.
- Nenhum ajuste dos limiares, das frases ou da rubrica olhando a rodada.
- Nenhum quadro, áudio ou número da captura vai ao modelo (GV-10).
- Nenhum resultado do marcador Opus ou do verificador ao Matheus antes da amostra dele.
- Nenhum número em resultado sem artefato em disco.
