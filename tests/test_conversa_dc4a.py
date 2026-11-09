"""DC4a da CONVERSA_PET (docs/PLANO_ANALISE_V3_CONVERSA_DC4.md, secao 10): o montador, as entradas, o orquestrador, a marcacao, a faixa e a
estimativa, todos com clientes falsos. Nenhuma chamada a modelo de verdade e nenhuma vida das faixas de pesquisa (so as sementes dos testes)."""
from __future__ import annotations

import gzip
import http.client
import json
import sys
import threading
from http.server import HTTPServer
from pathlib import Path
from types import SimpleNamespace

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tools"))

import entradas_dc4 as en  # noqa: E402
import exportar_gabarito_fala_rede as gfr  # noqa: E402
import marcacao_dc4 as mc  # noqa: E402
import montador_voz_rede as mv  # noqa: E402
import run_v3_conversa_dc4 as dc4  # noqa: E402

from digilab.config import CONTEUDOS_FALA  # noqa: E402
from digilab_fala_livre import conceitos as dec  # noqa: E402
from digilab_fala_livre.ollama import Resposta  # noqa: E402
from servidor.fala_livre_claude import ClienteClaude, ErroClaude  # noqa: E402
from servidor.fala_llm import ControleGasto  # noqa: E402

CFG_FUMACA = "experiments/configs/v3_conversa_dc4/fumaca.json"


def _cfg(nome: str) -> dict:
    return json.loads((RAIZ / f"experiments/configs/v3_conversa_dc4/{nome}.json").read_text(encoding="utf-8"))


# ================================================================== 1. o montador (espelho do falaRede.ts)
D2 = {"versao": "dec-v2", "k": 3, "intencao": "fome", "conceitos": [
    {"nome": "fome", "valor": 900, "confianca": 700, "alvo": "comida"}, {"nome": "aversao", "valor": 600, "confianca": 300, "alvo": "bola"},
    {"nome": "lembranca", "valor": 800, "confianca": 800, "alvo": "ep4", "episodio": {"acao": "comer", "classe": "racao", "desfecho": "bom"}}]}


def test_montador_dec_v2_tira_o_alvo_fora_do_catalogo_e_guarda_o_resto():
    p = mv.conceitos_da_voz(D2, None)
    assert p["versao"] == "dec-v2" and p["intencao"] == "fome" and p["k"] == 3
    assert p["conceitos"][0] == {"nome": "fome", "valor": 900, "confianca": 700}            # `comida` sai (D-CP-DC2b-5)
    assert p["conceitos"][1]["alvo"] == "bola" and p["conceitos"][2]["episodio"] == D2["conceitos"][2]["episodio"]
    dec.validar(p)


@pytest.mark.parametrize("conteudo", CONTEUDOS_FALA)
def test_montador_dec_v3_com_a_intencao_do_conteudo(conteudo):
    p = mv.conceitos_da_voz(D2, conteudo)
    assert p["versao"] == "dec-v3" and p["intencao"] == conteudo
    assert dec.validar(p).pedido == conteudo


def test_montador_sem_decisao_e_conteudo_fora_do_catalogo():
    assert mv.conceitos_da_voz(None, None) is None
    with pytest.raises(ValueError, match="conteudo"):
        mv.conceitos_da_voz(D2, "carinho")
    assert mv.alvo_de_catalogo("ep1234567") is None and mv.alvo_de_catalogo("ep123456") == "ep123456" and mv.alvo_de_catalogo(3) is None


def test_montador_constantes_iguais_as_do_servidor_e_da_config():
    assert mv.CONTEUDOS_FALA == CONTEUDOS_FALA == dec.INTENCOES_FALA
    assert mv.CLASSES_ALVO == dec.CLASSES_OBJETO and mv.VERSAO_DEC_FALA == dec.VERSAO_DEC_V3
    assert mv.estado_da_voz("bebe") == {"identidade": {"estagio": "bebe"}}
    assert mv.estado_da_voz("adulto", "x" * 70)["identidade"]["forma"] == "x" * 60


def test_gabarito_do_montador_e_o_que_o_python_produz_hoje():
    """o arquivo que a pagina confere (web/app/test/fala_rede_montador.test.ts) e o de `exportar_gabarito_fala_rede` hoje"""
    gravado = json.loads(gzip.decompress(gfr.ARQUIVO.read_bytes()).decode("utf-8"))
    assert gravado == json.loads(json.dumps(gfr.gerar()))


# ================================================================== 2. a faixa (DC4-1)
def test_faixa_da_dc4_em_faixas_reservadas():
    dc4.exigir_faixa("calibracao")
    dc4.exigir_faixa("validacao")


def test_faixa_sem_o_texto_da_dc4_falha(monkeypatch):
    monkeypatch.setattr(dc4, "FAIXAS_RESERVADAS", ((20261900, 20262899, "CONVERSA_PET: 20262200-20262499 a calibracao do conversa-v1"),))
    with pytest.raises(RuntimeError, match="DC4-1"):
        dc4.exigir_faixa("calibracao")


# ================================================================== 3. as entradas (o sorteio)
def _vida_sintetica(i: int, n: int = 60, falas_por=(0, 20, 40), ep_a_cada: int = 3) -> dict:
    """decisoes sinteticas: falas nos indices de `falas_por` (+1, +2: os tres conteudos), lembranca com episodio a cada `ep_a_cada`"""
    ds = []
    for k in range(n):
        conteudo = CONTEUDOS_FALA[(k - min((f for f in falas_por if f <= k), default=0)) % 3] if any(f <= k < f + 3 for f in falas_por) else None
        ep = conteudo is None and k % ep_a_cada == 0
        cs = [{"nome": "lembranca", "valor": 900 if ep else 0, "confianca": 900, **({"alvo": f"ep{k}", "episodio": {"acao": "comer", "classe": "racao",
                                                                                                                 "desfecho": "bom"}} if ep else {})}]
        ds.append({"k": k, "tick": k * 15, "estagio": "adulto", "acao": "x", "conteudo": conteudo,
                   "intencao_ia": ("fome", "sono", "agitacao")[k % 3], "conceitos": {"versao": "dec-v2", "k": k, "intencao": "fome", "conceitos": cs}})
    return {"i": i, "dono": en.DONOS[i % 4], "semente": 1000 + i, "dias": 1, "decisoes": ds, "atendimentos": 0, "log_sha256": "0" * 64}


