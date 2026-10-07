# Plano do porte do cérebro A para a web: pets v11 (2026-10-07)

Tarefa `docs/TAREFA_V2_W_PLANO_PORTE.md`, etapa W do `docs/ROADMAP_V2.md`. Rodada 15. **Só papel: nenhum código foi escrito para este
plano.**

**Ponto de partida, M6 (2026-10-07):** o DigiBrain da web é o cérebro A, os lobos (`digilab/policies/lobos.py`).
- Pela regra registrada seria o C. O A foi escolhido por evidência descritiva posterior: `docs/DESCRITIVO_V2_PLATO.md` e o
  `REGISTRO_DESVIOS` de 2026-10-07.
- Este plano não reabre essa escolha.

**Leituras de base:**
- `CLAUDE.md`: as seções da web (TAREFA_FRONT_TS, pets v1 a v10), do vínculo B e da V2 (L0, L1, N3, LOBOS-MUNDO, K2);
- `docs/TAREFA_FRONT_TS.md`;
- `docs/RESULTADO_V2_VALIDACAO_UNICA.md`;
- `docs/DESCRITIVO_V2_PLATO.md`.

**Do código da web, o que importa aqui:**
- `web/app/motor/bandit.ts`;
- `motor.ts`;
- `carater.ts`;
- `motivo.ts`;
- `test/vinculo.test.ts`;
- `src/falaLivre.ts`.

---

## 0. O que o bandit faz hoje no jogo

O bandit da v1 (`bandit.ts`) não é só a escolha da ação. O porte tem de dizer o que acontece com cada uma das funções abaixo no v11:

| função | onde | quem a usa |
|---|---|---|
| decidir a ação (`agir`, Thompson + prior do instinto) | `Bandit.agir` | `Motor`, a cada decisão |
| aprender com o dono (elogio, bronca, chamado atendido ou ignorado) | `receberAcaoDono`, `expirar` | `Motor` |
| escala da recompensa pelo **temperamento** (curiosidade, sensibilidade, teimosia, rancor) | `Bandit.k`, `MemoriaEspacos` | pets v2+ |
| **memória por espaços** e emoção, como features | `Bandit.mem`, `fx` | decisão, motivo, fala livre (`falaLivre.ts` lê `m.pol.mem`) |
| **desejo / vontade** (a ação de maior θ·x, com margem) | `Bandit.desejo` | vínculo, tela do Pet, voz |
| **caráter** pelo desvio da política, que decide a **linha e a forma adulta** | `carater.ts` (`caraterPolitica`, pets v3+) | evolução |
| gostos da história (desvio por ação) | `carater.desvioPorAcao` | voz própria (v7+) |
| distribuição média (θ) | `Bandit.media` | Cenários (pets v5, que não mudam) |
| motivo da decisão | `Bandit.ultDecisao` → `motivo.ts` | fala sob a tela, Aprendizado |
| assinatura | `Bandit.assinatura` | replay, paridade |

O cérebro A da pesquisa (`PoliticaLobos`) cobre a decisão, o aprendizado, o motivo e a assinatura. Não tem:
- temperamento no aprendizado;
- vontade;
- memória por espaços como entrada.

O lobo de memória e emoção da L0 só conta, com contribuição zero. As linhas sem par estão na seção 1.4 e nas decisões da seção 8.

---

## 1. O que entra nos pets v11 agora

**Ponto do aprendiz:** o da K2, isto é, o T3 da bancada (`bancada_v2.PONTOS_APRENDIZ["T3"]`).
- S = 2¹⁰;
- passo 512;
- teto 16·S = 16384;
- piso S/16;
- janela de latência 120 ticks;
- recompensas do dono +1 (elogio), −1 (bronca), −0,5 (chamado ignorado);
- sem traço;
- ganho da consequência 4.

Tudo em inteiros e nos mesmos floats da pesquisa. Sem `Math.exp`, `Math.log` ou `Math.sin` no núcleo.

### 1.1 O núcleo dos lobos (L0): tem sentido no jogo de hoje

