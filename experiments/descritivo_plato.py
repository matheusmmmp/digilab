"""V2, DESCRITIVO-PLATO: o aprendiz apaga a preferencia inata ou aprende qual fruta faz mal? (docs/TAREFA_V2_DESCRITIVO_PLATO.md; decisao
V-3 e pergunta Q-1 de docs/LEITURA_V2_VALIDACAO_UNICA.md). POS HOC DESCRITIVO, rotulado como tal: sem run nova, sem semente nova, sem gate,
sem mudar nenhuma leitura registrada.

As vidas sao REGENERADAS da config e do codigo (a bancada e deterministica: a mesma espec da a mesma vida), rejogadas do proprio log bit a
bit (G1) e conferidas contra as medidas gravadas (consumos, contagem das frutas, taxa da fruta ruim em toda janela, interacoes); divergiu,
falha alto:
    validacao unica     experiments/configs/v2_experimento_maior/validacao.json, bases 30101...30505 (K = 6), o cerebro A;
                        contra artifacts_v2_validacao_unica/frutas/medidas.json
    comparacao A x C    experiments/configs/v2_comparacao_cerebros/validacao_ac.json, bases 29101...29505 (K = 1), A e C;
                        contra artifacts_v2_comparacao_cerebros/validacao/medidas.json
Bracos P0, P1, P2, P2e e P3 (as vidas fechadas; os so cuidado ficam de fora), nas tres condicoes das frutas, dono atencioso.

O que se le de cada vida, nas janelas inicial (dias 1-7) e final (dias 8-14; no mutavel e o depois da troca), com a fruta classificada pelo
efeito VIGENTE no tick (boa > 0, neutra = 0, ruim < 0 no humor; no mutavel muda na troca; conferido contra o efeito de cada consumo):
    1. consumo por fruta    a fracao dos consumos da boa, da neutra e da ruim (comer por igual da ~1/3 em cada uma)
    2. escolha com varias   nas decisoes de comer com duas frutas ou mais e a ruim presente: a fracao em que a ruim foi escolhida, contra o
                            acaso (1/k) e contra o herdado (a escolha pelo incentivo do genoma, o sorteio do instinto)
    3. comer com uma so     nas decisoes com uma fruta so no cenario: p(comer) quando ela e a boa, a neutra e a ruim
    4. pesos no fim         A: o peso de cada fruta na escolha (prior S) e o termo de presenca na decisao de comer (prior 0);
                            C: apetitivo e aversivo da celula de identidade da fruta (escolha) e, para comer, a soma das celulas do objeto
                            daquela fruta (presenca e fome x presenca)
Saida: artifacts_v2_descritivo_plato/{validacao_unica,comparacao}.json e resumo.json; o relatorio em docs/DESCRITIVO_V2_PLATO.md.

    python experiments/descritivo_plato.py
"""
from __future__ import annotations

import argparse
import json
import platform
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import cerebro_c_bancada as cbc  # noqa: E402
import run_v2_comparacao_cerebros as ac  # noqa: E402
import run_v2_experimento_maior as em  # noqa: E402
from digilab.config import TICKS_POR_DIA  # noqa: E402
from digilab.events import FRUTAS  # noqa: E402
from digilab.metrics import bootstrap_ic, taxa_fruta_ruim  # noqa: E402

CONFIG_VU = "experiments/configs/v2_experimento_maior/validacao.json"
MEDIDAS_VU = "artifacts_v2_validacao_unica/frutas/medidas.json"
CONFIG_AC = "experiments/configs/v2_comparacao_cerebros/validacao_ac.json"
MEDIDAS_AC = "artifacts_v2_comparacao_cerebros/validacao/medidas.json"
SAIDA = "artifacts_v2_descritivo_plato"
BRACOS = ("P0", "P1", "P2", "P2e", "P3")
MUNDOS = em.MUNDOS
DONO = "atencioso"
CLASSES = ("boa", "neutra", "ruim")
JANELAS = ("inicio", "final")
BOOT = {"reamostragens": 10000, "semente": 4242, "nivel": 0.95}
ROTULO = "POS HOC DESCRITIVO (V-3, Q-1): sem gate, sem run nova, nao muda nenhuma leitura registrada"


class Divergiu(RuntimeError):
    """A vida regenerada nao e a que as medidas gravadas descrevem."""


def _dump(obj) -> str:
    return json.dumps(obj, indent=1, sort_keys=True, ensure_ascii=False, default=repr) + "\n"


def _gravar(caminho: Path, texto: str) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(texto, encoding="utf-8", newline="\n")


# ------------------------------------------------------------------ a classe da fruta no tick


