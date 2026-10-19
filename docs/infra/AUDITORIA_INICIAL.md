# Auditoria inicial do Digilab para a infraestrutura multiagente (2026-10-18)

Tarefa: `docs/TAREFA_V2_INFRA_MULTIAGENTE.md`. Foi feita na `origin/main` em `66bc21b`, a merge do #322. Esta auditoria só descreve o
repositório: não lê nenhuma conversa de fora dele.

## 1. O que está acessível

- **O repositório `matheusmmmp/digilab`**, público (`gh repo view`), com cerca de 800 commits. O `gh` funciona nesta máquina.
- **O plugin GitHub do Claude Code não conectou nesta sessão**: "Authorization header is badly formatted". Não atrapalhou, porque o `gh`
  CLI fez o trabalho, mas o plugin precisa ser reconectado do lado do Matheus.
- **As pastas locais em `D:\Trab\digilab`:**
  - `v1`, só leitura;
  - `v2`, a referência da `main`. Estava num commit antigo (HEAD destacado): quem lê a pasta sem `git fetch` vê o `CLAUDE.md` de 2.447
    linhas de antes da rodada de saúde;
  - mais de 60 worktrees `v2-*`.

## 2. Arquivos examinados

- `CLAUDE.md` (107 linhas), `docs/V2_TRABALHO_PARALELO.md`, `docs/modelos/TAREFA_V2_MODELO.md`, `docs/PAINEL_V2.md`,
  `docs/REGISTRO_DESVIOS.md`, `docs/TAREFA_V2_SAUDE.md`;
- `.claude/settings.json` e `.claude/hooks/h3_main.py`;
- `tools/conferir_saude.py` e `tests/test_conferir_saude.py`;
- `docs/referencias/` (as tabelas `*_verificadas.csv`, os `.bib`, os `*crossref.json`, `REGRAS_CITACAO_DIGILAB.md`);
- `docs/TAREFA_V2_CLAUDE_SCIENCE_LITERATURA.md`;
- as linhas `Status:` das 65 `docs/TAREFA_V2_*.md`;
- os corpos dos PRs #320 e #322.

## 3. O que já existe e cobre o plano

| o que o plano pedia | o que já existe |
|---|---|
| o repositório como fonte de verdade | "nenhum número sem artefato em disco", event sourcing, protocolos com hash, plano de análise antes da run |
| instruções persistentes | `CLAUDE.md` enxuto, com a tabela "Onde está o quê"; `web/app/CLAUDE.md`; `servidor/CLAUDE.md` |
| estado atual em uma página | `docs/PAINEL_V2.md`, curado pelo coordenador, com a fonte em cada linha |
| handoff de ida | `docs/TAREFA_V2_<FRENTE>.md` (65), pelo modelo |
| relato de volta | o corpo do PR (a regra do `CLAUDE.md`) e `docs/RESULTADO_V2_*.md` (17) |
| decisões e desvios | `docs/registro/AAAA-MM.md` com o índice em `docs/REGISTRO_DESVIOS.md` (238 entradas), conferido por `tools/conferir_saude.py` |
| governança multiagente | coordenador e workers, uma worktree por frente, merge só pelo Matheus, fila da GPU, faixas de sementes |
| proteção contra ação destrutiva | os hooks H1 e H1b (`engine.py`) e H3 (merge e push na `main` pedem aprovação) |
| literatura | `docs/referencias/` e a skill `literatura-digilab` |

## 4. Lacunas

1. **Não há porta de entrada para agentes que não são o Claude Code.** Não existe `AGENTS.md`, e o Codex lê esse arquivo.
2. **Não há CI** (`.github/` não existia). Nada conferia um PR sozinho.
3. **O relato de volta não tinha formato fixo.** Os PRs #320 e #322 têm "O que é" e "Testes", mas não têm tarefa, categoria, executor nem
   seção de desvios: o verificador novo reprova os dois, como esperado.
4. **Nada separa o que o agente declara do que foi verificado.** "Testes: não rodados" ou "N passed" no corpo do PR são só declarações.
5. **A origem da pesquisa não fica registrada** quando a tarefa ou a literatura vem do ChatGPT ou do Claude Science.

## 5. Inconsistências achadas (não corrigidas aqui)

- **`Status:` parado.** 54 das 65 tarefas dizem `ABERTA`, inclusive 9 que já têm um `RESULTADO_V2_*.md` que as cita (por exemplo, a
  `TAREFA_V2_N3_CONSEQUENCIA`, citada por `RESULTADO_V2_N3`). Sete não têm `Status:`. A contagem é a do `docs/ESTADO_ATUAL.md` gerado em
  2026-10-18. O `ESTADO_ATUAL.md` mostra o status como está
  escrito e ao lado os resultados que citam a tarefa, sem corrigir nada (IM-6).
- **"O repositório é privado"** em `docs/TAREFA_V2_CLAUDE_SCIENCE_LITERATURA.md`, mas hoje ele é público (IM-5).
- **Um DOI verificado fora da tabela.** O Lehman 2020 (`10.1162/artl_a_00319`) foi conferido depois da revisão e está no
  `referencias.bib`, não na `referencias_verificadas.csv`, como a skill `literatura-digilab` já diz. O verificador aceita o `.bib` e o
  `crossref.json`, mas, quando a tabela marca um DOI como não verificado, a tabela prevalece.

## 6. Riscos de integração

- **Um segundo sistema de verdade.** Mitigação: o `ESTADO_ATUAL.md` é gerado, e o `AGENTS.md` e o `INDICE.md` só apontam.
- **Um falso positivo do verificador trava PR legítimo.** Mitigação: o check não é obrigatório até a decisão IM-1.
- **O conector do ChatGPT só lê.** A ida (tarefa vinda do Work) sempre passa por uma pessoa que commita.
- **Execução com custo.** O `claude-code-action` e o Codex com chave de API não foram configurados.
- **A pasta `v2` local está desatualizada.** Quem lê sem fazer fetch, inclusive um agente, vê um estado antigo. O guia manda fazer
  `git fetch` e ler a `origin/main`.

## 7. Alterações feitas (todas nesta tarefa)

Estão listadas na seção 3 da tarefa. Nenhuma toca o `CLAUDE.md`, o `PAINEL_V2.md`, o código de pesquisa ou o jogo.
