"""O orquestrador do I2 da INDIVIDUALIDADE (experiments/run_v3_individualidade.py; docs/PLANO_ANALISE_V3_INDIVIDUALIDADE.md): a trava (o
cabecalho APROVADO, a secao do registro, a faixa, as bases e o K do plano, no maximo 4 processos, nada por cima de uma pasta), a analise
num caso sintetico e a fumaca de ponta a ponta. Vidas so com as sementes dos testes (101...505): nenhuma da faixa 85xxx roda aqui."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v3_individualidade as ri  # noqa: E402
from digilab import metrics as M  # noqa: E402

CONFIG = RAIZ / "experiments/configs/v3_individualidade/individualidade.json"


def _cfg(**troca) -> dict:
    c = json.loads(CONFIG.read_text(encoding="utf-8"))
    c.update(troca)
    return c


def _fumaca(dias: int = 2) -> dict:
    return _cfg(unidades={"bases": [101], "k": 1, "prefixo": ri.PREFIXO}, dias=dias)


def _plano_com(status: str, registro: bool) -> str:
    texto = (RAIZ / ri.PLANO).read_text(encoding="utf-8")
    linhas = texto.splitlines()
    i = next(i for i, x in enumerate(linhas) if x.startswith("**Status:"))
    linhas[i] = status
    texto = "\n".join(linhas)
    if registro and ri.TITULO_REGISTRO not in texto:
        texto += f"\n\n{ri.TITULO_REGISTRO}\n\no registro (so no teste)\n"
    if not registro:
        texto = "\n".join(x for x in texto.splitlines() if not x.startswith(ri.TITULO_REGISTRO))
    return texto


# ================================================================== a trava
def test_a_config_da_run_e_a_do_plano():
    cfg = _cfg()
    assert tuple(cfg["unidades"]["bases"]) == ri.BASES and cfg["unidades"]["k"] == ri.K_POR_BASE and cfg["dias"] == ri.DIAS
    assert any((lo, hi) == ri.FAIXA for lo, hi, _ in ri.FAIXAS_RESERVADAS)


def test_a_trava_libera_so_com_aprovado_e_registro():
    cfg = _cfg()
    assert ri.modo_da_config(cfg, _plano_com("**Status: APROVADO pelo Matheus em 2026-11-07.**", True)) == ri.FASE
    with pytest.raises(RuntimeError, match="registro"):
        ri.modo_da_config(cfg, _plano_com("**Status: APROVADO pelo Matheus em 2026-11-07.**", False))
    with pytest.raises(RuntimeError, match="APROVADO"):
        ri.modo_da_config(cfg, _plano_com("**Status: PROPOSTO.**", True))


def test_hoje_a_run_de_pesquisa_e_recusada_sem_o_registro():
    """o plano esta APROVADO, mas a secao do registro so entra no I2b, antes da primeira vida"""
    if ri.TITULO_REGISTRO in (RAIZ / ri.PLANO).read_text(encoding="utf-8"):
        pytest.skip("o registro ja esta no plano")
    with pytest.raises(RuntimeError, match="registro"):
        ri.modo_da_config(_cfg())


def test_fora_do_plano_falha_alto():
    plano = _plano_com("**Status: APROVADO pelo Matheus em 2026-11-07.**", True)
    with pytest.raises(ValueError):
        ri.modo_da_config(_cfg(unidades={"bases": list(ri.BASES), "k": 5, "prefixo": ri.PREFIXO}), plano)
    with pytest.raises(ValueError):
        ri.modo_da_config(_cfg(dias=10), plano)
    with pytest.raises(bv.SementeSemPlano):
        ri.modo_da_config(_cfg(unidades={"bases": [12345], "k": 12, "prefixo": ri.PREFIXO}), plano)
    with pytest.raises(ValueError):
        ri.modo_da_config(_cfg(sobra=1), plano)
    with pytest.raises(ValueError):
        ri.modo_da_config(_fumaca(dias=15))


def test_processos_e_pasta(tmp_path):
    with pytest.raises(ValueError):
        ri.rodar(_fumaca(), tmp_path / "x", 5)
    (tmp_path / "existe").mkdir()
    with pytest.raises(FileExistsError):
        ri.rodar(_fumaca(), tmp_path / "existe", 1)


# ================================================================== a analise num caso sintetico
def _pet(braco: str, dono: str, semente: int, nivel: float, faceta: int = 0) -> dict:
    """um pet cujo traco e o nivel dele mais um ruido pequeno e fixo por (dia, replica)"""
    tracos = []
    for dia in range(4):
        for r in range(3):
            ruido = ((dia * 3 + r) % 5 - 2) * 0.01
            tracos.append({"dia": dia, "replica": r, "apego": nivel + ruido, "tedio": 0.5 + ruido, "neofilia": float((dia + r + semente) % 2),
                           "ousadia": float(r == 0), "brincar": nivel / 2 + ruido, "susto": ruido})
    return {"braco": braco, "dono": dono, "semente": semente, "tracos": tracos,
            "facetas": {"apego_dono": faceta, "cautela_comida": 0, "ousadia_longe": 0} if braco == "REL+F" else None,
            "descritivo": {"latencias": {}, "andou": {}, "dias_sem_sonda": 0}}


def test_analise_sintetica():
    pets = []
    for i, s in enumerate((101, 202, 303, 404, 505)):
        for j, d in enumerate(ri.DONOS):
            nivel = 0.1 * i + 0.02 * j
            pets += [_pet("REL", d, s, nivel), _pet("REL+F", d, s, nivel, faceta=i * 10 + j)]
    a = ri.analisar(pets, boot=200)["por_braco"]
    rep = a["REL"]["repetibilidade"]["apego"]
    assert rep["R_pet"]["r"] > 0.9 and rep["R_dia"]["r"] > 0.9 and rep["R_pet"]["ic95"][0] > 0.8
    assert a["REL"]["repetibilidade"]["tedio"]["R_pet"]["r"] == 0.0          # o tedio so tem o ruido comum: nada entre pets
    assert a["REL+F"]["facetas"]["apego"]["spearman"] == pytest.approx(1.0)
    regra = a["REL"]["regra_i3"]
    assert "apego" in regra["ficam"]
    # a ousadia sintetica so varia entre as replicas do mesmo dia (1, 0, 0 em todo pet): o R_rep e 0, e a regra (c) a tira
    assert not regra["por_traco"]["ousadia"]["fica"] and regra["por_traco"]["ousadia"]["motivos"][0].startswith("c:")
    assert set(a["REL"]["sindrome"]["matriz"]) == set(M.TRACOS_INDIVIDUALIDADE)
    assert a["REL"]["norma_de_reacao"]["apego"]["braco"]["n"] == len(pets) // 2


def test_regra_i3_binario_fora_da_faixa():
    rep = {t: {"R_rep": {"r": 0.5, "ic95": [0.3, 0.7]}} for t in M.TRACOS_INDIVIDUALIDADE}
    validas = {t: 1.0 for t in M.TRACOS_INDIVIDUALIDADE}
    r = ri.regra_i3(rep, validas, {"neofilia": 0.5, "ousadia": 0.01})
    assert not r["por_traco"]["ousadia"]["fica"] and r["por_traco"]["neofilia"]["fica"]
    rep["susto"] = {"R_rep": {"r": 0.01, "ic95": [0.0, 0.04]}}
    validas["tedio"] = 0.3
    r = ri.regra_i3(rep, validas, {"neofilia": 0.5, "ousadia": 0.5})
    assert set(r["ficam"]) == {"apego", "neofilia", "ousadia", "brincar"} and not r["volta_ao_matheus"]


# ================================================================== a fumaca de ponta a ponta
def test_fumaca_de_ponta_a_ponta(tmp_path):
    pasta = tmp_path / "fumaca"
    r = ri.rodar(_fumaca(dias=2), pasta, 1, boot=50)
    assert r["meta"]["modo"] == "fumaca" and len(r["registros"]) == len(ri.BRACOS) * len(ri.DONOS)
    for n in ("meta.json", "medidas.json", "tracos.jsonl", "analise.json", "custo.json"):
        assert (pasta / n).exists()
    a = json.loads((pasta / "analise.json").read_text(encoding="utf-8"))
    assert set(a["por_braco"]) == set(ri.BRACOS) and "regra_i3" in a["por_braco"]["REL"] and "facetas" in a["por_braco"]["REL+F"]
    assert all(len(x["tracos"]) > 0 for x in r["registros"])
