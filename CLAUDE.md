# CLAUDE.md — Digilab

Contexto para o Claude Code. Este arquivo diz só o que muda o que o Claude faz; o resto está nos documentos da seção "Onde está o quê".

## O que é

Projeto de pesquisa pessoal do Matheus (**não é a pesquisa de mestrado dele**; nunca associar ao mestrado nem ao programa): um pet virtual
evolutivo com IA, inspirado em Tamagotchi e Digimon.
- **A direção (2026-10-24):** o produto jogável vem primeiro (`docs/PRODUTO_VISAO.md`), e o DigiBrain caminha para um cérebro
  **modular** (`docs/ARQUITETURA_DIGIBRAIN_MODULAR.md`). O cérebro A (os lobos em `digilab/policies/lobos.py`) é a linha de base, o
  controle e o fallback condicionado, não o cérebro final.
- **A pesquisa** fica no Python e serve ao produto e aos mecanismos do DigiBrain: um pet com corpo químico, objetos, outro pet e um
  dono.
- **O jogo** fica em `web/app/` e roda hoje o A v11. O modular entra por módulos, cada um com paridade.
- **Onde a V3 está agora:** `docs/PAINEL_V3.md`, uma página. O plano é o `docs/PLANO_V3.md` (as trilhas C cérebro, L layout e B
  batalha). A V2 está congelada na tag `v2-final`, com o estado de cada tarefa em `docs/FECHAMENTO_V2.md`.

## Regras não negociáveis

- **Não aumentar escopo.** Fazer só o que a tarefa pede. As exceções de escopo já autorizadas estão em `docs/historico/claude/fundacao.md`.
- **Falhar alto, não em silêncio:** `raise` em vez de `dropna`, valor padrão ou `except: pass`. Evento desconhecido no log levanta erro.
- **Determinismo é requisito:** mesma semente e mesmo log dão o mesmo resultado, até o último float.
  - **Se um teste de replay quebrar, pare tudo e conserte** antes de qualquer outra coisa.
  - Exceção decidida: o **modo livre gravado**. A LLM e o acaso real decidem ao vivo, mas toda saída entra no log como evento, e o replay
    lê o evento. O modo determinístico continua sendo o padrão e o único válido para resultado, protocolo com hash e paridade Python/web.
- **RNG de ambiente e de política separadas.** Trocar de política não pode mudar o mundo. Cada fluxo novo tem a sua rng, derivada por
  `derivar_semente`.
- **Métricas existem uma vez só:** `digilab/metrics.py`.
- **Nenhum número em resultado sem artefato em disco que o produza.**
- **Parâmetros ficam em `digilab/config.py`**, cada um com status PROPOSTO ou DECIDIDO e com fonte (ou SEM FONTE). Nenhum número mágico.
- **`digilab/engine.py` não muda.** O sha256 dele está congelado em `protocol.py` (`ENGINE_SHA256_V0`), e teste e preflight conferem.
- **Mecânica nova entra atrás de chave desligada.** Desligada, a vida de hoje sai byte a byte. O gabarito das vidas de hoje é gravado num
  commit próprio, antes da mudança, e um teste confere.
- **Português** nos comentários, docstrings e documentos; **sem acentos em identificadores**.
- **Só biblioteca padrão no pacote `digilab/`** (o preflight confere pela AST). `pytest` só nos testes.
- **LLM liberada** quando a tarefa pedir.

## Pesquisa: o método

- **Nenhuma run sem plano de análise registrado antes** (`docs/PLANO_ANALISE_V3_*.md`, ou um adendo ao
  `PLANO_ANALISE_V2_*` de uma frente herdada, commitado antes da primeira vida).
- **Sementes:**
  - os testes usam 101…505 e as sementes pequenas dos próprios testes;
  - toda run de pesquisa usa uma faixa reservada em `experiments/bancada/faixas.py` (`FAIXAS_RESERVADAS`, reexportada pelo
    `experiments/bancada_v2.py`), com a fonte;
  - uma faixa nova é pedida ao coordenador e entra na tabela antes da run;
  - as faixas em `FAIXAS_QUEIMADAS` não voltam.
