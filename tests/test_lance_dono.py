"""O lance do dono (docs/TAREFA_V3_BOLA_BRINCAR.md, BB1): a `ConfigLanceDono`, o lance da bola no `Mundo` (o fluxo `dono-bola`), o pet que
decide no mesmo tick, o convite `bola_do_dono` do DigiBrain modular, o cerebro A sem convite, o grupo e o replay. A chave desligada (a vida de
hoje byte a byte) esta no tests/test_gabarito_lance_dono.py.

As medidas (G-BB-1 e G-BB-2) usam o roteiro do dono que brinca de tempos em tempos (tests/gabarito_lance_dono.py: o Brincar a cada 2 h de
jogo, a racao no comedouro a cada 6 h), o braco REL (o do jogo) com o sono que segura (o pet v27; o v29 e ele com o lance), as sementes 101,
202 e 303 dos testes, 3 dias.

    python tests/test_lance_dono.py     # imprime a tabela da medida (a da secao "Resultado da BB1" da tarefa)
"""
from __future__ import annotations

import json
import sys
from dataclasses import fields, replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import gabarito_lance_dono as G  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402

from digilab.config import (CONFIG_DIGIBRAIN_INATOS, CONFIG_LANCE_DONO, CONFIG_LANCE_DONO_LIGADA, CONFIG_MUNDO, CONFIG_PADRAO,  # noqa: E402
                            CONFIG_SONO_SEGURA_LIGADA, PARAMETROS_LANCE_DONO, ConfigLanceDono)
from digilab.events import AcaoUsuario  # noqa: E402
from digilab.grupo import reproduzir_grupo, sementes_do_grupo  # noqa: E402
from digilab.mundo import MotorMundo, distancia  # noqa: E402
from digilab.config import CONFIG_GRUPO_LIGADA  # noqa: E402

S = CONFIG_DIGIBRAIN_INATOS.escala
SEMENTES = (101, 202, 303)
CL = CONFIG_LANCE_DONO_LIGADA
SONO = CONFIG_SONO_SEGURA_LIGADA


def _fabricas(braco: str, semente: int, lance=CL, sono=SONO):
    return orq.fabricas(braco, "atencioso", semente, G.DIAS, orq.ORCAMENTO_POR_DIA, conserto=True, sono=sono, lance=lance)


def _vida(braco: str, semente: int, lance=CL, sono=SONO, racao: bool = True):
    fp, fm = _fabricas(braco, semente, lance, sono)
    return G.roteiro(fp, fm, semente, racao=racao), (fp, fm)


def _ticks(motor) -> list[int]:
    return [t for t, _ in motor.acoes_recentes(10 ** 9)]


def medida(cl: ConfigLanceDono = CL, sementes=SEMENTES) -> dict:
    """por semente: os lances com decisao depois deles; os elegiveis (a primeira decisao do lance, no mesmo tick, sem o reflexo do sono e
    sem a fome urgente); os chutes na janela (uma rolagem da bola entre o lance e o fim da janela) e as recusas dos elegiveis; e, nas
    decisoes da janela com o reflexo ou a fome urgente, quantas sao e quantas chutam (o G-BB-2)"""
    out = {}
    for s in sementes:
        for racao in (True, False):
            fp, fm = _fabricas("REL", s, cl)
            m = G.roteiro(fp, fm, s, racao=racao)
            c = orq.cerebro_de(m.politica._pm)
            ticks = _ticks(m)
            rol = [r["tick"] for r in m.mundo.rolagens]
            linha = {"lances": 0, "elegiveis": 0, "chutes": 0, "recusas": 0, "sem_urgencia_reflexo": 0, "sem_urgencia_fome": 0,
                     "dec_reflexo": 0, "dec_fome": 0, "chutes_bloqueados": 0}
            for lance in m.mundo.lances:
                t = lance["tick"]
                if t not in ticks:                   # o ultimo Brincar da vida, sem decisao depois
                    continue
                mo = c.motivos[ticks.index(t)]
                if not mo["lance"]["convite"]:
                    raise AssertionError(f"a decisao do lance (tick {t}) sem o convite")
                linha["lances"] += 1
                chutou = any(t <= r < t + cl.janela_convite_ticks for r in rol)
                if mo["reflexo"]:
                    linha["sem_urgencia_reflexo"] += 1
                elif mo["lance"]["fome_urgente"]:
                    linha["sem_urgencia_fome"] += 1
                else:
                    linha["elegiveis"] += 1
                    linha["chutes"] += chutou
                    linha["recusas"] += not chutou
            for k, t in enumerate(ticks):
                mo = c.motivos[k]
                if not mo["lance"]["convite"] or not (mo["reflexo"] or mo["lance"]["fome_urgente"]):
                    continue
                linha["dec_reflexo" if mo["reflexo"] else "dec_fome"] += 1
                linha["chutes_bloqueados"] += t in rol
            out[(s, "com racao" if racao else "sem racao")] = linha
    return out


