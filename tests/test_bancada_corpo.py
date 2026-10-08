"""V2, W-BANCADA-CORPO (rodada 21): a etapa 8 do corpo, a bancada (docs/TAREFA_V2_CORPO_DRIVES.md, secao 14;
docs/PLANO_ANALISE_V2_CORPO_DRIVES.md, secoes 2 a 5 e adendos 1 e 2).

O que se confere:
- o regime "hoje" e a vida de antes byte a byte (P0, P1 e P3, nos mundos de hoje e no fisico, nas duas montagens);
- o regime "quimica": o com_corpo(...) do motor com a ConfigCorpo da bancada (ligada, digestao na taxa C e a Vida), o cerebro A com
  cfg_corpo, o G1 e o acoplado;
- a chave "corpo" da config (os numeros, nunca as sub-chaves);
- as medidas da secao 5 (BE/OC, o cuidado preservado, os drives novos indisponiveis sem a etapa 6) e a dominancia pelos receptores,
  conferida contra o motivo e os canais do cerebro, falhando alto quando divergem;
- o que espera a etapa 6 falha alto com o no: os bracos do corpo, do tapa e da generalizacao, o P1-cw e o filtro sem_gestos; e o corpo
  no mundo fisico, que espera o contrato dos ganchos do A e do B;
- a config com o plano e o prefixo do corpo, e o rodar da fumaca.
So as sementes dos testes.
"""
from __future__ import annotations

import json
import sys
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
from digilab.config import CONFIG_CONSEQUENCIA  # noqa: E402
from digilab.events import LogDeEventos  # noqa: E402
from digilab.motor_corpo import MotorCorpo  # noqa: E402

SONDA = {"estados": 5, "amostras": 5, "semente": 101}
CC_CANAIS = replace(CONFIG_CONSEQUENCIA, canais_ligados=True)
MUNDOS_HOJE = (("padrao", None), ("bola", None), ("descasado", None), ("mutavel", None), ("iguais_frutas", None),
               ("fisico", "perto"), ("fisico_afastado", "longe"))
MUNDOS_QUIMICA = ("padrao", "bola", "descasado", "mutavel", "iguais_frutas")
PENDENTES = {"P0-q": "DonoComGestos", "P1-q": "DonoComGestos", "P0-c": "etapa 6", "P1-c": "etapa 6", "P0-c-tapa": "etapa 6",
             "P1-c-tapa": "etapa 6", "P1-c-tapaX": "etapa 6", "P1-c-frutas": "etapa 6", "P1-cw": "etapa 6"}


def _bancada(montagem="simples", dias=2, cc=CONFIG_CONSEQUENCIA, **kw):
    if montagem == "completa":
        kw.update(cfg_lobos=bv.cfg_lobos_do_ponto("T3"), montagem="completa")
    return bv.Bancada(dias, 16 * dias, cfg_consequencia=cc, **kw)


def _cfg(**troca) -> dict:
    cfg = {"bracos": ["P0-hoje", "P0-quimica"], "donos": ["atencioso"], "sementes": [101], "dias": 1, "orcamento": 16, "sonda": SONDA,
           "bootstrap": {}, "mundos": ["bola"]}
    cfg.update(troca)
    return cfg


# ------------------------------------------------------------------ 1. o regime "hoje" e a vida de antes


@pytest.mark.parametrize("montagem", ("simples", "completa"))
def test_o_regime_hoje_e_a_vida_de_antes_byte_a_byte(montagem):
    b = _bancada(montagem, cc=CC_CANAIS)
    for mundo, lugar in MUNDOS_HOJE:
        for braco in ("P0", "P1", "P3"):
            for dono in ("atencioso", "aleatorio"):
                vh = b.vida(bv.EspecVida(dono, f"{braco}-hoje", 101, None, mundo, lugar=lugar))
                v0 = b.vida(bv.EspecVida(dono, braco, 101, None, mundo, lugar=lugar))
                assert not isinstance(vh.motor, MotorCorpo) and b.cfg_corpo_de(vh.espec) is None
                assert bv.resumo_motor(vh.motor) == bv.resumo_motor(v0.motor), (mundo, braco, dono)
                assert bv._interno(vh.motor).replace(f'"braco": "{braco}-hoje"', f'"braco": "{braco}"') == bv._interno(v0.motor)