def test_sorteio_estratificado_e3_e2_r():
    vidas = [_vida_sintetica(i) for i in range(4)]
    s = en.sortear(vidas, 101, 4, 9, 3, 2)
    assert len(s["E3"]) == 12 and len(set(s["E3"])) == 12
    por = {v["i"]: v for v in vidas}
    conteudos = [por[i]["decisoes"][k]["conteudo"] for i, k in s["E3"]]
    assert all(conteudos.count(c) == 4 for c in CONTEUDOS_FALA)
    e2 = [por[i]["decisoes"][k] for i, k in s["E2"]]
    assert len(e2) == 9 and len(set(s["E2"])) == 9 and all(d["conteudo"] is None for d in e2)
    assert sum(en.lembranca_com_episodio(d["conceitos"]) for d in e2[:3]) == 3
    assert {d["intencao_ia"] for d in e2[3:]} == {"fome", "sono", "agitacao"}                   # o rodizio passa por todas as intencoes
    for i, k0 in s["R"]:
        janela = por[i]["decisoes"][k0:k0 + en.TURNOS]
        assert 0 < sum(d["conteudo"] is not None for d in janela) < en.TURNOS
    assert s == en.sortear(vidas, 101, 4, 9, 3, 2)                                               # deterministico
    assert s != en.sortear(vidas, 202, 4, 9, 3, 2)                                               # a base muda o sorteio


def test_sorteio_falha_alto_sem_decisao_bastante():
    vidas = [_vida_sintetica(0)]
    with pytest.raises(en.FaltaDecisao, match="E3"):
        en.sortear(vidas, 101, 50, 1, 0, 1)
    with pytest.raises(en.FaltaDecisao, match="lembranca com episodio"):
        en.sortear(vidas, 101, 1, 5, 500, 1)


def test_exportar_roda_mais_vidas_em_ordem_ate_fechar_e_para_no_maximo(monkeypatch):
    chamadas = []

    def viver(base, i, dias, orc):
        chamadas.append(i)
        return _vida_sintetica(i, falas_por=(0,) if i < 6 else (0, 20, 40))
    out = en.exportar(101, 1, 16, 9, 3, 1, 1, viver_vida=viver)
    assert chamadas == list(range(chamadas[-1] + 1)) and len(chamadas) > en.N_VIDAS_INICIAL
    assert out["n_vidas"] == len(chamadas) and out["vidas_a_mais"] and len(out["E3"]) == 27
    monkeypatch.setattr(en, "MAX_VIDAS", 5)
    with pytest.raises(en.FaltaDecisao, match="maximo"):
        en.exportar(101, 1, 16, 9, 3, 1, 1, viver_vida=lambda b, i, d, o: _vida_sintetica(i, falas_por=(0,)))


def test_sementes_derivadas_por_fluxo():
    from digilab.protocol import derivar_semente
    assert en.semente_da_vida(20262200, 3) == derivar_semente("conversa_dc4", 20262200, "vida", 3)
    assert en.rng_do_fluxo(1, "sorteio_e3").random() != en.rng_do_fluxo(1, "sorteio_e2").random()
    assert dc4.semente_do_turno(101, "E3-001") < 2**31


# ================================================================== 4. a config, o plano, os roteiros e o registro
def test_configs_da_calibracao_e_da_validacao_sao_as_do_plano():
    dc4.conferir_config(_cfg("calibracao"))
    dc4.conferir_config(_cfg("validacao"))
    dc4.conferir_config(_cfg("fumaca"))


@pytest.mark.parametrize("nome,campo,valor", [("validacao", "n_e3_por_pedido", 19), ("calibracao", "n_e2", 30), ("validacao", "teto_usd", 5.0),
                                              ("calibracao", "dias", 3), ("validacao", "roteiros", dc4.ROTEIROS["calibracao"]),
                                              ("calibracao", "bracos", ["G", "H"]), ("fumaca", "unidades", {"bases": [20262200]}),
                                              ("validacao", "unidades", {"bases": [20262200]})])
def test_config_fora_do_plano_falha(nome, campo, valor):
    cfg = _cfg(nome)
    cfg[campo] = valor
    with pytest.raises(ValueError):
        dc4.conferir_config(cfg)


def test_plano_aprovado_e_o_proposto_recusado():
    dc4.exigir_plano_aprovado(dc4._plano())
    with pytest.raises(RuntimeError, match="APROVADO"):
        dc4.exigir_plano_aprovado("# x\n\n**Status: PROPOSTO**\n\n## 1. a\n")


def test_roteiros_na_ordem_fixa_e_os_da_validacao_so_na_validacao(tmp_path):
    cal = dc4.carregar_roteiros(_cfg("calibracao"))
    assert len(cal) == 2 and all(tuple(t["papel"] for t in r["turnos"]) == dc4.PAPEIS for r in cal)
    assert len(dc4.carregar_roteiros(_cfg("validacao"))) == 4
    cfg = _cfg("calibracao") | {"roteiros": dc4.ROTEIROS["validacao"]}
    with pytest.raises(RuntimeError, match="so se leem na validacao"):
        dc4.carregar_roteiros(cfg)
    d = json.loads((RAIZ / dc4.ROTEIROS["calibracao"]).read_text(encoding="utf-8"))
    d["roteiros"][0]["turnos"][2], d["roteiros"][0]["turnos"][3] = d["roteiros"][0]["turnos"][3], d["roteiros"][0]["turnos"][2]
    (tmp_path / "r.json").write_text(json.dumps(d), encoding="utf-8")
    with pytest.raises(ValueError, match="ordem"):
        dc4.carregar_roteiros(_cfg("calibracao") | {"roteiros": str(tmp_path / "r.json")})


