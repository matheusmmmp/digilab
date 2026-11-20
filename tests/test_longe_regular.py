"""O orquestrador da C1 (experiments/run_v2_longe_regular.py; o adendo 6 do plano, A6.2, A6.3, A6.4, A6.6, A6.7, A6.8 e A6.10): a config e a
trava (o adendo 6 APROVADO, a faixa 71101...71505, as bases, o K, os dias, no maximo 4 processos, nada por cima de uma pasta existente),
a classe de cada contraste, a leitura de A6.7, o motor que grava o corpo (sem mudar a vida), a conferencia da LP-2 e a fumaca de ponta a
ponta. Vidas so com as sementes dos testes (101...505): nenhuma da faixa 71xxx roda aqui."""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402
import run_v2_longe_regular as lr  # noqa: E402
from bancada.faixas import na_faixa_reservada  # noqa: E402

CONFIGS = RAIZ / "experiments" / "configs" / "v2_longe_regular"


def _cfg(nome: str = "longe_regular") -> dict:
    return json.loads((CONFIGS / f"{nome}.json").read_text(encoding="utf-8"))


# ------------------------------------------------------------------ o que o adendo fixa
def test_o_desenho_e_o_do_adendo_6():
    assert lr.BASES == (71101, 71202, 71303, 71404, 71505) and lr.K_POR_BASE == 30 and lr.DIAS == 14 and lr.ORCAMENTO_POR_DIA == 16
    assert lr.ESTILOS == ("longe_fixo", "longe") and len(lr.CELULAS) == 8 and lr.BRACOS == ("M0", "M2", "M3")
    assert lr.PREFIXO == "digibrain_prototipo" and lr.MARGEM == 0.022 and lr.MAX_PROCESSOS == 4
    us = bv.unidades_derivadas(lr.BASES, lr.K_POR_BASE, lr.PREFIXO)
    assert len(us) == 150 and len(us) * len(lr.BRACOS) * len(lr.CELULAS) == 3600


def test_os_bracos_sao_os_do_conserto_sem_a_intencao_suspensa():
    for b in lr.BRACOS:
        assert not orq.config_do_braco(b, conserto=True).intencao_suspensa
        assert orq.SUBCHAVES_CONSERTO[b].get("cheiro_inato") and orq.SUBCHAVES_CONSERTO[b].get("intencao_cheiro")
    assert orq.config_do_braco("M3", conserto=True).m_mem and not orq.config_do_braco("M2", conserto=True).m_mem


def test_a_faixa_esta_reservada_e_o_limiar_da_c5_e_o_da_privacao():
    assert na_faixa_reservada(71101) and na_faixa_reservada(71505) and not na_faixa_reservada(71506)
    lr.exigir_faixa_reservada()
    assert lr.LIMIAR_CORPO == orq.LIMIAR_PRIVACAO == 0.15


# ------------------------------------------------------------------ a config e a trava
def test_as_configs_seguem_o_adendo():
    assert lr.modo_da_config(_cfg()) == "longe_regular"
    assert lr.modo_da_config(_cfg("fumaca")) == "fumaca"


@pytest.mark.parametrize("bases", [[71101, 71202, 71303, 71404], [71101, 71202, 71303, 71404, 71506], [71505, 71404, 71303, 71202, 71101],
                                   [66101, 66202, 66303, 66404, 66505], [67303, 67404, 67505], [101, 71101], [101, 71202, 71303, 71404, 71505]])
def test_recusa_outra_base_e_sementes_fora_da_faixa(bases):
    c = _cfg()
    c["unidades"]["bases"] = bases
    with pytest.raises(bv.SementeSemPlano):
        lr.modo_da_config(c)


def test_recusa_outro_k_outros_dias_outro_orcamento_e_outro_plano():
    for chave, valor in (("k", 29), ("k", 100), ("dias", 13), ("dias", 15), ("orcamento_por_dia", 15), ("plano", "outro.md")):
        c = _cfg()
        if chave == "k":
            c["unidades"]["k"] = valor
        else:
            c[chave] = valor
        with pytest.raises(ValueError):
            lr.modo_da_config(c)
    c = _cfg()
    c["unidades"]["prefixo"] = "outro"
    with pytest.raises(ValueError, match="prefixo"):
        lr.modo_da_config(c)


def test_recusa_chave_a_mais_fase_errada_e_fumaca_com_dias_demais():
    with pytest.raises(ValueError, match="sobram"):
        lr.modo_da_config({**_cfg(), "inatos": {}})
    with pytest.raises(ValueError, match="fase"):
        lr.modo_da_config({**_cfg(), "fase": "l2_piloto"})
    c = _cfg("fumaca")
    c["dias"] = 15
    with pytest.raises(ValueError, match="fumaca"):
        lr.modo_da_config(c)


