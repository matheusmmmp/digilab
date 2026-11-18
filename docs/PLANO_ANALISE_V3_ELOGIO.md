# PLANO DE ANÁLISE V3 — ELOGIO: o carinho logo depois de comer X acelera o aprendizado do modular

**Status: PROPOSTO** (2026-11-17), parado no **CHECKPOINT EL-3** antes das medidas no `digilab/metrics.py`, da faixa no `faixas.py` e de
qualquer vida da faixa. As D-EL-18 a D-EL-24 (seção 8) esperam o Matheus.

Escrito em 2026-11-17 (Claude Code, Opus 5.5, branch `v3-elogio-plano`), na etapa 3 da [TAREFA_V3_ELOGIO.md](TAREFA_V3_ELOGIO.md)
("Comece a etapa 3 do elogio", Matheus, 2026-11-17). O código da etapa 2 está na `main` (#968, 1f77a5b8).

## 1. De onde vem

A tarefa (seção 4) esboçou os braços, as medidas M1 a M4, o contraste principal E-imed − E-sorteado em M2 e as premissas P0 e P1. A etapa 2
trocou o mundo do paladar pelo `casado` com as árvores (D-EL-9, vidas de 12 dias) e montou os donos (`experiments/elogio.py`). Este plano
fecha os números, a faixa e a regra de leitura, escritos antes da primeira vida da faixa.

## 2. A sonda (sementes dos testes; nada daqui é resultado)

`python experiments/sonda_elogio_plano.py --dias D` roda, nas sementes 101 a 160, o E0, o E-imed e o E-sorteado (o par) com a chave
ligada nos valores padrão (g = S, W = 1). Ela existe para escolher a duração e a medida, não para estimar o efeito.

| | 12 dias | 36 dias |
|---|---|---|
| frutas comidas por vida (mediana, E0) | 19 | 159,5 |
| X comida na 1ª metade (mediana, E-imed) | 3 | 17 |
| vidas do E-imed com menos de 5 X na 1ª metade | 38 de 60 | 4 de 60 |
| carinhos por vida (mediana, E-imed) | 3 | 17 |
| E-imed − E-sorteado, fração de X na 1ª metade | +0,101 (ep 0,028, n 55) | +0,020 (ep 0,018, n 60) |
| E-imed − E-sorteado, fração de X na 2ª metade | +0,047 (ep 0,030, n 59) | −0,016 (ep 0,010, n 60) |
| P1 no E0: fração da preferida, 2ª − 1ª metade | +0,006 (ep 0,037, n 55) | −0,017 (ep 0,021, n 60) |

Três leituras, todas para decidir o desenho:
1. **Os 12 dias bastam para a M2.** A fração de X sai em 55 das 60 vidas, e a diferença do par aparece. Em 36 dias o pet passa a comer
   muitas frutas na segunda parte da primeira metade, e o efeito se dilui. O M1 (8 de X nas últimas 10 frutas) quase nunca fecha em 12 dias.
2. **A P1 (a natural) não aparece na escolha.** O modular aprende o desfecho: numa vida de teste (101, 12 dias), a classe preferida tem
   humor +90 no desfecho e outra tem −41. Mas a fração escolhida da preferida não sobe entre as metades. A escolha do alvo pesa o incentivo
   pela proximidade (`impulso.py`), e o humor pesa pouco quando o drive do humor está baixo. Isto é uma hipótese da leitura do código, não uma medida.
3. **As três frutas estão quase sempre à vista.** Em três vidas de 36 dias, os passos do dono com as três frutas no mapa ficam entre 74 e
   87 %, e os com duas, entre 13 e 22 %.

## 3. As vidas

- **O mundo, o corpo e o cérebro:** os da etapa 2 (`experiments/elogio.py`): `CONFIG_MUNDO_LIGADA` com a condição `casado`, o
  `CONFIG_CORPO_DRIVES`, o modular do braço REL, o dono atencioso com o lugar `comedouro`. **12 dias** (D-EL-18). O contingente só na
  primeira metade (D-EL-7).
- **A unidade:** a semente; o genoma das frutas e a fruta X saem dela. Os braços da mesma unidade comparam pareados.
- **Os braços:** E0 (a chave ligada, sem carinho), E0-off (a chave desligada), E-imed, E-sorteado (o par do E-imed), E-atraso, E-incons.

## 4. As medidas (escritas antes; no `digilab/metrics.py` depois do checkpoint)

A **fração de X** de uma janela é a `metrics.fracao_da_fruta` (já existe), com os consumos (tick, fruta, frutas presentes). As presentes
de um consumo são os tipos de fruta no mapa no último passo do dono antes dele, mais a fruta comida (D-EL-19). Uma unidade sem consumo
elegível na janela fica fora do contraste, com o número reportado.

- **M2, a principal:** a fração de X na primeira metade da vida (a do elogio).
- **M3, a retenção:** a fração de X na segunda metade.
- **M1, descritiva:** a decisão (tick // 15) do primeiro consumo em que 8 das últimas 10 frutas são X (D-EL-4), censurada no fim da vida.
  Sai a fração de vidas que fecham e, entre elas, a mediana.
- **M4, a guarda:** a privação (`privacao_nas_decisoes`, limiar 0,15) e a exaustão (`exaustao_nas_decisoes`, energia < 0,25), as duas
  sobre todas as decisões da vida. A margem é 0,032, a mesma da VALUATION.
- **Descritivos:** as frutas e as rações comidas por dia, os carinhos por vida, o desfecho P1 da classe X no fim (humor e solidão).

## 5. A calibração (etapa 4; sementes 25101 a 25200, 100 unidades)

A grade da D-EL-8: g em {S/4, S/2, S, 2S} × W em {1, 2, 4}. Cada célula roda o par E-imed × E-sorteado. O E0 roda uma vez por unidade.
Isso dá 12 × 2 × 100 + 100 = 2 500 vidas, cerca de 1,1 s cada na sonda, perto de 12 min com 4 processos.

**A escolha (D-EL-21):** o menor g, e nele o menor W, com:
- E-imed − E-sorteado em M2 com o limite inferior do IC95 > 0 (`bootstrap_ic` sobre as diferenças por unidade, 2 000 reamostragens,
  semente `derivar_semente("elogio-bootstrap", célula)`);
- sem piora da M4: o limite superior do IC95 de E-imed − E-sorteado abaixo de +0,032, na privação e na exaustão.

Se nenhuma célula passar, a calibração para, e o resultado vai ao Matheus sem validação.

## 6. A validação (etapa 5; sementes 25301 a 25500, 200 unidades, uma vez)

No g e no W escolhidos, os seis braços: 1 200 vidas, perto de 6 min com 4 processos.

**As premissas, antes do contraste:**
- **P0, técnica:** o E0-off e o E0 dão o mesmo log, byte a byte, em toda unidade (com a chave ligada e sem carinho, nada muda). O sinal de
  todo carinho é diferente de 0.
- **P1, a natural:** no E0, a fração da preferida do genoma na 2ª metade menos a da 1ª, com o IC95 pelo t. A sonda sugere que ela falha.
  Pela regra do projeto, a falha é registrada como está e não para o contraste (D-EL-20): sem ela, a leitura "o elogio acelera a natural"
  cai, e fica "o elogio ensina X".
- **P1b, descritiva:** no fim da vida do E0, o humor do desfecho da classe preferida menos o da rejeitada.

**O gate G-EL1:** E-imed − E-sorteado em M2, o limite inferior do IC95 (o bootstrap da seção 5, semente `"elogio-validacao"`) > 0, e a M4
sem piora, com a mesma regra. A classe: "confirma" com os dois; "não confirma" sem o primeiro; "confirma com custo" se só a M4 falhar.

**Os secundários, descritivos com o IC95:**
- E-imed − E0 em M2;
- E-atraso − E-imed em M2, por atraso sorteado;
- E-incons − E-imed em M2;
- E-imed − E-sorteado em M3 (a retenção);
- a separação X = preferida × X ≠ preferida, em M2.

## 7. Os artefatos

`experiments/run_v3_elogio.py` (a escrever na etapa 4) grava em `resultados/v3_elogio/<fase>/`:
- `vidas.jsonl`: uma linha por vida, com as medidas da seção 4;
- `meta.json`: o sha256 deste plano, do orquestrador, do `elogio.py`, do `config.py`, do `metrics.py` e do `engine.py`, as sementes,
  a grade e o commit.

O pre-run do projeto confere a faixa e se há outra run.

## 8. As decisões para o CHECKPOINT EL-3

| id | decisão | recomendação | custo de errar |
|---|---|---|---|
| D-EL-18 | a duração | ficam os 12 dias da D-EL-9: a M2 sai em 55 de 60 vidas da sonda, e 36 dias diluem a primeira metade | médio: com poucas X por vida a M2 é ruidosa; os 200 da validação compensam |
| D-EL-19 | as frutas presentes de um consumo | os tipos no mapa no passo do dono antes dele, mais a comida | baixo: as três estão à vista em 74 a 87 % dos passos |
| D-EL-20 | a P1 que deve falhar | manter como premissa escrita e registrar a falha; a leitura passa a "o elogio ensina X" | médio: sem a natural, o "acelera" do pedido não é testado |
| D-EL-21 | a regra da calibração | o menor g e o menor W com o IC95 inferior > 0 em M2 e sem piora da M4; nenhum → para e volta | baixo: a regra é a do esboço da seção 4 da tarefa com os números |
| D-EL-22 | a faixa | 25101 a 25505: calibração 25101–25200, validação 25301–25500; conferida livre na `origin/main` e nos branches remotos em 2026-11-17 | baixo |
| D-EL-23 | o gate | G-EL1 da seção 6, com as três classes | médio: o gate está em M2; a M3 fica descritiva |
| D-EL-24 | o M1 | descritivo, com a censura no fim da vida | baixo: a M2 é a principal |
