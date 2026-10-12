"""Gabarito das vidas com o banheiro LIGADO na area de antes, gravado com o codigo da main ANTES da BN-8 (origin/main 8cdb70f: o banheiro
no canto da casa, celulas x 0 a 3 e y 0 a 5, com a ida que continua do #270). Pedido do Gerente (2026-10-11): o banheiro vai para perto de
onde o pet passa o dia; "se os gabaritos do banheiro ligado mudarem, grave o antes".

A BN-8 so troca a area padrao (`ConfigBanheiro.celulas_x`, `celulas_y`). Entao estas vidas, rodadas depois com a area de antes dada
explicitamente (`CB_CANTO`, e `canto()` para a bancada), tem de sair iguais byte a byte: o 2 x 2 do banheiro pela bancada, o instinto e os
lobos direto (com o carinho e com o limpador) e o grupo de dois pets.

    python tests/gabarito_banheiro_perto.py      # grava tests/gabaritos/banheiro_perto_antes.json (so com o codigo de antes)
"""
from __future__ import annotations

import contextlib
import hashlib
import json
import sys
from dataclasses import replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import bancada_v2 as bv  # noqa: E402
import gabarito_mundo as gm  # noqa: E402
from digilab.config import CONFIG_BANHEIRO_LIGADA, CONFIG_GRUPO_LIGADA, CONFIG_MUNDO_LIGADA  # noqa: E402

ARQUIVO = RAIZ / "tests" / "gabaritos" / "banheiro_perto_antes.json"
# o banheiro do #265 (BN-3 da etapa 3), no canto da casa: a area de antes da BN-8
CB_CANTO = replace(CONFIG_BANHEIRO_LIGADA, celulas_x=(0, 3), celulas_y=(0, 5))
DIAS = 3
SEMENTES = (101, 202, 303)
BRACOS = ("P0-B00", "P1-B0C", "P0-BL0", "P1-BLC")


@contextlib.contextmanager
def canto():
    """a bancada com o banheiro de antes (ela le a `CONFIG_BANHEIRO_LIGADA` do proprio modulo)"""
    antes = bv.CONFIG_BANHEIRO_LIGADA
    bv.CONFIG_BANHEIRO_LIGADA = CB_CANTO
    try:
        yield
    finally:
        bv.CONFIG_BANHEIRO_LIGADA = antes


def _sha(x) -> str:
    return hashlib.sha256(json.dumps(x, sort_keys=True, default=repr).encode()).hexdigest()


def impressao(motor, interacoes=None) -> dict:
    d = gm.impressao(motor, interacoes)
    d["fisico"] = _sha(motor.resumo_mundo_fisico())
    return d


def casos():
    for braco in BRACOS:
        for cerebro in ("lobos", "instinto") if braco.startswith("P0") else ("lobos",):
            for s in SEMENTES:
                yield f"bancada|{braco}~{cerebro}|{s}", ("bancada", (braco, cerebro, s))
    for cerebro in ("instinto", "lobos"):
        for limpador in (False, True):
            for s in SEMENTES:
                yield f"direto|{cerebro}|limpador={limpador}|{s}", ("direto", (cerebro, limpador, s))
    for s in (303, 404):
        yield f"grupo|{s}", ("grupo", s)


def vida(tipo: str, arg, cbh=None):
    """as vidas; `cbh` e o banheiro dos casos diretos e do grupo (a bancada usa o do modulo dela)"""
    import test_banheiro_mundo as tb
    from digilab.donos import criar_dono
    from digilab.grupo import PetDoGrupo, sementes_do_grupo, simular_grupo
    from digilab.mundo import DonoComLugar
    cbh = CONFIG_BANHEIRO_LIGADA if cbh is None else cbh
    if tipo == "bancada":
        braco, cerebro, s = arg
        v = bv.Bancada(DIAS, 16 * DIAS).vida(bv.EspecVida("atencioso", braco, s, None, "fisico", cerebro, lugar="comedouro"))
        return {None: (v.motor, v.interacoes)}
    if tipo == "direto":
        cerebro, limpador, s = arg
        cb = replace(cbh, limpador=limpador)
        fp = tb.fp_instinto(cb) if cerebro == "instinto" else tb.fp_lobos(cb)
        v, _ = tb.vida(fp, cb, semente=s, dias=DIAS, carinho=True)
        return {None: (v.motor, v.interacoes)}
    fabricas = {i: (tb.fp_instinto(cbh), tb.fm(cbh)) for i in ("A", "B")}
    sementes = sementes_do_grupo(arg, CONFIG_GRUPO_LIGADA.ids)
    pets = [PetDoGrupo(i, 0, fp, f, DonoComLugar(criar_dono("atencioso"), "perto", sementes[i], "atencioso", CONFIG_MUNDO_LIGADA),
                       "atencioso", "instinto") for i, (fp, f) in fabricas.items()]
    g = simular_grupo(CONFIG_MUNDO_LIGADA, arg, pets, 2)
    return {i: (g.motores[i], None) for i in ("A", "B")}


def registro(tipo: str, arg, cbh=None) -> dict:
    return {str(i): impressao(m, inter) for i, (m, inter) in vida(tipo, arg, cbh).items()}


def gerar() -> dict:
    return {chave: registro(*caso) for chave, caso in casos()}


if __name__ == "__main__":
    g = gerar()
    ARQUIVO.write_text(json.dumps(g, sort_keys=True, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"{ARQUIVO}: {len(g)} casos")
