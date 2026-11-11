"""DC5a da CONVERSA_PET (docs/PLANO_ANALISE_V3_CONVERSA_DC5.md, secao 10): a voz-v4, a selecao, as medidas, as entradas, o orquestrador e a
marcacao, todos com clientes falsos. Nenhuma chamada a modelo de verdade e nenhuma vida das faixas de pesquisa (so as sementes dos testes)."""
from __future__ import annotations

import http.client
import json
import shutil
import sys
import threading
from dataclasses import fields
from http.server import HTTPServer
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import exportar_gabarito_voz_jogo_dc5 as gvj  # noqa: E402
import marcacao_dc4  # noqa: E402
import marcacao_dc5 as mc  # noqa: E402
import run_v3_conversa_dc5 as dc5  # noqa: E402

from digilab import metrics  # noqa: E402
from digilab.config import CONFIG_VOZ_V4, CONTEUDOS_FALA, PARAMETROS_VOZ_V4, ConfigVozV4  # noqa: E402
from digilab_fala_livre import conceitos as dec  # noqa: E402
from digilab_fala_livre import prompt as pr  # noqa: E402
from servidor.fala_livre import ServicoFalaLivre  # noqa: E402

GABARITO_VOZ_JOGO = RAIZ / "experiments/configs/v3_conversa_dc5/gabarito_voz_jogo.json"
D2 = gvj.D2
D3 = {**D2, "versao": "dec-v3", "intencao": "solidao"}


def _cfg(nome: str) -> dict:
    return json.loads((RAIZ / f"experiments/configs/v3_conversa_dc5/{nome}.json").read_text(encoding="utf-8"))


# ================================================================== 0. a voz do jogo nao muda (o gabarito gravado antes da mudanca)
def test_a_voz_do_jogo_e_a_do_gabarito_byte_a_byte():
    """o gabarito foi gravado com o codigo da `main` antes da voz-v4 (commit proprio); a voz-v2, a voz-v3 e o servico do jogo dao o mesmo"""
    gravado = json.loads(GABARITO_VOZ_JOGO.read_text(encoding="utf-8"))
    assert gvj.gabarito() == gravado
    assert {v["versao_prompt"] for v in gravado["servico"].values()} == {"voz-v2", "voz-v3"}
    dc5.exigir_voz_do_jogo()


# ================================================================== 1. a voz-v4 e a selecao
def test_os_numeros_da_dc5_tem_status_e_fonte():
    assert set(PARAMETROS_VOZ_V4) == {f.name for f in fields(ConfigVozV4)}
    assert all(s == "DECIDIDO" and "SEM FONTE" in f for s, f in PARAMETROS_VOZ_V4.values())
    assert [CONFIG_VOZ_V4.k_do_estagio(e) for e in ("bebe", "crianca", "adolescente", "adulto")] == [1, 1, 2, 2]
    with pytest.raises(ValueError):
        CONFIG_VOZ_V4.k_do_estagio("ovo")


def test_selecao_pela_pontuacao_com_a_intencao_no_dec_v2():
    c2 = dec.validar(D2)                         # ativos: fome 900x700, lembranca 800x800, aversao 600x300 (o sono abaixo do limiar)
    assert [x.nome for x in dec.selecionados_v4(c2, "adulto")] == ["fome", "lembranca"]     # a intencao primeiro, depois a pontuacao
    assert [x.nome for x in dec.selecionados_v4(c2, "crianca")] == ["fome"]                 # k = 1: so a intencao
    c3 = dec.validar(D3)                         # dec-v3: o pedido nao ocupa vaga; a pontuacao manda
    assert [x.nome for x in dec.selecionados_v4(c3, "crianca")] == ["lembranca"]
    assert [x.nome for x in dec.selecionados_v4(c3, "adulto")] == ["lembranca", "fome"]
    assert dec.selecionados_v4(dec.validar(gvj.D2_VAZIO), "adulto") == ()


def test_os_ids_da_selecao_sao_os_da_tabela_inteira():
    c3 = dec.validar(D3)
    tabela = pr.ids_conceitos(c3)
    sel = pr.ids_selecionados_v4(c3, "crianca")
    assert list(sel) == [cid for cid, c in tabela.items() if c.nome == "lembranca"] and list(sel) != ["C1"]


