"""A TV no mundo (GOSTO_VISUAL, P1c; docs/ESPEC_GOSTO_VISUAL_P1.md, secoes 1, 2, 4, 8 e 9; GV-15, GV-20, GV-21 e GV-23 pela recomendacao).

- a config: o status de cada campo, os padroes desligados e a falha alto;
- os eventos `trocar_canal` e `sentido_tela`: ida e volta, e o mal formado levanta erro;
- a grade da TV do jogo: deterministica pela rng propria `tv-programas`, independente de quem pergunta e quando, nunca o mesmo programa
  duas vezes seguidas, dentro de [0, C]; o canal do dono vale ate o fim do programa da grade;
- o modo livre gravado: desligada antes do primeiro `sentido_tela`, os niveis em C/15 depois; o `ResumoTela` do GV-15 so emite na mudanca;
- o motor: a TV e o orgao da tela vao juntos (falha alto com um so, sem o mundo, sem o corpo, no grupo); o `sentir_tela` a cada tick, com
  zeros quando o pet nao olha; o assistir na decisao; a novidade pelo corte;
- o replay igual, o evento sem a chave e o evento desconhecido levantando erro, a chave desligada byte a byte.
Sementes: as dos testes (101, 202, 303).
"""
from __future__ import annotations

import json
import sys
from dataclasses import fields, replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import random  # noqa: E402

from digilab.config import ILHAS_DE_TROCA  # noqa: E402
from digilab.config import (CONFIG_CORPO_DRIVES, CONFIG_MUNDO_LIGADA, CONFIG_PADRAO, CONFIG_TELA, CONFIG_TV, CONFIG_TV_LIGADA,  # noqa: E402
                            PARAMETROS_TV, ConfigTela, ConfigTV)
from digilab.corpo import CANAIS_TELA, RECEPTOR_NOVIDADE_TELA  # noqa: E402
from digilab.events import (N_CANAIS_TELA, NIVEL_MAX_TELA, AcaoPet, Evento, LogDeEventos, avanco, ler_sentido_tela,  # noqa: E402
                            ler_trocar_canal, sentido_tela, trocar_canal)
from digilab.instinto_mundo import PoliticaInstintoMundo  # noqa: E402
from digilab.motor_corpo import com_corpo  # noqa: E402
from digilab.mundo import Mundo, MotorMundo, reproduzir_mundo  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402
from digilab.tv import TV, ResumoTela, TVSemChave, intensidades_dos_niveis, nivel_da_media  # noqa: E402

CFG = CONFIG_PADRAO
CM = CONFIG_MUNDO_LIGADA
CC = CONFIG_CORPO_DRIVES                                      # a etapa 6 inteira: drives_novos e gestos (a tela exige os dois)
TELA = ConfigTela(ligada=True)
TV_LIVRE = ConfigTV(ligada=True, fonte="evento")
C = CC.escala
MotorMundoCorpo = com_corpo(MotorMundo)


class Fixa:
    """O pet de teste: sempre a mesma acao; guarda os `ocorrido` do gancho do corpo."""

    nome = "fixa"

    def __init__(self, acao: AcaoPet = AcaoPet.OCIOSO) -> None:
        self.acao = acao
        self.ocorridos: list[dict] = []

    def agir(self, obs, rng):
        return self.acao

    def observar(self, t) -> None:
        return None

    def receber_acao_dono(self, acao, tick) -> None:
        return None

    def consequencia_corpo(self, acao, ocorrido, obs) -> None:
        self.ocorridos.append(ocorrido)

    def estado_interno(self) -> dict:
        return {"nome": self.nome}


def _fp_instinto(cfg=None):
    return PoliticaInstintoMundo(cfg or CFG)


def fabrica(ctv: ConfigTV = CONFIG_TV_LIGADA, ct: ConfigTela = TELA, cc=CC, **kw):
    return lambda p, cfg, s: MotorMundoCorpo(p, cfg, s, obediencia_desligada=True, cfg_mundo=CM, cfg_corpo=cc, cfg_tela=ct, cfg_tv=ctv,
                                             **kw)


def motor(politica=None, semente: int = 101, **kw):
    return fabrica(**kw)(politica if politica is not None else _fp_instinto(), CFG, semente)


