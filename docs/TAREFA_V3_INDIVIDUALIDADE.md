# TAREFA V3 — INDIVIDUALIDADE (2026-11-07)

Coordenador: Matheus (sessão direta). Worker da etapa I0: Claude Code, Opus 5.5, worktree `v3-individualidade`. Worktree e branch:
`v3-individualidade` (as etapas seguintes com sufixo, como `v3-individualidade-i0`). Status: **ABERTA; a proposta na `main` (#676);
as IN-1 a IN-8 DECIDIDAS em 2026-11-07, pela recomendação; o I0 (a conferência) ENTREGUE.** Nenhum código, nenhuma faixa, nenhuma vida.

Categoria: documentacao. Origem: Matheus, 2026-11-07: depois da conversa sobre o connectome e a escala, direcionar a pesquisa para o
temperamento herdado, o sinal do dono, a memória de episódios e o hábito, com uma medida comum de individualidade.

## 1. Pergunta

**O pet modular fica diferente dos outros de um jeito estável, e quanto disso vem do genoma, do dono e da interação?** A proposta inteira
está em `docs/futuro/individualidade_pet.md`. Ela junta o G1 do `docs/futuro/ecossistema_genetico.md` (a variância herdável) e uma
pergunta nova sobre o aprendiz modular (o dono), sem reabrir a leitura da v1 (`docs/LEITURA_CONSOLIDADA_DONO.md`).

## 2. Depende de

- Na `main`: nada além do que já está (`3d79072`).
- Do Matheus: as IN-1 a IN-8 (`docs/futuro/individualidade_pet.md`, seção 8), antes de qualquer etapa depois desta.
- Para o I3 e o I4: o Gate I no modular (GI-4; IN-4).

## 3. Mudança mínima

Esta etapa só escreve documentos: a proposta em `docs/futuro/individualidade_pet.md` e esta tarefa. Não mudam `engine.py`, o modular,
a web, o genoma (G0), as facetas (M5) nem o P2 (D-C2-4-2).

## 4. Experimento e gate (se houver run)

Nenhum nesta etapa. As etapas I2 a I5 terão o plano em `docs/PLANO_ANALISE_V3_INDIVIDUALIDADE.md`, commitado antes da primeira vida, e
uma faixa pedida ao coordenador. Nenhum número é decidido aqui.

## 5. Entrega

- Testes: não se aplicam (só documentos).
- PR contra a `main` com o relato no modelo. Merge só pelo Matheus.

## 6. Fora desta tarefa

Escalar a rede até o tamanho de um conectoma; um mecanismo novo de hábito; a calibração; a web até o I6; os dois pets
(`docs/futuro/individualidade_pet.md`, seção 6).

## 7. Critérios de aceitação

- `docs/futuro/individualidade_pet.md` existe, com a medida, o desenho, os passos I0 a I6 e as IN-1 a IN-8, cada uma com a recomendação e
  o custo de errar.
- Toda referência citada está em `docs/referencias/referencias_verificadas.csv` ou no `docs/research/digibrain/sources/`.
- Os links relativos dos documentos mudados resolvem (o CI da categoria documentacao).

## 8. Precisa do Matheus

As IN-1 a IN-8 estão DECIDIDAS (2026-11-07, pela recomendação). O I1 começa com o sim do Matheus.

## Resultado da proposta (2026-11-07, Claude Code, Opus 5.5, branch `v3-individualidade`)

A proposta e esta tarefa estão na `main` (#676, `df04915`).

## Resultado da etapa I0 (2026-11-07, Claude Code, Opus 5.5, branch `v3-individualidade-i0`)

- **As decisões:** as IN-1 a IN-8, pela recomendação. O Matheus escreveu "Agora siga com as recomendações" nesta sessão, depois do
  merge do #676.
- **A conferência das sondas** (`docs/futuro/individualidade_pet.md`, seção 3.1, "a conferência do I0"):
  - cinco das seis sondas saem de gestos ou estados que o motor já tem: comida nova, longe, bola, susto e tédio;
  - **a sonda "o dono chama" foi trocada por "o dono some"**, porque não existe ação de chamar do dono no `AcaoUsuario` (o desvio
    D-IND-I0-1). A troca lê o `chamar_atencao`, a ação em que a faceta `apego_dono` entra;
  - o susto sai do `tapa` só na cópia, nunca na vida real.
- **O dono das vidas:** o `CanalSemEnsino` das vidas da C1 e da C4 já cumpre a IN-6, e os quatro donos do protótipo são as personas.
- **Ficam para o I1:**
  - a forma da cópia: a cópia profunda ou o replay do prefixo, pela que passar no G2 e custar menos;
  - se o corpo das vidas da C4 liga os drives novos, porque o tédio depende disso.

## As etapas seguintes

| etapa | o quê | entrega |
|---|---|---|
| I1 | a bateria como ferramenta (`experiments/bancada/`), só leitura, com o gabarito e o G2 | código e testes, PR próprio |
| I2 | a linha de base descritiva no modular de hoje | `docs/PLANO_ANALISE_V3_INDIVIDUALIDADE.md` e uma faixa pedida antes; a run; o `RESULTADO_V3_INDIVIDUALIDADE.md` |
| Gate I | o Gate I no modular (IN-4), entre o I2 e o I3 | pela `docs/TAREFA_V2_GATE_I.md`, com os critérios no modular |
| I3, I4, I5, I6 | o temperamento, o dono, o hábito como medida e a ficha | pela proposta, seção 5 |
