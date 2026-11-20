# SÍNTESE — CORPO: o que o diagnóstico e o conserto permitem concluir (C5, 2026-11-20, Claude Code, Fable 5.2)

Esta é a fase C5 do programa do corpo (C0 a C5, `docs/TAREFA_V3_CORPO.md`). É um documento sem run e sem código: cada número abaixo vem
de um resultado já registrado e de um artefato versionado, com o sha256 na tabela das fontes. A especificação da primeira mudança está
em [ESPEC_CORPO_V1.md](ESPEC_CORPO_V1.md).

**O que abriu a C5:** no CHECKPOINT da C4, a leitura foi "confirma com ressalva" e o Matheus respondeu "Aceito, seguir à C5"
(2026-11-20, nesta sessão). A ressalva aceita é a célula do aleatório no comedouro (seção 4).

**Em uma frase:** no pet da bancada, pôr a falta de combustível na fome, com um teto em C/2, faz o pet passar mais tempo bem, comer mais
e dormir menos, sem reprovar nenhuma guarda; isso foi validado uma vez, em sementes novas, e ainda não foi medido no pet do jogo.

## 0. As fontes

| fase | o quê | documento | artefato (sha256) |
|---|---|---|---|
| A1 | o modular contra a baseline trivial (a pergunta que motivou o programa) | `docs/RESULTADO_V3_BASELINE_TRIVIAL.md` | `artifacts_v3_baseline_trivial/validacao/resultado.json` (`706a687a0b56dbee52b11710b3f906f84babc4a27ca2bf45613f630f9bf63b6c`) |
| C0 | o mapa do corpo e a sonda, nas sementes dos testes | `docs/MAPA_CORPO.md` | `artifacts_v3_corpo_acoplamento/sonda.json` (`f4f5962cae28521def685ee2d31ff895a60f0f0baedb190ec9f09137941ecbf4`) |
| a D | a opção D sozinha, numa run | `docs/RESULTADO_V3_CORPO_ACOPLAMENTO.md` | `artifacts_v3_corpo_acoplamento/run/resultado.json` (`20136834d15d481947e5b752c0d582f1d49aa96990d47ac0104b4f70b063f8f5`) |
| C1 e C2 | o plano e a ablação (D, D + E e D + C5) | `docs/PLANO_ANALISE_V3_CORPO.md`, `docs/RESULTADO_V3_CORPO.md` | `artifacts_v3_corpo/ablacao/resultado.json` (`daf59ef831fd8649e711a95d6a64964b3b21c7a47e1fbc27b664779e84ee2eb8`) |
| C2.5 | o diagnóstico, sem vida nova | `docs/RESULTADO_V3_CORPO.md`, seção 5 | `artifacts_v3_corpo/diagnostico_c25/diagnostico.json` (`a9c17057e309dc3582f19c89b5efed925f628c2a519a29003d6c6da1f0de25d0`) |
| C3 | a ponte com teto (D, DTL e DTB), a run que escolheu o braço | `docs/RESULTADO_V3_CORPO_C3.md` | `artifacts_v3_corpo/c3/resultado.json` (`b326081209127999bf9982872a2da772a57ffb45eb69b663b2d945a89dd0b21d`) |
| C3, replay | o "Tempo bem" nas vidas da C3 | `docs/PLANO_ANALISE_V3_CORPO_C4.md`, seção 5.3 | `artifacts_v3_corpo/c3_tempo_bem/resumo.json` (`45373085a8b78b2089918415bc2d47ec91c63f1e9987f1126d4ebcfa02f4595f`) |
| C4 | a validação do DTB, em sementes novas | `docs/RESULTADO_V3_CORPO_C4.md` | `artifacts_v3_corpo/c4/resultado.json` (`136c304837710a8bf543c63530ad44b6b898784e1dfc84b4ef574359b7969f2d`), `medidas.json` (`c20881a8e10e539c66b30e33661bd4a985d1dc2e16b8da095790c9d57c06e8a7`) |
| a bola | por que a bola não é chutada nos pares (o R-b) | `docs/RESULTADO_V3_BOLA_DIAGNOSTICO.md` | `artifacts_v3_bola_diagnostico/` |

Os números entre colchetes são o IC95 pelo t sobre as unidades. As classes ("> 0", "≈ 0", "< 0") são as da A6.6, com δ = 0,032 (SEM
FONTE).

## 1. A causa