def classe(efeito: float) -> str:
    return "boa" if efeito > 0.0 else ("ruim" if efeito < 0.0 else "neutra")


def efeitos_no_tick(motor, tick: int) -> dict:
    """O efeito vigente de cada fruta no tick: no mutavel, o de antes ate a troca e o de depois a partir dela."""
    t = motor.troca
    if t is not None and tick >= t["tick"]:
        return t["efeito_depois"]
    if t is not None:
        return t["efeito_antes"]
    return motor.efeito_humor


def janela(tick: int, dias: int) -> str:
    return "inicio" if tick < (dias // 2) * TICKS_POR_DIA else "final"


# ------------------------------------------------------------------ o que se le de uma vida


def ler_vida(motor, dias: int) -> dict:
    for c in motor.consumos:                         # a classe pelo tick tem de ser a do efeito que o motor aplicou
        if efeitos_no_tick(motor, c["tick"])[c["fruta"]] != c["efeito_humor"]:
            raise Divergiu(f"consumo em {c['tick']}: efeito {c['efeito_humor']} fora do vigente")
    out = {}
    for jan in JANELAS:
        cons = {k: 0 for k in CLASSES}
        multi = {"n": 0, "ruim": 0, "acaso": 0.0, "herdado": 0.0}
        so = {k: {"n": 0, "comeu": 0} for k in CLASSES}
        for c in motor.consumos:
            if janela(c["tick"], dias) == jan:
                cons[classe(c["efeito_humor"])] += 1
        for o in motor.ofertas:
            if janela(o["tick"], dias) != jan:
                continue
            ef = efeitos_no_tick(motor, o["tick"])
            pres = o["presentes"]
            if len(pres) == 1:
                k = classe(ef[pres[0]])
                so[k]["n"] += 1
                so[k]["comeu"] += o["escolhida"] is not None
            elif o["escolhida"] is not None:
                ruins = [f for f in pres if ef[f] < 0.0]
                if not ruins:
                    continue
                if len(ruins) != 1:
                    raise Divergiu("mais de uma fruta ruim no cenario")
                multi["n"] += 1
                multi["ruim"] += ef[o["escolhida"]] < 0.0
                multi["acaso"] += 1.0 / len(pres)
                inc = o["incentivos"]
                tot = sum(inc[f] for f in pres)
                multi["herdado"] += (inc[ruins[0]] / tot) if tot > 0.0 else 1.0 / len(pres)
        n = sum(cons.values())
        out[jan] = {"consumos": cons, "n_consumos": n,
                    "fracao": {k: (cons[k] / n if n else None) for k in CLASSES},
                    "escolha_varias": {"n": multi["n"], "ruim": (multi["ruim"] / multi["n"]) if multi["n"] else None,
                                       "acaso": (multi["acaso"] / multi["n"]) if multi["n"] else None,
                                       "herdado": (multi["herdado"] / multi["n"]) if multi["n"] else None},
                    "uma_so": {k: {"n": so[k]["n"], "p_comer": (so[k]["comeu"] / so[k]["n"]) if so[k]["n"] else None} for k in CLASSES}}
    return out


def pesos_no_fim(politica, motor) -> dict:
    """Os pesos do fim da vida, por classe da fruta no fim (o efeito vigente no ultimo tick)."""
    cerebro = bv.do_braco(politica).cerebro
    ef = efeitos_no_tick(motor, motor._estado.tick)
    cl = {f: classe(ef[f]) for f in FRUTAS}
    d = cerebro.estado_interno()
    if "sinapses" in d:                              # o C
        idx = {nome: i for i, nome in enumerate(d["celulas"]["objeto"])}
        s, sf = d["sinapses"]["objeto"], d["sinapses_fruta"]
        out = {}
        for f in FRUTAS:
            i_id = d["celulas_fruta"].index(f"id_{f}")
            obj = [i for nome, i in idx.items() if nome == f"fruta_{f}" or nome.endswith(f"*fruta_{f}")]
            out[cl[f]] = {"escolha_apetitivo": sf["apetitivo"][i_id], "escolha_aversivo": sf["aversivo"][i_id],
                          "comer_apetitivo": sum(s["apetitivo"]["comer"][i] for i in obj),
                          "comer_aversivo": sum(s["aversivo"]["comer"][i] for i in obj)}
            out[cl[f]]["escolha_liquido"] = out[cl[f]]["escolha_apetitivo"] - out[cl[f]]["escolha_aversivo"]
            out[cl[f]]["comer_liquido"] = out[cl[f]]["comer_apetitivo"] - out[cl[f]]["comer_aversivo"]
        return out
    return {cl[f]: {"escolha": d["pesos_fruta"][f] - d["pesos_fruta_prior"][f],
                    "comer_presenca": d["pesos_comer_fruta"][f] - d["pesos_comer_fruta_prior"][f]} for f in FRUTAS}


# ------------------------------------------------------------------ regenerar e conferir


def conferir(bancada, vida, gravada: dict, nome: str) -> None:
    """A vida regenerada e a das medidas gravadas: interacoes, consumos, contagem das frutas e a taxa da fruta ruim em toda janela."""
    bancada.conferir_replay(vida, vida.motor.log.para_jsonl())          # G1: o replay do proprio log, bit a bit
    m = vida.motor
    consumos = [(c["tick"], c["efeito_humor"]) for c in m.consumos]
    agora = {"interacoes": vida.interacoes, "consumos": len(consumos), "contagem": dict(m.contagem_frutas),
             "taxa_fruta_ruim": taxa_fruta_ruim(consumos, bancada.janelas_frutas(m.condicao))}
    antes = {"interacoes": gravada["interacoes"], "consumos": gravada["frutas"]["consumos"],
             "contagem": gravada["frutas"]["contagem"], "taxa_fruta_ruim": gravada["frutas"]["taxa_fruta_ruim"]}
    if json.loads(json.dumps(agora)) != antes:
        raise Divergiu(f"{nome}: a vida regenerada difere das medidas gravadas")


def regenerar_vu(log=print) -> list[dict]:
    cfg = json.loads((RAIZ / CONFIG_VU).read_text(encoding="utf-8"))
    bancada = bv.bancada_da_config(em.config_da_bancada(cfg, em.BRACOS, MUNDOS, []))
    gravadas = json.loads((RAIZ / MEDIDAS_VU).read_text(encoding="utf-8"))
    unidades = bv.unidades_derivadas(cfg["unidades"]["bases"], int(cfg["unidades"]["k"]))
    linhas, t0 = [], time.perf_counter()
    for i, u in enumerate(unidades):
        for mundo in MUNDOS:
            for braco in BRACOS:
                v = bancada.vida(bv.EspecVida(DONO, braco, u["semente"], u["genoma"], mundo))
                conferir(bancada, v, gravadas[v.nome], v.nome)
                linhas.append({"cerebro": "A", "braco": braco, "mundo": mundo, "unidade": u["semente"],
                               "leitura": ler_vida(v.motor, bancada.dias), "pesos": pesos_no_fim(v.motor.politica, v.motor)})
        log(f"[VU {i + 1}/{len(unidades)}] {len(linhas)} vidas, {time.perf_counter() - t0:.0f} s")
    return linhas


def regenerar_ac(log=print) -> list[dict]:
    cfg = json.loads((RAIZ / CONFIG_AC).read_text(encoding="utf-8"))
    _, unidades = ac.modo_e_unidades(cfg)
    bancada = ac.bancada_da_config(cfg)
    gravadas = json.loads((RAIZ / MEDIDAS_AC).read_text(encoding="utf-8"))
    linhas = []
    for u in unidades:
        for mundo in MUNDOS:
            for braco in BRACOS:
                for letra, cer in (("A", "lobos"), ("C", cbc.CEREBRO_C)):
                    if braco == "P0" and letra == "C":
                        continue                                     # o P0 e comum
                    rotulo = "P0" if braco == "P0" else f"{letra}:{braco}"
                    v = bancada.vida(bv.EspecVida(DONO, braco, u["semente"], u["genoma"], mundo, cer))
                    nome = f"{rotulo.replace(':', '-')}~{mundo}@{u['semente']}"
                    conferir(bancada, v, gravadas[nome], nome)
                    linhas.append({"cerebro": "comum" if braco == "P0" else letra, "braco": braco, "mundo": mundo,
                                   "unidade": u["semente"], "leitura": ler_vida(v.motor, bancada.dias),
                                   "pesos": pesos_no_fim(v.motor.politica, v.motor)})
        log(f"[AC] unidade {u['semente']}: {len(linhas)} vidas")
    return linhas


# ------------------------------------------------------------------ tabelas (IC por bootstrap das unidades)


def ic(valores: list) -> dict:
    v = [x for x in valores if x is not None]
    if len(v) < 2:
        return {"media": v[0] if v else None, "ic_inferior": None, "ic_superior": None, "n": len(v), "sem_valor": len(valores) - len(v)}
    return {**bootstrap_ic(v, BOOT["reamostragens"], BOOT["semente"], BOOT["nivel"]), "sem_valor": len(valores) - len(v)}


def _media(xs):
    v = [x for x in xs if x is not None]
    return sum(v) / len(v) if v else None


def _dif(a, b):
    return None if a is None or b is None else a - b


def tabelas(linhas: list[dict]) -> dict:
    """Por cerebro, braco, mundo e janela, a media sobre as unidades com IC 95%: as fracoes, a escolha com varias (e a diferenca para o
    acaso e para o herdado, por unidade), p(comer) com uma so (e ruim - media das outras, por unidade) e os pesos no fim."""
    out = {}
    grupos: dict = {}
    for ln in linhas:
        grupos.setdefault((ln["cerebro"], ln["braco"], ln["mundo"]), []).append(ln)
    for (cer, braco, mundo), ls in sorted(grupos.items()):
        ls = sorted(ls, key=lambda x: x["unidade"])
        t = {}
        for jan in JANELAS:
            r = [x["leitura"][jan] for x in ls]
            ev = [x["escolha_varias"] for x in r]
            us = [x["uma_so"] for x in r]
            t[jan] = {
                "fracao": {k: ic([x["fracao"][k] for x in r]) for k in CLASSES},
                "fracao_ruim_menos_terco": ic([_dif(x["fracao"]["ruim"], 1 / 3) for x in r]),
                "consumos": ic([x["n_consumos"] for x in r]),
                "escolha_varias": {"ruim": ic([e["ruim"] for e in ev]), "acaso": ic([e["acaso"] for e in ev]),
                                   "herdado": ic([e["herdado"] for e in ev]),
                                   "ruim_menos_acaso": ic([_dif(e["ruim"], e["acaso"]) for e in ev]),
                                   "ruim_menos_herdado": ic([_dif(e["ruim"], e["herdado"]) for e in ev]),
                                   "decisoes": sum(e["n"] for e in ev)},
                "uma_so": {k: ic([u[k]["p_comer"] for u in us]) for k in CLASSES}
                | {"ruim_menos_outras": ic([_dif(u["ruim"]["p_comer"], _media([u["boa"]["p_comer"], u["neutra"]["p_comer"]])) for u in us]),
                   "ofertas": {k: sum(u[k]["n"] for u in us) for k in CLASSES}},
            }
        p = [x["pesos"] for x in ls]
        chaves = sorted(p[0]["ruim"])
        t["pesos_no_fim"] = {k: {cl: ic([x[cl][k] for x in p]) for cl in CLASSES} for k in chaves}
        t["pesos_no_fim_ruim_menos_outras"] = {k: ic([x["ruim"][k] - (x["boa"][k] + x["neutra"][k]) / 2 for x in p]) for k in chaves}
        t["unidades"] = len(ls)
        out[f"{cer}/{braco}/{mundo}"] = t
    return out


def rodar(saida: Path, log=print) -> dict:
    t0 = time.perf_counter()
    vu = tabelas(regenerar_vu(log))
    _gravar(saida / "validacao_unica.json", _dump({"rotulo": ROTULO, "fonte": CONFIG_VU, "conferido_contra": MEDIDAS_VU, "tabelas": vu}))
    cmp_ = tabelas(regenerar_ac(log))
    _gravar(saida / "comparacao.json", _dump({"rotulo": ROTULO, "fonte": CONFIG_AC, "conferido_contra": MEDIDAS_AC, "tabelas": cmp_}))
    seg = time.perf_counter() - t0
    _gravar(saida / "meta.json", _dump({
        "rotulo": ROTULO, "segundos": seg, "bootstrap": BOOT, "bracos": BRACOS, "janelas": {"inicio": "dias 1-7", "final": "dias 8-14"},
        "script_sha256": bv._sha(Path(__file__)), "bancada_sha256": bv._sha(RAIZ / "experiments" / "bancada_v2.py"),
        "lobos_sha256": bv._sha(RAIZ / "digilab" / "policies" / "lobos.py"),
        "cerebro_c_sha256": bv._sha(RAIZ / "digilab" / "policies" / "cerebro_c.py"),
        "frutas_sha256": bv._sha(RAIZ / "digilab" / "frutas.py"), "python": platform.python_version(), "plataforma": platform.platform()}))
    return {"validacao_unica": vu, "comparacao": cmp_, "segundos": seg}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="descritivo pos hoc do plato de ~1/3 (V-3, Q-1)")
    ap.add_argument("--saida", default=SAIDA)
    a = ap.parse_args(argv)
    r = rodar(RAIZ / a.saida, log=lambda s: print(s, flush=True))
    print(f"{r['segundos']:.0f} s; {len(r['validacao_unica'])} + {len(r['comparacao'])} celulas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
