"""O mundo fisico minimo (V2; docs/TAREFA_V2_MUNDO_FISICO.md, etapa 2; MF-1 a MF-4 decididas em 2026-10-07).

Estende o MotorFrutas (digilab/frutas.py, que nao muda) por subclasse, como as frutas (N4) e a bola (A1) entraram; engine.py e
ambiente.py tambem nao mudam. Desligado (ConfigMundo.ligada False, o padrao): nenhuma rng nova, nenhum registro novo, nenhuma chave
nova em estado(), nem o embrulho da politica: o MotorFrutas byte a byte. Ligado, o mundo SUBSTITUI o cenario do N4 e da A1: frutas,
racao e bola sao objetos com posicao (ConfigFrutas.ligada e ConfigBola.ligada junto com o mundo levantam erro), e os gestos de hoje
(`alimentar`, `oferecer_fruta_<f>`, `por_bola`, `tirar_bola`) levantam erro: o gesto e o `deixar_*`.

O mapa (secao 3): 64 x 30 celulas de 16 subunidades; posicoes inteiras em subunidades (0 <= x < 1024, 0 <= y < 480), distancia
`isqrt(dx^2 + dy^2)`. Regioes por faixa de x (casa, jardim, campo, mata; ConfigMundo.layout); o pet nasce no ninho. Direcoes por uma
tabela inteira de 16 (DIR16, escala 1024; indice 0 = leste, crescendo no sentido anti-horario, com o norte em y menor).

O dono (secao 4): `deixar_comida(tipo, x, y)` (racao ou fruta) conta como contato, como o `alimentar` de hoje (zera o tempo sem
cuidado, soma um cuidado, gasta orcamento; o embrulho e o vinculo recebem `alimentar`); a fome so sobe quando o pet come.
`deixar_bola(x, y)` segue o `por_bola`: gasta orcamento e nao e contato. Os dois sao tipos novos do log (events.deixar_comida,
events.deixar_bola); so o `reproduzir_mundo` os entende. `DonoComLugar` troca o `alimentar` do dono sintetico pelo `deixar_comida`
no lugar do estilo (comedouro, perto, longe), com a rng propria `dono-lugar` (sem o braco: numeros comuns). `CanalMundo` impoe o
orcamento com os gestos; `simular_vida_mundo` e o `simular_vida` com ele.

O pet (secao 5): o cerebro escolhe a acao; nas decisoes de explorar, comer e brincar o motor monta os candidatos a alvo, sorteia um
`u` em [0, 2^16) da rng `alvo` (sempre nessas tres acoes: numeros comuns) e pergunta ao gancho opcional `escolher_alvo(acao,
candidatos, percepcao, u)` (None = o padrao do motor). O motor anda de uma vez, na decisao: alcance = velocidade x intervalo; energia
- custo x deslocamento, alem do efeito de sempre da acao. Ao chegar (raio de pegar 1 celula): comer come a comida do alvo; explorar
come a comida boa mais proxima no raio, com a fome abaixo de `fome_max_comer_achado` (MF-1); brincar com a bola sobe o humor e a bola
rola. Comer sem comida no alcance nao da fome: o mundo desfaz o +0,05 do `efeito_da_acao_do_pet` antes de qualquer cerebro observar
(MF-2). O alvo que ficou sem chegar vira o candidato `continuar` se a proxima decisao for a mesma acao.

O mundo (secao 6, MF-4): as arvores (quedas, recarga, ate 4 frutas no chao por arvore), a comida que amadurece, apodrece e some, e a
bola que rola, cada sorteio num fluxo proprio por `derivar_semente` (`mundo-arvores`, `mundo-bola`, `mundo-sujeira`), nunca na
`_rng_ambiente` do engine nem na rng do pet. As quedas nao dependem do pet: P0 e P1 da mesma semente veem as mesmas (G-NUMS).

O mundo como componente (docs/TAREFA_V2_DOIS_PETS.md, etapa 1; docs/futuro/dois_pets.md, secao 2): a classe `Mundo` guarda o que e do
mundo (arvores, comidas, bola, os fluxos `mundo-arvores` e `mundo-bola`, as quedas, as comidas que sumiram, as bolas deixadas e as
rolagens) e nao sabe de pet. O `MotorMundo` ligado e dono do proprio `Mundo`, com a semente do pet, e guarda o que e do pet (posicao,
alvo pendente, os fluxos `alvo` e `mundo-sujeira`, consumos, decisoes, regioes, visitas, comidas deixadas). A atualizacao do mundo e
idempotente por tick. Com um pet, a vida e a de antes byte a byte (G2); dois motores sobre o mesmo `Mundo` sao a etapa 2 (o `Grupo`).

A percepcao (secao 7, MF-3): `Observacao.mundo` = `PercepcaoMundo` (posicao, regiao, os objetos vistos a ate 6 celulas, o cheiro e a
direcao dele, o alvo pendente). A consequencia (secao 8): depois de andar, comer e brincar, o gancho opcional `consequencia_mundo(acao,
ocorrido, obs_depois)`, uma vez por decisao de explorar, comer ou brincar; o `fruta_comida` da E2 quando o pet come uma fruta; e o
cerebro observa a transicao com a observacao seguinte ja com tudo aplicado.

O que o motor registra para as medidas do plano (adendo 1, A1.8; as medidas sao do D): a posicao e a regiao a cada decisao
(`decisoes_mundo`), as trocas de regiao (`regioes`), as visitas as manchas das arvores com chegada e saida (`visitas`), as quedas
(`quedas`, do fluxo que nao depende do pet), os consumos (`consumos_mundo`), as comidas deixadas e as que sumiram.

O banheiro (docs/TAREFA_V2_BANHEIRO.md, secoes 2 a 5, etapa 3; BN-1 a BN-6 decididas em 2026-10-07): `cfg_banheiro` (ConfigBanheiro)
liga, e exige o corpo com a sub-chave `banheiro` na frente (com_corpo(MotorMundo), digilab/motor_corpo.py: a vontade e o conforto sao do
corpo). Desligado, nada muda (nenhuma rng, nenhum registro, nenhuma chave em estado()). Ligado:
- o banheiro e um retangulo de celulas da casa (`ConfigBanheiro.celulas_x`, `celulas_y`), sem parede;
- `aliviar` (AcaoPet.ALIVIAR) e uma acao com alvo: o motor sorteia o u da rng `alvo` e oferece dois candidatos, `banheiro` (o ponto do
  banheiro mais perto do pet) e `aqui` (onde o pet esta); sem o gancho do cerebro, `aqui`. O pet anda ate o alvo, com o custo de energia
  da distancia. Com `aqui`, alivia onde esta. Com `banheiro`, alivia ao chegar; o banheiro alem do alcance de uma decisao NAO e mais
  alivio no caminho (a continuacao, decisao do Matheus de 2026-10-11): o pet segura a vontade e o alvo fica pendente, como o `continuar`,
  ate chegar, ate o cerebro trocar de acao ou de alvo, ou ate a urgencia (registro `idas_banheiro`). Com a vontade acima de
  `limiar_urgente` (a regra urgente do instinto), o alvo tem de ser `aqui` (falha alto);
- a necessidade e um objeto do `Mundo` (fora da percepcao `vistos`: o pet a sente pelo corpo), deixada onde o pet aliviou. O limpador
  (`ConfigBanheiro.limpador`) a recolhe na hora quando o alivio termina dentro do banheiro; fora dele, nada. O corpo recebe o
  `estimulo_aliviar` (a vontade a zero) e, quando a necessidade fica no chao, o `estimulo_necessidade` (o cheiro imediato);
- a zona da necessidade e o banheiro (dentro do retangulo) ou a regiao de sempre (fora dele): a cada tick o corpo recebe quantas
  necessidades estao na zona do pet (`passo(..., necessidades=n)`). O `limpar` do dono recolhe as da zona do pet;
- o registro `alivios` (um dict por aliviar: tick do mundo, dentro, urgente, alvo, distancia ao banheiro na decisao, recolhido; o contrato
  da bancada, experiments/bancada_v2.py) e as `recolhas` do limpar. O `DonoCarinhoBanheiro` acaricia no primeiro passo do dono depois
  de cada alivio dentro do banheiro, fora do orcamento (`simular_vida_mundo(..., carinho=)`).

O pet que pensa (J5; docs/TAREFA_V2_PET_QUE_PENSA.md, secao 2.3, etapa 3; PP-1 e PP-5 do plano): `cfg_pqp` (ConfigPetQuePensaMundo)
liga, so com o mundo e so com um pet (fora do grupo). Desligado, nada muda. Ligado:
- os troncos que o pet ja viu: um tronco a ate o raio da visao do pet, na percepcao da decisao ou na posicao depois de andar, entra em
  `troncos_vistos` (id -> o primeiro tick do mundo); a percepcao ganha `troncos` (os troncos a vista agora: id, dx, dy, d);
- no explorar, depois dos candidatos de hoje, um candidato `arvore:<id>` por tronco ja visto, no pe da arvore, na ordem do layout (PP-1).
  O padrao do motor e o instinto nunca os escolhem; o `continuar` de uma ida a arvore leva ao mesmo ponto;
- a fruta na mao (`dar_fruta_<f>`, fora do orcamento): o pet a come na hora, onde esta, com o efeito vigente, sem decisao e sem andar
  (acordado; dormindo falha alto). Entra em `consumos_mundo` com `como` = "mao" e chega ao cerebro so pelo gancho opcional
  `fruta_na_mao(tipo, obs_antes, obs_depois)`: nao passa pelo `receber_acao_dono`, pelo `fruta_comida`, pelo `consequencia_mundo` nem
  pelo `mudanca_no_corpo` (a G-SEM-CREDITO). Nao e contato;
- a troca de tipo (`trocar_arvores_<x>_<y>`, fora do orcamento): no tick do evento as arvores do tipo x passam a dar y, e as do y a dar
  x. As quedas ate o tick do evento usam o tipo antigo e as frutas que ja estao no chao ficam como cairam. O registro e do `Mundo`
  (`trocas_tipo`), e o replay o refaz pelo log.

O Paladar, o lado do mundo (docs/futuro/paladar.md, secao 3.1, etapa 1): `cfg_paladar` (ConfigPaladar) liga, so com o mundo. Desligado,
nada muda. Ligado, cada consumo leva o perfil de gosto do tipo comido (um dict {qualidade: inteiro em [0, C]}, uma copia do da config):
o registro do consumo (`consumos_mundo`, e com ele o `ocorrido["comeu"]` do `comer` e do "achou e comeu") ganha `perfil`, o dict na comida
madura e None na podre; a fruta na mao (sempre madura) tambem. O mundo nao usa o perfil para nada: nao muda a nutricao, o humor, o cheiro,
a percepcao, os candidatos nem nenhuma rng. O corpo (o orgao do Paladar, do B) o le daqui.

A fruta ao lado da racao (o RP-2 de docs/futuro/paladar.md; `cfg_fruta_ao_lado`, ConfigFrutaAoLado): so com o mundo e um pet. Desligada,
nada muda. Ligada, o motor aceita o evento `deixar_fruta(tipo, x, y)` (events.deixar_fruta; o replay o refaz), so logo depois de uma racao
deixada pelo dono no mesmo tick (a racao de referencia); a fruta nasce madura com a origem `dono_ao_lado` (ORIGEM_AO_LADO), entra em
`frutas_ao_lado` (tick, id, tipo, x, y, racao) e no resumo do mundo fisico, e o estado() ganha `fruta_ao_lado` (as maduras ao lado no
chao, por tipo). E fora do orcamento e sem contato (o canal nao a ve; o deixar_bola e o modelo). Quem poe e o `DonoFrutaAoLado`, pelo
`simular_vida_mundo(..., ao_lado=)`.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from typing import Callable

from .ambiente import PoliticaInstintoBola
from .config import CONFIG_BOLA, CONFIG_DONOS, CONFIG_MUNDO, CONFIG_MUNDO_LIGADA, CONFIG_PADRAO, TICKS_POR_DIA, Config, ConfigMundo
from .config import CONFIG_BANHEIRO, CONFIG_PQP_MUNDO, ConfigBanheiro, ConfigDonos, ConfigPetQuePensaMundo
from .config import CONFIG_PALADAR, ConfigPaladar
from .config import CONFIG_FRUTA_AO_LADO, ConfigFrutaAoLado
from .config import ConfigOlfato, ConfigOuvido, ConfigSentidos
from .corpo import leitura_orgao
from .donos import Visao
from .engine import Motor
from .events import ACOES_PARAR_ARVORES, tipo_parado
from .events import (ACOES_BOLA, ACOES_FRUTAS, ACOES_MAO, ACOES_TROCA_ARVORES, FRUTAS, TIPOS_COMIDA_MUNDO, AcaoPet, AcaoUsuario,
                     LogDeEventos, fruta_dada, ler_deixar_bola, ler_deixar_comida, par_da_troca)
from .events import deixar_bola as evento_deixar_bola
from .events import deixar_fruta as evento_deixar_fruta
from .events import ler_deixar_fruta
from .events import deixar_comida as evento_deixar_comida
from .frutas import MotorFrutas
from .policy import Observacao, Transicao
from .protocol import derivar_semente
from .temperamento import NEUTRO, Temperamento
from .treino import CanalDeInteracao, OrcamentoExcedido, OrcamentoNaoConsumido, Vida

ESCALA_DIR = 1024
# as 16 direcoes em inteiros: (arred(1024 cos a), -arred(1024 sen a)), a = i x 22,5 graus; y cresce para o sul
DIR16 = ((1024, 0), (946, -392), (724, -724), (392, -946), (0, -1024), (-392, -946), (-724, -724), (-946, -392),
         (-1024, 0), (-946, 392), (-724, 724), (-392, 946), (0, 1024), (392, 946), (724, 724), (946, 392))
# as 8 do cheiro (secao 7): 1 a 8 = L, NE, N, NO, O, SO, S, SE (os indices pares do DIR16)
DIRECOES_CHEIRO = ("L", "NE", "N", "NO", "O", "SO", "S", "SE")
ACOES_COM_ALVO = (AcaoPet.EXPLORAR, AcaoPet.COMER, AcaoPet.BRINCAR)
ID_BOLA = 0
GESTOS_PROIBIDOS = (AcaoUsuario.ALIMENTAR,) + ACOES_BOLA + ACOES_FRUTAS


class MundoSemChave(RuntimeError):
    """Gesto do mundo (`deixar_*`) num motor com ConfigMundo.ligada = False."""


class BanheiroSemMundo(ValueError):
    """O banheiro (ConfigBanheiro ligada) sem o mundo fisico ligado, ou sem o corpo com a sub-chave banheiro na frente."""


class PetQuePensaSemChave(ValueError):
    """a fruta na mao, a troca de tipo ou a ConfigPetQuePensaMundo sem o mundo, sem a chave ou no grupo"""


class GestoForaDoMundo(ValueError):
    """Gesto de hoje (`alimentar`, `oferecer_fruta_<f>`, `por_bola`, `tirar_bola`) numa vida com o mundo: o gesto e o `deixar_*`."""


# ================================================================== a conta inteira (a mesma no TS da etapa 5)
def div_arred(n: int, d: int) -> int:
    """n / d em inteiros, arredondado ao mais proximo, meio longe do zero (o mesmo de lobos.div_arred). d > 0."""
    if d <= 0:
        raise ValueError(f"divisor nao positivo: {d}")
    q, r = divmod(abs(n), d)
    if 2 * r >= d:
        q += 1
    return q if n >= 0 else -q


def distancia(dx: int, dy: int) -> int:
    return math.isqrt(dx * dx + dy * dy)


def no_mapa(x: int, y: int, cm: ConfigMundo) -> tuple[int, int]:
    """corta para dentro do mapa"""
    return min(cm.celulas_x * cm.sub - 1, max(0, x)), min(cm.celulas_y * cm.sub - 1, max(0, y))


def deslocar(x: int, y: int, direcao: int, comprimento: int, cm: ConfigMundo) -> tuple[int, int]:
    """o ponto a `comprimento` subunidades na direcao (0 a 15 do DIR16), cortado para dentro do mapa"""
    cx, cy = DIR16[direcao]
    return no_mapa(x + div_arred(cx * comprimento, ESCALA_DIR), y + div_arred(cy * comprimento, ESCALA_DIR), cm)


def passo_ate(x: int, y: int, tx: int, ty: int, alcance: int, cm: ConfigMundo) -> tuple[int, int]:
    """secao 5: chega em t se d <= alcance; senao anda `alcance` na direcao de t, cortado para dentro do mapa"""
    dx, dy = tx - x, ty - y
    d = distancia(dx, dy)
    if d <= alcance:
        return tx, ty
    return no_mapa(x + div_arred(dx * alcance, d), y + div_arred(dy * alcance, d), cm)


def centro_da_celula(celula: tuple, cm: ConfigMundo) -> tuple[int, int]:
    return celula[0] * cm.sub + cm.sub // 2, celula[1] * cm.sub + cm.sub // 2


def regiao_de(x: int, cm: ConfigMundo) -> int:
    """0 casa, 1 jardim, 2 campo, 3 mata (a ordem de layout.regioes)"""
    celula = x // cm.sub
    for i, (_, x0, x1) in enumerate(cm.layout.regioes):
        if x0 <= celula <= x1:
            return i
    raise ValueError(f"x fora de toda regiao: {x}")


ZONA_BANHEIRO = -1                     # a zona da necessidade dentro do banheiro (fora dele, o indice da regiao)


def faixa_do_banheiro(cbh: ConfigBanheiro, cm: ConfigMundo) -> tuple[int, int, int, int]:
    """O retangulo do banheiro em subunidades, inclusivo: (x0, x1, y0, y1). Fora do mapa, ou fora da casa, falha alto."""
    (cx0, cx1), (cy0, cy1) = cbh.celulas_x, cbh.celulas_y
    if cx1 >= cm.celulas_x or cy1 >= cm.celulas_y:
        raise ValueError(f"banheiro fora do mapa: x {cbh.celulas_x}, y {cbh.celulas_y}")
    casa = cm.layout.regioes[0]
    if casa[0] != "casa" or not casa[1] <= cx0 <= cx1 <= casa[2]:
        raise ValueError(f"o banheiro tem de ficar dentro da casa {casa}: x {cbh.celulas_x}")
    sub = cm.sub
    return cx0 * sub, (cx1 + 1) * sub - 1, cy0 * sub, (cy1 + 1) * sub - 1


def no_banheiro(x: int, y: int, cbh: ConfigBanheiro, cm: ConfigMundo) -> bool:
    x0, x1, y0, y1 = faixa_do_banheiro(cbh, cm)
    return x0 <= x <= x1 and y0 <= y <= y1


def ponto_do_banheiro(x: int, y: int, cbh: ConfigBanheiro, cm: ConfigMundo) -> tuple[int, int]:
    """O ponto do banheiro mais perto de (x, y): a posicao cortada para dentro do retangulo (dentro dele, a propria posicao)."""
    x0, x1, y0, y1 = faixa_do_banheiro(cbh, cm)
    return min(x1, max(x0, x)), min(y1, max(y0, y))


def zona_da_necessidade(x: int, y: int, cbh: ConfigBanheiro, cm: ConfigMundo) -> int:
    """A zona em que a necessidade incomoda (secao 3): o banheiro (ZONA_BANHEIRO) dentro do retangulo, a regiao de sempre fora dele."""
    return ZONA_BANHEIRO if no_banheiro(x, y, cbh, cm) else regiao_de(x, cm)


def campo_em(x: int, y: int, fontes: list[tuple[int, int, int]], raio: int) -> int:
    """A conta inteira do cheiro (secao 7), com o raio dado em subunidades: a soma de A x (R - d) // R sobre as fontes com d < R; `fontes`
    = (x, y, A). O cheiro da comida (`cheiro_em`), o cheiro de cada pet e o rastro (dois pets, secao 5.3) e o som (5.4) usam esta conta."""
    total = 0
    for fx, fy, a in fontes:
        d = distancia(fx - x, fy - y)
        if d < raio:
            total += a * (raio - d) // raio
    return total


def direcao_do_campo(x: int, y: int, fontes: list[tuple[int, int, int]], raio: int, sub: int) -> tuple[int, int]:
    """(campo no centro, direcao): a direcao 1 a 8 em que o campo medido a 1 celula (`sub` subunidades) passa do centro, a maior vence e o
    empate fica com a ordem fixa; 0 sem gradiente. O ponto da medida nao e cortado ao mapa (so conta)."""
    centro = campo_em(x, y, fontes, raio)
    melhor, direcao = centro, 0
    for k in range(8):
        cx, cy = DIR16[2 * k]
        c = campo_em(x + div_arred(cx * sub, ESCALA_DIR), y + div_arred(cy * sub, ESCALA_DIR), fontes, raio)
        if c > melhor:
            melhor, direcao = c, k + 1
    return centro, direcao


def cheiro_em(x: int, y: int, fontes: list[tuple[int, int, int]], cm: ConfigMundo) -> int:
    """secao 7: a soma de A x (R - d) // R sobre as comidas boas com d < R; `fontes` = (x, y, A)"""
    return campo_em(x, y, fontes, cm.raio_cheiro_celulas * cm.sub)


