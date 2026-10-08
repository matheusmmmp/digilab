"""V2, BANCADA (docs/TAREFA_V2_BANCADA.md): orquestrador dos bracos P0-P3 sobre o mesmo aprendiz.

Gates: P0 = instinto byte a byte pela bancada (os G2 da L0); o modo acoplado reproduz (a vida de origem no proprio braco, o
acoplado da L1 e o registro sem os sinais); replay bit a bit de toda vida (G1). Sementes: so as dos testes (101...505)."""

import json
import random
import sys
from collections import Counter
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
from digilab import PoliticaInstinto  # noqa: E402
from digilab.config import CONFIG_LOBOS_APRENDIZ, TICKS_POR_DIA  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.events import AcaoUsuario, LogDeEventos  # noqa: E402
from digilab.metrics import custo_da_plasticidade, desempenho_no_ambiente, tabela_braco_condicao  # noqa: E402
from digilab.obediencia import MotorPersonalidade  # noqa: E402
from digilab.policies import PoliticaLobos  # noqa: E402
from digilab.policies.lobos import REGRAS  # noqa: E402
from digilab.protocol import ENGINE_SHA256_V0, sha256_engine  # noqa: E402
from digilab.temperamento import sortear as sortear_temperamento  # noqa: E402
from digilab.treino import reproduzir_com_feedback, simular_vida  # noqa: E402

DONOS = ("atencioso", "relapso", "aleatorio", "incoerente")
SEMENTES = (101, 202, 303, 404, 505)
DIAS, ORC = 3, 48
BANCADA = bv.Bancada(DIAS, ORC)
SONDA = {"estados": 30, "amostras": 30, "semente": 101}


class InstintoComGancho(PoliticaInstinto):
    """Controle do G2 no motor de personalidade (o embrulho sempre repassa receber_acao_dono): o instinto que ignora o dono."""

    def receber_acao_dono(self, acao, tick) -> None:
        return None


def _personalidade(politica, cfg, semente):
    return MotorPersonalidade(politica, cfg, semente, sortear_temperamento(semente))


def _interno_cerebro(motor) -> str:
    p = motor.politica
    p = getattr(p, "_p", p)                      # o embrulho do motor de personalidade
    return json.dumps(p.cerebro.estado_interno(), sort_keys=True)


# ------------------------------------------------------------------ contrato


def test_engine_intocado_e_bracos_com_fonte_e_no():
    assert sha256_engine() == ENGINE_SHA256_V0
    assert {b: (x.fonte, x.no) for b, x in bv.BRACOS.items()} == {
        "P0": ("nenhuma", "N0"), "P1": ("consequencia", "N3"), "P2": ("informacao", "N5"), "P2e": ("informacao", "N5"),
        "P2a": ("informacao", "N5"), "P3": ("dono", "N1"),
        # BANCADA-N6-N7: declarados, falham alto com o no ate a memoria e o pedido existirem (tests/test_bancada_n6_n7.py)
        "M0": ("nenhuma", "N6"), "MR": ("nenhuma", "N6"), "MT": ("nenhuma", "N6"), "ME": ("nenhuma", "N6"),
        "P0+ped": ("nenhuma", "N7"), "P1+ped": ("consequencia", "N7"), "P3+ped": ("dono", "N7"),
        # BANCADA-K4-CANAIS: as ablacoes da K-7 (tests/test_bancada_k4_canais.py)
        "P1c": ("consequencia", "K-7"), "P1c-mem": ("consequencia", "K-7"), "P1c-can": ("consequencia", "K-7"),
        # P2D-P3I, parte D: o momento e a interpretacao do adendo 3 (tests/test_bancada_p2d_p3i.py)
        "P2d": ("informacao", "adendo-3"), "P3i": ("dono", "adendo-3"),
        # W-BANCADA-MUNDO: o P0 sem explorar do mundo fisico, pendente do instinto do mundo (tests/test_bancada_mundo_fisico.py)
        "P0z": ("nenhuma", "mundo-fisico"),
        # W-BANCADA-CORPO: os bracos do plano do corpo (tests/test_bancada_corpo.py); o P1-cw e o P1-c com a pesos_janela
        "P0-hoje": ("nenhuma", "corpo-3.1"), "P1-hoje": ("consequencia", "corpo-3.1"), "P3-hoje": ("dono", "corpo-3.1"),
        "P0-quimica": ("nenhuma", "corpo-3.1"), "P1-quimica": ("consequencia", "corpo-3.1"), "P3-quimica": ("dono", "corpo-3.1"),
        "P0-q": ("nenhuma", "corpo-3.2"), "P1-q": ("consequencia", "corpo-3.2"), "P0-c": ("nenhuma", "corpo-3.2"),
        "P1-c": ("consequencia", "corpo-3.2"), "P0-c-tapa": ("nenhuma", "corpo-3.3"), "P1-c-tapa": ("consequencia", "corpo-3.3"),
        "P1-c-tapaX": ("consequencia", "corpo-A1.1"), "P1-c-frutas": ("consequencia", "corpo-A1.1"),
        "P1-cw": ("consequencia", "corpo-A2.4"),
        # W-BANCADA-BANHEIRO: o 2 x 2 do banheiro no P0 e no P1, pendente da etapa 3 do banheiro (tests/test_bancada_banheiro.py)
        **{f"{c}-{x}": (f, "banheiro") for c, f in (("P0", "nenhuma"), ("P1", "consequencia")) for x in ("B00", "B0C", "BL0", "BLC")}}
    assert (bv.BRACOS["P2"].informacao, bv.BRACOS["P2e"].informacao, bv.BRACOS["P2a"].informacao) == ("certa", "errada", "acoplada")


