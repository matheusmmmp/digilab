"""BANCADA-K4-CANAIS (docs/TAREFA_V2_BANCADA_K4_CANAIS.md): o K4 fora do orcamento no P3, os canais por braco, as ablacoes da K-7 e as
faixas da comparacao dos cerebros. Gates: os bracos de antes byte a byte (gabarito gravado antes); o P3 sem o julgamento e o P3 de hoje;
no P3 com o K4 o orcamento do dono fecha igual, ha um julgamento por consumo pelo efeito vigente (dos dois lados da troca do mutavel) e o
sem_ensino tira os julgamentos e guarda as ofertas; G1 de toda vida e acoplado novos. So as sementes dos testes."""

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import bancada_v2 as bv  # noqa: E402
import gabarito_bancada_k4 as gab  # noqa: E402
from digilab.events import ACOES_FRUTAS, AcaoUsuario, LogDeEventos  # noqa: E402

DIAS, ORC = 4, 64
LOBOS = {"memoria_ganho": 512}
K4 = bv.bancada_da_config({"dias": DIAS, "orcamento": ORC, "ponto": "T3", "lobos": LOBOS, "julgamento_fruta": True})
HOJE = bv.bancada_da_config({"dias": DIAS, "orcamento": ORC, "ponto": "T3", "lobos": LOBOS})
SONDA = {"estados": 5, "amostras": 5, "semente": 101}
OFERTAS = frozenset(a.value for a in ACOES_FRUTAS)
FRUTAS_MUNDOS = ("casado_frutas", "descasado", "mutavel")
ABLACOES = ("P1c", "P1c-mem", "P1c-can")


def _vida(bancada, braco, s=101, mundo="descasado", dono="atencioso", genoma=None):
    return bancada.vida(bv.EspecVida(dono, braco, s, genoma, mundo))


def _acoes(log, valores):
    return [(e.tick, str(e.valor)) for e in log if e.tipo == "acao_usuario" and str(e.valor) in valores]


# ------------------------------------------------------------------ os bracos de antes byte a byte


def test_bracos_de_antes_byte_a_byte_pelo_gabarito():
    """As 352 vidas do gabarito (gravado com o codigo da main antes desta tarefa, tests/gabarito_bancada_k4.py) saem iguais: os bracos
    P0 a P3, P2e, P2a, os do N6 e do N7, nos mundos das frutas e no padrao, e os acoplados. Sem a chave do K4, o P3 e o de hoje."""
    gravado = json.loads(gab.ARQUIVO.read_text(encoding="utf-8"))
    vistos = 0
    for nome, v in gab.casos():
        assert gab.impressao(v) == gravado[nome], nome
        vistos += 1
    assert vistos == len(gravado)


def test_a_chave_do_k4_e_os_canais_na_config_nao_mudam_quem_nao_e_do_dono():
    """Com o K4 ligado, so os bracos com fonte dono nos mundos das frutas mudam; com os canais ligados na config, o P0 e o P3 nao mudam
    (os canais so agem no sinal da consequencia). Fora das frutas, o P3 com a chave e o P3 de sempre."""
    gravado = json.loads(gab.ARQUIVO.read_text(encoding="utf-8"))
    com_k4 = bv.Bancada(4, 64, julgamento_fruta=True)
    canais = bv.bancada_da_config({"dias": 4, "orcamento": 64, "consequencia": {"canais_ligados": True}})
    for mundo in ("descasado", "padrao"):
        for b in (("P0", "P1", "P2") if mundo != "padrao" else ("P0", "P1", "P3")):
            v = _vida(com_k4, b, 101, mundo)
            assert gab.impressao(v) == gravado[f"L1|{v.nome}"], v.nome
    for b in ("P0", "P3"):
        v = _vida(canais, b, 202, "descasado", genoma=202)
        assert gab.impressao(v) == gravado[f"L1|{v.nome}"], v.nome
    assert not com_k4.julga_fruta(bv.EspecVida("atencioso", "P3", 101, mundo="padrao"))
    with pytest.raises(ValueError):
        com_k4.julgador(bv.EspecVida("atencioso", "P1", 101, mundo="descasado"))


# ------------------------------------------------------------------ o K4 no P3