def direcao_do_cheiro(x: int, y: int, fontes: list[tuple[int, int, int]], cm: ConfigMundo) -> tuple[int, int]:
    """(cheiro no centro, direcao): a direcao 1 a 8 em que o cheiro medido a 1 celula passa do centro, a maior vence e o empate fica
    com a ordem fixa; 0 sem gradiente. O ponto da medida nao e cortado ao mapa (so conta)."""
    return direcao_do_campo(x, y, fontes, cm.raio_cheiro_celulas * cm.sub, cm.sub)


# a fruta ao lado da racao (ConfigFrutaAoLado; o RP-2 de docs/futuro/paladar.md): a origem da comida que o dono poe ao lado da racao,
# para separar no registro do consumo "comeu a fruta ao lado" de "achou na arvore" e de "a comida do dono"
ORIGEM_AO_LADO = "dono_ao_lado"


# ================================================================== o Paladar, o lado do mundo (docs/futuro/paladar.md, secao 3.1)
# o registro de status dos campos da ConfigPaladar (conferido por teste contra os campos da dataclass)
PARAMETROS_PALADAR_MUNDO = {
    "ligada": ("PROPOSTO", "docs/futuro/paladar.md, secao 4: a chave do mundo, desligada por padrao"),
    "perfis": ("PROPOSTO", "SEM FONTE; docs/futuro/paladar.md, secao 3.1 (PL-3): quatro qualidades, as frutas como a mesma forma girada "
                           "(3C/4 e C/4), a racao com C/4 de salgado"),
}


# ================================================================== percepcao e alvos
@dataclass(frozen=True)
class PercepcaoMundo:
    """Secao 7. `vistos`: (id, tipo, dx, dy, d), em ordem de d, tipo e id, no maximo `max_vistos`; tipo = `racao`, `a`, `b`, `c`,
    o mesmo com `_podre`, ou `bola` (id 0). `cheiro` so das comidas boas; `direcao_cheiro` 0 a 8 (com o orgao do Olfato da comida, os
    dois ficam 0: o cheiro chega pelos receptores do corpo, dois pets, secao 5.6); `alvo_pendente` o tipo do alvo da
    decisao anterior que ficou sem chegar, ou None. `troncos` (o J5, so com ConfigPetQuePensaMundo.ligada; senao vazio): (id, dx, dy, d)
    dos troncos a ate o raio da visao, em ordem de d e id."""

    x: int
    y: int
    regiao: int
    vistos: tuple
    cheiro: int
    direcao_cheiro: int
    alvo_pendente: str | None
    troncos: tuple = ()


@dataclass(frozen=True)
class Alvo:
    """Um candidato a alvo (secao 5). tipo: `comida` (id), `bola` (id 0), `cheiro`, `vagar`, `casa`, `continuar` (de = o tipo do alvo
    antigo) ou `ponto` (so o cerebro, no explorar: um lugar lembrado). No grupo, o explorar tem tambem `seguir` (onde o outro esta, visto)
    e `onde_comeu` (onde se viu o outro comer), que o padrao do motor nunca escolhe (dois pets, secao 6)."""

    tipo: str
    x: int
    y: int
    id: int | None = None
    de: str | None = None

    @staticmethod
    def ponto(x: int, y: int) -> "Alvo":
        return Alvo("ponto", x, y)

    def objeto(self) -> str | None:
        """`comida` ou `bola` quando o alvo e um objeto (direto ou pelo continuar)"""
        t = self.de if self.tipo == "continuar" else self.tipo
        return t if t in ("comida", "bola") else None

    def para_dict(self) -> dict:
        return {"tipo": self.tipo, "x": self.x, "y": self.y, "id": self.id, "de": self.de}


# ================================================================== o Olfato da comida pelo orgao (dois pets, secao 5.6; DP-13)
# Com o orgao do Olfato da comida ligado, o pet nao recebe a direcao do cheiro: a percepcao do mundo fica sem `cheiro` e sem
# `direcao_cheiro`, e o candidato `cheiro` da lugar a dois candidatos que so usam o que o pet sente (G-SEM-DIRECAO): a leitura dos
# receptores das narinas (`PercepcaoCorpo.olfato_comida`, ou `_esq` e `_dir`), a direcao do ultimo passo (a propriocepcao) e o u do alvo.
# As funcoes abaixo so recebem isso; nenhuma le o mundo (conferido por AST no teste).
CANDIDATOS_CHEIRO_ORGAO = ("cheiro_seguir", "cheiro_virar")


def leitura_do_olfato(corpo, narinas: int) -> tuple[int, ...]:
    """A leitura dos receptores do Olfato da comida na `PercepcaoCorpo`: (r,) com uma narina, (r_esq, r_dir) com duas. Sem o receptor
    (o orgao desligado, ou outro numero de narinas), falha alto."""
    if narinas == 1:
        leitura = (corpo.olfato_comida,)
    elif narinas == 2:
        leitura = (corpo.olfato_comida_esq, corpo.olfato_comida_dir)
    else:
        raise ValueError(f"narinas: 1 ou 2, nao {narinas!r}")
    if any(type(r) is not int for r in leitura):
        raise ValueError(f"o Olfato da comida sem o receptor na percepcao do corpo: {leitura!r} ({narinas} narina(s))")
    return leitura


def olfato_forte(leitura: tuple[int, ...], limiar: int) -> bool:
    """o cheiro forte do explorar: alguma narina le acima do `limiar` (na escala S do receptor)"""
    return max(leitura) > limiar


def alvos_do_olfato(x: int, y: int, passo: int, leitura: tuple[int, ...], anterior: tuple[int, ...] | None, u: int,
                    cm: ConfigMundo) -> list[Alvo]:
    """Os candidatos do cheiro pelo orgao (secao 5.6), em (x, y), com a direcao do ultimo passo `passo` (0 a 15 na DIR16): nenhum sem
    cheiro (todas as narinas em 0); senao dois, a `passo_cheiro_celulas` celulas, com o preferido pela regra da opcao na frente.
    - `cheiro_seguir`: um passo na direcao do ultimo passo;
    - `cheiro_virar`: com duas narinas, 45 graus (dois indices da DIR16) para o lado da narina mais forte, a esquerda no sentido
      anti-horario; empatadas, o lado sai do bit 8 do u. Com uma narina, uma das outras 15 direcoes, sorteada pelos bits altos do u
      (`(u >> 8) % 15`; o u e o da rng `alvo`: "a direcao sorteada no fluxo alvo").
    - o preferido: com duas narinas, seguir se elas empatam, virar se nao; com uma, virar se a leitura caiu desde a decisao anterior
      (`anterior`), seguir se subiu ou ficou (e na primeira decisao)."""
    if type(passo) is not int or not 0 <= passo < 16:
        raise ValueError(f"passo fora da DIR16: {passo!r}")
    if type(u) is not int or not 0 <= u < (1 << 16):
        raise ValueError(f"u do alvo fora de [0, 2^16): {u!r}")
    if max(leitura) == 0:
        return []
    dist = cm.passo_cheiro_celulas * cm.sub
    if len(leitura) == 2:
        esq, dir_ = leitura
        lado = 2 if esq > dir_ else (-2 if dir_ > esq else (2 if (u >> 8) & 1 == 0 else -2))
        virar = (passo + lado) % 16
        prefere_virar = esq != dir_
    elif len(leitura) == 1:
        virar = (passo + 1 + (u >> 8) % 15) % 16
        prefere_virar = anterior is not None and leitura[0] < anterior[0]
    else:
        raise ValueError(f"leitura do olfato com {len(leitura)} narinas")
    seguir = Alvo("cheiro_seguir", *deslocar(x, y, passo, dist, cm))
    vira = Alvo("cheiro_virar", *deslocar(x, y, virar, dist, cm))
    return [vira, seguir] if prefere_virar else [seguir, vira]


def alvo_padrao_de(acao: AcaoPet, cands: list[Alvo], p: PercepcaoMundo, cmf: ConfigMundo) -> Alvo | None:
    """O alvo padrao do motor (secao 5), em funcao pura da percepcao da decisao: o que o instinto usa e nunca a comida podre.
    - comer: a comida boa vista mais proxima (os vistos ja vem em ordem de d, tipo e id), senao o cheiro;
    - explorar: o continuar, senao o cheiro forte (acima de `limiar_cheiro_explorar`), senao o vagar;
    - brincar: a bola vista.
    Com o orgao do Olfato da comida (dois pets, secao 5.6), o "cheiro" e o primeiro dos candidatos do orgao (`cheiro_seguir`,
    `cheiro_virar`): o motor os poe com o preferido pela regra da opcao na frente (`alvos_do_olfato`), e no explorar so os oferece com o
    cheiro forte (`olfato_forte`). A percepcao do mundo nao tem cheiro nem direcao, entao o ramo de hoje nao dispara (G-SEM-DIRECAO)."""
    if acao is AcaoPet.COMER:
        podres = {i for i, tipo, *_ in p.vistos if tipo.endswith("_podre")}
        for a in cands:
            if a.tipo == "comida" and a.id not in podres:
                return a
        return next((a for a in cands if a.tipo == "cheiro" or a.tipo in CANDIDATOS_CHEIRO_ORGAO), None)
    if acao is AcaoPet.EXPLORAR:
        cont = next((a for a in cands if a.tipo == "continuar"), None)
        if cont is not None:
            return cont
        if p.direcao_cheiro and p.cheiro > cmf.limiar_cheiro_explorar:
            return next(a for a in cands if a.tipo == "cheiro")
        olfato = next((a for a in cands if a.tipo in CANDIDATOS_CHEIRO_ORGAO), None)
        if olfato is not None:
            return olfato
        return next(a for a in cands if a.tipo == "vagar")
    return next((a for a in cands if a.tipo == "bola"), None)


# ================================================================== os sentidos sobre o outro (dois pets, etapa 3; degrau 1)
# docs/futuro/dois_pets.md, secao 5 (DP-4, DP-11): a visao (5.1) e o toque (5.2). Nenhum sentido le o estado interno do outro: as funcoes
# abaixo so recebem o que e fisico (a posicao, a acao que se ve de fora, o consumo visto, o contato). O grupo (digilab/grupo.py) as chama.
CANDIDATOS_SOCIAIS = ("seguir", "onde_comeu")      # os candidatos do explorar que so existem com o outro (secao 6)
TIPOS_TOQUE = ("disputa_ganhou", "disputa_perdeu", "encostou", "encostaram", "esbarrou")


@dataclass(frozen=True)
class PercepcaoSocial:
    """Secao 5. Sem campo de estado interno do outro (G-RECEPTOR-SOCIAL).
    - `outros`: (id, dx, dy, d, acao_visivel) dos pets a ate o raio da visao do mundo, em ordem de d e de id; `acao_visivel` e a acao
      que o outro escolheu na ultima decisao dele (o que se ve de fora);
    - `onde_comeu`: (id, x, y, idade) do ultimo ponto em que este pet VIU cada outro comer (dentro do raio, no momento do consumo), com a
      idade em ticks; em ordem de id; nada de quem nunca foi visto comendo;
    - `toque`: (id, tipo, direcao, idade) do ultimo contato com cada outro (tipo em TIPOS_TOQUE; direcao 1 a 8 na tabela do cheiro, 0 na
      mesma celula); em ordem de id;
    - `sentidos` (o degrau 1b, so com a ConfigSentidos ligada; senao None): o cheiro de cada outro, o rastro dele e os sons ouvidos
      (`PercepcaoSentidos`)."""

    outros: tuple
    onde_comeu: tuple
    toque: tuple
    sentidos: "PercepcaoSentidos | None" = None


# ------------------------------------------------------------------ o degrau 1b: o cheiro proprio, o rastro e o som (dois pets, etapa 8)
# docs/futuro/dois_pets.md, secoes 5.3, 5.4 e 5.6; OA-1 (o campo calculado), OA-2 (a direcao pelo mundo, como pre-processamento) e OA-3
# (o som em linha reta). Tudo aqui so le o que e fisico: a posicao do outro, o rastro que ele deixou no mundo e o som da acao dele.
SONS = ("comendo", "bola", "chamado", "emburrado")
SOM_DA_ACAO = {AcaoPet.CHAMAR_ATENCAO: "chamado", AcaoPet.EMBURRAR: "emburrado"}     # os sons das acoes sem alvo

