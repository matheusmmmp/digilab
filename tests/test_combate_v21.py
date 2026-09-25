"""Combate V2.1: catalogo, stats, transicoes, tecnicas, passivas, gambits por estagio, replay."""

from __future__ import annotations

import json
import random
from dataclasses import replace
from pathlib import Path

import pytest

from digilab.combate_v2.regras import AcaoIlegal
from digilab.combate_v2.v21.bots import ADOLESCENTES, ADULTOS, RESPOSTAS, com_resposta, lutador_adulto
from digilab.combate_v2.v21.catalogo import (LINHAS, CatalogoInvalido, Forma, Perfil, carater_canonico,
                                             forma_adulta, formas_da_especie, linha_do_adolescente, perfil,
                                             ramo_da_crianca, renormalizar, stats)
from digilab.combate_v2.v21.gambits import Condicao as C, GambitInvalido, lista, regra
from digilab.combate_v2.v21.partida import Lutador, jogar, reproduzir
from digilab.combate_v2.v21.regras import Acao as A, Distancia, EstadoCombate, Regras, eh_legal, estado_inicial, \
    resolver
from digilab.config import CONFIG_CATALOGO, CONFIG_COMBATE_V2, CONFIG_COMBATE_V21, STATS_V21

RAIZ = Path(__file__).resolve().parents[1]
R = Regras()
PERTO, MEDIO, LONGE = Distancia.PERTO, Distancia.MEDIO, Distancia.LONGE


def pf(tecnica=None, passiva=None, estagio="adulto", **kw) -> Perfil:
    """Perfil neutro (multiplicadores 1.0), para isolar a regra testada."""
    base = dict(rotulo="teste", estagio=estagio, tecnica=tecnica, passiva=passiva, hp_max=100.0,
                guts_inicial=50.0, guts_max=100.0, regen=8.0, mult_perto=1.0, mult_disparo=1.0, mult_guarda=1.0)
    base.update(kw)
    return Perfil(**base)


def est(pa: Perfil, pb: Perfil, d=MEDIO, **lado) -> EstadoCombate:
    e = estado_inicial(pa, pb)
    e = replace(e, distancia=d)
    for i, mud in lado.items():
        idx = 0 if i == "a" else 1
        lados = list(e.lados)
        lados[idx] = replace(lados[idx], **mud)
        e = replace(e, lados=tuple(lados))
    return e


# ------------------------------------------------------------------ catalogo

def test_config_igual_aos_jsons_de_docs():
    cat = json.loads((RAIZ / "docs" / "catalogo_pets.json").read_text(encoding="utf-8"))
    arv = json.loads((RAIZ / "docs" / "arvore_evolucao.json").read_text(encoding="utf-8"))
    c = CONFIG_CATALOGO
    assert set(c.especies) == set(cat["especies"])
    for nome, s in cat["especies"].items():
        assert c.especies[nome] == {k: s[k] for k in STATS_V21}
    for eixo in ("curiosidade", "teimosia", "sensibilidade", "rancor"):
        assert c.temperamento[eixo] == cat["temperamento"][eixo]
    for eixo in ("impetuoso", "paciente", "atento", "resistente"):
        assert c.carater[eixo] == cat["carater"][eixo]
    assert {k: v for k, v in cat["estagio"].items() if not k.startswith("_")} == c.mult_estagio
    assert (c.stat_min, c.stat_max, c.orcamento_especie) == (cat["_meta"]["stat_min"], cat["_meta"]["stat_max"],
                                                            cat["_meta"]["orcamento_especie"])
    arq = arv["arquetipos"]
    for ramo in ("sereno", "arisco"):
        assert c.arquetipos_crianca[ramo] == arq["crianca"][ramo]["stats"]
    for linha in LINHAS:
        a = arq["adolescente"][linha]
        assert c.arquetipos_adolescente[linha] == {"eixo": a["eixo"], "tecnica": a["tecnica"]["nome"],
                                                   "stats": a["stats"]}
        ad = arq["adulto"][linha]
        assert c.arquetipos_adulto[linha]["eixo_complementar"] == ad["eixo_complementar"]
        for forma, f in c.arquetipos_adulto[linha]["formas"].items():
            assert f["stats"] == ad[forma]["stats"]
            assert f["sinal"] == ad[forma]["condicao"].split(" ", 1)[1].replace(" ", "")
    assert c.limiar_cuidado_sereno == arv["transicoes"]["bebe_para_crianca"]["limiar"]
    assert c.sparring_minimo_adulto == arv["transicoes"]["adolescente_para_adulto"]["sparring_minimo"]
    v = CONFIG_COMBATE_V21
    t = {l: arq["adolescente"][l]["tecnica"] for l in LINHAS}
    assert (v.custo_investida, v.custo_contra_golpe, v.custo_marcar, v.custo_pele_dura) == tuple(
        t[l]["custo"] for l in LINHAS)
    assert [c.especies_ativas] and set(c.especies_ativas) <= set(c.especies) and len(c.especies_ativas) == 4


