"""Rebalanceamento da escada dos NPCs da campanha (combate V21C). So sementes de CALIBRACAO.

    python experiments/calibrar_campanha.py --candidatos experiments/configs/campanha/candidatos.json
    python experiments/calibrar_campanha.py --validar     # sementes de validacao, NPCs de ConfigCampanha

Cada NPC candidato ({"total": x, "estilo": "<familia>:<nome>"}) luta contra:
  - as 8 formas adultas canonicas x 4 especies, com treino uniforme 0, 18 e 36 (stats absolutos);
  - os 4 adolescentes canonicos x 4 especies, com treino 0 e 18.
Familias de estilo: v2 (bots da bateria V2), v2c (bots redesenhados da V2C), v21 (gambits canonicos
de uma forma adulta sem as regras de tecnica, que o NPC nao tem).

Criterios da escada (fixados ANTES da calibracao; docs/REGISTRO_DESVIOS.md), sobre a media das
especies, com as licoes de docs/pve_treino.json:
  K1 degraus: media dos adultos sem treino t1 > t2 > t3, cada degrau >= 0,10.
  K2 tier 1 (prova de stats, sugerido crianca): adultos sem treino >= 0,70; adolescentes sem treino
     em [0,25, 0,60]; treino decide: adolescentes com +18 >= sem treino + 0,15.
  K3 tier 2 (prova de estilo, sugerido adolescente): adultos sem treino em [0,35, 0,65], com pelo
     menos 2 formas >= 0,60 e 2 formas <= 0,40; adolescentes sem treino <= 0,40.
  K4 tier 3 (chefe, sugerido adulto): nenhuma forma adulta sem treino >= 0,50; adolescentes sem
     treino <= 0,15; alcancavel: com +36, pelo menos 2 formas adultas >= 0,50.
"""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab.campanha import REGRAS_CAMPANHA, gambit_npc, perfil_de_stats  # noqa: E402
from digilab.combate_v2.v21 import partida as p21  # noqa: E402
from digilab.combate_v2.v21.bots import ADOLESCENTES, FORMAS, ADULTOS  # noqa: E402
from digilab.combate_v2.v21.catalogo import LINHA_DA_FORMA, LINHAS, Forma, carater_canonico, perfil  # noqa: E402
from digilab.combate_v2.v21.partida import Lutador  # noqa: E402
from digilab.config import CONFIG_CAMPANHA, CONFIG_CATALOGO, CONFIG_COMBATE_V2, STATS_V21  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402

SEM_CALIBRACAO = (3101, 3202, 3303, 3404, 3505)
SEM_VALIDACAO = (4101, 4202, 4303, 4404, 4505)
NIVEIS_ADULTO = (0, 18, 36)
NIVEIS_ADOL = (0, 18)
LIMIARES = {"degrau": 0.10, "t1_adulto_min": 0.70, "t1_adol": (0.25, 0.60), "t1_ganho_treino": 0.15,
            "t2_adulto": (0.35, 0.65), "t2_alto": 0.60, "t2_baixo": 0.40, "t2_n_extremos": 2, "t2_adol_max": 0.40,
            "t3_forma_max": 0.50, "t3_adol_max": 0.15, "t3_alcancavel": 0.50, "t3_n_alcancavel": 2}


def lutador_npc(spec: dict, rotulo: str) -> Lutador:
    stats = {k: spec["total"] / len(STATS_V21) for k in STATS_V21}
    est = spec.get("estagio", "adulto")
    return Lutador(f"npc:{rotulo}:{spec['estilo']}:{spec['total']}" + ("" if est == "adulto" else f":{est}")
                   + (f":e{spec['epsilon']}" if "epsilon" in spec else ""),
                   perfil_de_stats(rotulo, stats, est, cfg=REGRAS_CAMPANHA.v21),
                   gambit_npc(spec["estilo"], est), spec.get("epsilon", CONFIG_CAMPANHA.epsilon_npc))


def lutador_pet(tipo: str, nome: str, especie: str, nivel: int) -> Lutador:
    """tipo 'adulto' (nome = forma) ou 'adolescente' (nome = linha); treino uniforme absoluto."""
    tr = {k: nivel / len(STATS_V21) for k in STATS_V21} if nivel else None
    cfg = REGRAS_CAMPANHA.v21
    if tipo == "adulto":
        f = Forma(especie, "adulto", "sereno", LINHA_DA_FORMA[nome], nome)
        car, gl = carater_canonico(nome, cfg), ADULTOS[nome]
    else:
        f = Forma(especie, "adolescente", "sereno", nome)
        car = carater_canonico(next(x for x in FORMAS if LINHA_DA_FORMA[x] == nome), cfg)
        gl = ADOLESCENTES[nome]
    p = perfil(f, None, car, 1.0, cfg, treino=tr, normalizar_treino=False)
    return Lutador(f"{tipo}:{nome}+{nivel}@{especie}", p, gl, CONFIG_COMBATE_V2.epsilon_bots)


def taxa(a: Lutador, b: Lutador, sementes, n: int) -> float:
    pts = []
    for s in sementes:
        for k in range(n):
            sp = derivar_semente("calib-campanha", s, a.nome, b.nome, k)
            pts.append(p21.jogar(a, b, sp, REGRAS_CAMPANHA).pontos_a if k < n // 2
                       else 1.0 - p21.jogar(b, a, sp, REGRAS_CAMPANHA).pontos_a)
    return sum(pts) / len(pts)


