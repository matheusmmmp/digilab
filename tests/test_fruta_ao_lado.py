"""A fruta ao lado da racao (o RP-2 de docs/futuro/paladar.md, decidido pelo Matheus em 2026-10-14; os numeros combinados com o adendo 5
do plano do J5, do C): o lado do mundo e do dono.

- A config e o evento: os numeros combinados, as falhas altas, o `deixar_fruta` so de fruta.
- G2: desligada, as 92 vidas de tests/gabaritos/fruta_ao_lado_vidas_de_hoje.json (gravado antes, tests/gabarito_fruta_ao_lado.py) byte a
  byte, sem a chave e com a chave explicita desligada.
- A mecanica, numa vida com a regra: toda fruta vai logo depois de uma racao do dono, no mesmo tick; as celulas sao a coluna do comedouro
  + 1 nas linhas do comedouro - 1, 0 e + 1, com o tipo pela permutacao da vida; no maximo uma madura de cada tipo ao lado, e a reposicao
  so da que falta; fora do orcamento e sem contato; o consumo com o tipo e a origem `dono_ao_lado`.
- A permutacao: uniforme entre as 6 sobre as sementes, pela rng propria, sem tocar o `random` global.
- G1: o replay refaz as frutas ao lado e o resto da vida. As recusas (o estilo, a chave, a fruta sem racao, o grupo).
Sementes: so as dos testes.
"""
from __future__ import annotations

import json
import random
import sys
from collections import Counter
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import gabarito_dois_pets as gdp  # noqa: E402
import gabarito_fruta_ao_lado as gfa  # noqa: E402
import gabarito_pet_que_pensa_plano as gpl  # noqa: E402
import gabarito_pqp_mundo as gq  # noqa: E402

from digilab.config import (CONFIG_FRUTA_AO_LADO, CONFIG_FRUTA_AO_LADO_LIGADA, CONFIG_GRUPO_LIGADA,  # noqa: E402
                            CONFIG_PADRAO, CONFIG_PALADAR_LIGADA, ConfigFrutaAoLado)
from digilab.donos import criar_dono  # noqa: E402
from digilab.events import FRUTAS, Evento, LogDeEventos, deixar_fruta, ler_deixar_fruta  # noqa: E402
from digilab.grupo import PetDoGrupo, sementes_do_grupo, simular_grupo  # noqa: E402
from digilab.instinto_mundo import PoliticaInstintoMundo  # noqa: E402
from digilab.motor_corpo import com_corpo  # noqa: E402
from digilab.mundo import (ORIGEM_AO_LADO, DonoComLugar, DonoFrutaAoLado, MotorMundo, centro_da_celula,  # noqa: E402
                           reproduzir_mundo, simular_vida_mundo)
from digilab.protocol import derivar_semente  # noqa: E402

CM = gq.LAYOUTS["padrao"]
LIGADA = CONFIG_FRUTA_AO_LADO_LIGADA
GRAVADO = json.loads(gfa.ARQUIVO.read_text(encoding="utf-8"))
BASE_MUNDO, BASE_CORPO = gq.MotorMundo, gq.MotorMundoCorpo
assert gpl.MotorMundoCorpo is BASE_CORPO
DIAS = 4


class Regra(DonoFrutaAoLado):
    """a regra de verdade, que tambem anota o que viu no estado() e o que pos, a cada chamada"""

    def __init__(self, *a, **kw) -> None:
        super().__init__(*a, **kw)
        self.chamadas: list[tuple] = []

    def acoes(self, estado):
        n = len(self.dono.lugares) - self._vistos
        saida = super().acoes(estado)
        self.chamadas.append((estado["tick"], dict(estado["fruta_ao_lado"]["no_chao"]), n, [a.tipo for a in saida]))
        return saida


def fabrica(cfal=LIGADA, corpo=None, cpal=None):
    if corpo is None:
        return lambda p, cfg, s: MotorMundo(p, cfg, s, obediencia_desligada=True, cfg_mundo=CM, cfg_fruta_ao_lado=cfal,  # noqa: E731
                                            **({} if cpal is None else {"cfg_paladar": cpal}))
    return lambda p, cfg, s: com_corpo(MotorMundo)(p, cfg, s, obediencia_desligada=True, cfg_mundo=CM, cfg_corpo=corpo,  # noqa: E731
                                                   cfg_fruta_ao_lado=cfal, **({} if cpal is None else {"cfg_paladar": cpal}))


