# Revisão DM: as fontes do substrato neural do DigiBrain modular (a PE-1)

Pedido do Gerente ao worker C em 2026-10-25, depois do merge do #407: a busca de literatura da PE-1, decidida pelo Matheus. É só papel:
nenhum código, nenhuma run, nenhuma semente.

**A pergunta:** as escolhas SEM FONTE das seções 2 e 14 de `docs/ESPEC_DIGIBRAIN_MODULAR.md` têm fonte verificada? São cinco frentes:
- **(a)** os integradores com vazamento em ponto fixo e as unidades de taxa como substrato de criaturas artificiais;
- **(b)** as redes recorrentes de tempo contínuo (CTRNN, CfC e NCP), só como estudo, com as licenças conferidas (DM-9);
- **(c)** as regras hebbianas de três fatores com modulação neuroquímica;
- **(d)** o crédito por opção contra o crédito por janela;
- **(e)** a memória episódica por lugar informando a escolha.

**Regras:**
- só as referências da tabela, com o status de `docs/referencias/REGRAS_CITACAO_DIGILAB.md`;
- conferência sobre os metadados e o resumo, **nunca o texto completo**;
- **nenhuma alegação de novidade** (a seção 9);
- **a espec não muda nesta tarefa:** cada item termina numa "troca proposta", que o Gerente leva ao Matheus (a seção 8).

**A tabela:** `dm_referencias_verificadas.csv` (36 linhas: 31 VERIFICADA, 1 VERIFICADA sem DOI e 4 NÃO LOCALIZADA). O BibTeX das 32
verificadas está em `dm_referencias.bib`, e o registro bruto por DOI, com o resumo e de onde ele veio, em `dm_verificacao_crossref.json`.

## 1. Método e limites

- **A busca foi feita em 2026-10-25.**
  - **Os metadados** vieram da API do Crossref: status, autores, ano, veículo, volume, páginas e o campo `update-to`.
  - **O resumo** veio do Crossref; na falta dele, do OpenAlex, e na falta dos dois, do PubMed (E-utilities).
  - **Os preprints** foram conferidos na API do arXiv.
  - **As licenças** saíram da API do GitHub e do PyPI.
- **Nenhum DOI de memória.** Os 29 DOIs da tabela resolveram no Crossref nesta sessão, todos com status 200 e nenhum com `update-to`
  (correção ou retratação).
- **Quanto do texto foi lido:**
  - **22 dos 29 têm o resumo lido:** 8 no Crossref, 9 no OpenAlex e 5 no PubMed;
  - **os 7 restantes** estão marcados linha a linha como "título e metadados", e não sustentam afirmação de conteúdo;
  - **os resumos automáticos (TLDR) do Semantic Scholar não contam como resumo.** Foram vistos e descartados.
- **O que ficou de fora, sem uso:**
  - a plasticidade diferenciável (Miconi et al. 2018, arXiv:1804.02464): o treino por retropropagação está fora do desenho;
  - o LSTM com memória episódica (Ritter et al. 2018, arXiv:1805.09692): é meta-aprendizado profundo;
  - os trabalhos de quantização mista em ponto fixo que a busca devolveu: tratam de redes treinadas sem estado, não de integradores.
- **As buscas temáticas** que não acharam nada viraram as quatro linhas NÃO LOCALIZADA da tabela, cada uma com as consultas feitas. A
  ausência de resultado numa busca por palavras é evidência fraca.

## 2. A resposta curta

