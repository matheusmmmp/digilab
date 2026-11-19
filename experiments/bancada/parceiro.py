"""O parceiro sob intervencao (docs/ESPEC_V3_SOCIAL_PAR_E1.md, APROVADA pelo Matheus em 2026-11-17, "Aprovo a E1"): so a bancada do Python.

Tres condicoes para o parceiro P de um pet focal F, na mesma semente do grupo e no mesmo mundo (a investigacao, secao 3.1):
  VIVO   P de verdade, com o cerebro dele
  GRAV   P reexecuta, decisao a decisao, as decisoes que tomou na vida VIVO sem perturbacao da mesma semente (Froese e Di Paolo 2008,
         10.1007/978-3-540-69134-1_6, adaptado: grava-se a decisao, nao a posicao; o motor de P anda, come e chuta pela fisica de hoje)
  OUTRA  P reexecuta as decisoes de uma vida da mesma semente em que F foi trocado por um pet passivo

A perturbacao: no tick t0, F e levado a d0 celulas de P pelo `Grupo.levar_pet` (a origem `intervencao`). Sem ela, a GRAV e a VIVO decisao a
decisao (o G-GRAV-IDENT): o motor e deterministico, e o mesmo F diante das mesmas decisoes de P vive a mesma vida.

O laco aberto (E1-1, E1-2): a `PoliticaGravada` nao le a observacao para decidir. O alvo gravado e o ALVO RESOLVIDO (o do cerebro, ou o
padrao do motor quando o cerebro devolveu None); na reexecucao, se ele esta entre os candidatos de agora (o mesmo tipo, id e ponto),
ele e devolvido; se nao, P vai ao ponto gravado (o motor aceita um ponto em toda acao com alvo so pela ConfigIntervencaoSocial,
`MotorMundo.aceitar_ponto_gravado`), e o caso conta como desvio. Assim P so vai aonde foi na vida gravada: um alvo que se move com F (o
`seguir`) ou que F pode mover (a bola) nunca e seguido ao vivo. O dono de P na GRAV e na OUTRA e o gravado (E1-3): os eventos dele sao
rejogados nos mesmos ticks, e o dono sintetico de P nao roda.

Os controles positivos (E1-6 e o adendo 1, A1-1 a A1-3), so aqui, nunca no pacote `digilab/` nem no jogo: o `Seguidor` (no tempo livre,
explora com o alvo `seguir` quando ve o outro), o `Evitador` (no tempo livre, foge um passo inteiro para o lado oposto ao outro visto) e o
`Passivo` (so fica ocioso ou dorme).

So biblioteca padrao.
"""
from __future__ import annotations

import random
import types
from dataclasses import dataclass, field
from typing import Callable

from digilab.config import CONFIG_DONOS, CONFIG_GRUPO_LIGADA, CONFIG_INTERVENCAO_SOCIAL_LIGADA, CONFIG_PADRAO, TICKS_POR_DIA
from digilab.config import ConfigIntervencaoSocial, ConfigMundo
from digilab.donos import Visao
from digilab.events import AcaoPet, AcaoUsuario
from digilab.grupo import ORIGEM_DONO, Grupo, sementes_do_grupo
from digilab.instinto_mundo import PoliticaInstintoMundo
from digilab.mundo import Alvo, CanalMundo, celula_de, deslocar, direcao_do_golpe
from digilab.protocol import derivar_semente

ROTULO_INTERVENCAO = "intervencao-social"        # o fluxo do t0 e da direcao (a espec, 2.3)
CONDICOES = ("VIVO", "GRAV", "OUTRA")
TIPOS_DONO = ("acao_usuario", "deixar_comida", "deixar_bola")