def test_modificadores_somam_zero():
    c = CONFIG_CATALOGO
    grupos = list(c.temperamento.values()) + list(c.carater.values()) + list(c.arquetipos_crianca.values())
    grupos += [a["stats"] for a in c.arquetipos_adolescente.values()]
    grupos += [f["stats"] for a in c.arquetipos_adulto.values() for f in a["formas"].values()]
    for g in grupos:
        assert sum(g.values()) == 0, g
    for e in c.especies.values():
        assert sum(e.values()) == c.orcamento_especie


def test_renormalizacao_devolve_o_orcamento_e_respeita_a_faixa():
    r = renormalizar({"vigor": 1.0, "folego": 25.0, "recuperacao": 10.0, "forca": 10.0, "mira": 7.0, "guarda": 7.0},
                     60.0, 3, 20)
    assert abs(sum(r.values()) - 60.0) < 1e-9
    assert all(3 <= x <= 20 for x in r.values())
    assert r["vigor"] == 3 and r["folego"] == 20
    with pytest.raises(CatalogoInvalido):
        renormalizar(dict.fromkeys(STATS_V21, 30.0), 180.0, 3, 20)


def test_stats_extremos_ficam_no_orcamento():
    for esp in CONFIG_CATALOGO.especies:
        for f in formas_da_especie(esp):
            s = stats(f, {"curiosidade": 1, "teimosia": -1, "rancor": 1}, {"impetuoso": 1, "atento": 1, "paciente": -1})
            assert abs(sum(s.values()) - 60.0) < 1e-9, (f, s)
            assert all(CONFIG_CATALOGO.stat_min <= x <= CONFIG_CATALOGO.stat_max for x in s.values())


def test_eixos_fora_da_faixa_ou_desconhecidos_levantam():
    f = Forma("brasa", "crianca", "sereno")
    with pytest.raises(CatalogoInvalido):
        stats(f, {"curiosidade": 1.5})
    with pytest.raises(CatalogoInvalido):
        stats(f, None, {"coragem": 0.5})


def test_forma_valida_o_caminho():
    with pytest.raises(CatalogoInvalido):
        Forma("brasa", "adolescente", "sereno")                 # falta linha
    with pytest.raises(CatalogoInvalido):
        Forma("brasa", "adulto", "sereno", "brigao", "tita")    # tita e do colosso
    with pytest.raises(CatalogoInvalido):
        Forma("dragao", "bebe")
    assert len(formas_da_especie("limo")) == 15
    with pytest.raises(CatalogoInvalido):
        perfil(Forma("brasa", "bebe"))


def test_perfil_neutro_da_os_numeros_da_conversao():
    neutro = replace(CONFIG_CATALOGO, especies={"x": dict.fromkeys(STATS_V21, 10)})
    import digilab.combate_v2.v21.catalogo as cat_mod
    original = cat_mod.CONFIG_CATALOGO
    try:
        cat_mod.CONFIG_CATALOGO = neutro
        p = perfil(Forma("x", "crianca", "sereno"), cat=neutro)
    finally:
        cat_mod.CONFIG_CATALOGO = original
    s = p.stats
    v = CONFIG_COMBATE_V21
    assert p.hp_max == pytest.approx((v.hp_base + v.hp_por_vigor * s["vigor"]) * 0.6)
    assert p.mult_perto == pytest.approx(v.mult_base + v.mult_por_ponto * s["forca"])


