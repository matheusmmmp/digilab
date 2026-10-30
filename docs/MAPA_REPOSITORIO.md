# Mapa do repositório e comandos

O mapa arquivo a arquivo e a lista de comandos, movidos inteiros do CLAUDE.md da raiz na etapa 1 da rodada de saúde
(`docs/TAREFA_V2_SAUDE.md`, 2026-10-13). O mapa descreve o repositório até o começo da V2; as frentes da V2 estão nos
`docs/historico/claude/v2_*.md` e nas tarefas. Atualizar aqui quando um arquivo novo de topo entrar.

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

## A bancada em módulos (2026-10-14, rodada de saúde, etapa 3)

A tabela acima é a de antes da rodada e fica como está. Desde a etapa 3, o código da bancada está no pacote `experiments/bancada/`, um
módulo por assunto (a tabela dos módulos está em `experiments/bancada/__init__.py`). O `experiments/bancada_v2.py` ficou como a porta de
entrada: reexporta todo nome do pacote, e a linha de comando é a mesma. As faixas reservadas ficam em `experiments/bancada/faixas.py`.
O mapa nó a nó, de onde saiu e para onde foi, está em `docs/historico/bancada_mapa.json`, e a ferramenta é `tools/dividir_bancada.py`.

## Atualizações depois da rodada de saúde

