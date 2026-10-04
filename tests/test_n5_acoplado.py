"""V2, N5-ACOPLADO (docs/TAREFA_V2_N5_ACOPLADO.md): o modo acoplado do informante (P2a) e o motivo das regras novas dos lobos.

Acoplado: os modos certo e errado de hoje byte a byte (gabarito gravado antes da mudanca); o acoplado tem o mesmo multiconjunto de
(fruta, conteudo) do P2, com o conteudo verdadeiro, em ticks diferentes; a rng dele nao mexe nas outras; G1.
Motivo: motivo_lobos cita bola_no_cenario, fruta_no_cenario e a escolha da fruta, com a regra de honestidade de hoje (so vira fator o
que mudou a escolha); o embrulho PoliticaComMotivo nao muda a vida (repassa os ganchos das frutas); textos com marcador unico.
"""
from __future__ import annotations

import hashlib
import json
import random
import sys
from collections import Counter
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab.ambiente import DonoComBola, fabricas_ambiente  # noqa: E402
from digilab.config import (CONFIG_BOLA, CONFIG_BOLA_LIGADA, CONFIG_FRUTAS_LIGADA, CONFIG_INFORMACAO_LIGADA, CONFIG_LOBOS,  # noqa: E402
                            CONFIG_LOBOS_APRENDIZ)
from digilab.donos import criar_dono  # noqa: E402
from digilab.events import FRUTAS, AcaoPet, LogDeEventos  # noqa: E402
from digilab.expressao import FATORES, expressar, validar_tabelas  # noqa: E402
from digilab.frutas import (DonoInformante, OfertasFrutas, PoliticaInstintoFrutas, efeitos_humor, fabricas_frutas,  # noqa: E402
                            genoma_frutas, reproduzir_frutas, simular_vida_frutas)
from digilab.motivo import FATORES_MUNDO, FATORES_VIDA, Motivo, PoliticaComMotivo, motivo_fruta, motivo_lobos  # noqa: E402
from digilab.policies.lobos import PoliticaLobos  # noqa: E402
from digilab.treino import simular_vida  # noqa: E402

DONOS = ("atencioso", "relapso", "aleatorio", "incoerente")
SEMENTES = (11, 22, 33)                 # so dos testes
CF, CI, CB = CONFIG_FRUTAS_LIGADA, CONFIG_INFORMACAO_LIGADA, CONFIG_BOLA_LIGADA
GABARITO = RAIZ / "tests" / "gabaritos" / "n5_informante_certo_errado.json"


def _nucleo(m) -> tuple:
    return (m._estado, tuple(m.acoes_recentes(10**9)), m._rng_politica.getstate(), m._rng_ambiente.getstate(),
            m._rng_fruta.getstate())


def _vida(dono: str, s: int, informante=None, politica_fabrica=None, dias: int = 3, orc: int = 48):
    fp, fm = fabricas_frutas(cfg_frutas=CF, cfg_informacao=CI, politica_fabrica=politica_fabrica)
    v = simular_vida_frutas(f"{dono}-n5", criar_dono(dono), fp(), s, dias, orc, fm, OfertasFrutas(CF), rotulo_dono=dono,
                            informante=informante)
    return v, fp, fm


def _p2_e_p2a(dono: str, s: int, dias: int = 3):
    p2 = DonoInformante.do_genoma("certo", s, CF)
    _vida(dono, s, p2, dias=dias)
    return p2, DonoInformante.acoplado_de(p2, s, dias)


# ------------------------------------------------------------------ acoplado


def test_certo_e_errado_byte_a_byte_como_antes():
    """O gabarito foi gravado com o codigo da main antes desta mudanca (24 vidas de 3 dias)."""
    gab = json.loads(GABARITO.read_text(encoding="utf-8"))
    assert len(gab) == 24
    for chave, ref in gab.items():
        modo, dono, s = chave.split("|")
        inf = DonoInformante.do_genoma(modo, int(s), CF)
        v, _, _ = _vida(dono, int(s), inf)
        assert hashlib.sha256(v.motor.log.para_jsonl().encode()).hexdigest() == ref["log_sha256"], chave
        assert [list(x) for x in inf.feitas] == ref["feitas"] and v.informacoes == ref["informacoes"], chave


