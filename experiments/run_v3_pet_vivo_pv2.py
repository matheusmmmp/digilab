"""PET_VIVO, PV-2: a run unica da quimiotaxia pela variacao do cheiro (docs/PLANO_ANALISE_V3_PET_VIVO_PV2.md, com os adendos 1 e 2;
docs/TAREFA_V3_PET_VIVO.md).

Pergunta (a secao 2 do plano): um pet que so sente o cheiro, e vira quando ele cai, acha a comida longe tao bem quanto o pet que recebe a
direcao, e melhor que um pet que vira na mesma taxa em hora qualquer? E a fome no ganho do cheiro deixa a escolha mais sensivel ao corpo?

As vidas (a secao 4): o REL da C4 (`pv2.viver`), nos 6 bracos (HOJE, OLF-0, OLF-DC, OLF-DCV, OLF-PLA, OLF-G), nas 12 celulas da C4 (os 4
donos x comedouro, longe e `longe_fixo`), 5 bases x K = 40 unidades, 14 dias: 14 400 vidas, uma vez. Cada vida grava o log, confere o G1 do
replay e o T-CENARIO-1. O contrafactual da SE-C (a A-4 da 0b, `auditoria_pet_vivo.Leitor`) roda nos k de 0 a 7 de cada base, nos bracos
OLF-0, OLF-DCV e OLF-G (1 440 vidas); o G1 do replay, sem o leitor, confere que ele nao muda a vida.

A checagem do v38 (a INT-8; o adendo 2, A2.3): descritiva, sem gate. O HOJE, o OLF-0 e o OLF-DCV com as chaves do pet do jogo que o Python
tem (`pv2.fabricas(..., v38=True)`), nos k de 0 a 7, no `longe` e no `longe_fixo`: 960 vidas a mais.

A analise (as secoes 6 e 7, escritas antes): G-PV2-LONGE, G-PV2-HORA, G-FORR, G-ESTADO e G-ESTADO-NI, pareados por unidade (base, semente),
com a media dos donos e o IC95 pelo t, como na C4; a regra de leitura da secao 7. O G-UNIDADES e conferencia nas sementes dos testes
(tests/test_pv2_codigo.py), antes da run. Ao lado, os descritivos: a H-VARR, a H-CUSTO, a hora da virada, o achado pelo cheiro, a RV.

A trava: a run de verdade recusa rodar sem o "APROVADO pelo Matheus" no adendo 2, sem a faixa em FAIXAS_RESERVADAS e com a pasta de saida
ja existente. A fumaca usa as sementes dos testes.
Uso: python experiments/run_v3_pet_vivo_pv2.py --config experiments/configs/v3_pet_vivo/pv2.json --processos 4
"""
from __future__ import annotations

import argparse
import gzip
import json
import platform
import shutil
import sys
import time
from dataclasses import asdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import auditoria_pet_vivo as ap  # noqa: E402
import bancada_v2 as bv  # noqa: E402
import exportar_gabarito_digibrain_modular as gab  # noqa: E402
import pv2  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402
import run_v2_longe_regular as lr  # noqa: E402
import run_v2_memoria_autobio as ma  # noqa: E402
import run_v3_valuation as V  # noqa: E402
from bancada.faixas import FAIXAS_RESERVADAS  # noqa: E402
from digilab import metrics as met  # noqa: E402
from digilab.config import CONFIG_DIGIBRAIN_INATOS, CONFIG_PV2  # noqa: E402
from digilab.metrics import medidas_pv2  # noqa: E402

