# RESULTADO V3 — PLASTICIDADE_EVOLUIDA, C0: a triagem do crítico (2026-11-21)

Worker: Claude Code, Fable 5.2, sessão lateral da Gerência da V3, branch `v3-pe-c0-resultado`. Tarefa:
[TAREFA_V3_PLASTICIDADE_EVOLUIDA.md](TAREFA_V3_PLASTICIDADE_EVOLUIDA.md), o adendo 1 (seção 9.1; PE-8 a PE-11, APROVADAS em 2026-11-21).
**É uma triagem, sem gate: nada confirmatório sai daqui.** O Matheus liberou a run com "libera a triagem C0 quando o código entrar" (recado
da Gerência da V3). Código: a `main` em `e73624eb`, `git_limpo` verdadeiro. O `pre_run` respondeu "pode rodar". A run rodou uma vez, com 4
processos, de 14:42 a 14:47 (319 s):

    python experiments/run_v3_plasticidade_c0.py --config experiments/configs/v3_plasticidade_c0/run.json --processos 4

Os artefatos ficam em `artifacts_v3_plasticidade/c0/`: `meta.json` (os sha256 do código, da tarefa, da config e dos artefatos),
`resultado.json`, `medidas.json` (as medidas por vida), `custos.json` (o relógio) e `vidas.tar.gz` (os 180 logs). **Todo número abaixo sai
do `resultado.json` ou do `meta.json`.** A média é a das 6 células por unidade, e o IC95 é o do t sobre as 10 unidades.

**O desenho:** o pet v38 do Python, três braços nas mesmas sementes (as bases 110001…110010), 6 células (atencioso e relapso ×
`comedouro`, `longe`, `longe_fixo`), 14 dias, 180 vidas.
- **HOJE:** o pet de hoje. Em toda vida, igual ao `pv2.viver("HOJE", ..., v38=True)` (a conferência C-HOJE).
- **CRÍTICO:** o mesmo pet com a `ConfigCritico` ligada (`eta_v` = 64, `gamma` = 960, na escala 1 024; PROPOSTOS, SEM FONTE).
- **CONGELADO:** o mesmo pet com o `p1` e o `p2` desligados.

## 1. A resposta curta

- **A leitura da seção 9.1: "nada muda".** O crítico não aumenta o valor do aprendizado além do ruído entre as unidades.
- **O contraste** (o valor do aprendizado com o crítico menos sem ele): **+0,0034**, IC95 de −0,0108 a +0,0175. O IC contém o 0.
- **O valor do aprendizado fica perto de 0 nos dois casos:** +0,0028 sem o crítico (IC95 de −0,0221 a +0,0278) e +0,0062 com ele (IC95 de
  −0,0122 a +0,0246). Nenhum dos dois IC exclui o 0.
- **O que segue, pela tarefa:** o E0 roda como está, e a leitura "estrutural" ganha força. O E0 pede outro ok do Matheus.
- **O corte da PQ3-9** (o IC95 acima de 0 e a média em 0,032 ou mais) não é atingido. Ele é só informado: o C0 é triagem.

## 2. O "Tempo bem" (dias 1 a 14)

| braço | média | IC95 |
|---|---|---|
| HOJE | 0,7932 | 0,7628 a 0,8236 |
| CRÍTICO | 0,7966 | 0,7724 a 0,8207 |
| CONGELADO | 0,7904 | 0,7673 a 0,8134 |

Os três braços ficam a menos de 0,007 um do outro, com os IC sobrepostos.

## 3. O valor do aprendizado (pareado por unidade)

| medida | média | dp | IC95 |
|---|---|---|---|
| sem o crítico (HOJE − CONGELADO) | +0,0028 | 0,0349 | −0,0221 a +0,0278 |
| com o crítico (CRÍTICO − CONGELADO) | +0,0062 | 0,0257 | −0,0122 a +0,0246 |
| o contraste (com − sem) | +0,0034 | 0,0198 | −0,0108 a +0,0175 |

Com 10 unidades e este desvio-padrão, a meia-largura do IC do contraste é 0,0142: a triagem não enxerga um efeito menor que isso.

