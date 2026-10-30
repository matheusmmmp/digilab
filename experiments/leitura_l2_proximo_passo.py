"""A leitura para o proximo passo do longe (docs/PROPOSTA_L2_PROXIMO_PASSO_DIGIBRAIN_MODULAR.md), so das partes gravadas da avaliacao da
L-2: nenhuma vida roda, e nenhum criterio novo. Descritiva e pos hoc.

  - relê as 12 partes pelo indice (o `ler_medidas` da L-2 confere o sha256 e as vidas de cada uma);
  - por lugar e por par (M3 x M3+S, o primario; M0 x M0+S, o descritivo), a diferenca pareada por unidade (base, semente), a media das 4
    celulas do lugar, com o IC do t (`metrics.ic_t`, o do adendo 4), de:
      as acoes por vida (as 7), os reflexos, as buscas e as buscas em meta ou achou,
      as trocas da busca pelo reflexo, por outra unidade e pelo dormir sorteado (o dormir vencedor menos o reflexo),
      e as trocas da busca por vencedora;
  - as buscas do braco sem a suspensao que o reflexo nao cortou: a fracao em meta ou achou, para ler ao lado das nunca suspensas (S-2).

    python experiments/leitura_l2_proximo_passo.py [--pasta <a pasta da avaliacao>]
grava artifacts_v2_digibrain_prototipo/l2/proximo_passo_leitura.json
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v2_digibrain_l2 as l2  # noqa: E402
from digilab.metrics import ic_t  # noqa: E402

AVALIACAO = RAIZ / l2.SAIDA["l2_avaliacao"]
SAIDA = RAIZ / "artifacts_v2_digibrain_prototipo" / "l2" / "proximo_passo_leitura.json"
PARES = (("M3", "M3+S"), ("M0", "M0+S"))
ACOES = ("ocioso", "dormir", "comer", "brincar", "chamar_atencao", "explorar", "emburrar")


def _s2(r: dict) -> dict:
    return r["l2"]["s2"]


def _trocas(r: dict) -> dict:
    return r["l2"]["trocas"]["busca"]


def _dormir_sorteado(r: dict) -> int:
    t = _trocas(r)
    n = t["por_vencedora"].get("dormir/None", 0) - t["reflexo"]
    if n < 0:
        raise RuntimeError(f"{r['vida']}: o dormir vencedor abaixo das trocas pelo reflexo")
    return n


MEDIDAS = {
    **{f"acoes/{a}": (lambda a: lambda r: r["acoes"].get(a, 0))(a) for a in ACOES},
    "reflexos": lambda r: r["reflexos"],
    "buscas": lambda r: _s2(r)["buscas_nunca_suspensas"] + _s2(r)["buscas_suspensas"],
    "buscas_meta_ou_achou": lambda r: _s2(r)["buscas_nunca_suspensas_meta_ou_achou"] + _s2(r)["buscas_suspensas_meta_ou_achou"],
    "trocas_busca/reflexo": lambda r: _trocas(r)["reflexo"],
    "trocas_busca/outra_unidade": lambda r: _trocas(r)["outra_com_racao_em_R"] + _trocas(r)["outra_sem_racao_em_R"],
    "trocas_busca/dormir_sorteado": _dormir_sorteado,
}


def _por_unidade(regs: dict, braco: str, lugar: str, medida) -> dict:
    """{semente: a media da medida nas 4 celulas (os donos) do lugar}"""
    grupos: dict = defaultdict(list)
    for r in regs.values():
        if r["braco"] == braco and r["lugar"] == lugar:
            grupos[(r["base"], r["semente"])].append(medida(r))
    if any(len(v) != 4 for v in grupos.values()):
        raise RuntimeError(f"{braco}/{lugar}: uma unidade sem as 4 celulas")
    return {k: sum(v) / 4 for k, v in grupos.items()}


def _par(regs: dict, par: tuple, lugar: str, medida) -> dict:
    a, b = _por_unidade(regs, par[0], lugar, medida), _por_unidade(regs, par[1], lugar, medida)
    if set(a) != set(b):
        raise RuntimeError(f"{par}/{lugar}: as unidades dos dois bracos nao sao as mesmas")
    ks = sorted(a)
    ic = ic_t([b[k] - a[k] for k in ks])
    return {par[0]: sum(a.values()) / len(a), par[1]: sum(b.values()) / len(b), "dif": ic["media"],
            "ic_inferior": ic["ic_inferior"], "ic_superior": ic["ic_superior"], "unidades": ic["n"]}


def _vencedoras(regs: dict, braco: str, lugar: str) -> dict:
    vs = [r for r in regs.values() if r["braco"] == braco and r["lugar"] == lugar]
    c: Counter = Counter()
    for r in vs:
        c.update(_trocas(r)["por_vencedora"])
    return {k: v / len(vs) for k, v in sorted(c.items())}


def _nao_cortadas(regs: dict, braco: str, lugar: str) -> dict:
    """as buscas do braco sem a suspensao que o reflexo nao cortou: todas menos as trocadas pelo reflexo; as em meta ou achou sao todas
    as dele (a cortada acaba no reflexo, sem meta)"""
    vs = [r for r in regs.values() if r["braco"] == braco and r["lugar"] == lugar]
    todas = sum(MEDIDAS["buscas"](r) for r in vs)
    cortadas = sum(_trocas(r)["reflexo"] for r in vs)
    sucesso = sum(MEDIDAS["buscas_meta_ou_achou"](r) for r in vs)
    return {"buscas": todas, "cortadas_pelo_reflexo": cortadas, "nao_cortadas": todas - cortadas,
            "frac_meta_ou_achou_nao_cortadas": sucesso / (todas - cortadas) if todas > cortadas else None}


def calcular(pasta: Path) -> dict:
    regs = l2.ler_medidas(pasta)
    out: dict = {}
    for par in PARES:
        for lugar in l2.orq.LUGARES:
            chave = f"{par[0]}x{par[1]}|{lugar}"
            out[chave] = {"medidas": {nome: _par(regs, par, lugar, f) for nome, f in MEDIDAS.items()},
                          "trocas_busca_por_vencedora_por_vida": {b: _vencedoras(regs, b, lugar) for b in par},
                          "sem_suspensao_nao_cortadas": _nao_cortadas(regs, par[0], lugar)}
    return {"rotulo": "a leitura para o proximo passo do longe: as partes da avaliacao da L-2 relidas, pareadas por unidade; descritiva, "
                      "pos hoc, sem criterio",
            "fontes": {n: bv._sha(pasta / n) for n in ("meta.json", "resultado.json", l2.INDICE)},
            "script": {"arquivo": l2.orq.rc._relativo(Path(__file__)), "sha256": bv._sha(Path(__file__))},
            "ic": "metrics.ic_t sobre as unidades (base, semente), cada uma a media das 4 celulas do lugar",
            "vidas": len(regs),
            "por_par_e_lugar": out}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pasta", type=Path, default=AVALIACAO, help="a pasta da avaliacao da L-2 (o padrao: a do repositorio)")
    d = calcular(ap.parse_args().pasta)
    bv._gravar(SAIDA, bv._dump(d))
    print(f"gravado {l2.orq.rc._relativo(SAIDA)} (sha256 {bv._sha(SAIDA)}), {d['vidas']} vidas")
