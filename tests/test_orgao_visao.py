"""O orgao da visao (GOSTO_VISUAL, OV2; docs/ESPEC_V3_ORGAO_VISAO.md, com as OV1-1 a OV1-14 DECIDIDAS em 2026-11-12): a lista, o evento, o
resumo de quem grava, a TV com os conceitos por programa, o M-SENS por conceito, o gosto por conceito, o mito na valencia, a falha alta e o
replay. Sementes: as dos testes (101, 202, 303)."""
from __future__ import annotations

import dataclasses
import hashlib
import json
import re
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import exportar_gosto_visual as X  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402
import run_v3_gosto_visual as R  # noqa: E402
import sonda_duas_tvs as sd  # noqa: E402

from digilab import orgao  # noqa: E402
from digilab.config import CONFIG_ORGAO_LIGADA, CONFIG_PADRAO, CONFIG_TV_LIGADA, ConfigOrgao  # noqa: E402
from digilab.digibrain.adapt import DigiBrain  # noqa: E402
from digilab.digibrain.afeto import Afeto  # noqa: E402
from digilab.events import AcaoUsuario, Evento, ler_percepcao_tela, percepcao_tela  # noqa: E402
from digilab.genoma_visao import genoma_visao  # noqa: E402
from digilab.motor_corpo import com_corpo  # noqa: E402
from digilab.mundo import MotorMundo, centro_da_celula, reproduzir_mundo  # noqa: E402
from digilab.temperamento import NEUTRO  # noqa: E402
from digilab.tv import TVSemChave  # noqa: E402

CONFIG_MITO = ConfigOrgao(ligada=True, mito=True)


# ------------------------------------------------------------------ a lista
def test_a_lista_tem_os_24_genericos_e_as_56_especies_do_corpus():
    from digilab_fala_livre import corpus
    esp, _, sha = corpus.carregar()
    assert sha.startswith("785f7834a2ee")
    assert {nome for _, nome, _ in orgao.ESPECIES} == set(esp)
    assert len(orgao.GENERICOS_VISAO) == 18 and len(orgao.GENERICOS_SOM) == 6 and len(orgao.ESPECIES) == 56
    assert len(orgao.CONCEITOS) == 80 and orgao.VERSAO_LISTA == "ov-lista-1"
    fora = {"Valkyrimon", "DemiVeemon", "SlashAngemon", "DinoBeemon"}
    assert not fora & {nome for _, nome, _ in orgao.ESPECIES}


def test_o_patrono_e_o_brasao_da_especie_no_jogo():
    texto = (RAIZ / "web" / "app" / "motor" / "nomes.ts").read_text(encoding="utf-8")
    forma = json.loads(re.search(r"DIGIMON_DA_FORMA[^=]*=\s*(\{.*?\});", texto).group(1))
    brasao_do_jogo = {}
    for chave, (nome, _) in forma.items():
        brasao_do_jogo.setdefault(nome, chave.split("_")[0])
    for ident, nome, brasao in orgao.ESPECIES:
        assert brasao_do_jogo[nome] == brasao, nome
        assert orgao.patrono(ident) == {"brasa": "coragem", "cirro": "amizade", "ferrugem": "conhecimento", "limo": "sinceridade"}[brasao]
    assert orgao.patrono("gato") is None


def test_os_pares_canonicos_e_a_falha_alta():
    assert orgao.canonico([("texto", 5), ("gato", 12), ("agumon", 12)], "tv") == (("gato", 12), ("agumon", 12), ("texto", 5))
    for ruim in ([("unicornio", 9)], [("gato", 3)], [("gato", 16)], [("gato", 9), ("gato", 8)], [("a", 4)] * 4):
        with pytest.raises(orgao.PercepcaoInvalida):
            orgao.canonico(ruim, "tv")
    with pytest.raises(orgao.PercepcaoInvalida):                    # OV1-7: o sensivel nunca com a fonte `tela`
        orgao.canonico([("rosto", 9)], "tela")
    with pytest.raises(orgao.PercepcaoInvalida):
        orgao.canonico([], "tv", "ov-lista-0")


# ------------------------------------------------------------------ o evento e o resumo
def test_o_evento_vai_e_volta():
    e = percepcao_tela(30, "tela", orgao.VERSAO_LISTA, (("gato", 12), ("agumon", 7)))
    assert e.valor == "tela|ov-lista-1|gato:12|agumon:7"
    assert ler_percepcao_tela(e) == ("tela", "ov-lista-1", (("gato", 12), ("agumon", 7)))
    assert ler_percepcao_tela(percepcao_tela(0, "tv", orgao.VERSAO_LISTA, ())) == ("tv", "ov-lista-1", ())
    for valor in ("tela", "rua|ov-lista-1", "tela|ov-lista-1|gato", "tela|ov-lista-1|Gato:4", "tela|ov-lista-1|gato:04",
                  "tela|ov-lista-1|a:4|b:4|c:4|d:4"):
        with pytest.raises(ValueError):
            ler_percepcao_tela(Evento(tick=0, tipo="percepcao_tela", valor=valor))


