"""A run da EVIDENCIA A1: o modular contra uma baseline trivial nas células da C4 (docs/PLANO_ANALISE_V3_BASELINE_TRIVIAL.md).

Pergunta (seção 1 do plano): o modular (o REL da C4) fecha mais episódios de fome no `longe_fixo` do que uma política de quatro regras
(experiments/bancada/baseline_trivial.py)? Três etapas, cada uma com a sua config:
- `fumaca`: as sementes dos testes, poucos dias; só confere que o orquestrador roda;
- `calibracao`: a grade de X, Y e Z da seção 4, só a baseline, só nas 4 células do `longe_fixo`, só na faixa 96101...96505; grava o
  ponto escolhido pela regra escrita antes;
- `validacao`: uma vez, o REL e a baseline nas 12 células da C4, na faixa 97101...97505; os limiares saem do `resultado.json` da
  calibração (o sha256 dele conferido contra o meta da calibração e gravado no meta da validação), nunca escritos à mão.

A trava (seção 0 do plano): a calibração e a validação recusam rodar sem o "APROVADO pelo Matheus" no cabeçalho do plano e sem as duas
faixas em FAIXAS_RESERVADAS. A vida do REL é a da C4, sem mudança (`run_v2_memoria_autobio._vida`); a da baseline usa as mesmas fábricas
do mundo e do corpo, o replay do disco (G1), o T-CENARIO-1 e as medidas do mundo (o ramo do A11 em `orq.medidas`, que só lê o motor).
Uso: python experiments/run_v3_baseline_trivial.py --config experiments/configs/v3_baseline_trivial/<etapa>.json [--processos 4]
"""
from __future__ import annotations

import argparse
import gzip
import io
import json
import platform
import shutil
import statistics
import subprocess
import sys
import tarfile
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import exportar_gabarito_lobos as gl  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402
import run_v2_longe_regular as lr  # noqa: E402
import run_v2_memoria_autobio as ma  # noqa: E402
from bancada.baseline_trivial import BaselineTrivial, LimiaresTriviais  # noqa: E402
from bancada.faixas import FAIXAS_RESERVADAS  # noqa: E402
from bancada.regras_mundo import simular_vida_fisico  # noqa: E402
from digilab.config import CONFIG_PADRAO  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.mundo import DonoComLugar  # noqa: E402
from digilab.temperamento import NEUTRO  # noqa: E402

PLANO = "docs/PLANO_ANALISE_V3_BASELINE_TRIVIAL.md"
PREFIXO = orq.PREFIXO                                                                 # 2.3 (o da C4)
FASE = "baseline_trivial"
ETAPAS = ("calibracao", "validacao")
BASES = {"calibracao": (96101, 96202, 96303, 96404, 96505), "validacao": (97101, 97202, 97303, 97404, 97505)}   # 2.3, PROPOSTAS (BT-3)
K_POR_BASE = {"calibracao": 5, "validacao": 40}                                       # 4.1 e 2.3, PROPOSTOS (BT-4, BT-5)
FAIXA = {e: (b[0], b[-1]) for e, b in BASES.items()}
SAIDA = "artifacts_v3_baseline_trivial"
DIAS, ORCAMENTO_POR_DIA = orq.DIAS, orq.ORCAMENTO_POR_DIA                             # 2.1 (os da C4)
MAX_PROCESSOS = 4                                                                     # V3-D8
DONOS = orq.DONOS
PRIMARIO, LUGARES = ma.PRIMARIO, ma.LUGARES                                           # 2.2: longe_fixo, comedouro, longe
CELULAS = ma.CELULAS                                                                  # as 12 da C4
MOD, TRIV = "REL", "TRIV"                                                             # 2.4: o REL da C4 e a baseline
BRACOS = (MOD, TRIV)
GRADE = {"fome": (0.3, 0.4, 0.5, 0.6, 0.7, 0.8), "energia": (0.1, 0.2, 0.3, 0.4), "tedio": (0.5, 0.7, 0.9, 1.0)}   # 4.2, PROPOSTA (BT-6)
MARGEM = ma.MARGEM                                                                    # 5.2: o 0,032 da C4 (AD9-5), SEM FONTE
EPISODIO = lr.EPISODIO
CHAVES_CONFIG = {"descricao", "plano", "fase", "etapa", "unidades", "dias", "orcamento_por_dia"}


