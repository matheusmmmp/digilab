# Plano de análise V3: SOCIAL_PAR A0 e B0, o parceiro que responde no pet de hoje

**Status: PROPOSTO.** Escrito em 2026-11-17 (Claude Code, Opus 5.5, na sessão com o Matheus, branch `v3-social-par-a0`). Nenhuma vida
roda, nem a do piloto, antes de quatro coisas:
1. este plano commitado na `main`, com a marca de aprovação do Matheus no cabeçalho;
2. as decisões A0-1 a A0-10 (seção 10) DECIDIDAS;
3. as duas faixas na `FAIXAS_RESERVADAS` (`experiments/bancada/faixas.py`), num commit próprio;
4. o código da seção 4 na `main`, com os gates dele passando.

Os números novos daqui são **PROPOSTOS e SEM FONTE**, salvo onde dito.

**De onde vem:**
- a investigação `docs/INVESTIGACAO_V3_SOCIAL_PAR.md`: os experimentos A (seção 3.1) e B (seção 3.2), o esqueleto de validade (seção 4) e a
  ordem (seção 6: o A0 e o B0 vêm depois da E1, e o SP-3 depende do A0);
- a E1 (`docs/ESPEC_V3_SOCIAL_PAR_E1.md`, PR #980). Ela deu o parceiro gravado, o `levar_pet` com a origem `intervencao` e as seis
  medidas de `digilab/metrics.py`, e validou o instrumento:
  - **a gravação é fiel:** sem perturbação, a GRAV refaz a VIVO com zero desvios (o G-GRAV-IDENT);
  - **o nulo passa:** o parceiro gravado não responde ao focal (o G-MET-NULO);
  - **os controles positivos passam,** mas só com parceiros de regra pura (o adendo 2, D-SP-21). Com pets que se movem e têm necessidades,
    o instrumento separou a VIVO da GRAV só na maioria das sementes (D-SP-13, D-SP-18);
- a SP-7: a margem e o N do A0 ficam num plano próprio, com um piloto.

**O que este plano não afirma:**
- que o pet de hoje percebe o parceiro;
- que uma diferença VIVO − GRAV é uma relação, um aprendizado ou um mecanismo;
- que o instrumento acha diferenças menores que a dos controles de regra pura.

**Nenhuma alegação de novidade:** a gravação de parceiro é a de Froese e Di Paolo 2008 (`10.1007/978-3-540-69134-1_6`), adaptada.

## 1. A pergunta e as previsões, escritas antes

**A pergunta do A0:** no pet de hoje (o DigiBrain modular nos dois, com a CO7 do jogo), o pet focal F volta a ficar perto do parceiro P mais
depressa quando P responde a ele (VIVO) do que quando P só repete o que fez numa vida em que F estava lá, sem responder (GRAV)?

**A pergunta do B0:** depois da mesma perturbação, P chuta a bola logo depois de F mais vezes quando responde a F do que quando repete a
gravação, descontada a alternância que sai só da taxa de chutes de cada um?

**As previsões** (a investigação, seções 0 e 3.1; a direção vem do código, não da literatura):
- **A0: ≈ 0.** O modular não tem ação dirigida ao outro (`digilab/digibrain/impulso.py:118-148`), e o corpo não sente o outro
  (`digilab/corpo.py:32`). O que resta é:
  - **o mundo comum:** a comida que um comeu some, a bola que um chutou rola;
  - **as regras da CO7:** elas leem a ação visível do outro e quase não mudam o que o pet faz (+0,0008 [−0,0014; +0,0039], a investigação,
    seção 1.4).
- **B0: ≈ 0,** pelo mesmo motivo.

**Por que medir uma previsão nula:** sem o A0, o SP-3 (a companhia no corpo) seria decidido sem saber o tamanho do que o mundo comum e a CO7
já produzem. Um "≈ 0" com uma margem escrita antes é o ponto de partida dos A1 e B1 (com o M1 e o M2). Um "≠ 0" diz que já há um caminho
social no pet de hoje, e ele tem de ser entendido antes de acrescentar outro.

## 2. O que não muda

- **Nenhuma mecânica nova no pet:** nem no cérebro, nem no corpo, nem no mundo.
- **O jogo web não muda** (a SP-2: a gravação mora só na bancada).
- **O `engine.py` não muda.**
- **As medidas são as da E1,** em `digilab/metrics.py`. O que se acrescenta é só o tempo restrito à janela (seção 4, item 3).
- **O instrumento é o da E1,** como está no PR #980. Nada nele se ajusta olhando para o piloto, salvo o N (seção 6).

## 3. O desenho

### 3.1 O par e o pet de hoje

- **Os dois pets:** o DigiBrain modular, com o braço e o motor do `experiments/exportar_gabarito_co6.py` (a `fabricas`).
- **A CO7 ligada nos dois** (A0-1): a `CONFIG_COOPERACAO_CO7` no grupo e no cérebro, como em `experiments/exportar_gabarito_co7_par.py`.
  É o que o jogo v39 faz (`web/app/motor/grupo_jogo.ts:59` e `:75`).
- **Os donos:** o atencioso nos dois, com o lugar `comedouro` (A0-2), como nos controles da E1.
- **O mapa:** o `CM` da bancada (`exportar_gabarito_co6.CM`).
- **A vida:** 5 dias. Os dois nascem juntos no tick 0, como no `viver_par`.

### 3.2 As três condições e as cinco vidas por par

Cada par (a semente do grupo) vive cinco vidas, sempre na mesma semente:

| vida | F (o pet A) | P (o pet B) | para quê |
|---|---|---|---|
| **base** | vivo | vivo, gravado | a gravação de P para a GRAV |
| **base-OUTRA** | o `Passivo` (`experiments/bancada/parceiro.py`) | vivo, gravado | a gravação de P para a OUTRA |
| **VIVO** | vivo | vivo | a condição VIVO, com a perturbação |
| **GRAV** | vivo | a gravação da base, com os eventos do dono da base | a condição GRAV, com a perturbação |
| **OUTRA** | vivo | a gravação da base-OUTRA, com os eventos do dono dela | a condição OUTRA, com a perturbação |

- **A identidade até o t0:** sem perturbação, a GRAV é a VIVO byte a byte (o G-GRAV-IDENT). Então, até o passo da perturbação, as duas vidas
  têm de ter as mesmas posições, decisão a decisão. Isso se confere em todo par (o G-INSTR, seção 5.3), e toda diferença depois vem do t0.
- **A OUTRA difere antes do t0,** porque P se moveu numa vida sem F. Ela é a do controle móvel (E1-5) e só entra no secundário S1.

### 3.3 A perturbação

- **Quem é levado:** F, para d0 células de P, por `Grupo.levar_pet`, com a origem `intervencao` no registro.
- **O d0: 12 células** (A0-4). É o dobro do raio "perto" (6, o da visão de hoje), para o reencontro ter de ser produzido pelos dois.
  Perto da borda do mapa, o ponto pode ser cortado. A distância real no t0 é medida e decide a elegibilidade (seção 5.1).
- **O t0 e a direção:** sorteados por par no fluxo `intervencao-social` (`parceiro.sortear_perturbacao`), antes da vida. O t0 cai num passo
  do dono entre o tick 1 440 e o 4 320 (os dias 1 a 3; A0-3), e a direção é uma das 16. Os dois são os mesmos nas três condições.
- **Se F estiver dormindo no t0,** a perturbação espera o primeiro passo em que ele estiver acordado (é o que o `viver_par` faz). O t0 real
  vai no resultado.
- **Uma perturbação por vida.**

### 3.4 As sementes e as faixas

Conferidas em 2026-11-17: não aparecem em `experiments/bancada/faixas.py`, em `docs/` nem em `experiments/` da `origin/main`, nem na
história de nenhum branch remoto. **As duas estão a confirmar com o coordenador** (A0-8) antes de entrar na tabela.
- **O piloto: 102101…102505.**
  - Bases 102101, 102202, 102303, 102404 e 102505; 20 pares por base, 100 pares.
  - Derivação: `unidades_derivadas(bases, 20, prefixo="social_par_piloto")`.
- **A run: 101101…101505.**
  - Bases 101101, 101202, 101303, 101404 e 101505; o K por base sai da regra da seção 6.
  - Derivação: `unidades_derivadas(bases, K, prefixo="social_par")`.
- **Nos dois:** a semente do grupo é a `semente` da unidade. O `genoma` derivado não é usado, porque as sementes dos pets saem de
  `sementes_do_grupo`.
- **As sementes 101…505** servem só à fumaça do orquestrador e aos testes.

## 4. O código, antes da run

1. **Os prefixos e as faixas:**
   - `social_par` e `social_par_piloto` entram em `PREFIXOS_UNIDADES`;
   - as duas faixas entram em `FAIXAS_RESERVADAS`, num commit próprio, depois da A0-8.
2. **A fábrica do par de hoje** em `experiments/bancada/parceiro.py`: o modular com a `cfg_cooperacao` da CO7. O `viver_par` já recebe a
   `cfg_cooperacao` do grupo.
3. **O tempo restrito à janela** em `digilab/metrics.py`: T\* = o tempo até o raio, ou a janela inteira se a série foi censurada. É o tempo
   médio restrito da análise de sobrevivência, sem fonte verificada nesta rodada. Teste: o T\* de séries conhecidas.
4. **Os gates do código** em `tests/test_social_par_e1.py` (ou num `tests/test_social_par_a0.py`):
   - **G-GRAV-IDENT-CO7:** com a CO7 ligada nos dois, sem perturbação, a GRAV refaz a VIVO com zero desvios, em 2 sementes de teste. A E1
     conferiu isso só sem a CO7;
   - **G-ORQ:** a fumaça do orquestrador em 2 pares das sementes de teste, com o G-INSTR e o G1 passando.
5. **O orquestrador** `experiments/run_v3_social_par_a0.py`:
   - as cinco vidas de cada par;
   - as medidas da seção 5 por par;
   - o G-INSTR em todo par (seção 5.3);
   - **o G1:** a VIVO rejogada pelo `reproduzir_grupo` (com a `cfg_intervencao`), bit a bit; a GRAV e a OUTRA refeitas a partir da gravação
     guardada em disco, com o mesmo sha256 do registro;
   - o `meta.json` com o commit, a árvore limpa, os sha256 e o tempo real;
   - no máximo 4 processos.
6. **O piloto** `experiments/piloto_social_par_a0.py`:
   - roda o mesmo orquestrador na faixa do piloto;
   - grava o `artifacts_v3_social_par_a0/piloto.json` só com o desvio padrão dos dois primários, as frequências das premissas (seção 5.1) e
     o N da regra (seção 6);
   - **por construção, não grava nem imprime a média de nenhum contraste.**

## 5. As medidas e os contrastes

**A unidade é o par** (a semente do grupo), e cada par dá um número por medida. As condições são pareadas pela semente.
**A janela** é a das 96 decisões depois do passo da perturbação (`janela_reencontro`, um dia). As decisões são os passos do dono, de 15
ticks.

### 5.1 As premissas

Se uma premissa falha, o primário daquela pergunta é **INCONCLUSIVO POR PREMISSA**, a lição da CB4.

- **PA-1, a janela cabe:** a perturbação aconteceu e as 96 decisões cabem na vida em ao menos 95 % dos pares. Os pares em que não cabe saem e
  são contados.
- **PA-2, a oportunidade:**
  - um par é **elegível no A** se a distância no passo da perturbação passa do raio perto (> 6 células);
  - ela é a mesma na VIVO e na GRAV (seção 3.2), então a elegibilidade não seleciona pelo resultado;
  - **a premissa:** ao menos 80 % dos pares elegíveis, e ao menos 100.
- **PA-3, há espaço para medir:** em ao menos 20 % dos pares elegíveis, o reencontro acontece dentro da janela em ao menos uma das duas
  condições. Abaixo disso, um "≈ 0" seria o teto da janela, não a resposta do parceiro.
- **PB-1, a oportunidade do B:**
  - um par é **elegível no B** se F e P chutam a bola ao menos 2 vezes cada um dentro da janela, na VIVO e na GRAV;
  - como os chutes dependem da condição, essa elegibilidade pode selecionar, e isso vai declarado no resultado;
  - **a premissa:** ao menos 100 pares elegíveis.

### 5.2 Os primários (um por pergunta)

- **O primário do A0:**
  - **a medida:** D_A = T\*_VIVO − T\*_GRAV, onde T\* é o tempo até o reencontro (distância ≤ 6 células) restrito à janela de 96 decisões
    (seção 4, item 3);
  - **a leitura do sinal:** negativo quer dizer que, com o parceiro que responde, F volta a ficar perto mais depressa;
  - **as unidades:** os pares elegíveis no A.
- **O primário do B0:**
  - **a medida:** D_B = E_VIVO − E_GRAV;
  - **o E,** o excesso de alternância, é a alternância de F para P (a fração dos chutes de F seguidos por um chute de P em até 60 ticks,
    antes do próximo chute de F; `metrics.alternancia`) menos a média das alternâncias substitutas (`metrics.alternancia_substituta`);
  - **os substitutos:** os chutes de P deslocados circularmente dentro da janela (1 440 ticks), por 15·j ticks, com j = 8 a 88. São 81
    deslocamentos, todos a mais de 8 decisões do original nos dois sentidos;
  - **a direção é só a de F para P:** na GRAV é P quem está em laço aberto, então só a resposta de P a F é tirada pela gravação. A de P para F
    fica no descritivo;
  - **as unidades:** os pares elegíveis no B.
- **O teste:** o IC95 pelo t sobre os pares (`metrics.ic_t`), bilateral. Os dois primários são lidos cada um, com a margem dele: são perguntas
  diferentes, sem Holm entre elas.

### 5.3 O gate de validade

**O G-INSTR:** em todo par, as posições de F e de P na VIVO e na GRAV são iguais em todos os passos antes do passo da perturbação. Um par que
falha é um erro do código. **A run para**, sem nenhuma leitura, e o erro é registrado.

### 5.4 Os secundários do A0

Uma família de três, com Holm (α = 0,05, bilateral):
- **S1, GRAV − OUTRA:** T\*_GRAV − T\*_OUTRA. Separa a cinemática que já foi contingente a F (antes do t0) da que nunca foi;
- **S2, a fração perto na janela:** a fração na VIVO menos a da GRAV (`metrics.fracao_em_raio`, raio 6);
- **S3, a contingência de F para P:** P(F se aproxima | P se aproximou) − P(F se aproxima | P se afastou), na janela, a da VIVO menos a da
  GRAV (`metrics.contingencia`). Os pares em que ela dá `None` numa das duas condições saem desse secundário e são contados.

As classes de S2 e S3 usam o IC e o sinal, sem margem.

## 6. A margem e o N, pelo piloto

- **A margem do A0: δ_A = 4 decisões** (A0-5): uma hora de jogo, o menor atraso que o jogador perceberia, SEM FONTE.
- **A margem do B0: δ_B = 0,05** (A0-6): cinco pontos na fração dos chutes de F seguidos por P, SEM FONTE.
- **O N** (A0-7). O piloto só dá o σ̂ de cada primário. O N de pares elegíveis é o menor de 200, 400, 800 e 1 600 com:

  1,97 × (1,2 σ̂) / √N ≤ δ / 2

  Assim, com efeito 0, o IC95 fica dentro de (−δ, +δ) com folga, e o "≈ 0" cabe. O fator 1,2 é a folga de 20 % da A5.9 do plano da C1.
  - O N é o maior dos dois (o do A e o do B). O K por base sai do N dividido pela fração de elegíveis do piloto, arredondado para cima, e
    dividido por 5.
  - **Se nem 1 600 bastar,** o N fica em 1 600. A margem efetiva vai no relato, e o critério não muda.
  - **O N e o K ficam DECIDIDOS pelo Matheus** depois do piloto e antes da run, num commit que atualiza esta seção.
- **O que o piloto não faz:**
  - não lê nenhuma média;
  - não muda o d0, a janela, as margens nem as premissas;
  - se uma premissa falha no piloto, o caminho é um adendo, não um ajuste.

## 7. A classificação e a regra de leitura

**As classes** (a regra da A6.6 do plano da C1, com a δ da seção 6):
- **≈ 0:** o IC95 inteiro dentro de (−δ, +δ);
- **< 0:** o limite superior abaixo de 0 e o IC fora de (−δ, +δ);
- **> 0:** o limite inferior acima de 0 e o IC fora de (−δ, +δ);
- **indeterminado:** qualquer outro caso.

**A regra de leitura do A0, escrita antes:**

| D_A | S1 (GRAV − OUTRA) | a leitura |
|---|---|---|
| **≈ 0** | qualquer | **o previsto:** no pet de hoje, o parceiro que responde não muda o reencontro em mais de uma hora de jogo. O instrumento só mostrou que detecta parceiros de regra pura, então isso não diz que o pet "ignora" o outro: diz que não há diferença acima da δ |
| **< 0** | qualquer | **um caminho social já existe no pet de hoje:** F volta mais depressa quando P responde. Os candidatos são a CO7 e o mundo comum. O descritivo (seção 8) aponta onde olhar, e separar os dois pede um adendo (a CO7 desligada, a variante sem comida) antes do SP-3 |
| **> 0** | qualquer | P que responde afasta o reencontro (por exemplo, disputando a comida). Mesmo caminho do `< 0` |
| indeterminado, ou inconclusivo por premissa | — | registrado como está; nada se decide com ele |

- **O S1** é lido à parte. `≠ 0` quer dizer que o passado de P com F importa mesmo sem resposta.

**A regra de leitura do B0:**

| D_B | a leitura |
|---|---|
| **≈ 0** | **o previsto:** P não chuta depois de F mais do que a gravação e a taxa de cada um explicam |
| **> 0** | P responde aos chutes de F: o primeiro sinal de coordenação pela bola no pet de hoje. O E_GRAV e a direção de P para F, no descritivo, dizem se é resposta ou geometria |
| **< 0** | P chuta menos depois de F quando responde (por exemplo, a bola foi para longe dele): registrado como está |
| indeterminado, ou inconclusivo por premissa | registrado como está |

- **Gate que falha não para a V3.** O resultado negativo é registrado como está.
- **A run roda uma vez.** Ela não se repete, e uma faixa nova só vem com um adendo.

## 8. O descritivo (sem gate; nenhum muda a seção 7)

1. **Os desvios da gravação** na GRAV e na OUTRA, por tipo (`fim_da_gravacao`, `parado`, `acao_trocada`, `alvo_fora`), e os consumos
   falhos de P.
2. **O estado de P no t0:** dormindo, comendo ou livre, com o D_A de cada estrato. É a lição da E1 (as necessidades passam na frente).
3. **A comida e a bola no mapa no t0,** com o D_A por estrato: o caminho do mundo comum.
4. **A idade:** o D_A contra o t0. Na leitura da investigação (seção 3.1), um efeito do acoplamento não cresce com a idade, e um efeito
   aprendido cresce.
5. **O reencontro em contato** (raio 1) e a duração dos episódios perto (`metrics.episodios_em_raio`), nas três condições.
6. **As conferências:**
   - **a contingência de P para F na GRAV:** é ≈ 0 por construção, porque P não responde;
   - **o E de P para F,** nas três condições.
7. **A taxa de chutes de P na base-OUTRA,** com F passivo: o "P sozinho com a bola" da investigação.
8. **O que a CO7 fez:** as decisões em que o escudo ou a culpa e a inveja mudaram a escolha, por condição, a partir do que o cérebro já
   registra.

## 9. O tamanho da run e a máquina

- **A conta:** 5 vidas por par, de 5 dias cada. Com N = 1 600 e 80 % de elegíveis, são 2 000 pares e 10 000 vidas.
- **O tempo:** uma vida de 3 dias do par modular, sem a CO7, levou 0,6 s num processo (a semente de teste 101, nesta sessão, só para a
  conta). Essa é uma estimativa de bolso, não um resultado: a do piloto vai no `piloto.json`, e a real no `meta.json`. Pela conta de bolso:
  - a run grande fica em menos de 1 h com 4 processos;
  - o piloto (100 pares, 500 vidas), em alguns minutos.
- **No máximo 4 processos e uma run de pesquisa por vez** (a V3-D8).
- **Os artefatos:**
  - em `artifacts_v3_social_par_a0/`: o `piloto.json` e o `run/` (o `meta.json`, o `resultado.json`, as medidas por par, e as gravações e
    os registros compactados);
  - o resultado no `docs/RESULTADO_V3_SOCIAL_PAR_A0.md`;
  - os desvios em `docs/registro/2026-11.md`.

## 10. As decisões do Matheus

| id | a decisão | a recomendação | o custo de errar |
|---|---|---|---|
| A0-1 | o pet de hoje | **o modular nos dois, com a CO7 ligada** (o jogo v39) | sem a CO7, mede um pet que não está no jogo. Com ela, uma diferença pode vir da regra, e separar a regra pede um adendo |
| A0-2 | os donos | **o atencioso nos dois, no `comedouro`** | outros donos mudam a fome e o sono, e com eles a oportunidade; ficam para depois, se o A0 der ≠ 0 |
| A0-3 | a vida e o t0 | **5 dias; o t0 nos dias 1 a 3; uma perturbação por vida** | com mais de uma por vida, os encontros deixam de ser independentes dentro do par; com vida mais curta, perde-se a leitura da idade |
| A0-4 | o d0 e o raio do reencontro | **12 células e o raio perto (6)** | com d0 pequeno, o reencontro é imediato nas duas condições (o teto da E1); com o raio do contato (1), quase tudo fica censurado |
| A0-5 | o primário e a margem do A0 | **D_A pelo T\* restrito, δ_A = 4 decisões** | uma δ maior aceita como ≈ 0 uma diferença que o jogador veria; uma menor pede um N fora do teto |
| A0-6 | o primário e a margem do B0 | **D_B pelo excesso de alternância de F para P, com a janela de 60 ticks e δ_B = 0,05** | as duas direções juntas misturariam a resposta de F, que a GRAV não tira |
| A0-7 | o piloto e a regra do N | **100 pares, só o σ̂ e as frequências, e a regra da seção 6, com o N de 200 a 1 600** | sem piloto, o N vem de chute, e foi assim que a CB4 ficou inconclusiva |
| A0-8 | as faixas | **102101…102505 para o piloto e 101101…101505 para a run**, a confirmar | nenhum, se a conferência no coordenador passar |
| A0-9 | o que fica fora | **a variante sem comida, a plasticidade congelada e a CO7 desligada ficam para um adendo**, só se o A0 der ≠ 0 | rodar tudo agora triplica as condições para uma pergunta cuja previsão é ≈ 0 |
| A0-10 | a regra de leitura | **a da seção 7, escrita antes** | uma regra escrita depois abre espaço para escolher a leitura |

## 11. O que fica fora

- **Os mecanismos M1 a M4,** os experimentos C a F e qualquer mudança no jogo.
- **As outras perturbações do B:** P congelado por n decisões e P tirado por uma janela. Elas pedem código novo de intervenção, que a E1 não
  tem, e mecanismo novo só entra aprovado.
- **A influência por ramos contrafactuais** (a investigação, seção 4.2), que fica como métrica de avaliação para depois do M1.
- **O pet sozinho no mapa:** o grupo exige os dois ids. A taxa de P com F passivo (seção 8, item 7) fica no lugar dele, como descritivo.