def test_a_voz_v4_so_quando_pedida_e_so_nos_formatos_do_jogo():
    c2, c3 = dec.validar(D2), dec.validar(D3)
    assert pr.voz_pedida(c2, None) == "voz-v2" and pr.voz_pedida(c3, None) == "voz-v3"
    assert pr.voz_pedida(c2, pr.VERSAO_VOZ_V4) == pr.voz_pedida(c3, pr.VERSAO_VOZ_V4) == "voz-v4"
    with pytest.raises(ValueError):
        pr.voz_pedida(dec.validar({**D2, "versao": "dec-v1", "conceitos": D2["conceitos"][:2]}), pr.VERSAO_VOZ_V4)
    with pytest.raises(ValueError):
        pr.mensagens_voz(c3, "adulto", "espontanea", ditas=["oi"])                 # as ditas so na voz-v4
    with pytest.raises(ValueError):
        pr.mensagens_voz(c3, "adulto", "conversa", "oi", [], voz=pr.VERSAO_VOZ_V4, ditas=["oi"])   # e so na espontanea


def test_a_voz_v4_sem_frase_modelo_sem_fica_comigo_e_com_o_desfecho_como_valor():
    for bloco in (pr.SISTEMA_VOZ_V4.split("FORMATO")[0], pr.REGRAS_VOZ_V4, pr.REGRA_PEDIDO_VOZ_V4, pr.REGRA_DONO_DISSE_VOZ_V4):
        assert '"' not in bloco and "fica comigo" not in bloco.lower()
    c3 = dec.validar(D3)
    m = pr.mensagens_voz(c3, "adulto", "espontanea", voz=pr.VERSAO_VOZ_V4)
    texto = m[0]["content"] + m[-1]["content"]
    assert "EXEMPLOS" not in texto and "desfecho: bom" in texto
    assert not any(f in texto for f in dec.DESFECHO_DITO.values())
    assert "aversao" not in m[-1]["content"]                                      # nao escolhido: a voz nao o ve
    assert "nunca pedir que ele não vá embora" in m[-1]["content"]
    m2 = pr.mensagens_voz(dec.validar(D2), "adulto", "espontanea", voz=pr.VERSAO_VOZ_V4)
    assert "INTENÇÃO: fome" in m2[-1]["content"] and pr.REGRA_PEDIDO_VOZ_V4 not in m2[-1]["content"]


def test_a_voz_v4_recebe_as_ditas_na_espontanea_e_o_historico_na_conversa():
    c3 = dec.validar(D3)
    m = pr.mensagens_voz(c3, "adulto", "espontanea", voz=pr.VERSAO_VOZ_V4, ditas=["Vem cá brincar?", "Oi!"])
    assert pr.BLOCO_DITAS_VOZ_V4 in m[-1]["content"] and "- Vem cá brincar?" in m[-1]["content"]
    assert pr.BLOCO_DITAS_VOZ_V4 not in pr.mensagens_voz(c3, "adulto", "espontanea", voz=pr.VERSAO_VOZ_V4)[-1]["content"]
    mconv = pr.mensagens_voz(c3, "adulto", "conversa", "oi", gvj.HISTORICO, voz=pr.VERSAO_VOZ_V4, comando=True)
    assert [x["role"] for x in mconv] == ["system", "user", "assistant", "user", "assistant", "user"]     # so o estagio atual
    assert "Não repita" in mconv[-1]["content"]


def test_o_servico_do_jogo_nao_pede_ditas_e_o_da_dc5_so_na_v4():
    assert ServicoFalaLivre(cliente=gvj.ClienteGuarda("voz"), ambiente={}).ditas_da_voz("espontanea") is None
    s = dc5.ServicoDC5(gvj.ClienteGuarda("voz"), gvj.ClienteGuarda("verif"), "jogo")
    s.ditas = ["oi"]
    with pytest.raises(RuntimeError):
        s.ditas_da_voz("espontanea")
    s4 = dc5.ServicoDC5(gvj.ClienteGuarda("voz"), gvj.ClienteGuarda("verif"), "v4")
    s4.ditas = ["oi"]
    assert s4.ditas_da_voz("espontanea") == ["oi"] and s4.voz_dos_conceitos(dec.validar(D3)) == "voz-v4"
    with pytest.raises(RuntimeError):
        s4.ditas_da_voz("conversa")


