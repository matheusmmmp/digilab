"""A etapa 0 do DigiBrain modular (docs/TAREFA_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md; docs/ESPEC_DIGIBRAIN_MODULAR.md, secoes 4.1 e 11): a
chave desligada, o esqueleto do pacote digilab/digibrain/ e os gates de engenharia que valem desde ja.

- A chave: `ConfigDigibrain` desligada por padrao, com as subchaves da secao 11, e nada fora do pacote a le (o G2: com nada ligado, as
  vidas de hoje saem como no tests/test_gabarito_digibrain.py).
- O M-ADAPT cumpre o `Protocol` `Politica`, falha alto como a secao 4.1 pede e so encaminha (conferido com modulos de mentira); os modulos
  levantam NotImplementedError.
- O G-INT (pela AST: sem float, sem `/`, sem `math`, so a biblioteca padrao), a G-RECEPTOR (nenhum arquivo importa o digilab/corpo.py) e
  o engine.py intacto (o preflight).
"""
from __future__ import annotations

import ast
import random
import re
import sys
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import run_arena  # noqa: E402

from digilab.config import CONFIG_DIGIBRAIN, CONFIG_DIGIBRAIN_LIGADA, ConfigDigibrain  # noqa: E402
from digilab.digibrain import DigiBrain, DigibrainDesligado, Intencao, Modulos  # noqa: E402
from digilab.digibrain import afeto, arb, estado, ganchos, impulso, mem, plast, sens  # noqa: E402
from digilab.events import AcaoPet, AcaoUsuario  # noqa: E402
from digilab.mundo import Alvo  # noqa: E402
from digilab.policy import Politica, Transicao  # noqa: E402
from digilab.protocol import ENGINE_SHA256_V0, sha256_engine  # noqa: E402

PACOTE = RAIZ / "digilab" / "digibrain"
OBS = SimpleNamespace(corpo=object(), mundo=object())


# ------------------------------------------------------------ a chave
def test_a_chave_desligada_por_padrao_com_as_subchaves_da_secao_11():
    assert CONFIG_DIGIBRAIN == ConfigDigibrain() and CONFIG_DIGIBRAIN.ligada is False and CONFIG_DIGIBRAIN_LIGADA.ligada is True
    assert (CONFIG_DIGIBRAIN.modula_g_apr, CONFIG_DIGIBRAIN.p2, CONFIG_DIGIBRAIN.m_mem, CONFIG_DIGIBRAIN.persistencia) == \
        (False, True, True, True)
    for nome in ("ligada", "modula_g_apr", "p2", "m_mem", "persistencia"):
        with pytest.raises(TypeError):
            ConfigDigibrain(**{nome: 1})


def test_nada_fora_do_pacote_le_a_chave():
    """o G2 da etapa 0: a chave nao chega ao motor, a bancada, as ferramentas nem aos experimentos (so o config, o pacote e os testes)"""
    nomes = re.compile(r"\b(ConfigDigibrain|CONFIG_DIGIBRAIN\w*)\b|digilab\.digibrain|from \.digibrain|from \.\.digibrain")
    citam = {p.relative_to(RAIZ).as_posix() for pasta in ("digilab", "experiments", "tools") for p in (RAIZ / pasta).rglob("*.py")
             if nomes.search(p.read_text(encoding="utf-8"))}
    assert {c for c in citam if not c.startswith("digilab/digibrain/")} == {"digilab/config.py"}


def test_o_digibrain_so_existe_com_a_chave_ligada():
    with pytest.raises(DigibrainDesligado):
        DigiBrain()
    with pytest.raises(DigibrainDesligado):
        DigiBrain(cfg_digibrain=replace(CONFIG_DIGIBRAIN_LIGADA, ligada=False))
    assert isinstance(DigiBrain(cfg_digibrain=CONFIG_DIGIBRAIN_LIGADA), Politica)


# ------------------------------------------------------------ o M-ADAPT
class _Mentira:
    """um modulo de mentira: grava cada chamada e devolve o que o teste manda"""

    def __init__(self, diario: list, nome: str, **respostas) -> None:
        self.diario, self.nome, self.respostas = diario, nome, respostas

    def __getattr__(self, metodo: str):
        if metodo.startswith("__"):
            raise AttributeError(metodo)

        def chamada(*a):
            self.diario.append(f"{self.nome}.{metodo}")
            return self.respostas.get(metodo)
        return chamada


def _cerebro(intencao: Intencao, cd: ConfigDigibrain = CONFIG_DIGIBRAIN_LIGADA):
    diario: list = []
    m = Modulos(**{n: _Mentira(diario, n) for n in ("sens", "afeto", "estado", "impulso", "mem", "plast")},
                arb=_Mentira(diario, "arb", escolher=intencao))
    return DigiBrain(cfg_digibrain=cd, modulos=m), diario


def _consequencia(c: DigiBrain, acao: AcaoPet) -> None:
    c.consequencia_corpo(acao, {"acao": acao.value, "estimulos": []}, OBS)
    c.observar(Transicao(observacao=OBS, acao=acao, observacao_seguinte=OBS))
    c.consequencia_mundo(acao, {}, OBS)


