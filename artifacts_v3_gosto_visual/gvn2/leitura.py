"""GVN-2 (docs/PLANO_ANALISE_V3_GOSTO_VISUAL_GVN2.md): a leitura descritiva (NAO confirmatoria) das sondas gravadas nos vidas.tar.gz da
GV3 e da GV3b. Nenhuma vida nova; nenhum codigo do repositorio importado; um processo so.

Uso: python -I leitura.py <raiz do repositorio>
Grava leitura.json ao lado deste script, com LF, igual byte a byte a cada execucao. Falha alto se a conferencia C0 nao bater.
"""
import json
import random
import statistics as st
import sys
import tarfile
from pathlib import Path

RAIZ = Path(sys.argv[1])
RUNS = {"gv3": RAIZ / "artifacts_v3_gosto_visual/gosto_visual", "gv3b": RAIZ / "artifacts_v3_gosto_visual/gosto_visual_enjoo2"}
JANELA = 240                       # experiments/sonda_duas_tvs.py, JANELA_TICKS
ID_ROTULO = {2: "A", 3: "B"}       # digilab/tv.py, IDS_DUAS_TVS = (2, 3); sonda_duas_tvs.ROTULO
S = 1024                           # digilab/config.py, _S
W_GOSTO = S                        # ConfigOlhar.w_gosto
A_MAX = 4 * S                      # ConfigDigibrainInatos.a_max
CHAVES_DECISAO = {"acao", "olha"}  # o que ler_replica grava de cada decisao
SEMENTE_BOOT = 20261112
BOOT = 2000


def div_arred(n, d):
    """a divisao arredondada do cerebro (metade para longe do zero), para o mul"""
    q, r = divmod(abs(n), d)
    q += 1 if 2 * r >= d else 0
    return q if n >= 0 else -q


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


def boot_unidades(pets, f):
    """o ponto e o IC95 percentil reamostrando unidades (base, k) inteiras; f(lista de pets) -> numero ou None"""
    unid = sorted({(p["base"], p["k"]) for p in pets})
    por = {u: [p for p in pets if (p["base"], p["k"]) == u] for u in unid}
    rng = random.Random(SEMENTE_BOOT)
    vals, indef = [], 0
    for _ in range(BOOT):
        amostra = [p for u in (rng.choice(unid) for _ in unid) for p in por[u]]
        v = f(amostra)
        if v is None:
            indef += 1
        else:
            vals.append(v)
    vals.sort()
    ic = None if not vals else [vals[int(0.025 * len(vals))], vals[min(len(vals) - 1, int(0.975 * len(vals)))]]
    return {"ponto": f(pets), "ic95": ic, "indefinidas": indef}


def hist(vs):
    h = {"0": 0, "1": 0, "2": 0, ">=3": 0}
    for v in vs:
        h[str(v) if v < 3 else ">=3"] += 1
    return {k: n / len(vs) for k, n in h.items()}


def resumo(vs):
    return {"media": st.mean(vs), "mediana": st.median(vs), "fracao": hist(vs)}


def percentis(vs):
    o = sorted(vs)
    p = lambda q: o[min(len(o) - 1, int(q * len(o)))]
    return {"media_S": st.mean(vs) / S, "p05_S": p(0.05) / S, "p50_S": p(0.50) / S, "p95_S": p(0.95) / S,
            "media_fracao_amax": st.mean(vs) / A_MAX, "p95_fracao_amax": p(0.95) / A_MAX}


# ------------------------------------------------------------------ a leitura e a conferencia C0
def ler_sondas(pasta):
    """os *_sonda.json do vidas.tar.gz, por nome da vida "genoma|dono|semente" (a chave do medidas.json)"""
    out = {}
    with tarfile.open(pasta / "vidas.tar.gz", "r:gz") as t:
        for m in sorted(t.getmembers(), key=lambda x: x.name):
            base = m.name.rsplit("/", 1)[-1]
            if not m.isfile() or not base.endswith("_sonda.json"):
                continue
            genoma, dono, semente = base[:-len("_sonda.json")].split("_")
            chave = f"{genoma}|{dono}|{semente}"
            if chave in out:
                raise RuntimeError(f"sonda repetida no tar: {chave}")
            out[chave] = json.loads(t.extractfile(m).read().decode("utf-8"))
    return out


def medidas_da_replica(r):
    a, b = r["ticks"]["A"], r["ticks"]["B"]
    p = r["primeira"]
    if p is None:
        return {"escolha": None, "tempo_relativo": None, "tempo_total": 0.0}
    return {"escolha": 1.0 if p == "A" else 0.0, "tempo_relativo": a / (a + b), "tempo_total": (a + b) / JANELA}