def test_k4_fora_do_orcamento_e_um_julgamento_por_consumo_pelo_efeito_vigente():
    viu_troca = False
    for mundo in FRUTAS_MUNDOS:
        for dono in ("atencioso", "incoerente"):
            for s, g in ((101, None), (202, 202)):
                v, hoje = _vida(K4, "P3", s, mundo, dono, g), _vida(HOJE, "P3", s, mundo, dono, g)
                # o orcamento do dono fecha igual ao do P3 de hoje; os julgamentos ficam a parte
                assert v.interacoes == hoje.interacoes == ORC
                assert bv.contar_acoes(v.motor.log)[0] - v.julgamentos == ORC
                # um julgamento por consumo de fruta que nao e neutra, pelo efeito que o motor aplicou (o vigente no tick)
                consumos = v.motor.consumos
                assert v.julgamentos == sum(1 for c in consumos if c["efeito_humor"] != 0.0)
                julgador = K4.julgador(v.espec)
                for c in consumos:
                    assert julgador.sinal(c["fruta"], c["tick"]) == (1 if c["efeito_humor"] > 0 else -1 if c["efeito_humor"] < 0 else 0)
                if mundo == "mutavel" and consumos:
                    lados = {c["tick"] >= K4.tick_troca for c in consumos}
                    viu_troca = viu_troca or lados == {True, False}
                    if lados == {True, False}:      # o julgador troca junto com o mundo
                        assert julgador.efeitos_depois is not None and julgador.tick_troca == K4.tick_troca
    assert viu_troca


def test_o_julgamento_chega_ao_p3_e_o_conhecimento_e_o_do_p2():
    """O feedback do julgamento chega ao aprendiz do P3 (os sinais do dono passam do orcamento), e o dono do P3 conhece o mesmo efeito
    real que o informante do P2 da mesma unidade (K4, E7)."""
    for s in (101, 303):
        v, hoje = _vida(K4, "P3", s), _vida(HOJE, "P3", s)
        if v.julgamentos:
            assert bv.do_braco(v.motor.politica).sinais_entregues > bv.do_braco(hoje.motor.politica).sinais_entregues
        ef = K4.efeitos_reais(v.espec)
        j = K4.julgador(v.espec)
        assert j.efeitos_antes == ef["antes"] and j.efeitos_depois == ef["depois"]


def test_so_cuidado_do_p3_com_k4_tira_os_julgamentos_e_guarda_as_ofertas(monkeypatch):
    for mundo in ("descasado", "mutavel"):
        v = _vida(K4, "P3", 202, mundo)
        a = K4.acoplar(v, "P0", "sem_ensino")
        assert not _acoes(a.motor.log, bv.JULGAMENTOS) and _acoes(a.motor.log, OFERTAS) == _acoes(v.motor.log, OFERTAS)
        assert a.julgamentos == 0 and a.interacoes == bv.contar_acoes(a.motor.log)[0]
        n = K4.acoplar(v, "P3", "nenhum")                 # sem filtro, os julgamentos ficam, fora do orcamento
        assert n.julgamentos == v.julgamentos and n.interacoes == ORC
        assert bv.resumo_motor(n.motor) == bv.resumo_motor(v.motor)
    # um filtro que tirasse so o elogio deixaria a conta sem como separar o julgamento do feedback do dono: falha alto
    monkeypatch.setitem(bv.FILTROS, "so_elogio", frozenset({AcaoUsuario.ELOGIAR.value}))
    with pytest.raises(ValueError, match="separam"):
        K4.acoplar(_vida(K4, "P3", 101), "P0", "so_elogio")


def test_k4_com_o_pedido_no_p3ped():
    v = _vida(K4, "P3+ped", 101, "descasado")
    dono_no_log, _ = bv.contar_acoes(v.motor.log)
    assert v.interacoes == ORC == dono_no_log - v.broncas - v.julgamentos
    assert v.julgamentos == sum(1 for c in v.motor.consumos if c["efeito_humor"] != 0.0)


# ------------------------------------------------------------------ canais e ablacoes da K-7