@pytest.mark.parametrize("dono", DONOS)
def test_acoplado_mesmo_multiconjunto_conteudo_verdadeiro_ticks_diferentes(dono):
    for s in SEMENTES:
        p2, p2a = _p2_e_p2a(dono, s)
        v, _, _ = _vida(dono, s, p2a)
        assert p2.feitas and p2a.pendentes() == 0 and v.informacoes == len(p2.feitas)
        assert Counter((f, c) for _, f, c in p2a.feitas) == Counter((f, c) for _, f, c in p2.feitas)
        real = efeitos_humor(genoma_frutas(s, CF), CF)
        assert all(c == ("mal" if real[f] < 0 else "bem") for _, f, c in p2a.feitas)
        assert [t for t, _, _ in p2a.feitas] != [t for t, _, _ in p2.feitas]
        assert all(t % 15 == 0 and 15 <= t <= 3 * 1440 for t, _, _ in p2a.feitas)


def test_acoplado_deterministico_e_a_ordem_do_multiconjunto_nao_importa():
    ef = {"a": -0.1, "b": 0.0, "c": 0.0}
    frutas = ["a", "b", "b", "c", "a"]
    d1 = DonoInformante.acoplado(ef, frutas, 77, 3)
    d2 = DonoInformante.acoplado(ef, list(reversed(frutas)), 77, 3)
    d3 = DonoInformante.acoplado(ef, frutas, 78, 3)
    assert d1.agenda == d2.agenda and d1.agenda != d3.agenda and d1.pendentes() == 5


def test_rng_do_acoplado_nao_mexe_nas_outras():
    """Com o instinto (que nao le a informacao) a vida com o acoplado e a vida sem informante sao a mesma: estado, acoes e as rngs
    de ambiente, politica e fruta; construir o acoplado nao toca o random global."""
    for s in SEMENTES:
        p2, _ = _p2_e_p2a("atencioso", s)
        antes = random.getstate()
        p2a = DonoInformante.acoplado_de(p2, s, 3)
        assert random.getstate() == antes
        com, _, _ = _vida("atencioso", s, p2a)
        sem, _, _ = _vida("atencioso", s, None)
        assert _nucleo(com.motor) == _nucleo(sem.motor) and com.interacoes == sem.interacoes == 48


def test_g1_replay_com_o_acoplado():
    for s in SEMENTES:
        _, p2a = _p2_e_p2a("incoerente", s)
        v, fp, fm = _vida("incoerente", s, p2a)
        r = reproduzir_frutas(LogDeEventos.de_jsonl(v.motor.log.para_jsonl()), fp, semente=s, fabrica_motor=fm)
        assert _nucleo(r) == _nucleo(v.motor) and r.resumo_frutas() == v.motor.resumo_frutas()


def test_acoplado_falha_alto_fora_do_contrato():
    ef = {f: 0.0 for f in FRUTAS}
    with pytest.raises(ValueError):
        DonoInformante.acoplado(ef, ["d"], 1, 3)
    with pytest.raises(ValueError):
        DonoInformante.acoplado_de(DonoInformante("errado", ef), 1, 3)
    with pytest.raises(ValueError):
        DonoInformante.acoplado(ef, ["a"], 1, 3).acoes(15, ["a"])
    with pytest.raises(ValueError):
        DonoInformante("acoplado", ef).acoes_do_passo(15, [])


# ------------------------------------------------------------------ motivo das regras novas


