# O gosto visual do pet: ver uma tela, gostar de umas imagens mais que de outras, e uma medida para isso

Status (2026-11-11): **PROPOSTO**. Pedido do Matheus depois da busca bibliográfica de 2026-11-10. Não autoriza implementação: as
decisões GV-1 a GV-14 (seção 10) são dele. A exceção é o protótipo P0 no jogo web (seção 14), que o Matheus pediu antes da revisão da
espec. A frente é a `docs/TAREFA_V3_GOSTO_VISUAL.md`. Nenhum código, nenhuma faixa, nenhuma vida,
nenhum plano de análise.

**O pedido:** o pet observa a tela compartilhada (ou uma TV dentro do jogo) e forma um gosto visual próprio, em parte de nascença e em
parte aprendido.

**Regras deste documento:**
- **a fonte é a nota do vault** `DigiLab — Revisão de escopo/BUSCA_GOSTO_VISUAL_2026-11-10.md` (56 referências conferidas por DOI e
  resumo, com os rótulos [sem resumo] e [resumo parcial] dela). Elas ainda **não** estão em `docs/referencias/`; a etapa GV0 as põe lá
  (GV-12). Onde a nota não tem fonte, este documento escreve SEM FONTE;
- todo número novo é PROPOSTO;
- **nenhuma alegação de novidade.** A busca não achou um agente que forme gosto visual a partir da tela do usuário (nota, seção 7), e
  isso só quer dizer que a busca não achou. Um agente artificial com interesse visual por padrões já existe (Saunders e Gero 2001,
  `10.52842/conf.caadria.2001.345`), e um agente que aprende preferências sem recompensa externa também (Sajid et al. 2022,
  arXiv:2207.13699, preprint);
- nada aqui diz que o pet sente prazer (F2, `docs/DEFINICOES_FRUTAS_V2.md`, seção 2.2): os nomes são de estímulo, de registro, de escolha
  e de medida;
- nada aqui muda `engine.py`, o modular, a web, o genoma de hoje ou uma decisão já tomada. Toda mecânica descrita entra, se entrar, atrás
  de uma chave desligada, com o gabarito das vidas de hoje gravado antes.

## 0. Em uma página

- **A visão** é um vetor de quatro inteiros (cor, brilho, movimento, complexidade), calculado a partir de um quadro, que é descartado na
  hora (seção 2). O quadro vem de uma **TV do jogo** (determinística, gerada da semente) ou da **tela real** do usuário
  (`getDisplayMedia`, só no modo livre gravado).
- **O gosto** tem dois registros, como o paladar: o **agrado** (quanto um estímulo "está certo" para o pet) e o **interesse** (quanto ele
  puxa o olhar agora). O agrado tem a forma de um pico; o interesse se gasta com a exposição e volta com o tempo (a habituação). Uma parte
  é inata (o genoma), outra é aprendida (a exposição e a consequência) (seção 3).
- **A ação "olhar"** gasta tempo, tem um alvo (uma TV) e é a única forma de o pet receber o vetor (seção 4).
- **A medida** são duas, sempre separadas: a **escolha entre dois** estímulos, com a posição sorteada, e o **tempo relativo olhando**. Só
  depois de uma fase de familiarização. A divergência entre as duas é dado, não erro (seção 5).
- **Os riscos centrais** são o dono ler o próprio gosto como se fosse o do pet (seção 6) e a privacidade da captura da tela (seção 7).
- **A ligação com a INDIVIDUALIDADE:** o gosto visual vira mais um traço lido por sondas em cópias do pet, no desenho genoma × dono
  (seção 8).
- **A ordem** (seção 9): a espec revisada pelo Matheus, depois o Python com a TV do jogo, depois a sonda, depois o plano e a run, e só no
  fim a web e a tela real. A exceção é o protótipo P0 (seção 14), pedido pelo Matheus antes da espec.
- **A pergunta do Matheus** ("ele pode começar a gostar de algo que eu assista ou ouça?") tem a resposta na seção 12, e **o som** na
  seção 13.

## 1. De onde vem e o que já existe no projeto

- **O paladar** (`docs/futuro/paladar.md` e `digilab/frutas.py`) é o modelo: o perfil do estímulo em inteiros em [0, C], dois registros
  (gostar e querer), a preferência inata no genoma com rng própria (`GenomaFrutas`, rng `frutas-ovo`), a neofobia e a saciedade específica.
  As restrições de `docs/DEFINICOES_FRUTAS_V2.md` (2.1 a 2.4) valem aqui com a troca de "comida" por "imagem".