def test_o_resumo_fica_com_o_maximo_da_janela_e_so_na_mudanca():
    r = orgao.ResumoOrgao("tela")
    assert all(r.classificar(t, {"gato": 2}) is None for t in range(4))
    e = r.classificar(4, {"gato": 9, "rosto": 15, "texto": 3})       # gato 9 sai; rosto (sensivel) e texto (abaixo do corte) nao
    assert ler_percepcao_tela(e)[2] == (("gato", 9),)
    r2 = orgao.ResumoOrgao("tela")
    evs = [r2.classificar(t, n) for t, n in enumerate([{"gato": 3}, {"gato": 9}, {}, {"rosto": 15}, {"agumon": 5}])]
    assert evs[:4] == [None] * 4 and ler_percepcao_tela(evs[4])[2] == (("gato", 9), ("agumon", 5))
    assert all(r2.classificar(5 + t, {"gato": 9, "agumon": 5}) is None for t in range(5))   # o mesmo conjunto nao grava de novo


# ------------------------------------------------------------------ a vida com o orgao
def fabricas_orgao(semente: int, cfg_orgao=CONFIG_ORGAO_LIGADA, fonte: str = "grade", brasao: str | None = None):
    cv, co = X.config_vida(), X.config_olhar(fonte)
    g = genoma_visao(semente)
    cfg_tv = CONFIG_TV_LIGADA if fonte == "grade" else X.config_tv("evento")
    kb = {} if brasao is None else {"brasao": brasao}

    def fp(cfg=None):
        return DigiBrain(cfg or CONFIG_PADRAO, cv, orq.CM, semente=semente, cfg_olhar=co, genoma_visao_ovo=g, cfg_orgao=cfg_orgao, **kb)

    def fm(politica, cfg, s):
        return com_corpo(MotorMundo)(politica, cfg, s, NEUTRO, "brasa", obediencia_desligada=True, cfg_mundo=orq.CM, cfg_corpo=R._cc(),
                                     cfg_tela=X.TELA, cfg_tv=cfg_tv, cfg_orgao=cfg_orgao)
    return fp, fm


def viver(semente: int, dias: int = 2, **kw):
    fp, fm = fabricas_orgao(semente, **kw)
    m = fm(fp(CONFIG_PADRAO), CONFIG_PADRAO, semente)
    x, y = centro_da_celula(orq.CM.layout.comedouro, orq.CM)
    for h in range(dias * 24):
        m.avancar(60)
        if h % 3 == 0:
            m.deixar_comida("racao", x, y)
        if h % 5 == 2 and not m.estado()["dormindo"]:
            m.observar(AcaoUsuario.ACARICIAR)
    return m, (fp, fm)


def _h(x) -> str:
    return hashlib.sha256(json.dumps(x, sort_keys=True, default=str).encode("utf-8")).hexdigest()


def test_a_grade_de_hoje_nao_muda_com_o_orgao():
    fp, fm = fabricas_orgao(101)
    com = fm(fp(CONFIG_PADRAO), CONFIG_PADRAO, 101)
    fp0, fm0 = R.fabricas(101, genoma_visao(101))
    sem = fm0(fp0(CONFIG_PADRAO), CONFIG_PADRAO, 101)
    assert com.mundo.tv.programas == sem.mundo.tv.programas
    assert [com.mundo.tv.em(t) for t in range(0, 3000, 7)] == [sem.mundo.tv.em(t) for t in range(0, 3000, 7)]
    progs = com.mundo.tv.conceitos_programas
    assert len(progs) == com.mundo.tv.cfg.n_programas and all(orgao.canonico(p, "tv") == p for p in progs)


@pytest.mark.parametrize("semente", [101, 202])
def test_a_vida_com_o_orgao_ve_habitua_e_aprende_e_o_replay_bate(semente):
    m, (fp, fm) = viver(semente)
    c = sd.cerebro_da_copia(m)
    vistos = [x["olhar"]["conceitos"] for x in c.motivos if x["olhar"].get("conceitos")]
    est = c.estado_interno()["modulos"]["sens"]["orgao"]
    if not any(m.mundo.tv.conceitos_programas):
        pytest.skip("nenhum programa desta semente tem conceito")
    assert vistos, "o pet olhou a TV e nunca viu um conceito"
    assert est["hab"], "a habituacao por conceito nao andou"
    assert all(-CONFIG_ORGAO_LIGADA.teto_gosto <= v <= CONFIG_ORGAO_LIGADA.teto_gosto for v in est["gosto"].values())
    r = reproduzir_mundo(m.log, fp, CONFIG_PADRAO, semente, fm)
    assert _h(sd.cerebro_da_copia(r).estado_interno()) == _h(c.estado_interno())
    assert _h(r.estado()) == _h(m.estado())


