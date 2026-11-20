"""Campanha na escala de stats (TAREFA_PLANILHA_PROGRESSAO, Parte C): calibra o fator de escala de cada NPC.

    python experiments/calibrar_escala.py --saida experiments/configs/escala/calibracao.json
    python experiments/calibrar_escala.py --validar --saida experiments/configs/escala/validacao.json

Escala LIGADA (ConfigEscala): o pet luta com o perfil do catalogo (treino normalizado) e E = vida do estagio x
(1 + beta x pontos); o NPC luta com perfil neutro e E = vida do estagio SUGERIDO x fator, epsilon da escala (0,2).
Pets: os mesmos bots de experiments/calibrar_progressao.py (criancas, adolescentes e adultos canonicos x 4 especies),
treino uniforme nos niveis NIVEIS.

Criterio (metas aprovadas pelo Matheus na Parte B, fixadas ANTES da calibracao), por NPC, media das formas do estagio
sugerido e das 4 especies:
  sem treino  <= 0,30
  com o treino tipico do lugar (ALCANCE de calibrar_progressao) >= 0,80
Escolha do fator: entre os que passam, o de maior folga min(0,30 - sem, com - 0,80); se nenhum passar, o de menor
violacao (registrado). Calibracao nas sementes 3101..3505; --validar mede os fatores de ConfigEscala nas 4101..4505.
"""
from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

from calibrar_campanha import SEM_CALIBRACAO, SEM_VALIDACAO, taxa  # noqa: E402
from calibrar_progressao import ALCANCE, NIVEIS, NOMES  # noqa: E402
from digilab.campanha import npc  # noqa: E402
from digilab.combate_v2.v21.bots import ADOLESCENTES, ADULTOS, CRIANCAS, FORMAS  # noqa: E402
from digilab.combate_v2.v21.catalogo import LINHA_DA_FORMA, Forma, carater_canonico, perfil  # noqa: E402
from digilab.combate_v2.v21.partida import Lutador  # noqa: E402
from digilab.campanha import REGRAS_CAMPANHA  # noqa: E402
from digilab.config import CONFIG_CAMPANHA, CONFIG_CATALOGO, CONFIG_COMBATE_V2, CONFIG_ESCALA_LIGADA, STATS_V21  # noqa: E402

META_SEM, META_COM = 0.30, 0.80
FATORES = tuple(round(0.8 + 0.1 * i, 1) for i in range(23))       # 0,8 .. 3,0
LUGAR = {"tier1": "crianca", "tier2": "adolescente", "tier3": "adulto"}


def lutador(est: str, nome: str, especie: str, nivel: int) -> Lutador:
    """Pet de referencia com a escala: treino uniforme (pontos), perfil normalizado, E pelo estagio e pelo treino."""
    cfg = REGRAS_CAMPANHA.v21
    tr = {k: nivel / len(STATS_V21) for k in STATS_V21} if nivel else None
    if est == "crianca":
        f, car, gl = Forma(especie, "crianca", nome), None, CRIANCAS[nome]
    elif est == "adolescente":
        f = Forma(especie, "adolescente", "sereno", nome)
        car, gl = carater_canonico(next(x for x in FORMAS if LINHA_DA_FORMA[x] == nome), cfg), ADOLESCENTES[nome]
    else:
        f, car, gl = Forma(especie, "adulto", "sereno", LINHA_DA_FORMA[nome], nome), carater_canonico(nome, cfg), ADULTOS[nome]
    p = perfil(f, None, car, 1.0, cfg, treino=tr, escala=CONFIG_ESCALA_LIGADA)
    return Lutador(f"{est}:{nome}+{nivel}@{especie}:escala", p, gl, CONFIG_COMBATE_V2.epsilon_bots)


def _tarefa(args):
    tier, fator, est, nome, nivel, sementes, n = args
    esc = replace(CONFIG_ESCALA_LIGADA, fator_npc={**CONFIG_ESCALA_LIGADA.fator_npc, tier: fator})
    adv = npc(tier, escala=esc)
    esp = list(CONFIG_CATALOGO.especies_ativas)
    return (tier, fator, est, nome, nivel), sum(taxa(lutador(est, nome, e, nivel), adv, sementes, n) for e in esp) / len(esp)


def nivel_tipico(tier: str) -> tuple[str, int]:
    lugar = CONFIG_CAMPANHA.npcs[tier]["lugar"]
    est = LUGAR[f"tier{lugar}"]
    teto = ALCANCE[f"tier{lugar}"][est]
    return est, max(nv for nv in NIVEIS[est] if nv <= teto)


