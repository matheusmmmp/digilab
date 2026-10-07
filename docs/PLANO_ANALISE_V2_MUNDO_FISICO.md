# Plano de análise — V2: o P1 no mundo físico mínimo

Status (2026-10-07): **PROPOSTO**, registrado **antes de qualquer run**. **PMF-1 a PMF-7 DECIDIDAS pelo Matheus em 2026-10-07, todas
pela recomendação** (seção 13). Tarefa: `docs/TAREFA_V2_MUNDO_FISICO.md`. Nenhum número deste plano
saiu de run no mundo físico; os que vêm de antes citam o artefato.

**Regras deste plano:**
- O que não está aqui é **descritivo pós hoc** e é declarado assim no resultado.
- Nada se reajusta olhando a validação.
- Pela decisão do Matheus de 2026-10-01, um gate que falha é registrado e não para a V2.

## 1. A pergunta

**O P1 (aprender pela consequência da própria ação) ganha do P0 (instinto) num mundo em que explorar compensa?**

**O ponto de partida.** No mundo `padrao`, o P1 não reduziu a privação (`docs/RESULTADO_V2_N3.md`; G-P1 +0,0008 [−0,0067; +0,0077],
`artifacts_v2_n3/validacao/ganho4/resultado.json`). Ele aprendeu a ficar parado:
- no tempo livre, o ocioso subiu de 28% para 47%;
- explorar caiu de 29% para 15%.

Explorar só gastava energia, e a comida vinha do dono e do `+0,05` do comer parado.

**O que muda no mundo físico** (tarefa, seções 4 a 6):
- a comida tem lugar: o dono a solta num ponto, e as árvores a derrubam longe da casa;
- comer parado não alimenta (MF-2);
- andar custa energia pela distância;
- o pet pode achar comida explorando e comê-la ali mesmo (MF-1).

**A pergunta tem uma premissa:** que, neste mundo, explorar compense de fato para o próprio instinto. O plano a confere com um braço de
controle (P0z, seção 3) antes de ler o P1. Se a premissa falha, um P1 que não ganha não diz nada sobre o P1.

**Predições** (todas com sentido fixado antes):

| # | predição | contraste | papel |
|---|---|---|---|
| PR-0 | explorar compensa para o instinto: o P0 tem déficit menor que o P0z | P0z − P0 > 0 | premissa (G-MUNDO) |
| PR-1 | com o mesmo cuidado, o P1 tem déficit menor que o P0 | P0 − P1ac > 0 | **primária** (G-MF1) |
| PR-2 | com o cuidado reagindo ao pet, o P1 tem déficit menor que o P0 | P0 − P1 > 0 | secundária (Holm) |
| PR-3 | com o mesmo cuidado, o P1 tem privação menor que o P0 (a medida do N3) | P0 − P1ac > 0 | secundária (Holm) |

## 2. O mundo

| item | valor | fonte |
|---|---|---|
| motor | `MotorMundo`, chave `ConfigMundo.ligada` | tarefa, seção 2 |
| mapa e regiões | 64 × 30 células, casa, jardim, campo e mata (M-4) | tarefa, seção 3 |
| frutas | o mundo **"iguais"**: as três frutas com efeito neutro no humor (PMF-7). A podre só com a escolha de um cérebro; o instinto nunca a come | tarefa, seções 5 e 6 |
| MF-1 a MF-4 | como recomendado na tarefa. **Se o Matheus decidir diferente, este plano ganha um adendo antes de qualquer run** | tarefa, seção 11 |
| duração | 14 dias | o mesmo do experimento maior (`experiments/configs/v2_experimento_maior/validacao.json`) |
| orçamento do dono | 224 interações | idem |
| morte | desligada, como no N3 | `docs/PLANO_ANALISE_V2_N3.md` |
| ofertas do calendário, informação, pedido, julgamento | desligados | — |

**Os donos.** São os quatro da v1: aleatório, relapso, atencioso e incoerente. Em todos os braços, os donos ficam **só com o cuidado**
(PMF-3):
- o filtro `sem_ensino` de hoje, sem elogiar nem repreender;
- é o pet do produto, sem os botões (`docs/DECISAO_PRODUTO_SEM_ELOGIO_BRONCA.md`).

O `alimentar` de cada dono vira `deixar_comida("racao", x, y)` pelo `DonoComLugar` (tarefa, seção 4).

**O lugar onde o dono solta a comida** é um fator fixo por vida, com três níveis (PMF-4): **comedouro**, **perto** e **longe**. É a variável
nova do cuidado (`mundo_fisico.md`, seção 7). Fica cruzado com o dono e o braço dentro de cada unidade.

## 3. Os braços

