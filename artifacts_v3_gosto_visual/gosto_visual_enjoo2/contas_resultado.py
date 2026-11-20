"""As contas do docs/RESULTADO_V3_GOSTO_VISUAL_ENJOO.md (a GV3b do adendo 2) que nao estao no analise.json, feitas so sobre o medidas.json desta pasta.

- a conferencia: a analise refeita a partir do medidas.json, comparada com o analise.json;
- o agrado inato (Delta_I) dos genomas proprios: o minimo, o maximo e quantos sao positivos;
- a parte da exposicao no agrado do cerebro (secao 4.2 do plano): por celula, a media, o minimo e o maximo de Delta_agora - Delta_I;
- os dias sem sonda e as replicas sem lugar (o adendo 2).

Uso (da raiz do repositorio): python artifacts_v3_gosto_visual/gosto_visual_enjoo2/contas_resultado.py
Grava contas_resultado.json nesta pasta.
"""
import json
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent
RAIZ = PASTA.parents[1]
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ))
import run_v3_gosto_visual as R  # noqa: E402

lidos = list(json.loads((PASTA / "medidas.json").read_text(encoding="utf-8")).values())
a = json.loads((PASTA / "analise.json").read_text(encoding="utf-8"))
refeito = {"familiarizacao": R.familiarizacao(lidos), "principal": R.analisar(lidos, R.BOOTSTRAP, False),
           "so_estaveis": R.analisar(lidos, R.BOOTSTRAP, True), "sem_lugar": R.contar_sem_lugar(lidos)}
igual = {k: json.dumps(v, sort_keys=True, default=str) == json.dumps(a[k], sort_keys=True, default=str) for k, v in refeito.items()}
di = [R.por_pet(r)["agrado_inato"] for r in lidos if r["genoma_tipo"] == "proprio"]
exposicao = {}
for g in R.GENOMAS:
    for d in R.DONOS:
        ps = [R.por_pet(r) for r in lidos if r["genoma_tipo"] == g and r["dono"] == d]
        ex = [p["agrado_agora"] - p["agrado_inato"] for p in ps if p["agrado_agora"] is not None]
        exposicao[f"{g}|{d}"] = {"n": len(ex), "media": sum(ex) / len(ex), "min": min(ex), "max": max(ex)}
out = {"analise_refeita_igual": igual,
       "agrado_inato_proprio": {"n": len(di), "min": min(di), "max": max(di), "positivos": sum(1 for x in di if x > 0)},
       "agrado_inato_vazio": sorted({R.por_pet(r)["agrado_inato"] for r in lidos if r["genoma_tipo"] == "vazio"}),
       "exposicao_delta_agora_menos_delta_inato": exposicao,
       "dias_sem_sonda": sum(r["dias_sem_sonda"] for r in lidos),
       "replicas_sem_lugar": sum(len(r["replicas_sem_lugar"]) for r in lidos)}
(PASTA / "contas_resultado.json").write_text(json.dumps(out, indent=1, ensure_ascii=True) + "\n", encoding="utf-8")
print(json.dumps(out, indent=1))