| peça | o que é | sentido no jogo de hoje |
|---|---|---|
| percepção | `(1, Estado.vetor (8), min(1, tdc/480))`, 10 entradas | sim: o `Observacao` do web (`v`, `tdc`) tem tudo isso. Os lobos usam a `hora` crua, sem o seno e o cosseno do bandit |
| impulsos | as 7 regras do instinto (`sono_exaustao` … `tempo_livre`) e os candidatos, na ordem do instinto | sim: são as regras do `distInstinto` do web, já conferidas pelas constantes |
| lobo de decisão | 490 pesos inteiros `w[regra][ação][entrada]` iniciados no prior (coeficientes do instinto × S); ativação linear; sorteio proporcional com **uma** chamada de `random()`, só quando há mais de um candidato | sim |
| memória e emoção (L0) | só contadores do que o dono fez; contribuição zero | sim, como hoje na pesquisa |
| piso no peso efetivo | S/16, só com o aprendizado ligado | sim |

Com o aprendizado desligado o A é o instinto byte a byte (G2 da L0). No jogo, isso quer dizer que o pet v11 recém-nascido decide como o
instinto, sem o piso do prior do bandit (`CB.piso`). A diferença é pequena, mas existe: o bandit recém-nascido não é o instinto.

### 1.2 O aprendizado da L1 pelo dono: tem sentido, é o braço do produto

- **Regra:** `Δw = arred(f·S·passo·X_j·(S·1[a=a*] − P_a)/(S·S·W_a))` em inteiros, cortada em prior ± teto.
- **Crédito:**
  - elogio e bronca vão para a última decisão;
  - o chamado atendido paga `1 − L/janela`;
  - o chamado ignorado paga −0,5 ao expirar.
- **Sentido no jogo:** é exatamente o que o dono humano faz no jogo de hoje (elogiar, repreender, atender o chamado). É o braço P3 da pesquisa,
  o do produto.
- **O que a pesquisa diz, para não prometer demais:**
  - na L1 (mundo `padrao`, teto 1·S), o aprendiz aprende a tarefa ensinada (G3-T: 0,663 contra 0,577 do instinto na validação);
  - mas muda pouco a distribuição de ações (G3 0,041 bit) e decide em ~18% das decisões (G4); o impulso decide ~80%;
  - o teto 16·S (T3) tira o limite que segurava a L1, mas **nunca foi medido no mundo `padrao` com o dono** (risco R3).

### 1.3 A consequência homeostática (P1): tem sentido, mas a combinação com o dono nunca rodou

- **O sinal:** `f_S = div_arred(ganho·(D_antes − D_depois), S)`, com `D = Σ(S − arred(h·S))²` sobre fome, higiene e energia, na janela
  imediata da própria decisão.
- **Sentido no jogo:** o pet come, dorme e brinca no jogo de hoje, então o sinal existe.
- **Três ressalvas da pesquisa:**
  1. **No mundo `padrao` o P1 falhou na validação do N3:** a privação não caiu (+0,0008 [−0,0067; +0,0077]), e o P1 aprendeu a evitar
     brincar e explorar, porque gastam energia.
  2. **O P1 derruba o acerto na tarefa do dono** (0,593 → 0,444): o dono elogia brincar e explorar, e a consequência ensina o contrário.
  3. **A pesquisa nunca rodou dono + consequência no mesmo cérebro.** P1 e P3 são braços separados em todos os experimentos. No produto os
     dois sinais chegariam juntos.
- **Por isso:** o código da consequência entra no porte com paridade, atrás de uma chave do motor web. Se ela fica **ligada** nos v11 é a
  decisão D-W1 (seção 8). **Recomendação: desligada no v11** até um plano próprio medir o P1+P3 combinado no Python.

### 1.4 O que o bandit fazia e o A não faz: o que vira cada coisa no v11

| função | no v11 | por quê |
|---|---|---|
| temperamento no aprendizado | **não age no cérebro** (D-W3); continua no vínculo, na obediência, na emoção e no desejo | o A da pesquisa não tem temperamento; pôr um fator na recompensa seria cérebro novo sem validação |
| memória por espaços | **continua rodando** como lobo de memória e emoção, só para emoção, fala e motivo de memória, com contribuição zero na decisão (D-W7) | a fala livre lê `m.pol.mem`; o A não usa memória como entrada |
| vontade (desejo) | **definição nova para o A, primeiro no Python** (D-W4) | o bandit usa θ·x, que o A não tem |
| caráter pelo desvio | **o mesmo método**, com o A recém-nascido (o instinto) no lugar do bandit recém-nascido; a escala `CCP.escala` pede medida (D-W5) | a escala foi feita para o desvio do bandit; o A com teto 16·S pode desviar mais, e a linha e a forma adulta mudam |
| gostos da história | o mesmo `desvioPorAcao`, com o A | só a fonte do desvio muda |
| `media()` | só pets v5 (Cenários) a usam; o v11 não precisa | Cenários seguem com pets v5 |