# ------------------------------------------------------------------ 2. o regime "quimica"


@pytest.mark.parametrize("montagem", ("simples", "completa"))
def test_o_regime_quimica_liga_o_corpo_no_motor_e_no_cerebro(montagem):
    b = _bancada(montagem, cc=CC_CANAIS)
    for mundo in MUNDOS_QUIMICA:
        for braco in ("P0", "P1", "P3"):
            v = b.vida(bv.EspecVida("aleatorio", f"{braco}-quimica", 202, None, mundo))   # Bancada.vida ja confere o G1
            assert isinstance(v.motor, MotorCorpo) and v.motor.cc == bv.CONFIG_CORPO_QUIMICA
            assert v.motor.cc.ligada and v.motor.cc.digestao and v.motor.cc.vida and not v.motor.cc.drives_novos
            assert "corpo" in v.motor.estado() and v.motor.consequencias > 0
            cerebro = bv.do_braco(v.motor.politica).cerebro
            assert cerebro._corpo == v.motor.cc
            r = b.rejogar(LogDeEventos.de_jsonl(v.motor.log.para_jsonl()), v.espec)
            assert bv.resumo_motor(r) == bv.resumo_motor(v.motor) and bv._interno(r) == bv._interno(v.motor)


def test_o_p1_quimica_aprende_pelo_sinal_do_corpo():
    b = _bancada(dias=3)
    v = b.vida(bv.EspecVida("aleatorio", "P1-quimica", 101, None, "bola"))
    cerebro = bv.do_braco(v.motor.politica).cerebro
    com_sinal = [m for m in cerebro.motivos if "sinal_corpo" in m]
    assert com_sinal and len(com_sinal) == len(cerebro.motivos)        # o credito de toda decisao veio pelo corpo
    assert any(m["sinal_corpo"]["f"] != 0 for m in com_sinal)


def test_o_acoplado_com_o_corpo():
    b = _bancada(dias=3)
    v = b.vida(bv.EspecVida("incoerente", "P0-quimica", 101, None, "bola"))
    mesmo = b.acoplar(v, "P0-quimica", "nenhum")
    assert bv.resumo_motor(mesmo.motor) == bv.resumo_motor(v.motor)
    ac = b.acoplar(v, "P1-quimica", "nenhum")                             # acoplar ja rejoga o registro bit a bit (G1)
    assert isinstance(ac.motor, MotorCorpo) and ac.rotulo_braco == "P1-quimica<P0-quimica:nenhum"
    acoes_dono = lambda log: [(e.tick, e.valor) for e in log if e.tipo == "acao_usuario"]  # noqa: E731
    assert acoes_dono(ac.motor.log) == acoes_dono(v.motor.log)


def test_a_chave_corpo_da_config_troca_os_numeros_e_nao_as_subchaves():
    b = bv.bancada_da_config(_cfg(corpo={"taxa_digestao": 225000}))
    assert b.cfg_corpo == replace(bv.CONFIG_CORPO_QUIMICA, taxa_digestao=225000)
    v = b.vida(bv.EspecVida("atencioso", "P0-quimica", 101, None, "bola"))
    assert v.motor.cc.taxa_digestao == 225000
    bv.validar_config(_cfg(corpo={"taxa_digestao": 225000}))
    for sub in ("ligada", "digestao", "vida", "drives_novos", "gestos"):
        with pytest.raises(ValueError, match="sub-chaves"):
            bv.validar_config(_cfg(corpo={sub: True}))
    with pytest.raises(ValueError, match="sem braco com corpo"):
        bv.validar_config(_cfg(bracos=["P0-hoje"], corpo={"taxa_digestao": 225000}))
    with pytest.raises(ValueError, match="quimica"):                    # a bancada guarda a quimica; o regime liga o resto
        bv.Bancada(1, 16, cfg_corpo=replace(bv.CONFIG_CORPO_QUIMICA, vida=False))


