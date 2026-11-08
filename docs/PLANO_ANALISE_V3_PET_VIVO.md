# PLANO DE ANÁLISE V3 — PET_VIVO, etapa 0: a auditoria da escolha (0b) e a medida de "age pelo estado" (0c) (2026-11-07, Claude Code, Opus 5.5)

**Status: APROVADO pelo Matheus em 2026-11-08, repassado pelo Gerente da V3.** À pergunta "Aprova o plano do #704 e as PV-0-1 a
PV-0-11 pela recomendação?", no chat do Gerente, a resposta foi "Aprovo todas". Depois de ler as decisões explicadas no vault
(DigiLab Research, `30 Decisões e protocolo/PET_VIVO — decisões PV-0.md`), à pergunta "Depois de ler, a aprovação das PV-0 continua
valendo?", a resposta foi "Continua valendo". O registro está nos dois comentários do PR #704 de 2026-11-08 (05:05 e 05:07 UTC). Eles foram escritos pela sessão do Gerente com a
conta `matheusmmmp`, sem app. **Esta sessão não ouviu o Matheus diretamente:** a confirmação dele vale no merge (a regra da memória das
aprovações repassadas da C4, 2026-11-01).

As decisões PV-0-1 a PV-0-11 estão DECIDIDAS pela recomendação, em `docs/TAREFA_V3_PET_VIVO.md`, seção 8. **Nenhum replay e nenhuma
conta deste plano rodam antes de três coisas:**
1. a marca "APROVADO pelo Matheus" neste cabeçalho (feita acima);
2. o código da seção 9 na `main`, com os testes dele;
3. as três conferências da seção 2.3, que falham alto antes de qualquer medida.

**Este plano não calcula nenhum número de resultado.** Os números que ele cita já estão em artefatos do git, ou são fatos do código, com o
arquivo. Os cortes e o Δ são PROPOSTOS e SEM FONTE.

