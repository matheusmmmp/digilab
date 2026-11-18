"""SOCIAL_PAR, o piloto do A0 e do B0 (docs/PLANO_ANALISE_V3_SOCIAL_PAR_A0.md, secao 6; A0-7, APROVADA pelo Matheus em 2026-11-17).

100 pares na faixa 102101...102505 (5 bases x 20, prefixo `social_par_piloto`), com as mesmas cinco vidas, o G-INSTR e o G1 do orquestrador
(`experiments/run_v3_social_par_a0.py`). O piloto grava SO:
  - o desvio padrao de D_A e de D_B nos pares elegiveis (nunca a media de nenhum contraste);
  - as frequencias das premissas (5.1);
  - a regra do N da secao 6 (o menor de 200, 400, 800 e 1 600 pares elegiveis com 1,97 x 1,2 dp / raiz(N) <= delta / 2), e o K por base
    que ela pede, pela fracao de elegiveis;
  - o tempo real por par.
Nada aqui muda o d0, a janela, as margens nem as premissas; o N e o K ficam DECIDIDOS pelo Matheus num commit que atualiza a secao 6.

    python experiments/piloto_social_par_a0.py --processos 4
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import run_v3_social_par_a0 as a0  # noqa: E402
from bancada.rodar import _dump, _gravar, _sha  # noqa: E402

CONFIG = RAIZ / "experiments/configs/v3_social_par_a0/piloto.json"
PASTA = RAIZ / "artifacts_v3_social_par_a0/piloto"
SAIDA = RAIZ / "artifacts_v3_social_par_a0/piloto.json"
CANDIDATOS_N = (200, 400, 800, 1600)          # 6
QUANTIL, FOLGA = 1.97, 1.2                    # 6: o t de 0,975 perto de N = 200 e a folga de 20 % da A5.9


def regra_do_n(dp: float | None, delta: float) -> dict:
    """a regra da secao 6: o menor N (pares elegiveis) com QUANTIL x FOLGA x dp / raiz(N) <= delta / 2; sem nenhum, 1 600 com a marca"""
    if dp is None:
        return {"n": None, "bastou": False, "motivo": "sem dp (menos de 2 pares elegiveis)"}
    for n in CANDIDATOS_N:
        if QUANTIL * FOLGA * dp / math.sqrt(n) <= delta / 2:
            return {"n": n, "bastou": True, "meia_largura_prevista": QUANTIL * FOLGA * dp / math.sqrt(n), "motivo": None}
    n = CANDIDATOS_N[-1]
    return {"n": n, "bastou": False, "meia_largura_prevista": QUANTIL * FOLGA * dp / math.sqrt(n),
            "motivo": "nem 1 600 bastou: a margem efetiva vai no relato, o criterio nao muda"}


def _dp(valores: list[float]) -> float | None:
    return statistics.stdev(valores) if len(valores) >= 2 else None


def resumo(registros: list[dict], parede_s: float, processos: int) -> dict:
    """o que o piloto grava; por construcao, nenhuma media de contraste"""
    n = len(registros)
    ea = [r for r in registros if a0.elegivel_a(r)]
    eb = [r for r in registros if a0.elegivel_b(r) and a0.d_b(r) is not None]
    out = {"pares": n, "premissas": a0.premissas(registros), "regra": {}}
    ks = {}
    for nome, eleg, valores, delta in (("A0", ea, [a0.d_a(r) for r in ea], a0.DELTA_A), ("B0", eb, [a0.d_b(r) for r in eb], a0.DELTA_B)):
        dp = _dp(valores)
        regra = regra_do_n(dp, delta)
        fracao = len(eleg) / n if n else 0.0
        k = None if regra["n"] is None or fracao == 0 else math.ceil(math.ceil(regra["n"] / fracao) / len(a0.BASES["run"]))
        ks[nome] = k
        out["regra"][nome] = {"dp": dp, "delta": delta, "n_elegiveis_piloto": len(eleg), "fracao_elegiveis": fracao, **regra,
                              "k_por_base": k}
    validos = [k for k in ks.values() if k is not None]
    out["k_por_base_sugerido"] = max(validos) if validos else None
    out["parede_por_par_s"] = parede_s * processos / n if n else None
    if out["k_por_base_sugerido"] is not None and out["parede_por_par_s"] is not None:
        out["parede_da_run_estimada_h"] = out["k_por_base_sugerido"] * len(a0.BASES["run"]) * out["parede_por_par_s"] / a0.MAX_PROCESSOS / 3600
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--processos", type=int, default=1)
    a = ap.parse_args()
    if SAIDA.exists():
        raise FileExistsError(f"{SAIDA} ja existe: o piloto roda uma vez")
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    if cfg.get("modo") != "piloto":
        raise ValueError(f"a config do piloto tem o modo piloto: {cfg}")
    meta, registros = a0.coletar(cfg, PASTA, a.processos, CONFIG)
    out = {"fase": "social_par_a0_piloto", "plano": a0.PLANO, "meta_sha256": _sha(PASTA / "meta.json"),
           **resumo(registros, meta["vidas_parede_s"], a.processos)}
    _gravar(SAIDA, _dump(out))
    print(json.dumps({k: out[k] for k in ("pares", "regra", "k_por_base_sugerido")}, indent=1, ensure_ascii=True, default=str))


if __name__ == "__main__":
    main()