| frente | veredito | as fontes verificadas que entram | o que continua sem fonte |
|---|---|---|---|
| **(a)** as unidades de taxa e os integradores | **tem fonte para o modelo, não para o ponto fixo** | Hopfield (1984) e Wilson e Cowan (1972), as unidades graduadas e as populações; Beer (1995), a CTRNN como sistema nervoso simples de agentes autônomos; Usher e McClelland (2001), o integrador com vazamento como unidade de decisão; Cañamero (1997), as motivações e os "hormônios" numa criatura | o integrador em ponto fixo como substrato de criatura (NÃO LOCALIZADA); que a forma I, sem acoplamento, baste |
| **(b)** a CTRNN, o CfC e o NCP | **tem fonte** (sai de CORPUS para VERIFICADA), e **as licenças foram conferidas** | Beer (1995); Funahashi e Nakamura (1993), só o título; Hasani et al. (2021), a LTC; Hasani et al. (2022), o CfC; Lechner et al. (2020), o NCP, só o título | a porta dura em inteiros (escolha nossa); as patentes de terceiros (não buscadas) |
| **(c)** o hebbiano de três fatores com modulação | **tem fonte para o termo e para a forma geral;** há precedentes em agentes que forrageiam | Hebb (2005 [1949]), a descrição da editora; Frémaux e Gerstner (2016); Gerstner et al. (2018); Kuśmierz et al. (2017); Izhikevich (2007); Doya (2002); Niv et al. (2002); Nogueira et al. (2013); Soltoggio et al. (2018); Moerland et al. (2017) | o sinal homeostático como terceiro fator (NÃO LOCALIZADA, é a junção de duas fontes); a excitação como ganho da taxa (o Doya põe a velocidade do aprendizado em outro modulador) |
| **(d)** o crédito por opção contra a janela | **tem fonte para as opções e para os traços, não para a escolha entre eles** | Sutton, Precup e Singh (1999), já na tabela v2; Bacon et al. (2017); Botvinick et al. (2009); Sutton (1988) e Singh e Sutton (1996), só o título; Gerstner et al. (2018) | a comparação direta (NÃO LOCALIZADA). A literatura verificada sustenta o traço como ponte temporal: a escolha por opção se apoia na evidência interna |
| **(e)** a memória episódica por lugar | **tem fonte,** em animais e em agentes | Clayton e Dickinson (1998); Gershman e Daw (2017); Lengyel e Dayan (2007), sem DOI; Blundell et al. (2016) e Pritzel et al. (2017), preprints; Tolman (1948) e Nuxoll e Laird (2012), só o título; Castro e Gudwin (2013), já na tabela v2 | "o mais recente do lugar manda" (NÃO LOCALIZADA); N_ep = 16; o despejo pelo menor \|r\| |

## 3. (a) As unidades de taxa e os integradores com vazamento

**A fonte diz:**
- **Hopfield (1984),** `10.1073/pnas.81.10.3088`, resumo: uma rede de neurônios com resposta graduada (sigmoide), determinística, tem as
  mesmas propriedades coletivas do modelo binário. É a unidade de taxa sem pulsos como modelo neural.
- **Wilson e Cowan (1972),** `10.1016/s0006-3495(72)86068-5`, resumo no PubMed: equações diferenciais acopladas para a atividade de
  **populações** localizadas de neurônios excitatórios e inibitórios. É a população, e não o neurônio, como unidade de modelagem.
- **Beer (1995),** `10.1177/105971239500300405`, resumo: as redes recorrentes de tempo contínuo são usadas "como sistemas nervosos
  simples de agentes autônomos". Mesmo os circuitos pequenos, de um e dois neurônios, têm dinâmica rica, inclusive caótica.
- **Usher e McClelland (2001),** `10.1037/0033-295x.108.3.550`, resumo: a escolha é uma acumulação gradual, **com vazamento**,
  estocástica e competitiva, em unidades de decisão não lineares, e vale para qualquer número de alternativas.
- **Cañamero (1997),** `10.1145/267658.267688`, resumo: uma criatura num mundo 2D tem o comportamento guiado por motivações que vêm das
  necessidades do corpo, com excitação e saciedade. As emoções mandam "hormônios" que mudam a intensidade do comportamento escolhido, e
  os dois são modelados por parâmetros fisiológicos.
- **Jacob et al. (2018),** `10.1109/cvpr.2018.00286`, já na tabela v2, resumo: inferência só com aritmética inteira em redes treinadas,
  que são redes sem estado.

