"""SOCIAL_PAR S2: o substrato, antes da run (docs/PLANO_ANALISE_V3_SOCIAL_PAR_S.md, APROVADO em 2026-11-18, com o adendo 1).

Os gates: a bola do experimento (`deixar_bola_intervencao`) no registro e no replay; a `IntervencaoT0`; o "desliga nao muda" (as vidas
gravadas da run do A0 se refazem com o mesmo sha256 depois da mudanca no `viver_par` e no grupo); o "liga resolve" de cada braco (o
que a intervencao faz no t0); o determinismo; as travas; a fumaca do orquestrador; e a S0 refatorada, igual ao artefato gravado.
"""
from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import run_v3_social_par_a0 as a0  # noqa: E402
import run_v3_social_par_s as s  # noqa: E402
from bancada import parceiro as pc  # noqa: E402
from bancada.faixas import FAIXAS_RESERVADAS, PREFIXOS_UNIDADES, SementeSemPlano, unidades_derivadas  # noqa: E402
from digilab.config import CONFIG_GRUPO_LIGADA, ConfigIntervencaoSocial  # noqa: E402
from digilab.grupo import ORIGEM_INTERVENCAO, Grupo, RegistroGrupo, reproduzir_grupo, sementes_do_grupo  # noqa: E402
from digilab.mundo import celula_de  # noqa: E402

RUN_A0 = RAIZ / "artifacts_v3_social_par_a0" / "run" / "vidas"


def _ss(semente):
    return sementes_do_grupo(semente, CONFIG_GRUPO_LIGADA.ids)


# ------------------------------------------------------------------ a bola do experimento
def test_a_bola_do_experimento_so_com_a_chave_e_volta_pelo_replay():
    g = Grupo(s.CM, 7, CONFIG_GRUPO_LIGADA, cfg_intervencao=ConfigIntervencaoSocial())
    with pytest.raises(ValueError, match="ConfigIntervencaoSocial"):
        g.deixar_bola_intervencao("A", 100, 100)
    u = unidades_derivadas([101], 1, s.PREFIXO["run"])[0]
    ss = _ss(u["semente"])
    v = pc.viver_par(s.CM, u["semente"], [a0._vivo("A", ss), a0._vivo("B", ss)], 2, cfg_intervencao=s.CI, cfg_cooperacao=s.CCO,
                     intervencao=pc.IntervencaoT0(1500, ("A",), lambda g: g.deixar_bola_intervencao("B", *g.motores["B"].pet), None))
    ev = [e for e in v.grupo.registro.eventos if e.tipo == "deixar_bola"]
    assert len(ev) == 1 and ev[0].origem == ORIGEM_INTERVENCAO and ev[0].tick == v.t0
    lido = RegistroGrupo.de_jsonl(v.grupo.registro.para_jsonl())
    r = reproduzir_grupo(lido, s._fabricas(ss, False), s.CM, cfg_cooperacao=s.CCO, cfg_intervencao=s.CI)
    assert r.registro == v.grupo.registro


def test_a_perturbacao_e_a_intervencao_nao_vao_juntas():
    ss = _ss(1)
    with pytest.raises(ValueError, match="nao vao juntas"):
        pc.viver_par(s.CM, 1, [a0._vivo("A", ss), a0._vivo("B", ss)], 1, perturbacao=("A", "B", 15, 0, 5), cfg_intervencao=s.CI,
                     intervencao=pc.IntervencaoT0(15, ("A",), lambda g: None))


# ------------------------------------------------------------------ desliga nao muda: as vidas da run do A0, refeitas com o codigo novo
@pytest.mark.parametrize("nome", ["101101-0000", "101505-0041"])
def test_desligado_as_vidas_da_run_do_a0_se_refazem_com_o_mesmo_sha256(nome):
    with gzip.open(RUN_A0 / f"{nome}.json.gz", "rt", encoding="utf-8") as f:
        disco = json.load(f)
    sem, pert = disco["semente"], tuple(disco["perturbacao"])
    ss = _ss(sem)
    vivo = a0._viver(sem, [a0._vivo("A", ss), a0._vivo("B", ss)], pert)
    assert a0._sha_vida(vivo) == disco["sha256"]["VIVO"]
    grav_d, ev = a0._gravacao_do_disco(disco["gravacoes"]["base"])
    grav = a0._viver(sem, [a0._vivo("A", ss), a0._gravado("B", ss, grav_d, ev)], pert)
    assert a0._sha_vida(grav) == disco["sha256"]["GRAV"]