def _tarefa(args):
    spec, tipo, nome, nivel, sementes, n = args
    esp = list(CONFIG_CATALOGO.especies_ativas)
    npc_ = lutador_npc(spec, "cand")
    return (tipo, nome, nivel), sum(taxa(lutador_pet(tipo, nome, e, nivel), npc_, sementes, n) for e in esp) / len(esp)


def medir(spec: dict, sementes, n: int, pool: ProcessPoolExecutor) -> dict:
    tarefas = [(spec, "adulto", f, nv, sementes, n) for f in FORMAS for nv in NIVEIS_ADULTO]
    tarefas += [(spec, "adolescente", l, nv, sementes, n) for l in LINHAS for nv in NIVEIS_ADOL]
    out = {"adulto": {f: {} for f in FORMAS}, "adolescente": {l: {} for l in LINHAS}}
    for (tipo, nome, nivel), v in pool.map(_tarefa, tarefas):
        out[tipo][nome][nivel] = round(v, 4)
    return out


def _media(d: dict, nivel: int) -> float:
    return sum(v[nivel] for v in d.values()) / len(d)


def criterios(m: dict) -> dict:
    """m = {tier1: medida, tier2: medida, tier3: medida}."""
    L = LIMIARES
    t1, t2, t3 = m["tier1"], m["tier2"], m["tier3"]
    ad = {t: _media(x["adulto"], 0) for t, x in m.items()}
    k1 = ad["tier1"] - ad["tier2"] >= L["degrau"] and ad["tier2"] - ad["tier3"] >= L["degrau"]
    a1_0, a1_18 = _media(t1["adolescente"], 0), _media(t1["adolescente"], 18)
    k2 = ad["tier1"] >= L["t1_adulto_min"] and L["t1_adol"][0] <= a1_0 <= L["t1_adol"][1] \
        and a1_18 >= a1_0 + L["t1_ganho_treino"]
    f2 = [v[0] for v in t2["adulto"].values()]
    a2_0 = _media(t2["adolescente"], 0)
    k3 = L["t2_adulto"][0] <= ad["tier2"] <= L["t2_adulto"][1] and sum(x >= L["t2_alto"] for x in f2) >= L["t2_n_extremos"] \
        and sum(x <= L["t2_baixo"] for x in f2) >= L["t2_n_extremos"] and a2_0 <= L["t2_adol_max"]
    a3_0 = _media(t3["adolescente"], 0)
    k4 = max(v[0] for v in t3["adulto"].values()) < L["t3_forma_max"] and a3_0 <= L["t3_adol_max"] \
        and sum(v[36] >= L["t3_alcancavel"] for v in t3["adulto"].values()) >= L["t3_n_alcancavel"]
    return {"K1": k1, "K2": k2, "K3": k3, "K4": k4, "ok": k1 and k2 and k3 and k4,
            "resumo": {"adultos_sem_treino": {t: round(v, 3) for t, v in ad.items()},
                       "adolescentes_sem_treino": {t: round(_media(x["adolescente"], 0), 3) for t, x in m.items()},
                       "adolescentes_18": {t: round(_media(x["adolescente"], 18), 3) for t, x in m.items()},
                       "adultos_36": {t: round(_media(x["adulto"], 36), 3) for t, x in m.items()}}}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidatos")
    ap.add_argument("--validar", action="store_true")
    ap.add_argument("--saida")
    ap.add_argument("-n", type=int, default=20, help="partidas por par por semente")
    a = ap.parse_args()
    with ProcessPoolExecutor() as pool:
        if a.validar:
            specs = {t: {"total": d["total_stats"], "estilo": d["estilo"]} for t, d in CONFIG_CAMPANHA.npcs.items()}
            m = {t.split("_")[0]: medir(s, SEM_VALIDACAO, a.n, pool) for t, s in specs.items()}
            out = {"conjunto": "validacao", "sementes": SEM_VALIDACAO, "npcs": specs, "medidas": m, "criterios": criterios(m)}
            print(json.dumps(out["criterios"], ensure_ascii=False))
        else:
            cand = json.loads(Path(a.candidatos).read_text(encoding="utf-8"))
            medidas = {}
            for rot, spec in cand["npcs"].items():
                medidas[rot] = medir(spec, SEM_CALIBRACAO, a.n, pool)
                m = medidas[rot]
                print(rot, spec, "adultos", {nv: round(_media(m["adulto"], nv), 3) for nv in NIVEIS_ADULTO},
                      "adol", {nv: round(_media(m["adolescente"], nv), 3) for nv in NIVEIS_ADOL},
                      {f: v[0] for f, v in m["adulto"].items()}, flush=True)
            out = {"conjunto": "calibracao", "sementes": SEM_CALIBRACAO, "candidatos": cand["npcs"], "medidas": medidas}
            if "escadas" in cand:
                out["escadas"] = {nome: criterios({t: medidas[r] for t, r in e.items()}) for nome, e in cand["escadas"].items()}
                for nome, c in out["escadas"].items():
                    print(nome, {k: c[k] for k in ("K1", "K2", "K3", "K4", "ok")}, c["resumo"], flush=True)
    out.update({"n_por_semente": a.n, "limiares": LIMIARES, "descricao": __doc__.strip().splitlines()[0]})
    if a.saida:
        Path(a.saida).parent.mkdir(parents=True, exist_ok=True)
        Path(a.saida).write_text(json.dumps(out, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
