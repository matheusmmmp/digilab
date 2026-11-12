"""O gosto no cerebro (GOSTO_VISUAL, P1d; docs/ESPEC_GOSTO_VISUAL_P1.md, secoes 5, 6, 8 e 9; GV-16 e GV-19 pela recomendacao).

- a config: a subchave `olhar` nasce desligada, e bool e nao se combina com a fala_unidades; a ConfigOlhar com o status de cada campo e a
  falha alto; a escala e a da tela e a da TV;
- o genoma da visao: deterministico pela rng propria `visao-ovo`, dentro das faixas, sem tocar a rng global; o vazio e o controle;
- o M-SENS: o pico, o agrado no otimo e longe dele, a exposicao com o teto; os receptores da tela falham alto sem a subchave;
- o olhar escolhido e reforcado: o assistir so nas decisoes do olhar, o H[olhar] e o desfecho da classe `tela` andam, o canal
  `gosto_visual` no r; o agrado no corpo so com a sub-chave da GV-16;
- o pet escolhe entre programas de perfis diferentes conforme o genoma (o genoma x o programa);
- o replay igual, ate o ultimo bit;
- a chave desligada: nenhum campo novo, os ganchos falham alto, e o olhar sem a TV deixa a vida do pet igual.
Sementes: as dos testes (101, 202, 303).
"""
from __future__ import annotations

import json
import random
import sys
from dataclasses import fields, replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab.config import (CANAIS_TELA, CONFIG_CORPO_DRIVES, CONFIG_DIGIBRAIN, CONFIG_DIGIBRAIN_LIGADA, CONFIG_MUNDO_LIGADA,  # noqa: E402
                            CONFIG_OLHAR, CONFIG_PADRAO, CONFIG_TELA, CONFIG_TV, CONFIG_TV_LIGADA, PARAMETROS_OLHAR, ConfigDigibrain,
                            ConfigOlhar, ConfigTela, ConfigTV)
from digilab.digibrain import DigiBrain  # noqa: E402
from digilab.digibrain._comum import mul  # noqa: E402
from digilab.digibrain.sens import RECEPTORES_TELA, Sens, pico  # noqa: E402
from digilab.events import LogDeEventos  # noqa: E402
from digilab.genoma_paladar import genoma_paladar  # noqa: E402
from digilab.genoma_visao import FLUXO, GenomaVisao, genoma_visao, genoma_visao_vazio  # noqa: E402
from digilab.motor_corpo import com_corpo  # noqa: E402
from digilab.mundo import MotorMundo, reproduzir_mundo  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402
from digilab.tv import ID_TV  # noqa: E402

CFG = CONFIG_PADRAO
CM = CONFIG_MUNDO_LIGADA
CC = CONFIG_CORPO_DRIVES                                      # a tela exige os drives novos e os gestos
TELA = ConfigTela(ligada=True)
TV_LIVRE = ConfigTV(ligada=True, fonte="evento")
CD = replace(CONFIG_DIGIBRAIN_LIGADA, olhar=True)
S = 1024
C = CONFIG_OLHAR.escala
MotorMundoCorpo = com_corpo(MotorMundo)
# dois programas de perfis opostos (16 niveis do evento; o volume baixo nos dois, abaixo do corte do estresse) e um genoma no otimo de cada
P = (12, 12, 12, 12, 4, 12, 12)
Q = (3, 3, 3, 3, 4, 3, 3)


