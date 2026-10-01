# DEFINIÇÕES DA V2 — as seis restrições da literatura sobre os gates PROPOSTOS

Status: **DECIDIDO pelo Matheus em 2026-10-01** (D1–D11 aprovadas como recomendadas; tabela no fim). Os números dos gates
continuam PROPOSTOS até o referendo do plano. Este documento não decide desenho, não muda código e não autoriza run. Ele fixa, para cada gate
PROPOSTO de `docs/PLANO_V2_PESQUISA.md` (fase 1) que a busca bibliográfica da V2 restringiu, **a definição, a justificativa e o artefato
que vai medi-la**. Tudo vale até o referendo do Matheus. A última seção planeja um pedido novo dele (frutas, gosto hedônico e vício) só
como pergunta.

**Fontes.** Busca da V2 (2026-10-01): `V2_SINTESE_Q1_Q7.md` e `v2_referencias_verificadas.csv`, em `docs/referencias/`
(no repositório desde a decisão D9). Rótulos de verificação da coluna `verificada` são vinculantes; nada NÃO LOCALIZADA é citado aqui. Números da v1
apontam o artefato em disco; números novos não existem ainda (nenhuma run foi feita).

**Não reabre nada.** A hipótese central da v1 continua refutada (`artifacts_confirmatoria/resultado.json`), a linhagem continua encerrada
(`docs/PLANO_LINHAGEM_ALIFE.md`) e a pergunta do efeito do dono neste motor continua encerrada (`docs/LEITURA_CONSOLIDADA_DONO.md`). A V2 pergunta
sobre um aprendiz novo.

---

## 1. Gate de divergência (G3: JSD entre donos coerentes ≥ 0,10 bit)

**O que a literatura impõe.** Os trabalhos de feedback humano medem "o treinador deixou marca" por sucesso na tarefa, eficiência amostral e
comparação com o desempenho do próprio treinador (MacGlashan et al., arXiv:1701.06049; Knox e Stone, `10.1145/1597735.1597738`; Warnell et al.,
`10.1609/aaai.v32i1.11485`; todos VERIFICADA). Não foi localizado precedente de divergência de política entre treinadores como métrica primária
(`V2_SINTESE_Q1_Q7.md`, Q1; busca com cobertura limitada, sem OpenAlex).

**Definição.**
- **G3 continua como está** (JSD entre donos coerentes ≥ 0,10 bit, IC fora de 0,02), declarado como **convenção do projeto, sem referente externo**.
- **De onde vem o 0,10:** é do `docs/PLANO_V2_PESQUISA.md` (fase 1, G3). A âncora é a v1: JSD média entre braços 0,0204 bit, dentro do braço 0,0131 e
  piso de ruído máximo 0,0125 (`artifacts/divergence.json`: `jsd_media_entre_bracos`, `jsd_media_dentro_do_braco`, `piso_ruido_maximo`). O 0,10 é
  cerca de 5 vezes a separação da v1 e 8 vezes o piso de ruído. É um alvo de efeito, não um valor tirado da literatura.
- **Métrica comparável, reportada ao lado (G3-T, sem gate próprio na fase 1):** **acerto na tarefa ensinada**. A tarefa do dono sintético está
  escrita no código (`digilab/donos.py`, `julgar_acao`: a ação que ele elogia ou repreende em cada situação). Mede-se:
  1. a fração de decisões do pet que o dono elogiaria, ao longo dos 14 dias (curva de aprendizado);
  2. a eficiência amostral: quantos sinais do dono até o pet chegar à metade do caminho entre o instinto e o máximo da curva;
  3. a comparação com o "desempenho do treinador": a política ótima do próprio dono (seguir `julgar_acao` sempre) é o teto, e o instinto é o piso.
  Os três por dono coerente, contra o aleatório e o "só cuidado" (seção 3), com IC por bootstrap sobre sementes.
- **Leitura:** passar G3 sem G3-T subir diz que os donos deixaram políticas diferentes, mas não que ensinaram. Os dois são reportados juntos.

