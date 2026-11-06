"""SPRITES_GERACAO, etapa G1 (docs/TAREFA_V3_SPRITES_GERACAO.md, secoes 3.1, 4.1 e 7): os gates e o conversor sobre arte sintetica.

Cada gate da secao 4.1 tem um caso que passa e um que falha alto (GateFalhou). O conversor e testado com quadros sinteticos. Os testes
que leem o remaster/ (fora do git: a ficha do Agumon e a carne de arte propria contra o derivado) pulam sem ele.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "tools" / "sprites_geracao"))
import converter as C  # noqa: E402
import ficha as F  # noqa: E402
import gates as G  # noqa: E402
import montar_candidato as M  # noqa: E402

REMASTER = RAIZ.parent / "remaster"
W, H, PE = 40, 24, 16
COR_A, COR_B = (200, 30, 30), (30, 30, 200)
COR_FORA = (1, 2, 3)


def idle0() -> np.ndarray:
    """Um Idle sintetico: corpo 8x6 opaco acabando no pe (linha 14) e uma sombra semitransparente de 3 linhas abaixo."""
    q = np.zeros((H, W, 4), np.uint8)
    q[PE - 5:PE + 1, 8:16] = (*COR_A, 255)
    q[PE + 1:PE + 4, 6:18] = (0, 0, 0, 90)
    return q


def ficha() -> dict:
    corpo = 8 * 6
    carne = F.CARNE_PALETA
    return {
        "digimon": "Sint", "caixa": [W, H], "pe_idle": PE, "orientacao": "perfil", "idle0_centro_x": F.centro_x_pe(idle0(), PE),
        "paleta": ["%02x%02x%02x" % c for c in (COR_A, COR_B)],
        "area": {"faixa": [0.9 * corpo, 1.1 * (corpo + 4)], "carne_max": 70.0},
        "ms_alvo": [200, 200, 200, 200, 100],
        "ms_limites": {"ciclo_min": 800, "ciclo_max": 1000, "quadro_max": 200},
        "tolerancias": {"centro_x_px": 2.0, "linhas_pe": 3},
        "carne": {"paleta": ["%02x%02x%02x" % c for c in carne], "canto": [20, 3], "canto_aproximado": False,
                  "sequencia": [{"ms": 200, "mordidas": 0, "farelo": 0}, {"ms": 200, "mordidas": 1, "farelo": 1},
                                {"ms": 200, "mordidas": 2, "farelo": 0}, {"ms": 200, "mordidas": 2, "farelo": 0},
                                {"ms": 100, "mordidas": 2, "farelo": 0}]},
    }


def clipe_bom(n: int = 5, ms=None, nome: str = "Comer") -> F.Clipe:
    base = idle0()
    base[PE - 5:PE + 1, 8:16] = (*COR_A, 255)
    qs = []
    for i in range(n):
        q = base.copy()
        if i % 2:
            q[PE - 5, 8:12] = (*COR_B, 255)             # um detalhe que muda de quadro para quadro
        qs.append(q)
    ms = ms or [200, 200, 200, 200, 100][:n]
    tag = {"name": nome, "from": 0, "to": n - 1, "direction": "forward"}
    return F.Clipe(nome, qs, list(ms), [(W, H)] * n, [False] * n, [False] * n, tag, [nome])


def objeto_bom(clipe: F.Clipe) -> F.Clipe:
    qs = []
    for i in range(len(clipe.quadros)):
        o = np.zeros((H, W, 4), np.uint8)
        o[3:5, 20:24] = (*F.CARNE_PALETA[1], 255)
        qs.append(o)
    return F.Clipe("Comer", qs, list(clipe.ms), list(clipe.fonte_caixa), [False] * len(qs), [False] * len(qs),
                   dict(clipe.tag), ["Comer"])


@pytest.fixture
def base():
    c = clipe_bom()
    return c, objeto_bom(c), ficha(), idle0()


def todos_passam(c, o, f, i0):
    G.g_pal(c, o, f); G.g_caixa(c, o, f); G.g_pe(c, f, i0); G.g_alfa(c, o, f); G.g_area(c, o, f); G.g_ms(c, o, f, True)


def test_base_sintetica_passa_em_todos(base):
    todos_passam(*base)


# ---- G-PAL
def test_g_pal_falha_com_cor_fora(base):
    c, o, f, i0 = base
    c.quadros[2][PE - 3, 9] = (*COR_FORA, 255)
    with pytest.raises(G.GateFalhou, match="G-PAL"):
        G.g_pal(c, o, f)


def test_g_pal_falha_com_cor_fora_na_carne(base):
    c, o, f, i0 = base
    o.quadros[1][3, 20] = (*COR_FORA, 255)
    with pytest.raises(G.GateFalhou, match="G-PAL"):
        G.g_pal(c, o, f)


# ---- G-CAIXA
def test_g_caixa_falha_com_caixa_diferente(base):
    c, o, f, i0 = base
    c.fonte_caixa[1] = (W - 1, H)
    with pytest.raises(G.GateFalhou, match="G-CAIXA"):
        G.g_caixa(c, o, f)


def test_g_caixa_falha_com_trim(base):
    c, o, f, i0 = base
    c.cortado[0] = True
    with pytest.raises(G.GateFalhou, match="G-CAIXA"):
        G.g_caixa(c, o, f)


def test_g_caixa_falha_com_pixel_opaco_na_borda(base):
    c, o, f, i0 = base
    c.quadros[3][0, 5] = (*COR_A, 255)
    with pytest.raises(G.GateFalhou, match="G-CAIXA"):
        G.g_caixa(c, o, f)


# ---- G-PE
def test_g_pe_falha_com_pe_fora_da_linha(base):
    c, o, f, i0 = base
    c.quadros[1] = np.roll(c.quadros[1], -1, axis=0)
    c.quadros[1][PE + 1:] = i0[PE + 1:]
    with pytest.raises(G.GateFalhou, match="G-PE"):
        G.g_pe(c, f, i0)


def test_g_pe_falha_com_sombra_diferente(base):
    c, o, f, i0 = base
    c.quadros[2][PE + 2, 7] = (0, 0, 0, 91)
    with pytest.raises(G.GateFalhou, match="sombra"):
        G.g_pe(c, f, i0)


def test_g_pe_falha_com_pixel_opaco_abaixo_do_pe(base):
    c, o, f, i0 = base
    c.quadros[0][PE + 1, 10] = (*COR_A, 255)
    with pytest.raises(G.GateFalhou, match="G-PE"):
        G.g_pe(c, f, i0)


def test_g_pe_falha_com_centro_x_longe(base):
    c, o, f, i0 = base
    q = c.quadros[4]
    q[PE - 5:PE + 1] = 0
    q[PE - 5:PE + 1, 12:20] = (*COR_A, 255)               # o corpo andou 4 px para a direita
    with pytest.raises(G.GateFalhou, match="centro x"):
        G.g_pe(c, f, i0)


# ---- G-ALFA
def test_g_alfa_falha_com_semitransparente_acima_do_pe(base):
    c, o, f, i0 = base
    c.quadros[2][PE - 6, 9] = (*COR_A, 238)
    with pytest.raises(G.GateFalhou, match="G-ALFA"):
        G.g_alfa(c, o, f)


def test_g_alfa_aceita_semitransparente_so_na_sombra(base):
    c, o, f, i0 = base                                      # a sombra (alfa 90, abaixo do pe) ja esta no quadro
    assert G.g_alfa(c, o, f)["semitransparentes_acima_do_pe"] == [0] * 5


def test_g_alfa_falha_com_alfa_na_carne(base):
    c, o, f, i0 = base
    o.quadros[0][3, 20, 3] = 128
    with pytest.raises(G.GateFalhou, match="G-ALFA"):
        G.g_alfa(c, o, f)


# ---- G-AREA
def test_g_area_falha_com_area_pequena(base):
    c, o, f, i0 = base
    c.quadros[1][PE - 5:PE - 1, 8:16] = 0
    c.quadros[1][PE - 5:PE - 1, 8:10] = (*COR_A, 255)
    with pytest.raises(G.GateFalhou, match="G-AREA"):
        G.g_area(c, o, f)


def test_g_area_falha_com_area_grande(base):
    c, o, f, i0 = base
    c.quadros[3][2:8, 0:20] = (*COR_A, 255)
    with pytest.raises(G.GateFalhou, match="G-AREA"):
        G.g_area(c, o, f)


def test_g_area_falha_com_carne_grande(base):
    c, o, f, i0 = base
    o.quadros[2][0:10, 0:10] = (*F.CARNE_PALETA[1], 255)
    with pytest.raises(G.GateFalhou, match="carne"):
        G.g_area(c, o, f)


# ---- G-MS
def test_g_ms_falha_com_ms_nao_inteiro(base):
    c, o, f, i0 = base
    c.ms[1] = 133.5
    with pytest.raises(G.GateFalhou, match="G-MS"):
        G.g_ms(c, o, f, True)


def test_g_ms_falha_com_quadro_longo(base):
    c, o, f, i0 = base
    c.ms = [400, 200, 200, 100, 100]
    o.ms = list(c.ms)
    with pytest.raises(G.GateFalhou, match="maximo"):
        G.g_ms(c, o, f, True)


def test_g_ms_falha_com_ciclo_curto_ou_longo(base):
    c, o, f, i0 = base
    c.ms = [100] * 5
    o.ms = list(c.ms)
    with pytest.raises(G.GateFalhou, match="ciclo"):
        G.g_ms(c, o, f, True)
    c.ms = [200, 200, 200, 200, 200, ]
    c.ms = [200] * 5 + [100]
    c.quadros.append(c.quadros[0]); o.quadros.append(o.quadros[0])
    o.ms = list(c.ms)
    c.fonte_caixa.append((W, H))
    with pytest.raises(G.GateFalhou, match="ciclo"):
        G.g_ms(c, o, f, True)


def test_g_ms_falha_com_objeto_diferente(base):
    c, o, f, i0 = base
    o.ms = [200, 200, 200, 100, 200]
    with pytest.raises(G.GateFalhou, match="Comer_objeto"):
        G.g_ms(c, o, f, True)


def test_g_ms_falha_com_direcao_ou_repeat(base):
    c, o, f, i0 = base
    c.tag["direction"] = "reverse"
    with pytest.raises(G.GateFalhou, match="forward"):
        G.g_ms(c, o, f, True)
    c.tag["direction"] = "forward"; c.tag["repeat"] = "1"
    with pytest.raises(G.GateFalhou, match="repeat"):
        G.g_ms(c, o, f, True)


def test_g_ms_falha_com_outra_tag_no_gerado_mas_nao_no_derivado(base):
    c, o, f, i0 = base
    c.tags_do_arquivo = ["Comer", "Feliz"]
    with pytest.raises(G.GateFalhou, match="so Comer"):
        G.g_ms(c, o, f, True)
    G.g_ms(c, o, f, False)                                  # o derivado carrega as tags do lote 1


# ---- G-CARGA (com um gerador de atlas de mentira)
def test_g_carga_passa_e_falha(tmp_path):
    ok = tmp_path / "ok.py"
    ok.write_text("import sys, json, pathlib\nd = pathlib.Path(sys.argv[sys.argv.index('--saida') + 1])\n"
                  "(d / 'digilab_atlas_up_clipes.json').write_text(json.dumps({'clipes_nomes': ['Idle', 'Comer']}))\n")
    assert "Comer" in G.gate_carga(tmp_path / "e", tmp_path / "s1", ok)["clipes_nomes"]
    quebrado = tmp_path / "q.py"
    quebrado.write_text("raise SystemExit('caixa diferente')\n")
    with pytest.raises(G.GateFalhou, match="G-CARGA"):
        G.gate_carga(tmp_path / "e", tmp_path / "s2", quebrado)
    sem = tmp_path / "sem.py"
    sem.write_text("import sys, json, pathlib\nd = pathlib.Path(sys.argv[sys.argv.index('--saida') + 1])\n"
                   "(d / 'digilab_atlas_up_clipes.json').write_text(json.dumps({'clipes_nomes': ['Idle']}))\n")
    with pytest.raises(G.GateFalhou, match="Comer"):
        G.gate_carga(tmp_path / "e", tmp_path / "s3", sem)


# ---- o conversor, com quadros sinteticos
def gerar_quadros(pasta: Path, n: int = 5, deslocado: bool = True, ms=None) -> None:
    """Quadros 'do gerador': o corpo sintetico, sem sombra, num canvas maior e fora do lugar (pe e x errados)."""
    pasta.mkdir(parents=True, exist_ok=True)
    itens = []
    for i in range(n):
        q = np.zeros((40, 50, 4), np.uint8)
        y0, x0 = (20, 30) if deslocado else (PE - 5, 8)
        q[y0:y0 + 6, x0:x0 + 8] = (*COR_A, 255)
        if i % 2:
            q[y0, x0:x0 + 4] = (*COR_B, 255)
        Image.fromarray(q).save(pasta / f"f{i:02d}.png")
        itens.append({"arquivo": f"f{i:02d}.png", "ms": (ms or [200, 200, 200, 200, 100])[i]})
    (pasta / "quadros.json").write_text(json.dumps({"quadros": itens}), encoding="utf-8")


def test_conversor_poe_o_pe_e_passa_nos_gates(tmp_path):
    gerar_quadros(tmp_path / "q")
    f, i0 = ficha(), idle0()
    C.converter_com_ficha("Sint", f, i0, tmp_path / "q", tmp_path / "export")
    c = F.ler_export(tmp_path / "export" / "Sint", "Comer")
    o = F.ler_export(tmp_path / "export" / "Sint_objeto", "Comer")
    assert c.fonte_caixa == [(W, H)] * 5 and not any(c.cortado) and not any(c.rotacionado)
    assert c.tag == {"name": "Comer", "from": 0, "to": 4, "direction": "forward", "color": "#000000ff"}
    assert c.ms == o.ms == [200, 200, 200, 200, 100]
    r = G.rodar("Sint", tmp_path / "export", f, i0, so_comer=True)
    assert r["passou"], {g: v.get("erro") for g, v in r["gates"].items() if not v["passou"]}
    # a sombra e a do Idle, byte a byte, e a carne e a da M1
    assert (c.quadros[0][PE + 1:] == i0[PE + 1:]).all()
    assert o.quadros[1][:, :, 3].max() == 255


def test_conversor_gera_carne_pela_sequencia_do_derivado(tmp_path):
    gerar_quadros(tmp_path / "q")
    f = ficha()
    C.converter_com_ficha("Sint", f, idle0(), tmp_path / "q", tmp_path / "export")
    o = F.ler_export(tmp_path / "export" / "Sint_objeto", "Comer")
    areas = [F.area_opaca(q) for q in o.quadros]
    assert areas[0] > areas[2]                              # a carne e mordida: perde pixels
    assert areas[1] > areas[2]                              # o farelo do quadro 1 e a carne inteira ainda


def test_conversor_falha_com_personagem_fora_da_caixa(tmp_path):
    gerar_quadros(tmp_path / "q")
    big = np.zeros((40, 50, 4), np.uint8)
    big[0:30, 0:40] = (*COR_A, 255)                         # 40x30 nao cabe numa caixa 24x20
    Image.fromarray(big).save(tmp_path / "q" / "f00.png")
    with pytest.raises(ValueError, match="fora da caixa"):
        C.converter_com_ficha("Sint", ficha(), idle0(), tmp_path / "q", tmp_path / "e")


def test_conversor_falha_com_alfa_intermediario(tmp_path):
    gerar_quadros(tmp_path / "q")
    q = np.array(Image.open(tmp_path / "q" / "f01.png"))
    q[20, 30, 3] = 120
    Image.fromarray(q).save(tmp_path / "q" / "f01.png")
    with pytest.raises(ValueError, match="alfa intermediario"):
        C.converter_com_ficha("Sint", ficha(), idle0(), tmp_path / "q", tmp_path / "e")


def test_conversor_falha_com_ms_invalido_e_arquivo_ausente(tmp_path):
    gerar_quadros(tmp_path / "q")
    j = json.loads((tmp_path / "q" / "quadros.json").read_text())
    j["quadros"][0]["ms"] = 0
    (tmp_path / "q" / "quadros.json").write_text(json.dumps(j))
    with pytest.raises(ValueError, match="ms invalido"):
        C.converter_com_ficha("Sint", ficha(), idle0(), tmp_path / "q", tmp_path / "e")
    j["quadros"][0]["ms"] = 100
    j["quadros"][1]["arquivo"] = "nao_existe.png"
    (tmp_path / "q" / "quadros.json").write_text(json.dumps(j))
    with pytest.raises(FileNotFoundError):
        C.converter_com_ficha("Sint", ficha(), idle0(), tmp_path / "q", tmp_path / "e")


def test_conversor_e_gates_acusam_cor_fora_da_paleta(tmp_path):
    gerar_quadros(tmp_path / "q")
    q = np.array(Image.open(tmp_path / "q" / "f02.png"))
    q[22, 32] = (*COR_FORA, 255)                            # o conversor nao mexe em cor: o gate levanta
    Image.fromarray(q).save(tmp_path / "q" / "f02.png")
    f, i0 = ficha(), idle0()
    C.converter_com_ficha("Sint", f, i0, tmp_path / "q", tmp_path / "export")
    r = G.rodar("Sint", tmp_path / "export", f, i0, so_comer=True)
    assert not r["passou"] and not r["gates"]["G-PAL"]["passou"]


def test_conversor_nao_escreve_em_acoes(tmp_path):
    with pytest.raises(SystemExit, match="acoes"):
        C.main(["--nome", "Agumon", "--quadros", str(tmp_path), "--saida", str(tmp_path / "acoes" / "export")])
    with pytest.raises(SystemExit, match="acoes"):
        M.montar(tmp_path, tmp_path, tmp_path / "remaster" / "acoes" / "export")


def test_campos_do_json_batem_com_o_formato_do_atlas(tmp_path):
    gerar_quadros(tmp_path / "q")
    C.converter_com_ficha("Sint", ficha(), idle0(), tmp_path / "q", tmp_path / "export")
    j = json.loads((tmp_path / "export" / "Sint.json").read_text())
    assert isinstance(j["frames"], list)                    # json_array, como o ler_folha do gerar_atlas_up_clipes.py espera
    for fr in j["frames"]:
        assert fr["rotated"] is False and fr["trimmed"] is False and isinstance(fr["duration"], int)
    assert [t["name"] for t in j["meta"]["frameTags"]] == ["Comer"]


# ---- a ficha e o derivado do Agumon (fora do git)
remaster = pytest.mark.skipif(not (REMASTER / "acoes" / "export" / "Agumon.json").exists(), reason="sem o remaster/ (fora do git)")


@remaster
def test_ficha_do_agumon():
    f = F.montar_ficha("Agumon", REMASTER)
    assert f["caixa"] == [94, 68] and f["pe_idle"] == 58
    assert f["ms_alvo"] == [133, 100, 67, 133, 100, 67, 133, 133]
    assert f["area"]["idle_min"] <= f["area"]["idle_max"]
    assert len(f["paleta"]) > 100 and len(set(f["paleta"])) == len(f["paleta"])


@remaster
def test_carne_de_arte_propria_bate_com_a_do_derivado():
    """Porta da carne do gerar.lua: sobre a sequencia do derivado, a camada comida sai igual ao export da M1, byte a byte."""
    f = F.montar_ficha("Agumon", REMASTER)
    d = F.ler_export(REMASTER / "acoes" / "export" / "Agumon_objeto", "Comer")
    for i, s in enumerate(f["carne"]["sequencia"]):
        img = np.zeros((68, 94, 4), np.uint8)
        C.desenhar_carne(img, s["mordidas"], f["carne"]["canto"][0], f["carne"]["canto"][1], bool(s["farelo"]), False, f"q{i}")
        assert (img == d.quadros[i]).all(), i


@remaster
def test_montar_candidato_so_com_derivado(tmp_path):
    n = M.montar(REMASTER, REMASTER.parent / "Assets", tmp_path / "candidato" / "export")
    assert n == 60
    c = F.ler_export(tmp_path / "candidato" / "export" / "Agumon", "Comer")
    assert c.tags_do_arquivo == ["Comer"]                   # sem o lote 1
    d = F.ler_export(REMASTER / "acoes" / "export" / "Agumon", "Comer")
    assert c.ms == d.ms and all((a == b).all() for a, b in zip(c.quadros, d.quadros))
