# AGENTS.md — Digilab

Para agentes que não são o Claude Code: o Codex (que lê este arquivo), o ChatGPT e o ChatGPT Work pelo conector GitHub, ou outro. O Claude
Code lê o `CLAUDE.md`. **As regras são as mesmas e moram no `CLAUDE.md`;** este arquivo não repete nenhuma, só diz por onde começar e o que
um agente de fora pode fazer. Status: PROPOSTO (`docs/TAREFA_V2_INFRA_MULTIAGENTE.md`).

## O que é

Projeto de pesquisa pessoal do Matheus: um pet virtual com IA (vida artificial). Não é trabalho de mestrado nem de programa nenhum; não
associe. A pesquisa fica no Python (`digilab/`, `experiments/`); o jogo, em `web/app/`.

## Ordem de leitura (pare quando tiver o que precisa)

1. `CLAUDE.md`: as regras não negociáveis, o método de pesquisa e o trabalho em paralelo. **Leia antes de propor qualquer coisa.**
2. `docs/INDICE.md`: onde mora cada tipo de informação (implementado, decidido, hipótese, proposta, resultado, problema, próximo).
3. `docs/PAINEL_V2.md`: o estado da V2 em uma página, curado pelo coordenador. `docs/ESTADO_ATUAL.md` é só um índice derivado dele e das
   tarefas, nunca fonte.
4. A frente: `docs/TAREFA_V2_<FRENTE>.md`, `docs/PLANO_ANALISE_V2_<FRENTE>.md`, `docs/RESULTADO_V2_<FRENTE>.md`.

## Separar o que é de verdade

- **Implementado** é o que está no código da `main` e tem teste. Um documento de plano, tarefa ou proposta **não** é evidência de que algo
  existe.
- **Decidido** é o que o Matheus decidiu, com data, no painel, na tarefa ou no registro. Todo número novo é PROPOSTO até ele decidir.
- **Resultado** é só o que tem artefato em disco (`artifacts_*/`) e plano de análise commitado antes da run.
- **Literatura:** só as referências de `docs/referencias/` marcadas VERIFICADA (`docs/referencias/REGRAS_CITACAO_DIGILAB.md`). Fora delas,
  SEM FONTE. Nunca alegar novidade.

## O que um agente de fora pode fazer

- Pesquisar, comparar, propor hipótese, arquitetura ou tarefa. A proposta entra no repositório como `docs/TAREFA_V2_<FRENTE>.md`, gerada por
  `python tools/nova_tarefa.py`, por PR do coordenador ou do Matheus.
- Revisar um PR: ler o corpo (o relato), o diff e o resumo do CI, e apontar inconsistências.
- Escrever código, se a ferramenta deixar (o Codex): numa worktree ou branch próprio `v2-<frente>`, com PR contra a `main`.

## O que nunca fazer

- Merge, push na `main`, ou mudar uma decisão do Matheus. O merge é só dele.
- Rodar a validação, escolher sementes fora de `experiments/bancada/faixas.py`, ou ajustar olhando os dados da validação.
- Mexer em `digilab/engine.py` (o sha está congelado) ou pôr dependência fora da biblioteca padrão em `digilab/`.
- Colocar credencial, token ou dado pessoal em qualquer arquivo.

## O relato de volta

O corpo do PR segue `.github/pull_request_template.md`. O CI (`tools/verificar_relato.py`) confere os campos e a evidência da categoria
(implementacao, experimento, literatura, arquitetura, documentacao). O que o agente escreve é **declarado**; prova é só o que o CI confere
ou roda sozinho.
