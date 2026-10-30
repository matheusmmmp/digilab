# PAINEL V3: onde a V3 está, em uma página

**Atualizado em 2026-10-30** (`main` `a4fd6d2`, depois do #485), pelo Gerente da V3. O plano é o `docs/PLANO_V3.md`; o
fechamento da V2, o `docs/FECHAMENTO_V2.md` (tag `v2-final`).

- Quem atualiza: o coordenador de cada trilha, uma linha por PR mergeado.
- Regra (herdada do `PAINEL_V2.md`): cada linha cita o documento ou o PR de onde veio; aqui não entra número novo.

## 0. A V3 em uma frase por trilha

| trilha | a pergunta | terminou quando |
|---|---|---|
| **C · cérebro** | os mecanismos que a triagem de 2026-10-30 aponta explicam ou corrigem as falhas do modular no longe e no hábito, testados com controle? | C1 e C2 rodaram uma vez; C3 e C4 com espec, código e plano; a espec do modular revista com [MECANISMO], [HIPÓTESE] e [EXISTE] |
| **L · layout** | o jogo fica inteiro no layout habitat, nas duas peles, com a primeira peça do modular com paridade? | M7 e T1–T3 na `main` com as capturas aprovadas; L3 na `main`, ou a decisão de não levar peça ainda |
| **B · batalha** | o combate em tempo real fecha as metas com o candidato v14, a ponto de ligá-la? | a conferência da rodada 2 rodou uma vez, e o Matheus decidiu ligar ou não a v14 |

## 1. As missões

| missão | o que é | estado | onde |
|---|---|---|---|
| infra · o prefixo V3 | o CI e as ferramentas aceitam `TAREFA_V3_*` e `PLANO_ANALISE_V3_*` | **na `main`** (#478) | `docs/TAREFA_V2_INFRA_PREFIXO_V3.md` |
| congelamento · V3-D5 | o cabeçalho "V2, congelado" e a última linha do `PAINEL_V2.md` | **na `main`** (#483) | `docs/PLANO_V3.md`, seção 7 |
| **C0** literatura | as fontes da triagem verificadas, a síntese e a alegação proibida nova | **na `main`** (#482) | `docs/TAREFA_V3_LITERATURA.md` |
| **C1** longe regular | o longe com lugares fixos; LR-1 a LR-7 e C1-E1/E2 DECIDIDAS (2026-10-30, pela recomendação; as entradas na `main`, #485) | etapa 1 (código) e etapa 2 (adendo 6) despachadas; a run (etapa 3) depois das duas na `main` | `docs/TAREFA_V2_LONGE_REGULAR.md` |
| **C2** o hábito com crédito na intenção | o braço de crédito na intenção contra o passo | sem tarefa; depois da C1 | `docs/PLANO_V3.md`, seção 2 |
| **C3** redecidir por evento | espec no formato da L-2, subchave desligada | sem tarefa; depois da C1 | idem |
| **C4** memória autobiográfica | ME-1 a ME-7 DECIDIDAS (2026-10-30, pela recomendação), com as entradas da C0 e as C4-E1 a C4-E3 | só papel; a espec depois, sem pressa (`digilab/digibrain/` com a C2 e a C3) | `docs/TAREFA_V2_MEMORIA_AUTOBIOGRAFICA.md`, seção 8 |
| **C5** viabilidade do corpo | as medidas do corpo fora da faixa, do replay | entra no adendo 6 da C1 | `docs/PLANO_V3.md`, seção 2 |
| **L1** M7 do layout | o fechamento do layout habitat | **na `main`** (#477) | `docs/TAREFA_V2_LAYOUT_HABITAT.md` |
| **L2** tema dos menus T1–T3 | a pele Vidro como padrão, a escolha em Ajustes, as capturas nas duas peles | T1 em PR (#486); T2 e T3 depois da L4 | `docs/TAREFA_V2_TEMA_MENUS.md`, seção 5 |
| **L3** o primeiro módulo do modular no jogo | o lugar lembrado do M-MEM, proposto, com paridade | depois da C1 e da C2 | `docs/TAREFA_V2_DIGIBRAIN_MODULAR_PRODUTO.md` |
| **L4** habitat como ilha 3D | a cena do modo mundo (v12) como ilha 3D, com o pet em papel; só vista | H0 a H5 em PRs empilhados (#488 a #494; a H1b liga o `CLIPES_UP`); ordem DECIDIDA (2026-10-30): depois da T1, antes da T2 e da T3; faltam as capturas aprovadas e a M3 | `docs/TAREFA_V3_HABITAT_ILHA_3D.md` (no #488) |
| **B1** rodada 2 do equilíbrio | as fases do `PLANO_EQUILIBRIO_COMBATE_TR_R2.md` | R2-0 a R2-3 **na `main`** (#479, #481, #487); R2-4 na sessão dela | `docs/EQUILIBRIO_COMBATE_TR.md` |
| **B2** ligar a v14 | trocar fatores, relógio e listas do jogo | depois da conferência da B1 e do sim do Matheus | `docs/PLANO_V3.md`, seção 4 |
| **B3** a luta no layout novo | o HUD e o palco na pele dos menus | depois da L2 | idem |

## 2. Decisões abertas do Matheus

- **A L4:** aprovar as capturas da ilha (390 e 1280; claro, escuro e noite) e medir a M3 com `?medir3d=1` no desktop e num celular.
- **Os merges, na ordem:** a T1 (#486); depois a L4, do #488 ao #494.
- **B2:** ligar a v14 só depois da conferência da rodada 2.

## 3. Riscos

| risco | o que se vê | onde |
|---|---|---|
| o aprendiz no mundo físico | o P1 perde do instinto (J1); o modular fecha 0,41 no longe só no cheiro contra 0,74 no comedouro | `docs/FECHAMENTO_V2.md`; `docs/TAREFA_V2_LONGE_REGULAR.md`, seção 1.1 |
| a alegação de novidade | a combinação corpo + aprendizado + memória já foi publicada; o ponto defensável é o teste causal com controle | `docs/PLANO_V3.md`, seção 2.2 |
| a máquina | WHEA 19 e o access violation de 2026-10-28; ≤ 4 processos, uma run por vez (V3-D8) | `docs/PLANO_V3.md`, seção 7 |
| arquivos disputados | `App.tsx`, `tokens.css`, `pet.css`, `Nav.tsx` (L2, L4, B3) e `digilab/digibrain/` (C2, C3, C4): uma missão por vez | `docs/PLANO_V3.md`, seção 5 |
