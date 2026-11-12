"""As duas regras do E1 da rodada de equilibrio do cuidado (docs/PLANO_V3_EQUILIBRIO_CUIDADO.md, EQ-7; a `ConfigEquilibrioCuidado`): a guarda
da fome urgente no brincar (o M-ARB) e o bebe que come com a fome dele (o M-IMPULSO e o gancho `estagio_bebe`). A chave desligada (a vida de
hoje byte a byte) esta no tests/test_gabarito_equilibrio_cuidado.py; a paridade com o TS, no web/app/test/equilibrio_cuidado_paridade.test.ts
(o gabarito do experiments/exportar_gabarito_digibrain_modular.py --equilibrio)."""
from __future__ import annotations

import random
import sys
from dataclasses import fields
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import gabarito_lance_dono as G  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402

from digilab.config import (CONFIG_DIGIBRAIN_INATOS, CONFIG_EQUILIBRIO_CUIDADO, CONFIG_LANCE_DONO_LIGADA,  # noqa: E402
                            CONFIG_SONO_SEGURA_LIGADA, INATOS_E1_PROPOSTOS, PARAMETROS_E1, PARAMETROS_EQUILIBRIO_CUIDADO,
                            ConfigEquilibrioCuidado, inatos_e1)
from digilab.digibrain.arb import Arbitragem  # noqa: E402

S = CONFIG_DIGIBRAIN_INATOS.escala
GUARDA = ConfigEquilibrioCuidado(guarda_fome_brincar=True)
BEBE = ConfigEquilibrioCuidado(comer_bebe=True)


def test_a_config_desligada_por_padrao_e_os_status():
    assert not CONFIG_EQUILIBRIO_CUIDADO.ligada
    assert not CONFIG_EQUILIBRIO_CUIDADO.guarda_fome_brincar and not CONFIG_EQUILIBRIO_CUIDADO.comer_bebe
    assert {f.name for f in fields(ConfigEquilibrioCuidado)} == set(PARAMETROS_EQUILIBRIO_CUIDADO)
    assert all(st == "DECIDIDO" and "SEM FONTE" in fonte for st, fonte in PARAMETROS_EQUILIBRIO_CUIDADO.values())   # APROVADOS em 2026-11-12 (E2/E3)
    with pytest.raises(TypeError):
        ConfigEquilibrioCuidado(guarda_fome_brincar=1)
    with pytest.raises(ValueError):
        ConfigEquilibrioCuidado(w_comer_bebe=0)


def test_os_inatos_do_e1_so_trocam_os_dois_numeros():
    assert set(INATOS_E1_PROPOSTOS) == set(PARAMETROS_E1)
    assert all(st == "DECIDIDO" and "SEM FONTE" in fonte for st, fonte in PARAMETROS_E1.values())   # APROVADOS em 2026-11-12 (E2/E3)
    e1 = inatos_e1()
    assert CONFIG_DIGIBRAIN_INATOS.urgencia_lambda == 512 and dict(dict(CONFIG_DIGIBRAIN_INATOS.w0)["brincar"])["vies"] == -256
    assert e1.urgencia_lambda == INATOS_E1_PROPOSTOS["urgencia_lambda"]
    assert dict(dict(e1.w0)["brincar"])["vies"] == INATOS_E1_PROPOSTOS["vies_brincar"]
    mudou = [f.name for f in fields(e1) if getattr(e1, f.name) != getattr(CONFIG_DIGIBRAIN_INATOS, f.name)]
    assert mudou == ["urgencia_lambda", "w0"] or sorted(mudou) == ["urgencia_lambda", "w0"]
    linhas = [(b, [c for c, v in linha if (b, c) != ("brincar", "vies") and v != dict(dict(e1.w0)[b])[c]]) for b, linha in CONFIG_DIGIBRAIN_INATOS.w0]
    assert all(not dif for _, dif in linhas)


def _unidade(acao: str, a: int) -> dict:
    return {"chave": (acao, None, None), "acao": acao, "a": a, "soma": a, "termos": {t: 0 for t in
            ("incentivo", "habito", "memoria", "persistencia")}}