@pytest.fixture(scope="module")
def tabela():
    return medida()


# ------------------------------------------------------------------ a config
def test_a_config_padrao_desligada_e_o_status_de_cada_campo():
    assert CONFIG_LANCE_DONO.ligada is False and CL.ligada is True
    assert (CL.lance_min_celulas, CL.lance_max_celulas, CL.janela_convite_ticks, CL.w_bola_do_dono) == (2, 3, 30, 4 * S)
    assert {f.name for f in fields(ConfigLanceDono)} == set(PARAMETROS_LANCE_DONO)
    assert all(st == "PROPOSTO" and "SEM FONTE" in fonte for st, fonte in PARAMETROS_LANCE_DONO.values())
    with pytest.raises(TypeError):
        ConfigLanceDono(ligada=1)
    with pytest.raises(ValueError):
        ConfigLanceDono(lance_min_celulas=4)
    with pytest.raises(ValueError):
        ConfigLanceDono(janela_convite_ticks=0)


def test_o_lance_exige_o_mundo():
    from digilab.policy import PoliticaInstinto
    with pytest.raises(ValueError, match="mundo fisico"):
        MotorMundo(PoliticaInstinto(CONFIG_PADRAO), CONFIG_PADRAO, 101, cfg_mundo=CONFIG_MUNDO, cfg_lance_dono=CL)


# ------------------------------------------------------------------ a chave desligada nao cria a rng nova
def test_desligada_nem_o_fluxo_nem_o_registro():
    m, _ = _vida("REL", 101, lance=None)
    assert m.mundo.rng_lance is None and m.mundo.lances is None and m.mundo.cld is None
    assert "lances" not in m.mundo.resumo() and "lances" not in m.resumo_mundo_fisico()
    assert all("lance" not in mo for mo in orq.cerebro_de(m.politica._pm).motivos)
    with pytest.raises(ValueError, match="ConfigLanceDono"):
        m.convite_ativo()


def test_o_cerebro_sem_a_chave_recusa_o_convite():
    fp, _ = _fabricas("REL", 101, lance=None)
    with pytest.raises(RuntimeError, match="ConfigLanceDono"):
        orq.cerebro_de(fp(CONFIG_PADRAO)).bola_do_dono(True)


def test_o_motor_com_o_lance_e_o_cerebro_sem_falha_alto():
    _, fm = _fabricas("REL", 101)
    fp, _ = _fabricas("REL", 101, lance=None)
    with pytest.raises(RuntimeError, match="ConfigLanceDono"):
        G.roteiro(fp, fm, 101, dias=1)


# ------------------------------------------------------------------ BB-1 a BB-3: o lance
def _motor_parado(braco: str = "REL", semente: int = 101):
    fp, fm = _fabricas(braco, semente)
    m = fm(fp(CONFIG_PADRAO), CONFIG_PADRAO, semente)
    m.avancar(200)
    return m


