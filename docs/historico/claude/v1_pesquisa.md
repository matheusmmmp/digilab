# A pesquisa da v1: resultados e leituras

Seções movidas inteiras do CLAUDE.md da raiz na etapa 1 da rodada de saúde (`docs/TAREFA_V2_SAUDE.md`, 2026-10-13): a arena v1, a
confirmatória, a educação, a linhagem, a pergunta do efeito do dono (encerrada) e a personalidade. Os números vêm dos artefatos citados em
cada seção.

## Estado atual (run canônica em `artifacts/`, protocolo `adce99fc3fdc…`)

Números abaixo vêm de `artifacts/metrics.json` e `artifacts/divergence.json`. Se reproduzir a
run, confira contra esses arquivos, não contra este texto.

- Run **APROVADA**, mas com 12 parâmetros ainda **PROPOSTOS** (orçamento, duração, definição
  de vitória, limiar etc.). O pesquisador ainda não os referendou.
- **Divergência entre políticas passou por margem mínima**: JSD média entre braços 0,0204 bits vs
  limiar 0,02. Dentro do braço 0,0131; piso de ruído 0,0125. Atencioso × relapso (0,0107) fica
  abaixo da divergência intra-braço. O aprendizado mexe pouco no comportamento (≈0,03–0,05 bits
  do instinto). O ambiente está no limite de profundidade.
- **Resultado central**: atencioso vence aleatório, 0,72 pontos, IC95 [0,64, 0,82], 5 sementes.
- **Confundidor não resolvido**: stats de combate vêm dos traços, e traços refletem também o
  *estado de vida* (fome etc.), não só aprendizado. Com políticas quase iguais, a vitória pode
  vir do cuidado, não do treino. A ablação abaixo (2026-09-24) testou isso.
- Com 16 interações/dia o braço **relapso** mantém o pet saudável — não é relapso de fato nesse orçamento.
- Erro padrão do Bradley-Terry trata partidas como independentes (subestima); a incerteza honesta
  é o bootstrap sobre sementes.

## Ablação treino × cuidado (2026-09-24, `artifacts_ablacao/`, protocolo `2b3460ee7a76…`)

Números abaixo vêm de `artifacts_ablacao/metrics.json` (`efeito_do_treino`,
`atencioso_vs_aleatorio_por_politica`) e `artifacts_ablacao/divergence.json`. Gerada em Windows,
Python 3.13.0.

- Desenho: 8 braços = 4 donos × {bandit, instinto}, mesmas 5 sementes, orçamento (224), duração
  (14 dias) e vitória da v1. Mesmo dono com a mesma rng nas duas políticas (`rotulo_dono`).
  Efeito do treino = (pontos atencioso − aleatório | bandit) − (idem | instinto), por semente.
- Run **APROVADA**. JSD entre braços bandit 0,020406 bits (limiar 0,02; mesmas vidas da canônica,
  mesmo número). JSD entre braços instinto: exatamente 0,0 nos 150 pares.
- **Cuidado sozinho (instinto)**: atencioso × aleatório 0,54 pontos, IC95 [0,46, 0,63]. **Não**
  distinguível de 0,5.
- **Com bandit, nesta run**: 0,61, IC95 [0,47, 0,71]. **Também não** distinguível de 0,5.
- **Efeito do treino**: 0,14 (em vantagem de pontos, escala −1..1), IC95 [0,00, 0,28]. O limite
  inferior é −4e−17, ou seja, zero em ponto flutuante. **Não distinguível de zero**: o IC encosta
  no zero. Por semente: +0,2, +0,4, +0,1, −0,1, +0,1.
- **Achado colateral importante**: as vidas bandit da ablação são byte a byte as da canônica. Só
  mudaram as sementes das partidas (derivadas do nome do braço: `atencioso@101` →
  `atencioso-bandit@101`). Com os mesmos pets, atencioso × aleatório caiu de 0,72 [0,64, 0,82]
  para 0,61 [0,47, 0,71]; a semente 505 foi de 0,90 para 0,60. O resultado central da canônica
  **depende do sorteio das partidas**; 20 partidas por par é pouco. O IC por bootstrap sobre 5
  sementes não captura essa fonte de variância de forma confiável.
