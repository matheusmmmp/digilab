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

As decisões 1 a 3 foram DECIDIDAS como recomendadas ("pode seguir para o plano lp6", 2026-11-11). A 4 está PROPOSTA.

1. **O apoio sai pela distância, com recarga própria (seção 3), ou ele ocupa o lugar da habilidade das 68 formas que a repetem?**
   - **Recomendado:** pela distância, com recarga própria. A habilidade sai pela recarga longa e na hora errada para o atirador.
   - **O custo de errar:** pela distância é um campo novo no motor e na tabela das formas. Pela habilidade é mais barato, mas o
     atirador colado continua sem resposta durante a maior parte da luta.
2. **As 7 formas com habilidade própria também ganham o apoio?**
   - **Recomendado:** sim, para todo Digimon ter as duas distâncias. Quatro delas estão entre os NPCs que nenhum total fecha.
   - **O custo de errar:** os líderes ficam com três ataques, e a identidade deles muda um pouco.
3. **O clipe do apoio:** reaproveitar o `Attack_1` (seção 4) ou gerar uma pose-chave por Digimon já na LP6-2?
   - **Recomendado:** reaproveitar o `Attack_1` na LP6-2. A pose-chave fica como passo opcional, depois das capturas.
   - **O custo de errar:** com o clipe reaproveitado, o apoio pode parecer igual ao golpe; as capturas mostram isso antes do PR.
4. **A arena do Ultimate e do Mega: espaço de verdade (seção 4a) ou só o visual que a LP3c já fez?**
   - **Recomendado:** espaço de verdade, com a elipse por estágio, atrás de chave, e calibrada junto com o segundo golpe.
   - **O custo de errar:** com espaço de verdade, a luta do Mega fica mais longa, e os torneios e os NPCs mudam (a LP6-3 mede isso). Só o
     visual mantém os corpos grandes se empurrando e o tiro sem espaço para recuar.
