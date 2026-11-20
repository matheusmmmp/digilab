"""A G-CUSTO da P4, etapa 1 (docs/TAREFA_V2_P4_CEREBRO_MUNDO.md, secao 4; PROPOSTA, SEM FONTE): o CPU de uma vida de 12 dias com as
chaves do contrato (os sensores e o controlador) fica abaixo de 3 vezes o de hoje.

A vida e a da validacao do adendo 8 (experiments/configs/v2_pet_que_pensa/validacao_adendo8.json: o paladar, a fruta ao lado, o T1 de 12
dias, o cerebro A com o planejador), numa semente dos testes. A unica diferenca entre as duas medidas e a chave `contrato` da
bancada do J5 (o `cfg_contrato` no motor). Mede o
`time.process_time` da vida (sem as medidas da bancada), o melhor de `--repeticoes`, e um descritivo do andar das duas vidas (as
chegadas e os consumos). Nao e run de pesquisa: nada vai para resultado.

    python tools/custo_p4_contrato.py --braco P1-plan --semente 101
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402

CONFIG = RAIZ / "experiments" / "configs" / "v2_pet_que_pensa" / "validacao_adendo8.json"
LIMITE = 3                                     # a G-CUSTO: abaixo de 3 vezes o de hoje
SEMENTES_TESTE = (101, 202, 303, 404, 505)


def bancada(contrato: bool):
    """a bancada do J5 da config da validacao do adendo 8, nas sementes dos testes, com a chave `contrato` da bancada (a etapa 3)"""
    cfg = {k: v for k, v in json.loads(CONFIG.read_text(encoding="utf-8")).items() if k not in ("validacao", "unidades")}
    return bv.bancada_pqp_da_config({**cfg, "sementes": list(SEMENTES_TESTE), "contrato": contrato})


def medir(contrato: bool, braco: str, semente: int, repeticoes: int) -> tuple[float, object]:
    bp = bancada(contrato)
    melhor, vida = None, None
    for _ in range(repeticoes):
        t = time.process_time()
        vida = bp.vida(bv.EspecPQP(braco, "T1", semente))
        dt = time.process_time() - t
        melhor = dt if melhor is None else min(melhor, dt)
    return melhor, vida


def descritivo(motor) -> dict:
    """o que muda no andar (descritivo, nao e gate): as decisoes com alvo, quantas chegaram, as comidas consumidas e, com o contrato,
    por que o controlador parou"""
    r = motor.resumo_mundo_fisico()
    com_alvo = [d for d in r["decisoes"] if d["alvo"] is not None]
    out = {"decisoes_com_alvo": len(com_alvo), "chegou": sum(1 for d in com_alvo if d["chegou"]), "consumos": len(r["consumos"])}
    if "contrato_decisoes" in r:
        parou = {}
        for c in r["contrato_decisoes"]:
            parou[c["parou_por"]] = parou.get(c["parou_por"], 0) + 1
        out["parou_por"] = dict(sorted(parou.items()))
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--braco", default="P1-plan", choices=list(bv.BRACOS_PQP))
    ap.add_argument("--semente", type=int, default=101)
    ap.add_argument("--repeticoes", type=int, default=3)
    a = ap.parse_args()
    if a.semente not in SEMENTES_TESTE:
        raise SystemExit(f"semente {a.semente}: so as dos testes {SEMENTES_TESTE}")
    hoje, vida_hoje = medir(False, a.braco, a.semente, a.repeticoes)
    com, vida = medir(True, a.braco, a.semente, a.repeticoes)
    if not getattr(vida.motor, "cct", None) or not vida.motor.cct.ligada:
        raise RuntimeError("a vida com o contrato nao tem o contrato ligado")
    razao = com / hoje
    print(json.dumps({"braco": a.braco, "semente": a.semente, "dias": 12, "cpu_hoje_s": round(hoje, 3), "cpu_contrato_s": round(com, 3),
                      "razao": round(razao, 2), "limite": LIMITE, "passa": razao < LIMITE,
                      "descritivo": {"hoje": descritivo(vida_hoje.motor), "contrato": descritivo(vida.motor)}}, ensure_ascii=False))


if __name__ == "__main__":
    main()
