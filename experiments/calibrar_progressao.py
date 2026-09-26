"""Progressao da campanha: o pet basico perde do NPC do seu estagio e o pet melhorado vence.

    python experiments/calibrar_progressao.py --candidatos experiments/configs/progressao/r0.json --saida ...
    python experiments/calibrar_progressao.py --validar --saida experiments/configs/progressao/validacao.json

Pedido do Matheus: um pet com stats basicos nao pode vencer o NPC inicial; um com stats maiores
consegue, para o jogador ter de melhorar o pet antes de cada desafio. "Melhorar" = treino (pontos
absolutos na campanha) e evolucao (multiplicador de estagio). Os niveis de treino sao os de uma vida
real (artifacts_treino/vidas, media dos bracos coerentes): fim da infancia ~8 pontos, fim da
adolescencia ~15, adulto ~29 (o exigente chega a ~36).

Decisao do Matheus (a evolucao pesava mais que o treino): o treino fica mais forte. Cada ponto
treinado vale `peso` pontos de stat em combate (ConfigTreino.peso_ponto_combate); os candidatos
variam o peso junto com o NPC do tier 1 ({"peso": k} no candidato).

Bots: bots.CRIANCAS (espelho das sementes da web), adolescentes e adultos canonicos, x 4 especies,
treino uniforme absoluto. Regras da campanha (V21C). Sementes de CALIBRACAO (3101..3505) nas rodadas;
--validar usa as de VALIDACAO (4101..4505) e os NPCs de ConfigCampanha.

Criterios (fixados ANTES da calibracao; media das especies e das formas do estagio):
  P1 tier 1 (estagio sugerido crianca): crianca sem treino <= 0,30; crianca +8 >= 0,55;
     adolescente sem treino <= 0,50 (evoluir sem treinar nao basta).
  P2 tier 2 (adolescente): adolescente sem treino <= 0,30; adolescente +15 >= 0,50 em pelo menos 2 das
     4 linhas (o estilo pesa); adulto sem treino (media) <= 0,45.
  P3 tier 3 (adulto): adulto sem treino: nenhuma forma >= 0,50 e media <= 0,20; adulto +29: pelo menos
     2 formas >= 0,50 (alcancavel com o treino de uma vida normal).
  P4 escada: adultos sem treino t1 > t2 > t3, cada degrau >= 0,10 (o K1 de calibrar_campanha).
"""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

from calibrar_campanha import SEM_CALIBRACAO, SEM_VALIDACAO, lutador_npc, taxa  # noqa: E402
from digilab.campanha import REGRAS_CAMPANHA  # noqa: E402
from digilab.combate_v2.v21.bots import ADOLESCENTES, ADULTOS, CRIANCAS, FORMAS  # noqa: E402
from digilab.combate_v2.v21.catalogo import LINHA_DA_FORMA, LINHAS, Forma, carater_canonico, perfil  # noqa: E402
from digilab.combate_v2.v21.partida import Lutador  # noqa: E402
from digilab.config import CONFIG_CAMPANHA, CONFIG_CATALOGO, CONFIG_COMBATE_V2, CONFIG_TREINO, STATS_V21  # noqa: E402

NIVEIS = {"crianca": (0, 4, 8, 12), "adolescente": (0, 8, 15, 22), "adulto": (0, 15, 29, 36)}
NOMES = {"crianca": tuple(CRIANCAS), "adolescente": tuple(LINHAS), "adulto": tuple(FORMAS)}
TIERS = ("tier1", "tier2", "tier3")


def lutador(est: str, nome: str, especie: str, nivel: int, peso: float = 1.0) -> Lutador:
    """peso: quanto cada ponto de treino vale em stat de combate (ConfigTreino.peso_ponto_combate)."""
    cfg = REGRAS_CAMPANHA.v21
    # catalogo.com_treino ja multiplica pelo peso do config; aqui vale o peso do candidato
    tr = {k: peso / CONFIG_TREINO.peso_ponto_combate * nivel / len(STATS_V21) for k in STATS_V21} if nivel else None
    if est == "crianca":
        f, car, gl = Forma(especie, "crianca", nome), None, CRIANCAS[nome]
    elif est == "adolescente":
        f = Forma(especie, "adolescente", "sereno", nome)
        car, gl = carater_canonico(next(x for x in FORMAS if LINHA_DA_FORMA[x] == nome), cfg), ADOLESCENTES[nome]
    else:
        f, car, gl = Forma(especie, "adulto", "sereno", LINHA_DA_FORMA[nome], nome), carater_canonico(nome, cfg), ADULTOS[nome]
    p = perfil(f, None, car, 1.0, cfg, treino=tr, normalizar_treino=False)
    return Lutador(f"{est}:{nome}+{nivel}@{especie}", p, gl, CONFIG_COMBATE_V2.epsilon_bots)


