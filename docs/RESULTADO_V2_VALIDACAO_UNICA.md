# Resultado — validação única do experimento maior da V2

Plano `docs/PLANO_ANALISE_V2_EXPERIMENTO_MAIOR.md`, adendos 1 a 4. Tarefas `docs/TAREFA_V2_V1_VALIDACAO_UNICA.md`, `docs/TAREFA_V2_V1_ADENDO3.md` e
`docs/TAREFA_V2_V1_LIGAR.md`. Sinal verde do coordenador, autorizado pelo Matheus, depois do #191 e do #192.

**Run única:**
- quando: 2026-10-06, das 19:58 às 23:22 (3 h 24 min);
- onde: nas bases 30101…30505 (adendo 4.1), com K = 6 (N = 30 unidades);
- config: `experiments/configs/v2_experimento_maior/validacao.json`, sem mudança;
- código: `main` `2660170` mais o registro `f1c32ab`; orquestrador sha256 `4d5c4b63…`, plano sha256 `080388f8…` (`meta.json`).

**O que rodou:**
- 1680 vidas, todas gravadas e rejogadas do disco bit a bit: bloco principal 720, padrão 90, blocos 510, durações 240, P2d e P3i 120;
- antes da run, uma fumaça da mesma config nas sementes dos testes (112 vidas) passou.

**De onde vêm os números:** de `artifacts_v2_validacao_unica/` (`resumo.json`, `contrastes.json`, `blocos.json`, `duracoes.json`,
`p2d_p3i.json`, `w_info_p2e.json`, `curvas.json`). As vidas (3 GB) ficam fora do git e se regeneram da config e do código.

**Nada foi ajustado olhando o resultado.**

## 1. As predições

Família de Holm com os seis primários (α = 0,05). Δ = 0,1986 nas taxas e 17,5 consumos no p3 (adendo 2).

| predição | contraste (d = o que a predição diz) | média | IC 95% | Holm | leitura | separação do cuidado (5.1) |
|---|---|---|---|---|---|---|
| 1. No casado, o P0 vence | p1_casado: P1 − P0, taxa final | +0,078 | [+0,048; +0,110] | rejeita | **confirma** | (sem braço com dono) |
| 2. No descasado e no mutável, o P1 vence o P0 | p2_descasado: P0 − P1, taxa final | +0,076 | [+0,050; +0,103] | rejeita | **confirma** | (sem braço com dono) |
| | p2_mutavel: P0 − P1, taxa depois da troca | +0,102 | [+0,077; +0,129] | rejeita | | |
| 3. O P2 chega à metade com menos consumos que o P1 | p3_consumos: P1 − P2, consumos | +11,4 | [+1,0; +22,7] | rejeita (p ajustado 0,03) | **confirma** | **P2: sem efeito acima do só cuidado** |
| 4. O P2e piora no começo e se recupera | p4a_piora: P2e − P1, taxa no início | +0,0005 | [−0,012; +0,013] | não rejeita | **inconclusivo** | P2e: sem efeito acima do só cuidado |
| | p4b_recupera: P0 − P2e, taxa final | +0,083 | [+0,058; +0,110] | rejeita | | |
| 5. O P3 não difere do P0 (equivalência, fora do Holm) | p5: P3 − P0, taxa final | −0,081 | [−0,141; −0,007] | — | **confirma** (IC 90% [−0,132; −0,021] dentro de ±Δ) | P3: sem efeito acima do só cuidado |

- **Unidades sem valor:** uma unidade fica fora dos contrastes 1, 2, 3 e 4b, porque o P0 dela (ou o P1 e o P2, no p3) não comeu fruta na
  janela; os contrastes usam 29. No p5 ficam 25, porque cinco unidades não têm valor no P3 ou no P0.
- **Predição 2:** a inclinação de P0 − P1 nos dias 11 a 14 não cresce:
  - descasado −0,010 [−0,049; +0,027];
  - mutável +0,031 [−0,002; +0,063].

  Não cabe a leitura "inconclusivo por duração". As duas condições confirmam.
