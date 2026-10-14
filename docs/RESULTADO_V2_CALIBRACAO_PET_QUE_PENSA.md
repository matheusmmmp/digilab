# Resultado — V2: a calibração do `g_plano` e o piloto do pet que pensa (J5)

Data: 2026-10-13. Plano: `docs/PLANO_ANALISE_V2_PET_QUE_PENSA.md`, seções 5 e 6, e o adendo 1 com os números desta run. Autorizada pelo
Matheus em 2026-10-13.

**Fonte dos números:** `artifacts_v2_pet_que_pensa/calibracao/`, com estes arquivos:
- `g_plano.json`, `g_plano_<g>/{medidas,meta}.json` e o `meta.json` da calibração;
- `piloto/piloto.json`, `piloto/<braço>/{medidas,meta}.json` e o `meta.json` do piloto.

As vidas (`vidas/*.jsonl`) ficam fora do git e saem de novo da config e do código.
- **Os comandos:**
  - `python experiments/run_v2_calibracao_pet_que_pensa.py --config experiments/configs/v2_pet_que_pensa/calibracao.json --saida artifacts_v2_pet_que_pensa/calibracao --processos 3`;
  - o mesmo, com `--piloto --processos 4`.
- **A run:** Python 3.13.0, Windows.
  - A calibração usou o código da `main` `ac8fa3e` (o artefato está no commit `61d0be4`) e levou 39 s.
  - O piloto usou o `0b1e226` e levou 111 s.
- **O replay:** toda vida foi gravada e rejogada a partir do texto do disco, bit a bit, e o replay da medição também foi conferido.
  Nenhuma divergência. Os gates de mecanismo (G-SEM-CREDITO, o congelamento, o G2) passaram em toda vida.

## Resumo

- **O `g_plano` = S (1024), fechou.** É o único ponto da grade em [0,10; 0,40], e por pouco: 0,1001.
- **O T1 não tem espaço:** nenhum braço escolhe a x antes da mudança (`f_antes` = 0 em toda unidade com oportunidade), então `Δ_T1` = 0.
- **O T2 não tem medida:** nenhuma unidade de nenhum braço teve busca da x depois da mudança.
- **Pela seção 6, a validação não roda, e o plano volta ao Matheus.** O N não foi calculado.

## 1. A calibração (só o P1-plan, só a fase 1)

| `g_plano` | média da fração (dias 4 a 6) | por unidade | decisões com alvo | o plano mudou a escolha |
|---|---|---|---|---|
| S/4 (256) | 0,0518 | 0,000 a 0,104 | 1.005 | 52 |
| S/2 (512) | 0,0410 | 0,000 a 0,123 | 1.041 | 45 |
| **S (1024)** | **0,1001** | 0,021 a 0,222 | 1.035 | 104 |

- Nenhuma unidade ficou sem decisão com alvo na janela.
- A fração não sobe de S/4 para S/2. Com 20 unidades e ~50 decisões com alvo por unidade na janela, essa diferença fica dentro do ruído.

## 2. O piloto (os 4 braços, T1 e T2, no `g_plano` = S)

**As premissas (só relato):**

| braço | T1: unidades com oportunidade antes / depois | `f_antes` do T1 | T2: unidades com busca antes / depois | expostas no T2 |
|---|---|---|---|---|
| P1 | 14 / 15 | 0 | 5 / 0 | 11 |
| P1-plan | 12 / 14 | 0 | 7 / 0 | 13 |
| P1-plan-desfecho | 12 / 14 | 0 | 7 / 0 | 13 |
| P1-plan-cong | 12 / 14 | 0 | 7 / 0 | 13 |

- **G-APRENDEU falha em todos:** o IC95 de `f_antes` é [0; 0].
- **G-OPORTUNIDADE falha em todos:** ficam sem oportunidade de 30% a 45% das unidades no T1 e 100% no T2.
- **G-EXPOSICAO falha:** de 35% a 45% das unidades não viram a x perto de uma árvore nova até o fim da janela.

**As margens:** `Δ_T1` = 0,000 e `Δ_T2` = 0,214. O T1 fica sem espaço (≤ 0,05).

**Quanto o plano decide na vida inteira** (descritivo):
- nos três braços com o planejador, o plano muda a escolha em ~8% das decisões com alvo (de 288 a 305 em ~3.700);
- o fator do plano aparece em ~1% das decisões (de 176 a 185 em 19.200);
- no P1, em nenhuma (o G2).

**O custo:** 0,62 s de CPU por vida de 10 dias.

## 3. Por que a x nunca é escolhida (descritivo, 4 unidades do P1-plan no T1)

Rejogando as vidas com o registro da medição:
- o pet come sobretudo ração: de 72 a 82 rações por vida, contra 0 a 2 vezes a x;
- nas oportunidades do T1 (fome ≤ S/2, a x à vista ou uma árvore da x lembrada, e outro alvo), o alvo é quase sempre a ração do comedouro,
  que o dono atencioso põe perto de onde o pet passa o dia;
- quando o explorar escolhe uma árvore pela memória, ela é de outro tipo.

O pet não chega a ligar a x ao bem que ela faz, porque quase não a come. A ração está sempre à mão, e o planejador soma pouco.

## 4. O que fica para o Matheus

- **O plano volta pela seção 6:** o T1 está sem margem, e o T2 sem busca depois da mudança.
- **Opções (para decisão, não aplicadas):**
  - mudar o desenho para a x ter chance de virar hábito (por exemplo, um dono que não põe a ração no comedouro, ou a ração mais longe);
  - medir o T1 pela escolha de comer a x quando ela está à vista, sem exigir a fome ≤ S/2;
  - aceitar o resultado como negativo para o J5 neste mundo.
- **Nada foi recalibrado olhando o piloto.**
