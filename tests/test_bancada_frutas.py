"""V2, BANCADA-FRUTAS (docs/TAREFA_V2_BANCADA_FRUTAS.md): os mundos das frutas na bancada e as unidades derivadas (E3).

Gates: G1 de toda vida dos mundos novos; casado x descasado com as mesmas ofertas, diferindo so no sinal do efeito; no mutavel a
troca aparece no registro e o replay a refaz; as unidades derivadas nao colidem com nenhuma faixa reservada ou ja usada.
Sementes: so as dos testes (101...505). As bases reservadas do experimento maior so entram em contas, nunca em vida."""

import json
import sys
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
from digilab.config import CONFIG_BOLA, CONFIG_FRUTAS_LIGADA, CONFIG_INFORMACAO_LIGADA, TICKS_POR_DIA  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.events import ACOES_FRUTAS, ACOES_V1, FRUTAS, LogDeEventos  # noqa: E402
from digilab.frutas import GenomaFrutas, MotorFrutas, PoliticaInstintoFrutas, genoma_frutas  # noqa: E402
from digilab.metrics import taxa_fruta_ruim  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402
from digilab.temperamento import NEUTRO  # noqa: E402

DONOS = ("atencioso", "relapso", "aleatorio", "incoerente")
DIAS, ORC = 4, 64
BANCADA = bv.Bancada(DIAS, ORC)
SONDA = {"estados": 20, "amostras": 20, "semente": 101}
MUNDOS_FRUTAS = ("casado_frutas", "descasado", "mutavel")
OFERTAS = {a.value for a in ACOES_FRUTAS}


def _ofertas(log) -> list[tuple[int, str]]:
    return [(e.tick, str(e.valor)) for e in log if e.tipo == "acao_usuario" and str(e.valor) in OFERTAS]


def _vida(dono="atencioso", braco="P0", s=101, mundo="casado_frutas", cerebro="instinto", genoma=None, bancada=BANCADA):
    return bancada.vida(bv.EspecVida(dono, braco, s, genoma, mundo, cerebro))


# ------------------------------------------------------------------ o efeito por condicao


def test_efeitos_casado_e_descasado_so_trocam_o_sinal():
    for s in (101, 202, 303, 404, 505):
        g = genoma_frutas(s, CONFIG_FRUTAS_LIGADA)
        c = bv.efeitos_da_condicao(g, CONFIG_FRUTAS_LIGADA, "casado")
        d = bv.efeitos_da_condicao(g, CONFIG_FRUTAS_LIGADA, "descasado")
        assert all(c[f] == -d[f] for f in FRUTAS)
        ruim = CONFIG_FRUTAS_LIGADA.efeito_humor_ruim
        assert sorted(c.values()) == sorted(d.values()) == [ruim, CONFIG_FRUTAS_LIGADA.efeito_humor_neutro, -ruim]
        pref = g.fruta_preferida()
        menor = min(FRUTAS, key=lambda f: g.preferencia_inata[f])
        assert c[pref] == -ruim and c[menor] == ruim                 # casado: a preferida faz bem, a rejeitada faz mal
        assert d[pref] == ruim and d[menor] == -ruim                 # descasado: o contrario
    with pytest.raises(ValueError):
        bv.efeitos_da_condicao(genoma_frutas(101, CONFIG_FRUTAS_LIGADA), CONFIG_FRUTAS_LIGADA, "mutavel")
    with pytest.raises(ValueError):
        bv.efeitos_da_condicao(GenomaFrutas(0.5, {f: 0.5 for f in FRUTAS}), CONFIG_FRUTAS_LIGADA, "casado")
    with pytest.raises(ValueError):
        bv.efeitos_da_condicao(genoma_frutas(101, CONFIG_FRUTAS_LIGADA), replace(CONFIG_FRUTAS_LIGADA, efeito_humor_ruim=0.1),
                               "casado")


