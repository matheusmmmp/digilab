"""Digimons que mentem (DESIGN_VOZ_PROPRIA, secao 9): honestidade, chance, janela de fala, desfechos, replay
e as reacoes dos donos simulados. Desligada por padrao (a V3 e a confirmatoria: test_reproducao_v3_confirmatoria)."""
from __future__ import annotations

import random
import sys
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

from digilab.config import (CONFIG_EDUCACAO_LIGADA, CONFIG_LESOES_LIGADA, CONFIG_MENTIRA,  # noqa: E402
                            CONFIG_MENTIRA_LIGADA)
from digilab.donos import Visao  # noqa: E402
from digilab.donos_educacao import DonoComEducacao, simular_vida_educacao  # noqa: E402
from digilab.educacao import MotorEducacao, fabricas_educacao, reproduzir_educacao  # noqa: E402
from digilab.events import AcaoUsuario, LogDeEventos  # noqa: E402
from digilab.evolucao import ovo  # noqa: E402
from digilab.protocol import hash_parametros_educacao, validar_parametros_mentira  # noqa: E402
from digilab.temperamento import sortear  # noqa: E402
from run_educacao import _fabricas, rival_por_nome, ticks_sparring  # noqa: E402

S = 69002


def _motor(**kw) -> MotorEducacao:
    fp, fm = fabricas_educacao(S, "brasa", sortear(S), ce=CONFIG_EDUCACAO_LIGADA, cm=CONFIG_MENTIRA_LIGADA, **kw)
    return fm(fp(None), None, S)


def test_parametros_e_hash_da_educacao_intacto():
    validar_parametros_mentira()
    assert hash_parametros_educacao().startswith("6a9037ade6b5")        # = artifacts_educacao_v3c/meta.json


def test_desligada_por_padrao_e_exige_educacao():
    assert not CONFIG_MENTIRA.ligada
    fp, fm = fabricas_educacao(S, "brasa", sortear(S), ce=CONFIG_EDUCACAO_LIGADA)
    m = fm(fp(None), None, S)
    with pytest.raises(ValueError):
        m.falar("reencontro")
    assert "honestidade" not in m.estado()["educacao"]
    with pytest.raises(ValueError):
        fp, fm = fabricas_educacao(S, "brasa", sortear(S), cm=CONFIG_MENTIRA_LIGADA)
        fm(fp(None), None, S)


def test_honestidade_e_chance_como_no_design():
    m = _motor()
    assert m.honestidade() == 1.0 and m.chance_mentira() == 0.0 and m.honestidade_mostrada() == 1.0
    # exemplo do design: sombrio, sobrecarga 80, disciplina 0 -> h = 0,24 e p = 0,38
    m.sombria = True
    m.treino.sobrecarga = 80.0
    assert m.honestidade() == pytest.approx(0.24) and m.chance_mentira() == pytest.approx(0.38)
    m.mentiras_impunes = 2
    assert m.chance_mentira() == pytest.approx(0.48)
    m.disciplina = 100
    assert m.chance_mentira() == pytest.approx(0.10)                   # so as impunes
    m.mentiras_impunes = 100
    assert m.chance_mentira() == CONFIG_MENTIRA.teto_chance and m.honestidade_mostrada() == 0.0
    m.acertos_mentira = CONFIG_MENTIRA.acertos_para_aprender
    assert m.chance_mentira() == 0.0
    m2 = _motor(honestidade_especie=CONFIG_MENTIRA.honestidade_enganador)
    assert m2.honestidade() == pytest.approx(0.7) and m2.chance_mentira() > 0


def _abrir(m, mentira: bool, tema="estado"):
    m.janela = {"tipo": "fala", "pedido": tema, "inicio": m.estado()["tick"], "prazo": m.estado()["tick"] + 30,
                "falso": mentira, "contradiz_barras": mentira and tema == "estado", "gatilho": "teste",
                "honestidade": 0.5, "chance": 0.5}


def test_desfechos_da_janela_de_fala():
    m = _motor()
    m.avancar(200)
    _abrir(m, True)
    assert m.estado()["educacao"]["janela"]["contradiz_barras"] is True
    m.observar(AcaoUsuario.REPREENDER)
    assert m.disciplina == CONFIG_EDUCACAO_LIGADA.passo_disciplina and m.acertos_mentira == 1 and m.janela is None
    _abrir(m, True, "historia")
    m.observar(AcaoUsuario.PETISCO)
    assert m.mentiras_impunes == CONFIG_MENTIRA.impunes_premiada and m.acertos_mentira == 0
    _abrir(m, True)
    m.observar(AcaoUsuario.ALIMENTAR)                     # nao julga: a janela continua
    assert m.janela is not None and m.contagem["refeicoes_recusadas"] == 0
    m.avancar(40)                                                      # prazo vencido: impune (confere na
    m.observar(AcaoUsuario.ACARICIAR)                                  # proxima decisao ou acao do dono)
    assert m.janela is None and m.mentiras_impunes == CONFIG_MENTIRA.impunes_premiada + 1
    v0 = m.vinculo.valor
    _abrir(m, False)
    m.observar(AcaoUsuario.REPREENDER)                    # bronca numa verdade
    assert m.contagem_mentira["broncas_injustas"] == 1 and m.disciplina == 25
    assert m.vinculo.serie[-1][2] == "bronca_sem_motivo" and v0 >= 0
    _abrir(m, False)
    m.observar(AcaoUsuario.ELOGIAR)
    assert m.contagem_mentira["verdades_aceitas"] == 1 and m.mentiras_impunes == 3
    assert [j["desfecho"] for j in m.historico_falas] == ["corrigida", "premiada", "impune", "bronca_injusta", "aceita"]