- Leitura: a hipótese "treino vence" não está sustentada com este orçamento de partidas. Nem
  treino nem cuidado separam atencioso de aleatório com confiança nesta run.

## Reprodutibilidade entre plataformas

Os artefatos de `artifacts/` foram gerados em Linux com Python 3.11. Em Windows eles **não se
reproduzem byte a byte**, com nenhuma versão de Python: o CPython usa a libm do sistema
(sin/cos/log diferem no último bit entre glibc e MSVC), e do 3.12 em diante o `sum()` de floats
é compensado. Diferença relativa ≤ 2e−13, nenhuma decisão muda: logs de vida, partidas e
resultado central idênticos. `test_canonico_intacto.py` confere byte a byte só no ambiente de
origem e, fora dele, exige discretos idênticos e floats com erro relativo ≤ 1e−9. Replay dentro do
mesmo ambiente continua bit a bit (é o que o orquestrador confere). Artefatos agora são
gravados sempre com LF (antes saíam CRLF no Windows).

## Análise de poder (2026-09-27, `docs/TAREFA_ANALISE_PODER.md`, `artifacts_poder/`)

`experiments/run_poder.py` (piloto) e `experiments/analisar_poder.py --etapa 2|3|4`; config
`experiments/configs/poder_pesquisa.json` (arena V21C normalizada, pets do pipeline do treino, sementes de
piloto 50001–50020 e confirmatórias 60001–60160). `ConfigArenaPesquisa.condicao_neutra` (desligada por
padrão; as runs antigas não mudam). Plano congelado em `docs/PLANO_ANALISE.md` (desenho B, condição
neutra, decidido antes da run).

- Os ovos dominam: σ²_ovo 0,17 × σ²_partida_1 0,058 no desenho A (ICC 0,74); com M = 100 as partidas são
  ~0,3% da variância do estimador. Aumentar N ajuda; aumentar M não.
- Δ = 0,10 com poder 0,8: A precisa de ~135 ovos (~12 min de máquina), B de ~40–44 (~5 min).
- Neutralizar a condição física tira cerca de metade do efeito do A no piloto (0,642 → 0,575).

## Confirmatória e educação-v1 (2026-09-28, branch `educacao-heranca-lesoes`)

- **Confirmatória** (`experiments/run_confirmatoria.py`, `artifacts_confirmatoria/resultado.json`, 160 ovos):
  - desenho B, neutra: atencioso − aleatório −0,034, IC95 [−0,072; +0,006] → hipótese central **REFUTADA**;
  - secundárias (Holm): relapso, incoerente e exigente abaixo do aleatório.
- **educação-v1** (`docs/DESIGN_EDUCACAO_HERANCA_LESOES.md`):
  - `MotorEducacao` (`digilab/educacao.py`, chaves `ConfigEducacao.ligada` e `ConfigLesoes.ligada`, desligadas por padrão): travessuras com janela e disciplina; eventos novos no log `luta`, `origem` e `decisao_externa`;
  - lesões e morte; qualificação por vitórias (condição para adulto);
  - herança (`digilab/heranca.py`);
  - durações teste/canônica;
  - personas de dono (`digilab/personas.py`, `tools/gerar_personas.py`);
  - modo livre gravado (`tools/decisor_livre.py`).
  - Parâmetros com status e fonte em `protocol.PARAMETROS_EDUCACAO_V1`.
- **Exploratória V3** (`docs/PLANO_ANALISE_V3.md`, `artifacts_educacao/`):
  - com educação, lesões e sparring real, atencioso − aleatório **+0,121** [+0,066; +0,175] (cerca de metade vem das mortes do aleatório; pós hoc sem mortes: +0,058);
  - atencioso − permissivo +0,077;
  - gate de equilíbrio dos estilos aprovado na neutra, reprovado na real.