@pytest.mark.parametrize("braco", ["P2", "P2e", "P2a"])                       # o P1 chegou no N3, a informacao na BANCADA-N5
def test_a_informacao_so_existe_num_mundo_das_frutas(braco):
    for mundo in ("padrao", "bola"):
        with pytest.raises(ValueError, match="mundo das frutas"):
            BANCADA.vida(bv.EspecVida("atencioso", braco, 101, mundo=mundo))
    bv.validar_config({"bracos": [braco], "donos": ["atencioso"], "sementes": [101], "dias": 1, "orcamento": 16,
                       "sonda": SONDA, "bootstrap": {}, "mundos": ["descasado"]})


def test_mundo_cerebro_braco_e_filtro_desconhecidos_falham_alto():
    with pytest.raises(NotImplementedError):
        BANCADA.vida(bv.EspecVida("atencioso", "P0", 101, mundo="lago"))
    with pytest.raises(KeyError, match="N11"):
        BANCADA.vida(bv.EspecVida("atencioso", "P0", 101, cerebro="camada_unica"))
    with pytest.raises(KeyError):
        BANCADA.vida(bv.EspecVida("atencioso", "P9", 101))
    v = BANCADA.vida(bv.EspecVida("atencioso", "P0", 101))
    with pytest.raises(KeyError):
        BANCADA.acoplar(v, "P0", "sem_comida")
    with pytest.raises(ValueError):
        bv.Bancada(DIAS, ORC, cfg_lobos=PoliticaLobos().cl)          # a cfg da bancada e a do aprendiz (ligado)


def test_mesmo_aprendiz_em_todos_os_bracos():
    p0 = BANCADA.politica(bv.EspecVida("atencioso", "P0", 101))
    p3 = BANCADA.politica(bv.EspecVida("atencioso", "P3", 101))
    assert type(p0.cerebro) is type(p3.cerebro) is PoliticaLobos
    assert p0.cerebro._prior == p3.cerebro._prior == p3.cerebro._pesos
    i0, i3 = p0.cerebro.estado_interno(), p3.cerebro.estado_interno()
    assert i0["pesos_prior"] == i3["pesos_prior"] and i0["entradas"] == i3["entradas"]
    assert not p0.cerebro.aprende and p3.cerebro.aprende and p3.cerebro.cl == CONFIG_LOBOS_APRENDIZ
    assert p0.estado_interno()["bancada"] == {"braco": "P0", "fonte": "nenhuma"}


# ------------------------------------------------------------------ gate: P0 = instinto byte a byte (os G2 da L0)


