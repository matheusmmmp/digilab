"""A análise da bancada da cooperacao (docs/PLANO_ANALISE_V3_COOPERACAO.md, secoes 3.3, 4 e 7; missao CB4): le as vidas do orquestrador
(experiments/run_v3_cooperacao_bancada.py) e aplica a regra de decisao escrita antes, sem nada escolhido depois.

  H-EMERGE  IC 95 % da diferenca pareada B1 - B0 na P1 todo acima de DELTA
  H-DOSE    a inclinacao pareada da P1 em D0, DM, B1 (dose 0, 1/2, 1) com o IC todo acima de 0, e as medias D0 <= DM <= B1
  H-REP     o pet A no B1 contra o RM: o IC da diferenca no k medio de A e na P1 de A, os dois todos acima de 0
  H-CUSTO   IC da diferenca B1 - B0 na P3 (a media dos dois pets) todo abaixo de EPSILON
  R-ESCUDO  descritivo: a diferenca media na P1 contra o B0 de B1E, B1U, B1A e B1
Cada hipotese le CONFIRMA, NAO CONFIRMA ou INCONCLUSIVO POR PREMISSA (menos de N_MIN vidas no contraste). Os ICs sao por bootstrap pareado
por semente, 10 000 reamostras, com a semente fixa do registro.

    python experiments/analisar_v3_cooperacao_bancada.py experiments/runs/cooperacao_bancada/principal.jsonl --saida resultado.json
"""
from __future__ import annotations

import argparse
import json
import random
import statistics as st
from pathlib import Path

DELTA = 0.10                  # CB-7
EPSILON = 0.02                # CB-7
N_MIN = 30                    # plano, secao 6
REAMOSTRAS = 10_000           # plano, 3.3
SEMENTE_BOOTSTRAP = 91000     # gravada no registro da analise (secao 10)
DOSES = (("D0", 0.0), ("DM", 0.5), ("B1", 1.0))


def ler(caminho: Path, sementes: set[int] | None = None) -> dict[int, dict[str, dict]]:
    """semente -> braco -> medidas; com `sementes`, so elas (a faixa principal), e uma vida repetida falha alto"""
    por: dict[int, dict[str, dict]] = {}
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        r = json.loads(linha)
        if sementes is not None and r["semente"] not in sementes:
            continue
        b = por.setdefault(r["semente"], {})
        if r["braco"] in b:
            raise ValueError(f"vida repetida: {r['semente']} {r['braco']}")
        b[r["braco"]] = r["medidas"]
    return por


def ic(valores: list[float], semente: int = SEMENTE_BOOTSTRAP) -> tuple[float, float, float]:
    """(a media, o limite de baixo, o de cima) do IC de 95 % por bootstrap da media"""
    rng = random.Random(semente)
    n = len(valores)
    medias = sorted(sum(valores[rng.randrange(n)] for _ in range(n)) / n for _ in range(REAMOSTRAS))
    return st.mean(valores), medias[int(0.025 * REAMOSTRAS)], medias[int(0.975 * REAMOSTRAS) - 1]


def _leitura(n: int, passa: bool) -> str:
    if n < N_MIN:
        return "INCONCLUSIVO POR PREMISSA"
    return "CONFIRMA" if passa else "NAO CONFIRMA"


def _k_medio(p5_pet: dict) -> float | None:
    ks = list(p5_pet["k_medio"].values())
    return sum(ks) / len(ks) if ks else None


def _p1_pet(m: dict, pet: str) -> float | None:
    p = m["P1_por_pet"][pet]
    return p["favoraveis"] / p["oportunidades"] if p["oportunidades"] else None


def _so_do_pet(m: dict, pet: str) -> dict:
    """as medidas vistas so pelo pet (o adendo 1, AD1-4): a P1 e a P3 dele"""
    return {**m, "P1": _p1_pet(m, pet), "P3": {pet: m["P3"][pet]}}


def analisar(por: dict[int, dict[str, dict]], pet: str | None = None) -> dict:
    """`pet`: so a P1 e a P3 desse pet (o adendo 1: o A); sem ele, as da CB4"""
    if pet is not None:
        por = {s: {b: _so_do_pet(m, pet) for b, m in bs.items()} for s, bs in por.items()}
    s_ord = sorted(por)
    out: dict = {"n_sementes": len(s_ord), "pet": pet}
    # H-EMERGE
    d = [por[s]["B1"]["P1"] - por[s]["B0"]["P1"] for s in s_ord if por[s]["B0"]["P1"] is not None and por[s]["B1"]["P1"] is not None]
    if d:
        m, lo, hi = ic(d)
        out["H-EMERGE"] = {"n": len(d), "diferenca": m, "ic": [lo, hi], "leitura": _leitura(len(d), lo > DELTA)}
    else:
        out["H-EMERGE"] = {"n": 0, "leitura": "INCONCLUSIVO POR PREMISSA"}
    # H-DOSE
    inclinacoes, por_dose = [], {b: [] for b, _ in DOSES}
    for s in s_ord:
        ys = [por[s][b]["P1"] for b, _ in DOSES]
        if any(y is None for y in ys):
            continue
        xs = [x for _, x in DOSES]
        mx, my = st.mean(xs), st.mean(ys)
        inclinacoes.append(sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs))
        for (b, _), y in zip(DOSES, ys):
            por_dose[b].append(y)
    if inclinacoes:
        m, lo, hi = ic(inclinacoes)
        medias = {b: st.mean(v) for b, v in por_dose.items()}
        ordem = medias["D0"] <= medias["DM"] <= medias["B1"]
        out["H-DOSE"] = {"n": len(inclinacoes), "inclinacao": m, "ic": [lo, hi], "medias": medias, "ordem": ordem,
                         "leitura": _leitura(len(inclinacoes), lo > 0 and ordem)}
    else:
        out["H-DOSE"] = {"n": 0, "leitura": "INCONCLUSIVO POR PREMISSA"}
    # H-REP: o pet A no B1 contra o RM (fora do adendo 1, AD1-3)
    if not all("RM" in por[s] for s in s_ord):
        out["H-REP"] = {"leitura": "FORA (sem o RM)"}
    else:
        out.update(_h_rep(por, s_ord))
    return _resto(out, por, s_ord, pet)