- **As sondas da INDIVIDUALIDADE** (`experiments/sondas_individualidade.py`, `docs/TAREFA_V3_INDIVIDUALIDADE.md`,
  `docs/futuro/individualidade_pet.md`): a situação padronizada aplicada a uma cópia do pet, com rng própria, e a vida real intacta.
- **O interesse que se gasta e volta** (a nota do vault `20 Temas/Ensinar a olhar`, a palestra do Trico, tradução de fã): cada objeto
  tem um nível de interesse que cai depois da ação e volta com o tempo. A literatura dá o nome, a habituação e a deshabituação, e um
  modelo calculável (seção 3.3).
- **Uma TV de tubo** já aparece na lista de enfeites possíveis da `docs/TAREFA_V3_MUNDO_ENFEITES.md` (4.1, fora daquela tarefa). Hoje ela
  não existe no jogo nem no motor.
- **Já no projeto e citadas pela nota** (`docs/referencias/referencias_verificadas.csv`): Oudeyer e Kaplan 2007, Schmidhuber 2010,
  Singh et al. 2010, Pathak et al. 2017, Lehman e Stanley 2011, Christiano et al. 2017.

## 2. A visão: um vetor de quatro números, e o quadro descartado

### 2.1 O vetor

Para cada quadro, quatro componentes, cada um um inteiro em [0, C] (a escala do corpo, CD-1), como as qualidades do paladar:

| componente | o que mede no quadro (PROPOSTO, SEM FONTE na conta exata) |
|---|---|
| `cor` | a saturação média (quanto o quadro é colorido, não qual cor) |
| `brilho` | a luminância média |
| `movimento` | a diferença média de luminância para o quadro anterior |
| `complexidade` | a densidade de bordas (a fração de vizinhos com contraste acima de um corte) |

- **O precedente:** estatísticas cromáticas e espaciais de baixo nível predizem a preferência de bebês e de adultos (McAdams et al.
  2023, `10.1167/jov.23.8.2`, [resumo parcial]). Um modelo de habituação que parte da própria imagem existe (Raz et al. 2025,
  `10.7554/elife.102713`).
- **As contas exatas** (a redução do quadro, o corte das bordas, a taxa de amostragem) são da espec (GV0) e são PROPOSTAS.
- **A alternativa** é um escalar só, a complexidade, que é a variável clássica do U invertido (Berlyne 1971, sem DOI; Yanagisawa 2021,
  `10.3389/fncom.2021.698252`). Quatro componentes deixam pets diferentes gostarem de coisas diferentes; um escalar só deixa os pets
  diferirem no ponto ótimo (GV-2).

### 2.2 De onde vem o quadro

| fonte | determinística | serve para resultado | privacidade |
|---|---|---|---|
| **a TV do jogo**: programas sintéticos gerados da semente, por uma rng própria (`derivar_semente`), com o vetor de cada quadro calculado direto do programa | sim | sim | nada a capturar |
| **a tela real** (`getDisplayMedia`) | não | **não**: só o modo livre gravado | o risco da seção 7 |

- **A TV do jogo** é um objeto do mundo, como o comedouro. O que passa nela é uma sequência de "programas", cada um com um perfil de
  vetor (e uma variação dentro do programa). Os programas são o análogo dos tipos de fruta. No Python, a TV não precisa de imagem: ela
  produz direto os quatro inteiros. Na web, a imagem é desenhada a partir do mesmo programa, e a paridade confere os inteiros.
- **A tela real** entra só pelo modo livre gravado (a exceção do `CLAUDE.md`): o vetor calculado ao vivo entra no log como evento, e o
  replay lê o evento. Ela nunca vale para resultado, protocolo com hash ou paridade.

### 2.3 O quadro descartado

O quadro nunca sai da função que calcula o vetor: não vai ao log, ao disco, ao servidor local nem à LLM. Só os quatro inteiros saem
(seção 7).

## 3. O gosto: inato e aprendido, em forma de pico, com habituação

### 3.1 Dois registros

Como o paladar (2.1 de `docs/DEFINICOES_FRUTAS_V2.md`):
- o **agrado** `A(v)`: o quanto o vetor `v` "está certo" para este pet. É o análogo do gostar;
- o **interesse** `I(v, t)`: o quanto o vetor puxa o olhar agora. É o análogo do querer, e é o que entra na escolha da ação "olhar".

