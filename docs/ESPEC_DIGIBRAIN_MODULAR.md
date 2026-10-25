# Especificação técnica do DigiBrain modular (2026-10-25)

**Status:**
- **A direção APROVADA pelo Matheus em 2026-10-25** (o gate da tarefa, `docs/TAREFA_V2_DIGIBRAIN_MODULAR_ESPEC.md`, seção 4), com as
  nove PE "antes" DECIDIDAS pelas recomendações (seção 15) e três correções pedidas por ele, feitas nesta revisão:
  - as cerca de 80 unidades da seção 2 reconciliadas com as ~16 da estimativa da seção 12 (só as unidades de comportamento, seção 2.1);
  - o protótipo implementa **só a memória episódica mínima**; a memória autobiográfica consolidada é **etapa planejada, com critério
    de conclusão**, não resolvida pelo protótipo (seção 9);
  - o candidato `lembranca` **AUTORIZADO** para a v13, Python e TS, atrás da chave, com o gabarito G2 antes da implementação; a v12 e o
    A preservados; a medição do A para o orçamento é pontual e só de desempenho (seções 11 e 12).
- O protótipo (`docs/TAREFA_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md`) começa depois deste documento entrar na `main`, pela etapa 0 (os
  gabaritos e a chave desligada) e pelo plano de análise.
- **O que está decidido** e não se rediscute aqui: a direção modular (2026-10-24) e as DM-1 a DM-9 (2026-10-25), com as condições do
  Matheus (`docs/ARQUITETURA_DIGIBRAIN_MODULAR.md`, seção 13).
- **Todo o resto é PROPOSTO:** os nomes, as formas, as equações, as constantes e a ordem.
  - **Todo número novo é PROPOSTO e SEM FONTE**, mesmo onde a marca não se repete a cada linha. Os valores de partida são postos à mão
    no protótipo; a calibração fica para ele.
  - Nada aqui está implementado, e este documento não traz código.
- **O que não se especifica aqui:** a topologia final, o genoma (só os ganchos dos parâmetros inatos) e a memória autobiográfica
  detalhada, que tem tarefa própria (`docs/TAREFA_V2_MEMORIA_AUTOBIOGRAFICA.md`).

**As marcas de cada peça** (as da arquitetura, seção "Regras deste documento"):
- **[EXISTE]:** está no código da `main`;
- **[MECANISMO]:** mecanismo transferível de uma fonte verificada;
- **[INSPIRAÇÃO]:** fonte de jogo ou de desenho, que não prova arquitetura;
- **[HIPÓTESE]:** aposta nossa, a testar.

As referências são só as verificadas (a skill `literatura-digilab` e as tabelas de `docs/referencias/`), lidas em metadados e resumo,
nunca no texto completo. Onde não há fonte, está escrito SEM FONTE. Nenhuma alegação de novidade.

## 0. Em uma página

**O que o cérebro é:** uma rede pequena de unidades de taxa, inteiras, desenhada à mão em populações, uma por módulo (seção 2).
- **O que cada módulo faz:**
  - o M-SENS codifica o que o pet vê e sente;
  - o M-AFETO lê o corpo químico, devolve a urgência de cada necessidade e modula o resto;
  - o M-ESTADO guarda o que persiste entre decisões (a intenção em curso, a habituação, a frustração);
  - o M-IMPULSO dá a cada comportamento possível, com o seu alvo, uma ativação;
  - o M-ARB escolhe entre todos eles;
  - o M-PLAST muda o que o pet espera de cada coisa e os hábitos dele;
  - o M-MEM guarda onde e quando o pet comeu.
- **O inato** são os pesos de partida das mesmas conexões que a vida muda. Não é uma cascata de regras.

**Como ele vai à comida pelos próprios módulos** (seção 5):
1. o M-SENS marca a ração vista e a proximidade dela;
2. o M-AFETO dá a urgência da fome;
3. o M-IMPULSO soma, para "comer aquela ração":
   - o peso inato fome × proximidade;
   - o incentivo aprendido, que é o alívio previsto do corpo naquele estado;
   - a persistência da intenção;
4. o M-ARB escolhe;
5. o controlador do motor anda, e o pet come;
6. o alívio do corpo volta ao M-PLAST e ao M-MEM.

Sem comida à vista e com fome, as alternativas são duas: ir ao lugar onde já comeu (M-MEM) ou chamar o dono (inato).

