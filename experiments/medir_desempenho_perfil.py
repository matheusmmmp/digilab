"""Medicao de desempenho das runs de pesquisa (docs/DESEMPENHO_PERFIL_2026-11.md): onde vai o tempo de uma vida tipica do cerebro modular
(a vida da C4, `run_v2_memoria_autobio._vida`), do replay dela e da analise. So mede: nao muda o motor, o cerebro nem as regras, e usa so as
sementes dos testes (101...505), nunca uma faixa reservada. Roda no CPython e no PyPy (o modo `tempo` nao usa o cProfile).

Os modos:
    perfil  -- o cProfile de uma vida (viver, gravar o log, replay G1, conferencias e medidas), por fase, com o tempo de cada categoria
    tempo   -- o tempo de parede por vida, sem profiler, e o sha256 do log e das medidas (para comparar interpretadores)
    analise -- o tempo de ler o medidas.json de uma run gravada (json, gzip) e o cProfile do `analisar` da C4 em cima dele
    logs    -- o peso do json e do gzip no log de uma vida e nas medidas, e (se instalados) do orjson e do msgspec
    comparar -- le dois arquivos do modo `tempo` (com --medidas) e diz, por semente, o que sai igual e quais medidas mudam
    gabaritos -- regera gabaritos de tests/ neste interpretador e conta as vidas que divergem do gravado, por chave

    python experiments/medir_desempenho_perfil.py perfil --semente 101 --saida artifacts_v3_desempenho/perfil_vida_101
"""
from __future__ import annotations

import argparse
import cProfile
import gzip
import hashlib
import io
import json
import math
import platform
import pstats
import sys
import tempfile
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v2_memoria_autobio as ma  # noqa: E402

orq = ma.orq
SEMENTES_TESTE = (101, 202, 303, 404, 505)
BRACO, LUGAR = "REL", ma.PRIMARIO                     # o braco e o lugar do primario da C4


def interpretador() -> dict:
    # a sonda do sum(): o CPython 3.12+ soma floats com compensacao (Neumaier) e da 2.0; uma soma ingenua (CPython ate 3.11, PyPy) da 0.0
    xs = [0.1] * 10 + [1e16, 1.0, -1e16]
    return {"implementacao": platform.python_implementation(), "versao": platform.python_version(), "executavel": sys.executable,
            "maquina": platform.machine(), "sistema": platform.platform(),
            "sonda_soma": {"sum": repr(sum(xs)), "math_fsum": repr(math.fsum(xs)), "sum_10x0_1": repr(sum([0.1] * 10))}}


def _exigir_semente(s: int) -> None:
    if s not in SEMENTES_TESTE:
        raise ValueError(f"semente {s}: so as dos testes {SEMENTES_TESTE} (nunca uma faixa reservada)")


# ================================================================== as categorias
CATEGORIAS = ("motor_mundo", "corpo", "cerebro", "log_eventos", "json_gzip", "metricas", "orquestrador", "fala", "outros")
_MOTOR = {"engine.py", "state.py", "mundo.py", "ambiente.py", "frutas.py", "treino.py", "instinto_banheiro.py", "instinto_mundo.py",
          "grupo.py", "config.py", "contrato.py", "protocol.py", "evolucao.py", "obediencia.py", "donos.py", "personas.py"}
_CORPO = {"corpo.py", "corpo_grafo.py", "motor_corpo.py"}


_RAIZ_TXT = str(RAIZ).replace("\\", "/").rstrip("/") + "/"


def _arquivo(func: tuple) -> str:
    """o arquivo da funcao, relativo a raiz do repositorio quando estiver nela ("/digilab/...", "/experiments/...")"""
    a = func[0].replace("\\", "/")
    return "/" + a[len(_RAIZ_TXT):] if a.lower().startswith(_RAIZ_TXT.lower()) else a


def categoria_direta(func: tuple) -> str | None:
    """a categoria de uma funcao pelo arquivo; None para a biblioteca padrao e os builtins (herdam a do chamador)"""
    arq, _, nome = func
    a = _arquivo(func)
    base = a.rsplit("/", 1)[-1]
    if base in ("gzip.py",) or "/json/" in a or "_json" in nome or "zlib" in nome or "gzip" in a:
        return "json_gzip"
    if "/digilab_fala_livre/" in a:
        return "fala"
    if "/digilab/" in a:
        if base == "metrics.py":
            return "metricas"
        if base == "events.py":
            return "log_eventos"
        if base in _CORPO:
            return "corpo"
        if base in _MOTOR:
            return "motor_mundo"
        return "cerebro"                              # digibrain/, policies/, memoria, desejo, motivo, emocao, vinculo...
    if "/experiments/" in a:
        if base == "regras_mundo.py":
            return "motor_mundo"
        return "orquestrador"
    if a.startswith("~") or "/Lib/" in a or "/lib/" in a or "lib_pypy" in a or a.startswith("<"):
        return None
    return "outros"


