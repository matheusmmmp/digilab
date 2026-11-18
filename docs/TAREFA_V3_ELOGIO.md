# TAREFA V3 — ELOGIO: o carinho logo depois da ação acelera o aprendizado do modular (2026-11-16)

Coordenador: Gerente da V3 (Claude Code). Worker da etapa 1: Claude Code, Opus 5.5 (método), worktree `v3-elogio`. Status: **ABERTA; etapa 1
(só papel) ENTREGUE; D-EL-1 a D-EL-8 (seção 8) DECIDIDAS em 2026-11-16, pela recomendação ("Aprovo todas"). Etapa 2 (código) ENTREGUE (seção 10): a leitura achou
que o cenário da D-EL-1 não roda no modular (seção 9); D-EL-9 a D-EL-13 DECIDIDAS em 2026-11-17 ("Aprovo todas"). Etapa 3 (plano) PROPOSTA em 2026-11-17: `docs/PLANO_ANALISE_V3_ELOGIO.md`, parado no CHECKPOINT EL-3 com D-EL-18 a D-EL-24.**

Categoria: arquitetura (depois, implementacao e experimento). Origem: Matheus, 2026-11-16: "logo após o pet fazer alguma ação [...] se a gente
usar [...] o carinho, ou o elogiar logo após aquela ação, vai dar um boost maior de ele entender que aquilo é uma coisa boa". Com o pedido de
"projetar testes para a gente conseguir calibrar essa vontade". Na escolha da tarefa, "Uma que já existe".

## 0. Os cinco pontos

1. **A pergunta:** o carinho do dono logo depois de uma ação do pet faz o DigiBrain modular aprender essa ação mais depressa do que só a
   consequência natural? E isso vem da **contingência** (o carinho logo depois da ação certa), e não só de haver mais carinho?
2. **O que já existe:** o cérebro A faz isso desde a V2. O motor com `gestos` chama `mudanca_no_corpo(obs_antes, obs_depois)` no carinho, e
   o A credita o `sinal_corpo` dessa mudança à última decisão, pela janela da v1 (CD-4, `docs/TAREFA_V2_CORPO_DRIVES.md`, seção 8;
   `digilab/policies/lobos.py`, `mudanca_no_corpo`). **O modular não tem o gancho:** o `M-ADAPT` só registra o gesto
   (`receber_acao_dono`), e o carinho chega a ele só como o ponto de partida da decisão seguinte. A tarefa é dar ao modular o caminho que o A
   tinha, atrás de uma chave, e calibrar o tamanho dele.
3. **O cenário:** a escolha da fruta no mundo das frutas com o paladar (J5), que o modular já aprende pelo desfecho (o P1, as classes
   `a`, `b`, `c`). O dono elogia o consumo de uma fruta X, como o `DonoTapaFruta` da V2 punia o de X (o P1-c-tapaX,
   `docs/PLANO_ANALISE_V2_CORPO_DRIVES.md`). É o espelho positivo dele.
4. **A fonte:** o humano como treinador (TAMER, `10.1145/1597735.1597738`); o retorno humano que depende da política atual (MacGlashan et
   al., `arXiv:1701.06049`); as pessoas reais dão retorno antecipado e inconsistente (Thomaz e Breazeal, `10.1016/j.artint.2007.09.009`).
   Que o reforço imediato ensina mais depressa no adestramento de animais é **SEM FONTE** na lista verificada. **Nenhuma alegação de
   novidade:** o crédito do carinho já existe no A.
5. **Esta etapa é só papel.** O código, o plano de análise com a faixa e a run vêm depois, cada um com o sim do Matheus (seção 5).

## 1. Pergunta

**O crédito do carinho pelo corpo, logo depois da ação, acelera o aprendizado do modular sem atrapalhar o que a consequência natural ensina?**

A regra da vida do pet (2026-11-04) continua valendo: o treino não é "clicar carinho e tapa". O carinho aqui não é uma recompensa à parte.
Ele mexe no corpo (a solidão e o estresse caem; com o banheiro, também a falta de conforto), e o que o pet aprende é essa mudança no corpo,
creditada à ação que veio logo antes. Sem o carinho, a fruta continua ensinando sozinha pelo paladar e pela nutrição. O carinho só soma a ela.