**O que o mapa descreveu** (C0, a sonda nas sementes dos testes; descritivo, não contrafactual):
- **Uma causa comum.** O jejum sobe a fome pelo relógio dela e sobe o cansaço por uma ponte: com o combustível abaixo de C/4, o corpo de
  hoje soma +500 por tick no cansaço.
- **Dois fechos do laço.** O reflexo do sono é um override: o pet com fome e cansado dorme, e dormindo não come. E a digestão só converte
  o que a fome deixa, então o combustível não se recupera.
- **O tamanho na sonda:** a ponte foi a maior fonte de cansaço em 0,767 das decisões com a fome urgente e a energia baixa
  (`docs/MAPA_CORPO.md`, seção 6).

**O que a intervenção confirmou** (a run da D e a C2: trocar o alvo da ponte, do cansaço para a fome):
- **A ponte é causa da exaustão e dos conflitos.** Com a D, os conflitos caem de 0,147 para 0,099 das decisões (−0,048
  [−0,050; −0,046]), a exaustão cai −0,078 [−0,081; −0,075] nas 12 células, e o pet dorme menos (de 0,465 para 0,376 dos ticks)
  (`docs/RESULTADO_V3_CORPO_ACOPLAMENTO.md`, seções 2 e 3).
- **O forrageio sobe:** a taxa por episódio de fome no `longe_fixo` sobe +0,115 [+0,102; +0,129] na run da D e +0,120 [+0,105; +0,136]
  na C2.

**O que a intervenção não confirmou:**
- **A coincidência condicional quase não muda.** A fração das decisões com a energia baixa em que a fome também é urgente vai de 0,613
  para 0,606 (−0,007 [−0,012; −0,001]). O que cai é a frequência da energia baixa (de 0,196 para 0,131), não a ligação entre as duas
  quando ela acontece.

**A segunda causa, achada no caminho** (C2 e C2.5):
- **A D sozinha cobra saúde de quem não tem comida.** A fome só cai comendo. Com os donos que deixam faltar comida (o relapso e o
  aleatório), a fome passa do limiar da privação, e o dano da privação é um degrau. Na C2.5, a saúde caiu de −0,119 a −0,236 nessas
  células (`docs/RESULTADO_V3_CORPO.md`, seção 5.3). Por isso a D saiu em "perda" na C2 e de novo na C3.
- **A E e a C5 não resolvem:** a D + E sai em "perda" pela mesma guarda, e a D + C5 quase dobra a exaustão (0,232 → 0,435)
  (`docs/RESULTADO_V3_CORPO.md`, seção 2).

## 2. O conserto

**O DTB:** a ponte da D com um teto baixo.
- **A regra:** com o combustível abaixo de C/4, a fome sobe `min(500, max(0, T_B − fome))` por tick, com T_B = 225 000 (C/2). Acima do
  teto, a falta não sobe nem a fome nem o cansaço; a fome continua subindo só pelo relógio dela.
- **Por que o teto fica abaixo do limiar:** o limiar da privação é 382 500. A C3 mediu o teto no próprio limiar (o DTL), e ele saiu em
  "perda", quase igual à D: o dano vem da chegada mais cedo ao limiar, e cortar a ponte só ali tira pouco
  (`docs/RESULTADO_V3_CORPO_C3.md`).
- **Onde está:** a `ConfigAcoplamentoCorpo` (a D) e a `ConfigTetoFomeCorpo` (o teto), em `digilab/config.py`, lidas em
  `digilab/corpo.py`; o espelho em `web/app/motor/corpo.ts`, com o gabarito `tests/gabaritos/corpo_teto_python.json` reproduzido
  inteiro a inteiro. As duas chaves estão desligadas por padrão, no Python e no jogo.
- **O status do número:** o T_B é PROPOSTO e SEM FONTE. A C3 testou dois tetos (C/2 e o limiar) e a C4 validou um.

## 3. O efeito no forrageio

| medida, DTB − CTRL | C3 | C4 (sementes novas) |
|---|---|---|
| a taxa por episódio de fome, `longe_fixo` | +0,120 [+0,105; +0,135] | +0,126 [+0,112; +0,140] |
| a taxa por episódio, 12 células | — | +0,095 [+0,088; +0,102] |
| refeições por dia, 12 células | — | +0,45 (3,15 → 3,60) |
| episódios de fome por vida, 12 células | — | +3,8 (13,9 → 17,7) |

