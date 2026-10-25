"""A chave e os gates de engenharia do DigiBrain modular (docs/TAREFA_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md, etapas 0 e 1a;
docs/ESPEC_DIGIBRAIN_MODULAR.md, secoes 4.1, 4.9 e 11):

- A chave: `ConfigDigibrain` desligada por padrao, com as subchaves da secao 11 e as duas da etapa 1a (`p1` e o controle do `g_apr`), e
  nada fora do pacote e do orquestrador do prototipo a le (o G2: com nada ligado, as vidas de hoje saem como no
  tests/test_gabarito_digibrain.py).
- O registro dos valores de partida (`ConfigDigibrainInatos`, o M-GEN): todo campo com status; a v13 so atras da chave.
- O M-ADAPT cumpre o `Protocol` `Politica`; os ganchos vazios (M-PERS, M-GEN, M-EXPR).
- O G-INT (pela AST: sem float, sem `/`, sem `math`, so a biblioteca padrao), a G-RECEPTOR (nenhum arquivo importa o digilab/corpo.py), o
  G-SEM-DIRECAO (a direcao do cheiro fica no motor: o pacote so le se ha cheiro) e o engine.py intacto (o preflight).
"""
from __future__ import annotations

import ast
import re
import sys
from dataclasses import fields, replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import run_arena  # noqa: E402

from digilab.config import (CONFIG_DIGIBRAIN, CONFIG_DIGIBRAIN_INATOS, CONFIG_DIGIBRAIN_LIGADA, PARAMETROS_DIGIBRAIN_INATOS,  # noqa: E402
                            VERSAO_PET_DIGIBRAIN, ConfigDigibrain, ConfigDigibrainInatos)
from digilab.digibrain import DigiBrain, DigibrainDesligado  # noqa: E402
from digilab.digibrain import ganchos  # noqa: E402
from digilab.policy import Politica  # noqa: E402
from digilab.protocol import ENGINE_SHA256_V0, sha256_engine  # noqa: E402

PACOTE = RAIZ / "digilab" / "digibrain"


# ------------------------------------------------------------ a chave
def test_a_chave_desligada_por_padrao_com_as_subchaves():
    assert CONFIG_DIGIBRAIN == ConfigDigibrain() and CONFIG_DIGIBRAIN.ligada is False and CONFIG_DIGIBRAIN_LIGADA.ligada is True
    c = CONFIG_DIGIBRAIN
    assert (c.modula_g_apr, c.p2, c.m_mem, c.persistencia, c.p1, c.controle_g_apr, c.g_apr_constante) == \
        (False, True, True, True, True, "nenhum", 0)
    for nome in ("ligada", "modula_g_apr", "p2", "m_mem", "persistencia", "p1"):
        with pytest.raises(TypeError):
            ConfigDigibrain(**{nome: 1})
    with pytest.raises(ValueError, match="controle_g_apr"):
        ConfigDigibrain(controle_g_apr="outro")
    with pytest.raises(ValueError, match="exige modula_g_apr"):
        ConfigDigibrain(ligada=True, controle_g_apr="embaralhado")
    with pytest.raises(ValueError, match="constante"):
        ConfigDigibrain(ligada=True, controle_g_apr="constante")
    with pytest.raises(ValueError, match="constante"):
        ConfigDigibrain(ligada=True, modula_g_apr=True, controle_g_apr="constante", g_apr_constante=900)
    with pytest.raises(ValueError, match="so com o controle constante"):
        ConfigDigibrain(ligada=True, g_apr_constante=900)
    assert ConfigDigibrain(ligada=True, controle_g_apr="constante", g_apr_constante=900).g_apr_constante == 900


def test_nada_fora_do_pacote_e_do_orquestrador_le_a_chave():
    """o G2: a chave nao chega ao motor, a bancada nem as ferramentas; so o config, o pacote e o orquestrador do prototipo"""
    nomes = re.compile(r"\b(ConfigDigibrain\w*|CONFIG_DIGIBRAIN\w*)\b|digilab\.digibrain|from \.digibrain|from \.\.digibrain")
    citam = {p.relative_to(RAIZ).as_posix() for pasta in ("digilab", "experiments", "tools") for p in (RAIZ / pasta).rglob("*.py")
             if nomes.search(p.read_text(encoding="utf-8"))}
    assert {c for c in citam if not c.startswith("digilab/digibrain/")} == {"digilab/config.py",
                                                                             "experiments/run_v2_digibrain_prototipo.py"}


def test_o_digibrain_so_existe_com_a_chave_ligada_e_e_a_v13():
    with pytest.raises(DigibrainDesligado):
        DigiBrain()
    with pytest.raises(DigibrainDesligado):
        DigiBrain(cfg_digibrain=replace(CONFIG_DIGIBRAIN_LIGADA, ligada=False))
    c = DigiBrain(cfg_digibrain=CONFIG_DIGIBRAIN_LIGADA)
    assert isinstance(c, Politica) and c.versao_pet == VERSAO_PET_DIGIBRAIN == 13 and c.estado_interno()["versao_pet"] == 13