# ================================================================== a trava
def _plano() -> str:
    return (RAIZ / PLANO).read_text(encoding="utf-8")


def exigir_plano_aprovado(plano: str) -> None:
    """a trava da seção 0: a primeira linha de status do plano diz "APROVADO pelo Matheus"; o PROPOSTO recusa a run"""
    status = [x for x in plano.splitlines() if x.startswith("**Status:")]
    if not status or not status[0].startswith("**Status: APROVADO pelo Matheus"):
        raise RuntimeError(f"o plano {PLANO} nao esta APROVADO pelo Matheus no cabecalho (secao 0): {status[:1] or 'sem a linha do status'}")


def exigir_faixa_reservada(etapa: str) -> None:
    if not any((lo, hi) == FAIXA[etapa] for lo, hi, _ in FAIXAS_RESERVADAS):
        raise bv.SementeSemPlano(f"a faixa {FAIXA[etapa]} da {etapa} nao esta em FAIXAS_RESERVADAS (2.3)")


def modo_da_config(cfg: dict) -> str:
    """'fumaca' (as sementes dos testes) ou a etapa, que segue o plano a letra: outra base, outro K, outros dias ou outro orcamento
    falham alto, sementes fora das faixas e dos testes levantam SementeSemPlano, e o plano sem o APROVADO recusa a run"""
    faltam, sobram = (CHAVES_CONFIG - {"descricao"}) - set(cfg), set(cfg) - CHAVES_CONFIG
    if faltam or sobram:
        raise ValueError(f"config: faltam {sorted(faltam)}, sobram {sorted(sobram)}")
    if cfg["fase"] != FASE or cfg["etapa"] not in ETAPAS:
        raise ValueError(f"fase {cfg['fase']!r} / etapa {cfg['etapa']!r}: so {FASE!r} e {ETAPAS}")
    u = cfg["unidades"]
    bases = tuple(u["bases"])
    if u.get("prefixo") != PREFIXO or cfg["orcamento_por_dia"] != ORCAMENTO_POR_DIA or type(u.get("k")) is not int or u["k"] < 1:
        raise ValueError("config fora do plano: o prefixo, o orcamento (2.1) ou o K")
    if bases and set(bases) <= bv.SEMENTES_TESTE:
        if not 1 <= cfg["dias"] <= DIAS:
            raise ValueError(f"fumaca com {cfg['dias']} dias: de 1 a {DIAS}")
        return "fumaca"
    etapa = cfg["etapa"]
    if bases != BASES[etapa]:
        raise bv.SementeSemPlano(f"bases {list(bases)}: so as dos testes (fumaca) ou {list(BASES[etapa])} ({etapa}, 2.3)")
    exigir_faixa_reservada(etapa)
    exigir_plano_aprovado(_plano())
    erros = [f"dias {cfg['dias']} (o plano: {DIAS})"] if cfg["dias"] != DIAS else []
    erros += [f"plano {cfg.get('plano')!r}"] if cfg.get("plano") != PLANO else []
    erros += [f"K por base {u['k']} (o plano: {K_POR_BASE[etapa]})"] if u["k"] != K_POR_BASE[etapa] else []
    if erros:
        raise ValueError(f"a {etapa} segue o plano a letra: {erros}")
    return etapa


# ================================================================== a vida da baseline
def fabricas_triv(limiares: LimiaresTriviais, dono: str, semente: int, dias: int, orcamento_por_dia: int) -> tuple:
    """(a fabrica da politica, a do motor): o motor e o da C4 (o lr.MotorGravaCorpo com o corpo do v11 e o CONFIG_MUNDO_MVP)"""
    cc = orq.bancada(dias, orcamento_por_dia).cfg_corpo_de(bv.EspecVida(dono, gl.BRACO_V11, semente))
    S = cc.escala_receptor                       # a escala dos receptores do corpo (o tedio e a falta da fome do Registro)

    def fp(cfg=None):
        return orq.Registro(BaselineTrivial(limiares, S), S)

    def fm(politica, cfg, s):
        return lr.MotorGravaCorpo(politica, cfg, s, NEUTRO, "brasa", obediencia_desligada=True, cfg_mundo=orq.CM, cfg_corpo=cc)
    return fp, fm


