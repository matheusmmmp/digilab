"""Os testes de mecanismo da parte (b) da L-2 (docs/ESPEC_LONGE_L2_DIGIBRAIN_MODULAR.md, secao 6): a intencao de comer suspensa no reflexo
do sono, atras da subchave `intencao_suspensa` da ConfigDigibrain (desligada por padrao).

  - T-L2-1, o byte a byte: tests/test_gabarito_digibrain_conserto.py e tests/test_gabarito_digibrain_modular.py (desligada, os dois
    gabaritos); aqui, so que a subchave nasce desligada e que, desligada, nenhum campo novo aparece;
  - T-L2-2 a T-L2-7: o M-ESTADO em cenarios feitos a mao;
  - T-L2-8: o G-SEM-DIRECAO e a rng;
  - T-L2-9: o reflexo extraido para o M-ARB da o mesmo valor que a conta de hoje.
Vidas inteiras so com as sementes dos testes."""
from __future__ import annotations

import ast
import inspect
import json
import sys
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import run_v2_digibrain_prototipo as orq  # noqa: E402
from digilab.config import CONFIG_DIGIBRAIN, CONFIG_DIGIBRAIN_INATOS, CONFIG_DIGIBRAIN_LIGADA, CONFIG_PADRAO  # noqa: E402
from digilab.digibrain import arb as arb_mod  # noqa: E402
from digilab.digibrain import estado as estado_mod  # noqa: E402
from digilab.digibrain._comum import mul  # noqa: E402
from digilab.digibrain.estado import EstadoDinamico  # noqa: E402
from digilab.events import LogDeEventos  # noqa: E402

P = CONFIG_DIGIBRAIN_INATOS
S = P.escala
CD = replace(CONFIG_DIGIBRAIN_LIGADA, intencao_cheiro=True, cheiro_inato=True, intencao_suspensa=True)
BUSCA = {"chave": ("comer", "cheiro", None), "d": None}
DORMIR = {"chave": ("dormir", None, None), "d": None}
FOME = {"urgencias": {"fome": S}}                       # a fome urgente (acima de lambda_retomar)
SACIADO = {"urgencias": {"fome": P.lambda_retomar - 1}}


def ida(ident: int = 7, d: int = 300) -> dict:
    return {"chave": ("comer", "comida", ident), "d": d}


def sens(cheiro: bool = True, objetos: tuple = ()) -> dict:
    """so o que o M-ESTADO le: os objetos vistos (id, classe, d) e se ha cheiro"""
    return {"ha_cheiro": cheiro, "objetos": [{"id": i, "classe": c, "d": d} for i, c, d in objetos]}


def estado(cd=CD) -> EstadoDinamico:
    return EstadoDinamico(CONFIG_PADRAO, cd, P)


def suspender(e: EstadoDinamico, unidade: dict = BUSCA, k0: int = 0) -> None:
    """a intencao comeca na decisao k0 e o reflexo a suspende na k0 + 1"""
    e.contexto()
    assert e.escolhida(unidade, [1, 2, 3], 100, k0) == []
    e.consequencia(10, None, {"visto": True, "d": unidade["d"], "ha_cheiro": True, "comida_boa_vista": False})
    e.contexto()
    assert e.escolhida(DORMIR, [0, 0, 0], 100, k0 + 1, reflexo=True) == []
    e.consequencia(50, None, {"visto": True, "d": None, "ha_cheiro": True, "comida_boa_vista": False})


# ------------------------------------------------------------------ T-L2-1
def test_t_l2_1_a_subchave_nasce_desligada_e_desligada_nao_ha_campo_novo():
    assert CONFIG_DIGIBRAIN.intencao_suspensa is False and CONFIG_DIGIBRAIN_LIGADA.intencao_suspensa is False
    e = estado(replace(CD, intencao_suspensa=False))
    assert "suspensa" not in e.estado_interno() and not set(estado_mod.FINS_SUSPENSA) & set(e.fins)
    with pytest.raises(RuntimeError, match="sem a subchave"):
        e.cuidar_suspensa(sens(), FOME, False)


