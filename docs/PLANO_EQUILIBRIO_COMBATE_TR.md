# Plano — rodada de equilíbrio do combate em tempo real

Status: **registrado antes da rodada; nenhum número foi ajustado.** Pedido do Matheus, 2026-10-30 (coordenação): "abrir o plano da
rodada de equilíbrio do combate em tempo real". As decisões da seção 7 foram DECIDIDAS pelo Matheus em 2026-10-30, pela recomendação
("após isso segue as recomendações"). A calibração roda depois do merge deste plano.
Todo número aqui é PROPOSTO, com a fonte ao lado ou SEM FONTE. Só as metas da seção 2 contam como "equilibrado".

**A base do método.** As duas rodadas anteriores:
- a rodada das formas, por turnos: `docs/PLANO_EQUILIBRIO_GERAL.md` e `docs/EQUILIBRIO_GERAL.md`;
- a arena do UP: `D:\Trab\digilab\remaster\arena_equilibrio.md`, fora do repositório.

As três ideias que vêm delas:
- metas fixadas antes da rodada;
- calibração só com as sementes de calibração;
- validação uma vez só, com as sementes de conferência, e nada se ajusta olhando para ela.

**Por que agora.** A COMBATE-TR fechou a R4 (#457): todo lugar de batalha luta em tempo real, e os números do relógio e do espaço
(`CTR_TR`, em `web/app/motor/combate_tr/constantes_tr.ts`) são PROPOSTOS sem calibração. Eles vêm do protótipo da arena ou da conversão
"turnos × `T_TR`". A espec (`docs/ESPEC_COMBATE_TR.md`) já deixava o equilíbrio para uma rodada no fim, e o Matheus confirmou essa regra.

## 1. O ponto de partida (medido, sem ajuste)

A medição da R0 (`web/app/scripts/medicoes/combate_tr.json`) foi feita pelo script `web/app/scripts/medir_combate_tr.ts`, que saiu na R3
e está no commit `efb2ded`. Ela tem 560 lutas, 112 pares e as sementes 101…505:

| medida | hoje |
|---|---|
| duração média / mediana / p90 | 46,9 s / 45,1 s / 80 s (o limite) |
| lutas que chegam ao limite de 80 s | 77 de 560 (13,8%) |
| ações por luta | 49,5 |
| custo por luta (Node) | 0,86 ms; uma luta no limite, 1,47 ms |

**Os achados das R3 e R4** (`docs/registro/2026-10.md`):
- um chip de regra que repete a condição de uma regra que o pet já tem nunca dispara, porque a primeira regra que vale decide (o Recuo e o
  Oportunista nos pets dos testes);
- a reação ao pesado anunciado ("rival preparando") quase não acontece no tempo real: o pet raramente está livre para decidir enquanto o
  rival prepara. **Isto ainda não foi medido com artefato**; é a primeira coisa que a fase 1 mede (meta T-5).

## 2. As metas

As linhas da tabela seguem a ordem do pedido. "Pet típico" é o pet com o treino típico do estágio (`CIT.tipico`: Rookie 8, Champion 22,
Ultimate 36, Mega 40; `web/app/motor/constantes.ts`).

### 2.1 O relógio (fase 1)

| # | o quê | meta PROPOSTA | fonte |
|---|---|---|---|
| **T-1** | duração da luta 1 × 1 no mesmo estágio | média entre 40 e 60 s, mediana entre 35 e 55 s | hoje 46,9 s (R0); a morte súbita aos 50 s e o limite de 80 s (D-5, DECIDIDO) |
| **T-2** | nenhuma luta sem fim | no limite de 80 s, ≤ 5% das lutas em cada confronto | "nenhuma luta sem fim" da arena do UP; hoje 13,8% (R0). Uma luta não pode passar de 80 s, então a meta é a fração que chega ao limite |
| **T-3** | lutas da série | a Cidadela (3 lutas) cabe em 3 min de tela no p90 | SEM FONTE (decisão DE-2) |
| **T-4** | o lado não decide | o lado A vence entre 0,45 e 0,55 no espelho (a mesma forma dos dois lados) | a arena do UP ("o azul perto de 50%") |
| **T-5** | as reações existem | contra quem prepara o pesado, a regra "rival preparando" decide ≥ 50% das vezes em que o pet está livre durante o preparo | SEM FONTE; o achado da R4 |

### 2.2 As formas, as linhas, as técnicas e as passivas (fase 2)

| # | o quê | meta PROPOSTA | fonte |
|---|---|---|---|
| **F-1** | cada forma adulta contra as outras 7 | todas as 8 entre 0,40 e 0,60, com o furioso | M-A1 (`PLANO_EQUILIBRIO_GERAL.md`) |
| **F-2** | distância entre a mais forte e a mais fraca | ≤ 0,20 | M-A3 |
| **F-3** | lugar no ciclo | toda forma vence ≥ 2 das outras 7 | M-A4 |
| **F-4** | as linhas do Rookie e do Champion (as técnicas) | cada linha entre 0,40 e 0,60 contra as outras do mesmo estágio | a extensão de M-A1 aos estágios de baixo; SEM FONTE para a faixa |
| **F-5** | de longe × de perto | quem luta de longe (disparo) vence entre 0,45 e 0,55 de quem luta de perto, por estágio | a arena do UP (45–55%) |
| **F-6** | as passivas | nenhuma passiva muda a força da forma em mais de 0,10, medida com e sem ela | SEM FONTE |
| **F-7** | a sombria | cada sombria entre 0,45 e 0,65 contra as normais do estágio; a sombria nunca chega ao Mega (DECIDIDO) | SEM FONTE para a faixa |

### 2.3 O estágio, o treino e o aprendizado (fase 3)

| # | o quê | meta PROPOSTA | fonte |
|---|---|---|---|
| **P-1** | um estágio | o pet típico de baixo vence o de cima ≤ 0,10; dois estágios acima, 0,00 ("Champion nunca vence Mega", DECIDIDO) | M-B1 (decisão DE-6) |
| **P-2** | um nível de treino | no mesmo estágio, o pet típico vence o pet sem treino ≥ 0,80 | M-B2 ("o treino tem que decidir", Matheus, 2026-09-30) |
| **P-3** | as regras aprendidas | a mesma forma com a lista aprendida (depois de `CAT.sparring` lutas) vence a mesma forma com a lista semente entre 0,55 e 0,70 | SEM FONTE |
| **P-4** | a evolução pede 0,8 | com o treino típico, ≥ 80% dos pets do estágio chegam à taxa `CLE.limiarTaxa` (0,8) nas `CAT.sparring` lutas contra o rival sugerido do estágio | `CLE.limiarTaxa = 0,8` e `CAT.sparring = 10` (`constantes.ts`); a pergunta do Matheus ("é alcançável?") |

### 2.4 A progressão e o fim de jogo (fase 4)

| # | o quê | meta PROPOSTA | fonte |
|---|---|---|---|
| **G-1** | os 6 líderes | sem treino ≤ 0,05; com o treino típico ≥ 0,80; a pior forma ≥ 0,50 | M-B2 |
| **G-2** | os desafiantes da campanha | sem treino ≤ 0,30; com o treino típico ≥ 0,80; a pior forma ≥ 0,50 | M-B3 |
| **G-3** | a Liga | com o treino típico do Mega, toda forma tem chance de título ≥ 0,25 e nenhuma passa de 0,85 | M-C1 |
| **G-4** | a Torre de Batalha e o Palácio | a melhor forma vence a 1ª luta ≥ 0,70, e a pior ≥ 0,40 | M-E1 |
| **G-5** | a Fábrica | com o melhor alugado, vencer ao menos uma série em ≥ 0,25 das tentativas | M-C2 |
| **G-6** | o Salão | cada nível, com o treino típico, entre 0,70 e 0,95 | M-C3 |

### 2.5 As cartas e os chips (fase 4)

| # | o quê | meta PROPOSTA | fonte |
|---|---|---|---|
| **I-1** | os itens não substituem o treino | com os melhores itens e a carta permitida, o pet sem treino vence cada líder ≤ 0,05 | M-D1 |
| **I-2** | os itens não quebram o estágio | com os melhores itens, P-1 continua | M-D2 |
| **I-3** | os itens não desequilibram as formas | com o melhor item de cada forma, a força contra as outras 7 fica ≤ 0,60 | M-D3 |
| **I-4** | cada carta faz diferença | cada carta muda a taxa de vitória do pet típico contra o líder do nível em ≥ 0,03 | SEM FONTE |
| **I-5** | cada chip de regra dispara | no confronto do `alvo` do chip (`itens.ts`), a regra dispara em ≥ 1 de cada 2 lutas, quando não está coberta (decisão DE-3) | SEM FONTE; o achado da R4 |

## 3. O método

**As lutas são de CPU contra CPU, com semente,** pelo motor do jogo (`web/app/motor/`, só o Node, sem tela):
- **o núcleo:** `jogarTR` e `jogarLuta`, com as regras `CV21E_TR`;
- **os lutadores:** os pets por `lutadorPet`. O pedido dizia `lutarPet`, mas a função do motor é `lutadorPet`, em `gambits_pet.ts`. Os
  bots, NPCs e líderes saem de `lutadorBot`, e os Megas da Liga, das instalações e da Fábrica, dos módulos deles;
- **as séries:** `jogarSerie` e `jogarSequencia` (Cidadela, Liga, Torre, Palácio), e o `TentativaFabrica` e o Salão pelos módulos;
- **o pet típico** é um perfil canônico: a forma, o caráter canônico e o treino típico por `perfilDe`, como na rodada das formas. Não é uma
  vida inteira. A meta P-4 é a única que usa vidas (`Motor` com o dono atencioso e o treino em rodízio), porque mede a evolução.

**Os confrontos:**
- **todos contra todos em cada estágio:** as formas adultas (8 × 8), as linhas do Rookie e do Champion e as sombrias contra as normais;
  sempre com os lados trocados;
- **estágio contra estágio:** o pet típico de cada estágio contra o de cima e o de dois acima (P-1);
- **cada lugar da campanha:** o pet típico de cada forma contra o líder e os desafiantes do lugar (G-1, G-2);
- **o fim de jogo:** a Liga, a Torre, o Palácio, a Fábrica e o Salão, com os pets típicos de cada forma;
- **o relógio** (T-1…T-5) sai de todos os confrontos acima. Nenhuma bateria própria é necessária.

**Quantas lutas:**
- **200 por célula** (100 sementes × os dois lados). Com p = 0,5, o erro padrão é 0,035, e uma faixa de ±0,10 fica a mais de 2,5 erros
  padrão. A conta é a binomial (SEM FONTE além dela).
- **O custo:** a matriz 8 × 8 tem 28 pares × 200 = 5 600 lutas, perto de 5 s no Node (0,86 ms por luta, R0). A rodada inteira fica em
  minutos.
- **P-4 usa vidas:** 50 pets por estágio, no mesmo gerador dos saves do e2e (`web/app/e2e/gerar_save_*.mjs`).

**As sementes (uma faixa nova):**
- **a calibração:** `68101…68505`. Todas as fases de ajuste (1 a 4) usam só ela;
- **a conferência** (a validação única, fase 5): `70101…70505`. Roda uma vez, depois de congelar tudo;
- as duas faixas estão livres hoje: nenhuma aparece em `FAIXAS_RESERVADAS` nem em `FAIXAS_QUEIMADAS`
  (`experiments/bancada/faixas.py`);
- **elas entram na `FAIXAS_RESERVADAS`** com a fonte ("equilíbrio do combate em tempo real: calibração" e "…: conferência"), num commit
  próprio, depois da aprovação do plano e antes da primeira luta. Neste PR elas **não** entram, porque a faixa nova é pedida ao
  coordenador e só se reserva com o plano aprovado (DE-6, DECIDIDA: reservar);
- as sementes 101…505 seguem só nos testes.

**O paralelismo:** no máximo 4 processos ao mesmo tempo. A máquina fica instável sob carga (coordenação, 2026-10-30).

**Os scripts e os artefatos:**
- os scripts ficam em `web/app/scripts/equilibrio_tr/`, um por fase, rodados com `npx tsx`;
- as saídas ficam em `web/app/scripts/medicoes/equilibrio_tr/<fase>/`, em JSON, com as sementes e o commit;
- cada fase escreve um relatório curto em `docs/EQUILIBRIO_COMBATE_TR.md`;
- nenhum número de resultado entra no relatório sem o JSON que o produz.

**A ordem (como a rodada das formas):**
1. **fase 1, o relógio** (T-1…T-5): os números do `CTR_TR`;
2. **fase 2, as formas** (F-1…F-7): as listas das formas e as passivas, em cima da fase 1;
3. **fase 3, o estágio, o treino e a evolução** (P-1…P-4);
4. **fase 4, a progressão, o fim de jogo e os itens** (G-1…G-6, I-1…I-5): os fatores e os itens;
5. **fase 5, a validação única** de todas as metas nas sementes de conferência. Nenhum número muda por causa dela; o que reprovar é
   relatado, e o Matheus decide se aceita como exceção.

## 4. O que pode mudar e o que não pode

**Pode mudar** (todos são do jogo web e PROPOSTOS hoje):
- **o relógio e o espaço** (`CTR_TR`): o ritmo das decisões, o atordoamento da interrupção, o andar, o recuo, a arrancada, o projétil, as
  faixas de distância (perto e médio), o contato e o empurrão;
- **as listas das formas** do jogo (`bots.ts`): as listas V21E dos bots e as listas das arenas (`GAMBITS_ARENA`);
- **os fatores:** dos líderes (`arenas.ts`), dos desafiantes (`CESC_V9.fatorNpc`), da Liga (`FATOR_LIGA_V9`), dos rivais das instalações,
  do Salão (`FATOR_SALAO_V9`) e da Fábrica (`FATOR_RIVAL_FABRICA_V9`);
- **a escala dos pets** (`CESC_V9`: a vida por estágio e o beta);
- **os itens** (`CIT`, `itens.ts`): o valor de cada carta e chip e as restrições de uso;
- **a estrutura das séries:** a cura entre as lutas da Liga e o número de lutas da Cidadela (só com DE-2).

**Não pode mudar:**
- **o que o Matheus decidiu:**
  - o tempo de turno, o limite e a morte súbita (D-5);
  - o instante do golpe igual para todos (D-1);
  - a trava 1/3/5, o limite do desafiado e "Champion nunca vence Mega";
  - a sombria nunca chega ao Mega;
  - nenhum controle durante a luta;
- **os números conferidos contra o Python:** a base do combate (`CV`, `CV21`, `CSO`) e as chaves da V21E. O `constantes.test.mjs`
  compara cada um com a config do Python, e o Python não muda nesta rodada. A alavanca equivalente no tempo real fica no `CTR_TR`;
- **o determinismo:**
  - mesma semente e mesmo log dão a mesma luta;
  - só + − × ÷ e `Math.min`/`max` no núcleo (D-7);
  - as RNG separadas por lado.

**A versão de pet.** Toda mudança de número muda as vidas v13 gravadas e o gabarito `test/gabaritos/v13_vidas_ts.json`. A regra do
`web/app/CLAUDE.md` é "uma versão de pet por mecânica, e os gabaritos não mudam". O caminho é a decisão DE-1.

## 5. O critério de parada

Cada fase para quando:
- **todas as metas dela passam** nas sementes de calibração; ou
- **três rodadas de ajuste da fase** (PROPOSTO, SEM FONTE) não fecham uma meta. Nesse caso a fase para, a meta é relatada como "não
  fechou", com o melhor valor e o porquê, e a fase seguinte começa em cima do que ficou.

Em qualquer fase:
- **um teste de replay ou de determinismo que quebre** para tudo até ser consertado (`CLAUDE.md`);
- **um ajuste que reprova uma meta já fechada de uma fase anterior** volta atrás.

**A rodada acaba** depois da fase 5 (a validação única), com a tabela de todas as metas, na calibração e na conferência.

## 6. O que fica fora

- **as regras de ambiente das arenas do UP** (a maré, a lava, o ringue, a área que fecha): E7, só o desenho;
- **os clipes do UP** (`CLIPES_UP`, desligado à espera do Matheus) e todo o desenho e o som: a rodada mede o motor, sem tela;
- **o Python da pesquisa:** o combate em tempo real não existe nele, e ele não muda;
- **os dados do Digimon UP** (os status, os golpes e os atributos do jogo): D-1, o resultado não depende deles;
- **o DigiBrain modular e o cérebro A**, que não lutam.

## 7. As decisões (DECIDIDAS pelo Matheus em 2026-10-30, pela recomendação)

Nas palavras do Matheus, pela coordenação (2026-10-30): "após isso segue as recomendações". Cada decisão abaixo vale como a recomendação
dela, e o custo de errar fica registrado.

| # | a decisão | a recomendação (DECIDIDA pelo Matheus em 2026-10-30) | o custo de errar |
|---|---|---|---|
| **DE-1** (DECIDIDA) | os números novos entram numa versão nova de pet (v14) ou mudam a v13? | **v14**, como a v9 foi "o combate equilibrado". Com o descarte com aviso, se ele quiser tirar a v13, ou com a v13 viva e o ramo por versão | v14 traz de volta um ramo por versão no motor, que o D-9 acabou de tirar. Mudar a v13 quebra a regra "uma versão por mecânica" e muda as vidas já jogadas (o gabarito v13 seria regravado) |
| **DE-2** (DECIDIDA) | a Cidadela fica com 3 lutas seguidas sem cura ou passa a 2? | **3**, até a fase 4 medir T-3 e G-1. Passar a 2 só se T-3 reprovar | com 3, a série pode passar de 4 min de tela; com 2, a Resistência perde peso e a medalha fica mais fácil (G-1 muda) |
| **DE-3** (DECIDIDA) | o chip coberto por uma regra do pet: avisar na tela de equipar ou mudar a ordem da lista? | **avisar**: a lista não muda, e o jogador escolhe outro chip | o aviso não muda nenhuma luta. Mudar a ordem (o chip antes da primeira regra com a mesma condição) muda as lutas de todo pet com chip e entra na DE-1 |
| **DE-4** (DECIDIDA) | se P-4 reprovar (a taxa de 0,8 não é alcançável com o treino típico): baixar o `CLE.limiarTaxa` ou ajustar os rivais do sparring? | **ajustar os rivais** (os fatores, na fase 4) e manter o 0,8, que é o critério da evolução desde a v4 | baixar o limiar muda a evolução de todo pet e o significado de "qualificado". Ajustar os rivais pode empurrar G-1 e G-2 |
| **DE-5** (DECIDIDA) | a meta de estágio: a de hoje (vizinho ≤ 0,10) ou a da arena do UP (o de cima vence ~0,70, dois acima ~0,85)? | **a de hoje** (P-1): "Champion nunca vence Mega" está decidido, e a progressão do DigiLab foi calibrada nela | com a do UP, um pet de baixo bem treinado vence às vezes, e a campanha e as medalhas mudam de ritmo |
| **DE-6** (DECIDIDA) | as faixas de sementes `68101…68505` (calibração) e `70101…70505` (conferência) | **reservar** as duas na `FAIXAS_RESERVADAS` num commit próprio, depois da aprovação | sem reservar, outra frente pode usar a mesma faixa, e a validação deixa de ser única |
| **DE-7** (DECIDIDA) | a duração alvo da luta (T-1: média de 40 a 60 s) | **manter**: ela cerca a medida de hoje e fica antes da morte súbita | uma luta mais longa pesa nas séries (Cidadela, Liga, Salão); uma mais curta reduz o efeito das regras aprendidas |

## 8. A entrega

- **Um PR por fase**, no branch `v2-combate-tr-equilibrio`, cada um com a tabela das metas da fase, na calibração, e os artefatos.
- **Depois da fase 5**, um PR com a tabela de todas as metas, na calibração e na conferência, e as exceções que o Matheus aceitar.
- **O merge é só do Matheus.**
