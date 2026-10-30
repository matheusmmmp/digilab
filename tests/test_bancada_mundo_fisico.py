"""V2, W-BANCADA-MUNDO (rodada 17): as faixas e o prefixo do banheiro, e o mundo fisico na bancada (docs/TAREFA_V2_MUNDO_FISICO.md,
secao 9, etapa 4; docs/PLANO_ANALISE_V2_MUNDO_FISICO.md).

O que se confere:
- as faixas do banheiro (PLANO_ANALISE_V2_BANHEIRO, secao 10) e o prefixo "banheiro", sem colisao, como no test_faixas_r17;
- os mundos `fisico` e `fisico_afastado` no MotorMundo, com o lugar do dono como fator da celula;
- o P0z, o cerebro "instinto" no mundo fisico e as runs com plano nele resolvem desde a W-LIGA-MUNDO (o gate do P0 com lobos = o
  instinto do mundo fica em tests/test_bancada_liga_mundo.py);
- o dono so com o cuidado (PMF-3): o sem_ensino ao vivo, o orcamento fechando com os sinais retirados;
- G1 de toda vida e acoplado; as quedas iguais entre os bracos (G-NUMS);
- as medidas do plano, de metrics.py, em vidas reais, com as visitas conferidas contra as do motor.
So as sementes dos testes.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
from digilab.config import LAYOUT_MUNDO_AFASTADO, LAYOUT_MUNDO_PADRAO  # noqa: E402
from digilab.events import AcaoUsuario, LogDeEventos  # noqa: E402
from digilab.metrics import custo_viagem  # noqa: E402
from digilab.mundo import ESTILOS_LUGAR, MotorMundo, centro_da_celula  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402

DONOS = ("atencioso", "relapso", "aleatorio", "incoerente")
SONDA = {"estados": 5, "amostras": 5, "semente": 101}
BASES_BANHEIRO = {"calibracao": (37101, 37202, 37303, 37404, 37505), "validacao": (38101, 38202, 38303, 38404, 38505)}
BASES_MUNDO = {"calibracao": (31101, 31202, 31303, 31404, 31505), "validacao": (32101, 32202, 32303, 32404, 32505)}
BASES_CORPO = {"calibracao": (33101, 33202, 33303, 33404, 33505), "validacao": (34101, 34202, 34303, 34404, 34505)}
PLANOS = (("experimento-maior", bv.BASES_EXPERIMENTO_MAIOR), ("n6", bv.BASES_N6), ("n7", bv.BASES_N7),
          ("comparacao-cerebros", bv.BASES_COMPARACAO), ("mundo", BASES_MUNDO), ("corpo", BASES_CORPO),
          ("banheiro", BASES_BANHEIRO))
K = 40


def _numeros_das_configs() -> set[int]:
    achados: set[int] = set()

    def andar(o, chave=""):
        marca = "semente" in chave.lower() or "base" in chave.lower()
        if isinstance(o, dict):
            for k, v in o.items():
                andar(v, k)
        elif isinstance(o, list):
            for v in o:
                andar(v, chave)
        elif isinstance(o, int) and not isinstance(o, bool) and marca:
            achados.add(o)

    for p in (RAIZ / "experiments" / "configs").rglob("*.json"):
        andar(json.loads(p.read_text(encoding="utf-8")))
    return achados


def _cfg(**troca) -> dict:
    cfg = {"bracos": ["P0", "P1"], "donos": ["atencioso"], "sementes": [101], "dias": 1, "orcamento": 16, "sonda": SONDA,
           "bootstrap": {}, "mundos": ["fisico"], "lugares": ["perto"]}
    cfg.update(troca)
    return cfg


def _vida(dono="atencioso", braco="P0", semente=101, lugar="perto", mundo="fisico", dias=2, **kw):
    b = bv.Bancada(dias, 16 * dias, **kw)
    return b, b.vida(bv.EspecVida(dono, braco, semente, None, mundo, lugar=lugar))


# ------------------------------------------------------------------ 1. as faixas e o prefixo do banheiro


def test_faixas_do_banheiro_reservadas_com_fonte_e_sem_colisao():
    faixas = {(lo, hi): fonte for lo, hi, fonte in bv.FAIXAS_RESERVADAS}
    for faixa in ((37101, 37505), (38101, 38505)):
        assert "PLANO_ANALISE_V2_BANHEIRO" in faixas[faixa]
    for fase, bs in BASES_BANHEIRO.items():
        for b in bs:
            fonte = bv.na_faixa_reservada(b)
            assert fonte is not None and "banheiro" in fonte and ("calibracao" in fonte) == (fase == "calibracao"), (b, fonte)
    los = sorted((lo, hi) for lo, hi, _ in bv.FAIXAS_RESERVADAS)
    assert all(a[1] < b[0] for a, b in zip(los, los[1:]))                      # nenhuma faixa colide com outra
    numeros = _numeros_das_configs()
    for lo, hi in ((37101, 37505), (38101, 38505)):
        assert not any(q_lo <= hi and lo <= q_hi for q_lo, q_hi, _ in bv.FAIXAS_QUEIMADAS)
        assert not [n for n in numeros if lo <= n <= hi], (lo, hi)


def test_prefixo_do_banheiro_e_unidades_sem_colisao():
    assert "banheiro" in bv.PREFIXOS_UNIDADES
    u = bv.unidades_derivadas(BASES_BANHEIRO["calibracao"], 4, "banheiro")[5]
    assert u["semente"] == derivar_semente("banheiro", u["base"], u["k"])
    assert u["genoma"] == derivar_semente("banheiro-genoma", u["base"], u["k"])
    todos, novos = [], []
    for prefixo, bases in PLANOS:
        for fase in ("calibracao", "validacao"):
            us = bv.unidades_derivadas(bases[fase], K, prefixo)
            vs = [x["semente"] for x in us] + [x["genoma"] for x in us]
            todos += vs
            novos += vs if prefixo == "banheiro" else []
    assert len(set(todos)) == len(todos)                                         # nem entre planos, nem entre fases
    numeros = _numeros_das_configs()
    for v in novos:
        assert bv.na_faixa_reservada(v) is None and v not in numeros and v not in bv.SEMENTES_TESTE, v


# ------------------------------------------------------------------ 2. o mundo fisico declarado


def test_os_mundos_fisicos_e_o_layout_afastado():
    for nome, layout in (("fisico", "padrao"), ("fisico_afastado", "afastado")):
        m = bv.mundo_de(nome)
        assert (m.condicao, m.fisico, m.ambiente, m.frutas, m.bola) == ("iguais", layout, True, False, None)
    b = bv.Bancada(1, 16)
    assert b.cfg_mundo_de(bv.mundo_de("fisico")).layout == LAYOUT_MUNDO_PADRAO
    afastado = b.cfg_mundo_de(bv.mundo_de("fisico_afastado"))
    assert afastado.layout == LAYOUT_MUNDO_AFASTADO and afastado.mult_queda == b.cfg_mundo.mult_queda
    with pytest.raises(ValueError):
        b.cfg_mundo_de(bv.mundo_de("padrao"))
    # o layout afastado so muda os troncos: o custo de viagem cresce
    custos = {}
    for nome in ("fisico", "fisico_afastado"):
        cm = b.cfg_mundo_de(bv.mundo_de(nome))
        custos[nome] = custo_viagem({i: centro_da_celula((x, y), cm) for i, x, y, _ in cm.layout.arvores})
    assert sum(custos["fisico_afastado"].values()) > sum(custos["fisico"].values())


def test_o_motor_e_o_mundo_do_plano():
    b, v = _vida(braco="P1")
    m = v.motor
    assert isinstance(m, MotorMundo) and m.cmf.ligada and not m.cf.ligada and not m.cb.ligada
    assert m.efeito_frutas == {"a": 0.0, "b": 0.0, "c": 0.0}                     # PMF-7: o mundo "iguais"
    assert m.obediencia_desligada


# ------------------------------------------------------------------ 3. o instinto do mundo ligado (W-LIGA-MUNDO)


def test_p0z_e_o_instinto_do_mundo_resolvem():
    assert bv.BRACOS["P0z"].instinto_mundo == "sem_explorar" and "instinto_mundo" not in bv.NOS_PENDENTES
    assert bv.braco_de("P0z") is bv.BRACOS["P0z"]
    bv.validar_config(_cfg(bracos=["P0", "P0z"]))
    bv.validar_config(_cfg(bracos=["P0z", "P0", "P1"], acoplados=[{"origem": "P0z", "destino": "P0", "filtro": "nenhum"},
                                                                    {"origem": "P0z", "destino": "P1", "filtro": "nenhum"}]))
    com_plano = _cfg(unidades={"bases": [31101], "k": 1, "prefixo": "mundo"}, plano="docs/PLANO_ANALISE_V2_MUNDO_FISICO.md")
    del com_plano["sementes"]
    bv.validar_config(com_plano)                                        # a run com plano no mundo fisico nao espera mais o no
    b = bv.Bancada(1, 16)
    for cerebro in ("instinto", "lobos"):                               # o P0z e o instinto do mundo sem explorar em qualquer cerebro
        pz = b.politica(bv.EspecVida("atencioso", "P0z", 101, None, "fisico", cerebro, "perto")).cerebro
        assert type(pz).__name__ == "PoliticaInstintoMundo" and pz.sem_explorar
    p0 = b.politica(bv.EspecVida("atencioso", "P0", 101, None, "fisico", "instinto", "perto")).cerebro
    assert type(p0).__name__ == "PoliticaInstintoMundo" and not p0.sem_explorar
    with pytest.raises(ValueError, match="mundo fisico"):              # fora do mundo fisico o P0z nao existe
        b.politica(bv.EspecVida("atencioso", "P0z", 101))
    with pytest.raises(ValueError, match="instinto do mundo so no P0"):
        b.politica(bv.EspecVida("atencioso", "P1", 101, None, "fisico", "instinto", "perto"))


def test_o_lugar_so_existe_no_mundo_fisico():
    b = bv.Bancada(1, 16)
    with pytest.raises(ValueError, match="lugar"):
        b.vida(bv.EspecVida("atencioso", "P0", 101, lugar="perto"))
    with pytest.raises(ValueError, match="lugar"):
        b.vida(bv.EspecVida("atencioso", "P0", 101, None, "fisico"))
    with pytest.raises(ValueError, match="lugar"):
        b.vida(bv.EspecVida("atencioso", "P0", 101, None, "fisico", lugar="sofa"))
    for ruim in ({"lugares": ["sofa"]}, {"lugares": ["perto", "perto"]}, {"lugares": []}):
        with pytest.raises(ValueError):
            bv.validar_config(_cfg(**ruim))
    with pytest.raises(ValueError):
        bv.validar_config(_cfg(mundos=["padrao"]))                          # lugares sem o mundo fisico
    with pytest.raises(ValueError):
        bv.validar_config({k: v for k, v in _cfg().items() if k != "lugares"})
    with pytest.raises(TypeError):
        bv.validar_config(_cfg(mundo={"nao_existe": 1}))
    bv.validar_config(_cfg(mundo={"mult_queda": 2.0}))
    assert bv.bancada_da_config(_cfg(mundo={"mult_queda": 2.0})).cfg_mundo.mult_queda == 2.0
    assert bv.EspecVida("atencioso", "P0", 101, None, "fisico", lugar="perto").nome == "atencioso-P0~fisico~perto@101"
    assert bv.EspecVida("atencioso", "P0", 101).nome == "atencioso-P0@101"          # os nomes de antes nao mudam


# ------------------------------------------------------------------ 4. as vidas: o dono so com o cuidado, o orcamento, G1


@pytest.mark.parametrize("dono", DONOS)
def test_vidas_do_mundo_fisico_dono_so_com_o_cuidado_e_g1(dono):
    for braco in ("P0", "P1", "P3"):
        for lugar in ESTILOS_LUGAR:
            b, v = _vida(dono, braco, 202, lugar)                       # a vida ja rejoga o log bit a bit (Bancada.vida -> G1)
            log = v.motor.log
            acoes = [str(e.valor) for e in log if e.tipo == "acao_usuario"]
            assert not set(acoes) & bv.SINAIS                            # PMF-3: o elogio e a bronca nao chegam ao motor
            assert AcaoUsuario.ALIMENTAR.value not in acoes              # o alimentar virou deixar_comida
            gestos = bv.contar_gestos_mundo(log)
            assert gestos == len(v.motor.deixadas) + len(v.motor.bolas_deixadas)
            assert v.interacoes == len(acoes) + gestos and v.interacoes + v.retirados == b.orcamento
            if lugar == "comedouro":
                assert {(d["x"], d["y"]) for d in v.motor.deixadas} <= {v.motor.comedouro}
            r = b.rejogar(LogDeEventos.de_jsonl(log.para_jsonl()), v.espec)
            assert bv.resumo_motor(r) == bv.resumo_motor(v.motor)
            assert bv._interno(r) == bv._interno(v.motor)
            if braco == "P3":                                            # o P3 aprende com o dono: aqui o dono nao ensina
                assert bv.do_braco(v.motor.politica).sinais_entregues == 0


def test_o_atencioso_teria_ensinado_e_os_sinais_contam_no_orcamento():
    _, v = _vida("atencioso", "P0", 101, "perto", dias=3)
    assert v.retirados > 0                                               # o atencioso elogia e repreende; o filtro os tirou
    _, w = _vida("relapso", "P0", 101, "perto", dias=3)
    assert w.interacoes + w.retirados == 48


def test_numeros_comuns_entre_os_bracos():
    """G-NUMS na bancada: na mesma semente, as quedas das arvores (o fluxo mundo-arvores) sao as mesmas em todo braco e lugar."""
    quedas = set()
    for braco in ("P0", "P1", "P3"):
        for lugar in ESTILOS_LUGAR:
            _, v = _vida("aleatorio", braco, 303, lugar, dias=3)
            quedas.add(json.dumps([(q["tick"], q["arvore"], q["sorteadas"], q["pontos"]) for q in v.motor.quedas]))
    assert len(quedas) == 1 and json.loads(quedas.pop())


def test_o_acoplado_no_mundo_fisico():
    b, v = _vida("incoerente", "P0", 101, "longe", dias=3)
    # no proprio braco sem filtro e a vida de origem
    mesmo = b.acoplar(v, "P0", "nenhum")
    assert bv.resumo_motor(mesmo.motor) == bv.resumo_motor(v.motor)
    # o P1 no registro do P0 (o encanamento do P1^ac do adendo 1): os mesmos gestos, nos mesmos ticks e lugares
    ac = b.acoplar(v, "P1", "nenhum")
    gestos = lambda log: [(e.tick, e.tipo, e.valor) for e in log if e.tipo in ("deixar_comida", "deixar_bola")]  # noqa: E731
    assert gestos(ac.motor.log) == gestos(v.motor.log) and gestos(v.motor.log)
    assert ac.interacoes == v.interacoes and ac.espec.lugar == "longe"
    assert ac.rotulo_braco == "P1<P0:nenhum"


# ------------------------------------------------------------------ 5. as medidas do plano


def test_medidas_do_mundo_fisico_em_vidas_reais(monkeypatch):
    achou = None
    for semente in (101, 202, 303, 404, 505):
        for lugar in ESTILOS_LUGAR:
            b, v = _vida("aleatorio", "P1", semente, lugar, dias=3)
            if v.motor.visitas:
                achou = (b, v)
                break
        if achou:
            break
    assert achou, "nenhuma vida com visita as manchas nas sementes dos testes"
    b, v = achou
    m = b.medir(v, SONDA)
    mf = m["mundo_fisico"]
    assert m["lugar"] == v.espec.lugar and m["retirados"] == v.retirados
    assert mf["janela"] == [0, 3 * 1440]                                 # vida de 3 dias: a janela e a vida toda
    assert 0.0 <= mf["d_fe"]["d_fe"] <= 1.0 and mf["d_fe"]["n"] == len(v.motor.decisoes_mundo)
    assert 0.0 <= mf["cuidado"]["privacao"] <= 1.0 and mf["horas_acordado"] > 0
    assert mf["quedas"] == len(v.motor.quedas) and mf["deixadas"] == len(v.motor.deixadas)
    feitas = [x for x in mf["visitas"] if not x["censurada"]]
    assert len(feitas) == len(v.motor.visitas)
    assert all(x["custo_viagem"] is not None for x in mf["visitas"])
    assert set(mf["permanencia_custo"]) >= {"n", "inclinacao"} and set(mf["taxa_no_abandono"]) >= {"razoes", "media_vida"}
    # a conferencia das visitas contra o motor falha alto (o replay de medicao com uma visita a menos no registro do motor)
    original = bv.Bancada.medidas_mundo

    def com_visita_a_menos(self, vida, motor, reg):
        motor.visitas = motor.visitas[1:]
        return original(self, vida, motor, reg)

    monkeypatch.setattr(bv.Bancada, "medidas_mundo", com_visita_a_menos)
    with pytest.raises(RuntimeError, match="visitas"):
        b.medir(v, SONDA)


def test_rodar_a_fumaca_do_mundo(tmp_path):
    cfg = json.loads((RAIZ / "experiments" / "configs" / "v2_mundo" / "fumaca.json").read_text(encoding="utf-8"))
    cfg.update(dias=2, orcamento=32, donos=["relapso"])                 # 2 unidades: o bootstrap da tabela pede pelo menos duas
    r = bv.rodar(cfg, tmp_path)
    n_vidas = 2 * 2 * 3 * 4                                              # 2 unidades x 2 mundos x 3 lugares x 4 bracos (P0z incluso)
    assert len(r["vidas"]) == n_vidas + 3 * (n_vidas // 4)               # mais P1<P0, P0<P0z e P1<P0z de cada celula
    t = r["tabelas"]["relapso"]
    assert {"P0z", "P0<P0z:nenhum", "P1<P0z:nenhum"} <= set(t["d_fe"]["bracos"])
    assert {"d_fe", "privacao_janela", "permanencia_media", "fracao_fora_de_privacao"} <= set(t)
    meta = json.loads((tmp_path / "meta.json").read_text(encoding="utf-8"))
    assert meta["mundo_sha256"] and meta["config"]["lugares"] == ["comedouro", "perto", "longe"]
    medidas = json.loads((tmp_path / "medidas.json").read_text(encoding="utf-8"))
    assert all(m["mundo_fisico"]["d_fe"]["n"] > 0 for m in medidas.values())
    assert {m["lugar"] for m in medidas.values()} == set(meta["config"]["lugares"])
