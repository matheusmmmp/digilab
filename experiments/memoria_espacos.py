"""Relatorio da memoria por espacos (docs/ADENDO_MEMORIA_EMOCAO_DF.md, Parte 1).

    python experiments/memoria_espacos.py

Reprocessa as vidas de artifacts_v1_memoria_espacos/vidas (replay do log, sem
reexecutar nada novo) e mede, a cada decisao do pet:
  - ocupacao media dos espacos de curto e longo prazo, por braco;
  - fracao do tempo em que cada categoria esta na memoria (curto ou longo);
  - fracao dos motivos que citam uma memoria (e dentre eles, qual categoria).
Grava artifacts_v1_memoria_espacos/espacos.json.
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab.events import LogDeEventos  # noqa: E402
from digilab.memoria_espacos import FATORES_ESPACOS, PoliticaBanditEspacos  # noqa: E402
from digilab.motivo import motivos_de_vida  # noqa: E402

PASTA = RAIZ / "artifacts_v1_memoria_espacos"


class _Amostrada(PoliticaBanditEspacos):
    """Mesma politica; so anota os espacos depois de cada decisao observada (leitura)."""

    def __init__(self, cfg=None):
        super().__init__(cfg)
        self.amostras: list[tuple[int, int, tuple[str, ...]]] = []

    def observar(self, transicao):
        super().observar(transicao)
        m = self.memoria
        self.amostras.append((len(m.curto), len(m.longo), tuple(sorted({x.categoria for x in m.curto + m.longo}))))


def main() -> int:
    vidas = sorted((PASTA / "vidas").glob("*@*.jsonl"))
    if not vidas:
        raise FileNotFoundError(f"sem vidas em {PASTA / 'vidas'}: rode run_arena.py com configs/memoria_espacos.json")
    por_braco: dict[str, dict] = defaultdict(lambda: {"curto": [], "longo": [], "presenca": Counter(), "n": 0,
                                                      "motivos": 0, "citam": 0, "cita_cat": Counter()})
    for arq in vidas:
        m = re.fullmatch(r"(.+)@(\d+)\.jsonl", arq.name)
        braco, semente = m.group(1), int(m.group(2))
        pols: list[_Amostrada] = []

        def fab(c):
            p = _Amostrada(c)
            pols.append(p)
            return p

        _, emb = motivos_de_vida(LogDeEventos.de_jsonl(arq.read_text(encoding="utf-8")), fab, semente)
        b = por_braco[braco]
        for curto, longo, cats in pols[-1].amostras:
            b["curto"].append(curto)
            b["longo"].append(longo)
            b["presenca"].update(cats)
            b["n"] += 1
        for mot in emb.motivos:
            b["motivos"] += 1
            cit = [f for f in mot.fatores if f in FATORES_ESPACOS]
            if cit:
                b["citam"] += 1
                b["cita_cat"].update(cit)
    saida = {}
    for braco, b in sorted(por_braco.items()):
        saida[braco] = {
            "decisoes": b["n"],
            "ocupacao_media_curto": sum(b["curto"]) / b["n"],
            "ocupacao_media_longo": sum(b["longo"]) / b["n"],
            "fracao_do_tempo_na_memoria": {c: b["presenca"][c] / b["n"] for c in FATORES_ESPACOS},
            "fracao_motivos_citam_memoria": b["citam"] / b["motivos"],
            "motivos_por_categoria": dict(b["cita_cat"]),
        }
    total_mot = sum(b["motivos"] for b in por_braco.values())
    total_cit = sum(b["citam"] for b in por_braco.values())
    resumo = {"por_braco": saida, "fracao_motivos_citam_memoria_total": total_cit / total_mot,
              "n_vidas": len(vidas), "fonte": "replay das vidas de artifacts_v1_memoria_espacos/vidas"}
    (PASTA / "espacos.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=2, sort_keys=True),
                                        encoding="utf-8", newline="\n")
    print(json.dumps(resumo, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
