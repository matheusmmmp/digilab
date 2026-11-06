"""CONVERSA_PET M5: o cliente Claude da fala livre, so com SDK falso (nenhuma chamada real a API)."""

from __future__ import annotations

import inspect
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "tests"))

from digilab_fala_livre.gerar import gerar  # noqa: E402
from digilab_fala_livre.ollama import ClienteOllama, Resposta  # noqa: E402
from digilab_fala_livre.prompt import esquema  # noqa: E402
from servidor import fala_livre_claude as flc  # noqa: E402
from servidor.fala_livre import ServicoFalaLivre  # noqa: E402
from servidor.fala_livre_claude import PALAVRAS_NAO_ACEITAS, PENSAMENTO, ClienteClaude, ErroClaude, traduzir_esquema  # noqa: E402
from digilab_fala_livre.prompt import MAX_CHARS  # noqa: E402
from digilab_fala_livre.saida import aparar  # noqa: E402
from servidor.fala_llm import PRECOS_USD_POR_MTOK, ControleGasto  # noqa: E402
from test_fala_livre import ESTADO  # noqa: E402

BOA = '{"fala": "Tava com fome.", "fatos_citados": ["R1"]}'
MSGS = [{"role": "system", "content": "Regra A."}, {"role": "system", "content": "Regra B."},
        {"role": "user", "content": "oi"}]


class SdkFalso:
    def __init__(self, texto=BOA, parada="end_turn", ent=2600, sai=100, erro=None):
        self.chamadas, self.texto, self.parada, self.ent, self.sai, self.erro = [], texto, parada, ent, sai, erro
        self.messages = self

    def create(self, **kw):
        self.chamadas.append(kw)
        if self.erro:
            raise self.erro
        return SimpleNamespace(content=[SimpleNamespace(type="text", text=self.texto)], stop_reason=self.parada,
                               model=kw["model"], usage=SimpleNamespace(input_tokens=self.ent, output_tokens=self.sai))


def _cliente(sdk, limite=3.0, modelo="claude-haiku-5-5", permitido=None):
    return ClienteClaude(modelo, ControleGasto(limite, None), sdk=sdk, permitido=permitido)


def test_interface_igual_a_do_ollama():
    a = inspect.signature(ClienteOllama.conversar)
    b = inspect.signature(ClienteClaude.conversar)
    assert list(a.parameters) == list(b.parameters)
    r = _cliente(SdkFalso()).conversar(MSGS, esquema("adulto"), 360, 7)
    assert isinstance(r, Resposta) and r.texto == BOA and r.completa and r.tokens_entrada == 2600 and r.tokens_saida == 100


def test_sistema_esquema_esforco_e_sem_temperatura_nem_semente():
    sdk = SdkFalso()
    esq = esquema("adulto")
    _cliente(sdk).conversar(MSGS, esq, 360, 7)
    kw = sdk.chamadas[0]
    assert kw["system"] == "Regra A.\n\nRegra B." and kw["messages"] == [{"role": "user", "content": "oi"}]
    assert kw["output_config"] == {"effort": "low", "format": {"type": "json_schema", "schema": traduzir_esquema(esq)}}
    assert not {"temperature", "top_p", "top_k", "seed", "semente"} & set(kw)
    assert kw["max_tokens"] >= 360


def test_gasto_acertado_pelo_usage():
    c = _cliente(SdkFalso(ent=2600, sai=100), modelo="claude-sonnet-5-5")
    c.conversar(MSGS, esquema("adulto"), 360, 0)
    assert c.gasto.gasto == pytest.approx((2600 * 2.0 + 100 * 10.0) / 1e6) and c.gasto.reservado == 0 and c.gasto.chamadas == 1


@pytest.mark.parametrize("sdk", [SdkFalso(parada="refusal"), SdkFalso(parada="max_tokens"),
                                 SdkFalso(erro=ConnectionError("rede"))])