### 1.1 Por que a contingência é a pergunta, e não o carinho

Um dono que faz mais carinho deixa o pet mais calmo e menos sozinho, e um pet calmo pode explorar e comer de outro jeito. Então "o pet do
dono que elogia aprendeu mais depressa" não basta: o controle tem o **mesmo número de carinhos** em momentos que não dependem da ação. A
diferença entre os dois é o efeito do crédito.

### 1.2 O que a literatura impõe ao desenho

- O dono humano típico não é coerente nem aleatório (Thomaz e Breazeal): um braço de dono **inconsistente** entra, que às vezes elogia a
  fruta errada e às vezes elogia antes de o pet comer.
- O retorno humano depende da política atual (MacGlashan et al.): quando o pet já come X, o elogio não traz informação nova. A leitura
  espera o efeito concentrado no começo da curva, e a retenção depois que o elogio para é uma medida própria.

## 2. Depende de

- A LZ2 da LIMPEZA (`docs/TAREFA_V3_LIMPEZA.md`): o código desta tarefa entra no modular e na bancada depois da LZ2a, para não colidir com a
  troca dos imports da base (`digilab/digibrain/base.py`).
- O modular precisa ler os receptores que o carinho mexe. **Premissa técnica a conferir na etapa 2 (P0):** com o corpo dos `gestos`, o
  modular tem os receptores da `solidao` e do `estresse`. Se não tiver, o carinho não muda nada que ele leia, e a tarefa para aí, registrada.
- O banheiro fica fora: o modular recusa o corpo dele hoje (os receptores da vontade e do conforto ficam fora do protótipo).

## 3. Mudança mínima

**No modular, atrás de uma chave desligada (`ConfigDigibrain.elogio_credito`, PROPOSTO):**
- o `M-ADAPT` ganha o gancho `mudanca_no_corpo(obs_antes, obs_depois)`, que o motor já chama no carinho;
- a mudança vira um sinal, `f = div_arred(g × sinal_corpo(antes, depois), S)`, com os mesmos drives e a mesma escala do corpo;
- o sinal vai à última decisão dentro de uma janela de W ticks, com o peso caindo com o atraso: `peso = S − div_arred(atraso × S, W)`,
  a forma da janela da v1 que o A usa;
- **a rota do sinal (D-EL-2):** ele soma ao `r` da opção da última decisão (o hábito do P2 e a valência do M-AFETO) e, quando a última
  decisão consumiu uma classe, ao desfecho dela no P1 (o que o pet espera daquela fruta).

Desligada, a vida de hoje sai byte a byte. O gabarito é gravado num commit próprio antes da mudança, e um teste confere.

**Na bancada:** o dono `DonoElogioFruta`, o espelho do `DonoTapaFruta`: um `acariciar` no primeiro passo do dono depois de cada consumo de
X, dentro do orçamento e contando como contato. As variantes dos braços (seção 4) mudam só quando e em que o dono faz o carinho.

Os três números, todos PROPOSTOS e SEM FONTE até a calibração: o ganho `g`, a janela `W` e a forma da queda (a linear da v1, D-EL-3).

## 4. Experimento e gate (se houver run)

Este é o esboço do plano. O plano de análise de verdade (`docs/PLANO_ANALISE_V3_ELOGIO.md`, com a faixa e os números) é escrito e
commitado antes da primeira vida, na etapa 3.

**Os braços** (todos com o modular, o corpo com `gestos`, o mundo das frutas com o paladar e o mesmo orçamento de contatos):

| braço | o dono |
|---|---|
| E0 | o `DonoComGestos` sem tapa: só a consequência natural |
| E-imed | E0 mais o carinho no primeiro passo depois de cada consumo de X |
| E-atraso | o mesmo carinho, com o atraso sorteado entre três valores (D-EL-5) |
| E-sorteado | **o controle principal:** o mesmo número de carinhos do E-imed da mesma unidade, em passos sorteados por uma rng própria, sem olhar o consumo |
| E-incons | o E-imed com uma fração dos carinhos trocada: alguns depois da fruta errada, alguns antes de comer (D-EL-6) |

