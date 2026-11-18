# ESPEC V3 — SOCIAL_PAR, E1: o parceiro sob intervenção na bancada (2026-11-17, PROPOSTO)

**Status: APROVADA pelo Matheus em 2026-11-17 ("Aprovo a E1"): a SP-1 e a SP-2 da investigação e as E1-1 a E1-6 (seção 8), pela
recomendação (D-SP-8).** Os números continuam PROPOSTOS. A
investigação que motiva esta etapa é `docs/INVESTIGACAO_V3_SOCIAL_PAR.md`; a tarefa, `docs/TAREFA_V3_SOCIAL_PAR.md`. Commit de
referência: `358895585858a06a6a8de4b7cab3e3890497dd11`.

## 1. O que a etapa entrega, e o que não entrega

- **Entrega:** o instrumento dos experimentos A e B, só na bancada do Python:
  - o parceiro gravado, que reexecuta decisões pelo próprio motor;
  - a perturbação exógena (o `levar_pet` no grupo);
  - as medidas de contato e de contingência;
  - dois pares de regra fixa como controles positivos.
- **Não entrega:**
  - nenhum mecanismo no pet: nenhuma mudança no DigiBrain, no corpo ou no jogo web;
  - nenhuma run de pesquisa: a A0 e a B0 vêm com o plano de análise delas, depois;
  - nada no TS. A intervenção é pesquisa (SP-2), e o jogo não a lê.

## 2. As peças e as interfaces

### 2.1 A chave

`ConfigIntervencaoSocial` em `digilab/config.py`, desligada, com status e fonte:

| campo | padrão | status |
|---|---|---|
| `ligada` | `False` | DECIDIDO quando o Matheus aprovar a E1; pesquisa, nunca no jogo |
| `janela_reencontro` | 96 decisões (1 dia) | PROPOSTO, SEM FONTE |
| `raio_contato_celulas` | 1 (o `raio_toque_celulas` de hoje) | PROPOSTO, igual ao toque |
| `raio_perto_celulas` | 6 (o `raio_visao_celulas` de hoje) | PROPOSTO, igual à visão |

Desligada, o `Grupo` é o de hoje byte a byte. Ligada, ela só habilita as peças abaixo: nenhuma muda uma vida que não as use.

### 2.2 A gravação: o `Gravador` e a `PoliticaGravada` (`experiments/bancada/parceiro.py`, novo)

- **O `Gravador`** embrulha a política viva de P sem mudá-la, como a `Coleta` da bancada da cooperação já embrulha o `DigiBrain.agir`
  (`experiments/run_v3_cooperacao_bancada.py:189-202`). A cada decisão ele guarda uma `DecisaoGravada`:

  ```python
  @dataclass(frozen=True)
  class DecisaoGravada:
      tick: int
      acao: str                         # o valor do AcaoPet
      alvo_tipo: str | None             # o tipo do candidato escolhido, ou None (o padrao do motor)
      alvo_id: int | str | None
      alvo_xy: tuple[int, int] | None
  ```

  Ele grava também os eventos do dono de P, que estão no `RegistroGrupo` com o destino `pet:P`.
