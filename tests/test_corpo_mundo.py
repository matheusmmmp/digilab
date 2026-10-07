"""Os estimulos do mundo fisico no corpo (CORPO-MUNDO; docs/TAREFA_V2_CORPO_DRIVES.md, secoes 4 e 5, para o A ligar o MotorMundo no
MotorCorpo): o andar, as comidas do mapa (a racao deixada, a fruta madura e a podre) e a MF-2. Cada um com o G-HOJE contra o float de hoje
do digilab/mundo.py: o mesmo estado de partida, o mesmo estimulo, e os drives lidos da quimica a ate 1e-9 do que o mundo escreve.

Duas conferencias: (1) uma grade de estados com cada comida, pelo proprio MotorMundo._comer_mundo; (2) vidas do mundo, decisao a decisao: o
Estado na decisao, a acao do pet com a MF-2, o andar e o que comeu, contra o Estado que o mundo deixa depois da consequencia. Sem o motor
do corpo (o MotorCorpo com o mundo e do A). So as sementes dos testes.
"""
from __future__ import annotations

import random
import sys
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab.config import CONFIG_MUNDO_LIGADA, CONFIG_PADRAO, ConfigCorpo  # noqa: E402
from digilab.corpo import Corpo, taxas_de  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.events import FRUTAS, TIPOS_COMIDA_MUNDO, AcaoPet, AcaoUsuario  # noqa: E402
from digilab.instinto_mundo import PoliticaInstintoMundo  # noqa: E402
from digilab.mundo import ESTILOS_LUGAR, DonoComLugar, MotorMundo, simular_vida_mundo  # noqa: E402
from digilab.state import Estado  # noqa: E402
from digilab.temperamento import NEUTRO  # noqa: E402

CM = CONFIG_MUNDO_LIGADA
CFG = CONFIG_PADRAO
CC = ConfigCorpo(ligada=True)
CC_DIGESTAO = ConfigCorpo(ligada=True, digestao=True)
C = CC.escala
EFEITO = {"a": -0.10, "b": 0.0, "c": 0.10}          # uma fruta que faz mal, uma neutra, uma que faz bem (os efeitos do N4)
DRIVES = ("fome", "higiene", "energia", "humor", "saude")
TOL = 1e-9
SEMENTES = (101, 202)                                # so dos testes


def _drives(e: Estado) -> dict[str, float]:
    return {d: getattr(e, d) for d in DRIVES}


def _confere(corpo: Corpo, esperado: Estado, contexto) -> None:
    lido = corpo.drives()
    for d in DRIVES:
        assert abs(lido[d] - getattr(esperado, d)) <= TOL, (contexto, d, lido[d], getattr(esperado, d))


# ------------------------------------------------------------------ as conversoes
def test_os_numeros_do_mundo_na_grade_de_c():
    c = Corpo.de_estado(Estado(energia=0.5), CFG, CC)
    c.estimulo_andar(60, CM.custo_energia_por_subunidade)
    assert c.q["cansaco"] == C // 2 + 75 * 60                    # o andar: 75 por subunidade (1/6000 x 450000)
    c2 = Corpo.de_estado(Estado(fome=0.4, humor=0.5), CFG, CC)
    c2.estimulo_consumo_mundo("a", "madura", CM, -0.10)
    assert c2.q["fome"] == 270000 - 67500 and c2.q["tristeza"] == 225000 + 45000   # fruta madura: 67500 e o efeito
    c3 = Corpo.de_estado(Estado(fome=0.4, humor=0.5), CFG, CC)
    c3.estimulo_consumo_mundo("racao", "madura", CM)
    assert c3.q["fome"] == 270000 - 202500 == 270000 + taxas_de(CFG, CC).dono[AcaoUsuario.ALIMENTAR]["fome"]  # a do alimentar
    c4 = Corpo.de_estado(Estado(fome=0.4, humor=0.5), CFG, CC)
    c4.estimulo_consumo_mundo("b", "podre", CM)
    assert c4.q["fome"] == 270000 and c4.q["tristeza"] == 225000 + 45000          # a podre: so o humor
    c5 = Corpo.de_estado(Estado(fome=0.4), CFG, CC)
    c5.acao_pet(AcaoPet.COMER, com_mundo=True)
    assert c5.q["fome"] == 270000                                                   # MF-2: comer sem comida nao da fome
    c5.acao_pet(AcaoPet.COMER)
    assert c5.q["fome"] == 270000 - 22500                                           # fora do mundo, o comer de hoje