O agrado só chega à escolha por uma atualização declarada do interesse. A razão empírica para separar os dois: adultos olharam mais as
figuras novas, mas avaliaram melhor as semifamiliares (Gustafsson et al. 2021, `10.3758/s13420-021-00484-3`). Tempo olhando não é gosto.

### 3.2 O pico

- **A forma PROPOSTA:** o agrado é uma função em pico da distância entre o vetor e o que o pet **espera** (um traço de exposição por
  componente): nem igual demais ao esperado, nem longe demais. O ponto ótimo e a largura do pico são **inatos por pet**.
- **O apoio:** a formalização de Yanagisawa 2021 (complexidade, novidade e incerteza no potencial de excitação); Sekoguchi et al. 2019
  (`10.1109/smc.2019.8914626`) para a habituação na mesma conta; os dados de Kidd et al. 2012 (`10.1371/journal.pone.0036399`, bebês
  desviam o olhar do muito simples e do muito complexo); Berlyne 1971 como origem.
- **As cautelas:** a literatura de ordem e complexidade é inconsistente (Van Geert e Wagemans 2020, `10.1037/aca0000224`, [resumo
  parcial]), e há condições em que o familiar vence o novo (Brooks et al. 2023, `10.1038/s41598-023-31953-6`). O pico é um bom padrão,
  não uma lei (GV-7).
- **A função exata** (gaussiana, triangular ou degraus inteiros) é da espec, em inteiros, como o resto do corpo. PROPOSTA, SEM FONTE.

### 3.3 A habituação: o interesse que se gasta e volta

- Cada estímulo (cada programa da TV, ou cada região do espaço do vetor) tem um nível de interesse que cai enquanto o pet olha e volta
  com o tempo sem olhar. É a ideia do Trico, com o nome da literatura: o olhar cai com a repetição e volta com o novo (Fantz 1964,
  `10.1126/science.146.3644.668`; Cao et al. 2022, `10.1111/tops.12631`; Raz et al. 2025).
- O traço de exposição da 3.2 se move na direção do que o pet vê. Por isso a exposição desloca o ponto em que um quadro "está certo".
- As meias-vidas são PROPOSTAS, SEM FONTE, e entram no `digilab/config.py` com esse status.

### 3.4 A parte inata

- **No genoma, numa seção própria, com rng própria** (`visao-ovo`, derivada por `derivar_semente`), fora do Temperamento, como o
  `GenomaFrutas` (F5): o ponto ótimo e a largura do pico por componente, e o peso de cada componente.
- **O genoma vazio** é o pet sem gosto visual inato (todos os pets iguais nessa parte). É o controle e é a vida de hoje com a chave
  ligada.
- **O apoio conceitual:** a preferência nasce em parte do viés do sistema receptor (Ryan 1998, `10.1126/science.281.5385.1999`), e a
  parte inata pode ser tratada como um prior evoluído (Singh et al. 2010, já no projeto). No paladar: predisposição e exposição (Birch
  1998, `10.1079/pns19980090`).
- **O aprendido é estado e nunca é herdado** (2.4 de `docs/DEFINICOES_FRUTAS_V2.md`). Se a parte inata entra no genoma é a GV-4.

### 3.5 A parte aprendida

Dois caminhos, cada um com o seu termo e separado no painel:
- **a exposição:** o que o pet vê muito desloca o traço de exposição e, com ele, o agrado (a mera exposição: Zajonc 1968,
  `10.1037/h0025848`; os moderadores na meta-análise de Bornstein 1989, `10.1037/0033-2909.106.2.265`, [resumo parcial]: a
  complexidade, o intervalo e a duração da exposição, que o jogo controla);
- **a consequência:** o que o pet viu antes de uma consequência do corpo (o canal da consequência que o cérebro já tem, como no paladar)
  ganha ou perde agrado. O análogo é a associação entre o tipo de comida e a consequência depois de comer (Provenza 1995,
  `10.2307/4002498`; Yearsley et al. 2006, `10.2307/3844777`). **SEM FONTE** para a mesma associação com imagens num agente. Qual sinal
  conta como consequência é a GV-8.

**O desenvolvimento:** a preferência pode mudar do familiar para o novo ao longo da vida (Perone e Spencer 2013,
`10.3389/fpsyg.2013.00648`). Fica fora da primeira versão (GV-9).

