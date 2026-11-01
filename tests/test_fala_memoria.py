"""T-ME-6 (C4, M6): a fala so alega memoria que o registro sustenta (docs/ESPEC_MEMORIA_AUTOBIOGRAFICA_DIGIBRAIN_MODULAR.md, 7.1, 9).
As tres lacunas da auditoria, uma por uma; a paridade com o gabarito do web; a desligada igual a hoje. Nenhuma LLM: saidas fixas."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import exportar_gabarito_fala_memoria as exp  # noqa: E402

from digilab.motivo import FATORES_MUNDO, Motivo, motivo_fruta  # noqa: E402
from digilab.expressao import FATORES, expressar  # noqa: E402
from digilab_fala_livre import memoria_fala as mf  # noqa: E402
from digilab_fala_livre.fatos import FatosInvalidos, fatos_de_estado  # noqa: E402
from digilab_fala_livre.ollama import Resposta  # noqa: E402
from digilab_fala_livre.prompt import SISTEMA_V6, VERSAO_PROMPT_V6, mensagens  # noqa: E402
from digilab_fala_livre.verificador import VERSAO_VERIFICADOR_V5, verificar  # noqa: E402

ESTADO = {"identidade": {"estagio": "adulto", "especie": "brasa"}, "estado": {"fome": 0.5, "humor": 0.5}}
LEM = {"episodio": 4, "categoria": ["comer", "podre", "negativo"], "decidiu": False}
FAC = {"faceta": "cautela_comida", "dia": 3, "passo": 1, "episodios": [4, 7]}


class _Falso:
    modelo = "falso"

    def __init__(self, *respostas):
        self.respostas = list(respostas)

    def conversar(self, msgs, esquema, max_tokens, semente):
        return Resposta(json.dumps(self.respostas.pop(0)), "falso", 0.1, None, None, True)


def _fatos(mem):
    return [f.para_dict() for f in fatos_de_estado({**ESTADO, "memoria_autobio": mem})]


def test_gabarito_do_web_esta_em_dia():
    g = json.loads(exp.ARQUIVO.read_text(encoding="utf-8"))
    assert g["casos"] == json.loads(json.dumps(exp.calcular()))


def test_lacunas_uma_por_uma_no_gabarito():
    por_nome = {c["nome"]: [a["sustentada"] for a in c["alegacoes"]] for c in exp.calcular()}
    assert por_nome["lacuna1_lembranca_sem_registro"] == [False] and por_nome["lacuna1_outro_episodio"] == [False]
    assert por_nome["lacuna1_lembranca_com_registro"] == [True]
    assert por_nome["lacuna2_causa_sem_sonda"] == [False] and por_nome["lacuna2_causa_por_fato_de_memoria_velha"] == [False]
    assert por_nome["lacuna2_causa_com_sonda"] == [True]
    assert por_nome["lacuna3_faceta_sem_registro"] == [False] and por_nome["lacuna3_faceta_sentido_contrario"] == [False]
    assert por_nome["lacuna3_outra_faceta"] == [False] and por_nome["lacuna3_faceta_com_registro"] == [True]
    assert por_nome["desligada_nao_confere"] == []


def test_fatos_da_memoria_so_com_a_chave():
    sem = fatos_de_estado(ESTADO)
    assert not any(f.tipo in mf.TIPOS_MEMORIA for f in sem)                       # desligada: o bloco de hoje
    assert [f.id for f in fatos_de_estado({**ESTADO, "memoria_autobio": {"lembranca": None, "facetas": []}})][-1] == "Q1"
    f = fatos_de_estado({**ESTADO, "memoria_autobio": {"lembranca": {**LEM, "decidiu": True}, "facetas": [FAC]}})
    assert [(x.id, x.tipo) for x in f if x.tipo in mf.TIPOS_MEMORIA] == [("Q1", mf.TIPO_LEMBRANCA), ("Q2", mf.TIPO_DECIDIU), ("Z1", mf.TIPO_FACETA)]
    for ruim in ({"lembranca": None}, {"lembranca": None, "facetas": [{**FAC, "faceta": "outra"}]},
                 {"lembranca": None, "facetas": [{**FAC, "episodios": []}]}, {"lembranca": {**LEM, "decidiu": 1}, "facetas": []}):
        with pytest.raises(FatosInvalidos):
            fatos_de_estado({**ESTADO, "memoria_autobio": ruim})


def test_prompt_so_ganha_as_regras_com_a_memoria():
    sem = mensagens(fatos_de_estado(ESTADO), "espontanea", versao=VERSAO_PROMPT_V6)
    assert sem[0]["content"] == SISTEMA_V6                                        # desligada: o prompt de hoje, byte a byte
    com = mensagens(fatos_de_estado({**ESTADO, "memoria_autobio": {"lembranca": None, "facetas": []}}), "espontanea", versao=VERSAO_PROMPT_V6)
    assert com[0]["content"] == SISTEMA_V6 + mf.REGRAS_MEMORIA and "lembranca que decidiu" in com[0]["content"]


def _verificar(fala, mem, juiz_sustenta=None):
    """extrator fixo (a fala inteira como lembranca/causa) e juiz fixo (aceita o fato `juiz_sustenta`, o velho comportamento)"""
    fatos = _fatos(mem) + [{"id": "M1", "tipo": "memoria", "texto": "(curto prazo, bronca) o dono me repreendeu, ha 20 min"}]
    ext = {"afirmacoes": [{"tipo": "causa", "trecho": fala}] if "lembr" in fala else []}      # a faceta o extrator nao ve
    juiz = {"sustentada": juiz_sustenta is not None, "fato": juiz_sustenta or ""}
    return verificar(_Falso(ext, juiz), fala, [], fatos, versao=VERSAO_VERIFICADOR_V5)


def test_verificador_recusa_causa_por_memoria_que_o_juiz_aceitava():
    # lacuna 2: o juiz aceita "porque lembrei" apoiado no fato [M1] de categoria e tempo; com a memoria ligada, nao vale
    v = _verificar("Fui comer porque lembrei da bronca.", {"lembranca": None, "facetas": []}, juiz_sustenta="M1")
    assert v.nao_suportadas == 1 and v.afirmacoes[0]["regra"] == "memoria_autobio" and v.afirmacoes[0]["sustentada"] is False
    assert v.memoria_autobio["substituidas"] and v.para_dict()["memoria_autobio"]["alegacoes"][0]["fato"] is None
    # lacuna 1: lembranca sem episodio recuperado
    assert _verificar("Lembrei de comer podre.", {"lembranca": None, "facetas": []}).nao_suportadas == 1
    # com o registro e a sonda, a mesma fala passa
    ok = _verificar("Comi podre ontem e fui evitar porque lembrei do podre.", {"lembranca": {**LEM, "decidiu": True}, "facetas": []})
    assert ok.nao_suportadas == 0 and ok.afirmacoes[0]["fato"] == "Q2"
    # lembranca sem a sonda nao e causa
    assert _verificar("Evitei o podre porque lembrei do podre.", {"lembranca": LEM, "facetas": []}).nao_suportadas == 1


def test_verificador_faceta_so_com_o_registro():
    fala = "Fiquei mais cauteloso com a comida."
    assert _verificar(fala, {"lembranca": None, "facetas": []}).nao_suportadas == 1
    assert _verificar(fala, {"lembranca": None, "facetas": [FAC]}).nao_suportadas == 0
    assert _verificar(fala, {"lembranca": None, "facetas": [{**FAC, "passo": -1}]}).nao_suportadas == 1     # desceu: o sentido contrario


def test_verificador_desligado_sai_como_hoje():
    fatos = [f.para_dict() for f in fatos_de_estado(ESTADO)] + [{"id": "M1", "tipo": "memoria", "texto": "(curto prazo, bronca) x, ha 20 min"}]
    fala = "Fui comer porque lembrei da bronca."
    v = verificar(_Falso({"afirmacoes": [{"tipo": "causa", "trecho": fala}]}, {"sustentada": True, "fato": "M1"}), fala, [], fatos,
                  versao=VERSAO_VERIFICADOR_V5)
    assert v.nao_suportadas == 0 and v.memoria_autobio is None and "memoria_autobio" not in v.para_dict()


# --- a lacuna 3: o motivo do N6
REG = {"presentes": ["a", "b"], "pesos": {"a": 0.2, "b": 0.8}, "u": 0.1, "escolhida": "b"}


def test_motivo_da_fruta_consulta_a_sonda_da_memoria():
    inc = {"a": 0.8, "b": 0.2}
    assert motivo_fruta(REG, inc) == ("escolha_aprendida_fruta", "decisao")                       # sem a sonda: o de hoje
    assert motivo_fruta(REG, inc, {"escolha_sem_memoria": "b", "mudou": False, "recuperou": True}) == ("escolha_aprendida_fruta", "decisao")
    assert motivo_fruta(REG, inc, {"escolha_sem_memoria": "a", "mudou": True, "recuperou": True}) == ("memoria_fruta", "memoria")
    assert "memoria_fruta" in FATORES_MUNDO
    m = Motivo("vida", "comer", ("memoria_fruta",), (), 0.5, False, tick=0)
    assert "lembrei dessa fruta" in expressar(m, "adulto").conteudo and FATORES["memoria_fruta"]["marcador"] in expressar(m, "crianca").conteudo
