# A espec da C4: a memória autobiográfica do DigiBrain modular (episódio, recuperação, consolidação, decisão, facetas e fala)

**O que é:** a especificação das etapas M0 a M7 da `docs/TAREFA_V2_MEMORIA_AUTOBIOGRAFICA.md` (seções 3 e 4), exatamente como as ME-1
a ME-7 e as C4-E1 a C4-E3 decidiram (a tarefa, seção 8; `docs/PLANO_V3.md`, seção 2.3). Só papel: nenhum código, nenhuma vida, nenhuma
faixa pedida, nenhum plano de análise.

**Quem e quando:** Claude Code, Opus 5.5, em 2026-11-01, na worktree `v3-memoria-espec` (de `origin/main` `687841f`), a pedido do Gerente
da V3.

**O status:** APROVADA pelo Matheus em 2026-11-01, com as MA-1 a MA-8 (seção 11) e os valores da seção 8 pela recomendação. A subchave, os campos e os números seguem SEM FONTE salvo onde a linha diz. As ME-1 a ME-7 e as
C4-E1 a C4-E3 são DECIDIDAS (o Matheus, 2026-10-30). As leituras que esta espec teve de fazer sobre o que elas não fixam estão na seção 11
(MA-1 a MA-8), cada uma com a recomendação e o custo de errar; o código, quando vier, segue a decisão do Matheus sobre cada uma.

**Os rótulos:** [DADO] é número de artefato no git; [EXISTE] é o que o código da `main` (`687841f`) já faz; [MECANISMO] é o que uma fonte
verificada diz de um mecanismo; [HIPÓTESE] é o que falta medir.

## 0. Em uma página

- **A pergunta** (a tarefa, seção 1): o pet modular guarda o que viveu, lembra o que importa no contexto, consolida o que se repete ou
  pesa, e isso muda o que ele faz e, devagar, quem ele é, com cada mudança rastreável até os episódios e com a fala fiel a eles?
- **O que existe** [EXISTE]: o M-MEM mínimo (`digilab/digibrain/mem.py`): episódios de consumo e de visita ao lugar lembrado, até 16;
  a recuperação só com fome sem comida boa à vista; o valor do lugar é o do episódio mais recente nele; um termo só, no "explorar o lugar".
  A `consolidar` e a `evidencia_faceta` são vazias, e o M-PERS (`ganchos.py`) falha alto em `mudar_faceta`. A sonda `sem_memoria` do
  M-ARB já mede quando a memória mudou a escolha.
- **O que é novo** (seção 2): o episódio completo (M0); a codificação pela significância, a variação do corpo (M1, ME-1); a recuperação
  pelo contexto e pelo corpo a cada decisão (M2, ME-2); três memórias, recente, duradoura e central (M3, ME-3); o termo da lembrança em
  qualquer unidade, além do lugar (M4); três facetas adquiridas no M-PERS (M5, ME-4); a fala fiel (M6, ME-6).
- **A visita vazia** (a D-C1-3 e a C4-E1, seção 5): hoje ela já entra como episódio, com r = 0, e já derruba o lugar pela regra da
  recência. Com a C4-E1 ela passa a ter a significância do custo da ida (negativa), e o valor do lugar passa a somar os episódios dele
  (MA-2). Sem essa troca de regra, a C4-E1 não muda nenhuma escolha. A espec não responde a D-C1-3 e não a usa como alvo.
- **Onde entra** (ME-5): só no pacote `digilab/digibrain/` (o M-MEM, o M-PERS, o M-IMPULSO, o M-ARB e o M-ADAPT) e na fala
  (`digilab_fala_livre/`, `digilab/motivo.py` e o espelho no jogo, na etapa M6), atrás de `ConfigDigibrain.memoria_autobio`, desligada.
  O `engine.py`, o motor, o mundo, o corpo, o A, a v12 e o temperamento inato não mudam.
- **Desligada,** as vidas de hoje saem byte a byte (o gabarito antes, num commit próprio; seção 9).
- **O que esta espec não afirma:** que a memória conserta o longe, que o modular supera o A, que o pet "lembra" em algum sentido além do
  registro, ou que o mecanismo é novo (seção 10).

## 1. De onde vem

### 1.1 O que a C1, a C2 e a C3 deixaram [DADO]

Do `docs/RESULTADO_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md`:
- **a C1** (seção 13): M3\* − M2 por episódio no `longe_fixo` **+0,0489 [+0,0355; +0,0624], "> 0"**; no sorteado **−0,0106 [−0,0236;
  +0,0024], "indeterminado"**; a G-PESA da memória no M3\* do `longe_fixo` 0,122. **As visitas ao lugar lembrado** (13.4, item 2): no
  `longe_fixo`, 12 704 visitas e 12 704 vazias (a fração que acha 0,000); no sorteado, 21 954 e 21 942. A ida ao lugar lembrado termina
  12 704 vezes em `meta` e 17 603 em `trocou`. A interpretação do worker (13.5, não testada): o ganho não vem de achar ração no lugar
  lembrado; o caminho fica em aberto (a D-C1-3, DECIDIDA como questão aberta, sem run; `docs/TAREFA_V2_LONGE_REGULAR.md`);