# os numeros do mundo sao os da ConfigOlfato e da ConfigOuvido (status em corpo.PARAMETROS_OLFATO e corpo.PARAMETROS_OUVIDO)
PARAMETROS_SENTIDOS: dict[str, tuple[str, str]] = {
    "ligada": ("DECIDIDO", "DP-11 (o degrau 1b), DP-13 e DP-14: desligada por padrao, o grupo de hoje (G2)"),
}
PASSO_INICIAL = 0            # a direcao do ultimo passo antes do primeiro passo: leste (0 na DIR16), uma convencao (secao 5.6)


@dataclass(frozen=True)
class PercepcaoSentidos:
    """O degrau 1b (secoes 5.3, 5.4 e 5.6). Sem campo de estado interno do outro (G-RECEPTOR-SOCIAL).
    - `passo`: a direcao do ultimo passo do proprio pet (0 a 15 na tabela DIR16; a propriocepcao que poe as narinas e os ouvidos);
    - `cheiro`: (id, intensidade, direcao, esq, dir) de cada outro presente, em ordem de id: a intensidade no centro do pet e a direcao 1 a 8
      (0 sem gradiente; a conta e o desempate do cheiro da comida) do canal do outro (o cheiro dele e o rastro dele), e a intensidade no
      ponto de cada narina;
    - `sons`: (id, som, direcao, distancia, intensidade, esq, dir, idade) dos sons ouvidos desde a decisao anterior, na ordem em que
      soaram: quem emitiu, o som (SONS), a direcao 1 a 8 e a distancia em linha reta ate onde soou, a intensidade no centro e no ponto de
      cada ouvido (tudo no momento do som) e a idade em ticks. Os sons do proprio pet nao entram.
    Com o orgao do Olfato social, `cheiro` fica vazio; com o da Audicao, `sons` fica vazio: o que o pet sente do outro chega so
    pelos receptores do corpo, sem direcao nem distancia do mundo (secao 5.6; G-SEM-DIRECAO)."""

    passo: int
    cheiro: tuple
    sons: tuple


def direcao_em_8(dx: int, dy: int) -> int:
    """a direcao 1 a 8 (L, NE, N, NO, O, SO, S, SE; a tabela do cheiro) mais perto do vetor (dx, dy): o maior produto escalar com DIR16,
    o empate fica com a ordem fixa; 0 no vetor nulo"""
    if dx == 0 and dy == 0:
        return 0
    melhor, direcao = None, 0
    for k in range(8):
        cx, cy = DIR16[2 * k]
        p = cx * dx + cy * dy
        if melhor is None or p > melhor:
            melhor, direcao = p, k + 1
    return direcao


def direcao_em_16(dx: int, dy: int) -> int | None:
    """o indice 0 a 15 da tabela DIR16 mais perto do vetor (dx, dy) (o maior produto escalar; o empate fica com a ordem fixa); None no
    vetor nulo"""
    if dx == 0 and dy == 0:
        return None
    melhor, direcao = None, 0
    for j, (cx, cy) in enumerate(DIR16):
        p = cx * dx + cy * dy
        if melhor is None or p > melhor:
            melhor, direcao = p, j
    return direcao


def pontos_laterais(x: int, y: int, passo: int, afastamento: int) -> tuple[tuple[int, int], tuple[int, int]]:
    """(esquerda, direita): os pontos a `afastamento` subunidades de lado em relacao a direcao `passo` (0 a 15 na DIR16; a esquerda e 90
    graus no sentido anti-horario, quatro indices adiante). Nao cortados ao mapa (so contam)."""
    pontos = []
    for lado in ((passo + 4) % 16, (passo + 12) % 16):
        cx, cy = DIR16[lado]
        pontos.append((x + div_arred(cx * afastamento, ESCALA_DIR), y + div_arred(cy * afastamento, ESCALA_DIR)))
    return pontos[0], pontos[1]


def fontes_do_pet(x: int, y: int, marcas: list[tuple[int, int, int]], tick: int, co: ConfigOlfato) -> list[tuple[int, int, int]]:
    """secao 5.3: as fontes do canal de um pet: o cheiro dele na posicao atual (`cheiro_pet`) e cada marca do rastro (x, y, tick em que foi
    deixada), com `cheiro_marca` x (T - idade) // T, T = `idade_marca`; a marca na idade T, ou com intensidade 0, nao conta"""
    fontes = [(x, y, co.cheiro_pet)]
    for mx, my, t in marcas:
        idade = tick - t
        if idade < 0:
            raise ValueError(f"marca do futuro: tick {t} no tick {tick}")
        if idade < co.idade_marca:
            a = co.cheiro_marca * (co.idade_marca - idade) // co.idade_marca
            if a > 0:
                fontes.append((mx, my, a))
    return fontes


def cheiro_do_pet(x: int, y: int, passo: int, fontes: list[tuple[int, int, int]], co: ConfigOlfato, sub: int) -> tuple:
    """(intensidade, direcao, esq, dir) do canal de um pet para quem esta em (x, y) com o ultimo passo `passo`: a conta inteira e a direcao
    do cheiro da comida (`direcao_do_campo`) com o raio do pet, e a intensidade no ponto de cada narina"""
    raio = co.raio_celulas * sub
    centro, direcao = direcao_do_campo(x, y, fontes, raio, sub)
    esq, dir_ = pontos_laterais(x, y, passo, co.afastamento_narinas)
    return centro, direcao, campo_em(*esq, fontes, raio), campo_em(*dir_, fontes, raio)


def som_ouvido(lx: int, ly: int, passo: int, sx: int, sy: int, cv: ConfigOuvido, sub: int) -> tuple | None:
    """(direcao, distancia, intensidade, esq, dir) do som que soou em (sx, sy) para quem esta em (lx, ly) com o ultimo passo `passo`, ou
    None fora do alcance (d >= R_som): a linha reta (OA-3), a intensidade A x (R - d) // R no centro e no ponto de cada ouvido"""
    raio = cv.raio_som_celulas * sub
    dx, dy = sx - lx, sy - ly
    d = distancia(dx, dy)
    if d >= raio:
        return None
    fonte = [(sx, sy, cv.som)]
    esq, dir_ = pontos_laterais(lx, ly, passo, cv.afastamento_ouvidos)
    return direcao_em_8(dx, dy), d, campo_em(lx, ly, fonte, raio), campo_em(*esq, fonte, raio), campo_em(*dir_, fonte, raio)


def celula_de(x: int, y: int, cm: ConfigMundo) -> tuple[int, int]:
    return x // cm.sub, y // cm.sub


def direcao_vizinha(dcx: int, dcy: int) -> int:
    """a direcao de uma celula vizinha na tabela do cheiro (1 a 8 = L, NE, N, NO, O, SO, S, SE; y cresce para o sul), 0 na mesma celula"""
    if max(abs(dcx), abs(dcy)) > 1:
        raise ValueError(f"celula nao vizinha: ({dcx}, {dcy})")
    if dcx == 0 and dcy == 0:
        return 0
    for k in range(8):
        cx, cy = DIR16[2 * k]
        if (cx > 0) - (cx < 0) == dcx and (cy > 0) - (cy < 0) == dcy:
            return k + 1
    raise AssertionError("tabela das direcoes incompleta")      # as 8 vizinhas estao todas na tabela


def em_contato(a: tuple[int, int], b: tuple[int, int], cm: ConfigMundo, raio_celulas: int) -> bool:
    """secao 5.2: as celulas a no maximo `raio_celulas` em Chebyshev (a mesma celula ou a vizinha, com 1)"""
    (ax, ay), (bx, by) = celula_de(*a, cm), celula_de(*b, cm)
    return max(abs(ax - bx), abs(ay - by)) <= raio_celulas


def perceber_social(x: int, y: int, tick: int, outros: list[tuple], viu_comer: dict, toques: dict, raio_visao: int,
                    sentidos: PercepcaoSentidos | None = None) -> PercepcaoSocial:
    """Pura: o que um pet em (x, y) percebe dos outros agora. `outros` = (id, x, y, acao_visivel), so o fisico; `viu_comer` = {id: (x, y,
    tick)} e `toques` = {id: (tipo, direcao, tick)}, a memoria do proprio pet; `tick` e o do mundo. `sentidos`: o degrau 1b, ja montado
    pelo grupo (so com a ConfigSentidos ligada)."""
    vistos = []
    for ident, ox, oy, acao in outros:
        dx, dy = ox - x, oy - y
        d = distancia(dx, dy)
        if d <= raio_visao:
            vistos.append((ident, dx, dy, d, acao))
    vistos.sort(key=lambda v: (v[3], v[0]))
    comeu = tuple((i, cx, cy, tick - t) for i, (cx, cy, t) in sorted(viu_comer.items()))
    toque = tuple((i, tipo, direcao, tick - t) for i, (tipo, direcao, t) in sorted(toques.items()))
    return PercepcaoSocial(tuple(vistos), comeu, toque, sentidos)


def tipos_do_contato(a: str, b: str, disputa: dict | None, seguiu: dict) -> dict[str, str]:
    """secao 5.2: o tipo do contato para cada um, pelo que aconteceu no tick (nunca por intencao). `disputa` = {"vencedor", "perdedor"} ou
    None; `seguiu` = {id: o id do pet que ele seguiu neste tick, ou None}. A disputa vence o encostar, que vence o esbarrar."""
    if disputa is not None:
        return {disputa["vencedor"]: "disputa_ganhou", disputa["perdedor"]: "disputa_perdeu"}
    tipos = {}
    for eu, outro in ((a, b), (b, a)):
        if seguiu.get(eu) == outro:
            tipos[eu] = "encostou"
        elif seguiu.get(outro) == eu:
            tipos[eu] = "encostaram"
        else:
            tipos[eu] = "esbarrou"
    return tipos


# ================================================================== o embrulho da politica
class _PoliticaComMundo:
    """Embrulho do MotorMundo (so com a chave): antes de `agir` avanca o mundo e injeta `obs.mundo`; em `observar` aplica a consequencia
    do mundo ANTES de repassar a transicao (com a observacao seguinte refeita), e depois chama os ganchos. Delega o resto."""

    def __init__(self, politica, motor: "MotorMundo") -> None:
        self._pm = politica
        self._motor = motor

    def agir(self, obs: Observacao, rng: random.Random) -> AcaoPet:
        obs = replace(obs, mundo=self._motor._antes_da_decisao(), social=self._motor._social)
        self._motor._obs_decisao = obs
        return self._pm.agir(obs, rng)

    def observar(self, transicao: Transicao) -> None:
        m = self._motor
        ocorrido = m._consequencia(transicao.acao)
        obs_depois = m._observacao_depois_mundo()
        self._pm.observar(Transicao(observacao=m._obs_decisao, acao=transicao.acao, observacao_seguinte=obs_depois,
                                    recompensa=transicao.recompensa))
        comeu = ocorrido["comeu"] if ocorrido is not None else None
        if comeu is not None and comeu["tipo"] in FRUTAS:
            aviso = getattr(self._pm, "fruta_comida", None)     # E2: os cerebros que ja o usam
            if aviso is not None:
                aviso(comeu["tipo"], obs_depois)
        if ocorrido is not None:
            gancho = getattr(self._pm, "consequencia_mundo", None)
            if gancho is not None:
                gancho(transicao.acao, ocorrido, obs_depois)

    def receber_acao_dono(self, acao: AcaoUsuario, tick: int) -> None:
        self._pm.receber_acao_dono(acao, tick)

    def estado_interno(self) -> dict:
        return self._pm.estado_interno()

    def __getattr__(self, nome: str):
        return getattr(self._pm, nome)


