"""Varredura de calibracao do combate V2.1 (SO sementes de calibracao).

    python experiments/calibrar_v21.py --variantes experiments/configs/calibracao/variantes_v21.json

Para cada variante (sobrescritas de ConfigCombateV21 e, opcionalmente, o
multiplicador de estagio do adolescente), mede E1 (suporte e dominantes), a
media de cada especie no E2 e a taxa adulto x adolescente do E4, com N
partidas por par por semente. Grava uma linha JSON por variante em
artifacts_combate_v21/calibracao_varredura.jsonl. Nao decide nada: o registro
da escolha fica em experiments/configs/calibracao_v21.json.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

from digilab.combate_v2.v21.bots import FORMAS, lutador_adolescente, lutador_adulto  # noqa: E402
from digilab.combate_v2.v21.catalogo import LINHA_DA_FORMA, carater_canonico  # noqa: E402
from digilab.combate_v2.v21.regras import Regras  # noqa: E402
from digilab.config import CONFIG_BATERIA_V21, CONFIG_CATALOGO, CONFIG_COMBATE_V21  # noqa: E402
from digilab.metrics import matriz_taxas  # noqa: E402
from run_bateria_v21 import avaliar_e1, partidas_par, round_robin_arquetipos  # noqa: E402


def avaliar(variante: dict, sementes: list[int], n: int) -> dict:
    sobre = dict(variante.get("v21", {}))
    v = replace(CONFIG_COMBATE_V21, **sobre)
    mult = dict(CONFIG_CATALOGO.mult_estagio)
    if "mult_adolescente" in variante:
        mult["adolescente"] = variante["mult_adolescente"]
    cat = replace(CONFIG_CATALOGO, mult_estagio=mult)
    r = Regras(v21=v)
    especies = list(CONFIG_CATALOGO.especies_ativas)

    conf = round_robin_arquetipos(especies, sementes, n, r, v, rotulo="cal-e1")
    ok, val = avaliar_e1(matriz_taxas(conf), CONFIG_BATERIA_V21)

    conf2 = []
    for f in FORMAS:
        lut = {e: lutador_adulto(f, e, v, cat=cat) for e in especies}
        for i, a in enumerate(especies):
            for b in especies[i:]:
                conf2 += [(a, b, x) for _, _, x, _ in partidas_par(lut[a], lut[b], f"cal-e2|{f}", sementes, n, r)]
    m2 = matriz_taxas(conf2)
    media_esp = {e: sum(m2[e][o] for o in especies) / len(especies) for e in especies}
    dom_esp = [e for e in especies if all(m2[e][o] > 0.5 for o in especies if o != e)]

    e4 = {}
    for f in FORMAS:
        pts = []
        for e in especies:
            ad = lutador_adulto(f, e, v, cat=cat)
            adol = lutador_adolescente(LINHA_DA_FORMA[f], e, carater_canonico(f, v), v, cat=cat)
            pts += [x for _, _, x, _ in partidas_par(ad, adol, "cal-e4", sementes, n, r)]
        e4[f] = sum(pts) / len(pts)
    cb = CONFIG_BATERIA_V21
    return {"nome": variante["nome"], "variante": variante, "e1_ok": ok, "e1_suporte": val["suporte"],
            "e1_dominantes": val["dominantes"], "e1_estrategia": val["estrategia"],
            "e2_media_especie": media_esp, "e2_dominantes": dom_esp, "e4_taxa": e4,
            "e4_dentro": sum(cb.taxa_min_e4 <= t <= cb.taxa_max_e4 for t in e4.values())}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--variantes", required=True, type=Path)
    a = ap.parse_args(argv)
    cfg = json.loads(a.variantes.read_text(encoding="utf-8"))
    saida = RAIZ / cfg["saida"]
    saida.parent.mkdir(parents=True, exist_ok=True)
    linhas = []
    for var in cfg["variantes"]:
        res = avaliar(var, cfg["sementes_calibracao"], cfg["partidas_por_par_por_semente"])
        linhas.append(json.dumps(res, sort_keys=True, ensure_ascii=False))
        print(f"{res['nome']:34s} E1 {res['e1_ok']!s:5} suporte {len(res['e1_suporte'])} "
              f"E2 dom {res['e2_dominantes']} {({k: round(x, 3) for k, x in res['e2_media_especie'].items()})} "
              f"E4 dentro {res['e4_dentro']}/8", flush=True)
    saida.write_text("\n".join(linhas) + "\n", encoding="utf-8", newline="\n")
    print(f"gravado {saida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
