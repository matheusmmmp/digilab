"""O orquestrador da AN4 (experiments/run_v3_acoes_novas.py; docs/PLANO_ANALISE_V3_ACOES_NOVAS.md, secoes 2, 3, 6, 7, 9 e 11): o desenho,
a trava (o plano APROVADO no cabecalho, trocado nos dois sentidos so no teste; a faixa em FAIXAS_RESERVADAS; o registro da run; as bases, o
K, os dias; no maximo 4 processos; nada por cima de uma pasta existente), os bracos, as conferencias do passeio (a urgencia, o alvo, o F, o
LAB sem passeio, a vista do credito), a analise com dados sinteticos (a guarda, as premissas, o MOV, a leitura de 7.4) e a varredura nas
sementes dos testes. **Nenhuma vida da faixa 78101...78505 roda aqui:** as vidas so usam as bases 101...505."""
from __future__ import annotations

import copy
import io
import json
import re
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402
import run_v3_acoes_novas as an  # noqa: E402
from bancada.faixas import FAIXAS_QUEIMADAS, FAIXAS_RESERVADAS  # noqa: E402

CONFIGS = RAIZ / "experiments" / "configs" / "v3_acoes_novas"
STATUS = re.compile(r"^\*\*Status: [^\n]*$", re.M)
PODER = RAIZ / "artifacts_v3_acoes_novas" / "plano_an3_poder.json"


def _cfg(nome: str = "acoes_novas") -> dict:
    return json.loads((CONFIGS / f"{nome}.json").read_text(encoding="utf-8"))


def _plano_com_status(status: str) -> str:
    """o plano real com a linha do status do cabecalho trocada (so no teste)"""
    plano = an._plano()
    i = plano.index("\n## ")
    cab, n = STATUS.subn(status, plano[:i])
    assert n == 1, "o cabecalho do plano tem de ter uma linha de status so"
    return cab + plano[i:]


@pytest.fixture
def sem_registro(monkeypatch):
    """o registro da run e conferido a parte (test_o_registro_*): aqui a trava das bases, do K e dos dias"""
    monkeypatch.setattr(an, "exigir_registro", lambda plano: None)


# ------------------------------------------------------------------ o desenho
def test_o_desenho_e_o_do_plano():
    assert an.BASES == (78101, 78202, 78303, 78404, 78505) and an.K_POR_BASE == 40 and an.FAIXA == (78101, 78505)
    assert an.DIAS == 14 and an.ORCAMENTO_POR_DIA == 16 and an.MAX_PROCESSOS == 4 and an.MARGEM == 0.018
    assert an.LUGARES == ("comedouro", "longe_fixo") and an.BRACOS == ("LAB", "LAB+P") and len(an.CELULAS) == 8
    assert len(an.BASES) * an.K_POR_BASE * len(an.BRACOS) * len(an.CELULAS) == 3200
    assert an.P_PASSEIO_LIMIAR == 0.01 and an.G_ELEGIVEL_EP == {"frac_vidas": 0.8, "episodios": 3}
    assert an.SAIDA == "artifacts_v3_acoes_novas/run" and an.PREFIXO == "digibrain_prototipo"


def test_os_bracos_sao_o_rel_da_c4_com_e_sem_a_passeio():
    lab, labp = (orq.config_do_braco(b, conserto=True) for b in an.BRACOS)
    rel = orq.config_do_braco("REL", conserto=True)
    assert lab == rel and not lab.passeio
    assert labp.passeio and {k: v for k, v in vars(labp).items() if k != "passeio"} == {k: v for k, v in vars(rel).items() if k != "passeio"}
    for cd in (lab, labp):
        assert not (cd.credito_corrida or cd.redecidir_evento or cd.intencao_suspensa or cd.facetas_mem)
        assert cd.memoria_autobio and cd.controle_mem == "rel"
    with pytest.raises(ValueError):
        orq.config_do_braco("LAB+P")                      # so nas fases do conserto


