"""CONVERSA_PET, M1 (D1, 2026-11-06): o livre-v9 (regras de verdade do livre-v2 + estilo da especie + comando) e o campo
`comando` do pedido da conversa. As versoes antigas nao mudam; sem o campo, a resposta e a de sempre (livre-v2)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "tests"))

from digilab_fala_livre.corpus import bloco_estilo, carregar  # noqa: E402
from digilab_fala_livre.fatos import fatos_de_estado  # noqa: E402
from digilab_fala_livre.prompt import (BLOCO_COMANDO_V8, SISTEMA, SISTEMA_V8, SISTEMA_V9, VERSAO_PROMPT_V8,  # noqa: E402
                                       VERSAO_PROMPT_V9, VERSOES, VERSOES_COMANDO, VERSOES_VOZ, mensagens)
from test_servidor_fala_livre import VOZ, _post, servidor  # noqa: E402,F401

PET = {"identidade": {"estagio": "adulto", "especie": "Amizade", "forma": "Angemon"},
       "estado": {"fome": 0.8, "humor": 0.7}, "vinculo": 0.6}
ROTA = "/api/fala-livre"


def test_livre_v9_regras_do_v2_estilo_e_comando():
    assert VERSAO_PROMPT_V9 == "livre-v9" and VERSAO_PROMPT_V9 in VERSOES and VERSAO_PROMPT_V9 in VERSOES_COMANDO
    assert VERSAO_PROMPT_V9 in VERSOES_VOZ                         # aceita o bloco de estilo
    regras = SISTEMA[SISTEMA.index("REGRAS DE VERDADE"):SISTEMA.index("JEITO DE FALAR")]
    assert regras in SISTEMA_V9                                    # as regras de verdade do v2, palavra por palavra
    assert "ESTILO DA ESPÉCIE" in SISTEMA_V9 and "COMANDO (só na conversa)" in SISTEMA_V9
    assert SISTEMA_V9.endswith(SISTEMA_V8[SISTEMA_V8.index("COMANDO (só na conversa)"):])
    assert "inventar" not in SISTEMA_V9.replace("não invente", "").replace("Não invente", "").replace("Nunca invente", "")


def test_livre_v9_mensagens_com_estilo_e_comando_e_recusa_fatos_de_voz():
    especies, _, _ = carregar()
    fatos = fatos_de_estado(PET)
    est = bloco_estilo(especies["Angemon"], None)
    m = mensagens(fatos, "conversa", "vai comer", versao=VERSAO_PROMPT_V9, estilo=est, comando=True)
    assert m[0]["content"] == SISTEMA_V9 and est in m[-1]["content"] and BLOCO_COMANDO_V8 in m[-1]["content"]
    for tipo_estado in (VOZ, {**PET, "mentira": {"regra": "demora", "verdade": "x", "molde": "y"}}, {**PET, "almanaque": {"id": "w"}}):
        try:
            fs = fatos_de_estado(tipo_estado)
        except Exception:                                          # estado que o proprio parser recusa tambem vale como recusa
            continue
        if any(f.id[0] in "HOPLFWA" for f in fs):
            with pytest.raises(ValueError):
                mensagens(fs, "conversa", "oi", versao=VERSAO_PROMPT_V9)
    assert any(f.id[0] == "O" for f in fatos_de_estado(VOZ))      # o VOZ tem fato O: recusado acima


def test_versoes_antigas_nao_mudam():
    assert SISTEMA_V8.count("COMANDO (só na conversa)") == 1 and "ESTILO DA ESPÉCIE" not in SISTEMA
    m = mensagens(fatos_de_estado(PET), "conversa", "oi", versao="livre-v8", comando=True)
    assert m[0]["content"] == SISTEMA_V8 and VERSAO_PROMPT_V8 in VERSOES


def test_servidor_comando_true_usa_livre_v9_estilo_e_devolve_o_comando(servidor):
    url, respostas, pedidos = servidor
    respostas += ['{"fala": "Vou comer!", "fatos_citados": [], "comando": "alimentar"}']
    cod, r = _post(url + ROTA, {"estado": PET, "situacao": "conversa", "fala_jogador": "vai comer", "semente": 3, "comando": True})
    assert cod == 200 and r["comando"] == "alimentar" and r["versao_prompt"] == "livre-v9" and r["erro"] is None
    assert r["especie_corpus"] == "Angemon"
    msg = pedidos[-1]["messages"]
    assert "ESTILO" in msg[-1]["content"] and "COMANDO:" in msg[-1]["content"] and "comando" in pedidos[-1]["format"]["required"]
    respostas += ['{"fala": "Vou lutar!", "fatos_citados": [], "comando": "lutar"}']
    cod, r = _post(url + ROTA, {"estado": PET, "situacao": "conversa", "fala_jogador": "vai lutar", "semente": 3, "comando": True})
    assert cod == 200 and r["comando"] is None and "fora do catalogo" in r["erro"]       # o catalogo fecha


def test_servidor_sem_o_campo_a_resposta_e_a_de_hoje(servidor):
    url, respostas, pedidos = servidor
    respostas += ['{"fala": "Oi.", "fatos_citados": []}']
    cod, r = _post(url + ROTA, {"estado": PET, "situacao": "conversa", "fala_jogador": "vai comer", "semente": 3})
    assert cod == 200 and r["comando"] is None and r["versao_prompt"] == "livre-v2" and "especie_corpus" not in r
    assert "comando" not in pedidos[-1]["format"]["properties"] and "ESTILO" not in pedidos[-1]["messages"][-1]["content"]
    respostas += ['{"fala": "Oi.", "fatos_citados": []}']
    cod, r = _post(url + ROTA, {"estado": PET, "situacao": "conversa", "fala_jogador": "vai comer", "semente": 3, "comando": False})
    assert cod == 200 and r["versao_prompt"] == "livre-v2"


@pytest.mark.parametrize("extra", [{"comando": "true"}, {"comando": 1}, {"comando": None}, {"comando": ["x"]},
                                   {"comando": True, "voz": True}])
def test_servidor_valida_o_campo_comando(servidor, extra):
    url, _, _ = servidor
    cod, r = _post(url + ROTA, {"estado": PET, "situacao": "conversa", "fala_jogador": "vai comer", "semente": 3, **extra})
    assert cod == 400 and "erro" in r


def test_servidor_comando_na_espontanea_e_recusado_e_fato_de_voz_no_estado_falha_alto(servidor):
    url, _, _ = servidor
    cod, _ = _post(url + ROTA, {"estado": PET, "situacao": "espontanea", "semente": 3, "comando": True})
    assert cod == 400
    cod, _ = _post(url + ROTA, {"estado": VOZ, "situacao": "conversa", "fala_jogador": "oi", "semente": 3, "comando": True})
    assert cod == 400                                              # a pagina nao traz a historia H/O/P/L pelo caminho do v9
    cod, _ = _post(url + ROTA, {"estado": "x", "situacao": "conversa", "fala_jogador": "oi", "semente": 3, "comando": True})
    assert cod == 400