**De onde vem:**
- a rodada PET_VIVO (vault DigiLab Research, `20 Temas/Pet vivo.md`, seção 5, a etapa 0, itens 0b e 0c). Os documentos de pesquisa ficam no vault, e não
  no repositório (decisão do Matheus, 2026-11-08; o PR #703 foi fechado). A nota substitui o antigo `rodada_pet_vivo.md`;
- a crítica às análises, na mesma nota, seção 4: o sorteio proporcional favorece quem tem mais unidades, e nenhum gate de hoje mede "age pelo
  estado";
- **a autorização do Matheus (2026-11-07): "Sim, a etapa 0"**, em resposta a "Aprovo a etapa 0 da PET_VIVO e despacho a verificação e a
  auditoria?". Ela libera o papel e as vidas já gravadas. Ela não aprova este plano e não libera vida nova.

**O molde:** o descritivo da D-C1-3 no REL (o adendo 11 do `docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md` e o
`experiments/descritivo_dc13_rel.py`). Daquele molde este plano reusa:
- os dois estágios (ler os artefatos, depois refazer as vidas no replay);
- o código da run numa worktree destacada;
- as três conferências que falham alto;
- a regra de leitura escrita antes, e o "roda uma vez".

**O que este plano não afirma:**
- que o pet "pensa" ou "tem estados internos" no sentido biológico. As medidas são nomes de conta;
- que a auditoria prova uma causa. Ela é pós hoc: as vidas já foram lidas, e as hipóteses foram escritas depois disso (seção 6);
- que o modular supera o A, ou o contrário.

**Nenhuma alegação de novidade.**

## 0. O que existe hoje (os fatos do código que o desenho usa)

Conferidos na `main` (`origin/main` de 2026-11-07).

- **As unidades** (`digilab/digibrain/impulso.py`, `Impulso.alvos`): cada decisão tem de 11 a 18 unidades (comportamento, alvo), na
  ordem fixa dos 7 comportamentos:
  - o `comer` tem uma unidade por comida vista e mais uma pelo cheiro, se há cheiro;
  - o `brincar` tem uma por bola vista, ou uma sem alvo;
  - o `explorar` tem o vagar, o cheiro (se há) e o ponto lembrado (se o M-MEM recuperou um);
  - o `ocioso`, o `dormir`, o `chamar_atencao` e o `emburrar` têm uma unidade cada.
- **A ativação** (`Impulso.unidades`): o termo `inato` de cada unidade é o `inato_b[b]` do comportamento **inteiro**, mais o `W0_tipo` do
  alvo. Ele se repete em cada unidade do mesmo comportamento. Os outros termos são `prox`, `nov`, `incentivo`, `habito`, `memoria`,
  `persistencia` e, com a `memoria_autobio`, `lembranca` (e `faceta` com as facetas).
- **O peso e o sorteio** (`digilab/digibrain/arb.py`): `w = a + mul(g_exp, ε)` nas unidades com `a > 0`, e 0 nas outras. Hoje ε = S/8
  (`ConfigDigibrainInatos.epsilon`, PROPOSTO, SEM FONTE). O sorteio é proporcional a `w` (a regra de Luce, espec 4.7).
  - **Daí vem o efeito do número de alvos:** um comportamento com k unidades ativas soma k vezes o inato e k vezes a exploração.
  - A probabilidade de cada unidade é exata: `w_i / T`, com `T = Σ w`. **A distribuição não precisa ser amostrada.** Ela sai do `w` de
    cada decisão.
- **O reflexo do sono** (`Arbitragem.reflexo`): com a leitura da energia abaixo de `lambda_sono`, dormir, sem sorteio e sem sonda.
- **O ganho da exploração** (`digilab/digibrain/afeto.py`): `g_exp = clamp(e0 + mul(β_T, falta do tédio) − mul(β_U, max_r u_r), 0, e_max)`.
  O corpo entra na escolha por três portas:
  - pelas urgências em `z` (o inato e o hábito);
  - pelo `g_exp`;
  - pelo incentivo do P1, que lê a percepção do corpo `pc`.
- **O registro de cada decisão** (o `motivo`, espec seção 7): as unidades com `termos`, `a` e `w`; o `u`; o `reflexo`; a `escolha`; as
  urgências e o `g_exp` em `afeto`; o estado; as sondas "quem decidiu". Os gabaritos da AN0 trazem esse `motivo` inteiro. Por exemplo, em
  `web/app/test/gabaritos/digibrain_modular_longe_fixo.json.gz` cada decisão tem 6 ou mais unidades com os 8 termos.
- **As sondas** (`SONDAS` em `arb.py`): refazem a escolha sem um termo, com o mesmo `u`. Elas dizem se o termo mudou **aquela** escolha,
  e não quanto ele muda a distribuição.
- **O que o `motivo` não traz:** o vetor `z`, que só existe dentro do `Impulso`. Para separar o inato por receptor (a seção 4.1) e para
  o contrafactual (a seção 4.4), é preciso o replay.

## 1. As perguntas, escritas antes

- **Q-0b:** em cada decisão, de onde vem a probabilidade de cada comportamento? Quanto vem de cada termo, quanto só do número de
  unidades, quanto do reflexo do sono, e quanto ela muda quando o corpo muda?
- **Q-0c:** qual medida diz, numa vida, quanto o pet "age pelo estado"? E como ela vira gate ao lado do forrageio?

**As três hipóteses da rodada** (a busca colada de 2026-11-07, pela crítica do vault DigiLab Research, `20 Temas/Pet vivo.md`, seção 4) são HIPÓTESES.
A HA tem uma pista na literatura (a nota da seção 4.2); as outras duas são SEM FONTE:

| | a hipótese | em uma frase |
|---|---|---|
| **HP** | **os pesos inadequados** | o corpo chega à escolha com força, mas para o comportamento errado, ou é afogado pelos termos que não são do corpo (o viés, o contexto) |
| **HA** | **o número de alvos** | o comportamento com mais unidades (o `explorar`, o `comer` com muita comida à vista) ganha probabilidade só por isso |
| **HC** | **o sinal do corpo fraco** | a distribuição quase não muda quando um receptor muda: o corpo pesa pouco em qualquer direção |

Os nomes HP, HA e HC são deste plano. Eles evitam a colisão com os M1 a M5, os PV-1 a PV-5 e os H1 a H5 da D-C1-3 (D-PV0-2).

## 2. A fonte dos dados

### 2.1 As vidas (PV-0-2)

| fonte | o que é | as vidas | o código |
|---|---|---|---|
| **a C4, o REL e o SEM** | a run da memória autobiográfica (o adendo 9 do plano da V2; RESULTADO, seção 16), faixa 77101…77505 | 200 unidades (5 bases × K = 40) × 4 donos × 3 lugares (`longe_fixo`, `comedouro`, `longe`) × 2 braços = **4 800 vidas**, de 14 dias cada | o do `a287ba2` (o `git_head` do `meta.json`) |
| **a AN0** | o descritivo de hoje da tarefa ACOES_NOVAS (`docs/TAREFA_V3_ACOES_NOVAS.md`, seção 10): os gabaritos da LM0 e os `fins` da LM4, nas sementes dos testes | as vidas de `digibrain_modular_comedouro.json.gz`, `digibrain_modular_longe_fixo.json.gz` e `digibrain_modular_fins.json.gz` (em `web/app/test/gabaritos/`), cerca de 5 400 decisões do REL (`artifacts_v3_acoes_novas/hoje.json`) | o da `main`. Os gabaritos são de paridade, refeitos pelo código de hoje |

- **Por que as duas:** a C4 tem o tamanho, com os 4 donos e os 3 lugares, mas com o código de antes do jogo v17 a v19. A AN0 é pequena,
  mas é o cérebro de hoje. A leitura sai por fonte, lado a lado, sem teste entre elas (como a AD11-5).
- **Por que o REL e o SEM:** o REL é o cérebro dos ovos (#562). O SEM é o mesmo cérebro sem a memória lida, então a comparação mostra
  quanto a lembrança e o lugar mudam a escolha. Os outros quatro braços da C4 ficam fora (seção 10).
- **O AN4 (as 78xxx, o LAB e o LAB+P) fica fora:** o passeio muda as unidades do `explorar`, e é outra pergunta.

### 2.2 Onde estão (PV-0-3)

- **A C4:** lida só da pasta `D:\Trab\digilab\v3-memoria-run\artifacts_v2_digibrain_prototipo\memoria_autobio\run\`, que fica fora do
  git. O script não escreve nela. Conferi nesta tarefa, com o `sha256sum`, que os arquivos dela têm os sha256 do `meta.json`:
  - `meta.json`: `6315784c…3a18`;
  - `resultado.json`: `6f8c91d8…d6d3`;
  - `medidas.json.gz`: `8b48d0a2…d93b`;
  - `vidas.tar.gz`: `aa0c3987…0aed`.

  **Achado (D-PV0-1):** a mesma pasta está no git, em `artifacts_v2_digibrain_prototipo/memoria_autobio/run/`, com os mesmos sha256 (o
  `vidas.tar.gz` conferido nas duas). A cópia do git fica de reserva: se a pasta de fora sumir, o script lê a do git, com as mesmas
  conferências.
- **A AN0:** os três gabaritos do git. O sha256 de cada um entra no código, conferido no dia do PR do código.

### 2.3 As conferências que falham alto, antes de qualquer medida (PV-0-4)

- **O código da C4:** os sha256 dos 18 módulos, dos 4 orquestradores e da config, numa worktree destacada no `a287ba2`, iguais aos do
  `meta.json`. É o `conferir_codigo` do `experiments/descritivo_dc13_rel.py`, reusado por import, sem mudar aquele arquivo.
- **A fonte:** o sha256 de cada arquivo da C4 (acima) e de cada gabarito da AN0.
- **O G1 de cada vida:**
  - **na C4:** as medidas refeitas no replay iguais às do `medidas.json` (menos o `custo`), e o log rejogado igual ao do disco;
  - **na AN0:** o `motivo` refeito igual ao do gabarito, decisão a decisão, e as assinaturas dos módulos iguais.
- **O G1 com o contrafactual ligado:** a mesma vida rejogada com o contrafactual da seção 4.4 sai igual, byte a byte, à vida sem ele. Se
  o contrafactual tocar qualquer estado do cérebro, da rng ou do corpo, o G1 pega e o script para.

## 3. A unidade e o recorte

- **A unidade da análise:** a vida. As contas por decisão viram médias por vida. Os IC são por (braço, lugar) sobre as unidades
  (base, semente), com a média dos 4 donos, como na C4 (A4.4.6). Os donos saem também separados, sem IC.
- **As decisões que entram:** todas, com o reflexo marcado. As medidas da distribuição (A-1, A-2 e A-4) usam só as decisões **com
  sorteio ou com um candidato só** (fora do reflexo e da escolha segurada). O reflexo tem a medida própria (A-3).
- **Os lugares saem separados, porque a posta da ração é diferente em cada um** (a nota do vault, `20 Temas/Pet vivo.md`, seção 2, lida
  em `fa09444`; conferido na `main` `f3f717e0`, em `DonoComLugar.lugar`, `digilab/mundo.py`):
  - no `comedouro`, a ração vai sempre ao centro do comedouro;
  - no `longe_fixo`, ela vai a um dos pontos fixos, sorteado entre eles a cada vez;
  - no `longe`, a direção (uma de 16) e a distância saem do sorteio a cada vez, a partir da posição do pet.
  Então, no `longe`, o lugar lembrado não prevê onde a próxima ração cai, e os termos `memoria` e `lembranca` da A-1 se leem de outro
  jeito nos três lugares. Juntar os lugares misturaria isso.
- **Os dias:** os 14, e também só os dias 8 a 14, como na C4 (depois que o hábito e a memória se formam).

## 4. As medidas da 0b, em cada decisão

As contas são todas inteiras ou em razão exata (`fractions`), a partir do `w`. A probabilidade de um comportamento b é
`P_b = Σ_{i ∈ b} w_i / T`.

### 4.1 A-1: o peso de cada termo

- **Na unidade escolhida e nas rivais:** para cada um dos 9 termos (inato, prox, nov, incentivo, hábito, memória, persistência, lembrança
  e a exploração `mul(g_exp, ε)`), a parte dele no `w`. A parte é `|t| / Σ|t|` sobre os termos da unidade, com a exploração entre eles.
  Saem a média e os quantis 10, 50 e 90 por vida.
- **"As rivais"** são as unidades com `w > 0` que não foram escolhidas, em duas versões: a rival mais forte e a média ponderada por `w`.
- **O inato por porta** (só no replay, porque precisa do `z`): o `inato_b` separado em viés (`z_0 = S`), as urgências dos 11 receptores,
  o contexto e as conjunções, e F, V e E. A **parte do corpo** no inato é a soma das urgências e das duas conjunções com urgência
  (`fome_sem_comida`, `cuidado_humor`), sobre o |inato|. O hábito se separa do mesmo jeito (`H·z`).
- **O quanto cada termo muda a distribuição:** a distância de variação total `TV(P, P^{−t})`, com `P^{−t}` a distribuição refeita sem o
  termo t (a ativação `phi(soma − t)`, como nas sondas). É a versão em distribuição da sonda "quem decidiu": a sonda diz se a escolha
  mudou com aquele `u`, e a TV diz quanto mudou a chance.
- **As sondas gravadas** (`<termo>_decidiu`) saem ao lado, como a fração de decisões, para comparar com a TV.

### 4.2 A-2: o número de alvos

- **Quantas unidades ativas** (`w > 0`) cada comportamento tem em cada decisão: a média, o máximo e o histograma por comportamento.
- **A distribuição com uma unidade por comportamento, com o mesmo máximo:** `P¹_b = max_{i ∈ b} w_i / Σ_{b'} max_{i ∈ b'} w_i`. É a
  pergunta "e se cada comportamento tivesse um alvo só, o melhor dele?".
- **As medidas:**
  - `TV(P, P¹)` por decisão: quanto da distribuição vem só do número;
  - **a inflação** de cada comportamento, `ρ_b = Σ_k P_b / Σ_k P¹_b` sobre as decisões da vida: ρ > 1 quer dizer que o comportamento
    ganha pela multiplicidade;
  - a parte da exploração no efeito: a mesma conta com `w` sem a exploração (`a` só), para separar quanto do efeito vem do inato
    repetido e quanto da exploração somada k vezes.
- **A pista da literatura para a HA:** Dulberg et al. 2023 (PNAS, `10.1073/pnas.2221180120`), lido no texto completo no vault
  (vault DigiLab Research, `20 Temas/Pet vivo.md`, seção 4). **Pista, a verificar no repositório:** ele não está em nenhum CSV. Pelo que a nota registra,
  um subagente por necessidade escolhe pela ação de maior valor (argmax, e não sorteio), e a vantagem modular aparece já com 4 objetivos
  estacionários. Ele não mede o número de alvos do Digilab, e a A-2 não depende dele: ele só é o motivo para a `P¹` ser a referência
  certa, um alvo por comportamento;
- **Uma segunda referência, só descritiva:** `P^μ`, com a média dos `w` de cada comportamento no lugar do máximo.
- **A troca instantânea:** a chance de sair da intenção em curso, `1 − P(unidade da intenção)`, sob P e sob P¹ (no nível do
  comportamento). Ela não é a medida das trocas de meta da R§13.4, só a chance por decisão.
- **O tempo em cada comportamento:** a fração observada (a escolha) ao lado de `E[P_b]` e de `E[P¹_b]`. Ela responde se o `explorar` em
  cerca de 29 % do tempo (a conta do levantamento, vault DigiLab Research, `DigiLab — Revisão de escopo/LEVANTAMENTO_CEREBRO_MODULAR_2026-11-07.md`, seção 1.4) cai sob P¹.

### 4.3 A-3: o reflexo do sono

- a fração das decisões com o reflexo, por vida e por hora do dia;
- dos `dormir` escolhidos, quantos vêm do reflexo e quantos do sorteio;
- nas decisões com sorteio, a `P_dormir` média;
- **a margem do reflexo:** a leitura da energia menos o `lambda_sono` nas decisões perto do corte (a menos de S/16), para ver quantas
  decisões o reflexo decide por pouco;
- **A nota do vault** (vault DigiLab Research, `20 Temas/Pet vivo.md`, seção 2): o reflexo passa por cima de tudo, e o dormir dá r = 0. Conferido na
  `main` (`f3f717e0`): em `Arbitragem.escolher`, o ramo `elif reflexo` escolhe o `dormir` antes do sorteio e sem sonda, e o `lambda_sono`
  é S/4 (`ConfigDigibrainInatos`, PROPOSTO). O r = 0 do dormir é da nota, lido em outro commit. **O PR do código o confere** pelo canal
  do `r` nas consequências do `dormir` (o mesmo da tabela do alívio, 4.4) e registra o que achar. Duas consequências para a leitura:
  - o reflexo não passa pelo `w`, então as sondas não o veem, e a A-1 subestima o corpo se ele ficar de fora. Por isso a A-3 sai antes
    da regra de leitura (seção 5);
  - se o dormir dá r = 0, o hábito e o P1 nunca aprendem o dormir pelo corpo, e o conflito entre a fome e o sono fica só com o
    reflexo. A nota marca isso como HIPÓTESE. A auditoria só o descreve: a fração das decisões com o reflexo e a fome urgente (u_fome
    ≥ S/2) ao mesmo tempo;
- **a parte do sono que o corpo decide:** o reflexo é o corpo (a energia) decidindo sem sorteio. Ele entra na A-4 como uma porta própria,
  e não fica escondido no `dormir`.

### 4.4 A-4: a sensibilidade da escolha ao corpo (o contrafactual fora da vida)

**O contrafactual** (PV-0-6):
- Em cada decisão da subamostra (PV-0-5), para cada receptor r presente, a falta de r vira `falta_r + Δ` e `falta_r − Δ`, com o corte em
  [0, S] e Δ = S/4. As outras faltas, o mundo, a memória e o estado do cérebro ficam os da decisão.
- **Tudo o que sai da falta é refeito:** a urgência de r, o `g_exp` (pelo `max u` e pelo tédio), o `z`, o inato, o hábito (`H·z`), o
  incentivo do P1 (pela `pc`), o reflexo (se r é a energia) e o `w`.
- **A conta é pura, sobre cópias:** nenhuma chamada da rng, nenhuma atualização da habituação, do afeto (V, E e a série E), do estado
  ou da plasticidade. O G1 com o contrafactual ligado confere isso (seção 2.3).
- **A forma** (o PR do código decide, dentro destas regras): uma função de leitura que recebe as entradas da decisão e devolve as
  unidades refeitas, sem mudar o `Impulso` nem o `Arbitragem`. Se for preciso mudar um módulo do cérebro para expor a conta, a mudança
  entra atrás de chave desligada, com o gabarito, e vira desvio.

**As medidas:**
- **S_r**, a sensibilidade ao receptor r: `TV(P^{r+}, P^{r−})` por decisão, a média por vida, com o reflexo contando como `P_dormir = 1`;
- **ΔP_{b,r}** = `P^{r+}_b − P^{r−}_b`, a matriz de 7 comportamentos × 11 receptores, a média por vida: para onde o receptor empurra;
- **a coerência C_r:** a parte da massa movida que vai para os comportamentos que aliviam r,
  `C_r = Σ_k Σ_{b ∈ A_r} max(0, ΔP_{b,r}) / Σ_k TV_k`, com A_r da tabela do alívio;
- **as portas:** a mesma conta com uma porta só ligada de cada vez (o `z`, o `g_exp`, o incentivo ou o reflexo). Ela separa por onde o
  corpo chega;
- **a entropia** `H(P)` média, em bits, só descritiva: um pet que só reage (H perto de 0) não é o "vivo" que a rodada procura.

**A tabela do alívio A_r** (PV-0-7):
- é empírica, das mesmas vidas, e fica fixada antes da A-4;
- para cada comportamento b e receptor r, o canal de r no `r` das consequências de b (`canais_do_sinal`, o `r` por drive do M-AFETO);
- b alivia r se a média do canal é > 0 e o IC95 (sobre as vidas) fica acima de 0;
- **a limitação, escrita antes:** o alívio empírico mistura o contexto (o `comer` só acontece com comida). Ele diz o que o comportamento
  fez no corpo nessas vidas, e não o que faria em qualquer contexto;
- **a posta sorteada** (seção 3) também entra no alívio empírico: o `comer` alivia a fome onde a ração está, e a ração está onde o dono
  a pôs. O alívio sai por lugar, como o resto;
- o susto fica fora, como no `r` (`fora_do_r`). Um receptor sem nenhum comportamento que o alivie fica sem C_r, e isso é contado.

## 5. A regra de leitura, escrita antes (PV-0-8)

Os cortes são PROPOSTOS e SEM FONTE. Cada hipótese é lida por (fonte, braço), com a média das vidas e o IC95 de A-4 (seção 3).

| hipótese | aponta se | o número que a sustenta |
|---|---|---|
| **HA, o número de alvos** | a mediana de `TV(P, P¹)` é ≥ 0,10 **e** o comportamento com mais unidades (o `explorar` ou o `comer`) tem ρ ≥ 1,25 | a A-2 |
| **HC, o sinal do corpo fraco** | em pelo menos 6 dos receptores com A_r não vazia, o ΔP do alívio, `Σ_{b ∈ A_r} ΔP_{b,r}`, fica abaixo de 0,05 (o limite de cima do IC95 abaixo de 0,05) **e** a parte do corpo no inato da escolhida é < 1/3 na mediana | a A-4 e a A-1 |
| **HP, os pesos inadequados** | a sensibilidade existe (a mediana de S_r ≥ 0,05 em pelo menos 6 receptores) **mas** a coerência fica < 1/2 em pelo menos metade deles, **ou** nas decisões com a urgência de r ≥ S/2 e o comportamento de alívio perdendo, a vantagem da vencedora vem sobretudo do viés e do contexto (mais da metade da diferença de `w`) | a A-4 e a A-1 |

**Como as hipóteses se combinam:**
- **HC e HP se excluem pela construção:** a HC pede a sensibilidade baixa, e a HP pede a sensibilidade presente. Se as duas condições
  passarem em receptores diferentes, o relato registra por receptor, sem escolher uma.
- **A HA é independente das outras:** ela pode valer junto com a HC ou com a HP.
- **Nenhuma aponta:** "indeterminado", com as partes registradas.
- **Duas ou mais apontam:** mistura, registrada sem escolher, como na regra de A11.5.
- **O reflexo (A-3)** não é uma hipótese. Ele entra como contexto. Se ele decide mais de 1/3 das decisões, o relato diz isso antes da
  leitura, porque a escolha que as três hipóteses discutem fica com menos de 2/3 do tempo.

**O que cada leitura sugere para a etapa 1** (vault DigiLab Research, `20 Temas/Pet vivo.md`, seção 5; a escolha é do Matheus):

| a leitura | o que a auditoria sugere testar primeiro |
|---|---|
| HA | normalizar o sorteio por comportamento: sortear o comportamento antes do alvo, ou o posto do Dill 2015 (pista, a verificar). É o conserto mais barato. A escolha por argmax entre subagentes do Dulberg et al. 2023 (pista, a verificar) é a alternativa maior |
| HC | o corpo como modulador (a frente 2 da rodada: a tabela de receptores químico → parâmetro e os dois estados persistentes; Flavell et al. 2013, pista, a verificar), ou a curva da urgência |
| HP | a revisão dos pesos inatos. **Ela esbarra na regra "calibração no fim"**, e quem decide se ela abre agora é o Matheus |
| indeterminado | a auditoria não escolhe a frente. A recomendação da rodada (PV-2 primeiro) fica como está |

**A comparação entre as fontes** (C4 e AN0) e entre os braços (REL e SEM) sai lado a lado, sem teste entre elas. Uma leitura igual nas
duas fontes diz que a regra aponta para o mesmo lugar no código de antes e no de hoje. Ela não diz que o mecanismo é o mesmo.

## 6. O que a 0b não decide

- **Nenhuma causa fica provada.** As vidas são da C4 e da AN0, já lidas, e as hipóteses foram escritas depois disso. **A leitura é
  descritiva e gera hipótese.**
- **O contrafactual não é uma vida.** Ele mede a escolha de uma decisão com o corpo mudado. Ele não mede o que o pet teria feito na vida
  inteira, porque o corpo, o mundo e o aprendizado teriam seguido outro caminho.
- **Nada muda no jogo nem no cérebro padrão.**
- **Nenhum número vira parâmetro.** Os cortes da seção 5 e o Δ continuam PROPOSTOS.

## 7. A medida de "age pelo estado" (0c)

### 7.1 As candidatas (PV-0-9)

| | a medida | a conta | o que ela pega | o que ela não pega |
|---|---|---|---|---|
| **SE-C** (a recomendada) | **a sensibilidade ao estado com a coerência** | por vida: a média, sobre os receptores com A_r não vazia, de `S_r · C_r`, a massa movida para o alívio quando r muda de `falta − Δ` para `falta + Δ` (seção 4.4). Sai também por receptor | o corpo que chega à escolha **e** na direção do alívio | o efeito na vida inteira (é por decisão); a escolha que alivia por outro caminho que a tabela não vê |
| **RV** (parte da SE-C) | **a revalorização no ato**, pela pista do Zhang et al. 2009 (PLoS Comput Biol 5(7):e1000437, `10.1371/journal.pcbi.1000437`; pista, a verificar na `v3c5`): a necessidade muda o "querer" da deixa sem reaprender | nas decisões com comida à vista, `P^{fome+}_comer − P^{fome−}_comer`, com a plasticidade parada (o contrafactual não aprende, por construção) | a revalorização sem aprendizado, que a C4 e o J5 já tocaram por outro caminho | as outras necessidades. Uma versão por par (receptor, comportamento) seria a SE-C de novo |
| a informação mútua (só descritiva) | `I(comportamento; urgência mais alta)`, das escolhas observadas, sem contrafactual | sai de qualquer log, também no jogo | a associação entre o estado e a ação | confunde o estado com o contexto (com fome, há comida perto porque o dono põe), então não serve de gate |

**O teste de desvalorização da revisão I** (vault DigiLab Research, `DigiLab — Revisão de escopo/REVISAO_I_PET_VIVO_2026-11-07.md`) (trocar a comida por uma que não alivia e contar as escolhas depois) pede vidas novas e fica
para os planos da etapa 2. A RV é a versão dele que cabe nos logs: ela muda a necessidade, e não o valor da comida.

**A SE-C não pode subir só por deixar o pet um autômato.** Um ganho na urgência ou um ε menor aumentam a SE-C e zeram a entropia. Por
isso, a entropia `H(P)` sai ao lado, e a guarda de forrageio entra no gate (7.4).

### 7.2 Onde a conta mora

- As contas por decisão (`P`, `P¹`, a TV, ρ, `S_r`, `C_r`, a RV, a entropia) e as médias por vida vão para o `digilab/metrics.py`, uma vez
  só, cada uma com teste contra um caso feito à mão.
- O contrafactual (a seção 4.4) não é métrica: é a leitura do cérebro. Ele fica numa função de leitura do script ou do pacote, conforme o
  PR do código.
- O replay e a contagem ficam no script da seção 9.

### 7.3 A ligação com a INDIVIDUALIDADE (o I2) (PV-0-11)

- **Os dois eixos:** o I2 (`docs/PLANO_ANALISE_V3_INDIVIDUALIDADE.md`, APROVADO; faixa 85101…85505) mede se os pets ficam **diferentes
  entre si** de um jeito que se repete (o R_pet, o ICC). A SE-C mede se **cada pet** escolhe pelo que sente. São dois eixos:
  - um pet pode ser repetível e cego ao corpo (um viés fixo);
  - outro pode ser sensível ao corpo e igual a todos (o mesmo reflexo).

  O "pet vivo" da rodada pede os dois.
- **O I2 é a linha de base do "antes" da individualidade, e a 0b é a do "antes" da SE-C.** As duas valem para o cérebro de hoje, antes de
  qualquer mecanismo da etapa 2.
- **O cruzamento, sem mexer nos arquivos do I2:** o I2 já grava o log de cada vida (o plano dele, seção 5). Depois da run do I2 e do
  merge da medida no `metrics.py`, a SE-C pode ser calculada por replay nesses logs, no `comedouro`, com os quatro donos. Esse
  cruzamento é um adendo deste plano, depois da run do I2. Ele não muda nada da run do I2.
- **O pedido à frente da INDIVIDUALIDADE** vai pelo corpo do PR e por uma nota na pasta de notas das sessões. São duas coisas:
  - guardar os logs do I2 como estão;
  - avisar se o I2a mudar a forma do `motivo` gravado.

### 7.4 Como a medida vira gate na etapa 2 (PV-0-10)

Cada plano de mecanismo da etapa 2 traz, escritos antes da run:
- **G-ESTADO (o gate novo):** o braço do mecanismo menos o controle na SE-C, por unidade, com o IC95. O mecanismo passa se o limite de
  baixo fica acima de uma margem δ_E. **δ_E não se decide aqui.** Ele sai do σ da SE-C por unidade que a 0b medir, no plano de cada
  mecanismo, como o δ da C4 saiu do piloto.
- **G-FORR (a guarda de forrageio):** a taxa de fechamento por episódio de fome do braço não fica pior que a do controle por mais que uma
  margem, como a guarda do comedouro do AN4. Um mecanismo que deixa o pet mais "reativo" e com mais fome não passa.
- **A entropia, só descritiva:** a `H(P)` do braço ao lado da do controle. Uma queda grande vai ao relato como sinal de autômato, sem gate.
- **Os gates de forrageio de cada mecanismo** (a quimiotaxia do PV-2, por exemplo) seguem como estão. A SE-C entra **ao lado**, e não no
  lugar.
- **A medida é implementada uma vez,** antes da primeira run da etapa 2, com o teste contra a 0b: os números da SE-C da 0b saem iguais
  quando a função do `metrics.py` roda nos mesmos dados.

## 8. O tamanho e o custo (PV-0-5)

- **A-1 a A-3:** saem do `motivo` e do `z` no replay, nas 4 800 vidas da C4 (cerca de 6,5 milhões de decisões, 14 dias × 96 por dia) e
  na AN0.
- **A-4, o contrafactual:** cerca de 22 refeitas da ativação por decisão (11 receptores × 2 sentidos), mais as portas. Por isso ele roda
  numa **subamostra fixada antes**: os k de 0 a 7 de cada base (8 × 5 = 40 unidades), nas 12 células e nos dois braços, isto é,
  **960 vidas**, mais toda a AN0.
- **O custo é estimado e SEM MEDIDA.** Na D-C1-3, o replay custou cerca de metade do CPU da vida. A C4 gastou 3,15 s de CPU por vida.
  - Para as 4 800 vidas sem o contrafactual: de 1 a 2 h de parede com 4 processos.
  - Para o contrafactual: um múltiplo desconhecido.
  - **A regra:** o PR do código mede o tempo de 2 vidas das sementes dos testes (uma fumaça, sem leitura). O tempo medido vai declarado no
    relato. Se a projeção para as 960 vidas passar de umas 8 h com 4 processos (o corte que veio junto com a aprovação), o PR propõe
    uma subamostra menor num adendo, **antes** do replay, nunca depois.
- **A máquina (V3-D8):** no máximo 4 processos, e o replay conta como a run de pesquisa do momento.

## 9. O que falta antes do replay (o PR do código, depois do APROVADO)

- **As funções do `digilab/metrics.py`** (seção 7.2), com o teste delas em `tests/test_metrics_pet_vivo.py` (nome PROPOSTO), cada uma
  contra um caso feito à mão:
  - P, P¹, a TV e ρ num caso de 3 comportamentos com 1, 2 e 3 unidades;
  - S_r e C_r num cérebro de brinquedo com uma coluna de W0 só;
  - a RV com a fome mudada;
  - a SE-C de um cérebro sem nenhuma coluna de corpo, que tem de dar 0.
- **O script** `experiments/auditoria_pet_vivo.py` (nome PROPOSTO): ele lê as fontes, faz as conferências da seção 2.3 e refaz as vidas
  (a C4 na worktree do `a287ba2`, a AN0 na `main`). Ele grava `artifacts_v3_pet_vivo/auditoria/auditoria.json`, com os sha256 das
  fontes e do código, e reusa o `descritivo_dc13_rel.py` por import, sem mudá-lo.
- **O teste do script**, nas sementes dos testes:
  - a soma das partes fecha;
  - P soma 1 em toda decisão;
  - o G1 com e sem o contrafactual sai igual;
  - duas execuções saem iguais, byte a byte;
  - o script falha alto com o código ou a fonte errados.
- **O modelo recomendado:** o Sonnet, para a implementação com escopo claro. Para o contrafactual, se ele pedir mexer num módulo do
  cérebro, escalar para o Opus.
- **O relato:** um `docs/RESULTADO_V3_PET_VIVO.md` novo, com a seção da 0b. A linha da regra da seção 5 vai também no corpo do PR.
- **Roda uma vez.** Nada se ajusta olhando o resultado. Uma regra diferente entra por adendo, antes do replay.

**O código não entra neste PR.** Este PR é só de documentos.

## 10. O que fica de fora

- **Vida nova, semente nova e faixa:** nenhuma.
- **Os mecanismos:** os PV-1 a PV-5, a normalização do sorteio e o corpo como modulador são da etapa 2.
- **Os outros braços da C4:** o REC, o EMB, o RELsN e o REL+F. As facetas deram ≈ 0 (C4, 16.3), e a relevância já foi respondida.
- **O cérebro A:** nenhum braço do A está nessas vidas.
- **O AN4:** o passeio muda as unidades do `explorar`.
- **O teste de desvalorização com vida nova:** é da etapa 2 (7.1).
- **A fala** (as unidades de fala da DC3): elas mudam o número de unidades do `chamar_atencao`. Ficam para um adendo, se a HA apontar.
- **A verificação das referências:** é a 0a, a tabela `v3c5`. Toda referência nova deste plano (Zhang et al. 2009, Dill 2015, Flavell
  et al. 2013 e Dulberg et al. 2023) fica como **pista, a verificar**, até entrar numa tabela do repositório. Luce 1977 e Usher e McClelland 2001 são as da espec, com o estado que a espec
  registra.
