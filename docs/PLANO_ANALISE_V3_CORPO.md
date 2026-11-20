# Plano de análise V3: a ablação do corpo (CORPO C1)

**Status: APROVADO pelo Matheus em 2026-11-18, com três ressalvas, todas DECIDIDAS** (CHECKPOINT C2): "Aprovar o C1 com essas três ressalvas". As
ressalvas foram o K = 40, o substrato social sem gate e a privação no comedouro fora dos critérios. Elas entram como as D-CO-5, D-CO-6 e
D-CO-10 (seção 9), e a forma de cada uma foi confirmada pelo Matheus ("Confirmo, siga"). **As D-CO-1 a D-CO-10 estão DECIDIDAS.** Nenhuma
vida desta run existe.

Escrito em 2026-11-18 por Claude Code (Opus 5.5, sessão lateral da CORPO_ACOPLAMENTO), no branch `v3-corpo-plano`, empilhado no #999. A
base é a `origin/main` em `8c6d17ae`. A tarefa é a [TAREFA_V3_CORPO.md](TAREFA_V3_CORPO.md), e o mapa que este plano segue é o
[MAPA_CORPO.md](MAPA_CORPO.md), APROVADO pelo Matheus no CHECKPOINT C1 ("Aprovado", 2026-11-18).

## 0. A trava e o que já foi visto

**Nenhuma vida roda antes de cinco coisas:**
1. este plano na `main`, com "APROVADO pelo Matheus" no cabeçalho. O orquestrador confere, e o `tools/pre_run.py` exige o plano igual ao da
   `origin/main`;
2. as D-CO-1 a D-CO-10 DECIDIDAS (feito em 2026-11-18);
3. a faixa da seção 4 em `FAIXAS_RESERVADAS`;
4. o código dos braços (seção 7) na `main`, cada um atrás de uma chave desligada, com o gabarito das vidas de hoje gravado antes;
5. nenhuma outra run de pesquisa rodando (V3-D8).

