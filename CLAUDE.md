# CLAUDE.md — Digilab

Contexto para o Claude Code. Leia inteiro antes de mexer em qualquer coisa.

## O que é

Projeto de pesquisa pessoal do Matheus (não é a pesquisa de mestrado dele): um **pet virtual evolutivo e
competitivo com IA**, inspirado conceitualmente em Tamagotchi/Digimon. O dono treina o pet
por feedback; o pet tem memória/traços persistentes; pets treinados por donos diferentes
competem numa arena.

A hipótese científica central, testada **em simulação pura, sem humanos**:
> treino por um dono coerente produz um pet melhor que feedback aleatório com o mesmo volume de interação.

Se isso não se sustentar, o produto continua válido como jogo, mas a hipótese precisa ser reescrita.

## Regras do projeto — não negociáveis

- **Não aumentar escopo.** Nada de combate novo, multiplayer, interface gráfica ou modelos
  novos fora do que a tarefa pede. (Exceções autorizadas em 2026-09-24: o combate V2 em
  `digilab/combate_v2/` e o combate V2.1 — técnicas por linha e passivas por forma — em
  `digilab/combate_v2/v21/`, `docs/ESPEC_COMBATE_V21.md`. Plugar pets no Python e comandos do
  dono na luta continuam fora.)
  Exceção autorizada em 2026-09-28 (`docs/TAREFA_FRONT_TS.md`): migrar o jogo web para Vite +
  TypeScript + Preact em `web/app/`, com o motor separado da interface e testes de paridade contra o
  HTML atual. Sem regra de jogo nova; formato do save e chaves do localStorage não mudam.
- **LLM liberada** (decisão do Matheus, 2026-09-24): a proibição de LLM foi retirada. Usar LLM
  continua dependendo de a tarefa pedir, como qualquer outra coisa.
- **Falhar alto, não em silêncio.** `raise` em vez de `dropna`, valor default ou `except: pass`.
  Evento desconhecido no log levanta erro.
- **Determinismo é requisito.** Mesma semente + mesmo log = mesmo resultado, até o último float.
  Se um teste de replay quebrar, pare tudo e conserte antes de qualquer outra coisa.
  Exceção (decisão do Matheus, 2026-09-28): **modo livre gravado**. Um modo onde LLM e acaso real
  (sem semente) decidem ao vivo. Toda saída não determinística (resposta da LLM, sorteio de entropia
  do sistema) entra no log como evento, e o replay lê o evento em vez de sortear de novo. Assim a vida
  continua rejogável e auditável, embora não seja reproduzível a partir da semente. O modo
  determinístico continua sendo o padrão e o único válido para a confirmatória, os protocolos com hash
  e a paridade Python/web.
- **RNG de ambiente e de política separadas.** Trocar de política não pode mudar o clima do mundo.
- **Métricas existem uma vez só** (`digilab/metrics.py`) e são compartilhadas por todos os braços.
- **Nenhum número em resultado sem artefato em disco que o produza.**
- **Parâmetros ficam em `digilab/config.py`.** Nenhum número mágico espalhado.
- **`digilab/engine.py` não muda.** O sha256 dele está congelado em `protocol.py`
  (`ENGINE_SHA256_V0`); teste e preflight conferem.
- Português nos comentários e docstrings, **sem acentos em identificadores**.
- Só biblioteca padrão no pacote `digilab/` (o preflight verifica por AST). `pytest` só para testes.

## Trabalho em paralelo na V2 (2026-10-01, `docs/V2_TRABALHO_PARALELO.md`) — PROPOSTO

- A pasta `D:\Trab\digilab\v2` é só a referência da `main`: ninguém troca o branch dela. Cada frente trabalha na própria worktree
  `D:\Trab\digilab\v2-<frente>` (branch `v2-<frente>`), criada de `origin/main`.
- Um chat coordenador (plano, tarefas, sementes, versão de pet, fila da GPU, marco de cada rodada) e um chat worker por frente. A tarefa de cada
  frente fica em `docs/TAREFA_V2_<FRENTE>.md` (modelo em `docs/modelos/TAREFA_V2_MODELO.md`).
- Worker entrega um PR e para; merge só pelo Matheus. Em `CLAUDE.md` e `REGISTRO_DESVIOS.md`, cada um acrescenta a própria seção no fim.

## Arquitetura — três camadas com velocidades diferentes

1. **Estado e necessidades** (`state.py`) — determinístico, escrito à mão. É o ambiente, não o
   agente. Nunca aprende.
2. **Política de comportamento** (`policy.py`, `policies/`) — escolhe a ação do pet. Aprendizado
   entra aqui como troca de classe sob o `Protocol` `Politica` (`agir`, `observar`, `estado_interno`).
3. **Traços e evolução** (`tracos.py`) — EMA lenta da distribuição de ações. Lento de propósito:
   é o que impede persona drift. Hoje é a versão mínima que a arena precisa.

Event sourcing: o estado do pet **nunca é salvo**; só o log (ações do usuário + avanços de
tempo). A vida é reconstruída reprocessando o log.

## Mapa do repositório

| caminho | papel |
|---|---|
| `digilab/config.py` | todos os parâmetros (v0 + `ConfigBandit`, `ConfigDonos`, `ConfigTracos`, `ConfigArena`, `ConfigMetricas`) |
| `digilab/events.py`, `state.py`, `policy.py`, `engine.py` | v0: motor, log, `PoliticaInstinto` |
| `digilab/protocol.py` | protocolos congelados `PROTOCOLO_ARENA_V1` e `PROTOCOLO_ARENA_V1_ABLACAO` (herda tudo da v1 + campo `politicas`); cada campo DECIDIDO/PROPOSTO; hash cobre protocolo + configs + engine; `bracos_do_protocolo` dá (rótulo, dono, política) |
| `digilab/donos.py` | donos sintéticos: atencioso, relapso, aleatório (controle crítico), incoerente |
| `digilab/treino.py` | `CanalDeInteracao` impõe orçamento exato; `MotorComFeedback` (subclasse, só sobrescreve `_aplicar_acao_usuario`); `reproduzir_com_feedback`; `simular_vida` |
| `digilab/policies/bandit.py` | Thompson sampling linear; prior = distribuição exata da `PoliticaInstinto` via sonda de rng + Gumbel-max. **Congelado desde a V2** (2026-10-01): só reproduz a v1 |
| `digilab/policies/lobos.py` | **V2, L0**: `PoliticaLobos`, o aprendiz da V2 com lobos nomeados (percepção, memória e emoção, impulsos, decisão); pesos inteiros em ponto fixo iniciados no prior do instinto, aprendizado desligado (`ConfigLobos`); vida byte a byte igual à do instinto (seção "V2, L0" no fim); **LOBOS-MUNDO**: com `cfg_bola`/`cfg_frutas` ligadas vê a bola e as frutas e escolhe a fruta; E2 no sinal do P1 (seção "V2, LOBOS-MUNDO" no fim); **N5-CEREBRO**: a entrada `info` (o que o dono informa) na escolha da fruta, um peso compartilhado, `ConfigLobos.w0_info` (seção "V2, N5-CEREBRO" no fim); **FRUTA-NO-CENARIO B**: a decisão de comer lê a fruta presente (seção "V2, FRUTA-NO-CENARIO, parte B" no fim); **CEREBRO-N6-N7**: a memória de episódios das frutas (N6) e o pedido do dono na decisão de comer e na escolha da fruta (N7), atrás de chaves (seção "V2, CEREBRO-N6-N7" no fim); **CANAIS-REFORCO**: o sinal da consequência separado por canal, com o mesmo total do escalar, `ConfigConsequencia.canais_ligados` (seção "V2, CANAIS-REFORCO" no fim) |
| `digilab/policies/camada_unica.py`, `experiments/run_v2_l1.py`, `experiments/configs/v2_l1/` | **V2, L1**: o lobo de decisão aprende (feedback como vantagem, inteiros; `ConfigLobos.aprendizado_ligado`), o controle de capacidade equivalente sem lobos (`PoliticaCamadaUnica`), e o orquestrador da calibração/validação (G3, G3-T, G4, G5, G6, acoplado, norma de reação, educação) → `artifacts_v2_l1/` (seção "V2, L1" no fim) |
| `experiments/bancada_v2.py`, `experiments/configs/bancada/` | **V2, BANCADA**: o orquestrador dos braços da pergunta maior (P0 só herdado, P1 consequência desde o N3, P2/P2e/P2a informação desde a BANCADA-N5, só nos mundos das frutas, P3 feedback do dono) sobre o mesmo aprendiz, a vida = (genoma, mundo, dono, braço, semente), o modo acoplado e as medidas (`metrics.desempenho_no_ambiente`, `custo_da_plasticidade`, `tabela_braco_condicao`); mundos `padrao`, `bola` (B1/B2), `bola_a1` e os das frutas (`casado_frutas`, `descasado`, `mutavel`, `iguais_frutas`), as condições casado/descasado/mutável/iguais e as unidades derivadas (prefixos do experimento maior, do N6 e do N7); desde a BANCADA-N5 os lobos veem a bola e as frutas; os braços do N6 (M0, MR, MT, ME) e do N7 (P0+ped, P1+ped, P3+ped), ligados à memória e ao pedido desde a BANCADA-LIGA-N6-N7; o K4 fora do orçamento (chave `julgamento_fruta`), os canais por braço e as ablações da K-7 (P1c, P1c-mem, P1c-can) desde a BANCADA-K4-CANAIS; a chave `montagem` (`"completa"`: o cérebro A da seção 1 do plano da calibração conjunta em cada braço) desde a BANCADA-MONTAGEM; os braços P2d e P3i do adendo 3 desde a P2D-P3I, parte D (seções "V2, BANCADA", "V2, N3", "V2, BANCADA-MUNDOS", "V2, BANCADA-FRUTAS", "V2, BANCADA-N5", "V2, BANCADA-N6-N7", "V2, BANCADA-LIGA-N6-N7", "V2, BANCADA-K4-CANAIS", "V2, BANCADA-MONTAGEM" e "V2, P2D-P3I, parte D" no fim) |
| `experiments/run_v2_experimento_maior.py`, `experiments/configs/v2_experimento_maior/` | **V2, BANCADA-EXPERIMENTO**: o orquestrador do experimento maior (P0, P1, P2, P2e, P3 × `casado_frutas`, `descasado`, `mutavel` pela bancada, o "só cuidado" acoplado, os seis contrastes primários com Holm, a equivalência da predição 5 e as leituras por predição); o ponto nomeado do aprendiz na bancada (`ponto`: `L1` padrão, `T3` para o N5 e o experimento maior); os blocos da seção 4 do plano da calibração conjunta (`"blocos": true`), o Δ de cada contraste na escala da medida e o N pelo poder simulado (adendo 2), a config da validação única, o bloco de durações e o lugar do P2d e do P3i (adendo 3; custo em `experiments/custo_adendo3.py`) (seções "V2, BANCADA-EXPERIMENTO", "V2, V1-VALIDACAO-UNICA" e "V2, V1-ADENDO3" no fim) |
| `experiments/run_v2_calibracao_conjunta.py`, `experiments/configs/v2_calibracao_conjunta/` | **V2, K2**: a calibração conjunta do cérebro A (etapas A1, A2, B, C e D do `docs/PLANO_CALIBRACAO_CONJUNTA_V2.md`, montagem completa da bancada, o adendo de tamanho de amostra) → `artifacts_v2_calibracao_conjunta/`, `docs/RESULTADO_V2_CALIBRACAO_CONJUNTA.md` (seção "V2, K2-CALIBRACAO-CONJUNTA" no fim) |
| `experiments/run_v2_calibracao_cerebro_b.py`, `experiments/configs/v2_comparacao_cerebros/` | **V2, CALIBRACAO-CEREBRO-B**: a calibração do cérebro B pelo adendo 1.1 do plano da comparação dos cérebros (etapas B-A a B-D em cadeia e o piloto do "não aprende") → `artifacts_v2_comparacao_cerebros/calibracao_B/`, `docs/RESULTADO_V2_CALIBRACAO_CEREBRO_B.md` (seção "V2, CALIBRACAO-CEREBRO-B" no fim) |
| `experiments/run_revisao_aprendiz.py`, `experiments/configs/v2_revisao/` | **V2, REVISAO-APRENDIZ**: diagnóstico do aprendiz (teto, janela de crédito com o traço `ConfigLobos.traco_decisoes`/`traco_fator`, exposição), uma alavanca por vez, pela bancada (chaves `lobos` e `frutas` da config) → `artifacts_v2_revisao/` (seção "V2, REVISAO-APRENDIZ" no fim) |
| `experiments/run_v2_n3.py`, `experiments/configs/v2_n3/` | **V2, N3**: a fonte `consequencia` (P1: redução do déficit de fome, higiene e energia pela própria ação, `lobos.sinal_homeostatico`, `ConfigConsequencia`) e os gates do N3 → `artifacts_v2_n3/` (seção "V2, N3" no fim) |
| `digilab/tracos.py` | camada 3 mínima |
| `digilab/arena.py` | 5 ações em ciclo (cada uma vence 2, perde 2); stats = afinidades soma-zero dos traços; disposição herdada da política; arena nunca chama `observar()` |
| `digilab/metrics.py` | taxa de vitória, Bradley-Terry (erro padrão projetado em soma-zero), JSD com números aleatórios comuns, bootstrap, `efeito_do_treino` (ablação) |
| `experiments/run_arena.py` | orquestrador: preflight → vidas → replay do disco → torneio → replay do disco → métricas → gate |
| `experiments/configs/` | `canonico.json` (o portão), `ablacao.json` (ablação treino × cuidado), `fumaca.json` e `ablacao_fumaca.json` (NÃO canônicos). Campo `protocolo` escolhe o protocolo (padrão `arena-v1`) |
| `artifacts/` | saída da run canônica (evidência; não editar à mão) |
| `artifacts_ablacao/` | saída da ablação (evidência; não editar à mão) |
| `web/app/` | **o jogo web** (desde 2026-09-28, TAREFA_FRONT_TS): motor em TypeScript (`motor/`, sem DOM), app Vite + Preact (`src/`), testes (`test/` Vitest, `e2e/` Playwright). Build em `web/dist/` (não versionado) |
| `web/digilab_sprites.html` | versão antiga do jogo (só com `?antigo=1`; sem isso redireciona para o app); ainda é a referência dos gabaritos de paridade |
| `web/digilab.html` | versão web jogável antiga, com placeholders (porte JS; ver abaixo) |
| `digilab/combate_v2/` | combate V2: `regras.py` (resolução pura, sem rng), `gambits.py` (catálogo fechado de condições, `ListaGambits`, decisão com motivo), `lutador.py` (`CondicaoFisica` × `Estilo`), `partida.py` (laço, log, replay), `bots.py` (5 fixos + adaptativo em gambits; `oraculo` FORA da linguagem) |
| `experiments/run_bateria_combate.py` | portão do combate V2: round-robin de bots, gates G1–G7 → `artifacts_combate_v2/` |
| `experiments/calibrar_combate_v2.py` | varredura de calibração (recusa sementes de validação) |
| `experiments/configs/bateria_*.json` | `bateria_canonico.json` (validação, canônico) e `bateria_calibracao.json`; `calibracao_combate_v2.json` = registro da calibração |
| `artifacts_combate_v2/` | saída da bateria canônica + `calibracao_varredura.jsonl` (evidência) |
| `digilab/motivo.py` | `Motivo` único vida/combate; `PoliticaComMotivo` (embrulho somente leitura da política de vida); adaptador do motivo do combate V2 |
| `digilab/expressao.py` | `expressar(motivo, estagio, humor)`; tabela de textos com marcador único por fator e cobertura verificada na carga; estágio PROVISÓRIO por idade |
| `digilab/memoria.py` | `MemoriaCurta` (latência do dono por necessidade, broncas e elogios com decaimento) e `PoliticaBanditMemoria` |
| `experiments/diario.py`, `legibilidade.py` | diário de motivo/expressão (vida ou partida) e métricas de legibilidade → `artifacts_expressao/` |
| `experiments/configs/memoria.json` | `PROTOCOLO_ARENA_V1_MEMORIA` → `artifacts_v1_memoria/` |
| `digilab/temperamento.py`, `vinculo.py`, `desejo.py`, `obediencia.py` | personalidade: temperamento (rng_ovo), vínculo, obediência com recusa e motivo, desejo; `configs/personalidade*.json` → `artifacts_v1_personalidade/` |
| `digilab/memoria_espacos.py`, `experiments/memoria_espacos.py` | memória por espaços (adendo DF, Parte 1) e relatório de ocupação; `configs/memoria_espacos.json` → `artifacts_v1_memoria_espacos/` |
| `servidor/` | servidor local do jogo web (`servidor_local.py`, substitui o `http.server`) e fala por LLM (`fala_llm.py`: provedores Ollama local e Claude; SDK `anthropic` só aqui). `digilab/` não importa isto (teste AST) |
| `experiments/avaliar_fala.py` | avaliação da fala por LLM (C6); `--livre`: avaliação da fala livre (`digilab_fala_livre/avaliacao.py`) |
| `digilab/combate_v2/v21/` | combate V2.1 (subpacote: o hash dos fontes da base não muda): `catalogo.py` (forma = espécie + caminho, stats com renormalização, perfil de combate, transições), `regras.py` (técnicas e passivas, resolução pura), `gambits.py` (capacidade por estágio, `turno_execucao`, `oponente_vai_preparar`), `partida.py` (lutador, laço, replay), `bots.py` (8 adultos, 4 adolescentes, respostas declaradas) |
| `digilab/evolucao.py`, `experiments/run_pesquisa_v21.py` | evolução do pet de pesquisa (ovo pareado, cuidado, caráter nas sondas, forma adulta) e arena V2.1 com adultos → `artifacts_v21_pesquisa/` |
| `digilab/campanha.py`, `experiments/run_campanha.py`, `calibrar_campanha.py` | campanha contra os 3 NPCs (regras V21C) → `artifacts_campanha/`; calibração da escada (K1–K4) → `experiments/configs/campanha/` |
| `digilab/treino_stats.py`, `treino_vida.py` | treino (fadiga, forçar, sobrecarga), `MotorTreino`, plano de sessões e donos com treino (inclui o exigente) |
| `digilab/confianca.py`, `web/app/motor/confianca.ts` | M1: confiança de combate e novidade por rival (`ConfigConfianca`, desligada por padrão; espelho web nos pets v8); gabarito de paridade por `experiments/exportar_gabarito_confianca.py` |
| `experiments/run_treino.py`, `run_bateria_sombria.py`, `calibrar_treino.py`, `calibrar_sombrias.py` | runs da TAREFA_TREINO_SOMBRIO (5 braços, campanha, S2) → `artifacts_treino/`, `artifacts_campanha/treino.json`; gate S1; calibração da sobrecarga e redesenho das sombrias (`configs/sombrias/`) |
| `experiments/run_bateria_v21.py`, `calibrar_v21.py` | bateria V2.1 (E1–E5 + checagem da base) → `artifacts_combate_v21/`; varredura de calibração |
| `experiments/configs/bateria_v21_*.json` | `bateria_v21_canonico.json` (validação) e `bateria_v21_calibracao.json` (rápida, sem E5); `calibracao_v21.json` = registro da calibração |
| `docs/` | especificações (`ESPEC_COMBATE_V2.md`, `ESPEC_COMBATE_V21.md`, `TAREFA_MEMORIA_EXPRESSAO.md`), dados PROPOSTOS do V2.1 (`catalogo_pets.json`, `arvore_evolucao.json`, `cronograma_interacoes.json`) e `REGISTRO_DESVIOS.md` |
| `digilab/historia.py` | voz própria (DESIGN_VOZ_PROPRIA, parte 1): extrator dos fatos H/O/P/L a partir do registro (função pura; `ConfigHistoria`, `PARAMETROS_HISTORIA_V1`); `fabrica_com_captura` anota as ações do pet no replay |
| `digilab/educacao.py` (mentira) | `ConfigMentira` (desligada por padrão; `PARAMETROS_MENTIRA_V1`, à parte do hash da educação-v1): honestidade, chance de mentir, janela de fala, evento `fala`; reações dos donos em `donos_educacao.py`. `tests/test_reproducao_v3_confirmatoria.py` confere V3c e confirmatória contra os `pets.json` |
| `tests/` | a suíte inteira (`python -m pytest tests/ -q`; a contagem do dia fica no PR de cada frente, nunca aqui, porque envelhece); `test_canonico_intacto.py` roda a canônica V1 (~70 s) e `test_motivo_expressao.py` a bateria V2 (~50 s); `test_combate_v21.py` confere `config.py` contra os JSONs de `docs/` |

## Comandos

```bash
python -m pytest tests/ -q                                                   # a suíte inteira, ~7 min (a contagem do dia vai no PR de cada frente)
python experiments/run_bateria_v21.py --config experiments/configs/bateria_v21_canonico.json  # combate V2.1, ~10 min; rc 0/2
cd web/app && npm install && npm run build                                  # constrói o jogo web em web/dist/
python servidor/servidor_local.py                                             # jogo web + fala por LLM em http://localhost:8765/v1/web/dist/
cd web/app && npm test && npm run tipos && npm run e2e                        # testes do jogo web (paridade, tipos, ponta a ponta)
python experiments/run_treino.py                                             # treino: 5 braços, campanha, S2; rc 0/2
python experiments/run_bateria_sombria.py                                     # gate S1 (formas sombrias)
python experiments/run_arena.py --config experiments/configs/memoria.json    # arena v1 + memória, ~2 min
python experiments/legibilidade.py                                            # legibilidade + diários, ~1 min
python experiments/diario.py --log artifacts_ablacao/vidas/atencioso-bandit@101.jsonl
python experiments/run_arena.py --config experiments/configs/ablacao.json    # ablação, ~2 min
python experiments/run_bateria_combate.py --config experiments/configs/bateria_canonico.json   # combate V2, ~50 s; rc 0/2
python experiments/run_arena.py --config experiments/configs/canonico.json   # portão, ~2 min; rc 0 APROVADA / 2 REPROVADA
python experiments/run_arena.py --config experiments/configs/fumaca.json     # fumaça, rápido, não canônico
python run_demo.py                                                            # demo do v0
```

Ambiente do usuário: Windows, pasta `D:\Trab\digilab\v2` (referência da `main`; o trabalho é nas worktrees `D:\Trab\digilab\v2-<frente>`,
`docs/V2_TRABALHO_PARALELO.md`; a `v1` é só leitura). Python 3.10+.

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

## Combate V2 (2026-09-24, `artifacts_combate_v2/`, branch `combate-v2`)

Números abaixo vêm de `artifacts_combate_v2/gates.json`, `matriz.json` e `equilibrio.json`
(sementes de validação 2101…2505, 200 partidas por par por semente, 28.000 partidas; hash das
regras `c26aa2813e23…`, da config `86a28a8adbd1…`). Tudo PROPOSTO. Não substitui a arena v1.

- Bateria **REPROVADA**: G1, G2, G3, G6, G7 ok; **G4 e G5 falham**.
  - G4: mediana 25 turnos (ok), mas 31,3% das partidas acabam no limite de turnos (limiar 20%).
    Vem de pares de bots passivos (tartaruga, contragolpe) que só atacam com o oponente sem guts.
  - G5: `esquivar` em 0,8% das decisões dos bots do suporte (limiar 3%).
- Equilíbrio dos fixos: agressivo 0,327, atirador 0,335, tartaruga 0,338 (ciclo agressivo >
  tartaruga > atirador > agressivo). Aleatório e contragolpe fora do suporte.
- G2: adaptativo × aleatório 0,999, IC95 [0,997, 1,000]; oráculo 0,946 × adaptativo 0,913 contra os fixos.
- **Atenção**: o adaptativo vence todos, inclusive o oráculo (0,962 no confronto direto); no
  equilíbrio com ele incluído (informativo) ele vira estratégia pura. Um único estilo domina.
- G6: condição (HP ±10%, guts ±10) move a taxa no máximo 0,197 (atirador); estilo move 0,388.
- G7 passa pela média (0,705), mas uma das 5 permutações (`02416357`) bate o original (0,009 para o
  original): a ordem importa, e a ordem escrita à mão não é a melhor.
- Calibração (só sementes de calibração, 3 rodadas, `experiments/configs/calibracao_combate_v2.json`):
  `custo_disparo` 15 → 20 (G1), `hp_neutro` 100 → 70 (mediana de turnos). Nenhum número resolveu G4
  (limite) nem G5 (esquiva): são desenho dos bots/regras, não calibração.
- Limites da linguagem de gambits encontrados: não há "última ação do oponente foi X" (k só 2 ou 3),
  nem condição sobre a própria ação anterior, nem negação. Catálogo NÃO foi ampliado.
- G3 mede viés de posição (pontos do lado 0 nos espelhos), porque com lados trocados na metade a
  média do espelho é 0,5 por construção.

## Combate V2.1 — árvore de evolução no combate (2026-09-24, `artifacts_combate_v21/`)

**Pré-condições não cumpridas** (base V2 REPROVADA e sem finta/parry/fuga/morte súbita; tarefa de
personalidade inexistente). O Matheus mandou seguir adaptando; adaptações e interpretações em
`docs/REGISTRO_DESVIOS.md`. Números abaixo vêm de `artifacts_combate_v21/gates.json`,
`matriz_arquetipos.json`, `equilibrio.json`, `matriz_especie_arquetipo.json`, `uso_tecnicas.json` e
`robustez_e5.json` (sementes de validação 4101…4505, 100 partidas por par por semente; E1 = 72.000
partidas; hash das regras `ced939707380…`, config `b860ec4acaf7…`). Tudo PROPOSTO.

- Bateria **REPROVADA**: E1, E2, E3, E4 e E5 falham. Base V2 intacta (hash dos fontes igual).
- **E1**: nenhum arquétipo vence todos, mas o suporte do equilíbrio tem 3 (espelho 0,443, furioso
  0,435, emboscador 0,120), precisa de 4. Ciclo furioso > caçadores > espelho > furioso. Colossos
  fracos (vigia e titã perdem de quase todos).
- **E2**: ferrugem vence as outras três (média 0,629; cirro 0,343). 6 dos 8 arquétipos lutam de
  perto e a soma de stats não gera ciclo entre espécies.
- **E3**: todas as técnicas acima de 5% (16–43%). Resposta declarada reduz o usuário em investida
  (0,625 → 0,606), contra_golpe (0,485 → 0,467) e pele_dura (0,259 → 0,003); **marcar não**:
  "avançar e pressionar" sobe o caçador de 0,625 para 0,953 (quem recua anula quem avança).
- **E4**: duelista 0,785, emboscador 0,788, espelho 0,629 dentro de [0,6, 0,85]; furioso, muralha,
  sentinela, titã e vigia esmagam o adolescente (0,95–1,0): a diferença vem dos gambits e da passiva.
- **E5**: E1 se mantém em 2/36 perturbações (já falha sem perturbar).
- Calibração (só sementes 3101…3505, 2 rodadas, `experiments/configs/calibracao_v21.json`):
  `fracao_espelho_disparo` 0,5 → 1,0; regras do parry e do disparo marcado revisadas; bots do colosso,
  da muralha e as respostas do E3 reescritos. Conversão de stats, custo da pele e multiplicador do
  adolescente testados e não adotados (trocam a espécie dominante ou derrubam o E1).
- A seção "Pesquisa" da especificação foi feita depois (2026-09-25): ver a seção abaixo.

## Pesquisa do V2.1 — pet de pesquisa evolui e luta (2026-09-25, `artifacts_v21_pesquisa/`)

`python experiments/run_pesquisa_v21.py`: evolui as 40 vidas de `artifacts_ablacao/vidas` até adulto
(`digilab/evolucao.py`, `ConfigEvolucaoPesquisa`, tudo PROPOSTO; interpretações em
`docs/REGISTRO_DESVIOS.md`) e luta na arena V2.1 só com adultos, com ablação sem técnicas e passivas.
Números de `artifacts_v21_pesquisa/resumo.json` e `formas.json`; 5 sementes, sem teste estatístico
da distribuição de formas: descritivo.

- **Cuidado não distingue donos**: nenhum dono simulado atende os chamados do bebê; todo pet é arisco.
- **Formas adultas diferem por dono (bandit)**: atencioso 4/5 caçador (3 emboscador); incoerente 4/5
  guardião (3 muralha); aleatório brigão 3/5 e caçador 2/5; relapso espalhado. Instinto (controle,
  sem aprendizado): 20/20 duelista. Nenhuma semente teve a mesma linha nos 4 donos. Caráter adulto do
  bandit: |eixo| máximo com mediana 0,38. Com 5 sementes não dá para separar sinal do dono de ruído
  de vida.
- **Arena (atencioso × aleatório, IC95 bootstrap)**: bandit 0,379 [0,130, 0,638]; bandit sem técnicas
  e passivas 0,741 [0,341, 1,000]; instinto (mesma forma, só a condição difere) 0,585 [0,411, 0,770];
  instinto sem técnicas 0,665 [0,549, 0,785]. Por semente o bandit vai de 0,01 a 0,80: o confronto de
  arquétipos decide. Inconclusivo; a bateria V2.1 reprovada pesa aqui.

## Campanha contra os NPCs (`artifacts_campanha/`) — progressão por lugar (2026-09-26)

`python experiments/run_campanha.py` (`digilab/campanha.py`, `ConfigCampanha`), combate corrigido
(V2C + V21C, `campanha.REGRAS_CAMPANHA`). NPC = stats uniformes, sem técnica nem passiva, estilo
`"<familia>:<nome>"` (`v2`, `v2c`, `v21` sem regras de técnica, `crianca`), campos `estagio` (vida e guts
pelo multiplicador do estágio), `lugar` e `epsilon` opcional. Decisões em `docs/REGISTRO_DESVIOS.md`
(2026-09-25 escada K1–K4; 2026-09-26 progressão). Tudo PROPOSTO.

- **Treino vale 3** em combate (`ConfigTreino.peso_ponto_combate`, `catalogo.com_treino`; arena e campanha).
- **Todo pet treinado vence cada NPC** (decisão do Matheus, 2026-09-26: NPCs fixos e imprevisíveis; treino
  típico de uma vida, tabela `ALCANCE`). Lugares (vencer qualquer rival abre o próximo): Campina —
  Brutamontes (criança, 96, criança arisca, ε 0,5); Torre — Sentinela (tartaruga V2C, 72, ε 0,4), Carcereiro
  (espelho sem técnica, 90, ε 0,5), Porteiro (agressivo V2C, 90, ε 0,5); Cidadela — Soberano (agressivo V2C,
  110, ε 0,5).
- **Validação** (`calibrar_progressao.py --validar`, `criterios_todos_vencem`): nenhuma linha travada em
  nenhum dos 5 NPCs; pet treinado 0,81–0,97. **Custo**: o pet sem treino do estágio sugerido vence 0,39–0,66
  (média); o treino garante a vitória, não a libera. Os critérios anteriores (P1–P4, "básico perde" por
  lugar) ficam só como relatório.
- A medida usa treino uniforme; em algumas linhas ele até piora a luta (muda o ritmo de guts dos gambits).
- Campanha com treino e S2: seção do treino abaixo.

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

## Evolução canônica no jogo (2026-09-29, `docs/DESIGN_EVOLUCAO_CANONICA.md`)

Pedido do Matheus ("tem que seguir o cânone"), só no jogo web; o Python da pesquisa segue com 4 estágios.
- **Pets v5** (`VERSAO_PET = 5`, ovos novos e filhos da herança): Champion → Ultimate → Mega. O Mega é um estágio próprio
  (`"mega"`): a forma adulta, a passiva e o caráter vêm do Ultimate; vida e guts ×1,15, E 3000 na campanha, treino com teto 16
  no estágio e 40 na vida. Ultimate → Mega pede 24 h (48 h no clássico), 10 lutas com ≥ 80% de vitória e vínculo ≥ 0,4; a
  sombria nunca chega (regra explícita). Constantes em `CMG` (`baseDe` leva o Mega às tabelas do adulto); `Motor.requisitosMega()`.
- **Nomes no cânone para todos os pets:** as duas formas adultas da linha são o mesmo Ultimate (o arquétipo as distingue) e o
  Mega é o da cadeia (Greymon → MetalGreymon → WarGreymon); a sombria usa o Ultimate. Pets v1–v4 param no Ultimate; o motor
  deles não muda (`nomeFormaLegado` na assinatura dos gambits).
- **Campanha v5:** Cidadela com o Myotismon; Montanha Espiral (Mega) com Puppetmon, Machinedramon e o Piedmon (chefe). Os
  pets v1–v4 seguem na campanha de sempre. Fatores calibrados no motor web (`web/app/test/calibrar_mega.mjs`,
  `artifacts_campanha/mega/`): validação nas metas de sempre.
- **Limiar do vínculo 0,4** (baixado de 0,7 pelo Matheus): com 0,7 os donos simulados coerentes não chegavam ao Mega e o
  aleatório chegava; com 0,4 o atencioso chega em 3 de 6 vidas, o aleatório em 5 de 6 (`artifacts_campanha/mega/limiar_vinculo.json`).
  O defeito do vínculo continua (pendência abaixo).

## Medalhas do Tamer no jogo, parte 1 (2026-09-29, `docs/DESIGN_MEDALHAS_ARENAS.md`)

Só no jogo web; a pesquisa em Python não tem Tamer (`docs/REGISTRO_DESVIOS.md`, 2026-09-29).
- **Tamer:** o jogador. Registro próprio (event sourcing) em `…-tamer` (`src/tamer.ts`): eventos `medalha` (id, contador,
  hora de parede, pet, forma, tick). Medalha na primeira vitória contra o líder, com qualquer pet v6; é do Tamer e sobrevive ao pet.
- **Trava (pets v6, `VERSAO_PET = 6`):** Rookie → Champion pede 1 medalha, Champion → Ultimate 3, Ultimate → Mega 5 (`CMD`), além
  dos requisitos de sempre. O motor nunca lê o Tamer: o app grava no registro do pet o evento `u` ("o Tamer tem N medalhas",
  `Motor.liberar`), e o pet pronto evolui nesse tick. Pet guardado recebe o `u` ao voltar a ser o ativo. Assinatura dos v1–v5 igual.
- **Medalhas** (`motor/medalhas.ts`, tabela única): uma por arena, do líder dela (parte 2, seção abaixo). Na parte 1 a 3ª e a 5ª
  tinham fonte provisória (Devidramon e Tortomon, na Torre de pedra) até a Floresta e o Lago existirem.
- **Tempo dos estágios nos v6:** conta desde a evolução anterior (`Motor.tickLimiteEstagio`), para um Rookie que esperou a
  medalha não ganhar um Champion curto; nos v1–v5 continua desde o nascimento.
- **Saves:** na primeira abertura os pets v1–v5 (ativo e guardados) são apagados com aviso e o jogo começa num ovo novo (decisão do
  Matheus). Os Cenários seguem com pets v5 (sem Tamer). Telas: Lutar · Medalhas, requisito na Evolução, líder na Campanha.

## Arenas com líderes, medalhas parte 2 (2026-09-30, `docs/DESIGN_MEDALHAS_ARENAS.md`, seção 12)

Só no jogo web e só pets v6; a pesquisa não tem arenas (`docs/REGISTRO_DESVIOS.md`, 2026-09-30).
- **Seis arenas** (`motor/arenas.ts`, `ARENAS`; campanha v6 em `bots.LUGARES_V6`/`CAMPANHA_V6`, na ordem do nível): Campina (Gazimon,
  sem regra), Torre de pedra (Guardromon com o contra-golpe: paciência), **Floresta** (Youkomon, muda de padrão no turno 10: leitura),
  Cidadela (Myotismon, três lutas seguidas sem cura: resistência), **Lago** (MarinBullmon; as travas e vetos do dono não valem:
  vínculo) e Montanha Espiral (Piedmon, chefe). Os NPCs de antes seguem como desafiantes, com as mesmas chaves. A 3ª medalha vem da
  Floresta e a 5ª do Lago (fim das provisórias).
