# V2 — Inventário do jogo e da pesquisa (F0-INVENTARIO, 2026-10-01)

Status: **ENTREGUE para decisão** (tarefa `docs/TAREFA_V2_F0_INVENTARIO.md`; fase 0, item 2 do `docs/PLANO_V2_PESQUISA.md`;
passo 1 do `docs/TODO_INTERACAO_CORPO.md`). Só documento: **nenhum código muda**. Nenhuma run nova: todo número vem de um
artefato já em disco (caminho ao lado) ou de uma constante de `digilab/config.py` / `web/app/motor/constantes.ts` (símbolo ao lado).

Conferido no código da `main` em `83fc08f` (PR #103). A auditoria externa `D:\Trab\digilab\docs\digibrain\integration\01_CURRENT_STATE.md`
(escrita sobre `3fe6d76`) foi o ponto de partida; cada item foi reconferido no código, e as divergências encontradas estão na seção 5.

**Rótulos** (os da auditoria): `EXECUTADO` = rodou e tem artefato; `ESPECIFICADO` = existe em documento ou código, sem execução que o
valide; `IDEIA` = só registrado. **Validação**: "gate" = passou (ou reprovou) num gate com artefato; "provisória" = sem gate, sem
artefato que a sustente, ou PROVISÓRIO declarado no código. **Pesquisa usa** = entra em alguma run com protocolo ou plano de análise
(V1 canônica, ablação, memória, personalidade, V3/V3b/V3c, confirmatória, E1, V21D painel, Etapas A e B). **Versão** = versão de pet
da web em que entrou (`VERSAO_PET`, `web/app/motor/constantes.ts`); "Py" = só Python; "web" = só jogo web.

---

## 0. Resumo

- **O pet decide uma coisa só: a próxima ação de vida, a cada 15 min, entre 7 ações, olhando só o próprio estado.** São 96
  decisões por dia (`TICKS_POR_DIA / Config.intervalo_decisao_ticks`), e nenhuma delas é sobre um objeto, um lugar ou uma situação
  que o dono tenha criado: o dono só muda o estado (alimentar, limpar…) e dá feedback.
- **Todas as outras "decisões" do pet são sorteios condicionados a contadores, não escolhas da política**: recusar o cuidado
  (`rng_obediencia`), fazer um chamado falso (`rng_travessura`), mentir (`rng_mentira`), enrolar no treino (`rng_obediencia`). O dono
  muda os contadores (vínculo, disciplina), mas o aprendiz não participa e não aprende com elas.
- **No combate o pet decide a cada turno, mas no Python a lista de regras é fixa** (a aprendizagem de gambits é só da web); o dono
  entra pela forma, pelo treino e pelo ε da disciplina.
- **Onde o dono importa hoje, importa pelo cuidado**: chamados do bebê (nenhum dono sintético os vê: 548 de 548 pets vivos da V3
  nasceram ariscos, `artifacts_educacao/pets.json`), avisos de banheiro, lesão e morte. É o confundidor da
  `docs/LEITURA_CONSOLIDADA_DONO.md`.
- **Recomendação**: a interação mínima da 1a é **um objeto de brincar posto pelo dono (a bola)**, porque é a única candidata cuja
  consequência vive fora da cadeia da saúde (humor e energia; `Estado.em_privacao` ignora o humor), o que torna o gate G5 (separação
  do cuidado) satisfazível por construção. A comida posta é a segunda, com mais consequência e no eixo do cuidado. Seção 4.

---

## 1. Tabela de mecânicas

### 1.1 Motor de vida (Python e web)

| mecânica | onde (arquivo e símbolo) | rótulo | validação | pesquisa usa | versão |
|---|---|---|---|---|---|
| Estado e necessidades (fome, higiene, energia, humor, saúde, sujeira, sono; 1 tick = 1 min) | `digilab/state.py` `Estado`, `avancar_um_tick`; `web/app/motor/estado.ts` | EXECUTADO | gate (canônica `artifacts/`; paridade web `test/paridade_ts.test.mjs`) | sim | v1 |
| Ações do dono: 6 da v1 (`ACOES_V1`), 6 de treino, 3 de educação | `digilab/events.py` `AcaoUsuario`; `web/app/motor/tipos.ts` `AcaoDono` | EXECUTADO | gate | sim (treino e educação só nas runs V3+) | v1 / v4 |
| Ações do pet: 7 (`ocioso`, `dormir`, `comer`, `brincar`, `chamar_atencao`, `explorar`, `emburrar`) | `digilab/events.py` `AcaoPet`; `policy.efeito_da_acao_do_pet` | EXECUTADO | gate | sim | v1 |
| Motor e replay (event sourcing; `engine.py` congelado por sha256) | `digilab/engine.py` `Motor`, `reproduzir`; `protocol.ENGINE_SHA256_V0`; `web/app/motor/motor.ts` `Motor.aplicarEvento` | EXECUTADO | gate (`tests/test_protocol.py`, replays em todos os níveis) | sim | v1 |
| Instinto (regras por prioridade; prior do aprendiz; braço de controle) | `digilab/policy.py` `PoliticaInstinto`; `web/app/motor/bandit.ts` | EXECUTADO | gate (ablação `artifacts_ablacao/`) | sim | v1 |
| Bandit Thompson linear (11 entradas; feedback creditado só à última decisão; latência do chamado) | `digilab/policies/bandit.py` `PoliticaBandit`, `features`, `receber_acao_dono`; `web/app/motor/bandit.ts` | EXECUTADO | gate (canônica, ablação, confirmatória) | sim | v1 |
| Traços (EMA α = 1/288 da ação) | `digilab/tracos.py`; `ConfigTracos` | EXECUTADO | gate (arena v1) | sim (arena v1) | v1 |
| Orçamento exato de interações do dono (16/dia na v1; 298 em 14 dias com treino) | `digilab/treino.py` `CanalDeInteracao`; `treino_vida.orcamento_treino` | EXECUTADO | gate | sim | Py (web: `donos.ts` nos Cenários) |
| Donos sintéticos: atencioso, relapso, aleatório, incoerente (+ exigente, permissivo, lutador, treinador, personas) | `digilab/donos.py` `julgar_acao`; `treino_vida.DonoComTreino`; `donos_educacao.DonoComEducacao`; `personas.py`; `web/app/motor/donos.ts` | EXECUTADO | gate | sim | Py (web: Cenários, pets v5) |
| Memória curta B1 (4 entradas no bandit) | `digilab/memoria.py` `MemoriaCurta`, `PoliticaBanditMemoria` | EXECUTADO | gate (`artifacts_v1_memoria/`; efeito ~0,001 bit sem evidência, `bootstrap_sementes.json`) | só no protocolo `arena-v1-memoria` | v1 |
| Memória por espaços (4 curtos + 2 longos, relembrar em cronograma) | `digilab/memoria_espacos.py` `MemoriaEspacos`, `PoliticaBanditEspacos`; `web/app/motor/memoria.ts` | EXECUTADO | gate (`artifacts_v1_memoria_espacos/`: 6,9% dos motivos citam memória) | sim (personalidade, treino, educação) | v2 |
| Temperamento inato (4 eixos, `rng_ovo`) | `digilab/temperamento.py`; `ConfigTemperamento` | EXECUTADO | gate (`artifacts_v1_personalidade/`) | sim | v2 |
| Vínculo (atendimento, coerência, desejo; EMA) | `digilab/vinculo.py` `Vinculo`; `web/app/motor/vinculo.ts` | EXECUTADO | gate, **com defeito conhecido** (favorece o aleatório: `artifacts_linhagem/sinal_dono/resultado.json`; frente `v2-f0-vinculo`) | sim | v2 |
| Obediência com recusa e motivo (logística de vínculo, teimosia e conflito; `rng_obediencia`) | `digilab/obediencia.py` `MotorPersonalidade._aplicar_acao_usuario`; `motor.ts` `_desobedeceu` | EXECUTADO | gate (`artifacts_v1_personalidade/`: obediência 0,77–0,92 por dono) | sim | v2 |
| Desejo (necessidade × vontade; só leitura) | `digilab/desejo.py` `desejo_de` | EXECUTADO | gate (descritivo) | sim | v2 |
| Emoção filtrada pelo temperamento (só leitura; `modula_memoria` desligada) | `digilab/emocao.py`; `ConfigEmocao` | EXECUTADO | gate (equivalência: não muda nada, `artifacts_v1_habituacao/`) | sim (só leitura) | Py |
| Habituação (0,8^repetições) | `ConfigHabituacao`; `PoliticaBandit._peso_recompensa` | EXECUTADO | gate (`artifacts_v1_habituacao/`; só no protocolo próprio) | só `arena-v1-personalidade-habituacao` | Py |
| Motivo e expressão (honestidade: fator só se o aprendido mudou a escolha) | `digilab/motivo.py`, `expressao.py`; `web/app/motor/motivo.ts`, `expressao.ts` | EXECUTADO | gate (`artifacts_expressao/legibilidade.json`: 13–18% das decisões com fator) | sim (legibilidade) | v1 |
| Caráter pelo desvio da política (sondas fixas) | `digilab/evolucao.py` `carater`; `web/app/motor/carater.ts` | EXECUTADO | gate (E1, Etapa A) | sim | v3 (v1/v2: pelos traços, PROVISÓRIO) |
| Evolução: bebê → criança (cuidado), criança → adolescente (linha pelo caráter), adolescente → adulto (eixo complementar + sparring) | `digilab/evolucao.py` `evoluir`, `fracao_cuidado_bebe`; `combate_v2/v21/catalogo.py`; `motor.ts` `_evoluir` | EXECUTADO | gate (`artifacts_v21_pesquisa/`, E1); durações PROPOSTAS (`ConfigEvolucaoPesquisa`, `ConfigDuracoes`) | sim | v1 (web desde 2026-09-24) |
| Chamados do bebê (10 em 3 h: fome a cada 30 min, higiene 60, carinho 45; janela 15 min) | `ConfigEvolucaoPesquisa.chamados_bebe_min`; `evolucao.fracao_cuidado_bebe` (pós hoc, do log); `motor.ts` `_chamados` (ao vivo) | EXECUTADO | gate; **no Python nenhum dono vê os chamados** (548/548 ariscos, `artifacts_educacao/pets.json`) | sim (só o ramo) | v1 |
| Treino: 6 exercícios, fadiga, forçar, sobrecarga, pedido de pausa, enrolar | `digilab/treino_stats.py` `TreinoPet`; `treino_vida.py` `MotorTreino`; `web/app/motor/treino.ts` | EXECUTADO | gate (`artifacts_treino/`, S1/S2; `sobrecarga_forcar` calibrado) | sim (V3+) | v1 (web antes das runs) |
| Formas sombrias (sobrecarga ≥ 60 no adulto) | `ConfigSombrio`; `combate_v2/v21/bots.py` `SOMBRIOS` | EXECUTADO | gate S1/S2 (`artifacts_treino/bateria_sombria/gates.json`) | sim | v1 |
| Educação: chamado falso com janela (15 min), disciplina 0–100, bronca/petisco/prazo | `digilab/educacao.py` `MotorEducacao._slot`, `_falso`, `_aplicar_acao_usuario`; `ConfigEducacao` (`ligada`, padrão False); `motor.ts` `_travessuras` | EXECUTADO | gate (V3 `artifacts_educacao/`, confirmatória) | sim (V3, V3b, V3c, confirmatória, E1) | v4 |
| Aviso antes de sujar (banheiro), bronca sem motivo, acordar, superalimentação | `educacao.py` `_slot` (tipo aviso), `_sozinhas`; `ConfigEducacao` | EXECUTADO | gate (V3) | sim | v4 |
| Petisco (meio ganho, sem sujeira; cede ao chamado falso) | `educacao.py` `_petisco`; `AcaoUsuario.PETISCO` | EXECUTADO | gate (V3c: ceder com petisco sem efeito detectável, `artifacts_educacao_v3c/`) | sim | v4 |
| Lesão (20% na derrota), morte (20 lesões ou 6 h sem tratar), tratar lesão | `educacao.py` `_lutar`, `_conferir_morte`; `ConfigLesoes` (`ligada`, padrão False) | EXECUTADO | gate (V3: metade do efeito do atencioso vem das mortes; E1: 40/40 mortes "lesão sem tratar") | sim | v4 |
| Qualificação por vitórias (≥ 10 lutas, ≥ 80%) como condição de adulto | `ConfigLesoes.efeito_qualificacao`; `motor.ts` `_evoluir` | EXECUTADO | gate (V3) | sim | v4 |
| Sparring real no adolescente (10 lutas; 20 no lutador) | `ConfigSparring`; `experiments/run_educacao.py` `ticks_sparring` | EXECUTADO | gate (V3) | sim | v1 (web: contra o bot aleatório) |
| Herança (temperamento = média + N(0, 0,1); espécie dos pais; nada aprendido passa) | `digilab/heranca.py` `cruzar`; `web/app/src/heranca.ts` | EXECUTADO | gate E1 **FALHOU** como pesquisa (σ²_genoma 4,9%, `artifacts_linhagem/natureza_criacao/especie_fixa/resultado.json`); fica como mecânica de jogo | não mais | v4 |
| Modo livre gravado (`decisao_externa` no log) | `tools/decisor_livre.py`; `educacao.py` `_falso` | EXECUTADO | gate (V3c, lote `gemma2-9b-01`) | sim (V3c) | Py |
| Personas de dono por LLM (24, gravadas) | `digilab/personas.py`; `tools/gerar_personas.py` | EXECUTADO | gate (V3c: só o limiar de cuidado tem efeito) | sim (V3c) | Py |
| Confiança de combate e desgaste por rival (M1) | `digilab/confianca.py`; `ConfigConfianca` (`ligada`, padrão False); `web/app/motor/confianca.ts` | EXECUTADO (G1, G2) | **provisória**: G3–G6 não rodados, `docs/PLANO_ANALISE_M1.md` não existe; 10 parâmetros sem fonte | não (chave desligada) | v8 |
| Voz própria: história (fatos H/O/P/L), mentira com janela de fala, fala por gatilho | `digilab/historia.py`; `educacao.py` `_abrir_fala`, `_julgar_fala`; `ConfigMentira` (`ligada`, padrão False); `web/app/motor/historia.ts`, `mentira.ts`; `src/voz.ts` | EXECUTADO | gate de jogo (`artifacts_voz/rodada1..4`); avaliação cega do Matheus pendente | não (chave desligada) | v7 |
| Fala por LLM (moldura `fala-v6`) e fala livre (`gemma2:9b`, `livre-v2`/`v6`) | `servidor/fala_llm.py`, `fala_livre.py`; `digilab_fala_livre/` | EXECUTADO | gate de jogo (`artifacts_fala/`, `artifacts_fala_livre/rodada2/`); leitura das 50 falas e avaliação cega pendentes | não | web |
| Comando pelo chat (catálogo fechado de 9 ações; execução direta) | `servidor/fala_livre.py` (`livre-v8`); `web/app/src/acoes.ts` `validarComando`, `agir` | EXECUTADO | gate PROPOSTO passou (rodada 3: falsos positivos 0/60, imperativos 85%, `artifacts_fala_livre/comando/rodada3/`) | não | v7 |
| Escala de stats (E = vida do estágio × (1 + β × treino)) | `ConfigEscala` (`ligada`, padrão False); `web` `CESC`, `CESC_V6`, `CESC_V9` | EXECUTADO | gate (campanha na escala; v6 `artifacts_campanha/escala_v6/`; v9 `artifacts_equilibrio_geral/fase2/`) | não (painel normaliza o treino) | web (v6, v9) |

### 1.2 Combate e progressão

| mecânica | onde | rótulo | validação | pesquisa usa | versão |
|---|---|---|---|---|---|
| Arena v1 (5 ações em ciclo; stats dos traços) | `digilab/arena.py` | EXECUTADO | gate (canônica APROVADA por margem mínima, `artifacts/`) | sim (v1, memória, personalidade) | Py |
| Combate V2 (resolução pura; gambits; 5 bots + adaptativo; oráculo fora da linguagem) | `digilab/combate_v2/regras.py`, `gambits.py`, `bots.py`, `partida.py` | EXECUTADO | gate **REPROVADA** (G4, G5, `artifacts_combate_v2/gates.json`) | não (substituída pela V2C) | Py |
| V2C (correções C1–C4, bots redesenhados) | `ConfigCombateV2C`; `GAMBITS_V2C` | EXECUTADO | gate aprovado com exceção do atirador (G6b, `artifacts_combate_v2c/validacao_bots/gates.json`) | sim (base do V21C) | v1 |
| V2.1: formas (4 espécies × 15 formas), técnicas por linha, passivas, condições por estágio, listas de 3/5/8 regras | `digilab/combate_v2/v21/catalogo.py`, `regras.py`, `gambits.py` (`CONDICOES_POR_ESTAGIO`, `max_regras`), `bots.py`; `web/app/motor/combate.ts`, `catalogo.ts`, `bots.ts` | EXECUTADO | gate E1–E5 **REPROVADA** (V2.1 original); V21C APROVADA COM RESSALVAS (E2, E4, G6b, G8 aceitas) | sim (V21C: V3, E1, confirmatória; `campanha.REGRAS_CAMPANHA`) | v1 |
| V21D (reequilíbrio, 4 chaves) | `ConfigCombateV21D`; `experiments/validar_v21d.py` | EXECUTADO | gate APROVADA, furioso exceção (`artifacts_combate_v21c/validacao_v21d/criterios.json`) | só no painel do E1 (`natureza_criacao_v21d`): compressão NÃO VERIFICADA | v6–v8 |
| V21E (equilíbrio geral, 5 chaves de lista) | `ConfigCombateV21E`; `bots._lista_v21e`; web `CV21E` | EXECUTADO | gate fase 4 (`artifacts_equilibrio_geral/fase4/`): M-A1–A4 passam; M-C1 e E3 do contra-golpe exceções aceitas | não | v9 |
| Campanha contra NPCs (Campina, Torre, Cidadela; escada K1–K4) | `digilab/campanha.py`; `ConfigCampanha`; web `bots.CAMPANHA*` | EXECUTADO | gate (`artifacts_campanha/`: todo pet treinado vence) | sim (NPCs do sparring por nome; `rival_padrao`) | v1 |
| Treino vale 3 em combate | `ConfigTreino.peso_ponto_combate` | EXECUTADO | gate (calibração da progressão) | sim | v1 |
| Pesquisa V2.1: pet de pesquisa evolui e luta com adultos | `experiments/run_pesquisa_v21.py` | EXECUTADO | descritivo (`artifacts_v21_pesquisa/`, 5 sementes) | sim (histórico) | Py |
| Painel B (8 formas × 4 espécies, condição neutra) e análise de poder | `experiments/run_poder.py`, `analisar_poder.py`; `ConfigArenaPesquisa.condicao_neutra` | EXECUTADO | gate (`artifacts_poder/`, `artifacts_confirmatoria/`) | sim | Py |
| Gambits híbridos: o PET aprende a lista; o dono trava e veta | `web/app/motor/gambits_pet.ts` `GambitsPet.aprender`, `intervir`; evento `g`; `GA` | EXECUTADO (web) | **provisória** (PROVISÓRIO declarado; sem protocolo, sem gate de que separa donos) | não (Python: listas fixas) | web (todas as versões) |
| Mega (estágio próprio; vínculo ≥ 0,4) | `CMG`; `Motor.requisitosMega` | EXECUTADO (web) | provisória (`artifacts_campanha/mega/limiar_vinculo.json`: aleatório 5/6 × atencioso 3/6) | não | v5 |
| Tamer: medalhas, trava da evolução (1/3/5) | `web/app/src/tamer.ts`; `motor/medalhas.ts`; evento `u`; `CMD` | EXECUTADO (web) | provisória (sem equilíbrio) | não | v6 |
| Seis arenas com líderes e regras | `web/app/motor/arenas.ts` `ARENAS`, `FATOR_LIDER_V9` | EXECUTADO (web) | gate de jogo (`artifacts_campanha/arenas/validacao.json`; v9 em `artifacts_equilibrio_geral/fase4/`) | não | v6 |
| Itens do Tamer (chips de stat e de regra, cartas) | `web/app/motor/itens.ts`; eventos `i`, `k`; `CIT`, `CIT_V9` | EXECUTADO (web) | gate fase 4 M-E1 (v9); v6 sem equilíbrio | não | v6 |
| Liga dos Líderes, Torre, Palácio, Fábrica, Salão | `web/app/motor/liga.ts`, `instalacoes.ts`, `fabrica.ts`, `salao.ts`; evento `f` | EXECUTADO (web) | gate fase 4 (M-C1 exceção; M-C2, M-C3, M-D1–D3 passam) | não | v6 |
| Limite de turnos do desafiado | `combate.ts` `desafiadoDaVersao` | EXECUTADO (web) | gate fase 4 | não | v6 |
| Cenários (dois pets com donos simulados; 100 lutas) | `web/app/motor/donos.ts` `treinarPet`; `src/telas` | EXECUTADO (web) | ferramenta de inspeção, não resultado | não | v5 |
| Jornada (brasão → ovo → Liga → conclusão) | `web/app/src/jornada.ts` | EXECUTADO (web) | sem gate (é tela) | não | v6 |

### 1.3 Só pesquisa (runs e análises)

| run / análise | onde | rótulo | resultado | artefato |
|---|---|---|---|---|
| Canônica v1 | `experiments/run_arena.py`, `configs/canonico.json` | EXECUTADO | APROVADA por margem mínima (JSD 0,0204 vs 0,02) | `artifacts/divergence.json` |
| Ablação treino × cuidado | `configs/ablacao.json` | EXECUTADO | efeito do treino 0,14 [0,00; 0,28]; superada | `artifacts_ablacao/metrics.json` |
| Memória B1, espaços, personalidade, habituação | `configs/memoria*.json`, `personalidade*.json` | EXECUTADO | APROVADAS; centrais INCONCLUSIVOS | `artifacts_v1_*/` |
| V3 exploratória, V3b, V3c | `run_educacao.py`, `configs/educacao*.json`, `docs/PLANO_ANALISE_V3.md` | EXECUTADO | atencioso − aleatório +0,121 [+0,066; +0,175]; metade pelas mortes | `artifacts_educacao*/resultado.json` |
| Confirmatória | `run_confirmatoria.py`, `docs/PLANO_ANALISE.md` | EXECUTADO | **REFUTADA** (−0,034 [−0,072; +0,006], 160 ovos) | `artifacts_confirmatoria/resultado.json` |
| E1 natureza × criação; dono × ambiente | `run_natureza_criacao.py`, `analisar_dono_ambiente.py` | EXECUTADO | gate FALHOU; forma explica 96% da taxa | `artifacts_linhagem/natureza_criacao/`, `dono_ambiente/` |
| V21D no painel, Etapa A (sinal do dono), Etapa B (canal) | `analisar_v21d.py`, `sinal_dono.py`, `analisar_canal.py` | EXECUTADO | compressão NÃO VERIFICADA; SINAL PRESENTE (só eixo resistente); CANAL NÃO ABERTO | `artifacts_linhagem/natureza_criacao_v21d/`, `sinal_dono/`, `natureza_criacao_canal/` |
| Pergunta do efeito do dono | `docs/LEITURA_CONSOLIDADA_DONO.md` | DECIDIDO | **ENCERRADA** (2026-10-01) | — |
| Plano da V2 (aprendiz com lobos; ambiente mínimo) | `docs/PLANO_V2_PESQUISA.md` (PR #102) | ESPECIFICADO / PROPOSTO | gates G1–G6 PROPOSTOS | — |
| Interação do jogador e corpo do pet | `docs/TODO_INTERACAO_CORPO.md` | IDEIA | — | — |
| Dwarf Fortress → V2 (slots, memória nuclear, faceta × valor, duas prioridades, estresse) | `docs/futuro/dwarf_fortress.md` | IDEIA / contexto | — | — |
| Combate 1×1 em tempo real; PvP com ghost | `CLAUDE.md` (stand-by); `TODO_INTERACAO_CORPO.md` | IDEIA | — | — |

**Suíte de testes** (só para confirmar que nada mudou nesta tarefa): `python -m pytest tests/ -q` na worktree `v2-f0-inventario`
(Windows, Python 3.13, 2026-10-01): **571 passaram, 1 pulado**, 6 min 38 s; 48 arquivos em `tests/` (o `CLAUDE.md` ainda diz 290; seção 5).

---

## 2. As decisões do pet hoje

### 2.1 Quando o pet escolhe, quantas vezes por dia, e se o dono muda o resultado

| momento | quem decide, como | quantas por dia | o dono muda o resultado? | o aprendiz vê a decisão? |
|---|---|---|---|---|
| **Ação de vida** (7 ações) | a política (`Politica.agir`), com `rng_politica`; instinto por regras, bandit por Thompson | **96** (a cada 15 ticks; `Config.intervalo_decisao_ticks`) | **sim, mas pouco e só depois**: elogio/bronca creditados **só à última decisão** (`PoliticaBandit.receber_acao_dono`); latência do chamado (janela 120 ticks). Na canônica o atencioso dá em média 93,6 elogios e 49,2 broncas em 14 dias (≈10 por dia para 96 decisões; `artifacts/vidas/atencioso@*.politica.json`, campo `recompensas`); o relapso 23,2 e 16 | sim: é a única decisão que entra no aprendizado |
| **Aceitar ou recusar o cuidado** (alimentar, limpar, brincar, acariciar) | sorteio na `rng_obediencia` com p = logística(vínculo, teimosia, conflito) (`obediencia.MotorPersonalidade`) | uma por ação de cuidado do dono: até ~16 na v1 | sim, pelo vínculo (que ele move) e pelo conflito (cuidado fora de hora) | **não**: a política recebe a ação do dono igual (recusa não corta aprendizado); nenhum peso muda por recusar |
| **Chamado falso** (travessura) | sorteio na `rng_travessura` com f(disciplina, petiscos) nos slots do cronograma (`MotorEducacao._slot`, `_falso`) | slots: 44 na criança, 33,6 no adolescente, 28 no adulto (`ConfigEducacao.intervalos_chamado_min`); janelas abertas de fato numa vida de 14 dias da V3: atencioso 6,3 falsos (todos corrigidos; f cai a 0 depois de 3 broncas certas), permissivo 55,8 (cede), relapso 25,5, aleatório 11,5 (`artifacts_educacao/pets.json`, `educacao`) | **sim**: bronca sobe a disciplina (→ ε do lutador), petisco reforça, prazo vencido derruba | **não**: a política não vê a janela; só o contador `disciplina` muda |
| **Aviso de banheiro** | slot fixo a cada 120 min (`tipo_slot_aviso`) | 12 | só cuidado: atender evita sujeira; ~100 avisos por vida no atencioso, 84 ignorados no relapso (`artifacts_educacao/pets.json`) | não |
| **Mentir** (fala com janela) | sorteio na `rng_mentira` com p(honestidade, disciplina, impunes) (`MotorEducacao._abrir_fala`) | 12 slots na pesquisa (`ConfigMentira.intervalo_fala_min`); no jogo, por gatilho (≤ 1 a cada 2 h, `src/voz.ts`) | sim (bronca, petisco, elogio, prazo) | não; e a chave está desligada na pesquisa |
| **Enrolar no treino / pedir pausa** | enrolar = `rng_obediencia`; pausa = `fadiga ≥ 40` (determinístico, vira Desejo) | sessões-alvo 10/8/5 por dia por estágio (`ConfigTreino.sessoes_alvo_dia`); 74 em 14 dias (`orcamento_treino`) | sim: o dono escolhe treinar, respeitar a pausa ou forçar (sobrecarga → sombria; vínculo −0,05) | não |
| **Decisão de combate** (ação por turno) | a primeira regra da lista de gambits cujas condições valem; ε → ação legal uniforme (`v21/gambits.decidir_gambits`); pesado automático | por luta: mediana 22 turnos, teto 40 (`artifacts_combate_v21c/validacao/gates.json`, `ConfigCombateV2.max_turnos`); na vida de pesquisa 10 lutas de sparring (20 no lutador), no adolescente | **Python**: só por fora (forma, treino ×3, ε da disciplina: `educacao.epsilon_pet`, condição física). **Web**: trava e veto (`g`), itens (`i`, `k`), escolha do rival e da hora (`l`), além dos mesmos | Python: **não** (lista fixa por forma); web: sim (nota por regra depois de cada luta, `GambitsPet.aprender`) |
| **Chamado do bebê** | não é decisão: horário fixo (10 chamados em 3 h) | — | só cuidado: ≥ 80% atendidos → sereno. No Python nenhum dono vê o chamado: **548 de 548 pets vivos da V3 são ariscos** (`artifacts_educacao/pets.json`); na web os donos simulados atendem | não |
| **Evolução** (ramo, linha, forma) | não é decisão: função do log (cuidado, caráter nas sondas) | 3 por vida | só pelo que o aprendizado deixou no caráter; o ambiente decide mais que o dono (κ de Fleiss ≈ 0, `artifacts_linhagem/natureza_criacao_v21d/especie_fixa/analise_plano.json`) | — |
| **Desejo / vontade** | calculado da posterior; só leitura | — | não (alimenta o vínculo) | — |

### 2.2 O que a tabela mostra

1. **Há uma decisão só que o aprendiz toma e com a qual aprende: a ação de vida.** Ela é condicionada ao próprio estado
   (8 valores + tempo sem cuidado); não existe no vetor de observação nada que o dono tenha **posto** no mundo. O dono muda
   o estado e dá feedback; ele não cria situações.
2. **As decisões "com consequência onde o dono importa" existem, mas estão fora do aprendiz.** Recusa, travessura, mentira e
   enrolar são sorteios sobre contadores (vínculo, disciplina, fadiga). O dono muda os contadores; nenhum peso da política muda.
   É por isso que o efeito do dono aparece pelo cuidado (`docs/LEITURA_CONSOLIDADA_DONO.md`, cadeia 2–5) e não pelo ensino: o
   único canal de ensino são ≈10 feedbacks por dia creditados à última das 96 decisões.
3. **A regra "B2 recusa não existe" do `CLAUDE.md` continua certa no sentido que importa:** a recusa existe como sorteio na
   hora da ação do dono (`MotorPersonalidade`), não como ação do pet que a política escolhe.
4. **No combate, o pet do Python não decide nada que o dono tenha ensinado.** A lista é a canônica da forma; o dono entra pelo
   ε da disciplina (0,05 a 0,15) e pelo treino. A aprendizagem de gambits, única mecânica em que o pet aprende com a luta e o
   dono intervém (trava/veto), **é só da web e é provisória**.
5. **Volume:** 96 decisões de vida por dia contra 28–44 slots de travessura, 12 avisos, 5–10 sessões de treino e, na pesquisa,
   10 lutas por vida. A V2 (H1) quer mais decisões em que o dono importe; hoje a conta é ≈10 feedbacks em 96.

---

## 3. Candidatas à interação mínima da fase 1a

Critérios, do plano da V2 e desta tabela: (a) é uma **decisão da política** (consome `rng_politica`, entra nas entradas da
observação, tem motivo), não um sorteio sobre contador; (b) **o dono cria a situação** (põe, tira, oferece) e **julga**; (c) a
**consequência** chega ao pet e pode mudar decisões futuras; (d) **separável do cuidado** (G5: a divergência tem de se manter
sem mortes nem lesões; a consequência não pode passar pela cadeia fome/higiene/energia → saúde → morte); (e) **custo no motor**
pequeno: camada por cima (`engine.py` intacto), um evento novo no log, sem corpo 2D; (f) **paridade web** com versão de pet nova.

Restrição comum a todas, encontrada no inventário: **uma ação nova do pet não pode entrar em `events.AcaoPet`** sem mudar a
canônica (o bandit tem um braço por ação, `tracos.ORDEM_TRACOS = tuple(AcaoPet)`, o desejo e as sondas iteram o enum). A ação
nova tem de ser da política da V2 (lobos) ou um **alvo** da ação existente (ex.: `brincar` com a bola), com `test_canonico_intacto`
e os gabaritos v1–v9 passando.

| candidata | o que o pet percebe | o que decide | consequência | o que mudaria no motor | risco de virar canal de cuidado |
|---|---|---|---|---|---|
| **A. Bola** (objeto de brincar posto pelo dono) | "há uma bola" (1 entrada: presente/idade do objeto); opcionalmente a distância em 2 ou 3 passos | ir até a bola e brincar, ou ignorar e seguir a própria ação | humor sobe mais que o `brincar` sozinho, energia cai (como hoje: `humor_por_tick_brincando`, −0,02 de energia); à noite ou cansado, o dono coerente repreende (`donos.julgar_acao` já tem a regra para brincar/explorar); a bola some depois de N min ou quando o dono tira | camada `MotorAmbiente` sobre o `MotorEducacao`: estado do objeto fora do `Estado`; evento `objeto` (dono põe/tira, tipo, tick); 1–2 entradas na observação; a ação é `brincar` **com alvo** (sem braço novo) ou ação própria da política dos lobos; web: evento novo no registro e versão de pet reservada pelo coordenador | **baixo**: humor e energia não entram em `Estado.em_privacao` (só fome, higiene, energia), então a bola não leva à morte; a energia cai pouco. O dono aleatório põe a bola ao acaso: controle natural |
| **B. Comida posta no cenário** (a do TODO) | "há comida" (tipo: refeição ou petisco; idade) | aproximar e comer, ou ignorar; comer saciado | fome sobe (como `alimentar`/`petisco`); comer com fome ≥ 0,9 custa saúde (`ConfigEducacao.custo_saude_superalimentacao`, já existe); a comida estraga depois de N min (sujeira +1) | o mesmo que A, com a comida no lugar da bola; a ação é `comer` com alvo | **alto**: fome é o eixo do cuidado. O atencioso que põe comida quando o pet tem fome está alimentando: a decisão vira cuidado. Só separa do cuidado com duas travas: a comida posta **nunca é a única fonte** (o `alimentar` continua) e **nunca atende necessidade abaixo do limiar** (abaixo de 0,35 o pet come sempre, como hoje `fome < 0,25 → chamar`); aí a decisão fica restrita a "comer sem fome", que é a superalimentação |
| **C. Obstáculo** | posição própria, do objeto e do destino | contornar, tentar mover, desistir | custo de energia; acesso (ou não) ao destino | exige espaço (posição, alcance, colisão) no motor e na web: é o corpo 2D inteiro, não a interação mínima | baixo, mas custo alto e sem ligação com o que o pet já faz |
| **D. Equipamento de treino deixado disponível** | "há equipamento" (exercício) e a própria fadiga | treinar sozinho ou não | pontos de treino, fadiga, sobrecarga (→ sombria), como as sessões de hoje | o treino já existe como ação do dono com o pet "enrolando" por sorteio; virar decisão do pet troca quem inicia a sessão (`MotorTreino._aplicar_acao_usuario` → decisão na política) | **médio**: sobrecarga e sombria são consequência de forçar, que é o eixo "cuidado" do treino (vínculo −0,05); e o treino é normalizado no painel, então não aparece na arena |
| **E. Área de descanso** | "há um lugar de dormir" | ir dormir lá ou não | energia (como `dormir`) | pouco novo: `dormir` já é decisão da política | baixo, mas não acrescenta decisão |
| **F. Convite ou pedido do dono como decisão da política** (as "duas prioridades" do DF) | "o dono pediu X" (tipo do pedido pendente) | atender o pedido ou seguir a própria ação | o cuidado só acontece se o pet for; o pedido expira | transforma toda ação de cuidado do dono em proposta: muda o significado do orçamento, os donos sintéticos e a comparabilidade com a v1; é a peça da fase 1b (lobo de impulsos), não um ambiente mínimo | **muito alto**: um pet que não vai comer morre; a recusa hoje já é descartada no estado por isso |
| **G. Escolha entre duas comidas** (refeição × petisco) | dois objetos | qual comer | preferência aprendida; petisco meio ganho e superalimentação | igual a B com dois tipos | alto, pelos mesmos motivos de B |

**Leitura.** A e B são as únicas que cumprem (a), (b), (c) e (e) ao mesmo tempo. Diferem em (d): A fica fora da cadeia da saúde
por construção; B fica dentro e só sai dela com travas que reduzem a decisão a "comer sem fome". C é o corpo 2D (fora da 1a); D e E
repetem decisões que já existem; F e G são variantes da 1b ou de B.

Para A, o que o gate G3 mediria: a JSD entre donos coerentes com a bola presente × ausente, nos estados de sonda; e o motivo
"porque a bola estava lá" conta para o G4. O controle H0 (só cuidado) é o braço sem bola.

---

## 4. Recomendação

A interação mínima da 1a deve ser **a bola: um objeto de brincar que o dono põe e tira, que o pet percebe como entrada da
política e decide usar ou ignorar, com consequência em humor e energia**, porque é a única candidata com decisão da política,
situação criada pelo dono e consequência fora da cadeia fome/higiene/energia → saúde → morte, o que deixa o gate G5 satisfazível
por desenho e não por sorte. A comida posta no cenário é a alternativa com mais consequência, mas ela é o eixo do cuidado e só
se separa dele com travas que a reduzem a "comer sem fome"; recomendo guardá-la para depois da bola passar G3–G5, se passar.
Nos dois casos a ação entra como alvo de uma ação existente ou como ação da política dos lobos, nunca em `AcaoPet`, e com
versão de pet própria na web.

**Pergunta ao Matheus:** aprova a bola como interação mínima da 1a, ou prefere a comida posta no cenário (com as duas travas:
nunca única fonte de comida e nunca abaixo do limiar de fome), ou outra da tabela?

---

## 5. Divergências entre documento e código encontradas

Registradas também em `docs/REGISTRO_DESVIOS.md` (seção desta tarefa). Nenhuma muda resultado; são correções de texto para quem
mantém os arquivos (as do `CLAUDE.md` são do coordenador).

1. `CLAUDE.md`, mapa do repositório e comandos: "290 testes". A auditoria contou 538 passados e 1 pulado em `3fe6d76`; nesta
   worktree (`83fc08f`) são 571 passados e 1 pulado.
2. `CLAUDE.md`, "Ambiente do usuário: Windows, pasta `D:\Trab\digilab\v1`": desde 2026-09-30 o trabalho é em `D:\Trab\digilab\v2`
   e nas worktrees (`docs/V2_TRABALHO_PARALELO.md`).
3. `web/app/motor/confianca.ts`, comentário de cabeçalho: "Só os pets v5 usam". O motor aplica a confiança nos pets **v8** em diante
   (`motor.ts`, `versao >= 8`; `CLAUDE.md`, seção M1).
4. `web/app/motor/donos.ts`, comentário: "a evolução não existe no Python". Existe (`digilab/evolucao.py`, função pura do log); o
   que não existe no Python é o dono sintético **ver** o chamado do bebê ao vivo (ele é contado depois, por `fracao_cuidado_bebe`).
5. `docs/TODO_INTERACAO_CORPO.md` e `docs/PLANO_V2_PESQUISA.md`: "o aprendido muda a política em cerca de 0,02 bit". O 0,02 bit é a
   JSD **entre braços** (0,0204, `artifacts/divergence.json`); a distância ao instinto é ≈0,03–0,05 bit (`CLAUDE.md`, "Estado
   atual"). Importa porque o G3 da V2 usa 0,02 como referência: a referência é a divergência entre donos, e o texto está certo
   nesse uso; só a frase "muda a política" é imprecisa.
6. `01_CURRENT_STATE.md` §11 descreve a web com "v6+ na V21D": os pets v9 lutam na V21E (o acréscimo A do próprio documento já
   registra). Sem correção a fazer no repositório.

Conferido e **sem divergência**: as linhas e símbolos citados na auditoria (`policy.py:66-132`, `bandit.py:146-161`,
`state.py:103-106`, `events.py:62-69`, `desejo.py:51-68`, `heranca.py:78-94`, `evolucao.py:130-155`, 12 tipos de evento em
`tipos.ts`), os números de `ConfigEducacao`, `ConfigLesoes`, `ConfigConfianca`, `ConfigMentira`, `CED`, `CLE`, `CCF`, `CMEN`,
`CMG`, e a ausência de `docs/PLANO_ANALISE_M1.md`.

---

## 6. Fora desta tarefa

Desenhar ou implementar a interação (vira tarefa própria, `v2-a1-<interacao>`, com plano de análise antes de qualquer run); o
vínculo (`v2-f0-vinculo`); os lobos (`v2-l0-lobos`); qualquer mudança de jogo.
