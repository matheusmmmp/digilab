"""Gabarito do G-PAR-CO7 e as vidas do G-ESCUDO (docs/ESPEC_V3_COOPERACAO_CO7.md, secao 6).

As vidas com a CO7 ligada (a ConfigCooperacao da CO7 no grupo e no cerebro do modular):
  - as tres da CO6a (experiments/exportar_gabarito_co6.py: o modular nos dois pets, 3 dias);
  - tres de 4 dias com o modular no pet A e o cerebro aleatorio no B (o do gabarito do mundo: emburra e anda muito, e chega perto da
    comida), para haver decisoes em que um outro aflito vai para a comida que o modular ve (D-CO7b-6). Os donos sao os atenciosos.

De cada decisao do modular: as entradas e as saidas das contas da CO7 (digilab/digibrain/dever.py): o `social` (a percepcao social, a
posicao e as posicoes de antes), a `situacao` (o que o pet ve, as urgencias e o k) com o `ajustar` dos pesos da escolha (as sondas repetem a
mesma conta e ficam de fora) e a `culpa_inveja`; e a escolha da decisao. O TS refaz cada conta com as mesmas entradas (o G-PAR-CO7,
web/app/test/cooperacao_co7.test.ts), e o Python conta o G-ESCUDO nelas (tests/test_cooperacao_co7.py).

    python experiments/exportar_gabarito_co7_par.py              # grava web/app/test/gabaritos/co7_python.json.gz
    python experiments/exportar_gabarito_co7_par.py --conferir   # refaz e compara com o gravado (falha alto se diferir)
"""
from __future__ import annotations

import argparse
import gzip
import json
import sys
from dataclasses import asdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import exportar_gabarito_co6 as e6  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402
from exportar_gabarito_mundo import CerebroAleatorio  # noqa: E402

from digilab.config import CONFIG_COOPERACAO_CO7, CONFIG_GRUPO_LIGADA, CONFIG_PADRAO  # noqa: E402
from digilab.digibrain import dever as dv  # noqa: E402
from digilab.digibrain.adapt import DigiBrain  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.grupo import PetDoGrupo, sementes_do_grupo, simular_grupo  # noqa: E402
from digilab.mundo import DonoComLugar  # noqa: E402

ARQUIVO = RAIZ / "web" / "app" / "test" / "gabaritos" / "co7_python.json.gz"
# (semente, cerebro de B, dias, lugar): o A e sempre o modular
VIDAS = ((101, "modular", 3, "comedouro"), (202, "modular", 3, "perto"), (303, "modular", 3, "comedouro"),
         (202, "aleatorio", 4, "perto"), (202, "aleatorio", 4, "comedouro"), (303, "aleatorio", 4, "perto"))


def _j(v):
    return json.loads(json.dumps(v, sort_keys=True, default=lambda o: o.para_dict() if hasattr(o, "para_dict") else repr(o)))


def grupo(semente: int, cerebro_b: str, dias: int, lugar: str, cco=CONFIG_COOPERACAO_CO7):
    cd = orq.config_do_braco(e6.BRACO, conserto=True)
    ss = sementes_do_grupo(semente, CONFIG_GRUPO_LIGADA.ids)
    pets = []
    for ident, cerebro in (("A", "modular"), ("B", cerebro_b)):
        _, fm = e6.fabricas("atencioso", ss[ident])
        if cerebro == "modular":
            fp = (lambda s: (lambda cfg=None: DigiBrain(cfg or CONFIG_PADRAO, cd, e6.CM, semente=s, cfg_cooperacao=cco)))(ss[ident])
        else:
            fp = lambda cfg=None: CerebroAleatorio(cfg or CONFIG_PADRAO)  # noqa: E731
        pets.append(PetDoGrupo(ident, 0, fp, fm, DonoComLugar(criar_dono("atencioso"), lugar, ss[ident], "atencioso", e6.CM),
                               "atencioso", cerebro))
    return simular_grupo(e6.CM, semente, pets, dias, cfg_cooperacao=cco)


