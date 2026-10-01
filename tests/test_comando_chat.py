"""Comando pelo chat (TAREFA_COMANDO_CHAT): parser, esquema, prompt livre-v7, gerador e rota do servidor.

A LLM so propoe uma acao do catalogo fechado (as 9 acoes do dono); fora dele o parser falha alto e o comando e None.
Os prompts anteriores nao mudam (os artefatos das rodadas 1-4 da voz reproduzem).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "tests"))

from digilab_fala_livre.fatos import fatos_de_estado  # noqa: E402
from digilab_fala_livre.gerar import gerar  # noqa: E402
from digilab_fala_livre.ollama import ClienteOllama  # noqa: E402
from digilab_fala_livre.prompt import (BLOCO_COMANDO, SISTEMA, SISTEMA_V3, SISTEMA_V4, SISTEMA_V5, SISTEMA_V6,  # noqa: E402
                                       SISTEMA_V7, VERSAO_PROMPT_V6, VERSAO_PROMPT_V7, VERSOES, VERSOES_VOZ,
                                       esquema, mensagens)
from digilab_fala_livre.revisao import gerar_com_revisao  # noqa: E402
from digilab_fala_livre.saida import CATALOGO_COMANDOS, FALA_GENERICA, SaidaInvalida, ler  # noqa: E402
from digilab_fala_livre.situacoes import MENSAGENS_COMANDO  # noqa: E402
from test_fala_livre import ESTADO, _falso  # noqa: E402
from test_servidor_fala_livre import VOZ, _post, servidor  # noqa: E402,F401

CATALOGO_WEB = ("alimentar", "limpar", "brincar", "acariciar", "elogiar", "repreender",
                "petisco", "levar_ao_banheiro", "tratar_lesao")


# ------------------------------------------------------------ catalogo e parser
def test_catalogo_e_o_acao_dono_do_jogo_web():
    """o catalogo fechado = AcaoDono de web/app/motor/tipos.ts (as 9 acoes; treino, luta e itens ficam fora)"""
    assert CATALOGO_COMANDOS == CATALOGO_WEB
    tipos = (RAIZ / "web" / "app" / "motor" / "tipos.ts").read_text(encoding="utf-8")
    for a in CATALOGO_WEB:
        assert f'"{a}"' in tipos.split("export type TracoCombate")[0]


@pytest.mark.parametrize("texto", ['{"fala": "Vou comer!", "fatos_citados": [], "comando": "treinar"}',
                                   '{"fala": "Vou comer!", "fatos_citados": [], "comando": "Alimentar"}',
                                   '{"fala": "Vou comer!", "fatos_citados": [], "comando": 1}',
                                   '{"fala": "Vou comer!", "fatos_citados": [], "comando": ["alimentar"]}',
                                   '{"fala": "Vou comer!", "fatos_citados": [], "comando": null, "x": 1}'])
def test_parser_falha_alto_com_comando_fora_do_catalogo(texto):
    with pytest.raises(SaidaInvalida):
        ler(texto)


def test_parser_aceita_null_e_ausencia_e_o_catalogo():
    assert ler('{"fala": "Tá bom.", "fatos_citados": [], "comando": null}').comando is None
    assert ler('{"fala": "Tá bom.", "fatos_citados": []}').comando is None           # espontanea: sem o campo
    for a in CATALOGO_COMANDOS:
        assert ler(json.dumps({"fala": "Vou!", "fatos_citados": [], "comando": a})).comando == a


# ------------------------------------------------------------ esquema e prompt
def test_esquema_com_comando_so_quando_pedido():
    sem = esquema("adulto")
    assert "comando" not in sem["properties"] and sem["required"] == ["fala", "fatos_citados"]
    com = esquema("adulto", comando=True)
    assert com["properties"]["comando"] == {"enum": [*CATALOGO_COMANDOS, None]}
    assert com["required"] == ["fala", "fatos_citados", "comando"]


def test_livre_v7_ao_lado_dos_anteriores_sem_mudar_os_anteriores():
    assert VERSAO_PROMPT_V7 in VERSOES and VERSAO_PROMPT_V7 in VERSOES_VOZ
    assert "COMANDO" in SISTEMA_V7 and '"comando"' in SISTEMA_V7
    for s in (SISTEMA, SISTEMA_V3, SISTEMA_V4, SISTEMA_V5, SISTEMA_V6):
        assert "comando" not in s.lower()
    assert SISTEMA_V7.split("COMANDO (só na conversa)")[0] == SISTEMA_V6.split("SAÍDA")[0]   # a v7 e a v6 + o comando


def test_bloco_comando_so_na_conversa_do_livre_v7():
    fatos = fatos_de_estado(VOZ)
    conv = mensagens(fatos, "conversa", "vai comer", versao=VERSAO_PROMPT_V7, comando=True)
    assert conv[0]["content"] == SISTEMA_V7 and BLOCO_COMANDO in conv[-1]["content"]
    for a, d in (("alimentar", "dar comida"), ("tratar_lesao", "tratar um machucado")):
        assert f"- {a}: {d}" in BLOCO_COMANDO
    esp = mensagens(fatos, "espontanea", versao=VERSAO_PROMPT_V7)
    assert "COMANDO:" not in esp[-1]["content"]
    with pytest.raises(ValueError):
        mensagens(fatos, "espontanea", versao=VERSAO_PROMPT_V7, comando=True)
    with pytest.raises(ValueError):
        mensagens(fatos, "conversa", "oi", versao=VERSAO_PROMPT_V6, comando=True)


# ------------------------------------------------------------ gerador e revisao
def test_gerar_devolve_o_comando_e_pede_o_esquema_com_enum():
    cap = []
    r = gerar(ClienteOllama("falso", abrir=_falso('{"fala": "Eba, comida!", "fatos_citados": [], "comando": "alimentar"}', cap)),
              VOZ, "conversa", "vai comer", semente=1, versao=VERSAO_PROMPT_V7, comando=True)
    assert r.comando == "alimentar" and r.erro is None and r.versao_prompt == "livre-v7"
    assert cap[0]["format"]["properties"]["comando"]["enum"][-1] is None and "comando" in cap[0]["format"]["required"]


def test_comando_fora_do_catalogo_vira_generica_com_comando_nulo():
    r = gerar(ClienteOllama("falso", abrir=_falso('{"fala": "Vou treinar!", "fatos_citados": [], "comando": "treinar"}', [])),
              VOZ, "conversa", "vai treinar", versao=VERSAO_PROMPT_V7, comando=True)
    assert r.fala == FALA_GENERICA and r.comando is None and r.erro.startswith("saida: comando fora do catalogo")


def test_sem_pedir_comando_o_campo_nunca_vem():
    r = gerar(ClienteOllama("falso", abrir=_falso('{"fala": "Oi.", "fatos_citados": [], "comando": "alimentar"}', [])),
              VOZ, "conversa", "oi", versao=VERSAO_PROMPT_V6)
    assert r.comando is None and r.erro is None


def test_revisao_mantem_o_comando_da_primeira_geracao():
    from test_servidor_fala_livre import _ollama_falso
    respostas = ['{"fala": "Tá, mas você nunca cuida de mim!", "fatos_citados": [], "comando": "alimentar"}',
                 '{"afirmacoes": [{"tipo": "apelo", "trecho": "você nunca cuida de mim"}]}',      # verificador
                 '{"fala": "Tá, vou comer.", "fatos_citados": [], "comando": null}',                  # reescrita
                 '{"afirmacoes": []}']
    cli = ClienteOllama("falso", abrir=_ollama_falso(respostas, []))
    r, tent = gerar_com_revisao(cli, VOZ, "conversa", 3, "vai comer", versao=VERSAO_PROMPT_V7, so_respeito=True,
                                versao_verificador="verif-v5", comando=True)
    assert r.fala == "Tá, vou comer." and r.comando == "alimentar" and len(tent) == 2


# ------------------------------------------------------------ servidor
def test_rota_devolve_o_comando_so_na_conversa_com_voz(servidor):
    url, respostas, pedidos = servidor
    respostas += ['{"fala": "Eba, comida!", "fatos_citados": [], "comando": "alimentar"}', '{"afirmacoes": []}']
    cod, r = _post(url + "/api/fala-livre", {"estado": VOZ, "situacao": "conversa", "fala_jogador": "vai comer",
                                             "semente": 3, "voz": True})
    assert cod == 200 and r["comando"] == "alimentar" and r["versao_prompt"] == "livre-v8" and r["erro"] is None
    assert pedidos[0]["format"]["properties"]["comando"]["enum"][0] == "alimentar" and "COMANDO" in pedidos[0]["messages"][-1]["content"]
    respostas += ['{"fala": "Oi!", "fatos_citados": []}', '{"afirmacoes": []}']
    cod, r = _post(url + "/api/fala-livre", {"estado": VOZ, "situacao": "espontanea", "semente": 3, "voz": True})
    assert cod == 200 and r["comando"] is None and r["versao_prompt"] == "livre-v6"
    assert "comando" not in pedidos[-1]["format"]["properties"]
    respostas += ['{"fala": "Oi.", "fatos_citados": []}']
    cod, r = _post(url + "/api/fala-livre", {"estado": ESTADO, "situacao": "conversa", "fala_jogador": "vai comer", "semente": 3})
    assert cod == 200 and r["comando"] is None and r["versao_prompt"] == "livre-v2"    # sem voz: como antes


def test_servidor_comando_fora_do_catalogo_vira_null(servidor):
    url, respostas, _ = servidor
    respostas += ['{"fala": "Vou lutar!", "fatos_citados": [], "comando": "lutar"}']
    cod, r = _post(url + "/api/fala-livre", {"estado": VOZ, "situacao": "conversa", "fala_jogador": "vai lutar",
                                             "semente": 3, "voz": True})
    assert cod == 200 and r["comando"] is None and r["fala"] == FALA_GENERICA and "fora do catalogo" in r["erro"]


# ------------------------------------------------------------ amostra da avaliacao
def test_mensagens_da_avaliacao_20_por_classe_e_esperado_no_catalogo():
    assert len(MENSAGENS_COMANDO) == 60 and len({m[0] for m in MENSAGENS_COMANDO}) == 60
    for texto, classe, esperado in MENSAGENS_COMANDO:
        assert classe in ("imperativo", "negativa", "conversa") and 0 < len(texto) <= 300
        assert (esperado in CATALOGO_COMANDOS) if classe == "imperativo" else esperado is None
    assert {m[2] for m in MENSAGENS_COMANDO if m[1] == "imperativo"} == set(CATALOGO_COMANDOS)   # toda acao aparece


# ------------------------------------------------------------ livre-v8 (rodada 3 do comando)
def test_livre_v8_so_muda_o_bloco_comando():
    from digilab_fala_livre.prompt import (BLOCO_COMANDO_V8, DESCRICAO_COMANDOS, DESCRICAO_COMANDOS_V8, SISTEMA_V8,
                                           VERSAO_PROMPT_V8, VERSOES_COMANDO)
    assert VERSAO_PROMPT_V8 in VERSOES and VERSAO_PROMPT_V8 in VERSOES_VOZ and VERSOES_COMANDO == (VERSAO_PROMPT_V7, VERSAO_PROMPT_V8)
    # o sistema: igual a v7 fora da regra do COMANDO
    antes, depois = SISTEMA_V7.split("Na conversa pode vir um bloco COMANDO")[0], SISTEMA_V7.split("Nunca invente uma ação fora da lista.")[1]
    assert SISTEMA_V8.startswith(antes) and SISTEMA_V8.endswith(depois) and SISTEMA_V8 != SISTEMA_V7
    for trecho in ('"elogiar"', '"repreender"', '"acariciar"', '"tratar_lesao"', "hipótese", "deixou para depois"):
        assert trecho in SISTEMA_V8
    # a lista: so as quatro acoes em que a mensagem e a propria acao mudam
    mudaram = {k for (k, a), (_, b) in zip(DESCRICAO_COMANDOS, DESCRICAO_COMANDOS_V8) if a != b}
    assert mudaram == {"elogiar", "repreender", "acariciar", "tratar_lesao"}
    fatos = fatos_de_estado(VOZ)
    v8 = mensagens(fatos, "conversa", "muito bem!", versao=VERSAO_PROMPT_V8, comando=True)
    v7 = mensagens(fatos, "conversa", "muito bem!", versao=VERSAO_PROMPT_V7, comando=True)
    assert v8[0]["content"] == SISTEMA_V8 and BLOCO_COMANDO_V8 in v8[-1]["content"] and BLOCO_COMANDO not in v8[-1]["content"]
    assert v7[0]["content"] == SISTEMA_V7 and BLOCO_COMANDO in v7[-1]["content"]          # a v7 nao muda
    assert v8[-1]["content"].replace(BLOCO_COMANDO_V8, "") == v7[-1]["content"].replace(BLOCO_COMANDO, "")
    with pytest.raises(ValueError):
        mensagens(fatos, "espontanea", versao=VERSAO_PROMPT_V8, comando=True)


def test_rodada3_do_comando_com_sementes_novas_e_livre_v8():
    from digilab_fala_livre.avaliacao import RODADAS_COMANDO
    r1, r3 = RODADAS_COMANDO[1], RODADAS_COMANDO[3]
    assert r3["prompt"] == "livre-v8" and r3["estilo"] is False and r1["prompt"] == "livre-v7"
    usadas = {s for k, r in RODADAS_COMANDO.items() if k != 3 for s in r["sementes"]}
    # a mensagem i usa semente + i: nenhuma semente da rodada 3 cai em nenhuma semente das outras rodadas
    n = len(MENSAGENS_COMANDO)
    assert not {s + i for s in r3["sementes"] for i in range(n)} & {s + i for s in usadas for i in range(n)}


def test_rodada4_do_comando_com_estilo_e_sementes_novas():
    """GPU-ESTILO (docs/PLANO_ANALISE_V2_GPU_ESTILO.md): livre-v8 com o estilo da especie, pasta propria, sementes reservadas
    pelo coordenador (20261501/1601/1701); semente + i de nenhuma mensagem cai nas rodadas 1-3; as rodadas 1-3 nao mudam."""
    from digilab_fala_livre.avaliacao import RODADAS_COMANDO
    r4 = RODADAS_COMANDO[4]
    assert r4 == {"pasta": "rodada4_estilo", "sementes": (20261501, 20261601, 20261701), "estilo": True, "prompt": "livre-v8"}
    assert RODADAS_COMANDO[3] == {"pasta": "rodada3", "sementes": (20261201, 20261301, 20261401), "estilo": False, "prompt": "livre-v8"}
    assert RODADAS_COMANDO[2]["sementes"] == RODADAS_COMANDO[1]["sementes"] == (20261003, 20261004, 20261005)
    assert len({r["pasta"] for r in RODADAS_COMANDO.values()}) == 4
    n = len(MENSAGENS_COMANDO)
    usadas = {s + i for k, r in RODADAS_COMANDO.items() if k != 4 for s in r["sementes"] for i in range(n)}
    assert not {s + i for s in r4["sementes"] for i in range(n)} & usadas
