# DigiBrain V3: a auditoria E0 do cérebro A no v11 e um desenho experimental

> **Nota (2026-10-24), a direção nova:** o Matheus decidiu, no PROMPT MESTRE, que o produto jogável vem primeiro, que o DigiBrain
> caminha para um cérebro **modular**, e que o cérebro A fica como linha de base, controle e fallback condicionado, e não como o cérebro
> final da web. As decisões "a web roda um DigiBrain, o A" (2026-10-01) e o M6 (rodada 15) estão **SUPERADAS** desde 2026-10-24; o
> texto abaixo fica como estava, como registro. Ver `docs/ARQUITETURA_DIGIBRAIN_MODULAR.md` e `docs/AUDITORIA_V2_PRODUTO_MODULAR.md`.
>
> A V3-2 ("só na pesquisa no Python, em chaves desligadas sobre o A") está superada para o que for ao produto: as peças do V3 (a
> competição, o traço, o passo modulado pela química) passam a ser candidatas a módulos (`docs/ARQUITETURA_DIGIBRAIN_MODULAR.md`).

Status (2026-10-18): **PROPOSTO, só papel e uma medição descritiva.** Pedido do Matheus, por uma sessão lateral do coordenador. As
decisões V3-1 a V3-8 (seção 6) são dele. Nada aqui muda o cérebro A, o `digilab/`, o v11 ou o porte da web: o A fica intacto como a
referência. Nenhuma run de pesquisa antes de uma tarefa e de um plano de análise registrados.

**O pedido:** o Matheus trouxe uma proposta de cognição incorporada. A ideia é um organismo pequeno cujo comportamento fique mais rico
que as regras explícitas que o compõem, em vez de escalar para o conectoma da mosca. O primeiro passo pedido é **auditar a decisão do
v11** (a arbitragem do instinto, o crédito e a memória) antes de desenhar um V3.

**Regras deste documento:**
- referências só as verificadas (a skill `literatura-digilab`; `docs/referencias/REGRAS_CITACAO_DIGILAB.md`), com quanto foi lido;
  SEM FONTE onde não houver;
- números novos PROPOSTOS; os números da parte 1 saem de `artifacts_v2_v3/e0_influencia.json`;
- **nenhuma alegação de novidade.** Modulação hormonal do aprendizado num pet artificial já existe no Creatures (seção 3.3);
- nenhum rótulo "sente", "pensa" ou "quer" como alegação: onde aparecem, são nomes de mecanismo.

## 1. A medição E0

`experiments/medir_e0_influencia_aprendido.py` → `artifacts_v2_v3/e0_influencia.json` (sha256 `48bd425c…`, igual em duas execuções).

- **Bancada:** a do v11, `exportar_gabarito_lobos.bancada_v11(14, 224)`, braço `P1-c-tapa` (o T3 com os canais, o ganho 4, o corpo do
  ponto (2, 1), `w_novos` 2; `S` = 1024, passo 512, teto 16 S, piso S/16, `traco_decisoes` = 0).
- **Vidas:** 4 donos (atencioso, relapso, aleatório, incoerente) × 5 sementes dos testes (101…505), 14 dias: 20 vidas, **26.880
  decisões**.
- **Natureza:** descritiva, sem gate e sem plano, como a medida do S-3 (`medir_v11_parado.py`). Não é resultado de pesquisa.
- **A sonda:** a mesma das sondas "quem decidiu" do N7 e do J5. Para cada decisão com escolha, a política já guardou as contribuições
  por lobo e o `u` do sorteio. O script:
  1. refaz o peso efetivo e o sorteio e confere contra o registro (falha alto se divergir);
  2. tira o termo aprendido, o lobo `decisao`, que no v11 já inclui as entradas do corpo;
  3. refaz o piso como a política faz;
  4. mede a distância de variação total `TV = ½ Σ |P − P0|` e se a ação sorteada com o mesmo `u` mudaria.

### 1.1 Mais da metade das decisões não tem escolha

| regra | candidatos | fração das decisões |
|---|---|---|
| `tempo_livre` | 4 | 42,5% |
| `sono_continuar` | 1 | **34,6%** |
| `abandono` | 1 | 8,8% |
| `pedido_necessidade` | 1 | 7,0% |
| `sono_noite` | 1 | 2,7% |
| `fome_moderada` | 2 | 2,2% |
| `sono_exaustao` | 1 | 2,2% |