def test_os_valores_de_partida_tem_status_e_um_lugar_por_modulo():
    campos = {f.name for f in fields(ConfigDigibrainInatos)}
    assert set(PARAMETROS_DIGIBRAIN_INATOS) == campos
    assert all(st in ("PROPOSTO", "DECIDIDO") and fonte for st, fonte in PARAMETROS_DIGIBRAIN_INATOS.values())
    assert PARAMETROS_DIGIBRAIN_INATOS["escala"][0] == "DECIDIDO" and CONFIG_DIGIBRAIN_INATOS.escala == 1024
    gen = ganchos.ParametrosInatos()
    assert set().union(*(set(gen.do_modulo(m)) for m in ganchos.CAMPOS_POR_MODULO)) == campos
    with pytest.raises(TypeError):
        ConfigDigibrainInatos(eta_d=0.5)
    with pytest.raises(ValueError, match="sinal|W0"):
        ConfigDigibrainInatos(w0=CONFIG_DIGIBRAIN_INATOS.w0[1:])


def test_os_ganchos_vazios():
    assert ganchos.Personalidade().faceta("curioso") == 0
    with pytest.raises(NotImplementedError, match="gancho vazio"):
        ganchos.Personalidade().mudar_faceta("curioso", 1, [])
    with pytest.raises(NotImplementedError, match="gancho vazio"):
        ganchos.Expressao().expressar({})
    with pytest.raises(KeyError):
        ganchos.ParametrosInatos().do_modulo("nenhum")


# ------------------------------------------------------------ o G-INT, a G-RECEPTOR, o G-SEM-DIRECAO e o preflight
ARQUIVOS = {"__init__.py", "_comum.py", "adapt.py", "afeto.py", "arb.py", "estado.py", "ganchos.py", "impulso.py", "mem.py", "plast.py",
            "sens.py"}


def _arvores():
    arquivos = sorted(PACOTE.glob("*.py"))
    assert {a.name for a in arquivos} == ARQUIVOS
    return [(a.name, ast.parse(a.read_text(encoding="utf-8"))) for a in arquivos]


def test_g_int_so_inteiros_pela_ast():
    for nome, arvore in _arvores():
        for no in ast.walk(arvore):
            assert not (isinstance(no, ast.Constant) and isinstance(no.value, float)), f"{nome}: float literal"
            assert not isinstance(no, ast.Div), f"{nome}: `/`"
            assert not (isinstance(no, ast.Name) and no.id == "float"), f"{nome}: float"
            if isinstance(no, ast.Import):
                assert all(a.name.split(".")[0] in sys.stdlib_module_names and a.name.split(".")[0] != "math" for a in no.names), nome
            elif isinstance(no, ast.ImportFrom) and no.level == 0:
                assert no.module.split(".")[0] in sys.stdlib_module_names and no.module.split(".")[0] != "math", nome


def test_g_receptor_nenhum_arquivo_importa_o_corpo():
    for nome, arvore in _arvores():
        for no in ast.walk(arvore):
            if isinstance(no, ast.ImportFrom):
                modulo = ("." * no.level) + (no.module or "")
                assert modulo not in ("..corpo", "digilab.corpo", "..motor_corpo", "digilab.motor_corpo") and not (
                    no.level == 2 and no.module is None and any(a.name in ("corpo", "motor_corpo") for a in no.names)), nome
            elif isinstance(no, ast.Import):
                assert all(a.name not in ("digilab.corpo", "digilab.motor_corpo") for a in no.names), nome


def test_g_sem_direcao_a_direcao_do_cheiro_fica_no_motor():
    """o pacote so pergunta se ha cheiro (`direcao_cheiro != 0`); nunca le a intensidade, o campo, as fontes nem as comidas do mundo, e do
    mundo so importa o `Alvo` e as acoes com alvo"""
    proibidos = {"cheiro", "fontes_de_cheiro", "comidas", "direcao_do_cheiro", "direcao_do_campo", "cheiro_em", "campo_em",
                 "alvos_do_olfato", "leitura_do_olfato", "direcao_em_8", "direcao_em_16", "olfato_comida", "olfato_comida_esq",
                 "olfato_comida_dir"}
    usos = 0
    for nome, arvore in _arvores():
        pais = {filho: pai for pai in ast.walk(arvore) for filho in ast.iter_child_nodes(pai)}
        for no in ast.walk(arvore):
            if isinstance(no, ast.ImportFrom) and no.level == 2 and no.module == "mundo":
                assert {a.name for a in no.names} <= {"Alvo", "ACOES_COM_ALVO"}, nome
            if isinstance(no, ast.Attribute):
                assert no.attr not in proibidos, f"{nome}: .{no.attr}"
                if no.attr == "direcao_cheiro":
                    pai = pais[no]
                    assert isinstance(pai, ast.Compare) and isinstance(pai.ops[0], ast.NotEq) and pai.comparators[0].value == 0, nome
                    usos += 1
            if isinstance(no, ast.Name):
                assert no.id not in proibidos - {"cheiro", "comidas"}, f"{nome}: {no.id}"
    assert usos == 2                                    # o M-SENS na decisao e o M-ADAPT na consequencia


def test_o_engine_intacto_e_o_pacote_so_com_a_biblioteca_padrao():
    assert sha256_engine() == ENGINE_SHA256_V0
    assert run_arena._imports_externos(RAIZ / "digilab") == set()
