"""Gabarito da CO6 (docs/ESPEC_V3_COOPERACAO_CO6.md, missao CO6a; a CO6-6): as vidas do `Grupo` de hoje com a cooperacao ligada e a
CO6 desligada, com as decisoes e os `estado_interno()` de cada cerebro. Gravado com o codigo da `main` ANTES da CO6b, num commit proprio:
e o par fixo do G2 (desligada, as vidas saem byte a byte) e da prova do G-SEM-DECISAO-CO6 (ligada, as decisoes e o log sao os mesmos).

O cerebro e o DigiBrain modular nos dois pets (o do jogo; a CB-2 do plano da bancada pede o modular no `Grupo` do Python, se houver), na
ConfigDigibrain do laboratorio (o braco REL da C4, o do exportar_gabarito_digibrain_modular), no mundo do produto (CONFIG_MUNDO_MVP) e com
o corpo da bancada (o v11). As vidas (semente do grupo, dono de A e de B, entrada de B em dias, lugar da comida do dono):
  101  atencioso  atencioso  0  comedouro   os dois no comedouro comum (as contencoes e as disputas)
  202  atencioso  relapso    0  perto       donos diferentes no cuidado
  303  atencioso  atencioso  1  comedouro   o segundo pet entra no dia 1 (o relogio de cada pet)

De cada vida: o registro do grupo, as acoes de cada decisao de cada pet (a acao e a escolha do motivo), o sha256 do `estado_interno()` de
cada cerebro no fim, o do log de cada pet e o do resumo do grupo, e o resumo da cooperacao (os atos, a pontuacao e a reputacao).

    python experiments/exportar_gabarito_co6.py              # grava tests/gabaritos/co6_vidas_de_hoje.json.gz
    python experiments/exportar_gabarito_co6.py --conferir   # refaz e compara com o gravado (falha alto se diferir)
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import run_v2_digibrain_prototipo as orq  # noqa: E402

from digilab.config import CONFIG_COOPERACAO_LIGADA, CONFIG_GRUPO_LIGADA, CONFIG_PADRAO, TICKS_POR_DIA  # noqa: E402
from digilab.digibrain.adapt import DigiBrain  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.grupo import PetDoGrupo, sementes_do_grupo, simular_grupo  # noqa: E402
from digilab.motor_corpo import com_corpo  # noqa: E402
from digilab.mundo import DonoComLugar, MotorMundo  # noqa: E402
from digilab.temperamento import NEUTRO  # noqa: E402

ARQUIVO = RAIZ / "tests" / "gabaritos" / "co6_vidas_de_hoje.json.gz"
DIAS = 3
BRACO = "REL"                                     # a ConfigDigibrain do laboratorio (exportar_gabarito_digibrain_modular.BRACO)
CM = orq.CM
VIDAS = ((101, ("atencioso", "atencioso"), 0, "comedouro"),
         (202, ("atencioso", "relapso"), 0, "perto"),
         (303, ("atencioso", "atencioso"), 1, "comedouro"))


def _sha(texto: str) -> str:
    return hashlib.sha256(texto.encode()).hexdigest()


def _json(obj) -> str:
    return json.dumps(obj, sort_keys=True, default=repr)


def fabricas(dono: str, semente_pet: int):
    """(a fabrica do cerebro, a do motor) de um pet do grupo: o modular do laboratorio e o motor com o corpo e o mundo do grupo"""
    cd = orq.config_do_braco(BRACO, conserto=True)
    cc = orq.bancada(DIAS, orq.ORCAMENTO_POR_DIA).cfg_corpo_de(orq.bv.EspecVida(dono, orq.gl.BRACO_V11, semente_pet))

    def fp(cfg=None):
        return DigiBrain(cfg or CONFIG_PADRAO, cd, CM, semente=semente_pet)

    def fm(politica, cfg, s, **kw):
        return com_corpo(MotorMundo)(politica, cfg, s, NEUTRO, "brasa", obediencia_desligada=True, cfg_mundo=CM, cfg_corpo=cc, **kw)
    return fp, fm


def grupo(semente: int, donos: tuple, entrada_b: int, lugar: str, cfg_cooperacao=CONFIG_COOPERACAO_LIGADA):
    """a vida do grupo (as duas fabricas e os donos de hoje); `cfg_cooperacao`, a da vida (a CO6 a liga nos testes da CO6b)"""
    sementes = sementes_do_grupo(semente, CONFIG_GRUPO_LIGADA.ids)
    pets = []
    for ident, dono, entrada in (("A", donos[0], 0), ("B", donos[1], entrada_b * TICKS_POR_DIA)):
        fp, fm = fabricas(dono, sementes[ident])
        d = DonoComLugar(criar_dono(dono), lugar, sementes[ident], dono, CM)
        pets.append(PetDoGrupo(ident, entrada, fp, fm, d, dono, "digibrain"))
    return simular_grupo(CM, semente, pets, DIAS, cfg_cooperacao=cfg_cooperacao)


def decisoes(cerebro) -> list:
    """a acao e a escolha de cada decisao (o motivo do M-ADAPT)"""
    return [[m["acao"], m["escolha"]] for m in cerebro.motivos]


def vida(v: tuple, cfg_cooperacao=CONFIG_COOPERACAO_LIGADA) -> dict:
    semente, donos, entrada_b, lugar = v
    g = grupo(semente, donos, entrada_b, lugar, cfg_cooperacao)
    r = g.resumo()
    pets = {}
    for i, m in sorted(g.motores.items()):
        pets[i] = {"decisoes": json.loads(_json(decisoes(m.politica))),
                   "estado_interno_sha256": _sha(_json(m.politica.estado_interno())),
                   "log_sha256": _sha(m.log.para_jsonl())}
    return {"semente": semente, "donos": list(donos), "entrada_b_dias": entrada_b, "lugar": lugar, "tick": g.tick,
            "registro": {"cabecalho": g.registro.cabecalho, "eventos": [e.para_dict() for e in g.registro.eventos]},
            "pets": pets, "resumo_sha256": _sha(_json(json.loads(_json(r)))),
            "cooperacao": json.loads(_json(r["cooperacao"]))}


def gerar() -> dict:
    return {"fonte": "experiments/exportar_gabarito_co6.py", "braco": BRACO, "dias": DIAS, "vidas": [vida(v) for v in VIDAS]}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--conferir", action="store_true", help="refaz e compara com o gabarito gravado")
    args = ap.parse_args()
    g = gerar()
    texto = json.dumps(g, sort_keys=True, separators=(",", ":"))
    if args.conferir:
        gravado = json.loads(gzip.decompress(ARQUIVO.read_bytes()).decode())
        if gravado != json.loads(texto):
            raise SystemExit(f"o gabarito da CO6 mudou: {ARQUIVO}")
        print(f"igual ao gravado: {ARQUIVO}")
        return
    ARQUIVO.write_bytes(gzip.compress(texto.encode(), mtime=0))
    for v in g["vidas"]:
        atos = v["cooperacao"]["atos"]
        por = {a: sum(1 for x in atos if x["ato"] == a) for a in ("disputa", "contencao", "encostar")}
        print(f"vida {v['semente']}: decisoes {[len(p['decisoes']) for p in v['pets'].values()]}, atos {por}, "
              f"reputacao {v['cooperacao']['reputacao']}")
    print(f"gravado: {ARQUIVO} ({ARQUIVO.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
