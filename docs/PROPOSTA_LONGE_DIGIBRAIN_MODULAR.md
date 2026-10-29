# Proposta — a falha do DigiBrain modular no lugar "longe" (2026-10-29)

Autor: o C (Claude Code, Opus 5.5), a pedido do Gerente (relato do Gerente, 2026-10-29), pela decisão do Matheus de tratar **o longe
primeiro** e o hábito depois. **Status: PROPOSTA, só papel.** Nenhum código, nenhuma vida, nenhuma semente, nenhuma faixa reservada.

**As regras deste documento:**
- **Todo número sai de um artefato no git,** com o caminho ao lado:
  - `artifacts_v2_digibrain_prototipo/descritivo_reavaliacao/descritivo.json` (o #433), chamado abaixo de **[desc]**;
  - `artifacts_v2_digibrain_prototipo/reavaliacao/resultado.json` (o #432), chamado de **[res]**, no bloco `descritivos_conserto`, salvo
    onde dito.
- **As contas à mão** saem das constantes de `digilab/config.py` e das fórmulas do motor, como a tabela do n_min do adendo 3 (A3.2).
- **Todo valor novo é PROPOSTO e SEM FONTE.** Nenhuma alegação de novidade, de prontidão ou de superioridade do modular sobre o A. O A11
  aparece só onde ajuda a ler o cenário, sem comparação de mérito.
- **O que é dado e o que é hipótese** fica separado em cada item: **[DADO]** é o que os artefatos mostram; **[CÓDIGO]** é leitura de
  código, sem execução; **[HIPÓTESE]** é aposta nossa, a medir.

## 0. Em uma página

- **O longe falha em todos os braços do modular, por igual.** Por episódio, no longe: o M0 (só o inato) fica em 0,476; o M3\* (tudo
  ligado), em 0,434. Nenhum módulo de hoje move o longe. O cheiro inato e a intenção no cheiro também não (o G-DX no longe: +0,013 e
  +0,001, os dois com o IC95 contendo 0). **A falha não está num módulo que faltou ligar.**
- **Três causas prováveis, nesta ordem de evidência:**
  1. **o cenário e a medida.** O dono põe 7,8 rações elegíveis por episódio no longe, cada uma a 20–30 células do pet, numa direção
     sorteada. Por isso **a taxa por ração no longe tem um teto perto de 0,13,** mesmo que todo episódio fechasse;
  2. **a percepção.** Fora da visão (6 células), o único guia é o campo do cheiro. O campo é a soma de cones lineares, e com várias rações
     espalhadas a direção dele pode não apontar para ração nenhuma [CÓDIGO; HIPÓTESE a medir];
  3. **a decisão.** Uma viagem de 20–30 células pede de 6 a 8 decisões seguidas andando. O sorteio refaz a escolha a cada decisão, e a
     troca de meta no longe é cerca de 4 vezes a do comedouro [DADO]. Quem vence as trocas não está medido.
- **O que falta medir** (seção 2): a direção do cheiro contra a das rações, quem vence cada troca e o andado contra a distância, por
  replay das vidas da reavaliação já gravadas, sem vida nova.
- **Quatro opções** (seção 3): L-1, o cheiro por fonte (percepção, no motor); L-2, o compromisso da viagem (decisão, no cérebro); L-3, o
  lugar lembrado pela consistência (memória, no cérebro); L-4, o cenário e a medida (não muda o pet).
- **A recomendação** (seção 4): **medir primeiro (a etapa L0),** com uma regra escrita antes que leva a L-1, a L-2 ou às duas. Sem a
  medição, **L-2 primeiro,** que não toca o motor nem o A.

## 1. O diagnóstico do longe

### 1.1 O que os artefatos mostram

**O longe contra os outros lugares, no M3\*** (200 vidas por lugar; [desc], `1_episodio_contra_racao_M3.por_lugar`):

| | comedouro | perto | longe |
|---|---|---|---|
| a taxa por episódio (a média das vidas) | 0,816 | 0,958 | **0,434** |
| a taxa por ração (a média das vidas) | 0,429 | 0,688 | **0,081** |
| rações elegíveis por episódio | 3,79 | 1,92 | **7,81** |
| rações fechadas por episódio fechado | 1,25 | 1,22 | 0,98 |
| as rações elegíveis nunca na visão na janela | 7 % | 0 % | **82 %** |
| a menor distância à ração na janela, média por vida (células) | 1,6 | 0,9 | **13,7** |
| episódios em que a oferta muda na janela | 25 | 1 | **280** |
| os fins das intenções por vida: meta · trocou · achou | 69,9 · 17,7 · 11,9 | 79,0 · 12,8 · 7,1 | 66,2 · **75,3** · 17,6 |
| as buscas pelo cheiro por vida: achou · trocou · sumiu · desistiu | 11,9 · 2,6 · — · — | 7,1 · 0,1 · — · — | 17,6 · **25,7** · 1,7 · 0,0 |
| a latência até comer, nos episódios vencidos (mediana, em decisões desde a abertura) | 16 | 13 | **28** |
| refeições de ração por dia, por vida | 3,83 | 3,28 | 2,42 |

**O episódio pela distância da ração mais próxima na abertura (d0)** (o M3\*; [desc], `episodios_por_distancia`):

| d0 | comedouro: n, taxa | longe: n, taxa |
|---|---|---|
| na visão (até 6 células) | 1 565, 0,91 | 433, 0,84 |
| só no cheiro (de 6 a 24 células) | 1 736, **0,74** | 1 629, **0,41** |
| além do cheiro (mais de 24 células) | 12, 0,00 | 441, 0,21 |

**O longe em todos os braços** (a taxa por episódio, a média das vidas; [res]):

| M0 | M1 | M2 | M3\* | M3-sp | M3\*−inato | M3\*−intencao | M3-420 | M4 |
|---|---|---|---|---|---|---|---|---|
| 0,476 | 0,445 | 0,465 | 0,434 | 0,413 | 0,421 | 0,433 | 0,427 | 0,427 |

- Sem IC: é descritivo. **Os contrastes com IC que existem no longe** são os do G-DX (`docs/RESULTADO_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md`,
  seção 8): o cheiro inato, +0,0129 [−0,0132; 0,0390]; a intenção no cheiro, +0,0005 [−0,0204; 0,0214].
- **O A11 no longe** não ajuda a ler: a taxa agregada (0,601) e a média das vidas (0,337) discordam, porque ele tem menos episódios e
  muito mais rações por episódio ([res], `A11|longe`). Fica fora das contas desta proposta.

**O sono e a memória no longe** ([res], o campo `cheiro.sono_na_janela` e o bloco `visitas`):
- **o sono não é maior no longe:** dormir ocupa 0,447 das decisões na janela no longe, contra 0,493 no comedouro (o M3\*);
- **a memória manda o pet a lugares vazios:** no M3\*, 6 939 visitas ao lugar lembrado no longe (34,7 por vida) contra 3 264 no comedouro
  (16,3 por vida); 6 932 delas saem vazias pela DX-1.
  - **A ressalva:** no comedouro também saem todas vazias (3 264 de 3 264), e lá a memória ajuda (o G-ABLA-MEM rejeita, +0,136). A
    "vazia" da DX-1 não separa a visita que ajuda da que atrapalha.

### 1.2 Cenário, percepção e decisão: o que os dados sustentam e o que é hipótese

**O cenário (o dono e a distância):**
- **[DADO] O dono põe muitas rações por episódio no longe:** 7,81 elegíveis por episódio, contra 3,79 no comedouro. Cada uma cai a 20–30
  células da posição do pet naquele momento, numa de 16 direções (`DonoComLugar.lugar`, `digilab/mundo.py:1957-1970`;
  `config.py:1785-1786`).
  As rações ficam no chão por 1 440 minutos (`maduro_racao_min`, `config.py:1776`) e se acumulam em volta do pet.
- **[DADO + CONTA] A taxa por ração no longe tem um teto.** Pela identidade do #433 (taxa por ração = rações fechadas por episódio fechado
  × taxa por episódio × episódios por ração elegível), com a taxa por episódio em 1 e as outras duas parcelas como estão no longe (0,979 e
  0,128, [desc] `identidade`), a taxa por ração chegaria a cerca de **0,13**. **Nenhuma vida do longe passa de 0,5 por ração porque o
  cenário não deixa,** e não só porque o pet falha. Uma mudança no pet tem de ser julgada **por episódio** no longe.
- **[CÓDIGO] O longe do jogo é outro:** no jogo, "longe" é um lugar nomeado a 20 células, para o lado com mais espaço, sempre o mesmo
  para a mesma posição (`web/app/src/telas/pet/vistaMundo.ts:42`; o registro "2026-10-24 — MVP-ETAPA2"). Na pesquisa, o longe sorteia
  distância e direção a cada ração. **O longe da pesquisa é mais duro que o do jogo:** a 20 células, a ração do jogo está sempre dentro
  do cheiro.

**A percepção (a visão e o cheiro):**
- **[DADO] Fora da visão, o pet acha pouco.** 82 % das rações elegíveis do longe nunca entram na visão na janela. Um episódio que abre com
  a ração na visão fecha 0,84 no longe; só no cheiro, 0,41; além do cheiro, 0,21.
- **[DADO] Estar no cheiro basta no comedouro, e não no longe:** a mesma faixa de d0 (de 6 a 24 células) fecha 0,74 no comedouro e 0,41 no
  longe. A distância dentro da faixa, a memória e o número de rações no chão diferem entre os dois lugares, e os artefatos não os separam.
- **[CÓDIGO] Como o cheiro guia** (`campo_em` e `direcao_do_campo`, `digilab/mundo.py:242-276`; `_alvo_cheiro`, `mundo.py:1340-1342`):
  - o campo num ponto é a soma, sobre todas as comidas maduras a menos de R = 24 células, de A × (R − d) // R, com A = 64 para a ração;
  - a direção é a de maior campo entre 8 vizinhos a 1 célula, com o empate pela ordem fixa;
  - o alvo `cheiro` fica 8 células nessa direção, e o cérebro só sabe se há direção (`ha_cheiro`, `digilab/digibrain/sens.py:96`), nunca
    qual (o G-SEM-DIRECAO).
- **[HIPÓTESE, pela conta do campo] Com várias rações espalhadas, a direção pode não levar a ração nenhuma.**
  - Cada cone cai com a mesma inclinação A/R. Entre duas rações dentro do raio, andar para uma aumenta a parcela dela tanto quanto diminui
    a da outra: **ao longo do segmento entre as duas, o campo é constante.** Com as duas num ângulo, o gradiente aponta entre elas.
  - Com o arredondamento de cada parcela, a direção nesses trechos sai de diferenças de 1 e da ordem fixa do empate, e não da ração mais
    perto.
  - No comedouro, as rações caem no mesmo ponto, e as parcelas somam na mesma direção. Isso combina com a diferença acima (0,74 contra
    0,41), mas não a prova.
  - **Contra a versão extrema** (o campo plano, sem direção): a busca acaba por "sumiu" só 1,7 vez por vida no longe [DADO]. Se a direção
    some, é pouco. O que sobra a medir é **para onde** ela aponta.

**A decisão (a troca de meta, a persistência e o explorar):**
- **[DADO] As trocas:** no longe, as intenções acabam trocadas 75,3 vezes por vida, contra 17,7 no comedouro; 25,7 buscas pelo cheiro por
  vida acabam trocadas, contra 17,6 que acham a ração.
- **[DADO] A intenção no cheiro e a persistência não mudaram o longe:** o G-DX-INTENCAO no longe dá +0,0005 [−0,0204; 0,0214]. A
  persistência decide 0,35 % das decisões do M3\* (a G-PESA, `RESULTADO`, seção 8).
- **[CÓDIGO] A viagem longa pede a mesma escolha muitas vezes:** de 20 a 30 células são de 6 a 8 decisões andando (A3.2). O sorteio é
  refeito em cada decisão (`docs/ESPEC_DIGIBRAIN_MODULAR.md`, seção 4.7); o reflexo do sono fica fora do sorteio e escolhe dormir quando a
  energia cai abaixo de `λ_sono`. Andar gasta energia (`custo_energia_por_subunidade`, `config.py:1746`).
- **[HIPÓTESE] Quem quebra a viagem** é uma destas, ou uma soma delas, e os artefatos não separam:
  - **(a)** o reflexo do sono no meio da viagem;
  - **(b)** outra unidade que vence o sorteio (chamar o dono, explorar o lugar lembrado, vagar);
  - **(c)** uma ração nova posta pelo dono em outra direção, que vira outra unidade (a oferta muda em 280 episódios do longe [DADO]).
- **[DADO] O explorar pela memória no longe vai a lugares vazios** 34,7 vezes por vida (acima). No longe, o lugar de cada refeição é
  sorteado de novo a cada ração, e o lugar lembrado quase nunca é o da próxima. É uma unidade a mais disputando a viagem. Contra ela: o
  M2, sem memória, fica em 0,465 no longe, perto do M3\* (0,434), sem IC.

**O que se pode dizer agora:**
- **sustentado:** a falha do longe não vem de um módulo que pesa de menos. Ela aparece com o inato sozinho, e nenhum braço a move. A taxa
  por ração no longe tem um teto de cenário;
- **provável, a medir:** a percepção fora da visão (para onde o cheiro aponta com várias rações) e a continuidade da viagem (quem a
  quebra);
- **não sustentado:** que o sono, sozinho, seja a causa. A fração de sono na janela não é maior no longe.

## 2. O que falta medir (a etapa L0, sem vida nova)

**Rejogando as vidas da reavaliação** (as 7 200 da 66xxx estão em disco, na worktree `v2-modular-reavaliacao`, fora do git). Rejogar não
é vida nova: mesmo log, mesmo commit `988cf0d`, o G1 conferindo que o replay refaz as medidas gravadas. Mas toca a faixa da avaliação, e
por isso é decisão do Matheus, como no #422 (seção 3.2). Só os braços M0 e M3\*, nas 12 células.

| # | a medida (PROPOSTA) | de onde sai | a pergunta |
|---|---|---|---|
| **M-L1** | em cada decisão com ração madura a menos de R e nenhuma comida vista: o ângulo entre a direção do cheiro e a direção da ração mais próxima; quantas rações dentro de R; a fração com a direção a mais de 45° de toda ração | o estado do motor no replay | **a percepção:** o cheiro leva a uma ração? |
| **M-L2** | em cada fim "trocou" de uma intenção de comer ou de busca: a unidade que venceu, e se foi o reflexo do sono | o registro da decisão no replay | **a decisão:** quem quebra a viagem? |
| **M-L3** | em cada episódio do longe: as decisões acordado na janela, quantas andaram, e o andado líquido em direção à ração que fechou (ou à mais próxima) contra o n_min(d0) | o motor e o registro | o pet andou o bastante? |
| **M-L4** | a distribuição de d0 dentro da faixa do cheiro, por lugar | o motor | a diferença 0,74 × 0,41 é de distância ou de lugar? |
| **M-L5** | qual ração fecha cada episódio | o motor | a questão aberta do #433 |
| **M-L6** | o número de rações maduras no chão a menos de R, por decisão, por lugar | o motor | quanto o campo é soma de várias fontes |

- **O script fica só de leitura,** com saída em `artifacts_v2_digibrain_prototipo/`, como o do #422 e o do #433. Nenhuma medida entra em
  gate.
- **A regra de escolha, escrita antes do replay** (os limiares são PROPOSTOS, SEM FONTE):
  - **a percepção pesa** se, no longe, a direção do cheiro fica a mais de 45° de toda ração em ao menos 25 % das decisões do M-L1;
  - **a decisão pesa** se, no longe, ao menos metade das buscas trocadas (M-L2) é quebrada pelo reflexo do sono ou por outra unidade com a
    ração ainda dentro de R;
  - **as duas, as duas;** nenhuma das duas, a proposta volta ao Gerente com o M-L3 e o M-L4.

## 3. As opções

Cada uma fica atrás de uma chave ou subchave desligada, com a vida de hoje byte a byte e o gabarito gravado antes, como toda mecânica
nova. **Nenhuma muda o `engine.py`.** O corpo não muda em nenhuma, e o código do A também não.

### L-1, o cheiro por fonte (a percepção, no motor)

- **O mecanismo:** a direção do cheiro passa a apontar para **a fonte de maior parcela** (a ração que, sozinha, cheira mais forte no
  pet), em vez do gradiente da soma. A intensidade que o cérebro lê não muda; só a direção do alvo `cheiro`.
- **Onde entra:** no mundo do motor (`direcao_do_cheiro` e `_alvo_cheiro`, `digilab/mundo.py`), atrás de uma chave nova da `ConfigMundo`,
  desligada; o espelho em `web/app/motor/mundo.ts` depois, com o G-PAR.
- **O que muda no jogo:** o pet com fome segue o cheiro da ração mais forte, e não o meio entre várias.
- **O risco para o comedouro e o perto:** baixo. No comedouro, as rações ficam no mesmo ponto, e a fonte mais forte e a soma apontam
  igual. No perto, a ração está na visão.
- **O custo:** médio. O motor Python, o gabarito do mundo (G2), o espelho TS e o G-PAR. **A mudança fica só na direção do cheiro da
  comida** (`direcao_do_cheiro`): o `campo_em` serve também ao cheiro de cada pet, ao rastro e ao som dos dois pets (`mundo.py:242-244`),
  e esses não mudam.
- **O que exige:** **muda o motor** (o mundo, não o `engine.py`). **Muda o mundo do A11 também,** quando ligada: a comparação com o A
  segue pareada, mas o A passa a viver noutro mundo. **Precisa da decisão explícita do Matheus.**
- **O que não resolve:** a ração além de 24 células (18 % dos episódios do longe abrem assim) e a viagem quebrada no meio.

### L-2, o compromisso da viagem (a decisão, no cérebro)

- **O mecanismo** (PROPOSTO, SEM FONTE), duas partes na mesma subchave:
  - **(a) a histerese:** com uma intenção de comer ou de busca em curso e a urgência da fome acima do limiar de busca, outra unidade só
    vence se o peso dela passar o da intenção por uma margem m (PROPOSTA: m = S/2). O sorteio continua com um `u` por decisão, e a
    contagem da rng não muda;
  - **(b) a intenção que sobrevive ao sono:** quando o reflexo do sono interrompe a viagem, a intenção fica suspensa, e não trocada. Ao
    acordar, ela volta com o compromisso C de antes, se a fome continuar acima do limiar e houver cheiro ou a comida vista.
- **Onde entra:** só no pacote `digilab/digibrain/` (o M-ESTADO e o M-ARB), atrás de uma subchave nova da `ConfigDigibrain`, desligada.
  O motor não muda.
- **O que muda no jogo:** o pet que sai atrás da comida longe vai até ela, mesmo com um cochilo no caminho.
- **O risco para o comedouro e o perto:** médio. A histerese pode prender o pet numa meta errada, sobretudo se L-1 for necessária e não
  estiver ligada: o pet persiste numa direção do cheiro que não leva a ração nenhuma. No perto, as viagens são de 0 a 2 decisões, e a
  histerese quase não age.
- **O custo:** baixo no Python (dois módulos do pacote e os testes), depois o espelho TS com o G-PAR.
- **O que exige:** nada fora do cérebro modular.
- **A relação com a espec:** é a persistência que a espec já previa (a seção 4.4), mais forte e só na viagem. A alternativa neural é o
  acumulador com inibição mútua da PE-5: a fonte afirma a escolha como acumulação com vazamento e competição entre unidades (Usher e
  McClelland 2001, `10.1037/0033-295x.108.3.550`, VERIFICADA, resumo). **Leitura do Digilab:** a histerese é uma versão discreta dessa
  competição, sem a fonte para o número m.

### L-3, o lugar lembrado pela consistência (a memória, no cérebro)

- **O mecanismo** (PROPOSTO, SEM FONTE): o valor de um lugar lembrado passa a ser multiplicado pela consistência espacial das últimas
  refeições, a fração dos últimos n episódios de consumo que caíram a menos de R_lugar daquele lugar (PROPOSTO: n = 4). Onde a comida
  muda de lugar a cada vez (o longe da pesquisa), o lugar perde peso. Onde ela volta ao mesmo ponto (o comedouro), nada muda.
- **Onde entra:** só no M-MEM (`digilab/digibrain/mem.py`), atrás de uma subchave nova, desligada.
- **O que muda no jogo:** o pet deixa de ir a lugares onde a comida não volta.
- **O risco para o comedouro e o perto:** médio no comedouro. O G-ABLA-MEM (+0,136) mora lá, e a consistência tem de ficar alta para o
  ganho não cair. No perto, a memória quase não age.
- **O custo:** baixo, no M-MEM, com o espelho TS.
- **O que exige:** nada fora do cérebro modular.
- **O que não resolve:** a percepção e a viagem. Ela só tira uma unidade da disputa. O M2 sem memória fica perto do M3\* no longe, então
  o ganho esperado é pequeno.

### L-4, o cenário e a medida (não muda o pet)

- **O que é:**
  - **(a)** declarar, no plano, que **a taxa por ração no longe não informa** (o teto perto de 0,13, seção 1.2) e ler o longe só por
    episódio;
  - **(b)** uma célula descritiva **"longe do jogo"**: a 20 células, para o lado com mais espaço, como `vistaMundo.ts:42`, ao lado do
    longe da pesquisa.
- **Onde entra:** no plano e no orquestrador (o `DonoComLugar` ganharia um estilo novo, e a chave fica na bancada). O pet não muda.
- **O que muda no jogo:** nada.
- **O risco:** **ler um número melhor como um pet melhor.** A célula nova é mais fácil por construção (sempre dentro do cheiro). Ela não
  conserta nada; só mostra quanto do longe é do sorteio da pesquisa.
- **O custo:** baixo.
- **O que exige:** mudar o `DonoComLugar` (`digilab/mundo.py`), que é do mundo da pesquisa. Atrás de um estilo novo, sem mudar os três de
  hoje.

### A comparação

| | onde | muda o motor? | muda o mundo do A11? | risco no comedouro e no perto | custo | o que resolve |
|---|---|---|---|---|---|---|
| **L-1** | percepção | **sim** (o mundo) | **sim**, ligada | baixo | médio (motor, TS, G-PAR) | o cheiro que não leva a ração |
| **L-2** | decisão | não | não | médio (prender na meta errada) | baixo | a viagem quebrada |
| **L-3** | memória | não | não | médio no comedouro | baixo | uma unidade a menos na disputa |
| **L-4** | cenário e medida | não (o dono da pesquisa) | não | nenhum no pet | baixo | a leitura, não o pet |

## 4. A recomendação

**Medir primeiro (a etapa L0, seção 2), e escolher pela regra escrita lá.** Junto com a L0, **a L-4 (a), escrita no plano já:** o longe se
lê por episódio, e a taxa por ração dele não informa.

- **Se o Matheus preferir não rejogar a 66xxx:** **L-2 primeiro.** Ela não toca o motor nem o mundo do A, é barata, e ataca o que os dados
  já mostram com clareza (as trocas, 4 vezes as do comedouro). L-1 fica para depois, se L-2 não mover o longe.
- **L-3 só depois de L-1 ou L-2,** e se a medida de mecanismo mostrar que as visitas ao lugar lembrado quebram viagens (o M-L2).
- **A L-4 (b), a célula "longe do jogo",** só como descritiva, se o Matheus quiser ver o longe do produto. Nunca como conserto.

**O custo de errar:**

| se | o que se perde |
|---|---|
| fazer L-2 sem medir, e a causa for o cheiro (L-1) | a histerese prende o pet numa direção que não leva a ração; o longe pode piorar, e o comedouro também, se o pet persistir na meta errada; uma rodada de calibração e de piloto gasta |
| fazer L-1 sem medir, e a causa for a viagem (L-2) | o motor, o TS e o mundo do A mudam por um ganho que não vem; o G-PAR e os gabaritos refeitos à toa |
| medir (a L0) | uma etapa de replay, de leitura, com o custo de rejogar 1 200 vidas (os dois braços nas 12 células), e a faixa 66xxx tocada (não reusada) |
| não fazer a L-4 (a) | uma melhora real no longe sai invisível na taxa por ração, que tem teto de cenário |

## 5. Como seria avaliada depois (só o esboço)

Nada aqui é reservado nem decidido; cada passo volta ao Matheus antes de rodar.

- **O plano:** um adendo novo ao `docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md`, ou um plano próprio, commitado antes de qualquer
  vida, com:
  - **a pergunta:** a mudança escolhida aumenta o fechamento **por episódio** no longe, sem piorar o comedouro e o perto?
  - **os braços:** o M3\* de hoje e o M3\* com a mudança (M3\*+L); o M0 com a mudança, para separar a mudança do aprendizado; com L-1,
    também o A11 no mundo novo, só descritivo;
  - **as células:** as 12 de hoje, mais a "longe do jogo" se a L-4 (b) entrar, descritiva;
  - **a medida primária:** o fechamento por episódio no longe (a média das unidades), como estimativa, na linha do adendo 4 (o IC pelo t
    sobre as unidades);
  - **a segurança:** a não inferioridade do fechamento por episódio no comedouro e no perto, com margens PROPOSTAS no plano;
  - **as medidas de mecanismo:** as M-L1 a M-L3 nos braços novos, descritivas;
  - **a taxa por ração no longe:** relatada, com o teto declarado (L-4 (a)).
- **A calibração:** só os valores novos (o m da L-2; nada na L-1, que não tem número novo; o n da L-3), nas sementes de calibração de uma
  faixa nova, com no máximo três rodadas, como o adendo 3.
- **O piloto e a avaliação:** o piloto para o K; a avaliação roda uma vez, numa faixa nova pedida ao coordenador quando o plano existir.
  **Nenhuma faixa é reservada agora.**
- **A web:** só depois, com o espelho TS e o G-PAR. Com L-1, o espelho do mundo também.

## 6. A relação com o hábito (o P2)

**O que se sabe** (`RESULTADO`, seção 9.2; [desc] `2_habito`):
- o hábito "ao contrário" (M2 − M1 no índice "ganhou, fica") mora no longe, com o atencioso e o incoerente;
- dentro do longe, mora no **explorar:** depois de um r positivo do explorar, o M1 repete +0,056, e o M2, −0,021. O sinal é o mesmo nas
  três runs.

**O que se espera, se o longe melhorar** ([HIPÓTESE], descritiva, sem gate):
- **Hoje,** no longe, a busca termina trocada mais vezes do que acha a ração (25,7 contra 17,6 por vida), e só cerca de 11 % das buscas
  que acham terminam em refeição pela opção composta ([res], `M3|longe`, `cheiro.frac_achou_com_refeicao`). O P2 recebe, no explorar,
  sobretudo opções sem refeição, com o custo do andar.
- **Com o longe melhor,** mais buscas terminam em refeição, e a opção composta leva o r da refeição ao começo da busca. **Espera-se que o
  M2 − M1 no explorar do longe suba para perto de zero ou acima.**
- **Se o longe melhorar e o M2 − M1 no longe continuar negativo,** o hábito ao contrário não é efeito do longe. Ele volta à frente do
  hábito: a H-P2a, um índice que cai quando o hábito funciona, ou o crédito, a DX-6, que hoje está fora.
- **Por isso a ordem do Matheus ajuda:** consertar o longe primeiro separa as duas explicações do hábito.

## 7. O que precisa do Matheus

Todas PROPOSTAS, com a recomendação primeiro.

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| **PL-1** | a etapa L0: rejogar as vidas da 66xxx (os braços M0 e M3\*) para as medidas M-L1 a M-L6, com a regra de escolha da seção 2 | **sim** | sem medir, a escolha entre L-1 e L-2 é aposta; com o replay, a faixa da avaliação é tocada (não reusada) |
| **PL-2** | a opção | **a que a regra da L0 apontar;** sem a L0, **L-2** | L-2 com a causa no cheiro: a histerese prende na meta errada; L-1 com a causa na viagem: o motor e o mundo do A mudam à toa |
| **PL-3** | a L-4 (a): o longe lido só por episódio, e a taxa por ração do longe declarada sem informação | **sim, já no próximo plano** | não declarar: uma melhora real fica invisível no teto de 0,13 |
| **PL-4** | a L-4 (b): a célula "longe do jogo", descritiva | **não agora;** só se o Matheus quiser ver o longe do produto | ler a célula mais fácil como pet melhor |
| **PL-5** | se a L-1 for escolhida: mudar o mundo do motor, com o A11 vivendo no mundo novo nos braços dela | **só com a evidência do M-L1** | sem evidência: o baseline muda de mundo por uma hipótese |
