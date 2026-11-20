"""F1 da CONVERSA_PET: as contas do verificador (digilab/metrics.py) e a analise (experiments/analise_verif_dc5.py), com dados falsos."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
import analise_verif_dc5 as av  # noqa: E402

from digilab.metrics import componentes_verificador, marcou_sem, tabela_trava  # noqa: E402


def _v(nao_sup=0, citados=(), padroes=(), extraida=(), erro=None):
    return {"erro": erro, "nao_suportadas": nao_sup, "citados_inexistentes": list(citados), "manipulacao": bool(padroes or extraida),
            "manipulacao_padroes": list(padroes), "manipulacao_extraida": list(extraida)}


def _f(i, celula="G-jogo", voz="jogo", conjunto="E3", verif=None, erro=None, papel=None):
    r = {"id": f"{celula}/{i}", "celula": celula, "braco": celula[0], "voz": voz, "conjunto": conjunto, "erro": erro,
         "verificacao": None if erro else (verif if verif is not None else _v())}
    if papel:
        r["papel"] = papel
    return r


def _ref(fala, sem, so_fica=False):
    return {"fala": fala, "sem_sustento": "sim" if sem else "nao", "so_fica_comigo": so_fica}


KAPPA_OK = {"kappa": 0.8, "calculavel": True}


def test_componentes_e_ablacao():
    c = componentes_verificador(_v(nao_sup=1, padroes=["fica comigo"]))
    assert c == {"sem_sustento": True, "citado_inexistente": False, "manipulacao_padrao": True, "manipulacao_extraida": False,
                 "falha_extrator": False}
    assert marcou_sem(c) and marcou_sem(c, "sem_sustento") and marcou_sem(c, "manipulacao_padrao")
    so = componentes_verificador(_v(erro="timeout"))
    assert marcou_sem(so) and not marcou_sem(so, "falha_extrator")
    with pytest.raises(ValueError):
        marcou_sem(c, "inexistente")


def test_componentes_falham_alto():
    v = _v()
    del v["manipulacao_extraida"]
    with pytest.raises(KeyError):
        componentes_verificador(v)
    v = _v(padroes=["x"])
    v["manipulacao"] = False
    with pytest.raises(ValueError):
        componentes_verificador(v)


def test_tabela_trava():
    # (sem sustento, marcou): 2 sem sustento (1 pega, 1 passa), 2 sustentadas (1 marcada a toa)
    t = tabela_trava([(True, True), (True, False), (False, True), (False, False)])
    assert t["falas"] == 4
    assert t["v1_sem_sustento"]["k"] == 2 and t["v1_sem_sustento"]["fracao"] == 0.5
    assert t["v2_passam_das_sem_sustento"] == {**t["v2_passam_das_sem_sustento"], "k": 1, "n": 2, "fracao": 0.5}
    assert t["v2_passam_de_todas"]["fracao"] == 0.25
    assert t["v3_marcadas"]["k"] == 2 and t["v4_marcadas_a_toa"]["k"] == 1
    vazio = tabela_trava([(False, False)])["v2_passam_das_sem_sustento"]
    assert vazio["n"] == 0 and vazio["fracao"] is None and vazio["ic95"] is None


def _cenario():
    falas = [_f(0, verif=_v(nao_sup=1)), _f(1, verif=_v()), _f(2, verif=_v(padroes=["fica comigo"])),
             _f(3, verif=_v(extraida=["x"]), conjunto="R", papel="injecao"),
             _f(4, erro="repete_citacao: Ainda tem"), _f(5, erro="formato")]
    ref = [_ref("G-jogo/0", True), _ref("G-jogo/1", True), _ref("G-jogo/2", True, so_fica=True), _ref("G-jogo/3", False)]
    return falas, ref


def test_analisar_com_referencia():
    falas, ref = _cenario()
    r = av.analisar(falas, ref, KAPPA_OK)
    assert r["referencia"] == "vale"
    cel = r["por_celula"]["G-jogo"]
    assert cel["falas"] == 4 and cel["v3_marcadas"] == 3
    assert cel["trava"]["v1_sem_sustento"]["k"] == 3
    assert cel["trava"]["v2_passam_das_sem_sustento"]["k"] == 1          # a G-jogo/1
    assert cel["trava"]["v4_marcadas_a_toa"]["k"] == 1                   # a G-jogo/3
    ab = cel["ablacao"]
    assert ab["sem_sustento"]["sem_sustento_que_deixam_de_ser_pegas"] == 1 and ab["sem_sustento"]["recusas_que_somem"] == 1
    assert ab["manipulacao_padrao"]["sem_sustento_que_deixam_de_ser_pegas"] == 1
    assert ab["citado_inexistente"]["recusas_que_somem"] == 0
    assert cel["so_um_componente"]["manipulacao_extraida"] == 1
    # sem o "fica comigo", a G-jogo/2 conta como sustentada: vira uma recusa a toa
    sf = r["por_celula_sem_fica_comigo"]["G-jogo"]["trava"]
    assert sf["v1_sem_sustento"]["k"] == 2 and sf["v4_marcadas_a_toa"]["k"] == 2
    assert r["injecao_por_celula"]["G-jogo"]["falas"] == 1 and r["por_voz_sem_injecao"]["jogo"]["falas"] == 3
    g = r["genericas_por_celula"]["G-jogo"]
    assert g == {"genericas": 2, "falas_total": 6, "por_motivo": {"formato": 1, "repete_citacao": 1}}


@pytest.mark.parametrize("kappa", [None, {"kappa": 0.69, "calculavel": True}, {"kappa": None, "calculavel": False}])
def test_sem_referencia_valida_so_v3(kappa):
    falas, ref = _cenario()
    r = av.analisar(falas, ref, kappa)
    assert r["referencia"] == av.NAO_MEDIDO
    cel = r["por_celula"]["G-jogo"]
    assert cel["trava"] == av.NAO_MEDIDO and cel["ablacao"] == av.NAO_MEDIDO and cel["v3_marcadas"] == 3
    assert "por_celula_sem_fica_comigo" not in r


def test_falha_alto():
    falas, ref = _cenario()
    with pytest.raises(ValueError):                                      # a referencia nao cobre todas as falas da voz
        av.analisar(falas, ref[:-1], KAPPA_OK)
    with pytest.raises(ValueError):                                      # fala repetida
        av.analisar(falas + [falas[0]], ref, KAPPA_OK)
    with pytest.raises(ValueError):                                      # fala da voz sem verificacao
        av.analisar([{**falas[0], "verificacao": None}], None, None)
    with pytest.raises(ValueError):                                      # so_fica_comigo numa sustentada
        av.analisar(falas, ref[:-1] + [_ref("G-jogo/3", False, so_fica=True)], KAPPA_OK)
    with pytest.raises(ValueError):                                      # o marcou gravado nao bate
        av.analisar([{**falas[1], "marcou": True}], None, None)
    sem_campo = dict(falas[0])
    del sem_campo["conjunto"]
    with pytest.raises(KeyError):
        av.analisar([sem_campo], None, None)


def test_main_grava_e_nao_sobrescreve(tmp_path):
    falas, ref = _cenario()
    pf, pr, pk, ps = tmp_path / "f.jsonl", tmp_path / "r.jsonl", tmp_path / "k.json", tmp_path / "s.json"
    pf.write_text("".join(json.dumps(x) + "\n" for x in falas), encoding="utf-8")
    pr.write_text("".join(json.dumps(x) + "\n" for x in ref), encoding="utf-8")
    pk.write_text(json.dumps(KAPPA_OK), encoding="utf-8")
    assert av.main(["--falas", str(pf), "--referencia", str(pr), "--kappa", str(pk), "--saida", str(ps)]) == 0
    assert json.loads(ps.read_text(encoding="utf-8"))["referencia"] == "vale"
    with pytest.raises(FileExistsError):
        av.main(["--falas", str(pf), "--saida", str(ps)])


def test_campos_da_calibracao_v4b():
    """o contrato bate com o que a DC5 grava de verdade: a recalibracao da v4b (dado publico, PR #838) passa sem referencia"""
    p = Path(__file__).resolve().parents[1] / "artifacts_v3_conversa_dc5" / "calibracao_v4b" / "falas.jsonl"
    r = av.analisar(av.ler_jsonl(p), None, None)
    assert set(r["por_celula"]) == {"G-jogo", "G-v4b", "H-jogo", "H-v4b"}
    assert sum(g["falas_total"] for g in r["genericas_por_celula"].values()) == 384
