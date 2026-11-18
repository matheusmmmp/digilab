"""SOCIAL_PAR, E1: o parceiro sob intervencao na bancada (docs/ESPEC_V3_SOCIAL_PAR_E1.md, APROVADA em 2026-11-17, secao 4).

Os gates desta etapa que nao dependem dos controles positivos: o G2 (desligada, o grupo de hoje), o G-GRAV-IDENT (sem perturbacao, a
gravacao refaz a vida ao vivo), o G-GRAV-CEGA (a gravada nao le a observacao), o G-LEVAR (a perturbacao no grupo e no replay) e o
G-METRICAS (as medidas em casos feitos a mao), o G-CONTROLE-POS (os controles de regra pura do adendo 2, secao 10, que separam a VIVO
da GRAV nas 5 sementes; os da secao 3 e do adendo 1 falharam, D-SP-13 e D-SP-18) e o G-MET-NULO (o adendo 1, 9.3).
"""
from __future__ import annotations

import ast
import inspect
import sys
import textwrap
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import exportar_gabarito_co6 as e6  # noqa: E402
from bancada import parceiro as pc  # noqa: E402
from digilab import metrics as mt  # noqa: E402
from digilab.config import (CONFIG_GRUPO_LIGADA, CONFIG_INTERVENCAO_SOCIAL, CONFIG_INTERVENCAO_SOCIAL_LIGADA, PARAMETROS_INTERVENCAO_SOCIAL,  # noqa: E402
                            TICKS_POR_DIA, ConfigIntervencaoSocial)
from digilab.donos import criar_dono  # noqa: E402
from digilab.events import AcaoPet  # noqa: E402
from digilab.grupo import Grupo, PetDoGrupo, reproduzir_grupo, sementes_do_grupo, simular_grupo  # noqa: E402
from digilab.mundo import Alvo, DonoComLugar  # noqa: E402
from digilab.protocol import ENGINE_SHA256_V0, sha256_engine  # noqa: E402

CM = e6.CM
DIAS = 2
SS = lambda s: sementes_do_grupo(s, CONFIG_GRUPO_LIGADA.ids)  # noqa: E731


def _dono(semente_pet):
    return DonoComLugar(criar_dono("atencioso"), "comedouro", semente_pet, "atencioso", CM)


def _vivo(ident, s, fabrica_cerebro=None, gravar=False, rotulo="digibrain"):
    fp, fm = e6.fabricas("atencioso", SS(s)[ident])
    return pc.Membro(ident, "vivo", fm, fabrica_cerebro or fp, _dono(SS(s)[ident]), "atencioso", rotulo, gravar=gravar)


def _gravado(ident, s, base):
    return pc.Membro(ident, "gravado", e6.fabricas("atencioso", SS(s)[ident])[1], gravacao=base.gravacoes[ident],
                     eventos_dono=pc.eventos_do_dono(base.grupo, ident), rotulo_dono="atencioso", rotulo_cerebro="gravada")


# ------------------------------------------------------------------ a chave
def test_a_chave_vem_desligada_com_status_e_fonte():
    assert CONFIG_INTERVENCAO_SOCIAL.ligada is False
    assert set(PARAMETROS_INTERVENCAO_SOCIAL) == {"ligada", "janela_reencontro", "raio_contato_celulas", "raio_perto_celulas"}
    for status, fonte in PARAMETROS_INTERVENCAO_SOCIAL.values():
        assert status in ("PROPOSTO", "DECIDIDO") and fonte
    assert CONFIG_INTERVENCAO_SOCIAL.janela_reencontro * 15 == TICKS_POR_DIA      # um dia de decisoes
    with pytest.raises(ValueError):
        ConfigIntervencaoSocial(janela_reencontro=0)


def test_o_engine_nao_mudou():
    assert sha256_engine() == ENGINE_SHA256_V0


# ------------------------------------------------------------------ G2
def test_g2_dois_vivos_sem_perturbacao_e_o_simular_grupo_byte_a_byte():
    s = 101
    v = pc.viver_par(CM, s, [_vivo("A", s), _vivo("B", s)], DIAS, cfg_intervencao=CONFIG_INTERVENCAO_SOCIAL)
    pets = []
    for i in ("A", "B"):
        fp, fm = e6.fabricas("atencioso", SS(s)[i])
        pets.append(PetDoGrupo(i, 0, fp, fm, _dono(SS(s)[i]), "atencioso", "digibrain"))
    g = simular_grupo(CM, s, pets, DIAS)
    assert v.grupo.registro.para_jsonl() == g.registro.para_jsonl()
    assert "intervencao" not in g.registro.cabecalho


def test_g2_desligada_o_grupo_recusa_a_perturbacao_e_o_ponto_gravado():
    g = Grupo(CM, 101)
    with pytest.raises(ValueError, match="ConfigIntervencaoSocial"):
        g.levar_pet("A", 0, 0)
    fp, fm = e6.fabricas("atencioso", SS(101)["A"])
    m = g.entrar("A", fp(None), fm, "digibrain", "atencioso")
    with pytest.raises(ValueError, match="ligada"):
        m.aceitar_ponto_gravado(CONFIG_INTERVENCAO_SOCIAL)
    assert m._ponto_gravado is False