def vida(s=101, dono_nome="atencioso", dias=DIAS, cfal=LIGADA, corpo=None, cpal=None, regra=True):
    dono = DonoComLugar(criar_dono(dono_nome), "comedouro", s, dono_nome, CM)
    r = Regra(dono, s, cfal, CM) if regra else None
    v = simular_vida_mundo(dono_nome, dono, PoliticaInstintoMundo(CONFIG_PADRAO), s, dias, 16 * dias, fabrica(cfal, corpo, cpal),
                           rotulo_dono=dono_nome, ao_lado=r)
    return v, dono, r


# ================================================================== a config e o evento
def test_os_numeros_combinados():
    c = CONFIG_FRUTA_AO_LADO
    assert not c.ligada and LIGADA.ligada
    assert c.tipos == FRUTAS == ("a", "b", "c") and c.coluna == 1 and c.linhas == (-1, 0, 1) and c.teto_por_tipo == 1
    assert ORIGEM_AO_LADO == "dono_ao_lado"
    # no layout de hoje: o comedouro (10, 15), a coluna 11, as linhas 14, 15 e 16
    r = DonoFrutaAoLado(DonoComLugar(criar_dono("atencioso"), "comedouro", 101, "atencioso", CM), 101, LIGADA, CM)
    assert CM.layout.comedouro == (10, 15)
    assert sorted(r.celulas.values()) == [centro_da_celula((11, y), CM) for y in (14, 15, 16)]
    assert [r.celulas[f] for f in r.permutacao] == [centro_da_celula((11, y), CM) for y in (14, 15, 16)]


def test_as_falhas_altas_da_config():
    for kw in (dict(ligada=1), ):
        with pytest.raises(TypeError):
            ConfigFrutaAoLado(**kw)
    for kw in (dict(tipos=()), dict(tipos=("a", "a", "b")), dict(tipos=("a", "racao", "b")), dict(linhas=(0, 1)),
               dict(linhas=(0, 0, 1)), dict(coluna=1.0), dict(teto_por_tipo=0)):
        with pytest.raises(ValueError):
            ConfigFrutaAoLado(**kw)
    ConfigFrutaAoLado(tipos=("b",), linhas=(0,))


def test_o_evento_so_de_fruta():
    e = deixar_fruta(7, "b", 184, 248)
    assert e == Evento(7, "deixar_fruta", "b|184|248") and ler_deixar_fruta(e) == ("b", 184, 248)
    with pytest.raises(ValueError):
        deixar_fruta(7, "racao", 1, 1)
    for valor in ("racao|1|1", "b|1", "b|x|1"):
        with pytest.raises(ValueError):
            ler_deixar_fruta(Evento(7, "deixar_fruta", valor))
    with pytest.raises(ValueError):
        ler_deixar_fruta(Evento(7, "deixar_comida", "b|1|1"))


# ================================================================== G2
def test_g2_desligada_as_vidas_de_hoje(monkeypatch):
    casos = dict(gfa.casos())
    assert set(casos) == set(GRAVADO) and len(GRAVADO) == 92
    for chave, caso in casos.items():
        assert gfa.impressao(*caso) == GRAVADO[chave], chave

    # a chave explicita desligada (os motores dos geradores com `cfg_fruta_ao_lado` desligada)
    def com_chave(base):
        class M(base):
            def __init__(self, *a, **kw):
                super().__init__(*a, cfg_fruta_ao_lado=CONFIG_FRUTA_AO_LADO, **kw)
        M.__name__ = M.__qualname__ = base.__name__        # a impressao do gabarito le o nome do motor
        return M
    monkeypatch.setattr(gq, "MotorMundo", com_chave(BASE_MUNDO))
    monkeypatch.setattr(gq, "MotorMundoCorpo", com_chave(BASE_CORPO))
    monkeypatch.setattr(gpl, "MotorMundoCorpo", com_chave(BASE_CORPO))
    for chave, caso in list(casos.items())[:84:7]:
        assert gfa.impressao(*caso) == GRAVADO[chave], chave


def test_sem_a_chave_nada_novo():
    m = MotorMundo(PoliticaInstintoMundo(CONFIG_PADRAO), CONFIG_PADRAO, 1, obediencia_desligada=True, cfg_mundo=CM)
    assert not m.cfal.ligada and not hasattr(m, "frutas_ao_lado")
    assert "fruta_ao_lado" not in m.estado() and "frutas_ao_lado" not in m.resumo_mundo_fisico()


