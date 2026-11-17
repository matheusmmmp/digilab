# Plano de análise V3: a ablação do Valuation (VALUATION V1)

**Status: APROVADO pelo Matheus em 2026-11-16,** com as D-VAL-7 a D-VAL-10 DECIDIDAS pela recomendação: "Aprovado, siga a V2", nesta
sessão (o CHECKPOINT V2). Escrito em 2026-11-16 (Claude Code, Opus 5.5, branch `v3-valuation`), na Fase V1 do pedido
([TAREFA_V3_VALUATION.md](TAREFA_V3_VALUATION.md)). O Matheus aprovou o CHECKPOINT V1 nesta sessão ("Aprovado, siga a V1"), com as
D-VAL-1 a D-VAL-6 pela recomendação. O plano para no **CHECKPOINT V2**.

## 0. A trava e o que já foi visto

**Nenhuma vida roda antes de quatro coisas:**
1. este plano commitado, com "APROVADO pelo Matheus" no cabeçalho (o `run_v3_valuation.py` confere e recusa sem);
2. as decisões D-VAL-7 a D-VAL-10 (seção 10) DECIDIDAS;
3. a faixa da seção 4 em `FAIXAS_RESERVADAS` (o orquestrador confere);
4. a ordem da D-VAL-6: a `main` fixa, com o PR #943 (a A1) mergeado e os imports do `digilab/policies/lobos.py` estáveis diante da
   LIMPEZA. O commit da run vai no `meta.json`.

O código da V2 (o orquestrador, as duas chaves de ablação, os gabaritos e os testes) vem num PR próprio, depois deste plano e antes de
qualquer vida.

**O que já foi visto antes deste plano:** o [MAPA_VALUATION.md](MAPA_VALUATION.md), escrito sobre os artefatos da A1 (o `medidas.json`
`cdaa5170…`, branch `v3-evidencia-a1`) e da C4. Os descritivos de lá orientaram a escolha das hipóteses e da ordem. Nenhum número deste
plano foi ajustado por uma vida nova: esta run não tem calibração. Os valores das ablações saem do código e do histórico das rodadas
(seção 3), não de uma vida.

**O que este plano não afirma:**
- que alguma hipótese é a causa;
- que uma ablação é um conserto. O conserto é a V3, atrás de chave, com a guarda do bem-estar;
- nada sobre o jogo web.

Nenhuma alegação de novidade.

## 1. A pergunta, as hipóteses e as previsões, escritas antes

**A pergunta (D-VAL-1):** qual elo do Valuation faz o REL fechar menos episódios de fome dentro da janela? A V0 mostrou que ele come
mais ração por dia que a TRIV (MAPA, seção 1).

**O desenho:** uma ablação por hipótese, cada uma contra o REL completo, na mesma unidade (base, semente).

**A previsão de cada hipótese** é a mesma forma: **se H causa a perda, a ablação sobe a taxa por episódio no `longe_fixo` (braço − REL >
0)**. A previsão não se afrouxa até passar. As previsões de tamanho do MAPA (seção 3) ficam como estão:
- B e F: nulo;
- C: o sinal contrário, pela C4;
- R e E: as mais fortes.

Elas não mudam a regra da seção 7.

## 2. O cenário (o que não muda)

- **A vida do REL** é a de `run_v2_memoria_autobio._vida` (a da C4 e da A1), sem mudança:
  - o `CONFIG_MUNDO_MVP` e o corpo do v11;
  - o pet sozinho;
  - 14 dias, orçamento de 16 por dia, morte desligada;
  - o `MotorGravaCorpo`;
  - o replay do disco e as conferências da C4.
- **O braço base** é o REL, `SUBCHAVES_C4["REL"]` (o M3 com o `cheiro_inato`, a `intencao_cheiro`, a `memoria_autobio` e o
  `controle_mem = "rel"`).
- **As células:** as 4 do `longe_fixo`, os donos atencioso, relapso, aleatório e incoerente. O comedouro e o longe sorteado ficam fora: o
  pedido mede o `longe_fixo`, e cada lugar a mais custa 8 braços.
