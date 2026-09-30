"""M1: confianca de combate e desgaste por rival repetido (docs/DESIGN_MVP_M1_CONFIANCA.md)."""
from __future__ import annotations

import hashlib
import json
import math
import sys
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

from digilab.confianca import (ConfiancaCombate, atualizar_confianca, atualizar_encontros,  # noqa: E402
                               epsilon_confianca, faixa, novidade, tick_saida_faixa)
from digilab.config import (CONFIG_CONFIANCA, CONFIG_CONFIANCA_LIGADA, CONFIG_EDUCACAO_LIGADA,  # noqa: E402
                            CONFIG_LESOES_LIGADA, ConfigConfianca)
from digilab.educacao import epsilon_disciplina, epsilon_pet, fabricas_educacao, reproduzir_educacao  # noqa: E402
from digilab.evolucao import ovo  # noqa: E402
from digilab.expressao import CONFIANCA_TXT, confiancas_citadas, expressar_confianca  # noqa: E402
from digilab.protocol import (PARAMETROS_CONFIANCA_M1, PARAMETROS_EDUCACAO_V1, Status,  # noqa: E402
                              confianca_nao_referendados, hash_parametros_educacao, validar_parametros_educacao)
from digilab.temperamento import Temperamento, sortear  # noqa: E402

C = CONFIG_CONFIANCA_LIGADA
GABARITO_G1 = RAIZ / "tests" / "gabaritos" / "confianca_g1_69001.json"


# ------------------------------------------------------------------ funcoes puras
def test_chave_desligada_por_padrao_e_numeros_do_desenho():
    assert CONFIG_CONFIANCA.ligada is False and C.ligada is True
    assert (C.lambda_novidade, C.tau_habituacao_min, C.eta_confianca, C.k_sensibilidade) == (0.7, 2880, 0.25, 0.5)
    assert (C.tau_confianca_min, C.kappa_eps, C.limiar_frase, C.histerese_frase_min) == (1440, 0.10, 0.4, 120)
    assert (C.limiar_tedio, C.n_tedio) == (0.3, 3)


def test_curva_da_novidade_por_rival():
    m = 0.0
    novs = []
    for _ in range(5):                          # lutas seguidas (dt 0) contra o mesmo rival
        novs.append(novidade(m, C.lambda_novidade))
        m = atualizar_encontros(m, 0, C.tau_habituacao_min)
    assert novs[0] == 1.0
    assert novs[2] == pytest.approx(0.25, abs=0.005)      # 3a: exp(-1,4) = 0,247
    assert novs[4] == pytest.approx(0.06, abs=0.002)      # 5a: exp(-2,8) = 0,061
    assert m == pytest.approx(5.0)
    # recuperacao com tau: dois dias sem enfrentar o rival devolvem parte da novidade
    m2 = m * math.exp(-2 * 1440 / C.tau_habituacao_min)
    assert novidade(m2, C.lambda_novidade) == pytest.approx(math.exp(-0.7 * 5 / math.e), rel=1e-12)
    assert 0.25 < novidade(m2, C.lambda_novidade) < 0.30    # ~0,28 (o desenho cita ~0,36 usando m = 4, antes da 5a)
    assert novidade(atualizar_encontros(m, 10 ** 9, C.tau_habituacao_min), C.lambda_novidade) == pytest.approx(math.exp(-0.7))


def test_confianca_sobe_com_vitoria_desce_com_derrota_e_corta_em_mais_menos_um():
    c = atualizar_confianca(0.0, 0, 1, 1.0, 0.0, C)
    assert c == pytest.approx(C.eta_confianca)
    assert atualizar_confianca(0.0, 0, -1, 1.0, 0.0, C) == pytest.approx(-C.eta_confianca)
    assert atualizar_confianca(0.3, 0, 0, 1.0, 0.0, C) == pytest.approx(0.3)       # empate: so o decaimento
    # a derrota pesa mais pela sensibilidade; a vitoria nao
    assert atualizar_confianca(0.0, 0, -1, 1.0, 1.0, C) == pytest.approx(-C.eta_confianca * (1 - C.k_sensibilidade))
    assert atualizar_confianca(0.0, 0, -1, 1.0, -1.0, C) == pytest.approx(-C.eta_confianca * (1 + C.k_sensibilidade))
    assert atualizar_confianca(0.0, 0, 1, 1.0, 1.0, C) == pytest.approx(C.eta_confianca)
    # a novidade pesa: repetir rende menos
    assert atualizar_confianca(0.0, 0, 1, 0.1, 0.0, C) == pytest.approx(0.1 * C.eta_confianca)
    # corte em +-1
    c = 0.0
    for _ in range(20):
        c = atualizar_confianca(c, 0, 1, 1.0, 0.0, C)
    assert c == 1.0
    for _ in range(40):
        c = atualizar_confianca(c, 0, -1, 1.0, 1.0, C)
    assert c == -1.0
    with pytest.raises(ValueError):
        atualizar_confianca(0.0, 0, 2, 1.0, 0.0, C)
    with pytest.raises(ValueError):
        atualizar_confianca(0.0, -1, 1, 1.0, 0.0, C)


