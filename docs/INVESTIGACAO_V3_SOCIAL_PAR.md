# INVESTIGAÇÃO V3 — SOCIAL_PAR: como o contato entre dois pets pode virar uma relação (2026-11-17, PROPOSTO)

**Status: PROPOSTO.** A SP-1 e a SP-2 estão DECIDIDAS pelo Matheus em 2026-11-17 ("Aprovo a E1", D-SP-8); as SP-3 a SP-8
(seção 9) seguem abertas. A tarefa é
`docs/TAREFA_V3_SOCIAL_PAR.md`; a primeira etapa está especificada em `docs/ESPEC_V3_SOCIAL_PAR_E1.md`.

**O commit analisado:** `358895585858a06a6a8de4b7cab3e3890497dd11` (a `main` de 2026-11-17). Toda referência `arquivo:linha` vale nele.

**O que foi feito, separado por tipo:**

| tipo | o quê |
|---|---|
| **lido** | os nove documentos pedidos (seção 1.1), o `docs/PLANO_V3_PARCEIRO.md` e o `docs/GDD_V3_PARCEIRO.md` |
| **verificado no código** | o Python (`digilab/grupo.py`, `mundo.py`, `cooperacao.py`, `digibrain/`, `corpo.py`, a bancada) e o TS (`web/app/motor/grupo*.ts`, `mundo.ts`, `cooperacao.ts`, `digibrain/`, `constantes.ts`, as telas). Dois subagentes de leitura (Opus 5.5) fizeram o levantamento linha a linha, e as linhas centrais foram conferidas à mão (seção 1.2) |
| **executado** | `python -m pytest -q -p no:cacheprovider tests/test_grupo.py tests/test_grupo_social.py tests/test_cooperacao.py tests/test_cooperacao_co6.py tests/test_cooperacao_co7.py tests/test_sentidos_mundo.py` → **161 passed** (85,6 s). Os testes do TS não foram rodados (a worktree não tem `node_modules`) |
| **medido** | nada novo. Os números de comportamento vêm dos artefatos já versionados da bancada da cooperação (seção 1.4), relidos e com o sha256 conferido |
| **verificado na literatura** | as 10 fontes da seção 2, com o Crossref para os 5 DOIs e as páginas oficiais para os 5 sem DOI; 7 com texto completo lido, 3 só pelo resumo (`docs/referencias/v3_social_par_referencias_verificadas.csv`) |
| **proposto** | os experimentos A a F (seção 3), os mecanismos (seção 5), a ordem (seção 6), a etapa E1 e as decisões SP-1 a SP-8 |

## 0. A resposta curta

1. **Hoje o outro pet entra na decisão do pet do jogo por dois caminhos, e nenhum é aprendido.**
   - **O mundo comum:** a comida que o outro comeu some, e a bola que ele chutou rola.
   - **As regras fixas da CO7**, ligadas no grupo v39: o escudo, o peso da universalização, a culpa e a inveja. Elas leem a ação visível
     ("aflito" = `emburrar` ou `chamar_atencao`) e a aproximação de uma comida.
2. **O DigiBrain modular não tem nenhuma ação dirigida ao outro.** As unidades são comida, cheiro, bola, vagar, ponto, fala e olhar
   (`web/app/motor/digibrain/impulso.ts:124-151`; `digilab/digibrain/impulso.py:118-148`). O motor oferece os candidatos `seguir` e
   `onde_comeu` no explorar (`mundo.ts:1275-1294`), mas o modular só pega o candidato do tipo da unidade escolhida (`adapt.ts:384-401`). Por
   isso o modular nunca segue o irmão, e o ato "encostar" da CO3 (que exige ter seguido, `grupo.ts:110-116`) não acontece no jogo de hoje.
3. **O corpo não sente o outro.** A solidão sobe sozinha e só o carinho do dono a baixa (`digilab/corpo.py:32`, `:538`, `:577`). Como o
   aprendizado do modular é movido pela variação do corpo (`docs/AUDITORIA_V3_SUCESSO_CORPO.md`), **não há o que aprender sobre o
   parceiro**: estar perto dele não muda nada no corpo.
4. **Os resultados da bancada confirmam o diagnóstico.** Mesmo quando a situação que a CO7 lê acontece muitas vezes, os deveres quase não
   mudam o que o pet faz: +0,0008 [−0,0014; +0,0039], n = 69 (seção 1.4).
5. **A recomendação:** começar pelo **instrumento**, não pelo mecanismo. A primeira etapa (E1) põe na bancada do Python um parceiro sob
   intervenção (ao vivo, gravado ou de outra vida) e as medidas de contato e de contingência, e valida as medidas em dois pares de regra
   fixa cuja resposta se conhece. Só depois disso faz sentido medir o pet de hoje (o A0) e decidir o primeiro mecanismo social.
   - O teste **ao vivo × gravação é viável** no Python, com uma gravação executada fisicamente pelo próprio motor (seção 3.1).
   - Ele **não é viável no jogo** sem quebrar o replay (`grupo_jogo.ts:166`).
   - Ele **não mede nada no pet de hoje além do mundo comum**, porque o pet não tem por onde responder ao outro. Por isso a E1 traz os dois
     controles de regra fixa: sem eles, um "nenhuma diferença" no pet de hoje não se distingue de um instrumento que não mede.

## 1. O estado atual

### 1.1 Os documentos, reconciliados com o que foi entregue