# ------------------------------------------------------------------ a fumaca do orquestrador (G-ORQ), uma vez por modulo
@pytest.fixture(scope="module")
def fumaca(tmp_path_factory):
    pasta = tmp_path_factory.mktemp("s") / "fumaca"
    cfg = json.loads((RAIZ / "experiments/configs/v3_social_par_s/fumaca.json").read_text(encoding="utf-8"))
    return s.rodar(cfg, pasta, 2), pasta


def _por_nome(fumaca):
    r, _ = fumaca
    return {x["par"]: x for x in r["registros"]}


def test_g_orq_a_fumaca_faz_os_tres_bracos_e_o_g_det(fumaca):
    r, pasta = fumaca
    nomes = sorted(x["par"] for x in r["registros"])
    assert nomes == sorted([f"{b}-{base}-0000" for b in s.BRACOS for base in (101, 202)] + [f"DET-{b}-303-0000" for b in s.BRACOS])
    assert all(x["g_instr"] and x["g1"] for x in r["registros"])
    assert r["meta"]["vidas"] == 6 * 5 + 3 * 3 and r["meta"]["d0"] == s.D0
    res = json.loads((pasta / "resultado.json").read_text(encoding="utf-8"))
    assert set(res["bracos"]) == set(s.BRACOS) and "conjunto" in res
    for b in s.BRACOS:
        assert set(res["bracos"][b]) >= {"premissas", "primarios", "secundarios", "g_det", "leitura", "substrato", "riqueza"}
        assert res["bracos"][b]["leitura"]["A"]["classe"] == "cego"           # 1 par no G-DET: sem IC, o gate nao passa


def test_liga_o_c_leva_f_para_dentro_da_visao(fumaca):
    for base in (101, 202):
        v = _por_nome(fumaca)[f"C-{base}-0000"]["condicoes"]["VIVO"]
        assert 1 < v["distancia_no_t0"] <= s.RAIO_PERTO                          # o adendo 1: os dois se veem no t0


def test_liga_o_b1_poe_os_dois_fora_da_casa_no_t0(fumaca):
    u = [x for x in unidades_derivadas([101], 1, s.PREFIXO["run"])][0]
    ctx = s.contexto("B1", u["semente"])
    ss = _ss(u["semente"])
    vivo = s.viver(u["semente"], [a0._vivo("A", ss), a0._vivo("B", ss)], ctx, base=False)
    base = s.viver(u["semente"], [a0._vivo("A", ss), a0._vivo("B", ss, gravar=True)], ctx, base=True)
    k = pc.indice_do_passo(vivo, vivo.t0)
    assert vivo.t0 == base.t0
    cq = celula_de(*ctx["q"], s.CM)
    assert s.Q_X[0] <= cq[0] <= s.Q_X[1]
    for i in ("A", "B"):
        assert celula_de(*vivo.posicoes[i][k], s.CM)[0] > s.CASA_X_MAX       # os dois fora da casa logo depois do t0
    assert celula_de(*base.posicoes["B"][k], s.CM)[0] > s.CASA_X_MAX          # na base, P tambem foi levado a Q
    assert 1 < pc.distancias_celulas(vivo, "A", "B")[k] <= s.RAIO_PERTO
    ev = [e for e in vivo.grupo.registro.eventos if e.tipo == "levar_pet"]
    assert [e.pet for e in ev] == ["B", "A"] and all(e.origem == ORIGEM_INTERVENCAO for e in ev)


def test_liga_o_b2_poe_a_bola_na_posicao_de_p(fumaca):
    u = unidades_derivadas([202], 1, s.PREFIXO["run"])[0]
    ctx = s.contexto("B2", u["semente"])
    ss = _ss(u["semente"])
    for base in (False, True):
        v = s.viver(u["semente"], [a0._vivo("A", ss), a0._vivo("B", ss)], ctx, base=base)
        bolas = v.grupo.mundo.bolas_deixadas
        assert len(bolas) == 1 and bolas[0]["tick"] == v.t0
        assert v.no_t0 is not None
    ev = [e for e in v.grupo.registro.eventos if e.tipo == "deixar_bola"]
    assert len(ev) == 1 and ev[0].origem == ORIGEM_INTERVENCAO


