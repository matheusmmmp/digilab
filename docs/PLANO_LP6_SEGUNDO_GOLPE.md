# PLANO LP6: o segundo golpe e a arena do Ultimate e do Mega (2026-11-11)

Status: as decisões 1 a 3 (o segundo golpe) foram DECIDIDAS pelo Matheus em 2026-11-11 ("pode seguir para o plano lp6"). A decisão 4 (a arena) segue
PROPOSTA, com a recomendação aplicada até ele dizer outra coisa. A fase foi decidida antes ("Sim, depois da LP5"). Os números seguem PROPOSTOS, SEM FONTE.
Tarefa-mãe: [TAREFA_V3_LUTA_POC.md](TAREFA_V3_LUTA_POC.md). A LP5 fechou na main em 2026-11-11 (#789, #798, #800: o `lp5_3` é a v23), e a LP6
parte dela. O pedido do Matheus junta a pendência da arena do Ultimate e do Mega a esta fase ("pode seguir para o plano lp6 e a outra
pendência do tamanho da arena").

## 1. Pergunta

Hoje cada forma da arena tem um só golpe, e é ele que diz se o Digimon luta de longe ou de perto (`web/app/motor/arena/formas.ts`).
Nas 75 formas:

- **50 atiram e não têm golpe de perto.** Quando o inimigo encosta, o atirador recua ou espera (a D-LP5-12).
- **25 batem de perto e não têm ataque de longe.** Diante de quem foge, ficam correndo atrás.
- **Só 7 têm habilidade própria,** e ela é do mesmo tipo do golpe: o Togemon, o Lillymon, o Myotismon, o Machinedramon e o Piedmon,
  de longe; o MetalSeadramon e o Puppetmon, de perto. As outras 68 repetem o golpe na habilidade (`sim.ts:40`: `sk = forma.habilidade || g`).

A pergunta da LP6: **um segundo golpe, do tipo que falta, deixa a luta mais legível e menos dependente da distância, sem quebrar o
que a LP5 calibrou?**

## 2. O que já existe no motor

- O lutador já tem dois ataques, o golpe (`g`, com a `recarga`) e a habilidade (`sk`, com o `recSk` pelo `hcd`) (`sim.ts:40–48`,
  `:216–224`).
- A habilidade sai pela recarga longa (o `hcd`), e não pela distância. Por isso ela não serve como golpe de perto do atirador: ela
  sairia rara e na hora errada.
- O golpe de perto e o tiro já têm todo o caminho: o alcance (`EQ.alcanceCorpo` 44 px, `ACAO.alcanceDist` 150 px), o dano
  (`danoCorpo`, `danoProj`), o projétil e a leitura do golpe de perto pela esquiva (a D-LP5-14).

## 3. O desenho proposto

Um terceiro campo na forma, o **golpe de apoio** (`apoio`), do tipo oposto ao golpe principal. Ele sai pela distância, não pela recarga
da habilidade:

| a forma | o golpe principal | o golpe de apoio | quando sai |
|---|---|---|---|
| atiradora (50) | o tiro de hoje | um golpe de perto, curto | o alvo está a menos da `distMin` do tiro (110 px no `lp5_3`) e a recarga do apoio zerou |
| de perto (25) | o golpe de hoje | um tiro fraco e lento | o alvo está além do alcance de perto por um tempo (ele foge ou está numa moita) e a recarga do apoio zerou |
| com habilidade própria (7) | sem mudança | o apoio do tipo que falta, como as outras | igual às linhas acima |

As regras do apoio (os números são PROPOSTOS, SEM FONTE, e entram na calibração da LP6):

- **Mais fraco que o golpe principal:** o dano do apoio é uma fração do principal (proposta: 0,6).
- **Com recarga própria,** mais longa que a do golpe (proposta: 2 vezes). Assim o apoio não vira o ataque de sempre.
- **O apoio de perto do atirador interrompe a espera do tiro (a D-LP5-12).** Ele não troca o recuo: o atirador bate e recua.
- **O tiro fraco de quem luta de perto** usa o projétil genérico do motor e a velocidade de 20 do `Guide`. O tipo do projétil fica
  como hoje.
- **A esquiva lê o apoio de perto** igual ao golpe de perto de hoje (a D-LP5-14).
- **Os NPCs e os rivais dos torneios ganham o apoio** pela mesma regra, porque usam as mesmas formas.

## 4. A animação (sem sprite novo)

Os sprites de luta só têm um clipe de ataque por Digimon, o `Attack_1`. Os 7 com habilidade própria já usam o mesmo clipe na
habilidade (o cabeçalho de `formas.ts`). A LP6 segue o mesmo caminho:

- **O apoio reaproveita o `Attack_1`,** mais rápido (proposta: 0,6 do tempo) e com um avanço curto do corpo, no de perto.
- **O efeito de acerto muda:** o apoio de perto usa o `Fx_Battle_Hit_A_Normal` ou o `Fx_Member_Hit_Slash_A`, que o jogo de origem
  já usa como golpe genérico. O tiro fraco usa um projétil pequeno do palco.
- **Nenhuma parte nova no desenho** (a regra das poses sem acréscimos).
- Um clipe próprio para o apoio (uma pose-chave por Digimon, pelo método barato das ações geradas) fica como passo opcional depois,
  com o Fable 5.2 para a animação.

## 4a. A arena do Ultimate e do Mega

A pendência veio da LP5-1 (a D-LP5-15): **"a arena maior é só visual, ou dá mais espaço de verdade?"** A LP3c (#778) já resolveu a parte visual:
os Megas cabem na tela e a escala não pula com o zoom. O que falta é o espaço da luta. Hoje toda luta, do Rookie ao Mega, acontece na mesma
elipse do mundo lógico (`ELIPSE` em `web/app/motor/arena/constantes.ts`: rx 210, ry 84, num mundo de 480 × 280). Os corpos grandes se
empurram, e o tiro com a distância mínima de 110 px quase não tem para onde recuar.

A proposta: **a elipse cresce com o estágio dos dois lutadores** (o maior dos dois), atrás de uma chave própria (`arenaPorEstagio`,
desligada):

| o estágio | o fator da elipse (PROPOSTO, SEM FONTE) |
|---|---|
| In-Training, Rookie e Champion | 1,0 (a de hoje) |
| Ultimate | 1,15 |
| Mega | 1,3 |

- **Tudo que é da cena escala junto:** as zonas, os obstáculos, a área segura que fecha, a linha da maré e os pontos de início.
  O tamanho dos corpos, o alcance e a velocidade não mudam. É só o chão que cresce.
- **O palco** enquadra a elipse maior pela câmera da LP3c, sem sprite novo.
- **A calibração** entra na mesma rodada curta do segundo golpe (LP6-3), porque os dois mexem na distância entre os lutadores.

## 5. As etapas

| etapa | o que entra | a chave |
|---|---|---|
| **LP6-0** | este plano revisado e as decisões da seção 7 | nenhuma |
| **LP6-1: o núcleo** | o campo `apoio` nas formas (gerado, não à mão), a regra de quando ele sai, a elipse por estágio (seção 4a), cada um com a sua chave; os testes: o replay bit a bit e a luta com as chaves desligadas igual à v23 | desligadas |
| **LP6-2: o palco** | o apoio no desenho (o clipe mais curto, o efeito de acerto, o tiro pequeno) e a câmera na elipse maior, as capturas no desktop e no celular, para a aprovação do Matheus antes do PR | desligada |
| **LP6-3: a calibração** | uma rodada curta da bancada (`web/app/scripts/equilibrio_poc/`), só nos números do apoio e da elipse e nos que eles mexerem (o dano do projétil, o recuo), nas sementes de calibração, e a conferência nas 87xxx | desligada |
| **LP6-4: no jogo** | uma `VERSAO_PET` nova com a chave ligada, como a LP5-5 fez com a v23 | ligadas |

## 6. O que fica de fora

- O controle do jogador na luta: o pet continua lutando sozinho.
- As regras dos mapas e as séries sem cura da Liga e da Torre: ficam com a investigação do núcleo.
- Sprites novos gerados: só no passo opcional da seção 4.

## 7. Decisões do Matheus

As decisões 1 a 3 foram DECIDIDAS como recomendadas ("pode seguir para o plano lp6", 2026-11-11). A 4 está PROPOSTA. A 2 foi atualizada na LP6-3,
pela R2 (abaixo).

1. **O apoio sai pela distância, com recarga própria (seção 3), ou ele ocupa o lugar da habilidade das 68 formas que a repetem?**
   - **Recomendado:** pela distância, com recarga própria. A habilidade sai pela recarga longa e na hora errada para o atirador.
   - **O custo de errar:** pela distância é um campo novo no motor e na tabela das formas. Pela habilidade é mais barato, mas o
     atirador colado continua sem resposta durante a maior parte da luta.
2. **As 7 formas com habilidade própria também ganham o apoio?**
   - **Recomendado:** sim, para todo Digimon ter as duas distâncias. Quatro delas estão entre os NPCs que nenhum total fecha.
   - **O custo de errar:** os líderes ficam com três ataques, e a identidade deles muda um pouco.
   - **Atualizada na LP6-3 (2026-11-11), pela R2:** o Matheus escolheu "(a) Apoio só no Ult/Mega (Recommended)", e o Gerente repassou.
     - **O que vale agora:** o apoio só existe na luta em que o maior estágio dos dois lutadores é Ultimate ou Mega.
     - **O que muda da decisão original:** ela queria todo Digimon com as duas distâncias. Agora, no In-Training, no Rookie e no Champion,
       ninguém tem o apoio. As 7 formas com habilidade própria seguem com ele quando a luta é de Ultimate ou de Mega.
     - **Por quê:** a R0 e a R1 mostraram que o apoio derruba quem atira no Rookie e no Champion, nas duas regras do apoio de perto. Só com a
       elipse, esses dois estágios ficam como no `lp5_3`.
     - **A regra antiga:** o apoio de perto sem o recuo. A regra do recuo da R1 fica atrás de uma chave própria, desligada (D-LP6-3-7).
3. **O clipe do apoio:** reaproveitar o `Attack_1` (seção 4) ou gerar uma pose-chave por Digimon já na LP6-2?
   - **Recomendado:** reaproveitar o `Attack_1` na LP6-2. A pose-chave fica como passo opcional, depois das capturas.
   - **O custo de errar:** com o clipe reaproveitado, o apoio pode parecer igual ao golpe; as capturas mostram isso antes do PR.
4. **A arena do Ultimate e do Mega: espaço de verdade (seção 4a) ou só o visual que a LP3c já fez?**
   - **Recomendado:** espaço de verdade, com a elipse por estágio, atrás de chave, e calibrada junto com o segundo golpe.
   - **O custo de errar:** com espaço de verdade, a luta do Mega fica mais longa, e os torneios e os NPCs mudam (a LP6-3 mede isso). Só o
     visual mantém os corpos grandes se empurrando e o tiro sem espaço para recuar.

## 8. A LP6-3: o que a rodada mede (registrado antes de qualquer luta, 2026-11-11)

O pedido veio do Gerente, com as palavras do Matheus: "pode seguir para o plano lp6 e a outra pendência do tamanho da arena". A rodada
usa a bancada da LP5 (`web/app/scripts/equilibrio_poc/`) sem mudar as metas, a régua nem a regra de escolha
(`docs/PLANO_EQUILIBRIO_LUTA_POC.md`, seções 2, 4.2 e 4.4).

**O ponto de partida.** O candidato `lp6_0` (`candidatos.ts`) é o `lp5_3` com as duas chaves da LP6-1 ligadas e os números dela: o apoio
com dano de 0,6, recarga de 2 vezes, clipe de 0,6 e espera de 1 500 ms (`APOIO_LP6`), e a elipse de 1,15 e 1,3 (`ARENA_POR_ESTAGIO_LP6`).
O teste `test/equilibrio_poc_lp6.test.ts` confere três coisas. Primeiro, o `lp6_0` só difere do `lp5_3` nas duas chaves. Segundo,
desligadas, nada entra na luta. Terceiro, a luta da bancada é a do núcleo com as mesmas entradas.

**A comparação.** O `lp5_3` sem as chaves, das medidas que já estão no git. Na calibração, `lp5_3/calibracao/resumo.json` (commit
`4a59d680`) dá 10 de 21: P1, P4, T1, T3, E1, D1, D3, A2, G4 e S1. Na conferência, `lp5_4/conferencia/resumo.json` (commit `d4debac3`)
dá 9 de 21, as mesmas sem o P4.

**As metas.** São as mesmas 21 da LP5, com os mesmos critérios (`criterios.ts` e `resumo_metas.ts`):

| tipo | metas |
|---|---|
| **protegidas** | as 10 que o `lp5_3` passa na calibração |
| **as que a LP6 deve mexer** (SEM FONTE) | A1 (atira × de perto), D1 e D2 (duração e empates), A2 (a distância do tiro), V1 (variedade) e as do Ultimate e do Mega (os grupos de formas, o P3, o G1 a G3) |

**As alavancas.** Só no candidato da bancada, PROPOSTAS, SEM FONTE.

| alavanca | hoje | o que é |
|---|---|---|
| `apoio.dano` | 0,6 | fração do dano do golpe principal |
| `apoio.recarga` | 2 | vezes o ciclo do ataque |
| `apoio.ritmo` | 0,6 | o tempo do clipe e do instante do golpe, em vezes os do golpe |
| `apoio.longeMs` | 1 500 | quanto o alvo fica longe antes do tiro fraco |
| `arena.Ultimate` e `arena.Mega` | 1,15 e 1,3 | a elipse por estágio |
| `tiro.danoProj` e `tiro.recuo` | 0,7 e 1,5 | as do tiro que o apoio e a elipse mexem |

Sobre o `apoio.ritmo`: a tabela do git tem 0,6. Outro ritmo só existe na bancada, pela mesma regra do `tools/gerar_tabela_arena.py`
(`tabelaDoRitmo`), e um teste confere que a regra refaz a tabela do git.

Ficam fora:
- a velocidade do tiro fraco (20) e o resto do `tiro`;
- o mapeamento, os NPCs, os rivais e a esquiva, já fechados na LP5;
- o núcleo fora das duas chaves.

**As fases.**
1. **R0:** a medida inteira do `lp6_0` nas sementes de calibração. É a linha de base com as chaves, para a primeira decisão.
2. **R1 a R3:** grades curtas (`grade.ts`, fase `lp6_3`) nas alavancas acima. São no máximo 3 rodadas, com a regra de parada e a regra
   de escolha da LP5 (seção 4.2): um número muda só quando uma meta reprovada passa. Um ajuste que reprova uma meta protegida volta atrás.
3. **A medida inteira** do candidato escolhido na calibração.
4. **A conferência, uma vez** nas sementes de conferência, com o candidato fechado num commit antes dela. A bancada recusa rodar de novo um
   grupo que já tem o JSON dela, e nada se ajusta olhando para a conferência.

**As sementes.**
- **A calibração:** as bases 86101…86505.
- **A conferência:** as bases 87101…87505, como na LP5, pelo pedido do Gerente.
- **O desvio D-LP6-3-1:** as 87xxx já foram vistas na LP5-4 pelo `lp5_3`. Nada da LP6 se ajusta nelas, mas o valor do `lp5_3` nelas é
  conhecido.

**Os pontos de decisão.** A rodada para em cada um e leva ao Matheus as opções, a recomendação e o custo de errar: depois da R0, depois de
cada grade e antes da conferência.

**A carga.** No máximo 4 processos e uma medida por vez (V3-D8), pelo gate `tools/pre_run.py --medicao`.

**A R0 e a decisão da R1 (2026-11-11).**
- **A R0** (PR #834): o `lp6_0` passa 6 de 21. Caem o P1, o P4, o G4 e o S1, e o A1 piora no Rookie (0,256) e no Champion (0,298).
  - O apoio de perto prende quem atira junto do inimigo.
- **A R1:** a resposta do Matheus ao #834, repassada pelo Gerente, foi "Regra e grade": a (b) e a (a) juntas, na mesma rodada. Antes dela,
  nesta sessão, ele tinha escolhido só a (a), "Grade do apoio (a)". A grade não chegou a rodar com a regra antiga.
- **A regra (D-LP6-3-4):** o atirador bate e recua, como a seção 3 já dizia, e a R0 mostrou que ele ficava colado.
  - Depois do apoio de perto, quem atira recua sem atacar até o alvo ficar na `distMin` do tiro. O recuo dura no máximo a espera do tiro
    (`esperaMax`, 1 500 ms no `lp5_3`), na velocidade do recuo do tiro.
  - Encurralado, o recuo acaba pelo tempo, a espera do tiro já vale como cumprida, e ele atira.
  - Sem o `tiro` na entrada, o limite é a metade do alcance, e o tempo é o `RECUO_APOIO_SEM_TIRO_MS` (1 500 ms; PROPOSTO, SEM FONTE).
  - Com as chaves desligadas, a luta é a de sempre: o gabarito da LP6-1 (`arena_lp6_v23.json`, a v21 e a v23) confere igual.
  - Os testes ficam em `web/app/test/arena_lp6_recuo.test.ts`.
- **A grade,** registrada aqui antes de rodar e já com a regra nova, mexe nos números do apoio:
  - O dano do apoio em 0,3, 0,45 e 0,6.
  - A recarga em 2, 3 e 4 vezes.
  - A espera do tiro fraco em 1 500 e 3 000 ms.
  - São 18 pontos, mais o controle `ctrl_arena`: a elipse ligada e o apoio desligado. O ponto `d60_r2_l15` é o `lp6_0`, agora com a regra
    nova. A R0 (6 de 21) foi medida com a regra antiga.
  - O ritmo fica em 0,6 e a elipse em 1,15 e 1,3; os dois ficam para a R2.
- **Como roda:** a grade usa a fase `lp6_3/r1`. Roda em todos os grupos, menos a vida, em 3 bases da calibração e com os tamanhos
  inteiros. A regra de escolha é a da seção 4.2 do plano da LP5, com as 10 metas protegidas do `lp5_3`.
- **Se nenhum ponto devolve o A1 e as protegidas,** a rodada para e volta ao Matheus com os números, antes de qualquer outra alavanca.

**A R1 e a decisão da R2 (2026-11-11).**
- **A R1** (PR #834, `lp6_3/r1`): nenhum dos 18 pontos do apoio passa nas protegidas. O recuo da regra nova piorou quem atira: no
  Rookie, o A1 fica de 0,13 a 0,27.
- **O controle `ctrl_arena`** (só a elipse, sem o apoio) passa 8 de 21. Deixa o Rookie e o Champion como hoje (0,47 e 0,54), mas o
  Ultimate (0,74) e o Mega (0,65) pendem para quem atira.
- **A R2:** o Matheus escolheu "Apoio só no Ult/Mega (a)".
- **As regras (D-LP6-3-7, no núcleo, atrás da chave do apoio):**
  - **o apoio pelo estágio:** o apoio tem o campo opcional `desde`. Com ele, o apoio só existe quando o maior estágio dos dois lutadores
    é esse ou maior. Abaixo, a luta é a mesma sem a chave, byte a byte;
  - **o recuo:** a regra do recuo da R1 (D-LP6-3-4) fica atrás do campo opcional `recua`, desligado. Sem ele, o apoio de perto é o da
    LP6-1, a regra antiga da R0;
  - **os testes:** `web/app/test/arena_lp6_recuo.test.ts`.
- **A grade (`lp6_3/r2`, registrada aqui antes de rodar):**
  - o apoio desde o Ultimate (`desde: 3`), sem o recuo, com a espera do tiro fraco em 1 500 ms e o clipe em 0,6;
  - o dano do apoio em 0,45 e 0,6;
  - a recarga em 2 e 3 vezes;
  - a elipse (Ultimate e Mega) em 1/1, 1,1/1,2, 1,15/1,3 e 1,2/1,4;
  - são 16 pontos, em todos os grupos menos a vida, em 3 bases da calibração e com os tamanhos inteiros;
  - a regra de escolha é a da seção 4.2 do plano da LP5, com as 10 protegidas do `lp5_3`;
  - todos os números são PROPOSTOS, SEM FONTE.

**A R2 e a escolha do candidato (2026-11-11, registrada antes das medidas inteiras).**
- **A R2** (PR #834, `lp6_3/r2`): 10 dos 16 pontos passam 9 de 21, e voltam o P1, o P4 e o G4.
  - **O S1** cai em todos os pontos. No Rookie, é ruído das 3 bases. No Ultimate e no Mega, depende da elipse.
- **A decisão:** o Matheus escolheu "(a) Medir os 3 (Recommended)", repassado pelo Gerente.
- **Os finalistas** (`candidatos.ts`) têm o apoio desde o Ultimate, sem o recuo, dano 0,6 e recarga 3 vezes:
  - `lp6_3_u110`, a elipse em 1,1/1,2;
  - `lp6_3_u115`, em 1,15/1,3;
  - `lp6_3_u120`, em 1,2/1,4.
- **As medidas:** cada finalista roda inteiro nas 5 bases da calibração, um por vez, com o `medir_tudo.ts`, nas fases `lp6_3_u110`,
  `lp6_3_u115` e `lp6_3_u120`.
- **O critério, nesta ordem:**
  1. **As 10 protegidas do `lp5_3` passam,** o S1 inclusive. Quem reprova uma delas sai.
  2. **Entre os que ficam, o de menor desvio do A1** no Ultimate e no Mega, o maior entre `|A1 Ultimate − 0,5|` e `|A1 Mega − 0,5|`
     (o A1 na soma dos 8 mapas).
  3. **Se dois ficam a menos de 0,01 um do outro,** vence o mais perto dos números da LP6-1, o `lp6_3_u115`, e depois o de menor fator.
- **Se nenhum passa as 10 protegidas,** a escolha volta ao Matheus antes da conferência, com os números.
- **Se o escolhido não tiver a elipse 1,15/1,3,** a decisão 4 do plano muda. Isso é um desvio a registrar e a avisar ao Gerente.
- **A conferência** roda uma vez nas 87xxx, com o escolhido, na fase `lp6_3`. A comparação usa o `comparar_conferencia.ts
  --conferencia lp6_3`.
