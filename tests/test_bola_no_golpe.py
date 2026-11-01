"""A bola no golpe (docs/TAREFA_V3_HABITAT_OBJETOS.md; os pets v15 do jogo web, a chave `bolaNoGolpe` de web/app/motor/mundo.ts): com a
`ConfigBolaNoGolpe` ligada, quando o pet brinca a bola sai na direcao em que ele vinha (de onde estava antes do passo ate ela), com a distancia sorteada de sempre. Desligada (o
padrao, a pesquisa), a vida de hoje.

- A chave nasce desligada, e ligada exige o mundo fisico.
- direcao_do_golpe: a das 16 mais alinhada; o empate vai a de menor indice; em cima da bola, None.
- Desligada explicita, a vida e a de hoje byte a byte (o resumo inteiro, o log e as rngs).
- Ligada, a mesma vida tem as mesmas distancias (o sorteio da direcao fica no fluxo `mundo-bola`) e a direcao do golpe em cada rolagem.
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

from digilab.config import (CONFIG_BOLA_NO_GOLPE, CONFIG_BOLA_NO_GOLPE_LIGADA, CONFIG_MUNDO_LIGADA, CONFIG_PADRAO,  # noqa: E402
                            ConfigBolaNoGolpe)
from digilab.events import AcaoPet  # noqa: E402
from digilab.mundo import DIR16, MotorMundo, direcao_do_golpe, fabricas_mundo  # noqa: E402
from digilab.policy import PoliticaInstinto  # noqa: E402

SEMENTES = (101, 202)                     # so dos testes


class Brincalhao:
    """Cerebro de teste: sempre brinca"""

    nome = "teste"

    def agir(self, obs, rng):
        return AcaoPet.BRINCAR

    def observar(self, transicao) -> None:
        pass

    def estado_interno(self) -> dict:
        return {"nome": self.nome}


def _vida(semente: int, **kw):
    """o pet que sempre brinca, com a bola deixada a dois passos dele a cada rodada: ele anda, chega e bate"""
    _, fm = fabricas_mundo(CONFIG_MUNDO_LIGADA, **kw)
    m = fm(Brincalhao(), CONFIG_PADRAO, semente)
    for i in range(30):
        x, y = m.pet
        m.deixar_bola(min(1023, max(0, x + (24, -24, 0, 0)[i % 4])), min(479, max(0, y + (0, 0, 24, -24)[i % 4])))
        m._estado = replace(m._estado, energia=1.0)
        m.avancar(15)
    return m


def _resumo(m) -> str:
    return json.dumps({"log": m.log.para_jsonl(), "estado": m.estado(), "estado_bruto": repr(m._estado),
                       "rng_ambiente": m._rng_ambiente.getstate(), "rng_politica": m._rng_politica.getstate(),
                       "mundo": m.resumo_mundo_fisico()}, sort_keys=True, default=str)


def test_a_chave_nasce_desligada_e_exige_o_mundo():
    assert CONFIG_BOLA_NO_GOLPE.ligada is False and CONFIG_BOLA_NO_GOLPE_LIGADA.ligada is True
    with pytest.raises(TypeError):
        ConfigBolaNoGolpe(ligada=1)
    with pytest.raises(ValueError, match="mundo fisico"):
        MotorMundo(PoliticaInstinto(CONFIG_PADRAO), CONFIG_PADRAO, 101, cfg_bola_golpe=CONFIG_BOLA_NO_GOLPE_LIGADA)
    with pytest.raises(TypeError):
        MotorMundo(PoliticaInstinto(CONFIG_PADRAO), CONFIG_PADRAO, 101, cfg_mundo=CONFIG_MUNDO_LIGADA, cfg_bola_golpe=True)


def test_a_direcao_do_golpe():
    assert direcao_do_golpe(0, 0, 0, 0) is None
    assert direcao_do_golpe(0, 0, 10, 0) == 0                      # leste
    assert direcao_do_golpe(0, 0, 0, -10) == 4                     # norte (y cresce para o sul)
    assert direcao_do_golpe(0, 0, -10, 0) == 8
    assert direcao_do_golpe(0, 0, 0, 10) == 12
    assert direcao_do_golpe(5, 5, 15, -5) == 2                     # nordeste
    for k, (cx, cy) in enumerate(DIR16):
        assert direcao_do_golpe(100, 100, 100 + cx, 100 + cy) == k


@pytest.mark.parametrize("semente", SEMENTES)
def test_desligada_e_a_vida_de_hoje(semente):
    assert _resumo(_vida(semente)) == _resumo(_vida(semente, cfg_bola_golpe=CONFIG_BOLA_NO_GOLPE))


@pytest.mark.parametrize("semente", SEMENTES)
def test_ligada_a_bola_sai_na_direcao_do_golpe(semente):
    hoje, golpe = _vida(semente), _vida(semente, cfg_bola_golpe=CONFIG_BOLA_NO_GOLPE_LIGADA)
    assert golpe.rolagens and len(golpe.rolagens) == len(hoje.rolagens)
    for r, h in zip(golpe.rolagens, hoje.rolagens):
        assert r["celulas"] == h["celulas"] and r["tick"] == h["tick"]
    # onde o pet estava antes de cada decisao: o x, y da anterior (so a decisao o move), e o ninho na primeira
    antes, batidas = golpe.mundo.ninho, []
    for d in golpe.decisoes_mundo:
        if d["brincou_com_bola"]:
            batidas.append(antes)
        antes = (d["x"], d["y"])
    assert len(batidas) == len(golpe.rolagens)
    ao_lado = 0
    for (x0, y0), r in zip(batidas, golpe.rolagens):
        esperada = direcao_do_golpe(x0, y0, *r["de"])
        if esperada is not None:
            assert r["direcao"] == esperada
            ao_lado += 1
    assert ao_lado > 0
