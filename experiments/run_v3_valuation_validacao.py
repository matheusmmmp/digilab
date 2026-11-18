"""VALUATION, a V4: a validacao contra a baseline trivial (docs/PLANO_ANALISE_V3_VALUATION_VALIDACAO.md), uma vez.

    python experiments/run_v3_valuation_validacao.py --config experiments/configs/v3_valuation/validacao.json --processos 4

Tres bracos nas mesmas unidades e nas 12 celulas da C4 (secao 2):
  - TRIV: a baseline trivial da A1 (`experiments/bancada/baseline_trivial.py`), com o ponto da calibracao da A1 lido do
    `artifacts_v3_baseline_trivial/calibracao/resultado.json`, com o sha256 conferido contra o meta dela (VB-2: sem calibracao nova);
  - REL e CON: as vidas do `run_v3_valuation_conserto.py`, sem mudanca (o CON com a `guarda_fome_reflexo` ligada), com a conferencia
    do reflexo decisao a decisao.

O primario e CON - TRIV na taxa por episodio no `longe_fixo` (a metrica da A1), com a classe de A6.6 e a margem 0,032 (secao 3). As
secundarias (REL - TRIV no `longe_fixo`; CON - TRIV no comedouro e no longe) e o descritivo do bem-estar nao tem gate.

As travas: o plano com "APROVADO pelo Matheus" no cabecalho; a faixa em FAIXAS_RESERVADAS; o `tools/pre_run.py` (o H10: o plano daqui e
o da `origin/main`, uma run por vez, no maximo 4 processos) antes de uma run de verdade; a pasta de saida nao pode existir (uma vez).
"""
from __future__ import annotations

import argparse
import gzip
import json
import platform
import shutil
import statistics
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tools"))

import bancada_v2 as bv  # noqa: E402
import pre_run  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402
import run_v2_longe_regular as lr  # noqa: E402
import run_v2_memoria_autobio as ma  # noqa: E402
import run_v3_baseline_trivial as B  # noqa: E402
import run_v3_valuation as V  # noqa: E402
import run_v3_valuation_conserto as K  # noqa: E402
from bancada.baseline_trivial import LimiaresTriviais  # noqa: E402
from bancada.faixas import FAIXAS_RESERVADAS  # noqa: E402

ORQUESTRADOR = "experiments/run_v3_valuation_validacao.py"
PLANO = "docs/PLANO_ANALISE_V3_VALUATION_VALIDACAO.md"
FASE = "validacao"
PREFIXO = orq.PREFIXO
BASES = (81101, 81202, 81303, 81404, 81505)                   # secao 2.3 (VB-3)
FAIXA = (81101, 81505)
K_POR_BASE = 40                                                # N = 200 (VB-3)
DIAS, ORCAMENTO_POR_DIA = orq.DIAS, orq.ORCAMENTO_POR_DIA      # secao 2.1 (os da C4)
SAIDA = "artifacts_v3_valuation/validacao"                     # secao 4
CALIBRACAO_A1 = RAIZ / "artifacts_v3_baseline_trivial" / "calibracao"   # VB-2
MAX_PROCESSOS = 4                                              # V3-D8
CELULAS = ma.CELULAS                                           # as 12 da C4 (VB-4)
PRIMARIO, LUGARES = ma.PRIMARIO, ma.LUGARES
TRIV, REL, CON = B.TRIV, "REL", "CON"
BRACOS = (TRIV, REL, CON)                                      # VB-1
MARGEM = B.MARGEM                                              # VB-5: o 0,032 da A1
EPISODIO = B.EPISODIO
CHAVES_CONFIG = V.CHAVES_CONFIG

LEITURA = {"> 0": "ganho: com o conserto, o modular fecha mais episodios que a TRIV",
           "≈ 0": "nulo: o conserto empata com a TRIV, e o gap da A1 fecha",
           "< 0": "perda: mesmo com o conserto, a TRIV fecha mais",
           "indeterminado": "indeterminado: o IC95 cruza o 0 sem caber na margem"}