def test_decaimento_para_zero_entre_lutas():
    assert atualizar_confianca(0.8, C.tau_confianca_min, 0, 1.0, 0.0, C) == pytest.approx(0.8 / math.e)
    assert atualizar_confianca(-0.8, 10 * C.tau_confianca_min, 0, 1.0, 0.0, C) == pytest.approx(-0.8 * math.exp(-10))
    cc = ConfiancaCombate(C)
    cc.registrar(100, "a", 1, 0.0)
    assert cc.valor(100) == pytest.approx(C.eta_confianca)
    assert cc.valor(100 + C.tau_confianca_min) == pytest.approx(C.eta_confianca / math.e)
    assert cc.c == pytest.approx(C.eta_confianca)                       # valor() nao muda o estado


def test_epsilon_so_sobe_com_inseguranca():
    assert epsilon_confianca(-1.0, C.kappa_eps) == pytest.approx(C.kappa_eps)
    assert epsilon_confianca(-0.5, C.kappa_eps) == pytest.approx(0.05)
    assert epsilon_confianca(0.0, C.kappa_eps) == 0.0 and epsilon_confianca(1.0, C.kappa_eps) == 0.0
    with pytest.raises(ValueError):
        epsilon_confianca(1.5, C.kappa_eps)
    # epsilon_pet: sem a chave a confianca nao entra; com ela soma kappa * max(0, -c)
    assert epsilon_pet(50, 0, confianca=-1.0) == epsilon_disciplina(50)
    assert epsilon_pet(50, 0, confianca=-1.0, cc=C) == pytest.approx(epsilon_disciplina(50) + C.kappa_eps)
    assert epsilon_pet(50, 0, confianca=1.0, cc=C) == epsilon_disciplina(50)
    assert epsilon_pet(100, 10 ** 6, confianca=-1.0, cc=C) == pytest.approx(C.kappa_eps)   # piso da experiencia + termo


# ------------------------------------------------------------------ o estado e as frases
def _lutas(cc: ConfiancaCombate, t0: int, rival: str, sinal: int, n: int, passo: int = 30, sens: float = 0.0) -> int:
    for k in range(n):
        cc.registrar(t0 + k * passo, rival, sinal, sens)
    return t0 + (n - 1) * passo


def test_estado_com_limiar_e_histerese():
    H = C.histerese_frase_min
    cc = ConfiancaCombate(C)
    assert cc.estado(0) == {"estado": "neutro", "desde": None, "c": 0.0, "lutas": []}
    # vitorias alternando dois rivais (novidade alta): c passa de 0,4 na 2a luta (tick 1030) e chega a ~0,72
    for k, r in enumerate(["a", "b", "a", "b"]):
        cc.registrar(1000 + 30 * k, r, 1, 0.0)
    t, ini = 1090, 1030
    assert cc.historico[0]["c"] < C.limiar_frase <= cc.historico[1]["c"] and cc.c > 0.7
    assert cc.estado(ini + H - 1)["estado"] == "neutro"      # ainda nao passou a histerese
    e = cc.estado(ini + H)
    assert e["estado"] == "confiante" and e["desde"] == ini + H
    assert e["lutas"] == [1090, 1060, 1030, 1000]              # as vitorias que puseram o pet no estado
    # a frase fica ate a confianca decair abaixo do limiar e ficar la por 2 h
    sai = tick_saida_faixa(t, cc.c, C)
    assert sai is not None and cc.valor(sai) < C.limiar_frase <= cc.valor(sai - 1)
    assert cc.estado(sai + H - 1)["estado"] == "confiante"
    assert cc.estado(sai + H)["estado"] == "neutro"
    # derrotas seguidas (sensibilidade -1, o melindroso: pesam mais): inseguro a partir da 2a
    for k in range(4):
        cc.registrar(sai + 5000 + 30 * k, "b", -1, -1.0)
    ini2 = next(x["tick"] for x in cc.historico if x["c"] <= -C.limiar_frase)
    assert ini2 == sai + 5030 and cc.c <= -C.limiar_frase
    assert cc.estado(ini2 + H - 1)["estado"] == "neutro"
    e = cc.estado(ini2 + H)
    assert e["estado"] == "inseguro" and e["lutas"] == [sai + 5090, sai + 5060, sai + 5030, sai + 5000]


