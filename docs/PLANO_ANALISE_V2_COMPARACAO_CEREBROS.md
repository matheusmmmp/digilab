# Plano de análise — comparação dos DigiBrains A × B × C (K3/V2)

Status: **registrado antes de qualquer dado e antes de os cérebros B e C existirem** (2026-10-05). Tarefa
`docs/TAREFA_V2_PLANO_COMPARACAO_CEREBROS.md`; etapa K3/V2 do `docs/ROADMAP_V2.md` (revisão 3); base
`docs/research/digibrain/synthesis/brain_comparison.md`; calibração do A em `docs/PLANO_CALIBRACAO_CONJUNTA_V2.md` (K-1 a K-11,
aprovadas). **Só papel:** nenhuma run, nenhum código, nenhuma semente de validação. Os números de desenho sem fonte estão marcados
PROPOSTO; o resto é decisão do Matheus (seção 11).

**A pergunta deste plano.** Como comparar, de modo justo, três cérebros que aprendem no mesmo mundo, para escolher o DigiBrain da web
(M6)?
- **A:** os lobos, família de origem no *Creatures*;
- **B:** CfC com ator-crítico, família do NORNBRAIN;
- **C:** circuitos especializados, família inspirada na *Drosophila*.

Cada um é calibrado com o mesmo orçamento, e depois os três passam por uma validação única.

**O que este plano não faz:**
- **Não atribui efeito a peça.** A × B muda representação, recorrência, regra e crédito de uma vez (problema 3 de `brain_comparison.md`).
  Este plano escolhe um cérebro de produto; não diz qual peça fez a diferença. A ablação fatorial fica de fora (decisão C-9).
- **Não fala das fontes.** "Inspirado em" fala do nosso cérebro (problema 4):
  - **Creatures:** Grand, Cliff e Malhotra 1997, `10.1145/267658.267663`; Grand e Cliff 1998, `10.1023/A:1010042522104`; Cliff e Grand
    1999, `10.1162/106454699568683`; todas VERIFICADA. Descrevem a família de origem do A, e nada aqui diz algo sobre o *Creatures*.
  - **NORNBRAIN, CfC (Hasani et al. 2022), NCP (Lechner et al. 2020) e FlyWire (Dorkenwald et al. 2024):** são CORPUS ou software não
    revisado. Entram como pista, nunca como evidência.
- **Não reabre as predições do experimento maior.** Elas são do A e ficam com a família de Holm delas. Esta comparação é uma **família
  própria**.
- **Nenhuma alegação de novidade.**

---

## 1. O contrato comum

O contrato que os três cérebros cumprem antes de qualquer calibração. Cada item é conferido por teste no PR que entrega o cérebro (C5); sem
ele o cérebro **não fecha** (seção 7).

### 1.1 Interface

| item | contrato |
|---|---|
| protocolo | `Politica` (`agir`, `observar`, `estado_interno`) e os ganchos que a bancada usa hoje: `receber_acao_dono`, `observar_consequencia`, `escolher_fruta`, `fruta_comida` |
| ações | as de `AcaoPet`, sem membro novo (V5); a fruta é sub-decisão de `comer` |
| o que vê | a mesma `Observacao` dos lobos que veem o mundo: estado, tempo sem cuidado, `bola`, `fruta`, `frutas_cenario`, `info_frutas`; nada do motor que o A não veja (nem os efeitos reais das frutas, nem a rng) |
| o herdado | **o mesmo nos três** (decisão C-1): a regra do instinto e os candidatos que ela propõe (o lobo de impulsos do A) entram como dado comum. Cada cérebro aprende **por cima** desse prior |
| aprendizado desligado | **= instinto byte a byte** pela bancada (o G2 da L0): o P0 é um só para os três |
| fontes do sinal | as da bancada (`PoliticaDoBraco`): P1 consequência com a E2, P2/P2e/P2a informação + consequência, P3 dono; o cérebro não escolhe de onde o sinal vem |
| sonda do aprendido | toda decisão expõe a escolha que sairia **com a parte aprendida zerada e o mesmo `u`**. É o que permite o motivo honesto (G4) nos três, com a mesma regra |
| determinismo | replay bit a bit no mesmo runtime (G1), estado interno incluído; rngs de ambiente e de política separadas |
| onde roda | só no Python (decisão de 2026-10-01); a web roda só o escolhido |

**Por que o herdado é comum.** A pergunta maior compara a plasticidade com o herdado. Se cada cérebro tivesse um prior diferente, a
comparação misturaria "aprende melhor" com "nasceu melhor". Com o prior comum, B e C diferem do A só no que aprendem e em como aprendem.
Para o B, isso quer dizer: os logits são o log do peso do instinto mais uma saída da rede iniciada em zero (exp(0) = 1 exato). Assim, no
começo, a política é a do instinto.

