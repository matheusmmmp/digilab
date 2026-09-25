"""Personalidade, obediencia e desejo (docs/TAREFA_PERSONALIDADE_OBEDIENCIA.md, secao 5)."""

from __future__ import annotations

import ast
import json
import random
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab.config import CONFIG_DESEJO, CONFIG_OBEDIENCIA  # noqa: E402
from digilab.desejo import Desejo, desejo_de  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.events import AcaoPet, AcaoUsuario as U  # noqa: E402
from digilab.expressao import expressar, validar_tabelas  # noqa: E402
from digilab.metrics import cumprimento_desejo, decomposicao_ovo_braco, fracao_tempo_vontade  # noqa: E402
from digilab.obediencia import MotorPersonalidade, PoliticaBanditPersonalidade, conflito, termos_obediencia  # noqa: E402
from digilab.policies.bandit import PoliticaBandit  # noqa: E402
from digilab.policy import Observacao  # noqa: E402
from digilab.protocol import PROTOCOLO_ARENA_V1_MEMORIA_ESPACOS, PROTOCOLO_ARENA_V1_PERSONALIDADE, \
    bracos_do_protocolo, hash_protocolo  # noqa: E402
from digilab.temperamento import NEUTRO, Temperamento, sortear  # noqa: E402
from digilab.treino import reproduzir_com_feedback, simular_vida  # noqa: E402

DIAS, ORC = 3, 48


def _vida(dono, semente, t, desligada=False, dias=DIAS, orc=ORC):
    fm = lambda politica, cfg, s: MotorPersonalidade(politica, cfg, s, t, obediencia_desligada=desligada)  # noqa: E731
    v = simular_vida(dono, criar_dono(dono), PoliticaBanditPersonalidade(temperamento=t), semente, dias, orc,
                     rotulo_dono=dono, fabrica_motor=fm)
    return v, fm


@pytest.mark.parametrize("dono", ["atencioso", "aleatorio"])
def test_equivalencia_neutro_sem_obediencia_reproduz_memoria_por_espacos(dono):
    """Temperamento neutro + obediencia desligada = a run gravada da memoria por espacos, bit a bit."""
    dias, orc = PROTOCOLO_ARENA_V1_MEMORIA_ESPACOS.v("dias_simulados"), PROTOCOLO_ARENA_V1_MEMORIA_ESPACOS.v("orcamento_interacoes")
    v, _ = _vida(dono, 101, NEUTRO, desligada=True, dias=dias, orc=orc)
    pasta = RAIZ / "artifacts_v1_memoria_espacos" / "vidas"
    assert v.motor.log.para_jsonl() == (pasta / f"{dono}@101.jsonl").read_text(encoding="utf-8")
    assert json.loads(json.dumps(v.motor.politica.estado_interno(), sort_keys=True)) == \
        json.loads((pasta / f"{dono}@101.politica.json").read_text(encoding="utf-8"))


def test_mesmo_ovo_mesmo_temperamento_e_rng_ovo_isolada():
    assert sortear(303) == sortear(303) and sortear(303) != sortear(404)
    estado = random.getstate()
    sortear(505)
    assert random.getstate() == estado
    with pytest.raises(ValueError):
        Temperamento(curiosidade=1.5)


def test_fatores_do_temperamento_valem_um_no_neutro():
    assert NEUTRO.fator_variancia() == 1.0 and NEUTRO.peso_elogio() == 1.0
    assert NEUTRO.peso_repreensao() == 1.0 and NEUTRO.fator_tau_rancor() == 1.0
    t = Temperamento(curiosidade=1.0, teimosia=1.0, sensibilidade=0.0, rancor=1.0)
    assert t.fator_variancia() == pytest.approx(2.0) and t.peso_repreensao() == pytest.approx(0.5)
    p = PoliticaBanditPersonalidade(temperamento=t)
    assert p.cb.variancia_amostra == pytest.approx(0.5) and p.memoria.fator_tau == {"demora": 2.0, "bronca": 2.0}


def test_obediencia_nao_mexe_nas_outras_rngs_e_desligada_nao_sorteia():
    t = sortear(101)
    v, _ = _vida("aleatorio", 101, t, desligada=True)
    assert v.motor.recusas == [] and v.motor.pedidos_obediencia == 0
    # ligada: o clima (rng de ambiente) e o mesmo; a rng de obediencia e propria
    ligada, _ = _vida("aleatorio", 101, t)
    assert ligada.motor._rng_obediencia is not ligada.motor._rng_ambiente


