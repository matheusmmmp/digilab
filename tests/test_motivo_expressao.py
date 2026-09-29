"""Parte A: motivo unificado e expressao. Somente leitura: nada muda decisao."""

import json
import random
import re
import sys
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import digilab.config as config_mod  # noqa: E402
import digilab.expressao as expressao_mod  # noqa: E402
from digilab.combate_v2.bots import TODOS, bot  # noqa: E402
from digilab.combate_v2.partida import jogar, reproduzir  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.expressao import (  # noqa: E402
    ESTAGIOS,
    FATORES,
    TabelaIncompleta,
    estagio_por_idade,
    expressar,
    marcadores_citados,
    validar_tabelas,
)
from digilab.motivo import (  # noqa: E402
    Motivo,
    PoliticaComMotivo,
    motivos_de_partida,
    motivos_de_vida,
    nome_base,
    regra_do_motivo,
)
from digilab.policies import PoliticaBandit  # noqa: E402
from digilab.policy import PoliticaInstinto  # noqa: E402
from digilab.protocol import PROTOCOLO_ARENA_V1, configs_congelados  # noqa: E402
from digilab.treino import simular_vida  # noqa: E402

DIAS, ORC = 2, 32
FABRICAS = {"bandit": lambda c=None: PoliticaBandit(c), "instinto": lambda c=None: PoliticaInstinto(c)}


def _vida(dono: str, pol: str, semente: int = 101, embrulhar: bool = True):
    interna = FABRICAS[pol]()
    politica = PoliticaComMotivo(interna) if embrulhar else interna
    v = simular_vida(dono, criar_dono(dono), politica, semente, DIAS, ORC)
    return v, politica


@pytest.fixture(scope="module")
def vidas():
    return {(d, p): _vida(d, p) for d in ("atencioso", "aleatorio") for p in ("bandit", "instinto")}


@pytest.fixture(scope="module")
def partidas():
    return [(a, b, jogar(bot(a), bot(b), 17 + i)) for i, (a, b) in enumerate(
        [(x, y) for x in TODOS for y in TODOS])]


# ------------------------------------------------------------ nada mudou


def test_embrulho_nao_muda_vida_nem_rng():
    for pol in ("bandit", "instinto"):
        com, emb = _vida("atencioso", pol)
        sem, _ = _vida("atencioso", pol, embrulhar=False)
        assert com.motor.log.para_jsonl() == sem.motor.log.para_jsonl()
        assert com.motor.estado() == sem.motor.estado()
        assert com.motor.acoes_recentes(10**9) == sem.motor.acoes_recentes(10**9)
        assert com.motor._rng_politica.getstate() == sem.motor._rng_politica.getstate()
        assert com.motor._rng_ambiente.getstate() == sem.motor._rng_ambiente.getstate()
        assert json.dumps(emb.estado_interno(), sort_keys=True) == json.dumps(
            sem.motor.politica.estado_interno(), sort_keys=True)
        assert len(emb.motivos) == len(com.motor.acoes_recentes(10**9))


def test_motivo_de_combate_nao_consome_rng(partidas):
    antes = random.getstate()
    for a, b, p in partidas[:10]:
        motivos_de_partida(list(p.log), (bot(a), bot(b)))
    assert random.getstate() == antes


def test_config_expressao_fora_dos_hashes(monkeypatch):
    import run_bateria_combate

    assert "ConfigExpressao" not in configs_congelados()
    cfg_json = json.loads((RAIZ / "experiments" / "configs" / "bateria_canonico.json").read_text(encoding="utf-8"))
    h_v1, h_bat = PROTOCOLO_ARENA_V1.hash(), run_bateria_combate.hashes(cfg_json)
    monkeypatch.setattr(config_mod, "CONFIG_EXPRESSAO", replace(config_mod.CONFIG_EXPRESSAO, limiar_motivo=0.9))
    assert PROTOCOLO_ARENA_V1.hash() == h_v1
    assert run_bateria_combate.hashes(cfg_json) == h_bat


