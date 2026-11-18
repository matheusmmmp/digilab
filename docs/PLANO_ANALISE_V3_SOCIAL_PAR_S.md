# PLANO DE ANÁLISE V3 — SOCIAL_PAR S: o substrato que deixa o social aparecer

- **Status:** APROVADO pelo Matheus em 2026-11-18 ("Aprovado"), com as decisões S-1 a S-8 da seção 10 como DECIDIDAS. Nenhuma vida
  rodou antes desta aprovação.
- **Snapshot:** a `main` em 8c6d17ae (2026-11-18), com o branch da S0 (`v3-social-par-s0`, PR #1000), que fica em cima do da run do A0
  (#998). O plano depende dos artefatos dos dois.
- **Pedido:** a fase S1 do pedido do Matheus de 2026-11-18. O Matheus aprovou a S0 e a ordem dos bloqueios: "Aprovado, B1 e B2".
- **Executor:** Claude Code, Opus 5.5.

## 0. A pergunta

**Com um substrato em que o encontro não é feito pela casa e a bola está ao alcance, o parceiro que responde muda o que o focal faz?**

O A0 respondeu "não acima da margem", mas a S0 mostrou por quê (`docs/OBSERVACAO_V3_SOCIAL_PAR.md`). Perto é 64 % da vida, porque a casa
puxa os dois: todo `explorar` tem um candidato fixo, a casa, que é o comedouro (`digilab/mundo.py`, o `Alvo("casa", …)` dos candidatos do
explorar). E F volta sozinho: em 193 de 201 pares, o T\* com P gravado é exatamente o de P vivo. A bola está a ~30 células da casa, e o
`brincar` só mira a bola dentro do raio de visão, de 6 células: o pet escolhe brincar ~12 vezes por vida e chuta 2 vezes em 420 vidas de
pet.

**Por isso o A0 não sabe dizer se o social não existe ou se o substrato não o deixa ver.** Este plano separa os dois casos com dois
braços de substrato e um controle positivo em cada braço.

## 1. O que entra e o que fica fora

- **Entram dois bloqueios,** como o Matheus aprovou:
  - **B1, o efeito-teto:** o encontro feito pela casa;
  - **B2, a bola morta:** a bola fora de alcance.
- **Ficam fora:**
  - **B3, o sono:** os dois dormem 45 % da vida, e dormir junto é o acaso (1,02; S0, seção 3). Mexer no reflexo do sono é a frente CORPO;
  - **B4, a gravação:** os desvios de P gravado mudam a janela, mas não o T\* (S0, seção 7). Só importa depois do B1, e o descritivo o
    acompanha;
  - **B5, a CO7:** ela muda 7 de 201.600 decisões (S0, seção 5). Fica como está, ligada nos dois, como no jogo v39;
  - **os mecanismos sociais M1–M4:** nenhum mecanismo novo no pet.
- **Nenhuma mudança no pet nem no jogo.** Os dois braços mudam só a intervenção do experimento no t0, como o `levar_pet` do A0: o
  cérebro, o corpo, o mundo e o layout são os de hoje. Os saves e a paridade com a web não mudam, e não há ovo v40.
  - **O que isso deixa de fora:** se a bola perto ou o encontro fora da casa devem virar mecânica do jogo é decisão de produto, e é do
    Matheus. Não entra aqui.

## 2. Os braços

Os três braços vivem a mesma vida do A0 até o t0:
- o pet de hoje, o modular com a CO7 nos dois, como o jogo v39;
- o dono "atencioso" no comedouro;
- 5 dias;
- o t0 sorteado em [1440, 4320] ticks;
- o d0 = 12 células;
- a janela de 96 decisões;
- as cinco vidas por par: base, base-OUTRA, VIVO, GRAV e OUTRA.

**Cada braço muda só o que acontece no t0:**

| braço | o que acontece no t0 | o bloqueio |
|---|---|---|
| **C, o controle** | F é levado a 12 células de P, como no A0 | nenhum (a A0 refeita nas sementes novas) |
| **B1, fora da casa** | P é levado a um ponto Q sorteado no campo ou na mata (x de 34 a 60 células), e F a 12 células de Q, fora da casa (x ≥ 16) | o encontro pela casa |
| **B2, a bola perto** | F é levado como no C, e a bola é posta parada na posição de P | a bola fora de alcance |

**Os detalhes que mudam a gravação:**
- **No B1, as vidas base também levam P a Q no t0.** Na base, F não é levado. Assim a gravação de P já começa fora da casa, e a GRAV e a
  VIVO são iguais até o t0, como pede o G-INSTR. Q e a direção de F saem de uma rng própria,
  `derivar_semente("social-par-s-q", semente)`.
- **No B2, as vidas base também recebem a bola no t0,** no mesmo ponto. A bola é posta pelo experimento, com a origem `intervencao` no
  registro (o `Grupo.deixar_bola` de hoje grava a origem `dono`; a S2 acrescenta a variante de intervenção, como o `levar_pet`).
- **A condição para o t0:** no B1, os dois pets precisam estar acordados, porque o `levar_pet` recusa um pet dormindo (PP-2). O t0 é o
  primeiro passo depois do sorteado em que os dois estão acordados (no A0, bastava F). No C e no B2, a regra é a do A0.

**Por que o B1 não é só um d0 maior** (o pedido sugeria 18 ou 24 células): com o candidato "casa" em todo explorar, F volta para a casa de
qualquer distância, e P está na casa. Um d0 maior aumenta o T\* sem tirar a causa comum. No B1, os dois começam fora da casa, e o encontro
só sai pela casa se os dois voltarem para ela. O descritivo mede onde o reencontro acontece. Se o Matheus preferir o d0 maior, ele entra
como um quarto braço, sem mudar os outros.

## 3. O controle positivo de cada braço: G-DET

**O instrumento precisa mostrar que vê o social quando ele existe, no mesmo substrato.** Esse é o "o social aparece acima da margem quando
existe" do pedido.

- **Como:** em cada braço, 50 pares com F, o modular de hoje, e com **P trocado pelo `SeguidorPuro`** da E1 (`experiments/bancada/parceiro.py`),
  que anda até F. Na VIVO, P segue o F deslocado. Na GRAV, P é a gravação da base, em que F não foi deslocado, e não segue. O previsto é
  um D_A claramente negativo.
- **O gate G-DET de cada braço:** o IC95 do D_A do controle positivo fica todo abaixo de −δ_A (−4 decisões), a classe "< 0" da seção 7
  com a margem.
- **O que ele decide:** um braço em que o G-DET falha **não lê o D_A dos pets de hoje**. O resultado do braço é "o substrato não deixa ver"
  (seção 7).
- **O B não tem controle positivo:** não há um parceiro de regra que chute em resposta. É uma lacuna declarada. O B0 de cada braço só se lê
  pela premissa PB-1.

## 4. As unidades e as sementes

- **K = 200 sementes independentes por braço:** as bases 103001…103200, cada uma com k = 1. É uma semente por base, e não 5 bases com 42
  derivações, como no A0. O pedido chama isso de "o erro da V2".
- **As mesmas 200 sementes nos três braços** (números aleatórios comuns): os braços diferem só pelo t0.
- **O G-DET:** as bases 103301…103350, k = 1, em cada braço.
- **A faixa reservada:** 103001…103400, em `experiments/bancada/faixas.py`, com esta fonte. Ela foi conferida livre no `faixas.py`, nos
  planos e nas configs da `origin/main` e de todos os branches remotos em 2026-11-18.
- **As células:**
  - **são as do A0:** 1 dono (atencioso) × 1 lugar (comedouro);
  - **a correção:** o pedido fala em "3 lugares × 2 doadores", mas o A0 não teve isso, e acrescentar lugares e donos muda mais de uma coisa
    por braço;
  - **se o Matheus quiser mais células,** elas entram como um adendo.
- **Os prefixos:** `social_par_s` (a run) e `social_par_s_det` (o G-DET), na `PREFIXOS_UNIDADES`, junto com o código da S2.

## 5. As medidas

**São as do A0, sem mudança** (`docs/PLANO_ANALISE_V3_SOCIAL_PAR_A0.md`, seções 3 e 5), em cada braço:
- **o primário do A:** D_A = T\*_VIVO − T\*_GRAV, o tempo até o raio perto (6 células) restrito à janela;
- **o primário do B:** D_B = E_VIVO − E_GRAV, o excesso de alternância dos chutes de F para P sobre os 81 substitutos circulares;
- **os secundários S1, S2 e S3** com o Holm;
- **as premissas:** PA-1, PA-2 e PA-3 para o A e PB-1 para o B, com os mesmos limiares. O A0 só lia uma premissa falha como "inconclusivo
  por premissa", e aqui é igual.

**As medidas novas são descritivas e não decidem nada:**
- **o substrato:**
  - **B1, o T\*:** a média do T\*_GRAV e a fração de reencontros fora da casa (o ponto do reencontro com x ≥ 16 células). O previsto,
    PROPOSTO, é T\*_GRAV > 30 decisões;
  - **B2, os chutes:** os chutes de cada pet na janela e por dia, e os pares elegíveis na PB-1. O previsto, PROPOSTO, é mais de 1 chute por
    dia de P e ao menos 100 elegíveis;
- **a riqueza do que os dois fazem juntos:** as medidas da S0 sobre as vidas VIVO de cada braço:
  - a fração perto;
  - a razão observada/esperada de comer, dormir, explorar e brincar juntos;
  - quem fecha a distância;
  - as disputas pela comida;
  - os contatos;
  - o efeito de presença.

## 6. As margens e o N

- **δ_A = 4 decisões e δ_B = 0,05,** as do A0 (A0-5 e A0-6), SEM FONTE. Elas não mudam, para os braços se compararem com o A0.
- **O N = 200 por braço é fixo,** como o pedido manda. Não há piloto para o N. A meia-largura efetiva do IC vai no relato.
  - No A0, o dp do D_A foi 1,30. Com N = 200, a meia-largura seria ~0,18, muito abaixo de δ_A/2.
  - Nos braços novos, o dp pode ser bem maior, porque o T\* deixa de ser curto. Se a meia-largura passar de δ_A/2 = 2, o relato diz isso,
    e a leitura segue a seção 7.

## 7. A regra de leitura, escrita antes

**O A de cada braço, nesta ordem:**

| o G-DET do braço | o D_A dos pets de hoje | a leitura |
|---|---|---|
| falha | qualquer | **o substrato não deixa ver:** o braço não diz nada sobre o pet de hoje |
| passa | **≈ 0** (o IC dentro de ±δ_A) | **nulo com um instrumento que vê:** o pet de hoje não responde ao parceiro neste substrato |
| passa | **< 0** ou **> 0** fora de ±δ_A | **o social aparece:** o parceiro que responde muda o reencontro |
| passa | indeterminado | registrado como está; nada se decide |

**O B de cada braço:**
- a PB-1 falha (menos de 100 elegíveis): **inconclusivo por premissa,** e o B2 não deu substrato;
- a PB-1 passa: a classe do D_B pela margem, como no A0 (≈ 0, < 0, > 0 ou indeterminado). Não há G-DET para o B (seção 3).

**O conjunto:**
- **o G-DET passa no B1 e o D_A dá ≈ 0 no B1:** o social não existe no pet de hoje, mesmo num substrato que o deixa ver. O próximo passo
  é mecanismo (M1–M4), não mais substrato;
- **o G-DET passa e o D_A não é ≈ 0 em algum braço:** o substrato resolveu, e o próximo passo é descrever esse caminho antes do M1;
- **o G-DET falha no B1 e no C:** o substrato ainda não deixa ver, e a S2 precisa de mais braços, numa rodada nova com plano novo.

**O que se prevê, PROPOSTO:**
- **no C:** o G-DET passa por pouco ou falha. A casa ajuda o seguidor só um pouco, e o T\* curto deixa pouco espaço;
- **no B1:** o G-DET passa, e o D_A dos pets de hoje dá ≈ 0. A S0 não mostrou nenhuma resposta de um pet ao outro;
- **no B2:** a PB-1 passa ou fica perto. O B0 sai ≈ 0 se passar.

Nada disso muda a leitura.

## 8. Os gates do código (na S2)

- **G-INSTR:** em todo par, a VIVO e a GRAV são iguais até o t0, nos três braços.
- **G1:** a VIVO pelo `reproduzir_grupo`, e a GRAV e a OUTRA refeitas da gravação lida do disco, como no A0.
- **G-C-IGUAL-A0:** o braço C refaz uma vida do A0 (as sementes de teste 101 e 202) com o mesmo sha256 do orquestrador do A0. A troca
  do orquestrador não pode mudar o controle.
- **G-DESLIGADO:** sem a intervenção nova, a vida é a de hoje byte a byte, e os testes da E1 e do A0 passam sem mudança.
- **A suíte inteira** roda antes da run, com as falhas conhecidas registradas.

## 9. O custo

- **Vidas:** os 3 braços × 200 pares × 5 vidas = 3.000, e os 3 braços × 50 pares do G-DET × 5 vidas = 750.
- **Tempo:** a ~9 s por par com o G1 (o A0), 750 pares com 4 processos levam uns 30 minutos de parede.
- **A máquina:** no máximo 4 processos, e uma run de pesquisa por vez (V3-D8), pelo `pre_run`.

## 10. As decisões (DECIDIDAS pelo Matheus em 2026-11-18, "Aprovado")

| | a decisão | a recomendação | o custo de errar |
|---|---|---|---|
| S-1 | os braços C, B1 e B2, com B3, B4 e a CO7 fora | sim | baixo: um braço a mais é um adendo |
| S-2 | o B1 como encontro fora da casa, e não um d0 maior | sim | médio: um d0 maior repetiria o efeito-teto com outro número |
| S-3 | o G-DET com o `SeguidorPuro` como P, e o "substrato não deixa ver" quando ele falha | sim | alto: sem ele, um ≈ 0 não se distingue de um instrumento cego |
| S-4 | K = 200 bases independentes, as mesmas nos três braços, e 50 para o G-DET | sim | baixo |
| S-5 | a faixa 103001…103400 | sim | baixo |
| S-6 | as margens e as medidas do A0, sem mudança | sim | baixo |
| S-7 | as células do A0 (atencioso × comedouro), e não "3 lugares × 2 doadores" | sim | médio: mais células mudam mais de uma coisa |
| S-8 | nenhuma mudança no pet nem no jogo: os braços são intervenções do experimento no t0 | sim | baixo: virar mecânica é outra decisão |

## 11. Adendo 1 (PROPOSTO, 2026-11-18): o parceiro não vê o focal deslocado

**O que se achou ao começar a S2,** antes de qualquer vida e antes do código do orquestrador:
- **O pet de hoje só percebe o outro a até 6 células.** A percepção social filtra os outros pela distância de visão (`digilab/mundo.py`, o
  `perceber_social`, com `d <= raio_visao`, e o `raio_visao_celulas` é 6). O cheiro e o som do outro existem só atrás da
  `ConfigSentidos` (V2, dois pets, etapa 8), que vem desligada e não está no jogo.
- **No A0, F é levado a 9–12 células de P, onde nenhum dos dois vê o outro.** O T\* é o tempo até 6 células, que é exatamente o raio da
  visão. **Por construção, P não pode responder a F antes do reencontro,** e por isso o T\* da GRAV é o da VIVO em 193 de 201 pares (a S0,
  seção 4). F volta pela casa (o candidato fixo do explorar), não porque vê P.
- **O efeito no plano aprovado:**
  - **o G-DET falharia em todos os braços:** o `SeguidorPuro` só segue quem vê, então na VIVO ele fica ocioso, longe de F;
  - **o B1, sozinho, não muda isso:** fora da casa, os dois continuam sem se ver depois do deslocamento.

**A proposta: o deslocamento fica dentro da visão, e o primário passa a ser o tempo até o contato.**
- **A1-1, o d0 = 5 células em linha reta** (de 4 a 5 pelo maior eixo, dentro das 6 da visão). No t0, os dois se veem, e P pode seguir,
  fugir ou ignorar F desde o primeiro passo. Isso vale para os braços C, B1 (F a 5 células de Q) e B2.
- **A1-2, o primário do A passa a ser o tempo até o contato:** D_A = T\*c_VIVO − T\*c_GRAV, com T\*c o tempo até 1 célula (o raio do
  contato, a medida `metrics.tempo_restrito` com o raio 1), restrito à janela de 96. O par é elegível com a distância > 1 no t0. A δ_A
  continua 4 decisões. O tempo até 6 células sai do primário, porque com d0 = 5 ele já começa alcançado.
  - **As premissas:** a PA-2 conta os elegíveis pela distância > 1. A PA-3 conta os com contato na janela.
  - **Os secundários:** os S1, S2 e S3 continuam, com o S1 sobre o T\*c.
- **A1-3, o G-DET continua com o `SeguidorPuro`:** agora ele vê F no t0.
- **A1-4, o controle C deixa de ser a A0 refeita,** porque o d0 e o primário mudam. A run do A0 (#998) fica como a referência do d0 = 12.
  O gate G-C-IGUAL-A0 vira um teste do código: com o d0 = 12, a perturbação de tupla refaz as vidas do A0 com o mesmo sha256.
- **O resto não muda:** os braços, o B1 fora da casa, o B2 com a bola na posição de P, as sementes, a faixa, as margens, a regra de leitura
  da seção 7 e o custo.

**A alternativa, não recomendada: ligar os sentidos** (o cheiro do outro até 24 células e o som até 16) nos dois pets. É mudar a percepção
do pet, o que o pedido chama de M1, a "percepção do outro", e o pedido proíbe antes da S4. E não é o pet do jogo.

**O custo de errar:** é alto. Sem o adendo, a run da S3 sai cega por construção: o G-DET falha, e os três braços dão "o substrato não
deixa ver".

| | a decisão | a recomendação |
|---|---|---|
| A1-1 | o d0 = 5 células, dentro da visão | sim |
| A1-2 | o primário do A pelo tempo até o contato (1 célula), com a δ_A = 4 | sim |
| A1-3 | o G-DET com o `SeguidorPuro`, como antes | sim |
| A1-4 | o C com o d0 novo, e a run do A0 como a referência do d0 = 12 | sim |
