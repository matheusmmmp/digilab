"""O orgao da tela no corpo (GOSTO_VISUAL, P1b; docs/ESPEC_GOSTO_VISUAL_P1.md, secoes 2, 4 e 8; GV-16, GV-17, GV-18, GV-21 e GV-23 pela
recomendacao, D-GV-P1-1).

- desligada (a ConfigTela padrao): nenhum quimico, receptor, emissor ou estimulo da tela existe, e o corpo e o de hoje (as mesmas
  operacoes dao os mesmos numeros; o gabarito byte a byte e o tests/test_gabarito_gosto_visual.py);
- ligada sem o mundo fisico, sem `drives_novos` ou sem `gestos`: falha alto;
- a adaptacao anda para I e decai sem estimulo (o interesse que se gasta e volta); o `novidade_tela` cai com o mesmo estimulo e sobe quando
  ele muda; o tick sem `sentir_tela` falha alto;
- os emissores: o estresse acima do corte (e nao abaixo), o susto so no salto de volume, o agrado na tristeza, o assistir no tedio (so com
  a tela ligada, com a variedade DS-4);
- tudo em inteiros e deterministico.
"""
from __future__ import annotations

import random
import sys
from dataclasses import fields, replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab.config import (CONFIG_CORPO_BANHEIRO, CONFIG_CORPO_DRIVES, CONFIG_CORPO_METABOLISMO, CONFIG_PADRAO, CONFIG_TELA,  # noqa: E402
                            ConfigCorpo, ConfigTela)
from digilab.corpo import (ATIVIDADE_TELA, CANAIS_ESTRESSE_TELA, CANAIS_TELA, PARAMETROS_TELA, PREFIXO_ADAPTACAO,  # noqa: E402
                           RECEPTOR_NOVIDADE_TELA, Corpo, div_arred, grafo_do_corpo, k_meia_vida, passo_adaptacao, passo_meia_vida,
                           quimicos_de, taxas_de, todos_receptores_tela)
from digilab.corpo_grafo import GrafoInvalido, ReceptorSoma, checar  # noqa: E402
from digilab.events import AcaoPet, AcaoUsuario  # noqa: E402
from digilab.motor_corpo import PercepcaoCorpo  # noqa: E402
from digilab.state import Estado  # noqa: E402

S = 1024
TELA = ConfigTela(ligada=True)
CC = CONFIG_CORPO_DRIVES                                       # a etapa 6 inteira: drives_novos e gestos
COMBOS = {"ligada": ConfigCorpo(ligada=True), "quimica": ConfigCorpo(ligada=True, digestao=True, vida=True), "drives": CC,
          "banheiro": CONFIG_CORPO_BANHEIRO, "metabolismo": CONFIG_CORPO_METABOLISMO}
ADAPTACOES = tuple(f"{PREFIXO_ADAPTACAO}tela_{c}" for c in CANAIS_TELA)


def corpo(cc: ConfigCorpo = CC, ct: ConfigTela = TELA) -> Corpo:
    return Corpo.de_estado(Estado(), CONFIG_PADRAO, cc, com_mundo=True, cfg_tela=ct)


def tela(**kw) -> dict[str, int]:
    """Os sete canais, zero nos que nao vieram."""
    return {c: kw.get(c, 0) for c in CANAIS_TELA}


def tick(c: Corpo, intensidades: dict[str, int], t: int = 0) -> None:
    c.sentir_tela(dict(intensidades))
    c.passo(Estado(tick=t))


# ================================================================== a config
def test_config_tabela_de_status_e_k_da_meia_vida():
    assert set(PARAMETROS_TELA) == {f.name for f in fields(ConfigTela)}
    assert {s for s, _ in PARAMETROS_TELA.values()} == {"PROPOSTO"}
    assert all("SEM FONTE" in fonte for _, fonte in PARAMETROS_TELA.values())
    assert not CONFIG_TELA.ligada
    assert CONFIG_TELA.k_adaptacao == k_meia_vida(CONFIG_TELA.meia_vida_adaptacao, 16)
    assert CONFIG_TELA.teto_intensidade == CC.escala                              # o perfil de programa em [0, C] entra sem conversao
    assert CONFIG_TELA.corte_novidade < S