def test_o_g_det_troca_p_pelo_seguidor_puro_e_so_tem_tres_vidas(fumaca):
    """o controle positivo (3): o P do G-DET e o SeguidorPuro, na base, na VIVO e na GRAV; o resultado do gate e da run, nao deste teste"""
    for b in s.BRACOS:
        x = _por_nome(fumaca)[f"DET-{b}-303-0000"]
        assert set(x["condicoes"]) == {"VIVO", "GRAV"} and "riqueza" not in x
    u = unidades_derivadas([303], 1, s.PREFIXO["det"])[0]
    ss = _ss(u["semente"])
    v = s.viver(u["semente"], [a0._vivo("A", ss), s._seguidor("B", ss)], s.contexto("C", u["semente"]), base=False)
    cab = json.loads(v.grupo.registro.para_jsonl().splitlines()[0])["cabecalho"]
    assert cab["pets"]["B"]["cerebro"] == "seguidor_puro" and cab["pets"]["A"]["cerebro"] == "digibrain"


def test_determinismo_o_mesmo_par_da_o_mesmo_disco(tmp_path):
    u = {**unidades_derivadas([101], 1, s.PREFIXO["run"])[0], "braco": "B1", "det": False}
    r1, r2 = s.par(u, str(tmp_path / "1")), s.par(u, str(tmp_path / "2"))
    assert r1["arquivo_sha256"] == r2["arquivo_sha256"]
    assert json.dumps(r1, sort_keys=True, default=str) == json.dumps(r2, sort_keys=True, default=str)


# ------------------------------------------------------------------ as travas
def test_as_travas_do_orquestrador_s(tmp_path, monkeypatch):
    run = json.loads((RAIZ / "experiments/configs/v3_social_par_s/run.json").read_text(encoding="utf-8"))
    assert s.modo_da_config(run) == "run"                                      # o plano e o adendo APROVADOS, a faixa, as bases
    with pytest.raises(SementeSemPlano):
        s.modo_da_config({**run, "unidades": {"bases": run["unidades"]["bases"][:-1], "k": 1}})
    with pytest.raises(ValueError, match="k = 1"):
        s.modo_da_config({**run, "unidades": {"bases": run["unidades"]["bases"], "k": 40}})
    with pytest.raises(ValueError, match="tres bracos"):
        s.modo_da_config({**run, "bracos": ["C"]})
    with pytest.raises(SementeSemPlano):
        s.modo_da_config({"modo": "fumaca", "bracos": ["C"], "unidades": {"bases": [103001], "k": 1}, "det": {"bases": [], "k": 1}})
    with pytest.raises(ValueError, match="processos"):
        s._executar([], str(tmp_path), 5)
    (tmp_path / "ja").mkdir()
    with pytest.raises(FileExistsError):
        s.rodar({"modo": "fumaca", "bracos": ["C"], "unidades": {"bases": [101], "k": 1}, "det": {"bases": [], "k": 1}}, tmp_path / "ja", 1)
    assert (103001, 103400) in {(lo, hi) for lo, hi, _ in FAIXAS_RESERVADAS}
    assert {"social_par_s", "social_par_s_det"} <= set(PREFIXOS_UNIDADES)
    chamadas = []

    def recusa(orq, config, processos):
        chamadas.append((orq, config, processos))
        raise s.pre_run.Recusa("recusada")
    monkeypatch.setattr(s.pre_run, "exigir", recusa)
    monkeypatch.setattr(sys, "argv", ["x", "--config", "experiments/configs/v3_social_par_s/run.json", "--processos", "4"])
    with pytest.raises(s.pre_run.Recusa):
        s.main()
    assert chamadas == [(s.ORQUESTRADOR, "experiments/configs/v3_social_par_s/run.json", 4)]


# ------------------------------------------------------------------ a S0 refatorada
def test_a_observacao_da_s0_refatorada_e_a_do_artefato():
    import observar_v3_social_par_s0 as s0
    ref = {p["par"]: p for p in json.loads((RAIZ / "artifacts_v3_social_par_s/s0/observacao.json").read_text(encoding="utf-8"))["pares"]}
    r = json.loads(json.dumps(s0.observar_par(str(RUN_A0 / "101101-0000.json.gz")), sort_keys=True))
    assert r == ref["101101-0000"]