| braço | política | cuidado | para quê |
|---|---|---|---|
| **P0** | `PoliticaInstintoMundo` (o instinto com a fome urgente do mundo) e os alvos padrão do motor | o dono reage ao pet | a referência |
| **P0z** | o P0 em modo `sem_explorar` (o peso de explorar no tempo livre vai para ocioso) | o dono reage ao pet | o controle da premissa; não é um pet do jogo |
| **P1** | o cérebro da montagem completa com a fonte consequência, no ponto já fixado, e os alvos padrão do motor | o dono reage ao pet | PR-2 |
| **P1ac** | o mesmo P1 | **acoplado ao P0 da mesma célula:** recebe a sequência de eventos de cuidado do P0, nos mesmos ticks e nas mesmas posições, e o dono não reage | PR-1 e PR-3 |

**O ponto do P1 não se recalibra** (M10). É o da validação única:
- `ponto` T3, `consequencia` com ganho 4 e canais ligados, `memoria_ganho` 512 (`experiments/configs/v2_experimento_maior/validacao.json`);
- o cérebro é o A, o DigiBrain escolhido (M6);
- o mundo não depende dele: o mesmo plano pode ser repetido com outro cérebro por adendo.

**O P1 usa os alvos padrão do motor.** Hoje nenhum cérebro tem o `escolher_alvo`, então o P1 aprende **quando** explorar, comer e brincar,
e não **para onde**. Um braço com alvo aprendido entra só por adendo, depois que o B entregar o gancho.

**O acoplado no espaço.** O "perto" do P0 é perto do pet do P0. No P1ac, a ração cai no mesmo ponto, que pode não estar perto do pet do
P1. É de propósito: o cuidado é idêntico no tempo e no espaço, e a diferença sobra para o pet.

## 4. Unidade, pareamento e células

- **Unidade:** a semente derivada por `unidades_derivadas(bases, K, prefixo="mundo")` (o prefixo novo vai para `PREFIXOS_UNIDADES`, etapa
  4 da tarefa). Ela dá a semente do pet e a do genoma.
- **Célula:** dono × lugar, 4 × 3 = 12. Cada unidade roda as 12 células nos 4 braços: **48 vidas por unidade**.
- **Pareamento:** por unidade e por célula. As quedas de fruta são as mesmas nos braços (G-NUMS da tarefa), e os desvios do lugar também
  (a rng `dono-lugar` não tem o braço).
- **Estatística por unidade:** a média das 12 células da diferença entre braços.

## 5. As medidas

### 5.1 A primária: o déficit de fome e energia

`D_FE = média, nas decisões dos dias 8 a 14, de ((1 − fome) + (1 − energia)) / 2`

**Por que fome e energia juntas:**
- um pet que anda demais paga na energia; um que fica parado paga na fome. A troca é a pergunta;
- a higiene fica fora, porque o mundo não mexe nela;
- o humor fica fora, porque o sinal do P1 não o vê (F6) e brincar não tem drive próprio até a W-TAREFA-CORPO.

**Por que os dias 8 a 14:**
- o P1 começa no prior do instinto, então os primeiros dias são iguais em esperança e só somam ruído;
- a vida toda entra como descritivo.

O `D_FE` é a média de dois déficits que o próprio sinal do P1 usa. Não é o sinal: o sinal é a mudança imediata do déficit por ação; o
`D_FE` é o nível médio que o pet sustenta. **O risco de a medida favorecer o P1 é declarado** (seção 10, R-6), e a PR-3 usa a privação do
N3, que não tem esse viés.

### 5.2 As secundárias (dentro do Holm)

- **Privação:** 1 − `fracao_fora_de_privacao`, pela `Estado.em_privacao`, amostrada em cada decisão dos dias 8 a 14. É a mesma definição do
  N3 (`docs/PLANO_ANALISE_V2_N3.md`, seção 5).
- **`D_FE` no P1 com o cuidado reagindo** (PR-2).

### 5.3 Os descritivos (sem gate)

| medida | definição |
|---|---|
| ganho líquido por hora de busca | nas decisões de explorar e nas de comer com deslocamento: (fome ganha com o que comeu − energia gasta na decisão), na escala 0–1, por hora dessas decisões |
| latência até achar | do `deixar_comida` ao consumo daquela ração, em minutos; a fração comida antes de apodrecer; a mediana entre as comidas |
| frutas das árvores | a fração das frutas caídas que o pet come; a fração comida podre (deve ser 0 no P0) |
| deslocamento | as células andadas por dia; o tempo em cada região |
| tempo livre | brincar, explorar, ocioso e chamar, como no N3; comer na fome moderada |
| fome urgente | a fração de decisões na regra de fome urgente, e quantas foram para a comida e quantas para o chamar |
| o lugar como cuidado | no P0, `D_FE` por lugar (longe − comedouro; perto − comedouro), com IC95; P0 − P1ac por lugar e por dono |
| o teto | as vidas do P1 com algum peso no teto (o G6 do N3, aqui só registro) |
| tempo de desistência (PISTA) | seção 9 |

## 6. A calibração do mundo (sementes de calibração)

