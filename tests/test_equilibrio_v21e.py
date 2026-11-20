"""Rodada de equilibrio geral, fase 1 (docs/EQUILIBRIO_GERAL.md): chaves da ConfigCombateV21E.

Desligadas, tudo reproduz a V21D (classe e hash das configs V21D gravadas, listas, partidas); ligadas (o config
experiments/configs/v21e/calibracao.json), so as listas do duelista, do tita, do espelho e da muralha mudam, cada uma com a
edicao declarada. A base V2C nao muda.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "experiments"))

import run_bateria_v21 as rb  # noqa: E402
from digilab.combate_v2.v21 import bots  # noqa: E402
from digilab.combate_v2.v21.bots import ADULTOS, FORMAS, SOMBRIOS, gambits_adulto, lutador_adulto  # noqa: E402
from digilab.combate_v2.v21.partida import jogar  # noqa: E402
from digilab.combate_v2.v21.regras import Acao  # noqa: E402
from digilab.config import ConfigCombateV21C, ConfigCombateV21D, ConfigCombateV21E  # noqa: E402

CFG_V21C = RAIZ / "experiments" / "configs" / "v21c" / "validacao.json"
CFG_V21D = RAIZ / "experiments" / "configs" / "v21d" / "validacao.json"
CFG_V21E = RAIZ / "experiments" / "configs" / "v21e" / "calibracao.json"
NOVAS = tuple(sorted(set(ConfigCombateV21E.__dataclass_fields__) - set(ConfigCombateV21D.__dataclass_fields__)))


def _ler(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def _regras(chaves: dict):
    c = rb.carregar(CFG_V21C)
    return rb.regras_de({**c, "regras_v21": {**c["regras_v21"], **chaves}})


def _v21d() -> dict:
    return _ler(CFG_V21D)["regras_v21"]


def test_chaves_da_v21e_desligadas_por_padrao_e_so_listas():
    assert set(NOVAS) == set(bots.CHAVES_LISTAS_V21E)
    assert not any(getattr(ConfigCombateV21E(), k) for k in NOVAS)
    # com as chaves da V21E todas em False, os campos herdados sao os da V21D
    d = ConfigCombateV21D(**{k: v for k, v in asdict(_regras(_v21d()).v21).items()})
    e = _regras({**_v21d(), **{k: False for k in NOVAS}}).v21
    assert type(e) is ConfigCombateV21E
    assert {k: v for k, v in asdict(e).items() if k not in NOVAS} == asdict(d)


def test_configs_v21c_e_v21d_montam_a_classe_de_antes():
    """As configs gravadas da V21C e da V21D continuam montando a mesma classe, com o mesmo config_sha256."""
    c = rb.carregar(CFG_V21C)
    assert type(rb.regras_de(c).v21) is ConfigCombateV21C
    gravado = _ler(RAIZ / "artifacts_combate_v21c" / "validacao" / "gates.json")["hashes"]["config_sha256"]
    assert rb.hashes(c)["config_sha256"] == gravado
    cd = {**c, "regras_v21": {**c["regras_v21"], **_v21d()}}
    assert type(rb.regras_de(cd).v21) is ConfigCombateV21D


def test_desligadas_as_listas_e_as_partidas_sao_as_da_v21d():
    rd = _regras(_v21d())
    re_ = _regras({**_v21d(), **{k: False for k in NOVAS}})
    for f in FORMAS + tuple(SOMBRIOS):
        assert gambits_adulto(f, re_.v21) is gambits_adulto(f, rd.v21)
    for i, fa in enumerate(FORMAS):
        fb = FORMAS[(i + 3) % len(FORMAS)]
        a_d, b_d = lutador_adulto(fa, "brasa", rd.v21), lutador_adulto(fb, "limo", rd.v21)
        a_e, b_e = lutador_adulto(fa, "brasa", re_.v21), lutador_adulto(fb, "limo", re_.v21)
        for s in (11, 12, 13):
            assert jogar(a_d, b_d, s, rd).log[1:] == jogar(a_e, b_e, s, re_).log[1:]


def test_config_v21e_liga_as_edicoes_declaradas():
    c = _ler(CFG_V21E)
    assert {k: c["regras_v21"][k] for k in _v21d()} == _v21d()
    assert all(c["regras_v21"][k] for k in NOVAS)
    r = _regras(c["regras_v21"])
    assert type(r.v21) is ConfigCombateV21E
    assert r.base == rb.regras_de(rb.carregar(CFG_V21C)).base          # a base V2C nao muda
    rd = _regras(_v21d())
    g = {f: gambits_adulto(f, r.v21) for f in FORMAS}
    d = {f: gambits_adulto(f, rd.v21) for f in FORMAS}
    defende, contra_pele = bots.REGRA_DEFENDE_DO_GOLPE, bots.REGRA_CONTRA_GOLPE_NA_PELE
    carregar20 = next(x for x in ADULTOS["duelista"].regras if x.acao is Acao.CARREGAR)
    # duelista: a regra nova logo depois da leitura do preparo; sai o carregar
    assert g["duelista"].regras[1] == defende and carregar20 not in g["duelista"].regras
    assert [x for x in g["duelista"].regras if x != defende] == [x for x in d["duelista"].regras if x != carregar20]
    # tita: depois das duas leituras do preparo
    assert g["tita"].regras[2] == defende and carregar20 not in g["tita"].regras
    assert [x for x in g["tita"].regras if x != defende] == [x for x in d["tita"].regras if x != carregar20]
    # espelho e muralha: sem o carregar (guts < 40); a muralha com o contra-golpe na pele em segundo
    for f in ("espelho", "muralha"):
        assert not any(x.acao is Acao.CARREGAR for x in g[f].regras)
    assert list(g["espelho"].regras) == [x for x in d["espelho"].regras if x.acao is not Acao.CARREGAR]
    assert g["muralha"].regras[1] == contra_pele
    assert [x for x in g["muralha"].regras if x != contra_pele] == [x for x in d["muralha"].regras if x.acao is not Acao.CARREGAR]
    # as outras formas, as sombrias e as listas canonicas nao mudam
    for f in ("furioso", "sentinela", "emboscador", "vigia"):
        assert g[f] is d[f]
    for s in SOMBRIOS:
        assert gambits_adulto(s, r.v21) is SOMBRIOS[s]
    assert defende not in ADULTOS["duelista"].regras + ADULTOS["tita"].regras
    for f in FORMAS:
        assert len(g[f].regras) <= 8


def test_chaves_da_muralha_pedem_a_lista_do_espelho():
    with pytest.raises(ValueError):
        gambits_adulto("muralha", ConfigCombateV21E(muralha_sem_carregar=True))
    with pytest.raises(ValueError):
        gambits_adulto("muralha", ConfigCombateV21E(muralha_contra_golpe_na_pele=True))


def test_calibracao_fase1_confere_o_config():
    import calibrar_equilibrio_geral as eg
    c = eg.config()
    assert c["variante"] == "v21e"
    assert eg.VARIANTES["v21e"][1] == c["regras_v21"] and eg.VARIANTES["v21d"][1] == _v21d()
    assert type(eg.regras("v21e").v21) is ConfigCombateV21E and type(eg.regras("v21d").v21) is ConfigCombateV21D
    assert eg.sementes() == [3101, 3202, 3303, 3404, 3505]


def test_gabarito_web_v21e_reproduz():
    """O gabarito de paridade da web (web/app/test/gabaritos/combate_v21e_python.json) sai igual do exportador."""
    import exportar_gabarito_v21e as ex
    gravado = _ler(ex.SAIDA)
    sem_fontes = lambda g: {**g, "hashes": {k: x for k, x in g["hashes"].items() if k != "regras_sha256"}}  # noqa: E731
    assert sem_fontes(json.loads(json.dumps(ex.gerar()))) == sem_fontes(gravado)
    assert gravado["resumo"]["diferentes_da_v21d"] > 20
