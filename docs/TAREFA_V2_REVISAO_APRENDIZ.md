# TAREFA V2 — REVISAO-APRENDIZ (2026-10-04, para a rodada 6)

Coordenador: chat "Principais jogos Digimon com diálogo". Worker: chat B (é dono de `lobos.py`). Worktree e branch:
`v2-revisao-aprendiz`. Status: **RESERVADA**. Começa depois do LOBOS-MUNDO (`docs/TAREFA_V2_LOBOS_MUNDO.md`) na `main` e **antes** da
calibração do experimento maior.

## 1. Pergunta

O que segura o aprendiz é o teto dos pesos, a janela de crédito ou a falta de exposição? Diagnóstico pedido pelo Matheus em 2026-10-04,
depois das rodadas 3 e 4:
- **teto:** pesos presos no limite em 12 de 20 vidas na L1 (`artifacts_v2_l1/validacao/`) e em 20 de 20 no N3
  (`artifacts_v2_n3/validacao/`);
- **instinto decidindo quase tudo:** cerca de 80% das decisões na L1 (`docs/RESULTADO_V2_L1.md`);
- **janela de crédito:** o sinal só vê o efeito imediato da ação (N3); a privação depende do cuidado do dono;
- **exposição:** p(comer | fruta no cenário) 0,208 (`artifacts_v2_n4/validacao/`).

O computador não é o gargalo: as runs da V2 levam minutos em CPU.

## 2. Mudança mínima

- Três alavancas, **uma por vez**, atrás de campos da `ConfigLobos`/`ConfigConsequencia`, com o padrão de hoje reproduzindo byte a byte:
  1. **teto dos pesos** (hoje 1·S): teto maior, ou teto relativo ao peso do prior;
  2. **janela de crédito:** além do efeito imediato, a consequência atrasada (um traço de elegibilidade curto, em inteiros), como variante
     declarada no plano do N3;
  3. **exposição:** grade maior de `w_fruta` (decisão N2) e, se preciso, mais ofertas por dia.
- Nada novo no mundo, nenhum objeto novo.

## 3. Experimento

- Plano de análise `docs/PLANO_ANALISE_V2_REVISAO_APRENDIZ.md` commitado antes de qualquer run.
- **Só sementes de calibração** (as do experimento maior, 14101…14505, ou uma faixa nova reservada pelo coordenador). Isto é um
  diagnóstico para escolher o ponto do experimento maior, não uma validação.
- Medidas: fração de decisões em que o aprendido decide; vidas com peso no teto; G6; desempenho no ambiente; tudo por braço (P1, P3) no
  mundo das frutas (casado e descasado).

## 4. Entrega

Um PR com o diagnóstico e o ponto recomendado para a calibração do experimento maior. Relato no corpo do PR. Merge só pelo Matheus.

## 5. Fora desta tarefa

Variedade de frutas (fator do experimento maior, seção 2 do plano), objetos novos, N6, N7.