def test_estado_entediado_do_rival():
    cc = ConfiancaCombate(C)
    # empates contra o mesmo rival: c fica 0, a novidade cai (1, 0,5, 0,25, 0,12...)
    t = _lutas(cc, 500, "x", 0, 5)
    novs = [x["novidade"] for x in cc.historico]
    assert novs[0] == 1.0 and all(n <= C.limiar_tedio for n in novs[-C.n_tedio:])
    assert faixa(0.0, tuple(novs), C) == "entediado" and faixa(0.0, tuple(novs[:2]), C) == "neutro"
    e = cc.estado(t + C.histerese_frase_min)
    assert e["estado"] == "entediado" and e["lutas"] == [x["tick"] for x in reversed(cc.historico[-C.n_tedio:])]
    assert cc.estado(t + C.histerese_frase_min - 1)["estado"] == "neutro"
    # confiante e inseguro tem prioridade sobre o tedio
    assert faixa(0.5, tuple(novs), C) == "confiante" and faixa(-0.5, tuple(novs), C) == "inseguro"
    with pytest.raises(ValueError):
        cc.estado(t - 1)


def test_frases_por_estagio_e_marcador_unico():
    for nome, e in CONFIANCA_TXT.items():
        for est in ("crianca", "adolescente", "adulto"):
            x = expressar_confianca({"estado": nome, "lutas": [1, 2]}, est)
            assert x is not None and confiancas_citadas(x.conteudo) == {nome} and x.motivo_ref == ("confianca", (1, 2))
        b = expressar_confianca({"estado": nome, "lutas": []}, "bebe")
        assert b.canal == "emote" and b.conteudo == e["bebe"] and not confiancas_citadas(b.conteudo)
    assert expressar_confianca({"estado": "confiante", "lutas": []}, "adulto").conteudo == "Tô confiante: ganhei as últimas."
    assert expressar_confianca({"estado": "inseguro", "lutas": []}, "adulto").conteudo == "Ando inseguro depois daquelas derrotas."
    assert expressar_confianca({"estado": "entediado", "lutas": []}, "adulto").conteudo == "De novo esse aí? Já sei tudo dele."
    assert expressar_confianca({"estado": "neutro", "lutas": []}, "adulto") is None
    with pytest.raises(ValueError):
        expressar_confianca({"estado": "neutro", "lutas": []}, "ovo")


# ------------------------------------------------------------------ registro de parametros
def test_parametros_registrados_propostos_sem_fonte_e_nao_referendados():
    validar_parametros_educacao()
    campos = {f"ConfigConfianca.{f}" for f in ConfigConfianca.__dataclass_fields__}
    assert set(PARAMETROS_CONFIANCA_M1) == campos
    for n, c in PARAMETROS_CONFIANCA_M1.items():
        assert c.valor == getattr(CONFIG_CONFIANCA, n.split(".")[1])
        if n != "ConfigConfianca.ligada":
            assert c.status is Status.PROPOSTO and "sem fonte" in c.justificativa, n
    assert sorted(confianca_nao_referendados()) == sorted(campos - {"ConfigConfianca.ligada"})
    # o registro do educacao-v1 (e o hash que as runs V3/E1 gravaram no meta) nao muda com o M1
    assert not any(n.startswith("ConfigConfianca.") for n in PARAMETROS_EDUCACAO_V1)
    assert hash_parametros_educacao() == hash_parametros_educacao(PARAMETROS_EDUCACAO_V1)


# ------------------------------------------------------------------ motor: replay e gate G1
S = 69001