def _h_rep(por, s_ord) -> dict:
    out = {}
    dk = [_k_medio(por[s]["B1"]["P5"]["A"]) - _k_medio(por[s]["RM"]["P5"]["A"]) for s in s_ord
          if _k_medio(por[s]["B1"]["P5"]["A"]) is not None and _k_medio(por[s]["RM"]["P5"]["A"]) is not None]
    dp = [_p1_pet(por[s]["B1"], "A") - _p1_pet(por[s]["RM"], "A") for s in s_ord
          if _p1_pet(por[s]["B1"], "A") is not None and _p1_pet(por[s]["RM"], "A") is not None]
    rep = {}
    for nome, v in (("k_A", dk), ("P1_A", dp)):
        if v:
            m, lo, hi = ic(v)
            rep[nome] = {"n": len(v), "diferenca": m, "ic": [lo, hi], "passa": lo > 0}
        else:
            rep[nome] = {"n": 0, "passa": False}
    n_rep = min(rep["k_A"]["n"], rep["P1_A"]["n"])
    out["H-REP"] = {**rep, "leitura": _leitura(n_rep, rep["k_A"]["passa"] and rep["P1_A"]["passa"])}
    return out


def _resto(out, por, s_ord, pet) -> dict:
    # H-CUSTO
    def p3(m):
        vs = [v for v in m["P3"].values() if v is not None]
        return sum(vs) / len(vs) if vs else None
    dc = [p3(por[s]["B1"]) - p3(por[s]["B0"]) for s in s_ord if p3(por[s]["B1"]) is not None and p3(por[s]["B0"]) is not None]
    m, lo, hi = ic(dc)
    out["H-CUSTO"] = {"n": len(dc), "diferenca": m, "ic": [lo, hi], "leitura": _leitura(len(dc), hi < EPSILON)}
    # R-ESCUDO e os descritivos
    desc = {}
    for b in ("B1", "B1E", "B1U", "B1A", "D0", "DM", "RM"):
        v = [por[s][b]["P1"] - por[s]["B0"]["P1"] for s in s_ord
             if b in por[s] and por[s][b]["P1"] is not None and por[s]["B0"]["P1"] is not None]
        desc[b] = {"n": len(v), "diferenca_P1_contra_B0": st.mean(v) if v else None}
    out["R-ESCUDO"] = desc
    bracos = sorted({b for s in s_ord for b in por[s]})
    out["descritivos"] = {
        b: {"vidas_com_oportunidade": sum(por[s][b]["P1_oportunidades"] > 0 for s in s_ord if b in por[s]),
            "oportunidades": sum(por[s][b]["P1_oportunidades"] for s in s_ord if b in por[s]),
            "P2": st.mean(por[s][b]["P2"] for s in s_ord if b in por[s] and por[s][b]["P2"] is not None),
            "P4": {k: sum(por[s][b]["P4"][k] for s in s_ord if b in por[s]) for k in ("contencao", "encostar", "disputa_anti")},
            "P6": st.mean(por[s][b]["P6"] for s in s_ord if b in por[s])}
        for b in bracos}
    if pet is not None:                                   # os dois descritivos do adendo 1 (12.4)
        for b in bracos:
            op = sum(por[s][b]["P1_por_pet"][pet]["oportunidades"] for s in s_ord if b in por[s])
            neg = sum(por[s][b]["P1_por_pet"][pet].get("proprio_comeu", 0) for s in s_ord if b in por[s])
            ci = [por[s][b].get("culpa_inveja", {}).get(pet) for s in s_ord if b in por[s]]
            ci = [c for c in ci if c]
            out["descritivos"][b]["P1_neg"] = neg / op if op else None
            out["descritivos"][b]["culpa"] = st.mean(c["culpa"] for c in ci) if ci else None
            out["descritivos"][b]["inveja"] = st.mean(c["inveja"] for c in ci) if ci else None
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("vidas", type=Path)
    ap.add_argument("--inicio", type=int, default=91201)
    ap.add_argument("--n", type=int, default=160, help="o N da regra (D-CB-12)")
    ap.add_argument("--pet", default=None, help="so a P1 e a P3 deste pet (o adendo 1: A)")
    ap.add_argument("--saida", type=Path, required=True)
    a = ap.parse_args()
    sementes = set(range(a.inicio, a.inicio + a.n))
    por = ler(a.vidas, sementes)
    faltam = sorted(sementes - set(por))
    if faltam:
        raise SystemExit(f"faltam sementes: {faltam[:5]}... ({len(faltam)})")
    r = analisar(por, a.pet)
    r["fonte"] = {"vidas": str(a.vidas), "sementes": [a.inicio, a.inicio + a.n - 1], "delta": DELTA, "epsilon": EPSILON, "n_min": N_MIN,
                  "reamostras": REAMOSTRAS, "semente_bootstrap": SEMENTE_BOOTSTRAP}
    a.saida.write_text(json.dumps(r, indent=1, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    for h in ("H-EMERGE", "H-DOSE", "H-REP", "H-CUSTO"):
        print(h, r[h]["leitura"], {k: v for k, v in r[h].items() if k != "leitura"})


if __name__ == "__main__":
    main()