# ------------------------------------------------------------------ T-L2-2
def test_t_l2_2_o_reflexo_suspende_a_busca_sem_trocar():
    e = estado()
    suspender(e)
    assert e.I is None and e.suspensa["chave"] == BUSCA["chave"] and e.suspensa["n_susp"] == 1
    assert e.fins["trocou"] == 0 and e.F == 0 and e.suspensas == 1
    assert e.estado_interno()["suspensa"]["n_susp"] == 1 and e.suspensa_resumo() == {"chave": ["comer", "cheiro", None], "n_susp": 1}


def test_t_l2_2_sem_a_subchave_o_reflexo_troca_como_hoje():
    e = estado(replace(CD, intencao_suspensa=False))
    e.contexto()
    e.escolhida(BUSCA, [1, 2, 3], 100, 0)
    e.consequencia(10, None, {"visto": True, "d": None, "ha_cheiro": True, "comida_boa_vista": False})
    e.contexto()
    fins = e.escolhida(DORMIR, [0, 0, 0], 100, 1, reflexo=True)
    assert [f["motivo"] for f in fins] == ["trocou"] and e.F > 0


# ------------------------------------------------------------------ T-L2-3
def test_t_l2_3_a_retomada_devolve_a_mesma_intencao_com_a_persistencia():
    e = estado()
    suspender(e)
    s = dict(e.suspensa)
    assert e.cuidar_suspensa(sens(cheiro=True), FOME, reflexo=False) == []
    assert e.suspensa is None and e.retomadas == 1
    assert {k: e.I[k] for k in ("chave", "C", "n_sp", "n", "inicio", "d", "e", "r")} == {k: s[k] for k in ("chave", "C", "n_sp", "n",
                                                                                                         "inicio", "d", "e", "r")}
    ctx = e.contexto()
    assert ctx["I"] == BUSCA["chave"] and ctx["persistencia"] == {BUSCA["chave"]: mul(P.w_pers, s["C"], S)}
    assert e.escolhida(BUSCA, [9, 9, 9], 100, 2) == [] and e.I["n"] == s["n"] + 1 and e.I["inicio"] == 0


def test_t_l2_3_a_retomada_nao_forca_a_escolha():
    e = estado()
    suspender(e)
    e.cuidar_suspensa(sens(cheiro=True), FOME, reflexo=False)
    e.contexto()
    fins = e.escolhida({"chave": ("explorar", "vagar", None), "d": None}, [0, 0, 0], 100, 2)
    assert [f["motivo"] for f in fins] == ["trocou"]


# ------------------------------------------------------------------ T-L2-4
@pytest.mark.parametrize("reflexo", [True, False])
def test_t_l2_4_saciou_sem_frustracao(reflexo):
    e = estado()
    suspender(e)
    fins = e.cuidar_suspensa(sens(cheiro=True), SACIADO, reflexo)
    assert [f["motivo"] for f in fins] == ["saciou"] and e.F == 0 and e.suspensa is None and e.fins["saciou"] == 1


@pytest.mark.parametrize("reflexo", [True, False])
def test_t_l2_4_sumiu_com_frustracao(reflexo):
    e = estado()
    suspender(e)
    fins = e.cuidar_suspensa(sens(cheiro=False), FOME, reflexo)
    assert [f["motivo"] for f in fins] == ["sumiu"] and e.F > 0 and e.suspensa is None
    e2 = estado()
    suspender(e2, ida(7))
    fins = e2.cuidar_suspensa(sens(objetos=((9, "racao", 50),)), FOME, reflexo)      # a comida-alvo 7 fora dos vistos
    assert [f["motivo"] for f in fins] == ["sumiu"] and e2.F > 0