# ================================================================== a gravacao
@dataclass(frozen=True)
class DecisaoGravada:
    """uma decisao de P: a acao do cerebro e, nas acoes com alvo, o alvo resolvido (o do cerebro, ou o padrao do motor)"""

    indice: int
    acao: AcaoPet
    acao_alvo: AcaoPet | None = None           # a acao com que o motor pediu o alvo (None: o motor nao pediu)
    alvo: Alvo | None = None

    def para_dict(self) -> dict:
        """a decisao em JSON (o A0 guarda as gravacoes em disco para o G1; docs/PLANO_ANALISE_V3_SOCIAL_PAR_A0.md, secao 4, item 5)"""
        return {"indice": self.indice, "acao": self.acao.value, "acao_alvo": None if self.acao_alvo is None else self.acao_alvo.value,
                "alvo": None if self.alvo is None else self.alvo.para_dict()}

    @staticmethod
    def de_dict(d: dict) -> "DecisaoGravada":
        if set(d) != {"indice", "acao", "acao_alvo", "alvo"}:
            raise ValueError(f"decisao gravada com os campos {sorted(d)}")
        alvo = d["alvo"]
        if alvo is not None and set(alvo) != {"tipo", "x", "y", "id", "de"}:
            raise ValueError(f"alvo gravado com os campos {sorted(alvo)}")
        return DecisaoGravada(d["indice"], AcaoPet(d["acao"]), None if d["acao_alvo"] is None else AcaoPet(d["acao_alvo"]),
                              None if alvo is None else Alvo(**alvo))


class Gravador:
    """Embrulha a politica viva de P SEM muda-la (como a `Coleta` da bancada da cooperacao): troca so os metodos da instancia, guarda
    cada decisao e devolve o que a politica devolveria. O motor e posto depois da entrada (`gravador.motor = ...`), para o padrao."""

    def __init__(self, politica) -> None:
        self.politica = politica
        self.motor = None
        self.decisoes: list[DecisaoGravada] = []
        agir0 = politica.agir
        escolher0 = getattr(politica, "escolher_alvo", None)
        grav = self

        def agir(_self, obs, rng):
            acao = agir0(obs, rng)
            grav.decisoes.append(DecisaoGravada(len(grav.decisoes), acao))
            return acao

        def escolher_alvo(_self, acao, candidatos, percepcao, u):
            alvo = None if escolher0 is None else escolher0(acao, candidatos, percepcao, u)
            resolvido = alvo if alvo is not None else grav.motor.alvo_padrao(acao, list(candidatos))
            ult = grav.decisoes[-1]
            if ult.acao_alvo is not None:
                raise RuntimeError(f"o motor pediu o alvo duas vezes na decisao {ult.indice}")
            grav.decisoes[-1] = DecisaoGravada(ult.indice, ult.acao, acao, resolvido)
            return alvo

        politica.agir = types.MethodType(agir, politica)
        politica.escolher_alvo = types.MethodType(escolher_alvo, politica)


class PoliticaGravada:
    """O parceiro em laco aberto (a docstring do modulo). `agir` nao le a observacao; `escolher_alvo` so confere se o alvo gravado esta
    entre os candidatos de agora, e le a posicao do proprio pet so no caso `parado` (o alvo gravado era None e agora ha candidatos)."""

    nome = "gravada"

    def __init__(self, decisoes: list[DecisaoGravada]) -> None:
        if [d.indice for d in decisoes] != list(range(len(decisoes))):
            raise ValueError("a gravacao tem de vir com os indices 0..n-1, na ordem")
        self.decisoes = list(decisoes)
        self._i = 0
        self._atual: DecisaoGravada | None = None
        self.desvios: list[tuple[int, str]] = []

    def agir(self, obs, rng) -> AcaoPet:
        if self._i < len(self.decisoes):
            self._atual = self.decisoes[self._i]
            acao = self._atual.acao
        else:
            self._atual = None
            self.desvios.append((self._i, "fim_da_gravacao"))
            acao = AcaoPet.OCIOSO
        self._i += 1
        return acao

    def escolher_alvo(self, acao, candidatos, percepcao, u):
        d = self._atual
        if d is None or d.alvo is None:
            if not candidatos:
                return None
            self.desvios.append((self._i - 1, "parado"))
            return Alvo.ponto(percepcao.x, percepcao.y)      # nao anda: o alvo gravado era nenhum
        if d.acao_alvo is not acao:
            self.desvios.append((d.indice, "acao_trocada"))
        if d.alvo in candidatos:
            return d.alvo
        if d.alvo.tipo == "ponto" and d.alvo.id is None and d.alvo.de is None:
            return d.alvo
        self.desvios.append((d.indice, "alvo_fora"))
        return Alvo.ponto(d.alvo.x, d.alvo.y)

    def observar(self, transicao) -> None:
        return None                                  # nao aprende

    def receber_acao_dono(self, acao, tick) -> None:
        """o gancho que os embrulhos do motor sempre chamam (o do instinto do mundo tambem e vazio): nada muda"""
        return None

    def estado_interno(self) -> dict:
        return {"nome": self.nome, "decisoes": len(self.decisoes), "lidas": self._i, "desvios": len(self.desvios)}