**Leitura nossa:**
- a forma I (`y ← y + mul(k, u − y)`) é a discretização de Euler do integrador com vazamento, a mesma equação de cada unidade de uma
  CTRNN sem os pesos recorrentes;
- as populações da seção 2.1 seguem o uso de Wilson e Cowan;
- o M-AFETO e os moduladores têm em Cañamero (1997) um precedente de criatura, além do Creatures.

**O que não sustenta:**
- **o ponto fixo.** O integrador ou a unidade de taxa em aritmética inteira como substrato de criatura ou de personagem é **NÃO
  LOCALIZADA**. O Jacob et al. trata de redes sem estado, e o ponto fixo continua sustentado pelo requisito de paridade do repositório,
  não pela literatura;
- **que a forma I baste.** O Beer mostra o contrário do que ela supõe: a riqueza vem do acoplamento, que a forma I não tem. É o risco
  que a seção 3 da espec já escreve ("pouca expressividade") e o gatilho da forma II;
- **a curva das urgências.** O Cañamero dá as motivações com excitação e saciedade, não a forma da curva, que continua SEM FONTE.

**Troca proposta (a):** na seção 3 da espec, trocar "Sem fonte verificada no repositório: os integradores com vazamento e as redes
recorrentes de tempo contínuo como modelo neural" pela frase abaixo.
- **[MECANISMO]** a unidade de taxa e a população: Hopfield (1984); Wilson e Cowan (1972);
- **[MECANISMO]** a CTRNN como sistema nervoso de agente: Beer (1995);
- **[MECANISMO]** o integrador com vazamento como unidade de decisão: Usher e McClelland (2001);
- **o ponto fixo continua SEM FONTE** (NÃO LOCALIZADA), sustentado pela paridade.

Na seção 2.1, acrescentar Cañamero (1997) como [INSPIRAÇÃO] do M-AFETO, ao lado de Cliff e Grand (1999).

## 4. (b) A CTRNN, o CfC e o NCP, e as licenças

**A fonte diz:**
- **Hasani et al. (2021), a LTC,** `10.1609/aaai.v35i9.16936`, resumo: são redes feitas de sistemas lineares de primeira ordem, moduladas
  por portas não lineares, e a constante de tempo varia com o estado. O comportamento é estável e limitado, e a saída sai de um
  solucionador numérico.
- **Hasani et al. (2022), o CfC,** `10.1038/s42256-022-00556-7`, resumo: é uma aproximação em forma fechada, com erro limitado, da
  dinâmica da LTC. Dispensa o solucionador e fica de uma a cinco ordens de grandeza mais rápida.
- **Lechner et al. (2020), o NCP,** `10.1038/s42256-020-00237-3`, e **Funahashi e Nakamura (1993),** `10.1016/s0893-6080(05)80125-x`:
  só título e metadados. Confirmam a existência, não o conteúdo.
- **Yamauchi e Beer (1994),** `10.1177/105971239400200301`, resumo: CTRNN evoluídas geram sequências e **aprendem** por reforço do
  ambiente sem uma regra de aprendizado que mude os pesos. O aprender fica na dinâmica. É o contraponto do desenho com plasticidade
  explícita (o P1 e o P2).

**Leitura nossa:** a forma II da seção 3 é a CTRNN de Beer, discretizada. A variante com portas troca a exponencial da forma fechada do
CfC por uma porta dura em inteiros, e isso é escolha nossa, sem fonte. O B (o CfC com ator-crítico, em float) não aprendeu (0,0077 das
decisões, `docs/RESULTADO_V2_CALIBRACAO_CEREBRO_B.md`): é evidência interna, que a literatura não muda.

**As licenças (DM-9, PE-15),** conferidas em 2026-10-25:

