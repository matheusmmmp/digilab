# V2, de 2026-10-01 a 2026-10-07: o aprendiz, a bancada, as frutas e os cérebros

Seções movidas inteiras do CLAUDE.md da raiz na etapa 1 da rodada de saúde (`docs/TAREFA_V2_SAUDE.md`, 2026-10-13), da L0 ao
descritivo do platô, na ordem em que entraram. Cada seção cita a tarefa, o plano e os artefatos.

## V2, L0 — a política com lobos, aprendizado desligado (2026-10-01, `docs/TAREFA_V2_L0_LOBOS.md`) — G1 e G2 PASSAM

Nó L0 da fase 1b do `docs/PLANO_V2_PESQUISA.md` (H1). **Decisão do Matheus (2026-10-01): a V2 abandona o bandit**; `policies/bandit.py`
e subclasses ficam congelados só para reproduzir a v1. O aprendiz da V2 é `digilab/policies/lobos.py` (`PoliticaLobos`, sob o `Protocol`
`Politica` e o gancho `receber_acao_dono`), com `ConfigLobos` em `config.py` (4 campos, todos PROPOSTOS, sem fonte; registro de status em
`lobos.PARAMETROS_LOBOS_L0`, conferido por teste; fora de qualquer hash de protocolo). Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **Os lobos** são estágios internos com nome, não interfaces: percepção (1, `Estado.vetor`, tempo sem cuidado normalizado como no
  bandit: 10 entradas); memória e emoção (só contadores do que o dono fez; contribuição zero); impulsos (as regras do `PoliticaInstinto`,
  executadas pelo próprio código dele com uma rng-sonda: devolvem a regra e os candidatos, na ordem do instinto); decisão (490 pesos
  inteiros `w[regra][ação][entrada]`, escala S = 2¹⁰, iniciados no prior: os coeficientes literais do instinto vezes S; ativação
  linear sem `exp`/`log`; sorteio proporcional com uma chamada de `random()`, a conta de `random.choices(k=1)` passo a passo).
- **Por que fecha byte a byte:** S potência de dois torna `w/S` exato e devolve os mesmos floats que o instinto escreve, somados na
  mesma ordem (laço, não `sum()` compensado); regra determinista = um candidato = nenhuma rng; na fome moderada os pesos [1, 1] viram
  `2u < 1`, isto é, `u < 0,5`, a conta literal do instinto. A restrição de desenho da tarefa (seção 3) foi resolvida sem relaxar o gate.
- **Gates** (`tests/test_lobos.py`, 23 testes, ~4 s; sementes 101…505, só as dos testes): **G2 passa** nos dois motores (`MotorComFeedback`
  e `MotorPersonalidade`, 4 donos × 5 sementes × 3 dias, mais um orçamento baixo com o aleatório onde as 7 regras disparam): log, estado
  final, ações e o estado das rngs de ambiente, política e obediência iguais aos do instinto; decisão a decisão em 3000 observações
  aleatórias (todas as regras), ação e estado da rng iguais. **G1 passa**: replay pelo log bit a bit, inclusive o `estado_interno()`.
  Os pesos nunca mudam com o feedback do dono (vida do atencioso + todas as ações de dono); `aprendizado_ligado=True` falha alto (é o L1).
- **Motivo (base do G4):** `estado_interno()["motivos"]` guarda, por decisão, regra, candidatos, entradas, a contribuição de cada lobo por
  candidato, os pesos efetivos, o `u` sorteado e o lobo decisivo; a soma das contribuições é o peso sobre o qual se sorteia, então fecha
  com a decisão por construção (teste).
- **Não mudou:** `engine.py` (sha256 igual), o bandit, protocolos, runs da v1, `obediencia.py`, o jogo web. Sem versão de pet nova.
- **Aberto:** o instinto puro não roda no `MotorPersonalidade` (o embrulho repassa `receber_acao_dono`); o controle do G2 ali é o
  instinto com gancho vazio, definido no teste. L1 (ligar o aprendizado), L2/L3 (peças do DF), A1 e o porte para a web ficam para as
  tarefas seguintes.
- **GPU-ESTILO (2026-10-01, `docs/TAREFA_V2_GPU_ESTILO.md`, plano `docs/PLANO_ANALISE_V2_GPU_ESTILO.md`):** com o corpus em português
  (F0-CORPUS) o estilo da espécie volta a funcionar no gemma2:9b. **Medida A** (`experiments/medir_estilo_latino.py --saida
  estilo_portugues` → `artifacts_voz/estilo_portugues/`; 30 mensagens × 3 espécies, livre-v6, um modo só porque o filtro não tira
  nada): **0/30 rejeitadas** por letra não latina, 0 outros erros, 0 falas não latinas (antes, `estilo_latino/`: 1/30 com o filtro e
  26/30 sem). **Medida B, rodada 4 do comando** (`avaliar_fala.py --livre --comando --rodada 4` → `artifacts_fala_livre/comando/
  rodada4_estilo/`; livre-v8 **com** o estilo, sementes 20261501/1601/1701): **gate PASSA**: falsos positivos nas negativas 2/60
  (3,3%), imperativos 53/60 (88,3%), 2/180 saídas rejeitadas pelo parser (não por japonês), latência p50 6,3 s. Rodada 3 (sem estilo):
  0/60 e 51/60; rodada 2 (estilo com o corpus antigo): 160/180 rejeitadas. Erros que ficam: "limpar" (3/9), "levar_ao_banheiro"
  (4/6), e «não vou te dar bronca dessa vez» virou repreender 2 vezes. Nada mudou no prompt, verificador, corpus ou servidor.

## V2, F0 — vínculo B: previsibilidade + desejo (2026-10-01, `docs/PLANO_ANALISE_V2_VINCULO.md`) — GATE PASSA

Decisão do Matheus (2026-10-01): a **alternativa B** de `docs/V2_VINCULO_PROPOSTA.md` (o diagnóstico: o vínculo de hoje premia o dono
aleatório porque o atendimento e o desejo só amostram quem deixa o pet em falta). Plano registrado antes da run; tarefa
`docs/TAREFA_V2_F0_VINCULO_NOVO.md`. Números de `artifacts_v2_vinculo_novo/{calibracao,validacao}/resumo.json` e `mega_v10.json`.
- **Python:** `ConfigVinculoSituacao` (`ligada` False por padrão; `limiar_necessidade` 0,5 = o limiar do pedido; `limiar_energia` 0,25 = a
  regra de exaustão do instinto; noite por `ConfigPadrao.e_noite`), **à parte da `ConfigVinculo`**: o hash `d986ff1b9308…` dos protocolos da
  personalidade não muda. Registro `protocol.PARAMETROS_VINCULO_B` (nenhum referendado). Ligada: o pedido não abre (o atendimento sai) e a
  coerência agrupa o feedback por (ação do pet, situação em que ele a decidiu); desejo, ajustes diretos, pausa e teto da sombria iguais.
  `MotorPersonalidade(..., cfg_vinculo_situacao=)`, `fabricas_treino`/`simular_vida_treino` idem. Desligada: byte a byte (`tests/test_vinculo_b.py`).
- **Web: pets v10** (`VERSAO_PET = 10` = v9 + vínculo B; `CVB`, `Vinculo(porSituacao)` em `motor/vinculo.ts`); v1–v9 iguais (assinaturas e
  gabaritos). Paridade: `experiments/exportar_gabarito_vinculo.py` → `test/gabaritos/vinculo_python.json` → `test/vinculo.test.ts` (3256
  chamadas, modos hoje e B, ≤ 1e−12).
- **Run** (`experiments/run_vinculo_novo.py`: vidas novas do pipeline do treino, 5 braços × 5 sementes × {hoje, B}, 14 dias, orçamento igual,
  replay do disco conferido): calibração 3101…3505 (fumaça, +0,232 [+0,035; +0,359]); **validação 5101…5505, uma vez: GATE PASSA**,
  atencioso − aleatório no vínculo final **+0,171 [+0,046; +0,280]** com o B (por semente +0,068, +0,294, +0,278, −0,041, +0,255), contra
  −0,066 [−0,188; +0,017] com o vínculo de hoje nas mesmas sementes. Vínculo final B: atencioso 0,665, relapso 0,613, aleatório 0,494,
  incoerente 0,387, exigente 0,247 (hoje: 0,557, 0,472, 0,623, 0,431, 0,343). Exigente − atencioso −0,418 [−0,471; −0,361] (o forçar segue
  separando); incoerente − aleatório −0,107 [−0,177; −0,035]. Obediência B: atencioso 0,911, aleatório 0,699. Com 5 sementes o IC é curto.
- **Mega no jogo** (`web/app/test/medir_vinculo_mega.mjs --versao 10` → `mega_v10.json`; 6 vidas de 3 dias, 16/dia, limiar 0,4, **só relato: o
  limiar não muda**): atencioso 1, incoerente 2, relapso 3, aleatório 3 (pets v5 com o vínculo de hoje: 3/3/4/5). Em 48 interações o atencioso
  da web quase não dá feedback (1 e 4 nas duas vidas conferidas; o resto é chamado e limpeza), então o vínculo B dele é quase só desejo expirado: 0,13–0,37 no fim, máximo no
  Ultimate 0,23–0,48 (aleatório 0,36–0,53); 8 das 24 vidas nem chegam ao adulto em 3 dias nos v10 (qualificação por vitórias). No jogo
  curto o B não inverte o Mega; o que fazer com o limiar e com o desejo fica para o Matheus.
- Desvios e interpretações em `docs/REGISTRO_DESVIOS.md` (2026-10-01, vínculo B).

## V2, L1 — o lobo de decisão aprende (2026-10-01, `docs/TAREFA_V2_L1_DECISAO.md`, `docs/PLANO_ANALISE_V2_L1.md` rev. 2) — VALIDAÇÃO FEITA: G3, G4, G5 e G6 FALHAM (resultado negativo registrado)