@pytest.mark.parametrize("dono", DONOS)
def test_p0_e_o_instinto_byte_a_byte(dono):
    for s in SEMENTES:
        a = simular_vida(dono, criar_dono(dono), PoliticaInstinto(), s, DIAS, ORC)
        b = BANCADA.vida(bv.EspecVida(dono, "P0", s))
        assert bv.resumo_motor(a.motor) == bv.resumo_motor(b.motor), (dono, s)
        assert not b.motor.politica.pesos_mudaram()


@pytest.mark.parametrize("dono", DONOS)
def test_p0_com_genoma_e_o_instinto_byte_a_byte_no_motor_de_personalidade(dono):
    for s in SEMENTES:
        a = simular_vida(dono, criar_dono(dono), InstintoComGancho(), s, DIAS, ORC, fabrica_motor=_personalidade)
        b = BANCADA.vida(bv.EspecVida(dono, "P0", s, genoma=s))
        assert isinstance(b.motor, MotorPersonalidade)
        assert bv.resumo_motor(a.motor) == bv.resumo_motor(b.motor), (dono, s)


def test_p0_com_todas_as_regras_e_genoma_separado_do_ambiente():
    a = simular_vida("aleatorio", criar_dono("aleatorio"), PoliticaInstinto(), 101, DIAS, 24)
    b = bv.Bancada(DIAS, 24).vida(bv.EspecVida("aleatorio", "P0", 101))
    assert bv.resumo_motor(a.motor) == bv.resumo_motor(b.motor)
    assert set(Counter(m["regra"] for m in b.motor.politica.motivos)) == set(REGRAS)
    # genoma de outra semente: so o temperamento muda; ambiente, politica e dono continuam os da semente
    g = BANCADA.vida(bv.EspecVida("atencioso", "P0", 101, genoma=202))
    assert g.motor.temperamento == sortear_temperamento(202) and g.motor.semente == 101


def test_p0_nao_recebe_nada_do_dono():
    v = BANCADA.vida(bv.EspecVida("atencioso", "P0", 202))
    cerebro = v.motor.politica.cerebro
    mem = cerebro.memoria.para_dict()
    assert mem["elogios"] == mem["broncas"] == mem["cuidados"] == 0 and mem["decisoes"] > 0
    assert cerebro.estado_interno()["aprendizado"]["recompensas"] == {"elogio": 0, "repreensao": 0, "latencia": 0, "ignorado": 0}


# ------------------------------------------------------------------ P3: a vida e a da L1


@pytest.mark.parametrize("genoma", [None, "semente"])
def test_p3_e_a_vida_da_l1_byte_a_byte(genoma):
    for dono, s in (("atencioso", 101), ("incoerente", 303)):
        fm = _personalidade if genoma else None
        a = simular_vida(f"{dono}-lobos", criar_dono(dono), PoliticaLobos(None, CONFIG_LOBOS_APRENDIZ), s, DIAS, ORC,
                         rotulo_dono=dono, fabrica_motor=fm)
        b = BANCADA.vida(bv.EspecVida(dono, "P3", s, genoma=s if genoma else None))
        assert bv.resumo_motor(a.motor) == bv.resumo_motor(b.motor), (dono, s)
        assert json.dumps(a.motor.politica.estado_interno(), sort_keys=True) == _interno_cerebro(b.motor)
        assert b.motor.politica.pesos_mudaram()


# ------------------------------------------------------------------ gate: G1, replay bit a bit


def test_g1_replay_bit_a_bit_de_toda_vida_e_divergencia_falha_alto():
    vidas = [BANCADA.vida(bv.EspecVida(d, b, s, genoma=g)) for d in ("atencioso", "aleatorio") for b in ("P0", "P3")
             for s, g in ((101, None), (202, 202))]
    vidas += [BANCADA.acoplar(v, d, f) for v in vidas if v.espec.braco == "P3" for d in ("P0", "P3") for f in bv.FILTROS]
    for v in vidas:
        BANCADA.conferir_replay(v)                                   # do texto serializado
        r = BANCADA.rejogar(LogDeEventos.de_jsonl(v.motor.log.para_jsonl()), v.espec)
        assert bv.resumo_motor(r) == bv.resumo_motor(v.motor)
    errada = bv.VidaBancada(vidas[1].espec, vidas[0].motor, ORC)     # o motor de outro braco
    with pytest.raises(bv.ReplayDivergiu):
        BANCADA.conferir_replay(errada)
    with pytest.raises(bv.ReplayDivergiu):
        BANCADA.conferir_replay(vidas[0], vidas[2].motor.log.para_jsonl())


