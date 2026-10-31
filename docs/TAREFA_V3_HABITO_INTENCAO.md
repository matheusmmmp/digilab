# TAREFA V3 — HABITO_INTENCAO: o hábito com o crédito na corrida do comportamento, contra o crédito no passo (2026-10-31)

Coordenador: Gerente da V3 (Claude Code). Worker da etapa 1: Claude Code, Opus 5.5 (método), worktree `v3-habito-intencao`. Worktree e
branch: `v3-habito-intencao` (as etapas seguintes, um sufixo por etapa, como `v3-habito-intencao-codigo`). Status: **ABERTA; etapa 1 (só papel) ENTREGUE; as
HI-1 a HI-8 (seção 8) DECIDIDAS em 2026-10-31, pela recomendação.** Nenhum código, nenhuma faixa e nenhuma vida.

Categoria: implementacao (depois, experimento). Origem: Matheus, 2026-10-31: a D-C1-2: depois da C1 (#510), a próxima do cérebro é a C2, o
hábito com crédito na intenção, em separado.

## 0. Os cinco pontos

1. **A pergunta:** o G-ABLA-P2 saiu ao contrário nas três runs do protótipo (M2 − M1 = −0,018 [−0,022; −0,013] na reavaliação). Isso
   acontece porque o P2 credita o passo?
2. **O que se testa:** um braço novo, o M2 com o crédito do P2 na **corrida do comportamento** (as decisões seguidas do mesmo
   comportamento, entregues ao P2 uma vez só, quando a corrida acaba), contra o M2 de hoje e o M1 (sem P2).
3. **O cenário:** o que a C1 deixa: o `longe_fixo` e o comedouro, sem o M-MEM nos três braços.
4. **A fonte:** só Gadanho e Hallam (2001), verificada na C0 e lida pela tese de 1999 (seção 1.2). Ela sugere a direção, não o tamanho.
   O resto é SEM FONTE. **Nenhuma alegação de novidade.**
5. **Esta etapa é só papel.** O código, o plano e a run vêm depois, cada um com o sim do Matheus (seção 5).

## 1. Pergunta

**O hábito (o P2) sai ao contrário porque o crédito cai no passo?** O teste é um braço com a atualização do P2 na corrida do comportamento,
a forma da "opção composta" que cabe aqui sem o gatilho da C3 (seção 1.3), contra o braço com a atualização no passo, que é a de hoje. É a
R2 da triagem (`docs/referencias/V3C0_SINTESE_TRIAGEM_2026-10-30.md`, seção 4) e a linha da C2 do `docs/PLANO_V3.md` (seção 2). Vem da
pergunta da trilha C do plano: os mecanismos que a triagem aponta explicam ou corrigem as falhas do modular no hábito, quando cada um é
testado com controle?

### 1.1 O que o projeto já sabe (os dados)

- **O hábito ao contrário, nas três runs** (`docs/RESULTADO_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md`, 9.2). O índice "ganhou, fica"
  (`digilab/metrics.py`, `repeticao_apos_alivio`, dias 8 a 14), M2 − M1:
  - **o total:** −0,011 no #420, −0,012 no piloto do conserto, −0,018 na reavaliação;
  - **no comedouro:** +0,008, 0,000 e −0,004;
  - **no longe:** −0,046, −0,038 e −0,045.
  - **Por ação,** na reavaliação, só os pares que começam numa ação com r possível (a DX-5):
    - no longe, o explorar dá M1 0,056, M2 −0,021, M2 − M1 −0,077;
    - o comer fica perto de 0 no comedouro (+0,002) e no longe (−0,004), e positivo no perto (+0,047).
- **O crédito de hoje já é por opção, mas a opção é o passo.** O código do PE-3 (`digilab/digibrain/estado.py`, a docstring e o
  `consequencia`; `digilab/digibrain/plast.py`, `creditar`) guarda o z da decisão que começou a opção, soma o r_n de cada consequência e
  entrega tudo ao P2 quando a opção acaba. Só as intenções duram mais de uma decisão. O replay do piloto mostrou o resultado
  (`docs/RESULTADO_V2_DIGIBRAIN_MODULAR_DIAGNOSTICO.md`, 3.2):
  - o `explorar/vagar` e o `explorar/cheiro` têm 1,00 decisão por opção nos três lugares;
  - no longe, só 21 das 871 opções `comer/comida` do M2 duram mais de uma decisão.
  - **Por isso, nesta tarefa, "o crédito no passo" é o crédito de hoje.** A interpretação está no registro (seção 5).
- **Onde o hábito decide:** no longe, a sonda do M2 (dias 8 a 14) achou 1 804 decisões mudadas no explorar e 424 no comer. No fim da vida,
  a linha do H do explorar é a maior no longe, com o viés em 171 (o mesmo diagnóstico, 3.1). O r positivo do explorar não vem da refeição:
  o explorar come em 0 a 2 % das decisões (3.2).
- **A C1 não mediu o P2:** os braços foram M0, M2 e M3\*, sem o M1 (`docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md`, A6.2). Ela
  deixa:
  - o `longe_fixo`, com o código, o gabarito e o orquestrador na `main`;
  - a G-PESA do hábito ao lado: 0,120 no M2 do `longe_fixo` e 0,111 no longe (o mesmo RESULTADO, 13.4, item 5);
  - o M2 − M0 por episódio, que é negativo nos dois estilos: −0,025 [−0,039; −0,011] no `longe_fixo` (13.4, item 5).

### 1.2 O que a literatura sugere (só a C0 verificada)

- **Gadanho e Hallam (2001), *Adaptive Behavior* 9(1), `10.1177/105971230200900102`,** VERIFICADA na C0
  (`docs/referencias/v3c0_referencias_verificadas.csv`). O que a linha sustenta:
  - o resumo do Crossref: um robô simulado numa tarefa de energia, com um modelo de emoção em três papéis dentro de um aprendizado por
    reforço (a percepção, o reforço e quando reavaliar a decisão);
  - pela triagem, lido pela tese de 1999 (a versão-irmã, não o artigo): **a recompensa emocional falha por ação primitiva e funciona por
    comportamento;** o gatilho de reavaliação explica a maior parte do ganho.
- **O que isso autoriza:** a direção da hipótese da C2. Creditar uma unidade maior que o passo pode fazer o reforço funcionar onde ele
  falha por passo. **Não autoriza** o tamanho do efeito, nem que o efeito apareça sem o gatilho. Os números da tese não são citados aqui:
  para citar um, ler o artigo (a ressalva da C0, seção 6).
- **A ressalva que pesa:** na fonte, o gatilho (a C3) explica a maior parte do ganho, e a duração do comportamento vinha dele. A C2 testa
  só a outra metade, o crédito, com a decisão a cada passo como hoje. Um resultado nulo aqui não contradiz a fonte.
- **Fora disso, SEM FONTE:**
  - a corrida do comportamento como unidade;
  - as variantes da HI-3;
  - as premissas e todos os números novos.
- **Nenhuma alegação de novidade** (a regra 9 de `docs/referencias/REGRAS_CITACAO_DIGILAB.md`). A combinação "corpo, aprendizado em vida
  e hábito" já foi publicada (a C0, conclusão 1).

### 1.3 Em que a C2 é diferente da DX-6 recusada

**Como a DX-6 caiu.** A proposta do diagnóstico (`docs/PROPOSTA_DIAGNOSTICO_DIGIBRAIN_MODULAR.md`, 1.4 e a tabela da seção 2) escreveu a
H-P2b: a opção longa somaria o custo da caminhada e a refeição num r_n só, creditado com o z do começo, e esse z ficaria longe do contexto
do alívio. A DX-6 era o conserto: creditar o P2 só com o z e o r da **última** consequência da opção, ou seja, **encurtar** o crédito.
- O replay do piloto mostrou que as opções duram uma decisão (1.1). A opção longa da H-P2b não existe, e a H-P2b não se sustentou como
  escrita (o diagnóstico, seções 3.2 e 4).
- O adendo 3 deixou a DX-6 fora (`docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md`, A3.0 e A3.6): "O diagnóstico mostrou opções de
  uma decisão".

**A C2 vai no sentido oposto, e por isso é outra hipótese:**
- **a DX-6 supunha** um crédito largo demais e o encurtava;
- **a C2 parte do mesmo dado que derrubou a DX-6,** as opções de uma decisão, e pergunta se o problema é justamente o crédito curto
  demais. Ela o **alarga** para a corrida do comportamento;
- **a C2 tem fonte verificada** para a direção: Gadanho e Hallam, pela tese, "falha por ação primitiva, funciona por comportamento". A
  DX-6 não tinha fonte nenhuma;
- **o que fica igual:** as duas mexem só na entrega ao P2, sem tocar a decisão, a intenção, a persistência nem o F.

**O que a C2 não reabre:** a H-P2b como escrita. Ela continua não sustentada.

### 1.4 O que cada resultado diria (escrito antes; a forma final vai no plano)

O primário é o P-A (seção 4.3): o índice de hoje, M2c − M2. O secundário S1 é o M2c − M1, o G-ABLA-P2 refeito com o crédito novo. A
classe de cada um ("> 0", "≈ 0", "< 0", "indeterminado") segue a regra da A6.6: o IC95 contra 0 e a margem δ do plano.

| P-A (M2c − M2) | S1 (M2c − M1) | o que diria | o que se faz |
|---|---|---|---|
| > 0 | > 0 | nestas condições, o crédito no passo explica a falha: com a corrida, o hábito faz o que se previa | a corrida vira candidata a substituir o crédito de hoje; volta ao Matheus. Não vai ao jogo sem a L3 |
| > 0 | ≈ 0, < 0 ou indeterminado | o crédito no passo explica parte da falha, mas o hábito ainda não sobe o "ganhou, fica" acima do sem-hábito | registrado; a C3 (o gatilho, a outra metade da fonte) fica como o próximo teste, em separado |
| ≈ 0 | qualquer | nestas condições, a unidade de crédito não é a causa. Fica a H-P2a: o índice mede a sensibilidade ao resultado, e um hábito é justamente a repetição pouco sensível | volta ao Matheus a medida do P2, não um mecanismo novo |
| < 0 | qualquer | a corrida piora o índice | registrado como está; a corrida fica fora |
| indeterminado | qualquer | nada se decide | registrado como indeterminado |
| qualquer, com a premissa P-CORRIDA falhando | — | inconclusivo por premissa: a corrida não ficou mais longa que o passo | registrado; nada se decide |

- **A previsão de sinal (PROPOSTA): P-A > 0.** A direção vem da fonte; o tamanho, de nada.
- **A previsão não se afrouxa até passar.** Se sair ≈ 0 ou < 0, fica registrado assim.
- **O S2, o M2 − M1 do cenário novo,** é a réplica do G-ABLA-P2 no `longe_fixo` e no comedouro. Ele sai sem previsão de sinal: no
  comedouro, as três runs deram de +0,008 a −0,004; no `longe_fixo`, nunca foi medido.

## 2. Depende de

- **Na `main`:** a C1 inteira (#495, #497, #503, #506, #507, #508, #510): o `longe_fixo`, o seu gabarito, o orquestrador do adendo 6 e as
  medidas da C5. Ela está lá (`5ecf5d9`).
- **Decisões que precisam existir:**
  - a D-C1-2 (o Matheus, 2026-10-31): a C2 em separado, sem combinar mecanismos;
  - as HI-1 a HI-8 desta tarefa (seção 8), antes da etapa 2.
- **Do Gerente:** a faixa de sementes (HI-6), conferida e posta na `FAIXAS_RESERVADAS` num commit próprio, antes da run.

## 3. Mudança mínima (etapa 2, código; nada nesta etapa)

### 3.1 O que muda

- **Uma subchave nova, `credito_corrida`,** em `ConfigDigibrain` (`digilab/config.py`), `False` por padrão, PROPOSTA, SEM FONTE como
  valor (a direção vem de Gadanho e Hallam). Entra também na lista do `__post_init__`, que confere o tipo.
- **A regra, só no M-ESTADO** (`digilab/digibrain/estado.py`), PROPOSTA:
  - **a corrida:** as decisões seguidas cujo comportamento é o mesmo (o `chave[0]`: comer, brincar, explorar, dormir...), qualquer que
    seja o alvo. Uma intenção, uma busca pelo cheiro e uma opção composta da DX-4 do mesmo comportamento ficam dentro da mesma corrida;
  - **a elegibilidade:** o z da primeira decisão da corrida;
  - **o r:** a soma dos r_n de todas as consequências da corrida, cortada em [−S, S], como o `op["r"]` de hoje;
  - **o g_apr:** o da última decisão;
  - **a entrega ao P2:** uma vez, na primeira decisão de outro comportamento. As intenções, o C, o F, os fins e a persistência seguem como
    hoje; só deixam de entregar ao P2 cada uma por si;
  - **o fim da vida:** a corrida aberta recebe o mesmo tratamento que a opção aberta de hoje recebe no fim. A espec da etapa 2 lê o código
    e fixa isso por teste;
  - **o reflexo do sono:** é uma decisão de `dormir`, então fecha a corrida em curso como qualquer troca de comportamento. A
    `intencao_suspensa` fica desligada (a LP-3), e a C2 não a combina.
- **O M-PLAST não muda:** o `creditar` recebe a corrida no mesmo formato do dicionário de hoje (`chave`, `e`, `r`, `g_apr`).
- **O `eta_h`, o `h_max` e os inatos do #428 não mudam** (HI-7). Com menos créditos por vida e r somados, o H pode chegar a outro tamanho;
  isso entra como descritivo (seção 4.4), não como calibração.
- **A medida, se a HI-5 pedir o índice por opção:** em `digilab/metrics.py`, ao lado do `repeticao_apos_alivio`, sem mudar a de hoje.
- **O braço `M2c`:** `{"m_mem": False, "cheiro_inato": True, "intencao_cheiro": True, "credito_corrida": True}`, ao lado do
  `SUBCHAVES_CONSERTO` (`experiments/run_v2_digibrain_prototipo.py`). O M1 e o M2 são os do conserto, sem mudança.

### 3.2 Os testes, antes de qualquer vida (com as sementes 101…505)

| teste | o que confere |
|---|---|
| **o gabarito antes** | um commit próprio, antes da mudança, grava as vidas de hoje do M1 e do M2 no `longe_fixo` e no comedouro. O gabarito do protótipo, o do MVP e o da C1 já estão commitados; o novo só entra se faltar uma dessas células |
| **G2** | com a `credito_corrida` desligada, as vidas do gabarito do protótipo, do MVP e da C1 saem byte a byte |
| **G2-SEPARADO** | a subchave ligada muda só as vidas do braço que a liga; fora do pacote `digibrain` e do orquestrador, nada a lê (o teste de hoje, estendido) |
| **G1** | o replay refaz cada vida com a subchave ligada |
| **T-CORRIDA-1** | uma sequência sintética explorar, explorar, explorar, comer: com a subchave, um crédito do explorar (o z da 1.ª decisão, a soma dos três r_n), depois o do comer; sem ela, três créditos de uma decisão, como hoje |
| **T-CORRIDA-2** | uma intenção `comer/comida` e uma busca `comer/cheiro` seguidas dentro de uma corrida de comer: um crédito só. Os fins, o C e o F são os mesmos de sem a subchave |
| **T-CORRIDA-3** | o reflexo do sono fecha a corrida; o fim da vida trata a corrida aberta como a espec fixar |
| **o `conferir_credito` do orquestrador** | estendido para a corrida, e falha alto em toda vida, como hoje |
| **G-MECANISMO, G-INT, G-SEM-DIRECAO, G-RECEPTOR** | os de hoje passam com a subchave ligada |

### 3.3 O que NÃO muda

- **O motor:** o `engine.py`, o mundo, o corpo, o cheiro, o `longe_fixo`, o A, a v12 e o jogo web.
- **No cérebro:** a decisão a cada passo (o gatilho é a C3), o M-MEM e o P1.
- **Os resultados anteriores:** o #420, a reavaliação, a L-2 e a C1 ficam como estão. Nenhuma faixa gasta (64xxx, 66xxx, 67xxx, 71xxx)
  volta.

## 4. Experimento e gate (etapas 3 e 4; PROPOSTO, tudo com o Matheus)

### 4.1 O plano e as sementes

- **O plano de análise:** um adendo 7 ao `docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md` (HI-8), commitado e APROVADO antes da
  primeira vida.
- **As sementes:** uma faixa nova pedida ao Gerente (HI-6). Sem calibração e sem piloto: a variância vem das vidas já gravadas (4.5).
- **GPU:** não.

### 4.2 O desenho

- **O cenário:** o da C1 (A6.2), sem mudança: o `CONFIG_MUNDO_MVP`, o corpo do v11, o pet sozinho, os quatro donos sem ensino, 14 dias,
  o orçamento de 16 por dia, a morte desligada.
- **Os lugares (HI-2):** o `longe_fixo` e o comedouro, os dois no primário. O longe sorteado entra só como descritivo.
- **As células:** 4 donos × 3 lugares = 12 por unidade.
- **Os braços (HI-1):** M1, M2 e M2c. São 36 vidas por unidade.
- **O pareamento:** por unidade e célula. A mesma semente, o mesmo genoma, o mesmo dono e o mesmo lugar nos três; só a subchave muda.

### 4.3 O primário e as secundárias

- **O primário P-A (HI-4):** o índice de hoje (`repeticao_apos_alivio`, dias 8 a 14), M2c − M2, a média das 8 células do `longe_fixo` e
  do comedouro por unidade, com o IC95 do t sobre as unidades (A4.4.6) e a previsão > 0.
- **A margem δ e o "≈ 0":** pela regra da A6.6, com o δ tirado do poder (4.5).
- **As premissas, PROPOSTAS e SEM FONTE:**
  - **P-CORRIDA:** no M2c, a corrida creditada dura em média mais de 1,1 decisão. Se não durar, a corrida não difere do passo, e o
    primário é inconclusivo por premissa;
  - **G-PESA do hábito:** no M2c, a fração das decisões que o hábito mudou é ≥ 0,01, como as G-PESA do adendo 6.
- **As secundárias** (pré-registradas, com o IC, sem gate):
  - **S1:** M2c − M1, o G-ABLA-P2 refeito com o crédito novo; previsão > 0;
  - **S2:** M2 − M1, a réplica no cenário novo; sem previsão de sinal (1.4).

### 4.4 Os descritivos (sem gate; nenhum muda a leitura de 1.4)

- **O índice "ganhou, fica":**
  - o da DX-5 (só as ações com r possível) e o índice por ação (comer e explorar), por lugar;
  - o índice no longe sorteado, onde o G-ABLA-P2 falhou;
  - o índice por opção creditada, se a HI-5 o pedir.
- **As corridas e o H:**
  - o comprimento das corridas creditadas, por comportamento;
  - os créditos por vida, o H no teto (o `no_teto`) e a norma do H no fim, por comportamento;
  - a G-PESA do hábito por braço.
- **O corpo:** a taxa por episódio (a do adendo 6) e as medidas da C5, para ver se o hábito com a corrida ajuda ou atrapalha o pet. O
  M2 − M0 da C1 já é negativo (1.1).
- **A LP-2:** os subgrupos que a própria corrida cria saem só por braço, não como contraste.

### 4.5 O tamanho (PROPOSTO; a conta vai no plano)

- **O ponto de partida:** K = 10 por base, 50 unidades, como a reavaliação (A4.4.6). Dá 1 800 vidas.
- **A conta do poder:** num script só de leitura, como o `experiments/adendo6_poder_longe_regular.py`, sobre o `medidas.json` da
  reavaliação (66xxx), com o dp do G-ABLA-P2 nas células comuns. O δ e o K finais saem dele. Nenhum número de poder é escrito aqui sem
  esse artefato.
- **A máquina (V3-D8):** 4 processos e uma run por vez. Pela C1, 3 600 vidas levaram 64 minutos com 4 processos (o RESULTADO, 13).

## 5. Entrega

### 5.1 Esta etapa (a etapa 1, só papel)

- **Esta tarefa,** preenchida.
- **O registro da interpretação:** "o crédito no passo é o crédito de hoje" (1.1), numa seção no fim de `docs/registro/2026-10.md`, com
  uma linha no fim de `docs/REGISTRO_DESVIOS.md`.
- **O PR contra a `main`,** no modelo `.github/pull_request_template.md`.
- **A conferência:** `python tools/conferir_saude.py` e o `tools/verificar_relato.py`.
- **Nenhum código, nenhuma faixa e nenhuma vida.**

### 5.2 As etapas seguintes, cada uma num PR e com o sim do Matheus

| etapa | o quê | categoria |
|---|---|---|
| **2** | a espec curta da corrida, o gabarito antes, a subchave e os testes da seção 3.2 | implementacao |
| **3** | o adendo 7, com o script do poder, a faixa na `FAIXAS_RESERVADAS` e o orquestrador | implementacao |
| **4** | a run, uma vez, e a leitura pela tabela de 1.4 | experimento |

- **Os testes:** `python -m pytest tests/ -q` em cada etapa de código, com a contagem no PR.
- **O resumo de cada etapa:** no corpo do PR e numa seção no fim desta tarefa (a run, num `RESULTADO`, conforme a HI-8). Nunca no
  `CLAUDE.md`.

## 6. Fora desta tarefa

- **Os outros mecanismos:**
  - a C3 (redecidir por evento), a C4 (a memória que decide) e a L-3;
  - qualquer combinação da corrida com o M-MEM, com o gatilho ou com a `intencao_suspensa` (a D-C1-2);
  - a D-C1-3 (as visitas ao lugar lembrado que não acham ração).
- **O que não se mexe:** o retorno zero do dormir e do chamar a atenção (a questão aberta do A3.6); a medida do hábito de hoje (o S2 e o
  P-A a usam como está).
- **Fora de escopo:** o A11 e qualquer leitura de superioridade sobre o A; o jogo web (a L3 só depois da C1 e da C2 e do sim do
  Matheus).

## 7. Critérios de aceitação

**Da etapa 1:**
- este arquivo existe na `main` depois do merge, sem nenhum marcador do modelo por preencher;
- as HI-1 a HI-8 têm recomendação e custo de errar;
- o registro e a linha do índice existem, com o mesmo título;
- `python tools/conferir_saude.py` sai com 0;
- o corpo do PR passa no `tools/verificar_relato.py --base origin/main`.

**Das seguintes:**
- o G2 byte a byte com a subchave desligada;
- os T-CORRIDA-1 a 3 passando;
- o adendo 7 APROVADO antes da primeira vida;
- toda vida rejogada bit a bit;
- cada número do resultado com o artefato.

## 8. Decisões do Matheus

**Todas DECIDIDAS em 2026-10-31, pela recomendação** ("Sim, siga as recomendações", no chat do Gerente da V3). A faixa
75101…75505 foi conferida livre pelo Gerente (a `main` e todos os branches remotos) e entra na `FAIXAS_RESERVADAS` num commit próprio, na
etapa 3. Os números novos seguem PROPOSTOS e SEM FONTE. A direção da HI-3 vem de Gadanho e Hallam, pela tese.

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| **HI-1** (DECIDIDA) | os braços | **M1, M2 e M2c,** todos sem o M-MEM, com as duas subchaves do cheiro (as do conserto) e a `intencao_suspensa` desligada. O M2 é o controle do primário, e o M1, o do S1 | sem o M1: o S1 não sai, e não se sabe se o hábito chega a ajudar; com o M-MEM (um M3\*c): a corrida se mistura com a memória, a combinação que a D-C1-2 proíbe sem plano próprio; com o M0: mais vidas sem pergunta |
| **HI-2** (DECIDIDA) | o cenário | **o `longe_fixo` e o comedouro no primário** (8 células), o que a C1 deixa; o longe sorteado só descritivo (mais 4 células) | só o sorteado: o hábito é testado onde a repetição não deveria pagar, e o nulo não distingue as hipóteses; sem o sorteado: não se vê se a corrida desfaz a falha onde ela mora (−0,045), e com o sorteado são 50 % a mais de vidas (de 8 para 12 células); com o perto: mais vidas, e o perto não é da C1 |
| **HI-3** (DECIDIDA) | a unidade de crédito | **a corrida do comportamento** (3.1). É a leitura mais literal de "por comportamento" sem o gatilho, e a menor mudança: só a entrega ao P2. As alternativas: (b) a opção composta por meta, uma corrida explorar → comer que acaba comendo credita o explorar com a refeição; (c) uma janela de K decisões. As duas são SEM FONTE | a (b) mira o explorar do longe direto, mas é uma regra feita para o caso e mistura comportamentos no mesmo crédito: se der > 0, não se sabe se foi a unidade ou a regra; a (c) põe um K novo sem fonte. Com a corrida, um nulo pode vir de corridas curtas, e a P-CORRIDA protege disso |
| **HI-4** (DECIDIDA) | o primário | **o P-A: o índice de hoje, M2c − M2, nas 8 células,** previsão > 0; o S1 (M2c − M1) e o S2 (M2 − M1) secundários | o S1 como primário mede se o hábito passa, não se o crédito é a causa, e falha também se a corrida ajudar só em parte; os dois como primários: o Holm come o poder |
| **HI-5** (DECIDIDA) | a medida do primário | **o índice de hoje** (a falha foi definida por ele, no G-ABLA-P2), com o índice por opção creditada e o da DX-5 como descritivos | o índice de hoje olha o r do passo, e a corrida credita a corrida: se o efeito for só no nível da corrida, o P-A pode sair ≈ 0 por medida (a H-P2a de novo). O índice por opção como primário é medida nova, com um nome e um código novos antes da run |
| **HI-6** (DECIDIDA) | a faixa de sementes, a pedir ao Gerente | **75101…75505,** com as bases 75101, 75202, 75303, 75404 e 75505. Ela não aparece no `experiments/bancada/faixas.py`, nas `experiments/configs/` nem no `docs/PLANO_V3.md` da `origin/main` e dos branches remotos (a busca de 2026-10-31). O Gerente confere e a põe na `FAIXAS_RESERVADAS` num commit próprio | uma faixa já usada (a 66xxx, a 71xxx) faz a validação deixar de ser única; uma faixa que outra frente pegue no mesmo dia dá colisão, que a `unidades_derivadas` pega alto, mas que custa refazer |
| **HI-7** (DECIDIDA) | calibrar o `eta_h` para o M2c | **não:** os inatos do #428 nos três braços, e o tamanho do H vai aos descritivos. A calibração fica para o fim (a decisão de 2026-10-13) | calibrar só o M2c dá a ele um ajuste que o M2 não teve, e o contraste deixa de ser só a unidade; não calibrar pode dar um nulo por H pequeno ou saturado, e por isso o H no teto e a norma saem ao lado |
| **HI-8** (DECIDIDA) | onde fica o plano | **um adendo 7 ao `PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md`.** O resultado fica numa seção nova do `docs/RESULTADO_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md`, como a C1 (a LR-7). Os braços, o episódio, a unidade, a A6.6 e o orquestrador já estão lá | um `PLANO_ANALISE_V3_HABITO_INTENCAO.md` novo repete as definições e pode divergir delas, e o orquestrador do protótipo teria de ler outro arquivo; o custo do adendo é só o tamanho do plano. (O `PLANO_ANALISE_V3.md` que existe é da v1, o glossário do `PLANO_V3`, seção 8) |

## Resultado da etapa 1 (só papel; 2026-10-31, worker Claude Code, Opus 5.5, worktree `v3-habito-intencao`)

- **Esta tarefa,** com:
  - a pergunta, o que a C1 deixa, a mudança mínima com o gabarito antes;
  - os braços, as medidas e a tabela de leitura escritos antes;
  - a diferença para a DX-6 (1.3) e as HI-1 a HI-8.
- **A fonte:** só Gadanho e Hallam (2001), da C0, pela tese; o resto SEM FONTE.
- **Nenhum código, nenhuma faixa e nenhuma vida.**
- **O registro:** a interpretação do "crédito no passo" em `docs/registro/2026-10.md`.