**Por que o A no v12 quase não come** (registro MVP-ETAPA2, um diagnóstico; o que segue é leitura do código, sem execução):
- com a fome abaixo de 0,25, o instinto só oferece `chamar_atencao` (`digilab/policy.py:131-134`, "Necessidades que o pet nao
  resolve sozinho: pede ajuda");
- a regra do abandono passa na frente da fome moderada (`policy.py:137-139`);
- o aprendizado do A só repesa os candidatos da regra que disparou (`lobos.py:2342`: o `impulsos` dá os candidatos, e só eles recebem peso);
- a competição V3-3/4 abriria essa disputa, mas não está no jogo.

É a hipótese a conferir no primeiro teste da cadeia (T-CADEIA-0, seção 10).

**Em que o modular não é o A reorganizado** (DM-7; detalhe na seção 8.2):
- nenhuma regra decide quais ações concorrem;
- há estado que persiste entre decisões;
- a química modula a aprendizagem;
- o que se aprende é o valor das coisas vistas, condicionado ao estado do corpo;
- o alvo é escolhido junto com a ação;
- a memória dos lugares entra na decisão.

**O que foi ao Matheus:** a revisão deste documento e as 16 decisões a pesquisar antes de implementar (seção 15), cada uma com a
recomendação e o custo de errar. As nove "antes" estão DECIDIDAS (2026-10-25); as sete "no protótipo" entram com o valor recomendado e
se decidem pela avaliação.

## 1. Convenções

**A aritmética (DM-2):**
- **Todo valor do cérebro é inteiro na escala S.** O inteiro v representa v/S. S = 1024, o do A (`ConfigLobos.bits_ponto_fixo` = 10).
- **O produto:** `mul(a, b) = div_arred(a × b, S)`. O `div_arred` é o do A (`lobos.py:449`): meio longe do zero, com o divisor
  positivo.
- **A ativação:** `φ(v) = clamp(v, 0, A_max)`, linear por partes, com A_max = 4S.
- **Nada de transcendentais nem de float** dentro do pacote. É o critério de porte do C (`cerebro_c.py`, "sem funcoes
  transcendentais") e o que o `tests/test_lobos.py:89-98` exige do A (sem `math`).
- **Referência e espelho:** a referência fica no Python, e o espelho TS com G-PAR (DM-2).
- **A paridade não é evidência de aprendizagem nem de qualidade comportamental.** O G-PAR é um gate de engenharia: diz só que as duas
  implementações fazem a mesma conta. A qualidade se mede pelos testes de mecanismo (seção 10) e pela avaliação do protótipo.
- **O precedente** de redes em aritmética só inteira, com treino, é Jacob et al. (2018), `10.1109/cvpr.2018.00286`, VERIFICADA por título
  e metadados. Sustenta só que pesos em ponto fixo podem ser treináveis, e não a forma desta rede.

**O tempo:**
- **Um passo do cérebro é uma decisão do motor:** Δ = `intervalo_decisao_ticks` = 15 ticks (`config.py:55`). O cérebro não roda entre
  as decisões.
- **Toda constante de tempo** τ está em ticks, com τ ≥ Δ, e vira um ganho por decisão `k = div_arred(S × Δ, τ)`.
- **Um integrador com vazamento** anda assim: `y ← y + mul(k, u − y)`. É a forma de Euler de τ ẏ = u − y.

**A rng:**
- **O cérebro consome só a rng de política** que o motor passa ao `agir`.
- **Uma chamada `rng.random()` por decisão** com dois candidatos ou mais, e nenhuma com um só. É a mesma contagem do A
  (`lobos.py:2361-2365`), para o número de sorteios da vida ser previsível.
- **Nenhum outro módulo sorteia.** Os empates se desfazem por ordem fixa (o tipo, a distância, o id), como os `vistos` do mundo.
- **Se um módulo futuro precisar de acaso próprio,** ele ganha uma rng derivada por `derivar_semente(semente, "digibrain", "<modulo>")`
  (`protocol.py:189`). O protótipo não precisa de nenhuma.
- **O `u` da rng `alvo` do motor** continua sendo sorteado em toda decisão de comer, explorar e brincar (números comuns, `mundo.py:20`).
  O modular o recebe no `escolher_alvo` e o ignora, porque o alvo já foi escolhido no `agir`.

**O registro:**
- **Cada decisão guarda o seu registro** (seção 7), derivado e nunca gravado no log.
- **O log do jogo não muda** (seção 11).

## 2. O substrato neural (a condição da DM-1)

**A condição do Matheus:** "integradores, impulsos e regras de arbitragem, por si só, não bastam para caracterizar o protótipo como
cérebro neural". Esta seção descreve o substrato inteiro:
- as unidades;
- as conexões;
- a ativação;
- a plasticidade;
- como o aprendizado muda o comportamento ao longo da vida.

Ela diz também o que ele **não** é. O que a literatura verificada não sustenta está marcado e vai para a lista da seção 15.

### 2.1 As unidades

São **unidades de taxa:** cada uma tem uma atividade inteira em [0, S] ou [0, A_max], e algumas também o sinal. Não há pulsos.

| população | módulo | unidades (protótipo) | atividade | marca |
|---|---|---|---|---|
| **interocepção** | M-SENS | uma por receptor do corpo presente: a falta `S − leitura` dos cinco de sempre (fome, higiene, energia, humor, saúde) e dos novos que o pet tiver (tédio, curiosidade, solidão, estresse, dor, susto) | [0, S] | [EXISTE] os receptores (`motor_corpo.py:92`); [HIPÓTESE] a população |
| **contexto** | M-SENS | noite, dormindo, tempo sem cuidado (o mesmo corte do A: `min(S, ticks × S / escala)`) | [0, S] | [EXISTE] as entradas do A (`lobos.py:405-410`) |
| **objeto** | M-SENS | uma linha por item dos `vistos` (no máximo `max_vistos` = 8): a classe (ração, fruta a, b, c, podre, bola), a proximidade e a novidade | [0, S] | [HIPÓTESE] |
| **conjunções** | M-SENS | comida à vista (a maior proximidade entre as comidas boas), sem comida (`S − comida à vista`), bola à vista | [0, S] | [HIPÓTESE]; o C já usa conjunções fixas herdadas (`cerebro_c.py`, "fome x fruta presente") |
| **urgência** | M-AFETO | uma por receptor, com a curva inata da necessidade (seção 4.3) | [0, S] | [HIPÓTESE] |
| **afeto** | M-AFETO | valência (com sinal) e excitação | [−S, S]; [0, S] | [HIPÓTESE] |
| **moduladores** | M-AFETO | o ganho da aprendizagem `g_apr` e o ganho da exploração `g_exp` | [0, 2S] | [HIPÓTESE], com o [MECANISMO] de Cliff e Grand (1999) |
| **estado** | M-ESTADO | a força do compromisso `C` com a intenção em curso; a frustração `F`; a habituação por classe de objeto | [0, S] | [HIPÓTESE] |
| **comportamento** | M-IMPULSO | uma por par (comportamento, alvo) possível na decisão: comer cada comida vista ou o cheiro; brincar com a bola ou sem alvo; explorar (vagar, o cheiro ou um lugar lembrado); dormir; chamar o dono; emburrar; ficar ocioso | [0, A_max] | [HIPÓTESE] |

**O tamanho, PROPOSTO:**
- **cerca de 80 unidades** no regime do v12 (corpo do v11 com mundo, sem as árvores), somando todas as populações da tabela;
- **cerca de 20 características de contexto** z (o viés, as urgências, as conjunções, `F`, a valência e a excitação), que entram em
  todos os comportamentos.

**As 80 e as 16 (a reconciliação pedida na revisão de 2026-10-25):** as ~16 unidades da estimativa de operações da seção 12 **são só
as unidades de comportamento** do M-IMPULSO, os pares (comportamento, alvo) da última linha da tabela: no máximo 18 (até 8 "comer" e o
cheiro; "brincar" com a bola ou sem alvo; "explorar" por vagar, pelo cheiro ou pelo lugar lembrado; dormir, chamar, emburrar, ocioso), ~16
no regime típico, com menos itens à vista. **Só elas fazem o produto com as ~20 características** (a equação da seção 2.3). As outras
~64 (interocepção, contexto, objeto, conjunções, urgência, afeto, moduladores, estado) são entradas ou integradores, com uma conta por
unidade e por decisão, e entram na estimativa como os "~20 integradores" e como as características.

### 2.2 As conexões

| de → para | o que é | muda? | tamanho (protótipo) | marca |
|---|---|---|---|---|
| contexto z → comportamento | **os pesos inatos** `W⁰[b, j]` | não: são o inato (o gancho do genoma, seção 4.9) | ≤ 7 comportamentos × ~20 | [HIPÓTESE]; substitui as regras do instinto |
| contexto z → comportamento | **os pesos de hábito** `H[b, j]`, com partida 0 | sim, pela regra P2 | ≤ 7 × ~20 | [MECANISMO] o hebbiano modulado de Cliff e Grand (1999); [HIPÓTESE] a forma |
| objeto → comportamento-com-alvo | proximidade, novidade e incentivo do item o vão à unidade (b, o) | os pesos `W⁰_prox[b]` e `W⁰_nov[b]` não; o incentivo, sim (P1) | por item | [HIPÓTESE] |
| interocepção → modelo do desfecho | `d̂[c, r]`: quanto cada receptor r muda ao comer a classe c | sim, pela regra P1 | 6 classes × até 11 receptores | [EXISTE] o desfecho do `ModeloMundo` (`modelo_mundo.py`), adaptado |
| M-MEM → comportamento "explorar o lugar P" | o valor lembrado do lugar | sim, por episódio (P3) | ≤ N_ep episódios | [HIPÓTESE]; o N6 é o precedente de desenho |
| comportamento escolhido → estado | o compromisso `C` da intenção escolhida volta como viés da mesma unidade na decisão seguinte | não (a constante de tempo é inata) | 1 laço | [HIPÓTESE]: é **a recorrência** do protótipo, pelo estado (seção 3) |
| moduladores → plasticidade e arbitragem | `g_apr` multiplica todo passo de P1 e P2; `g_exp` achata o sorteio | não | difusos | [MECANISMO] "modulação hormonal difusa" (Cliff e Grand 1999); [HIPÓTESE] o que modula o quê |

**A competição** entre as unidades de comportamento é o sorteio proporcional do M-ARB, uma normalização e não uma inibição lateral
explícita. A inibição recorrente entre as unidades é a forma II da seção 3, a pesquisar (PE-5).

### 2.3 A ativação

A ativação da unidade (b, o), o comportamento b com o alvo o (o vazio para os comportamentos sem alvo):

```
a[b,o] = φ(  Σ_j W⁰[b,j] · z_j            inato (contexto e urgências)
           + W⁰_prox[b] · prox_o           inato (aproximar-se do que está perto)
           + W⁰_nov[b]  · nov_o            inato (o novo atrai ou assusta, pelo sinal)
           + G[b,o]                        incentivo aprendido (P1), só comer e brincar com objeto
           + Σ_j H[b,j] · z_j              hábito aprendido (P2)
           + M[b,o]                        memória (M-MEM), só "explorar o lugar P"
           + h[b,o] )                      persistência (M-ESTADO), só a intenção em curso
```

- Cada produto `W · z` é um `mul`.
- **A soma antes do φ é guardada termo a termo:** é o que o motivo por módulo lê (seção 7).
- **Unidade a 0 não concorre.** Se todas ficarem em 0, o pet fica ocioso. É a falha alta do "nada a fazer", registrada.

**O incentivo** (o "querer" de comer o item o, da classe c):

```
G[comer,o] = clamp( div_arred(c_G · valor_previsto(corpo, d̂[c,·]), S_V), 0, G_max ) · prox_o / S
```

- **O `valor_previsto`** é a função do A (`lobos.py:2885`), [EXISTE]: o `sinal_corpo` do estado de agora para o previsto, com
  `D = Σ_d w_d · falta_d²`.
- **Por ser quadrático na falta,** o mesmo desfecho vale mais com o corpo mais necessitado. O incentivo se revaloriza com o estado sem
  reaprender nada, e é isso que o G-T1 do J5 mediu no planejador (seção 8.1).
- **O sustento:**
  - **a recompensa como redução do desvio homeostático:** Keramati e Gutkin (2014), `10.7554/elife.04811`, VERIFICADA, [MECANISMO];
  - **a separação entre querer** (o incentivo G), **gostar** (o paladar, fora do protótipo) **e aprender** (o M-PLAST): Berridge e
    Robinson (1998), `10.1016/s0165-0173(98)00019-8`, e Berridge, Robinson e Aldridge (2009), `10.1016/j.coph.2008.12.014`, VERIFICADAS
    (resumo). Elas sustentam a separação dos três componentes, não a equação.

### 2.4 A plasticidade

São três regras, todas locais, todas em inteiros e todas multiplicadas pelo ganho `g_apr` do M-AFETO.

**P1, o modelo do desfecho** (o quê cada coisa faz ao corpo). Em cada consumo percebido da classe c, para cada receptor r:

```
d̂[c,r] ← d̂[c,r] + mul( mul(g_apr, η_d), Δ_r − d̂[c,r] )
```

- **Δ_r** é a leitura depois de comer menos a da decisão. A energia é corrigida pelo andar previsto, como no `ModeloMundo`.
- **A partida é 0:** o pet não sabe o que nada faz.
- **A única diferença para o `ModeloMundo`** é o ganho `g_apr`. Com `g_apr = S`, é a conta dele.
- [EXISTE], adaptado: o G-T1 passa (0,197 [0,075; 0,323]) e o G-T1-DESF passa (0,177 [0,073; 0,281])
  (`docs/RESULTADO_V2_VALIDACAO_PET_QUE_PENSA_ADENDO8.md`).

**P2, o hábito** (o hebbiano modulado, de três fatores):
- **Na decisão,** a escolhida guarda a elegibilidade `e_j = z_j`, a atividade pré-sináptica do contexto. A pós-sináptica é 1 na unidade
  escolhida e 0 nas outras.
- **Na consequência**, com o sinal homeostático r do M-AFETO, só na linha do comportamento escolhido b*:

```
H[b*,j] ← clamp( H[b*,j] + mul( mul(g_apr, η_h), mul(r_n, e_j) ), −H_max, H_max )
```

- **r_n** é o r normalizado à escala S, `clamp(div_arred(r, R_n), −S, S)`.
- **Não depende da probabilidade da política,** ao contrário da L1 do A. Nenhum outro comportamento muda.
- **O sustento:**
  - [MECANISMO] Cliff e Grand (1999), `10.1162/106454699568683`, VERIFICADA: a rede do norn tem "aprendizado hebbiano e modulação
    hormonal". Sustenta a combinação, não a regra;
  - a regra de três fatores do C é o precedente no código (`cerebro_c.py:33`), com o empate com o A (#197);
  - a elegibilidade e os três fatores, como termos da literatura, estão SEM FONTE (`docs/ARQUITETURA_DIGIBRAIN_MODULAR.md`, seção 10).

**P3, o episódio** (onde e quando; o M-MEM, seção 4.6): cada consumo e cada visita a um lugar lembrado vira um episódio. A recuperação
muda a unidade "explorar o lugar P". Não muda peso nenhum.

**Os limites contra a deriva:**
- **H** fica cortado em ±H_max;
- **d̂** fica em [−S, S] por receptor;
- **o inato** não muda.

Se o hábito precisa ou não de um decaimento lento para o 0 é a PE-10 (SEM FONTE). O G6 da V2 ("nenhum peso preso no teto") vira medida
do protótipo.

### 2.5 Como o aprendizado muda o comportamento ao longo da vida

A trajetória esperada, cada passo com o teste que a confere (seção 10). É **o que a especificação prevê, não um resultado.**

1. **No nascimento,** só o inato vale (d̂ = 0, H = 0, memória vazia):
   - com fome acima do limiar inato e comida à vista, o pet se aproxima;
   - com fome e sem comida, chama o dono;
   - com pouca energia ou de noite, dorme;
   - com tédio, explora (T-IMPULSO-1).
2. **As primeiras refeições** levam o d̂ da ração para o alívio observado. O incentivo G da ração fica positivo e cresce com a fome do
   momento:
   - o pet passa a ir à ração **com menos fome** do que o limiar inato pedia;
   - entre comidas diferentes, prefere a de maior alívio previsto (T-CADEIA-2, T-IMPULSO-2).
3. **Os lugares:** as refeições no comedouro viram episódios. Com fome e sem comida à vista, "explorar o comedouro" ganha peso, e o pet
   vai ao lugar onde o dono costuma pôr a ração (T-MEM-2).
4. **O mundo muda:** uma visita ao lugar lembrado sem comida vira um episódio de valor zero, que passa na frente na recuperação daquele
   lugar. O pet deixa de voltar lá (T-MEM-4).
5. **Os hábitos:** o P2 reforça o comportamento em que o corpo melhorou, no contexto em que ele aconteceu. Por exemplo:
   - dormir de noite depois de comer;
   - chamar o dono com fome e sem comida, se o dono costuma responder pondo comida.

   Nesse segundo caso, **o dono pesa pela consequência no mundo, nunca como recompensa direta** (a D-A e a D-B do
   `docs/PLANO_V2_PESQUISA.md`, seção 3).
6. **As facetas adquiridas** (fora do protótipo; a etapa da memória autobiográfica): os episódios consolidados mudam devagar as
   inclinações do M-PERS, nunca o temperamento inato (DM-6). Aqui entra só o gancho (seção 9).

### 2.6 O que este substrato não é

- **Não tem pulsos, dendritos nem conectividade aprendida:** as populações e as conexões são desenhadas à mão. A estrutura variável e
  a evolução da arquitetura neural ficam fora (a arquitetura, seção 9).
- **Não é uma rede treinada de ponta a ponta:** as três regras são locais, cada uma no seu lugar.
- **É uma rede de taxa pequena,** com uma recorrência só, pelo estado (o compromisso), e modulação difusa.
  - **"Cérebro neural" fica como nome do projeto,** e o documento não promete mais do que isto.
  - Se isto basta para o nome é uma decisão do Matheus (PE-13).
- **A inspiração no Creatures é de desenho:**
  - [INSPIRAÇÃO] Grand, Cliff e Malhotra (1997), `10.1145/267658.267663`: a rede, a bioquímica e o genoma juntos;
  - [MECANISMO] só o hebbiano com modulação hormonal de Cliff e Grand (1999);
  - o manual, a wiki e o openc2e são pista, nunca "o Creatures faz X";
  - o NORNBRAIN só se estuda (DM-9).

## 3. As formas do estado dinâmico (DM-1)

| | **forma I: integradores com vazamento (a do protótipo, DM-1)** | **forma II: rede recorrente de taxa (a comparar só se a I não bastar)** |
|---|---|---|
| **a equação** | por variável: `y ← y + mul(k, u − y)`, com `k = div_arred(S·Δ, τ)`. Sem acoplamento entre as variáveis, fora o compromisso, que volta como viés (seção 2.2) | `y ← y + mul(k, φ_s(W_rec·y + W_in·u + b) − y)`, com φ_s uma sigmoide dura em inteiros (`clamp(S/2 + v/4, 0, S)`). É a discretização de Euler de uma rede recorrente de tempo contínuo |
| **a variante com portas** (do tipo CfC) | — | `y ← mul(σ_f, y) + mul(S − σ_f, h)`, com `σ_f = φ_s(W_f·[y,u])` e `h = φ(W_h·[y,u])`: a porta decide quanto do estado fica. A forma fechada do CfC (Hasani et al. 2022) usa a exponencial; aqui ela vira a porta dura, sem transcendentais. **É [HIPÓTESE] e CORPUS:** o CfC e o NCP são pista, e **as licenças do software não foram conferidas** (DM-9: conferir antes de qualquer reúso) |
| **onde mora** | M-SENS (a habituação), M-AFETO (a valência, a excitação), M-ESTADO (`C`, `F`) | o mesmo estado, num vetor só, com `W_rec` aprendível ou fixo |
| **o custo por decisão** | O(n) produtos, n ≈ 20 variáveis | O(n² + n·m) produtos; com n = 20 e m = 40, cerca de 1 200. A variante com portas, o dobro |
| **a paridade** | trivial (somas e produtos inteiros) | exata em inteiros, se φ_s for linear por partes; **não** em float (o B só reproduzia no mesmo runtime) |
| **o que se testaria** | a resposta ao degrau (T-ESTADO-1); a meia-vida igual à da tabela; a persistência da intenção sem oscilar (T-ESTADO-2) | a estabilidade (o estado limitado com a entrada limitada); a memória de trabalho de k decisões numa tarefa de atraso; e se a ablação da recorrência muda o comportamento |
| **o risco** | pouca expressividade: sem interação entre as variáveis, o estado não guarda sequências | o B (CfC com ator-crítico, em float) **não aprendeu** (0,0077 das decisões, `docs/RESULTADO_V2_CALIBRACAO_CEREBRO_B.md`); mais parâmetros para calibrar |

**Quando passar da I para a II** (o gatilho, PROPOSTO): um teste de mecanismo do M-ESTADO, ou uma ablação do protótipo, mostra uma
dependência temporal que a forma I não expressa nem com os parâmetros postos à mão (o D3 de `docs/TAREFA_V2_CEREBRO_A_BASELINE.md`).
Por exemplo:
- a intenção oscila entre dois alvos;
- o pet não guarda que acabou de visitar um lugar vazio.

Sem o gatilho, a forma II não entra. É a PE-8.

**Sem fonte verificada no repositório:** os integradores com vazamento e as redes recorrentes de tempo contínuo como modelo neural.
Os dois ficam [HIPÓTESE] de desenho (PE-1).

## 4. O contrato de cada módulo

Cada módulo é um contrato, não um arquivo nem uma rede (a arquitetura, seção 2). **No protótipo**, cada um fica no seu arquivo, num
pacote próprio (por exemplo `digilab/digibrain/`), atrás de uma chave, com o A e o `engine.py` intactos.

O formato de cada contrato:
- as entradas;
- o estado;
- as saídas;
- a atualização;
- a rng;
- a aritmética;
- o que vai ao registro da decisão.

### 4.1 M-ADAPT, o adaptador cérebro-corpo-motor

| campo | contrato |
|---|---|
| **entradas** | do motor: a `Observacao` no `agir(obs, rng)`; os candidatos a alvo no `escolher_alvo(acao, candidatos, percepcao, u)`; a consequência no `consequencia_mundo(acao, ocorrido, obs_depois)` e no `consequencia_corpo(...)`; os gestos no `receber_acao_dono(acao, tick)`; a `Transicao` no `observar` |
| **estado** | a intenção escolhida no `agir`, à espera do `escolher_alvo` e da consequência; uma pendência por decisão |
| **saídas** | a `AcaoPet` do `agir`; o alvo do `escolher_alvo`, **que tem de estar entre os candidatos do motor** (senão, `raise`); o `estado_interno()` com o estado de todos os módulos; o `ultimo_motivo` |
| **atualização** | encaminha a Observação ao M-SENS e ao M-AFETO; a consequência ao M-AFETO (o r), ao M-PLAST, ao M-MEM e ao M-ESTADO |
| **rng** | repassa a do `agir` ao M-ARB; ignora o `u` do `escolher_alvo` |
| **aritmética** | nenhuma conta própria |
| **registro** | a pendência e o alvo entregue |

**As falhas altas** (o padrão do A, `lobos.py:2318-2330`): `raise` quando:
- a Observação chega sem `corpo` ou sem `mundo`;
- uma decisão fica sem o gancho de consequência;
- o alvo escolhido não está entre os candidatos.

[EXISTE] o `Protocol` `Politica` (`policy.py:81`) e os ganchos do A. **O lugar lembrado** pede ao motor um tipo de candidato novo, o
`lembranca` no `explorar`, atrás da chave. É uma mudança no `mundo.py` e no TS, não no `engine.py` (PE-14).

### 4.2 M-SENS, a codificação sensorial

| campo | contrato |
|---|---|
| **entradas** | `obs.corpo` (a `PercepcaoCorpo`, os receptores na escala S); `obs.mundo` (a `PercepcaoMundo`: a posição, a região, os `vistos` (id, tipo, dx, dy, d), o cheiro, a direção dele, o alvo pendente); do `vetor_estado`, **só** a hora e o dormindo, que não são químicos; o `ticks_desde_cuidado` |
| **estado** | a habituação por classe de objeto, `hab[c]` ∈ [0, S] |
| **saídas** | a interocepção (a falta por receptor, pelas funções do A `falta_receptor` e `leitura_receptor`, `lobos.py:2812-2835`); o contexto; as linhas de objeto (classe, `prox_o`, `nov_o`); as conjunções |
| **atualização** | `prox_o = clamp(S − div_arred(d_o · S, R), 0, S)`, com R o raio da visão na unidade de `d`. Para cada classe: `hab[c] ← hab[c] + mul(k_hab, visto_c · S − hab[c])`, com `visto_c` = 1 se a classe está nos `vistos`. `nov_o = S − hab[classe(o)]` |
| **rng** | nenhuma |
| **aritmética** | inteira |
| **registro** | as linhas de objeto, as conjunções e a novidade |

**A G-RECEPTOR fica:** o M-SENS só lê a Observação. Nenhum arquivo do pacote importa `digilab/corpo.py` (conferido pela AST, como em
`tests/test_corpo.py:329`).

### 4.3 M-AFETO, os afetos e os moduladores

| campo | contrato |
|---|---|
| **entradas** | a interocepção do M-SENS; na consequência, os receptores de antes e de depois |
| **estado** | a valência `V` ∈ [−S, S] e a excitação `E` ∈ [0, S], integradores (forma I); os receptores da decisão, guardados para o r |
| **saídas** | as urgências `u_r`; o sinal homeostático `r` da consequência; os ganhos `g_apr` e `g_exp` |
| **atualização** | ver abaixo |
| **rng** | nenhuma |
| **aritmética** | inteira |
| **registro** | as urgências, `V`, `E`, `g_apr`, `g_exp` e o `r` da consequência anterior |

**A atualização:**
- **a urgência:** `u_r = clamp(mul(a_r, falta_r) + mul(b_r, max(0, falta_r − λ_r)), 0, S)`. É uma curva linear por partes que sobe
  mais depressa acima do limiar λ_r. Os a_r, b_r e λ_r são inatos, ganchos do genoma;
- **o sinal homeostático:** `r = sinal_corpo(antes, depois, drives, ganho, S)` (`lobos.py:2897`), [EXISTE]. Os canais por drive saem
  do `sinal_corpo_canais`, com a soma telescópica igual ao escalar (K-6);
- **a valência:** `V ← V + mul(k_V, r_n − V)`;
- **a excitação:** `E ← E + mul(k_E, max(|r_n|, dor, susto, estresse) − E)`;
- **o ganho da aprendizagem:** `g_apr = clamp(g₀ + mul(β_E, E), g_min, g_max)`;
- **o ganho da exploração:** `g_exp = clamp(e₀ + mul(β_T, falta_tedio) − mul(β_U, max_r u_r), 0, e_max)`.

**O que entra no protótipo:** a modulação do `g_apr` pela química entra **atrás de uma subchave, desligada no primeiro braço**
(`g_apr = g₀` constante). A avaliação a compara com os controles do V3 (`docs/futuro/digibrain_v3_e0.md`, seção 4):
- **o embaralhado:** a química de outra vida;
- **o constante:** o passo fixo na média.

Sem isso, "modular" não se separa de "aprender mais depressa em média" (PE-4).

**O sustento:**
- [MECANISMO] a modulação química da aprendizagem: Cliff e Grand (1999);
- a excitação que modula a consolidação, McGaugh (2005), `10.1101/lm.93405`: VERIFICADA só pelo título, [HIPÓTESE];
- o prazer que melhora a viabilidade: Lewis e Cañamero (2016), `10.1177/1059712316666331`, VERIFICADA (resumo), [MECANISMO] para o
  M-AFETO em geral, não para estas equações.

### 4.4 M-ESTADO, o estado dinâmico

| campo | contrato |
|---|---|
| **entradas** | a intenção escolhida pelo M-ARB; a distância ao alvo antes e depois; a consequência (chegou, comeu, o alvo sumiu) |
| **estado** | a intenção em curso `I* = (b, o)` ou nenhuma; a força do compromisso `C` ∈ [0, S]; a distância anterior; as decisões seguidas sem progresso `n_sp`; a frustração `F` ∈ [0, S] |
| **saídas** | a persistência `h[b,o] = mul(w_pers, C)`, só para `I*`; `F`, como característica de contexto |
| **atualização** | ver abaixo |
| **rng** | nenhuma |
| **aritmética** | inteira, forma I |
| **registro** | `I*`, `C`, `n_sp`, `F` e o motivo do fim da intenção |

**A atualização:**
- **escolheu `I*` de novo:** `C ← C + mul(k_C, S − C)`;
- **escolheu outra:** `I* ←` a nova, com `C ← mul(k_C, S)`;
- **sem progresso:** `n_sp += 1`. Com `n_sp ≥ N_desiste`, ou com o alvo fora dos `vistos` e sem cheiro, a intenção acaba com `C = 0`;
- **acabou com a meta** (comeu, ou chegou ao lugar): `C = 0`;
- **acabou sem a meta:** `F ← F + mul(k_F, S − F)`. A cada decisão, `F ← F − mul(k_F', F)`.

**A intenção como opção:** a intenção que dura várias decisões é uma opção no sentido de Sutton, Precup e Singh (1999),
`10.1016/s0004-3702(99)00052-1`. VERIFICADA por título e metadados, [MECANISMO]: o formalismo de abstração temporal, não esta regra.

### 4.5 M-IMPULSO, os impulsos e os circuitos de comportamento

| campo | contrato |
|---|---|
| **entradas** | o contexto z (do M-SENS, do M-AFETO e do M-ESTADO); as linhas de objeto; o incentivo G (do M-PLAST); o termo M (do M-MEM); a persistência h (do M-ESTADO) |
| **estado** | nenhum (os pesos ficam no M-PLAST e no inato) |
| **saídas** | a lista das unidades (b, o) com a ativação `a[b,o]` e os termos da soma |
| **atualização** | a equação da seção 2.3 |
| **rng** | nenhuma |
| **aritmética** | inteira |
| **registro** | todas as unidades com os termos (inato, incentivo, hábito, memória, persistência) |

**As unidades possíveis** (o protótipo usa as sete ações de `ACOES_PET_HOJE`, sem ação nova):
- **comer:** um alvo por comida vista; e o cheiro, se houver direção;
- **brincar:** com a bola vista, ou sem alvo;
- **explorar:** vagar; o cheiro; um lugar lembrado;
- **sem alvo:** dormir, chamar o dono, emburrar, ficar ocioso.

**Os sinais dos pesos inatos `W⁰`** (os valores, PROPOSTOS, ficam no protótipo; os testes conferem os sinais):

| comportamento | + (puxa) | − (empurra) |
|---|---|---|
| comer o item o | urgência da fome; proximidade; comida boa | podre (pelo `W⁰` da classe); a saciedade |
| chamar o dono | urgência da fome × sem comida; urgência da higiene; tempo sem cuidado | comida à vista |
| dormir | urgência da energia; noite; dormindo | urgência da fome alta |
| explorar | tédio; curiosidade; frustração; sem comida com fome moderada | urgência da energia |
| brincar | bola à vista; tédio; humor | urgência da fome e da energia |
| emburrar | tempo sem cuidado × humor baixo | — |
| ocioso | viés pequeno | qualquer urgência |

**Essas relações traduzem a intenção das sete regras do instinto** (`policy.py:117-149`) **em pesos de partida.** Duas diferenças, de
propósito:
1. **com fome e comida à vista, comer vence chamar;**
2. **nenhuma regra corta as outras:** todas as unidades concorrem sempre.

**A única exceção é o reflexo de segurança:** com a energia abaixo do limiar inato, dorme. Ele fica fora do sorteio (seção 4.7), como o
`sono_exaustao` ficou fora da disputa na V3-4 (`lobos.py:349`).

**O sustento:**
- [MECANISMO] as arquiteturas por comportamentos: Brooks (1986), `10.1109/jra.1986.1087032`; Bryson (2003),
  `10.1007/3-540-36559-1_7`. VERIFICADAS por título e metadados;
- [MECANISMO] quais ações cabem em quais estados (as *affordances*): Khetarpal et al. (2020), arXiv:2006.15085, VERIFICADA;
- a curva das urgências e os sinais da tabela estão SEM FONTE.

### 4.6 M-MEM, a memória mínima (episódios de alimentação)

| campo | contrato |
|---|---|
| **entradas** | na consequência: a posição (célula), a região, a classe comida (ou "não havia"), as variações dos receptores, o r, a hora e a fome antes; o tick do relógio do pet |
| **estado** | até N_ep episódios, cada um com (tick, lugar, região, classe, Δ receptores, r, hora, fome antes, origem: consumo ou visita) |
| **saídas** | no máximo um episódio recuperado, com o id; o termo `M[explorar, P]` do lugar P dele |
| **atualização** | ver abaixo |
| **rng** | nenhuma; os empates se desfazem por tick e depois por lugar |
| **aritmética** | inteira |
| **registro** | a pista, o episódio recuperado (id, lugar, r) ou nenhum, e o episódio codificado |

**A atualização:**
- **a codificação:**
  - todo consumo vira episódio (os consumos são poucos por dia; ME-1 decide o limiar na tarefa da memória);
  - toda chegada a um lugar lembrado vira episódio, com r = 0 e classe "não havia" se não havia comida;
  - **cheio**, sai o episódio de menor |r|, e no empate o mais antigo.
- **a recuperação:**
  - **a pista:** a urgência da fome acima do limiar de busca, e nenhuma comida boa à vista;
  - **o valor de cada lugar** é o r do episódio **mais recente** naquele lugar. A visita vazia derruba o lugar;
  - volta o lugar de maior `mul(valor, S − div_arred(dist · S, D_max))`, se esse valor for positivo;
  - o termo `M[explorar, P]` é `mul(w_mem, valor)`.

**O sustento:**
- [MECANISMO] um módulo de memória episódica por cenas acoplado a uma criatura: Castro e Gudwin (2013), `10.4018/jse.2013010102`,
  VERIFICADA. **Sem** afirmar que a cena recuperada informa a escolha: a tabela não sustenta isso;
- **a regra "o mais recente do lugar manda"** é escolha nossa, SEM FONTE. Os sorteios do *Dwarf Fortress* (NÃO VERIFICADA EM FONTE
  PRIMÁRIA) não entram.

O gancho da memória consolidada está na seção 9.

### 4.7 M-ARB, a arbitragem

| campo | contrato |
|---|---|
| **entradas** | as unidades (b, o) com `a[b,o]`; o `g_exp`; a interocepção (para o reflexo) |
| **estado** | nenhum |
| **saídas** | a intenção escolhida (b*, o*) e o `u`; as sondas por módulo (seção 7) |
| **atualização** | ver abaixo |
| **rng** | a de política: uma chamada com dois candidatos ou mais, nenhuma com um só ou com o reflexo |
| **aritmética** | inteira; o `u` é o float de `rng.random()`, como no A, e o alvo do sorteio vira inteiro antes da busca |
| **registro** | o reflexo (se disparou), os pesos `w`, o `u`, a escolha e as sondas |

**A atualização:**
1. **o reflexo:** se a leitura da energia está abaixo de `λ_sono`, a escolha é dormir, sem sorteio;
2. **o peso de cada unidade:** `w[b,o] = a[b,o] + mul(g_exp, ε)` para as unidades com `a > 0`. O ε achata o sorteio quando o tédio sobe
   e o estreita quando a urgência sobe;
3. **o sorteio:** com a soma inteira `T = Σ w`, o alvo é `int(u × T)`, e a escolha é a primeira unidade cuja soma acumulada passa dele.
   Na ordem fixa: comportamento, depois a ordem dos `vistos`. É a conta do `sortear` do A (`lobos.py:433`), feita em inteiros.

**Escolhas ainda abertas:**
- **o sorteio proporcional (a regra de Luce)** fica no protótipo para manter a contagem da rng e a sonda com o mesmo `u`;
- **um acumulador com inibição mútua,** recorrente, é a alternativa da PE-5.

**O sustento:**
- [MECANISMO] o aprendizado localizado por módulo sob um portão: Jacobs et al. (1991), `10.1162/neco.1991.3.1.79`, VERIFICADA. Aqui
  não há portão aprendido, e a referência fica só como o precedente, não como o desenho;
- a competição aberta com aprendizado ajudou no A (#396, seção 8.1). É evidência do projeto, não da literatura.

### 4.8 M-PLAST, a plasticidade

| campo | contrato |
|---|---|
| **entradas** | na consequência: o r (do M-AFETO); os receptores de antes e de depois; a classe comida; a elegibilidade guardada na decisão; o `g_apr` |
| **estado** | o modelo do desfecho `d̂[c, r]`; os pesos de hábito `H[b, j]`; a elegibilidade da intenção em curso |
| **saídas** | o incentivo `G[b, o]` para o M-IMPULSO; os registros das atualizações |
| **atualização** | P1 e P2 (seção 2.4). **O crédito:** a elegibilidade é a do começo da intenção, aplicada quando ela acaba (com a meta ou sem ela), e não uma janela de K decisões (seção 8.1, o traço) |
| **rng** | nenhuma |
| **aritmética** | inteira |
| **registro** | cada atualização: a regra, o índice, o antes, o depois e o r |

### 4.9 Os ganchos que ficam vazios no protótipo: M-PERS, M-GEN e M-EXPR

- **M-GEN:** todo parâmetro inato fica num registro só, `ParametrosInatos`, por módulo:
  - o `W⁰`, o `W⁰_prox` e o `W⁰_nov`;
  - as curvas `a_r`, `b_r` e `λ_r`;
  - as constantes de tempo;
  - os passos η e os ganhos β;
  - o `λ_sono`.

  **O genoma futuro** escreve esse registro (`docs/futuro/ecossistema_genetico.md`; a arquitetura, seção 9). **O aprendido nunca entra
  nele** (a EG-5). No protótipo, o registro é uma constante PROPOSTA.
- **M-PERS:** a interface `faceta(nome) -> int` e `mudar_faceta(nome, passo, episodios)`:
  - cada mudança guarda os ids dos episódios que a causaram;
  - **o temperamento inato fica fora do alcance dela** (DM-6);
  - no protótipo não há faceta, e a interface devolve o neutro.
- **M-EXPR:** lê só o registro da decisão (seção 7). Fica fora do cérebro e não decide nada.

## 5. A ida à comida, passo a passo

**O cenário:** o MVP, o pet do v12 no layout sem árvores, a ração posta pelo jogador.

| passo | módulo | o que acontece | o que o registro guarda |
|---|---|---|---|
| 1 | M-ADAPT → M-SENS | a ração entra nos `vistos` a d células: a linha de objeto (ração, `prox`, `nov`); "comida à vista" sobe | a linha e a conjunção |
| 2 | M-AFETO | a falta da fome dá a urgência `u_fome` | `u_fome`, `g_exp` |
| 3 | M-PLAST → M-IMPULSO | o incentivo `G[comer, ração]` sai do d̂ da ração e da falta de agora (0 antes da primeira refeição) | o G |
| 4 | M-IMPULSO | `a[comer, ração]` = o inato (fome × proximidade) + G + hábito + persistência; `a[chamar]` cai com a comida à vista | os termos de cada unidade |
| 5 | M-ARB | o sorteio escolhe (comer, ração) | os pesos, o `u` e as sondas |
| 6 | M-ESTADO | `I*` = (comer, ração), com o compromisso C | `I*`, C |
| 7 | M-ADAPT → motor | `agir` devolve `comer`; o `escolher_alvo` devolve a ração (que está nos candidatos); o controlador anda (alcance de 60 subunidades por decisão, `config.py:1745`) | o alvo entregue |
| 8 | motor | chegou: come; a fome cai | — |
| 9 | M-AFETO, M-PLAST, M-MEM, M-ESTADO | o r positivo; P1 move o d̂ da ração; P2 reforça comer no contexto da decisão; o episódio (comedouro ou lugar, ração, r) entra na memória; a intenção acaba com a meta | as atualizações e o episódio |

**Se a ração estiver longe,** a intenção persiste por h e o pet anda decisão a decisão. **Se ela sumir antes,** a intenção acaba sem a
meta, e F sobe.

**Sem comida à vista e com fome:**
- "explorar o lugar lembrado" concorre (M-MEM);
- "chamar o dono" concorre (inato, fome × sem comida);
- "explorar, vagar" concorre (tédio, F).

**A diferença para o A está no passo 4:** no A, com a fome abaixo de 0,25, o passo 4 não existe. A regra do pedido deixa só chamar o
dono (seção 0).

## 6. A ligação do corpo

**Os receptores em cada módulo:**

| receptor (`PercepcaoCorpo`) | M-SENS | M-AFETO | M-IMPULSO (pela urgência) | M-PLAST |
|---|---|---|---|---|
| fome | falta | urgência; parcela do r | comer, chamar, dormir (−) | Δ no desfecho; r |
| higiene | falta | urgência; parcela do r | chamar | r |
| energia | falta | urgência; o reflexo do sono | dormir, explorar (−), brincar (−) | Δ (corrigido pelo andar); r |
| humor | falta | urgência; parcela do r | brincar, emburrar | r |
| saúde | falta | urgência; parcela do r | (nenhum peso inato no protótipo) | Δ; r |
| tédio, curiosidade | falta | urgência; o `g_exp` (o tédio) | explorar, brincar | r (os canais dos drives novos) |
| solidão, estresse | falta | urgência; a excitação (o estresse) | chamar | r |
| dor, susto | concentração | a excitação (o susto fica fora do r, como no A, `lobos.py:220`) | (nenhum peso inato no protótipo) | r (a dor) |
| vontade, conforto; olfato e audição pelos órgãos | — | — | — | fora do protótipo (o banheiro não está no v12; os órgãos não têm cérebro que os leia, `docs/DEFINICOES_CORPO_V2.md`, seção 7.1) |

**Os ganhos que o M-AFETO dá:**
- **ao M-PLAST:** o `g_apr`, que multiplica os passos de P1 e P2, pela excitação, atrás da subchave (seção 4.3);
- **ao M-ARB:** o `g_exp`, que achata o sorteio com o tédio e o estreita com a urgência.

**A G-RECEPTOR fica:** o cérebro só lê `obs.corpo`, `obs.mundo`, a hora, o dormindo e o tempo sem cuidado. Os testes de hoje continuam
valendo:
- mudar um químico sem receptor não muda a observação;
- nenhum arquivo do pacote importa `digilab/corpo.py`;
- a política não tem referência ao objeto do corpo.

O G-SEM-DIRECAO também fica.

## 7. O motivo por módulo

**O registro de cada decisão** (o `ultimo_motivo`, derivado e nunca gravado no log):

```
{ "unidades": [ {b, o, "termos": {inato, prox, nov, incentivo, habito, memoria, persistencia}, a, w}, ... ],
  "reflexo": bool, "u": float | None, "escolha": (b*, o*),
  "afeto": {u_r..., V, E, g_apr, g_exp}, "estado": {I*, C, n_sp, F},
  "memoria": {"pista": bool, "recuperado": id | None, "lugar": P, "valor": int},
  "sondas": { "sem_incentivo": (b,o), "sem_habito": (b,o), "sem_memoria": (b,o), "sem_persistencia": (b,o),
              "sem_afeto": (b,o), "so_inato": (b,o),
              "<modulo>_decidiu": bool para cada um } }
```

**A sonda "quem decidiu"** generaliza a do A (`lobos.py:2288`; a da competição, `lobos.py:2446-2467`):
- refaz os pesos com o termo de um módulo zerado (o afeto: com o `g_exp` neutro) e sorteia com **o mesmo `u`**;
- o módulo decidiu se a escolha muda;
- são seis refeitas por decisão, só de leitura: não mudam peso, motivo nem rng.

**A medida de influência por módulo** é a fração de decisões com `<modulo>_decidiu`, como no E0 do V3 (`docs/futuro/digibrain_v3_e0.md`:
"o aprendido decide 15,6% das decisões"). **Ela não é a ablação:** a ablação desliga o módulo a vida inteira, e a sonda mede uma decisão.

**A fidelidade da fala** (o M-EXPR; a etapa M6 da memória):
- "lembrei de X" só com `memoria.recuperado` = X naquela decisão;
- "fiz Y porque lembrei de X" só com `memoria_decidiu` verdadeiro;
- "fiz Y porque estava com fome" só com a urgência da fome entre os termos que, zerados, mudariam a escolha.

Um teste falha se a fala alega o que o registro não tem (T-MOTIVO-2). Isso fecha, para o modular, as três lacunas da auditoria (seção 4):
- o prompt `livre-v6`;
- o verificador que aceita a causa por memória;
- o motivo do N6.

## 8. As peças do A, uma a uma (DM-7)

### 8.1 A decisão de cada peça

| peça do A | o que é | evidência | decisão | o que entra no modular |
|---|---|---|---|---|
| **o instinto** (as 7 regras em cascata, `policy.py:117-149`, e o `impulsos`, `lobos.py:321`) | a primeira regra que vale decide quais ações concorrem; os candidatos são os dela | 55,3% das decisões têm um candidato só, e o aprendido decide 15,6% (`docs/futuro/digibrain_v3_e0.md`, §1); com fome < 0,25, só chamar (`policy.py:131-134`); o A, o B e o C herdam a mesma cascata (o C-1, `cerebro_c.py`); no mundo, o A que aprende perde do instinto (o J1, P0 − P1, −0,0097 [−0,0149; −0,0046], `docs/RESULTADO_V2_VALIDACAO_MUNDO.md`) | **ADAPTAR o conteúdo; DEIXAR a forma** | a intenção de cada regra vira sinal de peso inato `W⁰` (seção 4.5); a cascata sai. O reflexo do sono (o `sono_exaustao`) fica, fora do sorteio |
| **a L1** (o gradiente de log p(a*) com o sinal no lugar da vantagem, `lobos.py:459-485`) | aprende uma tabela (regra, ação, entrada) dentro dos candidatos da regra | os G3 a G6 falham (o G3, 0,041 bit [0,026; 0,062] contra o alvo de 0,10, `docs/RESULTADO_V2_L1.md`); o controle sem lobos, com a mesma capacidade, diverge mais (0,113 bit); o alvo aprendido atrapalha (−0,0063 [−0,0105; −0,0022], `docs/RESULTADO_V2_VALIDACAO_MUNDO_ALVO.md`) | **DEIXAR como regra do protótipo** | nada da regra. A infraestrutura inteira fica (o `div_arred`, o `arred`, o corte no teto). Como a falha pode ser da cascata e não da regra, a L1 pode voltar como braço de comparação do P2 (PE-2) |
| **o traço de elegibilidade** (K decisões com λ^k, `lobos.py:1474-1500`) | o crédito volta às K decisões anteriores | ligado, piora o que se quer medir: Δ M1 de −0,018 a −0,020 com IC abaixo de 0; no P3, o acerto cai de −0,046 a −0,124 (`docs/RESULTADO_V2_REVISAO_APRENDIZ.md`, R3: "fica desligado") | **DEIXAR** | o crédito vai à decisão que **começou** a intenção, quando ela acaba (seção 4.8): um passo de crédito por opção, e não uma janela cega (PE-3) |
| **o planejador** (o `ModeloMundo`: o desfecho, o custo de andar, o mapa; o termo `g_plano`) | prevê o efeito de comer cada tipo e soma um termo em comer e explorar | o G-T1 passa (0,197 [0,075; 0,323]); o G-T1-DESF passa (0,177 [0,073; 0,281]); o G-T1-CONG não passa (0,103 [0,000; 0,207]); o mapa não foi testado (o T2 não mediu) (`docs/RESULTADO_V2_VALIDACAO_PET_QUE_PENSA_ADENDO8.md`) | **REAPROVEITAR o desfecho e o custo de andar; DEIXAR o mapa** | o desfecho vira o P1, com o `g_apr`, e o incentivo vira `valor_previsto` sobre ele (seção 2.3). O mapa sai: o lugar da comida passa a ser o M-MEM, com o mapa como braço de comparação, se servir |
| **a disputa** (V3-3/4, a competição das regras urgentes com o κ, `lobos.py:345-399, 2411-2467`) | abre a escolha entre as regras urgentes que valem | o G-R1 passa: 0,0124 [0,0093; 0,0156]; o G-R1-CONG passa: 0,0113 [0,0086; 0,0140]; "abrir sem aprender fica perto do R0" (`docs/RESULTADO_V2_VALIDACAO_COMPETICAO.md`) | **ADAPTAR** | a ideia que deu certo (todas as propostas concorrem, e o aprendido pesa) vira a forma nativa do M-ARB, sem regra que abra ou feche. O κ vira o inato. Ficam: o sorteio com um `u`, o reflexo fora da disputa e a sonda "abertura decidiu, aprendido decidiu" |
| **o N6** (a `MemoriaEpisodios`, `lobos.py:582-625`) | episódios de fruta comida; recuperação pela fruta presente | o G-CAUSAL é +0,028 [+0,009; +0,048], efeito pequeno (`docs/RESULTADO_V2_VALIDACAO_UNICA.md`); desligado por padrão; fora do jogo | **ADAPTAR** | o desenho (os espaços curtos e longos, a recuperação por pista, os controles de recência e embaralhado) é o precedente do M-MEM e da validação REL/SEM/REC/EMB. A pista muda (o contexto: fome, nada à vista, o lugar), e o que a lembrança muda também (o lugar a explorar, não a fruta a escolher) |
| (fora da lista da DM-7) a `MemoriaEmocao` | contadores | a contribuição é sempre 0 (`lobos.py:516-547`) | **DEIXAR** | nada |
| (fora da lista) os canais | o sinal por drive | o `_sensibilidade_canal` devolve sempre S; sem efeito visível na ablação (`docs/RESULTADO_V2_VALIDACAO_UNICA.md`, §2) | **REAPROVEITAR as funções** | o `sinal_corpo`, o `sinal_corpo_canais`, o `valor_previsto` e o `falta_receptor` são a interface do corpo do M-AFETO e do M-PLAST, importados sem mudar o `lobos.py` |

**O reaproveitamento é por importação:** o `lobos.py` não muda, e o A fica intocado.

### 8.2 Em que o modular não é o A reorganizado

Cada linha é uma diferença **testável**: o teste da última coluna passa no modular e falha no A por construção, e o A falhar nele é a
confirmação esperada.

| | o A | o modular | o teste que separa |
|---|---|---|---|
| **quem concorre** | a primeira regra que vale decide os candidatos; 55,3% das decisões têm um só | todas as unidades concorrem sempre; só o reflexo do sono fica fora | T-IMPULSO-1: com fome alta e ração à vista, comer tem peso > 0 (no A, com fome < 0,25, não tem) |
| **o estado entre decisões** | nenhum: cada decisão parte do zero; o "continuar" é do motor | o compromisso, a frustração, a habituação, a valência e a excitação persistem e decaem | T-ESTADO-2: a intenção persiste até a meta e acaba quando o alvo some |
| **a química na aprendizagem** | o passo é fixo; o R3 do V3 nunca foi construído | o `g_apr` multiplica todo passo (atrás da subchave, com os controles) | T-PLAST-3: o passo dobra com o `g_apr` dobrado |
| **o que se aprende** | pesos por (regra, ação, entrada), dentro dos candidatos | o desfecho de cada classe de coisa (o incentivo, revalorizado pelo estado) e os hábitos por contexto, em todos os comportamentos | T-CADEIA-2: depois de comer, a ração atrai com menos fome do que o limiar inato pedia |
| **o alvo** | separado da ação; o alvo aprendido atrapalhou | a unidade é o par (comportamento, alvo): a escolha é uma só | T-ADAPT-2: o alvo entregue é o da unidade escolhida |
| **a memória** | o N6, só para a fruta, desligado, fora do jogo | os lugares onde comeu entram na decisão, e a visita vazia apaga o lugar | T-MEM-2 e T-MEM-4 |
| **o motivo** | por lobo; a `memoria_emocao` é sempre 0 | por módulo, com seis sondas de mesmo `u` | T-MOTIVO-1 |

**O que fica igual, de propósito:**
- a aritmética;
- o sorteio com um `u`;
- o reflexo do sono;
- o modelo do desfecho;
- as funções do sinal do corpo;
- o `Protocol`;
- a forma da sonda.

São as peças com evidência a favor ou neutras de engenharia.

## 9. A memória: o M-MEM mínimo e o gancho da memória consolidada (DM-3)

**No protótipo** entra só o M-MEM mínimo da seção 4.6: os episódios de alimentação e de visita, a recuperação pela fome sem comida à
vista e o termo no "explorar o lugar". **Isto é memória episódica mínima, e só isto.**

**O que o protótipo não resolve (a condição da DM-3, repetida na revisão de 2026-10-25):** a memória autobiográfica consolidada, a que
muda as facetas adquiridas e as decisões futuras, **é uma etapa planejada**, a tarefa `docs/TAREFA_V2_MEMORIA_AUTOBIOGRAFICA.md` (as
etapas M0 a M7), **e não está resolvida pelo protótipo** nem por este documento. O protótipo deixa só a interface abaixo e o gancho
causal. **O critério de conclusão dessa etapa** (a seção 7 da tarefa da memória, mais a validação causal da seção 4 dela):
- cada etapa M0 a M7 com os testes da seção 3 da tarefa passando;
- o replay bit a bit (G1), e a chave desligada dando a vida de hoje (G2);
- a sonda contrafactual mostrando que uma lembrança recuperada **mudou uma decisão** (M4), e cada mudança de faceta adquirida apontando
  os episódios consolidados que a causaram, com o temperamento inato igual ao do nascimento (M5, DM-6);
- o teste de fidelidade da fala falhando quando ela alega uma causa por memória sem o registro (M6).

Até isso passar, nenhum documento descreve a memória autobiográfica como feita.

**A interface que a etapa da memória autobiográfica herda** (`docs/TAREFA_V2_MEMORIA_AUTOBIOGRAFICA.md`, etapas M0 a M7):

| chamada | o que faz no protótipo | o que a memória consolidada faz com ela |
|---|---|---|
| `codificar(episodio) -> id` | guarda o episódio de alimentação ou de visita | o M1: decide o que vira episódio (o limiar da ME-1), com o contexto, os participantes e o corpo |
| `recuperar(pista) -> (id, termos) | None` | o lugar de maior valor, pela fome sem comida à vista | o M2: a pista é o contexto inteiro (a ME-2); volta o episódio mais parecido |
| `consolidar(tick)` | não faz nada | o M3: recente → duradoura → central (a ME-3) |
| `termos_decisao(unidades) -> {(b, o): M}` | o termo M do lugar | o M4: o termo de qualquer unidade, registrado no motivo, com a sonda contrafactual |
| `evidencia_faceta(nome) -> [ids]` | devolve vazio | o M5: os episódios consolidados que pedem a mudança de uma faceta, que o M-PERS aplica devagar e com os ids (DM-6: nunca no temperamento) |

**O gancho causal:**
- a memória consolidada pesa nas decisões **só** pelo `termos_decisao`, e o M-ARB já mede quem decidiu (seção 7);
- ela pesa nas facetas **só** pelo `evidencia_faceta` e pelo `mudar_faceta` do M-PERS.

Nenhum outro caminho existe. Por isso a influência causal é verificável pela sonda e pelos ids.

## 10. Os testes de mecanismo planejados

Todos com resposta conhecida, calculada à mão a partir dos parâmetros do teste (PROPOSTOS). Os G1, G2 e G-PAR estão na seção 11.

| teste | módulo | o que monta | a resposta conhecida |
|---|---|---|---|
| **T-SENS-1** | M-SENS | a ração a d = 0, a d = R/2 e a d ≥ R | `prox` = S, S/2 (±1) e 0; a classe podre separada; no máximo 8 linhas, na ordem dos `vistos` |
| **T-SENS-2** | M-SENS | a mesma classe vista em n decisões seguidas, depois ausente | `hab` segue `S·(1 − (1 − k/S)^n)` (±1 por passo); a novidade volta com a mesma meia-vida |
| **T-SENS-3** | M-SENS | mudar um químico sem receptor; procurar `corpo` nos imports | a saída do M-SENS não muda; nenhum import (G-RECEPTOR) |
| **T-AFETO-1** | M-AFETO | faltas abaixo e acima do λ_r | a urgência é 0, depois a reta de inclinação a_r, depois a de a_r + b_r |
| **T-AFETO-2** | M-AFETO | um consumo com antes e depois dados | o r é igual ao `sinal_corpo` do A sobre os mesmos receptores, inteiro por inteiro |
| **T-AFETO-3** | M-AFETO | a excitação de 0 a S, com a subchave ligada e desligada | o `g_apr` dentro de [g_min, g_max]; desligada, constante em g₀ |
| **T-ESTADO-1** | M-ESTADO | um degrau na entrada de um integrador | depois de n decisões, `y = S·(1 − (1 − k/S)^n)` (±n); a meia-vida igual à da tabela de τ |
| **T-ESTADO-2** | M-ESTADO | escolher a mesma intenção duas vezes; tirar o alvo dos `vistos`; N_desiste decisões sem progresso | o C sobe e depois zera; a intenção acaba nos dois casos; o F sobe só no fim sem a meta |
| **T-IMPULSO-1** | M-IMPULSO | o inato sozinho (d̂ = 0, H = 0, sem memória): (a) fome alta e ração a 2 células; (b) fome alta, nada à vista; (c) saciado com a ração à vista; (d) energia baixa de noite | (a) comer a ração é a maior unidade; (b) chamar é a maior; (c) comer fica em 0; (d) dormir é a maior. São os sinais da tabela da seção 4.5 |
| **T-IMPULSO-2** | M-IMPULSO, M-PLAST | um d̂ da ração dado; a falta da fome F e depois 2F | o G sobe como o `valor_previsto` (quadrático na falta), igual à conta do A sobre os mesmos números |
| **T-MEM-1** | M-MEM | comer no comedouro com r > 0; refazer pelo log | um episódio com os campos certos; o replay dá os mesmos episódios |
| **T-MEM-2** | M-MEM | (a) com fome e nada à vista, um episódio positivo no lugar P; (b) saciado; (c) um episódio negativo | (a) a unidade "explorar P" com M > 0; (b) nenhuma recuperação; (c) nenhuma atração |
| **T-MEM-3** | M-MEM | N_ep + 1 episódios | sai o de menor \|r\|; no empate, o mais antigo |
| **T-MEM-4** | M-MEM | um episódio positivo em P e, depois, uma visita vazia a P | a recuperação de P cai a 0 (o mais recente do lugar manda) |
| **T-ARB-1** | M-ARB | pesos inteiros dados e uma grade de `u` | a escolha de cada `u` é a da conta à mão; uma chamada à rng com dois candidatos ou mais, nenhuma com um só |
| **T-ARB-2** | M-ARB | a energia abaixo de `λ_sono`, com outras unidades altas | dorme; nenhuma chamada à rng; o reflexo no registro |
| **T-PLAST-1** | M-PLAST | o mesmo Δ em n consumos | `d̂ = Δ·(1 − (1 − η'/S)^n)` (±n), com η' = `mul(g_apr, η_d)`; com `g_apr` = S, igual ao `ModeloMundo` |
| **T-PLAST-2** | M-PLAST | r > 0, r < 0 e r = 0; característica pré a 0 | o H sobe, desce ou fica, só na linha da escolhida; com o pré a 0, não muda; o teto segura |
| **T-PLAST-3** | M-PLAST, M-AFETO | o `g_apr` dobrado | o passo de P1 e de P2 dobra (±1) |
| **T-ADAPT-1** | M-ADAPT | o `Protocol`; uma Observação sem `corpo`; um alvo fora dos candidatos | o `isinstance(..., Politica)`; `raise` nos dois casos |
| **T-ADAPT-2** | M-ADAPT | a unidade escolhida (comer, item 3) | o `escolher_alvo` devolve o candidato do item 3 |
| **T-MOTIVO-1** | todos | uma decisão com cada termo conhecido | a soma dos termos é a ativação antes do φ; zerar um termo nulo não muda a sonda; num caso montado em que a memória vira a escolha, `memoria_decidiu` é verdadeiro |
| **T-MOTIVO-2** | M-EXPR | uma fala que diz "lembrei" sem recuperação; uma que diz "porque lembrei" sem `memoria_decidiu` | o verificador recusa as duas |
| **T-CADEIA-0** | o A (só leitura; nenhuma mudança) | o A do v12, fome < 0,25, ração a 2 células | confirma a leitura do código: o único candidato é chamar. É o ponto de partida, não um gate do A |
| **T-CADEIA-1** | todos, inato | o cenário do MVP com os parâmetros postos à mão (o D3): fome alta e ração a 2 células | para cada `u` da grade, a fração de escolhas de comer a ração é a do peso dela sobre a soma; com a escolha, o pet come na mesma decisão (o alcance de 60 subunidades cobre 2 células) |
| **T-CADEIA-2** | todos, com aprendizado | depois de k consumos com o mesmo Δ, uma fome moderada abaixo do limiar inato | antes dos consumos, comer a ração tem peso 0; depois, peso > 0, com o valor da conta |

**A avaliação do protótipo** (a ablação por módulo, o A como baseline, o G-MVP e o G-CUSTO) não é teste de mecanismo. Ela tem plano de
análise próprio (`docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md`), commitado antes da primeira vida.

## 11. A versão e o protocolo

**O cérebro:**
- **a versão de pet:** o modular entra no jogo como **v13** (DM-5). A v12 fica com o MVP e o A. Os saves v1 a v12, as assinaturas e os
  gabaritos não mudam;
- **cada mudança de módulo que mude a vida** vira uma versão nova;
- **a chave:** `ConfigDigibrain.ligada`, desligada por padrão, com uma subchave por peça que a avaliação desliga:
  - a modulação do `g_apr`;
  - o P2;
  - o M-MEM;
  - a persistência;
- **as ações:** nenhuma ação nova no protótipo, que usa as sete de `ACOES_PET_HOJE`. Se uma vier depois, entra no fim do enum, com a
  lista do bandit fixa, como o `ALIVIAR` (`events.py:211-222`).

**O motor:**
- **o `engine.py` não muda** (`ENGINE_SHA256_V0`). O cérebro entra pelo `Protocol` `Politica`;
- **o candidato `lembranca`** do explorar (PE-14) é uma camada do `MotorMundo` atrás da chave da v13, no Python e no TS.
  **AUTORIZADO pelo Matheus em 2026-10-25,** nestas condições: só na v13; nos dois lados; atrás da chave; **o gabarito G2 das vidas de
  hoje gravado num commit próprio antes da implementação**; a v12 e o A preservados byte a byte;
- **o log:** nenhum evento novo. O cérebro determinístico não grava nada, e a vida se refaz pelo log de sempre. O modo livre gravado
  não se aplica.

**Os gates de engenharia** (não são evidência de aprendizagem):
- **G1:** o replay é bit a bit;
- **G2:** com a chave desligada, as vidas de hoje (o v12, o A e as bancadas) saem byte a byte, com o gabarito num commit antes da
  mudança;
- **G-PAR:** o espelho TS refaz os gabaritos do Python decisão a decisão, sem campo mascarado;
- **G-INT:** pela AST, sem float, sem `/` e sem `math` no pacote;
- **G-RECEPTOR** e **G-SEM-DIRECAO.**

**A paridade, mais uma vez:** passar no G-PAR quer dizer que o TS faz a mesma conta. Não quer dizer que o cérebro aprende nem que ele
se comporta bem (DM-2).

## 12. O orçamento (PROPOSTO, SEM FONTE; a medir no protótipo)

| medida | o que se sabe hoje | o orçamento proposto | como se mede |
|---|---|---|---|
| **o CPU por decisão no navegador** | o A em Python: 339,5 µs por decisão com o motor e o mundo, "quase todo do motor e do mundo" (`docs/RESULTADO_V2_COMPARACAO_CEREBROS.md`); o A v11 no navegador **nunca foi medido** | o cérebro modular ≤ 2× o cérebro do A v11, no mesmo aparelho e no mesmo navegador (AF-4: o orçamento parte do custo do A) | o A v11 medido primeiro; depois a v13, com e sem as sondas. **A medição do A é pontual e só de desempenho** (tempo por decisão e por replay), **sem nova campanha de validação comportamental** do A (Matheus, 2026-10-25) |
| **as operações por decisão** (a estimativa) | — | ~16 **unidades de comportamento** (os pares (b, o) do M-IMPULSO, a reconciliação da seção 2.1; as outras ~64 unidades não fazem produto) × ~20 características × 7 somas (a decisão e as seis sondas) ≈ 2 200 produtos inteiros, mais ~20 integradores | contagem no protótipo |
| **o tamanho do log** | o A: 6 168 B por dia (a mesma fonte) | **+0 B por dia:** nenhum evento novo | o log de uma vida v13 contra o da v12 com as mesmas ações do dono |
| **o estado aprendível** | o A: 762 a 763 parâmetros | ≤ 1 000 inteiros: H (7 × ~20), d̂ (6 × 11), N_ep episódios (16 × ~15 campos), ~20 integradores | contagem no `estado_interno` |
| **o replay ao abrir o save** | 96 decisões por dia (1 440 / 15); uma vida de 14 dias tem 1 344 | o replay de 14 dias da v13 ≤ 1,5× o da v12 no mesmo aparelho | cronometrar o carregamento |

O D5 de `docs/TAREFA_V2_CEREBRO_A_BASELINE.md` só vale com esse orçamento decidido e medido.

## 13. A comparação com a visão do produto e da pesquisa (para a revisão)

**O que cada módulo entrega:**

| módulo | ao MVP (`docs/PRODUTO_VISAO.md`, seção 3) | à pesquisa (`docs/PLANO_V2_PESQUISA.md`, seção 2; a arquitetura, seção 11) |
|---|---|---|
| M-SENS | "o pet detecta" a comida posta num lugar (a linha de objeto, a proximidade) | as entradas da ablação; a G-RECEPTOR |
| M-AFETO | "a consequência muda o corpo e pode mudar o comportamento depois" (o r) | a química que modula a aprendizagem (o `g_apr`, com os controles embaralhado e constante): uma fonte de plasticidade que o A não tem |
| M-ESTADO | "decide, navega, alcança": a intenção que persiste até a comida | o estado interno dinâmico (o item 1 do pedido); a ablação da persistência |
| M-IMPULSO | o pet vai à comida por iniciativa própria, sem a cascata que o fazia só chamar | **o inato** da pergunta maior: as predisposições herdadas (o `W⁰`, o gancho do genoma) |
| M-ARB | uma escolha rastreável, com o motivo na tela | a sonda "quem decidiu" por módulo |
| M-PLAST | "pode mudar o comportamento depois" (o incentivo e o hábito) | **a plasticidade** da pergunta maior: P1 (desfecho), P2 (hábito), cada uma desligável |
| M-MEM | voltar ao lugar onde a comida esteve | a memória que muda a decisão, medida pela sonda e pela ablação; a base da validação REL/SEM/REC/EMB |
| M-ADAPT | a troca do cérebro sem mexer no mundo, no gesto nem na tela (o adaptador do `docs/TAREFA_V2_DIGIBRAIN_MODULAR_PRODUTO.md`) | o mesmo `Protocol` nos dois lados |

**Onde a espec fica aquém da visão:**
- **o treino, o crescimento, a batalha e a evolução** não tocam o cérebro nesta especificação, como no MVP ("nada novo no MVP");
- **as frutas e o paladar** ficam fora do protótipo (o v12 é só a ração). O d̂ por classe já os recebe quando entrarem;
- **o "cérebro neural"** é uma rede de taxa pequena desenhada à mão (seção 2.6). A PE-13 está DECIDIDA: "rede pequena de unidades"
  nos documentos técnicos, "DigiBrain" como nome do produto.

**Onde a espec serve à pergunta da pesquisa:**
- a pergunta maior ("em que condições a plasticidade durante a vida produz vantagem adaptativa sobre as predisposições herdadas?") vira
  a ablação dentro do mesmo cérebro, nos cenários do MVP:
  - o inato sozinho;
  - o inato com P1;
  - com P1 e P2;
  - com o M-MEM;
  - com a modulação;
- é o desenho que a arquitetura pede na seção 11. **O A entra só como baseline** (`docs/TAREFA_V2_CEREBRO_A_BASELINE.md`, seção 1).

**O que a espec não promete:** que o modular vença o A nas medidas antigas (o D6 sozinho não é limitação), nem que a modularidade traga
legibilidade. Na L1, a camada única foi mais legível que os lobos (a arquitetura, seção 10). **As duas coisas se medem.**

## 14. A literatura usada

| referência | status | o que sustenta, e só isso | onde |
|---|---|---|---|
| Cliff e Grand (1999), `10.1162/106454699568683` | VERIFICADA | rede recorrente modular com aprendizado hebbiano e modulação hormonal, especificadas geneticamente | P2; os moduladores; a seção 2.6 |
| Grand, Cliff e Malhotra (1997), `10.1145/267658.267663` | VERIFICADA | rede para a coordenação sensório-motora, bioquímica artificial e genoma juntos | [INSPIRAÇÃO], seção 2.6 |
| Grand e Cliff (1998), `10.1023/a:1010042522104` | VERIFICADA, só metadados | não sustenta conteúdo | não usada para conteúdo |
| Keramati e Gutkin (2014), `10.7554/elife.04811` | VERIFICADA | a recompensa como redução do desvio homeostático | o r; o incentivo (seção 2.3) |
| Berridge e Robinson (1998), `10.1016/s0165-0173(98)00019-8`; Berridge, Robinson e Aldridge (2009), `10.1016/j.coph.2008.12.014` | VERIFICADAS | impacto hedônico, aprendizado e saliência de incentivo como componentes separados; querer, gostar e aprender dissociáveis | a separação entre o incentivo, o paladar e o M-PLAST |
| Sutton, Precup e Singh (1999), `10.1016/s0004-3702(99)00052-1` | VERIFICADA, título e metadados | o formalismo das opções | a intenção como opção; o crédito por opção |
| Brooks (1986), `10.1109/jra.1986.1087032`; Bryson (2003), `10.1007/3-540-36559-1_7` | VERIFICADAS, título e metadados | arquitetura por camadas de competência; desenho modular por competências nomeadas | o M-IMPULSO |
| Jacobs et al. (1991), `10.1162/neco.1991.3.1.79` | VERIFICADA | aprendizado localizado por módulo sob um portão | o precedente do aprendizado por módulo (seção 4.7) |
| Khetarpal et al. (2020), arXiv:2006.15085 | VERIFICADA | as *affordances* em aprendizado por reforço | quais unidades existem em cada decisão |
| Castro e Gudwin (2013), `10.4018/jse.2013010102` | VERIFICADA | um módulo de memória episódica por cenas numa criatura | o M-MEM, sem dizer que a cena informa a escolha |
| Lewis e Cañamero (2016), `10.1177/1059712316666331` | VERIFICADA, resumo | o prazer melhora a viabilidade e a flexibilidade | o M-AFETO, em geral |
| McGaugh (2005), `10.1101/lm.93405` | VERIFICADA, só título | — | [HIPÓTESE]: a excitação modulando a aprendizagem |
| Jacob et al. (2018), `10.1109/cvpr.2018.00286` | VERIFICADA, título e metadados | redes treinadas para inferência em aritmética só inteira | a aritmética (seção 1) |
| Hasani et al. (2022), `10.1038/s42256-022-00556-7`; Lechner et al. (2020), `10.1038/s42256-020-00237-3` | CORPUS (pista) | — | a forma II, como [HIPÓTESE]; **as licenças não foram conferidas** (DM-9) |
| NORNBRAIN | software não revisado, "nunca evidência"; código em PolyForm Noncommercial 1.0.0 | — | só estudo (DM-9); nada dele entra |

**SEM FONTE no repositório,** e por isso marcados nas seções:
- o hebbiano como regra (de Hebb);
- os traços de elegibilidade;
- as regras de três fatores como termo da literatura;
- os integradores com vazamento e as redes recorrentes de tempo contínuo como modelo neural;
- a regra de Luce;
- os acumuladores com inibição mútua;
- a curva das urgências;
- a regra "o mais recente do lugar manda".

## 15. As decisões a pesquisar antes de implementar

Todas PROPOSTAS, com a recomendação primeiro. **"Antes"** quer dizer que bloqueia o começo do protótipo. **"No protótipo"** quer dizer
que entra com o valor recomendado e se decide pela avaliação, com o plano de análise.

| # | decisão | quando | recomendação | custo de errar |
|---|---|---|---|---|
| **PE-1** | a forma neural do estado sem fonte verificada (integradores e redes de tempo contínuo) | antes | **seguir com os integradores como [HIPÓTESE] de desenho** e pedir uma busca de literatura própria (a categoria `literatura`) sobre integradores com vazamento, redes recorrentes de tempo contínuo e regras de três fatores, para trocar os SEM FONTE por fontes ou por "não localizada" | sem a busca, a seção 2 fica sustentada só pelo Creatures e pelo código; com a busca antes de tudo, o protótipo espera uma rodada de literatura |
| **PE-2** | o P2 (o hábito hebbiano) no primeiro protótipo, ou só o P1 | antes | **os dois, o P2 atrás da subchave,** com a ablação. A L1 do A como braço de comparação do P2, se o plano achar que responde a algo | só o P1: o pet aprende o que as coisas fazem, mas não muda o que faz em cada contexto. Os dois sem subchave: nada se atribui |
| **PE-3** | o crédito: por opção (a decisão que começou a intenção) ou por janela de K decisões | antes | **por opção** | a janela: o traço do A piorou o que se queria medir; por opção sem teste: uma intenção longa pode creditar um começo que nada teve com o fim (o T-PLAST-2 com intenções longas confere) |
| **PE-4** | o que modula o `g_apr` (a excitação? o estresse? a dor?) e se ele entra ligado | antes | **a excitação, atrás da subchave desligada no primeiro braço,** com os controles embaralhado e constante do V3 | ligada sem controle: "modular" e "aprender mais depressa" não se separam (o risco do V3, seção 4) |
| **PE-5** | a arbitragem: o sorteio proporcional ou um acumulador recorrente com inibição mútua | no protótipo | **o sorteio proporcional,** que mantém a contagem da rng e a sonda de mesmo `u` | o acumulador antes do tempo: a sonda de mesmo `u` deixa de valer e o custo da paridade sobe; nunca testá-lo: a competição fica não neural |
| **PE-6** | as constantes da persistência (τ do compromisso, `w_pers`, `N_desiste`) | no protótipo | **o N_desiste pelo alcance:** as decisões que o pet leva para cruzar o raio da visão, mais uma | curto: o pet desiste no caminho; longo: insiste num alvo que sumiu |
| **PE-7** | o incentivo: o `valor_previsto` sobre o d̂ (revaloriza pelo estado) ou um valor escalar por classe | antes | **o `valor_previsto`** (a peça com o G-T1) | escalar: perde a revalorização, e o pet saciado continua querendo o mesmo |
| **PE-8** | a forma II (recorrente) e o gatilho dela | no protótipo | **não entra no primeiro protótipo;** o gatilho é o da seção 3 | antes do gatilho: repete o risco do B; nunca: a expressividade não se testa |
| **PE-9** | o tamanho: as linhas de objeto e as características de contexto | antes | **as linhas pelo `max_vistos` (8) e as ~20 características da seção 2.1** | muitas: o custo sobe e a ablação fica cara; poucas: o pet não distingue o que importa |
| **PE-10** | o decaimento do hábito H para o 0 | no protótipo | **sem decaimento no primeiro braço,** com o G6 (nenhum peso preso no teto) medido | sem decaimento: o hábito velho não sai; com decaimento sem fonte: o aprendido some sozinho |
| **PE-11** | a habituação e a novidade no M-SENS | no protótipo | **um integrador por classe** (seção 4.2) | por item: o custo e a memória sobem; nenhuma: a novidade não pesa |
| **PE-12** | a escala dos pesos aprendidos: S = 1024 ou uma escala maior só para os passos pequenos | antes | **S = 1024,** o do A; trocar só se um passo der 0 na conta (o T-PLAST-1 mostra) | escala pequena: os passos pequenos arredondam para 0, e nada aprende; escala grande sem necessidade: a paridade e os testes ficam mais caros |
| **PE-13** | se uma rede de taxa pequena, desenhada à mão, com uma recorrência pelo estado e modulação difusa, basta para chamar o protótipo de "cérebro neural" nos documentos e na tela | antes (é do Matheus) | **chamar de "rede pequena de unidades" nos documentos técnicos** e manter "DigiBrain" como nome do produto, sem prometer mais | prometer mais: a seção 2 não sustenta; chamar de menos: o nome do projeto perde o sentido |
| **PE-14** | o lugar lembrado no motor: o candidato novo `lembranca` no explorar, atrás da chave da v13 | antes | **o candidato novo,** no Python e no TS, com o G2 | sem o candidato: o M-MEM não leva o pet a lugar nenhum fora da vista e fica sem efeito no MVP |
| **PE-15** | as licenças do CfC e do NCP | antes de qualquer reúso da forma II | **conferir e registrar** antes de copiar qualquer código ou equação de software | reusar sem conferir: risco de licença no produto (DM-9) |
| **PE-16** | a capacidade e a codificação do M-MEM mínimo (N_ep; todo consumo vira episódio) | no protótipo | **N_ep = 16; todo consumo e toda visita viram episódio;** o limiar fino é a ME-1 da tarefa da memória | pequeno: o pet esquece o comedouro; grande sem limiar: ruído e custo |

**DECIDIDAS em 2026-10-25 (Matheus):** as nove PE "antes" (1, 2, 3, 4, 7, 9, 12, 13 e 14), **pelas recomendações da tabela**, com
estas notas da revisão:
- **PE-1:** a busca de literatura (categoria `literatura`) roda **em paralelo** à etapa 0 do protótipo (os gabaritos e a chave
  desligada, que não dependem da forma do estado), não antes dela; os SEM FONTE da seção 2 trocam por fontes ou por "não localizada"
  antes da primeira vida;
- **PE-13:** "rede pequena de unidades" nos documentos técnicos e na tela do motivo; "DigiBrain" como nome do produto;
- **PE-14:** autorizada para a v13, Python e TS, atrás da chave, com o gabarito G2 antes da implementação (seção 11).

As sete "no protótipo" (5, 6, 8, 10, 11, 16; a 15 só antes da forma II) entram com o valor recomendado e se decidem pela avaliação,
com o plano de análise.