@pytest.mark.parametrize("kw,erro", [
    ({"ligada": 1}, "bool"), ({"limiar": -1}, "limiar"), ({"meia_saturacao": 0}, "meia_saturacao"),
    ({"k_adaptacao": 0}, "k_adaptacao"), ({"teto_intensidade": 0}, "teto_intensidade"), ({"tedio_assistir": 0}, "tedio_assistir"),
    ({"ganho_humor_agrado": -5}, "ganho_humor_agrado"), ({"estresse_divisor": 1}, "estresse_divisor"),
    ({"estresse_corte": 450000}, "estresse_corte"), ({"salto_volume": 450000}, "salto_volume"), ({"susto_salto": 0}, "susto_salto"),
    ({"corte_novidade": 0}, "corte_novidade"), ({"limiar": 1.5}, "limiar"), ({"susto_salto": True}, "susto_salto")])
def test_config_falha_alto(kw, erro):
    with pytest.raises((ValueError, TypeError), match=erro):
        ConfigTela(**kw)


def test_ligada_com_k_ou_corte_errado_falha_alto():
    with pytest.raises(ValueError, match="k_adaptacao"):
        corpo(ct=replace(TELA, k_adaptacao=754))
    with pytest.raises(ValueError, match="corte_novidade"):
        corpo(ct=replace(TELA, corte_novidade=S))
    with pytest.raises(ValueError, match="chega a S"):
        corpo(ct=replace(TELA, meia_saturacao=1))


# ================================================================== desligada: nada existe, o corpo e o de hoje
def test_desligada_nada_existe():
    for cc in COMBOS.values():
        for com_mundo in (False, True):
            c = Corpo.de_estado(Estado(), CONFIG_PADRAO, cc, com_mundo=com_mundo)
            d = Corpo.de_estado(Estado(), CONFIG_PADRAO, cc, com_mundo=com_mundo, cfg_tela=CONFIG_TELA)
            for x in (c, d):
                assert x.orgaos_tela == () and x.estimulo_tela == {} and x.grafo.somas == ()
                assert not any("tela" in n for n in x.quimicos)
                assert not set(todos_receptores_tela()) & set(x.receptores())
                assert "tela" not in x.para_dict() and "somas" not in x.relato_grafo
                assert not [e.nome for e in x.grafo.emissores if "tela" in e.nome or ATIVIDADE_TELA in e.nome]
                with pytest.raises(ValueError, match="ConfigTela"):
                    x.sentir_tela(tela())
                with pytest.raises(ValueError, match="ConfigTela"):
                    x.estimulo_agrado_tela(10)
                if cc.drives_novos:
                    with pytest.raises(ValueError, match="ConfigTela"):
                        x.atividade(ATIVIDADE_TELA)
            assert c.grafo == d.grafo and c.quimicos == d.quimicos
            assert quimicos_de(cc, com_mundo) == quimicos_de(cc, com_mundo, cfg_tela=CONFIG_TELA)
            t = taxas_de(CONFIG_PADRAO, cc)
            assert grafo_do_corpo(CONFIG_PADRAO, cc, t, com_mundo) == grafo_do_corpo(CONFIG_PADRAO, cc, t, com_mundo, cfg_tela=CONFIG_TELA)


def test_desligada_a_mesma_sequencia_da_os_mesmos_numeros():
    """o corpo sem a tela e com a ConfigTela padrao passa pelas mesmas operacoes com os mesmos numeros (o de hoje)"""
    for com_mundo in (False, True):
        a = Corpo.de_estado(Estado(), CONFIG_PADRAO, CC, com_mundo=com_mundo)
        b = Corpo.de_estado(Estado(), CONFIG_PADRAO, CC, com_mundo=com_mundo, cfg_tela=CONFIG_TELA)
        rng = random.Random(4401)
        for i in range(400):
            k = rng.randrange(5)
            for c in (a, b):
                r = random.Random(i)
                if k == 0:
                    c.acao_dono(r.choice([AcaoUsuario.ALIMENTAR, AcaoUsuario.BRINCAR, AcaoUsuario.ACARICIAR]))
                elif k == 1:
                    c.acao_pet(r.choice([AcaoPet.BRINCAR, AcaoPet.EXPLORAR]), com_mundo=com_mundo)
                elif k == 2:
                    c.atividade(r.choice(["bola", "brincar", "explorar"]))
                else:
                    c.passo(Estado(tick=i, dormindo=r.random() < 0.3, sujeira=r.randrange(3)))
            assert a.receptores() == b.receptores() and a.para_dict() == b.para_dict()


# ================================================================== ligada: as exigencias
def test_ligada_exige_mundo_drives_novos_e_gestos():
    with pytest.raises(ValueError, match="mundo fisico"):
        Corpo.de_estado(Estado(), CONFIG_PADRAO, CC, com_mundo=False, cfg_tela=TELA)
    for cc in (ConfigCorpo(ligada=True), ConfigCorpo(ligada=True, digestao=True, vida=True),
               ConfigCorpo(ligada=True, digestao=True, vida=True, drives_novos=True)):
        with pytest.raises(ValueError, match="drives_novos e ConfigCorpo.gestos"):
            corpo(cc)
    for cc in (CC, CONFIG_CORPO_BANHEIRO):
        assert corpo(cc).orgaos_tela


