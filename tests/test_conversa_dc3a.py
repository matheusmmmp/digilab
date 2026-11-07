"""A DC3a (docs/PLANO_ANALISE_V3_CONVERSA_DC3.md, secao 10): a subchave `fala_unidades` do modular (3.1), o dono que atende (secao 2), a
`fala_nas_decisoes` do metrics.py (4.1 e 4.2), o orquestrador da run (secoes 5, 7 e 11, com a fumaca nas sementes dos testes e a analise com
dados sinteticos) e o `ganho_conteudo` da condicao da 3.1. Desligada, a vida de hoje sai byte a byte: tests/test_gabarito_conversa_dc3.py."""
from __future__ import annotations

import json
import random
import sys
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import run_v3_conversa_dc3 as dc  # noqa: E402

from digilab.config import (CARACTERISTICAS_DIGIBRAIN, CONFIG_DIGIBRAIN_INATOS, CONFIG_FALA_UNIDADES, CONTEUDOS_FALA,  # noqa: E402
                            PARAMETROS_DECODIFICADOR, PARAMETROS_FALA_UNIDADES, ConfigDecodificador, ConfigDigibrain,
                            ConfigFalaUnidades)
from digilab.digibrain._comum import mul  # noqa: E402
from digilab.digibrain.impulso import Impulso  # noqa: E402
from digilab.digibrain.plast import Plasticidade, linha_da_opcao  # noqa: E402
from digilab.events import AcaoUsuario  # noqa: E402
from digilab.metrics import fala_nas_decisoes, maior_urgencia_da_fala  # noqa: E402

S = CONFIG_DIGIBRAIN_INATOS.escala
LIGADA = replace(dc.config_do_braco("LAB"), fala_unidades=True)
BOOT = {"reamostragens": 200, "semente": 7, "nivel": 0.95}


# ================================================================== a config
def test_a_subchave_vem_desligada_e_nao_se_combina_com_as_outras_subchaves_de_hoje():
    assert ConfigDigibrain().fala_unidades is False
    for outra in ("passeio", "credito_corrida", "redecidir_evento", "facetas_mem"):
        with pytest.raises(ValueError):
            replace(LIGADA, **{outra: True})
    with pytest.raises(TypeError):
        ConfigDigibrain(fala_unidades=1)
    with pytest.raises(ValueError):
        ConfigFalaUnidades(ganho_conteudo=-1)
    assert PARAMETROS_FALA_UNIDADES["ganho_conteudo"][0] == "PROPOSTO"


