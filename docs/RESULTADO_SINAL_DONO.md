# Resultado — Etapa A: o sinal do dono chega ao que o pet aprende?

Status: **EXECUTADO** (2026-09-30), pelo plano registrado antes (`docs/PLANO_ANALISE_CANAL_DONO.md`, commits `d1e0cd9`
e `369a94b`). Todo número abaixo vem de `artifacts_linhagem/sinal_dono/resultado.json` (`experiments/sinal_dono.py`);
os valores por pet estão em `portadores_por_pet.json`.

**Duas execuções.** A primeira não calculava o contraste atencioso − aleatório, que a seção 3 do plano pede. O script
foi completado (commit `1b74f6b`) e rodado de novo. A segunda execução deu o mesmo gate e os mesmos componentes,
frações e médias, conferidos campo a campo contra a primeira: mesmas vidas, mesma semente, mesmas reamostras. Não
mudou nenhum número nem critério. Não é desvio: o contraste já estava no plano.

## Resultado em três frases

1. **Gate A: SINAL PRESENTE**, por um eixo só, o **resistente**: σ²_D +0,0034, IC 98,75% [+0,0009; +0,0121]. O dono
   explica 20,8% da variância desse eixo em `T_ADOL`. Os outros três eixos não passam.
2. **O sinal que passou não é o da coerência.** No eixo resistente, atencioso − aleatório é +0,012, IC95
   [−0,091; +0,115]. A separação é outra: o permissivo fica em −0,220 e o relapso em −0,058. O contraste
   atencioso − aleatório só aparece no eixo **paciente** (+0,212, IC95 [+0,001; +0,461]), que não passa no gate com
   Bonferroni.
3. **O ambiente pesa tanto quanto o dono ou mais.** A interação dono × ambiente leva de 24% a 48% da variância de
   cada eixo, e o ambiente sozinho leva 19% a 28% em dois deles. O que o pet aprende já depende de onde ele vive,
   antes de a forma existir.

## Conferências: todas passaram

| conferência | resultado |
|---|---|
| os 640 replays iguais ao `pets.json` do E1 (morte, sparring, disciplina, saúde, vínculo, treino, forma) | 640 de 640 |
| mortes antes de `T_ADOL` (900) | 0 (a primeira morte do E1 é no tick 1320) |
| `hash_parametros_educacao` igual ao do E1 | igual |
| a linha segue o caráter em `T_ADOL` | 1,0 |
| teste: o caráter em `T_ADOL` pelo replay é igual ao da simulação | `tests/test_sinal_dono.py` passa |

Replay: 1286 s na segunda execução (1095 s na primeira). Bootstrap: 77 s.

## Gate A: os 4 eixos do caráter em `T_ADOL`

Os 4 donos, 640 pets. IC do gate: pigeonhole de 98,75% (Bonferroni pelos 4 eixos), 10 000 reamostras, semente
20260930. As frações truncam cada componente em 0; o σ²_D é sem truncar.

| eixo | σ²_D [IC 98,75%] | frac D | frac G | frac R | frac DR | frac e | passa |
|---|---|---|---|---|---|---|---|
| atento | −0,0049 [−0,0086; +0,0311] | 0,000 | 0,010 | 0,194 | 0,476 | 0,244 | não |
| impetuoso | +0,0005 [−0,0033; +0,0160] | 0,021 | 0,000 | 0,277 | 0,406 | 0,261 | não |
| paciente | +0,0047 [−0,0014; +0,0456] | 0,093 | 0,000 | 0,000 | 0,309 | 0,341 | não |
| **resistente** | **+0,0034 [+0,0009; +0,0121]** | **0,208** | 0,060 | 0,030 | 0,242 | 0,340 | **sim** |

Médias por dono e contraste (IC95):

| eixo | aleatório | atencioso | permissivo | relapso | atencioso − aleatório |
|---|---|---|---|---|---|
| atento | −0,066 | −0,026 | +0,035 | −0,031 | +0,040 [−0,269; +0,348] |
| impetuoso | +0,087 | −0,044 | −0,002 | −0,003 | −0,132 [−0,287; +0,073] |
| paciente | +0,028 | +0,239 | +0,190 | +0,095 | **+0,212 [+0,001; +0,461]** |
| resistente | −0,136 | −0,125 | −0,220 | −0,058 | +0,012 [−0,091; +0,115] |

O desvio bruto, antes do corte em [−1, 1], dá as mesmas frações que o caráter: o corte não pesou.

## Portadores impostos (descritivo; fora do gate e da Etapa B, pelo plano)

| portador | frac D [IC95] | atencioso − aleatório [IC95] |
|---|---|---|
| disciplina final | 0,988 [0,982; 0,996] | +95,0 [+88,2; +99,3] |
| saúde final | 0,630 [0,499; 0,748] | +0,707 [+0,577; +0,810] |
| vínculo final | 0,393 [0,195; 0,628] | **−0,176** [−0,291; −0,061] |
| fração do treino em cada stat | 0,000 a 0,121 | de −0,032 (fôlego) a +0,032 (guarda) |

- Os portadores impostos carregam o dono quase por construção: a disciplina é 99% dono.
- O vínculo repete o defeito conhecido: o aleatório termina com vínculo maior que o atencioso.

## A linha: onde o ambiente entra

| dono | brigão | caçador | colosso | guardião | κ de Fleiss da linha entre ambientes |
|---|---|---|---|---|---|
| aleatório | 85 | 11 | 4 | 60 | 0,038 |
| atencioso | 37 | 33 | 1 | 89 | −0,100 |
| permissivo | 19 | 42 | 0 | 99 | 0,407 |
| relapso | 45 | 15 | 20 | 80 | −0,025 |

A linha é decidida pelo caráter em `T_ADOL` (conferido: 1,0). Mesmo assim, o mesmo genoma com o mesmo dono cai em
linhas diferentes conforme o ambiente (κ perto de 0), salvo no permissivo. É o mesmo padrão da forma adulta
(`docs/RESULTADO_V21D_PAINEL.md`), e ele já existe no primeiro gargalo.

O caráter em `T_ADUL` (só os vivos) está no artefato, como descritivo.

## Leitura

- **Pelo plano, a Etapa B pode rodar:** existe sinal do dono no que o pet aprende, e ele não passa pela forma.
- **Ressalva para ler a Etapa B:**
  - o eixo que passou (resistente) separa permissivo × relapso, **não** coerente × aleatório;
  - a pergunta original do projeto (coerência do feedback) aparece só no eixo paciente, sem passar no gate;
  - um canal pelo caráter pode dar peso ao dono sem dar peso à coerência do dono.
- **O ambiente move o que o pet aprende** (DR e R altos). Parte do "efeito do ambiente" na forma nasce aqui, no
  aprendizado, antes de qualquer luta.
- **Limites:**
  - 4 ambientes;
  - espécie fixa;
  - os donos sintéticos são quatro regras escritas por nós;
  - a primeira execução sem o contraste (relatado acima).

## Próximo passo (decisão do Matheus)

O plano manda registrar um adendo **antes** da Etapa B, dizendo:
- qual eixo passou (resistente);
- se k = 3 e 9 continuam.

**Recomendação:**
- manter o canal como está escrito: k multiplica o termo do caráter inteiro nos stats, com os 4 eixos, e não só o
  resistente;
- usar o resistente só na medida de transmissão.

Isso evita escolher o eixo pelo resultado.
