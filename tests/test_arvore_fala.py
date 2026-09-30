"""Arvore da especie da voz propria (digilab_fala_livre/arvore.py) = mapa de nomes do jogo web (nomes.ts)."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab_fala_livre.arvore import ARVORE, texto_arvore  # noqa: E402
from digilab_fala_livre.fatos import FatosInvalidos, fatos_de_estado  # noqa: E402
from digilab_fala_livre.verificador import tipo_de_fato_escondido  # noqa: E402


def _mapa_web() -> dict:
    fonte = (RAIZ / "web" / "app" / "motor" / "nomes.ts").read_text(encoding="utf-8")
    return json.loads(re.search(r"DIGIMON_DA_FORMA[^=]*=\s*(\{.*?\});", fonte).group(1))


def test_arvore_igual_ao_mapa_do_jogo():
    d = _mapa_web()
    for esp, a in ARVORE.items():
        assert d[f"{esp}_bebe"] == [a["bebe"], "In-Training"]
        assert [d[f"{esp}_crianca_{r}"][0] for r in ("sereno", "arisco")] == list(a["criancas"])
        chaves = [k for k in d if k.startswith(esp + "_")]
        linhas = [tuple(d[chaves[i + j]][0] for j in range(3)) for i, k in enumerate(chaves) if "_adolescente_" in k]
        assert linhas == list(a["linhas"])
        assert all(d[chaves[i + 1]][1] == "Ultimate" and d[chaves[i + 2]][1] == "Mega"
                   for i, k in enumerate(chaves) if "_adolescente_" in k)
    assert set(ARVORE) == {k.split("_")[0] for k in d}


def test_fato_a1_so_com_especie_do_jogo():
    ident = {"estagio": "crianca", "especie": "brasa", "forma": "Agumon"}
    fatos = fatos_de_estado({"identidade": ident, "arvore": True})
    assert [f.id for f in fatos][:2] == ["I1", "A1"] and fatos[1].texto == texto_arvore("brasa")
    assert "Greymon vira MetalGreymon e depois WarGreymon" in fatos[1].texto
    assert "A1" not in [f.id for f in fatos_de_estado({"identidade": ident})]
    for ruim in ({"identidade": {**ident, "especie": "Coragem"}, "arvore": True}, {"identidade": ident, "arvore": 1}):
        with pytest.raises(FatosInvalidos):
            fatos_de_estado(ruim)


@pytest.mark.parametrize("trecho", ["Agumon é um amigo meu", "ele evolui pra Greymon", "Agumon vira Greymon"])
def test_relacao_e_evolucao_em_opiniao_vao_ao_juiz(trecho):
    assert tipo_de_fato_escondido(trecho) is not None


def test_gatilhos_da_voz_sustentam_o_que_dizem():
    from digilab_fala_livre.verificador import RAIZES_GATILHO_VOZ, acao_do_gatilho
    fonte = (RAIZ / "web" / "app" / "src" / "voz.ts").read_text(encoding="utf-8")
    textos = set(re.findall(r'\w+: "([^"]+)"', fonte[fonte.index("TEXTO_GATILHO"):fonte.index("};", fonte.index("TEXTO_GATILHO"))]))
    assert set(RAIZES_GATILHO_VOZ) <= textos
    g1 = [{"id": "G1", "tipo": "evento agora", "texto": "o dono voltou depois de um tempo sumido"}]
    assert acao_do_gatilho("Você voltou", g1) == "G1" and acao_do_gatilho("Ontem lutei muito", g1) is None
