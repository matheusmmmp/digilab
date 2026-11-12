"""Gabarito das vidas de hoje para o enjoo da imagem no cerebro do Python (GOSTO_VISUAL; docs/registro/2026-11.md, D-GV-ENJOO-PY-1 a 3 e
D-GV-ENJOO-CER-1...). Gravado com o codigo de antes do conserto, num commit proprio. Com a chave nova desligada (o padrao), estas vidas tem
de sair iguais depois, byte a byte (o G2 do conserto).

As familias que o conserto toca, alem das que ja tem gabarito proprio (as vidas do P1a em tests/gabaritos/gosto_visual_vidas_de_hoje.json,
conferidas pelo tests/test_gabarito_gosto_visual.py; as do exportador da web em web/app/test/gabaritos/gosto_visual.json.gz, conferidas
pelo tests/test_gabarito_gosto_visual_web.py):
  - a vida da GV3 (o modular com o olhar e a TV do jogo, `run_v3_gosto_visual.viver`): os dois genomas, os tres donos e as unidades das
    bases 101, 202 e 303 (k = 0), 3 dias, com a sonda das duas TVs no ultimo dia (2 replicas);
  - a imagem parada (a fonte "evento" com um `sentido_tela` so, o modular com o olhar e o agrado no corpo): as sementes 101, 202 e 303,
    2 dias.
De cada vida, o sha256 do log, do estado, do corpo, do mundo e do estado interno do cerebro (com os motivos); da sonda, o sha256 do dump.

    python tests/gabarito_gosto_visual_enjoo.py     # grava tests/gabaritos/gosto_visual_enjoo_vidas_de_hoje.json (so com o codigo de antes)
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import exportar_gosto_visual as X  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402
import run_v3_gosto_visual as R  # noqa: E402
import sonda_duas_tvs as sd  # noqa: E402

from digilab.config import CONFIG_PADRAO  # noqa: E402
from digilab.digibrain.adapt import DigiBrain  # noqa: E402
from digilab.events import AcaoUsuario  # noqa: E402
from digilab.motor_corpo import com_corpo  # noqa: E402
from digilab.mundo import MotorMundo, centro_da_celula  # noqa: E402
from digilab.temperamento import NEUTRO  # noqa: E402

ARQUIVO = RAIZ / "tests" / "gabaritos" / "gosto_visual_enjoo_vidas_de_hoje.json"
BASES = (101, 202, 303)
DIAS_GV3 = 3
REPLICAS = 2
SEMENTES_PARADA = (101, 202, 303)
DIAS_PARADA = 2
HORA = 60
IMAGEM = (12, 12, 12, 12, 4, 12, 12)              # os niveis do evento (0 a 15) da imagem parada; o volume baixo, abaixo do corte do estresse


def _h(x) -> str:
    return hashlib.sha256(json.dumps(x, sort_keys=True, default=str).encode("utf-8")).hexdigest()


def impressao(m) -> dict:
    c = sd.cerebro_da_copia(m)
    return {"log": hashlib.sha256(m.log.para_jsonl().encode("utf-8")).hexdigest(), "estado": _h(m.estado()),
            "corpo": _h(m.corpo.para_dict()), "mundo": _h(m.resumo_mundo_fisico()), "cerebro": _h(c.estado_interno()),
            "decisoes": len(c.motivos), "olhares": sum(1 for x in c.motivos if x["olhar"]["olha"] is not None)}


def viver_parada(semente: int, dias: int = DIAS_PARADA, niveis=IMAGEM, **kw_cerebro):
    """a imagem parada: o modular da vida do exportador (o laboratorio com o olhar e o agrado no corpo), a TV do modo livre com um
    `sentido_tela` so no tick 0, o dono que poe comida a cada 3 horas e acaricia a cada 5. `kw_cerebro` vai ao DigiBrain"""
    cerebro = DigiBrain(CONFIG_PADRAO, X.config_vida(), orq.CM, semente=semente, cfg_olhar=X.config_olhar("evento"), **kw_cerebro)
    m = com_corpo(MotorMundo)(cerebro, CONFIG_PADRAO, semente, NEUTRO, "brasa", obediencia_desligada=True, cfg_mundo=orq.CM,
                              cfg_corpo=X._cc(), cfg_tela=X.TELA, cfg_tv=X.config_tv("evento"))
    m.sentido_tela("tv", niveis)
    x, y = centro_da_celula(orq.CM.layout.comedouro, orq.CM)
    for h in range(dias * 24):
        m.avancar(HORA)
        if h % 3 == 0:
            m.deixar_comida("racao", x, y)
        if h % 5 == 2 and not m.estado()["dormindo"]:
            m.observar(AcaoUsuario.ACARICIAR)
    return m


def casos():
    for b in BASES:
        for g in R.GENOMAS:
            for d in R.DONOS:
                yield f"gv3|{g}|{d}|{b}", ("gv3", g, d, b)
    for s in SEMENTES_PARADA:
        yield f"parada|{s}", ("parada", None, None, s)


def vida_de_hoje(familia: str, genoma: str | None, dono: str | None, semente: int) -> dict:
    if familia == "gv3":
        u = R.unidades([semente], 1)[0]
        m, fab, _ = R.viver(genoma, dono, u, DIAS_GV3)
        s = sd.sonda(m, fab, u["semente"], (DIAS_GV3 - 1,), REPLICAS)
        return {**impressao(m), "sonda": _h(s)}
    if familia == "parada":
        return impressao(viver_parada(semente))
    raise ValueError(f"familia desconhecida: {familia!r}")


def gerar() -> dict:
    return {chave: vida_de_hoje(*caso) for chave, caso in casos()}


if __name__ == "__main__":
    g = gerar()
    ARQUIVO.write_text(json.dumps(g, sort_keys=True, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"{ARQUIVO}: {len(g)} vidas")