Nó L1 da fase 1b (H1), com as decisões D1–D4 de `docs/DEFINICOES_V2.md`. Números de `artifacts_v2_l1/calibracao/` (sementes de
calibração 3101…3505; `escolha.json`, `varredura.jsonl`, `passo512_teto1024/{resultado,divergence,tarefa,legibilidade,deriva,
custo_gargalo,so_cuidado,norma_de_reacao}.json`, `educacao/resultado.json`; os `vidas/*.politica.json` ficam fora do git: 600 MB de
motivos, regeneráveis por replay dos `.jsonl`). **Validação (4101…4505) feita uma vez em 2026-10-01**, liberada pela decisão do Matheus
(PR #120: falhar não para a V2), sem reajuste: `artifacts_v2_l1/validacao/`, relatório em `docs/RESULTADO_V2_L1.md`; último item desta seção.
- **Código.** `PoliticaLobos` com `ConfigLobos(aprendizado_ligado=True)` (`CONFIG_LOBOS_APRENDIZ`): só o lobo de decisão muda, por
  `Δw = arred(f·S·passo·X_j·(S·1[a=a*] − P_a)/(S·S·W_a))` em inteiros (a direção do gradiente de `log p(a*)` da política proporcional
  com o sinal do dono no lugar da vantagem, COACH), janela de crédito da v1 (elogio/bronca na última decisão; chamado com latência),
  piso no peso efetivo e teto `|w − w0| ≤ teto`. Base `lobos.Aprendiz` compartilhada com o **controle sem lobos** `policies/camada_unica.py`
  (490 pesos por 7 fatias do dia, toda ação candidata, sem regra do instinto). `motivo.motivo_lobos` (impulso/prior × lobo de decisão,
  regra de honestidade do bandit). `metrics.acerto_na_tarefa`, `eficiencia_amostral`, `norma_de_reacao` (Finlay–Wilkinson).
  `fabricas_educacao`/`simular_vida_educacao` com `politica_fabrica` opcional (padrão intacto). L0 intacta (G1/G2 passam);
  `tests/test_lobos.py` 40 testes. Parâmetros novos em `ConfigLobos` (7, PROPOSTOS; `lobos.PARAMETROS_LOBOS_L1`); `passo` 512 e `teto`
  1024 vieram da calibração.
- **Calibração (grade 5 passos × 3 tetos, 39 min): não fechou.** Nenhum ponto passa o G6: com passo 32 a deriva ainda cresce linear
  (razão JSD dia 14 / dia 7 = 2,33) e de 64 em diante há pesos no teto. O ponto escolhido pela regra da seção 5 (menor razão) é
  **passo 512, teto 1024** (razão 1,19, mas 12 das 20 vidas com peso no teto). A divergência cresce com o passo (0,0014 → 0,034 bit) e
  o G4 do aprendido também (0,03 → 0,19); nenhum ponto chega perto dos alvos.
- **Gates no ponto escolhido (calibração, não validação):**
  - **G3 FALHA**: atencioso × relapso 0,029 bit [0,023; 0,038] (alvo 0,10; o bandit nas mesmas sementes dá 0,017; instinto 0,0). Na
    conta da v1: entre braços 0,035, dentro do braço 0,021 (v1: 0,020 e 0,013).
  - **G4 FALHA**: o lobo de decisão decide em 20,6% das decisões e tem fator em 18,8% [15,9; 21,6] (alvo 50%); bruto 70,5% (instinto
    51,6%; bandit 15,9% nos dois).
  - **G5**: (a) = G3, falha; **(c) passa**: ensino − acoplado +0,0196 bit [+0,0146; +0,0256] (o ensino diverge acima do cuidado); (b)
    insuficiente (2 sementes sem lesão nem morte; 1 morte, 6 pets com lesão; leitura com todos 0,102).
  - **G6 FALHA** pelo teto (12 vidas); razão 1,19 passa.
- **G3-T (sem gate): o aprendiz aprende a tarefa ensinada.** Acerto nos 7 últimos dias, atencioso: lobos **0,719** (instinto 0,574,
  bandit 0,598, teto do dono 1,0); relapso 0,529 (0,514); aleatório 0,624 (0,640); incoerente 0,481 (0,572). Eficiência amostral:
  40 sinais em média (de 138 na vida); o bandit chega à metade com 19, mas sobe pouco. O acoplado só cuidado cai a 0,467 (o canal do
  chamado ensina a chamar mais).
- **Controle sem lobos (D2):** diverge mais (G3 0,134 [0,105; 0,163]) e é mais "legível" pelo aprendido (0,284 × 0,188: lobos − controle
  −0,096 [−0,126; −0,064]): **a modularidade não compra legibilidade** por esta medida. **Custo do gargalo** a favor dos lobos: +0,386
  [+0,361; +0,413] de acerto (o controle, sem regra de sono, cuida mal de si).
- **Norma de reação (3.2):** Δα ensino − só cuidado +0,228 [+0,196; +0,260] no acerto e +0,020 na JSD ao instinto; **a inclinação é
  mal condicionada**: o índice do ambiente tem amplitude 0,007 (os 4 ambientes mal mudam a média), IC de Δβ [−3,5; +12,3].
- **Acoplado (D4):** 81–94 interações contra 224 (os sinais são 60% do atencioso); JSD acoplado × ensino 0,027; a variante sem carinho sai
  igual (o atencioso quase não acaricia).
- **Leitura, antes da validação:** o aprendiz da V2 aprende o que o dono ensina (G3-T sobe 0,145 sobre o instinto) e isso é ensino, não
  cuidado (G5c), mas o que se aprende quase não muda a distribuição de ações nas sondas (G3) nem decide muitas decisões (G4): o impulso
  (as regras do instinto) decide 79% das vezes. Os alvos 0,10 bit e 50% foram escritos antes de se ver o aprendiz; a decisão de
  mantê-los, relaxá-los ou declarar resultado negativo é do referendo. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **Validação (sementes 4101…4505, ponto 512/1024, 5 min; `docs/RESULTADO_V2_L1.md`):** **G3 FALHA** 0,041 bit [0,026; 0,062]
  (bandit 0,012; calibração 0,029); **G4 FALHA** 0,182 [0,145; 0,236] (bruto 0,703); **G5 FALHA**: (a) = G3; (c) ensino − acoplado
  +0,0099 [−0,010; +0,025] (na calibração passava); (b) 1 semente limpa, insuficiente; **G6 FALHA** pelo teto (12 de 20 vidas; razão
  1,45 passa). **G3-T**: atencioso 0,663 (instinto 0,577, bandit 0,607, controle 0,349, acoplado 0,446); incoerente 0,520 abaixo do
  instinto 0,586. Controle sem lobos: G3 0,113, G4 aprendido 0,283 (lobos − controle −0,101 [−0,136; −0,049]); custo do gargalo +0,314
  [+0,177; +0,422]. Norma de reação: Δα ensino − cuidado +0,238 [+0,211; +0,258]; inclinação mal condicionada. **Leitura:** resultado
  negativo para H1 com este aprendiz: o ensino chega (G3-T, Δα), mas o instinto decide 80% das decisões e o teto 1·S limita o resto; o
  controle sem lobos aprende mais e cuida pior. Os alvos e o ponto ficam como estão (nada se ajusta olhando a validação); a revisão
  das validações iniciais é decisão do Matheus.

## V2, BANCADA — o orquestrador dos braços da pergunta maior (2026-10-01, `docs/TAREFA_V2_BANCADA.md`) — GATES PASSAM

Infraestrutura, não pesquisa: nenhuma run com faixa reservada, nenhum número de resultado. `experiments/bancada_v2.py` monta toda vida dos
braços da pergunta maior (`docs/ARQUITETURA_V2_VALIDACAO.md`, seção 6) do mesmo jeito, para P0–P3 continuarem comparáveis quando o N3 e
o N5 chegarem. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **Vida = (genoma, mundo, dono, braço, semente)** (`EspecVida`, `Bancada.vida`): rngs de ambiente e de política do motor pela semente
  (engine intocado); a do dono derivada de (semente, nome do dono), igual em todos os braços; genoma `None` = `MotorComFeedback` (como a
  L1), um inteiro g = temperamento de g no `MotorPersonalidade`, separado da semente do ambiente. Mundo: só `padrao`; os outros levantam
  `NotImplementedError` (N4 e a rodada 4).
- **Fonte do sinal como campo do braço** (`BRACOS`, `PoliticaDoBraco`): o cérebro é sempre `PoliticaLobos` com o mesmo prior e a mesma
  `ConfigLobos` (`CONFIG_LOBOS_APRENDIZ`, passo 512, teto 1024); só muda o que passa por `receber_acao_dono`. `dono` (P3) repassa tudo:
  a vida é byte a byte a da L1. `nenhuma` (P0) não repassa nada e usa o aprendiz com o aprendizado desligado (o prior fixo), porque um
  aprendiz ligado sem sinal ainda aprende: o chamado expira por dentro (`Aprendiz._expirar`) e vira sinal negativo. `consequencia`
  (P1) e `informacao` (P2 certa, P2e errada) levantam `NotImplementedError` com o nó (N3, N5). Só o cérebro `lobos` (outros: N11).
- **Modo acoplado** (`Bancada.acoplar`, filtros `nenhum`, `sem_sinais`, `sem_sinais_sem_carinho`): o registro de uma vida, sem as ações
  do filtro, rejogado com o cérebro de outro braço (malha aberta); generaliza `log_so_cuidado`/`vidas_acopladas` de `run_v2_l1.py`, que
  ficam como estão.
- **Medidas** (só `digilab/metrics.py`): `desempenho_no_ambiente` (tempo fora de privação pela regra `Estado.em_privacao` e saúde média,
  amostrados em cada decisão, a cada 15 ticks), o acerto na tarefa do dono (`acerto_na_tarefa`, igual ao `curva_tarefa` da L1),
  `custo_da_plasticidade` (JSD ao prior herdado no fim de cada dia e o tempo até a metade do caminho pela `eficiencia_amostral`, com o
  piso no acerto do P0 da mesma célula; conta só os sinais que chegaram ao aprendiz) e `tabela_braco_condicao` (bootstrap por célula,
  grade completa ou erro). `rodar` grava vidas, `medidas.json`, `tabelas.json` (por dono e medida) e `meta.json`.
- **Gates** (`tests/test_bancada_v2.py`, 31 testes, ~16 s; sementes 101…505): **P0 = instinto byte a byte** pela bancada (os G2 da L0:
  4 donos × 5 sementes nos dois motores, mais as 7 regras com o orçamento baixo); **o acoplado reproduz** (no próprio braço sem filtro é a
  vida de origem; o P3 no próprio registro sem os sinais é o "só cuidado" da L1, com e sem carinho; o P0 no registro do P3 sem os sinais
  tem como log o da origem com os sinais retirados, evento a evento, e é a vida do instinto nesse registro); **G1**: toda vida e todo
  acoplado rejogados do texto do log bit a bit, e a divergência falha alto. Sementes fora de 101…505 exigem o campo `plano` com um
  arquivo do repositório (`SementeSemPlano`).
- **Fumaça** (`experiments/configs/bancada/fumaca.json`, NÃO canônica, `--saida <pasta>`): 80 vidas em ~26 s; sem artefato no repositório.
- **Não mudou:** `engine.py` (sha256 igual), `lobos.py`, `run_v2_l1.py`, o bandit, runs da v1, a web.

## V2, A1 — a bola, primeiro objeto do mundo com consequência (2026-10-01, `docs/TAREFA_V2_A1_BOLA_IMPL.md`, `docs/PLANO_ANALISE_V2_A1.md`) — VALIDAÇÃO: 1a-PET PASSA, CUIDADO CONTROLADO FALHA

Nó N2 de `docs/ARQUITETURA_V2_VALIDACAO.md`; desenho `docs/V2_A1_BOLA_DESENHO.md` (opção A, aprovado no #113). **Sem aprendizado**: a bola
entra pelo instinto, atrás de chave; a regra `bola_no_cenario` dos lobos é do chat B (A1 + L1). Números de `artifacts_v2_a1/calibracao/`
(`resultado.json`, `varredura.jsonl`, `pet.json`, `sembola.json`, `so_cuidado.json`; sementes 6101…6505; as vidas dos 27 pontos da grade
ficam fora do git, regeneráveis).
- **Código.** `digilab/ambiente.py`: `MotorAmbiente` (subclasse do `MotorEducacao`; a bola `{tick_posta, prazo}` fora do `Estado`; pôr e
  tirar não são contato; `brincar` com bola no cenário = humor + `ganho_humor_bola` e a bola some; expira no prazo; **nenhuma rng**),
  `PoliticaInstintoBola` (no tempo livre `brincar` ganha `w_bola × bola`, mesma chamada de `rng.choices`; regra `bola_no_cenario`),
  `reproduzir_ambiente`, `DonoComBola`. `AcaoUsuario.POR_BOLA`/`TIRAR_BOLA` no fim do enum (`ACOES_BOLA`; `ACOES_V1` e `AcaoPet`
  intactos); `Observacao.bola` (campo com padrão 0,0; só o `MotorAmbiente` injeta); `PoliticaInstinto._pesos_tempo_livre` (extração, os
  mesmos literais na mesma ordem); `ConfigBola` (`ligada` False; registro `protocol.PARAMETROS_BOLA_A1`, fora de todo hash, nenhum
  referendado); `metrics.resposta_a_bola`, `privacao_nas_decisoes`; `experiments/run_v2_a1.py`, `configs/v2_a1/`. `engine.py`, bandit,
  `policies/lobos.py` e web intactos.
- **G1 e G2 passam** (`tests/test_ambiente.py`, 26 testes): replay bit a bit; desligado = `MotorEducacao` numa vida da V3 com lutas;
  desligado com o instinto da bola = `MotorComFeedback` com o `PoliticaInstinto` (4 donos × 3 sementes); ligado sem bola no log =
  desligado. O orquestrador confere o replay de toda vida.
- **Calibração (27 pontos, 5 min): não fechou.** Δp cresce com `w_bola` (+0,02 a +0,26); a privação sobe com a bola **em todos os
  pontos** (+0,016 a +0,025), então nenhum passa a regra. Ponto escolhido pela regra de reserva (maior limite inferior de Δp):
  **duração 120 min, ganho 0,15, `w_bola` 6** (agora os padrões da `ConfigBola`).
  - **1a-pet passa na calibração:** Δp = p(brincar | bola) − p(brincar | sem bola) no tempo livre **+0,260 [+0,216; +0,317]**; com a
    bola que o instinto não vê, +0,025 [−0,061; +0,121]. p(brincar | bola) 0,607.
  - **Cuidado controlado falha:** privação bola − sem bola +0,019 [+0,006; +0,032]; mortes 0; humor −0,008 [−0,020; +0,006].
    **Causa: o dono aleatório**, que sorteia `por_bola` entre as ações e, com o orçamento fixo, alimenta e limpa menos (privação 0,355 →
    0,433; igual sem o pet ver a bola, 0,427). Atencioso e incoerente: privação 0 nos dois braços, e a bola (56 por vida) desloca
    elogios e broncas (elogios 87,6 → 58,8 no atencioso), não cuidado. Relapso: 1 bola em 5 vidas (nas visitas ele sempre tem cuidado a fazer).
  - Acoplado só cuidado (D4): 78–100 interações, privação 0; a variante sem carinho sai igual (o atencioso não acaricia).
    Sensibilidade `bolas_por_dia` 2 e 8: Δp +0,222 e +0,269, privação +0,019 nas duas.
- **Validação (7101…7505, uma vez; `artifacts_v2_a1/validacao/`, relatório `docs/RESULTADO_V2_A1.md`):** repete a calibração.
  **1a-pet PASSA**: Δp **+0,310 [+0,245; +0,375]** (bola que o instinto não vê: +0,036 [−0,025; +0,107]). **Cuidado controlado
  FALHA**: privação +0,017 [+0,009; +0,028], mortes 0; de novo só o aleatório (0,266 → 0,333; 0,334 sem o pet ver a bola). Humor
  −0,024 [−0,042; −0,008]: a bola tira elogios e carinhos. Nos coerentes a bola desloca o ensino (atencioso: elogios 93,0 → 61,4,
  broncas 46,0 → 20,0). Resultado registrado; a V2 segue (decisão de 2026-10-01). Decisões B1–B3 para o Matheus no relatório.
  Interpretações em `docs/REGISTRO_DESVIOS.md`.

## V2, N3 — a consequência da própria ação como sinal, braço P1 (2026-10-04, `docs/TAREFA_V2_N3_CONSEQUENCIA.md`, `docs/PLANO_ANALISE_V2_N3.md`) — VALIDAÇÃO FEITA: G-P1 E G6 FALHAM (resultado negativo registrado)

Nó N3 de `docs/ROADMAP_V2.md`; braço P1 da pergunta maior. Plano registrado antes de qualquer run (primeiro commit do branch), com a
janela de crédito decidida. Números de `artifacts_v2_n3/calibracao/` (sementes 8101…8505; `escolha.json`, `varredura.jsonl`,
`ganho<g>/resultado.json` e, da bancada, `ganho<g>/{medidas,tabelas,meta}.json` e `vidas/*.jsonl`; os `vidas/*.politica.json` ficam fora
do git, ~700 MB, regeneráveis por replay). Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **O sinal.** `lobos.sinal_homeostatico`: D = Σ(S − arred(h·S))² sobre fome, higiene e energia (ponto de ajuste 1,0; humor e saúde fora),
  f_S = div_arred(ganho · (D_antes − D_depois), S), em inteiros (Keramati e Gutkin, `10.7554/elife.04811`; expoente 2 sem raiz, escolha
  do projeto). **Janela imediata**: `observacao → observacao_seguinte` da mesma decisão, medida pelo motor antes do tempo e do dono:
  comer dá sinal positivo, brincar e explorar negativo (gastam energia), o resto zero. A consequência atrasada fica declarada, sem run.
- **O código.** `Aprendiz.observar_consequencia` (o gancho: credita f_S à decisão pela mesma `atualizar_pesos` da L1, sem relógio de
  cuidado nem chamados pendentes); `PoliticaDoBraco` com a fonte `consequencia` (nada do dono chega: nem sinal nem chamado);
  `Bancada.cfg_consequencia` e a chave `consequencia` do config da bancada; `ConfigConsequencia` (drives, ganho; PROPOSTOS,
  `lobos.PARAMETROS_CONSEQUENCIA_N3`); `experiments/run_v2_n3.py` monta os gates a partir das medidas da bancada. `engine.py`, `AcaoPet`,
  o bandit, a L0 e a L1 (o P3 continua byte a byte) e a web intactos. Testes: `tests/test_n3_consequencia.py` (G2: o P1 com ganho 0 ou
  com o aprendizado desligado é o P0 byte a byte, 4 donos × 5 sementes; G1; o sinal por ação; o mesmo f_S pela via do dono dá os mesmos
  pesos; nada do dono chega ao P1; o acoplado P1 ← P0 recebe o mesmo cuidado nos mesmos ticks).
- **Calibração (grade do ganho {4, 8, 16, 32, 64}, 38 min): não fechou.** Nenhum ganho passa o G6: 18 a 20 das 20 vidas prendem peso no
  teto (1·S, o da L1) em todos os pontos, porque o sinal tem sempre o mesmo sentido (brincar e explorar sempre gastam energia). Pela regra
  de reserva da seção 6 (menos vidas no teto), o escolhido é o **ganho 4** (agora o padrão da `ConfigConsequencia`).
- **No ganho 4 (calibração, não validação):** **G-P1 PASSA**: privação P0 − P1 **+0,0051 [+0,0008; +0,0091]**; vem toda do dono aleatório
  (+0,021 [+0,005; +0,034]); atencioso e incoerente sem privação nos dois braços; relapso −0,0001. **Sem mortes novas** (por construção:
  o mundo `padrao` não tem morte); saúde P1 − P0 +0,0046 [+0,0017; +0,0075]. **G6 FALHA** (18 vidas no teto; razão da deriva 1,68).
  Com o mesmo cuidado (acoplado P1 ← P0) a redução é a mesma, +0,0051 [+0,0003; +0,0092]: o efeito é das ações do próprio pet, não de um
  cuidado diferente do dono. Os outros ganhos também reduzem a privação (+0,006 a +0,011; o 32 com IC cruzando zero).
- **O que o P1 aprende** (a previsão do plano): na fome moderada come 91% das vezes (P0 47%); no tempo livre troca brincar e explorar
  (35% e 28% → 10% e 15%) por ocioso e chamar (28% e 9% → 48% e 27%). O acerto na tarefa do dono **cai** (0,58 → 0,43): o dono elogia
  brincar e explorar com energia, e o P1 aprendeu a evitá-los. G4 do aprendido 0,188 [0,179; 0,196] (bruto 0,671).
- **Validação (sementes 9101…9505, ganho 4, uma vez, 7 min; `artifacts_v2_n3/validacao/`, relatório `docs/RESULTADO_V2_N3.md`):**
  **G-P1 FALHA**: privação P0 − P1 **+0,0008 [−0,0067; +0,0077]** (por semente de −0,013 a +0,011; aleatório −0,002, relapso +0,005;
  atencioso e incoerente sem privação); com o mesmo cuidado (P1 ← P0) +0,0007 [−0,0067; +0,0073]. **G6 FALHA** (20 de 20 vidas no teto;
  razão 1,78). Sem mortes novas por construção; saúde P1 − P0 +0,003 [−0,005; +0,010]. O P1 aprende o mesmo que na calibração (come 94%
  na fome moderada; ocioso 47% e chamar 27% no tempo livre) e o acerto na tarefa do dono cai (0,593 → 0,444). **Leitura:** resultado
  negativo para o P1 no mundo `padrao`: a consequência imediata ensina a comer e a poupar energia, mas a privação depende do cuidado do
  dono, e a redução da calibração não se repetiu. Nada foi reajustado; a V2 segue (decisão de 2026-10-01).

## V2, BANCADA-MUNDOS — o mundo da bola e o contrato das condições (2026-10-04, `docs/TAREFA_V2_BANCADA_MUNDOS.md`) — GATES PASSAM

Infraestrutura, sem run de pesquisa nem número de resultado; só as sementes dos testes. O campo **mundo** da bancada
(`experiments/bancada_v2.py`) monta as condições da pergunta maior. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **Mundos** (`MUNDOS`, `mundo_de`): `padrao` (o de sempre); **`bola`**, a bola da A1 (`MotorAmbiente`, `CONFIG_BOLA_LIGADA`, obediência,
  educação e lesões desligadas, espécie brasa, temperamento neutro ou do genoma) com as decisões de 2026-10-01: **B1**, os donos são os
  da v1 e o aleatório não sorteia `por_bola` (nem põe bola por outra regra); **B2**, a bola entra por uma regra do mundo **fora do
  orçamento** (`RegraBola` + `simular_vida_mundo`: a regra dos coerentes do `DonoComBola` sem o limite do passo; o relapso só nas visitas,
  B3); e **`bola_a1`**, a bola exatamente como a A1 rodou (`DonoComBola`, o aleatório sorteando, a bola no orçamento), só para reproduzir a
  A1. `ambiente.py` e os donos da A1 não mudaram.
- **Contrato das condições** (`CONDICOES`): `casado` existe (os três mundos de hoje o realizam); `descasado` e `mutavel` levantam
  `NotImplementedError` com o que precisam do N4 (a preferência inata por fruta no genoma, o efeito real de cada fruta contrário a ela,
  com o efeito ruim no humor; no mutável, a troca do efeito num tick, gravada no registro). A tabela braço × condição usa a coluna
  `condicao/mundo` (hoje `casado/padrao`, `casado/bola`): dois mundos da mesma condição nunca dividem uma célula.
- **Cérebros:** `lobos` (todos os braços) e **`instinto`**, só no P0: no mundo da bola é o `PoliticaInstintoBola`, a predisposição
  herdada que vê a bola. Os lobos ainda não veem a bola (a regra `bola_no_cenario` deles é do chat B): no mundo da bola o P0 com lobos é
  o braço "bolacega" da A1.
- **Acoplado com mundo:** o registro é rejogado no mesmo mundo, e os **eventos do mundo** (`EVENTOS_DO_MUNDO`: pôr e tirar a bola; as
  ofertas de fruta entram aqui no N4) nunca saem; um filtro que os tirasse falha alto. O "só cuidado" da A1, que tirava a bola, fica em
  `run_v2_a1.py`. Medidas no mundo da bola: `metrics.resposta_a_bola` e a contagem da bola, ao lado das de sempre; `interacoes` conta só
  as ações do dono, `eventos_mundo` as da bola.
- **Gates** (`tests/test_bancada_mundos.py`, 22 testes, ~20 s): **`bola_a1` = a vida da A1 byte a byte** (4 donos × 2 sementes; com o
  instinto é o braço "bola", com os lobos o "bolacega"); **B1 e B2**: em 4 donos × 5 sementes o aleatório nunca põe bola, o orçamento é
  só de ações do dono e a bola vem por fora (o aleatório no mundo da bola tem o log, as ações e as rngs do mundo padrão; o laço do mundo
  sem eventos é o `simular_vida`); **G1** de toda vida e acoplado nos mundos novos; **acoplado com mundo** reproduz a vida de origem no
  próprio braço e, no P0 sem os sinais, guarda toda bola no mesmo tick e é o instinto cego à bola nesse registro.
  `tests/test_bancada_v2.py` segue passando (a coluna da tabela virou `casado/padrao`).
- **Fumaça** (`experiments/configs/bancada/fumaca.json`, NÃO canônica, agora com `padrao` e `bola`): 160 vidas em ~52 s; sem artefato.
- **Não mudou:** `engine.py`, `lobos.py`, `ambiente.py`, os donos e as runs da A1, `run_v2_l1.py`, a web.

## V2, N4 — frutas no mundo, sem aprendizado de política (2026-10-04, `docs/TAREFA_V2_N4_FRUTAS.md`, `docs/PLANO_ANALISE_V2_N4.md`) — VALIDAÇÃO: G-F7 PASSA, G-SEP E G-SSE FALHAM

Nó N4 do `docs/ROADMAP_V2.md` (a condição **descasado** da pergunta maior), com as definições F1–F11 de `docs/DEFINICOES_FRUTAS_V2.md` e as
decisões da bola B1 e B2. **O aprendiz da política fica desligado**: a fruta entra pelo instinto, atrás de chave; a regra das frutas nos
lobos é do chat B. Números de `artifacts_v2_n4/calibracao/` (`resultado.json`, `varredura.jsonl`, `vidas.json`, `so_cuidado.json`;
sementes 10101…10505; as vidas dos 18 pontos da grade ficam fora do git, regeneráveis).
- **Código.** `digilab/frutas.py`: `MotorFrutas` (subclasse do `MotorAmbiente`, que não muda; frutas `{fruta: prazo}` fora do `Estado`;
  oferecer não é contato), `PoliticaInstintoFrutas` (no tempo livre `comer` entra como candidato com peso `w_fruta × fruta`, a mesma
  chamada de `rng.choices`; regra `fruta_no_cenario`), a **sub-decisão de comer** (o pet escolhe a fruta proporcional ao **incentivo**,
  na `rng_fruta`, uma chamada em toda decisão `comer`), os **dois registros** por fruta (`incentivo`, `avaliacao`; F1), a **saciedade
  específica** (a avaliação de uma fruta cai com o consumo recente dela, sem a fome), o **genoma** (`neofobia`, `preferencia_inata`, rng
  `frutas-ovo`, fora do `Temperamento`; F4, F5), o efeito no corpo separado do gosto (nutrição igual em todas; no mundo **descasado** a
  preferida de nascença tem efeito ruim no **humor**, F6), `OfertasFrutas` (cronograma igual para os quatro donos, 9h/12h/15h/18h, rotação
  de 7 conjuntos, 4 com duas frutas ou mais) e `simular_vida_frutas` (ofertas **fora do orçamento** e do sorteio do aleatório: B1, B2).
  `AcaoUsuario.OFERECER_FRUTA_A/B/C` no fim do enum (`ACOES_FRUTAS`, `FRUTAS`, `fruta_de`, `oferta_de`); `Observacao.fruta` (padrão 0,0);
  `ConfigFrutas` (`ligada` False; registro `protocol.PARAMETROS_FRUTAS_N4`, nenhum referendado); `metrics.comer_por_incentivo`,
  `escolha_por_incentivo`, `saciedade_especifica`; `experiments/run_v2_n4.py`, `configs/v2_n4/`. `engine.py`, `AcaoPet`, bandit,
  `lobos.py`, `ambiente.py`, `heranca.py` e web intactos.
- **G1 e G2 passam** (`tests/test_frutas.py`, 31 testes): replay bit a bit; desligado = `MotorEducacao` numa vida da V3 com lutas;
  desligado com o instinto das frutas = `MotorComFeedback` com o `PoliticaInstinto`; ligado sem oferta = desligado; a vida da validação da
  A1 com a bola, rejogada pelo `MotorFrutas` com as frutas desligadas, sai igual à do `MotorAmbiente`.
- **Calibração (18 pontos, 4 min): não fechou.** Nenhum ponto chega à faixa de p(comer | fruta no cenário) [0,30; 0,80] (máximo 0,19,
  com `w_fruta` 6) e o G-SEP(ii) falha em 15 dos 18. Ponto pela regra de reserva (maior limite inferior do G-SEP(i)): **`w_fruta` 6,
  `k_saciedade` 1,0, duração 120** (agora os padrões da `ConfigFrutas`).
  - **G-SEP(i) passa** (a escolha de comer não é função só da fome): p(comer | incentivo alto) − p(comer | baixo), mesma faixa de fome,
    **+0,079 [+0,040; +0,140]**; **G-SEP(ii) falha** (qual fruta): +0,121 [−0,060; +0,304], com 0 a 27 escolhas entre duas frutas ou mais
    por vida. **G-SSE passa**: β_recente −0,769 [−0,873; −0,689], β_fome −0,024 [−0,113; +0,047]. **G-F7 passa**: saúde frutas −
    acoplado +0,014 [−0,004; +0,033], mortes 0 e 0.
  - **Canal de cuidado:** frutas − sem frutas na privação −0,003 [−0,007; +0,002], humor −0,003, saúde +0,005 (ICs contêm 0).
  - **Descasado:** o pet come a fruta que faz mal em 43% dos consumos [36%; 53%] (três frutas); humor descasado − iguais −0,009
    [−0,018; +0,002]. Sem aprendizado pela consequência (N3) nada o afasta dela, como esperado.
  - **A neofobia segura o comer:** o genoma é o mesmo para os quatro donos de uma semente; com neofobia 0,96 (semente 10101) o primeiro
    contato com uma fruta vem no 3º ao 8º dia e p(comer) fica em 0,05, contra 0,30 na semente de neofobia baixa.
- **Validação (11101…11505, uma vez; `artifacts_v2_n4/validacao/`, relatório `docs/RESULTADO_V2_N4.md`):** **G-SEP FALHA** pela (ii):
  (i) +0,094 [+0,049; +0,136] passa, (ii) +0,110 [−0,007; +0,213] falha por 0,007 (4 a 24 escolhas entre frutas por vida). **G-SSE
  FALHA** pelo β_fome −0,070 [−0,159; −0,014] (β_recente −0,778 [−0,901; −0,635] passa): a avaliação não lê a fome (código e teste);
  a regressão do plano não tem a preferência inata e o β_fome capta a diferença de preferência entre frutas. **G-F7 PASSA**: −0,004
  [−0,008; 0,000], mortes 0 e 0. Descritivos: custo do descasado no humor −0,023 [−0,030; −0,014]; a fruta que faz mal em 39% dos
  consumos; as frutas alimentam (privação −0,011 [−0,021; −0,003]). Resultado registrado; a V2 segue. Decisões N1–N4 no relatório.
  Interpretações em `docs/REGISTRO_DESVIOS.md`.

## V2, BANCADA-FRUTAS — os mundos das frutas e as unidades derivadas (2026-10-04, `docs/TAREFA_V2_BANCADA_FRUTAS.md`) — GATES PASSAM

Infraestrutura, sem run de pesquisa nem número de resultado; só as sementes dos testes. Cumpre o contrato das condições do #137 e as
seções 2, 4.1 e 8.1 de `docs/PLANO_ANALISE_V2_EXPERIMENTO_MAIOR.md` (E1, E3). Só `experiments/bancada_v2.py` e `digilab/metrics.py`
mudaram; `frutas.py`, `ambiente.py`, `lobos.py` e `engine.py` não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **Mundos das frutas** (`casado_frutas`, `descasado`, `mutavel`; condições `casado`, `descasado`, `mutavel`, que agora existem as três):
  `MotorFrutasMundo` (subclasse do `MotorFrutas`) com obediência, educação, lesões e bola desligadas, espécie brasa e o genoma das frutas
  do genoma da vida (ou da semente). **As mesmas ofertas nos três mundos e em todos os braços:** `CalendarioFrutas`, nos horários do N4,
  todo dia, a rotação do N4 começando num índice derivado da semente, sem olhar o estado do pet (oferece com ele dormindo; a fruta fica
  até o prazo), fora do orçamento e do sorteio do aleatório (B1, B2, pelo canal do mundo de `simular_vida_mundo`).
- **O efeito por condição** (`efeitos_da_condicao`; F6: no humor): no casado a fruta de **maior** preferência inata faz bem
  (−`efeito_humor_ruim`) e a de **menor** faz mal (`efeito_humor_ruim`); no descasado, o contrário; a do meio fica neutra. Casado e
  descasado diferem **só no sinal**, e os dois têm uma fruta boa e uma ruim. O **mutável** começa casado e troca para o descasado na
  metade da vida (`Bancada.tick_troca` = fim do dia `dias // 2`: dia 7 numa vida de 14); a troca fica em `MotorFrutasMundo.troca`
  (tick e os efeitos antes e depois) e no efeito de cada consumo, e o replay a refaz.
- **Medida da predição:** `metrics.taxa_fruta_ruim` (fração dos consumos com o efeito vigente negativo, por janela) nas medidas da
  bancada, com as janelas `inicio`, `final`, `antes_da_troca` e `depois_da_troca` (só no mutável) e uma por dia; `None` quando a janela
  não tem consumo. `humor_medio` (`metrics.privacao_nas_decisoes`) entrou nas medidas e na tabela de todos os mundos.
- **Unidades derivadas (E3):** `unidades_derivadas(bases, K)`: semente = `derivar_semente("experimento-maior", b, k)` e genoma =
  `derivar_semente("experimento-maior-genoma", b, k)`, k = 0…K−1; o campo `unidades` da config (`{"bases", "k"}`, no lugar de `sementes`;
  bases fora das dos testes pedem o `plano`). `BASES_EXPERIMENTO_MAIOR` (14101…14505, 15101…15505) e `FAIXAS_RESERVADAS` (as faixas do
  repositório, com a fonte).
- **Cérebros:** o `instinto` (só P0) nos mundos das frutas é o `PoliticaInstintoFrutas`, que vê as frutas. **Os lobos ainda não veem
  as frutas** (a regra é do chat B, `docs/TAREFA_V2_LOBOS_MUNDO.md`): o P0 com lobos é o instinto sem o candidato da fruta e, nos testes
  curtos, não come fruta nenhuma. P1 e P3 rodam, mas cegos às frutas até lá.
- **Gates** (`tests/test_bancada_frutas.py`, 17 testes, ~25 s): **as mesmas ofertas, só o sinal muda** (4 donos × 2 sementes, sem e com
  genoma: as ofertas são iguais nos três mundos, nos cérebros e nos braços; os efeitos de casado e descasado são opostos fruta a fruta);
  **a troca do mutável** está no registro no tick previsto, antes dela o mutável é o casado (eventos e consumos), depois os consumos têm o
  efeito do descasado, e o replay a refaz; **G1** de toda vida e acoplado (P0, P1, P3; com e sem genoma); **acoplado guarda as ofertas**;
  **unidades derivadas** seguem a regra, não colidem entre si nem entre calibração e validação, nem com as faixas reservadas, nem com
  nenhuma semente das configs de `experiments/configs/`. O `MotorFrutasMundo` com o efeito dado ao `MotorFrutas` é a mesma vida (só o
  efeito muda). `tests/test_bancada_mundos.py` e `tests/test_bancada_v2.py` seguem passando (o contrato agora tem as três condições).
- **Fumaça** (`experiments/configs/bancada/fumaca_frutas.json`, NÃO canônica: unidades derivadas das sementes dos testes, `padrao` e os
  três mundos das frutas, P0, P1 e P3): 80 vidas em ~32 s; sem artefato.

## V2, LOBOS-MUNDO — os lobos veem a bola e as frutas e escolhem a fruta; E2 no sinal do P1 (2026-10-04, `docs/TAREFA_V2_LOBOS_MUNDO.md`) — GATES PASSAM

Infraestrutura do aprendiz, sem run de pesquisa nem número de resultado; só as sementes dos testes (11, 22, 33). Achado 1 da rodada 4
(`docs/V2_RODADA_4.md`): sem isto o P1, o P2 e o P3 ficam cegos ao descasado. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **Como liga:** `PoliticaLobos(cfg, cfg_lobos, cfg_bola=None, cfg_frutas=None)`. Os lobos veem o mundo só com a chave dele ligada (como o
  instinto). Sem nenhuma (o padrão), nada muda: as formas, as vidas e o estado interno de antes, byte a byte (teste).
- **Percepção:** mais duas entradas no fim, `bola` e `fruta` (o que o `MotorAmbiente`/`MotorFrutas` já injetam na `Observacao`): 12.
- **Impulsos:** a sonda roda o `PoliticaInstintoFrutas` (a bola mais as frutas), então `bola_no_cenario` e `fruta_no_cenario` são regras
  dos lobos (9). Prior delas = o do tempo livre, com `w_bola` na entrada `bola` de brincar e, na das frutas, comer com `w_fruta` na entrada
  `fruta`, no fim dos candidatos como no instinto. O coeficiente vezes S tem de ser inteiro (6,0 × 1024 é), senão falha alto.
- **Sub-decisão da fruta:** um peso inteiro por fruta, prior S; peso da fruta = (w/S) × incentivo; o sorteio é o de
  `MotorFrutas._escolher` passo a passo, com o mesmo u da `rng_fruta`. O motor pergunta por `escolher_fruta` (gancho em `frutas.py`; sem ele,
  ou com `None`, a escolha de sempre; fruta fora do cenário falha alto). Com o aprendizado ligado ela entra no registro da decisão de comer
  e aprende com o mesmo sinal, pela mesma regra da L1 (a entrada de cada fruta é o incentivo dela; piso no coeficiente). Pesos: 9 × 7 × 12
  + 3 = 759, abaixo de mil.
- **E2** (`ConfigConsequencia.humor_na_fruta`, DECIDIDO): na fonte consequência, comer com fruta no cenário adia o crédito até o motor
  avisar `fruta_comida` (o segundo gancho em `frutas.py`, logo depois de comer); o sinal é `sinal_homeostatico_fruta`: os drives do N3
  mais o humor, com "depois" = o estado logo depois de comer (nutrição e efeito no humor aplicados). Fruta que faz mal dá sinal negativo
  pelo humor; as outras ações seguem com o `sinal_homeostatico` do N3, sem o humor. A bancada passa o `cfg_consequencia` dela (o mesmo
  ganho) a `observar_consequencia`; nas fontes dono e nenhuma o aviso não faz nada.
- **Gates** (`tests/test_lobos_mundo.py`, 37 testes, ~4 s): **G2 passa**: lobos desligados = `PoliticaInstintoBola` no mundo da bola
  (4 donos × 3 sementes) e = `PoliticaInstintoFrutas` no das frutas (descasado e iguais, 4 donos × 3 sementes), com a bola e as frutas
  juntas, byte a byte em estado, ações, log, rngs, `resumo_frutas` (escolhas, consumos, incentivos) e `rng_fruta`; a sub-decisão no prior
  = `_escolher` em 2000 sorteios; aprendiz ligado com ganho 0 = instinto. **G1 passa**: replay bit a bit, estado interno incluído, com o
  dono (L1) e no P1 com a E2. **E2**: fruta ruim → sinal negativo pelo humor, e o comer e a fruta desaprendem; nas 7 ações o humor sozinho
  dá sinal 0. A L0, a L1, o N3 e a bancada passam como antes (suíte inteira).
- **Fora:** a bancada ainda não monta os lobos que veem o mundo (`politica()` segue cega; os mundos das frutas na bancada são do chat D,
  `docs/TAREFA_V2_BANCADA_FRUTAS.md`). O `motivo_lobos` (expressão) não cita as regras novas: como no instinto da bola, fica para quem
  ligar a expressão no mundo.
- **Não mudou:** `engine.py`, `AcaoPet`, o bandit, `ambiente.py`, a web; a L1 e o N3 nos mundos de antes, byte a byte.

## V2, N5 — lado do mundo: o dono informa e a medida N1 da saciedade (2026-10-04, `docs/TAREFA_V2_N5_MUNDO.md`) — GATES PASSAM

Infraestrutura, sem run de pesquisa e sem faixa reservada. O desenho fino e o plano do N5 são do chat C (`docs/TAREFA_V2_N5_PLANO.md`);
**os nomes dos eventos foram combinados com ele** e o `docs/PLANO_ANALISE_V2_N5.md` (PR #142) os usa sem troca. A percepção da informação pelos
lobos é do chat B (rodada 6). Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **Evento:** `AcaoUsuario.INFORMAR_FRUTA_<A|B|C>_<BEM|MAL>` no fim do enum (`ACOES_INFORMACAO`, `informacao_de`, `informar`). O conteúdo
  é o que o dono diz; certo ou errado é decidido pelo braço. Só o `MotorFrutas` com `ConfigInformacao.ligada` (exige as frutas) aceita.
- **Informar não é cuidado nem reforço** (D-A): não mexe no estado, não conta como contato, não passa por `receber_acao_dono` e fica
  **fora do orçamento**, pelo canal das ofertas (B2). Fica vigente por `janela_min` (240, PROPOSTO) para a **percepção**:
  `Observacao.info_frutas` (+1 bem, −1 mal, 0 nenhuma, na ordem de `FRUTAS`), injetada pelo motor antes de cada decisão; informar de novo
  renova, o contrário troca. Registro derivado `MotorFrutas.informacoes`. O instinto não lê a informação.
- **`DonoInformante`** (sintético): informa sobre cada fruta oferecida logo depois da oferta, conhecendo o efeito real (E7); modo `certo`
  (P2) diz o efeito real, `errado` (P2e) o contrário, nos mesmos ticks; conteúdo binário ("mal" se o efeito no humor é negativo, senão
  "bem"). `simular_vida_frutas(..., informante=)`. O modo acoplado fica para o plano do C.
- **N1:** `metrics.saciedade_especifica_n1`: `avaliacao ~ 1 + preferência + recente + fome`, mais a queda média por unidade de consumo
  recente. A medida antiga (`saciedade_especifica`) fica, para reproduzir o N4.
- **Gates** (`tests/test_informacao.py`, 24 testes): **G1** replay bit a bit com informações (4 donos × 2 modos × 3 sementes); **G2** sem
  informação no log = a vida das frutas byte a byte (chave desligada ou ligada sem informante), e a vida `atencioso-frutas@11101` da
  validação do N4, rejogada do disco com o código novo, dá as medidas gravadas em `artifacts_v2_n4/validacao/vidas.json`; **o evento não
  muda a vida nem o orçamento** (com o instinto, a vida com o informante e sem ele têm o mesmo estado, ações e rngs; o canal fecha os
  mesmos 48) e **não chega ao aprendiz** (espião no `receber_acao_dono`); a janela, a renovação e a troca; **N1** recupera, em dados
  sintéticos com a preferência andando junto com a fome, a queda conhecida (β_recente = −k, β_fome = 0, β_pref = 1), onde a medida antiga
  põe a culpa na fome (|β_fome| > 0,1). Nenhuma releitura dos dados gravados.
- **Não mudou:** `engine.py`, `AcaoPet`, `lobos.py`, `ambiente.py`, o bandit, as vidas da bola e das frutas com o evento desligado, a web.

## V2, BANCADA-N5 — os lobos vendo o mundo e a fonte informacao (P2, P2e, P2a) (2026-10-04, `docs/TAREFA_V2_BANCADA_N5.md`) — GATES PASSAM

Infraestrutura, sem run de pesquisa nem número de resultado; só as sementes dos testes. Primeira tarefa da rodada 6 (`docs/V2_RODADA_5.md`),
com o plano do N5 (`docs/PLANO_ANALISE_V2_N5.md`, decisões N5-1 a N5-8) e o `CalendarioFrutas` (correção do coordenador). Só
`experiments/bancada_v2.py` e `digilab/metrics.py` mudaram; `lobos.py`, `frutas.py`, `ambiente.py` e `engine.py` não. Interpretações em
`docs/REGISTRO_DESVIOS.md`.
- **Os lobos veem o mundo na bancada:** `Bancada.politica()` passa `cfg_bola` no mundo da bola (`bola`, `bola_a1`) e `cfg_frutas` nos três
  mundos das frutas (`PoliticaLobos(cfg, cfg_lobos, cfg_bola=, cfg_frutas=)`, LOBOS-MUNDO). No `padrao` nada muda. Com isso o P0 com lobos
  é o instinto que vê o mundo byte a byte (`PoliticaInstintoBola`, `PoliticaInstintoFrutas`), o `bola_a1` com lobos é o braço "bola" da A1
  (antes o "bolacega") e o P1 come fruta e credita a E2 (`recompensas["consequencia_fruta"]`).
- **A fonte `informacao`** (`FONTES_IMPLEMENTADAS`; braços P2 certa, P2e errada e o novo **P2a acoplada**): o cérebro aprende pela
  consequência como o P1 (`APRENDE_PELA_CONSEQUENCIA`), nada do dono chega como sinal, e a informação entra pelo canal do mundo
  (`RegraFrutasComInformante`: as ofertas do `CalendarioFrutas` e, logo depois, o que o informante diz; fora do orçamento, B2). Só existe nos
  mundos das frutas (fora deles `ValueError`); a `ConfigInformacao` fica ligada em todo braço das frutas (`Bancada.cfg_informacao`).
  - **P2 e P2e** (`InformanteDoMundo`): dois `DonoInformante` (`certo`, `errado`) com os **efeitos reais da condição da bancada**
    (`Bancada.efeitos_reais`); no mutável, os de antes até o `tick_troca` e os de depois a partir dele. Informam nos mesmos ticks, com
    conteúdo oposto.
  - **P2a** (`InformanteAcoplado`, plano 4.2, N5-4): o mesmo multiconjunto de (fruta, conteúdo verdadeiro no tick original) que o P2 da
    unidade recebe, em passos do dono sorteados pela rng `derivar_semente("informacao-acoplada", semente)` (um `randrange` por item, na
    ordem do calendário). O modo `acoplado` do `DonoInformante` não está na `main`; a bancada implementa a regra do plano, e o chat A deve
    dar os mesmos eventos (ou reusar este).
- **Contagem e filtros:** informar não conta como interação do dono (`contar_acoes`); `contar_informacoes` e `VidaBancada.informacoes`;
  `FORA_DO_ORCAMENTO` = eventos do mundo + informações. Filtros novos do acoplado: `sem_informacao`, `sem_ensino` (sinais + informações) e
  `sem_ensino_sem_carinho`. A informação não é evento do mundo: o só cuidado pode tirá-la.
- **Medidas do N5** (só nos mundos das frutas): `metrics.consumos_ate_metade` (consumos até a taxa de fruta ruim cair à metade da do P0 da
  mesma célula, pela `eficiencia_amostral`; nunca chega = censurado à direita; o P0 usa a própria taxa total) e
  `metrics.tabela_braco_condicao_parcial` (grade completa, conta as vidas sem valor por célula). As tabelas ganham `taxa_fruta_ruim_inicio`,
  `taxa_fruta_ruim_final` e `consumos_ate_metade`; as medidas, `informacoes` e `decisoes_com_informacao`.
- **Gates** (`tests/test_bancada_n5.py`, 22 testes, ~40 s): **P0 lobos = P0 instinto byte a byte** na bola, no `bola_a1` e nos três mundos
  das frutas (4 donos × 2 sementes, sem e com genoma), e o `padrao` igual a antes; **G1** de toda vida e acoplado (P2, P2e, P2a; `sem_ensino`;
  P2 → P1 sem filtro); **sem informação no log, P2 = P1 byte a byte** (P2, P2e e P2a sem informante, em três mundos e donos);
  **P2 e P2e informam nos mesmos ticks**, com conteúdo oposto e o do P2 verdadeiro no tick (também no mutável, dos dois
  lados da troca); o **P2a** tem o mesmo multiconjunto em outros ticks e segue a regra do plano; **espião**: nenhum `informar_*` chega a
  `receber_acao_dono` e o cérebro não tem recompensa do dono. Testes antigos atualizados para os lobos que veem o mundo
  (`test_bancada_mundos`, `test_bancada_frutas`, `test_bancada_v2`).
- **Até o N5-CEREBRO (chat B):** os lobos ainda não leem `Observacao.info_frutas`, então hoje P2, P2e e P2a vivem como o P1 (mesmas ações e
  consumos; só o registro tem as informações). Por isso o G2 é testado pelo braço sem informante, que vale também depois que eles lerem.
- **Fumaça** (`experiments/configs/bancada/fumaca_n5.json`, NÃO canônica: descasado, atencioso, P0, P1, P2, P2e, P2a e os acoplados
  `sem_ensino`): 35 vidas em ~16 s; sem artefato.

## V2, N5-CEREBRO — a entrada `info` dos lobos (2026-10-04, `docs/TAREFA_V2_N5_CEREBRO.md`, `docs/PLANO_ANALISE_V2_N5.md`) — GATES PASSAM

Infraestrutura do aprendiz para o N5, sem run de pesquisa; só as sementes dos testes (11, 22, 33). Decisões N5-1 a N5-3 do plano.
Só `lobos.py` e `config.py` mudaram. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **A entrada:** `Observacao.info_frutas` (+1 bem, −1 mal, 0 nada; o `MotorFrutas` injeta com `ConfigInformacao.ligada`) entra **só na
  sub-decisão da fruta** (N5-2): peso da fruta f = (w_f/S) × incentivo_f + (w_info/S) × info_f, com **um peso `w_info` compartilhado**
  entre as frutas (N5-3). A fruta com informação vigente tem o piso (`piso_peso`/S) no peso efetivo, com o aprendizado ligado ou não,
  porque o "mal" pode levar o peso abaixo de zero; sem informação vigente a fruta tem o peso de hoje.
- **Confiança de partida:** `ConfigLobos.w0_info` (PROPOSTO, N5-1; `lobos.PARAMETROS_LOBOS_N5`), inteiro na escala S. **0 (o padrão)
  desliga a entrada**: sem termo e sem peso (a vida de hoje, byte a byte, com ou sem informação no registro). A grade {S/4, S/2, 3S/4}
  é a da calibração do N5 (rodada 7). Com w0 > 0 o peso existe só nos lobos que veem as frutas (`peso_info`, `peso_info_prior` no
  estado interno; um peso a mais, 760).
- **Aprendizado:** a regra da L1 no peso compartilhado (`lobos.atualizar_info`: a soma, sobre as frutas, de I_f (S·1[f=f*] − P_f)/W_f,
  com I_f = ±S ou 0), cortada em w0 ± teto. **Só a consequência mexe nele** (`_aplicar_sinal(..., consequencia=True)` em
  `observar_consequencia` e `fruta_comida`, o sinal do P1 com a E2); elogio, bronca, latência e chamado ignorado não mexem (os pesos de
  cada fruta continuam aprendendo com o dono, como no LOBOS-MUNDO).
- **Gates** (`tests/test_lobos_n5.py`, 17 testes, ~10 s): **G1** replay bit a bit (P1 e P3, informante certo e errado, w0 S/2);
  **w0 = 0 com informação** = a vida sem informação (estado, ações, rngs, consumos e pesos; lobos desligados e P1); **sem informação no
  registro** com w0 na grade (chave desligada ou ligada sem informante) = a vida de w0 = 0 byte a byte, log incluído; **com o aprendizado
  desligado a escolha pende na medida do w0** (p("mal") cai de 0,5 a ~0,06 de 0 a S/2, na conta exata; numa vida, o informante errado faz o
  pet comer mais a fruta ruim que o certo); **espião**: no P1 o peso da informação muda e todo sinal é da consequência; no P3 nenhum sinal
  do dono mexe nele em decisões com informação; um elogio depois de uma escolha informada muda o peso da fruta e não o da informação;
  fruta informada "bem" que derruba o humor baixa o peso, informada "mal" o sobe.
- **Para a bancada (chat D):** basta o `cfg_lobos` com `w0_info` e o `MotorFrutas` com `ConfigInformacao` ligada; nenhuma mudança no
  `PoliticaLobos` além disso.
- **Não mudou:** `engine.py`, `AcaoPet`, o bandit, a L0, a L1, o N3, os lobos sem informação (byte a byte), `frutas.py`, a web.

## V2, N5-ACOPLADO — o informante acoplado (P2a) e o motivo das regras novas dos lobos (2026-10-04, `docs/TAREFA_V2_N5_ACOPLADO.md`) — GATES PASSAM

Infraestrutura, sem run e sem faixa reservada; só as sementes dos testes (11, 22, 33). Decisão N5-4 (`docs/V2_RODADA_5.md`) e seção 4.2 de
`docs/PLANO_ANALISE_V2_N5.md`. Só `frutas.py`, `motivo.py` e `expressao.py` mudaram; `engine.py`, `lobos.py`, a bancada e a web não.
Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **Acoplado** (`DonoInformante.acoplado(efeito, frutas_do_p2, semente, dias)` ou `acoplado_de(p2, semente, dias)`): o mesmo multiconjunto
  de frutas sobre as quais o P2 (modo certo) da mesma unidade informou, com o conteúdo **verdadeiro**, em ticks sorteados uniformemente
  entre os passos do dono da vida (um sorteio por item, multiconjunto ordenado antes) pela rng própria
  `derivar_semente("informacao-acoplada", semente)`, toda consumida na construção: não toca a rng de ambiente, de política, da fruta, do
  dono nem o `random` global. Fora do orçamento, como os outros modos. O digilab não importa a bancada: quem monta o P2a passa o
  multiconjunto (a bancada, do chat D, com o `CalendarioFrutas`).
- **Interface da vida:** `simular_vida_frutas` chama `informante.acoes_do_passo(tick, ofertadas)` em todo passo do dono: certo e errado
  respondem às ofertas do passo (o `acoes` de sempre), o acoplado devolve o que a agenda marcou. `acoes` no acoplado e o acoplado sem o
  construtor falham alto; `pendentes()` = o que ainda não saiu (0 no fim da vida).
- **Motivo das regras novas** (`motivo_lobos`, e `motivo_instinto` para o instinto da bola e das frutas): `bola_no_cenario` e
  `fruta_no_cenario` com a regra de honestidade de sempre: a bola (fator `bola`) ou a fruta (`fruta`) só vira fator se, com o mesmo u e
  sem o termo dela (brincar = 1 + 3·humor; comer fora), a ação seria outra. No ramo aprendido as entradas `bola` e `fruta` dos lobos que
  veem o mundo viram fatores pelo nome. **A escolha da fruta** é o segundo fator da decisão de comer: `incentivo_fruta` quando o sorteio
  com o incentivo puro e o mesmo u dá a mesma fruta, `escolha_aprendida_fruta` quando o peso aprendido mudou a fruta; os incentivos vêm
  pelo gancho `escolher_fruta` (o registro dos lobos não os guarda). Textos com marcador único na `expressao.FATORES`, cobertura conferida
  na carga; nada de vocabulário de sensação (F2).
- **`PoliticaComMotivo` repassa os ganchos das frutas** (`escolher_fruta`, `fruta_comida`): antes, embrulhar os lobos que veem as frutas
  mudava a vida (a escolha caía no `_escolher` do motor e o E2 sumia).
- **Gates** (`tests/test_n5_acoplado.py`, 17 testes, ~3 s): **certo e errado byte a byte** contra `tests/gabaritos/n5_informante_certo_errado.json`
  (24 vidas, gravado com o código da main antes da mudança); **acoplado** com o mesmo multiconjunto (fruta, conteúdo) do P2, conteúdo
  verdadeiro, ticks diferentes, nada pendente, determinístico; **a rng do acoplado não mexe nas outras** (com o instinto, a vida com o
  acoplado e a sem informante têm o mesmo estado, ações e rngs, a da fruta incluída); **G1** com o acoplado; **motivo**: lobos que veem
  as frutas embrulhados, com o aprendizado desligado e ligado, a vida igual à sem embrulho, fatores ⊆ `FATORES_VIDA` e ≤ 2, `fruta` e
  `incentivo_fruta` citados (sem aprendizado, nunca `escolha_aprendida_fruta`); a bola citada no mundo da bola; o instinto das frutas
  embrulhado sem erro.

## V2, REVISAO-APRENDIZ — teto, janela de crédito ou exposição? (2026-10-04, `docs/TAREFA_V2_REVISAO_APRENDIZ.md`, `docs/PLANO_ANALISE_V2_REVISAO_APRENDIZ.md`) — DIAGNÓSTICO FEITO

Diagnóstico só com sementes de calibração (bases 18101…18505, K = 4: 20 unidades), sem gate. Plano no primeiro commit, antes da run.
Números de `artifacts_v2_revisao/calibracao/` (`<ponto>/resultado.json`, `avaliacao.json`, `diagnostico.json`, `recomendacao.json`;
vidas só da base no git, os outros pontos regeneráveis); relatório `docs/RESULTADO_V2_REVISAO_APRENDIZ.md`. Interpretações em
`docs/REGISTRO_DESVIOS.md`.
- **Código.** `ConfigLobos.traco_decisoes`/`traco_fator` (PROPOSTOS; 0 = o crédito de hoje, byte a byte): traço de elegibilidade em
  inteiros, em que o sinal (consequência, elogio, bronca) chega às K decisões anteriores com `div_arred(f·λ^k, S^k)`, e o chamado fica
  preso ao chamado (`Aprendiz._creditar`). `bancada_v2.bancada_da_config` lê as chaves `lobos` e `frutas` da config (sem elas, a bancada de
  sempre). `experiments/run_revisao_aprendiz.py` faz as seções 4–7 do plano; o motivo é rejogado no motor das frutas. Testes
  `tests/test_revisao_aprendiz.py` (10).
- **Desenho:** P0/P1/P3, `casado_frutas` e `descasado`, atencioso, 14 dias; base = passo 512, teto 1·S, ganho 4, E2, `w_fruta` 6,
  4 ofertas/dia; uma alavanca por ponto: teto 2·S, 4·S e 16·S; traço (2, S/2), (4, 3S/4), (8, 7S/8); `w_fruta` 12, 24 e 8 ofertas/dia.
- **Base:** no descasado o P1 come menos a fruta ruim que o P0 (G_ap **+0,109 [+0,050; +0,182]**); no casado, mais (−0,062
  [−0,110; −0,018]). O aprendido decide em 0,257 das decisões do P1 e 0,247 do P3. Vidas no teto: P1 20/20 e P3 17/20 no descasado. O P3
  quase não come fruta (p 0,06). A privação e a saúde não mudam em nenhum ponto: o atencioso nunca deixa o pet em privação.
- **Teto:** no P1 nada muda (Δ M1 e Δ G_ap 0,000, com as vidas no teto caindo a 0). No P3 o aprendido decide mais (T3 +0,039 [+0,008;
  +0,079]) e acerta menos a tarefa (−0,026 [−0,055; −0,001]). **Janela:** piora o G_ap do P1 (J3 −0,027 [−0,041; −0,014]), o M1 e o
  acerto do P3 (J3 −0,124). **Exposição:** os consumos sobem (8 ofertas: +63,5), mas o G_ap não (`w_fruta` 24: −0,064 [−0,106;
  −0,024]), porque o P0 também passa a comer mais.
- **Pelas regras registradas:** o teto segura (pelo P3), a janela e a exposição não. **Ponto recomendado para a calibração do N5 e do
  experimento maior: teto 16·S (16384)**, o resto na base; o T2 (4·S) dá quase o mesmo com teto finito.
- **Pós hoc (fora do plano):** o P1 aprende qual fruta evitar (peso da ruim ~90, com 17 de 20 vidas em 0; a boa ~1700), mas a escolha só
  age com duas frutas ou mais no cenário. Nelas o P1 come a ruim 29% das vezes, contra 44% do P0. Com uma fruta só, que é 55% dos
  consumos dele, come o que houver. **O gargalo é a decisão de comer não saber qual fruta está no cenário** (a entrada `fruta` é o
  maior incentivo), não as três alavancas. Decisões R1–R4 para o Matheus no relatório.
- **Não mudou:** `engine.py`, `AcaoPet`, o bandit, `frutas.py`, a web; com os campos novos no padrão, a L0, a L1, o N3, o N5 e a
  bancada byte a byte.

## V2, BANCADA-EXPERIMENTO — faixas, o ponto T3 e o orquestrador do experimento maior (2026-10-05, `docs/TAREFA_V2_BANCADA_EXPERIMENTO.md`) — GATES PASSAM

Infraestrutura, sem run com faixa reservada: só fumaça nas sementes dos testes. Rodada 7 (`docs/V2_RODADA_6.md`), plano
`docs/PLANO_ANALISE_V2_EXPERIMENTO_MAIOR.md` (seções 5 e 6) e decisão R1 (`docs/RESULTADO_V2_REVISAO_APRENDIZ.md`). Só `experiments/` e
`digilab/metrics.py` mudaram; `engine.py`, `lobos.py`, `frutas.py` e a web não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **Faixas reservadas** (`bancada_v2.FAIXAS_RESERVADAS`): mais 18101…18505 (revisão do aprendiz), 19101…19505 e 20101…20505 (N6) e o N11
  (16101…16505, 17101…17505, do `docs/ROADMAP_V2.md`, que o plano do N6 apontou como faltando).
- **Ponto do aprendiz** (`PONTOS_APRENDIZ`, `cfg_lobos_do_ponto`, campo `ponto` da config da bancada): `L1` (o `CONFIG_LOBOS_APRENDIZ`, passo
  512, teto 1024) é o padrão, então as runs antigas não mudam; `T3` = teto 16·S (16384), o resto igual, sem traço (R1);
  `PONTO_N5_EXPERIMENTO = "T3"`. A chave `lobos` troca campos por cima do ponto (o `w0_info` do N5, por exemplo). O T3 nomeado é o mesmo
  aprendiz do T3 da revisão (teste). O `meta.json` da bancada grava o ponto e o aprendiz efetivo.
- **Orquestrador** (`experiments/run_v2_experimento_maior.py`): P0, P1, P2, P2e e P3 × `casado_frutas`, `descasado` e `mutavel` com o
  atencioso, mais o "só cuidado" acoplado de P2, P2e e P3 (filtro `sem_ensino`: sem sinais e sem a informação, com as ofertas), e a
  referência do mundo padrão (P0, P1, P3, só descritiva). Pela seção 6: contrastes pareados por unidade, orientados para a predição,
  bootstrap reamostrando as sementes (`metrics.contraste_pareado`: IC 95% e 90%, p unilateral, teste t pareado como conferência);
  **Holm** sobre os seis primários (`metrics.holm`); a **equivalência** da predição 5 fora da família (`metrics.dentro_da_margem`); Δ pela
  regra da seção 6.3 na calibração e do adendo na validação; σ_d e N por contraste (`metrics.tamanho_amostra`). As **leituras**: confirma,
  refuta, inconclusivo, inconclusivo por duração (a inclinação de P0 − P1 nos 4 últimos dias), confirma parcialmente e não testável (sem o
  K2); a separação do cuidado (5.1); o dia em que o P2e cruza o P0. Grava `frutas/` e `padrao/` (a bancada), `contrastes.json`,
  `curvas.json`, `resumo.json` e `meta.json`.
- **Modos pelas sementes:** `fumaca` (101…505), `calibracao` (bases 14101…14505) e `validacao` (15101…15505). Calibração e validação pedem
  `plano` = este plano, as unidades derivadas e 14 dias; a validação exige o Δ do adendo e a calibração o recusa. Misturar faixas ou usar
  a de outro experimento falha alto.
- **Contratos:** o K2 (o humor da fruta no sinal do P1, E2) é lido da config; o **K4** (o dono do P3 julga a fruta pelo efeito real) **não
  está na main**: `K4_DONO_JULGA_FRUTA = False`, e a predição 5 sai com o aviso de que mede só que o P3 não sabe das frutas.
- **Gates** (`tests/test_experimento_maior.py`, 12 testes, ~25 s): **G1** de toda vida da fumaça, rejogada de novo do arquivo; **contrastes
  e Holm em dados sintéticos com resposta conhecida** (a t de Student da tabela, o exemplo clássico do Holm, o Holm que para na segunda,
  o bootstrap que reamostra as sementes juntas, o N da fórmula; medidas sintéticas em que tudo confirma, em que 1, 2 e 5 refutam, o
  "não testável" sem K2 e o "inconclusivo por duração" no lugar do refuta); **a fumaça recusa sementes de validação sem plano** (e com
  outro plano, misturadas, de outra faixa, sem Δ, com vida curta). A fumaça põe `w0_info` = S/2 só para a informação agir.
- **Fumaça** (`experiments/configs/v2_experimento_maior/fumaca.json`, NÃO canônica: 5 unidades derivadas das sementes dos testes, 4 dias,
  T3 com `w0_info` S/2): 120 vidas das frutas + 15 do padrão em ~1 min; sem artefato.
- **Fora:** o controle de capacidade sem lobos (E6, secundário no P1 e no P3) não roda: a bancada só tem os cérebros `lobos` e `instinto`
  (o `camada_unica` na bancada é do N11). A conferência do N por simulação fica para o adendo.

## V2, FRUTA-NO-CENARIO, parte A — o mundo diz qual fruta está no cenário (2026-10-05, `docs/TAREFA_V2_FRUTA_NO_CENARIO.md`) — GATES PASSAM

Decisão R2 (`docs/RESULTADO_V2_REVISAO_APRENDIZ.md`, `docs/V2_RODADA_6.md`). Infraestrutura, sem run; só as sementes dos testes. Só
`policy.py` (o campo) e `frutas.py` (a injeção) mudaram; `lobos.py` e a bancada não (a decisão de comer que lê o campo é a parte B, do
chat B). Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **Campo:** `Observacao.frutas_cenario`, a presença de cada fruta na ordem de `events.FRUTAS` (1,0 presente, 0,0 ausente), padrão
  `(0,0, 0,0, 0,0)`. Só o `MotorFrutas` com as frutas ligadas injeta, logo antes de `agir`, junto com `fruta` e `info_frutas`
  (`_presenca_na_decisao`): são as frutas de `_na_decisao`, já sem as vencidas, as mesmas que a sub-decisão de comer considera. `de_estado`,
  o instinto, os lobos de hoje e o bandit não o leem; `Observacao.fruta` continua o maior incentivo.
- **Gates** (`tests/test_frutas_cenario.py`, 8 testes, ~20 s): **G2**, nenhuma vida de hoje muda: 168 vidas da bancada (P0 com lobos e com
  instinto, P1, P2, P2e, P2a e P3; os três mundos das frutas; 4 donos; sementes 101 e 202) iguais a `tests/gabaritos/frutas_cenario_vidas_de_hoje.json`,
  gravado com o código da main **antes** do campo (sha256 do log, do estado final, das ações, das rngs de ambiente, política e fruta, do
  `resumo_frutas` e do estado interno da política); **a presença certa a cada decisão** (um espião na política: o campo é igual aos
  `presentes` do registro de ofertas, decisão a decisão, e `fruta` é o maior incentivo entre eles; há decisões com duas frutas ou mais);
  frutas desligadas não preenchem; **G1** com o campo e o informante.

## V2, FRUTA-NO-CENARIO, parte B — a decisão de comer lê a fruta presente (2026-10-05, `docs/TAREFA_V2_FRUTA_NO_CENARIO.md`) — GATES PASSAM

Decisão R2 (`docs/RESULTADO_V2_REVISAO_APRENDIZ.md`): o P1 aprendia qual fruta evitar, mas comia a ruim quando ela estava sozinha (55%
dos consumos dele no descasado), porque a decisão de comer só via `fruta` (o maior incentivo). Infraestrutura, sem run; só as sementes
dos testes. Só `lobos.py` mudou (e dois testes de outras frentes, abaixo). Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **O termo:** na regra `fruta_no_cenario`, o peso efetivo de comer ganha Σ_f (w_f / S) × presença_f, com `Observacao.frutas_cenario` da
  parte A; um peso inteiro por fruta, **prior 0**, no lobo de decisão (`contribuicoes["decisao"]`). No prior o termo é 0,0 exato e a vida
  é a do instinto das frutas byte a byte. Três pesos a mais (762 com as frutas; 763 com o `w0_info`).
- **Aprendizado:** a regra da L1 (`lobos.atualizar_comer_fruta`): Δw_f = arred(f_S · passo · X_f · (S·1[a* = comer] − P_comer) / (S·S·W_comer)),
  X_f = presença × S, cortado em ± teto. **Só a consequência mexe nesses pesos** (o P1 com a E2, pelo `_aplicar_sinal(..., consequencia=True)`);
  elogio, bronca e o chamado não mexem. **A informação do dono não entra** na decisão de comer (N5-2): continua só na escolha de qual fruta.
- **Gates** (`tests/test_comer_ve_fruta.py`, 11 testes, ~4 s): **G2**, P0 com lobos = P0 com o instinto das frutas pela bancada, byte a
  byte, nos três mundos; no prior a presença não muda o peso de comer; sem frutas, os lobos de hoje (sem as chaves novas). **O P1 com a
  fruta ruim sozinha aprende a não comer** (o peso dela fica negativo e p(comer | só ela) cai; a de efeito bom sobe). Na bancada (4 dias, 3
  sementes, descasado) os três pesos sobem, porque comer dá sinal positivo pela nutrição, mas **o da fruta ruim fica abaixo dos outros dois**;
  o P3 não mexe neles (espião: `atualizar_comer_fruta` nunca é chamada no P3). **G1** de toda vida pela bancada.
- **Testes de outras frentes ajustados:** `tests/test_frutas_cenario.py` (parte A, chat A): o G2 do gabarito passa a conferir só o P0 e o P3,
  com o estado interno sem as chaves da parte B; as vidas do P1, P2, P2e e P2a mudam por desenho. `tests/test_lobos_mundo.py`: a contagem de
  pesos (+3).
- **Não mudou:** `engine.py`, `AcaoPet`, o bandit, `frutas.py`, a bancada, a web; os lobos sem frutas e o P0/P3 nas frutas, byte a byte.

## V2, N7-MUNDO — o pedido "deixe a fruta X" e o dono que pede (2026-10-05, `docs/TAREFA_V2_N7_MUNDO.md`, `docs/PLANO_ANALISE_V2_N7.md`) — GATES PASSAM

Lado do mundo do N7 (pré-requisito R4 do plano; decisões N7-1, N7-6, N7-7 e N7-8). Infraestrutura, sem run de pesquisa nem faixa reservada;
só as sementes dos testes (11, 22, 33). Mudaram `events.py` (fim do enum), `frutas.py`, `policy.py` (o campo), `config.py` (`ConfigPedido`)
e `protocol.py` (o registro dela); `engine.py`, `AcaoPet`, `lobos.py` (a entrada `pedido` é do chat B), `ambiente.py`, a bancada (chat D) e
a web não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **Evento:** `AcaoUsuario.PEDIR_DEIXAR_FRUTA_<A|B|C>` no fim do enum (`ACOES_PEDIDO`, `pedido_de`, `pedir_deixar`), separado da informação
  do N5: é a vontade do dono, sem valor de verdade. Só o `MotorFrutas` com `ConfigPedido.ligada` (exige as frutas) aceita; sem a chave,
  `PedidoSemChave`.
- **O pedido não é cuidado nem reforço:** não mexe no estado, não conta como contato, não passa por `receber_acao_dono` e fica **fora do
  orçamento**, pelo canal das ofertas (B2). Fica vigente por `ConfigPedido.janela_min` (240, PROPOSTO, a mesma da informação) para a
  **percepção** `Observacao.pedido_frutas` (−1 na fruta com pedido vigente, 0 nas outras, na ordem de `FRUTAS`; padrão neutro), injetada
  antes de cada decisão; pedir de novo renova. Registros derivados: `MotorFrutas.pedidos`, `decisoes_com_pedido` e **`desobediencias`** (o
  pet comeu uma fruta que tinha −1 na percepção daquela decisão). Com a chave, `estado()` ganha `pedido` e `desobediencias` (a contagem).
- **`DonoPedinte`:** a fruta X sorteada uma vez por vida por `derivar_semente("pedido-fruta", semente)`, uniforme entre as frutas e sem
  olhar a preferência inata (N7-6); pede "deixe X" logo depois de cada oferta que tem X, só nos dias 1…`dias_pedido` (10, PROPOSTO) e nada
  depois (a extinção, N7-7). Com `bronca=True` (só o P3+ped, N7-8), uma `repreender` por desobediência no primeiro passo do dono depois
  dela, também fora do orçamento (a bronca chega ao aprendiz, como deve). `simular_vida_frutas(..., pedinte=)` chama
  `pedinte.acoes(motor.estado(), ofertadas)` depois das ofertas e do informante; `Vida.pedidos` e `Vida.broncas`.
- **Gates** (`tests/test_n7_pedido.py`, 24 testes, ~6 s): **G2**, 48 vidas (instinto e lobos aprendendo, com e sem o informante; 4 donos;
  3 sementes) iguais a `tests/gabaritos/n7_vidas_de_hoje.json`, gravado com o código da main **antes** da mudança (commit próprio), e a
  chave ligada sem pedido = a desligada; **o pedido não altera o estado nem o orçamento** (com o instinto, a vida com o pedinte e sem ele têm
  o mesmo estado, ações, rngs e consumos, o log só ganha os pedidos e o canal fecha os mesmos 48; o evento não muda o `Estado`); **não chega
  ao aprendiz** (espião); a **percepção** decisão a decisão; **as fases** (vida de 14 dias: pedido no mesmo tick de toda oferta de X até o
  fim do dia 10, nenhum depois) e **o sorteio** (600 sementes: uniforme, independente da preferida, o `random` global intacto); **a bronca**
  só com a chave, uma por desobediência, no primeiro passo depois; **G1** com pedidos, broncas e o informante; os erros de uso.
- **Para os chats B e D:** a entrada `pedido` dos lobos lê `obs.pedido_frutas`; a bancada monta o P0+ped, P1+ped e P3+ped com
  `DonoPedinte.da_semente(semente, CONFIG_PEDIDO_LIGADA, bronca=...)` (as ações saem de `acoes(estado, ofertadas)`), põe os pedidos (e só
  eles) no que fica fora do orçamento e tira os pedidos e as broncas no `sem_ensino` (plano 4.2).

## V2, CEREBRO-N6-N7 — memória de episódios (N6) e arbitragem do pedido (N7) nos lobos (2026-10-05, `docs/TAREFA_V2_CEREBRO_N6_N7.md`) — GATES PASSAM

Etapa C1 do `docs/ROADMAP_V2.md` (revisão 3: montar tudo, calibrar junto, validar uma vez). Só testes de mecanismo, nenhuma run com faixa
reservada; só as sementes dos testes (11, 22, 33, 101, 202). Planos `docs/PLANO_ANALISE_V2_N6.md` e `docs/PLANO_ANALISE_V2_N7.md`. Só
`lobos.py` e `config.py` mudaram. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **Chaves** (`ConfigLobos`, PROPOSTOS, `lobos.PARAMETROS_LOBOS_N6_N7`): `memoria_ligada` (False), `memoria_ganho` (0), `memoria_modo`
  (`relevante`, `recencia`, `embaralhada`), `memoria_janela_recencia_ticks` (240), `memoria_permutacao` (vazia) e `w0_pedido` (0). Com os
  padrões nada existe: a vida e o estado interno de hoje, byte a byte.
- **N6, a memória** (`MemoriaEpisodios`, só nos lobos que veem as frutas): todo consumo de fruta, em qualquer fonte, vira um episódio
  {tick, fruta, valência, intensidade}, com valência = arred(Δhumor / |`efeito_humor_ruim`| × S) cortada em [−S, S] (o humor da decisão e o
  logo depois de comer). Espaços da v1 (`CONFIG_MEMORIA_ESPACOS`: 4 no curto por 12 h, 2 no longo), a mesma regra de desempate, sem
  decaimento contínuo e sem relembrar. O tick vem da hora da observação (o dia vira quando a hora volta). **Age só na escolha da fruta**:
  cada fruta presente é uma pista, e o episódio recuperado (o mais forte; empate, o mais recente) soma m_f = div_arred(ganho × valência, S)
  ao peso dela. Modos: `relevante` (MR), `recencia` (MT, só episódios de até 240 min) e `embaralhada` (ME: a pista f recupera o episódio
  de π(f), π o desarranjo da vida, `lobos.desarranjo_n6(semente)`, rng `derivar_semente("n6-embaralha", semente)`). Ganho 0 com a memória
  ligada = o M0 (guarda, não age). **Sonda contrafactual** (com duas frutas ou mais): a mesma escolha com m = 0 e o mesmo u, no motivo
  (`sonda_memoria`) e nas contagens (`estado_interno()["memoria"]["sondas"]`); só lê.
- **N7, o pedido** (`Observacao.pedido_frutas`, −1 na fruta com pedido vigente, na ordem de `FRUTAS`; o campo é do chat A,
  `docs/TAREFA_V2_N7_MUNDO.md`, branch `v2-n7-mundo`, ainda fora da main; os lobos o leem por `getattr`, com padrão nenhum pedido): com
  `w0_pedido` ≠ 0 nos lobos que veem as frutas, p = −1 quando toda fruta no cenário tem pedido vigente (senão 0), e comer ganha
  (w_pedido / S) × p **só nas regras `fome_moderada` e `fruta_no_cenario`** (`REGRAS_PEDIDO`), com o piso; as urgentes não leem o pedido.
  Na escolha da fruta, (w_pedido / S) × pedido_f na forma da informação do N5, com o piso. Um peso compartilhado, iniciado em `w0_pedido`;
  aprende pela regra da L1 (`lobos.atualizar_pedido`, cortado em w0 ± teto) com o sinal de qualquer fonte (a consequência e o dono).
  **Sonda "quem decidiu"** (no motivo, `pedido`): a ação com o mesmo u e sem o termo, e se o pedido mudou a decisão.
- **Gates** (`tests/test_cerebro_n6_n7.py`, 26 testes, ~25 s): **G2**, chaves desligadas = a vida de hoje: 192 vidas (pontos L1 e T3 com
  `w0_info` S/2; padrão, bola e os três mundos das frutas; P0 a P3; 2 donos; 2 sementes) iguais a
  `tests/gabaritos/cerebro_n6_n7_vidas_de_hoje.json` (sha256 do resumo do motor e do estado interno), gravado com o código da main antes da
  mudança (`tests/gabarito_cerebro_n6_n7.py`, commit próprio); **G1** com memória e pedido, estado interno incluído; **memória**: um
  episódio ruim recente com X baixa p(X) só com a memória ligada, na medida do ganho (conta exata); a sonda reproduz a decisão sem memória;
  recência e embaralhado; a regra dos espaços; o relógio que vira o dia; o M0 é o P0 nas decisões e codifica todo consumo; **arbitragem**:
  G-URG (sono, necessidade, abandono iguais com pedido vigente), a fome moderada pesa na medida do `w0_pedido`, o pedido na escolha da
  fruta, o peso aprende pelo dono e pela consequência, sem o campo nada muda.
- **Para a bancada (chat D):** o braço ME precisa de `memoria_permutacao = desarranjo_n6(semente)` por vida (fora disso, recusado); os
  outros braços só trocam as chaves por cima do ponto (`cfg_lobos_do_ponto`).
- **Não mudou:** `engine.py`, `AcaoPet`, o bandit, `frutas.py`, a bancada, a web. A calibração e a validação do N5 não rodaram (nota
  `a810d03`, branch `v2-n5-calibracao`, como registro).

## V2, BANCADA-N6-N7 — o mundo iguais_frutas, os braços do N6 e do N7 e as medidas dos dois planos (2026-10-05, `docs/TAREFA_V2_BANCADA_N6_N7.md`) — GATES PASSAM

Infraestrutura, sem run de pesquisa e sem faixa reservada: só as sementes dos testes. Planos `docs/PLANO_ANALISE_V2_N6.md` (N6-1 a N6-10)
e `docs/PLANO_ANALISE_V2_N7.md` (N7-1 a N7-10). Só `experiments/bancada_v2.py` e `digilab/metrics.py` mudaram; `engine.py`, `lobos.py`,
`frutas.py` e a web não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **Faixas:** 21101…21505 e 22101…22505 (N7) nas `FAIXAS_RESERVADAS`; `BASES_N6` e `BASES_N7`. As unidades derivadas ganharam o prefixo
  do plano (`unidades_derivadas(bases, K, prefixo)`, campo `prefixo` em `unidades`: `"experimento-maior"` (o padrão), `"n6"`, `"n7"`;
  genoma `prefixo + "-genoma"`, seção 12.2 dos dois planos).
- **Mundo `iguais_frutas`** (N7-5): condição nova `iguais`, as três frutas com `efeito_humor_neutro` (o mundo "iguais" do N4 na bancada),
  as ofertas do `CalendarioFrutas`, iguais às dos outros mundos das frutas. Sem fruta ruim, a `taxa_fruta_ruim` é 0 e os
  `consumos_ate_metade` saem `sem_referencia`. O informante do P2 diz "bem" de toda fruta.
- **Braços do N6** (M0, MR, MT, ME; fonte `nenhuma`, o aprendizado do lobo de decisão desligado, N6-2; campo `Braco.memoria`) e **do N7**
  (P0+ped, P1+ped, P3+ped; campo `Braco.pedido`): declarados como o plano manda e **falhando alto com o nó** (`NOS_PENDENTES`: a memória é
  do chat B; o pedido, do chat A e da entrada `pedido` do chat B) em `braco_de`, na config e na vida. Filtros do N7 (`sem_pedido`,
  `sem_ensino_sem_pedido`) idem (`filtro_de`, `FILTROS_PENDENTES`). O **desarranjo** do ME (`desarranjo_n6`, N6-6) já existe: um dos dois
  ciclos de {a, b, c}, por `derivar_semente("n6-embaralha", semente)`, sem tocar outra rng.
- **Medidas** (`digilab/metrics.py`, em dados sintéticos): N6 `memoria_nas_subdecisoes` (fração decidida pela memória nas
  sub-decisões com 2+ frutas, G-CITA; cobertura; episódios decisivos; fração sobre todas as decisões, só descritiva) e
  `ocupacao_espacos_frutas`; N7 `quem_decidiu_conflito`, `deferencia_ao_pedido` (por zona `fome_moderada`/`fruta_no_cenario` e janela,
  com as violações das regras urgentes do G-URG), `fracao_da_fruta` (a fração de X nas ofertas com X e outra fruta, por janela) e
  `dia_cruza_zero`. Os contrastes e o Holm são os da BANCADA-EXPERIMENTO.
- **Gates** (`tests/test_bancada_n6_n7.py`, 19 testes, ~15 s): **`iguais_frutas` com as mesmas ofertas** dos outros mundos das frutas (4
  donos × 2 sementes, sem e com genoma) e de todos os braços; efeito neutro em todo consumo; P0 lobos = P0 instinto byte a byte; **G1** de
  toda vida nova (P0, P1, P2, P2a, P3) e dos acoplados `sem_ensino`, que guardam as ofertas; **os braços do N6 e do N7 falham alto com o
  nó** (`braco_de`, `validar_config`, `Bancada.vida`), e a única trava é o `NOS_PENDENTES`; o desarranjo; **as medidas recuperam a
  resposta conhecida** em dados sintéticos; o prefixo das unidades sem colisão entre planos e fases.
- **Quando a memória e o pedido chegarem:** tirar a entrada do `NOS_PENDENTES`, ligar a memória/o pedido em `Bancada.politica` e a regra do
  mundo do pedido em `Bancada.vida`, estender o `sem_ensino` aos pedidos (plano do N7, 4.2) e pôr os pedidos em `FORA_DO_ORCAMENTO`.

## V2, K4-DONO-JULGA-FRUTA — o dono do P3 julga a fruta pelo efeito real (2026-10-05, `docs/TAREFA_V2_K4_DONO_JULGA_FRUTA.md`) — GATES PASSAM

Contrato K4 e decisão E7 de `docs/PLANO_ANALISE_V2_EXPERIMENTO_MAIOR.md` (seção 1) e decisão K-11 de `docs/PLANO_CALIBRACAO_CONJUNTA_V2.md`.
Infraestrutura, sem run de pesquisa nem faixa reservada; só as sementes dos testes. Mudaram `frutas.py`, `config.py`
(`ConfigJulgamentoFruta`) e `protocol.py` (o registro dela), mais `experiments/medir_k4_orcamento.py` (a medida e a receita da bancada);
`engine.py`, `AcaoPet`, `lobos.py`, `bancada_v2.py` (o chat D liga na rodada 10), os donos de `donos.py` e a web não. Interpretações em
`docs/REGISTRO_DESVIOS.md`.
- **O conhecimento** (`JulgadorFruta`): o efeito real de cada fruta, o mesmo que o informante do P2 recebe (`Bancada.efeitos_reais`:
  antes e, no mutável, depois de `tick_troca`, a mesma regra do `InformanteDoMundo`); fora da bancada, `JulgadorFruta.do_genoma` (o mesmo
  do `DonoInformante.do_genoma`). Cada consumo é julgado pelo efeito vigente no tick dele: > 0 elogia (a fruta boa), < 0 repreende (a
  ruim, o "mal" do P2), 0 (a neutra) nada.
- **O momento e o crédito:** o primeiro passo do dono depois do consumo. O motor só expõe os consumos com a chave
  (`ConfigJulgamentoFruta.ligada` → `estado()["consumos_frutas"]`). Com uma decisão a cada 15 ticks, a decisão anterior ao julgamento é
  sempre a de comer a fruta julgada, então a janela da v1 (elogio e bronca na última decisão) credita exatamente o consumo (teste). O
  sinal chega pelo `receber_acao_dono` de sempre.
- **Orçamento (a escolha registrada: `no_orcamento=True`, o padrão):** `DonoJulgaFruta(base, julgador)` põe os julgamentos novos na frente
  das ações do passo, até o máximo do passo, e o dono embrulhado (o atencioso) decide com o que sobra; o canal fecha o mesmo orçamento.
  Medida (`python experiments/medir_k4_orcamento.py` → `artifacts_v2_k4/orcamento.json`; P3 atencioso, ponto T3, 14 dias, orçamento 224,
  sementes 101…505, só mecanismo): o julgamento gasta em média 32,8 (casado), 39,6 (descasado) e 29,8 (mutável) ações por vida, e o
  feedback da tarefa cai de 151,4 para 124,0, de 150,8 para 119,4 e de 150,6 para 126,6. O cuidado de necessidade (alimentar, limpar,
  brincar) também cai de 72,6 para 67,2, 73,2 para 65,0 e 73,4 para 67,6, mas **não por falta de vaga** (em nenhum passo o julgamento
  tomou a vaga de um cuidado; nada descartado): elogiado pela fruta boa, o pet come mais fruta e precisa de menos comida do dono.
  **A alternativa** (`no_orcamento=False`): o julgador entra por `simular_vida_frutas(..., julgador=)`, logo depois das ações do dono do
  passo e fora do orçamento, como as informações do P2; a tarefa fica intacta. Decisão do Matheus.
- **Gates** (`tests/test_k4_dono_julga_fruta.py`, 14 testes, ~50 s): **a vida de hoje byte a byte**: 168 vidas (a bancada nos três mundos
  das frutas, P0 a P3, 4 donos, sementes 101 e 202; o `simular_vida_frutas` com instinto e lobos, sem nada, com o informante e com o dono
  que pede) iguais a `tests/gabaritos/k4_vidas_de_hoje.json`, gravado antes da mudança num commit próprio; a chave ligada com o dono de
  sempre = a vida da bancada; **o julgamento segue o efeito real vigente** (o efeito que o motor aplicou em cada consumo, dos dois lados
  da troca do mutável), um por consumo, no passo seguinte, abrindo as ações daquele passo no log; o crédito vai à decisão de comer;
  **o P2 e o P3 da mesma unidade conhecem o mesmo efeito** (os mesmos efeitos e a mesma troca, e o P3 repreende o que o P2 diz que faz
  mal); **G1** pelo replay e pelo `Bancada.rejogar`; o descarte no passo cheio; a alternativa fora do orçamento; os erros de uso.
- **Para o chat D:** `experiments/medir_k4_orcamento.py` tem a receita: `julgador_da_vida` (o conhecimento pelos efeitos reais da
  bancada), `fabrica_motor_com_julgamento` (a `fabrica_motor` das frutas com `cfg_julgamento`) e `vida_p3_com_julgamento` (o
  `DonoJulgaFruta` em volta do dono do P3, no `simular_vida_mundo`). Fora do orçamento, a regra do mundo teria de aceitar elogio e
  bronca (hoje o `simular_vida_mundo` só aceita os eventos de `FORA_DO_ORCAMENTO`). O acoplado `sem_ensino` do P3 já tira esses
  julgamentos (são `elogiar`/`repreender`). Depois de ligar, o `K4_DONO_JULGA_FRUTA` do orquestrador do experimento maior vira `True`.

## V2, CANAIS-REFORCO — o sinal da consequência separado por canal, com o mesmo total (2026-10-05, `docs/TAREFA_V2_CANAIS_REFORCO.md`) — GATES PASSAM

Etapa C4 do `docs/ROADMAP_V2.md` (revisão 3); hipótese H-R2 de `docs/research/digibrain/mechanisms/reinforcement.md`; decisão K-6 de
`docs/PLANO_CALIBRACAO_CONJUNTA_V2.md`. Só constrói os canais, para a ablação "canais × escalar" da validação única. Só testes de mecanismo,
só as sementes dos testes (11, 101, 202). Só `lobos.py` e `config.py` mudaram. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **Chave:** `ConfigConsequencia.canais_ligados` (False, PROPOSTO, `lobos.PARAMETROS_CONSEQUENCIA_N3`). Desligada, o escalar de sempre,
  byte a byte. Nenhum outro parâmetro novo; a rota de cada canal é constante do código (`lobos.ROTA_CANAIS`).
- **Os canais:** um por drive do sinal (`lobos.CANAL_DO_DRIVE`): fome, higiene e energia (o N3) e, quando o pet come fruta com a E2, o
  humor. Δ_i = falta_i(antes)² − falta_i(depois)² (D é a soma deles). **Contrato K-6, mesmo total:** a parte de cada canal sai por
  arredondamento telescópico sobre as somas parciais, f_i = div_arred(g·(Δ_1 + … + Δ_i), S) − div_arred(g·(Δ_1 + … + Δ_(i−1)), S), então a
  soma dos canais é exatamente o escalar div_arred(g·ΣΔ, S), em inteiros (`lobos.sinal_por_canal`); cada canal fica a no máximo 1 da sua
  conta isolada. O aprendiz confere a soma contra o escalar em toda decisão e falha alto se diferir (`Aprendiz._creditar_canais`).
- **O que cada canal credita** (`ROTA_CANAIS`, uma rota por canal, nenhum canal creditado duas vezes): fome, higiene e energia → **corpo**,
  a tabela do lobo de decisão (a regra); humor → **fruta**, os pesos que leem a identidade da fruta (a escolha da fruta, a informação do
  N5, o pedido do N7 e a presença da FRUTA-NO-CENARIO). No escalar, f_S vai a todos eles. A nutrição é igual em todas as frutas (F6), então
  o que distingue as frutas chega pelo humor.
- **Ponto de entrada da H-R4** (`Aprendiz._sensibilidade_canal`): devolve S para todo canal, sem uso; uma sensibilidade diferente quebraria
  o total e entra só com o desenho da H-R4. **Fora:** os canais não andam com o traço (`traco_decisoes` > 0 falha alto; o T3 não tem traço);
  o sinal do dono (P3) continua escalar.
- **Gates** (`tests/test_canais_reforco.py`, 20 testes, ~90 s): **G2**, canais desligados = a vida de hoje: 192 vidas (pontos L1 e T3 com
  `w0_info` S/2; padrão, bola e os três mundos das frutas; P0 a P3; 2 donos; 2 sementes) iguais a
  `tests/gabaritos/canais_reforco_vidas_de_hoje.json`, gravado com o código da main antes da mudança (`tests/gabarito_canais_reforco.py`,
  commit próprio); **total igual ao escalar** em 3000 pares de estados por ganho (0, 1, 4, 16, 64) e decisão a decisão em vidas do P1 e do
  P2 (descasado, mutável, casado, padrão; L1 e T3); **conta exata**: uma fruta que mata a fome e piora o humor (fome 0,4 → 0,7, humor 0,8 →
  0,7, ganho 4) dá fome +1104 e humor −204 (escalar +900); pelos canais o comer recebe +1104 e a fruta escolhida desce, pelo escalar os dois
  recebem +900 e a fruta sobe; **G1** com os canais, pelo texto do log; o P0 e o P3 não mudam com os canais ligados; o P1 muda.
- **Para a bancada (chat D):** `"consequencia": {"canais_ligados": true}` na config (`bancada_da_config`), ou
  `Bancada(..., cfg_consequencia=replace(CONFIG_CONSEQUENCIA, canais_ligados=True))`. A `PoliticaDoBraco` já passa a `ConfigConsequencia` a
  `observar_consequencia`; nada mais muda na bancada. Os canais só agem nos braços que aprendem pela consequência (P1, P2, P2e, P2a e, quando a bancada o montar, o P1+ped).
- **Não mudou:** `engine.py`, `AcaoPet`, o mundo, a bancada, o bandit, a web.

## V2, BANCADA-LIGA-N6-N7 — a memória e o pedido ligados na bancada (2026-10-05, `docs/TAREFA_V2_BANCADA_LIGA_N6_N7.md`) — GATES PASSAM

Etapa C3 do `docs/ROADMAP_V2.md`: o cérebro (CEREBRO-N6-N7, #167) e o mundo do pedido (N7-MUNDO, #166) já estavam na `main`. Infraestrutura,
sem run de pesquisa nem faixa reservada; só as sementes dos testes. Só `experiments/bancada_v2.py` mudou (as medidas do #165 já estavam em
`digilab/metrics.py`); `engine.py`, `lobos.py`, `frutas.py` e a web não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **Fim do `NOS_PENDENTES`:** a tabela fica vazia (o lugar do K4 e dos canais, na rodada 10); os braços do N6 e do N7 rodam.
- **N6** (`cfg_lobos_do_braco`): M0, MR, MT e ME por cima do ponto (`cfg_lobos_do_ponto`), com o aprendizado do lobo de decisão desligado,
  `memoria_ligada`, o modo do braço (`relevante`, `recencia`, `embaralhada`), o ganho da config (`lobos.memoria_ganho`; o M0 sempre com 0) e,
  no ME, `memoria_permutacao = lobos.desarranjo_n6(semente)` (o `desarranjo_n6` da bancada confere que é o mesmo). Nos outros braços as
  chaves da memória e o `w0_pedido` voltam ao padrão: uma config com eles não muda nenhum braço antigo.
- **N7:** P0+ped, P1+ped e P3+ped com `DonoPedinte.da_semente(semente, cfg_pedido, bronca=...)` (a bronca só no P3+ped, o braço com pedido
  e fonte dono), pela regra do mundo (`RegraFrutasComPedinte`, depois das ofertas e da informação), a `ConfigPedido` ligada **só no motor
  dos braços com pedido** (`Bancada.cfg_pedido`) e o `w0_pedido` da config no cérebro. **Fora do orçamento:** os pedidos entram em
  `FORA_DO_ORCAMENTO` e o `contar_acoes` não os conta; as broncas do pedido são `repreender` no registro, vêm pelo canal do mundo (a regra
  declara `extras_fora_do_orcamento`) e saem da conta do dono pela contagem da regra (`VidaBancada.broncas`).
- **Filtros:** `sem_ensino` (e o `sem_ensino_sem_carinho`) tiram também os pedidos (as broncas saem com os sinais); `sem_pedido` tira só os
  pedidos (o controle P0<P0+ped:sem_pedido mantém os sinais do dono); `sem_ensino_sem_pedido` = `sem_ensino` (o nome do plano). O acoplado
  carrega as broncas da origem só quando o filtro não tira `repreender`.
- **Medidas** (no `medir`, blocos `n6` e `n7`, lidas das sondas que o cérebro grava no motivo; a decisão k cai no tick k × 15):
  - **N6:** as sub-decisões da fruta com a sonda contrafactual (`fruta.sonda_memoria`) dão `memoria_nas_subdecisoes` (G-CITA, cobertura,
    episódios decisivos, a fração sobre todas as decisões), conferida contra as contagens do cérebro (diverge, falha alto); a ocupação dos
    espaços por decisão; os marcos 1 e 2 exatos (todo consumo virou um episódio da mesma fruta, na mesma ordem).
  - **N7:** a fruta X da unidade; a deferência por zona e janela (dias 1–5, 6–10 e a extinção), com as violações das regras urgentes; a
    fração de X (também no acoplado de um braço com pedido, que o G-MARCA usa); as desobediências; o `w_pedido` no fim de cada dia (por
    replay até o dia, só quando o cérebro aprende) e o dia em que cruza o zero.
- **Gates** (`tests/test_bancada_liga_n6_n7.py`, 11 testes, ~2,5 min): **bracos antigos byte a byte** — as 312 vidas de
  `tests/gabaritos/bancada_liga_vidas_de_hoje.json` (P0 a P3, P2e, P2a; padrão, bola e os quatro mundos das frutas; pontos L1 e T3; os
  acoplados), gravado com o código da main **antes** (`tests/gabarito_bancada_liga.py`, commit próprio), e de novo com `memoria_ganho` e
  `w0_pedido` na config; **M0 = P0 nas decisões** (4 donos × 2 sementes × 3 mundos) e o M0 codifica todo consumo; **o pedido não muda o
  orçamento** (o dono gasta o orçamento exato; com `w0_pedido` 0 o P0+ped é o P0 com os pedidos no registro, e o acoplado sem eles é o P0);
  o pedinte é o do N7-MUNDO (um pedido logo depois de cada oferta de X); **o só cuidado do P3+ped tira pedidos e broncas e guarda as
  ofertas**; **G1** de toda vida nova e dos acoplados (MR → M0, MT, ME; P3+ped → P0 `sem_ensino` e → P3 `sem_pedido`; P0+ped → P0
  `sem_pedido`); **as medidas do N6 e do N7 saem de vidas reais** com valor finito; o `rodar` com os dois blocos.
- **Fumaça** (NÃO canônicas, sem artefato): `experiments/configs/bancada/fumaca_n6.json` (P0 e os quatro braços de memória no descasado, os
  acoplados do MR; 40 vidas em ~26 s) e `fumaca_n7.json` (P0, os três braços com pedido e o P3 no `iguais_frutas`, o só cuidado e o controle
  do pedido; 35 vidas em ~27 s), unidades com os prefixos `n6` e `n7`, ganho e `w0_pedido` S/2 só para as peças agirem.
- **Fora:** as tabelas braço × condição não ganharam as medidas do N6 e do N7 (ficam no `medidas.json`; o orquestrador da calibração
  conjunta lê de lá); o K4 e os canais são a rodada 10.

## V2, BANCADA-K4-CANAIS — o K4 fora do orçamento, os canais por braço, as ablações da K-7 e as faixas da comparação (2026-10-05, `docs/TAREFA_V2_BANCADA_K4_CANAIS.md`) — GATES PASSAM

Rodada 10 do `docs/ROADMAP_V2.md`; pré-requisito da calibração conjunta (K2). Infraestrutura, sem run de pesquisa nem faixa reservada; só as
sementes dos testes. Só `experiments/` mudou (a bancada e o orquestrador do experimento maior); `engine.py`, `lobos.py`, `frutas.py`,
`metrics.py` e a web não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **K4, fora do orçamento** (decisão do Matheus, 2026-10-05): com a chave `"julgamento_fruta": true` na config (`Bancada.julgamento_fruta`,
  desligada por padrão), o dono dos braços com fonte dono (o P3, e o P3+ped) nos mundos das frutas julga cada consumo pelo efeito real
  vigente (`Bancada.julgador`: `JulgadorFruta` do #170 com os `efeitos_reais` da bancada, os mesmos do informante do P2, e a troca do
  mutável), pela regra do mundo (`RegraFrutasComJulgador`, logo depois das ações do dono do passo, como no `simular_vida_frutas`). O motor
  desses braços expõe os consumos (`ConfigJulgamentoFruta(ligada=True, no_orcamento=False)`); o atencioso decide com o orçamento inteiro.
  Os julgamentos são `elogiar`/`repreender` aceitos só por essa regra (`extras_fora_do_orcamento`) e contados à parte
  (`VidaBancada.julgamentos`, como as broncas do pedido); o `sem_ensino` os tira; um filtro que tirasse só um dos dois falha alto.
- **Experimento maior:** `K4_DONO_JULGA_FRUTA = True`, e o orquestrador liga a chave na bancada: a predição 5 sai sem o aviso.
- **Canais por braço** (#169): os braços seguem a chave `"consequencia": {"canais_ligados": ...}` da config; um braço pode fixá-los
  (`Braco.canais`). **Ablações da K-7** (`PLANO_CALIBRACAO_CONJUNTA_V2`, seções 1 e 4.1), nomeadas na bancada: **`P1c`** (o P1 completo:
  memória relevante com o ganho da config e canais), **`P1c-mem`** (sem memória: memória ligada com ganho 0, o "g = 0" do plano) e
  **`P1c-can`** (escalar: canais desligados). Os braços de antes não mudam.
- **Faixas:** 28101…28505 e 29101…29505 (a comparação dos cérebros, C-8) em `FAIXAS_RESERVADAS` e `BASES_COMPARACAO`; as do N11
  (16101…17505) ficam marcadas como substituídas pela C-8.
- **Gates** (`tests/test_bancada_k4_canais.py`, 10 testes, ~1 min): **os braços de antes byte a byte** — as 352 vidas de
  `tests/gabaritos/bancada_k4_vidas_de_hoje.json` (P0 a P3, P2e, P2a, os do N6 e do N7; os quatro mundos das frutas e o padrão; L1 e T3 com
  informação, memória e pedido na config; os acoplados), gravado com o código da main **antes** (`tests/gabarito_bancada_k4.py`, commit
  próprio); com a chave do K4 os outros braços não mudam, e com os canais na config o P0 e o P3 não mudam; **no P3 com o K4** o orçamento do
  dono fecha igual ao do P3 de hoje, há um julgamento por consumo não neutro pelo efeito que o motor aplicou (dos dois lados da troca do
  mutável), o julgamento chega ao aprendiz e o conhecimento é o do P2; **o `sem_ensino` tira os julgamentos e guarda as ofertas**; o K4 com
  o pedido no P3+ped; as ablações com os canais e a memória certos; **G1** de toda vida e acoplado novos; `rodar` com o K4 e as ablações.
  `tests/test_experimento_maior.py` passa a esperar o K4 ligado.
- **Fumaça** (`experiments/configs/bancada/fumaca_k4_canais.json`, NÃO canônica, sem artefato: P0, P1, as três ablações e o P3 com o K4 no
  descasado e no mutável, o só cuidado do P3; ponto T3, ganho da memória S/2): 70 vidas em ~33 s.
- **Para o coordenador:** pela tabela da seção 1 do plano da calibração conjunta, o bloco principal da K2 tem memória em P1, P2 e P3 e
  canais em P1 e P2; na bancada as chaves são do braço, e os P1, P2 e P3 de hoje não têm memória nem canais fixos. A K2 precisa de braços
  nomeados para o "cérebro A montado" (como o `P1c`) ou de uma decisão sobre isso.

## V2, CEREBRO-C — o DigiBrain C, Fly-like (2026-10-05, `docs/TAREFA_V2_CEREBRO_C.md`) — GATES PASSAM

Etapa C5 do `docs/ROADMAP_V2.md`; contrato da seção 1 de `docs/PLANO_ANALISE_V2_COMPARACAO_CEREBROS.md` (C-1 a C-10); família "Fly-like" de
`docs/research/digibrain/synthesis/brain_comparison.md`. **Sem calibração e sem run**; só as sementes dos testes. Mudaram
`digilab/policies/cerebro_c.py` (novo), `digilab/config.py` (`ConfigCerebroC`) e `experiments/cerebro_c_bancada.py` (novo); **`lobos.py` e
`bancada_v2.py` não** (o C só importa funções públicas do A e a sonda do instinto). "Inspirado em" fala do nosso cérebro, não da mosca.
Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **O herdado (C-1):** a regra do instinto e os candidatos (`lobos.impulsos`) e o prior do A (`PoliticaLobos._tabela_prior`, a mesma
  ativação em ponto fixo). O C aprende por cima: peso efetivo = instinto + aprendido / S (+ o piso, só com o aprendizado ligado).
- **Circuitos por classe de estímulo**, com células binárias esparsas, fixas e herdadas (faixas e conjunções): **corpo** (fome, higiene,
  energia, humor, saúde, sujeira, dormindo, hora: 22), **social** (o tempo sem cuidado e a conjunção com a hora: 15) e **objeto** (bola,
  cada fruta, fome × fruta, energia × bola: 16). Na escolha da fruta, a identidade de cada fruta e o que o dono informou dela (bem, mal: 5).
- **Saída e competição:** cada célula ativa tem, por ação, um compartimento **apetitivo** e um **aversivo** (0 ≤ w ≤ teto); L_a = soma de
  apetitivo − aversivo nas células ativas; os comportamentos competem pelo sorteio proporcional de sempre. **Memória dependente de
  estado:** o apetitivo de comer só se expressa na medida da fome (gate = S − arred(fome × S)).
- **Canais de reforço paralelos** (no C, a arquitetura; no A, a chave `canais_ligados`): a consequência por drive
  (`lobos.sinal_homeostatico_canais`/`_fruta_canais`; a soma é o escalar da bancada, conferida em toda decisão): fome, higiene e energia
  vão ao corpo e ao social; o humor (a E2) vai ao objeto e à escolha da fruta; o dono (janela da v1 do A) vai a todos.
- **Plasticidade local:** só as sinapses das células ativas, para a ação executada, no compartimento do sinal: += div_arred(passo × |f|, S),
  cortado no teto. Nada depende da probabilidade da política (diferente da regra do A). Decisão com um candidato só não aprende.
- **Sonda do aprendido** (contrato 1.1): `motivos[-1]["sonda"]` (a ação com o aprendido zerado e o mesmo u) e, na fruta,
  `["fruta"]["sonda"]` (sem o aprendido; sem a informação).
- **Capacidade (C-3):** 752 parâmetros aprendíveis (53 células × 7 ações × 2 compartimentos + 5 × 2), **0,986×** os 763 do A no ponto da K2.
- **Parâmetros:** `ConfigCerebroC` (registro em `cerebro_c.PARAMETROS_CEREBRO_C`, todos PROPOSTOS). Livres para o adendo: `passo`, `teto`
  e `w0_info`; os do crédito do dono são os do A; os cortes das faixas são estrutura (os limiares do instinto).
- **Gates** (`tests/test_cerebro_c.py`, 23 testes, ~20 s): **aprendizado desligado = instinto byte a byte** (pela bancada: P0 no padrão, na
  bola e nos quatro mundos das frutas, 4 donos × 2 sementes; P1 e P3 desligados = o P0 do instinto; 3000 observações aleatórias decisão a
  decisão, ação e rng); **G1** (P0, P1, P2, P2e, P2a, P3 e o acoplado só cuidado, do texto do log, estado interno incluído); **capacidade
  na faixa**; **a sonda reproduz a decisão de um gêmeo zerado** com o mesmo u (decisão e fruta); **aprende com a consequência, conta
  exata**: a fruta que derruba o humor 0,8 → 0,7 dá o canal humor −204, cada uma das duas células do objeto ganha 13 no aversivo de comer e
  o peso de comer com ela sozinha cai exatamente 26/1024, sem mexer na outra fruta; a memória apetitiva só se expressa com fome; a
  informação "mal" que fez mal passa a pesar contra qualquer fruta informada "mal"; o dono chega aos três circuitos; os canais somam o
  escalar (falha alto se não); N6 e N7 recusados (C-2).
- **Para o chat D:** `experiments/cerebro_c_bancada.py` (`BancadaComC`) é a receita: `CEREBROS` ganha `cerebro_c` e, em `Bancada.politica`,
  `PoliticaDoBraco(PoliticaCerebroC(cfg, cc, cb, cf), braco, cfg_consequencia)`, com o aprendizado desligado no P0. O resto da bancada
  (motor, replay, medidas) lê os ganchos e o estado interno pelos mesmos nomes.

## V2, BANCADA-MONTAGEM — a chave `montagem` da bancada: o cérebro A montado em cada braço (2026-10-05, `docs/TAREFA_V2_BANCADA_MONTAGEM.md`) — GATES PASSAM

Pré-requisito da run da calibração conjunta (K2, chat B). Decisão do Matheus (2026-10-05, opção 1). Infraestrutura, sem run de pesquisa nem
faixa reservada; só as sementes dos testes. Só `experiments/` mudou (a bancada e o orquestrador do experimento maior); `engine.py`,
`lobos.py`, `frutas.py`, `cerebro_c.py` e a web não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **A chave:** `"montagem"` na config da bancada (`Bancada.montagem`, `MONTAGENS`). **`"simples"`** é o padrão (e o que vale sem a chave):
  a bancada de antes, byte a byte. **`"completa"`** monta em cada braço o cérebro A da seção 1 do `docs/PLANO_CALIBRACAO_CONJUNTA_V2.md`,
  pela fonte do braço (`MONTAGEM_COMPLETA`, `braco_montado`, `Bancada.braco`):

  | braço (fonte) | memória | canais | `w0_info` | `w0_pedido` |
  |---|---|---|---|---|
  | P0 (nenhuma) | — | desligados | 0 | 0 |
  | P1 (consequência) | relevante, ganho `g` | ligados | 0 | só com pedido |
  | P2, P2e, P2a (informação) | relevante, ganho `g` | ligados | o da config | só com pedido |
  | P3 (dono) | relevante, ganho `g` | desligados | 0 | só com pedido |

  `g`, `w0_info` e `w0_pedido` vêm da chave `"lobos"` da config (o que a K2 varre). A memória só existe nos mundos das frutas (fora deles o
  cérebro não a tem); os canais valem em todo mundo. O `w0_pedido` fica nos braços com pedido (P0+ped, P1+ped, P3+ped: "só age onde há
  pedido", o bloco N7); nos braços principais o motor não tem pedido e ele é 0.
- **O que o braço fixa vence a montagem:** o N6 (M0 a ME) e as ablações da K-7 ficam o que são. Por isso, na completa, **o `P1c` é o P1**
  (só o rótulo muda), **o `P1c-mem` é o P1 completo com g = 0** e **o `P1c-can` é o P1 completo sem os canais**. O P1+ped e o P3+ped ganham
  as peças do P1 e do P3 mais o pedido; o P0+ped e o N6 são os de antes sem o `w0_info`.
- **Na simples, o de antes:** o `w0_info` da config vale em todo braço (com ele, o P1 e o P3 têm o peso da informação no estado interno) e
  nenhum braço principal tem memória ou canais fixos. É o motivo da completa.
- **Medidas:** as do N6 (`n6` no `medidas.json`) saem em todo braço com memória montada (P1 a P3 na completa).
- **Experimento maior:** `MONTAGEM = "completa"` em `run_v2_experimento_maior.py`; `config_da_bancada` passa `"montagem": "completa"` e o
  `resumo.json` grava em `contratos`. O orquestrador da K2 (chat B, `v2-k2-calibracao-conjunta`) usa a mesma chave, com o mesmo valor, nas
  configs da K2 e da validação.
- **Gates** (`tests/test_bancada_montagem.py`, 17 testes, ~8 min): **simples e sem chave byte a byte** — as 516 vidas de
  `tests/gabaritos/bancada_montagem_vidas_de_hoje.json` (P0 a P3, P2e, P2a, os do N6, do N7 e da K-7; os quatro mundos das frutas e o
  padrão; L1, T3 com as peças na config, e T3 com as peças, os canais e o K4; os acoplados; as bancadas pela config), gravado com o código da
  main **antes** (`tests/gabarito_bancada_montagem.py`, commit próprio), com `"montagem": "simples"`, e as 120 primeiras de novo sem a chave;
  **na completa o P0 é o instinto byte a byte** (resumo do motor, nos quatro mundos das frutas e no padrão, com as peças, os canais e o K4
  na config) e o estado interno é o do P0 sem as peças; **cada braço com exatamente as peças da tabela no estado interno** (memória e ganho,
  canais, `peso_info`, `peso_pedido`), com os canais da config ligados ou não; **o P3 sem canais e o `w0_info` só nos P2** em todo mundo; o
  padrão sem as peças das frutas; **as ablações são o P1 completo menos uma peça** (o P1c = o P1 byte a byte; o P1c-mem = o P1 de uma config
  com g = 0; o P1c-can = o P1 com os canais desligados); o N6 e o P0+ped = os de antes sem o `w0_info`; **G1** de 82 vidas e 57 acoplados na
  completa; `rodar` com a completa (o bloco `n6` nos P1 a P3); o experimento maior usa a completa.
- **Fumaça** (`experiments/configs/bancada/fumaca_montagem.json`, NÃO canônica, sem artefato: P0, P1, P2, P2e, P2a, P3 e as duas ablações
  nos três mundos das frutas, o só cuidado do P2 e do P3; T3, K4, g, `w0_info` e `w0_pedido` S/2): 150 vidas rejogadas bit a bit em ~4 min.
- **Fora:** o cérebro C (`experiments/cerebro_c_bancada.py`) não lê a montagem: ela é do cérebro A.

## V2, CEREBRO-B — o DigiBrain B, CfC + ator-crítico + elegibilidade (2026-10-06, `docs/TAREFA_V2_CEREBRO_B.md`) — GATES PASSAM

Etapa C5 do `docs/ROADMAP_V2.md`; contrato da seção 1 de `docs/PLANO_ANALISE_V2_COMPARACAO_CEREBROS.md` (C-1 a C-10); família do NORNBRAIN
em `docs/research/digibrain/synthesis/brain_comparison.md`. **Sem calibração e sem run**; só as sementes dos testes. Mudaram
`digilab/policies/cerebro_b.py` (novo), `digilab/config.py` (`ConfigCerebroB`) e `experiments/cerebro_b_bancada.py` (novo); `lobos.py`,
`cerebro_c.py` e `bancada_v2.py` não. "Inspirado em" fala do nosso cérebro, não do NORNBRAIN (CORPUS). Interpretações em
`docs/REGISTRO_DESVIOS.md`.
- **O herdado (C-1):** a regra do instinto e os candidatos (`lobos.impulsos`) e o peso de cada um (o prior do A). O B aprende por cima:
  w_a = w_instinto(a) × exp(z_a), com o logit aprendido z iniciado em zero (exp(0) = 1 exato: no começo, e sempre com o aprendizado
  desligado, o instinto byte a byte).
- **A célula CfC** (ponto flutuante, `math.exp`/`tanh`): entrada x (as 9 do A sem o viés, bola, fruta e a presença de cada fruta: 14) e o
  estado oculto anterior; F, G, K = tanh(W v + b); s = σ(−F·dt); h = s·G + (1 − s)·K; 9 ocultos. Os pesos da célula começam sorteados por
  uma rng própria e fixa (herdada, igual em todo pet); as cabeças e o crítico, em zero. O estado oculto é a memória do B (C-2).
- **Ator, fruta e crítico:** z = A h + b nos candidatos; a escolha da fruta pesa incentivo × exp(q_f), q_f = F_f·h + b_f + θ_info·info_f
  (θ_info começa em `w0_info`; com 0, a escolha do `MotorFrutas` byte a byte); V(h) = C·h + c0.
- **O crédito:** o gradiente do log da escolha (ação e, comendo com duas frutas ou mais, a fruta) em todos os parâmetros do ator, a
  célula por retropropagação de um passo; traço e ← λe + g a cada decisão; a cada sinal r, δ = r − V(h da decisão), ator += taxa_ator·δ·e,
  crítico += taxa_critico·δ·h. Sinais das fontes da bancada: consequência r = f_S/S (o escalar da bancada, conferido; a E2 pela
  `fruta_comida`); dono com a janela da v1 do A (elogio e bronca pelo traço; o chamado pelo gradiente da decisão dele).
- **Sonda do aprendido** (contrato 1.1): `motivos[-1]["sonda"]` (a ação com z = 0 e o mesmo u) e `["fruta"]["sonda"]` (sem o aprendido;
  sem a informação).
- **Capacidade (C-3):** 759 parâmetros (célula 3 × (9 × 23 + 9) = 648; ator 7 × 10 = 70; fruta 3 × 10 + 1 = 31; crítico 10), **0,995×**
  os 763 do A no ponto da K2.
- **Parâmetros:** `ConfigCerebroB` (registro `cerebro_b.PARAMETROS_CEREBRO_B`, todos PROPOSTOS). Livres para o adendo: `taxa_ator`,
  `taxa_critico`, `lambda_elegibilidade` e `w0_info`; estrutura: `n_ocultos`, `delta_t`, `semente_pesos`, `escala_inicial`,
  `limite_logit`; o ponto fixo do prior, a percepção e o crédito do dono são os do A.
- **Gates** (`tests/test_cerebro_b.py`, 26 testes, ~1,5 min): **aprendizado desligado = instinto byte a byte e = o P0 dos lobos** (pela
  bancada: os quatro mundos das frutas e a bola, 4 donos × 2 sementes; o padrão; P1 e P3 desligados = o P0 do instinto; 3000 observações
  decisão a decisão, ação e rng); com o aprendizado ligado e nada aprendido, ainda o instinto; **G1** (P0, P1, P2, P2e, P2a, P3 e os
  acoplados só cuidado, do texto do log, estado interno incluído: pesos, oculto, traço, motivos); **capacidade na faixa**; **a sonda
  reproduz a decisão de um gêmeo com a parte aprendida zerada** (decisão e fruta, mais a fruta sem a informação); **aprende com a
  consequência, conta exata do primeiro passo** (a fruta que derruba o humor 0,8 → 0,7: r = −204/1024, δ = r, b_comer = taxa·δ·(1 − p),
  os outros candidatos taxa·δ·(−p), o viés do crítico taxa_critico·δ) e **a tendência** (p(comer | só a fruta) cai se ela faz mal e sobe
  se faz bem); a informação inata e a aprendida na escolha da fruta; o dono pelo traço; o chamado pela latência; a memória recorrente; o P0
  não aprende, P1/P2/P3 aprendem, cada um só pela própria fonte; N6 e N7 recusados (C-2).
- **Custo:** ~1,6 s por vida de 14 dias com o replay conferido (o A, ~2,4 s; medição informal nesta máquina, sem artefato).
- **Para a bancada:** `experiments/cerebro_b_bancada.py` (`BancadaComB`), a mesma receita do C: `CEREBROS` ganha `cerebro_b` e, em
  `Bancada.politica`, `PoliticaDoBraco(PoliticaCerebroB(cfg, cfg_b, cb, cf), braco, cfg_consequencia)`, com o aprendizado desligado no P0.
- **O adendo de calibração** (4 parâmetros, 10 pontos de 12, ~660 vidas, regras de estabilidade e de manipulação) está no corpo do PR,
  para o coordenador conferir antes de qualquer run.

## V2, K2-CALIBRACAO-CONJUNTA — a calibração conjunta do cérebro A (2026-10-06, `docs/TAREFA_V2_K2_CALIBRACAO_CONJUNTA.md`) — RUN FEITA; N DA VALIDAÇÃO ACIMA DO TETO, DECISÃO PENDENTE

Plano `docs/PLANO_CALIBRACAO_CONJUNTA_V2.md` (K-1 a K-11). Uma run, nas sementes de calibração 14101…14505 (K = 4, 20 unidades), 14
dias, atencioso, ponto T3, `"montagem": "completa"` (#178) e o K4 ligado; 4 h 12 min. Números de `artifacts_v2_calibracao_conjunta/`;
relatório `docs/RESULTADO_V2_CALIBRACAO_CONJUNTA.md`. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **Código:**
  - `experiments/run_v2_calibracao_conjunta.py`: as cinco etapas pela bancada, cada uma com a regra de escolha do plano e a de reserva;
    nenhuma regra lê a `taxa_fruta_ruim` nem um contraste entre braços;
  - recusa a validação e recusa a calibração sem as peças da bancada (`pecas_pendentes`);
  - `PoliticaLobos.escolha_sem_info`: a sonda da etapa C, só leitura;
  - testes: `tests/test_calibracao_conjunta.py`, 11.
- **Ponto:** `g` = S/2 (A1 fechou), `w0_pedido` = S/4 (A2 não fechou: nenhum conflito na `fome_moderada`), ganho 4 (B não fechou: todo
  ganho com vida no teto; a reserva escolhe o 4, razão da deriva 2,72), `w0_info` = S/4 (C fechou).
- **Piloto:** contratos K1–K9 passam; Δ 0,199 (N6 0,194; N7 0,202); 12,3 s por vida.
- **N da validação: 191.815 (~28.760 h), acima do teto de 12 h.** O `p3_consumos` é medido em consumos e recebe o Δ de taxa. Os outros
  cinco ficam no piso de 5, com poder simulado entre 0,73 e 0,77 em três deles. Alternativas em `alternativas_n.json`; a recomendada (Δ do
  p3 na escala dele e N pela simulação) dá N 30, ~4,5 h. A validação não roda sem decisão do Matheus (seção 5.3.6).

## V2, V1-VALIDACAO-UNICA — a config da validação única e o orquestrador pronto (2026-10-06, `docs/TAREFA_V2_V1_VALIDACAO_UNICA.md`) — PRONTA, NÃO RODADA

Parte 1 da tarefa: a config e os ajustes do orquestrador, testados só com fumaça nas sementes dos testes. **A run nas sementes de validação
(15101…15505) espera o sinal verde do coordenador** (os adendos do `docs/PREDICOES_V2.md`; um adendo 3 pode pedir a medida em três
durações de vida). Plano `docs/PLANO_ANALISE_V2_EXPERIMENTO_MAIOR.md`, adendos 1 e 2. Interpretações e a run parada antes da tarefa em
`docs/REGISTRO_DESVIOS.md`.
- **Config** (`experiments/configs/v2_experimento_maior/validacao.json`): 30 unidades das bases 15101…15505 (K = 6), 14 dias, orçamento
  224, atencioso, ponto T3, o ponto da K2 (`g` S/2, `w0_pedido` S/4, `w0_info` S/4, ganho 4, canais ligados;
  `artifacts_v2_calibracao_conjunta/escolha.json`). A montagem completa e o K4 vêm do orquestrador. Δ 0,1986, Δ do p3 17,5 consumos,
  Δ_N6 0,1935 e Δ_N7 0,2023 (`adendo_opcao_a.json`). Blocos ligados. Um teste confere a config contra os artefatos da K2.
- **Os blocos da seção 4** (`"blocos": true`, `BLOCOS`, `analisar_blocos`), cada um numa run própria da bancada, nas mesmas unidades: P2a,
  ablações da K-7, N6 (MR e os acoplados M0, MT, ME), N7 (P0, P0+ped, P1+ped, P3+ped, P3 e o só cuidado do P3+ped). Com o principal e o
  padrão, os 44 por unidade. Saem em `blocos.json`: N6 (Holm de G-CAUSAL, G-REC, G-EMB, G-CITA, G-M1/G-M2, G5; G-M3 não medido), N7 (Holm
  de G-EROSAO, G-MARCA, G-MARCA-E, G-ARB, G-URG, G5; G-MARCA e G-MARCA-E declarados subpotenciados), ablações e o N5 descritivo.
- **Adendo 2 no orquestrador:** cada contraste tem o Δ na escala da sua medida (o p3 em consumos, `delta_p3`, obrigatório na validação,
  como o `delta_n6`/`delta_n7` com blocos). O N vem do poder simulado: o `tamanhos` faz a busca, e a função passou da K2 para cá. Das 20
  unidades do piloto da K2 ela reproduz N = 30 e o p3 a 0,862 (teste); a fórmula dava 25. Na validação o resumo grava o poder simulado de
  cada primário no N da run, só descritivo.
- **Testes** (`tests/test_validacao_blocos.py`, 5): a config é a do adendo 2; o tamanho com o Δ por medida; o N simulado reproduz o
  adendo; a busca sem poder até o teto; a fumaça com os blocos (44 × 2 vidas, todas gravadas e rejogadas, `blocos.json` e o tamanho no
  `resumo.json`). Os da K2 e do experimento maior seguem passando.
- **Para rodar** (depois do sinal verde): `python experiments/run_v2_experimento_maior.py --config experiments/configs/v2_experimento_maior/validacao.json --saida artifacts_v2_validacao_unica`,
  ~4,5 h pela estimativa da K2 (o bloco principal e os blocos; a K2 mediu 12,3 s por vida). Resultado depois em `docs/RESULTADO_V2_VALIDACAO_UNICA.md`.

## V2, CALIBRACAO-CEREBRO-B — a calibração do cérebro B (2026-10-06, `docs/TAREFA_V2_CALIBRACAO_CEREBROS_B_C.md`) — RUN FEITA; O B NÃO FECHA ("não aprende")

Rodada 11; plano `docs/PLANO_ANALISE_V2_COMPARACAO_CEREBROS.md`, adendo 1.1 (conferido pelo coordenador). Uma run, sementes de calibração
28101…28505 (K = 4, 20 unidades, prefixo `comparacao-cerebros`), 14 dias, atencioso, as peças comuns no ponto da K2 do A (ganho 4, T3, K4,
montagem completa); **660 vidas em 25 min** (tetos: 1260 vidas e 4 × a K2 do A). Números de `artifacts_v2_comparacao_cerebros/calibracao_B/`;
relatório `docs/RESULTADO_V2_CALIBRACAO_CEREBRO_B.md`. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **Código:**
  - `experiments/run_v2_calibracao_cerebro_b.py`: as etapas B-A a B-D em cadeia pela `BancadaComB`, com as grades e as regras do adendo
    (estabilidade: nenhuma vida com logit no limite e menor razão da deriva; manipulação: o menor `w0_info` com IC95 inferior > 0,069),
    o reaproveitamento dos pontos já rodados, o teto de vidas contado antes da run e o de tempo; o piloto do "não aprende" (seção 7) nas
    vidas do P1 no ponto escolhido; nenhuma regra lê a `taxa_fruta_ruim` nem contraste entre braços ou cérebros; recusa a validação;
  - `cerebro_b.py`: o estado oculto e o traço só andam com a decisão observada (a sonda da deriva não move a memória) e a contagem dos
    logits no limite; `bancada_v2.PREFIXOS_UNIDADES` ganhou `comparacao-cerebros` (seção 6.2 do plano);
  - testes: `tests/test_calibracao_cerebro_b.py` (13) e um novo em `tests/test_cerebro_b.py`.
- **Ponto:** `taxa_ator` 0,01, `taxa_critico` 0,1, `lambda_elegibilidade` 0,95, `w0_info` 0,5; as quatro regras fecham (nenhuma vida no
  limite do logit; razão da deriva 2,15 no escolhido; a informação decide 0,154 [0,130; 0,180] das escolhas de fruta com informação).
- **Piloto: o B não aprende.** No P1, a parte aprendida muda a escolha em 0,0077 [0,0065; 0,0089] das decisões, limite superior abaixo de
  0,01; a deriva no dia 14 é positiva (4,3 × 10⁻⁵ bit). Pela seção 7, o B sai da escolha M6 com esse motivo.
- **Descritivo:** a regra de estabilidade empurrou a cadeia para o ponto em que o B menos aprende; com a taxa do ator 0,1 o aprendido
  decidiria 20% das decisões. Nada foi recalibrado olhando o piloto.

## V2, CALIBRACAO-CEREBRO-C — a calibração do cérebro C (2026-10-06, `docs/TAREFA_V2_CALIBRACAO_CEREBROS_B_C.md`) — O C FECHA

Rodada 11; grades e regras do adendo 1.2 de `docs/PLANO_ANALISE_V2_COMPARACAO_CEREBROS.md`. Uma run nas bases 28101…28505 (K = 4, prefixo
`comparacao-cerebros`, 20 unidades), atencioso, 14 dias, o ganho da K2 do A (4); 540 vidas (teto 1260), 1 h (teto 4× a K2). Números de
`artifacts_v2_comparacao_cerebros/calibracao_C/`; relatório `docs/RESULTADO_V2_CALIBRACAO_CEREBRO_C.md`. Interpretações em
`docs/REGISTRO_DESVIOS.md`.
- **Código:** `experiments/run_v2_calibracao_cerebro_c.py`, que liga o C pela `BancadaComC` (a bancada e o `cerebro_c.py` não mudaram),
  e `experiments/configs/v2_calibracao_cerebro_c/` (calibração e fumaça). Testes: `tests/test_calibracao_cerebro_c.py`, 12.
- **Ponto: passo 128, teto 4096, `w0_info` 256.** As três etapas fecharam:
  - C-A: nenhuma vida no teto; razão da deriva 3,00, 1,89 e **1,61** (a ponta da grade);
  - C-B: o teto S prende as 60 vidas; 4S e 16S empatam e fica o menor;
  - C-C: fração decidida pela informação 0,202 [0,164; 0,242] no 256 (0,019 com `w0_info` 0).
- **Piloto, o "não aprende" (seção 7): não dispara.** Deriva no dia 14 0,0222 [0,0218; 0,0227]; a parte aprendida muda 0,324 das
  decisões. O C entra no M6.

## V2, P2D-P3I, parte A — o julgamento da fruta como informação (2026-10-06, `docs/TAREFA_V2_P2D_P3I.md`) — GATES PASSAM

Rodada 12; adendo 3, seção 3.3, de `docs/PLANO_ANALISE_V2_EXPERIMENTO_MAIOR.md`, e `docs/PREDICOES_V2.md`. Infraestrutura, sem run e sem
faixa reservada; só as sementes dos testes. Só `frutas.py` mudou (`config.py`, `lobos.py`, a bancada e a web não). A parte D (os braços na
bancada) é do chat D. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **`JulgadorFruta(..., saida=)`:** `"feedback"` (o padrão, o K4 de hoje: elogio e bronca) ou `"informacao"` (P2d e P3i).
  - Usa o mesmo conhecimento (os efeitos reais, com a troca do mutável) e o mesmo momento (o primeiro passo do dono depois do consumo).
  - Emite `informar_fruta_<f>_<bem|mal>` sobre a fruta consumida, uma por consumo, a neutra incluída ("bem", como o `DonoInformante`).
  - Só fora do orçamento, e só com o canal da informação ligado no motor.
  - `informadas` guarda (tick do julgamento, fruta, conteúdo, tick do consumo).
  - No `simular_vida_frutas`, essas informações contam em `informacoes`.
- **Gates** (`tests/test_p2d_p3i_mundo.py`, 14 testes, ~30 s):
  - **a saída `feedback` é a vida de hoje byte a byte:** as 144 vidas de `tests/gabaritos/p2d_p3i_vidas_de_hoje.json` (a bancada com o
    K4, montagem simples e completa; o `simular_vida_frutas` com o julgador fora do orçamento, com e sem o canal da informação), gravado
    antes num commit próprio (`tests/gabarito_p2d_p3i.py`);
  - **uma informação por consumo** no passo seguinte, com o conteúdo do efeito que o motor aplicou, nos três mundos e dos dois lados da
    troca do mutável, no P2 e no P3; o orçamento do dono fecha igual;
  - **a neutra sai como "bem"**;
  - **não chega ao aprendiz** (espião no `receber_acao_dono`), mas entra na percepção;
  - o conteúdo é o do informante do P2 da unidade;
  - **G1**;
  - os erros de uso.

## V2, V1-ADENDO3 — o orquestrador da validação com o adendo 3 (2026-10-06, `docs/TAREFA_V2_V1_ADENDO3.md`) — PRONTO, NÃO RODADO; ESPERA O P2D/P3I

Adendo 3 do `docs/PLANO_ANALISE_V2_EXPERIMENTO_MAIOR.md` no orquestrador do experimento maior. Só fumaça nas sementes dos testes. **A run
nas sementes 15101…15505 espera o PR da bancada do P2d e do P3i (chat D) e o sinal verde do coordenador.** Interpretações em
`docs/REGISTRO_DESVIOS.md`.
- **Custo** (`experiments/custo_adendo3.py` → `artifacts_v2_v1_adendo3/custo.json`):
  - parte do tempo por vida da K2 (12,27 s) e da razão entre durações medida nas sementes dos testes (7 dias 0,42 ×, 28 dias 2,57 ×);
  - a validação inteira fica em **6,13 h com 28 dias**, então a duração maior é 28.
- **Bloco de durações** (`"duracoes": {"menor": 7, "maior": 28}`):
  - P0 e P1 no descasado e no mutável, com as mesmas interações por dia, em runs próprias da bancada (`rodar_duracoes`);
  - em `duracoes.json`: a taxa da fruta ruim na janela da predição 2 e o ganho P0 − P1 por duração, com IC, e a forma da curva
    (`forma_da_curva`: crescente, ótimo interior, decrescente, platô ou indeterminado, regra no registro);
  - fora do Holm; a confusão da troca do mutável vai declarada.
- **P2d e P3i** (`"p2d_p3i": true`, obrigatório na validação):
  - P2 − P2d e P3 − P3i, com o multiconjunto das informações, em `p2d_p3i.json`;
  - até a bancada ter os braços, falha alto antes de qualquer vida.
- **Correção do #183:** os consumos até a metade dos blocos (P2a, P2d, P3i) usam a referência do P0 do bloco principal
  (`consumos_com_referencia`); antes saíam sem referência.
- **Leitura:** o `resumo.json` traz o apoio teórico de cada predição e a limitação do mutável (adendo 3, seções 3.2 e P-5), sem mudar a
  regra.
- **Testes:** `tests/test_adendo3.py` (a forma em dados com resposta conhecida, o orçamento por dia, a config, o custo refeito do artefato,
  a falha antecipada do P2d/P3i, a referência do P0, a fumaça com o bloco de durações).

## V2, P2D-P3I, parte D — os braços P2d e P3i na bancada (2026-10-06, `docs/TAREFA_V2_P2D_P3I.md`) — GATES PASSAM

Rodada 12; adendo 3, seção 3.3, de `docs/PLANO_ANALISE_V2_EXPERIMENTO_MAIOR.md`. Infraestrutura, sem run com faixa reservada; só as sementes
dos testes. Mudaram `experiments/bancada_v2.py` e `digilab/metrics.py` (`frutas.py`, que é da parte A, `lobos.py`, `engine.py` e a web
não). Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **Os braços** (`BRACOS`, nó `adendo-3`):
  - **P2d** (fonte `informacao`, `informacao="depois"`): o P2 com a informação depois do consumo. O informante é o `JulgadorFruta` da
    parte A com `saida="informacao"` (`Bancada.julgador`), no primeiro passo do dono depois de cada consumo; o informante da oferta sai.
    O P2d julga em todo mundo das frutas, com ou sem a chave do K4 (`Bancada.julga_fruta`).
  - **P3i** (fonte `dono`, `Braco.julgamento="informacao"`): o P3 com o julgamento do K4 saindo como informação; segue a chave
    `julgamento_fruta`, como o P3.
  - O conhecimento é o mesmo do P2 e do K4 (`efeitos_reais`, com a troca do mutável). `Bancada.saida_julgamento` dá a saída de cada vida.
- **Montagem completa:** o P2d tem as peças do P2 (memória, canais, `w0_info`); o P3i as do P3 (memória, sem canais) mais o `w0_info` da
  config (`recebe_informacao`). Na simples, como antes, o `w0_info` da config vale em todo braço.
- **Contagem:** as informações dos dois contam em `informacoes` (o log) e não em `julgamentos`; o orçamento do dono fecha igual. A
  `RegraFrutasComJulgador` só põe elogio e bronca fora do orçamento quando a saída é o feedback. O `sem_ensino` tira essas informações.
- **Medidas:** `frutas.multiconjunto_informacoes` por vida (`metrics.multiconjunto_informacoes`: `{"<fruta>/<conteúdo>": n}`), o mesmo que o
  orquestrador do adendo 3 lê de `frutas.informacoes`. O `bracos_p2d_p3i_faltando` do orquestrador fica vazio.
- **Gates** (`tests/test_bancada_p2d_p3i.py`, 17 testes, ~2,5 min):
  - **os braços de antes byte a byte:** as 378 vidas de `tests/gabaritos/bancada_p2d_p3i_vidas_de_hoje.json` (P0 a P3, P2e, P2a, N6, N7
    e K-7; os quatro mundos das frutas e o padrão; montagem simples e completa com o K4; os acoplados), gravado antes num commit próprio
    (`tests/gabarito_p2d_p3i_bancada.py`);
  - **o P2d sem o julgador é o P1 completo** (o mesmo log e as mesmas decisões; o estado interno só com o que o `w0_info` põe nele);
  - **o P3i com o K4 desligado é o P3** (na simples também o estado interno; na completa, o mesmo que acima);
  - **P2 e P2d com o mesmo conhecimento:** os efeitos e a troca do informante do P2; cada informação do P2d fala da fruta consumida, no
    primeiro passo do dono depois do consumo, com o conteúdo do efeito vigente, a neutra incluída, uma por consumo;
  - **P3 e P3i com a mesma regra de tempo:** o primeiro passo do dono depois de cada consumo (o P3 só os não neutros, como elogio ou
    bronca; o P3i todos, como informação), pelo mesmo conhecimento;
  - as informações contadas, fora do orçamento e no multiconjunto; o `sem_ensino` as tira e guarda as ofertas;
  - **G1** dos braços novos e dos acoplados; `rodar` com os braços novos.
  - `tests/test_bancada_v2.py` ganhou os dois braços na tabela de contrato.
- **Fumaça** (`experiments/configs/bancada/fumaca_p2d_p3i.json`, NÃO canônica, sem artefato: P0, P2, P2d, P3 e P3i no descasado e no mutável,
  o só cuidado dos dois novos; T3, K4, montagem completa, `w0_info` S/4): 70 vidas rejogadas bit a bit em ~50 s.

## V2, V1-LIGAR — a faixa de validação nova e a leitura do adendo 4 (2026-10-06, `docs/TAREFA_V2_V1_LIGAR.md`) — PRONTO, NÃO RODADO; O P2D/P3I ESPERA A BANCADA

Adendo 4 do `docs/PLANO_ANALISE_V2_EXPERIMENTO_MAIOR.md`. Só fumaça nas sementes dos testes. **A run espera o PR da bancada do P2d e do P3i
(chat D) e o sinal verde do coordenador.** Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **Faixa de validação: bases 30101…30505** (adendo 4.1; `bancada_v2.BASES_EXPERIMENTO_MAIOR`, a config da validação). A 15101…15505 fica
  **queimada** (`FAIXAS_QUEIMADAS`): a bancada recusa essas bases e sementes mesmo com plano.
- **A leitura do 4.2 no `resumo.json`:**
  - o limiar na leitura das durações (L-3);
  - os componentes da mudança e o valor separado da eficiência no mutável (predição 2);
  - a trajetória diária do `w_info` do P2e (L-4; `w_info_p2e.json`, num replay só por vida, conferido contra o `politica_no_tick`).
- **Testes:**
  - `tests/test_adendo4.py`: a faixa nova, a queimada recusada, a trajetória dia a dia;
  - a fumaça do bloco de durações em `tests/test_adendo3.py`, que agora confere também a leitura do 4.2.

## V2, VALIDACAO-UNICA — a validação única do experimento maior (2026-10-06, `docs/RESULTADO_V2_VALIDACAO_UNICA.md`) — FEITA

Uma run nas bases 30101…30505 (N = 30, K = 6), config `experiments/configs/v2_experimento_maior/validacao.json` sem mudança, adendos 1 a 4;
1680 vidas rejogadas do disco, 3 h 24 min. Números de `artifacts_v2_validacao_unica/` (as vidas fora do git). Interpretações em
`docs/REGISTRO_DESVIOS.md`.
- **Predições** (Holm de seis):
  - **1** confirma: o P1 come mais a fruta ruim que o P0 no casado, +0,078 [+0,048; +0,110];
  - **2** confirma no descasado (+0,076) e no mutável (+0,102), sem inclinação final, então não é "por duração";
  - **3** confirma pelo contraste (+11,4 consumos, p ajustado 0,03), **mas o P2 não difere do próprio só cuidado**: pela seção 5.1, o efeito
    não conta como ensino;
  - **4** inconclusiva: o P2e não piora no começo, e a recuperação (b) sozinha não basta;
  - **5** confirma pela equivalência (IC 90% dentro de ±Δ), com o IC 95% do P3 − P0 abaixo de 0.
- **Separação do cuidado:** em todo braço com dono, (a) e (b) falham; o só cuidado acoplado cuida pior que o original (malha aberta).
- **Secundários:**
  - **N6:** confirma (G-CAUSAL, G-REC e G-EMB com Holm; G-CITA 0,204).
  - **N7:**
    - G-EROSAO não rejeita;
    - G-MARCA e G-MARCA-E subpotenciados, com só 6 unidades com valor;
    - G-ARB e G-URG passam.
  - **Ablações:** a memória ajuda só no mutável (+0,014); os canais, nada.
  - **Durações:**
    - descasado em platô (P0, P1 e ganho);
    - no mutável o ganho decresce até 28 dias;
    - não há degrau entre 7 e 14 dias.
  - **P2d e P3i:**
    - o P2d chega à metade 12,8 consumos antes do P2;
    - o P3 come menos a fruta ruim que o P3i (−0,11 e −0,09).
  - **`w_info` do P2e:** cruza o zero em 30 de 30 unidades, até o dia 5.

## V2, COMPARACAO-A-C — a comparação dos cérebros A × C (2026-10-07, `docs/TAREFA_V2_COMPARACAO_A_C.md`) — FEITA; PELO M6, O C (POR POUCO)

Rodada 13. Plano `docs/PLANO_ANALISE_V2_COMPARACAO_CEREBROS.md`, seções 2 a 8 e adendos 1 e 2 (o 2 commitado depois do piloto e antes da
validação). O B não rodou (não fecha: "não aprende"). Números de `artifacts_v2_comparacao_cerebros/{piloto,validacao}/` (as vidas fora do
git); relatório `docs/RESULTADO_V2_COMPARACAO_CEREBROS.md`. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **Código:**
  - `experiments/run_v2_comparacao_cerebros.py`: a `BancadaAC` é a bancada do experimento maior (montagem completa, K4, canais) com o C a
    mais; a montagem não vale para o C. Os pontos são lidos dos artefatos da K2 e da calibração do C;
  - por unidade e condição: o P0 comum; A e C em P1, P2, P2e e P3; o só cuidado `sem_ensino`; o C no registro do P1 do A (descasado e
    mutável), com a JSD por dia;
  - legibilidade pela sonda do aprendido nos dois cérebros (no A, o sorteio com o prior e o mesmo `u`, conferido contra o `motivo_lobos`);
  - custo: µs por decisão, bytes de log por dia, estado sem os motivos;
  - a família CC-1/CC-2 com Holm de dois, os secundários, as predições por cérebro e a tabela do M6;
  - o N do adendo (fórmula e simulação, α/2); a validação recusa rodar de novo; `--reanalisar` refaz a análise sobre o `medidas.json`;
  - `lobos.py`, `cerebro_c.py` e a bancada não mudaram.
  - Configs `experiments/configs/v2_comparacao_cerebros/{fumaca,piloto,validacao}_ac.json`; testes `tests/test_comparacao_a_c.py` (20).
- **Piloto** (28101…28505, K = 4, 940 vidas, 1 h 30): σ_d 0,035 (CC-1) e 0,036 (CC-2) contra Δ 0,1986. **N = 5, K = 1**, ~23 min. As
  vidas do C refeitas dão o "não aprende" da calibração dele, idêntico.
- **Validação** (29101…29505, uma vez, 235 vidas, 22 min):
  - **CC-1** C − A +0,016 [−0,017; +0,046] e **CC-2** +0,036 [−0,009; +0,078]: **empate nos dois** (dentro de ±Δ, nenhum passa no
    Holm). O sinal é do A nas duas runs.
  - **Legibilidade** (P1 descasado): A 0,262, C 0,327, C − A +0,065 [+0,057; +0,072]: **o C vence o passo 2** (limiar 0,05).
  - **Porte:** empate; os dois têm pesos inteiros e nenhuma função transcendental.
  - **Custo:** empate (CPU −4,3%, log −0,3%).
  - **Recomendação pelo M6: o C.**
- **O que pesa contra** (secundário, fora da regra): no P3, o C generaliza a bronca do dono para toda fruta e come 9 a 17 frutas por
  vida, contra 38 a 46 do A; no descasado e no mutável o A come muito menos a fruta ruim (C − A ~+0,20). No P3 a legibilidade também é do
  A. O C deriva menos (razão 1,57 × 2,43). A escolha é do Matheus.

## V2, DESCRITIVO-PLATO — o platô de ~1/3: apagar a preferência ou aprender qual fruta faz mal? (2026-10-07, `docs/TAREFA_V2_DESCRITIVO_PLATO.md`) — PÓS HOC DESCRITIVO

Decisão V-3, pergunta Q-1 de `docs/LEITURA_V2_VALIDACAO_UNICA.md`. **Sem run nova, sem gate e sem mudar leitura registrada.** Números de
`artifacts_v2_descritivo_plato/`; relatório `docs/DESCRITIVO_V2_PLATO.md`. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **Código:** `experiments/descritivo_plato.py`.
  - Regenera as vidas fechadas (P0, P1, P2, P2e e P3, nas três condições) da validação única (30101…30505, A, 450 vidas) e da comparação
    (29101…29505, A e C, 135 vidas).
  - Rejoga cada uma do próprio log e confere contra as medidas gravadas; uma divergência falharia alto, e nenhuma divergiu.
  - Lê o que o motor já registra (ofertas e consumos), com a fruta classificada pelo efeito vigente no tick.
  - Testes: `tests/test_descritivo_plato.py` (10).
  - Nada mais mudou.
- **Cérebro A (P1, P2, P2e): misto.**
  - **Na escolha entre frutas, aprende qual faz mal:** come a ruim em 2% a 11% das vezes, contra ~46% do acaso e 29% a 65% do herdado.
    O peso da escolha da ruim fica muito abaixo do das outras.
  - **Com uma fruta só, come o que houver:** a ruim tanto quanto as outras ou mais (+0,08 a +0,15 no descasado e no mutável, onde ela é a
    preferida inata). O termo de presença na decisão de comer aprende pouco (−270 a −370 em S).
  - **O ~1/3 é a soma dos dois:** com a nutrição, o aprendiz come muito mais fruta (24 → 42 por vida).
  - **P3:** a bronca derruba o peso da escolha da ruim, mas o dono não mexe na decisão de comer, e depois da troca do mutável o P3 não
    reaprende.
- **Cérebro C** (5 unidades):
  - **P1:** a escolha fica perto do herdado (descasado 0,56, herdado 0,61), embora os pesos mostrem a aversão aprendida. O ~1/3 dele vem
    mais de comer de tudo.
  - **P2e:** segue a informação errada (a ruim em 0,77–0,83; o A fica em 0,02–0,04).
  - **P3:** quase não come.
