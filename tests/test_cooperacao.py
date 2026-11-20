"""A cooperacao (docs/TAREFA_V3_COOPERACAO.md, etapa CO3): os atos sociais derivados, a pontuacao e a reputacao (digilab/cooperacao.py).

- o gabarito do TS (web/app/test/gabaritos/cooperacao_python.json.gz) refeito byte a byte; o exportador ja falha alto se a medida ligada
  mudar uma vida (o G-SEM-DECISAO), nas cinco vidas da CO1 e nas duas do cerebro aleatorio;
- a medida e funcao do log: o replay do registro com a medida ligada da os mesmos atos, a mesma pontuacao e a mesma reputacao;
- desligada, nada muda: nem a chave no resumo;
- a ConfigCooperacao (os numeros, o status e a fonte de cada um) e o que a Cooperacao recusa."""
from __future__ import annotations

import gzip
import json
import sys
from dataclasses import fields, replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "experiments"))

import exportar_gabarito_cooperacao as ec  # noqa: E402
import exportar_gabarito_grupo as eg  # noqa: E402

from digilab.config import (CONFIG_COOPERACAO, CONFIG_COOPERACAO_LIGADA, PARAMETROS_COOPERACAO, ConfigCooperacao)  # noqa: E402
from digilab.cooperacao import Conta, Cooperacao, decair, ganho_da_refeicao  # noqa: E402
from digilab.corpo import k_meia_vida  # noqa: E402
from digilab.grupo import RegistroGrupo, reproduzir_grupo  # noqa: E402


@pytest.fixture(scope="module")
def gabarito() -> dict:
    return ec.gerar()


def test_o_gabarito_do_ts_e_refeito_byte_a_byte(gabarito):
    gravado = json.loads(gzip.decompress(ec.ARQUIVO.read_bytes()).decode())
    assert gravado == json.loads(json.dumps(gabarito, sort_keys=True, separators=(",", ":")))


def test_o_gabarito_cobre_os_tres_atos_e_os_sinais(gabarito):
    atos = [a for v in gabarito["vidas"] for a in v["cooperacao"]["atos"]] + gabarito["sinteticos"]["resumo"]["atos"]
    assert {a["ato"] for a in atos} == {"disputa", "contencao", "encostar"}
    assert {a["sinal"] for a in atos} == {-1, 0, 1}
    assert any(a["repeticao"] > 0 for a in atos) and any(not a["testemunhas"] for a in atos)
    assert len(gabarito["vidas"]) == 7


def test_g_sem_decisao_a_medida_ligada_nao_muda_as_vidas_da_co1(gabarito):
    co1 = json.loads(gzip.decompress(ec.ARQUIVO_CO1.read_bytes()).decode())
    for v, vc in zip(gabarito["vidas"], co1["vidas"]):
        assert v["resumo_sha256"] == vc["resumo_sha256"]


def test_desligada_o_resumo_nao_tem_a_chave():
    g = ec._grupo(*eg.VIDAS[0], None)
    assert g.coop is None and "cooperacao" not in g.resumo()


def test_a_medida_e_funcao_do_log():
    v = ec.VIDAS_NOVAS[1]
    g = ec._grupo(*v, CONFIG_COOPERACAO_LIGADA)
    fabricas = {i: ec._fabricas(v[1], v[2], v[3]["AB".index(i)]) for i in g.motores}
    r = reproduzir_grupo(RegistroGrupo.de_jsonl(g.registro.para_jsonl()), fabricas, eg.LAYOUTS[v[1]],
                         cfg_cooperacao=CONFIG_COOPERACAO_LIGADA)
    assert r.resumo()["cooperacao"] == g.resumo()["cooperacao"]
    assert len(g.resumo()["cooperacao"]["atos"]) > 0


def test_a_config_cooperacao():
    assert CONFIG_COOPERACAO.ligada is False and CONFIG_COOPERACAO_LIGADA.ligada is True
    assert CONFIG_COOPERACAO.k_meia_vida_pontuacao == k_meia_vida(CONFIG_COOPERACAO.meia_vida_pontuacao)
    assert set(PARAMETROS_COOPERACAO) == {f.name for f in fields(ConfigCooperacao)}
    assert all(s in ("PROPOSTO", "DECIDIDO") and fonte for s, fonte in PARAMETROS_COOPERACAO.values())
    for ruim in ({"escala": 0}, {"meia_vida_pontuacao": -1}, {"janela_novidade": 1.5}, {"piso_fome": 1.0}):
        with pytest.raises(ValueError):
            replace(CONFIG_COOPERACAO, **ruim)
    with pytest.raises(TypeError):
        replace(CONFIG_COOPERACAO, ligada=1)


def test_a_conta():
    assert decair(-1000, 0, 32) == -1000 and decair(1000, 10, 32) == -decair(-1000, 10, 32)
    with pytest.raises(ValueError):
        decair(1, -1, 32)
    c = Conta(CONFIG_COOPERACAO_LIGADA)
    assert c.somar(0, "contencao", "B", 1000)[1:] == (1000, 1000)
    assert c.somar(10, "contencao", "B", 1000)[:2] == (1, 500)
    assert c.somar(1440, "contencao", "B", 1000)[:2] == (0, 1000)          # a janela nova
    assert 0 < c.em(1440 + 1440) < c.em(1440)                               # a meia-vida: cai, e devagar
    # um dia depois, quase a metade: o k inteiro (32, de 31,5 arredondado pela regra do corpo) encurta a meia-vida em ~1,5 %
    assert 0.48 * c.em(1440) <= c.em(2880) <= 0.5 * c.em(1440)
    assert ganho_da_refeicao({"fome_antes": 0.5, "fome_depois": 0.5, "humor_antes": 0.5, "humor_depois": 0.2}, 1024) == 0


def test_a_cooperacao_recusa():
    with pytest.raises(ValueError):
        Cooperacao(CONFIG_COOPERACAO)
    c = Cooperacao(CONFIG_COOPERACAO_LIGADA)
    pos, raios = {"A": (0, 0), "B": (1, 0)}, {"A": 96, "B": 96}
    with pytest.raises(ValueError, match="sem a refeicao"):
        c.fim_do_tick(5, [{"vencedor": "A", "perdedor": "B", "comida": 3}], [], {"A": "comer", "B": "comer"}, pos, raios)