def impressao(m) -> str:
    return json.dumps({"estado": m.estado(), "mundo": m.resumo_mundo_fisico(), "corpo": m.corpo.para_dict() if hasattr(m, "corpo") else None,
                       "log": m._log.para_jsonl(), "acoes": [(t, a.value) for t, a in m.acoes_recentes(10 ** 9)]},
                      sort_keys=True, default=str)


# ================================================================== a config
def test_config_status_padroes_e_escala():
    assert set(PARAMETROS_TV) == {f.name for f in fields(ConfigTV)}
    assert {s for s, _ in PARAMETROS_TV.values()} == {"PROPOSTO"}
    assert all("SEM FONTE" in fonte for _, fonte in PARAMETROS_TV.values())
    assert not CONFIG_TV.ligada and CONFIG_TV.fonte == "grade"
    assert CONFIG_TV.escala == CONFIG_TELA.teto_intensidade == C
    assert N_CANAIS_TELA == len(CANAIS_TELA)


@pytest.mark.parametrize("kw,erro", [
    ({"ligada": 1}, "bool"), ({"fonte": "tela"}, "fonte"), ({"celula": (1,)}, "celula"), ({"celula": (-1, 2)}, "celula"),
    ({"escala": 0}, "escala"), ({"n_programas": 1}, "n_programas"), ({"programa_min_ticks": 0}, "programa_min_ticks"),
    ({"programa_min_ticks": 100, "programa_max_ticks": 50}, "programa_min_ticks"), ({"cena_ticks": 0}, "cena_ticks"),
    ({"variacao": -1}, "variacao"), ({"variacao": 450000}, "variacao"), ({"n_programas": 2.0}, "n_programas")])
def test_config_falha_alto(kw, erro):
    with pytest.raises((ValueError, TypeError), match=erro):
        ConfigTV(**kw)


# ================================================================== os eventos
def test_eventos_ida_e_volta():
    e = trocar_canal(7, 3)
    assert (e.tipo, e.valor) == ("trocar_canal", "3") and ler_trocar_canal(e) == 3
    s = sentido_tela(9, "tela", (0, 1, 2, 3, 4, 15, 7))
    assert (s.tipo, s.valor) == ("sentido_tela", "tela|0|1|2|3|4|15|7")
    assert ler_sentido_tela(s) == ("tela", (0, 1, 2, 3, 4, 15, 7))
    # pelo jsonl: o mesmo evento volta
    log = LogDeEventos([e, s])
    assert [x.para_dict() for x in LogDeEventos.de_jsonl(log.para_jsonl())] == [e.para_dict(), s.para_dict()]
    assert len(json.dumps(s.para_dict(), ensure_ascii=False)) < 80          # a ordem de grandeza da espec (~74 bytes)


@pytest.mark.parametrize("valor", ["", "01", "-1", "+1", "1.0", "a", " 1", "١"])
def test_trocar_canal_malformado_levanta_erro(valor):
    with pytest.raises(ValueError):
        ler_trocar_canal(Evento(0, "trocar_canal", valor))


@pytest.mark.parametrize("valor", ["tela|0|0|0|0|0|0", "tela|0|0|0|0|0|0|0|0", "radio|0|0|0|0|0|0|0", "tela|16|0|0|0|0|0|0",
                                   "tela|00|0|0|0|0|0|0", "tela|-1|0|0|0|0|0|0", "tela|1.5|0|0|0|0|0|0", "|0|0|0|0|0|0|0", "tela"])
def test_sentido_tela_malformado_levanta_erro(valor):
    with pytest.raises(ValueError):
        ler_sentido_tela(Evento(0, "sentido_tela", valor))


def test_os_construtores_dos_eventos_falham_alto():
    with pytest.raises(ValueError):
        trocar_canal(0, -1)
    with pytest.raises(ValueError):
        trocar_canal(0, True)
    with pytest.raises(ValueError):
        sentido_tela(0, "tv", (0,) * 6)
    with pytest.raises(ValueError):
        sentido_tela(0, "tv", (0,) * 6 + (NIVEL_MAX_TELA + 1,))
    with pytest.raises(ValueError):
        sentido_tela(0, "radio", (0,) * 7)
    with pytest.raises(ValueError):
        ler_trocar_canal(sentido_tela(0, "tv", (0,) * 7))


