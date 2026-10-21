"""A etapa 0 da competicao entre as regras urgentes (docs/TAREFA_V2_V3_COMPETICAO.md, secao 4): o gabarito das vidas de hoje (G2), gravado
antes da medicao sombra."""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "tests"))
sys.path.insert(0, str(RAIZ / "experiments"))

import gabarito_competicao as gc  # noqa: E402


def test_as_vidas_de_hoje_sao_as_do_gabarito():
    """G2: as 20 vidas do v11 do E0 (4 donos x as sementes dos testes, 14 dias) saem iguais ao gabarito gravado antes da etapa 0"""
    gravado = json.loads(gc.ARQUIVO.read_text(encoding="utf-8"))
    assert gc.gerar() == gravado


def test_as_propostas_seguem_a_v3_4_e_a_cr_3():
    """o sono_exaustao fica forcado; o tempo livre nao entra; com uma regra urgente so, ou so o dormir, nao ha disputa; cada acao vem da
    regra mais urgente que a propoe"""
    import medir_competicao_etapa0 as m
    p = {"humor": 0.5}
    assert m.propostas(["sono_exaustao", "pedido_necessidade", "fome_moderada", "tempo_livre"], p) is None
    assert m.propostas(["fome_moderada", "tempo_livre"], p) is None
    assert m.propostas(["sono_continuar", "sono_noite", "tempo_livre"], p) is None
    assert m.propostas(["pedido_necessidade", "fome_moderada", "tempo_livre"], p) == {"chamar_atencao": "pedido_necessidade",
                                                                                      "comer": "fome_moderada"}
    assert m.propostas(["sono_continuar", "abandono", "tempo_livre"], {"humor": 0.2}) == {"dormir": "sono_continuar",
                                                                                         "emburrar": "abandono"}


def test_o_artefato_se_refaz_igual():
    """a etapa 0: a sombra nao muda a vida (o G2 e conferido dentro da medida, falha alto), e o artefato se refaz igual"""
    import medir_competicao_etapa0 as m
    gravado = json.loads(m.ARQUIVO.read_text(encoding="utf-8"))
    m.main()
    assert json.loads(m.ARQUIVO.read_text(encoding="utf-8")) == gravado
    a = gravado["analise"]
    assert abs(a["geral"]["frac_forcadas"] - 0.5525) < 1e-3          # o mesmo E0
    assert a["kappa_cr2"] == 16                                       # a CR-2: a menor potencia de 2 com o instinto >= 0,9 no nascimento
    assert a["g0_r1_pode_aprender"]["passa"] is True