def test_no_padrao_com_genoma_a_obediencia_fica_desligada_nos_dois_regimes():
    """O corpo exige a obediencia desligada (secao 2). Nos bracos do plano do corpo, o padrao com genoma usa o MotorPersonalidade com ela
    desligada nos dois regimes, como os mundos da bola e das frutas: o par G-HOJE difere so na quimica. Os bracos de antes nao mudam."""
    b = _bancada()
    vh = b.vida(bv.EspecVida("atencioso", "P0-hoje", 101, 202, "padrao"))
    vq = b.vida(bv.EspecVida("atencioso", "P0-quimica", 101, 202, "padrao"))
    v0 = b.vida(bv.EspecVida("atencioso", "P0", 101, 202, "padrao"))
    assert vh.motor.obediencia_desligada and vq.motor.obediencia_desligada and not v0.motor.obediencia_desligada
    assert isinstance(vq.motor, MotorCorpo) and not isinstance(vh.motor, MotorCorpo)


# ------------------------------------------------------------------ 3. as medidas da secao 5 e a dominancia pelos receptores


@pytest.mark.parametrize("mundo", ("bola", "padrao"))
def test_as_medidas_do_corpo(mundo):
    b = _bancada(dias=3, cc=CC_CANAIS)
    for braco, origem in (("P0-quimica", "sonda"), ("P1-quimica", "sinal"), ("P3-quimica", "sonda")):
        v = b.vida(bv.EspecVida("aleatorio", braco, 303, None, mundo))
        m = b.medir(v, SONDA)
        c = m["corpo"]
        assert c["regime"] == "quimica" and c["janela"] == [0, 3 * 1440]          # vida de 3 dias: a janela e a vida toda
        be = c["be"]
        assert be["n"] > 0 and 0.0 <= be["be"] <= 1.0 and be["be"] + be["oc"] <= 1.0 + 1e-12
        assert abs(sum(be["por_acao"].values()) - 1.0) < 1e-12 and be == c["be_vida"]
        assert 0.0 <= c["cuidado"]["privacao"] <= 1.0 and c["cuidado"]["n"] == len(v.motor.politica.estado_interno()["motivos"])
        assert c["drives_novos"] == {"disponivel": False, "motivo": bv.NOS_PENDENTES["corpo"]}
        assert c["corpo_final"] == v.motor.estado()["corpo"]
        d = m["dominancia"]
        assert d["pelo_corpo"] and d["origem"] == origem
        assert d["conferido_com_canais"] == d["conferido_com_motivo"] == (origem == "sinal")
        assert d["vida_toda"]["tempo_livre"]["n"] + d["vida_toda"]["resto"]["n"] > 0
    # sem corpo, nada de bloco do corpo, e a dominancia de antes
    m0 = b.medir(b.vida(bv.EspecVida("aleatorio", "P1-hoje", 303, None, mundo)), SONDA)
    assert m0["corpo"] is None and "pelo_corpo" not in m0["dominancia"]


def test_a_dominancia_pelo_corpo_falha_alto_quando_diverge(monkeypatch):
    b = _bancada(dias=2, cc=CC_CANAIS)
    v = b.vida(bv.EspecVida("aleatorio", "P1-quimica", 101, None, "bola"))
    original = bv.sinal_corpo_canais

    def mais_um(*a, **kw):
        out = dict(original(*a, **kw))
        out["fome"] += 1
        return out

    monkeypatch.setattr(bv, "sinal_corpo_canais", mais_um)
    with pytest.raises(RuntimeError, match="divergem"):
        b.medir(v, SONDA)
    monkeypatch.setattr(bv, "sinal_corpo_canais", original)
    orig_c = bv.contribuicoes_corpo
    monkeypatch.setattr(bv, "contribuicoes_corpo", lambda *a, **kw: {k: x + 1 for k, x in orig_c(*a, **kw).items()})
    with pytest.raises(RuntimeError, match="divergem"):
        b.medir(v, SONDA)


# ------------------------------------------------------------------ 4. o que espera a etapa 6 (e o contrato do mundo fisico)


@pytest.mark.parametrize("braco", sorted(PENDENTES))
def test_o_que_espera_a_etapa_6_falha_alto_com_o_no(braco):
    with pytest.raises(NotImplementedError, match=PENDENTES[braco]):
        bv.braco_de(braco)
    with pytest.raises(NotImplementedError):
        bv.validar_config(_cfg(bracos=[braco]))
    with pytest.raises(NotImplementedError):
        _bancada().vida(bv.EspecVida("atencioso", braco, 101, None, "bola"))