def test_recusa_consome_orcamento_e_feedback_chega_a_politica():
    v, _ = _vida("aleatorio", 202, Temperamento(teimosia=1.0))
    m = v.motor
    assert v.interacoes == ORC and sum(1 for e in m.log if e.tipo == "acao_usuario") == ORC
    assert m.recusas, "com teimosia maxima e dono aleatorio deveria haver recusa"
    # a politica recebeu TODA acao do dono, inclusive as recusadas: o ultimo cuidado dela e o do log
    ultimo = max(e.tick for e in m.log if e.tipo == "acao_usuario")
    assert m.politica._tick_ultimo_cuidado == ultimo


def test_replay_reconstroi_vinculo_desejo_e_recusas():
    t = sortear(303)
    v, fm = _vida("incoerente", 303, t)
    r = reproduzir_com_feedback(v.motor.log, lambda c: PoliticaBanditPersonalidade(c, t), semente=303, fabrica_motor=fm)
    assert r.vinculo.serie == v.motor.vinculo.serie and r.desejos == v.motor.desejos
    assert [x.para_dict() for x in r.recusas] == [x.para_dict() for x in v.motor.recusas]
    assert r.estado() == v.motor.estado()


def test_motivo_da_recusa_so_cita_o_que_entrou_na_logistica():
    obs = (0.1, 0.9, 0.9, 0.9, 1.0, 0.0, 0.0, 0.5)            # fome urgente
    conf, nec = conflito(obs, U.BRINCAR, CONFIG_OBEDIENCIA)
    assert nec == "fome" and conf > 0
    assert conflito(obs, U.ALIMENTAR, CONFIG_OBEDIENCIA) == (0.0, None)
    p, contrib = termos_obediencia(0.5, NEUTRO, conf, nec, CONFIG_OBEDIENCIA, 0.5)
    assert set(contrib) == {"vinculo_baixo", "teimosia", "necessidade_fome"}
    assert contrib["vinculo_baixo"] == 0.0 and contrib["teimosia"] == 0.0 and contrib["necessidade_fome"] < 0
    v, _ = _vida("aleatorio", 202, Temperamento(teimosia=1.0))
    for r in v.motor.recusas:
        assert len(r.motivo.fatores) <= 1
        assert set(r.motivo.fatores) <= {"vinculo_baixo", "teimosia", "necessidade_fome", "necessidade_higiene",
                                         "necessidade_energia", "necessidade_humor"}
        for est in ("crianca", "adolescente", "adulto"):
            expressar(r.motivo, est)                       # tabela cobre recusa e fatores


def test_desejo_nao_consome_rng_e_bandit_novo_nao_tem_vontade():
    obs = Observacao(vetor_estado=(0.9, 0.9, 0.9, 0.9, 1.0, 0.0, 0.0, 0.5), ticks_desde_cuidado=0, total_cuidados=0)
    estado = random.getstate()
    assert desejo_de(obs, PoliticaBandit(), 10) is None
    assert random.getstate() == estado
    fome = Observacao(vetor_estado=(0.1, 0.9, 0.9, 0.9, 1.0, 0.0, 0.0, 0.5), ticks_desde_cuidado=0, total_cuidados=0)
    d = desejo_de(fome, PoliticaBandit(), 10)
    assert d.tipo == "necessidade" and d.alvo == "comer" and 0 < d.intensidade <= 1


def test_metricas_de_desejo_e_decomposicao():
    ds = [Desejo(0, "vontade", "brincar", .5), Desejo(100, "necessidade", "comer", .5), Desejo(150, "vontade", "comer", .3)]
    acoes = [(30, AcaoPet.BRINCAR), (170, AcaoPet.OCIOSO)]
    c = cumprimento_desejo(ds, acoes, 60)
    assert c == {"vontades": 2, "cumpridas": 1, "cumprimento": .5}
    assert fracao_tempo_vontade(ds, 200) == pytest.approx((100 + 50) / 200)
    dec = decomposicao_ovo_braco({("1", "a"): 1.0, ("1", "b"): 1.0, ("2", "a"): 0.0, ("2", "b"): 0.0})
    assert dec["fracao_ovo"] == pytest.approx(1.0) and dec["fracao_braco"] == pytest.approx(0.0)