| documento | o que propunha | o que existe hoje |
|---|---|---|
| `docs/futuro/cognicao_social.md` (2026-10-04, IDEIA) | a escada de 10 degraus, da informação factual à convenção simbólica; o modelo dos outros (familiaridade, confiança, afinidade); o primeiro passo com um pet sintético informante | só ideia. O primeiro passo foi trocado por dois pets de verdade (`dois_pets.md`, 2026-10-07) |
| `docs/futuro/convivencia_mundo_fisico.md` (2026-10-07, IDEIA) | a escada no mapa; CV-1 a CV-6: disputa só por quem chega primeiro (CV-3), nenhum sinal no degrau 1 (CV-4), solidão e aglomeração no corpo só no degrau 3 (CV-5) | a CV-3 e a CV-4 valem no código; a CV-5 não foi feita: o corpo não sente o outro |
| `docs/futuro/dois_pets.md` (DP-1 a DP-14) | o motor de N pets, a ordem sorteada, o registro do grupo, os sentidos sem estado interno, os candidatos `seguir` e `onde_comeu` "que só o cérebro escolhe", o alvo aprendido no cérebro A, o modelo dos outros registrado, a medida "B aprende o que só A viveu" | **feito no Python:** o motor, a ordem, o registro, a visão, o toque, os candidatos sociais, o degrau 1b (som, cheiro, rastro) atrás da `ConfigSentidos` desligada, o alvo aprendido e o `ModeloOutros` só no cérebro A (atrás de chaves desligadas). **Não feito:** a medida da seção 11 (nenhuma run "B aprende o que só A viveu"). **No TS:** o grupo, sem o degrau 1b |
| `docs/TAREFA_V3_COOPERACAO.md` (CO0 a CO7) | o grupo no TS, os atos e a pontuação, os dois ovos, o que se vê, a reputação e o `k` na percepção (CO6), os deveres (CO7) | **tudo na `main`:** o ovo do brasão choca o grupo v39 com a CO6 e a CO7 ligadas (`constantes.ts:216-218`, `grupo_jogo.ts:59`). Os comentários de `grupo_jogo.ts:54-56` e `AtosDoIrmao.tsx:10` ainda dizem "desligada no jogo" e estão desatualizados |
| `docs/ESPEC_V3_COOPERACAO_CO6.md` | a reputação de cada presente e o peso dos deveres `k` na percepção, sem mudar a decisão | feito; o `k` é um por pet, não por parceiro (`cooperacao.py:161-189`) |
| `docs/ESPEC_V3_COOPERACAO_CO7.md` | o escudo duro, a universalização "que se reduz à tabela da CO3" (CO7-5), a culpa e a inveja no afeto | feito, com os ganchos de ablação só no Python (`config.py`, `fator_teto_k`, `co7_escudo`, `co7_universalizacao`, `co7_afeto`) |
| `docs/PLANO_ANALISE_V3_COOPERACAO.md` e o adendo 1 | a bancada: H-EMERGE, H-DOSE, H-REP, H-CUSTO; o adendo com o irmão aleatório | rodados (seção 1.4) |
| `docs/futuro/cooperacao_bancada_resultado.md` | o resultado | relido contra os artefatos (seção 1.4) |
| `docs/TAREFA_V3_PET_VIVO.md` | "o pet escolhe pelo que sente por dentro?" | toca esta investigação pelo mesmo incômodo: nenhum gate de hoje mede "age pelo estado", e nenhum mede "age pelo outro" |

**Uma decisão posterior que conversa com esta:** o parceiro da jornada (`docs/GDD_V3_PARCEIRO.md`, PAR-1 a PAR-3) é um modo ao lado do
habitat com o mesmo cérebro. A J1 prevê "um habitante especial com DigiBrain, preso a uma rotina" (`docs/PLANO_V3_PARCEIRO.md:51`). Esse
habitante seria um terceiro tipo de parceiro, nem irmão nem gravação, e não entra nesta investigação.

### 1.2 O código, conferido

As linhas centrais conferidas à mão estão marcadas com ✓; as demais vêm do levantamento dos subagentes.

- **O grupo do jogo** (TS):
  - `VERSAO_GRUPO = VERSAO_V39` ✓ (`constantes.ts:216`);
  - `nasceComDeveres` liga a CO6 e a CO7 na v37 e na v39 ✓ (`constantes.ts:218`);
  - o primeiro acesso, sem save, mostra um pet só v38 (`src/jogo.ts:59`).
- **A percepção social** (Python `mundo.py:555-574`; TS `mundo.ts:507-516`):
  - `outros`: (id, dx, dy, d, ação visível), a até 6 células, em distância euclidiana;
  - `onde_comeu`: só se o consumo foi visto;
  - `toque`: (id, tipo, direção, idade), a até 1 célula em Chebyshev;
  - com a CO6: `reputacao` e `peso_dever`.
  - Nenhum campo lê o estado interno do outro diretamente (`tests/test_grupo_social.py:95,127`).
  - **Uma exceção indireta:** o valor da disputa "anti" na reputação sai do ganho real da refeição de quem venceu ✓
    (`cooperacao.py:147-153`), e a reputação move o `k`, que liga o escudo. Com dois pets, o resto da conta usa só o corpo da própria
    testemunha.
- **Os candidatos sociais:**
  - existem, só no explorar e com o outro à vista ✓ (`mundo.ts:1275-1294`; `mundo.py:1896-1915`);
  - o padrão do motor e o instinto nunca os escolhem (`tests/test_grupo_social.py:336`);
  - o cérebro A os escolhe só com `alvo_aprendido` (desligado; `lobos.py:226-228`);
  - o modular nunca ✓ (as unidades em `impulso.ts:124-151`, a escolha em `adapt.ts:384-401`).
- **O toque `encostou`** exige ter seguido o outro ✓ (`grupo.ts:110-116`). Sem `seguir`, ele não sai no jogo.
- **O membro do grupo:** o Python só aceita um `MotorMundo` recém-nascido, ligado ao mundo do grupo ✓ (`grupo.py:242-252`). O TS aceita o
  `PetDoGrupo` (cérebro e engine de fora) e o `MotorNoGrupo` (`grupo.ts:193-235`). Nenhum dos dois tem um membro que rejoga decisões ou
  posições gravadas.
- **A interação física:**
  - os pets não colidem nem ocupam célula: só paredes e água são sólidas (`mundo.py:1627`);
  - a bola é uma só, rola na direção do golpe com `bolaNoGolpe` (`motor.ts:367`; `mundo.py:1340-1355`), e a distância é sorteada no fluxo
    `mundo-bola`;
  - não há passe, mira nem objeto carregado a dois;
  - o sacudir a árvore é do dono e falha alto no grupo (`mundo.py:203-204`).
- **A memória por parceiro:**
  - no modular, só `antes[id]`, a última posição em que viu cada outro, usada pela regra do escudo (`sens.py:307,373`);
  - o campo `outro` dos episódios do M-MEM é sempre `None` fora da luta (`mem.py:115,138`);
  - no cérebro A, o `ModeloOutros` por id, só registrado e desligado (`lobos.py:658-750`). O A está saindo do jogo (a LIMPEZA).
- **A comunicação:** nenhuma ação com destinatário outro pet. O `chamar_atencao` não tem alvo (`mundo.py:186`). Com a `ConfigSentidos`
  ligada (só no Python), ele emite o som "chamado", mas o modular não lê `ps.sentidos` e recusa os receptores dos órgãos
  (`digibrain/sens.py:192-194`).
- **O corpo:**
  - a solidão sobe +225 por tick acordado, e só o carinho a baixa ✓ (`corpo.py:32`, `:538`, `:577`);
  - nenhum emissor lê a presença do outro pet.

### 1.3 A matriz das capacidades

"Ativo no jogo" quer dizer: no grupo v39, que o ovo do brasão choca hoje.