def test_transicoes():
    assert ramo_da_crianca(0.8) == "sereno" and ramo_da_crianca(0.79) == "arisco"
    assert linha_do_adolescente({"atento": 0.4, "impetuoso": 0.3}) == "cacador"
    assert linha_do_adolescente({}) == "brigao"                  # empate: ordem fixa
    assert forma_adulta("brigao", {"paciente": 0.0}, 10) == "duelista"
    assert forma_adulta("brigao", {"paciente": -0.1}, 10) == "furioso"
    assert forma_adulta("colosso", {"atento": 0.2}, 9) is None   # sem sparring minimo
    for forma in ADULTOS:
        car = carater_canonico(forma)
        linha = [l for l in LINHAS if forma in CONFIG_CATALOGO.arquetipos_adulto[l]["formas"]][0]
        assert linha_do_adolescente(car) == linha
        assert forma_adulta(linha, car, 10) == forma


# ------------------------------------------------------------------ resolucao

def test_resolucao_pura_sem_rng():
    e = est(pf("investida"), pf("contra_golpe", "espelho"))
    random.seed(123)
    antes = random.getstate()
    x = resolver(e, A.INVESTIDA, A.CONTRA_GOLPE)
    assert random.getstate() == antes
    assert resolver(e, A.INVESTIDA, A.CONTRA_GOLPE) == x


def test_tecnica_so_para_a_propria_linha():
    e = est(pf("investida"), pf())
    assert eh_legal(e, 0, A.INVESTIDA)
    assert not eh_legal(e, 1, A.INVESTIDA)
    with pytest.raises(AcaoIlegal):
        resolver(e, A.DEFENDER, A.MARCAR)


def test_investida_acerta_no_medio_aproxima_e_esquiva_falha():
    e = est(pf("investida"), pf())
    novo, res = resolver(e, A.INVESTIDA, A.ESQUIVAR)
    assert res.dano_recebido[1] == CONFIG_COMBATE_V21.dano_investida
    assert novo.distancia is PERTO
    assert not eh_legal(est(pf("investida"), pf(), d=PERTO), 0, A.INVESTIDA)


def test_parry_anula_dano_e_avanco():
    e = est(pf("investida"), pf())
    novo, res = resolver(e, A.INVESTIDA, A.DEFENDER)
    assert res.dano_recebido[1] == 0.0
    assert novo.distancia is MEDIO
    assert novo.lados[0].guts == 50 - CONFIG_COMBATE_V21.custo_investida + 8


def test_contra_golpe_devolve_corpo_a_corpo():
    e = est(pf(), pf("contra_golpe"), d=PERTO)
    _, res = resolver(e, A.GOLPE_RAPIDO, A.CONTRA_GOLPE)
    b, v = CONFIG_COMBATE_V2, CONFIG_COMBATE_V21
    assert res.dano_recebido[1] == pytest.approx(b.dano_golpe_rapido * b.mult_defender)
    assert res.dano_recebido[0] == pytest.approx(v.fracao_contra_golpe * b.dano_golpe_rapido)
    assert not eh_legal(est(pf(), pf("contra_golpe")), 1, A.CONTRA_GOLPE)     # so perto


def test_marcar_dobra_ignora_defender_e_expira():
    v, b = CONFIG_COMBATE_V21, CONFIG_COMBATE_V2
    e = est(pf("marcar", guts_inicial=100.0), pf())
    e, _ = resolver(e, A.MARCAR, A.DEFENDER)
    assert e.lados[0].marca == v.turnos_marcar
    assert not eh_legal(e, 0, A.MARCAR)
    e2, res = resolver(e, A.DISPARO, A.DEFENDER)
    assert res.dano_recebido[1] == pytest.approx(b.dano_disparo * v.mult_marcar)
    assert e2.lados[0].marca == 0
    # sem disparo, expira em turnos_marcar turnos
    for _ in range(v.turnos_marcar):
        e, _ = resolver(e, A.DEFENDER, A.DEFENDER)
    assert e.lados[0].marca == 0
    # esquivar ainda anula o disparo marcado
    e = est(pf("marcar"), pf(), a={"marca": 2})
    _, res = resolver(e, A.DISPARO, A.ESQUIVAR)
    assert res.dano_recebido[1] == 0.0


def test_pele_dura_reduz_dois_turnos_e_protege_a_preparacao():
    v, b = CONFIG_COMBATE_V21, CONFIG_COMBATE_V2
    e = est(pf("pele_dura"), pf(), d=PERTO)
    e, res = resolver(e, A.PELE_DURA, A.GOLPE_RAPIDO)
    assert res.dano_recebido[0] == pytest.approx(b.dano_golpe_rapido * v.mult_pele_dura)
    e, res = resolver(e, A.PREPARAR_PESADO, A.GOLPE_RAPIDO)
    assert not res.interrompido[0] and e.lados[0].preparando
    assert res.dano_recebido[0] == pytest.approx(b.dano_golpe_rapido * v.mult_pele_dura)
    e, res = resolver(e, A.PESADO, A.GOLPE_RAPIDO)
    assert res.dano_recebido[0] == pytest.approx(b.dano_golpe_rapido)        # efeito acabou
    assert not eh_legal(est(pf("pele_dura"), pf(), a={"pele": 1}), 0, A.PELE_DURA)