---

## 2. O que espera, e de que depende

| peça | onde está na pesquisa | depende de | no v11 |
|---|---|---|---|
| frutas (sub-decisão, presença, `w_fruta`, E2) | `frutas.py`, LOBOS-MUNDO, FRUTA-NO-CENARIO | o mundo das frutas no jogo (D-W6) | fora |
| bola | `ambiente.py`, `bola_no_cenario` | um objeto do mundo no jogo; a A1 validou só o instinto da bola | fora |
| memória de episódios (N6) | `MemoriaEpisodios` | as frutas: os episódios são consumos de fruta | fora |
| pedido (N7) | `w0_pedido` | as frutas e a tela do pedido | fora |
| informação (N5) | `w0_info` | as frutas e a tela da informação | fora |
| K4 (o dono julga a fruta) | `JulgadorFruta` | as frutas | fora |
| canais de reforço | `canais_ligados` | na validação não mudaram nada (ablação K-7: −0,005 e −0,002, ICs com 0) | fora: sem frutas o humor não entra no sinal, e fome, higiene e energia num canal só dão o mesmo que o escalar |

**O mundo das frutas no jogo (D-W6) é decisão do Matheus.** O custo de levá-lo:
- o `MotorFrutas` em TS: ofertas, prazo, incentivo, avaliação, saciedade, genoma das frutas (neofobia, preferência inata), efeito no
  humor;
- a `rng_fruta` própria;
- os eventos novos no registro;
- a tela: oferecer, informar, pedir;
- o porte das peças do A que só existem com frutas (sub-decisão, presença, N5, N6, N7, K4), com paridade de cada uma;
- uma versão de pet nova (v12), porque muda o registro;
- **o gargalo conhecido viria junto:** a decisão de comer não aprende o efeito de uma fruta quando ela está sozinha
  (`docs/DESCRITIVO_V2_PLATO.md`, Q-8).

Estimativa grosseira: o dobro do porte do núcleo, mais o desenho de tela. **Recomendação: não agora.** Esperar a Q-8 (comer com a fruta
sozinha) e o desenho de jogo das frutas; o v11 sai sem elas.

**Limite registrado (não se resolve aqui):** no mundo das frutas, o A aprende qual fruta evitar quando há duas ou mais, e come o que houver
quando há uma só. O termo de presença aprende pouco (−270 a −370 numa escala de 1024). Isso não afeta o v11, que não tem frutas. Afeta
qualquer v12 com frutas.

---

## 3. Paridade Python ↔ TypeScript

### 3.1 O que dá para conferir e o que não dá

- **Uma vida inteira não sai igual nos dois lados.**
  - O web sorteia com o mulberry32 e o Python com o Mersenne Twister.
  - O motor web é um porte com outras regras de jogo (educação v4, treino, combate, evolução).
  - Isso já é assim hoje (`TAREFA_FRONT_TS`, regra 1).
- **O que dá para conferir: o cérebro com as mesmas entradas.** É como no vínculo B (`test/vinculo.test.ts`, 3256 chamadas) e na
  confiança (200 lutas):
  - o Python exporta fluxos de operações (observação e `u` de cada decisão, ações do dono com o tick, sinais de consequência);
  - o TS aplica o mesmo fluxo e confere o resultado.
- **Nos lobos a tolerância é zero, não 1e−12.**
  - os pesos são inteiros;
  - os pesos efetivos são somas de `(w/S)·x` com S potência de dois, na mesma ordem;
  - o sorteio é `u·total` com a busca da cumulativa.

  Tudo isso é IEEE 754 binário de 64 bits nos dois lados, sem função transcendental. A comparação é `===`.

### 3.2 Cuidados de aritmética (`Math` × inteiros)