- **a C2** (seção 14): o crédito do P2 na corrida, M2c − M2, sai "≈ 0" (+0,0028 [−0,0003; +0,0060]); registrada como negativa;
- **a C3** (seção 15): a escolha segurada até um evento, M3\*R − M3\*, sai **+0,0124 [−0,0060; +0,0308], "indeterminado"** (15.2). O Matheus decidiu seguir para a C4
  como planejada, **sem combinar com a C2 nem com a C3** (MA-7).

### 1.2 O M-MEM de hoje, linha a linha [EXISTE]

- **A codificação** (`Memoria.codificar`, chamada no fechamento da consequência em `adapt.py`): todo consumo vira episódio (origem
  `consumo`, a classe da comida); toda chegada ao `ponto` lembrado sem comer vira episódio (origem `visita`, classe `nao_havia`, **r = 0 e
  r_n = 0 forçados**). Cada episódio guarda a decisão, o lugar (a célula), o ponto, a região, a classe, as variações dos receptores, o r, o
  r_n, a hora e a falta da fome antes. Cheio (`n_ep` = 16), sai o de menor |r|, no empate o mais antigo.
- **A recuperação** (`Memoria.recuperar`): a pista é a urgência da fome acima de `lambda_busca` (S/4) e nenhuma comida boa à vista. O
  valor de cada lugar é o r_n do **episódio mais recente** nele ("o mais recente manda", SEM FONTE, `docs/ESPEC_DIGIBRAIN_MODULAR.md`,
  4.6). Volta o lugar de maior `mul(valor, S − min(S, dist·S/d_max))`, se positivo. **A visita vazia, com r_n = 0, já tira o lugar.**
- **O termo** (`termos_decisao`, `impulso.py`): `M = mul(w_mem, valor)`, só na unidade `("explorar", "ponto", P)`, que só existe se o
  M-MEM recuperou P. O M-ADAPT entrega o `Alvo.ponto`.
- **A sonda** (`arb.py`): `sem_memoria` tira o termo e a unidade do lugar, com o mesmo u; `memoria_decidiu` se a escolha muda.
- **O registro** (`motivo["memoria"]`): a pista, o id recuperado, o lugar e o valor; no fechamento, o id do episódio codificado.
- **Os ganchos vazios:** `consolidar` (nada), `evidencia_faceta` (vazio); o M-PERS devolve 0 em `faceta` e falha alto em `mudar_faceta`.
- **Sem rng** em nenhum deles.

### 1.3 As fontes

Todas da C0 (`docs/referencias/v3c0_referencias_verificadas.csv`) ou da V2 (`docs/referencias/v2_referencias_verificadas.csv`). As
ressalvas da C0 valem: a linha de Ho foi lida pela tese (a versão-irmã) e não faz teste de hipótese, com 10 a 50 execuções por condição;
**é direção, não tamanho de efeito.**

- [MECANISMO] **Ho (2005),** tese, University of Hertfordshire, `10.18745/th.14271`, VERIFICADA (DataCite). A fonte afirma, pela triagem
  (lida por inteiro): a significância de um evento é a variação das variáveis internas que ele causou; a memória longa guarda o evento mais
  significativo de cada categoria; a memória só supera o agente reativo quando guarda também os eventos negativos. **Autoriza:** a
  direção da ME-1 (a significância pelo corpo), da ME-3 (o mais significativo de cada categoria) e da C4-E1 (guardar o negativo). **Não
  autoriza:** os limiares, as capacidades, a regra de soma do lugar (MA-2), nem que o efeito se repita num pet com 11 receptores.
- [MECANISMO] **Ho, Dautenhahn e Nehaniv (2008),** *Connection Science* 20(1), `10.1080/09540090801889469`, VERIFICADA (metadados); a
  versão em periódico da tese, não lida: citada só pelo conteúdo da tese.
- [MECANISMO] **Francis, Mehta e Ram (2009),** o PEPE, `10.4018/978-1-60566-354-8.ch020`, VERIFICADA. A fonte afirma, pela triagem (texto
  completo, versão dos autores): episódios emocionais recuperados por semelhança fazem o robô buscar quem o acariciou e fugir de quem o
  chutou; guardar casos só mudou o comportamento com um reconhecedor que busca casos o tempo todo. Avaliação só qualitativa. **Autoriza:**
  a direção da ME-2 (recuperar a cada decisão, por semelhança). **Não autoriza:** a medida de semelhança daqui.
- [MECANISMO] **Castro e Gudwin (2013),** `10.4018/jse.2013010102`, VERIFICADA (V2): um módulo de memória episódica por cenas acoplado a
  uma criatura simulada. **Sem** afirmar que a cena recuperada informa a escolha (a fonte não sustenta isso; a espec do modular, 4.6).
