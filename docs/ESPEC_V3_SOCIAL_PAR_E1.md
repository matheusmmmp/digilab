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

## 9. Adendo 1: os controles positivos de novo, e os dois desvios da implementação (2026-11-17, PROPOSTO)

**Status: APROVADO pelo Matheus em 2026-11-17 ("Aprovo todas"): as A1-1 a A1-6 (9.6), pela recomendação (D-SP-17).** As seções 1 a 8 e o resultado da primeira
conferência não mudam: o `artifacts_v3_social_par_e1/controles_positivos.json` (sha256 `7a1049ac…`) fica como saiu, com os dois `false`
(D-SP-13).

**De onde vem:** o Matheus, em 2026-11-17, "Escreva o adendo", depois de a E1 parar porque os dois controles da seção 3 não separaram a
VIVO da GRAV.

### 9.1 O que a primeira conferência mostrou, e o que o adendo muda por causa disso

| controle da seção 3 | por que não serviu | o que o adendo faz |
|---|---|---|
| seguidor × seguidor | **o teto:** o alcance é de 3,75 células por decisão e o d0 era 5. Um seguidor sozinho fecha o contato em cerca de uma decisão, e a resposta do parceiro não muda o tempo | **sai como controle positivo.** Fica só como descritivo, sem resposta esperada: a vantagem da mutualidade (Froese e Di Paolo 2008) pede uma tarefa em que um sozinho não baste, e este mundo não a tem a esta velocidade |
| seguidor × evitador | **o desenho:** o ponto de fuga era 2 × o vetor até o outro, que some quando os dois estão na mesma célula ou vizinhos | **o evitador é refeito:** foge um passo inteiro na direção oposta ao outro (9.2), e no empate numa direção fixa |

O adendo também põe um controle novo, cuja resposta é conhecida **por construção**: o pet focal parado e o parceiro que o segue.

### 9.2 Os controles do adendo

- **C1, passivo (F) × seguidor (P).** F é o `Passivo` (só fica ocioso ou dorme) e nunca se move. Depois do t0, F está a d0 células de P.
  - Na VIVO, P vê F (d0 = 5 é menor que a visão de 6) e vai até ele.
  - Na GRAV, P repete o caminho gravado, que seguia F onde ele estava antes, e não vai até F.
  - Como F não se move, todo reencontro é obra de P. É o caso mais simples em que o instrumento tem de ver se o parceiro responde.
- **C2, seguidor (F) × evitador corrigido (P).** O evitador, no tempo livre com o outro à vista, explora para o ponto a um passo inteiro
  (o alcance de uma decisão, `velocidade × intervalo`) na direção oposta ao outro:
  - a direção é a das 16 mais alinhada com o vetor do outro para P (a `direcao_do_golpe` de `digilab/mundo.py`, a mesma conta inteira);
  - com os dois no mesmo ponto, vale a direção 0;
  - o ponto é cortado no mapa pela `deslocar`.

  Na VIVO, P foge de F; na GRAV, P repete o caminho gravado e não foge do F de agora.
- **O resto, igual à seção 3:** as sementes 101 a 505, 2 dias, o dono atencioso no comedouro, o t0 no dia 1 pelo fluxo
  `intervencao-social`, o d0 = 5 células. As sementes são as mesmas da primeira conferência: é uma validação do instrumento, não uma run,
  e os controles do adendo são políticas novas. Isso fica dito no resultado.

### 9.3 O que tem de sair (escrito antes de rodar)

| controle | o que tem de sair, em **todas** as 5 sementes | a medida |
|---|---|---|
| **C1** | o tempo até o contato menor na VIVO que na GRAV (a GRAV pode sair censurada), e a fração de contato depois do t0 maior na VIVO | `tempo_ate_raio` e `fracao_em_raio`, raio de 1 célula, janela de 96 decisões |
| **C2** | a fração de contato depois do t0 menor na VIVO que na GRAV | `fracao_em_raio`, raio de 1 célula |
| **G-MET-NULO** (no C2) | a contingência de P a partir de F, na GRAV e depois do t0, None ou com \|c\| ≤ 0,2 (PROPOSTO, SEM FONTE) | `contingencia` |

- **Se o C1 ou o C2 falhar em alguma semente:** a E1 para de novo e reporta, com o comando, a saída e a lacuna. Nenhum controle é
  mudado depois de ver o resultado.
- **Se passarem:** o G-CONTROLE-POS e o G-MET-NULO entram no `tests/test_social_par_e1.py`, e a E1 vai para o PR.
- **O seguidor × seguidor** continua rodando, só como descritivo.

