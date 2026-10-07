# Leitura da validação única do experimento maior da V2

Data: 2026-10-06. Tarefa `docs/TAREFA_V2_LEITURA_VALIDACAO.md`. **Só papel:** nenhuma run, nenhum código, nenhuma estatística nova.

**De onde vêm os números:**
- `docs/RESULTADO_V2_VALIDACAO_UNICA.md` (PR #193);
- `artifacts_v2_validacao_unica/`: `contrastes.json`, `resumo.json`, `frutas/tabelas.json`, `blocos.json`, `duracoes.json`, `p2d_p3i.json`
  e `w_info_p2e.json`, conferidos no commit `4dd962d` da `main`.

**As bases da leitura:**
- `docs/PREDICOES_V2.md`;
- as sínteses `docs/referencias/E_SINTESE_VALOR_APRENDIZADO.md` e `docs/referencias/E2_SINTESE_PISTAS_P7.md`;
- as decisões de 2026-10-06 no `docs/REGISTRO_DESVIOS.md`: a faixa 15101…15505 queimada, o cérebro B "não fecha" e o controle "só
  cuidado" como limitação.

**Regras** (`docs/referencias/REGRAS_CITACAO_DIGILAB.md`):
- **"o resultado diz"** fica separado de **"leitura nossa"**;
- nenhuma alegação de novidade;
- a comparação A × C (chat D) não terminou e não é antecipada aqui.

**A pergunta da V2:** em que condições a plasticidade durante a vida dá vantagem sobre o herdado?

---

## 0. Duas coisas que pesam em toda a leitura

### 0.1 As regras das predições 1 e 2 se sobrepõem, e os dois lados valem

**O resultado diz:**
- Nas predições 1 e 2, o contraste é positivo pelo teste e o Holm rejeita.
- O IC 90% de cada uma fica **inteiro dentro de ±Δ** (Δ = 0,1986; `resumo.json`, `delta`; `contrastes.json`, `primarios`):

  | contraste | IC 90% |
  |---|---|
  | p1_casado | [+0,052; +0,105] |
  | p2_descasado | [+0,054; +0,098] |
  | p2_mutavel | [+0,081; +0,124] |

**O que o plano registrou** (`PLANO_ANALISE_V2_EXPERIMENTO_MAIOR.md`, seção 5):
- "Confirma" quando o contraste é positivo pelo teste.
- "Refuta" quando o IC 95% fica inteiro abaixo de 0 **ou** o IC 90% fica inteiro dentro de (−Δ, +Δ). Na predição 1, esse segundo caso
  está escrito como "P0 não vence, empata".
- O plano não diz qual saída vale quando as duas acontecem juntas. O orquestrador gravou "confirma" (`resumo.json`, `predicoes`).

**Leitura nossa:**
- **O efeito existe e está na direção prevista, mas é menor que a margem de relevância registrada.** A margem é metade da distância entre
  o P0 descasado e o ótimo.
- **Quanto do caminho o P1 percorre** (pelas taxas finais de `frutas/tabelas.json`):
  - descasado: de 0,402 para 0,326, cerca de 19% da distância ao ótimo 0;
  - mutável: de 0,430 para 0,330, cerca de 23%.
- A forma honesta de reportar é **"confirma na direção, abaixo da margem de relevância"**. Não é "confirma" sozinho, nem "refuta" sozinho.
- A escolha do rótulo é do Matheus (decisão V-1). Não muda nenhum número nem a regra que já rodou.

### 0.2 Todo braço que aprende termina perto de 1/3 da fruta ruim, em todo mundo

**O resultado diz:** a taxa final da fruta ruim fica entre 0,30 e 0,34 nos braços plásticos (`frutas/tabelas.json`,
`taxa_fruta_ruim_final`):

| braço | casado | descasado | mutável |
|---|---|---|---|
| P1 | 0,319 | 0,326 | 0,330 |
| P2 | 0,322 | 0,323 | 0,323 |
| P2e | 0,320 | 0,320 | 0,320 |
| só cuidado do P2 | 0,305 | 0,324 | 0,339 |

**A exceção** é o P3 no mutável, com 0,388.

**Também diz:**
- **O P1 já está perto disso na janela inicial:** 0,329 no descasado, dias 1–7.
- **Nas três durações a taxa final do P1 não muda** (`duracoes.json`):
  - descasado: 0,321 (7 dias), 0,326 (14) e 0,328 (28);
  - mutável: 0,320, 0,330 e 0,328.
- **A referência do herdado** (a taxa final do P0) muda com o mundo: 0,239 no casado, 0,402 no descasado e 0,430 no mutável.

**Leitura nossa:**
- Em cada mundo uma das três frutas faz mal, outra faz bem e a terceira é neutra. Um pet que comesse as três por igual teria uma taxa de
  1/3. As ofertas também são iguais por fruta: cada fruta está em 4 dos 7 conjuntos da rotação (`digilab/config.py`, `_rotacao_ofertas`).
- **O padrão é compatível com o aprendiz apagar a preferência inata**, em vez de aprender qual fruta faz mal. Isso explicaria, com um
  mecanismo só, as duas confirmações:
  - **no casado,** a preferência inata está certa; apagá-la piora (predição 1, P1 come mais a fruta ruim que o P0);
  - **no descasado e no mutável,** a preferência inata está errada; apagá-la melhora (predição 2).
- **Isso não foi testado.** Faltam a fração de consumo de cada fruta e a escolha nas ofertas com uma fruta só. A validação não grava a
  primeira por fruta. É uma pergunta nova (seção 3, Q-1; decisão V-3), não uma conclusão.
- **O mesmo padrão com a informação certa (P2) e errada (P2e)** sugere que, no fim, a informação não muda onde o pet chega. Ver a
  predição 4.

---

## 1. Por predição

### Predição 1: no casado, o P0 vence (aprender só custa)

**O resultado diz:** P1 − P0 na taxa final, no casado: **+0,078 [+0,048; +0,110]**. O Holm rejeita; o IC 90% fica dentro de ±Δ (seção 0.1).

**Apoio teórico prévio:** APOIADA.
- Kozielska e Weissing 2024, texto completo: sem aprendizado, o desempenho é praticamente igual e a aptidão é maior, porque não se gasta
  tempo explorando.
- Eliassen et al. 2009, resumo: o valor de aprender é menor sem mudança e sem variação.

**Concordam?** Na direção, sim.
- A teoria esperava empate ou leve vantagem do P0 (`PREDICOES_V2.md`, leitura da predição 1), e foi isso: uma vantagem real e pequena.
- O mecanismo proposto pela teoria (o tempo gasto explorando) não foi medido. O padrão da seção 0.2 (apagar a preferência inata) é outra
  explicação possível, e as duas não se distinguem com estes dados.

### Predição 2: no descasado e no mutável, o P1 vence o P0, se a vida for longa

**O resultado diz:**
- **Contrastes:** P0 − P1 = **+0,076 [+0,050; +0,103]** no descasado e **+0,102 [+0,077; +0,129]** no mutável. O Holm rejeita os dois e
  os dois IC 90% ficam dentro de ±Δ (seção 0.1).
- **Inclinação nos dias 11 a 14:** não cresce. Descasado −0,010 [−0,049; +0,027]; mutável +0,031 [−0,002; +0,063].
- **Bloco de durações** (`duracoes.json`): o ganho P0 − P1 é +0,099, +0,076 e +0,085 no descasado e +0,108, +0,102 e +0,073 no
  mutável, a 7, 14 e 28 dias. O passo de 7 para 14 dias não difere de zero (descasado −0,023 [−0,059; +0,013]).

**Apoio teórico prévio:** APOIADA COM RESSALVA (a relação com a duração não é monotônica).
- Kozielska e Weissing 2024, texto completo.
- Dunlap e Stephens 2009, resumo.
- Liedtke e Fromhage 2019, texto completo: limiar e velocidade de aprender.

**Concordam?**
- **Direção:** concordam.
- **Forma:** concordam com a ressalva, não com o enunciado. O ganho já aparece aos 7 dias e não cresce com a vida; no mutável, encolhe
  aos 28. "Se a vida for longa" não se sustenta como condição: neste motor o ganho não depende da duração entre 7 e 28 dias.
- **Liedtke e Fromhage:** um limiar abaixo de 7 dias, se existir, não se distingue de um platô com estas três durações.
- **O mutável fica sem teoria dentro da vida** (adendo 3.2). O +0,102 descreve este motor e não testa teoria.
- **Valor e eficiência no mutável** (Eliassen et al. 2009, só resumo; seção 4):
  - o **valor** (P0 − P1) é positivo;
  - a **eficiência** é baixa: o P1 fica em 0,330 depois da troca, longe do ótimo 0.
- **As seções 0.1 e 0.2 pesam aqui:** o efeito está abaixo de Δ, e o nível de chegada, perto de 1/3, é o mesmo em todo mundo.

### Predição 3: o P2 chega à metade do caminho com menos consumos que o P1

**O resultado diz:**
- P1 − P2 nos consumos até a metade: **+11,4 [+1,0; +22,7]**. O Holm rejeita, com p ajustado 0,03.
- **Separação do cuidado (5.1):** o P2 contra o próprio só cuidado dá **−1,6 [−11,7; +8,2]** (a condição (a) falha). O só cuidado cuida
  pior: fora de privação +0,042 e saúde +0,022 a favor do P2 (a condição (b) falha).

**Apoio teórico prévio:** APOIADA, pela informação filtrada (Rendell et al. 2010, resumo).

**Concordam?** **Não se pode dizer.**
- O contraste primário confirma, mas o mesmo cérebro, sem a informação, no mesmo registro, chega à metade tão rápido quanto o P2.
- O ganho sobre o P1 não pode ser atribuído à informação. A teoria fala da informação; o resultado não a isola.

### Predição 4: o P2e piora no começo e se recupera quando o mundo refuta

**O resultado diz:**
- **(a) piora:** P2e − P1 na taxa inicial, **+0,0005 [−0,012; +0,013]**. Não rejeita.
- **(b) recupera:** P0 − P2e na taxa final, **+0,083 [+0,058; +0,110]**. Rejeita.
- **Leitura registrada:** inconclusivo. A (b) sozinha não basta, porque a (a) não apareceu.
- **O dia em que a curva do P2e cruza a do P0:** 3.
- **O peso da informação errada (`w_info`)** parte de 256 e cruza o zero nas 30 unidades até o dia 5. A média no fim da vida é −3004, e
  nenhuma unidade chega ao limite de −16128 (`w_info_p2e.json`).

**Apoio teórico prévio:** SEM APOIO DIRETO.
- A analogia da P-7 era o Eliassen, resumo: a velocidade de atualização.

**Concordam?** Não há teoria com que concordar. O que os dados dizem:
- **A informação errada quase não age.** A confiança de partida é baixa (`w0_info` = S/4, o ponto da K2), e o mundo a desfaz em dias.
- **O P2e não "segue o dono contra o mundo".** Mas também não há o que recuperar, porque ele não chegou a piorar.
- **O `w_info` fica negativo, não volta a zero.** O P2e passa a ler a informação errada **ao contrário**, o que, com uma fonte sempre
  errada, é informativo. Isso não é a "recuperação" da predição. É uma pergunta nova (seção 3, Q-6).

### Predição 5: o P3 não difere do P0 (equivalência)

**O resultado diz:**
- P3 − P0 na taxa final, no descasado: **−0,081**, IC 95% [−0,141; −0,007] e IC 90% [−0,132; −0,021] dentro de ±Δ. A leitura registrada é
  "confirma" (n = 25).
- **Separação do cuidado:** o P3 contra o próprio só cuidado dá −0,056 [−0,125; +0,022]. A (a) falha, e a (b) também: fora de privação
  +0,075, saúde +0,037.

**Apoio teórico prévio:** CONTESTADA.
- Ho et al. 2017, resumo: o feedback avaliativo funciona melhor como comunicação sobre o valor da ação do que como recompensa.

**Concordam?** Em parte. Aqui não há sobreposição de regras: a equivalência é o critério de "confirma".
- Pela regra, a predição confirma. Mas o IC 95% fica inteiro abaixo de 0: o P3 come menos a fruta ruim que o P0, numa diferença menor
  que Δ.
- A contestação de Ho et al. dizia que o P3 poderia fazer mais que o P0. Ele faz um pouco mais, dentro da margem.
- A separação do cuidado não deixa atribuir essa diferença ao ensino.

---

## 2. O que se pode afirmar e o que não se pode

**Pode-se afirmar** (neste motor, nestas 30 unidades, com o dono atencioso):
1. **A direção das predições 1 e 2:** um aprendiz pela consequência (P1) come mais a fruta ruim que o herdado onde o herdado acerta, e
   menos onde ele erra. Os efeitos são estatisticamente claros e **menores que a margem de relevância** registrada.
2. **Sem crescimento com a vida:** o ganho do P1 no descasado e no mutável aparece aos 7 dias e não cresce até 28.
3. **A informação errada (P2e)** não fez o pet comer mais a fruta ruim no começo, e o peso dela cruzou o zero em todas as unidades até o
   dia 5.
4. **O P3 fica dentro da margem do P0,** mas abaixo dele.

**Não se pode afirmar:**
1. **Que algum efeito do dono é ensino.** Pela seção 5.1, as condições (a) e (b) falham no P2, no P2e e no P3. Além disso, o controle é
   suspeito: o só cuidado acoplado rejoga em malha aberta um cuidado que foi dado ao pet original e cuida pior que ele (decisão de
   2026-10-06). **A régua não serve nesta montagem:** nem "é ensino" nem "não é ensino".
2. **Que a informação certa acelera o aprendizado** (predição 3). O contraste confirma, mas o mesmo cérebro sem a informação chega lá tão
   rápido.
3. **Que o P1 aprende qual fruta faz mal.** As taxas finais perto de 1/3 em todo mundo, com ou sem informação, são compatíveis com apagar a
   preferência inata. A distinção não foi medida (seção 3, Q-1).
4. **Nada de teoria sobre o mutável.** Os modelos disponíveis tratam mudança entre gerações (adendo 3.2).
5. **Que "vida longa" é condição da vantagem.** O platô vai de 7 a 28 dias; abaixo de 7 dias não foi medido.
6. **Nada sobre animais, pessoas, outros donos ou outros mundos.** E nada sobre os cérebros B e C: a comparação A × C não terminou, e o B
   "não fecha" e saiu da escolha (decisão de 2026-10-06).

---

## 3. Os achados secundários, como perguntas novas

Todos são descritivos, fora do Holm primário. Nenhum se lê como confirmação.

| # | o que se viu (com o artefato) | o que não se pode concluir | pergunta nova |
|---|---|---|---|
| Q-1 | Braços plásticos com taxa final ≈ 1/3 em todo mundo e duração (`frutas/tabelas.json`, `duracoes.json`) | que o aprendiz aprende qual fruta faz mal | **O aprendiz apaga a preferência inata ou aprende o efeito?** Medir a fração de consumo por fruta e a escolha nas ofertas com uma fruta só |
| Q-2 | **P2d antes do P2:** P2 − P2d nos consumos até a metade, **−12,8 [−23,4; −3,0]**; a taxa final não muda (`p2d_p3i.json`) | que informar depois do consumo ensina melhor. O P2d recebe outra quantidade e outra composição de informações (75,9 contra 96 por vida), e nem o P2 passou do próprio só cuidado | **Informar sobre a fruta que acabou de ser comida ajuda acima do mesmo cérebro sem a informação?** O P2d contra o próprio só cuidado, com a quantidade de informações igualada |
| Q-3 | **P3 melhor que o P3i:** P3 − P3i, **−0,111 [−0,217; −0,003]** no descasado e **−0,094 [−0,178; −0,014]** no mutável | que tratar o julgamento como recompensa é melhor que como informação: no P3i o `w_info` não aprende (o P3 não aprende pela consequência), então o P3i é a informação com peso fixo baixo | **Com o peso da informação aprendendo (ou fixo nos dois), a interpretação ainda importa?** É o teste que chega mais perto de Ho et al. 2017 |
| Q-4 | **A memória ajuda no mutável:** P1 sem memória − P1 completo, **+0,014 [+0,004; +0,024]** depois da troca; no descasado −0,002 [−0,011; +0,008] (`blocos.json`) | que a memória serve à mudança em geral. O efeito é pequeno e só existe um mutável (uma troca, no meio da vida) | **A memória de episódios ajuda a acompanhar uma troca dentro da vida, e a recuperação relevante vence a de recência depois dela?** O bloco N6 (G-REC +0,028 [+0,011; +0,044]) só foi medido no descasado |
| Q-5 | **Os canais não mudam nada:** −0,005 [−0,013; +0,004] no descasado e −0,002 [−0,010; +0,007] no mutável | que os canais são inúteis (H-R2). No mundo das frutas, só o canal do humor distingue as frutas (a nutrição é igual), então separar canais não muda o que se credita à escolha da fruta | **Num mundo em que duas consequências apontam para lados diferentes (por exemplo, uma fruta que alimenta e faz mal), os canais mudam a atribuição?** É o desenho do teste mínimo da H-R2 |
| Q-6 | **O P2e passa a ler a informação ao contrário:** `w_info` médio −3004 no fim, todas as unidades abaixo de zero (`w_info_p2e.json`) | que o pet "aprende a desconfiar" no sentido de ignorar. O peso negativo usa a informação invertida | **Uma fonte sempre errada vira informativa quando invertida, e o que acontece com uma fonte que erra só às vezes?** |
| Q-7 | **As durações dão platô:** o ganho P0 − P1 não cresce de 7 a 28 dias; no mutável cai aos 28 (+0,073) (`duracoes.json`) | que não há limiar. Abaixo de 7 dias não foi medido | **Abaixo de 7 dias há limiar, e uma taxa de aprendizado maior desloca ele** (Liedtke e Fromhage 2019)? |

**A pergunta que atravessa P2, P2e e P3** (decisão do Matheus de 2026-10-06): **um controle de cuidado em malha fechada.** É um braço que
recebe o cuidado reativo do mesmo dono, sem os sinais e sem a informação. Sem ele, nenhuma predição com dono pode ser lida como ensino.

---

## 4. L-1: o texto completo do Eliassen et al. 2009

**Tentativas** (2026-10-06):

| fonte | o que deu |
|---|---|
| Unpaywall | nenhum local aberto |
| Semantic Scholar | `CLOSED` |
| OpenAlex | só a página do editor e o PubMed, sem PDF aberto |
| NVA (o repositório nacional da Noruega, que substituiu o BORA da Universidade de Bergen) | registro sem arquivo associado |
| PDF do editor (journals.uchicago.edu) | HTTP 403 |

**Resultado:** **não há acesso aberto.** O Eliassen et al. 2009 fica conferido **só pelo resumo** (PubMed 19694535).
- A leitura de valor × eficiência (predição 2, mutável) e a analogia da velocidade de atualização (predição 4) apoiam-se só no resumo.
- Nenhum mecanismo nem número do modelo é citado.
- Ler o texto pede acesso institucional ou um pedido aos autores (decisão V-5).

---

## 5. Decisões que só o Matheus pode tomar

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| V-1 | **Como rotular as predições 1 e 2**, que cumprem ao mesmo tempo o "confirma" (positivo pelo teste) e o "refuta" (IC 90% dentro de ±Δ) da regra registrada | **"Confirma na direção, abaixo da margem de relevância"**, com os dois critérios ao lado. Nos planos futuros, regras que não se sobreponham (por exemplo, "refuta por empate" só quando o teste não rejeita) | só "confirma" esconde que o efeito é menor que a relevância que o próprio plano fixou; só "refuta" apaga um efeito estatístico claro na direção prevista |
| V-2 | **Controle de cuidado em malha fechada** como pergunta nova, com plano e sementes próprias | **Sim, depois da comparação A × C.** É o que falta para qualquer leitura de ensino nas predições 3 a 5 | sem ele, as predições com dono ficam ilegíveis como ensino; rodá-lo nestas sementes reabre a validação única |
| V-3 | **O platô de cerca de 1/3** (Q-1) | **Pós hoc descritivo, rotulado como tal,** nas vidas da validação regeneradas da config: a fração de consumo por fruta e a escolha nas ofertas com uma fruta só. Sem gate e sem mudar nenhuma leitura registrada. Se pedir desenho novo, vai para plano próprio | sem ele, a leitura da predição 2 ("o aprendiz corrige o prior") pode ser só "o aprendiz apaga o prior"; tratá-lo como confirmatório seria ler a validação duas vezes |
| V-4 | **Quais perguntas da seção 3 viram planos** | **Q-1 primeiro** (barata, muda a leitura de tudo); depois Q-3 (a mais próxima da contestação da predição 5) e o controle da V-2. Q-2, Q-4 a Q-7 ficam como ideias registradas | abrir todas juntas repete o que a revisão 3 do roadmap quis evitar: peças novas sem a pergunta principal fechada |
| V-5 | **O L-1 (Eliassen)** | **Fechar como "sem acesso aberto; só resumo"**; pedir o texto aos autores só se a leitura consolidada da fase 1 for usar valor × eficiência como argumento | citar mecanismo do modelo sem ler o texto viola as regras de citação; perseguir o texto agora atrasa a leitura sem mudar nenhum resultado |
| V-6 | **O que vai para a leitura consolidada da fase 1** | **As listas da seção 2** ("pode" e "não pode"), com a comparação A × C entrando só quando o chat D terminar | levar "o aprendiz aprende o que faz mal" ou "o dono ensina" para a leitura consolidada é afirmar o que os dados não sustentam |
