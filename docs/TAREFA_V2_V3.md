# TAREFA V2 — V3 (2026-10-19)

> **V2, congelado em 2026-10-30** (tag `v2-final`). O estado em que este documento fica na V3 está em `docs/FECHAMENTO_V2.md`; o
> plano da V3, em `docs/PLANO_V3.md`.

Coordenador: ChatGPT Work. Worker: Claude Code. Worktree e branch: `v2-v3`. Status: ABERTA.

Categoria: arquitetura. Origem: Matheus, 2026-10-19: investigar como ampliar as oportunidades de decisão do pet à luz do diagnóstico do PR #332 e preparar uma proposta segura para o DigiBrain V3.

## 1. Pergunta

Na fase 1 da H1 (plasticidade durante a vida versus predisposições herdadas), como aumentar as oportunidades de escolha e o repertório de comportamentos sem confundir número de ações com capacidade de aprender, nem alterar a referência do cérebro A?

A hipótese do Matheus — que poucas ações podem contribuir para os problemas do aprendiz — é uma hipótese a investigar, não uma conclusão. O ponto de partida é o diagnóstico E0 do PR #332 e `docs/futuro/digibrain_v3_e0.md`. O desenho do DigiBrain V3 no #332 permanece **PROPOSTO**; esta tarefa é uma investigação documental aberta.

## 2. Depende de

- PR #332 incorporado à `main`: auditoria E0 e desenho PROPOSTO do V3.
- Ler `CLAUDE.md`, `docs/INDICE.md`, `docs/PAINEL_V2.md`, `docs/ROADMAP_V2.md`, `docs/futuro/digibrain_v3_e0.md`, `digilab/policy.py`, `digilab/events.py` e `digilab/policies/lobos.py`.
- Considerar o estado atual do J1 e do J5 no painel. O J1 é negativo; a validação do J5 segue inconclusiva por premissa. Não tratar o planejamento de alvo como capacidade validada.
- Nenhuma decisão nova do Matheus é pré-requisito para esta investigação documental.

## 3. Mudança mínima

Criar `docs/futuro/v3_espaco_acoes.md`, uma proposta de arquitetura que:

1. Faça o inventário do que o cérebro A pode escolher hoje: as sete ações de `ACOES_PET_HOJE`, a ação de banheiro sob chave, as regras do instinto, os candidatos por regra e as ações com alvo já disponíveis no mundo.
2. Explique a distinção entre:
   - ampliar o conjunto de ações primitivas;
   - permitir que mais propostas existentes concorram, em vez de uma regra fechar a decisão;
   - criar ações parametrizadas, subdecisões ou objetivos compostos, como escolher um alvo para buscar.
3. Use o E0 corretamente: 55,3% de candidatos únicos, dos quais `sono_continuar` representa 34,6% do total; onde há escolha, o termo aprendido muda a ação em 34,8%. Esses dados são descritivos, sem plano, gate, intervalo ou replicação e não demonstram que o aprendiz melhora o desempenho.
4. Compare os mecanismos já propostos no E0:
   - R1: competição entre regras, preservando o `sono_exaustao` como regra forçada de segurança;
   - R2: crédito temporal que pula decisões forçadas e funcione com os canais, sem presumir que o traço existente resolveu o problema;
   - expansão futura por objetivos ou ações contextuais ligadas a comida, objetos, investigação e interação social.
5. Para cada família candidata, descreva a affordance necessária no mundo, o que o pet percebe, a consequência que pode aprender e o teste que permitiria distingui-la de mera variedade superficial. Identifique dependências de J1/J5, mundo 3D ou dois pets.
6. Recomende uma sequência mínima e critérios mensuráveis: distribuição do número de candidatos por regra/contexto, proporção de decisões forçadas, entropia/diversidade condicionada ao contexto, crédito que realmente atualiza pesos e desempenho em tarefa/homeostase. Não use diversidade bruta como objetivo isolado.
7. Separe explicitamente fatos implementados, resultados observados, hipóteses e propostas. Apresente as decisões que ainda cabem ao Matheus com recomendação e custo de errar.

**Direção a avaliar, sem assumir como decidida:** o E0 aponta que abrir oportunidades de escolha nas regras que hoje retornam uma única ação pode ter mais alcance imediato do que simplesmente acrescentar verbos ao enum. Uma expansão posterior pode usar objetivos/subdecisões — buscar e escolher comida, investigar algo incerto, ou interagir com objeto/pet — desde que exista percepção e consequência correspondentes.

A proposta não pode adicionar membros a `AcaoPet` nem modificar o bandit congelado. O ROADMAP V2 registra esse limite: ações novas no experimento precisam ser modeladas sem quebrar a reprodução da V1. A tarefa deve apresentar alternativas e deixar a escolha de arquitetura como PROPOSTA.

## 4. Experimento e gate

Não há run nesta tarefa. Não criar plano de análise nem selecionar números de calibração ou validação.

Se a investigação recomendar um experimento, definir apenas a pergunta, os contrastes necessários e as métricas candidatas. O plano de análise e as faixas de sementes são uma tarefa posterior, antes de qualquer run.

## 5. Entrega

- Novo documento: `docs/futuro/v3_espaco_acoes.md`.
- Revisar se a proposta é consistente com o E0, os contratos existentes e o estado descrito no painel.
- PR contra `main`, categoria `arquitetura`, preenchendo todas as seções do modelo do PR. Declarar que nenhum código, teste de comportamento ou experimento foi executado se esse for o caso.
- Registrar interpretação/desvio no arquivo mensal e no índice, se houver achado novo; não alterar `CLAUDE.md`, `PAINEL_V2.md` nem o roadmap nesta tarefa.
- Ao concluir, parar e devolver ao coordenador o resumo, os arquivos, as evidências e as decisões abertas.

## 6. Fora desta tarefa

- Implementar R1, R2 ou ações novas.
- Alterar `digilab/engine.py`, `AcaoPet`, o bandit, a web ou qualquer versão de pet.
- Rodar calibração, piloto ou validação; selecionar sementes; mexer em faixas reservadas.
- Declarar que o J5, a curiosidade, a interação social ou o mundo 3D já validaram os comportamentos descritos.
- Tomar as decisões V3-3/V3-4 do PR #332 em nome do Matheus.

## 7. Critérios de aceitação

- O documento diferencia claramente falta de alternativas, prioridade fixa, falta de affordances e limites de crédito.
- Cada ação/capacidade sugerida está marcada como existente, proposta ou dependente de validação.
- A proposta não apresenta o E0 como experimento confirmatório nem como prova de melhora.
- As opções priorizadas têm percepção, consequência e métrica de avaliação identificáveis.
- Não há mudança de comportamento ou quebra dos limites de pesquisa acima.

## 8. Precisa do Matheus

Nenhuma decisão para produzir esta análise. Se a proposta recomendar iniciar a implementação do R1, levar V3-3 e V3-4 ao Matheus, cada uma com recomendação e custo de errar; não interpretar este PR como aprovação para implementar ou rodar experimento.
