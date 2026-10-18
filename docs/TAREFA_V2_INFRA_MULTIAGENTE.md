# TAREFA V2 — INFRA_MULTIAGENTE (2026-10-18)

Coordenador e worker: esta sessão do Claude Code. Worktree e branch: `v2-infra-multiagente`. Status: ENTREGUE (PR aberto, sem merge).

Categoria: implementacao. Origem: Matheus, 2026-10-18: plano "Infraestrutura de colaboração multiagente — ChatGPT Work + Claude Code",
reduzido à versão enxuta e aprovado com sete ajustes obrigatórios.

## 1. Pergunta

Como o ChatGPT (pesquisa), o ChatGPT Work (orquestração) e o Claude Code (engenharia) trabalham sobre o mesmo repositório sem depender da
memória de nenhuma LLM? Não vem de hipótese do `docs/PLANO_V2_PESQUISA.md`: é infraestrutura, e não muda nenhuma decisão científica.

## 2. Depende de

A rodada de saúde na `main` (o `CLAUDE.md` enxuto, o registro por mês, o `PAINEL_V2.md`, os hooks). Nada mais.

## 3. Mudança mínima

**Muda (tudo novo, menos dois documentos que só ganham texto):**
- `AGENTS.md`, `docs/INDICE.md`, `docs/ESTADO_ATUAL.md` (gerado);
- `docs/infra/` (matriz, auditoria, guia, teste do Work, relatório da prova);
- `.github/pull_request_template.md`, `.github/workflows/verificar-pr.yml`;
- `tools/nova_tarefa.py`, `tools/verificar_relato.py`, `tools/gerar_estado_atual.py` e os três `tests/test_infra_*.py`;
- `docs/modelos/TAREFA_V2_MODELO.md`: **só acréscimo** (Categoria, Origem, seções 7 e 8, a linha do relato);
- `docs/V2_TRABALHO_PARALELO.md`: **uma seção nova no fim**, PROPOSTO.

**Não muda:** o `CLAUDE.md` (só com o ok do Matheus: IM-2), o `PAINEL_V2.md`, o `digilab/`, o `experiments/`, o `web/`, as regras de
coordenador, worker, sementes, plano de análise e aprovação.

## 4. Experimento e gate

Não há run.

## 5. Entrega

- Testes: `python -m pytest tests/test_infra_verificar_relato.py tests/test_infra_nova_tarefa.py tests/test_infra_estado_atual.py -q` e
  `python tools/conferir_saude.py`. A suíte inteira não muda: só entram arquivos de teste novos.
- PR contra a `main`, com o corpo no formato novo. Merge só pelo Matheus.

## 6. Fora desta tarefa

- Executar o Claude no CI (`claude-code-action`), que é pago ou gasta a assinatura.
- Refatorar o `CLAUDE.md`.
- Agentes especializados além do par coordenador e worker.
- Qualquer integração do ChatGPT Work dada como funcionando antes do teste (IM-3).

## 7. Critérios de aceitação

- Os três `tests/test_infra_*.py` passam localmente e no job `testes` do CI.
- O job `relato` passa no PR desta tarefa e reprova um relato incompleto (a prova de conceito).
- `tools/conferir_saude.py` continua passando.
- Todo link relativo dos documentos novos resolve (`verificar_relato.py`, categoria documentacao, na prova de conceito).
- A matriz tem um status (`DOC`, `TESTADO` ou `NÃO CONFIRMADO`) em toda linha, e nenhuma linha do Work está `TESTADO`.

## 8. Precisa do Matheus

- **IM-1, tornar o check `verificar-pr` obrigatório na `main`.** Recomendação: sim, mas só depois de 2 ou 3 PRs com o formato novo.
  - Errar para o sim cedo demais: PR legítimo travado por um falso positivo do verificador.
  - Errar para o não: o formato pode ser ignorado sem ninguém ver.
- **IM-2, uma linha no `CLAUDE.md`, em "Onde está o quê", apontando para `docs/INDICE.md` e `AGENTS.md`.** Recomendação: sim. Custo de
  errar: baixo; é uma linha e sai fácil.
- **IM-3, o teste do ChatGPT Work** (`docs/infra/TESTE_CHATGPT_WORK.md`). Recomendação: fazer antes de qualquer outro passo da integração.
  Custo de não fazer: o fluxo de volta continua sem prova.
- **IM-4, quem regenera o `docs/ESTADO_ATUAL.md`.** Recomendação: o coordenador, no fim da rodada, junto com o painel.
  - A alternativa, uma Action que faz commit na `main`, exige escrita do bot na `main`, o que contraria a regra do merge só pelo Matheus.
  - Custo de errar: um índice desatualizado (o CI avisa).
- **IM-5, a frase "o repositório é privado"** em `docs/TAREFA_V2_CLAUDE_SCIENCE_LITERATURA.md`. O repositório hoje é público. Recomendação:
  deixar o texto como registro histórico, porque a tarefa é de 2026-10-01. Custo de errar: nenhum para o código; para a literatura,
  confusão sobre o que o Claude Science pode ler.
- **IM-6, as tarefas antigas com `Status: ABERTA` depois da entrega** (achado da auditoria). Recomendação: não reescrever. O
  `ESTADO_ATUAL.md` mostra o status declarado e os resultados que citam a tarefa, e a correção, se houver, é uma etapa do coordenador.