- [MECANISMO] **Clayton e Dickinson (1998),** `10.1038/26216`, e **Gershman e Daw (2017)**, `10.1146/annurev-psych-122414-033625`,
  VERIFICADAS (resumo; a espec do modular, 4.6): o padrão de comportamento do lugar da comida e o episódio como fonte de valor. Seguem
  sustentando só o que já sustentavam.
- **SEM FONTE:** a medida de semelhança, os pesos dela, os limiares, as capacidades, a janela da consolidação, a soma do lugar, as
  facetas e os passos delas, e todo número da seção 8. **As mecânicas do *Dwarf Fortress*,** NÃO VERIFICADAS EM FONTE PRIMÁRIA (a tarefa,
  seção 3), são inspiração de desenho e não entram como fonte.
- **Nenhuma alegação de novidade.** Juntar corpo com homeostase, aprendizado em vida e memória episódica num agente já foi publicado (o
  `docs/PLANO_V3.md`, 2.2: Creatures, Gadanho e Hallam, Ho et al., Goertzel et al. e outros). O que o projeto faz é o teste causal com
  braço de controle, num pet persistente, com replay determinístico.

## 2. O que existe e o que é novo, por etapa

| etapa | [EXISTE] | novo (atrás de `memoria_autobio`) |
|---|---|---|
| **M0** o episódio | decisão, lugar, ponto, região, classe, Δ receptores, r, r_n, hora, fome antes, origem | o contexto (o que estava à vista, o cheiro, a noite), os participantes (o dono, o objeto; o outro pet como campo vazio), o corpo antes e depois (as leituras dos 11 receptores), o afeto antes e depois (V, E), a ação (a chave da unidade), a significância σ, a categoria, a referência ao log (o tick da decisão) |
| **M1** a codificação | todo consumo; toda visita, com r = 0 | pela significância σ ou pelo afeto acima de um limiar (ME-1); a visita vazia com σ = o custo da ida (C4-E1) |
| **M2** a recuperação | o lugar, só com fome sem comida boa | a lembrança: o episódio mais parecido com o contexto e o corpo, a cada decisão (ME-2, o PEPE); o lugar continua, com o valor pela soma (MA-2) |
| **M3** a consolidação | nada (`consolidar` vazia); a saída por menor \|r\| | recente → duradoura → central, por repetição e peso afetivo, com a central de um episódio por categoria e capacidade declarada (ME-3) |
| **M4** a decisão | o termo M só no lugar; a sonda `sem_memoria` | o termo L da lembrança na unidade da mesma ação; a sonda `sem_memoria` tira os dois |
| **M5** as facetas | o M-PERS neutro, `mudar_faceta` falha alto | três facetas nomeadas, passo pequeno, cada mudança com os ids (ME-4); o termo F no M-IMPULSO; a sonda `sem_faceta`; o temperamento intocado (ME-7, DM-6) |
| **M6** a fala | as três lacunas da auditoria (`docs/AUDITORIA_V2_PRODUTO_MODULAR.md`, seção 4) | a fala só alega o que o registro tem (ME-6), com o teste que falha |
| **M7** o determinismo | o G1 e o G2 das subchaves de hoje | o G1 e o G2 da `memoria_autobio`, com o gabarito antes |

## 3. O episódio e a codificação (M0 e M1)

### 3.1 O formato (M0)

Um episódio é um dicionário de inteiros, listas e cadeias, sem float, montado no fechamento da consequência (`adapt.py`, o mesmo ponto
de hoje), **só com o que o cérebro recebeu:** a Observação (o `sens` da decisão e o `pm1` do `observar`), os receptores (`l0`, `l1`), o
afeto do M-AFETO, os gestos do dono que o M-ADAPT já registra, e a unidade escolhida. Nenhum campo lê o motor por fora disso.

| campo | de onde | novo? |
|---|---|---|
| `id`, `decisao`, `tick` | o contador do M-MEM; o relógio do pet; o tick da decisão no log (a referência ao evento) | `tick` novo |
| `lugar`, `ponto`, `regiao` | `pm1` (como hoje) | — |
| `vista` | as classes à vista na decisão (`sens["objetos"]`), como lista ordenada sem repetição, de `TIPOS_ALVO_DIGIBRAIN` | novo |
| `cheiro`, `noite` | `sens["ha_cheiro"]`, `sens["contexto"]["noite"]` | novo |
| `acao` | a `chave` da unidade escolhida, como `chave_json` (comportamento, tipo de alvo, id ou ponto) | novo |
| `objeto` | o id e a classe do alvo, ou nenhum | novo |
| `dono` | os gestos do dono desde a decisão anterior (os nomes, na ordem) | novo |
| `outro` | sempre nenhum no protótipo (um pet só; a memória social está fora, a tarefa, seção 6) | novo, vazio |
| `corpo_antes`, `corpo_depois` | `l0`, `l1`, as leituras dos 11 receptores | novo (hoje só a diferença) |
| `delta` | `l1 − l0` por receptor (como hoje) | — |
| `V_antes`, `V_depois`, `E_antes`, `E_depois` | o M-AFETO antes e depois da consequência | novo |
| `r`, `r_n` | `cons` (como hoje; na visita, o de hoje é forçado a 0, ver 3.3) | — |
| `sigma` | a significância (3.2) | novo |
| `classe`, `origem`, `categoria` | 3.4 | `categoria` novo; origens novas |
| `fome_antes`, `hora` | como hoje | — |
| `rep`, `rec`, `memoria` | as contagens de repetição e de recuperação, e onde o episódio está (`recente`, `duradoura`, `central`) | novo (M3) |