| software | onde | licença | o que foi conferido |
|---|---|---|---|
| CfC (o código do artigo de 2022) | `github.com/raminmh/CfC`, commit `3ebaa03` (2022-12-16) | **Apache-2.0** | o arquivo `LICENSE` (texto da Apache 2.0) e a detecção do GitHub; não há arquivo `NOTICE` na raiz; o README não fala de patente nem de restrição comercial |
| NCP (a biblioteca `ncps`) | `github.com/mlech26l/ncps`, commit `695ec22` (2024-08-14); PyPI `ncps` 1.0.1 | **Apache-2.0** | o `LICENSE`, a detecção do GitHub e o campo de licença do PyPI; não há `NOTICE` na raiz |
| LTC (o código do artigo de 2021) | `github.com/raminmh/liquid_time_constant_networks` | Apache-2.0 | só a detecção do GitHub |
| keras-ncp (a versão antiga) | `github.com/mlech26l/keras-ncp` | Apache-2.0 | só a detecção do GitHub |
| NORNBRAIN | `github.com/thechimpmatrix/nornbrain`, commit `2397bf8` (último push em 2026-04-28) | **código em PolyForm Noncommercial 1.0.0; documentação em CC BY-NC 4.0** | o README (a seção "License"); igual ao registrado em `docs/research/digibrain/sources/nornbrain.md` em 2026-10-07 |

**O que as licenças dizem, sem conselho jurídico:**
- a Apache 2.0 permite uso comercial, com a cópia da licença e os avisos de atribuição ao redistribuir o código;
- a licença do código não cobre patentes de terceiros, que **não foram buscadas** (SEM FONTE);
- a espec não copia código de nenhum dos quatro: a forma II é reimplementação, com porta dura;
- o NORNBRAIN continua só estudo.

**Troca proposta (b):**
1. Na seção 3 e na 14 da espec, trocar "CORPUS (pista)" do Hasani et al. (2022) e do Lechner et al. (2020) por VERIFICADA (o de 2022 com
   resumo, o de 2020 só título), e acrescentar a LTC (Hasani et al. 2021) como a origem da variante com portas.
2. Trocar "as licenças do software não foram conferidas" por "conferidas em 2026-10-25: CfC e NCP em Apache-2.0
   (`docs/referencias/DM_REVISAO_SUBSTRATO_NEURAL.md`, seção 4); as patentes não foram buscadas".
3. Marcar a PE-15 como **feita quanto à licença do código**, com a ressalva das patentes.

## 5. (c) O hebbiano de três fatores com modulação neuroquímica

**A fonte diz:**
- **Hebb (2005, reedição do original de 1949),** `10.4324/9781410612403`: o único texto disponível é a descrição da editora. Ela
  sustenta que o livro propõe a regra e a assembleia de células, não uma forma matemática.
- **Frémaux e Gerstner (2016),** `10.3389/fncir.2015.00085`, resumo: dá o arcabouço das regras **neo-hebbianas de três fatores**. Elas
  dependem da atividade pré-sináptica, de variáveis pós-sinápticas e de um ou mais sinais neuromoduladores, de novidade ou de
  recompensa. Mecanismos sinápticos cobrem o intervalo até o sinal chegar.
- **Gerstner et al. (2018),** `10.3389/fncir.2018.00053`, resumo: a coativação marca a sinapse com um **traço de elegibilidade**, e o
  peso só muda se um terceiro fator chegar enquanto a marca existe. O fator pode ser recompensa, punição, surpresa ou novidade. Há
  experimentos que sustentam traços na escala de segundos.
- **Kuśmierz et al. (2017),** `10.1016/j.conb.2017.08.020`, resumo: os três fatores são uma abstração geral. O terceiro pode codificar
  recompensa, erro, estatística da população ou atenção, e não precisa ser a recompensa externa.
- **Izhikevich (2007),** `10.1093/cercor/bhl152`, resumo: um sinal de reforço **global e difuso** (a dopamina) escolhe as sinapses certas
  sobre marcas locais, que ficam sensíveis por alguns segundos. É feito em neurônios com pulsos.
