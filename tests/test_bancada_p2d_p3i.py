"""P2D-P3I, parte D (docs/TAREFA_V2_P2D_P3I.md, secao 3; adendo 3, secao 3.3, do plano do experimento maior): os bracos P2d (a informacao
depois do consumo) e P3i (o julgamento como informacao) na bancada. Gates: os bracos de antes byte a byte (gabarito gravado antes); o P2d
sem o julgador = o P1 completo; o P3i com o julgamento desligado = o P3; P2 e P2d com o mesmo conhecimento; P3 e P3i com a mesma regra de
tempo do julgamento; as informacoes contadas, no multiconjunto das medidas e fora no sem_ensino; G1 dos bracos novos e dos acoplados.
So as sementes dos testes."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import bancada_v2 as bv  # noqa: E402
import gabarito_p2d_p3i_bancada as gab  # noqa: E402
import run_v2_experimento_maior as em  # noqa: E402
from digilab.config import CONFIG_DONOS  # noqa: E402
from digilab.events import LogDeEventos, informacao_de  # noqa: E402

PECAS = {"memoria_ganho": 512, "w0_info": 256}
BASE = {"dias": 4, "orcamento": 64, "ponto": "T3", "lobos": PECAS, "julgamento_fruta": True}
COMPLETA = bv.bancada_da_config({**BASE, "consequencia": {"canais_ligados": True}, "montagem": "completa"})
SIMPLES = bv.bancada_da_config(BASE)
SEM_K4 = {"simples": bv.bancada_da_config({**BASE, "julgamento_fruta": False}),
          "completa": bv.bancada_da_config({**BASE, "julgamento_fruta": False, "consequencia": {"canais_ligados": True},
                                            "montagem": "completa"})}
MUNDOS = ("casado_frutas", "descasado", "mutavel")
SONDA = {"estados": 4, "amostras": 4, "semente": 101}
PASSO = CONFIG_DONOS.passo_ticks


def _vida(bancada, braco, s=101, mundo="descasado", dono="atencioso", genoma=None):
    return bancada.vida(bv.EspecVida(dono, braco, s, genoma, mundo))


def _infos(vida) -> list[tuple[int, str, str]]:
    return [(e.tick, *informacao_de(bv.AcaoUsuario(e.valor))) for e in vida.motor.log
            if e.tipo == "acao_usuario" and str(e.valor) in bv.INFORMACOES]


def _sem(d: dict, *chaves) -> dict:
    return {k: v for k, v in d.items() if k not in chaves}


def _impressao_sem_info(e: dict) -> str:
    """sha256 do estado interno sem o que o w0_info poe nele (o peso da informacao, o prior dele, a contagem dos parametros e a
    informacao vigente no motivo da escolha da fruta) e sem o rotulo do braco; o resto (pesos, memoria, motivos, aprendizado) fica. Em
    sha256 para uma diferenca nao virar um diff de dezenas de milhares de caracteres no pytest."""
    e = {k: v for k, v in e.items() if k not in ("bancada", "peso_info", "peso_info_prior", "parametros_aprendidos")}
    e["motivos"] = [{**m, "fruta": _sem(m["fruta"], "info")} if "fruta" in m else m for m in e["motivos"]]
    return hashlib.sha256(json.dumps(e, sort_keys=True, default=repr).encode()).hexdigest()


def _passo_seguinte(tick: int) -> int:
    """o primeiro passo do dono depois de um consumo no tick dado (os passos do dono caem em k x passo_ticks)"""
    return (tick // PASSO + 1) * PASSO


# ------------------------------------------------------------------ os bracos de antes


def test_bracos_de_antes_byte_a_byte_pelo_gabarito():
    """As 378 vidas do gabarito (gravado com o codigo da main antes, tests/gabarito_p2d_p3i_bancada.py: P0 a P3, P2e, P2a, N6, N7 e K-7;
    os quatro mundos das frutas e o padrao; montagem simples e completa com o K4; os acoplados) saem iguais."""
    gabarito = json.loads(gab.ARQUIVO.read_text(encoding="utf-8"))
    vistos = {nome: gab.impressao(v) for nome, v in gab.casos()}
    assert len(vistos) == len(gabarito) == 378
    assert {n for n in vistos if vistos[n] != gabarito[n]} == set()


def test_contrato_dos_bracos():
    p2d, p3i = bv.BRACOS["P2d"], bv.BRACOS["P3i"]
    assert (p2d.fonte, p2d.informacao, p2d.julgamento) == ("informacao", "depois", None)
    assert (p3i.fonte, p3i.informacao, p3i.julgamento) == ("dono", None, "informacao")
    assert em.bracos_p2d_p3i_faltando() == []
    with pytest.raises(ValueError, match="julgador"):
        COMPLETA.informante(bv.EspecVida("atencioso", "P2d", 101, None, "descasado"))
    # o P2d julga sempre nas frutas (o julgador e o informante dele); o P3i so com a chave do K4; nenhum fora das frutas
    for bancada, p3i_julga in ((COMPLETA, True), (SEM_K4["completa"], False)):
        assert bancada.julga_fruta(bv.EspecVida("atencioso", "P2d", 101, None, "descasado"))
        assert bancada.julga_fruta(bv.EspecVida("atencioso", "P3i", 101, None, "descasado")) is p3i_julga
    assert not COMPLETA.julga_fruta(bv.EspecVida("atencioso", "P3i", 101, None, "padrao"))
    for braco, saida in (("P2d", "informacao"), ("P3i", "informacao"), ("P3", "feedback"), ("P3+ped", "feedback")):
        assert COMPLETA.saida_julgamento(bv.EspecVida("atencioso", braco, 101, None, "descasado")) == saida


def test_pecas_da_montagem_completa():
    """O P2d tem as pecas do P2 (memoria, canais, w0_info); o P3i as do P3 (memoria, sem canais) mais o w0_info da config."""
    for braco, base, info in (("P2d", "P2", True), ("P3i", "P3", True), ("P3", "P3", False)):
        v = _vida(COMPLETA, braco, 202, "mutavel")
        e = bv.do_braco(v.motor.politica).cerebro.estado_interno()
        ref = bv.do_braco(_vida(COMPLETA, base, 202, "mutavel").motor.politica)
        assert v.motor.politica.cfg_consequencia.canais_ligados is ref.cfg_consequencia.canais_ligados, braco
        assert e["memoria"]["ganho"] == 512 and ("peso_info" in e) is info, braco
        assert bv.do_braco(v.motor.politica).cerebro.cl.w0_info == (256 if info else 0), braco


# ------------------------------------------------------------------ o P2d sem o julgador e o P3i sem o julgamento


def test_p2d_sem_o_julgador_e_o_p1_completo(monkeypatch):
    """Sem o julgador (o informante dele), o P2d vive a vida do P1 completo: as mesmas decisoes, o mesmo log; o estado interno so tem a
    mais o que o w0_info do P2 poe nele (o peso da informacao, parado, e a informacao vigente, zero, no motivo da fruta)."""
    original = bv.Bancada.julga_fruta
    monkeypatch.setattr(bv.Bancada, "julga_fruta", lambda self, e: False if e.braco == "P2d" else original(self, e))
    for mundo in MUNDOS:
        for s in (101, 202):
            p2d, p1 = _vida(COMPLETA, "P2d", s, mundo), _vida(COMPLETA, "P1", s, mundo)
            assert bv.resumo_motor(p2d.motor) == bv.resumo_motor(p1.motor) and p2d.informacoes == 0
            e2d = bv.do_braco(p2d.motor.politica).cerebro.estado_interno()
            e1 = bv.do_braco(p1.motor.politica).cerebro.estado_interno()
            assert e2d["peso_info"] == e2d["peso_info_prior"] == 256 and "peso_info" not in e1
            assert _impressao_sem_info(e2d) == _impressao_sem_info(e1)


@pytest.mark.parametrize("montagem", ("simples", "completa"))
def test_p3i_com_o_julgamento_desligado_e_o_p3(montagem):
    """Com a chave do K4 desligada, o P3i e o P3: o mesmo log e as mesmas decisoes; na simples o estado interno tambem (so o rotulo do
    braco muda); na completa ele tem a mais o que o w0_info poe no estado (o peso da informacao, parado, e a informacao vigente no
    motivo)."""
    bancada = SEM_K4[montagem]
    for mundo in MUNDOS:
        for s in (101, 202):
            p3i, p3 = _vida(bancada, "P3i", s, mundo), _vida(bancada, "P3", s, mundo)
            assert bv.resumo_motor(p3i.motor) == bv.resumo_motor(p3.motor) and p3i.informacoes == p3i.julgamentos == 0
            e3i, e3 = p3i.motor.politica.estado_interno(), p3.motor.politica.estado_interno()
            if montagem == "completa":
                assert e3i["peso_info"] == e3i["peso_info_prior"] == 256 and "peso_info" not in e3
                assert _impressao_sem_info(e3i) == _impressao_sem_info(e3)
            else:
                assert e3i["bancada"]["braco"] == "P3i"
                assert json.dumps(_sem(e3i, "bancada"), sort_keys=True, default=repr) == \
                    json.dumps(_sem(e3, "bancada"), sort_keys=True, default=repr)


# ------------------------------------------------------------------ o mesmo conhecimento e a mesma regra de tempo


@pytest.mark.parametrize("mundo", MUNDOS)
def test_p2_e_p2d_com_o_mesmo_conhecimento(mundo):
    """O julgador do P2d tem os efeitos reais e a troca do informante do P2 da unidade; cada informacao do P2d fala da fruta consumida, no
    primeiro passo do dono depois do consumo, com o conteudo que o informante do P2 daria (o efeito vigente: "mal" se < 0), a neutra
    incluida; uma por consumo."""
    for s, g in ((101, None), (202, 202)):
        e2d, e2 = bv.EspecVida("atencioso", "P2d", s, g, mundo), bv.EspecVida("atencioso", "P2", s, g, mundo)
        j = COMPLETA.julgador(e2d)
        inf = COMPLETA.informante(e2)
        ef = COMPLETA.efeitos_reais(e2)
        assert j.saida == "informacao" and j.efeitos_antes == inf.antes.efeito_humor == ef["antes"]
        assert (j.efeitos_depois, j.tick_troca) == ((ef["depois"], COMPLETA.tick_troca) if mundo == "mutavel" else (None, None))
        v = _vida(COMPLETA, "P2d", s, mundo, genoma=g)
        consumos = v.motor.consumos
        infos = _infos(v)
        assert len(infos) == len(consumos) > 0 and v.informacoes == len(infos)
        for (t, f, c), con in zip(infos, consumos):
            vig = ef["depois"] if (ef["depois"] is not None and con["tick"] >= COMPLETA.tick_troca) else ef["antes"]
            assert (t, f) == (_passo_seguinte(con["tick"]), con["fruta"])
            assert c == ("mal" if vig[f] < 0 else "bem") and (c == "mal") == (con["efeito_humor"] < 0)


@pytest.mark.parametrize("mundo", MUNDOS)
def test_p3_e_p3i_com_a_mesma_regra_de_tempo(mundo):
    """O P3 e o P3i julgam pelo mesmo conhecimento e no mesmo momento: o primeiro passo do dono depois de cada consumo (o P3 so os nao
    neutros, como elogio ou bronca; o P3i todos, como informacao). Elogio = "bem" e bronca = "mal" do mesmo efeito vigente."""
    for s in (101, 202):
        e3, e3i = bv.EspecVida("atencioso", "P3", s, None, mundo), bv.EspecVida("atencioso", "P3i", s, None, mundo)
        j3, j3i = COMPLETA.julgador(e3), COMPLETA.julgador(e3i)
        assert (j3.saida, j3i.saida) == ("feedback", "informacao")
        assert (j3.efeitos_antes, j3.efeitos_depois, j3.tick_troca) == (j3i.efeitos_antes, j3i.efeitos_depois, j3i.tick_troca)
        p3, p3i = _vida(COMPLETA, "P3", s, mundo), _vida(COMPLETA, "P3i", s, mundo)
        julg = [(e.tick, str(e.valor)) for e in p3.motor.log if e.tipo == "acao_usuario" and str(e.valor) in bv.JULGAMENTOS
                and e.tick in {_passo_seguinte(c["tick"]) for c in p3.motor.consumos}]
        esperado3 = [(_passo_seguinte(c["tick"]), "elogiar" if c["efeito_humor"] > 0 else "repreender") for c in p3.motor.consumos
                     if c["efeito_humor"] != 0]
        assert sorted(julg) == sorted(esperado3) and p3.julgamentos == len(esperado3)
        esperado3i = [(_passo_seguinte(c["tick"]), c["fruta"], "mal" if c["efeito_humor"] < 0 else "bem") for c in p3i.motor.consumos]
        assert _infos(p3i) == esperado3i and p3i.julgamentos == 0 and p3i.informacoes == len(esperado3i) > 0


# ------------------------------------------------------------------ contagem, orcamento, medidas e o sem_ensino


@pytest.mark.parametrize("bancada", (SIMPLES, COMPLETA), ids=("simples", "completa"))
def test_informacoes_contadas_fora_do_orcamento_e_no_multiconjunto(bancada):
    for braco in ("P2d", "P3i"):
        for mundo in ("descasado", "mutavel"):
            for dono in ("atencioso", "aleatorio"):
                v = _vida(bancada, braco, 202, mundo, dono)
                assert v.interacoes == 64 and v.julgamentos == 0 and v.informacoes == len(_infos(v)) > 0
                m = bancada.medir(v, SONDA)
                mc = m["frutas"]["multiconjunto_informacoes"]
                assert sum(mc.values()) == m["informacoes"] == v.informacoes
                assert mc == em.multiconjunto_informacoes(m)          # o que o orquestrador do adendo 3 le
                cont: dict = {}
                for _, f, c in _infos(v):
                    cont[f"{f}/{c}"] = cont.get(f"{f}/{c}", 0) + 1
                assert mc == dict(sorted(cont.items()))


def test_sem_ensino_tira_as_informacoes_e_guarda_as_ofertas():
    for braco in ("P2d", "P3i"):
        origem = _vida(COMPLETA, braco, 101, "mutavel")
        so = COMPLETA.acoplar(origem, "P0", "sem_ensino")
        assert so.informacoes == 0 and so.julgamentos == 0
        ofertas = lambda v: [(e.tick, str(e.valor)) for e in v.motor.log if e.tipo == "acao_usuario"  # noqa: E731
                             and str(e.valor) in bv.EVENTOS_DO_MUNDO]
        assert ofertas(so) == ofertas(origem) and ofertas(origem)
        igual = COMPLETA.acoplar(origem, braco, "nenhum")
        assert igual.informacoes == origem.informacoes and bv.resumo_motor(igual.motor) == bv.resumo_motor(origem.motor)


# ------------------------------------------------------------------ G1 e rodar


def test_g1_bracos_novos_e_acoplados():
    vidas = [_vida(b, br, s, m, d, g) for b in (SIMPLES, COMPLETA) for br in ("P2d", "P3i") for m in MUNDOS
             for d in ("atencioso", "aleatorio") for s, g in ((101, None), (202, 202))]
    acop = []
    for v in vidas[:24]:                                      # os da simples
        acop += [SIMPLES.acoplar(v, "P0", "sem_ensino"), SIMPLES.acoplar(v, v.espec.braco, "nenhum")]
    for v in vidas[24:]:
        acop.append(COMPLETA.acoplar(v, "P1", "sem_ensino"))
    for bancada, grupo in ((SIMPLES, vidas[:24] + acop[:48]), (COMPLETA, vidas[24:] + acop[48:])):
        for v in grupo:
            texto = v.motor.log.para_jsonl()
            bancada.conferir_replay(v, texto)
            r = bancada.rejogar(LogDeEventos.de_jsonl(texto), v.espec)
            assert bv.resumo_motor(r) == bv.resumo_motor(v.motor) and bv._interno(r) == bv._interno(v.motor)


def test_rodar_com_os_bracos_novos(tmp_path):
    cfg = {**BASE, "montagem": "completa", "bracos": ["P0", "P2", "P2d", "P3", "P3i"], "donos": ["atencioso"], "sementes": [101, 202],
           "mundos": ["descasado", "mutavel"], "sonda": SONDA, "bootstrap": {"reamostragens": 200, "semente": 101, "nivel": 0.95},
           "acoplados": [{"origem": "P3i", "destino": "P0", "filtro": "sem_ensino"}]}
    r = bv.rodar(cfg, tmp_path)
    assert len(r["vidas"]) == 2 * 2 * 5 + 4
    med = json.loads((tmp_path / "medidas.json").read_text(encoding="utf-8"))
    for m in med.values():
        assert sum(m["frutas"]["multiconjunto_informacoes"].values()) == m["informacoes"]
        assert (m["informacoes"] > 0) == (m["braco"] in ("P2", "P2d", "P3i"))