def medir(tiers_fatores: dict, sementes, n: int, pool) -> dict:
    """{tier: {fator: {'sem': media, 'com': media, 'por_forma': {...}}}}"""
    tarefas = []
    for tier, fatores in tiers_fatores.items():
        est, nv = nivel_tipico(tier)
        for fa in fatores:
            for nome in NOMES[est]:
                for nivel in (0, nv):
                    tarefas.append((tier, fa, est, nome, nivel, sementes, n))
    bruto: dict = {}
    for (tier, fa, est, nome, nivel), v in pool.map(_tarefa, tarefas):
        bruto.setdefault(tier, {}).setdefault(fa, {}).setdefault(nome, {})[nivel] = round(v, 4)
    out = {}
    for tier, por_f in bruto.items():
        est, nv = nivel_tipico(tier)
        out[tier] = {}
        for fa, por_nome in por_f.items():
            sem = sum(v[0] for v in por_nome.values()) / len(por_nome)
            com = sum(v[nv] for v in por_nome.values()) / len(por_nome)
            out[tier][fa] = {"sem": round(sem, 4), "com": round(com, 4), "nivel_tipico": nv, "estagio": est,
                             "passa": sem <= META_SEM and com >= META_COM,
                             "folga": round(min(META_SEM - sem, com - META_COM), 4),
                             "travados": sorted(k for k, v in por_nome.items() if v[nv] < 0.5), "por_forma": por_nome}
    return out


def escolher(med_tier: dict) -> tuple[float, dict]:
    passam = {fa: m for fa, m in med_tier.items() if m["passa"]}
    pool = passam or med_tier
    fa = max(pool, key=lambda x: (pool[x]["folga"], -x))
    return fa, pool[fa]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--validar", action="store_true")
    ap.add_argument("--saida", required=True)
    ap.add_argument("-n", type=int, default=10, help="partidas por par por semente")
    ap.add_argument("--processos", type=int, default=8)
    a = ap.parse_args()
    tiers = list(CONFIG_CAMPANHA.npcs)
    with ProcessPoolExecutor(a.processos) as pool:
        if a.validar:
            med = medir({t: [CONFIG_ESCALA_LIGADA.fator_npc[t]] for t in tiers}, SEM_VALIDACAO, a.n, pool)
            res = {t: next(iter(med[t].values())) for t in tiers}
            out = {"conjunto": "validacao", "sementes": SEM_VALIDACAO, "fator_npc": dict(CONFIG_ESCALA_LIGADA.fator_npc),
                   "resultado": res, "ok": all(r["passa"] for r in res.values())}
            for t, r in res.items():
                print(f"{t}: fator {CONFIG_ESCALA_LIGADA.fator_npc[t]} sem {r['sem']:.3f} com {r['com']:.3f} "
                      f"{'OK' if r['passa'] else 'REPROVA'} travados {r['travados']}", flush=True)
        else:
            med = medir({t: list(FATORES) for t in tiers}, SEM_CALIBRACAO, a.n, pool)
            escolha = {}
            for t in tiers:
                fa, m = escolher(med[t])
                escolha[t] = {"fator": fa, "sem": m["sem"], "com": m["com"], "passa": m["passa"], "folga": m["folga"],
                              "travados": m["travados"]}
                print(f"{t}: fator {fa} sem {m['sem']:.3f} com {m['com']:.3f} {'OK' if m['passa'] else 'NENHUM PASSA'}", flush=True)
            out = {"conjunto": "calibracao", "sementes": SEM_CALIBRACAO, "fatores_testados": list(FATORES),
                   "medidas": {t: {str(k): {x: y for x, y in v.items() if x != "por_forma"} for k, v in med[t].items()} for t in tiers},
                   "escolha": escolha}
    out.update({"n_por_semente": a.n, "metas": {"sem_treino_max": META_SEM, "com_treino_min": META_COM},
                "epsilon_npc": CONFIG_ESCALA_LIGADA.epsilon_npc, "beta_treino": CONFIG_ESCALA_LIGADA.beta_treino,
                "vida_por_estagio": CONFIG_ESCALA_LIGADA.vida_por_estagio, "descricao": __doc__.strip().splitlines()[0]})
    Path(a.saida).parent.mkdir(parents=True, exist_ok=True)
    Path(a.saida).write_text(json.dumps(out, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