- **Doya (2002),** `10.1016/s0893-6080(02)00044-8`, resumo no PubMed: os neuromoduladores levam **sinais globais que regulam os
  metaparâmetros** do aprendizado. A teoria propõe:
  - dopamina: o erro de previsão;
  - serotonina: a escala de tempo;
  - **noradrenalina: a aleatoriedade da escolha;**
  - **acetilcolina: a velocidade da atualização da memória.**
- **Os precedentes em agentes artificiais que buscam comida:**
  - Niv et al. (2002), `10.1177/1059-712302-010001-01`: regras de plasticidade evoluídas em abelhas que forrageiam, com exploração
    variável e aversão a risco;
  - Nogueira et al. (2013), `10.1162/978-0-262-31709-2-ch083`: uma rede plástica **neuromodulada** controla um personagem virtual e
    gera forrageamento;
  - Soltoggio, Stanley e Risi (2018), `10.1016/j.neunet.2018.07.013`: a revisão das redes plásticas evoluídas, com inato e plasticidade
    na mesma rede;
  - Cliff e Grand (1999), já na tabela principal: o hebbiano com modulação hormonal no norn.
- **Moerland et al. (2017),** `10.1007/s10994-017-5666-0`, resumo: emoções derivadas de homeostase ou de avaliação, e o efeito delas na
  eficiência do aprendizado, são uma categoria estudada.
- **McGaugh (2005),** `10.1101/lm.93405`, já na tabela v2: o título diz que a excitação emocional reforça a consolidação. O texto
  disponível é o primeiro parágrafo de um comentário.

**Leitura nossa:**
- o P2 é uma regra de três fatores em unidades de taxa: o pré é `e_j = z_j`, o pós é 1 na escolhida e o terceiro fator é o `r_n`;
- a elegibilidade guardada da decisão até a consequência é o "traço" de Gerstner et al., com uma marca só;
- o `g_apr` e o `g_exp` são os metaparâmetros globais de Doya.

**O que não sustenta:**
- **o sinal homeostático como terceiro fator:** NÃO LOCALIZADA. As peças estão separadas, o terceiro fator genérico (Kuśmierz et al.) e
  a recompensa como redução do desvio (Keramati e Gutkin 2014). A junção é nossa;
- **as unidades de taxa nas regras de três fatores:** as três revisões tratam de sinapses e STDP;
- **a excitação como ganho da taxa (a PE-4):**
  - o Doya põe a velocidade da atualização na acetilcolina e a aleatoriedade da escolha na noradrenalina. Associar a noradrenalina à
    excitação é leitura nossa, SEM FONTE;
  - o McGaugh (só o título) apoia a direção "excitação → consolidação";
  - o Moerland apoia só a categoria;
  - **as fontes não decidem entre o `g_apr` e o `g_exp`.**

**Troca proposta (c):**
1. Na seção 2.4 (o P2), trocar "a elegibilidade e os três fatores, como termos da literatura, estão SEM FONTE" pelo seguinte:
   - [MECANISMO] o termo e a forma pré × pós × modulador: Frémaux e Gerstner (2016) e Kuśmierz et al. (2017);
   - [MECANISMO] a elegibilidade como marca que espera o terceiro fator: Gerstner et al. (2018);
   - o r homeostático como terceiro fator continua leitura nossa (NÃO LOCALIZADA).
2. Na seção 14, trocar "o hebbiano como regra (de Hebb)" por Hebb (2005 [1949]), só a descrição da editora, sem forma matemática.
3. Nas seções 2.2 e 2.6, acrescentar Niv et al. (2002) e Nogueira et al. (2013) como [MECANISMO] da plasticidade modulada em agente que
   forrageia, ao lado de Cliff e Grand (1999).
4. Na PE-4 (decidida: a excitação, atrás da subchave desligada), acrescentar a nota de que o Doya (2002) mapeia a velocidade do
   aprendizado em outro modulador e a aleatoriedade da escolha na noradrenalina; o McGaugh (2005) apoia a direção "excitação →
   consolidação". A decisão fica como está, e a divergência fica escrita (a decisão D-1 da seção 8).

## 6. (d) O crédito por opção contra o crédito por janela

