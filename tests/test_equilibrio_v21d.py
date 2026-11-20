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


# ------------------------------------------------------------------ rodada 2 (docs/EQUILIBRIO_RODADA2.md)
CHAVES_R2 = ("investida_erra_contra_recuo", "preparo_prende", "tita_bate_em_quem_recua", "vigia_bate_em_quem_recua",
             "vigia_recua_do_preparo_sob_pele")
TODAS_DESLIGADAS = {k: False for k in ("preparo_sob_pele_oculto", "muralha_lista_espelho") + CHAVES_R2}


def test_rodada2_chaves_desligadas_por_padrao():
    d = ConfigCombateV21D()
    assert not any(getattr(d, k) for k in CHAVES_R2)
    assert not set(CHAVES_R2) & set(ConfigCombateV21C.__dataclass_fields__)


def test_rodada2_todas_desligadas_reproduzem_as_partidas():
    rc, rd = rb.regras_de(_cfg()), _regras(**TODAS_DESLIGADAS)
    for fa, fb in (("furioso", "sentinela"), ("furioso", "emboscador"), ("vigia", "tita"), ("tita", "sentinela"),
                   ("vigia", "emboscador"), ("duelista", "sentinela")):
        for k in range(6):
            a, b = lutador_adulto(fa, "brasa", rc.v21), lutador_adulto(fb, "brasa", rc.v21)
            a2, b2 = lutador_adulto(fa, "brasa", rd.v21), lutador_adulto(fb, "brasa", rd.v21)
            assert a2.gambits is a.gambits and b2.gambits is b.gambits
            assert jogar(a, b, 700 + k, rc).log == jogar(a2, b2, 700 + k, rd).log


def _par(fa: str, fb: str, r: Regras, distancia):
    a, b = lutador_adulto(fa, "brasa", r.v21), lutador_adulto(fb, "brasa", r.v21)
    e = estado_inicial(a.perfil, b.perfil)
    return replace(e, distancia=distancia, lados=tuple(replace(x, guts=x.perfil.guts_max) for x in e.lados))


def test_d2_investida_erra_contra_recuo():
    for chave in (False, True):
        r = _regras(investida_erra_contra_recuo=chave)
        e, res = resolver(_par("furioso", "emboscador", r, Distancia.MEDIO), Acao.INVESTIDA, Acao.RECUAR, r)
        assert (res.dano_recebido[1] == 0.0) is chave
        assert e.distancia is (Distancia.MEDIO if chave else Distancia.PERTO)
        # o avanco comum continua prendendo quem recua (fuga condicionada)
        e, _ = resolver(_par("furioso", "emboscador", r, Distancia.MEDIO), Acao.AVANCAR, Acao.RECUAR, r)
        assert e.distancia is Distancia.PERTO
        # quem nao recua continua levando a investida
        _, res = resolver(_par("furioso", "emboscador", r, Distancia.MEDIO), Acao.INVESTIDA, Acao.MARCAR, r)
        assert res.dano_recebido[1] > 0.0
    # a sentinela com a passiva pronta vai para longe (a passiva anula o avanco da investida)
    r = _regras(investida_erra_contra_recuo=True)
    e, res = resolver(_par("furioso", "sentinela", r, Distancia.MEDIO), Acao.INVESTIDA, Acao.RECUAR, r)
    assert res.dano_recebido[1] == 0.0 and e.distancia is Distancia.LONGE


def test_e1_preparo_prende():
    for chave in (False, True):
        r = _regras(preparo_prende=chave)
        e, _ = resolver(_par("tita", "emboscador", r, Distancia.PERTO), Acao.PREPARAR_PESADO, Acao.RECUAR, r)
        assert e.distancia is (Distancia.PERTO if chave else Distancia.MEDIO)
        e, _ = resolver(_par("tita", "emboscador", r, Distancia.PERTO), Acao.DEFENDER, Acao.RECUAR, r)
        assert e.distancia is Distancia.MEDIO


