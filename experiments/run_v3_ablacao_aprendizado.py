"""EVIDENCIA A2: a ablação do aprendizado no jogo (docs/PLANO_ANALISE_V3_ABLACAO_APRENDIZADO.md, registrado antes de qualquer vida).

Um comando só (seção 6 do plano): confere a trava (o plano APROVADO e a faixa reservada), chama o harness Node do jogo
(`web/app/scripts/ablacao_aprendizado.ts`), que vive as vidas e grava o `medidas.json`, e faz a análise da seção 5 (o IC95 pelo t sobre as
sementes, o p bilateral e o Holm sobre as 15 medidas), com a leitura da seção 5.3.

    python experiments/run_v3_ablacao_aprendizado.py --config experiments/configs/v3_ablacao_aprendizado/run.json

A pasta de saída padrão é `artifacts_v3_ablacao_aprendizado/<etapa>`; ela não pode existir (a run roda uma vez).
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import platform
import statistics
import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
import bancada_v2 as bv  # noqa: E402
from bancada.faixas import FAIXAS_RESERVADAS  # noqa: E402
from digilab.metrics import holm, ic_t, t_unilateral  # noqa: E402
from run_v2_longe_regular import margem_efetiva  # noqa: E402

PLANO = "docs/PLANO_ANALISE_V3_ABLACAO_APRENDIZADO.md"
FASE = "ablacao_aprendizado"
HARNESS = "web/app/scripts/ablacao_aprendizado.ts"
FAIXA = (98101, 98505)
FAIXA_TESTE = (101, 505)
ALFA = 0.05
DONOS = ("atencioso", "relapso", "incoerente")
BRACOS = ("A", "B")
ACOES = ("ocioso", "dormir", "comer", "brincar", "chamar_atencao", "explorar", "emburrar")
TIPOS = ("comida", "cheiro", "bola", "vagar", "ponto", "sem_objeto")
MEDIDAS = tuple([f"acao:{a}" for a in ACOES] + [f"tipo:{t}" for t in TIPOS] + ["reflexo", "nada_a_fazer"])
CODIGO = ("web/app/motor/digibrain/plast.ts", "web/app/motor/digibrain/adapt.ts", "web/app/motor/digibrain/impulso.ts", HARNESS)
CHAVES_CONFIG = {"etapa", "primeira", "k", "dias", "teste"}
LIMITE_GZ = 100 * 1024 * 1024


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=RAIZ, capture_output=True, text=True, check=True).stdout.strip()


def _versao_node() -> str:
    return subprocess.run(["node", "--version"], capture_output=True, text=True, check=True).stdout.strip()


def exigir_plano_aprovado(plano: str) -> None:
    """a trava da seção 0: a linha de status do plano diz "APROVADO pelo Matheus"; o PROPOSTO recusa a run"""
    status = [x for x in plano.splitlines() if x.startswith("**Status:")]
    if not status or not status[0].startswith("**Status: APROVADO pelo Matheus"):
        raise RuntimeError(f"o plano {PLANO} nao esta APROVADO pelo Matheus no cabecalho (secao 0): {status[:1] or 'sem a linha do status'}")


def exigir_faixa_reservada() -> None:
    if not any((lo, hi) == FAIXA for lo, hi, _ in FAIXAS_RESERVADAS):
        raise bv.SementeSemPlano(f"a faixa {FAIXA} nao esta em FAIXAS_RESERVADAS (secao 2.3 do plano)")


def conferir_config(cfg: dict) -> str:
    """o modo: 'run' (a faixa reservada, K = 200, 3 dias, a trava) ou 'fumaca' (as sementes de teste)"""
    if set(cfg) != CHAVES_CONFIG:
        raise ValueError(f"a config tem de ter exatamente {sorted(CHAVES_CONFIG)}: {sorted(cfg)}")
    lo, hi = FAIXA_TESTE if cfg["teste"] else FAIXA
    if not (lo <= cfg["primeira"] and cfg["primeira"] + cfg["k"] - 1 <= hi):
        raise bv.SementeSemPlano(f"as sementes {cfg['primeira']}...{cfg['primeira'] + cfg['k'] - 1} fora da faixa {lo}...{hi}")
    if cfg["teste"]:
        if cfg["etapa"] != "fumaca":
            raise ValueError("as sementes de teste so na fumaca")
        return "fumaca"
    if cfg["etapa"] != "run" or cfg["k"] != 200 or cfg["dias"] != 3:
        raise ValueError(f"a run do plano e K = 200 e 3 dias (AB-1, secao 2): {cfg}")
    return "run"


# ------------------------------------------------------------ a análise (seção 5)
def fracoes(v: dict) -> dict:
    """as 15 medidas de uma vida (seção 3): frações das decisões"""
    n = v["decisoes"]
    if n < 1:
        raise RuntimeError(f"a vida ({v['semente']}, {v['dono']}, {v['braco']}) sem decisao")
    if sum(v["acoes"].values()) != n or sum(v["tipos"].values()) != n or set(v["acoes"]) != set(ACOES) or set(v["tipos"]) != set(TIPOS):
        raise RuntimeError(f"as contagens da vida ({v['semente']}, {v['dono']}, {v['braco']}) nao fecham com as decisoes")
    out = {f"acao:{a}": v["acoes"][a] / n for a in ACOES}
    out.update({f"tipo:{t}": v["tipos"][t] / n for t in TIPOS})
    out.update({"reflexo": v["reflexo"] / n, "nada_a_fazer": v["nada_a_fazer"] / n})
    return out


def por_unidade(vidas: list[dict]) -> dict:
    """{semente: {braco: {medida: media dos 3 donos}}}; falha alto se faltar uma vida ou sobrar uma"""
    tab: dict = {}
    for v in vidas:
        chave = (v["semente"], v["dono"], v["braco"])
        if chave in tab:
            raise RuntimeError(f"vida repetida: {chave}")
        tab[chave] = fracoes(v)
    sementes = sorted({s for s, _, _ in tab})
    if len(tab) != len(sementes) * len(DONOS) * len(BRACOS):
        raise RuntimeError("faltam vidas: cada semente tem 3 donos x 2 bracos")
    return {s: {b: {m: statistics.fmean(tab[(s, d, b)][m] for d in DONOS) for m in MEDIDAS} for b in BRACOS} for s in sementes}


def contraste(difs: list[float]) -> dict:
    """o IC95 pelo t sobre as unidades e o p bilateral (seção 5.1); sem variação, o p fica None (o Holm o conta como 1)"""
    ic = ic_t(difs)
    out = {"n": ic["n"], "media": ic["media"], "dp": ic["dp"], "gl": ic["gl"], "ic95": {"ic_inferior": ic["ic_inferior"],
           "ic_superior": ic["ic_superior"]}, "t": None, "p_bilateral": None, "motivo": ic["motivo"],
           "margem_efetiva": margem_efetiva(ic["dp"], ic["n"])}
    if ic["motivo"] is None and ic["dp"] and ic["dp"] > 0.0:
        t = ic["media"] / (ic["dp"] / math.sqrt(ic["n"]))
        tu = t_unilateral(t, ic["gl"])
        out.update({"t": t, "p_bilateral": min(1.0, 2.0 * min(tu, 1.0 - tu))})
    elif ic["motivo"] is None:
        out["motivo"] = "sem variacao entre as unidades"
    return out


def inclui_zero(c: dict) -> bool:
    lo, hi = c["ic95"]["ic_inferior"], c["ic95"]["ic_superior"]
    return lo is None or (lo <= 0.0 <= hi)


def leitura(contrastes: dict, h: dict) -> dict:
    """a regra da seção 5.3, na ordem: 'muda', 'nula', 'indeterminado'"""
    if any(h[m]["rejeita"] for m in MEDIDAS):
        return {"classe": "muda", "texto": "o P1 e o P2 mudam o comportamento no jogo; H confirmada"}
    if all(inclui_zero(contrastes[m]) for m in MEDIDAS):
        return {"classe": "nula", "texto": "as distribuicoes iguais; H refutada"}
    return {"classe": "indeterminado", "texto": "algum IC95 sem ajuste exclui o 0, mas nenhum passa no Holm; H nao confirmada nem refutada"}


def analisar(vidas: list[dict]) -> dict:
    u = por_unidade(vidas)
    contrastes = {m: contraste([u[s]["A"][m] - u[s]["B"][m] for s in sorted(u)]) for m in MEDIDAS}
    h = holm({m: contrastes[m]["p_bilateral"] for m in MEDIDAS}, ALFA)
    for m in MEDIDAS:
        contrastes[m]["holm"] = h[m]
    niveis = {b: {m: statistics.fmean(u[s][b][m] for s in u) for m in MEDIDAS} for b in BRACOS}
    tv = 0.5 * sum(abs(niveis["A"][f"acao:{a}"] - niveis["B"][f"acao:{a}"]) for a in ACOES)
    va = [v for v in vidas if v["braco"] == "A"]
    desc = {
        "niveis": niveis, "tv_acoes_medias": tv,
        "mortes": {b: sum(1 for v in vidas if v["braco"] == b and v["morte"] is not None) for b in BRACOS},
        "recusas_do_motor": {b: sum(v["recusas"] for v in vidas if v["braco"] == b) for b in BRACOS},
        "decisoes": {b: sum(v["decisoes"] for v in vidas if v["braco"] == b) for b in BRACOS},
        "a_escolhida_por_decisao": {"incentivo": sum(v["escolhida"]["incentivo"] for v in va) / sum(v["decisoes"] for v in va),
                                    "habito": sum(v["escolhida"]["habito"] for v in va) / sum(v["decisoes"] for v in va)},
        "a_unidades_com_aprendido": sum(v["unidades_com_aprendido"] for v in va),
        "b_unidades_com_aprendido": sum(v["unidades_com_aprendido"] for v in vidas if v["braco"] == "B"),
        "escolha_fora_da_lista": sum(v["escolhida"]["fora_da_lista"] for v in vidas),
    }
    return {"unidades": len(u), "vidas": len(vidas), "familia": list(MEDIDAS), "alfa": ALFA, "contrastes": contrastes,
            "leitura": leitura(contrastes, h), "descritivo": desc,
            "nao_demonstra": ["que o aprendizado e bom ou ruim para o pet", "o resultado fora do ovo v38, dos 3 donos, dos 3 dias e sem luta",
                              "algo sobre o Python (a C4 mediu la)", "qual das duas regras (P1 ou P2) produz a diferenca"]}


# ------------------------------------------------------------ a run
def rodar(cfg: dict, pasta: Path, caminho_config: Path | None = None) -> dict:
    modo = conferir_config(cfg)
    if modo == "run":
        exigir_plano_aprovado((RAIZ / PLANO).read_text(encoding="utf-8"))
        exigir_faixa_reservada()
    if pasta.exists():
        raise FileExistsError(f"{pasta} ja existe: a run roda uma vez (secao 6)")
    pasta.mkdir(parents=True)
    cmd_node = ["node", HARNESS, "--primeira", str(cfg["primeira"]), "--k", str(cfg["k"]), "--dias", str(cfg["dias"]),
                *(["--teste"] if cfg["teste"] else []), "--saida", str((pasta / "medidas.json").resolve())]
    meta = {"modo": modo, "fase": FASE, "plano": PLANO, "plano_sha256": _sha(RAIZ / PLANO), "config": cfg,
            "config_arquivo": None if caminho_config is None else caminho_config.resolve().relative_to(RAIZ).as_posix(),
            "config_sha256": None if caminho_config is None else _sha(caminho_config),
            "comando": " ".join(["python", *sys.argv]) if sys.argv and sys.argv[0] else None,
            "comando_node": " ".join(cmd_node[:-1] + ["<pasta>/medidas.json"]),
            "python": platform.python_version(), "node": _versao_node(), "orquestrador_sha256": _sha(Path(__file__)),
            "codigo_sha256": {c: _sha(RAIZ / c) for c in CODIGO}, "git_head": _git("rev-parse", "HEAD"),
            "git_limpo": _git("status", "--porcelain") == "", "inicio": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())}
    t0 = time.time()
    subprocess.run(cmd_node, cwd=RAIZ, check=True)
    medidas = json.loads((pasta / "medidas.json").read_text(encoding="utf-8"))
    if medidas["node"] != meta["node"]:
        raise RuntimeError(f"o harness rodou noutro Node: {medidas['node']} != {meta['node']}")
    resultado = {"fase": FASE, "modo": modo, "plano": PLANO, **analisar(medidas["vidas"])}
    (pasta / "resultado.json").write_text(json.dumps(resultado, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    artefatos = {"medidas.json": _sha(pasta / "medidas.json"), "resultado.json": _sha(pasta / "resultado.json")}
    if (pasta / "medidas.json").stat().st_size > LIMITE_GZ:
        dados = (pasta / "medidas.json").read_bytes()
        (pasta / "medidas.json.gz").write_bytes(gzip.compress(dados, mtime=0))
        artefatos["medidas.json.gz"] = _sha(pasta / "medidas.json.gz")
    meta.update({"artefatos_sha256": artefatos, "vidas_sha256": {f"{v['semente']}|{v['dono']}|{v['braco']}": [v["log_sha256"], v["decisoes_sha256"]]
                                                                  for v in medidas["vidas"]},
                 "parede_s": time.time() - t0, "fim": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())})
    (pasta / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    return {"meta": meta, "resultado": resultado}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--config", required=True, type=Path)
    ap.add_argument("--saida", type=Path)
    a = ap.parse_args()
    cfg = json.loads(a.config.read_text(encoding="utf-8"))
    pasta = a.saida or RAIZ / "artifacts_v3_ablacao_aprendizado" / cfg["etapa"]
    out = rodar(cfg, pasta, a.config)
    print(json.dumps({"leitura": out["resultado"]["leitura"], "artefatos_sha256": out["meta"]["artefatos_sha256"]}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