**A fonte diz:**
- **Sutton, Precup e Singh (1999),** `10.1016/s0004-3702(99)00052-1`, já na tabela v2, só título e metadados: o arcabouço das opções (a
  abstração temporal).
- **Bacon, Harb e Precup (2017),** `10.1609/aaai.v31i1.10916`, resumo: dentro das opções, as políticas internas e as condições de
  **término** aprendem junto com a política sobre as opções.
- **Botvinick, Niv e Barto (2009),** `10.1016/j.cognition.2008.08.011`, resumo no PubMed: o aprendizado por reforço hierárquico, com
  ações agregadas em sub-rotinas, é a leitura do comportamento organizado em tarefas e subtarefas, e o artigo propõe um mapeamento para o
  córtex pré-frontal.
- **Sutton (1988),** `10.1007/bf00115009`, e **Singh e Sutton (1996),** `10.1007/bf00114726`: só título e metadados. São as fontes
  primárias do TD(λ) e dos traços de substituição.
- **Gerstner et al. (2018) e Izhikevich (2007),** da seção 5: o traço de elegibilidade é a ponte temporal entre o ato e a consequência,
  na escala de segundos.

**Leitura nossa:** a intenção da espec é uma opção, com início, persistência e término. O crédito por opção pode ser lido como **uma
elegibilidade que dura a opção inteira** e que fica só na decisão que a começou.

**O que não sustenta:**
- **a escolha entre os dois:** a comparação direta é NÃO LOCALIZADA;
- **a literatura verificada sustenta o traço como mecanismo,** o que joga a favor da janela, não contra. A escolha por opção (a PE-3,
  decidida) se apoia na **evidência interna:** com o traço ligado, o A piorou o que se queria medir
  (`docs/RESULTADO_V2_REVISAO_APRENDIZ.md`).

**Troca proposta (d):** na PE-3 e na seção 2.4, acrescentar as três frases abaixo.
- **[MECANISMO] o arcabouço das opções:** Sutton, Precup e Singh (1999), Bacon et al. (2017) e Botvinick et al. (2009). Eles sustentam a
  intenção como unidade estendida no tempo, não a regra de crédito.
- **A escolha por opção contra a janela vem da evidência interna.** A comparação direta é NÃO LOCALIZADA, e o traço tem sustento na
  literatura (Gerstner et al. 2018).
- **O T-PLAST-2, com intenções longas, é o teste que separa os dois.**

## 7. (e) A memória episódica por lugar informando a escolha

**A fonte diz:**
- **Clayton e Dickinson (1998),** `10.1038/26216`, resumo no PubMed: os gaios lembram **o que** esconderam, **onde** e **quando**:
  - buscam de preferência as larvas frescas pouco depois de esconder;
  - depois de um intervalo longo, em que elas estragam, aprendem depressa a não buscá-las.
- **Lengyel e Dayan (2007),** NIPS 20, sem DOI, resumo no OpenAlex: defende um terceiro sistema de controle, **o episódico**, ao lado do
  modelo do mundo e do hábito, útil sobretudo **bem no começo do aprendizado, antes de o hábito se formar**.
- **Gershman e Daw (2017),** `10.1146/annurev-psych-122414-033625`, resumo: dar memória episódica (traços de eventos individuais) ao
  aprendizado por reforço permite aproximar valores e aprender com poucos dados.
- **Blundell et al. (2016),** arXiv:1606.04460, e **Pritzel et al. (2017),** arXiv:1703.01988, preprints com a revisão por pares não
  conferida: agentes com controle episódico, um buffer de experiências com valor, aprendem mais depressa.
- **Castro e Gudwin (2013),** `10.4018/jse.2013010102`, já na tabela v2: um módulo de memória episódica por cenas numa criatura.
- **Tolman (1948),** `10.1037/h0061626`, e **Nuxoll e Laird (2012),** `10.1016/j.cogsys.2011.10.002`: só título e metadados.

