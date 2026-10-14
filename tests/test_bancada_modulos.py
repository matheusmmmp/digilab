"""A bancada em módulos (rodada de saúde, etapa 3; docs/TAREFA_V2_SAUDE.md): o pacote experiments/bancada/ e a fachada bancada_v2.

- G-AST: cada nó de topo do bancada_v2.py de antes (o commit de base do mapa) está, na mesma ordem, no módulo do mapa, com a AST igual,
  salvo a troca declarada; a fachada tem a docstring, as importações e o `if __name__` de antes.
- G-NOMES: a fachada tem exatamente os nomes do módulo de antes (os do mapa).
- A fachada propaga a atribuição aos módulos (o monkeypatch dos testes de antes), e o pacote importa sem ciclo, módulo a módulo.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tools"))
import bancada  # noqa: E402
import bancada_v2 as bv  # noqa: E402
import dividir_bancada as db  # noqa: E402

MAPA = json.loads((RAIZ / db.PROVA).read_text(encoding="utf-8"))


def _git_tem(commit: str) -> bool:
    return subprocess.run(["git", "-C", str(RAIZ), "cat-file", "-e", f"{commit}^{{commit}}"], capture_output=True).returncode == 0


@pytest.mark.skipif(not _git_tem(MAPA["base"]["commit"]), reason="o commit de base não está neste clone")
def test_g_ast_contra_o_commit_de_base():
    p = db.Particao(db.ler_fonte(MAPA["base"]["commit"]))
    mapa = db.conferir(p, MAPA["base"]["commit"])
    assert mapa == MAPA


def test_g_nomes():
    assert db.nomes_da_fachada() == set(MAPA["nomes"])


def test_modulos_do_pacote_e_do_mapa():
    assert tuple(db.MODULOS) == bancada.MODULOS
    assert {x["modulo"] for x in MAPA["nos"]} == set(bancada.MODULOS)
    for x in MAPA["nos"]:
        for nome in x["nome"].split(","):
            if nome in vars(bv):
                assert getattr(sys.modules[f"bancada.{x['modulo']}"], nome) is getattr(bv, nome)


def test_so_a_troca_declarada_muda():
    diferentes = [x for x in MAPA["nos"] if not x["igual"]]
    assert [x["nome"] for x in diferentes] == list(db.TROCAS)


def test_fachada_propaga_a_atribuicao(monkeypatch):
    original = bv.NOS_PENDENTES
    assert bancada.bracos.NOS_PENDENTES is original
    monkeypatch.setattr(bv, "NOS_PENDENTES", {"x": "y"})
    assert bancada.bracos.NOS_PENDENTES == {"x": "y"}
    monkeypatch.undo()
    assert bancada.bracos.NOS_PENDENTES is original and bv.NOS_PENDENTES is original


def test_fachada_propaga_nome_importado_em_varios_modulos(monkeypatch):
    original = bv.replace
    donos = [m for m in bancada.MODULOS if getattr(sys.modules[f"bancada.{m}"], "replace", None) is original]
    assert len(donos) > 1
    sentinela = object()
    bv.replace = sentinela
    try:
        assert all(sys.modules[f"bancada.{m}"].replace is sentinela for m in donos)
    finally:
        bv.replace = original
    assert all(sys.modules[f"bancada.{m}"].replace is original for m in donos)


@pytest.mark.parametrize("modulo", bancada.MODULOS)
def test_cada_modulo_importa_primeiro_sem_ciclo(modulo):
    codigo = f"import sys; sys.path.insert(0, {str(RAIZ / 'experiments')!r}); import bancada.{modulo}"
    r = subprocess.run([sys.executable, "-c", codigo], capture_output=True, cwd=RAIZ)
    assert r.returncode == 0, r.stderr.decode("utf-8", "replace")


def test_linha_de_comando_da_fachada():
    r = subprocess.run([sys.executable, str(RAIZ / "experiments" / "bancada_v2.py"), "--help"], capture_output=True, cwd=RAIZ)
    assert r.returncode == 0 and b"--config" in r.stdout