# ------------------------------------------------------------------ gate: as mesmas ofertas, so o sinal muda


@pytest.mark.parametrize("dono", DONOS)
def test_casado_e_descasado_com_as_mesmas_ofertas_so_o_sinal_muda(dono):
    for s, g in ((101, None), (303, 303)):
        vidas = {(m, c, b): _vida(dono, b, s, m, c, g) for m in MUNDOS_FRUTAS for c, b in
                 (("instinto", "P0"), ("lobos", "P0"), ("lobos", "P3"))}
        ofertas = {k: _ofertas(v.motor.log) for k, v in vidas.items()}
        ref = ofertas[("casado_frutas", "instinto", "P0")]
        assert ref and all(o == ref for o in ofertas.values())        # mundo, cerebro e braco: as mesmas ofertas
        for c, b in (("instinto", "P0"), ("lobos", "P0"), ("lobos", "P3")):
            mc, md = vidas[("casado_frutas", c, b)].motor, vidas[("descasado", c, b)].motor
            assert mc.genoma == md.genoma
            assert all(mc.efeito_humor[f] == -md.efeito_humor[f] for f in FRUTAS)
            assert mc.resumo_mundo()["efeitos"] == md.resumo_mundo()["efeitos"]   # as duas tabelas, a vigente muda
            assert (mc.efeito_vigente, md.efeito_vigente) == ("casado", "descasado")


def test_ofertas_fora_do_orcamento_e_do_sorteio_do_aleatorio():
    for dono in DONOS:
        v = _vida(dono, mundo="descasado")
        n_dono, n_mundo = bv.contar_acoes(v.motor.log)
        assert n_dono == ORC == v.interacoes and n_mundo == len(_ofertas(v.motor.log)) > 0
        if dono == "aleatorio":
            dono_acoes = {str(e.valor) for e in v.motor.log if e.tipo == "acao_usuario" and str(e.valor) not in OFERTAS}
            assert dono_acoes <= {a.value for a in ACOES_V1}        # B1: o sorteio dele e o da v1
    # o calendario sai da semente: igual entre donos, diferente entre sementes
    assert _ofertas(_vida("aleatorio").motor.log) == _ofertas(_vida("atencioso").motor.log)
    inicios = {bv.CalendarioFrutas(s, CONFIG_FRUTAS_LIGADA).k for s in (101, 202, 303, 404, 505)}
    assert len(inicios) > 1


def test_p0_lobos_e_o_instinto_que_ve_as_frutas():
    """Desde a BANCADA-N5 os lobos veem as frutas (LOBOS-MUNDO): no mundo das frutas o P0 com lobos e o instinto das frutas, no
    mesmo motor e com as mesmas ofertas (o gate de fato fica em tests/test_bancada_n5.py)."""
    for s in (101, 404):
        for mundo in MUNDOS_FRUTAS:
            espec = bv.EspecVida("atencioso", "P0", s, mundo=mundo)
            lob = BANCADA.vida(espec)
            ref = bv.simular_vida_mundo(criar_dono("atencioso"), bv.CalendarioFrutas(s, CONFIG_FRUTAS_LIGADA),
                                        PoliticaInstintoFrutas(None, CONFIG_BOLA, CONFIG_FRUTAS_LIGADA), s, DIAS, ORC, "atencioso",
                                        BANCADA.fabrica_motor(espec))
            assert bv.resumo_motor(lob.motor)[:5] == bv.resumo_motor(ref)[:5]