# ================================================================== a grade (a TV do jogo)
def _tv(semente: int = 101, cfg: ConfigTV = CONFIG_TV_LIGADA) -> TV:
    return TV(cfg, semente, 0, 0)


def test_a_grade_e_deterministica_e_da_rng_propria():
    a, b = _tv(101), _tv(101)
    assert [a.em(t) for t in range(0, 2000, 7)] == [b.em(t) for t in range(0, 2000, 7)]
    r = random.Random(derivar_semente("tv-programas", 101))
    assert a.programas == tuple(tuple(r.randint(0, C) for _ in CANAIS_TELA) for _ in range(CONFIG_TV.n_programas))
    assert _tv(202).programas != a.programas


def test_a_grade_nao_depende_de_quem_pergunta_nem_quando():
    a, b = _tv(303), _tv(303)
    longe = b.em(5000)                                    # b estende a grade de uma vez; a, aos poucos
    seq_a = [a.em(t) for t in range(5001)]
    assert seq_a[5000] == longe
    assert seq_a == [b.em(t) for t in range(5001)]
    assert a.grade == b.grade


def test_a_grade_troca_de_programa_e_fica_em_zero_a_c():
    tv = _tv(101)
    tv.em(20000)
    g = tv.grade
    assert g[0]["inicio"] == 0 and all(x["fim"] == y["inicio"] for x, y in zip(g, g[1:]))
    assert all(x["programa"] != y["programa"] for x, y in zip(g, g[1:]))
    assert all(CONFIG_TV.programa_min_ticks <= x["fim"] - x["inicio"] <= CONFIG_TV.programa_max_ticks for x in g)
    assert {x["programa"] for x in g} == set(range(CONFIG_TV.n_programas))
    for t in range(0, 20000, 13):
        v = tv.em(t)
        assert list(v) == list(CANAIS_TELA) and all(type(x) is int and 0 <= x <= C for x in v.values())
        seg = g[tv._segmento(t)]
        p = tv.programas[seg["programa"]]
        assert all(abs(v[c] - min(C, max(0, p[k]))) <= CONFIG_TV.variacao for k, c in enumerate(CANAIS_TELA))
    # sem variacao, cada canal e o perfil
    tv0 = _tv(101, replace(CONFIG_TV_LIGADA, variacao=0))
    assert tv0.em(3) == dict(zip(CANAIS_TELA, tv0.programas[tv0.grade[0]["programa"]]))


def test_o_canal_do_dono_vale_ate_o_fim_do_programa_da_grade():
    tv, ref = _tv(101), _tv(101)
    tv.em(0)
    fim = tv.grade[0]["fim"]
    outro = (tv.grade[0]["programa"] + 1) % CONFIG_TV.n_programas
    reg = tv.trocar_canal(outro, 3)
    assert reg == {"tick": 3, "programa": outro, "antes": tv.grade[0]["programa"], "ate": fim}
    assert tv.programa_em(3) == tv.programa_em(fim - 1) == outro
    assert tv.programa_em(fim) == tv.grade[1]["programa"]
    # a grade nao muda nem consome sorteio: depois do programa do dono, a TV e a de referencia
    assert [tv.em(t) for t in range(fim, fim + 300)] == [ref.em(t) for t in range(fim, fim + 300)]
    assert tv.grade == ref.grade
    with pytest.raises(ValueError, match="nao existe"):
        tv.trocar_canal(CONFIG_TV.n_programas, 4)
    with pytest.raises(TVSemChave):
        TV(CONFIG_TV, 101, 0, 0)


def test_o_modo_livre_desligada_antes_e_os_niveis_depois():
    tv = TV(TV_LIVRE, 101, 0, 0)
    assert tv.em(0) is None and tv.programa_em(0) is None and tv.rng is None and tv.programas == ()
    tv.sentir("tela", (0, 1, 2, 3, 13, 14, 15), 5)
    assert tv.em(6) == dict(zip(CANAIS_TELA, (0, 30000, 60000, 90000, 390000, 420000, 450000)))
    assert intensidades_dos_niveis((15,) * 7, C) == {c: C for c in CANAIS_TELA}
    with pytest.raises(TVSemChave):
        tv.trocar_canal(0, 7)
    with pytest.raises(TVSemChave):
        _tv().sentir("tv", (0,) * 7, 0)