### 1.2 O mesmo mundo, os mesmos braços

- **Bancada** (`experiments/bancada_v2.py`): os mundos `casado_frutas`, `descasado` e `mutavel`; o dono atencioso; as ofertas do
  `CalendarioFrutas`.
- **Braços:** P0 (comum), P1, P2, P2e, P3.
- **Só cuidado acoplado:** `sem_ensino` dos braços com dono, por cérebro.
- **Fora da comparação** (decisão C-2): os blocos N6 e N7 e o mundo `iguais_frutas`. São mecanismos do A (memória de episódios,
  arbitragem do pedido). Exigi-los de B e C impõe a arquitetura do A aos outros. B e C podem ter memória (a recorrência do CfC é uma) e
  arbitragem próprias, e o desempenho mede o que elas fizerem.

### 1.3 Mesma capacidade

- **Medida:** o número de parâmetros aprendíveis, por `estado_interno` (ou por contagem declarada no PR do cérebro).
- **Contrato:** B e C ficam entre 0,9× e 1,1× (PROPOSTO) da capacidade do A no ponto da K2.
- **A referência de hoje:** o A tem 763 pesos com as frutas e o `w0_info` (`CLAUDE.md`, seção "V2, FRUTA-NO-CENARIO, parte B"), mais o
  peso compartilhado do pedido. O número exato sai do estado interno do A no ponto da K2.
- **Curva por capacidade:** o B a 0,5× e 2× fica como descritivo opcional (decisão C-3).
- **O que conta:**
  - um parâmetro inteiro conta igual a um parâmetro em ponto flutuante;
  - parâmetros fixos do herdado não contam;
  - estado recorrente não é parâmetro;
  - a memória de episódios do A não tem peso.

### 1.4 Mesmo orçamento de calibração

**A moeda é a de vidas e de pontos de grade, não a de tempo** (decisão C-4). O tempo é limite de viabilidade.

| item | o orçamento de cada cérebro | origem |
|---|---|---|
| parâmetros livres | até 4 | o A tem 4 na K1 (`g`, `w0_pedido`, ganho, `w0_info`) |
| pontos de grade | até 12 (3 por parâmetro, varridos em cadeia, sem grade cruzada) | K-2 |
| vidas de calibração | no máximo as que o A gastou na K2, contadas no artefato da K2 (a K1 estima ~1260) | `PLANO_CALIBRACAO_CONJUNTA_V2.md`, seção 5.2 |
| regras de escolha | verificações de manipulação ou de estabilidade, **nunca** um contraste entre braços nem entre cérebros | K-3, K-4 |
| tempo de máquina | até 4× o tempo da K2 do A (PROPOSTO) | seção 7 |

**Antes de calibrar B ou C:** quem implementa registra, num **adendo a este plano**, os parâmetros livres, as grades e as regras. O
adendo é commitado antes de qualquer run e conferido pelo coordenador contra a tabela acima.

**O A não é recalibrado.** Ele entra no ponto da K2.

---

## 2. Modos

- **Fechado (primário):** cada cérebro vive a própria vida, com a mesma semente de mundo e de dono e as rngs separadas. Mede o desempenho
  com a experiência que cada cérebro provoca.
- **Acoplado (secundário):** o registro da vida do A no P1 é rejogado em malha aberta com B e C (modo acoplado da bancada, filtro
  `nenhum`). Mede quanto cada um aprende da **mesma** experiência (problema 1 de `brain_comparison.md`).

---

## 3. Medidas

| medida | o que é | onde |
|---|---|---|
| **`taxa_fruta_ruim`** (primária) | descasado: janela final (dias 8–14); mutável: depois da troca | `metrics.taxa_fruta_ruim` |
| `taxa_fruta_ruim` no casado | o custo de aprender onde o herdado já acerta (predição 1) | idem |
| eficiência amostral | consumos até a metade do caminho (`consumos_ate_metade`) | bancada |
| tempo fora de privação, saúde, mortes | o canal de cuidado; G5 contra o acoplado de cada cérebro | `desempenho_no_ambiente` |
| **legibilidade** | fração das decisões em que a parte aprendida mudou a escolha (sonda do aprendido), com o motivo honesto (G4 do aprendido) | sonda do contrato 1.1 |
| deriva | JSD ao instinto no fim de cada dia; razão 14/7 (G6) | `custo_da_plasticidade` |
| divergência da mesma experiência | no acoplado, a JSD entre a política de cada cérebro e a do A, por dia | sondas da v1 |
| custo | CPU por decisão, memória por pet, bytes de log por dia | medidos na run, com a máquina no `meta.json` |
| as cinco predições do experimento maior, por cérebro | descritivas para B e C (as do A são as da validação única) | contrastes da BANCADA-EXPERIMENTO |