A chave do crédito vem ligada em todos os braços. O E0 com a chave desligada é a conferência de que a chave não muda nada sem carinho.

**A fruta X:** sorteada por vida por uma rng própria (`derivar_semente("elogio-fruta", semente)`), uniforme entre as três, como no
`fruta_tapa`. Assim, X às vezes é a fruta de que o pet já gosta pelo paladar (o elogio acelera) e às vezes não (o elogio contra o gosto). As
duas leituras saem separadas, descritivas.

**As medidas:**
- **M1:** as decisões até a fração de X entre as frutas comidas passar de um critério (PROPOSTO: 0,8 numa janela móvel; D-EL-4);
- **M2:** a área sob a curva da fração de X;
- **M3, a retenção:** a fração de X nos dias depois que o elogio para (a segunda metade da vida sem carinho contingente; D-EL-7);
- **M4, a guarda:** o bem-estar (o mesmo da LONGE_GEOMETRIA) e a nutrição, para ver que o elogio não ensina o pet a comer pior.

**O contraste principal:** E-imed − E-sorteado em M2, pareado pela unidade (o mesmo genoma, o mesmo mundo, a mesma semente), com intervalo
por bootstrap. Os secundários: E-imed − E0, E-atraso − E-imed por atraso e E-incons − E-imed.

**As premissas (gates de premissa, antes do contraste):**
- **P0, técnica:** o modular lê a solidão e o estresse, e o `sinal_corpo` do carinho não é 0 (conferido em vidas de teste).
- **P1, a natural:** no E0, a fração da fruta preferida pelo paladar sobe ao longo da vida. Sem isso, não há o que acelerar.

**A calibração:** uma grade de `g` × `W` (D-EL-8), só com as sementes da calibração. O critério de escolha é o menor `g` com
E-imed − E-sorteado > 0 com folga em M2 e sem piora de M4. Depois, a validação **uma vez** nos valores escolhidos, com o plano commitado.

## 5. Entrega

As etapas, cada uma com o sim do Matheus:

1. **Papel (esta):** a tarefa, com D-EL-1 a D-EL-8.
2. **Código:** o gabarito antes; o gancho no modular atrás da chave; o `DonoElogioFruta` e as variantes; os testes (o byte a byte desligado,
   o crédito na janela, o sorteado sem olhar o consumo); a P0.
3. **Plano de análise:** `docs/PLANO_ANALISE_V3_ELOGIO.md`, com a faixa pedida ao coordenador, os números e o sha256 no meta.
4. **Calibração:** a grade, o relato e a escolha de `g` e `W`, levada ao Matheus.
5. **Validação:** uma vez, e o `docs/RESULTADO_V3_ELOGIO.md`.
6. **Web:** só depois da validação, e só se ela passar: o gancho no `web/app/src/cerebro.ts` com paridade.

## 6. Fora desta tarefa

- O banheiro (o "fazer cocô no lugar certo" do pedido): precisa do modular com os receptores dele, numa etapa própria. Depois desta, o
  mesmo desenho serve a ele.
- O tapa no modular: o sinal direto do tapa (CD-10) é outra pergunta.
- O elogio no cérebro A: ele já tem o crédito; esta tarefa não o mede de novo.
- A web, antes da validação.

## 7. Critérios de aceitação

- A tarefa diz o que já existe (o CD-4 no A) e o que falta (o gancho no modular), com os arquivos.
- O controle do mesmo número de carinhos está no desenho como o contraste principal.
- As premissas P0 e P1 vêm antes do contraste.
- As referências são só as verificadas, e o que não tem fonte está marcado.

## 8. Precisa do Matheus

Todas DECIDIDAS pela recomendação: "Aprovo todas" (Matheus, 2026-11-16). Os números da D-EL-4 a D-EL-8 são de desenho; o `g` e o `W`
escolhidos na calibração voltam ao Matheus.