- **A `PoliticaGravada`** cumpre o `Protocol` `Politica` (`digilab/policy.py:83`) e o gancho `escolher_alvo(acao, candidatos, percepcao, u)`
  (`digilab/mundo.py:21`):

  ```python
  class PoliticaGravada:
      """o parceiro em laco aberto: reexecuta as decisoes gravadas de P pelo motor de P; nao le a observacao para decidir"""
      nome = "gravada"

      def __init__(self, decisoes: list[DecisaoGravada]):
          self._por_tick = {d.tick: d for d in decisoes}     # falha alto se dois ticks repetem
          self.desvios = []                                   # (tick, motivo) de cada reexecucao que nao bateu
          self._atual = None

      def agir(self, obs, rng):
          d = self._decisao_em(obs.tick)    # a gravada neste tick; se nao houver, a ultima com tick <= este (desvio "tick")
          self._atual = d
          return AcaoPet(d.acao)

      def escolher_alvo(self, acao, candidatos, percepcao, u):
          d = self._atual
          if d.alvo_tipo is None:
              return Alvo.ponto(*d.alvo_xy) if d.alvo_xy else None    # o padrao do motor resolvido na gravacao: o ponto onde ele foi
          if d.alvo_tipo in TIPOS_QUE_SE_MOVEM:                        # seguir, onde_comeu, o continuar deles, a bola: so o ponto gravado
              return Alvo.ponto(*d.alvo_xy)                            # (nunca o candidato vivo, que leria onde F esta agora)
          for c in candidatos:                                         # 1) a mesma comida parada, pelo id
              if c.tipo == d.alvo_tipo and c.id == d.alvo_id:
                  return c
          self.desvios.append((d.tick, "alvo_sumiu"))                  # 2) a comida sumiu: o ponto gravado
          return Alvo.ponto(*d.alvo_xy)

      def observar(self, *a, **k):
          pass                                                         # nao aprende

      def estado_interno(self):
          return {"gravada": True, "desvios": len(self.desvios)}
  ```

  - P continua com o motor inteiro, com o corpo, o mundo e a física. Só a decisão vem da lista.
  - A `PoliticaGravada` **não lê a observação para decidir**. Um teste por AST confere que `agir` e `escolher_alvo` só usam `obs.tick` e a
    lista gravada.
  - **O laço aberto vale também pelo alvo.** Um alvo que se move com F (o `seguir`, o `onde_comeu` de F, o `continuar` deles) ou que F
    pode mover (a bola) é reexecutado pelas coordenadas gravadas, e nunca pelo candidato vivo. Pelo id, o `seguir` iria aonde F está
    agora, e P voltaria a responder a F. Só a comida, que não se move, é achada pelo id.
  - **O rótulo do alvo:** o ponto que substitui um alvo social leva o tipo e o id gravados como rótulo (o campo `de` que o alvo já tem
    no TS; no Python, um campo novo, só com a chave). O grupo deriva o toque (`encostou` exige ter seguido, `digilab/grupo.py:463-470`)
    por esse rótulo, para que o toque, a CO3 e o `k` de F saiam iguais aos da VIVO até o t0. O G-GRAV-IDENT confere isso.
  - **A ação que pede o objeto:** o `brincar` gravado com a bola longe do ponto gravado (mais de 1 célula) vira `explorar` até o ponto
    gravado, com o desvio `bola_movida`; o `comer` com a comida sumida vai ao ponto e conta o desvio `alvo_sumiu`. Explorar, comer e
    brincar aceitam o ponto: o mundo de hoje dá o candidato `ponto` só ao explorar (`digilab/mundo.py`, o lugar lembrado), e a E1 confere
    na implementação se comer e brincar aceitam um alvo de ponto. Se não aceitarem, a regra vira "explorar até o ponto", contada como
    desvio, e o relato diz isso.
- **O dono de P na GRAV:** os eventos gravados do dono de P são rejogados nos mesmos ticks, pelo `Canal` de hoje, e o dono sintético de P
  não roda. Assim nada de P responde a F.

### 2.3 A perturbação: o `levar_pet` no grupo

- **O que existe:** o `MotorMundo.levar_pet(x, y)` (`digilab/mundo.py:2351-2358`), que é o evento do dono "pegar o pet e soltar", com o
  evento no log e a falha alta com o pet dormindo (PP-2).
- **O que falta:** o grupo não o aceita (`digilab/grupo.py` não tem `levar_pet`).
- **A E1 acrescenta** `Grupo.levar_pet(ident, x, y)`, só com a `ConfigIntervencaoSocial` ligada. Ele grava `EventoGrupo(tick,
  "levar_pet", [x, y], destino_do_pet(ident), ident, ORIGEM_INTERVENCAO)` e chama o do motor. O `reproduzir_grupo` passa a rejogá-lo, e
  falha alto se a chave estiver desligada.
- **A origem `intervencao`** (nova, ao lado de `dono`) separa no registro a intervenção do experimento do dono de verdade. O jogo nunca
  grava essa origem.
- **O t0 e o destino:**
  - num fluxo novo, `intervencao-social` = `derivar_semente("intervencao-social", s)`, sorteados antes da vida (o dia e a decisão do t0, a
    direção);
  - o d0 é fixo pelo plano, e a direção é sorteada;
  - se F dorme no t0, vale a primeira decisão seguinte em que está acordado;
  - um destino em parede ou água é trocado pela célula livre mais perto, com o desempate estável.

### 2.4 As condições, montadas pela bancada

`experiments/bancada/parceiro.py`:

```python
def vida_vivo(semente, fp_F, fp_P, cfg) -> VidaPar          # os dois vivos; o Gravador em P
def vida_passiva(semente, fp_P, cfg) -> VidaPar             # F trocado pelo Passivo de tests/test_grupo.py:71-80, levado para o modulo
def vida_grav(semente, fp_F, gravacao, cfg, t0) -> VidaPar  # P = PoliticaGravada(gravacao da vida_vivo da mesma semente)
def vida_outra(semente, fp_F, gravacao_passiva, cfg, t0)    # P = PoliticaGravada(gravacao da vida_passiva da mesma semente)
```