**Ressalva da legibilidade:** a fração decidida pelo aprendido é uma medida do sistema, não de compreensão humana. Legibilidade para
pessoas tem de ser medida com pessoas (Anderson et al. 2019, `10.24963/ijcai.2019/184`, VERIFICADA). Isso fica para a fase 2.

---

## 4. Contrastes e família

**Família primária da comparação** (própria, Holm com α = 0,05, quatro testes **bilaterais**, sem direção predita):

| # | contraste | medida |
|---|---|---|
| CB-1 | B − A, P1 | `taxa_fruta_ruim` final, descasado |
| CB-2 | B − A, P1 | `taxa_fruta_ruim` depois da troca, mutável |
| CC-1 | C − A, P1 | `taxa_fruta_ruim` final, descasado |
| CC-2 | C − A, P1 | `taxa_fruta_ruim` depois da troca, mutável |

**Por que o P1 e essas duas condições:**
- o P1 é o braço em que a plasticidade vem só do mundo, o mesmo sinal para os três;
- descasado e mutável são as condições em que há o que aprender (predição 2 do experimento maior);
- os braços com dono e o casado entram como secundários, para a família não crescer.

**O resto:**
- **Empate:** a diferença é um **empate** quando o IC 90% fica dentro de (−Δ, +Δ). Δ é o do adendo do experimento maior (metade da
  distância entre o P0 descasado e 0, seção 6.3 de lá). É a mesma margem de relevância, sem número novo.
- **Secundário:** B − C, e todos os contrastes em P2, P2e, P3 e no casado.
- **Descritivo:** a legibilidade, a deriva, o custo e a divergência acoplada, com IC.
- **Pareamento:** por unidade (genoma, semente), bootstrap reamostrando as sementes, como na seção 6 do experimento maior.

---

## 5. O critério de escolha do DigiBrain da web (M6)

**Ordem de prioridade, aplicada de cima para baixo (decisão C-5).** Um cérebro só passa ao passo seguinte se empatar com o melhor no passo
atual.

| passo | critério | como se decide | empate quando |
|---|---|---|---|
| 0 | **admissão** | fechar (seção 7): determinístico, dentro do orçamento e da capacidade, aprende | — (eliminatório) |
| 1 | **desempenho na pergunta maior** | os contrastes CB e CC (seção 4): o cérebro com a menor `taxa_fruta_ruim`, com os dois contrastes de cada par lidos juntos | IC 90% de cada contraste dentro de (−Δ, +Δ), ou a diferença não passa no Holm |
| 2 | **legibilidade** | fração decidida pelo aprendido com motivo honesto, P1 descasado, validação; vence a maior | diferença com IC 95% contendo 0, ou menor que 0,05 em valor absoluto (PROPOSTO) |
| 3 | **determinismo inteiro e porte** | aritmética inteira sem funções transcendentais vence ponto flutuante: a paridade Python × web bit a bit (regra da casa para os pets) só é possível assim | dois cérebros inteiros |
| 4 | **custo** | CPU por decisão e bytes de log por dia; vence o menor | diferença menor que 20% (PROPOSTO) |
| 5 | **desempate final** | o A, que já está montado, validado e com porte conhecido | — |

**Por que esta ordem:**
- **O desempenho primeiro:** a pergunta maior é sobre vantagem adaptativa, e o DigiBrain da web é o que a responde melhor.
- **A legibilidade em segundo:** é a razão de ser do motivo e da fala.
- **O porte em terceiro:** é custo de engenharia, não de pesquisa (problema 5).

**A alternativa registrada:** legibilidade primeiro. É o que favorece o produto (o pet que explica o que aprendeu); o custo é escolher um
cérebro que aprende menos.

**O B quase certamente perde no passo 3**, se chegar a ele: ponto flutuante com `exp`/`tanh` não tem paridade bit a bit entre o V8 e o
CPython (`docs/research/digibrain/sources/nornbrain.md`). Para o B ser o escolhido, ele precisa vencer no passo 1 ou no 2.

---

## 6. Sementes, unidades e tamanho da amostra

### 6.1 Faixas propostas (o coordenador fecha)