def conferir(med, sondas):
    """C0 do plano: falha alto em qualquer diferenca"""
    if sorted(med) != sorted(sondas):
        raise RuntimeError(f"as vidas do tar e do medidas.json diferem: {len(sondas)} contra {len(med)}")
    n_rep = n_dec = 0
    for chave in sorted(med):
        reps = [r for d in sondas[chave]["por_dia"] for r in d["replicas"] if "sem_lugar" not in r]
        gravadas = med[chave]["medidas"]
        if len(reps) != len(gravadas):
            raise RuntimeError(f"{chave}: {len(reps)} replicas no tar, {len(gravadas)} no medidas.json")
        for r, g in zip(reps, gravadas):
            calc = {**medidas_da_replica(r), "agrado_inato": r["agrado"]["A"]["inato"] - r["agrado"]["B"]["inato"],
                    "agrado_agora": r["agrado"]["A"]["agora"] - r["agrado"]["B"]["agora"]}
            for campo, v in calc.items():
                if g[campo] != v:
                    raise RuntimeError(f"{chave}, replica {g['dia']}/{g['replica']}: {campo} {v!r} no tar, {g[campo]!r} no medidas.json")
            if sum(n for _, n in r["olhadas"]) != JANELA:
                raise RuntimeError(f"{chave}: os trechos nao somam {JANELA}")
            for rot in ("A", "B"):
                if sum(n for x, n in r["olhadas"] if x == rot) != r["ticks"][rot]:
                    raise RuntimeError(f"{chave}: os trechos de {rot} nao batem com os ticks")
            for d in r["decisoes"]:
                if set(d) != CHAVES_DECISAO:
                    raise RuntimeError(f"{chave}: uma decisao com as chaves {sorted(d)}, nao so acao e olha (a premissa do M4 errou)")
                if d["olha"] is not None and d["olha"] not in ID_ROTULO:
                    raise RuntimeError(f"{chave}: a decisao olha a TV {d['olha']!r}, que nao e das duas")
                n_dec += 1
            n_rep += 1
    return {"vidas": len(med), "replicas_conferidas": n_rep, "decisoes_conferidas": n_dec, "ok": True}


# ------------------------------------------------------------------ M1, M2 e M3 por replica
def m1_da_replica(r):
    tr = [x for x, _ in r["olhadas"]]
    out = {"episodios": 0, "saidas": 0, "trocas_diretas": 0, "voltas_mesma": 0, "voltas_outra": 0, "segunda_por": None}
    ultimo = None                    # a TV do ultimo trecho olhado
    vistas = []
    for i, x in enumerate(tr):
        if x is None:
            continue
        out["episodios"] += 1
        if i + 1 < len(tr) and tr[i + 1] is None:
            out["saidas"] += 1
        if i > 0 and tr[i - 1] is not None and tr[i - 1] != x:
            out["trocas_diretas"] += 1
            via = "troca_direta"
        elif i > 0 and tr[i - 1] is None and ultimo is not None:
            out["voltas_mesma" if x == ultimo else "voltas_outra"] += 1
            via = "volta"
        else:
            via = None
        if x not in vistas:
            vistas.append(x)
            if len(vistas) == 2:
                out["segunda_por"] = via
        ultimo = x
    out["voltas"] = out["voltas_mesma"] + out["voltas_outra"]
    return out


def pares_da_replica(r):
    """(tv olhada em t, desfecho em t+1, acao em t+1) de cada par de decisoes seguidas com a TV olhada em t"""
    ds = r["decisoes"]
    out = []
    for d0, d1 in zip(ds, ds[1:]):
        if d0["olha"] is None:
            continue
        x, y = ID_ROTULO[d0["olha"]], None if d1["olha"] is None else ID_ROTULO[d1["olha"]]
        out.append((x, "sai" if y is None else "fica" if y == x else "troca", d1["acao"]))
    return out


def ambas(r):
    return r["ticks"]["A"] > 0 and r["ticks"]["B"] > 0


def resumo_pares(pares):
    def fr(ps):
        n = len(ps)
        return {"n": n, **{k: (sum(1 for p in ps if p[1] == k) / n if n else None) for k in ("fica", "troca", "sai")}}
    acoes = {}
    for p in pares:
        if p[1] == "sai":
            acoes[p[2]] = acoes.get(p[2], 0) + 1
    return {"juntas": fr(pares), "A": fr([p for p in pares if p[0] == "A"]), "B": fr([p for p in pares if p[0] == "B"]),
            "acoes_na_saida": dict(sorted(acoes.items(), key=lambda kv: (-kv[1], kv[0])))}


def dif_fica(pares):
    pa = [p for p in pares if p[0] == "A"]
    pb = [p for p in pares if p[0] == "B"]
    if not pa or not pb:
        return None
    return sum(1 for p in pa if p[1] == "fica") / len(pa) - sum(1 for p in pb if p[1] == "fica") / len(pb)


