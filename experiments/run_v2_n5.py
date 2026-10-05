"""V2, N5: o dono informa, o mundo valida ou refuta (docs/PLANO_ANALISE_V2_N5.md, com o adendo 1; decisoes N5-1 a N5-8, R1, R2).

Calibracao (bases 12101...12505): a grade do `w0_info` pela bancada (P0, P1, P2, P2e, P2a e o "so cuidado" acoplado do P2 e do P2e;
descasado; atencioso; 14 dias; ponto T3), a escolha do `w0_info` (secao 8), o delta, o delta_EF e o N da validacao (adendo 1, A1.8).
Validacao (bases 13101...13505), uma vez, no `w0_info`, delta e K do adendo 2: os gates G-EF, G-PIORA, G-REC (Holm) e G5, as leituras e
os descritivos (secao 6). O G1 e conferido pela bancada em toda vida (replay do disco bit a bit).

    python experiments/run_v2_n5.py --config experiments/configs/v2_n5/calibracao.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import random
import statistics
import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import bancada_v2 as bv  # noqa: E402
from digilab.config import TICKS_POR_DIA  # noqa: E402
from digilab.events import LogDeEventos  # noqa: E402
from digilab.metrics import contraste_pareado, holm, t_unilateral, tamanho_amostra  # noqa: E402
from digilab.motivo import PoliticaComMotivo, indices_eventos_dono  # noqa: E402
from digilab.protocol import ENGINE_SHA256_V0, PROTOCOLO_ARENA_V1, sha256_engine  # noqa: E402
from digilab.treino import reproduzir_com_feedback  # noqa: E402

PLANO = "docs/PLANO_ANALISE_V2_N5.md"
BASES = {"calibracao": (12101, 12202, 12303, 12404, 12505), "validacao": (13101, 13202, 13303, 13404, 13505),
         "fumaca": tuple(sorted(bv.SEMENTES_TESTE))}
BRACOS = ("P0", "P1", "P2", "P2e", "P2a")
ACOPLADOS = [{"origem": "P2", "destino": "P2", "filtro": "sem_ensino"}, {"origem": "P2e", "destino": "P2e", "filtro": "sem_ensino"}]
MUNDO, DONO, ROTULO, PONTO = "descasado", "atencioso", "n5", "T3"
COM_INFO = ("P2", "P2e", "P2a")
APRENDEM = ("P1", "P2", "P2e", "P2a")
BOOT = {"reamostragens": PROTOCOLO_ARENA_V1.bootstrap_reamostragens.valor, "semente": PROTOCOLO_ARENA_V1.bootstrap_semente.valor,
        "nivel": PROTOCOLO_ARENA_V1.nivel_confianca.valor}
ALFA, PODER, N_MAXIMO, REPETICOES_PODER = 0.05, 0.8, 200, 2000
CHAVES = {"descricao", "conjunto", "bases", "k", "saida", "dias", "orcamento", "sonda", "grade_w0", "w0_info", "delta", "delta_ef"}
# a familia de Holm (N5-6): nome -> (medida, braco que deve ficar acima, braco de baixo); orientados para a predicao
FAMILIA = {"G_EF": ("ate_metade", "P1", "P2"), "G_PIORA": ("taxa_inicio", "P2e", "P1"), "G_REC": ("taxa_final", "P0", "P2e")}


def _dump(obj) -> str:
    return json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False, default=repr) + "\n"


def _gravar(caminho: Path, texto: str) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(texto, encoding="utf-8", newline="\n")


def _sha(caminho: Path) -> str:
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


def carregar(caminho: Path) -> dict:
    cfg = json.loads(caminho.read_text(encoding="utf-8"))
    return validar(cfg)


def validar(cfg: dict) -> dict:
    sobram = set(cfg) - CHAVES
    if sobram:
        raise KeyError(f"chaves desconhecidas: {sorted(sobram)}")
    if sha256_engine() != ENGINE_SHA256_V0:
        raise RuntimeError("engine.py mudou")
    conjunto = cfg["conjunto"]
    if conjunto not in BASES:
        raise ValueError(f"conjunto desconhecido {conjunto!r}: {sorted(BASES)}")
    if conjunto == "fumaca" and not set(cfg["bases"]) <= set(BASES["fumaca"]):
        raise ValueError(f"fumaca: so as sementes dos testes {BASES['fumaca']}")
    if conjunto != "fumaca" and tuple(cfg["bases"]) != BASES[conjunto]:
        raise ValueError(f"{conjunto}: bases {BASES[conjunto]} (o plano, secoes 8 e 9)")
    if conjunto == "calibracao" and ("grade_w0" not in cfg or {"w0_info", "delta", "delta_ef"} & set(cfg)):
        raise ValueError("calibracao: so a grade_w0 (o w0_info, o delta e o delta_EF saem dela)")
    if conjunto == "validacao" and not {"w0_info", "delta", "delta_ef"} <= set(cfg):
        raise ValueError("validacao: w0_info, delta e delta_ef do adendo 2")
    cfg.setdefault("dias", 14)
    cfg.setdefault("orcamento", 224)
    cfg.setdefault("sonda", {"estados": 64, "amostras": 200, "semente": 9001})
    if conjunto != "fumaca" and cfg["dias"] != 14:
        raise ValueError("vida de 14 dias (E5)")
    return cfg


def cfg_bancada(cfg: dict, w0: int) -> dict:
    return {"descricao": f"N5 {cfg['conjunto']}, w0_info {w0}", "plano": PLANO, "bracos": list(BRACOS), "donos": [DONO],
            "unidades": {"bases": list(cfg["bases"]), "k": int(cfg["k"]), "rotulo": ROTULO}, "mundos": [MUNDO],
            "dias": cfg["dias"], "orcamento": cfg["orcamento"], "sonda": cfg["sonda"], "bootstrap": BOOT,
            "acoplados": ACOPLADOS, "ponto": PONTO, "lobos": {"w0_info": int(w0)}}


# ------------------------------------------------------------------ o replay de leitura: motivo (G4) e w_info por dia


class _Espiao:
    """Por fora do PoliticaComMotivo: anota (tick, w_info do cerebro) antes de cada decisao. So le; repassa tudo, os ganchos das frutas
    inclusive (pelo __getattr__)."""

    def __init__(self, interna: PoliticaComMotivo, braco: bv.PoliticaDoBraco) -> None:
        self.interna = interna
        self.braco = braco
        self.nome = interna.nome
        self._tick_ultimo_cuidado = 0
        self.w_info: list[tuple[int, int | None]] = []

    def agir(self, obs, rng):
        self.w_info.append((obs.ticks_desde_cuidado + self._tick_ultimo_cuidado, self.braco.cerebro._peso_info))
        return self.interna.agir(obs, rng)

    def observar(self, transicao) -> None:
        self.interna.observar(transicao)

    def receber_acao_dono(self, acao, tick) -> None:
        self._tick_ultimo_cuidado = tick
        self.interna.receber_acao_dono(acao, tick)

    def estado_interno(self) -> dict:
        return self.interna.estado_interno()

    def __getattr__(self, nome):
        interna = self.__dict__.get("interna")
        if interna is None:
            raise AttributeError(nome)
        return getattr(interna, nome)


def _nucleo(motor) -> tuple:
    r = motor.resumo_frutas()
    return (motor.log.para_jsonl(), motor.estado(), motor.acoes_recentes(10**9), motor._rng_politica.getstate(),
            motor._rng_ambiente.getstate(), r["consumos"], r["incentivo"], r["rng_fruta"])


def leitura(bancada: bv.Bancada, vida: bv.VidaBancada, dias: int) -> dict:
    """A vida rejogada no motor dela com o motivo e o espiao; confere que a vida e a mesma. Devolve o G4 e o w_info no fim de cada dia."""
    log = LogDeEventos.de_jsonl(vida.motor.log.para_jsonl())
    indices = indices_eventos_dono(log)
    esp: list[_Espiao] = []

    def fab(cfg=None):
        braco = bancada.politica(vida.espec, cfg)
        e = _Espiao(PoliticaComMotivo(braco, indices), braco)
        esp.append(e)
        return e

    m = reproduzir_com_feedback(log, fab, semente=vida.espec.semente, fabrica_motor=bancada.fabrica_motor(vida.espec))
    if _nucleo(m) != _nucleo(vida.motor):
        raise bv.ReplayDivergiu(f"{vida.nome}: a leitura mudou a vida")
    e = esp[0]
    n = len(e.interna.motivos)
    final = bv.do_braco(vida.motor.politica).cerebro._peso_info
    por_dia = []
    for d in range(1, dias + 1):
        depois = [w for t, w in e.w_info if t >= d * TICKS_POR_DIA]
        por_dia.append(depois[0] if depois else final)
    return {"g4_decidiu": sum(x["lobo"] == "decisao" for x in e.interna.diagnosticos) / n,
            "g4_com_fator": sum(x["lobo"] == "decisao" and bool(mo.fatores) for mo, x in zip(e.interna.motivos, e.interna.diagnosticos)) / n,
            "w_info_por_dia": por_dia}


def medidas_da_vida(bancada: bv.Bancada, vida: bv.VidaBancada, m: dict, dias: int) -> dict:
    fr = m["frutas"]
    ate = fr["consumos_ate_metade"]
    rec = {"braco": m["braco"], "semente": vida.espec.semente, "genoma": vida.espec.genoma, "base": m["unidade"]["base"],
           "taxa_inicio": fr["taxa_fruta_ruim"]["inicio"]["taxa"], "taxa_final": fr["taxa_fruta_ruim"]["final"]["taxa"],
           "taxa_total": fr["taxa_fruta_ruim"]["total"]["taxa"], "consumos": fr["consumos"],
           "ate_metade": None if ate["sem_referencia"] else ate["consumos"], "censurado": ate["censurado"],
           "saude": m["saude_media"], "fora_privacao": m["fracao_fora_de_privacao"], "humor": m["humor_medio"],
           "informacoes": len(fr["informacoes"]), "decisoes_com_informacao": fr["decisoes_com_informacao"],
           "morte": vida.motor.morte, "deriva_por_dia": m["custo_da_plasticidade"]["deriva_por_dia"]}
    cerebro = bv.do_braco(vida.motor.politica).cerebro
    if vida.espec.braco in APRENDEM and vida.origem is None:
        rec["pesos_no_teto"] = cerebro.pesos_no_teto()
        rec["w_info_final"] = cerebro._peso_info
        rec["w0_info"] = cerebro._prior_info
        rec.update(leitura(bancada, vida, dias))
    return rec


def rodar_ponto(cfg: dict, w0: int, pasta: Path) -> dict:
    t = time.perf_counter()
    cb = cfg_bancada(cfg, w0)
    r = bv.rodar(cb, pasta)
    bancada = bv.bancada_da_config(cb)
    vidas = {nome: medidas_da_vida(bancada, v, r["medidas"][nome], cfg["dias"]) for nome, v in sorted(r["vidas"].items())}
    # G2 na run: com w0_info 0 a entrada `info` fica desligada e o P2 vive como o P1 (o log so difere pelas informacoes)
    g2 = None
    if w0 == 0:
        p1 = {(v.espec.semente, v.espec.genoma): v for v in r["vidas"].values() if v.espec.braco == "P1" and v.origem is None}
        g2 = all(_nucleo(v.motor)[1:] == _nucleo(p1[(v.espec.semente, v.espec.genoma)].motor)[1:]
                 for v in r["vidas"].values() if v.espec.braco == "P2" and v.origem is None)
    res = {"w0_info": w0, "vidas": vidas, "g2_w0_zero_p2_igual_p1": g2, "segundos": time.perf_counter() - t}
    _gravar(pasta / "resultado_vidas.json", _dump(res))
    return res


# ------------------------------------------------------------------ contrastes (secao 7, adendo A1.6)


def indice(res: dict) -> dict:
    idx: dict = {}
    for rec in res["vidas"].values():
        idx.setdefault(rec["braco"], {})[(rec["semente"], rec["genoma"])] = rec
    return idx


def diferencas(idx: dict, medida: str, mais: str, menos: str) -> dict:
    """{base: [medida(mais) - medida(menos)]}, pareado na unidade; unidade sem valor num dos dois fica fora."""
    g: dict = {}
    for u, a in idx[mais].items():
        b = idx[menos][u]
        if a[medida] is not None and b[medida] is not None:
            g.setdefault(a["base"], []).append(a[medida] - b[medida])
    return g


def contraste(idx: dict, medida: str, mais: str, menos: str) -> dict:
    g = diferencas(idx, medida, mais, menos)
    c = contraste_pareado(g, BOOT["reamostragens"], BOOT["semente"])
    c["definicao"] = f"{medida}: {mais} - {menos}, pareado na unidade, bases juntas no bootstrap"
    return c


def _ic_acima(c: dict) -> bool:
    return c["ic95"] is not None and c["ic95"]["ic_inferior"] > 0.0


def _ic_abaixo(c: dict) -> bool:
    return c["ic95"] is not None and c["ic95"]["ic_superior"] < 0.0


def _contem_zero(c: dict) -> bool:
    return c["ic95"] is not None and c["ic95"]["ic_inferior"] <= 0.0 <= c["ic95"]["ic_superior"]


def _equivalente(c: dict, delta: float | None) -> bool:
    return delta is not None and c["ic90"] is not None and -delta < c["ic90"]["ic_inferior"] and c["ic90"]["ic_superior"] < delta


def descritivos(idx: dict, res: dict) -> dict:
    so = {b: f"{b}<{b}:sem_ensino" for b in ("P2", "P2e")}
    d = {
        "P2a_menos_P2_ate_metade": contraste(idx, "ate_metade", "P2a", "P2"),
        "P2a_menos_P2_taxa_final": contraste(idx, "taxa_final", "P2a", "P2"),
        "P0_menos_P2_taxa_final": contraste(idx, "taxa_final", "P0", "P2"),
        "P0_menos_P1_taxa_final": contraste(idx, "taxa_final", "P0", "P1"),
        "so_cuidado": {b: {m: contraste(idx, m, b, so[b]) for m in ("saude", "fora_privacao", "taxa_final")} for b in so if so[b] in idx},
    }
    media = lambda xs: (sum(xs) / len(xs)) if xs else None  # noqa: E731
    por_braco = {}
    for b, us in idx.items():
        recs = list(us.values())
        r = {m: media([x[m] for x in recs if x[m] is not None]) for m in
             ("taxa_inicio", "taxa_final", "taxa_total", "consumos", "ate_metade", "saude", "fora_privacao", "humor",
              "decisoes_com_informacao", "informacoes")}
        r["unidades"] = len(recs)
        r["sem_valor"] = {m: sum(x[m] is None for x in recs) for m in ("taxa_inicio", "taxa_final", "ate_metade")}
        r["censurados"] = sum(bool(x["censurado"]) for x in recs if x["ate_metade"] is not None)
        r["mortes"] = sum(x["morte"] is not None for x in recs)
        if recs and "g4_decidiu" in recs[0]:
            r["g4_decidiu"] = media([x["g4_decidiu"] for x in recs])
            r["g4_com_fator"] = media([x["g4_com_fator"] for x in recs])
            r["vidas_com_peso_no_teto"] = sum(x["pesos_no_teto"] > 0 for x in recs)
            dpd = [x["deriva_por_dia"] for x in recs]
            meio = len(dpd[0]) // 2 - 1
            d7, d14 = media([x[meio] for x in dpd]), media([x[-1] for x in dpd])
            r["razao_deriva_14_7"] = d14 / d7 if d7 else None
            ws = [x["w_info_por_dia"] for x in recs if x["w0_info"]]
            if ws:
                r["w_info_por_dia_media"] = [media(col) for col in zip(*ws)]
        por_braco[b] = r
    d["por_braco"] = por_braco
    # o dia em que o w_info do P2e cruza o zero (adendo A1.5)
    p2e = [x for x in idx.get("P2e", {}).values() if x.get("w0_info")]
    dias_cruza = [next((i + 1 for i, w in enumerate(x["w_info_por_dia"]) if w < 0), None) for x in p2e]
    d["P2e_cruza_zero"] = {"fracao": (sum(c is not None for c in dias_cruza) / len(dias_cruza)) if dias_cruza else None,
                           "dias": dias_cruza}
    return d


def avaliar(res: dict, delta: float | None, delta_ef: float | None, teto: int) -> dict:
    idx = indice(res)
    fam = {n: contraste(idx, med, mais, menos) for n, (med, mais, menos) in FAMILIA.items()}
    h = holm({n: c["p_unilateral"] for n, c in fam.items()}, ALFA)
    passa = {n: bool(h[n]["rejeita"]) for n in fam}
    # leituras (secao 6, N5-7)
    cens = {b: descritivos_censura(idx, b) for b in ("P1", "P2")}
    ef_exposicao = any(v["fracao"] is not None and v["fracao"] > 0.5 for v in cens.values())
    p2e = [x for x in idx["P2e"].values() if x.get("w0_info")]
    preso = [any(w <= x["w0_info"] - teto for w in x["w_info_por_dia"]) for x in p2e]
    rec_refuta = _ic_abaixo(fam["G_REC"]) or _equivalente(fam["G_REC"], delta)
    if not passa["G_PIORA"]:
        leitura_piora_rec = "G-PIORA falha: a informacao nao teve efeito inicial; G-REC nao informa sobre correcao"
    elif passa["G_REC"]:
        leitura_piora_rec = "G-PIORA e G-REC passam: o pet seguiu o dono errado e o mundo o corrigiu"
    elif rec_refuta:
        leitura_piora_rec = ("G-PIORA passa e G-REC refuta: o pet obedece ao dono contra o mundo"
                             + ("; limitado pelo teto" if any(preso) else ""))
    else:
        leitura_piora_rec = "G-PIORA passa; G-REC inconclusivo"
    g5 = {f"{b}_menos_P1": {m: contraste(idx, m, b, "P1") for m in ("saude", "fora_privacao")} for b in ("P2", "P2e")}
    mortes = {b: sum(x["morte"] is not None for x in idx[b].values()) for b in ("P1", "P2", "P2e")}
    g5_passa = all(_contem_zero(c) for d in g5.values() for c in d.values()) and len(set(mortes.values())) == 1
    return {"familia": fam, "holm": h, "passa": passa,
            "leituras": {"G_EF": "inconclusivo por exposicao" if ef_exposicao and not passa["G_EF"] else
                         ("passa" if passa["G_EF"] else "falha"),
                         "G_EF_censura": cens, "G_PIORA_G_REC": leitura_piora_rec,
                         "G_REC_refuta": rec_refuta, "P2e_w_info_no_limite": {"vidas": sum(preso), "de": len(preso)}},
            "G5": {"contrastes": g5, "mortes": mortes, "passa": g5_passa},
            "delta": delta, "delta_ef": delta_ef, "descritivos": descritivos(idx, res)}


def descritivos_censura(idx: dict, b: str) -> dict:
    xs = [x for x in idx[b].values() if x["ate_metade"] is not None]
    return {"censurados": sum(bool(x["censurado"]) for x in xs), "de": len(xs),
            "fracao": (sum(bool(x["censurado"]) for x in xs) / len(xs)) if xs else None}


# ------------------------------------------------------------------ calibracao: escolha, delta e N (secao 8, adendo A1.8)


def escolher(avaliacoes: dict) -> dict:
    grade = sorted(w for w in avaliacoes if w > 0)
    ok = [w for w in grade if _ic_acima(avaliacoes[w]["familia"]["G_PIORA"])]
    if ok:
        return {"w0_info": ok[0], "fechou": True, "regra": "o menor w0_info com o IC 95% de P2e - P1 na taxa inicial acima de 0"}
    inf = lambda w: avaliacoes[w]["familia"]["G_PIORA"]["ic95"]["ic_inferior"] if avaliacoes[w]["familia"]["G_PIORA"]["ic95"] \
        else float("-inf")  # noqa: E731
    return {"w0_info": max(grade, key=inf), "fechou": False,
            "regra": "nenhum passou: o de maior limite inferior do IC 95% de P2e - P1 na taxa inicial (a calibracao nao fechou)"}


def poder_simulado(diffs: list[float], efeito: float, n: int, alfa: float, repeticoes: int, semente: int) -> float:
    """Reamostra n diferencas da calibracao deslocadas para a media `efeito` e conta quantas passam o t pareado unilateral em alfa."""
    if len(diffs) < 2 or n < 2:
        return 0.0
    m = sum(diffs) / len(diffs)
    base = [d - m + efeito for d in diffs]
    rng = random.Random(semente)
    passa = 0
    for _ in range(repeticoes):
        a = [base[rng.randrange(len(base))] for _ in range(n)]
        media = sum(a) / n
        var = sum((x - media) ** 2 for x in a) / (n - 1)
        if var > 0.0 and t_unilateral(media / (var / n) ** 0.5, n - 1) < alfa:
            passa += 1
    return passa / repeticoes


def tamanho_da_validacao(res: dict, delta: float, delta_ef: float) -> dict:
    idx = indice(res)
    out = {}
    for nome, (med, mais, menos) in FAMILIA.items():
        d = [x for v in diferencas(idx, med, mais, menos).values() for x in v]
        sigma = statistics.stdev(d) if len(d) > 1 else 0.0
        efeito = delta_ef if nome == "G_EF" else delta
        n = tamanho_amostra(sigma, efeito, ALFA / 3, PODER, 5) if efeito > 0 else None
        out[nome] = {"sigma_d": sigma, "efeito": efeito, "N": n, "diferencas": len(d)}
    ns = [v["N"] for v in out.values() if v["N"] is not None]
    n_val = min(max(ns), N_MAXIMO) if ns else N_MAXIMO
    n_val = max(10, 5 * -(-n_val // 5))
    for nome, (med, mais, menos) in FAMILIA.items():
        d = [x for v in diferencas(idx, med, mais, menos).values() for x in v]
        out[nome]["poder_simulado_no_N"] = poder_simulado(d, out[nome]["efeito"], n_val, ALFA / 3, REPETICOES_PODER, BOOT["semente"])
    return {"por_contraste": out, "N_validacao": n_val, "K_por_base": n_val // 5, "teto": N_MAXIMO, "alfa": ALFA / 3, "poder": PODER}


# ------------------------------------------------------------------ principal


def _commit() -> str | None:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=RAIZ, capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def executar(cfg: dict, saida: Path, origem: dict) -> dict:
    if cfg["conjunto"] == "validacao" and saida.exists():
        raise RuntimeError(f"{saida} ja existe: a validacao roda uma vez so")
    saida.mkdir(parents=True, exist_ok=True)
    _gravar(saida / "meta.json", _dump({
        **origem, "cfg": cfg, "commit": _commit(), "plano_sha256": _sha(RAIZ / PLANO), "python": platform.python_version(),
        "plataforma": platform.platform(), "engine_sha256": sha256_engine(),
        "sha256": {f: _sha(RAIZ / f) for f in ("digilab/policies/lobos.py", "digilab/frutas.py", "experiments/bancada_v2.py",
                                                 "digilab/metrics.py", "digilab/motivo.py", "experiments/run_v2_n5.py")}}))
    teto = bv.cfg_lobos_do_ponto(PONTO).teto
    t0 = time.perf_counter()
    grade = cfg["grade_w0"] if "grade_w0" in cfg else [cfg["w0_info"]]
    resultados, avaliacoes = {}, {}
    with (saida / "varredura.jsonl").open("w", encoding="utf-8", newline="\n") as f:
        for w0 in grade:
            res = rodar_ponto(cfg, int(w0), saida / f"w0_{w0}")
            resultados[w0] = res
            av = avaliar(res, cfg.get("delta"), cfg.get("delta_ef"), teto)
            avaliacoes[w0] = av
            _gravar(saida / f"w0_{w0}" / "resultado.json", _dump({**av, "g2_w0_zero_p2_igual_p1": res["g2_w0_zero_p2_igual_p1"]}))
            linha = {"w0_info": w0, "segundos": res["segundos"],
                     **{f"{n}_media": c["media"] for n, c in av["familia"].items()},
                     **{f"{n}_ic95_inf": (c["ic95"] or {}).get("ic_inferior") for n, c in av["familia"].items()},
                     **{f"{n}_passa": v for n, v in av["passa"].items()}}
            f.write(json.dumps(linha, sort_keys=True, default=repr) + "\n")
            f.flush()
            print(f"[w0 {w0}] {res['segundos']:.0f} s; " + "; ".join(
                f"{n} {c['media']:+.4f}" if c["media"] is not None else f"{n} -" for n, c in av["familia"].items()), flush=True)
    out = {"conjunto": cfg["conjunto"], "segundos_total": time.perf_counter() - t0}
    if cfg["conjunto"] in ("calibracao", "fumaca") and len(grade) > 1:
        esc = escolher(avaliacoes)
        res = resultados[esc["w0_info"]]
        idx = indice(res)
        taxas_p0 = [x["taxa_final"] for x in idx["P0"].values() if x["taxa_final"] is not None]
        ate_p1 = [x["ate_metade"] for x in idx["P1"].values() if x["ate_metade"] is not None]
        delta = (sum(taxas_p0) / len(taxas_p0)) / 2 if taxas_p0 else None
        delta_ef = (sum(ate_p1) / len(ate_p1)) / 2 if ate_p1 else None
        out.update({"escolha": esc, "delta": delta, "delta_ef": delta_ef,
                    "validacao": tamanho_da_validacao(res, delta, delta_ef) if delta and delta_ef else None,
                    "g2_w0_zero_p2_igual_p1": resultados[0]["g2_w0_zero_p2_igual_p1"] if 0 in resultados else None})
        print(f"[escolha] w0_info {esc['w0_info']} (fechou: {esc['fechou']}); delta {delta}; delta_EF {delta_ef}; "
              f"N {out['validacao']['N_validacao'] if out['validacao'] else None}", flush=True)
    else:
        av = avaliacoes[grade[0]]
        out.update({"w0_info": grade[0], "passa": av["passa"], "leituras": av["leituras"], "G5": av["G5"]["passa"]})
        print(f"[{cfg['conjunto']}] w0_info {grade[0]}: " + ", ".join(f"{n} {'PASSA' if v else 'FALHA'}" for n, v in av["passa"].items())
              + f"; G5 {'PASSA' if av['G5']['passa'] else 'FALHA'}; {av['leituras']['G_PIORA_G_REC']}", flush=True)
    _gravar(saida / ("escolha.json" if "escolha" in out else "resumo.json"), _dump(out))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    a = ap.parse_args(argv)
    caminho = Path(a.config)
    cfg = carregar(caminho)
    executar(cfg, RAIZ / cfg["saida"], {"config": str(caminho), "config_sha256": _sha(caminho)})
    return 0


if __name__ == "__main__":
    sys.exit(main())