def test_o_resumo_do_gv15_so_emite_na_mudanca():
    assert nivel_da_media([0.0]) == 0 and nivel_da_media([1.0]) == 15 and nivel_da_media([0.5]) == 8      # 7,5 sobe (meio para cima)
    assert nivel_da_media([0.0, 1.0 / 15]) == 1                                                          # 0,5 sobe
    with pytest.raises(ValueError):
        nivel_da_media([1.2])
    with pytest.raises(ValueError):
        nivel_da_media([])
    r = ResumoTela("tela", janela=10)
    saidas = [r.amostra(t, [0.5] * 7) for t in range(30)]
    eventos = [e for e in saidas if e is not None]
    assert len(eventos) == 1 and eventos[0].tick == 9 and ler_sentido_tela(eventos[0]) == ("tela", (8,) * 7)
    saidas = [r.amostra(30 + t, [0.5] * 6 + [1.0]) for t in range(10)]
    assert [e.valor for e in saidas if e is not None] == ["tela|8|8|8|8|8|8|15"]
    with pytest.raises(ValueError):
        r.amostra(40, [0.5] * 6)


# ================================================================== o motor: as chaves
def test_a_tv_e_a_tela_vao_juntas_e_falham_alto():
    with pytest.raises(ValueError, match="vao juntos"):
        motor(ct=CONFIG_TELA)                                          # a TV sem o orgao da tela
    with pytest.raises(ValueError, match="vao juntos"):
        motor(ctv=CONFIG_TV)                                           # o orgao sem a TV
    with pytest.raises(ValueError, match="teto_intensidade"):
        motor(ctv=replace(CONFIG_TV_LIGADA, escala=C - 1, variacao=0))
    with pytest.raises(TVSemChave, match="corpo na frente"):
        MotorMundo(_fp_instinto(), CFG, 101, obediencia_desligada=True, cfg_mundo=CM, cfg_tv=CONFIG_TV_LIGADA)
    with pytest.raises(TVSemChave, match="mundo fisico"):
        MotorMundoCorpo(_fp_instinto(), CFG, 101, obediencia_desligada=True, cfg_corpo=CC, cfg_tela=TELA, cfg_tv=CONFIG_TV_LIGADA)
    with pytest.raises(TVSemChave, match="fora do grupo"):
        MotorMundoCorpo(_fp_instinto(), CFG, 101, obediencia_desligada=True, cfg_mundo=CM, cfg_corpo=CC, cfg_tela=TELA,
                        cfg_tv=CONFIG_TV_LIGADA, mundo=Mundo(CM, 101))
    with pytest.raises(ValueError, match="agua|fora do mapa"):
        motor(ctv=replace(CONFIG_TV_LIGADA, celula=(64, 3)))
    with pytest.raises(TypeError):
        motor(ctv=TELA)


def test_sem_a_tv_os_gestos_da_tv_levantam_erro():
    m = MotorMundoCorpo(_fp_instinto(), CFG, 101, obediencia_desligada=True, cfg_mundo=CM, cfg_corpo=CC)
    for f in (lambda: m.trocar_canal(0), lambda: m.sentido_tela("tela", (0,) * 7), lambda: m.olhando_tv()):
        with pytest.raises(TVSemChave):
            f()
    assert "tv" not in m.estado() and "novidades_tela" not in m.estado() and "tv" not in m.resumo_mundo_fisico()
    g = motor()                                                       # a grade: o sentido_tela e da fonte "evento"
    with pytest.raises(TVSemChave):
        g.sentido_tela("tela", (0,) * 7)
    with pytest.raises(TVSemChave):
        motor(ctv=TV_LIVRE).trocar_canal(0)
    with pytest.raises(TVSemChave):
        g.mudar_ilha(sorted(ILHAS_DE_TROCA)[0])


