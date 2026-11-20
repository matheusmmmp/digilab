# O CLAUDE.md antes da rodada de saúde: a fundação

Seções movidas inteiras do CLAUDE.md da raiz na etapa 1 da rodada de saúde (`docs/TAREFA_V2_SAUDE.md`, 2026-10-13). As regras que valem
hoje estão no `CLAUDE.md` da raiz; aqui fica o texto como era, com as exceções de escopo e a hipótese da v1. O mapa de cada seção está em
`docs/historico/LEIA.md`.

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