- **A ordem fixa:**
  1. a `vida_vivo` **sem** a perturbação, que dá a gravação de P;
  2. a `vida_passiva`, que dá a gravação da OUTRA;
  3. as três condições com o mesmo t0: a VIVO (a `vida_vivo` com o `levar_pet` no t0), a GRAV e a OUTRA.
- **Por que a gravação sai da vida sem perturbação:** até o t0, a GRAV é a vida VIVO decisão a decisão, e é "o P de uma interação anterior
  que deu certo" (o protocolo de Froese e Di Paolo 2008). Depois do t0, só a VIVO tem um P que responde.
- **O `VidaPar`:** a série por decisão das posições, das ações e dos chutes na bola dos dois pets; os desvios da gravação; os consumos
  falhos de P; o registro do grupo e o sha256 dele.

### 2.5 As medidas (`digilab/metrics.py`, a regra "métricas existem uma vez só")

```python
def fracao_em_raio(dists: Sequence[int], raio: int, desde: int = 0) -> float
def tempo_ate_raio(dists: Sequence[int], raio: int, desde: int, janela: int) -> tuple[int, bool]   # (decisoes, censurado)
def episodios_em_raio(dists: Sequence[int], raio: int) -> list[int]                               # as duracoes
def contingencia(d_meu: Sequence[int], d_outro: Sequence[int]) -> float | None
    # P(eu me aproximo em t+1 | o outro se aproximou em t) - P(eu me aproximo em t+1 | o outro se afastou em t);
    # None se um dos dois condicionais nao tem caso
def alternancia(chutes_a: Sequence[int], chutes_b: Sequence[int], janela: int) -> float | None
def alternancia_substituta(chutes_a, chutes_b, janela, deslocamentos: Sequence[int]) -> list[float]   # B deslocado no tempo, circular
```

- As distâncias vêm em células (Chebyshev, a do toque) e em subunidades (euclidiana, a da visão), as duas guardadas.
- "Aproximar" é a distância cair entre duas decisões; "afastar", subir. Tudo em inteiros.

## 3. Os controles positivos (a validação do instrumento)

Duas políticas de regra fixa, **só em `experiments/bancada/parceiro.py`**, nunca no pacote `digilab/` nem no jogo:
- **`PoliticaSeguidor`:** o instinto do mundo de hoje, mas no tempo livre explora com o alvo `seguir` quando há outro à vista e com o
  `vagar` quando não há.
- **`PoliticaEvitador`:** igual, mas foge: explora com o candidato de `vagar` mais longe do outro visto.

**As respostas conhecidas por construção** (as conferências da E1, nas sementes dos testes 101…505, sem faixa):

| par | o que tem de sair | por quê |
|---|---|---|
| seguidor × seguidor | o reencontro mais rápido e o contato mais longo na VIVO do que na GRAV | na VIVO os dois se procuram; na GRAV só F procura, e P segue o rastro da vida antiga |
| seguidor (F) × evitador (P) | o contato mais curto na VIVO do que na GRAV | na VIVO P foge de F; na GRAV P não sabe onde F está |
| qualquer par, na GRAV | a contingência de P para F ≈ 0 (\|c\| abaixo de um limiar do teste) | P está em laço aberto |

Se as duas primeiras linhas não saírem, **o instrumento não mede reciprocidade**, e a E1 para e reporta. Não se ajustam as medidas para
"dar certo".

## 4. Os gates

| gate | o que confere | como |
|---|---|---|
| **G2** | com a `ConfigIntervencaoSocial` desligada, o grupo é o de hoje byte a byte | os gabaritos de hoje do grupo (`tests/gabaritos/dois_pets_vidas_de_hoje.json`, `grupo_python.json.gz`, o da CO7) e os testes `test_grupo*.py` e `test_cooperacao*.py` sem mudança |
| **G-GRAV-IDENT** | **sem perturbação, a GRAV é a VIVO byte a byte**: os eventos do registro, as posições, as ações e os corpos dos dois, com zero desvios. Só o cabeçalho difere, pelo nome do cérebro de P | o teste mais importante da etapa: prova que a gravação é uma reexecução fiel. **O risco conhecido:** se o motor de P gastar a `_rng_politica` fora do `agir`, a GRAV, que não a gasta, sai diferente. O gate acha isso, e a correção é a `PoliticaGravada` gastar os mesmos números (registrado como desvio) |
| **G-GRAV-CEGA** | a `PoliticaGravada` não lê nada da observação além do tick | AST e um espião que muda a observação de P sem mudar as decisões de P |
| **G-LEVAR** | o `levar_pet` no grupo põe o pet no ponto, entra no registro com a origem `intervencao`, é rejogado pelo `reproduzir_grupo` e falha alto com a chave desligada ou o pet dormindo | casos à mão |
| **G-CONTROLE-POS** | as duas primeiras linhas da tabela da seção 3, nas 5 sementes dos testes, em todas | o teste que valida o instrumento |
| **G-MET-NULO** | a contingência de P para F na GRAV, abaixo do limiar | a terceira linha da tabela |
| **G-METRICAS** | as funções novas em casos feitos à mão (séries curtas com a resposta conhecida, a censura na janela, None sem caso) | unidade |
| **G-NUMS** | trocar P por P gravado não muda as rngs de F, as quedas, nem o fluxo `intervencao-social` | o espírito do `test_grupo.py:390` |
| **G-ENGINE** | `engine.py` com o sha256 de sempre | o teste de sempre |

