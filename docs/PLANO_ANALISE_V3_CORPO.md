# Plano de análise V3: a ablação do corpo (CORPO C1)

**Status: PROPOSTO.** Espera o "aprovado" do Matheus no CHECKPOINT C2, com as decisões D-CO-1 a D-CO-9 (seção 9). Nenhuma vida desta run
existe.

Escrito em 2026-11-18 por Claude Code (Opus 5.5, sessão lateral da CORPO_ACOPLAMENTO), no branch `v3-corpo-plano`, empilhado no #999. A
base é a `origin/main` em `8c6d17ae`. A tarefa é a [TAREFA_V3_CORPO.md](TAREFA_V3_CORPO.md), e o mapa que este plano segue é o
[MAPA_CORPO.md](MAPA_CORPO.md), APROVADO pelo Matheus no CHECKPOINT C1 ("Aprovado", 2026-11-18).

## 0. A trava e o que já foi visto

**Nenhuma vida roda antes de cinco coisas:**
1. este plano na `main`, com "APROVADO pelo Matheus" no cabeçalho. O orquestrador confere, e o `tools/pre_run.py` exige o plano igual ao da
   `origin/main`;
2. as D-CO-1 a D-CO-9 DECIDIDAS;
3. a faixa da seção 4 em `FAIXAS_RESERVADAS`;
4. o código dos braços (seção 7) na `main`, cada um atrás de uma chave desligada, com o gabarito das vidas de hoje gravado antes;
5. nenhuma outra run de pesquisa rodando (V3-D8).

