"""TAREFA_TREINO_SOMBRIO, secao 7."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab.combate_v2.v21.bots import FORMAS, SOMBRIOS, lutador_adulto  # noqa: E402
from digilab.combate_v2.v21.catalogo import com_treino, stats, Forma  # noqa: E402
from digilab.combate_v2.v21.regras import Acao, eh_legal, estado_inicial  # noqa: E402
from digilab.config import CONFIG_CATALOGO, CONFIG_SOMBRIO, CONFIG_TREINO, STATS_V21  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.events import ACOES_TREINO, ACOES_V1, AcaoUsuario  # noqa: E402
from digilab.evolucao import ovo  # noqa: E402
from digilab.temperamento import sortear  # noqa: E402
from digilab.treino import CanalDeInteracao, reproduzir_com_feedback  # noqa: E402
from digilab.treino_stats import ToqueRejeitado, TreinoInvalido, TreinoPet  # noqa: E402
from digilab.treino_vida import BRACOS_TREINO, fabricas_treino, orcamento_treino, simular_vida_treino  # noqa: E402

DIAS = 3


def _vida(braco, s=3101, dias=DIAS):
    esp, _ = ovo(s)
    t = sortear(s)
    return simular_vida_treino(braco, s, dias, esp, t), esp, t


def test_replay_reproduz_treino_fadiga_e_sobrecarga_bit_a_bit():
    for b in ("exigente", "aleatorio"):
        v, esp, t = _vida(b)
        m = v.motor
        fp, fm = fabricas_treino(3101, esp, t)
        r = reproduzir_com_feedback(m.log, fp, semente=3101, fabrica_motor=fm)
        assert r.resumo_treino() == m.resumo_treino()
        assert [s.para_dict() for s in r.treino.sessoes] == [s.para_dict() for s in m.treino.sessoes]
        assert r.vinculo.serie == m.vinculo.serie and r.estado() == m.estado()


def test_sobrecarga_sobrevive_a_evolucao_e_os_contadores_zeram():
    t = TreinoPet("brasa")
    t.avancar(300, False, True)                     # crianca
    for k in range(5):
        t.avancar(300 + 10 * k, False, True)
        t.sessao(300 + 10 * k, "corrida", True)
    t.fadiga, t.sobrecarga, t.estresse, t.bem_cuidado = 70.0, 40.0, 10.0, False
    t.avancar(900, False, False)                    # vira adolescente, sem decaimento (mal cuidado)
    assert t.estagio == "adolescente" and t.fadiga == 0.0 and t.estresse == 0.0
    assert t.sobrecarga == 40.0 and t.total > 0


def test_forcar_so_com_fadiga_no_limite():
    t = TreinoPet("cirro")
    t.avancar(400, False, True)
    t.fadiga = CONFIG_TREINO.limite_forcar - 0.01
    s = t.sessao(400, "alvo", True)
    assert not s.forcada and t.sobrecarga == 0.0
    t.avancar(410, False, True)
    t.fadiga = CONFIG_TREINO.limite_forcar
    s = t.sessao(410, "alvo", True)
    assert s.forcada and t.sobrecarga == CONFIG_TREINO.sobrecarga_forcar
    with pytest.raises(TreinoInvalido):
        TreinoPet("cirro").sessao(0, "alvo", True)   # bebe nao treina


def test_toque_dentro_do_intervalo_e_rejeitado_sem_consumir_orcamento():
    esp, _ = ovo(3202)
    fp, fm = fabricas_treino(3202, esp, sortear(3202))
    motor = fm(fp(None), None, 3202)
    motor.avancar(400)
    canal = CanalDeInteracao(motor, 10, 6)
    canal.aplicar([AcaoUsuario.TREINAR_CORRIDA, AcaoUsuario.TREINAR_ALVO], 0, 10)
    assert canal.gasto == 1 and canal.rejeitados == 1
    assert sum(1 for e in motor.log if e.valor in {a.value for a in ACOES_TREINO}) == 1
    with pytest.raises(ToqueRejeitado):
        motor.observar(AcaoUsuario.TREINAR_ALVO)     # direto no motor: falha alto


def test_orcamento_identico_entre_bracos_incluindo_o_exigente():
    orc, _ = orcamento_treino(DIAS)
    gastos = {b: _vida(b)[0].interacoes for b in BRACOS_TREINO}
    assert set(gastos.values()) == {orc}
    assert _vida("exigente")[0].dono.contagem["treino"] > _vida("atencioso")[0].dono.contagem["treino"]


def test_donos_da_v1_nunca_sorteiam_treino():
    assert set(ACOES_V1).isdisjoint(ACOES_TREINO) and len(ACOES_V1) == 6
    import random
    d, rng = criar_dono("aleatorio"), random.Random(1)
    from digilab.donos import Visao
    for p in range(50):
        v = Visao(estado={"fome": .5, "higiene": .5, "humor": .5, "energia": .5, "sujeira": 0, "acao_atual": "ocioso",
                          "tick_do_dia": 600}, passo=p, passos_totais=50, orcamento=100, gasto=2 * p,
                  minimo_obrigatorio=2, maximo_permitido=2)
        assert all(a in ACOES_V1 for a in d.decidir(v, rng))


def test_normalizacao_preserva_proporcoes_e_devolve_o_total():
    base = stats(Forma("brasa", "adulto", "sereno", "brigao", "duelista"))
    treino = {"forca": 2.0, "vigor": 1.0}          # abaixo do teto de stat (no teto a sobra vai em partes iguais)
    n = com_treino(base, treino, True)
    tot = sum(base.values())
    assert sum(n.values()) == pytest.approx(tot)
    brutos = {k: base[k] + CONFIG_TREINO.peso_ponto_combate * treino.get(k, 0.0) for k in STATS_V21}
    livres = [k for k in STATS_V21 if CONFIG_CATALOGO.stat_min < n[k] < CONFIG_CATALOGO.stat_max]
    for a in livres:
        for b in livres:
            assert n[a] / n[b] == pytest.approx(brutos[a] / brutos[b])
    absoluto = com_treino(base, treino, False)
    assert sum(absoluto.values()) == pytest.approx(tot + 3.0 * CONFIG_TREINO.peso_ponto_combate)


def test_passivas_sombrias():
    dev, pred = lutador_adulto("devastador", "brasa"), lutador_adulto("predador", "cirro")
    e = estado_inicial(dev.perfil, pred.perfil)
    assert not eh_legal(e, 0, Acao.DEFENDER) and not eh_legal(e, 0, Acao.ESQUIVAR)
    assert not eh_legal(e, 1, Acao.RECUAR) and eh_legal(e, 1, Acao.AVANCAR)
    assert dev.epsilon >= CONFIG_SOMBRIO.epsilon_minimo and set(SOMBRIOS).isdisjoint(FORMAS)
    for linha, d in CONFIG_SOMBRIO.formas.items():
        assert sum(d["stats"].values()) == 0          # soma zero, como os demais modificadores


def test_treino_e_sobrecarga_fora_de_condicao_fisica_e_do_combate():
    """Barreira 2: nada em combate_v2/ importa o treino ou le sobrecarga/fadiga."""
    proibidos = {"treino_stats", "treino_vida"}
    nomes = {"sobrecarga", "fadiga", "estresse"}
    for arq in (RAIZ / "digilab" / "combate_v2").rglob("*.py"):
        arvore = ast.parse(arq.read_text(encoding="utf-8"))
        for no in ast.walk(arvore):
            if isinstance(no, ast.ImportFrom):
                assert not (no.module or "").split(".")[-1] in proibidos, arq
            if isinstance(no, (ast.Name, ast.Attribute)):
                nome = no.id if isinstance(no, ast.Name) else no.attr
                assert nome not in nomes, f"{arq}: {nome}"


def test_arvore_sombria_bate_com_o_json():
    import json
    arv = json.loads((RAIZ / "docs" / "arvore_evolucao.json").read_text(encoding="utf-8"))["ramos_sombrios"]
    for linha, d in arv["formas"].items():
        assert CONFIG_SOMBRIO.formas[linha]["nome"] == d["nome"] and CONFIG_SOMBRIO.formas[linha]["stats"] == d["stats"]
    assert CONFIG_SOMBRIO.epsilon_minimo == arv["efeitos_comuns"]["epsilon_minimo"]
    assert CONFIG_SOMBRIO.teto_vinculo == arv["efeitos_comuns"]["teto_de_vinculo"]


def test_sombrias_redesenhadas_para_o_s2():
    """A sombra tira a leitura do oponente: devastador fecha, bate e so solta o pesado com guts sobrando;
    bastiao = espelho sem as regras que leem o oponente. Predador e colosso partido seguem com os da base."""
    from digilab.combate_v2.v21.bots import ADULTOS
    dev = SOMBRIOS["devastador"]
    assert not any(c.nome.startswith("oponente_") for r in dev.regras for c in r.condicoes)
    assert Acao.PREPARAR_PESADO in [r.acao for r in dev.regras]
    bast = SOMBRIOS["bastiao_rachado"]
    assert bast.regras and all(r in ADULTOS["espelho"].regras for r in bast.regras)
    assert not any(c.nome.startswith("oponente_") for r in bast.regras for c in r.condicoes)
    assert SOMBRIOS["predador"] is ADULTOS["emboscador"] and SOMBRIOS["colosso_partido"] is ADULTOS["tita"]
    assert CONFIG_SOMBRIO.mult_devastador == 1.3 and CONFIG_SOMBRIO.mult_regen_colosso_partido == 0.85
