"""SOCIAL_PAR S0: o resumo da observacao (le `artifacts_v3_social_par_s/s0/observacao.json` e o `medidas.json` da run do A0; escreve o
`resumo.json` ao lado). Descritivo: medias sobre os pares, IC95 pela t como tamanho do que se ve, nenhum teste e nenhuma decisao.

    python experiments/resumir_v3_social_par_s0.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from digilab import metrics as mt  # noqa: E402

S0 = RAIZ / "artifacts_v3_social_par_s" / "s0"
RUN = RAIZ / "artifacts_v3_social_par_a0" / "run"
ACOES = ("dormir", "explorar", "comer", "chamar_atencao", "brincar", "ocioso", "emburrar")
MIN_PASSOS = 20                     # um par entra na comparacao perto x longe de um pet so com ao menos 20 decisoes de cada lado


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _ic(xs: list[float]) -> dict:
    """a media, o dp e o IC95 pela t sobre os pares (o `metrics.ic_t`, o mesmo das medidas do A0)"""
    ic = mt.ic_t(xs)
    return {"n": ic["n"], "media": ic["media"], "dp": ic["dp"], "ic95": [ic["ic_inferior"], ic["ic_superior"]],
            "motivo": ic["motivo"], "positivos": sum(1 for x in xs if x > 0), "negativos": sum(1 for x in xs if x < 0)}


def _frac(c: dict) -> dict:
    t = sum(c.values())
    return {a: c.get(a, 0) / t for a in ACOES} if t else {}


def presenca(pares: list[dict], pet: str) -> dict:
    """a fracao de cada acao do pet com o outro perto (<= 6 celulas) menos a fracao longe, par a par"""
    out, usados = {}, [p for p in pares if sum(p["perto"][pet].values()) >= MIN_PASSOS and sum(p["longe"][pet].values()) >= MIN_PASSOS]
    for a in ACOES:
        out[a] = _ic([_frac(p["perto"][pet])[a] - _frac(p["longe"][pet])[a] for p in usados])
        out[a]["fracao_perto"] = sum(_frac(p["perto"][pet])[a] for p in usados) / len(usados)
        out[a]["fracao_longe"] = sum(_frac(p["longe"][pet])[a] for p in usados) / len(usados)
    return {"pares_usados": len(usados), "acoes": out}


def juntos(pares: list[dict]) -> dict:
    """os dois perto: a dupla de acoes observada, contra a esperada pela independencia dentro do par (o produto das fracoes de cada um
    nos mesmos passos perto); a razao e somada sobre os pares"""
    obs, esp, n_perto = Counter(), Counter(), 0
    for p in pares:
        j = p["junto"]
        t = sum(j.values())
        if not t:
            continue
        n_perto += t
        fa, fb = Counter(), Counter()
        for k, c in j.items():
            a, b = k.split("|")
            fa[a] += c
            fb[b] += c
        for a in ACOES:
            obs[a] += j.get(f"{a}|{a}", 0)
            esp[a] += fa[a] * fb[a] / t
    return {"passos_perto": n_perto, "mesma_acao": {a: {"observado": obs[a], "esperado": esp[a],
                                                         "razao": None if esp[a] == 0 else obs[a] / esp[a]} for a in ACOES}}


def depois(pares: list[dict], pet: str) -> dict:
    """o que o pet faz na decisao seguinte a uma aproximacao do outro, contra a fracao dele em toda a vida (somado sobre os pares)"""
    dep, toda = Counter(), Counter()
    for p in pares:
        dep.update(p["depois_da_aproximacao"][pet])
        toda.update(p["acoes"][pet])
    fd, ft = _frac(dep), _frac(toda)
    return {"n_aproximacoes": sum(dep.values()), "acoes": {a: {"depois": fd.get(a, 0.0), "vida": ft.get(a, 0.0)} for a in ACOES}}


def fecha(pares: list[dict]) -> dict:
    c = Counter()
    for p in pares:
        c.update(p["fecha_a_distancia"])
    t = c["passos"]
    return {"passos_antes_do_perto": t, **{f"{x}_{k}": c[f"{x}_{k}"] / t for x in "AB" for k in ("encurta", "alonga")},
            "ganho_total": {x: c[f"{x}_ganho"] for x in "AB"}}


def co7(pares: list[dict]) -> dict:
    out = {}
    for pet in "AB":
        c, ex = Counter(), []
        for p in pares:
            x = p["co7"][pet]
            if x is None:
                raise ValueError(f"o par {p['par']} nao tem os motivos do pet {pet}")
            c.update(x["contagem"])
            ex += [{"par": p["par"], **e} for e in x["exemplos"]]
        out[pet] = {"decisoes": sum(p["n"] for p in pares), "contagem": dict(c), "exemplos": ex[:12], "n_exemplos": len(ex)}
    return out


def mundo(pares: list[dict]) -> dict:
    disp = [p["disputas"]["n"] for p in pares]
    ex = [{"par": p["par"], **e} for p in pares for e in p["disputas"]["exemplos"]]
    cont = Counter()
    for p in pares:
        cont.update(p["contatos"])
    return {"disputas": {"total": sum(disp), "pares_com": sum(1 for x in disp if x), "exemplos": ex[:8]},
            "comeu_por_vida": {x: sum(p["comeu"][x] for p in pares) / len(pares) for x in "AB"},
            "comer_junto_em_contato_por_vida": sum(p["comer_junto_em_contato"] for p in pares) / len(pares),
            "viu_o_outro_comer_por_vida": {x: sum(p["vistos_comer"][x] for p in pares) / len(pares) for x in "AB"},
            "contatos": dict(cont), "contatos_por_vida": sum(cont.values()) / len(pares),
            "brincar_por_vida": {x: sum(p["brincar"][x] for p in pares) / len(pares) for x in "AB"},
            "chutes_total": {x: sum(p["chutes"][x] for p in pares) for x in "AB"}}


def distancia(pares: list[dict]) -> dict:
    h = Counter()
    for p in pares:
        h.update({int(k): v for k, v in p["distancia_hist"].items()})
    t = sum(h.values())
    acum, ate = 0, {}
    for k in sorted(h):
        acum += h[k]
        ate[str(k)] = acum / t
    dorme = {x: [p["acoes"][x].get("dormir", 0) / p["n"] for p in pares] for x in "AB"}
    return {"fracao_perto": _ic([p["fracao_perto"] for p in pares]), "fracao_contato": _ic([p["fracao_contato"] for p in pares]),
            "acumulada": ate, "fracao_dormir": {x: _ic(v) for x, v in dorme.items()}}


def gravacao(medidas: dict) -> dict:
    """da run do A0: quantos pares tem a GRAV igual a VIVO na janela (P gravado faz o mesmo que P vivo)"""
    ig, zero, n, desv = 0, 0, 0, Counter()
    for r in medidas.values():
        v, g = r["condicoes"]["VIVO"], r["condicoes"]["GRAV"]
        if not (v["cabe"] and g["cabe"]) or v["distancia_no_t0"] <= 6:
            continue
        n += 1
        zero += v["t_perto"] == g["t_perto"]
        ig += all(v[k] == g[k] for k in ("t_perto", "t_contato", "fracao_perto", "contingencia_FP", "contingencia_PF"))
        desv[min(g["desvios_P_janela"].get("alvo_fora", 0), 10)] += 1
    return {"pares_elegiveis": n, "d_a_zero": zero, "janela_identica": ig, "desvios_P_janela_hist": {str(k): v for k, v in sorted(desv.items())}}


def main() -> None:
    obs = json.loads((S0 / "observacao.json").read_text(encoding="utf-8"))["pares"]
    medidas = json.loads((RUN / "medidas.json").read_text(encoding="utf-8"))
    out = {"pares": len(obs), "presenca": {"F": presenca(obs, "A"), "P": presenca(obs, "B")}, "juntos": juntos(obs),
           "depois_da_aproximacao": {"P_depois_de_F": depois(obs, "B"), "F_depois_de_P": depois(obs, "A")},
           "fecha_a_distancia": fecha(obs), "co7": co7(obs), "mundo": mundo(obs), "distancia": distancia(obs),
           "gravacao": gravacao(medidas),
           "fonte": {"observacao_sha256": _sha(S0 / "observacao.json"), "medidas_sha256": _sha(RUN / "medidas.json"),
                     "script_sha256": _sha(Path(__file__))}}
    (S0 / "resumo.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
    print(_sha(S0 / "resumo.json"))


if __name__ == "__main__":
    main()