def por_categoria(st: pstats.Stats) -> tuple[dict, dict]:
    """o tempo proprio (tottime) de cada funcao, somado por categoria; o da biblioteca padrao e dos builtins vai para a categoria do
    chamador, na proporcao do tempo de cada aresta (recursivo, com guarda de ciclo). Devolve (categorias, os 15 arquivos mais caros)."""
    stats = st.stats  # type: ignore[attr-defined]
    memo: dict = {}

    def distribuicao(func, pilha=()) -> dict:
        c = categoria_direta(func)
        if c is not None:
            return {c: 1.0}
        if func in memo:
            return memo[func]
        if func in pilha:
            return {"outros": 1.0}
        callers = stats[func][4]
        total = sum(v[2] for v in callers.values()) or sum(v[1] for v in callers.values())
        if not callers or total == 0:
            return {"outros": 1.0}
        out: dict = {}
        for chamador, v in callers.items():
            peso = (v[2] if sum(x[2] for x in callers.values()) else v[1]) / total
            if chamador not in stats:
                out["outros"] = out.get("outros", 0.0) + peso
                continue
            for k, f in distribuicao(chamador, pilha + (func,)).items():
                out[k] = out.get(k, 0.0) + peso * f
        memo[func] = out
        return out

    cats = {c: 0.0 for c in CATEGORIAS}
    arquivos: dict = {}
    for func, (_, _, tt, _, _) in stats.items():
        for k, f in distribuicao(func).items():
            cats[k] += tt * f
        a = _arquivo(func)
        chave = a if not a.startswith("~") else f"builtin:{func[2]}"
        arquivos[chave] = arquivos.get(chave, 0.0) + tt
    total = sum(cats.values())
    top = sorted(arquivos.items(), key=lambda x: -x[1])[:15]
    return ({k: {"s": round(v, 3), "frac": round(v / total, 4) if total else 0.0} for k, v in cats.items()},
            {k: round(v, 3) for k, v in top})


def _perfilar(f, saida: Path, nome: str):
    pr = cProfile.Profile()
    t0 = time.perf_counter()
    pr.enable()
    r = f()
    pr.disable()
    parede = time.perf_counter() - t0
    pr.dump_stats(str(saida / f"{nome}.prof"))
    st = pstats.Stats(pr)
    cats, top = por_categoria(st)
    buf = io.StringIO()
    pstats.Stats(pr, stream=buf).sort_stats("tottime").print_stats(30)
    (saida / f"{nome}_top30.txt").write_text(buf.getvalue(), encoding="utf-8")
    return r, {"parede_com_profiler_s": round(parede, 3), "categorias": cats, "arquivos_top15": top}


