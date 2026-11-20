# Resultado — V2: a validação do pet que pensa com o adendo 8 (J5)

> **V2, congelado em 2026-10-30** (tag `v2-final`). O estado em que este documento fica na V3 está em `docs/FECHAMENTO_V2.md`; o
> plano da V3, em `docs/PLANO_V3.md`.

Data: 2026-10-19. Plano: `docs/PLANO_ANALISE_V2_PET_QUE_PENSA.md`, seção 7, com o desenho dos adendos 5, 7 e 8 e os números congelados
do adendo 9. Autorizada pelo Matheus em 2026-10-19, com o **T1 como primário**. **Rodou uma vez.**

**Fonte dos números:** `artifacts_v2_pet_que_pensa/validacao_adendo8/`:
- `validacao.json` (as premissas, os contrastes, o Holm, as categorias e a leitura);
- `meta.json`;
- `<braço>/{medidas,meta}.json`.

As vidas ficam fora do git.

- **O comando:** `python experiments/run_v2_validacao_pet_que_pensa.py --config experiments/configs/v2_pet_que_pensa/validacao_adendo8.json
  --saida artifacts_v2_pet_que_pensa/validacao_adendo8 --processos 4`.
- **O código:** o adendo 9 e a config entraram num commit antes da run (`41ffddf`, sobre a `main` `e762425`). O orquestrador conferiu os
  números da config contra os artefatos da calibração e do piloto do adendo 8.
- **A run:** a árvore limpa, numa worktree própria; Python 3.13.0, Windows.
  - O `meta.json` traz o sha256 do pacote.
  - Os artefatos estão num commit próprio (`9ee7db1`).
- **As sementes:** as bases 55101…55505 com K_u = 10, 50 unidades. São 400 vidas de 12 dias, em 467 s com 4 processos.
- **O replay:** toda vida foi rejogada do disco bit a bit. Os gates de mecanismo (G-SEM-CREDITO, o congelamento, o G2) passaram em toda
  vida.
- **Os números congelados** (adendo 9): `ganho_gosto` = S/2, `g_plano` = S, `Δ_T1` = 0,258 e `Δ_T2` = 0,323. A G-APRENDEU vai pelo acaso
  médio. O bootstrap tem 10.000 reamostragens, semente 4242, agrupado por base, com Holm α 0,05.

## Resumo

- **O G-T1 passa,** o primeiro primário do J5 a passar:
  - o contraste é `q`(P1-plan) − `q`(P1), com média **0,197**, IC95 [0,075; 0,323] e IC90 [0,092; 0,303];
  - o p é 0,0003, e o Holm rejeita;
  - as premissas do T1 passam nos dois braços.
  - O superior do IC90 passa da margem (0,258), então a categoria é **"passa"**, sem o rótulo "abaixo de Δ".
- **O G-T2 é inconclusivo por premissa,** como o plano previa. A G-OPORTUNIDADE do T2 falha (de 15 a 21 de 50 sem busca), e a G-EXPOSICAO
  falha nos três braços com o planejador. O número sozinho cairia em equivalente: média −0,036, IC90 [−0,107; 0,022].
- **Os secundários:**
  - **o G-T1-DESF passa:** `q`(P1-plan-desfecho) − `q`(P1), média 0,177, IC95 [0,073; 0,281], o Holm rejeita;
  - **o G-T1-CONG não passa:** `q`(P1-plan) − `q`(P1-plan-cong), média 0,103, IC95 [0,000; 0,207]. O p é 0,023, e o Holm não rejeita;
  - **os do T2 não passam:** as premissas falham.
- **A leitura da seção 7:** "só o G-T1 passa". O modelo do desfecho funciona; o mapa não foi testado, porque o T2 não mediu.
  - **O aviso do G-T2-HAB:** ele sai com o sinal trocado (média −0,148, IC95 [−0,28; −0,02]), e pela seção 7 isso dá ao primário do T2 o
    aviso "a assinatura não separa".
  - O G-T2 já é inconclusivo por premissa, e a PJ8-4 manda ler o G-T2-HAB com o aviso da visão.
- **O rótulo "pensa"** (R-7) pede os dois primários: não vale.

## 1. As premissas

| premissa | P1 | P1-plan | P1-plan-desfecho | P1-plan-cong |
|---|---|---|---|---|
| G-APRENDEU (`f_antes`, IC95; limiar = o acaso médio) | 0,55 [0,48; 0,63] > 0,341, passa | 0,58 [0,51; 0,65] > 0,343, passa | 0,58 [0,51; 0,65] > 0,343, passa | 0,58 [0,51; 0,65] > 0,343, passa |
| G-OPORTUNIDADE, T1 (sem oportunidade) | 1 de 50, passa | 0 de 50, passa | 0 de 50, passa | 0 de 50, passa |
| G-OPORTUNIDADE, T2 | 15 de 50, **falha** | 18 de 50, **falha** | 21 de 50, **falha** | 16 de 50, **falha** |
| G-EXPOSICAO | 12 de 50, passa | 16 de 50, **falha** | 19 de 50, **falha** | 15 de 50, **falha** |