## 4. A ação "olhar"

- **O que é:** uma ação do pet com um alvo (uma TV, ou a "janela" da tela real). Enquanto olha, o pet recebe o vetor da TV a cada passo
  de amostragem e não faz outra coisa. Ele para quando o interesse cai abaixo do de outra ação.
- **Por que uma ação, e não um sentido sempre ligado:** sem a ação não há tempo olhando, nem escolha entre duas TVs, nem custo de olhar.
  E o pet que olha é visível para o dono (o pet vira a cabeça para a TV, a ideia do "pet olha antes de agir" do `Ensinar a olhar`).
- **Onde fica no cérebro:** um módulo do DigiBrain modular sob o `Protocol` `Politica`, ligado por um gancho como os de hoje
  (`consequencia_corpo`). O cérebro A não muda; sem o módulo, o pet nunca escolhe "olhar".
- **A chave:** desligada, nada disso existe e a vida de hoje sai byte a byte. O gabarito é gravado num commit próprio, antes da mudança.

## 5. A medida do gosto

### 5.1 Duas medidas, sempre separadas

| medida | como | o que lê |
|---|---|---|
| **a escolha entre dois** | duas TVs no mapa, cada uma com um programa, a posição sorteada por rng própria; qual o pet escolhe olhar primeiro | o agrado (a direção da preferência) |
| **o tempo relativo olhando** | a fração do tempo da janela olhando cada uma | o interesse (novidade e agrado misturados) |

- **O precedente do desenho:** duas fotos simultâneas e o tempo relativo de olhar em orangotangos (Adams e MacDonald 2020,
  `10.46867/ijcp.2018.31.04.05`); a escolha entre estímulos visuais por macacos (Hirskyj-Douglas e Kankaanpää 2021,
  `10.3390/ani11020557`, e 2022, `10.1145/3532106.3533577`).
- **Vários testes binários em vez de muitas opções juntas:** as opções simultâneas se influenciam, mais quanto mais opções (Pfefferle et
  al. 2025, `10.3758/s13428-025-02668-5`).
- **A divergência é dado:** se o tempo vai para o novo e a escolha para o semifamiliar, é o padrão de Gustafsson et al. 2021, e não um
  erro da medida.
- **A força, depois:** a escolha dá a direção, não a força (Duncan 1992, `10.3382/ps.0710658`). Um análogo do teste de demanda
  (Dawkins 1983, `10.1016/s0003-3472(83)80026-8`, [sem resumo]), como andar mais longe para olhar ou abrir mão de outra ação, mediria a
  força. Fica para depois da primeira medida (GV-5).

### 5.2 A familiarização antes de medir

O uso de uma tecnologia por animais cai quando ela deixa de ser nova (Hirskyj-Douglas e Webber 2021, `10.1145/3493842.3493893`). A TV
vai atrair o pet nos primeiros dias pela novidade da TV, e não pelo gosto. **O gosto só se mede depois de uma fase de familiarização com
a TV**, com a duração e o critério (por exemplo, o tempo olhando a TV em si ter estabilizado) escritos no plano de análise antes da
primeira vida (GV-6).

### 5.3 Os estímulos da medida

Os pares da medida usam programas que o dono **nunca** mostrou, gerados de perfis fixos que cobrem o espaço do vetor. Assim a medida lê o
gosto do pet sobre o que é novo para ele, e o efeito da exposição do dono se lê à parte (seção 6).

## 6. O risco de o dono confundir o gosto dele com o do pet

- **O mecanismo do risco:** o dono escolhe o que passa na TV. Pela mera exposição, o pet passa a "gostar" do que o dono mostra. O dono
  lê isso como o gosto do pet, e o gosto do dono volta para ele como se fosse do pet.
- **A fonte:** **SEM FONTE** que meça a leitura que o dono faz do gosto do pet (nota, seção 7). Nos cães, o tutor é o informante do que o
  cão vê e gosta (Montgomery et al. 2025, `10.1038/s41598-025-06580-y`), o que mostra o tamanho do problema, não a solução.