def test_estimulos_do_mundo_falham_alto_fora_da_grade_e_do_catalogo():
    c = Corpo.de_estado(Estado(), CFG, CC)
    with pytest.raises(ValueError, match="grade"):
        c.estimulo_andar(10, 1.0 / 7000.0)
    with pytest.raises(ValueError, match="deslocamento"):
        c.estimulo_andar(-1, CM.custo_energia_por_subunidade)
    with pytest.raises(ValueError, match="deslocamento"):
        c.estimulo_andar(1.5, CM.custo_energia_por_subunidade)
    with pytest.raises(ValueError, match="desconhecida"):
        c.estimulo_consumo_mundo("bola", "madura", CM)
    with pytest.raises(ValueError, match="situacao"):
        c.estimulo_consumo_mundo("a", "sumida", CM)


# ------------------------------------------------------------------ (1) a grade, pelo _comer_mundo do proprio mundo
def _motor() -> MotorMundo:
    return MotorMundo(PoliticaInstintoMundo(CFG), CFG, 101, NEUTRO, "brasa", obediencia_desligada=True, cfg_mundo=CM,
                      efeito_frutas=EFEITO)


def _estados() -> list[Estado]:
    rng = random.Random(20261007)                    # so para sortear a grade (nao e semente de vida)
    fixos = [Estado(fome=1.0, humor=1.0), Estado(fome=0.0, humor=0.0), Estado(fome=0.9, humor=0.95), Estado(fome=0.2, humor=0.05)]
    sorteados = [Estado(fome=rng.randrange(C + 1) / C, humor=rng.randrange(C + 1) / C, energia=rng.randrange(C + 1) / C)
                 for _ in range(40)]
    return fixos + sorteados


@pytest.mark.parametrize("cc", [CC, CC_DIGESTAO], ids=["quimica", "digestao"])
@pytest.mark.parametrize("tipo", TIPOS_COMIDA_MUNDO)
@pytest.mark.parametrize("situacao", ["madura", "podre"])
def test_g_hoje_cada_comida_contra_o_comer_do_mundo(cc, tipo, situacao):
    m = _motor()
    tick = 3000
    for e in _estados():
        posta = tick if situacao == "madura" else tick - m._prazo_maduro(tipo) - 10
        comida = m._nova_comida(tipo, 100, 100, posta, "dono")
        assert m.situacao(comida, tick) == situacao
        m._estado = replace(e, tick=tick)
        m._comer_mundo(comida["id"], "comer", tick)                  # o float de hoje
        corpo = Corpo.de_estado(replace(e, tick=tick), CFG, cc)
        corpo.estimulo_consumo_mundo(tipo, situacao, CM, EFEITO.get(tipo, 0.0))
        _confere(corpo, m._estado, (tipo, situacao, e))


@pytest.mark.parametrize("deslocamento", [0, 1, 37, 60, 128, 600])
def test_g_hoje_o_andar_contra_o_mundo(deslocamento):
    """a conta do mundo: energia = max(0, energia - custo x deslocamento), em float"""
    for e in _estados():
        esperado = max(0.0, e.energia - CM.custo_energia_por_subunidade * deslocamento)
        corpo = Corpo.de_estado(e, CFG, CC)
        corpo.estimulo_andar(deslocamento, CM.custo_energia_por_subunidade)
        assert abs(corpo.drives()["energia"] - esperado) <= TOL


# ------------------------------------------------------------------ (2) as vidas, decisao a decisao
class _MotorEspiao(MotorMundo):
    """o MotorMundo de hoje, guardando o Estado na decisao (antes do efeito da acao do pet) e o Estado depois da consequencia"""

    def __init__(self, *a, **kw) -> None:
        super().__init__(*a, **kw)
        self.pares: list[tuple] = []

    def _antes_da_decisao(self):
        p = super()._antes_da_decisao()
        self._estado_na_decisao = self._estado
        return p

    def _consequencia(self, acao):
        ocorrido = super()._consequencia(acao)
        self.pares.append((self._estado_na_decisao, acao, ocorrido, self._estado))
        return ocorrido