def test_a_guarda_zera_o_brincar_no_sorteio_e_nas_sondas():
    arb = Arbitragem(None, False, False)
    unidades = [_unidade("ocioso", 0), _unidade("brincar", 3000), _unidade("explorar", 100)]
    afeto = {"g_exp": 0}
    sens = {"leitura": {"energia": S}}
    livre = arb.escolher(unidades, afeto, sens, random.Random(1), False)
    guardado = arb.escolher(unidades, afeto, sens, random.Random(1), False, sem_brincar=True)
    assert livre["unidade"]["acao"] == "brincar"
    assert guardado["unidade"]["acao"] == "explorar" and guardado["pesos"][1] == 0
    assert all(v[0] != "brincar" for k, v in guardado["sondas"].items() if not k.endswith("decidiu"))
    with pytest.raises(TypeError):
        arb.escolher(unidades, afeto, sens, random.Random(1), False, sem_brincar=None)


def _vida(dono: str, semente: int, equilibrio, bebe_ate: int | None = None):
    fp, fm = orq.fabricas("REL", dono, semente, 1, orq.ORCAMENTO_POR_DIA, conserto=True, sono=CONFIG_SONO_SEGURA_LIGADA,
                          lance=CONFIG_LANCE_DONO_LIGADA, equilibrio=equilibrio)
    registro = fp()
    cerebro = orq.cerebro_de(registro)
    if bebe_ate is not None:
        agir = cerebro.agir

        def com_estagio(obs, rng):
            cerebro.estagio_bebe(cerebro.k < bebe_ate)
            return agir(obs, rng)
        cerebro.agir = com_estagio
    motor = G.roteiro(lambda _cfg=None: registro, fm, semente, dias=1)
    return motor, cerebro


def test_desligada_o_motivo_nao_ganha_campo():
    _, c = _vida("atencioso", 101, None)
    assert all("equilibrio" not in m for m in c.motivos)


def test_o_bebe_soma_o_peso_ao_inato_do_comer_e_exige_o_gancho():
    _, c = _vida("atencioso", 101, BEBE, bebe_ate=10)
    assert [m["equilibrio"]["bebe"] for m in c.motivos[:12]] == [S] * 10 + [0, 0]
    _, c = _vida("atencioso", 101, BEBE, bebe_ate=10 ** 6)
    _, hoje = _vida("atencioso", 101, None)
    # o termo so entra nas unidades do comer: ate a primeira decisao com uma, as duas vidas sao a mesma; nela, o inato do comer difere pelo peso
    k = next(i for i, m in enumerate(hoje.motivos) if any(u["chave"][0] == "comer" for u in m["unidades"]))
    assert [m["acao"] for m in c.motivos[:k]] == [m["acao"] for m in hoje.motivos[:k]]
    com = {str(u["chave"]): (u["chave"][0], u["termos"]["inato"]) for u in c.motivos[k]["unidades"]}
    sem = {str(u["chave"]): u["termos"]["inato"] for u in hoje.motivos[k]["unidades"]}
    assert any(acao == "comer" for acao, _ in com.values())
    for ch, (acao, v) in com.items():
        assert v - sem[ch] == (BEBE.w_comer_bebe if acao == "comer" else 0)
    with pytest.raises(RuntimeError, match="estagio_bebe"):
        _vida("atencioso", 101, BEBE)
    _, sem_regra = _vida("atencioso", 101, GUARDA)
    with pytest.raises(RuntimeError, match="comer_bebe"):
        sem_regra.estagio_bebe(True)


def test_a_guarda_bloqueia_o_brincar_com_a_fome_urgente():
    for semente in (101, 202):
        _, c = _vida("relapso", semente, GUARDA)
        guardadas = [m for m in c.motivos if m["equilibrio"]["fome_urgente_sem_brincar"]]
        assert guardadas, "a vida nao chega a fome urgente"
        assert all(m["acao"] != "brincar" for m in guardadas)
        assert all(u["w"] == 0 for m in guardadas for u in m["unidades"] if u["chave"][0] == "brincar")
