"""Gabarito das vidas com o banheiro LIGADO, gravado com o codigo da main ANTES da continuacao do alvo `banheiro` (origin/main b09793a, o
banheiro do #265). Pedido do Gerente (2026-10-11): "se o gabarito do banheiro ligado mudar, grave o antes e explique".

Com a continuacao, o `aliviar` com o alvo `banheiro` que nao chega ao banheiro deixa de aliviar no caminho: segura a vontade. Entao estas
vidas so podem mudar a partir da primeira decisao assim (a k*). Por vida, se ela tem uma k*, guarda o prefixo das decisoes do mundo antes
dela (sha256), a propria k* (tick, posicao, alvo) e os alivios antes; se nao tem, a impressao inteira (log, estado, rngs, registro do
mundo, estado interno), que tem de sair igual byte a byte.

    python tests/gabarito_banheiro_ligado.py      # grava tests/gabaritos/banheiro_ligado_antes.json (so com o codigo de antes)
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import bancada_v2 as bv  # noqa: E402
import gabarito_mundo as gm  # noqa: E402
import test_banheiro_mundo as tb  # noqa: E402
from digilab.config import CONFIG_GRUPO_LIGADA  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.grupo import PetDoGrupo, sementes_do_grupo, simular_grupo  # noqa: E402
from digilab.mundo import DonoComLugar  # noqa: E402

ARQUIVO = RAIZ / "tests" / "gabaritos" / "banheiro_ligado_antes.json"
DIAS = 3
SEMENTES = (101, 202, 303)
CBHS = {"B": tb.CB, "BL": tb.CBL, "perto": tb.CB_PERTO}
BRACOS = (("P0-B00", "lobos"), ("P1-B00", "lobos"), ("P1-BLC", "lobos"), ("P0-B0C", "instinto"))


def _sha(x) -> str:
    return hashlib.sha256(json.dumps(x, sort_keys=True, default=repr).encode()).hexdigest()


def k_estrela(motor) -> int | None:
    """o indice da primeira decisao do mundo que aliviou com o alvo `banheiro` fora do banheiro (o pet nao chegou), ou None"""
    ticks = {a["tick"] for a in motor.alivios if a["alvo"] == "banheiro" and not a["dentro"]}
    for k, d in enumerate(motor.decisoes_mundo):
        if d["acao"] == "aliviar" and d["tick"] in ticks:
            return k
    return None


def registro(motor, interacoes=None) -> dict:
    k = k_estrela(motor)
    if k is None:
        d = gm.impressao(motor, interacoes)
        d["fisico"] = _sha(motor.resumo_mundo_fisico())
        return {"k": None, "impressao": d, "alivios": len(motor.alivios)}
    dk = motor.decisoes_mundo[k]
    t = dk["tick"]
    return {"k": k, "prefixo": _sha(motor.decisoes_mundo[:k]), "decisao": [t, dk["antes"], dk["x"], dk["y"], dk["alvo"]],
            "alivios_antes": [a for a in motor.alivios if a["tick"] < t]}


def casos():
    for cerebro in ("instinto", "lobos"):
        for nome, cbh in CBHS.items():
            for s in SEMENTES:
                yield f"direto|{cerebro}|{nome}|{s}", ("direto", (cerebro, nome, s))
    for braco, cerebro in BRACOS:
        for s in SEMENTES:
            yield f"bancada|{braco}~{cerebro}|{s}", ("bancada", (braco, cerebro, s))
    for s in (303, 404):
        yield f"grupo|perto|{s}", ("grupo", s)


def vida_grupo(s: int):
    fabricas = {i: (tb.fp_instinto(tb.CB_PERTO), tb.fm(tb.CB_PERTO)) for i in ("A", "B")}
    sementes = sementes_do_grupo(s, CONFIG_GRUPO_LIGADA.ids)
    pets = [PetDoGrupo(i, 0, fp, f, DonoComLugar(criar_dono("atencioso"), "perto", sementes[i], "atencioso", tb.CM), "atencioso",
                       "instinto") for i, (fp, f) in fabricas.items()]
    return simular_grupo(tb.CM, s, pets, 2)


def vida_de_hoje(tipo: str, arg) -> dict:
    if tipo == "direto":
        cerebro, nome, s = arg
        cbh = CBHS[nome]
        fp = tb.fp_instinto(cbh) if cerebro == "instinto" else tb.fp_lobos(cbh)
        v, _ = tb.vida(fp, cbh, semente=s, dias=DIAS, carinho=True)
        return registro(v.motor, v.interacoes)
    if tipo == "bancada":
        braco, cerebro, s = arg
        v = bv.Bancada(DIAS, 16 * DIAS).vida(bv.EspecVida("atencioso", braco, s, None, "fisico", cerebro, lugar="comedouro"))
        return registro(v.motor, v.interacoes)
    g = vida_grupo(arg)
    return {i: registro(g.motores[i]) for i in ("A", "B")}


def gerar() -> dict:
    return {chave: vida_de_hoje(*caso) for chave, caso in casos()}


if __name__ == "__main__":
    g = gerar()
    ARQUIVO.write_text(json.dumps(g, sort_keys=True, indent=1) + "\n", encoding="utf-8", newline="\n")
    com_k = sum(1 for v in g.values() if ("k" in v and v["k"] is not None) or ("A" in v and any(v[i]["k"] is not None for i in "AB")))
    print(f"{ARQUIVO}: {len(g)} vidas, {com_k} com a k*")