def test_a_faixa_esta_reservada_e_nao_cruza_outra_nem_uma_queimada():
    assert any((lo, hi_) == an.FAIXA for lo, hi_, _ in FAIXAS_RESERVADAS)
    for lo, hi_, _ in FAIXAS_RESERVADAS:
        if (lo, hi_) != an.FAIXA:
            assert hi_ < an.FAIXA[0] or lo > an.FAIXA[1], (lo, hi_)
    for f in FAIXAS_QUEIMADAS:
        lo, hi_ = f[0], f[1]
        assert hi_ < an.FAIXA[0] or lo > an.FAIXA[1], f


def test_os_fins_conhecidos_sao_os_do_estado():
    assert an.fins_conhecidos("LAB") == frozenset({"meta", "trocou", "sumiu", "desistiu", "achou"})
    assert an.fins_conhecidos("LAB+P") == an.fins_conhecidos("LAB") | {"interrompido"}


def test_a_margem_e_o_k_sao_os_do_artefato_do_poder():
    d = json.loads(PODER.read_text(encoding="utf-8"))
    k = len(an.BASES) * an.K_POR_BASE
    assert round(d["por_k"][f"K={k}"]["margem"], 3) == an.MARGEM
    assert d["por_k"][f"K={k}"]["vidas"] == k * len(an.BRACOS) * len(an.CELULAS)


# ------------------------------------------------------------------ a trava
def test_o_plano_de_hoje_esta_aprovado_e_a_trava_o_le():
    an.exigir_plano_aprovado(an._plano())
    an.exigir_plano_aprovado(_plano_com_status("**Status: APROVADO pelo Matheus em 2026-11-05.**"))


@pytest.mark.parametrize("status", ["**Status: PROPOSTO (AN3), aguarda o Matheus.**", "**Status: aprovado pelo matheus**"])
def test_a_trava_recusa_o_plano_sem_o_aprovado(status):
    with pytest.raises(RuntimeError, match="APROVADO"):
        an.exigir_plano_aprovado(_plano_com_status(status))


def test_a_trava_recusa_o_plano_sem_status_ou_com_dois():
    plano = an._plano()
    with pytest.raises(RuntimeError):
        an.exigir_plano_aprovado(STATUS.sub("", plano, count=1))
    i = plano.index("\n## ")
    with pytest.raises(RuntimeError):
        an.exigir_plano_aprovado(plano[:i] + "\n**Status: APROVADO pelo Matheus**\n" + plano[i:])


def test_a_config_da_run_segue_o_plano(sem_registro):
    assert an.modo_da_config(_cfg()) == "acoes_novas"


def test_a_config_da_run_recusa_o_plano_proposto(monkeypatch, sem_registro):
    proposto = _plano_com_status("**Status: PROPOSTO.**")
    monkeypatch.setattr(an, "_plano", lambda: proposto)
    with pytest.raises(RuntimeError, match="APROVADO"):
        an.modo_da_config(_cfg())


def test_a_trava_exige_a_faixa_reservada(monkeypatch, sem_registro):
    monkeypatch.setattr(an, "FAIXAS_RESERVADAS", tuple(f for f in FAIXAS_RESERVADAS if (f[0], f[1]) != an.FAIXA))
    with pytest.raises(bv.SementeSemPlano):
        an.modo_da_config(_cfg())


@pytest.mark.parametrize("bases", [[78101, 78202, 78303, 78404], [78101, 78202, 78303, 78404, 78506], [78505, 78404, 78303, 78202, 78101],
                                   [77101, 77202, 77303, 77404, 77505], [101, 78202]])
def test_recusa_outra_base_e_sementes_fora_da_faixa(bases, sem_registro):
    cfg = _cfg()
    cfg["unidades"]["bases"] = bases
    with pytest.raises(bv.SementeSemPlano):
        an.modo_da_config(cfg)


