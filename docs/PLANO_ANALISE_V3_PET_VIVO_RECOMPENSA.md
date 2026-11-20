# PLANO DE ANÁLISE V3 — PET_VIVO, o teste de recompensa: o carinho depois do comer e do brincar deixa o pet mais tempo acordado? (2026-11-20, Claude Code, Fable 5.2)

**Status: APROVADO pelo Matheus em 2026-11-20.** À pergunta "Aprova o plano do teste de recompensa e as RC-1 a RC-7 pela
recomendação?", nesta sessão, a resposta foi "Aprovo todas" (D-RC-7). As decisões RC-1 a RC-7 da seção 10 estão DECIDIDAS pela
recomendação. Os números seguem SEM FONTE. O pedido do plano foi dele, no mesmo dia ("Sim, faz o plano do teste de recompensa").
**Nenhuma vida e nenhuma conta deste plano rodam antes de cinco coisas:**
1. a marca "APROVADO pelo Matheus" neste cabeçalho (feita acima);
2. a faixa de sementes reservada pelo coordenador no `experiments/bancada/faixas.py` (a seção 4);
3. o código da seção 8 na `main`, com os testes dele;
4. o `pre_run` respondendo "pode rodar" (uma run por vez; a C4 da CORPO também espera a máquina);
5. as conferências da seção 5, que falham alto antes de qualquer medida.

**De onde vem:**
- a pergunta do Matheus: **se o dono recompensar mais o comer e o brincar, o pet fica mais tempo acordado?**
- o [resultado do R-sono](RESULTADO_V3_PET_VIVO_SONO.md): "boa parte passa pelo sorteio: vale um teste de recompensa". Ele disse por
  onde o pet dorme, e não o que a recompensa faria;
- o [resultado do ELOGIO](RESULTADO_V3_ELOGIO.md): o crédito do carinho existe no modular (`ConfigElogio`, desligada). Lá, com
  g = S/4, o carinho na hora não ensinou a fruta X além do pet sem carinho, e "um g maior só volta com um plano novo". Este é um
  plano novo, com outra pergunta.

**O que este teste não é:** não é o R2 (a CREDITO_INTERVALO): nada do intervalo entre as decisões é creditado. Nenhum mecanismo novo
entra no cérebro, no corpo nem no motor. O `engine.py` não muda, e nada vai para a web.

**Os números que este plano cita** saem de 20 unidades das sementes dos testes (101 a 505), contadas por um script fora do
repositório, ou são fatos do código. Não são vidas de pesquisa e não são resultado. **Nenhuma alegação de novidade.**

## 1. A pergunta, os fatos do código e o desfecho esperado

**Os fatos do código** (conferidos em 2026-11-20, a `main` em `3ed5fdd6`):
- **"Recompensar" no jogo de hoje é o carinho** (o botão Elogiar é o acariciar). Os botões de nota saíram em 2026-10-07
  (`DECISAO_PRODUTO_SEM_ELOGIO_BRONCA.md`): o carinho age pelo corpo.
- **No corpo,** o carinho baixa a solidão e sobe o humor (`corpo.py:436`). Isso vale com ou sem a `ConfigElogio`.
- **No cérebro, só com a `ConfigElogio` ligada** (`adapt.py:705`): o que o carinho mudou no corpo vira um sinal, multiplicado pelo
  ganho g, e vai às últimas W decisões. Ele sobe a linha do hábito do comportamento creditado (o P2) e, se a decisão consumiu uma
  comida, o desfecho dela (o P1).
- **O crédito pequeno some no arredondamento.** O P2 é feito em inteiros. Nas sementes dos testes, com g = S/4 (o do ELOGIO), só
  26 % a 34 % dos créditos mudam a linha do hábito; com g = 2S, 52 % a 54 % (a seção 2.2).
- **O passo do dono e o da decisão são iguais** (15 ticks). O carinho dado no passo seguinte a uma decisão credita essa decisão com
  W = 1 (conferido no protótipo).
- **Alguns donos da C4 já acariciam por conta própria** (o relapso, por exemplo; o atencioso não). Com a `ConfigElogio` ligada,
  esses carinhos também são creditados.
- **O sono que segura** (`ConfigSonoSegura`) está ligado no pet do jogo (o v38). Com ele, só o adormecer passa pelo sorteio.

