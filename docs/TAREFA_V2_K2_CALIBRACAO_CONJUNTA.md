# TAREFA V2 — K2-CALIBRACAO-CONJUNTA (2026-10-05)

Coordenador: chat "Principais jogos Digimon com diálogo". Worker: chat B. Worktree e branch: `v2-k2-calibracao-conjunta`. Status: ABERTA.
Etapa K2 do `docs/ROADMAP_V2.md`; plano `docs/PLANO_CALIBRACAO_CONJUNTA_V2.md` (K-1 a K-11 decididas). Sementes **14101…14505, K = 4**,
só de calibração; as de validação (15101…15505) não se tocam.

## 1. Duas partes

1. **Agora, sem esperar:** o orquestrador `experiments/run_v2_calibracao_conjunta.py` (nome PROPOSTO), pela bancada.
   - As etapas A1, A2, B, C e D da seção 3 do plano, com as regras de escolha **exatamente** como registradas.
   - Os resultados em `artifacts_v2_calibracao_conjunta/`.
   - O replay de cada vida conferido a partir do disco.
   - O adendo de tamanho de amostra (seção 5) calculado no fim.
   - Testes com fumaça nas sementes dos testes.
2. **A run**, só depois do merge do PR do chat D (`docs/TAREFA_V2_BANCADA_K4_CANAIS.md`: o K4 fora do orçamento e os canais na bancada).
   - Atualize o branch com a `main` e rode uma vez, numa worktree própria.
   - A estimativa do plano é de ~2 h.

## 2. Regras

- O plano vem antes da run e já está na `main`. Qualquer desvio vai no `REGISTRO_DESVIOS.md`, num commit **antes** de rodar.
- Nada é escolhido olhando uma predição primária: a `taxa_fruta_ruim` e os contrastes da seção 6 do experimento maior não entram em
  nenhuma regra.
- Se uma etapa não fechar, use a regra de reserva do plano, registre e siga.
- O resultado vai em `docs/RESULTADO_V2_CALIBRACAO_CONJUNTA.md`:
  - o ponto escolhido;
  - o N da validação (seção 5.3);
  - se esse N cabe nas 12 h (K-10). Se não couber, pare e pergunte ao Matheus pelo PR.

## 3. Entrega

Um PR (orquestrador, run e resultado) com o relato no corpo e a suíte inteira, mais uma seção no fim do `CLAUDE.md` e do
`REGISTRO_DESVIOS.md`. Merge só pelo Matheus. Próximo para o B (rodada 11): a validação única (V1).
