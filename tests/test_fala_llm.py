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
from servidor.fala_llm import (  # noqa: E402
    ControleGasto,
    FalaReprovada,
    GeradorFala,
    custo_usd,
    motivo_de_dict,
    montar_pedido,
    template,
    validar,
)


def G(cliente, limite=2.0, **kw):
    """Gerador com teto de gasto em memoria (sem arquivo)."""
    return GeradorFala(cliente, gasto=ControleGasto(limite, arquivo=None), **kw)


class ClienteFalso:
    """Imita client.beta.messages.create devolvendo um JSON fixo; conta as chamadas."""

    def __init__(self, texto, citados, stop="end_turn", erro=None, uso=(900, 40)):
        self.chamadas = []
        self.saida = json.dumps({"texto": texto, "fatores_citados": citados}, ensure_ascii=False)
        self.stop, self.erro, self.uso = stop, erro, uso
        self.beta = NS(messages=NS(create=self._create))
        self.messages = NS(create=self._create)

    def _create(self, **kw):
        self.chamadas.append(kw)
        if self.erro:
            raise self.erro
        return NS(stop_reason=self.stop, model=kw["model"], content=[NS(type="text", text=self.saida)],
                  usage=NS(input_tokens=self.uso[0], output_tokens=self.uso[1]))


ESQUIVA = Motivo("combate", "esquivar", ("oponente_preparando",), (4,), None, False, turno=5)
DOIS = Motivo("combate", "golpe_rapido", ("distancia_eh(perto)", "guts_proprio_acima(40)"), (6,), None, False, turno=6)
VAZIO = Motivo("vida", "comer", (), (), 0.0, False, tick=100)
MEMORIA = Motivo("vida", "chamar_atencao", ("latencia_fome",), (12,), 0.8, False, tick=500)


def test_fala_valida_passa_e_vai_para_o_cache():
    c = ClienteFalso("Esquivei porque você ia soltar o pesado no turno 4!", ["oponente_preparando"])
    g = G(c)
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
    r = G(ClienteFalso(texto, citados)).gerar(motivo, estagio, 0.5)
    assert r.fonte == "template" and r.texto == template(motivo, estagio, 0.5)


def test_numeros_dos_parametros_do_fator_sao_permitidos():
    validar("Golpeei perto, com guts acima de 40.", ["distancia_eh(perto)", "guts_proprio_acima(40)"], DOIS, "adulto")


def test_bebe_e_crianca_nunca_chamam_a_llm():
    c = ClienteFalso("x", [])
    g = G(c)
    for est in ("bebe", "crianca"):
        assert g.gerar(ESQUIVA, est, 0.5).fonte == "template"
    assert c.chamadas == []


def test_sem_credencial_erro_recusa_e_limite_caem_no_template():
    assert GeradorFala(None).gerar(ESQUIVA, "adulto").fonte == "template"
    assert G(ClienteFalso("x", [], erro=RuntimeError("rede"))).gerar(ESQUIVA, "adulto").fonte == "template"
    assert G(ClienteFalso("x", [], stop="refusal")).gerar(ESQUIVA, "adulto").fonte == "template"
    c = ClienteFalso("Esquivei porque você ia usar o golpe pesado.", ["oponente_preparando"])
    g = G(c, limite_por_minuto=1)
    g.gerar(ESQUIVA, "adulto")
    assert g.gerar(ESQUIVA, "adolescente").detalhe == "limite de chamadas por minuto"


def test_pedido_leva_so_o_motivo_e_textos_permitidos():
    c = ClienteFalso("Esquivei porque você ia usar o golpe pesado.", ["oponente_preparando"])
    G(c).gerar(ESQUIVA, "adulto")
    kw = c.chamadas[0]
    carga = json.loads(kw["messages"][0]["content"])
    assert carga["fatores"] == ["oponente_preparando"] and carga["evento_ref"] == [4]
    assert set(carga["significado_dos_fatores"]) == {"oponente_preparando"}
    assert kw["output_config"]["format"]["type"] == "json_schema"
    assert kw["model"] == "claude-haiku-4-5"
    assert "effort" not in kw["output_config"] and "fallbacks" not in kw


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


def test_opus_usa_esforco_baixo_e_fallback_de_recusa():
    c = ClienteFalso("Esquivei porque você ia usar o golpe pesado.", ["oponente_preparando"])
    G(c, modelo="claude-opus-5").gerar(ESQUIVA, "adulto")
    kw = c.chamadas[0]
    assert kw["output_config"]["effort"] == "low" and kw["fallbacks"] == "default"


# ------------------------------------------------------------ teto de gasto


def test_gasto_e_contado_pelo_uso_real():
    c = ClienteFalso("Esquivei porque você ia usar o golpe pesado.", ["oponente_preparando"], uso=(1000, 50))
    g = G(c)
    g.gerar(ESQUIVA, "adulto")
    assert g.gasto.gasto == pytest.approx(custo_usd("claude-haiku-4-5", 1000, 50))
    assert g.gasto.reservado == pytest.approx(0.0) and g.gasto.chamadas == 1


def test_teto_atingido_nao_chama_a_api():
    c = ClienteFalso("Esquivei porque você ia usar o golpe pesado.", ["oponente_preparando"])
    g = G(c, limite=0.0001)
    r = g.gerar(ESQUIVA, "adulto")
    assert r.fonte == "template" and "limite de gasto" in r.detalhe and c.chamadas == []


def test_teto_para_de_chamar_quando_acaba_o_credito():
    c = ClienteFalso("Não sei, só quis.", [], uso=(1000, 100))
    g = G(c, limite=0.01)
    motivos = [Motivo("vida", "comer", (), (), 0.0, False, tick=t) for t in range(100)]
    fontes = [g.gerar(m, "adulto").fonte for m in motivos]
    assert "llm" in fontes and fontes[-1] == "template"
    assert g.gasto.gasto <= 0.01


def test_erro_sem_uso_conta_o_pior_caso():
    g = G(ClienteFalso("x", [], erro=RuntimeError("timeout")))
    g.gerar(ESQUIVA, "adulto")
    assert g.gasto.gasto > 0 and g.gasto.reservado == pytest.approx(0.0)


def test_gasto_persiste_entre_reinicios(tmp_path):
    arq = tmp_path / "gasto.json"
    c = ClienteFalso("Esquivei porque você ia usar o golpe pesado.", ["oponente_preparando"])
    GeradorFala(c, gasto=ControleGasto(2.0, arquivo=arq)).gerar(ESQUIVA, "adulto")
    antes = ControleGasto(2.0, arquivo=arq)
    assert antes.gasto > 0 and antes.chamadas == 1


def test_modelo_sem_preco_ou_sem_teto_nao_liga():
    with pytest.raises(ValueError, match="preco"):
        GeradorFala(ClienteFalso("x", []), modelo="modelo-inventado", gasto=ControleGasto(2.0, arquivo=None))
    with pytest.raises(ValueError, match="ControleGasto"):
        GeradorFala(ClienteFalso("x", []))
