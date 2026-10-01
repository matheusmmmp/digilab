"""V2, L1 (docs/PLANO_ANALISE_V2_L1.md, revisao 2, registrada antes da run): o lobo de decisao aprende com o feedback como
vantagem; G3-T, G4 do aprendido, controle sem lobos, "so cuidado" acoplado e norma de reacao (D1-D4 de docs/DEFINICOES_V2.md).

    python experiments/run_v2_l1.py --config experiments/configs/v2_l1/calibracao.json   # grade passo x teto, sementes 3101...3505
    python experiments/run_v2_l1.py --config experiments/configs/v2_l1/validacao.json    # UMA vez, 4101...4505, depois do referendo

Fluxo por ponto (passo, teto):
  1. vidas      - 4 donos x lobos (aprendendo) x sementes; instinto (piso do G3-T) e bandit (referencia v1) nao dependem do
                  ponto e rodam uma vez (pasta base/). O mesmo dono com a mesma rng em todas as politicas (rotulo_dono);
                  MotorComFeedback, 14 dias, orcamento da arena v1.
  2. replay     - toda vida e reconstruida DO DISCO (log + politica.json gravado ANTES das sondas) e comparada bit a bit.
  3. G3         - divergencia (sondas da arena v1, numeros aleatorios comuns): atencioso x relapso por semente, IC bootstrap.
  4. G3-T       - acerto na tarefa ensinada (donos.julgar_acao), por dia; teto do dono, piso do instinto, eficiencia amostral.
  5. G4         - legibilidade: PoliticaComMotivo sobre cada vida (motivo_lobos); gate so sobre o aprendido; bruto ao lado.
  6. G6         - deriva: JSD(politica no fim do dia d, instinto), d = 1..14, por vida lobos; pesos no teto no dia 14.
  7. gates      - PROPOSTOS (plano, secao 4). Calibracao: escolha do ponto pela regra da secao 5; validacao: uma vez.
So no ponto escolhido (e na validacao): o controle sem lobos (D2), o acoplado e a variante sem carinho (D4, G5 c), a norma de
reacao (3.2) e o braco de educacao com lesoes (3.1, G5 b).
Divergencia de replay nao e aviso: levanta erro e para tudo. Nenhuma metrica fora de digilab/metrics.py e digilab/motivo.py.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import random
import sys
import time
from collections import Counter
from dataclasses import replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

from digilab.config import (CONFIG_DONOS, CONFIG_EDUCACAO_LIGADA, CONFIG_LESOES_LIGADA, CONFIG_LOBOS, CONFIG_PADRAO,  # noqa: E402
                            ConfigLobos)
from digilab.donos import criar_dono, julgar_acao  # noqa: E402
from digilab.donos_educacao import simular_vida_educacao  # noqa: E402
from digilab.educacao import fabricas_educacao, reproduzir_educacao  # noqa: E402
from digilab.events import AcaoPet, AcaoUsuario, LogDeEventos  # noqa: E402
from digilab.evolucao import ovo, politica_no_tick  # noqa: E402
from digilab.metrics import (acerto_na_tarefa, bootstrap_ic, distribuicoes_de_acao, divergencia_politicas,  # noqa: E402
                             eficiencia_amostral, estados_sonda, jsd_media, norma_de_reacao)
from digilab.motivo import motivos_de_vida  # noqa: E402
from digilab.policies import PoliticaBandit, PoliticaCamadaUnica, PoliticaLobos  # noqa: E402
from digilab.policy import PoliticaInstinto  # noqa: E402
from digilab.protocol import ENGINE_SHA256_V0, PROTOCOLO_ARENA_V1, derivar_semente, sha256_engine  # noqa: E402
from digilab.temperamento import sortear  # noqa: E402
from digilab.treino import MotorComFeedback, Vida, reproduzir_com_feedback, simular_vida  # noqa: E402
from run_educacao import PetDaVida, rival_por_nome, ticks_sparring  # noqa: E402

TICKS_POR_DIA = 1440
SEMENTES_CALIBRACAO = (3101, 3202, 3303, 3404, 3505)
SEMENTES_VALIDACAO = (4101, 4202, 4303, 4404, 4505)
DONOS = ("atencioso", "relapso", "aleatorio", "incoerente")
COERENTES = ("atencioso", "relapso")          # os dois que aplicam a regra de feedback coerente (plano, secao 4)
ACOES = tuple(a.value for a in AcaoPet)
SINAIS = frozenset({AcaoUsuario.ELOGIAR.value, AcaoUsuario.REPREENDER.value})
CHAVES_CONFIG = {"descricao", "conjunto", "sementes", "saida", "grade", "ponto", "educacao", "dias", "orcamento", "sonda",
                 "bootstrap", "gates", "dias_deriva", "n_ambientes"}


class ReplayDivergiu(RuntimeError):
    pass


class DivergenciaInstintoNaoNula(RuntimeError):
    pass


def _dump(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True)


def _gravar(caminho: Path, texto: str) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(texto, encoding="utf-8", newline="\n")


def _sha(caminho: Path) -> str:
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


def cfg_lobos(ponto: dict) -> ConfigLobos:
    return replace(CONFIG_LOBOS, aprendizado_ligado=True, passo=int(ponto["passo"]), teto=int(ponto["teto"]))


def fabrica(pol: str, ponto: dict | None):
    if pol in ("lobos", "cuidado", "cuidado-semcarinho"):
        cl = cfg_lobos(ponto)
        return lambda cfg=None: PoliticaLobos(cfg, cl)
    if pol == "controle":
        cl = cfg_lobos(ponto)
        return lambda cfg=None: PoliticaCamadaUnica(cfg, cl)
    if pol == "instinto":
        return lambda cfg=None: PoliticaInstinto(cfg)
    if pol == "bandit":
        return lambda cfg=None: PoliticaBandit(cfg)
    raise KeyError(pol)


def rotulo(dono: str, pol: str) -> str:
    return f"{dono}-{pol}"


def par(div, a: str, b: str) -> float:
    return div.pares[tuple(sorted((a, b)))]


def media(xs) -> float:
    xs = list(xs)
    if not xs:
        raise ValueError("media de lista vazia")
    return sum(xs) / len(xs)


def ic_de(boot: dict):
    return lambda xs: bootstrap_ic(list(xs), boot["reamostragens"], boot["semente"], boot["nivel"])


class MotorGR(MotorComFeedback):
    """MotorComFeedback com a rng de AMBIENTE de outra semente (norma de reacao, plano 3.2): a semente do motor (o ovo)
    segue na rng da politica; engine.py intocado (so o atributo e trocado depois da construcao)."""

    def __init__(self, politica=None, cfg=None, semente: int = 42, semente_ambiente: int | None = None) -> None:
        super().__init__(politica=politica, cfg=cfg, semente=semente)
        if semente_ambiente is None:
            raise ValueError("MotorGR precisa da semente do ambiente")
        self._rng_ambiente = random.Random(semente_ambiente)
        self.semente_ambiente = semente_ambiente


# ------------------------------------------------------------------ 1-2. vidas e replay


def _conferir_replay(nome: str, v_motor, r, salvo: dict) -> None:
    if r.estado() != v_motor.estado() or r.acoes_recentes(10**9) != v_motor.acoes_recentes(10**9):
        raise ReplayDivergiu(f"{nome}: estado ou acoes divergem no replay")
    if r._rng_politica.getstate() != v_motor._rng_politica.getstate() or r._rng_ambiente.getstate() != v_motor._rng_ambiente.getstate():
        raise ReplayDivergiu(f"{nome}: rng diverge no replay")
    if json.loads(json.dumps(r.politica.estado_interno(), sort_keys=True)) != salvo:
        raise ReplayDivergiu(f"{nome}: parametros da politica divergem no replay")


def _gravar_vida(dir_vidas: Path, nome: str, motor) -> dict:
    _gravar(dir_vidas / f"{nome}.jsonl", motor.log.para_jsonl())
    salvo = json.dumps(motor.politica.estado_interno(), sort_keys=True)
    _gravar(dir_vidas / f"{nome}.politica.json", salvo)
    return json.loads(salvo)


def vidas_arena(pol: str, ponto: dict | None, sementes, dias: int, orcamento: int, pasta: Path, donos=DONOS) -> dict:
    """Vidas de uma politica nos donos x sementes, gravadas e rejogadas do disco. Devolve nome -> Vida."""
    fab = fabrica(pol, ponto)
    dir_vidas = pasta / "vidas"
    vidas, salvos = {}, {}
    for s in sementes:
        for dono in donos:
            v = simular_vida(rotulo(dono, pol), criar_dono(dono), fab(), s, dias, orcamento, rotulo_dono=dono)
            vidas[v.nome] = v
            salvos[v.nome] = _gravar_vida(dir_vidas, v.nome, v.motor)
    n_int = {n: sum(1 for e in v.motor.log if e.tipo == "acao_usuario") for n, v in vidas.items()}
    if set(n_int.values()) != {orcamento}:
        raise RuntimeError(f"interacoes por pet diferem do orcamento {orcamento}: {n_int}")
    for nome, v in sorted(vidas.items()):
        log = LogDeEventos.de_jsonl((dir_vidas / f"{nome}.jsonl").read_text(encoding="utf-8"))
        _conferir_replay(nome, v.motor, reproduzir_com_feedback(log, fab, semente=v.semente_coorte), salvos[nome])
    return vidas


def log_so_cuidado(log: LogDeEventos, sem_carinho: bool = False) -> LogDeEventos:
    """O mesmo log sem os eventos de elogio e bronca (e, na variante, sem acariciar): as acoes de cuidado nos mesmos ticks."""
    fora = set(SINAIS) | ({AcaoUsuario.ACARICIAR.value} if sem_carinho else set())
    return LogDeEventos([e for e in log if not (e.tipo == "acao_usuario" and str(e.valor) in fora)])


def vidas_acopladas(vidas_lobos: dict, ponto: dict, sementes, pasta: Path, sem_carinho: bool,
                    fabrica_motor=None, dono: str = "atencioso") -> dict:
    """"So cuidado" acoplado (D4): o log de <dono>-lobos@s sem os sinais, rejogado com uma PoliticaLobos aprendiz nova."""
    pol = "cuidado-semcarinho" if sem_carinho else "cuidado"
    fab = fabrica(pol, ponto)
    dir_vidas = pasta / "vidas"
    vidas = {}
    for s in sementes:
        origem = vidas_lobos[f"{rotulo(dono, 'lobos')}@{s}"]
        log = log_so_cuidado(origem.motor.log, sem_carinho)
        m = reproduzir_com_feedback(log, fab, semente=s, fabrica_motor=fabrica_motor)
        nome = f"{rotulo(dono, pol)}@{s}"
        v = Vida(braco=rotulo(dono, pol), semente_coorte=s, motor=m, interacoes=sum(1 for e in log if e.tipo == "acao_usuario"))
        v.origem = origem.nome
        vidas[nome] = v
        salvo = _gravar_vida(dir_vidas, nome, m)
        log2 = LogDeEventos.de_jsonl((dir_vidas / f"{nome}.jsonl").read_text(encoding="utf-8"))
        _conferir_replay(nome, m, reproduzir_com_feedback(log2, fab, semente=s, fabrica_motor=fabrica_motor), salvo)
    return vidas


# ------------------------------------------------------------------ 3. G3: divergencia


def _resumo_pol(div, pol: str, sementes, ic, donos=DONOS) -> dict:
    nome = lambda d, s: f"{rotulo(d, pol)}@{s}"  # noqa: E731
    prim = [par(div, nome("atencioso", s), nome("relapso", s)) for s in sementes]
    vs_aleatorio = {d: [par(div, nome(d, s), nome("aleatorio", s)) for s in sementes] for d in COERENTES}
    seis = [media(par(div, nome(a, s), nome(b, s)) for i, a in enumerate(donos) for b in donos[i + 1:]) for s in sementes]
    pets = [nome(d, s) for d in donos for s in sementes]
    entre = [par(div, a, b) for i, a in enumerate(pets) for b in pets[i + 1:] if a.split("@")[0] != b.split("@")[0]]
    dentro = [par(div, a, b) for i, a in enumerate(pets) for b in pets[i + 1:] if a.split("@")[0] == b.split("@")[0]]
    return {
        "primario_atencioso_x_relapso": {"por_semente": dict(zip(map(str, sementes), prim)), **ic(prim)},
        "coerente_x_aleatorio": {d: {"por_semente": dict(zip(map(str, sementes), xs)), **ic(xs)} for d, xs in vs_aleatorio.items()},
        "media_seis_pares": {"por_semente": dict(zip(map(str, sementes), seis)), **ic(seis)},
        "conta_v1": {"jsd_entre_bracos": media(entre), "jsd_dentro_do_braco": media(dentro), "n_pares_entre": len(entre),
                     "n_pares_dentro": len(dentro), "piso_ruido": media(div.piso_ruido[p] for p in pets)},
        "jsd_vs_instinto": {p: par(div, p, "instinto") for p in pets},
        "_entre": entre,
    }


def divergencia(vidas_por_pol: dict, acoplados: dict, sementes, sonda: dict, boot: dict) -> dict:
    """vidas_por_pol: politicas com os 4 donos; acoplados: {"cuidado": vidas, "cuidado-semcarinho": vidas} (so atencioso)."""
    politicas = {n: v.motor.politica for vidas in vidas_por_pol.values() for n, v in vidas.items()}
    for vidas in acoplados.values():
        politicas.update({n: v.motor.politica for n, v in vidas.items()})
    politicas["instinto"] = PoliticaInstinto()
    estados = estados_sonda(sonda["estados"], sonda["semente"])
    div, _ = divergencia_politicas(politicas, estados, sonda["amostras"], sonda["semente"])
    ic = ic_de(boot)
    saida = {}
    for pol in vidas_por_pol:
        r = _resumo_pol(div, pol, sementes, ic)
        entre = r.pop("_entre")
        if pol == "instinto" and any(v != 0.0 for v in entre):
            raise DivergenciaInstintoNaoNula("pares instinto x instinto com JSD != 0")
        saida[pol] = r
    for pol in acoplados:
        a = lambda s: f"{rotulo('atencioso', pol)}@{s}"  # noqa: E731
        vs_ensino = [par(div, a(s), f"atencioso-lobos@{s}") for s in sementes]
        vs_relapso = [par(div, a(s), f"relapso-lobos@{s}") for s in sementes]
        g5c = [saida["lobos"]["primario_atencioso_x_relapso"]["por_semente"][str(s)] - x for s, x in zip(sementes, vs_relapso)]
        saida[pol] = {"acoplado_x_ensino": {"por_semente": dict(zip(map(str, sementes), vs_ensino)), **ic(vs_ensino)},
                      "acoplado_x_relapso": {"por_semente": dict(zip(map(str, sementes), vs_relapso)), **ic(vs_relapso)},
                      "g5c_ensino_menos_acoplado": {"por_semente": dict(zip(map(str, sementes), g5c)), **ic(g5c)},
                      "jsd_vs_instinto": {a(s): par(div, a(s), "instinto") for s in sementes}}
    return saida


# ------------------------------------------------------------------ 4. G3-T: tarefa ensinada


class _Gravadora:
    """Embrulha a politica no replay e anota (tick, estado como o dono o julga, acao) e os sinais acumulados."""

    def __init__(self, interna) -> None:
        self.interna = interna
        self.nome = interna.nome
        self._tick_ultimo_cuidado = 0
        self.decisoes: list[tuple[int, dict, str]] = []
        self.sinais_na_decisao: list[int] = []
        self._sinais = 0

    def agir(self, obs, rng):
        acao = self.interna.agir(obs, rng)
        v = obs.vetor_estado
        estado = {"fome": v[0], "higiene": v[1], "energia": v[2], "tick_do_dia": int(round(v[7] * TICKS_POR_DIA))}
        self.decisoes.append((obs.ticks_desde_cuidado + self._tick_ultimo_cuidado, estado, acao.value))
        self.sinais_na_decisao.append(self._sinais)
        return acao

    def observar(self, transicao):
        self.interna.observar(transicao)

    def receber_acao_dono(self, acao, tick):
        self._tick_ultimo_cuidado = tick
        if acao.value in SINAIS:
            self._sinais += 1
        f = getattr(self.interna, "receber_acao_dono", None)
        if f is not None:
            f(acao, tick)

    def estado_interno(self):
        return self.interna.estado_interno()


def _julgar(estado: dict, acao: str) -> int:
    return julgar_acao({**estado, "acao_atual": acao}, CONFIG_DONOS)


def curva_tarefa(log: LogDeEventos, fab, semente: int, fabrica_motor=None, dias: int = 14) -> dict:
    grav = []

    def f(cfg):
        g = _Gravadora(fab(cfg))
        grav.append(g)
        return g

    reproduzir_com_feedback(log, f, semente=semente, fabrica_motor=fabrica_motor)
    g = grav[0]
    c = acerto_na_tarefa(g.decisoes, _julgar, ACOES, TICKS_POR_DIA)
    sinais = []
    for d in c["dias"]:
        ate = [s for (t, _, _), s in zip(g.decisoes, g.sinais_na_decisao) if t < (d + 1) * TICKS_POR_DIA]
        sinais.append(ate[-1] if ate else 0)
    c["sinais_acumulados"] = sinais
    c["sinais_total"] = g._sinais
    c["ultimos_7"] = media(c["acerto"][-7:])
    c["teto_ultimos_7"] = media(c["teto"][-7:])
    return c


def tarefa(vidas: dict, pol: str, ponto: dict | None, pasta: Path, piso_por_vida: dict | None, boot: dict,
           fabrica_motor=None) -> dict:
    """G3-T por vida e resumo por dono; piso = acerto total da vida <dono>-instinto da mesma semente."""
    fab = fabrica(pol, ponto)
    por_vida = {}
    for nome, v in sorted(vidas.items()):
        log = LogDeEventos.de_jsonl((pasta / "vidas" / f"{nome}.jsonl").read_text(encoding="utf-8"))
        c = curva_tarefa(log, fab, v.semente_coorte, fabrica_motor)
        dono = v.braco.split("-")[0]
        piso = piso_por_vida[f"{dono}-instinto@{v.semente_coorte}"] if piso_por_vida else c["acerto_total"]
        c["eficiencia"] = eficiencia_amostral(c["acerto"], c["sinais_acumulados"], piso)
        por_vida[nome] = c
    ic = ic_de(boot)
    resumo = {}
    for dono in sorted({v.braco.split("-")[0] for v in vidas.values()}):
        cs = [c for n, c in sorted(por_vida.items()) if n.startswith(f"{dono}-")]
        efic = [c["eficiencia"]["sinais"] for c in cs]
        resumo[dono] = {"ultimos_7": ic([c["ultimos_7"] for c in cs]), "teto_ultimos_7": ic([c["teto_ultimos_7"] for c in cs]),
                        "acerto_total": ic([c["acerto_total"] for c in cs]), "piso": ic([c["eficiencia"]["piso"] for c in cs]),
                        "sinais_total": ic([c["sinais_total"] for c in cs]),
                        "eficiencia_sinais": {"por_vida": efic, "chegaram": sum(e is not None for e in efic),
                                              **(ic([e for e in efic if e is not None]) if sum(e is not None for e in efic) >= 2 else {})},
                        "curva_media": [media(c["acerto"][d] for c in cs) for d in range(min(len(c["acerto"]) for c in cs))]}
    return {"por_vida": por_vida, "por_dono": resumo}


# ------------------------------------------------------------------ 5. G4: legibilidade


def legibilidade(vidas: dict, pol: str, ponto: dict | None, pasta: Path, boot: dict, fabrica_motor=None) -> dict:
    fab = fabrica(pol, ponto)
    por_vida: dict[str, Counter] = {}
    for nome, v in sorted(vidas.items()):
        log = LogDeEventos.de_jsonl((pasta / "vidas" / f"{nome}.jsonl").read_text(encoding="utf-8"))
        _, emb = motivos_de_vida(log, fab, v.semente_coorte) if fabrica_motor is None else _motivos_gr(log, fab, v, fabrica_motor)
        c = Counter()
        for m, d in zip(emb.motivos, emb.diagnosticos):
            lobo = d.get("lobo", "decisao" if d.get("valor_decidiu") else "impulsos")
            c["decisoes"] += 1
            c["com_fator"] += bool(m.fatores)
            c[f"{lobo}_decidiu"] += 1
            c[f"{lobo}_com_fator"] += bool(m.fatores)
            for f in m.fatores:
                c[f"fator:{f}"] += 1
        por_vida[nome] = c

    def fracoes(c: Counter) -> dict:
        n = c["decisoes"]
        return {"decisoes": n, "fracao_com_fator": c["com_fator"] / n,
                "fracao_decisao_decidiu": c["decisao_decidiu"] / n, "fracao_decisao_com_fator": c["decisao_com_fator"] / n,
                "fracao_impulsos_decidiu": (c["impulsos_decidiu"] + c["prior_decidiu"]) / n,
                "fracao_impulsos_com_fator": c["impulsos_com_fator"] / n,
                "fatores": {k.split(":", 1)[1]: v / n for k, v in c.items() if k.startswith("fator:")}}

    total = Counter()
    por_dono: dict[str, Counter] = {}
    por_semente: dict[int, Counter] = {}
    for nome, c in por_vida.items():
        total.update(c)
        por_dono.setdefault(nome.split("-")[0], Counter()).update(c)
        por_semente.setdefault(int(nome.split("@")[1]), Counter()).update(c)
    ic = ic_de(boot)
    aprendido_s = [fracoes(c)["fracao_decisao_com_fator"] for _, c in sorted(por_semente.items())]
    return {"total": fracoes(total), "por_dono": {d: fracoes(c) for d, c in sorted(por_dono.items())},
            "por_semente": {str(s): fracoes(c) for s, c in sorted(por_semente.items())},
            "aprendido_ic": ic(aprendido_s), "por_vida": {n: fracoes(c) for n, c in por_vida.items()}}


def _motivos_gr(log, fab, v, fabrica_motor):
    from digilab.motivo import PoliticaComMotivo, indices_eventos_dono
    indices = indices_eventos_dono(log)
    emb = []

    def f(c):
        p = PoliticaComMotivo(fab(c), indices)
        emb.append(p)
        return p

    motor = reproduzir_com_feedback(log, f, semente=v.semente_coorte, fabrica_motor=fabrica_motor)
    return motor, emb[0]


# ------------------------------------------------------------------ 6. G6: deriva


def deriva(vidas: dict, ponto: dict, pasta: Path, sonda: dict, dias_deriva) -> dict:
    fab = fabrica("lobos", ponto)
    estados = estados_sonda(sonda["estados"], sonda["semente"])
    d_inst = distribuicoes_de_acao(PoliticaInstinto(), estados, sonda["amostras"], sonda["semente"])
    serie, fim = {}, {}
    for nome, v in sorted(vidas.items()):
        log = LogDeEventos.de_jsonl((pasta / "vidas" / f"{nome}.jsonl").read_text(encoding="utf-8"))
        pontos = {}
        for d in dias_deriva:
            pol = politica_no_tick(log, fab, v.semente_coorte, d * TICKS_POR_DIA)
            pontos[str(d)] = jsd_media(distribuicoes_de_acao(pol, estados, sonda["amostras"], sonda["semente"]), d_inst)
        serie[nome] = pontos
        p = v.motor.politica
        fim[nome] = {"desvio_maximo": p.desvio_maximo(), "pesos_no_teto": p.pesos_no_teto(),
                     "cortes_teto": p.estado_interno()["aprendizado"]["cortes_teto"],
                     "n_atualizacoes": p.estado_interno()["aprendizado"]["n_atualizacoes"]}
    medias = {str(d): media(serie[n][str(d)] for n in serie) for d in dias_deriva}
    return {"por_vida": serie, "media_por_dia": medias, "fim": fim,
            "razao_14_7": medias["14"] / medias["7"] if medias["7"] > 0 else None,
            "vidas_com_peso_no_teto": sum(1 for f in fim.values() if f["pesos_no_teto"] > 0)}


# ------------------------------------------------------------------ 7. gates


def gates(div_lobos: dict, leg_lobos: dict, der: dict, g: dict) -> dict:
    prim = div_lobos["primario_atencioso_x_relapso"]
    g3 = {"media": prim["media"], "ic_inferior": prim["ic_inferior"], "ic_superior": prim["ic_superior"],
          "minimo_media": g["g3_media_min"], "minimo_ic": g["g3_ic_min"],
          "passa": prim["media"] >= g["g3_media_min"] and prim["ic_inferior"] > g["g3_ic_min"]}
    apr = leg_lobos["total"]["fracao_decisao_com_fator"]
    g4 = {"fracao_aprendido_com_fator": apr, "ic": leg_lobos["aprendido_ic"],
          "fracao_bruta_com_fator": leg_lobos["total"]["fracao_com_fator"],
          "fracao_aprendido_decidiu": leg_lobos["total"]["fracao_decisao_decidiu"],
          "minimo": g["g4_min"], "passa": apr >= g["g4_min"]}
    g5 = {"nota": "desenho da arena v1: sem morte e sem lesao por construcao; G5(a) = G3. (b): braco de educacao; (c): acoplado",
          "passa_a": g3["passa"]}
    g6 = {"razao_14_7": der["razao_14_7"], "maximo_razao": g["g6_razao_max"], "vidas_com_peso_no_teto": der["vidas_com_peso_no_teto"],
          "passa_a": der["razao_14_7"] is not None and der["razao_14_7"] <= g["g6_razao_max"],
          "passa_b": der["vidas_com_peso_no_teto"] == 0}
    g6["passa"] = g6["passa_a"] and g6["passa_b"]
    return {"G3": g3, "G4": g4, "G5": g5, "G6": g6}


def gate_g5b(edu: dict, g: dict) -> dict:
    ii = edu["leitura_ii_sem_lesao_nem_morte"]
    if ii["n_sementes"] < 3:
        return {"resultado": "insuficiente", "n_sementes": ii["n_sementes"], "passa": None}
    return {"resultado": "medido", "n_sementes": ii["n_sementes"], "media": ii["media"], "ic_inferior": ii["ic_inferior"],
            "passa": ii["ic_inferior"] > g["g3_ic_min"]}


# ------------------------------------------------------------------ 8. braco de educacao (G5 b)


def braco_educacao(ponto: dict, sementes, dias: int, pasta: Path, sonda: dict, boot: dict) -> dict:
    fp = fabrica("lobos", ponto)
    dir_vidas = pasta / "vidas"
    pets, politicas = {}, {}
    for s in sementes:
        esp, temp_ovo = ovo(s)
        tmp = sortear(s)
        for dono in DONOS:
            _, fm_base = fabricas_educacao(s, esp, tmp, ce=CONFIG_EDUCACAO_LIGADA, cl=CONFIG_LESOES_LIGADA, politica_fabrica=fp)
            pet = PetDaVida(dono, s, esp, temp_ovo, fp, fm_base)
            v = simular_vida_educacao(dono, s, dias, esp, tmp, cl=CONFIG_LESOES_LIGADA, sparring=ticks_sparring(dono),
                                      rival_sparring=pet.rival, lutador_do_pet=pet.lutador, rival_por_nome=rival_por_nome,
                                      politica_fabrica=fp)
            m = v.motor
            nome = f"{dono}@{s}"
            salvo = _gravar_vida(dir_vidas, nome, m)
            pet2 = PetDaVida(dono, s, esp, temp_ovo, fp, fm_base)
            _, fm2 = fabricas_educacao(s, esp, tmp, ce=CONFIG_EDUCACAO_LIGADA, cl=CONFIG_LESOES_LIGADA, politica_fabrica=fp,
                                       lutador_do_pet=pet2.lutador, rival_por_nome=rival_por_nome)
            r = reproduzir_educacao(LogDeEventos.de_jsonl((dir_vidas / f"{nome}.jsonl").read_text(encoding="utf-8")), fp,
                                    semente=s, fabrica_motor=fm2)
            if (r.estado() != m.estado() or r.historico_lutas != m.historico_lutas
                    or json.loads(json.dumps(r.politica.estado_interno(), sort_keys=True)) != salvo):
                raise ReplayDivergiu(f"educacao {nome}: replay divergiu")
            lesoes = sum(x["lesao"] for x in m.historico_lutas)
            pets[nome] = {"dono": dono, "semente": s, "especie": esp, "morta": v.morta, "morte": m.morte, "lesoes": lesoes,
                          "lutas": len(m.historico_lutas), "interacoes": v.interacoes, "tick_final": m.estado()["tick"],
                          "sem_lesao_nem_morte": lesoes == 0 and not v.morta,
                          "desvio_maximo": m.politica.desvio_maximo(), "pesos_no_teto": m.politica.pesos_no_teto(),
                          "n_atualizacoes": m.politica.estado_interno()["aprendizado"]["n_atualizacoes"]}
            politicas[nome] = m.politica
    politicas["instinto"] = PoliticaInstinto()
    estados = estados_sonda(sonda["estados"], sonda["semente"])
    div, _ = divergencia_politicas(politicas, estados, sonda["amostras"], sonda["semente"])
    ic = lambda xs: bootstrap_ic(xs, boot["reamostragens"], boot["semente"], boot["nivel"]) if len(xs) >= 2 else {}  # noqa: E731
    todos = [par(div, f"atencioso@{s}", f"relapso@{s}") for s in sementes]
    limpos_s = [s for s in sementes if pets[f"atencioso@{s}"]["sem_lesao_nem_morte"] and pets[f"relapso@{s}"]["sem_lesao_nem_morte"]]
    limpos = [par(div, f"atencioso@{s}", f"relapso@{s}") for s in limpos_s]
    return {
        "pets": pets,
        "mortes": sum(p["morta"] for p in pets.values()), "pets_com_lesao": sum(p["lesoes"] > 0 for p in pets.values()),
        "leitura_i_todos": {"por_semente": dict(zip(map(str, sementes), todos)), **ic(todos)},
        "leitura_ii_sem_lesao_nem_morte": {"sementes": limpos_s, "por_semente": dict(zip(map(str, limpos_s), limpos)),
                                           **ic(limpos), "n_sementes": len(limpos_s)},
        "jsd_vs_instinto": {n: par(div, n, "instinto") for n in pets},
    }


# ------------------------------------------------------------------ 9. norma de reacao (3.2)


def norma(ponto: dict, sementes, conjunto: str, n_ambientes: int, dias: int, orcamento: int, pasta: Path, sonda: dict,
          boot: dict) -> dict:
    """ovo (semente) x ambiente (semente derivada) x condicao {ensino, cuidado, instinto}; y = G3-T (ultimos 7 dias) e JSD vs instinto."""
    ambientes = {f"amb{k}": derivar_semente("ambiente-v2-l1", conjunto, k) for k in range(1, n_ambientes + 1)}
    estados = estados_sonda(sonda["estados"], sonda["semente"])
    d_inst = distribuicoes_de_acao(PoliticaInstinto(), estados, sonda["amostras"], sonda["semente"])
    y = {"ensino": {}, "cuidado": {}, "instinto": {}}
    yj = {"ensino": {}, "cuidado": {}, "instinto": {}}
    dir_vidas = pasta / "vidas"
    vidas_meta = {}
    for g in sementes:
        for c in y:
            y[c][str(g)] = {}
            yj[c][str(g)] = {}
        for amb, r in ambientes.items():
            fm = lambda politica, cfg, s, r=r: MotorGR(politica, cfg, s, r)  # noqa: E731
            fab_l, fab_i = fabrica("lobos", ponto), fabrica("instinto", None)
            v_l = simular_vida(f"ensino-{amb}", criar_dono("atencioso"), fab_l(), g, dias, orcamento,
                               rotulo_dono=f"atencioso#{amb}", fabrica_motor=fm)
            v_i = simular_vida(f"instinto-{amb}", criar_dono("atencioso"), fab_i(), g, dias, orcamento,
                               rotulo_dono=f"atencioso#{amb}", fabrica_motor=fm)
            log_c = log_so_cuidado(v_l.motor.log)
            m_c = reproduzir_com_feedback(log_c, fab_l, semente=g, fabrica_motor=fm)
            for nome, motor, fab in ((f"ensino-{amb}@{g}", v_l.motor, fab_l), (f"instinto-{amb}@{g}", v_i.motor, fab_i),
                                     (f"cuidado-{amb}@{g}", m_c, fab_l)):
                salvo = _gravar_vida(dir_vidas, nome, motor)
                log = LogDeEventos.de_jsonl((dir_vidas / f"{nome}.jsonl").read_text(encoding="utf-8"))
                _conferir_replay(nome, motor, reproduzir_com_feedback(log, fab, semente=g, fabrica_motor=fm), salvo)
                cond = nome.split("-")[0]
                curva = curva_tarefa(log, fab, g, fm)
                y[cond][str(g)][amb] = curva["ultimos_7"]
                yj[cond][str(g)][amb] = jsd_media(distribuicoes_de_acao(motor.politica, estados, sonda["amostras"], sonda["semente"]), d_inst)
                vidas_meta[nome] = {"ovo": g, "ambiente": amb, "semente_ambiente": r, "condicao": cond,
                                    "interacoes": sum(1 for e in log if e.tipo == "acao_usuario"),
                                    "sinais": curva["sinais_total"], "acerto_ultimos_7": curva["ultimos_7"]}
    ic = ic_de(boot)
    saida = {"ambientes": ambientes, "ovos": list(sementes), "vidas": vidas_meta, "medidas": {}}
    for nome_y, dados in (("acerto_ultimos_7", y), ("jsd_vs_instinto", yj)):
        res = {}
        for a, b in (("ensino", "cuidado"), ("ensino", "instinto"), ("cuidado", "instinto")):
            n = norma_de_reacao(dados, a, b)
            dif = n["diferenca_por_ovo"]
            res[f"{a}_menos_{b}"] = {"delta_alpha": ic([dif[g]["alpha"] for g in n["ovos"]]),
                                     "delta_beta": ic([dif[g]["beta"] for g in n["ovos"]]), "por_ovo": dif}
        n = norma_de_reacao(dados, "ensino", "cuidado")
        res["z"] = n["z"]
        res["medias"] = n["medias"]
        res["celulas"] = n["celulas"]
        res["valores"] = dados
        saida["medidas"][nome_y] = res
    return saida


# ------------------------------------------------------------------ um ponto


def rodar_ponto(ponto: dict, base: dict, sementes, cfg: dict, pasta: Path) -> dict:
    t0 = time.perf_counter()
    vidas = vidas_arena("lobos", ponto, sementes, cfg["dias"], cfg["orcamento"], pasta)
    div_por_pol = divergencia({"lobos": vidas, **base["vidas"]}, {}, sementes, cfg["sonda"], cfg["bootstrap"])
    leg = {"lobos": legibilidade(vidas, "lobos", ponto, pasta, cfg["bootstrap"]), **base["legibilidade"]}
    tar = {"lobos": tarefa(vidas, "lobos", ponto, pasta, base["piso_tarefa"], cfg["bootstrap"]), **base["tarefa"]}
    der = deriva(vidas, ponto, pasta, cfg["sonda"], cfg["dias_deriva"])
    gs = gates(div_por_pol["lobos"], leg["lobos"], der, cfg["gates"])
    resultado = {"ponto": ponto, "sementes": list(sementes), "gates": gs, "divergencia": div_por_pol,
                 "legibilidade_total": {p: {k: v for k, v in leg[p]["total"].items() if k != "fatores"} for p in leg},
                 "tarefa_por_dono": {p: tar[p]["por_dono"] for p in tar},
                 "deriva_media_por_dia": der["media_por_dia"], "deriva_fim": der["fim"], "segundos": time.perf_counter() - t0}
    _gravar(pasta / "resultado.json", _dump(resultado))
    _gravar(pasta / "divergence.json", _dump(div_por_pol))
    _gravar(pasta / "legibilidade.json", _dump(leg))
    _gravar(pasta / "tarefa.json", _dump(tar))
    _gravar(pasta / "deriva.json", _dump(der))
    return resultado, vidas


def complementos(ponto: dict, vidas_lobos: dict, base: dict, sementes, cfg: dict, pasta: Path, escolha: dict) -> None:
    """So no ponto escolhido: controle sem lobos (D2), acoplado (D4, G5 c), norma de reacao (3.2), educacao (3.1)."""
    boot = cfg["bootstrap"]
    ic = ic_de(boot)
    t0 = time.perf_counter()
    # controle sem lobos
    ctrl = vidas_arena("controle", ponto, sementes, cfg["dias"], cfg["orcamento"], pasta / "controle")
    leg_c = legibilidade(ctrl, "controle", ponto, pasta / "controle", boot)
    tar_c = tarefa(ctrl, "controle", ponto, pasta / "controle", base["piso_tarefa"], boot)
    leg_l = json.loads((pasta / "legibilidade.json").read_text(encoding="utf-8"))["lobos"]
    tar_l = json.loads((pasta / "tarefa.json").read_text(encoding="utf-8"))["lobos"]
    dif_g4 = [leg_l["por_semente"][str(s)]["fracao_decisao_com_fator"] - leg_c["por_semente"][str(s)]["fracao_decisao_com_fator"] for s in sementes]
    dif_t = [tar_l["por_vida"][f"atencioso-lobos@{s}"]["ultimos_7"] - tar_c["por_vida"][f"atencioso-controle@{s}"]["ultimos_7"] for s in sementes]
    custo = {"g4_aprendido_lobos_menos_controle": {"por_semente": dict(zip(map(str, sementes), dif_g4)), **ic(dif_g4),
                                                   "modularidade_compra_legibilidade": ic(dif_g4)["ic_inferior"] > 0},
             "custo_gargalo_g3t_atencioso_lobos_menos_controle": {"por_semente": dict(zip(map(str, sementes), dif_t)), **ic(dif_t)},
             "controle": {"legibilidade_total": leg_c["total"], "tarefa_por_dono": tar_c["por_dono"]}}
    _gravar(pasta / "controle" / "legibilidade.json", _dump(leg_c))
    _gravar(pasta / "controle" / "tarefa.json", _dump(tar_c))
    _gravar(pasta / "custo_gargalo.json", _dump(custo))
    # acoplado e variante
    acop = {"cuidado": vidas_acopladas(vidas_lobos, ponto, sementes, pasta / "acoplado", False),
            "cuidado-semcarinho": vidas_acopladas(vidas_lobos, ponto, sementes, pasta / "acoplado", True)}
    div = divergencia({"lobos": vidas_lobos, "controle": ctrl, **base["vidas"]}, acop, sementes, cfg["sonda"], boot)
    tar_a = {p: tarefa(v, p, ponto, pasta / "acoplado", base["piso_tarefa"], boot) for p, v in acop.items()}
    so_cuidado = {p: {"volume": {n: {"interacoes": v.interacoes, "origem": v.origem,
                                    "interacoes_origem": vidas_lobos[v.origem].interacoes} for n, v in acop[p].items()},
                      "divergencia": div[p], "tarefa_por_dono": tar_a[p]["por_dono"]} for p in acop}
    _gravar(pasta / "so_cuidado.json", _dump(so_cuidado))
    _gravar(pasta / "divergence.json", _dump(div))
    escolha["gates"]["G5"]["c"] = {"delta": div["cuidado"]["g5c_ensino_menos_acoplado"],
                                   "passa": div["cuidado"]["g5c_ensino_menos_acoplado"]["ic_inferior"] > 0}
    escolha["gates"]["G5"]["passa"] = escolha["gates"]["G5"]["passa_a"] and escolha["gates"]["G5"]["c"]["passa"]
    escolha["custo_gargalo"] = {k: v for k, v in custo.items() if k != "controle"}
    escolha["divergencia_controle"] = div["controle"]["primario_atencioso_x_relapso"]
    # norma de reacao
    nr = norma(ponto, sementes, cfg["conjunto"], cfg["n_ambientes"], cfg["dias"], cfg["orcamento"], pasta / "norma", cfg["sonda"], boot)
    _gravar(pasta / "norma_de_reacao.json", _dump(nr))
    escolha["norma_de_reacao"] = {m: {k: {"delta_alpha": v["delta_alpha"], "delta_beta": v["delta_beta"]}
                                      for k, v in nr["medidas"][m].items() if k.endswith("_menos_cuidado") or k.endswith("_menos_instinto")}
                                  for m in nr["medidas"]}
    print(f"[complementos] controle G3 {div['controle']['primario_atencioso_x_relapso']['media']:.4f}; "
          f"G4 lobos-controle {ic(dif_g4)['media']:+.3f} [{ic(dif_g4)['ic_inferior']:+.3f}]; "
          f"custo gargalo {ic(dif_t)['media']:+.3f}; G5c {div['cuidado']['g5c_ensino_menos_acoplado']['media']:+.4f} "
          f"[{div['cuidado']['g5c_ensino_menos_acoplado']['ic_inferior']:+.4f}] ({time.perf_counter() - t0:.0f} s)", flush=True)
    if cfg["educacao"]:
        edu = braco_educacao(ponto, sementes, cfg["dias"], pasta / "educacao", cfg["sonda"], boot)
        escolha["gates"]["G5"]["b"] = gate_g5b(edu, cfg["gates"])
        _gravar(pasta / "educacao" / "resultado.json", _dump(edu))
        print(f"[educacao] mortes {edu['mortes']}, pets com lesao {edu['pets_com_lesao']}, leitura ii: {escolha['gates']['G5']['b']}", flush=True)


def chave_escolha(r: dict) -> tuple:
    """Regra da secao 5 do plano: G6 e G4 (do aprendido) passando > maior IC inferior do G3 > menor passo > menor teto."""
    g = r["gates"]
    nivel = 2 if (g["G6"]["passa"] and g["G4"]["passa"]) else (1 if g["G6"]["passa"] else 0)
    if nivel > 0:
        valor = g["G3"]["ic_inferior"]
    else:
        valor = -(g["G6"]["razao_14_7"] if g["G6"]["razao_14_7"] is not None else float("inf"))
    return (nivel, valor, -r["ponto"]["passo"], -r["ponto"]["teto"])


def meta(cfg: dict, caminho_cfg: Path) -> dict:
    return {
        "config": str(caminho_cfg), "config_sha256": _sha(caminho_cfg), "descricao": cfg.get("descricao"),
        "conjunto": cfg["conjunto"], "sementes": cfg["sementes"],
        "sha256": {"digilab/policies/lobos.py": _sha(RAIZ / "digilab" / "policies" / "lobos.py"),
                   "digilab/policies/camada_unica.py": _sha(RAIZ / "digilab" / "policies" / "camada_unica.py"),
                   "digilab/config.py": _sha(RAIZ / "digilab" / "config.py"),
                   "digilab/motivo.py": _sha(RAIZ / "digilab" / "motivo.py"),
                   "digilab/metrics.py": _sha(RAIZ / "digilab" / "metrics.py"),
                   "digilab/engine.py": sha256_engine(), "engine_congelado": ENGINE_SHA256_V0},
        "python": platform.python_version(), "plataforma": platform.platform(),
        "config_lobos_base": {k: getattr(CONFIG_LOBOS, k) for k in ("bits_ponto_fixo", "piso_peso", "janela_latencia_ticks",
                                                                     "recompensa_pedido_ignorado", "recompensa_elogio",
                                                                     "recompensa_repreensao", "escala_ticks_desde_cuidado")},
        "sonda": cfg["sonda"], "bootstrap": cfg["bootstrap"], "gates": cfg["gates"], "dias": cfg["dias"], "orcamento": cfg["orcamento"],
        "n_ambientes": cfg["n_ambientes"],
    }


def carregar(caminho: Path) -> dict:
    cfg = json.loads(caminho.read_text(encoding="utf-8"))
    desconhecidas = set(cfg) - CHAVES_CONFIG
    if desconhecidas:
        raise KeyError(f"chaves desconhecidas no config: {sorted(desconhecidas)}")
    if cfg["conjunto"] not in ("calibracao", "validacao"):
        raise ValueError("conjunto precisa ser calibracao ou validacao")
    if sha256_engine() != ENGINE_SHA256_V0:
        raise RuntimeError("engine.py foi alterado")
    esperadas = SEMENTES_CALIBRACAO if cfg["conjunto"] == "calibracao" else SEMENTES_VALIDACAO
    if tuple(cfg["sementes"]) != esperadas:
        raise ValueError(f"sementes de {cfg['conjunto']} precisam ser {esperadas}")
    cfg.setdefault("dias", PROTOCOLO_ARENA_V1.v("dias_simulados"))
    cfg.setdefault("orcamento", PROTOCOLO_ARENA_V1.v("orcamento_interacoes"))
    cfg.setdefault("sonda", {"estados": PROTOCOLO_ARENA_V1.v("estados_sonda"), "amostras": PROTOCOLO_ARENA_V1.v("amostras_por_estado"),
                             "semente": PROTOCOLO_ARENA_V1.v("semente_sonda")})
    cfg.setdefault("bootstrap", {"reamostragens": 10000, "semente": 20261001, "nivel": 0.95})
    cfg.setdefault("gates", {"g3_media_min": 0.10, "g3_ic_min": 0.02, "g4_min": 0.5, "g6_razao_max": 1.5})
    cfg.setdefault("dias_deriva", list(range(1, 15)))
    cfg.setdefault("educacao", True)
    cfg.setdefault("n_ambientes", 4)
    if cfg["conjunto"] == "validacao" and "ponto" not in cfg:
        raise ValueError("validacao precisa do ponto escolhido na calibracao")
    if cfg["conjunto"] == "calibracao" and "grade" not in cfg:
        raise ValueError("calibracao precisa da grade")
    return cfg


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    args = ap.parse_args(argv)
    caminho = Path(args.config)
    cfg = carregar(caminho)
    saida = RAIZ / cfg["saida"]
    if cfg["conjunto"] == "validacao" and saida.exists():
        raise RuntimeError(f"{saida} ja existe: a validacao roda uma vez so")
    saida.mkdir(parents=True, exist_ok=True)
    _gravar(saida / "meta.json", _dump(meta(cfg, caminho)))
    sementes = tuple(cfg["sementes"])
    t0 = time.perf_counter()

    # bracos que nao dependem do ponto: instinto (so cuidado sem aprendizado, piso do G3-T) e bandit (referencia v1)
    base = {"vidas": {}, "legibilidade": {}, "tarefa": {}, "piso_tarefa": None}
    for pol in ("instinto", "bandit"):
        pasta = saida / "base" / pol
        base["vidas"][pol] = vidas_arena(pol, None, sementes, cfg["dias"], cfg["orcamento"], pasta)
        base["legibilidade"][pol] = legibilidade(base["vidas"][pol], pol, None, pasta, cfg["bootstrap"])
        base["tarefa"][pol] = tarefa(base["vidas"][pol], pol, None, pasta, base["piso_tarefa"], cfg["bootstrap"])
        if pol == "instinto":
            base["piso_tarefa"] = {n: c["acerto_total"] for n, c in base["tarefa"][pol]["por_vida"].items()}
        _gravar(pasta / "legibilidade.json", _dump(base["legibilidade"][pol]))
        _gravar(pasta / "tarefa.json", _dump(base["tarefa"][pol]))
        print(f"[base] {pol}: {len(base['vidas'][pol])} vidas, com fator {base['legibilidade'][pol]['total']['fracao_com_fator']:.3f}, "
              f"G3-T atencioso {base['tarefa'][pol]['por_dono']['atencioso']['ultimos_7']['media']:.3f}", flush=True)

    if cfg["conjunto"] == "calibracao":
        resultados, vidas_por_ponto = [], {}
        with (saida / "varredura.jsonl").open("w", encoding="utf-8", newline="\n") as f:
            for passo in cfg["grade"]["passo"]:
                for teto in cfg["grade"]["teto"]:
                    ponto = {"passo": int(passo), "teto": int(teto)}
                    r, vidas = rodar_ponto(ponto, base, sementes, cfg, saida / f"passo{passo}_teto{teto}")
                    g = r["gates"]
                    linha = {"ponto": ponto, "G3_media": g["G3"]["media"], "G3_ic_inferior": g["G3"]["ic_inferior"],
                             "G3_passa": g["G3"]["passa"], "G4_aprendido": g["G4"]["fracao_aprendido_com_fator"],
                             "G4_bruto": g["G4"]["fracao_bruta_com_fator"], "G4_passa": g["G4"]["passa"],
                             "G3T_atencioso_ultimos_7": r["tarefa_por_dono"]["lobos"]["atencioso"]["ultimos_7"]["media"],
                             "G6_razao_14_7": g["G6"]["razao_14_7"], "G6_vidas_no_teto": g["G6"]["vidas_com_peso_no_teto"],
                             "G6_passa": g["G6"]["passa"], "segundos": r["segundos"]}
                    f.write(json.dumps(linha, sort_keys=True) + "\n")
                    f.flush()
                    resultados.append(r)
                    vidas_por_ponto[(ponto["passo"], ponto["teto"])] = vidas
                    print(f"[grade] passo {passo} teto {teto}: G3 {g['G3']['media']:.4f} [{g['G3']['ic_inferior']:.4f}] "
                          f"G4 apr {g['G4']['fracao_aprendido_com_fator']:.3f} bruto {g['G4']['fracao_bruta_com_fator']:.3f} "
                          f"G3-T {linha['G3T_atencioso_ultimos_7']:.3f} G6 {g['G6']['razao_14_7']:.3f} teto {g['G6']['vidas_com_peso_no_teto']} "
                          f"({r['segundos']:.0f} s)", flush=True)
        escolhido = max(resultados, key=chave_escolha)
        nivel = chave_escolha(escolhido)[0]
        ponto = escolhido["ponto"]
        escolha = {"ponto": ponto, "gates": escolhido["gates"],
                   "regra": "secao 5 do plano (rev. 2): G6 e G4 do aprendido passando, maior IC inferior do G3; empate: menor passo, menor teto",
                   "calibracao_fechou": nivel == 2,
                   "nota": {2: "G6 e G4 passam no ponto escolhido", 1: "nenhum ponto passa G4 com G6: escolhido pelo G3 entre os que passam G6",
                            0: "nenhum ponto passa G6: escolhido pela menor razao 14/7; a calibracao nao fechou"}[nivel]}
        pasta_ponto = saida / f"passo{ponto['passo']}_teto{ponto['teto']}"
        vidas_lobos = vidas_por_ponto[(ponto["passo"], ponto["teto"])]
    else:
        ponto = {"passo": int(cfg["ponto"]["passo"]), "teto": int(cfg["ponto"]["teto"])}
        pasta_ponto = saida / "ponto"
        r, vidas_lobos = rodar_ponto(ponto, base, sementes, cfg, pasta_ponto)
        escolha = {"ponto": ponto, "gates": r["gates"]}

    complementos(ponto, vidas_lobos, base, sementes, cfg, pasta_ponto, escolha)
    escolha["segundos_total"] = time.perf_counter() - t0
    _gravar(saida / "escolha.json", _dump(escolha))
    g = escolha["gates"]
    print(f"[{cfg['conjunto']}] ponto {ponto}: G3 {'PASSA' if g['G3']['passa'] else 'FALHA'} ({g['G3']['media']:.4f} "
          f"[{g['G3']['ic_inferior']:.4f}, {g['G3']['ic_superior']:.4f}]), G4 {'PASSA' if g['G4']['passa'] else 'FALHA'} "
          f"(aprendido {g['G4']['fracao_aprendido_com_fator']:.3f}, bruto {g['G4']['fracao_bruta_com_fator']:.3f}), "
          f"G5 {'PASSA' if g['G5']['passa'] else 'FALHA'}, G6 {'PASSA' if g['G6']['passa'] else 'FALHA'} "
          f"(razao {g['G6']['razao_14_7']:.3f}, vidas no teto {g['G6']['vidas_com_peso_no_teto']})")
    return 0 if (g["G3"]["passa"] and g["G4"]["passa"] and g["G5"]["passa"]) else 2


if __name__ == "__main__":
    sys.exit(main())