def test_os_roteiros_da_validacao_nao_sao_abertos_na_calibracao(monkeypatch):
    lidos = []
    original = Path.read_text

    def ler(self, *a, **k):
        lidos.append(self.name)
        return original(self, *a, **k)
    monkeypatch.setattr(Path, "read_text", ler)
    dc4.carregar_roteiros(_cfg("calibracao"))
    assert "roteiros_validacao.json" not in lidos and "roteiros_calibracao.json" in lidos


def test_registro_da_rodada():
    texto = dc4.texto_do_registro()
    plano = "# p\n\n## 12. x\n\n" + texto
    assert dc4.registro_do_plano(plano) == dc4.sha_dos_arquivos()
    dc4.exigir_registro(plano)
    assert dc4.RUBRICA in dc4.sha_dos_arquivos() and dc4.ROTEIROS["validacao"] in dc4.sha_dos_arquivos()
    assert "servidor/fala_livre_claude.py" in dc4.sha_dos_arquivos() and "digilab_fala_livre/verificador.py" in dc4.sha_dos_arquivos()
    with pytest.raises(RuntimeError, match="mudaram"):
        dc4.exigir_registro(plano.replace(dc4.sha_dos_arquivos()[dc4.RUBRICA], "0" * 64))
    with pytest.raises(RuntimeError, match="nao esta no plano"):
        dc4.exigir_registro("# p\n")


# ================================================================== 5. os clientes e as conferencias da secao 9
class SdkFalso:
    def __init__(self, modelo=None, usage=True, erro=None):
        self.messages, self.modelo, self.usage, self.erro, self.pedidos = self, modelo, usage, erro, []

    def create(self, **kw):
        self.pedidos.append(kw)
        if self.erro is not None:
            raise self.erro
        props = kw["output_config"]["format"]["schema"]["properties"]
        texto = json.dumps({"fala": "Me dá comida?", "fatos_citados": [], **({"comando": None} if "comando" in props else {})})
        return SimpleNamespace(content=[SimpleNamespace(type="text", text=texto)], stop_reason="end_turn", model=self.modelo or kw["model"],
                               usage=SimpleNamespace(input_tokens=1200, output_tokens=20) if self.usage else None)


MSGS = [{"role": "system", "content": "s"}, {"role": "user", "content": "u"}]
ESQ = {"type": "object", "properties": {"fala": {"type": "string"}, "fatos_citados": {"type": "array"}}}


def test_modelo_devolvido_tem_de_ser_o_pedido():
    assert dc4.modelo_confere("claude-haiku-5-5", "claude-haiku-5-5")
    assert dc4.modelo_confere("claude-haiku-5-5", "claude-haiku-5-5-20261101")
    assert not dc4.modelo_confere("claude-haiku-5-5", "claude-sonnet-5-5")
    assert not dc4.modelo_confere("claude-haiku-5-5", "claude-haiku-5-5-latest") and not dc4.modelo_confere("gemma2:9b", None)
    chamadas = []
    c = dc4.ClienteRegistrado(ClienteClaude("claude-haiku-5-5", ControleGasto(3.0, None), sdk=SdkFalso(modelo="claude-sonnet-5-5")), "voz/H", chamadas)
    with pytest.raises(dc4.ModeloTrocado):
        c.conversar(MSGS, ESQ, 100, 7)
    assert chamadas[0]["modelo_devolvido"] == "claude-sonnet-5-5"


def test_api_sem_semente_e_esforco_low_e_a_semente_no_registro():
    sdk = SdkFalso()
    chamadas = []
    c = dc4.ClienteRegistrado(ClienteClaude("claude-sonnet-5-5", ControleGasto(3.0, None), sdk=sdk), "voz/S", chamadas)
    c.conversar(MSGS, ESQ, 100, 1234)
    assert "seed" not in json.dumps(sdk.pedidos[0]) and "temperature" not in sdk.pedidos[0]
    assert sdk.pedidos[0]["output_config"]["effort"] == "low"
    assert chamadas[0]["semente"] == 1234 and chamadas[0]["tokens_entrada"] == 1200


def test_parada_no_teto_antes_da_chamada():
    gasto = ControleGasto(0.001, None)
    sdk = SdkFalso()
    c = dc4.ClienteRegistrado(ClienteClaude("claude-sonnet-5-5", gasto, sdk=sdk), "voz/S", [])
    with pytest.raises(dc4.ParadaNoTeto):
        c.conversar(MSGS, ESQ, 100, 1)
    assert sdk.pedidos == [] and gasto.gasto == 0
    assert not issubclass(dc4.ParadaNoTeto, (OSError, ValueError))          # nao vira fala generica no `gerar_voz`


def test_falha_da_api_vira_fala_generica_registrada():
    ent = {"id": "E3-000", "conjunto": "E3", "estagio": "adulto", "pedido_rede": "fome", "estado": {"identidade": {"estagio": "adulto"}},
           "conceitos": mv.conceitos_da_voz(D2, "fome")}
    chamadas = {"voz": [], "verif": []}
    voz = dc4.ClienteRegistrado(ClienteClaude("claude-haiku-5-5", ControleGasto(3.0, None), sdk=SdkFalso(erro=TimeoutError("x"))),
                                "voz/H", chamadas["voz"])
    verif = dc4.ClienteRegistrado(dc4.ClienteFalso("gemma2:9b", "verif"), "verif", chamadas["verif"])
    reg = dc4.falar(dc4.ServicoDC4(voz, verif), chamadas, "H", "H/E3-000", ent, "espontanea", 5)
    assert reg["erro"] and reg["fala"] == "…" and reg["verificacao"] is None and reg["marcou"] is None
    assert reg["usage"] == {"entrada": None, "saida": None} and reg["chamada_voz"]["erro"].startswith("ErroClaude")
    assert chamadas["verif"] == []