### 3.2 A significância σ (ME-1)

- **σ = a variação do corpo que o evento causou,** lida pelo sinal homeostático que o M-AFETO já calcula: σ = r_n da consequência
  [EXISTE como conta; novo como campo]. É a leitura de Ho (a variação das variáveis internas), num número só, em [−S, S].
- **A visita vazia** (C4-E1, seção 5): σ = min(0, r da ida), com o r da ida o acumulado da intenção do `ponto` até a `meta` (o `op["r"]`
  do M-ESTADO, a soma dos r_n cortada em [−S, S] [EXISTE]). Nunca positivo: nada se achou. A magnitude é o custo medido, não um número
  posto (MA-1).
- **Com a C4-E2 no braço "REL sem negativos"** (seção 7): todo σ < 0 é gravado como 0 (MA-3).

### 3.3 Quando um evento vira episódio (M1, ME-1)

Um evento vira episódio se vale **uma** das três, conferidas nesta ordem, sem rng:
1. **a consequência no corpo pelo consumo:** comeu (como hoje);
2. **a visita ao lugar lembrado:** chegou ao `ponto` sem comer (como hoje, com σ da 3.2);
3. **a significância ou o afeto acima do limiar:** |σ| ≥ `theta_sig` **ou** a maior leitura de dor, susto ou estresse depois ≥
   `theta_afeto`. É o que traz para a memória o brincar que fez bem, o gesto do dono que mudou o corpo e o susto, e o que deixa fora o
   ocioso neutro.

