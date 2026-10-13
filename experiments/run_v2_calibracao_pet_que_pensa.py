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
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from experiments import bancada_v2 as bv  # noqa: E402

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


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="calibracao do g_plano do pet que pensa (PLANO_ANALISE_V2_PET_QUE_PENSA, secao 5)")
    ap.add_argument("--config", required=True)
    ap.add_argument("--saida", required=True)
    ap.add_argument("--processos", type=int, default=1, help="os pontos da grade em paralelo")
    a = ap.parse_args(argv)
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))
    r = rodar(cfg, Path(a.saida), a.processos)
    e = r["escolha"]
    for p in r["pontos"]:
        print(f"g_plano {p['g_plano']}: media {p['media']}, {p['sem_alvo']} unidade(s) sem alvo na janela")
    print(f"escolha: g_plano {e['g_plano']} ({'fechou' if e['fechou'] else 'nao fechou, desvio ' + str(e['desvio'])}); em {a.saida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
