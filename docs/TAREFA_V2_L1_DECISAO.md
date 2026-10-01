# TAREFA V2 — L1-DECISAO (2026-10-01)

Coordenador: chat "Principais jogos Digimon com diálogo" (coordenação da V2). Worker: o mesmo da L0 (chat B). Worktree e branch: `v2-l1-decisao`.
Status: ABERTA (começa só com o PR #108, L0, na `main`).

## 1. Pergunta

Com o lobo de decisão aprendendo por uma atualização que **depende da política atual** (o feedback do dono como vantagem, não recompensa fixa), donos
coerentes produzem políticas distinguíveis entre si e do aleatório, com decisões explicáveis? Hipótese H1, nó L1 da fase 1b (`docs/PLANO_V2_PESQUISA.md`).

## 2. Depende de

- PR #108 (`PoliticaLobos`, L0) mesclado; PRs #102 e #104 na `main`.
- **Referendo dos gates G3–G6 pelo Matheus** antes da run de **validação** (a calibração pode rodar antes, com o plano commitado).

## 3. Mudança mínima

- `PoliticaLobos` com `ConfigLobos.aprendizado_ligado = True` atualizando **só o lobo de decisão**:
  - atualização do tipo "feedback como vantagem" (gradiente de política com o sinal do dono no lugar da vantagem; referência de literatura verificada:
    MacGlashan et al., COACH, arXiv:1701.06049), em **inteiros**, com passo e teto dos pesos em `ConfigLobos` (PROPOSTO);
  - **um sinal escalar** (elogio +1, bronca −1, chamado como hoje). A versão multidimensional (H-REINF-001) **não** entra: uma mudança por vez;
  - **janela de crédito igual à da v1** (só a última decisão), para isolar a mudança da regra de atualização.
- `motivo.PoliticaComMotivo` passa a aceitar a `PoliticaLobos` (base do G4); a regra de honestidade do motivo é a de hoje (`CLAUDE.md`, "Honestidade do fator").
- **Não muda:** `engine.py`, o bandit, runs da v1, a L0 com aprendizado desligado (os testes G1/G2 da L0 continuam passando), a web.

## 4. Experimento e gate

- Plano de análise **`docs/PLANO_ANALISE_V2_L1.md` commitado antes de qualquer run**, com:
  - **Desenho:** o da arena v1 (`PROTOCOLO_ARENA_V1`: mesmos donos sintéticos, orçamento, 14 dias), trocando o bandit pela `PoliticaLobos`; mais o
    **bandit nas mesmas sementes** como referência da v1 (controle, não braço novo de pesquisa).
  - **Braços obrigatórios pelas decisões de `docs/DEFINICOES_V2.md` (aprovadas pelo Matheus em 2026-10-01):**
    - **"Só cuidado" acoplado (D4, seção 3):** para cada ovo e ambiente do atencioso, mesma semente e as mesmas ações de cuidado nos mesmos ticks
      (alimentar, limpar, levar ao banheiro, tratar lesão, acariciar), copiadas do registro do atencioso, sem elogiar nem repreender. Variante sem
      acariciar como sensibilidade.
    - **Controle de capacidade equivalente sem lobos (D2, seção 2):** mesmo número de pesos inteiros, mesmas entradas, mesma regra de atualização e
      mesmas sementes, numa camada de decisão única; atribuição pelos mesmos grupos de entrada.
  - **Sementes:** calibração **3101…3505** (ajustar passo e teto); validação **4101…4505**, **uma única vez**, depois do referendo.
  - **Métricas e gates (PROPOSTOS, do plano da V2, com as definições de `docs/DEFINICOES_V2.md`):**
    - G3 JSD entre donos coerentes ≥ 0,10 bit com IC fora de 0,02 (`divergencia_politicas`, `jsd_bits`); é convenção do projeto (D1);
    - **G3-T ao lado, sem gate (D1):** acerto na tarefa ensinada (a regra de `donos.julgar_acao`), eficiência amostral (sinais do dono até metade do
      caminho entre o instinto e o máximo) e a política ótima do próprio dono como teto; nova função em `digilab/metrics.py`;
    - **G4 só sobre o aprendido (D3):** fração de decisões em que a diferença entre os pesos atuais e os do prior muda a escolha e é atribuível a um
      fator nomeado; a fração bruta (com o instinto) reportada sem gate; G4 dos lobos × G4 do controle sem lobos, com IC; custo de desempenho do
      gargalo = G3-T dos lobos − G3-T do controle;
    - G5 a divergência se mantém sem mortes e sem lesão **e** acima do "só cuidado" acoplado (no desenho da arena v1 não há morte: registrar isso e medir
      também no motor de educação com lesões, braço próprio);
    - G6 distância ao instinto sem crescer sem limite em 14 dias;
    - análise por norma de reação (intercepto = nível, inclinação = sensibilidade ao ambiente) nos braços ensino × só cuidado (seção 3 das definições).
  - O sha256 de `digilab/policies/lobos.py` e de `digilab/config.py` vai no meta da run (o hash de protocolo não cobre código).
- Artefatos em `artifacts_v2_l1/{calibracao,validacao}/`. GPU: não.
- Parada: G3, G4 ou G5 falhando na validação = resultado negativo registrado; nada de reajustar olhando a validação.

## 5. Entrega

- Testes: `python -m pytest tests/ -q` (inclui os de L0 e `test_engine_nao_foi_alterado`).
- Registro: seção própria no fim do `CLAUDE.md` e do `docs/REGISTRO_DESVIOS.md`.
- **Dois PRs:** (1) plano de análise + código + calibração, antes da validação; (2) validação, depois do referendo. Números com artefato. Aviso ao
  coordenador. Merge só pelo Matheus.

## 6. Fora desta tarefa

Recompensa multidimensional; janela de crédito maior; L2/L3 (peças do Dwarf Fortress); A1; porte para a web (`VERSAO_PET = 11` reservado, só depois do G3–G5).
