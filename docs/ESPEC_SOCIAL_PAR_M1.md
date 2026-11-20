# ESPEC — SOCIAL_PAR M1: o outro na decisão do modular

- **Status:** PROPOSTA, para o checkpoint S5. Nenhum código entra antes do "aprovado" do Matheus.
- **Data:** 2026-11-19.
- **Fontes:**
  - a síntese da S (`docs/SINTESE_SOCIAL_PAR_S.md`);
  - o mapa dos mecanismos (`docs/INVESTIGACAO_V3_SOCIAL_PAR.md`, seção 5, a linha M1);
  - o código lido em 2026-11-19, no `v3-social-par-s3`.

## 0. O que é o M1, e o nome

**O pedido da S chama o M1 de "percepção do outro".** No código, a percepção física do outro **já existe** e não muda:
- **a `PercepcaoSocial`** (`digilab/mundo.py`, `perceber_social`) traz três coisas, todas físicas, sem estado interno do outro
  (G-RECEPTOR-SOCIAL):
  - os outros à vista: o id, a posição relativa, a distância e a ação visível;
  - onde este pet viu cada outro comer;
  - o último toque.
- **o motor já oferece, no explorar,** um candidato `seguir` por outro à vista e um `onde_comeu` por outro visto comendo
  (`MotorMundo._candidatos_sociais`). O padrão do motor nunca os escolhe; só um cérebro.

**O que falta é o outro chegar à decisão do modular.**
- O `M-SENS` (`digilab/digibrain/sens.py`) só leva a percepção social ao estado com a CO7 ligada, e só para os deveres.
- O `impulso.alvos` (`digilab/digibrain/impulso.py`) não gera nenhuma unidade com o outro como alvo.

O M1 é, então, **a percepção do outro dentro do cérebro** (o M-SENS lê o outro) **mais as unidades de decisão com ele como alvo**. É o M1
da investigação, e esta espec usa essa definição. A escolha do nome está na seção 9, M1-1.

## 1. Por que agora

- **A S3 mostrou que o instrumento vê o social e que o pet de hoje não responde.** O seguidor de regra muda o tempo até o contato em 16 a
  70 decisões, e o pet de hoje não sai de ±1,9 (`docs/RESULTADO_V3_SOCIAL_PAR_S.md`).
- **A razão no código:** o modular não tem nenhuma ação dirigida ao outro. O M1 é o primeiro dos dois pontos em que o caminho quebra,
  percepção → intenção → ação → consequência no corpo. O segundo, a consequência no corpo, é o M2.

## 2. A chave

- **`ConfigDigibrain.unidades_sociais: bool = False`**, em `digilab/config.py`. É PROPOSTO, SEM FONTE como valor.
  - Desligada, toda vida de hoje sai byte a byte, a do pet sozinho e a do grupo (o G2).
  - Ligada sem nenhum outro à vista e sem nenhum `onde_comeu`, a vida também sai byte a byte (o G2b): as unidades novas só existem com o
    outro.
- **As combinações:** ela não se combina com a `fala_unidades`, a `olhar` nem a `passeio`. Isso é PROPOSTO, porque essas combinações não
  têm teste. A regra segue o padrão do `__post_init__` da `ConfigDigibrain`, com `raise ValueError`.
- **Fora do jogo nesta etapa:** o `GrupoDoJogo` (`web/app/motor/grupo_jogo.ts`) não liga a chave. Levar ao ovo novo é decisão de produto
  (seção 9, M1-4).

## 3. As interfaces

### 3.1 As constantes (`digilab/config.py`)

```python
TIPOS_ALVO_SOCIAIS = ("seguir", "onde_comeu")      # = mundo.CANDIDATOS_SOCIAIS; os tipos das unidades do M1, so com a chave
```

- **O `TIPOS_ALVO_DIGIBRAIN` não muda.** O M-MEM itera sobre ele (`digilab/digibrain/mem.py:113`, `"vista"`), e acrescentar tipos mudaria o
  episódio das vidas de hoje.
- **O `W0_tipo` aceita os dois tipos novos só na linha do `explorar`.** O padrão não tem nenhuma entrada para eles, então o peso inato
  deles é 0 (seção 9, M1-2).
- Um teste confere que `TIPOS_ALVO_SOCIAIS == mundo.CANDIDATOS_SOCIAIS`.

### 3.2 O M-SENS (`digilab/digibrain/sens.py`)

