"""O diagnostico do DigiBrain modular, a parte com o replay (docs/PROPOSTA_DIAGNOSTICO_DIGIBRAIN_MODULAR.md, secao 3.2; a decisao do
Matheus de 2026-10-26: "Aprovo a proposta, com replay no piloto"). Rejoga do disco as 576 vidas do piloto (os logs em <pasta>/vidas/,
a pasta passada como argumento: as vidas regeradas do c3a4d82, que ficam fora do git) e conta o que so sai rejogando:
  - o indice "ganhou, fica" por acao e por contexto (H-P2a, H-P2c): o da medida (o drive, a comida a vista, a noite), o do z (as
    caracteristicas em que o H aprende, cada uma em -1, 0 ou +1 pelo corte S/2) e nenhum; e o mesmo sem as acoes de consumo (comer e
    dormir); mais quem o habito decidiu (a sonda), por acao;
  - as opcoes entregues ao P2 (H-P2b): o r_n e o numero de decisoes de cada uma, por comportamento e alvo, e nas de mais de uma decisao a
    distancia entre o z do comeco (a elegibilidade) e o z da ultima decisao; em que escolha (comportamento e alvo) o pet comeu; e o H no
    fim da vida;
  - nas racoes elegiveis (a definicao do G-MVP), a fracao de dormir dentro da janela de 8 decisoes, fechadas e nao fechadas;
  - nas racoes elegiveis, a distancia do pet a racao (em celulas) e o cheiro na decisao da posta, a menor distancia na janela, se ela
    entrou na visao e quantas decisoes foram ao cheiro.
A instrumentacao so embrulha, na instancia do cerebro do replay, tres metodos (o M-SENS codificar, o M-IMPULSO unidades e o M-PLAST
creditar) para guardar o que entra e sai; devolve o mesmo objeto, nao toca em rng e nada em digilab/ muda.

**A conferencia G1:** cada vida rejogada tem de refazer o log do disco e as medidas gravadas no medidas.json da pasta, fora dos campos de
relogio (o `custo`); senao falha alto e o diagnostico para. Grava artifacts_v2_digibrain_prototipo/diagnostico/replay_piloto.json.

    python experiments/diagnostico_replay_digibrain.py D:/Trab/digilab/v2-regera-piloto/artifacts_v2_digibrain_prototipo/piloto --processos 8
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402
from digilab.config import CARACTERISTICAS_DIGIBRAIN, COMPORTAMENTOS_DIGIBRAIN  # noqa: E402
from digilab.metrics import JANELA_8_14  # noqa: E402
from digilab.mundo import distancia  # noqa: E402

SAIDA = RAIZ / "artifacts_v2_digibrain_prototipo" / "diagnostico" / "replay_piloto.json"
COMMIT_PILOTO = "c3a4d82ffa9316e6728741892979e332d493cf0e"
CAMPOS_RELOGIO = ("custo",)                       # a decisao do Matheus ("Opcao 1"): a igualdade fora dos campos de relogio
CAMPOS_DA_VIDA = ("vida", "braco", "dono", "lugar", "semente", "base", "k")
CONSUMO = ("comer", "dormir")                     # as acoes de consumo, fora do indice "sem consumo" (a DX-5 da proposta)
CONTEXTOS = ("medida", "z", "nenhum")
PRIMEIRA = tuple(b for b in orq.BRACOS_MODULAR if b not in orq.SEGUNDA_PASSADA)
FAIXAS_D = ((0, 6, "ate_6_visao"), (6, 12, "6_a_12"), (12, 24, "12_a_24"), (24, 10**9, "alem_de_24_sem_cheiro"))


# ================================================================== o replay instrumentado
def _embrulhar(c) -> dict:
    """guarda, decisao a decisao, o que o M-SENS leu do mundo, o z do M-IMPULSO e as opcoes entregues ao P2 (so leitura)"""
    reg = {"mundo": [], "z": [], "opcoes": []}
    codificar, unidades, creditar = c.m.sens.codificar, c.m.impulso.unidades, c.m.plast.creditar

    def codificar_(obs):
        out = codificar(obs)
        pm = obs.mundo
        reg["mundo"].append((pm.x, pm.y, pm.cheiro, pm.direcao_cheiro, tuple(v[0] for v in pm.vistos)))
        return out

    def unidades_(*a, **kw):
        out = unidades(*a, **kw)
        reg["z"].append(list(out[1]))
        return out

    def creditar_(op):
        reg["opcoes"].append({"chave": op["chave"], "inicio": op["inicio"], "n": op["n"], "r": op["r"], "e": list(op["e"]),
                              "motivo": op["motivo"]})
        return creditar(op)

    c.m.sens.codificar, c.m.impulso.unidades, c.m.plast.creditar = codificar_, unidades_, creditar_
    return reg


def rejogar(pasta: str, braco: str, dono: str, lugar: str, semente: int, cfg: dict, gravada: dict, serie_e=None, g_apr_con=None):
    """uma vida rejogada do disco, com a conferencia G1 (o log e as medidas gravadas fora do relogio): (o motor, o registro, o cerebro,
    o que a instrumentacao guardou)"""
    texto = (Path(pasta) / "vidas" / braco / f"{dono}_{lugar}_{semente}.jsonl").read_text(encoding="utf-8")
    fp, fm = orq.fabricas(braco, dono, semente, cfg["dias"], cfg["orcamento_por_dia"], serie_e, g_apr_con)
    reg = fp(None)
    c = orq.cerebro_de(reg)
    inst = _embrulhar(c)
    motor = orq.reproduzir_mundo(orq.LogDeEventos.de_jsonl(texto), lambda _c=None: reg, semente=semente, fabrica_motor=fm)
    nome = f"{braco}|{dono}|{lugar}|{semente}"
    if motor.log.para_jsonl() != texto:
        raise bv.ReplayDivergiu(f"{nome}: o replay nao refaz o log do disco")
    orq.conferir_mecanismo(braco, reg, serie_e)
    refeitas = json.loads(json.dumps(orq.medidas(motor, reg, braco, cfg["dias"])))
    esperadas = {k: v for k, v in gravada.items() if k not in CAMPOS_RELOGIO + CAMPOS_DA_VIDA}
    if refeitas != esperadas:
        difs = sorted(k for k in set(refeitas) | set(esperadas) if refeitas.get(k) != esperadas.get(k))
        raise bv.ReplayDivergiu(f"{nome}: o replay nao refaz as medidas gravadas fora do relogio: {difs}")
    if not (len(inst["mundo"]) == len(inst["z"]) == len(c.motivos) == len(reg.estados)):
        raise RuntimeError(f"{nome}: a instrumentacao nao viu toda decisao")
    return motor, reg, c, inst


# ================================================================== as contagens de uma vida
def _bin(v: int, S: int) -> int:
    return 1 if v > S // 2 else (-1 if v < -(S // 2) else 0)


def _contexto(tipo: str, m: dict, z: list, S: int):
    if tipo == "medida":
        return orq._contexto_ganhou_fica(m)
    if tipo == "z":
        return tuple(_bin(v, S) for v in z[1:])                # sem o vies (constante)
    return 0


def ganhou_fica(ms: list, zs: list, ticks: list, S: int, tipo: str) -> dict:
    """os pares do `repeticao_apos_alivio` (digilab/metrics.py) com o contexto `tipo`, contados pela acao da primeira decisao do par:
    {acao: {"pos": [pares, repetiu], "nao": [pares, repetiu]}}"""
    ini, fim = JANELA_8_14
    ultimo: dict = {}
    out: dict = {}
    for t, m, z in zip(ticks, ms, zs):
        ctx = _contexto(tipo, m, z, S)
        r = None if m["consequencia"] is None else m["consequencia"]["r"]
        ant = ultimo.get(ctx)
        if ant is not None and ini <= ant[0] < fim and ant[2] is not None:
            lado = out.setdefault(ant[1], {"pos": [0, 0], "nao": [0, 0]})["pos" if ant[2] > 0 else "nao"]
            lado[0] += 1
            lado[1] += m["acao"] == ant[1]
        ultimo[ctx] = (t, m["acao"], r)
    return out


def _indice(cont: dict, acoes=None) -> dict:
    pos = [sum(v["pos"][i] for a, v in cont.items() if acoes is None or a in acoes) for i in (0, 1)]
    nao = [sum(v["nao"][i] for a, v in cont.items() if acoes is None or a in acoes) for i in (0, 1)]
    p_pos = pos[1] / pos[0] if pos[0] else None
    p_nao = nao[1] / nao[0] if nao[0] else None
    return {"n_pos": pos[0], "n_nao_pos": nao[0], "p_pos": p_pos, "p_nao_pos": p_nao,
            "indice": None if p_pos is None or p_nao is None else p_pos - p_nao}


def racoes_elegiveis(motor, reg, ms: list, inst: dict, cadeia: dict, passo: int, sub: int) -> list[dict]:
    """as racoes elegiveis da cadeia (a mesma definicao de `cadeia_comida_corpo`), cada uma com a janela de 8 decisoes: o dormir, o
    reflexo, a distancia do pet a racao, o cheiro, a visao e as escolhas do cheiro. Confere as contagens com a cadeia gravada."""
    w = orq.G_MVP["w_decisoes"]
    entrada = motor.entrada_mundo
    es = reg.estados
    consumos = {}
    for c in motor.consumos_mundo:
        t = c["tick"] - entrada
        consumos[c["id"]] = (t, reg.falta_depois[t // passo] < es[t // passo][5])
    out = []
    for d in motor.deixadas:
        if d["tipo"] != "racao":
            continue
        t0 = d["tick"] - entrada
        k0 = -(-t0 // passo)
        if k0 >= len(es) or es[k0][0] >= orq.G_MVP["fome_elegivel"]:
            continue
        c = consumos.get(d["id"])
        fechada = c is not None and c[0] <= t0 + w * passo and c[1]
        janela = range(k0, min(k0 + w, len(ms)))

        def dist(k):
            x, y = inst["mundo"][k][:2]
            return distancia(d["x"] - x, d["y"] - y)
        ds = [dist(k) / sub for k in janela]
        out.append({"fechada": fechada, "decisoes": len(janela),
                    "dormir": sum(1 for k in janela if ms[k]["acao"] == "dormir"),
                    "reflexo": sum(1 for k in janela if ms[k]["reflexo"]),
                    "dormindo_na_posta": ms[k0]["acao"] == "dormir",
                    "d0": ds[0], "d_min": min(ds), "cheiro_na_posta": inst["mundo"][k0][3] != 0, "intensidade_na_posta": inst["mundo"][k0][2],
                    "vista_na_janela": any(d["id"] in inst["mundo"][k][4] for k in janela),
                    "ao_cheiro": sum(1 for k in janela if ms[k]["tipo_escolha"] == "cheiro"),
                    "comer_ao_cheiro": sum(1 for k in janela if ms[k]["acao"] == "comer" and ms[k]["tipo_escolha"] == "cheiro")})
    if len(out) != cadeia["elegiveis"] or sum(r["fechada"] for r in out) != cadeia["fechadas"]:
        raise RuntimeError(f"as racoes elegiveis do diagnostico ({len(out)}, {sum(r['fechada'] for r in out)}) nao sao as da cadeia "
                           f"gravada ({cadeia['elegiveis']}, {cadeia['fechadas']})")
    return out


def contar_vida(motor, reg, c, inst: dict, gravada: dict) -> dict:
    """o que a vida da ao diagnostico (contagens que se somam entre vidas)"""
    S = c.S
    passo = orq.CONFIG_PADRAO.intervalo_decisao_ticks
    ms, zs = c.motivos, inst["z"]
    ticks = [k * passo for k in range(len(ms))]
    gf = {tipo: ganhou_fica(ms, zs, ticks, S, tipo) for tipo in CONTEXTOS}
    conf = _indice(gf["medida"])
    rep = gravada["repeticao"]
    if (conf["n_pos"], conf["n_nao_pos"], conf["indice"]) != (rep["n_pos"], rep["n_nao_pos"], rep["indice"]):
        raise RuntimeError("o ganhou_fica por acao, somado, nao refaz o indice gravado")
    sem = tuple(a for a in COMPORTAMENTOS_DIGIBRAIN if a not in CONSUMO)
    indices = {tipo: {"todas": _indice(gf[tipo])["indice"], "sem_consumo": _indice(gf[tipo], sem)["indice"]} for tipo in CONTEXTOS}
    ini, fim = JANELA_8_14
    habito_decidiu: dict = {}
    for t, m in zip(ticks, ms):
        if ini <= t < fim and m["sondas"]["habito_decidiu"]:
            habito_decidiu[m["acao"]] = habito_decidiu.get(m["acao"], 0) + 1
    opcoes: dict = {}
    for op in inst["opcoes"]:
        chave = f"{op['chave'][0]}|{op['chave'][1] if len(op['chave']) > 1 else '-'}"
        o = opcoes.setdefault(chave, {"n": 0, "soma_r": 0, "r_pos": 0, "r_neg": 0, "soma_decisoes": 0, "longas": 0, "soma_dz_longas": 0})
        o["n"] += 1
        o["soma_r"] += op["r"]
        o["r_pos"] += op["r"] > 0
        o["r_neg"] += op["r"] < 0
        o["soma_decisoes"] += op["n"]
        if op["n"] > 1:
            ultima = op["inicio"] + op["n"] - 1
            o["longas"] += 1
            o["soma_dz_longas"] += sum(abs(a - b) for a, b in zip(op["e"], zs[ultima])) / S
    comeu: dict = {}
    for m in ms:
        x = comeu.setdefault(f"{m['acao']}|{m['tipo_escolha']}", [0, 0])
        x[0] += 1
        x[1] += m["consequencia"] is not None and m["consequencia"]["comeu"] is not None
    racoes = racoes_elegiveis(motor, reg, ms, inst, gravada["cadeia"], passo, orq.CM.sub)
    return {"indices": indices, "pares": gf, "habito_decidiu": habito_decidiu, "opcoes": opcoes, "comeu_por_escolha": comeu,
            "H": {b: list(v) for b, v in c.m.plast.H.items()}, "racoes": racoes}


# ================================================================== as tarefas (uma unidade)
def tarefa_primeira(pasta: str, cfg: dict, semente: int, gravadas: dict) -> tuple[list, dict]:
    out, series = [], {}
    for b in PRIMEIRA:
        for dono, lugar in orq.CELULAS:
            g = gravadas[f"{b}|{dono}|{lugar}|{semente}"]
            motor, reg, c, inst = rejogar(pasta, b, dono, lugar, semente, cfg, g)
            out.append({"braco": b, "dono": dono, "lugar": lugar, "semente": semente, **contar_vida(motor, reg, c, inst, g)})
            if b == "M4":
                series[(dono, lugar)] = tuple(c.m.afeto.serie_e)
    return out, series


def tarefa_segunda(pasta: str, cfg: dict, semente: int, gravadas: dict, series: dict, g_apr_con: int) -> list:
    out = []
    for dono, lugar in orq.CELULAS:
        for b, kw in (("M4-emb", {"serie_e": series[(dono, lugar)]}), ("M4-con", {"g_apr_con": g_apr_con})):
            g = gravadas[f"{b}|{dono}|{lugar}|{semente}"]
            motor, reg, c, inst = rejogar(pasta, b, dono, lugar, semente, cfg, g, **kw)
            out.append({"braco": b, "dono": dono, "lugar": lugar, "semente": semente, **contar_vida(motor, reg, c, inst, g)})
    return out


# ================================================================== a agregacao (funcoes puras)
def _somar_pares(acc: dict, cont: dict) -> None:
    for a, v in cont.items():
        x = acc.setdefault(a, {"pos": [0, 0], "nao": [0, 0]})
        for lado in ("pos", "nao"):
            x[lado][0] += v[lado][0]
            x[lado][1] += v[lado][1]


def _media(xs) -> float | None:
    xs = [x for x in xs if x is not None]
    return statistics.fmean(xs) if xs else None


def _resumo_racoes(rs: list[dict]) -> dict:
    if not rs:
        return {"n": 0}
    dec = sum(r["decisoes"] for r in rs)
    return {"n": len(rs), "frac_dormir_na_janela": sum(r["dormir"] for r in rs) / dec, "frac_reflexo_na_janela": sum(r["reflexo"] for r in rs) / dec,
            "frac_dormindo_na_posta": sum(r["dormindo_na_posta"] for r in rs) / len(rs),
            "frac_janela_toda_dormindo": sum(r["dormir"] == r["decisoes"] for r in rs) / len(rs),
            "d0_media": _media(r["d0"] for r in rs), "d0_mediana": statistics.median(r["d0"] for r in rs),
            "d_min_media": _media(r["d_min"] for r in rs),
            "d0_por_faixa": {nome: sum(1 for r in rs if a <= r["d0"] < b) / len(rs) for a, b, nome in FAIXAS_D},
            "frac_cheiro_na_posta": sum(r["cheiro_na_posta"] for r in rs) / len(rs),
            "frac_vista_na_janela": sum(r["vista_na_janela"] for r in rs) / len(rs),
            "ao_cheiro_por_racao": _media(r["ao_cheiro"] for r in rs), "comer_ao_cheiro_por_racao": _media(r["comer_ao_cheiro"] for r in rs)}


def agregar(vidas: list[dict]) -> dict:
    grupos: dict = {}
    for v in vidas:
        for chave in (f"{v['braco']}|todas", f"{v['braco']}|{v['lugar']}"):
            grupos.setdefault(chave, []).append(v)
    out = {}
    for chave, vs in sorted(grupos.items()):
        pares = {tipo: {} for tipo in CONTEXTOS}
        hab, ops, comeu = {}, {}, {}
        for v in vs:
            for tipo in CONTEXTOS:
                _somar_pares(pares[tipo], v["pares"][tipo])
            for a, n in v["habito_decidiu"].items():
                hab[a] = hab.get(a, 0) + n
            for k, (n, c) in v["comeu_por_escolha"].items():
                x = comeu.setdefault(k, [0, 0])
                x[0] += n
                x[1] += c
            for k, o in v["opcoes"].items():
                acc = ops.setdefault(k, dict.fromkeys(o, 0))
                for x, n in o.items():
                    acc[x] += n
        racoes = [r for v in vs for r in v["racoes"]]
        out[chave] = {
            "vidas": len(vs),
            "indice_por_vida": {tipo: {lado: _media(v["indices"][tipo][lado] for v in vs) for lado in ("todas", "sem_consumo")}
                                for tipo in CONTEXTOS},
            "ganhou_fica_por_acao": {tipo: {a: {**_indice({a: p}), "pares": p["pos"][0] + p["nao"][0]} for a, p in sorted(pares[tipo].items())}
                                     for tipo in CONTEXTOS},
            "habito_decidiu_por_acao": dict(sorted(hab.items())),
            "opcoes_creditadas": {k: {"n_por_vida": o["n"] / len(vs), "r_n_medio": o["soma_r"] / o["n"], "frac_r_pos": o["r_pos"] / o["n"],
                                      "frac_r_neg": o["r_neg"] / o["n"], "decisoes_por_opcao": o["soma_decisoes"] / o["n"],
                                      "longas": o["longas"],
                                      "dz_medio_longas": o["soma_dz_longas"] / o["longas"] if o["longas"] else None}
                                  for k, o in sorted(ops.items())},
            "comeu_por_escolha": {k: {"decisoes_por_vida": n / len(vs), "frac_comeu": c / n} for k, (n, c) in sorted(comeu.items())},
            "H_fim_medio": {b: {f: statistics.fmean(v["H"][b][j] for v in vs) for j, f in enumerate(CARACTERISTICAS_DIGIBRAIN)
                                if any(v["H"][b][j] for v in vs)} for b in COMPORTAMENTOS_DIGIBRAIN},
            "racoes": {"fechadas": _resumo_racoes([r for r in racoes if r["fechada"]]),
                       "nao_fechadas": _resumo_racoes([r for r in racoes if not r["fechada"]])}}
    for lu in ("todas",) + orq.LUGARES:
        out.setdefault("M2-M1", {})[lu] = {tipo: {lado: out[f"M2|{lu}"]["indice_por_vida"][tipo][lado] - out[f"M1|{lu}"]["indice_por_vida"][tipo][lado]
                                                  for lado in ("todas", "sem_consumo")} for tipo in CONTEXTOS}
    return out


# ================================================================== a run do diagnostico
def diagnosticar(pasta: Path, processos: int) -> dict:
    meta = json.loads((pasta / "meta.json").read_text(encoding="utf-8"))
    cfg = meta["config"]
    if meta["fase"] != "piloto" or meta["git_head"] != COMMIT_PILOTO or not meta["git_limpo"]:
        raise ValueError(f"o replay e so das vidas do piloto regeradas no {COMMIT_PILOTO[:7]} com a arvore limpa")
    gravadas = json.loads((pasta / "medidas.json").read_text(encoding="utf-8"))
    unidades = meta["unidades"]
    fp, _ = orq.fabricas("M3", orq.DONOS[0], unidades[0]["semente"], cfg["dias"], cfg["orcamento_por_dia"])
    if orq.inatos_do_meta(meta) != orq.cerebro_de(fp(None)).inatos:
        raise ValueError("os valores de partida do piloto nao sao os do cerebro de hoje")
    t0 = time.perf_counter()
    saidas = orq.rc._executar([(tarefa_primeira, (str(pasta), cfg, u["semente"], gravadas)) for u in unidades], processos)
    vidas = [v for s in saidas for v in s[0]]
    series = {u["semente"]: s[1] for u, s in zip(unidades, saidas)}
    doa = orq.doadores(unidades)
    tarefas = [(tarefa_segunda, (str(pasta), cfg, u["semente"], gravadas, series[doa[u["semente"]]], meta["g_apr_m4_con"])) for u in unidades]
    vidas += [v for s in orq.rc._executar(tarefas, processos) for v in s]
    if len(vidas) != len(gravadas) or {f"{v['braco']}|{v['dono']}|{v['lugar']}|{v['semente']}" for v in vidas} != set(gravadas):
        raise RuntimeError("o replay nao cobriu as vidas do medidas.json")
    return {"proposta": "docs/PROPOSTA_DIAGNOSTICO_DIGIBRAIN_MODULAR.md, secao 3.2",
            "vidas_de": str(pasta).replace("\\", "/"), "commit_das_vidas": meta["git_head"],
            "medidas_sha256": orq.rc._sha_arquivo(pasta / "medidas.json"), "meta_sha256": orq.rc._sha_arquivo(pasta / "meta.json"),
            "g1": {"vidas_rejogadas": len(vidas), "conferidas_fora_do_relogio": len(vidas), "campos_de_relogio": list(CAMPOS_RELOGIO)},
            "janela": list(JANELA_8_14), "processos": processos, "parede_s": time.perf_counter() - t0,
            "grupos": agregar(vidas)}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("pasta", help="a pasta do piloto com meta.json, medidas.json e vidas/ (as vidas regeradas, fora do git)")
    ap.add_argument("--processos", type=int, default=1)
    a = ap.parse_args()
    d = diagnosticar(Path(a.pasta), a.processos)
    bv._gravar(SAIDA, bv._dump(d))
    print(json.dumps(d["g1"], ensure_ascii=False), round(d["parede_s"]))