def test_o_limiar_de_desfecho_e_o_de_valor_do_decodificador_estao_decididos():
    c = ConfigDecodificador()
    assert (c.limiar_desfecho, c.limiar_valor) == (S // 8, S // 2)
    assert PARAMETROS_DECODIFICADOR["limiar_desfecho"][0] == PARAMETROS_DECODIFICADOR["limiar_valor"][0] == "DECIDIDO"
    assert PARAMETROS_DECODIFICADOR["limiar_confianca"][0] == "PROPOSTO"


def test_o_ganho_conteudo_e_o_da_calibracao_nas_sementes_dos_testes():
    art = json.loads((RAIZ / "artifacts_v3_conversa_dc3" / "ganho_conteudo.json").read_text(encoding="utf-8"))
    assert art["escolhido"] == CONFIG_FALA_UNIDADES.ganho_conteudo
    assert set(art["sementes"]) <= {101, 202, 303, 404, 505} and art["modo"] == "ignora"
    r = {int(g): v["razao"] for g, v in art["por_ganho"].items()}
    assert min(r, key=lambda g: (abs(r[g] - 1), g)) == art["escolhido"]


# ================================================================== o M-IMPULSO e o M-PLAST
def _sens(**kw) -> dict:
    return {"pos": (0, 0), "objetos": [], "ha_cheiro": False, **kw}


def test_as_tres_unidades_de_fala_no_lugar_do_chamar_na_ordem_dos_conteudos():
    hoje = [u["chave"] for u in Impulso.alvos(_sens(), None) if u["acao"] == "chamar_atencao"]
    assert hoje == [("chamar_atencao", None, None)]
    fala = [u for u in Impulso.alvos(_sens(), None, fala=True) if u["acao"] == "chamar_atencao"]
    assert [u["chave"] for u in fala] == [("chamar_atencao", c, None) for c in CONTEUDOS_FALA]
    assert all(u["tipo"] is None and u["objeto"] is None for u in fala)


def test_o_inato_de_cada_unidade_e_o_do_chamar_com_o_termo_do_conteudo_vezes_o_ganho():
    idx = {c: j for j, c in enumerate(CARACTERISTICAS_DIGIBRAIN)}
    z = [S] + [0] * (len(CARACTERISTICAS_DIGIBRAIN) - 1)
    z[idx["fome_sem_comida"]], z[idx["u_higiene"]], z[idx["u_solidao"]], z[idx["u_estresse"]] = 600, 300, 900, 100
    w = dict(dict(CONFIG_DIGIBRAIN_INATOS.w0)["chamar_atencao"])
    comum = mul(w["vies"], S, S) + mul(w["u_estresse"], 100, S)
    t = {"fome": mul(w["fome_sem_comida"], 600, S), "higiene": mul(w["u_higiene"], 300, S), "solidao": mul(w["u_solidao"], 900, S)}
    for g in (S, 3 * S // 2, 0):
        imp = Impulso(None, LIGADA, ConfigFalaUnidades(ganho_conteudo=g))
        assert imp.inato_fala(z) == {c: comum + mul(g, t[c], S) for c in CONTEUDOS_FALA}
    # com o ganho S, a soma das tres e o chamar de hoje mais duas vezes o que nao e de conteudo
    inato_hoje = comum + sum(t.values())
    assert sum(Impulso(None, LIGADA, ConfigFalaUnidades(ganho_conteudo=S)).inato_fala(z).values()) == inato_hoje + 2 * comum


def test_uma_linha_de_h_por_unidade_de_fala_creditada_pelo_p2_de_hoje():
    p = Plasticidade(LIGADA)
    linhas = list(p.H)
    assert linhas[4:7] == [f"chamar_atencao/{c}" for c in CONTEUDOS_FALA] and "chamar_atencao" not in linhas
    assert list(Plasticidade(dc.config_do_braco("LAB")).H)[4] == "chamar_atencao"
    e = [S] * len(CARACTERISTICAS_DIGIBRAIN)
    reg = p.creditar({"chave": ("chamar_atencao", "higiene", None), "r": S, "e": e, "g_apr": S})
    assert reg["b"] == "chamar_atencao/higiene" and any(p.H["chamar_atencao/higiene"])
    assert not any(p.H["chamar_atencao/fome"]) and not any(p.H["chamar_atencao/solidao"])
    with pytest.raises(ValueError):
        linha_da_opcao(("chamar_atencao", None, None), True)
    assert linha_da_opcao(("chamar_atencao", None, None), False) == "chamar_atencao"


# ================================================================== a vida com a subchave
def test_a_vida_do_lab_f_fala_com_conteudo_e_passa_as_conferencias(tmp_path):
    u = dc.bv.unidades_derivadas([101], 1, dc.PREFIXO)[0]
    r = dc._vida({"dias": 3, "orcamento_por_dia": 16}, "LAB+F", "atende", "atencioso", u, str(tmp_path))
    assert r["fala"]["por_conteudo"]["sem_conteudo"] == 0 and r["fala"]["vida"]["falas"] > 0
    assert r["credito"]["atendimentos"] == r["atendimento"]["por_conteudo"]["fome"] + r["atendimento"]["por_conteudo"]["higiene"] \
        + r["atendimento"]["por_conteudo"]["solidao"]
    assert set(r["habito"]) == {"1", "3"} and set(r["habito"]["1"]) == {f"chamar_atencao/{c}" for c in CONTEUDOS_FALA}
    lab = dc._vida({"dias": 2, "orcamento_por_dia": 16}, "LAB", "ignora", "atencioso", u, str(tmp_path))
    assert lab["fala"]["por_conteudo"] == {"fome": 0, "higiene": 0, "solidao": 0, "sem_conteudo": lab["fala"]["vida"]["falas"]}
    assert lab["atendimento"] is None and lab["credito"] is None and set(lab["habito"]["1"]) == {"chamar_atencao"}


def test_a_conferencia_da_fala_falha_alto_com_uma_unidade_de_fala_no_lab():
    _, reg, _, _, _ = dc.viver("LAB+F", "ignora", "atencioso", 101, 1, 16)
    c = dc.orq.cerebro_de(reg)
    dc.conferir_fala("LAB+F", c)
    with pytest.raises(RuntimeError):
        dc.conferir_fala("LAB", c)


# ================================================================== o dono que atende
class _Base:
    nome = "teste"

    def __init__(self, acoes):
        self.acoes = acoes

    def decidir(self, visao, rng):
        rng.random()                                  # o dono de hoje consome a rng dele; o que atende nao consome nada a mais
        return list(self.acoes)


def _motivo(acao, conteudo=None, urg=None):
    return {"acao": acao, "escolha": [acao, conteudo, None], "afeto": {"urgencias": urg or {"fome": 0, "higiene": 0, "solidao": 0}}}


def test_o_dono_que_atende_da_o_cuidado_do_conteudo_no_mesmo_passo_e_no_mesmo_orcamento():
    ms = [_motivo("comer"), _motivo("chamar_atencao", "higiene")]
    d = dc.DonoQueAtende(_Base([AcaoUsuario.BRINCAR]), ms)
    rng, ref = random.Random(3), random.Random(3)
    v = SimpleNamespace(passo=1, estado={"tick": 30}, maximo_permitido=6)
    assert d.decidir(v, rng) == [AcaoUsuario.BRINCAR, AcaoUsuario.LIMPAR]
    ref.random()
    assert rng.getstate() == ref.getstate()           # sem rng nova
    assert d.atendimentos == [{"passo": 1, "tick": 30, "k": 1, "conteudo": "higiene", "acao": "limpar"}]
    ms.append(_motivo("chamar_atencao", "fome"))
    assert d.decidir(SimpleNamespace(passo=2, estado={"tick": 45}, maximo_permitido=1), rng) == [AcaoUsuario.BRINCAR]   # sem orcamento
    assert d.sem_orcamento[0]["k"] == 2 and len(d.atendimentos) == 1
    ms.append(_motivo("chamar_atencao", None, {"fome": 600, "higiene": 600, "solidao": 100}))   # o LAB: a maior urgencia, empate fome
    assert d.decidir(SimpleNamespace(passo=3, estado={"tick": 60}, maximo_permitido=6), rng)[-1] is AcaoUsuario.ALIMENTAR


def test_a_maior_urgencia_desempata_na_ordem_fome_higiene_solidao():
    assert maior_urgencia_da_fala({"fome": 5, "higiene": 5, "solidao": 5}) == "fome"
    assert maior_urgencia_da_fala({"fome": 4, "higiene": 5, "solidao": 5}) == "higiene"
    assert maior_urgencia_da_fala({"fome": 4, "higiene": 5, "solidao": 6, "energia": 999}) == "solidao"
    with pytest.raises(ValueError):
        maior_urgencia_da_fala({"fome": 1, "higiene": 1})


# ================================================================== a fala no metrics.py (4.1 e 4.2)
T = 1440


def _u(f=0, h=0, s=0):
    return {"fome": f, "higiene": h, "solidao": s}


def test_a_fala_pertinente_pede_o_conteudo_da_maior_urgencia_acima_do_limiar():
    dec = [(0, "chamar_atencao", "fome", _u(f=600)),          # pertinente
           (15, "chamar_atencao", "fome", _u(f=512)),         # no limiar: nao (estrito)
           (30, "chamar_atencao", "higiene", _u(f=700, h=600)),   # o conteudo nao e o da maior urgencia
           (45, "chamar_atencao", None, _u(f=900)),           # o chamar sem conteudo nunca
           (60, "dormir", None, _u(f=900)),
           (T + 0, "chamar_atencao", "solidao", _u(s=800)),   # dia 2, pertinente
           (T + 15, "comer", None, _u())]
    r = fala_nas_decisoes(dec, 2, 512)
    assert r["vida"]["falas"] == 5 and r["vida"]["pertinentes"] == 2 and r["vida"]["pertinencia"] == 2 / 5
    assert r["vida"]["pertinente_por_dia"] == 1.0 and r["vida"]["falas_por_dia"] == 2.5
    assert r["vida"]["frac_fala_fora_do_dormir"] == 5 / 6 and r["falas_por_dia"] == [4, 1]
    assert r["dias_1_3"]["dias"] == 2 and r["dias_1_3"]["pertinentes"] == 2 and r["dias_8_14"] is None
    assert r["por_conteudo"] == {"fome": 2, "higiene": 1, "solidao": 1, "sem_conteudo": 1}
    assert r["abaixo_do_limiar"] == {"fome": 1, "higiene": 0, "solidao": 0, "sem_conteudo": 0}


def test_as_janelas_dos_dias_1_a_3_e_8_a_14():
    dec = [(d * T, "chamar_atencao", "fome", _u(f=900)) for d in range(14)] + [(7 * T + 15, "chamar_atencao", "fome", _u(f=900))]
    r = fala_nas_decisoes(dec, 14, 512)
    assert r["dias_1_3"]["falas"] == 3 and r["dias_1_3"]["falas_por_dia"] == 1.0
    assert r["dias_8_14"]["falas"] == 8 and r["dias_8_14"]["pertinente_por_dia"] == 8 / 7
    assert fala_nas_decisoes([(0, "comer", None, _u())], 1, 512)["vida"]["pertinencia"] is None


def test_a_fala_falha_alto():
    with pytest.raises(ValueError):
        fala_nas_decisoes([], 1, 512)
    with pytest.raises(ValueError):
        fala_nas_decisoes([(T, "comer", None, _u())], 1, 512)              # depois do ultimo dia
    with pytest.raises(ValueError):
        fala_nas_decisoes([(0, "comer", "fome", _u())], 1, 512)            # conteudo fora da fala
    with pytest.raises(ValueError):
        fala_nas_decisoes([(0, "chamar_atencao", "tedio", _u())], 1, 512)  # conteudo desconhecido
    with pytest.raises(ValueError):
        fala_nas_decisoes([(0, "comer", None, _u())], 0, 512)


# ================================================================== a analise, com dados sinteticos
def _registros(escuta: float, guarda: float, frac_fala: float = 0.05, atende: float = 3.0, n: int = 12) -> list[dict]:
    """vidas sinteticas: n unidades, 4 donos, os 2 bracos e os 2 modos; a fala pertinente nos dias 8 a 14 sobe `escuta` com o dono que
    atende no LAB+F; a taxa por episodio do LAB+F com o que ignora fica `guarda` acima da do LAB; um ruido fixo por unidade"""
    out = []
    for i in range(n):
        s = 1000 + i
        ruido = ((i * 37) % 11 - 5) / 100
        for dono in dc.DONOS:
            for b in dc.BRACOS:
                for mo in dc.MODOS:
                    pert = 1.0 + ruido + (escuta if (b, mo) == ("LAB+F", "atende") else 0)
                    taxa = 0.6 + ruido / 2 + (guarda if (b, mo) == ("LAB+F", "ignora") else 0)
                    out.append({"semente": s, "base": 101 + (i % 5), "dono": dono, "braco": b, "modo": mo,
                                "episodios_fome": {"n": 5, "taxa": taxa},
                                "fala": {"vida": {"frac_fala_fora_do_dormir": frac_fala + ruido / 100},
                                         "dias_8_14": {"pertinente_por_dia": pert}},
                                "atendimento": {"dias_1_3_por_dia": atende + ruido} if mo == "atende" else None})
    return out


def test_a_analise_le_a_linha_2_quando_o_dono_que_atende_muda_a_fala_e_a_guarda_nao_cai():
    rs = _registros(escuta=0.5, guarda=0.0)
    prem, esc, gua = dc.premissas(rs), dc.escuta(rs, BOOT), dc.guarda(rs, BOOT)
    assert prem["conclusivo"] and esc["classe"]["classe"] == "> 0" and esc["passa"]
    assert gua["classe"]["classe"] == "≈ 0" and not gua["falha"]
    assert dc.leitura(prem, esc, gua)["linha"] == 2


def test_a_analise_le_as_linhas_1_3_e_4():
    rs = _registros(escuta=0.5, guarda=-0.2)
    assert dc.guarda(rs, BOOT)["falha"]
    assert dc.leitura(dc.premissas(rs), dc.escuta(rs, BOOT), dc.guarda(rs, BOOT))["linha"] == 3
    rs = _registros(escuta=0.0, guarda=0.0)
    esc = dc.escuta(rs, BOOT)
    assert esc["classe"]["classe"] == "indeterminado" and not esc["passa"]          # sem margem: nao ha "~ 0" (DC3-6)
    assert dc.leitura(dc.premissas(rs), esc, dc.guarda(rs, BOOT))["linha"] == 4
    for falha in ({"frac_fala": 0.0}, {"atende": 0.5}):
        rs = _registros(escuta=0.5, guarda=0.0, **falha)
        prem = dc.premissas(rs)
        assert not prem["conclusivo"] and dc.leitura(prem, dc.escuta(rs, BOOT), dc.guarda(rs, BOOT))["linha"] == 1


def test_a_celula_com_none_fica_fora_da_media_da_unidade():
    rs = _registros(escuta=0.5, guarda=0.0, n=3)
    for r in rs:
        if r["semente"] == 1000 and r["dono"] == "relapso" and r["braco"] == "LAB+F":
            r["episodios_fome"]["taxa"] = None
    difs = dc.por_unidade(rs, ("LAB+F", "ignora"), ("LAB", "ignora"), dc.EPISODIO)
    assert len(difs) == 3


# ================================================================== a trava e a fumaca
def test_a_config_da_run_recusa_rodar_antes_do_registro_e_a_fumaca_passa():
    cfg = json.loads((RAIZ / "experiments/configs/v3_conversa_dc3/conversa_dc3.json").read_text(encoding="utf-8"))
    with pytest.raises(RuntimeError, match="registro da run"):
        dc.modo_da_config(cfg)
    fum = json.loads((RAIZ / "experiments/configs/v3_conversa_dc3/varredura.json").read_text(encoding="utf-8"))
    assert dc.modo_da_config(fum) == "fumaca"
    with pytest.raises(dc.bv.SementeSemPlano):
        dc.modo_da_config({**fum, "unidades": {**fum["unidades"], "bases": [79101]}})
    with pytest.raises(ValueError):
        dc.rodar(fum, Path("nao_existe"), 5)


def test_a_fumaca_do_orquestrador_inteiro_nas_sementes_dos_testes(tmp_path):
    cfg = {"descricao": "fumaca do teste", "plano": dc.PLANO, "fase": dc.FASE, "dias": 2, "orcamento_por_dia": 16,
           "unidades": {"bases": [101, 202], "k": 1, "prefixo": dc.PREFIXO}}
    out = dc.rodar(cfg, tmp_path / "run", 1)
    res = out["resultado"]
    assert res["modo"] == "fumaca" and res["vidas"] == 2 * 16
    assert {"premissas", "escuta", "guarda", "leitura", "descritivo"} <= set(res)
    assert res["descritivo"]["credito"]["LAB+F"]["vidas"] == 2 * 4
    lidos = json.loads((tmp_path / "run" / "medidas.json").read_text(encoding="utf-8"))
    assert json.loads((tmp_path / "run" / "resultado.json").read_text(encoding="utf-8"))["vidas"] == len(lidos) == 32
    with pytest.raises(FileExistsError):
        dc.rodar(cfg, tmp_path / "run", 1)