- **O motor, o corpo, o mundo, o `engine.py` e a métrica da A1** não mudam. A TRIV não roda aqui: o contraste com ela é a V4.

## 3. Os braços

Oito braços: o REL e uma ablação por hipótese. Cada ablação muda **uma** coisa do REL.

| braço | hipótese | o que muda | de onde vem | a conferência de que a ablação fez efeito (falha alta) |
|---|---|---|---|---|
| **REL** | — (o controle) | nada | `SUBCHAVES_C4["REL"]` | as da C4 |
| **A** | A, a frequência de decisão | a `ConfigDecisaoNaComida(ligada=True)` no motor | já existe (`config.py:3217`; `mundo.py:2654`), ligada nos ovos novos do jogo (D-VAL-4) | ao menos uma decisão fora da cadência de 15 ticks numa vida com ração posta |
| **B** | B, o `g_exp` | `epsilon = 0` | `ConfigDigibrainInatos` (`config.py:2953`), um número | `pesos == ativações` em toda decisão |
| **C** | C, a memória de lugar | `controle_mem = "sem"` | o braço SEM da C4 (`config.py:2794`; `mem.py:363`) | nenhuma unidade `explorar/ponto` na vida |
| **E** | E, o limiar da fome | `W0[comer]`: o viés de −17S/16 para −S/2 (−1 088 → −512); o `u_fome` fica 3S | `ConfigDigibrainInatos.w0`, um número (D-VAL-8) | o W0 do comer no registro do cérebro |
| **F** | F, o V e o E | a chave nova `ablacao_ve_z`: o V e o E do z entram como 0 em todo o M-IMPULSO e no P2 | chave de ablação, desligada (D-VAL-3) | z[V] = z[E] = 0 em toda decisão |
| **G** | G, a diluição no sorteio | a chave nova `ablacao_maior_peso`: o M-ARB escolhe a unidade de maior peso (o caminho de `arb.py:98-99`, o primeiro no empate), sem chamar a rng | chave de ablação, desligada (D-VAL-3) | nenhuma `rng.random()` do cérebro na vida (`sorteios` = 0) |
| **R** | R, o reflexo do sono | `lambda_sono = 0`: o reflexo nunca dispara, e o dormir disputa no sorteio como as outras unidades | `ConfigDigibrainInatos` (`config.py:2954`), um número (D-VAL-2, D-VAL-7) | `reflexos` = 0 em toda vida |

**Os valores, escritos antes e sem calibração:**
- **E, −S/2.** Com ele, o `comer/cheiro` passa de 0 a partir da fome ≈ 0,83, em vez de 0,489, a conta da seção 2.6 do MAPA com o viés novo.
  A ablação é forte de propósito: se nem ela sobe o fechamento, E cai.
- **R, 0.** Tira o reflexo inteiro. É o teste mais limpo de "o reflexo ocupa a janela".

Um nulo vale só para esse valor (seção 9).

**O segundo braço de R aprovado na D-VAL-2, a `intencao_suspensa`, não pode ser montado.** O `ConfigDigibrain` recusa a `memoria_autobio`
com a `intencao_suspensa` (`config.py:2845`: "nao se combina", sem teste da combinação). Ligá-lo seria uma combinação nova, sem teste. A
D-VAL-7 leva isso ao Matheus. A parte "a intenção perdida" vira descritivo: a contagem das intenções de comer que o reflexo troca, no
braço REL (seção 5.3).

**As duas chaves novas** (F e G) entram no código da V2, desligadas, com o teste "desligada, a vida de hoje byte a byte" contra um gabarito
gravado num commit anterior. Elas não são mecanismo: só zeram duas entradas ou usam um caminho de escolha que o M-ARB já tem. Ficam fora
do jogo web (D-VAL-5).

**A rng:** no braço G, a rng de política deixa de ser lida. Ela é só do cérebro (`arb.py`, "a única do cérebro"), e a rng do ambiente não
muda, pela regra das rngs separadas. Nos outros braços, a rng de política é lida como no REL.

## 4. As sementes e o N

| etapa | faixa | bases | K por base | unidades | células | braços | vidas |
|---|---|---|---|---|---|---|---|
| a run da ablação (uma vez) | **99101…99505** (PROPOSTA, D-VAL-9) | 99101, 99202, 99303, 99404, 99505 | 40 | **N = 200** | as 4 do `longe_fixo` | 8 | **6 400** |