def test_os_bracos_do_plano_estao_declarados_como_o_plano_pede():
    B = bv.BRACOS
    assert {r: (B[r].regime, B[r].gestos) for r in PENDENTES} == {
        "P0-q": ("quimica", "sem_tapa"), "P1-q": ("quimica", "sem_tapa"), "P0-c": ("corpo", "sem_tapa"), "P1-c": ("corpo", "sem_tapa"),
        "P0-c-tapa": ("corpo", "tapa"), "P1-c-tapa": ("corpo", "tapa"), "P1-c-tapaX": ("corpo", "tapa_fruta"),
        "P1-c-frutas": ("corpo", "sem_tapa"), "P1-cw": ("corpo", "sem_tapa")}
    assert all(B[f"P{i}-hoje"].regime == "hoje" and B[f"P{i}-quimica"].regime == "quimica" for i in (0, 1, 3))
    assert B["P1-cw"] == replace(B["P1-c"], rotulo="P1-cw", no="corpo-A2.4", pesos_janela=True)


def test_a_trava_e_so_a_tabela(monkeypatch):
    """Sem as entradas, os bracos se resolvem. Desde a etapa 6 na main (#245, #247), a ConfigCorpo aceita as sub-chaves: o regime corpo
    monta drives_novos e gestos (quem tira as entradas do NOS_PENDENTES e o D)."""
    monkeypatch.setattr(bv, "NOS_PENDENTES", {})
    assert bv.braco_de("P1-c") is bv.BRACOS["P1-c"] and bv.braco_de("P1-q") is bv.BRACOS["P1-q"]
    cc = _bancada().cfg_corpo_de(bv.EspecVida("atencioso", "P1-c", 101, None, "bola"))
    assert cc.drives_novos and cc.gestos


def test_o_filtro_sem_gestos_falha_alto_com_o_no():
    with pytest.raises(NotImplementedError, match="tapa"):
        bv.filtro_de("sem_gestos")


def test_o_corpo_no_mundo_fisico_espera_o_contrato_dos_ganchos():
    with pytest.raises(NotImplementedError, match="consequencia_corpo"):
        bv.validar_config(_cfg(bracos=["P0-quimica"], mundos=["fisico"], lugares=["perto"]))
    with pytest.raises(NotImplementedError, match="consequencia_corpo"):
        _bancada().vida(bv.EspecVida("atencioso", "P1-quimica", 101, None, "fisico", lugar="perto"))
    bv.validar_config(_cfg(bracos=["P0-hoje"], mundos=["fisico"], lugares=["perto"]))     # o "hoje" roda no mundo fisico


# ------------------------------------------------------------------ 5. a config com o plano e a fumaca


def test_a_config_com_o_plano_do_corpo_valida():
    cfg = _cfg(bracos=["P0-hoje", "P1-hoje", "P3-hoje", "P0-quimica", "P1-quimica", "P3-quimica"],
               donos=["aleatorio", "relapso", "atencioso", "incoerente"], mundos=["bola", "padrao"], dias=14, orcamento=224,
               unidades={"bases": [33101], "k": 1, "prefixo": "corpo"}, plano="docs/PLANO_ANALISE_V2_CORPO_DRIVES.md")
    del cfg["sementes"]
    bv.validar_config(cfg)


def test_rodar_a_fumaca_do_corpo(tmp_path):
    cfg = json.loads((RAIZ / "experiments" / "configs" / "v2_corpo" / "fumaca.json").read_text(encoding="utf-8"))
    cfg.update(dias=2, orcamento=32, donos=["relapso"])                 # 2 unidades: o bootstrap da tabela pede pelo menos duas
    r = bv.rodar(cfg, tmp_path)
    n_vidas = 2 * 2 * 6                                                  # 2 unidades x 2 mundos x 6 bracos
    assert len(r["vidas"]) == n_vidas + 2 * (n_vidas // 6)               # mais os dois acoplados de cada celula
    medidas = json.loads((tmp_path / "medidas.json").read_text(encoding="utf-8"))
    for m in medidas.values():
        com_corpo = "quimica" in m["braco"].split("<")[0]
        assert (m["corpo"] is not None) == com_corpo, m["vida"]
        assert m["dominancia"].get("pelo_corpo", False) == com_corpo
    dom = json.loads((tmp_path / "dominancia.json").read_text(encoding="utf-8"))
    assert {"P1-quimica", "P1-hoje"} <= set(dom)
