# PLANO DE ANÁLISE V3 — CORPO_ACOPLAMENTO: a opção D numa run

**Status: APROVADO pelo Matheus em 2026-11-18** ("Aprovo, siga", na sessão lateral), com as D-CA-9 a D-CA-12 como recomendadas.
Nenhum orquestrador e nenhuma vida de faixa existiam antes da aprovação.

Escrito em 2026-11-18 por Claude Code (Opus 5.5, sessão lateral), no branch `v3-corpo-acoplamento-plano`, empilhado no #995. Ele segue a
D-CA-8 (a), que o Matheus escolheu: "(a) Plano da D". A tarefa é a [TAREFA_V3_CORPO_ACOPLAMENTO.md](TAREFA_V3_CORPO_ACOPLAMENTO.md), e o
plano da VALUATION que ele segue é o [PLANO_ANALISE_V3_VALUATION_CONSERTO.md](PLANO_ANALISE_V3_VALUATION_CONSERTO.md).

## 1. De onde vem

- **A VALUATION** ([RESULTADO_V3_VALUATION_CONSERTO.md](RESULTADO_V3_VALUATION_CONSERTO.md), seção 3): no REL, a fome está urgente em 0,635
  das decisões com a energia abaixo de `lambda_sono`. O pet não pode comer e descansar ao mesmo tempo, e o conserto do reflexo falhou na
  exaustão.
- **A etapa 1** (a seção 9 da tarefa) achou a causa no corpo. O jejum esvazia o combustível, e a ponte ME-1 sobe o cansaço: a falta de
  combustível é a maior fonte de cansaço do dia (0,829 C por dia).
- **A etapa 2** (a seção 11 da tarefa) pôs a opção D atrás de uma chave: a falta de combustível sobe a fome, e não o cansaço. Na sonda
  descritiva, nas sementes dos testes:
  - as decisões com as duas caem 30 % (de 0,150 para 0,105 das decisões);
  - a fome urgente na energia baixa fica em 0,761;
  - o pet dorme menos (de 0,465 para 0,375 dos ticks).

  Essas medidas não têm IC, e a etapa não mediu a privação, a exaustão nem a taxa por episódio.

**A pergunta da run:** com a chave D ligada, a vida da VALUATION tem menos decisões em que o pet precisa comer e descansar ao mesmo tempo,
sem piorar a privação, a exaustão e a taxa de fechamento dos episódios de fome?

## 2. A mudança

