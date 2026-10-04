"""V2, BANCADA-MUNDOS (docs/TAREFA_V2_BANCADA_MUNDOS.md): o mundo da bola na bancada e o contrato das condicoes.

Gates: G1 de toda vida dos mundos novos; o mundo da bola com as regras da A1 reproduz a vida da A1 byte a byte; com B1 e B2, o
dono aleatorio nunca sorteia por_bola e a bola nao gasta orcamento; o acoplado com mundo reproduz e nao perde os eventos do
mundo. Sementes: so as dos testes (101...505)."""

import json
import sys
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
from digilab.ambiente import PoliticaInstintoBola, fabricas_ambiente, reproduzir_ambiente  # noqa: E402
from digilab.config import CONFIG_BOLA, CONFIG_BOLA_LIGADA  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.events import AcaoUsuario, LogDeEventos  # noqa: E402
from digilab.policies.lobos import REGRAS  # noqa: E402
from digilab.protocol import ENGINE_SHA256_V0, sha256_engine  # noqa: E402
from digilab.treino import simular_vida  # noqa: E402

DONOS = ("atencioso", "relapso", "aleatorio", "incoerente")
DIAS, ORC = 3, 48
BANCADA = bv.Bancada(DIAS, ORC)
SONDA = {"estados": 30, "amostras": 30, "semente": 101}
POR_BOLA = AcaoUsuario.POR_BOLA.value


def _bolas(log) -> list[int]:
    return [e.tick for e in log if e.tipo == "acao_usuario" and str(e.valor) == POR_BOLA]


# ------------------------------------------------------------------ contrato das condicoes


def test_contrato_das_condicoes():
    """Desde a BANCADA-FRUTAS as tres condicoes existem (os mundos das frutas); o contrato e: todo mundo realiza uma condicao
    e nenhuma condicao espera no. Os mundos das frutas estao em tests/test_bancada_frutas.py."""
    assert set(bv.CONDICOES) == {"casado", "descasado", "mutavel"}
    assert all(c.precisa == "" and c.no == "" for c in bv.CONDICOES.values())
    assert {m: bv.MUNDOS[m].condicao for m in bv.MUNDOS} == {
        "padrao": "casado", "bola": "casado", "bola_a1": "casado", "casado_frutas": "casado", "descasado": "descasado",
        "mutavel": "mutavel"}
    assert bv.EspecVida("atencioso", "P0", 101, mundo="bola").condicao == "casado"
    with pytest.raises(NotImplementedError):
        bv.mundo_de("lago")
    with pytest.raises(NotImplementedError):
        bv.validar_config({"bracos": ["P0"], "donos": ["atencioso"], "sementes": [101], "dias": 1, "orcamento": 16,
                           "sonda": SONDA, "bootstrap": {}, "mundos": ["lago"]})


def test_configuracoes_invalidas_falham_alto():
    with pytest.raises(ValueError):
        bv.Bancada(DIAS, ORC, cfg_bola=CONFIG_BOLA)                       # a bola dos mundos da bola e ligada
    with pytest.raises(ValueError, match="P0"):
        BANCADA.vida(bv.EspecVida("atencioso", "P3", 101, mundo="bola", cerebro="instinto"))   # instinto nao aprende
    assert sha256_engine() == ENGINE_SHA256_V0


# ------------------------------------------------------------------ gate: bola com as regras da A1 = a vida da A1


@pytest.mark.parametrize("dono", DONOS)
def test_bola_a1_e_a_vida_da_a1_byte_a_byte(dono):
    """bola_a1 com o instinto que ve a bola = braco "bola" da A1; com os lobos (que ainda nao veem a bola) = braco "bolacega"."""
    from run_v2_a1 import _dono, _fabricas

    for s in (101, 303):
        for braco_a1, cerebro in (("bola", "instinto"), ("bolacega", "lobos")):
            fp, fm = _fabricas(braco_a1, CONFIG_BOLA_LIGADA)
            a1 = simular_vida(f"{dono}-{braco_a1}", _dono(braco_a1, dono, CONFIG_BOLA_LIGADA), fp(), s, DIAS, ORC,
                              rotulo_dono=dono, fabrica_motor=fm)
            b = BANCADA.vida(bv.EspecVida(dono, "P0", s, mundo="bola_a1", cerebro=cerebro))
            assert bv.resumo_motor(a1.motor) == bv.resumo_motor(b.motor), (dono, s, braco_a1)
            assert a1.motor.estado() == b.motor.estado()


