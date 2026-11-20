"""Gabarito dos estilos `comedouro`, `perto` e `longe` do `DonoComLugar`, gravado com o codigo da main ANTES do estilo `longe_fixo` (C1,
etapa 1; docs/TAREFA_V2_LONGE_REGULAR.md, secoes 3.1 e 7). O estilo novo tem rng propria e nao pode mudar nenhum sorteio dos outros tres:
estas vidas, rodadas depois, tem de sair iguais byte a byte (o log, o estado, as acoes, as rngs, o estado da politica e os lugares onde
cada racao caiu).

    python tests/gabarito_lugar_estilos.py      # grava tests/gabaritos/lugar_estilos_antes.json (so com o codigo de antes)
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "tests"))

import gabarito_mundo as gm  # noqa: E402
from digilab.config import CONFIG_LOBOS_APRENDIZ, CONFIG_MUNDO_LIGADA, CONFIG_PADRAO  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.mundo import DonoComLugar, fabricas_mundo, simular_vida_mundo  # noqa: E402
from digilab.policies.lobos import PoliticaLobos  # noqa: E402

ARQUIVO = RAIZ / "tests" / "gabaritos" / "lugar_estilos_antes.json"
ESTILOS = ("comedouro", "perto", "longe")
DONOS = ("atencioso", "relapso")
SEMENTES = (101, 202, 303)
CEREBROS = ("instinto", "lobos")
DIAS = 3
ORCAMENTO = 48


def _sha(x) -> str:
    return hashlib.sha256(json.dumps(x, sort_keys=True, default=repr).encode()).hexdigest()


def casos():
    for cerebro in CEREBROS:
        for estilo in ESTILOS:
            for dono in DONOS:
                for s in SEMENTES:
                    yield f"{cerebro}|{estilo}|{dono}|{s}", (cerebro, estilo, dono, s)


def registro(cerebro: str, estilo: str, dono: str, semente: int) -> dict:
    pf = None if cerebro == "instinto" else (lambda cfg=None: PoliticaLobos(cfg or CONFIG_PADRAO, CONFIG_LOBOS_APRENDIZ))
    fp, fm = fabricas_mundo(CONFIG_MUNDO_LIGADA, politica_fabrica=pf)
    d = DonoComLugar(criar_dono(dono), estilo, semente, dono)
    v = simular_vida_mundo(dono, d, fp(CONFIG_PADRAO), semente, DIAS, ORCAMENTO, fm, rotulo_dono=dono)
    r = gm.impressao(v.motor, v.interacoes)
    r["lugares"] = _sha(d.lugares)
    r["n_lugares"] = len(d.lugares)
    return r


def gerar() -> dict:
    return {chave: registro(*caso) for chave, caso in casos()}


if __name__ == "__main__":
    g = gerar()
    ARQUIVO.write_text(json.dumps(g, sort_keys=True, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"{ARQUIVO}: {len(g)} casos")