def test_a_trava_exige_o_adendo_6_aprovado(monkeypatch):
    plano = lr._plano()
    marca = "**Status: APROVADO pelo Matheus em 2026-10-30,** com as AD6-1"
    assert marca in plano
    monkeypatch.setattr(lr, "_plano", lambda: plano.replace(marca, "**Status: PROPOSTO,** com as AD6-1"))
    with pytest.raises(RuntimeError, match="nao esta APROVADO"):
        lr.modo_da_config(_cfg())
    lr.modo_da_config(_cfg("fumaca"))                    # a fumaca nao precisa do adendo


def test_a_trava_exige_a_faixa_reservada(monkeypatch):
    monkeypatch.setattr(lr, "FAIXAS_RESERVADAS", tuple(f for f in lr.FAIXAS_RESERVADAS if f[0] != 71101))
    with pytest.raises(bv.SementeSemPlano, match="FAIXAS_RESERVADAS"):
        lr.modo_da_config(_cfg())


def test_recusa_mais_de_4_processos_e_pasta_existente(tmp_path):
    with pytest.raises(ValueError, match="4 processos"):
        lr.rodar(_cfg("fumaca"), tmp_path / "x", 5)
    with pytest.raises(FileExistsError):
        lr.rodar(_cfg("fumaca"), tmp_path, 1)


# ------------------------------------------------------------------ a classe e a leitura (A6.6 e A6.7)
def _ic(lo, hi):
    return {"ic_inferior": lo, "ic_superior": hi, "motivo": None}


@pytest.mark.parametrize("lo,hi,esperada,sinal", [(-0.01, 0.01, "≈ 0", None), (0.001, 0.02, "≈ 0", "+"), (-0.02, -0.001, "≈ 0", "-"),
                                                  (0.01, 0.05, "> 0", None), (-0.051, -0.012, "< 0", None), (-0.03, 0.03, "indeterminado", None),
                                                  (-0.022, 0.01, "indeterminado", None)])
def test_a_classe_de_a6_6(lo, hi, esperada, sinal):
    c = lr.classe(_ic(lo, hi))
    assert c["classe"] == esperada and c["sinal"] == sinal


def test_a_classe_sem_ic_e_indeterminada():
    assert lr.classe({"ic_inferior": None, "ic_superior": None, "motivo": "menos de 2 valores"})["classe"] == "indeterminado"


def _prim(passa: bool, classe: str) -> dict:
    return {"passa": passa, "classe": {"classe": classe}, "ressalva_assimetria": None}


@pytest.mark.parametrize("passa,cl_fixo,sort,l3", [(True, "> 0", "≈ 0", True), (True, "> 0", "< 0", False), (True, "> 0", "> 0", False),
                                                  (False, "≈ 0", "≈ 0", False), (False, "≈ 0", "< 0", False), (False, "< 0", "≈ 0", False),
                                                  (False, "indeterminado", "≈ 0", False), (True, "> 0", "indeterminado", False)])
def test_a_leitura_de_a6_7_so_da_tarefa_a_l3_com_fixo_maior_que_0_e_sorteado_perto_de_0(passa, cl_fixo, sort, l3):
    r = lr.leitura(_prim(passa, cl_fixo), {"conclusivo": True}, {"classe": {"classe": sort}})
    assert r["l3_ganha_tarefa"] is l3


def test_sem_premissa_a_leitura_e_inconclusiva():
    r = lr.leitura(_prim(True, "> 0"), {"conclusivo": False}, {"classe": {"classe": "≈ 0"}})
    assert r["l3_ganha_tarefa"] is False and "inconclusivo por premissa" in r["linha"]


def test_a_margem_efetiva_e_a_formula_de_a6_5():
    # A6.5: delta = (t_0,975;149 + z_0,8) x sigma / raiz(150); com o sigma de planejamento 0,0966 da 0,022
    assert lr.margem_efetiva(0.0966, 150) == pytest.approx(0.022, abs=5e-4)
    assert lr.margem_efetiva(None, 150) is None


# ------------------------------------------------------------------ o motor que grava o corpo e a conferencia da LP-2
def test_gravar_o_corpo_nao_muda_a_vida():
    """o MotorGravaCorpo e o motor de hoje com um registro a mais: o log da vida de 1 dia sai igual ao do motor sem a gravacao"""
    sem, _, _ = orq.viver("M2", "atencioso", "longe_fixo", 101, 1, 16, conserto=True)
    com, registro, _ = lr.viver("M2", "atencioso", "longe_fixo", 101, 1, 16)
    assert com.log.para_jsonl() == sem.log.para_jsonl()
    assert len(com.serie_corpo) == 1440 and lr.medidas_do_corpo(com, registro, 1)["vida"]["n_ticks"] == 1440


def test_a_serie_do_corpo_e_conferida_contra_o_que_o_cerebro_viu():
    com, registro, _ = lr.viver("M0", "relapso", "longe", 202, 1, 16)
    registro.estados[3] = (0.123,) + tuple(registro.estados[3][1:])
    with pytest.raises(RuntimeError, match="nao e o que o cerebro viu"):
        lr.medidas_do_corpo(com, registro, 1)