- **O que o desenho faz:**
  - o painel do cérebro mostra a parte inata, a parte da exposição e a parte da consequência separadas, como já faz com o paladar;
  - o jogo não premia o dono por "acertar" o gosto do pet;
  - nada de comparação por pares feita pelo dono: ela é um jeito barato de ensinar (Christiano et al. 2017, já no projeto), mas vira o
    gosto do dono, não o do pet;
  - a medida usa estímulos que o dono nunca mostrou (5.3), e o desenho genoma × dono separa as duas partes (seção 8).
- **De quem é o gosto** é a GV-3.

## 7. A privacidade da captura da tela

- **O risco:** a tela é a maior fonte de vazamento de informação privada nas câmeras vestíveis (Korayem et al. 2016,
  `10.1145/2858036.2858417`). Moradores comparam o robô doméstico a um pet que **não** coleta dados (Li et al. 2026, arXiv:2602.16975,
  preprint). Processar no próprio computador não basta: importam o estado derivado que se guarda e o que se delega (Chung e Badhe 2026,
  arXiv:2606.10173, preprint; o caso Microsoft Recall só por essa fonte técnica, porque a fonte primária não foi aberta).
- **O desenho PROPOSTO** (desenho próprio; **SEM FONTE**, nenhuma fonte o propõe):
  - a captura é opcional, ligada pelo dono a cada sessão, e visível (o navegador já mostra o indicador de compartilhamento);
  - o quadro é reduzido e descartado dentro da função do vetor (2.3);
  - só os quatro inteiros saem, numa taxa baixa, e só para o log local da vida;
  - nada da captura vai ao servidor local, à LLM ou a qualquer rede;
  - o jogo diz isso ao dono, em uma frase, antes de ligar;
  - o estado derivado também conta: a série dos quatro números revela quando o computador estava em uso, e o tipo grosso do que passava
    (um vídeo, um texto). A espec decide a taxa, a quantização e se o horário entra no log com a resolução de hoje (GV-10).
- **A ordem:** a tela real só depois da TV do jogo, e só depois de uma revisão de privacidade própria (GV-1, etapa GV5).

## 8. A ligação com a INDIVIDUALIDADE

- **O gosto visual é mais um traço** que as sondas leem: a sonda das duas TVs (5.1) aplicada a uma cópia do pet num tick, com rng própria,
  e a vida real intacta, como as sondas de `experiments/sondas_individualidade.py`.
- **O desenho genoma × dono** (`docs/futuro/individualidade_pet.md`, seção 4) divide o traço numa parte do genoma (o pico inato), numa
  parte do dono (o que ele mostrou) e na interação. Os donos são personas sintéticas que mostram programas diferentes na TV; os clones
  com donos diferentes dão a parte do dono, e os genomas diferentes com o mesmo dono dão a parte do genoma. O genoma vazio (3.4) é o
  controle.
- **A repetibilidade:** a escolha e o tempo, em dias diferentes e em réplicas da sonda, dão quanto das diferenças entre pets se repete.
- **O que não muda:** a bateria de seis sondas decidida (IN-2) e as etapas em andamento da INDIVIDUALIDADE. A sonda das duas TVs é da
  frente nova, usa a mesma maquinaria e só faz sentido com a chave da visão ligada: nas vidas de hoje o traço não existe (GV-11).
- **Nenhuma etapa desta frente depende do I7** nem mexe na worktree da INDIVIDUALIDADE.

## 9. Os passos

| etapa | o quê | depende de | código |
|---|---|---|---|
| **GV0** | a espec: as contas do vetor, a forma do pico, as meias-vidas, a ação "olhar", a TV do jogo, a sonda, a privacidade; as 56 referências da nota em `docs/referencias/` (GV-12); **revisada pelo Matheus antes de qualquer protótipo** | as GV-1 a GV-12 | não |
| **GV1** | o Python atrás de chave desligada: a TV do jogo, o vetor, o gosto (genoma e estado), a ação "olhar" num módulo do modular; o gabarito das vidas de hoje gravado antes, num commit próprio | GV0 aprovada | sim |
| **GV2** | a sonda das duas TVs como ferramenta, só leitura, com o G2 (a vida com e sem a sonda sai byte a byte) | GV1 | sim |
| **GV3** | o `docs/PLANO_ANALISE_V3_GOSTO_VISUAL.md` e uma faixa pedida ao coordenador; a run descritiva genoma × dono, com a familiarização; o `RESULTADO_V3_GOSTO_VISUAL.md` | GV2 | run |
| **GV4** | a web: a TV do jogo com paridade contra os gabaritos do Python | GV3 | sim |
| **GV5** | a tela real (`getDisplayMedia`) no modo livre gravado, depois de uma revisão de privacidade própria | GV4 e a GV-10 | sim |