def test_bola_a1_mantem_a_bola_no_orcamento_e_o_aleatorio_sorteando():
    v = BANCADA.vida(bv.EspecVida("aleatorio", "P0", 101, mundo="bola_a1"))
    dono, mundo = bv.contar_acoes(v.motor.log)
    assert mundo > 0 and dono + mundo == ORC


# ------------------------------------------------------------------ gate: B1 e B2


@pytest.mark.parametrize("dono", DONOS)
def test_b1_b2_aleatorio_nao_sorteia_bola_e_a_bola_nao_gasta_orcamento(dono):
    for s in (101, 202, 303, 404, 505):
        v = BANCADA.vida(bv.EspecVida(dono, "P0", s, mundo="bola", cerebro="instinto"))
        n_dono, n_mundo = bv.contar_acoes(v.motor.log)
        assert n_dono == ORC == v.interacoes                              # o orcamento inteiro, so com acoes do dono
        assert n_mundo == len(_bolas(v.motor.log)) == v.motor.contagem_bola["postas"] + v.motor.contagem_bola["renovadas"]
        if dono == "aleatorio":
            assert n_mundo == 0                                           # B1: nunca sorteia por_bola
        elif dono in ("atencioso", "incoerente"):
            assert n_mundo > 0


def test_b1_o_aleatorio_no_mundo_da_bola_e_o_da_v1():
    """Sem bola no log, o mundo da bola e o padrao: o aleatorio (B1) tem o mesmo registro, as mesmas acoes e as mesmas rngs."""
    for s in (101, 404):
        a = BANCADA.vida(bv.EspecVida("aleatorio", "P0", s))
        b = BANCADA.vida(bv.EspecVida("aleatorio", "P0", s, mundo="bola"))
        assert a.motor.log.para_jsonl() == b.motor.log.para_jsonl()
        assert a.motor.acoes_recentes(10**9) == b.motor.acoes_recentes(10**9)
        assert a.motor._rng_politica.getstate() == b.motor._rng_politica.getstate()
        assert a.motor._rng_ambiente.getstate() == b.motor._rng_ambiente.getstate()


def test_b2_o_laco_do_mundo_sem_eventos_e_o_simular_vida():
    """O canal do mundo fora do orcamento nao muda nada quando a regra do mundo nao poe nada."""

    class Nada:
        def decidir(self, visao, acoes):
            return []

    for dono in DONOS:
        espec = bv.EspecVida(dono, "P3", 202)
        a = simular_vida(f"{dono}-P3", criar_dono(dono), BANCADA.politica(espec), 202, DIAS, ORC, rotulo_dono=dono,
                         fabrica_motor=BANCADA.fabrica_motor(espec))
        m = bv.simular_vida_mundo(criar_dono(dono), Nada(), BANCADA.politica(espec), 202, DIAS, ORC, dono,
                                  BANCADA.fabrica_motor(espec))
        assert bv.resumo_motor(a.motor) == bv.resumo_motor(m)


def test_b2_a_bola_nao_desloca_o_dono():
    """Com a bola fora do orcamento o atencioso faz as mesmas 48 acoes; na A1 a bola tomava lugar delas."""
    b = BANCADA.vida(bv.EspecVida("atencioso", "P0", 101, mundo="bola", cerebro="instinto"))
    a1 = BANCADA.vida(bv.EspecVida("atencioso", "P0", 101, mundo="bola_a1", cerebro="instinto"))
    assert bv.contar_acoes(b.motor.log)[0] == ORC > bv.contar_acoes(a1.motor.log)[0]
    with pytest.raises(ValueError, match="eventos do mundo"):
        class Errada:
            def decidir(self, visao, acoes):
                return [AcaoUsuario.ELOGIAR]
        espec = bv.EspecVida("atencioso", "P0", 101, mundo="bola")
        bv.simular_vida_mundo(criar_dono("atencioso"), Errada(), BANCADA.politica(espec), 101, DIAS, ORC, "atencioso",
                              BANCADA.fabrica_motor(espec))


# ------------------------------------------------------------------ gate: G1 nos mundos novos