def test_bateria_combate_v2_reproduz_artefatos(tmp_path):
    import run_bateria_combate

    cfg = json.loads((RAIZ / "experiments" / "configs" / "bateria_canonico.json").read_text(encoding="utf-8"))
    cfg["saida"] = str(tmp_path / "bat")
    (tmp_path / "cfg.json").write_text(json.dumps(cfg), encoding="utf-8")
    assert run_bateria_combate.main(["--config", str(tmp_path / "cfg.json")]) == 2  # REPROVADA, como gravado
    canon = RAIZ / "artifacts_combate_v2"
    for arq in ("matriz.json", "equilibrio.json", "partidas.csv", "amostra_replay.jsonl"):
        assert (canon / arq).read_bytes() == (tmp_path / "bat" / arq).read_bytes(), arq
    a = json.loads((canon / "gates.json").read_text(encoding="utf-8"))
    b = json.loads((tmp_path / "bat" / "gates.json").read_text(encoding="utf-8"))
    for m in (a, b):
        m.pop("ambiente")
        # TAREFA_CORRECAO_COMBATE: os fontes ganharam as chaves da V2C (desligadas na V2); o hash dos
        # fontes muda, o resultado nao (os artefatos acima sao os mesmos bytes)
        m["hashes"].pop("regras_sha256")
    assert a == b


# ------------------------------------------------------------ honestidade

_REF = re.compile(r"(?:evento #|turno )([\d, #]+)\)")


def _refs_citadas(conteudo: str) -> set[int]:
    return {int(x) for g in _REF.findall(conteudo) for x in re.findall(r"\d+", g)}


def _checar_honestidade(m: Motivo, humor):
    bases = [nome_base(f) for f in (() if m.exploracao else m.fatores)]
    for est in ESTAGIOS:
        e = expressar(m, est, humor)
        citados = marcadores_citados(e.conteudo)
        if est == "bebe":
            assert not citados, (m, e)
        elif est in ("crianca", "adolescente"):
            assert citados == set(bases[:1]), (m, e)
        else:
            assert citados == set(bases[:2]), (m, e)
            assert _refs_citadas(e.conteudo) <= set(m.evento_ref), (m, e)
            if not bases:
                geral = (expressao_mod.GENERICO_INSTINTO if m.origem == "vida" and not m.exploracao
                         else expressao_mod.GENERICO_ADULTO)
                assert geral in e.conteudo


def test_honestidade_na_vida(vidas):
    n = 0
    for (_, _), (_, emb) in vidas.items():
        for m, h in zip(emb.motivos, emb.humores):
            _checar_honestidade(m, h)
            n += 1
    assert n > 0


def test_honestidade_no_combate_e_fatores_valiam_no_turno(partidas):
    from digilab.config import CONFIG_COMBATE_V2

    citados = 0
    for a, b, p in partidas:
        lut = (bot(a), bot(b))
        for t, lado, m, estado in motivos_de_partida(list(p.log), lut):
            _checar_honestidade(m, None)
            ev = next(e for e in p.log if e.get("t") == t)
            regra = regra_do_motivo(lut[lado].estilo, ev["ma" if lado == 0 else "mb"])
            if regra is None:
                assert not m.fatores
                continue
            for c in regra.condicoes:
                assert c.vale(estado, lado, CONFIG_COMBATE_V2), (t, lado, c)
                citados += c.nome != "sempre"
    assert citados > 0


def test_bebe_nunca_cita_e_sem_fator_nunca_vira_causa():
    for fator in FATORES:
        m = Motivo("combate", "defender", (fator,) if fator != "sempre" else (), (3,), None, False, turno=3)
        assert not marcadores_citados(expressar(m, "bebe").conteudo)
    vazio = Motivo("vida", "comer", (), (), 0.0, False, tick=10)
    for est in ESTAGIOS:
        assert not marcadores_citados(expressar(vazio, est, 0.5).conteudo)
    expl = Motivo("combate", "esquivar", (), (), None, True, turno=4)
    assert expressar(expl, "adulto").conteudo.endswith(expressao_mod.GENERICO_ADULTO)
    # vida sem fator e sem exploracao: quem decidiu foi o prior do instinto
    assert expressar(vazio, "adulto", 0.5).conteudo.endswith(expressao_mod.GENERICO_INSTINTO)