| capacidade | implementado | ativo no jogo | regra fixa | aprendido | testes | resultado comportamental | aberto |
|---|---|---|---|---|---|---|---|
| **perceber o outro** | visão e toque (Python e TS); som, cheiro e rastro (só Python, desligados) | visão e toque | os sensores | — | `test_grupo_social.py:95-361`; `test_sentidos_mundo.py`; G-PAR-GRUPO | nenhum | o pet de hoje não usa a percepção para nada além da CO7 |
| **distinguir parceiro responsivo de objeto móvel** | só por construção: o outro chega em `social.outros`, os objetos em `mundo.vistos` | idem | o canal | — | `test_grupo_social.py:226` | nenhum | é uma etiqueta, não uma discriminação; nenhum teste de ao vivo × gravação |
| **sensibilidade à reciprocidade** | a reputação conta os atos testemunhados; o `k` sobe com quem tem reputação positiva | sim (CO6 e CO7) | a reputação, o `k`, o escudo | — | `test_cooperacao_co6.py:74-128`; G-PAR-CO6 | a H-REP da bancada saiu INCONCLUSIVA POR PREMISSA (16 vidas com oportunidade < 30) | nenhuma resposta do pet ao que o outro faz com ele |
| **coordenação temporal e espacial** | a vez sorteada (não é coordenação); o `seguir` (que o modular não escolhe) | não | — | — | — | nenhum | tudo |
| **comunicação que muda a decisão do receptor** | a ação visível lida como "aflito" pela CO7; os sons (Python, desligados) | a ação visível | o escudo lê `emburrar`/`chamar_atencao` | — | `test_cooperacao_co7.py:84-118,132` | os deveres mudam pouco o que o pet faz (seção 1.4) | nenhum canal dirigido, nenhum sinal aprendido |
| **aprendizado sobre um parceiro específico** | a reputação por par (regra), o `antes[id]`; o `ModeloOutros` do A (registrado) | a reputação, no painel e no `k` | sim | **nada** | `test_bancada_dois_pets.py:466-518` | nenhum | tudo |
| **atividade conjunta com papéis** | nada | não | — | — | — | — | tudo; não há tarefa que peça dois |
| **recuperação após interrupção** | o `continuar` de um alvo social, por uma decisão (`mundo.py:1864`) | não | sim | — | — | — | tudo |
| **generalização para parceiro desconhecido** | o grupo tem no máximo 2, sempre irmãos recém-nascidos (`config.py:2079`; `grupo.py:251`) | não | — | — | — | — | tudo |

### 1.4 A bancada da CO7, relida nos artefatos

Os artefatos são de `artifacts_v3_cooperacao_bancada/`:
- `resultado.json`: sha256 `ec143b7a13bb41a071509c03e42a061681d138200aa05c1f6b758602a764d9b7`;
- `resultado_ad1.json`: sha256 `d693f0466c784ebb3ce6a4434959fd865da3ea00bb631a4e07d7527e3453f28c`.

As vidas (`experiments/runs/cooperacao_bancada/*.jsonl`) **não estão no git**: a análise não se refaz pelo repositório
(`docs/AUDITORIA_EVIDENCIA.md`, 1.8).

| pergunta | CB4: dois pets modulares, dono atencioso, comedouro comum (sementes 91201–91360) | adendo 1: o B é o `CerebroAleatorio` (92201–92280) |
|---|---|---|
| **as oportunidades** (um aflito indo para uma comida que o pet vê) | 41 de 160 vidas, 197 oportunidades | 69 de 80 vidas, 837 a 839 por braço |
| **a CO7 mudou alguma medida** | em 5 das 160 vidas | em 12 das 80 |
| **H-EMERGE** (o aflito come a comida disputada, B1 − B0) | +0,005 [0,000; 0,015], n = 41, NÃO CONFIRMA (δ = 0,10) | +0,0008 [−0,0014; +0,0039], n = 69, NÃO CONFIRMA |
| **o escudo** (B1E, só o escudo, contra B0) | repete o B1 | +0,0008 (= o B1); a P1-neg cai de 0,081 para 0,072 |
| **a universalização** (B1U contra B0) | repete o B0 | +0,0015 |
| **a culpa e a inveja** (B1A contra B0) | repete o B0 | 0,0: disparam em 11,7 % e 5,9 % das decisões do A e não mudam nenhuma escolha |
| **H-CUSTO** (a privação do próprio pet) | −0,00001 [−0,0001; 0,00006], CONFIRMA | +0,0009 [−0,0012; +0,0034], n = 80, CONFIRMA |
| **H-REP** | INCONCLUSIVA POR PREMISSA | fora (o aleatório não retribui) |

**O que isso permite concluir:**
- **Com os pesos de hoje, os deveres impostos por regra quase não mudam o comportamento**, nem quando a situação acontece: o pet já
  quase não disputava a comida do aflito (a P1-neg, 8,1 %). O escudo faz o que diz e tem pouco a tirar.
- **O empurrão afetivo dispara e não vira decisão.**
- **Sobre a pergunta desta investigação** (o contato entre dois pets afeta funcionalmente as decisões e a experiência?), a bancada diz:
  - pelas regras da CO7, quase nada;
  - pelo aprendizado, nada, porque não há caminho;
  - a experiência no corpo também não muda, porque o corpo não sente o outro.

**O que não permite concluir:**
- que a cooperação não pode emergir: o mundo quase não dá a situação (CB4), e o irmão do adendo não é um pet de verdade (AD1-2);
- nada sobre um parceiro com o qual o pet tenha o que ganhar ou perder no corpo, porque esse parceiro não existe hoje.

## 2. A literatura: matriz de referências e aplicação

As 10 fontes estão em `docs/referencias/v3_social_par_referencias_verificadas.csv`, com o conteúdo lido de cada uma. A verificação foi
feita por um subagente (Opus 5.5) que baixou os PDFs abertos; os 5 DOIs foram reconferidos no Crossref nesta sessão
(`docs/referencias/v3_social_par_verificacao_crossref.json`). **Só resumo** quer dizer que o texto completo não abriu (403); o que não está
no resumo fica "não conferido".

