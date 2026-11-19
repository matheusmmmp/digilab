# PLANO DE ANÁLISE V3 — SOCIAL_PAR MD: a medida do M1 e do M2

- **Status:** APROVADO pelo Matheus em 2026-11-19 ("Aprovado"), com as decisões MD-1 a MD-8 da seção 10 como DECIDIDAS. Nenhuma vida
  rodou antes desta aprovação.
- **Snapshot:** o branch `v3-social-par-m2` (PR #1026, o código do M2), em cima do #1019, do #1018, do #1011 e do #1010. O plano depende
  do código dos dois mecanismos e do orquestrador da S (`experiments/run_v3_social_par_s.py`).
- **Pedido:** o M1-5 ("Siga para o M2") e as decisões já tomadas: o braço de controle do D-SP-63 ("Aprovado, opção (a)"), a espec do M2
  ("Aprovado") e o D-SP-68 ("Opção (a)"). O Matheus pediu este plano em 2026-11-19 ("Sim, escreva").
- **Executor:** Claude Code, Opus 5.5.

## 0. A pergunta

**Com as unidades sociais no cérebro (o M1) e a companhia no corpo (o M2), o parceiro passa a responder ao focal?** E, se responder, a
resposta vem do que o pet aprendeu (o P1 das unidades sociais) ou só de haver unidades a mais no sorteio?

A S3 deu "nulo com um instrumento que vê" nos três substratos (`docs/RESULTADO_V3_SOCIAL_PAR_S.md`):
- **o pet de hoje** ficou dentro de ±1,9 decisão;
- **o seguidor de regra** se separou por 16 a 70 decisões.

O M1 dá ao pet um alvo social e o M2 dá ao outro um valor no corpo: a solidão que cai em contato. **Esta medida é a S3 de novo, com os pets
dos mecanismos no lugar do pet de hoje.**

## 1. O que muda e o que não muda

**O instrumento é o da S3, sem mudança** (o plano da S com o adendo 1):
- as cinco vidas por par: base, base-OUTRA, VIVO, GRAV e OUTRA;
- o t0 sorteado em [1440, 4320] ticks;
- o d0 = 5 células;
- a janela de 96 decisões;
- o primário T\*c, o tempo até o contato;
- a margem δ_A = 4;
- o G-DET, o G-INSTR e o G1.

**Muda só a config do cérebro e do corpo dos dois pets** (os quatro braços de mecanismo da seção 2). O mundo, o dono atencioso no
comedouro, a CO7 nos dois e os 5 dias são os da S3.

**A GRAV também tem a companhia.** A companhia é física: a gravação de P põe P nas mesmas posições, e o corpo de F sente P do mesmo jeito.
- O motor de P gravado sai da mesma fábrica, e por isso tem a mesma `ConfigCompanhia`. A contagem do grupo lê a posição dos dois.
- Assim, o D_A continua medindo a resposta de P a F, e não a companhia em si (a espec do M2, seção 7).

**Nenhuma mudança no jogo.** Os mecanismos ficam só no Python (M1-4 e M2-6), e os saves e a paridade não mudam.

## 2. Os braços

**Os braços de mecanismo:** os dois pets do par recebem a mesma config.

| braço | o cérebro | o corpo | para quê |
|---|---|---|---|
| **M1** | `unidades_sociais` | a de hoje | as unidades sociais sem valor no corpo |
| **M1-inc0** | `unidades_sociais`, com o incentivo social em 0 | a de hoje | o controle do D-SP-63: as unidades a mais, sem o P1 na decisão |
| **M1+M2** | `unidades_sociais` | `ConfigCompanhia` ligada | os dois mecanismos |
| **M1-inc0+M2** | `unidades_sociais`, com o incentivo social em 0 | `ConfigCompanhia` ligada | o controle do M1+M2 |

- **O M1-inc0+M2 é novo neste plano (MD-2).** O D-SP-63 aprovou o controle do M1. Com a companhia, o corpo muda perto do outro, e isso
  pode mudar o que o pet faz por outros caminhos (a solidão mais baixa pesa menos nos drives). Sem esse controle, um D_A do M1+M2 não se
  atribui ao aprendizado.
- **O incentivo social em 0:** o termo `incentivo` das unidades sociais (`digilab/digibrain/impulso.py`, o ramo `social`) vale 0. O P1
  continua aprendendo o desfecho, que só não entra na decisão.
  - O inato, a proximidade e o hábito ficam como no M1.
  - O código é uma subchave nova da `ConfigDigibrain`, que só vale com a `unidades_sociais` ligada e vem desligada, com o seu G2 (seção 8).
- **O pet de hoje não roda de novo (MD-3).** A S3 é a referência dele, já rodada, nas sementes 103001…103200.

**Os braços de substrato (MD-4):**
- **o B1, fora da casa,** é o principal. É o substrato com o T\* longo (~52 decisões) e com o G-DET mais forte;
- **o C, o controle,** é o secundário;
- **o B2 fica fora.** A bola não teve premissa na S3 (13 elegíveis, abaixo do mínimo de 100), e nenhum dos dois mecanismos mexe nela.

## 3. O controle positivo: G-DET em cada célula

- **Como na S3:** o P vira o `SeguidorPuro`, e F é o pet do braço de mecanismo.
- **Por que em cada célula:** F muda com o braço, e um F que segue P (o `seguir` do M1) pode mudar o T\*c do controle positivo.
- **O gate:** o IC95 do D_A do controle positivo fica todo abaixo de −δ_A (−4 decisões).
- **Uma célula em que o G-DET falha não lê o D_A** dos pets do mecanismo. A leitura dela é "o substrato não deixa ver", como na S3.

## 4. As unidades e as sementes

- **K = 200 bases independentes por célula,** cada uma com k = 1. São as mesmas 200 nas oito células (números aleatórios comuns). As
  células só diferem pela config e pelo substrato.
- **O G-DET:** 50 bases por célula, as mesmas nas oito.
- **A faixa proposta (MD-5):** 105001…105400. A run fica em 105001…105200, e o G-DET em 105301…105350. **A faixa é pedida ao
  coordenador** e entra no `experiments/bancada/faixas.py` com esta fonte, antes da run. A conferência de que ela está livre vai no corpo
  do PR.
- **Os prefixos:** `social_par_md` (a run) e `social_par_md_det` (o G-DET), na `PREFIXOS_UNIDADES`, junto com o código.
- **As células da S3:** 1 dono (atencioso) × 1 lugar (comedouro).

## 5. As medidas

**Os primários são os da S3, em cada célula:**
- **o D_A = T\*c_VIVO − T\*c_GRAV:** o tempo até o contato (1 célula), restrito à janela, nos pares com distância > 1 no t0. Um valor
  negativo quer dizer que F e P se tocam mais depressa quando P responde;
- **as premissas PA-1, PA-2 e PA-3,** com os limiares da S3. O B fica fora, porque o B2 fica fora.

**Os contrastes entre braços,** pareados por semente (as mesmas bases):
- **o C-APR:** D_A(M1+M2) − D_A(M1-inc0+M2), por par. É o que o aprendizado acrescenta com a companhia;
- **o C-APR1:** D_A(M1) − D_A(M1-inc0), por par. É o mesmo sem a companhia;
- **a classe** de cada um vem pela δ_A = 4, como os primários (≈ 0, < 0, > 0 ou indeterminado), com o IC95 da diferença pareada.

**A premissa do mecanismo, nova (MD-6):**
- **PM-1, o P1 aprendeu o valor do outro:** no t0, em pelo menos 50 % dos pares, o P do braço M1+M2 tem o desfecho do `seguir` na solidão
  < 0. A medida é o `pl.desfecho["seguir"]` no receptor da solidão, como em `tests/test_corpo_companhia.py`. Ela é lida na vida base de P,
  que é igual à VIVO até o t0;
- **o limiar de 50 % é SEM FONTE;**
- **se a PM-1 falha,** um D_A ≈ 0 no M1+M2 lê-se "inconclusivo por premissa: o P1 não aprendeu o valor do outro antes do t0", e não "o
  pet não responde".

**Os descritivos, que não decidem nada:**
- **a frequência das unidades sociais:** a fração das decisões de P com uma unidade social escolhida, antes do t0 e na janela da VIVO;
- **o desfecho social no t0:** o do `seguir` e o do `onde_comeu`, em cada receptor, nos dois pets;
- **a solidão:** a média da solidão de P na janela da VIVO e da GRAV;
- **a riqueza da S0,** sobre as vidas VIVO de cada célula, como na S3. Inclui a fração perto, os contatos, quem fecha a distância e o
  comer, dormir, explorar e brincar juntos;
- **a comparação com a S3:** o D_A de cada célula ao lado do D_A do pet de hoje na S3. As sementes são outras, e por isso a comparação é
  só descritiva.

## 6. As margens e o N

- **δ_A = 4 decisões,** a do A0 e da S3, SEM FONTE. Ela não muda, para as células se compararem com a S3.
- **O N = 200 por célula é fixo,** como na S3. Não há piloto.
  - Na S3, o dp do D_A no B1 foi 6,88, e a meia-largura 0,96.
  - Com os mecanismos, o dp pode crescer. Se a meia-largura passar de δ_A/2 = 2, o relato diz isso, e a leitura segue a seção 7.
- **Um só valor do alívio, 900 (MD-7).** O alívio é SEM FONTE. Se o M1+M2 der ≈ 0, um segundo valor pede um plano novo. Ele não entra nesta
  run, para que ela mude uma coisa só por braço.

## 7. A regra de leitura, escrita antes

**O A de cada célula, nesta ordem:**

| o G-DET da célula | a PM-1 (só nos braços com o M2) | o D_A | a leitura |
|---|---|---|---|
| falha | qualquer | qualquer | **o substrato não deixa ver:** a célula não diz nada sobre o mecanismo |
| passa | falha | ≈ 0 | **inconclusivo por premissa:** o P1 não aprendeu o valor do outro antes do t0 |
| passa | passa ou não se aplica | **≈ 0** | **nulo com um instrumento que vê:** o mecanismo não faz P responder a F neste substrato |
| passa | qualquer | **< 0** ou **> 0** fora de ±δ_A | **o parceiro responde** |
| passa | qualquer | indeterminado | registrado como está; nada se decide |

**A atribuição, pelos contrastes:**
- **o M1+M2 responde e o C-APR é < 0:** a resposta vem do aprendizado do P1 social com a companhia. É a leitura que o M1-5 buscava;
- **o M1+M2 responde e o C-APR é ≈ 0:** a resposta vem das unidades a mais ou da companhia no corpo, não do aprendizado (o D-SP-62);
- **o M1 responde sem o M2:** o C-APR1 diz se é o `onde_comeu` (o P1 da fome) ou só as unidades a mais;
- **um contraste indeterminado** fica registrado como está.

**O conjunto:**
- **no B1, o M1+M2 responde e o C-APR é < 0:** os mecanismos fazem aparecer um social aprendido. O próximo passo é descrever o caminho e
  levar a decisão do jogo (M1-4 e M2-6) ao Matheus;
- **no B1, o M1+M2 dá nulo com a PM-1 passando:** o valor da solidão não basta para P responder. O próximo passo é um plano novo, com outro
  alívio ou outro mecanismo (o M3 ou o M4);
- **no B1, a PM-1 falha:** o P1 não chega a aprender antes do t0. O próximo passo é olhar a frequência do `seguir` antes do t0, num plano
  novo.

**O que se prevê, PROPOSTO:**
- **o M1 e o M1-inc0:** D_A ≈ 0 no C e no B1, porque o `seguir` não vale nada sem o M2 (a espec do M1, seção 7). No B1, o M1 pode sair de
  ≈ 0 pelo `onde_comeu`;
- **o M1+M2:** a PM-1 passa, e o D_A sai < 0 no B1, com o C-APR < 0;
- **o M1-inc0+M2:** D_A ≈ 0.

Nada disso muda a leitura.

## 8. O código, antes da run (a etapa MD1)

- **A subchave do incentivo social em 0,** na `ConfigDigibrain`, desligada, com um gabarito antes e o G2. Ligada sem a `unidades_sociais`,
  ela levanta erro.
- **O orquestrador:** o `run_v3_social_par_s.py` ganha os braços de mecanismo pela config, ou um orquestrador novo importa o dele. A
  escolha fica para a etapa de código. Em qualquer caso:
  - **G-S3-IGUAL:** com o pet de hoje, o orquestrador refaz duas vidas da S3 (as sementes de teste 101 e 202, nos braços C e B1) com o
    mesmo sha256;
  - **G-INSTR e G1:** em todo par, como na S3;
  - **G-GRAV-COMP:** num teste, na GRAV com a companhia, F recebe a contagem pela posição gravada de P, e a vida se refaz da gravação lida do
    disco;
  - **a PM-1 e os descritivos novos** saem do estado do cérebro de P no t0, gravado no par.
- **A suíte inteira** roda antes da run, com as falhas conhecidas registradas.
- **A etapa de código é um PR próprio,** que para antes da run. A run é outro PR.

## 9. O custo

- **Vidas:** 4 braços × 2 substratos × 200 pares × 5 vidas = 8.000. O G-DET soma 4 × 2 × 50 pares × 3 vidas = 1.200.
- **Tempo:** a S3 rodou 750 pares em 22 minutos com 4 processos. São 2.000 pares, e o tempo previsto é uns 60 minutos de parede, mais o
  custo das unidades sociais na decisão.
- **A máquina:** no máximo 4 processos, e uma run de pesquisa por vez (V3-D8), pelo `pre_run`.

## 10. As decisões (DECIDIDAS pelo Matheus em 2026-11-19, "Aprovado", pela recomendação)

| id | o que decidir | recomendação | custo de errar |
|---|---|---|---|
| **MD-1** | o instrumento | **o da S3, sem mudança** (as cinco vidas, o d0 = 5, o T\*c, a δ_A = 4, o G-DET) | mudar o instrumento junto com o pet tira a comparação com a S3 |
| **MD-2** | os braços de mecanismo | **M1, M1-inc0, M1+M2 e M1-inc0+M2** | sem o M1-inc0+M2, um D_A do M1+M2 pode vir da companhia no corpo ou das unidades a mais, e não do aprendizado |
| **MD-3** | o pet de hoje | **não roda de novo;** a S3 é a referência | baixo: 25 % a mais de custo, se rodar; a comparação com a S3 é só descritiva |
| **MD-4** | os substratos | **o B1 principal e o C secundário;** o B2 fora | baixo: o B2 não teve premissa na S3, e os mecanismos não mexem na bola |
| **MD-5** | as sementes | **a faixa 105001…105400, pedida ao coordenador;** 200 bases e 50 do G-DET, as mesmas nas oito células | baixo |
| **MD-6** | a premissa PM-1 | **o desfecho do `seguir` na solidão < 0 em ≥ 50 % dos P no t0, SEM FONTE** | sem ela, um ≈ 0 do M1+M2 não separa "o pet não responde" de "o pet não aprendeu" |
| **MD-7** | o alívio | **só 900;** outro valor num plano novo | médio: se 900 for pouco, a run dá nulo e pede outra rodada |
| **MD-8** | a ordem | **primeiro a etapa de código (MD1, um PR), depois a run (MD2, outro PR)** | baixo |

## 11. O que fica fora

- **O B2 e a bola** (MD-4).
- **O contágio** (DP-12), **o M3** (a memória por parceiro) e **o M4** (o som e os sentidos longos).
- **Um segundo valor do alívio** (MD-7).
- **O jogo web** (M1-4 e M2-6).
- **Qualquer mudança no `engine.py`, no `mundo.py`** e no instrumento da S3.
