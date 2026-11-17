# PLANO DE ANÁLISE V3 — SONDA_EMPOWERMENT, F5: o E(P) varia entre lugares? (2026-11-17, sessão da F5, Claude Code, Opus 5.5)

**Status: APROVADO pelo Matheus (2026-11-17).** À pergunta "Aprova o plano de análise e a D-F5-9 como recomendada?", ele respondeu
"Aprovo o plano". A D-F5-9 fica aceita como recomendada (sim). Este cabeçalho foi commitado antes do primeiro artefato (D-F5-8).

**O papel:** uma medida descritiva, sem gate e sem teste de hipótese. Ela decide uma coisa só: se a H-EMP-1 do levantamento vale um
plano depois da F3. A F5 não é frente (D-F5-1, "Pesquisa, com sonda").

**De onde vem:**
- a espec, `docs/ESPEC_V3_SONDA_EMPOWERMENT.md`, APROVADA em 2026-11-17 ("Aprovo as recomendações"), com as correções do SE1 aceitas
  ("Aceito as correções");
- a tarefa, `docs/TAREFA_V3_SONDA_EMPOWERMENT.md`, etapa SE2;
- o código, `experiments/sonda_empowerment_f5.py`, com os testes em `tests/test_sonda_empowerment_f5.py` (SE1, commit `3f882ffa`).

## 1. As vidas (D-F5-2, a opção (a))

FATO VERIFICADO: as dez vidas da AN0 da PET_VIVO (`auditoria_pet_vivo.vidas_an0`), refeitas no código de hoje. São 2 lugares
(`longe_fixo`, `comedouro`) × 2 donos (`atencioso`, `relapso`) × 2 sementes (101, 202), 4 dias cada, mais as 2 vidas dos fins sem
ajuste. Os gabaritos, conferidos com o `sha256sum` em 2026-11-17:

| arquivo (`web/app/test/gabaritos/`) | sha256 |
|---|---|
| `digibrain_modular_comedouro.json.gz` | `2034aa7e075809c028234262d6486c83d2f89967490158ec788a7841d63668a5` |
| `digibrain_modular_longe_fixo.json.gz` | `5b37fcb0314efff5b74b02116d81a7dcba725b00d89f77439bbb3c93412b109d` |
| `digibrain_modular_fins.json.gz` | `129177bf123bd65a4e2f5c453f07814075424fd1c4c3cb3a08c79c77d5836314` |

São sementes dos testes, não vidas de pesquisa; nenhuma faixa é reservada. A unidade de análise é a decisão, e cada vida também é
relatada à parte.

**Limite conhecido antes da medida** (visto ao depurar o coletor, sobre as entradas, não sobre o `E`): nessas vidas o pet só come ração
e brinca com a bola, e numa delas ele não come nenhuma vez. Com no máximo duas classes ao alcance, o `E` fica entre 1 e 5. Isso pode dar
"plano" por construção (seção 4).

## 2. As medidas (espec, seção 5)

Todas em inteiros ou em frações `num/den`.

- **M-S1, a variação:**
  - o `E` do lugar do pet por decisão, com o mínimo, os quartis e o máximo;
  - a fração das decisões com `E > 1`;
  - a amplitude `max_P E − min_P E` entre os lugares de cada decisão, com os quartis e a fração das decisões com amplitude ≥ 2.
- **M-S2, a separação do `CONT`:** sobre os pares de lugares de cada decisão, somados em todas, os pares concordantes, os discordantes,
  os empates só no `E`, os empates só no `CONT` e os empates nos dois. A fração lida é discordantes ÷ todos os pares.
- **M-S3, exploratória:** nas decisões de `explorar/ponto` com dois ou mais alvos candidatos, os acertos (o alvo escolhido tem o maior
  `E` entre os candidatos) contra o acaso com os empates (a soma, por decisão, de quantos candidatos têm o maior `E` ÷ os candidatos).
  Só descreve, e não entra na leitura.

## 3. As conferências que falham alto (espec, seção 6)

- **G-S0:** cada vida sai igual ao gabarito, com o mesmo sha256 do log, o mesmo do estado e os mesmos motivos. Se uma falhar, a medida
  para sem artefato.
- **G-S1:** o estado das rngs (a de política, a `random` global e as dos módulos) é o mesmo antes e depois de cada leitura.
- **Uma leitura por decisão:** o número de leituras é igual ao de decisões em cada vida.
- **Os processos:** no máximo 4 (V3-D8). O tempo já medido no SE1 dá 0,43 s por vida.

## 4. A leitura (registrada antes; espec 5.4; D-F5-7, os limiares PROPOSTOS, SEM FONTE)

Sobre todas as decisões juntas:
- **"plano"**: as decisões com amplitude ≥ 2 são menos de 1/10;
- **"igual ao CONT"**: os pares discordantes são menos de 1/20 de todos os pares;
- **se der "plano" ou "igual ao CONT", a F5 acaba ali, sem plano.** Uma exceção: se der "plano" e a M-S1 mostrar o `CONT` do lugar do
  pet ≤ 1 em mais da metade das decisões, a leitura é "plano pelas entradas". Aí a F5 não acaba. O relato pede ao Matheus a decisão
  sobre a opção (b) da D-F5-2 (uma run feita, depois de conferir o replay);
- se não der nenhum dos dois, a H-EMP-1 vira um plano de análise **depois da F3**, com as decisões dele.

A leitura por vida é só descritiva: ela não muda a leitura geral.

## 5. Os artefatos e o relato

- `artifacts_v3_f5_sonda/sonda.json`: as fontes (os sha256 dos gabaritos e deste plano), as medidas por vida e no total, e a leitura;
- `artifacts_v3_f5_sonda/sonda_decisoes.json.gz`: o registro por decisão (o lugar do pet, cada `[P, E, CONT]`, os candidatos, a
  escolha e o alvo);
- `docs/RESULTADO_V3_SONDA_EMPOWERMENT.md`: os números, a linha da leitura e as limitações (seção 6).

A medida roda **uma vez** (o script recusa se o `sonda.json` já existe).

## 6. Limitações registradas antes

- O `E` é medido sobre o modelo do pet, que só prevê o consumo (o `d̂` do M-PLAST). Ele não diz nada sobre outras ações.
- Dez vidas curtas, de sementes dos testes e de dois lugares: o resultado não generaliza para o pet do jogo.
- O `E` é uma medida tirada do registro. Ela não diz que o pet faz essa conta.
- Nenhuma alegação de novidade: a conta é a forma determinística do empowerment (Salge, Glackin e Polani 2014).

## 7. A decisão do Matheus

| id | pergunta | recomendação | custo de errar |
|---|---|---|---|
| **D-F5-9** | a exceção "plano pelas entradas" (seção 4): se a falta de classes explica o plano, a F5 espera a opção (b) em vez de acabar? | sim | sem ela, as entradas estreitas podem encerrar a F5 sem que o `E` tenha tido como variar |

Decisão: aceita como recomendada, em 2026-11-17 ("Aprovo o plano").