| fonte | lido | estudo e agentes | manipulação | resultado relevante | limite | adaptação ao DigiLab (**proposta desta análise**) |
|---|---|---|---|---|---|---|
| De Jaegher e Di Paolo 2007, `10.1007/s11097-007-9076-9` | texto completo | ensaio teórico | — | interação = acoplamento regulado entre autônomos; quebras e recuperações fazem a história da interação (pp. 493, 496) | especulativo (p. 502); sem medida operacional (p. 504) | medir contato, quebra e recuperação como séries no tempo, e não só taxas |
| Auvray, Lenay e Stewart 2009, `10.1016/j.newideapsych.2007.12.002` | **só resumo**; procedimento por De Jaegher e Di Paolo (pp. 501-502) | pares humanos, avatar em 1-D, toque tudo ou nada | parceiro × objeto fixo × sombra móvel do parceiro | o reconhecimento do parceiro vem da atividade conjunta: só o contato mútuo é estável | números não conferidos | as três condições do experimento A; a "sombra" vira o parceiro de outra vida (seção 3.1) |
| Froese e Di Paolo 2008, `10.1007/978-3-540-69134-1_6` | texto completo (preprint) | 2 agentes CTRNN de 3 nós, 1-D, sensor liga/desliga, GA, sem aprendizado em vida | mútuo × playback da trajetória do parceiro, com ruído novo no outro | escore médio 268 ao vivo × 19 no playback (p. 6 do PDF); a falha vem da co-regulação perdida | um melhor indivíduo, clones, 1-D | **o protocolo da gravação** (seção 3.1) e a leitura "a diferença pode vir do acoplamento, sem mecanismo" |
| Froese e Di Paolo 2010, `10.1080/09540090903197928` | **só resumo** | robótica evolutiva, cruzamento perceptivo | não conferida | um modelo de circuito inferido do comportamento se mostrou infundado na dinâmica interna | não conferidas | toda leitura de mecanismo pede a ablação ou o estado interno, não só o comportamento |
| Warneken, Chen e Tomasello 2006, `10.1111/j.1467-8624.2006.00895.x` | **só resumo** | crianças de 18-24 meses e 3 chimpanzés, parceiro adulto humano | o adulto para num ponto da tarefa | todas as crianças tentaram reengajar o adulto ao menos uma vez; nenhum chimpanzé | 3 chimpanzés; parceiro humano | o procedimento da interrupção do D; "reengajar" vira uma ação com efeito causal sobre o outro, não intencionalidade |
| Foerster et al. 2016, NeurIPS 29 | texto completo | MARL, DIAL e RIAL | com e sem canal | comunicação aprendida com treino centralizado e gradiente pelo canal | incompatível com aprendizado em vida separado | só referência de teto; nada a portar |
| Lowe et al. 2019, AAMAS | texto completo | jogos matriciais com canal | intervenção na mensagem (CIC), mensagens embaralhadas | correlação mensagem-ação aparece sem uso; a CIC fica no mínimo (p. 698) | um passo, sem corpo | **as medidas do C:** intervir no sinal; nunca concluir comunicação por correlação |
| Jaques et al. 2019, ICML | texto completo | Cleanup e Harvest, A3C | a influência causal como recompensa; MOA | eleva a recompensa coletiva; a influência pode ser não cooperativa (p. 4) | muitos hiperparâmetros, 5 sementes | **só métrica de avaliação**, por ramos contrafactuais do replay (seção 4.2) |
| Rabinowitz et al. 2018, ICML | texto completo | ToMnet supervisionada, grade 11×11 | espécies de agentes; crença falsa | prevê ações de agentes de espécies diferentes; crença falsa na grade | o observador vê todo o estado (p. 2) | o critério do E: "prever o parceiro melhor depois de conhecê-lo", com o observador sob visão parcial |
| Hu et al. 2020, ICML | texto completo | Hanabi, SAD | cross-play com parceiros treinados à parte | self-play 23,97 × cross-play 2,52 (Tabela 1, p. 7) | treino offline | o desenho do F; o método não se porta |

**O que as fontes humanas inspiram e o que não transfere:**
- **Auvray et al.:** inspiram as três condições e a medida pela estabilidade do contato. Não transferem a instrução verbal, o clique de
  reconhecimento nem a motivação de procurar o outro: no pet, a "procura" precisa de uma razão no corpo (seção 5, M2).
- **Warneken et al.:** inspiram o ponto definido de interrupção e o controle "o parceiro deixou de ser necessário". Não transferem o gesto,
  a fala, a leitura de meta compartilhada nem a história com um adulto humano.

## 3. Os experimentos candidatos

Cada experimento tem o mesmo esqueleto de validade (seção 4). Os números são PROPOSTOS, SEM FONTE, até um plano de análise próprio.

### 3.1 A — Reciprocidade: parceiro ao vivo × gravação × parceiro de outra vida

**A pergunta:** o pet focal mantém e recupera o contato de forma diferente quando o parceiro responde a ele?

**As três condições** (o mesmo pet focal F, a mesma semente do grupo, o mesmo mundo):

| condição | o parceiro P | o que preserva | o que tira |
|---|---|---|---|
| **VIVO** | o pet P de verdade, com o cérebro dele | tudo | — |
| **GRAV** | P executa, decisão a decisão, as decisões que ele tomou na vida VIVO da mesma semente | a aparência, os canais, a cinemática, a física (P come, chuta e anda pelo próprio motor) e a sequência de decisões | a resposta a F |
| **OUTRA** | P executa as decisões que tomou numa vida da mesma semente em que F foi trocado por um pet passivo (o `Passivo` de `tests/test_grupo.py:71-80`) | a aparência, os canais, um movimento plausível no mesmo mundo | qualquer correlação com a história de F |

- **A gravação executada fisicamente** (o protocolo de Froese e Di Paolo 2008, adaptado):
  - O que se grava é a **decisão** de P (a ação e o alvo, com o tipo, o id e as coordenadas), e não a posição.
  - Na reexecução, o motor de P anda, come e chuta como sempre, pela física de hoje. Por isso a cinemática é a do próprio motor, e um
    consumo só acontece se a comida ainda está lá.
  - Quando o alvo gravado não está mais entre os candidatos, vale uma regra escrita antes: o candidato do mesmo tipo mais perto das
    coordenadas gravadas; se não houver, o ponto gravado como alvo de explorar.
  - Cada caso conta como um **desvio da gravação**, que é medida e não erro.
  - O corpo de P continua vivo. Ele não responde a nada, nem à própria fome.
  - O dono de P também é gravado: os eventos dele na vida VIVO são rejogados, para que nada de P responda a F. O dono de F é o de sempre
    nas três condições.
- **Colisões:** não existem, porque os pets não ocupam célula (`mundo.py:1627`). **Recursos:** a comida e a bola são as do mundo comum. O
  número de desvios e de consumos falhos de P vai no resultado.
- **A perturbação:** sem ela, a GRAV é a VIVO byte a byte. O motor é determinístico, então o mesmo F diante das mesmas decisões de P vive a
  mesma vida, e isso é o teste de validade da gravação (o G-GRAV-IDENT da E1). A diferença só aparece depois de uma perturbação
  exógena num tick t0: F é levado a um ponto a d0 células de P pelo `levar_pet` que o motor já tem (`digilab/mundo.py:2351`), aceito no
  grupo com a origem `intervencao`. O t0 e a direção são sorteados por vida num fluxo próprio, antes, e são os mesmos nas três condições.