| id | decisão | recomendação | custo de errar |
|---|---|---|---|
| D-EL-1 | a tarefa é a escolha da fruta X no mundo do paladar | sim: o modular já aprende a fruta pelo P1, e o tapa X da V2 dá a forma | baixo: o banheiro, o exemplo do pedido, fica para depois |
| D-EL-2 | a rota do sinal no modular | as duas juntas: o `r` da opção (P2 e afeto) e o desfecho da classe consumida (P1). Só o `r` não ensina qual fruta, porque o hábito do P2 é por comportamento (`comer`), não por fruta | médio: pela rota do P1, o pet passa a "esperar" do X o conforto do carinho, o que é o próprio aprendizado pedido, mas mistura o dono com a fruta no desfecho. A divisão sai descritiva no motivo |
| D-EL-3 | a forma da janela | a linear da v1, a mesma do A | baixo: outra forma é um braço depois |
| D-EL-4 | o critério de M1 | 0,8 da fração de X numa janela de 10 frutas comidas | baixo: a M2 é a principal e não depende dele |
| D-EL-5 | os atrasos do E-atraso | três: 1, 3 e 6 passos do dono | baixo: descritivo |
| D-EL-6 | o dono inconsistente | 20 % dos carinhos depois de outra fruta e 10 % antes de comer | baixo: descritivo |
| D-EL-7 | a retenção | o elogio contingente só na primeira metade da vida; M3 na segunda | médio: vidas mais longas custam tempo de máquina |
| D-EL-8 | a grade | `g` em {S/4, S/2, S, 2S} × `W` em {1, 2, 4} passos | médio: uma grade grande custa vidas na calibração |

## 9. Etapa 2: o que a leitura do código mudou (2026-11-17)

**D-EL-9 a D-EL-13 DECIDIDAS** pela recomendação: "Aprovo todas" (Matheus, 2026-11-17).

A etapa 2 começou ("Comece a etapa 2 do elogio", Matheus, 2026-11-17) e parou antes do código. Três achados da leitura e de duas vidas de
sonda (sementes 101 e 202 dos testes, fora de qualquer faixa; nenhum número daqui vai a resultado):

1. **O P0 passa.** Com o corpo da etapa 6 (`CONFIG_CORPO_DRIVES`, com `gestos`), o modular tem os receptores `solidao` e `estresse`, e o
   `sinal_corpo` do carinho, com os drives e o `ganho_r` do M-AFETO, fica perto de 200 (a solidão cai de 77 a 108 para 0). O carinho
   mexe no que o modular lê.
