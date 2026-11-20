# PLANO DE ANÁLISE V3 — PET_VIVO, R-sono: o sono vem do reflexo ou do sorteio? (2026-11-20, Claude Code, Fable 5.2)

**Status: PROPOSTO.** As decisões SN-1 a SN-5 da seção 9 estão abertas. Os cortes são PROPOSTOS e SEM FONTE. **Nenhum replay e
nenhuma conta deste plano rodam antes de quatro coisas:**
1. a marca "APROVADO pelo Matheus" neste cabeçalho;
2. o código da seção 7 na `main`, com os testes dele;
3. o `pre_run` respondendo "pode rodar" (uma run por vez: a CORPO pode rodar a conferência do "Tempo bem" nas vidas da C3);
4. as conferências da seção 3, que falham alto antes de qualquer medida.

**De onde vem:**
- o pedido do Matheus à gerência da V3, em 2026-11-20, repassado pela sessão coordenadora: um replay do sono antes do R2, sem vida
  nova e sem faixa ("Sim, pede o replay do sono"). O repasse não é aprovação deste plano: a aprovação é dele, nesta sessão;
- o [resultado do R-a](RESULTADO_V3_PET_VIVO_RA.md): "só o sono". O R2 se reduz a ensinar o valor de dormir;
- a pergunta dele: **se o dono recompensar mais o comer e o brincar, o pet fica mais tempo acordado?**

**O que o R-sono é:** outra leitura das mesmas vidas do R1 e do R-a. Nada é creditado, nada muda no cérebro, e nenhuma vida nova
roda. **O R-sono não é o R2** e não testa recompensa nenhuma: ele diz por qual caminho o pet dorme hoje.

**Este plano não calcula nenhum número de resultado.** Os números que ele cita saem das sementes dos testes (101 a 505) ou são fatos
do código. **Nenhuma alegação de novidade.**

## 1. A pergunta, o fato do código e o desfecho esperado

**O fato do código** (conferido em 2026-11-20, `digilab/digibrain/arb.py`, a `main` em `5bae4227`):
- **O reflexo:** com a leitura da energia abaixo de `lambda_sono` (S/4 = 256, `config.py:3038`, PROPOSTO), o M-ARB escolhe o dormir
  sem sorteio (`Arbitragem.reflexo`, `arb.py:131`, e `escolher`, `arb.py:187`). Ele não lê nenhum peso: nada aprendido muda essa
  decisão.
- **Os pesos:** fora do reflexo, o dormir é uma unidade como as outras. A ativação dela soma o inato com os termos aprendidos
  (incentivo, hábito, memória, persistência), e a escolha sai do sorteio proporcional aos pesos. Só esse dormir é alcançável pela
  recompensa.
- **O sono que segura** (`ConfigSonoSegura`) estende o reflexo ao pet que já dorme, até a energia passar de `lambda_acordar`. Ele
  está **desligado** no HOJE da run do PV-2 e **ligado** na checagem do v38 (`pv2.py`, `v38=True`).

**As perguntas:**
- **Q-CAMINHO:** que fração do sono do pet vem do reflexo, e que fração passa pelos pesos?
- **Q-MARGEM:** no dormir que passa pelo sorteio, com que energia o pet está, e com que folga o dormir ganha?

**O desfecho esperado é "boa parte passa pelo sorteio".** Ele vem das sementes dos testes (a seção 2.2): lá, de 0,56 a 0,69 das
decisões de dormir ficam em episódios que os pesos começaram. Se sair, vale um teste de recompensa (que é outra run, com plano
próprio). Se sair "quase tudo reflexo", a alavanca para o pet ficar acordado é o corpo, e não a recompensa.

## 2. Os quatro itens da ficha de entrada

### 2.1 O que as vidas gravadas já respondem, e por que não bastam