- **Predição 4:** a parte (a) não aparece. O P2e não come mais a fruta ruim que o P1 no começo, então a (b) sozinha não confirma. O dia
  em que a curva do P2e cruza a do P0 é o 3.

### A separação do cuidado (seção 5.1) qualifica as predições 3, 4 e 5

Pela seção 5.1, um efeito que envolve P2, P2e ou P3 só conta como **ensino** se:
- (a) o braço difere do próprio "só cuidado" acoplado, que é o mesmo cérebro rejogado no registro sem a informação e sem os sinais;
- (b) o cuidado é igual entre os dois.

Nos três casos a condição (a) falha:
- **P2** (predição 3): P2 contra o só cuidado do P2 nos consumos até a metade dá −1,6 [−11,7; +8,2]. O P2 sem a informação, no mesmo
  registro, chega à metade tão rápido quanto com ela. **A confirmação da predição 3 não pode ser atribuída à informação.** O contraste
  primário confirma, mas o ganho do P2 sobre o P1 não vem do que o informante disse.
- **P2e** (predição 4): o P2e é igual ao só cuidado dele, nas duas medidas: +0,005 [−0,025; +0,036] e −0,001 [−0,011; +0,009].
- **P3** (predição 5): P3 contra o só cuidado do P3 dá −0,056 [−0,125; +0,022].

**A condição (b) também falha nos três:** os braços em malha fechada têm menos privação e mais saúde que o acoplado.
- fora de privação: +0,042 (P2), +0,045 (P2e) e +0,075 (P3);
- saúde: +0,022, +0,020 e +0,037.

O acoplado rejoga o cuidado do dono em malha aberta, e esse cuidado foi dado ao pet original, não ao rejogado. Isso fica registrado: o "só
cuidado" cuida pior que o original nesta montagem.

### Apoio teórico (adendo 3, só a leitura; a regra não muda)

| predição | apoio (`docs/PREDICOES_V2.md`) | o que o resultado diz ao lado |
|---|---|---|
| 1 | APOIADA | o P1 come mais a fruta ruim que o P0 no casado (+0,078): aprender custa onde o prior acerta |
| 2 | APOIADA COM RESSALVA (a relação com a duração não é monotônica) | confirma nas duas condições; o bloco de durações (seção 3) não mostra ganho crescente com a vida |
| 3 | APOIADA (pela informação filtrada, não pela economia de tentativas) | o contraste confirma, mas a separação do cuidado não atribui o efeito à informação |
| 4 | SEM APOIO DIRETO | inconclusivo: o P2e não piora no começo |
| 5 | CONTESTADA (Ho et al. 2017, `10.1016/j.cognition.2017.03.006`), mantida como registrada (P-5) | a equivalência confirma pela margem Δ, mas o IC 95% fica todo abaixo de 0: o P3 come menos a fruta ruim que o P0 (−0,081), uma diferença menor que Δ |

### O mutável (adendo 3.2 e adendo 4.2)

- **Limitação declarada (3.2):** os modelos disponíveis tratam mudança entre gerações, não dentro da vida (Kozielska e Weissing 2024,
  `10.1371/journal.pcbi.1011840`). No mutável, o resultado descreve o que este motor faz, e não testa teoria.
- **Componente da mudança (4.2):**
  - no descasado, a experiência é confiável e a melhor ação é estável dentro da vida; muda o mundo de origem do prior;
  - no mutável, a melhor ação troca uma vez, no fim do dia `dias // 2`.

  Um resultado da predição 2 vale para esses componentes, não para "ambientes que mudam".
- **Valor e eficiência separados (4.2, Eliassen et al. 2009, resumo):**
  - valor: o p2_mutavel, P0 − P1 = +0,102;
  - eficiência: a taxa da fruta ruim do P1 depois da troca, 0,330 [0,322; 0,337], longe do ótimo 0.

  Isso não se lê como falha. Descritivo: a taxa do P1 fica perto de 0,33 em toda condição e duração (seção 3).