def test_recusa_outro_k_outros_dias_outro_orcamento_e_outro_plano(sem_registro):
    for chave, valor in (("k", 39), ("dias", 13), ("plano", "docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md"), ("orcamento_por_dia", 15)):
        cfg = _cfg()
        if chave == "k":
            cfg["unidades"]["k"] = valor
        else:
            cfg[chave] = valor
        with pytest.raises(ValueError):
            an.modo_da_config(cfg)


def test_recusa_chave_a_mais_fase_errada_e_fumaca_com_dias_demais():
    cfg = _cfg("varredura")
    assert an.modo_da_config(cfg) == "fumaca"
    for mudar in (lambda c: c.update(extra=1), lambda c: c.update(fase="memoria_autobio"), lambda c: c.update(dias=15)):
        c = copy.deepcopy(cfg)
        mudar(c)
        with pytest.raises(ValueError):
            an.modo_da_config(c)


def test_recusa_mais_de_4_processos_e_pasta_existente(tmp_path):
    with pytest.raises(ValueError, match="4 processos"):
        an.rodar(_cfg("varredura"), tmp_path / "x", 5)
    (tmp_path / "y").mkdir()
    with pytest.raises(FileExistsError):
        an.rodar(_cfg("varredura"), tmp_path / "y", 1)
    assert not (tmp_path / "x").exists()


def _plano_com_registro(shas: dict) -> str:
    linhas = "\n".join(f"- `{f}`: `{s}`" for f, s in shas.items())
    return f"# plano\n\n## 13. x\n\n{an.REGISTRO_TITULO} (teste)\n\n{linhas}\n"


def test_o_registro_da_run_confere_os_sha256_de_hoje():
    hoje = an.sha_dos_arquivos()
    assert "experiments/run_v3_acoes_novas.py" in hoje and "digilab/engine.py" in hoje
    assert any(f.startswith("digilab/digibrain/") for f in hoje) and "docs/PLANO_ANALISE_V3_ACOES_NOVAS.md" not in hoje
    an.exigir_registro(_plano_com_registro(hoje))
    mudado = {**hoje, "digilab/metrics.py": "0" * 64}
    with pytest.raises(RuntimeError, match="mudaram"):
        an.exigir_registro(_plano_com_registro(mudado))
    with pytest.raises(RuntimeError, match="outros arquivos"):
        an.exigir_registro(_plano_com_registro({k: v for k, v in hoje.items() if k != "digilab/engine.py"}))
    with pytest.raises(RuntimeError, match="registro da run"):
        an.exigir_registro("# plano sem registro\n")


def test_o_engine_do_registro_e_o_congelado():
    from digilab.protocol import ENGINE_SHA256_V0
    assert an.sha_dos_arquivos()["digilab/engine.py"] == ENGINE_SHA256_V0


# ------------------------------------------------------------------ as conferencias numa vida (sementes dos testes)
@pytest.fixture(scope="module")
def vidas():
    """uma vida de cada braco, 2 dias, o relapso no comedouro (o que mais passeia e mais interrompe), semente 101"""
    out = {}
    for b in an.BRACOS:
        motor, registro, fab, pos = an.viver(b, "relapso", "comedouro", 101, 2, 16)
        out[b] = (motor, registro, fab, pos)
    return out


def test_a_vida_passa_em_todas_as_conferencias(vidas):
    for b, (motor, registro, fab, pos) in vidas.items():
        orq.conferir_replay(motor, fab, 101, motor.log.para_jsonl())
        c = orq.cerebro_de(registro)
        an.conferir_bracos(b, c)
        ab = an.conferir_passeio(b, c)
        an.conferir_mecanismo(b, registro, ab)
        assert len(pos) == len(c.motivos)
        m = an.medidas_movimento(c, pos, 2)
        assert 0 <= m["mov"] <= 1
    c = orq.cerebro_de(vidas["LAB+P"][1])
    p = an.medidas_passeio("LAB+P", c, 2)
    assert p["abertos"] > 0 and p["decisoes_que_continuam"] > 0 and p["fins"]["interrompido"] > 0
    assert p["urgencia_na_abertura"]["maxima"] <= c.inatos.urgencia_lambda
    assert an.medidas_passeio("LAB", orq.cerebro_de(vidas["LAB"][1]), 2) is None