# ================================================================== o mundo como componente (dois pets, etapa 1)
class Mundo:
    """O mundo fisico como componente (docs/futuro/dois_pets.md, secao 2; DP-1; docs/TAREFA_V2_DOIS_PETS.md, etapa 1): as arvores, as
    comidas, a bola, os fluxos do mundo (`mundo-arvores`, `mundo-bola`) e os registros do mundo (as quedas, as comidas que sumiram, as
    bolas deixadas e as rolagens). Nao sabe de pet: a posicao, o alvo pendente, a percepcao guardada, os fluxos do pet (`alvo`,
    `mundo-sujeira`) e os registros do pet (consumos, decisoes, regioes, visitas, comidas deixadas pelo dono) ficam no MotorMundo de cada
    pet. Com um pet, o MotorMundo e dono do proprio Mundo, com a semente do pet: a vida de hoje, byte a byte (G2). A forma e a do motor
    em TS (web/app/motor/mundo.ts: o mundo recebe a posicao e o estado do pet), sem a parte do pet, para dois motores poderem apontar
    para o mesmo Mundo (etapa 2).

    A atualizacao (quedas, apodrecer, sumir) e idempotente por tick (`atualizar`): a segunda chamada no mesmo tick nao faz nada, e um tick
    para tras falha alto. Com dois pets, quem decide primeiro no tick a dispara, e o resultado so le o tick e o fluxo `mundo-arvores`."""

    def __init__(self, cfg_mundo: ConfigMundo, semente: int) -> None:
        if not cfg_mundo.ligada:
            raise MundoSemChave("o Mundo so existe com a ConfigMundo ligada")
        cm = self.cmf = cfg_mundo
        self.semente = semente
        self.rng_arvores = random.Random(derivar_semente("mundo-arvores", semente))
        self.rng_bola = random.Random(derivar_semente("mundo-bola", semente))
        self.raio_visao = cm.raio_visao_celulas * cm.sub
        self.ninho = centro_da_celula(cm.layout.ninho, cm)
        self.comedouro = centro_da_celula(cm.layout.comedouro, cm)
        bx, by = centro_da_celula(cm.layout.bola_inicio, cm)
        self.bola = {"x0": bx, "y0": by, "x1": bx, "y1": by, "t0": 0, "d": 0}
        nomes = [r[0] for r in cm.layout.regioes]
        self.arvores: list[dict] = []
        for ident, x, y, fruta in cm.layout.arvores:
            if fruta not in FRUTAS:
                raise ValueError(f"arvore {ident} com fruta desconhecida: {fruta!r}")
            ax, ay = centro_da_celula((x, y), cm)
            nome = nomes[regiao_de(ax, cm)]
            if nome == "jardim":
                p = cm.p_queda_jardim * cm.mult_queda
            elif nome == "mata":
                p = cm.p_queda_mata * cm.mult_queda
            else:
                raise ValueError(f"arvore {ident} fora do jardim e da mata: {nome}")
            self.arvores.append({"id": ident, "x": ax, "y": ay, "fruta": fruta, "regiao": nome, "p": p, "recarga_ate": 0})
        self.comidas: dict[int, dict] = {}
        self.prox_id = ID_BOLA + 1
        self.passo_mundo = 0
        self.tick_atualizado: int | None = None          # o ultimo tick atualizado (a atualizacao e idempotente por tick)
        # os registros do mundo (derivados; o replay reconstroi tudo)
        self.quedas: list[dict] = []
        self.sumidas: list[dict] = []
        self.bolas_deixadas: list[dict] = []
        self.rolagens: list[dict] = []
        # o banheiro (TAREFA_V2_BANHEIRO, secao 3): as necessidades no chao, so depois de `ligar_necessidades` (um motor com o banheiro);
        # sem ele, None e nada muda (nem o resumo). Um contador proprio: os ids das comidas nao mudam com o banheiro
        self.necessidades: dict[int, dict] | None = None
        self.prox_necessidade = 1
        self.recolhidas: list[dict] = []
        # o J5 (o pet que pensa): as trocas de tipo por arvore, so depois de `ligar_trocas` (o motor com a ConfigPetQuePensaMundo); sem
        # ela, None e nada muda (nem o resumo)
        self.trocas_tipo: list[dict] | None = None
        # o J5, adendo 8 (A8.3): as paradas de arvores (o tick, o tipo, as arvores, os ids retirados do chao), so depois da primeira; sem
        # ela, None e nada muda (nem o resumo)
        self.paradas_arvores: list[dict] | None = None
        # dois pets, etapa 8 (o degrau 1b): o rastro de cada pet, {id: [(x, y, tick), ...]} em ordem de tick, so depois de `ligar_marcas`
        # (o grupo com a ConfigSentidos ligada); sem ele, None e nada muda (nem o resumo)
        self.marcas: dict[str, list[tuple[int, int, int]]] | None = None

    # ------------------------------------------------------------ dois pets, etapa 8: o rastro (secao 5.3)
    def ligar_marcas(self) -> None:
        if self.marcas is None:
            self.marcas = {}

    def deixar_marca(self, ident: str, x: int, y: int, tick: int, co: ConfigOlfato) -> None:
        """uma marca do pet `ident` em (x, y) no tick (do mundo): as que chegaram a idade T saem, e acima de `max_marcas` as mais antigas"""
        if self.marcas is None:
            raise ValueError("marca num Mundo sem o rastro (ligar_marcas: o grupo com a ConfigSentidos ligada)")
        lista = self.marcas.setdefault(ident, [])
        if lista and lista[-1][2] > tick:
            raise ValueError(f"marca fora de ordem: tick {tick} depois de {lista[-1][2]}")
        while lista and tick - lista[0][2] >= co.idade_marca:
            lista.pop(0)
        lista.append((x, y, tick))
        while len(lista) > co.max_marcas:
            lista.pop(0)

    def marcas_de(self, ident: str) -> list[tuple[int, int, int]]:
        if self.marcas is None:
            raise ValueError("rastro num Mundo sem o rastro (ligar_marcas)")
        return list(self.marcas.get(ident, []))

    # ------------------------------------------------------------ o J5: a troca de tipo por arvore e os troncos
    def ligar_trocas(self) -> None:
        if self.trocas_tipo is None:
            self.trocas_tipo = []

    def trocar_tipos(self, x: str, y: str, tick: int) -> dict:
        """No tick (o mundo ja atualizado ate ele), as arvores do tipo x passam a dar y e as do y a dar x. As frutas no chao nao mudam."""
        if self.trocas_tipo is None:
            raise PetQuePensaSemChave("troca de tipo num Mundo sem a ConfigPetQuePensaMundo")
        if x == y or x not in FRUTAS or y not in FRUTAS:
            raise ValueError(f"troca de tipo invalida: {x!r}, {y!r}")
        if self.tick_atualizado != tick:
            raise RuntimeError(f"troca de tipo no tick {tick} com o mundo atualizado ate {self.tick_atualizado}")
        novas = {}
        for arv in self.arvores:
            if arv["fruta"] in (x, y):
                arv["fruta"] = y if arv["fruta"] == x else x
                novas[arv["id"]] = arv["fruta"]
        reg = {"tick": tick, "x": x, "y": y, "arvores": novas}
        self.trocas_tipo.append(reg)
        return reg

    def parar_arvores(self, tipo: str, tick: int) -> dict:
        """O J5, adendo 8 (A8.3, PJ8-1): no tick (o mundo ja atualizado ate ele), as arvores que dao `tipo` param de dar fruta ate o fim da
        vida, e as frutas caidas delas que estao no chao (maduras ou podres) saem do mundo. As de outra origem (a fruta ao lado da racao, a
        comida do dono) nunca saem. Os sorteios das quedas continuam (o fluxo `mundo-arvores` anda igual), so nada cai dessas arvores."""
        if self.trocas_tipo is None:
            raise PetQuePensaSemChave("parar arvores num Mundo sem a ConfigPetQuePensaMundo")
        if tipo not in FRUTAS:
            raise ValueError(f"parar arvores de tipo invalido: {tipo!r}")
        if self.tick_atualizado != tick:
            raise RuntimeError(f"parar arvores no tick {tick} com o mundo atualizado ate {self.tick_atualizado}")
        if self.paradas_arvores is None:
            self.paradas_arvores = []
        arvores = sorted(a["id"] for a in self.arvores if a["fruta"] == tipo)
        for a in self.arvores:
            if a["id"] in arvores:
                a["parada"] = True
        retiradas = sorted(c["id"] for c in self.comidas.values() if c["origem"] in arvores)
        for i in retiradas:
            del self.comidas[i]
        reg = {"tick": tick, "tipo": tipo, "arvores": arvores, "retiradas": retiradas}
        self.paradas_arvores.append(reg)
        return reg

    def troncos_perto(self, x: int, y: int) -> list[tuple]:
        """(id, dx, dy, d) dos troncos a ate o raio da visao de (x, y), em ordem de d e id"""
        perto = []
        for arv in self.arvores:
            dx, dy = arv["x"] - x, arv["y"] - y
            d = distancia(dx, dy)
            if d <= self.raio_visao:
                perto.append((arv["id"], dx, dy, d))
        perto.sort(key=lambda t: (t[3], t[0]))
        return perto

    # ------------------------------------------------------------ o banheiro
    def ligar_necessidades(self) -> None:
        """Chamado pelo motor com o banheiro (todos os pets do mundo com ele chamam; a segunda vez nao faz nada)."""
        if self.necessidades is None:
            self.necessidades = {}

    def deixar_necessidade(self, x: int, y: int, tick: int) -> dict:
        """A necessidade que fica no chao, onde o pet aliviou (o limpador nao a recolheu)."""
        if self.necessidades is None:
            raise BanheiroSemMundo("necessidade num Mundo sem o banheiro ligado")
        if no_mapa(x, y, self.cmf) != (x, y):
            raise ValueError(f"necessidade fora do mapa: ({x}, {y})")
        n = {"id": self.prox_necessidade, "x": x, "y": y, "tick": tick}
        self.prox_necessidade += 1
        self.necessidades[n["id"]] = n
        return n

    def recolher_necessidades(self, ids: list[int], tick: int, como: str) -> None:
        """As necessidades `ids` saem do chao (o `limpar` do dono); a que nao esta no chao falha alto (KeyError)."""
        for i in ids:
            n = self.necessidades.pop(i)
            self.recolhidas.append({**n, "recolhida_em": tick, "como": como})

    # ------------------------------------------------------------ a comida e a bola no tempo
    def prazo_maduro(self, tipo: str) -> int:
        return self.cmf.maduro_racao_min if tipo == "racao" else self.cmf.maduro_fruta_min

    def situacao(self, comida: dict, tick: int) -> str | None:
        """`madura`, `podre`, ou None (sumiu), pela idade (secao 6)"""
        idade = tick - comida["tick_posta"]
        m = self.prazo_maduro(comida["tipo"])
        if idade < m:
            return "madura"
        if idade < m + self.cmf.prazo_podre_min:
            return "podre"
        return None

    def bola_em(self, tick: int) -> tuple[int, int]:
        """a bola anda `atrito` subunidades por tick ate parar no ponto final"""
        b = self.bola
        if b["d"] == 0 or tick >= b["t0"] + -(-b["d"] // self.cmf.atrito):
            return b["x1"], b["y1"]
        andou = self.cmf.atrito * (tick - b["t0"])
        return b["x0"] + div_arred((b["x1"] - b["x0"]) * andou, b["d"]), b["y0"] + div_arred((b["y1"] - b["y0"]) * andou, b["d"])

    def nova_comida(self, tipo: str, x: int, y: int, tick: int, origem: str) -> dict:
        c = {"id": self.prox_id, "tipo": tipo, "x": x, "y": y, "tick_posta": tick, "origem": origem}
        self.prox_id += 1
        self.comidas[c["id"]] = c
        return c

    def _remover_sumidas(self, tick: int) -> None:
        for c in [c for c in self.comidas.values() if self.situacao(c, tick) is None]:
            del self.comidas[c["id"]]
            fim = c["tick_posta"] + self.prazo_maduro(c["tipo"]) + self.cmf.prazo_podre_min
            self.sumidas.append({**c, "sumiu_em": fim})

    def atualizar(self, tick: int) -> None:
        """os passos do mundo ate o tick (secao 6): em cada um, cada arvore fora da recarga sorteia a queda no fluxo `mundo-arvores`.
        Os sorteios nao dependem do pet; so quantas frutas cabem no chao dependem (o excesso nao cai). Idempotente por tick: no mesmo
        tick nao faz nada (quem decide primeiro dispara), e um tick para tras falha alto."""
        if self.tick_atualizado is not None:
            if tick < self.tick_atualizado:
                raise ValueError(f"o mundo nao volta no tempo: atualizado ate o tick {self.tick_atualizado}, pedido o {tick}")
            if tick == self.tick_atualizado:
                return
        cm, rng = self.cmf, self.rng_arvores
        ate = tick // cm.passo_mundo_ticks
        while self.passo_mundo < ate:
            self.passo_mundo += 1
            tk = self.passo_mundo * cm.passo_mundo_ticks
            for arv in self.arvores:
                if tk < arv["recarga_ate"]:
                    continue
                if rng.random() >= arv["p"]:
                    continue
                n = rng.randint(cm.frutas_por_queda_min, cm.frutas_por_queda_max)
                pontos = [deslocar(arv["x"], arv["y"], rng.randrange(16), rng.randrange(cm.raio_queda_celulas * cm.sub + 1), cm)
                          for _ in range(n)]
                no_chao = sum(1 for c in self.comidas.values()
                              if c["origem"] == arv["id"] and self.situacao(c, tk) is not None)
                cabem = 0 if arv.get("parada") else max(0, cm.max_frutas_por_arvore - no_chao)
                ids = [self.nova_comida(arv["fruta"], x, y, tk, arv["id"])["id"] for x, y in pontos[:cabem]]
                self.quedas.append({"tick": tk, "arvore": arv["id"], "sorteadas": n, "pontos": pontos, "colocadas": ids})
                arv["recarga_ate"] = tk + cm.recarga_min
        self._remover_sumidas(tick)
        self.tick_atualizado = tick

    # ------------------------------------------------------------ percepcao
    def fontes_de_cheiro(self, tick: int) -> list[tuple[int, int, int]]:
        cm = self.cmf
        return [(c["x"], c["y"], cm.cheiro_racao if c["tipo"] == "racao" else cm.cheiro_fruta)
                for c in self.comidas.values() if self.situacao(c, tick) == "madura"]

    def perceber(self, x: int, y: int, tick: int, alvo_pendente: str | None = None, troncos: bool = False,
                 cheiro: bool = True) -> PercepcaoMundo:
        """Pura (nao sorteia nem muda nada): o que um pet em (x, y) percebe agora (MF-3); `alvo_pendente` e o do pet. `troncos` (o J5):
        os troncos a vista entram na percepcao. `cheiro` False (o orgao do Olfato da comida, dois pets, secao 5.6; G-SEM-DIRECAO): o
        cheiro e a direcao do cheiro nem sao calculados e ficam 0; o pet so sente o cheiro pelos receptores do corpo."""
        vistos = []
        for c in self.comidas.values():
            sit = self.situacao(c, tick)
            if sit is None:
                continue
            dx, dy = c["x"] - x, c["y"] - y
            d = distancia(dx, dy)
            if d <= self.raio_visao:
                vistos.append((c["id"], c["tipo"] if sit == "madura" else c["tipo"] + "_podre", dx, dy, d))
        bx, by = self.bola_em(tick)
        d = distancia(bx - x, by - y)
        if d <= self.raio_visao:
            vistos.append((ID_BOLA, "bola", bx - x, by - y, d))
        vistos.sort(key=lambda v: (v[4], v[1], v[0]))
        intensidade, direcao = direcao_do_cheiro(x, y, self.fontes_de_cheiro(tick), self.cmf) if cheiro else (0, 0)
        p = PercepcaoMundo(x, y, regiao_de(x, self.cmf), tuple(vistos[:self.cmf.max_vistos]), intensidade, direcao, alvo_pendente)
        return replace(p, troncos=tuple(self.troncos_perto(x, y))) if troncos else p

    def maduras_perto(self, x: int, y: int, tick: int, raio: int) -> list[tuple[int, str, int]]:
        """as comidas maduras a ate `raio` de (x, y), em (distancia, tipo, id), da mais perto (o "achou e comeu" do explorar, MF-1)"""
        perto = sorted((distancia(c["x"] - x, c["y"] - y), c["tipo"], c["id"]) for c in self.comidas.values()
                       if self.situacao(c, tick) == "madura")
        return [p for p in perto if p[0] <= raio]

    # ------------------------------------------------------------ o que muda o mundo
    def retirar_comida(self, ident: int) -> dict:
        """a comida sai do chao (alguem a comeu); a que nao esta no chao falha alto (KeyError)"""
        return self.comidas.pop(ident)

    def rolar_bola(self, tick: int) -> dict:
        """alguem brincou com a bola: ela rola do ponto em que esta, no fluxo `mundo-bola` (vai mais longe no campo)"""
        cm = self.cmf
        bx, by = self.bola_em(tick)
        direcao = self.rng_bola.randrange(16)
        celulas = self.rng_bola.randint(cm.bola_min_celulas, cm.bola_max_celulas)
        if cm.layout.regioes[regiao_de(bx, cm)][0] == "campo":
            celulas *= cm.mult_bola_campo
        x1, y1 = deslocar(bx, by, direcao, celulas * cm.sub, cm)
        self.bola = {"x0": bx, "y0": by, "x1": x1, "y1": y1, "t0": tick, "d": distancia(x1 - bx, y1 - by)}
        rolagem = {"tick": tick, "de": (bx, by), "para": (x1, y1), "direcao": direcao, "celulas": celulas}
        self.rolagens.append(rolagem)
        return rolagem

    def deixar_comida(self, tipo: str, x: int, y: int, tick: int) -> dict:
        """a comida que o dono deixa (origem `dono`); tipo desconhecido ou posicao fora do mapa falha alto"""
        if tipo not in TIPOS_COMIDA_MUNDO or no_mapa(x, y, self.cmf) != (x, y):
            raise ValueError(f"deixar_comida invalido: {tipo!r} ({x}, {y})")
        return self.nova_comida(tipo, x, y, tick, "dono")

    def deixar_fruta_ao_lado(self, tipo: str, x: int, y: int, tick: int) -> dict:
        """a fruta que o dono poe ao lado da racao (ConfigFrutaAoLado), com a origem `dono_ao_lado`; so fruta, dentro do mapa"""
        if tipo not in FRUTAS or no_mapa(x, y, self.cmf) != (x, y):
            raise ValueError(f"deixar_fruta invalido: {tipo!r} ({x}, {y})")
        return self.nova_comida(tipo, x, y, tick, ORIGEM_AO_LADO)

    def deixar_bola(self, x: int, y: int, tick: int) -> None:
        """o dono poe a bola parada em (x, y); fora do mapa falha alto"""
        if no_mapa(x, y, self.cmf) != (x, y):
            raise ValueError(f"deixar_bola fora do mapa: ({x}, {y})")
        self.bola = {"x0": x, "y0": y, "x1": x, "y1": y, "t0": tick, "d": 0}
        self.bolas_deixadas.append({"tick": tick, "x": x, "y": y})

    # ------------------------------------------------------------ leitura
    def resumo(self) -> dict:
        """tudo o que o mundo guarda (sem o que e do pet)"""
        return {"bola": dict(self.bola), "comidas": [dict(c) for c in self.comidas.values()], "prox_id": self.prox_id,
                "passo_mundo": self.passo_mundo, "tick_atualizado": self.tick_atualizado, "arvores": [dict(a) for a in self.arvores],
                "rngs": [r.getstate() for r in (self.rng_arvores, self.rng_bola)], "quedas": self.quedas, "sumidas": self.sumidas,
                "bolas_deixadas": self.bolas_deixadas, "rolagens": self.rolagens,
                **({} if self.necessidades is None else {
                    "necessidades": [dict(n) for n in self.necessidades.values()], "prox_necessidade": self.prox_necessidade,
                    "recolhidas": self.recolhidas}),
                **({} if self.trocas_tipo is None else {"trocas_tipo": self.trocas_tipo}),
                **({} if self.paradas_arvores is None else {"paradas_arvores": self.paradas_arvores}),
                **({} if self.marcas is None else {"marcas": {i: [list(m) for m in l] for i, l in sorted(self.marcas.items())}})}


# ================================================================== o motor
class MotorMundo(MotorFrutas):
    """O motor de um pet no mundo fisico. Ligado, e dono do proprio `Mundo` (`self.mundo`, com a semente do pet): o que e do mundo
    (arvores, comidas, bola, quedas, sumidas, rolagens, bolas deixadas e os fluxos `mundo-arvores` e `mundo-bola`) mora nele, e os
    atributos de antes (`comidas`, `arvores`, `bola_mundo`, `quedas`...) leem de la. O que e do pet fica aqui: a posicao, o alvo pendente,
    a percepcao da decisao, os fluxos `alvo` e `mundo-sujeira` e os registros do pet (consumos, decisoes, regioes, visitas, comidas
    deixadas pelo dono)."""

    def __init__(self, *a, cfg_mundo: ConfigMundo | None = None, efeito_frutas: dict | None = None, mundo: "Mundo | None" = None,
                 entrada_mundo: int = 0, cfg_banheiro: ConfigBanheiro | None = None, cfg_pqp: ConfigPetQuePensaMundo | None = None,
                 cfg_paladar: ConfigPaladar | None = None, cfg_fruta_ao_lado: ConfigFrutaAoLado | None = None, **kw) -> None:
        super().__init__(*a, **kw)
        self.cmf = cfg_mundo or CONFIG_MUNDO
        self.cbh = cfg_banheiro or CONFIG_BANHEIRO
        self.cpq = cfg_pqp or CONFIG_PQP_MUNDO
        self.cpal = cfg_paladar or CONFIG_PALADAR
        if not isinstance(self.cpal, ConfigPaladar):
            raise TypeError(f"cfg_paladar e uma ConfigPaladar: {self.cpal!r}")
        self.cfal = cfg_fruta_ao_lado or CONFIG_FRUTA_AO_LADO
        if not isinstance(self.cfal, ConfigFrutaAoLado):
            raise TypeError(f"cfg_fruta_ao_lado e uma ConfigFrutaAoLado: {self.cfal!r}")
        if not self.cmf.ligada:
            if efeito_frutas is not None or mundo is not None or entrada_mundo:
                raise ValueError("efeito_frutas, mundo e entrada_mundo so existem com o mundo ligado")
            if self.cbh.ligada:
                raise BanheiroSemMundo("o banheiro exige o mundo fisico (ConfigMundo.ligada)")
            if self.cpq.ligada:
                raise PetQuePensaSemChave("o J5 (ConfigPetQuePensaMundo) exige o mundo fisico (ConfigMundo.ligada)")
            if self.cpal.ligada:
                raise ValueError("o Paladar (ConfigPaladar) exige o mundo fisico (ConfigMundo.ligada): os perfis sao das comidas do mapa")
            if self.cfal.ligada:
                raise ValueError("a fruta ao lado (ConfigFrutaAoLado) exige o mundo fisico (ConfigMundo.ligada)")
            return                                     # desligado: o MotorFrutas byte a byte (nem embrulho, nem Mundo)
        if self.cf.ligada or self.cb.ligada:
            raise ValueError("o mundo substitui o cenario do N4 e da A1: ConfigFrutas e ConfigBola desligadas com ConfigMundo.ligada")
        if self.ce.ligada or self.cl.ligada:
            raise ValueError("o mundo minimo roda sem educacao e sem lesoes (a morte fica desligada, plano secao 2)")
        efeito = {f: 0.0 for f in FRUTAS} if efeito_frutas is None else dict(efeito_frutas)
        if set(efeito) != set(FRUTAS):
            raise ValueError(f"efeito_frutas precisa de {FRUTAS}: {sorted(efeito)}")
        self.efeito_frutas = efeito
        cm, sub = self.cmf, self.cmf.sub
        self._alcance = cm.velocidade * self.cfg.intervalo_decisao_ticks
        self._raio_pegar = cm.raio_pegar_celulas * sub
        self._raio_visao = cm.raio_visao_celulas * sub
        self._raio_mancha = cm.raio_mancha_celulas * sub
        semente = self.semente
        if mundo is None:
            if entrada_mundo:
                raise ValueError("entrada_mundo so com um Mundo dado (o do grupo)")
            self.mundo = Mundo(cm, semente)           # com um pet, o motor e dono do proprio mundo (a semente do mundo e a do pet)
        else:                                         # no grupo (digilab/grupo.py): o mundo e de todos, e o pet entra num tick dele
            if not isinstance(mundo, Mundo) or mundo.cmf != cm:
                raise ValueError("o Mundo dado tem de ser um Mundo com a mesma ConfigMundo do motor")
            if type(entrada_mundo) is not int or entrada_mundo < 0 or entrada_mundo % TICKS_POR_DIA:
                raise ValueError(f"entrada_mundo tem de ser um inicio de dia do mundo (multiplo de {TICKS_POR_DIA}): {entrada_mundo!r}")
            self.mundo = mundo
        # o relogio do pet (o Estado, o log, o corpo) comeca em 0 na entrada; o do mundo e o do pet mais a entrada. Os metodos do motor
        # recebem o tick do pet; o Mundo e os registros do mundo fisico usam o do mundo. Com a entrada no inicio do dia, a hora do dia
        # e a mesma nos dois relogios.
        self.entrada_mundo = entrada_mundo
        self._rng_sujeira = random.Random(derivar_semente("mundo-sujeira", semente))
        self._rng_alvo = random.Random(derivar_semente("alvo", semente))
        self.pet = self.mundo.ninho
        self._pendente: dict | None = None             # {"acao", "alvo"}: o alvo que ficou sem chegar
        self._fome_antes = 0.0
        self._percepcao: PercepcaoMundo | None = None
        self._obs_decisao: Observacao | None = None
        self._manchas_abertas: dict[str, dict] = {}
        # os registros do pet (derivados; o replay reconstroi tudo)
        self.consumos_mundo: list[dict] = []
        self.deixadas: list[dict] = []
        self.decisoes_mundo: list[dict] = []
        self.regioes: list[dict] = []
        self.visitas: list[dict] = []
        if self.cbh.ligada:
            # o banheiro (secao 2): exige o corpo na frente (a vontade e do corpo); o MotorCorpo confere a sub-chave `banheiro`
            from .motor_corpo import MotorCorpo
            if not isinstance(self, MotorCorpo):
                raise BanheiroSemMundo("o banheiro exige o corpo na frente do motor (com_corpo(MotorMundo)) com a sub-chave banheiro")
            faixa_do_banheiro(self.cbh, cm)                # o retangulo no mapa e dentro da casa (falha alto)
            self.mundo.ligar_necessidades()
            self.alivios: list[dict] = []              # o contrato da bancada: tick, dentro, urgente, alvo, distancia, recolhido
            self.recolhas: list[dict] = []             # o limpar do dono: tick, zona, ids recolhidos
            self.alivios_dentro = 0
            self.idas_banheiro: list[dict] = []        # a continuacao: cada aliviar com o alvo `banheiro` que segurou a vontade

        # dois pets, etapa 3: o grupo e o id do pet nele (o Grupo poe na entrada); fora do grupo, nada disto e usado e a vida e a de hoje
        if self.cfal.ligada:
            # a fruta ao lado da racao (RP-2 do paladar): so com um pet, fora do grupo (o registro do grupo nao tem o evento)
            if mundo is not None:
                raise ValueError("a fruta ao lado (ConfigFrutaAoLado) roda com um pet, fora do grupo")
            self.frutas_ao_lado: list[dict] = []        # cada fruta posta: tick, id, tipo, x, y, a racao de referencia
        if self.cpq.ligada:
            # o J5 (TAREFA_V2_PET_QUE_PENSA, secao 2.3): so com um pet (o grupo nao tem a mao nem a troca)
            if mundo is not None:
                raise PetQuePensaSemChave("o J5 (ConfigPetQuePensaMundo) roda com um pet, fora do grupo")
            self.troncos_vistos: dict[str, int] = {}     # id -> o primeiro tick do mundo em que o pet viu o tronco
            self.mundo.ligar_trocas()

        self._grupo = None
        self.ident: str | None = None
        self._social: PercepcaoSocial | None = None     # a percepcao social da decisao (None sozinho)
        self._cands_sociais: dict[Alvo, str] = {}       # o candidato social da decisao -> o id do outro
        self._pendente_antes: dict | None = None        # o alvo pendente com que a decisao comecou (a disputa)
        self._tick_social: dict | None = None           # o que o grupo le no fim do tick (partida, alvo, quem seguiu, o que comeu)
        self._viu_comer: dict[str, tuple] = {}          # a memoria da visao: {id: (x, y, tick)} do ultimo consumo visto de cada outro
        self._toques: dict[str, tuple] = {}             # a memoria do toque: {id: (tipo, direcao, tick)} do ultimo contato com cada outro
        # dois pets, etapa 8 (o degrau 1b): a direcao do ultimo passo (0 a 15 na DIR16), acompanhada so com a ConfigSentidos ligada no grupo
        # ou com o orgao do Olfato ou da Audicao no corpo (que a pede na primeira leitura); a caixa dos sons ouvidos desde a decisao
        # anterior (esvaziada a cada decisao) e o estimulo dos ouvidos do orgao, por tick (o tick do mundo em que o som entra no passo)
        self._passo: int | None = None
        self._olfato_anterior: tuple[int, ...] | None = None      # o orgao do Olfato da comida: a leitura da decisao anterior
        self._sons_ouvidos: list[tuple] = []
        self._sons_orgao: list[tuple] = []
        # os registros sociais do pet (as medidas; derivados, o replay refaz)
        self.vistos_comer: list[dict] = []
        self.idas_onde_comeu: list[dict] = []
        self.a_vista: dict[str, int] = {}               # decisoes com cada outro a vista
        self.decisoes_no_grupo = 0                      # decisoes com outro pet presente
        self.politica = _PoliticaComMundo(self.politica, self)

    # ------------------------------------------------------------ o que e do mundo (lido do Mundo)
    @property
    def comidas(self) -> dict[int, dict]:
        return self.mundo.comidas

    @property
    def arvores(self) -> list[dict]:
        return self.mundo.arvores

    @property
    def bola_mundo(self) -> dict:
        return self.mundo.bola

    @property
    def comedouro(self) -> tuple[int, int]:
        return self.mundo.comedouro

    @property
    def quedas(self) -> list[dict]:
        return self.mundo.quedas

    @property
    def sumidas(self) -> list[dict]:
        return self.mundo.sumidas

    @property
    def rolagens(self) -> list[dict]:
        return self.mundo.rolagens

    @property
    def bolas_deixadas(self) -> list[dict]:
        return self.mundo.bolas_deixadas

    @property
    def _rng_arvores(self) -> random.Random:
        return self.mundo.rng_arvores

    @property
    def _rng_bola(self) -> random.Random:
        return self.mundo.rng_bola

    @property
    def _prox_id(self) -> int:
        return self.mundo.prox_id

    @property
    def _passo_mundo(self) -> int:
        return self.mundo.passo_mundo

    def _tm(self, tick: int) -> int:
        """o tick do pet no relogio do mundo"""
        return tick + self.entrada_mundo

    def _prazo_maduro(self, tipo: str) -> int:
        return self.mundo.prazo_maduro(tipo)

    def situacao(self, comida: dict, tick: int) -> str | None:
        return self.mundo.situacao(comida, self._tm(tick))

    def bola_em(self, tick: int) -> tuple[int, int]:
        return self.mundo.bola_em(self._tm(tick))

    def _nova_comida(self, tipo: str, x: int, y: int, tick: int, origem: str) -> dict:
        return self.mundo.nova_comida(tipo, x, y, self._tm(tick), origem)

    def _atualizar_mundo(self, tick: int) -> None:
        self.mundo.atualizar(self._tm(tick))

    def _fontes_de_cheiro(self, tick: int) -> list[tuple[int, int, int]]:
        return self.mundo.fontes_de_cheiro(self._tm(tick))

    # ------------------------------------------------------------ percepcao
    def _perceber(self, tick: int) -> PercepcaoMundo:
        """Pura (nao sorteia nem muda nada): o que o pet percebe agora."""
        x, y = self.pet
        pend = self._pendente["alvo"].tipo if self._pendente is not None else None
        return self.mundo.perceber(x, y, self._tm(tick), pend, troncos=self.cpq.ligada, cheiro=not self._olfato_comida())

    def _observacao_depois_mundo(self) -> Observacao:
        """A observacao seguinte da decisao, com a consequencia do mundo aplicada (o MotorCorpo poe o `obs.corpo` por cima)."""
        return replace(Observacao.de_estado(self._estado), mundo=self._perceber(self._estado.tick), social=self.percepcao_social())

    def percepcao_social(self) -> "PercepcaoSocial | None":
        """o que o pet percebe dos outros agora (None fora do grupo, ou sozinho nele)"""
        return None if self._grupo is None else self._grupo.perceber_social(self.ident)

    def _antes_da_decisao(self) -> PercepcaoMundo:
        """Chamado pelo embrulho logo antes de `agir`: o mundo anda ate o tick (uma vez por tick) e o pet percebe."""
        t = self._estado.tick
        self.mundo.atualizar(self._tm(t))
        self._percepcao = self._perceber(t)
        self._fome_antes = self._estado.fome
        if self._olfato_comida() or self._olfato_outro() or self._audicao():
            self._ligar_propriocepcao()                     # os orgaos usam a direcao do ultimo passo (5.6), venha de onde vier o estimulo
        if self.cpq.ligada:
            self._ver_troncos(self._percepcao.troncos, self._tm(t))
        if self._grupo is not None:
            self._social = self.percepcao_social()
            if self._grupo.cs.ligada:
                self._sons_ouvidos = []                     # os sons desde a decisao anterior ja estao na percepcao desta
            self._pendente_antes = self._pendente
            self._cands_sociais = {}
            if self._social is not None:
                self.decisoes_no_grupo += 1
                for ident, *_ in self._social.outros:
                    self.a_vista[ident] = self.a_vista.get(ident, 0) + 1
        return self._percepcao

    def _intensidades_do_orgao(self) -> dict[str, int]:
        """O lado do mundo dos orgaos do Olfato e da Audicao (dois pets, secao 5.6; DP-13 e DP-14), pedido pelo MotorCorpo antes de cada tick
        e de cada percepcao: por receptor de orgao do corpo, a intensidade no ponto da narina (do ouvido), um inteiro, sem direcao. Com
        duas narinas, os pontos sao os de `pontos_laterais` pela direcao do ultimo passo; com uma, o centro do pet.
        - `olfato_comida`: o cheiro das comidas boas (`campo_em` com as fontes e o raio do cheiro da comida);
        - `olfato_outro`: o canal de cada outro pet do grupo (o cheiro proprio e o rastro, `fontes_do_pet`), so com a ConfigSentidos ligada
          e o outro presente; fora disso, 0;
        - `ouvido_<som>`: a soma dos sons daquele tipo que entram no passo deste tick (a intensidade no ponto do ouvido, de onde o pet estava
          quando o som soou); entre os sons, 0."""
        self._ligar_propriocepcao()
        agora = self._tm(self._estado.tick)
        self.mundo.atualizar(agora)                      # idempotente por tick: as quedas sao as mesmas atualizando em todo tick
        x, y = self.pet
        sub = self.cmf.sub
        g = self._grupo
        outros = [] if g is None or not g.cs.ligada else [i for i in g.ids_presentes() if i != self.ident]
        self._sons_orgao = [s for s in self._sons_orgao if s[0] >= agora]
        out = {}
        for o in self.corpo.orgaos:
            if o.sentido == "olfato":
                af = self.co.afastamento_narinas
                ponto = (x, y) if o.lado is None else pontos_laterais(x, y, self._passo, af)[0 if o.lado == "esq" else 1]
                if o.canal == "comida":
                    out[o.receptor] = campo_em(*ponto, self.mundo.fontes_de_cheiro(agora), self.cmf.raio_cheiro_celulas * sub)
                elif o.canal == "outro":
                    v = 0
                    for i in outros:
                        fontes = fontes_do_pet(*g.motores[i].pet, self.mundo.marcas_de(i), agora, g.cs.olfato)
                        v += campo_em(*ponto, fontes, g.cs.olfato.raio_celulas * sub)
                    out[o.receptor] = v
                else:
                    raise ValueError(f"canal do olfato desconhecido: {o.canal!r}")
            elif o.sentido == "ouvido":
                k = 2 if o.lado is None else (3 if o.lado == "esq" else 4)
                out[o.receptor] = sum(s[k] for s in self._sons_orgao if s[0] == agora and s[1] == o.canal)
            else:
                raise ValueError(f"orgao desconhecido: {o.sentido!r}")
        return out

    def _ligar_propriocepcao(self) -> None:
        """A direcao do ultimo passo (a propriocepcao, secao 5.6) e do motor: ela comeca em PASSO_INICIAL na primeira vez que alguem a
        pede (os orgaos na decisao, o lado do mundo do orgao antes de cada tick, os sentidos do grupo na entrada) e dai anda com o pet. Nao
        depende de quem entrega o estimulo dos orgaos: um lado do mundo trocado (um motor de teste) nao a deixa desligada."""
        if self._passo is None:
            self._passo = PASSO_INICIAL

    def _ver_troncos(self, troncos, tick_mundo: int) -> None:
        """o J5: os troncos a vista entram em `troncos_vistos` (o primeiro tick em que o pet os viu)"""
        for ident, *_ in troncos:
            self.troncos_vistos.setdefault(ident, tick_mundo)

    # ------------------------------------------------------------ os alvos
    # ------------------------------------------------------------ os orgaos do corpo (o MotorCorpo os liga; aqui, sem corpo, nenhum)
    def _olfato_comida(self) -> bool:
        """o orgao do Olfato da comida (dois pets, secao 5.6): so existe com o corpo na frente (o MotorCorpo responde)"""
        return False

    def _olfato_outro(self) -> bool:
        """o orgao do Olfato social (o cheiro do outro e o rastro): so com o corpo na frente"""
        return False

    def _audicao(self) -> bool:
        """o orgao da Audicao: so com o corpo na frente"""
        return False

    def _leitura_olfato_decisao(self) -> tuple[int, ...]:
        """a leitura das narinas na observacao da decisao (o que o pet sente; G-SEM-DIRECAO)"""
        if self._obs_decisao is None or self._obs_decisao.corpo is None:
            raise RuntimeError("o Olfato da comida sem a percepcao do corpo na observacao da decisao")
        return leitura_do_olfato(self._obs_decisao.corpo, self.co.narinas)

    def _limiar_olfato_explorar(self) -> int:
        """o `limiar_cheiro_explorar` de hoje lido pelo receptor: a leitura que o orgao sem adaptacao da a essa intensidade"""
        return leitura_orgao(self.cmf.limiar_cheiro_explorar, 0, self.co.limiar, self.co.meia_saturacao, self.cc.escala_receptor)

    def _alvos_olfato(self, p: PercepcaoMundo, u: int, explorar: bool) -> list[Alvo]:
        """os candidatos do cheiro pelo orgao na decisao (no explorar, so com o cheiro forte)"""
        if self._passo is None:
            raise RuntimeError("o Olfato da comida sem a direcao do ultimo passo (o orgao a pede na primeira leitura)")
        leitura = self._leitura_olfato_decisao()
        if explorar and not olfato_forte(leitura, self._limiar_olfato_explorar()):
            return []
        return alvos_do_olfato(p.x, p.y, self._passo, leitura, self._olfato_anterior, u, self.cmf)

    def _alvo_cheiro(self, p: PercepcaoMundo) -> Alvo:
        x, y = deslocar(p.x, p.y, 2 * (p.direcao_cheiro - 1), self.cmf.passo_cheiro_celulas * self.cmf.sub, self.cmf)
        return Alvo("cheiro", x, y)

    def _continuar(self, acao: AcaoPet) -> Alvo | None:
        pend = self._pendente
        if pend is None or pend["acao"] is not acao:
            return None
        velho: Alvo = pend["alvo"]
        if velho.tipo == "comida":
            c = self.mundo.comidas.get(velho.id)
            return None if c is None else Alvo("continuar", c["x"], c["y"], velho.id, "comida")
        if velho.tipo == "bola":
            bx, by = self.mundo.bola_em(self._tm(self._estado.tick))
            return Alvo("continuar", bx, by, ID_BOLA, "bola")
        return Alvo("continuar", velho.x, velho.y, None, velho.tipo)

    def candidatos(self, acao: AcaoPet, u: int) -> list[Alvo]:
        """secao 5, a tabela das sub-decisoes"""
        p, cm = self._percepcao, self.cmf
        cands: list[Alvo] = []
        if acao is AcaoPet.COMER:
            cands += [Alvo("comida", p.x + dx, p.y + dy, i) for i, tipo, dx, dy, _ in p.vistos if tipo != "bola"]
            if self._olfato_comida():
                cands += self._alvos_olfato(p, u, explorar=False)
            elif p.direcao_cheiro:
                cands.append(self._alvo_cheiro(p))
        elif acao is AcaoPet.EXPLORAR:
            if self._olfato_comida():
                cands += self._alvos_olfato(p, u, explorar=True)
            elif p.direcao_cheiro:
                cands.append(self._alvo_cheiro(p))
            faixa = cm.vagar_max_celulas - cm.vagar_min_celulas + 1
            vx, vy = deslocar(p.x, p.y, u % 16, (cm.vagar_min_celulas + (u // 16) % faixa) * cm.sub, cm)
            cands.append(Alvo("vagar", vx, vy))
            cands.append(Alvo("casa", *self.mundo.comedouro))
        elif acao is AcaoPet.BRINCAR:
            cands += [Alvo("bola", p.x + dx, p.y + dy, i) for i, tipo, dx, dy, _ in p.vistos if tipo == "bola"]
        elif acao is AcaoPet.ALIVIAR and self.cbh.ligada:
            # o banheiro (secao 4): o ponto do banheiro mais perto e onde o pet esta. Sem candidato `continuar`: a ida pendente ao banheiro
            # (a continuacao) aparece na percepcao (`alvo_pendente`); o ponto e recalculado da posicao nova, na direcao da ida
            return [Alvo("banheiro", *ponto_do_banheiro(p.x, p.y, self.cbh, cm)), Alvo("aqui", p.x, p.y)]
        else:
            raise ValueError(f"acao sem alvo: {acao}")
        cont = self._continuar(acao)
        if cont is not None:
            cands.append(cont)
        if acao is AcaoPet.EXPLORAR and self._social is not None:
            cands += self._candidatos_sociais(p)
        if acao is AcaoPet.EXPLORAR and self.cpq.ligada:
            # PP-1: um candidato por tronco ja visto, no pe da arvore, na ordem do layout, depois dos de hoje
            cands += [Alvo(f"arvore:{a['id']}", a["x"], a["y"]) for a in self.mundo.arvores if a["id"] in self.troncos_vistos]
        return cands

    def _candidatos_sociais(self, p: PercepcaoMundo) -> list[Alvo]:
        """dois pets, secao 6: `seguir` cada outro visto (onde ele esta) e `onde_comeu` de cada outro que este pet viu comer, depois dos
        de hoje. O padrao do motor nunca os escolhe; so o cerebro."""
        cands = []
        for ident, dx, dy, _, _ in self._social.outros:
            a = Alvo("seguir", p.x + dx, p.y + dy)
            self._cands_sociais[a] = ident
            cands.append(a)
        for ident, x, y, _ in self._social.onde_comeu:
            a = Alvo("onde_comeu", x, y)
            self._cands_sociais[a] = ident
            cands.append(a)
        return cands

    def alvo_padrao(self, acao: AcaoPet, cands: list[Alvo]) -> Alvo | None:
        """o que o instinto usa (secao 5). Nunca escolhe comida podre. A conta e a `alvo_padrao_de` (o cerebro a usa para saber a classe
        do padrao, no alvo aprendido). No `aliviar` (o banheiro), `aqui`: alivia onde esta."""
        if acao is AcaoPet.ALIVIAR:
            return next(a for a in cands if a.tipo == "aqui")
        return alvo_padrao_de(acao, cands, self._percepcao, self.cmf)

    def _validar_alvo(self, acao: AcaoPet, alvo: Alvo, cands: list[Alvo]) -> None:
        if alvo in cands:
            return
        if acao is AcaoPet.EXPLORAR and alvo.tipo == "ponto" and alvo.id is None and alvo.de is None:
            if type(alvo.x) is int and type(alvo.y) is int and no_mapa(alvo.x, alvo.y, self.cmf) == (alvo.x, alvo.y):
                return
            raise ValueError(f"ponto fora do mapa ou nao inteiro: ({alvo.x!r}, {alvo.y!r})")
        raise ValueError(f"alvo fora dos candidatos de {acao.value}: {alvo}")

    # ------------------------------------------------------------ a consequencia
    def _comer_mundo(self, ident: int, como: str, tick: int) -> dict:
        c = self.mundo.retirar_comida(ident)
        tick = self._tm(tick)                               # o registro do consumo e do mundo: o relogio do mundo
        sit = self.mundo.situacao(c, tick)
        e = self._estado
        fome, humor, sujeira = e.fome, e.humor, e.sujeira
        if sit == "madura" and c["tipo"] == "racao":
            fome = min(1.0, fome + self.cfg.ganho_alimentar)
            if self._rng_sujeira.random() < self.cfg.prob_sujeira_pos_refeicao:
                sujeira = min(self.cfg.sujeira_maxima, sujeira + 1)
        elif sit == "madura":
            fome = min(1.0, fome + self.cmf.nutricao_fruta)
            humor = min(1.0, max(0.0, humor + self.efeito_frutas[c["tipo"]]))
        else:
            humor = min(1.0, max(0.0, humor + self.cmf.efeito_podre))
        self._estado = replace(e, fome=fome, humor=humor, sujeira=sujeira)
        reg = {"tick": tick, "id": c["id"], "tipo": c["tipo"], "origem": c["origem"], "tick_posta": c["tick_posta"],
               "situacao": sit, "como": como, "fome_antes": e.fome, "humor_antes": e.humor, "fome_depois": fome,
               "humor_depois": humor}
        if self.cpal.ligada:
            reg["perfil"] = self.perfil_de(c["tipo"]) if sit == "madura" else None     # o Paladar: a podre nao tem perfil
        self.consumos_mundo.append(reg)
        if self._grupo is not None:                          # dois pets: o consumo e visto pelos outros e lido pela disputa
            self._tick_social["comeu"] = {"id": c["id"], "tipo": c["tipo"], "x": c["x"], "y": c["y"], "situacao": sit}
            self._grupo.viu_comer(self.ident, c["x"], c["y"])
            self._grupo.emitir_som(self.ident, "comendo")
        return reg

    def perfil_de(self, tipo: str) -> dict:
        """O Paladar (secao 3.1): uma copia do perfil de gosto do tipo, {qualidade: inteiro em [0, C]}. Sem a chave, falha alto."""
        if not self.cpal.ligada:
            raise ValueError("perfil de gosto sem o Paladar (ConfigPaladar.ligada)")
        return dict(self.cpal.perfis[tipo])

    def _rolar_bola(self, tick: int) -> None:
        self.mundo.rolar_bola(self._tm(tick))

    def _consequencia(self, acao: AcaoPet) -> dict | None:
        """Chamado pelo embrulho em `observar`, antes do cerebro: anda, come, brinca, desfaz o +0,05 do comer (MF-2) e registra."""
        tick = self._estado.tick
        x0, y0 = self.pet
        regiao_antes = regiao_de(x0, self.cmf)
        alvo = None
        ocorrido = None
        if self._grupo is not None and self._grupo.sentidos_ativos():
            self.mundo.deixar_marca(self.ident, x0, y0, self._tm(tick), self._grupo.cs.olfato)     # o rastro (5.3)
        if acao in ACOES_COM_ALVO:
            u = self._rng_alvo.randrange(1 << 16)               # sempre nas tres acoes: numeros comuns
            cands = self.candidatos(acao, u)
            escolher = getattr(self._pm_cerebro(), "escolher_alvo", None)
            alvo = escolher(acao, list(cands), self._percepcao, u) if escolher is not None else None
            if alvo is None:
                alvo = self.alvo_padrao(acao, cands)
            else:
                self._validar_alvo(acao, alvo, cands)
            x1, y1 = (x0, y0) if alvo is None else passo_ate(x0, y0, alvo.x, alvo.y, self._alcance, self.cmf)
            if self._grupo is not None:
                self._tick_social = {"tick": self._tm(tick), "de": (x0, y0), "alvo": alvo, "pendente_antes": self._pendente_antes,
                                     "social": self._id_social(alvo), "comeu": None}
            desloc = distancia(x1 - x0, y1 - y0)
            self.pet = (x1, y1)
            e = self._estado
            if acao is AcaoPet.COMER:
                e = replace(e, fome=self._fome_antes)               # MF-2: comer so da fome com comida
            energia_antes = e.energia
            if desloc:
                e = replace(e, energia=max(0.0, e.energia - self.cmf.custo_energia_por_subunidade * desloc))
            self._estado = e
            chegou = alvo is not None and distancia(alvo.x - x1, alvo.y - y1) <= self._raio_pegar
            comeu = None
            bola = False
            if chegou and acao is AcaoPet.COMER and alvo.objeto() == "comida":
                comeu = self._comer_mundo(alvo.id, "comer", tick)
            elif chegou and acao is AcaoPet.EXPLORAR and self._estado.fome < self.cmf.fome_max_comer_achado:
                perto = self.mundo.maduras_perto(x1, y1, self._tm(tick), self._raio_pegar)
                if perto:
                    comeu = self._comer_mundo(perto[0][2], "achou", tick)
            elif chegou and acao is AcaoPet.BRINCAR and alvo.objeto() == "bola":
                self._estado = replace(self._estado, humor=min(1.0, self._estado.humor + self.cmf.ganho_humor_bola))
                self._rolar_bola(tick)
                bola = True
                if self._grupo is not None:
                    self._grupo.emitir_som(self.ident, "bola")
            if self._grupo is not None and self._id_social(alvo) is not None:
                self._registrar_social(alvo, chegou, comeu, x1, y1, tick)
            if alvo is not None and not chegou:
                base = alvo if alvo.tipo != "continuar" else Alvo(alvo.de, alvo.x, alvo.y, alvo.id)
                self._pendente = {"acao": acao, "alvo": base}
                if self._grupo is not None and self._id_social(alvo) is not None:
                    self._pendente["social"] = self._id_social(alvo)
            else:
                self._pendente = None
            ocorrido = {"acao": acao.value, "u": u, "alvo": None if alvo is None else alvo.para_dict(), "de": (x0, y0),
                        "para": (x1, y1), "deslocamento": desloc, "energia_gasta": energia_antes - self._estado.energia,
                        "chegou": chegou, "comeu": comeu, "brincou_com_bola": bola}
        elif acao is AcaoPet.ALIVIAR:
            alvo, ocorrido = self._aliviar(tick, x0, y0)
            if self._grupo is not None:                      # como os outros ramos: o alvo do aliviar nunca e comida (sem disputa)
                self._tick_social = {"tick": self._tm(tick), "de": (x0, y0), "alvo": alvo, "pendente_antes": self._pendente_antes,
                                     "social": None, "comeu": None}
        else:
            self._pendente = None
            if self._grupo is not None:
                self._tick_social = {"tick": self._tm(tick), "de": (x0, y0), "alvo": None, "pendente_antes": self._pendente_antes,
                                     "social": None, "comeu": None}
                if acao in SOM_DA_ACAO:
                    self._grupo.emitir_som(self.ident, SOM_DA_ACAO[acao])
        if self._passo is not None and self.pet != (x0, y0):
            self._passo = direcao_em_16(self.pet[0] - x0, self.pet[1] - y0)     # a propriocepcao (5.6): a direcao do ultimo passo
        if self._olfato_comida():
            self._olfato_anterior = self._leitura_olfato_decisao()   # a leitura desta decisao, para a seguinte (uma narina: subiu ou caiu)
        self._registrar_decisao(tick, acao, (x0, y0), regiao_antes, alvo, ocorrido)
        return ocorrido

    def _aliviar(self, tick: int, x0: int, y0: int) -> tuple[Alvo, dict]:
        """O `aliviar` (secoes 3 e 4): o alvo (`banheiro` ou `aqui`, pelo gancho do cerebro com o u da rng `alvo`; sem gancho, `aqui`),
        o andar ate ele com o custo de energia, e o alivio. Dentro do banheiro com o limpador, a necessidade e recolhida na hora; senao ela
        fica no chao (um objeto do Mundo). A vontade e o cheiro sao estimulos do corpo (o MotorCorpo, pelo `ocorrido`).

        A continuacao (decisao do Matheus, 2026-10-11): com o alvo `banheiro`, o pet que nao chega ao banheiro nesta decisao NAO alivia:
        segura a vontade, e o alvo fica pendente, como o `continuar` das outras acoes (a percepcao mostra `alvo_pendente` "banheiro" na
        decisao seguinte; outra acao desfaz). Nada vai ao corpo alem do andar; a ida fica em `idas_banheiro`. Com o alvo `aqui`, alivia
        onde esta. A regra urgente continua aliviando `aqui` (o acidente), com ou sem a ida pendente."""
        cbh, cm = self.cbh, self.cmf
        if not cbh.ligada:
            raise BanheiroSemMundo("aliviar sem o banheiro (ConfigBanheiro.ligada)")
        u = self._rng_alvo.randrange(1 << 16)                   # como nas outras acoes com alvo: numeros comuns
        cands = self.candidatos(AcaoPet.ALIVIAR, u)
        escolher = getattr(self._pm_cerebro(), "escolher_alvo", None)
        alvo = escolher(AcaoPet.ALIVIAR, list(cands), self._percepcao, u) if escolher is not None else None
        if alvo is None:
            alvo = self.alvo_padrao(AcaoPet.ALIVIAR, cands)
        else:
            self._validar_alvo(AcaoPet.ALIVIAR, alvo, cands)
        corpo = self._obs_decisao.corpo if self._obs_decisao is not None else None
        if corpo is None or corpo.vontade is None:
            raise BanheiroSemMundo("aliviar sem o receptor da vontade na observacao da decisao (o corpo com a sub-chave banheiro)")
        S = self.cc.escala_receptor                               # o receptor na escala S do corpo
        urgente = corpo.vontade / S > cbh.limiar_urgente          # a regra urgente do instinto (o acidente): o alvo e `aqui`
        if urgente and alvo.tipo != "aqui":
            raise RuntimeError(f"aliviar urgente (vontade {corpo.vontade}/{S}) com o alvo {alvo.tipo!r}: a regra urgente alivia aqui")
        bx, by = ponto_do_banheiro(x0, y0, cbh, cm)
        dist_banheiro = distancia(bx - x0, by - y0)
        x1, y1 = passo_ate(x0, y0, alvo.x, alvo.y, self._alcance, cm)
        desloc = distancia(x1 - x0, y1 - y0)
        self.pet = (x1, y1)
        e = self._estado
        energia_antes = e.energia
        if desloc:
            self._estado = replace(e, energia=max(0.0, e.energia - cm.custo_energia_por_subunidade * desloc))
        dentro = no_banheiro(x1, y1, cbh, cm)
        tm = self._tm(tick)
        if alvo.tipo == "banheiro" and not dentro:
            # a continuacao: segura a vontade; o alvo do banheiro fica pendente para a proxima decisao
            continuacao = self._pendente is not None and self._pendente["acao"] is AcaoPet.ALIVIAR
            self._pendente = {"acao": AcaoPet.ALIVIAR, "alvo": alvo}
            restante = distancia(bx - x1, by - y1)
            self.idas_banheiro.append({"tick": tm, "de": (x0, y0), "para": (x1, y1), "distancia": dist_banheiro, "restante": restante,
                                       "continuacao": continuacao})
            ocorrido = {"acao": AcaoPet.ALIVIAR.value, "u": u, "alvo": alvo.para_dict(), "de": (x0, y0), "para": (x1, y1),
                        "deslocamento": desloc, "energia_gasta": energia_antes - self._estado.energia, "chegou": False,
                        "comeu": None, "brincou_com_bola": False, "alivio": None,
                        "segurou": {"distancia": dist_banheiro, "restante": restante, "continuacao": continuacao}}
            return alvo, ocorrido
        self._pendente = None
        recolhido = dentro and cbh.limpador
        necessidade = None if recolhido else self.mundo.deixar_necessidade(x1, y1, tm)["id"]
        self.alivios.append({"tick": tm, "dentro": dentro, "urgente": urgente, "alvo": alvo.tipo, "distancia": dist_banheiro,
                             "recolhido": recolhido})
        self.alivios_dentro += dentro
        ocorrido = {"acao": AcaoPet.ALIVIAR.value, "u": u, "alvo": alvo.para_dict(), "de": (x0, y0), "para": (x1, y1),
                    "deslocamento": desloc, "energia_gasta": energia_antes - self._estado.energia, "chegou": (x1, y1) == (alvo.x, alvo.y),
                    "comeu": None, "brincou_com_bola": False,
                    "alivio": {"dentro": dentro, "urgente": urgente, "recolhido": recolhido, "necessidade": necessidade,
                               "distancia": dist_banheiro}}
        return alvo, ocorrido

    def necessidades_na_zona(self) -> int:
        """Quantas necessidades estao no chao na zona do pet (o banheiro, ou a regiao fora dele): o que o corpo recebe a cada tick."""
        cbh, cm = self.cbh, self.cmf
        z = zona_da_necessidade(*self.pet, cbh, cm)
        return sum(1 for n in self.mundo.necessidades.values() if zona_da_necessidade(n["x"], n["y"], cbh, cm) == z)

    def _id_social(self, alvo: Alvo | None) -> str | None:
        """o id do outro de um alvo social (seguir, onde_comeu, ou o continuar deles), ou None"""
        if alvo is None:
            return None
        if alvo.tipo in CANDIDATOS_SOCIAIS:
            return self._cands_sociais[alvo]
        if alvo.tipo == "continuar" and alvo.de in CANDIDATOS_SOCIAIS:
            return self._pendente_antes["social"]
        return None

    def _registrar_social(self, alvo: Alvo, chegou: bool, comeu: dict | None, x1: int, y1: int, tick: int) -> None:
        """a ida a `onde_comeu` (a confianca da secao 8 sai daqui): chegou, comeu, e quantas comidas boas estavam a vista na chegada"""
        classe = alvo.de if alvo.tipo == "continuar" else alvo.tipo
        if classe != "onde_comeu":
            return
        tm = self._tm(tick)
        boas = len(self.mundo.maduras_perto(x1, y1, tm, self._raio_visao)) if chegou else None
        self.idas_onde_comeu.append({"tick": tm, "outro": self._id_social(alvo), "x": alvo.x, "y": alvo.y,
                                     "continuacao": alvo.tipo == "continuar", "chegou": chegou,
                                     "comeu": None if comeu is None else {k: comeu[k] for k in ("id", "tipo", "situacao", "como")},
                                     "boas_a_vista": boas})

    def _pm_cerebro(self):
        """o que esta embaixo do embrulho do mundo (os ganchos do cerebro passam pelos embrulhos de baixo)"""
        return self.politica._pm

    def _registrar_decisao(self, tick: int, acao: AcaoPet, antes: tuple, regiao_antes: int, alvo: Alvo | None,
                           ocorrido: dict | None) -> None:
        tick = self._tm(tick)                               # os registros do mundo fisico: o relogio do mundo
        x1, y1 = self.pet
        regiao = regiao_de(x1, self.cmf)
        if self.cpq.ligada:
            self._ver_troncos(self.mundo.troncos_perto(x1, y1), tick)
        for v in self._manchas_abertas.values():               # as decisoes tomadas de dentro da mancha
            v["decisoes"] += 1
        dentro = {a["id"] for a in self.mundo.arvores if distancia(a["x"] - x1, a["y"] - y1) <= self._raio_mancha}
        for ident in [i for i in self._manchas_abertas if i not in dentro]:
            v = self._manchas_abertas.pop(ident)
            v["saida"] = tick
            self.visitas.append(v)
        for ident in sorted(dentro - set(self._manchas_abertas)):
            self._manchas_abertas[ident] = {"arvore": ident, "chegada": tick, "saida": None, "decisoes": 0}
        if regiao != regiao_antes:
            self.regioes.append({"tick": tick, "de": regiao_antes, "para": regiao})
        self.decisoes_mundo.append({
            "tick": tick, "acao": acao.value, "regra": getattr(self._pm_cerebro(), "ultima_regra", None),
            "antes": antes, "regiao_antes": regiao_antes, "x": x1, "y": y1, "regiao": regiao,
            "alvo": None if alvo is None else alvo.tipo,
            "chegou": None if ocorrido is None else ocorrido["chegou"],
            "deslocamento": 0 if ocorrido is None else ocorrido["deslocamento"],
            "energia_gasta": 0.0 if ocorrido is None else ocorrido["energia_gasta"],
            "comeu": None if ocorrido is None or ocorrido["comeu"] is None else ocorrido["comeu"]["id"],
            "brincou_com_bola": False if ocorrido is None else ocorrido["brincou_com_bola"],
            "manchas": sorted(dentro)})

    # ------------------------------------------------------------ o dono
    def _aplicar_acao_usuario(self, acao: AcaoUsuario) -> None:
        if acao in ACOES_MAO or acao in ACOES_TROCA_ARVORES or acao in ACOES_PARAR_ARVORES:
            if not (self.cmf.ligada and self.cpq.ligada):
                raise PetQuePensaSemChave(f"{acao.value} sem o mundo e a ConfigPetQuePensaMundo ligados")
            if acao in ACOES_MAO:
                self._dar_fruta(fruta_dada(acao))
            elif acao in ACOES_TROCA_ARVORES:
                self._trocar_arvores(*par_da_troca(acao))
            else:
                self._parar_arvores(tipo_parado(acao))
            return
        if self.cmf.ligada and acao in GESTOS_PROIBIDOS:
            raise GestoForaDoMundo(f"{acao.value} numa vida com o mundo: use deixar_comida/deixar_bola")
        super()._aplicar_acao_usuario(acao)
        if acao is AcaoUsuario.LIMPAR and self.cmf.ligada and self.cbh.ligada:
            # o banheiro (secao 3): o limpar de hoje passa a recolher as necessidades da zona do pet (o efeito no corpo e o de sempre)
            cbh, cm = self.cbh, self.cmf
            z = zona_da_necessidade(*self.pet, cbh, cm)
            ids = [n["id"] for n in self.mundo.necessidades.values() if zona_da_necessidade(n["x"], n["y"], cbh, cm) == z]
            tm = self._tm(self._estado.tick)
            self.mundo.recolher_necessidades(ids, tm, "limpar")
            self.recolhas.append({"tick": tm, "zona": z, "ids": ids})

    # ------------------------------------------------------------ o J5: a fruta na mao e a troca de tipo
    def _dar_fruta(self, f: str) -> None:
        """A fruta na mao (PQ-4, PP-5): o pet come na hora, onde esta, com o efeito vigente (a conta da fruta madura do `_comer_mundo`),
        sem decisao e sem andar. Nao e contato. Chega ao cerebro so pelo gancho opcional `fruta_na_mao(tipo, obs_antes, obs_depois)`."""
        tick = self._estado.tick
        if self._estado.dormindo:
            raise RuntimeError(f"fruta na mao com o pet dormindo (tick {tick}): o dono da a fruta com o pet acordado")
        tm = self._tm(tick)
        self.mundo.atualizar(tm)                           # a percepcao de antes e de depois e a do mundo no tick
        antes = self._observacao_depois_mundo()
        e = self._estado
        fome = min(1.0, e.fome + self.cmf.nutricao_fruta)
        humor = min(1.0, max(0.0, e.humor + self.efeito_frutas[f]))
        self._estado = replace(e, fome=fome, humor=humor)
        reg = {"tick": tm, "id": None, "tipo": f, "origem": "dono", "tick_posta": tm, "situacao": "madura", "como": "mao",
               "fome_antes": e.fome, "humor_antes": e.humor, "fome_depois": fome, "humor_depois": humor}
        if self.cpal.ligada:
            reg["perfil"] = self.perfil_de(f)                  # o Paladar: a fruta na mao e sempre madura
        self.consumos_mundo.append(reg)
        self._n_eventos += 1                                # e um evento do log, mas NAO e contato
        self._estimulo_mao(f)
        gancho = getattr(self._pm_cerebro(), "fruta_na_mao", None)
        if gancho is not None:
            gancho(f, antes, self._observacao_depois_mundo())

    def _estimulo_mao(self, f: str) -> None:
        """o lugar do corpo (o MotorCorpo o troca pelo estimulo da fruta madura); sem o corpo, nada"""

    def _trocar_arvores(self, x: str, y: str) -> None:
        """A troca de tipo por arvore (o teste 2): o mundo anda ate o tick e as arvores dos tipos x e y trocam. Nao e contato."""
        tm = self._tm(self._estado.tick)
        self.mundo.atualizar(tm)
        self.mundo.trocar_tipos(x, y, tm)
        self._n_eventos += 1

    def _parar_arvores(self, tipo: str) -> None:
        """O J5, adendo 8: o mundo anda ate o tick, as arvores do tipo param e as frutas caidas delas saem. Nao e contato."""
        tm = self._tm(self._estado.tick)
        self.mundo.atualizar(tm)
        self.mundo.parar_arvores(tipo, tm)
        self._n_eventos += 1

    def deixar_comida(self, tipo: str, x: int, y: int) -> None:
        if not self.cmf.ligada:
            raise MundoSemChave("deixar_comida com ConfigMundo.ligada = False")
        evento = evento_deixar_comida(self._estado.tick, tipo, x, y)     # valida tipo e posicao antes do log
        self._log.anexar(evento)
        self._aplicar_deixar_comida(*ler_deixar_comida(evento))

    def deixar_fruta(self, tipo: str, x: int, y: int) -> None:
        """a fruta ao lado da racao (ConfigFrutaAoLado): fora do orcamento (o canal nao a ve) e sem contato"""
        if not (self.cmf.ligada and self.cfal.ligada):
            raise MundoSemChave("deixar_fruta sem o mundo e a ConfigFrutaAoLado ligados")
        evento = evento_deixar_fruta(self._estado.tick, tipo, x, y)      # valida tipo e posicao antes do log
        self._log.anexar(evento)
        self._aplicar_deixar_fruta(*ler_deixar_fruta(evento))

    def deixar_bola(self, x: int, y: int) -> None:
        if not self.cmf.ligada:
            raise MundoSemChave("deixar_bola com ConfigMundo.ligada = False")
        evento = evento_deixar_bola(self._estado.tick, x, y)
        self._log.anexar(evento)
        self._aplicar_deixar_bola(*ler_deixar_bola(evento))

    def _aplicar_deixar_comida(self, tipo: str, x: int, y: int) -> None:
        if not self.cmf.ligada:
            raise MundoSemChave("deixar_comida com ConfigMundo.ligada = False")
        tick = self._estado.tick
        c = self.mundo.deixar_comida(tipo, x, y, self._tm(tick))
        self.deixadas.append({"tick": self._tm(tick), "id": c["id"], "tipo": tipo, "x": x, "y": y, "pet": self.pet})
        # contato, como o alimentar de hoje: zera o tempo sem cuidado, soma um cuidado, vinculo e politica recebem `alimentar`
        self._contato(AcaoUsuario.ALIMENTAR, tick)

    def _aplicar_deixar_fruta(self, tipo: str, x: int, y: int) -> None:
        """A fruta ao lado: a racao de referencia e a ultima racao deixada pelo dono neste tick (sem ela, falha alto: a fruta vai logo
        depois da racao, no mesmo passo). Sem contato e fora do orcamento (o evento e do log, como o deixar_bola)."""
        if not (self.cmf.ligada and self.cfal.ligada):
            raise MundoSemChave("deixar_fruta sem o mundo e a ConfigFrutaAoLado ligados")
        tm = self._tm(self._estado.tick)
        racao = next((d for d in reversed(self.deixadas) if d["tick"] == tm and d["tipo"] == "racao"), None)
        if racao is None:
            raise ValueError(f"fruta ao lado sem racao deixada no tick {tm}: a fruta vai logo depois da racao, no mesmo passo")
        c = self.mundo.deixar_fruta_ao_lado(tipo, x, y, tm)
        self.frutas_ao_lado.append({"tick": tm, "id": c["id"], "tipo": tipo, "x": x, "y": y, "racao": racao["id"]})
        self._n_eventos += 1                     # e um evento do log, mas NAO e contato

    def ao_lado_no_chao(self) -> dict[str, int]:
        """as frutas ao lado maduras no chao agora, por tipo (o que o dono olha para repor)"""
        t = self._tm(self._estado.tick)
        n = {f: 0 for f in self.cfal.tipos}
        for c in self.mundo.comidas.values():
            if c["origem"] == ORIGEM_AO_LADO and self.mundo.situacao(c, t) == "madura":
                n[c["tipo"]] += 1
        return n

    def _aplicar_deixar_bola(self, x: int, y: int) -> None:
        if not self.cmf.ligada:
            raise MundoSemChave("deixar_bola com ConfigMundo.ligada = False")
        self.mundo.deixar_bola(x, y, self._tm(self._estado.tick))
        self._n_eventos += 1                     # e um evento do log, mas NAO e contato (o por_bola de hoje)

    # ------------------------------------------------------------ leitura
    def estado(self) -> dict:
        d = super().estado()
        if not self.cmf.ligada:
            return d                             # desligado: o estado() do MotorFrutas, sem chave nova
        t = self._tm(self._estado.tick)
        d["mundo"] = {"pet": self.pet, "regiao": self.cmf.layout.regioes[regiao_de(self.pet[0], self.cmf)][0],
                      "bola": self.mundo.bola_em(t),
                      "comidas": sum(1 for c in self.mundo.comidas.values() if self.mundo.situacao(c, t) is not None)}
        if self.cbh.ligada:
            d["banheiro"] = {"alivios": len(self.alivios), "alivios_dentro": self.alivios_dentro,
                             "necessidades": len(self.mundo.necessidades), "na_zona": self.necessidades_na_zona()}
        if self.cfal.ligada:
            d["fruta_ao_lado"] = {"no_chao": self.ao_lado_no_chao(), "postas": len(self.frutas_ao_lado)}
        return d

    def resumo_mundo_fisico(self) -> dict:
        """tudo o que o mundo e o pet guardam (o G1 compara isto bit a bit); as mesmas chaves de antes da separacao do Mundo"""
        m = self.mundo
        return {"pet": self.pet, "bola": dict(m.bola), "comidas": [dict(c) for c in m.comidas.values()],
                "prox_id": m.prox_id, "passo_mundo": m.passo_mundo,
                "arvores": [dict(a) for a in m.arvores],
                "pendente": None if self._pendente is None else {"acao": self._pendente["acao"].value,
                                                                 "alvo": self._pendente["alvo"].para_dict()},
                "rngs": [r.getstate() for r in (m.rng_arvores, m.rng_bola, self._rng_sujeira, self._rng_alvo)],
                "quedas": m.quedas, "consumos": self.consumos_mundo, "sumidas": m.sumidas, "deixadas": self.deixadas,
                "bolas_deixadas": m.bolas_deixadas, "rolagens": m.rolagens, "decisoes": self.decisoes_mundo,
                "regioes": self.regioes, "visitas": self.visitas,
                "manchas_abertas": [dict(v) for v in self._manchas_abertas.values()],
                **({} if not self.cbh.ligada else {
                    "necessidades": [dict(n) for n in m.necessidades.values()], "prox_necessidade": m.prox_necessidade,
                    "recolhidas": m.recolhidas, "alivios": self.alivios, "recolhas": self.recolhas,
                    "idas_banheiro": self.idas_banheiro}),
                **({} if not self.cpq.ligada else {"troncos_vistos": dict(self.troncos_vistos), "trocas_tipo": m.trocas_tipo}),
                **({} if m.paradas_arvores is None else {"paradas_arvores": m.paradas_arvores}),
                **({} if not self.cfal.ligada else {"frutas_ao_lado": self.frutas_ao_lado})}

    # ------------------------------------------------------------ o avanco em ticks (o grupo, dois pets, etapa 2)
    # O `_avancar(n)` de hoje e: o que cada classe faz uma vez por avanco (o MotorPersonalidade conta o evento de avanco no indice dos
    # eventos; o MotorEducacao confere a morte no fim) em volta do laco de n ticks do engine. O grupo intercala os ticks dos pets, entao
    # chama as tres partes separadas: `_abrir_avanco`, `_um_tick` n vezes e `_fechar_avanco`. Com um pet, e o `_avancar(n)` byte a byte
    # (o G2 do grupo); tests/test_grupo.py confere que nenhuma classe da cadeia tem outro `_avancar`.
    def resumo_social(self) -> dict:
        """os registros sociais do pet (so no grupo; o G1 do grupo compara)"""
        return {"viu_comer": self._viu_comer, "toques": self._toques, "vistos_comer": self.vistos_comer,
                "idas_onde_comeu": self.idas_onde_comeu, "a_vista": self.a_vista, "decisoes_no_grupo": self.decisoes_no_grupo}

    def _abrir_avanco(self) -> None:
        self._n_eventos += 1                     # o MotorPersonalidade._avancar

    def _um_tick(self) -> None:
        Motor._avancar(self, 1)                  # o laco do engine, um tick (decide se for a hora, e anda o tick)

    def _fechar_avanco(self) -> None:
        self._conferir_morte(self._estado.tick)  # o MotorEducacao._avancar (com as lesoes desligadas, nada)


# ================================================================== replay
def reproduzir_mundo(log: LogDeEventos, politica_fabrica: Callable, cfg: Config | None = None, semente: int = 42,
                     fabrica_motor: Callable | None = None, ate_tick: int | None = None) -> MotorMundo:
    """O replay que entende os eventos do mundo (`deixar_comida`, `deixar_bola`). `ate_tick`: para antes do primeiro evento nesse
    tick (corta o avanco que o atravessa), como o reproduzir_educacao. Evento desconhecido levanta erro; luta, origem, fala e
    decisao externa tambem: o mundo minimo roda sem educacao e sem lesoes."""
    cfg = cfg or CONFIG_PADRAO
    if fabrica_motor is None:
        raise ValueError("reproduzir_mundo precisa da fabrica do MotorMundo")
    motor = fabrica_motor(politica_fabrica(cfg), cfg, semente)
    if not isinstance(motor, MotorMundo):
        raise TypeError(f"a fabrica devolveu {type(motor).__name__}, nao MotorMundo")
    for evento in log:
        if ate_tick is not None and evento.tick >= ate_tick:
            break
        if evento.tipo == "avanco":
            motor._avancar(int(evento.valor) if ate_tick is None else min(int(evento.valor), ate_tick - evento.tick))
        elif evento.tipo == "acao_usuario":
            motor._aplicar_acao_usuario(AcaoUsuario(evento.valor))
        elif evento.tipo == "deixar_comida":
            motor._aplicar_deixar_comida(*ler_deixar_comida(evento))
        elif evento.tipo == "deixar_bola":
            motor._aplicar_deixar_bola(*ler_deixar_bola(evento))
        elif evento.tipo == "deixar_fruta":
            motor._aplicar_deixar_fruta(*ler_deixar_fruta(evento))
        else:
            raise ValueError(f"tipo de evento desconhecido no log do mundo: {evento.tipo!r}")
    motor._log = LogDeEventos([e for e in log if ate_tick is None or e.tick < ate_tick])
    return motor


def fabricas_mundo(cfg_mundo: ConfigMundo | None = None, politica_fabrica: Callable | None = None,
                   temperamento: Temperamento = NEUTRO, especie: str = "brasa", efeito_frutas: dict | None = None, **kw):
    """(fabrica da politica, fabrica do motor) de uma vida com o mundo, no desenho do plano (secao 2): obediencia, educacao, lesoes,
    frutas e bola desligadas. A politica padrao e o instinto com o gancho vazio do dono (o instinto do mundo e do chat B, etapa 3).
    Reusadas no replay."""
    cm = cfg_mundo or CONFIG_MUNDO_LIGADA
    fp = politica_fabrica or (lambda cfg=None: PoliticaInstintoBola(cfg, CONFIG_BOLA))  # noqa: E731
    fm = (lambda politica, cfg, s: MotorMundo(politica, cfg, s, temperamento, especie, obediencia_desligada=True,  # noqa: E731
                                              cfg_mundo=cm, efeito_frutas=efeito_frutas, **kw))
    return fp, fm


# ================================================================== o dono
@dataclass(frozen=True)
class DeixarComida:
    tipo: str
    x: int
    y: int


@dataclass(frozen=True)
class DeixarFruta:
    tipo: str
    x: int
    y: int


@dataclass(frozen=True)
class DeixarBola:
    x: int
    y: int


ESTILOS_LUGAR = ("comedouro", "perto", "longe")


class DonoComLugar:
    """Embrulha um dono sintetico (secao 4): o `alimentar` vira `deixar_comida("racao", x, y)` no lugar do estilo. A rng do lugar e
    `derivar_semente("dono-lugar", semente, rotulo_dono)`, sem o braco: P0 e P1 sorteiam os mesmos desvios. Um sorteio fixo por
    `alimentar` em cada estilo (perto e longe: direcao e distancia; comedouro: nenhum)."""

    def __init__(self, base, estilo: str, semente: int, rotulo_dono: str, cfg_mundo: ConfigMundo | None = None) -> None:
        if estilo not in ESTILOS_LUGAR:
            raise ValueError(f"estilo de lugar desconhecido: {estilo!r} (opcoes: {ESTILOS_LUGAR})")
        self.base = base
        self.estilo = estilo
        self.nome = getattr(base, "nome", rotulo_dono)
        self.cmf = cfg_mundo or CONFIG_MUNDO_LIGADA
        self._rng = random.Random(derivar_semente("dono-lugar", semente, rotulo_dono))
        self.lugares: list[dict] = []

    def lugar(self, estado: dict) -> tuple[int, int]:
        m = estado.get("mundo")
        if m is None:
            raise ValueError("o DonoComLugar precisa do estado() do MotorMundo ligado (chave `mundo`)")
        cm = self.cmf
        if self.estilo == "comedouro":
            return centro_da_celula(cm.layout.comedouro, cm)
        px, py = m["pet"]
        direcao = self._rng.randrange(16)
        if self.estilo == "perto":
            r = self._rng.randrange(cm.perto_max_celulas * cm.sub + 1)
        else:
            r = self._rng.randint(cm.longe_min_celulas * cm.sub, cm.longe_max_celulas * cm.sub)
        return deslocar(px, py, direcao, r, cm)

    def decidir(self, visao: Visao, rng: random.Random) -> list:
        saida = []
        for acao in self.base.decidir(visao, rng):
            if acao is AcaoUsuario.ALIMENTAR:
                x, y = self.lugar(visao.estado)
                self.lugares.append({"tick": visao.estado["tick"], "x": x, "y": y, "pet": visao.estado["mundo"]["pet"]})
                saida.append(DeixarComida("racao", x, y))
            else:
                saida.append(acao)
        return saida


class DonoFrutaAoLado:
    """A fruta ao lado da racao (o RP-2 de docs/futuro/paladar.md; ConfigFrutaAoLado): depois de cada racao que o `DonoComLugar` deixa no
    comedouro, no mesmo passo, o dono poe ao lado as frutas que faltam (as de cada tipo abaixo do `teto_por_tipo` de maduras ao lado no
    chao), fora do orcamento e sem contato, pelo `simular_vida_mundo(..., ao_lado=)`. As celulas sao a coluna do comedouro + `coluna`, nas
    linhas do comedouro + `linhas` (os centros, cortados ao mapa); o tipo de cada linha sai de uma permutacao de `tipos` sorteada uma vez
    na construcao pela rng propria `derivar_semente("fruta-ao-lado", semente)` (um `shuffle`), fixa na vida. So com o DonoComLugar no
    estilo `comedouro`: com `perto` ou `longe` a racao nao fica no comedouro, e "ao lado" nao teria sentido. Le so o estado() do motor
    (`fruta_ao_lado.no_chao`) e os lugares do proprio dono. Os depositos (tick, tipo, x, y, a racao) ficam em `depositos`."""

    def __init__(self, dono: DonoComLugar, semente: int, cfg: ConfigFrutaAoLado, cfg_mundo: ConfigMundo | None = None) -> None:
        if not isinstance(dono, DonoComLugar) or dono.estilo != "comedouro":
            raise ValueError("a fruta ao lado precisa do DonoComLugar no estilo `comedouro` (a racao no comedouro)")
        if not cfg.ligada:
            raise ValueError("DonoFrutaAoLado com a ConfigFrutaAoLado desligada")
        self.dono, self.cfg = dono, cfg
        cm = cfg_mundo or dono.cmf
        self.permutacao = list(cfg.tipos)
        random.Random(derivar_semente("fruta-ao-lado", semente)).shuffle(self.permutacao)
        cx, cy = cm.layout.comedouro
        self.celulas = {f: no_mapa(*centro_da_celula((cx + cfg.coluna, cy + dy), cm), cm) for f, dy in zip(self.permutacao, cfg.linhas)}
        self._vistos = 0                                  # os lugares do dono ja olhados
        self.depositos: list[dict] = []

    def acoes(self, estado: dict) -> list[DeixarFruta]:
        fal = estado.get("fruta_ao_lado")
        if fal is None:
            raise ValueError("o DonoFrutaAoLado precisa do estado() do MotorMundo com a ConfigFrutaAoLado ligada (chave `fruta_ao_lado`)")
        novos = self.dono.lugares[self._vistos:]
        self._vistos = len(self.dono.lugares)
        if not novos:
            return []
        if any(lg["tick"] != estado["tick"] for lg in novos):
            raise RuntimeError("racao de outro passo sem a fruta ao lado: a regra roda em todo passo, logo depois do dono")
        racao = novos[-1]
        no_chao = dict(fal["no_chao"])
        saida = []
        for f in self.cfg.tipos:
            if no_chao[f] < self.cfg.teto_por_tipo:
                x, y = self.celulas[f]
                saida.append(DeixarFruta(f, x, y))
                no_chao[f] += 1
                self.depositos.append({"tick": estado["tick"], "tipo": f, "x": x, "y": y, "racao": (racao["x"], racao["y"])})
        return saida


class DonoCarinhoBanheiro:
    """O dono que acaricia depois do banheiro (secao 5): depois de cada `aliviar` DENTRO do banheiro, um `acariciar` no primeiro passo
    do dono depois do alivio (o momento do K4), fora do orcamento (BN-2), pelo canal do mundo do `simular_vida_mundo(..., carinho=)`.
    Fora do banheiro, nada (nem bronca nem tapa). Le so o que o motor mostra no estado() (`banheiro.alivios_dentro`). Com uma decisao a
    cada 15 ticks e o passo do dono de 15, a ultima decisao antes do carinho e o `aliviar`: o cerebro o recebe pelo corpo (CD-4) e o credita
    a ela (G-CRED). Os ticks dos carinhos ficam em `ticks`."""

    def __init__(self) -> None:
        self.vistos = 0
        self.ticks: list[int] = []

    @property
    def feitos(self) -> int:
        return len(self.ticks)

    def acoes(self, estado: dict) -> list[AcaoUsuario]:
        b = estado.get("banheiro")
        if b is None:
            raise BanheiroSemMundo("o DonoCarinhoBanheiro precisa do estado() do MotorMundo com o banheiro (chave `banheiro`)")
        novos = b["alivios_dentro"] - self.vistos
        if novos < 0:
            raise RuntimeError(f"alivios dentro do banheiro voltaram: {b['alivios_dentro']} < {self.vistos}")
        self.vistos = b["alivios_dentro"]
        self.ticks += [estado["tick"]] * novos
        return [AcaoUsuario.ACARICIAR] * novos


class CanalMundo(CanalDeInteracao):
    """O CanalDeInteracao com os gestos do mundo: `DeixarComida` e `DeixarBola` gastam orcamento como qualquer acao do dono."""

    def aplicar(self, acoes: list, passo: int, passos_totais: int) -> None:
        minimo, maximo = self.limites(passo, passos_totais)
        if len(acoes) > maximo:
            raise OrcamentoExcedido(f"passo {passo}: dono pediu {len(acoes)} interacoes, maximo {maximo} "
                                    f"(gasto {self.gasto}/{self.orcamento})")
        if len(acoes) < minimo:
            raise OrcamentoNaoConsumido(f"passo {passo}: dono fez {len(acoes)} interacoes, minimo {minimo} "
                                        f"para fechar o orcamento")
        for acao in acoes:
            if isinstance(acao, DeixarComida):
                self.motor.deixar_comida(acao.tipo, acao.x, acao.y)
            elif isinstance(acao, DeixarBola):
                self.motor.deixar_bola(acao.x, acao.y)
            elif isinstance(acao, AcaoUsuario):
                aceita = getattr(self.motor, "aceita", None)
                if aceita is not None and not aceita(acao):
                    self.rejeitados += 1
                    continue
                self.motor.observar(acao)
            else:
                raise TypeError(f"acao invalida vinda do dono: {acao!r}")
            self.gasto += 1


def simular_vida_mundo(braco: str, dono, politica, semente: int, dias: int, orcamento: int, fabrica_motor: Callable,
                       cfg: Config | None = None, cfg_donos: ConfigDonos | None = None, rotulo_dono: str | None = None,
                       canal_classe: type | None = None, carinho: DonoCarinhoBanheiro | None = None,
                       ao_lado: DonoFrutaAoLado | None = None) -> Vida:
    """treino.simular_vida com o CanalMundo: o dono (embrulhado pelo DonoComLugar) deixa a comida e a bola pelos gestos do mundo, que
    gastam o orcamento. A rng do dono e a de sempre (`dono`, semente, rotulo). `canal_classe` troca o canal (o CanalMundoComGestos de
    digilab/gestos.py, com o DonoComGestos); o padrao e o CanalMundo. `carinho` (o DonoCarinhoBanheiro): os carinhos depois do banheiro,
    logo depois das acoes do dono no passo e fora do orcamento (BN-2; o `interacoes` da Vida nao os conta)."""
    cfg = cfg or CONFIG_PADRAO
    cfg_donos = cfg_donos or CONFIG_DONOS
    total = dias * TICKS_POR_DIA
    if total % cfg_donos.passo_ticks != 0:
        raise ValueError("duracao nao e multipla do passo do dono")
    passos = total // cfg_donos.passo_ticks
    motor = fabrica_motor(politica, cfg, semente)
    if not isinstance(motor, MotorMundo) or not motor.cmf.ligada:
        raise ValueError("simular_vida_mundo precisa do MotorMundo com o mundo ligado")
    rng_dono = random.Random(derivar_semente("dono", semente, rotulo_dono or braco))
    canal = (canal_classe or CanalMundo)(motor, orcamento, cfg_donos.max_interacoes_por_passo)
    for passo in range(passos):
        motor.avancar(cfg_donos.passo_ticks)
        minimo, maximo = canal.limites(passo, passos)
        visao = Visao(estado=motor.estado(), passo=passo, passos_totais=passos, orcamento=orcamento, gasto=canal.gasto,
                      minimo_obrigatorio=minimo, maximo_permitido=maximo)
        canal.aplicar(dono.decidir(visao, rng_dono), passo, passos)
        if carinho is not None:
            for acao in carinho.acoes(motor.estado()):
                motor.observar(acao)
        if ao_lado is not None:                  # a fruta ao lado da racao: logo depois das acoes do dono do passo, fora do orcamento
            for acao in ao_lado.acoes(motor.estado()):
                motor.deixar_fruta(acao.tipo, acao.x, acao.y)
    canal.fechar()
    return Vida(braco=braco, semente_coorte=semente, motor=motor, interacoes=canal.gasto)
