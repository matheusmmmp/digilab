"""C4, o `controle_mem` (docs/ESPEC_MEMORIA_AUTOBIOGRAFICA_DIGIBRAIN_MODULAR.md, secoes 7.2 e 9; MA-3): os cinco bracos da memoria
autobiografica, antes de qualquer vida de pesquisa. So as sementes 101 a 505 e sequencias sinteticas.

  - a chave: `controle_mem` nasce "rel", so aceita a lista, e so diferente de "rel" com a `memoria_autobio`;
  - cada braco faz o que a tabela 7.2 diz (a lembranca, o lugar, o sigma);
  - o "rel" e a vida de hoje com a chave ligada (a mesma da `memoria_autobio` sozinha);
  - a rng: o "emb" tem a propria (`derivar_semente(semente, "mem_emb")`) e nao consome a de politica; os outros bracos nao tem rng;
  - o replay bit a bit de cada braco, nas cinco sementes."""
from __future__ import annotations

import json
import random
import sys
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import run_v2_digibrain_prototipo as orq  # noqa: E402
import test_memoria_autobio as ta  # noqa: E402

from digilab.config import CONTROLES_MEM, CONFIG_MUNDO_LIGADA, ConfigDigibrain  # noqa: E402
from digilab.digibrain import mem as M  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402

SEMENTES = ta.SEMENTES
S = ta.S
BRACOS = CONTROLES_MEM


def memoria(controle: str, semente: int | None = 101) -> M.Memoria:
    return M.Memoria(CONFIG_MUNDO_LIGADA, autobio=True, controle=controle,
                    rng_emb=None if semente is None else random.Random(derivar_semente(semente, "mem_emb")))


# ------------------------------------------------------------------ a chave
def test_a_chave_nasce_rel_e_a_lista_e_a_da_espec():
    assert ConfigDigibrain().controle_mem == "rel"
    assert CONTROLES_MEM == ("rel", "sem", "rec", "emb", "rel_sem_neg")
    for b in BRACOS:
        assert replace(ta.LIGADA, controle_mem=b).controle_mem == b


@pytest.mark.parametrize("valor", ["REL", "embaralhado", "", None, 1])
def test_valor_fora_da_lista_falha_alto(valor):
    with pytest.raises(ValueError):
        replace(ta.LIGADA, controle_mem=valor)


@pytest.mark.parametrize("braco", [b for b in BRACOS if b != "rel"])
def test_braco_diferente_de_rel_sem_a_memoria_autobio_falha_alto(braco):
    with pytest.raises(ValueError):
        replace(ta.BASE, controle_mem=braco)
    assert replace(ta.BASE, controle_mem="rel").controle_mem == "rel"
    with pytest.raises(ValueError):
        M.Memoria(CONFIG_MUNDO_LIGADA, autobio=False, controle=braco)


def test_o_emb_pede_a_semente():
    with pytest.raises(ValueError):
        memoria("emb", None)


def test_desligada_o_estado_nao_tem_campo_novo_e_o_rel_tambem_nao():
    assert "autobio" not in M.Memoria(CONFIG_MUNDO_LIGADA).estado_interno()
    assert "controle" not in memoria("rel").estado_interno()["autobio"]
    assert memoria("sem").estado_interno()["autobio"]["controle"] == {"braco": "sem"}
    assert memoria("emb").estado_interno()["autobio"]["controle"] == {"braco": "emb", "sorteios": 0}


# ------------------------------------------------------------------ a lembranca de cada braco (7.2)
def _tres(mem):
    """tres episodios: um bom longe (mais antigo), um bom perto da pista, um ruim recente em outro lugar"""
    a = ta.guardar(mem, 500, ponto=(300, 100), unid=ta.COMER, comeu="a", decisao=1)
    b = ta.guardar(mem, 300, ponto=(40, 72), objetos=[ta.COMIDA], decisao=2)
    c = ta.guardar(mem, -400, ponto=(400, 100), unid=ta.COMER, comeu="podre", decisao=3)
    return a, b, c


def test_rel_lembra_o_mais_parecido():
    mem = memoria("rel")
    _, b, _ = _tres(mem)
    assert mem.lembrar(ta.pista(objetos=[ta.COMIDA]))["recuperado"] == b


def test_sem_nunca_le_a_lembranca_nem_o_lugar_mas_o_episodio_e_guardado():
    mem = memoria("sem")
    _tres(mem)
    rec = mem.lembrar(ta.pista(objetos=[ta.COMIDA]))
    assert rec == {"recuperado": None, "sim": 0, "memoria": None, "sigma": 0}
    assert mem.termo_lembranca(rec) is None and mem.lembrancas == 0 and all(e["rec"] == 0 for e in mem.recente)
    assert mem.valores_soma() == {} and mem.recuperar(ta.SEM, ta.FOME)["recuperado"] is None
    assert len(mem.recente) == 3                                                 # codificado e consolidado
    ta.virar_dia(mem)
    assert mem.consolidar(1000) is not None


