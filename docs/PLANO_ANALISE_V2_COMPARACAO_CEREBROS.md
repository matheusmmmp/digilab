# Plano de análise — comparação dos DigiBrains A × B × C (K3/V2)

> **V2, congelado em 2026-10-30** (tag `v2-final`). O estado em que este documento fica na V3 está em `docs/FECHAMENTO_V2.md`; o
> plano da V3, em `docs/PLANO_V3.md`.

> **Nota (2026-10-24), a direção nova:** o Matheus decidiu, no PROMPT MESTRE, que o produto jogável vem primeiro, que o DigiBrain
> caminha para um cérebro **modular**, e que o cérebro A fica como linha de base, controle e fallback condicionado, e não como o cérebro
> final da web. As decisões "a web roda um DigiBrain, o A" (2026-10-01) e o M6 (rodada 15) estão **SUPERADAS** desde 2026-10-24; o
> texto abaixo fica como estava, como registro. Ver `docs/ARQUITETURA_DIGIBRAIN_MODULAR.md` e `docs/AUDITORIA_V2_PRODUTO_MODULAR.md`.
>
> O propósito deste plano (escolher o DigiBrain da web pelo M6) está superado. Os resultados continuam como evidência sobre o A, o B e
> o C, e o B e o C ficam como referência para os módulos (`docs/ARQUITETURA_DIGIBRAIN_MODULAR.md`, seção 2).

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

**DECIDIDAS em 2026-10-05: C-1 a C-10, todas como recomendado** (rodada 10 do `docs/ROADMAP_V2.md`).

- As faixas 28101…28505 e 29101…29505 ficam reservadas.
- As faixas do N11 (16101…17505) ficam substituídas.

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

## Adendo 1 (2026-10-06, antes de qualquer run): calibração dos cérebros B e C