# ================================================================== uma vida, por fases
def _fases(semente: int, pasta: Path, perfil: Path | None) -> dict:
    """a `_vida` da C4 aberta nas fases (mesmas chamadas, na mesma ordem), cada uma medida (e perfilada, com `perfil`)"""
    _exigir_semente(semente)
    dono, dias, orc = ma.DONOS[0], ma.DIAS, ma.ORCAMENTO_POR_DIA
    out: dict = {"semente": semente, "braco": BRACO, "dono": dono, "lugar": LUGAR, "dias": dias, "fases": {}}

    def medir(nome, f):
        if perfil is not None:
            r, info = _perfilar(f, perfil, nome)
            out["fases"][nome] = info
            return r
        t0 = time.perf_counter()
        r = f()
        out["fases"][nome] = {"parede_s": round(time.perf_counter() - t0, 4)}
        return r

    motor, registro, fab, categorias = medir("viver", lambda: ma.viver(BRACO, dono, LUGAR, semente, dias, orc))
    arquivo = pasta / f"{dono}_{LUGAR}_{semente}.jsonl"
    texto = medir("gravar_log", lambda: (arquivo.write_text(motor.log.para_jsonl(), encoding="utf-8", newline="\n"),
                                         arquivo.read_text(encoding="utf-8"))[1])
    medir("replay_g1", lambda: orq.conferir_replay(motor, fab, semente, texto))

    def conferir_e_medir():
        orq.conferir_cenario(motor, registro)
        orq.conferir_mecanismo(BRACO, registro, None)
        ma.conferir_memoria(BRACO, orq.cerebro_de(registro))
        fins = ma.conferir_fins(BRACO, registro)
        med = orq.medidas(motor, registro, BRACO, dias, True)
        return {**med, "corpo": ma.lr.medidas_do_corpo(motor, registro, dias), "fins_conferidos": fins,
                "memoria": ma.medidas_memoria(registro, dias, categorias)}

    med = medir("conferir_e_medir", conferir_e_medir)
    out["log_bytes"] = len(texto.encode("utf-8"))
    out["log_eventos"] = len(motor.log)
    out["log_sha256"] = hashlib.sha256(texto.encode("utf-8")).hexdigest()
    out["medidas_sha256"] = hashlib.sha256(json.dumps(med, sort_keys=True).encode("utf-8")).hexdigest()
    out["estado_interno_sha256"] = hashlib.sha256(json.dumps(motor.politica.estado_interno(), sort_keys=True).encode("utf-8")).hexdigest()
    out["resumo_motor_sha256"] = hashlib.sha256(repr(bv.resumo_motor(motor)).encode("utf-8")).hexdigest()
    out["_medidas"] = med
    return out


def modo_perfil(a) -> dict:
    saida = Path(a.saida)
    saida.mkdir(parents=True, exist_ok=False)
    with tempfile.TemporaryDirectory() as tmp:
        r = _fases(a.semente, Path(tmp), saida)
    r.pop("_medidas")
    tot = {c: sum(f["categorias"][c]["s"] for f in r["fases"].values()) for c in CATEGORIAS}
    soma = sum(tot.values())
    r["total_categorias"] = {c: {"s": round(v, 3), "frac": round(v / soma, 4)} for c, v in tot.items()}
    return r


def modo_tempo(a) -> dict:
    vidas = []
    with tempfile.TemporaryDirectory() as tmp:
        for rep in range(a.repeticoes):
            for s in a.sementes:
                t0 = time.perf_counter()
                v = _fases(s, Path(tmp), None)
                med = v.pop("_medidas")
                if a.medidas and rep == 0:
                    Path(a.medidas).mkdir(parents=True, exist_ok=True)
                    (Path(a.medidas) / f"medidas_{s}.json").write_text(json.dumps(med, sort_keys=True, indent=1), encoding="utf-8", newline="\n")
                v["parede_total_s"] = round(time.perf_counter() - t0, 4)
                v["repeticao"] = rep
                vidas.append(v)
    return {"vidas": vidas}


# ================================================================== a analise de uma run gravada
def modo_analise(a) -> dict:
    pasta = Path(a.run)
    out: dict = {"run": str(pasta)}
    bruto = (pasta / "medidas.json").read_bytes()
    t0 = time.perf_counter()
    lidos = json.loads(bruto.decode("utf-8"))
    out["json_loads_s"] = round(time.perf_counter() - t0, 3)
    out["medidas_bytes"] = len(bruto)
    gz = (pasta / "medidas.json.gz").read_bytes()
    t0 = time.perf_counter()
    gzip.decompress(gz)
    out["gzip_decompress_s"] = round(time.perf_counter() - t0, 3)
    out["vidas"] = len(lidos)
    saida = Path(a.saida)
    saida.mkdir(parents=True, exist_ok=False)
    registros = list(lidos.values())
    res, info = _perfilar(lambda: ma.analisar(registros), saida, "analisar")
    out["analisar"] = info
    t0 = time.perf_counter()
    texto = bv._dump(res)
    out["dump_resultado_s"] = round(time.perf_counter() - t0, 3)
    out["resultado_sha256"] = hashlib.sha256(texto.encode("utf-8")).hexdigest()
    ref = pasta / "resultado.json"
    if ref.exists():
        gravado = json.loads(ref.read_text(encoding="utf-8"))
        out["resultado_igual_ao_gravado"] = {k: gravado.get(k) == v for k, v in json.loads(texto).items()}
    return out


# ================================================================== os logs
def _cronometrar(f, n: int) -> float:
    melhor = float("inf")
    for _ in range(n):
        t0 = time.perf_counter()
        f()
        melhor = min(melhor, time.perf_counter() - t0)
    return round(melhor, 5)


