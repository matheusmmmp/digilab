"""O script da auditoria da PET_VIVO (docs/PLANO_ANALISE_V3_PET_VIVO.md, secao 9), nas sementes dos testes: a vida da AN0 refeita com e
sem o contrafactual sai igual ao gabarito (o G1 com o contrafactual ligado), P soma 1, duas execucoes saem iguais byte a byte, e o script
falha alto com o codigo ou a fonte errados. A C4 nao roda aqui: ela pede a worktree do a287ba2 e a pasta da run."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "experiments"))

import auditoria_pet_vivo as aud  # noqa: E402

_CACHE: dict = {}


def _vida(cf: bool) -> dict:
    """a primeira vida da AN0 (o atencioso no longe_fixo, semente 101, 4 dias), refeita uma vez por modo"""
    if cf not in _CACHE:
        gab = aud.gabaritos()
        x = aud.vidas_an0()[0]
        _CACHE[cf] = aud.rejogar_an0((*x, cf, gab["vidas"][(x[0], x[1], x[2], x[3])]))
    return _CACHE[cf]


def _sem_tempo(v: dict) -> dict:
    return {k: x for k, x in v.items() if k != "parede_s"}


def test_as_contas_vem_do_metrics_desta_arvore():
    met = aud.metricas()
    assert Path(met.__file__).resolve() == (RAIZ / "digilab" / "metrics.py").resolve()
    assert hasattr(met, "distancia_tv") and hasattr(met, "se_c")


def test_as_vidas_da_an0_sao_as_dos_gabaritos_com_os_inatos_de_hoje():
    vidas = aud.vidas_an0()
    assert len(vidas) == 10
    assert all(aj == {} for *_, aj in vidas)
    gab = aud.gabaritos()
    assert all((x[0], x[1], x[2], x[3]) in gab["vidas"] for x in vidas)


def test_o_g1_vale_com_e_sem_o_contrafactual():
    sem, com = _vida(False), _vida(True)              # cada uma ja conferiu o log, o estado e os motivos contra o gabarito
    assert "A4" not in sem and "A4" in com
    fora = ("parede_s", "contrafactual", "A4", "RV")
    assert {k: v for k, v in sem.items() if k not in fora} == {k: v for k, v in com.items() if k not in fora}


def test_p_soma_um_em_toda_decisao_elegivel():
    v = _vida(True)
    for chave in ("soma_p", "soma_p1", "soma_pmu", "soma_pa"):
        assert sum(v["A2"][chave].values()) == pytest.approx(v["elegiveis"], abs=1e-6)
    assert v["A3"]["reflexos"] + v["elegiveis"] == v["decisoes"]


def test_o_contrafactual_cobre_cada_receptor_e_cada_variante():
    v = _vida(True)
    from digilab.config import RECEPTORES_DIGIBRAIN
    assert set(v["A4"]) <= set(RECEPTORES_DIGIBRAIN) and len(v["A4"]) >= 10
    for r, d in v["A4"].items():
        assert set(d) == set(aud.VARIANTES)
        for s in d.values():
            assert s["n"] == v["decisoes"]
            assert 0.0 <= s["S"] <= 1.0


def test_duas_execucoes_saem_iguais_byte_a_byte():
    gab = aud.gabaritos()
    x = aud.vidas_an0()[0]
    outra = aud.rejogar_an0((*x, True, gab["vidas"][(x[0], x[1], x[2], x[3])]))
    assert json.dumps(_sem_tempo(outra), sort_keys=True) == json.dumps(_sem_tempo(_vida(True)), sort_keys=True)


def test_a_leitura_de_um_grupo_sai_e_tem_a_linha():
    met = aud.metricas()
    g = aud.ler_grupo(met, [_vida(True)])
    assert set(g) >= {"HA", "HC", "HP", "A_r", "SE_C", "RV", "alivio"}
    assert aud.linha_da_leitura(g)["linha"].startswith(("indeterminado", "aponta para", "mistura"))


def test_a_linha_da_leitura_segue_a_regra():
    assert aud.linha_da_leitura({"HA": {"aponta": False}, "HC": {"aponta": False}, "HP": {"aponta": False}})["linha"] == "indeterminado"
    assert aud.linha_da_leitura({"HA": {"aponta": True}, "HC": {"aponta": False}, "HP": {"aponta": False}})["linha"] == "aponta para HA"
    assert aud.linha_da_leitura({"HA": {"aponta": True}, "HC": {"aponta": False}, "HP": {"aponta": True}})["linha"] == "mistura: HA + HP"
    assert aud.linha_da_leitura({"HA": {"aponta": False}, "reflexo_acima_de_um_terco": True})["aviso_reflexo"] is not None


def test_falha_alto_com_a_fonte_ou_o_codigo_errados(tmp_path):
    for nome in aud.SHA_C4:
        (tmp_path / nome).write_bytes(b"outro")
    with pytest.raises(RuntimeError, match="nao e o da C4"):
        aud.ler_fontes_c4(tmp_path)
    import descritivo_dc13_rel as drel
    meta = json.loads((aud.PASTA_C4_GIT / "meta.json").read_text(encoding="utf-8"))
    with pytest.raises(RuntimeError, match="nao e o da run"):
        drel.conferir_codigo(tmp_path, meta)


def test_a_auditoria_roda_uma_vez_e_com_ate_quatro_processos(tmp_path):
    (tmp_path / "auditoria.json").write_text("{}", encoding="utf-8")
    with pytest.raises(FileExistsError):
        aud.principal(tmp_path, tmp_path, 1, saida=tmp_path)
    with pytest.raises(SystemExit):
        aud.principal(tmp_path, tmp_path, 5, saida=tmp_path / "nova")