def viver_triv(limiares: LimiaresTriviais, dono: str, lugar: str, semente: int, dias: int, orcamento_por_dia: int):
    fp, fm = fabricas_triv(limiares, dono, semente, dias, orcamento_por_dia)
    registro = fp(CONFIG_PADRAO)
    d = DonoComLugar(criar_dono(dono), lugar, semente, dono, orq.CM)
    motor, _ = simular_vida_fisico(d, registro, semente, dias, orcamento_por_dia * dias, dono, fm)
    return motor, registro, (fp, fm)


def _vida_triv(cfg: dict, limiares: LimiaresTriviais, dono: str, lugar: str, unidade: dict, pasta: str | None) -> dict:
    """uma vida da baseline: vivida, rejogada do log (G1; do disco quando a pasta grava as vidas), conferida (T-CENARIO-1) e medida"""
    c0, p0 = time.process_time(), time.perf_counter()
    motor, registro, fab = viver_triv(limiares, dono, lugar, unidade["semente"], cfg["dias"], cfg["orcamento_por_dia"])
    texto = motor.log.para_jsonl()
    if pasta is not None:
        arquivo = Path(pasta) / "vidas" / TRIV / f"{dono}_{lugar}_{unidade['semente']}.jsonl"
        arquivo.parent.mkdir(parents=True, exist_ok=True)
        arquivo.write_text(texto, encoding="utf-8", newline="\n")
        texto = arquivo.read_text(encoding="utf-8")
    orq.conferir_replay(motor, fab, unidade["semente"], texto)
    orq.conferir_cenario(motor, registro)
    med = orq.medidas(motor, registro, "A11", cfg["dias"], True)     # o ramo do A11: so as medidas do mundo (o motor e o registro)
    return {"vida": f"{TRIV}|{dono}|{lugar}|{unidade['semente']}", "braco": TRIV, "dono": dono, "lugar": lugar,
            "semente": unidade["semente"], "base": unidade["base"], "k": unidade["k"], **med,
            "corpo": lr.medidas_do_corpo(motor, registro, cfg["dias"]),
            "custo": {"vida_cpu": time.process_time() - c0, "vida_parede": time.perf_counter() - p0}}


# ================================================================== as tarefas
def tarefa_calibracao(cfg: dict, ponto: tuple, unidade: dict) -> list[dict]:
    lim = LimiaresTriviais(*ponto)
    return [{**_vida_triv(cfg, lim, dono, PRIMARIO, unidade, None), "ponto": list(ponto)} for dono in DONOS]


def tarefa_validacao(cfg: dict, limiares: LimiaresTriviais, unidade: dict, pasta: str) -> list[dict]:
    out = [ma._vida(cfg, MOD, dono, lugar, unidade, pasta) for dono, lugar in CELULAS]      # a vida da C4, sem mudanca
    return out + [_vida_triv(cfg, limiares, dono, lugar, unidade, pasta) for dono, lugar in CELULAS]


def pontos_da_grade() -> list[tuple]:
    return [(x, y, z) for x in GRADE["fome"] for y in GRADE["energia"] for z in GRADE["tedio"]]


# ================================================================== a analise (funcoes puras)
def _celulas(lugar: str) -> tuple:
    return tuple((d, lugar) for d in DONOS)


def escolher_ponto(registros: list[dict]) -> dict:
    """4.3: em cada ponto, a media sobre as unidades da taxa por episodio media nas 4 celulas do longe_fixo; vence a maior; empate
    exato, o menor (X, Y, Z) na ordem lexicografica. Ponto sem unidade com valor falha alto."""
    por_ponto = {}
    for p in pontos_da_grade():
        regs = [r for r in registros if tuple(r["ponto"]) == p]
        niv = orq.por_unidade(regs, TRIV, None, EPISODIO, _celulas(PRIMARIO))
        if not niv:
            raise RuntimeError(f"ponto {p}: nenhuma unidade com episodio de fome")
        por_ponto[p] = {"n": len(niv), "media": statistics.fmean(niv.values())}
    melhor = min(por_ponto, key=lambda p: (-por_ponto[p]["media"], p))
    return {"pontos": [{"fome": p[0], "energia": p[1], "tedio": p[2], **v} for p, v in sorted(por_ponto.items())],
            "escolhido": {"fome": melhor[0], "energia": melhor[1], "tedio": melhor[2], **por_ponto[melhor]}}


