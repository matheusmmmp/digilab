# ESPEC V3 — COOPERACAO, CO6: a reputação e a convivência na percepção (2026-11-11, CO6-1 a CO6-7 DECIDIDAS, Claude Code, Opus 5.5)

**Status: revisada pelo Matheus; as CO6-1 a CO6-7 (seção 8) DECIDIDAS em 2026-11-11 ("Aprovo todas"), pela recomendação.** Os números continuam PROPOSTOS. Esta espec detalha a CO6 da `docs/TAREFA_V3_COOPERACAO.md` (a
seção 3: "a reputação entrar na percepção do cérebro"). Ela parte da proposta `docs/futuro/kant_cooperacao.md` (as K-1 a K-6, DECIDIDAS
pelo Matheus em 2026-11-11), seção 2.1. **O código da CO6 é coordenado pela frente COOPERACAO** (o Gerente da V3, pela K-1). Esta espec é o
papel dela. Todos os números são PROPOSTOS, SEM FONTE como escolha, e não há alegação
de novidade.

## 0. O que já existe (os fatos que a espec usa)

- **A CO3** (`digilab/cooperacao.py`, com o espelho `web/app/motor/cooperacao.ts`) é função do log e só mede:
  - os atos: a disputa, a contenção e o encostar;
  - a pontuação de cada pet;
  - a reputação de *i* vista por *k*: a mesma conta, só com os atos de *i* que *k* testemunhou dentro do raio da visão;
  - tudo em inteiros na escala S, com a meia-vida de um dia e a novidade caindo pela metade na repetição.
- **O `Grupo`** (`digilab/grupo.py`) chama a cooperação no fim de cada decisão e de cada tick. Ele monta a `PercepcaoSocial` de cada pet
  (`digilab/mundo.py`): os outros à vista, onde viu cada um comer e o último toque. **Nenhum campo lê o estado interno do outro** (o
  G-RECEPTOR-SOCIAL).
- **A reputação já cumpre o G-RECEPTOR-SOCIAL:** ela é feita só de atos que o próprio pet viu. Ela é a memória de *i* sobre *j*, e não uma
  leitura do corpo ou do cérebro de *j*.
- **A CO-3, DECIDIDA:** a CO3 só mede, e a decisão de um pet só muda na CO6 e na CO7, cada uma com o ok do Matheus.

## 1. A pergunta da etapa

O cérebro de cada pet pode **receber** a reputação dos outros e o próprio peso dos deveres, como percepção, sem que isso mude ainda o que
ele decide? A CO6 é a etapa que põe os sinais dentro do cérebro e os mostra. A CO7 é a que os usa para decidir (o escudo e o teste da
universalização). **Separar as duas** deixa ver, na CO7, que a mudança de comportamento vem do uso e não da chegada do sinal. É o mesmo
argumento da CO-3.

## 2. O que a CO6 acrescenta

### 2.1 A reputação na percepção social

- **O campo novo** `reputacao` na `PercepcaoSocial` traz `(id, r)` para cada outro presente no grupo, em ordem de id, com
  `r = Cooperacao.reputacao(id, vista_por=ident, tick)`, inteiro na escala S.
- **Os presentes, não só os à vista** (CO6-2): a reputação é memória, e o pet "lembra" de quem não está vendo agora.
- **Desligado** (a chave da CO6, seção 4), o campo vale `None`, e a percepção de hoje sai igual byte a byte.

### 2.2 O peso dos deveres (o `k`) pela convivência

A proposta (2.1, Alger e Weibull 2013, `10.3982/ecta10637`) põe o peso kantiano subindo com os encontros repetidos com quem retribui.
- **A conta, no motor, como função do log** (na `Cooperacao`, como a reputação):
  - a cada tick em que *i* e *j* estão a até o raio da visão um do outro e a reputação de *j* vista por *i* é positiva, `k_i` ganha um
    passo;
  - sem esses encontros, `k_i` decai pela mesma meia-vida da pontuação (CO6-3);
  - `k_i` é inteiro na escala S e fica limitado por um teto por estágio.
- **O teto por estágio** (CO6-4): é a roda de Kohlberg da nota *Moral do pet*, que leva ao estágio 6 no Mega (D-MM-1). Enquanto a evolução
  do motor não dá o estágio, ele vem da idade, pelo mesmo provisório do `config.py` (o estágio por dias simulados). Os tetos são
  PROPOSTOS: bebê 0, criança 1/4 S, adolescente 1/2 S, adulto 3/4 S, e S só para o Mega, quando existir.
- **O campo novo** `peso_dever` na percepção do próprio pet traz o `k_i`. É o estado moral do próprio pet, e não do outro, então não fere o
  G-RECEPTOR-SOCIAL.

### 2.3 O cérebro recebe e não usa (o G-SEM-DECISAO continua)

- **O M-SENS lê** os dois campos e os põe no `estado_interno()` do cérebro, na chave `social.reputacao` e `social.peso_dever`, para o painel
  e para as medidas.
- **Nenhum módulo** (afeto, impulso, arb, plast) usa os dois na decisão nesta etapa. Um teste confere que, com a chave da CO6 ligada, as
  decisões são as mesmas da CO6 desligada, byte a byte, em vidas do `Grupo` com a cooperação ligada (CO6-5).
- **A culpa e a inveja** (a proposta 2.3, K-4: no M-AFETO, não no corpo) ficam para a CO7, porque elas mudam o afeto e, por ele, a decisão.

