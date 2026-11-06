# TAREFA V3 — PONTE_LUTA (2026-11-04)

Coordenador: Gerente da V3 (Claude Code). Worker: Claude Code, Opus 5.5, worktree `v3-ponte-luta`. Worktree e branch: `v3-ponte-luta`. Status: ENTREGUE (só o papel); as PL-1 a PL-9 (seção 8) DECIDIDAS pelo Matheus em 2026-11-04, todas pela recomendação ("Aprovo e mescle"); o código (PE0 em diante) liberado.

Categoria: arquitetura. Origem: Matheus, 2026-11-04: o Matheus pediu o cérebro presente na luta, aprendendo com ela; o Gerente mostrou três opções e ele aprovou ligar o cérebro à luta, começando por esta tarefa no papel.

**Esta etapa é só papel.** Nenhum código, nenhuma vida e nenhum número de jogo. Os nomes de chave, de evento, de campo e de gancho abaixo
são PROPOSTOS. Todo número que aparece é ou um que já está no código (com o caminho), ou PROPOSTO e SEM FONTE.

**O pedido, nas palavras do Matheus (2026-11-04):** "ele ver o comportamento da batalha e ele alterar os próprios [gambits] de maneira
automática, ele mesmo rever as estratégias de batalha dele mesmo e ver qual que ele performa melhor".

**As três opções que o Gerente mostrou e o que o Matheus decidiu:** (1) mostrar o aprendizado da luta que já existe, uma tela, em outra
sessão, já; (2) ligar o cérebro à luta, **esta tarefa**; (3) o modular decidir os golpes, fora, de alto custo. O Matheus aprovou a
recomendação: o 1 já, e o 2 começando por este papel.

## 1. Pergunta

**Qual é a ligação mínima, nas duas direções, entre o DigiBrain modular e o aprendizado da luta em tempo real, de modo que o estado do
cérebro mude como o pet luta e aprende a lutar, e que o fim de cada luta chegue ao corpo, ao afeto e à memória autobiográfica, cada peça
atrás de chave desligada e com a vida de hoje byte a byte?**

Não é run de pesquisa e não mede se o pet luta melhor. Como na L3 (`docs/TAREFA_V3_LAB_MODULAR.md`, seção 1), o que esta ponte produz no
jogo serve para ver o pet; **nenhum número do jogo vira resultado.** A parte do pedido "ver qual que ele performa melhor" já existe hoje no
aprendizado próprio da luta (seção 2.1, o `GambitsPet`): a ponte não troca esse aprendizado, ela o liga ao resto do pet.

**Sem alegação de novidade.** Emoção que modula o aprendizado e decide quando reavaliar uma escolha já foi publicada (Gadanho e Hallam
2001, `10.1177/105971230200900102`); sinais globais que regulam os metaparâmetros do aprendizado, entre eles a aleatoriedade da escolha,
são a proposta teórica de Doya (2002), `10.1016/s0893-6080(02)00044-8`; motivações do corpo e "hormônios" que mudam a intensidade do
comportamento, Cañamero (1997), `10.1145/267658.267688`; episódios emocionais recuperados que fazem o agente buscar quem o acariciou e
fugir de quem o chutou, Francis, Mehta e Ram (2009), `10.4018/978-1-60566-354-8.ch020`. As quatro estão VERIFICADAS
(`docs/referencias/v3c0_referencias_verificadas.csv`, `docs/referencias/dm_referencias_verificadas.csv`), sobre resumo ou triagem, não
sobre o artigo inteiro. **Nenhuma delas fala de combate, de regras SE/ENTÃO nem de gambits:** autorizam a direção (o afeto como
modulador e a lembrança emocional), nunca os mapeamentos, as escalas ou os nomes desta tarefa, que são SEM FONTE.

## 2. Depende de