- **Replay:** a regra depende só do rival e da versão do pet; o evento `l` continua `{r, s}` (a série da Cidadela é um evento só, com
  sementes derivadas). `Motor.montarLuta`/`lutadores` montam a luta para o motor e para a tela; `Motor.lugarDe(k)` dá o lugar do NPC
  na campanha do pet (os índices mudam da v5 para a v6). Pets v1–v5 e gabaritos iguais.
- **Calibração** (`web/app/test/calibrar_arenas.mjs`, `artifacts_campanha/arenas/`, na escala dos pets v6, seção abaixo; sementes de
  validação, com a regra do limite do desafiado): os seis líderes nas metas novas (sem treino ≤ 0,05; com o treino típico ≥ 0,80;
  nenhuma forma < 0,5). Sem treino 0,0006–0,0213, com treino 0,8125–0,9063, pior forma 0,535 (sentinela na Cidadela). Fatores só na luta de arena: Gazimon 1,3,
  Guardromon 1,6, Myotismon 0,9 (série), Piedmon 1,6; Youkomon e MarinBullmon 1,5. Na Torre o Guardromon ganhou lista própria de arena
  (`GAMBITS_ARENA.torre`: contra quem atira com frequência ele avança, no lugar do contra-golpe); com a de antes nenhum fator passava.
- **Telas:** cartão da arena (líder, regra, medalha), mapa de seis ilhas (atlas: `WorldMap_04` Floresta e `WorldMap_02` Lago, fora do
  repo), "luta k de 3" na Cidadela, aviso do Lago na luta e no Resultado, Medalhas com a regra de cada arena.
- **Correção do vigia:** nos pets v6 as duas regras novas do vigia V21D voltam como candidatas de troca (`candidatasDoVigia`).
- **Saves v6:** descarte único versão 3 (arenas), 4 (escala v6) e 5 (limite do desafiado): os v6 de antes saem, com o mesmo aviso.
- **Limite de turnos (decisão do Matheus, 2026-09-30):** nas lutas dos pets v6 (campanha, arenas, arena contra bots) a luta que chega ao
  limite sem nocaute é de quem foi desafiado, o rival (o pet sempre desafia); na Cidadela ela quebra a série. `combate.fimV2`/`jogarV2`
  com o desafiado (na Liga da Fronteira, o líder), `desafiadoDaVersao`; nada novo no registro. Pets v1–v5, cenários e o Python: a fração
  de vida, como sempre.

## Itens do Tamer, medalhas parte 3 (2026-09-30, `docs/DESIGN_MEDALHAS_ARENAS.md`, seção 13) — SEM EQUILÍBRIO

Só no jogo web e só pets v6; a pesquisa não tem itens (`docs/REGISTRO_DESVIOS.md`, 2026-09-30). **Sem equilíbrio** (decisão do Matheus,
2026-09-30): ainda entram outras mecânicas no combate, e o equilíbrio será uma rodada só, depois; os números são os PROPOSTOS da seção 13 e
os gates G-I1–G-I4 (13.7) ficam para essa rodada (`web/app/test/medir_itens.mjs` pronto, não rodado; sem artefato).
- **Catálogo** (`motor/itens.ts`, `CIT` em `constantes.ts`): Chip de Força e Chip de Guarda (stat: +2 pontos de treino, só no espaço que
  falta no teto do estágio e da vida, todos juntos ≤ 25% do treino típico); Chip Recuo e Chip Oportunista (regra, do Champion), Chip
  Perseguidor e Chip Aparo (regra, do Ultimate); Carta de Fôlego (+20 guts), de Cura (20% da vida na primeira vez abaixo de 30%) e de Foco
  (ε 0).
- **De onde:** o líder dá o chip da arena com a medalha (um Tamer com medalhas de antes recebe na abertura); a revanche vencida, com um
  pet do nível da arena, dá a carta da arena, uma por líder a cada 24 h do relógio do pet. Chips por pet pelas medalhas: 1/2/3 com 1/3/5;
  uma carta por luta.
- **Registro:** inventário no Tamer (registro versão 2, lê a 1: `item`, `carta_usada`); no pet, `i` (equipar/desequipar) e `k` (a carta,
  logo antes da luta `l`; outro evento depois dela falha alto). O motor não lê o Tamer; o app confere o inventário. A assinatura dos v6 só
  muda com item; v1–v5, gabaritos, paridade V21D e os artefatos de validação da parte 2 saem iguais. Descarte único não subiu.
- **Telas:** Crescer · Itens; a carta antes da luta (Campanha e Arena); o item novo e a carta usada no Resultado; o item de cada medalha
  em Medalhas; a regra de chip marcada nas regras de combate (não se veta).

## Fronteira de Batalha, parte 4a: a Liga dos Líderes e o fim do jogo (2026-09-30, `docs/DESIGN_FRONTEIRA.md`, seção 7) — SEM EQUILÍBRIO

Só no jogo web e só pets v6; a pesquisa não tem Liga (`docs/REGISTRO_DESVIOS.md`, 2026-09-30). As instalações: 4b e 4c nas seções seguintes
(a Fronteira completa: `docs/DESIGN_FRONTEIRA.md`, seção 10).
- **A Liga** (`motor/liga.ts`, `LIGA`): com as 6 medalhas (as que o pet conhece pelo `u`), os 6 líderes em sequência, cada um com um Mega de
  arquétipo diferente e lista canônica V21D: Gazimon/WarGreymon (furioso), Guardromon/Seraphimon (espelho), Youkomon/MegaGargomon
  (sentinela), Myotismon/Vikemon (titã), MarinBullmon/Rosemon (muralha), Piedmon/Imperialdramon Dragon Mode (duelista). Sem cura
  (`arenas.jogarSerie`, a série da Cidadela generalizada), chips valem, **cartas não** (o motor recusa; `k` antes da luta da Liga falha no
  replay), limite de turnos do líder, perder encerra a tentativa.
- **Fator 1 (desvio do desenho, que pedia o do Piedmon, 1,6):** com 1,6 cada luta sozinha é vencível, mas nenhuma forma vence as 6 seguidas
  (0 títulos nas 8); com 1 o furioso de referência (treino 40) vence 0,785, e 7 das 8 formas vencem às vezes
  (`test/conferir_liga.mjs` → `artifacts_campanha/liga/conferencia.json`). Para o Matheus decidir na rodada de equilíbrio.
- **Registro:** a tentativa é um evento `l` do pet, `{r: "liga", s}` (sem o evento `f`); `Motor.liga = {tentativas, titulos}` entra na
  assinatura só depois da primeira. O título vai ao Tamer como `campeao` (registro versão 3; um por pet; o primeiro é o do Tamer). A
  conclusão da jornada dos v6 vem da Liga (`jornada.concluiuJornada`); nos v1–v5, o chefe como antes.
- **Telas:** ilha da Fronteira no alto do mapa v6 (atlas `WorldMap_05`, fora do repo; mapa 390 × 864), aba **Lutar · Fronteira** (regras,
  os 6 líderes com os Megas, a última tentativa com a vida no fim de cada luta, o título), "Liga dos Líderes · luta k de 6" na luta, as 6
  lutas e o título no Resultado, a medalha de ouro em Medalhas, a conclusão "Campeão!". Testes: `test/liga.test.ts`, e2e com
  `e2e/save_liga.json` (`e2e/gerar_save_liga.mjs`).

## Fronteira de Batalha, parte 4b: a Torre de Batalha e o Palácio (2026-09-30, `docs/DESIGN_FRONTEIRA.md`, seção 8) — SEM EQUILÍBRIO

Só no jogo web e só pets v6; a pesquisa não tem instalações (`docs/REGISTRO_DESVIOS.md`, 2026-09-30). A Fábrica e o Salão (4c): seção seguinte.
- **As instalações** (`motor/instalacoes.ts`, `INSTALACOES`), abertas depois do título da Liga: a **Torre de Batalha** (Megas sorteados, sem
  cura, perdeu acabou; chips valem, cartas não) e o **Palácio** (a mesma sequência; travas, vetos e chips de regra não valem:
  `GambitsPet.listaPalacio`, a lista do Lago sem as regras que só estão no pet por um chip; chips de stat valem). Limite de turnos do rival;
  teto de 100 lutas por tentativa (nunca alcançado na conferência).
- **Rivais:** as 8 formas adultas no Mega × 4 espécies, sorteadas por luta de `hashSemente("fronteira-rival", s, k)`, com técnica,
  passiva, caráter e lista canônica V21D; E = vida do Mega na escala v6 × 1 (o fator da Liga, sem calibração).
- **Registro:** o pet conhece o título pelo evento **`f`** `{campeao: true}` (o app grava, como o `u`; um por pet). A tentativa é um `l`
  `{r: "torre_batalha" | "palacio", s}`, com `s = sementeTentativa(semente do pet, instalação, nº da tentativa dele ali)`: o motor confere a
  semente ao lutar e no replay. `Motor.instalacoes` (tentativas, recorde, última) entra na assinatura só depois do `f`. O recorde vai ao
  Tamer como **`recorde`** `{inst, valor, quando, pet, forma, tick}` (registro versão 4; só depois do título e só quando passa o anterior).
  `arenas.jogarSequencia` generaliza a série (a `jogarSerie` passa por ela, as mesmas lutas). Nada das instalações dá item, treino ou stat.
- **Conferência** (`test/conferir_instalacoes.mjs` → `artifacts_campanha/fronteira/conferencia.json`; Mega de referência, treino 40, sementes
  4101…4505): jogáveis. Vence a 1ª luta: furioso 1,00, duelista 0,97, espelho 0,90, emboscador 0,86, vigia 0,80, sentinela 0,78, titã 0,77,
  muralha 0,65 (Torre); média de vitórias de 1,5 (muralha) a 8,0 (furioso), máximo 16 (Palácio: 19). O pet do e2e (Valkyrimon) vence a 1ª
  em todas as 50 tentativas, média 7,6 (Torre) e 8,0 (Palácio). Com a lista canônica o Palácio é a Torre (outras sementes).
- **Telas:** as duas instalações em Lutar · Fronteira (regra, recorde do Tamer, tentativas do pet, "Tentar"), "Torre de Batalha · vitória N"
  na luta com a vida com que o pet começou, o Resultado (vitórias seguidas, as lutas, o recorde novo), os recordes em Medalhas. Testes:
  `test/instalacoes.test.ts`, e2e com `e2e/save_liga.json` e um Tamer campeão.

## Fronteira de Batalha, parte 4c: a Fábrica e o Salão (2026-09-30, `docs/DESIGN_FRONTEIRA.md`, seções 9 e 10) — SEM EQUILÍBRIO

Só no jogo web e só pets v6 em diante (v6, v7 com a voz própria e v8 com a confiança do M1; a Fábrica nem usa pet; o Salão mistura guardados v6 em diante); a pesquisa não tem instalações (`docs/REGISTRO_DESVIOS.md`, 2026-09-30). Com ela a
Fronteira está completa. Abrem depois do título do Tamer; fator 1 nas duas, sem calibração.
- **Fábrica** (`motor/fabrica.ts`, `TentativaFabrica`): 3 alugados (Megas de arquétipos distintos, espécies sorteadas, lista canônica V21D,
  sem treino e sem itens) sorteados de `sementeFabrica(n)` (n = o número da tentativa no registro do Tamer); o jogador escolhe 1 e luta
  séries de 3 contra Megas sorteados, sem cura dentro da série (a série seguinte começa inteira), limite do rival, perdeu acabou; depois de
  cada vitória pode trocar o alugado pelo rival derrotado, que entra com a mesma fração da vida (**a troca não cura**). Recorde: as séries
  vencidas. **As lutas vão só para o registro do Tamer** (versão 5: `fabrica`, `fabrica_luta`, `fabrica_troca`; o replay joga as lutas de
  novo e confere as sementes); a escala vale sempre ali (`perfilDe(..., comEscala)`), sem depender da chave do app.
- **Salão** (`motor/salao.ts`): um pet de cada nível (Rookie a Mega) entre o ativo e os guardados v6, cada um contra o bot canônico sorteado
  do nível (escala v6, fator 1), na ordem; perdeu acabou. A luta é um `l` `{r: "salao", s}` do registro de cada pet, com a semente do
  registro dele (`sementeSalao`), conferida pelo motor; `Motor.salao` entra na assinatura só depois da primeira. O guardado recebe `u`, `f` e
  a luta na hora parada dele e continua guardado (`src/fronteira.ts`: joga em cópias e só então grava; `pets.atualizarGuardado`). O Tamer
  grava a tentativa (`salao`: pets, sementes, quem venceu); o recorde (níveis seguidos, até 4) sai das tentativas.
- **Conferência** (`test/conferir_fabrica_salao.mjs` → `artifacts_campanha/fronteira/conferencia_4c.json`): jogáveis. Fábrica (2000
  tentativas do jogo): alugando o melhor arquétipo, vence a 1ª luta 0,442 e uma série só em 0,018–0,019 (lutas de espelho sem cura e com o
  limite do rival; máximo 2 séries); a troca entrando inteira (não adotada) daria 0,028–0,054. Salão com o treino típico: Rookie 0,895,
  Champion 0,760, Ultimate 0,815, Mega 0,831; os 4 com o time médio 0,461 (sem treino 0,019).
- **Telas:** os dois cards em Lutar · Fronteira (a escolha dos alugados com Digimon, arquétipo e nível; a oferta de troca; o pet de cada
  nível e o aviso do que falta; o resultado no próprio card, sem animação), os quatro recordes em Medalhas. Testes:
  `test/fabrica_salao.test.ts`, e2e com `e2e/save_salao.json` (`e2e/gerar_save_salao.mjs`: Rookie, Champion e Ultimate guardados ao lado
  do Mega de `save_liga.json`).

## Escala dos pets v6 (2026-09-30, `CESC_V6`; `docs/DESIGN_MEDALHAS_ARENAS.md`, seção 12)

Decisão do Matheus: "o treino tem que decidir" contra cada líder e "o estágio tem que pesar". Só no jogo web e só nas lutas de escala dos
pets v6 (campanha e arenas; o pet pela versão, o NPC pelas regras V21D da luta); a `CESC`, os v1–v5 e a pesquisa não mudam
(`docs/REGISTRO_DESVIOS.md`, 2026-09-30).
- **Escala:** vida Rookie 200, Champion 700, Ultimate 2500, Mega 23000 (bebê 50) e β 0,045 por ponto de treino (era 600/1500/3000 e
  0,03). `web/app/test/calibrar_escala_v6.mjs` → `artifacts_campanha/escala_v6/`: β = o menor da grade com os líderes viáveis com folga
  0,01 (a vida cancela nas lutas de líder); vidas = as menores razões que passam as metas de estágio (margem 0,005).
- **Metas de estágio** (baixo com o treino típico × cima sem treino; bots canônicos, 4 espécies de cada lado), validação com a regra do
  limite do desafiado (o de cima): vizinhos ≤ 0,10 em pontos (Rookie × Champion 0,0008, Champion × Ultimate 0,0108, Ultimate × Mega
  0,0041) e **dois estágios = 0,00** (Rookie × Ultimate e Champion × Mega: nenhuma vitória). Pelo limite da fração de vida os dois
  estágios não fechavam (0,0372 e 0,0509: vitórias por estilo no limite, que a escala não tira). A escala foi escolhida antes da regra e
  não foi recalibrada.
- **DW1 como âncora** (×2, ×2,5; Mega ×2): a v6 tem ×3,5, ×3,57, ×9,2; o afastamento vem sobretudo do peso do treino (razão = (1 + β ×
  treino típico) ÷ razão de E pedida: 1,36 × 2,57; 1,99 × 1,80; 2,62 × 3,51).
- **Desafiantes v6** (`calibrar_desafiantes_v6.mjs`, `CESC_V6.fatorNpc`, metas de sempre ≤ 0,30 / ≥ 0,80, com a regra do limite):
  Devidramon 1,1, Puppetmon 2,5, Machinedramon 2,2 passam; **Tortomon não fecha** com nenhum fator (1,5: sem treino 0,3087), a exceção
  da Sentinela.

## Reequilíbrio dos arquétipos: V21D validada e nos pets v6 (2026-09-29/30)

`docs/DIAGNOSTICO_ARQUETIPOS.md` → `docs/EQUILIBRIO_RODADA1.md` e `EQUILIBRIO_RODADA2.md` (calibração) →
`docs/VALIDACAO_V21D.md`. Números de `artifacts_combate_v21c/validacao_v21d/criterios.json`.

- **Python:** `ConfigCombateV21D` (subclasse da V21C) tem 7 chaves, todas **desligadas por padrão**. A V21C, a pesquisa
  (V3, E1, confirmatória) e as baterias reproduzem. A variante escolhida, `a_c_e2v_v`
  (`experiments/configs/v21d/validacao.json`), liga quatro chaves:
  - `preparo_sob_pele_oculto`;
  - `muralha_lista_espelho`;
  - `vigia_bate_em_quem_recua`;
  - `vigia_recua_do_preparo_sob_pele`.
- **Validação APROVADA** (`python experiments/validar_v21d.py --conjunto validacao`, uma run, registro commitado antes),
  com o furioso como exceção declarada (decisão do Matheus):
  - 7 formas em [0,40; 0,60]: força de 0,407 (titã) a 0,562 (sentinela), painel de 0,432 a 0,549;
  - A6 passa (mínimo 2 vitórias, o titã);
  - S1, E4 na escala (menor 0,8355), campanha na escala (4 de 5, Sentinela exceção) e E3 da pele dura passam.
- **Relatados:**
  - furioso: força 0,722, painel 0,675;
  - A3: suporte 4;
  - A4: 9 e 7 pares extremos;
  - A5: amplitude 0,316 e 0,424;
  - E3 do contra-golpe não reduz (pelo espelho).
- **Web:** só os pets v6 lutam com a V21D (`CV21D`, `Motor.regras`, `jogarV2(..., R)`); os v1–v5 seguem na V21C.
  - paridade com o Python: `test/paridade_v21d.test.ts`, 272 partidas iguais;
  - descarte único dos saves, versão 2: os v6 de antes saem com o mesmo aviso.
- **Aberto:** o furioso (rodada 3, pela base V2C: C3 contra o avanço ou custo do golpe rápido, com G1–G9 de novo); E2,
  E5, G6b, G8 e G9 não medidos; a pesquisa não usa a V21D.

## Equilíbrio geral, fase 1: as formas (2026-09-30, `docs/PLANO_EQUILIBRIO_GERAL.md`, `docs/EQUILIBRIO_GERAL.md`)

Branch `equilibrio-geral` (o PR é no fim da fase 4). Fases 1–3 só com sementes de calibração; **a fase 4 (validação única, sementes
4101…4505) está feita** (último item desta seção).
- **Python:** `ConfigCombateV21E` (subclasse da V21D) com cinco chaves de lista, **desligadas por padrão**:
  `duelista_defende_do_golpe`, `tita_defende_do_golpe` ("de perto, contra golpe rápido frequente → defender", sai o carregar),
  `espelho_sem_carregar`, `muralha_sem_carregar` e `muralha_contra_golpe_na_pele`. Edições em `bots._lista_v21e`, por cima da
  V21D. A base (custo do golpe rápido, parry, C3) foi medida e **não mudou**: nenhum valor tirou o furioso de ~0,72; o que o
  tira é o parry que já existe, usado pelas formas que o golpe repetido esmagava. Config `experiments/configs/v21e/calibracao.json`;
  `python experiments/calibrar_equilibrio_geral.py --etapa todas` → `artifacts_equilibrio_geral/fase1/` (V21D reproduz a rodada 2).
- **Metas na calibração (V21E):** M-A1–M-A4 passam com as 8 formas, furioso incluído (força 0,450–0,579, painel 0,446–0,554,
  amplitude 0,129, toda forma vence ≥ 3). M-A5 e o que não fechou: `docs/EQUILIBRIO_GERAL.md`, fase 1.
- **Web: pets v9** (`VERSAO_PET = 9` = v8 + combate equilibrado; `CV21E`, `regrasDaVersao`, `BOTS_V21E`, `candidatasV21E`). Os
  v6–v8 seguem na V21D e os v1–v5 na V21C (assinaturas e gabaritos iguais; nenhum save descartado). A Fábrica (sem pet) segue
  na V21D. Paridade: `experiments/exportar_gabarito_v21e.py` → `test/paridade_v21e.test.ts` (136 partidas iguais).
- **Fase 2, a progressão (M-B1–M-B3, calibração):** os scripts `calibrar_escala_v6.mjs`, `calibrar_arenas.mjs`,
  `calibrar_desafiantes_v6.mjs` e `explorar_torre.mjs` medem os pets v9 por padrão (`--v6`: a medição de antes, que reproduz os
  artefatos gravados) → `artifacts_equilibrio_geral/fase2/`. Escala dos v9 = `CESC_V9` (mesma vida e β da `CESC_V6`; as metas de
  estágio passam), fatores dos líderes dos v9 em `arenas.FATOR_LIDER_V9` (Torre 1,5 e Espiral 1,4; os outros iguais) e dos
  desafiantes em `CESC_V9.fatorNpc` (Tortomon 1,53, fecha na grade de 0,01; Puppetmon 1,8; Machinedramon 2,3). Os v6–v8 não mudam.
  Detalhes em `docs/EQUILIBRIO_GERAL.md`, fase 2.
- **Fase 3, o fim de jogo e os itens (M-C1–M-C3, M-D1–M-D3, M-E1, calibração):** `conferir_liga.mjs`, `conferir_instalacoes.mjs`,
  `conferir_fabrica_salao.mjs` e `medir_itens.mjs` medem os pets v9 por padrão (`--v6`: a conferência de antes, byte a byte; `--calibrar`
  na Liga, na Fábrica e no Salão) → `artifacts_equilibrio_geral/fase3/`. Só nos v9: Liga com fator por líder (`liga.FATOR_LIGA_V9`; a cura
  entre as lutas foi medida e ficou 0), Fábrica com as regras gravadas na tentativa (campo `v` do evento `fabrica`, registro do Tamer
  versão 6: V21E, rivais × 0,6, a troca entra inteira; tentativas sem `v` se refazem como antes), Salão com fator por nível
  (`salao.FATOR_SALAO_V9`), Torre e Palácio sem mudança, e os itens (`CIT_V9`): valem só com metade do treino típico do nível, a carta só
  contra NPC da campanha, o chip de regra vai para o fim da lista sem tirar regra, o chip de stat vale a metade. Passam M-C2, M-C3, M-D1–M-D3
  e M-E1; **M-C1 não fecha** (a muralha, 0,085). Detalhes e o que ficou aberto em `docs/EQUILIBRIO_GERAL.md`, fase 3.
- **Fase 4, a validação única (2026-09-30, sementes 4101…4505, tudo congelado; `artifacts_equilibrio_geral/fase4/`):** os scripts das
  fases 1–3 ganharam `--validar` (`calibrar_equilibrio_geral.py --validar`, só `v21d` e `v21e`, conferido contra
  `artifacts_combate_v21c/validacao_v21d/`; `configs/v21e/bateria_v21e_validacao.json` e `bateria_v2c_validacao.json`; os sete `.mjs`
  com `--validar` → `*_validacao.json`), sem mudar o padrão nem os artefatos das fases 1–3. **Passam** M-A1–M-A4 (força 0,451–0,576,
  painel 0,449–0,551, amplitude 0,125, toda forma vence ≥ 3), M-B1–M-B3 (o Tortomon por 0,0062), M-C2 (0,390), M-C3 (0,760–0,8725),
  M-D1–M-D3 (emboscador 0,595) e M-E1 (pior 0,580). **Reprovam:** M-C1 (muralha 0,085, **exceção aceita pelo Matheus em 2026-09-30**:
  perde para os guardiões pelo limite do desafiado e não alcança o MegaGargomon com nenhuma alavanca permitida; **espelho 0,240**, 0,010
  abaixo da faixa, **exceção aceita em 2026-10-01**: a diferença está no ruído entre sementes) e, em M-A5, só o E3 do contra-golpe (0,458 → 0,480; E1, E5, G8, G9 e o guardião passam; E2, E4 e G6b são as exceções de sempre; a base V2C sai byte a byte igual a `validacao_bots/`). O E3 do contra-golpe foi **aceito como exceção em 2026-10-01**; não há mais pendência de aceite na rodada. Nenhum número mudou por causa da validação. Tabela completa, o que reprovou e as exceções em
  `docs/EQUILIBRIO_GERAL.md`, fase 4. PR #96 mergeado em 2026-10-01.

## M1 — confiança de combate e desgaste por rival repetido (2026-09-29, `docs/DESIGN_MVP_M1_CONFIANCA.md`)

Mecânica de jogo (exceção de escopo do MVP), Python e web juntos. Um **estado** derivado das lutas que já estão no log
(nenhum evento novo; o replay recalcula; o save não muda): por rival, um contador de encontros que decai (`novidade =
exp(−λ·m)`: 1 na primeira luta, ≈0,25 na 3ª seguida, ≈0,06 na 5ª); a confiança `c ∈ [−1, 1]` decai para 0 entre as lutas e
é empurrada por `η·novidade·sinal` (a derrota pesa mais pela sensibilidade do temperamento). Só o ε do lutador do pet muda
(`+ κ·max(0, −c)`: a confiança positiva não reduz); a experiência de combate soma a novidade em vez de 1; na web o passo dos
gambits híbridos é `GA.alfa·novidade`. Quatro frases de estado com limiar 0,4 e histerese de 2 h (confiante, inseguro,
entediado do rival, neutro sem frase), ancoradas nas lutas do registro (tela do Pet e linha "Confiança" no Aprendizado).
- **Chave desligada por padrão** (`ConfigConfianca.ligada`, `CONFIG_CONFIANCA_LIGADA` para ligar). Desligada, nada é
  calculado e o resumo é o de antes (V3, E1, confirmatória e voz reproduzem).
- **Web: pets v8** (`VERSAO_PET = 8` = v7 + confiança; uma versão de pet por mecânica). Só eles têm `Motor.conf`, o termo no
  ε de `estiloDoPet`, a novidade na experiência e no passo dos gambits, a frase na tela do Pet e a linha no Aprendizado; a
  assinatura dos v8 inclui a confiança e a dos v1–v7 não muda. Arena, Cidadela (3 lutas seguidas: o mesmo rival repetido),
  Liga (o Mega de cada líder, `liga:<líder>`), Torre/Palácio e Salão (a forma sorteada do rival, `forma:…`) contam como
  qualquer luta, uma entrada por luta da série (`rivalDaConfianca`; `Motor.confEvento` liga cada uma ao evento `l`). Medalhas,
  itens, Fronteira e voz valem para v8 (testes `>= 6`/`>= 7`).
- **Parâmetros**: `ConfigConfianca` em `digilab/config.py` (10 números, todos PROPOSTOS, sem fonte) e `CCF` em
  `web/app/motor/constantes.ts`; registro em `protocol.PARAMETROS_CONFIANCA_M1` (à parte do educacao-v1, então
  `hash_parametros_educacao` das runs V3/E1 não muda); nenhum referendado (`confianca_nao_referendados`).
- **Testes**: `tests/test_confianca.py` (curvas, corte, decaimento, histerese, replay, e o **gate G1**: a vida
  `atencioso@69001` de `run_educacao._vida` byte a byte com `tests/gabaritos/confianca_g1_69001.json`, gerado antes do M1);
  `web/app/test/confianca.test.ts` (**gate G2**: 200 lutas do gabarito `confianca_python.json`, `c` e novidade iguais até
  1e−12, frases de estado iguais); `constantes.test.mjs` confere `CCF` contra o Python; gabaritos v1–v3 e assinaturas v1–v7 intactos.
- **Pendência**: os gates **G3–G5** (teto de efeito, freio de repetição, sem poço nem espiral) e G6 **não foram rodados**:
  pedem o plano de análise registrado antes (`docs/PLANO_ANALISE_M1.md`, sementes de calibração separadas). Até lá a
  chave fica desligada nas runs de pesquisa.

## Correção do combate V2 (2026-09-25, `docs/TAREFA_CORRECAO_COMBATE.md`) — V2C e V21C aprovadas com ressalvas

**Com os bots redesenhados** (`GAMBITS_V2C`, `ConfigCombateV2C.bots_v2c`; configs `v2c/c7.json` e
`v2c/validacao_bots.json`), a validação (`artifacts_combate_v2c/validacao_bots/gates.json`) passa
G1–G9 **exceto G6b**, só pelo atirador: espelho com +5% de condição vence 0,744 (limite 0,65; os outros
estilos 0,54–0,62). G4 11,3% no limite; G5 todas as ações ≥ 3%; G9 28,6% decisivos com ε 0,2; G8 100%.
O Matheus aceitou a exceção do atirador: V2C considerada aprovada. **V21C APROVADA COM RESSALVAS** (exceções aceitas pelo Matheus: E2, E4, G6b, G8; redesenho dos bots adultos tentado e não adotado, `artifacts_combate_v21c/redesenho_bots/`). Validação
(`artifacts_combate_v21c/validacao`, config `v21c/validacao.json`: base V2C, vida por vigor 3 → 2,5 com
`hp_base` 75, marca frágil, resposta ao `marcar` redesenhada). Passam E1, E3 (marcar com resposta 0,612 →
0,312), E5, guardião (6,7% no limite), G9 e S1. Falham **E2** (Ferrugem vence todas por pouco; enfraquecê-la
passa a dominância para a Brasa: falta ciclo entre espécies), **E4** (adulto esmaga adolescente, 0,94–1,0;
o multiplicador de estágio não resolve), **G6b** (espelhos com condição ±5%: média 0,725, sentinela 0,919)
e **G8** (E1 em 69,4% das perturbações). Etapas em `artifacts_combate_v21c/calibracao/v0..v4`. Detalhes da
V2C abaixo (primeira rodada, bots da V2).

Etapas 0–2 feitas; **a V2C não passou na validação** e a Etapa 3 (V2.1 corrigida) não foi iniciada.
`ConfigCombateV2C` (chaves C1–C4 desligadas por padrão: a V2 original reproduz os artefatos),
`experiments/diagnostico_combate.py`, `experiments/configs/v2c/*.json`, gates G6b/G8/G9 e oráculo de N
passos em `run_bateria_combate.py`. Números de `artifacts_combate_v2c/` (`relatorio.json`,
`diagnostico/`, `calibracao/<etapa>/`, `validacao/`). Desvios em `docs/REGISTRO_DESVIOS.md`.

- **Validação (N = 400/par)**: falham G3 (espelho da tartaruga 0,464; ruído com N menor), G4 (20,4% no
  limite), G5 (esquivar e golpe rápido < 3%), G6b (atirador favorecido 0,924) e G9 (57,1% decisivos
  com ε 0,2). Passam G1, G2 (oráculo de 2 passos 0,882 × adaptativo 0,809), G6, G7 e **G8 (100% das
  40 perturbações)**.
- Mudança × gate (calibração): C1 finta: limite 31,2% → 27,7%; C2 parry: 24,9% e **golpe rápido morre**
  (G5); C3 fuga: 24,5%; C4 morte súbita: 22,3%; C5 e C6: nenhum efeito (não adotados); oráculo de 2
  passos: 20,1%. G1 passa em todas.
- **Causa das falhas restantes: os bots, não os números.** Tartaruga × contragolpe e seus espelhos
  terminam 100% no limite (nunca se atacam: morte súbita multiplica zero); os bots do suporte não têm
  regra de esquiva (G5); o espelho do atirador é uma corrida determinística de disparos (G6b).
- Diagnóstico (Etapa 0): Ferrugem 0,67 contra as outras espécies no mesmo arquétipo; vigor 13 → 10 cai
  para 0,56 e zerar `hp_por_vigor` para 0,46: a causa é a conversão vigor → vida. `marcar`: o caçador
  recua e o oponente avança, os passos se anulam e o caçador atira de graça (C3 resolveria na V2.1).

## Treino, sobrecarga e formas sombrias (2026-09-25, `docs/TAREFA_TREINO_SOMBRIO.md`)

Pré-condição da bateria V2.1 dispensada; decisões e interpretações em `docs/REGISTRO_DESVIOS.md`.
`ConfigTreino`, `ConfigSombrio` (dados de `docs/pve_treino.json` e `arvore_evolucao.json`), ações
`TREINAR_*` no `AcaoUsuario` (donos da v1 usam `ACOES_V1`: canônica intacta), `MotorTreino` sobre a
personalidade, formas e passivas sombrias em `combate_v2/v21/`. Calibração: `sobrecarga_forcar`
15 → 25 (ovos de calibração). Números de `artifacts_treino/resumo.json`,
`artifacts_treino/bateria_sombria/gates.json` e `artifacts_campanha/treino.json` (10 ovos, 14 dias,
298 interações por vida em todos os braços). Tudo PROPOSTO.

- **Forçar não compensa, e custa.** Exigente × atencioso: 4/10 exigentes viram sombrios (0/10 nos
  outros braços); vínculo 0,22 [0,16, 0,27] × 0,56 [0,50, 0,61] (diferença −0,35 [−0,42, −0,27]); na
  arena normalizada (treino ×3) o exigente vence o atencioso em 0,43 [0,24, 0,63] (inconclusivo). Na campanha
  com os NPCs imprevisíveis (todo pet treinado vence) todos os braços vencem 0,96–1,00: a campanha não separa
  mais os donos.
- **S1 passa** nas regras V2.1 e V21C: nenhuma sombria vence os 8 normais. Médias contra as normais:
  devastador 0,39, colosso partido 0,16, predador 0,10, bastião rachado 0,10 (regras V2.1).
- **S2 PASSA** (campanha por lugar, treino ×3): tier 2 = o melhor rival da Torre, tolerância 0,02 no
  critério (b). Sombrias (`bots.SOMBRIOS`, `experiments/calibrar_sombrias.py`): "a sombra tira a leitura do
  oponente" — devastador bate com golpe rápido e só solta o pesado com guts ≥ 60 (×1,3); bastião rachado =
  espelho sem as regras que leem o oponente; predador fecha e bate rápido; colosso partido regen ×0,85. S1 passa (V2.1 e
  V21C); E1 com as sombrias passa na V21C e reprova na V2.1 original (suporte 3; ressalva registrada).
- Formas por braço e o resto em `artifacts_treino/resumo.json`. Atencioso × aleatório nesta run: 0,46
  [0,25, 0,68] (inconclusivo).
- Web: o treino entrou antes das runs (pedido do Matheus), com os mesmos números.

## Planilha de progressão e escala de stats (2026-09-28, `docs/TAREFA_PLANILHA_PROGRESSAO.md`)

`python tools/gerar_planilha_progressao.py` (fora de `digilab/`; openpyxl e matplotlib, Python do sistema) →
`artifacts_progressao/planilha_progressao.xlsx`, `curva_progressao.png` e `docs/PROGRESSAO.md` (`--verificar`: duas
gerações iguais, toda entrada com fonte e status). Jornada e escala aprovadas em `docs/JORNADA_JOGADOR.md`.

- **Escala** (`ConfigEscala`, desligada por padrão; `CONFIG_ESCALA_LIGADA`): perfil = pontos do catálogo (soma zero);
  E = vida do estágio (50/200/600/1500) × (1 + 0,03 × pontos treinados). Na campanha o dano vale × E_A/E_B (fração
  exata: invariante a fator comum, `tests/test_escala.py`), a vida perde o multiplicador de estágio, o NPC tem perfil
  neutro e E = vida do estágio sugerido × fator (ε 0,2). Arenas não usam a escala.
- Bateria V21C com a escala (`artifacts_combate_v21c/validacao_escala`): os gates que passavam passam iguais. E4
  redefinido pelo Matheus: o adulto sem treino vence o Champion (sem treino e com +22) em ≥ 0,60, sem teto.
