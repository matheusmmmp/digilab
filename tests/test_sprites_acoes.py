"""SPRITES_ACOES, missao M1 (docs/TAREFA_V3_SPRITES_ACOES.md, secao 3.4): o export do clipe Comer.

- O ancoras.json (versionado) e conferido sempre: os 60, os modos, as sequencias e os ms.
- O export gerado (remaster/acoes/export, fora do git) e conferido quando existe: a caixa igual a do export do UP, o pe, os ms inteiros
  maiores que 0, e o Comer e o Comer_objeto casando em quadros e em ms. Sem o remaster/, esses testes pulam com aviso.
So biblioteca padrao (o PNG e lido aqui mesmo).
"""
from __future__ import annotations

import json
import struct
import zlib
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
ANCORAS = RAIZ / "tools" / "sprites_acoes" / "ancoras.json"
REMASTER = RAIZ.parent / "remaster"
EXPORT_UP = REMASTER / "export"
EXPORT_ACOES = REMASTER / "acoes" / "export"
MODOS = {"par", "prova1", "desenhar"}


def ancoras() -> dict:
    return json.loads(ANCORAS.read_text(encoding="utf-8"))


def ler_png(caminho: Path) -> tuple[int, int, list[bytes]]:
    """PNG RGBA 8 bits sem entrelacamento (o que o Aseprite grava): devolve largura, altura e as linhas RGBA. Outro formato levanta."""
    dados = caminho.read_bytes()
    if dados[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{caminho}: nao e PNG")
    pos, idat, cab = 8, b"", None
    while pos < len(dados):
        n, tipo = struct.unpack(">I4s", dados[pos:pos + 8])
        corpo = dados[pos + 8:pos + 8 + n]
        if tipo == b"IHDR":
            cab = struct.unpack(">IIBBBBB", corpo)
        elif tipo == b"IDAT":
            idat += corpo
        pos += 12 + n
    w, h, prof, cor, _, _, entrel = cab
    if (prof, cor, entrel) != (8, 6, 0):
        raise ValueError(f"{caminho}: PNG {prof} bits, tipo {cor}, entrelacamento {entrel}; so RGBA 8 bits")
    cru, bpp, linha = zlib.decompress(idat), 4, w * 4
    linhas, ant = [], bytes(linha)
    for y in range(h):
        f = cru[y * (linha + 1)]
        bruto = bytearray(cru[y * (linha + 1) + 1:(y + 1) * (linha + 1)])
        for i in range(linha):
            a = bruto[i - bpp] if i >= bpp else 0
            b = ant[i]
            c = ant[i - bpp] if i >= bpp else 0
            if f == 1:
                bruto[i] = (bruto[i] + a) & 255
            elif f == 2:
                bruto[i] = (bruto[i] + b) & 255
            elif f == 3:
                bruto[i] = (bruto[i] + (a + b) // 2) & 255
            elif f == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                bruto[i] = (bruto[i] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
            elif f != 0:
                raise ValueError(f"{caminho}: filtro {f}")
        linhas.append(bytes(bruto))
        ant = bruto
    return w, h, linhas


def ultima_linha_opaca(linhas: list[bytes], x: int, y: int, w: int, h: int) -> int:
    """A ultima linha (relativa ao quadro) com algum pixel opaco no retangulo; -1 se vazio."""
    for yy in range(h - 1, -1, -1):
        ln = linhas[y + yy]
        if any(ln[(x + xx) * 4 + 3] for xx in range(w)):
            return yy
    return -1


def quadros_tag(j: dict, tag: str) -> list[dict]:
    t = {t["name"]: t for t in j["meta"]["frameTags"]}[tag]
    return j["frames"][t["from"]:t["to"] + 1]


# ---- o ancoras.json, sempre ----

def test_ancoras_60_e_modos():
    d = ancoras()
    assert d["status"] == "PROPOSTO"
    dig = d["digimon"]
    assert len(dig) == 60
    for n, e in dig.items():
        assert e["modo"] in MODOS, n
        assert e["provisorio"] == (e["modo"] == "desenhar"), n
        assert e["orientacao"] in ("perfil", "frente"), n
        w, h = e["caixa"]
        assert 0 < e["pe_idle"] < h, n
        bx, by = e["boca"]
        assert 0 <= bx < w and 0 <= by < h, n
        if "fonte" in e:   # um .aseprite derivado, fora do git, e a regra que o fez
            assert e["fonte"].startswith("acoes/bocas/") and e["fonte"].endswith(".aseprite"), n
            assert ("olhos_do_idle" in e) != ("boca_desenhada" in e), n
            if "olhos_do_idle" in e:   # os olhos do Idle nos quadros da boca
                o = e["olhos_do_idle"]
                assert e["idle"][0] <= o["idle"] <= e["idle"][1], n
                assert set(o["quadros"].values()) <= set(e["fechada"]) | set(e["aberta"]), n
            else:                      # a boca desenhada (SA-9) que ja abre e fecha pelo par
                assert e["modo"] == "par" and e["boca_desenhada"]["quadro_up"] >= 1, n
        if e["modo"] == "par":
            assert len(e["seq"]) > 0 and e["fechada"] and e["aberta"], n
            assert {q[0] for q in e["seq"]} <= set(e["fechada"]) | set(e["aberta"]), n
            for q, ms, mo, fa in e["seq"]:
                assert isinstance(ms, int) and ms > 0 and mo in (0, 1) and fa in (0, 1), n
        else:
            a, b = e["idle"]
            assert 1 <= a <= b, n
            assert 0 <= e["escala_inclinacao"] <= 1 and isinstance(e["recuo_carne"], int), n
    for linha in d["prova1"]:
        assert isinstance(linha[5], int) and linha[5] > 0
    desl = d["carne_deslocamento"]
    assert set(desl) == {"perfil", "frente"}
    assert all(len(v) == 2 and all(isinstance(c, int) for c in v) for v in desl.values())


# ---- o export gerado, quando existe ----

def exige_export():
    if not EXPORT_ACOES.exists() or not EXPORT_UP.exists():
        pytest.skip(f"sem {EXPORT_ACOES} ou {EXPORT_UP}: o export das acoes fica fora do git (rode tools/sprites_acoes/gerar_acoes.py)")


@pytest.fixture(scope="module")
def nomes():
    return sorted(ancoras()["digimon"])


def test_export_existe_para_os_60(nomes):
    exige_export()
    faltam = [f"{n}{s}.{x}" for n in nomes for s in ("", "_objeto") for x in ("png", "json")
              if not (EXPORT_ACOES / f"{n}{s}.{x}").exists()]
    assert not faltam


def test_caixa_ms_e_objeto(nomes):
    exige_export()
    for n in nomes:
        up = json.loads((EXPORT_UP / f"{n}.json").read_text())
        caixa = (up["frames"][0]["sourceSize"]["w"], up["frames"][0]["sourceSize"]["h"])
        acao = json.loads((EXPORT_ACOES / f"{n}.json").read_text())
        obj = json.loads((EXPORT_ACOES / f"{n}_objeto.json").read_text())
        for j in (acao, obj):
            assert [t["name"] for t in j["meta"]["frameTags"]] == ["Comer"], n
            for f in j["frames"]:
                assert not f["trimmed"] and not f["rotated"], n
                assert (f["sourceSize"]["w"], f["sourceSize"]["h"]) == caixa, n
                assert (f["frame"]["w"], f["frame"]["h"]) == caixa, n
                assert isinstance(f["duration"], int) and f["duration"] > 0, n
        qa, qo = quadros_tag(acao, "Comer"), quadros_tag(obj, "Comer")
        assert len(qa) == len(qo) > 0, n
        assert [f["duration"] for f in qa] == [f["duration"] for f in qo], n


def test_pe_e_carne(nomes):
    """Nenhum quadro do Comer desce abaixo do pe do Idle do UP (sombra e personagem, como no export), e a carne aparece em todos."""
    exige_export()
    for n in nomes:
        up = json.loads((EXPORT_UP / f"{n}.json").read_text())
        _, _, lup = ler_png(EXPORT_UP / f"{n}.png")
        pe = max(ultima_linha_opaca(lup, f["frame"]["x"], f["frame"]["y"], f["frame"]["w"], f["frame"]["h"])
                 for f in quadros_tag(up, "Idle"))
        acao = json.loads((EXPORT_ACOES / f"{n}.json").read_text())
        _, _, la = ler_png(EXPORT_ACOES / f"{n}.png")
        for f in quadros_tag(acao, "Comer"):
            r = f["frame"]
            assert 0 <= ultima_linha_opaca(la, r["x"], r["y"], r["w"], r["h"]) <= pe, (n, f["filename"])
        obj = json.loads((EXPORT_ACOES / f"{n}_objeto.json").read_text())
        _, _, lo = ler_png(EXPORT_ACOES / f"{n}_objeto.png")
        for f in quadros_tag(obj, "Comer"):
            r = f["frame"]
            assert ultima_linha_opaca(lo, r["x"], r["y"], r["w"], r["h"]) >= 0, (n, f["filename"], "sem carne")