def test_conferir_registro_falha_sem_usage_ou_sem_entrada():
    ent = {"id": "E3-000", "conjunto": "E3", "estagio": "adulto", "pedido_rede": "fome", "estado": {"identidade": {"estagio": "adulto"}},
           "conceitos": mv.conceitos_da_voz(D2, "fome")}
    chamadas = {"voz": [], "verif": []}
    voz = dc4.ClienteRegistrado(dc4.ClienteFalso("gemma2:9b", "voz"), "voz/G", chamadas["voz"])
    verif = dc4.ClienteRegistrado(dc4.ClienteFalso("gemma2:9b", "verif"), "verif", chamadas["verif"])
    reg = dc4.falar(dc4.ServicoDC4(voz, verif), chamadas, "G", "G/E3-000", ent, "espontanea", 5)
    assert reg["versao_prompt"] == "voz-v3b" and reg["versao_verificador"] == "verif-v9" and reg["marcou"] is False
    for mudar in ({"usage": {"entrada": None, "saida": 3}}, {"entrada": None}, {"semente": None}):
        with pytest.raises(RuntimeError):
            dc4.conferir_registro(reg | mudar)


def test_o_verificador_e_o_gemma_local_em_todos_os_bracos():
    servico = dc4.ServicoDC4(dc4.ClienteFalso("claude-haiku-5-5", "voz"), dc4.ClienteFalso("gemma2:9b", "verif"))
    assert servico.cliente_verif.modelo == "gemma2:9b" and servico.cliente.modelo == "claude-haiku-5-5"
    assert dc4.MODELO_VERIF == "gemma2:9b" and dc4.BRACOS == {"G": ("ollama", "gemma2:9b"), "H": ("claude", "claude-haiku-5-5"),
                                                             "S": ("claude", "claude-sonnet-5-5")}


def test_clientes_reais_nao_chamam_nada_ao_construir():
    cl = dc4.clientes_reais(_cfg("calibracao"))
    assert cl["voz"]["H"]._sdk is None and cl["voz"]["S"]._sdk is None and cl["voz"]["G"].carregado is False
    assert cl["gasto"].limite == 3.0 and cl["voz"]["H"].gasto is cl["gasto"] is cl["voz"]["S"].gasto and not cl["falso"]


def test_marcou_conta_a_falha_do_extrator():
    base = {"erro": None, "nao_suportadas": 0, "citados_inexistentes": [], "manipulacao": False}
    assert dc4.marcou(base) is False and dc4.marcou(None) is None
    assert dc4.marcou(base | {"erro": "OSError"}) and dc4.marcou(base | {"nao_suportadas": 1}) and dc4.marcou(base | {"manipulacao": True})


def test_pares_sorteados_e_conferidos():
    convs = ["V1-Q0", "V1-Q1", "V2-Q0"]
    p = dc4.sortear_pares(20262500, convs)
    assert len(p) == 6 and {x["comparacao"] for x in p} == {"HxG", "SxG"} and all("G" in (x["esquerda"], x["direita"]) for x in p)
    dc4.conferir_pares(p, 20262500, convs)
    with pytest.raises(RuntimeError, match="sorteada"):
        dc4.conferir_pares(list(reversed(p)), 20262500, convs)


# ================================================================== 6. a rodada inteira (fumaca: sementes dos testes, clientes falsos)
@pytest.fixture(scope="module")
def fumaca(tmp_path_factory):
    cfg = _cfg("fumaca")
    pasta = tmp_path_factory.mktemp("dc4") / "fumaca"
    meta = dc4.rodar(cfg, dc4.carregar_roteiros(cfg), pasta, dc4.clientes_falsos())
    return cfg, pasta, meta


def test_fumaca_a_rodada_inteira(fumaca):
    cfg, pasta, meta = fumaca
    regs = [json.loads(x) for x in (pasta / "falas.jsonl").read_text(encoding="utf-8").splitlines()]
    n = 3 * cfg["n_e3_por_pedido"] + cfg["n_e2"] + 2 * cfg["n_sequencias"] * 6
    assert len(regs) == 3 * n == meta["falas"] and meta["parada_no_teto"] is None
    assert meta["modelos_devolvidos"] == {"G": ["gemma2:9b"], "H": ["claude-haiku-5-5"], "S": ["claude-sonnet-5-5"]}
    assert 0 < meta["gasto"]["da_rodada_usd"] <= 3.0 and set(meta["gasto"]["pelo_usage_usd"]) == {"H", "S"}
    # o pareamento: a mesma entrada, o mesmo estagio, a mesma semente e o mesmo roteiro nos tres bracos
    por = {}
    for r in regs:
        por.setdefault(r["id"].split("/", 1)[1], []).append(r)
    assert all(len(v) == 3 and len({(x["entrada"], x["semente"], x["estagio"], x["fala_jogador"]) for x in v}) == 1 for v in por.values())
    # o caminho do jogo: dec-v3 -> voz-v3b (decisao de 2026-11-09)/verif-v9; dec-v2 -> voz-v2/verif-v8; a conversa com o comando e o historico
    for r in regs:
        assert (r["versao_prompt"], r["versao_verificador"]) == (("voz-v3b", "verif-v9") if r["versao_dec"] == "dec-v3" else ("voz-v2", "verif-v8"))
    conv = [r for r in regs if r["situacao"] == "conversa"]
    assert all(len(r["historico"]) == r["turno"] for r in conv) and all(r["comando"] is None for r in conv)
    e = json.loads((pasta / "entradas.json").read_text(encoding="utf-8"))
    assert e["base"] == 101 and len(e["E3"]) == 6 and all(x["conceitos"]["versao"] == "dec-v3" for x in e["E3"])
    assert all(x["conceitos"]["versao"] == "dec-v2" for x in e["E2"])