def modo_logs(a) -> dict:
    _exigir_semente(a.semente)
    dono, dias, orc = ma.DONOS[0], ma.DIAS, ma.ORCAMENTO_POR_DIA
    motor, registro, fab, categorias = ma.viver(BRACO, dono, LUGAR, a.semente, dias, orc)
    LogDeEventos = orq.LogDeEventos
    texto = motor.log.para_jsonl()
    dicts = [e.para_dict() for e in motor.log]
    b = texto.encode("utf-8")
    n = a.repeticoes
    out = {"log_bytes": len(b), "eventos": len(dicts), "melhor_de": n, "s": {
        "para_jsonl": _cronometrar(motor.log.para_jsonl, n),
        "so_para_dict": _cronometrar(lambda: [e.para_dict() for e in motor.log], n),
        "so_json_dumps_por_linha": _cronometrar(lambda: "\n".join(json.dumps(d, ensure_ascii=False) for d in dicts), n),
        "de_jsonl": _cronometrar(lambda: LogDeEventos.de_jsonl(texto), n),
        "so_json_loads_por_linha": _cronometrar(lambda: [json.loads(x) for x in texto.splitlines() if x.strip()], n),
        "gzip_compress_6": _cronometrar(lambda: gzip.compress(b, compresslevel=6, mtime=0), n),
        "gzip_compress_9": _cronometrar(lambda: gzip.compress(b, compresslevel=9, mtime=0), n),
        "gzip_decompress": _cronometrar(lambda: gzip.decompress(gzip.compress(b, 9, mtime=0)), n),
    }}
    out["gzip9_bytes"] = len(gzip.compress(b, compresslevel=9, mtime=0))
    # as linhas como o LogDeEventos.para_jsonl as grava (separadores padrao ", " e ": "); "bytes_identicos_ao_json" compara com o compacto
    linhas_json = [json.dumps(d, ensure_ascii=False) for d in dicts]
    if "\n".join(linhas_json) != texto:
        raise RuntimeError("as linhas nao refazem o para_jsonl")
    try:
        import orjson  # noqa: PLC0415 -- so na medicao, fora do pacote digilab/
        out["orjson"] = {"versao": orjson.__version__,
                         "dumps_por_linha": _cronometrar(lambda: [orjson.dumps(d) for d in dicts], n),
                         "loads_por_linha": _cronometrar(lambda: [orjson.loads(x) for x in linhas_json], n),
                         "bytes_identicos_ao_json": all(orjson.dumps(d) == json.dumps(d, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
                                                        for d in dicts),
                         "bytes_identicos_ao_log": all(orjson.dumps(d) == x.encode("utf-8") for d, x in zip(dicts, linhas_json)),
                         "loads_igual": all(orjson.loads(x) == json.loads(x) for x in linhas_json)}
    except ImportError:
        out["orjson"] = None
    try:
        import msgspec  # noqa: PLC0415
        enc, dec = msgspec.json.Encoder(), msgspec.json.Decoder()
        out["msgspec"] = {"versao": msgspec.__version__,
                          "dumps_por_linha": _cronometrar(lambda: [enc.encode(d) for d in dicts], n),
                          "loads_por_linha": _cronometrar(lambda: [dec.decode(x) for x in linhas_json], n),
                          "bytes_identicos_ao_json": all(enc.encode(d) == json.dumps(d, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
                                                         for d in dicts),
                          "bytes_identicos_ao_log": all(enc.encode(d) == x.encode("utf-8") for d, x in zip(dicts, linhas_json)),
                          "loads_igual": all(dec.decode(x) == json.loads(x) for x in linhas_json)}
    except ImportError:
        out["msgspec"] = None
    return out


# ================================================================== comparar dois interpretadores
def _folhas(x, prefixo=""):
    if isinstance(x, dict):
        for k in sorted(x):
            yield from _folhas(x[k], f"{prefixo}.{k}" if prefixo else str(k))
    elif isinstance(x, list):
        for i, v in enumerate(x):
            yield from _folhas(v, f"{prefixo}[{i}]")
    else:
        yield prefixo, x


def modo_comparar(a) -> dict:
    ra, rb = (json.loads(Path(f).read_text(encoding="utf-8")) for f in (a.a, a.b))
    va = {v["semente"]: v for v in ra["vidas"] if v["repeticao"] == 0}
    vb = {v["semente"]: v for v in rb["vidas"] if v["repeticao"] == 0}
    if sorted(va) != sorted(vb):
        raise RuntimeError(f"sementes diferentes: {sorted(va)} x {sorted(vb)}")
    out = {"a": {"arquivo": a.a, "interpretador": ra["interpretador"]}, "b": {"arquivo": a.b, "interpretador": rb["interpretador"]},
           "sementes": {}}
    for s in sorted(va):
        igual = {k: va[s][k] == vb[s][k] for k in ("log_sha256", "estado_interno_sha256", "resumo_motor_sha256", "medidas_sha256")}
        fa = dict(_folhas(json.loads((Path(a.medidas_a) / f"medidas_{s}.json").read_text(encoding="utf-8"))))
        fb = dict(_folhas(json.loads((Path(a.medidas_b) / f"medidas_{s}.json").read_text(encoding="utf-8"))))
        if sorted(fa) != sorted(fb):
            raise RuntimeError(f"semente {s}: as medidas tem campos diferentes")
        difs = {k: {"a": repr(fa[k]), "b": repr(fb[k])} for k in sorted(fa) if fa[k] != fb[k]}
        out["sementes"][str(s)] = {"igual": igual, "medidas_campos": len(fa), "medidas_diferentes": difs}
    return out


# ================================================================== os gabaritos dos testes, regerados neste interpretador
def modo_gabaritos(a) -> dict:
    """Regera cada gabarito de tests/ (o `gerar()` do modulo) e conta, por chave de cada vida, quantas vidas divergem do gravado."""
    import importlib  # noqa: PLC0415
    sys.path.insert(0, str(RAIZ / "tests"))
    out = {}
    for nome in a.modulos:
        g = importlib.import_module(nome)
        gravado = json.loads(g.ARQUIVO.read_text(encoding="utf-8"))
        t0 = time.perf_counter()
        novo = json.loads(json.dumps(g.gerar(), sort_keys=True))
        cont: dict = {}
        for vida, v in gravado.items():
            if vida not in novo:
                raise RuntimeError(f"{nome}: a vida {vida} sumiu")
            for k in v:
                if v[k] != novo[vida].get(k):
                    cont[k] = cont.get(k, 0) + 1
        out[nome] = {"vidas": len(gravado), "chaves_por_vida": sorted({k for v in gravado.values() for k in v}),
                     "vidas_que_divergem_por_chave": cont, "parede_s": round(time.perf_counter() - t0, 1)}
    return {"gabaritos": out}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="modo", required=True)
    p = sub.add_parser("perfil")
    p.add_argument("--semente", type=int, default=101)
    p.add_argument("--saida", required=True)
    t = sub.add_parser("tempo")
    t.add_argument("--sementes", type=int, nargs="+", default=[101, 202, 303])
    t.add_argument("--repeticoes", type=int, default=1)
    t.add_argument("--medidas", default=None, help="pasta onde gravar as medidas de cada semente (a 1a repeticao), para comparar")
    t.add_argument("--saida", required=True)
    n = sub.add_parser("analise")
    n.add_argument("--run", required=True)
    n.add_argument("--saida", required=True)
    g = sub.add_parser("logs")
    g.add_argument("--semente", type=int, default=101)
    g.add_argument("--repeticoes", type=int, default=5)
    g.add_argument("--saida", required=True)
    c = sub.add_parser("comparar")
    for nome in ("--a", "--b", "--medidas-a", "--medidas-b", "--saida"):
        c.add_argument(nome, required=True)
    b = sub.add_parser("gabaritos")
    b.add_argument("--modulos", nargs="+", required=True)
    b.add_argument("--saida", required=True)
    a = ap.parse_args(argv)
    t0 = time.perf_counter()
    r = {"modo": a.modo, "interpretador": interpretador(), **{"perfil": modo_perfil, "tempo": modo_tempo, "analise": modo_analise,
                                                                "logs": modo_logs, "comparar": modo_comparar,
                                                                "gabaritos": modo_gabaritos}[a.modo](a)}
    r["parede_script_s"] = round(time.perf_counter() - t0, 3)
    destino = Path(a.saida) / "medida.json" if a.modo in ("perfil", "analise") else Path(a.saida)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(r, indent=1, ensure_ascii=False, sort_keys=True), encoding="utf-8", newline="\n")
    print(json.dumps({k: r[k] for k in r if k not in ("vidas",)}, ensure_ascii=True, default=str)[:3000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