def _fabricas_luta(cc=None, especie=None):
    from digilab.combate_v2.v21.bots import lutador_adulto
    esp, _ = ovo(S)
    esp = especie or esp
    return fabricas_educacao(S, esp, sortear(S), ce=CONFIG_EDUCACAO_LIGADA, cl=CONFIG_LESOES_LIGADA, cc=cc,
                             lutador_do_pet=lambda m: lutador_adulto("tita", esp))


def test_motor_com_a_chave_recalcula_a_confianca_no_replay():
    fp, fm = _fabricas_luta(cc=C)
    m = fm(fp(None), None, S)
    assert m.confianca is not None and m.epsilon_lutador() == pytest.approx(epsilon_disciplina(0))
    m.avancar(200)
    rivais = ["bot:muralha@limo", "bot:muralha@limo", "bot:duelista@brasa", "bot:muralha@limo"]
    for i, r in enumerate(rivais):
        m.lutar(r, 500 + i)
        m.avancar(20)
    h = m.historico_lutas
    assert all("confianca" in x for x in h) and h[0]["confianca"]["novidade"] == 1.0
    assert h[1]["confianca"]["novidade"] < 1.0 and h[2]["confianca"]["novidade"] == 1.0
    assert h[3]["confianca"]["novidade"] < h[1]["confianca"]["novidade"]
    assert m.vitorias_vida == pytest.approx(sum(x["confianca"]["novidade"] for x in h if x["resultado"] == "vitoria"))
    assert "confianca" in m.resumo_educacao() and m.resumo_educacao()["confianca"]["lutas"] == 4
    assert m.epsilon_lutador() >= epsilon_pet(m.disciplina, m.vitorias_vida)
    fp2, fm2 = _fabricas_luta(cc=C)
    r = reproduzir_educacao(m.log, fp2, semente=S, fabrica_motor=fm2)
    assert r.historico_lutas == m.historico_lutas and r.resumo_educacao() == m.resumo_educacao()
    assert r.confianca.historico == m.confianca.historico and r.confianca.estado(r._estado.tick) == m.confianca.estado(m._estado.tick)
    # a sensibilidade do temperamento e a que entra na derrota
    cc2 = ConfiancaCombate(C)
    for x in h:
        cc2.registrar(x["tick"], x["rival"], {"vitoria": 1, "derrota": -1, "empate": 0}[x["resultado"]], m.temperamento.sensibilidade)
    assert cc2.c == m.confianca.c


def test_sem_a_chave_nada_muda_nem_aparece():
    fp, fm = _fabricas_luta()
    m = fm(fp(None), None, S)
    assert m.confianca is None
    m.avancar(200)
    for i in range(3):
        m.lutar("bot:muralha@limo", 500 + i)
    assert isinstance(m.vitorias_vida, int) and m.vitorias_vida == sum(x["resultado"] == "vitoria" for x in m.historico_lutas)
    assert all("confianca" not in x for x in m.historico_lutas) and "confianca" not in m.resumo_educacao()
    assert m.epsilon_lutador() == pytest.approx(epsilon_pet(m.disciplina, m.vitorias_vida))


def test_gate_g1_vida_69001_byte_a_byte_com_a_chave_desligada(tmp_path):
    """GATE G1: a vida atencioso@69001 de run_educacao._vida (V3) e a mesma do gabarito gerado antes do M1."""
    import run_educacao
    from digilab.events import LogDeEventos
    g = json.loads(GABARITO_G1.read_text(encoding="utf-8"))
    (_, s), spec, dados, _ = run_educacao._vida(("atencioso", S, g["dias"], str(tmp_path), {}))
    log = (tmp_path / "vidas" / f"atencioso@{S}.jsonl").read_bytes()
    assert hashlib.sha256(log).hexdigest() == g["log_sha256"] and log.count(b"\n") == g["eventos"]
    esp, temp_ovo = ovo(S)
    fp, _, fm, _ = run_educacao._fabricas("atencioso", S, esp, sortear(S), temp_ovo)
    r = reproduzir_educacao(LogDeEventos.de_jsonl(log.decode("utf-8")), fp, semente=S, fabrica_motor=fm)
    assert r.resumo_educacao() == g["resumo_educacao"]
    assert r.historico_lutas == g["historico_lutas"] and r.transicoes == g["transicoes"]
    assert json.dumps(spec, sort_keys=True) == json.dumps(g["spec"], sort_keys=True)
    e = r.estado()
    for k, v in g["estado"].items():
        assert e[k] == pytest.approx(v, rel=1e-9) if isinstance(v, float) else e[k] == v, k
