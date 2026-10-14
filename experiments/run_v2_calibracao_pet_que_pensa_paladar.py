"""A calibracao do pet que pensa com o paladar (J5; docs/PLANO_ANALISE_V2_PET_QUE_PENSA.md, adendo 3: A3.2 a A3.5; PJ-3 a PJ-6).

Os passos, um depois do outro, na mesma pasta, cada um com o seu `--passo` (a ordem e conferida: um passo recusa rodar sem o anterior):

1. **`ganho_gosto`** (A3.3, passo 1; PL-8, PJ-3): a grade {S/2, S, 2S} do `ganho_gosto` (`ConfigConsequencia.ganho_gosto`). Roda o **P1**
   (sem o planejador), so na fase 1, nas unidades de calibracao do paladar (bases 49101...49505, K_u = 4, prefixo `pet_que_pensa`), uma
   vida por unidade e ponto, pela bancada do J5 (`rodar_pqp`, que grava as vidas e as rejoga do disco bit a bit).
   - **A medida:** por unidade, a fracao de fruta madura (os tres tipos juntos) entre os consumos no mapa nos dias 4 a 6
     (`bancada_v2.fracao_fruta_dias`; o denominador e todo consumo no mapa); por ponto, a media sobre as unidades com algum consumo.
   - **A regra:** o **menor** ponto com a media em [0,25; 0,60]. Sem ponto na faixa, o mais perto dela (empate: o menor), com o desvio
     declarado, e a calibracao segue (a faixa que nao fecha nao bloqueia).
   Saida: `<pasta>/ganho_gosto/ganho_<g>/` (a bancada) por ponto e `<pasta>/ganho_gosto/ganho_gosto.json`.
2. **`g_plano`** (A3.3, passo 2; PJ-4): a regra da secao 5 sem mudanca (o P1-plan na fase 1, a grade {S/4, S/2, S}, a sonda nos dias 4 a
   6, a faixa [0,10; 0,40]), com o `ganho_gosto` do passo 1, pelo orquestrador de antes (`run_v2_calibracao_pet_que_pensa.rodar`).
   Saida: `<pasta>/g_plano/` (o `g_plano.json` dele).
3. **`reval`** (A3.2; PJ-6): a premissa G-REVAL-POSSIVEL, sem vida nenhuma: por unidade, a conta do sinal do cerebro para comer cada tipo
   maduro no estado de referencia (`BancadaPQP.g_reval_possivel`), com o `ganho_gosto` do passo 1. A premissa passa com no maximo 25%
   das unidades falhando. Saida: `<pasta>/reval.json`.
4. **`piloto`** (A3.4): so com a G-REVAL-POSSIVEL passando (falhando, o T1 e inconclusivo por desenho, o piloto nao roda e o plano volta
   ao Matheus). Igual a secao 6, no `ganho_gosto` e no `g_plano` escolhidos, pelo orquestrador de antes (`rodar_piloto`), em
   `<pasta>/g_plano/piloto/`.

Nenhuma regra le a escolha da x, `f_antes`, `q`, `m` nem um contraste entre bracos. Recusa a pasta de cada passo que ja existe, as bases
da validacao e as da calibracao sem o paladar (45101..., A3.5).

    python experiments/run_v2_calibracao_pet_que_pensa_paladar.py --config experiments/configs/v2_pet_que_pensa/calibracao_paladar.json \\
        --saida artifacts_v2_pet_que_pensa/calibracao_paladar --passo ganho_gosto --processos 3
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
from experiments import run_v2_calibracao_pet_que_pensa as cpq  # noqa: E402

CHAVE_GOSTO = "calibracao_ganho_gosto"
CHAVE_PLANO = cpq.CHAVE
BRACO_GOSTO = "P1"                        # A3.3: o ganho_gosto se calibra sem o planejador
PROTOCOLO = "fase1"
LIMIAR_REVAL = 0.25                       # A3.2: no maximo 25% das unidades falhando (a tolerancia da G-OPORTUNIDADE)
PASSOS = ("ganho_gosto", "g_plano", "reval", "piloto")


def validar(cfg: dict) -> dict:
    """A config: a do J5 com o paladar, sem `bracos`, `protocolos` nem `g_plano` (o orquestrador os poe em cada passo) e sem o
    `ganho_gosto` na consequencia (vem da grade), mais `calibracao_ganho_gosto` e `calibracao_g_plano` = {grade, dias, faixa}. Cada
    ponto e conferido pela bancada (`validar_config_pqp`) e o passo 2 pelo orquestrador de antes."""
    if cfg.get("paladar") is not True:
        raise ValueError("a calibracao do adendo 3 e com o paladar: 'paladar': true")
    if {"bracos", "protocolos", "g_plano"} & set(cfg):
        raise ValueError("a config da calibracao com o paladar nao traz 'bracos', 'protocolos' nem 'g_plano': cada passo os poe")
    if "ganho_gosto" in cfg.get("consequencia", {}):
        raise ValueError("a calibracao escolhe o ganho_gosto: a 'consequencia' nao o traz (a grade vem em 'calibracao_ganho_gosto')")
    for chave in (CHAVE_GOSTO, CHAVE_PLANO):
        if chave not in cfg:
            raise ValueError(f"config da calibracao com o paladar sem {chave!r}")
        c = cfg[chave]
        if set(c) != {"grade", "dias", "faixa"}:
            raise ValueError(f"{chave}: {{'grade', 'dias', 'faixa'}}, nao {sorted(c)}")
    c = cfg[CHAVE_GOSTO]
    grade = list(c["grade"])
    if not grade or any(type(g) is not int or g <= 0 for g in grade) or grade != sorted(set(grade)):
        raise ValueError(f"grade do ganho_gosto {grade}: inteiros > 0, crescentes, sem repetir")
    d_a = int(cfg.get("d_a", bv.D_A_PQP))
    ini, fim = c["dias"]
    if not 0 <= ini <= fim <= d_a - 1:
        raise ValueError(f"dias da regra do ganho_gosto {c['dias']}: dentro da fase 1 (0 a {d_a - 1})")
    lo, hi = c["faixa"]
    if not 0 <= lo < hi <= 1:
        raise ValueError(f"faixa da regra do ganho_gosto {c['faixa']}")
    if "unidades" in cfg:
        validacao = set(cfg["unidades"]["bases"]) & set(bv.BASES_PET_QUE_PENSA["validacao"])
        if validacao:
            raise bv.SementeSemPlano(f"bases {sorted(validacao)} da validacao do J5: a calibracao recusa (secao 11)")
    for g in grade:
        bv.validar_config_pqp(config_do_gosto(cfg, g))
    cpq.validar(config_do_plano(cfg, grade[0]))
    return cfg


def _com_ganho(cfg: dict, g: int) -> dict:
    return {**{k: v for k, v in cfg.items() if k not in (CHAVE_GOSTO, CHAVE_PLANO)},
            "consequencia": {**cfg.get("consequencia", {}), "ganho_gosto": g}}


def config_do_gosto(cfg: dict, g: int) -> dict:
    """um ponto do passo 1: o P1 na fase 1, com o ganho_gosto g"""
    return {**_com_ganho(cfg, g), "bracos": [BRACO_GOSTO], "protocolos": [PROTOCOLO]}


def config_do_plano(cfg: dict, g: int) -> dict:
    """a config do orquestrador de antes (passos 2 e 4): o P1-plan na fase 1, com o ganho_gosto g e a grade do g_plano"""
    return {**_com_ganho(cfg, g), "bracos": [cpq.BRACO_CALIBRACAO], "protocolos": [cpq.PROTOCOLO_CALIBRACAO],
            CHAVE_PLANO: cfg[CHAVE_PLANO]}


def fracoes_do_ponto(medidas: dict, dias: tuple) -> dict:
    """por unidade (uma vida do P1 na fase 1), a fracao de fruta da regra; a media sobre as unidades com algum consumo na janela"""
    por_unidade = []
    for nome in sorted(medidas):
        m = medidas[nome]
        if m["braco"] != BRACO_GOSTO or m["protocolo"] != PROTOCOLO:
            raise ValueError(f"vida {nome} fora da calibracao do ganho_gosto")
        por_unidade.append({"vida": nome, "semente": m["semente"], "unidade": m.get("unidade"), "x": m["x"],
                            **bv.fracao_fruta_dias(m, tuple(dias))})
    com = [u["fracao"] for u in por_unidade if u["fracao"] is not None]
    return {"por_unidade": por_unidade, "n_unidades": len(por_unidade), "sem_consumo": len(por_unidade) - len(com),
            "media": None if not com else sum(com) / len(com)}


def escolha_ganho(pontos: list, faixa: tuple) -> dict:
    """A regra do A3.3: o menor ganho_gosto com a media na faixa; senao, o mais perto dela (empate, o menor), com o desvio."""
    lo, hi = faixa
    validos = [p for p in pontos if p["media"] is not None]
    if not validos:
        raise RuntimeError("nenhum ponto da grade do ganho_gosto com consumo na janela da regra")
    dentro = [p for p in validos if lo <= p["media"] <= hi]
    if dentro:
        p = min(dentro, key=lambda q: q["ganho_gosto"])
        return {"ganho_gosto": p["ganho_gosto"], "media": p["media"], "fechou": True, "desvio": 0.0}
    dist = lambda q: lo - q["media"] if q["media"] < lo else q["media"] - hi  # noqa: E731
    p = min(validos, key=lambda q: (dist(q), q["ganho_gosto"]))
    return {"ganho_gosto": p["ganho_gosto"], "media": p["media"], "fechou": False, "desvio": dist(p),
            "lado": "abaixo" if p["media"] < lo else "acima"}


def _meta(cfg: dict, processos: int) -> dict:
    return {**bv.meta(cfg), "plano": bv.PLANO_PQP, "modelo_mundo_sha256": bv._sha(RAIZ / "digilab" / "modelo_mundo.py"),
            "orquestrador_sha256": bv._sha(Path(__file__)), "orquestrador_g_plano_sha256": bv._sha(Path(cpq.__file__)),
            "processos": processos}


def rodar_ganho_gosto(cfg: dict, pasta: Path, processos: int = 1) -> dict:
    validar(cfg)
    saida = pasta / "ganho_gosto"
    if saida.exists():
        raise FileExistsError(f"{saida}: a pasta do passo do ganho_gosto ja existe")
    c = cfg[CHAVE_GOSTO]
    grade, dias, faixa = list(c["grade"]), tuple(c["dias"]), tuple(c["faixa"])
    saida.mkdir(parents=True)
    t0 = time.time()
    tarefas = [(config_do_gosto(cfg, g), str(saida / f"ganho_{g}")) for g in grade]
    if processos > 1:
        with ProcessPoolExecutor(max_workers=min(processos, len(tarefas))) as ex:
            resultados = list(ex.map(cpq._rodar_ponto, *zip(*tarefas)))
    else:
        resultados = [cpq._rodar_ponto(*t) for t in tarefas]
    pontos = []
    for g, r in zip(grade, resultados):
        if any(m["paladar"]["g_reval"]["ganho_gosto"] != g for m in r["medidas"].values()):
            raise RuntimeError(f"o ponto ganho_gosto {g} tem vidas com outro ganho_gosto")
        f = fracoes_do_ponto(r["medidas"], dias)
        cpu = [m["custo"]["cpu_s"] for m in r["medidas"].values()]
        pontos.append({"ganho_gosto": g, **f, "parede_s": r["parede_s"], "cpu_s_por_vida": sum(cpu) / len(cpu)})
    e = escolha_ganho(pontos, faixa)
    out = {"regra": {"medida": "fracao de fruta madura (os tres tipos) entre os consumos no mapa, media sobre as unidades",
                     "dias": list(dias), "faixa": list(faixa), "grade": grade,
                     "fonte": "PLANO_ANALISE_V2_PET_QUE_PENSA, adendo 3, A3.3 (PL-8, PJ-3)"},
           "pontos": pontos, "escolha": e, "parede_s": time.time() - t0}
    bv._gravar(saida / "ganho_gosto.json", bv._dump(out))
    bv._gravar(saida / "meta.json", bv._dump(_meta(cfg, processos)))
    return out


def _ganho_escolhido(pasta: Path) -> int:
    caminho = pasta / "ganho_gosto" / "ganho_gosto.json"
    if not caminho.is_file():
        raise FileNotFoundError(f"{caminho}: o passo do ganho_gosto (o 1) ainda nao rodou")
    return json.loads(caminho.read_text(encoding="utf-8"))["escolha"]["ganho_gosto"]


def rodar_g_plano(cfg: dict, pasta: Path, processos: int = 1) -> dict:
    validar(cfg)
    return cpq.rodar(config_do_plano(cfg, _ganho_escolhido(pasta)), pasta / "g_plano", processos)


def g_reval(cfg: dict, ganho_gosto: int) -> dict:
    """A G-REVAL-POSSIVEL (A3.2) nas unidades da config, com o ganho_gosto dado: a conta por unidade e a premissa (no maximo 25%
    falhando). Nao roda vida nenhuma."""
    c = config_do_gosto(cfg, ganho_gosto)
    bp = bv.bancada_pqp_da_config(c)
    if "unidades" in c:
        sementes = [(u["semente"], {"base": u["base"], "k": u["k"]})
                    for u in bv.unidades_derivadas(c["unidades"]["bases"], int(c["unidades"]["k"]), c["unidades"]["prefixo"])]
    else:
        sementes = [(int(s), None) for s in c["sementes"]]
    por_unidade = [{"semente": s, "unidade": u, **bp.g_reval_possivel(s)} for s, u in sementes]
    falham = sum(1 for u in por_unidade if not u["passa"])
    return {"ganho_gosto": ganho_gosto, "por_unidade": por_unidade, "n": len(por_unidade), "falham": falham,
            "fracao_falha": falham / len(por_unidade), "limiar": LIMIAR_REVAL, "passa": falham / len(por_unidade) <= LIMIAR_REVAL,
            "regra": "PLANO_ANALISE_V2_PET_QUE_PENSA, adendo 3, A3.2 (PJ-6): a unidade passa se o sinal da x depois da mudanca for menor que "
                     "o da racao ou o de outra fruta; a premissa, com no maximo 25% das unidades falhando"}


def rodar_reval(cfg: dict, pasta: Path) -> dict:
    validar(cfg)
    caminho = pasta / "reval.json"
    if caminho.exists():
        raise FileExistsError(f"{caminho}: a G-REVAL-POSSIVEL ja foi conferida")
    out = g_reval(cfg, _ganho_escolhido(pasta))
    bv._gravar(caminho, bv._dump({**out, "meta": _meta(cfg, 1)}))
    return out


def rodar_piloto(cfg: dict, pasta: Path, processos: int = 1) -> dict:
    validar(cfg)
    caminho = pasta / "reval.json"
    if not caminho.is_file():
        raise FileNotFoundError(f"{caminho}: a G-REVAL-POSSIVEL (o passo 3) ainda nao rodou")
    reval = json.loads(caminho.read_text(encoding="utf-8"))
    ganho = _ganho_escolhido(pasta)
    if reval["ganho_gosto"] != ganho:
        raise RuntimeError(f"a G-REVAL-POSSIVEL foi conferida no ganho_gosto {reval['ganho_gosto']}, o escolhido e {ganho}")
    if not reval["passa"]:
        raise RuntimeError(f"G-REVAL-POSSIVEL falha ({reval['falham']} de {reval['n']} unidades): o T1 e inconclusivo por desenho; o "
                           "piloto nao roda e o plano volta ao Matheus (A3.2)")
    return cpq.rodar_piloto(config_do_plano(cfg, ganho), pasta / "g_plano", processos)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="calibracao do pet que pensa com o paladar (PLANO_ANALISE_V2_PET_QUE_PENSA, adendo 3)")
    ap.add_argument("--config", required=True)
    ap.add_argument("--saida", required=True)
    ap.add_argument("--passo", required=True, choices=PASSOS)
    ap.add_argument("--processos", type=int, default=1, help="os pontos da grade (ou os bracos do piloto) em paralelo")
    a = ap.parse_args(argv)
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))
    pasta = Path(a.saida)
    if a.passo == "ganho_gosto":
        r = rodar_ganho_gosto(cfg, pasta, a.processos)
        for p in r["pontos"]:
            print(f"ganho_gosto {p['ganho_gosto']}: media {p['media']}, {p['sem_consumo']} unidade(s) sem consumo na janela")
        e = r["escolha"]
        print(f"escolha: ganho_gosto {e['ganho_gosto']} ({'fechou' if e['fechou'] else 'nao fechou, desvio ' + str(e['desvio'])})")
    elif a.passo == "g_plano":
        e = rodar_g_plano(cfg, pasta, a.processos)["escolha"]
        print(f"escolha: g_plano {e['g_plano']} ({'fechou' if e['fechou'] else 'nao fechou, desvio ' + str(e['desvio'])})")
    elif a.passo == "reval":
        r = rodar_reval(cfg, pasta)
        print(f"G-REVAL-POSSIVEL no ganho_gosto {r['ganho_gosto']}: {r['falham']} de {r['n']} unidades falham; "
              f"{'passa' if r['passa'] else 'FALHA: o piloto nao roda'}")
    else:
        r = rodar_piloto(cfg, pasta, a.processos)
        mg, n = r["margens"], r["n"]
        print(f"piloto: Delta_T1 {mg['delta_t1']}, Delta_T2 {mg['delta_t2']}, K_u {None if n is None else n['k']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
