# RESULTADO V3 — BOLA_DIAGNOSTICO (o replay R-b): por que o brincar não vira chute

- **Pedido:** o R-b do planejamento das próximas runs, aprovado pelo Matheus em 2026-11-19. A pergunta: por que cerca de 12 ações
  `brincar` por vida viram quase nenhum chute na bola (2 chutes em 420 vidas de pet no S0 da SOCIAL_PAR; 0 chutes em 400 pares na C2 e na
  C3 da CORPO).
- **O que é:** um diagnóstico. Sem vida nova, sem faixa de sementes, sem mudança no jogo ou no cérebro, e sem proposta de conserto em
  código. Os números novos daqui são descritivos; nada aqui é teste.
- **Resposta curta:** **a cadeia quebra no primeiro elo. O `brincar` só tem alvo com a bola a até 6 células do pet, e a bola fica a 30
  células do comedouro.** Nas vidas de par, o pet nunca chega perto dela: em 800 vidas de pet da C3, nenhuma das 384.000 decisões teve a
  bola no raio da visão. Quando a bola está à vista, a cadeia funciona: 76 % desses `brincar` viram chute.
- **De onde vem cada número:** `artifacts_v3_bola_diagnostico/resumo.json` (a soma) e `contagens.json` (uma linha por vida de pet),
  feitos por `python experiments/diagnosticar_v3_bola.py --c3 <a pasta artifacts_v3_corpo/c3> --processos 2`, no commit a15ccb3f, em
  387 s. O `meta.json` grava o sha256 de cada fonte.

## 1. A cadeia, lida no código

O caminho inteiro está em `digilab/mundo.py` (o `MotorMundo`) e em `digilab/digibrain/` (o cérebro modular). A decisão acontece a cada
15 ticks.

| elo | a condição | onde está |
|---|---|---|
| 0. o cérebro escolhe `brincar` | o `brincar` é uma unidade do M-IMPULSO. Com a bola à vista, a unidade é "brincar com a bola"; sem ela, é "brincar sem alvo", que existe sempre | `digibrain/impulso.py`, `alvos` |
| 1. a bola está à vista | a distância do pet à bola é ≤ 6 células (`raio_visao_celulas`) no começo da decisão, e a bola está entre os 8 objetos mais próximos (`max_vistos`) | `Mundo.perceber` |
| 2. o `brincar` tem alvo (a tentativa) | o único candidato do `brincar` é a bola vista, ou o `continuar` de um `brincar` anterior que não chegou. Sem candidato, o alvo é nenhum, e o pet não sai do lugar | `MotorMundo.candidatos`, `alvo_padrao_de`, `adapt.escolher_alvo` |
| 3. o pet chega | ele anda até 3,75 células por decisão (4 subunidades por tick × 15 ticks) e chega se fica a ≤ 1 célula da bola (`raio_pegar_celulas`). Então a bola a até 4,75 células é chutada na mesma decisão | `MotorMundo._consequencia` |
| 4. o chute | chegou com o alvo na bola: a bola rola (`rolar_bola`), o humor sobe, e o registro marca `brincou_com_bola` | idem |

O que decorre da leitura, antes de qualquer contagem:
- **O `brincar` não leva o pet até a bola.** Fora do raio da visão não há candidato, e não existe "ir até onde a bola está": o cérebro
  não guarda o lugar da bola. O pet só encontra a bola se outra ação o levar para perto dela.
- **O `brincar` sem alvo ainda vale para o pet:** ele reduz o tédio (`tedio_brincar`, −45.000; com a bola, `tedio_bola`, −135.000) e
  sobe o humor. Por isso o pet escolhe brincar na casa, sem bola.
- **A bola começa em (40, 15), no campo.** O ninho fica em (4, 15) e o comedouro em (10, 15), na casa: 36 e 30 células de distância.
  Depois de um chute ela rola de 3 a 10 células, e o dobro no campo.
- **Se o `brincar` não chega,** a ida fica pendente e só continua se a decisão seguinte for `brincar` de novo.
- **O Brincar do dono não mexe na bola nessas vidas:** o lance do dono (`ConfigLanceDono`), que joga a bola perto do pet, fica desligado
  nos orquestradores do A0 e da C3. O script para se achar um lance ou uma bola deixada pelo dono, e não achou nenhum.

