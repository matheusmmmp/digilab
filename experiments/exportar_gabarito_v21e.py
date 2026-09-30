"""Gabarito de paridade Python x web do combate V21E (equilibrio geral, fase 1; docs/EQUILIBRIO_GERAL.md): partidas jogadas no
Python com a variante escolhida (experiments/configs/v21e/calibracao.json: as regras da validacao V21C, as quatro chaves da
V21D validada e as cinco da ConfigCombateV21E), que e o combate dos pets v9 na web.

Mesmos confrontos, lutadores e sementes do gabarito da V21D (experiments/exportar_gabarito_v21d.py): os 36 pares das 8 formas
adultas em duas combinacoes de especie, os 4 adolescentes contra as 8 formas adultas e as 4 sombrias contra as 8 formas
adultas, com a semente derivar_semente("gabarito-v21d", n). Assim o resumo diz quantas partidas mudam da V21D para a V21E.
Cada partida grava os dois lutadores, o perfil de cada um, os turnos (acao e motivo dos dois lados), o sha256 dos turnos e o
fim. O teste web (web/app/test/paridade_v21e.test.ts) refaz cada partida no TS: as decisoes por regra, a leitura do vigia e a
resolucao sao do TS; so as acoes de exploracao (epsilon) vem do gabarito.

So le digilab/: nada no pacote muda.

uso: python experiments/exportar_gabarito_v21e.py [saida.json]
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import exportar_gabarito_v21d as v21d  # noqa: E402
import run_bateria_v21 as rb  # noqa: E402
from digilab.combate_v2.v21 import bots  # noqa: E402
from digilab.combate_v2.v21.partida import jogar  # noqa: E402
from digilab.config import ConfigCombateV21E  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402

SAIDA = RAIZ / "web" / "app" / "test" / "gabaritos" / "combate_v21e_python.json"
CFG_V21E = RAIZ / "experiments" / "configs" / "v21e" / "calibracao.json"
FORMAS_COM_LISTA_NOVA = ("duelista", "espelho", "muralha", "vigia", "tita")


def cfg() -> dict:
    c = rb.carregar(v21d.CFG_V21C)
    e = json.loads(CFG_V21E.read_text(encoding="utf-8"))
    return {**c, "regras_v21": {**c["regras_v21"], **e["regras_v21"]}}


def regras():
    r = rb.regras_de(cfg())
    if type(r.v21) is not ConfigCombateV21E:
        raise RuntimeError(f"config v21e montou {type(r.v21).__name__}")
    return r


def gerar() -> dict:
    r = regras()
    partidas = []
    for n, (da, db) in enumerate(v21d.confrontos()):
        a, b = v21d.lutador(da, r), v21d.lutador(db, r)
        semente = derivar_semente("gabarito-v21d", n)
        p = jogar(a, b, semente, r)
        txt = v21d.turnos_texto(p.log)
        fim = p.log[-1]
        partidas.append({
            "variante": "v21e", "n": n, "semente": str(semente), "a": da, "b": db,
            "perfil_a": {k: getattr(a.perfil, k) for k in v21d.CAMPOS_PERFIL},
            "perfil_b": {k: getattr(b.perfil, k) for k in v21d.CAMPOS_PERFIL},
            "epsilon": [a.epsilon, b.epsilon],
            "turnos": txt, "sha256_turnos": hashlib.sha256(txt.encode("utf-8")).hexdigest(),
            "pontos_a": p.pontos_a, "motivo": p.motivo_fim, "n_turnos": p.turnos,
            "hp_a": fim["hp_a"], "hp_b": fim["hp_b"]})
    antes = [p for p in json.loads(v21d.SAIDA.read_text(encoding="utf-8"))["partidas"] if p["variante"] == "a_c_e2v_v"]
    if [(p["n"], p["semente"]) for p in antes] != [(p["n"], p["semente"]) for p in partidas]:
        raise RuntimeError("o gabarito da V21D nao tem os mesmos confrontos e sementes")
    e = json.loads(CFG_V21E.read_text(encoding="utf-8"))
    return {"nota": "paridade Python x web do combate V21E (pets v9; docs/EQUILIBRIO_GERAL.md, fase 1); gerado por "
                    "experiments/exportar_gabarito_v21e.py. Turnos: 'a,ma,b,mb' separados por ';' (ma/mb: indice da "
                    "regra, 'exploracao' ou 'pesado_automatico'). Mesmos confrontos e sementes do gabarito da V21D",
            "chaves_v21e": e["regras_v21"], "hashes": rb.hashes(cfg()),
            "listas_v21e": {f: bots.gambits_adulto(f, r.v21).para_dict() for f in FORMAS_COM_LISTA_NOVA},
            "partidas": partidas,
            "resumo": {"partidas": len(partidas),
                       "com_exploracao": sum("exploracao" in x["turnos"] for x in partidas),
                       "diferentes_da_v21d": sum(x["sha256_turnos"] != y["sha256_turnos"] for x, y in zip(partidas, antes))}}


def main() -> int:
    saida = Path(sys.argv[1]) if len(sys.argv) > 1 else SAIDA
    g = gerar()
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text(json.dumps(g, ensure_ascii=False, indent=0) + "\n", encoding="utf-8", newline="\n")
    print(f"{saida}: {len(g['partidas'])} partidas; {g['resumo']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
