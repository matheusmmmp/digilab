# RESULTADO V3 — PET_VIVO, o teste de recompensa: o carinho depois do comer e do brincar deixa o pet mais acordado? (2026-11-20)

Worker: Claude Code, Fable 5.2, worktree `v3-integracao-r1-plano`. Plano: [PLANO_ANALISE_V3_PET_VIVO_RECOMPENSA.md](PLANO_ANALISE_V3_PET_VIVO_RECOMPENSA.md)
(APROVADO em 2026-11-20, RC-1 a RC-7 decididas). Pré-registro: `docs/PREREGISTRO.md`, seção `PR-PET-VIVO-RECOMPENSA`, escrita antes da
run. Código das vidas: `82551431`, a `main` com o #1048 (o plano) e o #1050 (o código), `git_limpo` verdadeiro. O pedido do
Matheus (2026-11-20): "Sim, merge e roda". O `pre_run` respondeu "pode rodar" depois de o replay da fome da CORPO terminar. A run
rodou uma vez: `python experiments/run_v3_pet_vivo_recompensa.py --config experiments/configs/v3_pet_vivo/recompensa.json --processos 4`,
de 15:51 a 18:36.

**A análise parou num erro do código e foi refeita sem reviver nenhuma vida (D-RC-15, a seção 2).** As 9600 vidas e as
medidas delas são as da run. Uma guarda do plano, a saúde dos dias 8 a 14, **não foi medida**.

Os artefatos ficam em `artifacts_v3_pet_vivo/recompensa/run/`: `meta.json`, `resultado.json` e `medidas.json.gz`. O `medidas.json`
cru (84 MB) e o `vidas.tar.gz` (49 MB, os logs das 9600 vidas) ficam fora do repositório, com o sha256 no `meta.json`. Todo
número abaixo sai do `resultado.json`.

## 1. A resposta curta

- **L-ACORDADO: "nao: com a recompensa o pet dorme mais".** O pet com a recompensa fica acordado em 0,519 das
  decisões, contra 0,530 do pet de hoje. O D1 é **−0,0109 [−0,0113; −0,0105]** (n 200): cerca de
  16 minutos a menos por dia. É o desfecho esperado, escrito antes ("não: dorme mais ou fica igual").
- **O efeito é pequeno.** O IC inteiro também cabe em ±0,02 (o δ_A). A regra lê em ordem, e a primeira linha é a do "dorme mais".
- **L-BEM: "o pet fica melhor".** O "Tempo bem" sobe +0,0183 [+0,0152; +0,0215]. O ganho está todo no lugar `longe`; nos outros dois ele
  cai um pouco (a seção 5).
- **L-PORQUÊ: "pela recompensa na hora, e pelo que o pet aprende".** A frase da regra não descreve bem o que saiu (a seção 4): o crédito e a hora certa
  puxam para **mais** tempo acordado (D3 +0,0070, D2 +0,0096), e o que faz o pet dormir mais é o
  carinho no corpo.

## 2. As vidas, as conferências e a análise refeita

- **9600 vidas:** 4 braços × 12 células × 200 unidades (as bases 108001…108200), 14 dias, o pet do v38.
- **As conferências que falham alto passaram em todas:** a C-G1, a C-HOJE, a C-CORPO, a C-HORA e a C-MESMO-N. Uma falha levantaria
  erro antes de o `medidas.json` ser gravado.
- **O custo:** 2 h 45 min de parede com 4 processos, contra a projeção de 2,4 h da fumaça e o corte de 4 h.
- **O erro (D-RC-15):** depois de gravar o `medidas.json`, a análise parou num `KeyError: 'saude_media'`. O `medir` nunca gravou a
  saúde por vida, e a fumaça não exercitava a análise. O erro é do código do #1050.
- **O conserto:** a guarda saiu da lista de medidas, e o orquestrador ganhou o `--reanalisar`, que lê o `medidas.json` gravado e
  recusa-se a rodar se o número de vidas ou de logs não for o do plano. O commit do conserto (`56921401`)
  veio antes de qualquer número ser lido. **Nenhuma vida foi revivida, e nenhuma regra de leitura mudou.**
- **O que ficou sem medir:** a saúde dos dias 8 a 14. Só o replay dos 9600 logs a daria (perto de 1 h de máquina, estimado,
  não medido).

## 3. As premissas (registradas, não param)

- **P-EVENTO: cumpre nas 12 células.** Nenhuma célula saiu da leitura.
- **P-DOSE: cumpre.** 0,570 dos 451914 créditos mudam a linha do hábito (o piso é
  0,30).
- **P-SINAL: cumpre.** Nenhum carinho com sinal negativo; 5733 de 451914 com sinal 0.

