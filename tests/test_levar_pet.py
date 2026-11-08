"""O levar pet (docs/TAREFA_V3_PEGAR_PET.md, P1; os pets v19 do jogo web): o dono pega o pet e o solta noutro lugar do mapa. O espelho
do web/app/test/levar_pet.test.ts.

- O formato do log (events.levar_pet, ler_levar_pet): o ponto solto e inteiro e com sinal, so na forma canonica.
- So a posicao muda (PP-1): o estado, o corpo e o cerebro nao recebem nada; o pendente se perde.
- Fora do mapa, o pet cai na borda mais proxima (PP-4); o log guarda o ponto pedido.
- O pet dormindo nao e pego (PP-2): falha alto antes do log.
- Sem o mundo, falha alto; o replay (reproduzir_mundo) refaz a vida byte a byte.
- Sem levadas, o resumo do mundo nao ganha chave nova (a vida de hoje).
- O gabarito do G-PAR do TS (web/app/test/gabaritos/levar_pet_python.json) esta em dia byte a byte.
Sementes: so as dos testes.
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
import exportar_gabarito_levar_pet as G  # noqa: E402

from digilab.config import CONFIG_MUNDO_MVP, CONFIG_PADRAO  # noqa: E402
from digilab.events import Evento, ler_levar_pet, levar_pet  # noqa: E402
from digilab.mundo import MotorMundo, MundoSemChave, fabricas_mundo, no_mapa, reproduzir_mundo  # noqa: E402
from digilab.policy import PoliticaInstinto  # noqa: E402

TEXTO = G.ARQUIVO.read_text(encoding="utf-8")
GRAVADO = json.loads(TEXTO)
CM = CONFIG_MUNDO_MVP
SEMENTES = (101, 202)                     # so dos testes


class Espiao:
    """O instinto com os ganchos do dono contados: o levar pet nao chama nenhum"""

    def __init__(self, cfg=None):
        self._p = PoliticaInstinto(cfg or CONFIG_PADRAO)
        self.chamadas: list[str] = []
        self.nome = "espiao"

    def agir(self, obs, rng):
        return self._p.agir(obs, rng)

    def observar(self, transicao) -> None:
        self._p.observar(transicao)

    def estado_interno(self) -> dict:
        return {"nome": self.nome}

    def receber_acao_dono(self, *a, **k) -> None:
        self.chamadas.append("receber_acao_dono")

    def consequencia_mundo(self, *a, **k) -> None:
        self.chamadas.append("consequencia_mundo")


def _motor(semente: int):
    fp, fm = fabricas_mundo(CM, politica_fabrica=lambda cfg=None: Espiao(cfg))
    return fp, fm, fm(fp(CONFIG_PADRAO), CONFIG_PADRAO, semente)


def _acordado(m) -> None:
    m.avancar(120)
    for _ in range(300):
        if not m._estado.dormindo:
            return
        m.avancar(7)
    raise RuntimeError("o pet nao acordou")


def _resumo(m) -> str:
    return json.dumps({"log": m.log.para_jsonl(), "estado": m.estado(), "estado_bruto": repr(m._estado),
                       "rng_ambiente": m._rng_ambiente.getstate(), "rng_politica": m._rng_politica.getstate(),
                       "mundo": m.resumo_mundo_fisico()}, sort_keys=True, default=str)


def test_o_formato_do_log():
    assert levar_pet(9, 10, 20) == Evento(9, "levar_pet", "10|20")
    assert levar_pet(9, -40, 99999).valor == "-40|99999"
    assert levar_pet(9, 2 ** 53 - 1, -(2 ** 53 - 1)).valor == f"{2 ** 53 - 1}|{-(2 ** 53 - 1)}"
    for x, y in ((1.5, 0), (0, float("nan")), ("1", 0), (True, 0), (2 ** 53, 0), (0, -(2 ** 53))):
        with pytest.raises(ValueError, match="levar_pet"):
            levar_pet(9, x, y)
    assert ler_levar_pet(Evento(0, "levar_pet", "-40|7")) == (-40, 7)
    assert ler_levar_pet(Evento(0, "levar_pet", "0|0")) == (0, 0)
    for v in ("07|1", "-0|1", "+1|1", "1.0|1", "1|", "|1", "1|2|3", "a|1", " 1|1", "1|1 ", "--1|1", "9007199254740992|0", "١|1"):
        with pytest.raises(ValueError):
            ler_levar_pet(Evento(0, "levar_pet", v))
    with pytest.raises(ValueError, match="nao e levar_pet"):
        ler_levar_pet(Evento(0, "deixar_bola", "1|1"))


def test_sem_o_mundo_falha_alto():
    m = MotorMundo(PoliticaInstinto(CONFIG_PADRAO), CONFIG_PADRAO, 101)
    with pytest.raises(MundoSemChave):
        m.levar_pet(10, 10)
    assert len(m.log) == 0


@pytest.mark.parametrize("semente", SEMENTES)
def test_so_a_posicao_muda(semente):
    _, _, m = _motor(semente)
    _acordado(m)
    estado, n, chamadas, n_eventos = m._estado, len(m.log), list(m.politica.chamadas), m._n_eventos
    decisoes = len(m.decisoes_mundo)
    m.levar_pet(321, 123)
    assert m.pet == (321, 123)
    assert m.resumo_mundo_fisico()["pendente"] is None
    assert [e.para_dict() for e in list(m.log)[n:]] == [levar_pet(estado.tick, 321, 123).para_dict()]
    assert m._estado == estado                        # o estado do pet (humor, fome, cuidado) nao muda
    assert m.politica.chamadas == chamadas            # nenhum gancho do cerebro
    assert len(m.decisoes_mundo) == decisoes
    assert m._n_eventos == n_eventos + 1              # e um evento do log, como o deixar_bola, mas nao e contato
    assert m.levadas[-1]["pedido"] == [321, 123] and m.levadas[-1]["para"] == [321, 123]


def test_fora_do_mapa_cai_na_borda():
    _, _, m = _motor(101)
    _acordado(m)
    assert (CM.celulas_x * CM.sub - 1, CM.celulas_y * CM.sub - 1) == (1023, 479)
    for x, y, px, py in ((-50, 9000, 0, 479), (5000, -3, 1023, 0), (-1, 240, 0, 240), (1024, 480, 1023, 479), (0, 0, 0, 0)):
        m.levar_pet(x, y)
        assert m.pet == (px, py) == no_mapa(x, y, CM)
        assert list(m.log)[-1] == levar_pet(m._estado.tick, x, y)


def test_dormindo_nao_e_pego():
    _, _, m = _motor(101)
    _acordado(m)
    m._estado = replace(m._estado, dormindo=True)
    n, antes = len(m.log), _resumo(m)
    with pytest.raises(RuntimeError, match="dormindo"):
        m.levar_pet(10, 10)
    assert len(m.log) == n and _resumo(m) == antes


@pytest.mark.parametrize("semente", SEMENTES)
def test_o_replay_refaz_a_vida(semente):
    fp, fm, m = _motor(semente)
    _acordado(m)
    for x, y in ((100, 100), (-20, 300), (900, 9999), (512, 240)):
        if not m._estado.dormindo:
            m.levar_pet(x, y)
        m.avancar(45)
    assert any(e.tipo == "levar_pet" for e in m.log)
    r = reproduzir_mundo(m.log, fp, CONFIG_PADRAO, semente, fabrica_motor=fm)
    assert _resumo(r) == _resumo(m)


def test_sem_levadas_o_resumo_e_o_de_hoje():
    _, _, m = _motor(101)
    m.avancar(200)
    assert "levadas" not in m.resumo_mundo_fisico()


def test_o_gabarito_esta_em_dia_byte_a_byte():
    assert TEXTO == json.dumps(G.gerar(), sort_keys=True, separators=(",", ":")) + "\n"
    assert all(v["semente"] in bv.SEMENTES_TESTE for v in GRAVADO["vidas"])
    for v in GRAVADO["vidas"]:
        levadas = v["resumo"]["levadas"]
        assert len(levadas) == v["levadas"] and v["dormindo_em"]
        assert all(lv["para"] == list(no_mapa(*lv["pedido"], CM)) for lv in levadas)
        assert any(lv["para"] != lv["pedido"] for lv in levadas)