def _tarefa(args):
    spec, est, nome, nivel, sementes, n, peso = args
    esp = list(CONFIG_CATALOGO.especies_ativas)
    if spec.get("estagio") == "acompanha":      # NPC no estagio do pet, com o estilo daquele estagio
        spec = {**spec, "estagio": est, "estilo": spec["estilos"][est], "total": spec.get("totais", {}).get(est, spec["total"])}
        spec.pop("estilos"); spec.pop("totais", None)
    npc_ = lutador_npc(spec, "prog")
    return (est, nome, nivel), sum(taxa(lutador(est, nome, e, nivel, peso), npc_, sementes, n) for e in esp) / len(esp)


def medir(spec: dict, sementes, n: int, pool, peso: float = 1.0) -> dict:
    tarefas = [(spec, est, nome, nv, sementes, n, peso) for est in NIVEIS for nome in NOMES[est] for nv in NIVEIS[est]]
    out = {est: {nome: {} for nome in NOMES[est]} for est in NIVEIS}
    for (est, nome, nv), v in pool.map(_tarefa, tarefas):
        out[est][nome][nv] = round(v, 4)
    return out


def media(m: dict, est: str, nivel: int) -> float:
    return sum(v[nivel] for v in m[est].values()) / len(m[est])


def criterios(m: dict) -> dict:
    t1, t2, t3 = (m[t] for t in TIERS)
    c = {
        "P1": media(t1, "crianca", 0) <= 0.30 and media(t1, "crianca", 8) >= 0.55 and media(t1, "adolescente", 0) <= 0.50,
        "P2": media(t2, "adolescente", 0) <= 0.30 and sum(v[15] >= 0.50 for v in t2["adolescente"].values()) >= 2
        and media(t2, "adulto", 0) <= 0.45,
        "P3": max(v[0] for v in t3["adulto"].values()) < 0.50 and media(t3, "adulto", 0) <= 0.20
        and sum(v[29] >= 0.50 for v in t3["adulto"].values()) >= 2,
    }
    ad = [media(x, "adulto", 0) for x in (t1, t2, t3)]
    c["P4"] = ad[0] - ad[1] >= 0.10 and ad[1] - ad[2] >= 0.10
    c["ok"] = all(c[k] for k in ("P1", "P2", "P3", "P4"))
    c["resumo"] = {t: {est: {nv: round(media(m[t], est, nv), 3) for nv in NIVEIS[est]} for est in NIVEIS} for t in TIERS}
    return c


# criterios POR LINHA (pedido do Matheus depois que a media escondeu a linha cacadora travada no tier 1;
# fixados ANTES das rodadas 6+). Treino maximo por estagio: crianca 8, adolescente 15 (tier 2: 22),
# adulto 29 (chefe: 36).
ALCANCE = {"tier1": {"crianca": 8, "adolescente": 15, "adulto": 29},
           "tier2": {"adolescente": 22, "adulto": 29},
           "tier3": {"adulto": 36}}


def _alcanca(v: dict, teto: int) -> bool:
    return any(x >= 0.5 for nv, x in v.items() if int(nv) <= teto)


def criterios_linha(m: dict) -> dict:
    """Q1 basico perde; Q2 ninguem travado (toda linha/forma vence com o treino do estagio); Q3 = P4."""
    t1, t2, t3 = (m[t] for t in TIERS)
    q1 = {
        "tier1": all(v[0] <= 0.35 for v in t1["crianca"].values()) and sum(v[0] <= 0.5 for v in t1["adolescente"].values()) >= 3,
        "tier2": sum(v[0] <= 0.35 for v in t2["adolescente"].values()) >= 3 and sum(v[0] <= 0.5 for v in t2["adulto"].values()) >= 6,
        "tier3": all(v[0] <= 0.35 for v in t3["adulto"].values()),
    }
    travados = {t: {est: [n for n, v in m[t][est].items() if not _alcanca(v, teto)] for est, teto in ALCANCE[t].items()}
                for t in TIERS}
    q2 = {t: not any(travados[t].values()) for t in TIERS}
    ad = [media(x, "adulto", 0) for x in (t1, t2, t3)]
    q3 = ad[0] - ad[1] >= 0.10 and ad[1] - ad[2] >= 0.10
    return {"Q1": q1, "Q2": q2, "Q3": q3, "travados": travados, "ok": all(q1.values()) and all(q2.values()) and q3}


def resumo_tier(m: dict, tier: str) -> dict:
    """So o que vale para um tier isolado (Q1 e Q2 do tier): para varrer NPCs de um lugar por vez."""
    fake = {t: m for t in TIERS}
    c = criterios_linha(fake)
    return {"Q1": c["Q1"][tier], "Q2": c["Q2"][tier], "travados": c["travados"][tier]}