# ================================================================== a mecanica
@pytest.mark.parametrize("dono_nome", ["atencioso", "relapso"])
def test_a_mecanica_numa_vida(dono_nome):
    for s in (101, 202, 303):
        v, dono, r = vida(s, dono_nome)
        m = v.motor
        assert m.frutas_ao_lado and r.depositos
        racoes = {d["id"]: d for d in m.deixadas if d["tipo"] == "racao"}
        assert len(r.depositos) == len(m.frutas_ao_lado)
        for f, dep in zip(m.frutas_ao_lado, r.depositos):
            # logo depois de uma racao do dono, no mesmo tick, na celula do tipo pela permutacao
            assert racoes[f["racao"]]["tick"] == f["tick"] and (f["x"], f["y"]) == r.celulas[f["tipo"]]
            assert (dep["tipo"], dep["x"], dep["y"]) == (f["tipo"], f["x"], f["y"])
            assert dep["racao"] == (racoes[f["racao"]]["x"], racoes[f["racao"]]["y"])
        # o teto e a reposicao: em cada passo com racao, o dono poe exatamente os tipos com menos de uma madura ao lado no chao
        com_racao = 0
        for tick, no_chao, n_racoes, postos in r.chamadas:
            if n_racoes:
                com_racao += 1
                assert postos == [f for f in LIGADA.tipos if no_chao[f] < LIGADA.teto_por_tipo]
            else:
                assert postos == []
            assert all(v_ <= LIGADA.teto_por_tipo for v_ in no_chao.values())
        assert com_racao == len(dono.lugares)
        if dono_nome == "atencioso":                     # o relapso volta tarde: as frutas ja foram comidas ou sumiram
            assert any(p == [] for _, _, n, p in r.chamadas if n)                  # ha passos com racao e o teto cheio
        # fora do orcamento: o canal fechou o orcamento de sempre, e as frutas nao contam como gesto do dono
        gestos = sum(1 for e in m.log if e.tipo in ("acao_usuario", "deixar_comida", "deixar_bola"))
        assert v.interacoes == 16 * DIAS == gestos
        assert sum(1 for e in m.log if e.tipo == "deixar_fruta") == len(m.frutas_ao_lado)
        # o consumo leva o tipo e a origem
        ao_lado = [c for c in m.consumos_mundo if c["origem"] == ORIGEM_AO_LADO]
        assert ao_lado and all(c["tipo"] in FRUTAS for c in ao_lado)
        ids = {f["id"] for f in m.frutas_ao_lado}
        assert all(c["id"] in ids for c in ao_lado)


def test_sem_contato():
    """a fruta ao lado nao conta como cuidado: o relogio do cuidado e o cerebro nao a veem"""
    vistos = []

    class Espiao(PoliticaInstintoMundo):
        def receber_acao_dono(self, acao, tick):
            vistos.append(acao)
    m = MotorMundo(Espiao(CONFIG_PADRAO), CONFIG_PADRAO, 101, obediencia_desligada=True, cfg_mundo=CM, cfg_fruta_ao_lado=LIGADA)
    m.avancar(30)
    m.deixar_comida("racao", *centro_da_celula(CM.layout.comedouro, CM))
    antes = (m._estado.ticks_desde_cuidado if hasattr(m._estado, "ticks_desde_cuidado") else None, len(vistos), m.estado())
    m.deixar_fruta("a", *centro_da_celula((11, 14), CM))
    depois = (m._estado.ticks_desde_cuidado if hasattr(m._estado, "ticks_desde_cuidado") else None, len(vistos), m.estado())
    assert antes[:2] == depois[:2]
    assert {k: v for k, v in antes[2].items() if k not in ("mundo", "fruta_ao_lado")} == \
        {k: v for k, v in depois[2].items() if k not in ("mundo", "fruta_ao_lado")}
    assert depois[2]["fruta_ao_lado"] == {"no_chao": {"a": 1, "b": 0, "c": 0}, "postas": 1}


def test_a_permutacao_uniforme_e_a_rng_propria():
    estado = random.getstate()
    cont = Counter()
    for s in range(600):
        r = DonoFrutaAoLado(DonoComLugar(criar_dono("atencioso"), "comedouro", s, "atencioso", CM), s, LIGADA, CM)
        ref = list(FRUTAS)
        random.Random(derivar_semente("fruta-ao-lado", s)).shuffle(ref)
        assert r.permutacao == ref
        cont[tuple(r.permutacao)] += 1
    assert random.getstate() == estado
    assert len(cont) == 6 and all(70 <= n <= 130 for n in cont.values()), cont


