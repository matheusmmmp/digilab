# Espec V3: as necessidades num conjunto (prioridade e escalonamento entre urgências)

**Status:** PROPOSTO, **não aprovado.** Só papel: nenhuma linha de código, teste ou vida sai antes de o Matheus escrever "APROVADO" neste
cabeçalho. Todo número novo é PROPOSTO, SEM FONTE, e a calibração fica para a rodada de equilíbrio no fim (`CLAUDE.md`, "Números novos são
PROPOSTOS"; o prompt das cinco frentes, regras comuns).

- **A frente:** F3 das cinco frentes da síntese de 2026-11-16 (o prompt está no vault, `30 Decisões e protocolo/PROMPT_CINCO_FRENTES_2026-11-16`).
- **O levantamento:** no vault, `DigiLab — Revisão de escopo/LEVANTAMENTO_URGENCIAS_PRIORIDADE_2026-11-17` (as fontes, cada DOI conferido no
  Crossref; Keramati e Gutkin no texto completo).
- **O commit da `main` lido:** `a794c3ae` (2026-11-16, o merge do PR #951). As referências `arquivo:linha` abaixo são desse commit.
- **Executor:** Claude Code (Opus 5.5), sessão da F3, worktree `D:\Trab\digilab\v3-urgencias`, branch `v3-urgencias`.

## 0. Em uma página

**A pergunta do Matheus:** cada urgência é calculada sozinha, mas o pet só faz uma ação. Então tem de haver uma ordem de prioridade, um
escalonamento e uma parametrização entre as urgências.

**O que o código faz hoje** (seção 1): cada urgência sai sozinha, e a prioridade fica **implícita**, nos sinais do W0 escritos à mão, no H
aprendido e no peso do sorteio. Por cima disso há **três guardas lexicográficas feitas caso a caso** no M-ARB. O sinal do corpo é uma soma
de quadrados: o ganho de comer não depende da energia nem de nenhuma outra falta.

**O que a literatura dá** (o levantamento):
- a forma da interação: o impulso de Keramati e Gutkin (2014), `D = (Σ |δ|^n)^(1/m)` com `n > m > 1`. A raiz faz a falta de uma necessidade
  **inibir** o valor de satisfazer outra (a eq. 8 do artigo), e o DigiLab hoje é o caso `n = 2, m = 1`, sem a raiz;
- o custo da comutação rígida: o Tyrrell (1993) defende a hierarquia de fluxo livre, que deixa ganhar o candidato de compromisso;
  Spier e McFarland (1997) acham oscilação nos mecanismos de custo;
- a pirâmide de Maslow não serve de mecanismo, e a ordem estrita não aparece no dado de Tay e Diener (2011).

**Os quatro desenhos** (seção 4) diferem **no lugar onde a interação entra:**

| | onde | o que muda | fonte da forma |
|---|---|---|---|
| (a) | no r e no incentivo | `D` com raiz, `n = 4, m = 2` | Keramati e Gutkin, eq. 1 |
| (b) | no M-ARB | escalonamento lexicográfico acima de um limiar, com um peso de prioridade por necessidade | SEM FONTE (jogo); a crítica do Tyrrell vale contra |
| (c) | no H | nada novo no cérebro: a prioridade aprendida, medida | — |
| (d) | nas urgências, no lado da decisão | a falta normalizada pelas outras, antes da curva | o gradiente da eq. 1; a forma em animais é HIPÓTESE |

**A previsão** (seção 2) foi escrita antes de qualquer código: num cenário de duas necessidades altas (fome e energia, com ração à vista),
cada desenho muda o peso do `comer` de um jeito diferente, e a coluna "sem desfecho aprendido" separa (a) de (d).

**A sonda nova** (seção 3): "quem decidiu entre as necessidades", uma por necessidade, com o mesmo `u` e sem rng nova. Ela vale também para o
cérebro de hoje.

**A recomendação** (seção 8): medir antes. Primeiro a sonda por necessidade e os testes de mecanismo da previsão, sem mudar o comportamento.
Depois, (a) e (d) atrás de chave, com o de hoje como linha de base e (b) só como braço de contraste.

## 1. Como a prioridade funciona hoje

Lido no código; nada foi executado.

**1.1 A urgência, uma por necessidade (M-AFETO).**
- `urg = {r: self.urgencia(f) for r, f in falta.items()}` (`digilab/digibrain/afeto.py:107`); no TS, `web/app/motor/digibrain/afeto.ts:88`.
- A curva é a mesma nos onze receptores: `u = clamp(mul(a, f) + mul(b, max(0, f − λ)), 0, S)` (`afeto.py:95-97`). Os valores são a = S/2,
  b = 3S/2 e λ = S/2, PROPOSTO, SEM FONTE (`digilab/config.py:2921-2923`). No jogo (v38, v39), λ = 640, DECIDIDO pela rodada do cuidado
  (`config.py:3190`, 3194).
- A única leitura cruzada no afeto é o ganho da exploração, que cai com a maior urgência: `max(urg.values())` (`afeto.py:121`).

**1.2 As urgências em todos os comportamentos (M-IMPULSO).**
- O contexto z leva as onze urgências, mais as conjunções `fome_sem_comida` e `cuidado_humor` (`impulso.py:104-114`).
- O inato de cada comportamento é `Σ_j W0[b,j]·z_j` (`impulso.py:173`), e o hábito é `Σ_j H[b,j]·z_j` (`impulso.py:186`; `plast.py:84`).
- **Os sinais do W0 são a prioridade de hoje** (`config.py:2936-2946`):
  - o `dormir` lê `u_energia` (+3S) e `u_fome` (−S): a fome freia o sono;
  - o `brincar` lê `u_fome` e `u_energia` (−S/2 cada); o `explorar` lê `u_energia` (−2S);
  - o `comer` só lê `u_fome` (+3S). **A energia não freia o comer.**

  A interação existe, mas é assimétrica e escolhida linha a linha.

**1.3 O sorteio e as três guardas (M-ARB).**
- O sorteio é proporcional ao peso `w = a + mul(g_exp, ε)` (`arb.py:84-86`, 42-53), com uma chamada da rng de política por decisão com dois
  candidatos ou mais (`arb.py:146-153`).
- As três guardas ficam acima dele:
  1. **o reflexo do sono:** a leitura da energia abaixo de `λ_sono` = S/4, dorme sem sorteio (`arb.py:109-110`, 142-145);
  2. **o sono que segura:** dormindo e com a energia abaixo de `λ_acordar`, segue dormindo, salvo com a fome urgente (`arb.py:111-115`);
  3. **a guarda do brincar:** com a fome urgente, o peso do brincar vai a 0 (`arb.py:117-120`, 134-135; montada em `digibrain/adapt.py:340-345`).
- **É uma ordem lexicográfica de fato:** a energia muito baixa vence tudo, e a fome urgente (a urgência da fome acima do `urgencia_lambda`)
  vence o sono que segura e o brincar.

**1.4 O sinal do corpo, somado.**
- `sinal_corpo` = `div_arred(ganho · (D(antes) − D(depois)), S)`, com `D = Σ_d w_d · f_d²` (`digilab/policies/lobos.py:2899-2909`, pelas
  `contribuicoes_corpo`, 2842-2862). O M-AFETO usa esse r na consequência (`afeto.py:139`), e o incentivo usa a mesma conta no futuro
  previsto, o `valor_previsto` (`lobos.py:2887-2896`, chamado em `plast.py:81`).
- Na notação de Keramati e Gutkin, é **n = 2, m = 1.** O `docs/PLANO_ANALISE_V2_N3.md:41` já dizia que tirar a raiz foi "escolha do projeto,
  para ficar em inteiros sem raiz".
- **A consequência:** a parte de cada drive, `w_d · (f_antes² − f_depois²)`, não lê as outras. A convexidade existe (comer vale mais com mais
  fome); a interação, não.
- **Uma interação indireta, só no r:** o corpo paga o andar até a comida, e esse custo em r cresce com a falta de energia. O incentivo não
  vê isso: o desfecho previsto tira o andar da energia (`plast.py:111-115`), e o `incentivo` usa só o desfecho da classe (`plast.py:75-82`).

## 2. A previsão (escrita antes de qualquer código)

**2.1 O cenário C-UR,** uma decisão montada à mão, sem vida e sem sementes (um teste de mecanismo, como os da seção 10 da
`docs/ESPEC_DIGIBRAIN_MODULAR.md`):
- o pet acordado, de dia, sem intenção em curso (C = 0, sem persistência), F = 0, V = E = 0, sem memória recuperada, sem bola;
- o corpo com todas as faltas em 0, salvo a da fome `f_F` e a da energia `f_E`;
- uma ração à vista, com a proximidade `p` fixa;
- a leitura da energia acima de `λ_sono` (`f_E ≤ 3S/4`), para o reflexo não disparar;
- a grade, PROPOSTA: `f_F, f_E ∈ {0, S/4, S/2, 5S/8, 3S/4}`;
- duas condições do desfecho aprendido: **sem desfecho** (`d̂ = 0`: o P1 desligado, ou antes da primeira refeição) e **com desfecho**
  (`d̂[ração, fome]` fixo e positivo, o resto 0; o valor é PROPOSTO no teste);
- os inatos de hoje, sem calibrar nada.

**2.2 O que se mede**, sem sorteio: os pesos `w` do M-ARB e a probabilidade exata de cada unidade, `π_x = w[x] / Σ w` (o sorteio é
proporcional, então π sai da conta). As medidas são `w[comer, ração]`, `w[dormir]` e `π_comer`.

**2.3 A previsão por desenho** (cada linha é falsificável por um teste de uma decisão):

| desenho | `f_E = 0` (uma necessidade só) | `f_E` alto, sem desfecho | `f_E` alto, com desfecho |
|---|---|---|---|
| hoje | a referência | `w[comer]` igual ao de `f_E = 0`; `π_comer` cai só porque `w[dormir]` sobe | igual: `w[comer]` não lê `f_E` |
| (a) | **igual a hoje, bit a bit** | **igual a hoje** (o incentivo é 0 sem desfecho) | `w[comer]` **menor** que com `f_E = 0` |
| (b) | **diferente de hoje** sempre que a fome passa do limiar: só as unidades que servem à fome ficam | com as duas acima do limiar, só as da dominante ficam: `π_dormir = 0` ou `π_comer = 0`, um salto | o mesmo |
| (c) | igual a hoje ao nascer (H = 0) | igual a hoje ao nascer | igual a hoje ao nascer; muda só com a idade |
| (d) | **igual a hoje, bit a bit** | `w[comer]` **menor**; `w[dormir]` sobe **menos** que hoje | `w[comer]` menor |

**Por que** (a conta de cada desenho está na seção 4):
- (a) e (d) são a identidade com uma necessidade só, porque `√(f⁴) = f²` e `f³ / f² = f` em inteiros exatos;
- a coluna "sem desfecho" **separa (a) de (d)**: em (a) a interação entra pelo incentivo, que é 0 sem desfecho; em (d) ela entra pela
  urgência, que está no inato;
- (b) é o único que muda o pet com uma necessidade só;
- em (c) nada muda na decisão; a previsão é sobre o hábito (2.4).

**2.4 A previsão do hábito (desenho c), em vidas:** HIPÓTESE de que o hebbiano **não** aprende a prioridade do sono sobre a comida. O passo
credita todas as características ativas no começo da opção (`e_j = z_j`, `plast.py:17`). Se as refeições de um pet cansado ainda dão r
positivo, `H[comer, u_energia]` **sobe**, e o pet aprende a comer cansado.
- **Falsifica:** `H[comer, u_energia]` com média negativa nas vidas da bancada.
- Esta parte pede vidas, e por isso só roda com um plano de análise e uma faixa reservados (D-UR-9).

**2.5 O que falsifica cada desenho** (o teste falha se):
- (a): `w[comer]` muda com `f_E` sem desfecho, ou não cai com desfecho. Com uma ressalva: o incentivo tem teto (`g_max_incentivo`,
  `plast.py:82`), e com o incentivo no teto nos dois casos a diferença some. O teste escolhe um `d̂` que deixe o incentivo abaixo do teto.
- (b): `π_dormir > 0` com a fome dominante acima do limiar, ou `π` contínuo ao cruzar o limiar.
- (c): uma decisão de pet recém-nascido diferente da de hoje.
- (d): qualquer diferença com `f_E = 0`, ou `w[comer]` que não cai com `f_E` sem desfecho.

## 3. A sonda nova: "quem decidiu entre as necessidades"

**A regra, a mesma das sondas do M-ARB** (`arb.py:154-168`): refazer a decisão com uma parte zerada, sortear com **o mesmo `u`**, e dizer que
a parte decidiu se a escolha muda. Só leitura: não mexe em peso, motivo nem rng. No reflexo e na escolha segurada, nenhuma sonda decide
(como hoje, `arb.py:156-159`).

**3.1 Uma sonda por necessidade, válida para o cérebro de hoje e para todos os desenhos.**
- Para cada necessidade r com `u_r > 0`, a contribuição dela em cada unidade é
  `c_r = mul(W0[b, u_r], u_r) + mul(H[b, u_r], u_r)` mais os termos das conjunções que a usam (`fome_sem_comida` para a fome, `cuidado_humor`
  para o humor).
- A sonda `sem_urgencia_<r>` tira `c_r` da soma de cada unidade, antes do `φ` (como as sondas de hoje tiram um termo,
  `arb.py:160-161`), e sorteia com o mesmo `u`. Grava `urgencia_decidiu[r]`.
- O `g_exp` fica o da decisão (PROPOSTO): a sonda isola o canal do z e não o ganho da exploração.
- **Isso também serve à fala.** A espec do modular já pede, para "fiz Y porque estava com fome", a urgência da fome entre os termos que,
  zerados, mudariam a escolha (`docs/ESPEC_DIGIBRAIN_MODULAR.md`, seção 7). Hoje essa sonda não existe (nenhum `sem_urgencia` no código).

**3.2 Uma sonda por desenho**, `sem_prioridade`, com `prioridade_decidiu`:
- em (a) e (d), a unidade guarda um termo novo, `prioridade` = (a soma com o desenho) − (a soma de hoje). A sonda tira esse termo, como as
  outras;
- em (b), a sonda refaz os pesos sem o filtro do escalonamento;
- em (c), não há sonda nova: a `sem_habito` de hoje já mede o H.

**3.3 O custo:** até onze refeitas a mais por decisão, só nas necessidades com `u_r > 0`. São somas e subtrações de termos já calculados, sem
rng.

**3.4 O registro:** o `motivo` ganha `sondas.urgencia_decidiu` (um booleano por necessidade) e, com um desenho ligado, `sondas.sem_prioridade`
e `sondas.prioridade_decidiu`. O registro é derivado e nunca vai ao log, que não muda. A divisão Python × TS do registro detalhado (os `c_r`
por unidade) é a D-UR-6.

## 4. Os quatro desenhos

**O que vale para todos:**
- cada um entra atrás de uma subchave da `ConfigDigibrain`, PROPOSTA: `urgencias` ∈ {`"hoje"`, `"kg"`, `"escalonamento"`, `"normalizada"`},
  com `"hoje"` como padrão;
- desligado, a vida de hoje sai byte a byte, conferida por um gabarito gravado num commit próprio antes da mudança (`CLAUDE.md`);
- a referência fica no Python (`digilab/digibrain/`), e o espelho TS em `web/app/motor/digibrain/` sai com o G-PAR;
- **as três guardas de hoje ficam como estão** e leem a urgência crua (D-UR-5);
- **nada muda no `lobos.py`** (seção 6.1);
- **ligar um desenho no jogo** pede uma versão nova de pet, porque muda as decisões. Isso só acontece depois da comparação.

### 4.1 (a) O impulso de Keramati e Gutkin com raiz

**A forma.** `D = (Σ_d f_d^n)^(1/m)`, com (n, m) = (4, 2), PROPOSTO, SEM FONTE de valor (o artigo dá só `n > m > 1`). Em inteiros:
- `D_kg = raiz_inteira(Σ_d (f_d · f_d)²)`, sobre os mesmos drives do r de hoje (sem o susto, `afeto.py:133-134`), com `raiz_inteira`, a raiz
  inteira exata que o projeto já tem (`digilab/modelo_mundo.py`);
- com uma necessidade só, `D_kg = f²`, o mesmo D de hoje, bit a bit;
- o maior valor é 11 · 2⁴⁰ ≈ 1,2 · 10¹³, abaixo de 2⁵³: cabe exato num `number` do TS, sem `BigInt` (conferir no teste de paridade);
- `r_kg = div_arred(ganho · (D_kg(antes) − D_kg(depois)), S)`, com o mesmo `ganho_r` e o mesmo `r_norm` de hoje.

**Onde entra:**
- **no r** (o M-AFETO, `consequencia`, `afeto.py:139`): o `r_kg` no lugar do `sinal_corpo`. Muda V, E e o H, nunca o d̂ (que aprende das
  leituras, não do r);
- **no incentivo** (o M-PLAST, `incentivo`, `plast.py:81`): um `valor_previsto_kg`, o `r_kg` do estado de agora para o previsto;
- **os canais por drive** (o K-6, a soma telescópica igual ao escalar): com a raiz, D não é soma. A regra PROPOSTA troca, na ordem dos drives,
  um drive por vez do antes para o depois, e o canal d é a queda de `D_kg` nessa troca. A soma dos canais é o total, exata.

**O efeito:** o ganho marginal de reduzir a falta j é `2 f_j³ / √(Σ f⁴)`. Ele cai quando outra necessidade está longe do setpoint (a eq. 8
do artigo) e sobe com a própria falta (a eq. 7).

**O código:**
- Python: um módulo novo, `digilab/digibrain/necessidades.py`, com `impulso_kg`, `sinal_kg`, `canais_kg` e `valor_previsto_kg`. Ele lê as
  faltas pelo `falta_receptor` (só importa; não muda nada no `lobos.py`). O `afeto.py` e o `plast.py` escolhem a conta pela subchave;
- TS: o espelho em `web/app/motor/digibrain/necessidades.ts`, com o `afeto.ts` e o `plast.ts`.

**O registro:** o `ultimo` do M-AFETO ganha `r_hoje` ao lado do `r` (para medir a diferença sem rodar duas vidas), e as unidades do comer e
do brincar ganham o termo `prioridade` = (o incentivo com `D_kg`) − (o de hoje).

**O risco:** muda o sinal de aprendizagem de toda a vida, não só a decisão. Todos os gabaritos com a chave ligada mudam, e a comparação em
vidas mistura o efeito na decisão com o efeito no H. A D-UR-4 pergunta se vale um braço "só no incentivo" para separar os dois.

### 4.2 (b) Um peso de prioridade por necessidade, com escalonamento acima de um limiar

**A forma**, PROPOSTA, SEM FONTE:
- uma `ConfigPrioridade` com, por necessidade r, o peso `π_r` e o limiar de escalonamento `Λ_r`;
- uma tabela `SERVE`, PROPOSTA: comportamento → necessidades que ele atende:
  - comer → fome; dormir → energia;
  - chamar o dono → fome, higiene, solidão;
  - brincar → tédio, humor; explorar → tédio, curiosidade;
  - ocioso e emburrar → nenhuma;
- **a regra no M-ARB**, depois dos pesos e antes do sorteio:
  - as escalonadas são `E = {r : u_r > Λ_r}`;
  - se `E` não é vazio, a dominante é `r* = argmax_{r ∈ E} mul(π_r, u_r)`, com o empate pela ordem de `RECEPTORES_DIGIBRAIN`;
  - o peso das unidades que não servem a `r*` vai a 0, como a guarda do brincar (`arb.py:117-120`);
  - se nenhuma unidade que serve a `r*` tem peso positivo, não há filtro, e o registro marca `fora` (como a escolha segurada, `arb.py:138`).

**Uma observação de desenho:** um `π_r` que multiplicasse a urgência no z seria só uma escala da coluna do W0, e não acrescentaria nada.
Por isso o `π_r` aqui só ordena as necessidades **escalonadas**. A parte nova de (b) é o escalonamento.

**O que generaliza:** as três guardas de hoje são casos deste filtro com uma tabela fixa. Pela D-UR-5, elas ficam como estão; uma troca
delas pela tabela seria outro PR, com o gabarito.

**O código:** a `ConfigPrioridade` em `digilab/config.py`, com o status de cada campo; o filtro em `arb.py`, no mesmo lugar da guarda do
brincar e depois da CO7 (como ela, D-EQ2-2); o espelho em `arb.ts` e `constantes.ts`.

**A rng:** o filtro pode deixar um candidato só, e então a decisão não chama a rng. A contagem da rng muda com a chave ligada, como já muda
com a guarda do brincar. É a rng de política, e o mundo não muda.

**O registro:** `prioridade = {escalonadas, dominante, filtradas, fora}`; a sonda `sem_prioridade` sem o filtro.

**O risco** (o levantamento, seção 3): é a comutação rígida que o Tyrrell critica. Perto do limiar, o pet pode oscilar (Spier e McFarland), e
o compromisso some: brincar perto da comida com fome moderada deixa de concorrer. A persistência do M-ESTADO amortece a oscilação, mas não a
tira. **Muda o pet até com uma necessidade só**, o que (a) e (d) não fazem.

### 4.3 (c) A prioridade aprendida no H, sem camada nova

**A forma:** nada muda na decisão. A prioridade é a que o W0 e o H dão. O desenho é **medir**:
- a sonda por necessidade (seção 3.1), no registro;
- o cenário C-UR (seção 2) como teste de uma decisão, que hoje passa a "previsão de hoje";
- em vidas, o sinal e o tamanho dos pesos cruzados, `H[comer, u_energia]`, `H[dormir, u_fome]` e os do brincar (2.4).

**Uma variante, (c2), registrada e não recomendada:** pares `mul(u_r, u_s)` para alguns pares de necessidades no z, com o W0 = 0 neles, para
o H aprender a interação. Ela muda o tamanho de `CARACTERISTICAS_DIGIBRAIN` e do H, e o passo do hábito é pequeno (η_h = S/256,
`config.py:2957`). HIPÓTESE: numa vida, ela quase não aprende; e, pela 2.4, pode aprender o sinal errado.

**O código:** só a sonda (seção 3) e os testes. Nenhuma versão nova de pet, porque as decisões e o log não mudam. Isso se confere na
implementação: se o `motivo` entra em algum hash, a conta muda.

**O risco:** quase nenhum, e é a linha de base dos outros. O custo é não responder à pergunta, só medir.

### 4.4 (d) A normalização divisiva das urgências (o que o levantamento trouxe)

**A ideia:** o gradiente do impulso de (a) posto no lado da decisão. Em vez de o r cair quando outra necessidade está em falta, a
**urgência** cai.
- Com (n, m) = (4, 2), o gradiente é `2 f_j³ / √(Σ f⁴)`.
- Normalizado para a mesma escala da falta: `ν_j = div_arred(f_j³, Q)`, com `Q = raiz_inteira(Σ_i f_i⁴)` (o `D_kg` de (a)), e `ν_j = 0` com
  `Q = 0`.
- A urgência passa a ser a curva de hoje sobre `ν`: `u_j = clamp(mul(a, ν_j) + mul(b, max(0, ν_j − λ)), 0, S)`.

**As propriedades** (álgebra, sem execução):
- com uma necessidade só, `Q = f²` e `ν = f³ / f² = f`: a identidade, bit a bit;
- com duas faltas iguais, `ν ≈ f / √2` nas duas;
- com `f_F > f_E`, a razão `ν_F / ν_E = (f_F / f_E)³`: a maior ganha mais do que hoje, que dá a razão simples. A normalização **aguça** a
  disputa a favor da maior falta e **atenua** as duas quando elas empatam.

**Onde entra:** no M-AFETO, no `ler` (`afeto.py:107`), antes da curva. As urgências normalizadas vão ao z e às conjunções.

**O que fica na falta crua** (PROPOSTO): as três guardas (D-UR-5), o `g_exp` (`afeto.py:121`) e o r (o desenho (d) não muda o aprendizado).

**O conjunto da soma:** os mesmos drives do r (sem o susto), PROPOSTO. A dor e o susto entram como concentração, não como falta
(`lobos.py:2825-2839`); a D-UR-3 cobre a escolha do conjunto.

**O código:** a conta em `necessidades.py` (a mesma `raiz_inteira` de (a)); o `afeto.py` escolhe pela subchave; o espelho em `afeto.ts`.

**O registro:** o `afeto` do `motivo` ganha `urgencias_cruas` ao lado de `urgencias`, e cada unidade ganha o termo `prioridade` = (a soma
com `ν`) − (a soma com a falta crua). O M-IMPULSO calcula as duas, o que dobra a conta do inato e do hábito.

**O sustento:** a forma vem da derivada da eq. 1 de Keramati e Gutkin, feita por nós. O artigo põe a interação no **valor do desfecho**, não
na urgência. O nome "normalização divisiva" é de Carandini e Heeger (2012), `10.1038/nrn3136`, conferido só no título e nos metadados: **não**
sustenta que necessidades se normalizem assim. É HIPÓTESE nossa.

**O risco:** muda todos os comportamentos de uma vez, porque toda urgência está em todo z. Com três necessidades altas, todas caem, e o viés e
o `ε` do sorteio pesam mais. O `ocioso` (que lê −S/4 de quatro urgências) e o `explorar` mudam junto.

## 5. A comparação resumida

| | muda com uma necessidade só? | sem desfecho aprendido | muda o aprendizado? | código novo | custo de errar |
|---|---|---|---|---|---|
| hoje / (c) | — | — | não | só a sonda | baixo: não responde à pergunta |
| (a) | não (identidade) | igual a hoje | sim (o r) | `necessidades.py`, `afeto`, `plast`, TS | todos os gabaritos ligados; a decisão e o aprendizado misturados |
| (b) | **sim** | salto no limiar | não | `ConfigPrioridade`, `arb`, TS | oscilação e perda do compromisso; tabela `SERVE` à mão |
| (d) | não (identidade) | `w[comer]` cai | não | `necessidades.py`, `afeto`, `impulso` (a conta dupla), TS | todos os comportamentos de uma vez |

## 6. As dependências

**6.1 A limpeza e o `lobos.py`.** O `sinal_corpo`, o `contribuicoes_corpo`, o `falta_receptor` e o `valor_previsto` moram hoje no
`digilab/policies/lobos.py`. A LZ2 os leva, sem mudar a conta, para `digilab/digibrain/base.py` (`docs/TAREFA_V3_LIMPEZA.md`, seção 3, LZ2),
e a LZ3 leva o `lobos.ts` para `motor/digibrain/base.ts`.
- **Esta espec não propõe mudança nenhuma no `lobos.py`.** Os desenhos (a) e (d) põem funções **novas** num módulo novo do `digibrain/`, que
  só importa as de hoje.
- **Mesmo assim, depende de combinar com a sessão da limpeza:**
  - o momento: o código desta frente entra depois da LZ2 (e o TS depois da LZ3), para importar do `base.py` e não mover duas vezes;
  - o lugar: se as funções novas devem ficar no `base.py` ao lado das de hoje, ou num módulo próprio. A D-UR-7 pergunta isso.
- **Nada aqui usa o cérebro A** como controle ou fallback. A linha de base de todos os desenhos é o modular de hoje (o desenho c).

**6.2 A F4 (a palavra do dono).** Se a palavra entrar como termo do M-IMPULSO, a regra "o corpo vence" da F4 (urgência acima de λ ignora a
palavra) depende do desenho escolhido aqui:
- com (b), o escalonamento já tira a unidade da palavra quando ela não serve à necessidade dominante;
- com (a), (c) e (d), a palavra não é urgência e não é atenuada: a F4 precisa de uma guarda própria, como as três de hoje.

Isso é a D-UR-8, e uma nota para a F4 ficou na pasta das notas da Gerente.

**6.3 A rodada de equilíbrio.** Os números (n, m, `π_r`, `Λ_r`, a tabela `SERVE`, a grade do C-UR) são PROPOSTO, SEM FONTE. Nenhum entra
calibrado.

## 7. Os números desta espec (todos PROPOSTO, SEM FONTE)

| número | onde | valor PROPOSTO | por quê |
|---|---|---|---|
| (n, m) | (a), (d) | (4, 2) | cumpre `n > m > 1`; cabe em inteiros exatos com a `raiz_inteira`; é a identidade com uma necessidade só |
| `π_r` | (b) | S em todas | neutro: com o empate, a ordem de `RECEPTORES_DIGIBRAIN` decide |
| `Λ_r` | (b) | o `urgencia_lambda` do pet | o mesmo limiar da "fome urgente" das três guardas; nenhum número novo |
| a tabela `SERVE` | (b) | a da seção 4.2 | a leitura dos sinais positivos do W0 |
| a grade de `f_F`, `f_E` | o C-UR | {0, S/4, S/2, 5S/8, 3S/4} | cobre os dois lados do joelho da curva (λ = S/2 e 640) sem o reflexo |
| `d̂[ração, fome]` | o C-UR | um valor do teste, com o incentivo abaixo do teto | só para o teste; não é parâmetro do pet |

## 8. As decisões para o Matheus

Cada uma com a pergunta curta, a recomendação e o custo de errar. A resposta dele entra aqui literal.

- **D-UR-1. Fazer a prioridade explícita agora, ou medir antes?**
  - Recomendação: **medir antes.** O primeiro PR de código é a sonda por necessidade (seção 3.1) e o C-UR como teste de uma decisão, sem mudar
    o comportamento (o desenho c).
  - Custo de errar: pular a medida é escolher um desenho sem saber se o pet de hoje decide mal com duas necessidades. Medir custa um PR pequeno.
  - Resposta:
- **D-UR-2. Quais desenhos entram na comparação?**
  - Recomendação: **(a) e (d)**, atrás de chave, com o de hoje como linha de base. **(b) só como braço de contraste**, não como candidato ao
    jogo. A (c2) não entra.
  - Custo de errar: pôr (b) no jogo arrisca a oscilação e a perda do compromisso que a literatura já descreve. Deixar (a) de fora perde a
    única forma com fonte revisada.
  - Resposta:
- **D-UR-3. (n, m) = (4, 2), e a soma sobre os drives do r (sem o susto)?**
  - Recomendação: **sim, como PROPOSTO, SEM FONTE.** É o par mais simples que cumpre `n > m > 1` e fica exato em inteiros.
  - Custo de errar: outro par, como (3, 2), pede a raiz de um número que não é quadrado em todo passo e perde a identidade exata com uma
    necessidade só. A escolha do conjunto muda a força da interação; a rodada de equilíbrio pode revê-la.
  - Resposta:
- **D-UR-4. No (a), a raiz entra no r e no incentivo juntos, ou também num braço "só no incentivo"?**
  - Recomendação: **juntos**, como no artigo (é um D só). O braço "só no incentivo" fica como opção, se a comparação misturar demais o efeito
    na decisão com o efeito no aprendizado.
  - Custo de errar: juntos, o resultado não diz de onde veio a diferença. Separados, é um braço a mais na run.
  - Resposta:
- **D-UR-5. As três guardas (o reflexo do sono, o sono que segura e a fome no brincar) ficam como estão, lendo a urgência crua, em todos os
  desenhos?**
  - Recomendação: **sim.** Elas estão DECIDIDAS e validadas na rodada do cuidado, e trocá-las pela tabela de (b) seria outro PR.
  - Custo de errar: guardas lendo a urgência normalizada em (d) mudariam quando o pet acorda pela fome, um efeito que a rodada do cuidado já
    mediu e fechou.
  - Resposta:
- **D-UR-6. A sonda por necessidade vai também ao jogo web?**
  - Recomendação: **os booleanos `urgencia_decidiu` nos dois, com paridade; os `c_r` por unidade só no Python.**
  - Custo de errar: no web, o registro detalhado pesa no `motivo` de cada decisão. Sem nada no web, a fala não ganha o "porque estava com fome"
    verificável.
  - Resposta:
- **D-UR-7. O código de (a) e (d) espera a LZ2 (Python) e a LZ3 (TS), e mora num módulo novo do `digibrain/`?**
  - Recomendação: **sim, depois da LZ2 e da LZ3, num `necessidades.py` (e `.ts`) que importa do `base.py`**, combinado com a sessão da limpeza
    antes do PR. Nada no `lobos.py`.
  - Custo de errar: entrar antes faz a limpeza mover código novo junto e arrisca o gabarito da LZ1.
  - Resposta:
- **D-UR-8. A palavra do dono (F4) passa pela prioridade desta frente?**
  - Recomendação: **não.** O "corpo vence" da palavra é uma guarda como as três de hoje, lendo a urgência crua acima do `urgencia_lambda`.
    Ela não depende do desenho escolhido aqui.
  - Custo de errar: amarrar a F4 à F3 faz uma esperar a outra. Se (b) for escolhido depois, a guarda da palavra pode virar uma linha da tabela.
  - Resposta:
- **D-UR-9. A parte em vidas (o hábito da 2.4 e a comparação de (a) e (d)) ganha um plano de análise próprio, ou entra na rodada de
  equilíbrio?**
  - Recomendação: **um plano de análise próprio**, `docs/PLANO_ANALISE_V3_URGENCIAS.md`, depois dos testes de uma decisão, com a faixa
    pedida ao coordenador. Não entra na rodada de equilíbrio, que calibra números e não compara mecanismos.
  - Custo de errar: na rodada de equilíbrio, a escolha do mecanismo e a dos números se misturam.
  - Resposta:

## 9. A literatura

As fontes, o que cada uma afirma e o que ficou sem conferir estão no levantamento do vault. As usadas aqui:
- Keramati e Gutkin (2014), `10.7554/eLife.04811`, VERIFICADA, texto completo: a eq. 1 e a frase da eq. 8 (a privação de outra necessidade
  inibe o valor). O sinal da eq. 8 no XML do Europe PMC contradiz o texto; ao citar, usar a frase;
- Tyrrell (1993), `10.1177/105971239300100401`; McFarland e Sibly (1975), `10.1098/rstb.1975.0009`; Spier e McFarland (1997),
  `10.1006/jtbi.1997.0517`: conferidas no Crossref e lidas pelo resumo;
- Kenrick et al. (2010), `10.1177/1745691610369469`; Tay e Diener (2011), `10.1037/a0023779`: pelo resumo, só para dizer que a ordem estrita
  não serve de mecanismo;
- Carandini e Heeger (2012), `10.1038/nrn3136`: só o título, para o nome da forma de (d).

**Nenhuma alegação de novidade.** O impulso de Keramati e Gutkin num agente artificial já existe (o próprio artigo; o CTCS-HRRL).

## 10. Fora do escopo

- Nenhum código, teste, gabarito ou vida.
- Nenhuma calibração.
- A troca das três guardas por uma tabela.
- O acumulador com inibição mútua da PE-5 (`docs/ESPEC_DIGIBRAIN_MODULAR.md`, seção 4.7), que é outra forma de arbitragem e não de
  prioridade entre necessidades.