- **A derivação** é a da C4 e da A1: semente `derivar_semente("digibrain_prototipo", base, k)`, k = 0…39.
- **Todo braço vive as mesmas 200 unidades nas mesmas 4 células.** A diferença é pareada por unidade.
- **A faixa** foi conferida livre em 2026-11-16 no `faixas.py` da `main` e nos branches remotos (seção 10, D-VAL-9).
- **O N:** o mesmo da A1. Com o dp das diferenças da C4 (a margem efetiva de 0,018 para REL − SEM com 200 unidades), o N = 200 dá folga
  para δ = 0,032. Um braço com dp maior reporta a margem efetiva dele (seção 6.2).
- **O custo:** a vida do REL custou 3,7 s de CPU na A1 (`custo.vida_cpu`). Com 6 400 vidas, são cerca de 6,6 h de CPU, cerca de 1,7 h com 4
  processos. A run só começa com a máquina livre: uma run de pesquisa por vez, no máximo 4 processos.

## 5. As medidas

### 5.1 O primário

**A taxa de fechamento por episódio de fome** (`episodios_fome.taxa`, `metrics.episodios_de_fome`; o `EPISODIO` do `run_v2_longe_regular`).
É a mesma medida da A1 e da C4, sem mudança. A unidade é (base, semente), com a média das 4 células do `longe_fixo`. O contraste de cada
hipótese é braço − REL na mesma unidade.

### 5.2 A guarda do bem-estar (sem gate na V2; vinculante na V3)

As medidas são a privação (`privacao`, a fração das decisões com min(fome, higiene, energia) < 0,15) e a exaustão (`exaustao`, a fração das
decisões dos dias 8–14 com energia < 0,25). Para cada braço, braço − REL por unidade, com o IC95 pelo t.

Um braço "piora o bem-estar" se uma das duas sair na classe "> 0", com a mesma regra de classes e a mesma margem 0,032 da seção 7.
- Isso **não muda** a classe da hipótese: a V2 diagnostica.
- Uma hipótese confirmada cuja ablação piora o bem-estar vai à V3 marcada assim. O conserto da V3 tem de fechar mais sem essa piora.

### 5.3 Os descritivos (sem gate)

Por braço, a média por unidade e braço − REL, com o IC95 ao lado e sem classe:
- as refeições de ração por dia (`cadeia.refeicoes_por_dia`) e o consumo de todas as comidas por dia, as frutas incluídas;
- a fração dos episódios que acabam em "janela_vencida";
- a fração das decisões do episódio em `dormir` e em `comer`;
- os reflexos por vida e a latência média do fechamento;
- **para a R:** no braço REL, as intenções de comer (`comer/comida` e a busca `comer/cheiro`) que acabaram em "trocou" numa decisão de
  reflexo, por vida;
- **para a G:** no braço REL, a fração das decisões do episódio em que uma unidade do comer tinha o maior peso e o sorteio escolheu outra
  (dos `pesos` gravados no motivo, `adapt.py:373`);
- as sondas "quem decidiu" (`influencia`).

## 6. O teste

### 6.1 O contraste

- **O IC95** pelo t sobre as 200 unidades, com o p unilateral (H: braço − REL > 0), pelo `orq.contraste_t` da C4 (o t pareado, A4.4.6).
- **A família** são os 7 contrastes, de A a R. O Holm vai sobre os 7 p unilaterais, com α = 0,025 unilateral na família, como a A9.4 da
  C4 (D-VAL-10).
- **Ao lado, rotulados, sem mudar a classe:** o IC95 percentil do bootstrap (10 000 reamostragens, semente 4242; anticonservador com 5
  bases, A4.4) e o g1.

### 6.2 A margem

δ = 0,032, a da C4 e da A1 (AD9-5), SEM FONTE: o "efeito trivial". A margem efetiva de cada contraste (o menor efeito com poder 0,8 pelo dp
observado) vai ao lado. Quando ela passa de δ, a leitura de "≈ 0" daquele braço fica enfraquecida e o resultado diz isso.