| ponto | Python | TS | cuidado |
|---|---|---|---|
| inteiros grandes | `int` sem limite | `number` exato só até 2⁵³ | na atualização, o pior caso de `f·passo·X·fator` com o ganho 4 e S = 1024 fica na ordem de 10¹³, abaixo de 2⁵³ ≈ 9·10¹⁵; mesmo assim, conferir com `Number.isSafeInteger` e **falhar alto**, ou usar `BigInt` só nessa conta. Um teste de pior caso (f máximo, X = S, fator = S, W mínimo) fixa o limite |
| `div_arred` | `divmod(abs(n), d)`, metade longe do zero | `%` do JS tem o sinal do dividendo | portar sobre `Math.abs` e reaplicar o sinal, exatamente como o Python |
| `arred(x)` | `int(x + 0.5)`, simétrico | `Math.trunc(x + 0.5)`, simétrico | não usar `Math.round` (meio para cima, assimétrico no negativo) |
| soma dos termos | laço da esquerda para a direita | laço, nunca `reduce` com outra ordem | a ordem é parte do contrato (L0) |
| sorteio | `accumulate` + `bisect_right(cum, u·total, 0, n−1)` | portar passo a passo | `total = cum[-1] + 0.0`; o mesmo `hi = n−1` |
| consumo da rng | uma chamada de `random()`, só com mais de um candidato | o mesmo, na `rPol` do pet | o bandit consumia uma gaussiana por ação e por entrada, mais um uniforme por ação; a sequência de `rPol` dos v11 é outra (sem efeito nos v1–v10) |

### 3.3 Os gates de paridade (no estilo do vínculo B e do V21E)

| gate | o que confere | gabarito |
|---|---|---|
| P-1 constantes | `ConfigLobos` do T3, `ConfigConsequencia` e a tabela do prior (7 regras × 7 ações × 10 entradas) iguais às do TS | `exportar_constantes_web.py` + `mapa_constantes.json` |
| P-2 decisão | 3000+ observações aleatórias cobrindo as 7 regras, com pesos no prior e pesos aprendidos: regra, candidatos, pesos efetivos, ação e o consumo da rng iguais (`===`) | `exportar_gabarito_lobos.py` (novo) |
| P-3 atualização | registros de decisão com f_S (elogio, bronca, latência, ignorado, consequência): a tabela de pesos e os cortes no teto iguais | idem |
| P-4 vidas | vidas do Python com `PoliticaLobos` no T3, fonte dono (e uma série com a consequência), exportadas como fluxo: o cérebro TS alimentado pelo fluxo tem os pesos iguais em checkpoints diários e no fim | idem |
| P-5 motivo | `motivo_lobos` (impulso × lobo de decisão, regra de honestidade): os fatores, a intensidade e o "lobo decisivo" iguais | idem |
| P-6 G1 web | o registro de um pet v11 rejogado pelo `Motor.reproduzir`: a assinatura bit a bit, no mesmo runtime (o Node dos testes) | gabaritos próprios do app |
| P-7 v1–v10 intactos | os gabaritos de paridade, as assinaturas e os testes das versões anteriores, iguais | os de hoje (`gabaritos.test.mjs`, `paridade_ts`, `vinculo`, `confianca`, `paridade_v21d/e`…) |
| P-8 motor sem DOM | `lobos.ts` sem `window`, `Math.random` nem transcendental no núcleo | `motor_sem_dom.test.mjs` |

Como no front TS, o replay só é bit a bit no mesmo runtime. Chrome e Node podem diferir no último bit de `exp`/`log`, mas o núcleo dos lobos
não usa essas funções. O que pode diferir entre runtimes é o resto do motor web (combate, caráter), como já acontece hoje.

---

## 4. A versão do pet: v11 = v10 + o DigiBrain A

- **`VERSAO_PET = 11`.** Só os ovos novos, e os filhos da herança (`Motor` filho com `VERSAO_PET`), nascem v11.
- **Os pets v1 a v10 não mudam:** o mesmo `Bandit`, a mesma sequência de `rPol`, as mesmas assinaturas e os mesmos gabaritos. O `Motor`
  escolhe o cérebro pela versão (`versao >= 11` → lobos), como o vínculo B (`CVB.versaoPet`) e o V21E.
