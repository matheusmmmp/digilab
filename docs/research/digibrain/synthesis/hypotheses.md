# Registro de hipóteses

Toda linha é **HIPÓTESE DIGILAB**, PROPOSTO. Nenhuma é promovida a DECIDIDO ou EXECUTADO por leitura de literatura. Uma
hipótese só roda com tarefa e plano de análise commitados antes, numa versão de pet própria.

## A pergunta maior

**H-PLASTICITY:** em que condições a plasticidade durante a vida produz vantagem adaptativa sobre as predisposições herdadas?
Braços P0 (só herdado), P1 (só consequências), P2 (ensino contextual certo), P2e (ensino contextual errado), P3 (feedback
explícito); eixo de ambiente casado × descasado × mutável. Desenho: `docs/ARQUITETURA_V2_VALIDACAO.md`, seção 6.

## Por mecanismo

| ID | pergunta curta | arquivo | depende de | estado |
|---|---|---|---|---|
| H-R1 | reforço escalar basta | `reinforcement.md` | N3 | PROPOSTO |
| H-R2 | multidimensional vence escalar (antiga H-REINF-001) | `reinforcement.md` | H-R1 | PROPOSTO |
| H-R3 | homeostático + hedônico explica além da necessidade | `reinforcement.md` | frutas | PROPOSTO |
| H-R4 | genoma modula a sensibilidade por canal | `reinforcement.md` | H-R2 | PROPOSTO |
| H-R5 | canal de combate com freio próprio | `reinforcement.md` | H-R4 | PROPOSTO |
| H-HED-01 | nutrição e valor hedônico independentes por item | `hedonic_system.md` | definições das frutas | PROPOSTO |
| H-HED-02 | consequência atualiza preferência | `hedonic_system.md` | H-HED-01 | PROPOSTO |
| H-HED-03 | saciedade sensório-específica sem passar pela fome | `hedonic_system.md` | H-HED-01 | PROPOSTO |
| H-HED-04 | neofobia do ovo, preferência aprendida | `hedonic_system.md` | H-HED-01 | PROPOSTO |
| H-HED-05 | vício como assimetria querer × gostar | `hedonic_system.md` | H-HED-01..03 | PROPOSTO |
| H-HED-06 | genoma modula o canal hedônico | `hedonic_system.md` | H-R4 | PROPOSTO |
| H-HOM-01 | redução de déficit como reforço ensina | `homeostasis.md` | N1 (regra de atualização) | PROPOSTO |
| H-HOM-02 | necessidade modula a expressão do aprendido | `homeostasis.md` | H-HOM-01 | PROPOSTO |
| H-ACT-001 | seletor modular × atual, capacidade igual | `action_selection.md` | — | parcialmente coberta pela L0/L1 |
| H-ACT-02 | circuitos por classe de estímulo | `action_selection.md` | mundo com ameaça, social e objeto | IDEIA |
| H-ACT-03 | duas prioridades (L3) | `action_selection.md` | L1 | PROPOSTO |
| H-ASSOC-01 | aprende e inverte associações | `associative_memory.md` | N3 | PROPOSTO |
| H-ASSOC-02 | memórias separáveis por canal | `associative_memory.md` | H-R2 | IDEIA |
| H-MEM-001 | episódio recuperado muda a decisão | `episodic_memory.md` | L1 | PROPOSTO |
| H-MEM-02 | memória autobiográfica = memória causal | `episodic_memory.md` | H-MEM-001 | IDEIA |
| H-BODY-01 | consequências fiéis dispensam corpo de baixo nível | `body_feedback.md` | inventário | PROPOSTO |
| H-PERS-001 | personalidade de genoma × história | `personality.md` | H-R4 | PROPOSTO |
| H-PERS-02 | sensibilidade por canal > eixos configurados | `personality.md` | H-R4 | IDEIA |
| H-PLAST-001 | herdar a capacidade de aprender | `genome_plasticity.md` | fase 3 | BLOQUEADA até a fase 3 |
| H-GEN-01 | = H-R4, lado do genoma | `genome_plasticity.md` | H-R2 | PROPOSTO |
| H-GEN-02 | genoma define fisiologia e prior | `genome_plasticity.md` | fase 3 | IDEIA |
| H-TEACH-001 | aprender por consequência sem elogio/bronca | = braço P1 | N3 | PROPOSTO |
| H-TEACH-002 | informação do dono como incerta, validada pela consequência | = braços P2/P2e | N5 | PROPOSTO |
| H-BRAIN-01 | DigiBrains A × B × C, mesmo mundo e mesmas sementes | `brain_comparison.md` | marco da fase 1 | IDEIA |

## Fechadas (não reabrir)

A hipótese central da v1 (REFUTADA); a pergunta do efeito do dono neste motor (ENCERRADA); calibrações de forma ou de peso do
caráter atrás de efeito do dono; a "V4" do E1; a linhagem com o genoma da v1.