**Só o mundo se calibra, e só com o instinto.** A calibração usa o P0 e o P0z. **O P1 não entra na escolha do mundo**, para o mundo não
ser ajustado a favor dele (PMF-5).

- **O que varia:** o multiplicador `m` das probabilidades de queda das árvores (`p_queda` do jardim e da mata, tarefa seção 6), em
  `m ∈ {1/2, 1, 2}`. O resto do mundo fica nos valores da tarefa.
- **As bases:** 31101, 31202, 31303, 31404 e 31505, com K = 4 (N = 20 unidades), em 3 × 12 × 2 = 72 vidas por unidade.
- **A regra da escolha:** o **menor** `m` em que a premissa passa na calibração, com o limite inferior do IC95 de (P0z − P0) em `D_FE`
  acima de 0. O menor é o mundo mais escasso em que explorar ainda compensa: é ali que procurar pesa mais.
- **Se nenhum `m` passa:** para tudo e relata. Explorar não compensa nem para o instinto com os números da tarefa, e o desenho do mundo
  volta para o Matheus (PMF-5). Nenhuma validação roda.

**O piloto do N.** No `m` escolhido, e só nele, roda o P1 e o P1ac nas mesmas 20 unidades (12 × 2 = 24 vidas por unidade). Esse piloto
serve só para o N:
- nada do mundo muda depois dele;
- os números dele não entram no resultado como evidência sobre o P1. São relatados como piloto.

**O Δ do plano:** `Δ_MF = ½ × (P0z − P0)` em `D_FE`, a média da calibração no `m` escolhido. É metade do que explorar vale para o instinto.
Fica congelado no adendo.

**O N:** o menor K, de 4 a 10 por base (N de 20 a 50), com poder simulado ≥ 0,8 para detectar `Δ_MF` no G-MF1:
- é um bootstrap das diferenças P0 − P1ac do piloto, centradas e deslocadas para `Δ_MF`, 2.000 réplicas por K;
- se nem K = 10 chega a 0,8, a validação roda com K = 10 e declara o poder;
- o custo medido na calibração vai junto.

**O adendo.** O `m`, o `Δ_MF`, o K, o poder e o custo entram em `docs/PLANO_ANALISE_V2_MUNDO_FISICO.md`, adendo 1, num commit **antes** da
validação. O piloto não reabre nenhuma outra escolha.

## 7. A validação (uma vez)

- **As bases:** 32101, 32202, 32303, 32404 e 32505, com o K do adendo. É uma vez só, nos 4 braços e nas 12 células.
- **O replay:** toda vida é rejogada e comparada bit a bit (G1). Divergência para tudo.
- **O bootstrap:** sobre as unidades, com 10.000 reamostragens e a semente 4242, como no experimento maior.
- **O IC primário** é de 95%; o IC90 entra só na regra de equivalência.

## 8. Gates e regra de decisão

| gate | contraste (por unidade, média das 12 células) | regra | papel |
|---|---|---|---|
| **G-MUNDO** | P0z − P0 em `D_FE` | limite inferior do IC95 > 0 | premissa: sem ela, o G-MF1 é **inconclusivo por premissa**, qualquer que seja o número |
| **G-MF1** | P0 − P1ac em `D_FE` | as categorias abaixo | **primário** |
| G-MF2 | P0 − P1 em `D_FE` | limite inferior do IC95 > 0, com Holm | secundário |
| G-MF3 | P0 − P1ac em privação | limite inferior do IC95 > 0, com Holm | secundário |

**As categorias do G-MF1** são exclusivas e lidas nesta ordem; vale a primeira que se aplica:
1. **o P1 ganha:** o limite inferior do IC95 > 0. Se, além disso, o limite superior do IC90 < `Δ_MF`, o resultado leva o rótulo **"ganha,
   abaixo de Δ"**.
2. **o P1 perde:** o limite superior do IC95 < 0.
3. **equivalente:** o IC90 inteiro dentro de ±`Δ_MF`.
4. **inconclusivo:** o resto.