# ================================================================== a baseline (VB-2)
def limiares_da_a1(pasta: Path = CALIBRACAO_A1) -> tuple[LimiaresTriviais, dict]:
    """o ponto da calibracao da A1, com o sha256 do resultado conferido contra o meta dela (falha alto se nao confere)"""
    return B.limiares_da_calibracao(pasta, "validacao")


# ================================================================== as vidas
def tarefa(cfg: dict, limiares: LimiaresTriviais, unidade: dict, pasta: str) -> list[dict]:
    out = [B._vida_triv(cfg, limiares, dono, lugar, unidade, pasta) for dono, lugar in CELULAS]
    return out + [K._vida(cfg, b, dono, lugar, unidade, pasta) for b in (REL, CON) for dono, lugar in CELULAS]


# ================================================================== a analise (secao 3, escrita antes; funcoes puras)
def _celulas(lugar: str | None) -> tuple:
    return CELULAS if lugar is None else tuple(c for c in CELULAS if c[1] == lugar)


def contraste(registros: list[dict], a: str, b: str, lugar: str, boot: dict = orq.BOOTSTRAP) -> dict:
    """a - b na taxa por episodio, nas 4 celulas do lugar: o t pareado, a classe de A6.6 e a margem efetiva"""
    difs = orq.por_unidade(registros, a, b, EPISODIO, _celulas(lugar))
    c = orq.contraste_t(difs, boot)
    ic = {"ic_inferior": c["ic95"]["ic_inferior"], "ic_superior": c["ic95"]["ic_superior"], "motivo": c["motivo"]}
    dp = statistics.stdev(difs.values()) if len(difs) > 1 else None
    return {"contraste": f"{a} - {b}, a taxa de fechamento por episodio, nas 4 celulas do {lugar}", **c,
            "classe": lr.classe(ic, MARGEM), "margem": MARGEM, "margem_efetiva": lr.margem_efetiva(dp, c["n"])}


def leitura(prim: dict) -> dict:
    """3.2: a classe do IC95 de CON - TRIV, nas palavras do pedido"""
    c = prim["classe"]["classe"]
    return {"classe": c, "leitura": LEITURA[c].split(":")[0], "texto": LEITURA[c]}


MEDIDAS = {"episodio": EPISODIO, "privacao": lambda r: r["privacao"], "exaustao": lambda r: r["exaustao"],
           "episodios_n": lambda r: r["episodios_fome"]["n"]}


def descritivo(registros: list[dict]) -> dict:
    """3.3, sem classe: o nivel de cada braco em cada lugar e as diferencas CON - TRIV e REL - TRIV"""
    sem_classe = lambda e: {k: v for k, v in e.items() if k != "classe"}   # noqa: E731
    out = {}
    for m, f in MEDIDAS.items():
        out[m] = {lu: {"niveis": {b: sem_classe(ma.estimativa(orq.por_unidade(registros, b, None, f, _celulas(lu)))) for b in BRACOS},
                       **{f"{a} - {TRIV}": sem_classe(ma.estimativa(orq.por_unidade(registros, a, TRIV, f, _celulas(lu)))) for a in (CON, REL)}}
                  for lu in LUGARES}
    return out


def analisar(registros: list[dict], boot: dict = orq.BOOTSTRAP) -> dict:
    prim = contraste(registros, CON, TRIV, PRIMARIO, boot)
    return {"primario": prim, "leitura": leitura(prim),
            "secundarias": {"REL - TRIV, longe_fixo (a replica da A1)": contraste(registros, REL, TRIV, PRIMARIO, boot),
                            **{f"CON - TRIV, {lu}": contraste(registros, CON, TRIV, lu, boot) for lu in LUGARES if lu != PRIMARIO}},
            "descritivo": descritivo(registros),
            "nao_demonstra": ["que o conserto pode entrar num pet: ele reprovou na V3 pela exaustao (G2), e esta run nao muda isso",
                              "que a baseline e a melhor politica trivial possivel (so a grade da A1)",
                              "nada sobre o jogo web", "nada fora das 12 celulas, dos 14 dias e do mundo do MVP"]}


