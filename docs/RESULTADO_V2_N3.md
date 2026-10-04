# Resultado — V2, N3: a consequência da própria ação como sinal, braço P1 (validação, 2026-10-04)

Plano: `docs/PLANO_ANALISE_V2_N3.md` (registrado antes de qualquer run). Tarefa: `docs/TAREFA_V2_N3_CONSEQUENCIA.md`. Validação **única**
nas sementes 9101…9505, no ganho escolhido pela calibração (4; a calibração **não fechou**: `artifacts_v2_n3/calibracao/escolha.json`).
**Nada foi reajustado olhando a validação.** Pela decisão do Matheus de 2026-10-01, a falha é registrada e não para a V2. Números de
`artifacts_v2_n3/validacao/` (`escolha.json`, `meta.json`, `ganho4/resultado.json` e, da bancada, `ganho4/{medidas,tabelas,meta}.json` e
`vidas/*.jsonl`; os `vidas/*.politica.json` ficam fora do git, regeneráveis por replay, que a bancada confere bit a bit). Windows,
Python 3.13.0; sha256 de `lobos.py` `bf4391d31185…`, `config.py` `695e49291fa9…` (`meta.json`).

## 1. Gates (PROPOSTOS, plano seção 5)

| gate | definição | validação (9101…9505) | calibração (8101…8505) | resultado |
|---|---|---|---|---|
| **G-P1** privação | por semente, média nos 4 donos de (privação P0 − privação P1) | **+0,0008 [−0,0067; +0,0077]** | +0,0051 [+0,0008; +0,0091] | **FALHA** (o IC cruza zero) |
| sem mortes novas | mortes P1 − P0 | 0 − 0 | 0 − 0 | passa por construção (o mundo `padrao` não tem morte) |
| **G6** | nenhuma vida do P1 com peso no teto | **20 de 20** com peso no teto | 18 de 20 | **FALHA** |
| G1, G2 | replay bit a bit; fonte desligada = P0 byte a byte | a bancada conferiu o replay de toda vida | idem | passam (`tests/test_n3_consequencia.py`) |

Por semente, o G-P1 vai de −0,013 (9101) a +0,011 (9505).

## 2. O que o P1 faz (sem gate)

| medida | P0 | P1 | P3 (L1) | artefato |
|---|---|---|---|---|
| privação média | 0,105 | 0,105 | 0,125 | `ganho4/resultado.json` |
| privação com o mesmo cuidado (acoplado P1 ← P0) | — | 0,105 (P0 − P1 +0,0007 [−0,0067; +0,0073]) | — | idem |
| privação P0 − P1 por dono | aleatório −0,002 [−0,033; +0,024]; relapso +0,005 [−0,002; +0,009]; atencioso e incoerente 0 (sem privação) | | | idem |
| saúde média | 0,916 | 0,919 (P1 − P0 +0,003 [−0,005; +0,010]) | 0,885 | idem |
| comer na fome moderada | 50% | **94%** | — | idem |
| tempo livre: brincar, explorar, ocioso, chamar | 35%, 29%, 28%, 9% | **11%, 15%, 47%, 27%** | — | idem |
| acerto na tarefa do dono | 0,593 | **0,444** | 0,634 | idem |
| G4 do aprendido (bruto) | — | 0,181 [0,172; 0,189] (0,682) | — | idem |
| deriva final ao prior (JSD) | 0 | 0,036 (razão dia 14 / dia 7 1,78) | 0,019 | idem |

- **O P1 aprende a regra que o sinal ensina**, nas duas rodadas e na mesma proporção: come quase sempre na fome moderada e troca brincar
  e explorar por ficar parado e chamar, porque com a janela imediata comer reduz o déficit e brincar e explorar o aumentam.
- **Isso não vira menos privação.** A privação depende quase toda do dono: o atencioso e o incoerente nunca deixam o pet em privação nos
  dois braços, e o relapso e o aleatório põem o pet em privação de higiene e de fome que o próprio pet não resolve (ele não se limpa, e
  comer sozinho dá +0,05 de fome contra +0,45 da refeição do dono). Na calibração a redução apareceu no aleatório; na validação não.
- **O custo aparece no que o dono ensina:** o acerto na tarefa do dono cai 0,15, porque o dono elogia brincar e explorar quando o pet tem
  energia, e o P1 aprendeu a evitá-los. Com o humor fora do sinal (decisão F6), brincar só tem custo.
- **O teto domina:** o sinal tem sempre o mesmo sentido para cada ação, então os pesos andam até o teto da L1 (1·S) em todas as vidas, em
  qualquer ganho da grade. O freio é o teto, não a dinâmica.

## 3. Leitura

1. **Resultado negativo registrado para o P1 neste mundo:** a consequência imediata da própria ação ensina o pet a comer e a poupar
   energia, mas, no mundo `padrao`, o que tira o pet da privação é o cuidado do dono, e o P1 não reduz a privação em relação ao P0 com
   IC fora de zero. A redução da calibração (+0,005) não se repetiu.
2. É o resultado esperado de um mundo em que a própria ação do pet quase não mexe nos drives que levam à privação; o N4 (frutas) dá ao pet
   uma ação com consequência no mundo. O que fica para a revisão das validações (decisão do Matheus): a janela imediata, o humor fora, o
   teto da L1 aplicado a um sinal de sentido fixo. Nada disso se ajusta neste PR.

## 4. Reprodução

```bash
python experiments/run_v2_n3.py --config experiments/configs/v2_n3/validacao.json   # recusa rodar se a pasta ja existir
```