def test_g1_replay_bit_a_bit_dos_mundos_novos():
    vidas = [BANCADA.vida(bv.EspecVida(d, b, s, genoma=g, mundo=m, cerebro=c))
             for m in ("bola", "bola_a1") for d in ("atencioso", "aleatorio") for s, g in ((101, None), (202, 202))
             for b, c in (("P0", "lobos"), ("P3", "lobos"), ("P0", "instinto"))]
    vidas += [BANCADA.acoplar(v, "P0", "sem_sinais") for v in vidas if v.espec.braco == "P3"]
    for v in vidas:
        BANCADA.conferir_replay(v)
        r = BANCADA.rejogar(LogDeEventos.de_jsonl(v.motor.log.para_jsonl()), v.espec)
        assert bv.resumo_motor(r) == bv.resumo_motor(v.motor) and r.estado() == v.motor.estado()
    p3 = next(v for v in vidas if v.espec.braco == "P3" and v.origem is None and v.espec.mundo == "bola")
    assert p3.motor.politica.pesos_mudaram()                                # o P3 aprende no mundo da bola
    with pytest.raises(bv.ReplayDivergiu):
        BANCADA.conferir_replay(bv.VidaBancada(vidas[1].espec, vidas[0].motor, ORC))


# ------------------------------------------------------------------ gate: acoplado com mundo


@pytest.mark.parametrize("mundo", ["bola", "bola_a1"])
def test_acoplado_no_proprio_braco_reproduz_a_vida_no_mundo(mundo):
    for braco, cerebro, g in (("P0", "lobos", None), ("P3", "lobos", 202), ("P0", "instinto", None)):
        v = BANCADA.vida(bv.EspecVida("atencioso", braco, 202, genoma=g, mundo=mundo, cerebro=cerebro))
        a = BANCADA.acoplar(v, braco, "nenhum")
        assert bv.resumo_motor(a.motor) == bv.resumo_motor(v.motor) and a.motor.estado() == v.motor.estado()
        assert json.dumps(a.motor.politica.estado_interno(), sort_keys=True) == \
            json.dumps(v.motor.politica.estado_interno(), sort_keys=True)


def test_acoplado_nao_perde_os_eventos_do_mundo():
    """P3 no mundo da bola acoplado ao P0 sem os sinais: o log e o da origem sem elogios e broncas, com toda bola no mesmo
    tick, e a vida e a do instinto (que nao ve a bola) nesse registro, no mesmo mundo."""
    for dono, s in (("atencioso", 101), ("incoerente", 505)):
        origem = BANCADA.vida(bv.EspecVida(dono, "P3", s, mundo="bola"))
        assert _bolas(origem.motor.log)
        a = BANCADA.acoplar(origem, "P0", "sem_sinais")
        assert _bolas(a.motor.log) == _bolas(origem.motor.log) and a.eventos_mundo == origem.eventos_mundo
        assert a.motor.log.para_jsonl() == bv.filtrar_log(origem.motor.log, bv.SINAIS).para_jsonl()
        assert not any(e.tipo == "acao_usuario" and str(e.valor) in bv.SINAIS for e in a.motor.log)
        cega = replace(CONFIG_BOLA_LIGADA, w_bola=0.0)
        fp, fm = fabricas_ambiente(cfg_bola=CONFIG_BOLA_LIGADA, politica_fabrica=lambda cfg=None: PoliticaInstintoBola(cfg, cega))
        ref = reproduzir_ambiente(a.motor.log, fp, semente=s, fabrica_motor=fm)
        assert bv.resumo_motor(ref) == bv.resumo_motor(a.motor)
        assert a.rotulo_braco == "P0<P3:sem_sinais" and a.interacoes < origem.interacoes


def test_filtro_nunca_tira_evento_do_mundo():
    assert not any(f & bv.EVENTOS_DO_MUNDO for f in bv.FILTROS.values())
    assert POR_BOLA in bv.EVENTOS_DO_MUNDO and AcaoUsuario.TIRAR_BOLA.value in bv.EVENTOS_DO_MUNDO
    v = BANCADA.vida(bv.EspecVida("atencioso", "P0", 101, mundo="bola"))
    with pytest.raises(ValueError, match="eventos do mundo"):
        bv.filtrar_log(v.motor.log, frozenset({POR_BOLA}))


