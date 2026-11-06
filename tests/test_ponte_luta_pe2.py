"""A ponte da luta, PE2 (docs/TAREFA_V3_PONTE_LUTA.md, secoes 3.2 e 3.5): o gancho `receber_luta`, o resumo da luta na Observacao e a
origem `luta` no M-MEM (`outro` = rival), atras de `ConfigLutaMemoria.ligada` (a chave `luta_memoria`, desligada).

T-PL-2: um resumo de derrota com dor vira um episodio `luta` com o rival em `outro`; um empate sem dor nao vira; o mesmo log da os mesmos
episodios; a consolidacao guarda um por categoria (lutar, rival, sinal). G2: desligada, nada novo (os gabaritos de hoje estao nos testes
deles). Nenhum modulo recebe o resultado como recompensa (secao 7): o V, o E, o g_apr e o M-PLAST nao andam. So as sementes dos testes."""
from __future__ import annotations

import json
import sys
from dataclasses import fields, replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab.config import (CONFIG_CORPO_DRIVES, CONFIG_DIGIBRAIN_INATOS, CONFIG_DIGIBRAIN_LIGADA, CONFIG_LUTA_CORPO_LIGADA,  # noqa: E402
                            CONFIG_LUTA_MEMORIA, CONFIG_LUTA_MEMORIA_LIGADA, CONFIG_MUNDO_LIGADA, CONFIG_PADRAO,
                            PARAMETROS_LUTA_MEMORIA, RECEPTORES_DIGIBRAIN, ConfigDigibrain, ConfigLutaMemoria)
from digilab.digibrain import mem as M  # noqa: E402
from digilab.digibrain.adapt import DigiBrain  # noqa: E402
from digilab.events import LogDeEventos, LutaSemChave  # noqa: E402
from digilab.motor_corpo import com_corpo  # noqa: E402
from digilab.mundo import MotorMundo, reproduzir_mundo  # noqa: E402

P = CONFIG_DIGIBRAIN_INATOS
S = P.escala
BASE = replace(CONFIG_DIGIBRAIN_LIGADA, cheiro_inato=True, intencao_cheiro=True)
AUTOBIO = replace(BASE, memoria_autobio=True)
LM = CONFIG_LUTA_MEMORIA_LIGADA
MotorMundoCorpo = com_corpo(MotorMundo)


def leituras(**kw) -> list:
    return [kw.get(r, 0) for r in RECEPTORES_DIGIBRAIN]


def _sens() -> dict:
    return {"objetos": [], "ha_cheiro": False, "contexto": {"noite": 0}, "falta": {"fome": 300}, "minuto": 600, "pos": (40, 72), "regiao": 1}


def _resumo(rival="muralha", resultado=-1, vida=400, tick=30) -> dict:
    return {"rival": rival, "resultado": resultado, "vida_perdida_s": vida, "tick": tick}


def _ep(r_n=0, depois=None, rival="muralha", resultado=-1, vida=400, k=4, tick=75):
    return M.episodio_luta(_sens(), RECEPTORES_DIGIBRAIN, leituras(), depois or leituras(), {"V": 5, "E": 9}, {"r": 2 * r_n, "r_n": r_n},
                           _resumo(rival, resultado, vida), k, tick, P)


# ------------------------------------------------------------------ a chave
def test_a_chave_nasce_desligada_tem_status_e_fica_fora_da_config_do_digibrain():
    assert ConfigLutaMemoria().ligada is False and CONFIG_LUTA_MEMORIA.ligada is False
    assert PARAMETROS_LUTA_MEMORIA["ligada"][0] in ("PROPOSTO", "DECIDIDO")
    assert {f.name for f in fields(ConfigLutaMemoria)} == set(PARAMETROS_LUTA_MEMORIA)
    assert "luta_memoria" not in {f.name for f in fields(ConfigDigibrain)}     # o dump do modular (gabarito de paridade) nao muda
    with pytest.raises(TypeError):
        ConfigLutaMemoria(ligada=1)


def test_a_chave_so_vale_com_a_memoria_autobio():
    with pytest.raises(ValueError, match="memoria_autobio"):
        DigiBrain(cfg_digibrain=BASE, cfg_luta_memoria=LM)
    with pytest.raises(ValueError, match="memoria_autobio"):
        M.Memoria(CONFIG_MUNDO_LIGADA, luta=True)
    assert DigiBrain(cfg_digibrain=AUTOBIO, cfg_luta_memoria=LM).luta_memoria is True


def test_desligada_o_gancho_levanta_erro_e_nada_ganha_campo():
    c = DigiBrain(cfg_digibrain=AUTOBIO)
    assert c.luta_memoria is False
    with pytest.raises(LutaSemChave):
        c.receber_luta("muralha", -1, 400, 30)
    mem = M.Memoria(CONFIG_MUNDO_LIGADA, autobio=True)
    with pytest.raises(ValueError, match="luta"):
        mem.codificar_autobio(_ep(r_n=-300))
    assert "lutas" not in json.dumps(c.estado_interno())


# ------------------------------------------------------------------ T-PL-2: o episodio
def test_t_pl_2_a_derrota_com_dor_vira_episodio_luta_com_o_rival_em_outro():
    ep = _ep(r_n=-300, depois=leituras(dor=400), rival="muralha", resultado=-1, vida=400)
    assert ep is not None
    assert ep["origem"] == "luta" and ep["outro"] == "muralha" and ep["classe"] == "muralha"
    assert ep["acao"] == ["lutar", "muralha"] and ep["categoria"] == ["lutar", "muralha", -1] and ep["sigma"] == -300
    assert ep["resultado"] == -1 and ep["vida_perdida_s"] == 400 and ep["dono"] == []
    assert ep["V_antes"] == ep["V_depois"] == 5 and ep["E_antes"] == ep["E_depois"] == 9       # a luta nao mexe no afeto
    mem = M.Memoria(CONFIG_MUNDO_LIGADA, autobio=True, luta=True)
    i = mem.codificar_autobio(ep)
    assert mem.recente[0]["id"] == i and mem.recente[0]["outro"] == "muralha"
    json.dumps(mem.estado_interno())