**Com a chave,** o `sens` ganha dois campos. Eles são lidos só da `obs.social` (a `PercepcaoSocial`):

```python
out["outros"] = [  # um por outro a vista, na ordem da percepcao (d, depois id)
    {"id": ident, "x": pm.x + dx, "y": pm.y + dy, "d": d, "prox": self.proximidade(d), "acao": acao_visivel}
    for ident, dx, dy, d, acao_visivel in ps.outros]
out["onde_comeu"] = [  # um por outro visto comendo, na ordem de id
    {"id": ident, "x": x, "y": y, "d": raiz_inteira((x - pm.x) ** 2 + (y - pm.y) ** 2), "prox": self.proximidade(d), "idade": idade}
    for ident, x, y, idade in ps.onde_comeu]
```

- **A conta:** o `self.proximidade(d)` é a mesma conta do `prox` dos objetos no M-SENS hoje (`sens.py`, `proximidade`), sem
  número novo.
- **A unidade do `d`:** a etapa de código confere que o `d` da `PercepcaoSocial` está na mesma unidade do `d` dos objetos. Se não
  estiver, converte antes da conta. Um teste confere que um outro e um objeto na mesma posição dão o mesmo `prox`.
- **Sem a percepção social** (o pet sozinho: `obs.social` é None), os dois campos são listas vazias.
- **Sem a chave,** nenhum campo novo entra.
- **O G-RECEPTOR-SOCIAL:** um teste pela AST confere que o código novo só lê `outros` e `onde_comeu` da `PercepcaoSocial`. Ele não lê a
  `reputacao`, o `peso_dever`, os `sentidos` nem nada do motor do outro.

### 3.3 As unidades (`impulso.alvos` e `impulso.unidades`)

**Com a chave,** depois das unidades de hoje do `explorar` (vagar ou passeio, cheiro e lugar lembrado, nessa ordem), entram:

```python
for o in sens["outros"]:
    out.append({"chave": chave_unidade("explorar", "seguir", o["id"]), "acao": "explorar", "tipo": "seguir", "objeto": o, "d": o["d"]})
for o in sens["onde_comeu"]:
    out.append({"chave": chave_unidade("explorar", "onde_comeu", o["id"]), "acao": "explorar", "tipo": "onde_comeu", "objeto": o,
                "d": o["d"]})
```

- **A posição:** as unidades novas ficam no fim do bloco do `explorar`. Assim, as unidades de hoje mantêm a ordem e o índice, e a ordem
  dos sorteios não muda quando não há ninguém à vista.
- **Os termos da unidade** (`impulso.unidades`), sem termo novo:
  - **inato:** `inato_b["explorar"] + W0_tipo["explorar"].get(tipo, 0)`, como hoje (0 pelo padrão, seção 9, M1-2);
  - **prox:** `mul(w0_prox["explorar"], o["prox"])`, pelo ramo `elif o is not None` de hoje;
  - **nov:** `mul(w0_nov["explorar"], o.get("nov", 0))`. O `nov` do outro é 0 no M1 (seção 9, M1-3);
  - **incentivo:** com a chave, o ramo `if b in ("comer", "brincar")` passa a valer também para os dois tipos sociais. O valor é
    `plast.incentivo(sens["pc"], tipo, drives)` vezes o `prox`. É o único lugar em que o valor aprendido entra;
  - **hábito e persistência:** os de hoje, pela `linha_da_opcao` (a linha do `explorar`) e pela chave da unidade.

### 3.4 O aprendizado (`digilab/digibrain/plast.py`)

- **O P1 ganha as duas classes:** com a chave, `CLASSES_DESFECHO + TIPOS_ALVO_SOCIAIS`. O desfecho de uma decisão `explorar/seguir` ou
  `explorar/onde_comeu` vai ao `consequencia_p1` com a classe igual ao tipo, como o `comer` vai com a classe da comida.
  - Sem a chave, as classes são as de hoje.
  - A partida das classes novas é 0, como as de hoje.
- **O P2 (o hábito):** não muda. A linha é a do `explorar`.
- **O que o P1 aprende sem o M2:** só o que muda no corpo depois de seguir ou de ir aonde o outro comeu.
  - **No `seguir`, o previsto é ~0,** porque estar perto do outro não muda nenhum receptor hoje. É o argumento do M2.
  - **No `onde_comeu`, o previsto é o valor da comida que costuma haver lá,** pelo mesmo canal da comida de hoje. É o "aprender
    observando" da DP-5.