def test_com_o_corpo_e_o_paladar():
    """com o corpo quimico e o Paladar no mundo: a fruta ao lado e comida com o perfil do tipo no registro"""
    v, _, _ = vida(202, corpo=gq.CORPOS["quimica"], cpal=CONFIG_PALADAR_LIGADA, dias=3)
    ao_lado = [c for c in v.motor.consumos_mundo if c["origem"] == ORIGEM_AO_LADO]
    assert ao_lado and all(c["perfil"] == CONFIG_PALADAR_LIGADA.perfis[c["tipo"]] for c in ao_lado if c["situacao"] == "madura")


# ================================================================== G1
@pytest.mark.parametrize("corpo", [None, "quimica"])
def test_g1_o_replay_refaz_as_frutas_ao_lado(corpo):
    cc = None if corpo is None else gq.CORPOS[corpo]
    v, _, _ = vida(303, corpo=cc)
    fm = fabrica(LIGADA, cc)
    r = reproduzir_mundo(LogDeEventos.de_jsonl(v.motor.log.para_jsonl()), lambda cfg=None: PoliticaInstintoMundo(cfg or CONFIG_PADRAO),
                         CONFIG_PADRAO, 303, fabrica_motor=fm)
    assert r.frutas_ao_lado == v.motor.frutas_ao_lado
    assert gdp.impressao(r) == gdp.impressao(v.motor)
    if cc is not None:
        assert r.corpo.para_dict() == v.motor.corpo.para_dict()


# ================================================================== as recusas
def test_as_recusas():
    for estilo in ("perto", "longe"):
        with pytest.raises(ValueError, match="comedouro"):
            DonoFrutaAoLado(DonoComLugar(criar_dono("atencioso"), estilo, 1, "atencioso", CM), 1, LIGADA, CM)
    with pytest.raises(ValueError, match="desligada"):
        DonoFrutaAoLado(DonoComLugar(criar_dono("atencioso"), "comedouro", 1, "atencioso", CM), 1, CONFIG_FRUTA_AO_LADO, CM)
    with pytest.raises(ValueError, match="mundo fisico"):
        MotorMundo(PoliticaInstintoMundo(CONFIG_PADRAO), CONFIG_PADRAO, 1, obediencia_desligada=True, cfg_fruta_ao_lado=LIGADA)
    sem = MotorMundo(PoliticaInstintoMundo(CONFIG_PADRAO), CONFIG_PADRAO, 1, obediencia_desligada=True, cfg_mundo=CM)
    with pytest.raises(Exception, match="FrutaAoLado"):
        sem.deixar_fruta("a", 10, 10)
    com = MotorMundo(PoliticaInstintoMundo(CONFIG_PADRAO), CONFIG_PADRAO, 1, obediencia_desligada=True, cfg_mundo=CM,
                     cfg_fruta_ao_lado=LIGADA)
    with pytest.raises(ValueError, match="sem racao"):
        com.deixar_fruta("a", 10, 10)
    # a regra sem o estado da chave
    r = DonoFrutaAoLado(DonoComLugar(criar_dono("atencioso"), "comedouro", 1, "atencioso", CM), 1, LIGADA, CM)
    with pytest.raises(ValueError, match="fruta_ao_lado"):
        r.acoes(sem.estado())
    # no grupo, falha alto
    sementes = sementes_do_grupo(101, CONFIG_GRUPO_LIGADA.ids)
    pets = []
    for ident in ("A", "B"):
        fm = lambda p, cfg, s_, **kw: MotorMundo(p, cfg, s_, obediencia_desligada=True, cfg_mundo=CM,  # noqa: E731
                                                 cfg_fruta_ao_lado=LIGADA, **kw)
        d = DonoComLugar(criar_dono("atencioso"), "comedouro", sementes[ident], "atencioso", CM)
        pets.append(PetDoGrupo(ident, 0, lambda cfg=None: PoliticaInstintoMundo(cfg or CONFIG_PADRAO), fm, d, "atencioso", "instinto"))
    with pytest.raises(ValueError, match="fora do grupo"):
        simular_grupo(CM, 101, pets, 1)
