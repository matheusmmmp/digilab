"""O piloto do adendo 7 do pet que pensa (J5; docs/PLANO_ANALISE_V2_PET_QUE_PENSA.md, A7.2 a A7.4 e A7.8; PJ7-1 a PJ7-6). SEM recalibrar.

A fase 1 e a mesma do adendo 5 (PJ7-5): ficam o `ganho_gosto` e o `g_plano` do adendo 6, conferidos contra os artefatos da calibracao com
a fruta ao lado (`adendo_7.calibracao`). Nas unidades do piloto do adendo 7 (bases 52101...52505, K_u = 4, prefixo `pet_que_pensa`), com
a chave `adendo_7` da bancada (a oportunidade nova do T1, a busca sem a fome e a fruta ao lado parando em `T_m` no T2) e a janela de 5 dias:

1. **`reval`** (A3.2, refeita nas sementes novas): a G-REVAL-POSSIVEL por unidade, sem vida; passa com no maximo 25% das unidades
   falhando. Saida: `<pasta>/reval.json`.
2. **`piloto`** (secao 6, com as definicoes novas): so com a G-REVAL-POSSIVEL passando. Os 4 bracos x T1 e T2, pelo nucleo do piloto do J5
   (`run_v2_calibracao_pet_que_pensa.piloto`), com a G-APRENDEU pelo acaso medio do braco (PJ7-3). Saida: `<pasta>/piloto/` (as margens,
   o N, as premissas e o custo, que vao ao adendo 8).

Recusa a pasta de cada passo que ja existe e as bases fora das do piloto do adendo 7.

**O adendo 8** (`"adendo_8": true`, por cima do 7; A8.5 e A8.9): o mesmo piloto, sem recalibrar, nas bases 54101...54505, com a chave
`piloto_adendo8` no lugar da `piloto_adendo7`. Na bancada, a x sai das arvores no T1 em `T_m` e o T2 busca pelas arvores, sem o corte.

    python experiments/run_v2_piloto_pet_que_pensa_adendo7.py --config experiments/configs/v2_pet_que_pensa/piloto_adendo7.json \\
        --saida artifacts_v2_pet_que_pensa/piloto_adendo7 --passo reval
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from experiments import bancada_v2 as bv  # noqa: E402
from experiments import run_v2_calibracao_pet_que_pensa as cpq  # noqa: E402
from experiments import run_v2_calibracao_pet_que_pensa_paladar as cpp  # noqa: E402

CHAVE = "piloto_adendo7"
CHAVE_8 = "piloto_adendo8"


def chave(cfg: dict) -> str:
    """a chave do orquestrador na config: a do adendo 8 com `adendo_8`, senao a do 7"""
    return CHAVE_8 if cfg.get("adendo_8") is True else CHAVE


def bases_piloto(cfg: dict) -> tuple:
    return bv.BASES_PQP_ADENDO8["piloto"] if cfg.get("adendo_8") is True else bv.BASES_PQP_ADENDO7["piloto"]
PASSOS = ("reval", "piloto")


def validar(cfg: dict) -> dict:
    """A config: a do J5 com o paladar, a fruta ao lado e o `adendo_7`, o `ganho_gosto` na consequencia e o `g_plano`, sem `bracos` nem
    `protocolos` (cada passo os poe), mais `piloto_adendo7` = {calibracao} com as bases do plano (os numeros do adendo 6 conferidos)."""
    if not (cfg.get("paladar") is True and cfg.get("fruta_ao_lado") is True and cfg.get("adendo_7") is True):
        raise ValueError("o piloto do adendo 7 e com o paladar, a fruta ao lado e o adendo 7: as tres chaves true")
    if {"bracos", "protocolos"} & set(cfg):
        raise ValueError("a config do piloto do adendo 7 nao traz 'bracos' nem 'protocolos': cada passo os poe")
    if {CHAVE, CHAVE_8} & set(cfg) != {chave(cfg)} or set(cfg[chave(cfg)]) - {"calibracao"}:
        raise ValueError(f"{chave(cfg)!r} (e so ela): {{'calibracao'}} (vazio so nas sementes dos testes)")
    if "ganho_gosto" not in cfg.get("consequencia", {}) or type(cfg.get("g_plano")) is not int:
        raise ValueError("o piloto do adendo 7 usa o ganho_gosto e o g_plano do adendo 6: na consequencia e em 'g_plano'")
    bv.validar_config_pqp(config_do_piloto(cfg))
    if "unidades" in cfg:
        if not set(cfg["unidades"]["bases"]) <= set(bases_piloto(cfg)):
            raise bv.SementeSemPlano(f"o piloto usa as bases {bases_piloto(cfg)} ({'A8.9' if cfg.get('adendo_8') else 'A7.8'})")
        if "calibracao" not in cfg[chave(cfg)]:
            raise ValueError("o piloto com as bases do plano confere o ganho_gosto e o g_plano contra a calibracao: a chave 'calibracao'")
        conferir_adendo6(cfg)
    return cfg


def conferir_adendo6(cfg: dict) -> dict:
    """PJ7-5: o `ganho_gosto` e o `g_plano` da config sao os escolhidos na calibracao com a fruta ao lado (o adendo 6). Falha alto."""
    pasta = RAIZ / cfg[chave(cfg)]["calibracao"]
    gg = json.loads((pasta / "ganho_gosto" / "ganho_gosto.json").read_text(encoding="utf-8"))["escolha"]["ganho_gosto"]
    gp = json.loads((pasta / "g_plano" / "g_plano.json").read_text(encoding="utf-8"))["escolha"]["g_plano"]
    if (cfg["consequencia"]["ganho_gosto"], cfg["g_plano"]) != (gg, gp):
        raise ValueError(f"o ganho_gosto e o g_plano do piloto do adendo 7 nao sao os do adendo 6: "
                         f"{(cfg['consequencia']['ganho_gosto'], cfg['g_plano'])} contra {(gg, gp)}")
    return {"ganho_gosto": gg, "g_plano": gp}


def _base(cfg: dict) -> dict:
    return {k: v for k, v in cfg.items() if k not in (CHAVE, CHAVE_8)}


def config_do_piloto(cfg: dict) -> dict:
    return {**_base(cfg), "bracos": list(bv.BRACOS_PQP), "protocolos": list(cpq.PROTOCOLOS_PILOTO)}


def rodar_reval(cfg: dict, pasta: Path) -> dict:
    validar(cfg)
    caminho = pasta / "reval.json"
    if caminho.exists():
        raise FileExistsError(f"{caminho}: a G-REVAL-POSSIVEL ja foi conferida")
    base = {k: v for k, v in _base(cfg).items() if k != "g_plano"}
    out = cpp.g_reval({**base, "consequencia": {k: v for k, v in base["consequencia"].items() if k != "ganho_gosto"}},
                      cfg["consequencia"]["ganho_gosto"])
    pasta.mkdir(parents=True, exist_ok=True)
    bv._gravar(caminho, bv._dump({**out, "meta": {**bv.meta(_base(cfg)), "plano": bv.PLANO_PQP,
                                                   "orquestrador_sha256": bv._sha(Path(__file__))}}))
    return out


def rodar_piloto(cfg: dict, pasta: Path, processos: int = 1) -> dict:
    validar(cfg)
    caminho = pasta / "reval.json"
    if not caminho.is_file():
        raise FileNotFoundError(f"{caminho}: a G-REVAL-POSSIVEL (o passo reval) ainda nao rodou")
    reval = json.loads(caminho.read_text(encoding="utf-8"))
    if reval["ganho_gosto"] != cfg["consequencia"]["ganho_gosto"]:
        raise RuntimeError(f"a G-REVAL-POSSIVEL foi conferida no ganho_gosto {reval['ganho_gosto']}, a config tem outro")
    if not reval["passa"]:
        raise RuntimeError(f"G-REVAL-POSSIVEL falha ({reval['falham']} de {reval['n']} unidades): o T1 e inconclusivo por desenho; o "
                           "piloto nao roda e o plano volta ao Matheus (A3.2)")
    escolha = {"g_plano": cfg["g_plano"], "fonte": "adendo 6 (PJ7-5: sem recalibrar)",
               **({"calibracao": cfg[chave(cfg)]["calibracao"]} if "calibracao" in cfg[chave(cfg)] else {})}
    return cpq.piloto(config_do_piloto(cfg), pasta / "piloto", processos, bv.LIMIAR_ACASO_MEDIO, escolha)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="piloto do adendo 7 do pet que pensa (PLANO_ANALISE_V2_PET_QUE_PENSA, A7.4)")
    ap.add_argument("--config", required=True)
    ap.add_argument("--saida", required=True)
    ap.add_argument("--passo", required=True, choices=PASSOS)
    ap.add_argument("--processos", type=int, default=1, help="os bracos do piloto em paralelo")
    a = ap.parse_args(argv)
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))
    if a.passo == "reval":
        r = rodar_reval(cfg, Path(a.saida))
        print(f"G-REVAL-POSSIVEL: {r['falham']} de {r['n']} unidades falham; {'passa' if r['passa'] else 'FALHA: o piloto nao roda'}")
    else:
        r = rodar_piloto(cfg, Path(a.saida), a.processos)
        mg, n = r["margens"], r["n"]
        print(f"piloto do adendo 7: Delta_T1 {mg['delta_t1']}, Delta_T2 {mg['delta_t2']}, K_u {None if n is None else n['k']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