| célula (dono / lugar) | carinhos a mais por vida (média) | mínimo | fração das vidas com 50 ou mais |
|---|---|---|---|
| aleatorio / comedouro | 127,1 | 65 | 1,00 |
| aleatorio / longe | 147,0 | 82 | 1,00 |
| aleatorio / perto | 133,4 | 64 | 1,00 |
| atencioso / comedouro | 194,1 | 164 | 1,00 |
| atencioso / longe | 154,8 | 74 | 1,00 |
| atencioso / perto | 202,2 | 176 | 1,00 |
| incoerente / comedouro | 194,1 | 164 | 1,00 |
| incoerente / longe | 155,2 | 100 | 1,00 |
| incoerente / perto | 202,2 | 181 | 1,00 |
| relapso / comedouro | 142,0 | 101 | 1,00 |
| relapso / longe | 169,1 | 125 | 1,00 |
| relapso / perto | 155,3 | 126 | 1,00 |

## 4. Os contrastes (por unidade, a média das 12 células, IC95, n 200)

D1 = R-CB − R0 (o efeito inteiro). D2 = R-CB − R-SORT (a hora do carinho). D3 = R-CB − R-CORPO (o crédito).

| medida | D1 | D2 | D3 |
|---|---|---|---|
| T_ACORDADO (dias 1 a 14) | −0,0109 [−0,0113; −0,0105] | +0,0096 [+0,0093; +0,0100] | +0,0070 [+0,0067; +0,0073] |
| T_ACORDADO (dias 8 a 14) | −0,0062 [−0,0069; −0,0056] | +0,0124 [+0,0118; +0,0130] | +0,0091 [+0,0086; +0,0096] |
| "Tempo bem" | +0,0183 [+0,0152; +0,0215] | +0,0025 [−0,0007; +0,0056] | +0,0012 [−0,0015; +0,0038] |
| taxa por episódio | +0,0209 [+0,0147; +0,0270] | +0,0069 [+0,0009; +0,0129] | +0,0065 [+0,0006; +0,0125] |
| decisões de comer | +14,1 [+13,6; +14,6] | +15,4 [+14,8; +15,9] | +16,1 [+15,7; +16,6] |
| decisões de brincar | +11,5 [+10,9; +12,1] | +22,1 [+21,5; +22,7] | +17,7 [+17,2; +18,2] |
| F_PESOS-DEC (o dormir pelo sorteio) | +0,0162 [+0,0155; +0,0170] | −0,0307 [−0,0318; −0,0297] | +0,0097 [+0,0090; +0,0104] |
| linha do hábito do comer | +897 [+883; +910] | +887 [+874; +901] | +991 [+978; +1005] |
| linha do hábito do brincar | +393 [+385; +400] | +425 [+417; +432] | +476 [+469; +483] |

As médias por braço:

| medida | R0 | R-CORPO | R-CB | R-SORT |
|---|---|---|---|---|
| T_ACORDADO (dias 1 a 14) | 0,5300 | 0,5121 | 0,5191 | 0,5095 |
| T_ACORDADO (dias 8 a 14) | 0,5193 | 0,5039 | 0,5131 | 0,5007 |
| "Tempo bem" | 0,7767 | 0,7939 | 0,7951 | 0,7926 |
| taxa por episódio | 0,6609 | 0,6752 | 0,6817 | 0,6749 |
| decisões de comer | 67,2 | 65,2 | 81,3 | 65,9 |
| decisões de brincar | 71,8 | 65,7 | 83,4 | 61,3 |
| F_PESOS-DEC (o dormir pelo sorteio) | 0,1145 | 0,1210 | 0,1307 | 0,1614 |
| linha do hábito do comer | 588 | 493 | 1485 | 597 |
| linha do hábito do brincar | 269 | 186 | 662 | 237 |

- **O carinho sem o crédito faz o pet dormir mais.** O R-CORPO fica acordado em 0,5121 das
  decisões e o R0 em 0,5300: −0,0179 na diferença das médias. Este contraste não está no plano
  e não tem IC.
- **O crédito devolve uma parte:** o D3 é +0,0070 [+0,0067; +0,0073]. Com o crédito o pet come e brinca mais (no D1,
  +14,1 decisões de comer e +11,5 de brincar em 14 dias), mas isso não
  cobre o que o carinho tira.
- **A hora certa também puxa para acordado:** o D2 é +0,0096 [+0,0093; +0,0100]. O R-SORT é o braço que mais dorme (−0,0205 contra o R0,
  na diferença das médias).
- **A L-PORQUÊ foi escrita supondo o D1 no mesmo sentido do D2 e do D3.** Saiu o contrário: o D1 abaixo de 0, o D2 e o D3 acima. A
  regra devolve "pela recompensa na hora, e pelo que o pet aprende", e isso fica registrado como está. O que os números mostram é outra coisa: **o pet
  dorme mais com o carinho no corpo, e o que ele aprende com o crédito reduz essa perda** (D-RC-16).
- **Nos dias 8 a 14** o D1 encolhe para −0,0062 [−0,0069; −0,0056].

## 5. Por dono e por lugar (descritivo)

