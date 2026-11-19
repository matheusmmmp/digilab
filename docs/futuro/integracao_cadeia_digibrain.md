# A integração da cadeia no DigiBrain modular: diagnóstico, recomendação e plano (2026-11-17, Claude Code, Opus 5.5)

**Status: as INT-1 a INT-9 (seção 9) estão DECIDIDAS pela recomendação, em 2026-11-17.** O Matheus escreveu, nesta sessão: "Aprovo as
INT-1 a INT-9 pela recomendação" (D-INT-9).
- **O que isso decide:** a ordem das etapas, o lugar e as regras do desenho.
- **O que continua PROPOSTO e SEM FONTE:** todo número novo do documento, como o K, o λ e o η do traço, o θ_dor e o corte da saturação
  da INT-4, salvo onde a fonte está escrita. Esses números se medem e se propõem no PR de cada etapa.
- **O que não muda:** as PV2-1 a PV2-10, salvo a ordem da PV2-10, que a INT-1 refaz em parte.

**A origem:** pedido do Matheus, repassado na íntegra pela sessão que abriu esta: "investigue como melhorar a experiência do pet virtual
por meio da integração entre órgãos, bioquímica, percepção, estado interno, memória, decisão, ação e aprendizado". Esta sessão não ouviu
o Matheus diretamente.

**Por que fica em `docs/futuro/`:** é desenho de código ainda sem tarefa, e o `docs/ONDE_VAI_CADA_DOCUMENTO.md` manda o desenho para cá.
A primeira etapa recomendada (seção 8) já tem tarefa e plano aprovados (o PV-2 da PET_VIVO). As três referências novas ficam em
`docs/referencias/v3_integracao_referencias_verificadas.csv`, que é o lugar das referências. O desvio está no D-INT-1.

## 0. O que foi feito, e com que evidência