def test_e2_e_v_so_trocam_as_listas_do_colosso():
    tita, vigia = ADULTOS["tita"], ADULTOS["vigia"]
    for chaves, esperado_t, esperado_v in (
            ({"tita_bate_em_quem_recua": True}, bots.GAMBITS_TITA_V21D, vigia),
            ({"vigia_bate_em_quem_recua": True}, tita, bots.GAMBITS_VIGIA_V21D[(True, False)]),
            ({"vigia_recua_do_preparo_sob_pele": True}, tita, bots.GAMBITS_VIGIA_V21D[(False, True)]),
            ({"vigia_bate_em_quem_recua": True, "vigia_recua_do_preparo_sob_pele": True}, tita,
             bots.GAMBITS_VIGIA_V21D[(True, True)])):
        r = _regras(**chaves)
        assert lutador_adulto("tita", "brasa", r.v21).gambits is esperado_t
        assert lutador_adulto("vigia", "brasa", r.v21).gambits is esperado_v
        for f in FORMAS:
            if f not in ("tita", "vigia"):
                assert lutador_adulto(f, "brasa", r.v21).gambits is ADULTOS[f]
        for s in bots.SOMBRIOS:
            assert lutador_adulto(s, "brasa", r.v21).gambits is bots.SOMBRIOS[s]
    # listas variantes: 8 regras, a regra nova no lugar certo; as canonicas intactas
    for g in (bots.GAMBITS_TITA_V21D, *bots.GAMBITS_VIGIA_V21D.values()):
        assert len(g.regras) == 8
    assert bots.GAMBITS_TITA_V21D.regras.index(bots.REGRA_BATE_EM_QUEM_RECUA) == \
        bots.GAMBITS_TITA_V21D.regras.index(tita.regras[4]) - 1
    assert bots.GAMBITS_VIGIA_V21D[(True, True)].regras[0] == bots.REGRA_RECUA_DO_PREPARO_SOB_PELE
    assert bots.REGRA_BATE_EM_QUEM_RECUA not in tita.regras + vigia.regras
    assert bots.REGRA_RECUA_DO_PREPARO_SOB_PELE not in vigia.regras
    assert len(tita.regras) == len(vigia.regras) == 8


# ---------------------------------------------------------------- validacao da variante a_c_e2v_v (docs/VALIDACAO_V21D.md)
def test_config_da_validacao_v21d_e_a_variante_a_c_e2v_v():
    """O config registrado liga exatamente as 4 chaves da a_c_e2v_v e lista as outras 3 da V21D desligadas; sem ele, a
    ConfigCombateV21D padrao continua com tudo desligado."""
    import validar_v21d
    c = validar_v21d.config()
    assert {k for k, x in c["regras_v21"].items() if x} == {
        "preparo_sob_pele_oculto", "muralha_lista_espelho", "vigia_bate_em_quem_recua", "vigia_recua_do_preparo_sob_pele"}
    assert not any(asdict(ConfigCombateV21D())[k] for k in c["regras_v21"])


def test_gabarito_web_v21d_reproduz():
    """O gabarito de paridade da web (web/app/test/gabaritos/combate_v21d_python.json) sai igual do exportador."""
    import exportar_gabarito_v21d as ex
    gravado = json.loads(ex.SAIDA.read_text(encoding="utf-8"))
    assert _sem_hash_dos_fontes(json.loads(json.dumps(ex.gerar()))) == _sem_hash_dos_fontes(gravado)


def _sem_hash_dos_fontes(g: dict) -> dict:
    """O hash dos fontes de combate_v2/v21 (regras_sha256) muda quando os fontes ganham chaves novas desligadas (a V21E da
    rodada de equilibrio geral); as partidas, as listas e o config_sha256 nao podem mudar."""
    return {**g, "hashes": {v: {k: x for k, x in h.items() if k != "regras_sha256"} for v, h in g["hashes"].items()}}