def test_falha_sobe_como_oserror_e_o_gerar_cai_na_fala_generica(sdk):
    c = _cliente(sdk)
    with pytest.raises(OSError):
        c.conversar(MSGS, esquema("adulto"), 360, 0)
    r = gerar(c, ESTADO, "espontanea", semente=1)
    assert r.erro is not None and r.fala            # a fala generica de hoje, com o erro registrado
    assert "chamada: ErroClaude" in r.erro


def test_json_invalido_cai_na_fala_generica_como_no_ollama():
    r = gerar(_cliente(SdkFalso(texto="isto nao e json")), ESTADO, "espontanea", semente=1)
    assert r.erro is not None and r.erro.startswith("saida:")


def test_teto_barra_a_chamada():
    sdk = SdkFalso()
    c = _cliente(sdk, limite=0.0, modelo="claude-sonnet-5-5")
    with pytest.raises(ErroClaude, match="teto"):
        c.conversar(MSGS, esquema("adulto"), 360, 0)
    assert sdk.chamadas == [] and c.gasto.gasto == 0


def test_falha_de_rede_conta_o_maximo_reservado():
    c = _cliente(SdkFalso(erro=ConnectionError("x")))
    with pytest.raises(ErroClaude):
        c.conversar(MSGS, esquema("adulto"), 360, 0)
    assert c.gasto.gasto > 0 and c.gasto.reservado == 0


def test_modelo_sem_preco_nao_liga():
    with pytest.raises(ValueError, match="sem preco"):
        ClienteClaude("claude-inexistente", ControleGasto(1.0, None), sdk=SdkFalso())


def test_precos_novos_na_tabela():
    assert PRECOS_USD_POR_MTOK["claude-haiku-5-5"] == (0.10, 0.50)
    assert PRECOS_USD_POR_MTOK["claude-sonnet-5-5"] == (2.00, 10.00)


def test_desligado_no_remoto_nao_chama():
    sdk = SdkFalso()
    with pytest.raises(ErroClaude, match="desligada"):
        _cliente(sdk, permitido=lambda: False).conversar(MSGS, esquema("adulto"), 360, 0)
    assert sdk.chamadas == []


def test_papel_desconhecido_e_conversa_sem_user_falham_alto():
    c = _cliente(SdkFalso())
    with pytest.raises(ValueError):
        c.conversar([{"role": "tool", "content": "x"}], esquema("adulto"), 360, 0)
    with pytest.raises(ValueError):
        c.conversar([{"role": "system", "content": "x"}], esquema("adulto"), 360, 0)


def test_servico_padrao_continua_ollama_sem_mudanca():
    s = ServicoFalaLivre(ambiente={})
    assert isinstance(s.cliente, ClienteOllama) and s.cliente.modelo == "gemma2:9b"
    assert s.cliente_verif is s.cliente and s.gasto is None
    st = s.status()
    assert st["provedor"] == "ollama" and st["modelo"] == "gemma2:9b" and st["ativo"] is True and st["gasto"] is None


def test_servico_claude_com_verificador_ollama_proprio():
    gasto = ControleGasto(3.0, None)
    env = {"DIGILAB_PROVEDOR_LIVRE": "claude", "DIGILAB_MODELO_LIVRE": "claude-haiku-5-5"}
    s = ServicoFalaLivre(ambiente=env, gasto=gasto, sdk=SdkFalso())
    assert isinstance(s.cliente, ClienteClaude) and isinstance(s.cliente_verif, ClienteOllama)
    assert s.cliente.cliente_verif is s.cliente_verif and s.cliente_verif.modelo == "gemma2:9b"
    st = s.status()
    assert (st["provedor"], st["modelo"], st["provedor_verificador"], st["modelo_verificador"]) == \
        ("claude", "claude-haiku-5-5", "ollama", "gemma2:9b")
    assert st["gasto"]["limite_usd"] == 3.0


def test_servico_remoto_desliga_o_claude_no_status():
    env = {"DIGILAB_PROVEDOR_LIVRE": "claude", "DIGILAB_MODELO_LIVRE": "claude-sonnet-5-5"}
    s = ServicoFalaLivre(ambiente=env, gasto=ControleGasto(3.0, None), sdk=SdkFalso(), claude_permitido=lambda: False)
    assert s.status()["ativo"] is False
    with pytest.raises(ErroClaude):
        s.cliente.conversar(MSGS, esquema("adulto"), 360, 0)