### 9.4 Os dois desvios da implementação, para decidir

- **D-SP-10, o ponto gravado pela porta no motor.**
  - A espec (2.2) mandava trocar a ação por "explorar até o ponto" quando comer e brincar não aceitassem um ponto.
  - A implementação abriu uma porta no motor: o `MotorMundo.aceitar_ponto_gravado`, só com a `ConfigIntervencaoSocial` ligada, deixa
    comer e brincar irem a um ponto, sem comer nem chutar ao chegar.
  - O motivo: trocar a ação muda o que F vê de P e o gasto, e a gravação deixaria de repetir a mesma ação.
- **D-SP-11, a regra do alvo gravado.**
  - A espec (2.2 e E1-2) dizia: o candidato do mesmo tipo mais perto, e senão o ponto gravado.
  - A implementação usa o **alvo resolvido**: o candidato idêntico ao gravado (o mesmo tipo, id e ponto), e senão o ponto gravado.
  - O motivo: "o do mesmo tipo mais perto" poderia escolher um `seguir` ou uma bola em outro lugar, o que é ler onde estão agora. A regra
    implementada só vai aonde P foi.

### 9.5 Os arquivos

| arquivo | o que muda |
|---|---|
| `experiments/bancada/parceiro.py` | o `Evitador` corrigido (9.2); o `Passivo` já existe |
| `experiments/conferir_controles_social_par_e1.py` | os pares C1, C2 e o seguidor × seguidor descritivo, com a saída nova em `artifacts_v3_social_par_e1/controles_positivos_ad1.json`; o arquivo da primeira conferência fica |
| `tests/test_social_par_e1.py` | o G-CONTROLE-POS e o G-MET-NULO, só se o 9.3 sair |
| `docs/registro/2026-11.md` | o resultado do adendo |

### 9.6 As decisões do adendo (PROPOSTAS; cada uma com a recomendação e o custo de errar)

| id | a decisão | a recomendação | o custo de errar |
|---|---|---|---|
| **A1-1** | o C1, passivo × seguidor | **entra**, como o controle de resposta conhecida por construção | sem ele, não há nenhum caso em que se saiba de antemão que a resposta do parceiro muda o que F vive |
| **A1-2** | o evitador | **refeito:** um passo inteiro na direção oposta ao outro, com a direção 0 no empate | o de antes não foge de perto; um passo maior que o alcance não muda nada, porque o motor anda no máximo o alcance |
| **A1-3** | o seguidor × seguidor | **sai dos controles positivos e fica descritivo** | mantê-lo como gate pede um resultado que a velocidade do mundo não deixa sair; mudar a velocidade mudaria o mundo do jogo |
| **A1-4** | o limiar do G-MET-NULO | **\|c\| ≤ 0,2, ou None** | mais apertado, um P parado com poucos casos reprova por ruído; mais frouxo, o nulo deixa de dizer alguma coisa |
| **A1-5** | o D-SP-10 | **aceitar a porta no motor**, só com a chave de pesquisa | voltar à troca por explorar faz a gravação mudar a ação que F vê, o que é uma diferença entre VIVO e GRAV que não vem da resposta de P |
| **A1-6** | o D-SP-11 | **aceitar o alvo resolvido** | a regra da espec deixava P seguir um alvo vivo, e a GRAV voltaria a responder a F |

## 10. Adendo 2: controles só de regra (2026-11-17, PROPOSTO)

**Status: APROVADO pelo Matheus em 2026-11-17 ("Aprovo todas"): as A2-1 a A2-5 (10.5), pela recomendação (D-SP-20).** As seções 1 a 9 e as duas conferências não
mudam: `controles_positivos.json` (`7a1049ac…`, D-SP-13) e `controles_positivos_ad1.json` (`e1fe96b6…`, D-SP-18) ficam como saíram.

**De onde vem:** o Matheus, em 2026-11-17, "Controles só de regra", depois de os controles do adendo 1 passarem só na maioria das sementes
(o C1 em 4 de 5, o C2 em 3 de 5). Nas que falharam, o parceiro estava comendo, brincando, dormindo ou chamando o dono no t0: o instinto
do mundo, que os controles usavam, põe as necessidades do corpo na frente da regra social.

