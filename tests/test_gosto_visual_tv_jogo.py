"""GOSTO_VISUAL, a TV no jogo: as decisoes A, B e D da captura ligada ao cerebro ("Sim a tudo", Matheus, 2026-11-12; docs/registro/2026-11.md,
D-GV-TVJOGO), no Python.

  - A, a TV desligada: o `sentido_tela` `fonte|desligada` (so com a ConfigTVJogo.desligar) tira a TV das TVs a vista e o pet nao a olha;
  - D, o ir ate a TV: com a ConfigTVJogo.ir_ate_tv e o DigiBrain com o `ir_ate_tv`, a linha da TV vai ao cerebro tambem fora do raio, e o
    olhar de uma TV longe vira a acao IR_TV: o pet anda sozinho ate ela e depois a olha;
  - B, a TV no grupo: uma TV do mundo comum, os dois pets olhando, o `sentido_tela` como evento do grupo, e o replay;
  - desligadas, nada muda (o gabarito tests/gabaritos/tv_jogo_vidas_de_hoje.json confere as vidas de hoje) e cada chave falha alto sozinha.
Sementes: as dos testes."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import exportar_gosto_visual as X  # noqa: E402
import exportar_tv_jogo as T  # noqa: E402

from digilab.config import (CONFIG_GRUPO_LIGADA, CONFIG_PADRAO, CONFIG_TVJOGO, CONFIG_TVJOGO_LIGADA, PARAMETROS_TVJOGO,  # noqa: E402
                            ConfigTV, ConfigTVJogo)
from digilab.digibrain.adapt import DigiBrain  # noqa: E402
from digilab.events import (ACOES_PET_BANHEIRO, ACOES_PET_HOJE, ACOES_PET_TV, AcaoPet, Evento, ler_sentido_tela,  # noqa: E402
                            sentido_tela_desligada)
from digilab.grupo import Grupo, reproduzir_grupo  # noqa: E402
from digilab.mundo import acao_visivel, distancia  # noqa: E402
from digilab.policies.lobos import ACOES_VISIVEIS  # noqa: E402
from digilab.tv import ID_TV, TVSemChave  # noqa: E402


def _cerebro(s: int, ir: bool = True) -> DigiBrain:
    return DigiBrain(CONFIG_PADRAO, X.config_vida(), X.orq.CM, semente=s, cfg_olhar=X.config_olhar("evento"), ir_ate_tv=ir)


def _ligar(m, niveis=(8, 8, 8, 8, 4, 4, 4)) -> None:
    m.sentido_tela("tv", tuple(niveis))


# ================================================================== os formatos e as chaves
def test_o_formato_da_tv_desligada_e_o_enum():
    ev = sentido_tela_desligada(7, "tela")
    assert (ev.tipo, ev.valor) == ("sentido_tela", "tela|desligada")
    assert ler_sentido_tela(ev) == ("tela", None)
    for ruim in ("tela|desligado", "radio|desligada", "tela|desligada|1"):
        with pytest.raises(ValueError):
            ler_sentido_tela(Evento(0, "sentido_tela", ruim))
    with pytest.raises(ValueError):
        sentido_tela_desligada(0, "radio")
    assert tuple(AcaoPet)[-1] is AcaoPet.IR_TV and ACOES_PET_TV == (AcaoPet.IR_TV,)
    assert ACOES_PET_HOJE + ACOES_PET_BANHEIRO + ACOES_PET_TV == tuple(AcaoPet)
    assert AcaoPet.IR_TV.value not in ACOES_VISIVEIS and acao_visivel(AcaoPet.IR_TV) == "explorar"
    assert all(acao_visivel(a) == a.value for a in ACOES_PET_HOJE + ACOES_PET_BANHEIRO)


def test_a_config_e_as_chaves_falham_alto():
    assert CONFIG_TVJOGO.ligada is False and CONFIG_TVJOGO_LIGADA.ligada is True
    assert set(PARAMETROS_TVJOGO) == {"desligar", "ir_ate_tv"} and all(s == "PROPOSTO" for s, _ in PARAMETROS_TVJOGO.values())
    with pytest.raises(TypeError):
        ConfigTVJogo(desligar=1)
    with pytest.raises(TVSemChave, match="ConfigTV ligada"):
        X.com_corpo(X.MotorMundo)(_cerebro(101), CONFIG_PADRAO, 101, X.NEUTRO, "brasa", obediencia_desligada=True, cfg_mundo=X.orq.CM,
                                  cfg_corpo=X._cc(), cfg_tela=X.TELA, cfg_tv_jogo=CONFIG_TVJOGO_LIGADA)
    with pytest.raises(TVSemChave, match="fonte"):
        X.com_corpo(X.MotorMundo)(_cerebro(101), CONFIG_PADRAO, 101, X.NEUTRO, "brasa", obediencia_desligada=True, cfg_mundo=X.orq.CM,
                                  cfg_corpo=X._cc(), cfg_tela=X.TELA, cfg_tv=X.config_tv("grade"), cfg_tv_jogo=CONFIG_TVJOGO_LIGADA)
    with pytest.raises(ValueError, match="subchave olhar"):
        DigiBrain(CONFIG_PADRAO, X.E.config_laboratorio(), X.orq.CM, semente=101, ir_ate_tv=True)


def test_sem_a_config_tv_jogo_a_tv_desligada_e_o_ir_tv_falham_alto():
    m = X.com_corpo(X.MotorMundo)(_cerebro(101, ir=False), CONFIG_PADRAO, 101, X.NEUTRO, "brasa", obediencia_desligada=True,
                                  cfg_mundo=X.orq.CM, cfg_corpo=X._cc(), cfg_tela=X.TELA, cfg_tv=X.config_tv("evento"))
    n = len(m.log)
    with pytest.raises(TVSemChave, match="desligar"):
        m.desligar_tela("tv")
    assert len(m.log) == n
    with pytest.raises(TVSemChave, match="ir_ate_tv"):
        m._ir_ate_tv(0, *m.pet)
    # sem o ir ate a TV, a TV fora do raio nao entra nas linhas, e o cerebro recusa uma linha longe
    _ligar(m)
    m.pet = (m.mundo.tv.x + 20 * X.orq.CM.sub, m.mundo.tv.y)
    assert m._linhas_tela() == []
    c = _cerebro(101, ir=False)
    with pytest.raises(ValueError, match="fora do raio"):
        c.m.sens._linhas_tela([(ID_TV, 900, 0, 900)])


# ================================================================== A: a TV desligada nao e vista
def test_a_tv_desligada_sai_das_tvs_a_vista_e_o_pet_nao_a_olha():
    m = T.laco(_cerebro(202), 202)
    _ligar(m)
    m.pet = (m.mundo.tv.x, m.mundo.tv.y + X.orq.CM.sub)            # ao lado da TV, no raio
    assert m._linhas_tela() and m.mundo.tv.em(0) is not None
    m.desligar_tela("tv")
    assert list(m.log)[-1].valor == "tv|desligada"
    assert m.mundo.tv.em(m._tm(m.estado()["tick"])) is None and m._linhas_tela() == []
    m.avancar(240)
    cer = m.politica
    assert all(x["olhar"]["telas"] == [] and x["olhar"]["olha"] is None for x in cer.motivos)
    assert m.estado()["tv"]["ligada"] is False and not m.olhando_tv()
    # o proximo sentido_tela religa
    _ligar(m)
    assert m.mundo.tv.em(m._tm(m.estado()["tick"])) is not None
    assert m.mundo.tv.sentidos[-2]["niveis"] is None


# ================================================================== D: o pet vai ate a TV sozinho
def test_o_pet_vai_ate_a_tv_sozinho_e_depois_a_olha():
    for s in (101, 202, 303):
        m = T.laco(_cerebro(s), s)
        _ligar(m)
        tv = m.mundo.tv
        m.levar_pet(tv.x + 14 * X.orq.CM.sub, tv.y)                # 14 celulas da TV: fora do raio da visao (6)
        d0 = distancia(tv.x - m.pet[0], tv.y - m.pet[1])
        assert d0 > m._raio_visao and m._linhas_tela()[0][3] == d0  # a TV longe vai ao cerebro
        foi = olhou = False
        for _ in range(48):
            m.avancar(60)
            ms = m.politica.motivos
            foi = foi or any(x["acao"] == "ir_tv" for x in ms)
            olhou = olhou or any(x["olhar"]["olha"] == ID_TV for x in ms)
            if foi and olhou:
                break
        assert foi and olhou, s
        ida = [d for d in m.decisoes_mundo if d["acao"] == "ir_tv"]
        assert ida and all(d["alvo"] == "tv" for d in ida)
        # cada ida aproxima o pet da TV (ou o deixa onde estava, preso)
        assert all(d["deslocamento"] >= 0 for d in ida)
        k = next(i for i, x in enumerate(m.politica.motivos) if x["acao"] == "ir_tv")
        mo = m.politica.motivos[k]
        assert mo["escolha"][0] == "olhar" and mo["olhar"]["olha"] is None     # o olhar de uma TV longe vira o ir, sem olhar


def test_o_replay_refaz_a_vida_com_o_ir_tv_e_a_tv_desligada():
    from digilab.mundo import reproduzir_mundo
    m, c, _, _ = T.viver(101, gravar=False)
    assert any(x["acao"] == "ir_tv" for x in c.motivos)
    r = reproduzir_mundo(m.log, lambda cfg: T.cerebro(101), CONFIG_PADRAO, 101, fabrica_motor=lambda p, cfg, s: T.laco(p, s))
    assert json.dumps(r.politica.estado_interno(), sort_keys=True, default=repr) == json.dumps(c.estado_interno(), sort_keys=True, default=repr)
    assert r.resumo_mundo_fisico() == m.resumo_mundo_fisico()


# ================================================================== B: a TV no grupo
def test_o_grupo_com_a_tv_os_dois_olham_e_o_replay_confere():
    g = T.viver_grupo(101)
    assert g.registro.cabecalho["tv"]["fonte"] == "evento" and g.registro.cabecalho["tv_jogo"] == {"desligar": True, "ir_ate_tv": True}
    st = [e for e in g.registro.eventos if e.tipo == "sentido_tela"]
    assert st and all(e.destino == "mundo" and e.pet is None for e in st)
    assert any(e.valor == "tv|desligada" for e in st)
    for i, m in g.motores.items():
        assert m.mundo.tv is g.mundo.tv                              # uma TV so, do mundo comum
        assert any(x["olhar"]["olha"] == ID_TV for x in m.politica.motivos), i
        assert any(x["acao"] == "ir_tv" for x in m.politica.motivos), i
        assert all(e.tipo != "sentido_tela" for e in m.log)        # a TV nao entra na projecao de nenhum pet
        assert m.log.para_jsonl() == g.registro.projecao(i).para_jsonl()
    fab = {i: (lambda cfg, s=g.sementes[i]: T.cerebro(s), lambda p, cfg, sem, **kw: T.laco(p, sem, **kw)) for i in g.cg.ids}

    class G(Grupo):                                                  # o segundo pet com a semente do jogo, como no exportador
        def __init__(self, *a, **kw):
            super().__init__(*a, **kw)
            self.sementes[self.cg.ids[1]] = T.semente_do_segundo_jogo(self.semente)
    import digilab.grupo as dg
    original = dg.Grupo
    dg.Grupo = G
    try:
        r = reproduzir_grupo(g.registro, fab, X.orq.CM, CONFIG_GRUPO_LIGADA, CONFIG_PADRAO, cfg_tv=T.CTV, cfg_tv_jogo=CONFIG_TVJOGO_LIGADA)
    finally:
        dg.Grupo = original
    assert json.dumps(r.resumo(), sort_keys=True, default=repr) == json.dumps(g.resumo(), sort_keys=True, default=repr)


def test_o_grupo_com_a_tv_falha_alto_sem_as_configs():
    with pytest.raises(TVSemChave, match="fonte"):
        Grupo(X.orq.CM, 101, CONFIG_GRUPO_LIGADA, CONFIG_PADRAO, cfg_tv=ConfigTV(ligada=True))
    with pytest.raises(TVSemChave, match="ConfigTV ligada"):
        Grupo(X.orq.CM, 101, CONFIG_GRUPO_LIGADA, CONFIG_PADRAO, cfg_tv_jogo=CONFIG_TVJOGO_LIGADA)
    g = Grupo(X.orq.CM, 101, CONFIG_GRUPO_LIGADA, CONFIG_PADRAO)
    assert "tv" not in g.registro.cabecalho and g.mundo.tv is None
    with pytest.raises(TVSemChave, match="ConfigTV ligada"):
        g.sentido_tela("tv", (1,) * 7)
    g = Grupo(X.orq.CM, 101, CONFIG_GRUPO_LIGADA, CONFIG_PADRAO, cfg_tv=T.CTV)
    with pytest.raises(TVSemChave, match="desligar"):
        g.desligar_tela("tv")
    # o pet que entra sem a mesma TV
    with pytest.raises(TVSemChave):
        g.entrar("A", T.cerebro(101), lambda p, cfg, sem, **kw: T.laco(p, sem, **kw), "modular", "teste")
    # o sentido_tela de um pet do grupo e do mundo comum
    g = Grupo(X.orq.CM, 101, CONFIG_GRUPO_LIGADA, CONFIG_PADRAO, cfg_tv=T.CTV, cfg_tv_jogo=CONFIG_TVJOGO_LIGADA)
    m = g.entrar("A", T.cerebro(101), lambda p, cfg, sem, **kw: T.laco(p, sem, **kw), "modular", "teste")
    with pytest.raises(TVSemChave, match="mundo comum"):
        m.sentido_tela("tv", (1,) * 7)