- **O laço aberto pelo alvo:** um alvo de P que se move com F (o `seguir`) ou que F pode mover (a bola) é reexecutado pelas coordenadas
  gravadas, nunca pelo candidato vivo. Senão a gravação voltaria a seguir F (a espec da E1, 2.2).
- **O replay do parceiro não é o replay do jogo.**
  - O replay do jogo (`Motor.reproduzir`, `reproduzir_grupo`) refaz a vida inteira a partir das causas de fora, com os dois cérebros
    decidindo de novo. É uma garantia de determinismo e não muda nada.
  - O replay do parceiro é uma **intervenção**: tira o cérebro de P do laço e põe no lugar uma lista de decisões. A vida que sai é outra
    vida, com um registro próprio marcado como de pesquisa. Ela não pode morar no jogo: o `GrupoDoJogo.reproduzir` refaz dois `Motor`s
    (`grupo_jogo.ts:166`) e o save quebraria. Ela mora na bancada do Python, atrás de uma chave de pesquisa.
- **As medidas:**
  - a fração das decisões em contato (distância ≤ 1 célula) e perto (≤ 6) depois de t0;
  - o tempo até o reencontro, censurado na janela;
  - a duração dos episódios de contato;
  - a **contingência nas duas direções:** P(F se aproxima | P se aproximou no passo anterior) − P(F se aproxima | P se afastou), e o mesmo
    de P para F. Na GRAV, a contingência de P para F tem de dar ≈ 0 por construção, e isso serve de conferência da medida.
- **Como ler uma diferença VIVO − GRAV:**
  - **pelo acoplamento:** a dinâmica mútua se sustenta e a de mão única não, sem que F distinga nada (Froese e Di Paolo 2008). O sinal
    disso é que a diferença aparece já no primeiro encontro depois de t0 e não cresce com a idade;
  - **por um mecanismo aprendido:** F passa a reagir diferente a um parceiro que não responde. Isso exige que a diferença cresça com a
    experiência e suma com a plasticidade congelada (o braço B da ablação da A2 aplicado a F);
  - **por outra propriedade:** a comida que P gravado deixou de comer, a bola em outro lugar. Isso se controla pela contagem de desvios e
    de consumos falhos, e por uma variante sem comida no mapa (só a bola e o vagar).
- **GRAV − OUTRA:** separa a cinemática que já foi contingente a F (antes de t0) da que nunca foi.
- **No pet de hoje (o A0):** a previsão é "nenhuma diferença além do mundo comum", porque F não tem ação dirigida ao outro. É um resultado
  que vale registrar, mas só depois de a E1 mostrar que o instrumento detecta a diferença onde ela existe por construção.

### 3.2 B — Brincadeira coordenada: a bola

**A tarefa escolhida:** a bola, porque é a única ação de hoje que muda um objeto que o outro também usa. A bola rola na direção do golpe,
de onde o pet estava para a bola (`bolaNoGolpe`). Um "passe" pode sair da geometria quando os dois chegam de lados opostos. O transporte
conjunto não existe e não é escolhido.

- **A medida primária:** a taxa de chutes alternados (F chuta e P chuta em seguida, dentro de uma janela de decisões) por chute.
- **As medidas ao lado:** a latência entre os chutes, a continuidade (o comprimento das sequências) e o custo no corpo (a energia gasta e
  a fome, pelos receptores do próprio pet).
- **As perturbações:** P congelado por n decisões (atraso), P tirado por uma janela (interrupção breve) e P deslocado (mudança de
  posição), por eventos de pesquisa.
- **Os controles:**
  - **o relógio:** P GRAV, como no A. Uma alternância que sobrevive à gravação não é resposta ao parceiro;
  - **a atração pelo mesmo objeto e o estímulo comum:** a alternância esperada sob processos independentes, por substitutos que
    deslocam no tempo a sequência de chutes de P dentro da mesma vida (deslocamento circular). Isso preserva a taxa de cada um e quebra o
    acoplamento;
  - **o pet sozinho com a bola:** a taxa de chutes sem parceiro.
- **No pet de hoje:** viável, porque a bola e a unidade `brincar/bola` existem. A previsão é que a alternância não passe dos substitutos, já
  que nada no modular leva o outro em conta.

### 3.3 C — Informação assimétrica

**O desenho:**
- F vê uma comida. P está fora do raio da visão dela (6 células) e dentro do alcance do som (16, PROPOSTO em `dois_pets.md`, seção 5.4).
- O sinal possível é o som `comendo`, que F emite ao comer, ou o `chamado`.
- **As condições:**
  - o som original;
  - o silêncio (o som não chega a P);
  - a intervenção: o som chega com a direção trocada, ou atribuído a um ponto sorteado;
  - os sons embaralhados entre vidas.
- **A medida primária** é a influência causal da comunicação (CIC de Lowe et al. 2019): a mudança da política de P entre o som original e
  o som intervindo, com o sucesso da tarefa (P acha a comida) ao lado.
- **As pistas alternativas a controlar:**
  - seguir o emissor (F visível a P);
  - ver o recurso (a comida a até 6 células de P);
  - inferi-lo pela posição inicial (os pontos de partida e da comida sorteados por vida).
- **O que é do projetista:** a física do som (quem emite, quando, o alcance) e o vocabulário fechado, se houver. **O que precisa ser
  aprendido:** o valor de ir na direção do som para P, pela consequência (achou comida). O significado do sinal é a associação que P
  aprende. Na emissão de hoje, F não escolhe emitir: o som é involuntário, honesto por construção.
- **O limite de arquitetura:** um sinal **escolhido** por F (o `chamar_atencao` com destinatário, DP-6) só se aprende se o corpo de F
  ganhar algo quando P chega. Hoje não ganha (seção 1.2). Isso põe o C atrás do M2 (seção 5).
- **Hoje:** inviável. O modular não lê os sons (`digibrain/sens.py:192-194`), e os sons não existem no TS.

### 3.4 D — Interrupção da atividade conjunta

- **O pré-requisito:** uma tarefa com funções complementares. Hoje não há nenhuma: o sacudir a árvore é do dono e falha no grupo
  (`mundo.py:203-204`), e nenhum objeto pede dois pets.
- **O desenho, quando houver a tarefa:**
  - interromper P num ponto definido (congelado ou tirado) e observar o que F faz: espera, volta, recruta (uma ação que aumenta a chance
    de P voltar), assume o papel de P ou abandona;
  - **o controle:** a mesma interrupção quando P deixou de ser necessário (a tarefa já está feita, ou F consegue fazê-la sozinho);
  - a troca de papéis e de posições entre as tentativas.
- **Regra × experiência:** a mesma resposta com o aprendizado congelado é da regra; a que só aparece com a história é da experiência.
- **Hoje:** inviável sem uma mecânica nova de mundo. É o último da fila.

### 3.5 E — Aprendizado sobre o parceiro

