"""O resumo de todas as metas de uma pasta de medicoes (a saida de medir_tudo.py): uma linha por meta, com o valor que decide e se passa.
uso (em web/app): python scripts/equilibrio_tr/resumo_metas.py scripts/medicoes/equilibrio_tr/r2_0 [outra pasta para comparar]"""
import json, os, sys


def metas(d):
    L = lambda f: json.load(open(os.path.join(d, f), encoding="utf-8"))["metas"]
    r, f, m34, g1 = L("relogio.json"), L("formas.json"), L("estagio_p34.json"), L("g1.json")
    out = {
        "T-1": (f"{r['T-1']['duracao_media_s']} s / {r['T-1']['duracao_mediana_s']} s", r["T-1"]["passa"]),
        "T-2": (f"limite {r['T-2']['no_limite_total']}; pior par {r['T-2']['no_limite_pior_par']}", r["T-2"]["passa"]),
        "T-3": (f"p90 {r['T-3']['cidadela_p90_s']} s", r["T-3"]["passa"]),
        "T-4": (str(r["T-4"]["espelho_vitorias_a_entre_decididas"]), r["T-4"]["passa"]),
        "T-5": (str(r["T-5"]["reagiu_quando_livre_com_regra"]), r["T-5"]["passa"]),
        "F-1": ("fora: " + ", ".join(f"{k} {f['F-1']['forca'][k]}" for k in f["F-1"]["fora"]), f["F-1"]["passa"]),
        "F-2": (str(f["F-2"]["distancia"]), f["F-2"]["passa"]),
        "F-3": ("", f["F-3"]["passa"]),
        "F-4": (json.dumps(f["F-4"]["champion"]) + f"; rookie {f['F-4']['rookie_sereno_x_arisco']}", f["F-4"]["passa"]),
        "F-5": (f"champion {f['F-5']['champion_cacador_x_perto']}; ultimate {f['F-5']['ultimate_longe_x_perto']}", f["F-5"]["passa"]),
        "F-6": (", ".join(f"{k} {v['efeito']}" for k, v in f["F-6"]["passivas"].items() if abs(v["efeito"]) > .1), f["F-6"]["passa"]),
        "F-7": (json.dumps(f["F-7"]["forca"]), f["F-7"]["passa"]),
        "P-1": ("", L("estagio_p1.json")["P-1"]["passa"]),
        "P-2": ("", L("estagio_p2.json")["P-2"]["passa"]),
        "P-3": (f"champion {m34['P-3']['champion']['media']}; ultimate {m34['P-3']['ultimate']['media']}", m34["P-3"]["passa"]),
        "P-4": (f"champion {m34['P-4']['champion']['qualificados']}; ultimate {m34['P-4']['ultimate']['qualificados']}", m34["P-4"]["passa"]),
        "G-1": ("fora: " + ", ".join(f"{k} (sem {v['sem']}, com {v['com']}, pior {v['pior']} {v['pior_forma']})" for k, v in g1["G-1"]["arenas"].items() if not v["passa"]), g1["G-1"]["passa"]),
        "I-1": (str(g1["I-1"]["pior_lider_sem_treino"]), g1["I-1"]["passa"]),
    }
    g2 = L("g2.json")["G-2"]; out["G-2"] = ("fora: " + ", ".join(k for k, v in g2["desafiantes"].items() if not v["passa"]), g2["passa"])
    g3 = L("g3.json")["G-3"]; out["G-3"] = (f"{g3['min']} a {g3['max']}; fora {g3['fora']}", g3["passa"])
    g4 = L("g4.json")["G-4"]; out["G-4"] = (f"{g4['melhor']} e {g4['pior']}", g4["passa"])
    g5 = L("g5.json")["G-5"]; out["G-5"] = (str(g5["uma_serie"]), g5["passa"])
    g6 = L("g6.json")["G-6"]; out["G-6"] = (", ".join(f"{k} {v['taxa']}" for k, v in g6["niveis"].items()), g6["passa"])
    out["I-2"] = ("", L("i2.json")["I-2"]["passa"])
    i3 = L("i3.json")["I-3"]; out["I-3"] = (str(i3["max"]), i3["passa"])
    i4 = L("i4.json")["I-4"]; out["I-4"] = (", ".join(f"{k} {v['efeito_medio']}" for k, v in i4["cartas"].items()), i4["passa"])
    i5 = L("i5.json")["I-5"]; out["I-5"] = (", ".join(f"{k} {v['media']}" for k, v in i5["chips"].items()), i5["passa"])
    return out


ds = sys.argv[1:]
ms = [metas(d) for d in ds]
for k in ms[0]:
    print(k, " | ".join(f"{'sim' if m[k][1] else 'NAO'} {m[k][0]}" for m in ms))