- **Já respondem:** o pet dorme em cerca de 620 das 1 343 decisões de uma vida (R-a, seção 4.3).
- **Não bastam:** o `medidas.json.gz` do R1 e o do R-a guardam médias por comportamento. Nenhum guarda, por decisão, se o dormir
  veio do reflexo, a energia da hora nem os pesos das unidades.
- **Por isso o R-sono rejoga as mesmas vidas pelo log,** com a `ConfigRastro` ligada, como o R1 e o R-a. O `motivo` de cada decisão
  já traz o `reflexo`, o `u` do sorteio, os pesos das unidades e a leitura da energia. Nenhuma vida nova e nenhuma faixa nova.

### 2.2 A contagem do evento da premissa, nas sementes dos testes

O evento é a decisão de dormir, por caminho. A contagem saiu de 15 vidas das sementes dos testes (101, 202, 303, 404 e 505; o HOJE
do PV-2, o dono atencioso, 14 dias, 1 344 decisões por vida). **Não são vidas de pesquisa.**

| lugar | decisões de dormir por vida | pelo reflexo | pelo sorteio | candidato único | F_PESOS (média; desvio entre as 5 vidas) |
|---|---|---|---|---|---|
| `comedouro` | 614 a 633 | 80 a 146 | 470 a 526 | 5 a 10 | 0,69; 0,08 |
| `longe` | 573 a 612 | 100 a 264 | 334 a 456 | 4 a 17 | 0,56; 0,10 |
| `longe_fixo` | 583 a 670 | 34 a 564 | 106 a 522 | 0 a 27 | 0,56; 0,34 |

- **Os dois caminhos têm evento de sobra em toda vida:** o mínimo visto é 34 decisões pelo reflexo e 106 pelo sorteio.
- **O candidato único é raro** (até 27 por vida) e fica só como descritivo, somado aos pesos na F_PESOS (SN-2).
- **A F_PESOS da tabela conta decisões, e não ticks:** as decisões de dormir em episódios que os pesos começaram, sobre todas as de
  dormir. A do replay conta ticks (a seção 5).
- **Uma vida do `longe_fixo` saiu quase toda pelo reflexo** (F_PESOS 0,06, a semente 101). A fração varia muito entre vidas ali.

### 2.3 A precisão, calculada antes

- A leitura é por lugar, com n 200 unidades (a média dos 4 donos em cada unidade), IC95 pelo t.
- Com o maior desvio visto entre vidas (0,34, no `longe_fixo`), a meia-largura do IC95 com n 200 fica perto de 0,05. Com o desvio
  dos outros lugares (0,08 a 0,10), perto de 0,015. A média dos donos na unidade só aperta isso.
- **Isso resolve os cortes da seção 6** (0,10 e 0,25, a 0,15 um do outro). Cinco vidas de teste por lugar dão um desvio grosseiro: é
  ordem de grandeza, não estimativa.

### 2.4 O corpo e os donos

- **O corpo é o de hoje,** o das vidas da run do PV-2 (antes da C3 e da C4 da CORPO). Se o teto do combustível entrar no corpo, a
  energia cai de outro jeito e a fração pode mudar: o plano que usar esta leitura diz se mede de novo.
- **Os donos são os 4 da C4.** A leitura da regra é a média deles; cada dono sai ao lado, como descritivo.
- **Por que não as vidas da C3:** elas têm outro corpo, que ainda não foi adotado, e a CORPO as usa agora. A fonte do R1 já tem as
  conferências prontas.

## 3. A fonte e as conferências

- **As vidas:** as do R1 e do R-a. O HOJE da run do PV-2 (2 400) dá a leitura; o OLF-0 (2 400) e o HOJE do v38 (320) saem ao lado.
  São 5 120 replays.
- **Onde estão:** `D:\Trab\digilab\v3-pet-vivo-pv2-run\artifacts_v3_pet_vivo\pv2\run\vidas.tar.gz` (72 MB, com o sha256 no
  `meta.json` da run do PV-2). **Esse arquivo não pode ser limpo antes do R-sono** (SN-5).