def test_passivas():
    b, v = CONFIG_COMBATE_V2, CONFIG_COMBATE_V21
    # duelista: pesado contra esquiva causa dano extra e devolve o guts do preparar
    e = est(pf("investida", "duelista"), pf(), d=PERTO, a={"preparando": True})
    novo, res = resolver(e, A.PESADO, A.ESQUIVAR)
    assert res.dano_recebido[1] == v.dano_extra_duelista
    assert novo.lados[0].guts == 50 + b.custo_preparar_pesado + 8
    # furioso: sem defender; corpo a corpo x mult abaixo do limiar
    e = est(pf("investida", "furioso"), pf(), d=PERTO, a={"hp": 40.0})
    assert not eh_legal(e, 0, A.DEFENDER)
    _, res = resolver(e, A.GOLPE_RAPIDO, A.CARREGAR)
    assert res.dano_recebido[1] == pytest.approx(b.dano_golpe_rapido * v.mult_furioso * b.mult_carregar)
    # espelho: contra_golpe a distancia devolve disparo (mesmo marcado)
    e = est(pf("marcar"), pf("contra_golpe", "espelho"), a={"marca": 2})
    assert eh_legal(e, 1, A.CONTRA_GOLPE)
    _, res = resolver(e, A.DISPARO, A.CONTRA_GOLPE)
    assert res.dano_recebido[1] == pytest.approx(b.dano_disparo * v.mult_marcar)   # reducao ignorada
    assert res.dano_recebido[0] == pytest.approx(v.fracao_espelho_disparo * b.dano_disparo * v.mult_marcar)
    # muralha: defender da guts extra
    e = est(pf("contra_golpe", "muralha"), pf())
    novo, _ = resolver(e, A.DEFENDER, A.DEFENDER)
    assert novo.lados[0].guts == 50 + 8 + b.guts_extra_defender + v.guts_extra_muralha
    # sentinela: recuo vale contra avanco, com recarga
    e = est(pf("marcar", "sentinela"), pf())
    novo, _ = resolver(e, A.RECUAR, A.AVANCAR)
    assert novo.distancia is LONGE and novo.lados[0].recarga == v.recarga_sentinela
    novo2, _ = resolver(replace(novo, distancia=MEDIO), A.RECUAR, A.AVANCAR)
    assert novo2.distancia is MEDIO                                      # em recarga
    # emboscador: so o primeiro disparo
    e = est(pf("marcar", "emboscador"), pf())
    e, res = resolver(e, A.DISPARO, A.DEFENDER)
    assert res.dano_recebido[1] == pytest.approx(b.dano_disparo * v.mult_emboscador * b.mult_defender)
    _, res = resolver(e, A.DISPARO, A.DEFENDER)
    assert res.dano_recebido[1] == pytest.approx(b.dano_disparo * b.mult_defender)
    # tita: pesado x mult
    e = est(pf("pele_dura", "tita"), pf(), d=PERTO, a={"preparando": True})
    _, res = resolver(e, A.PESADO, A.CARREGAR)
    assert res.dano_recebido[1] == pytest.approx(b.dano_pesado * v.mult_tita * b.mult_carregar)


def test_vigia_ve_a_preparacao():
    vig = lutador_adulto("vigia", "brasa")
    alvo = Lutador("prepara", pf(), lista([regra(C("sempre"), A.PREPARAR_PESADO)], A.DEFENDER), 0.0)
    e = est(vig.perfil, alvo.perfil, d=PERTO)
    vig0 = replace(vig, epsilon=0.0)
    acao, motivo = vig0.decidir(e, 0, random.Random(1), alvo, R)
    assert (acao, motivo) == (A.GOLPE_RAPIDO, 0)
    with pytest.raises(GambitInvalido):
        Lutador("nao-vigia", lutador_adulto("tita", "brasa").perfil,
                lista([regra(C("oponente_vai_preparar"), A.RECUAR)], A.DEFENDER), 0.0)