**O commit analisado:** `origin/main` `35889558` (o merge do #972, 2026-11-17 16:07 -0300), na worktree `D:\Trab\digilab\v3-integracao-cadeia`.
Todos os números de linha valem nesse commit.

| tipo | o quê |
|---|---|
| **consultado** | o `CLAUDE.md`, a `TAREFA_V3_PET_VIVO`, o `RESULTADO_V3_PET_VIVO`, o `PLANO_ANALISE_V3_PET_VIVO_PV2`, a `AUDITORIA_V3_SUCESSO_CORPO`, a `TAREFA_V3_CADEIA`, a `TAREFA_V3_LIMPEZA` (status e etapas) e as seções 2 a 4 da `ESPEC_DIGIBRAIN_MODULAR`; o código de `digilab/digibrain/`, `corpo.py`, `motor_corpo.py`, as partes do olfato em `mundo.py` e as configs em `config.py`; os espelhos em `web/app/motor/` e `web/app/src/cerebro.ts`; os PRs pelo `gh` (#704, #705, #711, #736, #741, #809–#812, #940–#956, #945–#973, #953, #958, #964, #968); as tabelas de `docs/referencias/`; no vault, a revisão I do PET_VIVO (só a linha do Root et al. 2011) e a existência das notas citadas pelo plano do PV-2 |
| **executado** | só leitura: `git`, `gh`, `grep` e `sed`; consultas ao Crossref, ao OpenAlex e ao PubMed para as referências. **Nenhuma vida, nenhum teste, nenhuma run, nenhuma faixa de sementes** |
| **medido** | nada. Todo número de comportamento citado vem de um artefato ou de um relato de PR já existentes, com a fonte ao lado |
| **inferido** | toda leitura do que o código faria numa vida que ninguém rodou. Está marcada "(leitura do código)" |

**Como a leitura foi feita:** três subagentes de leitura (Claude Code, Opus 5.5) levantaram a cadeia no Python, o porte para o TypeScript
e o estado dos PRs. As linhas centrais foram conferidas à mão:
- `motor_corpo.py:411-448`, o r medido no mesmo tick;
- `motor_corpo.py:604-630`, o carinho fora do `receber_acao_dono`;
- `corpo.py:440`, o dormir sem estímulo;
- `config.py:2914`, o `tau_c`;
- `plast.py:75-82`, o incentivo cortado em 0;
- `mem.py:393-412`, a pista da memória;
- `sens.py:185-200` e `:360-366`, o M-SENS e o `ha_cheiro`;
- `config.py:2216-2264` e `mundo.py:488-517`, o órgão do Olfato;
- `web/app/motor/motor.ts:1210-1214`, a vontade do A no jogo.

As outras linhas são do levantamento e não foram reconferidas uma a uma.

**Lacunas das fontes:**
- **O vault está acessível.** Desta tarefa, só a linha do Root et al. 2011 da revisão I foi lida no texto. As notas `20 Temas/Pet vivo.md`
  e `30 Decisões e protocolo/PET_VIVO — decisões PV-0.md` foram conferidas só quanto a existir e ao resumo.
- **A VALUATION e o ELOGIO não estão na `main`.** Os números deles vêm dos corpos dos PRs abertos (#945 a #973; #953 e #968) e não foram
  conferidos contra os artefatos.

## 1. O diagnóstico do código atual

### 1.1 O cérebro que os ovos usam

**O REL da pesquisa** é o `SUBCHAVES_C4["REL"]` (`experiments/run_v2_digibrain_prototipo.py:114`, `:129-131`). Liga:
- o `p1`, o `p2`, o `m_mem` e a `persistencia`;
- o `cheiro_inato` (DX-3) e a `intencao_cheiro` (DX-4);
- a `memoria_autobio`, com o `controle_mem` "rel".

Fica desligada a `modula_g_apr`: o `g_apr` é constante e vale S (`afeto.py:119-120`).

**O jogo** (`VERSAO_PET` 38, `web/app/motor/digibrain/constantes.ts:71-90`, `:122`) usa o mesmo núcleo e mais:
- o olhar;
- o sono que segura;
- o lance do dono;
- os inatos do E1 e a guarda da fome no brincar (`equilibrio_e1.ts:76-79`).

**Nenhum gabarito de paridade junta a combinação inteira do v38.** Cada peça tem o dela (as notas do porte TS, seção 5).

### 1.2 A cadeia, elo por elo

Notação: S = 1024 é a escala do cérebro, C = 450 000 a do corpo, 1 tick = 1 minuto, e há uma decisão a cada Δ = 15 ticks
(`config.py:52`). "Pesquisa" é o REL na bancada do Python; "jogo" é o modular do v38.

| elo | entradas → saídas (onde) | estado entre decisões | escala | fixo / aprendido | chave; pesquisa e jogo | influência medida na decisão |
|---|---|---|---|---|---|---|
| **1. evento → corpo** | ações do pet, do dono e do mundo → químicos (`corpo.py:427-473`, `:820-826`, `:857-866`, `:969-1000`) | as quantidades dos químicos; as meias-vidas (`corpo.py:476-477`): estresse 1 440, dor 60, susto 30 ticks | tick | **fixo:** as tabelas de efeito das ações (PROPOSTAS, SEM FONTE; a auditoria do sucesso, seção 1); **a digestão é instantânea** (`taxa_digestao` = C) | `CONFIG_CORPO_QUIMICA`; nos dois | é a fonte de todo r (a auditoria do sucesso, seção 3) |
| **2. corpo → órgão** | o campo do cheiro no ponto de cada narina → leitura com limiar, adaptação e saturação (`corpo.py:368-384`) | a adaptação de cada narina (meia-vida 60 ticks) | tick | fixo (PROPOSTOS, `config.py:2216-2264`) | `ConfigOlfato`, **desligada**; ausente no TS | nenhuma: o modular **falha alto** com o receptor do órgão (`sens.py:192-194`) |
| **3. órgão / corpo → sinal** (M-SENS) | os 11 receptores e a `PercepcaoMundo` → falta, contexto, objetos (até 8), conjunções, `ha_cheiro` (`sens.py:327-391`) | a habituação por classe, integrador com τ = 120 ticks (`sens.py:355-356`) | decisão | fixo | nos dois | do cheiro, **só o bit** `ha_cheiro = direcao_cheiro != 0` (`sens.py:365`): a direção é um oráculo do mundo (`mundo.py:1849-1851`). A habituação das comidas é calculada e não pesa em nada (só o `w0_nov` do brincar) |
| **4. sinal → estado** (M-AFETO, M-ESTADO) | as faltas → urgências (curva inata, `afeto.py:95-97`), o `g_exp` (`afeto.py:121`), a valência V e a excitação E (`afeto.py:147-149`), a frustração F (`estado.py:144-169`), o compromisso C | V (τ 240), E (τ 120), F (sobe τ 60, desce τ 480), C | decisão | fixo; o `g_apr` constante | nos dois | **V e E não estão em nenhuma linha do W⁰**: só pesam pelo hábito H. **O C é um degrau:** `tau_c` = 15 = Δ dá k_C = S, e a persistência vai ao teto A_max na primeira decisão (`config.py:2914`) |
| **5. estado → intenção** (M-IMPULSO, M-ARB) | o z de 23 características → as unidades (comportamento, alvo) (`impulso.py:104-247`) → o reflexo do sono ou o sorteio proporcional (`arb.py:102-175`) | nenhum | decisão | **fixo:** W⁰, W⁰_tipo, W⁰_prox, W⁰_nov, ε, λ_sono; **aprendido:** o incentivo G (P1), o hábito H (P2), o termo M e a lembrança L (memória) | nos dois | o reflexo do sono decide de 15 % a 24 % das decisões da C4 (`RESULTADO_V3_PET_VIVO`, seção 1) e 20,4 % do REL na VALUATION (#945, relato). **Cada alvo visto é uma unidade a mais no sorteio** (seção 4.5) |
| **6. intenção → execução** | a unidade → a `AcaoPet` e o alvo (`adapt.py:164-175`, `:567-601`) → o motor anda 60 subunidades e come ou brinca se chegou (`mundo.py:1972-2073`) | a intenção I*, a busca guardada (DX-4) | decisão | as regras de fim: "meta", "sumiu", "desistiu" (3 decisões; 6 na busca), "trocou", "achou" (`estado.py:350-399`) | nos dois | **nenhuma interrupção por fome, dor ou fadiga**: só o reflexo do sono troca a intenção |
| **7. execução → consequência** | o corpo da decisão (`pc0`) e **o corpo logo depois dos estímulos da ação, no mesmo tick** (`pc1`, `motor_corpo.py:444-447`) → `r = 4 · Σ (falta₀² − falta₁²) / S` (`afeto.py:136-151`) | a pendência da decisão (`adapt.py:678-791`) | **o mesmo tick** | fixo: `ganho_r` 4, `r_norm` 2, pesos 1 para todos os drives | nos dois | **o que acontece nos 15 ticks seguintes não chega a decisão nenhuma** (seção 1.3) |
| **8. consequência → aprendizado** (M-PLAST) | o r → o P1 (`plast.py:95-137`) e o P2 (`plast.py:140-155`) | o desfecho `d̂[6 classes][11 receptores]` e o `andar`; o hábito `H[7][23]` | consumo; fim da opção | aprendidos: o P1 com passo S/4, o P2 com passo S/256 e teto S/2 | nos dois | o G-T1 do J5 passou no A (0,197); no modular, a ablação do aprendizado muda 9 de 15 medidas (EVIDENCIA A2, #952, relato) |
| **9. aprendizado → memória** (M-MEM) | consumos e visitas → episódios (`mem.py:213-226`); a autobiográfica (`mem.py:88-120`), consolidada uma vez por dia (`mem.py:425-475`) | até 16 episódios; recente, duradoura e central | consequência; dia | regras fixas de codificação e de consolidação (DECIDIDAS 2026-11-01, SEM FONTE) | nos dois | o cenário do lugar lembrado: a sonda `sem_memoria` mostra que a memória decide nas 5 sementes (`TAREFA_V3_CADEIA`, seção 9) |
| **10. memória → decisão futura** | a pista (fome > S/4 e nenhuma comida boa à vista) → o lugar de maior valor (`mem.py:393-422`); a lembrança L nas unidades que casam (`mem.py:276-357`) | os σ gravados | decisão | o σ é o r do momento da codificação e **nunca é reavaliado** | nos dois | a mesma do elo 9; a L é **o único caminho do REL para uma aversão aprendida por classe** |

### 1.3 O que fica fora do aprendizado (leitura do código)

1. **O intervalo entre as decisões não é creditado.** O r compara o corpo da decisão com o corpo logo depois dos estímulos da ação, no
   mesmo tick (`motor_corpo.py:444-447`). O decaimento, a recuperação do sono e o efeito dos gestos do dono acontecem entre o `pc1` de
   uma decisão e o `pc0` da seguinte. A única exceção é a `fala_unidades`, que lê o corpo da decisão seguinte só no chamar
   (`adapt.py:694-697`), e ela está desligada no REL.
2. **O r do dormir é 0 por construção.** O `DORMIR` não tem estímulo (`corpo.py:440`), então `pc1 = pc0`. A energia recuperada dormindo
   (1/240 de C por tick) não ensina nada a ninguém. O hábito de dormir só se forma pelo r de outras coisas no mesmo tick, que é 0.
3. **Não há consequência atrasada para aprender.** A digestão é instantânea, e não existe emissor com atraso (a dor depois da podre, por
   exemplo). Um traço de elegibilidade não teria o que medir nas vidas de hoje.
4. **Os gestos do dono não entram no cérebro.**
   - O `receber_acao_dono` só registra (`adapt.py:622-625`).
   - **O carinho nem chega a ele:** o `MotorCorpo._gesto` só repassa o tapa e chama o `mudanca_no_corpo` no carinho
     (`motor_corpo.py:620-630`), e o DigiBrain não tem esse gancho (o `grep` não acha `mudanca_no_corpo` em `digilab/digibrain/`).
   - Isso está de acordo com a regra de 2026-11-04 (o treino nunca por clicar) e com a auditoria do sucesso. O ELOGIO (#968) é quem
     acrescenta o gancho.
5. **O P1 só aprende no consumo de comida e no brincar com a bola** (`adapt.py:744-748`), sem contexto: o desfecho é por classe, não por
   lugar, hora ou estado.
6. **O incentivo é cortado em 0** (`plast.py:82`). O pet aprende que uma classe faz mal (d̂ negativo), mas o incentivo dela fica 0 e
   nunca vira aversão. A aversão à podre vem só do W⁰_tipo inato (−2S), e a aprendida, só da lembrança L.
7. **A memória não se revaloriza.** O valor do lugar é a soma dos σ gravados (`mem.py:359-381`). A pista olha só a fome. Um lugar onde
   o pet comeu com muita fome vale o mesmo quando ele está quase saciado.

### 1.4 O que a "rede neural" é de fato

A especificação já diz isto (`ESPEC_DIGIBRAIN_MODULAR`, seção 2.6), e o código confere. O texto ao jogador e os documentos não devem
prometer mais que isto.

- **É uma rede de taxa pequena,** com unidades (comportamento, alvo). A ativação é uma soma linear de termos inteiros,
  `φ = clamp(·, 0, 4S)` (`impulso.py:156-247`).
- **Não é treinada por gradiente** e não tem pulsos, dendritos nem conectividade aprendida.
- **Os pesos aprendidos:**
  - o P1: o desfecho por classe e receptor (6 × 11) e o `andar`, uma média móvel do Δ observado;
  - o P2: o hábito por comportamento e característica (7 × 23), hebbiano de três fatores, `r_n × e_j`;
  - a memória: valores codificados nos episódios, que não são pesos.
- **Os integradores com vazamento:** a habituação, V, E e F. O C é um degrau no REL.
- **As regras fixas:** o reflexo do sono, os fins das intenções, a pista da memória, a consolidação e as sondas.
- **A escolha:** o sorteio proporcional inteiro, com uma chamada `rng.random()` da rng de política (`arb.py:148-153`). O reflexo dispara
  sem rng.
- **A recorrência é uma só,** pelo compromisso C. Com o C degenerado, ela vira "a intenção em curso ganha sempre o teto".

### 1.5 Implementado, mas desligado, sem integração ou sem avaliação

| capacidade | estado | evidência |
|---|---|---|
| o órgão do Olfato (2 narinas, adaptação, saturação) | **desligado**; incompatível com o modular hoje; ausente no TS | `config.py:2216`; `sens.py:192-194`; notas do TS, item 3 |
| a quimiotaxia do PV-2 | **plano APROVADO, sem código** | #741; `grep` sem resultado em `.py` e `.ts` |
| o `g_apr` modulado pela excitação | desligado (`modula_g_apr`) | `afeto.py:119-120` |
| a variação dos receptores (dC/dt) | não existe: o M-SENS lê só o nível | `sens.py:327-391` |
| a saciedade homeostática | não existe; só a do paladar, desligada | `corpo.py:950-967` |
| o paladar, o banheiro e a tela no modular | o paladar e o banheiro falham alto; a tela já tem um caminho próprio no M-SENS | `sens.py:185-194`; o ELOGIO parou no paladar (D-EL-9, #968) |
| a dor | sobe com o tapa e a luta e entra no r e na E, mas **nenhuma linha do W⁰ usa `u_dor`** | notas do TS, item 4; `config.py:2936-2947` |
| a digestão lenta | o parâmetro existe (`taxa_digestao`, `config.py:1554`), mas o REL e o jogo usam C | notas do TS, item 4 |
| o crédito do carinho | **no PR #968, aberto** | o ELOGIO |
| o conserto do reflexo do sono | **no #969, aberto, reprovado pela exaustão**; a frente foi encerrada sem conserto (D-VAL-23, #973) | a VALUATION |
| a explicação ao jogador | o painel lê o modular (`leitura.ts`), mas **o balão e a vontade do jogo vêm do cérebro A, parado** (`motor.ts:1210-1214` → `desejoLobos`) | notas do TS, item 6 |

### 1.6 Divergências encontradas (registro; nada foi corrigido aqui)

- **Docstrings velhas:**
  - `mem.py:45-47` e `adapt.py:17-19` dizem que a lembrança não entra na escolha; ela entra (`impulso.py:235-236`);
  - `estado.py:9-11` descreve o C como integrador;
  - `motor_corpo.py:37` chama o tapa de "sinal direto";
  - as docstrings do pacote ainda citam o `lobos.py`, que o pacote não importa mais (LZ2a).
- **O plano do PV-2, seção 0,** cita linhas que mudaram:
  - o `ha_cheiro` foi da linha 108 para a 365;
  - o `alvos_do_olfato`, das linhas 407 e 431 para as 488 a 517;
  - o `escolher_alvo`, da 296 para a 567.

  A tarefa da PET_VIVO ainda diz que a `v3c5` não está na `main`, e ela está (#705).
- **Cabeçalhos de status velhos:** a `TAREFA_V3_CADEIA` diz "PR aberto", e as três etapas estão na `main` (#809, #810, #812). O
  `PAINEL_V3` parou em 2026-11-07, e o #974, aberto, o atualiza.
- **O `cheiro_inato` e a `intencao_cheiro`** estão como "DECIDIDO, desligada por padrão" (`config.py:2807-2808`), mas o REL e o jogo as
  ligam sempre. Não é erro: o padrão do Python é o desligado. Fica anotado para quem ler o `config.py`.
- **O PV-2 previu que o placebo usa os bits baixos do `u`.** Conferido: o `alvos_do_olfato` só usa o bit 8 e o `u >> 8`
  (`mundo.py:499-512`). Os bits 0 a 7 estão livres nessa função. Os outros consumidores do `u` no motor não foram conferidos (INT-2).

## 2. A matriz bibliografia → mecanismo → adaptação → teste

**Os tipos:**
- **F**, argumento filosófico;
- **E**, resultado experimental em animal;
- **M**, modelo computacional ou teoria;
- **Eng**, relato de engenharia ou de produto.

"Consultado" diz o que foi efetivamente lido. Toda linha é VERIFICADA nas tabelas de `docs/referencias/`, salvo onde se diz o contrário.
Nenhuma referência sustenta parâmetro nem eficácia no jogo: elas sustentam que o mecanismo existe, ou o enquadramento.

| referência | tipo | consultado | mecanismo ou ideia sustentada | limitação | adaptação ao DigiLab | teste (seção 6) |
|---|---|---|---|---|---|---|
| Dreyfus 1972/1992, *What Computers Still Can't Do* (sem DOI; registro pela resenha `10.2307/1575958`) | F | o texto do editor na resenha; **o livro não foi lido** (`v3_dreyfus_referencias_verificadas.csv`) | a crítica à máquina sem corpo e, na 2ª edição, às redes | o argumento da relevância e as quatro suposições são do texto, não lido | a pergunta de fundo: quem decide o que é relevante para o pet? Hoje somos nós, pelas tabelas do corpo | nenhum direto; enquadra a T4 e a T5 |
| Dreyfus 2002, `10.1023/A:1021351606209` | F | texto completo, na rodada de 2026-11-16 | o sucesso, num agente com corpo, deveria ser a satisfação do próprio agente | não diz como medir | já usada na auditoria do sucesso: o r vem do corpo, mas a direção das tabelas é nossa | T5 (o efeito adverso independente da comida) |
| Braitenberg 1984, *Vehicles* (sem DOI; registro pela resenha `10.2307/2185146`) | F, experimento de pensamento | o texto do editor no OpenAlex; **o livro não foi lido** (D-INT-2) | comportamento rico a partir de acoplamentos sensor-motor simples | experimentos de pensamento, sem dado | manter a busca pelo cheiro **no laço sensor-motor** (a pirueta no executor), e não numa representação da direção (PV2-2, PV2-3) | T1, T8 |
| Clark 1997, *Being There*, `10.7551/mitpress/1552.001.0001` | F | metadados no Crossref e textos do editor no OpenAlex; **o livro não foi lido** | cérebro, corpo e mundo em causação circular; o cérebro como controlador da atividade corporificada | não sustenta mecanismo nenhum | a percepção ativa: o pet anda para sentir, e a variação do que sente decide quando virar | T1 |
| Thompson 2007, *Mind in Life* (sem DOI; registro pelas resenhas `10.1007/s10743-009-9057-7` e `10.1353/utq.0.0350`) | F | o sumário dos capítulos no OpenAlex; **o livro não foi lido** | a mente entendida a partir da organização do vivo; emoção e valência como dinâmica do organismo | só enquadramento | só na linguagem: nunca dizer que o pet é autônomo nesse sentido | nenhum |
| Varela, Thompson e Rosch 1991, `10.7551/mitpress/6730.001.0001` | F | resumo do editor (tabela Dreyfus) | a cognição corporificada e vivida | não sustenta mecânica | o mesmo do Thompson | nenhum |
| Pierce-Shimomura, Morse e Lockery 1999, `10.1523/JNEUROSCI.19-21-09557.1999` | E e M | **resumo relido no PubMed nesta sessão** (PMID 10531458); a tabela `v3c5` | o início das piruetas se correlaciona com dC/dt, e não com a concentração absoluta; a pirueta é mais provável descendo o gradiente; um modelo estocástico que só impõe essa correlação basta para a quimiotaxia | é verme, em gradiente químico, em segundos; o resumo não dá o tamanho da janela do dC/dt | o acumulador da queda e a pirueta do OLF-DC; a janela é a decisão do jogo (15 ticks), escolha nossa | T1 (o OLF-DC e o OLF-DCV contra o OLF-0 e o OLF-PLA) |
| Iino e Yoshida 2009, `10.1523/JNEUROSCI.3633-08.2009` | E e M | o resumo (`v3c5`) | o cata-vento (curva para o lado mais concentrado) junto da pirueta; os dois juntos são mais eficientes em simulação | o cata-vento lê a direção | a tropotaxia do motor (o `cheiro_virar` para a narina mais forte) fica no executor, e o cérebro não lê a diferença entre as narinas (PV2-3) | T1 (o OLF-0 é o cata-vento sozinho) |
| Gomez-Marin, Stephens e Louis 2011, `10.1038/ncomms1455` | E | resumo e texto completo (`v3c5`) | a queda integrada durante a corrida decide quando virar; a varredura da cabeça decide para onde (81,6 % dos giros começam gradiente abaixo) | é larva de mosca | o OLF-DCV: o acumulador decide quando, e a varredura das narinas decide para onde. Os 81,6 % são contexto, não alvo | T1 (a medida "a hora da virada") |
| Root et al. 2011, `10.1016/j.cell.2011.02.008` | E | **resumo relido no PubMed nesta sessão** (PMID 21458672); a linha da revisão I no vault | a fome aumenta a atividade pré-sináptica de neurônios olfativos específicos pelo sNPF; a insulina reprime o receptor; o ramo é necessário para a busca faminta, e facilitá-lo numa mosca alimentada basta para imitar a busca | é Drosophila; o resumo não dá o tamanho do ganho | o OLF-G (`div_arred(c · (G0 + u_fome), G0)`, PV2-5). **O freio pela saciedade** (a insulina) fica para quando houver o receptor da saciedade | T1 (o G-ESTADO), T2 |
| Flavell et al. 2013, `10.1016/j.cell.2013.08.001` | E | o resumo (`v3c5`) | dois neuromoduladores opostos iniciam e prolongam estados duradouros ("ficar" e "percorrer") sobre circuitos motores rápidos | é verme | a candidata da frente "o corpo modula" (seção 4.2): estados lentos que mudam os ganhos, sem código agora | T2, T8 |
| Keramati e Gutkin 2014, `10.7554/eLife.04811` | M (teoria normativa com simulação) | resumo e texto completo, na rodada `v3c5`; **não reaberto nesta sessão** | a recompensa primária como redução do desvio homeostático; buscar recompensa e manter a estabilidade coincidem sob essa definição | não diz a escala temporal do jogo nem os pesos dos drives | **já é o r do modular** (`afeto.py:136-151`). Novo seria só a linha de base do PV-3 e o r do intervalo (seção 4.3) | T4, T5 |
| Izhikevich 2007, `10.1093/cercor/bhl152` | M | **resumo relido no PubMed nesta sessão** (PMID 17220510) | a STDP deixa uma marca que dura alguns segundos e que a dopamina converte em mudança de peso; a atividade aleatória durante a espera não atrapalha; um sinal global e difuso escolhe as sinapses certas | neurônios de pulso, segundos; não diz nada sobre minutos de jogo | o traço de elegibilidade das decisões recentes, que decai por decisão e recebe o r do intervalo (seção 4.3). **A constante de tempo não se transfere:** a do jogo é escolha nossa, SEM FONTE | T4 |
| Gerstner et al. 2018, `10.3389/fncir.2018.00053` | M (revisão) | o resumo (citado na especificação, seção 2.4) | a coativação marca a sinapse, e o peso só muda se o terceiro fator chegar enquanto a marca existe | é sobre sinapses | a forma do traço: marca na decisão, terceiro fator na consequência | T4 |
| Frémaux e Gerstner 2016, `10.3389/fncir.2015.00085` | M (revisão) | o resumo (`dm_referencias_verificadas.csv`) | as regras de três fatores: pré, pós e modulador | o foco é a STDP; não sustenta o sinal homeostático como terceiro fator | o P2 de hoje e o P2 com o traço | T4 |
| Singh e Sutton 1996, `10.1007/bf00114726` | M | **só o título** (`dm_referencias_verificadas.csv`) | os traços de elegibilidade de substituição existem | o conteúdo não foi lido | o "substituir" em vez de "acumular" quando a mesma característica volta ao traço: só a pista do nome | T4 |
| Doya 2002, `10.1016/S0893-6080(02)00044-8` | M (teoria, sem teste próprio) | **resumo relido no PubMed nesta sessão** (PMID 12371507) | os neuromoduladores levam sinais globais que regulam os metaparâmetros: o erro de previsão, a escala temporal da previsão, a aleatoriedade da escolha, a velocidade da atualização | é proposta teórica, não medida | a tabela estado do corpo → metaparâmetro (seção 4.2): a urgência estreita a exploração (já é o `g_exp`), e o estado poderia mudar a duração do traço | T2 |
| Zhang et al. 2009, `10.1371/journal.pcbi.1000437` | M com dados de rato | resumo e texto completo (`v3c5`) | um fator fisiológico modula no ato o valor aprendido de uma deixa, sem reaprender | a forma "V + log κ" não foi reconferida | já é a revalorização do P1 (o `valor_previsto` com o estado de agora). A extensão leva a mesma conta à memória do lugar (seção 4.4) | T2, T3, T8 |
| Clayton e Dickinson 1998, `10.1038/26216` | E | o resumo (especificação, seção 4.6) | gaios lembram o quê, onde e quando, e aprendem depressa a não buscar o que estragou | não sustenta mecanismo | o lugar que perde valor e o lugar revalorizado pela necessidade de agora | T3, T8 |
| Gershman e Daw 2017, `10.1146/annurev-psych-122414-033625` | M (revisão) | o resumo (`v3c5`) | a memória episódica no aprendizado por reforço, para aprender com poucos dados e para consequências longas | revisão geral | o episódio como fonte de valor, já no M-MEM | T8 |
| Sutton, Precup e Singh 1999, `10.1016/S0004-3702(99)00052-1` | M | **só metadados** (`v3c5`) | o arcabouço das opções: a ação estendida no tempo | não sustenta afirmação de conteúdo | a intenção como opção, com início, continuidade, interrupção e término explícitos (seção 4.5) | T6 |
| Bacon, Harb e Precup 2017, `10.1609/aaai.v31i1.10916` | M | o resumo (`dm_referencias_verificadas.csv`) | o término da opção aprendido junto com a política interna | o término aqui é regra, não aprendido | a guarda de término como regra explícita e registrada; aprender o término fica fora | T6 |
| Grand e Cliff 1998, `10.1023/A:1010042522104` | Eng | **só metadados** (o resumo foi omitido pela editora; `v3c5`) | vale só para citar o periódico | não sustenta conteúdo | nenhuma; para o conteúdo, usar o Cliff e Grand 1999 | nenhum |
| Cliff e Grand 1999, `10.1162/106454699568683` | Eng | o resumo (`referencias_verificadas.csv`) | a rede dos norns com aprendizado hebbiano e modulação hormonal | é relato de produto, sem teste controlado | o precedente de desenho do P2 e da modulação difusa | nenhum |

**O que a literatura não sustenta (SEM FONTE):**
- todas as constantes de tempo do jogo (a janela do dC, o L da pirueta, a duração do traço);
- o sinal homeostático como terceiro fator (NÃO LOCALIZADA, especificação, seção 2.4);
- a comparação direta entre o crédito por opção e o traço de K decisões (NÃO LOCALIZADA, `dm_referencias_verificadas.csv`);
- toda tabela de efeito das ações no corpo.

## 3. As melhorias candidatas, avaliadas

### 3.1 A. A percepção ativa e a busca olfativa

- **O que existe:** o órgão com limiar, adaptação (meia-vida 60 ticks, isto é, 4 decisões) e saturação; a tropotaxia do motor; e a
  pirueta de um passo com uma narina (`mundo.py:488-517`). O cérebro lê só o bit `ha_cheiro`, que vem do oráculo.
- **O plano do PV-2 já responde à pergunta.** Ele separa:
  - o efeito do sensor: o OLF-0 contra o HOJE, descritivo;
  - o da frequência das viradas: o OLF-PLA, com a mesma taxa em hora sorteada;
  - o do momento das viradas: o OLF-DCV contra o OLF-PLA, o G-PV2-HORA.
- **Compatível com as PV2-1 a PV2-10,** com três conferências que o código ainda precisa fazer:
  1. **o M-SENS tem de aceitar o receptor do órgão por um caminho próprio,** como já faz com a tela (`sens.py:185-191`): fora dos drives,
     fora do r e fora das urgências (INT-3);
  2. **o "nível" que o cérebro lê é a média das duas narinas.** A diferença entre elas fica só no motor (PV2-3);
  3. **os tipos dos candidatos** (`cheiro_seguir`, `cheiro_virar`) têm de casar com a unidade `comer/cheiro` no `escolher_alvo`, e a DX-4
     tem de herdar o "achou" da busca. Hoje ele casa pelo tipo `cheiro` (leitura do código).
- **A adaptação ajuda a quimiotaxia:** um cheiro parado cai pela metade em 4 decisões. Então o nível sozinho engana o pet que fica
  parado, e a variação é o sinal útil. É a razão mecânica de o dC entrar no z (leitura do código, não medido).
- **O ganho do OLF-G:** com `u_fome` em [0, S] e G0 = 64, o ganho vai de 1 a 17. A revisão I escreveu `cheiro*(64+fome)>>6` sem dizer
  a escala da fome. Com a fome em 8 bits, o teto seria cerca de 5. O PV2-5 decidiu G0 = 64; o que fazer com isso é a INT-4.

### 3.2 B. A modulação pelo estado corporal

**Já ativos:** as urgências, o `g_exp` (a urgência estreita, o tédio alarga), a revalorização do P1, o reflexo do sono e o corpo de agora
na semelhança da lembrança.

**Desligados ou ausentes:** o `g_apr` pela excitação, a saciedade, a dor no W⁰ e a exaustão como químico.

| relação | origem | alvo | fórmula candidata (inteiros) | limites | atualização | controle |
|---|---|---|---|---|---|---|
| **B1. a fome aumenta o ganho do cheiro** | `u_fome` | o nível do cheiro no M-SENS | a do PV2-5 | [0, S] depois do ganho | por decisão | OLF-G contra OLF-DCV (G-ESTADO) |
| **B2. a saciedade freia o cheiro e o comer** | um receptor novo da saciedade: o integrador do que foi comido, com meia-vida | o ganho do B1 e o W⁰ do comer | `c_g = div_arred(c · (G0 + u_fome − mul(β_s, sac)), G0)`, com corte em [0, S] | `sac` ∈ [0, S] | por tick no corpo, lido por decisão | o braço com o receptor e β_s = 0 (o mesmo corpo sem o freio) |
| **B3. a dor interrompe** | a subida da dor desde o começo da intenção | o fim da intenção | `interrompe` se `dor₁ − dor_ini ≥ θ_dor` | θ_dor PROPOSTO | por decisão | a guarda com θ_dor = S + 1 (nunca dispara), com a mesma vida |
| **B4. a fadiga corta a exploração** | `u_energia` | o ε do `g_exp` | já existe pelo β_U (a maior urgência); fica como está | — | — | — |
| **B5. a dor e o susto estreitam a escolha** | `max(u_dor, u_susto)` | o `g_exp` | `g_exp ← g_exp − mul(β_D, max(u_dor, u_susto))` | [0, e_max] | por decisão | β_D = 0 |
| **B6. o estado muda a duração do traço** (pista do Doya 2002) | a urgência máxima | o λ do traço da seção 3.3 | `λ = λ₀ − mul(β_λ, max_u)` | [0, λ₀] | por decisão | λ constante |

**O nível de detalhe biológico:**
- **Basta um escalar por relação,** lido da química que o corpo já tem. Não há razão para modelar o sNPF, a insulina ou a serotonina.
  As fontes sustentam que o estado do corpo muda um ganho, e não a forma do ganho.
- **O que importa é o sinal (para que lado o ganho vai) e o limite (não saturar).** Os dois são testáveis no braço com o coeficiente
  zerado.

**A recomendação:**
- o B1 já está no PV-2;
- o B3 vai junto com a interrupção (seção 3.5);
- o B2 espera o receptor da saciedade, que é corpo novo e precisa de tarefa;
- o B5 e o B6 ficam como hipóteses, sem código, porque a VALUATION mostrou que mexer no que decide o sono e a fome tem efeito grande e
  difícil de prever (#949: tirar o reflexo dá +0,129 na taxa e piora a exaustão de 0,22 para 0,50, pelo relato).

### 3.3 C. As consequências atrasadas e o crédito

**A janela de hoje** é o mesmo tick (seção 1.3). O crédito por opção já existe (PE-3):
- a elegibilidade `e = z` da decisão que abriu a opção;
- a soma dos `r_n` de cada consequência dela;
- o P2 no fim (`estado.py:247-281`, `:355`; `adapt.py:794-799`).

O que chega e o que não chega ao aprendizado:

| acontecimento | chega? | por onde |
|---|---|---|
| a fome que cai ao comer | sim | o r do mesmo tick (a digestão é instantânea) |
| a digestão lenta (se ligada) | **não** | cairia no intervalo |
| a energia que volta dormindo | **não** | o intervalo; o r do dormir é 0 |
| o carinho e o tapa | **não** no REL; o carinho entra no ELOGIO (#968, aberto) | o ELOGIO usa uma janela W de decisões, com o P2 na linha do comportamento e o P1 na classe consumida (D-EL-9 a D-EL-13) |
| o tédio e a solidão que sobem parado | **não** | o intervalo |
| a intenção interrompida pelo reflexo | sim, em parte | o r somado até a troca vai ao P2 com "trocou" |

**O mecanismo recomendado: o r do intervalo, com um traço curto das decisões recentes.** É o "R2" da seção 5, depois do PV-2.

- **O que fica elegível:** as últimas K opções fechadas ou em curso, cada uma com o `e = z` dela, o comportamento b e a classe consumida,
  se houve. K é PROPOSTO = 4, isto é, uma hora de jogo.
- **Como nasce:** no `_fechar`, quando a opção entra no traço, com o peso `τ = S`.
- **Como decai:** a cada decisão, `τ ← mul(λ, τ)`, com λ PROPOSTO = S/2. O traço sai quando `τ < τ_min` ou quando passa de K.
- **Como substitui:** se a mesma opção volta (o dormir de novo, por exemplo), o peso volta a S, sem somar (pela pista do Singh e Sutton
  1996, que o título sustenta e o conteúdo não).
- **A conta do intervalo:**
  - no `_fechar` da decisão k+1, `r_int = div_arred(ganho_r · Σ (falta(pc1_k)² − falta(pc0_{k+1})²), S)`, sobre os mesmos receptores
    do r;
  - **a linha de base** contra o decaimento, que não depende da ação: `b ← integrar(b[ctx], r_int, k_b)`, com `ctx` ∈ {acordado,
    dormindo} (é o PV-3, `r − EMA(r)`);
  - o crédito é `δ = clamp(div_arred(r_int − b[ctx], R_n), −S, S)`.
- **A atualização** de cada item i do traço: `H[b_i, j] += mul(mul(g_apr, η_int), mul(mul(τ_i, δ), e_ij))`, com o corte em ±H_max. η_int
  é PROPOSTO, menor que η_h.
- **O atraso em ticks** entra só pelo λ por decisão. Como o intervalo é sempre de 15 ticks, um decaimento por decisão é um decaimento
  por tempo. Na pausa do jogo e no sono longo, o intervalo continua de 15 ticks, porque as decisões continuam.
- **Cada intervalo é contado uma vez só:** o par (`tick` de `pc1_k`, `tick` de `pc0_{k+1}`) fica no registro da atualização, e um teste
  confere que nenhum par se repete. O r do mesmo tick continua indo à opção como hoje, então o imediato e o posterior somam sem se
  sobrepor: cobrem trechos disjuntos do tempo.
- **Com ações no meio:** o traço reparte o δ pelo peso τ. A ação mais recente leva mais. Uma ação irrelevante no meio leva crédito
  também, e é isso que a T4 mede: o crédito na ação certa tem de crescer mais que na irrelevante quando o efeito segue a ação certa com
  regularidade.
- **O replay:** o traço, a linha de base e o `pc1` anterior ficam no estado do cérebro. O replay refaz a vida pelo log e passa pelos
  mesmos `_fechar`. Nenhuma rng nova.
- **Os limites:** K itens de 23 inteiros (cerca de 100 inteiros); uma conta de O(11) receptores e O(K · 23) produtos por decisão. A
  saturação fica no corte de H e no δ ∈ [−S, S].
- **A escala temporal:** o Izhikevich sustenta uma marca de segundos num neurônio. No jogo, a marca dura decisões de 15 minutos. **Nada
  se transfere em número:** a analogia é só de forma, marca e terceiro fator. O λ e o K se medem nas sementes dos testes e se propõem por
  adendo.
- **A ligação com o ELOGIO:** a janela W do #968 é um caso particular disto, um sinal entre decisões creditado às W últimas. A
  recomendação é a INT-5: as duas frentes usam a mesma estrutura de traço, para que não haja dois mecanismos de crédito no mesmo
  cérebro.
- **O risco:** creditar a energia do sono reforça o dormir com a energia baixa. A VALUATION mostrou que o sono já disputa com a fome.
  A guarda de forrageio (PV-0-10) é obrigatória no plano.

### 3.4 D. O aprendizado de desfechos corporais

- **O que atualiza o modelo vetorial hoje:** só o consumo de comida e o brincar com a bola, no mesmo tick.
- **O que fica de fora:**
  - o dormir num lugar;
  - o efeito depois de comer;
  - o que o dono fez;
  - o lugar.
- **A menor extensão** (o "R4" da seção 5) tem três partes, cada uma atrás de subchave:
  1. **D1, o efeito posterior do consumo:** a classe consumida fica elegível por `K_c` decisões (PROPOSTO = 4), e o Δ do intervalo menos a
     linha de base vai ao d̂ dela com o peso τ. É o mesmo traço da seção 3.3, aplicado ao P1.
  2. **D2, o contexto com volta à média:**
     - a previsão é `d̂[c] + o[c, ctx]`, com `ctx` = a região do mapa (as regiões do `MundoFisico`);
     - o desvio `o` aprende só o resíduo, `o ← o + mul(η_o, Δ − d̂[c] − o)`;
     - o geral aprende como hoje.
     - **A generalização inadequada fica contida** porque o geral continua valendo nas regiões sem dado (o `o` parte de 0), e uma
       mudança só num lugar mexe no `o` daquele lugar.
     - **A revisão depois de uma mudança:** o passo S/4 do P1 já revê em cerca de 4 consumos (a média móvel); o teste T3 mede.
  3. **D3, o incentivo com sinal:** `G ∈ [−G_max, G_max]`. Uma classe que faz mal passa a empurrar. O φ corta a ativação em 0, então o
     pior caso é a unidade não concorrer, e nunca uma ativação negativa.
- **Descansar num lugar:** é uma classe nova do P1, `dormir@regiao`, atualizada pelo r do intervalo do sono (precisa do R2). O incentivo
  dela entraria numa unidade nova `dormir/lugar` e criaria unidades: **espera a normalização do sorteio** (o R5).

### 3.5 E. As intenções e as sequências

- **O que existe:**
  - a intenção para comida, bola, lugar e busca pelo cheiro;
  - a sequência procurar → achar → comer, que já é uma opção composta (a DX-4 com o `_herdar_busca`, `estado.py:393-399`: o "achou"
    não frustra, e a ida seguinte herda a elegibilidade e o r).
- **O que falta:**
  - a interrupção por necessidade;
  - um compromisso que não seja degrau;
  - o término pela perda de progresso que não seja só a distância.
- **As condições explícitas da opção "buscar comida"** (o "R3"):

  | fase | começa | continua | interrompe | termina |
  |---|---|---|---|---|
  | procurar (o cheiro) | o sorteio escolhe `comer/cheiro` | o cheiro existe e a busca tem menos de 6 decisões sem progresso | **a dor sobe ≥ θ_dor; a energia cai abaixo de λ_sono (o reflexo); o susto ≥ θ_susto** | "achou" (comida boa à vista: passa a aproximar), "sumiu" (sem cheiro), "desistiu" |
  | aproximar | "achou", ou o sorteio escolhe `comer/item` | o alvo à vista e a distância caindo em menos de 3 decisões | as mesmas, mais **o alvo sumiu** | "meta" (comeu), "sumiu", "desistiu" |
  | consumir | chegou ao alvo | — | — | "meta" |

- **O fim "interrompeu":** é novo, não frustra (F não sobe, porque a culpa não é da intenção), e o r somado vai ao P2 como hoje.
- **A fome alta não interrompe a busca de comida.** Interrompe as outras intenções (o brincar, o lugar sem comida) só pela F3 urgências
  (D-UR-5), que já desenhou as guardas do M-ARB lendo a urgência crua. **Esta parte é da F3:** a recomendação é não duplicar.
- **O compromisso C:** com `tau_c = 15`, a intenção ganha o teto na primeira decisão. A interrupção por dor só aparece se a guarda
  disparar, porque o sorteio quase nunca troca. **Mudar o `tau_c` é calibração**, e a regra "calibração no fim" vale (INT-6).
- **O comportamento e o alvo:**
  - hoje, N comidas à vista dão N unidades de `comer`;
  - o ε do `g_exp` soma em cada unidade (`arb.py:84-86`);
  - então duplicar um objeto equivalente aumenta a chance de comer.
- **O conserto mais barato é o item 1 da PV2-10, o sorteio em dois estágios com um `u` só:**
  - `w_b = max_o a[b,o] + mul(g_exp, ε)`, e o comportamento sai pelo `u`, como hoje;
  - o resto do mesmo `u` escolhe o alvo dentro do comportamento: `u' = (u·T − acumulado_antes) / w_b`, proporcional aos `a[b,o]`;
  - é uma chamada de rng só, determinística, e a contagem de chamadas não muda.
  - **Não é o braço G da VALUATION:** ele trocou o sorteio pelo maior peso e piorou −0,290 (#949, relato). O dois estágios mantém o sorteio.

### 3.6 F. A memória e a explicação do comportamento

- **A recuperação considera a necessidade só pela pista,** a fome acima de S/4. O valor da lembrança não se reavalia: o σ fica como foi
  gravado.
- **O que os episódios mudam:**
  - o termo M do `explorar/ponto`;
  - a lembrança L nas unidades que casam pela ação e pela classe.
- **O que as sondas mostram de fato:** a sonda zera um termo com o mesmo `u` e diz se a escolha daquela decisão mudaria (`arb.py:36-68`).
  É uma afirmação sobre **uma decisão**, e não sobre a vida: sem o termo, a vida seguinte seria outra.
  - O cenário do lugar lembrado mostra que a memória decide numa situação montada (5 sementes).
  - A 0b mostra a sensibilidade da escolha ao corpo (a SE-C) e nunca mediu uma vida contrafactual.
- **A proposta de reavaliação (o "R4", parte D4):** o valor do lugar passa a ser `valor_previsto(pc_agora, d̂[classe do episódio])`
  vezes a confiança no lugar, que é a soma dos σ cortada em [0, S]. O lugar diz **onde**, e o P1 diz **quanto vale agora**. É a conta do
  Zhang et al. 2009 levada à memória, atrás de subchave.
- **O rastro diagnóstico (o "R1", seção 5): um registro por decisão, só leitura, nos dois lados,** com:
  - `cadeia_id`, o tick da decisão e a unidade escolhida, com os termos (já existem no registro);
  - o r do mesmo tick, por canal;
  - **o r do intervalo**, por canal: o que hoje fica fora;
  - quais atualizações a decisão causou: o P1 (classe, receptor, antes, depois), o P2 (a linha, o Δ) e os episódios codificados, com
    os ids;
  - quais episódios, quais linhas de H e quais d̂ pesaram nesta escolha, pelos termos e pelas sondas;
  - **a ponte ao jogador:** o texto do balão e do painel cita o `cadeia_id` de onde veio. Hoje **o balão e a vontade vêm do cérebro A
    parado** (`motor.ts:1210-1214`). Isso tem de ir para a LZ3 da LIMPEZA (INT-7): enquanto o jogo explicar o pet pela vontade de outro
    cérebro, nenhuma melhoria da cadeia aparece para o jogador.

## 4. As decisões anteriores que merecem revisão

**As três camadas:** **código** (entregue), **cenário** (validado numa situação montada) e **produto** (generalizado para a vida do jogo).
Nada do que já foi medido se apaga: a proposta é sempre por adendo, com a pergunta nova.

| decisão anterior | evidência original | camada | limitação atual | pergunta nova | recomendação |
|---|---|---|---|---|---|
| **PE-3, o crédito por opção** (especificação, seção 2.4) | o traço piorou o A (`RESULTADO_V2_REVISAO_APRENDIZ`); a C2 (#517) deu ≈ 0 | código e cenário | o r é do mesmo tick, então a opção não vê o que vem depois; o traço testado foi o do A, sobre outro sinal | o r do intervalo, creditado por um traço curto, ensina o que hoje fica de fora (o sono, a digestão lenta) sem tirar o pet da comida? | **reabrir por adendo**, como o R2, com a T4 e a guarda de forrageio. A PE-3 continua para o r imediato |
| **PV2-10, a ordem das etapas** (o sorteio, o corpo modula, os órgãos, as opções e o crédito) | a HA da 0b indeterminada; o ρ do `explorar` > 1,25 em quatro grupos | papel | não sabia que o r é do mesmo tick nem que o carinho não chega ao cérebro; o ELOGIO já constrói uma janela de crédito agora | o crédito pode vir antes, aproveitando a estrutura do ELOGIO? | **reordenar em parte** (INT-1): o PV-2, depois o rastro (R1), depois o crédito do intervalo (R2) com o ELOGIO, e só então o sorteio |
| **D-PV0R-6, os cortes da HC inatingíveis** | só 2 a 4 receptores têm a A_r não vazia | cenário | a coerência só mede receptores que mudam no mesmo tick | com o r do intervalo, a energia e o tédio passariam a ter A_r? | registrar a pergunta; a medida só depois do R2, por adendo ao plano da 0b |
| **`tau_c` = 15** (calibração do conserto, #427) | a rodada 3 da calibração | código | o C virou degrau: a persistência vai ao teto na primeira decisão, e a recorrência do protótipo some | um C que integra de fato muda a interrupção e a troca de alvo? | **não mexer agora** ("calibração no fim"); registrar como limitação da R3 (INT-6) |
| **o REL como cérebro da pesquisa** (C4) | as runs da C4 e da 0b | cenário | o jogo é o v38, com o olhar, o sono que segura, o lance do dono e o E1; nenhum gabarito junta tudo | o efeito medido no REL vale no v38? | em cada run da cadeia, uma checagem descritiva com a config do v38, sem gate (INT-8) |
| **PV2-5, G0 = 64** | a forma da revisão I | papel | a escala da fome não foi escrita; com S = 1024, o ganho vai a 17 | o ganho satura o cheiro? | manter o decidido e medir a saturação nas sementes dos testes; se passar de um corte, um adendo antes da run (INT-4) |
| **a auditoria do sucesso: "o dono não ensina o modular"** | a leitura do código, #964 | código | é verdade e continua: o carinho nem chega ao `receber_acao_dono` | — | **não reabrir.** O ELOGIO muda isso pelo corpo, e a regra de 2026-11-04 vale |
| **a VALUATION encerrada sem conserto** (D-VAL-23) | #949 e #969, relatos | cenário | o reflexo do sono decide e piora a fome; o conserto reprovou pela exaustão | uma interrupção pela energia dentro da intenção (o R3), em vez de um reflexo fora dela, muda o dilema? | não reabrir a VALUATION; a pergunta vai para o plano do R3 |
| **"cérebro neural" como nome** (PE-13) | a especificação, seção 2.6 | papel | — | — | nenhuma mudança. O texto ao jogador segue a seção 1.4 |

**O que já é de outras frentes:**
- **a quimiotaxia e o ganho pela fome:** PET_VIVO, PV-2 (plano #741);
- **o crédito do carinho:** ELOGIO (#953, #968);
- **as guardas de urgência no M-ARB:** F3 (#958);
- **a vontade do A no jogo:** LIMPEZA, LZ3;
- **o sono contra a fome:** a VALUATION, encerrada, e o SONO_SEGURA;
- **a normalização do sorteio, o corpo modula, os órgãos de dentro, as opções e o crédito:** a seção 9 do plano do PV-2, sem tarefa.

## 5. Os testes que podem refutar as propostas

**As regras:**
- todos os cenários são determinísticos, nas sementes dos testes ou numa faixa pedida ao coordenador quando viram run;
- o **controle** é sempre a mesma vida (mesmo genoma, mundo, dono e semente) com a subchave do mecanismo desligada, ou o coeficiente
  zerado;
- "**decisão**" quer dizer a probabilidade numa decisão de estado fixo (a sonda ou o contrafactual da 0b); "**vida**" quer dizer a
  medida sobre a vida inteira.

**A validade da SE-C e da RV:**
- a SE-C mede quanto a escolha de uma decisão muda com o corpo mudado e se muda para o lado do alívio. **Serve à T1 e à T2.** Não
  mede aprendizado nem crédito;
- a RV mede a mesma coisa só para o `comer` e a fome. **Serve à T2,** e não à T3: a T3 pede a curva no tempo depois da mudança.

| # | cenário | o esperado | o mecanismo avaliado | o controle | o que enfraquece a hipótese | medidas |
|---|---|---|---|---|---|---|
| **T1** | **mesmo ambiente, fome diferente:** a ração fora da vista, a 15 células, com o cheiro chegando; fome de S/4, S/2 e 3S/4 | com mais fome, mais buscas `comer/cheiro` e menos decisões até comer; no OLF-G, a dependência é mais forte | B1 e o PV-2 | o OLF-DCV sem o ganho; o OLF-0 para a busca | a SE-C do OLF-G não passa a do OLF-DCV por mais que δ_E; ou o G-FORR reprova | a SE-C, a RV, as decisões até comer, "achou" (o plano do PV-2, seção 5) |
| **T2** | **mesmo corpo, históricos diferentes:** dois pets com o mesmo corpo na decisão de teste; um comeu a fruta a com alívio por 3 dias, o outro a fruta b | na decisão de teste, com a e b à vista, cada um prefere a da sua história; com a fome zerada no contrafactual, a preferência encolhe (revaloriza) | o P1 e a lembrança L | as mesmas vidas com o `p1` desligado | a preferência não muda com a história; ou não encolhe com a fome zerada | a probabilidade de cada unidade na decisão de teste; a RV por classe |
| **T3** | **o efeito de um alimento muda:** a ração passa a dar dor (um emissor de teste atrás de chave) no dia 4 | o d̂ da ração cai em poucos consumos; a escolha da ração cai; com o D3, o incentivo fica negativo e o pet a evita mesmo com fome moderada | o P1, o D3 e a L | o mesmo mundo sem a mudança; o D3 desligado | o d̂ muda e a escolha não (o corte em 0); ou leva mais de uma janela PROPOSTA de 10 consumos | a curva da P(comer ração | estado fixo) por dia; o d̂ registrado |
| **T4** | **efeito atrasado com uma ação irrelevante no meio:** a fruta c dá humor +X 30 ticks depois de comida (digestão lenta, ou um emissor de teste); entre as duas, o pet às vezes brinca | com o R2, o H do `comer` no contexto da fome cresce mais que o do `brincar`; sem o R2, nenhum dos dois | o R2 (o traço e a linha de base) | o R2 desligado; e um mundo em que o efeito vem sem relação com a fruta (o tempo sorteado pelo `u` do motor, o mesmo placebo do PV-2) | o H do `brincar` cresce tanto quanto o do `comer`; ou o placebo dá o mesmo H | as linhas de H registradas; o crédito por item do traço |
| **T5** | **efeito adverso independente da comida:** a dor por um tapa do dono, num horário que não depende do que o pet comeu | o d̂ das comidas não muda; o H do `comer` não cai | o D1 e a linha de base do R2 | o mundo sem o tapa | o d̂ ou o H do comer cai: o pet atribui ao alimento o que veio do dono | o d̂ e o H, antes e depois |
| **T6** | **dor durante uma intenção:** um tapa no meio da ida à comida | com o R3, a intenção acaba em "interrompeu" na decisão seguinte; sem o R3, ela continua (C no teto) | o R3 e o B3 | θ_dor = S + 1 | não interrompe; ou interrompe e frustra; ou volta sempre à mesma intenção logo depois (oscila) | o fim da intenção registrado; as decisões até voltar à comida |
| **T7** | **objetos equivalentes duplicados:** 1, 2 e 4 rações iguais à mesma distância | sem o R5, a P(comer) cresce com N (a leitura do código); com o R5, fica igual | o R5 (os dois estágios) | o sorteio de hoje | com o R5, a P(comer) ainda muda com N | a P(comportamento) por N; a A-2 da 0b |
| **T8** | **os recursos mudam de lugar:** o comedouro muda de região no dia 5 | as visitas ao lugar velho caem; com o D4, um lugar onde comeu com fome vale menos quando o pet está saciado | o M-MEM, o D2 e o D4 | o D4 desligado; o lugar sem mudança | o pet volta ao lugar velho tanto quanto antes; ou o valor não muda com a fome | as visitas por lugar e por dia; a sonda `sem_memoria` |

**Para cada mecanismo, quatro medidas juntas, e nenhuma sozinha:**
- **a coerência corporal:** a SE-C;
- **a manutenção:** a taxa por episódio de fome (o G-MVP-EP) e a exaustão (o G2 da VALUATION);
- **a recuperação depois de uma perturbação:** as decisões até voltar ao forrageio depois da T3, da T6 e da T8;
- **a atribuição certa:** a T4 e a T5.

Ao lado delas vão **o custo** (o tempo por vida, medido) e **a experiência observável:** o rastro do R1 tem de mostrar a cadeia em
texto, e o teste lê esse texto. A legibilidade com pessoas é da frente LEGIBILIDADE.

## 6. A sequência recomendada, conciliada com as tarefas

| ordem | etapa | o que entra | frente que já cobre | depende de | run? |
|---|---|---|---|---|---|
| **R0** | **o código do PV-2** (seção 8) | o órgão no M-SENS, o dC, a pirueta, a varredura, o placebo, o OLF-G | **PET_VIVO, PV-2** (#741, APROVADO) | nada; o código toca `sens.py`, `adapt.py` e `config.py`, então precisa conversar com a F3 e o ELOGIO no merge | não no PR do código; a run do PV-2 depois, com faixa |
| **R1** | **o rastro da cadeia** (só leitura, Python e TS) | o `cadeia_id`, o r do intervalo medido e não creditado, as atualizações e as sondas por decisão; a medida "quanto do corpo fica fora do r" nas vidas da 0b, por replay | a seção 9 do plano do PV-2 (o "teste do sinal certo") e a CADEIA, etapa 3 (o painel) | R0 (para incluir o cheiro) | só replay, sem vida nova |
| **R2** | **o r do intervalo e o traço** (seção 3.3) | o traço K = 4, a linha de base por contexto, o crédito no P2 | **PV-3 (o crédito, seção 9.5 do plano do PV-2)**, juntado ao **ELOGIO** (a janela W) | R1 (os números do intervalo); o #968 na `main` | sim, plano novo |
| **R3** | **a interrupção e a opção de buscar comida** | o "interrompeu", o B3, as condições da seção 3.5 | **PV-1 e PV-5** (seção 9.4 do plano do PV-2); as guardas de fome são da **F3** | R2; a F3 | sim |
| **R4** | **os desfechos com contexto e a memória reavaliada** | D1 a D4 | seção 9.3 do plano do PV-2 (em parte); nenhuma tarefa para a memória | R2 | sim |
| **R5** | **o sorteio em dois estágios** | seção 3.5 | **PV2-10, item 1** | nada no código; vem aqui para não misturar com a SE-C das etapas anteriores (INT-1) | sim |
| **R6** | **a saciedade e os órgãos de dentro** | o receptor da saciedade, o freio do B2, o paladar no M-SENS | seção 9.3 do plano do PV-2; o ELOGIO precisa do paladar (D-EL-9) | uma tarefa de corpo | sim |
| **Web** | cada etapa, depois da validação dela | o espelho com paridade | a regra "sempre aplicar na web"; **a LZ3 tira a vontade do A do balão** (INT-7) | a validação da etapa; a LZ3 | — |

**A ordem acima é a decidida (INT-1, 2026-11-17).** A alternativa, manter a PV2-10 como estava (o R5 logo depois do R0), ficou de fora.

## 7. O plano de código por mudança (as etapas R1 a R6, em resumo; o R0 está na seção 8)

**As regras de cada etapa:**
- uma subchave nova na `ConfigDigibrain`, desligada;
- o gabarito de hoje num commit próprio;
- o byte a byte desligado;
- o G1 do replay ligado;
- nenhuma rng nova;
- inteiros;
- os parâmetros no `config.py` com o status;
- as medidas no `metrics.py`;
- o plano de análise antes da run;
- a web só depois.

**O registro:** nenhum evento novo no log em nenhuma etapa. Tudo é estado do cérebro, refeito pelo replay. Os saves e os logs de hoje
continuam válidos, e a `VERSAO_PET` só muda quando o jogo ligar a etapa.

| etapa | problema (evidência) | arquivos e funções | campos e interfaces | equação | custo e como medir | aceitação |
|---|---|---|---|---|---|---|
| **R1** | o intervalo e a origem da explicação são invisíveis (seções 1.3 e 3.6) | `adapt.py` (`_fechar`, o registro); `afeto.py` (uma função `r_intervalo`, só cálculo); `metrics.py` (a fração do corpo fora do r); `web/app/motor/digibrain/leitura.ts` e `adapt.ts` | `registro["cadeia"] = {id, r_mesmo_tick, r_intervalo, atualizacoes, pesou}`; a subchave `rastro` | `r_int` da seção 3.3, sem crédito | O(11) por decisão; o tempo por vida nas sementes dos testes, ligado contra desligado | o byte a byte desligado; ligado, a escolha é idêntica decisão a decisão (a sonda não muda nada); a paridade do registro em TS |
| **R2** | o r do dormir é 0, e o que vem no intervalo não ensina (seção 1.3) | `estado.py` (o traço), `plast.py` (`creditar_traco`), `adapt.py` (`_fechar`), `afeto.py` (a linha de base) | `ConfigDigibrain.traco_intervalo`; os inatos `k_traco`, `lambda_traco`, `eta_int`, `k_base` (PROPOSTOS) | a seção 3.3 | O(K·23) produtos por decisão; o tempo medido | a T4 e a T5; a guarda de forrageio; um teste de que cada intervalo é contado uma vez |
| **R3** | a intenção não se interrompe pela dor (seção 3.5) | `estado.py` (`_consequencia`, o fim "interrompeu") | `ConfigDigibrain.interrupcao`; os inatos `theta_dor`, `theta_susto` | `dor₁ − dor_ini ≥ θ_dor` | O(1) | a T6; nenhum fim novo com a chave desligada |
| **R4** | o P1 sem contexto e sem aversão; a memória sem revalorização (seções 3.4 e 3.6) | `plast.py` (`desfecho_ctx`, `incentivo`), `mem.py` (`recuperar`), `adapt.py` | as subchaves `p1_posterior`, `p1_contexto`, `incentivo_sinal`, `mem_revaloriza` | as seções 3.4 e 3.6 | O(classes × regiões × 11) de memória; medir | a T2, a T3, a T5 e a T8 |
| **R5** | o número de alvos infla o comportamento (seção 3.5) | `arb.py` (`escolher`, `sortear_inteiro`) | a subchave `sorteio_dois_estagios` | a seção 3.5, um `u` só | O(n) | a T7; a contagem de chamadas da rng igual |
| **R6** | não há saciedade (seção 1.5) | `corpo.py` (um receptor novo), `sens.py` | uma `ConfigSaciedade` nova, desligada | o B2 | — | tarefa própria; a T1 com o freio |

## 8. A especificação da primeira etapa: o código do PV-2 (R0)

**Por que esta primeiro:**
- é a etapa aprovada que falta (#741, as PV2-1 a PV2-10 DECIDIDAS) e não tem código;
- é a ligação órgão → cérebro mais direta do pedido;
- tem os controles prontos para separar o sensor, a frequência e o momento das viradas;
- não depende da LIMPEZA nem do ELOGIO.

O que segue é o detalhe que o plano deixou "para o PR do código", com as conferências que esta leitura achou.

### 8.1 O problema e a evidência

- O cérebro recebe a direção da comida como oráculo (`sens.py:365`, `mundo.py:1849-1851`).
- O órgão que sentiria o cheiro existe (`ConfigOlfato`), mas está desligado, e ligá-lo faz o modular falhar alto (`sens.py:192-194`).

### 8.2 Os commits, na ordem

1. **O gabarito de hoje:** as vidas do REL nos três lugares, nas sementes dos testes, gravadas antes de qualquer mudança. O gabarito
   `digibrain_modular_*` que já existe pode bastar, se cobrir os três lugares; senão, um `pv2_de_hoje.json` novo.
2. **A config:** uma `ConfigPV2` dentro da `ConfigDigibrain` (`ligada=False`) em `config.py`:
   - `braco` ∈ {"OLF-0", "OLF-DC", "OLF-DCV", "OLF-PLA", "OLF-G"};
   - `w0_dc`: o peso inato do dC na unidade do cheiro, PROPOSTO;
   - `l_pirueta`, `n_varredura` e `taxa_placebo`: PROPOSTOS, medidos nas sementes dos testes e propostos por adendo (PV2-9);
   - `g0 = 64`: DECIDIDO (PV2-5).

   A `ConfigOlfato(ligada=True, comida=True, narinas=2)` vem da config que já existe. **O `__post_init__` falha alto** se a `ConfigPV2`
   estiver ligada com o olfato desligado, ou o contrário, com o modular.
3. **O M-SENS** (`sens.py`):
   - as constantes `RECEPTORES_OLFATO = ("olfato_comida_esq", "olfato_comida_dir")`;
   - no `_receptores`, com a `ConfigPV2` ligada, elas saem dos `presentes` como a tela sai (`sens.py:185-191`). Fora isso, falha alto
     como hoje;
   - **elas nunca entram na falta, nas urgências nem no r;**
   - no `codificar`:
     ```
     c   = div_arred(esq + dir, 2)                 # o nivel: a media das narinas (PV2-3; nunca esq - dir)
     dC  = 0 se c_ant is None, senao clamp(c - c_ant, -S, S)
     c_ant <- c                                    # estado do M-SENS, refeito pelo replay
     ha_cheiro = c > 0                             # a leitura ja passou pelo limiar do orgao
     ```
     O `out` ganha `cheiro = {"c": c, "dC": dC}`. Com a chave desligada, nenhum campo novo.
4. **O z** (`impulso.py`): com a chave ligada, a característica `dC` entra no fim do z (o `CARACTERISTICAS_DIGIBRAIN` ganha uma
   característica só com a chave), com o `w0_dc` só na unidade `comer/cheiro` (PV2-4).
   - O `prox` da unidade do cheiro vira o `c`. No OLF-G, vira `c_g = clamp(div_arred(c · (g0 + u_fome), g0), 0, S)`.
   - **O P2 ganha uma coluna:** o `H` passa a 7 × 24 com a chave. O teste confere que o desligado continua 7 × 23.
5. **O executor** (`adapt.py`, `escolher_alvo`): a unidade `comer/cheiro` (e a `explorar/cheiro`) casa com os candidatos
   `cheiro_seguir` e `cheiro_virar` que o motor oferece (`mundo.py:488-517`).
   - **A regra por braço:**

     | braço | a regra |
     |---|---|
     | OLF-0 | o primeiro candidato, que é o preferido do motor (a tropotaxia) |
     | OLF-DC | `A ← max(0, A − dC)` se dC < 0, senão `A ← 0`; se `A ≥ l_pirueta`, então `cheiro_virar` e `A ← 0`; senão `cheiro_seguir` |
     | OLF-DCV | como o OLF-DC; na pirueta, a varredura fica `n_varredura` decisões no `cheiro_virar` do motor (o lado da narina mais forte) antes de voltar a seguir |
     | OLF-PLA | vira quando `(u & 0xFF) < taxa_placebo`, com a mesma varredura e sem ler o A |
     | OLF-G | o OLF-DCV, com o `c_g` no lugar do `c` |

   - **O estado:** o acumulador A e a fase da varredura ficam no estado do M-ADAPT. A DX-4 continua: "achou" com comida à vista,
     "sumiu" com `c = 0`, "desistiu" com 6 decisões.
6. **As medidas** (`metrics.py`): o "achou" pelo cheiro, as decisões até comer, a hora da virada (a fração das viradas com dC < 0), as
   unidades por decisão (o G-UNIDADES) e a taxa de saturação do `c_g` (a fração das decisões com `c_g = S`, para a INT-4).
7. **A medida do custo:** 2 vidas por braço nas sementes dos testes, com a projeção da run com 4 processos. Se passar de umas 8 h, um K
   menor por adendo (o plano do PV-2, seção 4).
8. **O adendo** ao `PLANO_ANALISE_V3_PET_VIVO_PV2.md` com o `l_pirueta`, o `n_varredura`, a `taxa_placebo` e o `w0_dc` medidos, antes da
   run. A faixa vai ao coordenador.

### 8.3 As conferências que falham alto (testes novos em `tests/test_pv2_codigo.py`)

- desligado, as vidas do gabarito saem byte a byte;
- ligado, o G1 do replay em cada braço;
- **o G-UNIDADES:** decisão a decisão, o número de unidades dos braços com o órgão é igual ao do OLF-0;
- o placebo não muda a contagem de chamadas da rng `alvo` nem da de política;
- **o cérebro nunca lê `esq − dir`:** o teste troca as narinas entre si (esquerda ↔ direita) e confere que o `sens` sai igual;
- o M-SENS falha alto com o órgão ligado sem a `ConfigPV2` (a falha alta de hoje continua);
- um teste de cenário: a ração atrás de um obstáculo, fora da vista, e o pet do OLF-DCV a acha em N decisões nas 5 sementes. N fica só
  registrado, sem corte.

### 8.4 O escopo, a compatibilidade, o Python e o TypeScript

- **Não mudam:** o `engine.py`, o `MotorMundo`, o corpo, a web, o log e o save.
- **Os registros existentes continuam válidos:** a chave desligada não grava nada novo.
- **O TypeScript não entra neste PR:** o `ConfigOlfato` não existe no TS. A web vem por tarefa própria depois da validação, e essa
  tarefa porta o órgão (o `corpo.ts` e o `mundo.ts`), o M-SENS e o executor, com gabaritos novos.
- **A validação pela entrada normal do jogo** só é possível depois do porte: o dono põe a ração longe pela tela, e o log é o de sempre.
  No Python, a mesma coisa sai da bancada com o gesto "pôr ração".

### 8.5 Os critérios de aceitação do PR do código

- os testes da seção 8.3;
- o `python -m pytest tests/ -q` com a contagem no corpo do PR;
- o `python tools/conferir_saude.py`;
- o custo medido;
- o adendo escrito e PROPOSTO;
- nenhuma vida da run.

## 9. As limitações, as dependências e as decisões ainda necessárias

**As limitações desta análise:**
- **nada foi rodado,** e toda leitura do comportamento é do código;
- **as referências filosóficas** (Braitenberg, Clark, Thompson) foram conferidas pelo registro e pelos textos do editor, não pelo livro;
- **os números da VALUATION e do ELOGIO** vêm de PRs abertos;
- **o porte TS** foi lido por um subagente e não reconferido linha a linha, salvo o `motor.ts:1210-1214`.

**As dependências:**
- a merge do #968 (o ELOGIO) antes do R2;
- a LZ3 antes de qualquer etapa na web;
- a F3 antes do R3;
- a máquina livre e uma faixa para cada run.

**As decisões com o Matheus (DECIDIDAS pela recomendação em 2026-11-17, "Aprovo as INT-1 a INT-9 pela recomendação"; D-INT-9):**

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| **INT-1** | a ordem das etapas (seção 6) | **R0 (o PV-2), R1 (o rastro), R2 (o crédito do intervalo com o ELOGIO), R3, R4, R5 (o sorteio), R6.** Muda a PV2-10 só na posição do crédito e do sorteio, pela evidência nova da seção 1.3 | com o sorteio antes, a SE-C do R2 sai sem a confusão do número de alvos, mas o pet continua sem aprender do sono e da digestão por mais duas etapas. Com o crédito antes, a T4 mistura um pouco o número de alvos; o plano do R2 mede a A-2 ao lado |
| **INT-2** | o placebo no `u & 0xFF` | **conferir no PR do código** todos os consumidores do `u` da rng `alvo`, e não só o `alvos_do_olfato` | se outro consumidor usar os bits baixos, o placebo se correlaciona com o alvo e o G-PV2-HORA perde o controle |
| **INT-3** | o caminho do receptor do olfato no M-SENS | **o mesmo padrão da tela:** fora dos drives, do r e das urgências | se o cheiro entrasse no r, comer perto da comida daria r pelo cheiro, e o pet aprenderia a ficar perto do cheiro em vez de comer |
| **INT-4** | o ganho do OLF-G (até 17 vezes) | **manter o G0 = 64 decidido e medir a saturação** nas sementes dos testes. Se o `c_g` ficar em S em mais de metade das decisões com cheiro (corte PROPOSTO, SEM FONTE), um adendo propõe outro G0 antes da run | saturado, o OLF-G vira "a fome liga o cheiro no máximo": o G-ESTADO poderia passar por um efeito de degrau, e não de ganho |
| **INT-5** | o crédito do intervalo e a janela do ELOGIO | **uma estrutura de traço só** no cérebro, usada pelo ELOGIO (W decisões) e pelo R2 (K decisões), com sinais separados no registro | dois mecanismos de crédito no mesmo P2 somam o mesmo intervalo duas vezes (o carinho está dentro do r do intervalo), e o efeito do elogio fica impossível de separar |
| **INT-6** | o `tau_c` = 15 (o C como degrau) | **não mudar agora** ("calibração no fim"); registrar como limitação da R3 e medir a frequência de troca de intenção no R1 | mudar agora mexe em todas as runs em curso; não registrar esconde por que a interrupção quase não aparece |
| **INT-7** | a vontade do A no balão e na fala livre do jogo | **levar à LIMPEZA, LZ3:** a vontade e o balão passam a ler o motivo do modular (`leitura.ts`) | se a LZ3 só apagar o A, o balão fica sem vontade; se mantiver, o jogador continua lendo a vontade de um cérebro que não decide |
| **INT-8** | o REL e o v38 | **uma checagem descritiva com a config do v38** em cada run da cadeia, sem gate | o efeito pode não aparecer no pet do jogo, por causa do sono que segura e do E1, e ninguém saber |
| **INT-9** | onde fica esta análise | **`docs/futuro/`** (desenho de código sem tarefa), com as referências novas em `docs/referencias/` (D-INT-1) | no vault, o desenho ficaria longe do código que ele cita; numa `TAREFA_V3_*` nova, abriria uma frente sem o pedido do Matheus |

## 10. A situação jogável que a primeira etapa torna possível, e como provar

**A situação:** o jogador põe a ração atrás da barraca, fora da vista do pet, a umas 15 células.
- O pet com fome não vai em linha reta como hoje.
- Ele sai na direção em que veio. Quando o cheiro cai, para e vira; experimenta o lado mais forte e segue.
- Perto da comida, o cheiro para de subir, porque as narinas se adaptam. A ração entra na vista, e ele vai até ela.
- Com o OLF-G, o pet com pouca fome passa pelo cheiro sem buscar, e o pet faminto busca de longe.
- O jogador vê o zigue-zague, e (com o R1) o painel diz "o cheiro caiu duas vezes; virei para o lado mais forte".

**Isso só fica visível depois do porte para a web,** por tarefa própria. No Python, a mesma cena é o teste de cenário da seção 8.3.

**Como provar que a melhoria vem do mecanismo, e não de outra coisa:**

| a explicação rival | o braço que a separa | o que precisa sair |
|---|---|---|
| o pet acha porque o mundo dá a direção | o OLF-0 e os braços com o órgão não têm a direção (o `direcao_cheiro` vai a 0 com o órgão; uma conferência falha alto) | o "achou" sem o oráculo |
| acha só por virar mais vezes | o OLF-PLA, com a mesma taxa de viradas em hora sorteada | o G-PV2-HORA passa: o OLF-DCV ganha do OLF-PLA no `longe` e no `longe_fixo` |
| acha só pela tropotaxia das duas narinas | o OLF-0 | o G-PV2-LONGE passa |
| o cérebro aprendeu a direção por outra porta | o teste que troca as narinas confere que o cérebro não lê a diferença | o `sens` igual com as narinas trocadas |
| o ganho pela fome é só um degrau | a taxa de saturação do `c_g` (INT-4) | a saturação abaixo do corte, e o G-ESTADO passa |
| piorou perto de casa | o G-FORR no `comedouro` | não reprova |

Pela regra de leitura do plano do PV-2 (seção 7), só a primeira linha da tabela de lá (os três gates passando) leva a quimiotaxia ao
cérebro padrão e à web.