- **As conferências que falham alto,** antes de qualquer medida: a C-FONTE, a C-G1, a C-FECHO e a C-UMA-VEZ do R1, e duas novas:
  - **C-REFLEXO:** no HOJE e no OLF-0 (o sono que segura desligado), toda decisão com `reflexo` verdadeiro é dormir e tem a leitura
    da energia abaixo de `lambda_sono`, e toda decisão sem ele tem a energia em `lambda_sono` ou acima. No v38, toda decisão com
    `reflexo` é dormir;
  - **C-SOMA:** em cada vida, os caminhos somam todas as decisões de dormir, e os ticks dos caminhos somam os ticks de sono.

## 4. Os caminhos (SN-2)

Cada decisão de dormir cai em um caminho, pelo que o `motivo` grava:

| caminho | a condição | a recompensa alcança? |
|---|---|---|
| REFLEXO | `reflexo` verdadeiro e a energia abaixo de `lambda_sono` | não |
| SEGURA | `reflexo` verdadeiro e a energia em `lambda_sono` ou acima (só com o sono que segura: o v38) | não |
| SORTEIO | `reflexo` falso e `u` presente (dois candidatos ou mais) | sim |
| ÚNICO | `reflexo` falso e sem `u` (o dormir era o único candidato) | sim: outra unidade com peso positivo abre o sorteio |

- **Os pesos** são o SORTEIO mais o ÚNICO. **O reflexo** é o REFLEXO mais o SEGURA.
- **O episódio de sono** é a sequência de decisões de dormir seguidas. O caminho do episódio é o da **primeira** decisão dele: o
  sono que continua entra no caminho que o começou.
- **Os ticks** de uma decisão são os que vão até a decisão seguinte (pelo `tick` do rastro; a última vai até o fim da vida).

## 5. As medidas (no `digilab/metrics.py`, uma vez só)

Por vida:
- **M-DEC:** a fração das decisões de dormir em cada caminho.
- **M-TICKS:** os ticks de sono por caminho da decisão, e por caminho do episódio.
- **F_PESOS:** a fração dos ticks de sono em episódios que os pesos começaram. É a medida da regra.
- **F_PESOS-DEC:** a fração das decisões de dormir pelos pesos, sem olhar o episódio. Sai ao lado.
- **M-MARGEM, só nas decisões de dormir pelo SORTEIO:** a leitura da energia (a média e os quartis); a chance do dormir no sorteio
  (o peso dele sobre a soma dos pesos); a folga do peso do dormir sobre a segunda unidade de maior peso (negativa quando o dormir
  ganhou sem ser o maior); a fração dessas decisões em que o comer ou o brincar eram candidatos (peso positivo); e a parte aprendida
  da ativação do dormir (os termos fora o inato).
- **M-ACORDADO:** nas decisões acordadas com a energia em `lambda_sono` ou acima, a chance que o dormir tinha no sorteio. Diz quanto
  do tempo acordado já disputa com o sono.

Os resumos: por lugar (a média dos donos na unidade, n 200, IC95 pelo t), no HOJE, no OLF-0 e no v38 (n 40, 2 lugares); e por dono
e lugar, como descritivo.

## 6. A regra de leitura, escrita antes

Nenhuma medida é gate. A regra se lê no HOJE, nos 3 lugares, pelo limite do IC95 da F_PESOS. Os cortes (0,10 e 0,25) são PROPOSTOS
e SEM FONTE (SN-3).

| o que sai | a leitura | o que segue |
|---|---|---|
| o limite de cima < 0,10 nos 3 lugares | "quase tudo reflexo: a alavanca é o corpo" | recompensar o comer e o brincar não tira o pet do sono; o que muda o tempo acordado é a energia (o corpo) ou o `lambda_sono` |
| o limite de baixo > 0,25 em pelo menos 2 lugares | "boa parte passa pelo sorteio: vale um teste de recompensa" | um teste com vidas novas e plano próprio, que a M-MARGEM ajuda a desenhar |
| outro caso | "misto", com os números por lugar | o Matheus decide com os números; a M-MARGEM sai do mesmo jeito |