**Decidido pelo Matheus em 2026-11-01 (#530, pela recomendação), antes da M2 e da M3:** o afeto passa a ser lido pela **variação**
na decisão (a subida de dor, susto ou estresse, l1 − l0 ≥ `theta_sig`), e não pelo nível depois ≥ `theta_afeto`. O motivo: nas vidas
de teste da M0 e da M1, o nível do estresse codificava quase todo evento (o registro de 2026-11, a seção da M0 e da M1). A troca entra
no código no PR da M2 e da M3, atrás da mesma chave desligada; até lá o código segue a regra acima. SEM FONTE além da leitura de Ho.

Os limiares (seção 8) são PROPOSTOS e SEM FONTE. O teste T-ME-1 confere que um evento forte vira episódio e um neutro não.

### 3.4 A categoria

`categoria = (comportamento, classe do alvo ou "sem_alvo", sinal de σ)`, com o sinal em {−1, 0, +1}; a visita vazia é
`("explorar", "nao_havia", −1)` (ou `0` com σ = 0). As origens passam a ser `consumo`, `visita` e `evento` (o caso 3 de 3.3). As classes
ganham `bola` e `sem_alvo`. A categoria é a unidade do "mais significativo de cada categoria" (ME-3, seção 4.3).

## 4. A recuperação e a consolidação (M2 e M3)

### 4.1 A lembrança (M2, ME-2)

**A cada decisão** (o PEPE: o reconhecedor que busca o tempo todo), depois do M-AFETO e do contexto do M-ESTADO, o M-MEM compara a pista
com cada episódio guardado (as três memórias) e devolve **a lembrança**: no máximo um episódio.

- **A pista** (ME-2): o lugar e a região de agora, as classes à vista, o cheiro, a noite (da Observação) e as faixas das urgências dos 11
  receptores, em quartos de S (a mesma faixa da C3: o número de limites S/4, S/2, 3S/4 que a urgência alcança) (do corpo).
- **A semelhança,** inteira, em [0, S]:
  `sim = div_arred(w_lugar·s_lugar + w_vista·s_vista + w_corpo·s_corpo, w_lugar + w_vista + w_corpo)`, com
  - `s_lugar = S − min(S, div_arred(dist·S, d_max))` (a distância do ponto do episódio, a conta de hoje);
  - `s_vista = div_arred(|A ∩ B|·S, |A ∪ B|)` sobre as classes à vista, mais o cheiro e a noite como dois itens; `S` se as duas são vazias;
  - `s_corpo = div_arred(n_iguais·S, 11)`, com `n_iguais` os receptores na mesma faixa.
- **Volta** o episódio de maior `sim`, se `sim ≥ sim_min`; senão nenhum (um contexto novo não recupera nada). **O empate** se desfaz por
  ordem fixa: o maior |σ|, depois o mais recente (a decisão, depois o id). **Sem rng** (MA-4).
- **A recuperação conta:** `rec += 1` no episódio lembrado (a M3 lê).

### 4.2 O lugar (o caminho de hoje, com o valor pela soma)

O caminho do lugar lembrado [EXISTE] continua, com a mesma pista (fome acima de `lambda_busca`, nenhuma comida boa à vista), a mesma nota
pela distância e o mesmo termo `M = mul(w_mem, valor)`. **Muda só o valor do lugar** (MA-2):

`valor(P) = clamp(Σ σ dos episódios de consumo de comida boa e de visita em P, nas três memórias, −S, S)`

no lugar de "o r_n do mais recente". Uma refeição boa e uma ida vazia que custou mais que ela deixam o lugar negativo; uma ida vazia que
custou pouco não apaga um lugar de três refeições. Com σ da visita = 0 (o braço sem negativos), as visitas não pesam na soma.

### 4.3 A consolidação (M3, ME-3)

Três memórias, cada uma com capacidade declarada (seção 8). A `consolidar(decisao)` roda **uma vez por dia do pet** (a cada 96 decisões,
na primeira decisão depois da virada do dia), sem rng:

- **a repetição:** quando um episódio novo é codificado, todo episódio guardado com a mesma categoria e o mesmo lugar ganha `rep += 1`;
- **o peso:** `peso = min(S, mul(|σ|, S + div_arred(rep·S, 2) + div_arred(rec·S, 4)))` (a repetição pesa mais que a recuperação; SEM
  FONTE);
- **recente → duradoura:** na consolidação, cada episódio da recente com mais de `janela_rec` decisões sobe se `rep ≥ 1`, ou se
  |σ| ≥ `theta_dur`, ou se `rec ≥ 1`; **senão é esquecido** (sai, com o id e o motivo `esquecido` no registro). A recente cheia descarta o
  de menor peso, como hoje (a PE-16);
- **duradoura → central:** em cada categoria, o episódio de maior peso com `rep ≥ n_rep_central` é o candidato; a central guarda **um
  por categoria**, até `n_cen` categorias, as de maior peso. **Um episódio forte único (rep = 0) nunca entra na central** (o custo de errar
  da ME-3). Quem sai da central volta à duradoura;
- **a duradoura cheia** descarta o de menor peso, no empate o mais antigo (a regra de hoje, generalizada);
- **o registro** de cada consolidação: os ids que subiram, os que foram esquecidos e os que saíram por capacidade, por memória.

## 5. A visita vazia ao lugar lembrado (a D-C1-3 e a C4-E1)

- **O que existe** [EXISTE]: a visita sem comida já é episódio (origem `visita`, r = 0) e, pela regra "o mais recente manda", já tira o
  lugar da recuperação. Das 12 704 visitas da C1 no `longe_fixo`, nenhuma achou ração [DADO, 1.1].
- **O que a C4-E1 muda:** a visita ganha σ = min(0, r da ida) (3.2), o custo que a viagem teve no corpo. **Com a regra de hoje, isso não
  muda nenhuma escolha:** valor 0 e valor negativo dão o mesmo "fora" (o `recuperar` pula valor ≤ 0). A C4-E1 só tem efeito com a soma do
  lugar (4.2) e com a lembrança da ida vazia na M4 (a unidade `explorar` ao `ponto` P ganha um termo L negativo quando a lembrança é a ida
  vazia a P). Por isso a MA-2 vai junto da C4-E1.
- **O controle** (C4-E2): o braço "REL sem negativos" grava σ = 0 em todo episódio negativo, inclusive a visita (MA-3); a única diferença
  entre os dois é o sinal.
- **A L-3** (C4-E3): fica fora pela D-C1-1. Se ela voltar, o plano diz qual é o braço e qual é o controle antes de somar os dois.
- **A D-C1-3 não é respondida aqui,** e a espec não a usa como alvo. O que a espec dá ao descritivo dela, sem run: o registro de cada
  visita (o σ, o número de decisões da ida, as classes à vista na chegada e na decisão seguinte, e se uma comida boa entrou na vista
  durante a ida).
- **Um risco escrito antes** [HIPÓTESE]: a interpretação da C1 (13.5, não testada) é que a ida ao lugar lembrado deixa o pet perto dos
  pontos fixos quando a ração cai. Se for isso, a C4-E1, que corta as idas vazias, pode **tirar** o ganho da C1 no `longe_fixo`. Um nulo ou
  um negativo da C4-E1 ali é plausível e não é falha do código.

## 6. A decisão e as facetas (M4 e M5)

### 6.1 O termo da lembrança (M4)

- **Onde:** a lembrança (4.1) soma `L = mul(w_lem, σ)` à unidade da lista de agora com a mesma ação do episódio: o mesmo comportamento e
  a mesma classe de alvo (para `ponto`, o mesmo lugar; para `sem_alvo`, o comportamento). Sem unidade correspondente, nenhum termo. O L
  pode ser negativo: a comida que fez mal (`comer`, `podre`, σ < 0) à vista de novo, o caso do T1 do J5.
- **O termo** é um novo nome em `TERMOS` do M-IMPULSO (`lembranca`), somado antes da `phi`, como os outros; o M ao lugar continua em
  `memoria`.
- **A sonda contrafactual** (a tarefa, M4): `sem_memoria` passa a tirar os dois (`memoria` e `lembranca`), com o mesmo u, como hoje; e
  uma sonda nova, `sem_lembranca`, tira só o L. `memoria_decidiu` e `lembranca_decidiu` no registro. **Nenhuma rng nova:** a sonda reusa o
  u da decisão (o padrão de `arb.py`).
- **O registro:** `motivo["memoria"]` ganha a lembrança (o id, o `sim`, a memória onde estava, o σ, o L e a unidade que o recebeu).

### 6.2 As facetas adquiridas (M5, ME-4 e ME-7)

**Três, nomeadas** (MA-5), cada uma um inteiro em [−S/4, S/4], começando em 0 em toda vida:

| faceta | a evidência (`evidencia_faceta`) | o termo F (no M-IMPULSO) |
|---|---|---|
| `cautela_comida` | os episódios de `comer` na duradoura e na central, com σ | `−mul(f, S)` em `comer` de classe ainda sem episódio positivo; positiva = mais cautela |
| `apego_dono` | os episódios com algum gesto do dono, com σ | `mul(f, S)` em `chamar_atencao` |
| `ousadia_longe` | os episódios de `explorar` (o cheiro, o vagar, o lugar; a visita vazia entra aqui) | `mul(f, S)` em `explorar` com alvo fora da vista |

- **A mudança** (`mudar_faceta`): na consolidação diária, para cada faceta, o sinal da soma dos σ da evidência; a faceta anda **um passo**
  `eta_faceta` nesse sinal (zero se a soma for 0), cortada em [−S/4, S/4]. Cada mudança guarda os ids dos episódios da evidência, o passo e
  o dia.
- **O termo F** entra em `TERMOS` (`faceta`) e ganha a sonda `sem_faceta`, com `faceta_decidiu`.
- **O temperamento inato não muda** (ME-7, DM-6): o M-PERS não tem acesso à `ConfigDigibrainInatos` nem ao genoma; um teste confere que o
  registro inato no fim da vida é igual ao do nascimento, campo a campo.
- **A subchave própria** (MA-6): as facetas ficam atrás de `facetas_mem`, que só vale com a `memoria_autobio`, para a validação separar a
  decisão da faceta.

## 7. A fala (M6), os braços e o que não muda

### 7.1 A fidelidade da fala (M6, ME-6)

As regras são as da `docs/ESPEC_DIGIBRAIN_MODULAR.md`, seção 7 (o motivo por módulo, "a fidelidade da fala"), aplicadas à memória nova:
- "lembrei de X" só com a lembrança = X naquela decisão;
- "fiz Y porque lembrei de X" só com `lembranca_decidiu` (ou `memoria_decidiu`, no lugar) verdadeiro naquela decisão;
- "fiquei mais cauteloso com Z" só com uma mudança de faceta registrada, citando os ids.

**As três lacunas da auditoria** (`docs/AUDITORIA_V2_PRODUTO_MODULAR.md`, seção 4) são corrigidas na M6, antes de a fala citar a memória
nova: o prompt `livre-v6` (`digilab_fala_livre/prompt.py`), o verificador que aceita causa por memória (`digilab_fala_livre/verificador.py` e o espelho
`web/app/src/falaLivre.ts`) e o motivo do N6 (`digilab/motivo.py`). Como a lacuna do verificador está também no jogo, a M6 toca o `web/app/` com
paridade (MA-8). O teste falha se a fala alega o que o registro não tem.

### 7.2 Os braços que o código dá (para o plano; os números e o contraste são do plano)

`ConfigDigibrain.controle_mem: str = "rel"`, com `CONTROLES_MEM = ("rel", "sem", "rec", "emb", "rel_sem_neg")`, só com a
`memoria_autobio` (a tarefa, seção 4, e a C4-E2):

| braço | a lembrança (4.1) | o lugar (4.2) | σ < 0 |
|---|---|---|---|
| **REL** | o mais parecido | a soma | como é |
| **SEM** | nenhuma (o episódio é codificado e consolidado, nunca lido na decisão) | nenhum | como é |
| **REC** | o mais recente, sem olhar o contexto | o lugar do consumo bom mais recente | como é |
| **EMB** | um sorteado entre os guardados, por uma rng própria (`derivar_semente(semente, "mem_emb")`, nunca a de política) | o lugar do episódio sorteado, se for consumo bom | como é |
| **REL sem neg** (C4-E2) | o mais parecido | a soma | gravado como 0 (MA-3) |

As facetas, no SEM, seguem os episódios consolidados (elas não leem a lembrança); o plano diz se isso basta ou se o SEM desliga a
`facetas_mem` (MA-6).

### 7.3 Onde entra e o que não muda

**Onde entra:**
- **as subchaves:** `ConfigDigibrain.memoria_autobio: bool = False`, `facetas_mem: bool = False` e `controle_mem: str = "rel"`,
  PROPOSTAS, SEM FONTE como valor (a direção vem de Ho e do PEPE). **Erro alto (`ValueError`):** `memoria_autobio` sem `m_mem`; com a
  `credito_corrida`, a `intencao_suspensa` ou a `redecidir_evento` (a decisão de não combinar C4 com C2 nem C3; MA-7); sem as duas
  subchaves do cheiro (os braços do conserto, como a RE-4 da C3); `facetas_mem` sem `memoria_autobio`; `controle_mem` fora da lista, ou
  diferente de `"rel"` sem a `memoria_autobio`;
- **os campos** (seção 8): na `ConfigDigibrainInatos`, no módulo `mem` do `CAMPOS_POR_MODULO` (`ganchos.py`), e as facetas num módulo
  `pers` novo;
- **os módulos:** o M-MEM (o episódio, a codificação, a lembrança, o lugar pela soma, a consolidação, a evidência), o M-PERS (as facetas),
  o M-IMPULSO (os termos `lembranca` e `faceta`), o M-ARB (as sondas `sem_lembranca` e `sem_faceta`; `sem_memoria` tira os dois) e o
  M-ADAPT (a ordem, o episódio completo, a consolidação diária e o registro); na M6, a fala.

**O que não muda:** o `engine.py` (o sha em `ENGINE_SHA256_V0`), o motor, o mundo, o corpo, o cheiro, o `longe_fixo`, o A, a v12; o P1, o
P2, a persistência, o reflexo e os inatos do #428; o temperamento inato e o genoma (a EG-5: o aprendido nunca entra nele); as medidas do
orquestrador. **A web** fica fora até a M6 (a pesquisa de cérebro atrás de chave desligada fica no Python; o modular ainda não está no
jogo); a M6 é a exceção, pela lacuna no `web/app/src/falaLivre.ts`.

## 8. Os parâmetros (DECIDIDOS pelo Matheus em 2026-11-01, pela recomendação; SEM FONTE; nenhuma calibração por nó)

| campo | valor | o que é | por que este |
|---|---|---|---|
| `theta_sig` | S/8 = 128 | o \|σ\| que faz um evento virar episódio (M1) | a metade do `lambda_busca`; nenhuma fonte |
| `theta_afeto` | S/2 = 512 | a leitura de dor, susto ou estresse que faz um evento virar episódio | o meio da escala |
| `n_rec` | 16 | a capacidade da recente | o `n_ep` de hoje |
| `n_dur` | 32 | a capacidade da duradoura | o dobro da recente |
| `n_cen` | 8 | a capacidade da central (categorias) | pequena (ME-3) |
| `janela_rec` | 96 decisões | quanto um episódio fica na recente antes de subir ou ser esquecido | um dia do pet (1 440 ticks, 15 por decisão) |
| `theta_dur` | S/4 = 256 | o \|σ\| que sobe sem repetição nem recuperação | o `lambda_busca` |
| `n_rep_central` | 2 | as repetições para a central | o mínimo que exclui o episódio único |
| `w_lugar`, `w_vista`, `w_corpo` | 2, 1, 1 | os pesos da semelhança (4.1) | o lugar pesa como o mundo e o corpo juntos |
| `sim_min` | 3S/4 = 768 | a semelhança mínima para lembrar | alta, para um contexto novo não recuperar |
| `w_lem` | S/2 = 512 | `L = mul(w_lem, σ)` | a metade do `w_mem` (o lugar fica como o caminho principal) |
| `eta_faceta` | S/64 = 16 | o passo da faceta por dia | 16 dias para o teto de S/4: "devagar" (ME-4) |
| teto das facetas | S/4 | o \|f\| máximo | pequeno (ME-4) |

O `n_ep`, o `lambda_busca`, o `d_max` e o `w_mem` de hoje não mudam. Os números vão à decisão do Matheus junto da espec; uma calibração,
se houver, é do plano e com sementes próprias, e a validação roda uma vez (CLAUDE.md, "Pesquisa: o método").

## 9. Os testes planejados (antes de qualquer vida; sementes 101…505)

| teste | o que confere |
|---|---|
| **o gabarito antes** | `tests/gabaritos/memoria_autobio_de_hoje.json`: o M3\* no `longe_fixo`, no longe e no comedouro, gravado num commit próprio antes do código |
| **G2** | com a `memoria_autobio` desligada, os gabaritos do M3\*, do M2 (`habito_intencao_de_hoje.json`, #513), da C3 (`redecidir_evento_de_hoje.json`), do conserto e do modular saem byte a byte; o estado interno e o motivo sem campo novo |
| **G2-SEPARADO** | ligada, ela muda só a vida do braço que a liga; fora do pacote `digibrain`, do orquestrador e da fala, nada a lê |
| **G1** | o replay bit a bit de cada vida com a subchave ligada, nos cinco braços de 7.2, nas cinco sementes, com e sem a `facetas_mem` |
| **T-ME-0** (M0) | o episódio sai igual no replay; um teste por AST confere que o M-MEM só recebe o `sens`, o `pm1` do `observar`, os receptores, o afeto, os gestos e a unidade (nenhum objeto do motor) |
| **T-ME-1** (M1) | um evento forte vira episódio e um neutro não; o mesmo log codifica os mesmos episódios; a visita vazia tem σ = min(0, r da ida) |
| **T-ME-2** (M2) | um contexto conhecido recupera o episódio certo; um contexto novo (sim < `sim_min`) não recupera nada; o empate pela ordem fixa |
| **T-ME-3** (M3) | um episódio repetido consolida; um esquecido some e fica no registro; um episódio forte único não entra na central; a central tem um por categoria e no máximo `n_cen` |
| **T-ME-4** (M4) | a sonda contrafactual: numa sequência sintética, a lembrança muda a escolha e `lembranca_decidiu` é verdadeiro; sem a lembrança, a escolha de antes. O L negativo da comida que fez mal |
| **T-ME-5** (M5) | cada mudança de faceta aponta os ids; o registro inato e o temperamento iguais ao do nascimento, campo a campo; `mudar_faceta` com `facetas_mem` desligada falha alto |
| **T-ME-6** (M6) | o teste falha se a fala alega lembrança, causa por memória ou mudança de faceta sem o registro; as três lacunas, uma por uma |
| **T-ME-VISITA** | a C4-E1 e a C4-E2: com a regra de hoje, a σ negativa não muda a escolha (o caso de 5); com a soma, muda; no "REL sem neg", a visita pesa 0 |
| **a rng** | o M-MEM só chama rng no braço EMB, a dele; a rng de política tem as mesmas chamadas com e sem a lembrança |
| **G-MECANISMO, G-INT, G-SEM-DIRECAO, G-RECEPTOR** | os de hoje passam com a subchave ligada |

## 10. O que esta espec não afirma

- **Que a memória conserta o longe,** nem que a C4-E1 melhora o `longe_fixo` (o risco escrito em 5).
- **Que a D-C1-3 está respondida.**
- **Que o modular supera o A.** O A11 não está em nenhum braço.
- **Que o pet lembra** em algum sentido além de "o episódio está no registro e mudou a decisão pela sonda".
- **Que o mecanismo é novo** (1.3).

## 11. O que esta espec leu além das ME (para o Matheus)

As ME-1 a ME-7 e as C4-E1 a C4-E3 não fixam estes oito pontos. **Todos DECIDIDOS pelo Matheus em 2026-11-01, pela recomendação; SEM FONTE.**

| # | a leitura | a recomendação | o custo de errar |
|---|---|---|---|
| **MA-1** | o tamanho do episódio negativo da visita vazia(DECIDIDA) | **σ = min(0, r da ida):** o custo medido no corpo, a leitura de Ho | um negativo fixo (−S/4, por exemplo): um número sem fonte que não é a variação do corpo; σ igual ao r de uma decisão só: o custo da ida some |
| **MA-2** | o valor do lugar(DECIDIDA) | **a soma dos σ dos episódios do lugar,** no lugar de "o mais recente manda" | manter a recência: a C4-E1 não muda nenhuma escolha (valor 0 e negativo dão o mesmo "fora"), e a validação mede um nulo por construção |
| **MA-3** | o que é o braço "REL sem negativos" (C4-E2)(DECIDIDA) | **σ < 0 gravado como 0:** os mesmos episódios, só sem o sinal | não codificar os negativos: muda a capacidade e as repetições junto com o sinal, e o controle mede duas coisas |
| **MA-4** | o empate da lembrança (a tarefa deixa "ordem fixa ou rng própria")(DECIDIDA) | **ordem fixa:** o maior \|σ\|, depois o mais recente | uma rng própria: mais um fluxo para o G1 e para a separação das rngs, sem pergunta que o peça |
| **MA-5** | quais facetas (ME-4: "poucas, nomeadas")(DECIDIDA) | **três: `cautela_comida`, `apego_dono` e `ousadia_longe`,** cada uma ligada a episódios que o mundo de hoje produz | muitas: o pet "muda de personalidade" e a rastreabilidade se perde; uma só: a M5 não mostra nada além da comida |
| **MA-6** | as facetas atrás de subchave própria(DECIDIDA) | **sim, `facetas_mem`:** a validação separa o que a lembrança muda do que a faceta muda | na mesma chave: um efeito da faceta aparece como efeito da recuperação |
| **MA-7** | a C4 com a C2 ou a C3(DECIDIDA) | **recusar com erro alto** (a decisão do Matheus de seguir sem combinar) e exigir as subchaves do cheiro (o M3\* do conserto) | aceitar: um braço sem plano roda; recusar demais só pede tirar a linha quando houver um braço novo com plano |
| **MA-8** | a M6 no jogo(DECIDIDA) | **a M6 corrige as três lacunas nos dois lados,** com paridade, porque a do verificador está também em `web/app/src/falaLivre.ts` | só no Python: o jogo segue aceitando "porque lembrei" sem verdade, e a fala do A v11 continua com a lacuna |

**A ordem das etapas** (a tarefa, seção 5: um PR por etapa): o gabarito antes; M0 e M1 juntas (o episódio e a codificação, sem efeito
na escolha); M2 e M3; M4 (a primeira que muda a escolha); M5; M6; e o M7 em cada PR. A validação causal (a seção 4 da tarefa) vem
depois, com o plano antes, e só se o Matheus mandar.