**Leitura nossa:**
- o M-MEM mínimo da espec (o consumo e a visita viram episódio; com fome e sem comida à vista, o lugar lembrado ganha peso; uma visita
  sem comida derruba o lugar) é o padrão comportamental de Clayton e Dickinson: onde está a comida guia a busca, e o desfecho muda a
  busca seguinte. O T-MEM-4 é a versão nossa do "aprender a não buscar onde estragou";
- o Lengyel e Dayan dá uma **predição** para a trajetória da seção 2.5: o M-MEM pesa mais cedo, e o hábito (o P2) depois.

**O que não sustenta:**
- **a regra "o mais recente do lugar manda":** NÃO LOCALIZADA. O Clayton e Dickinson mostra que o quando importa, não uma regra de
  recência;
- **N_ep = 16 e o despejo pelo menor |r|:** continuam PROPOSTOS e SEM FONTE;
- **o mecanismo:** nenhuma fonte de animal sustenta como a memória é implementada.

**Troca proposta (e):**
1. Na seção 4.6 e na 9 (o M-MEM), acrescentar:
   - **[MECANISMO] em animais,** a memória de onde está a comida, com o quando, guiando a busca e mudando com o desfecho: Clayton e
     Dickinson (1998);
   - **[MECANISMO] em agentes,** a memória episódica como fonte de valor: Gershman e Daw (2017), com os preprints de Blundell et al.
     (2016) e Pritzel et al. (2017) como pista;
   - **"o mais recente do lugar manda" continua SEM FONTE.**
2. Na seção 2.5, passo 3, acrescentar como [HIPÓTESE] com fonte a predição de Lengyel e Dayan (2007): o peso da memória cai à medida que
   o hábito se forma. A decisão D-2 da seção 8 diz se ela vai ao plano de análise do protótipo.

## 8. As trocas propostas, numa tabela (para o Gerente levar ao Matheus)

A espec **não foi mudada** nesta tarefa. Cada linha diz onde trocar, o que entra e o custo de não trocar.

| # | onde (`docs/ESPEC_DIGIBRAIN_MODULAR.md`) | hoje | troca proposta | custo de não trocar |
|---|---|---|---|---|
| T-a1 | seção 3, último parágrafo; seção 14, lista dos SEM FONTE | "sem fonte verificada: os integradores com vazamento e as redes recorrentes de tempo contínuo" | [MECANISMO] Hopfield (1984), Wilson e Cowan (1972), Beer (1995), Usher e McClelland (2001); o ponto fixo continua SEM FONTE (NÃO LOCALIZADA), sustentado pela paridade | o substrato parece sem fonte quando tem |
| T-a2 | seção 2.1, linha dos moduladores | só Cliff e Grand (1999) | mais Cañamero (1997) como [INSPIRAÇÃO] do M-AFETO | nenhum grave; perde-se um precedente de criatura |
| T-b1 | seção 3, variante com portas; seção 14 | Hasani et al. (2022) e Lechner et al. (2020) como "CORPUS (pista)" | VERIFICADA (2022 com resumo; 2020 só título), mais a LTC (Hasani et al. 2021) | a tabela da espec contradiz a de `docs/referencias/` |
| T-b2 | seção 3; seção 14; PE-15 | "as licenças do software não foram conferidas" | "conferidas em 2026-10-25: CfC e NCP em Apache-2.0; patentes não buscadas"; a PE-15 feita quanto à licença do código | a PE-15 fica aberta sem motivo e bloqueia a forma II à toa |
| T-c1 | seção 2.4 (o P2); seção 14 | "a elegibilidade e os três fatores, como termos, estão SEM FONTE"; "o hebbiano como regra" | Frémaux e Gerstner (2016), Kuśmierz et al. (2017), Gerstner et al. (2018); Hebb (2005 [1949]); o r homeostático como terceiro fator continua leitura nossa | o P2 parece sem fonte quando tem |
| T-c2 | seções 2.2 e 2.6 | só o Creatures como precedente da plasticidade modulada | mais Niv et al. (2002) e Nogueira et al. (2013) | o leitor pensa que só o Creatures fez isso, e isso beira a alegação de novidade |
| T-c3 | PE-4 | a excitação no `g_apr`, sem fonte além do McGaugh (só título) | a nota da divergência com Doya (2002) e o apoio do McGaugh (2005); a decisão não muda | uma escolha discutível fica sem a ressalva escrita |
| T-d1 | PE-3; seção 2.4 | o crédito por opção sem fonte | o arcabouço das opções (Sutton et al. 1999, Bacon et al. 2017, Botvinick et al. 2009); a escolha vem da evidência interna; a comparação direta é NÃO LOCALIZADA | a escolha parece sustentada pela literatura quando não é, e a literatura dos traços aponta para o outro lado |
| T-e1 | seções 4.6 e 9 | Castro e Gudwin (2013), "sem dizer que a cena informa a escolha" | mais Clayton e Dickinson (1998) e Gershman e Daw (2017), com os preprints como pista | o M-MEM parece sem fonte quando tem |
| T-e2 | seção 2.5, passo 3 | a trajetória sem a ordem memória → hábito | a predição de Lengyel e Dayan (2007) como [HIPÓTESE] com fonte | perde-se uma predição testável de graça |
| — | seção 14: a regra de Luce; os acumuladores com inibição mútua | SEM FONTE | Luce (1977), só título; Usher e McClelland (2001), resumo | a PE-5 fica sem a fonte da alternativa |
| — | seção 14: a curva das urgências; "o mais recente do lugar manda" | SEM FONTE | **continuam SEM FONTE** | — |

