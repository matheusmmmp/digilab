"""Gabarito da LIMPEZA (docs/TAREFA_V3_LIMPEZA.md, a LZ1): as vidas do modular pelo caminho da LONGE_GEOMETRIA, gravadas com o codigo da
main (58a22928) ANTES de a LZ2 mexer na cadeia de motores e nas pecas que o modular importa do A. Depois da LZ2, da LZ3 e da LZ4, estas
vidas tem de sair iguais, byte a byte.

O gabarito do conserto (tests/gabarito_digibrain_conserto.py) ja cobre o modular nas 12 celulas de hoje (comedouro, perto e longe) pelo
orquestrador do prototipo. Este cobre o que ele nao cobre:
  - o MotorGravaCorpo da C1 (o motor das runs da C1 a C4 e da LONGE_GEOMETRIA);
  - os lugares `longe_um`, `longe_fixo`, `longe_ancora` e `longe` do DonoComLugar;
  - os quatro bracos da LONGE_GEOMETRIA (o PAD, que e o REL da C4 com a memoria autobiografica, o M3*, o M2 e o M0);
  - os quatro donos, com as sementes dos testes.

De cada vida: o sha256 do log (o JSONL do motor), o do estado interno do cerebro, o das medidas do orquestrador (sem o `custo`, que e o
relogio), o dos lugares postos pelo dono e o numero de decisoes.

    python tests/gabarito_limpeza_lg.py     # grava tests/gabaritos/limpeza_lg_de_hoje.json (so com o codigo de antes da LZ2)
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import run_v2_digibrain_prototipo as orq  # noqa: E402
import run_v3_longe_geometria as lg  # noqa: E402

ARQUIVO = RAIZ / "tests" / "gabaritos" / "limpeza_lg_de_hoje.json"
SEMENTES = (101, 202)
DIAS = 2
BRACOS = lg.BRACOS
LUGARES = ("longe_um", "longe_fixo", "longe_ancora", "longe")


def _sha(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def _texto(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def impressao(braco: str, dono: str, lugar: str, semente: int) -> dict:
    motor, registro, _fab, d = lg.viver(braco, dono, lugar, semente, DIAS, lg.ORCAMENTO_POR_DIA)
    c = orq.cerebro_de(registro)
    return {"log": _sha(motor.log.para_jsonl()), "estado": _sha(_texto(c.estado_interno())),
            "medidas": _sha(_texto(orq.medidas(motor, registro, lg.BRACO_DO_ORQ[braco], DIAS, True))),
            "lugares": _sha(_texto(lg.lugares_da_vida(d))), "decisoes": len(c.motivos)}


def gerar() -> dict:
    return {f"{b}|{dono}|{lugar}|{s}": impressao(b, dono, lugar, s)
            for b in BRACOS for s in SEMENTES for dono in orq.DONOS for lugar in LUGARES}


if __name__ == "__main__":
    ARQUIVO.write_text(json.dumps(gerar(), sort_keys=True, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(ARQUIVO)
