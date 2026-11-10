"""O I5 da INDIVIDUALIDADE (docs/PLANO_ANALISE_V3_INDIVIDUALIDADE_I5.md): os perfis do habito e a distintividade em `digilab/metrics.py`
contra casos feitos a mao; o orquestrador (experiments/run_v3_individualidade_i5.py): a trava (o cabecalho APROVADO, a secao do registro, as
vidas, as bases e o K do I2, no maximo 4 processos, nada por cima de uma pasta), a leitura do pacote de vidas, a analise num caso sintetico
e a fumaca de ponta a ponta. Vidas so com as sementes dos testes (101...505): nenhuma vida do I2 e rejogada aqui."""
from __future__ import annotations

import io
import json
import sys
import tarfile
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v3_individualidade_i5 as r5  # noqa: E402
from digilab import metrics as M  # noqa: E402

CONFIG = RAIZ / "experiments/configs/v3_individualidade/individualidade_i5.json"
FUMACA = RAIZ / "experiments/configs/v3_individualidade/individualidade_i5_fumaca.json"
APROVADO = "**Status: APROVADO pelo Matheus em 2026-11-09.**"


def _dia(acoes: list[str], x: int = 0, y: int = 0, dia: int = 1) -> list[dict]:
    """as 96 decisoes de um dia: as `acoes` primeiro, o resto `dormir`, todas na posicao (x, y)"""
    acoes = acoes + ["dormir"] * (96 - len(acoes))
    t0 = (dia - 1) * M.TICKS_POR_DIA
    return [{"tick": t0 + 15 * i, "acao": a, "x": x, "y": y} for i, a in enumerate(acoes)]


# ================================================================== os perfis (metrics.py)
def test_as_caixas_sao_as_do_plano():
    assert M.CAIXAS_HABITO == {"SEQ": 49, "LUGAR": 128, "HORA": 84}
    assert len(M.ACOES_ACORDADAS_HABITO) == 7 and "dormir" not in M.ACOES_ACORDADAS_HABITO


def test_perfis_de_um_dia_feito_a_mao():
    acoes = ["explorar"] * 20
    acoes[10] = "dormir"                       # 19 acordadas; o sono no meio corta o par 9-11
    p = M.perfis_habito_dia(_dia(acoes), 1)
    e = M.ACOES_ACORDADAS_HABITO.index("explorar")
    assert sum(p["SEQ"]) == 9 + 8 and p["SEQ"][e * 7 + e] == 17
    assert p["LUGAR"][0] == 19 and sum(p["LUGAR"]) == 19
    # os ticks 0..105 (8) na faixa 0; 120..285 (11, menos o tick 150 do sono) nas faixas 1 e 2
    assert p["HORA"][0 * 7 + e] == 8 and p["HORA"][1 * 7 + e] == 7 and p["HORA"][2 * 7 + e] == 4


def test_o_bloco_e_a_hora_de_uma_decisao():
    x, y = 16 * 12 + 5, 16 * 28                 # a celula (12, 28): o bloco (3, 7)
    decisoes = _dia(["comer", "brincar"] * 8, x=x, y=y, dia=2)
    p = M.perfis_habito_dia(decisoes, 2)
    assert p["LUGAR"][7 * 16 + 3] == 16
    c, b = M.ACOES_ACORDADAS_HABITO.index("comer"), M.ACOES_ACORDADAS_HABITO.index("brincar")
    assert p["SEQ"][c * 7 + b] == 8 and p["SEQ"][b * 7 + c] == 7
    assert M.perfis_habito_dia(decisoes, 1) is None          # o dia 1 sem decisao nenhuma


def test_dia_com_poucas_acordadas_fica_fora():
    assert M.perfis_habito_dia(_dia(["ocioso"] * 15), 1) is None
    assert M.perfis_habito_dia(_dia(["ocioso"] * 16), 1) is not None


def test_perfis_falham_alto():
    with pytest.raises(ValueError, match="desconhecida"):
        M.perfis_habito_dia(_dia(["voar"] * 20), 1)
    with pytest.raises(ValueError, match="mapa"):
        M.perfis_habito_dia(_dia(["ocioso"] * 20, x=1024), 1)
    d = _dia(["ocioso"] * 20)
    d[3], d[4] = d[4], d[3]
    with pytest.raises(ValueError, match="ordem"):
        M.perfis_habito_dia(d, 1)


# ================================================================== a distintividade (metrics.py)
A, B, C = [4, 0, 0], [0, 4, 0], [2, 2, 0]      # TV(A, B) = 1, TV(A, C) = TV(B, C) = 0,5


def test_distancia_entre_dias_e_no_mesmo_dia():
    assert M.distancia_entre_dias({1: A, 2: A, 3: C}, [1, 2, 3]) == pytest.approx((0 + 0.5 + 0.5) / 3)
    assert M.distancia_entre_dias({1: A, 2: None, 3: B}, [1, 2, 3]) == pytest.approx(1.0)
    assert M.distancia_entre_dias({1: A, 2: None}, [1, 2]) is None
    # o dia 1: media(TV(A, B), TV(A, C)) = 0,75; o dia 2: so o outro com o dia dentro, TV(A, A) = 0; a media sobre os dias: 0,375
    assert M.distancia_mesmo_dia({1: A, 2: A}, [{1: B, 2: None}, {1: C, 2: A}], [1, 2]) == pytest.approx(0.375)
    assert M.distancia_mesmo_dia({1: A}, [{1: None}], [1]) is None