**Artefato.** `artifacts_v2_l1/validacao/divergencia.json` (G3) e `artifacts_v2_l1/validacao/tarefa.json` (G3-T), gerados pelas funções de
`digilab/metrics.py` (a regra "métricas existem uma vez só" vale: G3-T entra lá, não no script da run). Plano: `docs/PLANO_ANALISE_V2_L1.md`.

## 2. Gate de fator explicável (G4: ≥ 50% das decisões)

**O que a literatura impõe.** A decomposição em módulos nomeados é desenho estabelecido (Brooks, `10.1109/jra.1986.1087032`; Bryson,
`10.1007/3-540-36559-1_7`; Jacobs et al., `10.1162/neco.1991.3.1.79`; Creatures, `10.1023/A:1010042522104`), mas **não foi localizado** estudo
mostrando que modularidade melhora a legibilidade sob **capacidade igual**. O precedente que mede o custo de um gargalo interpretável é Concept
Bottleneck Models (Koh et al., arXiv:2007.04612, VERIFICADA), em classificação de imagem.

**Um problema que a v1 já mostra.** A regra de honestidade dá fator explicável em 34% a 76% das decisões ao **instinto** e em 13% a 18% ao bandit
(`artifacts_expressao/legibilidade.json`, `vida.*.fracao_com_fator`: atencioso-instinto 0,342, relapso-instinto 0,757; atencioso-bandit 0,185,
relapso-bandit 0,133). Como o lobo de impulsos da V2 contém as regras do instinto (`digilab/policies/lobos.py`), **o G4 pode passar sem que nada
tenha sido aprendido**.

**Definição.**
- **G4 é medido só sobre o que foi aprendido:** a fração de decisões em que a contribuição do **lobo de decisão aprendido** (a diferença entre os
  pesos atuais e os do prior) muda a escolha e é atribuível a um fator nomeado. É o critério da v1 ("só quando o termo aprendido mudou a escolha",
  `CLAUDE.md`, "Honestidade do fator do bandit") aplicado aos lobos. A fração bruta (com o instinto) é reportada ao lado, sem gate.
- **Braço de controle de capacidade equivalente sem módulos:** um aprendiz com o **mesmo número de pesos inteiros, as mesmas entradas, a mesma regra
  de atualização e as mesmas sementes**, sem lobos nomeados (uma única camada de decisão sobre todas as entradas). A atribuição nele usa os mesmos
  grupos de entrada como "pseudo-lobos". A afirmação "a modularidade compra legibilidade" só pode ser feita se o G4 dos lobos superar o G4 do controle
  com IC fora de zero.
- **Custo de desempenho do gargalo (como no CBM):** o acerto na tarefa ensinada (G3-T, seção 1) dos lobos menos o do controle, com IC. É reportado
  sempre, passe ou não o G4.

**Artefato.** `artifacts_v2_l1/validacao/legibilidade.json` (G4 aprendido, G4 bruto, por braço, lobos e controle) e
`artifacts_v2_l1/validacao/custo_gargalo.json`. O controle entra no `docs/PLANO_ANALISE_V2_L1.md` (D2, aprovada).

## 3. Braço "só cuidado" (V2-H0)

**O que a literatura impõe.** A literatura de métodos de treino de cães compara métodos (China et al., `10.3389/fvets.2020.00508`; Casey et al.,
`10.1038/s41598-021-97743-0`; Vieira de Castro et al., `10.1371/journal.pone.0225023`; Hiby et al., `10.1017/s0962728600026683`; revisões de Ziv,
`10.1016/j.jveb.2017.02.004`, e Guilherme Fernandes et al., `10.1016/j.applanim.2017.07.001`), mas nos estudos localizados o método aversivo é ao
mesmo tempo sinal de ensino e agressão ao bem-estar, e **nenhum tem braço de cuidado isolado** (`V2_SINTESE_Q1_Q7.md`, Q3). O molde conceitual da
separação é Darling e Steinberg (`10.1037/0033-2909.113.3.487`): estilo (o contexto em que a criação acontece) × prática (o conteúdo ensinado).

