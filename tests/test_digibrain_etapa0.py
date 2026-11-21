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
    """o G2: a chave nao chega ao motor, a bancada nem as ferramentas; so o config, o pacote, o orquestrador do prototipo e o exportador
    do gabarito do modular para a web (LM0, #543: monta a config do braco REL pelo orquestrador; desvio de 2026-11-03)"""
    # a base neutra (digilab/digibrain/base.py, LIMPEZA LZ2: as contas inteiras e a interface do corpo) nao e a chave: importar so ela
    # nao conta
    nomes = re.compile(r"\b(ConfigDigibrain\w*|CONFIG_DIGIBRAIN\w*)\b|digilab\.digibrain(?!\.base\b)|from \.digibrain(?!\.base\b)|"
                       r"from \.\.digibrain(?!\.base\b)")
    citam = {p.relative_to(RAIZ).as_posix() for pasta in ("digilab", "experiments", "tools") for p in (RAIZ / pasta).rglob("*.py")
             if nomes.search(p.read_text(encoding="utf-8"))}
    assert {c for c in citam if not c.startswith("digilab/digibrain/")} == {"digilab/config.py",
                                                                             "experiments/run_v2_digibrain_prototipo.py",
                                                                             "experiments/exportar_gabarito_digibrain_modular.py",
                                                                             # a AN0 (#575): so le as constantes (CONFIG_DIGIBRAIN_INATOS, RECEPTORES_DIGIBRAIN); nenhuma vida
                                                                             "experiments/medir_v3_acoes_novas_hoje.py",
                                                                             # a DC1 (2026-11-06): o gabarito do decodificador de conceitos le o motivo; nenhuma vida
                                                                             "experiments/exportar_decodificador.py",
                                                                             # a DC3 (#672, #679, #686): o orquestrador da run unica monta o LAB e o LAB+F; a calibracao
                                                                             # do ganho_conteudo so le as constantes; o exportador do gabarito da fala_unidades para a web
                                                                             "experiments/run_v3_conversa_dc3.py", "experiments/calibrar_ganho_conteudo_dc3.py",
                                                                             "experiments/exportar_gabarito_fala_unidades.py",
                                                                             # GOSTO_VISUAL, P1f: o exportador do gabarito do olhar para a web (o laboratorio com o olhar)
                                                                             "experiments/exportar_gosto_visual.py", "experiments/exportar_gabarito_corpo_chaves.py",
                                                                             # GOSTO_VISUAL, P1e: o orquestrador da GV3 (o laboratorio com o olhar)
                                                                             "experiments/run_v3_gosto_visual.py",
                                                                             # a DC4a (e6da35cc): as entradas da avaliacao da voz so importam o decodificador; nenhuma vida
                                                                             "experiments/entradas_dc4.py",
                                                                             # COOPERACAO, CO6a: o gabarito das vidas do grupo com o modular (o braco REL pelo orquestrador)
                                                                             "experiments/exportar_gabarito_co6.py",
                                                                             # COOPERACAO, CO7b: o gabarito do G-PAR-CO7 (o modular com a CO7 no grupo)
                                                                             "experiments/exportar_gabarito_co7_par.py",
                                                                             # GOSTO_VISUAL, a TV no jogo (#883): o exportador do gabarito, que faltava aqui (D-CO7b-9)
                                                                             "experiments/exportar_tv_jogo.py",
                                                                             # COOPERACAO, CB1: a bancada da cooperacao (o modular nos dois pets do grupo)
                                                                             "experiments/run_v3_cooperacao_bancada.py",
                                                                             # GOSTO_VISUAL, a fala do assistir (FA-2): o gabarito do dec-v4 (vidas curtas da GV3b
                                                                             # nas sementes dos testes, pelo orquestrador da GV3; o decodificador so le)
                                                                             "experiments/exportar_decodificador_v4.py",
                                                                             # VALUATION, a ablacao do Valuation (V2): os bracos montam o REL da C4
                                                                             # com uma mudanca so (docs/PLANO_ANALISE_V3_VALUATION.md, secao 3)
                                                                             "experiments/run_v3_valuation.py",
                                                                             # VALUATION, o conserto (V3): o REL da C4 com a guarda da fome no reflexo
                                                                             # (docs/PLANO_ANALISE_V3_VALUATION_CONSERTO.md, secao 2)
                                                                             "experiments/run_v3_valuation_conserto.py",
                                                                             # ELOGIO, etapa 2: as vidas dos bracos (o modular REL com a ConfigElogio)
                                                                             "experiments/elogio.py",
                                                                             # PET_VIVO, o codigo do PV-2: as vidas dos bracos (o REL com a ConfigPV2 e o orgao)
                                                                             "experiments/pv2.py",
                                                                             # PET_VIVO, o codigo do PV-2: a medicao nas sementes dos testes (le o CONFIG_DIGIBRAIN_INATOS)
                                                                             "experiments/medir_pv2.py",
                                                                             # a run do PV-2 (o adendo 2): so le a escala dos inatos e o
                                                                             # DigiBrain das vidas do pv2.py (D-PV2R-1)
                                                                             "experiments/run_v3_pet_vivo_pv2.py",
                                                                             # o PET_VIVO SONO (#1041): o replay monta o modular; faltava aqui (o teste falhava na main)
                                                                             "experiments/run_v3_pet_vivo_sono.py",
                                                                             # o PET_VIVO recompensa (#1050): as vidas dos bracos e o orquestrador montam o modular;
                                                                             # faltavam aqui (o teste falhava na main, a5b1f76a)
                                                                             "experiments/recompensa.py", "experiments/run_v3_pet_vivo_recompensa.py",
                                                                             # ELOGIO, etapas 4 e 5: o orquestrador da calibracao e da validacao
                                                                             "experiments/run_v3_elogio.py",
                                                                             # SOCIAL_PAR, A0 (D-SP-29): o orquestrador monta o pet de hoje (o modular com a CO7)
                                                                             "experiments/run_v3_social_par_a0.py", "experiments/run_v3_corpo.py", "experiments/run_v3_corpo_c3.py",
                                                                             # a CORPO V1-a: o pet v38 da PET_VIVO no motor da sonda, com as chaves do corpo do braco (D-V1A-2)
                                                                             "experiments/run_v3_corpo_v1.py",
                                                                             # o PET_VIVO, o teste de recompensa (#1050): as vidas e o orquestrador so leem o CONFIG_DIGIBRAIN_INATOS (a escala e o
                                                                             # lambda_sono); faltavam aqui (o teste falhava na main), acrescentados no PR do codigo da CORPO V1-a
                                                                             "experiments/recompensa.py", "experiments/run_v3_pet_vivo_recompensa.py",
                                                                             # a SOCIAL_PAR MD1: o orquestrador da medida monta os bracos do M1 e do M2
                                                                             "experiments/run_v3_social_par_md.py",
                                                                             "experiments/run_v3_corpo_acoplamento.py"}


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
ARQUIVOS = {"__init__.py", "_comum.py", "adapt.py", "afeto.py", "arb.py", "base.py", "decodificador.py", "dever.py", "estado.py", "ganchos.py", "impulso.py", "mem.py", "pers.py", "plast.py", "rastro.py",
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
    mundo so importa o `Alvo`, as acoes com alvo e os nomes dos candidatos do orgao. Com o PV-2 (a leitura da PV2-3, DECIDIDA em
    2026-11-09: o cerebro le o nivel e a variacao do que as narinas sentem, nunca a direcao), as narinas so se leem pelos nomes de
    RECEPTORES_OLFATO_COMIDA, no M-SENS (o nivel, a media) e no M-ADAPT (se ha cheiro depois, o maximo); a troca das narinas nao muda o
    que o M-SENS entrega (tests/test_pv2_codigo.py)"""
    proibidos = {"cheiro", "fontes_de_cheiro", "comidas", "direcao_do_cheiro", "direcao_do_campo", "cheiro_em", "campo_em",
                 "alvos_do_olfato", "leitura_do_olfato", "direcao_em_8", "direcao_em_16", "olfato_comida", "olfato_comida_esq",
                 "olfato_comida_dir"}
    usos = 0
    leem_narinas = []
    for nome, arvore in _arvores():
        pais = {filho: pai for pai in ast.walk(arvore) for filho in ast.iter_child_nodes(pai)}
        for no in ast.walk(arvore):
            if isinstance(no, ast.ImportFrom) and no.level == 2 and no.module == "mundo":
                assert {a.name for a in no.names} <= {"Alvo", "ACOES_COM_ALVO", "CANDIDATOS_CHEIRO_ORGAO"}, nome
            if isinstance(no, ast.Attribute):
                assert no.attr not in proibidos, f"{nome}: .{no.attr}"
                if no.attr == "direcao_cheiro":
                    pai = pais[no]
                    assert isinstance(pai, ast.Compare) and isinstance(pai.ops[0], ast.NotEq) and pai.comparators[0].value == 0, nome
                    usos += 1
            if isinstance(no, ast.Name):
                assert no.id not in proibidos - {"cheiro", "comidas"}, f"{nome}: {no.id}"
                if no.id == "RECEPTORES_OLFATO_COMIDA" and isinstance(no.ctx, ast.Load):
                    funcao = pais[no]
                    while not isinstance(funcao, (ast.FunctionDef, ast.Module)):
                        funcao = pais[funcao]
                    leem_narinas.append((nome, getattr(funcao, "name", None)))
            if isinstance(no, ast.Constant) and no.value in ("olfato_comida_esq", "olfato_comida_dir"):
                assert nome == "sens.py", f"{nome}: o nome de uma narina fora do M-SENS"
    # o M-SENS na decisao, a conferencia do PV-2 no M-SENS (o mundo nao manda a direcao com o orgao) e o M-ADAPT na consequencia
    assert usos == 3
    assert sorted(set(leem_narinas)) == [("adapt.py", "_ha_cheiro_depois"), ("sens.py", "_ler_olfato"), ("sens.py", "_receptores")]


def test_o_engine_intacto_e_o_pacote_so_com_a_biblioteca_padrao():
    assert sha256_engine() == ENGINE_SHA256_V0
    assert run_arena._imports_externos(RAIZ / "digilab") == set()
