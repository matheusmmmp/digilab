"""A etapa L0 da proposta do longe (docs/PROPOSTA_LONGE_DIGIBRAIN_MODULAR.md, secoes 2 e 8): um diagnostico so de leitura. Rejoga, dos
logs que a run da reavaliacao gravou (o commit 988cf0d, o #432), as 1 200 vidas M0 e M3* da 66xxx nas 12 celulas, confere o G1 (as
medidas refeitas no replay iguais as do medidas.json, menos o custo; os sha do codigo iguais aos do meta.json) e mede as M-L1 a M-L6 pela
forma registrada na secao 8, antes do replay. Aplica a regra de escolha da secao 2 como esta (limiares PROPOSTOS, SEM FONTE).

Nenhuma vida nova, nenhuma semente, nenhum gate. O motor, o engine.py, o corpo, os cerebros e as medidas por vida nao mudam: o embrulho da
captura so le a Observacao que o cerebro recebe e as fontes do cheiro do proprio mundo (funcoes puras), e repassa tudo o mais. Os logs
so sao lidos. Uma vida que nao se refaz para tudo, sem gravar nada.

    python experiments/longe_l0_digibrain.py --vidas <a pasta vidas/ da reavaliacao> --processos 4
grava artifacts_v2_digibrain_prototipo/longe_l0/l0.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402
from digilab.metrics import n_min_decisoes  # noqa: E402
from digilab.mundo import DIR16, distancia  # noqa: E402

PASTA = RAIZ / "artifacts_v2_digibrain_prototipo"
MEDIDAS = PASTA / "reavaliacao" / "medidas.json"
META = PASTA / "reavaliacao" / "meta.json"
SAIDA = PASTA / "longe_l0" / "l0.json"
SHA_MEDIDAS = "73ae8a8a1659f880bc4516ed06fcbdd441a5a9b187c833dace06fad5476ddf01"     # o #432 (A4.10 e RESULTADO, secao 8)
BRACOS = ("M0", "M3")                 # o M3 do registro e o M3* da leitura
BRACO_DA_REGRA = "M3"
DIAS, ORCAMENTO = 14, 16
ROTULO = "diagnostico so de leitura (a etapa L0, PROPOSTA_LONGE, secao 8): replay dos logs da 66xxx, sem vida nova e sem gate"
# a regra de escolha da secao 2 da proposta, como esta: os limiares sao PROPOSTOS, SEM FONTE
ANGULO_LIMITE = 45.0
FRAC_PERCEPCAO = 0.25
FRAC_DECISAO = 0.5
BUSCA, COMER_COMIDA = ["comer", "cheiro"], ["comer", "comida"]
FAIXAS_D0 = ((6, 12), (12, 18), (18, 24))  # a faixa do cheiro em celulas, (a, b]: o M-L4


class Captura:
    """Embrulho que so le, por fora do Registro da run: em cada decisao, a posicao, a direcao do cheiro (1 a 8, ou 0) e as fontes do cheiro
    do mundo naquele tick (`_fontes_de_cheiro`, pura). Repassa todo o resto; nao toca em rng."""

    def __init__(self, interna, caixa: dict) -> None:
        self._interna = interna
        self._caixa = caixa
        self.decisoes: list[tuple] = []

    def agir(self, obs, rng):
        motor = self._caixa["motor"]
        tick = motor._estado.tick
        pm = obs.mundo
        self.decisoes.append((tick, pm.x, pm.y, pm.direcao_cheiro, tuple(motor._fontes_de_cheiro(tick))))
        return self._interna.agir(obs, rng)

    def __getattr__(self, nome: str):
        interna = self.__dict__.get("_interna")
        if interna is None:
            raise AttributeError(nome)
        return getattr(interna, nome)


def _sha(caminho: Path) -> str:
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


def _sem_custo(v: dict) -> dict:
    return {k: x for k, x in v.items() if k != "custo"}


def _angulo(dx: int, dy: int, vx: int, vy: int) -> float:
    """o angulo, em graus, entre (dx, dy) e (vx, vy); 0 com o pet em cima da fonte"""
    na, nb = math.hypot(dx, dy), math.hypot(vx, vy)
    if na == 0 or nb == 0:
        return 0.0
    c = max(-1.0, min(1.0, (dx * vx + dy * vy) / (na * nb)))
    return math.degrees(math.acos(c))


def rejogar(tarefa: tuple) -> dict:
    """uma vida: o replay do log, o G1 e as contagens das M-L1 a M-L6 (so a vida; a soma fica no principal)"""
    braco, dono, lugar, semente, arquivo, gravada = tarefa
    texto = Path(arquivo).read_text(encoding="utf-8")
    fp, fm = orq.fabricas(braco, dono, semente, DIAS, ORCAMENTO, conserto=True)
    caixa: dict = {}

    def fp2(cfg=None):
        return Captura(fp(cfg), caixa)

    def fm2(politica, cfg, s):
        motor = fm(politica, cfg, s)
        caixa["motor"] = motor
        return motor

    motor = orq.reproduzir_mundo(orq.LogDeEventos.de_jsonl(texto), fp2, semente=semente, fabrica_motor=fm2)
    if motor.log.para_jsonl() != texto:
        raise orq.bv.ReplayDivergiu(f"{arquivo}: o log rejogado nao e o do disco")
    cap = motor.politica
    registro = cap._interna
    orq.conferir_cenario(motor, registro)
    orq.conferir_mecanismo(braco, registro, None)
    refeita = {"vida": gravada["vida"], "braco": braco, "dono": dono, "lugar": lugar, "semente": semente, "base": gravada["base"],
               "k": gravada["k"], **orq.medidas(motor, registro, braco, DIAS, True)}
    if json.dumps(refeita, sort_keys=True) != json.dumps(_sem_custo(gravada), sort_keys=True):
        raise RuntimeError(f"G1 da L0: a vida {gravada['vida']} nao refaz as medidas gravadas")

    g = orq.geometria()
    R, passo_sub, cm = orq.CM.raio_cheiro_celulas * orq.CM.sub, g["passo"], orq.CM
    passo = orq.CONFIG_PADRAO.intervalo_decisao_ticks
    entrada = motor.entrada_mundo
    ms = orq.cerebro_de(registro).motivos
    decs = cap.decisoes
    n = len(decs)
    if n != len(ms) or any(t - entrada != k * passo for k, (t, *_r) in enumerate(decs)):
        raise RuntimeError(f"{gravada['vida']}: as decisoes capturadas nao sao as do cerebro, no tick k x {passo}")
    pos = [(x, y) for _t, x, y, _d, _f in decs]
    perto = []                                # as fontes a menos de R, por decisao
    for _t, x, y, _d, fontes in decs:
        if any(a != cm.cheiro_racao for _x, _y, a in fontes):
            raise RuntimeError(f"{gravada['vida']}: uma fonte do cheiro que nao e racao (o T-CENARIO-1)")
        perto.append([(fx, fy) for fx, fy, _a in fontes if distancia(fx - x, fy - y) < R])

    # M-L1, a percepcao
    ml1 = {"decisoes": 0, "a_mais_de_45_de_todas": 0, "direcao_0": 0, "angulo_mais_proxima": [], "racoes_em_R": []}
    for k, (_t, x, y, direcao, _f) in enumerate(decs):
        if not perto[k] or ms[k]["contexto"]["comida_vista"]:
            continue
        if direcao == 0:
            ml1["direcao_0"] += 1
            continue
        vx, vy = DIR16[2 * (direcao - 1)]
        angulos = [(distancia(fx - x, fy - y), _angulo(fx - x, fy - y, vx, vy)) for fx, fy in perto[k]]
        ml1["decisoes"] += 1
        ml1["a_mais_de_45_de_todas"] += all(a > ANGULO_LIMITE for _d, a in angulos)
        ml1["angulo_mais_proxima"].append(min(angulos)[1])
        ml1["racoes_em_R"].append(len(perto[k]))

    # M-L2, a decisao
    ml2 = {t: {"trocadas": 0, "quebra": 0, "reflexo_sono": 0, "outra_com_racao_em_R": 0, "outra_sem_racao_em_R": 0, "para_comer": 0,
               "por_vencedora": {}} for t in ("busca", "comer")}
    for k, m in enumerate(ms):
        for f in m["fins"]:
            if f["motivo"] != "trocou" or f["chave"][:2] not in (BUSCA, COMER_COMIDA):
                continue
            c = ml2["busca" if f["chave"][:2] == BUSCA else "comer"]
            c["trocadas"] += 1
            v = "/".join(str(x) for x in m["escolha"][:2])
            c["por_vencedora"][v] = c["por_vencedora"].get(v, 0) + 1
            if m["reflexo"]:
                c["reflexo_sono"] += 1
                c["quebra"] += 1
            elif m["acao"] == "comer":
                c["para_comer"] += 1
            elif perto[k]:
                c["outra_com_racao_em_R"] += 1
                c["quebra"] += 1
            else:
                c["outra_sem_racao_em_R"] += 1

    # a oferta de cada decisao (as racoes do dono maduras e nao comidas no chao), como a do episodio de fome no orquestrador
    k_comida = {c["id"]: (c["tick"] - entrada) // passo for c in motor.consumos_mundo}
    racoes = {d["id"]: d for d in motor.deixadas if d["tipo"] == "racao"}

    def oferta(k: int) -> dict:
        x, y = pos[k]
        return {i: distancia(d["x"] - x, d["y"] - y) for i, d in racoes.items()
                if orq._no_chao(d["tick"] - entrada, k_comida.get(i), k, passo, cm.maduro_racao_min)}

    comeu_em = {(c["tick"] - entrada) // passo: c["id"] for c in motor.consumos_mundo if c["id"] in racoes}
    es = registro.estados

    # M-L3, o andado; M-L5, a racao que fecha
    ml3, ml5 = [], {"fechados": 0, "a_mais_proxima_na_abertura": 0, "na_oferta_da_abertura": 0, "elegivel": 0, "idade_decisoes": []}
    for k_i, d0, _w, fim, motivo in refeita["episodios_fome"]["episodios"]:
        of = oferta(k_i)
        if not of or min(of.values()) != d0:
            raise RuntimeError(f"{gravada['vida']}: a oferta da abertura {k_i} nao da o d0 gravado")
        mais_proxima = min(of, key=lambda i: (of[i], i))
        if motivo == "fechou":
            alvo = comeu_em.get(fim)
            if alvo is None:
                raise RuntimeError(f"{gravada['vida']}: o episodio fechado em {fim} sem a racao comida")
            ml5["fechados"] += 1
            ml5["a_mais_proxima_na_abertura"] += alvo == mais_proxima
            ml5["na_oferta_da_abertura"] += alvo in of
            t0 = racoes[alvo]["tick"] - entrada
            k0 = -(-t0 // passo)
            ml5["elegivel"] += k0 < n and es[k0][0] < orq.G_MVP["fome_elegivel"]     # como a cadeia_w do orquestrador
            ml5["idade_decisoes"].append(fim - k0)
        else:
            alvo = mais_proxima
        rx, ry = racoes[alvo]["x"], racoes[alvo]["y"]
        ks = range(k_i, fim + 1)
        liquido = distancia(rx - pos[k_i][0], ry - pos[k_i][1]) - distancia(rx - pos[fim][0], ry - pos[fim][1])
        ml3.append({"motivo": motivo, "d0": d0, "decisoes": len(ks),
                    "acordado": sum(1 for k in ks if ms[k]["acao"] != "dormir"),
                    "andou": sum(1 for k in ks if k + 1 < n and pos[k + 1] != pos[k]),
                    "liquido_decisoes": liquido / passo_sub, "n_min": n_min_decisoes(d0, g["raio_pegar"], passo_sub)})

    # M-L6, as fontes
    ml6 = [len(p) for p in perto]
    return {"vida": gravada["vida"], "braco": braco, "dono": dono, "lugar": lugar, "log_sha256": hashlib.sha256(texto.encode("utf-8")).hexdigest(),
            "ml1": ml1, "ml2": ml2, "ml3": ml3, "ml5": ml5, "ml6": ml6}


# ------------------------------------------------------------------ a soma
def _quantis(xs: list) -> dict | None:
    if not xs:
        return None
    xs = sorted(xs)
    q = statistics.quantiles(xs, n=4) if len(xs) > 1 else [xs[0]] * 3
    return {"n": len(xs), "media": statistics.fmean(xs), "q1": q[0], "mediana": q[1], "q3": q[2], "min": xs[0], "max": xs[-1]}


def _hist(xs: list, bordas: list) -> dict:
    out = {}
    for a, b in zip(bordas, bordas[1:]):
        out[f"{a}-{b}"] = sum(1 for x in xs if a <= x < b)
    out[f"{bordas[-1]}+"] = sum(1 for x in xs if x >= bordas[-1])
    return out


def _razao(a, b):
    return a / b if b else None


def somar(vs: list[dict], d0_gravados: list[tuple]) -> dict:
    """as M-L1 a M-L6 de um conjunto de vidas; `d0_gravados` = (d0, motivo) dos episodios (o M-L4)"""
    sub = orq.CM.sub
    ang = [a for v in vs for a in v["ml1"]["angulo_mais_proxima"]]
    rr = [x for v in vs for x in v["ml1"]["racoes_em_R"]]
    n1 = sum(v["ml1"]["decisoes"] for v in vs)
    gt = sum(v["ml1"]["a_mais_de_45_de_todas"] for v in vs)
    z = sum(v["ml1"]["direcao_0"] for v in vs)
    ml1 = {"decisoes": n1, "a_mais_de_45_de_todas": gt, "frac_a_mais_de_45_de_todas": _razao(gt, n1),
           "direcao_0": {"decisoes": z, "frac_das_decisoes_com_racao_em_R_sem_comida_vista": _razao(z, n1 + z)},
           "angulo_a_mais_proxima": {"quantis": _quantis(ang), "hist_graus": _hist(ang, [0, 15, 30, 45, 60, 90, 135])},
           "racoes_em_R": {"quantis": _quantis(rr), "hist": _hist(rr, [1, 2, 3, 4, 6, 10])}}
    ml2 = {}
    for t in ("busca", "comer"):
        c = {k: sum(v["ml2"][t][k] for v in vs) for k in ("trocadas", "quebra", "reflexo_sono", "outra_com_racao_em_R",
                                                           "outra_sem_racao_em_R", "para_comer")}
        venc: dict = {}
        for v in vs:
            for u, x in v["ml2"][t]["por_vencedora"].items():
                venc[u] = venc.get(u, 0) + x
        c["frac_quebra"] = _razao(c["quebra"], c["trocadas"])
        c["por_vencedora"] = dict(sorted(venc.items(), key=lambda kv: (-kv[1], kv[0])))
        c["por_vida"] = c["trocadas"] / len(vs)
        ml2[t] = c
    eps = [e for v in vs for e in v["ml3"]]
    ml3 = {}
    for nome, sel in (("todos", eps), ("fechados", [e for e in eps if e["motivo"] == "fechou"]),
                      ("nao_fechados", [e for e in eps if e["motivo"] != "fechou"])):
        ml3[nome] = {"episodios": len(sel),
                     "frac_acordado": _razao(sum(e["acordado"] for e in sel), sum(e["decisoes"] for e in sel)),
                     "frac_andou": _razao(sum(e["andou"] for e in sel), sum(e["decisoes"] for e in sel)),
                     "decisoes_na_janela": _quantis([e["decisoes"] for e in sel]),
                     "liquido_decisoes": _quantis([e["liquido_decisoes"] for e in sel]),
                     "n_min": _quantis([e["n_min"] for e in sel]),
                     "frac_liquido_ao_menos_n_min": _razao(sum(1 for e in sel if e["liquido_decisoes"] >= e["n_min"]), len(sel))}
    no_cheiro = [(d / sub, m) for d, m in d0_gravados if orq.geometria()["raio_visao"] < d <= orq.geometria()["corte_d0"]]
    ml4 = {"episodios_na_faixa_do_cheiro": len(no_cheiro), "d0_celulas": _quantis([d for d, _m in no_cheiro]),
           "por_faixa": {f"{a}-{b}": {"episodios": sum(1 for d, _m in no_cheiro if a < d <= b),
                                     "taxa": _razao(sum(1 for d, m in no_cheiro if a < d <= b and m == "fechou"),
                                                    sum(1 for d, _m in no_cheiro if a < d <= b))} for a, b in FAIXAS_D0}}
    f5 = {k: sum(v["ml5"][k] for v in vs) for k in ("fechados", "a_mais_proxima_na_abertura", "na_oferta_da_abertura", "elegivel")}
    ml5 = {**f5, "frac_a_mais_proxima": _razao(f5["a_mais_proxima_na_abertura"], f5["fechados"]),
           "frac_na_oferta_da_abertura": _razao(f5["na_oferta_da_abertura"], f5["fechados"]),
           "frac_elegivel": _razao(f5["elegivel"], f5["fechados"]),
           "idade_decisoes": _quantis([x for v in vs for x in v["ml5"]["idade_decisoes"]])}
    m6 = [x for v in vs for x in v["ml6"]]
    ml6 = {"decisoes": len(m6), "quantis": _quantis(m6), "hist": _hist(m6, [0, 1, 2, 3, 4, 6, 10])}
    return {"vidas": len(vs), "M-L1": ml1, "M-L2": ml2, "M-L3": ml3, "M-L4": ml4, "M-L5": ml5, "M-L6": ml6}


def regra(longe: dict) -> dict:
    """a regra de escolha da secao 2, como esta, sobre o longe do braco da regra"""
    p = longe["M-L1"]["frac_a_mais_de_45_de_todas"]
    d = longe["M-L2"]["busca"]["frac_quebra"]
    if p is None or d is None:
        raise RuntimeError("a regra sem as decisoes do M-L1 ou sem as buscas trocadas do M-L2 no longe")
    percepcao, decisao = p >= FRAC_PERCEPCAO, d >= FRAC_DECISAO
    aponta = {(True, False): "L-1 (a percepcao)", (False, True): "L-2 (a decisao)", (True, True): "L-1 e L-2 (as duas)",
              (False, False): "nenhuma: a proposta volta ao Gerente com o M-L3 e o M-L4"}[(percepcao, decisao)]
    return {"limiares": {"angulo_graus": ANGULO_LIMITE, "frac_percepcao": FRAC_PERCEPCAO, "frac_decisao": FRAC_DECISAO,
                         "status": "PROPOSTOS, SEM FONTE (a secao 2 da proposta)"},
            "percepcao": {"frac_a_mais_de_45_de_todas": p, "pesa": percepcao,
                          "direcao_0": longe["M-L1"]["direcao_0"]},
            "decisao": {"frac_buscas_trocadas_quebradas": d, "pesa": decisao, "buscas_trocadas": longe["M-L2"]["busca"]["trocadas"]},
            "aponta": aponta}


def conferir_codigo(meta: dict) -> dict:
    """os sha do codigo de hoje sao os da run (o meta.json da reavaliacao); falha alto se nao"""
    diffs = []
    for rel, sha in meta["sha256"].items():
        if _sha(RAIZ / "digilab" / rel) != sha:
            diffs.append(rel)
    if _sha(RAIZ / "experiments" / "run_v2_digibrain_prototipo.py") != meta["orquestrador_sha256"]:
        diffs.append("experiments/run_v2_digibrain_prototipo.py")
    if diffs:
        raise RuntimeError(f"o codigo nao e o da run da reavaliacao: {diffs}")
    return {"arquivos": len(meta["sha256"]) + 1, "iguais_ao_meta": True}


def principal(vidas: Path, processos: int) -> dict:
    if SAIDA.exists():
        raise FileExistsError(f"{SAIDA} ja existe: a L0 roda uma vez")
    if _sha(MEDIDAS) != SHA_MEDIDAS:
        raise RuntimeError("o medidas.json nao e o do #432")
    meta = json.loads(META.read_text(encoding="utf-8"))
    if meta["git_head"] != "988cf0d4345806ba5b486d2c5b0588cd4723a113" or meta["fase"] != "reavaliacao":
        raise RuntimeError("o meta.json nao e o da reavaliacao do commit 988cf0d")
    codigo = conferir_codigo(meta)
    medidas = json.loads(MEDIDAS.read_text(encoding="utf-8"))
    tarefas = []
    for chave, v in sorted(medidas.items()):
        if v["braco"] not in BRACOS:
            continue
        arquivo = vidas / v["braco"] / f"{v['dono']}_{v['lugar']}_{v['semente']}.jsonl"
        if not arquivo.is_file():
            raise FileNotFoundError(f"o log da vida {chave} nao esta em {arquivo}")
        tarefas.append((v["braco"], v["dono"], v["lugar"], v["semente"], str(arquivo), v))
    if len(tarefas) != 1200:
        raise RuntimeError(f"{len(tarefas)} vidas M0 e M3, e nao 1 200")
    c0, p0 = time.process_time(), time.perf_counter()
    if processos <= 1:
        saidas = [rejogar(t) for t in tarefas]
    else:
        with ProcessPoolExecutor(max_workers=processos) as pool:
            saidas = list(pool.map(rejogar, tarefas))
    parede = time.perf_counter() - p0
    gravadas = {v["vida"]: v for *_x, v in tarefas}
    out: dict = {}
    for b in BRACOS:
        vs = [s for s in saidas if s["braco"] == b]

        def d0s(sel):
            return [(e[1], e[4]) for s in sel for e in gravadas[s["vida"]]["episodios_fome"]["episodios"]]

        out[b] = {"todas": somar(vs, d0s(vs)),
                  "por_lugar": {lu: somar([s for s in vs if s["lugar"] == lu], d0s([s for s in vs if s["lugar"] == lu]))
                                for lu in orq.LUGARES},
                  "por_celula": {f"{d}|{lu}": somar(sel, d0s(sel)) for d, lu in orq.CELULAS
                                 for sel in [[s for s in vs if s["dono"] == d and s["lugar"] == lu]]}}
    logs = {s["vida"]: s["log_sha256"] for s in saidas}
    return {
        "rotulo": ROTULO,
        "registro": "docs/PROPOSTA_LONGE_DIGIBRAIN_MODULAR.md, secao 8 (o commit 442ff86, antes do replay)",
        "fontes": {orq.rc._relativo(MEDIDAS): _sha(MEDIDAS), orq.rc._relativo(META): _sha(META)},
        "script": {"arquivo": orq.rc._relativo(Path(__file__)), "sha256": _sha(Path(__file__))},
        "git_head": orq.rc._git("rev-parse", "HEAD"), "git_limpo": orq.rc._git("status", "--porcelain") == "",
        "commit_da_run": meta["git_head"], "codigo": codigo, "processos": processos,
        "vidas": len(saidas), "g1": {"vidas_refeitas": len(saidas), "todas_iguais": True},
        "logs_sha256": logs, "logs_sha256_do_conjunto": hashlib.sha256("".join(logs[k] for k in sorted(logs)).encode()).hexdigest(),
        "tempo": {"parede_s": parede, "cpu_principal_s": time.process_time() - c0},
        "medidas": out,
        "regra": {"braco": BRACO_DA_REGRA, "lugar": "longe", **regra(out[BRACO_DA_REGRA]["por_lugar"]["longe"]),
                  "M0_ao_lado": regra(out["M0"]["por_lugar"]["longe"])},
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--vidas", type=Path, required=True)
    ap.add_argument("--processos", type=int, default=1)
    a = ap.parse_args()
    if a.processos > 4:
        raise SystemExit("ate 4 processos (a maquina; a BIOS segue a FH)")
    d = principal(a.vidas.resolve(), a.processos)
    bv._gravar(SAIDA, bv._dump(d))
    print(f"gravado {orq.rc._relativo(SAIDA)} (sha256 {_sha(SAIDA)}); a regra aponta: {d['regra']['aponta']}")
