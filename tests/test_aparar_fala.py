"""Fala que bate no limite de caracteres do esquema (o Ollama corta no meio da palavra): fica so a parte inteira."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "tests"))

from digilab_fala_livre.gerar import gerar  # noqa: E402
from digilab_fala_livre.ollama import ClienteOllama  # noqa: E402
from digilab_fala_livre.prompt import MAX_CHARS  # noqa: E402
from digilab_fala_livre.revisao import gerar_com_revisao  # noqa: E402
from digilab_fala_livre.saida import aparar  # noqa: E402
from test_fala_livre import _falso  # noqa: E402
from test_servidor_fala_livre import VOZ, _ollama_falso  # noqa: E402

BEBE = {**VOZ, "identidade": {"estagio": "bebe", "especie": "Coragem", "forma": "Koromon"}, "historia": []}


@pytest.mark.parametrize("fala,esperado", [
    ("M-mm! Já tô com fome! Vou co-c", "M-mm! Já tô com fome!"),        # ultimo fim de frase
    ("Ah... tá bom. Mas eu tô com mu", "Ah... tá bom."),
    ("Eu tô com muita fome mesmo e q", "Eu tô com muita fome mesmo e…"),  # sem fim de frase: ultimo espaco
    ("Eu tô com muita fome mesmo, qu", "Eu tô com muita fome mesmo…"),   # virgula pendurada sai
    ("Nh" + "a" * 28, "Nh" + "a" * 28),                                     # uma palavra so: fica
    ("Tô com fome! Vou comer agora!!", "Tô com fome! Vou comer agora!!"),  # termina em fim de frase: inteira
])
def test_aparar_no_limite_do_bebe(fala, esperado):
    assert len(fala) >= MAX_CHARS["bebe"] - 1 and len(fala) <= MAX_CHARS["bebe"]
    assert aparar(fala, MAX_CHARS["bebe"]) == esperado


def test_abaixo_do_limite_nao_muda():
    assert aparar("Vou co-c", MAX_CHARS["bebe"]) == "Vou co-c"
    assert aparar("Tô com fome! Vou co", 30) == "Tô com fome! Vou co"       # 19 caracteres, longe do limite


def test_gerar_apara_a_fala_cortada_e_a_revisao_tambem():
    cortada = "M-mm! Já tô com fome! Vou co-c"
    assert len(cortada) == MAX_CHARS["bebe"]
    r = gerar(ClienteOllama("falso", abrir=_falso(json.dumps({"fala": cortada, "fatos_citados": []}), [])), BEBE, "conversa", "vai comer")
    assert r.fala == "M-mm! Já tô com fome!" and r.erro is None
    respostas = [json.dumps({"fala": "Você nunca cuida de mim, seu…", "fatos_citados": []}),
                 '{"afirmacoes": [{"tipo": "apelo", "trecho": "Você nunca cuida de mim"}]}',
                 json.dumps({"fala": cortada, "fatos_citados": []}), '{"afirmacoes": []}']
    r2, _ = gerar_com_revisao(ClienteOllama("falso", abrir=_ollama_falso(respostas, [])), BEBE, "conversa", 1, "vai comer",
                              so_respeito=True, versao_verificador="verif-v5")
    assert r2.fala == "M-mm! Já tô com fome!"
