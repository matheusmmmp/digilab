"""Gabarito de paridade Python x web da confianca de combate (M1, gate G2).

Uma sequencia FIXA de 200 lutas (rival, tick, resultado, sensibilidade), sorteada de uma rng propria com semente
fixa, passada por digilab/confianca.py com a ConfigConfianca ligada; grava a novidade e a confianca `c` a cada
passo e a frase de estado (com histerese) no tick de cada luta e 2 h depois. O teste web
(web/app/test/confianca.test.ts) reproduz tudo em motor/confianca.ts e exige diferenca <= 1e-12.

So le digilab/: nada no pacote muda.

uso: python experiments/exportar_gabarito_confianca.py [saida.json]
"""
from __future__ import annotations

import dataclasses
import json
import random
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab.confianca import ConfiancaCombate  # noqa: E402
from digilab.config import CONFIG_CONFIANCA_LIGADA  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402

SAIDA = RAIZ / "web" / "app" / "test" / "gabaritos" / "confianca_python.json"
SEMENTE = 20260929
N_LUTAS = 200
RIVAIS = ("aleatorio", "agressivo", "tier1_brutamontes", "duelista", "muralha")


def gerar(semente: int = SEMENTE, n: int = N_LUTAS) -> dict:
    rng = random.Random(derivar_semente("gabarito-confianca", semente))
    cfg = CONFIG_CONFIANCA_LIGADA
    cc = ConfiancaCombate(cfg)
    passos = []
    tick = 0
    # blocos: as vezes o mesmo rival varias vezes seguidas (tedio), as vezes rodizio; intervalos de 0 a 12 h, com
    # pausas longas de vez em quando (a recuperacao pelo tau)
    rival = RIVAIS[0]
    for k in range(n):
        if k == 0 or rng.random() < 0.4:
            rival = RIVAIS[rng.randrange(len(RIVAIS))]
        tick += 0 if rng.random() < 0.1 else rng.randrange(1, 12 * 60 + 1) if rng.random() < 0.9 else rng.randrange(12 * 60, 4 * 1440)
        sinal = rng.choice((1, 1, -1, -1, 0))
        sensibilidade = round(rng.uniform(-1.0, 1.0), 3)
        r = cc.registrar(tick, rival, sinal, sensibilidade)
        e0, e1 = cc.estado(tick), cc.estado(tick + cfg.histerese_frase_min)
        passos.append({"k": k, "tick": tick, "rival": rival, "sinal": sinal, "sensibilidade": sensibilidade,
                       "novidade": r["novidade"], "c": r["c"], "valor_2h": cc.valor(tick + cfg.histerese_frase_min),
                       "estado": e0["estado"], "desde": e0["desde"], "lutas": e0["lutas"],
                       "estado_2h": e1["estado"], "desde_2h": e1["desde"], "lutas_2h": e1["lutas"]})
    return {"nota": "M1 (docs/DESIGN_MVP_M1_CONFIANCA.md) gate G2: paridade Python x web da confianca e da novidade numa "
                    "sequencia fixa de lutas; gerado por experiments/exportar_gabarito_confianca.py",
            "semente": semente, "config": dataclasses.asdict(cfg), "passos": passos, "final": cc.para_dict(),
            "estados": sorted({p["estado"] for p in passos} | {p["estado_2h"] for p in passos})}


def main() -> int:
    saida = Path(sys.argv[1]) if len(sys.argv) > 1 else SAIDA
    g = gerar()
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text(json.dumps(g, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"{saida}: {len(g['passos'])} lutas; estados vistos: {g['estados']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
