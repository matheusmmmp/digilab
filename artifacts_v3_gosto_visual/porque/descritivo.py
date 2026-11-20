"""Exploracao descritiva (NAO confirmatoria) das GV3 e GV3b, so a partir dos medidas.json e analise.json gravados.

Uso: python -I descritivo.py <raiz do repositorio>
Grava descritivo.json ao lado deste script. Nenhuma vida nova; nenhum codigo do repositorio importado.
"""
import json
import random
import statistics as st
import sys
from pathlib import Path

RAIZ = Path(sys.argv[1])
RUNS = {"gv3": RAIZ / "artifacts_v3_gosto_visual/gosto_visual", "gv3b": RAIZ / "artifacts_v3_gosto_visual/gosto_visual_enjoo2"}
JANELA = 240
DECISAO = 15


def ranks(xs):
    ordem = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(xs):
        j = i
        while j + 1 < len(xs) and xs[ordem[j + 1]] == xs[ordem[i]]:
            j += 1
        for k in range(i, j + 1):
            r[ordem[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def spearman(xs, ys):
    if len(xs) < 3 or len(set(xs)) < 2 or len(set(ys)) < 2:
        return None
    rx, ry = ranks(xs), ranks(ys)
    mx, my = st.mean(rx), st.mean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5
    return num / den


def boot_unidades(pets, f, n=2000, semente=20261112):
    """IC95 percentil reamostrando unidades (base, k) inteiras; f(lista de pets) -> numero ou None"""
    unid = sorted({(p["base"], p["k"]) for p in pets})
    por = {u: [p for p in pets if (p["base"], p["k"]) == u] for u in unid}
    rng = random.Random(semente)
    vals, indef = [], 0
    for _ in range(n):
        amostra = [p for u in (rng.choice(unid) for _ in unid) for p in por[u]]
        v = f(amostra)
        if v is None:
            indef += 1
        else:
            vals.append(v)
    vals.sort()
    if not vals:
        return None
    return {"ic95": [vals[int(0.025 * len(vals))], vals[min(len(vals) - 1, int(0.975 * len(vals)))]], "indefinidas": indef}


def por_pet(r):
    meds = r["medidas"]
    validas = [x for x in meds if x["tempo_relativo"] is not None]
    ambas = [x for x in validas if 0 < x["tempo_relativo"] < 1]
    ag = [x["agrado_agora"] for x in meds if x["agrado_agora"] is not None]
    return {"base": r["base"], "k": r["k"], "genoma": r["genoma_tipo"], "dono": r["dono"],
            "di": meds[0]["agrado_inato"], "dagora": st.mean(ag) if ag else None,
            "tr": st.mean(x["tempo_relativo"] for x in validas) if validas else None,
            "esc": st.mean(x["escolha"] for x in validas) if validas else None,
            "tr_ambas": st.mean(x["tempo_relativo"] for x in ambas) if ambas else None,
            "n_validas": len(validas), "n_ambas": len(ambas),
            "var_tr": st.pvariance([x["tempo_relativo"] for x in validas]) if len(validas) > 1 else None,
            "fr_olhando": st.mean(r["fracoes_olhando"])}


def resumo_run(pasta):
    med = json.loads((pasta / "medidas.json").read_text(encoding="utf-8"))
    vidas = list(med.values())
    reps = [x for r in vidas for x in r["medidas"]]
    out = {"n_vidas": len(vidas), "n_replicas": len(reps)}
    # (R1) quantas decisoes de olhar cabem numa replica: os ticks nas duas TVs / 15
    ticks = [round(x["tempo_total"] * JANELA) for x in reps]
    dec = [t / DECISAO for t in ticks]
    hist = {}
    for d in dec:
        c = "0" if d == 0 else "<=1" if d <= 1 else "<=2" if d <= 2 else "<=3" if d <= 3 else ">3"
        hist[c] = hist.get(c, 0) + 1
    out["R1_decisoes_olhando_por_replica"] = {"media": st.mean(dec), "mediana": st.median(dec),
                                              "fracao": {k: v / len(reps) for k, v in sorted(hist.items())}}
    # (R2) nas replicas validas, quantas viram uma TV so (o tempo relativo e 0 ou 1 e repete a escolha)
    val = [x for x in reps if x["tempo_relativo"] is not None]
    uma = [x for x in val if x["tempo_relativo"] in (0.0, 1.0)]
    igual = [x for x in val if x["tempo_relativo"] == x["escolha"]]
    out["R2_uma_tv_so"] = {"validas": len(val), "fracao_uma_tv_so": len(uma) / len(val),
                           "fracao_tempo_relativo_igual_a_escolha": len(igual) / len(val),
                           "fracao_ambas": 1 - len(uma) / len(val)}
    pets = [por_pet(r) for r in vidas]
    # (R3) confiabilidade por pet do tempo relativo: variancia entre pets das medias contra o erro-padrao medio ao quadrado
    for g in ("proprio", "vazio"):
        ps = [p for p in pets if p["genoma"] == g and p["tr"] is not None and p["var_tr"] is not None]
        entre = st.pvariance([p["tr"] for p in ps])
        erro = st.mean(p["var_tr"] / p["n_validas"] for p in ps)
        out[f"R3_confiabilidade_tr_{g}"] = {"n_pets": len(ps), "var_entre_medias": entre, "erro2_medio": erro,
                                            "fracao_sinal": max(0.0, (entre - erro) / entre) if entre > 0 else None,
                                            "n_validas_medio": st.mean(p["n_validas"] for p in ps)}
    # (R4) o tempo relativo so nas replicas em que o pet viu as duas TVs, contra Delta_I (proprio, os tres donos juntos)
    pr = [p for p in pets if p["genoma"] == "proprio"]
    pa = [p for p in pr if p["tr_ambas"] is not None]
    f_amb = lambda ps: spearman([p["di"] for p in ps if p["tr_ambas"] is not None], [p["tr_ambas"] for p in ps if p["tr_ambas"] is not None])
    f_tr = lambda ps: spearman([p["di"] for p in ps if p["tr"] is not None], [p["tr"] for p in ps if p["tr"] is not None])
    f_esc = lambda ps: spearman([p["di"] for p in ps if p["esc"] is not None], [p["esc"] for p in ps if p["esc"] is not None])
    out["R4_proprio_juntos"] = {
        "n_pets": len(pr), "n_pets_com_ambas": len(pa), "n_ambas_medio": st.mean(p["n_ambas"] for p in pr),
        "spearman_di_tr": {"ponto": f_tr(pr), **(boot_unidades(pr, f_tr) or {})},
        "spearman_di_escolha": {"ponto": f_esc(pr), **(boot_unidades(pr, f_esc) or {})},
        "spearman_di_tr_so_ambas": {"ponto": f_amb(pr), **(boot_unidades(pr, f_amb) or {})}}
    # (R5) o vazio (Delta_I = 0): o desvio de 0,5 e o que a sonda faz sem o gosto inato (o estresse de B, o salto, a novidade)
    vz = [p for p in pets if p["genoma"] == "vazio"]
    f_m_tr = lambda ps: st.mean(p["tr"] for p in ps if p["tr"] is not None)
    f_m_esc = lambda ps: st.mean(p["esc"] for p in ps if p["esc"] is not None)
    out["R5_vazio_juntos"] = {"n_pets": len(vz),
                              "tempo_relativo": {"ponto": f_m_tr(vz), **boot_unidades(vz, f_m_tr)},
                              "escolha": {"ponto": f_m_esc(vz), **boot_unidades(vz, f_m_esc)}}
    # (R6) o agrado do cerebro (Delta_agora) e o comportamento: no vazio so a exposicao o move
    f_ag = lambda ps: spearman([p["dagora"] for p in ps if p["tr"] is not None], [p["tr"] for p in ps if p["tr"] is not None])
    expo = [p["dagora"] - p["di"] for p in pets]
    out["R6_exposicao"] = {
        "dp_delta_inato_proprio": st.pstdev([p["di"] for p in pr]),
        "media_abs_exposicao_proprio": st.mean(abs(p["dagora"] - p["di"]) for p in pr),
        "media_abs_exposicao_vazio": st.mean(abs(p["dagora"] - p["di"]) for p in vz),
        "dp_delta_agora_vazio": st.pstdev([p["dagora"] for p in vz]),
        "spearman_dagora_tr_vazio": {"ponto": f_ag(vz), **(boot_unidades(vz, f_ag) or {})},
        "spearman_dagora_tr_proprio": {"ponto": f_ag(pr), **(boot_unidades(pr, f_ag) or {})},
        "n_expo": len(expo)}
    # (R7) a fracao das decisoes acordadas olhando a TV da vida, nos 14 dias (a base de quanto o pet olha)
    out["R7_fracao_olhando_vida"] = {"media": st.mean(p["fr_olhando"] for p in pets)}
    # o que o analise.json ja diz (so para conferir que a leitura e a mesma)
    an = json.loads((pasta / "analise.json").read_text(encoding="utf-8"))
    out["conferencia_analise"] = an["conferencia"]
    return out


res = {k: resumo_run(p) for k, p in RUNS.items()}
(Path(__file__).resolve().parent / "descritivo.json").write_bytes((json.dumps(res, indent=1, ensure_ascii=True) + "\n").encode("utf-8"))
print(json.dumps(res, indent=1))