- **O forrageio sobe e se repete** em sementes novas. Na C4 a taxa por episódio é guarda, e passa.
- **O DTB não perde forrageio contra a D:** na C3, DTB − D na taxa por episódio é −0,004 [−0,015; +0,007].
- **O pet tem mais episódios de fome e fecha uma fração maior deles.** Por que há mais episódios não foi explicado (seção 6).

**O que isso muda no veredito da A1: nada demonstrado.**
- **A A1** mediu o modular contra uma baseline trivial e achou REL − TRIV = −0,083 [−0,128; −0,038] na taxa por episódio do
  `longe_fixo`: a baseline vence no forrageio (REL 0,562, TRIV 0,645).
- **O programa previa** refazer essa comparação na C4, com o conserto ligado no REL. **O plano aprovado da C4 mudou isso:** ele comparou
  o DTB com o CTRL (o mesmo cérebro, dois corpos), com o "Tempo bem" como primária. A TRIV não entrou.
- **Ao lado, só descritivo:** o DTB chega a 0,698 no `longe_fixo` (C4), acima do 0,645 da TRIV (A1). São duas runs com sementes
  diferentes, e esse par não é um contraste.
- **O que a A1 já mostrava e continua valendo:** a TRIV vence no forrageio vivendo em privação (0,986 das decisões no `longe_fixo`,
  contra 0,382 do REL). A taxa por episódio sozinha não mede o bem-estar, e por isso a primária passou a ser o "Tempo bem" (D-MP-1).

## 4. O efeito no bem-estar

**A primária da C4, o "Tempo bem"** (a fração das decisões dos dias 1 a 14 sem privação e sem exaustão):

| onde | CTRL | DTB | DTB − CTRL | classe |
|---|---|---|---|---|
| as 12 células | 0,633 | 0,695 | +0,062 [+0,058; +0,067] | > 0 |
| as 11 células distintas | 0,608 | 0,672 | +0,064 [+0,059; +0,068] | > 0 |
| comedouro | 0,757 | 0,786 | +0,029 [+0,027; +0,031] | ≈ 0, sinal + |
| longe | 0,528 | 0,598 | +0,070 [+0,062; +0,078] | > 0 |
| `longe_fixo` | 0,613 | 0,701 | +0,088 [+0,078; +0,098] | > 0 |

- **De onde vem o ganho:** nas 12 células, a exaustão da vida desce −0,080 e a privação desce −0,038.
- **A saúde:** +0,056 [+0,049; +0,064] nas 12 células, e +0,013 [+0,005; +0,022] nas 6 células do relapso e do aleatório. Nenhuma das
  sete guardas reprova.
- **O ganho é maior com os donos que alimentam** (de +0,048 a +0,155 no "Tempo bem" por célula) e menor com o relapso e o aleatório
  (de −0,001 a +0,050).

**Onde não melhora:**
- **O comedouro.** O "Tempo bem" sobe pouco, a privação da vida sobe +0,008 [+0,006; +0,010] e a saúde média desce −0,012
  [−0,016; −0,009]. Tudo dentro de δ.
- **A ressalva aceita, o aleatório no comedouro.** A saúde cai −0,049 [−0,061; −0,038] (na C3, −0,048), a privação sobe +0,026, e o
  "Tempo bem" não muda (−0,001 [−0,005; +0,002]). No corpo de hoje o pet já vive mal ali (saúde 0,397).
- **O relapso no comedouro** vai na mesma direção, em tamanho menor: a saúde desce −0,008 [−0,010; −0,006].

## 5. O efeito no substrato social

Nenhum mecanismo social entrou no programa. O que foi medido é o substrato: o que o corpo deixa disponível para o social.

| medida | CTRL | DTB | fonte |
|---|---|---|---|
| o tempo até o reencontro nos pares (S2), em decisões | 10,79 | 7,49; DTB − CTRL −3,30 [−4,31; −2,29] | C4, 500 pares por braço |
| a fração dos ticks dormindo | 0,465 | 0,377 | C4, 12 células |
| as escolhas de "brincar" por vida | 26,7 | 46,1 | C4, 12 células |
| chutes na bola por vida, `longe_fixo` | 2,49 | 2,72; +0,23 [+0,05; +0,41] | C4, descritivo |
| chutes na bola por vida, longe | 0,95 | 1,38; +0,44 [+0,24; +0,63] | C4, descritivo |

