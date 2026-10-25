"""O diagnostico de uma rodada da calibracao do DigiBrain modular (docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md, secao 6.1; o
adendo 1): rejoga do disco as vidas M3 da rodada (o log de cada uma, em vidas/M3/) e conta, so lendo:
  - nas racoes elegiveis que nao fecharam (a definicao de `cadeia_comida_corpo`), as 8 decisoes depois da posta: a acao, o reflexo do
    sono e se a racao estava entre as unidades;
  - no fim da vida, os pesos de habito em +-H_max por comportamento;
  - as intencoes que acabaram, pelo numero de decisoes e pelo motivo;
  - a fracao das decisoes com uma intencao em curso.
O cerebro do replay usa os valores da propria rodada (os `inatos` do meta.json), e as medidas refeitas de cada vida tem de ser as
gravadas no medidas.json da rodada (senao falha alto). Nada muda na vida. Grava diagnostico.json na pasta da rodada.

    python experiments/diagnostico_calibracao_digibrain.py artifacts_v2_digibrain_prototipo/calibracao/rodada_1
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402

from digilab.config import ConfigDigibrainInatos  # noqa: E402
from digilab.digibrain import DigiBrain  # noqa: E402


def _tuplas(v):
    return tuple(_tuplas(x) for x in v) if isinstance(v, list) else v


def inatos_da_rodada(meta: dict) -> ConfigDigibrainInatos:
    """os valores da rodada, do meta.json (o JSON troca as tuplas por listas)"""
    return ConfigDigibrainInatos(**{k: _tuplas(v) for k, v in meta["inatos"].items()})


def diagnosticar(pasta: Path) -> dict:
    meta = json.loads((pasta / "meta.json").read_text(encoding="utf-8"))
    cfg = meta["config"]
    if meta["fase"] != "calibracao":
        raise ValueError("o diagnostico e so da calibracao")
    passo = orq.CONFIG_PADRAO.intervalo_decisao_ticks
    inatos = inatos_da_rodada(meta)
    gravadas = json.loads((pasta / "medidas.json").read_text(encoding="utf-8"))
    falhas = {"acoes": Counter(), "reflexo": Counter(), "racao_entre_as_unidades": Counter(), "janelas": 0, "decisoes": 0}
    teto, total_h = Counter(), 0
    fins = Counter()
    com_intencao, decisoes = 0, 0
    for u in meta["unidades"]:
        s = u["semente"]
        for dono, lugar in orq.CELULAS:
            texto = (pasta / "vidas" / "M3" / f"{dono}_{lugar}_{s}.jsonl").read_text(encoding="utf-8")
            _, fm = orq.fabricas("M3", dono, s, cfg["dias"], cfg["orcamento_por_dia"])
            reg = orq.Registro(DigiBrain(orq.CONFIG_PADRAO, orq.config_do_braco("M3"), orq.CM, inatos=inatos), inatos.escala)
            motor = orq.reproduzir_mundo(orq.LogDeEventos.de_jsonl(texto), lambda c=None, reg=reg: reg, semente=s, fabrica_motor=fm)
            c = orq.cerebro_de(reg)
            refeitas = json.loads(json.dumps(orq.medidas(motor, reg, "M3", cfg["dias"])))
            antes = {k: v for k, v in gravadas[f"M3|{dono}|{lugar}|{s}"].items() if k in refeitas}
            if refeitas != antes:
                raise RuntimeError(f"{dono}/{lugar}/{s}: o replay com os valores da rodada nao refaz as medidas gravadas")
            ms = c.motivos
            comidos = {x["id"]: x["tick"] for x in motor.consumos_mundo}
            for d in motor.deixadas:
                if d["tipo"] != "racao":
                    continue
                k0 = -(-d["tick"] // passo)
                if k0 >= len(ms) or reg.estados[k0][0] >= orq.G_MVP["fome_elegivel"]:
                    continue
                if d["id"] in comidos and comidos[d["id"]] <= d["tick"] + orq.G_MVP["w_decisoes"] * passo:
                    continue
                falhas["janelas"] += 1
                for m in ms[k0:k0 + orq.G_MVP["w_decisoes"]]:
                    falhas["decisoes"] += 1
                    falhas["acoes"][m["acao"]] += 1
                    falhas["reflexo"][m["reflexo"]] += 1
                    falhas["racao_entre_as_unidades"][any(x["chave"][:2] == ["comer", "comida"] and x["chave"][2] == d["id"]
                                                          for x in m["unidades"])] += 1
            for b, linha in c.m.plast.H.items():
                teto[b] += sum(1 for v in linha if abs(v) == c.inatos.h_max)
                total_h += len(linha)
            for m in ms:
                decisoes += 1
                com_intencao += m["estado"]["I"] is not None
                for f in m["fins"]:
                    fins[f"{f['motivo']}|{f['n']}"] += 1
    n = falhas["decisoes"]
    return {"rodada": cfg.get("rodada"), "pasta": orq.rc._relativo(pasta),
            "falhas": {"janelas": falhas["janelas"], "decisoes": n,
                       "frac_reflexo": falhas["reflexo"][True] / n if n else None,
                       "frac_racao_entre_as_unidades": falhas["racao_entre_as_unidades"][True] / n if n else None,
                       "acoes": {a: x / n for a, x in sorted(falhas["acoes"].items())} if n else {}},
            "habito_no_teto": {"por_comportamento": dict(sorted(teto.items())), "total": sum(teto.values()), "pesos": total_h},
            "intencoes_que_acabaram": dict(sorted(fins.items())),
            "frac_decisoes_com_intencao": com_intencao / decisoes}


if __name__ == "__main__":
    pasta = Path(sys.argv[1])
    d = diagnosticar(pasta)
    bv._gravar(pasta / "diagnostico.json", bv._dump(d))
    print(json.dumps({k: v for k, v in d.items() if k != "intencoes_que_acabaram"}, indent=1, ensure_ascii=False))