- **Calibração e validação:** a calibração usa só as sementes dela. A validação roda **uma vez**, e nada se ajusta olhando para ela.
  Gate que falha não para a V3: o resultado negativo é registrado como está.
- **A máquina (V3-D8):** no máximo 4 processos por run e uma run de pesquisa por vez (as medições do combate contam), até o teste
  da BIOS FP.
- **Referências:** só as verificadas (a skill `literatura-digilab`). Onde não há, escrever SEM FONTE. Nunca alegar novidade.
- **Números novos são PROPOSTOS** até o Matheus decidir. Toda decisão levada a ele vai com a recomendação e o custo de errar.
- **Decisões que valem:**
  - a pergunta do efeito do dono está encerrada (`docs/LEITURA_CONSOLIDADA_DONO.md`): só se reabre com pergunta nova sobre o aprendiz;
  - o bandit está congelado e só reproduz a v1;
  - o produto jogável vem primeiro, e o DigiBrain é modular; o A é a linha de base, o controle e o fallback condicionado (2026-10-24;
    substitui o M6 e a regra "um DigiBrain na web, o A" de 2026-10-01).

## Trabalho em paralelo

**"V3" nos documentos antigos não é a fase nova:** a V3-9, a V3-3/4, o `digibrain_v3` e o `TAREFA_V2_V3` são da V2; o
`PLANO_ANALISE_V3.md` é da v1. O glossário completo está no `docs/PLANO_V3.md`, seção 8.

- **A pasta `D:\Trab\digilab\v3`** é só a referência da `main`: ninguém troca o branch dela. A `D:\Trab\digilab\v2` fica congelada
  como referência da V2.
- **Cada frente trabalha numa worktree própria,** `D:\Trab\digilab\v3-<frente>`, no branch `v3-<frente>`, criada de `origin/main`.
- **A tarefa de cada frente** fica em `docs/TAREFA_V3_<FRENTE>.md`; o modelo está em `docs/modelos/TAREFA_V3_MODELO.md`
  (`python tools/nova_tarefa.py <FRENTE> --fase V3 ...`). As frentes herdadas da V2 continuam no `TAREFA_V2_*` delas.
- **Um PR por tarefa ou etapa,** com o relato no corpo do PR. O worker entrega e para. **O merge é só do Matheus.**
- **O desvio** (interpretação, número escolhido, achado) vai numa seção própria no fim de `docs/registro/AAAA-MM.md` (o mês da data),
  com data, nome e worker, e com uma linha no fim do índice `docs/REGISTRO_DESVIOS.md`.
- **O resumo da etapa não vai no CLAUDE.md.** Vai no corpo do PR e numa seção no fim do documento da frente: o `RESULTADO_V3_*.md` da
  run, ou o `TAREFA_V3_*.md` da etapa de código (o `_V2_` numa frente herdada). O coordenador põe uma linha no `docs/PAINEL_V3.md`. Este arquivo só muda com o ok do
  Matheus.
- **Nunca usar `git stash` sem nome:** o stash é compartilhado entre as worktrees.

## Escolha de modelo e contexto

- **Escolher pela incerteza, pelo risco e pela possibilidade de verificar o resultado**, não só pelo tamanho da tarefa.
- **Sonnet é a preferência para implementação com escopo claro. Haiku, para buscas, extrações e ajustes mecânicos delimitados.**
  **Opus, para arquitetura, método científico, matemática difícil ou diagnóstico complexo**, conforme a disponibilidade da sessão.
- **Operações determinísticas vão para scripts, ferramentas e CI.** Não abrir um worker só para executar um comando conhecido.
- **Contexto mínimo suficiente:** passar a tarefa, as regras aplicáveis e os arquivos necessários; devolver síntese e evidências, sem
  copiar o histórico inteiro. Cada frente longa continua na própria worktree; delegar só o que tiver escopo e entrega claros.
- **Escalar o modelo quando a análise ou a verificação indicar dificuldade**, com uma síntese do que já foi tentado. Informar no relato
  o modelo efetivamente usado, quando disponível, e o motivo da escalada; não inferir o modelo de uma sessão.