## 2. As vidas lidas

As vidas não se guardam inteiras: o script refaz cada uma com o código da run e só lê a que confere com a gravada. Todas conferiram.

| fonte | o que é | vidas de pet | como se confere |
|---|---|---|---|
| A0 | a VIVO dos 210 pares da SOCIAL_PAR A0, as mesmas vidas do S0; 5 dias, dono atencioso, ração no comedouro | 420 | o sha256 do registro e das posições no `.json.gz` do par |
| C3, pares | os 400 pares do bloco II da CORPO C3 (100 por braço: CTRL, D, DTL, DTB); 5 dias, o mesmo substrato do A0 | 800 | o registro do grupo igual ao `.jsonl.gz` do `pares.tar.gz` |
| C3, um pet | uma amostra das vidas de um pet da CORPO C3: o braço CTRL, as 10 primeiras bases (106001 a 106010), as 12 células de dono × lugar; 14 dias | 120 | o `log_sha256` do `medidas.json.gz` |

- A amostra das vidas de um pet foi fixada antes da contagem. São 120 das 2.400 vidas do CTRL.
- Os artefatos da C3 não estão na `main`: foram lidos da worktree `v3-corpo-acoplamento` (PR #1035, aberto), sem alterar nada.

## 3. Em que elo a cadeia quebra

**"À vista"** é a bola a até 6 células do pet no começo da decisão. **"Com alvo"** é o que o registro do motor diz. **"Chute"** é o
`brincou_com_bola`.

| fonte | vidas de pet | `brincar` | por vida | com a bola à vista | com alvo | chutes | vidas que nunca tiveram a bola à vista |
|---|---|---|---|---|---|---|---|
| A0 | 420 | 5.006 | 11,9 | 3 | 3 | 2 | 418 |
| C3, pares | 800 | 13.716 | 17,1 | 0 | 0 | 0 | 800 |
| C3, um pet | 120 | 3.020 | 25,2 | 171 | 168 | 130 | 57 |

- **Nas vidas de par, o `brincar` morre no elo 1.** No A0, 5.003 dos 5.006 `brincar` não tinham alvo. Na C3, todos os 13.716.
- **Não é só o `brincar`: o pet nunca chega perto da bola.** No A0, a bola esteve à vista em 11 das 201.600 decisões, de qualquer ação.
  Nos pares da C3, em 0 de 384.000.
- **Quando a bola está à vista, a cadeia funciona.** Nas vidas de um pet, 168 dos 171 `brincar` com a bola à vista tiveram alvo, e 130
  viraram chute (76 %). No A0, foram 2 de 3.
- **O que sobra depois do elo 1 é pequeno:**
  - 38 tentativas não chegaram na mesma decisão. A decisão seguinte foi `brincar` em 20, `dormir` em 14 e `chamar atenção` em 4;
  - em 3 `brincar`, a bola estava no raio e o registro não tem alvo (uma célula só, incoerente em `longe_fixo`). A causa fica **NÃO
    CONFIRMADA**; o corte dos 8 objetos mais próximos é a hipótese.

### Por distância à bola

A distância do pet à bola no começo de cada `brincar`:

| fonte | ≤ 1 célula | ≤ 4,75 (chega numa decisão) | ≤ 6 (à vista) | ≤ 12 | ≤ 24 | > 24 |
|---|---|---|---|---|---|---|
| A0 | 0 | 2 | 1 | 4 | 172 | 4.827 |
| C3, pares | 0 | 0 | 0 | 0 | 454 | 13.262 |
| C3, um pet | 10 | 119 | 42 | 251 | 824 | 1.774 |

No A0, 96 % dos `brincar` acontecem a mais de 24 células da bola.

### Por lugar do mapa

Onde o pet estava em cada `brincar`, e onde ele passa as decisões:

| fonte | `brincar` na casa | no jardim | no campo | na mata | decisões na casa | no campo |
|---|---|---|---|---|---|---|
| A0 | 4.758 | 245 | 3 | 0 | 92,8 % | 0,03 % |
| C3, pares | 13.087 | 629 | 0 | 0 | 93,2 % | 0,03 % |
| C3, um pet | 1.428 | 1.003 | 450 | 139 | 51,8 % | 12,7 % |

Nas vidas de par, 93 % das decisões são na casa (x de 0 a 15), e o campo, onde a bola está (x de 34 a 47), recebe 3 em cada 10.000.

### Por lugar da comida e por dono (as 120 vidas de um pet da C3, CTRL)

O que decide o chute é **onde o dono põe a comida**, não quem é o dono:

| lugar da comida | vidas | `brincar` | com a bola à vista | chutes | vidas com chute | menor distância à bola (mediana) |
|---|---|---|---|---|---|---|
| comedouro | 40 | 819 | 1 | 1 | 1 | 16,8 células |
| longe | 40 | 1.088 | 45 | 33 | 13 | 5,2 |
| longe_fixo | 40 | 1.113 | 125 | 96 | 35 | 1,5 |

| dono | vidas | `brincar` | por vida | com a bola à vista | chutes | vidas com chute |
|---|---|---|---|---|---|---|
| aleatório | 30 | 438 | 14,6 | 31 | 26 | 14 |
| atencioso | 30 | 1.200 | 40,0 | 45 | 33 | 9 |
| incoerente | 30 | 1.199 | 40,0 | 58 | 42 | 11 |
| relapso | 30 | 183 | 6,1 | 37 | 29 | 15 |

- **Com a ração no comedouro, há 1 chute em 40 vidas de 14 dias.** Com a comida longe da casa, o pet anda pelo campo, passa perto da bola
  e chuta: 96 chutes em 40 vidas no `longe_fixo`.
- **O dono muda quanto o pet brinca, não se ele chuta.** O relapso brinca 6 vezes por vida e o atencioso 40, e os chutes ficam entre 26 e
  42 por 30 vidas.
- **Em todas as 2.400 vidas do CTRL** (direto das medidas gravadas da C3, sem replay), o `brincar` por vida vai de 4,6 (relapso no
  comedouro) a 48,5 (incoerente no `longe`). Os chutes dessas vidas não estão nas medidas.

### O que o pet faz com a bola à vista

Nas 120 vidas de um pet, a bola esteve à vista em 2.133 decisões:

| ação | decisões | fração |
|---|---|---|
| dormir | 978 | 45,9 % |
| explorar | 443 | 20,8 % |
| chamar atenção | 344 | 16,1 % |
| brincar | 171 | 8,0 % |
| comer | 156 | 7,3 % |
| emburrar e ocioso | 41 | 1,9 % |

O `brincar` é 8,0 % das decisões com a bola à vista, contra 1,9 % em toda a vida (3.020 de 161.280): a bola à vista quadruplica o
brincar, mas dormir e explorar ainda ganham.

## 4. A causa

- **CONFIRMADO, a causa principal:** nas vidas de par, e em toda vida com a ração no comedouro, o `brincar` não vira chute porque **a
  bola nunca entra no raio da visão**. O `brincar` não tem como ir até ela, e nada mais leva o pet ao campo. Não é o cérebro que recusa a
  bola, nem o pet que tenta e não chega.
- **CONFIRMADO:** com a bola à vista, 76 % dos `brincar` viram chute. Do elo 2 em diante, a cadeia está inteira.
- **CONFIRMADO, por leitura do código:** os 12 `brincar` por vida são a unidade "brincar sem alvo". Eles não são tentativas frustradas.
- **NÃO CONFIRMADO:**
  - por que o `brincar` é só 8 % das decisões com a bola à vista. Não li os pesos do cérebro nem o estado do pet nessas decisões;
  - os 3 `brincar` com a bola no raio e sem alvo;
  - o que acontece depois do chute. A bola rola de 3 a 20 células e pode sair da vista; não contei quantas vezes o pet a perde assim;
  - o jogo web. Nada daqui foi lido no motor em TypeScript, onde o lance do dono está ligado.
- **De outra sessão, não refeito aqui:** a run S da SOCIAL_PAR (PR #1010, aberto) pôs a bola uma vez na posição de P (o braço B2) e
  mediu 0,505 e 0,604 chute por dia de pet, contra 0 no controle. É o mesmo sentido: com a bola ao alcance, o pet chuta.

## 5. O que isso muda

### O braço B da SOCIAL_PAR (a bola entre os dois pets)

- **O que muda:** o B não tem premissa no substrato de hoje, e não é por falta de pares ou de dias. Com a ração no comedouro, o evento
  não pode acontecer. Pôr a bola perto uma vez (o B2) dá cerca de meio chute por dia, e depois a bola rola para longe e nada traz o pet
  de volta.
- **Recomendação:** não rodar o B de novo trocando só o substrato. Deixar o B como "inconclusivo por premissa" até existir uma mecânica
  que mantenha a bola ao alcance (o pet ir até a bola, que é a EQ-8 do equilíbrio do cuidado, hoje fora da rodada; ou o lance do dono
  ligado na bancada). Essa mecânica é decisão de produto, do Matheus. A decisão sobre o B é da Gerência da V3.
- **Custo de errar:** se o B rodar de novo sem a mecânica, gasta-se uma run para repetir "inconclusivo". Se o B ficar parado e a troca de
  bola entre os pets for importante para o produto, a pergunta social sobre a bola atrasa até a mecânica existir.

### A M-C1 do equilíbrio do cuidado (chutes por lance)

- **O que muda:** nada na medida. A M-C1 conta os chutes depois do lance do dono, que joga a bola a 2 ou 3 células do pet: o lance entra
  na cadeia depois do elo 1, que é o que quebra aqui. O 76 % deste diagnóstico (a bola à vista, sem lance e sem convite) é compatível com
  a régua de 0,8 chute por lance, mas não é a mesma medida.
- **O que fica claro:** a M-C1 mede a resposta ao lance, não o pet brincando sozinho. Um pet que passa na M-C1 pode nunca tocar na bola
  sem o dono, e é o que acontece hoje com a ração no comedouro.
- **Recomendação:** manter a M-C1 como está e não usá-la como evidência de que "a bola tem propósito" sem o dono. Se o Matheus quiser o
  pet brincando sozinho, isso pede uma medida nova e a mecânica da EQ-8.
- **Custo de errar:** baixo. O risco é só de leitura: tomar a M-C1 verde como "o pet usa a bola".

### A guarda S1 da CORPO (chutes por dia nos pares)

- **O que muda:** a S1 não é uma guarda. Nos 400 pares da C3, a bola não esteve à vista em nenhuma das 384.000 decisões, nos quatro
  braços. Um braço que estragasse o brincar com a bola passaria igual. A D-C3-5 já a tinha rebaixado a descritivo; este diagnóstico diz
  por quê.
- **Recomendação:** tirar a S1 dos pares e, se a CORPO quiser uma guarda da bola, medi-la nas vidas de um pet em `longe_fixo`, onde o
  evento existe (96 chutes em 40 vidas, 35 das 40 com chute, no CTRL). O piso e a forma são PROPOSTOS e ficam para o plano de quem usar.
- **Custo de errar:** se a S1 ficar como está, a C4 e a validação da CORPO seguem com uma linha que parece cobrir a bola e não cobre. Se a
  guarda nova entrar nas vidas de um pet, custa uma medida a mais numa run que já existe, sem vida nova.

## 6. Limites

- **As vidas de um pet são uma amostra:** 120 de 2.400, só o braço CTRL. Os pares são todos (210 do A0 e 400 da C3).
- **A posição da bola é refeita pelo script** a partir das rolagens gravadas no mundo, com a conta do `Mundo.bola_em`. Um teste confere o
  contador numa vida em que a bola começa ao lado do pet (`tests/test_bola_diagnostico.py`).
- **"À vista" aqui é só a distância.** O corte dos 8 objetos mais próximos não foi refeito.
- **Nenhum intervalo de confiança:** são contagens, e a diferença entre 0 em 13.716 e 130 em 171 não precisa de teste.

## 7. Resumo da etapa (2026-11-19)

O R-b refez 1.340 vidas de pet já gravadas (420 do A0, 800 dos pares da C3 e 120 de um pet da C3), todas conferidas contra a gravação, e
contou a cadeia do `brincar`. A cadeia quebra no elo 1: a bola fica a 30 células do comedouro, o `brincar` só mira a bola a até 6
células e não há como ir até ela. Com a bola à vista, 76 % dos `brincar` viram chute. O braço B da SOCIAL_PAR e a guarda S1 da CORPO
não têm o evento no substrato de hoje; a M-C1 não muda, porque o lance do dono traz a bola até o pet. Nenhum conserto foi proposto em
código.
