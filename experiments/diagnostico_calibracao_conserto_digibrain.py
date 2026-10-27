"""O diagnostico de uma rodada da calibracao do conserto (docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md, A3.11): rejoga do disco as
vidas M3* da rodada (o log de cada uma, em vidas/M3/), com os valores da propria rodada (os `inatos` do meta.json), e conta, so lendo:
  - o incentivo de cada classe antes da proximidade (o `Plasticidade.incentivo`): o valor, os zeros e os que batem no G_max;
  - a fracao das decisoes com uma intencao em curso, por tipo (o limite do que a persistencia pode decidir);
  - os termos medios da unidade escolhida (inato, habito, memoria, incentivo, persistencia), por terco da vida.
As medidas refeitas de cada vida tem de ser as gravadas no medidas.json da rodada (senao falha alto). Nada muda na vida. Grava
diagnostico.json na pasta da rodada.

    python experiments/diagnostico_calibracao_conserto_digibrain.py artifacts_v2_digibrain_prototipo/conserto/calibracao/rodada_1
"""
from __future__ import annotations

import json
import statistics
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402

# os termos do M-IMPULSO, na ordem dos motivos (o pacote do cerebro so e citado pelo orquestrador: T-PONTO-3)
TERMOS = ("inato", "prox", "nov", "incentivo", "habito", "memoria", "persistencia")


def _espiar(plast, anotar: list) -> None:
    """troca, so nesta instancia do M-PLAST, o `incentivo` por um que devolve o mesmo valor e anota (classe, valor, no teto)"""
    original = plast.incentivo

    def incentivo(pc, classe, drives):
        out = original(pc, classe, drives)
        if plast.cd.p1:
            anotar.append((classe, out, out == plast.p.g_max_incentivo))
        return out

    plast.incentivo = incentivo


def _quantil(xs: list, q: float):
    return xs[min(len(xs) - 1, int(len(xs) * q))]


def diagnosticar(pasta: Path) -> dict:
    meta = json.loads((pasta / "meta.json").read_text(encoding="utf-8"))
    cfg = meta["config"]
    if meta["fase"] != "calibracao_conserto":
        raise ValueError("o diagnostico e so da calibracao do conserto")
    inatos = orq.inatos_do_meta(meta)
    gravadas = json.loads((pasta / "medidas.json").read_text(encoding="utf-8"))
    intencoes, decisoes = Counter(), 0
    termos = {t: {terco: [] for terco in range(3)} for t in TERMOS}
    incentivos: list = []
    for u in meta["unidades"]:
        s = u["semente"]
        for dono, lugar in orq.CELULAS:
            texto = (pasta / "vidas" / "M3" / f"{dono}_{lugar}_{s}.jsonl").read_text(encoding="utf-8")
            fp, fm = orq.fabricas("M3", dono, s, cfg["dias"], cfg["orcamento_por_dia"], inatos=inatos, conserto=True)
            reg = fp(None)
            _espiar(orq.cerebro_de(reg).m.plast, incentivos)
            motor = orq.reproduzir_mundo(orq.LogDeEventos.de_jsonl(texto), lambda c=None, reg=reg: reg, semente=s,
                                         fabrica_motor=fm)
            c = orq.cerebro_de(reg)
            refeitas = json.loads(json.dumps(orq.medidas(motor, reg, "M3", cfg["dias"], conserto=True)))
            antes = {k: v for k, v in gravadas[f"M3|{dono}|{lugar}|{s}"].items() if k in refeitas}
            if refeitas != antes:
                raise RuntimeError(f"{dono}/{lugar}/{s}: o replay com os valores da rodada nao refaz as medidas gravadas")
            ms = c.motivos
            for m in ms:
                decisoes += 1
                I = m["estado"]["I"]
                if I is not None:
                    intencoes[f"{I[0]}/{I[1]}"] += 1
                escolhida = next((x for x in m["unidades"] if x["chave"] == m["escolha"]), None)
                if escolhida is not None:
                    if tuple(escolhida["termos"]) != TERMOS:
                        raise RuntimeError(f"os termos do motivo mudaram: {tuple(escolhida['termos'])}")
                    terco = min(2, 3 * m["k"] // len(ms))
                    for t in TERMOS:
                        termos[t][terco].append(escolhida["termos"][t])
    incentivo = {}
    for classe in sorted({x[0] for x in incentivos}):
        vs = sorted(x[1] for x in incentivos if x[0] == classe)
        incentivo[classe] = {"n": len(vs), "zero": sum(1 for v in vs if v == 0),
                             "no_teto": sum(1 for x in incentivos if x[0] == classe and x[2]),
                             "mediana": _quantil(vs, 0.5), "p90": _quantil(vs, 0.9), "max": vs[-1]}
    return {"rodada": cfg["rodada"], "inatos": meta["inatos"], "vidas": len(gravadas), "decisoes": decisoes,
            "incentivo_antes_da_proximidade": incentivo,
            "intencao_em_curso": {"frac": sum(intencoes.values()) / decisoes, "por_tipo": dict(intencoes)},
            "termos_da_escolhida_por_terco": {t: [statistics.fmean(v) if v else None for v in (por[0], por[1], por[2])]
                                              for t, por in termos.items()}}


def main() -> None:
    pasta = Path(sys.argv[1])
    out = diagnosticar(pasta)
    bv._gravar(pasta / "diagnostico.json", bv._dump(out))
    print(json.dumps({k: v for k, v in out.items() if k != "inatos"}, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