- **Na `main`, já:** a luta em tempo real (`web/app/motor/combate_tr/`), o `GambitsPet` com o aprendizado do candidato v14
  (`web/app/motor/gambits_pet.ts`, `APRENDIZADO_V14`), a confiança M1 (`web/app/motor/confianca.ts`), o modular inteiro em TS no pet de
  teste v16 (a L3, #542 a #551), o modular como cérebro padrão dos ovos novos, na v17, com o A selecionável (o #562,
  `docs/TAREFA_V3_CEREBRO_PRIMARIO.md`) e a memória autobiográfica no Python (a C4, #529 a #541).
- **Antes da etapa PE1:** a PE0 confirma que o pet de teste v16 e o pet v17 lutam com o modular ativo. No v16 isso **não foi testado**: a
  L3 deixou "lutar com o pet de teste não foi testado" e a B3 deixou de fora "a luta com o pet de teste v16" (`docs/PAINEL_V3.md`, seção 1,
  as linhas da L3 e da B3). A v17 "luta como a v14" (`docs/TAREFA_V3_CEREBRO_PRIMARIO.md`, seção 3), mas nenhum teste citado lá luta com o
  modular ativo.
- **Do Matheus:** as PL-1 a PL-9 (seção 8), antes da PE1.
- **A outra sessão (a opção 1, a tela do aprendizado):** nenhuma dependência de código. Se ela mudar o `GambitsPet` (ela não deveria: é
  uma tela), a PE0 é refeita.

## 2.1 O que já existe (verificado na `main` em `d0f7f17`, depois do #562)

### A luta e o aprendizado dela (só na web)

| peça | o que faz | onde |
|---|---|---|
| a luta em tempo real | dois lutadores comandados por listas SE/ENTÃO, avaliadas quando o lutador fica livre; o motivo de cada ação (o índice da regra, `"exploracao"` ou `"pesado_automatico"`) vai junto, para o aprendizado | `web/app/motor/combate_tr/` (`luta.ts`, `controlador.ts`, `constantes_tr.ts`); `docs/ESPEC_COMBATE_TR.md`, seção 2 |
| o ε da luta | a chance de uma ação legal sorteada no lugar da regra: a base `CV.eps`, o piso da sombria (`CSO.epsMin`), a disciplina e a experiência de combate (v4+), e a insegurança da confiança (v8+) | `web/app/motor/gambits_pet.ts`, `estiloDoPet` (linhas 391-403) |
| a nota por regra | depois de cada luta, cada regra que agiu tem a nota puxada para a média do saldo de dano das ações dela, mais o bônus do resultado: `nota += alfa × novidade × (saldo médio + bonus × (pontos − 0,5) − nota)` | `GambitsPet.aprender`, `gambits_pet.ts:327-353` |
| a reordenação | a lista se ordena pela nota; nos v14, mais o peso fixo da posição na lista de partida (`prior`) | `GambitsPet.ordenar` e `chaveOrdem`, `gambits_pet.ts:189-226` |
| a troca da pior regra (a "exploração" do repertório) | a pior regra livre (sem trava e sem chip) abaixo do limiar dá lugar a uma candidata do repertório, sorteada pela rng `hashSemente("propor", semente)` da luta | `gambits_pet.ts:342-351` |
| os números do aprendizado | o `GA = { base: .05, alfa: .2, bonusResultado: .1, limiarTroca: -.02 }` (os v13) e o `APRENDIZADO_V14 = { alfa: .2, prior: .1, bonus: .1, limiar: .05 }` (os v14, DR2-5) | `web/app/motor/constantes.ts:364`; `web/app/motor/combate_tr/constantes_tr.ts:101-102` |
| o dono | só trava (a regra fica na posição) ou veta (o pet não a usa), entre as lutas, pelo evento `"g"` | `GambitsPet.intervir`, `gambits_pet.ts:354-372` |
| a confiança M1 | um estado derivado das lutas do registro: a novidade por rival (`exp(−λ m)`), a confiança `c` empurrada pelo resultado (a derrota pesa mais pela sensibilidade do temperamento) e decaindo no tempo; a insegurança soma `kappaEps × max(0, −c)` ao ε | `web/app/motor/confianca.ts`; `CCF` em `constantes.ts:117` |
| o ponto em que a luta ensina | para cada luta da série: `conf.registrar(...)`, depois `gp.aprender(res, s, M.usadas, novidade)`; a novidade do rival multiplica o passo | `web/app/motor/motor.ts:585-594` (`_lutar`) |

**O que a luta não toca hoje:** o corpo químico e o cérebro. Nada em `web/app/motor/corpo.ts`, `motor_corpo.ts`, `motor_corpo_mundo.ts`
nem em `web/app/motor/digibrain/` lê uma luta (procurado por `lut`, `combate`, `rival`). No pet de teste v16 e no pet v17 com o modular
ativo a luta passa ao lado do modular: o `_lutar` é o mesmo de todo pet, e o `DigiBrain` (`this.lab`, `motor.ts:216-237`) não é chamado.

**O pet v17 (o #562, na `main` desde 2026-11-04):** os ovos novos nascem v17 com o modular decidindo; o evento `"cb"` troca o cérebro no
meio da vida, e o que sai fica parado (`Motor._trocarCerebro`, `motor.ts:1052-1058`). A v17 luta como a v14 (a `docs/TAREFA_V3_CEREBRO_PRIMARIO.md`,
seção 3). Ou seja: **o modular já decide em pets de verdade**, e a D-C1-3 deixou de ser a porta para isso (PL-7).

### O modular (Python de referência e espelho TS no pet v16 e no v17)

| peça | o que faz | onde |
|---|---|---|
| o M-AFETO | a cada decisão, a urgência de cada receptor, o `g_apr` (o ganho da aprendizagem) e o `g_exp` (o ganho da exploração); na consequência, a valência `V` e a excitação `E` | `digilab/digibrain/afeto.py`; `web/app/motor/digibrain/afeto.ts` (o `g_exp` na linha 98) |
| o `g_exp` | `clamp(e0 + β_t · falta de tédio − β_u · maior urgência, 0, e_max)`, com `e0 = 512` e `e_max = 1024` numa escala `S = 1024`; no M-ARB, soma `g_exp × ε` às ativações | `afeto.ts:98`; `web/app/motor/digibrain/constantes.ts:14-17`; `arb.ts:66-67` |
| o `g_apr` | **constante no pet de teste:** `g_apr = g0 = 1024`, porque a `modula_g_apr` está desligada na L3 (LAB-1) | `digilab/config.py:2316` e `:2366`; `constantes.ts:23`; `docs/TAREFA_V3_LAB_MODULAR.md`, seção 3 |
| os receptores do estresse, da dor e do susto | drives do corpo químico; o tapa do dono sobe os três, o carinho baixa o estresse | `web/app/motor/corpo.ts:36-42`, `:485-486`, `:568-573`; `digilab/corpo.py` |
| os gestos do dono | o motor os entrega a `receber_acao_dono`; o M-ADAPT só os registra na decisão seguinte, **nunca como recompensa direta**: o corpo os sente pelos receptores | `digilab/digibrain/adapt.py:37-39` e `:289`; `adapt.ts:207-210` |
| o episódio autobiográfico | montado no fechamento da consequência, só com o que o cérebro recebeu; três origens, `consumo`, `visita` e `evento`; o campo `outro` existe e é sempre vazio (um pet só) | `digilab/digibrain/mem.py:73` (`ORIGENS_AUTOBIO`), `:113` (`"outro": None`); `docs/ESPEC_MEMORIA_AUTOBIOGRAFICA_DIGIBRAIN_MODULAR.md`, seção 3.1 |
| a significância σ | a variação do corpo que o evento causou (o `r_n` da consequência); um evento vira episódio se \|σ\| ≥ `theta_sig` ou se a subida de dor, susto ou estresse ≥ `theta_sig` | a espec da C4, seções 3.2 e 3.3 |
| a lembrança | a cada decisão, o episódio mais parecido com a pista (o lugar, o que está à vista, o cheiro, a noite, as faixas do corpo); o rival não está na pista | a espec da C4, seção 4.1 |

### A luta no Python: não existe em tempo real

- **O Python só tem o combate por turnos**, congelado: `digilab/arena.py` (a arena de pesquisa da Etapa 4) e `digilab/combate_v2/` com a
  `v21/` (as listas de gambits são estáticas: `ListaGambits`, `combate_v2/v21/gambits.py:176`). O pet luta pelo `MotorEducacao._lutar`
  (`digilab/educacao.py:376-420`) com uma lista fixa; entre as lutas só muda o ε (`epsilon_pet`, `educacao.py:111`) e a confiança
  (`digilab/confianca.py`).
- **Não há `combate_tr`, nem `GambitsPet`, nem nota por regra no Python.** Os documentos dizem isso: "Sem porte nem paridade Python. O
  `digilab/combate_v2/` do Python fica como está" (`docs/TAREFA_V2_COMBATE_TR.md:46`); "ficam, congelados: `digilab/combate_v2/` e todo o
  Python (E1)" (`docs/ESPEC_COMBATE_TR.md:311`); os gambits híbridos "existem só na web" (`docs/DESIGN_MVP_M1_CONFIANCA.md:88`). Só os
  números do `GA` são conferidos contra o Python (`docs/EQUILIBRIO_COMBATE_TR.md`).
- **O modular do Python não tem nenhum gancho de luta:** nada em `digilab/digibrain/` fala de luta, rival, vitória ou gambit.

## 3. Mudança mínima

### 3.1 O princípio: o cérebro só vê a luta pelo corpo e pela Observação

A mesma regra dos gestos do dono (`adapt.py:37-39`) e da G-RECEPTOR (`docs/ARQUITETURA_DIGIBRAIN_MODULAR.md`, seção 2): **o resultado da
luta não entra em nenhum módulo como recompensa direta.** Ele chega por dois caminhos, e só por eles:
1. **pelo corpo:** a luta é um estímulo no corpo químico (a dor, o estresse); o M-AFETO lê os receptores na decisão seguinte, como lê o
   tapa;
2. **pela Observação:** o resumo da luta entra como um evento sensorial na decisão seguinte, como os gestos do dono entram hoje
   (`receber_acao_dono`); o M-MEM o usa para montar o episódio.

E no sentido inverso, **o cérebro não escolhe golpes nem regras:** ele só lê o próprio estado num momento fixo (o começo da luta) e esse
número mexe num parâmetro que o aprendizado da luta já tem. A lista, a nota, a reordenação e a troca continuam do `GambitsPet`.

### 3.2 Da luta para o cérebro (a direção que entra primeiro)

| o quê | como (PROPOSTO) | por quê | chave (PROPOSTA) |
|---|---|---|---|
| **o fim da luta como estímulo no corpo** | um emissor novo no corpo, do tipo `estimulo` (como o `tapa`, `corpo.ts:573`): a **dor** pela fração da vida perdida na luta, `div_arred(dano recebido × S, vida máxima)`, cortada em [0, S]. É a única leitura sem número livre: a escala é a da própria luta. O **estresse** pela derrota só entra se o Matheus quiser (PL-3), e aí com um número PROPOSTO | a σ da C4 é a variação do corpo (Ho 2005, pela espec da C4, 1.3); sem estímulo no corpo a luta nunca vira episódio pela regra 3 da 3.3 da C4, e o afeto não a sente | `luta_corpo` |
| **o resumo da luta como evento da Observação** | o motor guarda, no fim de cada luta da série, um resumo **em inteiros**: o rival (o mesmo rótulo de `rivalDaConfianca`), o resultado (−1, 0, +1), a vida perdida em S e o tick; o M-ADAPT o recebe por um gancho novo, `receber_luta(resumo, tick)`, irmão do `receber_acao_dono`, e o entrega ao M-SENS na decisão seguinte | é a forma de a luta chegar ao cérebro sem que o Python precise da luta (3.4) | `luta_memoria` |
| **o fim da luta como episódio autobiográfico** | uma quarta origem, `luta`, ao lado de `consumo`, `visita` e `evento`: o episódio leva o rival no campo `outro` (hoje sempre vazio), a ação `("lutar", rival)`, o corpo e o afeto antes e depois, e σ pela variação do corpo (como todo episódio). A categoria é `("lutar", rival, sinal de σ)`. Vira episódio pela regra de hoje (\|σ\| ou a subida da dor ≥ `theta_sig`); **nenhum limiar novo**. A consolidação, a capacidade e o esquecimento são os de hoje | o pedido: a luta na memória autobiográfica; a categoria por rival é o que deixa a consolidação guardar "a pior luta contra o rival X" (o "mais significativo de cada categoria", ME-3) | `luta_memoria` (só vale com `memoria_autobio`) |

**O que não muda nessa direção:** a lembrança (a pista não ganha o rival; ver PL-6), as facetas (fora do laboratório, LAB-1), o M-PLAST
(a luta não é consequência de uma decisão do modular: não há crédito a dar a nenhuma unidade dele), a confiança M1 e o `GambitsPet`.

**Uma luta numa série** (Cidadela, Liga, instalações) gera um estímulo e um resumo por luta, como a confiança já faz (`motor.ts:585-591`);
as lutas da série entram na mesma decisão seguinte, na ordem.

### 3.3 Do cérebro para a luta (a direção que entra depois)

O cérebro mexe **em um parâmetro só**, no começo de cada luta, lendo o estado da última decisão do modular. As leituras candidatas e o que
cada uma mudaria:

| leitura do modular | parâmetro da luta | como (PROPOSTO) | o que já se sabe | recomendação |
|---|---|---|---|---|
| **o `g_exp`** (o ganho da exploração: sobe com o tédio, desce com a maior urgência do corpo) | **o ε da luta** (`estiloDoPet`) | `ε da luta = min(1, ε de hoje × g_exp / e0)`; com `g_exp = e0` (o neutro), o ε é o de hoje, sem número novo | o mesmo conceito dos dois lados: a aleatoriedade da escolha (Doya 2002, como metaparâmetro; teoria, não medida). Um pet com fome forte ou dor explora menos na luta; um pet entediado, mais | **esta primeiro** (PL-4) |
| a valência `V` (negativa: o pet está mal) | o ε da luta | `+ kappaEps × max(0, −V/S)`, a mesma conta da insegurança da confiança, com o mesmo `CCF.kappaEps`; nenhum número novo | soma uma segunda insegurança à da confiança M1; as duas leriam "o pet está mal" por caminhos diferentes e se confundiriam | não por agora |
| o `g_apr` (o ganho da aprendizagem) | o passo do aprendizado (`alfa`) | `alfa × g_apr / g0` | **no pet de teste o `g_apr` é constante** (`g0`, a `modula_g_apr` desligada, LAB-1): a conta não mudaria nada. Ligar a `modula_g_apr` é trazer de volta um controle de pesquisa que a L3 deixou fora, e a D-1 marca a excitação no `g_apr` como HIPÓTESE EXPERIMENTAL (`docs/ESPEC_DIGIBRAIN_MODULAR.md`, seção 2.4) | fora (PL-5) |
| o medo (o receptor do susto) ou o estresse | o limiar da troca da pior regra | o pet sob estresse troca mais cedo (ou mais tarde) | sem fonte para o sentido; mexe na "exploração do repertório", que muda a lista que o dono vê | fora (PL-5) |
| a lembrança de um rival (os episódios com `outro` = rival) | a novidade do rival, ou o ε contra ele | a soma dos σ dos episódios do rival como um segundo termo da confiança | depende de a direção 3.2 existir e de haver episódios de luta guardados para olhar; é o PEPE (fugir de quem chutou), por semelhança | depois (PL-6) |

**A conversão na fronteira:** o modular é só inteiro e o `GambitsPet` é float. A conta da ponte lê inteiros do modular e devolve um float
ao `estiloDoPet`; como `e0 = 512` e `S = 1024` são potências de 2, `g_exp / e0` é exato em binário e a conta é determinística no replay.

**O momento da leitura:** o começo da luta, com o estado da última decisão do modular (o `afeto.g_exp` que o motivo da decisão já grava,
`adapt.ts:135`). Nenhuma decisão nova do modular é tomada para a luta; nenhuma rng do modular é consumida. Numa série, a mesma leitura vale
para todas as lutas dela (o modular não decide entre elas).

### 3.4 Onde mora a ponte

A luta em tempo real e o `GambitsPet` **só existem na web** (2.1). O caminho "Python primeiro, com paridade" não se aplica inteiro. A
recomendação (PL-1) divide a ponte pelo lado:

| parte | onde | por quê |
|---|---|---|
| o lado do cérebro e do corpo (o estímulo da luta, o gancho `receber_luta`, a origem `luta` no M-MEM) | **Python primeiro**, em `digilab/corpo.py`, `digilab/digibrain/` e no replay do mundo (`digilab/mundo.py`, `reproduzir_mundo`), atrás das chaves; depois o espelho TS com G-PAR | é a regra do porte da L3 (seção 3.1 dela): nenhum número nasce na web, e o modular do Python é a referência |
| **o resumo da luta no Python** | um evento novo no log do mundo do Python, que **carrega o resumo pronto** (rival, resultado, vida perdida em S): o Python não simula a luta, ele recebe o que a luta deu. Os testes e o exportador usam resumos escritos à mão | o Python não precisa da luta em tempo real para testar a memória e o corpo; portar o `combate_tr` ao Python é a E1, fora (`docs/ESPEC_COMBATE_TR.md:311`) |
| o lado da luta (o ε pelo `g_exp`, a montagem do resumo a partir do `ResultadoLuta`) | **só na web**, em `web/app/motor/gambits_pet.ts` e `motor.ts` (`_lutar`) | o `GambitsPet` e o `ResultadoLuta` só existem na web; o gabarito é o do replay dos pets v16 com luta (PE0), não um gabarito do Python |

Não se reproduz o `combate_v2` do Python nesta tarefa: ele é por turnos, e a luta do jogo não é mais (o descarte 6).

### 3.5 Etapas (não há run)

Cada etapa num PR próprio, cada mecânica atrás da sua chave desligada, e **o gabarito antes**, num commit próprio, conferido por teste.

| etapa | o quê | onde | gabarito antes | gate | modelo |
|---|---|---|---|---|---|
| **PE0** | o v16 e o v17 lutam com o modular ativo? Um e2e e um teste do motor: o pet nasce, chega a um estágio que luta, luta contra um bot e uma série, e o replay refaz as lutas. **O gabarito das lutas de hoje:** vidas curtas com lutas (sementes 101…505) do v16, do v17 com o modular, do v17 com o A e do v17 com um `"cb"` entre duas lutas, gravando por luta o `ResultadoLuta` resumido, a assinatura do `GambitsPet`, a da confiança e o `estadoInterno` do modular | `web/app/test/`, `web/app/e2e/` | — (é ele) | os dois lutam e o replay sai bit a bit; se não lutarem, a ponte para e o conserto vira tarefa própria | Sonnet |
| **PE1** | o estímulo da luta no corpo (a dor pela vida perdida) e o evento do resumo no replay do mundo do Python | `digilab/corpo.py`, `digilab/config.py` (`luta_corpo`), `digilab/mundo.py` (o evento, aceito só com a chave) | os gabaritos de hoje que passam pelo corpo e pelo mundo (o da LM0, `web/app/test/gabaritos/digibrain_modular_*.json.gz`; o do G0, `tests/gabaritos/genoma_g0_vidas_de_hoje.json`) seguem byte a byte com a chave desligada | **G2:** desligada, byte a byte; **T-PL-1:** um resumo com vida perdida sobe a dor exatamente `div_arred(...)`, sem rng; um resumo com a chave desligada levanta erro | Sonnet |
| **PE2** | o gancho `receber_luta`, o resumo na Observação e a origem `luta` no M-MEM (`outro` = rival) | `digilab/digibrain/adapt.py`, `sens.py`, `mem.py`, `digilab/config.py` (`luta_memoria`) | o gabarito da C4 e o da LM0, byte a byte desligada | **G2**; **T-PL-2:** um resumo de derrota com dor vira um episódio `luta` com o rival em `outro`; um empate sem dor não vira; o mesmo log dá os mesmos episódios; a consolidação guarda um por categoria `("lutar", rival, sinal)` | Sonnet |
| **PE3** | o espelho TS da PE1 e da PE2; o evento da ponte no registro (o nome PROPOSTO `"pl"`, gravado no ovo novo pelo `ligarProduto`, como o `"cb"`, e no ovo de teste do laboratório); e o `_lutar` do v16 e do v17 com o evento entregando o resumo ao corpo e, com o modular ativo, ao `DigiBrain` (3.7) | `web/app/motor/corpo.ts`, `web/app/motor/digibrain/`, `motor.ts` | o da PE0 e todos os de hoje | **G-PAR** do corpo e do M-MEM com um exportador novo de leituras (`experiments/exportar_gabarito_digibrain_modular.py`, numa opção nova, como o `--fins` da LM4); **G2:** o gabarito da PE0 passa com as chaves desligadas; **G1:** o replay do v16 e do v17 com luta bit a bit, com o modular e com o A, e com um `"cb"` no meio | Sonnet |
| **PE4** | o ε da luta pelo `g_exp`, no v16 e no v17 com o evento da ponte e o modular ativo (com o A, o ε de hoje, 3.7) | `web/app/motor/gambits_pet.ts` (`estiloDoPet`), `motor.ts` | o da PE0 | **G2:** desligada, o gabarito da PE0 byte a byte; **T-PL-4:** com `g_exp = e0` o ε é o de hoje; o ε lido é o da última decisão; o replay bit a bit | Sonnet |
| **PE5** (só se o Matheus decidir, PL-6) | a lembrança do rival na luta | papel antes do código | — | — | Opus |

A PE4 só depende da PE0 (não da PE1 a PE3): se o Matheus preferir ver primeiro o cérebro mudando a luta, ela pode vir antes (PL-2).

### 3.6 O que não muda

- `digilab/engine.py` (o sha256 congelado), o `combate_tr` (a luta em si: a física, o controlador, as condições), o `GambitsPet.aprender`,
  a nota, a reordenação, a troca e as rngs da luta.
- Os pets v13, v14 e v15: nenhuma ponte. Os v16 e v17 sem o evento da ponte (todos os que estão vivos hoje) saem como hoje, byte a byte
  (PL-7). Os saves de hoje abrem iguais.
- A confiança M1 e o `CCF`.
- O `docs/ESPEC_COMBATE_TR.md` e as metas do equilíbrio do combate.

### 3.7 Quando o cérebro ativo é o A (o v17 depois de um `"cb"` do A)

A regra do #562: o cérebro que sai "fica parado enquanto o outro decide (não recebe decisão, consequência nem gesto do dono); ao voltar,
continua dali" (`docs/registro/2026-11.md`, a seção CÉREBRO PRIMÁRIO, interpretação 1). A ponte segue a mesma regra (a recomendação da PL-9):

| peça da ponte | com o modular ativo | com o A ativo |
|---|---|---|
| o estímulo da luta no corpo (a dor) | sim | **sim:** o corpo é do pet, não do cérebro. O A sente a dor pelos receptores, como sente o tapa (a dor está entre os receptores e os drives do A, `web/app/motor/lobos.ts:49-51`) |
| o resumo na Observação e o episódio `luta` | sim | **não:** o modular está parado. A luta não vira episódio, e o resumo não fica guardado para quando ele voltar |
| o ε da luta pelo `g_exp` | sim | **não:** o ε é o de hoje. O `g_exp` do modular parado é de antes da troca e não descreve o pet de agora |
| o `GambitsPet` e a confiança M1 | iguais | iguais: a luta aprende como hoje com qualquer cérebro |

**Ao voltar ao modular:** ele continua dali, sem as lutas do tempo do A na memória, e só lê a dor que ainda estiver no corpo. **O A nunca
recebe nada da ponte além do corpo:** o A é a linha de base e o controle, e nenhum gancho novo entra nele.

## 4. Experimento e gate (se houver run)

Não há run. Não há plano de análise nem sementes reservadas: os gabaritos usam as sementes dos testes (101…505), como na L3. Os gates são
os de cada etapa (3.5): G2 (desligada, byte a byte), G1 (o replay), G-PAR (Python × TS no lado do cérebro) e os testes T-PL. Medir se o pet
luta melhor com a ponte é outra pergunta, com plano próprio (PL-8).

## 5. Entrega

- Testes: `python -m pytest tests/ -q`; em `web/app`: `npm test`, `npm run tipos`, `npm run e2e` (da PE0 em diante, que tocam a web).
- Registro: seção própria no fim de `docs/registro/2026-11.md` (ou do mês da etapa) e uma linha no fim do índice
  `docs/REGISTRO_DESVIOS.md`. O resumo de cada etapa vai no corpo do PR e numa seção no fim deste documento.
- PR contra a `main`, no modelo `.github/pull_request_template.md`, conferido por `tools/verificar_relato.py`. Merge só pelo Matheus.

**Arquivos disputados** (`docs/PLANO_V3.md`, seção 5): `digilab/digibrain/` (trilha C), `digilab/mundo.py` (uma missão por vez; o G0 da
genética, E2, também o toca) e `web/app/motor/motor.ts` (a L3, o #525 e o G0, se for à web). A PE1 e a PE2 conferem no `PAINEL_V3.md` que
nenhuma outra frente está com esses arquivos abertos.

## 6. Fora desta tarefa

- **O modular decidir os golpes ou as regras** (a opção 3): o cérebro não escolhe ação nem regra na luta, não reordena a lista e não troca
  regra. Ele só mexe num parâmetro (3.3).
- **Treino por clique de recompensa ou punição.** Regra do Matheus: nada de treino baseado em clicar carinho e tapa. A ponte não cria
  nenhum gesto do dono que ensine a luta, não usa o carinho nem o tapa como sinal da luta e não deixa a luta virar recompensa direta de
  nenhum módulo (3.1). O dono continua só travando e vetando (`GambitsPet.intervir`).
- A tela do aprendizado da luta (a opção 1, outra sessão) e qualquer tela desta ponte (o painel do laboratório mostrar a lembrança de uma
  luta é tarefa própria, depois da PE3).
- Portar o `combate_tr` ou o `GambitsPet` ao Python (a E1 do combate).
- A ponte nos pets v13 a v15, e ligá-la num v16 ou v17 que já está vivo (PL-7).
- A `modula_g_apr`, as facetas, a C2, a C3 e a L-2 no pet de teste (LAB-1).
- O outro pet como participante (o `outro` passa a ter o rival da luta, não um pet do mundo).
- A calibração de qualquer número (a rodada de equilíbrio, no fim).

## 7. Critérios de aceitação

- Desta etapa (o papel): este documento na `main` com as PL-1 a PL-9 decididas pelo Matheus.
- De cada etapa de código: com as chaves desligadas, todos os gabaritos e e2e de hoje passam sem regravar; com elas ligadas, o replay do
  pet v16 e do v17 com luta é bit a bit, com qualquer dos dois cérebros; o lado do cérebro tem G-PAR Python × TS; nenhum número sem status e sem fonte (ou SEM FONTE) em
  `digilab/config.py`.
- Nenhum módulo do modular recebe o resultado da luta como recompensa: um teste confere que, com a dor zerada à mão, uma derrota não muda
  nenhum `g_apr`, `V`, `E` nem crédito do M-PLAST.

## 8. Precisa do Matheus

Cada uma com a recomendação e o custo de errar.

**DECIDIDAS pelo Matheus em 2026-11-04, todas pela recomendação:** "Aprovo e mescle".

| decisão | a pergunta | recomendação | custo de errar |
|---|---|---|---|
| **PL-1** | onde mora a ponte, já que a luta em tempo real só existe na web | **dividida:** o lado do cérebro e do corpo no Python primeiro, com o resumo da luta como evento pronto no log do mundo, e espelho TS com G-PAR; o lado da luta só na web, com o gabarito do replay do v16 (3.4) | tudo só na web: a memória e o corpo do modular ganham um número e uma regra que o Python não tem, e a paridade da L3 quebra. Portar a luta ao Python: semanas de trabalho para testar o que um resumo pronto já testa |
| **PL-2** | a ordem das direções | **da luta para o cérebro primeiro** (PE1 a PE3), depois do cérebro para a luta (PE4); a PE0 antes de tudo | ao contrário: o pet muda como luta antes de a luta deixar rastro no corpo e na memória, e o Matheus vê o efeito sem a causa no painel. A troca custa pouco: a PE4 só depende da PE0 |
| **PL-3** | o que a luta faz no corpo | **só a dor pela fração da vida perdida**, sem número livre; o estresse da derrota fica fora até haver um número PROPOSTO que o Matheus aceite | com o estresse, um número SEM FONTE entra no corpo, e cada derrota pesa no humor do pet pelo resto do dia (a meia-vida do estresse é 1 440 min, `corpo.ts:486`). Sem a dor, a luta nunca vira episódio pela regra de hoje |
| **PL-4** | qual leitura do cérebro muda a luta primeiro | **o `g_exp` no ε da luta**, `ε × g_exp / e0`, neutro no `e0` | a valência no ε duplica a insegurança da confiança M1; o `g_apr` no `alfa` não muda nada no pet de teste (é constante) |
| **PL-5** | o `g_apr` no passo do aprendizado e o estresse ou o medo no limiar da troca | **fora agora**; voltam só com a `modula_g_apr` validada ou com fonte para o sentido | dentro: um controle de pesquisa (`modula_g_apr`) volta ao pet sem validação, e o pet troca regras por um sentido sem fonte, o que muda a lista que o dono vê |
| **PL-6** | a lembrança do rival na luta (o rival na pista, ou a soma dos σ do rival na confiança) | **depois**, com papel próprio (PE5), quando a PE3 mostrar episódios de luta guardados de verdade | antes: a memória de luta pesa na luta sem nenhum episódio para olhar, e a lembrança passa a disputar com a confiança M1, que já lê o rival |
| **PL-7** | em que pets a ponte liga | **no v16 do laboratório e no v17, pelo evento da ponte no registro, gravado no ovo novo** (como o `"cb"`); um v16 ou v17 já vivo, sem o evento, fica como hoje. Com o #562, o modular já é o cérebro do pet de verdade: a ponte não fica restrita ao pet de teste (pedido do Gerente, 2026-11-04). A pergunta "até a D-C1-3?" perdeu o objeto | sem o evento, isto é, a ponte em todo v17: o replay de todo v17 vivo muda e o save não abre igual. Ligar num pet vivo: a dor SEM FONTE e a memória de luta entram num pet que não volta atrás; se o Matheus quiser, é um evento a mais, como o `"cb"` do pet ativo (CP-1) |
| **PL-8** | medir se o pet luta melhor com a ponte | **não nesta tarefa:** o laboratório serve para ver o pet; uma medida pede plano de análise e faixa de sementes próprios, e a bancada da luta (`web/app/scripts/equilibrio_tr/`) não roda o modular | medir sem plano: um número do jogo vira resultado sem gate, contra a regra do `CLAUDE.md` |
| **PL-9** | o que a ponte faz com o A ativo | **só o corpo:** a dor da luta vale com qualquer cérebro; o episódio e o ε pelo `g_exp` só com o modular ativo; com o A, nada fica guardado para o modular (3.7) | a dor só com o modular: o corpo passa a depender de qual cérebro decide, e um pet que perde uma luta sob o A não sente nada. Guardar as lutas para o modular: o cérebro parado passa a receber, contra a regra do #562 |

## 9. PE0, o resumo da etapa (2026-11-06, Sonnet 5.5, branch `v3-ponte-luta-pe0`)

**Resposta: o pet de teste v16 e o v17 lutam** (com o modular, com o A e com um `"cb"` entre duas lutas), e o replay refaz as lutas bit a bit.
Nenhum conserto foi preciso: a PE1 pode seguir. Os desvios D-PE0-1 a D-PE0-5 estão em `docs/registro/2026-11.md`.

- **O dono e o resumo da luta:** `web/app/test/ponte_luta_pe0.ts` (a vida curta com lutas, 2 dias, e o resumo por luta).
- **O gabarito das lutas de hoje:** `web/app/test/gabaritos/ponte_luta_pe0.json.gz`, 20 vidas (v16, v17 modular, v17 A e v17 `"cb"` × sementes 101…505) e
  512 lutas; por luta, o `ResultadoLuta` resumido e o sha256 da assinatura do `GambitsPet`, da confiança e do `estadoInterno` do modular.
  Gravado por `web/app/test/gerar_gabarito_pe0.ts` (Node), num commit antes do e2e e dos documentos. Daqui em diante é o gabarito G2 das PE1 a PE4:
  com as chaves da ponte desligadas, tem de sair byte a byte.
- **O teste do motor:** `web/app/test/ponte_luta_pe0.test.ts` (43 testes): cada vida nasce, passa do In-Training, luta contra bots e na Liga, o
  cérebro que decidia em cada luta é o esperado (o A parado e o modular continuando dali no `"cb"`), o replay evento a evento e por
  `Motor.reproduzir` fecha, e a vida de hoje sai igual ao gabarito luta a luta.
- **O e2e:** `web/app/e2e/ponte_luta.spec.ts` (saves de `e2e/gerar_save_ponte_luta.mjs`): v16 (pelo laboratório), v17 modular e v17 A lutam na Arena e na
  Liga e o app reabre o save com as mesmas lutas.
- **Limite:** a série do gabarito é a Liga, que o pet de vida curta quase sempre perde na primeira luta (1 série de 2 lutas em 20; D-PE0-2).

## 10. PE1, o resumo da etapa (2026-11-06, Sonnet 5.5, branch `v3-ponte-luta-pe1`)

**Resposta: o resumo de uma luta já sobe a dor do corpo e entra no replay do mundo do Python, atrás de uma chave desligada.** Os desvios D-PE1-1 a
D-PE1-5 estão em `docs/registro/2026-11.md`.

- **A chave:** `ConfigLutaCorpo(ligada=False)` em `digilab/config.py` (`CONFIG_LUTA_CORPO`, `CONFIG_LUTA_CORPO_LIGADA`, status em
  `PARAMETROS_LUTA_CORPO`: PROPOSTO, sem número livre). Fica fora de `ConfigCorpo` para o dump do gabarito de paridade do corpo e o `corpo.test.ts` não mudarem (D-PE1-1).
- **A dor:** `Corpo.estimulo_luta(vida_perdida_s)` em `digilab/corpo.py`: a dor sobe exatamente `div_arred(p × C, S)`, com `p` cortado em [0, S], sem rng
  (D-PE1-2). Exige `gestos`.
- **O evento:** `lt` (renomeado do `pl` a pedido do Matheus na revisão: o `"pl"` fica livre para a marca do ovo da PE3) com valor `rival|resultado|vida_perdida_s` (`digilab/events.py`: `resumo_luta`, `ler_resumo_luta`, `LutaSemChave`);
  `MotorMundo.resumo_luta` e o `reproduzir_mundo` (`digilab/mundo.py`) o entendem; o `MotorCorpo` (`digilab/motor_corpo.py`) o aplica. Com a chave
  desligada, ou sem o corpo, levanta `LutaSemChave`.
- **Testes:** `tests/test_ponte_luta_pe1.py` (T-PL-1: a dor exata, o corte, o erro com a chave desligada, o replay refaz o corpo). **G2:** os
  gabaritos da LM0 (`digibrain_modular_*`), do G0 (`genoma_g0_vidas_de_hoje.json`), do corpo, do corpo no mundo e do passeio seguem byte a byte; nenhum
  arquivo de gabarito foi tocado.
- **Limite:** o rival e o resultado só são validados; entram em módulo na PE2. Nada na web (o espelho TS é a PE3).

## 11. PE2, o resumo da etapa (2026-11-06, Sonnet 5.5, branch `v3-ponte-luta-pe2`)

**Resposta: o resumo de uma luta já chega ao DigiBrain modular, vira (ou não) um episódio `luta` no M-MEM com o rival em `outro`, atrás de uma chave
desligada.** Os desvios D-PE2-1 a D-PE2-3 estão em `docs/registro/2026-11.md`.

- **A chave:** `ConfigLutaMemoria(ligada=False)` em `digilab/config.py` (`CONFIG_LUTA_MEMORIA`, `CONFIG_LUTA_MEMORIA_LIGADA`, `PARAMETROS_LUTA_MEMORIA`:
  PROPOSTO, sem número livre), fora de `ConfigDigibrain` (D-PE2-1). Só com a `memoria_autobio`.
- **O gancho e a Observação:** `DigiBrain.receber_luta(rival, resultado, vida_perdida_s, tick)` (`adapt.py`), entregue pelo `MotorCorpo` ao aplicar o evento `lt`
  da PE1; o M-SENS o põe em `sens["lutas"]` na decisão seguinte (`Sens.resumir_lutas`). O `"pl"` não é usado.
- **O episódio:** `episodio_luta` e a origem `luta` em `mem.py` (a regra de hoje, `theta_sig`; σ pela variação do corpo, sem mexer em V, E, g_apr nem M-PLAST: `Afeto.sigma_luta`).
- **Testes:** `tests/test_ponte_luta_pe2.py` (T-PL-2: derrota com dor vira episódio com o rival em `outro`; empate sem dor não; o mesmo log dá os mesmos
  episódios, no replay do mundo; a consolidação guarda um por categoria `("lutar", rival, sinal)`; a seção 7: com a dor zerada nenhum módulo anda). **G2:** os gabaritos da C4
  (`test_gabarito_memoria_autobio`), da LM0 (`test_gabarito_digibrain_modular*`), do G0 e do corpo seguem byte a byte; nenhum arquivo de gabarito foi tocado.
- **Limite:** nada na web (o espelho TS e o `"pl"` do ovo são a PE3). O A não recebe nada (3.7): o gancho só existe no DigiBrain.

## 12. PE3, o resumo da etapa (2026-11-06, Sonnet 5.5, branch `v3-ponte-luta-pe3`)

**Resposta: a dor da luta e o episódio `luta` já chegam ao jogo (v16 e v17 com a marca `"pl"`), com o corpo e o M-MEM conferidos contra o Python.** Os desvios D-PE3-1 a
D-PE3-7 estão em `docs/registro/2026-11.md`.

- **O espelho TS:** `Corpo.estimuloLuta` e `CONFIG_LUTA_CORPO` (`motor/corpo.ts`), o evento `lt` do `MotorCorpo` (`motor/motor_corpo.ts`: `resumoLuta`, `aplicarResumoLuta`,
  `lerResumoLuta`), `DigiBrain.receberLuta`/`ligarLutaMemoria`, `Sens.resumirLutas`, `Afeto.sigmaLuta`, `episodioLuta` e a origem `luta` (`motor/digibrain/`).
- **A marca e o `_lutar`:** `Motor.ligarPonteLuta()` grava `"pl"` (`{ luta: true }`, depois do `"cb"`) no ovo novo pelo `ligarProduto` (`src/produto.ts`, que também cobre o ovo
  de teste do laboratório); `Motor._lutar` calcula a vida perdida em S de cada luta da série (D-PE3-3) e entrega o resumo ao corpo (qualquer cérebro) e, só com o modular
  ativo, ao `DigiBrain` (3.7). Sem a marca, o `_lutar` é o de hoje.
- **G-PAR:** `experiments/exportar_gabarito_digibrain_modular.py --luta` grava `web/app/test/gabaritos/digibrain_modular_luta.json.gz` (3 vidas, 6 resumos cada); o
  `test/digibrain_modular_vida.test.ts` confere a dor de cada resumo, cada decisão (ação, motivo com as lutas, assinatura) e o estado interno no fim; o pytest
  (`tests/test_gabarito_digibrain_modular_web.py`) confere que o arquivo bate com uma execução nova.
- **G2:** o gabarito da PE0 e todos os de hoje passam sem mudar nenhum arquivo deles; **G1:** `test/ponte_luta_pe3.test.ts` (20 vidas com a marca: v16, v17 modular, v17 A e v17 com um
  `"cb"` no meio × 5 sementes; replay bit a bit; a dor exata; o A ativo não entrega nada ao modular; a marca só nos v16/v17, uma vez) e o e2e (`e2e/ponte_luta.spec.ts` com os saves `_ponte`).
- **Limite:** nada do ε (PE4). Os v16/v17 vivos sem a marca seguem como hoje (PL-7); nenhum save de hoje ganha a marca.

## 13. PE4, o resumo da etapa (2026-11-06, Sonnet 5.5, branch `v3-ponte-luta-pe4`)

**Resposta: o cérebro já muda a luta por um parâmetro só, o ε, pelo `g_exp` da última decisão do modular, nos ovos novos (marca `{ luta: true, eps: true }`).** Os desvios D-PE4-1 a
D-PE4-3 estão em `docs/registro/2026-11.md`.

- **A conta:** `ε da luta = min(1, ε de hoje × g_exp / e0)` em `estiloDoPet` (`motor/gambits_pet.ts`), com o fator `Motor.fatorEpsLuta()` (`motor/motor.ts`): lê o `afeto.g_exp`
  do `ultimoMotivo` do modular no começo da luta (a série inteira usa a mesma leitura), sem decisão nova nem rng. Com o A ativo, ou antes da primeira decisão, o ε é o de hoje (3.7).
- **A marca (D-PE4-1):** só `{ luta: true, eps: true }` liga; os saves com `{ luta: true }` (PE3) e os sem marca seguem com o ε de hoje, byte a byte. O `ligarProduto` grava `eps`.
- **Testes:** `test/ponte_luta_pe4.test.ts` (T-PL-4: `g_exp = e0` dá o ε de hoje, `256` metade, `1024` o dobro cortado em 1; o ε lido é o da última decisão e a leitura não mexe no
  modular; 20 vidas com `eps` — v16, v17 modular, v17 A e v17 com um `"cb"` no meio × 5 sementes — refazem bit a bit; com o A o fator é nulo; a validação da marca). **G2:** o gabarito da
  PE0, o da PE3 e os testes da PE3 (marca `{ luta: true }`) passam sem mudar nenhum arquivo de gabarito.
- **Limite:** não se mediu se o pet luta melhor; é outra pergunta (PL-8). O A não recebe nada. Fica a PE5 (a lembrança do rival), só se o Matheus decidir (PL-6).