class _ComePodre(PoliticaInstintoMundo):
    """o instinto do mundo que, no comer, vai a uma comida podre quando ve uma (o padrao do motor nunca vai)"""

    def escolher_alvo(self, acao, candidatos, percepcao, u):
        if acao is not AcaoPet.COMER:
            return None
        podres = {i for i, tipo, *_ in percepcao.vistos if tipo.endswith("_podre")}
        return next((a for a in candidatos if a.tipo == "comida" and a.id in podres), None)


def _vida(politica, dono: str, estilo: str, semente: int, dias: int = 4, cm=CM) -> _MotorEspiao:
    fm = (lambda pol, cfg, s: _MotorEspiao(pol, cfg, s, NEUTRO, "brasa", obediencia_desligada=True, cfg_mundo=cm,  # noqa: E731
                                           efeito_frutas=EFEITO))
    lugar = DonoComLugar(criar_dono(dono), estilo, semente, dono, cm)
    return simular_vida_mundo(dono, lugar, politica, semente, dias, 16 * dias, fm, rotulo_dono=dono).motor


def _corpo_da_decisao(cc, antes: Estado, acao: AcaoPet, ocorrido: dict | None, motor: MotorMundo) -> Corpo:
    corpo = Corpo.de_estado(antes, CFG, cc)
    corpo.acao_pet(acao, com_mundo=True)
    if ocorrido is not None:
        corpo.estimulo_andar(ocorrido["deslocamento"], motor.cmf.custo_energia_por_subunidade)
        comeu = ocorrido["comeu"]
        if comeu is not None:
            corpo.estimulo_consumo_mundo(comeu["tipo"], comeu["situacao"], motor.cmf, motor.efeito_frutas.get(comeu["tipo"], 0.0))
        if ocorrido["brincou_com_bola"]:
            corpo.estimulo_bola(motor.cmf.ganho_humor_bola)            # a bola do mundo: o estimulo da bola de sempre (A1)
    return corpo


@pytest.mark.parametrize("cc", [CC, CC_DIGESTAO], ids=["quimica", "digestao"])
def test_g_hoje_as_vidas_decisao_a_decisao(cc):
    cobertura = {"andou": 0, "racao": 0, "fruta_madura": 0, "podre": 0, "achou": 0, "comer_sem_comida": 0, "brincou": 0}
    cm = replace(CM, mult_queda=2.0)                 # mais frutas no chao: mais fruta madura e mais podre
    for semente in SEMENTES:
        for dono in ("atencioso", "relapso", "aleatorio"):
            for estilo in ESTILOS_LUGAR:
                for politica in (PoliticaInstintoMundo(CFG), _ComePodre(CFG)):
                    m = _vida(politica, dono, estilo, semente, cm=cm)
                    for antes, acao, ocorrido, depois in m.pares:
                        corpo = _corpo_da_decisao(cc, antes, acao, ocorrido, m)
                        _confere(corpo, depois, (dono, estilo, semente, acao, ocorrido))
                        if ocorrido is None:
                            continue
                        cobertura["andou"] += ocorrido["deslocamento"] > 0
                        cobertura["brincou"] += ocorrido["brincou_com_bola"]
                        comeu = ocorrido["comeu"]
                        if comeu is None:
                            cobertura["comer_sem_comida"] += acao is AcaoPet.COMER
                        elif comeu["situacao"] == "podre":
                            cobertura["podre"] += 1
                        else:
                            cobertura["racao" if comeu["tipo"] == "racao" else "fruta_madura"] += 1
                            cobertura["achou"] += comeu["como"] == "achou"
    assert all(v > 0 for v in cobertura.values()), cobertura


def test_o_humor_da_fruta_em_vida_e_dos_tres_tipos():
    """a vida do teste come as tres frutas, com o efeito de cada uma (a que faz mal, a neutra e a que faz bem)"""
    m = _vida(PoliticaInstintoMundo(CFG), "atencioso", "perto", 101, dias=6, cm=replace(CM, mult_queda=2.0))
    comidas = {c["tipo"] for c in m.consumos_mundo if c["situacao"] == "madura"}
    assert set(FRUTAS) <= comidas