As seções acima são cópias inteiras do CLAUDE.md antigo (o G-NADA-PERDIDO confere). O que mudou depois entra aqui:
- **2026-10-19, TAREFA_V2_FRONT_REACT (#368):** o app de `web/app/src/` passou de Preact para **React** (Vite mantido). Comando novo: `cd web/app && npm run capturas` — as capturas das telas contra a referência, pixel a pixel.
- **2026-10-19, TAREFA_V2_FRONT_REACT, etapa 2:** **Tailwind 4** (só tema e utilidades, sem o preflight; `src/estilo/tailwind.css`, com os tokens `--dl-*` e `--ui-*` no tema), **shadcn** (`components.json`, `src/lib/utils.ts`, `src/componentes/ui/`, alias `@/` = `src/`) e **lucide-react**, sem mudar o visual de nenhuma tela.
- **2026-10-19, TAREFA_V2_TELA_PET:** a tela Pet tem a vista 3D do POC como cenário (`web/app/src/telas/pet/cena3d.ts`, o único módulo do app que importa o three, por import dinâmico; a reserva sem WebGL é o `CenarioPet`). A M3 da cena no celular: `?medir3d=1` no endereço do jogo (instruções na TAREFA).
- **2026-10-20, TAREFA_V2_MOLDURA_DESKTOP:** a casca do desktop é a da prancha `TelasLayoutDesktop` (lateral escura com o logo, as abas no topo, o painel de cantos cortados em `div.moldura`). O roteiro de capturas aceita `DIGILAB_CAPTURAS_LARGURAS` (ex.: `360`) e `DIGILAB_CAPTURAS_RESERVA=1` (sem o atlas e a decoração do UP).
- **2026-10-20, TAREFA_V2_PET_QUADRO:** a tela Pet do desktop é um quadro modular (`src/componentes/Quadro.tsx`): os módulos do motor (habitat, ações, estado, desejo, próxima evolução, últimas ações, DigiBrain, o porquê da fala) se arrastam entre as colunas e se recolhem; o arranjo fica no `localStorage` (`digilab-web-v21-sprites-quadro-pet`), fora do save.
- **2026-10-21, TAREFA_V2_EXPLORACAO:** a aba Lutar › Campanha se chama Exploração (a rota `#/lutar/campanha` não muda) e mostra o mapa 3D de ilhas de voxels (`src/telas/lutar/mapa3d.ts`, chunk próprio; a disposição em `mapaLayout.ts`, os cartões e o marcador em `MapaExploracao.tsx`); sem WebGL, o mapa 2D de antes. O roteiro de capturas soma `lutar-exploracao-v6`.
- **2026-10-21, TAREFA_V2_EVOLUCAO:** o momento da evolução (`src/componentes/Revelacao.tsx`) é a tela azul cheia com o pet na plataforma de luz, o cartão, o "de → para", o que decidiu e as medalhas; a aba Crescer › Evolução foi recomposta (destaque, próxima evolução, árvore, porquê, histórico com "Ver a revelação de novo"); `src/estilo/evolucao.css`. O save `e2e/save_evolucao.json` (`e2e/gerar_save_evolucao.mjs`) evolui quando o relógio anda; o roteiro de capturas soma `evolucao-momento` e `crescer-evolucao-v6`.
- **2026-10-22, TAREFA_V2_TREINO:** a aba Crescer › Treinar tem composição própria (a sala clara com o pet na plataforma, o stat em foco, o cansaço, os exercícios, o treinado na vida, o último treino; `src/estilo/treino.css`), sem minigame nem nível. Os saves `e2e/save_treino_pausa.json` e `e2e/save_treino_forcar.json` (`e2e/gerar_save_treino.mjs`); o roteiro de capturas soma `treino-pausa` e `treino-forcar`.
- **2026-10-24, TAREFA_V2_MVP_MUNDO_PRODUTO, etapa 2:** a Tela Pet dos v12 desenha o mapa do motor (o modo mundo de `src/telas/pet/cena3d.ts`; sem WebGL, `MundoReserva.tsx`; a janela e a interpolação em `vistaMundo.ts`); a ração vai ao chão pelo gesto, pelo toque ou por um lugar nomeado (`PorRacao.tsx`, o evento `dc`); o Alimentar fica como reserva. O save `e2e/save_mundo.json` (`e2e/gerar_save_mundo.mjs`); o roteiro de capturas soma `pet-v12`.
- **2026-10-25, TAREFA_V2_DIGIBRAIN_MODULAR_PROTOTIPO, etapa 1b:** o gabarito das vidas v12 do jogo em TS (`web/app/test/gabaritos/v12_jogo_ts.json`, de `test/v12_jogo_ts.test.ts`, com `GRAVAR_V12=1`); o `ponto` no laço atrás da chave da v13 (`OpcoesLacoMundo.digibrain` e o gancho `escolherAlvo` da política; `test/ponto_v13.test.ts`); a medição pontual do A v11 no navegador: `cd web/app && node --experimental-strip-types test/medir_custo_a.mjs` grava `test/custo_a_v11_navegador.json`.
- **2026-10-29, TAREFA_V2_PRODUTO_FOME:** as chaves do produto dos pets v12 no evento `"p"` do registro (`motor/tipos.ts`, `Motor.ligarProduto`; o jogo as liga nos ovos novos por `src/produto.ts`): o chamado de fome do bebê pela fome do corpo (`CHAMADO_FOME_CORPO`) e a decisão na comida (`OpcoesLacoMundo.decidirNaComida`; no Python, `ConfigDecisaoNaComida`). Os testes `test/produto_fome.test.ts` e `test/decisao_na_comida.test.ts` (o G-PAR, com o laço gravado em `test/laco_gravado.ts`); o gabarito `python experiments/exportar_gabarito_decisao_na_comida.py` grava `web/app/test/gabaritos/decisao_na_comida_python.json` (`tests/test_decisao_na_comida.py`); o efeito no bebê: `cd web/app && node --experimental-strip-types test/medir_chamado_fome.ts` grava `test/efeito_chamado_fome.json`.
- **2026-10-30, TAREFA_V2_PRODUTO_CUIDADO:** a terceira chave do produto, `chamadosPeloCorpo` (o evento `"p"` dos ovos novos; `src/produto.ts`): os três chamados do bebê pelo corpo, com os limiares do bebê (`CHAMADO_BEBE_CORPO`, `Motor._chamadoCorpo`). O teste `test/produto_cuidado.test.ts`; o efeito no bebê: `cd web/app && node --experimental-strip-types test/medir_chamados_bebe.ts` grava `test/efeito_chamados_bebe.json`.
