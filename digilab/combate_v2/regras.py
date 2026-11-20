"""Combate V2: estado, acoes e resolucao pura de um turno.

A resolucao e uma funcao pura de (estado, acao_a, acao_b) e NAO consome rng:
nao ha dano variavel nem chance de acerto. Toda aleatoriedade da partida vem
das decisoes (epsilon), em gambits.py.

Ordem de um turno:
  1. revelacao simultanea (quem chama ja tem as duas acoes)
  2. custos de guts; acao ilegal levanta AcaoIlegal
  3. ataques, com a distancia do INICIO do turno
  4. dano simultaneo
  5. movimento (distancia limitada a perto..longe)
  6. regeneracao de guts (+ ganho de defender / carregar)
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum

from ..config import CONFIG_COMBATE_V2, ConfigCombateV2


class AcaoIlegal(ValueError):
    pass


class Distancia(int, Enum):
    PERTO = 0
    MEDIO = 1
    LONGE = 2

    @property
    def rotulo(self) -> str:
        return self.name.lower()


class Acao(str, Enum):
    AVANCAR = "avancar"
    RECUAR = "recuar"
    GOLPE_RAPIDO = "golpe_rapido"
    PREPARAR_PESADO = "preparar_pesado"
    DISPARO = "disparo"
    DEFENDER = "defender"
    ESQUIVAR = "esquivar"
    CARREGAR = "carregar"
    # nao e escolhida: executada automaticamente no turno seguinte ao preparar
    PESADO = "pesado"
    # V2C (C1): alternativa ao pesado, so no turno de execucao e so com ConfigCombateV2C.finta
    FINTAR = "fintar"


ACOES_ESCOLHIVEIS = tuple(a for a in Acao if a not in (Acao.PESADO, Acao.FINTAR))
# ataques com golpe rapido (a finta e um golpe rapido)
GOLPES = (Acao.GOLPE_RAPIDO, Acao.FINTAR)


def _opcao(cfg, nome: str, padrao):
    """Chaves da V2C (ConfigCombateV2C); a ConfigCombateV2 original nao as tem: comportamento antigo."""
    return getattr(cfg, nome, padrao)


@dataclass(frozen=True)
class EstadoLutador:
    hp: float
    hp_max: float
    guts: int
    regen: int
    preparando: bool
    historico: tuple[Acao, ...]

    @property
    def fracao_hp(self) -> float:
        return self.hp / self.hp_max


@dataclass(frozen=True)
class EstadoCombate:
    turno: int
    distancia: Distancia
    lados: tuple[EstadoLutador, EstadoLutador]

    def proprio(self, lado: int) -> EstadoLutador:
        return self.lados[lado]

    def oponente(self, lado: int) -> EstadoLutador:
        return self.lados[1 - lado]

    def espelhado(self) -> "EstadoCombate":
        return replace(self, lados=(self.lados[1], self.lados[0]))


def estado_inicial(
    hp_max: tuple[float, float], guts_inicial: tuple[int, int], regen: tuple[int, int]
) -> EstadoCombate:
    lados = tuple(
        EstadoLutador(hp=float(hp_max[i]), hp_max=float(hp_max[i]), guts=int(guts_inicial[i]),
                      regen=int(regen[i]), preparando=False, historico=())
        for i in (0, 1)
    )
    return EstadoCombate(turno=0, distancia=Distancia.MEDIO, lados=lados)  # type: ignore[arg-type]


def custo(acao: Acao, cfg: ConfigCombateV2) -> int:
    return {
        Acao.GOLPE_RAPIDO: cfg.custo_golpe_rapido,
        Acao.PREPARAR_PESADO: cfg.custo_preparar_pesado,
        Acao.DISPARO: cfg.custo_disparo,
        Acao.ESQUIVAR: cfg.custo_esquivar,
    }.get(acao, 0)


def eh_legal(estado: EstadoCombate, lado: int, acao: Acao, cfg: ConfigCombateV2 | None = None) -> bool:
    """Legalidade de uma acao ESCOLHIDA. Quem esta preparando nao escolhe."""
    cfg = cfg or CONFIG_COMBATE_V2
    eu = estado.proprio(lado)
    if acao is Acao.FINTAR:
        return _opcao(cfg, "finta", False) and eu.preparando
    if eu.preparando or acao is Acao.PESADO:
        return False
    if eu.guts < custo(acao, cfg):
        return False
    if acao in (Acao.GOLPE_RAPIDO, Acao.PREPARAR_PESADO):
        return estado.distancia is Distancia.PERTO
    if acao is Acao.DISPARO:
        return estado.distancia is not Distancia.PERTO
    if _opcao(cfg, "fuga_condicionada", False):
        if acao is Acao.AVANCAR:
            return estado.distancia is not Distancia.PERTO
        if acao is Acao.RECUAR:
            return estado.distancia is not Distancia.LONGE
    return True


def acoes_legais(estado: EstadoCombate, lado: int, cfg: ConfigCombateV2 | None = None) -> tuple[Acao, ...]:
    """Acoes que o lado pode escolher, em ordem fixa. Vazia se ele esta preparando."""
    return tuple(a for a in ACOES_ESCOLHIVEIS if eh_legal(estado, lado, a, cfg))


def acao_obrigatoria(estado: EstadoCombate, lado: int) -> Acao | None:
    """PESADO se o lado esta preparando (nao escolhe nada); senao None."""
    return Acao.PESADO if estado.proprio(lado).preparando else None


def _validar(estado: EstadoCombate, lado: int, acao: Acao, cfg: ConfigCombateV2) -> None:
    if not isinstance(acao, Acao):
        raise AcaoIlegal(f"lado {lado}: acao desconhecida {acao!r}")
    obrig = acao_obrigatoria(estado, lado)
    if obrig is not None:
        if acao is not obrig and not (acao is Acao.FINTAR and eh_legal(estado, lado, acao, cfg)):
            raise AcaoIlegal(f"lado {lado} esta preparando: so pode executar o pesado, veio {acao.value}")
        return
    if not eh_legal(estado, lado, acao, cfg):
        eu = estado.proprio(lado)
        raise AcaoIlegal(
            f"lado {lado}: {acao.value} ilegal (guts {eu.guts}, distancia {estado.distancia.rotulo})"
        )


def _dano_bruto(acao: Acao, distancia_inicio: Distancia, cfg: ConfigCombateV2) -> float:
    if acao is Acao.GOLPE_RAPIDO:
        return cfg.dano_golpe_rapido
    if acao is Acao.FINTAR:          # golpe rapido no lugar do pesado: so acerta de perto
        return cfg.dano_golpe_rapido if distancia_inicio is Distancia.PERTO else 0.0
    if acao is Acao.DISPARO:
        return cfg.dano_disparo
    if acao is Acao.PESADO:
        return cfg.dano_pesado if distancia_inicio is Distancia.PERTO else 0.0
    return 0.0


def _dano_recebido(ataque: Acao, bruto: float, reacao: Acao, cfg: ConfigCombateV2) -> float:
    if bruto == 0.0:
        return 0.0
    if reacao is Acao.ESQUIVAR:
        return bruto if ataque in GOLPES else 0.0
    if reacao is Acao.DEFENDER:
        return bruto * (cfg.mult_defender_contra_pesado if ataque is Acao.PESADO else cfg.mult_defender)
    if reacao is Acao.CARREGAR:
        return bruto * cfg.mult_carregar
    return bruto


@dataclass(frozen=True)
class ResumoTurno:
    dano_recebido: tuple[float, float]
    interrompido: tuple[bool, bool]
    pesado_errou: tuple[bool, bool]


def resolver(
    estado: EstadoCombate, acao_a: Acao, acao_b: Acao, cfg: ConfigCombateV2 | None = None
) -> tuple[EstadoCombate, ResumoTurno]:
    """Um turno. Funcao pura: mesma entrada, mesma saida; nao usa rng."""
    cfg = cfg or CONFIG_COMBATE_V2
    acoes = (acao_a, acao_b)
    for lado in (0, 1):
        _validar(estado, lado, acoes[lado], cfg)

    # 2. custos
    guts = [estado.lados[i].guts - custo(acoes[i], cfg) for i in (0, 1)]

    # 3. ataques com a distancia do inicio do turno
    d0 = estado.distancia
    dano = [0.0, 0.0]            # dano recebido por lado
    interrompido = [False, False]
    errou = [False, False]
    parry = _opcao(cfg, "dano_parry", 0.0)
    for atk in (0, 1):
        alvo = 1 - atk
        bruto = _dano_bruto(acoes[atk], d0, cfg)
        if acoes[atk] is Acao.PESADO and bruto == 0.0:
            errou[atk] = True
        dano[alvo] += _dano_recebido(acoes[atk], bruto, acoes[alvo], cfg)
        # golpe rapido (e a finta) interrompe quem esta PREPARANDO neste turno (o pesado
        # executando tem armadura e nao e interrompido)
        if acoes[atk] in GOLPES and acoes[alvo] is Acao.PREPARAR_PESADO:
            interrompido[alvo] = True
        # C2 parry: defender contra golpe rapido que acertou devolve dano ao atacante
        if parry and bruto > 0.0 and acoes[atk] in GOLPES and acoes[alvo] is Acao.DEFENDER:
            dano[atk] += parry
    # C4 morte subita: a partir do turno N (o turno resolvido agora e estado.turno + 1)
    t_ms = _opcao(cfg, "turno_morte_subita", 0)
    if t_ms and estado.turno + 1 >= t_ms:
        dano = [x * cfg.mult_morte_subita for x in dano]

    # 5. movimento (C3: recuar nao afasta se o oponente avanca no mesmo turno)
    passo = {Acao.AVANCAR: -1, Acao.RECUAR: 1}
    pa, pb = passo.get(acao_a, 0), passo.get(acao_b, 0)
    if _opcao(cfg, "fuga_condicionada", False):
        if acao_a is Acao.RECUAR and acao_b is Acao.AVANCAR:
            pa = 0
        if acao_b is Acao.RECUAR and acao_a is Acao.AVANCAR:
            pb = 0
    d = int(d0) + pa + pb
    distancia = Distancia(min(int(Distancia.LONGE), max(int(Distancia.PERTO), d)))

    # 4 + 6. dano simultaneo, regeneracao
    novos = []
    for i in (0, 1):
        s = estado.lados[i]
        g = guts[i] + s.regen
        if acoes[i] is Acao.DEFENDER:
            g += cfg.guts_extra_defender
        if acoes[i] is Acao.CARREGAR:
            g += cfg.guts_carregar
        novos.append(replace(
            s,
            hp=s.hp - dano[i],
            guts=max(0, min(cfg.guts_max, g)),
            preparando=acoes[i] is Acao.PREPARAR_PESADO and not interrompido[i],
            historico=s.historico + (acoes[i],),
        ))
    novo = EstadoCombate(turno=estado.turno + 1, distancia=distancia, lados=(novos[0], novos[1]))
    return novo, ResumoTurno(dano_recebido=(dano[0], dano[1]), interrompido=(interrompido[0], interrompido[1]),
                             pesado_errou=(errou[0], errou[1]))


def resultado(estado: EstadoCombate, cfg: ConfigCombateV2 | None = None) -> tuple[float, str] | None:
    """(pontos do lado 0, motivo) se acabou; None se continua.

    KO: hp <= 0 (duplo = empate). Limite de turnos: maior fracao de hp vence;
    igualdade exata = empate.
    """
    cfg = cfg or CONFIG_COMBATE_V2
    a, b = estado.lados
    ko_a, ko_b = a.hp <= 0.0, b.hp <= 0.0
    if ko_a or ko_b:
        return (0.5 if ko_a and ko_b else 0.0 if ko_a else 1.0), "ko"
    if estado.turno >= cfg.t_max:
        fa, fb = a.fracao_hp, b.fracao_hp
        return (0.5 if fa == fb else 1.0 if fa > fb else 0.0), "limite"
    return None