def test_o_motor_do_mundo_so_muda_o_efeito():
    """MotorFrutasMundo = MotorFrutas com o efeito trocado: dando ao MotorFrutas o mesmo efeito, a vida e a mesma."""
    for mundo in ("casado_frutas", "descasado"):
        espec = bv.EspecVida("incoerente", "P0", 202, mundo=mundo, cerebro="instinto")
        v = BANCADA.vida(espec)

        def fm(politica, cfg, semente):
            m = MotorFrutas(politica, cfg, semente, NEUTRO, "brasa", obediencia_desligada=True, cfg_bola=CONFIG_BOLA,
                            cfg_frutas=CONFIG_FRUTAS_LIGADA, cfg_informacao=CONFIG_INFORMACAO_LIGADA)
            m.efeito_humor = dict(v.motor.efeito_humor)
            return m

        ref = bv.simular_vida_mundo(criar_dono("incoerente"), bv.CalendarioFrutas(202, CONFIG_FRUTAS_LIGADA),
                                    PoliticaInstintoFrutas(None, CONFIG_BOLA, CONFIG_FRUTAS_LIGADA), 202, DIAS, ORC,
                                    "incoerente", fm)
        assert ref.log.para_jsonl() == v.motor.log.para_jsonl() and ref.resumo_frutas() == v.motor.resumo_frutas()
        assert ref.estado() == v.motor.estado()


# ------------------------------------------------------------------ gate: a troca do mutavel