# ================================================================== a trava e a run
def exigir_aprovado(plano: str) -> None:
    status = [x for x in plano.splitlines() if x.startswith("**Status:")]
    if not status or not status[0].startswith("**Status: APROVADO pelo Matheus"):
        raise RuntimeError(f"o plano {PLANO} nao esta APROVADO pelo Matheus no cabecalho: {status[:1] or 'sem a linha do status'}")


def modo_da_config(cfg: dict) -> str:
    faltam, sobram = (CHAVES_CONFIG - {"descricao"}) - set(cfg), set(cfg) - CHAVES_CONFIG
    if faltam or sobram:
        raise ValueError(f"config: faltam {sorted(faltam)}, sobram {sorted(sobram)}")
    if cfg["fase"] != FASE:
        raise ValueError(f"fase {cfg['fase']!r}: so {FASE!r}")
    u = cfg["unidades"]
    bases = tuple(u["bases"])
    if u.get("prefixo") != PREFIXO or cfg["orcamento_por_dia"] != ORCAMENTO_POR_DIA or type(u.get("k")) is not int or u["k"] < 1:
        raise ValueError("config fora do plano: o prefixo, o orcamento ou o K (secao 2.3)")
    if bases and set(bases) <= bv.SEMENTES_TESTE:
        if not 1 <= cfg["dias"] <= DIAS:
            raise ValueError(f"fumaca com {cfg['dias']} dias: de 1 a {DIAS}")
        return "fumaca"
    if bases != BASES:
        raise bv.SementeSemPlano(f"bases {list(bases)}: so as dos testes (fumaca) ou {list(BASES)} (secao 2.3)")
    if not any((lo, hi) == FAIXA for lo, hi, _ in FAIXAS_RESERVADAS):
        raise bv.SementeSemPlano(f"a faixa {FAIXA} nao esta em FAIXAS_RESERVADAS (secao 2.3)")
    exigir_aprovado((RAIZ / PLANO).read_text(encoding="utf-8"))
    erros = [m for m, ok in ((f"dias {cfg['dias']} (o plano: {DIAS})", cfg["dias"] == DIAS), (f"plano {cfg.get('plano')!r}", cfg.get("plano") == PLANO),
                             (f"K por base {u['k']} (o plano: {K_POR_BASE})", u["k"] == K_POR_BASE)) if not ok]
    if erros:
        raise ValueError(f"a run segue o plano a letra: {erros}")
    return FASE


