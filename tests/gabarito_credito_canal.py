"""Gabarito das vidas de hoje para a etapa 0 do credito por canal (docs/TAREFA_V2_V3_CREDITO_CANAL.md, secao 5): gravado com o codigo da
main ANTES da medicao das tabelas sombra. A medicao embrulha o cerebro so para ler; toda vida daqui tem de sair igual com o embrulho, o
estado interno incluido (G2). As vidas sao as do T1 do J5 na config da fumaca do piloto do adendo 8, com a duracao do piloto (7 + 5 dias),
nas sementes dos testes, nos dois bracos de base (P1 e P1-plan).

    python tests/gabarito_credito_canal.py      # grava tests/gabaritos/credito_canal_vidas_de_hoje.json (so com o codigo de antes)
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402

ARQUIVO = RAIZ / "tests" / "gabaritos" / "credito_canal_vidas_de_hoje.json"
CONFIG = RAIZ / "experiments" / "configs" / "v2_pet_que_pensa" / "fumaca_piloto_adendo8.json"
DURACAO = {"d_a": 7, "janela": 5}               # a do piloto do adendo 8 (experiments/configs/v2_pet_que_pensa/piloto_adendo8.json)
BRACOS = ("P1", "P1-plan")
SEMENTES = tuple(sorted(bv.SEMENTES_TESTE))     # so dos testes


def bancada():
    import run_v2_piloto_pet_que_pensa_adendo7 as p7
    cfg = {**json.loads(CONFIG.read_text(encoding="utf-8")), **DURACAO}
    return bv.bancada_pqp_da_config(p7.config_do_piloto(cfg))


def _sha(texto: str) -> str:
    return hashlib.sha256(texto.encode()).hexdigest()


def impressao(motor) -> dict:
    return {"log": _sha(motor.log.para_jsonl()),
            "resumo": _sha(json.dumps(bv.resumo_motor(motor), sort_keys=True, default=repr)),
            "politica": _sha(json.dumps(motor.politica.estado_interno(), sort_keys=True, default=repr))}


def casos():
    for braco in BRACOS:
        for s in SEMENTES:
            yield f"T1|{braco}|{s}", bv.EspecPQP(braco, "T1", s)


def gerar() -> dict:
    bp = bancada()
    return {chave: impressao(bp.vida(espec).motor) for chave, espec in casos()}


if __name__ == "__main__":
    if ARQUIVO.exists():
        raise SystemExit(f"{ARQUIVO} ja existe: o gabarito e gravado uma vez, com o codigo de antes")
    g = gerar()
    ARQUIVO.write_text(json.dumps(g, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(len(g), "vidas")