- **V3c, personas** (`artifacts_educacao_v3c/`, lote `gemma2-9b-01`, 24 personas × 40 ovos, 2026-09-29):
  - os braços fixos repetem a V3 (atencioso − aleatório +0,139 [+0,058; +0,222]);
  - entre as personas, só o **limiar de cuidado** tem efeito com IC fora de zero: +0,065 [+0,008; +0,115] por 1,0 (cuidar mais cedo);
  - atender a janela, ceder com petisco, a coerência do feedback e o perfil de treino não têm efeito detectável;
  - as personas vão de 0,318 a 0,474 no painel, todas abaixo do atencioso (0,528); 17 de 960 vidas morreram;
  - 3 aleatórios mortos têm a saúde final um pouco diferente da V3 (a morte agora é vista no fim do avanço): mesmo tick e causa, e pet morto conta 0 no painel.
- **V3b** (`artifacts_educacao_v3b/`): "luta treina" levou 577/640 pets à forma sombria. Ficou desligado (opção B), e o equilíbrio dos estilos virou tarefa de game design (REGISTRO_DESVIOS).
- **Web**: pets v4 (`VERSAO_PET = 4`, só ovos novos; v1–v3 e gabaritos intactos):
  - janelas, disciplina, lesão e morte, qualificação, herança (Cruzar em Meus pets);
  - dicas do Bit;
  - constantes `CED`, `CLE` e `CHE` conferidas contra o Python.

## Linhagem, E1 natureza × criação (2026-09-29, `docs/PLANO_ANALISE_LINHAGEM.md`) — gate FALHOU

Exceção de escopo autorizada pelo Matheus **só para o E1** de `docs/PLANO_LINHAGEM_ALIFE.md`; nenhuma mecânica nova.
`experiments/run_natureza_criacao.py` separa a semente do genoma (`g`: espécie e os dois temperamentos) da do
ambiente (`r`: motor, dono, travessuras, lesões, sparring) sem mexer no `engine.py`; com `g = r` a vida é a da V3
byte a byte (teste e logs da V3 em disco). `metrics.componentes_cruzados`/`decomposicao_cruzada` (estende a
`decomposicao_ovo_braco`) e `bootstrap_cruzado` (pigeonhole). Números de
`artifacts_linhagem/natureza_criacao/<rodada>/resultado.json`; 40 genomas × 4 donos × 4 ambientes, painel B neutra.

- **Gate (espécie fixa, brasa): FALHOU.** σ²_genoma +0,0016, IC95 pigeonhole [−0,0007; +0,0032] (4,9% da variância).
  Reamostrando só os genomas (secundário) o IC é [+0,0005; +0,0028]: a incerteza vem dos só 4 ambientes. Pelo plano
  congelado, E2 e E3 não seguem com este genoma sem decisão do Matheus.
- O que pesa: resíduo 66% e **dono × ambiente 22%** (as mortes do aleatório, 32 de 160, dependem do ambiente); dono 5%.
- Com as 4 espécies (descritiva): σ²_genoma +0,0030 [+0,0002; +0,0058], 8,4%; a espécie explica 32% da variação
  entre genomas (ferrugem 0,467 × cirro 0,372: E2 de novo).
- Donos (espécie fixa): atencioso − aleatório **+0,123** [+0,016; +0,204] (repete a V3, +0,121); atencioso −
  permissivo +0,005 [−0,127; +0,142] (na V3 era +0,077).
- **Decisão do Matheus (2026-09-29): a linhagem para como pesquisa.** E2–E4 arquivados; fica como mecânica de jogo
  (herança v4). Um genoma com aptidões por indivíduo foi descartado: o treino é normalizado na arena e ajustar o
  genoma para passar o gate viciaria o teste. Pergunta aberta mais promissora: a interação dono × ambiente.
- **Análise dono × ambiente** (exploratória, pós hoc, `docs/ANALISE_DONO_AMBIENTE_E1.md`,
  `experiments/analisar_dono_ambiente.py` → `artifacts_linhagem/dono_ambiente/resultado.json`): as mortes são todas
  "lesão sem tratar" (o ambiente sorteia a exposição; o aleatório nunca responde a lesão e o relapso só na visita:
  regra do dono sintético). Sem as mortes a interação continua porque o ambiente muda a **forma** final, e **a forma
  explica 96% da taxa no painel** (furioso 0,71 × titã 0,19). Dentro da forma sobra 4%; nele o dono explica 22%
  (atencioso +0,027 acima da média da forma, pelo ε da disciplina). Leitura: o painel mede quase só o arquétipo; a
  V4 "cuidado reduz a variância entre ambientes" testaria regras escritas por nós e **não deve rodar**.