# ================================================================== o motor: o estimulo, o assistir e a novidade
def test_o_sentir_tela_a_cada_tick_com_zeros_sem_olhar():
    m = motor(Fixa(AcaoPet.OCIOSO))
    tv = m.mundo.tv
    vistos = []
    for _ in range(40):
        m.avancar(1)
        vistos.append((dict(m.corpo.estimulo_tela), m.olhando_tv(), tv.em(m._tm(m._estado.tick))))
    assert all(olha for _, olha, _ in vistos)                         # no ninho, parado, a TV no raio da visao
    m.levar_pet(900, 240)                                             # longe da TV: zeros
    m.avancar(5)
    assert not m.olhando_tv() and set(m.corpo.estimulo_tela.values()) == {0}
    # dormindo, tambem nao olha
    d = motor(Fixa(AcaoPet.DORMIR))
    d.avancar(30)
    assert not d.olhando_tv() and set(d.corpo.estimulo_tela.values()) == {0} and d.estado()["novidades_tela"] == []


def test_o_estimulo_e_o_que_a_tv_passa_no_tick():
    m = motor(Fixa(AcaoPet.OCIOSO))
    for _ in range(25):
        t = m._tm(m._estado.tick)
        m.avancar(1)
        # o estimulo que o tick t usou e o que a TV passava em t (o _sentir do tick vem antes do passo)
        assert m.corpo.estimulo_tela == m.mundo.tv.em(t)


def test_o_assistir_na_decisao_em_que_o_pet_olha():
    olha = Fixa(AcaoPet.OCIOSO)
    m = motor(olha)
    m.avancar(150)
    assert olha.ocorridos and all(("atividade", "assistir") in o["estimulos"] for o in olha.ocorridos)
    longe = Fixa(AcaoPet.OCIOSO)
    n = motor(longe)
    n.levar_pet(900, 240)
    n.avancar(150)
    assert longe.ocorridos and not any(("atividade", "assistir") in o["estimulos"] for o in longe.ocorridos)
    # o tedio cai com o assistir: o pet que olha fica com menos tedio que o que nao olha
    assert m.corpo.q["tedio"] < n.corpo.q["tedio"]


def test_a_novidade_pelo_corte_uma_vez_por_subida():
    olha = Fixa(AcaoPet.OCIOSO)
    m = motor(olha)
    lidas = []
    for _ in range(600):
        m.avancar(1)
        lidas.append(m.corpo.leituras_tela()[RECEPTOR_NOVIDADE_TELA])
    nov = m.estado()["novidades_tela"]
    assert nov and nov == sorted(set(nov))
    assert nov[0] == 0                                                # ligar a TV no ninho: a primeira subida
    # cada novidade e uma subida (no tick anterior estava no corte ou abaixo): nunca duas seguidas sem descer
    corte = TELA.corte_novidade
    assert all(b - a > 1 for a, b in zip(nov, nov[1:]))
    assert max(lidas) > corte and min(lidas) <= corte
    # quem nao olha nunca tem novidade
    n = motor(Fixa(AcaoPet.OCIOSO))
    n.levar_pet(900, 240)
    n.avancar(600)
    assert n.estado()["novidades_tela"] == [] and m.corpo.q["curiosidade"] <= n.corpo.q["curiosidade"]


def test_trocar_canal_e_so_da_tv():
    m, ref = motor(semente=202), motor(semente=202)
    m.avancar(10)
    ref.avancar(10)
    p = (m.estado()["tv"]["programa"] + 1) % CONFIG_TV.n_programas
    m.trocar_canal(p)
    assert m.estado()["tv"]["programa"] == p
    assert m._log[-1].tipo == "trocar_canal" and m._log[-1].valor == str(p)
    # nao e contato nem cuidado: o estado do pet e o do outro, tirando a TV
    a, b = m.estado(), ref.estado()
    assert {k: v for k, v in a.items() if k != "tv"} == {k: v for k, v in b.items() if k != "tv"}


def test_trocar_de_politica_nao_muda_a_grade():
    a, b = motor(Fixa(AcaoPet.OCIOSO), semente=303), motor(semente=303)
    a.avancar(400)
    b.avancar(400)
    assert a.mundo.tv.programas == b.mundo.tv.programas
    assert [a.mundo.tv.em(t) for t in range(400)] == [b.mundo.tv.em(t) for t in range(400)]


# ================================================================== o replay
def _vida_grade(semente: int):
    m = motor(semente=semente)
    for passo in range(12):
        m.avancar(45)
        if passo % 3 == 1:
            m.trocar_canal(passo % CONFIG_TV.n_programas)
    return m