def vida(v: tuple) -> dict:
    """a vida com as contas da CO7 gravadas, decisao a decisao, de cada pet do modular"""
    chamadas: list = []
    orig = {n: getattr(dv, n) for n in ("social", "situacao", "ajustar", "culpa_inveja")}
    pendente = {"ajustar": False}

    def social(ps, pos, antes, r):
        out = orig["social"](ps, pos, antes, r)
        chamadas.append({"f": "social", "ps": None if ps is None else _j(asdict(ps)), "pos": list(pos),
                         "antes": {i: list(p) for i, p in sorted(antes.items())}, "r": r, "out": _j(out)})
        return out

    def situacao(sens, urg, cfg, S):
        out = orig["situacao"](sens, urg, cfg, S)
        chamadas.append({"f": "situacao", "sens": _j({"social": sens["social"], "leitura": sens["leitura"], "pos": sens["pos"],
                                                       "objetos": [{k: o[k] for k in ("id", "tipo", "dx", "dy")} for o in sens["objetos"]]}),
                         "urgencias": _j(urg), "out": _j(out)})
        pendente["ajustar"] = True
        return out

    def ajustar(unidades, w, sit):
        out = orig["ajustar"](unidades, w, sit)
        if pendente["ajustar"]:                       # so o da escolha; as sondas repetem a mesma conta
            pendente["ajustar"] = False
            chamadas.append({"f": "ajustar", "chaves": _j([x["chave"] for x in unidades]), "w": list(w), "sit": _j(sit), "out": _j(out)})
        return out

    def culpa_inveja(sens, cfg):
        out = orig["culpa_inveja"](sens, cfg)
        chamadas.append({"f": "culpa_inveja", "sens": _j({"social": sens["social"], "leitura": sens["leitura"]}), "out": list(out)})
        return out

    for n, f in (("social", social), ("situacao", situacao), ("ajustar", ajustar), ("culpa_inveja", culpa_inveja)):
        setattr(dv, n, f)
    try:
        g = grupo(*v)
    finally:
        for n, f in orig.items():
            setattr(dv, n, f)
    semente, cerebro_b, dias, lugar = v
    escolhas = {i: [[m["acao"], m["escolha"], m["dever"]] for m in mt.politica.motivos]
                for i, mt in sorted(g.motores.items()) if getattr(mt.politica, "nome", None) == DigiBrain.nome}
    return {"semente": semente, "cerebro_b": cerebro_b, "dias": dias, "lugar": lugar, "chamadas": chamadas, "escolhas": _j(escolhas),
            "cooperacao": _j(g.resumo()["cooperacao"])}


def gerar() -> dict:
    return {"fonte": "experiments/exportar_gabarito_co7_par.py", "vidas": [vida(v) for v in VIDAS]}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--conferir", action="store_true", help="refaz e compara com o gabarito gravado")
    args = ap.parse_args()
    g = gerar()
    texto = json.dumps(g, sort_keys=True, separators=(",", ":"))
    if args.conferir:
        gravado = json.loads(gzip.decompress(ARQUIVO.read_bytes()).decode())
        if gravado != json.loads(texto):
            raise SystemExit(f"o gabarito do G-PAR-CO7 mudou: {ARQUIVO}")
        print(f"igual ao gravado: {ARQUIVO}")
        return
    ARQUIVO.write_bytes(gzip.compress(texto.encode(), mtime=0))
    for v in g["vidas"]:
        ds = [d for es in v["escolhas"].values() for _, _, d in es if d is not None]
        print(f"vida {v['semente']} {v['cerebro_b']} {v['lugar']}: {len(v['chamadas'])} chamadas; com o escudo valendo "
              f"{sum(1 for d in ds if d['proibidas'] and d['escudo'])}, reprovadas {sum(len(d['reprovadas']) for d in ds)}, "
              f"aprovadas {sum(1 for d in ds if d['aprovadas'])}, culpa {sum(1 for d in ds if d['culpa'])}, "
              f"inveja {sum(1 for d in ds if d['inveja'])}")
    print(f"gravado: {ARQUIVO} ({ARQUIVO.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