# ------------------------------------------------------------------ gate: o acoplado reproduz


@pytest.mark.parametrize("genoma", [None, 202])
def test_acoplado_no_proprio_braco_sem_filtro_e_a_vida_de_origem(genoma):
    for braco in ("P0", "P3"):
        v = BANCADA.vida(bv.EspecVida("atencioso", braco, 202, genoma=genoma))
        a = BANCADA.acoplar(v, braco, "nenhum")
        assert bv.resumo_motor(a.motor) == bv.resumo_motor(v.motor)
        assert json.dumps(a.motor.politica.estado_interno(), sort_keys=True) == \
            json.dumps(v.motor.politica.estado_interno(), sort_keys=True)
        assert a.nome == f"atencioso-{braco}~de-{braco}-nenhum{'' if genoma is None else '~g202'}@202"


@pytest.mark.parametrize("sem_carinho", [False, True])
def test_acoplado_generaliza_o_so_cuidado_da_l1(tmp_path, sem_carinho):
    """O P3 acoplado ao proprio registro sem os sinais e, byte a byte, o "so cuidado" acoplado de run_v2_l1."""
    from run_v2_l1 import log_so_cuidado, vidas_acopladas

    ponto = {"passo": CONFIG_LOBOS_APRENDIZ.passo, "teto": CONFIG_LOBOS_APRENDIZ.teto}
    filtro = "sem_sinais_sem_carinho" if sem_carinho else "sem_sinais"
    for s in (101, 404):
        origem = BANCADA.vida(bv.EspecVida("atencioso", "P3", s))
        l1 = simular_vida("atencioso-lobos", criar_dono("atencioso"), PoliticaLobos(None, CONFIG_LOBOS_APRENDIZ), s, DIAS,
                          ORC, rotulo_dono="atencioso")
        ref = vidas_acopladas({f"atencioso-lobos@{s}": l1}, ponto, [s], tmp_path, sem_carinho)
        ref_motor = next(iter(ref.values())).motor
        a = BANCADA.acoplar(origem, "P3", filtro)
        assert bv.resumo_motor(a.motor) == bv.resumo_motor(ref_motor)
        assert json.dumps(ref_motor.politica.estado_interno(), sort_keys=True) == _interno_cerebro(a.motor)
        assert a.motor.log.para_jsonl() == log_so_cuidado(origem.motor.log, sem_carinho).para_jsonl()
        rec = a.motor.politica.cerebro.estado_interno()["aprendizado"]["recompensas"]
        assert rec["elogio"] == rec["repreensao"] == 0 and rec["latencia"] + rec["ignorado"] > 0


def test_acoplado_com_o_sinal_desligado_e_o_registro_da_origem_sem_os_sinais():
    """P0 (fonte nenhuma) acoplado ao registro do P3 sem os sinais: o log e o da origem com os sinais retirados, evento a
    evento, e a vida e a do instinto nesse mesmo registro, byte a byte."""
    for dono, s in (("atencioso", 101), ("relapso", 505)):
        origem = BANCADA.vida(bv.EspecVida(dono, "P3", s))
        a = BANCADA.acoplar(origem, "P0", "sem_sinais")
        sinais = {AcaoUsuario.ELOGIAR.value, AcaoUsuario.REPREENDER.value}
        esperado = [e for e in origem.motor.log if not (e.tipo == "acao_usuario" and str(e.valor) in sinais)]
        assert list(a.motor.log) == esperado and len(esperado) < len(list(origem.motor.log))
        inst = reproduzir_com_feedback(LogDeEventos(esperado), lambda cfg: PoliticaInstinto(cfg), semente=s)
        assert bv.resumo_motor(a.motor) == bv.resumo_motor(inst)
        assert not a.motor.politica.pesos_mudaram() and a.rotulo_braco == "P0<P3:sem_sinais"


# ------------------------------------------------------------------ metricas da pergunta maior