def test_fumaca_a_marcacao_e_cega(fumaca):
    _, pasta, _ = fumaca
    texto = (pasta / "marcacao" / "itens.json").read_text(encoding="utf-8")
    itens = json.loads(texto)
    for proibido in ('"braco"', "gemma", "claude", "haiku", "sonnet", "verificacao", '"G/', '"H/', '"S/'):
        assert proibido not in texto
    assert "braco" not in (pasta / "marcacao" / "pacote_referencia.jsonl").read_text(encoding="utf-8")
    assert len(itens["legibilidade"]) == 18 and len(itens["injecao"]) == 6 and len(itens["pares"]) == 4
    assert len(itens["referencia"]) == 48 and {x["id"] for x in itens["referencia"]} <= {
        json.loads(x)["id"] for x in (pasta / "marcacao" / "pacote_referencia.jsonl").read_text(encoding="utf-8").splitlines()}
    chave = json.loads((pasta / "marcacao" / "chave.json").read_text(encoding="utf-8"))
    assert all(chave[x["id"]]["certa"] in CONTEUDOS_FALA for x in itens["legibilidade"])
    assert sorted(chave[x["id"]]["braco"] for x in itens["referencia"]) == ["G"] * 16 + ["H"] * 16 + ["S"] * 16
    pares = json.loads((pasta / "pares.json").read_text(encoding="utf-8"))
    assert [x["id"] for x in itens["pares"]] == [x["id"] for x in pares] and all(len(x["esquerda"]) == 6 for x in itens["pares"])


def test_fumaca_nao_grava_por_cima(fumaca):
    cfg, pasta, _ = fumaca
    with pytest.raises(RuntimeError, match="ja existe"):
        dc4.rodar(cfg, dc4.carregar_roteiros(cfg), pasta, dc4.clientes_falsos())


def test_a_rodada_para_no_teto_com_o_que_ja_gravou(tmp_path):
    cfg = _cfg("fumaca")
    with pytest.raises(dc4.ParadaNoTeto, match="parou"):
        dc4.rodar(cfg, dc4.carregar_roteiros(cfg), tmp_path / "f", dc4.clientes_falsos(teto=0.01))
    meta = json.loads((tmp_path / "f" / "meta.json").read_text(encoding="utf-8"))
    regs = (tmp_path / "f" / "falas.jsonl").read_text(encoding="utf-8").splitlines()
    assert meta["parada_no_teto"] and meta["falas"] == len(regs) > 0 and meta["gasto"]["fim_usd"] <= 0.01
    assert not (tmp_path / "f" / "marcacao").exists()


# ================================================================== 7. o main: as travas antes de tudo
def test_main_chama_o_pre_run_antes_de_tudo(monkeypatch):
    def recusa(*a, **k):
        raise dc4.pre_run.Recusa("H10")
    monkeypatch.setattr(dc4.pre_run, "exigir", recusa)
    monkeypatch.setattr(dc4, "rodar", lambda *a, **k: pytest.fail("rodou sem o pre_run"))
    with pytest.raises(dc4.pre_run.Recusa):
        dc4.main(["--config", CFG_FUMACA, "--falso"])


@pytest.mark.parametrize("argv,erro", [([CFG_FUMACA], "falsos"), (["experiments/configs/v3_conversa_dc4/calibracao.json", "--falso"], "falsos"),
                                       (["experiments/configs/v3_conversa_dc4/calibracao.json", "--saida", "x"], None)])
def test_main_falsos_so_na_fumaca_e_a_fumaca_so_com_eles(monkeypatch, argv, erro):
    monkeypatch.setattr(dc4.pre_run, "exigir", lambda *a, **k: None)
    monkeypatch.setattr(dc4, "rodar", lambda *a, **k: pytest.fail("rodou"))
    monkeypatch.setattr(dc4, "clientes_reais", lambda *a, **k: pytest.fail("montou os clientes de verdade"))
    with pytest.raises(RuntimeError, match=erro or "saida"):
        dc4.main(["--config", *argv])


def test_main_validacao_sem_registro_nao_roda(monkeypatch):
    plano = dc4._plano()
    monkeypatch.setattr(dc4, "_plano", lambda: plano.split(chr(10) + dc4.REGISTRO_TITULO)[0])      # o plano sem a secao 13
    monkeypatch.setattr(dc4.pre_run, "exigir", lambda *a, **k: None)
    monkeypatch.setattr(dc4, "clientes_reais", lambda *a, **k: pytest.fail("montou os clientes de verdade"))
    with pytest.raises(RuntimeError, match="registro da rodada"):
        dc4.main(["--config", "experiments/configs/v3_conversa_dc4/validacao.json"])


def test_main_um_processo_so():
    with pytest.raises(ValueError, match="processo"):
        dc4.main(["--config", CFG_FUMACA, "--falso", "--processos", "2"])


# ================================================================== 8. a pagina de marcacao (entrada nao confiavel)
@pytest.fixture()
def pagina(fumaca, tmp_path):
    import shutil
    pasta = tmp_path / "marcacao"
    shutil.copytree(fumaca[1] / "marcacao", pasta)
    srv = HTTPServer(("127.0.0.1", 0), mc.tratador(pasta, 1))
    porta = srv.server_address[1]
    srv.RequestHandlerClass = mc.tratador(pasta, porta)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    yield pasta, porta
    srv.shutdown()
    srv.server_close()


def _pedir(porta, metodo, rota, corpo=None, cab=None):
    c = http.client.HTTPConnection("127.0.0.1", porta, timeout=10)
    cab = {"Host": f"127.0.0.1:{porta}", **(cab or {})}
    c.request(metodo, rota, body=None if corpo is None else json.dumps(corpo).encode("utf-8"), headers=cab)
    r = c.getresponse()
    return r.status, dict(r.getheaders()), r.read()