**55,3% das decisões têm um candidato só** (confirma o achado prévio). Nelas o instinto decide por construção, e há uma consequência a
mais: **o crédito dessas decisões não muda peso nenhum.** A regra da L1 multiplica por `S·1[a = a*] − P_a`, que é zero quando o único
candidato tem `P = 1` (`atualizar_pesos`, `digilab/policies/lobos.py`). Toda consequência que cai numa decisão forçada é perdida para o
aprendizado.

A fração varia com o dono: 43,6% (atencioso), 41,7% (incoerente), 61,6% (aleatório), **74,2% (relapso)**. O pet negligenciado passa
mais tempo em regras urgentes e tem menos decisões em que pode aprender.

### 1.2 De onde vem o "80%", e o que o `lobo_decisivo` não mede

**Correção do achado prévio.** O "instinto decide 80%" da L1 (`docs/RESULTADO_V2_L1.md`, seção 2: "o lobo de decisão decidiu 20,3%")
**não vem do `lobo_decisivo`**. Vem de uma sonda contrafactual (`motivo._motivo_lobos_decisao`, usada por `run_v2_l1.legibilidade`): o
impulso decidiu quando a regra tem um candidato só, ou quando o sorteio só com os pesos do prior e o mesmo `u` devolve a mesma ação. A
fração é sobre **todas** as decisões, e foi medida noutro aprendiz (o da L1, com teto 1·S e o elogio e a bronca).

A mesma sonda no v11 (`mudou_l1` no artefato; dá o mesmo número que a sonda com o piso refeito, `mudou`):
- **o aprendido decide 15,6% das decisões**, e o instinto 84,4%;
- os 84,4% se partem em **55,3% de decisões sem escolha** e 29,2% de decisões com escolha em que o aprendido não mudaria o sorteio
  (65,2% dos 44,7% com escolha; a soma passa de 84,4% pelo arredondamento);
- **onde há escolha, o aprendido muda a ação em 34,8%**, com TV média de 0,239.

O "instinto decide ~80%" é, portanto, em dois terços uma propriedade da arbitragem (as regras forçadas) e em um terço o tamanho do termo
aprendido onde ele pode agir.

**O `lobo_decisivo` é outra coisa.** É o lobo de maior contribuição à ação escolhida (`_registrar`, perto da linha 978 de `lobos.py`),
e é o campo que o porte da web reproduz decisão a decisão (`web/app/motor/lobos.ts`). O painel DigiBrain mostra as
contribuições por lobo em barras, e a tarefa do porte já prevê "a barra do impulso quase sempre cheia"
(`docs/TAREFA_V2_W_PORTE_CEREBRO_A.md`, seção 6). Ele dá impulsos em 81,4% das decisões com escolha, o que parece concordar com
o "80%", mas não mede causa:

| | `lobo_decisivo` = impulsos | o aprendido mudaria a ação (mesmo `u`) | TV média |
|---|---|---|---|
| todas as decisões | 91,7% | 15,6% | — |
| só as com escolha | 81,4% | **34,8%** | 0,239 |
| `tempo_livre` | 82,5% | 34,4% | 0,229 |
| `fome_moderada` | 59,4% | 41,9% | 0,435 |

O caso mais claro é o do **dono atencioso**:
- o `lobo_decisivo` dá impulsos em **99,95%** das decisões com escolha;
- mas o aprendido muda a ação em **24,6%** delas.

O termo aprendido quase nunca é o maior na ação que ganha, e ainda assim muda um quarto das escolhas. A soma |decisão| / |impulsos|
sobre os candidatos é 2,21 nesse dono: o aprendido pesa mais no conjunto, mas espalhado pelos candidatos, e não na ação que ganha (não medimos
o sinal por candidato). Por dono:

| dono | um candidato | `lobo_decisivo` = impulsos (escolha) | o aprendido mudaria (escolha) | aprendido decide (todas) | TV média |
|---|---|---|---|---|---|
| atencioso | 43,6% | 99,95% | 24,6% | 13,9% | 0,130 |
| incoerente | 41,7% | 76,0% | 36,9% | 21,5% | 0,222 |
| aleatório | 61,6% | 83,3% | 36,1% | 13,9% | 0,309 |
| relapso | 74,2% | 49,9% | **50,8%** | 13,1% | 0,414 |