def test_desempenho_no_ambiente():
    d = desempenho_no_ambiente([(False, 1.0), (True, 0.5), (False, 0.75), (False, 0.25)])
    assert d == {"n": 4, "fracao_fora_de_privacao": 0.75, "saude_media": 0.625}
    with pytest.raises(ValueError):
        desempenho_no_ambiente([])
    with pytest.raises(TypeError):
        desempenho_no_ambiente([(0, 1.0)])
    with pytest.raises(ValueError):
        desempenho_no_ambiente([(False, 1.5)])


def test_custo_da_plasticidade():
    c = custo_da_plasticidade([0.01, 0.03, 0.02], [0.5, 0.6, 0.7], [2, 5, 9], piso=0.5)
    assert c["deriva_final"] == 0.02 and c["deriva_maxima"] == 0.03 and c["deriva_por_dia"] == [0.01, 0.03, 0.02]
    assert c["tempo_ate_metade"] == {"alvo": 0.6, "piso": 0.5, "maximo": 0.7, "dia": 1, "sinais": 5}
    with pytest.raises(ValueError):
        custo_da_plasticidade([], [0.5], [1], 0.5)
    with pytest.raises(ValueError):
        custo_da_plasticidade([-0.1], [0.5], [1], 0.5)


def test_tabela_braco_condicao():
    t = tabela_braco_condicao({("P0", "padrao"): [0.5, 0.7], ("P3", "padrao"): [0.6, 0.8, 1.0]}, 200, 1, 0.95)
    assert t["bracos"] == ["P0", "P3"] and t["condicoes"] == ["padrao"]
    assert abs(t["celulas"]["P0"]["padrao"]["media"] - 0.6) < 1e-12 and t["celulas"]["P3"]["padrao"]["n"] == 3
    with pytest.raises(ValueError, match="incompleta"):
        tabela_braco_condicao({("P0", "a"): [1.0, 2.0], ("P3", "b"): [1.0, 2.0]}, 200, 1, 0.95)
    with pytest.raises(ValueError):
        tabela_braco_condicao({("P0", "a"): [1.0]}, 200, 1, 0.95)
    with pytest.raises(ValueError):
        tabela_braco_condicao({}, 200, 1, 0.95)


def test_medir_reaproveita_a_tarefa_da_l1_e_o_p0_nao_deriva():
    from run_v2_l1 import curva_tarefa

    p0 = BANCADA.vida(bv.EspecVida("atencioso", "P0", 303))
    p3 = BANCADA.vida(bv.EspecVida("atencioso", "P3", 303))
    m0 = BANCADA.medir(p0, SONDA)
    m3 = BANCADA.medir(p3, SONDA, piso=m0["acerto_total"])
    n = DIAS * TICKS_POR_DIA // p0.motor.cfg.intervalo_decisao_ticks
    assert m0["n"] == m3["n"] == n                                    # uma amostra por decisao
    assert m0["deriva_final"] == 0.0 and m0["custo_da_plasticidade"]["deriva_maxima"] == 0.0
    # no P0 o dono elogia e repreende, mas nada chega ao aprendiz; no P3 tudo chega (o dono reage ao pet: as contagens diferem)
    assert m0["sinais_total"] == 0 < m0["sinais_do_dono"] and m3["sinais_total"] == m3["sinais_do_dono"] > 0
    assert m3["custo_da_plasticidade"]["deriva_maxima"] > 0.0 and m3["sinais_total"] > 0
    assert m3["custo_da_plasticidade"]["tempo_ate_metade"]["piso"] == m0["acerto_total"]
    ref = curva_tarefa(p3.motor.log, lambda cfg=None: PoliticaLobos(cfg, CONFIG_LOBOS_APRENDIZ), 303, dias=DIAS)
    assert ref["acerto"] == m3["acerto_por_dia"] and ref["acerto_total"] == m3["acerto_total"]
    assert ref["sinais_acumulados"] == m3["sinais_acumulados"]
    inst = curva_tarefa(p0.motor.log, lambda cfg=None: PoliticaInstinto(cfg), 303, dias=DIAS)
    assert inst["acerto_total"] == m0["acerto_total"]
    # o replay de medicao nao muda a vida: medir de novo da o mesmo numero
    assert BANCADA.medir(p3, SONDA, piso=m0["acerto_total"]) == m3