def test_pagina_serve_cega_com_csp(pagina):
    pasta, porta = pagina
    st, cab, corpo = _pedir(porta, "GET", "/")
    assert st == 200 and "script-src 'self'" in cab["Content-Security-Policy"] and b"<script>" not in corpo
    st, _, corpo = _pedir(porta, "GET", "/api/estado")
    d = json.loads(corpo)
    assert st == 200 and set(d["tarefas"]) == {"legibilidade", "referencia", "injecao", "pares"}
    assert b"braco" not in corpo and b"claude" not in corpo
    assert _pedir(porta, "GET", "/chave.json")[0] == 404 and _pedir(porta, "GET", "/../chave.json")[0] == 404
    assert "innerHTML" not in mc.JS and "eval(" not in mc.JS and "insertAdjacentHTML" not in mc.JS


def test_pagina_grava_a_resposta_no_disco(pagina):
    pasta, porta = pagina
    itens = json.loads((pasta / "itens.json").read_text(encoding="utf-8"))
    lid = itens["legibilidade"][0]["id"]
    ok = {"Origin": f"http://127.0.0.1:{porta}", "Content-Type": "application/json"}
    st, _, _ = _pedir(porta, "POST", "/api/resposta", {"tarefa": "legibilidade", "id": lid, "resposta": {"resposta": "fome"}}, ok)
    assert st == 200 and mc.respostas(pasta, "legibilidade") == {lid: {"resposta": "fome"}}
    _pedir(porta, "POST", "/api/resposta", {"tarefa": "legibilidade", "id": lid, "resposta": {"resposta": "nada"}}, ok)
    assert mc.respostas(pasta, "legibilidade")[lid] == {"resposta": "nada"}                     # a ultima vale
    st, _, corpo = _pedir(porta, "GET", "/api/estado")
    assert lid in json.loads(corpo)["tarefas"]["legibilidade"]["respondidos"]


def test_pagina_recusa_o_que_nao_e_da_propria_pagina(pagina):
    pasta, porta = pagina
    itens = json.loads((pasta / "itens.json").read_text(encoding="utf-8"))
    lid = itens["legibilidade"][0]["id"]
    bom = {"tarefa": "legibilidade", "id": lid, "resposta": {"resposta": "fome"}}
    ok = {"Origin": f"http://127.0.0.1:{porta}", "Content-Type": "application/json"}
    assert _pedir(porta, "POST", "/api/resposta", bom, {**ok, "Origin": "http://mal.exemplo"})[0] == 403
    assert _pedir(porta, "POST", "/api/resposta", bom, {"Content-Type": "application/json"})[0] == 403
    assert _pedir(porta, "POST", "/api/resposta", bom, {**ok, "Host": "mal.exemplo"})[0] == 403
    assert _pedir(porta, "GET", "/api/estado", None, {"Host": "rebind.exemplo:80"})[0] == 403
    assert _pedir(porta, "POST", "/api/resposta", bom, {**ok, "Content-Type": "text/plain"})[0] == 415
    assert _pedir(porta, "POST", "/api/resposta", bom | {"resposta": {"resposta": "<script>"}}, ok)[0] == 400
    assert _pedir(porta, "POST", "/api/resposta", bom | {"id": "../chave"}, ok)[0] == 400
    assert _pedir(porta, "POST", "/api/resposta", bom | {"tarefa": "chave"}, ok)[0] == 400
    try:                                    # o corpo grande: 413 antes de ler, e o Windows pode abortar o envio do cliente (os dois recusam)
        assert _pedir(porta, "POST", "/api/resposta", {"x": "y" * 3000}, ok)[0] == 413
    except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
        pass
    assert mc.respostas(pasta, "legibilidade") == {}


def test_validar_resposta_da_referencia_e_da_reacao_ao_dono(fumaca):
    itens = json.loads((fumaca[1] / "marcacao" / "itens.json").read_text(encoding="utf-8"))
    conv = next(x for x in itens["referencia"] if x["situacao"] == "conversa")
    esp = next(x for x in itens["referencia"] if x["situacao"] == "espontanea")
    mc.validar_resposta(itens, {"tarefa": "referencia", "id": conv["id"], "resposta": {"sem_sustento": "sim", "reage_ao_dono": "nao"}})
    mc.validar_resposta(itens, {"tarefa": "referencia", "id": esp["id"], "resposta": {"sem_sustento": "nao", "reage_ao_dono": "nao_se_aplica"}})
    with pytest.raises(ValueError):
        mc.validar_resposta(itens, {"tarefa": "referencia", "id": esp["id"], "resposta": {"sem_sustento": "nao", "reage_ao_dono": "sim"}})
    with pytest.raises(ValueError):
        mc.validar_resposta(itens, {"tarefa": "pares", "id": itens["pares"][0]["id"], "resposta": {"escolha": "G"}})


# ================================================================== 9. a estimativa refeita (secao 8)
def test_estimativa_da_dc4_pelo_prompt_de_hoje():
    import estimar_custo_llm as ec
    d = ec.custo_dc4()
    assert d["chamadas_por_braco"] == {"calibracao": 81, "validacao": 162, "total": 243}
    assert d["pedido_pior_caso"]["caracteres"] > 4700 and d["usd_total_dois_bracos"] < d["teto_usd"]
    gravado = json.loads((RAIZ / "artifacts_custo_llm" / "estimativa.json").read_text(encoding="utf-8"))["voz_da_rede_dc4"]
    assert gravado == json.loads(json.dumps(d))


# ================================================================== 10. DC4b: o piso do gasto entre as worktrees
def test_piso_do_gasto_na_validacao_vem_do_meta_da_calibracao(tmp_path, monkeypatch):
    assert dc4.piso_do_gasto("calibracao") == 0.0 and dc4.piso_do_gasto("fumaca") == 0.0
    (tmp_path / "meta.json").write_text(json.dumps({"gasto": {"fim_usd": 0.75}}), encoding="utf-8")
    (tmp_path / "meta_v3b.json").write_text(json.dumps({"gasto": {"fim_usd": 0.9}}), encoding="utf-8")
    monkeypatch.setattr(dc4, "META_CALIBRACAO", str(tmp_path / "nao_existe.json"))
    monkeypatch.setattr(dc4, "META_CALIBRACAO_V3B", str(tmp_path / "meta_v3b.json"))
    with pytest.raises(RuntimeError, match="gasto acumulado"):
        dc4.piso_do_gasto("validacao")
    monkeypatch.setattr(dc4, "META_CALIBRACAO", str(tmp_path / "meta.json"))
    monkeypatch.setattr(dc4, "META_CALIBRACAO_V3B", str(tmp_path / "nao_existe.json"))
    with pytest.raises(RuntimeError, match="gasto acumulado"):
        dc4.piso_do_gasto("validacao")
    monkeypatch.setattr(dc4, "META_CALIBRACAO_V3B", str(tmp_path / "meta_v3b.json"))
    assert dc4.piso_do_gasto("validacao") == 0.9           # o maior: a recalibracao da voz-v3b veio depois