**As decisões que estas trocas pedem** (a recomendação primeiro):
- **D-0, aplicar na espec as trocas T-a1 a T-e2 e as duas linhas sem número.** Recomendação: **aplicar todas, numa tarefa de
  documentação curta,** antes da primeira vida do protótipo (a nota da PE-1 pede os SEM FONTE trocados antes dela). Custo de errar:
  aplicar sem rever pode levar à espec uma leitura nossa como se fosse da fonte; por isso cada troca acima separa "a fonte diz" de
  "leitura nossa".
- **D-1, a PE-4 diante do Doya.** Recomendação: **manter a decisão** (a excitação no `g_apr`, atrás da subchave desligada) e só escrever a
  divergência. O plano de análise do protótipo pode registrar, como leitura secundária, se a excitação mexe mais na exploração que na
  taxa. Custo de errar: mudar agora para o `g_exp` troca uma escolha sem fonte por outra, já que o mapeamento do Doya é teórico e cita
  outros moduladores; não registrar deixa a escolha sem a ressalva.
- **D-2, a predição de Lengyel e Dayan no plano do protótipo.** Recomendação: **entrar como leitura descritiva, sem gate.** Custo de
  errar: como gate, um teste novo cuja potência ninguém calculou; fora do plano, perde-se uma predição de graça.

## 9. Nenhuma novidade

Cada peça do substrato da espec tem precedente verificado. Não se pode alegar que o Digilab é o primeiro em nenhuma destas:
- **a rede pequena de unidades contínuas como sistema nervoso de agente:** Beer (1995); Yamauchi e Beer (1994);
- **o hebbiano com modulação difusa em criatura ou em agente que forrageia:** Cliff e Grand (1999); Niv et al. (2002); Nogueira et al.
  (2013);
- **as motivações vindas do corpo, com "hormônios", numa criatura:** Cañamero (1997);
- **a memória episódica guiando a busca de comida:** em animais, Clayton e Dickinson (1998); em agentes, Blundell et al. (2016) e
  Gershman e Daw (2017);
- **o inato e a plasticidade na mesma rede:** Soltoggio, Stanley e Risi (2018), além das regras 1 e 2 da skill `literatura-digilab`.

O que a espec pode dizer é o que ela **testa:** os testes de mecanismo da seção 10 e as sondas de mesmo `u`. A junção em inteiros com
paridade Python e TS é exigência de engenharia do repositório, e também não é afirmada como novidade.