| o quê | faixa | bases |
|---|---|---|
| calibração de B e C (e o piloto da comparação, com o A no ponto da K2) | **28101…28505** | 28101, 28202, 28303, 28404, 28505 |
| validação da comparação, A, B e C, uma vez | **29101…29505** | 29101, 29202, 29303, 29404, 29505 |

**Por que faixas novas** (a tarefa pede):
- ficam fora de `FAIXAS_RESERVADAS` (até 22505, mais 50001…82004 e as de 2026) e da seção 6 do roadmap;
- as faixas do N11 (16101…17505, reservadas para "cérebros") **não** são usadas. A decisão C-8 pede ao coordenador marcá-las como
  substituídas por estas;
- **também ficaram de fora** as faixas 23101…27505, propostas pela leitura parcial (LP) e superadas pela M11, para não haver confusão.

**Busca feita** no repositório, fora dos artefatos: nenhuma das 10 bases aparece.

### 6.2 Unidades

- **Derivação:** `derivar_semente("comparacao-cerebros", b, k)` e `derivar_semente("comparacao-cerebros-genoma", b, k)`. O prefixo novo
  entra na `unidades_derivadas` da bancada, que já aceita prefixo (BANCADA-N6-N7).
- **Mesmas unidades para os três cérebros:** o pareamento é por unidade.
- **K da calibração = 4 por base, 20 unidades (PROPOSTO):** o mesmo da K1.

### 6.3 Adendo de tamanho de amostra

1. **Piloto:** no fim da calibração de B e C, os três cérebros, cada um no seu ponto, rodam o piloto nas unidades de 28101…28505. O A
   entra só como referência, sem nada escolhido nele.
2. **σ²_d** dos quatro contrastes primários.
3. **N por contraste:** N = ((z₁₋α/₂ + z₀,₈) × σ_d / Δ)², bilateral, α/4 (o passo mais exigente de Holm), poder 0,8. Conferência por
   simulação com bootstrap das unidades do piloto.
4. **N da validação = o maior N**, arredondado para cima ao múltiplo de 5. K da validação = N / 5.
5. **Teto de tempo:** o da decisão K-10 (12 h). Acima dele, o Matheus decide antes da validação.
6. **Conteúdo do adendo** (commitado neste arquivo antes da validação): os pontos de B e C e as regras que os escolheram, Δ, σ²_d, N, as
   unidades e o tempo estimado.

**Custo estimado por unidade na validação:**
- 3 cérebros × (P1, P2, P2e, P3 × 3 condições) = 36 vidas;
- os acoplados `sem_ensino` dos três braços com dono, por cérebro: 27 vidas;
- o P0 comum: 3 vidas;
- o acoplado da mesma experiência (B e C no registro do P1 do A, descasado e mutável): 4 vidas;
- **total: 70 vidas por unidade.**

O tempo por vida de B e C não é conhecido. O do A, na revisão do aprendiz, foi ~5,5 s (`docs/RESULTADO_V2_REVISAO_APRENDIZ.md`: 1 h 50
min para 1200 vidas).

---

## 7. Quando um cérebro "não fecha"

Um cérebro que não fecha sai da escolha M6, com o motivo registrado como resultado, e a comparação segue com os outros. Se só o A fechar,
ele é o escolhido por omissão, e o relatório diz isso.

| motivo | conta como não fechar quando | onde se confere |
|---|---|---|
| **não é determinístico** | o replay diverge (G1) ou o aprendizado desligado não é o instinto byte a byte (G2) | testes do PR do cérebro (C5) |
| **não cumpre o contrato** | falta um gancho, a entrada da informação, a sub-decisão da fruta ou a sonda do aprendido | idem |
| **não tem a mesma capacidade** | parâmetros aprendíveis fora de [0,9; 1,1] × A | idem |
| **não cabe no orçamento** | a calibração passa das vidas ou dos 12 pontos do A, ou o tempo passa de 4× o da K2 do A | calibração |
| **não aprende** | no piloto, o P1 tem a deriva ao instinto no dia 14 com o limite inferior do IC 95% ≤ 0, **ou** a parte aprendida muda a escolha em menos de 1% das decisões (limite superior do IC 95% < 0,01; PROPOSTO) | piloto da calibração |

"Não aprende" não é o mesmo que "aprende pior": um cérebro que aprende pior segue na comparação e perde no passo 1.

---

## 8. Ordem e regra de parada

1. **Pré-requisitos:**
   - a validação única do A (V1) na `main`, com o ponto da K2 e o Δ do adendo do experimento maior;
   - B e C (C5) na `main`, com o contrato da seção 1 conferido por teste;
   - os adendos de calibração de B e C commitados.