- A rodada balanceada caiu ao gravar o meta (outra sessão trocou o branch da pasta `v1` no meio da run); a análise
  foi refeita dos arquivos gravados (`--reanalisar`, conferido: a reanálise da espécie fixa sai idêntica).

## Pergunta do efeito do dono: ENCERRADA (2026-10-01, `docs/LEITURA_CONSOLIDADA_DONO.md`)

Decisão do Matheus, depois das três runs abaixo (V21D no painel, Etapa A e Etapa B). Leitura consolidada: **neste
motor, o dono pesa pelo cuidado (mortes, saúde, limiar de cuidado), não pelo ensino.** O feedback deixa pouca marca no
que o pet aprende, essa marca depende mais do ambiente que do dono, e nem comprimir as formas nem levar o caráter
direto aos stats deu peso ao dono.
- **Não rodar de novo** calibrações de forma ou de peso do caráter atrás de efeito do dono, nem a "V4" (cuidado
  reduz a variância entre ambientes).
- **Reabrir só com uma pergunta nova sobre o aprendiz**, com plano registrado antes da run.
- O código das runs fica, com as chaves desligadas por padrão.

## Painel do E1 com a V21D: força do canal de forma (2026-09-30, `docs/PLANO_ANALISE_V21D.md`) — COMPRESSÃO NÃO VERIFICADA

Pergunta adotada: que propriedade do mapa até o desempenho dá efeito mensurável ao dono? O desenho é pareado: as mesmas
640 vidas e sementes do E1 (vida em V21C: o sparring usa a `REGRAS_CAMPANHA`), e só o painel B luta com as quatro chaves
da V21D. Rodam `experiments/configs/linhagem/natureza_criacao_v21d.json` e `experiments/analisar_v21d.py`. Números de
`artifacts_linhagem/natureza_criacao_v21d/especie_fixa/analise_plano.json`; relatório em `docs/RESULTADO_V21D_PAINEL.md`.

- **Gate: COMPRESSÃO NÃO VERIFICADA**, no subconjunto primário (atencioso + permissivo, sem mortes):
  - r²_forma 0,929 → 0,939, Δ +0,010 [−0,042; +0,040];
  - pelo plano o experimento não testa a hipótese, e nada se conclui sobre o dono (o passo 2, Δfrac_D, não se aplica).
- **Por quê:** a V21D encolhe a amplitude entre as formas adultas (0,521 → 0,387), mas **troca a ordem** das duas mais
  comuns:
  - espelho (158 pets) 0,406 → 0,301;
  - muralha (128 pets) 0,279 → 0,351.
  Pesada pela distribuição de formas que a vida produz, a variância entre formas não cai. A compressão da validação é
  dos bots com pesos iguais.
- **QD:** o κ de Fleiss da forma entre ambientes fica perto de 0 em três donos (permissivo 0,27): o ambiente decide a
  forma mais que o dono ou o genoma.
- **Código:**
  - `regras_de` monta a `ConfigCombateV21D` só com uma chave dela na config;
  - `lutador_painel` usa `gambits_adulto`;
  - o `metrics.py` ganhou `r2_por_categoria`, `kappa_fleiss`, `qualidade_diversidade` e `icc_um_fator`;
  - conferido: vidas byte a byte iguais, piloto V21C igual e `analisar_dono_ambiente` igual.

## Canal do dono fora da forma, Etapa A (2026-09-30, `docs/PLANO_ANALISE_CANAL_DONO.md`) — SINAL PRESENTE

A Etapa A mede se o sinal do dono chega ao que o pet aprende. Não usa vida nova nem mecânica nova: o
`experiments/sinal_dono.py` reproduz as 640 vidas arquivadas do E1, confere cada uma contra o `pets.json` e decompõe
o caráter em `T_ADOL` por genoma × dono × ambiente. Números de `artifacts_linhagem/sinal_dono/resultado.json`;
relatório em `docs/RESULTADO_SINAL_DONO.md`.