def test_distintividade_de_um_pet_com_habito():
    """o pet repete A todo dia; os outros do dono fazem B; os do mundo, C: H_dono = 1 e H_mundo = 0,5"""
    proprio = {d: A for d in (8, 9, 10)}
    x = M.distintividade_habito(proprio, [{d: B for d in (8, 9, 10)}] * 3, [{d: C for d in (8, 9, 10)}] * 2, [8, 9, 10])
    assert x["D_si"] == 0 and x["H_dono"] == pytest.approx(1.0) and x["H_mundo"] == pytest.approx(0.5) and x["dias_dentro"] == 3
    y = M.distintividade_habito({8: A, 9: None}, [{8: B}], [{8: C}], [8, 9])
    assert y["D_si"] is None and y["H_dono"] is None and y["D_dono"] == pytest.approx(1.0)


def test_media_habito():
    assert M.media_habito([0.2, None, 0.4]) == {"media": pytest.approx(0.3), "n": 2, "fora": 1}
    assert M.media_habito([None]) == {"media": None, "n": 0, "fora": 1}


# ================================================================== a trava
def _cfg(caminho: Path = CONFIG, **troca) -> dict:
    c = json.loads(caminho.read_text(encoding="utf-8"))
    c.update(troca)
    return c


def _plano_com(status: str, registro: bool) -> str:
    linhas = (RAIZ / r5.PLANO).read_text(encoding="utf-8").splitlines()
    i = next(i for i, x in enumerate(linhas) if x.startswith("**Status:"))
    linhas[i] = status
    linhas = [x for x in linhas if not x.startswith(r5.TITULO_REGISTRO)]
    texto = "\n".join(linhas)
    return texto + (f"\n\n{r5.TITULO_REGISTRO}\n\no registro (so no teste)\n" if registro else "")


def test_a_config_da_analise_e_a_do_plano():
    cfg = _cfg()
    assert tuple(cfg["unidades"]["bases"]) == r5.BASES and cfg["unidades"]["k"] == r5.K_POR_BASE and cfg["dias"] == r5.DIAS
    assert cfg["vidas"] == r5.VIDAS_I2 and cfg["plano"] == r5.PLANO
    assert r5.DONOS == ("atencioso", "relapso", "aleatorio")


def test_a_trava_libera_so_com_aprovado_e_registro():
    cfg = _cfg()
    assert r5.modo_da_config(cfg, _plano_com(APROVADO, True)) == r5.FASE
    with pytest.raises(RuntimeError, match="registro"):
        r5.modo_da_config(cfg, _plano_com(APROVADO, False))
    with pytest.raises(RuntimeError, match="APROVADO"):
        r5.modo_da_config(cfg, _plano_com("**Status: PROPOSTO.**", True))


def test_hoje_a_analise_e_recusada_sem_o_registro():
    """o plano esta APROVADO, mas a secao do registro so entra no I5b, antes da primeira vida rejogada"""
    if r5.TITULO_REGISTRO in (RAIZ / r5.PLANO).read_text(encoding="utf-8"):
        pytest.skip("o registro ja esta no plano")
    with pytest.raises(RuntimeError, match="registro"):
        r5.modo_da_config(_cfg())


def test_fora_do_plano_falha_alto():
    plano = _plano_com(APROVADO, True)
    with pytest.raises(ValueError):
        r5.modo_da_config(_cfg(unidades={"bases": list(r5.BASES), "k": 5, "prefixo": r5.PREFIXO}), plano)
    with pytest.raises(ValueError):
        r5.modo_da_config(_cfg(dias=10), plano)
    with pytest.raises(ValueError):
        r5.modo_da_config(_cfg(vidas="outro.tar.gz"), plano)
    with pytest.raises(bv.SementeSemPlano):
        r5.modo_da_config(_cfg(unidades={"bases": [12345], "k": 12, "prefixo": r5.PREFIXO}), plano)
    with pytest.raises(ValueError):
        r5.modo_da_config(_cfg(sobra=1), plano)
    with pytest.raises(ValueError, match="dias"):
        r5.modo_da_config(_cfg(FUMACA, dias=7))
    with pytest.raises(ValueError, match="null"):
        r5.modo_da_config(_cfg(FUMACA, vidas=r5.VIDAS_I2))
    with pytest.raises(ValueError, match="duas sementes"):
        r5.modo_da_config(_cfg(FUMACA, unidades={"bases": [101], "k": 1, "prefixo": r5.PREFIXO}))
    assert r5.modo_da_config(_cfg(FUMACA)) == "fumaca"


