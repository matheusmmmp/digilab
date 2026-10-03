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
| `digilab/policies/lobos.py` | **V2, L0**: `PoliticaLobos`, o aprendiz da V2 com lobos nomeados (percepção, memória e emoção, impulsos, decisão); pesos inteiros em ponto fixo iniciados no prior do instinto, aprendizado desligado (`ConfigLobos`); vida byte a byte igual à do instinto (seção "V2, L0" no fim) |
| `digilab/policies/camada_unica.py`, `experiments/run_v2_l1.py`, `experiments/configs/v2_l1/` | **V2, L1**: o lobo de decisão aprende (feedback como vantagem, inteiros; `ConfigLobos.aprendizado_ligado`), o controle de capacidade equivalente sem lobos (`PoliticaCamadaUnica`), e o orquestrador da calibração/validação (G3, G3-T, G4, G5, G6, acoplado, norma de reação, educação) → `artifacts_v2_l1/` (seção "V2, L1" no fim) |
| `experiments/bancada_v2.py`, `experiments/configs/bancada/` | **V2, BANCADA**: o orquestrador dos braços da pergunta maior (P0 só herdado, P3 feedback do dono; P1/P2/P2e falham alto até o N3/N5) sobre o mesmo aprendiz, a vida = (genoma, mundo, dono, braço, semente), o modo acoplado e as medidas (`metrics.desempenho_no_ambiente`, `custo_da_plasticidade`, `tabela_braco_condicao`) (seção "V2, BANCADA" no fim) |
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
- **IDEIA: mecânicas de Dwarf Fortress → V2** (`docs/futuro/dwarf_fortress.md`, Matheus, 2026-10-01): contexto das peças (slots 8+8,
  memória nuclear, faceta × valor, duas prioridades, estresse em duas escalas) para o planejamento da V2; a v1 não recebe nada. O
  desenho (`docs/futuro/proposta_df.md`) só depois do gatilho da tarefa, junto com a fase 1b do plano da V2. DF é pista, não evidência.
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
