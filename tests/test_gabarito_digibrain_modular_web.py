"""O exportador do gabarito do DigiBrain modular para a web (docs/TAREFA_V3_LAB_MODULAR.md, etapa LM0): sai igual em duas execucoes, byte a byte,
e o gabarito gravado (web/app/test/gabaritos/digibrain_modular_*) bate com uma execucao nova. Se mudar o pacote digilab/digibrain/, o
mundo ou o exportador, rode `python experiments/exportar_gabarito_digibrain_modular.py`. Sementes: as dos testes (101 e 202)."""
from __future__ import annotations

import gzip
import hashlib
import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import exportar_gabarito_digibrain_modular as E  # noqa: E402

from digilab.config import CONFIG_DIGIBRAIN_INATOS  # noqa: E402


@pytest.fixture(scope="module")
def duas_execucoes():
    return E.arquivos(), E.arquivos()


def test_o_exportador_sai_igual_em_duas_execucoes_byte_a_byte(duas_execucoes):
    a, b = duas_execucoes
    assert a.keys() == b.keys()
    for nome in a:
        assert E.texto_original(nome, a[nome]) == E.texto_original(nome, b[nome]), nome


def test_o_gabarito_gravado_bate_com_uma_execucao_nova(duas_execucoes):
    novo = duas_execucoes[0]
    for nome, dados in novo.items():
        gravado = (E.PASTA / nome).read_bytes()
        assert E.texto_original(nome, gravado) == E.texto_original(nome, dados), nome


def test_o_sha256_das_constantes_e_o_do_texto_original_e_cada_arquivo_cabe():
    c = json.loads(E.ARQUIVO_CONSTANTES.read_text(encoding="utf-8"))
    assert sorted(c["arquivos"]) == sorted(f"{E.PREFIXO}{lugar}.json" for lugar in E.LUGARES)
    for nome, info in c["arquivos"].items():
        gz = E.PASTA / info["gz"]
        assert gz.stat().st_size < 10 * 1024 * 1024
        bruto = gzip.decompress(gz.read_bytes())
        assert hashlib.sha256(bruto).hexdigest() == info["sha256"] and len(bruto) == info["bytes"]
    assert E.ARQUIVO_CONSTANTES.stat().st_size < 10 * 1024 * 1024


def test_as_constantes_sao_as_efetivas_do_laboratorio():
    c = json.loads(E.ARQUIVO_CONSTANTES.read_text(encoding="utf-8"))
    cd = c["config_digibrain"]
    assert cd["ligada"] and cd["cheiro_inato"] and cd["intencao_cheiro"] and cd["memoria_autobio"] and cd["controle_mem"] == "rel"
    assert cd["p1"] and cd["p2"] and cd["m_mem"] and cd["persistencia"]
    for desligada in ("facetas_mem", "redecidir_evento", "credito_corrida", "intencao_suspensa", "modula_g_apr"):
        assert cd[desligada] is False
    assert cd["controle_g_apr"] == "nenhum" and cd["g_apr_constante"] == 0
    assert c["config_digibrain_inatos"] == E.paraj(CONFIG_DIGIBRAIN_INATOS.__dict__)


def test_a_cobertura_das_vidas_inclui_intencao_lembranca_e_p2():
    c = json.loads(E.ARQUIVO_CONSTANTES.read_text(encoding="utf-8"))
    cob = c["cobertura"]
    assert len(cob) == len(E.LUGARES) * len(E.DONOS) * len(E.SEMENTES)
    for chave in ("habito_p2", "lembranca_com_termo", "lembranca_sem", "lugar_lembrado_alvo", "consolidacoes", "episodios_autobio",
                  "busca_entregue", "persistencia", "incentivo_p1", "memoria_recuperada"):
        assert sum(v[chave] for v in cob) > 0, chave
    assert {m for v in cob for m in v["fins"]} >= {"achou", "meta", "trocou"}


def test_toda_decisao_tem_o_agir_o_motivo_e_a_assinatura():
    with gzip.open(E.PASTA / f"{E.PREFIXO}comedouro.json.gz", "rt", encoding="utf-8") as f:
        g = json.load(f)
    for vida in g["vidas"]:
        assert [d["k"] for d in vida["decisoes"]] == list(range(len(vida["decisoes"])))
        for d in vida["decisoes"]:
            assert any(ch["m"] == "adapt.agir" for ch in d["chamadas"])
            assert d["motivo"]["k"] == d["k"] and set(d["assinatura"]) == set(E.ASSINADOS)
