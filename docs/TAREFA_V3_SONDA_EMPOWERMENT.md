# TAREFA V3 — SONDA_EMPOWERMENT (2026-11-17)

Coordenador: Matheus, pela sessão da F5, aberta pela Gerente das cinco frentes. Worker: Claude Code, Opus 5.5, na worktree
`wt-v3-f5-sonda`, branch `v3-f5-sonda-empowerment`. Status: **ABERTA; a espec APROVADA pelo Matheus; as D-F5-2 a D-F5-8 aceitas (2026-11-17).**

Categoria: arquitetura. Origem: a frente F5 do prompt das cinco frentes (vault, `30 Decisões e protocolo/PROMPT_CINCO_FRENTES_2026-11-16.md`)
e o levantamento do vault (`DigiLab — Revisão de escopo/LEVANTAMENTO_EMPOWERMENT_F5_2026-11-17.md`). Decisões do Matheus, as três de
2026-11-17 e literais:
- **D-F5-1**: à pergunta "A F5 fica como pesquisa ou vira frente agora?", ele respondeu "Pesquisa, com sonda";
- à pergunta "Escrevo agora a espec da sonda do E(P) em docs/, numa worktree com PR?", ele respondeu "Sim, escreva a espec".
- à pergunta "Você revisa e aprova a espec e as D-F5-2 a D-F5-8 no PR #965?", ele respondeu "Aprovo as recomendações".

## 1. Pergunta

**O número de corpos distintos que o pet alcança comendo, a partir de um lugar (o `E(P)`), varia entre lugares? E ele se separa da
simples contagem das classes lembradas por perto?** É uma pergunta descritiva. Ela decide só se a hipótese H-EMP-1 do levantamento vale um
plano depois da F3. A F5 não é frente.

## 2. Depende de

- Na `main`: nada além do que já está. O M-PLAST (`d̂`, `andar`) e o M-MEM (episódios, `_faixa`) são lidos, não mudados.
- Do Matheus: a aprovação da `docs/ESPEC_V3_SONDA_EMPOWERMENT.md` e as D-F5-2 a D-F5-8, antes de qualquer código (dada em 2026-11-17).
- Não depende da F3. A H-EMP-1, sim, se a sonda não acabar com ela.

## 3. Mudança mínima

Esta etapa só escreve documentos:
- a espec, `docs/ESPEC_V3_SONDA_EMPOWERMENT.md`;
- esta tarefa;
- as referências, `docs/referencias/v3_f5_empowerment_referencias_verificadas.csv`.

Na etapa seguinte, só mudam `experiments/` e `tests/` (espec, seção 3). O `digilab/`, o `engine.py`, o `config.py` e a web não mudam.

## 4. Experimento e gate (se houver run)

Nenhuma run nesta etapa. A medida não roda vida nova: ela rejoga vidas que já existem (espec, seção 4). O plano de análise vai num
`docs/PLANO_ANALISE_V3_SONDA_EMPOWERMENT.md`, commitado antes do primeiro artefato (D-F5-8). O papel é descritivo, não gate; a leitura
registrada está na espec, seção 5.4.

## 5. Etapas

1. **SE0 (este PR):** a espec, a tarefa e as referências.
2. **SE1, depois da aprovação:** os testes T-E1 a T-E6, as funções puras e o coletor, sem medida.
3. **SE2:** o plano de análise commitado; depois, a medida nas vidas da D-F5-2 e o resultado em `docs/RESULTADO_V3_SONDA_EMPOWERMENT.md`.