- **Gate A: SINAL PRESENTE**, só pelo eixo **resistente**: σ²_D +0,0034, IC 98,75% [+0,0009; +0,0121], frac D 0,208.
  Atento, impetuoso e paciente não passam.
- **O sinal não é o da coerência.**
  - No eixo resistente, atencioso − aleatório é +0,012 [−0,091; +0,115]; o que se separa é o permissivo (−0,220) do
    relapso (−0,058).
  - Atencioso − aleatório só aparece no eixo paciente (+0,212 [+0,001; +0,461]), que não passa com Bonferroni.
- **O ambiente move o aprendizado:** dono × ambiente fica entre 24% e 48% de cada eixo.
- **A linha já é loteria:** o κ de Fleiss da linha entre ambientes fica perto de 0, salvo no permissivo (0,41).
- **Impostos** (descritivo): a disciplina é 99% dono; o vínculo tem atencioso − aleatório −0,176 (o defeito
  conhecido).
- **Etapa B:** autorizada pelo Matheus, condicionada a este gate. Pelo plano, só roda depois de um adendo registrado
  antes da run.

## Canal do dono fora da forma, Etapa B (2026-09-30) — CANAL NÃO ABERTO

O pet do painel luta com o peso do caráter nos stats multiplicado por k (`ConfigCatalogo.peso_carater_stats`, padrão
1,0; só no pet do painel, vidas iguais às do E1). k = 3 e k = 8: o k = 9 do plano quebrava a renormalização em 3 pets
e foi trocado antes da run (desvio registrado). Números de `artifacts_linhagem/natureza_criacao_canal/analise_plano.json`
(`experiments/analisar_canal.py`); relatório em `docs/RESULTADO_CANAL_DONO.md`.

- **Gate B: CANAL NÃO ABERTO**, por margem mínima: Δr² da forma nos vivos (k = 8) −0,039, IC95 [−0,081; +0,0008].
- **Descritivo:** o dono perde peso.
  - frac_D da taxa: 0,050 → 0,039 → 0,028;
  - atencioso − aleatório: Δ +0,007 [−0,018; +0,029].
  - O caráter amplificado afasta as formas (emboscador sobe, espelho e titã descem) e alimenta dono × ambiente.
  - Com k = 8, 30% dos stats ficam presos no limite.
- **Leitura:** o caminho da arquitetura, como testado, fecha negativo. O gargalo é o que o pet aprende, que carrega
  mais ambiente que dono. Neste motor o dono pesa pelo cuidado, não pelo ensino.

## Motivo, expressão e memória (2026-09-24, `docs/TAREFA_MEMORIA_EXPRESSAO.md`)

**Pré-condição dispensada**: a Parte A exigia a bateria do combate V2 APROVADA; ela está
REPROVADA (G4, G5). O Matheus mandou seguir mesmo assim; registrado em `docs/REGISTRO_DESVIOS.md`.
Números abaixo vêm de `artifacts_expressao/legibilidade.json` e `artifacts_v1_memoria/metrics.json`.

- Parte A é somente leitura: V1 canônica e bateria V2 reproduzem os artefatos (testes). `ConfigExpressao`
  não entra em nenhum hash (teste). `PoliticaInstinto.ultima_regra` e `PoliticaBandit.ultima_decisao`
  são atributos somente leitura; `estado_interno()` não mudou.
- **Honestidade do fator do bandit** (desvio registrado): só vira fator uma contribuição POSITIVA,
  ≥ `limiar_motivo`, e só quando o termo aprendido mudou a escolha (sem ele, o argmax de
  log-prior + Gumbel daria outra ação). A fórmula literal da tarefa dava fator em 100% das decisões
  (sempre há contribuição acima do limiar, muitas vezes ruído de Thompson).
- **Legibilidade na vida é baixa no bandit**: 13,3% (relapso) a 18,5% (atencioso) das decisões têm
  fator; é exatamente a fração em que o aprendido decidiu. Nos outros ~82–87% o adulto diz "não sei".
  Instinto: 34% (atencioso) a 76% (relapso), quase tudo sono/cansaço e, no relapso, tempo sem cuidado.