A ordem resolve a sobreposição que a leitura da validação única achou entre "confirma" e "refuta" (PR #196).

**O Holm** cobre {G-MF2, G-MF3}, com α = 0,05. O G-MF1 é único e não entra.

**A leitura para as decisões do Matheus:**
- **G-MUNDO passa e o P1 ganha:** a consequência sozinha aprende a sustentar fome e energia num mundo em que procurar compensa. O pet
  parado do N3 era do mundo, e não da fonte. Isso apoia ligar a consequência nos pets novos junto com o mundo físico. Os drives do corpo
  (S-3) continuam necessários para brincar.
- **G-MUNDO passa e o P1 empata ou perde:** mesmo onde explorar compensa, a consequência imediata não aprende a procurar. Isso aponta para
  o crédito entre decisões (R-1) e reforça o pet que planeja (`docs/V2_RODADA_16.md`, seção 6). É resultado negativo, registrado.
- **G-MUNDO falha na validação:** a premissa não se repetiu fora da calibração, e o P1 não é lido. O mundo volta para revisão.

## 9. Pista: o teorema do valor marginal (Charnov 1976)

Charnov, E. L. (1976). *Optimal foraging, the marginal value theorem*. Theoretical Population Biology 9(2), 129–136.
`10.1016/0040-5809(76)90040-x`.
- **A conferência:** metadados conferidos no Crossref em 2026-10-07 (título, autor, revista, volume, número, páginas e data, pela API
  `api.crossref.org/works/`). O texto e o resumo não foram lidos.
- **O estatuto:** não está nas tabelas de `docs/referencias/` e entra como **PISTA**. Não sustenta nenhuma afirmação deste plano.

**O uso** é só a pergunta "quando sair de um lugar". Um descritivo, sem gate e sem predição:
- **o tempo de desistência:** depois que o pet come a última fruta a até 3 células de uma árvore, os minutos até sair desse raio. É
  comparado entre P0 e P1ac e entre o jardim (árvore perto da casa) e a mata (longe);
- **por que só descritivo:** as condições do modelo (manchas que se esgotam, o tempo de viagem entre elas e a taxa de ganho como moeda) não
  são conferidas neste mundo.

**Nenhuma alegação de novidade.** O resultado não diz que o pet "segue" ou "viola" o teorema.

## 10. Riscos

| # | risco | o que o plano faz |
|---|---|---|
| R-1 | **Crédito entre decisões.** Com a janela imediata, as decisões que só andam registram o gasto, e o ganho fica com a que come. Uma ida longa à mata se parte em várias decisões, e o P1 pode aprender a evitar idas longas mesmo quando elas compensam | o MF-1 cobre o achado perto. As idas longas são o caso que só um cérebro com crédito entre decisões ou com plano resolve. O descritivo de deslocamento por região mostra se aconteceu |
| R-2 | **O teto.** O sinal tem sentido fixo por ação, e no N3 os pesos foram ao teto em 20 de 20 vidas | o teto é registrado (5.3). O ponto não se recalibra (M10) |
| R-3 | **O dono domina.** O atencioso e o incoerente não deixaram o pet em privação no N3, e no comedouro e no perto a busca pode quase não importar | o primário é a média das 12 células. O efeito por lugar e por dono é descritivo, sem gate, para não multiplicar testes |
| R-4 | **Números do mundo sem fonte.** O mapa, os raios, a velocidade e os custos são PROPOSTOS, e só o `m` se calibra | declarado. O resultado vale para este mundo. Mudar o layout é outro plano |
| R-5 | **A premissa só na calibração.** O `m` escolhido pode passar por pouco e falhar na validação | o G-MUNDO é conferido de novo na validação. Se falhar, o P1 não é lido |
| R-6 | **A medida perto do sinal.** O `D_FE` usa fome e energia, dois dos drives do sinal do P1 | o G-MF3 usa a privação do N3, que é um limiar de qualquer necessidade e não a média |
| R-7 | **Brincar não paga.** Sem o tédio, brincar com a bola só mexe no humor, que o sinal não vê. O P1 pode largar o brincar, como no N3 | é esperado e medido no tempo livre. É a W-TAREFA-CORPO (S-3) que trata, não este plano |
| R-8 | **O MF-2 sem implementação limpa.** Se o A não conseguir desfazer o `+0,05` sem tocar o `engine.py`, a tarefa para | o plano não roda sem o MF-2 (a premissa dependeria do comer parado) |
| R-9 | **O P0z não é um pet.** Tirar o explorar muda o tempo livre de um jeito que nenhum pet do jogo tem | ele serve só para a premissa e não é comparado ao P1 |
| R-10 | **O custo.** São 48 vidas por unidade, com N até 50 (2.400 vidas na validação), num motor mais caro | o custo medido na calibração vai no adendo. Se passar do teto de tempo que o Matheus der, o K cai e o poder é declarado |
| R-11 | **A tentação pós hoc.** Há muitos descritivos por lugar, por dono e por região | só os quatro gates da seção 8 decidem. O resto é declarado descritivo |

## 11. Sementes

| uso | faixa | bases |
|---|---|---|
| calibração do mundo e piloto do N | **31101…31505** | 31101, 31202, 31303, 31404, 31505 (K = 4) |
| validação | **32101…32505** | 32101, 32202, 32303, 32404, 32505 (K do adendo) |

**Conferências feitas em 2026-10-07 no `origin/main` (`dcd1157`) e em todos os branches remotos:**
- as duas faixas estão fora de `FAIXAS_RESERVADAS` e da `FAIXAS_QUEIMADAS` (`experiments/bancada_v2.py`). A 15101…15505 continua
  queimada;
- elas também ficam fora da 23101…27505 proposta na leitura parcial;
- `git grep` das bases em `docs/`, `experiments/`, `tests/`, `digilab/`, `web/app/src/` e `CLAUDE.md` não acha nenhum uso como semente. Os
  acertos estão só em CSVs de partidas e em hashes de gabaritos.

**Quem registra:** a bancada (etapa 4, chat D) põe as duas faixas em `FAIXAS_RESERVADAS` com a fonte deste plano, e o teste de colisão das
unidades derivadas passa a cobrir o prefixo `"mundo"`.

## 12. Artefatos e reprodução

- **As pastas:** `artifacts_v2_mundo/calibracao/` e `artifacts_v2_mundo/validacao/`. Cada uma traz `meta.json` (sha256 de `mundo.py`,
  `config.py`, `lobos.py` e `engine.py`, a versão do Python), `medidas.json`, `resultado.json` e as vidas em `vidas/*.jsonl`.
- **As configs:** `experiments/configs/v2_mundo/{calibracao,validacao}.json`, com o campo `"plano"` apontando para este arquivo.
- **A recusa:** a run se recusa a rodar se a pasta de saída já existe.

## 13. Decisões do Matheus

**DECIDIDAS em 2026-10-07: PMF-1 a PMF-7, todas como recomendado** (a coluna "recomendação" é o que vale).

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| PMF-1 | A medida primária | **`D_FE` nos dias 8 a 14** (seção 5.1), com a privação do N3 como secundária | só a privação: com os donos que não deixam privação, a medida fica perto de zero na maioria das células e o poder cai. Só a fome: premia andar demais |
| PMF-2 | O contraste primário | **P0 − P1ac** (o mesmo cuidado), com o P1 de malha fechada como secundário | o fechado mistura o pet com a reação do dono. No N3, o P1 chamou mais, e o dono pode ter cuidado mais |
| PMF-3 | Os donos sem elogiar e repreender em todos os braços | **sim**: é o pet sem botões, e o acoplado vira o "só cuidado" | com o ensino: o P1 recebe nota que o produto não terá, e a pergunta deixa de ser a do produto |
| PMF-4 | O lugar como fator fixo por vida, com três níveis | **sim**: comedouro, perto e longe, cruzados com o dono | sortear por soltura: o efeito do lugar fica sem estimativa limpa |
| PMF-5 | A calibração só do mundo, só com o instinto, pelo menor `m` que passa a premissa | **sim** (seção 6). Se nenhum passar, para e volta ao Matheus | calibrar com o P1: o mundo fica ajustado a favor dele e o resultado perde o valor |
| PMF-6 | As faixas de sementes | **31101…31505** (calibração e piloto) e **32101…32505** (validação) | colidir com uma faixa usada: as unidades deixam de ser novas |
| PMF-7 | As frutas "iguais" (efeito neutro) no mundo deste plano | **sim**: isola a busca da escolha da fruta, que é a pergunta do N4 e do platô | com o descasado: o efeito da busca se mistura com aprender qual fruta evitar |

## Adendo 1 (2026-10-07, antes de qualquer run): a PMF-2 revisada, o primário em malha fechada

Pedido do coordenador na rodada 17 (`docs/V2_RODADA_17.md`, seção 4). **Status: PMF-2r DECIDIDA pelo Matheus em 2026-10-07, pela
recomendação** (A1.7): o primário passa a P0 − P1 em malha fechada, e a PMF-2 do #212 fica substituída. Nenhuma run foi feita, então nada aqui foi escolhido olhando dado do mundo físico.

### A1.1 Por que revisar

**O primário de hoje é P0 − P1ac:** o P0 em malha fechada contra um P1 acoplado em malha aberta ao cuidado do P0 (seções 3 e 8). Os dois
lados do contraste não estão na mesma condição de cuidado:
- o P0 recebe um cuidado que reage a ele;
- o P1ac recebe um cuidado gravado para outro pet.

**O que a validação única mostrou.** O acoplado em malha aberta cuidou **pior** que o braço original. Em todo braço com dono, o original teve
menos privação e mais saúde que o seu só cuidado (`docs/RESULTADO_V2_VALIDACAO_UNICA.md`, seção 1):
- fora de privação: +0,042 (P2), +0,045 (P2e) e +0,075 (P3);
- saúde: +0,022, +0,020 e +0,037.

**O risco aqui.** Num mundo em que a comida tem lugar e o dono a solta "perto do pet", a desvantagem pode ser maior: no P1ac, a ração cai
perto do pet do P0, e não do P1 (seção 3, "o acoplado no espaço"). O G-MF1 de hoje poderia achar um P1 "pior" que é só o acoplado.

**O que a literatura diz** (`docs/referencias/F_REVISAO_V2_SEIS_PERGUNTAS.md`, P2):
- **Church (1964)**, `10.1037/h0042733` (só metadados conferidos), é a fonte original da objeção ao desenho acoplado: quando os sujeitos
  diferem na reação ao reforçador, o erro aleatório pode virar efeito sistemático;
- **Kimmel e Terrant (1968)**, `10.3758/BF03209860` (só a página 1 de 4 lida), descrevem o mecanismo. Em geral, o acoplado recebe o
  estímulo na hora que serviu ao parceiro, e a diferença sai espúria, a favor do procedimento experimental;
- **a objeção é contestada na própria fonte da alternativa.** No mesmo artigo, Kimmel e Terrant registram reservas sérias a Church e
  consideram duas das premissas dele quase insustentáveis para respostas mediadas pelo sistema autônomo. **O defensável é que o acoplado é
  enviesável, não inválido.** O achado da validação única é o motivo concreto deste plano; a literatura dá o mecanismo, não a magnitude.

### A1.2 O desenho novo

**Nenhum acoplado é comparado com malha fechada.** É a mesma regra do plano do corpo (`docs/PLANO_ANALISE_V2_CORPO_DRIVES.md`, seção 3.5 e
PCD-3).

| braço | política | cuidado | papel |
|---|---|---|---|
| P0 | `PoliticaInstintoMundo` e os alvos padrão | o dono reage ao pet | **primário** e premissa |
| P0z | o P0 em `sem_explorar` | o dono reage ao pet | premissa (G-MUNDO) e **fonte dos acoplados** |
| P1 | o mesmo da seção 3 | o dono reage ao pet | **primário** |
| **P0^ac** (novo) | o P0 | **acoplado ao P0z da mesma célula** | secundário: o mesmo cuidado |
| **P1^ac** (novo) | o P1 | **acoplado ao mesmo P0z** | secundário: o mesmo cuidado |
| P1ac (o de antes) | — | — | **sai** |

**Por que a fonte é o P0z.** A fonte não pode ser um dos dois lados. O P0 rejogado no próprio registro é ele mesmo, byte a byte (o gate da
bancada "no próprio braço sem filtro é a vida de origem"). Então ele não teria a desvantagem da malha aberta, e o P1 teria.
- O P0z já roda em toda célula, e não custa vida a mais como fonte.
- Os dois lados recebem o mesmo registro (eventos de cuidado, ticks e posições, com o filtro `nenhum`, porque os donos só cuidam: PMF-3),
  com a mesma desvantagem.
- **O que fica declarado:** o cuidado do P0z foi gerado para um pet que não explora. O "perto" dele cai perto de um pet que fica mais em
  casa. O contraste mede "o mesmo cuidado, que não é o de nenhum dos dois". Não é uma estimativa do cuidado típico.

**Vidas por unidade:** 5 braços × 12 células = **60** (eram 48: o P1ac sai, entram o P0^ac e o P1^ac).

### A1.3 Predições e gates

As predições da seção 1 passam a ser estas. A PR-0 (a premissa) não muda.

| # | predição | contraste | gate | papel |
|---|---|---|---|---|
| PR-0 | explorar compensa para o instinto | P0z − P0 em `D_FE` | **G-MUNDO**, como na seção 8 | premissa |
| PR-1r | com o dono reagindo, o P1 tem déficit menor que o P0 | **P0 − P1** em `D_FE` | **G-MF1r**, as categorias da seção 8 | **primária** |
| PR-2r | com o mesmo cuidado, o P1 tem déficit menor que o P0 | **P0^ac − P1^ac** em `D_FE` | **G-MF2r**, limite inferior do IC95 > 0 | secundária (Holm) |
| PR-3r | com o dono reagindo, o P1 tem privação menor (a medida do N3) | **P0 − P1** em privação | **G-MF3r**, limite inferior do IC95 > 0 | secundária (Holm) |

- **O Holm** cobre {G-MF2r, G-MF3r} e as medidas de forrageio da A1.8 (G-PERM, G-OPORT e G-DIST), com α = 0,05. O G-MF1r é único e
  não entra.
- **As categorias do G-MF1r** são as da seção 8, sem mudança: ganha (com o rótulo "abaixo de Δ"), perde, equivalente e inconclusivo, nessa
  ordem.

### A1.4 O que muda no N, nas margens e na calibração

- **As margens não mudam.** O `Δ_MF` continua metade de (P0z − P0) em `D_FE`, a média da calibração no `m` escolhido, na escala da medida
  (seção 6). Os dois lados dele estão em malha fechada.
- **A calibração do mundo não muda:** só o P0 e o P0z, pelo menor `m` que passa a premissa (PMF-5).
- **O piloto muda de braços.** No `m` escolhido roda o P1, o P0^ac e o P1^ac nas mesmas 20 unidades: 12 × 3 = 36 vidas por unidade. O P0
  e o P0z já rodaram na grade. Como antes, o piloto serve só para o N.
- **O N** é o menor K, de 4 a 10 por base, com poder simulado ≥ 0,8 para detectar `Δ_MF` no **G-MF1r**:
  - é um bootstrap das diferenças **P0 − P1** (malha fechada) do piloto, centradas e deslocadas para `Δ_MF`, com 2.000 réplicas por K;
  - o poder do G-MF2r e do G-MF3r no N escolhido sai no adendo, só como relato;
  - abaixo de 0,5, o gate é lido como subpotenciado.
- **A variância esperada pode subir.** Em malha fechada, o dono reage a cada pet, e as diferenças P0 − P1 carregam também a variação do
  cuidado. Isso pode pedir um K maior que o do desenho antigo. SEM FONTE para o tamanho: o piloto mede.
- **O custo** sobe 25% por unidade (60 vidas contra 48), e o bloco do layout afastado da A1.8 soma mais 24 (84). Ele entra no adendo do N com o tempo medido, e o teto de tempo do Matheus continua
  valendo (R-10).

### A1.5 A regra de decisão nova

Com o G-MUNDO passando:

| G-MF1r (P0 − P1, dono reagindo) | G-MF2r (o mesmo cuidado) | leitura |
|---|---|---|
| ganha | passa | **o P1 ganha, e o ganho é do pet:** aparece também com o cuidado fixo |
| ganha | não passa | **o P1 ganha, mas o ganho pode vir do dono reagindo** ao que o P1 faz. No N3, o P1 chamou mais no tempo livre (27%, contra 9% do P0, `docs/RESULTADO_V2_N3.md`). Fica registrado ao lado, sem trocar a categoria do primário |
| empata, perde ou é inconclusivo | qualquer | a consequência imediata não aprende a procurar neste mundo, como na seção 8 |

- **Com o G-MUNDO falhando,** o P1 não é lido, como antes.
- **O que muda na leitura da seção 8.** "Isso apoia ligar a consequência nos pets novos junto com o mundo físico" passa a exigir a primeira
  linha. A segunda pede antes uma conta: quanto do ganho é o pet pedindo mais cuidado.

### A1.6 A alternativa registrada: o acoplado recíproco

**O desenho** (Kimmel e Terrant 1968, página 1, pela revisão P2): cada sujeito recebe dois estímulos. Num há contingência; no outro, ele está
acoplado ao estímulo do parceiro. Cada um é o controle acoplado do outro, num 2×2 dentro do sujeito.

**No mundo físico** seriam dois canais de comida por pet, por exemplo dois pontos de soltura ou dois tipos de ração:
- num canal, o dono responde a este pet;
- no outro, as solturas são as que o dono fez para o parceiro do par.

**O que ele resolve:** a comparação entre o cuidado que reage e o que não reage passa a ser dentro do mesmo pet e da mesma vida.

**Por que não entra agora (o custo):**
- **Bancada:** os dois pets do par precisam rodar juntos, passo a passo, porque cada um alimenta o canal do outro na hora. Hoje cada vida
  roda sozinha, e o acoplado rejoga um registro já gravado. É orquestração nova, com o replay G1 de duas vidas entrelaçadas.
- **Mundo e dono:** o dono divide o orçamento entre dois canais, e o pet precisa distinguir os canais na percepção. Isso muda o mundo da
  tarefa (seção 4) e o dono sintético (`DonoComLugar`).
- **Pergunta:** ele separa "cuidado que reage" de "cuidado que não reage". Não compara o P1 com o P0 diretamente; para isso, o par teria de
  ser P0 e P1, e cada canal misturaria os dois cérebros.
- **Tamanho:** SEM FONTE para o número de vidas. O par dobra as vidas por célula, e as células ganham o fator canal.

**Quando valeria:** se o G-MF1r e o G-MF2r divergirem (a segunda linha de A1.5) e a pergunta "quanto é o dono reagindo" virar o centro. Aí
entra por plano próprio.

### A1.8 As medidas de forrageio (DS-5, decidida pelo Matheus em 2026-10-07)

Fonte: `docs/DEFINICOES_V2_SEIS_PERGUNTAS.md`, seção 5. A DS-5 já foi decidida: as medidas 1 e 3 entram como secundárias, e a 2 só como
descritiva. **O motivo é separar forragear de seguir o cheiro:** a medida primária (`D_FE`) diz se explorar compensou, mas não diz como.

**As definições comuns** (PROPOSTAS, SEM FONTE para os números):
- **mancha:** a área a até 3 células do tronco de uma árvore;
- **visita:** do primeiro tick do pet dentro da mancha até o primeiro tick fora dela. Contam só as visitas dos dias 8 a 14 com ao menos uma
  decisão dentro;
- **permanência:** a duração da visita, em minutos;
- **custo de viagem da árvore:** a distância, em células (`isqrt`), do tronco dela ao tronco da árvore mais próxima. Ele é fixo pelo layout.

**O que entra e onde:**

| medida | definição no mundo | contraste (por unidade, braços em malha fechada) | gate | onde |
|---|---|---|---|---|
| **1. permanência × custo de viagem** (Hayden, Pearson e Platt 2011, `10.1038/nn.2856`, resumo: com viagens mais longas, o limiar de abandono da mancha sobe) | a inclinação (mínimos quadrados) da permanência sobre o custo de viagem, nas visitas da unidade | inclinação do P1 − inclinação do P0 | **G-PERM:** limite inferior do IC95 > 0 | **dentro do Holm** |
| **3. custo de oportunidade aprendido** (Constantino e Daw 2015, `10.3758/s13415-015-0350-y`: o custo de oportunidade do tempo é aprendido) | o A não tem uma estimativa explícita da taxa média, então a medida é **pelo comportamento**: a inclinação da permanência sobre a **taxa recente do ambiente** (as frutas caídas por hora nas 24 h antes da visita, contadas do fluxo `mundo-arvores`, que não depende do pet). Quem aprende o custo de oportunidade sai antes depois de dias ricos | inclinação do P1 − inclinação do P0 | **G-OPORT:** limite superior do IC95 < 0 | **dentro do Holm** |
| **2. a taxa no abandono contra a média** | a taxa de ganho (a fome ganha com comida) nos 30 min antes de sair da mancha, dividida pela taxa média da vida (o ganho por hora acordado). SEM APOIO DIRETO: é a forma do teorema, e Charnov 1976 só tem os metadados conferidos | a razão por braço e a diferença P1 − P0, com IC | — | **fora do Holm, só descritiva** |
| **previsão da distância** | o mesmo mundo com o **layout afastado**: os troncos de cada região a duas vezes a distância do centro da região, cortados para dentro dela. Nada mais muda: as mesmas `p_queda`, as mesmas regiões, a casa e o `m` da calibração | [P1(afastado) − P1(padrão)] − [P0(afastado) − P0(padrão)] na permanência média | **G-DIST:** limite inferior do IC95 > 0 | **dentro do Holm** |

**O contraste é a diferença de inclinações** com o P0, e não a inclinação do P1 sozinha:
- o P0 usa os alvos padrão, que seguem o cheiro, e o layout pode criar uma inclinação mecânica nele;
- o que o P1 aprende fica na diferença.

**A previsão da distância é leitura nossa.** É a direção que Hayden et al. descrevem em macacos, numa tarefa de manchas. Ligar o padrão ao
teorema do valor marginal também é leitura nossa: Charnov não é citado pelo conteúdo. Se o P1 não muda a permanência com o afastamento, ele
segue o cheiro e não forrageia (definições, seção 5).

**O limite do cérebro A.** O P1 deste plano usa os alvos padrão do motor (seção 3): ele aprende **quando** explorar, e não **para onde**.
- As medidas 1, 2 e 3 só podem mostrar a decisão de ficar ou sair, pela escolha entre explorar e as outras ações.
- Um cérebro com o gancho `escolher_alvo` entraria por outro adendo.

**O Holm passa a cobrir** {G-MF2r, G-MF3r, G-PERM, G-OPORT, G-DIST}, com α = 0,05. O G-MF1r continua único.
- O poder de cada um no N escolhido sai no adendo do N, só como relato.
- Abaixo de 0,5, o gate é lido como subpotenciado.
- O N continua o do G-MF1r (A1.4).

**O bloco do layout afastado:** P0 e P1, em malha fechada, nas 12 células, dá **24 vidas por unidade a mais** (84 no total, contra 60).
- **A dependência:** ele precisa de um segundo layout na `ConfigMundo` (dono: o A, etapa 2 da tarefa do mundo). Sem ele, o G-DIST sai como
  "não rodado", e o Holm fica com quatro gates.
- **O teto de tempo:** se o custo medido no piloto passar do teto de tempo do Matheus, **este bloco é o primeiro a sair**, decidido aqui,
  antes do piloto. O Holm, então, fica com quatro gates.

**A seção 9 (o tempo de desistência)** continua como descritivo. A medida 1 a complementa, mas não a substitui.

### A1.7 A decisão do Matheus

**DECIDIDA em 2026-10-07: PMF-2r, como recomendado.**

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| PMF-2r | O contraste primário do mundo | **P0 − P1 em malha fechada**, com o par acoplado à mesma fonte (o P0z), P0^ac − P1^ac, como secundário. O P1ac sai. O acoplado recíproco fica registrado como alternativa (A1.6) | **manter o P0 − P1ac:** a desvantagem da malha aberta, que a validação única mediu, entra no primário e pode ser lida como efeito da busca. **Trocar:** o primário passa a incluir a reação do dono ao pet; o G-MF2r a separa, e a leitura da A1.5 diz o que fazer quando os dois divergem. O custo em vidas é +25% por unidade |

**Os pontos das seções 3, 5.3, 9 e 10 que citam o P1ac** passam a valer com o P1 de malha fechada:
- o lugar como cuidado: P0 − P1 por lugar e por dono;
- o tempo de desistência do Charnov: P0 contra P1;
- o R-6: o G-MF3r usa a privação, agora em malha fechada.

Isso vale se a PMF-2r for aceita.