- **O desenho:**
  - parceiros com padrões diferentes, por exemplo um informante confiável (onde ele come é fruta boa) e um não confiável, pelo efeito da
    fruta por árvore que o mundo já tem (`dois_pets.md`, seção 11);
  - a medida: F prevê e decide melhor sobre aquele parceiro depois de conhecê-lo (a fração das idas de F a `onde_comeu` de cada um que
    acham fruta boa, e a escolha entre os dois);
  - a revisão: o parceiro troca de padrão num dia sorteado, e se mede o tempo de F até reverter.
- **A identidade:**
  - a única pista de identidade na percepção é o `id`, um rótulo e não um traço percebido. No jogo os dois pets têm espécies diferentes, mas
    o cérebro não vê a espécie;
  - o rótulo é informação privilegiada e tem de ser declarado;
  - **o controle de aparência:** trocar os ids entre os parceiros no meio da vida. Se o aprendido segue o id e não o comportamento, F
    erra depois da troca.
- **O controle de posição e de contexto:** os parceiros começam em pontos sorteados e trocam de lado do mapa entre os dias.
- **Hoje:** inviável. O modular não tem memória por parceiro nem unidade que use o `onde_comeu`.

### 3.6 F — Generalização

- **O desenho:**
  - o parceiro habitual (o irmão com quem F cresceu), um parceiro treinado à parte (um pet que cresceu com outro irmão, numa semente
    reservada) e um desconhecido (de outra população);
  - **o desempenho inicial** (o primeiro encontro) separado da **adaptação** (a inclinação nos encontros seguintes), à maneira do
    cross-play de Hu et al. 2020;
  - as sementes, as populações e os pares de avaliação ficam reservados e nunca são usados no desenvolvimento.
- **O que se lê:** uma convenção específica do par cai no cruzamento; uma capacidade que se transfere não cai.
- **Hoje:** inviável. Pede o E e um grupo que aceite um pet já crescido (hoje só entra recém-nascido, `grupo.py:251-252`).

### 3.7 A comparação

| | viável hoje | o que mede no pet de hoje | o que pede antes | custo (PROPOSTO) | o que destrava |
|---|---|---|---|---|---|
| **A** | **sim, no Python**, com a E1 | só o mundo comum | a E1 | E1: uma sessão de código; o A0: ~200 pares × 3 condições × 3 dias, dentro de 4 processos | o instrumento de B, D, E e F |
| **B** | sim, no Python | a alternância por geometria e estímulo comum | a E1 (o congelar e o deslocar) | como o A0, mais os substitutos | o primeiro sinal de coordenação |
| **C** | não | — | M2 (a razão do corpo), M4 (o som no modular) | alto | a comunicação |
| **D** | não | — | uma tarefa de dois pets (mecânica nova de mundo) | o mais alto | os papéis |
| **E** | não | — | M3 (a memória por parceiro) | médio | o F |
| **F** | não | — | E, e o pet crescido entrando no grupo | alto | a generalização |

## 4. A validade dos testes

### 4.1 O esqueleto, experimento por experimento

| | hipótese × alternativa | manipulada | o que cada agente observa | controles | primária | leitura | unidade | tamanho (PROPOSTO) | o que enfraqueceria |
|---|---|---|---|---|---|---|---|---|---|
| **A** | F recupera o contato mais depressa com P responsivo × não há diferença além do mundo comum | a condição de P | F: a percepção social de hoje (visão, toque); P GRAV: nada (laço aberto) | GRAV, OUTRA, a variante sem comida, a plasticidade congelada | o tempo até o reencontro depois de t0, VIVO − GRAV | IC95 pareado, as classes < 0, ≈ 0, > 0 e indeterminado, com a margem do plano | a semente do grupo (o par) | 200 sementes; o piloto fixa o N | uma diferença que some na variante sem comida (era recurso) |
| **B** | os chutes alternam acima dos substitutos × alternância só por estímulo comum | a condição de P e as perturbações | os dois: a bola e o outro à vista | GRAV, substitutos circulares, pet sozinho | a alternância observada − a dos substitutos | idem | a semente | idem | uma alternância que sobrevive à GRAV |
| **C** | o som muda a política de P (CIC > 0) e o sucesso × P acha pelo vagar | o som | P: só o som; F: a comida | silêncio, direção trocada, sons embaralhados, recurso fora da visão | a CIC | idem | a semente | depois do M2 e do M4 | uma CIC que some ao esconder o emissor (era seguir) |
| **D** | F recruta ou espera quando P é necessário × abandona igual nos dois casos | a necessidade de P | os dois, de hoje | P desnecessário; aprendizado congelado | a taxa de reengajamento | idem | a semente | depois da tarefa | a mesma taxa com P desnecessário |
| **E** | F decide melhor sobre o parceiro conhecido × decide igual | o padrão do parceiro | F: o id e o `onde_comeu` | a troca de ids, posições sorteadas | a fração de idas boas por parceiro, conhecido − novo | idem | a semente | depois do M3 | o aprendido segue o id depois da troca |
| **F** | o desempenho inicial com o desconhecido fica perto do habitual × cai | o parceiro | idem | o treinado à parte | habitual − desconhecido no primeiro encontro, e a adaptação | idem | o par avaliado | depois do E | queda com o treinado à parte igual à com o desconhecido |

### 4.2 As regras que valem para todos

- **A dependência dentro do par:** F e P não são independentes. A unidade é o par (a semente do grupo), e a medida de cada par é um número
  só (a média dos episódios dele). As condições são pareadas pela semente, e a reamostragem é do par, não do episódio nem da decisão.
- **Os encontros repetidos:** os episódios de uma vida são dependentes. Entram na média do par, nunca como unidades. A adaptação ao longo
  dos encontros é uma inclinação por par.
- **A incerteza:** IC95 por bootstrap pareado por semente (10 000 reamostras, a semente do bootstrap fixa no plano) ou pelo t sobre os
  pares, com o `ic_t` de `digilab/metrics.py`.
- **As múltiplas comparações:** um contraste primário por experimento. Os secundários vão com Holm na família escrita no plano.
- **As oportunidades sociais:** cada plano define a oportunidade (A: uma perturbação com P a até d0; B: a bola à vista dos dois; C: um som
  emitido com P fora da visão), conta a frequência num piloto de sementes próprias e tem uma regra de parada. Com menos de `n_min` pares
  com oportunidade, a leitura é INCONCLUSIVO POR PREMISSA, a lição da CB4.
- **As quatro coisas separadas:**
  - **influência causal:** a mudança no comportamento de um causada pelo outro;
  - **benefício conjunto:** o piso lexicográfico do par (D-MM-14);
  - **benefício individual:** os receptores de cada pet;
  - **estabilidade corporal:** a privação e a exaustão, as do descritivo da A1.

  Um ganho conjunto à custa da estabilidade de um dos dois é lido assim.
