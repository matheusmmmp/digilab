"""ELOGIO: a calibracao (etapa 4) e a validacao (etapa 5) do credito do carinho no modular (docs/PLANO_ANALISE_V3_ELOGIO.md;
docs/TAREFA_V3_ELOGIO.md).

As vidas sao as do `experiments/elogio.py` (o mundo `casado`, o corpo com os gestos, o modular REL, o dono atencioso no comedouro), 12 dias
(D-EL-18), com a `VistaFrutas` (so le) para as frutas presentes de cada consumo (D-EL-19). A unidade e a semente.
  - **calibracao** (secao 5; 25101...25200): por unidade, o E0 (a chave ligada, sem carinho) e, em cada celula g x W da D-EL-8, o par
    E-imed x E-sorteado (`viver_par`). A escolha (D-EL-21): o menor g e, nele, o menor W com o IC95 inferior de E-imed - E-sorteado em M2
    acima de 0 e sem piora da M4 (o IC95 superior da privacao e da exaustao abaixo de +0,032). Nenhuma: `escolha` None, e para.
  - **validacao** (secao 6; 25301...25500; uma vez, no g e no W da config): E0-off (a chave desligada), E0, E-imed, E-sorteado, E-atraso
    e E-incons; P0, P1, P1b, o G-EL1 (D-EL-23) e os secundarios.

As medidas (secao 4) saem do `digilab/metrics.py`: `consumos_com_presentes`, `fracao_da_fruta` (M2 na 1a metade, M3 na 2a),
`decisao_do_criterio` (M1), `privacao_nas_decisoes` e `exaustao_nas_decisoes` (M4, toda a vida).

As travas: o `tools/pre_run.py` (o plano na `origin/main`, a faixa, nenhuma outra run, no maximo 4 processos), o "APROVADO pelo Matheus"
no cabecalho do plano, a config a letra do plano e a pasta de saida nova. A fumaca usa as sementes dos testes e vai para fora de
`resultados/`.
Uso: python experiments/run_v3_elogio.py --config experiments/configs/v3_elogio/calibracao.json --processos 4
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tools"))

import bancada_v2 as bv  # noqa: E402
import elogio as el  # noqa: E402
import pre_run  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402
from bancada.faixas import FAIXAS_RESERVADAS  # noqa: E402
from digilab.config import (CONFIG_DIGIBRAIN_INATOS, CONFIG_ELOGIO, CONFIG_FRUTAS, CONFIG_PADRAO, TICKS_POR_DIA,  # noqa: E402
                            ConfigElogio)
from digilab.events import FRUTAS  # noqa: E402
from digilab.frutas import genoma_frutas  # noqa: E402
from digilab.metrics import (bootstrap_ic, consumos_com_presentes, decisao_do_criterio, exaustao_nas_decisoes,  # noqa: E402
                             fracao_da_fruta, ic_t, privacao_nas_decisoes)
from digilab.protocol import derivar_semente  # noqa: E402

ORQUESTRADOR = "experiments/run_v3_elogio.py"
PLANO = "docs/PLANO_ANALISE_V3_ELOGIO.md"
FAIXA = (25101, 25505)
FASES = {"calibracao": {"base": 25101, "n": 100}, "validacao": {"base": 25301, "n": 200}}
DIAS = 12                                                    # D-EL-18
S = CONFIG_DIGIBRAIN_INATOS.escala
GRADE_G = (S // 4, S // 2, S, 2 * S)                         # D-EL-8
GRADE_W = (1, 2, 4)
CELULAS = tuple((g, w) for g in GRADE_G for w in GRADE_W)    # a ordem da escolha: o menor g, nele o menor W
REAMOSTRAGENS, NIVEL, MARGEM = 2000, 0.95, 0.032             # secao 5; a margem da VALUATION
JANELA_M1, MINIMO_M1 = 10, 8                                 # D-EL-4
LIMIAR_PRIVACAO, LIMIAR_EXAUSTAO = orq.LIMIAR_PRIVACAO, orq.LIMIAR_EXAUSTAO
PASSO = CONFIG_PADRAO.intervalo_decisao_ticks
BRACOS_VALIDACAO = ("E0-off", "E0", "E-imed", "E-sorteado", "E-atraso", "E-incons")
MAX_PROCESSOS = 4
CHAVES_CONFIG = {"descricao", "fase", "plano", "dias", "unidades", "ganho", "janela"}
SAIDA = "resultados/v3_elogio"


# ================================================================== a vida e as medidas
def medir(v: dict, semente: int, dias: int) -> dict:
    """as medidas da secao 4 de uma vida (o dict do `elogio.viver_completo` com a vista)"""
    motor, registro, cerebro, dono, vista = v["motor"], v["registro"], v["cerebro"], v["dono"], v["vista"]
    fim = dias * TICKS_POR_DIA
    meio = fim // 2
    genoma = genoma_frutas(semente, CONFIG_FRUTAS)
    pref = genoma.fruta_preferida()
    rej = min(FRUTAS, key=lambda f: (genoma.preferencia_inata[f], FRUTAS.index(f)))
    x = el.fruta_elogio(semente)
    if motor.entrada_mundo != 0:
        raise RuntimeError("o relogio do mundo nao e o do pet (um pet so)")
    fr = [(c["tick"], c["tipo"]) for c in motor.consumos_mundo if c["tipo"] in FRUTAS]
    cons = consumos_com_presentes(fr, vista.passos)
    janelas = {"m2": (0, meio), "m3": (meio, fim)}
    fx = fracao_da_fruta(cons, x, janelas)
    fp = fracao_da_fruta(cons, pref, janelas)
    es = registro.estados
    if len(es) * PASSO != fim:
        raise RuntimeError(f"{len(es)} decisoes em {dias} dias")
    priv = privacao_nas_decisoes([(k * PASSO, e[0], e[1], e[2], e[3]) for k, e in enumerate(es)], LIMIAR_PRIVACAO)["fracao_privacao"]
    exa = exaustao_nas_decisoes([(k * PASSO, e[2]) for k, e in enumerate(es)], (0, fim), LIMIAR_EXAUSTAO)["frac"]
    rec = list(cerebro.m.sens.receptores)
    desf = cerebro.m.plast.desfecho
    elogios = getattr(cerebro, "elogios", None)
    return {"semente": semente, "x": x, "preferida": pref, "rejeitada": rej, "x_e_preferida": x == pref,
            "m2": fx["m2"]["taxa"], "m2_n": fx["m2"]["n"], "m3": fx["m3"]["taxa"], "m3_n": fx["m3"]["n"],
            "pref_1a": fp["m2"]["taxa"], "pref_2a": fp["m3"]["taxa"],
            "m1": decisao_do_criterio(fr, x, JANELA_M1, MINIMO_M1, PASSO),
            "privacao": priv, "exaustao": exa,
            "frutas_dia": len(fr) / dias, "racoes_dia": sum(1 for c in motor.consumos_mundo if c["tipo"] == "racao") / dias,
            "carinhos": 0 if dono is None else len(dono.carinhos), "atrasos": [] if dono is None else list(dono.atrasos),
            "elogios": 0 if elogios is None else len(elogios),
            "sinais_zero": 0 if elogios is None else sum(1 for e in elogios if e["sinal"] == 0),
            "desfecho_x": {r: desf[x][rec.index(r)] for r in ("humor", "solidao")},
            "p1b_humor": desf[pref][rec.index("humor")] - desf[rej][rec.index("humor")],
            "log_sha256": hashlib.sha256(motor.log.para_jsonl().encode("utf-8")).hexdigest()}


def _vida(braco: str, semente: int, dias: int, cfg: ConfigElogio, sorteados=None) -> dict:
    nome = "E0" if braco == "E0-off" else braco
    return medir(el.viver_completo(nome, semente, dias, cfg, sorteados, vista=True), semente, dias)


def _par(semente: int, dias: int, cfg: ConfigElogio) -> tuple[dict, dict]:
    """o E-imed e o E-sorteado com o mesmo numero de carinhos (o `elogio.viver_par`, com a vista)"""
    imed = _vida("E-imed", semente, dias, cfg)
    sorteados = el.passos_sorteados(imed["carinhos"], el.passos_da_vida(dias) // 2, semente)
    return imed, _vida("E-sorteado", semente, dias, cfg, sorteados)


def tarefa(fase: str, semente: int, dias: int, ganho: int | None, janela: int | None) -> list[dict]:
    """as vidas de uma unidade na fase"""
    out = []
    if fase == "calibracao":
        out.append({"celula": None, "braco": "E0", **_vida("E0", semente, dias, ConfigElogio(ligada=True))})
        for g, w in CELULAS:
            imed, sort = _par(semente, dias, ConfigElogio(ligada=True, ganho=g, janela=w))
            out += [{"celula": [g, w], "braco": "E-imed", **imed}, {"celula": [g, w], "braco": "E-sorteado", **sort}]
        return out
    if fase != "validacao":
        raise ValueError(f"fase {fase!r}")
    cfg = ConfigElogio(ligada=True, ganho=ganho, janela=janela)
    out.append({"celula": None, "braco": "E0-off", **_vida("E0-off", semente, dias, CONFIG_ELOGIO)})
    out.append({"celula": None, "braco": "E0", **_vida("E0", semente, dias, cfg)})
    imed, sort = _par(semente, dias, cfg)
    out += [{"celula": None, "braco": "E-imed", **imed}, {"celula": None, "braco": "E-sorteado", **sort}]
    for b in ("E-atraso", "E-incons"):
        out.append({"celula": None, "braco": b, **_vida(b, semente, dias, cfg)})
    return out


# ================================================================== a analise (funcoes puras)
def _por_semente(regs: list[dict], braco: str, celula=None) -> dict:
    out = {}
    for r in regs:
        if r["braco"] == braco and r["celula"] == celula:
            if r["semente"] in out:
                raise RuntimeError(f"vida repetida: {braco} {celula} {r['semente']}")
            out[r["semente"]] = r
    return out


def diferencas(regs: list[dict], a: str, b: str, medida: str, celula=None) -> dict:
    """a - b por unidade na medida; as unidades com a medida None em um dos dois ficam fora, contadas"""
    ra, rb = _por_semente(regs, a, celula), _por_semente(regs, b, celula)
    if set(ra) != set(rb):
        raise RuntimeError(f"{a} e {b} sem as mesmas unidades")
    d = [ra[s][medida] - rb[s][medida] for s in sorted(ra) if ra[s][medida] is not None and rb[s][medida] is not None]
    return {"valores": d, "fora": len(ra) - len(d)}


def _ic(valores: list[float], semente: int) -> dict:
    """o IC95 por bootstrap; com menos de 2 unidades nao ha IC (None), e o contraste nao passa"""
    if len(valores) < 2:
        return {"media": None, "ic95": None, "n": len(valores)}
    b = bootstrap_ic(valores, REAMOSTRAGENS, semente, NIVEL)
    return {"media": b["media"], "ic95": [b["ic_inferior"], b["ic_superior"]], "n": b["n"]}


def contraste(regs: list[dict], a: str, b: str, celula, rotulo: str) -> dict:
    """M2 com a guarda da M4 (secoes 5 e 6): o IC95 por bootstrap das diferencas por unidade, com a semente do rotulo"""
    out = {}
    for k, m in enumerate(("m2", "privacao", "exaustao")):
        d = diferencas(regs, a, b, m, celula)
        out[m] = {**_ic(d["valores"], derivar_semente(rotulo, m, k)), "fora": d["fora"]}
    out["m2_passa"] = out["m2"]["ic95"] is not None and out["m2"]["ic95"][0] > 0
    out["m4_passa"] = all(out[m]["ic95"] is not None and out[m]["ic95"][1] < MARGEM for m in ("privacao", "exaustao"))
    return out


def analisar_calibracao(regs: list[dict]) -> dict:
    celulas = []
    for g, w in CELULAS:
        c = contraste(regs, "E-imed", "E-sorteado", [g, w], f"elogio-bootstrap-{g}x{w}")
        celulas.append({"ganho": g, "janela": w, **c, "passa": c["m2_passa"] and c["m4_passa"]})
    escolha = next(({"ganho": c["ganho"], "janela": c["janela"]} for c in celulas if c["passa"]), None)
    e0 = _por_semente(regs, "E0")
    p1 = [r["pref_2a"] - r["pref_1a"] for r in e0.values() if r["pref_1a"] is not None and r["pref_2a"] is not None]
    return {"celulas": celulas, "escolha": escolha, "p1_e0": {**ic_t(p1), "n": len(p1)}}


def analisar_validacao(regs: list[dict]) -> dict:
    off, e0 = _por_semente(regs, "E0-off"), _por_semente(regs, "E0")
    p0 = {"log_igual": all(off[s]["log_sha256"] == e0[s]["log_sha256"] for s in off),
          "sinais_zero": sum(r["sinais_zero"] for r in regs)}
    p0["passa"] = p0["log_igual"] and p0["sinais_zero"] == 0
    p1v = [r["pref_2a"] - r["pref_1a"] for r in e0.values() if r["pref_1a"] is not None and r["pref_2a"] is not None]
    p1 = {**ic_t(p1v), "n": len(p1v)}
    p1["passa"] = None if p1["ic_inferior"] is None else p1["ic_inferior"] > 0
    g = contraste(regs, "E-imed", "E-sorteado", None, "elogio-validacao")
    classe = ("confirma" if g["m2_passa"] and g["m4_passa"] else "confirma com custo" if g["m2_passa"] else "nao confirma")
    sec = {}
    for nome, (a, b) in {"imed_menos_e0": ("E-imed", "E0"), "atraso_menos_imed": ("E-atraso", "E-imed"),
                         "incons_menos_imed": ("E-incons", "E-imed")}.items():
        d = diferencas(regs, a, b, "m2")
        sec[nome] = {**_ic(d["valores"], derivar_semente("elogio-secundario", nome)), "fora": d["fora"]}
    d3 = diferencas(regs, "E-imed", "E-sorteado", "m3")
    sec["m3_imed_menos_sorteado"] = {**_ic(d3["valores"], derivar_semente("elogio-secundario", "m3")), "fora": d3["fora"]}
    imed, sort = _por_semente(regs, "E-imed"), _por_semente(regs, "E-sorteado")
    for lado, alvo in (("x_preferida", True), ("x_outra", False)):
        v = [imed[s]["m2"] - sort[s]["m2"] for s in imed if imed[s]["x_e_preferida"] is alvo
             and imed[s]["m2"] is not None and sort[s]["m2"] is not None]
        sec[f"imed_menos_sorteado_{lado}"] = _ic(v, derivar_semente("elogio-secundario", lado))
    atrasos = [a for r in _por_semente(regs, "E-atraso").values() for a in r["atrasos"]]
    sec["atrasos_sorteados"] = {str(a): atrasos.count(a) for a in el.ATRASOS}
    p1b = [r["p1b_humor"] for r in e0.values()]
    return {"P0": p0, "P1": p1, "P1b": {**ic_t(p1b), "n": len(p1b)}, "G_EL1": {**g, "classe": classe}, "secundarios": sec}


# ================================================================== a trava e a run
def exigir_aprovado(texto: str) -> None:
    status = [x for x in texto.splitlines() if x.startswith("**Status:")]
    if not status or not status[0].startswith("**Status: APROVADO pelo Matheus"):
        raise RuntimeError(f"o plano {PLANO} nao esta APROVADO pelo Matheus no cabecalho")


def modo_da_config(cfg: dict) -> str:
    faltam, sobram = (CHAVES_CONFIG - {"descricao"}) - set(cfg), set(cfg) - CHAVES_CONFIG
    if faltam or sobram:
        raise ValueError(f"config: faltam {sorted(faltam)}, sobram {sorted(sobram)}")
    fase = cfg["fase"]
    if fase not in FASES:
        raise ValueError(f"fase {fase!r}: so {sorted(FASES)}")
    if cfg["plano"] != PLANO:
        raise ValueError(f"plano {cfg['plano']!r}: so {PLANO}")
    if fase == "calibracao" and (cfg["ganho"] is not None or cfg["janela"] is not None):
        raise ValueError("a calibracao roda a grade: ganho e janela None")
    if fase == "validacao" and (cfg["ganho"] not in GRADE_G or cfg["janela"] not in GRADE_W):
        raise ValueError(f"a validacao roda uma celula da grade: ganho {cfg['ganho']}, janela {cfg['janela']}")
    bases, n = list(cfg["unidades"]["bases"]), cfg["unidades"]["n"]
    if len(bases) != 1 or type(n) is not int or n < 2:
        raise ValueError("unidades: uma base e n >= 2 (as sementes base...base+n-1)")
    sementes = range(bases[0], bases[0] + n)
    if all(101 <= s <= 505 for s in sementes):              # as sementes dos testes
        if not 1 <= cfg["dias"] <= DIAS:
            raise ValueError(f"fumaca com {cfg['dias']} dias: de 1 a {DIAS}")
        return "fumaca"
    if bases[0] != FASES[fase]["base"] or n != FASES[fase]["n"] or cfg["dias"] != DIAS:
        raise bv.SementeSemPlano(f"a {fase} segue o plano a letra: base {FASES[fase]['base']}, n {FASES[fase]['n']}, {DIAS} dias")
    if not any((lo, hi) == FAIXA for lo, hi, _ in FAIXAS_RESERVADAS):
        raise bv.SementeSemPlano(f"a faixa {FAIXA} nao esta em FAIXAS_RESERVADAS")
    exigir_aprovado((RAIZ / PLANO).read_text(encoding="utf-8"))
    return fase


def rodar(cfg: dict, pasta: Path, processos: int, caminho_config: Path | None = None) -> dict:
    if processos > MAX_PROCESSOS:
        raise ValueError(f"no maximo {MAX_PROCESSOS} processos (V3-D8)")
    modo = modo_da_config(cfg)
    if pasta.exists():
        raise FileExistsError(f"{pasta} ja existe: a run se recusa a gravar por cima")
    fase, dias = cfg["fase"], cfg["dias"]
    base, n = cfg["unidades"]["bases"][0], cfg["unidades"]["n"]
    pasta.mkdir(parents=True)
    rc = orq.rc
    inicio = time.time()
    meta = {"modo": modo, "fase": fase, "plano": PLANO, "plano_sha256": rc._sha_arquivo(RAIZ / PLANO), "config": cfg,
            "config_arquivo": None if caminho_config is None else rc._relativo(caminho_config),
            "config_sha256": None if caminho_config is None else rc._sha_arquivo(caminho_config),
            "comando": " ".join(["python", *sys.argv]) if sys.argv and sys.argv[0] else None, "python": platform.python_version(),
            "orquestrador_sha256": rc._sha_arquivo(Path(__file__)), "elogio_sha256": rc._sha_arquivo(Path(el.__file__)),
            "prototipo_sha256": rc._sha_arquivo(Path(orq.__file__)),
            "git_head": rc._git("rev-parse", "HEAD"), "git_limpo": rc._git("status", "--porcelain") == "", "processos": processos,
            "sementes": [base, base + n - 1], "faixa": list(FAIXA), "celulas": [list(c) for c in CELULAS],
            "sha256": {k: rc._sha_arquivo(RAIZ / "digilab" / k) for k in ("config.py", "engine.py", "metrics.py", "mundo.py")}
            | {f"digibrain/{p.name}": rc._sha_arquivo(p) for p in sorted((RAIZ / "digilab" / "digibrain").glob("*.py"))},
            "inicio": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(inicio))}
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    regs = [r for s in rc._executar([(tarefa, (fase, s, dias, cfg["ganho"], cfg["janela"])) for s in range(base, base + n)], processos)
            for r in s]
    esperadas = n * (1 + 2 * len(CELULAS) if fase == "calibracao" else len(BRACOS_VALIDACAO))
    if len(regs) != esperadas:
        raise RuntimeError(f"{len(regs)} vidas, eram {esperadas}")
    with open(pasta / "vidas.jsonl", "w", encoding="utf-8", newline="\n") as f:
        for r in sorted(regs, key=lambda r: (r["semente"], r["braco"], r["celula"] or [])):
            f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
    lidos = [json.loads(x) for x in (pasta / "vidas.jsonl").read_text(encoding="utf-8").splitlines()]
    analise = analisar_calibracao(lidos) if fase == "calibracao" else analisar_validacao(lidos)
    resultado = {"modo": modo, "fase": fase, "plano": PLANO, "unidades": n, "vidas": len(lidos), **analise}
    bv._gravar(pasta / "resultado.json", bv._dump(resultado))
    meta["fim"] = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
    meta["duracao_s"] = time.time() - inicio
    meta["artefatos_sha256"] = {k: bv._sha(pasta / k) for k in ("vidas.jsonl", "resultado.json")}
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    return resultado


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--config", required=True)
    ap.add_argument("--saida", default=None)
    ap.add_argument("--processos", type=int, default=1)
    a = ap.parse_args()
    caminho = Path(a.config)
    cfg = json.loads(caminho.read_text(encoding="utf-8"))
    modo = modo_da_config(cfg)
    if modo == "fumaca":
        if a.saida is None:
            raise SystemExit(f"a fumaca precisa de --saida (fora de {SAIDA})")
    else:
        pre_run.exigir(ORQUESTRADOR, a.config, a.processos)          # o H10 (D-IA-6) e a V3-D8, antes de tudo
    pasta = Path(a.saida) if a.saida else RAIZ / SAIDA / cfg["fase"]
    r = rodar(cfg, pasta, a.processos, caminho)
    print(json.dumps({k: r[k] for k in r if k in ("modo", "fase", "vidas", "escolha", "G_EL1", "P0", "P1")}, indent=1, ensure_ascii=True,
                     default=str))


if __name__ == "__main__":
    main()