def test_sem_a_vista_o_credito_do_prototipo_recusa_o_passeio(vidas):
    """o desvio D-AN4-1: a decisao que abre o passeio tem a escolha `explorar/vagar` no motivo; sem a vista, a conferencia do credito do
    prototipo le a opcao do passeio como de outra unidade e falha"""
    with pytest.raises(RuntimeError, match="nao e da unidade da opcao"):
        orq.conferir_mecanismo("LAB+P", vidas["LAB+P"][1], None)


class _Falso:
    def __init__(self, c, motivos):
        self._c, self.motivos = c, motivos

    def __getattr__(self, nome):
        return getattr(self.__dict__["_c"], nome)


def test_a_conferencia_do_passeio_falha_alto_com_urgencia_alta(vidas):
    c = orq.cerebro_de(vidas["LAB+P"][1])
    ms = copy.deepcopy(c.motivos)
    k = next(m["k"] for m in ms if m["escolha"][:2] == an.PASSEIO)
    ms[k]["afeto"]["urgencias"]["fome"] = c.inatos.urgencia_lambda + 1
    with pytest.raises(RuntimeError, match="urgencia"):
        an.conferir_passeio("LAB+P", _Falso(c, ms))


def test_a_conferencia_do_passeio_falha_alto_com_o_alvo_errado(vidas):
    c = orq.cerebro_de(vidas["LAB+P"][1])
    ms = copy.deepcopy(c.motivos)
    k = next(m["k"] for m in ms if m["escolha"][:2] == an.PASSEIO)
    ms[k]["alvo"]["x"] += 1
    with pytest.raises(RuntimeError, match="alvo"):
        an.conferir_passeio("LAB+P", _Falso(c, ms))


def test_a_conferencia_do_f_pega_o_interrompido_que_frustra(vidas):
    """se o interrompido subisse o F, o F gravado depois dele seria outro: a conta refeita falha"""
    c = orq.cerebro_de(vidas["LAB+P"][1])
    ms = copy.deepcopy(c.motivos)
    k = next(m["k"] for m in ms if any(f["motivo"] == "interrompido" for f in m["fins"]))
    for f in ms[k]["fins"]:
        if f["motivo"] == "interrompido":
            f["motivo"] = "trocou"                           # o mesmo fim, lido como um que frustra, na decisao anterior ao contexto
    ms[k - 1]["fins"] = ms[k - 1]["fins"] + [f for f in ms[k]["fins"] if f["motivo"] == "trocou"]
    with pytest.raises(RuntimeError, match="o F da decisao"):
        an.conferir_frustracao("LAB+P", _Falso(c, ms))


def test_no_lab_nenhum_passeio(vidas):
    c = orq.cerebro_de(vidas["LAB"][1])
    ms = copy.deepcopy(c.motivos)
    k = next(m["k"] for m in ms if "alvo" in m)
    ms[k]["alvo"]["do_passeio"] = False
    with pytest.raises(RuntimeError, match="LAB: o passeio"):
        an.conferir_passeio("LAB", _Falso(c, ms))


def test_o_braco_errado_falha_alto(vidas):
    with pytest.raises(RuntimeError):
        an.conferir_bracos("LAB", orq.cerebro_de(vidas["LAB+P"][1]))
    with pytest.raises(RuntimeError):
        an.conferir_bracos("LAB+P", orq.cerebro_de(vidas["LAB"][1]))


