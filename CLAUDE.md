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
| `digilab/policies/bandit.py` | Thompson sampling linear; prior = distribuição exata da `PoliticaInstinto` via sonda de rng + Gumbel-max |
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
| `tests/` | 290 testes; `test_canonico_intacto.py` roda a canônica V1 (~70 s) e `test_motivo_expressao.py` a bateria V2 (~50 s); `test_combate_v21.py` confere `config.py` contra os JSONs de `docs/` |

## Comandos

```bash
python -m pytest tests/ -q                                                   # 290 testes, ~4 a 7 min
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

Ambiente do usuário: Windows, pasta `D:\Trab\digilab\v1`. Python 3.10+.

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
- **Pendente**: revisão humana de `artifacts_fala/ollama_qwen2.5-3b_fala-v6_s20260928/revisao.csv`
  (50 falas aprovadas). Sem ela, a fala por LLM continua desligada por padrão.

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
- Voz própria no jogo (parte 4, 2026-09-30): pets **v7** (`VERSAO_PET = 7`: v6 + voz própria) com janela de fala, mentira (`CMEN`) e evento `fl` (o `f` é da Fronteira); `motor/historia.ts` e `motor/mentira.ts` conferidos contra o Python (`experiments/exportar_gabaritos_voz.py` → `test/gabaritos/voz_python.json`, `tests/test_gabaritos_voz.py`); gatilhos e ritmo em `src/voz.ts`; servidor com `voz: true` (livre-v6, autocorreção, verif-v5, corpus, almanaque). Avaliação: `artifacts_voz/rodada1..4` (`experiments/avaliar_voz.py --rodada N`).
- Voz própria (DESIGN_VOZ_PROPRIA, parte 2): `livre-v3` e `verif-v4` ao lado das versões do jogo; fatos H/O/P/L, mentira F (`mentira.py`), almanaque W (`almanaque.json`), corpus de espécies (`corpus.py`, `corpus_especies.json` = EXEMPLO com 2 espécies) e filtro contra repetir citação.
- **Comando pelo chat (2026-09-30, `docs/TAREFA_COMANDO_CHAT.md`, decisão do Matheus):** a regra "o que o jogador escreve não ensina o
  pet" **deixa de valer para o comando, mediado por um catálogo fechado**; fora do catálogo o texto continua sem efeito. Na CONVERSA
  dos pets v7+ (`voz: true`) o servidor usa o prompt `livre-v7` (= v6 + bloco COMANDO) e devolve `comando`: uma das 9 ações de
  `AcaoDono` (`web/app/motor/tipos.ts`) ou `null`; `saida.ler` falha alto fora do catálogo (fala genérica, comando null). A LLM só
  propõe: o app valida de novo (`src/acoes.ts`: catálogo, pet nascido e vivo, ações v4 só em pets v4+, tratar só com lesão), mostra um
  chip no balão da resposta ("Alimentar?") e **só o toque** grava o evento `d` de sempre pelo mesmo caminho do botão (`acoes.agir`,
  usado pela tela do Pet, pelos atalhos e pelo chip). No registro do pet não entra nada da LLM: replay, assinaturas v1–v8, gabaritos e
  paridade iguais; sem o modo livre gravado. O chip some com outra mensagem, outra fala do pet ou 60 s. Log de apresentação versão 2
  (`comando`, `comando_executado`; lê a 1). Treino, luta, itens, fala espontânea e pets sem voz (v1–v6, `livre-v2`) ficam fora.
  Avaliação: `python experiments/avaliar_fala.py --livre --comando [--rodada 1|2]` → `artifacts_fala_livre/comando/rodada1/` (sem o
  estilo da espécie) e `rodada2_estilo/` (com); 60 mensagens em `situacoes.MENSAGENS_COMANDO` × 3 sementes; gate PROPOSTO: falsos
  positivos ≤ 5% nas negativas e imperativos ≥ 80%. **Execução direta (sem chip) só com decisão do Matheus depois do gate.**

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

- Evolução canônica: o limiar de vínculo do Mega baixou para 0,4, mas o vínculo ainda favorece o dono aleatório (5 de 6
  vidas viram Mega, contra 3 de 6 do atencioso). Rever o desenho do vínculo resolveria de vez.

- Fala por LLM: repetida com outra semente (2026-09-29, `artifacts_fala/ollama_qwen2.5-3b_fala-v6_s20260929/`):
  92% aprovadas, nenhuma barrada por fator fora da lista. Pré-leitura (coluna própria no `revisao.csv`): nenhuma
  das 50 cita causa fora dos fatores (desde a v4 a LLM só escreve a moldura); 9 tinham caractere quebrado do
  qwen 2.5 3b, agora barrado na validação da moldura. Falta a leitura do Matheus (coluna s/n).

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