def test_dois_fatores_so_o_adulto_cita_os_dois():
    m = Motivo("combate", "golpe_rapido", ("distancia_eh(perto)", "guts_proprio_acima(40)"), (5,), None, False, turno=5)
    assert marcadores_citados(expressar(m, "adulto").conteudo) == {"distancia_eh", "guts_proprio_acima"}
    for est in ("crianca", "adolescente"):
        assert marcadores_citados(expressar(m, est).conteudo) == {"distancia_eh"}


# ------------------------------------------------------------ cobertura e estagio


def test_tabela_completa_e_falta_levanta_erro(monkeypatch):
    validar_tabelas()
    falta = dict(FATORES)
    falta.pop("fome")
    monkeypatch.setattr(expressao_mod, "FATORES", falta)
    with pytest.raises(TabelaIncompleta, match="fome"):
        validar_tabelas()


def test_tabela_rejeita_bebe_com_causa_e_marcador_ausente(monkeypatch):
    ruim = {k: dict(v) for k, v in FATORES.items()}
    ruim["fome"]["bebe"] = "fome!"
    monkeypatch.setattr(expressao_mod, "FATORES", ruim)
    with pytest.raises(TabelaIncompleta, match="bebe"):
        validar_tabelas()
    ruim["fome"]["bebe"] = ""
    ruim["fome"]["adulto"] = "porque sim"
    with pytest.raises(TabelaIncompleta, match="marcador"):
        validar_tabelas()


def test_estagio_provisorio_por_idade():
    cfg = config_mod.CONFIG_EXPRESSAO
    assert estagio_por_idade(0) == "bebe"
    assert estagio_por_idade(cfg.dias_fim_bebe) == "crianca"
    assert estagio_por_idade(cfg.dias_fim_crianca) == "adolescente"
    assert estagio_por_idade(cfg.dias_fim_adolescente) == "adulto"
    with pytest.raises(ValueError):
        estagio_por_idade(-1)


# ------------------------------------------------------------ replay


def test_replay_da_vida_reproduz_motivos_e_expressoes(vidas):
    for (dono, pol), (v, emb) in vidas.items():
        _, rep = motivos_de_vida(v.motor.log, lambda c, p=pol: FABRICAS[p](c), 101)
        # ao vivo sem indices do log: evento_ref de cuidado so existe no replay; compara o resto
        vivo = [replace(m, evento_ref=()) for m in emb.motivos]
        refeito = [replace(m, evento_ref=()) for m in rep.motivos]
        assert vivo == refeito, (dono, pol)
        assert [expressar(m, "crianca").conteudo for m in vivo] == [expressar(m, "crianca").conteudo for m in refeito]


def test_evento_ref_da_vida_aponta_para_acao_do_dono(vidas):
    for (_, pol), (v, _) in vidas.items():
        _, rep = motivos_de_vida(v.motor.log, lambda c, p=pol: FABRICAS[p](c), 101)
        eventos = list(v.motor.log)
        for m in rep.motivos:
            for r in m.evento_ref:
                assert eventos[r].tipo == "acao_usuario" and eventos[r].tick <= m.tick


def test_replay_da_partida_reproduz_motivos(partidas):
    for a, b, p in partidas[:20]:
        r = reproduzir(list(p.log), bot(a), bot(b))
        m1 = [(t, l, m) for t, l, m, _ in motivos_de_partida(list(p.log), (bot(a), bot(b)))]
        m2 = [(t, l, m) for t, l, m, _ in motivos_de_partida(list(r.log), (bot(a), bot(b)))]
        assert m1 == m2


def test_evento_desconhecido_no_log_de_combate_levanta_erro(partidas):
    a, b, p = partidas[0]
    with pytest.raises(ValueError, match="desconhecido"):
        motivos_de_partida(list(p.log) + [{"tipo": "clima"}], (bot(a), bot(b)))