**O que já foi visto antes deste plano:**
- o mapa (C0) e as sondas da CORPO_ACOPLAMENTO, nas sementes dos testes;
- a run da opção D (`docs/PLANO_ANALISE_V3_CORPO_ACOPLAMENTO.md`, faixa 100101…100505), que passou (#1002). O resultado dela escolheu
  o conjunto de braços (seção 2), pela regra que o mapa escreveu antes (a seção 8 do mapa). Nenhum outro número deste plano sai dela;
  ela também diz que a privação sobe no comedouro com a D (+0,072), o que este plano lê nas 12 células, como lá.

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
- **As unidades:** 200 por célula, pela derivação `digibrain_prototipo`, com K = 40 por base e 5 bases (D-CO-5). Cada unidade (base,
  semente) dá o mesmo pet e o mesmo mundo a todos os braços.
- **Os dias:** 14, orçamento 16, os da VALUATION.

## 4. A run

| item | valor |
|---|---|
| bloco I: o pet sozinho | 4 braços (CTRL e os 3) × 12 células × 200 unidades = **9 600 vidas** |
| bloco II: o substrato social | 4 braços × 100 pares, no instrumento da SOCIAL_PAR A0 (só a condição VIVO), 5 dias (D-CO-6) |
| faixa | **104101…104505**, PROPOSTA (D-CO-7): bases 104101, 104202, 104303, 104404 e 104505 para o bloco I; o bloco II usa as mesmas bases com o prefixo `corpo_par` |
| custo | o bloco I, cerca de 2 h com 4 processos (a VALUATION fez 4 800 vidas em 1 h); o bloco II, a medir na fumaça, e declarado no `meta.json` |
| processos | no máximo 4, uma run de pesquisa por vez |

A run roda **uma vez**. A fumaça usa as sementes dos testes.

## 5. As medidas e a regra de leitura, escritas antes

**O contraste:** braço − CTRL, pareado por unidade (base, semente), com o t (`orq.contraste_t`). As classes são as da A6.6
(`run_v2_longe_regular.classe`), com δ = 0,032, SEM FONTE, a da C4, da A1 e da VALUATION.

**O primário, o forrageio (F):** a taxa de fechamento por episódio de fome no `longe_fixo`, as 4 células, a medida da A1
(`EPISODIO`). O p é unilateral, para braço − CTRL > 0, com o **Holm** sobre os 3 braços em α = 0,025.

**O bem-estar (B), vinculante:** a privação e a exaustão (`PRIVACAO`, `EXAUSTAO`, as medidas da V2), no `longe_fixo` e nas 12 células.

**A leitura de cada braço:**

| leitura | F | B |
|---|---|---|
| **ganho** | "> 0" e o Holm rejeita | nenhuma das quatro (privação e exaustão, no `longe_fixo` e nas 12) em "> 0" |
| **perda** ("virou a baseline") | "> 0" e o Holm rejeita | alguma das quatro em "> 0" |
| **nulo** | "≈ 0", "< 0", ou "> 0" sem o Holm | qualquer |
| **indeterminado** | "indeterminado" (o IC inclui o 0 e sai da faixa de δ) | qualquer |

**O poder:** a referência mais próxima é o conserto da VALUATION, um braço pareado contra o mesmo REL, com 200 unidades. Ele deu
+0,106 [+0,094; +0,118] na taxa por episódio do `longe_fixo` (`docs/RESULTADO_V3_VALUATION_CONSERTO.md:34`), uma meia largura de 0,012,
bem abaixo de δ = 0,032. Um braço do corpo pode sair menos correlacionado com o CTRL que o conserto; o IC de cada braço vai no resultado,
como está.

**Ao lado, sem classe, com o IC95:**
- **os conflitos** (a fração das decisões com a energia baixa e a fome urgente, a medida da run da D) e a fome urgente na energia baixa;
- **o tempo livre:** a fração das decisões em brincar e explorar;
- **o bloco II, o substrato social:** os chutes de bola por dia de cada pet e o tempo até o reencontro (T\*, na janela de 96 decisões
  depois da perturbação, distância ≤ 6 células), as medidas da SOCIAL_PAR A0. O contraste é braço − CTRL por par. O pedido trata o
  substrato como critério; este plano o lê ao lado, porque o A0 não tem um gate para ele (D-CO-6);
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

## 9. As decisões (PROPOSTAS)

- **D-CO-1, o conjunto de braços pela run da D (seção 2): D, D + E e D + C5.**
  - **A recomendação:** este, a regra que o mapa aprovou, com a D aprovada na run.
  - **O custo de errar:** a D passou com folga (a P com o IC inteiro abaixo de −δ). O custo é outro: cada braço se mede contra o CTRL, e o
    que a E e a C5 somam sobre a D só sai pela diferença entre os braços, descritiva.
- **D-CO-2, o primário no `longe_fixo`, com o bem-estar vinculante.**
  - **A recomendação:** o `longe_fixo`, onde a A1 achou a perda do forrageio. Assim o resultado fica comparável à A1 e à VALUATION.
  - **O custo de errar:** um ganho só no comedouro passa como nulo.
- **D-CO-3, os tamanhos da seção 2, SEM FONTE.**
  - **A recomendação:** estes. Cada um é o mínimo que testa a predição, sem calibrar.
  - **O custo de errar:** um braço pode falhar pelo tamanho, e não pela opção.
- **D-CO-4, a C5 sem mexer no `lambda_sono`.**
  - **A recomendação:** uma mudança por braço.
  - **O custo de errar:** o ajuste do limiar, que o pedido junta à C5, fica sem medida.
- **D-CO-5, K = 40 por base com a derivação, e não 200 sementes independentes.**
  - **A recomendação:** a derivação. As sementes derivadas já são distintas, e a derivação deixa os braços comparáveis à A1, à VALUATION e à
    run da D.
  - **O custo de errar:** se houver efeito da base, o IC sai estreito demais. As 5 bases deixam ver isso ao lado.
- **D-CO-6, o substrato social no bloco II, lido ao lado e sem gate.**
  - **A recomendação:** ao lado, com o IC.
  - **O custo de errar:** um braço com ganho pode matar o substrato sem reprovar.
  - **A alternativa:** um gate de não piorar os chutes e o T\*, com δ próprio, SEM FONTE.
- **D-CO-7, a faixa 104101…104505.**
  - **A recomendação:** esta. Ela foi conferida livre em 2026-11-18 nos códigos, nas configs, nos planos, nas tarefas, nos resultados e no
    registro de todos os branches remotos. A 103xxx não está livre: o branch `v3-social-par-s1` usa as bases 103001…103200 e
    103301…103350 (`docs/PLANO_ANALISE_V3_SOCIAL_PAR_S.md`). A reserva é do coordenador.
  - **O custo de errar:** baixo.
- **D-CO-8, o orquestrador em Python, e não o harness em TS do pedido.**
  - **A recomendação:** o Python, pelo CLAUDE.md ("A pesquisa fica no Python"). O TS entra só na paridade das chaves.
  - **O custo de errar:** o motor TS não é exercitado na run. A paridade cobre a diferença.
- **D-CO-9, o Holm sobre os 3 braços.**
  - **A recomendação:** o Holm, como na VALUATION.
  - **O custo de errar:** com 3 braços, um efeito pequeno perde o poder.