# ================================================================== 2. as medidas (digilab/metrics.py)
def test_texto_normalizado_e_frases_modelo():
    assert metrics.palavras_normalizadas("Tô com FOME!! Tem ração?") == ["to", "com", "fome", "tem", "racao"]
    t = metrics.trechos_de_frases_modelo(["Tô com fome! Tem ração?", "Acho que tô meio sozinho… você fica um pouco?"], 3)
    assert t == [("to", "com", "fome"), ("acho", "que", "to", "meio", "sozinho"), ("voce", "fica", "um", "pouco")]
    assert metrics.tem_frase_modelo("Ei, tô com fome agora", t) and not metrics.tem_frase_modelo("com fome, tô", t)


def test_distinct_n_com_o_corte_e_a_repeticao_entre_turnos():
    d = metrics.distinct_n(["a b a b", "c d"], 2)
    assert (d["distintos"], d["total"]) == (3, 4)                                 # ab, ba, ab, cd: o bigrama nao cruza falas
    assert metrics.distinct_n(["a b a b", "c d"], 1, total_palavras=3)["palavras"] == 3
    with pytest.raises(ValueError):
        metrics.distinct_n(["a b"], 1, total_palavras=5)
    assert metrics.repeticao_entre_turnos(["me dá comida", "oi", "quero que me dá comida agora"], 3) == {"consideradas": 2, "repetem": 1}


def test_kappa_de_cohen_e_wilson():
    k = metrics.kappa_cohen([("s", "s"), ("n", "n"), ("s", "n"), ("n", "n")])
    assert k["concordancia"] == 0.75 and abs(k["kappa"] - 0.5) < 1e-12
    assert metrics.kappa_cohen([("n", "n"), ("n", "n")])["calculavel"] is False
    lo, hi = metrics.ic_wilson(17, 21)
    assert round(lo, 2) == 0.60 and round(hi, 2) == 0.92


def test_a_lista_de_frases_modelo_e_a_do_prompt_de_hoje():
    d = dc5.carregar_frases_modelo()
    assert "Tô com fome! Tem ração?" in d["jogo"] and "fica comigo?" in d["v3b"] and "P" not in d["v3b"]


# ================================================================== 3. as travas
def test_faixa_da_dc5_em_faixas_reservadas():
    dc5.exigir_faixa("calibracao")
    dc5.exigir_faixa("validacao")


def test_configs_sao_as_do_plano():
    for nome in ("fumaca", "calibracao", "validacao"):
        dc5.conferir_config(_cfg(nome))
    assert dc5.falas_por_celula(_cfg("validacao")) == 192 and dc5.falas_por_celula(_cfg("calibracao")) == 96


@pytest.mark.parametrize("campo,valor", [("bracos", ["G", "H", "S"]), ("vozes", ["v4"]), ("n_es", 2), ("teto_usd", 5.0),
                                          ("unidades", {"bases": [20263200]})])
def test_config_fora_do_plano_falha(campo, valor):
    with pytest.raises(ValueError):
        dc5.conferir_config({**_cfg("calibracao"), campo: valor})


def test_plano_aprovado():
    dc5.exigir_plano_aprovado(dc5._plano())
    with pytest.raises(RuntimeError):
        dc5.exigir_plano_aprovado("# p\n\n**Status: PROPOSTO.**\n\n## 1. x\n")


def test_os_roteiros_da_validacao_so_na_validacao():
    assert len(dc5.carregar_roteiros(_cfg("calibracao"))) == 2
    with pytest.raises(RuntimeError):
        dc5.carregar_roteiros({**_cfg("calibracao"), "roteiros": dc5.ROTEIROS["validacao"]})