**As perguntas:**
- **Q-ACORDADO:** o pet cujo dono acaricia depois do comer e do brincar passa mais decisões acordado do que o pet de hoje?
- **Q-PORQUÊ:** se muda, é pelo que o pet aprende (o crédito), pela hora do carinho (a contingência) ou só pelo carinho no corpo?
- **Q-BEM:** o que acontece com o "Tempo bem" (a medida primária do projeto, D-MP-1)?

**O desfecho esperado é "não: dorme mais ou fica igual".** Nas 20 unidades das sementes dos testes (a seção 2.2), o pet com o
carinho ficou de 0,001 a 0,037 **menos** tempo acordado do que o pet sem carinho, com as duas doses. O carinho na hora ficou de
0,007 a 0,018 acima do carinho sorteado com g = 2S, abaixo do tamanho que este plano chama de relevante (0,02). É uma previsão
grosseira: 5 sementes por célula, em 4 das 12 células.

## 2. Os quatro itens da ficha de entrada

### 2.1 O que as vidas gravadas já respondem, e por que não bastam

- **Já respondem:** por onde o pet dorme (o R-sono). No v38, de 11 % a 13 % das decisões de dormir passam pelo sorteio, e a parte
  aprendida do peso do dormir é 0.
- **Não bastam:** nenhuma vida gravada tem o carinho depois do comer e do brincar, nem a `ConfigElogio` ligada com os donos da C4.
  Um replay não serve: o carinho muda o corpo e as decisões seguintes. **O teste pede vidas novas.**

### 2.2 A contagem do evento e a prévia, nas sementes dos testes

O protótipo: o pet do v38 (`pv2.fabricas` com `v38=True`), 14 dias, as sementes 101, 202, 303, 404 e 505, 2 donos e 2 lugares. Em
cada unidade, três vidas: sem carinho a mais, com o carinho depois de cada decisão de comer ou brincar, e com o mesmo número de
carinhos em passos sorteados. A `ConfigElogio` estava ligada nas três, com W = 1. **Não são vidas de pesquisa.**

| g | lugar, dono | acordado, sem carinho | com carinho − sem (desvio) | na hora − sorteado (desvio) | carinhos por vida | com sinal 0 |
|---|---|---|---|---|---|---|
| S/4 | `comedouro`, atencioso | 0,538 | −0,025 (0,009) | +0,003 (0,004) | 149 a 156 | 0 |
| S/4 | `comedouro`, relapso | 0,528 | −0,017 (0,002) | +0,001 (0,006) | 174 a 190 | 44 em 5 vidas |
| S/4 | `longe`, atencioso | 0,574 | −0,037 (0,016) | +0,001 (0,012) | 123 a 150 | 0 |
| S/4 | `longe`, relapso | 0,511 | −0,005 (0,012) | +0,003 (0,009) | 201 a 214 | 48 em 5 vidas |
| 2S | `comedouro`, atencioso | 0,538 | −0,010 (0,011) | +0,018 (0,004) | 197 a 209 | 0 |
| 2S | `comedouro`, relapso | 0,522 | −0,009 (0,007) | +0,008 (0,008) | 187 a 215 | 38 em 5 vidas |
| 2S | `longe`, atencioso | 0,574 | −0,032 (0,010) | +0,007 (0,016) | 139 a 170 | 0 |
| 2S | `longe`, relapso | 0,510 | −0,001 (0,015) | +0,011 (0,006) | 193 a 235 | 45 em 5 vidas |

- **O evento sobra:** o pet decide comer de 54 a 123 vezes e brincar de 23 a 112 vezes por vida. O mínimo visto é 123 carinhos por
  vida.
- **Nenhum carinho teve sinal negativo.** Com o relapso, cerca de 1 em 20 tem sinal 0 (o corpo já sem solidão a baixar).
- **A dose:** a fração dos créditos que mudam a linha do hábito, em 4 vidas por dose: 0,26 a 0,34 com S/4; 0,48 a 0,51 com S/2;
  0,46 a 0,57 com S; 0,52 a 0,54 com 2S.
- **Com o relapso, o "sem carinho" do protótipo não é o pet de hoje:** a `ConfigElogio` estava ligada, e os carinhos do próprio dono
  foram creditados. Por isso as duas linhas do relapso diferem entre as doses. Na run, o braço de base tem a chave desligada (a
  seção 3).
- **O "Tempo bem"** variou de −0,005 a +0,126 (com carinho − sem), sem padrão em 5 sementes. Não entra no desfecho esperado.

### 2.3 A precisão, calculada antes

