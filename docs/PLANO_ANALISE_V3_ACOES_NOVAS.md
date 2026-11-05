# PLANO DE ANÁLISE V3 — AÇÕES NOVAS: o passeio ligado contra desligado (AN3; 2026-11-05, worker da AN3, Claude Code, Opus 5.5)

**Status: APROVADO pelo Matheus em 2026-11-05 ("Aprovo e mescle").** As decisões AN3-1 a AN3-9 (seção 13) DECIDIDAS, todas pela recomendação. **Nenhuma
vida da faixa 78101…78505 rodou nem roda antes de quatro coisas:** este cabeçalho com a marca "APROVADO pelo Matheus"; o código do passeio
(a AN2) na `main`, com o G2-py; a medida do movimento em `digilab/metrics.py` e o orquestrador da AN4, com a trava e a varredura (seção
11); e o registro da run (seção 11), num commit empurrado antes da primeira vida.

**De onde vem:** a `docs/TAREFA_V3_ACOES_NOVAS.md` (a pergunta da seção 1, a mudança mínima da seção 3, o experimento da seção 4 e as AN-1 a
AN-7 da seção 8, DECIDIDAS pelo Matheus em 2026-11-04), o descritivo de hoje (a AN0, seção 10 da tarefa; `artifacts_v3_acoes_novas/hoje.json`)
e a conferência dos gabaritos (a AN1, seção 11). **Este plano reusa, sem mudar,** do `docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md`:
o cenário (A6.2), a taxa de fechamento por episódio de fome (o G-MVP-EP de A3.3, com a W(d₀) de A3.2, a medida de A6.4), a G-ELEGIVEL-EP
(A6.4), a unidade (base, semente) e o IC95 do t sobre as unidades (A4.4.6), a ressalva do g1 (A4.4.6), a classe de cada contraste (a regra
de A6.6, com a margem deste plano), a fórmula do poder (A6.5), as medidas da C5 (A6.8, item 4; AD6-4) e a forma da guarda G-COMEDOURO
(A8.4 e AD8-5; A9.4 e AD9-9).

**A fonte dos números novos:** o `experiments/plano_an3_poder_acoes_novas.py`, que só lê artefatos do git: o `medidas.json.gz` da C4
(77101 a 77505, 14 400 vidas; sha256 `8b48d0a2…d93b`, e o descomprimido `869ff397…3023`, os registrados na seção 16 do
`docs/RESULTADO_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md`) e o `meta.json` da mesma run (`6315784c…3a18`), conferidos pelo script antes da conta.
Ele grava `artifacts_v3_acoes_novas/plano_an3_poder.json` (sha256 `7b1168c2…aa77`) e, rodado duas vezes, sai igual, byte a byte
(`tests/test_plano_an3_poder.py` confere contra uma execução nova). **Nenhuma vida, nenhum replay e nenhuma semente nova.** Abaixo,
**[poder]** é esse artefato e **[AN0]** é o `hoje.json`.

**O que este plano não afirma:** que o passeio aumenta o apego do jogador (não se mede no Python; a tarefa, seção 1), que o pet "parece
parado" ou "parece passear" ao jogador (SEM FONTE; é do Matheus, jogando), que o modular supera o A, ou que algum cérebro está pronto. Os
contrastes são entre dois braços do próprio modular e medem uma subchave, num cenário. **Nenhuma alegação de novidade:** pets que andam
sozinhos estão em quase todo jogo da pesquisa de referências (a tarefa, seção 9).

## 0. O que não muda

- **O motor, o corpo, o mundo, o cheiro, o `longe_fixo`, o `engine.py`, o A, os pets v11 a v17 e o jogo web.** No cérebro, tudo o que está
  na `main` e o que a AN2 traz atrás da `passeio` (a tarefa, 3.1 a 3.4), como a AN2 for mesclada. **Nenhuma mecânica nova nesta etapa nem
  na AN4:** o código novo da AN4 é só o orquestrador, a medida do movimento (seção 4.3) e os dois braços.
- **Os valores:** os inatos do #428, os da memória (seção 8 da espec da C4) e o `urgencia_lambda` (S/2, PROPOSTO; a AN-4), iguais nos dois
  braços. **Nenhuma calibração e nenhum piloto** (a tarefa, seção 4: a calibração fica para a rodada de equilíbrio, no fim): a variância vem
  das vidas já gravadas da C4 (seção 6).
- **A C2, a C3 e a L-2 ficam desligadas nos dois braços,** como no REL da C4 (a MA-7).
- **As faixas gastas** (64xxx, 66xxx, 67xxx, 71xxx, 75xxx, 76xxx, 77xxx) não entram em nada, salvo a leitura dos artefatos que já estão
  no git.