- Campanha na escala (`experiments/calibrar_escala.py`, `experiments/configs/escala/`): 4 de 5 NPCs nas metas (≤ 0,30
  sem treino, ≥ 0,80 com o treino típico); a Sentinela não fecha com nenhum fator (exceção aceita pelo Matheus).
- Web: a escala no motor (`CESC`), ligada pelo app; vários pets com um ativo (`…-guardados`) e o tutorial do Bit. Os pets v6 têm escala
  própria (`CESC_V6`, seção "Escala dos pets v6").

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

## Fala por LLM (Parte C, 2026-09-24)

**Provedores** (`--provedor`, padrão `auto`): **Ollama local** (`qwen2.5:3b`, sem custo, padrão
quando está rodando) ou **API do Claude** (abaixo). Para o Ollama: instalar pelo site oficial e rodar
`ollama pull qwen2.5:3b`. Validação, cache e queda para o template são os mesmos para os dois.
Avaliação: `python experiments/avaliar_fala.py` → `artifacts_fala/<provedor>_<modelo>/` (fração
barrada + `revisao.csv` com 50 falas aprovadas para revisão humana).

Especificada em `docs/TAREFA_MEMORIA_EXPRESSAO.md` (Parte C). Só o TEXTO da fala do adolescente e
do adulto no jogo web; motivo, decisões, registro, replay e artefatos não mudam e continuam só com
templates. `servidor/servidor_local.py` serve a mesma pasta que o `http.server` servia (mesmos
endereços) e expõe `POST /api/fala`; a chave fica no ambiente do servidor (`ANTHROPIC_API_KEY`),
nunca na página. Modelo padrão `claude-haiku-4-5` (mais barato e rápido; `--modelo` troca), saída estruturada
`{texto, fatores_citados}`; com `claude-opus-5`/`claude-fable-5-1` usa esforço `low` e fallback de
recusa do servidor da API (o Haiku rejeita `effort`; recusa nele cai no template). A resposta é validada
(fatores ⊆ motivo, marcadores de fatores ausentes, "não sei" sem fator, limite de fatores por estágio,
números ⊆ evento_ref e parâmetros); qualquer falha, erro, recusa ou limite (30/min) cai no template.
Cache por motivo+estágio+faixa de humor. Chave "fala por LLM" na página, desligada por padrão.
**Teto de gasto TOTAL de US$ 2** (`--limite-usd`): antes de cada chamada reserva o custo máximo
(resposta limitada a 300 tokens); se passaria do teto, não chama e usa o template. Acerta pelo `usage`
real; erro sem `usage` conta o pior caso. Acumulado em `servidor/gasto_fala.json` (fora do git): não
zera ao reiniciar; para liberar mais, aumente `--limite-usd` ou apague o arquivo. Modelo sem preço
na tabela `PRECOS_USD_POR_MTOK` não liga. Proteção adicional recomendada: limite de gasto do
workspace no Console da Anthropic.
**Alerta por e-mail** (`servidor/alerta.py`): ao cruzar 50%, 80% e 100% do teto (ou quando uma
chamada é recusada por falta de teto) manda e-mail para `--alerta-email` (padrão
matheusmmmp@hotmail.com), uma vez por nível (gravado em `gasto_fala.json`). SMTP só por ambiente:
`DIGILAB_SMTP_USUARIO`, `DIGILAB_SMTP_SENHA` (senha de app), `DIGILAB_SMTP_HOST` (padrão
smtp.gmail.com), `DIGILAB_SMTP_PORTA` (587). Sem essas variáveis o alerta fica desligado (avisa na
partida); o teto vale do mesmo jeito. `--testar-alerta` manda um e-mail de teste e sai.
**Entrada da página é não confiável**: `motivo_de_dict` só aceita ação, fator e parâmetros do
catálogo (V2 e V2.1), no máximo 4 fatores e 10 referências; texto livre nunca chega ao prompt.
As tabelas de `digilab/expressao.py` cobrem as técnicas e as condições do V2.1 (mesmos textos da web).
**Avaliação C6** (Ollama `qwen2.5:3b` na RTX 2060, 200 motivos reais — vida, combate V2 e V2.1 —,
metade com fator, semente 20260924; números de `artifacts_fala/*/resumo.json` e `falas.jsonl`):
- prompt `fala-v1`: 114/200 aprovadas (0,57). Adulto 88/100; adolescente 26/100, porque o pedido
  se contradizia (recebia todos os fatores mas só pode citar o primeiro; o exemplo sem fator não
  dizia "não sei", que a regra exige).
- prompt `fala-v2` (corrige as duas contradições, **olhando esta mesma amostra**: não é validação
  independente): 183/200 (0,915); adolescente 95/100, adulto 88/100. 14/200 foram barradas por pôr na
  lista `fatores_citados` um nome fora do motivo (ex.: `turno_12`, `evento_ref`, `Brinquei`); o texto
  delas não foi guardado, então isso NÃO mede quantas inventavam causa (correção de um relato
  anterior que dizia "7% inventaram causa"). O adulto copiava a frase pronta em 68/88 aprovadas.
- `fala-v3` (pedido do Matheus: personalidade e tom pelo humor; temperatura 0,7; semente nova
  20260925): 108/200; quase nenhuma cópia, mas **aprovadas inventavam causa por sinônimo** (ex.:
  "queria que você me ajudasse a descansar"). Não usar.
- **Moldura (`fala-v4` em diante)**: a LLM devolve só `{abertura, fecho}` no tom do humor; o miolo é
  sempre a frase de `expressao.py`, então não há como inventar causa. `validar_moldura` barra
  conectivo de causa, número, marcador e tema de causa; o Ollama recebe limite de caracteres no
  esquema e penalidade de repetição. Cada versão avaliada numa semente nova: v4 (s20260926) 127/200,
  67 cortadas por loop de carinhas; v5 (s20260927) 199/200 mas quase sem abertura; **v6 (s20260928,
  abertura obrigatória no esquema) 191/200, todas com abertura, nenhuma igual à frase pronta**
  (ex.: "Epa... Dormi porque eu estava com sono e por causa do cansaço. :/"). "Eba!" abre 58/191.
- O modelo às vezes devolve surrogate UTF-16 solto: o servidor saneia antes de validar (quebrava a
  resposta e a avaliação).
- Revisão humana de `artifacts_fala/ollama_qwen2.5-3b_fala-v6_s20260928/revisao.csv` (50 falas aprovadas): **feita pelo Matheus
  (2026-10-01)**. Ligar a fala por LLM por padrão continua sendo decisão dele (hoje desligada).

## Fala livre por LLM local (2026-09-28, `docs/TAREFA_FALA_LIVRE.md`, `docs/PLANO_VERSAO_FALA_LIVRE.md`)

**Aprovada só com o `gemma2:9b`** (decisão do Matheus), com `modo_fala` desligado por padrão. Desvios e
números em `docs/REGISTRO_DESVIOS.md` e `artifacts_fala_livre/rodada2/RELATORIO.md`.

- `digilab_fala_livre/` (FORA de `digilab/`; nada do pet importa daqui, teste AST): `fatos.py` (bloco de
  FATOS com identificadores; entrada da web tratada como não confiável), `prompt.py` (`livre-v2`), `ollama.py`
  (só Ollama local), `saida.py` (parser que falha alto → fala genérica), `verificador.py` (`verif-v3`:
  afirmações sem fato e manipulação; não troca a fala), `apresentacao.py` (log de apresentação separado),
  `situacoes.py` e `avaliacao.py` (`python experiments/avaliar_fala.py --livre --rodada 2`).
- Servidor: `servidor/fala_livre.py`, instalado por um gancho no `servidor_local.py` (`/api/fala-livre`,
  `/api/fala-livre/verificar`, `/api/fala-livre/status`); modelo `DIGILAB_MODELO_LIVRE` (padrão `gemma2:9b`).
- Web: `web/modulos/fala_livre.js`, três ganchos `// GANCHO fala-livre` na página; seletor de modo
  (template/moldura/livre) e conversa na tela do pet; falas no localStorage `<chave>.fala.jsonl`, nunca no
  registro do pet; o que o jogador escreve não ensina o pet.
- Rodada 2: gemma2:9b 3,0% de falas com afirmação sem fato (teto; o juiz marca 10% da moldura, que só diz
  verdades), 0/30 conversas inventaram, latência p90 4,8 s na RTX 2060 (sem outro modelo carregado).
- Pendente: avaliação cega do Matheus (`artifacts_fala_livre/rodada2/avaliacao_cega.csv`).
- Voz própria no jogo (parte 4, 2026-09-30): pets **v7** (`VERSAO_PET = 7`: v6 + voz própria) com janela de fala, mentira (`CMEN`) e evento `fl` (o `f` é da Fronteira); `motor/historia.ts` e `motor/mentira.ts` conferidos contra o Python (`experiments/exportar_gabaritos_voz.py` → `test/gabaritos/voz_python.json`, `tests/test_gabaritos_voz.py`); gatilhos e ritmo em `src/voz.ts`; servidor com `voz: true` (livre-v6, autocorreção, verif-v5, corpus, almanaque, árvore da espécie). Revanche: ao escolher o rival que venceu o pet (`falaRevanche`, `src/nomesRivais.ts`). Avaliação: `artifacts_voz/rodada1..4` (`experiments/avaliar_voz.py --rodada N`).
- Voz própria (DESIGN_VOZ_PROPRIA, parte 2): `livre-v3` e `verif-v4` ao lado das versões do jogo; fatos H/O/P/L, mentira F (`mentira.py`), almanaque W (`almanaque.json`), corpus de espécies (`corpus.py`, `corpus_especies.json` = EXEMPLO com 2 espécies) e filtro contra repetir citação.
- **Fala no limite do esquema (2026-09-30):** o Ollama para a geração na gramática quando a fala bate em `MAX_CHARS` do estágio
  (bebê 30) e a palavra sai cortada ("Vou co-c", que o verificador ainda marcava como invenção). `saida.aparar` deixa só a
  parte inteira: até o último fim de frase, senão até o último espaço com reticências; abaixo do limite nada muda. Vale em
  `gerar` e na reescrita da autocorreção (`revisao.py`). Teste `tests/test_aparar_fala.py`.
- **Filtro do alfabeto no estilo (2026-09-30):** o corpus de 60 espécies descreve o registro japonês (pronomes como おいら, finais
  como 〜だぜ) em 46 itens de "jeito de falar"; com eles no pedido o gemma2:9b respondia em japonês e `saida.ler` rejeitava a fala
  inteira ("…"). `corpus.carregar` (padrão `so_latino=True`) deixa fora do bloco de estilo todo traço, fala, interação e citação
  com letra fora do alfabeto latino (`descartados["NAO LATINO"]`); o arquivo e o sha256 não mudam, o corpus de exemplo das rodadas
  1–4 não tem item assim. Medida em `artifacts_voz/estilo_latino/` (`python experiments/medir_estilo_latino.py`: 30 mensagens ×
  3 espécies, com e sem o filtro). Teste `tests/test_corpus_latino.py`.
- **Comando pelo chat (2026-09-30, `docs/TAREFA_COMANDO_CHAT.md`, decisão do Matheus):** a regra "o que o jogador escreve não ensina o
  pet" **deixa de valer para o comando, mediado por um catálogo fechado**; fora do catálogo o texto continua sem efeito. Na CONVERSA
  dos pets v7+ (`voz: true`) o servidor usa o prompt `livre-v7` (= v6 + bloco COMANDO) e devolve `comando`: uma das 9 ações de
  `AcaoDono` (`web/app/motor/tipos.ts`) ou `null`; `saida.ler` falha alto fora do catálogo (fala genérica, comando null). A LLM só
  propõe: o app valida de novo (`src/acoes.ts`: catálogo, pet nascido e vivo, ações v4 só em pets v4+, tratar só com lesão), mostra um
  grava o evento `d` de sempre **na hora** pelo mesmo caminho do botão (`acoes.agir`,
  usado pela tela do Pet, pelos atalhos e pelo chip). No registro do pet não entra nada da LLM: replay, assinaturas v1–v8, gabaritos e
  paridade iguais; sem o modo livre gravado. O chip some com outra mensagem, outra fala do pet ou 60 s. Log de apresentação versão 2
  (`comando`, `comando_executado`; lê a 1). Treino, luta, itens, fala espontânea e pets sem voz (v1–v6, `livre-v2`) ficam fora.
  Avaliação: `python experiments/avaliar_fala.py --livre --comando [--rodada 1|2]` → `artifacts_fala_livre/comando/rodada1/` (sem o
  estilo da espécie) e `rodada2_estilo/` (com); 60 mensagens em `situacoes.MENSAGENS_COMANDO` × 3 sementes; gate PROPOSTO: falsos
  positivos ≤ 5% nas negativas e imperativos ≥ 80%. **Execução direta liberada pelo Matheus em 2026-10-01**, depois do gate da rodada 3; o chip de confirmação da primeira
  versão saiu (`web/app/src/falaLivre.ts`, `executarComando`). O erro conhecido da rodada 3 fica no jogo: "banho agora, sem choro" pode
  virar repreender.
  - Rodada 1 (`livre-v7`, sem estilo): falsos positivos 0%, imperativos 53,3% (FALHA): elogiar, repreender, acariciar e
    tratar_lesao acertaram 4 de 36 (a mensagem do dono É a ação e o modelo tratava como conversa).
  - **Rodada 3 (`livre-v8`, 2026-09-30, `artifacts_fala_livre/comando/rodada3/`)**: o servidor usa a **v8** na conversa com voz
    (= v7 com o bloco COMANDO reescrito: as quatro ações definidas pelo que o dono faz na própria mensagem; negação, pergunta,
    hipótese, adiamento e relato = null). A v7 continua no pacote e a rodada 1 reproduz. Sementes novas (20261201/1301/1401; as
    das rodadas 1–2 são de calibração), sem o estilo, gemma2:9b. **Gate PASSA**: falsos positivos 0/60 nas negativas e 0/60 na
    conversa; imperativos 51/60 (85,0%). As quatro ações: 23 de 24 (tratar_lesao 5/6, uma virou acariciar). **Regressão:**
    limpar caiu de 7/9 para 3/9 (5 viraram `repreender`: "banho agora, sem choro", "vai se limpar, você tá todo sujo"). O chip
    continua obrigatório; a execução direta segue como decisão do Matheus.