## 10. As decisões do Matheus (todas PROPOSTAS)

| id | a decisão | a recomendação | o custo de errar |
|---|---|---|---|
| **GV-1** | A TV do jogo ou a tela real primeiro. | **A TV do jogo.** Ela é determinística, serve para resultado e paridade, e não tem risco de privacidade. A tela real só no fim (GV5), no modo livre gravado. | Com a tela real primeiro, nada do que se mede vale para resultado (o modo livre não vale), e o risco de privacidade vem antes de se saber se o gosto funciona. Com a TV primeiro, o custo é adiar a parte mais vistosa. |
| **GV-2** | O vetor de quatro números (cor, brilho, movimento, complexidade) ou outro. | **Os quatro, como inteiros em [0, C]**, com as contas fixadas na GV0. | Um escalar só (a complexidade) é mais simples e tem a fonte clássica, mas os pets só diferem no ponto ótimo, não no que gostam. Mais componentes diluem a medida e pedem mais vidas. Trocar depois exige refazer o gabarito e a sonda. |
| **GV-3** | De quem é o gosto: do pet ou do dono. | **Do pet.** O dono só influencia pela exposição e pela consequência, e o painel mostra as partes separadas; nenhuma comparação por pares do dono. | Se o gosto for do dono (o dono ensina por pares), a frente vira um preditor da preferência do dono e o traço deixa de ser do pet: a ligação com a INDIVIDUALIDADE perde o sentido. Se for do pet, o dono pode achar que o pet "não aprende" o que ele mostra; é o custo de produto. |
| **GV-4** | Se a parte inata entra no genoma. | **Sim, numa seção própria com rng própria (`visao-ovo`), fora do Temperamento e do G0, como o `GenomaFrutas`.** O genoma vazio é o controle. | Sem parte inata, o traço só pode vir do dono e do acaso, e a parte do genoma da INDIVIDUALIDADE sai zero por construção. Dentro do G0, mexe num genoma decidido e nas vidas que o usam. |
| **GV-5** | A medida principal. | **A escolha entre dois para o agrado e o tempo relativo para o interesse, sempre separados**; a divergência é registrada. O teste de força (o custo de olhar) fica para depois. | Medir só pelo tempo olhando faz o pet "gostar" do novo (Gustafsson et al. 2021). Medir só pela escolha perde a habituação, que é metade do desenho. |
| **GV-6** | A fase de familiarização antes de medir. | **Obrigatória**, com a duração e o critério de estabilização escritos no plano de análise antes da primeira vida. Número PROPOSTO só no plano. | Sem ela, mede-se a novidade da TV, não o gosto. Com um critério fixado depois de ver os dados, convida-se a escolher o resultado. |
| **GV-7** | A forma do agrado. | **O pico (U invertido) sobre a distância ao esperado**, com a forma exata em inteiros na GV0. | A literatura é inconsistente: se o pico não aparecer nos pets, é um resultado a registrar, não um ajuste a fazer. Uma forma monotônica (mais é melhor) é mais simples, mas não tem habituação com sentido. |
| **GV-8** | Qual sinal conta como consequência de ter olhado. | **O canal da consequência do corpo que o cérebro já tem (o mesmo do paladar)**, numa janela curta depois de olhar. | Uma consequência larga demais associa a imagem a tudo o que acontece depois (ruído lido como gosto). Sem consequência, o aprendido é só exposição. |
| **GV-9** | O desenvolvimento (do familiar para o novo ao longo da vida). | **Fora da primeira versão.** | Com ele desde o início, a idade vira mais um fator e confunde a primeira medida. Sem ele, o pet bebê e o adulto gostam do mesmo jeito, o que pode ser pouco vivo. |
| **GV-10** | O que da tela real fica guardado. | **Só os quatro inteiros, numa taxa baixa, no log local; nada à rede, ao servidor ou à LLM; a captura ligada a cada sessão e anunciada.** A taxa e a resolução do horário na GV0. | Guardar mais (o quadro, uma miniatura, uma taxa alta) torna o log um registro do que o usuário faz no computador. Guardar menos pode deixar o pet cego ao movimento. |
| **GV-11** | A sonda das duas TVs entra na bateria da INDIVIDUALIDADE. | **Não: sonda própria desta frente, com a mesma maquinaria**, sem mexer na IN-2 nem nas etapas em andamento. | Entrar na bateria muda uma decisão tomada e o custo das runs de lá; as vidas de hoje nem têm o traço. Separada, a comparação com os outros traços pede um passo a mais no plano. |
| **GV-12** | As 56 referências da nota no repositório. | **Sim, na GV0**, num `docs/referencias/*_verificadas.csv` com o status e os rótulos [sem resumo] e [resumo parcial] da nota. | Sem isso, a frente cita fontes que só existem no vault, e o CI da categoria literatura não as confere. O custo é um PR a mais. |

