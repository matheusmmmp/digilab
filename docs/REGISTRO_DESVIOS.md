# Registro de desvios de pré-condição e de interpretação

## 2026-09-24 — TAREFA_MEMORIA_EXPRESSAO iniciada com a bateria do combate V2 REPROVADA

- Pré-condição da Parte A (`docs/TAREFA_MEMORIA_EXPRESSAO.md`): bateria do combate V2
  **APROVADA** em `artifacts_combate_v2/gates.json`.
- Estado em disco no início da tarefa: `status = REPROVADA`, `falharam = [G4_ritmo,
  G5_sem_acao_morta]` (conjunto de validação; commit `8f61e52` na `main`).
- Decisão do pesquisador (Matheus, em conversa): seguir a tarefa **ignorando a reprovação**,
  mantendo este registro. Nada na bateria nem nos artefatos do combate V2 foi alterado.
- Consequência: a expressão de combate é exercitada sobre um combate que ainda não passou no
  próprio portão (31,3% das partidas no limite de turnos; `esquivar` quase não aparece nas
  decisões dos bots do suporte). Resultados de legibilidade no combate herdam essa limitação.

## 2026-09-24 — interpretações adotadas na Parte A (propostas antes de começar)

- `PoliticaInstinto`: a regra que disparou fica em atributo somente leitura (`ultima_regra`),
  não em `estado_interno()`, para não alterar `artifacts_ablacao/vidas/*.politica.json`.
- Bandit: a decisão é argmax de `log(prior) + valor amostrado + Gumbel`. O fator só é atribuído
  se o termo de valor **mudou** a escolha (sem ele, a ação seria outra); caso contrário o motivo
  fica sem fator, porque quem decidiu foi o prior/ruído e citar um peso seria inventar causa.
  A fração sem essa checagem também é reportada.
- `hora_sin` e `hora_cos` somam contribuição num único fator `hora`; o intercepto vira o fator
  `habito` (preferência aprendida pela ação, independente do estado).
- Os docs foram copiados de `D:\Trab\digilab\*.md` para `docs/`, onde a tarefa os referencia.