**Registro.** O braço "só cuidado" é **contribuição metodológica do projeto**, não lacuna de citação: é a operacionalização de uma separação que os
estudos de treino animal localizados não fazem. Ressalva obrigatória junto: é resultado de busca com cobertura limitada (sem OpenAlex), então se diz
"não localizamos", nunca "ninguém fez".

**Definição.**
- **Braço "só cuidado" acoplado (yoked):** para cada ovo e ambiente do braço atencioso, um braço com a **mesma semente e as mesmas ações de cuidado nos
  mesmos ticks** (alimentar, limpar, levar ao banheiro, tratar lesão), copiadas do registro do atencioso, e **sem nenhum sinal de ensino** (elogiar,
  repreender). Acariciar é ambíguo (cuidado afetivo ou sinal): entra como cuidado por padrão, com a variante sem acariciar como sensibilidade (D3).
- **Volume:** o acoplado tem menos interações que o atencioso (os sinais de ensino somem). Reporta-se a diferença de volume; a comparação central é
  atencioso × só cuidado com o **mesmo cuidado**, não com o mesmo volume.
- **Análise por norma de reação** (Dingemanse et al., `10.1016/j.tree.2009.07.013`): para cada medida (G3-T, eixos do caráter, decisões na situação
  ensinada), um modelo com **intercepto = nível do pet na condição** (ensino + cuidado × só cuidado) e **inclinação = sensibilidade ao ambiente**
  (os 4 ambientes do desenho do E1, `experiments/run_natureza_criacao.py`). O efeito do ensino é a diferença de intercepto; a mudança de inclinação diz
  se o ensino deixa o pet mais ou menos dependente do ambiente. Referência de magnitude para o componente do ovo: Dochtermann et al.,
  `10.1098/rspb.2014.2201` (~52% de variação genética aditiva na personalidade animal; a v1 mediu 4,9% para o desempenho,
  `artifacts_linhagem/natureza_criacao/especie_fixa/resultado.json`).
- **G5** (a divergência se mantém sem mortes e sem lesão) passa a ser lido junto: o que sobra de G3 no braço sem mortes e sem lesão **e** acima do
  acoplado.

**Artefato.** `artifacts_v2_l1/validacao/so_cuidado.json` (vidas acopladas e diferenças) e `artifacts_v2_l1/validacao/norma_de_reacao.json`
(interceptos, inclinações e IC). O ajuste do modelo misto entra em `digilab/metrics.py` (biblioteca padrão), com teste.

## 4. As duas alavancas (1a ambiente mínimo; 1b aprendiz com lobos)

**O que a literatura impõe.** Ela apoia a consequência pós-ingestiva como mecanismo de aprendizado **do animal**: controles pós-ingestivos positivos
(Sclafani, `10.1006/appe.2000.0370`), recompensa sem receptor de gosto (de Araujo et al., `10.1016/j.neuron.2008.04.003`), preferência por infusão
intragástrica (Blusk, Ackroff e Sclafani, `10.1016/0195-6663(92)90038-8`) e a revisão de substratos (Bodnar, `10.1016/j.appet.2016.12.015`). Em todos,
**não há treinador no laço**: nada localizado mostra que mais decisões com consequência aumentam o efeito do treinador (`V2_SINTESE_Q1_Q7.md`, Q4).

**Atenção à escolha já feita.** O Matheus escolheu a **bola** para a 1a (`docs/V2_RODADA_1.md`). A consequência da bola é no humor, não pós-ingestiva:
o apoio específico acima é para **comida**. Para a bola sobra o apoio geral de cognição mínima (van Duijn et al., `10.1177/105971230601400207`) e de
affordances (Khetarpal et al., arXiv:2006.15085). A seção 7 trata das frutas.

**Definição: duas perguntas separadas, com status diferentes no plano.**
- **1a-pet (apoiada na literatura):** com a alavanca, o pet aprende pela própria consequência. Teste **sem dono no laço** (só cuidado mínimo, nenhum
  sinal de ensino): a escolha muda na direção da consequência em relação ao instinto, com IC. Métrica: fração de escolhas da opção com consequência
  melhor, por dia.