def test_rec_lembra_o_mais_recente_sem_olhar_o_contexto():
    mem = memoria("rec")
    a, b, c = _tres(mem)
    rec = mem.lembrar(ta.pista(objetos=[ta.COMIDA]))                           # a pista casa com o b; o braco volta o c
    assert rec["recuperado"] == c and mem.recente[2]["rec"] == 1 and mem.lembrancas == 1
    assert mem.lembrar(ta.pista(pos=(900, 900)))["recuperado"] == c
    mover = mem.recente[2]
    ta.mover(mem, mover, "duradoura")                                            # o mais recente das tres memorias
    assert mem.lembrar(ta.pista())["recuperado"] == c


def test_rec_o_lugar_e_o_do_consumo_bom_mais_recente():
    mem = memoria("rec")
    a, b, c = _tres(mem)
    v = mem.valores_soma()
    assert list(v) == [(300 // mem.sub, 100 // mem.sub)] and v[next(iter(v))][0] == 500        # o a: o ruim e o evento nao contam
    rec = mem.recuperar(ta.SEM, ta.FOME)
    assert rec["recuperado"] == a and rec["valor"] == 500
    d = ta.guardar(mem, 200, ponto=(400, 100), unid=ta.COMER, comeu="b", decisao=9)
    assert mem.recuperar(ta.SEM, ta.FOME)["recuperado"] == d and mem.recuperar(ta.SEM, ta.FOME)["valor"] == 200


def test_rec_sem_consumo_bom_nao_tem_lugar():
    mem = memoria("rec")
    ta.guardar(mem, 500, ponto=(400, 100), unid=ta.COMER, comeu="podre")
    assert mem.valores_soma() == {}


def test_emb_sorteia_entre_os_guardados_pela_rng_propria():
    mem = memoria("emb", 202)
    _tres(mem)
    ref = random.Random(derivar_semente(202, "mem_emb"))
    guardados = list(mem.recente)
    esperado = [guardados[ref.randrange(3)]["id"] for _ in range(6)]
    obtido = [mem.lembrar(ta.pista(objetos=[ta.COMIDA]))["recuperado"] for _ in range(6)]
    assert obtido == esperado and mem.sorteios == 6 and mem.lembrancas == 6
    assert len(set(obtido)) > 1                                                  # nao e o mais parecido


def test_emb_sem_guardado_nao_sorteia():
    mem = memoria("emb")
    assert mem.lembrar(ta.pista())["recuperado"] is None and mem.sorteios == 0


def test_emb_o_lugar_e_o_do_sorteado_se_for_consumo_bom():
    mem = memoria("emb", 303)
    a, b, c = _tres(mem)
    vistos = {"bom": 0, "nao": 0}
    for _ in range(40):
        rec = mem.lembrar(ta.pista())
        v = mem.valores_soma()
        e = next(x for x in mem.recente if x["id"] == rec["recuperado"])
        if e["origem"] == "consumo" and e["classe"] == "a":
            assert list(v) == [tuple(e["lugar"])] and v[tuple(e["lugar"])][0] == 500
            vistos["bom"] += 1
        else:
            assert v == {}
            vistos["nao"] += 1
    assert vistos["bom"] and vistos["nao"]


def test_rel_sem_neg_grava_sigma_negativo_como_zero_e_o_resto_como_e():
    mem = memoria("rel_sem_neg")
    ta.guardar(mem, 500, ponto=(400, 100), unid=ta.COMER, comeu="a", decisao=0)
    neg = ta.guardar(mem, -400, ponto=(400, 100), unid=ta.COMER, comeu="podre", decisao=1)
    visita = ta.guardar(mem, 0, **ta.ida_vazia((402, 101), -300), decisao=2)
    pos = ta.guardar(mem, 250, ponto=(40, 72), unid=ta.COMER, comeu="b", decisao=3)
    por_id = {e["id"]: e for e in mem.recente}
    assert por_id[0]["sigma"] == 500 and por_id[pos]["sigma"] == 250
    assert por_id[neg]["sigma"] == 0 and por_id[visita]["sigma"] == 0
    assert por_id[neg]["categoria"][2] == -1                                    # os mesmos episodios, so sem o sinal (MA-3)
    assert mem.valores_soma()[(400 // mem.sub, 100 // mem.sub)][0] == 500       # a visita pesa 0 (T-ME-VISITA)


def test_rel_sem_neg_lembra_e_localiza_como_o_rel():
    a, b = memoria("rel"), memoria("rel_sem_neg")
    for m in (a, b):
        ta.guardar(m, 300, ponto=(40, 72), objetos=[ta.COMIDA], decisao=2)
    assert a.lembrar(ta.pista(objetos=[ta.COMIDA])) == b.lembrar(ta.pista(objetos=[ta.COMIDA]))
    assert a.termo_lembranca({"recuperado": 0}) == b.termo_lembranca({"recuperado": 0})


def test_t_me_visita_o_rel_pesa_a_visita_e_o_sem_neg_nao():
    rel, sn = memoria("rel"), memoria("rel_sem_neg")
    for m in (rel, sn):
        ta.guardar(m, 500, ponto=(400, 100), unid=ta.COMER, comeu="a", decisao=0)
        ta.guardar(m, 0, **ta.ida_vazia((402, 101), -900), decisao=1)
    assert rel.recuperar(ta.SEM, ta.FOME)["recuperado"] is None                 # a soma muda a escolha (o lugar fica negativo)
    assert sn.recuperar(ta.SEM, ta.FOME)["valor"] == 500                         # a visita pesa 0


def test_so_o_emb_tem_rng():
    import inspect
    fonte = inspect.getsource(M)
    assert fonte.count("self._rng_emb.") == 1 and "import random" not in fonte    # um unico sorteio, na lembranca do emb
    for b in BRACOS:
        assert hasattr(memoria(b), "_rng_emb") == (b == "emb")


# ------------------------------------------------------------------ as vidas
def _viver(braco: str, semente: int, lugar: str = "longe_fixo"):
    original = orq.config_do_braco
    orq.config_do_braco = lambda b, g=None, c=False: replace(original(b, g, c), memoria_autobio=True, controle_mem=braco)
    try:
        motor, reg, fab = orq.viver("M3", "relapso", lugar, semente, 3, 16, conserto=True)
    finally:
        orq.config_do_braco = original
    return motor, reg, fab


@pytest.mark.parametrize("semente", SEMENTES)
@pytest.mark.parametrize("braco", BRACOS)
def test_g1_o_replay_bit_a_bit_de_cada_braco(braco, semente):
    motor, reg, fab = _viver(braco, semente)
    orq.conferir_replay(motor, fab, semente, motor.log.para_jsonl())
    c = orq.cerebro_de(reg)
    assert c.cd.controle_mem == braco
    est = c.m.mem.estado_interno()["autobio"]
    assert ("controle" in est) == (braco != "rel")
    if braco == "sem":
        assert est["lembrancas"] == 0
    if braco == "emb":
        assert est["controle"]["sorteios"] > 0


@pytest.mark.parametrize("semente", (101, 303))
def test_o_rel_e_a_vida_de_hoje_com_a_chave_ligada(semente):
    """a vida do braco "rel" e a da `memoria_autobio` sozinha, byte a byte (log e estado interno)"""
    sozinha = ta._viver(semente)
    motor, reg, _ = _viver("rel", semente)
    assert motor.log.para_jsonl() == sozinha[0].log.para_jsonl()
    dump = lambda r: json.dumps(orq.cerebro_de(r).estado_interno(), sort_keys=True)   # noqa: E731
    assert dump(reg) == dump(sozinha[1])


def test_trocar_o_braco_nao_muda_o_mundo_nem_a_rng_de_politica():
    """o "emb" tem rng propria: a rng de politica faz as mesmas chamadas que a do "rel" quando o cerebro escolhe igual; aqui, que o mundo
    (o motor) nao depende do braco e que a politica nao sorteia mais que uma vez por decisao"""
    for braco in ("rel", "emb", "sem"):
        motor, reg, _ = _viver(braco, 101)
        c = orq.cerebro_de(reg)
        assert c.m.arb.sorteios <= len(c.motivos)
    em = _viver("emb", 101)
    a = orq.cerebro_de(em[1])
    # o sorteio do emb nao e da rng de politica: sao fluxos distintos (as sementes derivam de rotulos diferentes)
    assert derivar_semente(101, "mem_emb") != 101 and a.m.mem._rng_emb is not None


def test_a_rng_de_politica_nao_e_tocada_pelo_emb_numa_sequencia_sintetica():
    """a mesma sequencia de lembrancas com a rng de politica contada: o M-MEM nunca recebe a rng de politica"""
    mem = memoria("emb", 505)
    _tres(mem)
    contada = ta.RngContada(0.5)
    for _ in range(10):
        mem.lembrar(ta.pista())
        mem.valores_soma()
        mem.recuperar(ta.SEM, ta.FOME)
    assert contada.n == 0