# ------------------------------------------------------------------ G-GRAV-IDENT
def _identicas(v, w):
    assert [e.para_dict() for e in v.grupo.registro.eventos] == [e.para_dict() for e in w.grupo.registro.eventos]
    assert v.posicoes == w.posicoes
    for i in ("A", "B"):
        # o campo `regra` e o rotulo interno que o cerebro poe na decisao (o `ultima_regra` do instinto); a gravada nao tem regra, e o rotulo
        # nao e fisica: fica fora da comparacao. Todo o resto da decisao (acao, alvo, posicao, chegada, comida, bola) tem de ser igual
        sem_regra = lambda ds: [{k: x for k, x in d.items() if k != "regra"} for d in ds]  # noqa: E731
        assert sem_regra(v.grupo.motores[i].decisoes_mundo) == sem_regra(w.grupo.motores[i].decisoes_mundo)
        assert repr(v.grupo.motores[i]._estado) == repr(w.grupo.motores[i]._estado)
    assert all(not d for d in w.desvios.values())


@pytest.mark.parametrize("s", [101, 202])
def test_g_grav_ident_o_modular_gravado_refaz_a_vida_ao_vivo(s):
    base = pc.viver_par(CM, s, [_vivo("A", s), _vivo("B", s, gravar=True)], DIAS)
    assert len(base.gravacoes["B"]) == DIAS * 96
    grav = pc.viver_par(CM, s, [_vivo("A", s), _gravado("B", s, base)], DIAS)
    _identicas(base, grav)


def test_g_grav_ident_com_o_seguidor_e_o_alvo_social():
    s = 303
    seg = lambda c: pc.Seguidor(c)  # noqa: E731
    base = pc.viver_par(CM, s, [_vivo("A", s, seg, rotulo="seguidor"), _vivo("B", s, seg, gravar=True, rotulo="seguidor")], DIAS)
    assert any(d.alvo is not None and d.alvo.tipo == "seguir" for d in base.gravacoes["B"])     # o alvo social foi gravado
    grav = pc.viver_par(CM, s, [_vivo("A", s, seg, rotulo="seguidor"), _gravado("B", s, base)], DIAS)
    _identicas(base, grav)
    assert base.grupo.contatos == grav.grupo.contatos                                            # o toque (encostou) tambem


# ------------------------------------------------------------------ G-GRAV-CEGA
def _nomes_lidos(funcao) -> set[str]:
    arvore = ast.parse(textwrap.dedent(inspect.getsource(funcao)))
    return {n.attr for n in ast.walk(arvore) if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id in
            ("obs", "percepcao")}


def test_g_grav_cega_a_gravada_nao_le_a_observacao():
    assert _nomes_lidos(pc.PoliticaGravada.agir) == set()
    assert _nomes_lidos(pc.PoliticaGravada.escolher_alvo) <= {"x", "y"}        # so a propria posicao, no caso `parado`
    p = pc.PoliticaGravada([pc.DecisaoGravada(0, AcaoPet.EXPLORAR, AcaoPet.EXPLORAR, Alvo("seguir", 32, 48))])
    assert p.agir(None, None) is AcaoPet.EXPLORAR                              # sem observacao nenhuma
    assert p.escolher_alvo(AcaoPet.EXPLORAR, [Alvo("seguir", 99, 99)], None, 0) == Alvo.ponto(32, 48)   # nunca o seguir de agora
    assert p.desvios == [(0, "alvo_fora")]
    assert p.agir(None, None) is AcaoPet.OCIOSO and p.desvios[-1] == (1, "fim_da_gravacao")


# ------------------------------------------------------------------ G-LEVAR
def test_g_levar_a_perturbacao_entra_no_registro_e_o_replay_a_refaz():
    s = 202
    seg = lambda c: pc.Seguidor(c)  # noqa: E731
    t0, direcao = pc.sortear_perturbacao(s, TICKS_POR_DIA, 2 * TICKS_POR_DIA - 15, 15)
    assert (t0, direcao) == pc.sortear_perturbacao(s, TICKS_POR_DIA, 2 * TICKS_POR_DIA - 15, 15)      # sorteado antes, do fluxo proprio
    v = pc.viver_par(CM, s, [_vivo("A", s, seg, rotulo="seguidor"), _vivo("B", s, seg, rotulo="seguidor")], DIAS,
                     perturbacao=("A", "B", t0, direcao, 5))
    assert v.t0 is not None and v.t0 >= t0
    levados = [e for e in v.grupo.registro.eventos if e.tipo == "levar_pet"]
    assert len(levados) == 1 and levados[0].origem == "intervencao" and levados[0].pet == "A" and levados[0].tick == v.t0
    assert v.grupo.registro.cabecalho["intervencao"]["ligada"] is True
    assert len(v.grupo.motores["A"].levadas) == 1
    fabricas = {i: (seg, e6.fabricas("atencioso", SS(s)[i])[1]) for i in ("A", "B")}
    r = reproduzir_grupo(v.grupo.registro, fabricas, CM, cfg_intervencao=CONFIG_INTERVENCAO_SOCIAL_LIGADA)
    assert r.registro == v.grupo.registro
    assert [tuple(r.motores[i].pet) for i in "AB"] == [tuple(v.grupo.motores[i].pet) for i in "AB"]
    with pytest.raises(ValueError, match="ConfigIntervencaoSocial"):            # o replay sem a chave falha alto
        reproduzir_grupo(v.grupo.registro, fabricas, CM)


