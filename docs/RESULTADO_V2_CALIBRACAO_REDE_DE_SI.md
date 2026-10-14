# Resultado — V2: a calibração da rede de si e o piloto (Digicorpo, etapa 2 do ego)

Data: 2026-10-14. Plano: `docs/PLANO_ANALISE_V2_REDE_DE_SI.md`, seções 5 e 6, e o adendo 1 com os números desta run. Autorizada pelo
Matheus em 2026-10-13.

**Fonte dos números:** `artifacts_v2_rede_de_si/calibracao/`:
- `escolha.json`, `grade/grade.json` e o `meta.json`;
- `piloto/medidas.json`, `medidas.json` e `resultado.json`.

As vidas (`vidas/*.jsonl`) ficam fora do git e saem de novo da config e do código.
- **O comando:** `python experiments/run_v2_calibracao_rede_de_si.py --config experiments/configs/v2_rede_de_si/calibracao.json --processos 8`.
- **A run:** commit `8294d74`, árvore limpa, Python 3.13.0, Windows. Levou 7,6 min (a grade em 100 s, o piloto em 357 s).
- **As sementes:** as bases 43101…43505 (K_u = 4, prefixo `rede_de_si`, 20 unidades). A validação (44101…44505) não rodou.
- **O replay:** toda vida foi gravada e rejogada do disco bit a bit, com o G1-REDE.
  - Na grade, as três vidas de cada unidade (uma por `passo`) saíram iguais byte a byte (G-OBS).
  - No P1-c-lenta, a troca da digestão foi conferida no tick e na taxa pedidos.

## Resumo

- **O `passo` = S/16 (64), fechou.**
- **A taxa lenta = C // 8, "não fechou":** nenhuma taxa da grade muda o receptor da fome por mais de S/16.
- **A margem é negativa:** o oráculo prevê pior que a persistência em todas as 20 unidades. **Pela seção 6, a validação não roda, e o plano
  volta ao Matheus.** O N não foi calculado.
- A causa é o oráculo, não o teto da persistência (seção 3).

## 1. A grade do `passo` (só o P1-c, na `bola`)

| `passo` | MAE_rede(1), dias 1 a 7 | vidas com peso no teto |
|---|---|---|
| S/64 (16) | 18,17 | 0 de 20 |
| **S/16 (64)** | **10,42** | 0 de 20 |
| S/4 (256) | 13,89 | 6 de 20 |

A regra pega o menor erro entre os pontos que não prendem pesos no teto em mais da metade das vidas: o 64.

## 2. A taxa lenta da digestão (o P1-c-lenta, na `bola`)

| taxa (a partir do fim do dia 7) | receptor da fome, média dos dias 8 a 10 | diferença do P1-c (738,1) |
|---|---|---|
| C // 2 | 738,1 | 0,0 |
| C // 4 | 731,8 | 6,3 |
| C // 8 | 727,9 | 10,2 |

- Nenhuma passa S/16 (64). Fica a menor taxa, pela reserva.
- Com o dono atencioso, a digestão lenta quase não muda a fome que o pet sente. C // 2 não muda nada, porque ainda cobre o que o pet come
  num tick.
- O G-ADAPTA, com essa troca, mede pouca mudança do corpo.

## 3. O piloto e a margem

**O MAE a 4 decisões nos dias 8 a 14** (média das 20 unidades; o piloto não é evidência, seção 6):

| braço | persistência | rede | média histórica | oráculo | D_SI (IC95) |
|---|---|---|---|---|---|
| P1-c | 47,4 | 54,4 | 81,4 | 71,9 | −6,97 [−7,97; −6,14] |
| P0-c | 44,8 | 50,8 | 60,0 | 66,6 | −6,02 [−6,40; −5,62] |
| P1-c-lenta | 47,2 | 54,0 | 80,4 | 71,1 | −6,78 [−7,49; −6,14] |
| P1-c-tapa | 53,2 | 62,4 | 90,5 | 82,1 | −9,21 [−9,97; −8,46] |
| P1+ped-c | 45,7 | 52,3 | 78,7 | 68,0 | −6,62 [−7,42; −5,79] |

- **A margem:** a distância persistência − oráculo no P1-c é −24,5 (negativa em 20 de 20 unidades), e `Δ_SI` = −12,3. No G-ADAPTA, a
  distância congelada − oráculo na fome é −18,5. **A regra da seção 6 (distância ≤ S/128) para a validação.**
- **O texto automático da run** ("a persistência já é quase o teto") é o da seção 6, mas não é o que aconteceu.
  - O oráculo recebe os 14 químicos a mais com o mesmo `passo` da rede. Mais entradas dão um passo efetivo maior, e o oráculo fica pior
    que a rede e que a persistência.
  - É o mesmo achado da fumaça, registrado antes da run (`docs/TAREFA_V2_REDE_DE_SI.md`, seção 9): nas sementes dos testes, com o `passo`
    16 (S/64) o oráculo ficava perto da rede, e com o 64 (S/16), pior que a persistência.
- **Descritivo:** a rede no `passo` 64 também prevê pior que a persistência a 4 decisões em todos os braços (D_SI negativo). Ela bate a
  média histórica (D_MEDIA de +9 a +28).
- **A autoria** (descritivo):
  - o `BSS_NASC` médio fica entre −0,24 e −0,49 nos cinco braços;
  - o `BSS_PED` no P1+ped-c é −0,36, com 16 unidades com valor e 4 fora por menos de 20 decisões.
  - Os dois são piores que a frequência na mesma vida.

## 4. O custo

- A grade custa 5,1 s de CPU por vida.
- O piloto custa por vida, com o replay e a medição: P0-c 18,2 s, P1-c 19,7 s, P1-c-lenta 20,4 s, P1-c-tapa 21,3 s e P1+ped-c 33,4 s.

## 5. O que fica para o Matheus

- **O plano volta pela seção 6:** a margem saiu negativa.
- **Opções** (para decisão, não aplicadas):
  - **dar ao oráculo o próprio `passo`:** o menor MAE numa grade dele, que é o teto que o PRS-4 supõe. A margem e o N sairiam de novo no
    piloto, nas mesmas sementes, com um adendo antes;
  - **trocar o horizonte primário para n = 1:** a rede bate a persistência a 1 decisão (o erro que a regra minimizou). O PRS-1 já pesou
    esse custo: o teste fica fraco;
  - **aceitar o resultado como negativo:** com o `passo` escolhido, a rede não bate a persistência a 4 decisões, e o oráculo do plano não dá
    margem.
- **A taxa lenta não fechou:** para o G-ADAPTA medir alguma coisa, a mudança do corpo precisaria ser maior que a da grade.
- **Nada foi recalibrado olhando o piloto.**