def _registro_falso(motivos: list, suspensa: bool = False):
    cerebro = SimpleNamespace(cd=SimpleNamespace(intencao_suspensa=suspensa), motivos=motivos)
    return SimpleNamespace(_interna=cerebro)


def _m(fins=(), reflexo=False, acao="comer", escolha=("comer", "cheiro", None), **extra):
    return {"fins": list(fins), "reflexo": reflexo, "acao": acao, "escolha": list(escolha), **extra}


def test_as_trocas_de_meta_contam_o_motivo():
    ms = [_m([{"chave": ["comer", "cheiro", None], "motivo": "trocou"}], reflexo=True, acao="dormir"),
          _m([{"chave": ["comer", "comida", 3], "motivo": "trocou"}], acao="dormir", escolha=("dormir", None, None)),
          _m([{"chave": ["explorar", "ponto", [1, 2]], "motivo": "trocou"}], acao="explorar", escolha=("explorar", "cheiro", None)),
          _m([{"chave": ["comer", "cheiro", None], "motivo": "achou"}, {"chave": ["brincar", None, None], "motivo": "trocou"}])]
    r = lr.trocas_de_meta(_registro_falso(ms))
    assert r["trocas"]["busca"] == {"reflexo": 1, "dormir_sorteio": 0, "outra_unidade": 0, "por_vencedora": {}}
    assert r["trocas"]["ida"]["dormir_sorteio"] == 1
    assert r["trocas"]["lugar_lembrado"]["outra_unidade"] == 1 and r["trocas"]["lugar_lembrado"]["por_vencedora"] == {"explorar/cheiro": 1}
    assert r["fins"]["busca"]["achou"] == 1 and r["trocas_total"] == 3                  # o "brincar" nao e meta de comer/explorar


def test_o_fim_desistiu_da_busca_e_contado_a_parte_e_nao_e_troca():
    ms = [_m([{"chave": ["comer", "cheiro", None], "motivo": "desistiu"}]),
          _m([{"chave": ["comer", "comida", 3], "motivo": "desistiu"}, {"chave": ["comer", "cheiro", None], "motivo": "desistiu"}])]
    r = lr.trocas_de_meta(_registro_falso(ms))
    assert r["fins"]["busca"]["desistiu"] == 2 and r["fins"]["ida"]["desistiu"] == 1
    assert r["trocas_total"] == 0 and r["trocas"]["busca"] == {"reflexo": 0, "dormir_sorteio": 0, "outra_unidade": 0, "por_vencedora": {}}


def test_uma_retomada_ou_um_n_susp_falham_alto_com_a_intencao_suspensa_desligada():
    with pytest.raises(RuntimeError, match="retomada"):
        lr.trocas_de_meta(_registro_falso([_m(retomou=True)]))
    with pytest.raises(RuntimeError, match="n_susp"):
        lr.trocas_de_meta(_registro_falso([_m([{"chave": ["comer", "cheiro", None], "motivo": "trocou", "n_susp": 1}])]))
    with pytest.raises(RuntimeError, match="ligada"):
        lr.trocas_de_meta(_registro_falso([], suspensa=True))
    with pytest.raises(RuntimeError, match="dos conhecidos"):
        lr.trocas_de_meta(_registro_falso([_m([{"chave": ["comer", "cheiro", None], "motivo": "inventado"}])]))


# ------------------------------------------------------------------ a fumaca de ponta a ponta
def test_a_fumaca_roda_de_ponta_a_ponta(tmp_path):
    cfg = copy.deepcopy(_cfg("fumaca"))
    cfg["unidades"] = {"bases": [101], "k": 1, "prefixo": "digibrain_prototipo"}
    cfg["dias"] = 1
    pasta = tmp_path / "fumaca"
    r = lr.rodar(cfg, pasta, 1, CONFIGS / "fumaca.json")
    assert r["meta"]["modo"] == "fumaca" and len(r["registros"]) == 24 and r["resultado"]["vidas"] == 24
    meta = json.loads((pasta / "meta.json").read_text(encoding="utf-8"))
    assert set(meta["artefatos_sha256"]) == {"medidas.json", "resultado.json"}
    for nome, sha in meta["artefatos_sha256"].items():
        assert bv._sha(pasta / nome) == sha
    assert set(meta["sha256"]) >= {"config.py", "engine.py", "metrics.py"} and meta["processos"] == 1
    assert len(list((pasta / "vidas").rglob("*.jsonl"))) == 24
    res = json.loads((pasta / "resultado.json").read_text(encoding="utf-8"))
    assert {"primario", "premissas", "sorteado", "leitura", "descritivo"} <= set(res)
    assert set(res["descritivo"]) == {"faixas_d0", "visitas", "trocas", "corpo", "outros"}
    assert all(set(v["corpo"]) == {"vida", "dias_8_14"} for v in json.loads((pasta / "medidas.json").read_text(encoding="utf-8")).values())
    with pytest.raises(FileExistsError):
        lr.rodar(cfg, pasta, 1)