- **Registro e save:** sem evento novo. O save continua `{semente, log, versao}` na mesma chave. Não há descarte de saves.
- **Assinatura:** nos v11, a parte da política é a assinatura dos lobos: pesos, pendentes, contadores do lobo de memória e emoção, e o
  estado da memória por espaços, que segue rodando (seção 1.4). A dos v1–v10 não muda.
- **Tudo o que os v10 têm continua** (vínculo B, confiança, voz, medalhas, itens, Fronteira, V21E). Só o cérebro da vida troca. Os gambits
  híbridos do combate são outro aprendizado e não mudam.
- **Cenários** continuam com pets v5.

### 4.1 O motivo na tela, a partir do `motivo_lobos`

- **Portar `motivo_lobos`** (`digilab/motivo.py`) para `motor/motivo.ts`, ao lado do `motivoVida` do bandit, escolhido pela versão.
- **Regra de honestidade, a mesma da pesquisa:**
  - **o impulso decidiu** quando a regra tem um candidato só, ou quando o sorteio com os pesos do **prior** e o mesmo `u` dá a mesma
    ação. Nesse caso os fatores são os da regra do instinto (`motivo_instinto`), e o adulto diz "Foi instinto: é o meu jeito." quando não há
    fator (`GENERICO_INSTINTO`, já resolvido em 2026-09-29);
  - **o lobo de decisão decidiu** no resto. A contribuição de cada entrada é o termo aprendido da escolhida menos a média dos termos
    aprendidos dos outros candidatos. Só vira fator uma contribuição positiva e ≥ `limiar_motivo`, no máximo 2.
- **Vocabulário dos fatores:** o dos lobos (`habito`, `fome` … `tempo_sem_cuidado`) já é o `FATOR_BASE` do web, sem o `hora` duplicado do
  seno e do cosseno. Os fatores de memória do bandit (`FATORES_ESPACOS`) não aparecem como fator de decisão no v11, porque a memória não
  entra na decisão.
- **Tela:**
  - a fala sob a tela e o motivo (clique) seguem o mesmo componente;
  - a aba Aprendizado mostra, no lugar dos braços do bandit:
    - o **desvio dos pesos** sobre o prior, por regra e ação (o que o pet aprendeu);
    - a **fração das decisões em que o aprendido decidiu** (a sonda da honestidade).
- **Nenhum fator é inventado:** a tela só cita o que o `motivo_lobos` devolve.

---

## 5. A fala e a voz: o que muda no que a LLM lê

- **A moldura** (`fala-v6`, Ollama) e **a fala livre** (`livre-v8`, gemma2:9b) leem o **motivo** (ação e fatores) e os **fatos**
  (H/O/P/L, do registro). Nos v11:
  - **os fatores vêm do `motivo_lobos`**, com o mesmo vocabulário e o mesmo limite de fatores por estágio. As tabelas de `expressao.py` e
    `expressao.ts` já cobrem esses nomes. Conferir com o teste de cobertura;
  - **mais "foi instinto":** com o impulso decidindo ~80% das vezes no mundo `padrao` (L1), o motivo sem fator aprendido vai ser o caso
    comum. É honesto: o pet que segue o instinto diz que seguiu. A tela não deve fingir aprendizado;
  - **as emoções** (`m.pol.mem` em `falaLivre.ts`) continuam vindo da memória por espaços (D-W7). Se o Matheus decidir tirá-la, a fala
    livre perde o bloco de emoção, e o `falaLivre.ts` precisa de outra fonte;
  - **os gostos da história** (`desvioPorAcao`, voz v7+) passam a medir o desvio do A sobre o instinto. A escala muda (D-W5), e o limiar do
    "gosto" pode precisar de outro valor (medir junto com o caráter);
  - **o comando pelo chat** não muda: ele vira o evento `d` do dono, que chega ao A como qualquer ação do dono.
- **Nada da LLM entra no registro** (regra do front e da fala livre); o A não lê texto.

---

## 6. A ordem das tarefas de código, com dono e gates