Registrado pelo coordenador, que copiou os adendos dos PRs [#179](https://github.com/matheusmmmp/digilab/pull/179) (B) e
[#176](https://github.com/matheusmmmp/digilab/pull/176) (C) sem mudar o conteúdo. Pela seção 1.4, os dois foram **conferidos pelo
coordenador** em 2026-10-06:

| | parâmetros livres (≤ 4) | pontos de grade (≤ 12, em cadeia) | vidas | regras |
|---|---|---|---|---|
| B | 4 | 10 | ~660 | estabilidade (K-4) e manipulação (K-3) |
| C | 3 | 9 | 480 a 540 | estabilidade (K-4) e manipulação (K-3) |

Nos dois, nenhuma regra de escolha usa contraste entre braços nem entre cérebros, nem a `taxa_fruta_ruim`.

**Condição pendente:** o teto de vidas de cada cérebro é o número de vidas que o A gastar na K2, contado no artefato da K2. Antes de
calibrar B ou C, o coordenador confere esse número em `artifacts_v2_calibracao_conjunta/`. Se um dos dois passar do teto, a grade dele
encolhe por um adendo novo, antes da run.

### 1.1 Adendo do cérebro B (do #179)

**Parâmetros livres: 4 de 4** — `taxa_ator`, `taxa_critico`, `lambda_elegibilidade` e `w0_info`.
- Fixos e iguais aos do A: o ponto fixo do prior (S = 1024), a percepção, a janela de crédito e as recompensas do dono.
- O ganho do sinal da consequência é o da K2 do A, porque a fonte do sinal é comum (C-1).
- São estrutura, não parâmetros: `n_ocultos` (que dá a capacidade), `delta_t`, `semente_pesos`, `escala_inicial` e `limite_logit`.

**Unidades:** 28101…28505, K = 4 por base (20 unidades), prefixo `comparacao-cerebros`. Atencioso, 14 dias, o ponto do A da K2 para tudo que é comum.

**Grades, em cadeia (sem grade cruzada): 10 pontos distintos de 12.**

| etapa | parâmetro | grade | fixo | vidas | regra |
|---|---|---|---|---|---|
| B-A | `taxa_ator` | {0,01; 0,03; 0,1} | crítico 0,03, λ 0,8, w0_info 0 | P1 × {casado_frutas, descasado, mutável} × 20 = 60 por ponto → 180 | estabilidade (abaixo) |
| B-B | `taxa_critico` | {0,01; 0,03; 0,1} | o ator da B-A | 120 novas (o 0,03 já rodou) | a mesma |
| B-C | `lambda_elegibilidade` | {0,5; 0,8; 0,95} | ator e crítico escolhidos | 120 novas (o 0,8 já rodou) | a mesma |
| B-D | `w0_info` | {0,5; 1,0; 2,0} (logit) | os três escolhidos | P2 × 3 condições × 20 = 60 por ponto → 180, mais 60 do w0_info 0 como referência descritiva | manipulação (abaixo) |

- **Regra de estabilidade** (a K-4 do A, com o limite do logit no lugar do teto):
  - entre os pontos em que nenhuma vida tem logit aprendido no limite (|z| = 20), o de menor razão da deriva (JSD ao instinto, dia 14 / dia 7), nas três condições juntas;
  - se nenhum escapar do limite, o de menos vidas no limite; o desempate é pela menor razão.
- **Regra de manipulação (K-3):** o menor `w0_info` em que a fração das escolhas de fruta com duas frutas ou mais decididas pela informação (`fruta.sonda.info_decidiu`) passa de 0,069. Se nenhum passar, o de maior fração.

**Total:** ~660 vidas, abaixo do teto da seção 1.4. O teto são as vidas que o A gastar na K2; a K1 estima ~1260.

**Regras e limites:**
- Nenhuma regra usa contraste entre braços nem entre cérebros, nem a `taxa_fruta_ruim`.
- O "não aprende" (seção 7) se confere no piloto.
- **Tempo:** ~1,6 s por vida, abaixo do custo do A; fica abaixo de 4× o tempo da K2 do A.
- **Artefato:** `artifacts_v2_comparacao_cerebros/calibracao_B/`.
- **Risco 2 do plano:** um ator-crítico costuma pedir muitas amostras. No mundo das frutas há 4 a 24 escolhas com duas frutas ou mais por vida, então o "não aprende" pode disparar. O B fica pronto para isso; a regra é a da seção 7.

### 1.2 Adendo do cérebro C (do #176)

**Parâmetros livres: 3 de 4** — `passo`, `teto` e `w0_info`.
- Fixos e iguais aos do A: o ponto fixo (S = 1024), o piso (S/16), a janela de crédito e as recompensas do dono.
- O **ganho** do sinal da consequência é o escolhido para o A na K2: a fonte do sinal é comum (C-1, seção 1.1), então o C não o calibra.
- Os cortes das faixas são estrutura (os limiares do instinto), não parâmetros.

**Unidades:** as da calibração dos cérebros, 28101…28505, K = 4 por base (20 unidades), prefixo `comparacao-cerebros`. Atencioso, 14 dias, ponto do A da K2 para tudo que é comum.

**Grades, em cadeia (sem grade cruzada): 9 pontos de 12.**

| etapa | parâmetro | grade | fixo | vidas | regra de escolha |
|---|---|---|---|---|---|
| C-A | `passo` | {S/32, S/16, S/8} = {32, 64, 128} | teto 4S, w0_info 0 | P1 × {casado_frutas, descasado, mutável} × 20 = 60 por ponto → 180 | a da K-4 (abaixo) |
| C-B | `teto` | {S, 4S, 16S} = {1024, 4096, 16384} | o passo da C-A | 120 novas (o 4S já rodou na C-A) | a mesma |
| C-C | `w0_info` | {S/4, S/2, 3S/4} = {256, 512, 768} | passo e teto escolhidos | P2 × 3 condições × 20 = 60 por ponto → 180, mais 60 do w0_info 0 como referência descritiva | a da K-3 (abaixo) |

- **Regra da K-4 (estabilidade):** entre os pontos em que nenhuma vida tem compartimento no teto, o de menor razão da deriva (JSD ao instinto, dia 14 / dia 7), nas três condições juntas. Se nenhum ponto escapar do teto, o de menos vidas no teto; desempate pela menor razão.
- **Regra da K-3 (manipulação):** o menor `w0_info` em que a fração das escolhas de fruta (com duas frutas ou mais) decididas pela informação passa de 0,069. A medida é a sonda `info_decidiu`. Se nenhum passar, o de maior fração.

**Total:** 480 a 540 vidas, abaixo do teto da seção 1.4. O teto são as vidas que o A gastar na K2, contadas no artefato da K2; a K1 estima cerca de 1260.

**Regras e limites:**
- Nenhuma regra usa contraste entre braços nem entre cérebros, nem a `taxa_fruta_ruim`.
- O "não aprende" (seção 7) se confere no piloto, não aqui.
- **Tempo:** por vida, o C custa o mesmo que o A (~0,4 s por vida de 14 dias com o replay conferido, medição informal nesta máquina, sem artefato). Fica abaixo de 4× o tempo da K2 do A.
- **Artefato:** `artifacts_v2_comparacao_cerebros/calibracao_C/`.


---

## Adendo 2 (2026-10-07, antes da validação): a comparação A × C, a família de dois e o tamanho da amostra

Registrado pelo worker D (tarefa `docs/TAREFA_V2_COMPARACAO_A_C.md`, rodada 13), **depois do piloto e antes de qualquer vida da validação**.

- **Piloto:** `artifacts_v2_comparacao_cerebros/piloto/` (`resumo.json`, `analise.json`, `medidas.json`, `meta.json`, `run.log`); as
  vidas ficam fora do git.
- **Orquestrador:** `experiments/run_v2_comparacao_cerebros.py`.
- **Config:** `experiments/configs/v2_comparacao_cerebros/piloto_ac.json`.

### 2.1 O B sai; o que muda na família (interpretação registrada)

- **O B não fecha** pelo motivo "não aprende" (seção 7): no piloto da calibração dele, a parte aprendida muda 0,0077 [0,0065; 0,0089]
  das decisões do P1 (`docs/RESULTADO_V2_CALIBRACAO_CEREBRO_B.md`; decisão de 2026-10-06 no `REGISTRO_DESVIOS`). O B não roda.
- **Família primária: CC-1 e CC-2.**
  - O que medem: C − A no P1, na `taxa_fruta_ruim` final do descasado e na de depois da troca do mutável.
  - O teste: **Holm de dois**, bilateral, α = 0,05 (passos 0,025 e 0,05).
  - O p bilateral é o do bootstrap das unidades: 2 × a menor cauda das médias reamostradas.
- **CB-1 e CB-2: não testáveis**, porque o B não fecha.
- **Empate** (seção 4 e passo 1 do M6): o IC 90% fica dentro de (−Δ, +Δ).
  - A margem vem antes do teste: uma diferença que passa no Holm, mas fica dentro da margem, é empate.
  - Fora da margem, a leitura é "C melhor" ou "A melhor" só com o Holm; sem ele, é inconclusivo.
  - No passo 1 do M6, inconclusivo conta como empate ("a diferença não passa no Holm").
- **Δ = 0,1986268570547561**, o do adendo 2 do experimento maior (`experiments/configs/v2_experimento_maior/validacao.json`).
- **Secundários** (seção 4, sem o B), descritivos, sem Holm, com a leitura pelo IC 95%:
  - C − A em P1, P2, P2e e P3 nas três condições, fora as duas primárias, cada condição na janela da primária (final no casado e no
    descasado, depois da troca no mutável);
  - os consumos até a metade, no descasado.
- **Descritivos com IC:**
  - a legibilidade;
  - a deriva (P1, dia a dia, e a razão 14/7);
  - o custo (CPU por decisão, bytes de log por dia, estado interno sem os motivos, parâmetros aprendíveis);
  - a divergência acoplada (o C no registro do P1 do A, JSD por dia);
  - o canal de cuidado (cada braço com dono menos o próprio só cuidado);
  - as predições do experimento maior, por cérebro.

### 2.2 Os pontos e as regras que os escolheram

| cérebro | ponto | de onde | regras |
|---|---|---|---|
| A | T3, `g` 512, `w0_info` 256, `w0_pedido` 256, ganho 4; canais ligados, K4, montagem completa | `artifacts_v2_calibracao_conjunta/escolha.json` | K2: A1 (`g`) e C (`w0_info`) fecharam; A2 (`w0_pedido`) e B (ganho) ficaram na reserva (`docs/RESULTADO_V2_CALIBRACAO_CONJUNTA.md`) |
| C | passo 128, teto 4096, `w0_info` 256; o ganho do A (4) | `artifacts_v2_comparacao_cerebros/calibracao_C/escolha.json` | adendo 1.2: C-A e C-B pela estabilidade (K-4), C-C pela manipulação (K-3); as três fecharam (`docs/RESULTADO_V2_CALIBRACAO_CEREBRO_C.md`) |

- **O mundo é o mesmo para os dois, incluído o K4** (o dono do P3 julga a fruta).
- **O C não lê a montagem nem a chave dos canais.** As peças da montagem são do A; no C, os canais são a arquitetura.
- **As vidas do C da calibração ficaram fora do git; o piloto as refez.** Com o mesmo bootstrap, o "não aprende" do C no P1 sai igual ao
  gravado em `calibracao_C/piloto.json`: deriva no dia 14 de 0,02224 e fração decidida pelo aprendido de 0,32447, médias e ICs idênticos.

### 2.3 O piloto (unidades de 28101…28505, K = 4, 20 unidades)

- **O desenho é o da validação inteira**, por unidade e condição:
  - o P0 comum;
  - A e C em P1, P2, P2e e P3;
  - o só cuidado `sem_ensino` de P2, P2e e P3, de cada cérebro;
  - o C no registro do P1 do A, no descasado e no mutável.
- **47 vidas por unidade, 940 no total**, todas rejogadas do disco bit a bit.
- **Tempo:** 1 h 30 (270 s por unidade).
- Nada se escolheu aqui.

| contraste | média C − A | IC 95% | IC 90% | σ²_d | σ_d |
|---|---|---|---|---|---|
| CC-1 (descasado, final) | +0,0124 | [−0,0021; +0,0272] | [+0,0001; +0,0248] | 0,001204 | 0,0347 |
| CC-2 (mutável, depois da troca) | +0,0334 | [+0,0181; +0,0489] | [+0,0206; +0,0463] | 0,001304 | 0,0361 |

### 2.4 O N e as unidades

- **Fórmula** (seção 6.3, bilateral, α' = α / 2 = 0,025, o passo mais exigente do Holm de dois):
  - N = ((z₀,₉₈₇₅ + z₀,₈) σ_d / Δ)² = ((2,2414 + 0,8416) σ_d / 0,1986)²;
  - CC-1 dá 0,29 e CC-2 dá 0,31; os dois arredondam para cima, ao múltiplo de 5, para **5**.
- **Conferência por simulação:** bootstrap das unidades centradas em Δ, teste t no mesmo α' / 2, 2000 réplicas, semente 4242. Dá N = 5,
  com poder 1,0 nos dois contrastes.
- **N da validação = 5** (o maior entre a fórmula e a simulação, ao múltiplo de 5); **K = 1**.
- **Unidades:** `derivar_semente("comparacao-cerebros", b, 0)` e `derivar_semente("comparacao-cerebros-genoma", b, 0)`:

| base | semente | genoma |
|---|---|---|
| 29101 | 1813325358624552102 | 18352371978552326836 |
| 29202 | 10104299035107049184 | 12056934342943575927 |
| 29303 | 4250120258739622145 | 2369633733587340594 |
| 29404 | 3781795229716141642 | 2042150382593049627 |
| 29505 | 3036763020792814318 | 411338248574605006 |

- **Tempo estimado:** 5 × 270 s ≈ **23 min**, 235 vidas, sem os braços do B; abaixo do teto de 12 h.

### 2.5 O que o N = 5 implica (registrado antes, sem mudar a regra)

- **O passo 1 do M6 quase só pode sair empate.** Com Δ = 0,199 e σ_d ≈ 0,035, uma diferença só sai da margem se |C − A| passar de
  ~0,17. O piloto mediu 0,01 e 0,03.
- **O M6 tende a se decidir no passo 2, a legibilidade, em 5 unidades.** No piloto: A 0,255 [0,249; 0,263], C 0,323 [0,318; 0,329],
  C − A +0,068 [+0,062; +0,074].
- **Os secundários e os descritivos ficam com 5 unidades:** ICs largos, só leitura.
- **O N não cresce:** o tamanho sai da família primária (seção 6.3), e nada se ajusta olhando os dados.

### 2.6 Medidas (interpretações registradas)

- **Legibilidade (passo 2 do M6):** a fração das decisões do P1 no descasado em que a **sonda do aprendido** muda a escolha (contrato
  1.1: a escolha com a parte aprendida zerada e o mesmo `u`). A regra é a mesma nos dois cérebros:
  - **no A**, a sonda é o sorteio com os pesos do lobo de impulsos (o prior), conferido decisão a decisão contra o `motivo_lobos`;
  - **no C**, é a sonda gravada no motivo;
  - **"com motivo honesto":** o C não tem a expressão do motivo (o fator), então fica o próprio teste da sonda. A fração do A com fator
    (o G4 da L1) sai ao lado, só descritiva.
- **Custo (passo 4):**
  - CPU por decisão, pelo tempo de `Bancada.vida` (sem o replay e sem as medidas) sobre as decisões, e bytes de log por dia;
  - média por unidade das vidas fechadas (P1 a P3, nas três condições);
  - empate abaixo de 20% nas duas medidas; a máquina fica no `meta.json`.
- **Porte (passo 3):** os dois cérebros têm pesos inteiros e nenhuma função transcendental (nenhum `math` no `lobos.py` nem no
  `cerebro_c.py`): empate.
- **A leitura segue a seção 4 e o M6: a margem antes do teste.** Na primeira versão do orquestrador, o Holm vinha antes da margem; a
  correção foi feita no piloto, antes deste adendo, para seguir o texto do plano.

### 2.7 A validação

- **Uma vez,** com `experiments/configs/v2_comparacao_cerebros/validacao_ac.json` e saída em `artifacts_v2_comparacao_cerebros/validacao/`.
  O orquestrador recusa rodar de novo se a pasta já tem o `resumo.json`.
- **Refazer só por erro de execução,** com sementes novas registradas antes.
- **Faixas que não toca:** a do experimento maior (30101…30505) e a queimada (15101…15505).