| **GV-13** | O som: um vetor de áudio ao lado do visual. | **Sim, um vetor de três inteiros em [0, C]: o volume, a variação (o ritmo) e o brilho do timbre (o centróide espectral)**, calculado no computador do usuário, com a mesma regra de privacidade da GV-10, e com o seu próprio pico inato e a sua habituação. Antes da GV0, uma busca dirigida (seção 13). | Sem o som, o pet "assiste" um vídeo mudo, e a pergunta do Matheus (seção 12) só tem metade da resposta. Com o som sem a busca, o desenho do áudio fica SEM FONTE inteiro; e um áudio mais rico (palavras, melodia) aumenta o risco de privacidade sem ganho para o gosto. |
| **GV-14** | O risco de o gosto aprendido ser só o gosto do dono, por exposição, e como o painel separa as partes. | **O painel mostra três barras por componente: o inato (do genoma, fixo), o da exposição e o da consequência**, e um "gosta mais de…" calculado só do total; o jogo não premia o acerto; a medida usa estímulos que o dono nunca mostrou (5.3); o desenho genoma × dono (seção 8) mede a parte do dono. | Sem a separação, o dono vê o próprio gosto devolvido como se fosse do pet, e qualquer leitura de "o pet aprendeu a gostar" fica confundida com "o pet viu muito". Separado demais na tela, o painel vira um gráfico de pesquisa e perde o tom de jogo. |

## 11. Riscos

- **Ler ruído como gosto.** Mitigação: o genoma vazio como controle, réplicas de sonda e de semente, e a familiarização.
- **A mecânica medir a si mesma.** Se todo pet escolhe o mesmo programa, a sonda não separa ninguém. Mitigação: os perfis de programa
  cobrem o espaço do vetor, e o plano diz antes o que fazer com uma sonda sem variância.
- **O olhar comer a vida.** Uma TV sempre ligada pode tomar o tempo do pet. Mitigação: o interesse se gasta, e a run mede o tempo total
  olhando como efeito colateral.
- **A privacidade.** Mitigação: a seção 7 e a ordem da seção 9.
- **A alegação de novidade.** Mitigação: as regras do topo; o que a busca não achou não vira "inédito".

## 12. A pergunta do Matheus: o pet pode começar a gostar do que eu assisto ou ouço?

A pergunta (Matheus, 2026-11-11): "se eu streamar minha tela para o pet, ele pode começar a gostar de algo que eu assista ou ouça".

**A resposta pelo desenho: sim, pelas características, não pelo sentido.**
- **O pet gosta do vetor, não do conteúdo.** Ele recebe a cor, o brilho, o movimento e a complexidade (e, com a GV-13, o volume, o ritmo
  e o timbre). Ele não sabe que é um filme, um jogo ou uma planilha. Se o dono assiste muito anime colorido e rápido, o que o pet pode
  passar a preferir é "colorido e rápido", e isso vale para qualquer outra coisa colorida e rápida.
- **O primeiro caminho é a mera exposição** (3.5; Zajonc 1968, `10.1037/h0025848`): o que o pet vê muito desloca a expectativa dele,
  e o ponto em que um quadro "está certo" anda na direção do que o dono assiste.
- **O segundo caminho é a consequência** (3.5; o análogo do paladar, Provenza 1995, `10.2307/4002498`): se o dono faz carinho enquanto
  passa um tipo de coisa, aquele tipo ganha agrado. **SEM FONTE** para isso com imagens ou sons num agente.
- **O excesso gasta o interesse.** A habituação (3.3) faz o pet desviar do que viu demais agora, e o pico (3.2) faz o igual demais deixar
  de "estar certo". Por isso a resposta não é "o pet passa a gostar de tudo o que o dono assiste": um pouco de exposição aproxima o gosto,
  exposição demais cansa, e o pet volta a procurar o que difere (Gustafsson et al. 2021, `10.3758/s13420-021-00484-3`: o novo atrai o
  olhar, o semifamiliar fica com o agrado).