# ------------------------------------------------------------------ a analise, com dados sinteticos
BOOT = {"reamostragens": 200, "semente": 4242, "nivel": 0.95}


def _registros(efeito: float = 0.0, n: int = 30, p_passeio: float = 0.1, episodios: int = 5, mov: float = 0.0) -> list[dict]:
    """vidas falsas: a taxa por episodio do LAB e 0,8 + ruido; a do LAB+P, a do LAB + `efeito`; o MOV do LAB+P, o do LAB + `mov`"""
    out = []
    for k in range(n):
        ruido = ((k * 37) % 11 - 5) / 1000
        for d in an.DONOS:
            for lu in an.LUGARES:
                for b in an.BRACOS:
                    tratado = b == "LAB+P"
                    taxa = 0.8 + ruido * (k % 3) + (efeito + ruido if tratado else 0)
                    out.append({"braco": b, "dono": d, "lugar": lu, "semente": 1000 + k, "base": (101, 202, 303, 404, 505)[k % 5],
                                "episodios_fome": {"n": episodios, "taxa": taxa},
                                "movimento": {"mov": 0.5 + ruido + (mov + ruido if tratado else 0)},
                                "passeio": {"p_passeio": p_passeio + ruido} if tratado else None})
    return out


@pytest.mark.parametrize("efeito,classe,falha", [(0.0, "≈ 0", False), (-0.006, "≈ 0", False), (-0.05, "< 0", True), (0.05, "> 0", False)])
def test_a_guarda_falha_so_com_a_classe_menor_que_0(efeito, classe, falha):
    g = an.guarda(_registros(efeito), BOOT)
    assert g["classe"]["classe"] == classe and g["falha"] is falha and g["margem"] == 0.018
    assert g["n"] == 30 and g["p_unilateral"] is not None and g["margem_efetiva"] is not None


def test_a_guarda_le_so_o_comedouro():
    rs = _registros()
    for r in rs:
        if r["lugar"] == "longe_fixo" and r["braco"] == "LAB+P":
            r["episodios_fome"]["taxa"] -= 0.5
    assert an.guarda(rs, BOOT)["classe"]["classe"] == "≈ 0"
    assert an.longe(rs, BOOT)["LONGE-AN"]["classe"]["classe"] == "< 0"


def test_o_mov_le_as_8_celulas_e_move_so_com_o_limite_inferior_acima_de_0():
    assert an.movimento(_registros(mov=0.05), BOOT)["move"]
    assert not an.movimento(_registros(mov=0.0), BOOT)["move"]
    assert an.movimento(_registros(mov=0.05), BOOT)["n"] == 30


def test_as_premissas():
    ok = an.premissas(_registros())
    assert ok["P-PASSEIO"]["passa"] and ok["G-ELEGIVEL-EP"]["passa"] and ok["conclusivo"]
    assert set(ok["G-ELEGIVEL-EP"]["por_braco"]) == {"LAB", "LAB+P"}
    assert not an.premissas(_registros(p_passeio=0.008))["P-PASSEIO"]["passa"]
    assert not an.premissas(_registros(episodios=2))["conclusivo"]


@pytest.mark.parametrize("conclusivo,falha,move,linha,an5", [(False, False, True, 1, False), (False, True, True, 1, False),
                                                            (True, True, True, 2, False), (True, False, True, 3, True),
                                                            (True, False, False, 4, True)])
def test_a_leitura_de_7_4(conclusivo, falha, move, linha, an5):
    gua = {"classe": {"classe": "< 0" if falha else "≈ 0", "sinal": None}, "falha": falha, "ressalva_assimetria": None}
    r = an.leitura({"conclusivo": conclusivo}, gua, {"move": move})
    assert r["linha"] == linha and r["an5_pode_rodar"] is an5 and r["o_que_se_faz"]


