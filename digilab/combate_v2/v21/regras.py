"""Combate V2.1: resolucao pura com tecnicas (adolescente) e passivas (adulto).

Mesma espinha da V2 (docs/ESPEC_COMBATE_V2.md, secao 2): revelacao simultanea,
custos, ataques com a distancia do INICIO do turno, dano simultaneo, movimento,
regeneracao. Numeros base (danos, custos, multiplicadores) vem de
ConfigCombateV2; os de tecnica/passiva e a conversao de stats, de
ConfigCombateV21. Sem rng.

Tecnicas (acao nova, so para quem tem a linha):
  investida     medio; ataque corpo a corpo que ACERTA na distancia media e
                aproxima (distancia -1 no movimento). EXCECAO documentada a
                regra "ataque perto so acerta perto". Esquivar nao funciona;
                defender (parry) anula o dano E o avanco (o investidor fica
                onde estava, com o guts gasto). Interrompe preparar_pesado (na
                pratica nunca: preparar exige perto e a investida exige medio).
  contra_golpe  perto; postura de defesa (redutores de defender) que devolve
                fracao do dano BRUTO corpo a corpo recebido ao atacante.
  marcar        medio/longe; o proximo disparo em ate N turnos causa dano
                multiplicado e ignora a reducao de defender/contra_golpe (o
                contra_golpe do espelho ainda devolve). Ilegal com marca ativa.
  pele_dura     qualquer distancia; neste turno e no proximo, dano recebido x
                mult e a preparacao do pesado nao pode ser interrompida.
                Ilegal com pele ativa.

Passivas (modificadores de regra, nunca stats escondidos):
  duelista    pesado contra esquiva: causa dano extra fixo e devolve o guts do
              preparar (adaptacao da "finta", que nao existe na base)
  furioso     abaixo do limiar de hp, dano corpo a corpo x mult; defender ilegal
  espelho     contra_golpe legal em qualquer distancia e devolve tambem fracao
              do disparo
  muralha     defender da guts extra ("sem fadiga de guarda" nao se aplica: a
              base nao tem fadiga)
  sentinela   recuar vale mesmo se o oponente avanca/investe, com recarga
  emboscador  o primeiro disparo da partida causa dano multiplicado
  vigia       libera a condicao oponente_vai_preparar (gambits.py)
  tita        pesado causa dano multiplicado
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum

from ...config import CONFIG_COMBATE_V2, CONFIG_COMBATE_V21, ConfigCombateV2, ConfigCombateV21
from ..regras import AcaoIlegal, Distancia
from .catalogo import Perfil

__all__ = ["Acao", "AcaoIlegal", "Distancia", "EstadoLutador", "EstadoCombate", "ResumoTurno",
           "estado_inicial", "eh_legal", "acoes_legais", "acao_obrigatoria", "resolver", "resultado",
           "TECNICAS", "ACOES_ESCOLHIVEIS", "Regras"]


class Acao(str, Enum):
    AVANCAR = "avancar"
    RECUAR = "recuar"
    GOLPE_RAPIDO = "golpe_rapido"
    PREPARAR_PESADO = "preparar_pesado"
    DISPARO = "disparo"
    DEFENDER = "defender"
    ESQUIVAR = "esquivar"
    CARREGAR = "carregar"
    INVESTIDA = "investida"
    CONTRA_GOLPE = "contra_golpe"
    MARCAR = "marcar"
    PELE_DURA = "pele_dura"
    PESADO = "pesado"


ACOES_ESCOLHIVEIS = tuple(a for a in Acao if a is not Acao.PESADO)
TECNICAS = {"investida": Acao.INVESTIDA, "contra_golpe": Acao.CONTRA_GOLPE,
            "marcar": Acao.MARCAR, "pele_dura": Acao.PELE_DURA}
CORPO_A_CORPO = (Acao.GOLPE_RAPIDO, Acao.PESADO, Acao.INVESTIDA)
POSTURAS = (Acao.DEFENDER, Acao.CONTRA_GOLPE)


@dataclass(frozen=True)
class Regras:
    base: ConfigCombateV2 = CONFIG_COMBATE_V2
    v21: ConfigCombateV21 = CONFIG_COMBATE_V21


REGRAS_PADRAO = Regras()


@dataclass(frozen=True)
class EstadoLutador:
    perfil: Perfil
    hp: float
    guts: float
    preparando: bool
    historico: tuple[Acao, ...]
    marca: int = 0              # turnos restantes da marca (marcar)
    pele: int = 0               # turnos restantes de pele_dura DEPOIS do atual
    recarga: int = 0            # sentinela
    disparou: bool = False      # emboscador

    @property
    def hp_max(self) -> float:
        return self.perfil.hp_max

    @property
    def fracao_hp(self) -> float:
        return self.hp / self.perfil.hp_max


@dataclass(frozen=True)
class EstadoCombate:
    turno: int
    distancia: Distancia
    lados: tuple[EstadoLutador, EstadoLutador]

    def proprio(self, lado: int) -> EstadoLutador:
        return self.lados[lado]

    def oponente(self, lado: int) -> EstadoLutador:
        return self.lados[1 - lado]


def estado_inicial(pa: Perfil, pb: Perfil) -> EstadoCombate:
    lados = tuple(EstadoLutador(perfil=p, hp=p.hp_max, guts=p.guts_inicial, preparando=False, historico=())
                  for p in (pa, pb))
    return EstadoCombate(turno=0, distancia=Distancia.MEDIO, lados=lados)  # type: ignore[arg-type]


def custo(acao: Acao, r: Regras) -> int:
    b, v = r.base, r.v21
    return {
        Acao.GOLPE_RAPIDO: b.custo_golpe_rapido, Acao.PREPARAR_PESADO: b.custo_preparar_pesado,
        Acao.DISPARO: b.custo_disparo, Acao.ESQUIVAR: b.custo_esquivar,
        Acao.INVESTIDA: v.custo_investida, Acao.CONTRA_GOLPE: v.custo_contra_golpe,
        Acao.MARCAR: v.custo_marcar, Acao.PELE_DURA: v.custo_pele_dura,
    }.get(acao, 0)


def eh_legal(estado: EstadoCombate, lado: int, acao: Acao, r: Regras = REGRAS_PADRAO) -> bool:
    eu = estado.proprio(lado)
    p = eu.perfil
    if eu.preparando or acao is Acao.PESADO:
        return False
    if acao in TECNICAS.values() and TECNICAS.get(p.tecnica or "") is not acao:
        return False
    if eu.guts < custo(acao, r):
        return False
    d = estado.distancia
    if acao in (Acao.GOLPE_RAPIDO, Acao.PREPARAR_PESADO):
        return d is Distancia.PERTO
    if acao is Acao.DISPARO:
        return d is not Distancia.PERTO
    if acao is Acao.INVESTIDA:
        return d is Distancia.MEDIO
    if acao is Acao.CONTRA_GOLPE:
        return p.passiva == "espelho" or d is Distancia.PERTO
    if acao is Acao.MARCAR:
        return d is not Distancia.PERTO and eu.marca == 0
    if acao is Acao.PELE_DURA:
        return eu.pele == 0
    if acao is Acao.DEFENDER:
        return p.passiva != "furioso"
    return True


def acoes_legais(estado: EstadoCombate, lado: int, r: Regras = REGRAS_PADRAO) -> tuple[Acao, ...]:
    return tuple(a for a in ACOES_ESCOLHIVEIS if eh_legal(estado, lado, a, r))


def acao_obrigatoria(estado: EstadoCombate, lado: int) -> Acao | None:
    return Acao.PESADO if estado.proprio(lado).preparando else None


def _validar(estado: EstadoCombate, lado: int, acao: Acao, r: Regras) -> None:
    if not isinstance(acao, Acao):
        raise AcaoIlegal(f"lado {lado}: acao desconhecida {acao!r}")
    obrig = acao_obrigatoria(estado, lado)
    if obrig is not None:
        if acao is not obrig:
            raise AcaoIlegal(f"lado {lado} esta preparando: so pode executar o pesado, veio {acao.value}")
        return
    if not eh_legal(estado, lado, acao, r):
        eu = estado.proprio(lado)
        raise AcaoIlegal(f"lado {lado} ({eu.perfil.rotulo}): {acao.value} ilegal "
                         f"(guts {eu.guts}, distancia {estado.distancia.rotulo})")


@dataclass(frozen=True)
class ResumoTurno:
    dano_recebido: tuple[float, float]
    devolvido: tuple[float, float]       # dano que o lado DEVOLVEU (contra_golpe)
    interrompido: tuple[bool, bool]
    pesado_errou: tuple[bool, bool]
    marca_usada: tuple[bool, bool]


def resolver(estado: EstadoCombate, acao_a: Acao, acao_b: Acao,
             r: Regras = REGRAS_PADRAO) -> tuple[EstadoCombate, ResumoTurno]:
    b, v = r.base, r.v21
    acoes = (acao_a, acao_b)
    for lado in (0, 1):
        _validar(estado, lado, acoes[lado], r)
    lados = estado.lados

    # 2. custos
    guts = [lados[i].guts - custo(acoes[i], r) for i in (0, 1)]

    # pele ativa neste turno: usada agora ou restante de antes
    pele_ativa = [acoes[i] is Acao.PELE_DURA or lados[i].pele > 0 for i in (0, 1)]

    # 3. ataques com a distancia do inicio do turno
    d0 = estado.distancia
    dano = [0.0, 0.0]
    devolvido = [0.0, 0.0]
    interrompido = [False, False]
    errou = [False, False]
    marca_usada = [False, False]
    parry = [False, False]       # investida aparada: nao aproxima
    for atk in (0, 1):
        alvo = 1 - atk
        eu, ele = lados[atk], lados[alvo]
        pa, pal = eu.perfil, ele.perfil
        acao, reacao = acoes[atk], acoes[alvo]

        bruto = 0.0
        if acao is Acao.GOLPE_RAPIDO:
            bruto = b.dano_golpe_rapido * pa.mult_perto
        elif acao is Acao.INVESTIDA:
            bruto = v.dano_investida * pa.mult_perto
        elif acao is Acao.PESADO:
            if d0 is Distancia.PERTO:
                bruto = b.dano_pesado * pa.mult_perto
                if pa.passiva == "tita":
                    bruto *= v.mult_tita
            else:
                errou[atk] = True
        elif acao is Acao.DISPARO:
            bruto = b.dano_disparo * pa.mult_disparo
            if eu.marca > 0:
                bruto *= v.mult_marcar
                marca_usada[atk] = True
            if pa.passiva == "emboscador" and not eu.disparou:
                bruto *= v.mult_emboscador
        if acao in CORPO_A_CORPO and pa.passiva == "furioso" and eu.fracao_hp < v.limiar_hp_furioso:
            bruto *= v.mult_furioso
        if bruto == 0.0:
            continue

        # reacao do alvo
        recebido = bruto
        marcado = acao is Acao.DISPARO and marca_usada[atk]
        if reacao is Acao.ESQUIVAR:
            if acao in (Acao.PESADO, Acao.DISPARO):
                recebido = 0.0
                if acao is Acao.PESADO and pa.passiva == "duelista":
                    recebido = v.dano_extra_duelista
                    guts[atk] += b.custo_preparar_pesado
        elif reacao in POSTURAS:
            # disparo marcado ignora a REDUCAO da postura; o contra_golpe ainda devolve
            if marcado:
                pass
            elif acao is Acao.INVESTIDA:
                recebido = bruto * v.mult_parry_investida
                if reacao is Acao.DEFENDER:
                    parry[atk] = True
            elif acao is Acao.PESADO:
                recebido = bruto * b.mult_defender_contra_pesado * pal.mult_guarda
            else:
                recebido = bruto * b.mult_defender * pal.mult_guarda
            if reacao is Acao.CONTRA_GOLPE:
                if acao in CORPO_A_CORPO:
                    devolvido[alvo] += v.fracao_contra_golpe * bruto
                elif acao is Acao.DISPARO and pal.passiva == "espelho":
                    devolvido[alvo] += v.fracao_espelho_disparo * bruto
        elif reacao is Acao.CARREGAR:
            recebido = bruto * b.mult_carregar
        if pele_ativa[alvo]:
            recebido *= v.mult_pele_dura
        dano[alvo] += recebido

        # golpe rapido / investida interrompem quem esta PREPARANDO, salvo pele_dura
        if acao in (Acao.GOLPE_RAPIDO, Acao.INVESTIDA) and reacao is Acao.PREPARAR_PESADO and not pele_ativa[alvo]:
            interrompido[alvo] = True

    # dano devolvido pelo contra_golpe (pele_dura do atacante tambem reduz)
    for i in (0, 1):
        if devolvido[i]:
            dano[1 - i] += devolvido[i] * (v.mult_pele_dura if pele_ativa[1 - i] else 1.0)

    # 5. movimento
    passo = {Acao.AVANCAR: -1, Acao.RECUAR: 1, Acao.INVESTIDA: -1}
    passos = [0 if parry[i] else passo.get(acoes[i], 0) for i in (0, 1)]
    recarga = [max(0, lados[i].recarga - 1) for i in (0, 1)]
    for i in (0, 1):
        # sentinela: o recuo vale mesmo se o oponente se aproxima
        if (lados[i].perfil.passiva == "sentinela" and acoes[i] is Acao.RECUAR and passos[1 - i] < 0
                and lados[i].recarga == 0):
            passos[1 - i] = 0
            recarga[i] = v.recarga_sentinela
    d = int(d0) + passos[0] + passos[1]
    distancia = Distancia(min(int(Distancia.LONGE), max(int(Distancia.PERTO), d)))

    # 4 + 6. dano simultaneo, regeneracao, contadores
    novos = []
    for i in (0, 1):
        s = lados[i]
        p = s.perfil
        g = guts[i] + p.regen
        if acoes[i] is Acao.DEFENDER:
            g += b.guts_extra_defender + (v.guts_extra_muralha if p.passiva == "muralha" else 0)
        if acoes[i] is Acao.CARREGAR:
            g += b.guts_carregar
        if acoes[i] is Acao.MARCAR:
            marca = v.turnos_marcar
        else:
            marca = 0 if marca_usada[i] else max(0, s.marca - 1)
        pele = v.turnos_pele_dura - 1 if acoes[i] is Acao.PELE_DURA else max(0, s.pele - 1)
        novos.append(replace(
            s, hp=s.hp - dano[i], guts=max(0.0, min(p.guts_max, g)),
            preparando=acoes[i] is Acao.PREPARAR_PESADO and not interrompido[i],
            historico=s.historico + (acoes[i],), marca=marca, pele=pele, recarga=recarga[i],
            disparou=s.disparou or acoes[i] is Acao.DISPARO,
        ))
    novo = EstadoCombate(turno=estado.turno + 1, distancia=distancia, lados=(novos[0], novos[1]))
    return novo, ResumoTurno((dano[0], dano[1]), (devolvido[0], devolvido[1]), (interrompido[0], interrompido[1]),
                             (errou[0], errou[1]), (marca_usada[0], marca_usada[1]))


def resultado(estado: EstadoCombate, r: Regras = REGRAS_PADRAO) -> tuple[float, str] | None:
    a, b = estado.lados
    ko_a, ko_b = a.hp <= 0.0, b.hp <= 0.0
    if ko_a or ko_b:
        return (0.5 if ko_a and ko_b else 0.0 if ko_a else 1.0), "ko"
    if estado.turno >= r.base.t_max:
        fa, fb = a.fracao_hp, b.fracao_hp
        return (0.5 if fa == fb else 1.0 if fa > fb else 0.0), "limite"
    return None