def test_ablacoes_da_k7_e_os_canais_por_braco():
    canais_config = bv.bancada_da_config({"dias": DIAS, "orcamento": ORC, "ponto": "T3", "lobos": LOBOS,
                                          "consequencia": {"canais_ligados": True}})
    for bancada, canal_p1 in ((HOJE, False), (canais_config, True)):
        def pol(b):
            return bancada.politica(bv.EspecVida("atencioso", b, 101, mundo="descasado"))
        assert pol("P1").cfg_consequencia.canais_ligados is canal_p1             # o P1 segue a config
        c, m, e = pol("P1c"), pol("P1c-mem"), pol("P1c-can")
        assert c.cfg_consequencia.canais_ligados and m.cfg_consequencia.canais_ligados and not e.cfg_consequencia.canais_ligados
        for p, ganho in ((c, 512), (m, 0), (e, 512)):                          # P1c-mem: g = 0 (a memoria guarda, nao age)
            cl = p.cerebro.cl
            assert cl.memoria_ligada and cl.memoria_modo == "relevante" and cl.memoria_ganho == ganho and cl.aprendizado_ligado
        assert not pol("P1").cerebro.cl.memoria_ligada
    for b in ABLACOES:
        assert bv.BRACOS[b].fonte == "consequencia" and bv.BRACOS[b].no == "K-7"
    # as ablacoes mudam o que o P1 completo aprende (o estado interno difere)
    vs = {b: _vida(HOJE, b, 202, "descasado") for b in ABLACOES}
    assert bv._interno(vs["P1c"].motor) != bv._interno(vs["P1c-can"].motor)
    assert bv._interno(vs["P1c"].motor) != bv._interno(vs["P1c-mem"].motor)


# ------------------------------------------------------------------ faixas


def test_faixas_da_comparacao_dos_cerebros():
    for s in (28101, 28505, 29101, 29505):
        assert "comparacao dos cerebros" in bv.na_faixa_reservada(s)
    assert "substituida pela C-8" in bv.na_faixa_reservada(16101) and "substituida pela C-8" in bv.na_faixa_reservada(17505)
    assert all(bv.na_faixa_reservada(b) for bs in bv.BASES_COMPARACAO.values() for b in bs)
    los = sorted((lo, hi) for lo, hi, _ in bv.FAIXAS_RESERVADAS)
    assert all(a[1] < b[0] for a, b in zip(los, los[1:]))


# ------------------------------------------------------------------ G1


def test_g1_vidas_e_acoplados_novos():
    vidas = [_vida(K4, "P3", s, m, d, g) for m in FRUTAS_MUNDOS for d in ("atencioso", "aleatorio") for s, g in ((101, None), (202, 202))]
    vidas += [_vida(K4, "P3+ped", 101, "descasado")]
    vidas += [_vida(K4, b, s, m) for b in ABLACOES for m in ("descasado", "mutavel") for s in (101, 202)]
    acop = [K4.acoplar(v, "P0", "sem_ensino") for v in vidas if v.espec.braco == "P3"]
    acop += [K4.acoplar(v, "P3", "nenhum") for v in vidas[:3]]
    acop += [K4.acoplar(v, "P1c-can", "nenhum") for v in vidas if v.espec.braco == "P1c"]
    for v in vidas + acop:
        texto = v.motor.log.para_jsonl()
        K4.conferir_replay(v, texto)
        r = K4.rejogar(LogDeEventos.de_jsonl(texto), v.espec)
        assert bv.resumo_motor(r) == bv.resumo_motor(v.motor) and bv._interno(r) == bv._interno(v.motor)


def test_rodar_e_medidas(tmp_path):
    cfg = {"bracos": ["P0", "P1", *ABLACOES, "P3"], "donos": ["atencioso"], "sementes": [101, 202], "mundos": ["descasado", "mutavel"],
           "dias": 2, "orcamento": 32, "ponto": "T3", "lobos": LOBOS, "julgamento_fruta": True, "sonda": SONDA,
           "bootstrap": {"reamostragens": 200, "semente": 101, "nivel": 0.95},
           "acoplados": [{"origem": "P3", "destino": "P0", "filtro": "sem_ensino"}]}
    r = bv.rodar(cfg, tmp_path)
    assert len(r["vidas"]) == 2 * 2 * (6 + 1)
    med = json.loads((tmp_path / "medidas.json").read_text(encoding="utf-8"))
    assert all(m["interacoes"] == 32 for m in med.values() if m["origem"] is None)
    assert all(m["julgamentos"] == 0 for m in med.values() if m["braco"] != "P3")
    meta = json.loads((tmp_path / "meta.json").read_text(encoding="utf-8"))
    assert meta["config"]["julgamento_fruta"] is True