def test_ligada_os_quimicos_o_grafo_e_a_percepcao():
    c = corpo()
    assert c.quimicos[-len(CANAIS_TELA):] == ADAPTACOES
    for n in ADAPTACOES:
        qm = c.grafo.quimico(n)
        assert (qm.teto, qm.receptor, qm.meia_vida, qm.k_meia_vida) == (TELA.teto_intensidade, None, 60, 753)
        assert c.q[n] == 0
    assert [o.receptor for o in c.orgaos_tela] == [f"tela_{k}" for k in CANAIS_TELA]
    assert c.orgaos == () and c.estimulo == {}                                   # o Olfato e a Audicao seguem desligados
    assert c.grafo.somas == (ReceptorSoma(RECEPTOR_NOVIDADE_TELA, ADAPTACOES, TELA.meia_saturacao),)
    assert c.relato_grafo["somas"] == {RECEPTOR_NOVIDADE_TELA: list(ADAPTACOES)}
    assert c.relato_grafo["orgaos"] == [f"tela_{k}" for k in CANAIS_TELA]
    # nenhum laco novo: o estresse da tela le o estimulo, nao um quimico
    assert c.relato_grafo["lacos"] == Corpo.de_estado(Estado(), CONFIG_PADRAO, CC, com_mundo=True).relato_grafo["lacos"]
    assert {e.nome for e in c.grafo.emissores} >= {f"atividade:{ATIVIDADE_TELA}", "estresse_tela", "susto_tela", "agrado_tela"}
    assert not [n for n in c.quimicos + tuple(c.receptores()) if "prazer" in n or "gost" in n]   # nenhum quimico de prazer
    # os campos da PercepcaoCorpo: os receptores da tela no fim, na ordem de todos_receptores_tela
    campos = [f.name for f in fields(PercepcaoCorpo)]
    assert campos[-len(todos_receptores_tela()):] == list(todos_receptores_tela())
    p = PercepcaoCorpo(**c.receptores())
    assert all(getattr(p, n) == 0 for n in todos_receptores_tela())
    assert set(c.para_dict()["tela"]) == {"estimulo", "sentido"}


def test_o_grafo_recusa_somas_e_gatilho_mal_formados():
    c = corpo()
    g = c.grafo
    with pytest.raises(GrafoInvalido, match="nao sao de orgao"):
        checar(replace(g, somas=(ReceptorSoma("novidade_tela", ("fome",), 10),)))
    with pytest.raises(GrafoInvalido, match="receptor repetido"):
        checar(replace(g, somas=(ReceptorSoma("tela_cor", ADAPTACOES, 10),)))
    e = g.emissor("estresse_tela")
    with pytest.raises(GrafoInvalido, match="tela_acima"):
        checar(replace(g, emissores=tuple(replace(x, divisor=1) if x is e else x for x in g.emissores)))
    with pytest.raises(GrafoInvalido, match="so o orgao move"):
        checar(replace(g, emissores=g.emissores + (replace(g.emissor("susto_tela"), nome="mexe", efeitos=((ADAPTACOES[0], 1),)),)))


# ================================================================== o estimulo e a adaptacao
def test_sentir_tela_falha_alto():
    c = corpo()
    with pytest.raises(ValueError, match="canais da tela"):
        c.sentir_tela({"cor": 1})
    with pytest.raises(ValueError, match="canais da tela"):
        c.sentir_tela({**tela(), "extra": 0})
    for v in (-1, TELA.teto_intensidade + 1, 1.0, True, None):
        with pytest.raises(ValueError, match="inteiro em"):
            c.sentir_tela(tela(cor=v))


def test_o_tick_sem_sentir_tela_falha_alto():
    c = corpo()
    with pytest.raises(RuntimeError, match="sentir_tela"):
        c.passo(Estado())
    c = corpo()
    tick(c, tela(cor=1000))
    with pytest.raises(RuntimeError, match="sentir_tela"):
        c.passo(Estado(tick=1))                                                   # um sentir vale um tick so