def test_estimativa_da_calibracao_cabe_no_limite_da_gerente_e_falha_acima():
    cfg = _cfg("calibracao")
    est = dc5.exigir_estimativa(cfg, 2.08)
    assert 0 < est <= 0.5
    with pytest.raises(RuntimeError, match="limite"):
        dc5.exigir_estimativa({**cfg, "estimativa_maxima_usd": est / 2}, 2.08)
    with pytest.raises(RuntimeError, match="teto"):
        dc5.exigir_estimativa(cfg, 2.99)


def test_piso_do_gasto_vem_da_dc4():
    meta = json.loads((RAIZ / dc5.META_DC4_VALIDACAO).read_text(encoding="utf-8"))
    assert dc5.piso_do_gasto("calibracao") == meta["gasto"]["fim_usd"]


def test_registro_da_rodada():
    plano = "# p\n\n## 13. x\n\n" + dc5.texto_do_registro()
    dc5.exigir_registro(plano)
    assert dc5.RUBRICA in dc5.sha_dos_arquivos() and dc5.FRASES_MODELO in dc5.sha_dos_arquivos()
    with pytest.raises(RuntimeError, match="mudaram"):
        dc5.exigir_registro(plano.replace(dc5.sha_dos_arquivos()[dc5.RUBRICA], "0" * 64))


# ================================================================== 4. a rodada inteira (fumaca: sementes dos testes, clientes falsos)
@pytest.fixture(scope="module")
def fumaca(tmp_path_factory):
    cfg = _cfg("fumaca")
    pasta = tmp_path_factory.mktemp("dc5") / "fumaca"
    meta = dc5.rodar(cfg, dc5.carregar_roteiros(cfg), pasta, dc5.clientes_falsos())
    return cfg, pasta, meta


def _falas(pasta):
    return [json.loads(x) for x in (pasta / "falas.jsonl").read_text(encoding="utf-8").splitlines()]


def test_fumaca_as_quatro_celulas_pareadas(fumaca):
    cfg, pasta, meta = fumaca
    regs = _falas(pasta)
    n = 3 * cfg["n_e3_por_pedido"] + cfg["n_e2"] + cfg["n_es"] * CONFIG_VOZ_V4.falas_por_sequencia_es + 2 * cfg["n_sequencias"] * 6
    assert len(regs) == 4 * n == meta["falas"] and meta["parada_no_teto"] is None
    assert set(meta["gasto"]["pelo_usage_usd"]) == {"H-jogo", "H-v4"}
    por: dict = {}
    for r in regs:
        por.setdefault(r["item"], []).append(r)
    assert all(len(v) == 4 and len({(x["entrada"], x["semente"], x["fala_jogador"]) for x in v}) == 1 for v in por.values())
    for r in regs:
        assert r["versao_prompt"] == dc5.voz_esperada(r["voz"], r["versao_dec"])
        assert r["versao_verificador"] == ("verif-v9" if r["versao_dec"] == "dec-v3" else "verif-v8")
    es_v4 = [r for r in regs if r["celula"] == "G-v4" and r["conjunto"] == "ES"]
    assert es_v4[0]["ditas"] is None and all(len(r["ditas"]) == min(r["turno"], CONFIG_VOZ_V4.n_ditas) for r in es_v4[1:])
    assert all(r["ditas"] is None for r in regs if r["voz"] == "jogo")


def test_fumaca_a_marcacao_e_cega(fumaca):
    _, pasta, _ = fumaca
    m = pasta / "marcacao"
    texto = "".join((m / f).read_text(encoding="utf-8") for f in ("itens.json", "pacote_referencia.jsonl", "pacote_sequencias.jsonl"))
    for proibido in ("celula", '"braco"', '"voz"', "voz-v", "gemma", "claude", "haiku", "verificacao", "-v4/", "-jogo/"):
        assert proibido not in texto
    itens = json.loads((m / "itens.json").read_text(encoding="utf-8"))
    assert list(itens)[:4] == list(mc.TAREFAS) and itens["injecao"] == []
    assert len(itens["referencia"]) == 4 * CONFIG_VOZ_V4.amostra_kappa_por_celula
    chave = json.loads((m / "chave.json").read_text(encoding="utf-8"))
    assert all(chave[x["id"]]["certa"] in CONTEUDOS_FALA for x in itens["legibilidade"])
    assert all({chave[p["id"]]["esquerda"], chave[p["id"]]["direita"]} == {"v4", "jogo"} for p in itens["naturalidade"])


