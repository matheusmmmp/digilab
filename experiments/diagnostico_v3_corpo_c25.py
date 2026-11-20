"""O diagnostico da C2.5 (docs/PLANO_ANALISE_V3_CORPO.md; o CHECKPOINT C2.5, "Sim, diagnosticar"): por que a D sobe a privacao no
comedouro. So le as vidas que ja existem: cada vida e rejogada do log gravado pela run (artifacts_v3_corpo/ablacao/vidas), com as
fabricas do braco, e a privacao rejogada tem de sair igual a do medidas.json (falha alta). Nenhuma semente nova, nenhuma vida nova.

Por decisao da janela dos dias 8 a 14 (a da privacao), le o Estado (fome, higiene, energia, o dormindo e a noite) e a quimica do corpo
(o combustivel, a fome, o alimento no estomago, o dano) e a saude. Decompoe a privacao em qual necessidade fica abaixo do limiar e em que contexto.

Uso: python experiments/diagnostico_v3_corpo_c25.py --unidades 50 --processos 4
     grava artifacts_v3_corpo/diagnostico_c25/diagnostico.json
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import statistics
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import run_v3_corpo as rc  # noqa: E402
from digilab.config import CONFIG_PADRAO  # noqa: E402
from digilab.events import LogDeEventos  # noqa: E402
from digilab.metrics import JANELA_8_14  # noqa: E402
from digilab.mundo import reproduzir_mundo  # noqa: E402

RUN = RAIZ / "artifacts_v3_corpo" / "ablacao"
SAIDA = RAIZ / "artifacts_v3_corpo" / "diagnostico_c25"
BRACOS = ("CTRL", "D", "DE")
LUGARES = ("comedouro", "longe_fixo")
DONOS = ("atencioso", "relapso", "aleatorio", "incoerente")
LIM = CONFIG_PADRAO.limiar_privacao
PASSO = CONFIG_PADRAO.intervalo_decisao_ticks


def rejogar(braco: str, dono: str, lugar: str, semente: int, dias: int, orcamento: int) -> list[dict]:
    """a vida gravada, rejogada do log; por decisao, o Estado e a quimica (so le o motor)"""
    texto = (RUN / "vidas" / braco / f"{dono}_{lugar}_{semente}.jsonl").read_text(encoding="utf-8")
    fp0, fm0 = rc.fabricas(braco, dono, semente, dias, orcamento)
    caixa: dict = {}
    linhas: list[dict] = []

    def fm(politica, cfg, s):
        caixa["m"] = fm0(politica, cfg, s)
        return caixa["m"]

    def fp(cfg=None):
        reg = fp0(cfg)
        agir = reg.agir

        def agir_e_ler(obs, rng):
            m = caixa["m"]
            e, q = m._estado, m.corpo.q
            linhas.append({"t": len(linhas) * PASSO, "fome": e.fome, "higiene": e.higiene, "energia": e.energia, "saude": e.saude,
                           "q_dano": q.get("dano", 0), "dormindo": bool(e.dormindo), "noite": CONFIG_PADRAO.e_noite(e.tick_do_dia),
                           "combustivel": q["combustivel"], "q_fome": q["fome"], "alimento": q.get("alimento", 0)})
            return agir(obs, rng)

        reg.agir = agir_e_ler
        return reg

    motor = reproduzir_mundo(LogDeEventos.de_jsonl(texto), fp, semente=semente, fabrica_motor=fm)
    if motor.log.para_jsonl() != texto:
        raise RuntimeError("o replay nao refaz o log gravado")
    return linhas


def resumir(linhas: list[dict], C: int) -> dict:
    ini, fim = JANELA_8_14
    js = [x for x in linhas if ini <= x["t"] < fim]
    n = len(js)
    if not n:
        raise ValueError("sem decisao na janela")
    priv = [x for x in js if min(x["fome"], x["higiene"], x["energia"]) < LIM]
    pf = [x for x in priv if x["fome"] < LIM]
    out = {"n": n, "privacao": len(priv) / n,
           "so_fome": sum(1 for x in priv if x["fome"] < LIM and x["energia"] >= LIM and x["higiene"] >= LIM) / n,
           "so_energia": sum(1 for x in priv if x["energia"] < LIM and x["fome"] >= LIM and x["higiene"] >= LIM) / n,
           "fome_e_energia": sum(1 for x in priv if x["fome"] < LIM and x["energia"] < LIM) / n,
           "com_higiene": sum(1 for x in priv if x["higiene"] < LIM) / n,
           "fome_baixa": len(pf) / n,
           "fome_baixa_dormindo": sum(1 for x in pf if x["dormindo"]) / n,
           "fome_baixa_acordado": sum(1 for x in pf if not x["dormindo"]) / n,
           "fome_baixa_noite": sum(1 for x in pf if x["noite"]) / n,
           "fome_baixa_comb_abaixo": sum(1 for x in pf if x["combustivel"] < C // 4) / n,
           "fome_baixa_comb_acima": sum(1 for x in pf if x["combustivel"] >= C // 4) / n,
           "fome_baixa_com_alimento": sum(1 for x in pf if x["alimento"] > 0) / n,
           "dormindo": sum(1 for x in js if x["dormindo"]) / n,
           "comb_abaixo": sum(1 for x in js if x["combustivel"] < C // 4) / n,
           "fome_media": statistics.fmean(x["fome"] for x in js),
           "combustivel_medio": statistics.fmean(x["combustivel"] for x in js) / C,
           "saude_media": statistics.fmean(x["saude"] for x in js),
           "saude_baixa": sum(1 for x in js if x["saude"] < LIM) / n,
           "saude_fim": js[-1]["saude"]}
    # a fome ao acordar: na primeira decisao acordado depois de um sono
    acordar = [b for a, b in zip(js, js[1:]) if a["dormindo"] and not b["dormindo"]]
    out["acordou"] = len(acordar)
    out["fome_ao_acordar"] = statistics.fmean(x["fome"] for x in acordar) if acordar else None
    out["acordou_em_privacao_de_fome"] = (sum(1 for x in acordar if x["fome"] < LIM) / len(acordar)) if acordar else None
    return out


def _uma(args) -> dict:
    braco, dono, lugar, unidade, dias, orc, C = args
    linhas = rejogar(braco, dono, lugar, unidade["semente"], dias, orc)
    return {"braco": braco, "dono": dono, "lugar": lugar, "base": unidade["base"], "semente": unidade["semente"], **resumir(linhas, C)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--unidades", type=int, default=50)
    ap.add_argument("--processos", type=int, default=4)
    a = ap.parse_args()
    if a.processos > 4:
        raise ValueError("V3-D8: no maximo 4 processos")
    meta = json.loads((RUN / "meta.json").read_text(encoding="utf-8"))
    dias, orc = meta["config"]["dias"], meta["config"]["orcamento_por_dia"]
    from digilab.config import CONFIG_CORPO_METABOLISMO
    C = CONFIG_CORPO_METABOLISMO.escala
    unidades = meta["unidades"][:a.unidades]
    medidas = {m["vida"]: m for m in json.load(gzip.open(RUN / "medidas.json.gz", "rt", encoding="utf-8"))}
    tarefas = [(b, d, l, u, dias, orc, C) for u in unidades for b in BRACOS for l in LUGARES for d in DONOS]
    with ProcessPoolExecutor(a.processos) as ex:
        vidas = list(ex.map(_uma, tarefas, chunksize=4))
    for v in vidas:
        gravada = medidas[f"{v['braco']}|{v['dono']}|{v['lugar']}|{v['semente']}"]["privacao"]
        if abs(v["privacao"] - gravada) > 1e-12:
            raise RuntimeError(f"a privacao rejogada {v['privacao']} nao e a gravada {gravada}: {v}")
    chaves = [k for k in vidas[0] if k not in ("braco", "dono", "lugar", "base", "semente", "n", "acordou")]
    agregado = {}
    for l in LUGARES:
        por = {b: {} for b in BRACOS}
        for b in BRACOS:
            for u in unidades:
                vs = [v for v in vidas if v["braco"] == b and v["lugar"] == l and v["base"] == u["base"]]
                por[b][u["base"]] = {k: statistics.fmean(v[k] for v in vs if v[k] is not None) for k in chaves}
        agregado[l] = {}
        for k in chaves:
            niv = {b: statistics.fmean(por[b][u["base"]][k] for u in unidades) for b in BRACOS}
            dif = {}
            for b in BRACOS[1:]:
                ds = [por[b][u["base"]][k] - por["CTRL"][u["base"]][k] for u in unidades]
                m, sd = statistics.fmean(ds), statistics.stdev(ds)
                meia = 1.96 * sd / len(ds) ** 0.5
                dif[f"{b} - CTRL"] = {"media": m, "ic95_aprox": [m - meia, m + meia]}
            agregado[l][k] = {"niveis": niv, **dif}
    SAIDA.mkdir(parents=True, exist_ok=True)
    out = {"unidades": len(unidades), "bases": [u["base"] for u in unidades], "bracos": BRACOS, "lugares": LUGARES,
           "limiar": LIM, "janela": list(JANELA_8_14), "vidas_rejogadas": len(vidas),
           "conferencia": "a privacao rejogada de cada vida e igual a do medidas.json da run", "agregado": agregado, "vidas": vidas}
    texto = json.dumps(out, ensure_ascii=False, sort_keys=True, indent=1) + "\n"
    (SAIDA / "diagnostico.json").write_text(texto, encoding="utf-8", newline="\n")
    print("gravado", (SAIDA / "diagnostico.json").relative_to(RAIZ), hashlib.sha256(texto.encode()).hexdigest())


if __name__ == "__main__":
    main()