- Combate (bots, sementes de validação): adaptativo 85,2% das decisões por regra com fator; tartaruga
  86,2% e contragolpe 69,3% caem na regra final `sempre`; aleatório 95,1% exploração. Regras que
  nunca disparam: tartaruga #1 e contragolpe #1, #3 (sombreadas por regras anteriores).
- **B2 recusa não existe**: o dono age direto no estado (`engine.aplicar_acao_usuario`); o pet não tem
  ação que bloqueie isso. Exigiria mudar `engine.py`/`state.py` e o espaço de ações. Não foi criado.
- **Parte B** (`PROTOCOLO_ARENA_V1_MEMORIA`, hash `be9aae5a833c…`, memória em todos os braços):
  run APROVADA; JSD entre braços 0,021415 bits com memória vs 0,020406 sem (artifacts/ e
  artifacts_ablacao/). Diferença de ~0,001 bit, sem IC, e a divergência dentro do braço também subiu
  (0,01496 vs 0,01306). Fatores de memória citados em 3,1–6,1% das decisões (mais no aleatório).

## Personalidade, obediência e desejo (2026-09-25, `docs/TAREFA_PERSONALIDADE_OBEDIENCIA.md`)

Sobre a memória por espaços (decisão do Matheus); pré-condição da bateria V2 dispensada. Módulos
`digilab/temperamento.py`, `vinculo.py`, `desejo.py`, `obediencia.py` (`MotorPersonalidade`,
subclasse do `MotorComFeedback`; `engine.py`, `CanalDeInteracao` e `combate_v2/` intactos). Protocolos
`arena-v1-personalidade` (`d986ff1b9308…`), `-neutro` (`edd9fdc25aae…`) e `-sem-obediencia`
(`e43305c4b17d…`), 10 ovos (101…1010), configs `experiments/configs/personalidade*.json`. Números de
`artifacts_v1_personalidade/{completa,neutro,sem_obediencia}/metrics.json` (seção `personalidade`).
Interpretações em `docs/REGISTRO_DESVIOS.md`. Tudo PROPOSTO.

- **O temperamento não engole o efeito do dono**: na run completa, a taxa de vitória por pet se decompõe
  em braço 16,9%, ovo 8,5%, resíduo 74,7%.
- Resultado central (atencioso × aleatório): completa 0,615 [0,450, 0,770] INCONCLUSIVO; temperamento
  neutro 0,655 [0,520, 0,790] ATENCIOSO_VENCE; obediência desligada 0,685 [0,525, 0,815] ATENCIOSO_VENCE.
  Temperamento e obediência somam ruído e empurram o central para inconclusivo.
- **Obediência (completa)**: atencioso 0,918, incoerente 0,897, relapso 0,818, aleatório 0,771;
  atencioso − aleatório +0,147 [0,092, 0,205]. **O vínculo não acompanha**: aleatório 0,607, atencioso
  0,539, relapso 0,500, incoerente 0,419; atencioso − aleatório −0,069 [−0,206, 0,074]. A obediência vem
  do conflito (o dono aleatório pede cuidado que não atende a necessidade urgente), não do vínculo; e o
  componente de atendimento premia o dono aleatório, que faz cuidado com frequência. Revisar o desenho
  do vínculo antes de usar como medida de coerência.
- Desejo (completa): cumprimento de vontade 0,445–0,545 por braço; fração do tempo com vontade ativa
  atencioso 0,552, incoerente 0,558, relapso 0,300, aleatório 0,237.
- Expressão (1.3 e 3.2, somente leitura): `expressar_temperamento` (tom por eixo marcante,
  |eixo| ≥ `limiar_extremo`, 0,2 desde a Parte 2 do adendo DF) e `expressar_desejo` (criança em diante distingue `preciso` ×
  `queria`); tabelas com marcador único e cobertura verificada na carga (`validar_tabelas_personalidade`).
- Equivalência: temperamento neutro + obediência desligada reproduz as vidas de
  `artifacts_v1_memoria_espacos/` byte a byte (teste). Parte 2 do adendo DF (emoção, extremos,
  habituação): feita, seção própria abaixo.