| recorte | T_ACORDADO, D1 | T_ACORDADO, D2 | T_ACORDADO, D3 | "Tempo bem", D1 |
|---|---|---|---|---|
| lugar `comedouro` | −0,0091 [−0,0099; −0,0084] | +0,0106 [+0,0099; +0,0113] | +0,0091 [+0,0085; +0,0097] | −0,0032 [−0,0057; −0,0006] |
| lugar `longe` | −0,0158 [−0,0166; −0,0150] | +0,0073 [+0,0067; +0,0080] | +0,0030 [+0,0024; +0,0036] | +0,0598 [+0,0506; +0,0690] |
| lugar `perto` | −0,0078 [−0,0083; −0,0073] | +0,0110 [+0,0106; +0,0114] | +0,0088 [+0,0084; +0,0091] | −0,0016 [−0,0025; −0,0007] |
| dono `aleatorio` | −0,0055 [−0,0061; −0,0049] | +0,0046 [+0,0040; +0,0052] | +0,0014 [+0,0009; +0,0019] | +0,0036 [+0,0005; +0,0068] |
| dono `atencioso` | −0,0142 [−0,0150; −0,0134] | +0,0149 [+0,0142; +0,0156] | +0,0126 [+0,0120; +0,0132] | +0,0252 [+0,0166; +0,0337] |
| dono `incoerente` | −0,0141 [−0,0151; −0,0132] | +0,0148 [+0,0142; +0,0155] | +0,0128 [+0,0122; +0,0134] | +0,0327 [+0,0254; +0,0400] |
| dono `relapso` | −0,0098 [−0,0104; −0,0093] | +0,0042 [+0,0036; +0,0047] | +0,0010 [+0,0006; +0,0015] | +0,0118 [+0,0079; +0,0158] |

- **O D1 do T_ACORDADO é negativo em todos os recortes,** de −0,0055 a −0,0158.
- **O "Tempo bem" só sobe no `longe`** (+0,0598 [+0,0506; +0,0690]). No `comedouro` e no `perto` ele cai
  (−0,0032 [−0,0057; −0,0006] e −0,0016 [−0,0025; −0,0007]), dentro da margem de 0,032.
- **O ganho do "Tempo bem" não se separa do carinho no corpo:** o D2 e o D3 dele são +0,0025 [−0,0007; +0,0056] e +0,0012 [−0,0015; +0,0038]. Os três
  braços com carinho ficam perto uns dos outros, acima do R0.

## 6. As guardas

- **A taxa por episódio:** o D1 é +0,0209 [+0,0147; +0,0270]. Sem veredito automático (D-RC-11).
- **O "Tempo bem" por lugar:** na seção 5.
- **A saúde dos dias 8 a 14: não medida** (D-RC-15).

## 7. O que não muda

Nada no cérebro, no corpo, no motor nem na web. A chave do ELOGIO segue desligada no jogo. O `engine.py` não muda.

## 8. O que esta run não demonstra

- **Nada sobre jogadores:** o dono simulado recompensa toda vez e na hora.
- **Nada sobre outras doses:** o resultado vale para g = 2S e W = 1. O "não" daqui não diz que nenhuma dose funcionaria.
- **Nada sobre outras recompensas** (comida a mais, brinquedo, o crédito do intervalo do R2).
- **Nada sobre o corpo depois da C3 ou da C4,** nem sobre o jogo web, nem fora dos 14 dias e das 12 células.
- **Nada sobre a saúde do pet:** a guarda não foi medida.
- **A separação entre o crédito e o corpo não é perfeita:** os braços divergem depois do primeiro carinho, e o crédito alcança
  também os carinhos do próprio dono.
- **O δ_A (0,02), a margem (0,032) e os pisos são SEM FONTE,** e foram escritos depois de ver 20 unidades das sementes dos testes
  (D-RC-5).

## 9. As decisões que ficam para o Matheus

| nº | a decisão | a recomendação | o custo de errar |
|---|---|---|---|
| RC-8 | medir a guarda que faltou (a saúde dos dias 8 a 14) pelo replay dos logs | não agora: a resposta da pergunta não depende dela; medir se o carinho com crédito for cogitado para o jogo | baixo: perto de 1 h de máquina, e a cópia dos logs está guardada |
| RC-9 | seguir com a recompensa como caminho para o pet mais acordado | não: com esta dose o pet dorme um pouco mais, e o que pesa é o carinho no corpo | médio: outra dose ou outra recompensa é outra pergunta, com plano próprio |
| RC-10 | olhar por que o carinho no corpo faz o pet dormir mais | só se a pergunta voltar; começa por leitura do corpo, sem vidas novas | baixo |

Os sha256: `resultado.json` `97892493…`, `medidas.json` `e8333972…`, `vidas.tar.gz`
`3a68a35f…`. A cópia do `vidas.tar.gz` fica em `D:\Trab\digilab\guarda_vidas\recompensa_run`, só leitura.
