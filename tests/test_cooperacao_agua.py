"""O grupo de dois pets na ilha com agua (docs/TAREFA_V3_COOPERACAO.md, etapa CO4a): o controlador sozinho do contrato vale no grupo.

- o gabarito do TS (web/app/test/gabaritos/grupo_agua_python.json.gz) refeito byte a byte;
- o replay do registro do grupo na agua da o mesmo resumo;
- nenhum pet fica na agua, em decisao nenhuma, e a comida do dono fica em terra;
- no grupo, o cone e as paredes do contrato continuam recusados (so o controlador, a agua, entra)."""
from __future__ import annotations

import gzip
import json
import sys
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "experiments"))

import exportar_gabarito_grupo as eg  # noqa: E402
import exportar_gabarito_grupo_agua as ea  # noqa: E402

from digilab.config import CONFIG_CONTRATO_AGUA, CONFIG_PADRAO  # noqa: E402
from digilab.grupo import Grupo, RegistroGrupo, reproduzir_grupo  # noqa: E402
from digilab.instinto_mundo import PoliticaInstintoMundo  # noqa: E402
from digilab.mundo import MotorMundo  # noqa: E402


@pytest.fixture(scope="module")
def gabarito() -> dict:
    return ea.gerar()


def test_o_gabarito_do_ts_e_refeito_byte_a_byte(gabarito):
    gravado = json.loads(gzip.decompress(ea.ARQUIVO.read_bytes()).decode())
    assert gravado == json.loads(json.dumps(gabarito, sort_keys=True, separators=(",", ":")))
    assert gabarito["layout"] == "mvp_agua" and len(gabarito["vidas"]) == 3


def test_o_replay_do_grupo_na_agua():
    v = ea.VIDAS[1]
    g = ea.grupo(*v)
    fabricas = {i: ea._fabricas(v[1], v[2]["AB".index(i)]) for i in g.motores}
    r = reproduzir_grupo(RegistroGrupo.de_jsonl(g.registro.para_jsonl()), fabricas, ea.CM)
    assert eg._json(r.resumo()) == eg._json(g.resumo())


def test_nenhum_pet_na_agua_e_a_comida_em_terra(gabarito):
    secas = ea.grupo(*ea.VIDAS[0]).mundo
    decisoes = 0
    for v in gabarito["vidas"]:
        for i, p in v["resumo"]["pets"].items():
            for d in p["fisico"]["decisoes"]:
                assert secas.seca(d["x"], d["y"]), (v["semente"], i, d)
                decisoes += 1
            assert p["fisico"]["contrato_decisoes"], "o controlador andou no grupo"
        for c in v["resumo"]["mundo"]["comidas"]:
            assert secas.seca(c["x"], c["y"])
    assert decisoes == 6 * 288


def test_no_grupo_o_cone_e_as_paredes_seguem_recusados():
    for contrato in (replace(CONFIG_CONTRATO_AGUA, sensores=True), replace(CONFIG_CONTRATO_AGUA, paredes=True)):
        g = Grupo(ea.CM, 101)
        fm = lambda p, cfg, s, contrato=contrato, **kw: MotorMundo(p, cfg, s, obediencia_desligada=True, cfg_mundo=ea.CM,  # noqa: E731
                                                                   cfg_contrato=contrato, **kw)
        with pytest.raises(ValueError, match="so o controlador"):
            g.entrar("A", PoliticaInstintoMundo(CONFIG_PADRAO), fm, "instinto", "nenhum")
