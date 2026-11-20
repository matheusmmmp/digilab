"""A medida do movimento da AN4 (`digilab.metrics.movimento_nas_decisoes`; docs/PLANO_ANALISE_V3_ACOES_NOVAS.md, 4.3; AN3-5): o teste de
unidade e o teste contra a AN0 (`artifacts_v3_acoes_novas/hoje.json`) nas vidas gravadas da LM0 (os 0,49 e os 50,5 % de la). Nenhuma vida
roda aqui: as vidas da LM0 sao os gabaritos ja gravados (sementes dos testes)."""
from __future__ import annotations

import gzip
import json
import math
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import medir_v3_acoes_novas_hoje as an0  # noqa: E402
from digilab.metrics import movimento_nas_decisoes  # noqa: E402


# ------------------------------------------------------------------ unidade
def test_mov_conta_so_as_decisoes_fora_do_dormir_e_a_ultima_fica_fora():
    d = [("ocioso", 0, 0), ("ocioso", 0, 0), ("explorar", 3, 4), ("dormir", 3, 4), ("dormir", 6, 8), ("comer", 6, 8)]
    m = movimento_nas_decisoes(d, 2)
    # passos: 0, 5, 0, 5, 0; fora do dormir com passo: k = 0, 1, 2 (a ultima, k = 5, nao tem passo)
    assert m["n_fora_do_dormir"] == 3
    assert m["saem_do_lugar"] == 1                      # so o k = 1 (ocioso que vira explorar: o passo do ocioso e > 0)
    assert m["mov"] == pytest.approx(1 / 3)
    assert m["distancia"] == pytest.approx(10.0)       # o passo do dormir (k = 3) entra na distancia
    assert m["distancia_por_dia"] == pytest.approx(5.0)


def test_zigue_zague_nas_corridas_de_explorar():
    # uma corrida de 3 explorar (k = 1, 2, 3) que vai e volta, depois um ocioso
    d = [("ocioso", 0, 0), ("explorar", 0, 0), ("explorar", 10, 0), ("explorar", 0, 0), ("ocioso", 10, 0), ("ocioso", 10, 0)]
    z = movimento_nas_decisoes(d, 1)["zigue_zague"]
    assert z["corridas_de_2_ou_mais"] == 1
    assert z["caminho"] == pytest.approx(30.0)         # os passos de k = 1, 2, 3
    assert z["liquido"] == pytest.approx(10.0)         # de (0, 0) a (10, 0), a posicao da decisao seguinte a corrida
    assert z["liquido_sobre_caminho"] == pytest.approx(1 / 3)
    assert z["pares"] == 2 and z["pares_que_invertem"] == 2
    assert z["fracao_que_inverte"] == 1.0


def test_corrida_que_termina_a_vida_e_pares_com_passo_zero_ficam_fora():
    d = [("explorar", 0, 0), ("explorar", 0, 0), ("explorar", 5, 0)]
    z = movimento_nas_decisoes(d, 1)["zigue_zague"]
    assert z["corridas_de_2_ou_mais"] == 0 and z["liquido_sobre_caminho"] is None
    assert z["pares"] == 0 and z["fracao_que_inverte"] is None


def test_a_acao_da_corrida_e_um_parametro():
    d = [("vagar", 0, 0), ("vagar", 4, 0), ("explorar", 8, 0), ("ocioso", 8, 0)]
    assert movimento_nas_decisoes(d, 1, "vagar")["zigue_zague"]["corridas_de_2_ou_mais"] == 1
    assert movimento_nas_decisoes(d, 1)["zigue_zague"]["corridas_de_2_ou_mais"] == 0


@pytest.mark.parametrize("d, dias", [([], 1), ([("ocioso", 0, 0), ("ocioso", 0, 0)], 0), ([("dormir", 0, 0), ("ocioso", 1, 1)], 1)])
def test_falha_alto(d, dias):
    with pytest.raises(ValueError):
        movimento_nas_decisoes(d, dias)


# ------------------------------------------------------------------ contra a AN0
def _vidas_lm0():
    for nome in ("digibrain_modular_comedouro.json.gz", "digibrain_modular_longe_fixo.json.gz"):
        with gzip.open(an0.PASTA_GAB / nome, "rt", encoding="utf-8") as f:
            for v in json.load(f)["vidas"]:
                decs = sorted(v["decisoes"], key=lambda x: x["k"])
                # a AN0 le o zigue-zague nas corridas de vagar (a escolha), nao de explorar (a acao): o rotulo da corrida e "vagar"
                yield [("vagar" if d["motivo"]["escolha"][:2] == an0.VAGAR else d["motivo"]["acao"], *an0._posicao(d)) for d in decs]


def test_contra_a_an0_nas_vidas_da_lm0():
    hoje = json.loads((RAIZ / "artifacts_v3_acoes_novas" / "hoje.json").read_text(encoding="utf-8"))["grupos"]["lm0|todos|todos"]
    ms = [movimento_nas_decisoes(d, 4, "vagar") for d in _vidas_lm0()]
    assert len(ms) == hoje["vidas"] == 8
    zz = [m["zigue_zague"] for m in ms]
    pares, inverte = sum(z["pares"] for z in zz), sum(z["pares_que_invertem"] for z in zz)
    liq, cam = sum(z["liquido"] for z in zz), sum(z["caminho"] for z in zz)
    esperado = hoje["zigue_zague_do_vagar"]
    assert pares == esperado["pares_de_vagar_seguidos_com_passo"] == 206
    assert inverte == esperado["pares_que_invertem"] == 104
    assert round(inverte / pares, 6) == esperado["fracao_que_inverte"] == 0.504854
    assert round(liq / cam, 6) == esperado["razao_liquido_sobre_caminho_nas_corridas_de_2_ou_mais"] == 0.488214
    # a distancia: a soma dos passos e a soma de media x n das tres classes da AN0 (que cobrem toda decisao com passo)
    dist = sum(m["distancia"] for m in ms)
    desloc = hoje["deslocamento_por_decisao"]
    assert dist == pytest.approx(sum(c["media"] * c["n"] for c in desloc.values()), abs=0.01)
    # as decisoes que saem do lugar: as fora do dormir (MOV) mais as do dormir; o total e o das tres classes da AN0
    saem_an0 = sum(round(c["n"] * (1 - c["fracao_sem_sair_do_lugar"])) for c in desloc.values())
    saem_dormir = 0
    for d in _vidas_lm0():
        saem_dormir += sum(1 for k in range(len(d) - 1) if d[k][0] == "dormir" and math.hypot(d[k + 1][1] - d[k][1], d[k + 1][2] - d[k][2]) > 0)
    assert sum(m["saem_do_lugar"] for m in ms) + saem_dormir == saem_an0