def test_provedor_desconhecido_falha_alto():
    with pytest.raises(ValueError, match="provedor desconhecido"):
        ServicoFalaLivre(ambiente={"DIGILAB_PROVEDOR_LIVRE": "openai"})


def test_arquivo_de_gasto_proprio_e_teto_padrao_3():
    assert flc.ARQUIVO_GASTO_LIVRE.name == "gasto_fala_livre.json" and flc.LIMITE_USD_LIVRE_PADRAO == 3.0
    assert "gasto_fala_livre.json" in (RAIZ / ".gitignore").read_text(encoding="utf-8")


def test_chave_nunca_em_arquivo_do_servidor():
    for arq in ("fala_livre_claude.py", "fala_livre.py"):
        assert "sk-ant" not in (RAIZ / "servidor" / arq).read_text(encoding="utf-8")


def _chaves(x):
    if isinstance(x, dict):
        for k, v in x.items():
            yield k
            yield from _chaves(v)
    elif isinstance(x, list):
        for v in x:
            yield from _chaves(v)


@pytest.mark.parametrize("est", ["bebe", "crianca", "adolescente", "adulto"])
@pytest.mark.parametrize("comando", [False, True])
def test_esquema_enviado_nao_tem_palavra_proibida(est, comando):
    sdk = SdkFalso()
    original = esquema(est, comando)
    _cliente(sdk).conversar(MSGS, original, 360, 0)
    enviado = sdk.chamadas[0]["output_config"]["format"]["schema"]
    assert not PALAVRAS_NAO_ACEITAS & set(_chaves(enviado))
    assert enviado["additionalProperties"] is False and enviado["required"] == original["required"]
    if comando:
        assert enviado["properties"]["comando"] == original["properties"]["comando"]      # o enum com null fica
    assert "maxLength" in set(_chaves(original))                  # o original (Ollama) nao foi mexido


def test_fala_longa_e_cortada_no_limite_e_depois_aparada():
    """O `aparar` sozinho nao corta (so tira o pedaco incompleto de quem o Ollama parou no limite): o cliente corta no `maxLength`
    que o esquema do Ollama tinha, como o Ollama faria, e o `aparar` deixa so o inteiro."""
    longa = "Oi, tudo bem. " * 40
    assert len(aparar(longa, MAX_CHARS["adulto"])) > MAX_CHARS["adulto"]           # documenta o limite do aparar
    sdk = SdkFalso(texto='{"fala": "%s", "fatos_citados": []}' % longa)
    r = _cliente(sdk).conversar(MSGS, esquema("adulto"), 360, 0)
    assert len(json.loads(r.texto)["fala"]) == MAX_CHARS["adulto"]
    res = gerar(_cliente(sdk), ESTADO, "espontanea", semente=1)
    assert res.erro is None and 0 < len(res.fala) <= MAX_CHARS[res.estagio] and res.fala.endswith(".")


def test_fala_dentro_do_limite_passa_intacta():
    assert _cliente(SdkFalso()).conversar(MSGS, esquema("adulto"), 360, 0).texto == BOA


def test_pensamento_desligado_por_modelo():
    for modelo, esperado in (("claude-haiku-5-5", {"type": "disabled"}), ("claude-sonnet-5-5", {"type": "between_tools"})):
        sdk = SdkFalso()
        _cliente(sdk, modelo=modelo).conversar(MSGS, esquema("adulto"), 360, 0)
        assert sdk.chamadas[0]["thinking"] == esperado == PENSAMENTO[modelo]
        assert sdk.chamadas[0]["output_config"]["effort"] == "low"      # between_tools/disabled so valem com esforco high ou abaixo


def test_modelo_com_preco_mas_sem_regra_de_pensamento_nao_liga():
    with pytest.raises(ValueError, match="pensamento"):
        ClienteClaude("claude-opus-5", ControleGasto(1.0, None), sdk=SdkFalso())
