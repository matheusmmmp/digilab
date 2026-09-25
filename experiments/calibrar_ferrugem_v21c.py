"""Etapa 3 da TAREFA_CORRECAO_COMBATE: calibracao da formula de vida (causa da dominancia da Ferrugem).

So sementes de CALIBRACAO da V2.1 (3101..3505). Base V2C (C1-C4). Para cada coeficiente de vida por
vigor, hp_base e ajustado para a vida neutra (vigor 10) continuar 100. Mede a taxa da Ferrugem contra
as outras especies ativas, mesmo arquetipo e estilo (mesma medida do diagnostico da Etapa 0), e a
dispersao entre especies (max - min da taxa media de cada especie contra as outras).

Criterio (fixado antes): o menor desvio do coeficiente original cuja maior taxa media de especie
fique <= 0,60 (E2 pede nenhuma especie dominante).

    python experiments/calibrar_ferrugem_v21c.py
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab.combate_v2.v21 import partida as p21  # noqa: E402
from digilab.combate_v2.v21.bots import FORMAS, lutador_adulto  # noqa: E402
from digilab.combate_v2.v21.regras import Regras  # noqa: E402
from digilab.config import CONFIG_CATALOGO, CONFIG_COMBATE_V2, CONFIG_COMBATE_V21, ConfigCombateV2C, ConfigCombateV21C  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402

SEM = (3101, 3202, 3303, 3404, 3505)
BASE_V2C = {"finta": True, "dano_parry": 5.0, "fuga_condicionada": True, "turno_morte_subita": 25,
            "mult_morte_subita": 1.5}
COEFS = (3.0, 2.5, 2.0, 1.5, 1.0)
LIMITE = 0.60


def taxa_especies(r: Regras, n: int) -> dict:
    esp = list(CONFIG_CATALOGO.especies_ativas)
    pts = {e: [] for e in esp}
    for f in FORMAS:
        lut = {e: lutador_adulto(f, e, r.v21) for e in esp}
        for i, a in enumerate(esp):
            for b in esp[i + 1:]:
                for s in SEM:
                    for k in range(n):
                        sp = derivar_semente("ferr-c", f, s, a, b, k)
                        x = p21.jogar(lut[a], lut[b], sp, r).pontos_a if k < n // 2 else 1.0 - p21.jogar(lut[b], lut[a], sp, r).pontos_a
                        pts[a].append(x)
                        pts[b].append(1.0 - x)
    return {e: sum(v) / len(v) for e, v in pts.items()}


def main() -> int:
    base = ConfigCombateV2C(**{**asdict(CONFIG_COMBATE_V2), **BASE_V2C})
    linhas = []
    for c in COEFS:
        v21 = ConfigCombateV21C(**{**asdict(CONFIG_COMBATE_V21), "hp_por_vigor": c, "hp_base": 100.0 - 10.0 * c})
        t = taxa_especies(Regras(base=base, v21=v21), 20)
        linhas.append({"hp_por_vigor": c, "hp_base": v21.hp_base, "taxa_por_especie": t, "maior": max(t.values()),
                       "dispersao": max(t.values()) - min(t.values())})
        print(c, {k: round(x, 3) for k, x in t.items()}, flush=True)
    ok = [l for l in linhas if l["maior"] <= LIMITE]
    escolha = min(ok, key=lambda l: abs(l["hp_por_vigor"] - CONFIG_COMBATE_V21.hp_por_vigor)) if ok else None
    (RAIZ / "experiments" / "configs" / "v21c" / "calibracao_ferrugem.json").write_text(json.dumps({
        "descricao": __doc__.strip().splitlines()[0], "sementes": SEM, "partidas_por_par_por_semente": 20,
        "criterio": f"maior taxa media de especie <= {LIMITE}; o coeficiente mais proximo do original",
        "original": {"hp_por_vigor": CONFIG_COMBATE_V21.hp_por_vigor, "hp_base": CONFIG_COMBATE_V21.hp_base},
        "varredura": linhas, "escolha": escolha}, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print("escolha:", escolha and (escolha["hp_por_vigor"], escolha["hp_base"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