### 3.5 A escolha do alvo (`digilab/digibrain/adapt.py`)

**O `Alvo` do motor não muda.** O `seguir` e o `onde_comeu` têm `id = None`, e o id do outro fica no `_cands_sociais` do motor. Mudar
isso mexeria no registro do grupo de hoje.

Com a chave, a intenção de uma unidade social guarda o tipo e o ponto `(o["x"], o["y"])`. O `escolher_alvo` acha o candidato por tipo e
posição:

```python
if it.tipo_alvo in TIPOS_ALVO_SOCIAIS:
    alvo = next((c for c in candidatos if c.tipo == it.tipo_alvo and (c.x, c.y) == it.ponto), None)
    if alvo is None:
        raise ValueError(f"o alvo social ({it.tipo_alvo}, {it.ponto}) nao esta entre os candidatos do motor: ...")
```

- **Por que a posição bate exatamente:** o motor monta o `seguir` com `p.x + dx` e o `onde_comeu` com o `(x, y)` da percepção. O M-SENS usa
  os mesmos números, da mesma `PercepcaoSocial` da mesma decisão.
- **Dois outros na mesma célula:** dariam dois candidatos com tipo e posição iguais. O `next` pega o primeiro, que é o mesmo `Alvo`
  (frozen, iguais por valor), e o motor resolve o id pelo `_cands_sociais`. Um teste cobre esse caso.
- **O `continuar` de uma intenção social:** é o de hoje (o motor mantém o ponto antigo). O M1 não o muda.

### 3.6 O que não muda

- **O motor:** o `engine.py`, o `mundo.py` e o `grupo.py`. Os candidatos já existem.
- **O registro do grupo, o replay e os saves:** a decisão é do cérebro, e o replay refaz a vida a partir do log.
- **O cérebro A, a CO6 e a CO7.**

## 4. O pseudocódigo da decisão, com a chave

```
sens    = M-SENS(obs)                          # + outros, onde_comeu (3.2)
lista   = alvos(sens, memoria, passeio)        # + explorar/seguir:<id>, explorar/onde_comeu:<id> no fim do explorar (3.3)
termos  = para cada unidade u da lista: inato + prox + nov + incentivo(P1, tipo) + habito + persistencia (3.3)
u*      = arbitragem de hoje (softmax pela rng da politica)
intencao= (acao de u*, tipo de u*, ponto de u*)
alvo    = escolher_alvo: o candidato do motor com o mesmo tipo e ponto (3.5)
...o mundo anda...
P1      = consequencia_p1(acao, classe = tipo de u*, leitura antes, leitura depois)   # aprende o desfecho de seguir / onde_comeu (3.4)
```

## 5. Os testes (`tests/test_digibrain_m1_social.py`)

| teste | o que confere |
|---|---|
| **G2, a chave desligada** | as vidas de hoje, do pet sozinho e do grupo, saem byte a byte contra o gabarito gravado num commit próprio, antes do código. Vale para o modular de hoje e para a v-grupo do jogo |
| **G2b, ligada sem o outro** | o pet sozinho com a chave ligada sai byte a byte igual ao desligado; o grupo com a chave ligada também, até a primeira decisão com outro à vista ou com `onde_comeu` |
| **as unidades** | com outro à vista, há exatamente uma `explorar/seguir:<id>` por outro, no fim do `explorar` e na ordem da percepção; com `onde_comeu`, uma por id; sem o outro, nenhuma |
| **o alvo** | uma intenção `seguir` resolve para o candidato do motor na posição do outro, e o motor registra o id certo pelo `_cands_sociais`; um ponto que não está entre os candidatos levanta erro |
| **dois na mesma célula** | o caso da seção 3.5 não levanta erro e é determinístico |
| **o P1** | depois de N decisões `onde_comeu` que levam a comer, o incentivo da classe `onde_comeu` sai do 0; o `seguir` sem consequência no corpo continua em 0, porque nenhum receptor muda |
| **o prox** | um outro e um objeto na mesma posição relativa dão o mesmo `d` e o mesmo `prox` no M-SENS (3.2) |
| **G-RECEPTOR-SOCIAL** | pela AST, o código novo do M-SENS só lê `outros` e `onde_comeu` da `PercepcaoSocial` |
| **as combinações** | a `unidades_sociais` com a `fala_unidades`, a `olhar` ou a `passeio` levanta `ValueError` |
| **o determinismo** | a mesma semente dá o mesmo registro, com a chave ligada |
| **a escolha só com o outro à vista** | numa vida de grupo com a chave, toda decisão `explorar/seguir` acontece com o outro no `sens["outros"]` |