def test_t_l2_4_expirou_sem_frustracao():
    e = estado()
    suspender(e)
    for _ in range(P.n_suspensa_max - 1):
        assert e.cuidar_suspensa(sens(cheiro=True), FOME, reflexo=True) == []
    fins = e.cuidar_suspensa(sens(cheiro=True), FOME, reflexo=True)                  # a decisao de reflexo n_suspensa_max + 1
    assert [f["motivo"] for f in fins] == ["expirou"] and fins[0]["n_susp"] == P.n_suspensa_max + 1 and e.F == 0


def test_t_l2_4_achou_ao_acordar_com_a_opcao_composta():
    e = estado()
    suspender(e)
    fins = e.cuidar_suspensa(sens(cheiro=True, objetos=((3, "racao", 80),)), FOME, reflexo=False)
    assert [f["motivo"] for f in fins] == ["achou"] and fins[0]["credito"] is False and e.F == 0
    assert e.guardada is not None and e.suspensa is None and e.I is None
    e.contexto()
    assert e.escolhida(ida(3, 80), [5, 5, 5], 100, 2) == [] and e.I.get("composta") and e.I["inicio"] == 0


def test_t_l2_4_superada_ao_acordar():
    e = estado()
    suspender(e, ida(7, 300))
    fins = e.cuidar_suspensa(sens(objetos=((7, "racao", 300), (8, "racao", 100))), FOME, reflexo=False)
    assert [f["motivo"] for f in fins] == ["superada"] and e.F == 0
    e2 = estado()
    suspender(e2, ida(7, 300))
    assert e2.cuidar_suspensa(sens(objetos=((7, "racao", 300), (8, "racao", 400))), FOME, reflexo=False) == []   # mais longe: retoma


def test_t_l2_4_com_o_reflexo_nao_ha_achou_nem_superada():
    e = estado()
    suspender(e)
    assert e.cuidar_suspensa(sens(cheiro=True, objetos=((3, "racao", 80),)), FOME, reflexo=True) == []
    e2 = estado()
    suspender(e2, ida(7, 300))
    assert e2.cuidar_suspensa(sens(objetos=((7, "racao", 300), (8, "racao", 100))), FOME, reflexo=True) == []


def test_t_l2_4_cada_fim_vai_ao_p2_uma_vez():
    """pelo M-ADAPT: cada fim entra uma vez nos fins da decisao, e so o "achou" fica sem credito (segue pela opcao composta)"""
    from digilab.digibrain.adapt import _creditar

    class Plast:
        def __init__(self):
            self.n = 0

        def creditar(self, f):
            self.n += 1
            return {"ok": True}

    for motivo, cenario in (("saciou", (sens(), SACIADO)), ("sumiu", (sens(cheiro=False), FOME))):
        e = estado()
        suspender(e)
        p = Plast()
        _creditar(p, e.cuidar_suspensa(*cenario, reflexo=False))
        assert p.n == 1, motivo
    e = estado()
    suspender(e)
    p = Plast()
    _creditar(p, e.cuidar_suspensa(sens(objetos=((3, "racao", 80),)), FOME, reflexo=False))
    assert p.n == 0


# ------------------------------------------------------------------ T-L2-5
def test_t_l2_5_o_tempo_suspenso_se_soma_na_vida_da_intencao():
    e = estado()
    suspender(e)                                                                     # n_susp 1
    assert e.cuidar_suspensa(sens(), FOME, reflexo=True) == []                       # 2
    assert e.cuidar_suspensa(sens(), FOME, reflexo=False) == []                      # a retomada
    e.contexto()
    assert e.escolhida(BUSCA, [0, 0, 0], 100, 4) == []
    e.consequencia(0, None, {"visto": True, "d": None, "ha_cheiro": True, "comida_boa_vista": False})
    e.contexto()
    assert e.escolhida(DORMIR, [0, 0, 0], 100, 5, reflexo=True) == [] and e.suspensa["n_susp"] == 3   # nao zera ao voltar
    for _ in range(P.n_suspensa_max - 3):
        assert e.cuidar_suspensa(sens(), FOME, reflexo=True) == []
    fins = e.cuidar_suspensa(sens(), FOME, reflexo=True)
    assert [f["motivo"] for f in fins] == ["expirou"] and fins[0]["n_susp"] == P.n_suspensa_max + 1