def test_a_adaptacao_anda_para_i_e_decai_sem_estimulo():
    """o interesse que se gasta e volta: com I constante a adaptacao chega a I (a conta exata do passo); sem olhar (zeros) ela decai a 0;
    a metade perto da meia-vida declarada"""
    c = corpo()
    I = 300000
    a = 0
    for t in range(60):
        tick(c, tela(cor=I, volume=I), t)
        a = passo_adaptacao(a, I, TELA.k_adaptacao)
        assert c.q[ADAPTACOES[0]] == a == c.q[f"{PREFIXO_ADAPTACAO}tela_volume"]
        assert c.q[f"{PREFIXO_ADAPTACAO}tela_brilho"] == 0
    assert abs(a - I // 2) < I // 100                                              # a metade na meia-vida (60 ticks)
    for t in range(60, 2000):
        tick(c, tela(cor=I, volume=I), t)
    assert c.q[ADAPTACOES[0]] == I                                                 # chega a I e nao passa
    for t in range(2000, 2060):
        tick(c, tela(), t)
    assert abs(c.q[ADAPTACOES[0]] - I // 2) < I // 100                             # sem olhar, decai com a mesma meia-vida
    for t in range(2060, 4000):
        tick(c, tela(), t)
    assert all(c.q[n] == 0 for n in ADAPTACOES)


def test_os_receptores_a_conta_exata():
    c = corpo()
    niveis = {"cor": 450000, "brilho": 30000, "movimento": 1, "complexidade": 0, "volume": 225000, "variacao": 123457, "timbre": 7}
    for t in range(37):
        tick(c, niveis, t)
    c.sentir_tela(niveis)
    r = c.receptores()
    for k, v in niveis.items():
        assert r[f"tela_{k}"] == div_arred(S * v, TELA.teto_intensidade)          # o nivel, sem adaptacao
    e = sum(max(0, v - c.q[f"{PREFIXO_ADAPTACAO}tela_{k}"] - TELA.limiar) for k, v in niveis.items())
    assert e > 0 and r[RECEPTOR_NOVIDADE_TELA] == div_arred(S * e, e + TELA.meia_saturacao)
    assert all(type(v) is int and 0 <= v < S + 1 for v in r.values())
    assert r["tela_cor"] == S and r["tela_complexidade"] == 0


def test_a_novidade_cai_com_o_mesmo_estimulo_e_sobe_quando_muda():
    c = corpo()
    programa = tela(cor=300000, brilho=240000, movimento=150000, complexidade=210000, volume=180000, variacao=120000, timbre=270000)
    c.sentir_tela(dict(programa))
    novidades = [c.receptores()[RECEPTOR_NOVIDADE_TELA]]
    for t in range(240):
        c.passo(Estado(tick=t))
        c.sentir_tela(dict(programa))
        novidades.append(c.receptores()[RECEPTOR_NOVIDADE_TELA])
    assert novidades[0] > TELA.corte_novidade                                       # ligar a TV e novidade
    assert all(x >= y for x, y in zip(novidades, novidades[1:]))                    # o mesmo programa: so cai
    assert novidades[-1] < TELA.corte_novidade < novidades[0]                      # o enjoo
    # o mesmo programa nunca volta a ser novidade; outro programa (os canais mudando) e
    outro = {k: min(TELA.teto_intensidade, v + 150000) for k, v in programa.items()}
    c.passo(Estado(tick=240))
    c.sentir_tela(outro)
    assert c.receptores()[RECEPTOR_NOVIDADE_TELA] > TELA.corte_novidade > novidades[-1]
    # um nivel a mais num canal so nao conta como novidade
    d = corpo()
    for t in range(3000):
        tick(d, programa, t)
    d.sentir_tela({**programa, "cor": programa["cor"] + 30000})
    assert 0 < d.receptores()[RECEPTOR_NOVIDADE_TELA] < TELA.corte_novidade


# ================================================================== os emissores
def test_o_estresse_sobe_acima_do_corte_e_nao_abaixo():
    corte = TELA.estresse_corte
    k = CC.k_meia_vida_estresse
    for canal in CANAIS_ESTRESSE_TELA:
        abaixo, acima, controle = corpo(), corpo(), corpo()
        tick(abaixo, tela(**{canal: corte}))
        tick(acima, tela(**{canal: corte + 25600}))
        tick(controle, tela())
        assert controle.q["estresse"] == 0 and abaixo.q["estresse"] == 0
        assert acima.q["estresse"] == passo_meia_vida(div_arred(25600, TELA.estresse_divisor), k) == 99
    # o volume e o movimento juntos somam; os outros canais no teto nao estressam
    c = corpo()
    teto = TELA.teto_intensidade
    tick(c, {k_: teto for k_ in CANAIS_TELA if k_ not in CANAIS_ESTRESSE_TELA} | {k_: 0 for k_ in CANAIS_ESTRESSE_TELA})
    assert c.q["estresse"] == 0
    tick(c, tela(volume=teto, movimento=teto), 1)
    assert c.q["estresse"] == passo_meia_vida(div_arred(2 * (teto - corte), TELA.estresse_divisor), k)
    # por tick: o estresse acumula enquanto o pet olha
    antes = c.q["estresse"]
    tick(c, tela(volume=teto, movimento=teto), 2)
    assert c.q["estresse"] > antes


def test_o_susto_so_no_salto_de_volume():
    salto, s = TELA.salto_volume, TELA.susto_salto
    c = corpo()
    c.sentir_tela(tela(volume=salto))                                              # igual ao salto: nao e mais que o salto
    assert c.q["susto"] == 0
    c.passo(Estado())
    c = corpo()
    c.sentir_tela(tela(volume=salto + 1))
    assert c.q["susto"] == s
    c.sentir_tela(tela(volume=salto + 1))                                          # o mesmo volume de novo: nada
    assert c.q["susto"] == s
    c = corpo()
    for v in range(0, TELA.teto_intensidade + 1, 100000):                          # subir devagar: nada
        c.sentir_tela(tela(volume=v))
    assert c.q["susto"] == 0
    c.sentir_tela(tela(volume=0))                                                  # cair nao assusta; subir de novo de uma vez assusta
    assert c.q["susto"] == 0
    c.sentir_tela(tela(volume=TELA.teto_intensidade))
    assert c.q["susto"] == s
    c = corpo()
    c.sentir_tela(tela(movimento=TELA.teto_intensidade, cor=TELA.teto_intensidade))   # so o volume assusta
    assert c.q["susto"] == 0


def test_o_agrado_tira_tristeza():
    for agrado in (0, 1, 333, 512, S):
        c = corpo()
        c.q["tristeza"] = 200000
        c.estimulo_agrado_tela(agrado)
        assert c.q["tristeza"] == 200000 - div_arred(TELA.ganho_humor_agrado * agrado, S)
    c = corpo()
    c.q["tristeza"] = 1000
    c.estimulo_agrado_tela(S)
    assert c.q["tristeza"] == 0                                                    # cortado em 0
    for ruim in (-1, S + 1, 1.0, True):
        with pytest.raises(ValueError, match="agrado"):
            c.estimulo_agrado_tela(ruim)


def test_assistir_tira_tedio_so_com_a_tela_ligada():
    c = corpo()
    c.q["tedio"] = 300000
    J, base = CC.janela_tedio, TELA.tedio_assistir
    c.atividade(ATIVIDADE_TELA)
    assert c.q["tedio"] == 300000 - base
    c.atividade(ATIVIDADE_TELA)                                                    # a variedade DS-4: a repetida tira menos
    assert c.q["tedio"] == 300000 - base - div_arred(base * (J - 1), J)
    assert c.janela_tedio == [ATIVIDADE_TELA, ATIVIDADE_TELA]
    c.atividade("bola")                                                            # a mesma janela das atividades de hoje
    assert c.janela_tedio[-1] == "bola"
    sem = Corpo.de_estado(Estado(), CONFIG_PADRAO, CC, com_mundo=True)
    with pytest.raises(ValueError, match="ConfigTela"):
        sem.atividade(ATIVIDADE_TELA)
    with pytest.raises(ValueError, match="desconhecida"):
        c.atividade("ver")


# ================================================================== inteiros e determinismo
def sequencia(semente: int) -> list:
    rng = random.Random(semente)
    c = corpo()
    saida = []
    for t in range(800):
        olhando = rng.random() < 0.6
        c.sentir_tela({k: rng.randrange(0, TELA.teto_intensidade + 1) if olhando else 0 for k in CANAIS_TELA})
        if rng.random() < 0.2:
            c.atividade(ATIVIDADE_TELA)
        if rng.random() < 0.2:
            c.estimulo_agrado_tela(rng.randrange(0, S + 1))
        if rng.random() < 0.05:
            c.acao_dono(AcaoUsuario.ACARICIAR)
        c.passo(Estado(tick=t, dormindo=rng.random() < 0.2))
        saida.append((c.receptores(), c.para_dict()))
    return saida


def test_tudo_em_inteiros_e_deterministico():
    a, b = sequencia(7301), sequencia(7301)
    assert a == b
    assert sequencia(7302) != a
    for r, d in a:
        assert all(type(v) is int for v in r.values())
        assert all(type(v) is int and v >= 0 for v in d["q"].values())
        assert all(type(v) is int for v in d["tela"]["estimulo"].values())
