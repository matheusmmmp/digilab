"""O adendo 3 do I7 da INDIVIDUALIDADE (docs/PLANO_ANALISE_V3_INDIVIDUALIDADE_I7.md, secao 16): a trava, os grupos, os niveis, o Delta, a
leitura da 16.4 em ICs sinteticos e o estado do original no momento, numa vida curta com as sementes dos testes."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import run_v3_individualidade_i7_ad3 as a3  # noqa: E402


def _plano() -> str:
    return (RAIZ / a3.PLANO).read_text(encoding="utf-8")


def test_a_trava():
    texto = _plano()
    assert any(x.startswith(a3.MARCA_ADENDO) for x in texto.splitlines()[:40])
    com = texto if a3.TITULO_REGISTRO in texto else texto + f"\n{a3.TITULO_REGISTRO}\n\no registro.\n"
    a3.exigir_plano(com, "candidatos")
    if a3.MARCA_NIVEIS not in com[com.index(a3.TITULO_REGISTRO):]:
        with pytest.raises(RuntimeError, match="niveis"):
            a3.exigir_plano(com, "leitura")
    a3.exigir_plano(com + f"\n{a3.MARCA_NIVEIS}: as medianas.\n", "leitura")
    with pytest.raises(RuntimeError, match="DECIDIDO"):
        a3.exigir_plano(com.replace(a3.MARCA_ADENDO, "**O adendo 3 (seção 16) está PROPOSTO"), "candidatos")


def test_os_grupos_de_um_pet():
    seq = lambda *v: {"SEQ": list(v)}  # noqa: E731
    p = {"perfis": {("N", None): {d: seq(1, 1) for d in range(1, 7)}, ("G", None): {d: seq(1, 0) for d in range(1, 7)},
                    ("E", 2): {3: seq(1, 1), 4: seq(1, 1), 5: seq(1, 1), 6: seq(1, 1)},
                    ("R", 2): {3: seq(1, 0), 4: seq(0, 1), 5: seq(1, 0), 6: seq(1, 0)}},
         "parciais": {("E", 2): seq(1, 1), ("R", 2): seq(1, 0), ("N", 2): seq(1, 1), ("G", 2): seq(1, 0)}}
    g = a3.grupos_do_pet(p, ("E", "R"), idades=(2,), janela=4, dias=6)
    assert g[("E", 2)] == {"grupo": "absorve", "imediato_zero": True}
    assert g[("R", 2)] == {"grupo": "afasta", "imediato_zero": False}


def _c(**k):
    base = {"amostra": "descoberta", "braco": "REL", "dono": "atencioso", "semente": 1, "idade": 2, "energia": 0.5, "fome": 0.5,
            "humor": 0.5, "acao": "dormir"}
    return {**base, **k}


def test_os_niveis_e_o_delta():
    linhas = [_c(semente=1, energia=0.2), _c(semente=2, energia=0.4), _c(semente=3, energia=0.6, acao="explorar")]
    grupos = {("descoberta", "REL", "atencioso", s, b, 2): {"grupo": g, "imediato_zero": False}
              for s, g in ((1, "afasta"), (2, "absorve"), (3, "misto")) for b in ("E", "R")}
    nv = a3.niveis_da_descoberta(linhas, grupos)
    assert nv["medianas"]["energia"] == pytest.approx(0.3) and nv["acao_mais_comum"] == "dormir"   # o misto fica fora
    regs = a3.registros(linhas, grupos, "descoberta", "E")
    assert [r["semente"] for r in regs] == [1, 2]
    assert a3.delta(regs, "C-ENERGIA", nv) == pytest.approx(1.0)       # energia baixa: 1/1 se afasta; alta: 0/1
    assert a3.delta(regs, "C-BRACO", nv) is None                       # nenhum REL+F: um nivel vazio


def test_a_leitura_da_16_4():
    sim, nao, neg = [0.1, 0.3], [-0.1, 0.1], [-0.3, -0.1]
    ics = {"C-ENERGIA": {"descoberta|E": sim, "descoberta|R": sim, "confirmacao|E": sim},
           "C-FOME": {"descoberta|E": sim, "descoberta|R": sim, "confirmacao|E": nao},
           "C-HUMOR": {"descoberta|E": sim, "descoberta|R": neg, "confirmacao|E": sim},
           "C-DONO": {"descoberta|E": nao, "descoberta|R": nao, "confirmacao|E": neg}}
    le = a3.leitura(ics)
    assert le["C-ENERGIA"] == "separa"
    assert le["C-FOME"].startswith("so na descoberta")
    assert le["C-HUMOR"] == "nao separa nesta analise"
    assert le["C-DONO"] == "separa"                                     # so a confirmacao (D-IND-AD3-2)
    assert a3.lado(None) == 0


def test_o_estado_no_momento_e_antes_do_tapa():
    import run_v2_memoria_autobio as ma
    import sondas_individualidade as so
    import run_v3_individualidade_i5 as i5
    from run_v2_digibrain_prototipo import LogDeEventos, reproduzir_mundo
    motor, *_ = ma.viver("REL", "atencioso", a3.r7.LUGAR, 101, 4, a3.ORCAMENTO_POR_DIA)
    texto = motor.log.para_jsonl()
    fp, fm = i5.fabricas_vida("REL", "atencioso", 101, 4, a3.ORCAMENTO_POR_DIA)
    mot = reproduzir_mundo(LogDeEventos.de_jsonl(texto), fp, semente=101, fabrica_motor=fm)
    tick = next(t for _, t in so.momentos(mot, 3) if t is not None)
    e = a3.estado_no_momento("REL", "atencioso", 101, texto, tick)
    assert set(e) == {"energia", "fome", "humor", "acao"} and all(0.0 <= e[d] <= 1.0 for d in a3.DRIVES)
