"""O gabarito do laco do pet com o mundo do produto no MVP (web/app/test/gabaritos/mvp_produto_python.json; docs/TAREFA_V2_MVP_MUNDO_PRODUTO.md,
a etapa 1, opcao 1 do Matheus de 2026-10-24: o layout sem arvores, so a racao do jogador) esta em dia com o Python, byte a byte.
Se mudar o corpo, o mundo ou o laco do motor com eles, rode `python experiments/exportar_gabarito_mvp_produto.py`: o G-PAR do pet v12
confere o TS contra este arquivo.

- O arquivo em disco e o que o exportador gera hoje, byte a byte.
- O cenario e o da etapa 0 (as vidas, os donos, os lugares, o cerebro) com o mundo do produto: sem arvores, so a racao do dono.
- O layout do MVP nao vaza para a pesquisa: so o produto e este gabarito o usam; a bancada segue com o layout padrao.
Sementes: so as dos testes.
"""
from __future__ import annotations

import json
import re
import sys
from dataclasses import asdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import exportar_gabarito_mvp_mundo as E0  # noqa: E402
import exportar_gabarito_mvp_produto as G  # noqa: E402

from digilab.config import CONFIG_MUNDO_LIGADA, CONFIG_MUNDO_MVP, LAYOUT_MUNDO_MVP, LAYOUT_MUNDO_PADRAO  # noqa: E402

TEXTO = G.ARQUIVO.read_text(encoding="utf-8")
GRAVADO = json.loads(TEXTO)


def test_o_gabarito_esta_em_dia_byte_a_byte():
    assert TEXTO == json.dumps(G.gerar(), sort_keys=True, separators=(",", ":")) + "\n"


def test_o_mundo_do_produto_e_o_padrao_sem_arvores():
    assert LAYOUT_MUNDO_MVP.arvores == () and LAYOUT_MUNDO_MVP.nome == "mvp"
    assert asdict(LAYOUT_MUNDO_MVP) == {**asdict(LAYOUT_MUNDO_PADRAO), "nome": "mvp", "arvores": ()}
    assert asdict(CONFIG_MUNDO_MVP) == {**asdict(CONFIG_MUNDO_LIGADA), "layout": asdict(LAYOUT_MUNDO_MVP)}
    assert GRAVADO["config"]["mundo"] == json.loads(json.dumps(asdict(CONFIG_MUNDO_MVP)))


def test_o_cenario_e_o_da_etapa_0_so_com_o_mundo_do_produto():
    e0 = json.loads(E0.ARQUIVO.read_text(encoding="utf-8"))
    assert {k: v for k, v in GRAVADO["config"].items() if k != "mundo"} == e0["config"]
    chaves = ("nome", "cerebro", "dono", "lugar", "semente", "dias")
    assert [[v[k] for k in chaves] for v in GRAVADO["vidas"]] == [[v[k] for k in chaves] for v in e0["vidas"]]
    assert all(v["semente"] in bv.SEMENTES_TESTE for v in GRAVADO["vidas"])


def test_o_gabarito_cobre_o_laco_sem_fruta():
    vidas = GRAVADO["vidas"]
    for v in vidas:
        assert v["resumo"]["arvores"] == [] and v["resumo"]["quedas"] == []
        assert all(c["tipo"] == "racao" and c["origem"] == "dono" for c in v["resumo"]["consumos"])
    ops = [o for v in vidas for o in v["traco"]]
    dec = [o for o in ops if o["op"] == "decisao"]
    assert any(o["op"] == "deixar_comida" for o in ops)
    assert all("corpo_antes" in o and "corpo_depois" in o for o in dec)
    assert {"pet", "andar", "comida", "novidade", "atividade"} <= {e[0] for o in dec for e in o["corpo_depois"]["estimulos"]}
    racao = [o for o in dec if o["ocorrido"] and o["ocorrido"]["comeu"] and o["ocorrido"]["comeu"]["tipo"] == "racao"
             and o["ocorrido"]["comeu"]["situacao"] == "madura"]
    assert len(racao) >= 10 and all(o["corpo_depois"]["q"]["fome"] < o["corpo_antes"]["q"]["fome"] for o in racao)
    assert all(o["ocorrido"]["comeu"]["tipo"] == "racao" for o in dec if o["ocorrido"] and o["ocorrido"]["comeu"])
    # o A tambem come no mundo do produto (a racao do dono)
    assert any(o["ocorrido"] and o["ocorrido"]["comeu"] for v in vidas if v["cerebro"] == "a_v11" for o in v["traco"]
               if o["op"] == "decisao")
    assert sum(1 for o in dec if o["ocorrido"] and o["ocorrido"]["deslocamento"] > 0) >= 50


def test_o_layout_do_mvp_nao_vaza_para_a_pesquisa():
    """So o config (que o define), o exportador do produto e os testes citam o mundo do MVP; nenhum modulo do digilab/ nem da bancada."""
    nomes = re.compile(r"\b(CONFIG_MUNDO_MVP|LAYOUT_MUNDO_MVP)\b")
    permitidos = {Path("digilab/config.py"), Path("experiments/exportar_gabarito_mvp_produto.py"),
                  Path("tests/test_gabarito_mvp_produto_web.py"),
                  Path("experiments/run_v2_digibrain_prototipo.py")}     # PPM-3: a avaliacao do prototipo do modular roda no MVP
    citam = {p.relative_to(RAIZ) for pasta in ("digilab", "experiments", "tests", "tools") for p in (RAIZ / pasta).rglob("*.py")
             if nomes.search(p.read_text(encoding="utf-8"))}
    assert citam == permitidos
    assert E0.CM is CONFIG_MUNDO_LIGADA and CONFIG_MUNDO_LIGADA.layout is LAYOUT_MUNDO_PADRAO