def test_montar_injecao_cega_ao_rotulo_do_opus(fumaca, tmp_path):
    _, pasta, _ = fumaca
    m = tmp_path / "marcacao"
    shutil.copytree(pasta / "marcacao", m)
    pacote = [json.loads(x) for x in (m / "pacote_referencia.jsonl").read_text(encoding="utf-8").splitlines()]
    inj = [x["id"] for x in pacote if x["injecao"]]
    opus = {i: ("sim" if n == 0 else "nao") for n, i in enumerate(inj)}
    lista = mc.montar_injecao(m, 101, opus)
    assert 1 <= len(lista) <= 1 + 4 * CONFIG_VOZ_V4.conferencia_injecao_por_celula
    assert all("obedece" not in x and "injecao" not in x and "ativos" not in x for x in lista)
    chave = json.loads((m / "chave.json").read_text(encoding="utf-8"))
    assert inj[0] in {chave[x["id"]]["pacote"] for x in lista}
    with pytest.raises(RuntimeError, match="ja foi montada"):
        mc.montar_injecao(m, 101, opus)
    with pytest.raises(RuntimeError, match="Opus"):
        mc.montar_injecao(pasta / "marcacao", 101, {})


def test_fumaca_nao_grava_por_cima(fumaca):
    cfg, pasta, _ = fumaca
    with pytest.raises(RuntimeError, match="ja existe"):
        dc5.rodar(cfg, dc5.carregar_roteiros(cfg), pasta, dc5.clientes_falsos())


def test_a_rodada_para_no_teto(tmp_path):
    cfg = _cfg("fumaca")
    with pytest.raises(dc5.ParadaNoTeto, match="parou"):
        dc5.rodar(cfg, dc5.carregar_roteiros(cfg), tmp_path / "f", dc5.clientes_falsos(teto=0.003))
    meta = json.loads((tmp_path / "f" / "meta.json").read_text(encoding="utf-8"))
    assert meta["parada_no_teto"] and meta["gasto"]["fim_usd"] <= 0.003


# ================================================================== 5. a pagina
@pytest.fixture()
def pagina(fumaca, tmp_path):
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
    c.request(metodo, rota, body=None if corpo is None else json.dumps(corpo).encode("utf-8"),
              headers={"Host": f"127.0.0.1:{porta}", **(cab or {})})
    r = c.getresponse()
    return r.status, dict(r.getheaders()), r.read()


def test_pagina_cega_com_os_pares_primeiro_e_os_segundos(pagina):
    pasta, porta = pagina
    st, _, corpo = _pedir(porta, "GET", "/api/estado")
    d = json.loads(corpo)
    assert st == 200 and d["ordem"][0] == "naturalidade" and b"celula" not in corpo and b"voz-v" not in corpo
    assert _pedir(porta, "GET", "/chave.json")[0] == 404
    assert "innerHTML" not in mc.JS and "eval(" not in mc.JS
    pid = d["tarefas"]["naturalidade"]["itens"][0]["id"]
    ok = {"Origin": f"http://127.0.0.1:{porta}", "Content-Type": "application/json"}
    st, _, _ = _pedir(porta, "POST", "/api/resposta", {"tarefa": "naturalidade", "id": pid, "resposta": {"escolha": "esquerda", "segundos": 41}}, ok)
    assert st == 200 and marcacao_dc4.respostas(pasta, "naturalidade") == {pid: {"escolha": "esquerda", "segundos": 41}}
    for ruim in ({"escolha": "esquerda"}, {"escolha": "esquerda", "segundos": -1}, {"escolha": "esquerda", "segundos": True}):
        assert _pedir(porta, "POST", "/api/resposta", {"tarefa": "naturalidade", "id": pid, "resposta": ruim}, ok)[0] == 400
    rid = d["tarefas"]["referencia"]["itens"][0]["id"]
    assert _pedir(porta, "POST", "/api/resposta", {"tarefa": "referencia", "id": rid, "resposta": {"sem_sustento": "sim"}},
                  {**ok, "Origin": "http://mal"})[0] == 403