def test_tabelas_cobrem_os_fatores_do_mundo_com_marcador_unico():
    validar_tabelas()
    assert set(FATORES_MUNDO) <= set(FATORES_VIDA) <= set(FATORES)
    for f in FATORES_MUNDO:
        m = Motivo("vida", "comer", (f,), (), 0.5, False, tick=0)
        assert FATORES[f]["marcador"] in expressar(m, "adulto").conteudo
        assert FATORES[f]["marcador"] in expressar(m, "crianca").conteudo
    texto = " ".join(FATORES[f][e] for f in FATORES_MUNDO for e in ("crianca", "adolescente", "adulto")).lower()
    for palavra in ("prazer", "gosto", "delícia", "gostoso", "saboroso", "adoro"):
        assert palavra not in texto, palavra


def _registro(regra, candidatos, prior, u, acao, percepcao=None, aprendido=None):
    return {"regra": regra, "candidatos": candidatos, "contribuicoes": {"impulsos": prior}, "u": u, "acao": acao,
            "percepcao": percepcao or {"humor": 0.5}, "aprendido": aprendido}


def test_regra_do_mundo_so_e_fator_quando_mudou_a_escolha():
    cand = ["ocioso", "explorar", "brincar", "chamar_atencao", "comer"]
    prior = {"ocioso": 3.0, "explorar": 3.0, "brincar": 2.5, "chamar_atencao": 1.0, "comer": 4.0}
    # u no fim: com a fruta cai em comer; sem a fruta (comer = 0) cairia em chamar_atencao -> a fruta mudou a escolha
    m, _ = motivo_lobos(_registro("fruta_no_cenario", cand, prior, 0.99, "comer"), 0, None)
    assert m.fatores == ("fruta",)
    # u no comeco: ocioso com ou sem a fruta -> a fruta nao mudou nada
    m, _ = motivo_lobos(_registro("fruta_no_cenario", cand, prior, 0.01, "ocioso"), 0, None)
    assert m.fatores == ()
    cand_b = ["ocioso", "explorar", "brincar", "chamar_atencao"]
    prior_b = {"ocioso": 3.0, "explorar": 3.0, "brincar": 2.5 + 6.0, "chamar_atencao": 1.0}   # 1 + 3 x 0,5 + w_bola
    m, _ = motivo_lobos(_registro("bola_no_cenario", cand_b, prior_b, 0.60, "brincar"), 0, None)
    assert m.fatores == ("bola",)                                    # sem a bola, u 0,60 cairia em explorar
    m, _ = motivo_lobos(_registro("bola_no_cenario", cand_b, prior_b, 0.10, "ocioso"), 0, None)
    assert m.fatores == ()


def test_aprendido_cita_as_entradas_do_mundo():
    nomes = ["vies", "fome", "higiene", "energia", "humor", "saude", "sujeira", "dormindo", "hora", "ticks_sem_cuidado",
             "bola", "fruta"]
    cand = ["ocioso", "comer"]
    prior = {"ocioso": 5.0, "comer": 0.1}                            # o prior daria ocioso: o aprendido decidiu comer
    aprendido = {"ocioso": [0.0] * 12, "comer": [0.0] * 11 + [3.0]}  # o termo aprendido da entrada `fruta` puxou comer
    reg = _registro("fruta_no_cenario", cand, prior, 0.5, "comer", percepcao=dict.fromkeys(nomes, 0.5), aprendido=aprendido)
    m, diag = motivo_lobos(reg, 0, None)
    assert diag["lobo"] == "decisao" and m.fatores == ("fruta",)


def test_motivo_da_fruta():
    reg = {"presentes": ["a", "b"], "pesos": {"a": 0.2, "b": 0.8}, "u": 0.1, "escolhida": "a"}
    assert motivo_fruta(reg, {"a": 0.2, "b": 0.8}) == ("incentivo_fruta", "impulsos")
    assert motivo_fruta({**reg, "escolhida": "b"}, {"a": 0.2, "b": 0.8}) == ("escolha_aprendida_fruta", "decisao")
    assert motivo_fruta(reg, {"a": 0.0, "b": 0.0}) == (None, "impulsos")
    with pytest.raises(ValueError):
        motivo_fruta(reg, {"a": 0.2})
    base = _registro("fome_moderada", ["comer", "chamar_atencao"], {"comer": 1.0, "chamar_atencao": 1.0}, 0.2, "comer",
                     percepcao={"fome": 0.4, "higiene": 0.9, "energia": 0.8, "humor": 0.5, "saude": 1.0, "sujeira": 0.0,
                                "dormindo": 0.0, "hora": 0.5})
    with pytest.raises(ValueError):
        motivo_lobos({**base, "fruta": reg}, 0, None)
    m, diag = motivo_lobos({**base, "fruta": reg}, 0, None, incentivos={"a": 0.2, "b": 0.8})
    assert m.fatores == ("fome", "incentivo_fruta") and diag["fruta"]["fator"] == "incentivo_fruta"