def classe(ic: dict) -> dict:
    return lr.classe(ic, MARGEM)


def leitura(prim: dict) -> dict:
    """5.3, escrita antes: a classe do IC95 pelo t (A6.6, margem 0,032) e, no "> 0", se o IC exclui o efeito trivial (inferior >= margem)"""
    c, lo = prim["classe"]["classe"], prim["ic95"]["ic_inferior"]
    if c == "> 0":
        texto = ("o modular vence a baseline, e o IC95 exclui o efeito trivial" if lo >= MARGEM else
                 "o modular vence a baseline, mas o IC95 nao exclui um efeito trivial (inferior < margem)")
        return {"classe": c, "exclui_trivial": lo >= MARGEM, "texto": texto}
    texto = {"≈ 0": "empate: a diferenca fica dentro da margem", "< 0": "a baseline vence o modular",
             "indeterminado": "indeterminado: o IC95 cruza a margem"}[c]
    return {"classe": c, "exclui_trivial": False, "texto": texto}


def contraste_lugar(registros: list[dict], lugar: str, boot: dict) -> dict:
    difs = orq.por_unidade(registros, MOD, TRIV, EPISODIO, _celulas(lugar))
    c = orq.contraste_t(difs, boot)
    ic = {"ic_inferior": c["ic95"]["ic_inferior"], "ic_superior": c["ic95"]["ic_superior"], "motivo": c["motivo"]}
    dp = statistics.stdev(difs.values()) if len(difs) > 1 else None
    return {"contraste": f"{MOD} - {TRIV}, a taxa de fechamento por episodio, nas 4 celulas do {lugar}", **c, "classe": classe(ic),
            "margem": MARGEM, "margem_efetiva": lr.margem_efetiva(dp, c["n"])}


def _nivel(registros: list[dict], braco: str, medida, lugar: str) -> dict:
    v = orq.por_unidade(registros, braco, None, medida, _celulas(lugar))
    return {"n": len(v), "media": statistics.fmean(v.values()) if v else None}


def analisar(registros: list[dict], boot: dict = orq.BOOTSTRAP) -> dict:
    prim = contraste_lugar(registros, PRIMARIO, boot)
    medidas = {"episodio": EPISODIO, "privacao": lambda r: r["privacao"], "exaustao": lambda r: r["exaustao"], "d_fe": lambda r: r["d_fe"],
               "episodios_n": lambda r: r["episodios_fome"]["n"]}
    acoes = {b: {lu: dict(sorted(_somar_acoes([r for r in registros if r["braco"] == b and r["lugar"] == lu]).items())) for lu in LUGARES}
             for b in BRACOS}
    return {"primario": prim, "leitura": leitura(prim),
            "secundarias": {lu: contraste_lugar(registros, lu, boot) for lu in LUGARES if lu != PRIMARIO},
            "descritivo": {"niveis": {m: {b: {lu: _nivel(registros, b, f, lu) for lu in LUGARES} for b in BRACOS} for m, f in medidas.items()},
                           "acoes": acoes},
            "nao_demonstra": ["que a baseline e a melhor politica trivial possivel (so a grade da secao 4)",
                              "o resultado fora das 12 celulas da C4, do mundo do MVP e dos 14 dias",
                              "algo sobre o jogo web (as vidas sao do Python)", "que o modular e pior ou melhor em outra medida"]}


def _somar_acoes(regs: list[dict]) -> dict:
    out: dict = {}
    for r in regs:
        for a, n in r["acoes"].items():
            out[a] = out.get(a, 0) + n
    return out