## 4. O crítico mexeu no aprendiz

O "nada muda" não vem de um crítico parado:
- **Nenhuma das 60 vidas do CRÍTICO sai igual à do HOJE** na mesma célula e unidade.
- **O `V̂` aprendeu:** a soma dos |v| no fim da vida é 2 522 em média.
- **O crédito:** 79 311 opções receberam o crédito pelo `δ`; nenhuma ficou pendente no fim da vida. Só **6 590 (8,3 %)** moveram o hábito.
  O resto arredonda para 0 com o `eta_h` de hoje.
- **O hábito no fim da vida** (a soma dos |H|): 1 097,3 no HOJE e 1 002,6 no CRÍTICO.

## 5. Ao lado

| medida | HOJE | CRÍTICO | CONGELADO |
|---|---|---|---|
| a fração `aprendido_decidiu` (dias 1 a 14) | 0,1822 | 0,1791 | 0,1502 |
| o crédito do hábito que vai ao dormir, pela soma dos \|ΔH\| | 0,0000 | 0,1131 | sem crédito |
| o crédito do hábito que vai ao dormir, pelo número de créditos | 0,4730 | 0,4735 | sem crédito |
| a saúde, dias 8 a 14 | 0,7599 | 0,7752 | 0,7556 |
| a exaustão, dias 8 a 14 | 0,1170 | 0,1167 | 0,1220 |

- **O crédito ao sono:** quase metade dos créditos é do dormir, nos dois braços. No HOJE nenhum deles move o hábito do dormir (0,0000):
  a recompensa do mesmo tick do dormir é 0, o achado do R1. Com o crítico, 11,3 % do que o hábito anda é na linha do dormir: o `δ` leva
  ao dormir o valor do estado seguinte.
- **A `aprendido_decidiu` no CONGELADO não é 0:** a sonda tira também a memória e a persistência, que o CONGELADO mantém.
- Estas medidas são descritivas, sem IC e sem leitura escrita antes.

## 6. A entropia da decisão (PE-10)

| medida | HOJE | CRÍTICO | CONGELADO |
|---|---|---|---|
| a entropia do sorteio, em bits | 1,8250 | 1,8118 | 1,7984 |
| a fração dos sorteios abaixo de 0,1 bit | 0,00008 | 0,00006 | 0,00012 |

O sorteio fica perto de 1,8 bit nos três braços, e quase nenhum sorteio é concentrado. O crítico não deixa a escolha mais concentrada nem
mais espalhada. A previsão da seção 9.2 fala dos genes do E0 e não se aplica ao C0.

## 7. O custo

- **Parede da run:** 319 s (287 s nas vidas), com 4 processos.
- **Por vida:** 6,25 s de parede e 3,99 s de CPU, com o replay e as conferências.
- A estimativa da tarefa era de cerca de 10 minutos para 360 vidas; a run teve 180 (D-PE-C0-5) e levou 5 min 19 s.

## 8. O que este resultado não diz

- **Nada confirmatório:** é uma triagem com 10 unidades.
- **Nada sobre outros valores do `eta_v` e do `gamma`:** o C0 testou um ponto só. Um crítico com outros números pode se comportar de outro
  jeito.
- **Nada sobre o crítico com um hábito que ande mais:** só 8,3 % dos créditos movem o hábito com o `eta_h` de hoje. O crítico herda esse
  limite, e o C0 não separa "o crítico não ajuda" de "o hábito quase não anda".
- **Nada sobre donos e lugares fora das seis células,** nem por célula: a leitura é da média das seis.
- **Nada sobre o jogo:** a chave fica desligada nele, e o pet é o v38 do Python.

## 9. As conferências

Em toda vida, antes de qualquer medida: o replay pelo log (G1), o T-CENARIO-1, o pet e o braço (`conferir_vida`), a C-HOJE no braço HOJE e
a contabilidade do crédito no CRÍTICO. Todas passaram: a run não parou. Os sha256 dos artefatos estão no `meta.json`
(`resultado.json` `598e6daa…`, `medidas.json` `c356b0d6…`, `vidas.tar.gz` `bd88a13c…`).