## 7. A regra de leitura, escrita antes

**A classe de cada contraste** é a da A6.6 (`run_v2_longe_regular.classe`), na ordem:
1. **"≈ 0"** se o IC95 cabe em (−δ, +δ), com o sinal se ele também exclui o 0;
2. **"> 0"** se o limite inferior passa de 0;
3. **"< 0"** se o limite superior fica abaixo de 0;
4. **"indeterminado"** nos outros casos.

**A leitura de cada hipótese:**

| leitura | condição |
|---|---|
| **confirmada** | a classe é "> 0" **e** o Holm a rejeita |
| **efeito trivial** | a classe é "≈ 0" com o sinal + e o Holm a rejeita: o efeito existe, mas fica abaixo de δ e não explica a perda |
| **refutada** | a classe é "≈ 0" (sem o sinal +) ou "< 0" |
| **indeterminada** | qualquer outro caso |

**O CHECKPOINT V2.5:**
- **Nenhuma confirmada:** a frente para com **"causa não localizada"**, com o resultado registrado como está, e a V3 não começa.
- **Uma ou mais confirmadas:**
  - todas vão à V3 como candidatas, com a guarda do bem-estar da seção 5.2;
  - a fração do gap da A1 (0,083) que cada uma cobre vai ao lado, como descritivo;
  - qual conserto entra é decisão do Matheus. A run não testa interações entre as ablações (seção 9).

**Falha alta, que para a run sem leitura:**
- um replay que diverge;
- uma conferência da C4 que falha;
- uma conferência da seção 3 que falha (a ablação não fez o que diz);
- uma faixa fora de `FAIXAS_RESERVADAS`;
- o plano sem "APROVADO".

## 8. Os artefatos

Em `artifacts_v3_valuation/ablacao/`:
- `resultado.json`: os 7 contrastes, as leituras, a guarda, os descritivos e o `nao_demonstra`;
- `medidas.json` (ou `.gz` acima de 100 MB);
- `vidas.tar.gz`, determinístico;
- `meta.json`, com:
  - o comando, o commit e a árvore limpa;
  - o `plano_sha256` e o sha256 da config;
  - a faixa, as unidades e os braços com as subchaves e os inatos de cada um;
  - as versões do Python e do Node;
  - a duração e o sha256 de cada artefato.

O comando, que roda uma vez:

```bash
python experiments/run_v3_valuation.py --config experiments/configs/v3_valuation/ablacao.json --processos 4
```

## 9. O que esta run não demonstra

- **As interações:** cada ablação muda uma coisa só, e duas hipóteses confirmadas podem não somar.
- **Um nulo vale só para o valor testado.** A E e a R têm um valor cada (seção 3).
- **Nada fora das 4 células do `longe_fixo`,** do mundo do MVP e dos 14 dias.
- **Nada sobre o jogo web.** As vidas são do Python, e os pets do jogo (v38, v39) já ligam a `decisaoNaComida` e as chaves da EQ-7.
- **Que uma ablação confirmada é o conserto.** Ela localiza o elo, e a V3 é que conserta, atrás de chave e sem piorar o bem-estar.
- **A D (P1 e P2)** fica com a A2.

## 10. As decisões abertas para o CHECKPOINT V2

Cada uma tem a recomendação e o custo de errar.

- **D-VAL-7, o braço `intencao_suspensa` da R.**
  - **A recomendação:** não montar. Fica só o `lambda_sono = 0`, com o descritivo das intenções trocadas pelo reflexo (5.3).
  - **O porquê:** ligar a `intencao_suspensa` com a `memoria_autobio` é uma combinação que o código recusa hoje, e liberá-la é mexer numa
    trava sem teste.
  - **O custo de errar:** se a causa for só a intenção perdida, o `lambda_sono = 0` também a tira, mas mistura isso com o sono. A separação
    fica para a V3, se a R se confirmar.
- **D-VAL-8, o valor da ablação da E.**
  - **A recomendação:** o viés −S/2.
  - **O porquê:** é uma ablação forte. O −S da rodada 2 é a alternativa fraca: o `comer/cheiro` passaria de 0 só a partir da fome ≈ 0,5, o
    limiar do episódio.
  - **O custo de errar:** com um valor fraco, um nulo não refuta E. Com o forte, uma confirmação pode vir de comer cedo demais, e a guarda
    do bem-estar mostra isso.