# ------------------------------------------------------------------ T-L2-6
def test_t_l2_6_o_credito_e_a_elegibilidade_do_comeco_e_o_r_so_das_decisoes_dela():
    e = estado()
    suspender(e)                       # a busca soma r = 10; o cochilo (r = 50) e uma opcao de uma decisao
    fins = e.cuidar_suspensa(sens(cheiro=False), FOME, reflexo=False)
    assert fins[0]["e"] == [1, 2, 3] and fins[0]["r"] == 10 and fins[0]["inicio"] == 0


# ------------------------------------------------------------------ T-L2-7
@pytest.mark.parametrize("unidade", [{"chave": ("brincar", "bola", 1), "d": 50}, {"chave": ("explorar", "ponto", (10, 10)), "d": 500}])
def test_t_l2_7_o_que_nao_suspende_troca_como_hoje(unidade):
    e = estado()
    e.contexto()
    e.escolhida(unidade, [1, 1, 1], 100, 0)
    e.consequencia(0, None, {"visto": True, "d": unidade["d"], "ha_cheiro": True, "comida_boa_vista": False})
    e.contexto()
    fins = e.escolhida(DORMIR, [0, 0, 0], 100, 1, reflexo=True)
    assert [f["motivo"] for f in fins] == ["trocou"] and e.suspensa is None


def test_t_l2_7_o_dormir_pelo_sorteio_troca_como_hoje():
    e = estado()
    e.contexto()
    e.escolhida(BUSCA, [1, 1, 1], 100, 0)
    e.consequencia(0, None, {"visto": True, "d": None, "ha_cheiro": True, "comida_boa_vista": False})
    e.contexto()
    fins = e.escolhida(DORMIR, [0, 0, 0], 100, 1, reflexo=False)
    assert [f["motivo"] for f in fins] == ["trocou"] and e.suspensa is None


# ------------------------------------------------------------------ T-L2-8
def test_t_l2_8_o_m_estado_nao_tem_rng_e_so_le_se_ha_cheiro():
    arvore = ast.parse(Path(estado_mod.__file__).read_text(encoding="utf-8"))
    nomes = {n.id for n in ast.walk(arvore) if isinstance(n, ast.Name)} | {a.arg for a in ast.walk(arvore) if isinstance(a, ast.arg)}
    importados = {a.name for n in ast.walk(arvore) if isinstance(n, (ast.Import, ast.ImportFrom)) for a in n.names}
    assert "rng" not in nomes and "random" not in importados
    assert "rng" not in inspect.signature(EstadoDinamico.cuidar_suspensa).parameters
    assert "direcao_cheiro" not in Path(estado_mod.__file__).read_text(encoding="utf-8")
    e = estado()
    suspender(e)
    e.cuidar_suspensa({"ha_cheiro": True, "objetos": []}, FOME, reflexo=False)      # sem a direcao: so se ha cheiro


# ------------------------------------------------------------------ as vidas (sementes dos testes)
@pytest.fixture
def com_suspensa(monkeypatch):
    original = orq.config_do_braco
    monkeypatch.setattr(orq, "config_do_braco", lambda b, g=None, c=False: replace(original(b, g, c), intencao_suspensa=True))