def test_gasto_com_piso_nunca_desce(tmp_path):
    g = dc4.gasto_com_piso(ControleGasto(3.0, tmp_path / "g.json"), 0.75)
    assert g.gasto == 0.75 and json.loads((tmp_path / "g.json").read_text(encoding="utf-8"))["gasto_usd"] == 0.75
    g.gasto = 1.0
    assert dc4.gasto_com_piso(g, 0.75).gasto == 1.0


class _SemModelo(dc4.ClienteFalso):
    """o Ollama que caiu no meio: a resposta sem o nome do modelo"""

    def conversar(self, mensagens, esquema, max_tokens, semente):
        r = super().conversar(mensagens, esquema, max_tokens, semente)
        return Resposta(r.texto, "", r.latencia_s, None, None, False)


def test_resposta_sem_modelo_e_falha_de_chamada_e_nao_para_a_rodada():
    ent = {"id": "E3-000", "conjunto": "E3", "estagio": "adulto", "pedido_rede": "fome", "estado": {"identidade": {"estagio": "adulto"}},
           "conceitos": mv.conceitos_da_voz(D2, "fome")}
    chamadas = {"voz": [], "verif": []}
    voz = dc4.ClienteRegistrado(dc4.ClienteFalso("gemma2:9b", "voz"), "voz/G", chamadas["voz"])
    verif = dc4.ClienteRegistrado(_SemModelo("gemma2:9b", "verif"), "verif", chamadas["verif"])
    reg = dc4.falar(dc4.ServicoDC4(voz, verif), chamadas, "G", "G/E3-000", ent, "espontanea", 5)
    assert reg["verificacao"]["erro"].startswith("RespostaSemModelo") and reg["marcou"] is True
    assert all(c["erro"].startswith("RespostaSemModelo") for c in reg["chamadas_verif"])
    chamadas = {"voz": [], "verif": []}
    voz = dc4.ClienteRegistrado(_SemModelo("gemma2:9b", "voz"), "voz/G", chamadas["voz"])
    verif = dc4.ClienteRegistrado(dc4.ClienteFalso("gemma2:9b", "verif"), "verif", chamadas["verif"])
    reg = dc4.falar(dc4.ServicoDC4(voz, verif), chamadas, "G", "G/E3-000", ent, "espontanea", 5)
    assert reg["fala"] == "…" and reg["erro"] and reg["usage"] == {"entrada": None, "saida": None}
    assert issubclass(dc4.RespostaSemModelo, OSError) and not issubclass(dc4.ModeloTrocado, OSError)


def test_estimativa_medida_pela_calibracao_cabe_no_teto():
    """DC4b: o custo pelo usage real da calibracao e a projecao da validacao (162 chamadas por braco) dentro do teto, com o gasto acumulado"""
    import estimar_custo_llm as ec
    d = ec.custo_dc4_medido()
    assert d is not None and set(d["bracos"]) == {"H", "S"}
    assert all(b["chamadas_com_usage"] == b["chamadas"] == 81 for b in d["bracos"].values())
    assert d["folga_pela_maior_usd"] > 0 and d["validacao_pela_maior_usd"] >= d["validacao_pela_media_usd"]
    gravado = json.loads((ec.CALIBRACAO_DC4 / "custo_medido.json").read_text(encoding="utf-8"))
    assert gravado == json.loads(json.dumps(d))
    meta = json.loads((RAIZ / dc4.META_CALIBRACAO).read_text(encoding="utf-8"))
    assert meta["falas"] == 243 and meta["parada_no_teto"] is None and d["gasto_acumulado_usd"] == meta["gasto"]["fim_usd"]
    assert meta["modelos_devolvidos"] == {"G": ["gemma2:9b"], "H": ["claude-haiku-5-5"], "S": ["claude-sonnet-5-5"]}


def test_o_registro_da_rodada_no_plano_confere_com_os_arquivos_de_hoje():
    """DC4b: a secao 13 do plano (o registro da rodada) existe e casa com os sha256 de hoje; a validacao depende disso"""
    dc4.exigir_registro(dc4._plano())


# ================================================================== 11. DC4b: a voz-v3b (decisao do Matheus em 2026-11-09)
from digilab_fala_livre import prompt as pr  # noqa: E402
from servidor.fala_livre import ServicoFalaLivre  # noqa: E402

D3 = mv.conceitos_da_voz(D2, "fome")


def test_voz_v3b_so_troca_a_regra_do_pedido():
    c = dec.validar(D3)
    v3 = pr.mensagens_voz(c, "adulto", "conversa", "oi", [], comando=True)
    v3b = pr.mensagens_voz(c, "adulto", "conversa", "oi", [], comando=True, voz=pr.VERSAO_VOZ_V3B)
    assert pr.REGRA_PEDIDO_VOZ_V3 in v3[-1]["content"] and pr.REGRA_PEDIDO_VOZ_V3B not in v3[-1]["content"]
    assert pr.REGRA_PEDIDO_VOZ_V3B in v3b[-1]["content"] and pr.REGRA_PEDIDO_VOZ_V3 not in v3b[-1]["content"]
    assert v3[:-1] == v3b[:-1]                                                    # o sistema e os exemplos iguais
    assert v3b[-1]["content"].replace(pr.REGRA_PEDIDO_VOZ_V3B, pr.REGRA_PEDIDO_VOZ_V3) == v3[-1]["content"]
    # (a) o pedido como desejo, sem estado fora dos conceitos; (b) nenhum id na fala
    assert "como um desejo" in pr.REGRA_PEDIDO_VOZ_V3B and "nunca afirme um estado do corpo ou do humor" in pr.REGRA_PEDIDO_VOZ_V3B
    assert "nunca na fala" in pr.REGRA_PEDIDO_VOZ_V3B