- **D-VAL-9, a faixa 99101…99505.**
  - **A recomendação:** reservar esta faixa, conferida livre.
  - **Um achado ao lado, que não é desta frente:** a `main` reserva a 96101…96505 à LONGE_GEOMETRIA (`faixas.py`, D-EQ2-11), e a
    calibração da A1 (branch `v3-evidencia-a1`) usou a mesma faixa. O pedido desta frente ainda dava a 93101…93505 à LONGE_GEOMETRIA. Fica
    registrado para o coordenador, e este plano não usa nenhuma das duas.
  - **O custo de errar:** uma colisão de faixa queima a run.
- **D-VAL-10, a família do Holm.**
  - **A recomendação:** os 7 contrastes numa família, com α = 0,025 unilateral, como a C4.
  - **O custo de errar:** sem o Holm, 7 testes dão uma chance de falso "confirmada" bem acima de 2,5 %. Com ele, um efeito pequeno pode sair
    "indeterminado", e a margem efetiva mostra quando isso acontece.

## Adendo 1: o braço A fora da run (D-VAL-11)

**Status do adendo 1: APROVADO pelo Matheus em 2026-11-16** ("Aprovo o adendo 1", nesta sessão; D-VAL-11 DECIDIDA). Escrito em 2026-11-16 (Claude Code, Opus 5.5, branch `v3-valuation-v2`), na montagem do código da V2,
antes de qualquer vida. O orquestrador recusa a run de verdade até esta linha dizer "APROVADO pelo Matheus".

**A1.1 O que se achou.** O braço A liga a `ConfigDecisaoNaComida`: o pet decide no passo seguinte à queda da ração, fora da grade de 15
ticks. As medidas da A1, que o plano não muda, pressupõem a grade:
- o `orq.medidas` recusa a vida no primeiro consumo fora de um múltiplo de 15 ("consumo fora do tick de uma decisao") e exige
  `decisões × 15 = os ticks da vida`;
- o `metrics.episodios_de_fome` conta a janela W(d0) em decisões k = 0, 1, …, cada uma de 15 ticks. Com decisões extras, a mesma W cobre menos
  tempo, e o contraste com o REL deixa de comparar a mesma coisa.

Medir o braço A pede mudar a métrica da A1, o que o pedido proíbe ("não mudar a métrica da A1").

**A1.2 O que muda.**
- **Os braços:** o braço A sai da run (`run_v3_valuation.FORA`; pedi-lo falha alto). A run passa a ter **7 braços**: o REL, B, C, E, F, G
  e R.
- **As vidas:** **5 600** (7 × 4 células × 200 unidades), cerca de 5,8 h de CPU.
- **A família do Holm:** **6** contrastes, com o mesmo α = 0,025 unilateral.
- **A hipótese A** fica sem ablação. O `nao_demonstra` do resultado o diz, e o MAPA (seção 3) já registrava que a TRIV decide na mesma
  cadência de 15 ticks.

**A1.3 Dois acertos de leitura, sem mudança de número:**
- **O consumo de todas as comidas (5.3)** é o mesmo número que as refeições de ração. O T-CENARIO-1 confere em toda vida que toda comida
  do mundo é ração do dono, e por isso o descritivo sai uma vez só.
- **A conferência do braço F (seção 3)** não pode ler o z decisão a decisão, porque o motivo do cérebro não guarda o z. A vida confere a
  chave ligada nos dois módulos e o cérebro do braço, e o `tests/test_valuation.py` confere a conta (o z com o V e o E em 0, o resto igual).

**A1.4 A decisão (D-VAL-11).**
- **A recomendação:** aprovar o braço A fora.
- **A alternativa:** um plano próprio para a cadência, com uma medida em ticks no lugar da janela em decisões. Isso seria outra métrica,
  fora do pedido.
- **O custo de errar:** perde-se a única ablação da A. O MAPA já previa que a cadência sozinha não separa o REL da TRIV.