def genoma_no(niveis) -> GenomaVisao:
    return GenomaVisao({c: n * (C // 15) for c, n in zip(CANAIS_TELA, niveis)}, {c: CONFIG_OLHAR.largura_min for c in CANAIS_TELA})


class Gravador:
    """Embrulho que so le (como o Registro do orquestrador): guarda o `ocorrido` do corpo de cada decisao e repassa o resto."""

    def __init__(self, interna) -> None:
        self._interna = interna
        self.ocorridos: list[dict] = []

    def agir(self, obs, rng):
        return self._interna.agir(obs, rng)

    def observar(self, t) -> None:
        self._interna.observar(t)

    def consequencia_corpo(self, acao, ocorrido, obs) -> None:
        self.ocorridos.append(ocorrido)
        self._interna.consequencia_corpo(acao, ocorrido, obs)

    def estado_interno(self) -> dict:
        return self._interna.estado_interno()

    def __getattr__(self, nome: str):
        interna = self.__dict__.get("_interna")
        if interna is None:
            raise AttributeError(nome)
        return getattr(interna, nome)


def cerebro(semente: int, cd: ConfigDigibrain = CD, **kw) -> DigiBrain:
    return DigiBrain(CFG, cd, CM, semente=semente, **kw)


def fabrica(ctv: ConfigTV | None = CONFIG_TV_LIGADA, ct: ConfigTela | None = TELA):
    extra = {} if ctv is None else {"cfg_tela": ct, "cfg_tv": ctv}
    return lambda p, cfg, s: MotorMundoCorpo(p, cfg, s, obediencia_desligada=True, cfg_mundo=CM, cfg_corpo=CC, **extra)


def viver(semente: int, cd: ConfigDigibrain = CD, ctv: ConfigTV | None = CONFIG_TV_LIGADA, niveis=None, ticks: int = 1440,
          trocas: bool = False, **kw):
    g = Gravador(cerebro(semente, cd, **kw))
    m = fabrica(ctv)(g, CFG, semente)
    if niveis is not None:
        m.sentido_tela("tv", niveis)
    for passo in range(ticks // 60):
        m.avancar(60)
        m.deixar_comida("racao", 160, 240)
        if trocas and passo % 4 == 1:
            m.trocar_canal(passo % CONFIG_TV.n_programas)
    return m, g


def impressao(m) -> str:
    return json.dumps({"estado": m.estado(), "mundo": m.resumo_mundo_fisico(), "corpo": m.corpo.para_dict(), "log": m._log.para_jsonl(),
                       "acoes": [(t, a.value) for t, a in m.acoes_recentes(10 ** 9)],
                       "cerebro": m.politica.estado_interno()}, sort_keys=True, default=str)


def de_vida(m) -> str:
    """so a vida do pet (o log, o estado, as acoes, o corpo e o mundo), sem o registro do cerebro"""
    return json.dumps({"estado": m.estado(), "mundo": m.resumo_mundo_fisico(), "corpo": m.corpo.para_dict(), "log": m._log.para_jsonl(),
                       "acoes": [(t, a.value) for t, a in m.acoes_recentes(10 ** 9)]}, sort_keys=True, default=str)


# ================================================================== a config
def test_a_subchave_nasce_desligada_e_falha_alto():
    assert CONFIG_DIGIBRAIN.olhar is False and CONFIG_DIGIBRAIN_LIGADA.olhar is False
    with pytest.raises(TypeError):
        ConfigDigibrain(olhar=1)
    with pytest.raises(ValueError, match="olhar"):
        ConfigDigibrain(olhar=True, fala_unidades=True)


def test_a_config_do_olhar_status_e_escala():
    assert set(PARAMETROS_OLHAR) == {f.name for f in fields(ConfigOlhar)}
    assert {s for s, _ in PARAMETROS_OLHAR.values()} == {"PROPOSTO"}
    assert all("SEM FONTE" in fonte for _, fonte in PARAMETROS_OLHAR.values())
    assert CONFIG_OLHAR.escala == CONFIG_TELA.teto_intensidade == CONFIG_TV.escala
    assert CONFIG_OLHAR.agrado_no_corpo is False


@pytest.mark.parametrize("kw", [{"agrado_no_corpo": 1}, {"largura_min": 0}, {"largura_min": 5, "largura_max": 4},
                                {"largura_max": 450001}, {"tau_exposicao": 10}, {"teto_exposicao": 2000}, {"w_gosto": -1},
                                {"w0_olhar": (("nada", 1),)}, {"w0_olhar": (("vies", 1.0),)}])
def test_a_config_do_olhar_falha_alto(kw):
    with pytest.raises((ValueError, TypeError)):
        ConfigOlhar(**kw)


# ================================================================== o genoma da visao
def test_o_genoma_e_deterministico_da_rng_propria_e_nas_faixas():
    estado = random.getstate()
    g = genoma_visao(101)
    assert random.getstate() == estado                               # nao toca a rng global
    assert g == genoma_visao(101) and g != genoma_visao(202)
    r = random.Random(derivar_semente(FLUXO, 101))                    # a ordem: canal a canal, o otimo e a largura
    for c in CANAIS_TELA:
        assert g.otimo[c] == r.randint(0, C) and g.largura[c] == r.randint(CONFIG_OLHAR.largura_min, CONFIG_OLHAR.largura_max)
    for s in (101, 202, 303, 404, 505):
        h = genoma_visao(s)
        assert all(0 <= v <= C for v in h.otimo.values())
        assert all(CONFIG_OLHAR.largura_min <= v <= CONFIG_OLHAR.largura_max for v in h.largura.values())
    assert FLUXO == "visao-ovo" and derivar_semente(FLUXO, 101) != derivar_semente("paladar-ovo", 101)
    # o genoma do paladar (e o resto do ovo) nao depende do da visao
    antes = genoma_paladar(101)
    genoma_visao(101)
    assert genoma_paladar(101) == antes


def test_o_genoma_vazio_e_a_escala_do_cerebro_e_a_falha_alto():
    v = genoma_visao_vazio()
    assert set(v.otimo.values()) == {C // 2} and len(set(v.largura.values())) == 1
    otimo, largura = genoma_no(P).na_escala(S, C)
    assert otimo["cor"] == 819 and largura["cor"] == S // 4          # div_arred(360000 x 1024, 450000) = 819
    with pytest.raises(ValueError):
        GenomaVisao({"cor": 1}, {"cor": 1})
    with pytest.raises(ValueError):
        GenomaVisao(dict.fromkeys(CANAIS_TELA, -1), dict.fromkeys(CANAIS_TELA, 1))
    with pytest.raises(ValueError):
        GenomaVisao(dict.fromkeys(CANAIS_TELA, 0), dict.fromkeys(CANAIS_TELA, 0))
    with pytest.raises(ValueError):
        GenomaVisao(dict.fromkeys(CANAIS_TELA, C + 1), dict.fromkeys(CANAIS_TELA, 1)).na_escala(S, C)


# ================================================================== o M-SENS: o pico, o agrado e a exposicao
def sens(niveis=P) -> Sens:
    return Sens(CFG, CM, olhar=CONFIG_OLHAR, genoma=genoma_no(niveis))


def no_s(niveis) -> dict:
    return {c: n * S // 15 for c, n in zip(CANAIS_TELA, niveis)}


def test_o_pico_e_o_agrado():
    assert pico(0, 100, S) == S and pico(50, 100, S) == S // 2 and pico(-50, 100, S) == S // 2 and pico(100, 100, S) == 0
    assert pico(300, 100, S) == 0
    with pytest.raises(ValueError):
        pico(1, 0, S)
    s = sens(P)
    assert s.agrado(no_s(P)) >= S - 8                                 # no otimo (o arredondamento da escala)
    assert s.agrado(no_s(Q)) == (S + 3) // 7                          # longe: so o volume (o mesmo nos dois) agrada; |12 - 3| passa da largura
    assert s.agrado(no_s(P)) == s.agrado_inato(no_s(P))               # sem exposicao, o alvo e o otimo


def test_a_exposicao_anda_para_o_visto_com_o_teto():
    s = sens(P)
    longe = no_s(Q)
    for _ in range(2000):
        s.expor(longe)
    teto = CONFIG_OLHAR.teto_exposicao
    assert all(v == -teto for c, v in s.desloc.items() if c != "volume") and s.desloc["volume"] == 0
    assert s.agrado(no_s(P)) < s.agrado_inato(no_s(P))               # o alvo saiu do otimo: o inato fica, o aprendido anda
    assert s.estado_interno()["tela"]["exposicoes"] == 2000


def test_os_receptores_da_tela_sem_a_subchave_falham_alto():
    m = fabrica()(cerebro(101, CONFIG_DIGIBRAIN_LIGADA), CFG, 101)    # o modular sem o olhar, com a TV
    with pytest.raises(RuntimeError, match="olhar"):
        m.avancar(30)
    s = Sens(CFG, CM)
    with pytest.raises(RuntimeError, match="olhar"):
        s.agrado(no_s(P))
    with pytest.raises(ValueError):
        Sens(CFG, CM, olhar=CONFIG_OLHAR)                            # a ConfigOlhar sem o genoma
    assert RECEPTORES_TELA[-1] == "novidade_tela" and len(RECEPTORES_TELA) == len(CANAIS_TELA) + 1


# ================================================================== o olhar escolhido e reforcado
@pytest.fixture(scope="module")
def vida_grade():
    return viver(101, ticks=2880, trocas=True)


def test_o_olhar_e_escolhido_e_o_motor_o_executa_parado(vida_grade):
    m, g = vida_grade
    motivos = m.politica.estado_interno()["motivos"]
    olhar = [mt["k"] for mt in motivos if mt["escolha"][0] == "olhar"]
    assert olhar, "o pet nunca olhou a TV"
    assert all(mt["acao"] == "ocioso" and mt["escolha"] == ["olhar", "tela", ID_TV] for mt in motivos if mt["escolha"][0] == "olhar")
    # o assistir do corpo e exatamente o das decisoes do olhar (a regra provisoria da P1c, o ocioso perto da TV, saiu para o modular)
    assistiu = [k for k, o in enumerate(g.ocorridos) if ("atividade", "assistir") in o["estimulos"]]
    assert assistiu == olhar
    ociosas_perto = [mt["k"] for mt in motivos if mt["escolha"][0] == "ocioso" and mt["olhar"]["telas"]]
    assert ociosas_perto and not set(ociosas_perto) & set(assistiu)
    # a unidade de olhar so existe com a TV a vista, e sempre no fim da lista
    for mt in motivos:
        chaves = [u["chave"][0] for u in mt["unidades"]]
        assert ("olhar" in chaves) == bool(mt["olhar"]["telas"])
        if "olhar" in chaves:
            assert chaves[-1] == "olhar" and chaves.count("olhar") == 1
        assert all("gosto" in u["termos"] for u in mt["unidades"])


def test_o_olhar_e_reforcado_pelo_p1_e_pelo_p2_e_o_gosto_visual_entra_no_r(vida_grade):
    m, _ = vida_grade
    est = m.politica.estado_interno()
    plast = est["modulos"]["plast"]
    assert list(plast["H"])[-1] == "olhar" and any(plast["H"]["olhar"])        # o P2: a linha do olhar andou
    assert list(plast["desfecho"])[-1] == "tela" and any(plast["desfecho"]["tela"]) and plast["consumos"]["tela"] > 0   # o P1
    olhou = [mt for mt in est["motivos"] if mt["escolha"][0] == "olhar" and mt["consequencia"] is not None]
    assert olhou
    for mt in olhou:
        cons = mt["consequencia"]
        gv = cons["olhar"]["gosto_visual"]
        assert gv == mul(CONFIG_OLHAR.ganho_gosto_visual, cons["olhar"]["agrado"] - S // 2, S)
        assert cons["canais"]["gosto_visual"] == gv and sum(cons["canais"].values()) == cons["r"]
        assert cons["p1"]["classe"] == "tela"
    nao_olhou = [mt for mt in est["motivos"] if mt["escolha"][0] != "olhar" and mt["consequencia"] is not None]
    assert all(mt["consequencia"]["olhar"] is None and "gosto_visual" not in mt["consequencia"]["canais"] for mt in nao_olhou)
    assert est["modulos"]["sens"]["tela"]["exposicoes"] == len(olhou)
    assert est["olhar"]["genoma_visao"] == genoma_visao(101).para_dict()


def test_o_gosto_na_decisao_seguinte_e_o_agrado_do_que_ele_olhava(vida_grade):
    m, _ = vida_grade
    motivos = m.politica.estado_interno()["motivos"]
    seguidas = [(a, b) for a, b in zip(motivos, motivos[1:]) if a["escolha"][0] == "olhar" and b["olhar"]["telas"]]
    assert seguidas
    for a, b in seguidas:
        ag = b["olhar"]["agrado"]
        un = next(u for u in b["unidades"] if u["chave"][0] == "olhar")
        assert b["olhar"]["olhava"] == ID_TV and un["termos"]["gosto"] == b["olhar"]["gosto"]
        assert un["termos"]["gosto"] == mul(CONFIG_OLHAR.w_gosto, ag - S // 2, S)
        assert all(u["termos"]["gosto"] == 0 for u in b["unidades"] if u["chave"][0] != "olhar")


def test_o_agrado_no_corpo_so_com_a_sub_chave():
    _, sem = viver(101, ticks=1440)
    assert not any(e[0] == "agrado_tela" for o in sem.ocorridos for e in o["estimulos"])
    _, com = viver(101, ticks=1440, cfg_olhar=replace(CONFIG_OLHAR, agrado_no_corpo=True))
    agrados = [e for o in com.ocorridos for e in o["estimulos"] if e[0] == "agrado_tela"]
    assistir = [o for o in com.ocorridos if ("atividade", "assistir") in o["estimulos"]]
    assert agrados and len(agrados) == len(assistir) and all(0 <= a <= S for _, a in agrados)


# ================================================================== o genoma x o programa
@pytest.mark.parametrize("semente", (101, 202, 303))
def test_o_pet_escolhe_o_programa_conforme_o_genoma(semente):
    """O mesmo pet (a mesma semente, a mesma vida ate a primeira decisao em que o gosto pesa), com o genoma no otimo de P ou no de Q, diante
    de P ou de Q (o modo livre gravado, um programa parado): olha mais o programa do proprio genoma."""
    olhou = {}
    for g in ("P", "Q"):
        for prog in ("P", "Q"):
            _, c = viver(semente, ctv=TV_LIVRE, niveis=P if prog == "P" else Q, ticks=2880, genoma_visao_ovo=genoma_no(P if g == "P" else Q))
            olhou[g, prog] = sum(1 for mt in c.estado_interno()["motivos"] if mt["escolha"][0] == "olhar")
    assert olhou["P", "P"] > olhou["Q", "P"] and olhou["Q", "Q"] > olhou["P", "Q"], olhou


# ================================================================== o replay
@pytest.mark.parametrize("semente,ctv", [(101, CONFIG_TV_LIGADA), (202, TV_LIVRE)])
def test_o_replay_e_igual(semente, ctv):
    def vida():
        g = cerebro(semente)
        m = fabrica(ctv)(g, CFG, semente)
        r = random.Random(semente)                                    # o acaso "real" do modo livre so entra no log pelo evento
        for passo in range(16):
            m.avancar(45)
            if ctv.fonte == "evento":
                m.sentido_tela("tv", tuple(r.randint(0, 15) for _ in CANAIS_TELA))
            elif passo % 3 == 1:
                m.trocar_canal(passo % CONFIG_TV.n_programas)
            m.deixar_comida("racao", 160, 240)
        return m
    m = vida()
    assert any(mt["escolha"][0] == "olhar" for mt in m.politica.estado_interno()["motivos"])
    r = reproduzir_mundo(LogDeEventos.de_jsonl(m._log.para_jsonl()), lambda cfg=None: cerebro(semente), CFG, semente, fabrica(ctv))
    assert impressao(r) == impressao(m)
    assert impressao(vida()) == impressao(m)                          # a mesma vida duas vezes, ate o ultimo bit


# ================================================================== a chave desligada
def test_desligada_nenhum_campo_novo_e_os_ganchos_falham_alto():
    c = cerebro(101, CONFIG_DIGIBRAIN_LIGADA)
    m = fabrica(None)(c, CFG, 101)
    m.avancar(300)
    est = c.estado_interno()
    assert "olhar" not in est and "tela" not in est["modulos"]["sens"] and "tela" not in est["modulos"]["sens"]["hab"]
    assert "olhar" not in est["modulos"]["plast"]["H"] and "tela" not in est["modulos"]["plast"]["consumos"]
    assert all("olhar" not in mt and "gosto" not in mt["unidades"][0]["termos"] for mt in est["motivos"])
    assert all(mt["consequencia"] is None or "olhar" not in mt["consequencia"] for mt in est["motivos"])
    for gancho, args in (("ver_tela", ([],)), ("olhando_tela", ()), ("agrado_tela", ({},))):
        with pytest.raises(RuntimeError, match="olhar"):
            getattr(c, gancho)(*args)
    with pytest.raises(ValueError, match="olhar"):
        DigiBrain(CFG, CONFIG_DIGIBRAIN_LIGADA, CM, semente=101, cfg_olhar=CONFIG_OLHAR)
    with pytest.raises(ValueError, match="genoma"):
        DigiBrain(CFG, CD, CM)                                        # o olhar sem a semente nem o genoma


@pytest.mark.parametrize("semente", (101, 202))
def test_o_olhar_sem_a_tv_deixa_a_vida_do_pet_igual(semente):
    """Sem a TV no mundo nao ha linha da classe `tela` nem unidade de olhar: a vida do pet (o log, o estado, as acoes, o corpo, o mundo)
    com a subchave ligada e a mesma da desligada; so o registro do cerebro ganha os campos novos."""
    ligada, _ = viver(semente, CD, ctv=None, ticks=1440)
    desligada, _ = viver(semente, CONFIG_DIGIBRAIN_LIGADA, ctv=None, ticks=1440)
    assert de_vida(ligada) == de_vida(desligada)


def test_a_chave_desligada_byte_a_byte_com_o_modular():
    """Com a subchave desligada (passada ou o padrao) a vida do modular e o registro do cerebro sao os de hoje. O gabarito das vidas de antes
    do P1 e o tests/test_gabarito_gosto_visual.py; o do modular para a web, o tests/test_gabarito_digibrain_modular_web.py."""
    a, _ = viver(303, CONFIG_DIGIBRAIN_LIGADA, ctv=None, ticks=720)
    b, _ = viver(303, replace(CONFIG_DIGIBRAIN_LIGADA, olhar=False), ctv=None, ticks=720)
    assert impressao(a) == impressao(b)