2. **O mundo do paladar não roda com o modular.** O M-SENS recusa os receptores do paladar (`sens.py`, `_receptores`: "receptores fora
   do protótipo (os órgãos, o paladar, o banheiro)"). O modular nunca aprendeu fruta pelo paladar. Sem o paladar, no mundo com as árvores
   (`CONFIG_MUNDO_LIGADA`) e a condição `iguais`, as três frutas têm o mesmo efeito (0 no humor), e o pet comeu 14 e 2 frutas em 6 dias,
   quase sempre a ração. A P1 (a consequência natural ensina uma fruta) não teria o que mostrar, e o M1 (10 frutas comidas) mal fecha.
3. **O mundo físico da bancada não aceita os gestos do dono** (`nucleo.py`, `vida`: "os gestos do dono ficam fora do mundo físico"). O
   caminho que existe é o `carinho` do `simular_vida_fisico`, o do banheiro (BN-2): fora do orçamento, como contato.

E três detalhes do mecanismo que a seção 3 deixava abertos, porque o modular fecha a decisão só no começo da decisão seguinte e o passo do
dono é igual ao intervalo da decisão (15 ticks): o carinho do primeiro passo depois de comer cai sempre um passo depois da decisão.

| id | decisão | recomendação | custo de errar |
|---|---|---|---|
| D-EL-9 | o cenário no lugar do mundo do paladar | o mundo físico com as árvores e a condição `casado` (o efeito de cada fruta no humor pela preferência inata do genoma), com vidas de 12 dias, para o pet comer frutas bastante. A alternativa é dar ao modular os receptores do paladar antes, numa tarefa própria | médio: com o `casado` a fruta X boa é a preferida do genoma; a leitura "X a favor do gosto" e "X contra" continua, pelo genoma |
| D-EL-10 | o carinho na bancada | o gancho `carinho` do `simular_vida_fisico`, fora do orçamento, como o do banheiro; o E-sorteado tem o mesmo número de carinhos, então a comparação não muda | baixo: o "dentro do orçamento" da seção 3 vira "fora", igual nos braços |
| D-EL-11 | a janela | W em decisões: o carinho credita a decisão j passos para trás (j = 0 é a última), com o peso `S − div_arred(j × S, W)` para j < W. Com W = 1, só a última | médio: em ticks, o carinho de um passo depois teria peso 0 com W = 1 |
| D-EL-12 | a rota (detalhe da D-EL-2) | no carinho, na hora: o P2 da linha do comportamento da decisão (com o `z` e o `g_apr` dela, r = o sinal pesado) e, se ela comeu uma classe, o desfecho dessa classe anda pelo que o carinho mudou nos receptores, somado (não puxado para o alvo, que apagaria o que a fruta ensinou). A valência do M-AFETO não recebe | médio: sem a valência, o carinho não muda o humor do cérebro, só o que ele aprende |
| D-EL-13 | a ordem | o gabarito e o código só depois destas decisões | baixo |

## 10. Etapa 2: o código (2026-11-17)

- **O gabarito** (commit próprio, antes do código): `tests/gabarito_elogio.py` e `tests/gabaritos/elogio_de_hoje.json`, 12 vidas do
  modular (o braço REL) com o carinho pelo corpo: o mundo `casado` e o do laboratório, sem carinho, um a cada 4 passos e um depois de cada
  fruta, sementes 101 e 202. O `tests/test_gabarito_elogio.py` confere o byte a byte.
- **A chave:** `ConfigElogio` (`digilab/config.py`; `ligada`, `ganho` = S e `janela` = 1, PROPOSTOS e SEM FONTE; status em
  `PARAMETROS_ELOGIO`). Fica fora da `ConfigDigibrain` para o dump do modular não mudar (D-EL-14).
- **O gancho:** `DigiBrain(cfg_elogio=...)`. Com a chave ligada, o cérebro ganha o `mudanca_no_corpo`; desligada, não o tem, e o motor não
  o chama. O sinal e as duas rotas são os da seção 3 com a D-EL-11 e a D-EL-12; o P1 do carinho é o `Plasticidade.elogio_p1` (soma, não
  puxa). O registro fica em `elogios` e no estado interno (`elogio`).
- **Os braços:** `experiments/elogio.py`, com o `DonoElogioFruta` (E-imed, E-atraso, E-sorteado, E-incons; o E0 sem carinho), a fruta X
  (`elogio-fruta`), o par E-imed × E-sorteado (`viver_par`) e o contingente só na primeira metade. Sem métricas: elas entram no
  `digilab/metrics.py` com o plano (etapa 3).
- **Os testes:** `tests/test_elogio.py` (a config, o gancho só com a chave, o P0, a janela e o peso, a decisão que comeu X, o ganho 0, o
  sorteado sem olhar o consumo, o par, a metade, os atrasos, as falhas altas e o replay com a chave ligada).
- **O P0 passa** nas vidas dos testes: o modular lê a solidão e o estresse, e todo carinho dá sinal diferente de 0.
- **Para a etapa 3:** nas vidas de 6 dias dos testes, o pet comeu a fruta X de 1 a 17 vezes. Os 12 dias da D-EL-9 e o critério do M1 (10
  frutas) precisam ser conferidos no plano, antes da faixa.

## 11. Etapa 3: o plano de análise (2026-11-17)

O plano é o [PLANO_ANALISE_V3_ELOGIO.md](PLANO_ANALISE_V3_ELOGIO.md), PROPOSTO e parado no CHECKPOINT EL-3. Uma sonda nas sementes dos
testes (`experiments/sonda_elogio_plano.py`) decidiu o desenho:
- os 12 dias da D-EL-9 bastam para a M2;
- 36 dias diluem o efeito;
- o M1 quase não fecha e vira descritivo;
- a premissa P1 (a natural) não aparece na escolha da fruta.

A faixa proposta é 25101 a 25505. As medidas entram no `digilab/metrics.py`, e a faixa no `faixas.py`, depois do sim às D-EL-18 a D-EL-24.