# ================================================================== os artefatos
def tar_deterministico(pasta_vidas: Path, destino: Path) -> None:
    """o vidas.tar.gz igual byte a byte para as mesmas vidas: nomes em ordem, mtime 0, dono 0, modo 0644, o gzip com mtime 0"""
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w", format=tarfile.PAX_FORMAT) as tar:
        for f in sorted(p for p in pasta_vidas.rglob("*") if p.is_file()):
            dados = f.read_bytes()
            info = tarfile.TarInfo(f.relative_to(pasta_vidas.parent).as_posix())
            info.size, info.mtime, info.mode, info.uid, info.gid, info.uname, info.gname = len(dados), 0, 0o644, 0, 0, "", ""
            tar.addfile(info, io.BytesIO(dados))
    with open(destino, "wb") as saida, gzip.GzipFile(filename="", mode="wb", fileobj=saida, mtime=0, compresslevel=9) as gz:
        gz.write(buf.getvalue())


def _versao_node() -> str | None:
    """a run nao usa o Node (as vidas sao do Python); a versao fica no meta como o pedido manda, ou None sem o Node"""
    try:
        return subprocess.run(["node", "--version"], capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def _meta_base(cfg: dict, modo: str, caminho_config: Path | None, processos: int, unidades: list[dict]) -> dict:
    rc = orq.rc
    return {"modo": modo, "fase": FASE, "etapa": cfg["etapa"], "plano": PLANO, "plano_sha256": rc._sha_arquivo(RAIZ / PLANO), "config": cfg,
            "config_arquivo": None if caminho_config is None else rc._relativo(caminho_config),
            "config_sha256": None if caminho_config is None else rc._sha_arquivo(caminho_config),
            "comando": " ".join(["python", *sys.argv]) if sys.argv and sys.argv[0] else None,
            "python": platform.python_version(), "node": _versao_node(),
            "orquestrador_sha256": rc._sha_arquivo(Path(__file__)), "baseline_sha256": rc._sha_arquivo(RAIZ / "experiments" / "bancada" / "baseline_trivial.py"),
            "prototipo_sha256": rc._sha_arquivo(Path(orq.__file__)), "c4_sha256": rc._sha_arquivo(Path(ma.__file__)),
            "git_head": rc._git("rev-parse", "HEAD"), "git_limpo": rc._git("status", "--porcelain") == "", "processos": processos,
            "unidades": unidades, "inicio": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())}


def limiares_da_calibracao(pasta_cal: Path, modo: str) -> tuple[LimiaresTriviais, dict]:
    """o ponto escolhido, lido do resultado.json da calibracao, com o sha256 conferido contra o meta dela; a validacao so aceita a
    calibracao de verdade, e a fumaca so a calibracao de fumaca (falha alto se nao confere)"""
    meta = json.loads((pasta_cal / "meta.json").read_text(encoding="utf-8"))
    sha = bv._sha(pasta_cal / "resultado.json")
    esperado = "fumaca" if modo == "fumaca" else "calibracao"
    if (meta.get("artefatos_sha256", {}).get("resultado.json") != sha or meta.get("etapa") != "calibracao"
            or meta.get("modo") != esperado):
        raise RuntimeError(f"o resultado da calibracao em {pasta_cal} nao confere com o meta dela (ou nao e da calibracao)")
    e = json.loads((pasta_cal / "resultado.json").read_text(encoding="utf-8"))["escolhido"]
    return LimiaresTriviais(e["fome"], e["energia"], e["tedio"]), {"pasta": orq.rc._relativo(pasta_cal), "resultado_sha256": sha,
                                                                   "git_head": meta["git_head"], "escolhido": e}