PLANO = "docs/PLANO_ANALISE_V3_PET_VIVO_PV2.md"
STATUS_ADENDO_2 = "**Status do adendo 2: APROVADO pelo Matheus"
FASE = "pv2"
PREFIXO = orq.PREFIXO
BASES = (83101, 83202, 83303, 83404, 83505)                   # secao 4; a faixa pedida ao coordenador em 2026-11-17 (o adendo 2, A2.1)
FAIXA = (83101, 83505)
K_POR_BASE = 40                                               # PV2-6
DIAS, ORCAMENTO_POR_DIA = V.DIAS, V.ORCAMENTO_POR_DIA         # 14 dias, 16 (os da C4)
SAIDA = "artifacts_v3_pet_vivo/pv2/run"
MAX_PROCESSOS = 4                                             # V3-D8
CELULAS = ma.CELULAS                                          # as 12 da C4
LUGARES = ("comedouro", "longe_fixo", "longe")
LONGES = ("longe", "longe_fixo")
BRACOS = pv2.BRACOS                                           # HOJE, OLF-0, OLF-DC, OLF-DCV, OLF-PLA, OLF-G
BRACOS_CF = ("OLF-0", "OLF-DCV", "OLF-G")                     # secao 4: o contrafactual da SE-C
K_SUBAMOSTRA = ap.K_SUBAMOSTRA                                # os k de 0 a 7 (PV-0-5)
BRACOS_V38 = ("HOJE", "OLF-0", "OLF-DCV")                     # o adendo 2, A2.3
DELTA_F = 0.018                                               # secao 6: a margem da G-COMEDOURO-AN
DELTA_E = {"comedouro": 0.0029, "longe_fixo": 0.0085, "longe": 0.0042}   # PV2-7, secao 6
EPISODIO = ma.EPISODIO
CHAVES_CONFIG = lr.CHAVES_CONFIG
S = CONFIG_DIGIBRAIN_INATOS.escala


def com_contrafactual(braco: str, unidade: dict) -> bool:
    return braco in BRACOS_CF and unidade["k"] < K_SUBAMOSTRA


# ================================================================== a vida
def _vida(cfg: dict, braco: str, dono: str, lugar: str, unidade: dict, pasta: str, v38: bool = False) -> dict:
    c0, p0 = time.process_time(), time.perf_counter()
    semente = unidade["semente"]
    cf = not v38 and com_contrafactual(braco, unidade)
    leitores = []
    montar = (lambda c: leitores.append(ap.Leitor(c, ap.comum_do_pacote("digilab"), True))) if cf else None
    try:
        motor, registro, fab = pv2.viver(braco, dono, lugar, semente, cfg["dias"], cfg["orcamento_por_dia"], v38=v38, ao_montar=montar)
    finally:
        for x in leitores:
            x.soltar()
    grupo = "v38" if v38 else "run"
    arquivo = Path(pasta) / "vidas" / grupo / braco / f"{dono}_{lugar}_{semente}.jsonl"
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    arquivo.write_text(motor.log.para_jsonl(), encoding="utf-8", newline="\n")
    orq.conferir_replay(motor, fab, semente, arquivo.read_text(encoding="utf-8"))   # sem o leitor: confere que ele nao mudou a vida
    orq.conferir_cenario(motor, registro)
    c = orq.cerebro_de(registro)
    esperado = pv2.config_pv2(braco)
    if c.pv2 != esperado:
        raise RuntimeError(f"{braco}: a ConfigPV2 do cerebro nao e a do braco")
    med = orq.medidas(motor, registro, "REL", cfg["dias"], True)
    out = {"vida": f"{grupo}|{braco}|{dono}|{lugar}|{semente}", "grupo": grupo, "braco": braco, "dono": dono, "lugar": lugar,
           "semente": semente, "base": unidade["base"], "k": unidade["k"], **med,
           "pv2": medidas_pv2(c.motivos, motor.consumos_mundo, braco != "HOJE", c.S), "contrafactual": cf}
    if cf:
        red = ap.reduzir(met, ap.comum_do_pacote("digilab"), c.m.arb, leitores[0].registros, [gab.paraj(x) for x in c.motivos], True)
        out["se"] = {"canais": red["canais"], "A4": red["A4"], "RV": red["RV"], "entropia_media": red["A2"]["entropia_media"],
                     "t_contrafactual_s": leitores[0].t_cf}
    out["custo"] = {"vida_cpu": time.process_time() - c0, "vida_parede": time.perf_counter() - p0}
    return out


def tarefa(cfg: dict, unidade: dict, pasta: str) -> list[dict]:
    out = [_vida(cfg, b, dono, lugar, unidade, pasta) for b in BRACOS for dono, lugar in CELULAS]
    if unidade["k"] < K_SUBAMOSTRA:
        out += [_vida(cfg, b, dono, lugar, unidade, pasta, v38=True) for b in BRACOS_V38 for dono, lugar in CELULAS if lugar in LONGES]
    return out