# ================================================================== os controles positivos (E1-6)
TEMPO_LIVRE = (AcaoPet.OCIOSO, AcaoPet.BRINCAR, AcaoPet.CHAMAR_ATENCAO, AcaoPet.EXPLORAR, AcaoPet.EMBURRAR)


class Seguidor(PoliticaInstintoMundo):
    """o instinto do mundo; no tempo livre com o outro a vista, explora com o alvo `seguir` (o primeiro outro visto)"""

    nome = "seguidor"

    def __init__(self, cfg=None) -> None:
        super().__init__(cfg)
        self._ve_outro = False

    def agir(self, obs, rng):
        acao = super().agir(obs, rng)
        self._ve_outro = obs.social is not None and bool(obs.social.outros)
        return AcaoPet.EXPLORAR if self._ve_outro and acao in TEMPO_LIVRE else acao

    def escolher_alvo(self, acao, candidatos, percepcao, u):
        if acao is AcaoPet.EXPLORAR and self._ve_outro:
            return next((c for c in candidatos if c.tipo == "seguir"), None)
        return None


class Evitador(PoliticaInstintoMundo):
    """o instinto do mundo; no tempo livre com o outro a vista, explora para o ponto a um passo inteiro (o alcance de uma decisao) na
    direcao oposta ao outro: das 16, a mais alinhada com o vetor do outro para o pet (a `direcao_do_golpe`, a mesma conta inteira), e a 0
    com os dois no mesmo ponto (o adendo 1 da espec, 9.2, A1-2; o de antes fugia para 2 x o vetor e nao saia do lugar de perto)"""

    nome = "evitador"

    def __init__(self, cfg_mundo: ConfigMundo, cfg=None) -> None:
        super().__init__(cfg)
        self.cmf = cfg_mundo
        self._passo = cfg_mundo.velocidade * self.cfg.intervalo_decisao_ticks
        self._outro: tuple[int, int] | None = None

    def agir(self, obs, rng):
        acao = super().agir(obs, rng)
        outros = [] if obs.social is None else obs.social.outros
        self._outro = None if not outros else (outros[0][1], outros[0][2])
        return AcaoPet.EXPLORAR if self._outro is not None and acao in TEMPO_LIVRE else acao

    def escolher_alvo(self, acao, candidatos, percepcao, u):
        if acao is AcaoPet.EXPLORAR and self._outro is not None:
            dx, dy = self._outro                                 # o outro, relativo ao pet
            direcao = direcao_do_golpe(dx, dy, 0, 0)             # do outro para o pet
            return Alvo.ponto(*deslocar(percepcao.x, percepcao.y, 0 if direcao is None else direcao, self._passo, self.cmf))
        return None


class Estatua(PoliticaInstintoMundo):
    """o pet focal dos controles do adendo 2 (docs/ESPEC_V3_SOCIAL_PAR_E1.md, 10.1, A2-2): sempre ocioso, nunca se move nem dorme"""

    nome = "estatua"

    def agir(self, obs, rng):
        return AcaoPet.OCIOSO


class SeguidorPuro(PoliticaInstintoMundo):
    """o adendo 2 (10.1, A2-1): ve o outro, explora com o alvo `seguir`; nao ve, fica ocioso. Nao come, nao dorme, nao chama"""

    nome = "seguidor_puro"

    def __init__(self, cfg=None) -> None:
        super().__init__(cfg)
        self._ve_outro = False

    def agir(self, obs, rng):
        self._ve_outro = obs.social is not None and bool(obs.social.outros)
        return AcaoPet.EXPLORAR if self._ve_outro else AcaoPet.OCIOSO

    def escolher_alvo(self, acao, candidatos, percepcao, u):
        if acao is AcaoPet.EXPLORAR and self._ve_outro:
            return next(c for c in candidatos if c.tipo == "seguir")
        return None