A chave já está no código (#995): a `ConfigAcoplamentoCorpo` (`digilab/config.py`).
- **Ligada,** o emissor `falta_combustivel` sobe a fome em `falta_fome` = 500 por tick, e não o cansaço.
- **O 500** é PROPOSTO, SEM FONTE: é o `falta_cansaco` de hoje.
- **A run não calibra o `falta_fome`:** mede o ponto de partida, uma vez.

Nada mais muda entre os braços.

## 3. Os testes do código

**Já existem**, no #995:
- **"desliga não muda":** o gabarito das vidas de hoje (`tests/gabaritos/corpo_acoplamento_de_hoje.json`), gravado antes do código.
- **A unidade:** um tick com e sem a falta; a ponte troca de alvo; as falhas altas (`tests/test_corpo_acoplamento_chave.py`).
- **A paridade TS:** `web/app/test/corpo_acoplamento.test.ts`. A web não roda nesta run.

**Entram com o orquestrador, depois da aprovação** (a seção 7):
- **A conferência de cada vida, com falha alta:**
  - o corpo do braço tem a ponte do braço: o cansaço no REL, a fome no D;
  - no D, nenhum tick sobe o cansaço pela falta;
  - o replay do disco sai igual;
  - as conferências da VALUATION (o T-CENARIO-1, as da C4).
- **O REL daqui é a vida do REL da VALUATION**, byte a byte (o mesmo `viver`).

## 4. A run

| item | valor |
|---|---|
| braços | **REL** (o da C4 e da VALUATION) e **D** (o REL com a `ConfigAcoplamentoCorpo` ligada); uma mudança só |
| células | as 12 da C4: os 4 donos × comedouro, longe e `longe_fixo` |
| unidades | 200, pela derivação `digibrain_prototipo`, K = 40 por base |
| faixa | **100101…100505**, PROPOSTA (D-CA-10), bases 100101, 100202, 100303, 100404 e 100505 |
| dias | 14, orçamento 16 (os da VALUATION) |
| vidas | 2 × 12 × 200 = **4 800** |
| custo | a VALUATION levou 1 h para 4 800 vidas com 4 processos: cerca de 1 h |

- A run roda **uma vez**, com no máximo 4 processos e sem outra run de pesquisa do DigiLab ao mesmo tempo (V3-D8).
- **A trava,** como na VALUATION: o orquestrador recusa rodar sem o "APROVADO pelo Matheus" no cabeçalho deste plano, sem a faixa em
  `FAIXAS_RESERVADAS` e com a pasta de saída já existente. A fumaça usa as sementes dos testes.

## 5. As medidas e a regra de leitura, escritas antes

**O contraste:**
- A unidade é (base, semente), e o contraste é D − REL, pareado por unidade.
- O teste é o t (o `orq.contraste_t` da C4 e da VALUATION).
- As classes são as da A6.6 (`run_v2_longe_regular.classe`), com δ = 0,032, SEM FONTE, a da VALUATION (D-VAL-20).

**A medida nova:** os **conflitos** de uma vida são a fração das decisões com a energia abaixo de `lambda_sono` e a fome urgente (a urgência
da fome do M-AFETO acima do `urgencia_lambda`).
- O denominador é o total de decisões da vida, não só as com a energia baixa.
- A contagem vem da mesma leitura da VALUATION: o invólucro do `Arbitragem.reflexo` e o motivo.

**Os critérios:**

| critério | medida | passa se |
|---|---|---|
| **P, "menos conflitos"** | os conflitos, média das 12 células | classe **"< 0"** e p unilateral < 0,025 |
| **G1, a privação** | a privação, no `longe_fixo` e nas 12 células | nenhuma das duas em "> 0" |
| **G2, a exaustão** | a exaustão, no `longe_fixo` e nas 12 células | nenhuma das duas em "> 0" |
| **G3, a taxa por episódio** | a taxa de fechamento por episódio de fome, no `longe_fixo` e nas 12 células | nenhuma das duas em "< 0" |
| **D, "desliga não muda"** | o gabarito da seção 3 | o teste passa antes da run |

As medidas da G1, da G2 e da G3 são as da VALUATION (`run_v3_valuation`: `PRIVACAO`, `EXAUSTAO`, `EPISODIO`).

**A leitura:**
- **passa:** P, G1, G2, G3 e D passam;
- **efeito trivial:** a P sai "≈ 0" com o sinal −. Conta como falha;
- **falha:** qualquer critério que não passa. O resultado fica registrado como está, e a chave continua desligada.

**Por que sem Holm:** há um primário só. As G são guardas, todas vinculantes, como na VALUATION.

**O poder** (a conta com os dois artefatos da etapa 2; os 60 pares REL × D de `sonda_e2_hoje.json` e `sonda_chave_d.json`, por vida):
- a diferença média dos conflitos foi de −0,045;
- o desvio-padrão por célula foi de 0,054, e o da média das 12 células, com 5 unidades, de 0,023;
- **o σ de planejamento é 0,064:** o desvio por célula, o mais alto, com uma folga de 20 %;
- com n = 200, a meia largura do IC95 fica perto de 1,97 × 0,064 / √200 = **0,009**, bem abaixo de δ = 0,032.

**O risco do primário:** o efeito nas sementes dos testes (−0,045) é só 1,4 δ. Na faixa da VALUATION, a coincidência foi menor (0,635
contra 0,759), e o efeito pode sair menor. Um efeito entre −0,032 e 0 cai no "≈ 0", o efeito trivial.

**Ao lado, sem classe:**
- a fome urgente na energia baixa e na energia boa: a fração que motivou a tarefa;
- as decisões com a energia baixa por vida;
- a fração dos ticks dormindo;
- o cansaço por fonte e o combustível abaixo de C/4;
- os descritivos da 5.3 da VALUATION: as refeições por dia, a `janela_vencida`, a fração de `dormir` e de `comer` no episódio, os reflexos
  por vida e a latência.

O bootstrap e o g1 vão rotulados, como na VALUATION.

**O que a run não demonstra:**
- **nada sobre o jogo web:** a chave fica desligada nele (D-CA-7);
- **nada sobre o I-PAD da LONGE_GEOMETRIA.** O sono muda, e o I-PAD vem do sono; medir de novo é outra run;
- **nada sobre a calibração do cuidado** (E1 e E2);
- **nada sobre outro `falta_fome`** além do 500, nem com o conserto da VALUATION ou o sono que segura ligados;
- nada fora dos 14 dias e do mundo do MVP.

## 6. Os artefatos

Em `artifacts_v3_corpo_acoplamento/run/`, como na VALUATION:
- `resultado.json`, `medidas.json` e `vidas.tar.gz`, determinístico;
- `meta.json`, com o comando, o commit, a árvore limpa, o `plano_sha256`, a faixa, os braços e o sha256 de cada artefato.

## 7. A implementação, depois da aprovação

- **O orquestrador:** `experiments/run_v3_corpo_acoplamento.py`. É o `run_v3_valuation_conserto.py` com os braços REL e D:
  - o motor do D recebe `cfg_acoplamento_corpo`;
  - entram a conferência da seção 3 e a medida dos conflitos.
- **A config:** `experiments/configs/v3_corpo_acoplamento/run.json`.
- **A faixa:** entra em `FAIXAS_RESERVADAS`, com a fonte, num commit antes da run.
- **A fumaça e o teste do orquestrador,** nas sementes dos testes.
- **O relato:** o `docs/RESULTADO_V3_CORPO_ACOPLAMENTO.md`, num PR próprio.

## 8. As decisões abertas (todas PROPOSTAS)

- **D-CA-9, o primário: os conflitos sobre todas as decisões, nas 12 células.**
  - **A recomendação:** esta. Ela mede o que o pet vive: quantas vezes precisa comer e descansar ao mesmo tempo.
  - **A alternativa:** a fração condicional, a fome urgente na energia baixa. A sonda mostrou que ela não se mexe com a D (0,759 contra
    0,761). Ela entra ao lado.
  - **O custo de errar:** a P pode passar com o pet ainda tendo fome em 3 de cada 4 decisões cansadas. A fração ao lado mostra isso.
- **D-CA-10, a faixa 100101…100505.**
  - **A recomendação:** aprovar e pedir a reserva ao coordenador. Ela foi conferida livre em 2026-11-18 nos 981 branches remotos, no
    `faixas.py`, nas configs, nos planos, nas tarefas, nos resultados e nos orquestradores.
  - **Por que não outra:**
    - a 23xxx e a 24xxx foram propostas na V2 (LP-1, LP-2);
    - a 83xxx e a 84xxx são da rodada 3 da luta;
    - abaixo de 10101, as bases colidem com as sementes pequenas.
  - **O custo:** é a primeira base de seis dígitos. A bancada não limita os dígitos, mas um leitor pode estranhar.
- **D-CA-11, os braços: o REL e o D, sem o CON.**
  - **A recomendação:** só esses dois. O conserto da VALUATION falhou e está desligado. Na sonda, o CON com a D piorou a fração.
  - **O custo de errar:** a combinação dos dois fica sem medida.
- **D-CA-12, as guardas pela classe com δ = 0,032.**
  - **A recomendação:** a mesma regra da VALUATION (D-VAL-20).
  - **O custo de errar:** uma piora pequena na exaustão, abaixo de δ, passa.