- **1a-dono (sem apoio; hipótese do projeto):** a alavanca **aumenta o efeito do dono**. Teste: interação no desenho 2 × 2 ambiente (com, sem) ×
  dono (coerente, aleatório) sobre G3 e G3-T. O plano diz, por escrito, que **1a-pet passar não é evidência para 1a-dono**.
- **Ordem:** 1a sozinha e 1b sozinha (cada uma na sua versão de pet), cada uma com as duas perguntas; só depois as duas juntas. Nenhum braço com as
  duas alavancas novas antes de cada uma passar sozinha (`docs/V2_TRABALHO_PARALELO.md`, seção 4).

**Artefato.** `artifacts_v2_a1/{pet,dono}.json` e, para o desenho combinado, `artifacts_v2_a1_l1/interacao.json`. Plano: `docs/PLANO_ANALISE_V2_A1.md`.

## 5. Peças do Dwarf Fortress

**O que a literatura impõe.** As mecânicas do jogo são **NÃO VERIFICADAS EM FONTE PRIMÁRIA** (wiki de fã; `v2_referencias_verificadas.csv`, linha DF).
O capítulo de Adams (`10.1515/9783839453452-007`) analisa narrativa, não valida mecanismo. Cinco peças têm análogo científico **na forma**; uma está
**contestada** (`V2_SINTESE_Q1_Q7.md`, Q5).

**Definição: quais entram e com que ressalva.** Cada peça que entrar carrega no código (docstring), na tarefa e em qualquer texto a ressalva abaixo,
literalmente: "inspirada no Dwarf Fortress; o análogo citado é inspiração declarada, não validação".

| peça | entra? | quando | ressalva específica |
|---|---|---|---|
| Espaços de memória com disputa por força | **Só como regra de capacidade de engenharia** (já existe na v1: `digilab/memoria_espacos.py`, 4+2 espaços, a mais forte fica) | L2, se a memória for usada | "A disputa por força é uma regra de capacidade do projeto, não um modelo de esquecimento: a explicação por competição é **contestada** na psicologia (Raaijmakers e Jakab, `10.3758/s13421-011-0131-y`)." |
| Relembrar reaplica a emoção e altera a memória | Sim, candidata | L2 | "Análogo na forma da reconsolidação (Nader, Schafe e LeDoux, `10.1038/35021052`; modulação emocional em McGaugh, `10.1101/lm.93405`); não é modelo de reconsolidação." |
| Tarefa pedida × necessidade própria ("duas prioridades") | Sim, candidata | L3 | "Análogo do conflito aproximação-evitação (Elliot, `10.1007/s11031-006-9028-7`); a regra de arbitragem é do projeto." |
| Facetas × valores filtrando a emoção | Adiada | fase 3 (genoma novo) | "Análogo na forma do modelo componencial (Scherer, `10.1080/02699930902928969`) e do desenvolvimento da personalidade (Stamps e Groothuis, `10.1111/j.1469-185x.2009.00103.x`); traços correlacionados, não independentes." |
| Estresse em duas escalas com recuperação assimétrica | Adiada | depois de L2, com G5 valendo também sem ela | "Análogo na forma da carga alostática (McEwen e Stellar, `10.1001/archinte.1993.00410180039004`; McEwen, `10.1056/nejm199801153380307`). Risco do projeto: é outro canal de cuidado." |
| Memória nuclear que muda a personalidade | Adiada | só com o braço "só cuidado" no desenho | "A literatura dá mudança de traço **gradual e ligada a metas** (Conway e Pleydell-Pearce, `10.1037/0033-295x.107.2.261`; Specht et al., `10.1037/a0024950`), não uma memória única virando traço: o apoio é **parcial**." |

**Artefato.** Nenhum agora. Cada peça que entrar ganha a própria tarefa, versão de pet e plano; a ressalva vira item de checagem do PR.

## 6. Gate de replay e paridade (G1)

**O que a literatura impõe.** Não foi localizado trabalho sobre paridade bit a bit entre Python e navegador do mesmo aprendiz: é engenharia sem
benchmark (`V2_SINTESE_Q1_Q7.md`, Q6). A justificativa de por que o requisito importa é Polhill, Izquierdo e Gotts (`10.1016/j.envsoft.2004.10.011`,
VERIFICADA): em modelos baseados em agentes, o ponto flutuante muda resultados entre implementações; Goldberg (`10.1145/103162.103163`) dá o porquê.
Aritmética inteira para redes treináveis tem precedente em Jacob et al. (`10.1109/cvpr.2018.00286`).