**O G-PAR (o espelho no TS)** só entra se o M1 for ao jogo (seção 9, M1-4). Nesse caso, ele pega o `impulso.ts`, o `sens.ts`, o
`adapt.ts`, o `plast.ts` e o `constantes.ts`, além do gabarito pelo `experiments/exportar_gabarito_digibrain_modular.py`. Como em toda peça
do modular, a paridade prova só que as duas implementações concordam, e não que o mecanismo funciona.

## 6. Os critérios de aceitação

1. O gabarito das vidas de hoje está gravado num commit antes do código, e o G2 e o G2b passam.
2. Todos os testes da seção 5 passam, e a suíte inteira roda, com a contagem e as falhas conhecidas no corpo do PR.
3. O `engine.py`, o `mundo.py` e o `grupo.py` não mudam (o diff).
4. Os números novos (o `W0_tipo` 0 das classes sociais e o `nov` 0) estão em `digilab/config.py` com status e fonte.
5. Nenhuma vida de pesquisa roda na etapa de código. A medida do M1 tem um plano próprio (seção 7).

## 7. Como o M1 usa o substrato da S

- **O instrumento da S fica pronto para medir o M1 sem mudança:**
  - os três braços (C, B1 e B2), o VIVO, a GRAV e a OUTRA;
  - o G-DET em cada braço;
  - o primário T\*c e as medidas de riqueza.
- **A medida é a mesma da S3,** com os pets do M1 no lugar dos pets de hoje. Só muda a config do cérebro, e o resto vem da S3:
  - o mesmo `run_v3_social_par_s.py`, num plano novo;
  - a mesma margem;
  - o G-DET como controle;
  - o S3 como a linha de base, já rodada.
- **O braço que importa é o B1:** com os dois fora da casa, há menos comida perto, e o `onde_comeu` tem com o que render.
- **O previsto, PROPOSTO, para o plano novo:**
  - o D_A do M1 sozinho fica ≈ 0 no C e no B2, porque o `seguir` não vale nada sem o M2;
  - no B1, o D_A pode sair de ≈ 0 pelo `onde_comeu`;
  - essa run não decide nada antes de ter plano.
- **O que essa medida não pode dizer:** se o pet "gosta" do outro. Isso pede o M2, a companhia no corpo.

## 8. O que fica fora

- **O M2** (a companhia no corpo), **o M3** (a memória por parceiro) e **o M4** (o som e os sentidos longos).
- **A CO7, a CO6** e qualquer peso de dever.
- **O jogo web**, até a decisão M1-4.
- **Qualquer mudança no motor** ou no registro do grupo.

## 9. As decisões para o Matheus (checkpoint S5)

| id | o que decidir | recomendação | custo de errar |
|---|---|---|---|
| **M1-1** | o que o M1 é | **a percepção do outro dentro do cérebro mais as unidades com ele como alvo** (o M1 da investigação). A percepção física já existe | chamar de M1 só a percepção no M-SENS daria uma etapa que não muda nenhuma decisão, e a medida daria ≈ 0 por construção |
| **M1-2** | o peso inato das unidades sociais | **0**: o pet não nasce querendo seguir, e o valor vem do P1 | um inato > 0 mede o projetista, não o pet. É o mesmo motivo da SP-5 |
| **M1-3** | a novidade do outro | **0 no M1** | uma novidade do outro pede uma memória do outro, que é o M3 |
| **M1-4** | o M1 no jogo | **só no Python primeiro;** o TS e o ovo novo só depois da medida | levar ao jogo antes da medida põe no ovo um comportamento sem evidência e custa o G-PAR duas vezes, se a medida mudar o desenho |
| **M1-5** | a ordem com o M2 | **o código do M1, depois o do M2, e um plano com os dois braços** (M1 e M1+M2) sobre o substrato da S | medir o M1 sozinho antes do M2 dá, pelo previsto, um ≈ 0 caro no `seguir`; o M2 antes do M1 não tem ação que aproveite a companhia |
