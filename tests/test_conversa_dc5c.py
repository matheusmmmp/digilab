"""O adendo da DC5c (docs/PLANO_ANALISE_V3_CONVERSA_DC5.md, secao 15): a config da validacao e o registro da rodada. Nenhuma chamada a modelo."""
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
import run_v3_conversa_dc5 as dc5  # noqa: E402

CFG = json.loads((RAIZ / dc5.CONFIGS["validacao"]).read_text(encoding="utf-8"))


def test_a_validacao_e_o_desenho_do_adendo():
    dc5.conferir_config(CFG)
    assert CFG["fase"] == "validacao" and CFG["unidades"]["bases"] == [20263200]
    assert dc5.celulas_da_config(CFG) == (("G", "jogo"), ("G", "v4b"), ("H", "jogo"), ("H", "v4b"))
    assert CFG["especie"] is True and CFG["verificador_dc5"] is True and CFG["teto_usd"] == 3.0
    assert "estimativa_maxima_usd" not in CFG


def test_o_piso_soma_as_calibracoes():
    assert dc5.metas_do_piso(CFG) == ["artifacts_v3_conversa_dc4/validacao/meta.json", "artifacts_v3_conversa_dc5/calibracao/meta.json",
                                      "artifacts_v3_conversa_dc5/calibracao_v4b/meta.json"]
    piso = dc5.piso_do_gasto(CFG)
    assert piso + dc5.exigir_estimativa(CFG, piso) <= CFG["teto_usd"]


def test_o_plano_tem_o_adendo_e_o_registro_de_hoje():
    plano = dc5._plano()
    dc5.exigir_plano_aprovado(plano)
    assert "\n## 15. O adendo da DC5c" in plano
    # o registro de hoje e conferido pelo orquestrador antes da validacao, nao aqui: digilab/config.py e outros arquivos dele mudam em
    # outras frentes, e o teste quebraria fora da DC5
    assert set(dc5.registro_do_plano(plano)) == set(dc5.arquivos_do_registro())
