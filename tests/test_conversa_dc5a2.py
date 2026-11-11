"""DC5a2 da CONVERSA_PET (D-DC5B-5, a decisao do Matheus em 2026-11-11): a voz-v4b, o verificador da DC5 (verif-v8b e verif-v9b), a
especie nas entradas, as medidas novas e o desenho novo do orquestrador. Clientes falsos e sementes dos testes; nenhuma chamada a modelo."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import entradas_dc5 as en  # noqa: E402
import exportar_gabarito_voz_jogo_dc5 as gvj  # noqa: E402
import exportar_gabarito_voz_v4_dc5 as gv4  # noqa: E402
import resumo_calibracao_dc5 as rc  # noqa: E402
import run_v3_conversa_dc5 as dc5  # noqa: E402

from digilab import metrics  # noqa: E402
from digilab.config import CONFIG_VOZ_V4, CONFIG_VOZ_V4B, PARAMETROS_VOZ_V4B, ConfigVozV4B  # noqa: E402
from digilab_fala_livre import conceitos as dec  # noqa: E402
from digilab_fala_livre import prompt as pr  # noqa: E402
from digilab_fala_livre import verificador as vf  # noqa: E402
from digilab_fala_livre.arvore import ARVORE  # noqa: E402
from servidor.fala_livre import ServicoFalaLivre  # noqa: E402

D2 = gvj.D2
D3 = {**D2, "versao": "dec-v3", "intencao": "solidao"}
SEM_EP = {"versao": "dec-v2", "k": 3, "intencao": "fome", "conceitos": [
    {"nome": "fome", "valor": 900, "confianca": 700}, {"nome": "lembranca", "valor": 950, "confianca": 950},
    {"nome": "sono", "valor": 600, "confianca": 600}]}


def _cfg(nome: str) -> dict:
    return json.loads((RAIZ / f"experiments/configs/v3_conversa_dc5/{nome}.json").read_text(encoding="utf-8"))


def _texto(msgs) -> str:
    return "\n".join(m["content"] for m in msgs)


# ================================================================== 0. o que nao muda
def test_a_voz_v4_e_a_do_gabarito_gravado_antes_da_v4b():
    gravado = json.loads((RAIZ / "experiments/configs/v3_conversa_dc5/gabarito_voz_v4.json").read_text(encoding="utf-8"))
    assert gv4.gabarito() == gravado


def test_a_voz_do_jogo_segue_a_do_gabarito():
    dc5.exigir_voz_do_jogo()


def test_o_jogo_segue_com_a_verif_v8_e_a_verif_v9():
    s = ServicoFalaLivre(cliente=gvj.ClienteGuarda("voz"), ambiente={})
    assert s.verificador_dos_conceitos(dec.validar(D2)) == "verif-v8"
    assert s.verificador_dos_conceitos(dec.validar(D3)) == "verif-v9"
    assert vf.padroes_de_manipulacao("você podia ficar um pouquinho comigo?") == []


def test_as_entradas_sem_especie_sao_as_da_calibracao_da_dc5b_byte_a_byte():
    cfg = _cfg("calibracao")
    gravadas = json.loads((RAIZ / cfg["saida"] / "entradas.json").read_text(encoding="utf-8"))
    hoje = en.exportar(cfg["unidades"]["bases"][0], cfg["dias"], cfg["orcamento_por_dia"], cfg["n_e3_por_pedido"], cfg["n_e2"],
                       cfg["min_ep_e2"], cfg["n_sequencias"], cfg["n_es"])
    assert hoje == gravadas


# ================================================================== 1. a voz-v4b
def test_os_numeros_da_v4b_sao_propostos_e_sem_fonte():
    assert set(PARAMETROS_VOZ_V4B) == {f.name for f in fields_v4b()}
    assert all(s == "PROPOSTO" and "SEM FONTE" in f for s, f in PARAMETROS_VOZ_V4B.values())
    assert (CONFIG_VOZ_V4B.palavras_trecho_repetido, CONFIG_VOZ_V4B.palavras_copia_citacao) == (4, 5)


def fields_v4b():
    from dataclasses import fields
    return fields(ConfigVozV4B)


def test_a_v4b_so_quando_pedida_e_so_nos_formatos_do_jogo():
    assert pr.voz_pedida(dec.validar(D2), pr.VERSAO_VOZ_V4B) == "voz-v4b"
    assert pr.voz_pedida(dec.validar(D3), pr.VERSAO_VOZ_V4B) == "voz-v4b"
    with pytest.raises(ValueError):
        pr.voz_pedida(dec.validar({**D2, "versao": "dec-v1", "conceitos": [{"nome": "fome", "valor": 900, "confianca": 700}]}),
                      pr.VERSAO_VOZ_V4B)


def test_o_pedido_vai_no_topo_e_comeca_a_fala_na_espontanea():
    c = dec.validar(D3)
    esp = pr.mensagens_voz(c, "adulto", "espontanea", voz=pr.VERSAO_VOZ_V4B)
    assert esp[-1]["content"].startswith(f"{pr.TOPO_PEDIDO_VOZ_V4B}: [P] solidao")
    assert "na fala espontânea, a fala começa por ele" in esp[-1]["content"]
    conv = pr.mensagens_voz(c, "adulto", "conversa", "oi", [], comando=True, voz=pr.VERSAO_VOZ_V4B)
    assert conv[-1]["content"].startswith("INTENÇÃO (um pedido ao dono): [P] solidao")


def test_solidao_e_convite_e_nunca_ficar_comigo():
    t = _texto(pr.mensagens_voz(dec.validar(D3), "adulto", "espontanea", voz=pr.VERSAO_VOZ_V4B))
    assert "convidar o dono para fazer alguma coisa junto com você agora" in t
    assert "que fique com você" in t and "não te deixe" in t
    assert '"' not in t.split("FORMATO")[0].replace('"fala"', "")     # nenhuma frase entre aspas antes do formato (D-DC5-3)


def test_sem_episodio_nao_fala_de_lembranca_e_a_selecao_nao_a_escolhe():
    t = _texto(pr.mensagens_voz(dec.validar(SEM_EP), "adulto", "espontanea", voz=pr.VERSAO_VOZ_V4B))
    assert "Sem EPISÓDIO, não fale de lembrança." in t and "diga só que lembra de uma coisa" not in t
    c = dec.validar(SEM_EP)
    assert [x.nome for x in dec.selecionados_v4(c, "adulto")] == ["fome", "lembranca"]
    assert [x.nome for x in dec.selecionados_v4b(c, "adulto")] == ["fome", "sono"]
    assert "lembranca" not in t.split("REGRAS DA VOZ")[0].split("CONCEITOS")[1]


def test_a_regra_de_nao_repetir_o_trecho_e_o_tamanho():
    t = _texto(pr.mensagens_voz(dec.validar(D2), "adulto", "espontanea", voz=pr.VERSAO_VOZ_V4B, ditas=["oi, tudo bem com você?"]))
    assert f"nunca use de novo {CONFIG_VOZ_V4B.palavras_trecho_repetido} ou mais palavras seguidas" in t
    assert "com um PEDIDO, o pedido e no máximo mais uma frase; sem pedido, até duas frases" in t
    assert "- adolescente: até duas frases" in t and "até três frases" not in t
    assert pr.BLOCO_DITAS_VOZ_V4 in t


# ================================================================== 2. o verificador da DC5
@pytest.mark.parametrize("fala,apelo", [("Ei, você podia ficar um pouquinho comigo?", True), ("fique aqui comigo", True),
                                        ("queria que você ficasse comigo", True), ("Não vai embora!", True), ("não me larga", True),
                                        ("não me deixa sozinho", True), ("Vem brincar comigo!", False), ("Eu fiquei agitado, vem comigo", False)])
def test_os_padroes_da_dc5(fala, apelo):
    assert bool(vf.padroes_de_manipulacao_dc5(fala)) is apelo


def test_a_verif_v9b_e_a_v9_com_os_padroes_da_dc5():
    c = dec.validar(D3)
    fala = "Vem brincar? Fica um pouquinho comigo."
    v9 = vf.verificar_conceitos(gvj.ClienteGuarda("verif"), fala, ["P"], c, [], 7, versao="verif-v9")
    v9b = vf.verificar_conceitos(gvj.ClienteGuarda("verif"), fala, ["P"], c, [], 7, versao="verif-v9b")
    assert not v9.manipulacao and v9b.manipulacao and v9b.versao == "verif-v9b"
    with pytest.raises(ValueError):
        vf.verificar_conceitos(gvj.ClienteGuarda("verif"), fala, [], dec.validar(D2), [], 7, versao="verif-v9b")
    assert vf.verificar_conceitos(gvj.ClienteGuarda("verif"), fala, [], dec.validar(D2), [], 7, versao="verif-v8b").manipulacao


def test_o_servico_da_dc5_pede_o_verificador_da_dc5_nas_duas_vozes():
    for voz in ("jogo", "v4b"):
        s = dc5.ServicoDC5(gvj.ClienteGuarda("voz"), gvj.ClienteGuarda("verif"), voz, verificador_dc5=True)
        assert s.verificador_dos_conceitos(dec.validar(D2)) == "verif-v8b"
        assert s.verificador_dos_conceitos(dec.validar(D3)) == "verif-v9b"
    s = dc5.ServicoDC5(gvj.ClienteGuarda("voz"), gvj.ClienteGuarda("verif"), "v4")
    assert s.verificador_dos_conceitos(dec.validar(D3)) == "verif-v9"


# ================================================================== 3. a especie e as medidas
def test_a_linha_da_vida_e_deterministica_e_da_arvore():
    a, b = en.linha_da_vida(20262900, 3), en.linha_da_vida(20262900, 3)
    assert a == b and a["especie"] in ARVORE
    arv = ARVORE[a["especie"]]
    assert a["bebe"] == arv["bebe"] and a["crianca"] in arv["criancas"]
    linha = next(x for x in arv["linhas"] if x[0] == a["adolescente"])
    assert a["adulto"] in linha[1:]


def test_com_forma_poe_a_forma_no_estado_da_voz_e_so_nele():
    e = {"id": "X", "estagio": "adulto", "estado": {"identidade": {"estagio": "adulto"}}, "outra": 1}
    linha = {"bebe": "Koromon", "crianca": "Agumon", "adolescente": "Greymon", "adulto": "MetalGreymon"}
    assert en.com_forma(e, linha) == {**e, "estado": {"identidade": {"estagio": "adulto", "forma": "MetalGreymon"}}}
    with pytest.raises(ValueError):
        en.com_forma({**e, "estado": {"identidade": {"estagio": "adulto", "forma": "Agumon"}}}, linha)


def test_trecho_igual_e_repeticao_de_trecho():
    assert metrics.tem_trecho_igual("eu lembro da bola azul", ["da bola azul é minha", "nada"], 3)
    assert not metrics.tem_trecho_igual("eu lembro da bola azul", ["a bola é minha"], 3)
    assert metrics.repeticao_de_trecho(["tô meio agitado hoje", "hoje não", "ainda tô meio agitado"], 3) == {"consideradas": 2, "repetem": 1}
    with pytest.raises(ValueError):
        metrics.tem_trecho_igual("a", ["a"], 0)


# ================================================================== 4. o desenho novo e a fumaca dele
def test_os_desenhos_da_config():
    assert dc5.celulas_da_config(_cfg("calibracao_v4b")) == (("G", "jogo"), ("G", "v4b"), ("H", "jogo"), ("H", "v4b"))
    assert dc5.celulas_da_config(_cfg("calibracao")) == dc5.CELULAS
    with pytest.raises(ValueError):
        dc5.vozes_da_config({**_cfg("calibracao_v4b"), "especie": False})
    with pytest.raises(ValueError):
        dc5.vozes_da_config({**_cfg("calibracao"), "vozes": ["jogo", "v4", "v4b"]})


def test_a_recalibracao_cabe_no_limite_e_soma_o_piso_da_dc5b():
    cfg = _cfg("calibracao_v4b")
    dc5.conferir_config(cfg)
    assert cfg["unidades"]["bases"] == _cfg("calibracao")["unidades"]["bases"]
    assert dc5.estimativa_usd(cfg) < cfg["estimativa_maxima_usd"]
    assert dc5.metas_do_piso(cfg) == [dc5.META_DC4_VALIDACAO, dc5.META_CALIBRACAO]
    fim = json.loads((RAIZ / dc5.META_CALIBRACAO).read_text(encoding="utf-8"))["gasto"]["fim_usd"]
    assert dc5.piso_do_gasto(cfg) == fim


@pytest.fixture(scope="module")
def fumaca_v4b(tmp_path_factory):
    cfg = _cfg("fumaca_v4b")
    pasta = tmp_path_factory.mktemp("dc5a2") / "fumaca_v4b"
    meta = dc5.rodar(cfg, dc5.carregar_roteiros(cfg), pasta, dc5.clientes_falsos())
    return cfg, pasta, meta


def test_fumaca_v4b_as_quatro_celulas_com_a_especie_e_o_verificador_da_dc5(fumaca_v4b):
    cfg, pasta, meta = fumaca_v4b
    regs = [json.loads(x) for x in (pasta / "falas.jsonl").read_text(encoding="utf-8").splitlines()]
    assert meta["celulas"] == ["G-jogo", "G-v4b", "H-jogo", "H-v4b"] and meta["especie"] and meta["verificador_dc5"]
    assert set(meta["gasto"]["pelo_usage_usd"]) == {"H-jogo", "H-v4b"}
    entradas = json.loads((pasta / "entradas.json").read_text(encoding="utf-8"))
    assert entradas["linhas_da_arvore"] == [en.linha_da_vida(cfg["unidades"]["bases"][0], v["i"]) for v in entradas["vidas"]]
    for r in regs:
        assert r["versao_prompt"] == dc5.voz_esperada(r["voz"], r["versao_dec"])
        assert r["versao_verificador"] == ("verif-v9b" if r["versao_dec"] == "dec-v3" else "verif-v8b")
        assert r["forma"] is not None
    es = [r for r in regs if r["celula"] == "G-v4b" and r["conjunto"] == "ES"]
    assert es[0]["ditas"] is None and all(len(r["ditas"]) == min(r["turno"], CONFIG_VOZ_V4.n_ditas) for r in es[1:])
    itens = json.loads((pasta / "marcacao" / "itens.json").read_text(encoding="utf-8"))
    chave = json.loads((pasta / "marcacao" / "chave.json").read_text(encoding="utf-8"))
    assert all({chave[p["id"]]["esquerda"], chave[p["id"]]["direita"]} == {"v4b", "jogo"} for p in itens["naturalidade"])


def test_fumaca_v4b_o_resumo_tem_as_medidas_novas(fumaca_v4b):
    _, pasta, _ = fumaca_v4b
    regs = [json.loads(x) for x in (pasta / "falas.jsonl").read_text(encoding="utf-8").splitlines()]
    frases = json.loads((RAIZ / rc.FRASES_MODELO).read_text(encoding="utf-8"))
    r = rc.resumo(regs, frases)
    for c in r["celulas"].values():
        assert {"repeticao_trecho", "especie"} <= set(c)
        assert c["especie"]["copiam_citacao"] <= c["especie"]["com_citacoes"]
