# TAREFA V2 — N6-PLANO (2026-10-04)

Coordenador: chat "Principais jogos Digimon com diálogo". Worker: chat C. Worktree e branch: `v2-n6-plano`. Status: ABERTA.
**Só papel: nenhuma run, nenhum código.**

## 1. Pergunta

O plano de análise do **N6, memória** (`docs/ROADMAP_V2.md`, R6.2; `docs/ARQUITETURA_V2_VALIDACAO.md`, nó N6): um episódio do mundo das
frutas, **recuperado**, muda a decisão do pet com o estado atual igual, além de uma janela de recência?

## 2. Entrega

**`docs/PLANO_ANALISE_V2_N6.md`:**
- Os **quatro marcos** separados (`docs/research/digibrain/mechanisms/episodic_memory.md`): registrado, codificado, recuperado, causal.
- **O que é um episódio** no mundo das frutas (por exemplo, "comi a fruta X e o humor caiu"), onde mora (lobo de memória e emoção, hoje com
  contribuição zero) e como chega à decisão. Espaços como regra de engenharia (D7); desempate explícito.
- **Controles:** recuperação relevante, nenhuma, só recência e embaralhada (H-MEM-001), com o "só cuidado" acoplado.
- **Gates** e o que conta como confirmar, refutar ou inconclusivo; a fração de motivos que citam memória contra os 6,9% da v1
  (`artifacts_v1_memoria_espacos/metrics.json`).
- **Sementes:** proponha faixas novas para o coordenador fechar (não use as reservadas).
- **Ligação com a fala:** H-MEM-02 (a memória que o jogador vê é a que decide), só como pergunta registrada.
- No fim, as decisões que só o Matheus pode tomar, com recomendação e custo de errar.

## 3. Regras

Referências só VERIFICADAS (Castro e Gudwin, `10.4018/jse.2013010102`; o resto do corpus como pista); nenhuma alegação de novidade; números
só com artefato.

## 4. Fora desta tarefa

Código, runs, o N7.