# ================================================================== a analise (secoes 6 e 7, escritas antes)
def _celulas(lugar: str | None) -> tuple:
    return CELULAS if lugar is None else tuple(c for c in CELULAS if c[1] == lugar)


def _ic(difs: dict) -> dict:
    ic = met.ic_t([v for _, v in sorted(difs.items())])
    return {"n": ic["n"], "media": ic["media"], "dp": ic["dp"], "ic_inferior": ic["ic_inferior"], "ic_superior": ic["ic_superior"],
            "motivo": ic.get("motivo")}


def contraste(registros: list[dict], a: str, b: str | None, medida, lugar: str | None) -> dict:
    """a - b por unidade (a media das celulas do lugar), com o IC95 pelo t (b None: o nivel de a)"""
    return _ic(orq.por_unidade(registros, a, b, medida, _celulas(lugar)))


def alivio_do_grupo(vidas: list[dict]) -> dict:
    """A_r do grupo (braco, lugar), fixado nas vidas dele antes da medida (PV-0-7): a tabela do alivio sobre os canais das vidas"""
    canais: dict = {}
    for v in vidas:
        for chave, x in v["se"]["canais"].items():
            bh, r = chave.split("|")
            canais.setdefault((bh, r), []).append(x)
    tab = met.tabela_do_alivio(canais)
    return {r: [bh for bh in ap.COMPORTAMENTOS if tab.get((bh, r), {}).get("alivia")] for r in sorted({r for _, r in canais}) if r != "susto"}


def se_c_por_vida(registros: list[dict]) -> dict:
    """{vida: a SE-C dela}, com a A_r do (braco, lugar) dela; so as vidas com o contrafactual"""
    out = {}
    for b in BRACOS_CF:
        for lugar in LUGARES:
            vidas = [v for v in registros if v["grupo"] == "run" and v["braco"] == b and v["lugar"] == lugar and v["contrafactual"]]
            if not vidas:
                continue
            A = alivio_do_grupo(vidas)
            for v in vidas:
                vals = {}
                for r, Ar in A.items():
                    s = v["se"]["A4"].get(r, {}).get("todo")
                    vals[r] = None if not s or not s["n"] else met.sensibilidade_coerente(s["movido_para"], Ar, s["n"])
                out[v["vida"]] = met.se_c(vals)
    return out


def _por_unidade_se(registros: list[dict], se: dict, a: str, b: str | None, lugar: str) -> dict:
    """{(base, semente): a media dos donos da SE-C de a menos a de b} (so as unidades da subamostra)"""
    def nivel(braco):
        por: dict = {}
        for v in registros:
            if v["grupo"] == "run" and v["braco"] == braco and v["lugar"] == lugar and v["vida"] in se and se[v["vida"]] is not None:
                por.setdefault((v["base"], v["semente"]), []).append(se[v["vida"]])
        return {u: sum(xs) / len(xs) for u, xs in por.items()}
    na = nivel(a)
    if b is None:
        return na
    nb = nivel(b)
    return {u: na[u] - nb[u] for u in sorted(set(na) & set(nb))}


