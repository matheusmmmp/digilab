"""Gabarito das vidas de hoje para o P1 do GOSTO_VISUAL (docs/ESPEC_GOSTO_VISUAL_P1.md, secao 8; a etapa P1a). Gravado com o codigo de
antes de qualquer peca do P1 (o orgao da tela, a TV, o evento `sentido_tela`, o `GenomaVisao`, o comportamento `olhar`), num commit
proprio. Com todas as chaves do P1 desligadas (o padrao), estas vidas tem de sair iguais depois, byte a byte.

Duas familias, as que o P1 toca:
  - o modular: o braco LAB da C4 (`run_v3_acoes_novas.viver`, o motor que grava o corpo, o mundo fisico e o corpo ligados) no comedouro,
    com os quatro donos e as cinco sementes dos testes; de cada vida, o sha256 do log, do estado interno do cerebro, das medidas do
    orquestrador e das medidas do corpo, e o numero de decisoes (a impressao do gabarito da DC3);
  - o A com o corpo e o mundo fisico: a bancada `completa` no mundo `fisico`, o braco P1 com os lobos, os dois donos e as cinco sementes;
    a impressao do gabarito do corpo no mundo (o registro do mundo fisico inteiro incluido).

    python tests/gabarito_gosto_visual.py     # grava tests/gabaritos/gosto_visual_vidas_de_hoje.json (so com o codigo de antes)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import bancada_v2 as bv  # noqa: E402
import gabarito_conversa_dc3 as dc3  # noqa: E402
import gabarito_corpo_mundo as cm  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402
import run_v3_acoes_novas as an  # noqa: E402

ARQUIVO = RAIZ / "tests" / "gabaritos" / "gosto_visual_vidas_de_hoje.json"
SEMENTES = (101, 202, 303, 404, 505)
DIAS = dc3.DIAS
DONOS_A = ("atencioso", "aleatorio")


def casos():
    for semente in SEMENTES:
        for dono in orq.DONOS:
            yield f"modular|LAB|{dono}|comedouro|{semente}", ("modular", dono, semente)
        for dono in DONOS_A:
            yield f"A|completa|fisico|P1~lobos|{dono}|comedouro|{semente}", ("A", dono, semente)


def vida_de_hoje(familia: str, dono: str, semente: int) -> dict:
    if familia == "modular":
        motor, reg, _, _ = an.viver(dc3.BRACO, dono, dc3.LUGAR, semente, DIAS, orq.ORCAMENTO_POR_DIA)
        return dc3.impressao(motor, reg)
    if familia == "A":
        return cm.vida_de_hoje("completa", bv.EspecVida(dono, "P1", semente, None, "fisico", "lobos", "comedouro"))
    raise ValueError(f"familia desconhecida: {familia!r}")


def gerar() -> dict:
    return {chave: vida_de_hoje(*caso) for chave, caso in casos()}


if __name__ == "__main__":
    g = gerar()
    ARQUIVO.write_text(json.dumps(g, sort_keys=True, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"{ARQUIVO}: {len(g)} vidas")