| # | tarefa | dono | depende de | gates |
|---|---|---|---|---|
| W1 | **Gabaritos Python** (`experiments/exportar_gabarito_lobos.py` → `web/app/test/gabaritos/lobos_python.json`): constantes do T3 e do prior, as observações da P-2, os registros da P-3, as vidas em fluxo da P-4 (fonte dono; uma série com a consequência), os motivos da P-5. Sementes só dos testes. Se D-W4 escolher a vontade nova, ela entra no Python primeiro, com teste | chat B | D-W4 | o exportador roda duas vezes e dá o mesmo arquivo; a suíte Python inteira; nada do `digilab/` muda além da vontade (se decidida) |
| W2 | **Núcleo do A em TS** (`web/app/motor/lobos.ts`): percepção, impulsos (as regras do `distInstinto` com nome), tabela do prior, decisão, piso, L1 pelo dono, a consequência atrás de chave, a assinatura. Sem ligar no `Motor` ainda | chat A | W1 | P-1, P-2, P-3, P-4 (`===`), P-8; o pior caso de inteiro (seção 3.2) |
| W3 | **Pets v11 no motor:** `VERSAO_PET = 11`, o `Motor` escolhe o cérebro pela versão; memória por espaços como lobo de memória e emoção; desejo/vontade (D-W4); caráter e `desvioPorAcao` com o A recém-nascido; temperamento fora do cérebro (D-W3) | chat A | W2, D-W3, D-W4, D-W7 | P-6, P-7 (os v1–v10 intactos, gabaritos e assinaturas); `motor_sem_dom`; um save v10 abre igual |
| W4 | **Motivo e fala do v11:** `motivo_lobos` em `motivo.ts`, regra de honestidade, cobertura das tabelas de expressão, `falaLivre.ts` lendo a memória do v11 | chat A | W3 | P-5; `voz.test.ts` e `voz_app.test.ts` nas versões de antes e no v11; nenhum fator fora do motivo |
| W5 | **Medida do caráter e da forma no v11** (D-W5): um script como o `medir_vinculo_mega.mjs`, com os donos simulados da web, que mede a distribuição de linhas e formas adultas do v11 contra a do v10. Artefato em `artifacts_v2_web/` | chat A | W3 | só relato; o Matheus decide a escala antes de liberar o v11 |
| W6 | **Tela:** aba Aprendizado do v11 (desvio dos pesos, fração em que o aprendido decidiu), o motivo, o e2e com um save v11 | chat A ou D | W3, W4 | `npm test`, `npm run tipos`, `npm run e2e` (checklist da seção 14 do guia, 360/390 px, dois temas); sem erro no console |
| W7 | **Ligar o v11 no jogo** (o `VERSAO_PET` dos ovos novos) e registrar (`CLAUDE.md`, memória) | coordenador + Matheus | W1–W6 e D-W5 | a suíte web inteira e a Python |

**Paralelismo:** W1 e o esqueleto do W2 andam juntos (o W2 só fecha com o gabarito). W5 e W6 andam juntos depois do W3. A consequência
(chave do W2) só é ligada se o D-W1 mandar.

---

## 7. Riscos