def test_mutavel_troca_no_registro_e_o_replay_a_refaz():
    T = BANCADA.tick_troca
    assert T == (DIAS // 2) * TICKS_POR_DIA
    for dono, s, g in (("atencioso", 101, None), ("relapso", 505, 505)):
        mut = _vida(dono, s=s, mundo="mutavel", genoma=g)
        cas = _vida(dono, s=s, mundo="casado_frutas", genoma=g)
        des = _vida(dono, s=s, mundo="descasado", genoma=g)
        t = mut.motor.troca
        assert t["tick"] == T and (t["de"], t["para"]) == ("casado", "descasado")
        assert t["efeito_antes"] == cas.motor.efeito_humor and t["efeito_depois"] == des.motor.efeito_humor
        assert mut.motor.efeito_vigente == "descasado"
        # antes da troca o mutavel e o casado: os mesmos eventos e os mesmos consumos
        assert [e for e in mut.motor.log if e.tick < T] == [e for e in cas.motor.log if e.tick < T]
        antes = [c for c in mut.motor.consumos if c["tick"] < T]
        assert antes == [c for c in cas.motor.consumos if c["tick"] < T]
        depois = [c for c in mut.motor.consumos if c["tick"] >= T]
        assert all(c["efeito_humor"] == des.motor.efeito_humor[c["fruta"]] for c in depois)
        assert depois, "nenhum consumo depois da troca"
        # o replay refaz a troca
        r = BANCADA.rejogar(LogDeEventos.de_jsonl(mut.motor.log.para_jsonl()), mut.espec)
        assert r.troca == t and bv.resumo_motor(r) == bv.resumo_motor(mut.motor)
    with pytest.raises(ValueError):
        bv.Bancada(1, 16).tick_troca


# ------------------------------------------------------------------ gate: G1 e acoplado nos mundos das frutas


def test_g1_replay_bit_a_bit_dos_mundos_das_frutas():
    vidas = [_vida(d, b, s, m, c, g) for m in MUNDOS_FRUTAS for d in ("atencioso", "aleatorio") for s, g in ((101, None), (202, 202))
             for b, c in (("P0", "instinto"), ("P0", "lobos"), ("P1", "lobos"), ("P3", "lobos"))]
    vidas += [BANCADA.acoplar(v, "P0", "sem_sinais") for v in vidas if v.espec.braco == "P3"]
    for v in vidas:
        BANCADA.conferir_replay(v)
        r = BANCADA.rejogar(LogDeEventos.de_jsonl(v.motor.log.para_jsonl()), v.espec)
        assert bv.resumo_motor(r) == bv.resumo_motor(v.motor) and r.estado() == v.motor.estado()
    with pytest.raises(bv.ReplayDivergiu):
        BANCADA.conferir_replay(bv.VidaBancada(vidas[1].espec, vidas[0].motor, ORC))


@pytest.mark.parametrize("mundo", MUNDOS_FRUTAS)
def test_acoplado_guarda_as_ofertas(mundo):
    origem = _vida("atencioso", "P3", 303, mundo, "lobos")
    a = BANCADA.acoplar(origem, "P0", "sem_sinais")
    assert _ofertas(a.motor.log) == _ofertas(origem.motor.log) and a.eventos_mundo == origem.eventos_mundo
    assert not any(e.tipo == "acao_usuario" and str(e.valor) in bv.SINAIS for e in a.motor.log)
    mesma = BANCADA.acoplar(origem, "P3", "nenhum")
    assert bv.resumo_motor(mesma.motor) == bv.resumo_motor(origem.motor)
    with pytest.raises(ValueError, match="eventos do mundo"):
        bv.filtrar_log(origem.motor.log, frozenset({ACOES_FRUTAS[0].value}))


# ------------------------------------------------------------------ medidas


def test_taxa_fruta_ruim():
    consumos = [(10, -0.1), (20, 0.1), (30, 0.0), (1500, -0.1), (1600, -0.1)]
    t = taxa_fruta_ruim(consumos, {"inicio": (0, 1440), "final": (1440, 2880), "vazia": (2880, 4320)})
    assert t["inicio"] == {"inicio": 0, "fim": 1440, "n": 3, "ruins": 1, "taxa": 1 / 3}
    assert t["final"]["taxa"] == 1.0 and t["vazia"] == {"inicio": 2880, "fim": 4320, "n": 0, "ruins": 0, "taxa": None}
    for janela in ((10, 10), (-1, 5), (0.0, 10)):
        with pytest.raises(ValueError):
            taxa_fruta_ruim(consumos, {"x": janela})


def test_medir_nos_mundos_das_frutas():
    for mundo in MUNDOS_FRUTAS:
        v = _vida("atencioso", "P0", 404, mundo, "instinto")
        m = BANCADA.medir(v, SONDA)
        f = m["frutas"]
        janelas = set(BANCADA.janelas_frutas(v.motor.condicao))
        assert set(f["taxa_fruta_ruim"]) == janelas and f["consumos"] == len(v.motor.consumos) > 0
        assert ("antes_da_troca" in janelas) == (mundo == "mutavel")
        por_dia = [f["taxa_fruta_ruim"][f"dia_{d + 1}"]["n"] for d in range(DIAS)]
        assert sum(por_dia) == f["consumos"]
        assert f["taxa_fruta_ruim"]["inicio"]["n"] + f["taxa_fruta_ruim"]["final"]["n"] == f["consumos"]
        ruins = sum(c["efeito_humor"] < 0 for c in v.motor.consumos)
        assert f["taxa_fruta_ruim"]["inicio"]["ruins"] + f["taxa_fruta_ruim"]["final"]["ruins"] == ruins
        assert 0.0 <= m["humor_medio"] <= 1.0 and m["condicao"] == bv.MUNDOS[mundo].condicao
        assert BANCADA.medir(v, SONDA) == m                                  # medir nao muda a vida
    lob = BANCADA.medir(_vida("atencioso", "P0", 404, "descasado", "lobos"), SONDA)        # os lobos veem as frutas: comem
    ins = BANCADA.medir(_vida("atencioso", "P0", 404, "descasado", "instinto"), SONDA)
    assert lob["frutas"]["consumos"] == ins["frutas"]["consumos"] > 0
    assert lob["frutas"]["taxa_fruta_ruim"] == ins["frutas"]["taxa_fruta_ruim"]
    assert BANCADA.medir(_vida("atencioso", "P0", 404, "padrao", "lobos"), SONDA)["frutas"] is None


# ------------------------------------------------------------------ gate: unidades derivadas


def _sementes_das_configs() -> tuple[set[int], list[tuple[int, int]]]:
    pontos, faixas = set(), []

    def andar(o, chave=""):
        if isinstance(o, dict):
            for k, v in o.items():
                andar(v, k)
        elif isinstance(o, list):
            nums = [x for x in o if isinstance(x, int) and not isinstance(x, bool)]
            if nums and "semente" in chave.lower():
                faixas.append((min(nums), max(nums)))
            for v in o:
                andar(v, chave)
        elif isinstance(o, int) and not isinstance(o, bool) and "semente" in chave.lower():
            pontos.add(o)

    for p in (RAIZ / "experiments" / "configs").rglob("*.json"):
        andar(json.loads(p.read_text(encoding="utf-8")))
    return pontos, faixas


def test_unidades_derivadas_regra_e_sem_colisao():
    K = 200
    cal = bv.unidades_derivadas(bv.BASES_EXPERIMENTO_MAIOR["calibracao"], K)
    val = bv.unidades_derivadas(bv.BASES_EXPERIMENTO_MAIOR["validacao"], K)
    assert len(cal) == len(val) == 5 * K
    u = cal[7]
    assert u["semente"] == derivar_semente("experimento-maior", u["base"], u["k"])
    assert u["genoma"] == derivar_semente("experimento-maior-genoma", u["base"], u["k"])
    assert [(x["base"], x["k"]) for x in cal[:3]] == [(14101, 0), (14101, 1), (14101, 2)]
    todos = [x["semente"] for x in cal + val] + [x["genoma"] for x in cal + val]
    assert len(set(todos)) == len(todos)                                        # nenhuma colisao, nem cal x val
    pontos, faixas = _sementes_das_configs()
    assert pontos and faixas
    for v in todos:
        assert bv.na_faixa_reservada(v) is None, v
        assert v not in pontos and not any(lo <= v <= hi for lo, hi in faixas), v
        assert v not in bv.SEMENTES_TESTE
    # as bases reservadas estao na tabela de faixas
    assert all(bv.na_faixa_reservada(b) for bs in bv.BASES_EXPERIMENTO_MAIOR.values() for b in bs)
    with pytest.raises(ValueError):
        bv.unidades_derivadas((14101,), 0)
    with pytest.raises(ValueError):
        bv.unidades_derivadas((14101, 14101), 1)


def test_config_com_unidades(tmp_path):
    base = {"descricao": "fumaca de teste, nao canonica", "bracos": ["P0"], "donos": ["atencioso", "aleatorio"],
            "mundos": ["casado_frutas", "descasado"], "dias": 2, "orcamento": 32,
            "sonda": {"estados": 10, "amostras": 10, "semente": 101},
            "bootstrap": {"reamostragens": 200, "semente": 101, "nivel": 0.95}}
    with pytest.raises(ValueError):
        bv.validar_config({**base, "sementes": [101], "unidades": {"bases": [101], "k": 1}})
    with pytest.raises(ValueError):
        bv.validar_config({**base, "unidades": {"bases": [101], "k": 1}, "genomas": [101]})
    with pytest.raises(bv.SementeSemPlano):
        bv.validar_config({**base, "unidades": {"bases": [14101], "k": 2}})
    bv.validar_config({**base, "unidades": {"bases": [14101], "k": 2}, "plano": "docs/PLANO_ANALISE_V2_EXPERIMENTO_MAIOR.md"})
    r = bv.rodar({**base, "unidades": {"bases": [101, 202], "k": 1}}, tmp_path)   # bases dos testes: sem plano
    us = bv.unidades_derivadas([101, 202], 1)
    assert len(r["vidas"]) == 2 * 2 * 2
    for m in r["medidas"].values():
        assert m["unidade"] in [{"base": u["base"], "k": u["k"]} for u in us]
        assert (m["semente"], m["genoma"]) in [(u["semente"], u["genoma"]) for u in us]
    t = json.loads((tmp_path / "tabelas.json").read_text(encoding="utf-8"))
    assert t["atencioso"]["humor_medio"]["condicoes"] == ["casado/casado_frutas", "descasado/descasado"]
