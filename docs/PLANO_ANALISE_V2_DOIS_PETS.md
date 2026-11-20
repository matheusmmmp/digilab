# Plano de análise — V2: dois pets, o degrau 1 (o B aprende o que só o A viveu?)

> **V2, congelado em 2026-10-30** (tag `v2-final`). O estado em que este documento fica na V3 está em `docs/FECHAMENTO_V2.md`; o
> plano da V3, em `docs/PLANO_V3.md`.

Status (2026-10-08): **PROPOSTO**, registrado **antes de qualquer run**. **PDP-1 a PDP-6 DECIDIDAS pelo Matheus em 2026-10-08, todas pela
recomendação** (seção 12). É a etapa 6 de `docs/TAREFA_V2_DOIS_PETS.md`. O desenho é
`docs/futuro/dois_pets.md`, com DP-1 a DP-12 decididas.

**O degrau 1 fica INCONCLUSIVO POR PREMISSA (decisão do Matheus, 2026-10-13; adendo 1.3):** o A não aprendeu no mundo físico
(G-K, adendo 1.2, #287), e o degrau 1 só volta quando um pet aprender de verdade lá.

**Regras deste plano:**
- Os números novos são PROPOSTOS, SEM FONTE, salvo onde citam um artefato.
- O que não está aqui é descritivo pós hoc.
- Nada se ajusta olhando a validação, que roda uma vez só.
- Nenhuma alegação de novidade: aprendizado social entre agentes artificiais já está publicado (`docs/futuro/cognicao_social.md`,
  seção 9).

## 1. A pergunta

**O B aprende algo que só o A viveu?**
- **O que o A viveu:** dias sozinho no mapa, aprendendo pela consequência qual tipo de árvore dá fruta que faz mal.
- **O que o B tem:** o B nasce depois, nunca comeu lá, e só pode saber pelo que **vê** o A fazer e pelo **toque** (DP-11: visão e toque
  no degrau 1).

**A predição** (sentido fixado agora): com o companheiro **informativo**, o B come menos a fruta ruim do que com o companheiro
**embaralhado**, que tem a mesma presença e a mesma competência, mas informação sem valor para o mundo do B.

**O que não se pergunta aqui:** a audição e o cheiro (degrau 1b, etapa 8), o segundo dono (etapa 7), a comunicação (degrau 2) e a relação
(degrau 3). Os lugares deles estão previstos na seção 10.

## 2. O mundo, os pets e o dono

| item | valor | fonte |
|---|---|---|
| mundo | o físico, layout padrão, com o grupo (`ConfigGrupo`) | tarefa, etapas 1 a 3 |
| os números do mundo | os do adendo do plano do mundo físico (o `m` das quedas), sem recalibrar | `docs/PLANO_ANALISE_V2_MUNDO_FISICO.md`, seção 6 |
| **o efeito da fruta** | **um tipo de fruta faz mal** (o efeito ruim no humor, `efeito_humor_ruim`), os outros dois são neutros. O tipo ruim é sorteado por unidade, `derivar_semente("dois-pets-ruim", s)`, uniforme entre `a`, `b` e `c`. Cada tipo tem árvores no jardim e na mata (`LAYOUT_MUNDO_PADRAO`) | PROPOSTO |
| os sentidos | visão e toque (DP-11) | desenho, seções 5.1 e 5.2 |
| o cérebro | o A no P1 (a consequência com a E2), no ponto da K2, com a montagem completa e com o que a etapa 4 acrescenta (o alvo aprendido e as entradas sociais), sem recalibrar (M10). **Os canais ficam (PDP-7, DECIDIDA em 2026-10-11):** o B cria a rota do canal do humor no cérebro do mundo físico | tarefa, etapas 4 e 4c; PDP-7 | tarefa, etapa 4 |
| o corpo | desligado (PDP-1) | — |
| o dono | um dono (o atencioso) com orçamento de 16 interações por dia **para cada pet**, decidindo por pet, só com o cuidado (PMF-3, sem elogiar nem repreender), com o `DonoComLugar` no comedouro | DP-7, validação inicial; PMF-3 e PMF-4 do mundo |
| morte | desligada | — |

## 3. Os braços

**O grupo de cada braço** (por unidade, com a semente do grupo s):
- **o A:** entra no tick 0 e vive **K dias sozinho** antes do B;
- **o B:** entra no dia K e vive **14 dias** com o A. Todos os B são P1.

| braço | o companheiro A | os K dias do A | papel |
|---|---|---|---|
| **B + Ainf** (informativo) | P1 | o mundo com o efeito **verdadeiro** | o braço que pode transmitir |
| **B + Aemb** (embaralhado) | P1 | o efeito **desarranjado** entre os tipos: o tipo π(ruim) faz mal, com π o desarranjo da unidade por `derivar_semente("dois-pets-embaralha", s)`, como o `desarranjo_n6`. **No dia K, o mundo passa ao efeito verdadeiro para os dois** | o acoplado no estilo P2a: a mesma presença, a mesma competência e a mesma disputa, com informação sem valor para o B |
| **B + Aing** (ingênuo) | P0, recém-nascido, que entra junto com o B no dia K | — | a presença sem experiência |
| **B só** | nenhum | o mundo passa os K dias **sem pet**, com as mesmas quedas | a referência |

**O B só e o pet A sozinho.** Pelo desenho (seção 2), o pet A usa a semente do grupo. Por isso o B só deste plano não é a "vida de hoje":
é o B, com a semente dele, entrando no dia K de um mundo sem ninguém. É a referência certa para o B, com o mesmo mundo e as mesmas quedas.

**O mundo do dia K** difere entre os braços pelo que o A comeu nos K dias. É a interação física, declarada (R-3).

**Os registros sem leitura:** as vidas dos A também são registradas, mas só os B entram nos contrastes. Os A dão a condição de K (seção 5).

## 4. As medidas

Todas nos **7 primeiros dias do B** (do dia K ao K + 7), quando o B ainda está aprendendo. Os 14 dias inteiros entram como descritivo.

**A primária: `R_B`, a taxa de fruta ruim do B.** É a fração dos consumos de fruta do B que são do tipo ruim vigente (o efeito verdadeiro),
pela `metrics.taxa_fruta_ruim` sobre os consumos do B no mundo. Menor é melhor.

**As secundárias (dentro do Holm, seção 6):** a mesma `R_B`, nos contrastes com o B só e com o B + Aing.

**Os descritivos (sem gate):**

| medida | definição |
|---|---|
| uso dos candidatos sociais | a fração das decisões de explorar do B em que ele escolheu `onde_comeu` e `seguir`, por dia |
| o que o B viu | quantas vezes o B viu o A comer, e de que tipo |
| a disputa | as disputas por comida, quantas o B ganhou e a distância de cada um no momento (desenho, seção 3) |
| o toque | os contatos por tipo (disputa, encostar, esbarrar), por dia |
| o custo de ter companhia | o `D_FE` (o déficit de fome e energia do plano do mundo) e a privação do B, em cada braço |
| o que o B aprendeu | o peso da escolha do tipo ruim e o peso das classes `onde_comeu` e `seguir` no fim de cada dia |
| o A | a `R_A` nos K dias e depois, e se o A embaralhado reaprende depois do dia K |
| o modelo dos outros | a familiaridade, a confiança por atividade e a afinidade do B sobre o A (só registradas, DP-8) |

## 5. A calibração (só o mundo e o K, sem o primário)

**O mundo não se calibra aqui.** Os números são os do adendo do plano do mundo físico. Se ele não estiver pronto, este plano espera.

**O K se escolhe só pelos A sozinhos** (PDP-3). A calibração não roda nenhum B, então não tem como olhar a `R_B`.
- **A grade:** K ∈ {3, 5, 7} dias.
- **O que roda:** o A informativo sozinho, P1, 10 dias, nas sementes de calibração (seção 8). A vida até o dia K é a mesma para todo K ≤ 10,
  então uma run serve à grade inteira.
- **A regra:** o **menor** K em que o A aprendeu. Aprendeu = o limite superior do IC95 de `R_A` no dia K (bootstrap sobre as unidades)
  abaixo de **metade** da `R_A` do dia 1.
- **Se nenhum K passa:** o A não aprende no mundo físico em 7 dias, e não há o que transmitir. O plano para e volta ao Matheus.

**O que não se calibra:** o ponto do A (M10), o prior das classes sociais do alvo aprendido (etapa 4, PROPOSTO) e os números da visão e do
toque (desenho). Ficam como estão, e são iguais em todos os braços.

## 6. O piloto, a margem e o N

**O piloto:** no K escolhido, os quatro braços, nas mesmas 20 unidades da calibração. Serve só para a margem, o N e o custo; os números
dele não entram como evidência.

**A margem `Δ_S`, na escala da medida** (a convenção de "metade" da regra 6.3 do experimento maior): metade da distância entre o B que não
sabe nada e o A que já sabe:

`Δ_S = ½ × [R_B(B só) − R_A(Ainf, dias K − 6 a K)]`

É o que o B ganharia aprendendo metade do que o A sabe. Se a distância do piloto for ≤ 0,05 (PROPOSTO), o A não sabe muito mais que o B
ingênuo, e a validação não roda: o plano volta ao Matheus.

**O N:** o menor K_u (unidades por base) de 4 a 10 com poder simulado ≥ 0,8 para detectar `Δ_S` no contraste primário.
- **O método:** um bootstrap das diferenças por unidade do piloto, deslocadas para `Δ_S`, com 2.000 réplicas por K_u.
- **Os secundários:** o poder de cada um sai só como relato; abaixo de 0,5, o gate é lido como subpotenciado.
- **Se nem K_u = 10 chega a 0,8,** a validação roda com 10 e o poder sai declarado.

**O adendo 1:** o K, a `Δ_S`, o K_u, o poder e o custo entram num commit antes da validação.

## 7. Gates e regra de decisão

**O bootstrap:** sobre as unidades, com 10.000 reamostragens, semente 4242 e IC95; o IC90 só na equivalência. O replay de todo grupo é
conferido bit a bit (G1-GRUPO).

| gate | contraste (por unidade) | regra | papel |
|---|---|---|---|
| **G-K** | `R_A` do Ainf no dia K contra o dia 1 | limite superior do IC95 abaixo de metade do dia 1 | **pré-condição:** sem ela, o primário é **inconclusivo por premissa** |
| **G-SOCIAL** | `R_B(B + Aemb) − R_B(B + Ainf)` | as categorias abaixo | **primário** |
| G-COMPANHIA | `R_B(B só) − R_B(B + Ainf)` | limite inferior do IC95 > 0, Holm | secundário |
| G-INGENUO | `R_B(B + Aing) − R_B(B + Ainf)` | limite inferior do IC95 > 0, Holm | secundário |

**As categorias do G-SOCIAL** são exclusivas e lidas nesta ordem (a ordem do PR #196):
1. **o B aprende do A:** o limite inferior do IC95 > 0. Se o limite superior do IC90 < `Δ_S`, leva o rótulo **"abaixo de Δ"**;
2. **o B piora com o A informativo:** o limite superior do IC95 < 0;
3. **equivalente:** o IC90 dentro de ±`Δ_S`;
4. **inconclusivo:** o resto.

**O Holm** cobre {G-COMPANHIA, G-INGENUO}, com α = 0,05. O G-SOCIAL é único e não entra.

**A leitura:**
- **G-K passa e o B aprende do A:** a primeira resposta da frente é **sim**, pela visão e pelo toque, com a presença e a competência iguais.
  Os descritivos de uso dos candidatos dizem por onde (`onde_comeu` ou `seguir`). Isso libera a etapa 8 (o acréscimo da audição e do
  cheiro) com o mesmo desenho.
- **G-K passa e o G-SOCIAL empata ou fica inconclusivo:** o B não aprende o que o A viveu por estes sentidos, com este cérebro. Os
  descritivos dizem se o B nem usou os candidatos sociais (o alvo aprendido não aprendeu a ir) ou se usou e não adiantou.
- **O B piora com o A informativo:** registrado. O descritivo da disputa diz se o A informativo, por saber onde comer, tirou a comida boa
  do B.
- **G-COMPANHIA e G-INGENUO** separam "ter companhia" de "ter companhia que sabe". Eles não mudam a categoria do primário.

## 8. Sementes

| uso | faixa | bases |
|---|---|---|
| calibração do K e piloto | **39101…39505** | 39101, 39202, 39303, 39404, 39505 (K_u = 4) |
| validação | **40101…40505** | 40101, 40202, 40303, 40404, 40505 (K_u do adendo) |
| **previstas para os adendos** (seção 10) | **41101…41505** (degrau 1b) e **42101…42505** (dois donos) | a confirmar em cada adendo |

- **O prefixo de unidades:** `"dois_pets"` (a semente do grupo e o genoma; a semente do B sai dela, pelo desenho).
- **Conferências em 2026-10-08,** no `origin/main` (`f8449ba`) e nos branches remotos:
  - as quatro faixas estão fora de `FAIXAS_RESERVADAS` e da `FAIXAS_QUEIMADAS`;
  - elas também ficam fora da 23101…27505 e da 35101…36505 (transferência, ainda não registrada lá);
  - `git grep` das bases não acha uso fora dos gabaritos.
- **O D registra** as faixas e o prefixo, com a fonte deste plano (tarefa, etapa 5).

## 9. Riscos

| # | risco | o que o plano faz |
|---|---|---|
| R-1 | **O B nem tenta os candidatos sociais:** o prior das classes `onde_comeu` e `seguir` é pequeno | o uso dos candidatos sai por dia. Um "não aprende" com uso zero é lido como "não tentou", e não como "tentou e não serviu" |
| R-2 | **O A embaralhado reaprende depois do dia K** e vira informativo com atraso | é o que o P1 faz. A janela de 7 dias do B é curta, e a `R_A` do Aemb depois de K sai descrita. Se ele reaprende cedo, o contraste encolhe a favor da equivalência: o efeito medido é conservador |
| R-3 | **O mundo do dia K difere** pelo que o A comeu | é a interação física. O B só e o B + Aing entram num mundo sem consumo nos K dias, e a diferença sai como descritivo (as frutas no chão no dia K) |
| R-4 | **A disputa pesa contra o B informado:** o A que sabe tira a comida boa | a disputa e o `D_FE` saem por braço. O G-SOCIAL compara dois A igualmente competentes, então a disputa é parecida nos dois |
| R-5 | **A sorte da ordem no tick** | é igual em distribuição nos braços (o fluxo `mundo-ordem` da mesma semente), e sai medida |
| R-6 | **A janela de 7 dias** | ela pega o aprendizado do B no começo. A vida inteira de 14 dias sai como descritivo |
| R-7 | **O custo:** cada unidade tem 4 grupos e o A vive K dias a mais | o custo medido no piloto vai no adendo, com o teto de tempo do Matheus |
| R-8 | **Os rótulos** ("seguiu", "aprendeu do outro") | só valem pelas medidas e regras desta seção. A leitura não usa intenção |

## 10. O lugar dos adendos

- **Adendo 2, o degrau 1b (a audição e o cheiro; etapa 8; DP-11):**
  - **o desenho:** o mesmo, com os quatro braços e o mesmo K;
  - **as duas condições por braço:** visão e toque, e visão, toque, audição e cheiro;
  - **o contraste:** o **acréscimo** de cada canal no G-SOCIAL, medido como a diferença entre as duas condições. A audição e o cheiro
    podem entrar juntos ou um de cada vez, a decidir no adendo;
  - **as sementes:** 41101…41505;
  - **quando:** antes da run do 1b, depois da validação deste plano.
- **Adendo 3, os dois donos (etapa 7; DP-7):**
  - **antes:** o G-DONOS, dois donos de mesmo comportamento iguais a um, é gate de mecanismo, sem run de pesquisa;
  - **a pergunta do adendo** (por exemplo, o B com um dono relapso e o A com um atencioso);
  - **as sementes:** 42101…42505;
  - **quando:** depois do G-DONOS.
- **Nenhum adendo muda o primário deste plano.** Cada um traz o próprio gate.

## 11. Artefatos e reprodução

- **As pastas:**
  - `artifacts_v2_dois_pets/calibracao/`, com `k.json` e o `piloto/`;
  - `artifacts_v2_dois_pets/validacao/`.

  Cada uma traz `meta.json` (o sha256 de `mundo.py`, `grupo.py`, `lobos.py`, `config.py` e `engine.py`) e os registros dos grupos.
- **As configs:** `experiments/configs/v2_dois_pets/{calibracao,validacao}.json`, com o campo `"plano"`.
- **A recusa:** a run se recusa a rodar se a pasta de saída já existe.

## 12. Decisões do Matheus

**DECIDIDAS em 2026-10-08: PDP-1 a PDP-6, todas como recomendado. DECIDIDA em 2026-10-11: PDP-7, os canais.**

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| PDP-1 | O corpo neste primeiro degrau | **desligado:** a pergunta é sobre o que o B vê, e o corpo só soma drives que não entram no contraste | ligado: a solidão e o estresse mexem no B por ter companhia, e o degrau 1 passa a medir também o efeito do corpo, que é do degrau 3 |
| PDP-2 | A medida primária | **`R_B` nos 7 primeiros dias do B** | a vida inteira: dilui o efeito, porque o B sozinho também aprende com o tempo |
| PDP-3 | O K | **o menor de {3, 5, 7} dias em que o A aprendeu** (G-K), escolhido só pelos A sozinhos | escolher olhando o B: o K vira ajuste a favor do primário |
| PDP-4 | O controle primário | **o A embaralhado** (DP-9), com o desarranjo dos tipos nos K dias e o mundo verdadeiro depois | o A ingênuo como controle primário: ele difere em competência e presença, e o contraste mistura isso com a informação |
| PDP-5 | A margem | **metade da distância entre o B só e o A informativo** | uma margem fixa sem dado: larga demais (tudo equivalente) ou estreita demais (N acima do teto) |
| PDP-6 | As faixas de sementes | **39101…39505** e **40101…40505**, mais 41101…41505 e 42101…42505 previstas para os adendos | uma colisão tira o "novo" das unidades |
| PDP-7 | Os canais no mundo dos dois pets (o nó `canais_fruta_mundo`, #264) | **DECIDIDA em 2026-10-11: o B cria a rota do canal do humor no cérebro do mundo físico, e a montagem completa fica no plano, com os canais.** Hoje, no mundo dos dois pets, comer a fruta que mexe no humor com os canais ligados falha alto no cérebro do mundo físico (a "rota de adendo" do MUNDO-CEREBROS). Até a rota existir, o nó segue pendente e nenhuma run do plano roda | rodar sem os canais: o P1 dos dois pets deixaria de ser o cérebro A da K2 (a montagem completa), e o resultado não seria comparável com o resto da V2 |

## Adendo 1 (2026-10-13)

### 1.1 Antes da run da calibração: as janelas da regra do K e a agregação

Decisão do Matheus (2026-10-13), PDC-1 pela recomendação do #283. Este trecho foi commitado **antes de qualquer run** nas sementes 39101…39505.

**O problema (fumaça nas sementes dos testes, só contagens):**
- o A sozinho come de 0 a 9 frutas maduras por dia; o resto da comida é a ração do dono no comedouro;
- no dia 1, as 5 unidades da fumaça somaram 1 fruta madura;
- na letra da seção 5 (o dia K contra o dia 1), a R_A do dia 1 sairia de uns 4 consumos nas 20 unidades, e a regra pararia por falta de
  dado.

**A regra G-K passa a ler janelas de dois dias** (`"janelas": "dois_dias"` em `experiments/configs/v2_dois_pets/calibracao.json`):
- **o início:** os dias 1 e 2;
- **o K:** os dias K − 1 e K. No K = 3, as janelas se sobrepõem no dia 2, o que torna a regra mais difícil de passar, não mais fácil;
- **a regra:** o menor K de {3, 5, 7} com o limite superior do IC95 de R_A nos dias K − 1 e K abaixo de metade da R_A dos dias 1 e 2. O
  resto da seção 5 não muda.
- **A validação** (o G-K da seção 7) usa as mesmas janelas.

**O que o plano não dizia, nos valores recomendados no #283** (PDC-2 a PDC-5):
- **a R entre unidades:** a razão das somas (`taxa.modo`). Cada consumo pesa igual, e a unidade sem consumo não pesa (ela não tem taxa;
  não é zero). Vale na G-K e na `Δ_S`;
- **a exposição mínima:** 20 consumos somados em cada janela da regra (`taxa.n_minimo`, PROPOSTO, SEM FONTE). Abaixo disso a regra lê
  "exposição baixa" e não passa;
- **a unidade sem consumo do B** nos 7 primeiros dias, num dos dois braços de um contraste, sai do contraste por unidade e é contada;
- **o poder:** o G-SOCIAL no t unilateral a 0,025 (o "limite inferior do IC95 > 0"); os secundários no relato, a 0,025 e a 0,05;
- **o mundo:** o `m` = 1 da calibração do mundo (`docs/PLANO_ANALISE_V2_MUNDO_FISICO.md`, que já validou: #285).

### 1.2 Depois da calibração: os números

**A calibração rodou uma vez** em 2026-10-13, no commit `24f0b6d` (com a árvore limpa), pela config
`experiments/configs/v2_dois_pets/calibracao.json`:
- 20 grupos A-so (bases 39101…39505, K_u = 4), 10 dias cada;
- todo grupo foi gravado e rejogado do disco bit a bit;
- 26 s de CPU, 9 s de parede com 8 processos.

Os números saem de `artifacts_v2_dois_pets/calibracao/` (`k.json`, `resultado.json`, `k/medidas.json`, `meta.json`).

**G-K, as janelas do 1.1:** a R_A dos dias 1 e 2 é 0,485, com 33 consumos em 10 unidades. O limiar é 0,242.

| K | dias | R_A | consumos (unidades com valor) | IC95 | leitura |
|---|---|---|---|---|---|
| 3 | 2 e 3 | 0,358 | 53 | [0,162; 0,552] | não aprendeu |
| 5 | 4 e 5 | 0,338 | 77 | [0,164; 0,518] | não aprendeu |
| 7 | 6 e 7 | 0,366 | 71 | [0,160; 0,567] | não aprendeu |

**Nenhum K passa, e não é por exposição:** toda janela tem 20 consumos ou mais.

**Pela seção 5, o plano para aqui:**
- o A não aprende no mundo físico em 7 dias, e não há o que transmitir;
- não roda piloto, `Δ_S` nem N, e a validação (40101…40505) não roda;
- o plano volta ao Matheus.

**Descritivo, fora da regra:** a R_A por dia, somada nas 20 unidades.

| dia | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| R_A | 0,80 | 0,35 | 0,37 | 0,29 | 0,39 | 0,50 | 0,21 | 0,41 | 0,22 | 0,25 |
| consumos | 10 | 23 | 30 | 38 | 39 | 38 | 33 | 17 | 32 | 40 |

- Na vida toda, a R_A é 0,343 em 300 consumos, perto de 1/3, a fração de um tipo entre três.
- Cada A come em média 15 frutas maduras e 83 rações em 10 dias.

### 1.3 A decisão do Matheus (2026-10-13): o degrau 1 fica inconclusivo por premissa

- **O degrau 1 é lido como "inconclusivo por premissa"** (a leitura do G-K da seção 7): sem um A que aprenda, não há o que o B possa
  aprender dele. Isso não diz nada sobre a pergunta social, só que ela não foi testada.
- **O mundo não muda** para fazer o A aprender: nem o `m`, nem as quedas, nem o efeito da fruta. Mudar o mundo olhando o G-K seria ajustar a
  premissa até ela passar.
- **O degrau 1 volta quando um pet aprender de verdade no mundo físico,** por um de dois caminhos, cada um com plano próprio:
  - o alvo aprendido (`docs/PLANO_ANALISE_V2_MUNDO_ALVO.md`), se o G-ALVO sair "o alvo ajuda";
  - o pet que pensa (J5, `docs/PLANO_ANALISE_V2_PET_QUE_PENSA.md`), se os dois testes da DS-1 passarem.
- **Ao voltar, o plano ganha um adendo antes de qualquer run nova:** o cérebro do A (e do B) passa a ser o que aprendeu, e a calibração do K
  roda de novo, com as regras da seção 5 e do adendo 1.1 (PROPOSTO). A faixa dessa calibração fica para o adendo. A 39101…39505 já foi usada
  nesta; a 40101…40505 (validação) não rodou e continua reservada.
- **O código fica:** o `Grupo`, os sentidos, as entradas sociais, a bancada do grupo e o orquestrador da calibração continuam na `main`,
  com as chaves desligadas por padrão.
