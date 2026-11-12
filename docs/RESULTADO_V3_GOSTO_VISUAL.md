# RESULTADO V3 — GOSTO_VISUAL, GV3: a run descritiva genoma × dono com a sonda das duas TVs (2026-11-12, Claude Code, Opus 5.5)

**O plano:** [PLANO_ANALISE_V3_GOSTO_VISUAL.md](PLANO_ANALISE_V3_GOSTO_VISUAL.md), APROVADO pelo Matheus em 2026-11-11 ("e segue o
experimento com as suas recomendações."), com o registro da run na seção 11, empurrado antes da primeira vida. O código da P1e entrou na
`main` no merge `846dadd9` antes da primeira vida (D-GV-P1e-12).

**O achado registrado antes da leitura:** o `docs/registro/2026-11.md`, seção "o enjoo da imagem no cérebro do Python, achado antes de
ler a GV3", D-GV-ENJOO-PY-1 a 3 (commit `f8738a5a`, empurrado antes de qualquer leitura dos artefatos). A seção 4 deste documento lê o
resultado com ele.

**Este resultado é descritivo** (o plano não tem gate). Todos os números são PROPOSTOS e SEM FONTE. O documento não afirma que o pet
"gosta", sente prazer ou tem gosto estético: escolha, tempo relativo e agrado são nomes de medida. **Nenhuma alegação de novidade.**
Nenhuma referência é citada aqui: as do plano ainda não estão nas tabelas verificadas (a GV-12 não foi feita).

## 0. A run e os artefatos

- **O piloto** (bases 89101 e 89202, K = 2, 24 vidas): `artifacts_v3_gosto_visual/piloto/`. 4 processos, 2026-11-11 das 23:34 às 23:37
  (126,8 s, `meta.json`, `duracao_s`). A conferência da seção 6 (GVP-7), em `analise.json`, `conferencia`: 504 réplicas, fração com uma
  olhada 0,942, mínimo 0,25, **`a_run_pode_rodar: true`**. Nada foi ajustado olhando o piloto.
- **A run** (bases 89303, 89404 e 89505, K = 12: 36 unidades, 216 vidas de 14 dias), **uma vez**: `artifacts_v3_gosto_visual/gosto_visual/`.
  - No commit `48736040`, árvore limpa (`meta.json`: `git_head`, `git_limpo: true`), 4 processos, de 2026-11-11T23:37:47 a 23:59:01
    (1273,7 s de parede, `meta.json`, `duracao_s`). Nenhuma outra run de pesquisa rodava.
  - **O custo** (`custo.json`): 23,5 s por vida em média, 60,8 s no máximo, 1271,4 s de parede nas vidas. A estimativa do plano era cerca
    de 16 s (sem artefato).
  - **A conferência por réplica** (`analise.json`, `conferencia`): 4536 réplicas, fração com uma olhada 0,944. Nenhum dia ficou sem sonda
    (`contas_resultado.json`, `dias_sem_sonda`: 0) e nenhum pet ficou sem sonda válida (`analise.json`, `sem_sonda_valida` 0 nas seis
    células).
- **Os arquivos:** `meta.json`, `medidas.json`, `analise.json`, `custo.json` e `vidas.tar.gz` (as 216 vidas e as 216 sondas) no git; as
  vidas soltas fora (`.gitignore`). Os sha256 do `medidas.json`, do `analise.json` e do `custo.json` batem com os do `meta.json`
  (`artefatos_sha256`).
- **A origem dos números:** todo número sai do `analise.json` da run, salvo os marcados `contas_resultado.json`. Esse arquivo sai do
  `contas_resultado.py` da mesma pasta, que só lê o `medidas.json`. Ele também refaz a análise a partir do `medidas.json`: a familiarização,
  a principal e a "só estáveis" saem iguais às do `analise.json` (`analise_refeita_igual`).

## 1. A familiarização (2.2)

`analise.json`, `familiarizacao`: **168 das 216 vidas passaram no critério** (a média dos dias 5 e 6 a no máximo 0,05 da dos dias 3 e 4),
então `nao_estabilizou: false`. Por célula, as estáveis em 36: próprio × nenhum 29, × calmo 26, × agitado 32; vazio × nenhum 24, × calmo 30,
× agitado 27. A fração média das decisões acordadas olhando a TV da vida nos 14 dias fica entre 0,043 (próprio × nenhum) e 0,061 (vazio ×
calmo) (`fracao_media_olhando`).

## 2. A tabela (7.1), análise principal (todas as 216 vidas, 36 pets por célula)

`analise.json`, `principal.celulas`: a média das médias dos pets. Nenhuma medida ficou sem variância em nenhuma célula (5.6).

| genoma × dono | escolha | tempo relativo | tempo total |
|---|---|---|---|
| próprio × nenhum | 0,497 | 0,502 | 0,205 |
| próprio × calmo | 0,511 | 0,507 | 0,211 |
| próprio × agitado | 0,518 | 0,509 | 0,209 |
| vazio × nenhum | 0,513 | 0,520 | 0,219 |
| vazio × calmo | 0,483 | 0,494 | 0,253 |
| vazio × agitado | 0,531 | 0,526 | 0,248 |

### 2.1 A parte do genoma (5.2): Spearman(Δ_I, medida) nos genomas próprios, IC95 do bootstrap por unidade (2000, 0 indefinidas)

O Δ_I dos 108 pets de genoma próprio vai de −514 a 459, com 48 positivos; no vazio, Δ_I = 0 em todos (`contas_resultado.json`).

| dono | escolha | tempo relativo |
|---|---|---|
| nenhum | 0,175 [−0,168; 0,522] | 0,244 [−0,085; 0,555] |
| calmo | 0,103 [−0,262; 0,428] | 0,137 [−0,195; 0,436] |
| agitado | 0,117 [−0,228; 0,448] | 0,231 [−0,098; 0,530] |

**A parte do genoma não aparece com 36 unidades** em nenhum dono e em nenhuma das duas medidas: todo IC95 contém 0.

### 2.2 A parte do dono (5.3): diferenças dentro da unidade, média sobre 36 unidades, IC95

| genoma | diferença | escolha | tempo relativo |
|---|---|---|---|
| próprio | calmo − agitado | −0,007 [−0,044; 0,027] | −0,002 [−0,026; 0,023] |
| próprio | calmo − nenhum | 0,015 [−0,033; 0,067] | 0,005 [−0,028; 0,039] |
| próprio | agitado − nenhum | 0,022 [−0,027; 0,066] | 0,008 [−0,031; 0,044] |
| vazio | calmo − agitado | −0,048 [−0,097; 0,004] | −0,032 [−0,066; 0,006] |
| vazio | calmo − nenhum | −0,029 [−0,080; 0,019] | −0,026 [−0,062; 0,008] |
| vazio | agitado − nenhum | 0,018 [−0,018; 0,058] | 0,006 [−0,021; 0,034] |

**A parte do dono não aparece com 36 unidades** em nenhum genoma: todo IC95 contém 0. No vazio, os pontos de `calmo − agitado` são
negativos e os IC95 passam de 0 por pouco (0,004 e 0,006); pela regra da 7.2, isso é "não aparece", e não um efeito do contrário.

### 2.3 A interação (5.4)

(calmo − agitado no próprio) − (calmo − agitado no vazio): escolha 0,041 [−0,025; 0,106], tempo relativo 0,029 [−0,011; 0,070]
(`principal.interacao`). **Não aparece com 36 unidades.**

### 2.4 A divergência (5.5) e a repetibilidade (5.7)

- **A divergência** (`principal.divergencia`): em 45 dos 216 pets a escolha e o tempo relativo ficam de lados opostos de 0,5; o Spearman
  entre as duas medidas por pet é 0,750.
- **A repetibilidade** (`principal.repetibilidade`, o ICC(1) das médias por dia, só o ponto): próprio 0,0 na escolha e 0,0 no tempo
  relativo; vazio 0,044 na escolha e 0,031 no tempo relativo. O 0,0 é o ponto preso em 0 pelo `metrics.icc1_estatisticas` quando a
  variância entre pets estimada sai negativa. Nas duas leituras, quase nada da variação entre os dias é do pet.

### 2.5 O efeito colateral

O tempo total na sonda (a fração dos 240 ticks olhando alguma das duas TVs) fica entre 0,205 e 0,211 no próprio e entre 0,219 e 0,253 no
vazio (a tabela da seção 2). A fração olhando a TV da vida está na seção 1. Nenhum IC95 foi pedido para isso no plano; é descritivo.

### 2.6 A parte da exposição no agrado do cérebro (4.2; descritivo)

Δ_agora − Δ_I, a média por célula sobre os pets (`contas_resultado.json`, `exposicao_delta_agora_menos_delta_inato`):

| genoma | nenhum | calmo | agitado |
|---|---|---|---|
| próprio | −8,8 | 9,6 | −37,4 |
| vazio | −4,1 | 67,2 | −85,5 |

O sinal acompanha o dono no vazio: o `calmo` desloca o agrado do cérebro para o lado de A, e o `agitado` para o lado de B. Esse
deslocamento está no cérebro, e o comportamento na sonda não o acompanha (a seção 2.2).

## 3. A análise "só estáveis" (168 vidas)

`analise.json`, `so_estaveis`: a mesma leitura. Todo IC95 da parte do genoma, da parte do dono e da interação contém 0.
- **A parte do genoma:** o Spearman com o tempo relativo é 0,267 [−0,105; 0,598] (nenhum), 0,215 [−0,194; 0,558] (calmo) e 0,232
  [−0,121; 0,545] (agitado).
- **A parte do dono:** `calmo − agitado` no tempo relativo é 0,004 [−0,027; 0,037] no próprio e −0,014 [−0,064; 0,037] no vazio.
- **A divergência:** 34 de 168 pets de lados opostos; o Spearman é 0,768.
- **As células:** a escolha fica entre 0,485 e 0,530, e o tempo relativo entre 0,496 e 0,515.

## 4. A leitura (com as D-GV-ENJOO-PY-1 e 2)

- **O que a run mostra:** nem a parte do genoma, nem a parte do dono, nem a interação aparecem com 36 unidades, nas duas medidas e nas
  duas análises. Isto é o resultado negativo, registrado como está (seção 8 do plano). Ele não diz que o genoma ou o dono "não têm
  efeito": diz que, neste cérebro e nesta sonda, com 36 unidades, o efeito não se separa do ruído.
- **E1 (a escolha perto de 0,5):** confere. As seis células ficam entre 0,483 e 0,531. A primeira olhada não lê o agrado (D-GV-P1e-4).
- **E2 (o tempo relativo acompanha Δ_I):** não se vê. Os pontos do Spearman são positivos (0,137 a 0,244), mas todo IC95 contém 0.
- **E3 (a parte do dono menor que a do genoma):** não se pode conferir, porque nenhuma das duas aparece.
- **D-GV-ENJOO-PY-1 (o pet não chega a enjoar e olha em rajadas curtas):**
  - O que a sonda mede é o que o pet faz em poucas decisões seguidas. Não há habituação ao conteúdo que tire o pet de uma TV de agrado
    baixo ou o segure numa de agrado alto por mais tempo. O plano (E2, GVP-6) contava com isso.
  - As medidas do tempo relativo ficam, por construção do cérebro de hoje, sem o mecanismo que a pergunta queria ler. A repetibilidade
    quase nula entre os dias (2.4) e o tempo total perto de 0,2 a 0,25 são coerentes com rajadas curtas, mas a run não mede as rajadas
    diretamente.
- **D-GV-ENJOO-PY-2 (os três efeitos da sonda que não vêm do gosto):**
  - Os três efeitos são estes: a novidade só conta a subida, então passar de A para B dá novidade e de B para A nunca; começar a olhar B
    dá susto sempre; olhar B dá estresse.
  - Os três vêm só do volume e do movimento dos dois perfis (A = C/5, B = 4C/5), e não do agrado. Valem para todo pet, inclusive o vazio,
    onde Δ_I = 0.
  - **Toda diferença entre A e B nesta run tem de ser lida com eles.** O desvio de 0,5 numa célula (por exemplo o tempo relativo 0,526
    no vazio × agitado, ou 0,494 no vazio × calmo) pode vir desses efeitos, do sorteio ou da exposição. A run não os separa, e este
    documento não atribui nenhuma dessas diferenças ao gosto.
  - **Também não se lê "o pet evita B por gosto"** nem "prefere A por gosto". A run não mede o sentido de cada um dos três efeitos sobre
    o olhar (a novidade pode puxar para B, e o susto e o estresse, para longe dele), e os pontos das células ficam perto de 0,5 nos dois
    lados.
  - **A diferença do tempo total entre o vazio (0,219 a 0,253) e o próprio (0,205 a 0,211)** é descritiva, sem IC95. Ela pode vir do pico
    da visão do genoma próprio (que muda o agrado inato das duas TVs, não só o contraste entre elas) e dos efeitos de volume e de
    movimento. Fica sem leitura causal.
- **O que fica para o Matheus:** a D-GV-ENJOO-PY-3 propõe, numa etapa à parte e atrás de uma chave desligada, que o cérebro passe a ler
  o enjoo e que a novidade conte a queda também (o que tira a assimetria entre A e B). Uma nova pergunta sobre o gosto, com esse
  mecanismo, é um plano novo com uma faixa nova; esta run não roda de novo.

## 5. O negativo

Registrado como está:
- a parte do genoma, a parte do dono e a interação não aparecem com 36 unidades, nas duas medidas e nas duas análises;
- a repetibilidade fica perto de 0;
- o custo por vida (23,5 s) passou da estimativa (16 s).

Não houve medida sem variância, nem familiarização que não estabilizou, nem pet que quase não olhou: a fração das réplicas com uma olhada
foi 0,944.
