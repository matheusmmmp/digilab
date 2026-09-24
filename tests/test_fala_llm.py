"""Parte C: fala por LLM, validada contra o motivo. Sem rede (cliente falso)."""

import ast
import json
import sys
from pathlib import Path
from types import SimpleNamespace as NS

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab.motivo import Motivo  # noqa: E402
from servidor.fala_llm import FalaReprovada, GeradorFala, motivo_de_dict, montar_pedido, template, validar  # noqa: E402


class ClienteFalso:
    """Imita client.beta.messages.create devolvendo um JSON fixo; conta as chamadas."""

    def __init__(self, texto, citados, stop="end_turn", erro=None):
        self.chamadas = []
        self.saida = json.dumps({"texto": texto, "fatores_citados": citados}, ensure_ascii=False)
        self.stop, self.erro = stop, erro
        self.beta = NS(messages=NS(create=self._create))

    def _create(self, **kw):
        self.chamadas.append(kw)
        if self.erro:
            raise self.erro
        return NS(stop_reason=self.stop, model=kw["model"], content=[NS(type="text", text=self.saida)])


ESQUIVA = Motivo("combate", "esquivar", ("oponente_preparando",), (4,), None, False, turno=5)
DOIS = Motivo("combate", "golpe_rapido", ("distancia_eh(perto)", "guts_proprio_acima(40)"), (6,), None, False, turno=6)
VAZIO = Motivo("vida", "comer", (), (), 0.0, False, tick=100)
MEMORIA = Motivo("vida", "chamar_atencao", ("latencia_fome",), (12,), 0.8, False, tick=500)


def test_fala_valida_passa_e_vai_para_o_cache():
    c = ClienteFalso("Esquivei porque você ia soltar o pesado no turno 4!", ["oponente_preparando"])
    g = GeradorFala(c)
    r = g.gerar(ESQUIVA, "adulto")
    assert r.fonte == "llm" and "Esquivei" in r.texto
    assert g.gerar(ESQUIVA, "adulto") is r and len(c.chamadas) == 1


@pytest.mark.parametrize("motivo,estagio,texto,citados,erro", [
    (ESQUIVA, "adulto", "Esquivei porque estava com fome.", ["oponente_preparando"], "fator ausente"),
    (ESQUIVA, "adulto", "Esquivei porque você ia usar o golpe pesado.", ["fome"], "fora do motivo"),
    (VAZIO, "adulto", "Comi porque você demorou com a comida.", [], "fator ausente"),
    (VAZIO, "adulto", "Comi porque deu vontade.", [], "nao sabe"),
    (DOIS, "adolescente", "perto... folga de guts...", ["distancia_eh(perto)", "guts_proprio_acima(40)"], "permite 1"),
    (ESQUIVA, "adulto", "Esquivei porque você preparou o pesado no turno 3.", ["oponente_preparando"], "numeros"),
    (MEMORIA, "adulto", "Chamei você porque você demorou com a comida da última vez, e fiquei sem cuidado.",
     ["latencia_fome"], "fator ausente"),
])
def test_validacao_reprova_e_cai_no_template(motivo, estagio, texto, citados, erro):
    with pytest.raises(FalaReprovada, match=erro):
        validar(texto, citados, motivo, estagio)
    r = GeradorFala(ClienteFalso(texto, citados)).gerar(motivo, estagio, 0.5)
    assert r.fonte == "template" and r.texto == template(motivo, estagio, 0.5)


def test_numeros_dos_parametros_do_fator_sao_permitidos():
    validar("Golpeei perto, com guts acima de 40.", ["distancia_eh(perto)", "guts_proprio_acima(40)"], DOIS, "adulto")


def test_bebe_e_crianca_nunca_chamam_a_llm():
    c = ClienteFalso("x", [])
    g = GeradorFala(c)
    for est in ("bebe", "crianca"):
        assert g.gerar(ESQUIVA, est, 0.5).fonte == "template"
    assert c.chamadas == []


def test_sem_credencial_erro_recusa_e_limite_caem_no_template():
    assert GeradorFala(None).gerar(ESQUIVA, "adulto").fonte == "template"
    assert GeradorFala(ClienteFalso("x", [], erro=RuntimeError("rede"))).gerar(ESQUIVA, "adulto").fonte == "template"
    assert GeradorFala(ClienteFalso("x", [], stop="refusal")).gerar(ESQUIVA, "adulto").fonte == "template"
    c = ClienteFalso("Esquivei porque você ia usar o golpe pesado.", ["oponente_preparando"])
    g = GeradorFala(c, limite_por_minuto=1)
    g.gerar(ESQUIVA, "adulto")
    assert g.gerar(ESQUIVA, "adolescente").detalhe == "limite de chamadas por minuto"


def test_pedido_leva_so_o_motivo_e_textos_permitidos():
    c = ClienteFalso("Esquivei porque você ia usar o golpe pesado.", ["oponente_preparando"])
    GeradorFala(c).gerar(ESQUIVA, "adulto")
    kw = c.chamadas[0]
    carga = json.loads(kw["messages"][0]["content"])
    assert carga["fatores"] == ["oponente_preparando"] and carga["evento_ref"] == [4]
    assert set(carga["significado_dos_fatores"]) == {"oponente_preparando"}
    assert kw["output_config"]["format"]["type"] == "json_schema"
    assert kw["model"] == "claude-opus-5"


def test_motivo_de_dict_e_estritos():
    m = motivo_de_dict({"origem": "vida", "acao": "comer", "fatores": ["fome"], "evento_ref": [3],
                        "intensidade": .4, "exploracao": False, "tick": 900})
    assert m.tick == 900 and m.fatores == ("fome",)
    with pytest.raises(KeyError):
        motivo_de_dict({"origem": "vida", "acao": "comer"})
    with pytest.raises(ValueError):
        motivo_de_dict({"origem": "sonho"})
    assert "exemplo" in json.loads(montar_pedido(m, "adulto", .5))


def test_digilab_nao_importa_servidor_nem_anthropic():
    for arq in (RAIZ / "digilab").rglob("*.py"):
        for no in ast.walk(ast.parse(arq.read_text(encoding="utf-8"))):
            nomes = [a.name for a in no.names] if isinstance(no, ast.Import) else \
                [no.module or ""] if isinstance(no, ast.ImportFrom) else []
            assert not any(n.split(".")[0] in ("servidor", "anthropic") for n in nomes), arq
