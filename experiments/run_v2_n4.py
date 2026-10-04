"""V2, N4: frutas no mundo, sem aprendizado de politica (docs/PLANO_ANALISE_V2_N4.md, registrado antes da run).

    python experiments/run_v2_n4.py --config experiments/configs/v2_n4/calibracao.json   # grade, sementes 10101...10505
    python experiments/run_v2_n4.py --config experiments/configs/v2_n4/validacao.json    # UMA vez, 11101...11505

Fluxo por ponto (w_fruta, k_saciedade, duracao_min):
  1. vidas    - arena v1 (4 donos, 224 interacoes, 14 dias), MotorFrutas com obediencia, educacao, lesoes e bola desligadas,
                temperamento neutro, especie brasa; o mesmo dono com a mesma rng em todos os bracos. Ofertas pelo cronograma, FORA do
                orcamento e do sorteio do dono (B1, B2). Bracos: frutas (descasado), semfrutas (nao depende do ponto) e, so no ponto
                escolhido e na validacao, iguais (efeito igual, F7).
  2. replay   - toda vida rejogada do log gravado e conferida bit a bit (estado, acoes, rngs, registros das frutas) (G1).
  3. acoplado - o log de cada vida `frutas` sem elogiar e repreender (as mesmas ofertas e o mesmo cuidado), rejogado (G-F7);
                variante sem carinho so no ponto escolhido e na validacao.
  4. gates    - G-SEP (i, ii), G-SSE, G-F7 (plano, secao 2); escolha do ponto pela regra da secao 4.
Divergencia de replay levanta erro e para tudo. Nenhuma metrica fora de digilab/metrics.py.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import time
from dataclasses import asdict, replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab.config import CONFIG_FRUTAS_LIGADA, CONFIG_PADRAO, ConfigFrutas  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.events import FRUTAS, AcaoUsuario, LogDeEventos  # noqa: E402
from digilab.frutas import OfertasFrutas, fabricas_frutas, reproduzir_frutas, simular_vida_frutas  # noqa: E402
from digilab.metrics import (bootstrap_ic, comer_por_incentivo, escolha_por_incentivo, privacao_nas_decisoes,  # noqa: E402
                             saciedade_especifica)
from digilab.protocol import ENGINE_SHA256_V0, PROTOCOLO_ARENA_V1, sha256_engine  # noqa: E402

SEMENTES_CALIBRACAO = (10101, 10202, 10303, 10404, 10505)
SEMENTES_VALIDACAO = (11101, 11202, 11303, 11404, 11505)
DONOS = ("atencioso", "relapso", "aleatorio", "incoerente")
DIAS = PROTOCOLO_ARENA_V1.dias_simulados.valor
ORCAMENTO = PROTOCOLO_ARENA_V1.orcamento_interacoes.valor
BOOT = {"reamostragens": 10_000, "semente": 20261001, "nivel": 0.95}
FAIXA_P_COMER = (0.30, 0.80)
SINAIS = (AcaoUsuario.ELOGIAR.value, AcaoUsuario.REPREENDER.value)


class ReplayDivergiu(RuntimeError):
    pass


def _dump(obj) -> str:
    return json.dumps(obj, indent=1, ensure_ascii=False, sort_keys=True) + "\n"


def _gravar(caminho: Path, texto: str) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(texto, encoding="utf-8", newline="\n")


def _sha(caminho: Path) -> str:
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


def ic(xs) -> dict:
    return bootstrap_ic(list(xs), BOOT["reamostragens"], BOOT["semente"], BOOT["nivel"])


def media(xs) -> float:
    xs = list(xs)
    if not xs:
        raise ValueError("media de lista vazia")
    return sum(xs) / len(xs)


def nome_ponto(p: dict) -> str:
    return f"w{p['w_fruta']}_k{p['k_saciedade']}_d{p['duracao_min']}"


def cfg_frutas(p: dict, mundo: str = "descasado") -> ConfigFrutas:
    return replace(CONFIG_FRUTAS_LIGADA, w_fruta=p["w_fruta"], k_saciedade=p["k_saciedade"], duracao_min=p["duracao_min"], mundo=mundo)


# ------------------------------------------------------------------ gravador (so no replay)


class _Gravadora:
    """Embrulha a politica no replay e anota as necessidades em cada decisao. So repassa: nenhuma rng a mais."""

    def __init__(self, interna) -> None:
        self.interna = interna
        self.nome = interna.nome
        self.decisoes: list[tuple] = []

    def agir(self, obs, rng):
        a = self.interna.agir(obs, rng)
        v = obs.vetor_estado
        self.decisoes.append((len(self.decisoes), v[0], v[1], v[2], v[3]))
        return a

    def observar(self, transicao):
        self.interna.observar(transicao)

    def receber_acao_dono(self, acao, tick):
        self.interna.receber_acao_dono(acao, tick)

    def estado_interno(self):
        return self.interna.estado_interno()

    def __getattr__(self, nome):
        return getattr(self.interna, nome)


def _nucleo(m) -> tuple:
    return (m._estado, tuple(m.acoes_recentes(10**9)), m._rng_politica.getstate(), m._rng_ambiente.getstate())


def medir(m_vivo, log: LogDeEventos, fp, fm, semente: int, nome: str) -> dict:
    grav = []

    def fab(cfg=None):
        g = _Gravadora(fp(cfg))
        grav.append(g)
        return g

    r = reproduzir_frutas(log, fab, semente=semente, fabrica_motor=fm)
    if _nucleo(r) != _nucleo(m_vivo) or r.resumo_frutas() != m_vivo.resumo_frutas() or r.estado() != m_vivo.estado():
        raise ReplayDivergiu(f"{nome}: o replay do log diverge da vida")
    tick = CONFIG_PADRAO.intervalo_decisao_ticks
    priv = privacao_nas_decisoes([(k * tick, f, h, e, hu) for k, f, h, e, hu in grav[0].decisoes], CONFIG_PADRAO.limiar_privacao)
    rf = m_vivo.resumo_frutas()
    acoes = {}
    for e in log:
        if e.tipo == "acao_usuario":
            acoes[str(e.valor)] = acoes.get(str(e.valor), 0) + 1
    out = {"privacao": priv, "saude_final": m_vivo._estado.saude, "humor_final": m_vivo._estado.humor, "morte": m_vivo.morte,
           "acoes_dono": acoes}
    if rf["ligada"]:
        linhas = rf["ofertas"]
        ruim = [f for f, v in rf["efeito_humor"].items() if v < 0]
        out.update({
            "genoma": rf["genoma"], "contagem": rf["contagem"], "efeito_humor": rf["efeito_humor"],
            "sep_i": comer_por_incentivo([(o["regra"], True, o["visto"], o["acao"]) for o in linhas]),
            "sep_ii": escolha_por_incentivo([(o["presentes"], o["incentivos"], o["escolhida"]) for o in linhas]),
            "consumos": [(c["avaliacao"], c["consumo_recente_antes"], c["fome_antes"]) for c in rf["consumos"]],
            "comidas_por_fruta": {f: sum(c["fruta"] == f for c in rf["consumos"]) for f in FRUTAS},
            "fracao_fruta_ruim": (sum(c["fruta"] in ruim for c in rf["consumos"]) / len(rf["consumos"])) if rf["consumos"] and ruim else None,
            "primeiro_contato": rf["primeiro_contato"], "incentivo_final": rf["incentivo"], "avaliacao_final": rf["avaliacao"]})
    return out


def vidas_braco(braco: str, cf: ConfigFrutas, sementes, pasta: Path | None) -> tuple[dict, dict]:
    """(medidas por nome, logs por nome). frutas/iguais: com ofertas; semfrutas: chave ligada, nenhuma oferta."""
    fp, fm = fabricas_frutas(cfg_frutas=cf)
    medidas, logs = {}, {}
    for s in sementes:
        for dono in DONOS:
            nome = f"{dono}-{braco}@{s}"
            ofertas = None if braco == "semfrutas" else OfertasFrutas(cf)
            v = simular_vida_frutas(f"{dono}-{braco}", criar_dono(dono), fp(), s, DIAS, ORCAMENTO, fm, ofertas, rotulo_dono=dono)
            if v.interacoes != ORCAMENTO:
                raise RuntimeError(f"{nome}: {v.interacoes} interacoes no canal, orcamento {ORCAMENTO}")
            texto = v.motor.log.para_jsonl()
            if pasta is not None:
                _gravar(pasta / "vidas" / f"{nome}.jsonl", texto)
                texto = (pasta / "vidas" / f"{nome}.jsonl").read_text(encoding="utf-8")
            log = LogDeEventos.de_jsonl(texto)
            m = medir(v.motor, log, fp, fm, s, nome)
            m["ofertas"] = v.ofertas
            medidas[nome], logs[nome] = m, log
    return medidas, logs


def log_acoplado(log: LogDeEventos, sem_carinho: bool = False) -> LogDeEventos:
    """F7 (D4): o mesmo log sem elogio e bronca (e, na variante, sem acariciar): o mesmo cuidado e as mesmas ofertas nos mesmos ticks."""
    fora = set(SINAIS) | ({AcaoUsuario.ACARICIAR.value} if sem_carinho else set())
    return LogDeEventos([e for e in log if not (e.tipo == "acao_usuario" and str(e.valor) in fora)])


def acoplados(cf: ConfigFrutas, logs: dict, sementes, pasta: Path | None, sem_carinho: bool) -> dict:
    fp, fm = fabricas_frutas(cfg_frutas=cf)
    variante = "acoplado-semcarinho" if sem_carinho else "acoplado"
    saida = {}
    for s in sementes:
        for dono in DONOS:
            log = log_acoplado(logs[f"{dono}-frutas@{s}"], sem_carinho)
            nome = f"{dono}-{variante}@{s}"
            texto = log.para_jsonl()
            if pasta is not None:
                _gravar(pasta / "acoplado" / "vidas" / f"{nome}.jsonl", texto)
                texto = (pasta / "acoplado" / "vidas" / f"{nome}.jsonl").read_text(encoding="utf-8")
            m_vivo = reproduzir_frutas(log, fp, semente=s, fabrica_motor=fm)
            m = medir(m_vivo, LogDeEventos.de_jsonl(texto), fp, fm, s, nome)
            m["interacoes"] = sum(1 for e in log if e.tipo == "acao_usuario")
            saida[nome] = m
    return saida


# ------------------------------------------------------------------ resumos e gates


def _por_semente(medidas: dict, braco: str, sementes, f, faltas: list | None = None) -> list[float]:
    out = []
    for s in sementes:
        vals = []
        for d in DONOS:
            x = f(medidas[f"{d}-{braco}@{s}"])
            if x is None:
                if faltas is not None:
                    faltas.append(f"{d}-{braco}@{s}")
            else:
                vals.append(x)
        if not vals:
            raise ValueError(f"{braco}@{s}: nenhum dono com a medida definida")
        out.append(media(vals))
    return out


def resumo(frutas: dict, sem: dict, acop: dict, sementes) -> dict:
    s = list(sementes)
    faltas_i, faltas_ii = [], []
    sep_i = _por_semente(frutas, "frutas", s, lambda m: m["sep_i"]["delta"], faltas_i)
    sep_ii = _por_semente(frutas, "frutas", s, lambda m: m["sep_ii"]["delta"], faltas_ii)
    p_comer = _por_semente(frutas, "frutas", s, lambda m: m["sep_i"]["p_comer"])
    sse = [saciedade_especifica([c for d in DONOS for c in frutas[f"{d}-frutas@{x}"]["consumos"]]) for x in s]
    saude = [media(frutas[f"{d}-frutas@{x}"]["saude_final"] - acop[f"{d}-acoplado@{x}"]["saude_final"] for d in DONOS) for x in s]
    mortes_f = sum(m["morte"] is not None for m in frutas.values())
    mortes_a = sum(m["morte"] is not None for m in acop.values())
    priv = [media(frutas[f"{d}-frutas@{x}"]["privacao"]["fracao_privacao"] - sem[f"{d}-semfrutas@{x}"]["privacao"]["fracao_privacao"]
                  for d in DONOS) for x in s]
    humor = [media(frutas[f"{d}-frutas@{x}"]["privacao"]["humor_medio"] - sem[f"{d}-semfrutas@{x}"]["privacao"]["humor_medio"]
                   for d in DONOS) for x in s]
    saude_sem = [media(frutas[f"{d}-frutas@{x}"]["saude_final"] - sem[f"{d}-semfrutas@{x}"]["saude_final"] for d in DONOS) for x in s]
    ruim = _por_semente(frutas, "frutas", s, lambda m: m["fracao_fruta_ruim"])
    por_dono = {}
    for d in DONOS:
        ms = [frutas[f"{d}-frutas@{x}"] for x in s]
        por_dono[d] = {"ofertas": media(m["ofertas"] for m in ms), "comidas": media(m["contagem"]["comidas"] for m in ms),
                       "expiradas": media(m["contagem"]["expiradas"] for m in ms),
                       "p_comer": [m["sep_i"]["p_comer"] for m in ms], "sep_i": [m["sep_i"]["delta"] for m in ms],
                       "sep_ii": [m["sep_ii"]["delta"] for m in ms], "fracao_fruta_ruim": [m["fracao_fruta_ruim"] for m in ms],
                       "privacao": media(m["privacao"]["fracao_privacao"] for m in ms),
                       "privacao_semfrutas": media(sem[f"{d}-semfrutas@{x}"]["privacao"]["fracao_privacao"] for x in s),
                       "humor": media(m["privacao"]["humor_medio"] for m in ms),
                       "humor_semfrutas": media(sem[f"{d}-semfrutas@{x}"]["privacao"]["humor_medio"] for x in s),
                       "saude_final": media(m["saude_final"] for m in ms),
                       "saude_final_acoplado": media(acop[f"{d}-acoplado@{x}"]["saude_final"] for x in s)}
    return {"sep_i": {"por_semente": sep_i, **ic(sep_i)}, "sep_ii": {"por_semente": sep_ii, **ic(sep_ii)},
            "faltas_sep_i": faltas_i, "faltas_sep_ii": faltas_ii,
            "p_comer": {"por_semente": p_comer, **ic(p_comer)},
            "sse": {"por_semente": sse, "beta_recente": ic([x["beta_recente"] for x in sse]),
                    "beta_fome": ic([x["beta_fome"] for x in sse])},
            "f7_saude_frutas_menos_acoplado": {"por_semente": saude, **ic(saude)}, "mortes_frutas": mortes_f, "mortes_acoplado": mortes_a,
            "privacao_frutas_menos_semfrutas": {"por_semente": priv, **ic(priv)},
            "humor_frutas_menos_semfrutas": {"por_semente": humor, **ic(humor)},
            "saude_frutas_menos_semfrutas": {"por_semente": saude_sem, **ic(saude_sem)},
            "fracao_fruta_ruim": {"por_semente": ruim, **ic(ruim)}, "por_dono": por_dono}


def gates(r: dict) -> dict:
    f7 = r["f7_saude_frutas_menos_acoplado"]
    sep = {"i": r["sep_i"]["ic_inferior"] > 0, "ii": r["sep_ii"]["ic_inferior"] > 0}
    sse = {"beta_recente_ic": [r["sse"]["beta_recente"]["ic_inferior"], r["sse"]["beta_recente"]["ic_superior"]],
           "beta_fome_ic": [r["sse"]["beta_fome"]["ic_inferior"], r["sse"]["beta_fome"]["ic_superior"]]}
    sse["passa"] = sse["beta_recente_ic"][1] < 0 and sse["beta_fome_ic"][0] <= 0 <= sse["beta_fome_ic"][1]
    return {"G-SEP": {**sep, "passa": sep["i"] and sep["ii"]}, "G-SSE": sse,
            "G-F7": {"saude_ic": [f7["ic_inferior"], f7["ic_superior"]], "mortes": [r["mortes_frutas"], r["mortes_acoplado"]],
                     "passa": f7["ic_inferior"] <= 0 <= f7["ic_superior"] and r["mortes_frutas"] == r["mortes_acoplado"]},
            "G1": "replay do log bit a bit em toda vida (o orquestrador para se divergir)", "G2": "tests/test_frutas.py (a, b, c, d)",
            "1a-dono": "nao testada: sem apoio na literatura (D6)"}


def escolher(varredura: list[dict]) -> dict:
    def ok(v):
        g, p = v["gates"], v["resumo"]["p_comer"]["media"]
        return (FAIXA_P_COMER[0] <= p <= FAIXA_P_COMER[1] and g["G-SEP"]["passa"] and g["G-SSE"]["passa"] and g["G-F7"]["passa"])

    chave = lambda v: (-v["resumo"]["sep_i"]["ic_inferior"], v["ponto"]["w_fruta"], v["ponto"]["k_saciedade"],  # noqa: E731
                       v["ponto"]["duracao_min"])
    cand = [v for v in varredura if ok(v)]
    v = min(cand if cand else varredura, key=chave)
    return {"ponto": v["ponto"], "fechou": bool(cand), "candidatos": [nome_ponto(c["ponto"]) for c in cand], "regra": "plano, secao 4",
            "faixa_p_comer": FAIXA_P_COMER}


# ------------------------------------------------------------------ principal


def meta(cfg: dict, t0: float, cf: ConfigFrutas) -> dict:
    arquivos = ["digilab/frutas.py", "digilab/ambiente.py", "digilab/policy.py", "digilab/config.py", "digilab/metrics.py",
                "digilab/events.py", "digilab/engine.py", "experiments/run_v2_n4.py"]
    if sha256_engine() != ENGINE_SHA256_V0:
        raise RuntimeError("engine.py mudou")
    return {"config": cfg, "sha256": {a: _sha(RAIZ / a) for a in arquivos}, "python": sys.version, "plataforma": platform.platform(),
            "segundos": round(time.perf_counter() - t0, 1), "config_frutas": asdict(cf), "dias": DIAS, "orcamento": ORCAMENTO,
            "bootstrap": BOOT}


def ponto(p: dict, sementes, pasta: Path | None, sem: dict) -> dict:
    cf = cfg_frutas(p)
    frutas, logs = vidas_braco("frutas", cf, sementes, pasta)
    acop = acoplados(cf, logs, sementes, pasta, False)
    r = resumo(frutas, sem, acop, sementes)
    return {"ponto": p, "resumo": r, "gates": gates(r), "_frutas": frutas, "_logs": logs, "_acop": acop}


def principal(cfg: dict) -> int:
    t0 = time.perf_counter()
    sementes = tuple(cfg["sementes"])
    esperadas = SEMENTES_CALIBRACAO if cfg["conjunto"] == "calibracao" else SEMENTES_VALIDACAO
    if sementes != esperadas:
        raise ValueError(f"conjunto {cfg['conjunto']} com sementes {sementes}; o plano diz {esperadas}")
    saida = RAIZ / cfg["saida"]
    if cfg["conjunto"] == "validacao" and (saida / "resultado.json").exists():
        raise RuntimeError("a validacao roda uma vez: resultado.json ja existe")
    sem, _ = vidas_braco("semfrutas", CONFIG_FRUTAS_LIGADA, sementes, saida / "semfrutas")
    if cfg["conjunto"] == "calibracao":
        varredura = []
        for w in cfg["grade"]["w_fruta"]:
            for k in cfg["grade"]["k_saciedade"]:
                for d in cfg["grade"]["duracao_min"]:
                    p = {"w_fruta": w, "k_saciedade": k, "duracao_min": d}
                    v = ponto(p, sementes, saida / "grade" / nome_ponto(p), sem)
                    r, g = v["resumo"], v["gates"]
                    varredura.append({"ponto": p, "resumo": r, "gates": g})
                    print(f"{nome_ponto(p)}: p_comer {r['p_comer']['media']:.3f} sep_i {r['sep_i']['media']:+.3f} [{r['sep_i']['ic_inferior']:+.3f}] "
                          f"sep_ii {r['sep_ii']['media']:+.3f} [{r['sep_ii']['ic_inferior']:+.3f}] b_rec {r['sse']['beta_recente']['media']:+.3f} "
                          f"b_fome {r['sse']['beta_fome']['media']:+.3f} f7 {r['f7_saude_frutas_menos_acoplado']['media']:+.4f} "
                          f"SEP {g['G-SEP']['passa']} SSE {g['G-SSE']['passa']} F7 {g['G-F7']['passa']}", flush=True)
        _gravar(saida / "varredura.jsonl", "".join(json.dumps(v, sort_keys=True, ensure_ascii=False) + "\n" for v in varredura))
        escolha = escolher(varredura)
        p = escolha["ponto"]
    else:
        escolha = {"ponto": cfg["ponto"], "fechou": None, "regra": "validacao: o ponto do config, commitado antes"}
        p = cfg["ponto"]
    pasta = saida / "ponto"
    v = ponto(p, sementes, pasta, sem)
    iguais, _ = vidas_braco("iguais", cfg_frutas(p, "iguais"), sementes, pasta / "iguais")
    acop_sc = acoplados(cfg_frutas(p), v["_logs"], sementes, pasta, True)
    r, g = v["resumo"], v["gates"]
    s = list(sementes)
    custo = [media(v["_frutas"][f"{d}-frutas@{x}"]["privacao"]["humor_medio"] - iguais[f"{d}-iguais@{x}"]["privacao"]["humor_medio"]
                   for d in DONOS) for x in s]
    sep_iguais = _por_semente(iguais, "iguais", s, lambda m: m["sep_i"]["delta"])
    sc = [media(v["_frutas"][f"{d}-frutas@{x}"]["saude_final"] - acop_sc[f"{d}-acoplado-semcarinho@{x}"]["saude_final"] for d in DONOS)
          for x in s]
    neo = [(m["genoma"]["neofobia"], min((t for t in m["primeiro_contato"].values() if t is not None), default=None))
           for m in v["_frutas"].values()]
    resultado = {"conjunto": cfg["conjunto"], "sementes": s, "escolha": escolha, "ponto": p, "resumo": r, "gates": g,
                 "descasado_menos_iguais_humor": {"por_semente": custo, **ic(custo)},
                 "sep_i_iguais": {"por_semente": sep_iguais, **ic(sep_iguais)},
                 "f7_semcarinho_saude": {"por_semente": sc, **ic(sc)},
                 "neofobia_x_primeiro_contato": neo,
                 "acoplado_interacoes": {n: m["interacoes"] for n, m in v["_acop"].items()}}
    _gravar(saida / "vidas.json", _dump({"frutas": v["_frutas"], "iguais": iguais, "semfrutas": sem}))
    _gravar(saida / "so_cuidado.json", _dump({"acoplado": v["_acop"], "acoplado-semcarinho": acop_sc}))
    _gravar(saida / "resultado.json", _dump(resultado))
    _gravar(saida / "meta.json", _dump(meta(cfg, t0, cfg_frutas(p))))
    print(f"ponto {nome_ponto(p)} (fechou: {escolha['fechou']}); G-SEP {g['G-SEP']} G-SSE {g['G-SSE']['passa']} G-F7 {g['G-F7']['passa']}; "
          f"{time.perf_counter() - t0:.0f} s")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--config", required=True)
    a = ap.parse_args()
    return principal(json.loads((RAIZ / a.config).read_text(encoding="utf-8")))


if __name__ == "__main__":
    raise SystemExit(main())
