# TAREFA V2 — K4-DONO-JULGA-FRUTA (2026-10-05)

> **V2, congelado em 2026-10-30** (tag `v2-final`). O estado em que este documento fica na V3 está em `docs/FECHAMENTO_V2.md`; o
> plano da V3, em `docs/PLANO_V3.md`.

Coordenador: chat "Principais jogos Digimon com diálogo". Worker: chat A. Worktree e branch: `v2-k4-dono-julga-fruta`. Status: ABERTA.
Decisão K-11 de `docs/PLANO_CALIBRACAO_CONJUNTA_V2.md` (aprovada em 2026-10-05); contrato K4 e decisão E7 de
`docs/PLANO_ANALISE_V2_EXPERIMENTO_MAIOR.md` (seção 1).

## 1. Pergunta

No experimento maior, o dono dos braços P2, P2e e P3 sabe o mesmo efeito real das frutas. No P2 ele **informa** esse efeito; no P3 ele
**julga a escolha**: elogia o consumo da fruta boa e repreende o da ruim, além da tarefa de sempre (`donos.julgar_acao`). Hoje o dono do P3
não sabe das frutas. Sem isso, P2 × P3 compara canal e conhecimento juntos.

## 2. Mudança mínima (só `frutas.py` e os donos; `config.py` se precisar de chave)

- Um dono sintético (ou uma opção do atencioso) que, depois de cada consumo de fruta, julga pelo **efeito real vigente** no tick (no
  mutável, o de antes ou o de depois da troca): elogia a fruta boa, repreende a ruim e não faz nada com a neutra.
- **Orçamento:** o julgamento da fruta usa as ações `elogiar`/`repreender` de sempre e **conta no orçamento**, como o resto do feedback do
  P3. Se isso tirar ações da tarefa, registre quanto e proponha a alternativa (fora do orçamento, como as informações) para o Matheus decidir.
  Escolha uma, registre no `REGISTRO_DESVIOS` e deixe a outra atrás de opção.
- O momento: o primeiro passo do dono depois do consumo (como a bronca do `DonoPedinte`). O sinal chega ao aprendiz pelo `receber_acao_dono`
  e pela janela de crédito de sempre; documente a que decisão ele é creditado.
- O conhecimento vem dos mesmos efeitos reais que o `InformanteDoMundo` do P2 usa (`Bancada.efeitos_reais`): a mesma fonte.
- **Não muda:** `engine.py`, `AcaoPet`, `lobos.py` (B), `bancada_v2.py` (D liga na rodada 10), a web.

## 3. Gates (mecanismo; só as sementes dos testes)

- G1 com o julgamento.
- Chave desligada (ou o dono sem o julgamento) = vida de hoje byte a byte, por gabarito gravado antes da mudança.
- O julgamento segue o efeito real vigente (também dos dois lados da troca do mutável), um por consumo, no passo seguinte.
- O P2 e o P3 da mesma unidade conhecem o mesmo efeito (teste).

## 4. Entrega

Um PR, com o relato no corpo e um bloco "para o chat D" dizendo como montar o P3 com o julgamento. Suíte inteira. Seção no fim do `CLAUDE.md`
e do `docs/REGISTRO_DESVIOS.md`. Merge só pelo Matheus. Próximo para o A (rodada 10): o cérebro C (Fly-like).