- A leitura é pela média das 12 células em cada unidade, n 200, IC95 pelo t.
- O maior desvio visto da diferença entre dois braços, numa célula só, é 0,016. Com n 200, a meia-largura do IC95 fica perto de
  0,002 numa célula, e menor na média das 12.
- **Isso resolve o tamanho relevante (0,02) com folga.** Cinco sementes dão um desvio grosseiro: é ordem de grandeza.
- Para o "Tempo bem", o desvio do contraste entre braços nas vidas da C3 foi de 0,015 a 0,068 por lugar
  (`PLANO_ANALISE_V3_CORPO_C4.md`, a tabela da precisão): a meia-largura com n 200 fica abaixo de 0,010, contra a margem de 0,032.

### 2.4 O corpo, o pet e os donos

- **O pet é o do jogo que o Python tem** (o v38 do PV-2: os inatos do E1, o sono que segura, o lance do dono, as duas regras do E1 e
  o bebê nas primeiras 96 decisões). É a recomendação do resultado do R-sono: sem o sono que segura, o teste mede uma janela que o
  jogo não tem.
- **O corpo é o de hoje,** antes da C3 e da C4 da CORPO. Se o teto do combustível for adotado, a exaustão muda, e o plano que usar
  esta leitura diz se mede de novo.
- **Os donos e os lugares são os da C4:** 4 donos × 3 lugares, 12 células. O R-sono mostrou que o caminho do sono depende do dono;
  cada dono sai ao lado.

## 3. Os braços (RC-1, RC-3 e RC-4)

**O carinho da recompensa:** no passo do dono seguinte a cada decisão do pet de comer ou de brincar, um carinho
(`AcaoUsuario.ACARICIAR`), pelo gancho `carinho` da bancada, fora do orçamento, como no ELOGIO (D-EL-10). Vale a vida inteira. O
dono só lê o que o pet fez.

| braço | o carinho a mais | a `ConfigElogio` | para que serve |
|---|---|---|---|
| R0 | nenhum | desligada | o pet de hoje |
| R-CORPO | depois do comer e do brincar | desligada | o carinho só no corpo, sem crédito |
| R-CB | depois do comer e do brincar | ligada, g = 2S, W = 1 | a recompensa da pergunta |
| R-SORT | o mesmo número do R-CB da mesma unidade e célula, em passos sorteados | ligada, g = 2S, W = 1 | o controle da hora do carinho, como o E-sorteado do ELOGIO |

- **A dose é fixa e escrita antes (RC-3):** g = 2S, o topo da grade do ELOGIO (D-EL-8), onde cerca de metade dos créditos chega ao
  hábito. W = 1, porque o carinho chega no passo seguinte e a decisão recompensada é a última. **Não há calibração:** uma run só.
- **O R-SORT** sorteia os passos com uma rng própria, `derivar_semente("recompensa-sorteado", semente)`, uniforme nos passos da
  vida, sem olhar o pet. Ela não toca o mundo nem o cérebro.
- **Nos braços com a chave ligada, os carinhos do próprio dono também são creditados.** O contraste R-CB − R-SORT é limpo disso (os
  dois têm a chave). O R-CB − R0 e o R-CB − R-CORPO o incluem, nos donos que acariciam. Com o atencioso, que não acaricia, os três
  contrastes são limpos.
- **O dono simulado recompensa toda vez.** Pessoas reais recompensam fora de hora e de forma inconsistente (Thomaz e Breazeal,
  `10.1016/j.artint.2007.09.009`). O teste mede o teto de um dono perfeito, e não um jogador.

## 4. As células, as sementes e o tamanho (RC-5 e RC-6)

- **As células:** 4 donos (atencioso, incoerente, relapso, aleatório) × 3 lugares (`comedouro`, `longe`, `longe_fixo`), 14 dias.
- **As unidades:** 200 sementes independentes (k = 1). Cada unidade vive os 4 braços nas 12 células: **9 600 vidas.**
- **A faixa: 108001…108200, PROPOSTA.** Conferida livre no `faixas.py` da `main` (`3ed5fdd6`) e nos PRs abertos em 2026-11-20. Ela
  é pedida ao coordenador e entra na tabela, com o PR do código, antes de qualquer vida.
- **Nenhuma vida da faixa roda antes do APROVADO.** A fumaça do código usa as sementes dos testes.

## 5. As conferências e as premissas