class EvitadorPuro(Evitador):
    """o adendo 2 (10.1, A2-1): ve o outro, foge um passo inteiro (a conta do Evitador do adendo 1); nao ve, fica ocioso"""

    nome = "evitador_puro"

    def agir(self, obs, rng):
        outros = [] if obs.social is None else obs.social.outros
        self._outro = None if not outros else (outros[0][1], outros[0][2])
        return AcaoPet.EXPLORAR if self._outro is not None else AcaoPet.OCIOSO


class Passivo(PoliticaInstintoMundo):
    """um parceiro que nao mexe no mundo: so fica ocioso ou dorme (o de tests/test_grupo.py:71-80)"""

    nome = "passivo"

    def agir(self, obs, rng):
        a = super().agir(obs, rng)
        return a if a is AcaoPet.DORMIR else AcaoPet.OCIOSO


# ================================================================== a vida do par
@dataclass(frozen=True)
class Membro:
    """um pet do par: `tipo` vivo (a fabrica do cerebro e o dono sintetico) ou gravado (a gravacao e os eventos do dono gravados)"""

    ident: str
    tipo: str                                    # "vivo" | "gravado"
    fabrica_motor: Callable
    fabrica_cerebro: Callable | None = None      # vivo: (cfg) -> politica
    dono: object = None                          # vivo: o dono sintetico (DonoComLugar); None = sem dono
    rotulo_dono: str = "sem_dono"
    rotulo_cerebro: str = ""
    gravacao: list = field(default_factory=list)          # gravado: as DecisaoGravada
    eventos_dono: list = field(default_factory=list)      # gravado: [EventoGrupo] do dono deste pet, na ordem
    gravar: bool = False                          # vivo: guardar as decisoes (o Gravador)


@dataclass
class VidaPar:
    """o que sai de uma vida do par"""

    grupo: Grupo
    passos: list[int]                             # o tick do mundo no fim de cada passo do dono
    posicoes: dict[str, list[tuple[int, int]]]    # pet -> a posicao no fim de cada passo
    gravacoes: dict[str, list[DecisaoGravada]]    # pet -> as decisoes guardadas (so os vivos com `gravar`)
    desvios: dict[str, list[tuple[int, str]]]     # pet -> os desvios da reexecucao (so os gravados)
    t0: int | None = None                         # o tick da perturbacao, ou None
    levado: str | None = None
    no_t0: dict | None = None                     # o mundo no passo da perturbacao, logo antes do levar (o descritivo do A0, secao 8)


def eventos_do_dono(grupo: Grupo, ident: str) -> list:
    """os eventos do dono do pet `ident` no registro do grupo, na ordem (a gravacao do dono, E1-3)"""
    return [e for e in grupo.registro.eventos if e.pet == ident and e.origem == ORIGEM_DONO and e.tipo in TIPOS_DONO]


def _aplicar_evento_dono(g: Grupo, e) -> None:
    if e.tipo == "acao_usuario":
        g.acao_dono(e.pet, AcaoUsuario(e.valor))
    elif e.tipo == "deixar_comida":
        tipo, x, y = str(e.valor).split("|")
        g.deixar_comida(e.pet, tipo, int(x), int(y))
    elif e.tipo == "deixar_bola":
        x, y = str(e.valor).split("|")
        g.deixar_bola(e.pet, int(x), int(y))
    else:
        raise ValueError(f"evento do dono desconhecido: {e}")