## Memória por espaços (2026-09-25, `docs/ADENDO_MEMORIA_EMOCAO_DF.md` Parte 1)

Protocolo `arena-v1-memoria-espacos` (hash `7dbe33a52ed6…`), política `bandit_espacos`,
`digilab/memoria_espacos.py`, `ConfigMemoriaEspacos` (tudo PROPOSTO). A B1 (`arena-v1-memoria`)
continua reproduzível. Interpretações em `docs/REGISTRO_DESVIOS.md`. Números de
`artifacts_v1_memoria_espacos/metrics.json` e `espacos.json` (`python experiments/memoria_espacos.py`).

- Run APROVADA; central INCONCLUSIVO (0,68, IC95 [0,50, 0,83], 5 sementes). JSD entre braços 0,02281
  bits com espaços × 0,02142 com a B1 × 0,02041 sem memória; dentro do braço 0,01629. Sem IC:
  diferenças da ordem de 0,001 bit, não conclusivas.
- A memória muda comportamento, mas pouco: 6,9% dos motivos citam uma memória (6,3% atencioso a 7,8%
  aleatório). Bronca e elogio dominam as citações.
- Ocupação média: curto 1,8 (atencioso) a 3,1 (aleatório) de 4; longo 1,3 a 1,9 de 2. O atencioso
  nunca tem `demora` na memória; relapso e aleatório têm `demora` em ~86–90% do tempo. `carinho`
  (intensidade 0,5) perde espaço para bronca/elogio (1,0) nos donos coerentes.
- Parte 2 feita: ver a seção seguinte. A web usa a memória por espaços nos pets v2.

## Emoção, extremos e habituação (2026-09-25, `docs/ADENDO_MEMORIA_EMOCAO_DF.md` Parte 2)

`digilab/emocao.py` (tabela categoria × temperamento → emoção, `ConfigEmocao`), `ConfigHabituacao`,
`MemoriaEspacos.eventos`/`fator_habituacao`, gancho `PoliticaBandit._peso_recompensa` (1,0 fora da
habituação), `expressar_emocao`/`expressar_carater`/`limiar_extremo` em `expressao.py`. Protocolos
`arena-v1-personalidade-habituacao` (`1cebd118a833…`) e `-sem-habituacao` (`ce36d15dd1e0…`), mesmos 10
ovos, configs `experiments/configs/personalidade_{habituacao,sem_habituacao}.json`. Números de
`artifacts_v1_habituacao/{com,sem}/metrics.json`. Interpretações em `docs/REGISTRO_DESVIOS.md`
(emoção só leitura; a modulação da memória pela valência existe desligada). Tudo PROPOSTO.

- **A habituação não muda o resultado central, mas encolhe a separação entre donos**: atencioso ×
  aleatório 0,615 [0,480, 0,750] com × 0,615 [0,450, 0,770] sem, os dois INCONCLUSIVO. JSD entre braços
  0,0212 com × 0,0262 sem (limiar 0,02; dentro do braço 0,0162 × 0,0195). Taxa do atencioso 0,563
  [0,538, 0,590] com × 0,596 [0,526, 0,660] sem; ICs sobrepostos, 10 ovos.
- Run "sem" = personalidade completa: as 80 vidas e políticas são byte a byte as de
  `artifacts_v1_personalidade/completa/` (emoção e extremos não mudam nada).
- Emoções (run com): aleatório e relapso são dominados por `demora` (3494 e 2426 eventos) e sentem
  raiva (52% e 42%); atencioso e incoerente recebem elogio e bronca e sentem orgulho/euforia (27%/27% e
  20%/20%) com raiva em 17% e 27%. O eixo que mais escolhe a emoção é rancor nos donos que deixam
  esperando e sensibilidade nos que dão feedback.
- **Extremos quase nunca calam**: com o limiar 0,2 e o sorteio uniforme em [−1, 1], os 10 ovos têm pelo
  menos um eixo descrito (1,0).
- Decomposição da taxa por pet (run com): braço 14,5%, ovo 13,2%, resíduo 72,4%.