**Critério de aceitação (G1).**
1. **Replay Python:** a mesma semente e o mesmo log reconstroem a vida com **igualdade exata** de ações, pesos inteiros e estado interno do aprendiz em
   cada checkpoint (sha256 do estado serializado), na mesma máquina.
2. **Entre plataformas Python:** ações e pesos inteiros **idênticos**; os floats do estado do pet (que vêm do motor da v1, com `sin`/`cos`) com erro
   relativo ≤ 1e−9, a regra que já vale (`tests/test_canonico_intacto.py`).
3. **Python → navegador:** gabarito gerado pelo Python com K vidas (K fixado no plano) e N checkpoints cada; o motor TS reproduz **ações e pesos
   inteiros idênticos** e o estado do pet com erro relativo ≤ 1e−12, a mesma tolerância da paridade da M1 (`web/app/test/confianca.test.ts`). Roda no
   Node (Vitest) e no Chromium (e2e), porque o Chrome difere da libm no último bit de `exp`/`log` (`CLAUDE.md`, gabaritos).
4. **Falhou qualquer item:** para tudo, pela regra do projeto ("se um teste de replay quebrar, pare tudo").

O aprendiz da V2 usa só inteiros e ativação sem funções transcendentais (`docs/PLANO_V2_PESQUISA.md`, fase 1), então os itens 1–3 são exigíveis por
igualdade exata no que é dele. Registrado como **critério do projeto, sem benchmark externo**.