**As conferências, que falham alto antes de qualquer medida:**
- **C-G1:** cada vida rejogada pelo log dá o mesmo log.
- **C-HOJE:** o R0 é o pet do v38 de hoje, byte a byte (a mesma vida do `pv2.viver` com `v38=True`).
- **C-CORPO:** no R0 e no R-CORPO o cérebro não tem o gancho do carinho, e nenhum crédito do carinho existe.
- **C-HORA:** no R-CB e no R-CORPO, todo carinho da recompensa cai no passo seguinte a uma decisão de comer ou de brincar, e toda
  decisão dessas recebe um; no R-CB, o crédito dele vai a essa decisão.
- **C-MESMO-N:** o R-SORT tem o mesmo número de carinhos a mais do R-CB da mesma unidade e célula.

**As premissas.** A que falha fica registrada e não para a run; a leitura diz o que cai com ela. Os pisos são PROPOSTOS e SEM FONTE.

| premissa | o que confere | o piso | visto nas sementes dos testes | se falhar |
|---|---|---|---|---|
| P-EVENTO | os carinhos da recompensa por vida do R-CB | pelo menos 50 em 95 % das vidas | 123 a 235 | a célula sai da leitura, dita |
| P-DOSE | a fração dos créditos do R-CB que mudam a linha do hábito | pelo menos 0,30 | 0,52 a 0,54 | a leitura "pelo que o pet aprende" cai |
| P-SINAL | os carinhos do R-CB com sinal negativo | nenhum | nenhum | registrado; os de sinal 0 são contados, sem piso |

## 6. As medidas (no `digilab/metrics.py`, uma vez só)

Por vida, nos dias 1 a 14:
- **T_ACORDADO:** a fração das decisões em que o pet não escolheu dormir. É a medida da pergunta.
- **"Tempo bem":** a fração das decisões sem privação e sem exaustão (`tempo_bem_nas_decisoes`, com os limiares de hoje, 0,15 e
  0,25). É a medida primária do projeto (D-MP-1).
- **As guardas da D-MP-1:** a saúde dos dias 8 a 14 e a taxa por episódio.
- **Os descritivos:** as decisões de comer e de brincar; os caminhos do sono do R-sono (`medidas_caminho_sono`, com o rastro
  ligado, que só lê); os carinhos, o sinal e os créditos; a linha do hábito do comer e a do brincar no fim da vida; o T_ACORDADO
  dos dias 8 a 14.

**Os contrastes,** por unidade, na média das 12 células, IC95 pelo t (n 200):
- **D1 = R-CB − R0:** o efeito inteiro da recompensa. Responde a Q-ACORDADO.
- **D2 = R-CB − R-SORT:** a hora do carinho.
- **D3 = R-CB − R-CORPO:** o crédito, com o carinho na mesma regra.
- Cada um também por dono e por lugar, como descritivo.

## 7. As regras de leitura, escritas antes (RC-2 e RC-7)

**O tamanho relevante, δ_A = 0,02** (PROPOSTO, SEM FONTE): 2 pontos do tempo, cerca de 29 minutos por dia do pet.

**L-ACORDADO,** pelo IC95 do D1 no T_ACORDADO, em ordem:

| o que sai | a leitura |
|---|---|
| o limite de cima < 0 | "não: com a recompensa o pet dorme mais" |
| o IC inteiro dentro de ±δ_A | "não: fica igual" (se o limite de baixo passar de 0, "sobe, mas abaixo do relevante") |
| o limite de baixo > δ_A | "sim, fica mais tempo acordado" |
| outro caso | "inconclusivo", com os números |

**L-PORQUÊ,** só se o D1 não for "fica igual", pelos IC95 do D2 e do D3:
- o limite de baixo do D2 e o do D3 acima de 0: "pela recompensa na hora, e pelo que o pet aprende";
- o do D3 acima de 0 e o do D2 não: "pelo crédito, em qualquer hora";
- nenhum dos dois acima de 0: "pelo carinho no corpo, e não pelo que o pet aprende".
- Com a P-DOSE falha, só a terceira leitura pode sair.

**L-BEM,** pelo IC95 do D1 no "Tempo bem" (a margem 0,032 é a das runs anteriores, sem fonte para esta fração):

| o que sai | a leitura |
|---|---|
| o limite de baixo > 0 | "o pet fica melhor" |
| o limite de baixo > −0,032 | "não piora" |
| o limite de cima < −0,032 | "piora" |
| outro caso | "inconclusivo" |

As guardas (a saúde dos dias 8 a 14, a taxa por episódio e o "Tempo bem" por lugar) saem ao lado, com o mesmo critério da C4.

