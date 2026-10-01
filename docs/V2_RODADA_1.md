# V2 — marco da rodada 1 (2026-10-01)

Coordenação: `docs/V2_TRABALHO_PARALELO.md`. Quatro frentes, sem run estatística e sem GPU. Todas entregaram; nenhum PR mesclado ainda.

## O que passou

| frente | PR | entrega | números (com artefato, no PR) |
|---|---|---|---|
| F0-INVENTARIO | #106 | `docs/V2_INVENTARIO_JOGO.md`: mecânicas, decisões do pet, candidatas à 1a | 96 decisões de vida por dia, uma só da política; 548/548 pets da V3 ariscos; recomendação: **bola** |
| L0-LOBOS | #108 | `digilab/policies/lobos.py`, `ConfigLobos`, `tests/test_lobos.py` | G2 byte a byte com o instinto em 20 vidas × 2 motores; G1 replay; 490 pesos inteiros; suíte 594 + 1 pulado |
| F0-VINCULO | #109 | `docs/V2_VINCULO_PROPOSTA.md`, `experiments/analisar_vinculo.py`, `artifacts_v2_vinculo/` | causa: atendimento e desejo só amostram em falta; "previsibilidade" leva atencioso − aleatório de −0,069 a +0,223 (contrafactual) |
| F0-CORPUS | #107 | 49 itens reescritos em português, nenhum removido | itens no estilo 455 → 504; não latinos 49 → 0 |

## Observações do coordenador

- **#109 lê logs fora do repositório** (`D:/Trab/digilab/arquivo/`): o artefato só se reproduz nesta máquina. Aceitável para diagnóstico; a frente que
  implementar o vínculo novo mede em vidas novas, com plano.
- **#108:** o controle do G2 no `MotorPersonalidade` é um instinto com gancho vazio definido no teste (o instinto puro não roda nesse motor). Registrado no PR.
- **Contagem do corpus:** a tarefa dizia 46; eram 49 (o "3ª" conta como letra não latina). Corrigido pelo worker.

## Decisões pendentes do Matheus

1. **Interação da fase 1a:** bola (recomendada: a consequência fica fora da cadeia que leva à morte, então o G5 é satisfazível por desenho) ou comida posta.
2. **Vínculo:** A (só previsibilidade), B (previsibilidade com o desejo) ou outra (`docs/V2_VINCULO_PROPOSTA.md`, seção 5).
3. **Referendo** dos gates G3–G6 do plano da V2 (necessário antes da validação da L1).
4. Merges: #104 → #102 → #105 → #106 → #107 → #108 → #109.

## Rodada 2 (divisão)

| chat | frente | tarefa | começa quando |
|---|---|---|---|
| B | L1-DECISAO | `docs/TAREFA_V2_L1_DECISAO.md` | #108 na `main` (validação só depois do referendo) |
| D | GPU-ESTILO | `docs/TAREFA_V2_GPU_ESTILO.md` (fila da GPU: 1) | #107 na `main` |
| A | F0-LIMPEZA | `docs/TAREFA_V2_F0_LIMPEZA.md` | #102 a #107 na `main` |
| C | aguarda | vínculo novo (implementação) ou A1, conforme as decisões 1 e 2 | decisão do Matheus |

Reservas: `VERSAO_PET` 10 = lobos na web (depois do L1), 11 = vínculo novo, 12 = interação da 1a. Sementes do comando com estilo: 20261501, 20261601,
20261701. Sementes da L1: calibração 3101…3505, validação 4101…4505 (uma vez).