**Artefato.** Testes `tests/test_lobos.py` (G1 e G2 do L0 já passam: PR #108) e, na web, `web/app/test/paridade_lobos.test.ts` com o gabarito
`web/app/test/gabaritos/lobos_python.json` (a gerar quando a frente da web dos lobos abrir, pets v11).

## 7. Frutas, gosto hedônico e vício (pedido do Matheus, 2026-10-01) — planejamento, não desenho

O Matheus quer **frutas diferentes**, uma **variável de gosto hedônico** com preferências do pet e a possibilidade de **vício, como no Creatures**.
Aqui fica só o que isso pede da pesquisa; o desenho é dele.

**O que a literatura sustenta.**
- Preferência por comida aprendida pela consequência pós-ingestiva, separada do gosto oral: Sclafani (`10.1006/appe.2000.0370`), de Araujo et al.
  (`10.1016/j.neuron.2008.04.003`), Blusk, Ackroff e Sclafani (`10.1016/0195-6663(92)90038-8`), Bodnar (`10.1016/j.appet.2016.12.015`). Todas
  VERIFICADA. Isso apoia frutas com **gosto** (oral) e **efeito** (consequência) separados.
- A distinção "gostar" (liking) × "querer" (wanting) × aprendizado (Berridge e Robinson 1998, `10.1016/S0165-0173(98)00019-8`; Berridge et al. 2009,
  `10.1016/j.coph.2008.12.014`) está no corpus DigiBrain, **mas não na tabela verificada do projeto**: verificar antes de citar como base.
- **Vício:** nenhuma referência sobre dependência está verificada pelo projeto. O mecanismo de vício do Creatures vem de documentação de jogo e wiki
  de fã: **NÃO VERIFICADO EM FONTE PRIMÁRIA**. Os artigos do Creatures verificados (Grand e Cliff, `10.1023/A:1010042522104`; Cliff e Grand,
  `10.1162/106454699568683`) falam de bioquímica artificial e modulação, não de vício especificamente.

**O que isso pede da V2.**
- **É uma alavanca nova** (ambiente), na família da 1a: vale a seção 4 (1a-pet apoiada; 1a-dono sem apoio) e o G5.
- **Risco principal:** comida é canal de cuidado (fome → saúde → morte, `digilab/state.py`), e vício acopla gosto a saúde. Um efeito de dono que venha
  por aí é cuidado, não ensino (`docs/LEITURA_CONSOLIDADA_DONO.md`). Por isso o "só cuidado" acoplado (seção 3) é obrigatório em qualquer braço com
  frutas.
- **Separar no desenho três variáveis** (operacionais, sem afirmar experiência subjetiva do pet): necessidade (fome), gosto hedônico (preferência inata
  ou aprendida por fruta) e efeito (consequência no corpo). Vício seria uma quarta: o **querer** que cresce com o consumo enquanto o **gostar** não
  cresce ou cai. Cada uma com parâmetro próprio em `digilab/config.py` e RNG própria se houver sorteio.
- **Determinismo e web:** frutas e vício entram como eventos do log e numa versão de pet própria (a ordem cumulativa das versões é do coordenador).
- **Pesquisa pendente** (para o Claude Science, antes do desenho): literatura verificada de dependência e sensibilização de incentivo; modelos
  computacionais de vício em agentes; fonte primária do mecanismo do Creatures.

---

## Decisões (todas aprovadas pelo Matheus como recomendadas, 2026-10-01)

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| D1 | G3: manter o 0,10 bit absoluto, declarado como convenção sem referente, com G3-T ao lado | Manter o 0,10 e reportar G3-T sempre; não criar gate novo para G3-T na fase 1 | Trocar o limiar depois de ver dados vira ajuste olhando a amostra; sem G3-T, um revisor não tem com o que comparar |
| D2 | Incluir o braço de controle de capacidade equivalente sem módulos já na validação da L1 | Incluir: é barato (CPU) e é o único jeito de afirmar algo sobre legibilidade | Sem ele, "modularidade compra legibilidade" fica sem sustentação, e refazer a validação custa uma rodada inteira de sementes |
| D3 | Medir o G4 só sobre o aprendido (fração bruta sem gate) | Sim | Com a fração bruta, o G4 passa com o aprendizado desligado (o instinto já dá 34–76%) e o gate não mede nada |
| D4 | "Só cuidado" acoplado: acariciar conta como cuidado | Sim no braço principal; sem acariciar como sensibilidade | Se acariciar for ensino disfarçado, o acoplado carrega sinal de ensino e o contraste fica subestimado |
| D5 | Registrar o "só cuidado" como contribuição metodológica ("não localizamos"), nunca como primazia | Sim | Alegar primazia com busca de cobertura limitada é o tipo de afirmação que a revisão já bloqueou três vezes |
| D6 | Duas perguntas por alavanca (pet × dono), com 1a-dono explicitamente sem apoio | Sim | Ler 1a-pet como evidência de efeito do dono é exatamente a inferência que a literatura não sustenta |
| D7 | Peças do DF: espaços só como regra de engenharia; relembrar (L2) e duas prioridades (L3) como candidatas; o resto adiado | Sim | Entrar com estresse ou memória nuclear antes do "só cuidado" abre outro canal de cuidado e confunde o G5 |
| D8 | G1 com igualdade exata nos inteiros e tolerância só nos floats do motor da v1 | Sim | Aceitar tolerância nos pesos esconderia divergência que se acumula e quebra o replay depois de dias de vida |
| D9 | Trazer a busca da V2 (`V2_SINTESE_Q1_Q7.md`, CSV, BibTeX, verificação) para o repositório (`docs/referencias/`), hoje só na pasta `v1` sem commit | Sim, num PR próprio | Fora do git, as citações deste documento apontam para arquivos que podem sumir ou mudar sem registro |
| D10 | Frutas, gosto hedônico e vício: substituir a bola na 1a ou vir depois dela | Manter a **bola** como 1a (G5 satisfazível por desenho) e planejar as frutas como **alavanca seguinte**, depois de a bola passar, com o "só cuidado" obrigatório | Trocar a bola por frutas agora põe o primeiro teste da 1a dentro do canal de cuidado, onde a v1 já mostrou que todo efeito vira cuidado |
| D11 | Pedir ao Claude Science a pesquisa de vício e sensibilização de incentivo antes de desenhar as frutas | Sim | Desenhar vício só pelo Creatures é desenhar por wiki de fã, sem fonte primária |