def test_vinculo_temperamento_e_obediencia_fora_do_combate():
    proibidos = ("vinculo", "temperamento", "obediencia", "personalidade")
    for arq in (RAIZ / "digilab" / "combate_v2").rglob("*.py"):
        for no in ast.walk(ast.parse(arq.read_text(encoding="utf-8"))):
            nomes = []
            if isinstance(no, ast.Import):
                nomes = [a.name for a in no.names]
            elif isinstance(no, ast.ImportFrom):
                nomes = [no.module or ""] + [a.name for a in no.names]
            assert not any(p in n for n in nomes for p in proibidos), (arq, nomes)


def test_tabelas_e_protocolo():
    validar_tabelas()
    p = PROTOCOLO_ARENA_V1_PERSONALIDADE
    assert {pol for _, _, pol in bracos_do_protocolo(p)} == {"bandit_personalidade"}
    assert len(p.v("sementes_coorte")) == 10
    assert hash_protocolo(PROTOCOLO_ARENA_V1_MEMORIA_ESPACOS).startswith("7dbe33a52ed6")
    assert CONFIG_DESEJO.k_cumprimento_ticks > 0


def test_tom_do_temperamento_cobre_tabela_e_so_cita_eixos_marcantes():
    from digilab.config import CONFIG_EXPRESSAO
    from digilab.expressao import ESTAGIOS, TOM_TEMPERAMENTO, TabelaIncompleta, expressar_temperamento, \
        tons_citados, validar_tabelas_personalidade

    validar_tabelas_personalidade()
    lim = CONFIG_EXPRESSAO.limiar_extremo
    for ovo in range(1, 60):
        t = sortear(ovo)
        marcantes = {(e, "+" if v > 0 else "-") for e, v in t.para_dict().items() if abs(v) >= lim}
        for est in ESTAGIOS:
            x = expressar_temperamento(t, est)
            citados = tons_citados(x.conteudo)
            assert citados <= marcantes, (ovo, est, x.conteudo)
            if est == "bebe":
                assert not citados                    # bebe so por emote, sem palavra
            if marcantes and est != "bebe":
                assert citados
    # cada polo de cada eixo aparece sozinho quando so ele passa do limiar
    for (eixo, polo) in TOM_TEMPERAMENTO:
        t = Temperamento(**{eixo: 0.9 if polo == "+" else -0.9})
        assert tons_citados(expressar_temperamento(t, "adulto").conteudo) == {(eixo, polo)}
        assert expressar_temperamento(t, "bebe").conteudo == TOM_TEMPERAMENTO[(eixo, polo)]["bebe"]
    assert tons_citados(expressar_temperamento(NEUTRO, "adulto").conteudo) == set()
    with pytest.raises(ValueError):
        expressar_temperamento(NEUTRO, "velho")
    assert issubclass(TabelaIncompleta, ValueError)


def test_desejo_na_expressao_distingue_tipo_da_crianca_em_diante_e_so_cita_o_calculo():
    from digilab.desejo import NECESSIDADES
    from digilab.expressao import ALVOS_DESEJO, DESEJO_TIPO, ESTAGIOS, expressar_desejo, marcadores_citados

    for tipo in ("necessidade", "vontade"):
        alvos = [a for _, a in NECESSIDADES.values()] if tipo == "necessidade" else [a.value for a in AcaoPet]
        for alvo in alvos:
            d = Desejo(3, tipo, alvo, 0.5)
            bebe = expressar_desejo(d, "bebe").conteudo
            assert all(e["marcador"] not in bebe for e in DESEJO_TIPO.values())
            for est in ESTAGIOS[1:]:
                c = expressar_desejo(d, est).conteudo
                outro = "vontade" if tipo == "necessidade" else "necessidade"
                assert DESEJO_TIPO[tipo]["marcador"] in c and DESEJO_TIPO[outro]["marcador"] not in c, c
                citados = marcadores_citados(c)
                if tipo == "necessidade" and est != "crianca":
                    nome = next(n for n, (_, a) in NECESSIDADES.items() if a == alvo)
                    assert citados == {nome}, c        # so a necessidade que passou do limiar
                else:
                    assert citados == set(), c         # vontade: nenhuma causa inventada
    assert set(ALVOS_DESEJO) >= {a.value for a in AcaoPet}