def criterios_lugares(m: dict) -> dict:
    """Criterios finais (decisao do Matheus: media + ninguem travado, com rivais a escolha por lugar).
    Cada rival: o pet basico do estagio sugerido perde (Q1 da media do lugar). O lugar: toda linha/forma
    alcanca >= 0,5 contra PELO MENOS UM rival com o treino do estagio (ALCANCE); no chefe, as formas que
    nao alcancam ficam listadas (excecao aceita: brigoes e cacadores)."""
    lug = {}
    for k, d in CONFIG_CAMPANHA.npcs.items():
        lug.setdefault(d["lugar"], []).append(k)
    t_de = {1: "tier1", 2: "tier2", 3: "tier3"}
    out = {}
    for L, ks in sorted(lug.items()):
        t = t_de[L]
        if t == "tier1":
            basico = {k: all(v[0] <= 0.35 for v in m[k]["crianca"].values()) and media(m[k], "crianca", 8) >= 0.55 for k in ks}
        elif t == "tier2":
            basico = {k: media(m[k], "adolescente", 0) <= 0.30 and media(m[k], "adulto", 0) <= 0.45 for k in ks}
        else:
            basico = {k: max(v[0] for v in m[k]["adulto"].values()) < 0.50 and media(m[k], "adulto", 0) <= 0.20
                      and sum(v[29] >= 0.50 for v in m[k]["adulto"].values()) >= 2 for k in ks}
        travados = {e: [n for n in m[ks[0]][e] if not any(_alcanca(m[k][e][n], teto) for k in ks)]
                    for e, teto in ALCANCE[t].items()}
        out[t] = {"rivais": ks, "basico_perde": basico, "travados": travados,
                  "adultos_sem_treino_melhor_rival": round(max(media(m[k], "adulto", 0) for k in ks), 3)}
    ad = [out[t]["adultos_sem_treino_melhor_rival"] for t in ("tier1", "tier2", "tier3")]
    out["degraus"] = ad[0] - ad[1] >= 0.10 and ad[1] - ad[2] >= 0.10
    excecao = {"adulto": ["duelista", "emboscador", "furioso", "sentinela"]}
    out["ok"] = (all(all(o["basico_perde"].values()) for t, o in out.items() if t.startswith("tier"))
                 and out["degraus"]
                 and not any(out["tier1"]["travados"].values()) and not any(out["tier2"]["travados"].values())
                 and all(set(v) <= set(excecao.get(e, [])) for e, v in out["tier3"]["travados"].items()))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidatos")
    ap.add_argument("--validar", action="store_true")
    ap.add_argument("--saida")
    ap.add_argument("-n", type=int, default=10, help="partidas por par por semente")
    a = ap.parse_args()
    with ProcessPoolExecutor() as pool:
        if a.validar:
            specs = {k: {"total": d["total_stats"], "estilo": d["estilo"], "estagio": d.get("estagio", "adulto"),
                         **({"epsilon": d["epsilon"]} if "epsilon" in d else {})} for k, d in CONFIG_CAMPANHA.npcs.items()}
            m = {k: medir(s_, SEM_VALIDACAO, a.n, pool, CONFIG_TREINO.peso_ponto_combate) for k, s_ in specs.items()}
            out = {"conjunto": "validacao", "sementes": SEM_VALIDACAO, "npcs": specs, "medidas": m,
                   "criterios_lugares": criterios_lugares(m)}
            print(json.dumps(out["criterios_lugares"], ensure_ascii=False))
        else:
            cand = json.loads(Path(a.candidatos).read_text(encoding="utf-8"))
            med = {}
            for rot, spec in cand["npcs"].items():
                med[rot] = m = medir({k: v for k, v in spec.items() if k != "peso"}, SEM_CALIBRACAO, a.n, pool,
                                     spec.get("peso", 1.0))
                print(rot, {est: {nv: round(media(m, est, nv), 2) for nv in NIVEIS[est]} for est in NIVEIS}, flush=True)
            out = {"conjunto": "calibracao", "sementes": SEM_CALIBRACAO, "candidatos": cand["npcs"], "medidas": med}
            if "tier" in cand:                 # varredura de um lugar: criterios por linha so desse tier
                out["por_tier"] = {r: resumo_tier(med[r], cand["tier"]) for r in med}
                for r, c in out["por_tier"].items():
                    print("  ", "OK" if c["Q1"] and c["Q2"] else "  ", r, c, flush=True)
            if "escadas" in cand:
                out["escadas"] = {k: criterios({t: med[r] for t, r in e.items()}) for k, e in cand["escadas"].items()}
                for k, c in out["escadas"].items():
                    c["linha"] = criterios_linha({t: med[r] for t, r in cand["escadas"][k].items()})
                    c["ok_final"] = c["ok"] and all(c["linha"]["Q2"].values())     # media P1-P4 + ninguem travado
                    print("OK" if c["ok_final"] else "  ", k, {x: c[x] for x in ("P1", "P2", "P3", "P4")},
                          "Q2", c["linha"]["Q2"], flush=True)
    out.update({"n_por_semente": a.n, "niveis": NIVEIS, "descricao": __doc__.strip().splitlines()[0]})
    if a.saida:
        Path(a.saida).parent.mkdir(parents=True, exist_ok=True)
        Path(a.saida).write_text(json.dumps(out, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