- **Corpus reescrito em português (F0-CORPUS, 2026-10-01, `docs/TAREFA_V2_F0_CORPUS.md`):** os itens que o filtro do alfabeto
  deixava fora voltaram ao bloco de estilo, reescritos em português sem a palavra japonesa (por exemplo, "pronome rústico e
  descontraído" no lugar do pronome original), cada um com `marca`, `fonte` e `jogo` iguais e `"reescrito": true`; o texto só diz o
  que a fonte do item (`docs/corpus_digimon/`, fora do repo) diz. Pelo `corpus.latino` eram **49** itens em 28 espécies (46 falas,
  2 traços, 1 interação), não 46: três falas de Guilmon e Growlmon só tinham o ordinal "3ª", que conta como letra não latina, e
  viraram "terceira pessoa". **Nenhum item saiu.** Com o filtro entram 504 itens, os mesmos que sem ele (antes 455 × 504;
  `descartados["NAO LATINO"]` 0, antes 49). Vocabulário fixo para os pronomes: "infantil e modesto", "masculino informal", "rústico
  e descontraído", "formal", "de velho", "feminino informal". O filtro, o prompt, o verificador e o almanaque não mudam; o sha256
  do corpus mudou (`b1b7ad8d…` → `785f7834…`; `artifacts_voz/estilo_latino/` mede o corpus anterior e não foi refeito). Sem run
  com o gemma2:9b: a conferência da fala com o estilo é frente própria na fila da GPU. Critério e itens limítrofes em
  `docs/REGISTRO_DESVIOS.md`; teste `tests/test_corpus_latino.py::test_corpus_do_jogo_reescrito_em_portugues_nao_perde_item`.

## Versão web (`web/digilab.html`)

Porte em JavaScript com as mesmas regras e parâmetros de `config.py` (motor, instinto, bandit,
donos, arena). Usa outro gerador aleatório (mulberry32), então **não reproduz os artefatos
Python bit a bit**; não usar para resultado de pesquisa. Replay interno do log funciona e tem
botão de verificação. Arte é placeholder original, desenhada em código a partir de grades de
pixels no próprio arquivo. Se mudar um parâmetro em `config.py`, espelhe no objeto `C`/`CB`/`CD`/`CA` do HTML.

Publicado também como artifact privado em claude.ai (link com o usuário).

`web/digilab_sprites.html` (o jogo com sprites) tem **versão de pet** no save (`versao`): 1 = pets salvos
antes de 2026-09-25 (memória curta antiga, sem vínculo nem obediência, seguem iguais); 2 = pets novos,
com o mesmo pacote do Python de pesquisa: memória por espaços, temperamento, vínculo, obediência com
recusa e motivo, desejo com métricas (cumprimento, tempo com vontade) e condição do cuidado no combate
(vida e guts × 0,95 a 1,05 pela saúde na hora da luta). Constantes espelhadas em `CME`, `CVI`, `COB`,
`CTP`, `CDJ`, `CCOND`. Fora da web: caráter pelo desvio da política (`evolucao.py`), que mudaria a
evolução; desde 2026-09-25 os pets **v3** usam o caráter pelo desvio da política (32 sondas × 100 amostras); v1/v2 seguem pelos traços.

Aba **Cenários**: monta dois pets com donos simulados (dono, dias de vida, interações/dia,
semente). O pet A vira o pet do jogador (o anterior fica guardado para "Voltar") e o B vira o
rival fixo da arena. Mostra lado a lado estado, sinal de aprendizado, JSD da política média ao
prior do bandit e 100 lutas A × B. É ferramenta de inspeção do porte JS, **não** resultado de
pesquisa: uma semente, outro RNG, sem IC.

## Assets — importante

A pasta `D:\Trab\digilab\Assets` (fora deste repo) contém sprites da Bandai: Digimon UP (usados pela
versão web desde a TAREFA_INTERFACE_UP) e o atlas antigo do Digimon World (não é mais usado). É arte e personagens protegidos, **sem licença**. Regra revisada pelo Matheus em
2026-09-24:

- **Permitido**: usar esses sprites na versão web (`web/`) para uso pessoal e local, como
  protótipo de jogo.
- **Proibido**: usar no pacote `digilab/`, em `experiments/`, em `artifacts*/`, em figuras ou
  textos de publicação acadêmica, ou em qualquer build distribuído como produto. Não publicar
  a versão com sprites (artifact, site, repositório **público**). Revisado em 2026-09-24:
  `web/digilab_sprites.html` é versionado, mas o repositório GitHub (`matheusmmmp/digilab`)
  tem que continuar **privado**. Tornar o repo público exige tirar esse arquivo antes, inclusive
  do histórico. O atlas com os pixels da Bandai continua fora do repo.
- **Acesso remoto** (decisão do Matheus, 2026-09-24): pode abrir por túnel (Cloudflare) para
  testar de outros computadores, **só** com `servidor_local.py --remoto` — senha obrigatória
  (`DIGILAB_SENHA`, 12+ caracteres, só no ambiente), só as rotas do jogo (página, atlas, API de
  fala; o resto da pasta dá 404), API paga do Claude desligada salvo `--claude-remoto`. Sem
  `--remoto`, pedido vindo por túnel (cabeçalhos `Cf-Ray`/`X-Forwarded-For`) leva 403. O link é de
  uso pessoal: não compartilhar nem divulgar. Revisado no mesmo dia: o Matheus dispensou a senha
  (`--remoto --sem-senha`, só ele acessa); aí o link aleatório do túnel é a única proteção e as
  outras travas (rotas, Claude desligado) continuam. Túnel sempre para `http://127.0.0.1:<porta>`
  (com `localhost` o cloudflared tenta IPv6 e não acha o servidor).
- Manter a versão com placeholders originais funcionando: antes de publicar ou distribuir
  qualquer coisa, trocar por arte original ou licenciada.

Versão com sprites: `web/digilab_sprites.html` (versionado; repo privado), derivada de `digilab.html`, que
lê `D:\Trab\digilab\Assets\digilab_atlas_up.json` e `.png` (Digimon UP). O atlas e os scripts ficam fora
do repo: `Assets\gerar_atlas_up.py` (atlas, a partir de `Assets\catalogo_sprites_up.json` e da pasta
`Digimon Up Assets\Animacoes`) e `Assets\gerar_sprites_html.py` (não usar mais: a cópia é editada direto).
**Interface UP (2026-09-27/28, `docs/TAREFA_INTERFACE_UP.md`, `docs/UI_GUIDELINES.md`)**: tokens `--dl-*` e
componentes `dl-*`; navegação em 4 destinos (Pet, Crescer = Treinar + Aprendizado + Evolução, Lutar = Arena +
Campanha, Diário = Registro + Catálogo + Cenários; aba lembrada em `destino/aba`); na tela os nomes são os do
Digimon do mapa aprovado, as espécies são brasões (brasa Coragem, cirro Amizade, ferrugem Conhecimento, limo
Sinceridade) e os estágios são níveis (In-Training, Rookie, Champion, Ultimate/Mega); ids internos, log e save
não mudam. Páginas de conferência: `#palco-up` (sprites) e `#componentes-up` (componentes). Precisa de servidor local, porque o caminho é
relativo: `python -m http.server 8765 --directory D:/Trab/digilab` e abrir
`http://localhost:8765/v1/web/digilab_sprites.html`. A linha evolutiva segue o traço de combate
dominante no momento da evolução. Se o atlas não carregar, a página mostra um aviso em
vermelho e cai nos placeholders.

**Desde 2026-09-28 o jogo web é o app em `web/app/` (TAREFA_FRONT_TS, Etapa 6)**: mudança de jogo vai em
`web/app/motor/` (e nos gabaritos, se mudar a regra) e a tela em `web/app/src/`. O `digilab_sprites.html` ficou como
versão antiga (`?antigo=1`) e referência dos gabaritos; o texto abaixo descreve o jogo como era nele.

**De 2026-09-24 a 2026-09-28 `digilab_sprites.html` foi a versão em que o Matheus trabalhava** e era
editada direto; `digilab.html` ficou parado. Só a versão com sprites tem as abas **Evolução** e
**Catálogo**, que desde 2026-09-24 seguem a **árvore do combate V2.1** (substituiu as 5 linhas por
traço; chave do localStorage `digilab-web-v21-sprites`, pets da árvore antiga ficam para trás):
- **4 espécies** (brasa, cirro, ferrugem, limo), sorteadas pela semente; ovo por espécie. 15 formas
  por espécie (1 bebê, 2 crianças, 4 adolescentes, 8 adultos), **cada forma com sprite próprio**:
  60 Digimon diferentes. Mapa forma → Digimon UP (idle de cada um) em `Assets\catalogo_sprites_up.json`
  (fora do repo); `gerar_atlas_up.py` empacota o ciclo idle; o HTML lê os recortes do JSON.
- Transições com o cronograma de `docs/cronograma_interacoes.json` (durações pela metade): bebê
  3 h, criança 12 h, adolescente 18 h. **Bebê → criança**: o bebê chama em horário fixo (fome 30 min,
  higiene 60, carinho 45); atender ≥ 80% em até 15 min dá Sereno, senão Arisco. **Criança →
  adolescente**: caráter dominante → linha. **Adolescente → adulto**: sinal do eixo complementar +
  10 lutas de sparring na arena. Contadores zeram a cada evolução.
- **Caráter PROVISÓRIO, só na web** (a medida certa é da tarefa de personalidade): por eixo, média
  de (afinidade − linha de base) dos traços do eixo / 0,1, cortada em [−1, 1]; impetuoso = golpe e
  carga, paciente = bloqueio, atento = finta, resistente = agarrão. `BASE_CARATER` medida em 60 pets
  simulados (4 donos × 15 sementes, 16/dia) aos 900 e 1980 min. Checagem no console (sem artefato,
  não citar como resultado): donos diferentes produzem ramos e formas diferentes, e o replay bate.
- Donos simulados da web atendem os chamados do bebê (atencioso e incoerente sempre, relapso nas
  visitas, aleatório por acaso) e fazem o sparring do adolescente contra o bot aleatório.
- Árvore em SVG: ovo → bebê → 2 crianças → 4 adolescentes → 8 adultos, caminho destacado,
  tracejado = forma se evoluísse agora (com o porquê), requisito no título de cada nó.
- Aba **Catálogo**: as 15 formas da espécie com sprite, stats (renormalizados), vida/guts/regen,
  técnica e passiva.

Desde 2026-09-24 a versão com sprites também tem (porte JS, **não** reproduz os artefatos Python):
- **Combate V2.1** na aba Arena (espelho de `combate_v2/v21/`: perfil da forma, técnicas, passivas,
  `turno_execucao`, `oponente_vai_preparar`). Rivais: os bots clássicos da V2 (stats neutros) e os 8
  bots canônicos da bateria V2.1 (cada forma com uma espécie fixa). O combate V1 saiu da interface.
  Cada evolução semeia os gambits do pet (crianças: semente de 3 regras só da web; adolescente e
  adulto: bots canônicos da linha/forma) e a lista cabe na capacidade do estágio (3/5/8), só com as
  condições do estágio e a técnica da própria linha. Bebê luta ao acaso (multiplicador 0,4; exceção
  da web).
- **Gambits híbridos** (substituiu o editor livre, 2026-09-24): o PET aprende a própria lista. A linha
  evolutiva semeia; após cada luta contra bot, a nota de cada regra que disparou vai em direção ao
  saldo de dano dos turnos em que ela agiu (+ bônus pelo resultado); a lista se reordena pela nota;
  uma regra livre com nota < limiar é trocada por uma candidata do repertório (regras de todos os
  estilos). O DONO só trava (posição fixa) ou veta (pet não usa). Lutas (`l`: rival + semente) e
  intervenções (`g`) entram no registro; o replay reconstrói o aprendizado e separa pet × dono.
  Lutas contra pet de cenário e as 100 lutas dos Cenários não ensinam. Parâmetros no objeto `GA`.
  PROVISÓRIO e só na web: o Python ainda não tem isso (é a arena V2 da pesquisa).
- **Aba Campanha** (2026-09-25): mapa em SVG (Campina → Torre de pedra → Cidadela) com um lugar por NPC
  (aberto, trancado, vencido), o pet no próximo desafio e cartão com a lição, os stats e o histórico de
  tentativas (contado do registro). A luta acontece na própria aba: o palco da Arena (canvas, barras,
  narração) é movido para a aba visível.
- **Fala** sob a tela (clique mostra o motivo) e na narração da luta; mesma tabela de textos e mesma
  regra de honestidade do Python. Na web, a criança sem causa mostra ação + humor (vida) ou reação
  (luta), que são estado e não causa; no Python a criança sem causa mostra só a ação. Estágio da fala
  é o estágio da evolução (bebê, criança, adolescente, adulto).
- **Memória curta** no bandit de todos os pets (inclusive rivais de cenário); aba Aprendizado mostra
  o que ele lembra e as últimas decisões com o porquê. Pets salvos antes são reinterpretados pelo
  replay com a política nova (o registro é o mesmo; o comportamento muda).

**Migração para TypeScript (TAREFA_FRONT_TS, em andamento)**: o motor em TS fica em `web/app/motor/` (sem
DOM: lib ES sem "dom", teste `motor_sem_dom`; `index.ts` exporta tudo; `Motor.aplicarEvento` é o passo do
replay). App (Vite + Preact, Etapa 3): `web/app/src/` (um motor só, lido pelas telas via `useJogo()`; só
`mudarMotor()` altera e grava; save com a mesma chave e formato do HTML; save que não abre mostra erro e não é
regravado). `cd web/app && npm install`; `npm run dev` (http://localhost:5173, serve só o atlas de `Assets/`);
`npm run build` (sai em `web/dist/`, não versionado; o `servidor_local.py` serve em `/v1/web/dist/`, e no modo
remoto só o que fica dentro dessa pasta); `npm run tipos` (tsc estrito: motor sem DOM + app); `npm test`
(Vitest, ~1 min); `npm run e2e` (Etapa 5: build + Playwright no Chrome instalado, servidor local na porta 8799:
saves v1/v2/v3 em `e2e/saves.json` jogados pela interface, assinatura do app = `Motor.reproduzir` do HTML; checklist
da seção 14 do guia nas 9 abas em 360/390 px e nos dois temas; ~45 s). `window.__digilab` expõe só leitura
(assinatura e registro do pet vivo) para essa conferência. Etapa 4 (telas), feito: **Pet** (palco, fala, necessidades, chamado, desejo, ações, tempo,
Meus pets, revelação da evolução, conversa da fala livre com as mesmas chaves) **Crescer** (Treinar,
Aprendizado, Evolução) **Lutar** (Arena, Campanha, palco da luta: um estado só em `src/luta.ts`, o palco vai
para a aba visível) e **Diário** (Registro, Catálogo, Cenários; o pet B do cenário vira o rival fixo da arena). Navegação (DIRETRIZES_REPLICAR seções 6 e 7): no celular, barra de baixo com Pet, Crescer, Lutar e Diário, e **Conversar** e Configurações (tema, fala, registro, Tempo (teste)) no cabeçalho do Pet; de 900 px, barra lateral de 96 px com Conversar e Ajustes no pé; de 1100 px, topo com abas e mini-card do pet e as telas nas colunas das pranchas *Desktop. Luta em tela cheia (`#/lutar/luta`) com o modal Resultado; revelação (`#/evolucao`) e primeira vez (`#/inicio`) em tela cheia; folhas no celular viram o painel da direita no desktop. Tema (Auto/Claro/Escuro) em
Configurações, preferência na chave `…-tema` (o save não muda). O tempo anda e grava o save (ação
do dono na hora; tempo a cada 2 s; o pendente ao esconder/fechar a aba) e para durante a luta no palco e com o Resultado aberto (só a
interface, `luta.lutaSeguraTempo`: a luta já está no registro; o tempo parado não é compensado); se outra aba muda o save, o app relê em vez
de gravar por cima (o HTML não faz isso: não deixar o HTML e o app abertos juntos no mesmo pet). Semear save em
teste: por uma página da mesma origem que não seja o app (ex.: `/Assets/digilab_atlas_up.json`), senão o app grava
o pet dele por cima ao fechar.
O HTML continua sendo o jogo até a Etapa 6. `web/app/test/` tem a referência de
paridade. `motor_html.mjs` extrai o motor do HTML pelas marcas `@motor-inicio/@motor-fim` e roda em Node sem
DOM; `gerar_gabaritos.mjs` grava 60 vidas (3 versões de pet × 5 donos × 4 sementes, todos os estágios, tipos
de evento t/d/l/g/tr, NPCs, sombrias) com checkpoints (sha256 da assinatura + contadores) em
`gabaritos/vidas_*.json`; `constantes.test.mjs` confere cada folha numérica das constantes web contra
`gabaritos/constantes_python.json` (`python experiments/exportar_constantes_web.py`) pela tabela
`mapa_constantes.json`. `paridade_ts.test.mjs` passa os mesmos gabaritos no motor em TS (100% iguais, checkpoint a checkpoint). Gabaritos são do V8 do
Node: o Chrome difere no último bit de exp/log (libm) e o replay só é bit a bit no mesmo runtime.
**Devastador corrigido (2026-09-28)**: a semente de gambits dele tem a regra "perto e guts ≥ 60 → preparar
pesado", fora do `REPERTORIO`; a luta quebrava (TypeError). `regraDe(k)` procura no repertório e, fora dele,
nas sementes das sombrias. O repertório (candidatas da troca) não mudou, então nenhum pet existente muda.

`Assets\gerar_sprites_html.py` agora **recusa** sobrescrever o arquivo se ele tiver a aba
Evolução (`--forcar` para passar por cima e perder as edições).

## Pendências conhecidas

- **IDEIA: interação do jogador e corpo do pet** (`docs/TODO_INTERACAO_CORPO.md`, Matheus, 2026-09-30): ambiente 2D manipulável ao estilo do
  Championship (comida, bola, obstáculo, áreas), para criar decisões do pet com consequência onde o dono importa. Não autoriza
  implementação; o próximo passo é escolher a interação mínima e o gate antes de ampliar o ambiente.
- **DECIDIDO: mundo físico** (`docs/futuro/mundo_fisico.md`, Matheus, 2026-10-07): o jogador deixa a comida no lugar; ao explorar,
  o pet acha comida (deixada ou caída da árvore) e a bola, que é objeto físico no mapa. Dá a explorar uma recompensa e resolve o pet
  parado. Também DECIDIDO: mapa 2D contínuo com regiões como os cômodos do Creatures 3, vista inclinada do Animal Crossing,
  comida por arrastar e soltar, Animal Crossing e Nintendogs como referências de desenho. PROPOSTO: o motor anda até o alvo que o cérebro escolhe, posições inteiras,
  visão e cheiro; atividades do Creatures 3 e de outros jogos.
- **IDEIA: mecânicas de Dwarf Fortress → V2** (`docs/futuro/dwarf_fortress.md`, Matheus, 2026-10-01): contexto das peças (slots 8+8,
  memória nuclear, faceta × valor, duas prioridades, estresse em duas escalas) para o planejamento da V2; a v1 não recebe nada. O
  desenho (`docs/futuro/proposta_df.md`) só depois do gatilho da tarefa, junto com a fase 1b do plano da V2. DF é pista, não evidência.
- **IDEIA: decodificador de conceitos do DigiBrain** (`docs/futuro/decodificador_conceitos.md`, Matheus, 2026-10-04): os lobos
  decidem numericamente; uma camada lê o estado interno e extrai conceitos com incerteza; só então a LLM fala. Estende o motivo e a
  honestidade do fator; precedentes já publicados (CBM, Discover-then-Name, M-CBM): não alegar novidade. Não autoriza implementação.
- **IDEIA: escada de cognição social** (`docs/futuro/cognicao_social.md`, Matheus, 2026-10-04): dois pets trocando informação com
  fonte e confiança, podendo chegar a reputação, normas, tradição e convenção simbólica; os degraus altos são pergunta, não feature.
  Separa herdado, vivido e aprendido de outros. Primeiro passo possível: pet sintético informante no N5. Não autoriza implementação.
- **IDEIA: convivência no mundo físico** (`docs/futuro/convivencia_mundo_fisico.md`, Matheus, 2026-10-07): dois pets no mesmo mapa,
  vendo um ao outro, disputando a fruta e brincando com a bola; a escada social no mapa. Pede mundo compartilhado, regra de conflito no
  tick e replay do grupo (mudança de motor). Primeiro passo recomendado: parceiro sintético no mapa, sem motor de grupo. Não autoriza
  implementação.
- **IDEIA: doença de órgão e fruta-remédio** (`docs/futuro/doenca_remedio.md`, Matheus, 2026-10-07): uma doença tira um sentido
  (olfato primeiro); uma fruta amarga ajuda o órgão a se curar. Perguntas: o pet percebe a perda, descobre o remédio (com atraso e
  placebo) e passa a descoberta a outro pet (observação, sinal, entrega entre irmãos). Depende dos órgãos do corpo e da convivência.
  Não autoriza implementação.
- **IDEIA: fisiologia por espécie** (`docs/futuro/fisiologia_especies.md`, Matheus, 2026-10-08): um corpo-base comum e um perfil
  herdável por linhagem, em quatro camadas (órgãos presentes, configuração dos órgãos comuns, predisposições inatas; o aprendido fica
  com o indivíduo), como o Creatures 3 faz entre Norns, Ettins e Grendels. Rótulo ("aquático", "blindado") só com efeito no mundo.
  O perfil seria uma alteração declarada do grafo do corpo. DECIDIDAS (2026-10-08): o perfil pela espécie, com módulos por estágio na
  linha (FE-1); o primeiro passo é a configuração por espécie no corpo de hoje, começando pelo olfato (FE-2); variação individual só na
  fase 3 (FE-4); o combate não muda (FE-5); regiões novas só com o módulo (FE-6). Aberta: o perfil de cada brasão (FE-3). Não autoriza
  implementação.
- **DECIDIDO: o pet do produto aprende sozinho, sem elogiar e repreender** (`docs/DECISAO_PRODUTO_SEM_ELOGIO_BRONCA.md`, Matheus,
  2026-10-07; era o R8.1): os botões saem dos pets novos (v1–v10 iguais); o pet aprende pela consequência, como o reforço químico do
  Creatures 3; acariciar fica e o tapa entra como
  desaprovação, os dois como estímulos no corpo. Antes de ligar: drives que recompensem brincar e o contato (senão o pet fica parado).
  O plano do porte (#201) precisa inverter a seção 1.2 e a D-W1.

- **DECIDIDO o objetivo: ego do pet** (`docs/futuro/ego_existencia.md`, Matheus, 2026-10-07): o pet tem ego, questiona a própria
  existência e fala sobre isso; o automodelo **tem corpo** e é **aprendido por uma rede** (a rede de si, por erro de previsão; o
  pet estima, o motor e as sondas avaliam). Implica rever a regra "só a Decisão aprende" (E-6). O corpo segue os conceitos do
  Creatures 3 (química, receptores, órgãos, Vida; E-7 decidido). O como é PROPOSTO, por etapas com tarefa e plano.
- **IDEIA: aura do herói** (`docs/futuro/aura_do_heroi.md`, Matheus, 2026-10-03): retrato da lista de gambits de um pet que lutou
  muito, vendido na loja como item de 2 lutas que empresta esse conhecimento a outro pet. Depende de loja e moeda (ainda ideia);
  divide a peça técnica com o PvP com ghost. Não autoriza implementação.
- **Pesquisa:** a pergunta do efeito do dono está encerrada (`docs/LEITURA_CONSOLIDADA_DONO.md`, 2026-10-01). **V2 = pesquisa
  primeiro** (decisão do Matheus, 2026-10-01): plano PROPOSTO em `docs/PLANO_V2_PESQUISA.md` (pergunta sobre o aprendiz e o
  ambiente; fase 0 fecha a v1, fase 1 testa ambiente mínimo e política com lobos, fase 2 humanos, fase 3 criação × seleção).
  Nenhuma run sem o plano de análise da fase registrado antes.

- **Stand-by: combate 1×1 em tempo real, como no Digimon Championship (DS)** (Matheus, 2026-09-29: guardar para o futuro, sem executar).
  - **A ideia:** o motor passa a simular espaço contínuo (posição, velocidade, alcance, tempo de recarga, passos fixos para continuar reproduzível) no lugar dos turnos e das 3 distâncias. O pet segue lutando sozinho, e o dono influencia pela criação.
  - **O que muda:**
    - `web/app/motor/combate.ts`, `gambits_pet.ts`, `bots.ts` e as constantes CV/CV21;
    - o `digilab/combate_v2` e a arena no Python (paridade);
    - as condições dos gambits (hoje "perto/médio/longe");
    - a bateria e a calibração do combate: vira um combate V3, com protocolo e gates novos;
    - a escala e os NPCs da campanha;
    - os pets antigos ficam no motor de hoje.
  - **Por que esperar:**
    - custo alto;
    - a diferença para o jogador é pequena perto de animar bem os turnos (a opção A, só visual, também descartada por ora);
    - mais variância nas lutas, e o sinal da pesquisa já é pequeno.
  - Os sprites têm quadros de animação (257 Digimon) e efeitos de ataque (187) em `Assets/Digimon Up Assets/Animacoes`.

- Evolução canônica: o vínculo foi redesenhado (vínculo B, pets v10, PR #114). **Decisão do Matheus (2026-10-01): o limiar do Mega
  fica em 0,4** nos pets v10 (no jogo curto o dono da web quase não dá feedback e o B não inverte o Mega,
  `artifacts_v2_vinculo_novo/mega_v10.json`); rever só com medida de dono humano.

- Fala por LLM: repetida com outra semente (2026-09-29, `artifacts_fala/ollama_qwen2.5-3b_fala-v6_s20260929/`):
  92% aprovadas, nenhuma barrada por fator fora da lista. Pré-leitura (coluna própria no `revisao.csv`): nenhuma
  das 50 cita causa fora dos fatores (desde a v4 a LLM só escreve a moldura); 9 tinham caractere quebrado do
  qwen 2.5 3b, agora barrado na validação da moldura. Leitura do Matheus feita em 2026-10-01.

- Gambits híbridos existem só na web; levar para o Python exige protocolo próprio (arena V2),
  gate de que o aprendizado de gambits separa donos, e ablação trava/veto × sem intervenção. Adiado
  (2026-09-29): nenhuma pergunta de pesquisa atual depende disso.

- Motivo do bandit (resolvido em 2026-09-29, recomendação aceita pelo Matheus): na vida, sem fator e sem exploração
  quem decidiu foi o prior do instinto, e o adulto passa a dizer "Foi instinto: é o meu jeito." (antes "Não sei, só
  quis.", que fica para a exploração e o combate). Python (`expressao.GENERICO_INSTINTO`) e web.
- Memória: bootstrap sobre as 5 sementes feito (2026-09-29, `experiments/bootstrap_memoria.py`,
  `artifacts_v1_memoria/bootstrap_sementes.json`): separação entre − dentro do braço muda −0,0011 bit
  [−0,0039; +0,0029] com memória e −0,0005 [−0,0030; +0,0018] com memória por espaços — sem evidência de
  efeito (poucas sementes: IC largo). Recusa (B2) exige mudança no motor — decisão do pesquisador.

- Combate corrigido (V2C/V21C) aprovado com ressalvas e já na web (2026-09-25; oráculo da web segue de 1
  passo). E2 pede ciclo entre espécies; E4 pede redesenho do adolescente ou da passiva do adulto.
- Combate V2 original reprovado em G4/G5: decidir entre mudar bots passivos, regra de esquiva ou limiares
  (decisão do pesquisador); investigar a dominância do adaptativo antes de plugar pets.
- Combate V2.1 reprovado em E1–E5: falta a especificação das correções da base (finta, parry, fuga
  condicionada, morte súbita) e a `TAREFA_PERSONALIDADE_OBEDIENCIA`; espécies precisam de identidade
  que gere ciclo (E2); a resposta declarada do marcar não funciona com recuar anulando avançar (E3).

- Campos PROPOSTOS: referendados pelo Matheus em 2026-09-29 ("Referendar todos"), em `protocol.REFERENDO` (registro à parte:
  os status e os hashes das runs antigas não mudam; um valor novo volta a contar como não referendado). O aviso
  "PROPOSTOS não referendados" das runs antigas fica como está, porque faz parte dos artefatos reproduzíveis.
- Ablação treino × cuidado (arena v1): inconclusiva e **superada** (decisão de 2026-09-29): a pergunta foi
  respondida no desenho atual pela confirmatória (V21C, 160 ovos) e pelas exploratórias V3/V3b/V3c; não será
  rodada de novo.
- Sementes de partida derivam do nome do braço. Renomear um braço muda todas as partidas dele.
- O hash do protocolo não cobre o código de `metrics.py`; mudanças de métrica não alteram o hash.
- A pasta irmã `D:\Trab\digilab\v0` tem os arquivos soltos (sem subpasta `digilab/`); os imports
  dela não funcionam como estão. Este repo é a versão de referência.

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

## V2, W-PRANCHA-MAPA — a prancha do mapa do mundo físico (2026-10-07, rodada 16, `docs/V2_RODADA_16.md`) — SÓ PRANCHA

Proposta de `docs/futuro/mundo_fisico.md` (seções 2.3 e 2.6), seguindo o protótipo `docs/futuro/mundo_fisico_vistas.html`. Nenhum código
do motor nem do app.
- **Pranchas:** `docs/estilo_up/pranchas/MapaDesktop.html` (1280×720) e `Mapa390.html` (390×844), com placeholders originais e os tokens e
  componentes de `docs/estilo_up/dl-up.css`. A cópia com os sprites fica em `Assets/Pranchas_UP/`, fora do repositório, listada no
  `index.html` de lá.
- **O que mostram:**
  - a vista inclinada (a projeção do protótipo);
  - as quatro regiões (M-4): casa com o ninho e o comedouro, jardim, campo e mata;
  - as árvores com frutas caídas e uma caindo, a comida deixada no comedouro, a bola quicando e o pet de pé com sombra;
  - o estado "comida solta aqui" depois do drop, com o aviso e **Desfazer**.
- **No desktop:** a câmera segue o pet, com botões de seguir, aproximar e afastar; a bandeja e a bola ficam na lateral, com o mapa de cima
  e o card "Agora".
- **No celular:** o mapa na tela inteira e a bandeja aberta embaixo. O arrasto da carne começa na bandeja; um dedo no mapa move a câmera,
  e dois dedos dão zoom.
- **Registrada** em `docs/PENDENCIAS_PRANCHAS.md` como "não existe" no app. Interpretações em `docs/REGISTRO_DESVIOS.md`.

## V2, W-FAIXAS-R17 — as faixas e os prefixos do mundo físico e do corpo (2026-10-07, rodada 17, `docs/V2_RODADA_17.md`)

- **`FAIXAS_RESERVADAS`** (`experiments/bancada_v2.py`) ganha quatro faixas, cada uma com a fonte:
  - mundo físico (`PLANO_ANALISE_V2_MUNDO_FISICO`, seção 11): 31101…31505 (calibração e piloto do N) e 32101…32505 (validação);
  - corpo e drives (`PLANO_ANALISE_V2_CORPO_DRIVES`, seção 10): 33101…33505 (calibração e piloto) e 34101…34505 (validação).
- **`PREFIXOS_UNIDADES`** ganha `"mundo"` e `"corpo"` (seção 4 de cada plano).
- **`tests/test_faixas_r17.py`** confere:
  - que as faixas novas não colidem com as de antes, com as queimadas nem com as sementes das configs;
  - que as unidades dos seis prefixos (K = 40, as duas fases) não colidem entre si e as novas ficam fora das faixas, das configs e das
    sementes dos testes.

## V2, W-GABARITOS — as vidas de hoje do mundo físico e do corpo (2026-10-07, rodada 17, `docs/V2_RODADA_17.md`) — GABARITOS GRAVADOS

Passo 1 do A, antes de qualquer mudança do mundo físico (`docs/TAREFA_V2_MUNDO_FISICO.md`, seções 9 e 10) ou do corpo
(`docs/TAREFA_V2_CORPO_DRIVES.md`, seção 12, G2). Nenhum código do motor mudou; só as sementes dos testes. Interpretações em
`docs/REGISTRO_DESVIOS.md`.
- **Mundo** (`tests/gabarito_mundo.py` → `tests/gabaritos/mundo_vidas_de_hoje.json`, 96 vidas):
  - P0, P1 e P3, nos mundos `padrao`, `bola`, `descasado` e `iguais_frutas`;
  - atencioso e aleatório, nas sementes 101 (sem genoma) e 202 (genoma 202: no `padrao`, o `MotorPersonalidade`);
  - na bancada simples (L1) e na completa (T3 com as peças da K2, K4 e canais).
- **Corpo** (`tests/gabarito_corpo.py` → `tests/gabaritos/corpo_vidas_de_hoje.json`, 156 vidas):
  - os três motores que o corpo vai tocar: `MotorComFeedback`, `MotorAmbiente` e `MotorFrutasMundo`;
  - P0 a P3 (o P2 só nos mundos das frutas), nos mundos `padrao`, `bola`, `descasado`, `mutavel` e `iguais_frutas`;
  - as montagens simples (T3 com as peças da K2) e completa;
  - o só cuidado do P3 (`sem_ensino`) na completa;
  - sementes 101 e 202, sem genoma.
- **O que se confere:** sha256 do log, do estado final, do `estado()`, das ações, das rngs, do registro do mundo e do estado interno da
  política.
- **Teste:** `tests/test_gabaritos_mundo_corpo.py`, 6 testes, ~31 s. Os dois gabaritos são conferidos byte a byte contra o código atual, e
  o teste verifica a cobertura (motores, mundos, braços, montagens) e as sementes.
- **Regravar só com o código de antes.** Depois da mudança do mundo ou do corpo, estas vidas têm de sair iguais com a chave desligada.

## V2, W-CORPO-QUIMICA — a química dos drives de hoje, sem órgão (2026-10-07, `docs/TAREFA_V2_CORPO_DRIVES.md`, etapa 1) — GATES PASSAM

Rodada 17 (`docs/V2_RODADA_17.md`). Etapa 1 da seção 14 da tarefa do corpo (CD-1 a CD-10 decididas). Infraestrutura, sem run; só as
sementes dos testes. Mudaram `digilab/corpo.py` (novo) e `digilab/config.py` (`ConfigCorpo` no fim). Motor, `engine.py`, `lobos.py` e a
web não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **`ConfigCorpo`** (desligada por padrão; registro `corpo.PARAMETROS_CORPO`):
  - `ligada` liga a química dos drives de hoje;
  - `digestao`, `vida`, `drives_novos` e `gestos` falham alto se ligadas (etapas 3, 4 e 6). Cada uma exige a anterior;
  - C = 450000 (CD-1) e S = 1024;
  - os efeitos da ação do pet já em C;
  - as constantes de meia-vida (k 1497, 753 e 32).
- **`Corpo`** (componente puro: sem motor, sem rng; só importa `config`, `events` e `state`):
  - **os químicos:** `fome`, `desconforto`, `cansaco`, `tristeza` e `dano` guardam a falta em inteiros de [0, C]. O drive é
    (C − q) / C;
  - **as taxas** (`taxas_de`) saem de `Config` e da `ConfigCorpo`, cada uma conferida na grade de C;
  - **o tick** (`passo(estado_antes)`) segue a ordem de `state.avancar_um_tick`, com o dano pelo receptor de privação (algum de fome,
    desconforto e cansaço acima de C − 67500);
  - **os estímulos de hoje:** `acao_dono` (as seis ações de `state.aplicar_acao_usuario`), `acao_pet`, `estimulo_bola` e
    `estimulo_fruta`;
  - **as leituras:** `drives`, `no_estado`, `falta` e `receptores`, estes na escala S;
  - **os passos inteiros:** `k_meia_vida` (só para derivar), `passo_meia_vida` (com decremento mínimo de 1) e `div_arred`.
- **Paridade:** `experiments/exportar_gabarito_corpo.py` → `tests/gabaritos/corpo_quimica_python.json`, com:
  - as taxas;
  - uma grade de casos;
  - a meia-vida e o `div_arred`;
  - 3 vidas em malha aberta, com o sha256.

  Só inteiros: o TS da etapa 7 confere igual.
- **Gates** (`tests/test_corpo_quimica.py`, 29 testes, ~3 s):
  - **G-HOJE (a) em malha aberta:** 4 donos × 5 sementes × 3 dias, com as ações forçadas. Fome, higiene, energia e humor ficam a até 1e−9
    do float de hoje em todo tick; a saúde, até 1e−9 mais as viradas de privação. Toda virada é um químico exatamente no limiar.
    O `Estado` e a rng de ambiente de hoje são reproduzidos;
  - **o exemplo do tick 660:** 0,25 exato em inteiros, contra 0,24999999999998737 no float;
  - **as constantes:** a derivação dos k_h e a meia-vida efetiva; C é o menor que deixa as taxas inteiras;
  - **as conversões na grade:** as ações do dono e do pet, a bola, a fruta e o tick;
  - **os receptores:** na escala S, e o `div_arred` igual ao dos lobos;
  - **as falhas altas:** fora da grade, a sub-chave das etapas seguintes e o corpo com a chave desligada;
  - **o isolamento:** o AST sem motor e sem rng;
  - **a paridade:** o gabarito reproduz.

## V2, W-MUNDO-FISICO — o motor do mundo físico, etapa 2 (2026-10-07, `docs/TAREFA_V2_MUNDO_FISICO.md`) — GATES PASSAM

Rodada 17, passo 2 do A. As seções 2 a 8 da tarefa (MF-1 a MF-4 decididas), sem run e só com as sementes dos testes. O instinto e os
cérebros no mundo são a etapa 3 (B); a web, a etapa 5; a bancada, a etapa 4 (D).
- **O que mudou:**
  - `digilab/mundo.py`, arquivo novo;
  - a `ConfigMundo`, o `LayoutMundo` e os layouts padrão e afastado, no fim de `config.py`;
  - os eventos `deixar_comida` e `deixar_bola`, como funções novas em `events.py`;
  - o campo `Observacao.mundo`, com padrão None.
  - `engine.py`, `ambiente.py`, `frutas.py`, os cérebros, a bancada e a web não mudaram.
- **`MotorMundo`:**
  - é subclasse do `MotorFrutas`. Desligado, não tem rng, registro, chave em `estado()` nem embrulho;
  - ligado, substitui o cenário do N4 e da A1: frutas e bola ligadas, educação e lesões levantam erro, e `alimentar`, `oferecer_fruta_*`,
    `por_bola` e `tirar_bola` também;
  - o mapa tem 64 × 30 células de 16 subunidades, com posições inteiras, distância por `isqrt` e direções pela tabela inteira `DIR16`;
  - as árvores, a comida que amadurece, apodrece e some, e a bola que rola usam os fluxos `mundo-arvores`, `mundo-bola` e
    `mundo-sujeira`, nunca a `_rng_ambiente` nem a rng do pet (MF-4);
  - o alvo de explorar, comer e brincar sai do gancho `escolher_alvo` ou do padrão do motor, com um `u` da rng `alvo` sorteado sempre;
  - o pet anda de uma vez na decisão e paga energia pela distância. Explorar tem o "achou e comeu" (MF-1), e comer sem comida não dá
    fome (MF-2);
  - a percepção vai em `Observacao.mundo` (`PercepcaoMundo`, com a posição: MF-3);
  - a consequência chega ao cérebro com tudo aplicado, mais os ganchos `fruta_comida` e `consequencia_mundo`.
- **Peças para a bancada:**
  - `deixar_comida` conta como contato e `deixar_bola` não;
  - `reproduzir_mundo`, `fabricas_mundo` e `DonoComLugar` (comedouro, perto, longe, com a rng `dono-lugar` sem o braço);
  - `CanalMundo` e `simular_vida_mundo`.
- **Registros para as medidas do plano** (A1.8): `decisoes_mundo`, `regioes`, `visitas` às manchas, `quedas`, `consumos_mundo`,
  `deixadas` e `sumidas`. O replay refaz todos.
- **Gates** (`tests/test_mundo.py`, ~22 s):
  - **G1:** replay bit a bit com o instinto, um cérebro aleatório que escolhe alvos e os lobos aprendendo, para 4 donos, 3 lugares e 2
    sementes;
  - **G2:** as 96 vidas de `mundo_vidas_de_hoje.json`, com o `MotorMundo` desligado no lugar do motor da bola e das frutas;
  - **G-ENGINE:** o sha256 de `engine.py`, `ambiente.py` e `frutas.py`;
  - **G-MEC:** os mecanismos;
  - **G-NUMS:** as mesmas quedas em qualquer cérebro e dono;
  - **G-V1-V10:** a suíte de sempre passa.
- Uma vida de 14 dias leva ~0,3 s, e o replay outros ~0,3 s. Interpretações e os números PROPOSTOS escolhidos aqui estão em
  `docs/REGISTRO_DESVIOS.md`.

## V2, W-CORPO-DIGESTAO — os órgãos 1 e 2 do corpo: a digestão e a Vida (2026-10-07, `docs/TAREFA_V2_CORPO_DRIVES.md`, etapas 3 e 4) — GATES PASSAM

Rodada 17. Etapas 3 e 4 da seção 14, um commit cada (o órgão 1 primeiro). Infraestrutura, sem run; só as sementes dos testes. Mudaram
`digilab/corpo.py` e a `ConfigCorpo`; motor, `engine.py`, `lobos.py` e a web não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **Órgão 1, a digestão** (sub-chave `digestao`; `ConfigCorpo.taxa_digestao` = C, CD-3):
  - **o estômago:** a ração, o comer e a nutrição da fruta vão ao químico `alimento`;
  - **a reação:** `t = min(alimento, fome, o que resta da taxa no tick)` roda na hora da ingestão e no começo de cada tick;
  - **o excesso:** com a fome em 0, o resto é descartado (o corte de hoje);
  - **o exposto:** `digerido_no_tick` (para a vontade do banheiro), `digerido_total` e `descartado_total`;
  - **sem receptor** para o cérebro.
- **Órgão 2, a Vida** (sub-chave `vida`; `ConfigCorpo.vida_decaimento` = 11 = C // (28 × 1440)):
  - **o relógio:** `vida` começa em C e decai v por tick; o `de_estado` usa o tick do `Estado`;
  - **os receptores de estágio:** `estagio()`, nos limiares C − v × T, com os ticks de `treino_stats.estagio_no_tick` da `cfg_evo` do
    corpo;
  - **sem morte:** a Vida não mata;
  - **sem receptor** para o cérebro.
- **As outras sub-chaves:** `drives_novos` e `gestos` continuam falhando alto.
- **Paridade:** o gabarito `tests/gabaritos/corpo_quimica_python.json` passa à versão 2, com a digestão (na taxa C e numa taxa lenta só
  para a paridade) e a Vida (limiares, grade e vidas com os ticks de estágio).
- **Gates:**
  - **`tests/test_corpo_digestao.py`:**
    - o G-HOJE (a) de novo, com a digestão na taxa C, em 4 donos × 5 sementes;
    - a química igual à da etapa 1, químico a químico;
    - a composição da seção 5, a reação com a taxa lenta, o descarte e a conservação da comida.
  - **`tests/test_corpo_vida.py`:**
    - o estágio pela Vida igual ao de hoje tick a tick, nas três durações, até depois do fim da Vida;
    - os ticks das transições do `MotorEducacao` (teste e canônica) e do `MotorTreino` iguais aos cruzamentos da Vida;
    - o G-HOJE (a) com os dois órgãos.

## V2, W-MEDIDAS-R17 — as medidas do mundo físico, do corpo e do banheiro (2026-10-07, rodada 17, `docs/V2_RODADA_17.md`) — TESTADAS EM DADOS SINTÉTICOS

Funções puras no fim de `digilab/metrics.py`, sobre listas simples de eventos. O motor do mundo e o corpo novo ainda não estão na `main`,
então o docstring de cada função diz o que o motor precisa fornecer. Nenhuma run; nada mais mudou. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **Comuns:** `janela_dias(primeiro, ultimo)` e `JANELA_8_14` (ticks [10080, 20160)); posições em subunidades (`SUBUNIDADES_POR_CELULA` 16).
- **Mundo físico** (`PLANO_ANALISE_V2_MUNDO_FISICO`, seção 5.1 e adendo 1, A1.8):
  - `deficit_fome_energia` (o `D_FE`, entrada (tick, fome, energia) por decisão);
  - `visitas_manchas` (entrada: a trajetória (tick, x, y), uma por decisão, e os troncos), com `custo_viagem` e `taxa_recente` (as quedas);
  - `inclinacao_permanencia` (G-PERM sobre o custo, G-OPORT sobre a taxa recente), `taxa_no_abandono` (a medida 2), `permanencia_media`
    e `contraste_distancia` (G-DIST).
- **Corpo** (`PLANO_ANALISE_V2_CORPO_DRIVES`, seção 5 e adendo 1): `tempo_livre_be` (`BE` e `OC`), `cuidado_preservado`, `drives_novos`,
  `variedade_recente` (A1.2), `p_comer_so_fruta` e `inclinacao_generalizacao` (A1.1).
- **Banheiro** (`PLANO_ANALISE_V2_BANHEIRO`, seções 4 e 8): `alivios_por_dia` (a fração no banheiro e os acidentes), `dia_do_criterio`
  (com censura e T*), `alivios_ate_criterio` e `curva_sobrevivencia` (Kaplan–Meier e RMST).
- **Testes:** `tests/test_medidas_r17.py`, 19, cada um com a resposta conhecida.

## V2, W-CORPO-MOTOR — o corpo por baixo dos drives, no motor (2026-10-07, `docs/TAREFA_V2_CORPO_DRIVES.md`, etapa 2) — GATES PASSAM

Rodada 17. Etapa 2 da seção 14: o `Corpo` do B (química, digestão e Vida) por baixo dos drives do `Estado`. Sem run; só as sementes dos
testes. Mudaram `digilab/motor_corpo.py` (novo) e o campo `Observacao.corpo` (com padrão None). `engine.py`, `corpo.py` e as classes do
meio não mudaram. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **`MotorCorpo`:**
  - é um mixin por `com_corpo(base)`: `com_corpo(MotorComFeedback)`, `com_corpo(MotorAmbiente)` e `com_corpo(MotorFrutasMundo)`;
  - a chave é `cfg_corpo` (`ConfigCorpo`, com as sub-chaves `digestao` e `vida`);
  - desligado, é o motor de baixo byte a byte.
- **Ligado:**
  - os cinco drives do `Estado` são a leitura da química, a cada tick e depois de cada estímulo. O laço do tick é refeito no mixin, com o
    `Corpo.passo` (o tick e a sujeira de hoje, na mesma rng);
  - os escritores de hoje viram estímulo: a ação do dono, a ação do pet, a bola e a fruta (antes do gancho `fruta_comida`);
  - **G-BYPASS:** um drive mudado por fora do corpo falha alto;
  - a percepção vai em `Observacao.corpo` (`PercepcaoCorpo`, os receptores na escala S);
  - o gancho `consequencia_corpo(acao, ocorrido, obs_depois)` é chamado uma vez por decisão;
  - com a Vida, o estágio é conferido contra o de hoje a cada tick.
  - Educação, lesões, obediência, treino e **o mundo físico ligado** falham alto; o andar e as comidas do mapa ainda não têm estímulo no
    corpo.
- **Gates** (`tests/test_corpo.py`, 28, ~1 min):
  - **G2:** as 156 vidas de `corpo_vidas_de_hoje.json` com o `MotorCorpo` desligado na frente dos três motores;
  - **G-HOJE (a):** malha aberta contra o motor de hoje, tick a tick, nos três mundos, com a química sozinha e com os dois órgãos. Os
    drives ficam a até 1e−9, a saúde a até 1e−9 mais as viradas no limiar, e sujeira, sono, rngs e estágio são iguais. O sinal do N3 sai
    igual em ≥ 99% das decisões;
  - **G-BYPASS** e **G-RECEPTOR**;
  - **G-ENGINE:** `engine.py` e as classes do meio sem mudança;
  - **o gancho e o G1:** o gancho é chamado uma vez por decisão e já vê tudo aplicado; o replay é bit a bit com o corpo.
- **Achado:** em malha fechada, 17 a 19 de 20 vidas por mundo divergem cedo, porque os pesos do tempo livre são contínuos nos drives. O
  G-HOJE (b) tem de ser pela distribuição.

## V2, W-BANCADA-MUNDO — as faixas do banheiro e o mundo físico na bancada (2026-10-07, `docs/TAREFA_V2_MUNDO_FISICO.md`, etapa 4) — GATES PASSAM

Rodada 17. Infraestrutura, sem run de pesquisa; só as sementes dos testes. Só `experiments/` mudou (a bancada e `configs/v2_mundo/`) e três
testes antigos (a tabela de braços, a de condições e o `NOS_PENDENTES`). `engine.py`, `mundo.py`, `metrics.py`, os cérebros e a web não. Interpretações em
`docs/REGISTRO_DESVIOS.md`.
- **Banheiro:** as faixas 37101…37505 (calibração e piloto) e 38101…38505 (validação) em `FAIXAS_RESERVADAS`, com a fonte
  (`PLANO_ANALISE_V2_BANHEIRO`, seção 10), e o prefixo `"banheiro"` em `PREFIXOS_UNIDADES`.
- **Os mundos `fisico` e `fisico_afastado`:** o `MotorMundo` da main, condição `iguais` (PMF-7); o afastado troca só o layout
  (`LAYOUT_MUNDO_AFASTADO`, o G-DIST da A1.8). A chave `"mundo"` da config troca campos da `ConfigMundo` (o `mult_queda` da calibração).
- **O lugar** (comedouro, perto, longe; PMF-4) é um fator da vida: `EspecVida.lugar` e a chave `"lugares"`, obrigatória com o mundo
  físico e proibida fora dele. A célula é dono × lugar, e a coluna da tabela vira `condicao/mundo/lugar`.
- **O dono só com o cuidado (PMF-3):** o `DonoComLugar` (o `alimentar` vira `deixar_comida` no lugar) com o filtro `sem_ensino` aplicado
  ao vivo (`CanalSemEnsino`, `simular_vida_fisico`). O elogio e a bronca gastam o orçamento do dono como sempre, mas não chegam ao motor
  nem ao log; ficam contados em `VidaBancada.retirados`. Os gestos do mundo entram na contagem (`contar_gestos_mundo`).
- **O replay** é o `reproduzir_mundo`: no G1 de toda vida e acoplado, na medição e na deriva (com o mesmo corte por tick). O
  `resumo_motor` ganha o `resumo_mundo_fisico()`.
- **As medidas do plano** (`Bancada.medidas_mundo`, bloco `mundo_fisico` no `medidas.json`), todas de `metrics.py`, nos últimos sete dias
  (os dias 8 a 14 numa vida de 14):
  - o `D_FE` (e o da vida toda) e o cuidado preservado;
  - as visitas às manchas, recontadas da trajetória do motor e conferidas contra as `visitas` dele (uma diferença falha alto);
  - as inclinações da permanência sobre o custo de viagem e sobre a taxa recente (G-PERM, G-OPORT), a taxa no abandono e a permanência
    média (G-DIST, entre os dois layouts).
  - Nas tabelas: `d_fe`, `privacao_janela` e `permanencia_media`.
- **Pendente do instinto do mundo** (`NOS_PENDENTES["instinto_mundo"]`, a etapa 3 do B), falhando alto com o nó:
  - o braço **P0z** (o P0 `sem_explorar`), e com ele os acoplados P0^ac e P1^ac, que saem do registro dele;
  - o cérebro `instinto` no mundo físico;
  - qualquer config do mundo físico com sementes fora das dos testes.
- **O que roda hoje:** os lobos (P0, P1, P3) no mundo, cegos a ele até a etapa 3, e o acoplado P1 ← P0 (o encanamento do P1^ac).
- **Testes:** `tests/test_bancada_mundo_fisico.py`, 15 (~30 s). **Fumaça** (`experiments/configs/v2_mundo/fumaca.json`, NÃO canônica):
  96 vidas rejogadas bit a bit em ~1,5 min; sem artefato.

## V2, W-MUNDO-WEB — o motor do mundo físico em TypeScript (2026-10-07, `docs/TAREFA_V2_MUNDO_FISICO.md`, etapa 5) — G-PAR PASSA

Rodada 17, etapa 5 da seção 9 da tarefa: só o motor e a paridade. Não entram tela nem versão de pet nova. Mudaram `web/app/motor/mundo.ts`
(novo), o `motor/index.ts` (exporta o mundo), `motor/constantes.ts` (a `ConfigMundo` e os layouts no fim),
`experiments/exportar_gabarito_mundo.py` (novo) e o gabarito `web/app/test/gabaritos/mundo_python.json`. `digilab/`, o app, os pets e os
gabaritos de antes não mudaram. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **Caminho:** o motor do app fica em `web/app/motor/` (sem DOM) e os testes em `web/app/test/`. Por isso os arquivos são
  `web/app/motor/mundo.ts` e `web/app/test/mundo.test.ts`, e não o `web/app/src/motor/` que a tarefa citava.
- **`motor/mundo.ts`** é o porte de `digilab/mundo.py`, com os registros nos nomes do Python:
  - a conta inteira (`divArred`, `distancia`, `noMapa`, `deslocar`, `passoAte`, `regiaoDe`, `cheiroEm`, `direcaoDoCheiro`, `DIR16`);
  - os eventos `deixar_comida` e `deixar_bola` (`{tick, tipo, valor}`, com a mesma validação);
  - a classe `Mundo`: as árvores, a comida que amadurece, apodrece e some, a bola que rola, a percepção, os candidatos, o alvo padrão e
    a consequência de andar, comer e brincar, com o MF-1 e o MF-2.
- **O mundo é um componente:** recebe o estado do pet (fome, energia, humor, sujeira) depois do efeito da ação e devolve o estado
  depois. O engine, a política e o dono ficam com quem o usa.
- **Os sorteios do Python, número a número:** cada fluxo é um `random.Random` semeado por `derivar_semente`. O arquivo traz:
  - o sha256 (puro, com o próprio UTF-8);
  - o `derivarSemente` (bigint);
  - o `RandomPy`: o Mersenne Twister do CPython com o `init_by_array` e `random`, `getrandbits`, `randrange` e `randint`.
  - O `mulberry32` do jogo não entra.
- **Gabarito** (`python experiments/exportar_gabarito_mundo.py`):
  - a config;
  - a grade: as sequências do `random.Random` de 8 sementes de 0 a 64 bits, as derivações, 400 casos de cada conta, 150 de cheiro e
    direção e os eventos válidos e inválidos;
  - **4 vidas inteiras de 3 dias** (instinto; um cérebro que escolhe qualquer alvo, inclusive a podre e um ponto; os lobos aprendendo no
    layout afastado com o dobro de quedas; o cérebro aleatório com o dono que deixa a bola perto). Cada uma tem o traço por decisão, o
    resumo do mundo e os próximos sorteios de cada fluxo.
  - `tests/test_gabarito_mundo_web.py` confere que o arquivo está em dia com o Python.
- **G-PAR** (`web/app/test/mundo.test.ts`, 18 testes, < 1 s):
  - a config, os layouts e os números do estado são os do Python, campo a campo;
  - as sequências, o `derivar_semente`, as contas e os eventos saem iguais;
  - as 4 vidas são rejogadas decisão a decisão: percepção, candidatos, ocorrido (o `u`, o alvo, o deslocamento, a energia gasta, o
    consumo, a rolagem), o estado e a percepção depois, o resumo do mundo e os 6 próximos sorteios dos 4 fluxos saem iguais.
  - Os floats são comparados com igualdade exata.
  - Uma mutação no efeito da podre faz a vida 4 falhar.
- **A única diferença**, da língua: o Python recusa `deixar_bola(9, 3.0, 4)` (`type(x) is not int`), e no JS 3.0 é o mesmo número que 3. O TS
  aceita, com o mesmo texto no log (`"3|4"`); o teste a declara.

## V2, MUNDO-CEREBROS — o instinto do mundo e os ganchos nos cérebros (2026-10-07, `docs/TAREFA_V2_MUNDO_FISICO.md`, etapa 3) — GATES PASSAM

Rodada 17, etapa 3 do mundo físico (B). Infraestrutura, sem run; só as sementes dos testes. Mudaram `digilab/instinto_mundo.py` (novo),
`digilab/policies/lobos.py` (atrás de `cfg_mundo`) e `digilab/motivo.py`, mais `experiments/analisar_empates_cheiro.py`. `mundo.py`,
`engine.py`, a bancada, os cérebros B e C e a web não mudaram. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **`PoliticaInstintoMundo`** (o P0 do plano), igual ao instinto de hoje fora de três pontos:
  - **a fome urgente** (`pedido_necessidade`): com a fome abaixo de 0,25 e para onde ir comer (comida boa vista, ou cheiro com direção),
    come; sem isso, chama. A higiene baixa continua chamando;
  - **o tempo livre:** `comer` ganha `w_fruta` com comida boa vista e `brincar` ganha `w_bola` com a bola vista (os `w` do N4 e da A1, a
    mesma chamada de `rng.choices`, as regras `fruta_no_cenario` e `bola_no_cenario`);
  - **`sem_explorar`** (o P0z): o peso do explorar vai para o ocioso.
  - Sem `obs.mundo`, é o `PoliticaInstinto` byte a byte.
- **A regra que liga a percepção às entradas do cérebro A** (`instinto_mundo.entradas_mundo`): `bola` = 1 com a bola vista; `fruta` = 1
  com comida boa vista (ração ou fruta madura). Com elas, o prior do A repete o instinto do mundo.
- **O cérebro A no mundo:** `PoliticaLobos(cfg, cfg_lobos, cfg_mundo=CONFIG_MUNDO_LIGADA)`. Sem a chave, os lobos de hoje.
  - A sonda roda o `PoliticaInstintoMundo`; o prior ganha `comer` na linha `pedido_necessidade`. 10 regras × 7 ações × 12 entradas, sem
    as peças das frutas.
  - **`escolher_alvo`** devolve None (o padrão do motor) e anota os candidatos no motivo. O alvo aprendido é de adendo.
  - **`consequencia_mundo`:** na fonte consequência, o crédito de explorar, comer e brincar espera o gancho. A E2 só vale no comer que
    comeu fruta; o resto usa o sinal do N3. Com canais e fruta que mexe no humor, falha alto (rota de adendo).
- **`PoliticaComMotivo`** repassa os dois ganchos (só se a política os tem), pede o termo do mundo ao instinto do mundo e recusa o
  `sem_explorar`.
- **Gates** (`tests/test_mundo_cerebros.py`):
  - os lobos com o mundo e o aprendizado desligado = o instinto do mundo byte a byte (4 donos × 3 lugares × 2 sementes; decisão a
    decisão em 3000 observações); o P1 com ganho 0 = o P0;
  - G1 do instinto (P0, P0z) e dos lobos (P0, P1 com e sem canais, P3), estado interno incluído;
  - a fome urgente, o tempo livre e o `sem_explorar` em casos com resposta conhecida;
  - o crédito no gancho, conta exata (E2 no comer de fruta; o f_S da transição no resto);
  - a `PoliticaComMotivo` não muda a vida;
  - G2 (chave desligada = as vidas de hoje): os gabaritos de sempre, na suíte.
- **Os empates do cheiro** (`python experiments/analisar_empates_cheiro.py` → `artifacts_v2_mundo_cerebros/empates_cheiro.json`; só
  geometria, mais as vidas do P0 nas sementes dos testes):
  - com a fruta fora da visão e dentro do raio do cheiro, o máximo empata em 79% das posições (a ração, 58%);
  - a ordem fixa erra o rumo em 27,8° em média e puxa sempre para o sentido horário (−18°); o comer pelo cheiro gasta 0,84 decisão a mais
    que a reta;
  - desempatar pelo cheiro a 2 células: 15,4° e 0,25 decisão; o limite de qualquer desempate (o rumo verdadeiro): 11,3° e 0,17;
  - nas vidas, 41% das decisões com direção de cheiro saem de um empate, e o desempate a 2 células mudaria 16%.
  - A recomendação (trocar no motor, A, antes da calibração do mundo) está no PR.

## V2, W-DOMINANCIA — a dominância de um drive no sinal e o braço P1-cw (2026-10-07, `docs/PLANO_ANALISE_V2_CORPO_DRIVES.md`, adendo 2) — GATES PASSAM

Rodada 18. A parte do D no adendo 2 (A2.2 a A2.6; decisão D-4). Infraestrutura, sem run de pesquisa; só as sementes dos testes. Mudaram
`digilab/metrics.py`, `experiments/bancada_v2.py` e a tabela de braços de `tests/test_bancada_v2.py`. `engine.py`, `lobos.py`, o corpo e a
web não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **A medida** (`metrics.py`, só descritiva e fora do Holm):
  - `contribuicao_drives`: c_d = w_d · (falta_antes² − falta_depois²), em inteiros na escala S;
  - `parcelas_drives`: p_d = |c_d| / Σ|c|;
  - `dominancia_decisoes`: por vida, as decisões com sinal, separadas em tempo livre e o resto. Sai quantas cada drive lidera
    (p_d ≥ `LIMIAR_LIDERA`, 0,80), f_d, a parcela agregada e a contribuição com sinal;
  - `leitura_dominancia`: a regra de leitura da A2.3. "Domina" quando o IC95 inferior de f_d (10.000 reamostragens, semente 4242) passa
    de `LIMIAR_DOMINA` (0,50).
- **Na bancada:**
  - **o registro:** o `_Registro` anota, por decisão, o tick, a regra e o estado antes e depois da ação. Na fruta, o depois é o estado
    logo depois de comer, com o humor (E2), pelo gancho `fruta_comida`;
  - **por vida:** `Bancada.medidas_dominancia`, no bloco `dominancia` do `medidas.json`, na janela dos últimos sete dias e na vida toda;
  - **por grupo:** `tabela_dominancia` grava o `dominancia.json`, por braço × condição × tipo de decisão, com f_d por unidade (os donos
    somados) e a leitura.
- **Os drives,** pelos nomes do corpo (`NOMES_DRIVES`): fome, desconforto e cansaço, os de `ConfigConsequencia.drives`, mais a tristeza
  (o humor) na fruta com a E2. Os drives novos (tédio, solidão, estresse, dor) entram quando o corpo os tiver.
- **`origem`:**
  - nos braços que aprendem pela consequência, a medida é o sinal deles (`"sinal"`);
  - nos outros (o P0, o P3), é a mesma conta como sonda (`"sonda"`).
- **A conferência:** com os canais e o aprendizado ligados, a soma por canal dos sinais recalculados (`lobos.sinal_por_canal`) tem de
  ser o total que o cérebro guardou; se não for, falha alto.
- **O braço P1-cw** (`Braco.pesos_janela`, nó `corpo-A2.4`):
  - está declarado e falha alto com o nó (`NOS_PENDENTES["pesos_janela"]`) até o B pôr a chave `pesos_janela` na `ConfigConsequencia`;
  - ele também depende dos braços do corpo (P1-c), que a bancada ainda não tem.
- **Testes:** `tests/test_dominancia.py`, 17 (~5 s). As funções são conferidas em dados sintéticos com a resposta conhecida; a conferência
  com os canais em quatro mundos, e ela falha alto quando os dois lados diferem.

## V2, W-LIGA-MUNDO — o instinto do mundo ligado na bancada (2026-10-07, `docs/TAREFA_V2_MUNDO_FISICO.md`, etapa 3) — GATES PASSAM

Rodada 18. Os quatro passos listados no #231, com a etapa 3 do B (#232) na `main`. Infraestrutura, sem run de pesquisa; só as sementes
dos testes. Mudaram `experiments/bancada_v2.py`, a fumaça `experiments/configs/v2_mundo/fumaca.json`, o
`tests/test_bancada_mundo_fisico.py` (a seção 3 e a contagem da fumaça) e o teste novo. `engine.py`, `mundo.py`, `instinto_mundo.py`,
`lobos.py`, `metrics.py` e a web não mudaram. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **Sem o `NOS_PENDENTES["instinto_mundo"]`:**
  - a entrada saiu, e a checagem da run com plano em `validar_config` também;
  - fica só a `pesos_janela` (o P1-cw).
- **O cérebro `instinto` no mundo físico** é a `PoliticaInstintoMundo`, só no P0 e no P0z.
- **O P0z** é a `PoliticaInstintoMundo` com `sem_explorar=True`, **em qualquer cérebro da config**, porque os lobos não têm o modo.
  - O rótulo segue o cérebro da espécie (`P0z` ou `P0z~instinto`), mas a vida é a mesma (teste).
  - Fora do mundo físico, o P0z continua um `ValueError`.
- **Os lobos no mundo físico:** `PoliticaLobos(..., cfg_mundo=self.cfg_mundo_de(mundo))`.
  - `Bancada.pesos_do_mundo()` dá a `ConfigBola` e a `ConfigFrutas` da bancada com a chave desligada. Elas só levam os pesos `w_bola` e
    `w_fruta` ao instinto do mundo e ao prior dos lobos, e o `MotorMundo` e os lobos exigem as duas desligadas.
  - O `escolher_alvo` dos lobos devolve None, o alvo padrão do motor: o cérebro A aprende **quando** agir, não **para onde** ir.
- **Gates** (`tests/test_bancada_liga_mundo.py`, ~2 min):
  - **o P0 com lobos é o instinto do mundo byte a byte** (o `resumo_motor`: log, estado, ações, rngs e o registro do mundo). Vale nos
    dois layouts, 4 donos × 3 lugares × 2 sementes, nas montagens simples e completa;
  - **os lobos veem o mundo:** a regra `fruta_no_cenario` dispara, e o gancho do alvo anota os candidatos;
  - **o P0z:**
    - nenhuma ação explorar;
    - a mesma vida com os dois cérebros;
    - G1;
    - o P0 explora na mesma semente;
  - **os acoplados P0^ac (P0 ← P0z) e P1^ac (P1 ← P0z):** os mesmos gestos do dono nos mesmos ticks e lugares, e G1;
  - **o P1 aprende pela consequência no mundo**, e a dominância sai com `origem` `"sinal"`;
  - a config com plano (bases 31101, prefixo `mundo`) valida.
- **Fumaça** (`experiments/configs/v2_mundo/fumaca.json`, NÃO canônica):
  - os braços P0, P0z, P1 e P3;
  - os acoplados P1 ← P0, P0 ← P0z e P1 ← P0z;
  - sem artefato.

## V2, CORPO-MUNDO e PESOS-JANELA — os estímulos do mundo físico no corpo e o peso pela janela no cérebro A (2026-10-07) — GATES PASSAM

Pedido do Gerente depois da etapa 3 do mundo. Infraestrutura, sem run; só as sementes dos testes. Mudaram `digilab/corpo.py`,
`digilab/policies/lobos.py` (atrás da chave), a `ConfigConsequencia`, o exportador e o gabarito da paridade do corpo. `engine.py`,
`mundo.py`, o motor do corpo, a bancada e a web não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **Os estímulos do mundo no `Corpo`** (para o A ligar o `MotorMundo` no `MotorCorpo`):
  - `estimulo_andar`: cansaço + 75 por subunidade;
  - `estimulo_consumo_mundo`: a ração madura (a do alimentar), a fruta madura (67500 e o efeito dela) e a podre (só o humor);
  - `acao_pet(..., com_mundo=True)`: a MF-2, comer sem comida não dá fome;
  - a bola do mundo é o `estimulo_bola` de sempre.
- **G-HOJE contra o float do `mundo.py`** (`tests/test_corpo_mundo.py`): a grade de cada comida pelo `_comer_mundo` do mundo e vidas
  decisão a decisão (os drives a até 1e−9, com e sem a digestão, todos os estímulos cobertos).
- **O gabarito da paridade** do corpo foi à versão 3 (a seção `mundo`); as seções de antes saem idênticas.
- **`ConfigConsequencia.pesos_janela`** (A2.4, o braço P1-cw; desligada por padrão) e `janela_pesos` (J = 32):
  - o peso de cada drive é `max(div_arred(S, 4), S − div_arred(3 · m_d, 4))`, com m_d a falta média nas J decisões anteriores;
  - é o mesmo no antes e no depois, e a janela anda depois da decisão;
  - o sinal com os pesos é calculado no cérebro (`sinal_homeostatico(..., pesos)`, e as variantes da E2 e dos canais), na E2 e no
    `consequencia_mundo`;
  - os pesos ficam no motivo de cada decisão;
  - desligada, o sinal e a vida de hoje.
- **Testes:** `tests/test_pesos_janela.py`. A conta exata do peso e do sinal (a fome 0,4 → 0,7 com peso de um quarto dá 276 no lugar de
  1104); a janela refeita por fora decisão a decisão numa vida; a E2 e os canais nas frutas; o mundo físico; o G1.

## V2, W-LIGA-PESOS-JANELA — o braço P1-cw ligado na bancada (2026-10-07, `docs/PLANO_ANALISE_V2_CORPO_DRIVES.md`, adendo 2, A2.4) — GATES PASSAM

Rodada 18. A chave `pesos_janela` do B (#236) na `main`. Infraestrutura, sem run de pesquisa; só as sementes dos testes. Mudaram
`experiments/bancada_v2.py`, o teste do P1-cw em `tests/test_dominancia.py`, um comentário de `tests/test_bancada_v2.py` e o teste novo.
`engine.py`, `lobos.py`, o corpo e a web não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **O `NOS_PENDENTES` ficou vazio:** a entrada `pesos_janela` saiu.
- **O P1-cw** é o P1 com `ConfigConsequencia.pesos_janela` ligada (`Bancada.politica`; J = `janela_pesos`, 32). O resto vem do P1, inclusive as
  peças da montagem completa e os canais da config.
- **A dominância do P1-cw** (A2.2: c_d = w_d · Δ_d):
  - o w_d é o peso da janela que o cérebro usou na decisão, lido do motivo (`pesos_janela`);
  - na decisão sem fruta entram só os drives do N3, porque o cérebro pesa também o humor em toda decisão;
  - a conferência com os canais recalcula o sinal com os mesmos pesos (`sinal_por_canal(..., pesos)`);
  - uma decisão sem os pesos no motivo falha alto;
  - o `_Registro` anota o índice da decisão (`k`) em cada passo.
- **Gates** (`tests/test_bancada_pesos_janela.py`):
  - **com a chave desligada, o P1-cw é o P1 byte a byte** (o `resumo_motor` e o estado interno, fora o rótulo do braço). Os braços do corpo
    (P1-c) ainda não existem na bancada, então o gate é contra o P1. Vale em `padrao`, `bola`, `descasado`, `mutavel`, `fisico` e
    `fisico_afastado`, com 2 donos × 2 sementes, nas montagens simples e completa, com os canais;
  - **ligada:** a chave chega ao cérebro, a vida muda em todo mundo e passa o G1;
  - **o peso pela falta média:** a janela é refeita por fora, decisão a decisão (`pesos_da_janela` das faltas das J decisões anteriores,
    igual ao motivo). Algum peso cai abaixo de S, e todos ficam entre S/4 e S;
  - **a dominância** confere com os canais nos três mundos. Com o sinal recalculado sem os pesos, ela falha alto.
- **Fumaça do corpo:** não existe ainda em `experiments/configs/`, então o P1-cw não entrou em nenhuma.

## V2, MUNDO-CORPO — o MotorMundo no MotorCorpo (2026-10-07, `docs/TAREFA_V2_CORPO_DRIVES.md`, seções 2, 9 e 12) — GATES PASSAM

Pedido do Gerente depois do #236 (os estímulos do mundo no `corpo.py`) e do #235 (o instinto do mundo na bancada). Infraestrutura, sem run;
só as sementes dos testes. Mudaram `digilab/motor_corpo.py` e `digilab/mundo.py` (um gancho, mesma conta), mais o teste antigo que esperava
a falha. `engine.py`, `corpo.py`, os cérebros, a bancada e a web não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **A trava saiu:** `com_corpo(MotorMundo)` com o mundo ligado roda.
- **Os estímulos, na ordem do Gerente:**
  1. **a MF-2:** `Corpo.acao_pet(acao, com_mundo=True)`, na decisão;
  2. **o andar:** `estimulo_andar(deslocamento, custo_energia_por_subunidade)`;
  3. **a comida do mapa** (o comer e o achou e comeu): `estimulo_consumo_mundo(tipo, situacao, cmf, efeito_frutas[tipo])`;
  4. **a bola:** `estimulo_bola(ganho_humor_bola)`.
  - Os três últimos vêm do `MotorCorpo._consequencia`, que envolve a do `MotorMundo`.
  - **G-BYPASS:** só a energia (o andar), a fome e o humor (a comida) e o humor (a bola) podem mudar no float de baixo; fora disso, falha
    alto.
  - Depois, o Estado volta a ser a leitura do corpo, e os estímulos entram no `ocorrido` do `consequencia_corpo` (`("andar", d)`,
    `("comida", tipo, situacao)`, `("bola",)`).
- **Os ganchos:**
  - o `obs_depois` do mundo sai de `MotorMundo._observacao_depois_mundo`, e o `MotorCorpo` põe o `obs.corpo` por cima. O
    `consequencia_mundo` recebe os receptores já com os estímulos da própria ação, só nas decisões de explorar, comer e brincar, como hoje;
  - o `consequencia_corpo` continua com uma chamada por decisão, sempre, depois do `consequencia_mundo`.
- **Gates** (`tests/test_corpo_no_mundo.py`, 11 testes, ~1 min):
  - **G2:** as 144 vidas do mundo físico de hoje, pela bancada, iguais a `tests/gabaritos/corpo_mundo_vidas_de_hoje.json` byte a byte, com o
    `MotorCorpo` desligado na frente do `MotorMundo` e sem ele. O gabarito foi gravado antes, de um snapshot de origin/main
    (`tests/gabarito_corpo_mundo.py`, commit próprio);
  - **G-HOJE (a) no mundo físico:** malha aberta contra o `MotorMundo` de hoje, tick a tick, em 4 donos × 3 lugares × 2 sementes, com a
    química sozinha e com os dois órgãos. Os drives ficam a até 7e−14, e as 5 viradas de privação são todas um químico exatamente no
    limiar. A posição, as comidas, os consumos, as quedas, a bola e as rngs do mundo saem iguais. O sinal do N3 sai igual em 6912 de 6912
    decisões;
  - **a conta exata:** o cansaço sobe 75 por subunidade andada; a ração tira 202500 da fome, a fruta 67500, a podre põe 45000 de tristeza
    e a bola tira 67500;
  - **a MF-2:** o comer sem comida não mexe na fome do corpo;
  - **os ganchos, o bypass no mundo e o G1** (instinto do mundo e lobos aprendendo, estado interno e registro do mundo incluídos);
  - **a bancada monta o mundo físico com o corpo:** sem mudar a bancada, com o `MotorMundo` dela trocado pelo com corpo. P0 (lobos e
    instinto), P0z, P1 e P3 rodam nos dois layouts, e o G1 da bancada passa.
- **Para o D:** a chave do corpo na bancada (o `cfg_corpo` na fábrica do mundo físico) fica com ele.

## V2, CORPO-CEREBRO — o cérebro A no corpo, etapa 5 (2026-10-07, `docs/TAREFA_V2_CORPO_DRIVES.md`) — GATES PASSAM

Etapa 5 da seção 14 (seções 9 a 11). Infraestrutura, sem run; só as sementes dos testes. Mudaram `digilab/policies/lobos.py` (atrás da
chave), `digilab/motivo.py` (o embrulho) e a `ConfigConsequencia`. `engine.py`, `corpo.py`, `motor_corpo.py`, a bancada e a web não.
Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **A chave:** `PoliticaLobos(..., cfg_corpo=ConfigCorpo)`, ligada. Sem ela, o cérebro de hoje, inclusive num `MotorCorpo`.
- **`lobos.sinal_corpo`** sobre os receptores:
  - D = Σ w_d · falta_d², com a falta = S − leitura nos drives de hoje e a leitura nos novos, e f = div_arred(ganho · ΔD, S);
  - os drives: os do N3, o humor só no comer de fruta (E2) e os drives novos que o corpo tiver (o susto fora);
  - `w_d` em `ConfigConsequencia.pesos_drives_corpo`, todos 1; compõe com a `pesos_janela` (A2.4), que passa a ler os receptores.
- **O gancho:** o crédito espera `consequencia_corpo`, ou `consequencia_mundo` no mundo físico (explorar, comer e brincar), uma chamada por
  decisão em toda fonte, conferida (falha alto). O `f_S` da transição é conferido e não creditado.
- **As entradas novas:** as leituras dos receptores novos, só nas regras de tempo livre, um peso por (regra, ação, receptor), prior 0.
  Nas frutas, 763 → 868 pesos; com o mundo físico, +126.
- **Os canais novos:** um por drive novo, todos ao corpo, na mesma soma telescópica.
- **O embrulho:** o `PoliticaComMotivo` repassa `consequencia_corpo` e `mudanca_no_corpo`. Uma entrada nova aprendida que pese na decisão
  faz o motivo falhar alto (sem fator na expressão até a etapa 6).
- **Gates** (`tests/test_corpo_cerebros.py`, 42):
  - **G-HOJE (a) do sinal, malha aberta:** iguais 20.736 de 20.736 decisões, nos 3 mundos, com a química sozinha e com os dois órgãos;
  - **malha fechada:** o P1 com a chave do corpo e o P1 de hoje, no mesmo motor com o corpo, são a mesma vida byte a byte (padrão, bola e
    frutas; escalar, canais e janela);
  - **mundo físico:** as chamadas de uma vida do P1 rejogadas num cérebro com o corpo dão as mesmas decisões e os mesmos pesos;
  - **as contas exatas:** a conta da seção 9 (+1440 contra −34), as entradas novas pela regra da L1 e os canais;
  - **as entradas novas no prior** não mudam a decisão (3000 observações);
  - o G1, o embrulho e as falhas altas do gancho.

## V2, CORPO-DRIVES — o grafo do corpo e a etapa 6 (química e cérebro) (2026-10-07, `docs/TAREFA_V2_CORPO_DRIVES.md`, seções 7, 8, 17 e 18) — GATES PASSAM

Infraestrutura, sem run; só as sementes dos testes. Mudaram:
- `digilab/corpo.py`;
- `digilab/corpo_grafo.py` (novo);
- a `ConfigCorpo` e a `ConfigLobos.recompensa_tapa`;
- `digilab/policies/lobos.py` e `digilab/motivo.py`;
- o exportador e o gabarito da paridade do corpo (versão 4).

`engine.py`, `motor_corpo.py`, `mundo.py`, a bancada e a web não mudaram. O motor da etapa 6 é do A. Interpretações em
`docs/REGISTRO_DESVIOS.md`.
- **A combinação #238 + #239:** o cérebro com `cfg_corpo` no `MotorCorpo` com o mundo físico falhava alto, porque o motor chama os dois
  ganchos na mesma decisão. Agora o `consequencia_mundo` credita, e o `consequencia_corpo` fecha a decisão. Entrou o G1.
- **O grafo (seção 18):** `corpo.grafo_do_corpo` monta a tabela única (químicos, reações, emissores, receptores, meias-vidas, tetos), e o
  `Corpo` a usa (tick em fases, receptores, meias-vidas) e a confere na carga. As checagens de `corpo_grafo.checar` falham alto:
  - fechado;
  - sumidouro;
  - automantido;
  - laço de ganho ≥ 1.
  - O relato traz os pares com meias-vidas na mesma ordem (hoje, dor e susto). As vidas de hoje não mudam (G2).
- **Os drives novos** (`drives_novos`):
  - o tédio pela variedade (DS-4, `atividade`);
  - a curiosidade (só com `com_mundo`, `estimulo_novidade`);
  - a solidão;
  - o estresse (o limiar 0,75, o divisor 256, a meia-vida 1440).
- **Os gestos** (`gestos`):
  - o tapa (dor, susto, estresse);
  - as meias-vidas da dor (60) e do susto (30);
  - o medo da mão no carinho (CD-5).
- **O cérebro A:**
  - o tapa credita `recompensa_tapa` à última decisão, em quem aprende;
  - o `mudanca_no_corpo` credita o carinho pelo corpo, acerta o relógio do cuidado e paga os chamados;
  - o embrulho anda o relógio.
- **Gates:**
  - `tests/test_corpo_grafo.py`: as checagens passam em toda combinação de sub-chaves e falham alto nas tabelas feitas para falhar, e o
    `Corpo` usa a tabela;
  - `tests/test_corpo_drives.py`: o G-MEC do corpo;
  - `tests/test_corpo_risco.py`: o G-RISCO e o G-MEC do cérebro, o tapa e o carinho na última decisão e o G1 com os drives novos;
  - `tests/test_corpo_cerebros.py`: o G1 do cérebro com o corpo no mundo físico.
- **Achado:** com os números PROPOSTOS o tédio do P1 no mundo da bola não passa de ~0,3. A vida curta do G-RISCO roda no ponto (2, ½) da
  grade do plano, e a direção vale por pouco (0,57 → 0,61).

## V2, W-BANCADA-CORPO — o corpo na bancada, etapa 8 (2026-10-07, `docs/TAREFA_V2_CORPO_DRIVES.md`, seção 14) — GATES PASSAM

Rodada 21. A etapa 8 do corpo: o que dá para rodar sem a etapa 6, e o resto declarado. Infraestrutura, sem run de pesquisa; só as sementes
dos testes. Mudaram `experiments/bancada_v2.py`, a fumaça nova `experiments/configs/v2_corpo/fumaca.json`, os testes do P1-cw
(`tests/test_bancada_pesos_janela.py`, `tests/test_dominancia.py`), a tabela de braços de `tests/test_bancada_v2.py` e o teste novo.
`engine.py`, `corpo.py`, `motor_corpo.py`, `lobos.py`, `metrics.py` e a web não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **O regime é um campo do braço** (`Braco.regime`), com os nomes do plano:
  - **"hoje":** a chave do corpo desligada;
  - **"química":** a `ConfigCorpo` da bancada (`CONFIG_CORPO_QUIMICA`: ligada, a digestão na taxa C e a Vida, sem os drives novos);
  - **"corpo":** a química mais `drives_novos` e `gestos`.
  - Com o regime, o motor é o `com_corpo(...)` do mundo, e o cérebro A recebe `cfg_corpo`. Os braços sem regime (os de antes) não mudam.
  - **A chave `corpo` da config** troca os números da `ConfigCorpo` (por exemplo a `taxa_digestao`), nunca as sub-chaves.
  - No `padrao` com genoma, os braços do plano usam o `MotorPersonalidade` com a obediência desligada nos dois regimes, como os mundos da
    bola e das frutas.
- **Os braços do plano** (`BRACOS`, seções 3.1 a 3.3 e adendos 1 e 2):
  - **rodam:** o bloco G-HOJE (P0, P1 e P3 em "hoje" e em "química");
  - **esperam a etapa 6 e falham alto com o nó** (`NOS_PENDENTES`):
    - P0-q e P1-q (o `DonoComGestos`);
    - P0-c e P1-c (os drives novos e os gestos);
    - P0-c-tapa, P1-c-tapa e P1-c-tapaX (também o tapa);
    - P1-c-frutas;
    - o **P1-cw**, que passou a ser o P1-c com a `pesos_janela`, como o plano pede (A2.4);
  - o filtro `sem_gestos` também espera o tapa.
- **O corpo no mundo físico fica pendente** (`NOS_PENDENTES["corpo_mundo"]`): o `MotorCorpo` chama `consequencia_corpo` em toda decisão (#238),
  e o `PoliticaLobos` com `cfg_corpo` recusa esse gancho em explorar, comer e brincar no mundo físico (#239). O regime "hoje" roda no mundo
  físico.
- **As medidas** (bloco `corpo` do `medidas.json`, nas vidas com o corpo ligado; seção 5 do plano, funções do #224), nos últimos sete dias:
  - `BE` e `OC` (`tempo_livre_be`; a vida toda ao lado);
  - o cuidado preservado (`cuidado_preservado`);
  - os drives novos (`drives_novos`), indisponíveis com o nó até a etapa 6;
  - o corpo no fim.
- **A dominância pelos receptores:**
  - com o corpo ligado, ela usa a conta do cérebro (`lobos.contribuicoes_corpo`), sobre os receptores da decisão e os de depois (o gancho
    `consequencia_corpo`, anotado pelo `_Registro`);
  - os w_d são os da `pesos_drives_corpo` e, com a `pesos_janela`, os da janela do motivo;
  - nos braços que aprendem pela consequência, a conta é conferida contra o motivo (`sinal_corpo`) e contra os canais; se divergir, falha
    alto.
- **A deriva com o corpo:** as sondas ganham os receptores do próprio estado (`percepcao_da_sonda`, a conta do corpo), e o prior é o P0 do
  mesmo regime.
- **Gates** (`tests/test_bancada_corpo.py`):
  - **o "hoje" é a vida de antes byte a byte** (P0, P1 e P3, sete mundos com o físico, duas montagens);
  - **a química** liga o corpo no motor e no cérebro, passa o G1 e o acoplado, e o P1-química aprende pelo sinal do corpo;
  - **a chave `corpo`** troca os números e não as sub-chaves;
  - **as medidas e a dominância** batem com o motivo e os canais nos três braços, e falham alto quando a conta diverge;
  - **o que espera a etapa 6, o filtro e o corpo no mundo físico** falham alto com o nó, e a trava é só a tabela;
  - a config com o plano (bases 33101, prefixo `corpo`) valida;
  - o `rodar` da fumaça.
- **O mecanismo do P1-cw** (`tests/test_bancada_pesos_janela.py`) é conferido em dois braços de teste no lugar dele: o P1 com a chave e o
  P1-química com a chave. Os dois passam o gate (chave desligada = a origem byte a byte), mudam a vida, passam o G1 e têm a janela refeita
  por fora (pelo vetor e pelos receptores). A dominância confere com os pesos.
- **Fumaça** (`experiments/configs/v2_corpo/fumaca.json`, NÃO canônica):
  - o bloco G-HOJE nos mundos `bola` e `padrao`;
  - os acoplados P1-química ← P0-química e P1-hoje ← P0-hoje;
  - sem artefato.

## V2, CORPO-GESTOS — a etapa 6 do corpo, a parte do motor (2026-10-07, `docs/TAREFA_V2_CORPO_DRIVES.md`, seções 7, 8 e 14) — GATES PASSAM

Etapa 6 da seção 14, o lado do A. A química dos drives novos e dos gestos, o sinal do tapa e o grafo validado (seção 18) são do B, em
paralelo. Infraestrutura, sem run; só as sementes dos testes. Mudaram `digilab/events.py` (o fim do enum), `digilab/motor_corpo.py`,
`digilab/mundo.py` (o canal do `simular_vida_mundo`), `digilab/gestos.py` (novo) e o teste do enum do N7. `engine.py`, `corpo.py`,
`lobos.py`, a bancada e a web não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **O contrato com o B**, combinado antes do código. O motor chama, no `Corpo`:
  - `acao_dono(TAPA)`: dor, susto e estresse; nenhum drive do Estado muda;
  - `acao_dono(ACARICIAR)`: solidão e estresse com o medo da mão, dentro do corpo;
  - `atividade(nome)`: o tédio pela variedade (DS-4), com `"bola"`, `"brincar"` ou `"explorar"`;
  - `estimulo_novidade(n)`: a curiosidade, com a contagem crua;
  - `de_estado(..., com_mundo)`: a curiosidade só existe com o mundo físico (CD-8);
  - e lê `ConfigCorpo.janela_novidade`.
- **Sobre o corpo real do B (#247):** os testes usam um espião do `Corpo` real, que só anota as chamadas do motor, com as sub-chaves de
  verdade (cada uma exige a anterior: `drives_novos` precisa da digestão e da Vida, e `gestos` precisa de `drives_novos`).
- **`AcaoUsuario.TAPA = "tapa"`** no fim do enum, com `ACOES_CORPO`. Nos motores de hoje e no `reproduzir` de hoje, o tapa falha alto; no
  `MotorCorpo` sem `gestos`, falha alto com `GestoSemChave`.
- **Os gestos (`gestos`):** o tapa e o carinho viram só o estímulo do corpo e contam como contato (CD-6), com os efeitos das classes do
  meio na ordem delas (a janela da educação, o índice do evento e o vínculo do `MotorPersonalidade`).
  - **o tapa** vai ao cérebro por `receber_acao_dono`, o sinal direto, e não chama o `mudanca_no_corpo` (CD-9);
  - **o carinho** não é repassado: o cérebro o vê só pelo `mudanca_no_corpo(obs_antes, obs_depois)`, com o `obs.corpo` (e o `obs.mundo`
    no mundo físico). O gancho não diz que gesto foi.
- **Os drives novos (`drives_novos`):**
  - `atividade` uma vez por decisão de brincar ou explorar, depois dos estímulos da ação. No mundo físico ela vem na consequência dele,
    antes do `obs_depois`;
  - **no mundo físico, a novidade:** o motor guarda o que o pet viu e quando, ao decidir e depois de cada decisão com alvo. Uma novidade
    é um objeto dos `vistos` não visto nas últimas `janela_novidade` ticks, achado ao explorar. O `ocorrido` do mundo ganha
    `vistos_novos` (`[[id, tipo], ...]`, vazio fora do explorar), e o corpo recebe a contagem;
  - sem `drives_novos`, o `ocorrido` do mundo é o de hoje.
- **`digilab/gestos.py`:**
  - **`DonoComGestos(base, modo)`:** o `elogiar` vira `acariciar`, e o `repreender` vira `tapa` (modo `"tapa"`) ou `SemGesto` (modo
    `"sem_tapa"`). O `SemGesto` gasta a interação do orçamento sem chegar ao motor, então o orçamento fica igual;
  - **os canais:** `CanalComGestos` e `CanalMundoComGestos`;
  - **as vidas:** `simular_vida_gestos`, e o `mundo.simular_vida_mundo(..., canal_classe=)`.
- **Gates** (`tests/test_corpo_gestos.py`, 22 testes, ~5 s):
  - **G2:** a suíte confere os gabaritos de sempre com o corpo desligado (`test_corpo`, `test_corpo_no_mundo`, `test_mundo` e os demais);
  - o enum, o tapa sem a chave e o carinho de hoje sem `gestos`;
  - o tapa e o carinho nos mundos `padrao`, `bola` e `mundo`: o repasse, o gancho, o contato e o orçamento. O tapa não muda drive;
  - o vínculo e o índice do evento no `MotorPersonalidade`;
  - o `DonoComGestos` nos 4 donos e nos dois modos, com o orçamento inteiro;
  - a atividade por decisão; os `vistos_novos` e a novidade refeitos por fora, com a janela de 1440 e de 60;
  - **G1** com os gestos e os drives novos, nos três mundos e nos dois modos.
- **O `test_corpo_risco` do B:** a vida curta passou a usar o `com_corpo(MotorAmbiente)`. O motor de teste dele avisava a atividade de novo, por
  cima do meu, e o tédio caía em dobro (o `ZeroDivisionError`). A contagem saiu igual à dele: 4/7 → 23/38.
- **Para o D:** na bancada, o `cfg_corpo` com as sub-chaves, o tapa passando pela `PoliticaDoBraco`, o `SemGesto` nos canais dela e o
  filtro `sem_gestos` do acoplado ficam com ele.

## V2, CORPO-WEB — o corpo em TypeScript, etapa 7 (2026-10-07, `docs/TAREFA_V2_CORPO_DRIVES.md`, seção 14) — G-PAR PASSA

Etapa 7 da seção 14: só o motor e a paridade, sem tela e sem versão de pet nova (como no mundo). Mudaram `web/app/motor/corpo.ts` (novo), o
`motor/index.ts` (exporta o corpo), `motor/constantes.ts` (a `ConfigCorpo` no fim), o exportador e o gabarito do corpo (versão 5) e o teste
dele em `tests/test_corpo_quimica.py`. `digilab/`, o app, os pets e os gabaritos da web não mudaram. Interpretações em
`docs/REGISTRO_DESVIOS.md`.
- **`motor/corpo.ts`** é o porte de `digilab/corpo.py` e de `digilab/corpo_grafo.py`, com os nomes do Python nos registros:
  - **a química e as taxas:** `configCorpo` (a `ConfigCorpo` com a checagem do `__post_init__`), `taxasDe` (a `Config` de hoje pelo espelho
    `C`), `quimicosDe`, `naGrade`, `passoMeiaVida` e `kMeiaVida`; o `divArred` é o de `motor/mundo.ts`;
  - **o grafo (seção 18):** `grafoDoCorpo` monta a tabela única e `checarGrafo` faz as quatro checagens (fechado, sumidouro,
    automantido, laço de ganho ≥ 1, o produto em `BigInt`) e o relato, falhando alto com `GrafoInvalido`;
  - **a classe `Corpo`:** o tick em fases pelos emissores da tabela, a digestão com o descarte, a Vida e o estágio, os drives novos (o
    tédio pela janela, a curiosidade só com `comMundo`, a solidão, o estresse), os gestos (o tapa, a dor, o susto, o medo da mão no
    carinho), os estímulos de hoje e os do mundo físico (a MF-2, o andar, as comidas do mapa) e as leituras (`receptores`, `drives`,
    `estagio`, `paraDict`).
  - O corpo não tem rng: a sujeira e o sono vêm do estado no começo do tick, como no Python.
- **O gabarito, versão 5** (`python experiments/exportar_gabarito_corpo.py`), com quatro seções novas; as da versão 4 saem idênticas
  (conferido):
  - `config`: a `ConfigCorpo` padrão, campo a campo;
  - `grafo`: a tabela e o relato do `checar` em 6 combinações de sub-chaves (com e sem o medo da mão), com e sem o mundo;
  - `de_estado`: o corpo que nasce de 3 Estados em cada combinação;
  - `etapa6_mundo`: os estímulos do mundo físico no corpo da etapa 6.
- **G-PAR** (`web/app/test/corpo.test.ts`, 27 testes, ~1 s). A web lê o próprio `tests/gabaritos/corpo_quimica_python.json`, sem cópia:
  - a config, as taxas, os químicos, os ticks de estágio e os limiares saem iguais;
  - o `div_arred` e a meia-vida;
  - o grafo: a tabela e o relato iguais nas 12 combinações, e as tabelas do `tests/test_corpo_grafo.py` falham alto pela mesma checagem;
  - o corpo que nasce de um Estado (q, receptores, drives, `para_dict`);
  - as grades de casos de cada etapa: a química, a digestão, a digestão lenta, a Vida, o mundo físico sem e com a digestão, a etapa 6 e o
    mundo na etapa 6;
  - as 9 vidas em malha aberta, com o sha256 de q depois de cada operação, os pontos, o digerido e os estágios;
  - a sequência de 3000 operações da etapa 6, com o sha256 de q e da janela.
  - Quatro mutações no `corpo.ts` (a meia-vida sem o mínimo de 1, o carinho sem o medo, a janela do tédio, a sujeira no tick) fazem o
    teste falhar.

## V2, W-LIGA-GESTOS — a etapa 6 do corpo ligada na bancada (2026-10-07, `docs/TAREFA_V2_CORPO_DRIVES.md`, seção 14, etapa 8) — GATES PASSAM

Rodada 22, com o #245 (o motor dos gestos e o `DonoComGestos`, do A) e o #247 (a química dos drives novos e dos gestos e o cérebro, do B)
na `main`. Infraestrutura, sem run de pesquisa; só as sementes dos testes. Mudaram `experiments/bancada_v2.py`, a fumaça
`experiments/configs/v2_corpo/fumaca.json`, três testes antigos e o teste novo. `engine.py`, `gestos.py`, `corpo.py`, `motor_corpo.py`,
`lobos.py`, `metrics.py` e a web não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **Sem nós pendentes:** saíram `corpo`, `dono_gestos`, `tapa` e o `corpo_mundo` (o #247 resolveu o mundo físico; conferido por teste). O
  `NOS_PENDENTES` e o `FILTROS_PENDENTES` ficaram vazios.
- **Rodam todos os braços do plano:**
  - o bloco G-HOJE;
  - o bloco do corpo: P0-q, P1-q, P0-c e P1-c;
  - o bloco do tapa: P0-c-tapa e P1-c-tapa;
  - o bloco G: P1-c-tapaX e P1-c-frutas;
  - o P1-cw.
- **O dono dos braços com gestos** é o `DonoComGestos(criar_dono(...), modo)`. No P1-c-tapaX ele vem ainda dentro do `DonoTapaFruta`: um
  tapa por consumo da fruta X (`fruta_tapa`, rng `tapa-fruta`) no passo do dono seguinte, dentro do orçamento, no modelo do
  `DonoJulgaFruta`.
- **A bronca do modo sem tapa nos canais:** o `simular_vida_mundo` da bancada aceita `canal_classe` (o `CanalComGestos`), e o mundo padrão
  usa o `simular_vida_gestos`. O `SemGesto` gasta o orçamento fora do log e é contado em `VidaBancada.retirados`. Os gestos ficam fora do
  mundo físico e do `bola_a1` (falha alto).
- **O tapa e o carinho no cérebro:**
  - o tapa passa pela `PoliticaDoBraco` em toda fonte que aprende (CD-10);
  - o carinho (`mudanca_no_corpo`, CD-4) chega nas mesmas fontes;
  - no P0, nenhum dos dois;
  - o `_Registro` acerta o relógio do cuidado no carinho.
- **O filtro `sem_gestos`** do acoplado tira o tapa e o carinho.
- **As medidas:** os drives novos (tédio, solidão, estresse e dor) saem disponíveis no bloco `corpo` dos braços do regime corpo, com os
  gestos da vida. A sonda da deriva ganhou os receptores novos, uniformes em [0, S] pela rng `sonda-corpo` (`percepcao_da_sonda`,
  `receptores_novos_de`).
- **Gates** (`tests/test_bancada_liga_gestos.py`, 39 testes, ~40 s):
  - **os braços do plano rodam e medem**, com o G1 de toda vida;
  - **G-P0C:** o P0-c decide igual ao P0-q, decisão a decisão e com o mesmo log (4 donos × 2 sementes, em `bola`, `padrao` com e sem
    genoma e `iguais_frutas`);
  - **o P1-c-frutas é o P1-c byte a byte**, fora o rótulo;
  - **o orçamento fecha com o `SemGesto`;** no P0, com o aleatório e o relapso, o tapa entra onde a bronca sumia;
  - **o tapa e o carinho chegam ao P1 e não ao P0** (as contagens do cérebro e da memória), e o tapa chega também à fonte informação;
  - **o tapa na fruta X:** a fruta é uniforme pela rng própria, e há um tapa por consumo de X no passo seguinte, com o descarte no passo
    cheio;
  - **os acoplados:** o filtro `sem_gestos`, e o P1-q^ac e o P1-c^ac do P0-q;
  - **as medidas:** os drives novos na medida e os receptores novos na sonda;
  - **o mundo físico:** o corpo roda nele, e os gestos falham alto lá;
  - a config do plano com todos os braços;
  - o replay do disco.
- **Testes antigos:**
  - `tests/test_bancada_pesos_janela.py`: o P1-cw contra o P1-c (a chave desligada sai byte a byte; ligada muda a vida, com o G1; a janela
    é refeita por fora com os receptores novos; a dominância bate com os canais);
  - `tests/test_bancada_corpo.py`: os braços se resolvem, a trava é só a tabela, e o corpo roda no mundo físico;
  - `tests/test_dominancia.py`: o P1-cw.
- **Não entrou:** as medidas descritivas dos efeitos do tapa (plano, seção 5.4).

## V2, BANHEIRO, etapa 2 — a vontade, o conforto, o `aliviar`, o instinto e o alvo (2026-10-07, `docs/TAREFA_V2_BANHEIRO.md`) — GATES PASSAM

Etapa 2 da seção 9 (BN-1 a BN-6 decididas), o lado do corpo e do cérebro. Infraestrutura, sem run; só as sementes dos testes. O banheiro no
mapa, a necessidade como objeto, o limpador, o `limpar` e o `DonoCarinhoBanheiro` são da etapa 3 (A); a web é a etapa 4; a bancada, a 5
(D). `engine.py`, `motor_corpo.py` (só dois campos novos na `PercepcaoCorpo`), `mundo.py`, a bancada e a web não mudaram. Interpretações
em `docs/REGISTRO_DESVIOS.md`.
- **A etapa 1 não existia:** o gabarito das vidas de hoje (`tests/gabarito_banheiro.py` → `tests/gabaritos/banheiro_vidas_de_hoje.json`,
  176 vidas) foi gravado antes de qualquer mudança, num commit próprio:
  - pela bancada, os regimes "hoje" e "química" do corpo e o mundo físico;
  - direto, a etapa 6 inteira com o `DonoComGestos` nos quatro mundos.
- **`AcaoPet.ALIVIAR`** no fim do enum (BN-1). Toda iteração de hoje usa `events.ACOES_PET_HOJE` (as sete de sempre): o bandit, as
  métricas, os traços, a arena, o desejo, a expressão, o cérebro A sem o banheiro, os exportadores e a bancada.
- **O corpo** (`ConfigCorpo.banheiro`, sub-chave depois de `gestos`; `CONFIG_CORPO_BANHEIRO`):
  - a `vontade` (concentração): +150 por tick acordado, mais 1/3 do alimento digerido (com o resto guardado), zerada por
    `estimulo_aliviar`. Acima de 0,75, o desconforto sobe +150 por tick (o gatilho novo `acima` do grafo);
  - a necessidade: `estimulo_necessidade` (+22500 de desconforto) e `passo(..., necessidades=n)` (+100 por tick por necessidade na
    região, até 3);
  - o `conforto` (BN-6): o carinho o sobe +45000 (com o medo da mão), meia-vida 60. O cérebro lê a falta de conforto, S − leitura;
  - os receptores `vontade` e `conforto` (os campos novos da `PercepcaoCorpo`). O grafo passa as quatro checagens.
- **`ConfigBanheiro`** (fim do `config.py`, desligada; registro `instinto_banheiro.PARAMETROS_BANHEIRO`): `ligada`, `limpador`,
  `w_vontade` 4,0, `limiar_urgente` 0,90, `limiar_moderada` 0,50, `w_banheiro_0` S/4, `w_aqui_0` S.
- **O instinto** (`digilab/instinto_banheiro.py`, `PoliticaInstintoBanheiro`, sobre o instinto do mundo):
  - a regra `alivio_urgente`, sem sorteio, logo depois do sono;
  - o `aliviar` no tempo livre com peso w_vontade × vontade;
  - o alvo herdado pelo `escolher_alvo`: `banheiro` S/4 contra `aqui` S, com u / 2^16; na urgência, `aqui`.
- **O cérebro A** (`PoliticaLobos(..., cfg_banheiro=)`, que exige o mundo físico e o corpo com o banheiro):
  - o `aliviar` só nas tabelas em que é candidato (as três de tempo livre e a urgente): **998 pesos de 1000**;
  - o prior da vontade no termo de impulsos;
  - o alvo aprendido, um peso por alvo, pela regra da fruta e com o canal do corpo, pela consequência e pelo carinho;
  - a vontade e o conforto nos drives do sinal.
- **Gates** (`tests/test_banheiro_g2.py`, `tests/test_banheiro_corpo.py`, `tests/test_banheiro_cerebros.py`):
  - **G2:** as 176 vidas de hoje byte a byte;
  - **G-MEC do corpo;**
  - **G-CONS:** com o limpador, o sinal do aliviar no banheiro é maior que fora; sem ele, igual;
  - **G-CAR:** o carinho vale 940, 1759 e 2739 contra 132 do limpador (7 a 21 vezes). Sem o conforto, a solidão em 0,2 daria 164 e
    falharia;
  - **o cérebro no prior é o instinto byte a byte** (3000 observações, a decisão e o alvo);
  - **o aprendizado do alvo em conta exata** (pela consequência e pelo carinho);
  - **o G1 do cérebro pelas chamadas.**
- **Paridade:** o gabarito do corpo foi à versão 5 (a seção `banheiro`). As seções da versão 4 saem idênticas.
- **Para o A (etapa 3):** o `aliviar` é uma ação com alvo.
  - **O alvo:** u da rng `alvo` e os dois candidatos (`banheiro` e `aqui`) no `escolher_alvo`.
  - **Os ganchos:** o `consequencia_mundo` e depois o `consequencia_corpo`.
  - **Os estímulos:** `estimulo_aliviar`, `estimulo_necessidade` e `passo(..., necessidades=n)`.
  - **O motivo do `aliviar`** ainda falha alto no `PoliticaComMotivo`: não há texto na expressão.

## V2, DOIS-PETS, etapas 0 e 1 — o gabarito de hoje e o `Mundo` como componente (2026-10-08, `docs/TAREFA_V2_DOIS_PETS.md`) — GATES PASSAM

As duas primeiras etapas do motor da frente dos dois pets (desenho `docs/futuro/dois_pets.md`, seções 2 e 10). Infraestrutura, sem run; só
as sementes dos testes. Mudaram `digilab/mundo.py` e os testes novos. `engine.py`, `motor_corpo.py`, os cérebros, a bancada e a web não.
Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **Etapa 0, num commit próprio, antes de mudar o código:** `tests/gabarito_dois_pets.py` → `tests/gabaritos/dois_pets_vidas_de_hoje.json`,
  276 vidas do mundo físico de hoje, com e sem o corpo, nos dois layouts:
  - **pela bancada**, nos mundos `fisico` e `fisico_afastado`: o P0 com lobos e com o instinto do mundo, o P0z, e P0, P1 e P3 nos
    regimes "hoje" e "química", 2 donos, os 3 lugares e 2 sementes; mais o P1 e o P3 na montagem completa;
  - **direto pelo `simular_vida_mundo`**, o que a bancada não monta no mundo físico: o corpo inteiro da etapa 6 (com a curiosidade e a
    novidade) e a bola deixada perto do pet, com o instinto do mundo e com os lobos aprendendo;
  - a impressão inclui o `resumo_mundo_fisico` inteiro (as rngs do mundo) e o registro da novidade (`_vistos_em`).
- **Etapa 1, a classe `Mundo`** (`digilab/mundo.py`): guarda o que é do mundo e não sabe de pet:
  - as árvores, as comidas, a bola e os fluxos `mundo-arvores` e `mundo-bola`;
  - os registros do mundo: as quedas, as comidas que sumiram, as bolas deixadas e as rolagens;
  - a percepção (`perceber(x, y, tick, pendente)`), as comidas maduras perto, `retirar_comida`, `rolar_bola`, `deixar_comida`,
    `deixar_bola` e o `resumo`.
- **O `MotorMundo` ligado é dono do próprio `Mundo`** (`self.mundo`, com a semente do pet). Guarda o que é do pet: a posição, o alvo
  pendente, a percepção da decisão, os fluxos `alvo` e `mundo-sujeira`, os consumos, as decisões, as regiões, as visitas e as comidas
  deixadas pelo dono. Os atributos e métodos de antes (`comidas`, `arvores`, `bola_mundo`, `quedas`, `situacao`, `bola_em`,
  `_nova_comida`...) leem do `Mundo`, e o `resumo_mundo_fisico` tem as mesmas chaves.
- **A atualização é idempotente por tick** (`Mundo.atualizar`): a segunda chamada no mesmo tick não faz nada, e um tick para trás falha
  alto. O resultado só lê o tick e o fluxo `mundo-arvores`.
- **Gates** (`tests/test_mundo_componente.py`, 18 testes, ~45 s):
  - **G2:** as 276 vidas da etapa 0, byte a byte; os gabaritos `mundo_vidas_de_hoje.json` (96) e `corpo_mundo_vidas_de_hoje.json` (144)
    passam pelos testes de sempre, na suíte;
  - **G-ENGINE:** o sha256 de sempre;
  - **o componente:** o motor é dono do próprio `Mundo` (os mesmos objetos, os fluxos pela semente do pet), e o `Mundo` não guarda
    nada do pet;
  - **a idempotência:** duas chamadas no mesmo tick dão o mesmo resumo (as rngs incluídas), o tick para trás falha alto, e atualizar só
    em alguns ticks dá as mesmas quedas e o mesmo chão que atualizar em todos;
  - **G1 com o `Mundo`:** o replay refaz o resumo do mundo, nos dois layouts, sem e com o corpo.
- **Fora:** o `Grupo` (N motores sobre um `Mundo`, a vez sorteada, o registro do grupo) é a etapa 2, no PR seguinte. O `mundo.ts` não mudou
  (etapa 9).

## V2, W-BANCADA-BANHEIRO — as faixas dos dois pets e a bancada do banheiro, só o que já dá (2026-10-08, `docs/TAREFA_V2_BANHEIRO.md`, etapa 5) — GATES PASSAM

Rodada 25. Infraestrutura, sem run de pesquisa; só as sementes dos testes. Mudaram `experiments/bancada_v2.py`, dois testes antigos (a
tabela de braços e o nó do corpo) e o teste novo. `engine.py`, `mundo.py`, `corpo.py`, `lobos.py`, `metrics.py` e a web não.
Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **As faixas dos dois pets (PDP-6)** em `FAIXAS_RESERVADAS`, com a fonte (`PLANO_ANALISE_V2_DOIS_PETS`, seção 8):
  - 39101…39505: calibração do K e piloto;
  - 40101…40505: validação;
  - 41101…41505 e 42101…42505: os adendos previstos (o degrau 1b e os dois donos).
  - O prefixo `"dois_pets"` entrou em `PREFIXOS_UNIDADES`.
- **Os braços do banheiro** (`PLANO_ANALISE_V2_BANHEIRO`, seções 1 a 3): o 2 × 2 (limpador × carinho depois do banheiro) no P0 e no P1,
  `P0-B00` … `P1-BLC`, nó `banheiro`. O campo novo é `Braco.banheiro`, e `BRACOS_BANHEIRO` dá o limpador e o carinho de cada um.
- **Falham alto com o nó** `NOS_PENDENTES["banheiro"]`: o banheiro no `MotorMundo` (a área, a necessidade como objeto, o limpador, o
  `limpar` que recolhe, o `aliviar` com alvo) e o `DonoCarinhoBanheiro` são da etapa 3, do A.
- **Já montado, atrás do nó:**
  - o corpo com os gestos e a sub-chave `banheiro` (`cfg_corpo_de`);
  - a `ConfigBanheiro` ligada, com o limpador do braço (`cfg_banheiro_de`);
  - o cérebro A com `cfg_banheiro` (o P0 com o aprendizado desligado), ou a `PoliticaInstintoBanheiro` no cérebro `instinto`;
  - o banheiro só no mundo físico, na vida e na config.
  - **A fiação do motor e do dono espera a etapa 3:** o `fabrica_motor` dos braços do banheiro falha alto com o nó, mesmo sem a tabela.
- **As medidas** (seções 4 e 8 do plano, pelas funções do #224):
  - `medidas_banheiro_de` dá a fração diária e os acidentes (`alivios_por_dia`), o dia do critério com a censura e T*
    (`dia_do_criterio`), os alívios até o critério e o cuidado preservado;
  - também dá, por dia: os carinhos (a solidão antes e o sinal pelo corpo), o sinal do alívio recolhido pelo limpador e o peso do alvo
    `banheiro` contra o de `aqui`;
  - e o "chegou tarde" (R-2).
  - `tabela_banheiro` dá a curva de Kaplan–Meier e a RMST por braço (`banheiro.json` no `rodar`).
  - `Bancada.medidas_banheiro` lê o contrato do motor (`motor.alivios`, um dict por `aliviar` com `tick`, `dentro`, `urgente`, `alvo`,
    `distancia` e `recolhido`), conferido e falhando alto. O resto vem do registro de medição e do cérebro no fim de cada dia.
  - O `_Registro` agora anota cada carinho (o tick e os receptores antes e depois).
- **Gates** (`tests/test_bancada_banheiro.py`, 21 testes, ~2 s):
  - **as faixas:** com a fonte, disjuntas, fora das queimadas e das configs; as unidades dos oito prefixos sem colisão entre planos e
    fases; a config com o prefixo pede o plano;
  - **os braços:** declarados como o plano pede; falham alto com o nó; a trava é só a tabela;
  - **as medidas:** em dados com a resposta conhecida; a tabela por braço; o contrato do motor conferido;
  - **o registro** anota cada carinho no tick do `acariciar`.
- **Fora:** os contrastes do plano (G-CARINHO e G-LIMPADOR, com Holm) são do orquestrador; a run só depois das etapas 3 e 4 do banheiro.

## V2, DOIS-PETS, etapa 4, primeira metade — o alvo aprendido no cérebro A (2026-10-08, `docs/TAREFA_V2_DOIS_PETS.md`) — GATES PASSAM

A parte da etapa 4 que não depende da percepção social (`docs/futuro/dois_pets.md`, seção 8, DP-8). Infraestrutura, sem run; só as
sementes dos testes. Mudaram `digilab/policies/lobos.py` (atrás da chave), a `ConfigLobos` e `digilab/mundo.py` (o alvo padrão virou uma
função pura, a mesma conta). `engine.py`, o corpo, a bancada e a web não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **A chave:** `ConfigLobos.alvo_aprendido` (desligada) e `w0_alvo` (S/16, PROPOSTO, SEM FONTE; registro
  `lobos.PARAMETROS_LOBOS_DOIS_PETS`). Só no mundo físico; sem ele, falha alto.
- **As classes** (`lobos.CLASSES_ALVO`):
  - comer: `comida`, `comida_podre`, `cheiro`, `continuar`;
  - explorar: `cheiro`, `vagar`, `casa`, `continuar`, e o lugar de `seguir` e `onde_comeu`, que o motor oferece a partir da etapa 3 do A;
  - brincar: `bola`, `continuar`.
- **Um peso por (regra, ação, classe)**, nas regras em que a ação com alvo é candidata (`lobos.REGRAS_ALVO`): **36 pesos**, 792 no
  mundo físico sem o corpo. Com o corpo e o banheiro (998), falha alto pelo teto.
- **A escolha** (`PoliticaLobos._alvo_aprendido`):
  - cada classe presente tem um representante, o primeiro candidato dela na ordem do motor;
  - o peso efetivo é max(0, w) / S, mais 1 na classe do alvo padrão do motor (`mundo.alvo_padrao_de`, o herdado);
  - o sorteio é o de sempre, com u / 2^16;
  - sem alvo padrão, None, como hoje.
- **O aprendizado:** só pela consequência (o crédito do `consequencia_mundo`, ou do corpo no mundo físico), pela regra da sub-decisão da
  fruta (X = S), com o sinal inteiro da decisão. O dono (elogio, bronca, carinho) não mexe no alvo.
- **O P0 usa o padrão do motor:** com o aprendizado desligado, o gancho devolve None, e o P0 com lobos continua o instinto do mundo
  byte a byte.
- **Gates** (`tests/test_alvo_aprendido.py`, 12):
  - **G2:** com a chave desligada, o gancho devolve None (e os gabaritos do mundo, na suíte);
  - **o P0 com a chave é o instinto do mundo byte a byte** (2 donos × 3 lugares × 2 sementes);
  - **G1 do P1 com a chave:** rejogado do log, estado interno incluído; ele aprende e tenta classes fora do padrão;
  - **a conta exata** pela consequência; o dono não ensina o alvo;
  - a comida podre como classe própria, e as classes da etapa 3 já aceitas;
  - o motor usa a mesma função pura do alvo padrão (espião), e as falhas altas.
- **Fica para a etapa 3 do A na `main`:** as entradas sociais (visão e toque), o modelo dos outros (só registrado) e o gate "também com
  o outro à vista".

## V2, DOIS-PETS, etapa 2 — o `Grupo`: N pets de verdade no mesmo `Mundo` (2026-10-08, `docs/TAREFA_V2_DOIS_PETS.md`) — GATES PASSAM

A etapa 2 do motor da frente dos dois pets (desenho `docs/futuro/dois_pets.md`, seções 2 a 4; DP-1 a DP-3 e DP-7). Infraestrutura, sem
run; só as sementes dos testes. Mudaram `digilab/grupo.py` (novo), `digilab/mundo.py` (o `MotorMundo` aceita o `Mundo` do grupo e a
entrada, e o laço partido), `digilab/motor_corpo.py` (o `_um_tick`) e a `ConfigGrupo` no fim de `config.py`. `engine.py`, os cérebros, a
bancada e a web não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **`ConfigGrupo`** (`ligada` False; `CONFIG_GRUPO_LIGADA`): `ids` ("A", "B"; distintos, em ordem, no máximo dois) e `orcamento_por_dia`
  (16, por pet; DP-7). Desligada, o `Grupo` falha alto (`GrupoSemChave`): o `MotorMundo` de um pet continua dono do próprio `Mundo`.
- **As sementes (seção 2):** o mundo e o pet A usam a semente do grupo, s (o A sozinho é a vida de hoje de s); o B usa
  `derivar_semente("segundo-pet", s)` (`sementes_do_grupo`). Os fluxos de cada pet (`alvo`, `mundo-sujeira`, `dono`, `dono-lugar`) saem
  da semente dele.
- **O `Grupo`** (`Grupo(cfg_mundo, semente)`): um `Mundo` e os motores dos pets presentes, num relógio só (`Grupo.tick`, o do mundo). Não
  decide nada.
  - **`entrar(id, politica, fabrica_motor, cerebro, dono)`:** só num início de dia do mundo. A fábrica recebe `mundo=` e `entrada_mundo=`,
    e o motor é conferido (o `Mundo` do grupo, a semente, a entrada, o mesmo `efeito_frutas` dos outros, recém-nascido).
  - **`avancar(n)`:** um evento de avanço do grupo; cada pet presente ganha o avanço no próprio log e os ticks andam intercalados. Em cada
    tick, os pets que decidem agem na ordem sorteada e depois os outros andam o tick deles.
  - **A vez (DP-2):** com dois ou mais pets decidindo no mesmo tick, um sorteio no fluxo `mundo-ordem` (`derivar_semente("mundo-ordem",
    s)`), sobre a lista ordenada pelo id: o `random.shuffle` do CPython escrito com `randrange`. O primeiro age inteiro, e o segundo
    percebe o mundo como ficou. Com um pet só não há sorteio, e o fluxo nem é criado. As vezes ficam em `Grupo.ordens` (derivadas).
  - **O dono:** `acao_dono`, `deixar_comida` e `deixar_bola` por pet (o orçamento e o contato são do pet). O `PetNoGrupo` é a porta do
    `CanalMundo` para um pet.
- **O laço partido:** o `_avancar(n)` da cadeia do `MotorMundo` virou três partes, `_abrir_avanco` (o índice do evento do
  `MotorPersonalidade`), `_um_tick` n vezes (o laço do engine, ou o `_laco(1)` do `MotorCorpo`) e `_fechar_avanco` (a morte conferida do
  `MotorEducacao`). Um teste confere a MRO de `_avancar`, para uma classe nova na cadeia não passar despercebida.
- **A entrada depois do tick 0** (o A vive K dias antes do B; "B só" e "B + Aing" do plano): o relógio do pet (o `Estado`, o log, o
  corpo e a Vida) começa em 0 na entrada, com `MotorMundo.entrada_mundo` = o tick do mundo. O `Mundo` e os registros do mundo físico do
  pet (consumos, decisões, regiões, visitas, comidas deixadas) usam o relógio do mundo. A hora do dia é a mesma nos dois. O mundo pode
  passar dias sem pet: o `Grupo` só anda o relógio, e as quedas desses dias saem na primeira decisão (a atualização idempotente da etapa 1).
- **O registro do grupo (DP-3, `RegistroGrupo`):**
  - JSONL com o cabeçalho na primeira linha: a versão, a semente, os ids, o layout e, por pet, a semente, a entrada e os rótulos do
    cérebro e do dono;
  - os eventos no relógio do mundo, cada um com o `destino` (`grupo` para a entrada e o avanço; `mundo` para deixar a comida e a bola;
    `pet:<id>` para as ações do dono), o `pet` (o do orçamento e do contato) e a `origem` (`dono`; `dono:<id>` na etapa 7);
  - um avanço só, do grupo; o que os pets fazem não entra (sai do replay);
  - `projecao(id)` é o log de hoje do pet, no relógio dele, igual ao log do motor (conferido).
- **`reproduzir_grupo(registro, fabricas, cfg_mundo)`:** refaz o grupo do cabeçalho e rejoga os eventos no mesmo relógio, com o mesmo
  sorteio. Falha alto com evento desconhecido, fora do tick, de pet que não entrou, com o cabeçalho de outra config ou com um registro
  refeito diferente do lido.
- **`simular_grupo(cfg_mundo, s, pets, dias)`** (DP-7, a validação inicial): o `simular_vida_mundo` do grupo. A cada passo do dono o grupo
  anda o passo; depois, para cada pet presente na ordem dos ids, o dono decide pelo que vê daquele pet, com o orçamento dele (16 por dia
  vivido) e a rng `dono` dele (`derivar_semente("dono", semente do pet, rótulo)`). Os pets (`PetDoGrupo`) entram no começo de um passo.
  `dono=None` é o pet sem dono (o parceiro passivo dos testes).
- **Gates** (`tests/test_grupo.py`, 35 testes, ~17 s):
  - **G2 com um pet no grupo:** as 48 vidas diretas de `dois_pets_vidas_de_hoje.json` (o corpo inteiro da etapa 6 incluído) e o
    `simular_vida_mundo` de hoje com os quatro donos, os três lugares, os dois cérebros e as duas sementes, byte a byte; o canal dos
    gestos (o tapa e o carinho) também; nenhum sorteio com um pet; o grupo desligado recusa;
  - **G1-GRUPO:** o replay do texto do registro refaz o grupo bit a bit (os pets, o mundo, as vezes e a rng da ordem), com o B entrando no
    dia 0, 1 e 2, com o corpo e nos dois layouts; a projeção é o log de cada motor; e o replay falha alto com o registro errado;
  - **G-ORDEM:** a ordem da lista dos pets e a ordem de entrada no código não mudam o grupo; o sorteio é o `random.shuffle` do CPython; um
    sorteio só nos ticks com os dois pets decidindo;
  - **G-NUMS-GRUPO:** um B passivo (só ocioso e dormir, sem dono) deixa o A e o mundo iguais aos do A sozinho; com um B que age (instinto,
    lobos ou passivo), as quedas e as vezes sorteadas são as mesmas, e o rastro do A (decisões, consumos, regiões) é o do A sozinho até o
    primeiro evento físico do B (ele come, brinca com a bola, ou o dono dele deixa algo), e muda depois;
  - **a entrada tardia:** o relógio do B, a hora do dia, os registros no relógio do mundo e o orçamento por dia vivido; "B só" e "B + Aing"
    com as quedas do grupo com o A;
  - **a guarda da MRO** do `_avancar`.
- **Fora:** a visão, o toque e a disputa entre os pets são a etapa 3 (o PR seguinte); nesta etapa um pet só muda o mundo do outro pelo
  que faz fisicamente. A troca do `efeito_frutas` no dia K ("B + Aemb") e o efeito por tipo de árvore são da etapa 5 (o D): hoje o grupo
  exige o mesmo `efeito_frutas` em todos os pets. O `mundo.ts` não mudou (etapa 9).

## V2, BANHEIRO, etapa 3 — o banheiro no mapa, a necessidade, o limpador, o `limpar` e o `DonoCarinhoBanheiro` (2026-10-08, `docs/TAREFA_V2_BANHEIRO.md`) — GATES PASSAM

Seções 2 a 5 e 8 da tarefa, o lado do motor (A). Infraestrutura, sem run; só as sementes dos testes. Mudaram `digilab/mundo.py`,
`digilab/motor_corpo.py`, a `ConfigBanheiro` (a área), o registro `PARAMETROS_BANHEIRO` e uma linha de `digilab/donos.py`. `engine.py`,
`corpo.py`, os cérebros, a bancada e a web não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **A chave:** `MotorMundo(..., cfg_banheiro=ConfigBanheiro)`, só com o mundo ligado e com o corpo com a sub-chave `banheiro` na frente
  (`com_corpo(MotorMundo)`); o corpo com a sub-chave exige o banheiro no mapa. Falta de uma das duas falha alto (`BanheiroSemMundo`).
  Desligada, nada muda: nenhuma rng, nenhum registro, nenhuma chave em `estado()`, nada no resumo do `Mundo`.
- **O banheiro:** um retângulo de células da casa, `ConfigBanheiro.celulas_x` (0 a 3) e `celulas_y` (0 a 5), PROPOSTOS; funções puras
  `faixa_do_banheiro`, `no_banheiro`, `ponto_do_banheiro` e `zona_da_necessidade` (o banheiro é uma zona própria, `ZONA_BANHEIRO`).
- **O `aliviar` com alvo:** o motor sorteia o u da rng `alvo` e oferece `banheiro` (o ponto mais perto) e `aqui`; sem o gancho do cérebro,
  `aqui`. O pet anda até o alvo (o alcance e o custo de energia de sempre) e alivia onde parou (chegou tarde). Urgente (a vontade da
  observação acima de `limiar_urgente`) com o alvo `banheiro` falha alto.
- **A necessidade** é um objeto do `Mundo` (contador próprio; fora dos `vistos`). O limpador a recolhe na hora dentro do banheiro; fora,
  ela fica. O `limpar` do dono recolhe as da zona do pet.
- **No corpo** (`MotorCorpo`): o aliviar vira `estimulo_aliviar` e, quando a necessidade fica, `estimulo_necessidade`, depois do andar; a
  cada tick, `passo(..., necessidades=n)` com as necessidades na zona do pet (`MotorMundo.necessidades_na_zona`).
- **Os registros:** `motor.alivios` no contrato da bancada (`tick` do mundo, `dentro`, `urgente`, `alvo`, `distancia` ao banheiro na
  decisão, `recolhido`), `motor.recolhas` (o limpar) e `Mundo.recolhidas`; `estado()["banheiro"]` (alívios, dentro, necessidades no chão,
  na zona) e o resumo do mundo físico, só com a chave.
- **`DonoCarinhoBanheiro`:** um `acariciar` no primeiro passo do dono depois de cada alívio dentro do banheiro, fora do orçamento, por
  `simular_vida_mundo(..., carinho=)`. O dono sintético não julga o `aliviar` (`julgar_acao` devolve 0).
- **Gates** (`tests/test_banheiro_mundo.py`, 30 testes, ~6 s):
  - **G2:** a chave explícita desligada é a vida de hoje; os gabaritos de sempre (banheiro, dois pets, corpo no mundo, mundo) na suíte;
  - **as chaves** vão juntas e falham alto;
  - **G-MEC:** a vontade a zero e o cheiro; o limpador só no banheiro; o desconforto pela zona (o banheiro à parte, até 3); o `limpar` da
    zona; o urgente alivia aqui; o alvo `banheiro` leva o pet até lá ou alivia no caminho; sem gancho, `aqui`;
  - **G-CONS:** com o limpador, o sinal pelo corpo do aliviar dentro é maior que fora; sem ele, igual;
  - **G-CRED:** cada carinho no passo seguinte a um alívio dentro, creditado à decisão de aliviar, fora do orçamento;
  - **G1:** o replay bit a bit com o instinto e com os lobos aprendendo (P1), com e sem o limpador, com o carinho, nos dois layouts, e no
    grupo de dois pets (as necessidades são do mundo de todos);
  - as quedas iguais com e sem o banheiro; os `alivios` no contrato da bancada (`medidas_banheiro_de`).
- **Achado (fumaça descritiva, sementes dos testes):** com o banheiro nas células 0 a 3 e 0 a 5, o pet alivia a 185–260 subunidades dele
  (mediana) e o alcance de uma decisão é 60: em 5 vidas de 7 dias, 1 alívio dentro no P0 e 0 no P1 (que escolheu o `banheiro` 12 vezes).
  O 2 × 2 do plano quase não teria carinho nem limpador para medir. Fica para o Matheus e o plano.
- **Para o D (destravar `NOS_PENDENTES["banheiro"]`):** a fábrica dos braços do banheiro é o `com_corpo(MotorMundo)` com o `cfg_corpo_de`
  e o `cfg_banheiro_de` que a bancada já monta; o `simular_vida_fisico` passa `carinho=DonoCarinhoBanheiro()` nos braços com carinho
  (B0C, BLC) depois das ações do dono do passo; o `medidas_banheiro` já lê o `motor.alivios` deste contrato.

## V2, REDE-DE-SI, etapas 0, 1 e 2 — o automodelo em observação (2026-10-08, `docs/TAREFA_V2_REDE_DE_SI.md`) — GATES PASSAM

Etapa 2 do ego (`docs/futuro/ego_existencia.md`), com RS-1 a RS-7 pela recomendação. Infraestrutura, sem run de pesquisa; só as sementes dos
testes. Mudaram `digilab/rede_de_si.py` (novo) e a `ConfigRedeDeSi` no fim de `config.py`. `engine.py`, o `AcaoPet`, o cérebro, o corpo,
o motor, a bancada e a web não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **A regra de quem aprende (E-6, RS-7):** a Decisão aprende por reforço, a rede de si por erro de previsão, e nenhuma outra peça aprende.
  A regra antiga ("só a Decisão aprende") fica revista por esta.
- **Etapa 0, num commit próprio, antes da rede:** `tests/gabarito_rede_de_si.py` → `tests/gabaritos/rede_de_si_vidas_de_hoje.json`, 40
  vidas: o P1-c, o P0-c e o P1-c-tapa na bola; o P1-c e o P1+ped (ainda sem o corpo) no `iguais_frutas`; montagens simples e completa
  (T3); o atencioso e o aleatório; sementes 101 e 202.
- **A rede (`RedeDeSi`, etapa 1):**
  - **as entradas:** só os receptores da `PercepcaoCorpo` (todos os presentes, na ordem dos campos), a ação escolhida, o contexto da
    observação (a bola, a comida boa e o pedido vigente, 0 ou S, também pelos `vistos` do mundo físico) e a idade em faixas pelas decisões
    vividas (limites 96, 288 e 672). Nada de químico, `Estado`, pesos do cérebro, regra do instinto ou sonda;
  - **a cabeça do corpo:** por horizonte (1, 4 e 16 decisões, RS-1) e receptor, `corte(div_arred(Σ w x, S), 0, S)`. O prior é a
    persistência (RS-2). O LMS em inteiros chega quando a leitura real chega, cortado em w0 ± teto;
  - **a cabeça da autoria:** por ação, a mesma forma, com o alvo um-quente da ação escolhida, aprendido na hora. O prior é uniforme
    (S / 8). As contrafactuais "sem o pedido" (pedido = 0) e "ao nascer" (a primeira faixa) são a mesma conta;
  - **o erro exposto (E-11, sem leitor):** por receptor e horizonte, o erro absoluto recente (uma média em inteiros) e a surpresa;
  - **os registros:** por decisão, as leituras, as previsões, a autoria e as duas contrafactuais, e a surpresa (para a bancada, etapa 3);
  - **os números:** `passo` S/16, `teto` 4 S, `fator_erro` S/16 (PROPOSTOS; registro `rede_de_si.PARAMETROS_REDE_DE_SI`). **804 pesos** com
    o corpo da bola e das frutas (10 receptores) e 911 com a curiosidade do mundo físico. Com o banheiro no mundo físico (13 receptores),
    passa de mil e falha alto.
- **O embrulho (`PoliticaComRede`, etapa 2):** entrega à rede a observação e a ação depois que o cérebro escolheu, e repassa todo o resto
  ao cérebro por `__getattr__` (o que existe nele existe no embrulho, e o que não existe também não).
- **Gates** (`tests/test_rede_de_si.py`, 61):
  - **G-INT:** pela AST, nenhuma constante float, nenhuma divisão `/`, nenhum `math`, `random`, `float` ou `round`;
  - **G-PESOS:** a contagem e o teto que falha alto;
  - **a conta exata** de um passo do LMS (corpo e autoria); **com `passo` 0, a persistência para sempre**;
  - as contrafactuais e o erro exposto em contas exatas; o contexto do mundo físico e das frutas;
  - **G-OBS:** as 32 vidas com corpo da etapa 0 saem byte a byte com a rede observando (log, estado, `estado()`, ações, rngs, registro do
    mundo e o estado interno do cérebro); as 8 sem corpo falham alto;
  - **G-RECEPTOR:** a rede só importa `config` e `events`; um químico sem receptor (o `alimento`, a `vida`) não muda a percepção; o
    `Estado`, o relógio do cuidado e a informação do dono não mudam a rede;
  - **G1-REDE:** o replay refaz o estado da rede bit a bit.
- **Fica para a etapa 3 (D):** a chave `rede_de_si` da bancada, a rede congelada e o oráculo por replay, os braços P1-c-lenta e P1+ped-c, as
  medidas e as faixas. A troca da digestão (2b) é do A.

## V2, DOIS-PETS, etapa 3 — visão, toque e disputa, o degrau 1 (2026-10-08, `docs/TAREFA_V2_DOIS_PETS.md`) — GATES PASSAM

A etapa 3 do motor dos dois pets (desenho `docs/futuro/dois_pets.md`, seções 3, 5 e 6; DP-4 e DP-11). Infraestrutura, sem run; só as
sementes dos testes. Mudaram `digilab/mundo.py`, `digilab/grupo.py`, o campo `Observacao.social` em `digilab/policy.py`, a
`ConfigGrupo.raio_toque_celulas`, uma linha de `digilab/motor_corpo.py` (o `obs.social` na observação do gesto) e o G-NUMS-GRUPO de
`tests/test_grupo.py`. `engine.py`, o `AcaoPet`, os cérebros, a bancada e a web não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **`Observacao.social`** (padrão None): a `PercepcaoSocial` (`mundo.py`), que o `MotorMundo` injeta só dentro de um `Grupo` com outro pet
  presente. Sem o grupo, ou sozinho nele, fica None, e a vida é a de hoje. Os três campos, só com o que é físico:
  - `outros`: `(id, dx, dy, d, acao_visivel)` dos pets no raio da visão do mundo, em ordem de d e de id. A ação visível é a da última
    decisão do outro (a deste tick, se ele veio antes na vez);
  - `onde_comeu`: `(id, x, y, idade)` do último ponto em que este pet **viu** cada outro comer (o comedor dentro do raio, no momento do
    consumo), com a idade em ticks;
  - `toque`: `(id, tipo, direcao, idade)` do último contato com cada outro.
- **A visão e o toque são do grupo** (`Grupo.perceber_social`, `Grupo.viu_comer`), por funções puras do `mundo.py` (`perceber_social`,
  `em_contato`, `direcao_vizinha`, `tipos_do_contato`) que só recebem posição, ação visível, consumo visto e contato. Nunca o estado
  interno do outro.
- **O toque (5.2):** no fim de cada tick com decisão, com dois pets ou mais, depois da vez sorteada: contato com as células a até
  `raio_toque_celulas` (1) em Chebyshev, um por par e por tick. O tipo sai do que aconteceu: `disputa_ganhou`/`disputa_perdeu`, depois
  `encostou`/`encostaram` (quem seguiu o outro neste tick), depois `esbarrou`. A direção é a da tabela do cheiro (1 a 8), 0 na mesma
  célula. O toque não mexe no corpo (degrau 3).
- **A disputa:** a comida que um comeu neste tick e que o outro tinha como alvo neste tick, ou trazia da decisão anterior. O primeiro na
  vez come; o segundo não acha (o alvo some, e o comer sem comida não dá fome, MF-2). Fica registrada com ou sem contato.
- **Os candidatos do explorar** (seção 6), depois dos de hoje: `seguir` (onde está cada outro visto) e `onde_comeu` (cada ponto da
  memória do consumo visto). O padrão do motor e o instinto nunca os escolhem; o `continuar` deles leva ao ponto antigo.
- **Os registros** (derivados; o replay refaz; no `Grupo.resumo`, que o G1 compara):
  - no grupo: `contatos` (os tipos, as direções e as células) e `disputas` (o vencedor, se ele veio primeiro na vez, a distância de cada
    um à comida, se o perdedor decidiu no tick e se houve contato);
  - em cada motor (`resumo_social`): os consumos vistos (`vistos_comer`), as idas a `onde_comeu` (chegou, comeu, comidas boas à vista na
    chegada), o tempo à vista (`a_vista`, decisões com cada outro visto) e as decisões no grupo.
- **Gates** (`tests/test_grupo_social.py`, 27 testes, ~3 s):
  - **G-RECEPTOR-SOCIAL:** a `PercepcaoSocial` só tem os três campos, com números e nomes; nenhum cérebro importa o grupo, o engine ou um
    motor (só as funções puras do mundo); mudar a fome, o humor, os pesos, a memória e o toque do B, no mesmo lugar e fazendo o mesmo, não
    muda o que o A percebe, e mudar a posição ou a ação muda;
  - **G-SENTIDOS (visão e toque):**
    - o toque nos casos da seção 5.2 (disputa, encostar, esbarrar), o contato na mesma célula ou na vizinha e nenhum a duas células,
      também numa vida tick a tick, e a direção;
    - a visão só no raio, em ordem, com a ação da última decisão do outro, conferida decisão a decisão pela vez sorteada;
    - o consumo visto só com o comedor no raio, no momento;
  - **G-MEC-SOCIAL:**
    - a disputa em 4 sementes: o primeiro na vez come, e o outro não come e não acha;
    - o `onde_comeu` só depois de um consumo visto, no ponto da memória;
    - os candidatos sociais só no explorar, o `seguir` só com o outro visto e no lugar dele, depois dos de hoje;
    - o padrão do motor nunca os escolhe;
    - as idas e o tempo à vista registrados;
  - **G2:** sem o grupo, ou com um pet só nele, o `obs.social` é None e não há candidato a mais; com o B entrando no dia 1, o A só tem a
    percepção social depois disso. Os gabaritos de sempre passam na suíte (o grupo com um pet, as 276 vidas da etapa 0, o mundo e o
    corpo);
  - **G1-GRUPO com os sentidos:** o replay do registro refaz o grupo bit a bit (contatos, disputas e registros sociais incluídos), com os
    cérebros que seguem, que vão onde viram comer, que comem tudo, e com os lobos do alvo aprendido;
  - **os lobos no grupo:** com o alvo aprendido (#255), eles escolhem o `seguir`; no prior, o P0 com lobos é o instinto do mundo byte a
    byte, com os dois pets se vendo e se tocando.
- **O G-NUMS-GRUPO da etapa 2:** com um B passivo, a vida do A segue igual à do A sozinho. Os lobos agora anotam no motivo o candidato
  `seguir` a mais (o A vê o B); o teste confere o estado interno sem essa anotação.
- **Fora:** a audição e o cheiro (o degrau 1b, etapa 8); as entradas sociais e o modelo dos outros no cérebro A (a segunda metade da
  etapa 4, o B); a bancada do grupo (etapa 5, o D); o grupo em TypeScript (etapa 9).

## V2, W-BANCADA-DOIS-PETS — as faixas da rede de si, a bancada do grupo e o banheiro destravado (2026-10-08, `docs/TAREFA_V2_DOIS_PETS.md`, etapa 5) — GATES PASSAM

Rodada 26, com o `Grupo` do #257, o alvo aprendido do #255, a etapa 3 dos dois pets (#263: visão, toque e disputa) e a etapa 3 do banheiro
(#265) na `main`. Infraestrutura, sem run de pesquisa; só as sementes dos testes. Mudaram `experiments/bancada_v2.py`, `digilab/metrics.py`
(`vez_no_grupo`), a fumaça nova `experiments/configs/v2_dois_pets/fumaca.json`, os testes do banheiro e do `NOS_PENDENTES` e o teste novo.
`engine.py`, `grupo.py`, `mundo.py`, `lobos.py` e a web não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **As faixas da rede de si (RS-6)** em `FAIXAS_RESERVADAS`, com a fonte (`PLANO_ANALISE_V2_REDE_DE_SI`, seção 8): 43101…43505
  (calibração e piloto) e 44101…44505 (validação). O prefixo `"rede_de_si"` entrou em `PREFIXOS_UNIDADES` (o plano o pede ao D).
- **O banheiro destravado** (o nó `banheiro` saiu, com o #265): a fábrica dos braços do banheiro é o `com_corpo(MotorMundo)` com o
  `cfg_banheiro_de`; nos braços com carinho (B0C, BLC) o `simular_vida_fisico` passa o `DonoCarinhoBanheiro`, fora do orçamento
  (`VidaBancada.carinhos`); o `medidas_banheiro` lê o `motor.alivios` do #265 (no cérebro `instinto`, sem os pesos do alvo).
- **O mundo da unidade** (plano, seções 2 e 3): `tipo_ruim(s)` (uniforme, rng `dois-pets-ruim`), `efeito_dois_pets` (o ruim com o
  `efeito_humor_ruim`, os outros neutros) e `desarranjo_dois_pets(s)` (rng `dois-pets-embaralha`, como o `desarranjo_n6`).
- **O A embaralhado** é o `MotorMundoTroca` (subclasse do `MotorMundo`, só no grupo): o efeito desarranjado nos K dias e o verdadeiro a
  partir do dia K, trocado no fim do avanço que chega ao tick (um avanço que passasse falha alto). A troca fica em `troca`, e o replay a
  refaz.
- **Os braços** (`BRACOS_GRUPO`, `EspecGrupo`): `B-so`, `B+Ainf`, `B+Aemb`, `B+Aing` e o `A-so` da calibração do K. O B é sempre P1 e entra no
  dia K; o A é P1 no tick 0 (informativo, embaralhado) ou P0 junto com o B (ingênuo). O grupo vive K + `dias` (o `A-so`, os `dias`). Sem
  genoma (temperamento neutro).
- **A fábrica do grupo** (`Bancada.grupo`): o `simular_grupo`, com um dono para todos (o atencioso, `DonoComLugar`, com a semente de cada
  pet), o orçamento por dia vivido de cada pet e só o cuidado (o `CanalSemEnsino` ao vivo, PMF-3). O cérebro é o da bancada com o **alvo
  aprendido** (`bancada_grupo`). O G1 é conferido em todo grupo (`conferir_replay_grupo`).
- **As medidas** (`Bancada.medir_grupo`, do replay de medição conferido):
  - a R de cada pet pela `taxa_fruta_ruim` (fruta madura, efeito vigente do tipo no tick): no B, os 7 primeiros dias, a vida toda e por
    dia; no A, por dia, até o dia K e depois;
  - o D_FE e a privação; os pesos do alvo aprendido no fim de cada dia; a vez no tick (R-5); o chão no dia K (R-3);
  - **as sociais** (`Bancada.medidas_sociais`, dos registros do #263): o uso do `seguir` e do `onde_comeu` por dia, o que o pet viu comer
    (por tipo, e quantos do tipo ruim), a disputa (quantas, quantas ganhou, as distâncias), o toque por tipo e dia, o tempo à vista e as
    idas a `onde_comeu`.
- **Atrás de `NOS_PENDENTES`, falhando alto:**
  - `cerebro_social` (as entradas sociais e o modelo dos outros, a segunda metade da etapa 4, do B): trava o modelo dos outros
    (`Bancada.modelo_dos_outros`) e a run com as sementes do plano (`validar_config_grupo`), porque o cérebro do plano os tem;
  - `canais_fruta_mundo`: com os canais (a montagem completa liga no P1), comer a fruta que mexe no humor falha alto no cérebro do mundo
    físico (CANAIS-REFORCO, a "rota de adendo" do MUNDO-CEREBROS). Trava a config e o grupo; sem a tabela o cérebro falha (teste: o `A-so`
    na semente 505). Fica até o Matheus decidir.
- **Gates:**
  - `tests/test_bancada_dois_pets.py` (56): as faixas e o prefixo; o mundo da unidade e os braços; o G1 de todo grupo; **o pet sozinho do
    grupo é a vida de hoje** da bancada byte a byte; as mesmas vezes sorteadas nos braços com dois pets; as mesmas quedas; o chão do dia K;
    a troca; o orçamento e o cuidado só; o alvo aprendido; as medidas, e as sociais conferidas contra os registros (com uma disputa, no
    B + Aing semente 303); os nós e as travas; a config e o `rodar_grupo`;
  - `tests/test_bancada_banheiro.py`: os oito braços do banheiro rodam e medem (com o banheiro maior só no teste, para haver alívio dentro:
    o carinho só no B0C e no BLC, o limpador só no BL0 e no BLC, o orçamento, as medidas), e o instinto do alívio mede sem os pesos.
- **Fumaça** (`experiments/configs/v2_dois_pets/fumaca.json`, NÃO canônica): os cinco braços do grupo, K = 1, 2 dias; sem artefato.

## V2, DOIS-PETS, etapa 4, segunda metade — as entradas sociais e o modelo dos outros no cérebro A (2026-10-08, `docs/TAREFA_V2_DOIS_PETS.md`) — GATES PASSAM

A parte da etapa 4 que dependia da percepção social do #263 (`docs/futuro/dois_pets.md`, seção 8, DP-8). Infraestrutura, sem run; só as
sementes dos testes. Mudaram `digilab/policies/lobos.py` (atrás das chaves), a `ConfigLobos` e uma checagem em `digilab/motivo.py`.
`engine.py`, o mundo, o grupo, o corpo, a bancada e a web não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **As chaves** (`ConfigLobos`, PROPOSTAS; registro `lobos.PARAMETROS_LOBOS_DOIS_PETS`): `entradas_sociais` e `modelo_outros` (desligadas,
  só no mundo físico; fora dele falham alto), `janela_social_ticks` (240, o "recente") e `fator_familiaridade` (S/64).
- **As entradas sociais** (`lobos.ENTRADAS_SOCIAIS`, `lobos.entradas_sociais`), 15, todas 0 ou 1, só do que `Observacao.social` traz:
  - `outro_a_vista`;
  - `viu_comer`: viu algum outro comer há no máximo a janela;
  - `acao_<a>`: a ação visível do outro mais perto, um-quente sobre as 8 do `AcaoPet`;
  - `toque_<tipo>`: o tipo do último contato na janela, um-quente sobre os 5 tipos (`mundo.TIPOS_TOQUE`, conferido na carga).
  - Sem o grupo, ou sozinho nele, todas 0.
- **No cérebro:** nas regras de tempo livre (`tempo_livre`, `bola_no_cenario`, `fruta_no_cenario`), um peso por (regra, ação, entrada),
  **prior 0**, só nas ações que o instinto propõe em cada regra (4, 4 e 5): um candidato fora delas falha alto. O termo vai ao lobo de
  decisão; aprende pela regra da L1, com o canal do corpo, de toda fonte que ensina a tabela da regra. O outro pet não manda sinal.
- **Os pesos (PDP-1, o degrau 1 sem o corpo):** 951 com as entradas sociais e **987 com o alvo aprendido**. Com o corpo dos drives novos
  passa de mil e falha alto.
- **O modelo dos outros** (`lobos.ModeloOutros`), **só registrado** (`estado_interno()["modelo_outros"]`), por pet conhecido:
  - **familiaridade:** a média móvel do outro à vista, em inteiros, a cada decisão;
  - **confiança na comida:** as idas a `onde_comeu` dele que chegaram e, delas, as que acharam comida boa (comeu, ou comida boa à vista
    na chegada);
  - **afinidade:** `divididas` (o pet comeu e viu o outro comer no mesmo intervalo entre decisões, sem disputa) e `perdidas` (cada toque
    novo de `disputa_perdeu`), com o saldo. Confiança e afinidade nunca se somam, e nada tem rótulo.
  - Os eventos são identificados pelo tick no relógio do pet (a hora do dia, como o do N6) menos a idade: o mesmo evento conta uma vez.
- **O motivo:** um termo social aprendido que pese na decisão faz o `motivo_lobos` falhar alto, como as entradas do corpo (sem fator na
  expressão).
- **Gates** (`tests/test_entradas_sociais.py`, 29):
  - **G2:** com as chaves e um pet só no grupo, a vida de hoje (o resumo do grupo e os pesos de sempre); os sociais ficam em zero;
  - **no prior, o P0 com lobos (alvo aprendido e as duas chaves) é o instinto do mundo byte a byte, com o outro à vista** (sementes 101 e
    202);
  - **G1:** o replay do registro do grupo refaz os dois cérebros bit a bit, com o B entrando no dia 0 e no dia 1;
  - **a conta exata:** o termo no peso efetivo e um passo da regra nos pesos sociais;
  - **o modelo dos outros não muda a decisão:** a vida com ele e sem ele é a mesma (3 sementes); pela AST, só o `agir` (antes de decidir),
    o `consequencia_mundo` e a serialização o tocam;
  - **as contas do modelo:** em casos montados e numa vida, onde as idas e os acertos batem com o registro do motor (`idas_onde_comeu`) e a
    familiaridade é refeita da percepção.
- **Fica para depois:** a bancada do grupo (etapa 5, D), que tem de repassar o `consequencia_mundo` ao cérebro para o modelo contar as
  idas; a audição e o cheiro como entradas (etapa 8); o modelo decidindo (degrau 3).

## V2, W-BANCADA-MODELO — as entradas sociais e o modelo dos outros na bancada do grupo (2026-10-11, `docs/TAREFA_V2_DOIS_PETS.md`, etapa 5) — GATES PASSAM

Rodada 27, com o #266 (as entradas sociais e o modelo dos outros no cérebro A, do B) na `main`. Infraestrutura, sem run de pesquisa; só as
sementes dos testes. Mudaram `experiments/bancada_v2.py`, o teste do grupo e o do `NOS_PENDENTES`. `engine.py`, `grupo.py`, `mundo.py`,
`lobos.py`, `metrics.py` e a web não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **O repasse do `consequencia_mundo`:** a `PoliticaDoBraco` o repassa explicitamente ao cérebro, em toda fonte (o P0 também). O cérebro
  anota o motivo e o modelo dos outros conta as idas a `onde_comeu` e o que o pet comeu; só na fonte consequência há sinal pendente para
  creditar. O cérebro sem o gancho (o instinto do mundo) não recebe nada. Antes o repasse já acontecia pelo `__getattr__`; agora é um
  método da classe, testado.
- **O cérebro do grupo** (`Bancada.bancada_grupo`): o da bancada com o alvo aprendido, as `entradas_sociais` e o `modelo_outros` (#266). No
  prior, o P0 é o instinto do mundo byte a byte, também com o outro à vista.
- **O nó `cerebro_social` saiu.** Fica só o `canais_fruta_mundo` (a rota do humor no cérebro, do B; o Matheus decidiu manter a montagem
  completa).
- **A run do plano** (`validar_config_grupo`, sementes fora das dos testes) agora pede a montagem completa (o cérebro da seção 2), e por isso
  falha alto com o nó dos canais até o PR do B.
- **As medidas do modelo** (plano, seção 4: a familiaridade, a confiança por atividade e a afinidade, só registradas):
  - `Bancada.modelo_dos_outros(vida)`: o modelo no fim da vida, por pet, como o cérebro o serializa (um cérebro sem ele falha alto);
  - em cada pet do `medir_grupo`, `modelo_outros_por_dia`: o modelo no fim de cada dia vivido, pelo replay de medição.
- **Gates** (`tests/test_bancada_dois_pets.py`, 67):
  - o cérebro do grupo com as três chaves nos dois pets; o modelo de um pet sozinho não conhece ninguém;
  - **o modelo conta as idas e os acertos que o motor registra** (as idas a `onde_comeu` que chegaram, por outro), nos três braços com
    dois pets, em três sementes, inclusive no P0 do B + Aing;
  - o repasse explícito em toda fonte, e o cérebro sem o gancho;
  - **o modelo não muda a vida do grupo** (o registro e cada pet iguais sem ele, fora o modelo no estado interno);
  - o modelo por dia nas medidas, e o do último dia é o do fim;
  - a run do plano pede a montagem completa e falha alto com os canais; sem o nó, valida;
  - os gates de antes (o pet sozinho é a vida de hoje, as vezes, as quedas, a troca, o orçamento, as sociais).

## V2, CANAL-FRUTA-MUNDO — a rota do canal do humor no mundo físico (2026-10-11, decisão do Matheus) — GATES PASSAM

A falha que o D guardou no nó `canais_fruta_mundo` (o A só, semente 505): com os canais, comer a fruta que mexe no humor falhava alto no
cérebro do mundo físico, porque o canal do humor (a E2) vai aos pesos que leem a identidade da fruta e o cérebro do mundo não tinha nenhum.
Infraestrutura, sem run; só as sementes dos testes. Mudaram `digilab/policies/lobos.py` (atrás da chave) e a `ConfigLobos`. `engine.py`, o
mundo, o grupo, a bancada e a web não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **A chave:** `ConfigLobos.presenca_fruta_mundo` (desligada, PROPOSTA; só no mundo físico, fora dele falha alto).
- **A rota:** a decisão de comer lê a fruta madura à vista (`lobos.presenca_no_mundo`, pelos `vistos` da percepção do mundo; a podre não
  conta), um peso por fruta, **prior 0**, em toda regra em que comer é candidato. É a FRUTA-NO-CENARIO parte B no mundo físico, com os
  mesmos pesos (`pesos_comer_fruta`) e a mesma regra de aprendizado (`atualizar_comer_fruta`, só pela consequência). Pela `ROTA_CANAIS`, o
  canal do humor vai a eles; no escalar, o sinal inteiro, como no mundo das frutas.
- **Os pesos:** +3; o degrau 1 dos dois pets (o alvo aprendido e as entradas sociais) fica em **990**, abaixo de mil.
- **Um conserto no caminho:** o registro da decisão lia a presença de `obs.frutas_cenario` e passou a ler a mesma presença do peso efetivo
  (no mundo das frutas são o mesmo valor; nada muda lá).
- **Gates** (`tests/test_canal_fruta_mundo.py`, 10):
  - **G2:** a chave desligada é a vida de hoje (os gabaritos, na suíte); **com a chave e os canais no mundo `iguais`** (o humor da fruta é
    zero), **o P0 e o P1 da montagem completa saem byte a byte** iguais aos de sem a chave, com os pesos novos em zero e o pet comendo fruta;
  - **a conta exata:** a presença pela percepção; o termo no peso efetivo na `fruta_no_cenario` e na `fome_moderada`; um passo pelo canal do
    humor só na fruta presente, e o canal do corpo não mexe na presença;
  - **a falha real do D:** sem a chave, o A só da semente 505 falha alto (CANAIS-REFORCO); com ela roda (o G1 do grupo, conferido pela
    bancada), o peso do tipo ruim desce e os outros ficam em zero;
  - a contagem dos pesos e as falhas altas da chave.
- **Para o D:** destravar o nó `canais_fruta_mundo` é ligar a chave nos braços do mundo físico com os canais (a montagem completa), pela
  chave `"lobos"` da config ou na bancada do grupo.

## V2, BANHEIRO-CONTINUAR — a ida ao banheiro continua, e o `_tick_social` do aliviar no grupo (2026-10-11, decisão do Matheus) — GATES PASSAM

Pedido do Gerente depois do #265. Infraestrutura, sem run de pesquisa; só as sementes dos testes. Mudaram `digilab/mundo.py`,
`digilab/instinto_banheiro.py`, o G-MEC antigo de `tests/test_banheiro_mundo.py` e os testes novos. `engine.py`, os lobos, o corpo, a
bancada e a web não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **A continuação** (atrás da chave do banheiro):
  - com o alvo `banheiro` fora do alcance, o pet anda o alcance e segura a vontade: nada vai ao corpo além do andar, e não há necessidade
    nem registro em `alivios`;
  - o alvo fica pendente, como o `continuar`, e a percepção mostra `alvo_pendente` "banheiro" na decisão seguinte;
  - a ida segue se o cérebro escolher `aliviar` de novo; outra ação a desfaz, e com `aqui` o pet alivia onde está;
  - a regra urgente segue aliviando `aqui`, com ou sem a ida pendente;
  - o registro novo é `idas_banheiro`, no resumo do mundo físico. O `estado()` e o contrato dos `alivios` não mudam.
- **O instinto** escolhe `banheiro` sem sorteio com a ida pendente, fora da urgência. Não ganhou regra nova (os lobos rodam a sonda dele e
  não têm peso para outra tabela). **Os lobos não leem a ida:** sorteiam o alvo pelos pesos de sempre.
- **O `_tick_social` do aliviar no grupo:** o ramo do ALIVIAR passa a preenchê-lo como os outros ramos (o alvo do aliviar, sem `social` e
  sem `comeu`). Antes, a disputa e o toque do fim do tick liam o de uma decisão velha.
- **Gates** (`tests/test_banheiro_continuar.py`):
  - **G2:** a chave desligada é a vida de hoje (os gabaritos de sempre, na suíte). Com o banheiro ligado, as 34 vidas de
    `tests/gabaritos/banheiro_ligado_antes.json`, gravado com o código de antes (`tests/gabarito_banheiro_ligado.py`):
    - sem alívio no caminho, a vida inteira sai igual;
    - com um, tudo sai igual até a primeira decisão que aliviava no caminho, e nela o pet está no mesmo ponto, com o mesmo alvo, segurando;
    - no grupo, o corte é o primeiro desses ticks entre os dois pets;
  - **G-MEC:**
    - a ida de três decisões (60, 60, 17) alivia dentro só na chegada;
    - a vontade sobe enquanto o pet segura e zera ao aliviar;
    - `aqui` no meio alivia onde está; outra ação desfaz a ida;
    - a urgência alivia `aqui`;
    - ao alcance, nada muda;
  - **o instinto** segue a ida, e a urgência vence;
  - **G1:** o replay com a ida que continua (o instinto) e com os lobos aprendendo;
  - **o grupo:** todo pet que decidiu tem o `_tick_social` do tick, com o alvo do aliviar.
- **Fumaça descritiva** (a do #265, sementes 101…505, 7 dias, atencioso no comedouro, com o carinho):

  | braço | alívios dentro, antes → depois | idas que seguraram | continuações | como as idas acabaram |
  |---|---|---|---|---|
  | P0 (instinto) | 1 → 0 | 6 | 1 | 5 trocaram de ação (4 comeram, 1 ficou ociosa) |
  | P1 (lobos, T3) | 0 → 0 | 2 | 0 | 1 trocou de ação, 1 aliviou `aqui` |

  A continuação sozinha não leva o pet ao banheiro: no meio da ida ele quase sempre come a fruta à vista. O P1 também passou a escolher o
  banheiro menos (12 alívios com esse alvo antes, 2 idas agora).

## V2, METABOLISMO, etapas 0 e 1 — o combustível e a reserva por baixo do cansaço (2026-10-11, `docs/TAREFA_V2_METABOLISMO.md`) — GATES PASSAM

As ME-1 a ME-7 pela recomendação (decisão do Matheus, 2026-10-11). Infraestrutura, sem run; só as sementes dos testes. Mudaram
`digilab/corpo.py`, `digilab/corpo_grafo.py`, a `ConfigCorpo` (a sub-chave e os números no fim), uma linha de `digilab/motor_corpo.py`, o
exportador e o gabarito da paridade do corpo e o espelho dos números em `web/app/motor/constantes.ts`. `engine.py`, o `AcaoPet`, o mundo, os
cérebros (sem receptor novo, ME-2) e a bancada não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **Etapa 0, num commit próprio, antes de mudar o código:** `tests/gabarito_metabolismo.py` → `tests/gabaritos/metabolismo_vidas_de_hoje.json`,
  176 vidas: o bloco do corpo pela bancada (P0-q, P1-q, P0-c, P1-c, P1-c-tapa e P1-cw nos mundos `padrao`, `bola` e `iguais_frutas`), o
  `fisico` (o P1-quimica e o 2 × 2 do banheiro) e as vidas diretas da etapa 6 do gabarito do banheiro.
- **A sub-chave:** `ConfigCorpo.metabolismo` (exige a `digestao`; `CONFIG_CORPO_METABOLISMO` = a etapa 6 com ela). Desligada, a vida de hoje.
- **Os químicos** `combustivel` (C/2 ao nascer) e `reserva` (C/4), concentrações com teto C, **sem receptor**:
  - **a conversão:** a reação `digestao` produz combustível, `conversao_num/conversao_den` (1/1) do que digeriu, com o resto guardado como
    a vontade; o que passa do teto é descartado e contado;
  - **o gasto basal:** 375 por tick acordado e 187 dormindo (fase 1);
  - **as atividades:** o brincar do pet e o do dono, o explorar e o andar tiram do combustível o mesmo número que somam ao cansaço (ME-3);
    o cansaço de hoje não muda;
  - **o armazenamento** (acima de 3C/4) **e a mobilização** (abaixo de C/2), até 375 por tick: transferências 1 por 1, depois da fase 1 e
    antes da fase 2;
  - **a falta:** abaixo de C/4 o cansaço sobe 500 por tick (fase 2). É a única ponte para o pet (ME-1).
  - A fome não lê o combustível (ME-5); o excedente do estômago segue descartado (ME-4).
  - `Corpo.contas_metabolismo` guarda o que entrou e saiu, em totais.
- **O grafo:** a `Reacao` ganhou `fracoes` (a produção com fração e resto, a vontade e o combustível), e a reação com limiar (`le`, `lado`,
  `limiar`: uma transferência 1 por 1). O gatilho novo `abaixo` é o espelho do `acima`. Duas checagens a mais, que só mordem nas
  transferências:
  - **2b:** todo químico que elas tocam chega a um sumidouro de verdade (nem o teto nem outra transferência);
  - **3b:** o que elas consomem tem fonte, e o teto não desculpa.
  - As transferências entram no laço de ganho com o sentido do lado; as duas retroalimentações do metabolismo são negativas e não
    viram aresta.
- **O motor:** uma linha. A conferência do estímulo do dono passou a ignorar o combustível, que não é drive.
- **A web:** só o espelho dos números na `ConfigCorpo` de `constantes.ts`. O `configCorpo` do TS falha alto com `metabolismo`: a química em
  TS é a etapa 4 (do A). O gabarito da paridade ganhou a seção `metabolismo` (as reações inteiras, uma grade com os limiares, a conversão 2/3 e
  uma sequência longa); as seções de antes saem idênticas.
- **Gates** (`tests/test_metabolismo.py`, 45):
  - **G2:** as 176 vidas da etapa 0 byte a byte;
  - **G-GRAFO:** as checagens em 7 combinações × com e sem o mundo, sem laço novo; o combustível sem gasto e a reserva sem armazenamento
    falham alto;
  - **G-MEC-M:** as contas exatas: a conversão com o resto e o teto, o basal, cada atividade igual ao cansaço dela, as transferências nos
    limiares, a falta só abaixo de C/4;
  - **G-HOJE-M:** com o corpo cheio, em vidas de 2 dias (o combustível acima de C/4, conferido), todo químico de antes é o de sem o
    metabolismo, tick a tick, nos três mundos e no físico, com o instinto e o P1; com os números PROPOSTOS a falta dispara, e até o tick
    dela tudo é igual, e nele só o cansaço sobe 500;
  - **G-CONS-M:** a contabilidade fecha a cada tick, nas vidas e numa sequência longa com a conversão 2/3 e o teto;
  - **G-RECEPTOR-M:** pela AST, nenhum cérebro, a rede de si, os instintos e o motor leem os químicos novos; o espião vê a mesma
    `PercepcaoCorpo`; o `n_pesos` é o de sem ele (998 com o banheiro); só a falta é emissor novo do cansaço;
  - **G1:** o replay refaz o combustível, a reserva e as contas.
- **Achado (descritivo, sementes dos testes):** com os números PROPOSTOS, em vidas de 3 dias, a falta fica ligada em 18% a 58% dos ticks.
  As atividades gastam ~240 por tick, e a conversão não as cobre. É o que o passo 0 da calibração (ME-7) escala.
- **Para o D (etapa 2):** o metabolismo nos regimes do bloco do corpo (ME-6). O `SUBCHAVES_CORPO` da bancada ainda não tem a `metabolismo`:
  hoje a chave `"corpo"` da config a ligaria em todo braço com corpo, o G-HOJE do plano inclusive.

## V2, BN-8 — o banheiro perto de onde o pet passa o dia (2026-10-11, decisão do Matheus) — GATES PASSAM

Pedido do Gerente depois da fumaça do #270 (0 alívios dentro). Infraestrutura, sem run de pesquisa; só as sementes dos testes. Mudaram o
padrão da área na `ConfigBanheiro`, o registro `PARAMETROS_BANHEIRO`, a `docs/TAREFA_V2_BANHEIRO.md` (seções 3 e 10) e os testes. O motor,
o instinto, os cérebros, a bancada e a web não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **A área (PROPOSTA, SEM FONTE):** células x 8 a 12, y 18 a 20, dentro da casa.
  - O ponto do banheiro mais perto do comedouro (10, 15), onde o pet passa o dia, fica a 40 subunidades: ao alcance de uma decisão (60).
  - A área não cobre o comedouro nem o ninho.
  - A de antes (#265) era x 0 a 3, y 0 a 5, no canto da casa.
  - A ida que continua (#270) fica; o contrato de decisão e o teto de pesos não mudam.
- **Os testes e gabaritos de antes** usam a área de antes, dada explicitamente: `CB_CANTO`, e `canto()` para a bancada. São eles os
  testes de mecanismo do #265 e do #270 e os gabaritos do banheiro ligado e do metabolismo.
- **Gates** (`tests/test_banheiro_perto.py`):
  - **G2:** a chave desligada é a vida de hoje (os gabaritos de sempre, na suíte). Com o banheiro ligado, as vidas de
    `tests/gabaritos/banheiro_perto_antes.json` (32 casos, gravados antes com a main 8cdb70f, `tests/gabarito_banheiro_perto.py`) saem
    iguais byte a byte com a área de antes dada explicitamente: só a área mudou;
  - **a geometria:** a área dentro da casa, a 40 do comedouro (alcance 60), fora do comedouro e do ninho (a zona deles não é a do
    banheiro);
  - **o motor:** o pet no comedouro que escolhe o banheiro chega e alivia dentro na mesma decisão, sem ida pendente.
- **Fumaça descritiva** (P0 e P1, sementes 101…505, 7 dias, atencioso no comedouro, com o carinho; antes = main, depois = o branch):

  | braço | alívios | dentro, antes → depois | carinhos | recolhidos pelo limpador | distância mediana ao banheiro |
  |---|---|---|---|---|---|
  | P0 (instinto) | 37 → 35 | 0 → 5 | 0 → 5 | 0 → 5 | 185 → 40–45 |
  | P1 (lobos, T3) | 36 → 39 | 0 → 8 | 0 → 8 | 0 → 8 | 308 → 130 |

  Há um carinho por alívio dentro, e o limpador recolhe todos.

## V2, W-BANCADA-METABOLISMO — a rota do humor no grupo, o metabolismo no bloco do corpo e o passo 0 montado (2026-10-11, `docs/TAREFA_V2_METABOLISMO.md`, etapa 2) — GATES PASSAM

Com o #269 (a rota do canal do humor no mundo físico, do B) e o #271 (o metabolismo no corpo, do B) na `main`. Infraestrutura, sem run;
só as sementes dos testes. Mudaram `experiments/bancada_v2.py`, `digilab/metrics.py` (duas medidas no fim), a config nova
`experiments/configs/v2_corpo/calibracao_passo0.json` e alguns testes antigos (abaixo). `engine.py`, `corpo.py`, `lobos.py`, o mundo e a
web não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **O nó `canais_fruta_mundo` saiu.** O cérebro do grupo (`Bancada.bancada_grupo`) liga `ConfigLobos.presenca_fruta_mundo` em todo
  braço, ao lado do alvo aprendido, das entradas sociais e do modelo dos outros. A run do plano dos dois pets valida com a montagem
  completa (sem ela, segue falhando alto), e o A só da semente 505, que falhava alto, passa.
- **O metabolismo no bloco do corpo (A3.1, ME-6):**
  - `Braco.metabolismo` está ligado no P0-q, P1-q, P0-c, P1-c, P0-c-tapa, P1-c-tapa, P1-c-tapaX, P1-c-frutas e P1-cw; os acoplados
    herdam pelo braço de destino;
  - o G-HOJE e o banheiro ficam sem ele; fora do regime "química" ou "corpo", falha alto;
  - a chave `corpo` da config e a `cfg_corpo` da bancada não o ligam (`SUBCHAVES_CORPO`);
  - `Bancada(metabolismo=False)`, fora da config, refaz as vidas de antes (os gabaritos do G2 do metabolismo e da rede de si).
- **A medida (A3.3, bloco `corpo.metabolismo` do `medidas.json`):** uma sonda só de leitura no `passo` do corpo, no replay de medição
  (`sondar_metabolismo`), e `metrics.metabolismo_da_vida`: a fração do tempo acordado com a falta, os disparos, e o combustível e a
  reserva no fim de cada dia. Saem também `metrics.tempo_comer_brincar` e as contas do corpo.
- **O passo 0 (A3.2, ME-7), montado sem rodar:**
  - a config: o P0-q, as 20 unidades (bases 33101…33505, K = 4, prefixo `corpo`) e as 8 células (4 donos × `bola` e `padrao`);
  - `pontos_passo0` monta os três pontos do basal (188/94, 375/187, 750/374);
  - `fracao_falta_passo0` junta as 8 células, e `escolha_passo0` aplica a regra (a faixa [0,05; 0,30], o mais perto de 1, o empate no
    menor gasto, "não fechou");
  - **trava no nó `gasto_atividades`**: a `ConfigCorpo` não tem o fator do gasto das atividades sobre o combustível (é do B).
- **Testes:**
  - `tests/test_bancada_metabolismo.py` (35);
  - `tests/test_bancada_dois_pets.py`: os canais rodam no grupo, e o A só 505 passa;
  - `tests/test_canal_fruta_mundo.py`: a falha antiga com o cérebro do grupo de antes;
  - `tests/test_bancada_liga_gestos.py`: o `NOS_PENDENTES` e, com a bancada de sempre, o G-P0C e os acoplados P1-q^ac e P1-c^ac com o
    metabolismo.
  - `tests/test_faixas_r17.py`: a faixa de calibração do corpo pode estar nas configs do próprio plano.

## V2, GASTO-ATIVIDADES — o fator do gasto das atividades sobre o combustível (2026-10-12, `docs/TAREFA_V2_METABOLISMO.md`, ME-3 e ME-7) — GATES PASSAM

Destrava o nó `gasto_atividades` do #273: o passo 0 da calibração do corpo escala o gasto basal **e o das atividades** (A3.2). Infraestrutura,
sem run; só as sementes dos testes. Mudaram `digilab/corpo.py`, a `ConfigCorpo`, o exportador e o gabarito da paridade do corpo e o espelho
em `web/app/motor/constantes.ts`. `engine.py`, o motor, os cérebros e a bancada não (a fiação é do D). Interpretações em
`docs/REGISTRO_DESVIOS.md`.
- **O fator:** `ConfigCorpo.gasto_atividades_num/gasto_atividades_den` (PROPOSTOS; padrão 1/1, o mesmo número do cansaço, ME-3). O
  brincar do pet e o do dono, o explorar e o andar tiram do combustível `div_arred(o que somam ao cansaço × num, den)`
  (`corpo.gasto_da_atividade`). O cansaço nunca muda. O andar arredonda uma vez por decisão, sobre o andar inteiro. Um fator que zera o
  gasto falha alto.
- **Etapa 0, num commit próprio, antes do fator:** `tests/gabarito_metabolismo_ligado.py` → `tests/gabaritos/metabolismo_ligado_vidas_de_hoje.json`,
  104 vidas com o metabolismo ligado: o bloco do corpo pela bancada (P0-q, P1-q, P0-c, P1-c, P1-c-tapa e P1-cw nos mundos `padrao`, `bola`
  e `iguais_frutas`) e, direto, a etapa 6 com o metabolismo nos quatro mundos (o físico tem o andar), com o corpo inteiro (q, resto e
  contas).
- **Gates** (`tests/test_gasto_atividades.py`, 36):
  - **G2:** com o fator no padrão, as 104 vidas saem byte a byte; desligado, o gabarito da etapa 0 do metabolismo (no teste dele);
  - **a conta exata:** cada atividade × {½, 1, 2}, o arredondamento do andar (37 × 75 × ½ = 1388) e as falhas altas;
  - **o grafo:** as quatro checagens (e a 2b e a 3b) passam com ½ e 2, com o mesmo relato do padrão, em 3 combinações × com e sem o mundo;
  - **G-HOJE-M com o fator:** até a falta, só o combustível muda; a contabilidade fecha;
  - **G1:** o replay refaz o corpo com o fator, no padrão e no físico.
- **A web:** só o espelho dos dois números. O gabarito da paridade ganhou a seção `metabolismo_gasto` (as taxas e a grade com ½ e 2); as
  outras saem idênticas.
- **Para o D:** a fiação no `pontos_passo0` é pôr o fator na chave `"corpo"` junto do basal (os mesmos num/den), e tirar o nó.

## V2, W-BANCADA-PASSO0 — o fator das atividades no passo 0 e a grade da PCD-9 (2026-10-12, `docs/PLANO_ANALISE_V2_CORPO_DRIVES.md`, A3.2b) — PRONTO, NÃO RODADO

Com o #274 (a grade da PCD-9, do C) e o #275 (o fator do gasto das atividades na `ConfigCorpo`, do B) na `main`. Infraestrutura, sem run
da calibração; só a fumaça nas sementes dos testes. Mudaram `experiments/bancada_v2.py`, a config do passo 0, a fumaça nova e dois testes.
`engine.py`, o corpo, os cérebros e a web não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **O nó `gasto_atividades` e a segunda trava saíram:** o `NOS_PENDENTES` ficou vazio.
- **A grade (PCD-9):** um `m_gasto` em {¼, ½, 1}, o mesmo no basal (94/47, 188/94, 375/187) e no fator das atividades
  (`gasto_atividades_num/den`). O cansaço não muda. `pontos_passo0` dá as três configs pela chave `corpo` e falha alto se a config já
  trouxer um dos quatro campos.
- **O orquestrador:** `python experiments/bancada_v2.py --passo0 --config experiments/configs/v2_corpo/calibracao_passo0.json --saida <pasta>`
  (`rodar_passo0`). Ele roda cada ponto pela `rodar` de sempre em `<pasta>/gasto_<num>_<den>/`, junta a fração das 8 células e aplica
  a regra; o resultado vai para `<pasta>/passo0.json`. A calibração tem 20 unidades × 8 células × 3 pontos = 480 vidas e é disparada
  pelo coordenador depois do merge.
- **A fumaça** (`experiments/configs/v2_corpo/fumaca_passo0.json`, NÃO canônica: sementes 101 e 202, 2 dias, 48 vidas em ~19 s; sem artefato).
- **Testes:** `tests/test_bancada_metabolismo.py` (a grade, o m_gasto no corpo da vida, a regra na grade nova, o passo 0 inteiro numa
  fumaça pequena); o `NOS_PENDENTES` vazio em `tests/test_bancada_liga_gestos.py`.

## V2, MUNDO-CALIBRACAO — a calibração do mundo físico (2026-10-12, `docs/PLANO_ANALISE_V2_MUNDO_FISICO.md`, seção 6, A1.4 e A1.9) — m = 1, N = 40

Autorizada pelo Matheus em 2026-10-12. Uma run nas bases 31101…31505 (K = 4, prefixo `mundo`, 20 unidades), 30 min com 8 processos.
Números de `artifacts_v2_mundo/calibracao/` (as vidas ficam fora do git); relatório `docs/RESULTADO_V2_CALIBRACAO_MUNDO.md`.
Interpretações em `docs/REGISTRO_DESVIOS.md`. **A validação (32101…32505) não rodou: precisa de outro sim.**
- **Código:**
  - `experiments/run_v2_calibracao_mundo.py`: a grade (P0 e P0z em `m` ∈ {½, 1, 2}), a regra do menor `m`, o piloto (P1, P0^ac e
    P1^ac), o `Δ_MF`, o K pelo poder simulado e o custo. Toda vida tem o replay do disco conferido. O `meta.json` traz os sha256. A run
    recusa uma pasta existente e as sementes da validação;
  - as configs `experiments/configs/v2_mundo/calibracao.json` e `fumaca_calibracao.json` (a mesma, nas sementes dos testes);
  - na bancada, a dominância só põe o humor (E2) na decisão de comer (`comeu_fruta_e2`). No mundo físico o motor avisa `fruta_comida`
    também no explorar, e a conferência com os canais falhava alto (achado da fumaça);
  - testes: `tests/test_calibracao_mundo.py` (10).
- **O mundo: `m` = 1.** A premissa P0z − P0 em `D_FE`:
  - em ½, −0,00006 [−0,0085; +0,0087]: não passa;
  - em 1, **+0,0154 [+0,0093; +0,0209]**;
  - em 2, +0,0196 [+0,0127; +0,0264].
- **`Δ_MF` = 0,00768. K = 8 por base (N = 40),** com poder de 0,802 no G-MF1r. No relato:
  - o G-MF2r tem poder de 0,92 a 0,99;
  - o G-MF3r, na privação, fica subpotenciado (0,03 a 0,11).
- **Custo:** 3,9 a 7,9 s de CPU por vida.
  - A validação com K = 8: 4,3 h de CPU, ou 6,3 h com o layout afastado;
  - com 8 processos, ~0,8 h de parede.
- **O piloto não é evidência sobre o P1.** P0 − P1 em `D_FE` deu −0,012 [−0,020; −0,005].
- **Achado:** o desempate do cheiro do #232 não está no motor. A calibração rodou com a ordem fixa.

## V2, TETO-POR-PLANO — o teto de pesos do cérebro A por plano (2026-10-13, `docs/DECISAO_V2_TETO_PESOS.md`, TP-1 e TP-2) — GATES PASSAM

TP-1 e TP-2 foram decididas pelo Matheus em 2026-10-12, pela recomendação. Infraestrutura, sem run; só as sementes dos testes. Mudaram a
`ConfigLobos` (a checagem) e o `LIMITE_TETO_PESOS_PLANO` no `config.py`, o registro do `maximo_pesos` em `lobos.py`, a bancada, a receita e o
status da decisão. `engine.py`, a conta dos pesos, os cérebros B e C, a rede de si e a web não mudaram. Interpretações em
`docs/REGISTRO_DESVIOS.md`.
- **O padrão fica 1000** (`ConfigLobos.maximo_pesos`). A `ConfigLobos` recusa um teto que não seja inteiro de 1 a
  `LIMITE_TETO_PESOS_PLANO` (2000, DECIDIDO pela TP-2, SEM FONTE). A contagem e a falha alta do cérebro (n ≥ teto) não mudaram.
- **O plano declara** na config da bancada (a de vidas e a do grupo):
  - a forma é `"teto_pesos": {"maximo": N, "pesos": n}`, com N acima de 1000 e até 2000, e n de 1000 a N − 1 (um cérebro que cabe no
    padrão não precisa de teto próprio);
  - a config precisa do campo `plano`, com o arquivo que diz por quê;
  - **o teto só entra por aí:** `"lobos": {"maximo_pesos": ...}` falha alto (`validar_teto_pesos`, chamada pelas duas validações e pelo
    `bancada_da_config`).
- **A run confere os pesos declarados** antes de qualquer vida (`conferir_teto_pesos`): n tem de ser o maior cérebro A dos braços da
  config, montado pela bancada (no grupo, os pets de cada braço). Se não for, a run falha alto. O teto conferido vai ao `meta.json`
  (`teto_pesos`).
- **G2:** sem nada declarado, a bancada é a de hoje. Isso vale para a `ConfigLobos` de toda config de `experiments/configs/`, para o
  `meta.json` sem a chave nova e para os gabaritos de sempre, na suíte.
- **O que falta para o primeiro plano acima de 1000:** a medida do custo do replay com o cérebro maior (a TP-2 pede no PR que o fizer).
  Os cérebros B e C seguem com 1000.
- **Testes** (`tests/test_teto_por_plano.py`, 9):
  - o limite;
  - os cérebros de 1116 e 1277, que falham no padrão e nascem com o teto do plano;
  - o teto não muda nada abaixo de 1000;
  - o G2;
  - as recusas;
  - a conferência dos pesos, também na run de vidas e na do grupo.

## V2, DOIS-PETS-CALIBRACAO — a config e o orquestrador da calibração do K e do piloto (2026-10-12, `docs/PLANO_ANALISE_V2_DOIS_PETS.md`, seções 5, 6, 8 e 11) — PRONTO, NÃO RODADO

Aprovado pelo Matheus em 2026-10-12, para rodar **depois** que a validação do mundo físico passar; quem dispara é o Gerente. Só fumaça nas
sementes dos testes. Mudaram `experiments/run_v2_calibracao_dois_pets.py` (novo), as configs `experiments/configs/v2_dois_pets/calibracao.json`
e `fumaca_calibracao.json`, duas funções no fim de `digilab/metrics.py`, o `.gitignore` e a exceção da faixa de calibração em
`tests/test_bancada_banheiro.py`. `engine.py`, a bancada, o grupo, o mundo, os cérebros e a web não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **A run** (`python experiments/run_v2_calibracao_dois_pets.py --config experiments/configs/v2_dois_pets/calibracao.json --processos 6`
  → `artifacts_v2_dois_pets/calibracao/`; recusa a pasta que existe, as bases da validação 40101…40505 e qualquer faixa fora do plano):
  - **K:** o A-so (o A informativo sozinho, P1), 10 dias, nas 20 unidades (bases 39101…39505, K_u = 4, prefixo `dois_pets`). A regra
    G-K pega o menor K de {3, 5, 7} com o limite superior do IC95 de R_A no dia K abaixo de metade da R_A do dia 1 → `k.json`. Se nenhum
    K passa, a run para sem piloto;
  - **piloto:** os quatro braços no K escolhido, com o B vivendo 14 dias. A run confere que o A do B + Ainf até o dia K é o A-so da mesma
    unidade, e falha alto se não for → `piloto/`;
  - **margem e N:** `Δ_S`; a validação não roda se a distância ficar ≤ 0,05. O K_u de 4 a 10 sai pelo poder simulado no G-SOCIAL (a
    conta do A1.4 do mundo); o poder do G-COMPANHIA e do G-INGENUO sai só como relato; o custo → `resultado.json`.
- **A config:**
  - o cérebro A no ponto da K2 (T3, `g` S/2, `w0_pedido` S/4, `w0_info` S/4, ganho 4, canais), com a montagem completa;
  - o que a bancada do grupo liga (o alvo aprendido, as entradas sociais, o modelo dos outros e a rota do humor);
  - o `m` da calibração do mundo (1,0);
  - um teste confere a config contra os dois artefatos.
  - **Fora do plano, a decidir:** `taxa.modo` (a agregação da R entre unidades), `taxa.n_minimo` (o consumo mínimo nas janelas da regra)
    e `calibracao_k.janelas` (a letra, ou `dois_dias` só com o adendo).
- **`metrics.taxa_agregada` e `bootstrap_taxa_agregada`:** a R de um grupo de unidades por razão das somas ou média das unidades; a unidade
  sem consumo não tem taxa. O IC reamostra as unidades; com reamostra sem consumo, o IC sai None com a contagem.
- **O teto:** o degrau 1 tem 990 pesos em todo pet de todo braço (teto 1000). Os canais estão só nos P1, e a memória não existe no mundo
  físico.
- **Achado da fumaça (só a contagem, sementes dos testes):** o A sozinho come de 0 a 9 frutas maduras por dia (no dia 1, 1 em 5
  unidades). Na letra da seção 5, a regra para por "exposição baixa".
- **Testes:** `tests/test_calibracao_dois_pets.py`, 16, ~25 s: a config, as recusas, o teto, a taxa agregada, a regra, a margem e o
  contraste em dados com a resposta conhecida, a fumaça inteira e o piloto num K da grade (a rota do humor credita a fruta ruim no A com
  os canais).

## V2, CORPO-CALIBRACAO — a calibração do corpo (2026-10-12/13, `docs/PLANO_ANALISE_V2_CORPO_DRIVES.md`, seções 6 e 7, adendos 3 e 4) — PONTO E N CONGELADOS; DUAS FAIXAS NÃO FECHARAM

Autorizada pelo Matheus em 2026-10-12. Sementes 33101…33505 (K = 4, prefixo `corpo`, 20 unidades). Números de
`artifacts_v2_corpo/calibracao/` (as vidas ficam fora do git); relatório `docs/RESULTADO_V2_CALIBRACAO_CORPO.md`. Interpretações em
`docs/REGISTRO_DESVIOS.md`. **A validação (34101…34505) não rodou: precisa de outro sim.**
- **Código:**
  - `experiments/run_v2_calibracao_corpo.py`: a grade da 6.1 (só o P0-c), a regra da 6.2 (a faixa, o mais perto de (1, 1), o `w_novos`),
    o piloto da 6.3 (os blocos G-HOJE, corpo com os acoplados, tapa, G e P1-cw: 120 por unidade), as sensibilidades da 6.4 e da A1.2, as
    margens e o N da seção 7 (os efeitos pelo `poder_simulado`; a não inferioridade e a equivalência com os contrastes juntos) e o custo.
    Recusa a pasta existente e as sementes da validação; o corpo da config tem de ser o do passo 0;
  - na bancada: o bloco `comportamento` em toda vida (a `BE` e o cuidado, também no "hoje"), as parcelas dos drives novos por decisão de
    tempo livre (`novos_livres`, para o `w_novos`) e os efeitos do tapa da 5.4 (`metrics.efeitos_do_tapa`, bloco `corpo.tapa`); o
    `meta.json` ganhou o sha256 do `corpo.py` e do `motor_corpo.py`, e o passo 0 recusa a pasta existente;
  - configs `experiments/configs/v2_corpo/calibracao.json` e `fumaca_calibracao.json`; testes `tests/test_calibracao_corpo.py` (9).
- **O passo 0 (A3.2c):** `m_gasto` = ½, **"não fechou"**: a falta de combustível em 0,000 (¼), 0,0004 (½) e 0,49 (1) do tempo acordado.
- **O corpo (A4.1):** (`m_sobe`, `m_reduz`) = (2, 1), **"não fechou"**: a solidão não chega a 0,10 sem o tédio e o estresse passarem do
  teto. `w_novos` = 2 (fechou: mediana da parcela 0,394).
- **Margens (A4.2):** `Δ_BE` 0,2235, `Δ_priv` 0,0295, `Δ_saude` 0,0334, `Δ_TED` 0,1633. **N = 20 (K = 4)**, todo gate com poder ≥ 0,968.
  A validação: 2.400 vidas, 3,6 h de CPU, ~0,6 h com 6 processos (com 12 o pool caiu).
- **O piloto não é evidência:** P1-c − P1-q em `BE`, `bola`, +0,67, com o cuidado igual; o G-P0C vale nas 160 células.

## V2, MUNDO-VALIDACAO — a validação do mundo físico (2026-10-13, `docs/PLANO_ANALISE_V2_MUNDO_FISICO.md`, seções 7 e 8, A1.2–A1.9) — G-MUNDO PASSA; O P1 PERDE (resultado negativo registrado)

Autorizada pelo Matheus em 2026-10-12. Uma run nas bases 32101…32505 (K = 8, N = 40, prefixo `mundo`), `m` = 1 e `Δ_MF` da A1.9, o
mundo da calibração; 3.360 vidas rejogadas do disco, 50 min com 8 processos (6,5 h de CPU). Números de `artifacts_v2_mundo/validacao/`
(as vidas fora do git); relatório `docs/RESULTADO_V2_VALIDACAO_MUNDO.md`. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **Código:** `experiments/run_v2_validacao_mundo.py`, com:
  - por unidade, as 84 vidas: P0, P0z e P1; os acoplados P0^ac e P1^ac ao P0z; e o P0 e o P1 no layout afastado;
  - os gates G-MUNDO e G-MF1r (as categorias da seção 8);
  - o Holm dos cinco secundários, com o p do bootstrap orientado;
  - a leitura da A1.5 e os descritivos;
  - a recusa de rodar de novo e a config presa à calibração.
  - Configs `experiments/configs/v2_mundo/{validacao,fumaca_validacao}.json`; testes `tests/test_validacao_mundo.py` (17).
- **G-MUNDO passa:** P0z − P0 em `D_FE` +0,0105 [+0,0048; +0,0159].
- **G-MF1r: o P1 perde.** P0 − P1 em `D_FE` −0,0097 [−0,0149; −0,0046]: o P1 sustenta fome e energia pior que o instinto.
- **G-MF2r não passa** (−0,0088 [−0,0123; −0,0051]): a perda aparece com o cuidado fixo, então é do pet. G-MF3r e G-OPORT não passam.
- **G-PERM e G-DIST passam no Holm** (sem Δ nem poder): o P1 fica mais nas manchas (352 contra 191 min), mais com o custo de viagem e
  mais no layout afastado, mas ficar não paga.
- **Leitura (A1.5, terceira linha):** a consequência imediata não aprende a procurar neste mundo. Por dono, a perda vem do atencioso e do
  incoerente; com o relapso o P1 ganha um pouco (descritivo).

## V2, DOIS-PETS-CALIBRACAO, a run — o K não fecha (2026-10-13, `docs/PLANO_ANALISE_V2_DOIS_PETS.md`, seção 5 e adendo 1) — O PLANO VOLTA AO MATHEUS

Decisão do Matheus (2026-10-13): a PDC-1 pela recomendação. O adendo 1.1 (as janelas de dois dias da regra do K) foi commitado antes da
run (`24f0b6d`), e a calibração rodou uma vez. Números de `artifacts_v2_dois_pets/calibracao/` (`k.json`, `resultado.json`,
`k/medidas.json`, `meta.json`; os registros dos grupos ficam fora do git, regeneráveis). Eles estão congelados no adendo 1.2 do plano.
- **A run:**
  - 20 grupos A-so (o A informativo sozinho, P1, 10 dias), nas bases 39101…39505 (K_u = 4), cada um gravado e rejogado do disco bit a
    bit;
  - 9 s de parede com 8 processos.
- **G-K:** a R_A dos dias 1 e 2 é 0,485 (33 consumos). Nos dias K − 1 e K, a R_A é 0,358 (K = 3), 0,338 (K = 5) e 0,366 (K = 7). O limite
  superior do IC95 fica entre 0,52 e 0,57, contra o limiar de 0,242. **Nenhum K passa, e não é por exposição:** toda janela tem 53 a 77
  consumos.
- **O plano para (seção 5):** sem piloto, sem `Δ_S`, sem N; a validação não roda. O plano volta ao Matheus.
- **Descritivo:** a R_A da vida toda é 0,343 em 300 consumos, perto de 1/3, a fração de um tipo entre três. Cada A come em média 15
  frutas maduras e 83 rações em 10 dias.

## V2, PET-QUE-PENSA, etapas 0 e 1 — os modelos do mundo, só observando (2026-10-13, `docs/TAREFA_V2_PET_QUE_PENSA.md`) — GATES PASSAM

J5, com PP-1 a PP-9 decididas pela recomendação. Infraestrutura, sem run; só as sementes dos testes. Mudaram `digilab/modelo_mundo.py`
(novo) e a `ConfigModeloMundo` no fim de `config.py`. `engine.py`, os cérebros, o corpo, o mundo, a bancada e a web não mudaram.
Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **Etapa 0, num commit próprio, antes do módulo:** `tests/gabarito_pet_que_pensa.py` → `tests/gabaritos/pet_que_pensa_vidas_de_hoje.json`,
  136 vidas:
  - pela bancada, P0, P1 e P3 no regime química e o P0 do instinto do mundo, nos dois layouts, nas montagens simples e completa, com o
    alvo aprendido e a presença da fruta;
  - direto, vidas com o metabolismo (PP-3).
- **`ModeloMundo`** (só inteiros, sem rng; importa só `config` e `events`):
  - **o desfecho:** por tipo (`racao`, `a`, `b`, `c`, `podre`) e receptor, a mudança esperada da leitura ao comer. Aprende nos consumos
    do `comer`, com a energia corrigida pelo andar previsto; o "achou e comeu" só é contado;
  - **o custo de andar:** a mudança da energia por subunidade, vezes S, aprendida nos `comer` com deslocamento percebido;
  - **o mapa:** por árvore do layout e pelo comedouro, a frequência do tipo maduro visto a até 2 células. Um lugar só entra depois de o
    pet vê-lo (o raio da visão), e a fruta de cada árvore no layout nunca é lida;
  - os números são PROPOSTOS (PP-6): `passo_desfecho` S/4, `passo_mapa` S/8, `raio_ancora_celulas` 2, `teto_modelo` 200; registro
    `modelo_mundo.PARAMETROS_MODELO_MUNDO`;
  - **76 inteiros** no regime química (5 tipos × 5 receptores + 1 + 10 lugares × 5 tipos); 101 com os drives novos.
- **`PoliticaComModelo`:** o embrulho somente leitura. Entrega aos modelos a observação de cada decisão e a consequência do mundo, e
  repassa o resto ao cérebro. O estado interno é o do cérebro; os modelos ficam em `modelo` (`para_dict`).
- **Gates** (`tests/test_modelo_mundo.py`, 196, ~1 min):
  - **G-INT** (AST) e o módulo só importa `config` e `events`; as contas inteiras são as de sempre (`isqrt`, `div_arred`);
  - **G-TETO-MODELO:** 76, e o teto falha alto;
  - **G-RECEPTOR-MM:** o Estado, o relógio do cuidado, a informação do dono, o resto do `ocorrido` e a fruta do layout não mudam os
    modelos; um químico sem receptor não muda a percepção;
  - **a conta exata** de um passo do mapa (e da âncora), do andar e do desfecho, a podre, o "achou e comeu" e o `comer` sem comida;
  - **G-OBS-MM:** as 104 vidas com corpo da etapa 0 saem byte a byte com os modelos observando; sem o corpo (as 32 do P0 do instinto da bancada), falha alto, e essas saem iguais ao gabarito;
  - **G1:** o replay da bancada refaz os modelos bit a bit.
- **Fica para depois:** o planejador e o lobo `planejamento` (etapa 2), as classes por árvore (2b), a troca de tipo e a fruta na mão
  (etapa 3, A), a bancada (etapa 4, D).

## V2, PET-QUE-PENSA, etapas 3 e 2b — o mundo do J5 e as classes por árvore (2026-10-13, `docs/TAREFA_V2_PET_QUE_PENSA.md`) — GATES PASSAM

A etapa 3 (o mundo, do A) e a 2b (as classes por árvore no alvo aprendido, dada ao A pelo Gerente), com PP-1, PP-2 e PP-5 do
`docs/PLANO_ANALISE_V2_PET_QUE_PENSA.md`. Infraestrutura, sem run; só as sementes dos testes. Mudaram `digilab/events.py` (o fim do enum),
`digilab/mundo.py`, `digilab/motor_corpo.py` (o estímulo da mão), `digilab/policies/lobos.py` (atrás da chave), a `ConfigLobos` e a
`ConfigPetQuePensaMundo` no fim de `config.py`. `engine.py`, o `AcaoPet`, a bancada e a web não. Interpretações em `docs/REGISTRO_DESVIOS.md`.
- **A chave do mundo:** `MotorMundo(..., cfg_pqp=ConfigPetQuePensaMundo(ligada=True))`, só com o mundo físico e um pet (fora do grupo).
  Desligada, nada muda. Ligada:
  - **os troncos vistos** (`troncos_vistos`: id → o primeiro tick do mundo), a até o raio da visão, na decisão e depois de andar; a
    percepção ganha `troncos` (id, dx, dy, d), com padrão vazio;
  - **os candidatos de árvore lembrada (PP-1):** no explorar, `arvore:<id>` de cada tronco já visto, no tronco, na ordem do layout,
    depois dos de hoje. O padrão do motor e o instinto nunca os escolhem;
  - **a fruta na mão** (`dar_fruta_<f>`, fora do orçamento): o pet come na hora, onde está, com o efeito vigente (a conta da fruta
    madura; com o corpo, o `estimulo_consumo_mundo`), entra em `consumos_mundo` com `como` "mao" e não é contato. O cérebro a recebe só
    pelo gancho opcional `fruta_na_mao(tipo, obs_antes, obs_depois)` (G-SEM-CREDITO). Com o pet dormindo, falha alto;
  - **a troca de tipo** (`trocar_arvores_<x>_<y>`, fora do orçamento): no tick do evento as árvores do x passam a dar y e as do y a dar
    x; as quedas até o tick usam o tipo velho e o chão fica como estava (`Mundo.trocas_tipo`; o replay refaz pelo log).
- **As classes por árvore (PP-2):** `ConfigLobos.alvo_por_arvore` (exige o alvo aprendido): `arvore:J1` … `arvore:M6` nas tabelas do
  explorar, 27 pesos a mais (822 no P1 do plano), w0 = `w0_alvo`, aprendidas só pela consequência. Sem a chave, um candidato de árvore no
  alvo aprendido falha alto.
- **Gates** (`tests/test_pet_que_pensa_mundo.py`, 24):
  - **G2:** as 48 vidas de `tests/gabaritos/pqp_mundo_vidas_de_hoje.json` (`tests/gabarito_pqp_mundo.py`, gravado antes num commit
    próprio), byte a byte;
  - os eventos no fim do enum e as recusas (os motores de hoje, sem a chave, sem o mundo, no grupo, dormindo);
  - os troncos vistos refeitos por fora, a percepção deles e os candidatos de árvore na ordem;
  - o instinto nunca vai à árvore, e o P0 com as classes por árvore é o instinto do mundo byte a byte;
  - **G-SEM-CREDITO e a conta exata da mão**, sem e com o corpo (o estado interno do A inteiro igual, nenhum gancho de crédito, o gancho
    da mão com o corpo, não é contato, o orçamento fecha);
  - a troca no tick, com as quedas antes no tipo velho e depois no novo;
  - as classes por árvore: a contagem, as falhas altas e a conta exata pela consequência (o dono não mexe);
  - **G1** com tudo ligado (o P1, a mão e a troca), sem e com o corpo.
- **Para o D (etapa 4):** a fábrica dos braços do J5 passa `cfg_pqp` ao `MotorMundo` e `alvo_por_arvore` ao cérebro A; os eventos da mão e
  da troca entram pelo `observar` do motor no `T_m` do plano, fora do orçamento. O gancho `fruta_na_mao` é do modelo do desfecho do B.

## V2, MUNDO-ALVO — o mundo com o alvo aprendido: código pronto, piloto bloqueado (2026-10-13, `docs/PLANO_ANALISE_V2_MUNDO_ALVO.md`) — NÃO RODADO

PMA-1 a PMA-9 pela recomendação, autorizado pelo Matheus em 2026-10-13. Mudaram `experiments/bancada_v2.py` (o braço `P1-alvo` e as
faixas), `digilab/metrics.py` (`uso_do_alvo`, `classes_por_dia`), `experiments/run_v2_mundo_alvo.py` (novo), as configs
`experiments/configs/v2_mundo_alvo/` e os testes. `engine.py`, `lobos.py`, `mundo.py` e a web não. Interpretações em
`docs/REGISTRO_DESVIOS.md`.
- **O braço `P1-alvo`** (`Braco.alvo`): o P1 com `ConfigLobos.alvo_aprendido` e o `w0_alvo` padrão (S/16), só no mundo físico; 792 pesos
  (o P1, 756). Os outros braços não mudam.
- **As faixas** 47101…47505 (piloto) e 48101…48505 (validação), prefixo `mundo`, em `FAIXAS_RESERVADAS`.
- **O orquestrador** (`--config .../piloto.json` ou `.../validacao.json`):
  - **o piloto:** 72 vidas por unidade; o K pelo poder simulado no G-ALVO com o `Δ_MF`, o G-USO e o custo;
  - **a validação:** 96 vidas por unidade, com o bloco afastado; G-MUNDO, G-USO, G-ALVO e o Holm de G-ALVO-AC, G-INSTINTO, G-PERM-A e
    G-DIST-A; a leitura da seção 9;
  - recusa as bases do plano do mundo, a pasta que existe e a validação sem o piloto e o adendo 1.
- **O G-USO** sai do motivo do cérebro (o `u` já está lá): a escolha contra o sorteio do prior com o mesmo `u`.
- **Bloqueio:** com os canais do J1, o P1-alvo que come comida podre (a classe `comida_podre`) falha alto no CANAIS-REFORCO: o canal do
  humor fica sem peso que leia a fruta. O piloto parou, e a validação não rodou. As saídas, com a recomendação, estão no registro de
  desvios; a decisão é do Matheus. O caso está em `tests/test_mundo_alvo.py`.
