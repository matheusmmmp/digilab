"""O gabarito do decodificador `dec-v4` para a web (a fala do assistir, docs/futuro/fala_do_assistir.md, FA-2; DECIDIDA pelo Matheus em
2026-11-12): o TS (`web/app/motor/digibrain/decodificador.ts`, `decodificarV4`) decodifica os mesmos motivos e confere bit a bit
(`web/app/test/decodificador_v4.test.ts`). O gabarito do `dec-v1`/`dec-v2` (`exportar_decodificador.py`) nao muda.

O que vai no arquivo (`web/app/test/gabaritos/decodificador_v4_python.json.gz`):
  - a `ConfigFalaAssistir` e o catalogo do assistir;
  - `gabaritos`: a saida do `dec-v4` em toda decisao das vidas com o enjoo dos gabaritos que a web ja rejoga (`gosto_visual_enjoo.json.gz` e
    `tv_jogo.json.gz`, as vidas de um pet so); os motivos ficam la (o TS os le de la), e aqui so a saida, decisao a decisao;
  - `vidas`: vidas curtas da GV3b (o laboratorio com o olhar e o enjoo ligado, o orquestrador `run_v3_gosto_visual.viver`, 4 dias), nas
    sementes dos testes (101, 202 e 303, o genoma da visao da mesma semente, os donos `nenhum`, `calmo` e `agitado`). Delas vao os pares
    (anterior, motivo) das decisoes em que o pet olhava, mais uma decisao a cada 24 (o assistir nulo e os 12 conceitos com o olhar no
    catalogo), com a saida do `dec-v4`;
  - `sinteticos`: o primeiro motivo olhando da primeira vida com os sinais trocados (o agrado, o agrado efetivo, o enjoo, o tedio, o susto, o
    susto anterior e o tapa), numa grade e em combinacoes de uma rng propria do exportador (`gabarito-dec-v4`, so escolhe os sinais), para a
    paridade passar por todo ramo da conta.
Sementes dos testes; nao sao vidas de pesquisa e nenhuma faixa e reservada.

    python experiments/exportar_decodificador_v4.py        # grava web/app/test/gabaritos/decodificador_v4_python.json.gz
"""
from __future__ import annotations

import copy
import gzip
import json
import random
import sys
from dataclasses import asdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import run_v3_gosto_visual as G  # noqa: E402
import sonda_duas_tvs as sd  # noqa: E402

from digilab.config import CONFIG_FALA_ASSISTIR  # noqa: E402
from digilab.digibrain.decodificador import CATALOGO_ASSISTIR, decodificar_v4  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402

PASTA = RAIZ / "web" / "app" / "test" / "gabaritos"
ARQUIVO = PASTA / "decodificador_v4_python.json.gz"
GABARITOS = ("gosto_visual_enjoo.json.gz", "tv_jogo.json.gz")
SEMENTES = (101, 202, 303)
DIAS = 4
CADA = 24                                              # a decisao sem olhar que vai no gabarito: k % CADA == 0
SINAIS = ("agrado", "agrado_efetivo", "enjoo", "tedio", "susto", "susto_anterior")
N_COMBINACOES = 160


def _json(x):
    return json.loads(json.dumps(x))


def _decisoes_do_gabarito(nome: str) -> list[dict]:
    """a saida do dec-v4 em toda decisao das vidas de um pet so do gabarito (os motivos ficam no arquivo de la)"""
    with gzip.open(PASTA / nome, "rt", encoding="utf-8") as f:
        g = json.load(f)
    out = []
    for i, v in enumerate(g["vidas"]):
        ms = [d["motivo"] for d in v["decisoes"]]
        if [m["k"] for m in ms] != list(range(len(ms))):
            raise RuntimeError(f"{nome}, vida {i}: as decisoes nao sao 0..n-1")
        out.append({"arquivo": nome, "vida": i, "decisoes": [decodificar_v4(m, ms[k - 1] if k else None) for k, m in enumerate(ms)]})
    return out


def _vida(semente: int, dono: str) -> tuple[dict, list[dict]]:
    unidade = {"semente": semente, "genoma": semente}
    motor, _, _ = G.viver("proprio", dono, unidade, DIAS, enjoo=True)
    ms = [_json(m) for m in sd.cerebro_da_copia(motor).motivos]
    pares = []
    for k, m in enumerate(ms):
        if m["olhar"]["olhava"] is not None or k % CADA == 0:
            ant = ms[k - 1] if k else None
            pares.append({"anterior": ant, "motivo": m, "dec": decodificar_v4(m, ant)})
    return {"semente": semente, "dono": dono, "dias": DIAS, "decisoes": len(ms), "pares": pares}, ms


def _aplicar(base: dict, ant: dict, sinais: dict) -> tuple[dict, dict]:
    m, a = copy.deepcopy(base), copy.deepcopy(ant)
    o, u = m["olhar"], m["afeto"]["urgencias"]
    o["agrado"], o["agrado_efetivo"], o["enjoo"] = sinais["agrado"], sinais["agrado_efetivo"], sinais["enjoo"]
    u["tedio"], u["susto"] = sinais["tedio"], sinais["susto"]
    a["afeto"]["urgencias"]["susto"] = sinais["susto_anterior"]
    m["gestos"] = [["tapa", 0]] if sinais["tapa"] else []
    return m, a


def _sinteticos(par: dict) -> dict:
    base, ant = par["motivo"], par["anterior"]
    rng = random.Random(derivar_semente("gabarito-dec-v4", 101, 0))
    S = 1024
    neutro = {"agrado": 512, "agrado_efetivo": 512, "enjoo": 512, "tedio": 128, "susto": 0, "susto_anterior": 0, "tapa": False}
    casos = []
    for s in SINAIS:
        for x in range(0, S + 1, 64):
            casos.append({**neutro, s: x})
    for x in range(0, S + 1, 128):
        casos.append({**neutro, "susto": x, "susto_anterior": 0, "tapa": True})
    for _ in range(N_COMBINACOES):
        casos.append({**{s: rng.randrange(S + 1) for s in SINAIS}, "tapa": rng.random() < 0.2})
    saida = []
    for c in casos:
        m, a = _aplicar(base, ant, c)
        saida.append({"sinais": c, "dec": decodificar_v4(m, a)})
    return {"base": base, "anterior": ant, "casos": saida}


def gerar() -> dict:
    vidas, primeiro = [], None
    for s in SEMENTES:
        for dono in G.DONOS:
            v, _ = _vida(s, dono)
            vidas.append(v)
            if primeiro is None:
                primeiro = next((p for p in v["pares"] if p["motivo"]["olhar"]["olhava"] is not None and p["anterior"] is not None), None)
    if primeiro is None:
        raise RuntimeError("nenhuma decisao olhando nas vidas do gabarito")
    return {"versao": 1, "catalogo_assistir": list(CATALOGO_ASSISTIR), "config_fala_assistir": asdict(CONFIG_FALA_ASSISTIR),
            "gabaritos": [x for n in GABARITOS for x in _decisoes_do_gabarito(n)], "vidas": vidas, "sinteticos": _sinteticos(primeiro)}


def bytes_do_arquivo(g: dict | None = None) -> bytes:
    texto = json.dumps(g or gerar(), sort_keys=True, separators=(",", ":")) + chr(10)
    return gzip.compress(texto.encode("utf-8"), compresslevel=9, mtime=0)


if __name__ == "__main__":
    b = bytes_do_arquivo()
    ARQUIVO.write_bytes(b)
    print(f"{ARQUIVO} ({len(b) / 1024:.0f} KiB)")