def test_t_l2_8_a_vida_com_a_subchave_e_determinista_e_a_rng_e_so_a_do_m_arb(com_suspensa):
    motor, reg, (fp, fm) = orq.viver("M3", "atencioso", "longe", 101, 4, orq.ORCAMENTO_POR_DIA, conserto=True)
    c = orq.cerebro_de(reg)
    assert c.m.estado.suspensas > 0 and c.m.estado.retomadas > 0 and all("suspensa" in m for m in c.motivos)
    assert sum(m["retomou"] for m in c.motivos) == c.m.estado.retomadas                 # o registro das S-4 e S-6
    assert any("n_susp" in f for m in c.motivos for f in m["fins"])                     # o das S-1 e S-2
    r = orq.reproduzir_mundo(LogDeEventos.de_jsonl(motor.log.para_jsonl()), fp, semente=101, fabrica_motor=fm)
    assert r.log.para_jsonl() == motor.log.para_jsonl()
    assert json.dumps(r.politica.estado_interno(), sort_keys=True) == json.dumps(c.estado_interno(), sort_keys=True)
    assert c.m.arb.sorteios == sum(1 for m in c.motivos if m["u"] is not None)


def test_t_l2_9_o_reflexo_extraido_e_a_conta_de_hoje(monkeypatch):
    vistos = []
    original = arb_mod.Arbitragem.reflexo

    def anotar(self, s):
        r = original(self, s)
        vistos.append((s["leitura"]["energia"] < self.p.lambda_sono, r))
        return r

    monkeypatch.setattr(arb_mod.Arbitragem, "reflexo", anotar)
    for braco in ("M0", "M3"):
        vistos.clear()
        _motor, reg, _ = orq.viver(braco, "atencioso", "longe", 202, 3, orq.ORCAMENTO_POR_DIA, conserto=True)
        ms = orq.cerebro_de(reg).motivos
        assert len(vistos) == len(ms) and any(r for _, r in vistos)
        assert all(a == r for a, r in vistos) and [r for _, r in vistos] == [m["reflexo"] for m in ms]


def test_t_l2_desligada_a_vida_nao_tem_campo_novo():
    _motor, reg, _ = orq.viver("M3", "atencioso", "longe", 101, 2, orq.ORCAMENTO_POR_DIA, conserto=True)
    c = orq.cerebro_de(reg)
    assert not any("suspensa" in m or "retomou" in m for m in c.motivos) and "suspensa" not in c.estado_interno()["modulos"]["estado"]
    assert not any("n_susp" in f for m in c.motivos for f in m["fins"])


# ------------------------------------------------------------------ o registro da avaliacao (o adendo 5), antes de qualquer vida
def test_o_adendo_5_esta_no_plano_aprovado_e_a_trava_o_aceita():
    """o adendo 5 foi registrado PROPOSTO (o #437) e APROVADO pelo Matheus em 2026-10-29 (o PR das fases da L-2)"""
    plano = (RAIZ / "docs" / "PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md").read_text(encoding="utf-8")
    orq.exigir_adendo_aprovado(plano, 4)                                             # a trava da reavaliacao segue valendo
    orq.exigir_adendo_aprovado(plano, 5)
    with pytest.raises(RuntimeError, match="nao esta APROVADO"):
        orq.exigir_adendo_aprovado(plano.replace("**Status: APROVADO pelo Matheus em 2026-10-29,** com o piloto",
                                                 "**Status: PROPOSTO,** com o piloto"), 5)
    texto = plano[plano.index("## Adendo 5:"):]
    for c in ("C-L2-1", "C-L2-2", "C-L2-3", "C-L2-4", "67101", r"M3\*+S", "M0+S"):
        assert c in texto, c


def test_a_faixa_da_l2_esta_reservada_e_nao_colide():
    import bancada_v2 as bv
    faixas = {(a, b): f for a, b, f in bv.FAIXAS_RESERVADAS}
    assert (67101, 67505) in faixas and "adendo 5" in faixas[(67101, 67505)]
    for a, b in faixas:
        if (a, b) != (67101, 67505):
            assert b < 67101 or a > 67505, (a, b)


def test_o_poder_da_l2_se_refaz_igual():
    import bancada_v2 as bv
    import poder_l2_digibrain as pw
    assert pw.SAIDA.read_text(encoding="utf-8") == bv._dump(pw.calcular(json.loads(pw.ENTRADA.read_text(encoding="utf-8"))))
