"""A calibracao do g_plano do pet que pensa (J5; docs/PLANO_ANALISE_V2_PET_QUE_PENSA.md, secoes 5, 8 e 11; PP-6).

So o `g_plano` se calibra, na grade {S/4, S/2, S}. Roda o P1-plan so na fase 1 (os dias 0 a D_a - 1, sem mudanca), nas unidades de
calibracao (bases 45101...45505, K_u = 4, prefixo `pet_que_pensa`): uma vida por unidade e ponto, pela bancada do J5
(`experiments/bancada_v2.py`, `rodar_pqp`, que grava as vidas e as rejoga do disco bit a bit).

- **A medida da regra:** por unidade, a fracao das decisoes com alvo em que o termo do plano muda a escolha (a sonda "quem decidiu", da
  acao ou do alvo), nos dias 4 a 6 (`bancada_v2.fracao_plano_dias`); por ponto, a media sobre as unidades com alguma decisao com alvo na
  janela.
- **A regra:** o menor `g_plano` com a media em [0,10; 0,40] (R-3: o planejador soma, nao domina). Se nenhum ponto cai na faixa, fica o
  mais perto dela (empate: o menor), com o desvio declarado.
- **A regra nao le** a escolha de x (`f_antes`), nem um contraste entre bracos: a fase 1 nao tem mudanca, e so o P1-plan roda.

Saida: `<pasta>/g_plano_<g>/` (a bancada: vidas/, medidas.json, meta.json) por ponto, `<pasta>/g_plano.json` (os pontos e a escolha) e
`<pasta>/meta.json`. Recusa a pasta que ja existe e as bases da validacao (secao 11).

    python experiments/run_v2_calibracao_pet_que_pensa.py --config experiments/configs/v2_pet_que_pensa/calibracao.json \\
        --saida artifacts_v2_pet_que_pensa/calibracao --processos 3

**O piloto (secao 6),** com `--piloto`, depois da calibracao e na mesma pasta: no `g_plano` escolhido (o `g_plano.json`), os 4 bracos x os 2
protocolos (T1, T2), nas mesmas unidades, em `<pasta>/piloto/<braco>/` (a bancada) e `<pasta>/piloto/piloto.json`. Serve para as premissas
(G-APRENDEU, G-OPORTUNIDADE, G-EXPOSICAO), as margens (`Delta_T1` = 1/2 x a media de `f_antes` do P1-plan no T1; `Delta_T2` = 1/2 x a media de
1 - `f_antes` do P1-plan no T2; <= 0,05 e o teste sem espaco, e a validacao nao roda), o N (o menor K_u de 4 a 10 com poder simulado >= 0,8
nos dois primarios, a alfa/2 cada, com o bootstrap das diferencas por unidade deslocadas para a margem, 2.000 replicas, e o N efetivo de
cada primario descontado pela taxa de unidades sem oportunidade no piloto; sem chegar, K_u = 10 com o poder declarado), o poder dos
secundarios (so relato) e o custo. Os numeros do piloto nao entram como evidencia: os contrastes saem so como descritivo. Recusa a pasta
`piloto/` que ja existe.

    python experiments/run_v2_calibracao_pet_que_pensa.py --config experiments/configs/v2_pet_que_pensa/calibracao.json \\
        --saida artifacts_v2_pet_que_pensa/calibracao --piloto --processos 4
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from experiments import bancada_v2 as bv  # noqa: E402
from experiments import run_v2_experimento_maior as em  # noqa: E402
from digilab.metrics import bootstrap_ic, contraste_pareado  # noqa: E402

CHAVE = "calibracao_g_plano"
BRACO_CALIBRACAO = "P1-plan"
PROTOCOLO_CALIBRACAO = "fase1"


def validar(cfg: dict) -> dict:
    """A config da calibracao: a do J5 (validada ponto a ponto pela bancada) mais `calibracao_g_plano` = {grade, dias, faixa}. So o
    P1-plan e a fase 1; o `g_plano` vem da grade, nunca da config. Fora das sementes dos testes, so as bases de calibracao."""
    if CHAVE not in cfg:
        raise ValueError(f"config da calibracao do g_plano sem {CHAVE!r}")
    if "g_plano" in cfg:
        raise ValueError("a calibracao escolhe o g_plano: a config nao o traz (a grade vem em 'calibracao_g_plano')")
    if list(cfg.get("bracos", [])) != [BRACO_CALIBRACAO] or list(cfg.get("protocolos", [])) != [PROTOCOLO_CALIBRACAO]:
        raise ValueError(f"a calibracao roda so o {BRACO_CALIBRACAO} na {PROTOCOLO_CALIBRACAO} (secao 5)")
    c = cfg[CHAVE]
    if set(c) != {"grade", "dias", "faixa"}:
        raise ValueError(f"{CHAVE}: {{'grade', 'dias', 'faixa'}}, nao {sorted(c)}")
    grade = list(c["grade"])
    if not grade or any(type(g) is not int or g <= 0 for g in grade) or grade != sorted(set(grade)):
        raise ValueError(f"grade do g_plano {grade}: inteiros > 0, crescentes, sem repetir")
    d_a = int(cfg.get("d_a", bv.D_A_PQP))
    ini, fim = c["dias"]
    if not 0 <= ini <= fim <= d_a - 1:
        raise ValueError(f"dias da regra {c['dias']}: dentro da fase 1 (0 a {d_a - 1})")
    lo, hi = c["faixa"]
    if not 0 <= lo < hi <= 1:
        raise ValueError(f"faixa da regra {c['faixa']}")
    if "unidades" in cfg:
        validacao = set(cfg["unidades"]["bases"]) & set(bv.BASES_PET_QUE_PENSA["validacao"])
        if validacao:
            raise bv.SementeSemPlano(f"bases {sorted(validacao)} da validacao do J5: a calibracao recusa (secao 11)")
    for g in grade:
        bv.validar_config_pqp(config_do_ponto(cfg, g))
    return cfg


def config_do_ponto(cfg: dict, g: int) -> dict:
    return {**{k: v for k, v in cfg.items() if k != CHAVE}, "g_plano": g}


def _rodar_ponto(cfg_ponto: dict, pasta: str) -> dict:
    """um ponto da grade pela bancada do J5 (num processo proprio, com --processos): devolve as medidas gravadas"""
    t = time.time()
    bv.rodar_pqp(cfg_ponto, Path(pasta))
    medidas = json.loads((Path(pasta) / "medidas.json").read_text(encoding="utf-8"))
    return {"medidas": medidas, "parede_s": time.time() - t}


def fracoes_do_ponto(medidas: dict, dias: tuple) -> dict:
    """por unidade (uma vida do P1-plan na fase 1), a fracao da regra; a media sobre as unidades com decisao com alvo na janela"""
    por_unidade = []
    for nome in sorted(medidas):
        m = medidas[nome]
        if m["braco"] != BRACO_CALIBRACAO or m["protocolo"] != PROTOCOLO_CALIBRACAO:
            raise ValueError(f"vida {nome} fora da calibracao")
        por_unidade.append({"vida": nome, "semente": m["semente"], "unidade": m.get("unidade"), "g_plano": m["g_plano"],
                            **bv.fracao_plano_dias(m, tuple(dias))})
    com = [u["fracao"] for u in por_unidade if u["fracao"] is not None]
    return {"por_unidade": por_unidade, "n_unidades": len(por_unidade), "sem_alvo": len(por_unidade) - len(com),
            "media": None if not com else sum(com) / len(com)}


def escolha(pontos: list, faixa: tuple) -> dict:
    """A regra da secao 5: o menor g_plano com a media na faixa; senao, o mais perto dela (empate, o menor), com o desvio."""
    lo, hi = faixa
    validos = [p for p in pontos if p["media"] is not None]
    if not validos:
        raise RuntimeError("nenhum ponto da grade com decisao com alvo na janela da regra")
    dentro = [p for p in validos if lo <= p["media"] <= hi]
    if dentro:
        p = min(dentro, key=lambda q: q["g_plano"])
        return {"g_plano": p["g_plano"], "media": p["media"], "fechou": True, "desvio": 0.0}
    dist = lambda q: lo - q["media"] if q["media"] < lo else q["media"] - hi  # noqa: E731
    p = min(validos, key=lambda q: (dist(q), q["g_plano"]))
    return {"g_plano": p["g_plano"], "media": p["media"], "fechou": False, "desvio": dist(p),
            "lado": "abaixo" if p["media"] < lo else "acima"}


def rodar(cfg: dict, pasta: Path, processos: int = 1) -> dict:
    if pasta.exists():
        raise FileExistsError(f"{pasta}: a pasta de saida da calibracao do g_plano ja existe")
    validar(cfg)
    c = cfg[CHAVE]
    grade, dias, faixa = list(c["grade"]), tuple(c["dias"]), tuple(c["faixa"])
    pasta.mkdir(parents=True)
    t0 = time.time()
    tarefas = [(config_do_ponto(cfg, g), str(pasta / f"g_plano_{g}")) for g in grade]
    if processos > 1:
        with ProcessPoolExecutor(max_workers=min(processos, len(tarefas))) as ex:
            resultados = list(ex.map(_rodar_ponto, *zip(*tarefas)))
    else:
        resultados = [_rodar_ponto(*t) for t in tarefas]
    pontos = []
    for g, r in zip(grade, resultados):
        f = fracoes_do_ponto(r["medidas"], dias)
        if any(u["g_plano"] != g for u in f["por_unidade"]):
            raise RuntimeError(f"o ponto g_plano {g} tem vidas com outro g_plano")
        cpu = [m["custo"]["cpu_s"] for m in r["medidas"].values()]
        pontos.append({"g_plano": g, **f, "parede_s": r["parede_s"], "cpu_s_por_vida": sum(cpu) / len(cpu)})
    e = escolha(pontos, faixa)
    out = {"regra": {"medida": "fracao das decisoes com alvo em que a sonda do plano muda a escolha (acao ou alvo), media sobre as "
                                "unidades", "dias": list(dias), "faixa": list(faixa), "grade": grade,
                     "fonte": "PLANO_ANALISE_V2_PET_QUE_PENSA, secao 5 (PP-6, R-3)"},
           "pontos": pontos, "escolha": e, "parede_s": time.time() - t0}
    bv._gravar(pasta / "g_plano.json", bv._dump(out))
    bv._gravar(pasta / "meta.json", bv._dump({**bv.meta(cfg), "plano": bv.PLANO_PQP,
                                              "modelo_mundo_sha256": bv._sha(RAIZ / "digilab" / "modelo_mundo.py"),
                                              "orquestrador_sha256": bv._sha(Path(__file__)), "processos": processos}))
    return out


# ================================================================== o piloto (secao 6 do plano)
PROTOCOLOS_PILOTO = ("T1", "T2")
PRIMARIOS = {"G-T1": ("t1", "q", "P1-plan", "P1"), "G-T2": ("t2", "m", "P1-plan", "P1-plan-desfecho")}
SECUNDARIOS = {"G-T1-DESF": ("t1", "q", "P1-plan-desfecho", "P1"), "G-T1-CONG": ("t1", "q", "P1-plan", "P1-plan-cong"),
               "G-T2-HAB": ("t2", "m", "P1-plan", "P1"), "G-T2-CONG": ("t2", "m", "P1-plan", "P1-plan-cong")}
PODER_PILOTO = {"k_min": 4, "k_max": 10, "replicas": 2000, "alvo": 0.8, "alfa": 0.025, "alfas_relato": [0.0125, 0.05]}
BOOTSTRAP_PILOTO = {"reamostragens": 10000, "semente": 4242, "nivel": 0.95}
MARGEM_MINIMA = 0.05                      # secao 6: uma margem <= 0,05 e o teste sem espaco (PROPOSTO)
LIMIAR_SEM = 0.25                         # G-OPORTUNIDADE e G-EXPOSICAO: no maximo 25% das unidades
LIMIAR_APRENDEU = 1 / 3                   # G-APRENDEU: o acaso entre os 3 tipos (secao 7); o adendo 5 usa 1/4 (PJ5-3, pelo orquestrador dele)
VIDAS_POR_UNIDADE = len(bv.BRACOS_PQP) * len(PROTOCOLOS_PILOTO)


def config_do_piloto(cfg: dict, g: int) -> dict:
    return {**config_do_ponto(cfg, g), "bracos": list(bv.BRACOS_PQP), "protocolos": list(PROTOCOLOS_PILOTO)}


def config_do_braco(cfg_p: dict, braco: str) -> dict:
    """um braco por run da bancada (os bracos em paralelo); o P1 sem o g_plano (a bancada o recusa sem braco com o planejador)"""
    c = {**cfg_p, "bracos": [braco]}
    if not bv.BRACOS_PQP[braco].planejador:
        del c["g_plano"]
    return c


def _rodar_braco(cfg_braco: dict, pasta: str) -> dict:
    return _rodar_ponto(cfg_braco, pasta)


def _por_unidade(medidas: dict) -> dict:
    """{(braco, protocolo): {semente: medida}}"""
    out: dict = {}
    for m in medidas.values():
        out.setdefault((m["braco"], m["protocolo"]), {})[m["semente"]] = m
    return out


def _difs(por: dict, teste: str, campo: str, a: str, b: str) -> dict:
    """{semente: (base, valor(a) - valor(b))} nas unidades em que os dois tem valor (com oportunidade)"""
    prot = "T1" if teste == "t1" else "T2"
    ma, mb = por[(a, prot)], por[(b, prot)]
    if set(ma) != set(mb):
        raise RuntimeError(f"{a} e {b} no {prot} com unidades diferentes")
    out = {}
    for s in sorted(ma):
        va, vb = ma[s][teste][campo], mb[s][teste][campo]
        if va is not None and vb is not None:
            out[s] = (ma[s]["unidade"]["base"] if ma[s].get("unidade") else s, va - vb)
    return out


def _agrupado(difs: dict) -> dict:
    grupos: dict = {}
    for base, v in difs.values():
        grupos.setdefault(base, []).append(v)
    return grupos


def premissas(por: dict, boot: dict, limiar_aprendeu: float = LIMIAR_APRENDEU) -> dict:
    """G-APRENDEU (f_antes do T1 com o IC95 inferior > 1/3, por braco), G-OPORTUNIDADE (<= 25% sem oportunidade, por braco e teste) e
    G-EXPOSICAO (<= 25% sem exposicao no T2, por braco). No piloto, descritivas."""
    out: dict = {"G-APRENDEU": {}, "G-OPORTUNIDADE": {}, "G-EXPOSICAO": {}}
    for braco in bv.BRACOS_PQP:
        fa = [m["t1"]["f_antes"] for m in por[(braco, "T1")].values() if m["t1"]["f_antes"] is not None]
        ic = bootstrap_ic(fa, boot["reamostragens"], boot["semente"], boot["nivel"]) if len(fa) >= 2 else None
        out["G-APRENDEU"][braco] = {"n": len(fa), "ic": ic, "passa": ic is not None and ic["ic_inferior"] > limiar_aprendeu}
        for prot, teste in (("T1", "t1"), ("T2", "t2")):
            ms = list(por[(braco, prot)].values())
            sem = sum(1 for m in ms if m[teste]["sem_oportunidade"])
            out["G-OPORTUNIDADE"][f"{braco}/{prot}"] = {"sem": sem, "n": len(ms), "fracao": sem / len(ms),
                                                         "passa": sem / len(ms) <= LIMIAR_SEM}
        ms = list(por[(braco, "T2")].values())
        sem = sum(1 for m in ms if m["t2"]["sem_exposicao"])
        out["G-EXPOSICAO"][braco] = {"sem": sem, "n": len(ms), "fracao": sem / len(ms), "passa": sem / len(ms) <= LIMIAR_SEM}
    return out


def margens(por: dict) -> dict:
    """Delta_T1 = 1/2 x media de f_antes do P1-plan no T1; Delta_T2 = 1/2 x media de (1 - f_antes) do P1-plan no T2 (o "n_antes" do plano
    e a fracao de buscas que vao as novas antes da mudanca, o f_antes do T2)."""
    f1 = [m["t1"]["f_antes"] for m in por[("P1-plan", "T1")].values() if m["t1"]["f_antes"] is not None]
    f2 = [m["t2"]["f_antes"] for m in por[("P1-plan", "T2")].values() if m["t2"]["f_antes"] is not None]
    d1 = None if not f1 else 0.5 * sum(f1) / len(f1)
    d2 = None if not f2 else 0.5 * sum(1 - f for f in f2) / len(f2)
    return {"delta_t1": d1, "n_t1": len(f1), "delta_t2": d2, "n_t2": len(f2), "minima": MARGEM_MINIMA,
            "com_espaco": {"T1": d1 is not None and d1 > MARGEM_MINIMA, "T2": d2 is not None and d2 > MARGEM_MINIMA}}


def n_efetivo(n: int, com_valor: int, total: int) -> int:
    """o N do primario descontado pela taxa de unidades sem oportunidade no piloto (o chao: a conta conservadora)"""
    return math.floor(n * com_valor / total)


def escolher_k_dois(difs_por: dict, deltas: dict, total: int, n_bases: int, poder: dict, semente: int) -> dict:
    """O menor K_u de k_min a k_max com poder simulado >= alvo nos DOIS primarios, a alfa cada (o Holm de 2); sem chegar, k_max."""
    tabela = []
    for k in range(poder["k_min"], poder["k_max"] + 1):
        n = n_bases * k
        linha = {"k": k, "n": n}
        for nome, difs in difs_por.items():
            ne = n_efetivo(n, len(difs), total)
            linha[nome] = {"n_efetivo": ne, "poder": em.poder_simulado([v for _b, v in difs.values()], deltas[nome], ne, poder["alfa"],
                                                                      poder["replicas"], semente)}
        tabela.append(linha)
    ok = lambda ln: all(ln[nm]["poder"] is not None and ln[nm]["poder"] >= poder["alvo"] for nm in difs_por)  # noqa: E731
    chega = [ln for ln in tabela if ok(ln)]
    e = chega[0] if chega else tabela[-1]
    return {"k": e["k"], "n": e["n"], "chega_ao_alvo": bool(chega), "escolhido": e, "tabela": tabela, **poder, "semente": semente}


def rodar_piloto(cfg: dict, pasta: Path, processos: int = 1, limiar_aprendeu: float = LIMIAR_APRENDEU) -> dict:
    validar(cfg)
    escolha_g = json.loads((pasta / "g_plano.json").read_text(encoding="utf-8"))["escolha"]
    saida = pasta / "piloto"
    if saida.exists():
        raise FileExistsError(f"{saida}: a pasta do piloto do J5 ja existe")
    g = escolha_g["g_plano"]
    cfg_p = config_do_piloto(cfg, g)
    bv.validar_config_pqp(cfg_p)
    saida.mkdir(parents=True)
    t0 = time.time()
    tarefas = [(config_do_braco(cfg_p, b), str(saida / b)) for b in bv.BRACOS_PQP]
    if processos > 1:
        with ProcessPoolExecutor(max_workers=min(processos, len(tarefas))) as ex:
            res = list(ex.map(_rodar_braco, *zip(*tarefas)))
    else:
        res = [_rodar_braco(*t) for t in tarefas]
    parede = time.time() - t0
    medidas = {nome: m for r in res for nome, m in r["medidas"].items()}
    if any(m["g_plano"] != (g if bv.BRACOS_PQP[m["braco"]].planejador else 0) for m in medidas.values()):
        raise RuntimeError("o piloto tem vida com o g_plano errado")
    por = _por_unidade(medidas)
    total = len(por[("P1", "T1")])
    n_bases = len(cfg["unidades"]["bases"]) if "unidades" in cfg else len(cfg["sementes"])
    boot, poder = BOOTSTRAP_PILOTO, PODER_PILOTO
    mg = margens(por)
    deltas = {"G-T1": mg["delta_t1"], "G-T2": mg["delta_t2"]}
    difs_p = {nm: _difs(por, *c) for nm, c in PRIMARIOS.items()}
    difs_s = {nm: _difs(por, *c) for nm, c in SECUNDARIOS.items()}
    if all(deltas[nm] is not None and deltas[nm] > 0 for nm in PRIMARIOS):
        n = escolher_k_dois(difs_p, deltas, total, n_bases, poder, boot["semente"])
        relato = {}
        for nm, difs in difs_s.items():
            d = mg["delta_t1"] if SECUNDARIOS[nm][0] == "t1" else mg["delta_t2"]
            ne = n_efetivo(n["n"], len(difs), total)
            relato[nm] = {"delta": d, "n_efetivo": ne, "poder": {str(a): em.poder_simulado([v for _b, v in difs.values()], d, ne, a,
                                                                                          poder["replicas"], boot["semente"])
                                                                 for a in poder["alfas_relato"]}}
            relato[nm]["subpotenciado"] = {a: (p is None or p < 0.5) for a, p in relato[nm]["poder"].items()}
    else:
        n, relato = None, None
    descritivo = {nm: {"unidades_com_valor": len(d), **contraste_pareado(_agrupado(d), boot["reamostragens"], boot["semente"])}
                  for nm, d in {**difs_p, **difs_s}.items()}
    cpu = {b: [m["custo"]["cpu_s"] for m in medidas.values() if m["braco"] == b] for b in bv.BRACOS_PQP}
    cpu_vida = sum(sum(v) for v in cpu.values()) / len(medidas)
    custo = {"cpu_s_por_vida": {b: sum(v) / len(v) for b, v in cpu.items()}, "cpu_s_por_vida_media": cpu_vida, "parede_s_piloto": parede,
             "processos": processos, "vidas_por_unidade": VIDAS_POR_UNIDADE}
    if n is not None:
        custo["validacao"] = {"n": n["n"], "vidas": n["n"] * VIDAS_POR_UNIDADE, "cpu_h": n["n"] * VIDAS_POR_UNIDADE * cpu_vida / 3600}
    out = {"g_plano": g, "escolha_g_plano": escolha_g, "unidades": total, "premissas": premissas(por, boot, limiar_aprendeu), "margens": mg, "n": n,
           "poder_secundarios": relato, "descritivo_nao_e_evidencia": descritivo, "custo": custo,
           "valida_validacao": all(mg["com_espaco"].values()),
           "regras": {"poder": poder, "bootstrap": boot, "margem_minima": MARGEM_MINIMA, "limiar_sem": LIMIAR_SEM, "limiar_aprendeu": limiar_aprendeu,
                      "fonte": "PLANO_ANALISE_V2_PET_QUE_PENSA, secoes 6 e 7"}}
    bv._gravar(saida / "piloto.json", bv._dump(out))
    bv._gravar(saida / "meta.json", bv._dump({**bv.meta(cfg_p), "plano": bv.PLANO_PQP, "g_plano": g,
                                              "modelo_mundo_sha256": bv._sha(RAIZ / "digilab" / "modelo_mundo.py"),
                                              "orquestrador_sha256": bv._sha(Path(__file__)), "processos": processos}))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="calibracao do g_plano do pet que pensa (PLANO_ANALISE_V2_PET_QUE_PENSA, secao 5)")
    ap.add_argument("--config", required=True)
    ap.add_argument("--saida", required=True)
    ap.add_argument("--processos", type=int, default=1, help="os pontos da grade (ou os bracos do piloto) em paralelo")
    ap.add_argument("--piloto", action="store_true", help="o piloto da secao 6, no g_plano escolhido (depois da calibracao, na mesma pasta)")
    a = ap.parse_args(argv)
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))
    if a.piloto:
        r = rodar_piloto(cfg, Path(a.saida), a.processos)
        mg, n = r["margens"], r["n"]
        print(f"piloto no g_plano {r['g_plano']}: Delta_T1 {mg['delta_t1']}, Delta_T2 {mg['delta_t2']}, "
              f"K_u {None if n is None else n['k']} (chega ao alvo: {None if n is None else n['chega_ao_alvo']}); em {a.saida}/piloto")
        return 0
    r = rodar(cfg, Path(a.saida), a.processos)
    e = r["escolha"]
    for p in r["pontos"]:
        print(f"g_plano {p['g_plano']}: media {p['media']}, {p['sem_alvo']} unidade(s) sem alvo na janela")
    print(f"escolha: g_plano {e['g_plano']} ({'fechou' if e['fechou'] else 'nao fechou, desvio ' + str(e['desvio'])}); em {a.saida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