def _vida_livre(semente: int):
    m = motor(semente=semente, ctv=TV_LIVRE)
    r = ResumoTela("tela")
    rng = random.Random(semente)                                      # o acaso "real" do teste: so entra no log pelo evento
    for _ in range(40):
        m.avancar(10)
        for s in range(10):
            e = r.amostra(m._estado.tick, [rng.random() for _ in CANAIS_TELA])
            if e is not None:
                m.sentido_tela(*ler_sentido_tela(e))
    return m


@pytest.mark.parametrize("vida,fabricar", [(_vida_grade, lambda: fabrica()), (_vida_livre, lambda: fabrica(ctv=TV_LIVRE))])
@pytest.mark.parametrize("semente", (101, 202))
def test_o_replay_e_igual(vida, fabricar, semente):
    m = vida(semente)
    tipos = {e.tipo for e in m._log}
    assert tipos & {"trocar_canal", "sentido_tela"}
    r = reproduzir_mundo(LogDeEventos.de_jsonl(m._log.para_jsonl()), _fp_instinto, CFG, semente, fabricar())
    assert impressao(r) == impressao(m)
    assert impressao(vida(semente)) == impressao(m)                  # a mesma vida duas vezes, ate o ultimo bit


def test_o_replay_sem_a_chave_e_o_evento_desconhecido_levantam_erro():
    sem_tv = lambda p, cfg, s: MotorMundoCorpo(p, cfg, s, obediencia_desligada=True, cfg_mundo=CM, cfg_corpo=CC)  # noqa: E731
    for ev in (trocar_canal(5, 1), sentido_tela(5, "tv", (1,) * 7)):
        log = LogDeEventos([avanco(0, 5), ev, avanco(5, 5)])
        with pytest.raises(TVSemChave):
            reproduzir_mundo(log, _fp_instinto, CFG, 101, sem_tv)
    # a fonte errada tambem
    with pytest.raises(TVSemChave):
        reproduzir_mundo(LogDeEventos([avanco(0, 5), sentido_tela(5, "tv", (1,) * 7)]), _fp_instinto, CFG, 101, fabrica())
    with pytest.raises(TVSemChave):
        reproduzir_mundo(LogDeEventos([avanco(0, 5), trocar_canal(5, 1)]), _fp_instinto, CFG, 101, fabrica(ctv=TV_LIVRE))
    with pytest.raises(ValueError, match="nao existe"):
        reproduzir_mundo(LogDeEventos([avanco(0, 5), trocar_canal(5, 99)]), _fp_instinto, CFG, 101, fabrica())
    with pytest.raises(ValueError, match="desconhecido"):
        reproduzir_mundo(LogDeEventos([avanco(0, 5), Evento(5, "tv_desconhecida", "1")]), _fp_instinto, CFG, 101, fabrica())
    # o replay da v1 (sem mundo) tambem nao entende os eventos novos
    from digilab.engine import reproduzir
    with pytest.raises(ValueError):
        reproduzir(LogDeEventos([avanco(0, 5), trocar_canal(5, 1)]), _fp_instinto, CFG, 101)


# ================================================================== a chave desligada
@pytest.mark.parametrize("semente", (101, 202, 303))
def test_desligada_a_vida_de_hoje_byte_a_byte(semente):
    """Com a ConfigTV e a ConfigTela desligadas (passadas ou nao), a vida do corpo no mundo e a mesma: nenhuma chave nova no estado(), no
    resumo do mundo nem no corpo. O gabarito das vidas de antes do P1 e o tests/test_gabarito_gosto_visual.py."""
    def vida(**kw):
        m = MotorMundoCorpo(_fp_instinto(), CFG, semente, obediencia_desligada=True, cfg_mundo=CM, cfg_corpo=CC, **kw)
        for _ in range(8):
            m.avancar(45)
            m.deixar_comida("racao", 160, 240)
        return m
    hoje, desligada = vida(), vida(cfg_tv=CONFIG_TV, cfg_tela=CONFIG_TELA)
    assert impressao(hoje) == impressao(desligada)
    assert "tv" not in hoje.estado() and "novidades_tela" not in hoje.estado() and "tela" not in hoje.corpo.para_dict()
    assert hoje.mundo.tv is None