def gates(registros: list[dict]) -> dict:
    run = [r for r in registros if r["grupo"] == "run"]
    se = se_c_por_vida(run)
    longe = {lg: contraste(run, "OLF-DCV", "OLF-0", EPISODIO, lg) for lg in LONGES}
    hora = {lg: contraste(run, "OLF-DCV", "OLF-PLA", EPISODIO, lg) for lg in LONGES}
    forr = {"OLF-DCV - OLF-0": contraste(run, "OLF-DCV", "OLF-0", EPISODIO, "comedouro"),
            "OLF-G - OLF-DCV": contraste(run, "OLF-G", "OLF-DCV", EPISODIO, "comedouro")}
    estado = {lg: _ic(_por_unidade_se(run, se, "OLF-G", "OLF-DCV", lg)) for lg in LUGARES}
    estado_ni = {lg: _ic(_por_unidade_se(run, se, "OLF-DCV", "OLF-0", lg)) for lg in LUGARES}

    def acima(x, corte):
        return x["ic_inferior"] is not None and x["ic_inferior"] > corte

    return {
        "G-PV2-LONGE": {"contraste": "OLF-DCV - OLF-0, a taxa por episodio", "por_lugar": longe,
                        "passa": all(acima(x, 0) for x in longe.values())},
        "G-PV2-HORA": {"contraste": "OLF-DCV - OLF-PLA, a taxa por episodio", "por_lugar": hora,
                       "passa": all(acima(x, 0) for x in hora.values())},
        "G-FORR": {"contraste": "no comedouro, o IC nao fica abaixo de -delta_F", "delta_F": DELTA_F, "por_contraste": forr,
                   "passa": all(x["ic_inferior"] is not None and x["ic_inferior"] >= -DELTA_F for x in forr.values())},
        "G-ESTADO": {"contraste": "OLF-G - OLF-DCV, a SE-C", "delta_E": DELTA_E, "por_lugar": estado,
                     "passa": all(acima(estado[lg], DELTA_E[lg]) for lg in LUGARES)},
        "G-ESTADO-NI": {"contraste": "OLF-DCV - OLF-0, a SE-C", "delta_E": DELTA_E, "por_lugar": estado_ni,
                        "passa": all(acima(estado_ni[lg], -DELTA_E[lg]) for lg in LUGARES)},
        "G-UNIDADES": {"onde": "tests/test_pv2_codigo.py, nas sementes dos testes, antes da run (secao 6)"},
    }


def leitura(g: dict) -> dict:
    """a regra da secao 7, na ordem: o custo perto de casa primeiro (vale qualquer que seja o resto); o OLF-G sai separado"""
    lon, hor, forr = g["G-PV2-LONGE"]["passa"], g["G-PV2-HORA"]["passa"], g["G-FORR"]["passa"]
    if not forr:
        q = ("custa perto de casa", "nao levar, qualquer que seja o resto")
    elif not lon:
        q = ("sem ganho sobre a tropotaxia", "a pirueta nao soma as duas narinas; o OLF-0 fica como a forma sem oraculo, se o H-CUSTO for pequeno")
    elif hor:
        q = ("a quimiotaxia funciona e gira na hora certa", "levar o OLF-DCV ao cerebro padrao e a web, com a paridade, por tarefa propria")
    else:
        q = ("ajuda, mas pelo numero de viradas", "o placebo explica o ganho; nao levar a pirueta; rever a varredura")
    return {"quimiotaxia": {"leitura": q[0], "sugere": q[1]},
            "olf_g": {"G-ESTADO": g["G-ESTADO"]["passa"], "G-FORR": g["G-FORR"]["passa"],
                      "leitura": "o ganho entra" if g["G-ESTADO"]["passa"] and g["G-FORR"]["passa"] else "o ganho nao entra"}}


DESC_PV2 = {"achou_pelo_cheiro": lambda r: r["pv2"]["achou_pelo_cheiro"],
            "decisoes_ate_comer": lambda r: r["pv2"]["decisoes_ate_comer"],
            "hora_da_virada": lambda r: r["pv2"].get("hora_da_virada"),
            "taxa_viradas": lambda r: r["pv2"].get("taxa_viradas"),
            "episodio": EPISODIO}


def _sem_motivo(x: dict) -> dict:
    return {k: v for k, v in x.items() if k != "motivo"}


def descritivo(registros: list[dict]) -> dict:
    run = [r for r in registros if r["grupo"] == "run"]
    se = se_c_por_vida(run)
    out = {"niveis": {lg: {b: {n: _sem_motivo(contraste(run, b, None, f, lg)) for n, f in DESC_PV2.items()} for b in BRACOS}
                      for lg in LUGARES},
           "H-VARR": {lg: _sem_motivo(contraste(run, "OLF-DCV", "OLF-DC", EPISODIO, lg)) for lg in LONGES},
           "H-CUSTO": {lg: {b: _sem_motivo(contraste(run, "HOJE", b, EPISODIO, lg)) for b in BRACOS if b != "HOJE"} for lg in LUGARES},
           "SE_C": {lg: {b: _sem_motivo(_ic(_por_unidade_se(run, se, b, None, lg))) for b in BRACOS_CF} for lg in LUGARES},
           "RV": {lg: {b: _sem_motivo(_ic(_rv(run, b, lg))) for b in BRACOS_CF} for lg in LUGARES}}
    v38 = [r for r in registros if r["grupo"] == "v38"]
    if v38:
        out["v38"] = {"nota": "descritivo, sem gate (INT-8; o adendo 2, A2.3); o olhar fica de fora",
                      "niveis": {lg: {b: _sem_motivo(contraste(v38, b, None, EPISODIO, lg)) for b in BRACOS_V38} for lg in LONGES},
                      "OLF-DCV - OLF-0": {lg: _sem_motivo(contraste(v38, "OLF-DCV", "OLF-0", EPISODIO, lg)) for lg in LONGES},
                      "HOJE - OLF-DCV": {lg: _sem_motivo(contraste(v38, "HOJE", "OLF-DCV", EPISODIO, lg)) for lg in LONGES}}
    return out