# ------------------------------------------------------------------ gambits por estagio

def test_capacidade_por_estagio():
    with pytest.raises(GambitInvalido):
        lista([regra(C("sempre"), A.DEFENDER)] * 4, A.DEFENDER, "crianca")          # 3 regras
    with pytest.raises(GambitInvalido):
        lista([regra(C("oponente_preparando"), A.ESQUIVAR)], A.DEFENDER, "crianca")  # sem condicao do oponente
    with pytest.raises(GambitInvalido):
        lista([regra(C("oponente_repete", (A.DEFENDER, 2)), A.AVANCAR)], A.DEFENDER, "adolescente")
    with pytest.raises(GambitInvalido):
        lista([regra(C("sempre"), A.INVESTIDA)], A.DEFENDER, "crianca")
    with pytest.raises(GambitInvalido):
        lista([], A.DEFENDER, "bebe")
    with pytest.raises(GambitInvalido):
        lista([regra(C("turno_execucao", (7,)), A.AVANCAR)], A.DEFENDER)
    lista([regra(C("sempre"), A.AVANCAR)] * 3, A.CARREGAR, "crianca")
    for g in ADOLESCENTES.values():
        assert len(g.regras) <= 5
    for g in ADULTOS.values():
        assert len(g.regras) <= 8


def test_lutador_recusa_tecnica_de_outra_linha_e_estagio_trocado():
    p = lutador_adulto("duelista", "brasa").perfil
    with pytest.raises(GambitInvalido):
        Lutador("x", p, lista([regra(C("sempre"), A.MARCAR)], A.DEFENDER), 0.05)
    with pytest.raises(GambitInvalido):
        Lutador("x", p, ADOLESCENTES["brigao"], 0.05)


def test_resposta_vai_para_o_topo_e_respeita_o_limite():
    g = com_resposta(ADULTOS["duelista"], "contra_golpe")
    assert g.regras[:2] == RESPOSTAS["contra_golpe"] and len(g.regras) == 8


def test_furioso_com_final_defender_cai_para_carregar():
    p = replace(lutador_adulto("furioso", "brasa").perfil)
    lut = Lutador("f", p, lista([], A.DEFENDER), 0.0)
    e = est(p, pf())
    assert lut.decidir(e, 0, random.Random(0), lut, R)[0] is A.CARREGAR


# ------------------------------------------------------------------ partida

def test_replay_bit_a_bit_e_evento_desconhecido():
    a, b = lutador_adulto("vigia", "cirro"), lutador_adulto("emboscador", "limo")
    p = jogar(a, b, 99)
    assert reproduzir(list(p.log), a, b).log == p.log
    with pytest.raises(ValueError):
        reproduzir(list(p.log) + [{"tipo": "misterio"}], a, b)


def test_trocar_lados_espelha_o_resultado():
    a, b = lutador_adulto("espelho", "ferrugem"), lutador_adulto("furioso", "brasa")
    a0 = replace(a, epsilon=0.0)
    b0 = replace(b, epsilon=0.0)
    assert jogar(a0, b0, 5).pontos_a == 1.0 - jogar(b0, a0, 5).pontos_a


def test_base_v2_intacta():
    """Os fontes de combate_v2/*.py sao os do artefato da bateria base."""
    import sys
    sys.path.insert(0, str(RAIZ / "experiments"))
    from run_bateria_combate import hashes

    gravado = json.loads((RAIZ / "artifacts_combate_v2" / "gates.json").read_text(encoding="utf-8"))
    cfg = json.loads((RAIZ / "experiments" / "configs" / "bateria_canonico.json").read_text(encoding="utf-8"))
    assert hashes(cfg)["regras_sha256"] == gravado["hashes"]["regras_sha256"]


def test_motivos_de_partida_v21_tem_texto_para_tudo():
    from digilab.expressao import expressar
    from digilab.motivo import motivos_de_partida_v21

    a, b = lutador_adulto("vigia", "limo"), lutador_adulto("emboscador", "cirro")
    p = jogar(a, b, 11)
    mots = motivos_de_partida_v21(list(p.log), (a, b))
    assert len(mots) == 2 * p.turnos
    for _, _, m, _ in mots:
        for est in ("crianca", "adolescente", "adulto"):
            expressar(m, est, None)                      # tabela cobre tecnicas e condicoes V2.1
    assert any(m.acao in ("marcar", "pele_dura") for _, _, m, _ in mots)