def rodar(cfg: dict, pasta: Path, processos: int, caminho_config: Path | None = None, pasta_cal: Path | None = None) -> dict:
    if processos > MAX_PROCESSOS:
        raise ValueError(f"no maximo {MAX_PROCESSOS} processos (V3-D8)")
    modo = modo_da_config(cfg)
    if pasta.exists():
        raise FileExistsError(f"{pasta} ja existe: a run se recusa a gravar por cima (uma vez; secao 6)")
    unidades = bv.unidades_derivadas(cfg["unidades"]["bases"], int(cfg["unidades"]["k"]), PREFIXO)
    calibrando = cfg["etapa"] == "calibracao"
    origem = None
    if not calibrando:
        if pasta_cal is None:
            raise ValueError("a validacao precisa da pasta da calibracao (os limiares saem dela)")
        limiares, origem = limiares_da_calibracao(pasta_cal, modo)
    pasta.mkdir(parents=True)
    inicio = time.time()
    meta = _meta_base(cfg, modo, caminho_config, processos, unidades)
    meta.update({"grade": GRADE, "celulas": [[d, PRIMARIO] for d in DONOS], "bracos": [TRIV]} if calibrando else
                {"celulas": [list(c) for c in CELULAS], "bracos": {MOD: orq.SUBCHAVES_C4[MOD], TRIV: origem["escolhido"]},
                 "calibracao": origem})
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    t0 = time.perf_counter()
    if calibrando:
        tarefas = [(tarefa_calibracao, (cfg, p, u)) for p in pontos_da_grade() for u in unidades]
        esperadas = len(pontos_da_grade()) * len(unidades) * len(DONOS)
    else:
        tarefas = [(tarefa_validacao, (cfg, limiares, u, str(pasta))) for u in unidades]
        esperadas = len(unidades) * len(BRACOS) * len(CELULAS)
    registros = [r for s in orq.rc._executar(tarefas, processos) for r in s]
    meta["vidas_parede_s"] = time.perf_counter() - t0
    if len(registros) != esperadas:
        raise RuntimeError(f"{len(registros)} vidas, eram {esperadas}")
    chave = (lambda r: (tuple(r["ponto"]), r["vida"])) if calibrando else (lambda r: r["vida"])
    bv._gravar(pasta / "medidas.json", bv._dump([r for r in sorted(registros, key=chave)]))
    lidos = json.loads((pasta / "medidas.json").read_text(encoding="utf-8"))       # a analise sai do artefato gravado
    corpo = escolher_ponto(lidos) if calibrando else analisar(lidos)
    resultado = {"modo": modo, "fase": FASE, "etapa": cfg["etapa"], "plano": PLANO, "unidades": len(unidades), "vidas": len(lidos), **corpo}
    bv._gravar(pasta / "resultado.json", bv._dump(resultado))
    nomes = ["medidas.json", "resultado.json"]
    if (pasta / "medidas.json").stat().st_size > 100 * 2**20:                          # o pedido: o .gz so acima de 100 MB
        with open(pasta / "medidas.json", "rb") as f, open(pasta / "medidas.json.gz", "wb") as s, \
                gzip.GzipFile(filename="", mode="wb", fileobj=s, mtime=0, compresslevel=9) as gz:
            shutil.copyfileobj(f, gz)
        nomes.append("medidas.json.gz")
    if (pasta / "vidas").exists():
        tar_deterministico(pasta / "vidas", pasta / "vidas.tar.gz")
        nomes.append("vidas.tar.gz")
    meta["fim"] = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
    meta["duracao_s"] = time.time() - inicio
    meta["artefatos_sha256"] = {n: bv._sha(pasta / n) for n in nomes}
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    return {"meta": meta, "registros": registros, "resultado": resultado}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--config", required=True)
    ap.add_argument("--saida", default=None)
    ap.add_argument("--calibracao", default=None, help="a pasta da calibracao (so na validacao); padrao: a da run")
    ap.add_argument("--processos", type=int, default=1)
    a = ap.parse_args()
    caminho = Path(a.config)
    cfg = json.loads(caminho.read_text(encoding="utf-8"))
    modo = modo_da_config(cfg)
    if modo == "fumaca" and a.saida is None:
        raise SystemExit(f"a fumaca precisa de --saida (fora de {SAIDA}/)")
    saida = Path(a.saida) if a.saida else RAIZ / SAIDA / cfg["etapa"]
    cal = Path(a.calibracao) if a.calibracao else (None if cfg["etapa"] == "calibracao" else RAIZ / SAIDA / "calibracao")
    r = rodar(cfg, saida, a.processos, caminho, cal)["resultado"]
    print(json.dumps({k: r[k] for k in r if k in ("modo", "etapa", "vidas", "escolhido", "primario", "leitura", "secundarias")}, indent=1,
                     ensure_ascii=True, default=str)[:4000])


if __name__ == "__main__":
    main()