- **A influência social de Jaques et al.:**
  - **como métrica de avaliação, sim.** O motor é determinístico, então o avaliador ramifica a vida na decisão t, troca a ação de F por cada
    alternativa, rejoga uma janela e mede a divergência da política de P. Isso usa acesso privilegiado ao cérebro real de P e só existe na
    bancada, fora do jogo. É a CIC de Lowe et al. estendida a vários passos;
  - **como recompensa de treino, não.** O sinal de aprendizado do modular é a variação do corpo (`digilab/digibrain/afeto.py:139-146`). Uma recompensa de
    influência seria sucesso escrito pelo projetista, o achado D-LG-3 da auditoria. Ela pediria um modelo dos outros (o MOA), e a própria
    fonte diz que a influência pode ser não cooperativa (p. 4). Não é compatível com a arquitetura de hoje e não é recomendada.
- **As três origens de uma relação, separadas:**
  - **a imposta pelo código:** a CO7 inteira, o escudo e a culpa e a inveja. Lê-se pela ablação dos ganchos da bancada;
  - **a produzida pelo acoplamento:** VIVO − GRAV com a plasticidade congelada;
  - **a aprendida:** a parte da diferença que só aparece com a plasticidade ligada e cresce com a experiência.

### 4.3 A informação privilegiada

| quem | o que usa | existe no jogo? |
|---|---|---|
| a decisão (CO7) | a ação visível, a posição, a aproximação de uma comida; o `k`, cuja reputação usa o ganho real de quem venceu a disputa "anti" (`cooperacao.py:147-153`) | sim; o ganho real é um vazamento pequeno do corpo do outro para a decisão, só na disputa "anti" (rara: 2 disputas "anti" nas 80 vidas de cada braço do adendo) |
| a percepção | o `id` do outro, um rótulo | sim; é o que permite a memória por parceiro (E) e tem de ser declarado |
| o avaliador da bancada | a fome e o humor reais de cada pet (`run_v3_cooperacao_bancada.py:143-147`) | não; só depois da vida, fora da decisão |
| o avaliador proposto (A a F) | as posições, as ações, os receptores de cada pet; os ramos contrafactuais com o cérebro real de P | não; só na bancada |
| o treino | nada do outro | — |

## 5. Os mecanismos para o DigiLab

O mesmo caminho para todos: **a percepção entra no estado → muda uma intenção → produz uma ação → volta como consequência no corpo**. Hoje o
caminho quebra em dois pontos: não há intenção com o outro como alvo (o 2º passo), e o corpo não sente o outro (o 4º).

| | problema | mecanismo | interface | arquivos | teste |
|---|---|---|---|---|---|
| **M0 (a E1)** | não há como medir a resposta ao parceiro | o parceiro sob intervenção (VIVO, GRAV, OUTRA), a perturbação e as medidas de contato e de contingência | `PoliticaGravada` (Protocol `Politica`), o `levar_pet` no grupo com a origem `intervencao`, a `ConfigIntervencaoSocial` (pesquisa, desligada), funções novas em `digilab/metrics.py` | `experiments/bancada/parceiro.py`, `digilab/grupo.py`, `digilab/config.py`, `digilab/metrics.py` | G2, G-GRAV-IDENT, G-CONTROLE-POS, G-MET-NULO (a espec da E1) |
| **M1** | o modular não tem ação dirigida ao outro | as unidades `explorar/seguir:<id>` e `explorar/onde_comeu:<id>`, com o alvo que o motor já oferece; o valor pelo P1 e pelo P2 de sempre | `impulso.alvos` com `sens.social`, o `TIPOS_ALVO_DIGIBRAIN` com os dois tipos, o `escolher_alvo` pelo `id_alvo` | `digilab/digibrain/{impulso,adapt,sens}.py`, `config.py`; o espelho TS e o gabarito | G2 (chave desligada byte a byte), G-PAR, a escolha só com o outro à vista |
| **M2** | estar com o outro não muda nada no corpo, então não há o que aprender | um emissor do grafo do corpo, `companhia`: a proximidade ou o toque do outro baixam a solidão, sem ler nada do corpo do outro. É a CV-5 e a DP-12, adiantadas (SP-3) | um emissor externo declarado na seção 18 do corpo, lido da percepção social | `digilab/corpo.py`, `motor_corpo.py`, `grupo.py`; TS | G2, o grafo (laço de ganho entre os dois corpos), G-RECEPTOR-SOCIAL |
| **M3** | nada é aprendido por parceiro | o valor das unidades sociais indexado pelo `id` (e não só pela classe) | a chave da unidade já leva o id (`chaveUnidade(b, tipo, id)`) | `plast.py`/`plast.ts` | G2, a troca de ids (E) |
| **M4** | o modular não ouve o outro | a unidade `explorar/som:<id>` com a direção do som, quando a `ConfigSentidos` estiver ligada | `sens` lendo `ps.sentidos` | `digibrain/sens.py`, o porte dos sentidos ao TS | G2, G-PAR, a CIC |

**O que se reaproveita:**
- a percepção física do outro (a visão, o toque, o `onde_comeu`), sem mudança;
- o histórico de movimentos (o `antes[id]` do M-SENS e as posições no traço da bancada);
- a memória por parceiro só com o M3; o M-MEM já tem o campo `outro`;
- o aprendizado de consequências (o P1 e o P2), sem mudança;
- as intenções persistentes (o `continuar` do motor);
- as ações com destinatário: nenhuma hoje;
- os canais sensoriais e os chamados (o degrau 1b no Python);
- as sondas e os registros da bancada da cooperação (a `Coleta`, a P1, a P1-neg).

**O determinismo e a paridade:**
- toda peça nova entra atrás de uma chave desligada, com o gabarito antes e o G2;
- a perturbação e a gravação são eventos de pesquisa num registro próprio, marcado, que o jogo nunca lê;
- a rng da perturbação é um fluxo novo, `intervencao-social`, derivado da semente do grupo;
- o M0 é só do Python (pesquisa). Do M1 em diante, cada peça tem o espelho no TS e o G-PAR, se for ao jogo.

**O dimensionamento:**
- o M0 cabe numa sessão e não toca o jogo;
- o M1 é pequeno: os candidatos já existem;
- o M2 é a única ampliação de arquitetura, porque o corpo passa a ter uma entrada do outro. Ela se justifica porque, sem ela, o modular
  não tem como dar valor ao parceiro (seção 0, item 3).

## 6. A ordem recomendada