**O que a regra não decide:** se a recompensa de fato tira o pet do sono, quanto, nem se isso é bom para o pet. A M-MARGEM é
descritiva: uma folga pequena sugere que pouca recompensa basta, mas só o teste diz.

## 7. O que falta antes do replay (o PR do código, depois do APROVADO)

- `metrics.medidas_caminho_sono(motivos, lambda_sono, fim)`, que lê o que o `motivo` já grava. **Nada muda no cérebro, no corpo nem
  no motor.** O `engine.py` não muda.
- `experiments/run_v3_pet_vivo_sono.py`, que reusa a leitura da fonte e as conferências do R1, e a config
  `experiments/configs/v3_pet_vivo/sono.json`.
- Os testes: cada caminho conferido à mão numa vida curta, a C-REFLEXO e a C-SOMA numa vida das sementes dos testes, as falhas
  altas e a regra de leitura.
- A fumaça da C-G1 em 2 vidas reais, como no R1, antes do replay inteiro. Nenhuma medida é lida nelas.
- A seção `PR-PET-VIVO-SONO` no `docs/PREREGISTRO.md` já entra com este plano, antes da run.

## 8. O custo e a máquina

- **O tempo:** o R-a levou 33 min com 4 processos nas mesmas 5 120 vidas. O R-sono faz a mesma coisa com contas mais leves. Se a
  projeção da fumaça passar de 2 h, o replay não roda e o plano volta ao Matheus (SN-4).
- **O disco:** o D: tinha 80 GB livres em 2026-11-20. O replay grava cerca de 30 MB. O worker confere de novo antes de soltar; o
  piso é 10 GB.
- **A vez:** uma run por vez, até 4 processos (V3-D8). O `pre_run` é o gate; o R-sono não roda junto com a conferência do "Tempo
  bem" da CORPO.

## 9. As decisões com o Matheus (PROPOSTAS)

| nº | a decisão | a recomendação | o custo de errar |
|---|---|---|---|
| SN-1 | a fonte | as vidas do R1 e do R-a (o corpo de hoje), e não as da C3 | baixo: outro replay nas vidas da C3 custa cerca de 40 min, se o corpo novo for adotado |
| SN-2 | os caminhos e o episódio | os quatro da seção 4; o episódio entra no caminho da primeira decisão; o ÚNICO conta com os pesos | médio: contar por decisão, e não por episódio, sobe a fração dos pesos (a F_PESOS-DEC sai ao lado para comparar) |
| SN-3 | os cortes da F_PESOS | 0,10 e 0,25, SEM FONTE | médio: eles separam "a alavanca é o corpo" de "vale um teste de recompensa"; entre os dois, "misto" |
| SN-4 | o corte de custo | a projeção acima de 2 h não roda | baixo |
| SN-5 | o `vidas.tar.gz` | fica na máquina até o R-sono rodar | alto se for apagado: as vidas teriam de ser regeneradas, 4 h de máquina |

## 10. O que este plano não demonstra, mesmo depois do replay

- **Nada sobre a recompensa.** O replay diz por onde o pet dorme, e não o que aconteceria se o dono recompensasse mais o comer e o
  brincar. Essa resposta pede vidas novas.
- **Nada sobre o que é melhor para o pet.** Ficar mais tempo acordado pode custar energia e saúde. A medida primária ("Tempo bem")
  não entra aqui.
- **Nada sobre o corpo depois da C3 ou da C4,** nem sobre o jogo web, nem fora dos 14 dias e dos lugares da C4.
- **O v38 é descritivo:** 2 lugares, 40 unidades, e com o sono que segura ligado o reflexo segura mais.
- **Os cortes são SEM FONTE,** e a contagem da seção 2.2 vem de 15 vidas das sementes dos testes.