- **Os resultados anteriores:** nada aqui muda a C1 (#510), a C2 (#517), a C3 (#527) nem a C4 (#541).

## 1. A pergunta e as previsões, escritas antes

**A pergunta** (a tarefa, seção 1): um passeio sem alvo de necessidade, disparado pelo tédio e pela curiosidade que o corpo já tem, faz o pet
com o DigiBrain modular se mover mais e de forma legível, **sem piorar o cuidado das necessidades perto do comedouro?** A run responde à
segunda metade com um gate (a guarda) e à primeira com uma leitura sem limiar (o movimento; a AN-1).

**O dado de hoje** [AN0]: o vagar é 19,1 % das 5 376 decisões gravadas (26,0 % no comedouro da LM0); 75 % das corridas de vagar têm uma
decisão só; cada decisão de vagar já anda (média 60,0 unidades de posição, 0,15 % sem sair do lugar), e 94 % das decisões fora do explorar
não saem do lugar; 26,7 % das decisões de vagar têm a fome, a higiene, a energia ou a saúde acima do `urgencia_lambda`.

**As previsões (PROPOSTAS; escritas aqui antes de qualquer vida):**

| contraste | lugar | o que é | a previsão | o papel |
|---|---|---|---|---|
| **G-COMEDOURO-AN: LAB+P − LAB** | comedouro | a taxa por episódio com o passeio contra sem ele | **não "< 0"** | **a guarda, o único gate** (seção 7) |
| **MOV: LAB+P − LAB** | as 8 células | a fração das decisões fora do dormir em que o pet sai do lugar | **> 0, com um nulo plausível** | a leitura do produto, sem limiar (seção 7) |
| **LONGE-AN: LAB+P − LAB** | `longe_fixo` | a taxa por episódio longe da ração | **sem previsão de sinal** | secundária, sem gate |

- **A guarda não "< 0"** vem do desenho da tarefa (3.2): a persistência do passeio é 0 acima do limiar, e o passeio acaba `interrompido`
  quando uma necessidade aperta. É previsão do desenho, SEM FONTE externa. Um "< 0" fica registrado como está.
- **O nulo plausível do MOV fica escrito antes:** pelo [AN0], toda decisão de vagar já sai do lugar; o passeio muda para onde o pet anda
  (o mesmo destino por várias decisões), não se cada decisão anda. O MOV só sobe se a persistência fizer o explorar ganhar decisões que hoje
  são de ficar parado (o ocioso, o chamar, o emburrar). Um passeio que segura o destino e não muda a fração das decisões que andam é um
  resultado possível, e ele não diz que o passeio "não funciona": o zigue-zague é lido no descritivo (seção 8, item 2).
- **O LONGE-AN sai sem previsão** (a tarefa, seção 4): o passeio pode ajudar a achar a comida longe ou atrapalhar a ida.

## 2. O desenho

- **O cenário:** o da C4 (A9.2, que é o da C1, A6.2), sem mudança: o `CONFIG_MUNDO_MVP`, o corpo do v11, o contrato da P4 desligado, o pet
  sozinho, os quatro donos sem ensino (atencioso, relapso, aleatório, incoerente), **14 dias, orçamento de 16 por dia,** morte desligada
  (AN3-1).
- **Os lugares (AN3-1; a tarefa, seção 4, "os do MVP"):** o **comedouro** na guarda (4 células) e o **`longe_fixo`** na secundária (4).
  São **8 células por unidade.** O longe sorteado e o perto não rodam.
  - **A célula repetida, como na C4:** com o `sem_ensino`, a vida do incoerente no comedouro é byte a byte a do atencioso no comedouro
    (`CELULA_DUPLICADA` do orquestrador do protótipo, adendo 2). Ela fica nas 4 células do comedouro, como ficou na C3 e na C4, e o σ da
    seção 6 já a inclui.
- **Os braços (AN3-1):**

| braço | no código | o que é | o papel |
|---|---|---|---|
| **LAB** | `config_do_braco("REL", conserto=True)` (`SUBCHAVES_C4["REL"]`) | a configuração do pet de teste: o M3\* do conserto com a `memoria_autobio` REL, sem as facetas, sem a C2, a C3 e a L-2 (a `docs/TAREFA_V3_LAB_MODULAR.md`, seção 5) | o controle |
| **LAB+P** | a mesma, com a `passeio` ligada (o nome é a AN-2) | o LAB com o vagar que segura o destino (a tarefa, 3.1 a 3.4) | o braço novo |

- **As vidas:** 2 braços × 8 células = **16 vidas por unidade.**
- **O pareamento:** por unidade e célula. Os dois braços vivem a mesma semente, o mesmo genoma, o mesmo dono e o mesmo lugar; só a
  `passeio` muda. A rng do dono e a dos lugares fixos não dependem do braço (a regra das rngs separadas); o ponto do passeio é o candidato
  `vagar` que o motor já sorteia (a tarefa, 3.1, item 2), sem rng nova.
- **Se a AN2 entrar na `main` com outra forma** (outro nome da subchave, outra regra de fim, uma dependência de outra subchave): o braço
  LAB+P é "o LAB com o passeio da AN2 como mesclado". Uma diferença que mude uma medida deste plano (um fim a mais, um campo do motivo que a
  seção 4 lê) é registrada como desvio antes da run, e uma que mude a guarda pede adendo.

## 3. As sementes e a faixa

- **A faixa: 78101…78505** (AN3-9), conferida livre em 2026-11-05: nenhuma faixa de `FAIXAS_RESERVADAS` nem de `FAIXAS_QUEIMADAS` a cruza,
  e nenhum inteiro de semente ou base das configs de `experiments/configs/` cai nela (o único "78125" lá é dígito de um decimal, em
  `sombrias/r0_resultado.json` e `r1_resultado.json`). **Ela entra em `FAIXAS_RESERVADAS` neste PR,** num commit próprio (o primeiro), com a
  fonte (este plano, PROPOSTO), a pedido do coordenador; `tests/test_faixas_r17.py` passa com ela.
- **As bases:** 78101, 78202, 78303, 78404 e 78505.
- **O K: 40 por base, 200 unidades** (PROPOSTO; seção 6 e AN3-2). São **3 200 vidas.**
- **A derivação:** `bancada_v2.unidades_derivadas(bases, K, prefixo="digibrain_prototipo")`, o prefixo da reavaliação, da L-2 e das C1 a
  C4 (como a AD6-5). A função falha alto com colisão, e o `meta.json` grava as unidades.
- **A run roda uma vez,** com todas as bases. Não há calibração nem piloto.
- **As sementes dos testes** (101…505) servem só à fumaça, à varredura dos fins (seção 11) e aos testes do orquestrador.

## 4. As medidas

**Nenhuma métrica nova fora do `digilab/metrics.py`.** As da guarda, da secundária, do corpo e da privação já estão lá e já saem do
orquestrador do protótipo; a do movimento é a única nova e entra no `metrics.py` antes da run (4.3).

### 4.1 A medida da guarda e da secundária

- **A taxa de fechamento por episódio de fome** (`episodios_fome.taxa`, a de A6.4, sem mudança), por vida.
- **A unidade:** a (base, semente). Em cada unidade, a diferença LAB+P − LAB célula a célula (no mesmo dono), com a média das 4 células do
  lugar. **Uma célula com a taxa `None` num dos dois braços** (uma vida sem episódio) **fica fora da média daquela unidade,** e a unidade
  sem nenhuma célula fica fora (a regra do `por_unidade` do orquestrador do protótipo). Na C4, nenhuma célula do comedouro nem do
  `longe_fixo` saiu fora no REL [poder].

### 4.2 O corpo e a privação (secundárias, só "pior ou não")

- **A privação de hoje:** a fração das decisões dos dias 8 a 14 com `min(fome, higiene, energia) < Config.limiar_privacao` (0,15)
  (`metrics.privacao_nas_decisoes`, o campo `privacao` das medidas do protótipo).
- **As medidas da C5** (AD6-4, como estão): a fração dos ticks com alguma variável abaixo de 0,15 e a menor necessidade, média e mínimo, na
  vida e nos dias 8 a 14 (o campo `corpo`); a exaustão (o campo `exaustao`).
- **A "saúde ao fim" da tarefa** (seção 4) **não entra como medida nova** (AN3-6): o orquestrador do protótipo não a mede, e uma leitura
  de um tick só seria uma medida nova com pouca informação. A menor necessidade da C5 (que inclui a saúde) e a privação respondem ao "pior
  ou não" do corpo.

### 4.3 O movimento (a leitura do produto; a medida nova, no `metrics.py`)

**A definição, escrita antes** (AN3-5, SEM FONTE; a da AN0, seção 2.1 da tarefa, escrita como função):
- **A posição:** a do pet no tick de cada decisão (o `x, y` do `Observacao.mundo`, em unidades de posição do mundo; a entrada do
  `adapt.agir`), a mesma que a AN0 leu nos gabaritos da LM0.
- **O passo da decisão k:** a distância euclidiana entre a posição da decisão k e a da k + 1. A última decisão da vida não tem passo e
  fica fora.
- **"Sai do lugar":** o passo maior que 0.
- **As decisões fora do dormir:** as decisões cuja ação escolhida não é `dormir` (o reflexo do sono incluído, porque a ação dele é o dormir).
- **A medida primária do produto, MOV:** a fração das decisões fora do dormir que saem do lugar, por vida.
- **Ao lado, sem leitura própria:** a distância por dia (a soma dos passos de todas as decisões sobre os dias da vida).

**Onde entra:** uma função `movimento_nas_decisoes(decisoes, dias)` em `digilab/metrics.py`, com `decisoes` = (ação, x, y) por decisão na
ordem, que devolve a fração MOV, o número de decisões fora do dormir, a distância por dia e, para o descritivo (seção 8, item 2), o
deslocamento líquido sobre o caminho das corridas de `explorar` de duas decisões ou mais e a fração dos pares de passos de explorar
seguidos cujo passo inverte o anterior (as duas medidas do zigue-zague da AN0). **Ela entra no PR do orquestrador da AN4, com um teste de
unidade e um teste que confere contra o [AN0] nas vidas da LM0** (os 0,49 e os 50,5 % de lá), **antes de qualquer vida da faixa.** É a
única métrica nova; o orquestrador grava a posição por decisão só para ela.

### 4.4 O passeio e a guarda do cérebro (descritivo; e conferência)

- **Os passeios** (só no LAB+P): quantos por dia, a duração em decisões, e os fins (`meta`, `trocou`, `desistiu`, `interrompido`), lidos
  da contagem do próprio estado (`EstadoDinamico.fins`) e dos `fins` do motivo, que o orquestrador confere entre si (seção 11).
- **A fração das decisões fora do dormir que continuam um passeio** (a unidade do passeio em curso escolhida, não a decisão que o abre),
  por vida: é a premissa P-PASSEIO (seção 7.1).
- **A urgência no passeio** (a tarefa, seção 4: "confere a guarda do cérebro"): **não é medida, é conferência.** Pela regra da 3.2, uma
  decisão que continua um passeio tem a maior urgência de fome, higiene, energia e saúde no limiar ou abaixo dele. Em toda vida do LAB+P, uma
  decisão que continua um passeio com a urgência acima do `urgencia_lambda` **falha alto** (seção 11). Ao lado, no descritivo, a urgência
  máxima nas decisões que abrem um passeio (a abertura não tem guarda; a AN0 mostra 26,7 % das decisões de vagar acima do limiar).
- **O crédito descartado** (a 3.3; a AN-6): quantas opções do passeio não foram entregues ao P2 por um gesto do dono no intervalo
  (`credito: "gesto"` no motivo). **Escrito antes:** nas vidas gravadas da AN0 os donos não deram carinho nem tapa (`gestos_do_dono`), e o
  aleatório não estava lá. A contagem pode sair 0 ou perto disso; isso não é falha, e o teste do crédito descartado da AN2 é quem fecha a
  conferência da 3.3 (a tarefa, seção 10).

## 5. O que a run grava

- Por vida: as medidas do protótipo que a C4 já grava (as de `_medidas`, `conserto=True`), mais o MOV e o resto da 4.3, os passeios e a
  P-PASSEIO da 4.4 e o crédito descartado.
- Os artefatos: o `meta.json`, o `medidas.json` (no git como `.gz` se passar de 100 MB, como na C4) e o `resultado.json`, com
  `git add -f`; as vidas num `vidas.tar.gz`, fora das medidas.

## 6. A margem, pelo poder (e o "≈ 0")

**A conta** ([poder]; a da A6.5, um contraste só, α = 0,025 unilateral):
1. **A dispersão.** O LAB+P não existe. A dispersão de um contraste da mesma medida (a taxa por episódio), na unidade da 4.1, é lida na C4,
   entre o REL (o LAB) e os braços que diferem dele numa subchave ou num controle da memória, sempre com a média das 4 células de um lugar e
   com 200 unidades:

   | fonte | lugar | contraste | média | IC95 (t) | dp entre as unidades | g1 | no σ |
   |---|---|---|---|---|---|---|---|
   | a C4 | comedouro | REL+F − REL (uma subchave a mais por cima do REL) | +0,0035 | [−0,0046; +0,0115] | 0,0577 | 0,01 | sim |
   | a C4 | comedouro | REL − RELsN | −0,0022 | [−0,0060; +0,0017] | 0,0275 | 0,25 | sim |
   | a C4 | comedouro | REL − REC | +0,0450 | [+0,0353; +0,0547] | 0,0696 | −0,08 | sim |
   | a C4 | comedouro | REL − EMB | +0,0733 | [+0,0627; +0,0840] | **0,0763** | 0,07 | sim |
   | a C4 | comedouro | REL − SEM (a memória inteira) | +0,1981 | [+0,1861; +0,2101] | 0,0861 | 0,14 | não |
   | a C4 | `longe_fixo` | REL+F − REL | −0,0023 | [−0,0120; +0,0075] | 0,0700 | −0,11 | não |
   | a C4 | `longe_fixo` | REL − EMB | +0,0636 | [+0,0507; +0,0764] | 0,0925 | 0,12 | não |
   | a C4 | `longe_fixo` | REL − SEM | +0,0646 | [+0,0515; +0,0778] | 0,0943 | 0,09 | não |

   Nenhum é o contraste da AN4: servem só para o tamanho do dp, nunca como evidência dela. O REL − SEM fica fora do σ porque tira a memória
   inteira, não uma subchave; o `longe_fixo` fica ao lado (a secundária). Os outros contrastes do `longe_fixo` estão no [poder].
2. **O σ de planejamento:** o maior dos quatro do comedouro, com a folga de 20 % da A5.9: **σ = 0,0763 × 1,2 = 0,0915** (AN3-3).
3. **O poder** da classe "< 0" com o dano verdadeiro −δ: **1 − Φ(t₀,₉₇₅;K−1 − (δ / σ) · √K)** (a de A6.5; pela simetria do t, a mesma
   conta do limite inferior acima de 0).
4. **A margem δ(K):** o menor dano com poder 0,8 de sair "< 0", o menor dano perto da ração que a run detecta, e a régua do "≈ 0".
5. **A conferência por simulação:** as 200 diferenças REL+F − REL do comedouro da C4 (a subchave a mais por cima do REL, o desenho do
   LAB+P − LAB), centradas, na escala de σ, deslocadas e sorteadas com reposição em K unidades, com o IC95 do t, lidas pela classe de A6.6;
   2 000 réplicas, semente 4242. Com o dano verdadeiro −δ, a fração "< 0"; com o efeito verdadeiro 0, o falso "< 0" e a fração com o IC95
   inteiro dentro de (−δ, +δ), com o σ de planejamento e com o σ observado do REL+F − REL (0,0577).

| K (unidades) | por base | vidas | a margem δ(K) | "< 0" simulado com o dano −δ(K) | efeito 0: falso "< 0" | efeito 0: "≈ 0" (σ de planejamento) | efeito 0: "≈ 0" (σ observado) |
|---|---|---|---|---|---|---|---|
| 50 | 10 | 800 | 0,0369 | 0,804 | 0,024 | 0,583 | 0,984 |
| 100 | 20 | 1 600 | 0,0259 | 0,804 | 0,024 | 0,599 | 0,987 |
| 150 | 30 | 2 400 | 0,0211 | 0,790 | 0,022 | 0,596 | 0,989 |
| **200** | **40** | **3 200** | **0,0182** | **0,802** | **0,027** | **0,600** | **0,983** |
| 300 | 60 | 4 800 | 0,0148 | 0,813 | 0,025 | 0,598 | 0,986 |
| 400 | 80 | 6 400 | 0,0129 | 0,793 | 0,019 | 0,595 | 0,987 |

**O PROPOSTO: K = 200 (40 por base) e a margem δ = 0,018** (AN3-2; o 0,0182 do [poder], arredondado a três casas como nas AD7-1 a AD9-5).
- **O tamanho:** no comedouro o LAB fecha 0,876 dos episódios na C4 (o REL; [poder], `niveis_rel`). A margem é um dano de cerca de 2
  pontos nessa taxa, cerca de um décimo do que a memória inteira vale ali (o REL − SEM, +0,198) e menor que a margem das guardas da C3
  (0,025) e da C4 (0,032). Um dano real de 0,018 ou mais sai "< 0" com 0,8; um dano menor que a margem sai "≈ 0 com o sinal −" e é
  descrito, não falha (7.2).
- **O falso "< 0"** (o passeio sem efeito na comida e a guarda falhando) sai em cerca de 2,5 % das réplicas, o α unilateral.
- **O "≈ 0" com o efeito 0:** com o σ de planejamento, cerca de 60 % das réplicas; com o σ observado do REL+F − REL, 98 %. O número real
  fica entre os dois, e o relato dá a "margem efetiva" (o menor efeito com poder 0,8 pelo dp observado, a fórmula de A6.5). Nenhum dos dois
  muda a margem nem a regra.
- **O custo é pequeno em qualquer linha** (seção 10): o K não sai do orçamento; sai do tamanho de dano que vale ler. O K = 300 (δ 0,015)
  custa 50 % a mais por um dano de 1,5 ponto em vez de 1,8.
- **O que a margem não é:** um limiar do movimento. O MOV não tem margem (7.3).

**O "≈ 0" e a classe de cada contraste** são os de A6.6, como estão, com δ = 0,018: (1) "≈ 0": o IC95 inteiro dentro de (−δ, +δ), com o
sinal se ele também exclui o 0; (2) "> 0": o limite inferior acima de 0 e o IC fora de (−δ, +δ); (3) "< 0": o limite superior abaixo de
0 e o IC fora; (4) "indeterminado": qualquer outro caso. **A régua vale para a taxa por episódio** (a guarda e o LONGE-AN); as medidas do
corpo e o MOV saem com o IC95 e a classe pela mesma regra só como descrição (a margem foi feita para a taxa por episódio), como as medidas
da C5 nas C3 e C4.

## 7. A análise e a regra de leitura

### 7.1 As premissas (PROPOSTAS, SEM FONTE; AN3-4)

Se uma falha, **a guarda é inconclusiva por premissa,** qualquer que seja o IC dela (7.4, a primeira linha).
- **P-PASSEIO:** no LAB+P, nas 4 células do comedouro, **a fração das decisões fora do dormir que continuam um passeio** (4.4), uma por vida,
  com a média das 4 células por unidade; **o limite inferior do IC95 pelo t > 0,01** (o limiar da G-PESA de A6.4, como está; nenhum número
  novo). Se não passa, o passeio quase nunca dura perto da ração, o LAB+P é o LAB de hoje, e a guarda não testa nada: um "passa" dela seria
  vazio.
- **G-ELEGIVEL-EP** (a de A6.4, como está): ao menos 80 % das vidas **do LAB e do LAB+P** no comedouro com 3 episódios ou mais. Na C4, o
  REL teve 17,1 episódios por vida no comedouro [poder]; a premissa está aqui pela regra, não por risco.

### 7.2 A guarda G-COMEDOURO-AN (o único gate)

- **O contraste:** LAB+P − LAB na taxa por episódio, só nas 4 células do comedouro, na unidade de 4.1.
- **O teste:** o IC95 pelo t sobre as unidades (o `metrics.ic_t`, A4.4.6), lido pela classe de A6.6 com δ = 0,018. **A guarda falha só
  com a classe "< 0"** (o limite superior abaixo de 0 e o IC fora de (−δ, +δ); a forma da AD8-5 e da AD9-9, que a tarefa, 3.2, pede).
  - um **"≈ 0 com o sinal −"** (o IC inteiro abaixo de 0, mas dentro da margem) não é "< 0": é um custo menor que o que a run detecta, e sai
    assim descrito;
  - um **"indeterminado"** não é "< 0" (a C3, 15.3, ficou assim): a guarda não falha, e o relato diz que a run não separa o custo de 0.
- **Um contraste só, sem Holm:** não há outro gate.
- **O que sai ao lado:** a estimativa, o IC95, o p unilateral, o g1 das diferenças, o IC percentil do bootstrap (rotulado como na A4.10) e a
  margem efetiva.
- **A ressalva do g1** (A4.4.6, como está): com g1 ≤ −0,5, o contraste sai com a frase de lá. Para a guarda, a frase diz que um "não
  falha" com essa assimetria não é lido como "o passeio não atrapalha"; a ressalva não muda o IC nem a decisão gravada.

### 7.3 O movimento (a leitura do produto, sem limiar; a AN-1)

- **O contraste MOV:** LAB+P − LAB na fração MOV (4.3), **nas 8 células,** com a média das 8 por unidade (AN3-5), e o IC95 pelo t sobre as
  unidades.
- **A leitura:** o relato diz **"o passeio move o pet" só se o limite inferior do IC95 ficar acima de 0** (a tarefa, seção 4). Não há
  margem nem limiar: qual movimento basta é do Matheus, jogando (a AN-1). O MOV não é gate, e nenhum resultado dele muda a guarda.
- **Ao lado, pela classe de A6.6 só como descrição:** o MOV por lugar (o comedouro e o `longe_fixo`, 4 células cada) e a distância por dia
  nos dois lugares.

### 7.4 A regra de leitura (o que se decide em cada resultado)

As linhas são lidas na ordem, e vale a primeira que serve. **O porte (AN5) segue a AN-7:** só se a guarda não falhar.

| ordem | premissas (7.1) | G-COMEDOURO-AN | MOV | o que diria | o que se faz |
|---|---|---|---|---|---|
| 1 | uma falha | qualquer | qualquer | inconclusivo por premissa: o passeio quase não durou perto da ração, ou os donos não deram episódios | registrado; **a AN5 não roda** (inconclusivo não é "não falhou"); volta ao Matheus (AN3-8) |
| 2 | passam | "< 0" | qualquer | **a guarda falha:** nestas condições, o passeio tira o pet do comedouro | registrado como está; a `passeio` fica desligada; a AN5 não roda (a tarefa, seção 0) |
| 3 | passam | não "< 0" | > 0 (o limite inferior acima de 0) | a guarda passa, e o passeio move o pet | a AN5 pode rodar (a AN-7); o Matheus vê no jogo |
| 4 | passam | não "< 0" | não "> 0" | a guarda passa, e o Python não mostra mais movimento: o passeio muda para onde o pet anda, não quanto (o nulo escrito em 1) | a AN5 pode rodar (a AN-7), e o relato diz que o MOV não subiu; o Matheus decide jogando (AN3-7) |

- **A classe da guarda sai sempre ao lado** ("≈ 0", "≈ 0 com o sinal −", "> 0", "indeterminado"), como descrição do tamanho.
- **O LONGE-AN, as medidas do corpo e o descritivo da seção 8 não mudam nenhuma linha.** Um "< 0" no LONGE-AN ou no corpo volta ao Matheus
  como dado, ao lado da linha, para a decisão do porte; não é gate (a tarefa, seção 4: "secundárias, só 'pior ou não'").
- **Gate que falha não para a V3.** O resultado negativo é registrado como está. **A run não se repete,** nada se ajusta olhando para ela,
  e uma faixa nova só vem com um adendo novo.

## 8. O descritivo (sem gate)

Os contrastes LAB+P − LAB, com o IC95 do t sobre as unidades e a classe de A6.6 (só como descrição fora da taxa por episódio), e os níveis
por braço e lugar. **Nenhum muda a leitura de 7.4.** A lição LP-2 (os grupos que o mecanismo cria não viram contraste): **as decisões de
passeio, os passeios e os fins do passeio saem só no LAB+P, por lugar,** sem contraste.
1. **A secundária LONGE-AN** e a taxa por episódio por braço e lugar; os episódios de fome por vida.
2. **O movimento e o zigue-zague:** o MOV e a distância por dia por braço e lugar, em nível e nos contrastes; o deslocamento líquido sobre o
   caminho das corridas de explorar de 2 decisões ou mais e a fração dos pares de passos de explorar seguidos que invertem o anterior, **só
   em nível, por braço e lugar** (a corrida de explorar muda de forma com o passeio, a LP-2). É a pergunta "de forma legível" da tarefa,
   seção 1, sem limiar; o [AN0] dá a escala de hoje (0,49 e 50,5 %).
3. **O passeio (só no LAB+P):** os passeios por dia, a duração em decisões, os fins somados por motivo (`meta`, `trocou`, `desistiu`,
   `interrompido`), a P-PASSEIO também no `longe_fixo`, a urgência máxima nas decisões que abrem um passeio e o crédito descartado (4.4).
4. **O corpo:** a privação e as medidas da C5 (4.2), em nível e nos contrastes, nos dois lugares.
5. **Os outros:** a fração das decisões `explorar` (o campo `exploracao`) e as ações por tipo, em nível e nos contrastes; a G-PESA de cada
   módulo de hoje; os fins das intenções somados por braço e lugar (a conferência de 11); por dono, só a média da taxa por episódio e do MOV.

## 9. A análise, por extenso (o que o `resultado.json` grava)

- As premissas (7.1), com o valor, o IC, o limiar e "passa".
- A guarda (7.2): a média, o IC95, o p unilateral, o g1, o IC do bootstrap rotulado, a margem efetiva, a classe e "falha".
- O MOV (7.3): a média, o IC95, o p unilateral, o g1 e "o passeio move o pet" (o limite inferior acima de 0).
- A linha de 7.4 e o que se faz.
- O descritivo da seção 8.
- O `nao_demonstra`: o apego do jogador, o "parece passear" ao jogador, que o modular supera o A, um tamanho fora das condições da run e
  qualquer novidade.
- O resumo no console em ASCII (o `ensure_ascii` do #518), para não quebrar num console cp1252.

## 10. O tamanho da run e a máquina

- **200 unidades × 16 vidas = 3 200 vidas,** 14 dias cada.
- **No máximo 4 processos e uma run de pesquisa por vez** (a V3-D8; as medições do combate contam). O número de processos não muda nenhuma
  vida nem o resultado.
- **A estimativa das horas** [poder, `parede_4_processos_c4` e `estimativa_parede`]: a C4, com 4 processos, gastou 0,805 s de parede por
  vida (11 598 s para 14 400 vidas), na média dos seis braços; com 3 200 vidas, **43 min.** O REL custou 3,41 s de CPU por vida no comedouro
  e no `longe_fixo` [poder, `custo_rel`], contra 3,15 s da média da C4 (o RESULTADO, seção 16): cerca de 8 % a mais, **47 min.** O custo do
  passeio e da gravação da posição não é conhecido; a varredura (seção 11) o mede nas sementes dos testes, e o registro da run dá a
  estimativa com ele. **Estimativa: de 45 min a 1 h 15 min com a análise.** É estimativa; o tempo real vai ao RESULTADO.
- **O tamanho em disco:** pelo da C4 (138,2 MB para 14 400 vidas no `medidas.json`), cerca de 31 MB para 3 200 vidas, mais o movimento e o
  passeio; as vidas num `vidas.tar.gz`, fora do `medidas.json`.

## 11. O que falta antes da primeira vida, e os critérios de parada

- **A aprovação deste plano** (o cabeçalho com "APROVADO pelo Matheus") e as AN3-1 a AN3-9.
- **A AN2 na `main`:** a `passeio` desligada, o G2-py (os gabaritos da AN1 sem regravar, salvo o `digibrain_modular_constantes.json` pela
  decisão de 2026-11-04), os testes dos fins, da persistência zerada acima do limiar e do crédito descartado, e o replay bit a bit.
- **A faixa** 78101…78505 em `FAIXAS_RESERVADAS` (este PR, o primeiro commit).
- **O PR do orquestrador da AN4** (`experiments/run_v3_acoes_novas.py`, com a config em `experiments/configs/v3_acoes_novas/`):
  - **a medida do movimento** em `digilab/metrics.py` (4.3), com o teste de unidade e o teste contra o [AN0];
  - os braços LAB e LAB+P (seção 2), as 8 células, as bases e o K da seção 3, 14 dias, orçamento de 16; em toda vida, a `passeio` ligada
    exatamente no LAB+P e a C2, a C3 e a L-2 desligadas (senão, falha alto);
  - **a trava:** exige este plano com a marca "APROVADO pelo Matheus" no cabeçalho (hoje ela recusa, e um teste confere com o cabeçalho
    trocado nos dois sentidos) e a faixa em `FAIXAS_RESERVADAS`; recusa, com `SementeSemPlano`, outra base, outro K, outros dias ou
    sementes fora da faixa; não grava por cima de uma pasta que já existe; mais de 4 processos levantam erro;
  - **a pasta de saída:** `artifacts_v3_acoes_novas/run/` (a pasta-mãe já tem o `hoje.json` e o `plano_an3_poder.json`);
  - **a conferência dos fins (a lição do #507):** os fins conhecidos de cada braço são as chaves de `EstadoDinamico.fins` com a config dele
    (no LAB+P, com o `interrompido` da AN2); um fim fora deles, ou uma contagem do registro diferente da do próprio estado, **falha alto**;
  - **a conferência do passeio,** em toda vida do LAB+P, falhando alto: a decisão que continua um passeio tem a urgência no limiar ou abaixo
    (4.4); o alvo dela é o ponto do passeio aberto (`do_passeio` no motivo); o `interrompido` não sobe o F (a AN-5); no LAB, nenhum
    `do_passeio`, nenhuma intenção de tipo `passeio` e nenhum `interrompido`;
  - o replay bit a bit (o G1), o T-CENARIO-1, o G-MECANISMO, a conferência do crédito e a `conferir_memoria` da C4 em toda vida;
  - as medidas da seção 4 e a análise das seções 6 a 9, gravadas no `resultado.json` com a classe de cada contraste e a linha da leitura.
- **A varredura, antes da run:** o orquestrador inteiro com as cinco sementes dos testes (bases 101 a 505, K = 1), os 2 braços, as 8
  células e 14 dias (80 vidas). O resultado vai no relato do PR: os fins que apareceram, a P-PASSEIO e o custo por vida. Um fim
  desconhecido ou uma conferência que falhe para a etapa. **A varredura não é dado da AN4.**
- **Antes da run:** os testes de mecanismo e de vidas, os gabaritos (o G2) e a suíte. **Qualquer quebra do G1, do G2 ou do G-MECANISMO
  para tudo.**
- **O registro da run** (uma seção 14 neste plano), num commit empurrado antes da primeira vida: o commit, a config com o sha256, as bases,
  o K, a primeira e a última unidade, os braços e os sha do orquestrador, do protótipo, do `config.py`, do `engine.py`, do `metrics.py`, de
  todo `digilab/digibrain/` e deste plano; a pasta de saída sem vida da faixa em disco; o comando.
- **O RESULTADO:** `docs/RESULTADO_V3_ACOES_NOVAS.md` (a tarefa, seção 7), com a guarda e o movimento, cada número com o artefato.
- **A run roda uma vez.** O resultado é registrado como está, e nada se ajusta olhando para ele.

## 12. As referências

Só as linhas verificadas que a tarefa já usa (a seção 9 dela; `docs/referencias/referencias_verificadas.csv`, a skill
`literatura-digilab`), e só no que elas autorizam:
- **Oudeyer e Kaplan (2007), `10.3389/neuro.12.006.2007`:** separa a motivação intrínseca (a novidade, o progresso) da recompensa externa.
  Dá o enquadramento do passeio pelo tédio e pela curiosidade; **não dá direção nem tamanho de nenhum contraste deste plano.**
- **Nenhuma outra fonte é citada.** Nenhuma fonte verificada dá a direção da guarda, do MOV ou do LONGE-AN.
- **SEM FONTE:** as previsões da seção 1; a definição do MOV e das decisões fora do dormir; o K, a margem, a folga de 20 %, o σ de
  planejamento; o 0,01 da P-PASSEIO (o da G-PESA), o 80 % e os 3 episódios da G-ELEGIVEL-EP, o −0,5 do g1, o 0,15 da C5; a faixa. Os números
  de contexto saem dos artefatos citados ([poder], [AN0]).

## 13. As decisões do Matheus (DECIDIDAS em 2026-11-05, todas pela recomendação)

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| **AN3-1** | o cenário, os braços e os lugares (PROPOSTA) | **o cenário da C4 (14 dias, orçamento 16, os 4 donos sem ensino); o LAB = o REL da C4, o LAB+P = o REL com a `passeio`; o comedouro na guarda e o `longe_fixo` na secundária; 8 células, 16 vidas por unidade** (seção 2) | 4 dias como os gabaritos da LM0: o σ da C4 (14 dias) deixa de valer, e a margem fica sem base; com o longe sorteado: +8 vidas por unidade para um lugar que nenhuma pergunta lê; outro LAB que não o REL: o braço deixa de ser o pet de teste do jogo, que é onde o passeio chega (AN-7) |
| **AN3-2** | o K e a margem (PROPOSTA) | **K = 200 (40 por base), δ = 0,018,** o menor dano com poder 0,8 de sair "< 0" pelo σ conservador (seção 6). 3 200 vidas, de 45 min a 1 h 15 min com 4 processos | K = 100 (δ 0,026, 1 600 vidas, cerca de 25 min): um dano de 2 pontos no comedouro passa como "≈ 0" ou "indeterminado" e a guarda não o pega; K = 300 (δ 0,015, 4 800 vidas, cerca de 1 h 10 min): pega um dano de 1,5 ponto, por 50 % a mais de máquina; com K = 200, um dano real menor que 1,8 ponto sai "≈ 0 com o sinal −" e não falha, e isso fica escrito antes |
| **AN3-3** | o σ de planejamento (PROPOSTA) | **o maior dp dos quatro contrastes do comedouro da C4 entre o REL e um braço que difere numa subchave ou num controle (o REL − EMB, 0,0763), com a folga de 20 % (0,0915)**; o REL − SEM e o `longe_fixo` só ao lado | só o REL+F − REL (0,0577 × 1,2 = 0,069): a margem cai para cerca de 0,014 com K = 200, mas se o passeio mexer na dispersão como um controle da memória mexe (0,07 a 0,08), o poder real fica abaixo de 0,8; com o REL − SEM (0,0861 × 1,2): a margem sobe para cerca de 0,021 por um contraste que tira a memória inteira, longe do desenho de uma subchave |
| **AN3-4** | as premissas (PROPOSTA) | **a P-PASSEIO no comedouro, pelo limite inferior do IC95 > 0,01 (o limiar da G-PESA); a G-ELEGIVEL-EP no LAB e no LAB+P** (7.1) | sem a P-PASSEIO: um passeio que quase nunca dura perto da ração (a guarda do cérebro cortando tudo) dá uma guarda que "passa" sem testar nada, e a AN5 portaria um passeio que só existe longe; a P-PASSEIO pela média sem IC: um LAB+P que mal passeia lê como premissa cumprida |
| **AN3-5** | a medida do movimento e a forma do MOV (PROPOSTA) | **a fração das decisões fora do dormir em que o pet sai do lugar (o passo até a decisão seguinte > 0), numa função nova do `metrics.py` que entra no PR do orquestrador com teste; o MOV nas 8 células, com "o passeio move o pet" só com o limite inferior do IC95 acima de 0; a distância por dia e o zigue-zague ao lado** (4.3, 7.3) | a distância por dia como a leitura: ela sobe com qualquer explorar a mais, e o vagar de hoje já anda em toda decisão; o MOV só no comedouro: o produto lê o pet em todo lugar, e o comedouro é onde a guarda corta o passeio; o MOV com uma margem: um limiar sem fonte, contra a AN-1 |
| **AN3-6** | a "saúde ao fim" da tarefa (PROPOSTA) | **não entra como medida nova; o "pior ou não" do corpo sai da privação e das medidas da C5, que já existem** (4.2) | uma medida nova da saúde num tick: um número a mais no `metrics.py` com pouca informação (o valor de um instante, num corpo que oscila com o dia), e o descritivo do corpo deixa de ser comparável com a C3 e a C4 |
| **AN3-7** | a linha 4 (a guarda passa, o MOV não sobe) (PROPOSTA) | **a AN5 pode rodar pela AN-7, e o relato diz que o MOV não subiu; o Matheus decide jogando** (7.4) | parar a AN5 sem o MOV: o MOV vira gate sem limiar, contra a AN-1, e um passeio que só muda a forma do andar (o que a tarefa pede: "legível") não chega ao jogo; ir sem dizer: o Matheus vê no jogo uma mudança que o Python não mediu como "mais movimento" sem saber disso |
| **AN3-8** | o inconclusivo por premissa e o porte (PROPOSTA) | **a AN5 não roda; volta ao Matheus** (7.4, a linha 1) | portar no inconclusivo: a AN-7 diz "só se a guarda não falhar", e uma guarda que não testou não é uma guarda que passou; o passeio chegaria a todo ovo novo (o v17 é o padrão desde o #562) sem a medida que a AN-1 pediu |
| **AN3-9** | a faixa e quando ela entra (PROPOSTA) | **78101…78505, as bases 78101, 78202, 78303, 78404 e 78505; em `FAIXAS_RESERVADAS` já neste PR, a pedido do coordenador, com a fonte "PROPOSTO" e nenhuma vida antes da aprovação** (seção 3) | depois da aprovação (o precedente da AD9-7): nenhum custo além de um commit a mais; reservar agora e o plano mudar: a faixa fica presa a um plano que mudou, e o adendo que mudar diz se ela segue ou se queima; outra faixa: só trocar as bases no orquestrador, na config e no teste |

## 14. O registro da run (AN4; 2026-11-05, worker do orquestrador, Claude Code, Opus 5.5, branch `v3-acoes-novas-an4`)

Gerado por `python experiments/run_v3_acoes_novas.py --registro` (nenhuma vida; só deriva as sementes), num commit empurrado antes da
primeira vida (seção 11). **O commit da run** é o da `main` com o PR do orquestrador mesclado: ele vai ao `meta.json` (`git_head`,
`git_limpo`), e os sha256 abaixo amarram o código. **A trava confere** cada sha256 contra a árvore antes da primeira vida: um arquivo
mudado depois deste registro recusa a run, e um registro novo vai num commit antes dela (o desvio D-AN4-7). Nenhuma vida da faixa
78101…78505 está em disco neste commit.

- **A config:** `experiments/configs/v3_acoes_novas/acoes_novas.json` (o sha256 na lista abaixo).
- **As bases:** 78101, 78202, 78303, 78404, 78505; **K = 40 por base**, 200 unidades, o prefixo `digibrain_prototipo`; 3200 vidas de 14 dias, orcamento 16 por dia.
- **A primeira unidade:** base 78101, k 0, semente 9302717491086198706, genoma 5029551504080525806.
- **A ultima unidade:** base 78505, k 39, semente 17128216646918455119, genoma 16126371893882073772.
- **Os bracos:** LAB = `{"cheiro_inato": true, "controle_mem": "rel", "intencao_cheiro": true, "memoria_autobio": true}` sobre a config ligada do DigiBrain; LAB+P = `{"cheiro_inato": true, "controle_mem": "rel", "intencao_cheiro": true, "memoria_autobio": true, "passeio": true}` sobre a config ligada do DigiBrain.
- **As celulas:** atencioso/comedouro, atencioso/longe_fixo, relapso/comedouro, relapso/longe_fixo, aleatorio/comedouro, aleatorio/longe_fixo, incoerente/comedouro, incoerente/longe_fixo.
- **A saida:** `artifacts_v3_acoes_novas/run/`, que nao existe antes da run (a run recusa gravar por cima).
- **O comando:** `python experiments/run_v3_acoes_novas.py --config experiments/configs/v3_acoes_novas/acoes_novas.json --processos 4`.
- **Os sha256** (a trava confere cada um contra a arvore antes da primeira vida; o plano fica fora, porque guarda o registro):

- `experiments/run_v3_acoes_novas.py`: `5aa5b8364abe84abd8acee7443a0f7be46a5eb81fd90b9d95b0f3f02f5b95278`
- `experiments/run_v2_digibrain_prototipo.py`: `e3071e6729a6a9dade31946c1372606215bc68b10e0c6f72584d1fa3ba45ae63`
- `experiments/run_v2_longe_regular.py`: `5583a217edd04ad2493c91c23d67d913605adb780699a14a9495e6b58a9a900c`
- `experiments/run_v2_habito_intencao.py`: `8a6cc3de0d3af4cc8fa4a19b15215b9607bd016989129bc8bb666c31c4102701`
- `experiments/run_v2_memoria_autobio.py`: `dcc83a04f88db17e777a66d95b467a3e15ff24e59a5c7ab510db0a7925b30cf0`
- `experiments/configs/v3_acoes_novas/acoes_novas.json`: `452de2addda238bfb911c5e3ca0e9d93cd9ed500609cf2306be81faf8fb3503a`
- `digilab/config.py`: `08b32ce64c04e387c695346ab11764bb4d6fc3aa99fe4b98dfd611d0aa9cabbd`
- `digilab/engine.py`: `48ba51ce6426eb98a726c05e07f3a57992ae0f328f517740ec36f1c3db153630`
- `digilab/metrics.py`: `5e04403e18649b54382cdbfcddfc793d573d432bf171c8da6273b3aa11648b29`
- `digilab/mundo.py`: `eceb37e9e3749f8e9cb598fb67af49d90947b992fdabac84d10e16b5cde3899e`
- `digilab/digibrain/__init__.py`: `3d50ce23bd4001f607018485282fbea22b021d7e4f825c070b9be87197cb2b55`
- `digilab/digibrain/_comum.py`: `164ef9c3e5781f68a711d50de9a014751073ea7343540e5d6af9feff0a81d160`
- `digilab/digibrain/adapt.py`: `ab2f281ea25a1d7fbe0e580d75f156b10437f2b70591183ee654e24eb3b42300`
- `digilab/digibrain/afeto.py`: `e890523b5239b6b12818997a5d82ff5f722f390ecf3f69ebcfd60324c43c525f`
- `digilab/digibrain/arb.py`: `f5465f353366a81da3fd32b84377d40988ff46d60dda17237ad47c3053d3fa64`
- `digilab/digibrain/estado.py`: `76a5f54acccdee3ec3305d6127f2f459b67ce615e0970c3e350955150b34b3c6`
- `digilab/digibrain/ganchos.py`: `595e7f57fddb5e3d06bf2aa939acd59dce379843b503a7f04021821b2328a224`
- `digilab/digibrain/impulso.py`: `01ca39d48c5f77fdc6a993a226d83d952616824b9817d1124c91a375d7e3c7c3`
- `digilab/digibrain/mem.py`: `69b5907c3b19ba3f38779d8894eb19dfb2dc3c6581dda882e1fa85fe570f5b05`
- `digilab/digibrain/pers.py`: `c0e3ef850d84d12b7263baeba438f5395512f34a05e49fea831c346ab1594528`
- `digilab/digibrain/plast.py`: `6739a7032a7a45328b251916c54e81b91755c34168409b12b5ba3044c681b0b8`
- `digilab/digibrain/sens.py`: `fa58b1e6161ca6388027a5ce6cc8a111b25f1cc7ab0eb9fe9ca6a1e135872d8a`