**O que já foi visto antes deste plano:**
- o mapa (C0) e as sondas da CORPO_ACOPLAMENTO, nas sementes dos testes;
- a run da opção D (`docs/PLANO_ANALISE_V3_CORPO_ACOPLAMENTO.md`, faixa 100101…100505), que passou (#1002). O resultado dela escolheu
  o conjunto de braços (seção 2), pela regra que o mapa escreveu antes (a seção 8 do mapa). Nenhum outro número deste plano sai dela;
  ela também diz que a privação sobe no comedouro com a D (+0,072). Por isso a ressalva do Matheus pôs a privação de cada lugar na
  guarda (D-CO-10), o que torna a regra mais estrita, e não mais frouxa. A consequência está na seção 5.

**O que este plano não afirma:** que uma opção é um conserto do jogo (a C3 e a C4 do programa vêm depois), nada sobre o jogo web, nada
sobre o social além do substrato. Nenhuma alegação de novidade.

## 1. A pergunta e a hipótese, escritas antes

**A pergunta:** alguma das opções do mapa reduz a tensão entre a fome e a energia sem piorar o bem-estar?

**A hipótese geral:** ao menos um braço sobe a taxa de fechamento por episódio de fome no `longe_fixo` sem subir a privação nem a exaustão.

**A previsão de cada braço**, a mesma forma: **braço − CTRL > 0 na taxa por episódio do `longe_fixo`**, com a privação e a exaustão fora do
"> 0". As predições de cada opção estão na seção 7 do mapa e não se afrouxam até passar.

**O que refuta a hipótese geral:** nenhum braço com "ganho" (seção 5). O resultado fica registrado como "tensão não localizada por estas
opções", e o programa para no CHECKPOINT C2.5.

## 2. Os braços

O controle **CTRL** é o REL da VALUATION, com o corpo de hoje (o `viver` do `run_v3_valuation_conserto.py`, como o REL da run da D). Cada
braço muda só a sua opção, atrás da sua chave.

**O conjunto saiu do resultado da run da D, pela leitura do plano dela.** A run rodou em 2026-11-18 e **passou**
(`docs/RESULTADO_V3_CORPO_ACOPLAMENTO.md`, no #1002). Os braços são, portanto, **CTRL, D, D + E e D + C5.** A regra, escrita no mapa antes
do resultado:

| a run da D | os braços | por quê (a seção 8 do mapa) |
|---|---|---|
| **passa** | **D**, **D + E**, **D + C5** | a D é a base; a E fecha o déficit, e a C5 separa o comportamento do corpo |
| **efeito trivial ou falha** | **E**, **C5**, **C1** | a D fica registrada como falha; as outras se medem contra o corpo de hoje |

A C2, a C3 e a C4 ficam fora, pela prioridade aprovada.

**Os tamanhos, PROPOSTOS, SEM FONTE (D-CO-3):**
- **D:** o `falta_fome` = 500 da `ConfigAcoplamentoCorpo`, o da run da D.
- **E:** não tem número: o alimento vai ao combustível pela quantidade comida, e a fome cai como hoje. O descarte com a fome em zero deixa
  de existir.
- **C5:** o reflexo deixa de pular o sorteio. Com a energia abaixo de `lambda_sono`, a unidade `dormir` ganha +S (1 024) no peso, somado ao
  `a + g_exp·ε`. O `lambda_sono` fica em S/4: o ajuste do limiar seria uma segunda mudança no mesmo braço (D-CO-4).
- **C1:** o consumo da comida madura tira C/10 (45 000) do cansaço, um décimo do que o −202 500 da ração tira da fome.

## 3. As células e as unidades

- **As células:** as 12 da C4, da A1 e da VALUATION: os 4 donos × o comedouro, o longe e o `longe_fixo`. O pedido diz "3 lugares × 2
  doadores"; a A1 rodou em 12 células (`docs/RESULTADO_V3_BASELINE_TRIVIAL.md:21`), e este plano segue a A1.
- **As unidades (a ressalva 1, D-CO-5):** 200 sementes independentes por célula: 200 bases, cada uma com k = 1 (a derivação
  `digibrain_prototipo` dá uma semente por base), como no plano da SOCIAL_PAR S. Não há agrupamento por base, e o t e o bootstrap ficam
  sobre as mesmas 200 unidades. Cada unidade dá o mesmo pet e o mesmo mundo a todos os braços.
- **Os dias:** 14, orçamento 16, os da VALUATION.

## 4. A run

| item | valor |
|---|---|
| bloco I: o pet sozinho | 4 braços (CTRL e os 3) × 12 células × 200 unidades = **9 600 vidas** |
| bloco II: o substrato social | 4 braços × 100 pares, no instrumento da SOCIAL_PAR A0 (só a condição VIVO), 5 dias (D-CO-6) |
| faixa | **104001…104400**, DECIDIDA (D-CO-7): as bases 104001…104200 (k = 1) para o bloco I, e as 104301…104400 (k = 1, prefixo `corpo_par`) para o bloco II |
| custo | o bloco I, cerca de 2 h com 4 processos (a VALUATION fez 4 800 vidas em 1 h); o bloco II, a medir na fumaça, e declarado no `meta.json` |
| processos | no máximo 4, uma run de pesquisa por vez |

A run roda **uma vez**. A fumaça usa as sementes dos testes.

## 5. As medidas e a regra de leitura, escritas antes

**O contraste:** braço − CTRL, pareado por unidade (base, semente), com o t (`orq.contraste_t`). As classes são as da A6.6
(`run_v2_longe_regular.classe`), com δ = 0,032, SEM FONTE, a da C4, da A1 e da VALUATION.

**O primário, o forrageio (F):** a taxa de fechamento por episódio de fome no `longe_fixo`, as 4 células, a medida da A1
(`EPISODIO`). O p é unilateral, para braço − CTRL > 0, com o **Holm** sobre os 3 braços em α = 0,025.

**O bem-estar (B), vinculante:** a privação e a exaustão (`PRIVACAO`, `EXAUSTAO`, as medidas da V2). A exaustão é lida no `longe_fixo` e
nas 12 células. **A privação é lida em cada lugar** (o comedouro, o longe e o `longe_fixo`) e nas 12 células: é a ressalva 3 (D-CO-10).

**O substrato social (S), vinculante (a ressalva 2, D-CO-6):** o bloco II, por par:
- **S1, os chutes de bola por dia**, somados dos dois pets: braço − CTRL não pode sair em "< 0";
- **S2, o tempo até o reencontro** (T\*, na janela de 96 decisões depois da perturbação, distância ≤ 6 células, a medida da SOCIAL_PAR A0):
  braço − CTRL não pode sair em "> 0" (mais lento).

Para S1 e S2, o δ é 10 % do nível do CTRL na própria run, SEM FONTE: as unidades não são as da δ = 0,032.

**A leitura de cada braço:**

| leitura | F | B |
|---|---|---|
| **ganho** | "> 0" e o Holm rejeita | nenhuma das seis guardas do bem-estar (a privação nos 3 lugares e nas 12; a exaustão no `longe_fixo` e nas 12) em "> 0", e S1 e S2 passam |
| **perda** ("virou a baseline") | "> 0" e o Holm rejeita | alguma guarda do bem-estar em "> 0", ou S1 ou S2 reprova |
| **nulo** | "≈ 0", "< 0", ou "> 0" sem o Holm | qualquer |
| **indeterminado** | "indeterminado" (o IC inclui o 0 e sai da faixa de δ) | qualquer |

**A consequência da ressalva 3, escrita antes:** na run da D (#1002), a privação do comedouro subiu +0,072 [+0,068; +0,076], acima de
δ. Se ela se repetir aqui, os três braços (todos com a D) saem em "perda" pela privação do comedouro, mesmo com o forrageio melhor. Pelo
programa, a perda vai ao Matheus: ele decide se o trade-off vale. A diferença entre os braços mostra se a E ou a C5 seguram essa
privação, como descritivo.

**O poder:** a referência mais próxima é o conserto da VALUATION, um braço pareado contra o mesmo REL, com 200 unidades. Ele deu
+0,106 [+0,094; +0,118] na taxa por episódio do `longe_fixo` (`docs/RESULTADO_V3_VALUATION_CONSERTO.md:34`), uma meia largura de 0,012,
bem abaixo de δ = 0,032. Um braço do corpo pode sair menos correlacionado com o CTRL que o conserto; o IC de cada braço vai no resultado,
como está.

**Ao lado, sem classe, com o IC95:**
- **os conflitos** (a fração das decisões com a energia baixa e a fome urgente, a medida da run da D) e a fome urgente na energia baixa;
- **o tempo livre:** a fração das decisões em brincar e explorar;
- os chutes de cada pet separados e a fração dos pares com algum chute;
- os descritivos da 5.3 da VALUATION: as refeições por dia, a `janela_vencida`, os reflexos por vida.

**O que a run não demonstra:**
- nada sobre o jogo web: as chaves ficam desligadas nele;
- nada sobre a calibração do cuidado (E1 e E2) nem sobre o I-PAD da LONGE_GEOMETRIA, que vem do sono;
- nada sobre outros tamanhos (seção 2), nem sobre combinações fora dos braços;
- nada sobre o social além do substrato: nenhum mecanismo social entra.

## 6. Os artefatos

Em `artifacts_v3_corpo/ablacao/`:
- `resultado.json`, `medidas.json` (o `medidas.json.gz` se passar de 100 MB) e `vidas.tar.gz`, determinístico;
- `meta.json`, com o commit, a árvore limpa, o comando exato, as versões do Python e do Node, o `plano_sha256`, a faixa, os braços e o sha256
  de cada artefato.

## 7. A implementação, depois da aprovação

**Um PR de código, antes de qualquer vida** (categoria implementacao):
- **as chaves dos braços** que ainda não existem, cada uma com o gabarito das vidas de hoje gravado antes, num commit próprio, e um teste
  "desligada sai byte a byte":
  - a E na `ConfigCorpo` nova da digestão (`digilab/corpo.py`, `web/app/motor/corpo.ts`), com a paridade;
  - a C5 numa config do M-ARB (`digilab/digibrain/arb.py`, `web/app/motor/digibrain/arb.ts`), com a paridade;
  - a C1, só se o conjunto da seção 2 a pedir;
- **o orquestrador** `experiments/run_v3_corpo.py`, em Python (D-CO-8), sobre o `run_v3_corpo_acoplamento.py` para o bloco I e o
  `run_v3_social_par_a0.py` para o bloco II;
- **a conferência de cada vida, com falha alta:** o corpo e o M-ARB de cada braço têm as chaves do braço; o replay do disco sai igual; as
  conferências da VALUATION;
- **a fumaça e o teste do orquestrador**, nas sementes dos testes.

O resultado vai num PR próprio, no `docs/RESULTADO_V3_CORPO.md`.

## 8. A ordem do programa

C1 (este plano) → CHECKPOINT C2 → o código da seção 7 → a run, uma vez → o `RESULTADO_V3_CORPO.md` → CHECKPOINT C2.5.

## 9. As decisões

O Matheus aprovou o plano com três ressalvas ("Aprovar o C1 com essas três ressalvas", 2026-11-18). As D-CO-1 a D-CO-4, a D-CO-8 e a
D-CO-9 ficam **DECIDIDAS** como recomendadas. A D-CO-5, a D-CO-6 e a D-CO-10 dão uma forma a cada ressalva, e a D-CO-7 muda com a
D-CO-5. O Matheus confirmou as quatro ("Confirmo, siga", 2026-11-18): **DECIDIDAS**.

- **D-CO-1 (DECIDIDA), os braços D, D + E e D + C5,** pela regra do mapa, com a D aprovada na run.
  - **O custo de errar:** o que a E e a C5 somam sobre a D só sai pela diferença entre os braços, descritiva.
- **D-CO-2 (DECIDIDA), o primário no `longe_fixo`,** onde a A1 achou a perda do forrageio.
- **D-CO-3 (DECIDIDA), os tamanhos da seção 2, SEM FONTE.**
- **D-CO-4 (DECIDIDA), a C5 sem mexer no `lambda_sono`:** uma mudança por braço.
- **D-CO-5 (DECIDIDA, a ressalva 1), 200 sementes independentes por célula, com k = 1 por base.**
  - **A forma:** as bases 104001…104200, como no plano da SOCIAL_PAR S. O custo é o mesmo: 9 600 vidas.
  - **O custo de errar:** os braços deixam de usar o mesmo desenho de unidades da A1, da VALUATION e da run da D. Cada contraste é dentro da
    run (o CTRL roda de novo), então isso não estraga o contraste. Só não dá para juntar unidades entre as runs.
- **D-CO-6 (DECIDIDA, a ressalva 2), o substrato social com gate:** S1, os chutes por dia, não pode sair em "< 0", e S2, o T\*, não pode
  sair em "> 0".
  - **A forma do δ:** 10 % do nível do CTRL na própria run, SEM FONTE.
  - **O custo de errar:** o piloto da SOCIAL_PAR B0 achou a bola quase sem chutes (o registro D-SP-33). Com o CTRL perto de 0, o S1 tem δ
    quase 0 e pode reprovar por ruído. A alternativa é exigir só que o braço não zere os chutes. O Matheus confirmou a forma de cima.
- **D-CO-7 (DECIDIDA), a faixa 104001…104400:** as bases 104001…104200 para o bloco I e as 104301…104400 para o bloco II.
  - **Por quê:** a 104xxx inteira foi conferida livre em 2026-11-18 nos códigos, nas configs, nos planos, nas tarefas, nos resultados e no
    registro de todos os branches remotos. A 103xxx não está livre: o branch `v3-social-par-s1` usa as bases 103001…103200 e 103301…103350
    (`docs/PLANO_ANALISE_V3_SOCIAL_PAR_S.md`).
  - **A reserva** é do coordenador.
- **D-CO-8 (DECIDIDA), o orquestrador em Python,** e não o harness em TS do pedido. O TS entra só na paridade das chaves.
- **D-CO-9 (DECIDIDA), o Holm sobre os 3 braços.**
- **D-CO-10 (DECIDIDA, a ressalva 3), a privação de cada lugar como guarda:** o comedouro, o longe e o `longe_fixo`, mais as 12 células.
  - **O custo de errar:** pela run da D, os três braços podem sair em "perda" só pelo comedouro (a seção 5). É o que a ressalva quer ver. Se
    acontecer, o trade-off vai ao Matheus, pela regra do programa.
