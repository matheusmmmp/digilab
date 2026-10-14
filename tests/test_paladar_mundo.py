"""O Paladar, o lado do mundo (docs/futuro/paladar.md, secoes 3.1, 4 e 6, etapa 1, do A; PL-1 a PL-9 pela recomendacao).

- A `ConfigPaladar`: os perfis do desenho (a forma girada das frutas, o salgado da racao), o registro de status e as falhas altas.
- G2: desligado, as 84 vidas de tests/gabaritos/paladar_mundo_vidas_de_hoje.json (gravado antes, tests/gabarito_paladar_mundo.py) byte a
  byte, sem a chave e com a chave explicita desligada.
- Ligado, o mundo nao usa o perfil: a vida e a mesma (log, estado, acoes, rngs, percepcao, quedas), e o registro do consumo so ganha o
  `perfil` (o do tipo na comida madura, None na podre), no `comer`, no "achou e comeu" e na fruta na mao; o `ocorrido["comeu"]` e o mesmo
  registro. O perfil e uma copia.
- G1: o replay refaz os registros com o perfil. No grupo, os pets tem o mesmo Paladar.
Sementes: so as dos testes.
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
import sys
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import gabarito_dois_pets as gdp  # noqa: E402
import gabarito_paladar_mundo as gpm  # noqa: E402
import gabarito_pet_que_pensa_plano as gpl  # noqa: E402
import gabarito_pqp_mundo as gq  # noqa: E402

import digilab.mundo as mundo  # noqa: E402
from digilab.config import (CONFIG_CORPO, CONFIG_GRUPO_LIGADA, CONFIG_PADRAO, CONFIG_PALADAR, CONFIG_PALADAR_LIGADA,  # noqa: E402
                            QUALIDADES_PALADAR, TICKS_POR_DIA, ConfigPaladar)
from digilab.donos import criar_dono  # noqa: E402
from digilab.events import LogDeEventos  # noqa: E402
from digilab.grupo import PetDoGrupo, sementes_do_grupo, simular_grupo  # noqa: E402
from digilab.instinto_mundo import PoliticaInstintoMundo  # noqa: E402
from digilab.mundo import DonoComLugar, MotorMundo, reproduzir_mundo  # noqa: E402

C = CONFIG_CORPO.escala
GRAVADO = json.loads(gpm.ARQUIVO.read_text(encoding="utf-8"))
BASE_MUNDO, BASE_CORPO = gq.MotorMundo, gq.MotorMundoCorpo     # os motores dos geradores, antes de qualquer troca
assert gpl.MotorMundoCorpo is BASE_CORPO


class _ComPaladar:
    """troca o MotorMundo dos geradores pelo mesmo com `cfg_paladar` (e grava o motor e os ocorridos)"""

    def __init__(self, monkeypatch, cpal) -> None:
        self.cpal, self.motores, self.ocorridos = cpal, [], []
        base_mundo, base_corpo = BASE_MUNDO, BASE_CORPO
        dono = self

        def fabrica(base):
            class M(base):
                def __init__(self, *a, **kw):
                    super().__init__(*a, cfg_paladar=dono.cpal, **kw)
                    dono.motores.append(self)

                def _consequencia(self, acao):
                    oc = super()._consequencia(acao)
                    if oc is not None and oc.get("comeu") is not None:
                        dono.ocorridos.append(oc)
                    return oc
            M.__name__ = M.__qualname__ = base.__name__      # a impressao do gabarito le o nome do motor
            return M
        monkeypatch.setattr(gq, "MotorMundo", fabrica(base_mundo))
        monkeypatch.setattr(gq, "MotorMundoCorpo", fabrica(base_corpo))
        monkeypatch.setattr(gpl, "MotorMundoCorpo", fabrica(base_corpo))


def _vida(fonte, caso):
    if fonte == "mundo":
        return gq.vida(*caso).motor
    m, _, _ = gpl.vida(*caso)
    return m


def _sem_perfil(consumos: list[dict]) -> list[dict]:
    return [{k: v for k, v in c.items() if k != "perfil"} for c in consumos]


def _impressao_sem_perfil(m) -> dict:
    """a impressao do gabarito com os consumos sem o perfil (o resto do registro do mundo fisico inteiro)"""
    d = gdp.impressao(m)
    r = m.resumo_mundo_fisico()
    r["consumos"] = _sem_perfil(r["consumos"])
    d["fisico"] = hashlib.sha256(json.dumps(r, sort_keys=True, default=repr).encode()).hexdigest()
    return d


# ================================================================== a config
def test_os_perfis_do_desenho():
    p = CONFIG_PALADAR.perfis
    q1, q3 = C // 4, 3 * C // 4
    assert QUALIDADES_PALADAR == ("doce", "azedo", "amargo", "salgado")
    assert p["racao"] == {"doce": 0, "azedo": 0, "amargo": 0, "salgado": q1}
    assert p["a"] == {"doce": q3, "azedo": q1, "amargo": 0, "salgado": 0}
    # as tres frutas sao a mesma forma girada nas tres primeiras qualidades, sem salgado
    for k, f in enumerate(("a", "b", "c")):
        giro = [p["a"][QUALIDADES_PALADAR[(j - k) % 3]] for j in range(3)]
        assert [p[f][q] for q in QUALIDADES_PALADAR[:3]] == giro and p[f]["salgado"] == 0
    assert not CONFIG_PALADAR.ligada and CONFIG_PALADAR_LIGADA.ligada and CONFIG_PALADAR_LIGADA.perfis == p


def test_o_registro_de_status_cobre_os_campos():
    assert set(mundo.PARAMETROS_PALADAR_MUNDO) == {f.name for f in dataclasses.fields(ConfigPaladar)}
    assert all(s == "PROPOSTO" for s, _ in mundo.PARAMETROS_PALADAR_MUNDO.values())


def test_as_falhas_altas_da_config():
    bom = CONFIG_PALADAR.perfis
    with pytest.raises(TypeError):
        ConfigPaladar(ligada=1)
    with pytest.raises(ValueError, match="um perfil por tipo"):
        ConfigPaladar(perfis={k: v for k, v in bom.items() if k != "c"})
    with pytest.raises(ValueError, match="qualidades"):
        ConfigPaladar(perfis={**bom, "a": {"doce": 1}})
    for ruim in (-1, C + 1, 1.0):
        with pytest.raises(ValueError, match="fora de inteiros"):
            ConfigPaladar(perfis={**bom, "b": {**bom["b"], "amargo": ruim}})
    ConfigPaladar(perfis={**bom, "b": {**bom["b"], "amargo": C}})


def test_o_paladar_exige_o_mundo():
    with pytest.raises(ValueError, match="mundo fisico"):
        MotorMundo(PoliticaInstintoMundo(CONFIG_PADRAO), CONFIG_PADRAO, 1, obediencia_desligada=True, cfg_paladar=CONFIG_PALADAR_LIGADA)
    with pytest.raises(TypeError, match="ConfigPaladar"):
        MotorMundo(PoliticaInstintoMundo(CONFIG_PADRAO), CONFIG_PADRAO, 1, obediencia_desligada=True, cfg_mundo=gq.LAYOUTS["padrao"],
                   cfg_paladar={"ligada": True})
    m = MotorMundo(PoliticaInstintoMundo(CONFIG_PADRAO), CONFIG_PADRAO, 1, obediencia_desligada=True, cfg_mundo=gq.LAYOUTS["padrao"])
    with pytest.raises(ValueError, match="sem o Paladar"):
        m.perfil_de("a")


# ================================================================== G2
def test_g2_desligado_as_vidas_de_hoje(monkeypatch):
    """sem a chave e com a chave explicita desligada: as 84 vidas byte a byte"""
    casos = dict(gpm.casos())
    assert set(casos) == set(GRAVADO) and len(GRAVADO) == 84
    for chave, caso in casos.items():
        assert gpm.impressao(*caso) == GRAVADO[chave], chave
    _ComPaladar(monkeypatch, CONFIG_PALADAR)
    for chave, caso in list(casos.items())[::6]:
        assert gpm.impressao(*caso) == GRAVADO[chave], chave


# ================================================================== ligado: so o registro ganha o perfil
def test_ligado_a_vida_e_a_mesma_e_o_consumo_leva_o_perfil(monkeypatch):
    sem = {chave: _impressao_sem_perfil(_vida(*caso)) for chave, caso in gpm.casos()}
    sem_consumos = {}
    for chave, caso in gpm.casos():
        sem_consumos[chave] = _vida(*caso).consumos_mundo
    pal = _ComPaladar(monkeypatch, CONFIG_PALADAR_LIGADA)
    como = {"comer": 0, "achou": 0, "mao": 0}
    podres = 0
    for chave, caso in gpm.casos():
        m = _vida(*caso)
        assert m.cpal.ligada
        assert _impressao_sem_perfil(m) == sem[chave], chave                  # o mundo nao usa o perfil
        assert _sem_perfil(m.consumos_mundo) == sem_consumos[chave]
        for c in m.consumos_mundo:
            assert "perfil" in c
            if c["situacao"] == "madura":
                assert c["perfil"] == CONFIG_PALADAR.perfis[c["tipo"]] and c["perfil"] is not CONFIG_PALADAR.perfis[c["tipo"]]
            else:
                assert c["situacao"] == "podre" and c["perfil"] is None
                podres += 1
            como[c["como"]] += 1
    assert all(como.values()), como                                           # o comer, o achou e comeu e a fruta na mao
    # o ocorrido do comer e do achou e comeu e o proprio registro (o corpo do B le o perfil dali)
    assert pal.ocorridos
    for oc in pal.ocorridos:
        reg = oc["comeu"]
        m = next(mm for mm in pal.motores if any(r is reg for r in mm.consumos_mundo))
        assert reg["perfil"] == (m.perfil_de(reg["tipo"]) if reg["situacao"] == "madura" else None)
    del podres


def test_o_perfil_e_uma_copia():
    m = MotorMundo(PoliticaInstintoMundo(CONFIG_PADRAO), CONFIG_PADRAO, 1, obediencia_desligada=True, cfg_mundo=gq.LAYOUTS["padrao"],
                   cfg_paladar=CONFIG_PALADAR_LIGADA)
    p = m.perfil_de("racao")
    p["salgado"] = 0
    assert CONFIG_PALADAR_LIGADA.perfis["racao"]["salgado"] == C // 4 == m.perfil_de("racao")["salgado"]
    with pytest.raises(KeyError):
        m.perfil_de("bola")


def test_outros_perfis_so_mudam_o_registro(monkeypatch):
    """um perfil diferente nao muda nada do mundo: so o que vai no registro"""
    outro = ConfigPaladar(ligada=True, perfis={t: {q: C for q in QUALIDADES_PALADAR} for t in ("racao", "a", "b", "c")})
    caso = next(c for k, c in gpm.casos() if k.startswith("j5|"))
    _ComPaladar(monkeypatch, CONFIG_PALADAR_LIGADA)
    a = _vida(*caso)
    _ComPaladar(monkeypatch, outro)
    b = _vida(*caso)
    assert _impressao_sem_perfil(a) == _impressao_sem_perfil(b)
    assert all(c["perfil"] in (None, {q: C for q in QUALIDADES_PALADAR}) for c in b.consumos_mundo)


# ================================================================== G1
@pytest.mark.parametrize("cerebro", ["instinto", "P1-alvo"])
def test_g1_o_replay_refaz_o_perfil(monkeypatch, cerebro):
    _ComPaladar(monkeypatch, CONFIG_PALADAR_LIGADA)
    for corpo in ("sem", "quimica"):
        caso = ("padrao", corpo, cerebro, "longe", 202)
        v = gq.vida(*caso)
        fp, fm = gq.fabricas("padrao", corpo, cerebro, gq.x_do_caso("longe", 202))
        r = reproduzir_mundo(LogDeEventos.de_jsonl(v.motor.log.para_jsonl()), fp, CONFIG_PADRAO, 202, fabrica_motor=fm)
        assert r.cpal.ligada and r.consumos_mundo == v.motor.consumos_mundo
        assert gdp.impressao(r) == gdp.impressao(v.motor)


# ================================================================== o grupo
def _pets(s, cpal_b):
    cm = gq.LAYOUTS["padrao"]
    sementes = sementes_do_grupo(s, CONFIG_GRUPO_LIGADA.ids)
    pets = []
    for ident, cpal in (("A", CONFIG_PALADAR_LIGADA), ("B", cpal_b)):
        fp = lambda cfg=None: PoliticaInstintoMundo(cfg or CONFIG_PADRAO)  # noqa: E731
        fm = lambda p, cfg, s_, cpal=cpal, **kw: MotorMundo(p, cfg, s_, obediencia_desligada=True, cfg_mundo=cm,  # noqa: E731
                                                             cfg_paladar=cpal, **kw)
        d = DonoComLugar(criar_dono("atencioso"), "perto", sementes[ident], "atencioso", cm)
        pets.append(PetDoGrupo(ident, 0 if ident == "A" else TICKS_POR_DIA, fp, fm, d, "atencioso", "instinto"))
    return pets


def test_no_grupo_o_mesmo_paladar_em_todos_os_pets():
    g = simular_grupo(gq.LAYOUTS["padrao"], 101, _pets(101, CONFIG_PALADAR_LIGADA), 2)
    regs = [c for m in g.motores.values() for c in m.consumos_mundo]
    assert regs and all("perfil" in c for c in regs)
    with pytest.raises(ValueError, match="Paladar diferente"):
        simular_grupo(gq.LAYOUTS["padrao"], 101, _pets(101, CONFIG_PALADAR), 2)
    with pytest.raises(ValueError, match="Paladar diferente"):
        simular_grupo(gq.LAYOUTS["padrao"], 101, _pets(101, replace(CONFIG_PALADAR_LIGADA, perfis={
            **CONFIG_PALADAR.perfis, "racao": {q: 0 for q in QUALIDADES_PALADAR}})), 2)