**A regra desta tentativa:** é a terceira. Se ela falhar em qualquer semente, **a E1 fecha com a ressalva** (a opção "fechar com a
ressalva" de 2026-11-17), sem um quarto desenho.

### 10.1 Os controles

Três políticas de regra pura, só em `experiments/bancada/parceiro.py`. Nenhuma come, dorme ou chama: o corpo continua rodando, mas a
decisão não o lê. O sono só vem da ação `dormir` (`digilab/policy.py:177-179`), então elas nunca dormem.

| política | regra |
|---|---|
| **Estátua** | sempre `ocioso`: nunca se move |
| **Seguidor puro** | vê o outro → `explorar` com o alvo `seguir`; não vê → `ocioso` |
| **Evitador puro** | vê o outro → `explorar` até o ponto a um passo inteiro na direção oposta (o evitador do adendo 1, 9.2); não vê → `ocioso` |

**O pet focal F é sempre a estátua.** Como ele nunca se move, toda mudança de distância depois do t0 é obra do parceiro P, e a resposta de
P é a única coisa que pode separar a VIVO da GRAV.

| controle | F × P | o d0 | o que acontece por construção |
|---|---|---|---|
| **C1** | estátua × seguidor puro | 5 células (dentro da visão de 6) | VIVO: P vê F e vai até ele em 2 decisões (5 / 3,75). GRAV: na vida gravada, P parou ao lado de F antes do t0, e a gravação o mantém lá: não vai até F |
| **C2** | estátua × evitador puro | 1 célula (o contato) | VIVO: P vê F encostado e foge. GRAV: na vida gravada, P fugiu de F no começo e parou fora da visão; a gravação o mantém parado, e F, posto ao lado dele, fica em contato |

### 10.2 A janela e o t0

- **A janela:** as **8 decisões** depois do t0 (PROPOSTO, SEM FONTE). É curta para o resultado não depender do que vem depois, e longa o
  bastante para o seguidor puro chegar (2 decisões) com folga.
- **O t0:** o do fluxo `intervencao-social`, no dia 1, como antes. A estátua nunca dorme, então o `levar_pet` sempre vale no t0 pedido.

### 10.3 O que tem de sair (escrito antes de rodar), em todas as 5 sementes (101 a 505)

| controle | tem de sair | a medida, nas 8 decisões depois do t0 |
|---|---|---|
| **C1** | VIVO chega (não censurado) e GRAV não chega (censurado); e a fração de contato maior na VIVO | `tempo_ate_raio` (raio 1 célula, janela 8) e `fracao_em_raio` |
| **C2** | a fração de contato menor na VIVO que na GRAV | `fracao_em_raio`, raio 1 célula, nas 8 decisões |

- O G-MET-NULO já passou no adendo 1 (D-SP-18) e não se repete: com F parado, a contingência de P a partir de F não tem caso.
- **Se passar:** o G-CONTROLE-POS entra no `tests/test_social_par_e1.py` com os C1 e C2 deste adendo, e a E1 vai para o PR.
- **Se falhar em qualquer semente:** a E1 vai para o PR fechada com a ressalva. A seção de limitações diz que o instrumento separou a
  VIVO da GRAV só na maioria dos casos de regra, com os três arquivos de conferência, e o plano do A0 tem de levar isso em conta.

### 10.4 Os arquivos

| arquivo | o que muda |
|---|---|
| `experiments/bancada/parceiro.py` | a `Estatua`, o `SeguidorPuro` e o `EvitadorPuro` |
| `experiments/conferir_controles_social_par_e1.py` | a conferência do adendo 2, com a saída em `artifacts_v3_social_par_e1/controles_positivos_ad2.json`; a do adendo 1 fica no histórico do git |
| `tests/test_social_par_e1.py` | o G-CONTROLE-POS, só se o 10.3 sair |
| `docs/registro/2026-11.md` | o resultado |

### 10.5 As decisões do adendo 2 (PROPOSTAS; cada uma com a recomendação e o custo de errar)

| id | a decisão | a recomendação | o custo de errar |
|---|---|---|---|
| **A2-1** | os controles | **só de regra:** a estátua, o seguidor puro e o evitador puro, sem comer, dormir nem chamar | com o instinto embaixo, a semente passa ou falha pelo estado do corpo (D-SP-18) |
| **A2-2** | o pet focal | **sempre a estátua** | um F que se move mistura a resposta de P com a de F, e a resposta conhecida deixa de ser por construção |
| **A2-3** | o d0 | **5 células no C1 e 1 no C2** | o C2 com 5 células mediria a fuga de longe, que pode não acontecer se P já estiver fora da visão |
| **A2-4** | a janela | **8 decisões depois do t0** | a janela de um dia (96) deixa o resultado depender do que vem depois, que é o que derrubou o adendo 1 |
| **A2-5** | se falhar | **fechar a E1 com a ressalva**, sem um quarto desenho | um quarto desenho depois de três falhas vira ajustar até dar certo |
