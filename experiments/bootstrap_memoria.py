"""Bootstrap sobre sementes do efeito da memoria na divergencia (pendencia do CLAUDE.md: "efeito pequeno e sem
incerteza; precisa de bootstrap sobre sementes antes de qualquer conclusao").

    python experiments/bootstrap_memoria.py

Le so artefatos que ja existem (nenhuma vida nova): artifacts/ (canonica, sem memoria), artifacts_v1_memoria/ e
artifacts_v1_memoria_espacos/. Estatistica de cada run: separacao = JSD media entre bracos - JSD media dentro do
braco (pares de pets de sementes diferentes). Efeito = separacao(com memoria) - separacao(sem), nas sementes em
comum. Bootstrap: reamostra as sementes com reposicao (10000, semente 20260929); um par (a@s1, b@s2) pesa
w(s1) * w(s2), w = quantas vezes a semente saiu. Com poucas sementes o IC e largo: e isso que ele deve mostrar.
Saida: artifacts_v1_memoria/bootstrap_sementes.json.
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
BOOT, SEMENTE = 10000, 20260929


def pares(pasta: str) -> dict[tuple[str, int, str, int], float]:
    d = json.loads((RAIZ / pasta / "divergence.json").read_text(encoding="utf-8"))
    out = {}
    for k, v in d["pares"].items():
        a, b = (x.strip() for x in k.split("|"))
        if "@" not in a or "@" not in b:
            continue                                  # pets de referencia (instinto) nao sao bracos com semente
        (ba, sa), (bb, sb) = (x.split("@") for x in (a, b))
        out[(ba, int(sa), bb, int(sb))] = v
    return out


def separacao(pp: dict, peso: dict[int, int]) -> float:
    ent = den = went = wden = 0.0
    for (ba, sa, bb, sb), v in pp.items():
        if sa == sb:
            continue                                  # so pares de sementes diferentes (a semente em comum confunde)
        w = peso.get(sa, 0) * peso.get(sb, 0)
        if not w:
            continue
        if ba == bb:
            den += w * v; wden += w
        else:
            ent += w * v; went += w
    if not went or not wden:
        return float("nan")
    return ent / went - den / wden


def main() -> int:
    base = pares("artifacts")
    out = {"descricao": __doc__.strip().splitlines()[0], "bootstrap": {"reamostragens": BOOT, "semente": SEMENTE}, "comparacoes": {}}
    for nome in ("artifacts_v1_memoria", "artifacts_v1_memoria_espacos"):
        mem = pares(nome)
        sem = sorted({s for k in base for s in (k[1], k[3])} & {s for k in mem for s in (k[1], k[3])})
        todos = {s: 1 for s in sem}
        est = separacao(mem, todos) - separacao(base, todos)
        rng, dist = random.Random(SEMENTE), []
        for _ in range(BOOT):
            w: dict[int, int] = {}
            for _ in sem:
                s = sem[rng.randrange(len(sem))]
                w[s] = w.get(s, 0) + 1
            x = separacao(mem, w) - separacao(base, w)
            if x == x:                                   # nan quando a reamostra tem uma semente so
                dist.append(x)
        dist.sort()
        ic = [dist[int(.025 * len(dist))], dist[int(.975 * len(dist)) - 1]]
        out["comparacoes"][f"{nome} - artifacts"] = {
            "sementes": sem, "separacao_com_memoria": separacao(mem, todos), "separacao_sem": separacao(base, todos),
            "efeito": est, "ic95": ic, "reamostras_validas": len(dist),
            "leitura": "IC inclui 0: sem evidencia de efeito" if ic[0] <= 0 <= ic[1] else "IC exclui 0"}
        print(f"{nome}: efeito {est:+.5f} bits, IC95 [{ic[0]:+.5f}, {ic[1]:+.5f}] ({len(sem)} sementes)")
    (RAIZ / "artifacts_v1_memoria" / "bootstrap_sementes.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
