# Plano de análise V3: a ponte com teto (CORPO C3)

**Status: PROPOSTO, esperando o Matheus.** A direção foi escolhida por ele em 2026-11-19 ("Ponte com teto", a opção 1 da seção 5.5 do
`docs/RESULTADO_V3_CORPO.md`): a falta de combustível sobe a fome só até o limiar da privação. As decisões da seção 9 estão abertas, e
nenhuma vida desta run existe. A faixa está pedida ao coordenador (D-C3-7).

## 0. A trava e o que já foi visto

**A trava:** o orquestrador recusa a run sem a palavra APROVADO neste status, como na C2.

**O que já foi visto antes deste plano:**
- **A run da D** (#1002, faixa 100101…100505) e **a ablação da C2** (#1012, faixa 104001…104400): a D sobe o forrageio e baixa a exaustão,
  mas reprova pela privação do comedouro.
- **O diagnóstico da C2.5** (#1014, o `docs/RESULTADO_V3_CORPO.md`, seção 5, sobre as vidas gravadas da C2): a D tira a falta de
  combustível do cansaço, que o sono resolve, e a põe na fome, que só a comida resolve.
  - Com o atencioso e o incoerente, o pet come mais e a privação cai.
  - Com o relapso e o aleatório, não há comida a mais, a fome passa do limiar, e o dano da privação baixa a saúde (−0,12 a −0,24).
- **O achado do instrumento:** no comedouro, as vidas do incoerente saem iguais às do atencioso (400 de 400).

**Nenhum número deste plano é calibrado nessas runs.** Elas só escolhem o que testar: o teto, a guarda da saúde (que nasce do
diagnóstico) e a pergunta do incoerente.

## 1. A pergunta e a hipótese, escritas antes

**A pergunta:** a ponte da D com teto mantém o ganho de forrageio da D e tira o dano da fome que o pet não tem como resolver?

**O que o mecanismo prevê, escrito antes** (pelo código: `digilab/corpo.py`, os emissores `falta_combustivel`, `fome_tick` e
`dano_privacao`):
- **O dano da privação é um degrau.** Cada tick com a fome acima do limiar (85 % de C) custa o mesmo dano, por mais alta que esteja a fome.
- **O dano a mais da D vem de a fome chegar mais cedo ao limiar,** 875 por tick em vez de 375 com o combustível abaixo de C/4, e não de ela
  subir mais alto depois.
- **Por isso, um teto exatamente no limiar deve tirar pouco do dano.** Ele não muda a hora da chegada. Ajuda só um pouco: depois de uma
  refeição, a fome desce de um ponto mais baixo e demora mais para voltar.
- **Um teto mais baixo atrasa a chegada,** porque de lá ao limiar só sobe a fome basal, como no CTRL. Mas também tira parte do empurrão
  para comer, que é o ganho da D com os donos bons.

Por isso o plano propõe dois tetos (D-C3-2): o do limiar, a escolha do Matheus, e um mais baixo, para ver se o dano se resolve.

**Hipóteses:**
- **H1, o teto no limiar:** sai perto da D, o F sobe e a privação do comedouro sobe também. A previsão é "perda" pela mesma guarda.
- **H2, o teto baixo:** a privação e a saúde dos donos que deixam faltar comida ficam perto do CTRL, e o F sobe menos que na D.

## 2. Os braços

| braço | a ponte da falta de combustível (abaixo de C/4) |
|---|---|
| **CTRL** | sobe o cansaço em 500 por tick, como hoje |
| **D** | sobe a fome em 500 por tick, a D da C2, como referência pareada |
| **DTL**, o teto no limiar | sobe a fome em até 500 por tick, só até a fome química chegar a T_L = 382 500 (85 % de C, o limiar da privação) |
| **DTB**, o teto baixo (se a D-C3-2 for aprovada) | igual, só até T_B = 225 000 (C/2) |

**A regra do teto, para as duas:** num tick com a falta, a ponte soma à fome `min(500, max(0, T − fome))`. A fome basal (`fome_tick`,
+375) continua igual nos quatro braços. Acima de T, a falta não sobe nem a fome nem o cansaço.

**Os números:**
- **T_L = 382 500** não é número novo: é `C × (1 − limiar_privacao)`, o ponto em que o `Estado.em_privacao` passa a valer pela fome.
- **T_B = C/2 é PROPOSTO, SEM FONTE.** É a metade do caminho, a fome do `Estado` em 0,5.
- **O 500 continua** o `falta_fome` da D.

**O que fica de fora:** a E e a C5. A E não segurou a privação no comedouro, e a C5 reprovou pela exaustão (#1012). A ponte dividida e a
ponte com transbordo para o cansaço acima do teto ficam fora (D-C3-3).

## 3. As células e as unidades

As mesmas da C2: as 12 células da C4 (os 4 donos × o comedouro, o longe e o `longe_fixo`), 200 sementes independentes (200 bases, k = 1,
derivação `digibrain_prototipo`), 14 dias e orçamento 16. Cada unidade dá o mesmo pet e o mesmo mundo a todos os braços.

## 4. A run

| item | valor |
|---|---|
| bloco I | 4 braços × 12 células × 200 unidades = **9 600 vidas** (7 200 sem o DTB) |
| bloco II | 4 braços × 100 pares, o instrumento da C2 (SOCIAL_PAR A0, só VIVO, 5 dias) |
| faixa | **106001…106400, PEDIDA ao coordenador** (D-C3-7): as bases 106001…106200 para o bloco I, e as 106301…106400 (prefixo `corpo_par`) para o bloco II |
| custo | cerca de 2 h com 4 processos (a C2 fez 9 600 vidas em 2 h 6 min) |
| processos | no máximo 4, uma run de pesquisa por vez |

A run roda **uma vez**. A fumaça usa as sementes dos testes.

## 5. As medidas e a regra de leitura, escritas antes

**O contraste:** braço − CTRL, pareado por unidade, com o t (`orq.contraste_t`) e as classes da A6.6, com δ = 0,032 (SEM FONTE, o da C2).

**F, o primário:** a taxa de fechamento por episódio de fome no `longe_fixo`, a medida da A1 e da C2. O p é unilateral para braço − CTRL
> 0, com o **Holm sobre os braços com teto** (DTL e DTB; só o DTL sem a D-C3-2), α = 0,025. A D não entra no Holm: é a referência.

**B, o bem-estar, vinculante:**
- **a privação:** no comedouro, no longe, no `longe_fixo` e nas 12 células, como a ressalva 3 da C2 (D-CO-10); reprova com "> 0";
- **a exaustão:** no `longe_fixo` e nas 12 células; reprova com "> 0";
- **a saúde (nova, D-C3-4):** a saúde média do `Estado` na janela dos dias 8 a 14, nas 12 células e nas 6 células dos donos que deixam
  faltar comida (o relapso e o aleatório, nos três lugares); reprova com "< 0". É a medida do dano que o diagnóstico achou.

**S, o substrato social (D-C3-5):** o S2, o tempo até o reencontro, reprova com "> 0". O S1, os chutes por dia, vai como descritivo,
porque na C2 nenhum par chutou.

**A leitura de cada braço com teto:**

| leitura | F | B e S |
|---|---|---|
| **ganho** | "> 0" e o Holm rejeita | nenhuma das oito guardas do bem-estar reprova, e o S2 passa |
| **perda** | "> 0" e o Holm rejeita | alguma guarda reprova |
| **nulo** | "≈ 0", "< 0", ou "> 0" sem o Holm | qualquer |
| **indeterminado** | "indeterminado" | qualquer |

**O descritivo, sem teste:**
- **braço − D,** nas mesmas medidas: quanto o teto custa em forrageio e quanto devolve em privação e saúde;
- **por dono,** as contas da seção 5.2 do diagnóstico, com as refeições por dia;
- **a decomposição da privação,** a do `experiments/diagnostico_v3_corpo_c25.py`: só a fome, acordado ou dormindo;
- **a fração dos ticks com a ponte no teto,** e a fome química média nesses ticks.

**A pergunta do instrumento: o incoerente e o atencioso (D-C3-6).** Ela não muda o primário nem as guardas, e é respondida no resultado:
- **(a)** quantas vidas do incoerente saem iguais às do atencioso, em cada lugar e em cada braço;
- **(b)** por que, pelo código: o incoerente difere do atencioso só no que o pet recebe e o cérebro não usa nesse lugar? A resposta é
  lida, não consertada aqui;
- **(c)** a sensibilidade: o F e as guardas das "12 células" refeitos também sobre as 11 células distintas, sem a cópia, ao lado do número
  oficial.

Um conserto do dono, se houver, vai num plano próprio.

## 6. Os artefatos

Em `artifacts_v3_corpo/c3/`: `resultado.json`, `medidas.json` (em `.gz` se passar de 100 MB), `pares.json`, `vidas.tar.gz`,
`pares.tar.gz` e `meta.json`, com o sha256 de cada um, do plano, do orquestrador e das configs.

## 7. A implementação, depois da aprovação

- **A chave:** um campo novo na `ConfigAcoplamentoCorpo`, o `teto_fome: int | None = None`. Com `None`, a D de hoje sai byte a byte. O
  gabarito da D (`tests/gabaritos/corpo_acoplamento_*.json`) e o de hoje não mudam.
- **O status:** em `PARAMETROS_ACOPLAMENTO_CORPO`, com o T_L DECIDIDO (derivado do limiar, pela escolha do Matheus) e o T_B PROPOSTO,
  SEM FONTE.
- **O web:** o espelho em `web/app/motor/corpo.ts`, com um gabarito de paridade novo, num arquivo próprio. A chave fica desligada no jogo.
- **O orquestrador:** o `experiments/run_v3_corpo.py` ganha a fase `c3` (os braços, a guarda da saúde e o descritivo da seção 5), com a
  fumaça e os testes.
- **A ordem:** este plano na `main`, depois o código num PR próprio, depois a run. Nenhuma vida antes dos dois.

## 8. A ordem do programa

Ganho de um braço com teto leva à C4, a validação, pelo programa. Perda ou nulo dos dois volta ao Matheus, com a opção de não mudar o
corpo (a opção 3 da seção 5.5 do resultado).

## 9. As decisões

- **D-C3-1 (DECIDIDA pelo Matheus em 2026-11-19, "Ponte com teto"), a direção:** a ponte da D com teto no limiar da privação.
- **D-C3-2 (PROPOSTA), o segundo teto:** o braço DTB, com T_B = C/2, SEM FONTE.
  - **Por quê:** o mecanismo prevê que o teto no limiar tire pouco do dano (a seção 1). Sem um teto mais baixo, a run pode só confirmar a
    perda.
  - **A recomendação:** incluir. Custa 2 400 vidas, cerca de 30 min.
  - **O custo de errar:** sem o DTB, uma perda do DTL não diz se algum teto serve, e a pergunta volta numa run nova.
- **D-C3-3 (PROPOSTA), o que fica de fora:** a E, a C5, a ponte dividida e o transbordo para o cansaço acima do teto.
  - **A recomendação:** deixar fora, para a run responder só à pergunta do teto.
  - **O custo de errar:** se nenhum teto servir, o transbordo seria o próximo candidato, numa run nova.
- **D-C3-4 (PROPOSTA), a guarda da saúde:** a saúde média na janela dos dias 8 a 14, nas 12 células e nas 6 células do relapso e do
  aleatório, reprova com "< 0", com δ = 0,032.
  - **Por quê:** a privação mede o tempo abaixo do limiar, e a saúde mede o dano. O diagnóstico achou o dano onde a média das 12 células o
    dilui.
  - **O custo de errar:** sem ela, um braço pode passar com o dano escondido nas células dos donos que deixam faltar comida. Com ela, a
    regra fica mais estrita do que a da C2.
- **D-C3-5 (PROPOSTA), o bloco II:** o S2 como guarda e o S1 como descritivo. Muda a forma da ressalva 2 da C2 (D-CO-6) só no S1.
  - **A recomendação:** aceitar, porque o S1 não mediu nada na C2 (zero chutes).
  - **O custo de errar:** um efeito na bola passaria sem guarda, mas o instrumento não o veria de qualquer jeito.
- **D-C3-6 (PROPOSTA), a pergunta do incoerente:** as três leituras da seção 5, sem mexer no dono nem no primário.
  - **O custo de errar:** se a cópia for um defeito do dono, as médias das 12 células da C2 e desta run pesam o atencioso duas vezes no
    comedouro. A sensibilidade (c) mostra quanto isso muda.
- **D-C3-7 (PEDIDA ao coordenador), a faixa 106001…106400:** conferida livre no `faixas.py`, nas configs e nos planos de todos os branches
  remotos em 2026-11-19.
- **D-C3-8 (PROPOSTA), os tamanhos:** os da C2, com 200 unidades, 14 dias e δ = 0,032. A C2 deu meias larguras de IC de 0,015 no F e
  abaixo de 0,01 nas guardas das 12 células, abaixo de δ.