def test_o_adaptador_encaminha_aos_modulos_e_fecha_a_decisao_na_seguinte():
    c, diario = _cerebro(Intencao(AcaoPet.COMER, "comida", 7))
    assert c.agir(OBS, random.Random(1)) is AcaoPet.COMER
    assert diario == ["sens.codificar", "afeto.ler", "estado.contexto", "mem.recuperar", "plast.incentivo", "impulso.unidades",
                      "arb.escolher", "estado.escolhida"]
    cands = [Alvo("comida", 10, 10, 3), Alvo("comida", 20, 20, 7), Alvo("cheiro", 30, 30)]
    assert c.escolher_alvo(AcaoPet.COMER, cands, None, 12345) == cands[1]          # o u nao conta
    _consequencia(c, AcaoPet.COMER)
    diario.clear()
    c.agir(OBS, random.Random(1))
    assert diario[:4] == ["afeto.consequencia", "plast.aprender", "mem.codificar", "estado.consequencia"]
    # sem o M-MEM, ele nao e chamado
    c, diario = _cerebro(Intencao(AcaoPet.DORMIR), replace(CONFIG_DIGIBRAIN_LIGADA, m_mem=False))
    c.agir(OBS, random.Random(1))
    _consequencia(c, AcaoPet.DORMIR)
    c.agir(OBS, random.Random(1))
    assert not any(d.startswith("mem.") for d in diario)


def test_as_falhas_altas_da_secao_4_1():
    c, _ = _cerebro(Intencao(AcaoPet.COMER, "comida", 9))
    with pytest.raises(ValueError, match="corpo e o mundo"):
        c.agir(SimpleNamespace(corpo=None, mundo=object()), random.Random(1))
    with pytest.raises(ValueError, match="corpo e o mundo"):
        c.agir(SimpleNamespace(corpo=object(), mundo=None), random.Random(1))
    with pytest.raises(RuntimeError, match="sem decisao pendente"):
        c.escolher_alvo(AcaoPet.COMER, [], None, 0)
    c.agir(OBS, random.Random(1))
    with pytest.raises(ValueError, match="nao esta entre os candidatos"):
        c.escolher_alvo(AcaoPet.COMER, [Alvo("comida", 1, 1, 3)], None, 0)
    with pytest.raises(RuntimeError, match="na decisao de comer"):
        c.consequencia_corpo(AcaoPet.EXPLORAR, {}, OBS)
    with pytest.raises(RuntimeError, match="nao pediu o alvo"):          # a decisao com objeto, sem o alvo pedido
        _consequencia(c, AcaoPet.COMER)
        c.agir(OBS, random.Random(1))
    c, _ = _cerebro(Intencao(AcaoPet.DORMIR))
    c.agir(OBS, random.Random(1))
    with pytest.raises(RuntimeError, match="sem o gancho de consequencia"):
        c.agir(OBS, random.Random(1))
    c, _ = _cerebro(Intencao(AcaoPet.EXPLORAR))
    c.agir(OBS, random.Random(1))
    with pytest.raises(ValueError, match="sem objeto"):
        c.escolher_alvo(AcaoPet.EXPLORAR, [Alvo("vagar", 1, 1)], None, 0)
    c, _ = _cerebro("comer")
    with pytest.raises(TypeError, match="Intencao"):
        c.agir(OBS, random.Random(1))


def test_os_modulos_ainda_nao_tem_equacao():
    c = DigiBrain(cfg_digibrain=CONFIG_DIGIBRAIN_LIGADA)
    with pytest.raises(NotImplementedError, match="M-SENS.codificar"):
        c.agir(OBS, random.Random(1))
    with pytest.raises(NotImplementedError):
        c.estado_interno()
    with pytest.raises(NotImplementedError, match="M-ADAPT.receber_acao_dono"):
        c.receber_acao_dono(AcaoUsuario.ALIMENTAR, 0)
    classes = (sens.Sens, afeto.Afeto, estado.EstadoDinamico, impulso.Impulso, mem.Memoria, arb.Arbitragem, plast.Plasticidade,
               ganchos.Personalidade, ganchos.ParametrosInatos, ganchos.Expressao)
    n = 0
    for cls in classes:
        for nome, f in vars(cls).items():
            if callable(f) and not nome.startswith("_"):
                args = [None] * (f.__code__.co_argcount - 1)
                with pytest.raises(NotImplementedError, match="sem equacao na etapa 0"):
                    f(cls(), *args)
                n += 1
    assert n == 23                                  # os 19 metodos dos sete modulos e os 4 dos ganchos vazios


# ------------------------------------------------------------ o G-INT, a G-RECEPTOR e o preflight
def _arvores():
    arquivos = sorted(PACOTE.glob("*.py"))
    assert {a.name for a in arquivos} == {"__init__.py", "_comum.py", "adapt.py", "afeto.py", "arb.py", "estado.py", "ganchos.py",
                                          "impulso.py", "mem.py", "plast.py", "sens.py"}
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
                assert modulo not in ("..corpo", "digilab.corpo") and not (no.level == 2 and no.module is None and
                                                                           any(a.name == "corpo" for a in no.names)), nome
            elif isinstance(no, ast.Import):
                assert all(a.name != "digilab.corpo" for a in no.names), nome


def test_o_engine_intacto_e_o_pacote_so_com_a_biblioteca_padrao():
    assert sha256_engine() == ENGINE_SHA256_V0
    assert run_arena._imports_externos(RAIZ / "digilab") == set()
