"""V2, REVISAO-APRENDIZ: teto, janela de credito ou exposicao? (docs/TAREFA_V2_REVISAO_APRENDIZ.md,
docs/PLANO_ANALISE_V2_REVISAO_APRENDIZ.md, registrado antes de qualquer run).

Diagnostico so com as sementes de calibracao 18101...18505: cada ponto muda UMA alavanca em relacao a base (secao 3 do plano) e roda
pela bancada (P0, P1, P3; casado_frutas e descasado; atencioso; unidades derivadas K por base). Por ponto: as medidas da secao 4; depois,
os contrastes pareados contra a base (secao 5), a leitura (secao 6), a recomendacao (secao 7) e, se duas alavancas ou mais sairem da
base, a conferencia da combinacao. Saida em artifacts_v2_revisao/calibracao/.

    python experiments/run_revisao_aprendiz.py --config experiments/configs/v2_revisao/calibracao.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import bancada_v2 as bv  # noqa: E402
from digilab.config import TICKS_POR_DIA  # noqa: E402
from digilab.events import LogDeEventos  # noqa: E402
from digilab.metrics import bootstrap_ic  # noqa: E402
from digilab.motivo import PoliticaComMotivo, indices_eventos_dono  # noqa: E402
from digilab.protocol import ENGINE_SHA256_V0, sha256_engine  # noqa: E402
from digilab.treino import reproduzir_com_feedback  # noqa: E402

PLANO = "docs/PLANO_ANALISE_V2_REVISAO_APRENDIZ.md"
BASES_REVISAO = (18101, 18202, 18303, 18404, 18505)
MUNDOS = ("casado_frutas", "descasado")
BRACOS = ("P0", "P1", "P3")
APRENDEM = ("P1", "P3")
ALAVANCAS = {"T": "teto", "J": "janela", "X": "exposicao"}
CHAVES = {"descricao", "conjunto", "bases", "k", "saida", "dias", "orcamento", "sonda", "bootstrap", "pontos"}
MEDIDAS = ("m1_decidiu", "m1_com_fator", "no_teto", "deriva_final", "fora_privacao", "saude", "humor", "taxa_final", "consumos",
           "p_comer", "acerto", "g_ap")


def _dump(obj) -> str:
    return json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _gravar(caminho: Path, texto: str) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(texto, encoding="utf-8", newline="\n")


def _sha(caminho: Path) -> str:
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


def carregar(caminho: Path) -> dict:
    cfg = json.loads(caminho.read_text(encoding="utf-8"))
    sobram, faltam = set(cfg) - CHAVES, CHAVES - set(cfg)
    if sobram or faltam:
        raise KeyError(f"config: sobram {sorted(sobram)}, faltam {sorted(faltam)}")
    if sha256_engine() != ENGINE_SHA256_V0:
        raise RuntimeError("engine.py mudou")
    if cfg["conjunto"] != "calibracao" or tuple(cfg["bases"]) != BASES_REVISAO:
        raise ValueError(f"so calibracao, nas bases {BASES_REVISAO} (o plano, secao 2)")
    if "base" not in cfg["pontos"] or cfg["pontos"]["base"]:
        raise ValueError("o ponto 'base' tem de existir e nao mudar nada")
    for nome, mudanca in cfg["pontos"].items():
        if nome != "base" and (nome[0] not in ALAVANCAS or len(mudanca) != 1 or set(mudanca) - {"lobos", "frutas"}):
            raise ValueError(f"ponto {nome!r}: uma alavanca so (T, J ou X), em 'lobos' ou 'frutas': {mudanca}")
    return cfg


def cfg_bancada(cfg: dict, nome: str, mudanca: dict) -> dict:
    return {"descricao": f"REVISAO-APRENDIZ, ponto {nome}", "plano": PLANO, "bracos": list(BRACOS), "donos": ["atencioso"],
            "unidades": {"bases": list(cfg["bases"]), "k": int(cfg["k"])}, "mundos": list(MUNDOS), "dias": cfg["dias"],
            "orcamento": cfg["orcamento"], "sonda": cfg["sonda"], "bootstrap": cfg["bootstrap"], **mudanca}


def motivos(bancada: bv.Bancada, vida: bv.VidaBancada) -> PoliticaComMotivo:
    """A vida rejogada com o motivo (PoliticaComMotivo) no motor do mundo dela; confere que a vida e a mesma."""
    log = LogDeEventos.de_jsonl(vida.motor.log.para_jsonl())
    indices = indices_eventos_dono(log)
    emb: list[PoliticaComMotivo] = []

    def fab(cfg=None):
        p = PoliticaComMotivo(bancada.politica(vida.espec, cfg), indices)
        emb.append(p)
        return p

    m = reproduzir_com_feedback(log, fab, semente=vida.espec.semente, fabrica_motor=bancada.fabrica_motor(vida.espec))
    # a vida (log, estado, acoes, rngs, consumos e incentivos) tem de ser a mesma; o registro das ofertas guarda a `regra` da politica,
    # que o PoliticaComMotivo nao repassa (sai None): esse campo fica fora da conferencia
    if _nucleo(m) != _nucleo(vida.motor):
        raise bv.ReplayDivergiu(f"{vida.nome}: o motivo mudou a vida")
    return emb[0]


def _nucleo(motor) -> tuple:
    r = motor.resumo_frutas()
    return (motor.log.para_jsonl(), motor.estado(), motor.acoes_recentes(10**9), motor._rng_politica.getstate(),
            motor._rng_ambiente.getstate(), r["consumos"], r["incentivo"], r["rng_fruta"], motor.resumo_mundo())


def medidas_da_vida(bancada: bv.Bancada, vida: bv.VidaBancada, m: dict) -> dict:
    """As medidas da secao 4 do plano numa vida fechada (sem G_ap, que pareia com o P0)."""
    fr = m["frutas"]
    c = fr["contagem"]
    out = {"semente": vida.espec.semente, "genoma": vida.espec.genoma, "mundo": vida.espec.mundo, "braco": vida.espec.braco,
           "fora_privacao": m["fracao_fora_de_privacao"], "saude": m["saude_media"], "humor": m["humor_medio"],
           "taxa_final": fr["taxa_fruta_ruim"]["final"]["taxa"], "consumos": fr["consumos"],
           "p_comer": ((c["decisoes_com_fruta"] - c["ignoradas"]) / c["decisoes_com_fruta"]) if c["decisoes_com_fruta"] else None,
           "acerto": m["acerto_total"], "deriva_final": m["deriva_final"],
           "deriva_por_dia": m["custo_da_plasticidade"]["deriva_por_dia"]}
    cerebro = bv.do_braco(vida.motor.politica).cerebro
    if vida.espec.braco in APRENDEM:
        emb = motivos(bancada, vida)
        n = len(emb.motivos)
        out["m1_decidiu"] = sum(d["lobo"] == "decisao" for d in emb.diagnosticos) / n
        out["m1_com_fator"] = sum(d["lobo"] == "decisao" and bool(mo.fatores) for mo, d in zip(emb.motivos, emb.diagnosticos)) / n
        out["no_teto"] = cerebro.pesos_no_teto()
        out["recompensas"] = dict(cerebro.estado_interno()["aprendizado"]["recompensas"])
    else:
        out["m1_decidiu"] = out["m1_com_fator"] = None
        out["no_teto"] = 0
    return out


def rodar_ponto(cfg: dict, nome: str, mudanca: dict, saida: Path) -> dict:
    t = time.perf_counter()
    cb = cfg_bancada(cfg, nome, mudanca)
    pasta = saida / nome
    r = bv.rodar(cb, pasta)
    bancada = bv.bancada_da_config(cb)
    vidas = {}
    for nome_vida, v in sorted(r["vidas"].items()):
        if v.origem is None:
            vidas[nome_vida] = medidas_da_vida(bancada, v, r["medidas"][nome_vida])
    # G_ap: taxa final do P0 - a do braco, na mesma unidade e mundo (secao 4)
    p0 = {(x["mundo"], x["semente"]): x["taxa_final"] for x in vidas.values() if x["braco"] == "P0"}
    for x in vidas.values():
        ref = p0[(x["mundo"], x["semente"])]
        x["g_ap"] = None if (ref is None or x["taxa_final"] is None) else ref - x["taxa_final"]
    res = {"ponto": nome, "mudanca": mudanca, "vidas": vidas, "celulas": celulas(vidas, cfg["bootstrap"]),
           "segundos": time.perf_counter() - t}
    _gravar(pasta / "resultado.json", _dump(res))
    return res


def _ic(valores: list, boot: dict) -> dict:
    v = [x for x in valores if x is not None]
    if len(v) < 2:
        return {"media": (v[0] if v else None), "ic_inferior": None, "ic_superior": None, "n": len(v)}
    return bootstrap_ic(v, boot["reamostragens"], boot["semente"], boot["nivel"])


def celulas(vidas: dict, boot: dict) -> dict:
    """Por mundo e braco: media e IC de cada medida, vidas com peso no teto e a razao da deriva (dia 14 / dia 7)."""
    out = {}
    for mundo in MUNDOS:
        for braco in BRACOS:
            xs = [x for x in vidas.values() if x["mundo"] == mundo and x["braco"] == braco]
            c = {med: _ic([x[med] for x in xs], boot) for med in MEDIDAS}
            meio = len(xs[0]["deriva_por_dia"]) // 2 - 1
            d7 = sum(x["deriva_por_dia"][meio] for x in xs) / len(xs)
            d14 = sum(x["deriva_por_dia"][-1] for x in xs) / len(xs)
            c["vidas_no_teto"] = sum(x["no_teto"] > 0 for x in xs)
            c["vidas"] = len(xs)
            c["razao_deriva_14_7"] = d14 / d7 if d7 > 0 else None
            out[f"{mundo}/{braco}"] = c
    return out


def contraste(ponto: dict, base: dict, mundo: str, braco: str, medida: str, boot: dict) -> dict:
    """Delta = ponto - base, pareado na unidade (mesma semente e genoma), IC por bootstrap sobre as unidades (secao 5)."""
    b = {(x["semente"], x["genoma"]): x[medida] for x in base["vidas"].values() if x["mundo"] == mundo and x["braco"] == braco}
    d = []
    for x in ponto["vidas"].values():
        if x["mundo"] == mundo and x["braco"] == braco:
            y = b[(x["semente"], x["genoma"])]
            if x[medida] is not None and y is not None:
                d.append(x[medida] - y)
    return _ic(d, boot)


def contrastes(ponto: dict, base: dict, boot: dict) -> dict:
    return {f"{mundo}/{braco}": {med: contraste(ponto, base, mundo, braco, med, boot) for med in MEDIDAS}
            for mundo in MUNDOS for braco in APRENDEM}


def _positivo(c: dict) -> bool:
    return c["ic_inferior"] is not None and c["ic_inferior"] > 0.0


def _negativo(c: dict) -> bool:
    return c["ic_superior"] is not None and c["ic_superior"] < 0.0


def piora_cuidado(ct: dict) -> bool:
    """Secao 6: delta da fracao fora de privacao ou da saude media, em P1 ou P3, em algum mundo, com IC inteiro abaixo de 0."""
    return any(_negativo(ct[k][med]) for k in ct for med in ("fora_privacao", "saude"))


def m1_descasado(ponto: dict, base: dict, boot: dict) -> dict:
    """Delta do M1 (aprendido decide) no descasado, media do P1 e do P3 por unidade (secao 7, passo 1)."""
    def por_unidade(res):
        out = {}
        for x in res["vidas"].values():
            if x["mundo"] == "descasado" and x["braco"] in APRENDEM:
                out.setdefault((x["semente"], x["genoma"]), []).append(x["m1_decidiu"])
        return {u: sum(v) / len(v) for u, v in out.items()}
    p, b = por_unidade(ponto), por_unidade(base)
    return _ic([p[u] - b[u] for u in p], boot)


def avaliar(resultados: dict, boot: dict) -> dict:
    base = resultados["base"]
    av = {}
    for nome, res in resultados.items():
        if nome == "base":
            continue
        ct = contrastes(res, base, boot)
        av[nome] = {"contrastes": ct, "piora_cuidado": piora_cuidado(ct), "m1_descasado_P1_P3": m1_descasado(res, base, boot),
                    "g_ap_descasado_P1": ct["descasado/P1"]["g_ap"]}
    return av


def diagnostico(resultados: dict, av: dict) -> dict:
    """Secao 6 do plano."""
    base = resultados["base"]["celulas"]
    pontos = lambda letra: [n for n in av if n.startswith(letra) and n != "combinado"]  # noqa: E731
    def sobe(n):
        a = av[n]
        return _positivo(a["g_ap_descasado_P1"]) or any(_positivo(a["contrastes"][k]["m1_decidiu"]) for k in a["contrastes"])
    metade = any(base[f"{m}/{b}"]["vidas_no_teto"] * 2 >= base[f"{m}/{b}"]["vidas"] for m in MUNDOS for b in APRENDEM)
    p_comer = base["descasado/P1"]["p_comer"]["media"]
    teto = {"metade_no_teto_na_base": metade, "pontos_que_sobem": [n for n in pontos("T") if sobe(n)]}
    teto["segura"] = metade and bool(teto["pontos_que_sobem"])
    janela = {"pontos_que_sobem": [n for n in pontos("J") if sobe(n)]}
    janela["segura"] = bool(janela["pontos_que_sobem"])
    expo = {"p_comer_base_descasado_P1": p_comer,
            "pontos_que_sobem": [n for n in pontos("X") if _positivo(av[n]["contrastes"]["descasado/P1"]["consumos"])
                                 and _positivo(av[n]["g_ap_descasado_P1"])]}
    expo["segura"] = p_comer is not None and p_comer < 0.30 and bool(expo["pontos_que_sobem"])
    return {"teto": teto, "janela": janela, "exposicao": expo,
            "piora_cuidado": [n for n in av if av[n]["piora_cuidado"]],
            "nenhuma_segura": not (teto["segura"] or janela["segura"] or expo["segura"])}


def escolher(av: dict, letra: str) -> dict:
    """Secao 7, passo 1: o ponto escolhido para uma alavanca (ou a base)."""
    cand = [n for n in av if n.startswith(letra) and n != "combinado" and not av[n]["piora_cuidado"]]
    ajudam = [n for n in cand if _positivo(av[n]["g_ap_descasado_P1"])]
    if ajudam:
        n = max(ajudam, key=lambda n: av[n]["g_ap_descasado_P1"]["ic_inferior"])
        return {"ponto": n, "por": "g_ap"}
    pelo_m1 = [n for n in cand if _positivo(av[n]["m1_descasado_P1_P3"])]
    if pelo_m1:
        n = max(pelo_m1, key=lambda n: av[n]["m1_descasado_P1_P3"]["ic_inferior"])
        return {"ponto": n, "por": "m1"}
    return {"ponto": "base", "por": None}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    a = ap.parse_args(argv)
    caminho = Path(a.config)
    cfg = carregar(caminho)
    executar(cfg, RAIZ / cfg["saida"], {"config": str(caminho), "config_sha256": _sha(caminho)})
    return 0


def executar(cfg: dict, saida: Path, origem: dict) -> dict:
    """O diagnostico inteiro (secoes 4 a 7 do plano) numa config ja carregada; devolve a recomendacao."""
    saida.mkdir(parents=True, exist_ok=True)
    _gravar(saida / "meta.json", _dump({
        **origem, "cfg": cfg, "plano_sha256": _sha(RAIZ / PLANO),
        "python": platform.python_version(), "plataforma": platform.platform(), "engine_sha256": sha256_engine(),
        "sha256": {f: _sha(RAIZ / f) for f in ("digilab/policies/lobos.py", "digilab/config.py", "experiments/bancada_v2.py",
                                                 "digilab/metrics.py", "digilab/motivo.py", "experiments/run_revisao_aprendiz.py")}}))
    t0 = time.perf_counter()
    resultados = {}
    with (saida / "varredura.jsonl").open("w", encoding="utf-8", newline="\n") as f:
        for nome, mudanca in cfg["pontos"].items():
            res = rodar_ponto(cfg, nome, mudanca, saida)
            resultados[nome] = res
            c = res["celulas"]
            linha = {"ponto": nome, "mudanca": mudanca, "segundos": res["segundos"],
                     **{f"{k}:{med}": c[k][med]["media"] for k in c for med in ("m1_decidiu", "g_ap", "p_comer", "saude")},
                     **{f"{k}:vidas_no_teto": c[k]["vidas_no_teto"] for k in c}}
            f.write(json.dumps(linha, sort_keys=True) + "\n")
            f.flush()
            print(f"[{nome}] {res['segundos']:.0f} s; descasado/P1: g_ap {c['descasado/P1']['g_ap']['media']}, "
                  f"M1 {c['descasado/P1']['m1_decidiu']['media']:.3f}, no teto {c['descasado/P1']['vidas_no_teto']}/"
                  f"{c['descasado/P1']['vidas']}", flush=True)
        boot = cfg["bootstrap"]
        av = avaliar(resultados, boot)
        diag = diagnostico(resultados, av)
        escolha = {ALAVANCAS[l]: escolher(av, l) for l in ALAVANCAS}
        movem = {k: e["ponto"] for k, e in escolha.items() if e["ponto"] != "base"}
        rec = {"regra": "plano, secao 7", "por_alavanca": escolha, "combinacao": None}
        if len(movem) >= 2:
            mudanca = {}
            for p in movem.values():
                for chave, campos in cfg["pontos"][p].items():
                    mudanca.setdefault(chave, {}).update(campos)
            res = rodar_ponto(cfg, "combinado", mudanca, saida)
            resultados["combinado"] = res
            ct = contrastes(res, resultados["base"], boot)
            melhor = max(movem.values(), key=lambda n: av[n]["g_ap_descasado_P1"]["media"] or float("-inf"))
            pior = (piora_cuidado(ct) or (ct["descasado/P1"]["g_ap"]["media"] or float("-inf"))
                    < (av[melhor]["g_ap_descasado_P1"]["media"] or float("-inf")))
            av["combinado"] = {"contrastes": ct, "piora_cuidado": piora_cuidado(ct),
                               "m1_descasado_P1_P3": m1_descasado(res, resultados["base"], boot),
                               "g_ap_descasado_P1": ct["descasado/P1"]["g_ap"]}
            rec["combinacao"] = {"mudanca": mudanca, "fica_a_melhor_sozinha": pior, "melhor_sozinha": melhor}
            rec["ponto_recomendado"] = {"pontos": [melhor]} if pior else {"pontos": sorted(movem.values())}
        else:
            rec["ponto_recomendado"] = {"pontos": sorted(movem.values()) or ["base"]}
        rec["mudanca_recomendada"] = {}
        for p in rec["ponto_recomendado"]["pontos"]:
            for chave, campos in cfg["pontos"][p].items():
                rec["mudanca_recomendada"].setdefault(chave, {}).update(campos)
    _gravar(saida / "avaliacao.json", _dump(av))
    _gravar(saida / "diagnostico.json", _dump(diag))
    rec["segundos_total"] = time.perf_counter() - t0
    _gravar(saida / "recomendacao.json", _dump(rec))
    print(f"diagnostico: teto {diag['teto']['segura']}, janela {diag['janela']['segura']}, exposicao {diag['exposicao']['segura']}; "
          f"recomendado {rec['ponto_recomendado']['pontos']} {rec['mudanca_recomendada']} ({rec['segundos_total']:.0f} s)")
    return rec


if __name__ == "__main__":
    sys.exit(main())