### 2.4 O que se vê

- **No painel do DigiBrain:** a reputação de cada outro pet e o peso dos deveres do próprio pet, em palavras e sem número (D-MM-8). Por
  exemplo, "confia no irmão" ou "ainda não confia", e "sente o dever: pouco, médio, muito".
- **Na ilha:** nada novo nesta etapa. O que a cooperação mostra é da CO5.

## 3. O que não muda

- **O motor do pet sozinho:** sem `Grupo`, não há percepção social, e a CO6 não existe.
- **O corpo químico** (D-MM-10), a luta (D-MM-2 e LP-3), o `engine.py` e a fala (a LLM é só voz).
- **A decisão de qualquer pet** (o G-SEM-DECISAO da 2.3).
- **Os saves de versões antigas:** a CO6 só existe nas vidas com dois pets, na versão da CO4.

## 4. A chave, o gabarito e a paridade

- **A chave:** uma subchave nova `co6` na `ConfigCooperacao` (no Python, em `digilab/config.py`, com status e fonte), espelhada em
  `motor/constantes.ts`. Desligada por padrão. Ela só liga com a `ligada` da cooperação também ligada; sem isso, falha alto.
- **O gabarito, num commit próprio, antes da mudança** (CO6-6): as vidas do `Grupo` de hoje com a cooperação ligada e a CO6 desligada, com
  as decisões e os `estado_interno()`. Elas são o par do G2 (desligado, byte a byte).
- **Os testes:**
  - o G2: desligada, as vidas de hoje e o gabarito saem byte a byte;
  - o G-SEM-DECISAO-CO6: ligada, as decisões e o log são os mesmos da desligada;
  - o G-RECEPTOR-SOCIAL: nenhum campo novo lê o estado interno do outro (a reputação vem só dos atos testemunhados);
  - o `k` e a reputação em casos feitos à mão (o passo, o decaimento e o teto por estágio);
  - o G-PAR-CO6: a mesma reputação e o mesmo `k`, tick a tick, no Python e no TS, contra um gabarito exportado.
- **O replay:** tudo é função do log, e nada é estado salvo. O replay de uma vida com a CO6 ligada devolve os mesmos campos.

## 5. A ordem das missões

| missão | o quê |
|---|---|
| **CO6-espec** | este documento e as CO6-1 a CO6-7 |
| **CO6a** | o gabarito das vidas de hoje, num commit próprio |
| **CO6b** | o Python: a subchave, o `k` na `Cooperacao`, os dois campos na percepção, o M-SENS lendo, e os testes |
| **CO6c** | o TS: o espelho, o G-PAR-CO6 e o painel |

**A ordem com as outras etapas:** a CO6 vem depois da CO4 na `main` (a versão do save com os dois pets), porque o painel e a paridade
leem vidas de dois pets. A CO7 vem depois da CO6.

## 6. O que fica para a CO7

- **O escudo duro, por estágio** (K-2): as ações proibidas, como a disputa "anti", saem das candidatas.
- **O teste da universalização, brando** (K-3): na forma de Roemer, julgado pela felicidade lexicográfica (D-MM-14) e pesado por `k`.
- **A culpa e a inveja no M-AFETO** (K-4).
- **O uso da reputação para escolher a quem seguir e com quem dividir.**

## 7. Uma pergunta de pesquisa possível depois (sem plano ainda)

"O peso dos deveres sobe mais entre irmãos que se encontram muito do que entre os que se encontram pouco?" É a previsão de Alger e Weibull
transposta (a assortatividade). Ela só roda com um plano de análise próprio, na bancada, como a run que a tarefa da cooperação já deixa de
fora.

## 8. As decisões (DECIDIDAS pelo Matheus em 2026-11-11, todas pela recomendação; cada uma com a recomendação e o custo de errar)

| | a decisão | a recomendação | o custo de errar |
|---|---|---|---|
| **CO6-1** | a CO6 muda a decisão? | **não**: só recebe e mostra (G-SEM-DECISAO), e a CO7 usa | se usar já, a CO7 não consegue separar o efeito do sinal do efeito do uso |
| **CO6-2** | a reputação de quem | **de todos os presentes no grupo**, não só dos que estão à vista | só dos à vista, o pet "esquece" o irmão quando ele sai do campo, o que não combina com a reputação ser memória |
| **CO6-3** | a meia-vida do `k` | **a mesma da pontuação** (um dia, `meia_vida_pontuacao`), sem número novo | uma meia-vida própria seria mais um número sem fonte; a mesma pode deixar o `k` cair rápido demais entre visitas |
| **CO6-4** | o teto do `k` por estágio | **0, 1/4, 1/2 e 3/4 de S** do bebê ao adulto, e S só no Mega, PROPOSTOS | tetos altos cedo deixam o bebê kantiano; tetos baixos demais tornam a CO7 invisível até o adulto |
| **CO6-5** | a prova do G-SEM-DECISAO | **as vidas do `Grupo` com a cooperação ligada, CO6 ligada contra desligada, byte a byte** | sem ela, uma mudança acidental na decisão passaria sem ser vista |
| **CO6-6** | o gabarito | **num commit próprio, antes da CO6b** | sem ele, o G2 não tem par fixo |
| **CO6-7** | o painel | **em palavras, sem número** (D-MM-8) | um número convida o dono a otimizar a reputação, contra a D-MM-8 |