def sortear_perturbacao(semente: int, tick_min: int, tick_max: int, passo: int) -> tuple[int, int]:
    """(o t0, a direcao 0..15) do fluxo `intervencao-social` da semente do grupo, sorteados antes da vida; o t0 num passo do dono"""
    if tick_min % passo or tick_max % passo or not 0 < tick_min <= tick_max:
        raise ValueError(f"a janela do t0 em passos do dono: {tick_min}, {tick_max}, {passo}")
    rng = random.Random(derivar_semente(ROTULO_INTERVENCAO, semente))
    t0 = tick_min + passo * rng.randrange((tick_max - tick_min) // passo + 1)
    return t0, rng.randrange(16)


@dataclass(frozen=True)
class IntervencaoT0:
    """A intervencao do experimento no t0, generalizada (SOCIAL_PAR S: docs/PLANO_ANALISE_V3_SOCIAL_PAR_S.md, secao 2): no primeiro passo
    com o tick >= `t0` em que todos os `acordados` estao acordados, `aplicar(g)` roda uma vez (o `levar_pet` e o `deixar_bola_intervencao`
    do grupo, com a origem `intervencao`). `levado` e o pet que a medida trata como focal (o `VidaPar.levado`). A `perturbacao` de tupla
    (a E1 e o A0) continua sendo o caminho deles, byte a byte."""
    t0: int
    acordados: tuple[str, ...]
    aplicar: Callable
    levado: str | None = None


def viver_par(cfg_mundo: ConfigMundo, semente: int, membros: list[Membro], dias: int, perturbacao: tuple | None = None,
              cfg=None, cfg_intervencao: ConfigIntervencaoSocial = CONFIG_INTERVENCAO_SOCIAL_LIGADA, cfg_cooperacao=None,
              intervencao: IntervencaoT0 | None = None) -> VidaPar:
    """O laco do `simular_grupo` (digilab/grupo.py) para um par nascido junto no tick 0, com o membro gravado e a perturbacao.
    `perturbacao` = (quem e levado, a referencia (o outro), t0, direcao, d0 em celulas): no primeiro passo >= t0 em que quem e levado esta
    acordado, ele vai para d0 celulas da referencia, na direcao. Sem perturbacao e com dois vivos, e o `simular_grupo` byte a byte (o G2)."""
    cfg = cfg or CONFIG_PADRAO
    cd = CONFIG_DONOS
    passo = cd.passo_ticks
    total = dias * TICKS_POR_DIA
    if {m.ident for m in membros} != set(CONFIG_GRUPO_LIGADA.ids):
        raise ValueError(f"o par tem os ids {CONFIG_GRUPO_LIGADA.ids}")
    g = Grupo(cfg_mundo, semente, CONFIG_GRUPO_LIGADA, cfg, cfg_cooperacao=cfg_cooperacao, cfg_intervencao=cfg_intervencao)
    por_id = sorted(membros, key=lambda m: m.ident)
    canais, rngs, passos_pet, gravadores, gravadas, pendentes = {}, {}, {}, {}, {}, {}
    for m in por_id:
        if m.tipo == "vivo":
            politica = m.fabrica_cerebro(cfg)
            if m.gravar:
                gravadores[m.ident] = Gravador(politica)
        elif m.tipo == "gravado":
            politica = gravadas[m.ident] = PoliticaGravada(m.gravacao)
            pendentes[m.ident] = list(m.eventos_dono)
        else:
            raise ValueError(f"membro desconhecido: {m.tipo!r}")

        def fm(pol, c, s, _fm=m.fabrica_motor, _grav=(m.tipo == "gravado"), **kw):
            motor = _fm(pol, c, s, **kw)
            if _grav:
                motor.aceitar_ponto_gravado(cfg_intervencao)
            return motor
        motor = g.entrar(m.ident, politica, fm, m.rotulo_cerebro or getattr(politica, "nome", ""), m.rotulo_dono)
        if m.ident in gravadores:
            gravadores[m.ident].motor = motor
        if m.tipo == "vivo" and m.dono is not None:
            passos_pet[m.ident] = total // passo
            orcamento = CONFIG_GRUPO_LIGADA.orcamento_por_dia * total // TICKS_POR_DIA
            canais[m.ident] = CanalMundo(g.pet(m.ident), orcamento, cd.max_interacoes_por_passo)
            rngs[m.ident] = random.Random(derivar_semente("dono", g.sementes[m.ident], m.rotulo_dono))
    passos, posicoes = [], {m.ident: [] for m in por_id}
    if perturbacao is not None and intervencao is not None:
        raise ValueError("a perturbacao (a tupla da E1 e do A0) e a IntervencaoT0 nao vao juntas")
    feita, t0_feito, no_t0 = perturbacao is None and intervencao is None, None, None
    for k in range(total // passo):
        t = k * passo
        g.avancar(passo)
        if not feita and perturbacao is not None and g.tick >= perturbacao[2]:
            quem, ref, _t0, direcao, d0 = perturbacao
            if not g.motores[quem]._estado.dormindo:
                no_t0 = retrato_do_mundo(g)
                rx, ry = g.motores[ref].pet
                x, y = deslocar(rx, ry, direcao, d0 * cfg_mundo.sub, cfg_mundo)
                g.levar_pet(quem, x, y)
                feita, t0_feito = True, g.tick
        if not feita and intervencao is not None and g.tick >= intervencao.t0:
            if not any(g.motores[i]._estado.dormindo for i in intervencao.acordados):
                no_t0 = retrato_do_mundo(g)
                intervencao.aplicar(g)
                feita, t0_feito = True, g.tick
        for m in por_id:
            if m.ident in canais:
                canal = canais[m.ident]
                n = t // passo
                minimo, maximo = canal.limites(n, passos_pet[m.ident])
                visao = Visao(estado=g.motores[m.ident].estado(), passo=n, passos_totais=passos_pet[m.ident], orcamento=canal.orcamento,
                              gasto=canal.gasto, minimo_obrigatorio=minimo, maximo_permitido=maximo)
                canal.aplicar(m.dono.decidir(visao, rngs[m.ident]), n, passos_pet[m.ident])
            elif m.ident in pendentes:
                fila = pendentes[m.ident]
                while fila and fila[0].tick == g.tick:
                    _aplicar_evento_dono(g, fila.pop(0))
                if fila and fila[0].tick < g.tick:
                    raise RuntimeError(f"evento gravado do dono de {m.ident} ficou para tras: {fila[0]} (grupo no tick {g.tick})")
        passos.append(g.tick)
        for m in por_id:
            posicoes[m.ident].append(tuple(g.motores[m.ident].pet))
    for canal in canais.values():
        canal.fechar()
    return VidaPar(g, passos, posicoes, {i: list(gv.decisoes) for i, gv in gravadores.items()},
                   {i: list(p.desvios) for i, p in gravadas.items()}, t0_feito,
                   intervencao.levado if intervencao is not None else None if perturbacao is None else perturbacao[0], no_t0)


def retrato_do_mundo(g: Grupo) -> dict:
    """o que o descritivo do A0 le no t0 (o plano, secao 8, itens 2 e 3): as comidas no mapa, onde a bola esta, e de cada pet se dorme e
    a ultima acao (a decisao do passo que acabou de terminar); so leitura"""
    b = g.mundo.bola
    return {"comidas": len(g.mundo.comidas), "bola": [b["x1"], b["y1"]],
            "pets": {i: {"dormindo": bool(m._estado.dormindo),
                         "ultima_acao": m.decisoes_mundo[-1]["acao"] if m.decisoes_mundo else None,
                         "comeu": bool(m.decisoes_mundo[-1]["comeu"]) if m.decisoes_mundo else False}
                     for i, m in sorted(g.motores.items())}}


# ================================================================== as series que as medidas leem
def distancias_celulas(vida: VidaPar, a: str, b: str) -> list[int]:
    """a distancia de Chebyshev em celulas entre os dois pets no fim de cada passo (a do toque)"""
    cm = vida.grupo.mundo.cmf
    out = []
    for pa, pb in zip(vida.posicoes[a], vida.posicoes[b]):
        (ax, ay), (bx, by) = celula_de(*pa, cm), celula_de(*pb, cm)
        out.append(max(abs(ax - bx), abs(ay - by)))
    return out


def chutes(vida: VidaPar, ident: str) -> list[int]:
    """os ticks do mundo em que o pet chutou a bola (o `brincou_com_bola` das decisoes)"""
    return [d["tick"] for d in vida.grupo.motores[ident].decisoes_mundo if d["brincou_com_bola"]]


def indice_do_passo(vida: VidaPar, tick: int) -> int:
    """o indice do passo em que o tick caiu (o fim do passo)"""
    for k, t in enumerate(vida.passos):
        if t >= tick:
            return k
    raise ValueError(f"tick {tick} depois do fim da vida")