**Leitura (nossa):**
- o número da L1 está certo como medida, e o v11 dá um parecido (84,4%);
- mas ele mistura a **arbitragem** (55% das decisões sem escolha, estrutural) com o **tamanho do aprendido** (um terço das escolhas);
- o relapso mostra a mistura: o aprendido muda metade das escolhas dele, mas ele quase não tem escolhas, e o total fica em 13,1%;
- o `lobo_decisivo` do painel não deve ser lido como "quem decidiu". Fica PROPOSTO trocar a leitura (V3-1).

### 1.3 Ao longo da vida

| dia | decisões com escolha | TV média | mudaria (escolha) | \|decisão\|/\|impulsos\| | `lobo_decisivo` = impulsos |
|---|---|---|---|---|---|
| 0 | 1.110 | 0,062 | 9,2% | 0,12 | 99,6% |
| 1 | 896 | 0,162 | 25,3% | 0,39 | 95,8% |
| 3 | 807 | 0,234 | 35,3% | 0,85 | 94,3% |
| 6 | 784 | 0,276 | 39,0% | 1,72 | 77,4% |
| 9 | 796 | 0,282 | 41,7% | 2,82 | 71,9% |
| 13 | 796 | 0,269 | 43,2% | 3,90 | 67,2% |

(Os 14 dias estão no artefato, `por_dia`.)

- A influência causal sobe rápido nos três primeiros dias e se achata perto de 0,28 de TV e 40% de mudança a partir do dia 6.
- O termo aprendido continua crescendo: a razão |decisão|/|impulsos| vai de 0,12 a 3,90.
- Os pesos chegam perto do teto: o desvio máximo `|w − w0|` vai a 16.329 de 16.384 numa vida, com zero pesos exatamente no teto.

**Leitura (nossa):** depois do dia 6, o peso aprendido cresce sem mudar mais escolhas. O sorteio proporcional satura. Pesos maiores
empurram candidatos que já perdiam, ou o piso segura o que já estava no fundo. Não medimos qual das duas.

### 1.4 O cruzamento com a janela de crédito e com o J1