2. **Calibração de B e C** (28101…28505), cada um no seu orçamento.
3. **Piloto e adendo** de tamanho de amostra (seção 6.3).
4. **Validação** (29101…29505), uma vez, análise única.
5. **Refazer:** só por erro de execução, com sementes novas registradas antes; nunca pelo resultado.
6. **Escolha M6** pela seção 5, registrada em `docs/RESULTADO_V2_COMPARACAO_CEREBROS.md` e lida na leitura consolidada da fase 1.

**Artefatos:** `artifacts_v2_comparacao_cerebros/{calibracao_B,calibracao_C,piloto,validacao}/`.

---

## 9. Riscos registrados antes

1. **O C pode ficar parecido demais com o A neste mundo.** Os circuitos por classe de estímulo (H-ACT-02) pedem ameaça, social e objeto.
   O mundo tem só objetos e o dono (`docs/research/digibrain/mechanisms/action_selection.md`). Depois do C4, o A também tem canais. Um
   empate A × C no passo 1 é provável e cai no desempate. Isso é registrado como limite do mundo, não como resultado sobre circuitos.
2. **O B pode não aprender com tão poucas consequências.** Ator-crítico com gradiente costuma pedir muito mais amostras do que uma vida de
   14 dias dá. Escolhas com duas frutas ou mais: 4 a 24 por vida no N4 (`docs/RESULTADO_V2_N4.md`). O critério "não aprende" (seção 7)
   existe para isso.
3. **"Mesmo orçamento" favorece quem tem menos parâmetros livres.** Um cérebro com muitos hiperparâmetros (taxas, elegibilidade, escala da
   rede) fica pior afinado com 12 pontos. Isso é aceito de propósito: o produto não pode depender de uma afinação que o A não teve.
4. **A capacidade igual é aproximada.** Parâmetros inteiros e em ponto flutuante não carregam a mesma informação. A curva por capacidade
   do B (C-3) é o único remédio dentro deste plano.
5. **O A foi calibrado em outras sementes** (14101…14505) e B e C, nas de 28101. As três validações usam as mesmas unidades
   (29101…29505), que nenhum dos três viu.

---

## 10. Fora deste plano

- código e runs;
- o desenho de B e C (C5);
- a ablação fatorial das peças;
- os blocos N6 e N7 em B e C;
- outros donos;
- humanos;
- o porte para a web (W).

---

## 11. Decisões do Matheus

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| C-1 | o herdado é comum aos três (o instinto como prior, cada cérebro aprende por cima; desligado = instinto byte a byte) | sim | priors diferentes misturam "aprende melhor" com "nasceu melhor", e o P0 deixa de ser um só |
| C-2 | blocos N6 e N7 fora da comparação | sim; B e C podem ter memória e arbitragem próprias, medidas pelo desempenho | exigi-los impõe a arquitetura do A a B e C e multiplica as vidas |
| C-3 | capacidade | 0,9× a 1,1× a do A; a curva do B (0,5× e 2×) só como descritivo opcional | sem faixa, a comparação mede tamanho; com curva obrigatória, o orçamento dobra |
| C-4 | moeda do orçamento | vidas e pontos de grade (até 4 parâmetros, 12 pontos, as vidas da K2 do A); tempo como limite (4×) | orçamento por tempo favorece o cérebro mais rápido, não o que aprende melhor |
| C-5 | ordem do critério M6 | desempenho → legibilidade → determinismo inteiro e porte → custo → o A | legibilidade primeiro escolhe um cérebro que explica mais e aprende menos; porte primeiro elimina o B antes de qualquer medida |
| C-6 | família primária | quatro contrastes bilaterais (B − A e C − A, P1, descasado e mutável), Holm próprio; o resto secundário | família grande derruba o poder; uma família só com o descasado ignora a adaptação à mudança |
| C-7 | o que é "não fecha" | os cinco motivos da seção 7, com os limiares PROPOSTOS | sem critério, um cérebro que não aprende arrasta a comparação; com critério frouxo, entra um que só replica o instinto |
| C-8 | faixas | 28101…28505 (calibração de B e C e piloto) e 29101…29505 (validação); as do N11 (16101…17505) marcadas como substituídas | usar as do N11 contraria a tarefa; reusar qualquer faixa vicia o teste (M7) |
| C-9 | ablação fatorial | fora deste plano; a comparação escolhe um cérebro, não atribui efeito a peça | fazê-la agora multiplica os cérebros (o "Frankenstein" que o corpus desaconselha) antes de saber se B e C fecham |
| C-10 | adendo de calibração de B e C | obrigatório antes de calibrar, conferido pelo coordenador contra a seção 1.4 | sem ele, o orçamento vira o que cada implementador achar que precisa |