- **A seleção efetiva do modelo fica na sessão ou na configuração do agente.** Este arquivo orienta a escolha; não muda o modelo sozinho.
  Economia de tokens não reduz os gates, o determinismo, a revisão nem a autoridade do Matheus.

## Arquitetura

- **Event sourcing:** o estado do pet nunca é salvo. Só o log (ações do dono e avanços de tempo); a vida é refeita reprocessando o log.
- **O motor** é o `engine.py`, com subclasses em camadas, cada uma atrás da sua chave:
  - `treino.MotorComFeedback`, `ambiente.MotorAmbiente` (bola) e `frutas.MotorFrutas`;
  - `mundo.MotorMundo` (o mapa físico) e `motor_corpo.com_corpo(...)` (o corpo químico, `corpo.py`);
  - `grupo.Grupo` (dois pets no mesmo `Mundo`).
- **A política** fica sob o `Protocol` `Politica` (`agir`, `observar`, `estado_interno`). A de referência (a linha de base) é a
  `PoliticaLobos`, e os módulos do DigiBrain modular cumprem o mesmo `Protocol`; ganchos como `receber_acao_dono`,
  `consequencia_mundo` e `consequencia_corpo` ligam o motor ao aprendizado.
- **A bancada** (o pacote `experiments/bancada/`, um módulo por assunto, com o `experiments/bancada_v2.py` como porta de entrada) monta
  toda vida de pesquisa: (genoma, mundo, dono, braço, semente), o modo acoplado e as medidas. Os orquestradores das runs ficam em
  `experiments/run_v2_*.py`, com as configs em `experiments/configs/`.
- **O jogo web** (`web/app/`) espelha o motor em TypeScript, com testes de paridade contra gabaritos do Python. As regras dele estão em
  `web/app/CLAUDE.md`; as do servidor local e da fala por LLM, em `servidor/CLAUDE.md`.

## Onde está o quê

| o quê | onde |
|---|---|
| estado da V3 em uma página (trilhas, missões, decisões abertas, riscos) | `docs/PAINEL_V3.md` |
| o plano da V3, as decisões V3-D1 a V3-D8 e o glossário V2 × V3 | `docs/PLANO_V3.md` |
| o fechamento da V2 (a marca de cada tarefa e marco) | `docs/FECHAMENTO_V2.md`; a V2 congelada na tag `v2-final` |
| marcos J1–J10 e o plano da V2 (congelados) | `docs/ROADMAP_V2.md` (seção 8), `docs/PLANO_V2_PESQUISA.md` |
| tarefa, plano e resultado de cada frente | `docs/TAREFA_V3_*.md`, `docs/PLANO_ANALISE_V3_*.md`, `docs/RESULTADO_V3_*.md`; os `_V2_` da V2 e das frentes herdadas |
| desvios e interpretações | o índice `docs/REGISTRO_DESVIOS.md`; as seções em `docs/registro/AAAA-MM.md` |
| ideias e desenhos ainda sem tarefa | `docs/futuro/` |
| mapa do repositório arquivo a arquivo e todos os comandos | `docs/MAPA_REPOSITORIO.md` |
| o que cada etapa construiu (o resumo antigo do CLAUDE.md, seção a seção) | `docs/historico/claude/` (índice em `docs/historico/LEIA.md`) |
| a v1: arena, confirmatória, educação, linhagem, pergunta do dono | `docs/historico/claude/v1_pesquisa.md` |
| o combate (V2, V2.1, correções, equilíbrio, treino, M1) | `docs/historico/claude/combate.md` |
| a rodada de saúde do repositório | `docs/TAREFA_V2_SAUDE.md` |

Antes de mexer numa frente, leia a tarefa dela e a seção dela em `docs/historico/claude/`.

## Comandos

```bash
python -m pytest tests/test_<frente>.py -q    # os testes da frente, antes de cada commit
python -m pytest tests/ -q                     # a suíte inteira, ~36 min; a contagem do dia vai no corpo do PR
python tools/conferir_saude.py                 # o G-NADA-PERDIDO da rodada de saúde
```

Os outros comandos, inclusive os das runs e do jogo web, estão em `docs/MAPA_REPOSITORIO.md` e em `web/app/CLAUDE.md`.

Ambiente: Windows, Python 3.10 ou mais novo.