| # | risco | efeito | mitigação |
|---|---|---|---|
| R1 | aritmética divergente (inteiro acima de 2⁵³, `%` com sinal, `Math.round`, ordem da soma) | pesos diferentes do Python, em silêncio | `===` nos gates P-2 a P-4, teste do pior caso, falhar alto em `!Number.isSafeInteger` |
| R2 | o A aprende pouco no mundo `padrao` (L1: G3 e G4 falharam; o impulso decide ~80%) | o jogador não vê o pet aprender; a fala diz "foi instinto" quase sempre | é o resultado da pesquisa e fica declarado na tela (seção 4.1); não se calibra o v11 para parecer que aprende |
| R3 | o T3 (teto 16·S) nunca rodou no `padrao` com o dono; a L1 validou o teto 1·S | a deriva pode crescer sem o teto segurar (o G6 falhou pelo teto na L1) | a medida do W5 relata a deriva; se o Matheus preferir, o v11 fica no L1 (D-W2) |
| R4 | o dono humano não tem orçamento: pode elogiar sem parar | os pesos andam até o teto em minutos | o teto segura (16·S); o bandit tinha o mesmo risco; registrar como limite de produto |
| R5 | o caráter e a forma adulta mudam com o A (o desvio tem outra escala) | outra distribuição de linhas e formas; o equilíbrio do combate foi feito com as formas dos v9 | W5 mede antes; D-W5 decide |
| R6 | dono + consequência no mesmo cérebro nunca rodou; no `padrao` o P1 falhou e brigou com a tarefa do dono | se ligada, o pet pode aprender a evitar brincar e explorar e ignorar o elogio | D-W1: desligada no v11 |
| R7 | a escolha do A é pós hoc (M6 declarado) e a evidência vem do mundo das frutas, que o v11 não tem | o que fez o A vencer (escolher a fruta e resistir à informação errada) não aparece no v11 | declarar no `CLAUDE.md` do v11: o v11 tem o A do mundo `padrao` |
| R8 | ações do dono do web que o A da pesquisa não conhece (v4: tratar lesão, disciplina; treino) | crédito do chamado ou do sinal diferente da pesquisa | W1 exporta o mapa ação do web → efeito no A (cuidado que atende chamado, sinal, nada); W2 confere |
| R9 | a `rPol` dos v11 é consumida de outro jeito (uma chamada por decisão com escolha) | sistemas que compartilhassem a `rPol` mudariam | hoje só a política a usa (`motor.ts:848`; o caráter sonda com rngs próprias); o W3 mantém assim, e a P-7 cobre os v1–v10 |
| R10 | o gargalo da fruta sozinha (Q-8) | nenhum no v11; num v12 com frutas o pet come a fruta ruim sozinha | registrado como limite; v12 espera a Q-8 |

---

## 8. Decisões do Matheus

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| D-W1 | a consequência homeostática ligada no v11? | **não:** portar com paridade, atrás de chave, desligada; ligar só depois de um plano que meça P1+P3 juntos no Python | ligada sem medir: o pet pode aprender contra o dono (o N3 derrubou o acerto da tarefa de 0,59 para 0,44), e corrigir pede um v12 |
| D-W2 | o ponto do aprendiz no `padrao`: T3 (o da K2, teto 16·S) ou L1 (teto 1·S, o validado no `padrao`)? | **T3**, como o M6 e a tarefa pedem, com a deriva relatada pelo W5 antes de ligar | T3: deriva sem freio, a forma muda mais. L1: teto preso em 12 de 20 vidas (G6 da L1), aprende menos ainda |
| D-W3 | o temperamento no aprendizado | **fora do cérebro no v11** (continua no vínculo, obediência, emoção e desejo) | pôr um fator na recompensa sem validar seria cérebro novo; tirar perde a diferença "sensível × teimoso" no aprender, que hoje existe nos v2–v10 |
| D-W4 | a vontade (desejo) com o A | **definir no Python primeiro** (W1): a ação de maior desvio aprendido sobre o prior na regra `tempo_livre`, com a mesma margem (`CDJ.limiarVontade`), e gabarito. Alternativa: v11 só com necessidades, sem vontade | sem vontade, o vínculo B (que usa o desejo) e a tela do desejo mudam de comportamento; com uma definição só na web, perde a paridade |
| D-W5 | a escala do caráter (`CCP.escala`) no v11 | **medir primeiro** (W5); manter a escala se a distribuição de linhas e formas ficar perto da do v10; senão, recalibrar só nos v11 | sem medir: formas adultas concentradas ou espalhadas, e o equilíbrio do combate (validado com as formas de hoje) sai do lugar |
| D-W6 | o mundo das frutas no jogo | **não agora:** esperar a Q-8 e um desenho de jogo das frutas; vira v12 | levar agora: ~o dobro do porte, com o gargalo da fruta sozinha embutido no produto |
| D-W7 | a memória por espaços nos v11 | **manter** como lobo de memória e emoção, sem entrar na decisão (só emoção, fala e motivo de memória) | tirar: a fala livre perde as emoções e o `falaLivre.ts` precisa de outra fonte; pôr na decisão seria cérebro novo |

---

## 9. Fora deste plano

- Código. Este documento é só papel; as tarefas W1 a W7 são PRs próprios.
- Os cérebros B e C. O B não fecha, e o C não foi escolhido no M6.
- Qualquer run com faixa reservada. Os gabaritos do W1 usam só as sementes dos testes.
- Mudar o que a validação única ou o descritivo do platô leram.
- Nenhuma alegação de novidade.
