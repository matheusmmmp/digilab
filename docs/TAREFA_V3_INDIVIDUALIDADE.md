# TAREFA V3 — INDIVIDUALIDADE (2026-11-07)

Coordenador: Matheus (sessão direta). Worker da etapa I0: Claude Code, Opus 5.5, worktree `v3-individualidade`. Worktree e branch:
`v3-individualidade` (as etapas seguintes com sufixo, como `v3-individualidade-i0`). Status: **ABERTA; a proposta na `main` (#676);
as IN-1 a IN-8 DECIDIDAS em 2026-11-07, pela recomendação; o I0 (a conferência) na `main` (#684); o I1 (a bateria como ferramenta)
ENTREGUE.** Nenhuma faixa, nenhuma vida de pesquisa.

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

## Resultado da etapa I1 (2026-11-07, Claude Code, Opus 5.5, branch `v3-individualidade-i1`)

- **A ferramenta:** `experiments/sondas_individualidade.py`, fora do `digilab/`. O `engine.py`, o cérebro e a web não mudam.
  - A vida é a da C4 (`run_v2_memoria_autobio.viver`), com o braço, o dono, o lugar, a semente e os dias como argumentos.
  - Por dia, o momento é o passo do dono em que cai a primeira decisão acordada da vida real a partir das 10 h, até as 18 h.
  - A cópia sai do replay do log até esse tick (`reproduzir_mundo(..., ate_tick=T)`). Cada réplica é uma cópia profunda dela, com a rng
    de política e a da posição derivadas por `derivar_semente`.
  - As decisões da janela (240 ticks) saem do registro do cérebro: as ações, a contagem, a latência da ação-chave (o `comer` da comida
    posta, pelo id) e as posições.
- **As janelas:** cinco, e não seis. O "dono some" e o "tédio" são a mesma janela sem estímulo, a `nula`, lida por dois traços
  (D-IND-I1-1). A `nula` também é o controle das outras.
- **O que o I0 deixou aberto, resolvido:**
  - a cópia é o replay do prefixo mais a cópia profunda por réplica (D-IND-I1-3);
  - o corpo das vidas da C4 liga os drives novos e os gestos (`drives_novos=True`, `gestos=True`), então o tédio e o susto existem.
- **O contato:** a comida nova e o longe usam o `deixar_comida` do motor, que é contato do dono, como no jogo (D-IND-I1-2). A bola não é
  contato.
- **Os números da ferramenta** (a hora, as janelas, as réplicas e as distâncias) são PROPOSTOS, SEM FONTE, no topo do módulo. Ela mede,
  não é mecânica do pet, e por isso eles não entram no `config.py`. O plano do I2 pode trocá-los antes da run.
- **O que o I1 não calcula:** nenhuma métrica. A bateria só grava as decisões de cada janela. A repetibilidade de cada traço, a divisão
  da variância e a norma de reação são do I2 e vão para o `digilab/metrics.py` ("métricas existem uma vez só"), com o plano registrado
  antes.
- **O gabarito:** nenhuma vida de hoje muda (o G2 prova isso por teste), então não há gabarito "antes" para gravar num commit próprio. O
  gabarito novo é o da própria bateria e nasce com ela.
- **Testes:** `tests/test_sondas_individualidade.py`, 8 testes.
  - o G2: a vida com e sem a bateria sai com o mesmo log e o mesmo resumo;
  - o tapa só na cópia; o determinismo; a cópia para no tick;
  - as cinco janelas e as réplicas em todo dia com sonda; o momento cai numa decisão acordada;
  - a sonda desconhecida falha alto;
  - o gabarito (o sha256 da bateria de uma vida de teste, em `tests/gabaritos/sondas_individualidade.json`).

## O plano do I2 (2026-11-07, Claude Code, Opus 5.5, branch `v3-individualidade-i2-plano`)

O `docs/PLANO_ANALISE_V3_INDIVIDUALIDADE.md` está PROPOSTO, com as IP-1 a IP-9 para o Matheus.
- O desenho: o REL e o REL+F, os quatro donos, o `comedouro`, 14 dias e 60 sementes pareadas, num total de 480 vidas.
- As medidas: seis traços e, por traço, o R_pet, o R_dia e o R_rep, o η² do dono, as facetas, a síndrome e a norma de reação.
- A regra escrita antes para os traços que entram no I3.
- O longe passa a 16 células do pet, fora da visão e dentro do cheiro.
- A faixa foi pedida ao Gerente. Nenhuma vida roda antes do APROVADO, da faixa, do I2a e do registro.

## As etapas seguintes

| etapa | o quê | entrega |
|---|---|---|
| I1 | a bateria como ferramenta (`experiments/bancada/`), só leitura, com o gabarito e o G2 | código e testes, PR próprio |
| I2 | a linha de base descritiva no modular de hoje | `docs/PLANO_ANALISE_V3_INDIVIDUALIDADE.md` e uma faixa pedida antes; a run; o `RESULTADO_V3_INDIVIDUALIDADE.md` |
| Gate I | o Gate I no modular (IN-4), entre o I2 e o I3 | pela `docs/TAREFA_V2_GATE_I.md`, com os critérios no modular |
| I3, I4, I5, I6 | o temperamento, o dono, o hábito como medida e a ficha | pela proposta, seção 5 |