def test_processos_e_pasta(tmp_path):
    with pytest.raises(ValueError):
        r5.rodar(_cfg(FUMACA), tmp_path / "x", 5)
    (tmp_path / "existe").mkdir()
    with pytest.raises(FileExistsError):
        r5.rodar(_cfg(FUMACA), tmp_path / "existe", 1)


# ================================================================== o pacote de vidas
def _pacote(caminho: Path, nomes: list[str]) -> None:
    with tarfile.open(caminho, "w:gz") as tar:
        for n in nomes:
            info = tarfile.TarInfo(n)
            info.size = 2
            tar.addfile(info, io.BytesIO(b"{}"))


def test_ler_vidas_falha_alto(tmp_path):
    esperadas = [("REL", "atencioso", 7), ("REL", "relapso", 7)]
    ok = tmp_path / "ok.tar.gz"
    _pacote(ok, [r5.nome_da_vida(*e) for e in esperadas] + [r5.nome_da_vida("REL", "incoerente", 7)])
    assert set(r5.ler_vidas(ok, esperadas)) == set(esperadas)
    falta = tmp_path / "falta.tar.gz"
    _pacote(falta, [r5.nome_da_vida(*esperadas[0])])
    with pytest.raises(RuntimeError, match="faltam"):
        r5.ler_vidas(falta, esperadas)
    sobra = tmp_path / "sobra.tar.gz"
    _pacote(sobra, [r5.nome_da_vida(*e) for e in esperadas] + [r5.nome_da_vida("REL", "atencioso", 8)])
    with pytest.raises(RuntimeError, match="fora do plano"):
        r5.ler_vidas(sobra, esperadas)


# ================================================================== a analise num caso sintetico
def _registro(braco: str, dono: str, semente: int) -> dict:
    """o LUGAR de cada pet e um bloco so dele (a semente e o dono), igual todo dia: o habito de lugar e total; a SEQ e a HORA sao iguais
    para todos (nenhum habito)"""
    lugar = [0] * 128
    lugar[(semente * 3 + r5.DONOS.index(dono)) % 128] = 20
    comum = {"SEQ": [20] + [0] * 48, "HORA": [20] + [0] * 83}
    return {"braco": braco, "dono": dono, "semente": semente,
            "perfis": {str(d): {"LUGAR": lugar, **comum} for d in range(1, 15)},
            "regiao": {str(d): {"casa": 20} for d in range(1, 15)}}


def test_analise_sintetica():
    regs = [_registro(b, d, s) for b in r5.BRACOS for d in r5.DONOS for s in range(5)]
    a = r5.analisar(regs, 14, boot=200)
    assert a["janela"] == [8, 14] and a["dias_cedo"] == [1, 7]
    for braco in r5.BRACOS:
        lugar = a["por_braco"][braco]["por_perfil"]["LUGAR"]
        assert lugar["medias"]["H_dono"]["media"] == pytest.approx(1.0) and lugar["medias"]["D_si"]["media"] == 0
        assert lugar["ic95"]["H_dono"][0] > 0 and lugar["frases"]["H_dono"].startswith("o pet tem habito")
        seq = a["por_braco"][braco]["por_perfil"]["SEQ"]
        assert seq["medias"]["H_dono"]["media"] == 0 and seq["frases"]["H_dono"] == "nao se distingue de zero nesta analise"
        assert a["por_braco"][braco]["dias_fora"]["janela"] == {d: 0 for d in r5.DONOS}
        assert a["por_braco"][braco]["regiao"]["atencioso"] == {"casa": 1.0}
    regs[0]["perfis"]["9"] = None
    b = r5.analisar(regs, 14, boot=50)["por_braco"][regs[0]["braco"]]["dias_fora"]["janela"]
    assert b[regs[0]["dono"]] == 1


# ================================================================== a fumaca de ponta a ponta
def test_fumaca_de_ponta_a_ponta(tmp_path):
    pasta = tmp_path / "fumaca"
    cfg = _cfg(FUMACA, dias=8, unidades={"bases": [101], "k": 2, "prefixo": r5.PREFIXO})
    r = r5.rodar(cfg, pasta, 1, boot=50)
    assert r["meta"]["modo"] == "fumaca" and len(r["registros"]) == 2 * len(r5.BRACOS) * len(r5.DONOS)
    for n in ("meta.json", "perfis.jsonl", "analise.json", "custo.json", "vidas_fumaca.tar.gz"):
        assert (pasta / n).exists()
    linhas = (pasta / "perfis.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(linhas) == len(r["registros"]) * 8 * len(M.PERFIS_HABITO)
    a = json.loads((pasta / "analise.json").read_text(encoding="utf-8"))
    assert a["janela"] == [8, 8] and set(a["por_braco"]) == set(r5.BRACOS)
    assert set(a["por_braco"]["REL"]["por_perfil"]) == set(M.PERFIS_HABITO)
    # a analise sai do perfis.jsonl gravado: refeita dele, sai igual
    lidos = r5._ler_perfis(pasta / "perfis.jsonl", r["registros"])
    assert bv._dump(r5.analisar(lidos, 8, 50)) == bv._dump({k: v for k, v in a.items() if k not in ("modo", "fase", "plano", "vidas")})