- **O traço não existe no v11.** O v11 roda com os canais (T3), e os canais não andam com o traço (`raise` em `observar`: "o T3 não tem
  traço", R1). O crédito do v11 é imediato: a consequência vai à decisão que a causou, e o tapa vai à última decisão.
- **Um traço gastaria metade em decisões forçadas.** Medimos, para um traço hipotético de k decisões, a fração das k anteriores que tem
  um candidato só: 55,2% para k = 1, 2, 4 e 8. A REVISAO-APRENDIZ testou o traço numa montagem sem canais
  (`docs/RESULTADO_V2_REVISAO_APRENDIZ.md`). Esta medida só diz que, na distribuição de regras do v11, cerca de metade do crédito
  propagado cairia onde a regra da L1 não aprende.
- **O J1** (`docs/RESULTADO_V2_VALIDACAO_MUNDO.md`): no mundo físico, o crédito imediato ensina a comer e a poupar energia, mas não a
  procurar. O P1 perde do instinto, e o alvo aprendido também perdeu (#296). O E0 dá uma razão estrutural possível, não testada: procurar
  é uma sequência de passos em que o sinal chega no último. Com o crédito de um passo, os passos anteriores não recebem nada. Com um
  traço de k passos, metade deles cai em decisões que não aprendem.

**O que o E0 não diz:**
- não mede se o aprendido melhora o pet: TV e mudança são influência, não qualidade;
- não roda o mundo físico, as frutas ou o J5;
- são as sementes dos testes, sem intervalo e sem replicação.

## 2. O que o E0 muda na pergunta

1. **A arbitragem pesa mais que o aprendiz.** 55% das decisões não passam pelo aprendido, e o crédito delas se perde. Nenhuma melhoria do
   aprendiz alcança essas decisões enquanto a prioridade fixa do instinto as fecha.
2. **Onde há escolha, o aprendido já age.** Ele muda um terço das escolhas, e isso satura perto do dia 6. Um aprendiz "mais forte" no
   mesmo lugar daria pouco.
3. **O crédito é imediato, e um traço cairia metade em decisões forçadas.** É a razão estrutural mais simples, ainda não testada, para o
   J1 negativo.
4. **A medida do painel e a medida causal divergem.** Antes de qualquer V3, a leitura "quem decidiu" tem de ser a sonda contrafactual,
   não o `lobo_decisivo` (V3-1).

## 3. A proposta do Matheus, item a item, contra o que já existe

A proposta tem seis mudanças, um benchmark e uma definição de individualidade. Para cada item: o que o projeto já tem, o que deu, e o que
seria novo **para o projeto** (não para a literatura).

### 3.1 Competição entre propostas no lugar da prioridade fixa

- **Hoje:** `impulsos` (`lobos.py`, ~311) roda o instinto da v1 (`policy.py`), que tem ordem fixa: `sono_exaustao`, `sono_continuar`,
  `sono_noite`, `pedido_necessidade`, `abandono`, `fome_moderada`, `tempo_livre`. As cinco primeiras devolvem um candidato só. A
  competição existe **dentro** das duas regras com escolha: os lobos somam um peso por candidato, e o sorteio é proporcional.
- **O que o E0 diz:** é o item de maior alcance. As regras forçadas são 55% das decisões; só o `sono_continuar` é 34,6%.
- **O que seria novo para o projeto:** a competição **entre** regras. As propostas das regras urgentes passam a competir no mesmo sorteio,
  com o termo do instinto como prior forte, em vez de fechar a decisão. O crédito passa a ensinar nessas decisões.
- **Literatura:** a arbitragem entre sistemas de controle por incerteza é tema de Daw, Niv e Dayan (2005), lido **só o título**: é pista,
  não suporte. O instinto como prior evoluído, com o aprendizado por cima, é a leitura de Singh et al. (2010). A partição instinto ×
  aprendido dentro do mesmo agente já existe (Hallawa et al. 2021): não é diferencial.

### 3.2 Memória episódica e crédito temporal (traços, TD(λ), options)

- **A memória de episódios (N6)** já existe (`MemoriaEpisodios`, `lobos.py`, ~515). Guarda o comer de uma fruta e o efeito no humor, e
  entra só na sub-decisão de qual fruta comer. Na validação única (`docs/RESULTADO_V2_VALIDACAO_UNICA.md`, seção 2), confirma com efeito
  pequeno: G-CAUSAL +0,028 [+0,009; +0,048].
- **O traço de elegibilidade** já existe (`traco_decisoes`, `traco_fator`). Na REVISAO-APRENDIZ (`docs/RESULTADO_V2_REVISAO_APRENDIZ.md`),
  as três janelas pioram o acerto do P3 (−0,046, −0,091, −0,124), e o traço ficou desligado. Ele não anda com os canais (T3), que o v11
  usa.
- **O cérebro B** já tinha ator-crítico com elegibilidade e não aprendeu: o aprendido mudava menos de 1% das decisões
  (`docs/RESULTADO_V2_CALIBRACAO_CEREBRO_B.md`).
- **O J1** já mostrou que o crédito imediato não ensina a procurar (seção 1.4).
- **O que seria novo para o projeto:** um traço que **pula as decisões forçadas** (o E0 mostra que metade do traço cairia nelas) e que
  ande com os canais. Options como macro-ação ("ir até um alvo") têm parente no J5, o planejador de um alvo. Um crítico com TD(λ) seria
  a terceira via, e é a que o B já tentou.
- **Literatura:** options, Sutton, Precup e Singh (1999), verificada por título e metadados, sem resumo. TD(λ): SEM FONTE na lista
  verificada.

### 3.3 A bioquímica modulando plasticidade, atenção e exploração

- **Hoje não existe:**
  - o `passo` é constante (`self.cl.passo`);
  - o `_sensibilidade_canal` (`lobos.py`, ~1362), a entrada prevista da H-R4, está sem uso e devolve S;
  - o `ConfigEmocao.modula_memoria` é `False`;
  - o mais perto é o braço P1-cw (`pesos_janela`): a falta recente de cada drive pesa o **sinal**, não o passo.
- **O que seria novo para o projeto:** a química do corpo mudando **quanto** o cérebro aprende (o passo); depois, **o quê** ele olha (a
  atenção) e **quanto** ele arrisca (a exploração).
- **Literatura e precedente:** **não é novo fora do projeto.** O Creatures já tinha redes com aprendizado hebbiano e modulação hormonal
  (Cliff e Grand 1999, resumo). Os papéis computacionais da dopamina no aprendizado por reforço estão em Montague, Hyman e Cohen (2004,
  resumo). O que o projeto pode ter de próprio é o teste com controle (seção 4.3), não o mecanismo.
- **Condição:** o metabolismo decidido antes. Hoje ele não fechou: o ponto (2, 1) não fechou, e o #327 espera a decisão. Com o
  metabolismo mudando, um efeito da modulação não se separa de um efeito do corpo (V3-6).

### 3.4 Uma rede recorrente pequena

- **Já tentado:** o cérebro B (CfC, recorrente, A2C) não aprendeu e saiu da comparação. O C (Fly-like, esparso) fecha e empata com o A:
  CC-1 +0,016 [−0,017; +0,046], CC-2 +0,036 [−0,009; +0,078] (`docs/RESULTADO_V2_COMPARACAO_CEREBROS.md`).
- **O que seria novo:** nada que o E0 peça. A recorrência dá estado interno, e o corpo químico já é um estado interno lento (leitura
  nossa). **Fica fora do V3 inicial** (V3-8).

### 3.5 Curiosidade como valor e um modelo do mundo

- **A curiosidade** já é um drive do corpo (`corpo.py`): sobe +300 por tick acordado e cai −90000 por novidade, até 2 por decisão. Só
  existe com o mundo físico e entra no sinal de crédito com peso 1 (`DRIVES_NOVOS_SINAL`). Ficou fora dos braços do plano dos drives.
- **O modelo do mundo** já existe (J5, `digilab/modelo_mundo.py`): o desfecho de comer cada tipo, o custo de andar e o mapa da comida, em
  inteiros. O planejador de um alvo soma o termo do lobo `planejamento`. A calibração do `g_plano` fecha; a validação não rodou; o
  planejador ainda não está ligado na bancada (`docs/PAINEL_V2.md`).
- **O que seria novo para o projeto:** a curiosidade medida pelo **erro de previsão do modelo do J5**, e não por um contador de novidade.
- **Literatura:** curiosidade como erro de predição, Pathak et al. (2017); como progresso de predição, Schmidhuber (2010); junto com um
  drive homeostático, Magrans de Abril e Kanai (2018, preprint). Todos lidos no resumo. Planejar com modelo aprendido: Dyna, Sutton
  (1990), só o título. Nada disso é novo.

### 3.6 Desenvolvimento individual pelo genoma

- **Já desenhado:** `docs/futuro/ecossistema_genetico.md` (EG-1 a EG-8 decididas; G0 a G5 na fase 3). Propõe um registro único com
  temperamento, espécie, corpo, paladar, prior e **plasticidade**; o aprendido nunca entra.
- **Já medido:** o E1 da v1 falhou o gate. O genoma explicou 4,9% da variância, σ²_genoma +0,0016 [−0,0007; +0,0032]
  (`docs/historico/claude/v1_pesquisa.md`).
- **A definição operacional do Matheus** (100 pets com o mesmo genoma e experiências diferentes, e o grupo inverso) é um desenho de
  normas de reação: o intercepto é o indivíduo e a inclinação é a plasticidade (Dingemanse et al. 2010). Na literatura, cerca de 52% da
  variação de personalidade animal é genética aditiva (Dochtermann et al. 2015), mas a raça explica só 9% do comportamento em cães
  (Morrill et al. 2022).
- **O que seria novo para o projeto:** o genoma regular a **plasticidade** (a modulação da seção 3.3), e não só o prior.
- **Condição:** medir a individualidade antes de o pet aprender no mundo físico tende a repetir o E1 (V3-7).

### 3.7 O benchmark "procurar comida escondida"

- **É o J1.** O mundo `fisico` (40 unidades × 12 células, 14 dias) já pede para achar comida no mapa, e já deu negativo duas vezes:
  - P0 − P1, −0,0097 [−0,0149; −0,0046] em `D_FE` (`docs/RESULTADO_V2_VALIDACAO_MUNDO.md`);
  - o alvo aprendido, −0,0063 [−0,0105; −0,0022] (`docs/RESULTADO_V2_VALIDACAO_MUNDO_ALVO.md`).
- **Recomendação:** usar o J1 como o benchmark do V3, com as mesmas medidas e uma faixa nova (V3-5). O instinto, o P1 e o alvo já têm
  número; um braço do V3 que não passe deles é o mesmo negativo.

### 3.8 Resumo

| item da proposta | já existe | deu | novo para o projeto |
|---|---|---|---|
| 1 competição | sorteio dentro de 2 regras | 55% das decisões sem escolha (E0) | **competição entre regras** |
| 2 memória e crédito | N6, o traço, o crítico do B | N6 pequeno; o traço piora; o B não aprende | o traço que pula as forçadas |
| 3 neuromodulação | nada (o passo é fixo) | — | **o passo pela química** |
| 4 recorrência | o cérebro B | não aprende | nada (fora) |
| 5 curiosidade e modelo | o drive no corpo; o J5 | o J5 sem validação | a curiosidade pelo erro do modelo |
| 6 genoma | o ecossistema genético; o E1 | 4,9% | o genoma regulando a plasticidade |
| benchmark | o J1 | negativo duas vezes | — |

## 4. O desenho do V3

### 4.1 Princípios

- **O A fica intacto.** O V3 é um conjunto de chaves desligadas por cima da `PoliticaLobos`. Desligadas, a vida do A sai byte a byte, e o
  gabarito é gravado num commit antes da mudança.
- **Só pesquisa no Python.** Nada vai à web sem a decisão do Matheus; o v11 e o porte não mudam.
- **M10:** montar todas as peças, calibrar junto, validar uma vez (`docs/ROADMAP_V2.md`, M10 e M11). Não se calibra nó a nó.
- **A calibração fica no fim**, e uma faixa que não fecha não bloqueia.
- **Nenhuma run sem plano registrado,** numa faixa reservada pedida ao coordenador.
- **O metabolismo estável antes da neuromodulação.**
- **A medida de influência é a sonda contrafactual** (TV e "mudaria sem o termo", por regra e por dia), como no E0. O `lobo_decisivo`
  fica só como descrição.

### 4.2 Os braços

Os nomes R0 a R3 evitam a confusão com os cérebros A, B e C; na proposta, são os braços A, B, C e D.

| braço | o que é | na proposta |
|---|---|---|
| **R0** | o A como está (o P1 do J1) | A |
| **R1** | R0 + a competição entre regras (3.1) | B |
| **R2** | R1 + o traço que pula as decisões forçadas e anda com os canais (3.2) | C |
| **R3** | R2 + o passo modulado pela química (3.3) | D |
| P0 | o instinto, sem aprender | o piso do J1 |

### 4.3 Controles e ablações (na validação única, não na calibração)

| controle | o que separa |
|---|---|
| **R1-congelado** (a competição aberta, sem aprender) | "abrir as regras muda o pet" × "o aprendido usa a abertura". Sem ele, um efeito do R1 pode ser só o pet dormir menos |
| **R2 sem a competição** (o traço novo sobre o A) | o traço sozinho, sem a arbitragem |
| **R3-embaralhado** (a química de outra vida, com a mesma distribuição) | o passo ligado ao estado do próprio corpo × só mais variação de passo |
| **R3-constante** (o passo fixo na média do R3) | modular × aprender mais rápido em média |
| **R3 sem a competição** e **R3 sem o traço** | as interações: a modulação depende das outras peças? |
| o E0 em cada braço | quanto o aprendido decide, por regra e ao longo da vida (descritivo) |

Uma regra de segurança fica igual em todos os braços: o `sono_exaustao` continua forçado. Sem ela, um braço pode aprender a não dormir e
morrer de cansaço, e a comparação vira de sobrevivência (V3-4).

### 4.4 O roadmap

O E0 a E6 da proposta, nesta ordem e com estas portas:

| passo | o quê | porta |
|---|---|---|
| **E0** | esta auditoria | feita (este documento) |
| **E1** | a tarefa (`docs/TAREFA_V2_V3.md`); o gabarito do A; as chaves R1, R2 e R3 desligadas, uma etapa e um PR por peça | o A byte a byte com as chaves desligadas; os testes da frente |
| **E2** | o plano de análise (`docs/PLANO_ANALISE_V2_V3.md`), commitado antes da primeira vida: predições, medidas do J1, controles da 4.3, a faixa | o Matheus aprova o plano |
| **E3** | a calibração conjunta das três peças (M10), só nas sementes dela, **depois** do metabolismo decidido | as faixas que fecham; as que não fecham ficam registradas |
| **E4** | a validação única no J1, com os controles e as ablações | roda uma vez; o negativo fica como está |
| **E5** | a individualidade (100 pets com o mesmo genoma, e o inverso), só se o E4 mostrar um braço que aprende no mundo | um plano próprio, ligado ao ecossistema genético |
| **E6** | a curiosidade pelo erro do modelo do J5 e, se o J5 validar, a ligação com o planejador | um plano próprio |

A rede recorrente (3.4) não está no roadmap. A web só entra se o Matheus decidir, depois do E4.

### 4.5 As predições (PROPOSTAS, a registrar no plano do E2)

- **V3-P1:** no R1, a fração de decisões sem escolha cai de 55% para perto da do `sono_exaustao` (2,2% no E0), e o aprendido decide mais
  que os 15,6% do A.
- **V3-P2:** no J1, o R2 tem `D_FE` menor que o R0. Se não tiver, a razão do J1 não é a janela de crédito.
- **V3-P3:** o R3 difere do R3-embaralhado e do R3-constante. Se não diferir, a modulação é só um passo diferente.
- **V3-P4:** o R1-congelado não explica o efeito do R1.

Nenhum tamanho de efeito aqui: o Δ mínimo e o N saem do plano do E2, pelo poder simulado, como na K2.

## 5. Os riscos

| risco | o que fazer |
|---|---|
| O R1 abre as regras e o pet piora por perder o instinto, não por aprender | o R1-congelado e o `sono_exaustao` forçado |
| A modulação confundida com o metabolismo | o E3 só depois do metabolismo decidido; o R3-embaralhado |
| Um terceiro negativo no J1 | fica registrado (gate que falha não para a V2); o E0 por braço diz onde o aprendido age |
| O teto de pesos (990 de 1000 no degrau 1) | o R1 abre mais tabelas; medir antes o custo do replay, como pede o `docs/DECISAO_V2_TETO_PESOS.md` |
| O rótulo | "competição", "curiosidade" e "modulação" são nomes de mecanismo; nenhum resultado vira "o pet sente" ou "o pet pensa" |
| Alegar novidade | o Creatures já modulava o aprendizado por hormônios (3.3); o texto diz isso sempre que a modulação aparecer |

## 6. Decisões para o Matheus

Todas PROPOSTAS; a recomendação vem primeiro.

| # | decisão | recomendação | as outras opções | custo de errar |
|---|---|---|---|---|
| **V3-1** | a leitura "quem decidiu" | **a sonda contrafactual** (TV e "mudaria sem o aprendido") nos documentos novos. O painel DigiBrain ganha "o aprendido mudou esta decisão" numa etapa futura do porte, com a conta feita no Python antes | manter o `lobo_decisivo` | baixo para trocar. Alto para manter: o painel mostra impulsos como maior em 99,95% das escolhas do atencioso, e o aprendido muda 24,6% delas |
| **V3-2** | onde o V3 vive | **só na pesquisa no Python,** em chaves desligadas sobre o A, sem tocar o v11 | um cérebro novo do zero; direto na web | médio: um cérebro do zero perde a comparação com o A; na web, quebra a paridade e o porte |
| **V3-3** | a primeira peça | **a competição entre regras (R1):** a de maior alcance pelo E0, e não depende do metabolismo | a neuromodulação primeiro; o crédito primeiro | médio: a modulação primeiro mexe só nos 45% com escolha e espera o metabolismo; o crédito primeiro repete a REVISAO |
| **V3-4** | a forma da competição | **as regras urgentes viram prior forte num sorteio comum, com o `sono_exaustao` forçado** | vencedor-leva-tudo por urgência; arbitragem por incerteza (só pista na literatura) | médio: sem a regra de segurança, um braço pode morrer de cansaço, e a comparação vira de sobrevivência |
| **V3-5** | o benchmark | **o J1,** com as mesmas medidas e faixa nova | um mundo novo de "comida escondida" | alto para o mundo novo: outra calibração, e os números do P0, do P1 e do alvo deixam de servir |
| **V3-6** | quando a neuromodulação | **depois do metabolismo decidido (#327 e o ponto do corpo),** só o passo, com o R3-embaralhado e o R3-constante | modular já; modular também a atenção e a exploração | alto: com o corpo mudando, o efeito da modulação não se separa do efeito do metabolismo |
| **V3-7** | a individualidade (100 × genoma) | **depois do E4,** num plano próprio ligado ao ecossistema genético | medir já | médio: medir antes de o pet aprender no mundo tende a repetir o E1 (4,9%) e gasta uma faixa |
| **V3-8** | a rede recorrente e a curiosidade nova | **fora do V3 inicial;** a curiosidade volta no E6 se o J5 validar | as duas já no R3 | médio: o B recorrente já não aprendeu, e peças demais no mesmo braço encarecem a ablação |

## 7. Referências

Só as verificadas (`docs/referencias/*.csv`, a skill `literatura-digilab`), com quanto foi lido. A leitura de conteúdo foi sobre
metadados e resumo, não sobre o texto completo.

| referência | DOI | quanto foi lido | o que sustenta aqui |
|---|---|---|---|
| Cliff e Grand (1999). The Creatures global digital ecosystem. Artificial Life 5(1) | `10.1162/106454699568683` | resumo | redes com aprendizado hebbiano e modulação hormonal num pet artificial: a modulação não é nova |
| Grand e Cliff (1998). Creatures: entertainment software agents with artificial life. AAMAS 1(1) | `10.1023/a:1010042522104` | resumo | a referência canônica do Creatures |
| Montague, Hyman e Cohen (2004). Computational roles for dopamine in behavioural control. Nature 431 | `10.1038/nature03015` | resumo | os papéis computacionais da dopamina no aprendizado por reforço (pista para a 3.3) |
| Sutton, Precup e Singh (1999). Between MDPs and semi-MDPs. Artificial Intelligence 112 | `10.1016/s0004-3702(99)00052-1` | título e metadados | o formalismo de options |
| Sutton (1990). Integrated Architectures for Learning, Planning, and Reacting… (Dyna) | `10.1016/b978-1-55860-141-3.50030-4` | só o título | a existência da linha; nenhuma afirmação de conteúdo |
| Daw, Niv e Dayan (2005). Nat Neurosci | `10.1038/nn1560` | só o título | pista: a arbitragem por incerteza entre sistemas |
| Singh, Lewis, Barto e Sorg (2010). Intrinsically motivated RL: an evolutionary perspective. IEEE TAMD 2(2) | `10.1109/tamd.2010.2051031` | resumo | o instinto como prior evoluído |
| Hallawa et al. (2021). Evo-RL: evolutionary-driven reinforcement learning. GECCO'21 Companion | `10.1145/3449726.3459475` | resumo | a partição instinto × aprendido no mesmo agente já existe |
| Pathak et al. (2017). Curiosity-driven exploration by self-supervised prediction. CVPRW | `10.1109/cvprw.2017.70` | resumo | a curiosidade como erro de predição |
| Schmidhuber (2010). Formal theory of creativity, fun, and intrinsic motivation. IEEE TAMD 2(3) | `10.1109/tamd.2010.2056368` | resumo | a curiosidade como progresso de predição |
| Magrans de Abril e Kanai (2018). Curiosity-driven RL with homeostatic regulation | `arXiv:1801.07440` | resumo (preprint) | a curiosidade e o drive homeostático no mesmo agente |
| Dingemanse et al. (2010). Behavioural reaction norms. TREE 25(2) | `10.1016/j.tree.2009.07.013` | resumo | o formalismo da individualidade (intercepto e inclinação) |
| Dochtermann, Schwab e Sih (2015). Proc R Soc B | `10.1098/rspb.2014.2201` | resumo | ~52% da variação de personalidade animal é genética aditiva |
| Morrill et al. (2022). Science 376 | `10.1126/science.abk0639` | resumo | a raça explica 9% do comportamento em cães |

**SEM FONTE:** TD(λ); "cognição incorporada" como quadro teórico; a afirmação de que um organismo pequeno pode ter comportamento mais rico
que as suas regras explícitas; toda leitura marcada "nossa" neste documento.