- **O pet fica mais tempo acordado, brinca mais e reencontra o outro mais cedo.** O S2 é guarda na C4, e passa.
- **A bola nos pares não mede nada.** Nenhum par chutou a bola na C2 nem na C3. O R-b mostrou por quê: nos pares, a bola nunca entra
  no raio da visão do pet. Por isso a C4 tirou a bola dos pares e levou os chutes das vidas de um pet como descritivo.
- **Os chutes a mais são descritivo,** sem teste. A contagem nas sementes dos testes tinha dado o contrário, com 5 unidades.

## 6. O que ficou sem explicação

- **Os episódios de fome a mais do DTB** (+3,8 por vida). O replay da fome, acrescentado depois da aprovação da C4, pode ajudar; ele
  ainda não tinha rodado quando esta síntese foi escrita.
- **Por que a saúde cai no aleatório do comedouro** e não no aleatório do longe. O mecanismo da D (a fome só cai comendo) explica a
  direção. O tamanho por lugar não foi investigado.
- **O teto.** C/2 é um número só. Nada diz se ele é o melhor, nem onde o dano começa entre C/2 e o limiar.
- **A coincidência condicional** entre a fome urgente e a energia baixa (seção 1): o conserto reduz a frequência, não a ligação.
- **O incoerente no comedouro** sai igual ao atencioso (200 de 200 vidas na C4). As 12 células têm 11 distintas. A causa exata espera
  o replay dos donos.
- **O déficit de combustível** que o mapa calculou (0,267 C por dia, mesmo comendo tudo o que a fome deixa) não foi medido de novo com
  o DTB.

## 7. O que isso muda na visão

A visão do projeto é um pet com corpo: órgãos, químicos e um cérebro que lê o corpo. Ela só se sustenta se o pet consegue agir sobre o
que sente. O programa do corpo diz três coisas sobre isso. As duas primeiras são medidas; a terceira é leitura.

- **Medido: no corpo de hoje, um sinal apontava para a ação errada.** A falta de combustível aparecia como cansaço. O pet respondia
  dormindo, e dormir não traz combustível. Trocar o alvo da ponte tira exaustão e conflitos (seção 1).
- **Medido: pôr o sinal no canal certo não basta.** A D sozinha põe a falta na fome, que só a comida resolve, e cobra saúde de quem
  não tem comida. O teto abaixo do limiar é o que tira esse custo (seções 1 e 4).
- **Leitura, não medida: o desenho do corpo decide o que o cérebro consegue aprender.** O cérebro foi o mesmo nos dois braços. O que
  mudou foi qual necessidade o corpo acusa, e o comportamento mudou junto (mais refeições, menos sono, mais tempo bem). Nenhuma run
  separou quanto disso é aprendizado e quanto é reflexo.

**O que a visão ainda não tem daqui:** nada sobre hormônios ou genomas (o programa não mexeu neles), nada sobre o jogador perceber a
diferença, e nada sobre o pet do jogo (seção 8).

## 8. O que não foi demonstrado

- **O pet do jogo.** As vidas de um pet da C2, da C3 e da C4 usam o pet da bancada: o modular com a memória e o corpo v11, sem o "sono
  que segura", sem o lance do dono e sem o equilíbrio do cuidado, que o pet v38 do jogo tem (`experiments/run_v3_corpo_c3.py`,
  `fabricas`). O efeito do DTB no pet v38 não foi medido. É o primeiro passo da especificação.
- **O jogo web.** A paridade do corpo com o teto existe (inteiro a inteiro, no gabarito). Nenhuma vida do jogo rodou com a chave
  ligada, e nenhuma versão de pet a liga.
- **O modular contra a baseline trivial** com o corpo consertado (seção 3).
- **Outro teto** além de C/2 e do limiar.
- **Um dono de verdade.** Os quatro donos são os da bancada.
- **O social.** Só o substrato foi medido; nenhum mecanismo social entrou.
- **A réplica.** A run da C4 não foi refeita do zero; o `medidas.json` sem o relógio permite a réplica byte a byte.
- **Nenhuma novidade é alegada.**

## 9. O que fica para o Matheus (o CHECKPOINT da C5)

As decisões estão na [ESPEC_CORPO_V1.md](ESPEC_CORPO_V1.md), seção 8, cada uma com a recomendação e o custo de errar:
- se o DTB vai ao jogo, e por qual caminho;
- se o T_B passa de PROPOSTO a DECIDIDO;
- se a comparação com a baseline trivial é refeita.
