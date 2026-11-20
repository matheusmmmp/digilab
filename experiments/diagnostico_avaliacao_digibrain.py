"""O diagnostico do DigiBrain modular, a parte so com os artefatos (docs/PROPOSTA_DIAGNOSTICO_DIGIBRAIN_MODULAR.md, secao 3.1): refaz as
tabelas da secao 1 da proposta a partir do medidas.json da avaliacao unica (artifacts_v2_digibrain_prototipo/avaliacao/, no git). So
le: nenhuma vida, nenhum replay, nenhum gate. Cada numero e uma media por vida (as vidas de cada celula, salvo onde dito); a taxa da
cadeia e a media das taxas das vidas com racao elegivel, como no G-MVP.

    python experiments/diagnostico_avaliacao_digibrain.py
grava artifacts_v2_digibrain_prototipo/diagnostico/avaliacao.json
"""
from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402

ENTRADA = RAIZ / "artifacts_v2_digibrain_prototipo" / "avaliacao" / "medidas.json"
SAIDA = RAIZ / "artifacts_v2_digibrain_prototipo" / "diagnostico" / "avaliacao.json"
BRACOS_HABITO = ("M0", "M1", "M2", "M3")              # a secao 1.4: o indice "ganhou, fica" nos bracos sem e com o P2
BRACOS_MEMORIA = ("M3", "M3-sp", "M4", "M4-con", "M4-emb")


def _media(xs) -> float | None:
    xs = [x for x in xs if x is not None]
    return statistics.fmean(xs) if xs else None


def _frac_com_cadeia(vs: list[dict]) -> dict:
    sel = [v["com_cadeia"] for v in vs if v["com_cadeia"] is not None]
    return {"frac": sum(sel) / len(sel) if sel else None, "vidas_com_elegivel": len(sel), "vidas": len(vs)}


def _decisoes(v: dict) -> int:
    return sum(v["acoes"].values())


def _frac_dormir(vs: list[dict]) -> float:
    return statistics.fmean(v["acoes"].get("dormir", 0) / _decisoes(v) for v in vs)


def celula(vs: list[dict]) -> dict:
    """a linha da tabela 1.1 de uma celula"""
    return {"vidas": len(vs), "refeicoes_por_dia": _media(v["cadeia"]["refeicoes_por_dia"] for v in vs),
            "privacao": _media(v["privacao"] for v in vs), "elegiveis": _media(v["cadeia"]["elegiveis"] for v in vs),
            "fechadas": _media(v["cadeia"]["fechadas"] for v in vs), "taxa": _media(v["cadeia"]["taxa"] for v in vs),
            "com_cadeia": _frac_com_cadeia(vs), "dormir": _frac_dormir(vs)}


def diagnosticar(medidas: dict) -> dict:
    por: dict = {}
    for v in medidas.values():
        por.setdefault((v["braco"], v["dono"], v["lugar"]), []).append(v)
    decisoes = {_decisoes(v) for v in medidas.values()}
    if len(decisoes) != 1:
        raise RuntimeError(f"vidas com numeros de decisoes diferentes: {sorted(decisoes)}")

    def vidas(braco: str, dono: str | None = None, lugar: str | None = None) -> list[dict]:
        out = [v for (b, d, lu), vs in sorted(por.items()) if b == braco and dono in (None, d) and lugar in (None, lu) for v in vs]
        if not out:
            raise RuntimeError(f"nenhuma vida em {braco}/{dono}/{lugar}")
        return out

    # 1.1 e 1.2: a cadeia por celula, no M3
    cel = {f"{d}|{lu}": celula(vidas("M3", d, lu)) for d, lu in orq.CELULAS}
    longe = {d: {k: cel[f"{d}|longe"][k] for k in ("privacao", "taxa", "refeicoes_por_dia")} for d in orq.DONOS}
    # 1.3: o sono
    fecha = [k for k, c in cel.items() if c["com_cadeia"]["frac"] is not None and c["com_cadeia"]["frac"] >= 0.5]
    nao_fecha = [k for k in cel if k not in fecha]
    m3 = vidas("M3")
    sono = {"dormir_por_braco": {b: _frac_dormir(vidas(b)) for b in orq.BRACOS},
            "dormir_por_celula_m3": {k: c["dormir"] for k, c in cel.items()},
            "celulas_que_fecham": fecha, "celulas_que_nao_fecham": nao_fecha,
            "faixa_dormir_fecham": [min(cel[k]["dormir"] for k in fecha), max(cel[k]["dormir"] for k in fecha)] if fecha else None,
            "faixa_dormir_nao_fecham": [min(cel[k]["dormir"] for k in nao_fecha), max(cel[k]["dormir"] for k in nao_fecha)],
            "reflexos_por_vida_m3": _media(v["reflexos"] for v in m3),
            "frac_reflexo_m3": _media(v["reflexos"] / _decisoes(v) for v in m3)}
    # 1.4: o indice "ganhou, fica" por lugar
    habito = {}
    for b in BRACOS_HABITO:
        habito[b] = {"todas": {k: _media(v["repeticao"][k] for v in vidas(b)) for k in ("indice", "p_pos", "p_nao_pos")}}
        for lu in orq.LUGARES:
            habito[b][lu] = {k: _media(v["repeticao"][k] for v in vidas(b, lugar=lu)) for k in ("indice", "p_pos", "p_nao_pos")}
    habito["M2-M1"] = {lu: habito["M2"][lu]["indice"] - habito["M1"][lu]["indice"] for lu in ("todas",) + orq.LUGARES}
    # 1.5: a persistencia
    pers = {}
    for b in ("M3-sp", "M3"):
        vs = vidas(b)
        fins: dict = {}
        for v in vs:
            for m, n in v["fins"].items():
                fins[m] = fins.get(m, 0) + n
        pers[b] = {"intencoes_com_meta": _media(v["intencoes_com_meta"] for v in vs),
                   "fins_por_vida": {m: n / len(vs) for m, n in sorted(fins.items())}}
    # 1.6: as visitas ao lugar lembrado
    visitas = {b: {"visitas_por_vida": _media(v["visitas_lugar_lembrado"] for v in vidas(b)),
                   "vazias_por_vida": _media(v["visitas_vazias"] for v in vidas(b)),
                   "vidas_com_toda_visita_vazia": sum(1 for v in vidas(b) if v["visitas_vazias"] == v["visitas_lugar_lembrado"])
                   / len(vidas(b))}
               for b in BRACOS_MEMORIA}
    return {"fonte": orq.rc._relativo(ENTRADA), "proposta": "docs/PROPOSTA_DIAGNOSTICO_DIGIBRAIN_MODULAR.md, secao 1",
            "vidas": len(medidas), "decisoes_por_vida": decisoes.pop(),
            "1.1_cadeia_por_celula_m3": cel, "1.2_longe_m3": longe, "1.3_sono": sono, "1.4_ganhou_fica": habito,
            "1.5_persistencia": pers, "1.6_visitas": visitas}


if __name__ == "__main__":
    d = diagnosticar(json.loads(ENTRADA.read_text(encoding="utf-8")))
    bv._gravar(SAIDA, bv._dump(d))
    print(json.dumps(d, indent=1, ensure_ascii=False)[:6000])
