"""Gabarito do SOCIAL_PAR MD1 (docs/PLANO_ANALISE_V3_SOCIAL_PAR_MD.md, secao 8): as vidas de hoje do pet com as unidades sociais (o M1),
com e sem a companhia (o M2), gravadas com o codigo de ANTES da subchave do incentivo social em 0, num commit proprio. Com a subchave
desligada, estas vidas tem de sair iguais, byte a byte (o G2).

As vidas (so as sementes dos testes), com os helpers do gabarito do M2 (`tests/gabarito_social_m2.py`):
  - `sozinho|M1|<semente>`: o pet com o M1 sozinho, 3 dias;
  - `par|<braco>|<mecanismo>|<semente>`: a vida VIVO do par da S3 (C ou B1), 5 dias, com o M1 ou o M1+M2.

    python tests/gabarito_social_md.py     # grava tests/gabaritos/social_md_de_hoje.json (so com o codigo de antes)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "tests"))

import gabarito_social_m2 as m2  # noqa: E402
from digilab.config import CONFIG_COMPANHIA_LIGADA  # noqa: E402

ARQUIVO = RAIZ / "tests" / "gabaritos" / "social_md_de_hoje.json"
SEMENTES = m2.SEMENTES
BRACOS = m2.BRACOS
M1 = {"unidades_sociais": True}
COMP = {"cfg_companhia": CONFIG_COMPANHIA_LIGADA}
MECANISMOS = {"M1": (M1, None), "M1+M2": (M1, COMP)}


def gerar() -> dict:
    out = {f"sozinho|M1|{sm}": m2.impressao_sozinho(sm, M1) for sm in SEMENTES}
    out.update({f"par|{b}|{nome}|{sm}": m2.impressao_grupo(m2.vida_par(b, sm, cd, mk).grupo)
                for b in BRACOS for nome, (cd, mk) in MECANISMOS.items() for sm in SEMENTES})
    return out


if __name__ == "__main__":
    if ARQUIVO.exists():
        raise SystemExit(f"{ARQUIVO} ja existe: o gabarito e gravado uma vez, com o codigo de antes da subchave")
    ARQUIVO.write_text(json.dumps(gerar(), sort_keys=True, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(ARQUIVO)
