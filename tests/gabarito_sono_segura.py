"""Gabarito das vidas de hoje do DigiBrain modular antes do sono que segura (docs/TAREFA_V3_SONO_SEGURA.md; a regra da chave desligada).
Gravado com o codigo da main (0b319dd3) ANTES da `ConfigSonoSegura`, num commit proprio. Com a chave desligada (o padrao), estas vidas tem
de sair iguais, byte a byte.

O sono que segura mexe so no reflexo do sono do M-ARB (`Arbitragem.reflexo`), que o M-ADAPT passa ao M-ESTADO (a intencao suspensa, o
passeio, a redecisao por evento) e ao `escolher`. Por isso os bracos sao os que leem o reflexo por caminhos diferentes, todos do conserto:
  - `REL`: o braco do laboratorio e do jogo (o M3* com a memoria autobiografica, controle "rel");
  - `M3+S`: o M3* com a intencao suspensa (a L-2), que conta as decisoes de reflexo;
  - `M3R`: o M3* com a escolha refeita so por evento (a C3), em que o reflexo e evento;
  - `LAB+P`: o laboratorio com o passeio (a AN4), que acaba o passeio no reflexo.
Os quatro donos, o `longe_fixo` e o comedouro, as sementes 101 e 202 dos testes, 3 dias, pelo orquestrador do prototipo com as medidas do
conserto. De cada vida: o sha256 do log (o JSONL do motor), o do estado interno do cerebro e o das medidas, e o numero de decisoes (a
impressao do tests/gabarito_habito_intencao.py).

    python tests/gabarito_sono_segura.py     # grava tests/gabaritos/sono_segura_de_hoje.json (so com o codigo de antes da mudanca)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import gabarito_habito_intencao as H  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402

ARQUIVO = RAIZ / "tests" / "gabaritos" / "sono_segura_de_hoje.json"
SEMENTES = (101, 202)
DIAS = H.DIAS
BRACOS = ("REL", "M3+S", "M3R", "LAB+P")
LUGARES = ("longe_fixo", "comedouro")
DONOS = orq.DONOS


def gerar() -> dict:
    out = {}
    for braco in BRACOS:
        for semente in SEMENTES:
            for dono in DONOS:
                for lugar in LUGARES:
                    motor, reg, _ = orq.viver(braco, dono, lugar, semente, DIAS, orq.ORCAMENTO_POR_DIA, conserto=True)
                    out[f"{braco}|{dono}|{lugar}|{semente}"] = H.impressao(motor, reg, braco)
    return out


if __name__ == "__main__":
    ARQUIVO.write_text(json.dumps(gerar(), sort_keys=True, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(ARQUIVO)
