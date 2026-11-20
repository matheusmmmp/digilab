"""V2, N3 (docs/PLANO_ANALISE_V2_N3.md, registrado antes da run): a consequencia da propria acao como sinal (braco P1).

    python experiments/run_v2_n3.py --config experiments/configs/v2_n3/calibracao.json   # grade do ganho, sementes 8101...8505
    python experiments/run_v2_n3.py --config experiments/configs/v2_n3/validacao.json    # UMA vez, 9101...9505

Por ponto (ganho): a bancada (experiments/bancada_v2.py, `rodar`) monta P0, P1 e P3 nos 4 donos x 5 sementes, os acoplados
P1 <- P0 (filtro nenhum: o cuidado controlado) e P3 <- P3 (sem sinais: o "so cuidado" da L1), rejoga toda vida do disco bit a
bit e grava medidas e tabelas. Aqui so se montam os gates do plano (secao 5) a partir das medidas da bancada e de
digilab/metrics.py e digilab/motivo.py; nenhuma metrica nova. Calibracao: a regra de escolha da secao 6. Validacao: uma vez.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import time
from collections import Counter
from dataclasses import replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
from digilab.config import CONFIG_CONSEQUENCIA  # noqa: E402
from digilab.events import LogDeEventos  # noqa: E402
from digilab.metrics import bootstrap_ic  # noqa: E402
from digilab.motivo import motivos_de_vida  # noqa: E402
from digilab.protocol import ENGINE_SHA256_V0, sha256_engine  # noqa: E402

SEMENTES_CALIBRACAO = (8101, 8202, 8303, 8404, 8505)
SEMENTES_VALIDACAO = (9101, 9202, 9303, 9404, 9505)
DONOS = ("atencioso", "relapso", "aleatorio", "incoerente")
PLANO = "docs/PLANO_ANALISE_V2_N3.md"
CHAVES = {"descricao", "conjunto", "sementes", "saida", "grade_ganho", "ganho", "dias", "orcamento", "sonda", "bootstrap"}
ACOPLADOS = [{"origem": "P0", "destino": "P1", "filtro": "nenhum"}, {"origem": "P3", "destino": "P3", "filtro": "sem_sinais"}]


def _dump(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _gravar(caminho: Path, texto: str) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(texto, encoding="utf-8", newline="\n")


def _sha(caminho: Path) -> str:
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


def cfg_bancada(cfg: dict, ganho: int) -> dict:
    return {"descricao": f"N3 ganho {ganho} ({cfg['conjunto']})", "plano": PLANO, "bracos": ["P0", "P1", "P3"],
            "donos": list(DONOS), "sementes": list(cfg["sementes"]), "genomas": [None], "mundos": ["padrao"],
            "dias": cfg["dias"], "orcamento": cfg["orcamento"], "sonda": cfg["sonda"], "bootstrap": cfg["bootstrap"],
            "acoplados": ACOPLADOS, "consequencia": {"ganho": int(ganho)}}


def privacao(m: dict) -> float:
    return 1.0 - m["fracao_fora_de_privacao"]


def _por(medidas: dict, braco: str) -> dict:
    """(dono, semente) -> medida do braco (rotulo da tabela: "P1" ou "P1<P0:nenhum")."""
    out = {}
    for m in medidas.values():
        if m["braco"] == braco:
            chave = (m["dono"], m["semente"])
            if chave in out:
                raise RuntimeError(f"duas vidas do braco {braco} na celula {chave}")
            out[chave] = m
    return out


def diferenca_por_semente(a: dict, b: dict, sementes, donos, medida) -> list[float]:
    """Por semente, a media nos donos de medida(a) - medida(b), pareado pela celula (dono, semente)."""
    return [sum(medida(a[(d, s)]) - medida(b[(d, s)]) for d in donos) / len(donos) for s in sementes]


def legibilidade_p1(r: dict, bancada: bv.Bancada, boot: dict, sementes) -> dict:
    """G4 do aprendido (relatado): pela regra de honestidade da L1 (motivo.motivo_lobos), nas vidas fechadas do P1."""
    por_semente: dict[int, Counter] = {}
    for v in r["vidas"].values():
        if v.espec.braco != "P1" or v.origem is not None:
            continue
        log = LogDeEventos.de_jsonl(v.motor.log.para_jsonl())
        _, emb = motivos_de_vida(log, bancada.fabrica_politica(v.espec), v.espec.semente)
        c = por_semente.setdefault(v.espec.semente, Counter())
        for m, d in zip(emb.motivos, emb.diagnosticos):
            c["decisoes"] += 1
            c["com_fator"] += bool(m.fatores)
            c["decisao_decidiu"] += d["lobo"] == "decisao"
            c["decisao_com_fator"] += d["lobo"] == "decisao" and bool(m.fatores)
    tot = sum(por_semente.values(), Counter())
    frac = [por_semente[s]["decisao_com_fator"] / por_semente[s]["decisoes"] for s in sementes]
    return {"fracao_aprendido_com_fator": tot["decisao_com_fator"] / tot["decisoes"],
            "fracao_aprendido_decidiu": tot["decisao_decidiu"] / tot["decisoes"],
            "fracao_bruta_com_fator": tot["com_fator"] / tot["decisoes"],
            "ic_aprendido": bootstrap_ic(frac, boot["reamostragens"], boot["semente"], boot["nivel"])}


def acoes_por_regra(r: dict, braco: str) -> dict:
    """Fracao de cada acao nas duas regras com sorteio (fome moderada, tempo livre), nas vidas fechadas do braco: a previsao da
    secao 3.1 do plano. Le os motivos que o proprio cerebro registrou na vida."""
    cont: dict[str, Counter] = {"fome_moderada": Counter(), "tempo_livre": Counter()}
    for v in r["vidas"].values():
        if v.espec.braco != braco or v.origem is not None:
            continue
        for m in v.motor.politica.cerebro.motivos:
            if m["regra"] in cont:
                cont[m["regra"]][m["acao"]] += 1
    return {regra: {a: n / sum(c.values()) for a, n in sorted(c.items())} for regra, c in cont.items() if c}


def avaliar(r: dict, bancada: bv.Bancada, cfg: dict, ganho: int) -> dict:
    medidas, sementes, boot = r["medidas"], list(cfg["sementes"]), cfg["bootstrap"]
    ic = lambda xs: bootstrap_ic(xs, boot["reamostragens"], boot["semente"], boot["nivel"])  # noqa: E731
    p0, p1, p3 = _por(medidas, "P0"), _por(medidas, "P1"), _por(medidas, "P3")
    p1a, so_cuidado = _por(medidas, "P1<P0:nenhum"), _por(medidas, "P3<P3:sem_sinais")
    g_p1 = diferenca_por_semente(p0, p1, sementes, DONOS, privacao)
    acop = diferenca_por_semente(p0, p1a, sementes, DONOS, privacao)
    por_dono = {d: ic([privacao(p0[(d, s)]) - privacao(p1[(d, s)]) for s in sementes]) for d in DONOS}
    saude = diferenca_por_semente(p1, p0, sementes, DONOS, lambda m: m["saude_media"])
    vidas_p1 = [v for v in r["vidas"].values() if v.espec.braco == "P1" and v.origem is None]
    no_teto = {v.nome: v.motor.politica.cerebro.pesos_no_teto() for v in vidas_p1}
    deriva = [p1[c]["custo_da_plasticidade"]["deriva_por_dia"] for c in p1]
    meio = cfg["dias"] // 2 - 1                    # 14 dias: o dia 7 (indice 6) e o dia 14 (o ultimo)
    d7 = sum(x[meio] for x in deriva) / len(deriva)
    d14 = sum(x[-1] for x in deriva) / len(deriva)
    gp1 = ic(g_p1)
    gates = {
        "G_P1_privacao": {**gp1, "por_semente": dict(zip(map(str, sementes), g_p1)), "passa": gp1["ic_inferior"] > 0.0,
                          "definicao": "por semente, media nos 4 donos de (privacao P0 - privacao P1), vidas fechadas"},
        "sem_mortes_novas": {"mortes_P0": 0, "mortes_P1": 0, "passa": True,
                             "nota": "mundo padrao (MotorComFeedback, sem lesoes nem morte): vale por construcao"},
        "G6": {"vidas_com_peso_no_teto": sum(n > 0 for n in no_teto.values()), "pesos_no_teto_por_vida": no_teto,
               "passa": all(n == 0 for n in no_teto.values()),
               "razao_deriva_14_7": d14 / d7 if d7 > 0 else None, "deriva_media_dia7": d7, "deriva_media_dia14": d14},
    }
    media = lambda tab, f: sum(f(m) for m in tab.values()) / len(tab)  # noqa: E731
    return {
        "ganho": ganho, "gates": gates,
        "relatado": {
            "privacao_por_dono_P0_menos_P1": por_dono,
            "acoplado_P0_menos_P1_mesmo_cuidado": {**ic(acop), "por_semente": dict(zip(map(str, sementes), acop))},
            "saude_P1_menos_P0": ic(saude),
            "privacao_media": {b: media(t, privacao) for b, t in
                               (("P0", p0), ("P1", p1), ("P3", p3), ("P1<P0:nenhum", p1a), ("P3<P3:sem_sinais", so_cuidado))},
            "saude_media": {b: media(t, lambda m: m["saude_media"]) for b, t in (("P0", p0), ("P1", p1), ("P3", p3))},
            "acerto_na_tarefa_media": {b: media(t, lambda m: m["acerto_total"]) for b, t in (("P0", p0), ("P1", p1), ("P3", p3))},
            "deriva_final_media": {b: media(t, lambda m: m["deriva_final"]) for b, t in (("P1", p1), ("P3", p3))},
            "g4": legibilidade_p1(r, bancada, boot, sementes),
            "acoes_por_regra": {"P0": acoes_por_regra(r, "P0"), "P1": acoes_por_regra(r, "P1")},
            "interacoes_acoplado_so_cuidado": sorted({m["interacoes"] for m in so_cuidado.values()}),
        },
    }


def chave_escolha(a: dict) -> tuple:
    """Secao 6: G6 passando > maior IC inferior do G-P1 > menor ganho. Sem G6: menos vidas no teto, depois o G-P1."""
    g = a["gates"]
    if g["G6"]["passa"]:
        return (1, 0, g["G_P1_privacao"]["ic_inferior"], -a["ganho"])
    return (0, -g["G6"]["vidas_com_peso_no_teto"], g["G_P1_privacao"]["ic_inferior"], -a["ganho"])


def carregar(caminho: Path) -> dict:
    cfg = json.loads(caminho.read_text(encoding="utf-8"))
    sobram = set(cfg) - CHAVES
    if sobram:
        raise KeyError(f"chaves desconhecidas: {sorted(sobram)}")
    if sha256_engine() != ENGINE_SHA256_V0:
        raise RuntimeError("engine.py mudou")
    esperadas = {"calibracao": SEMENTES_CALIBRACAO, "validacao": SEMENTES_VALIDACAO}[cfg["conjunto"]]
    if tuple(cfg["sementes"]) != esperadas:
        raise ValueError(f"sementes de {cfg['conjunto']} precisam ser {esperadas}")
    if cfg["conjunto"] == "calibracao" and "grade_ganho" not in cfg:
        raise ValueError("calibracao precisa da grade_ganho")
    if cfg["conjunto"] == "validacao" and "ganho" not in cfg:
        raise ValueError("validacao precisa do ganho escolhido na calibracao")
    cfg.setdefault("dias", 14)
    cfg.setdefault("orcamento", 224)
    cfg.setdefault("sonda", {"estados": 64, "amostras": 200, "semente": 9001})
    cfg.setdefault("bootstrap", {"reamostragens": 10000, "semente": 20261004, "nivel": 0.95})
    return cfg


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    a = ap.parse_args(argv)
    caminho = Path(a.config)
    cfg = carregar(caminho)
    saida = RAIZ / cfg["saida"]
    if cfg["conjunto"] == "validacao" and saida.exists():
        raise RuntimeError(f"{saida} ja existe: a validacao roda uma vez so")
    saida.mkdir(parents=True, exist_ok=True)
    _gravar(saida / "meta.json", _dump({
        "config": str(caminho), "config_sha256": _sha(caminho), "cfg": cfg, "python": platform.python_version(),
        "plataforma": platform.platform(), "engine_sha256": sha256_engine(),
        "sha256": {f: _sha(RAIZ / f) for f in ("digilab/policies/lobos.py", "digilab/config.py", "experiments/bancada_v2.py",
                                                 "digilab/metrics.py", "experiments/run_v2_n3.py")}}))
    ganhos = cfg["grade_ganho"] if cfg["conjunto"] == "calibracao" else [cfg["ganho"]]
    avaliacoes = []
    t0 = time.perf_counter()
    with (saida / "varredura.jsonl").open("w", encoding="utf-8", newline="\n") as f:
        for g in ganhos:
            t = time.perf_counter()
            cb = cfg_bancada(cfg, g)
            pasta = saida / f"ganho{g}"
            r = bv.rodar(cb, pasta)
            bancada = bv.Bancada(cb["dias"], cb["orcamento"], cfg_consequencia=replace(CONFIG_CONSEQUENCIA, ganho=int(g)))
            av = avaliar(r, bancada, cfg, g)
            av["segundos"] = time.perf_counter() - t
            _gravar(pasta / "resultado.json", _dump(av))
            gt = av["gates"]
            f.write(json.dumps({"ganho": g, "G_P1": gt["G_P1_privacao"]["media"], "G_P1_ic_inferior": gt["G_P1_privacao"]["ic_inferior"],
                                "G_P1_passa": gt["G_P1_privacao"]["passa"], "G6_vidas_no_teto": gt["G6"]["vidas_com_peso_no_teto"],
                                "G6_passa": gt["G6"]["passa"], "razao_deriva": gt["G6"]["razao_deriva_14_7"],
                                "segundos": av["segundos"]}, sort_keys=True) + "\n")
            f.flush()
            avaliacoes.append(av)
            print(f"[ganho {g}] G-P1 {gt['G_P1_privacao']['media']:+.4f} [{gt['G_P1_privacao']['ic_inferior']:+.4f}; "
                  f"{gt['G_P1_privacao']['ic_superior']:+.4f}] G6 {gt['G6']['vidas_com_peso_no_teto']} vidas no teto "
                  f"(razao {gt['G6']['razao_deriva_14_7']}) ({av['segundos']:.0f} s)", flush=True)
    escolhido = max(avaliacoes, key=chave_escolha)
    escolha = {"conjunto": cfg["conjunto"], "ganho": escolhido["ganho"], "gates": escolhido["gates"],
               "segundos_total": time.perf_counter() - t0}
    if cfg["conjunto"] == "calibracao":
        escolha["regra"] = "secao 6 do plano: G6 passando, maior IC inferior do G-P1; empate: menor ganho"
        escolha["calibracao_fechou"] = escolhido["gates"]["G6"]["passa"]
    _gravar(saida / "escolha.json", _dump(escolha))
    g = escolha["gates"]
    print(f"[{cfg['conjunto']}] ganho {escolha['ganho']}: G-P1 {'PASSA' if g['G_P1_privacao']['passa'] else 'FALHA'} "
          f"({g['G_P1_privacao']['media']:+.4f} [{g['G_P1_privacao']['ic_inferior']:+.4f}; {g['G_P1_privacao']['ic_superior']:+.4f}]), "
          f"G6 {'PASSA' if g['G6']['passa'] else 'FALHA'} ({g['G6']['vidas_com_peso_no_teto']} vidas no teto), sem mortes novas (por construcao)")
    return 0 if (g["G_P1_privacao"]["passa"] and g["G6"]["passa"]) else 2


if __name__ == "__main__":
    sys.exit(main())