def _rv(run: list[dict], braco: str, lugar: str) -> dict:
    por: dict = {}
    for v in run:
        if v["braco"] == braco and v["lugar"] == lugar and v["contrafactual"] and v["se"]["RV"]["media"] is not None:
            por.setdefault((v["base"], v["semente"]), []).append(v["se"]["RV"]["media"])
    return {u: sum(xs) / len(xs) for u, xs in por.items()}


def analisar(registros: list[dict]) -> dict:
    g = gates(registros)
    return {"gates": g, "leitura": leitura(g), "descritivo": descritivo(registros),
            "nao_demonstra": ["nada sobre o jogo web (a checagem do v38 e so descritiva, e sem o olhar)",
                              "nada fora dos 14 dias, do mundo do MVP e dos lugares da C4", "nada sobre o freio da saciedade (a lacuna 3)",
                              "nada sobre outro L da pirueta, outro w0_dc ou outro G0 alem dos do adendo 1"]}


# ================================================================== a trava e a run
def exigir_aprovado(plano: str) -> None:
    linhas = [x for x in plano.splitlines() if x.startswith("**Status do adendo 2:")]
    if not linhas or not linhas[0].startswith(STATUS_ADENDO_2):
        raise RuntimeError(f"o adendo 2 de {PLANO} nao esta APROVADO pelo Matheus: {linhas[:1] or 'sem a linha do status'}")


def modo_da_config(cfg: dict) -> str:
    faltam, sobram = (CHAVES_CONFIG - {"descricao"}) - set(cfg), set(cfg) - CHAVES_CONFIG
    if faltam or sobram:
        raise ValueError(f"config: faltam {sorted(faltam)}, sobram {sorted(sobram)}")
    if cfg["fase"] != FASE:
        raise ValueError(f"fase {cfg['fase']!r}: so {FASE!r}")
    u = cfg["unidades"]
    bases = tuple(u["bases"])
    if u.get("prefixo") != PREFIXO or cfg["orcamento_por_dia"] != ORCAMENTO_POR_DIA or type(u.get("k")) is not int or u["k"] < 1:
        raise ValueError("config fora do plano: o prefixo, o orcamento ou o K (secao 4)")
    if bases and set(bases) <= bv.SEMENTES_TESTE:
        if not 1 <= cfg["dias"] <= DIAS:
            raise ValueError(f"fumaca com {cfg['dias']} dias: de 1 a {DIAS}")
        return "fumaca"
    if bases != BASES:
        raise bv.SementeSemPlano(f"bases {list(bases)}: so as dos testes (fumaca) ou {list(BASES)} (secao 4)")
    if not any((lo, hi) == FAIXA for lo, hi, _ in FAIXAS_RESERVADAS):
        raise bv.SementeSemPlano(f"a faixa {FAIXA} nao esta em FAIXAS_RESERVADAS (secao 4)")
    exigir_aprovado((RAIZ / PLANO).read_text(encoding="utf-8"))
    erros = [m for m, ok in ((f"dias {cfg['dias']} (o plano: {DIAS})", cfg["dias"] == DIAS), (f"plano {cfg.get('plano')!r}", cfg.get("plano") == PLANO),
                             (f"K por base {u['k']} (o plano: {K_POR_BASE})", u["k"] == K_POR_BASE)) if not ok]
    if erros:
        raise ValueError(f"a run segue o plano a letra: {erros}")
    return FASE