## 2. Os secundários (fora do Holm primário)

### N6 (plano do N6), família própria com Holm de três

| gate | contraste | média | IC 95% | resultado |
|---|---|---|---|---|
| G-CAUSAL | M0 (acoplado) − MR, taxa final | +0,028 | [+0,009; +0,048] | Holm rejeita |
| G-REC | MT (acoplado) − MR | +0,028 | [+0,011; +0,044] | Holm rejeita |
| G-EMB | ME (acoplado) − MR | +0,053 | [+0,032; +0,075] | Holm rejeita |
| G-CITA | fração decidida pela memória no MR | 0,204 | [0,173; 0,235] | passa (> 0,069) |

- G-M1 e G-M2 passam (120 vidas); G5 passa (saúde e privação iguais); o G-M3 não é medido pela bancada.
- **Leitura: confirma.** O efeito é pequeno: o IC 90% do G-CAUSAL também cabe em ±Δ_N6.

### N7 (plano do N7), família própria com Holm de três

| gate | contraste | média | IC 95% | resultado |
|---|---|---|---|---|
| G-EROSAO | P0+ped − P1+ped, deferência dias 6–10 | −0,001 | [−0,016; +0,015] | não rejeita |
| G-MARCA | só cuidado do P3+ped − P3+ped, fração de X na extinção | +0,236 | [−0,319; +0,681] | não rejeita, **n = 6** |
| G-MARCA-E | P3 − P3+ped | +0,139 | [−0,361; +0,514] | não rejeita, **n = 6** |
| G-ARB | deferência do P0+ped, dias 1–10 | 0,016 | [0,009; 0,024] | passa |
| G-URG | violações das regras urgentes | 0 | — | passa |

- **G-MARCA e G-MARCA-E são declarados subpotenciados** (adendo 2: poder simulado 0,34 e 0,38). Aqui, além disso, só 6 das 30 unidades
  têm valor na fração de X da extinção (24 sem valor, contadas em `blocos.json`). Nada se lê deles.
- G5: o P0+ped − P0 passa. **O P3+ped − o só cuidado dele falha:** fora de privação +0,005 [+0,002; +0,009] e saúde +0,0006
  [+0,0002; +0,0011]. É a mesma diferença de malha aberta da seção 1.

### Ablações da K-7 (P1 completo menos uma peça; positivo = a peça baixa a taxa da fruta ruim)

| peça | condição | média | IC 95% |
|---|---|---|---|
| memória | descasado (final) | −0,002 | [−0,011; +0,008] |
| memória | mutável (depois da troca) | **+0,014** | [+0,004; +0,024] |
| canais | descasado | −0,005 | [−0,013; +0,004] |
| canais | mutável | −0,002 | [−0,010; +0,007] |

A memória ajuda só no mutável; os canais não mudam nada que se veja.

### N5, descritivo: a informação em momentos sorteados (P2a) − na hora (P2), no descasado

- consumos até a metade: +6,2 [−0,9; +13,1];
- taxa no início: +0,019 [+0,008; +0,030];
- taxa final: −0,008 [−0,019; +0,003].