# ------------------------------------------------------------------ medidas no mundo da bola


def test_medir_no_mundo_da_bola():
    inst = BANCADA.vida(bv.EspecVida("atencioso", "P0", 303, mundo="bola", cerebro="instinto"))
    lob = BANCADA.vida(bv.EspecVida("atencioso", "P0", 303, mundo="bola"))
    p3 = BANCADA.vida(bv.EspecVida("atencioso", "P3", 303, mundo="bola"))
    mi, ml = BANCADA.medir(inst, SONDA), BANCADA.medir(lob, SONDA)
    m3 = BANCADA.medir(p3, SONDA, piso=ml["acerto_total"])
    assert mi["bola"]["contagem"] == inst.motor.contagem_bola and mi["bola"]["resposta"]["n_com_bola"] > 0
    assert mi["condicao"] == "casado" and mi["mundo"] == "bola" and mi["eventos_mundo"] == len(_bolas(inst.motor.log))
    assert mi["deriva_final"] == ml["deriva_final"] == 0.0                # o P0 nao deriva, com ou sem a bola na sonda
    assert m3["custo_da_plasticidade"]["deriva_maxima"] > 0.0
    assert BANCADA.medir(p3, SONDA, piso=ml["acerto_total"]) == m3       # medir nao muda a vida
    # os lobos ainda nao tem a regra da bola; o instinto que ve a bola usa a regra bola_no_cenario
    reg = []

    def fab(cfg=None):
        r = bv._Registro(BANCADA.politica(lob.espec, cfg))
        reg.append(r)
        return r

    reproduzir_ambiente(lob.motor.log, fab, semente=303, fabrica_motor=BANCADA.fabrica_motor(lob.espec))
    assert {r for _, r, _ in reg[0].bola} <= set(REGRAS) and any(b for b, _, _ in reg[0].bola)
    reg.clear()

    def fab_i(cfg=None):
        r = bv._Registro(BANCADA.politica(inst.espec, cfg))
        reg.append(r)
        return r

    reproduzir_ambiente(inst.motor.log, fab_i, semente=303, fabrica_motor=BANCADA.fabrica_motor(inst.espec))
    assert "bola_no_cenario" in {r for _, r, _ in reg[0].bola}


def test_rodar_com_os_mundos(tmp_path):
    cfg = {"descricao": "fumaca de teste, nao canonica", "bracos": ["P0", "P3"], "donos": ["atencioso", "aleatorio"],
           "sementes": [101, 202], "mundos": ["padrao", "bola"], "dias": 2, "orcamento": 32,
           "sonda": {"estados": 20, "amostras": 20, "semente": 101},
           "bootstrap": {"reamostragens": 200, "semente": 101, "nivel": 0.95},
           "acoplados": [{"origem": "P3", "destino": "P0", "filtro": "sem_sinais"}]}
    r = bv.rodar(cfg, tmp_path)
    assert len(r["vidas"]) == 2 * 2 * 2 * 2 + 2 * 2 * 2
    t = json.loads((tmp_path / "tabelas.json").read_text(encoding="utf-8"))
    assert t["atencioso"]["saude_media"]["condicoes"] == ["casado/bola", "casado/padrao"]
    med = json.loads((tmp_path / "medidas.json").read_text(encoding="utf-8"))
    for m in med.values():
        assert (m["bola"] is None) == (m["mundo"] == "padrao")
        if m["dono"] == "aleatorio":
            assert m["eventos_mundo"] == 0
        if m["origem"] is None:
            assert m["interacoes"] == 32
    # a mesma config de novo: tudo igual (determinismo)
    bv.rodar(cfg, tmp_path / "de_novo")
    assert (tmp_path / "medidas.json").read_text(encoding="utf-8") == \
        (tmp_path / "de_novo" / "medidas.json").read_text(encoding="utf-8")


def test_dono_aleatorio_da_bola_da_a1_continua_sorteando():
    """Os donos da A1 ficam como estao: o DonoComBola do aleatorio ainda sorteia por_bola (a A1 reproduz)."""
    from digilab.ambiente import DonoComBola, DonoAleatorioBola

    assert AcaoUsuario.POR_BOLA in DonoAleatorioBola.POOL
    assert isinstance(DonoComBola("aleatorio", CONFIG_BOLA_LIGADA).base, DonoAleatorioBola)