| passo | o quê | depende de | custo (PROPOSTO) |
|---|---|---|---|
| **E1** | o instrumento (M0) e a validação nos controles de regra fixa | SP-1, SP-2 | uma sessão de código, sem run |
| **A0 e B0** | o plano de análise e a run descritiva no pet de hoje (VIVO × GRAV × OUTRA; a bola com os substitutos) | a E1 na `main`; uma faixa nova | um plano e uma run, dentro de 4 processos |
| **SP-3** | a decisão do M2 (a companhia no corpo) e do M1 | o A0 | — |
| **M1 e M2** | as unidades sociais e a companhia no corpo, atrás de chaves | SP-3 | duas a três etapas de código, com o TS |
| **A1 e B1** | o A e o B com o M1 e o M2 | os mecanismos | uma run cada |
| **M3, E** | a memória por parceiro e o experimento E | o A1 | — |
| **M4, C** | o som no modular e o C | o M2 | — |
| **F** | a generalização | o E e o grupo aceitando um pet crescido | — |
| **D** | a tarefa de papéis e a interrupção | uma mecânica de mundo nova, com desenho próprio | — |

## 7. As decisões anteriores que merecem uma pergunta nova

| decisão | o que diz | a pergunta nova |
|---|---|---|
| **CV-5 e DP-12** | a solidão e a aglomeração no corpo só no degrau 3, depois de o degrau 1 ter resposta | sem o corpo sentir o outro, o degrau 1 não tem como ter resposta no modular, cujo aprendizado é do corpo. A companhia no corpo deve vir antes? (SP-3) |
| **DP-5** | o primeiro degrau é aprender observando | ainda vale, mas pede o M1: hoje o modular não pode ir aonde o outro comeu |
| **DP-8** | o alvo aprendido e o modelo dos outros no cérebro A | o A sai do jogo (a LIMPEZA). Essas peças do A não têm par no modular. Portar a ideia ao modular (M1, M3) ou deixá-la sair com o A? (SP-4) |
| **CO7-1 e CO7-7** | os deveres como restrição e o gesto na tela | o único comportamento social ativo é por regra, e quase não muda nada (seção 1.4). Seguir investindo nos pesos da CO7 ou deixar o social vir do aprendizado? (SP-5) |
| **D-CO3-3** | o encostar vale 0 | no jogo de hoje ele nem acontece, porque o modular não segue. Com o M1, ele passa a existir |
| **G-RECEPTOR-SOCIAL** | nenhum sentido lê o estado interno do outro | vale para a percepção, e a reputação tem um vazamento pequeno pelo ganho do vencedor da disputa "anti" (seção 4.3). Aceitar, ou trocar o valor por algo visível? (SP-6) |
| **PAR-14** | a jornada só no web, sem pesquisa | o habitante especial com DigiBrain da J1 seria um parceiro novo, fora do grupo. Fica fora desta frente |

## 8. Uma situação jogável

**"O irmão que vem quando chamam"**, depois do M1 e do M2, sem número na tela (D-MM-8):
- O pet em foco, com a solidão alta, vai até o irmão. Os dois ficam juntos, e a solidão dos dois cai (o M2).
- Com o tempo, cada pet aprende que ir ao irmão faz bem (o M1, pelo P1 e pelo P2). O jogador vê o hábito nascer: no começo eles se
  esbarram por acaso, depois um procura o outro.
- **O que o jogador pode provocar:** deixar um dos dois sem carinho por um tempo e ver o outro ir até ele. Ou separar os dois (levar um
  para longe) e ver se o outro vai atrás.
- **O que tornaria a relação visível:** o painel "Com o irmão" ganha a frase "gosta de ficar perto" quando o valor aprendido da unidade
  `seguir` passa de um limiar, em palavras. E o ícone de coração do "encostar", que hoje nunca aparece, passa a aparecer.
- **O que não se diz na tela:** "ama", "amigo", "sente falta". Só o que a medida sustenta.

## 9. As limitações e as decisões pendentes

**As limitações:**
- O levantamento do código foi de subagentes; só as linhas centrais (✓) foram reconferidas.
- Os testes do TS não foram rodados.
- Três fontes só pelo resumo. A A4 (Froese e Di Paolo 2010) poderia ter uma condição de gravação que não conferi; o protocolo usado é o
  da A3.
- As vidas da bancada da cooperação não estão no git; os números vêm só dos `resultado*.json`.
- Nenhuma afirmação de novidade: a interação mínima, a gravação de parceiro, a comunicação emergente e o cross-play estão publicados.

**As decisões para o Matheus:**

| id | o que decidir | recomendação | custo de errar |
|---|---|---|---|
| **SP-1** | a primeira etapa | **a E1, o instrumento com os dois controles de regra fixa**, sem mecanismo novo no pet | começar por um mecanismo (M1) sem o instrumento: não se sabe se o que muda é da relação ou do mundo comum |
| **SP-2** | onde mora a gravação | **só na bancada do Python**, atrás da `ConfigIntervencaoSocial`, num registro de pesquisa | no jogo, ela quebraria o save e o replay (`grupo_jogo.ts:166`) |
| **SP-3** | a companhia no corpo (M2) antes do degrau 3 | **sim, depois do A0**: o emissor `companhia` baixando a solidão, só pelo que é físico | sem ele, o modular não tem como dar valor ao outro; com ele cedo demais, o "aprendido" mistura o contágio com a companhia (o motivo da DP-12) |
| **SP-4** | as peças sociais do cérebro A | **portar a ideia ao modular** (o M1 e o M3), não o código | deixá-las sair com o A apaga o único desenho de alvo social que existia |
| **SP-5** | os pesos da CO7 | **congelar onde estão** e medir o social aprendido primeiro | subir os pesos agora mede o projetista, não o pet |
| **SP-6** | o vazamento do ganho do vencedor na reputação | **aceitar e declarar**: é raro e só na disputa "anti" | trocá-lo agora muda a CO6 e a CO7 do jogo por pouco |
| **SP-7** | a margem e o N do A0 | **num plano de análise próprio, depois da E1** | escolher agora, sem o piloto, repete a CB4 |
| **SP-8** | os experimentos C, D e F | **ficam como desenho, sem tarefa**, até o M2 e o E | abrir cedo gasta etapas em mecânicas que dependem do corpo sentir o outro |

## 10. Referências

Todas em `docs/referencias/v3_social_par_referencias_verificadas.csv`:
- `10.1007/s11097-007-9076-9`, `10.1016/j.newideapsych.2007.12.002`, `10.1007/978-3-540-69134-1_6`, `10.1080/09540090903197928`,
  `10.1111/j.1467-8624.2006.00895.x`;
- e as sem DOI: NeurIPS 29 (Foerster et al.), AAMAS 2019 (Lowe et al.), PMLR 97 (Jaques et al.), PMLR 80 (Rabinowitz et al.) e PMLR 119
  (Hu et al.).