def test_o_modo_livre_grava_o_evento_e_o_replay_le():
    fp, fm = fabricas_orgao(303, fonte="evento")
    m = fm(fp(CONFIG_PADRAO), CONFIG_PADRAO, 303)
    m.sentido_tela("tela", (12, 12, 12, 12, 4, 12, 12))
    m.percepcao_tela("tela", [("gato", 13), ("musica", 6)])
    for h in range(24):
        m.avancar(60)
        if h == 12:
            m.percepcao_tela("tela", [])
    assert [e.valor for e in m.log if e.tipo == "percepcao_tela"] == ["tela|ov-lista-1|gato:13|musica:6", "tela|ov-lista-1"]
    with pytest.raises(orgao.PercepcaoInvalida):
        m.percepcao_tela("tela", [("pessoa", 9)])                   # OV1-7: o sensivel fica fora da tela real
    r = reproduzir_mundo(m.log, fp, CONFIG_PADRAO, 303, fm)
    assert _h(sd.cerebro_da_copia(r).estado_interno()) == _h(sd.cerebro_da_copia(m).estado_interno())


def test_a_chave_falha_alto():
    fp0, fm0 = R.fabricas(101, genoma_visao(101))
    m = fm0(fp0(CONFIG_PADRAO), CONFIG_PADRAO, 101)
    with pytest.raises(TVSemChave):
        m.percepcao_tela("tv", [])
    with pytest.raises(TVSemChave):                                   # o orgao sem a TV
        com_corpo(MotorMundo)(fp0(CONFIG_PADRAO), CONFIG_PADRAO, 101, NEUTRO, "brasa", obediencia_desligada=True, cfg_mundo=orq.CM,
                              cfg_corpo=R._cc(), cfg_tela=X.TELA, cfg_orgao=CONFIG_ORGAO_LIGADA)
    fp, fm = fabricas_orgao(101)                                      # o motor com o orgao e o cerebro sem ele: o gancho falha
    with pytest.raises(RuntimeError):
        fm(fp0(CONFIG_PADRAO), CONFIG_PADRAO, 101).avancar(60)
    with pytest.raises(ValueError):                                   # o orgao no cerebro sem o olhar
        DigiBrain(CONFIG_PADRAO, dataclasses.replace(X.config_vida(), olhar=False), orq.CM, semente=101, cfg_orgao=CONFIG_ORGAO_LIGADA)
    with pytest.raises(ValueError):
        ConfigOrgao(mito=True)


# ------------------------------------------------------------------ o mito
def test_o_mito_so_na_valencia_da_decisao_e_so_do_mesmo_brasao():
    from digilab.config import CONFIG_DIGIBRAIN_INATOS
    af = Afeto(CONFIG_PADRAO, X.config_vida(), CONFIG_DIGIBRAIN_INATOS)
    af.ligar_mito(CONFIG_MITO, "brasa")
    S = af.S
    sens = {"falta": {"fome": 0}, "conceitos": {"agumon": S, "gabumon": S, "gato": S},
            "nov_conceito": {"agumon": S, "gabumon": S, "gato": S}}
    out = af.ler(sens)
    assert out["mito"] == CONFIG_MITO.peso_mito                       # so o Agumon (brasa, Coragem) conta
    assert out["V"] == CONFIG_MITO.peso_mito and af.V == 0            # a valencia da decisao; o V guardado nao anda
    sens["nov_conceito"]["agumon"] = 0
    assert af.ler(sens)["mito"] == 0                                  # habituado, nao pesa
    with pytest.raises(ValueError):
        af.ligar_mito(CONFIG_MITO, "fogo")


def test_a_vida_com_o_mito_registra_o_termo_e_o_replay_bate():
    m, (fp, fm) = viver(202, cfg_orgao=CONFIG_MITO, brasao="brasa")
    c = sd.cerebro_da_copia(m)
    assert all("mito" in x for x in c.motivos)
    r = reproduzir_mundo(m.log, fp, CONFIG_PADRAO, 202, fm)
    assert _h(sd.cerebro_da_copia(r).estado_interno()) == _h(c.estado_interno())