def test_t_pl_2_um_empate_sem_dor_nao_vira_episodio():
    assert _ep(r_n=0, resultado=0, vida=0) is None
    assert _ep(r_n=P.theta_sig - 1, depois=leituras(dor=P.theta_sig - 1), resultado=0, vida=0) is None
    # a regra e a de hoje, sem limiar novo: a subida da dor basta, e o sigma tambem
    assert _ep(r_n=0, depois=leituras(dor=P.theta_sig)) is not None
    assert _ep(r_n=-P.theta_sig) is not None
    assert _ep(r_n=0, depois=leituras(dor=P.theta_sig))["categoria"] == ["lutar", "muralha", 0]


def test_t_pl_2_o_mesmo_resumo_da_o_mesmo_episodio():
    a = _ep(r_n=-300, depois=leituras(dor=400))
    b = _ep(r_n=-300, depois=leituras(dor=400))
    assert a == b and json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def test_t_pl_2_a_consolidacao_guarda_um_por_categoria():
    mem = M.Memoria(CONFIG_MUNDO_LIGADA, autobio=True, luta=True)
    for rival, r_n in (("muralha", -400), ("sombra", -300), ("muralha", 300)):
        for _ in range(3):
            mem.codificar_autobio(_ep(r_n=r_n, rival=rival, k=0))
    assert len(mem.recente) == 9 and max(e["rep"] for e in mem.recente) >= P.n_rep_central
    mem.relogio(100)
    mem.relogio(10)                                   # o dia vira
    reg = mem.consolidar(P.janela_rec + 10)
    assert reg is not None and not mem.recente
    categorias = [tuple(e["categoria"]) for e in mem.central]
    assert sorted(categorias) == [("lutar", "muralha", -1), ("lutar", "muralha", 1), ("lutar", "sombra", -1)]
    assert len(set(categorias)) == len(categorias)
    assert all(e["outro"] == e["classe"] for e in mem.central + mem.duradoura)


# ------------------------------------------------------------------ no cerebro, com o motor
def _fabrica_motor(p, cfg, s):
    return MotorMundoCorpo(p, cfg, s, obediencia_desligada=True, cfg_mundo=CONFIG_MUNDO_LIGADA, cfg_corpo=CONFIG_CORPO_DRIVES,
                           cfg_luta_corpo=CONFIG_LUTA_CORPO_LIGADA)


def _cerebro(luta_memoria: bool, semente: int = 101):
    return DigiBrain(CONFIG_PADRAO, AUTOBIO, CONFIG_MUNDO_LIGADA, semente=semente,
                     cfg_luta_memoria=LM if luta_memoria else CONFIG_LUTA_MEMORIA)


def _vida(luta_memoria: bool, resumos: dict | None = None, passos: int = 600, semente: int = 101):
    """o DigiBrain no mundo com o corpo; `resumos`: passo de entrada -> (rival, resultado, vida perdida em S)"""
    cerebro = _cerebro(luta_memoria, semente)
    m = _fabrica_motor(cerebro, CONFIG_PADRAO, semente)
    for t in range(0, passos, 30):
        m.avancar(30)
        if resumos and t in resumos:
            m.resumo_luta(*resumos[t])
    return m, cerebro


RESUMOS = {120: ("muralha", -1, 700), 240: ("sombra", 0, 0), 360: ("muralha", -1, 900)}


def test_t_pl_2_no_cerebro_a_derrota_vira_episodio_e_o_empate_sem_dor_nao():
    m, c = _vida(True, RESUMOS)
    lutas = [x for mot in c.motivos for x in mot.get("lutas", [])]
    assert [x["rival"] for x in lutas] == ["muralha", "sombra", "muralha"]
    assert [x["episodio"] is not None for x in lutas] == [True, False, True]
    eps = [e for e in c.m.mem._guardados() if e["origem"] == "luta"]
    assert len(eps) == 2 and all(e["outro"] == "muralha" and e["sigma"] < 0 for e in eps)


def test_t_pl_2_o_mesmo_log_da_os_mesmos_episodios_no_replay():
    m, c = _vida(True, RESUMOS)
    r = reproduzir_mundo(LogDeEventos.de_jsonl(m.log.para_jsonl()), lambda cfg=None: _cerebro(True), CONFIG_PADRAO, 101,
                         fabrica_motor=_fabrica_motor)
    assert json.dumps(r.politica.estado_interno(), sort_keys=True) == json.dumps(c.estado_interno(), sort_keys=True)
    assert any(e["origem"] == "luta" for e in c.m.mem._guardados())


def test_a_luta_nao_e_recompensa_com_a_dor_zerada_nenhum_modulo_anda():
    """secao 7: uma derrota sem dor (vida perdida 0) nao muda o V, o E, o g_apr nem o M-PLAST, com a chave ligada ou desligada"""
    _, a = _vida(True, {120: ("muralha", -1, 0), 240: ("muralha", -1, 0)})
    _, b = _vida(False)
    ia, ib = a.estado_interno(), b.estado_interno()
    for modulo in ("afeto", "plast", "estado", "impulso", "arb", "sens"):
        if modulo in ia["modulos"]:
            assert json.dumps(ia["modulos"][modulo], sort_keys=True) == json.dumps(ib["modulos"][modulo], sort_keys=True), modulo