**O que as regras não decidem:** se o crédito do carinho vai para o jogo. Isso é decisão do Matheus, com as três leituras.

## 8. O que falta antes da run (o PR do código, depois do APROVADO)

- `experiments/recompensa.py`: o dono do carinho (o molde é o `DonoElogioFruta`), os 4 braços sobre `pv2.fabricas` com `v38=True`,
  e a rng do R-SORT. **Nada muda no cérebro, no corpo nem no motor.**
- `metrics.py`: o T_ACORDADO. As outras medidas já existem.
- `experiments/run_v3_pet_vivo_recompensa.py` e a config, com as conferências da seção 5, as recusas de sempre (o plano APROVADO, a
  pasta de saída, o `pre_run`, 10 GB livres) e a faixa no `faixas.py`.
- Os testes: o carinho na hora certa conferido à mão numa vida curta, o R0 igual ao v38 de hoje, o R-SORT com o mesmo número, a
  rng separada, as falhas altas e as regras de leitura.
- A fumaça em vidas das sementes dos testes, só para o custo. Nenhuma medida é lida nelas.
- A seção `PR-PET-VIVO-RECOMPENSA` do `docs/PREREGISTRO.md` já entra com este plano, antes da run.

## 9. O custo e a máquina

- **O tempo:** o protótipo deu 1,75 s por vida de 14 dias. Com o replay do G1, cerca de 3,5 s. As 9 600 vidas, com 4 processos,
  ficam perto de 2,3 h. Se a projeção da fumaça passar de 4 h, a run não roda e o plano volta ao Matheus (RC-6).
- **O disco:** os logs comprimidos das 9 600 vidas ficam perto de 150 MB (os 5 120 da run do PV-2 deram 72 MB). O piso é 10 GB
  livres.
- **A vez:** uma run por vez, até 4 processos (V3-D8). A C4 da CORPO também espera a máquina; a ordem entre as duas é do Matheus.

## 10. As decisões com o Matheus (DECIDIDAS pela recomendação em 2026-11-20, "Aprovo todas"; D-RC-7)

| nº | a decisão | a recomendação | o custo de errar |
|---|---|---|---|
| RC-1 | o que é "recompensar" | um carinho no passo seguinte a cada decisão de comer ou brincar, creditado pela `ConfigElogio` | médio: outra forma (comida a mais, brinquedo) é outra pergunta e outra run |
| RC-2 | a medida | o T_ACORDADO responde a pergunta; o "Tempo bem" sai ao lado, como a primária do projeto, e nenhum dos dois é gate | médio: só o T_ACORDADO esconderia um pet acordado e pior |
| RC-3 | a dose | g = 2S e W = 1, fixos, sem calibração | médio: com dose menor o crédito some no arredondamento; a dose de 2S é o teto da grade, e não um valor de jogo |
| RC-4 | os braços | os quatro da seção 3 | baixo: sem o R-CORPO e o R-SORT não se sabe por que mudou |
| RC-5 | o pet e o corpo | o v38 (com o sono que segura), o corpo de hoje, as 12 células da C4 | médio: se a C4 mudar o corpo, as frações mudam e a leitura pede outra medida |
| RC-6 | o tamanho, a faixa e o corte | 200 unidades, 9 600 vidas, a faixa 108001…108200, o corte de 4 h | baixo: cerca de 2,3 h de máquina |
| RC-7 | os números da leitura | δ_A = 0,02 e a margem 0,032 do "Tempo bem", SEM FONTE; os pisos da seção 5 | médio: eles separam "fica igual" de "sim" |

## 11. O que este plano não demonstra, mesmo depois da run

- **Nada sobre jogadores.** O dono simulado recompensa toda vez e na hora.
- **Nada sobre outras doses.** Com g = 2S o resultado vale para g = 2S. Um "não" aqui não diz que nenhuma dose funcionaria.
- **Nada sobre outras recompensas** (comida a mais, brinquedo, o crédito do intervalo do R2).
- **Nada sobre o corpo depois da C3 ou da C4,** nem sobre o jogo web, nem fora dos 14 dias e das 12 células.
- **Nada sobre o que é bom para o pet além do "Tempo bem" e das guardas.** Ficar mais acordado não é, por si, melhor.
- **A separação entre o crédito e o corpo não é perfeita:** os braços divergem depois do primeiro carinho, e nos donos que acariciam
  o crédito alcança também os carinhos deles.
- **A prévia veio de 20 unidades das sementes dos testes,** vistas antes de escrever o desfecho esperado e os números da leitura.