def test_o_lance_joga_a_bola_perto_do_pet_pelo_fluxo_proprio():
    m = _motor_parado()
    bola_antes = m.mundo.rng_bola.getstate()
    pet, tick = m.pet, m._estado.tick
    for _ in range(12):
        m.observar(AcaoUsuario.BRINCAR)
    assert len(m.mundo.lances) == 12 and m.mundo.rng_bola.getstate() == bola_antes      # o `mundo-bola` de quem nao lanca nao anda
    sub = m.cmf.sub
    for lance in m.mundo.lances:
        assert lance["tick"] == m._tm(tick) and lance["pet"] == pet
        assert CL.lance_min_celulas <= lance["celulas"] <= CL.lance_max_celulas and 0 <= lance["direcao"] < 16
        d = distancia(lance["para"][0] - pet[0], lance["para"][1] - pet[1])
        assert (lance["celulas"] - 1) * sub <= d <= lance["celulas"] * sub + 1     # o corte do mapa e a terra podem encurtar
        assert m.mundo.seca(*lance["para"])
    ultimo = m.mundo.lances[-1]["para"]
    assert m.mundo.bola == {"x0": ultimo[0], "y0": ultimo[1], "x1": ultimo[0], "y1": ultimo[1], "t0": m._tm(tick), "d": 0}
    assert len({(x["direcao"], x["celulas"]) for x in m.mundo.lances}) > 3        # o fluxo sorteia


def test_bb2_o_brincar_de_sempre_continua():
    """o Brincar com o lance e o de hoje no corpo, no estado e no cerebro; so a bola e o momento da decisao mudam"""
    estados = []
    for lance in (None, CL):
        fp, fm = _fabricas("REL", 101, lance)
        m = fm(fp(CONFIG_PADRAO), CONFIG_PADRAO, 101)
        m.avancar(200)
        m.observar(AcaoUsuario.BRINCAR)
        d = m.estado()
        d["mundo"].pop("bola")
        c = orq.cerebro_de(m.politica._pm)
        estados.append((json.dumps(d, sort_keys=True, default=repr), repr(m._estado), json.dumps(c._gestos), dict(c.gestos),
                        json.dumps(m.corpo.para_dict(), sort_keys=True, default=repr)))
    assert estados[0] == estados[1]


def test_bb3_o_pet_decide_no_mesmo_tick():
    m = _motor_parado()
    t = m._estado.tick
    assert m._proxima_decisao > t
    m.observar(AcaoUsuario.BRINCAR)
    assert m._proxima_decisao == t and m.convite_ativo()
    m.avancar(1)
    assert _ticks(m)[-1] == t
    assert orq.cerebro_de(m.politica._pm).motivos[-1]["lance"]["convite"] is True
    m.avancar(CL.janela_convite_ticks)
    assert not m.convite_ativo()


def test_bb4_o_convite_entra_no_inato_do_brincar_e_so_ali():
    """em cada decisao com o convite, as unidades com a entrada em 0 (a mesma conta do M-IMPULSO) so diferem no inato do brincar, de
    mul(w_bola_do_dono, S)"""
    fp, fm = _fabricas("REL", 101)
    reg = fp(CONFIG_PADRAO)
    imp = orq.cerebro_de(reg).m.impulso
    original = imp.unidades
    vistos = []

    def unidades(*a, **kw):
        out = original(*a, **kw)
        if kw["bola_do_dono"]:
            zero, _ = original(*a, **{**kw, "bola_do_dono": 0})
            for u, u0 in zip(out[0], zero):
                assert u["chave"] == u0["chave"]
                d = {t: u["termos"][t] - u0["termos"][t] for t in u["termos"]}
                assert d == {**dict.fromkeys(d, 0), "inato": CL.w_bola_do_dono if u["acao"] == "brincar" else 0}
            vistos.append(len(out[0]))
        return out
    imp.unidades = unidades
    G.roteiro(lambda cfg=None: reg, fm, 101, dias=1)
    assert vistos


# ------------------------------------------------------------------ G-BB-1 e G-BB-2
def test_g_bb_1_o_pet_acordado_e_sem_fome_urgente_chuta_a_bola(tabela):
    com = [v for (s, r), v in tabela.items() if r == "com racao"]
    eleg = sum(v["elegiveis"] for v in com)
    chutes = sum(v["chutes"] for v in com)
    assert eleg >= 30, eleg
    assert chutes * 10 >= 8 * eleg, (chutes, eleg)