def test_privacao_amostrada_pela_regra_do_estado():
    """O orcamento minimo do aleatorio deixa o pet em privacao parte do tempo: a fracao fora de privacao cai abaixo de 1."""
    b = bv.Bancada(DIAS, 24)
    m = b.medir(b.vida(bv.EspecVida("aleatorio", "P0", 101)), SONDA)
    assert 0.0 < m["fracao_fora_de_privacao"] < 1.0 and 0.0 < m["saude_media"] < 1.0


# ------------------------------------------------------------------ orquestrador


def _cfg(**kw):
    c = {"descricao": "fumaca de teste, nao canonica", "bracos": ["P0", "P3"], "donos": ["atencioso", "aleatorio"],
         "sementes": [101, 202], "dias": 2, "orcamento": 32, "sonda": {"estados": 20, "amostras": 20, "semente": 101},
         "bootstrap": {"reamostragens": 200, "semente": 101, "nivel": 0.95},
         "acoplados": [{"origem": "P3", "destino": "P0", "filtro": "sem_sinais"},
                       {"origem": "P3", "destino": "P3", "filtro": "sem_sinais"}]}
    c.update(kw)
    return c


def test_rodar_grava_rejoga_do_disco_e_monta_as_tabelas(tmp_path):
    r = bv.rodar(_cfg(), tmp_path)
    assert len(r["vidas"]) == 2 * 2 * 2 + 2 * 2 * 2                 # 8 vidas + 8 acopladas
    for nome, v in r["vidas"].items():
        texto = (tmp_path / "vidas" / f"{nome}.jsonl").read_text(encoding="utf-8")
        BANCADA_2 = bv.Bancada(2, 32)
        BANCADA_2.conferir_replay(v, texto)
    t = json.loads((tmp_path / "tabelas.json").read_text(encoding="utf-8"))
    assert set(t) == {"atencioso", "aleatorio"} and set(t["atencioso"]) == set(bv.MEDIDAS_TABELA)
    assert t["atencioso"]["acerto_total"]["bracos"] == ["P0", "P0<P3:sem_sinais", "P3", "P3<P3:sem_sinais"]
    assert t["atencioso"]["deriva_final"]["condicoes"] == ["casado/padrao"]
    assert t["atencioso"]["deriva_final"]["celulas"]["P0"]["casado/padrao"]["media"] == 0.0
    med = json.loads((tmp_path / "medidas.json").read_text(encoding="utf-8"))
    for nome, m in med.items():
        if m["braco"] != "P0":
            p0 = med[f"{m['dono']}-P0@{m['semente']}"]
            assert m["custo_da_plasticidade"]["tempo_ate_metade"]["piso"] == p0["acerto_total"]
    meta = json.loads((tmp_path / "meta.json").read_text(encoding="utf-8"))
    assert meta["engine_sha256"] == ENGINE_SHA256_V0 and len(meta["lobos_sha256"]) == 64
    # mesma config, outra pasta: tudo igual (determinismo)
    r2 = bv.rodar(_cfg(), tmp_path / "de_novo")
    assert (tmp_path / "medidas.json").read_text(encoding="utf-8") == \
        (tmp_path / "de_novo" / "medidas.json").read_text(encoding="utf-8")
    assert set(r2["vidas"]) == set(r["vidas"])


def test_sementes_fora_das_dos_testes_pedem_o_plano():
    with pytest.raises(bv.SementeSemPlano):
        bv.validar_config(_cfg(sementes=[3101, 3202]))
    with pytest.raises(bv.SementeSemPlano):
        bv.validar_config(_cfg(genomas=[4101]))
    with pytest.raises(bv.SementeSemPlano):
        bv.validar_config(_cfg(sementes=[3101, 3202], plano="docs/NAO_EXISTE.md"))
    bv.validar_config(_cfg(sementes=[3101, 3202], plano="docs/PLANO_ANALISE_V2_L1.md"))
    with pytest.raises(ValueError):
        bv.validar_config(_cfg(saida="x"))                       # chave fora do formato
    with pytest.raises(ValueError):
        bv.validar_config(_cfg(acoplados=[{"origem": "P1", "destino": "P0", "filtro": "sem_sinais"}]))