# ------------------------------------------------------------------ a varredura nas sementes dos testes
def test_a_varredura_roda_de_ponta_a_ponta_nas_sementes_dos_testes(tmp_path):
    """o orquestrador inteiro com as cinco sementes dos testes (101...505, K = 1), os 2 bracos e as 8 celulas, 1 dia (80 vidas): nenhuma
    semente nem base na faixa 78101...78505"""
    cfg = copy.deepcopy(_cfg("varredura"))
    cfg["dias"] = 1
    pasta = tmp_path / "varredura"
    r = an.rodar(cfg, pasta, 1, CONFIGS / "varredura.json")
    assert r["meta"]["modo"] == "fumaca" and len(r["registros"]) == 80 and r["resultado"]["vidas"] == 80
    for u in r["meta"]["unidades"]:
        assert u["base"] in bv.SEMENTES_TESTE
        assert not (an.FAIXA[0] <= u["semente"] <= an.FAIXA[1]) and not (an.FAIXA[0] <= u["genoma"] <= an.FAIXA[1])
    meta = json.loads((pasta / "meta.json").read_text(encoding="utf-8"))
    for nome, sha in meta["artefatos_sha256"].items():
        assert bv._sha(pasta / nome) == sha
    assert meta["bracos"]["LAB+P"]["passeio"] is True and "passeio" not in meta["bracos"]["LAB"]
    assert meta["fins_conhecidos"]["LAB+P"] == sorted(an.fins_conhecidos("LAB+P"))
    assert len(list((pasta / "vidas").rglob("*.jsonl"))) == 80
    res = json.loads((pasta / "resultado.json").read_text(encoding="utf-8"))
    assert {"premissas", "guarda", "movimento", "leitura", "descritivo", "nao_demonstra"} <= set(res)
    assert set(res["descritivo"]) == {"longe", "movimento", "passeio", "corpo", "outros"}
    med = json.loads((pasta / "medidas.json").read_text(encoding="utf-8"))
    assert all((v["passeio"] is not None) == (v["braco"] == "LAB+P") for v in med.values())
    assert sum(v["passeio"]["abertos"] for v in med.values() if v["passeio"]) > 0
    with pytest.raises(FileExistsError):
        an.rodar(cfg, pasta, 1)


def test_resumo_no_console_cp1252_nao_quebra(monkeypatch):
    r = {"modo": "m", "vidas": 1, "premissas": {}, "guarda": {}, "movimento": {}, "leitura": "≈ 0,5"}
    buf = io.TextIOWrapper(io.BytesIO(), encoding="cp1252", errors="strict")
    monkeypatch.setattr("sys.stdout", buf)
    an._imprimir_resumo(r)
    buf.flush()
    assert "2248" in buf.buffer.getvalue().decode("ascii")


# ------------------------------------------------------------------ o isolamento (a licao do #515)
def test_o_orquestrador_nao_monta_o_digibrain():
    """so o orquestrador do prototipo cita o pacote do DigiBrain e a ConfigDigibrain; o da AN4 passa por ele"""
    nomes = re.compile(r"\b(ConfigDigibrain\w*|CONFIG_DIGIBRAIN\w*)\b|digilab\.digibrain|from \.digibrain|from \.\.digibrain|import digibrain")
    assert not nomes.search((RAIZ / "experiments/run_v3_acoes_novas.py").read_text(encoding="utf-8"))


def test_o_texto_do_registro_e_lido_pela_trava():
    """o corpo da secao 14 gerado por `--registro` volta pela `registro_do_plano` com os sha256 de hoje (so deriva sementes; nenhuma vida)"""
    texto = an.texto_do_registro()
    assert "78101" in texto and "K = 40 por base" in texto and an.COMANDO in texto
    plano = f"# plano\n\n{an.REGISTRO_TITULO} (AN4)\n\n{texto}"
    assert an.registro_do_plano(plano) == an.sha_dos_arquivos()
    an.exigir_registro(plano)