## 5. O que sai da E1, e o que vem depois

- **Sai:** o código e os testes acima, com o relato no PR (categoria implementacao). Nenhum número de pesquisa: os resultados dos controles
  positivos são conferências de teste, não uma run.
- **Depois (A0 e B0), num PR à parte:**
  - o `docs/PLANO_ANALISE_V3_SOCIAL_PAR_A0.md`, commitado antes da primeira vida: as três condições no pet de hoje (o modular nos dois),
    a variante sem comida, a bola com os substitutos, a margem e o N pelo piloto (SP-7);
  - uma faixa nova pedida ao coordenador.

## 6. Os arquivos

| arquivo | o que muda |
|---|---|
| `digilab/config.py` | a `ConfigIntervencaoSocial`, com status e fonte |
| `digilab/grupo.py` | o `levar_pet` no grupo, a origem `intervencao`, o replay dele; tudo só com a chave |
| `digilab/metrics.py` | as seis funções da seção 2.5 |
| `experiments/bancada/parceiro.py` (novo) | o `Gravador`, a `DecisaoGravada`, a `PoliticaGravada`, o `Seguidor`, o `Evitador`, o `Passivo` (do teste) e as quatro montagens |
| `tests/test_social_par_e1.py` (novo) | os gates da seção 4 |
| `tests/gabaritos/` | **nenhum gabarito novo antes**: a chave nova não muda nenhuma vida que já tem gabarito, e o G2 usa os de hoje. Se a mudança do `grupo.py` tocar o caminho de hoje, o gabarito das vidas do grupo de hoje entra num commit próprio, antes (a regra do CLAUDE.md) |
| `docs/TAREFA_V3_SOCIAL_PAR.md` | o resumo da etapa, no fim |
| `docs/registro/2026-11.md` | os desvios da etapa |

**O que não muda:** `engine.py`, o DigiBrain, o corpo, a CO3/CO6/CO7, o jogo web, as faixas de sementes.

## 7. Os critérios de aceitação

1. O G2 e o G-ENGINE passam, e a suíte inteira não ganha falha nova (as 2 que já falham na `main`, `test_fala_livre` e
   `test_gabarito_mvp_produto_web`, ficam como estão).
2. O G-GRAV-IDENT passa em todas as sementes dos testes, com zero desvios.
3. O G-CONTROLE-POS e o G-MET-NULO passam. **Se falharem, a E1 para e reporta com o comando, a saída e a lacuna**, sem mexer nas medidas.
4. O G-GRAV-CEGA, o G-LEVAR, o G-METRICAS e o G-NUMS passam.
5. Nenhum arquivo do `web/app/` muda.

## 8. As decisões da etapa (PROPOSTAS; cada uma com a recomendação e o custo de errar)

| id | a decisão | a recomendação | o custo de errar |
|---|---|---|---|
| **E1-1** | gravar o quê | **a decisão (ação e alvo), reexecutada pelo motor**, e não a posição | gravar a posição pede um membro que não é motor e uma física à parte; a cinemática deixaria de ser a do pet |
| **E1-2** | o alvo gravado que sumiu | **o do mesmo tipo mais perto; senão, o ponto no explorar; cada caso é um desvio contado** | outra regra (ocioso, por exemplo) muda a cinemática de P e confunde com "não responsivo" |
| **E1-3** | o dono de P na GRAV | **os eventos gravados, rejogados** | o dono sintético vivo responderia ao estado de P, que muda com F: um caminho de contingência escondido |
| **E1-4** | a perturbação | **o `levar_pet` que já existe, no grupo, com a origem `intervencao`** | um evento novo pediria outro tipo no registro e outro replay, para o mesmo efeito |
| **E1-5** | o controle móvel | **a OUTRA: P gravado numa vida com F passivo, na mesma semente** | a "sombra" de Auvray pede mexer na percepção de F, o que separa o que F vê da física do mundo |
| **E1-6** | os controles positivos | **o seguidor e o evitador, de regra fixa, só na bancada** | sem eles, um "nenhuma diferença" no pet de hoje não se distingue de um instrumento que não mede |