def test_evolucao_zera_impunes_e_acertos():
    m = _motor()
    m.mentiras_impunes, m.acertos_mentira = 5, 2
    m._evoluiu("adolescente", m.estado()["tick"])
    assert (m.mentiras_impunes, m.acertos_mentira) == (0, 0)


@pytest.fixture(scope="module")
def vidas():
    """exigente (vira sombrio) e permissivo, 14 dias, com a mentira ligada"""
    out = {}
    s = 70003
    esp, t_ovo = ovo(s)
    tmp = sortear(s)
    for b in ("exigente", "permissivo"):
        fp, _, _, pet = _fabricas(b, s, esp, tmp, t_ovo)
        cm = CONFIG_MENTIRA_LIGADA if b == "exigente" else replace(CONFIG_MENTIRA_LIGADA, fator_sombria=1.0)
        v = simular_vida_educacao(b, s, 14, esp, tmp, cl=CONFIG_LESOES_LIGADA, sparring=ticks_sparring(b),
                                  rival_sparring=pet.rival, lutador_do_pet=pet.lutador, rival_por_nome=rival_por_nome,
                                  cm=cm)
        out[b] = (v, s, esp, tmp, t_ovo, cm)
    return out


def test_vida_com_mentira_rejoga_bit_a_bit(vidas):
    for b, (v, s, esp, tmp, t_ovo, cm) in vidas.items():
        m = v.motor
        fp2, _, fm2, pet2 = _fabricas(b, s, esp, tmp, t_ovo)
        _, fm_m = fabricas_educacao(s, esp, tmp, ce=CONFIG_EDUCACAO_LIGADA, cl=CONFIG_LESOES_LIGADA,
                                    lutador_do_pet=pet2.lutador, rival_por_nome=rival_por_nome, cm=cm)
        r = reproduzir_educacao(LogDeEventos.de_jsonl(m.log.para_jsonl()), fp2, semente=s, fabrica_motor=fm_m)
        assert r.estado() == m.estado() and r.historico_janelas == m.historico_janelas
        assert r.resumo_mentira() == m.resumo_mentira() and r.vinculo.serie == m.vinculo.serie


def test_mesmas_falas_nos_mesmos_ticks_entre_bracos(vidas):
    # os slots de fala dependem so do tempo e do estagio; a rng_mentira e consumida sempre (numeros comuns)
    c = [vidas[b][0].motor.contagem_mentira["falas"] for b in ("exigente", "permissivo")]
    assert c[0] == c[1] > 0


def test_sombrio_mente_e_disciplinador_corrige(vidas):
    m = vidas["exigente"][0].motor
    assert m.sombria and m.contagem_mentira["mentiras"] > 0
    assert m.contagem_mentira["corrigidas"] > 0 and m.contagem_mentira["premiadas"] == 0
    assert vidas["exigente"][0].dono.respostas_fala["petisco"] == 0


def test_evento_fala_do_jogo_grava_e_rejoga():
    m = _motor()
    m.avancar(400)                                                     # crianca
    m.treino.sobrecarga = 100.0
    abertas = [m.falar("reencontro")]
    m.avancar(35)
    abertas.append(m.falar("marco"))
    assert [e.tipo for e in m.log].count("fala") == 2 and any(abertas)
    fp, fm = fabricas_educacao(S, "brasa", sortear(S), ce=CONFIG_EDUCACAO_LIGADA, cm=CONFIG_MENTIRA_LIGADA)
    r = reproduzir_educacao(m.log, fp, semente=S, fabrica_motor=fm)
    # a sobrecarga posta a mao nao esta no log: so confere que o replay leu o evento e sorteou igual
    assert r.contagem_mentira["falas"] == m.contagem_mentira["falas"]
    with pytest.raises(ValueError):
        fp, fm = fabricas_educacao(S, "brasa", sortear(S), ce=CONFIG_EDUCACAO_LIGADA)
        reproduzir_educacao(m.log, fp, semente=S, fabrica_motor=fm)


def _visao(janela):
    e = {"fome": 0.9, "higiene": 0.9, "humor": 0.9, "energia": 0.9, "saude": 1.0,
         "educacao": {"disciplina": 0, "lesionado": False, "janela": janela}}
    return Visao(estado=e, passo=40, passos_totais=288, orcamento=67, gasto=0, minimo_obrigatorio=0, maximo_permitido=6)


@pytest.mark.parametrize("braco,contradiz,esperado", [
    ("atencioso", True, AcaoUsuario.REPREENDER), ("atencioso", False, None),
    ("exigente", True, AcaoUsuario.REPREENDER), ("lutador", False, None),
    ("permissivo", True, AcaoUsuario.PETISCO), ("permissivo", False, AcaoUsuario.PETISCO),
    ("aleatorio", True, None)])
def test_reacao_dos_donos_a_fala(braco, contradiz, esperado):
    j = {"tipo": "fala", "pedido": "estado", "inicio": 0, "prazo": 30, "contradiz_barras": contradiz}
    r = DonoComEducacao(braco, 3)._resposta(_visao(j), random.Random(1))
    assert (r[0] if r else None) is esperado


def test_relapso_nao_ve_e_incoerente_sorteia():
    j = {"tipo": "fala", "pedido": "estado", "inicio": 0, "prazo": 30, "contradiz_barras": True}
    d = DonoComEducacao("relapso", 3)
    assert d._resposta_fala(j, random.Random(1)) is None
    inc = DonoComEducacao("incoerente", 3)
    vistos = {inc._resposta_fala(j, random.Random(k))[0] for k in range(40)}
    assert vistos == {AcaoUsuario.ELOGIAR, AcaoUsuario.REPREENDER}
