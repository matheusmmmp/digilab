"""E0 do DigiBrain V3 (docs/futuro/digibrain_v3_e0.md, parte 1): de onde vem o "instinto decide ~80%" no cerebro A do pets v11.

Medicao DESCRITIVA, sem gate e sem plano de analise: so le as decisoes ja registradas pela politica (o `motivos` do estado interno),
nas sementes dos testes (101...505), na bancada do v11 (`exportar_gabarito_lobos.bancada_v11(14, 224)`, braco `P1-c-tapa`), com os
quatro donos do gabarito. Nao muda nada no cerebro; a sonda e a mesma das sondas "quem decidiu" do N7 e do J5: a mesma decisao, com o
mesmo u, sem um termo.

Por decisao com escolha (mais de um candidato):
  - P   = peso efetivo / soma (o que a politica sorteou);
  - P0  = o mesmo sem o termo aprendido (o lobo `decisao`, que ja inclui as entradas do corpo), com o piso refeito como na politica;
  - TV  = (1/2) sum |P - P0|, a distancia de variacao total;
  - mudou = a acao sorteada com P0 e o mesmo u e outra.
  - mudou_l1 = a medida da L1 ("o lobo de decisao decidiu", `motivo._motivo_lobos_decisao`): o sorteio so com os impulsos.
Tambem: a fracao de decisoes com um candidato so (o instinto decide por construcao e o credito nelas nao muda peso nenhum, porque
o fator S*1[a=a*] - P_a e zero), o `lobo_decisivo` por regra e, para a janela de credito (o traco da REVISAO-APRENDIZ), a fracao
das k decisoes anteriores que tem um candidato so.

    python experiments/medir_e0_influencia_aprendido.py      # grava artifacts_v2_v3/e0_influencia.json
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import exportar_gabarito_lobos as gl  # noqa: E402

from digilab.policies.lobos import sortear  # noqa: E402

ARQUIVO = RAIZ / "artifacts_v2_v3" / "e0_influencia.json"
DIAS = 14
ORCAMENTO = 16 * DIAS
DONOS = ("atencioso", "relapso", "aleatorio", "incoerente")
SEMENTES = tuple(sorted(bv.SEMENTES_TESTE))
K_TRACO = (1, 2, 4, 8)


def _vida(args: tuple) -> dict:
    """As decisoes de uma vida, ja medidas (so o que a analise usa)."""
    dono, semente = args
    b = gl.bancada_v11(DIAS, ORCAMENTO)
    if b.cfg_lobos.traco_decisoes != 0:
        raise RuntimeError("o v11 roda sem traco (os canais nao andam com o traco); a bancada mudou")
    v = b.vida(bv.EspecVida(dono, gl.BRACO_V11, semente))
    pol = v.motor.politica
    if not pol.aprende:
        raise RuntimeError("o v11 aprende; a politica veio sem aprendizado")
    piso = pol._piso
    dia, hora_ant, saida = 0, -1.0, []
    for m in pol.motivos:
        hora = m["percepcao"]["hora"]
        if hora < hora_ant:
            dia += 1
        hora_ant = hora
        cands = m["candidatos"]
        c = m["contribuicoes"]
        if set(c) - {"impulsos", "decisao", "memoria_emocao", "piso"}:
            raise RuntimeError(f"termo inesperado nas contribuicoes: {sorted(c)}")
        d = {"dia": dia, "regra": m["regra"], "n_cand": len(cands), "acao": m["acao"], "decisivo": m["lobo_decisivo"]}
        if len(cands) > 1:
            efet, sem = [], []
            for a in cands:
                e = c["impulsos"][a] + c["decisao"][a] + c["memoria_emocao"][a] + c["piso"][a]
                if e != m["pesos"][a]:
                    raise RuntimeError(f"peso efetivo refeito {e} != registrado {m['pesos'][a]} ({m['regra']}, {a})")
                s = c["impulsos"][a] + c["memoria_emocao"][a]
                s = s + (piso - s if s < piso else 0.0)
                efet.append(e)
                sem.append(s)
            te, ts = sum(efet), sum(sem)
            P = [x / te for x in efet]
            P0 = [x / ts for x in sem]
            if cands[sortear(efet, m["u"])] != m["acao"]:
                raise RuntimeError("o sorteio refeito nao da a acao registrada")
            d.update({
                "tv": 0.5 * sum(abs(p - q) for p, q in zip(P, P0)),
                "mudou": cands[sortear(sem, m["u"])] != m["acao"],
                # a medida da L1 (motivo._motivo_lobos_decisao): o sorteio so com os impulsos (sem o piso), o mesmo u
                "mudou_l1": cands[sortear([c["impulsos"][a] for a in cands], m["u"])] != m["acao"],
                "abs_dec": sum(abs(c["decisao"][a]) for a in cands),
                "abs_imp": sum(abs(c["impulsos"][a]) for a in cands),
                "p_acao": P[cands.index(m["acao"])], "p0_acao": P0[cands.index(m["acao"])],
            })
        saida.append(d)
    return {"dono": dono, "semente": semente, "decisoes": saida, "desvio_maximo": pol.desvio_maximo(),
            "n_pesos": pol.n_pesos(), "pesos_no_teto": pol.pesos_no_teto()}


def _frac(n: int, total: int) -> float | None:
    return None if total == 0 else n / total


def _resumo(decs: list[dict]) -> dict:
    esc = [d for d in decs if d["n_cand"] > 1]
    return {
        "n": len(decs), "n_escolha": len(esc),
        "frac_um_candidato": _frac(len(decs) - len(esc), len(decs)),
        "frac_decisivo_impulsos_na_escolha": _frac(sum(d["decisivo"] == "impulsos" for d in esc), len(esc)),
        "frac_decisivo_impulsos_todas": _frac(sum(d["decisivo"] == "impulsos" for d in decs), len(decs)),
        "tv_media_na_escolha": _frac(sum(d["tv"] for d in esc), len(esc)) if esc else None,
        "frac_mudou_na_escolha": _frac(sum(d["mudou"] for d in esc), len(esc)),
        "frac_mudou_todas": _frac(sum(d.get("mudou", False) for d in decs), len(decs)),
        "frac_mudou_l1_todas": _frac(sum(d.get("mudou_l1", False) for d in decs), len(decs)),
        "frac_mudou_l1_na_escolha": _frac(sum(d["mudou_l1"] for d in esc), len(esc)),
        "razao_dec_imp_na_escolha": (sum(d["abs_dec"] for d in esc) / sum(d["abs_imp"] for d in esc)) if esc else None,
    }


def _traco(vidas: list[dict]) -> dict:
    """Para cada decisao, a fracao das k anteriores (o que um traco de k decisoes creditaria) que tem um candidato so."""
    out = {}
    for k in K_TRACO:
        n_um = n_tot = 0
        for v in vidas:
            nc = [d["n_cand"] for d in v["decisoes"]]
            for i in range(len(nc)):
                for j in range(max(0, i - k), i):
                    n_tot += 1
                    n_um += nc[j] == 1
        out[str(k)] = _frac(n_um, n_tot)
    return out


def analisar(vidas: list[dict]) -> dict:
    todas = [d for v in vidas for d in v["decisoes"]]
    por_regra = defaultdict(list)
    por_dia = defaultdict(list)
    for d in todas:
        por_regra[d["regra"]].append(d)
        por_dia[d["dia"]].append(d)
    por_dono = defaultdict(list)
    for v in vidas:
        por_dono[v["dono"]].extend(v["decisoes"])
    regra_um = {r: sum(d["n_cand"] == 1 for d in ds) for r, ds in por_regra.items()}
    return {
        "geral": _resumo(todas),
        "por_regra": {r: {**_resumo(ds), "frac_do_total": len(ds) / len(todas),
                          "candidatos": sorted({d["n_cand"] for d in ds})} for r, ds in sorted(por_regra.items())},
        "um_candidato_por_regra_frac_do_total": {r: n / len(todas) for r, n in sorted(regra_um.items()) if n},
        "por_dia": {str(k): _resumo(ds) for k, ds in sorted(por_dia.items())},
        "por_dono": {k: _resumo(ds) for k, ds in sorted(por_dono.items())},
        "traco_frac_anteriores_um_candidato": _traco(vidas),
        "pesos": [{"dono": v["dono"], "semente": v["semente"], "desvio_maximo": v["desvio_maximo"], "n_pesos": v["n_pesos"],
                   "pesos_no_teto": v["pesos_no_teto"]} for v in vidas],
    }


def main() -> None:
    especs = [(d, s) for d in DONOS for s in SEMENTES]
    with ProcessPoolExecutor() as ex:
        vidas = list(ex.map(_vida, especs))
    out = {"versao": 2, "braco": gl.BRACO_V11, "dias": DIAS, "orcamento": ORCAMENTO, "donos": list(DONOS),
           "sementes": list(SEMENTES), "analise": analisar(vidas)}
    ARQUIVO.parent.mkdir(exist_ok=True)
    ARQUIVO.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    g = out["analise"]["geral"]
    print(f"{ARQUIVO}: {g['n']} decisoes; um candidato {g['frac_um_candidato']:.3f}; TV {g['tv_media_na_escolha']:.4f}; "
          f"mudou na escolha {g['frac_mudou_na_escolha']:.4f}")


if __name__ == "__main__":
    main()