A referência do P0 vem do bloco principal (correção do #189).

### Bloco de durações (adendo 3.1): P0 e P1, 7, 14 e 28 dias, mesmas interações por dia

| condição | braço | 7 dias | 14 dias | 28 dias | forma (regra registrada) |
|---|---|---|---|---|---|
| descasado (final) | P0 | 0,420 | 0,402 | 0,413 | platô |
| | P1 | 0,321 | 0,326 | 0,328 | platô |
| | ganho P0 − P1 | +0,099 | +0,076 | +0,085 | platô |
| mutável (depois da troca) | P0 | 0,427 | 0,430 | 0,400 | crescente (o P0 melhora de 14 a 28) |
| | P1 | 0,320 | 0,330 | 0,328 | platô |
| | ganho P0 − P1 | +0,108 | +0,102 | +0,073 | decrescente |

- **No mutável a troca acompanha a duração** (fim do dia `dias // 2`), e a janela "depois da troca" muda junto. A leitura dele fica separada
  da do descasado.
- **Limiar (adendo 4.2, L-3):** o passo de 7 para 14 dias não é diferente de zero em nenhuma curva. Por exemplo, o do ganho no descasado
  é −0,023 [−0,059; +0,013]. Não há degrau entre 7 e 14 dias. Um limiar, se existir, fica abaixo de 7 dias e, com estas três durações,
  não se distingue de um platô.
- **Para a predição 2:** o ganho do P1 já está presente aos 7 dias e não cresce com a vida; no mutável, ele encolhe aos 28.

### P2d e P3i (adendo 3.3), sem Holm

| contraste | medida | condição | média | IC 95% |
|---|---|---|---|---|
| P2 − P2d (o momento) | taxa final | descasado | +0,003 | [−0,006; +0,011] |
| | taxa final | mutável | −0,004 | [−0,011; +0,002] |
| | consumos até a metade | descasado | **−12,8** | [−23,4; −3,0] |
| P3 − P3i (a interpretação) | taxa final | descasado | **−0,111** | [−0,217; −0,003] (n = 26) |
| | taxa final | mutável | **−0,094** | [−0,178; −0,014] (n = 28) |
| | consumos até a metade | descasado | −0,5 | [−4,9; +3,6] |

- **O momento:** a informação depois do consumo (P2d) chega à metade com menos consumos que a informação na oferta (P2). A taxa final não
  muda.
- **A interpretação:** o julgamento como feedback (P3) leva a comer menos a fruta ruim que o mesmo julgamento como informação (P3i).
- **Informações por vida:**
  - P2: 96, o mesmo nos dois mundos;
  - P2d: 75,9 (descasado) e 74,7 (mutável);
  - P3i: 29,4 e 30,2;
  - P3: 0.

  O multiconjunto por fruta e conteúdo está em `p2d_p3i.json`.
- **Declarado:**
  - P2d × P3i não entra em contraste (diferem na fonte do aprendizado);
  - no P3i o `w_info` não aprende.

### A trajetória do `w_info` do P2e (adendo 4.2, L-4), descritivo

O peso da informação errada parte de 256 e **cruza o zero em todas as 30 unidades**:
- 10 no dia 1, 9 no dia 2, 7 no dia 3, 3 no dia 4 e 1 no dia 5;
- a média no fim da vida é −3004;
- nenhuma unidade chega ao limite de baixo (−16128).

A recuperação do P2e não é lenta nem limitada pelo teto. O P2e aprende cedo a desconfiar da informação, o que é coerente com a parte (a)
da predição 4 não aparecer.

## 3. Descritivos ao lado

- **Poder no N da run** (bootstrap das 30 unidades da validação, só descritivo): 1,0 em cinco primários e 0,78 no p3. A simulação nestes
  dados daria N = 35. **O N da run é o do adendo 2 (30) e não muda.**
- **Secundários da predição 1:** P2 − P0 no casado +0,082 [+0,051; +0,115]; P3 − P0 +0,053 [−0,028; +0,148].

## 4. O que fica para a leitura

- **Literatura (L-1):** buscar o texto completo do Eliassen et al. 2009 antes da leitura final. A leitura de valor e eficiência acima se
  apoia só no resumo.
- **A separação do cuidado no desenho:**
  - **O que muda a leitura:** o "só cuidado" acoplado cuida pior que o braço original (malha aberta), e a condição (b) falha em todo braço
    com dono. A (a) falha também, então nenhuma predição com dono pode ser lida como "ensino" por esta régua.
  - **O que fica para decidir:** se o acoplado é o controle certo para o P2 e o P3 nesta montagem é pergunta do coordenador e do Matheus.
    Não se ajustou nada aqui.
- **Interpretações e desvios:** em `docs/REGISTRO_DESVIOS.md`, seção VALIDACAO-UNICA.