def esperadas(n_unidades: int, n_sub: int) -> int:
    return n_unidades * len(BRACOS) * len(CELULAS) + n_sub * len(BRACOS_V38) * len(_celulas("longe")) * len(LONGES)


def rodar(cfg: dict, pasta: Path, processos: int, caminho_config: Path | None = None) -> dict:
    if processos > MAX_PROCESSOS:
        raise ValueError(f"no maximo {MAX_PROCESSOS} processos (V3-D8)")
    modo = modo_da_config(cfg)
    if pasta.exists():
        raise FileExistsError(f"{pasta} ja existe: a run se recusa a gravar por cima (uma vez)")
    unidades = bv.unidades_derivadas(cfg["unidades"]["bases"], int(cfg["unidades"]["k"]), PREFIXO)
    pasta.mkdir(parents=True)
    inicio = time.time()
    rc = orq.rc
    meta = {"modo": modo, "fase": FASE, "plano": PLANO, "plano_sha256": rc._sha_arquivo(RAIZ / PLANO), "config": cfg,
            "config_arquivo": None if caminho_config is None else rc._relativo(caminho_config),
            "config_sha256": None if caminho_config is None else rc._sha_arquivo(caminho_config),
            "comando": " ".join(["python", *sys.argv]) if sys.argv and sys.argv[0] else None, "python": platform.python_version(),
            "orquestrador_sha256": rc._sha_arquivo(Path(__file__)), "pv2_sha256": rc._sha_arquivo(Path(pv2.__file__)),
            "auditoria_0b_sha256": rc._sha_arquivo(Path(ap.__file__)), "prototipo_sha256": rc._sha_arquivo(Path(orq.__file__)),
            "git_head": rc._git("rev-parse", "HEAD"), "git_limpo": rc._git("status", "--porcelain") == "", "processos": processos,
            "unidades": unidades, "celulas": [list(c) for c in CELULAS], "bracos": list(BRACOS), "bracos_contrafactual": list(BRACOS_CF),
            "bracos_v38": list(BRACOS_V38), "k_subamostra": K_SUBAMOSTRA, "config_pv2": asdict(CONFIG_PV2), "faixa": list(FAIXA),
            "sha256": {n: rc._sha_arquivo(RAIZ / "digilab" / n) for n in ("config.py", "engine.py", "metrics.py", "mundo.py", "corpo.py")}
            | {f"digibrain/{p.name}": rc._sha_arquivo(p) for p in sorted((RAIZ / "digilab" / "digibrain").glob("*.py"))},
            "inicio": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(inicio))}
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    t0 = time.perf_counter()
    registros = [r for s in rc._executar([(tarefa, (cfg, u, str(pasta))) for u in unidades], processos) for r in s]
    meta["vidas_parede_s"] = time.perf_counter() - t0
    n_sub = sum(1 for u in unidades if u["k"] < K_SUBAMOSTRA)
    if len(registros) != esperadas(len(unidades), n_sub):
        raise RuntimeError(f"{len(registros)} vidas, eram {esperadas(len(unidades), n_sub)}")
    bv._gravar(pasta / "medidas.json", bv._dump(sorted(registros, key=lambda r: r["vida"])))
    lidos = json.loads((pasta / "medidas.json").read_text(encoding="utf-8"))
    resultado = {"modo": modo, "fase": FASE, "plano": PLANO, "unidades": len(unidades), "vidas": len(lidos), **analisar(lidos)}
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
    return json.dumps({"modo": r["modo"], "vidas": r["vidas"], "leitura": r["leitura"],
                       "gates": {k: v.get("passa") for k, v in r["gates"].items()}}, indent=1, ensure_ascii=True, default=str)


def main() -> None:
    ap_ = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap_.add_argument("--config", required=True)
    ap_.add_argument("--saida", default=None)
    ap_.add_argument("--processos", type=int, default=1)
    a = ap_.parse_args()
    caminho = Path(a.config)
    cfg = json.loads(caminho.read_text(encoding="utf-8"))
    if modo_da_config(cfg) == "fumaca" and a.saida is None:
        raise SystemExit(f"a fumaca precisa de --saida (fora de {SAIDA})")
    print(_resumo(rodar(cfg, Path(a.saida) if a.saida else RAIZ / SAIDA, a.processos, caminho)["resultado"]))


if __name__ == "__main__":
    main()
