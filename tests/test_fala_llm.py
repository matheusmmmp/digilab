"""Parte C: fala por LLM, validada contra o motivo. Sem rede (clientes falsos)."""

import ast
import io
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
    ProvedorClaude,
    ProvedorOllama,
    custo_usd,
    escolher_provedor,
    motivo_de_dict,
    montar_pedido,
    template,
    validar,
)

ESQUIVA = Motivo("combate", "esquivar", ("oponente_preparando",), (4,), None, False, turno=5)
DOIS = Motivo("combate", "golpe_rapido", ("distancia_eh(perto)", "guts_proprio_acima(40)"), (6,), None, False, turno=6)
VAZIO = Motivo("vida", "comer", (), (), 0.0, False, tick=100)
MEMORIA = Motivo("vida", "chamar_atencao", ("latencia_fome",), (12,), 0.8, False, tick=500)
BOA = ("Esquivei porque você ia usar o golpe pesado.", ["oponente_preparando"])


# ------------------------------------------------------------ Claude falso


class ClienteFalso:
    """Imita client.messages.create / client.beta.messages.create; conta as chamadas."""

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


def G(cliente, limite=2.0, modelo="claude-haiku-4-5", **kw):
    """Gerador com provedor Claude falso e teto de gasto em memoria (sem arquivo)."""
    return GeradorFala(ProvedorClaude(cliente, modelo), gasto=ControleGasto(limite, arquivo=None), **kw)


# ------------------------------------------------------------ Ollama falso