## 2. Os contrastes

| gate | contraste | unidades com valor | média | IC95 | IC90 | p (Holm) | categoria |
|---|---|---|---|---|---|---|---|
| **G-T1** | `q`(P1-plan) − `q`(P1) | 49 | **0,197** | [0,075; 0,323] | [0,092; 0,303] | 0,0003 (rejeita) | **passa** |
| **G-T2** | `m`(P1-plan) − `m`(P1-plan-desfecho) | 28 | −0,036 | [−0,120; 0,024] | [−0,107; 0,022] | 0,875 | **inconclusivo por premissa** (pelo número: equivalente) |
| G-T1-DESF | `q`(P1-plan-desfecho) − `q`(P1) | 49 | 0,177 | [0,073; 0,281] | | 0,0003 (rejeita) | **passa** |
| G-T1-CONG | `q`(P1-plan) − `q`(P1-plan-cong) | 50 | 0,103 | [0,000; 0,207] | | 0,023 (não rejeita) | não passa |
| G-T2-HAB | `m`(P1-plan) − `m`(P1) | 27 | −0,148 | [−0,280; −0,025] | | 0,987 | não passa (premissas; sinal trocado) |
| G-T2-CONG | `m`(P1-plan) − `m`(P1-plan-cong) | 29 | −0,046 | [−0,155; 0,024] | | 0,877 | não passa (premissas) |

## 3. O descritivo do T1 (não é teste)

| | P1 | P1-plan | P1-plan-desfecho | P1-plan-cong |
|---|---|---|---|---|
| `f_antes` (média) | 0,553 | 0,580 | 0,580 | 0,580 |
| `f_depois` (média) | 0,565 | 0,403 | 0,423 | 0,507 |
| `q` (média) | −0,014 | 0,177 | 0,157 | 0,073 |

- **O hábito sozinho (P1) não revaloriza:** depois que a x passa a fazer mal pela mão, ele a escolhe igual.
- **Os braços com o planejador revalorizam:** a escolha da x cai de 0,58 para 0,40.
- **O P1-plan-desfecho cai quase o mesmo** que o P1-plan. Ele tem o mapa congelado em `T_m` e o desfecho aprendendo, então quem leva a
  revalorização à escolha é o modelo do desfecho.
- **O P1-plan-cong** (os dois modelos congelados em `T_m`) cai menos, 0,58 para 0,51. O G-T1-CONG não passa: com os modelos congelados,
  ainda sobra uma parte da queda.

## 4. O custo

O CPU por vida de 12 dias foi 0,90 s no P1 e de 1,09 a 1,10 s nos braços com o planejador.

## 5. Leitura (seção 7 do plano)

- **"Só o G-T1 passa":** o modelo do desfecho funciona e leva a revalorização pela mão à escolha.
  - O pet com o planejador deixa de escolher a fruta que passou a fazer mal, e o pet só com o hábito não deixa.
  - O G-T1-DESF passando confirma que o desfecho sozinho basta para isso.
- **O mapa não foi testado:** o T2 não mediu, porque as premissas de oportunidade e de exposição falharam. O resultado não diz que o mapa
  não funciona.
- **O G-T1-CONG não passa:** a queda no P1-plan não se explica toda pelo modelo que aprendeu depois de `T_m`. Parte dela aparece mesmo
  com os modelos congelados. É leitura do número, não do gate.
- **O rótulo "pensou" na tela** (R-7) pede os dois primários e o fator do plano no motivo. Com o T2 inconclusivo, não vale.
- **Nada foi ajustado olhando a validação.**

## 6. A decisão do Matheus: o Gate C aprovado em parte (2026-10-21)

**O Matheus decidiu em 2026-10-21, pela recomendação do Gerente: o Gate C fica APROVADO EM PARTE.**
- **O que está demonstrado:** a revalorização pelo planejador. O G-T1 passa, e o G-T1-DESF mostra que o modelo do desfecho sozinho basta
  para ela (seção 5).
- **O que fica pendente:** a busca, o T2 (o mapa). Ela não foi medida, porque as premissas falharam, e fica para um plano próprio, ainda
  sem tarefa. O resultado não diz que o mapa não funciona.
- **O que isso libera:** a P4 do `docs/futuro/mundo_3d.md` (o cérebro A no mundo 3D) com o planejador. O esboço da tarefa está em
  `docs/TAREFA_V2_P4_CEREBRO_MUNDO.md`.
- **O que não muda:**
  - o rótulo "pensa" (R-7) continua sem valer, porque pede os dois primários;
  - os números acima são os da validação, e nada foi refeito.