def termo_gosto(agrado):
    return div_arred(W_GOSTO * (agrado - S // 2), S)


# ------------------------------------------------------------------ por run
def ler_run(pasta):
    med = json.loads((pasta / "medidas.json").read_text(encoding="utf-8"))
    sondas = ler_sondas(pasta)
    out = {"C0": conferir(med, sondas)}
    pets = []
    for chave in sorted(med):
        v = med[chave]
        reps = [r for d in sondas[chave]["por_dia"] for r in d["replicas"] if "sem_lugar" not in r]
        val = [r for r in reps if r["primeira"] is not None]
        inatos = {r["agrado"]["A"]["inato"] - r["agrado"]["B"]["inato"] for r in reps}
        if len(inatos) != 1:
            raise RuntimeError(f"{chave}: o agrado inato mudou na vida: {sorted(inatos)}")
        pares = [p for r in val for p in pares_da_replica(r)]
        pares_amb = [p for r in val if ambas(r) for p in pares_da_replica(r)]
        pets.append({"base": v["base"], "k": v["k"], "genoma": v["genoma_tipo"], "di": inatos.pop(), "validas": val,
                     "pares": pares, "dif": dif_fica(pares), "dif_amb": dif_fica(pares_amb)})
    for g in ("proprio", "vazio"):
        ps = [p for p in pets if p["genoma"] == g]
        val = [r for p in ps for r in p["validas"]]
        m1 = [m1_da_replica(r) for r in val]
        amb = [x for r, x in zip(val, m1) if ambas(r)]
        out[f"M1_{g}"] = {
            "n_pets": len(ps), "replicas_validas": len(val),
            **{k: resumo([x[k] for x in m1]) for k in ("episodios", "saidas", "trocas_diretas", "voltas", "voltas_mesma", "voltas_outra")},
            "fracao_com_volta": sum(1 for x in m1 if x["voltas"] > 0) / len(m1),
            "total_voltas_mesma": sum(x["voltas_mesma"] for x in m1), "total_voltas_outra": sum(x["voltas_outra"] for x in m1),
            "viu_as_duas": {"replicas": len(amb), "segunda_por_troca_direta": sum(1 for x in amb if x["segunda_por"] == "troca_direta"),
                            "segunda_por_volta": sum(1 for x in amb if x["segunda_por"] == "volta")}}
        todos = [q for p in ps for q in p["pares"]]
        com = [p for p in ps if p["dif"] is not None]
        m2 = {"pares": resumo_pares(todos),
              "pares_por_pet_medio": st.mean(len(p["pares"]) for p in ps),
              "pares_por_replica_valida_medio": len(todos) / len(val),
              "pets_com_pares_das_duas": len(com), "pets_sem_pares_das_duas": len(ps) - len(com),
              "pets_com_pares_das_duas_so_ambas": sum(1 for p in ps if p["dif_amb"] is not None)}
        if g == "proprio":
            f = lambda xs: spearman([p["di"] for p in xs if p["dif"] is not None], [p["dif"] for p in xs if p["dif"] is not None])
            fa = lambda xs: spearman([p["di"] for p in xs if p["dif_amb"] is not None],
                                     [p["dif_amb"] for p in xs if p["dif_amb"] is not None])
            m2["spearman_di_dif_fica"] = boot_unidades(ps, f)
            m2["spearman_di_dif_fica_so_ambas"] = boot_unidades(ps, fa)
        else:
            f = lambda xs: st.mean(p["dif"] for p in xs if p["dif"] is not None) if any(p["dif"] is not None for p in xs) else None
            m2["media_dif_fica"] = boot_unidades(ps, f)
        out[f"M2_{g}"] = m2
        ga = [abs(termo_gosto(r["agrado"]["A"]["agora"])) for r in val]
        gb = [abs(termo_gosto(r["agrado"]["B"]["agora"])) for r in val]
        dg = [abs(termo_gosto(r["agrado"]["A"]["agora"]) - termo_gosto(r["agrado"]["B"]["agora"])) for r in val]
        out[f"M3_{g}"] = {"replicas_validas": len(val), "abs_g_A": percentis(ga), "abs_g_B": percentis(gb), "abs_d_g": percentis(dg)}
    out["M4"] = {"status": "nao_mensuravel",
                 "razao": "a sonda grava de cada decisao so acao e olha (conferido em C0); os termos e os pesos das unidades nao estao no tar"}
    return out


res = {"plano": "docs/PLANO_ANALISE_V3_GOSTO_VISUAL_GVN2.md", "S": S, "w_gosto": W_GOSTO, "a_max": A_MAX,
       **{k: ler_run(p) for k, p in RUNS.items()}}
texto = json.dumps(res, indent=1, ensure_ascii=True, sort_keys=True) + "\n"
(Path(__file__).resolve().parent / "leitura.json").write_bytes(texto.encode("utf-8"))
print(texto)