def rodar(cfg: dict, pasta: Path, processos: int, caminho_config: Path | None = None) -> dict:
    if processos > MAX_PROCESSOS:
        raise ValueError(f"no maximo {MAX_PROCESSOS} processos (V3-D8)")
    modo = modo_da_config(cfg)
    if pasta.exists():
        raise FileExistsError(f"{pasta} ja existe: a run se recusa a gravar por cima (uma vez; secao 4)")
    limiares, calibracao = limiares_da_a1()
    unidades = bv.unidades_derivadas(cfg["unidades"]["bases"], int(cfg["unidades"]["k"]), PREFIXO)
    pasta.mkdir(parents=True)
    inicio = time.time()
    rc = orq.rc
    meta = {"modo": modo, "fase": FASE, "plano": PLANO, "plano_sha256": rc._sha_arquivo(RAIZ / PLANO), "config": cfg,
            "config_arquivo": None if caminho_config is None else rc._relativo(caminho_config),
            "config_sha256": None if caminho_config is None else rc._sha_arquivo(caminho_config),
            "comando": " ".join(["python", *sys.argv]) if sys.argv and sys.argv[0] else None,
            "python": platform.python_version(), "node": V._versao_node(),
            "orquestrador_sha256": rc._sha_arquivo(Path(__file__)), "conserto_sha256": rc._sha_arquivo(Path(K.__file__)),
            "baseline_trivial_sha256": rc._sha_arquivo(Path(B.__file__)), "valuation_v2_sha256": rc._sha_arquivo(Path(V.__file__)),
            "prototipo_sha256": rc._sha_arquivo(Path(orq.__file__)), "c4_sha256": rc._sha_arquivo(Path(ma.__file__)),
            "baseline_sha256": rc._sha_arquivo(RAIZ / "experiments" / "bancada" / "baseline_trivial.py"),
            "calibracao_a1": calibracao,
            "git_head": rc._git("rev-parse", "HEAD"), "git_limpo": rc._git("status", "--porcelain") == "", "processos": processos,
            "unidades": unidades, "celulas": [list(c) for c in CELULAS], "bracos": list(BRACOS), "faixa": list(FAIXA),
            "sha256": {n: rc._sha_arquivo(RAIZ / "digilab" / n) for n in ("config.py", "engine.py", "metrics.py", "mundo.py")}
            | {f"digibrain/{p.name}": rc._sha_arquivo(p) for p in sorted((RAIZ / "digilab" / "digibrain").glob("*.py"))},
            "inicio": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(inicio))}
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    t0 = time.perf_counter()
    registros = [r for s in rc._executar([(tarefa, (cfg, limiares, u, str(pasta))) for u in unidades], processos) for r in s]
    meta["vidas_parede_s"] = time.perf_counter() - t0
    esperadas = len(unidades) * len(BRACOS) * len(CELULAS)
    if len(registros) != esperadas:
        raise RuntimeError(f"{len(registros)} vidas, eram {esperadas}")
    bv._gravar(pasta / "medidas.json", bv._dump(sorted(registros, key=lambda r: r["vida"])))
    lidos = json.loads((pasta / "medidas.json").read_text(encoding="utf-8"))
    resultado = {"modo": modo, "fase": FASE, "plano": PLANO, "unidades": len(unidades), "vidas": len(lidos),
                 "limiares_triv": calibracao["escolhido"], **analisar(lidos)}
    bv._gravar(pasta / "resultado.json", bv._dump(resultado))
    nomes = ["medidas.json", "resultado.json"]
    if (pasta / "medidas.json").stat().st_size > 100 * 2**20:
        with open(pasta / "medidas.json", "rb") as f, open(pasta / "medidas.json.gz", "wb") as s, \
                gzip.GzipFile(filename="", mode="wb", fileobj=s, mtime=0, compresslevel=9) as gz:
            shutil.copyfileobj(f, gz)
        nomes.append("medidas.json.gz")
    V.tar_deterministico(pasta / "vidas", pasta / "vidas.tar.gz")
    nomes.append("vidas.tar.gz")
    meta["fim"] = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
    meta["duracao_s"] = time.time() - inicio
    meta["artefatos_sha256"] = {n: bv._sha(pasta / n) for n in nomes}
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    return {"meta": meta, "registros": registros, "resultado": resultado}


def _resumo(r: dict) -> str:
    """o resumo no console, ASCII puro"""
    curto = lambda c: {k: c[k] for k in ("media", "ic95", "p_unilateral")} | {"classe": c["classe"]["classe"]}   # noqa: E731
    return json.dumps({"modo": r["modo"], "vidas": r["vidas"], "leitura": r["leitura"]["leitura"], "primario": curto(r["primario"]),
                       "secundarias": {n: curto(c) for n, c in r["secundarias"].items()}}, indent=1, ensure_ascii=True, default=str)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--config", required=True)
    ap.add_argument("--saida", default=None)
    ap.add_argument("--processos", type=int, default=1)
    a = ap.parse_args()
    caminho = Path(a.config)
    cfg = json.loads(caminho.read_text(encoding="utf-8"))
    if modo_da_config(cfg) == "fumaca":
        if a.saida is None:
            raise SystemExit(f"a fumaca precisa de --saida (fora de {SAIDA})")
    else:
        pre_run.exigir(ORQUESTRADOR, a.config, a.processos)          # o H10 (D-IA-6) e a V3-D8, antes da run de verdade
    print(_resumo(rodar(cfg, Path(a.saida) if a.saida else RAIZ / SAIDA, a.processos, caminho)["resultado"]))


if __name__ == "__main__":
    main()
