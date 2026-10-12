"""V2, W-BANCADA-METABOLISMO: a etapa 2 do metabolismo na bancada (docs/TAREFA_V2_METABOLISMO.md, ME-6 e ME-7;
docs/PLANO_ANALISE_V2_CORPO_DRIVES.md, adendo 3, A3.1 a A3.3), com o #271 (o combustivel e a reserva no corpo, do B) na main.

O que se confere:
- A3.1: o metabolismo exatamente nos bracos do bloco do corpo, do tapa e do G (P0-q, P1-q, P0-c, P1-c, P0-c-tapa, P1-c-tapa, P1-c-tapaX,
  P1-c-frutas e P1-cw; os acoplados herdam pelo braco de destino); o G-HOJE e o banheiro sem ele; o metabolismo so com o corpo; a chave
  `corpo` da config e a cfg_corpo da bancada nao o ligam; `Bancada(metabolismo=False)` refaz a vida de antes (os gabaritos do G2);
- o motor dos bracos tem o combustivel e a reserva, e o resto do corpo e o do regime;
- A3.3: o bloco `metabolismo` das medidas, conferido contra uma recontagem por fora (a sonda propria no passo do corpo, o fim da vida e a
  conta do corpo); so nas vidas com o metabolismo;
- as medidas novas de metrics.py em dados com a resposta conhecida;
- A3.2, o passo 0: os tres pontos (o basal x 1/2, 1 e 2: 188/94, 375/187 e 750/374) antes de falhar alto com o no `gasto_atividades`; a
  trava e so a tabela (sem ela, a segunda trava); a fracao das 8 celulas juntas; a regra de escolha (a faixa, o empate, o "nao fechou");
  a config do passo 0 valida e e a do plano.
O G-P0C com o metabolismo (o P0-c decide igual ao P0-q) e os acoplados P1-q^ac e P1-c^ac ficam em tests/test_bancada_liga_gestos.py, que
roda os bracos com a bancada de sempre (agora com o metabolismo). So as sementes dos testes; nenhuma run do passo 0.
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
from digilab.config import ConfigCorpo  # noqa: E402
from digilab.events import LogDeEventos  # noqa: E402
from digilab.metrics import metabolismo_da_vida, tempo_comer_brincar  # noqa: E402
from digilab.treino import reproduzir_com_feedback  # noqa: E402

COM_METABOLISMO = {"P0-q", "P1-q", "P0-c", "P1-c", "P0-c-tapa", "P1-c-tapa", "P1-c-tapaX", "P1-c-frutas", "P1-cw"}
G_HOJE = ("P0-hoje", "P1-hoje", "P3-hoje", "P0-quimica", "P1-quimica", "P3-quimica")
SONDA = {"estados": 5, "amostras": 5, "semente": 101}
CFG_PASSO0 = RAIZ / "experiments" / "configs" / "v2_corpo" / "calibracao_passo0.json"


def _bancada(dias=2, **kw):
    return bv.Bancada(dias, 16 * dias, **kw)


# ------------------------------------------------------------------ 1. A3.1: quais bracos


def test_o_metabolismo_esta_nos_bracos_do_adendo_3():
    assert {r for r, b in bv.BRACOS.items() if b.metabolismo} == COM_METABOLISMO
    for r in G_HOJE:
        assert not bv.BRACOS[r].metabolismo, r                                  # o G-HOJE fica sem (A3.1)
    for r, b in bv.BRACOS.items():
        if b.metabolismo:
            assert b.regime in ("quimica", "corpo") and b.banheiro is None, r
    assert "metabolismo" in bv.SUBCHAVES_CORPO


def test_o_metabolismo_so_existe_com_o_corpo(monkeypatch):
    monkeypatch.setitem(bv.BRACOS, "P1-x", replace(bv.BRACOS["P1"], rotulo="P1-x", metabolismo=True))
    with pytest.raises(ValueError, match="metabolismo so existe com o corpo"):
        bv.braco_de("P1-x")


def test_a_chave_corpo_e_a_cfg_da_bancada_nao_ligam_o_metabolismo():
    cfg = {"bracos": ["P0-q"], "donos": ["atencioso"], "sementes": [101], "mundos": ["bola"], "dias": 2, "orcamento": 32,
           "sonda": SONDA, "bootstrap": {"reamostragens": 10, "semente": 1, "nivel": 0.95}}
    bv.validar_config(cfg)
    with pytest.raises(ValueError, match="metabolismo"):
        bv.validar_config({**cfg, "corpo": {"metabolismo": True}})
    with pytest.raises(ValueError, match="metabolismo"):
        bv.Bancada(2, 32, cfg_corpo=replace(bv.CONFIG_CORPO_QUIMICA, metabolismo=True))


@pytest.mark.parametrize("braco,mundo", (("P0-q", "bola"), ("P1-q", "padrao"), ("P0-c", "bola"), ("P1-c", "iguais_frutas"),
                                         ("P1-c-tapa", "bola"), ("P1-cw", "bola")))
def test_o_motor_dos_bracos_tem_o_combustivel(braco, mundo):
    b = _bancada()
    v = b.vida(bv.EspecVida("atencioso", braco, 101, None, mundo))              # Bancada.vida ja confere o G1
    cc = v.motor.cc
    assert cc.metabolismo and cc.digestao and cc.vida
    assert cc.drives_novos == cc.gestos == (bv.BRACOS[braco].regime == "corpo")
    q = v.motor.corpo.q
    assert {"combustivel", "reserva"} <= set(q) and 0 <= q["combustivel"] <= cc.escala
    assert sum(v.motor.corpo.contas_metabolismo.values()) > 0
    # sem o metabolismo na bancada, o mesmo braco e o de antes do adendo 3
    a = _bancada(metabolismo=False).vida(bv.EspecVida("atencioso", braco, 101, None, mundo))
    assert not a.motor.cc.metabolismo and "combustivel" not in a.motor.corpo.q


@pytest.mark.parametrize("braco", G_HOJE)
def test_o_g_hoje_nao_muda_com_a_chave_da_bancada(braco):
    """Os bracos sem o metabolismo saem iguais com a bancada de sempre e com `metabolismo=False` (a chave so tira, nunca liga)."""
    for mundo in ("bola", "padrao"):
        e = bv.EspecVida("aleatorio", braco, 202, None, mundo)
        com, sem = _bancada().vida(e), _bancada(metabolismo=False).vida(e)
        assert bv.resumo_motor(com.motor) == bv.resumo_motor(sem.motor) and bv._interno(com.motor) == bv._interno(sem.motor)
        assert not getattr(getattr(com.motor, "cc", None), "metabolismo", False)


def test_o_acoplado_herda_o_metabolismo_pelo_braco_de_destino():
    b = _bancada()
    o = b.vida(bv.EspecVida("atencioso", "P0-q", 101, None, "bola"))
    assert b.acoplar(o, "P1-c", "nenhum").motor.cc.metabolismo                  # o P1-c^ac
    assert not b.acoplar(o, "P1-quimica", "nenhum").motor.cc.metabolismo


# ------------------------------------------------------------------ 2. A3.3: a medida, conferida por fora


def _recontar(b, v) -> list:
    """O replay da vida com uma sonda propria (outro codigo, o mesmo passo do corpo): (tick, dormindo, combustivel, reserva) por tick."""
    anotado = []
    fm_base = b.fabrica_motor(v.espec)

    def fm(*a, **kw):
        motor = fm_base(*a, **kw)
        original = motor.corpo.passo

        def passo(antes, *aa, **kk):
            r = original(antes, *aa, **kk)
            anotado.append((antes.tick, antes.dormindo, motor.corpo.q["combustivel"], motor.corpo.q["reserva"]))
            return r
        motor.corpo.passo = passo
        return motor
    m = reproduzir_com_feedback(LogDeEventos.de_jsonl(v.motor.log.para_jsonl()), b.fabrica_politica(v.espec), semente=v.espec.semente,
                                fabrica_motor=fm)
    assert bv.resumo_motor(m) == bv.resumo_motor(v.motor)
    return anotado


@pytest.mark.parametrize("braco,mundo", (("P0-q", "bola"), ("P1-c", "bola"), ("P1-q", "padrao"), ("P1-c", "iguais_frutas")))
def test_a_medida_do_metabolismo_confere_com_uma_recontagem(braco, mundo):
    b = _bancada()
    v = b.vida(bv.EspecVida("atencioso", braco, 202, None, mundo))
    met = b.medir(v, SONDA)["corpo"]["metabolismo"]
    anotado = _recontar(b, v)
    assert len(anotado) == b.dias * bv.TICKS_POR_DIA and [t for t, *_ in anotado] == list(range(len(anotado)))
    limiar = v.motor.cc.falta_limiar
    acordados = [c for _, dormindo, c, _ in anotado if not dormindo]
    assert met["acordado"] == len(acordados) and met["acordado_com_falta"] == sum(1 for c in acordados if c < limiar)
    assert met["fracao"] == met["acordado_com_falta"] / met["acordado"]
    inicios = sum(1 for k, (_, _, c, _) in enumerate(anotado) if c < limiar and (k == 0 or anotado[k - 1][2] >= limiar))
    assert met["disparos"] == inicios and met["ticks_com_falta"] == sum(1 for *_, c, _ in anotado if c < limiar)
    # o fim de cada dia e o fim da vida
    assert [d["combustivel"] for d in met["por_dia"]] == [anotado[(k + 1) * bv.TICKS_POR_DIA - 1][2] for k in range(b.dias)]
    assert met["por_dia"][-1] == {"dia": b.dias, "combustivel": v.motor.corpo.q["combustivel"], "reserva": v.motor.corpo.q["reserva"]}
    assert met["contas"] == v.motor.corpo.contas_metabolismo and met["fim"] == b.dias * bv.TICKS_POR_DIA
    assert met["tempo_comer_brincar"]["n"] >= 0


def test_sem_o_metabolismo_nao_ha_o_bloco():
    b = _bancada()
    for braco in ("P1-quimica", "P0-hoje"):
        m = b.medir(b.vida(bv.EspecVida("atencioso", braco, 101, None, "bola")), SONDA)
        assert "metabolismo" not in (m.get("corpo") or {})
    v = _bancada(metabolismo=False).vida(bv.EspecVida("atencioso", "P1-c", 101, None, "bola"))
    assert "metabolismo" not in _bancada(metabolismo=False).medir(v, SONDA)["corpo"]


def test_a_sonda_que_nao_cobre_a_vida_falha_alto(monkeypatch):
    b = _bancada()
    v = b.vida(bv.EspecVida("atencioso", "P0-q", 101, None, "bola"))
    monkeypatch.setattr(bv, "sondar_metabolismo", lambda corpo, destino: None)   # nenhuma anotacao
    with pytest.raises(RuntimeError, match="sonda do metabolismo"):
        b.medir(v, SONDA)


# ------------------------------------------------------------------ 3. as medidas novas, em dados com a resposta conhecida


def test_metabolismo_da_vida_em_dados_conhecidos():
    # 2 dias de 4 ticks; limiar 10; dorme nos ticks 2 e 6
    sonda = [(0, False, 12, 5), (1, False, 9, 5), (2, True, 8, 5), (3, False, 11, 6),
             (4, False, 7, 6), (5, False, 7, 6), (6, True, 10, 7), (7, False, 9, 7)]
    r = metabolismo_da_vida(sonda, 10, 4)
    assert r["acordado"] == 6 and r["acordado_com_falta"] == 4 and r["fracao"] == 4 / 6
    assert r["disparos"] == 3 and r["ticks_com_falta"] == 5                     # 1-2, 4-5, 7 (o 10 nao e falta: estritamente abaixo)
    assert r["por_dia"] == [{"dia": 1, "combustivel": 11, "reserva": 6}, {"dia": 2, "combustivel": 9, "reserva": 7}]
    assert metabolismo_da_vida([(0, False, 1, 0), (1, True, 1, 0)], 10, 2)["disparos"] == 1   # o primeiro tick ja com falta conta
    assert metabolismo_da_vida([(0, True, 1, 0)], 10, 1)["fracao"] is None
    for ruim, tpd in (([(0, False, 1, 0), (2, False, 1, 0)], 2), ([(0, False, 1, 0)], 2), ([], 1)):
        with pytest.raises(ValueError):
            metabolismo_da_vida(ruim, 10, tpd)


def test_tempo_comer_brincar_em_dados_conhecidos():
    decs = [(0, "brincar"), (15, "comer"), (30, "brincar"), (45, "ocioso"), (60, "brincar"), (75, "comer"), (120, "brincar")]
    r = tempo_comer_brincar(decs)
    assert r == {"n": 3, "media": (15 + 45 + 45) / 3, "mediana": 45}
    assert tempo_comer_brincar([(0, "comer"), (15, "brincar"), (30, "brincar")])["mediana"] == 22.5
    assert tempo_comer_brincar([(0, "brincar")]) == {"n": 0, "media": None, "mediana": None}
    with pytest.raises(ValueError):
        tempo_comer_brincar([(30, "comer"), (15, "brincar")])


# ------------------------------------------------------------------ 4. A3.2: o passo 0, montado e sem rodar


def _cfg_passo0() -> dict:
    return json.loads(CFG_PASSO0.read_text(encoding="utf-8"))


def test_a_config_do_passo_0_e_a_do_plano():
    cfg = _cfg_passo0()
    bv.validar_config(cfg)
    assert cfg["bracos"] == [bv.PASSO0_BRACO] and cfg["plano"] == "docs/PLANO_ANALISE_V2_CORPO_DRIVES.md"
    assert cfg["unidades"] == {"bases": [33101, 33202, 33303, 33404, 33505], "k": 4, "prefixo": "corpo"}
    assert len(cfg["donos"]) * len(cfg["mundos"]) == 8 and set(cfg["mundos"]) == {"bola", "padrao"}
    assert len(bv.unidades_derivadas(cfg["unidades"]["bases"], cfg["unidades"]["k"], "corpo")) == 20
    b = bv.bancada_da_config(cfg)
    assert b.montagem == "completa" and b.metabolismo and b.cfg_lobos == bv.cfg_lobos_do_ponto("T3")
    assert bv.BRACOS[bv.PASSO0_BRACO].metabolismo


def test_os_pontos_do_passo_0_e_a_trava(monkeypatch):
    cfg = _cfg_passo0()
    base = ConfigCorpo()
    assert (base.gasto_basal_acordado, base.gasto_basal_dormindo) == (375, 187)
    capturados = []
    original = bv._escalar
    monkeypatch.setattr(bv, "_escalar", lambda v, n, d: capturados.append((v, n, d, original(v, n, d))) or original(v, n, d))
    with pytest.raises(NotImplementedError, match="gasto_atividades"):
        bv.pontos_passo0(cfg)
    assert [c[3] for c in capturados] == [188, 94, 375, 187, 750, 374]          # o 1/2 arredondado para cima (registro)
    # a trava e so a tabela: sem a entrada, a segunda trava (a fiacao do fator entra com o campo do B)
    monkeypatch.setattr(bv, "NOS_PENDENTES", {})
    with pytest.raises(NotImplementedError, match="fiacao do fator"):
        bv.pontos_passo0(cfg)
    with pytest.raises(ValueError, match="so o P0-q"):
        bv.pontos_passo0({**cfg, "bracos": ["P0-q", "P1-q"]})


def test_cada_ponto_do_passo_0_valida_e_monta_o_basal():
    """Os tres pontos, montados pela mesma conta do `pontos_passo0`, sao configs validas e a bancada deles tem o basal escalado."""
    cfg = _cfg_passo0()
    for num, den in bv.PASSO0_MULTIPLICADORES:
        acordado, dormindo = bv._escalar(375, num, den), bv._escalar(187, num, den)
        ponto = {**cfg, "corpo": {"gasto_basal_acordado": acordado, "gasto_basal_dormindo": dormindo}}
        bv.validar_config(ponto)
        cc = bv.bancada_da_config(ponto).cfg_corpo
        assert (cc.gasto_basal_acordado, cc.gasto_basal_dormindo) == (acordado, dormindo) and not cc.metabolismo


def test_a_fracao_do_passo_0_junta_as_8_celulas():
    def m(vida, braco, acordado, falta, origem=None, met=True):
        corpo = {"metabolismo": {"acordado": acordado, "acordado_com_falta": falta}} if met else {}
        return {"vida": vida, "braco": braco, "origem": origem, "corpo": corpo}
    medidas = {"a": m("a", "P0-q", 100, 10), "b": m("b", "P0-q", 300, 50), "c": m("c", "P1-q", 100, 100),
               "d": m("d", "P0-q", 100, 100, origem="x")}
    assert bv.fracao_falta_passo0(medidas) == {"vidas": 2, "acordado": 400, "acordado_com_falta": 60, "fracao": 60 / 400}
    with pytest.raises(ValueError, match="sem a medida"):
        bv.fracao_falta_passo0({**medidas, "e": m("e", "P0-q", 1, 0, met=False)})
    with pytest.raises(ValueError):
        bv.fracao_falta_passo0({"c": medidas["c"]})


@pytest.mark.parametrize("fracoes,ponto,fechou", (
    ({(1, 2): 0.40, (1, 1): 0.20, (2, 1): 0.10}, [1, 1], True),                 # o central passa: fica ele
    ({(1, 2): 0.20, (1, 1): 0.40, (2, 1): 0.10}, [1, 2], True),                 # empate de |log2| (1/2 e 2): o menor gasto
    ({(1, 2): 0.40, (1, 1): 0.35, (2, 1): 0.25}, [2, 1], True),                 # so o 2 passa
    ({(1, 2): 0.05, (1, 1): 0.31, (2, 1): 0.60}, [1, 2], True),                 # a borda da faixa passa
    ({(1, 2): 0.50, (1, 1): 0.33, (2, 1): 0.01}, [1, 1], False),                # nenhum: o mais perto do centro (0,175)
    ({(1, 2): 0.03, (1, 1): 0.02, (2, 1): 0.01}, [1, 2], False),
))
def test_a_regra_de_escolha_do_passo_0(fracoes, ponto, fechou):
    r = bv.escolha_passo0(fracoes)
    assert r["ponto"] == ponto and r["fechou"] is fechou and r["fracao"] == fracoes[tuple(ponto)]
    assert (r.get("registro") == "nao fechou") is (not fechou)


def test_a_regra_do_passo_0_pede_os_tres_pontos():
    with pytest.raises(ValueError, match="tres pontos"):
        bv.escolha_passo0({(1, 1): 0.2, (2, 1): 0.1})