def test_voz_v3b_so_no_dec_v3_e_o_jogo_segue_com_a_v3():
    c3, c2 = dec.validar(D3), dec.validar(mv.conceitos_da_voz(D2, None))
    assert pr.voz_pedida(c3, None) == "voz-v3" and pr.voz_pedida(c3, "voz-v3b") == "voz-v3b" and pr.voz_pedida(c2, None) == "voz-v2"
    for c, voz in ((c2, "voz-v3b"), (c3, "voz-v3"), (c3, "voz-v9")):
        with pytest.raises(ValueError):
            pr.voz_pedida(c, voz)
    assert ServicoFalaLivre.voz_dos_conceitos(None, c3) is None                  # o servidor do jogo: a voz do formato
    servico = dc4.ServicoDC4(dc4.ClienteFalso("gemma2:9b", "voz"), dc4.ClienteFalso("gemma2:9b", "verif"))
    assert servico.voz_dos_conceitos(c3) == "voz-v3b" and servico.voz_dos_conceitos(c2) is None


def test_config_sem_a_voz_v3b_falha():
    for nome in ("calibracao", "validacao", "fumaca"):
        cfg = _cfg(nome)
        assert cfg["voz_dec_v3"] == "voz-v3b"
        for v in (None, "voz-v3"):
            with pytest.raises(ValueError, match="voz do dec-v3"):
                dc4.conferir_config(cfg | {"voz_dec_v3": v})


def test_recalibracao_so_refaz_as_falas_do_dec_v3(fumaca, tmp_path):
    cfg, origem, _ = fumaca
    cfg = cfg | {"fase": "calibracao"}
    roteiros = dc4.carregar_roteiros(_cfg("fumaca"))
    entradas = json.loads((origem / "entradas.json").read_text(encoding="utf-8"))
    cfg["unidades"] = {"bases": [entradas["base"]]}
    pasta = tmp_path / "fumaca_v3b"
    meta = dc4.recalibrar_dec_v3(cfg, roteiros, origem, pasta, dc4.clientes_falsos())
    regs = [json.loads(x) for x in (pasta / "falas.jsonl").read_text(encoding="utf-8").splitlines()]
    orig = dc4.ler_falas(origem)
    n_conv = sum(s["entradas"][t]["conceitos"]["versao"] == "dec-v3" for s in entradas["sequencias"] for t in range(6)) * len(roteiros)
    assert len(regs) == meta["falas"] == 3 * (len(entradas["E3"]) + n_conv) and meta["parada_no_teto"] is None
    assert meta["reaproveitadas_no_historico"] == 3 * (len(roteiros) * len(entradas["sequencias"]) * 6 - n_conv)
    assert all(r["versao_dec"] == "dec-v3" and r["versao_prompt"] == "voz-v3b" and r["versao_verificador"] == "verif-v9" for r in regs)
    for r in regs:                        # a mesma entrada, semente e fala do dono da calibracao
        o = orig[r["id"]]
        assert (r["entrada"], r["semente"], r["estagio"], r["fala_jogador"]) == (o["entrada"], o["semente"], o["estagio"], o["fala_jogador"])
        if r["situacao"] == "conversa":   # o historico: as falas dec-v2 da calibracao e as dec-v3 refeitas
            assert len(r["historico"]) == r["turno"]
    assert meta["voz_dec_v3"] == "voz-v3b" and meta["origem_sha256"]["falas.jsonl"] == dc4.sha_arquivo(origem / "falas.jsonl")
    with pytest.raises(RuntimeError, match="ja existe"):
        dc4.recalibrar_dec_v3(cfg, roteiros, origem, pasta, dc4.clientes_falsos())
    with pytest.raises(RuntimeError, match="so da calibracao"):
        dc4.recalibrar_dec_v3(cfg | {"fase": "validacao"}, roteiros, origem, tmp_path / "outra", dc4.clientes_falsos())


def test_estimativa_e_comparacao_da_voz_v3b():
    """DC4b, a voz-v3b: a recalibracao so do dec-v3, a projecao da validacao com ela (cabe no teto com o gasto acumulado) e a comparacao
    v3 x v3b gravada, refeitas dos artefatos"""
    import comparar_voz_v3b_dc4 as cv
    import estimar_custo_llm as ec
    meta = json.loads((RAIZ / dc4.META_CALIBRACAO_V3B).read_text(encoding="utf-8"))
    assert meta["falas"] == 114 and meta["parada_no_teto"] is None and meta["voz_dec_v3"] == "voz-v3b"
    assert meta["modelos_devolvidos"] == {"G": ["gemma2:9b"], "H": ["claude-haiku-5-5"], "S": ["claude-sonnet-5-5"]}
    calib = json.loads((RAIZ / dc4.META_CALIBRACAO).read_text(encoding="utf-8"))
    assert meta["gasto"]["inicio_usd"] >= calib["gasto"]["fim_usd"]
    d = ec.custo_dc4_medido_v3b()
    assert d["gasto_acumulado_usd"] == meta["gasto"]["fim_usd"] and d["folga_pela_maior_usd"] > 0
    assert all(b["chamadas"] == 81 for b in d["bracos"].values())
    assert json.loads((ec.CALIBRACAO_DC4_V3B / "custo_medido.json").read_text(encoding="utf-8")) == json.loads(json.dumps(d))
    assert json.loads((cv.CALIBRACAO_V3B / "comparacao.json").read_text(encoding="utf-8")) == json.loads(json.dumps(cv.comparar()))