def test_g_bb_2_dormindo_ou_com_a_fome_urgente_ele_nao_chuta(tabela):
    assert sum(v["dec_reflexo"] for v in tabela.values()) > 0
    assert sum(v["dec_fome"] for v in tabela.values()) > 0
    assert sum(v["chutes_bloqueados"] for v in tabela.values()) == 0


def test_o_convite_e_o_fora_da_janela_valem_zero_com_a_fome_urgente():
    m, _ = _vida("REL", 202, racao=False)
    ms = orq.cerebro_de(m.politica._pm).motivos
    assert any(x["lance"]["fome_urgente"] for x in ms)
    assert all(x["lance"]["bola_do_dono"] == (S if x["lance"]["convite"] and not x["lance"]["fome_urgente"] else 0) for x in ms)


# ------------------------------------------------------------------ G-BB-3: o replay
@pytest.mark.parametrize("braco", ("REL", "A11"))
def test_g_bb_3_o_replay_refaz_a_vida(braco):
    m, fabs = _vida(braco, 303)
    assert m.mundo.lances
    orq.conferir_replay(m, fabs, 303, m.log.para_jsonl())


# ------------------------------------------------------------------ BB-6: o cerebro A
def test_bb6_com_o_a_so_a_bola_se_mexe():
    """o A nao tem o convite (nenhum gancho) e segue no relogio de sempre (as decisoes nos mesmos ticks); a bola cai perto dele"""
    sem, _ = _vida("A11", 101, lance=None)
    com, _ = _vida("A11", 101)
    assert not hasattr(orq.cerebro_de(com.politica._pm), "bola_do_dono")
    assert _ticks(com) == _ticks(sem)
    assert len(com.mundo.lances) == len([e for e in com.log if e.tipo == "acao_usuario" and e.valor == "brincar"])


# ------------------------------------------------------------------ o grupo aceita o lance
def test_o_grupo_aceita_o_lance_e_o_replay_o_refaz():
    g = G.grupo_modular(101, lance=CL, sono=SONO)
    assert g.mundo.lances and "lances" in g.mundo.resumo()
    pets = {lance["pet"] for lance in g.mundo.lances}
    assert len(pets) >= 2                                 # o lance cai perto do pet do Brincar, de qualquer dos dois
    for m in g.motores.values():
        assert any(mo["lance"]["convite"] for mo in orq.cerebro_de(m.politica._pm).motivos)
    sementes = sementes_do_grupo(101, CONFIG_GRUPO_LIGADA.ids)
    fabs = {i: G.fabricas_grupo("REL", d, sementes[i], lance=CL, sono=SONO) for i, d in zip(CONFIG_GRUPO_LIGADA.ids, ("atencioso", "relapso"))}
    r = reproduzir_grupo(g.registro, fabs, orq.CM)
    assert G.eg._json(r.resumo()) == G.eg._json(g.resumo())


def test_no_grupo_o_lance_ligado_duas_vezes_com_outra_config_falha_alto():
    g = G.grupo_modular(101, dias=1, lance=CL, sono=SONO)
    with pytest.raises(ValueError, match="outra ConfigLanceDono"):
        g.mundo.ligar_lance(replace(CL, janela_convite_ticks=31))


if __name__ == "__main__":
    t = medida()
    print("| semente | roteiro | lances | elegiveis | chutes na janela | recusas | lance com reflexo | lance com fome urgente | "
          "decisoes da janela com reflexo | com fome urgente | chutes nelas |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    for (s, r), v in t.items():
        print(f"| {s} | {r} | {v['lances']} | {v['elegiveis']} | {v['chutes']} | {v['recusas']} | {v['sem_urgencia_reflexo']} | "
              f"{v['sem_urgencia_fome']} | {v['dec_reflexo']} | {v['dec_fome']} | {v['chutes_bloqueados']} |")