def test_g_levar_o_pet_dormindo_falha_antes_do_registro():
    g = Grupo(CM, 101, cfg_intervencao=CONFIG_INTERVENCAO_SOCIAL_LIGADA)
    for i in ("A", "B"):
        fp, fm = e6.fabricas("atencioso", SS(101)[i])
        g.entrar(i, fp(None), fm, "digibrain", "atencioso")
    m = g.motores["A"]
    from dataclasses import replace
    m._estado = replace(m._estado, dormindo=True)
    n = len(g.registro.eventos)
    with pytest.raises(RuntimeError, match="dormindo"):
        g.levar_pet("A", 32, 32)
    assert len(g.registro.eventos) == n


# ------------------------------------------------------------------ G-METRICAS
def test_g_metricas_contato_reencontro_e_episodios():
    d = [5, 3, 1, 0, 0, 4, 1]
    assert mt.fracao_em_raio(d, 1) == 4 / 7
    assert mt.fracao_em_raio(d, 1, desde=5) == 1 / 2
    assert mt.tempo_ate_raio(d, 1, 0, 10) == (2, False)
    assert mt.tempo_ate_raio(d, 1, 5, 10) == (1, False)
    assert mt.tempo_ate_raio([5, 5, 5], 1, 0, 1) == (1, True)                 # censurado na janela
    assert mt.tempo_ate_raio([5, 5, 5], 1, 0, 9) == (2, True)                 # censurado no fim da serie
    assert mt.episodios_em_raio(d, 1) == [3, 1]
    with pytest.raises(ValueError):
        mt.fracao_em_raio([1, -1], 1)


def test_g_metricas_contingencia_separa_quem_se_moveu():
    # o outro (b) chega mais perto em t=1 e se afasta em t=3; eu (a) respondo chegando perto depois de ele se aproximar
    a = [(0, 0), (0, 0), (2, 0), (2, 0), (2, 0)]
    b = [(10, 0), (8, 0), (8, 0), (12, 0), (12, 0)]
    assert mt.contingencia(a, b) == 1.0
    assert mt.contingencia([(0, 0)] * 5, b) == 0.0                           # quem nao se move nunca responde
    assert mt.contingencia(a, [(10, 0)] * 5) is None                         # o outro parado: sem caso


def test_g_metricas_alternancia_e_o_substituto_circular():
    assert mt.alternancia([10, 50], [20, 90], 30) == 0.5
    assert mt.alternancia([], [1], 5) is None
    assert mt.alternancia_substituta([10, 50], [20, 90], 30, [0, 30], 100) == [0.5, 0.5]
    with pytest.raises(ValueError):
        mt.alternancia([5, 1], [], 3)


# ------------------------------------------------------------------ G-CONTROLE-POS (o adendo 2) e G-MET-NULO (o adendo 1)
def test_g_controle_pos_os_controles_de_regra_pura_separam_vivo_e_grav():
    import conferir_controles_social_par_e1 as cc
    r = cc.conferir()
    assert r["o_que_a_espec_espera_saiu"] == {"C1": True, "C2": True}
    for linha in r["pares"]["C1_estatua_x_seguidor_puro"].values():
        assert linha["VIVO"]["desvios_B"] == 0                       # o vivo nao tem gravacao
        assert linha["GRAV"]["distancias"] == [linha["GRAV"]["distancia_no_t0"]] * (cc.JANELA + 1)   # o gravado nao sai do lugar


def test_g_met_nulo_o_parceiro_gravado_nao_responde_ao_focal():
    seg, evi = (lambda c: pc.Seguidor(c)), (lambda c: pc.Evitador(CM, c))  # noqa: E731
    for s in (101, 202, 303, 404, 505):
        t0, direcao = pc.sortear_perturbacao(s, TICKS_POR_DIA, 2 * TICKS_POR_DIA - 15, 15)
        base = pc.viver_par(CM, s, [_vivo("A", s, seg, rotulo="c"), _vivo("B", s, evi, gravar=True, rotulo="c")], DIAS)
        grav = pc.viver_par(CM, s, [_vivo("A", s, seg, rotulo="c"), _gravado("B", s, base)], DIAS, perturbacao=("A", "B", t0, direcao, 5))
        k = pc.indice_do_passo(grav, grav.t0)
        c = mt.contingencia(grav.posicoes["B"][k:], grav.posicoes["A"][k:])
        assert c is None or abs(c) <= 0.2, (s, c)                   # A1-4
