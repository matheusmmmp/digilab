# TAREFA V2 — DOIS PETS: dois pets de verdade no mesmo mundo (2026-10-07)

Coordenador: Gerente. Workers: A (motor e web), B (cérebro), D (bancada) e C (plano). Worktree e branch de cada etapa:
`v2-dois-pets-<etapa>`. Status: **ABERTA, PROPOSTA.** As etapas só começam depois de o Matheus decidir DP-1 a DP-10.

**O desenho:** `docs/futuro/dois_pets.md`. Esta tarefa só põe em ordem, com dono e gate, o que o desenho propõe.

**Já decidido pelo Matheus em 2026-10-07:** dois pets de verdade no mesmo mundo, e não um pet sintético informante.

**Só papel até as etapas começarem.** Nenhuma run de pesquisa sem o plano de análise (etapa 6), commitado antes.

## 1. Pergunta

Dois pets reais no mesmo mapa, competindo pela comida e vendo um ao outro: **o B aprende algo que só o A viveu?** É o degrau 1 da escada de
`docs/futuro/cognicao_social.md` (o "aprendido de outros"). É a terceira via de informação ao lado do herdado (P0) e do vivido (P1), no
mesmo agente e com controles.

## 2. Depende de

- **As decisões DP-1 a DP-10** do desenho (seção 14).
- **Na `main` já estão:** o `MotorMundo` (#232 e seguintes), o instinto do mundo, o `MotorCorpo` no mundo, a bancada do mundo físico e o
  motor em TypeScript.
- **A etapa 6 do corpo** (os drives novos e os gestos, do B), antes da etapa 4 desta tarefa, porque o B está nela.
- **A validação do mundo físico,** antes de qualquer run desta frente: ela dá a referência do pet sozinho.

## 3. Etapas e donos

| etapa | dono | arquivos | entrega | gates |
|---|---|---|---|---|
| **0. gabaritos** | A | `tests/gabaritos/dois_pets_vidas_de_hoje.json` | as vidas do mundo físico de hoje, com e sem o corpo, nos dois layouts, gravadas **antes** da etapa 1 | — |
| **1. o `Mundo` como componente** | A | `digilab/mundo.py` (separar o `Mundo` do `MotorMundo`, como o `mundo.ts`) | com um pet, o `MotorMundo` é dono do próprio `Mundo`; a atualização do mundo fica idempotente por tick | **G2** (os gabaritos da etapa 0, os de `mundo_vidas_de_hoje.json` e `corpo_mundo_vidas_de_hoje.json`), G-ENGINE, a suíte de sempre |
| **2. o `Grupo`** | A | `digilab/grupo.py` (novo), `ConfigGrupo` no fim de `config.py` | N motores sobre um `Mundo`; a vez sorteada no fluxo `mundo-ordem` (DP-2); as sementes do grupo (seção 2 do desenho); o registro do grupo com cabeçalho e destino (DP-3); o `reproduzir_grupo`; a entrada de um pet depois do tick 0 | **G2** com um pet no grupo, **G1-GRUPO**, **G-ORDEM**, **G-NUMS-GRUPO** |
| **3. a percepção e a disputa** | A | `digilab/mundo.py`, `digilab/policy.py` (só o campo `Observacao.social`, com padrão `None`) | a `PercepcaoSocial` (seção 5 do desenho, DP-4); os candidatos `seguir` e `onde_comeu` no explorar; a disputa (o primeiro na vez come, o segundo não acha: MF-2); os registros para as medidas (as disputas e quem ganhou, as idas a `onde_comeu`, o tempo à vista) | **G-RECEPTOR-SOCIAL**, **G-MEC-SOCIAL**, o G2 de novo |
| **4. o cérebro A no grupo** | B | `digilab/policies/lobos.py` (atrás de uma chave) | o alvo aprendido por classe de candidato, com o prior do padrão e o peso pequeno nas outras classes (PROPOSTO); as entradas sociais nas regras de tempo livre com prior 0; o modelo dos outros (familiaridade, confiança por atividade, afinidade) só registrado (DP-8); o embrulho repassando o que for novo | com a chave e sem o grupo, a vida de hoje (**G2**); **no prior, o P0 com lobos é o instinto do mundo byte a byte**, também com o outro à vista; **G1**; a conta exata do alvo aprendido; o modelo dos outros não muda a decisão |
| **5. a bancada do grupo** | D | `experiments/bancada_v2.py`, `digilab/metrics.py`, `experiments/configs/v2_dois_pets/` | o grupo como célula; o A experiente que entra K dias antes; os braços B só, B + A informativo, B + A embaralhado, B + A ingênuo (seção 11 do desenho, DP-9); o mundo com o efeito por tipo de árvore e o desarranjo do embaralhado; as medidas do plano; as faixas e o prefixo `dois_pets`, quando o plano os der | o G1 de todo grupo; **o B só é a vida de hoje** com a mesma semente; os braços com as mesmas ordens sorteadas quando a composição é a mesma |
| **6. o plano de análise** | C | `docs/PLANO_ANALISE_V2_DOIS_PETS.md` | a pergunta, as medidas, o contraste primário (B + informativo contra B + embaralhado), a calibração (só o que for do mundo e do K, sem o primário), as sementes novas, o gate e a regra de decisão | commitado **antes de qualquer run** |
| **7. o grupo em TypeScript** | A | `web/app/motor/grupo.ts` e a paridade | quando o produto voltar (o v11 está pausado) | **G-PAR** |

**A ordem:** 0 → 1 → 2 → 3, em paralelo com as etapas 6 a 8 do corpo. Depois vêm 4 (depois da etapa 6 do corpo) e 5. O plano (6) pode ser
escrito em paralelo, mas é commitado antes de qualquer run. A etapa 7 fica para quando o produto voltar.

Um PR por etapa, com o relato no corpo. **O merge é do Matheus.**

## 4. Experimento e gate

- **O plano** é `docs/PLANO_ANALISE_V2_DOIS_PETS.md` (etapa 6), commitado antes da run.
- **As sementes:** faixas novas fora de `FAIXAS_RESERVADAS`, propostas pelo plano e registradas pelo D.
- **A medida e o gate:** são do plano. O desenho só aponta o contraste primário (seção 11).
- **GPU:** não.

## 5. Fronteiras (o que não muda)

- **`engine.py`:** o sha256 de sempre.
- **O `AcaoPet`:** nenhum membro novo. Os candidatos sociais são alvos, e a comunicação (degrau 2, fora desta tarefa) seria sub-decisão
  do `chamar_atencao` (DP-6).
- **Os pets v1 a v10 e a web de hoje:** iguais. Nenhuma versão de pet nova nesta tarefa.
- **Com a chave do grupo desligada, ou um pet só,** tudo byte a byte como hoje (G2).
- **Nenhum sinal de reforço sai do outro pet,** e nenhum parâmetro passa de um cérebro ao outro (desenho, seção 7).
- **Sem agressão entre pets** (CV-3).

## 6. Entrega de cada etapa

- **Os testes:** `python -m pytest tests/ -q`. Em `web/app`, `npm test` e `npm run tipos`, só na etapa 7.
- **O registro:** uma seção própria no fim do `CLAUDE.md` e do `docs/REGISTRO_DESVIOS.md`.
- **O PR** vai contra a `main`, com o resumo e os números, cada um com o artefato. O relato vai no corpo do PR.

## 7. Fora desta tarefa

- **O degrau 2,** a comunicação (`COMIDA(lugar)`), com tarefa e plano próprios, depois de o degrau 1 ter resposta.
- **O degrau 3:** a relação e o modelo dos outros decidindo, com a solidão e a aglomeração no corpo (CV-5).
- **Os degraus 4 em diante** (tradição e acima), que pedem gerações.
- **O cheiro do outro.**
- **A agressão entre pets.**
- **A visita do pet de outro jogador,** que fica com o PvP com ghost.
- **A tela.**
- **O ego social** (`docs/futuro/ego_existencia.md`, etapa 7).
