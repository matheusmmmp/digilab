"""Reequilibrio dos arquetipos, rodada 1 (docs/EQUILIBRIO_RODADA1.md): chaves da ConfigCombateV21D.

Com as chaves desligadas tudo reproduz a V21C (hash das configs gravadas, listas canonicas, partidas); ligadas, o
candidato A esconde o preparo feito sob pele_dura e o candidato C troca so a lista da muralha.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "experiments"))

import run_bateria_v21 as rb  # noqa: E402
from digilab.combate_v2.v21 import bots  # noqa: E402
from digilab.combate_v2.v21.bots import ADULTOS, FORMAS, GAMBITS_MURALHA_V21D, gambits_adulto, lutador_adulto  # noqa: E402
from digilab.combate_v2.v21.gambits import CONTEXTO_VAZIO, Condicao  # noqa: E402
from digilab.combate_v2.v21.partida import jogar  # noqa: E402
from digilab.combate_v2.v21.regras import Acao, Distancia, Regras, estado_inicial, resolver  # noqa: E402
from digilab.config import ConfigCombateV21C, ConfigCombateV21D  # noqa: E402

CFG_VALIDACAO = RAIZ / "experiments" / "configs" / "v21c" / "validacao.json"
MECANISMO = RAIZ / "artifacts_combate_v21c" / "diagnostico_arquetipos" / "mecanismo.json"


def _cfg() -> dict:
    return rb.carregar(CFG_VALIDACAO)


def _regras(**chaves) -> Regras:
    c = _cfg()
    return rb.regras_de({**c, "regras_v21": {**c["regras_v21"], **chaves}})


def test_config_v21c_intacta():
    """As configs V21C continuam montando a ConfigCombateV21C: mesmo config_sha256 da validacao gravada."""
    c = _cfg()
    assert type(rb.regras_de(c).v21) is ConfigCombateV21C
    gravado = json.loads((RAIZ / "artifacts_combate_v21c" / "validacao" / "gates.json").read_text(encoding="utf-8"))
    assert rb.hashes(c)["config_sha256"] == gravado["hashes"]["config_sha256"]
    r = _regras(preparo_sob_pele_oculto=False, muralha_lista_espelho=False)
    assert type(r.v21) is ConfigCombateV21D
    assert {k: v for k, v in asdict(r.v21).items() if k in ConfigCombateV21C.__dataclass_fields__} == asdict(rb.regras_de(c).v21)
    assert not ConfigCombateV21D().preparo_sob_pele_oculto and not ConfigCombateV21D().muralha_lista_espelho


def _tita_preparando(sob_pele: bool, r: Regras):
    ta, op = lutador_adulto("tita", "brasa", r.v21), lutador_adulto("espelho", "brasa", r.v21)
    e = estado_inicial(ta.perfil, op.perfil)
    e = replace(e, distancia=Distancia.PERTO,
                lados=tuple(replace(x, guts=x.perfil.guts_max) for x in e.lados))
    if sob_pele:
        e, _ = resolver(e, Acao.PELE_DURA, Acao.DEFENDER, r)
    e, res = resolver(e, Acao.PREPARAR_PESADO, Acao.DEFENDER, r)
    assert not res.interrompido[0] and e.lados[0].preparando
    return e


def test_candidato_a_esconde_so_o_preparo_sob_pele():
    prep = Condicao("oponente_preparando")
    for chave in (False, True):
        r = _regras(preparo_sob_pele_oculto=chave)
        com_pele, sem_pele = _tita_preparando(True, r), _tita_preparando(False, r)
        assert com_pele.lados[0].preparo_sob_pele and not sem_pele.lados[0].preparo_sob_pele
        assert prep.vale(sem_pele, 1, CONTEXTO_VAZIO, r)                 # sem pele: sempre visivel
        assert prep.vale(com_pele, 1, CONTEXTO_VAZIO, r) is (not chave)  # sob pele: so a chave esconde
        assert prep.vale(com_pele, 1, CONTEXTO_VAZIO)                    # regras padrao: visivel
    # no turno seguinte o pesado sai e o preparo acaba
    e, _ = resolver(_tita_preparando(True, _regras(preparo_sob_pele_oculto=True)), Acao.PESADO, Acao.DEFENDER,
                    _regras(preparo_sob_pele_oculto=True))
    assert not e.lados[0].preparando and not e.lados[0].preparo_sob_pele


def test_candidato_c_so_troca_a_muralha():
    r0, rc = _regras(), _regras(muralha_lista_espelho=True)
    for f in FORMAS:
        assert gambits_adulto(f, r0.v21) is ADULTOS[f]
        assert lutador_adulto(f, "brasa", r0.v21).gambits is ADULTOS[f]
        esperado = GAMBITS_MURALHA_V21D if f == "muralha" else ADULTOS[f]
        assert lutador_adulto(f, "brasa", rc.v21).gambits is esperado
    assert GAMBITS_MURALHA_V21D.regras == ADULTOS["espelho"].regras
    assert ADULTOS["muralha"] is not GAMBITS_MURALHA_V21D and ADULTOS["muralha"].regras != ADULTOS["espelho"].regras
    for s in bots.SOMBRIOS:
        assert lutador_adulto(s, "brasa", rc.v21).gambits is bots.SOMBRIOS[s]


def test_chaves_desligadas_reproduzem_as_partidas():
    """V21D com as duas chaves em False joga as mesmas partidas (log igual) que a V21C."""
    rc, rd = rb.regras_de(_cfg()), _regras(preparo_sob_pele_oculto=False, muralha_lista_espelho=False)
    for fa, fb in (("tita", "espelho"), ("vigia", "tita"), ("muralha", "furioso"), ("tita", "muralha")):
        for k in range(6):
            a, b = lutador_adulto(fa, "cirro", rc.v21), lutador_adulto(fb, "cirro", rc.v21)
            a2, b2 = lutador_adulto(fa, "cirro", rd.v21), lutador_adulto(fb, "cirro", rd.v21)
            assert jogar(a, b, 900 + k, rc).log == jogar(a2, b2, 900 + k, rd).log


def test_chave_desligada_reproduz_o_diagnostico_na_brasa():
    """Matriz da brasa nas sementes de calibracao (N = 100 por semente) com a V21D desligada = pontos por especie
    do diagnostico (artifacts_combate_v21c/diagnostico_arquetipos/mecanismo.json). ~20 s."""
    c = _cfg()
    r = _regras(preparo_sob_pele_oculto=False, muralha_lista_espelho=False)
    gravado = json.loads(MECANISMO.read_text(encoding="utf-8"))["pontos_por_especie"]
    lut = {f: lutador_adulto(f, "brasa", r.v21) for f in FORMAS}
    for i, fa in enumerate(FORMAS):
        for fb in FORMAS[i + 1:]:
            pts = [x for _, _, x, _ in rb.partidas_par(lut[fa], lut[fb], "e1|brasa", c["sementes_calibracao"], 100, r)]
            assert sum(pts) / len(pts) == gravado[f"brasa|{fa}|{fb}"]["pontos"], (fa, fb)