- **A parte inata não se move.** Dois pets com o mesmo dono e a mesma tela terminam com gostos diferentes, porque partem de picos
  diferentes. Isso é o que torna o gosto do pet, e não só o do dono (GV-3, GV-14).

## 13. O som

- **A ideia:** um vetor de áudio de três inteiros em [0, C], calculado no computador do usuário a partir do áudio da captura e descartado
  na hora, como o quadro: o **volume** (a energia média), a **variação** (o quanto o volume muda entre janelas, um substituto barato do
  ritmo) e o **brilho do timbre** (o centróide espectral). As contas exatas são PROPOSTAS, SEM FONTE (GV-13).
- **O gosto do som** segue a mesma forma do visual: um pico inato por componente, a expectativa que se desloca e o interesse que se gasta.
- **A privacidade:** a mesma regra da GV-10. Só os três números saem; nenhum trecho de áudio, nenhuma transcrição, nada à LLM.
- **A fonte: SEM FONTE no levantamento.** A nota do vault cobre só a visão (o único resultado sonoro dela é Gold et al. 2019,
  `10.1523/jneurosci.0428-19.2019`, sobre o prazer da música e a predição, [resumo parcial]).
- **A busca dirigida proposta (não feita):** pelas mesmas bases e regras da nota (OpenAlex, Crossref, DOI e resumo conferidos), em três
  trilhas:
  - a preferência auditiva em animais e a escolha entre sons (o enriquecimento sonoro em cães, gatos e primatas; os sistemas de escolha
    sonora de Hirskyj-Douglas e Kankaanpää 2022 como ponto de partida);
  - a habituação e a mera exposição a sons e música (a curva de exposição na música, o U invertido da complexidade musical);
  - os descritores de baixo nível (volume, ritmo, centróide espectral) como preditores de preferência, em humanos ou em agentes.

## 14. O protótipo P0 no jogo web (pedido do Matheus antes da espec)

**O pedido (Matheus, 2026-11-11):** "então implemente uma proposta que faça o pet rodar no navegador naquele modo que a janela fica
pequena e ele possa ver e ouvir uma tela do meu computador, posso ver as reações dele e ele recebendo essas informações do meu
comportamento, passando tempo com o usuário e demonstrando preferência por certas coisas". Ele pula a revisão da espec antes do protótipo
(a regra é dele; o registro está em `docs/registro/2026-11.md`, D-GV-P0-1). A GV0 continua valendo para tudo o que vier depois.

**O que o P0 é, e o que não é:**
- **é** um protótipo de produto no `web/app/`, para o Matheus ver e sentir a ideia: o pet numa janela pequena flutuante (a Document
  Picture-in-Picture API), vendo e ouvindo a tela pela captura (`getDisplayMedia`), com as reações e o painel do gosto;
- **não é** uma mecânica do motor: o gosto fica num módulo TS separado (`web/app/src/gostoVisual/`), fora do motor, fora do log e fora do
  save do pet. Ele não tem par no Python, não tem paridade, não entra em nenhuma medida e não vale para resultado. As GV-1 a GV-14 seguem
  em aberto, e o P0 não decide nenhuma delas;
- **entra atrás de uma chave desligada** (o parâmetro `?gosto_visual=1`). Desligado, o jogo é o de hoje, e um teste confere.

**Como ele segue a proposta:** o vetor de quatro números da visão (seção 2) e o de três do som (seção 13), uma vez por segundo, com o quadro
e o áudio descartados na hora; o agrado em pico com o ponto ótimo e a largura inatos derivados da semente do pet; a expectativa que anda
com a exposição; o interesse que se gasta e volta; o carinho do dono durante a exibição puxando o gosto (a associação); o painel com o
inato e o aprendido separados (GV-14). Todos os números do P0 são PROPOSTOS, SEM FONTE, e ficam no próprio módulo, porque ele não é do
motor nem do `config.py`.

**A privacidade no P0:** a captura começa só por clique; só os sete números existem depois de cada segundo; nada é enviado. Só o estado
do gosto (os desvios aprendidos e o tempo assistindo junto) fica guardado, no `localStorage` deste navegador, por pet.
