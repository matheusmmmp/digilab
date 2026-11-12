"""A fala do assistir (docs/futuro/fala_do_assistir.md, FA-2): os sinais do assistir lidos das vidas GRAVADAS da GV3 e da GV3b (adendo 2).

So le artefatos em disco: os `vidas.tar.gz` de `artifacts_v3_gosto_visual/gosto_visual/` (a GV3, o olhar sem o enjoo) e de
`artifacts_v3_gosto_visual/gosto_visual_enjoo2/` (a GV3b do adendo 2, o enjoo ligado, como o jogo v35+). Nenhuma vida nova, nenhuma semente
nova, nenhuma faixa: cada log e rejogado com as fabricas do orquestrador (`run_v3_gosto_visual.fabricas`, com a semente e o genoma da unidade
lidos do `meta.json` da run), e a vida rejogada e conferida contra o que a run gravou (o numero de decisoes e as `fracoes_olhando` de
`medidas.json`, bit a bit); uma divergencia levanta erro.

De cada decisao em que o pet olhava uma TV no intervalo que acabou (`motivo["olhar"]["olhava"]` nao nulo; "so enquanto o pet olha", FA-5) sai
uma linha com os sinais que o `dec-v4` le do motivo: o agrado, o agrado efetivo e o enjoo (so na GV3b), as urgencias do tedio e do susto, o
susto da decisao anterior e se houve tapa nos gestos. As vidas sao separadas por run, genoma e dono. As sondas das duas TVs NAO entram (sao
copias fora da vida).

    python artifacts_v3_gosto_visual/fala_limiares/extrair_sinais.py --processos 4     # grava sinais.json.gz nesta pasta
"""
from __future__ import annotations

import argparse
import gzip
import json
import sys
import tarfile
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

PASTA = Path(__file__).resolve().parent
RUNS = {"gv3": ("gosto_visual", False), "gv3b": ("gosto_visual_enjoo2", True)}   # nome -> (pasta da run, enjoo ligado)
SAIDA = PASTA / "sinais.json.gz"
MAX_PROCESSOS = 4                                    # V3-D8


def _vidas(pasta: str) -> list[tuple[str, str]]:
    """(nome, texto do log) de cada vida do tar, na ordem do nome; as sondas ficam fora"""
    out = []
    with tarfile.open(RAIZ / "artifacts_v3_gosto_visual" / pasta / "vidas.tar.gz", "r:gz") as t:
        for m in t.getmembers():
            if m.isfile() and m.name.endswith(".jsonl"):
                out.append((Path(m.name).stem, t.extractfile(m).read().decode("utf-8")))
    return sorted(out)


def _uma(args: tuple) -> dict:
    run, nome, texto, unidade, fr_gravadas, enjoo = args
    import run_v3_gosto_visual as G
    import run_v2_digibrain_prototipo as orq
    import sonda_duas_tvs as sd
    from digilab.events import LogDeEventos
    from digilab.genoma_visao import genoma_visao, genoma_visao_vazio
    from digilab.mundo import reproduzir_mundo

    genoma_tipo, dono, semente = nome.split("_")
    if int(semente) != unidade["semente"]:
        raise RuntimeError(f"{run}/{nome}: a unidade do meta nao e a da vida")
    g = genoma_visao(unidade["genoma"]) if genoma_tipo == "proprio" else genoma_visao_vazio()
    fp, fm = G.fabricas(unidade["semente"], g, enjoo)
    motor = reproduzir_mundo(LogDeEventos.de_jsonl(texto), fp, semente=unidade["semente"], fabrica_motor=fm)
    if motor.log.para_jsonl() != texto:
        raise RuntimeError(f"{run}/{nome}: o log rejogado nao e o gravado")
    dias = len(fr_gravadas)
    if G.fracoes_olhando(motor, dias) != fr_gravadas:
        raise RuntimeError(f"{run}/{nome}: as fracoes_olhando rejogadas divergem das de medidas.json")
    c = sd.cerebro_da_copia(motor)
    linhas, anterior = [], None
    for m in c.motivos:
        o = m["olhar"]
        if o["olhava"] is not None:
            u = m["afeto"]["urgencias"]
            linhas.append({"k": m["k"], "agrado": o["agrado"], "agrado_efetivo": o.get("agrado_efetivo"), "enjoo": o.get("enjoo"),
                           "tedio": u["tedio"], "susto": u["susto"],
                           "susto_anterior": None if anterior is None else anterior["afeto"]["urgencias"]["susto"],
                           "tapa": any(x[0] == "tapa" for x in m["gestos"]), "olha_depois": o["olha"] is not None,
                           "acao": m["acao"]})
        anterior = m
    return {"run": run, "vida": nome, "genoma_tipo": genoma_tipo, "dono": dono, "semente": unidade["semente"],
            "decisoes": len(c.motivos), "acordadas": sum(1 for m in c.motivos if m["acao"] != "dormir"), "olhava": linhas}


def tarefas() -> list[tuple]:
    out = []
    for run, (pasta, enjoo) in RUNS.items():
        base = RAIZ / "artifacts_v3_gosto_visual" / pasta
        meta = json.loads((base / "meta.json").read_text(encoding="utf-8"))
        medidas = json.loads((base / "medidas.json").read_text(encoding="utf-8"))
        unidades = {u["semente"]: u for u in meta["unidades"]}
        for nome, texto in _vidas(pasta):
            genoma_tipo, dono, semente = nome.split("_")
            out.append((run, nome, texto, unidades[int(semente)], medidas[f"{genoma_tipo}|{dono}|{semente}"]["fracoes_olhando"], enjoo))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--processos", type=int, default=MAX_PROCESSOS)
    a = ap.parse_args()
    if not 1 <= a.processos <= MAX_PROCESSOS:
        raise SystemExit(f"--processos de 1 a {MAX_PROCESSOS} (V3-D8)")
    ts = tarefas()
    with ProcessPoolExecutor(a.processos) as ex:
        vidas = list(ex.map(_uma, ts, chunksize=4))
    texto = json.dumps({"runs": {r: p for r, (p, _) in RUNS.items()}, "vidas": vidas}, sort_keys=True, separators=(",", ":")) + "\n"
    SAIDA.write_bytes(gzip.compress(texto.encode("utf-8"), compresslevel=9, mtime=0))
    print(f"{SAIDA}: {len(vidas)} vidas, {sum(len(v['olhava']) for v in vidas)} decisoes olhando")


if __name__ == "__main__":
    main()
