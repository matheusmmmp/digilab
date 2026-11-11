# Onde vai cada documento

Status: **PROPOSTO** (Gerente da V3, 2026-11-10). O Matheus pediu para mapear por onde os documentos vazam para fora do lugar certo.
Vale como guia até ele decidir. As linhas marcadas **(a decidir)** ficam com ele. Só este documento, o `AGENTS.md` e o `docs/INDICE.md`
apontam para cá. O `CLAUDE.md` só muda com o ok do Matheus: a linha dele que manda "ideias e desenhos" para `docs/futuro/` continua lá.
A troca que fecha esse vazamento está na seção 3.

## 1. O mapa: um tipo, um lugar

Os três lugares de documento são:
- o **repositório**, `D:\Trab\digilab\v3` e as worktrees;
- o **vault** do Obsidian, `C:\Users\mathe\Documents\DigiLab Research`;
- a **pasta de fora do git**, `D:\Trab\digilab`.

| tipo | lugar | observação |
|---|---|---|
| tarefa, plano de análise, resultado | repositório: `docs/TAREFA_V3_*`, `docs/PLANO_ANALISE_V3_*`, `docs/RESULTADO_V3_*` | a tarefa nasce de `python tools/nova_tarefa.py <FRENTE>`, que gera V3 desde 2026-11-10. As frentes herdadas ficam no `_V2_` delas |
| saída de run (meta, medidas, figuras) | repositório: `artifacts_<frente>/`, com a exceção no `.gitignore` | as vidas ficam fora do git (`**/vidas/`) |
| desvio, interpretação, decisão do Matheus | repositório: uma seção no fim de `docs/registro/AAAA-MM.md`, mais uma linha no `docs/PAINEL_V3.md` | é a fonte. O vault (`30 Decisões e protocolo`) só explica, com link para o registro |
| ideia de mecânica ou de código ainda sem tarefa | repositório: `docs/futuro/` | só desenho de jogo ou de código. Levantamento não entra aqui |
| levantamento, revisão, crítica, auditoria, tema de pesquisa | vault: `10 Auditoria` e `20 Temas` | decisão de 2026-11-08 (`docs/registro/2026-11.md`) |
| rascunho de artigo, revisão de escopo | vault: `60 Artigos`, `DigiLab — Revisão de escopo` | |
| referência verificada (bib, csv, regras de citação) | repositório: `docs/referencias/` | é a fonte. O vault só cita. Revisões novas não entram aqui |
| diário do dia | vault: `50 Diário de bordo/AAAA-MM-DD.md` | |
| promo, vídeo e os prompts dele | vault: `40 Produção e divulgação`; os arquivos grandes em `D:\Trab\digilab\promo` | |
| prompt de gerente, prompt mestre **(a decidir)** | recomendado: o vault, numa pasta `40 Produção e divulgação/prompts/`. A outra opção é `docs/infra/prompts/`, se precisar estar versionado | hoje: os antigos em `D:\Trab\digilab\arquivo\2026-11-10_organizacao\prompts_e_rascunhos\`, e outros no repositório (`docs/V2_RODADA_4_PROMPTS.md`) |
| corpo de PR | o próprio PR. O rascunho fica no scratchpad da sessão | nunca na raiz `D:\Trab\digilab` |
| log de teste, e2e ou run local | o scratchpad da sessão, ou `artifacts_*/` se for da run | nunca na raiz `D:\Trab\digilab` |
| capturas de aprovação **(a decidir)** | recomendado: `D:\Trab\digilab\capturas\<frente>_<AAAA-MM-DD>\` enquanto esperam o Matheus; depois de aprovadas, `D:\Trab\digilab\arquivo\` | as pranchas que vão ao PR ficam em `docs/pranchas/`. As referências do e2e ficam em `artifacts_v2_front_react/capturas` |
| assets grandes (sprites, extraídos, 3D) | fora do git: `D:\Trab\digilab\Assets`, `remaster` e `extraido` | UI_GUIDELINES 5.1 |

## 2. Por onde vaza hoje (levantamento de 2026-11-10, só leitura)

1. **Revisão solta no checkout da `main`:** `docs/referencias/I_REVISAO_PET_VIVO_MODULACAO.md` e `I_diagnostico_vies_alvos/` estão em
   `D:\Trab\digilab\v3`, sem estar no git. Foram commitadas só no branch do PR #703, que fechou sem merge. O vault tem uma versão diferente.
2. **Levantamentos em `docs/futuro/` e `docs/research/` de antes da regra de 2026-11-08:** `futuro/vida_do_pet_referencias.md`,
   `futuro/digibrain_v3_e0.md` (uma auditoria) e `futuro/mutacao_possibilidades.md`, mais
   `research/DIAGNOSTICO_CONVERSA_PET.md` e `research/REFERENCIAS_CONVERSA_PET.md`. Ficam onde estão, porque são citados. Os novos vão
   para o vault.
3. **Revisões em `docs/referencias/`:** as `F_`, `G_`, `H_` e `DM_REVISAO_*` e as `*_SINTESE_*`. São de antes da regra e são citadas
   por tarefas, então ficam. As novas não entram aqui.
4. **O mesmo documento em dois ou três lugares:**
   - `revisao_alife_linhagem.md` está em `D:\Trab\digilab\docs`, em `docs/referencias/` e no vault, com versões diferentes;
   - os `referencias.bib` estão no repositório e no vault, e diferem;
   - `D:\Trab\digilab\docs\digibrain\` é uma bifurcação de `docs/research/digibrain/`.
5. **Prompts em três lugares:** a raiz (já levada para o arquivo), `docs/V2_RODADA_4_PROMPTS.md` e `PROMPT_DIAGRAMACAO_ARQUITETURA.md`
   no repositório, e `40 Produção e divulgação` no vault.
6. **Capturas em três lugares:** `D:\Trab\digilab\capturas_*`, `docs/capturas_*` e `docs/pranchas/`, e
   `artifacts_v2_front_react/capturas`.
7. **Decisões em quatro lugares:** o registro, a tarefa, o `PAINEL_V3` e o vault (`30 Decisões`), além de notas de decisão guardadas
   como auditoria (`10 Auditoria/Padrão dos objetos 3D 2026-11-10.md`).
8. **Logs e corpos de PR na raiz `D:\Trab\digilab`:** eram 80 logs e 5 corpos em 2026-11-10. Nenhuma instrução manda escrever lá; é
   hábito de sessão.

## 3. De onde vem o vazamento e o que fecha cada um

| origem | o que mandava | situação |
|---|---|---|
| `AGENTS.md` e `docs/INDICE.md` | `PAINEL_V2`, `TAREFA_V2_*` e o branch `v2-<frente>` | corrigido neste PR |
| `tools/nova_tarefa.py` | V2 por padrão, e a worktree a partir da `v2` | corrigido neste PR (V3 por padrão) |
| `CLAUDE.md`, linha "ideias e desenhos ainda sem tarefa → `docs/futuro/`" | levantamentos em `futuro/` | **a decidir pelo Matheus**: acrescentar "levantamento, revisão e crítica → vault; ver `docs/ONDE_VAI_CADA_DOCUMENTO.md`". O PR #586 (`v3-docs-vault`) já propõe um ponteiro para o vault e não entrou |
| a regra do vault só existe na memória do Claude Code | o Codex e os agentes de fora não a veem | fechada pelo `AGENTS.md` (item 5 da ordem de leitura) e por este documento |
| capturas, logs e corpos de PR | nenhuma regra | a seção 1 dá o lugar; as capturas ficam **a decidir** |
| `.gitignore` sem exceção para 6 pastas de artifacts rastreadas | um arquivo novo nelas era ignorado em silêncio | corrigido neste PR |