def _vida_com_motivo(politica_fabrica, dono="atencioso", s=11, dias=3):
    p = []

    def fab(cfg=None):
        x = PoliticaComMotivo(politica_fabrica(cfg))
        p.append(x)
        return x

    v, _, _ = _vida(dono, s, None, fab, dias=dias)
    return v, p[0]


@pytest.mark.parametrize("aprende", (False, True))
def test_lobos_no_mundo_das_frutas_com_motivo(aprende):
    """Os lobos vendo as frutas, embrulhados: o embrulho nao muda a vida (os ganchos das frutas passam), e os motivos citam a fruta
    no cenario e a escolha da fruta; sem aprendizado, a escolha e sempre do incentivo."""
    cl = CONFIG_LOBOS_APRENDIZ if aprende else CONFIG_LOBOS
    fab = lambda cfg=None: PoliticaLobos(cfg, cl, None, CF)  # noqa: E731
    citados = Counter()
    for s in SEMENTES:
        v, pm = _vida_com_motivo(fab, s=s)
        nu, _, _ = _vida("atencioso", s, None, fab)
        assert _nucleo(v.motor) == _nucleo(nu.motor)
        assert all(set(m.fatores) <= set(FATORES_VIDA) and len(m.fatores) <= 2 for m in pm.motivos)
        citados.update(f for m in pm.motivos for f in m.fatores)
        frutas_diag = [d["fruta"] for d in pm.diagnosticos if "fruta" in d]
        assert len(frutas_diag) == v.motor.contagem_frutas["comidas"]
        if not aprende:
            assert all(d["lobo"] == "impulsos" for d in frutas_diag)
    assert citados["fruta"] > 0 and citados["incentivo_fruta"] > 0
    if not aprende:
        assert citados["escolha_aprendida_fruta"] == 0


def test_lobos_no_mundo_da_bola_citam_a_bola():
    fab = lambda cfg=None: PoliticaComMotivo(PoliticaLobos(cfg, CONFIG_LOBOS, CB, None))  # noqa: E731
    citados = Counter()
    for s in SEMENTES:
        fp, fm = fabricas_ambiente(cfg_bola=CB, politica_fabrica=fab)
        p = fp()
        simular_vida("atencioso-bola", DonoComBola("atencioso", CB), p, s, 3, 48, rotulo_dono="atencioso", fabrica_motor=fm)
        citados.update(f for m in p.motivos for f in m.fatores)
    assert citados["bola"] > 0


def test_instinto_no_mundo_com_motivo():
    """O instinto das frutas embrulhado nao quebra nas regras do mundo: cita a fruta quando come com ela no cenario, nunca a bola."""
    fab = lambda cfg=None: PoliticaInstintoFrutas(cfg, CONFIG_BOLA, CF)  # noqa: E731
    citados = Counter()
    for s in SEMENTES:
        v, pm = _vida_com_motivo(fab, s=s)
        nu, _, _ = _vida("atencioso", s, None, fab)
        assert _nucleo(v.motor) == _nucleo(nu.motor)
        for m in pm.motivos:
            assert "bola" not in m.fatores
            if "fruta" in m.fatores:
                assert m.acao == AcaoPet.COMER.value
        citados.update(f for m in pm.motivos for f in m.fatores)
    assert citados["fruta"] > 0