class RespostaHTTP(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class OllamaFalso:
    """Substitui urllib.request.urlopen: /api/tags lista modelos, /api/chat devolve JSON fixo."""

    def __init__(self, texto="", citados=(), modelos=("qwen2.5:3b",), fora_do_ar=False, done_reason="stop", bruto=None):
        self.pedidos = []
        self.modelos, self.fora, self.done = modelos, fora_do_ar, done_reason
        self.conteudo = bruto if bruto is not None else json.dumps({"texto": texto, "fatores_citados": list(citados)},
                                                                   ensure_ascii=False)

    def __call__(self, req, timeout=None):
        if self.fora:
            raise ConnectionRefusedError("Ollama fora do ar")
        corpo = json.loads(req.data.decode("utf-8")) if req.data else None
        self.pedidos.append((req.full_url, corpo, timeout))
        if req.full_url.endswith("/api/tags"):
            dados = {"models": [{"name": m, "model": m} for m in self.modelos]}
        else:
            dados = {"model": corpo["model"], "message": {"role": "assistant", "content": self.conteudo},
                     "done": True, "done_reason": self.done, "prompt_eval_count": 800, "eval_count": 30}
        return RespostaHTTP(json.dumps(dados).encode("utf-8"))


def O(falso, **kw):
    return GeradorFala(ProvedorOllama(abrir=falso), **kw)


# ------------------------------------------------------------ validacao (comum aos provedores)


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
def test_validacao_reprova_e_cai_no_template_nos_dois_provedores(motivo, estagio, texto, citados, erro):
    with pytest.raises(FalaReprovada, match=erro):
        validar(texto, citados, motivo, estagio)
    for g in (G(ClienteFalso(texto, citados)), O(OllamaFalso(texto, citados))):
        r = g.gerar(motivo, estagio, 0.5)
        assert r.fonte == "template" and r.texto == template(motivo, estagio, 0.5)


def test_numeros_dos_parametros_do_fator_sao_permitidos():
    validar("Golpeei perto, com guts acima de 40.", ["distancia_eh(perto)", "guts_proprio_acima(40)"], DOIS, "adulto")


def test_bebe_e_crianca_nunca_chamam_llm():
    c, o = ClienteFalso("x", []), OllamaFalso("x")
    for g in (G(c), O(o)):
        for est in ("bebe", "crianca"):
            assert g.gerar(ESQUIVA, est, 0.5).fonte == "template"
    assert c.chamadas == [] and o.pedidos == []


def test_sem_provedor_so_template():
    assert GeradorFala(None).gerar(ESQUIVA, "adulto").fonte == "template"


# ------------------------------------------------------------ Claude


def test_claude_fala_valida_passa_e_vai_para_o_cache():
    c = ClienteFalso(*BOA)
    g = G(c)
    r = g.gerar(ESQUIVA, "adulto")
    assert r.fonte == "llm" and "Esquivei" in r.texto and r.detalhe.startswith("claude:")
    assert g.gerar(ESQUIVA, "adulto") is r and len(c.chamadas) == 1


def test_claude_erro_recusa_e_limite_por_minuto_caem_no_template():
    assert G(ClienteFalso("x", [], erro=RuntimeError("rede"))).gerar(ESQUIVA, "adulto").fonte == "template"
    assert G(ClienteFalso("x", [], stop="refusal")).gerar(ESQUIVA, "adulto").fonte == "template"
    g = G(ClienteFalso(*BOA), limite_por_minuto=1)
    g.gerar(ESQUIVA, "adulto")
    assert g.gerar(ESQUIVA, "adolescente").detalhe == "limite de chamadas por minuto"


def test_claude_pedido_haiku_sem_effort_e_opus_com_fallback():
    c = ClienteFalso(*BOA)
    G(c).gerar(ESQUIVA, "adulto")
    kw = c.chamadas[0]
    carga = json.loads(kw["messages"][0]["content"])
    assert carga["fatores"] == ["oponente_preparando"] and carga["evento_ref"] == [4]
    assert kw["model"] == "claude-haiku-4-5" and "effort" not in kw["output_config"] and "fallbacks" not in kw
    c2 = ClienteFalso(*BOA)
    G(c2, modelo="claude-opus-5").gerar(ESQUIVA, "adulto")
    assert c2.chamadas[0]["output_config"]["effort"] == "low" and c2.chamadas[0]["fallbacks"] == "default"


def test_claude_gasto_pelo_uso_real_e_teto():
    c = ClienteFalso(*BOA, uso=(1000, 50))
    g = G(c)
    g.gerar(ESQUIVA, "adulto")
    assert g.gasto.gasto == pytest.approx(custo_usd("claude-haiku-4-5", 1000, 50)) and g.gasto.reservado == pytest.approx(0)
    c2 = ClienteFalso(*BOA)
    r = G(c2, limite=0.0001).gerar(ESQUIVA, "adulto")
    assert r.fonte == "template" and "limite de gasto" in r.detalhe and c2.chamadas == []


def test_claude_teto_para_quando_acaba_o_credito():
    g = G(ClienteFalso("Não sei, só quis.", [], uso=(1000, 100)), limite=0.01)
    fontes = [g.gerar(Motivo("vida", "comer", (), (), 0.0, False, tick=t), "adulto").fonte for t in range(100)]
    assert "llm" in fontes and fontes[-1] == "template" and g.gasto.gasto <= 0.01


def test_claude_erro_sem_uso_conta_o_pior_caso():
    g = G(ClienteFalso("x", [], erro=RuntimeError("timeout")))
    g.gerar(ESQUIVA, "adulto")
    assert g.gasto.gasto > 0 and g.gasto.reservado == pytest.approx(0.0)


def test_gasto_persiste_entre_reinicios(tmp_path):
    arq = tmp_path / "gasto.json"
    GeradorFala(ProvedorClaude(ClienteFalso(*BOA)), gasto=ControleGasto(2.0, arquivo=arq)).gerar(ESQUIVA, "adulto")
    novo = ControleGasto(2.0, arquivo=arq)
    assert novo.gasto > 0 and novo.chamadas == 1


def test_claude_sem_preco_ou_sem_teto_nao_liga():
    with pytest.raises(ValueError, match="preco"):
        ProvedorClaude(ClienteFalso("x", []), "modelo-inventado")
    with pytest.raises(ValueError, match="ControleGasto"):
        GeradorFala(ProvedorClaude(ClienteFalso("x", [])))


# ------------------------------------------------------------ Ollama


def test_ollama_fala_valida_sem_custo_e_com_semente_por_motivo():
    o = OllamaFalso(*BOA)
    g = O(o)
    r = g.gerar(ESQUIVA, "adulto")
    assert r.fonte == "llm" and r.detalhe == "ollama: qwen2.5:3b" and g.gasto is None
    url, corpo, timeout = o.pedidos[0]
    assert url.endswith("/api/chat") and corpo["model"] == "qwen2.5:3b" and corpo["stream"] is False
    assert corpo["format"]["required"] == ["texto", "fatores_citados"]
    assert corpo["options"]["temperature"] <= 0.5 and isinstance(corpo["options"]["seed"], int)
    semente = corpo["options"]["seed"]
    o2 = OllamaFalso(*BOA)
    O(o2).gerar(ESQUIVA, "adulto")
    assert o2.pedidos[0][1]["options"]["seed"] == semente          # mesmo motivo, mesma semente


def test_ollama_fora_do_ar_nao_json_e_cortado_caem_no_template():
    assert O(OllamaFalso(fora_do_ar=True)).gerar(ESQUIVA, "adulto").fonte == "template"
    assert O(OllamaFalso(bruto="isso nao e json")).gerar(ESQUIVA, "adulto").fonte == "template"
    r = O(OllamaFalso(*BOA, done_reason="length")).gerar(ESQUIVA, "adulto")
    assert r.fonte == "template" and "interrompida" in r.detalhe


def test_ollama_disponibilidade():
    assert ProvedorOllama(abrir=OllamaFalso()).disponivel() == (True, "")
    ok, motivo = ProvedorOllama(abrir=OllamaFalso(modelos=("llama3.2:3b",))).disponivel()
    assert not ok and "ollama pull qwen2.5:3b" in motivo
    ok, motivo = ProvedorOllama(abrir=OllamaFalso(fora_do_ar=True)).disponivel()
    assert not ok and "não está rodando" in motivo


def test_ollama_primeira_chamada_espera_o_aquecimento():
    o = OllamaFalso(*BOA)
    p = ProvedorOllama(abrir=o)
    GeradorFala(p).gerar(ESQUIVA, "adulto")
    GeradorFala(p).gerar(DOIS, "adulto")
    assert o.pedidos[0][2] > o.pedidos[1][2]


def test_escolher_provedor(monkeypatch):
    import servidor.fala_llm as f

    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_AUTH_TOKEN", raising=False)
    monkeypatch.delenv("ANTHROPIC_PROFILE", raising=False)
    monkeypatch.setattr(f.ProvedorOllama, "disponivel", lambda self: (True, ""))
    p, gasto, _ = escolher_provedor("auto")
    assert p.nome == "ollama" and gasto is None
    monkeypatch.setattr(f.ProvedorOllama, "disponivel", lambda self: (False, "fora do ar"))
    p, _, motivo = escolher_provedor("auto")
    assert p.nome == "ollama" and motivo == "fora do ar"        # fica com o Ollama: vale quando for ligado
    assert escolher_provedor("claude")[0] is None
    assert escolher_provedor("nenhum")[0] is None
    with pytest.raises(ValueError):
        escolher_provedor("gpt")


# ------------------------------------------------------------ fronteira e entrada


def test_motivo_de_dict_e_estrito():
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


def test_avaliacao_roda_com_ollama_falso():
    sys.path.insert(0, str(RAIZ / "experiments"))
    import avaliar_fala

    motivos = avaliar_fala.coletar_motivos(20)
    assert len(motivos) == 20
    assert sum(bool(m.fatores) and not m.exploracao for m, _, _ in motivos) == 10
    # dizer menos do que o motivo e permitido: "nao sei" passa sempre
    linhas, resumo = avaliar_fala.avaliar(O(OllamaFalso("Não sei, só quis.", [])), motivos)
    assert resumo["n"] == 20 and resumo["fracao_aprovada"] == 1.0
    assert all((l["fala"] is None) == (not l["aprovada"]) for l in linhas)
    # inventar causa ("sujeira") so passa onde o motivo tem esse fator
    _, resumo2 = avaliar_fala.avaliar(O(OllamaFalso("Fiz isso por causa da sujeira.", ["sujeira"])), motivos)
    tem_sujeira = sum("sujeira" in m.fatores for m, _, _ in motivos)
    assert resumo2["aprovadas"] == tem_sujeira and resumo2["quedas_por_tipo"]
