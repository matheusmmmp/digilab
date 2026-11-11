# PLANO LP6: o segundo golpe de cada Digimon (2026-11-11, PROPOSTO)

Status: PROPOSTO. A fase foi decidida pelo Matheus ("Sim, depois da LP5", 2026-11-11). O desenho abaixo espera a revisão dele.
Tarefa-mãe: [TAREFA_V3_LUTA_POC.md](TAREFA_V3_LUTA_POC.md). Ela só começa depois da LP5-5 (a v22 no jogo).

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

## 5. As etapas

| etapa | o que entra | a chave |
|---|---|---|
| **LP6-0** | este plano revisado e as decisões da seção 7 | nenhuma |
| **LP6-1: o núcleo** | o campo `apoio` nas formas (gerado, não à mão), a regra de quando ele sai, os testes: o replay bit a bit e a luta com a chave desligada igual à v22 | desligada |
| **LP6-2: o palco** | o apoio no desenho (o clipe mais curto, o efeito de acerto, o tiro pequeno), as capturas no desktop e no celular, para a aprovação do Matheus antes do PR | desligada |
| **LP6-3: a calibração** | uma rodada curta da bancada (`web/app/scripts/equilibrio_poc/`), só nos números do apoio e nos que ele mexer (o dano do projétil, o recuo), nas sementes de calibração, e a conferência nas 87xxx | desligada |
| **LP6-4: no jogo** | uma `VERSAO_PET` nova com a chave ligada, como a LP5-5 fez com a v22 | ligada |

## 6. O que fica de fora

- O controle do jogador na luta: o pet continua lutando sozinho.
- As regras dos mapas, as séries sem cura da Liga e da Torre, e a arena do Ultimate e do Mega: cada uma tem tarefa ou decisão própria.
- Sprites novos gerados: só no passo opcional da seção 4.

## 7. Decisões do Matheus (PROPOSTAS)

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
