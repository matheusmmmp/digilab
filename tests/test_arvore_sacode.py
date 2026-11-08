"""O sacudir a arvore e a fruta do mundo como comida (docs/TAREFA_V3_ARVORE_SACODE.md, S1; os pets v20 do jogo web).

- O formato do log (events.sacudir_arvore, ler_sacudir_arvore): o id da arvore em letras e digitos ASCII.
- O galho (AS-3): nasce cheio, cada sacudida com fruta e lugar no chao derruba uma (AS-2), repoe uma a cada `recarga_galho_min`, e o
  relogio para com ele cheio. Sem fruta, com o chao cheio ou com a arvore parada, nada cai e nada se sorteia.
- Onde cai (AS-5): a ate `raio_queda_celulas` do tronco, do tipo da arvore, madura, com a origem = a arvore, pelo fluxo `arvore-sacode`.
- A queda natural nao muda (AS-4): os sorteios do fluxo `mundo-arvores` sao os mesmos com e sem sacudidas.
- Nao e cuidado (AS-1): o estado, o corpo e o cerebro nao recebem nada; vale com o pet dormindo.
- Sem o mundo, sem a chave, no grupo ou com uma arvore que nao existe, falha alto antes do log; o replay refaz a vida byte a byte.
- Desligadas, nenhuma chave nova no resumo nem no estado (o gabarito de hoje fica em tests/test_gabarito_arvore_sacode.py).
- A fruta do mundo como comida (AS-11): o laco nao entrega o `fruta_comida`, e o A do v11 com o corpo come a fruta sem quebrar.
- O CONFIG_MUNDO_ILHA e o MVP com J1, J2 e J3; o gabarito do G-PAR do TS (web/app/test/gabaritos/arvore_sacode_python.json) esta em dia.
Sementes: so as dos testes.
"""
from __future__ import annotations

import json
import sys
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import bancada_v2 as bv  # noqa: E402
import exportar_gabarito_arvore_sacode as G  # noqa: E402
import exportar_gabarito_mvp_mundo as e0  # noqa: E402
import gabarito_arvore_sacode as H  # noqa: E402

from digilab.config import (CONFIG_FRUTA_COMO_COMIDA_LIGADA, CONFIG_MUNDO_ILHA, CONFIG_MUNDO_MVP, CONFIG_PADRAO,  # noqa: E402
                            CONFIG_SACUDIR, CONFIG_SACUDIR_LIGADA, LAYOUT_MUNDO_PADRAO, ConfigSacudir)
from digilab.events import FRUTAS, Evento, ler_sacudir_arvore, sacudir_arvore  # noqa: E402
from digilab.mundo import (MotorMundo, Mundo, SacudirSemChave, distancia, fabricas_mundo, reproduzir_mundo)  # noqa: E402
from digilab.instinto_mundo import PoliticaInstintoMundo  # noqa: E402
from digilab.policy import PoliticaInstinto  # noqa: E402

TEXTO = G.ARQUIVO.read_text(encoding="utf-8")
GRAVADO = json.loads(TEXTO)
CM = CONFIG_MUNDO_ILHA
CS = CONFIG_SACUDIR_LIGADA
RAIO = CM.raio_queda_celulas * CM.sub
SEMENTES = (101, 202)                     # so dos testes


class Espiao:
    """O instinto do mundo com os ganchos do dono e do mundo contados: o sacudir nao chama nenhum"""

    def __init__(self, cfg=None):
        self._p = PoliticaInstintoMundo(cfg or CONFIG_PADRAO)
        self.chamadas: list[str] = []
        self.nome = "espiao"

    def agir(self, obs, rng):
        return self._p.agir(obs, rng)

    def observar(self, transicao) -> None:
        self._p.observar(transicao)

    def estado_interno(self) -> dict:
        return {"nome": self.nome}

    def receber_acao_dono(self, *a, **k) -> None:
        self.chamadas.append("receber_acao_dono")

    def consequencia_mundo(self, *a, **k) -> None:
        self.chamadas.append("consequencia_mundo")

    def fruta_comida(self, *a, **k) -> None:
        self.chamadas.append("fruta_comida")


def _motor(semente: int, **kw):
    fp, fm = fabricas_mundo(CM, politica_fabrica=lambda cfg=None: Espiao(cfg), cfg_sacudir=CS, **kw)
    return fp, fm, fm(fp(CONFIG_PADRAO), CONFIG_PADRAO, semente)


def _mundo(semente: int = 101, cs: ConfigSacudir = CS) -> Mundo:
    m = Mundo(CM, semente)
    m.ligar_sacudir(cs)
    return m


def _resumo(m) -> str:
    return json.dumps({"log": m.log.para_jsonl(), "estado": m.estado(), "estado_bruto": repr(m._estado),
                       "rng_ambiente": m._rng_ambiente.getstate(), "rng_politica": m._rng_politica.getstate(),
                       "mundo": m.resumo_mundo_fisico()}, sort_keys=True, default=str)


# ------------------------------------------------------------------ o log
def test_o_formato_do_log():
    assert sacudir_arvore(9, "J1") == Evento(9, "sacudir_arvore", "J1")
    assert ler_sacudir_arvore(Evento(0, "sacudir_arvore", "M6")) == "M6"
    for v in ("", " J1", "J1 ", "J-1", "J|1", "J1\n", "á", "A" * 17, 1, None, True):
        with pytest.raises(ValueError, match="sacudir_arvore"):
            sacudir_arvore(9, v)
        if isinstance(v, str):
            with pytest.raises(ValueError):
                ler_sacudir_arvore(Evento(0, "sacudir_arvore", v))
    with pytest.raises(ValueError, match="nao e sacudir_arvore"):
        ler_sacudir_arvore(Evento(0, "deixar_bola", "1|1"))


# ------------------------------------------------------------------ o mundo da ilha
def test_o_mundo_da_ilha():
    assert CM == H.mundo_ilha_de_hoje()
    assert CM.layout.nome == "ilha" and CM.layout.arvores == tuple(a for a in LAYOUT_MUNDO_PADRAO.arvores if a[0] in ("J1", "J2", "J3"))
    assert replace(CM, layout=CONFIG_MUNDO_MVP.layout) == CONFIG_MUNDO_MVP
    assert sorted(a[3] for a in CM.layout.arvores) == list(FRUTAS)          # uma arvore de cada fruta
    assert CONFIG_MUNDO_MVP.layout.arvores == ()                           # o mundo dos pets v12 a v19 nao muda


def test_a_config():
    assert CONFIG_SACUDIR.ligada is False and (CS.galho_max, CS.recarga_galho_min) == (3, 240)
    for kw in ({"ligada": 1}, {"galho_max": 0}, {"galho_max": 2.0}, {"recarga_galho_min": 0}, {"recarga_galho_min": True}):
        with pytest.raises((TypeError, ValueError)):
            replace(CS, **kw)


# ------------------------------------------------------------------ o galho, a queda e o chao (no Mundo)
def test_o_galho_esvazia_e_repoe():
    m = _mundo()
    m.atualizar(100)
    regs = [m.sacudir("J1", 100) for _ in range(4)]
    assert [r["motivo"] for r in regs] == ["caiu", "caiu", "caiu", "galho_vazio"]
    assert [r["no_galho_antes"] for r in regs] == [3, 2, 1, 0]
    assert m.galho_em("J1", 100) == (0, 340)                    # o relogio comecou na primeira fruta, com o galho cheio
    assert m.galho_em("J1", 339) == (0, 340) and m.galho_em("J1", 340) == (1, 580) and m.galho_em("J1", 820) == (3, None)
    assert m.galho_em("J2", 100) == (3, None)                   # as outras arvores nao mudam
    m.atualizar(580)
    r = m.sacudir("J1", 580)                                    # dois repostos; o relogio segue de 580, nao recomeca
    assert (r["no_galho_antes"], r["motivo"]) == (2, "caiu") and m.galho_em("J1", 580) == (1, 820)


def test_onde_a_fruta_cai():
    m = _mundo()
    m.atualizar(30)
    for ident, x, y, fruta in CM.layout.arvores:
        r = m.sacudir(ident, 30)
        c = m.comidas[r["caiu"]]
        arv = next(a for a in m.arvores if a["id"] == ident)
        assert (c["tipo"], c["origem"], c["tick_posta"], c["x"], c["y"]) == (fruta, ident, 30, r["x"], r["y"])
        assert m.situacao(c, 30) == "madura" and distancia(c["x"] - arv["x"], c["y"] - arv["y"]) <= RAIO


def test_o_chao_cheio_e_a_arvore_parada():
    m = _mundo()
    m.atualizar(10)
    for _ in range(3):
        m.sacudir("J2", 10)
    m.atualizar(250)
    assert m.sacudir("J2", 250)["motivo"] == "caiu"            # 4 no chao (o teto de hoje, max_frutas_por_arvore)
    m.atualizar(490)
    estado = m.rng_sacode.getstate()
    r = m.sacudir("J2", 490)
    assert (r["motivo"], r["no_chao_antes"], r["caiu"]) == ("chao_cheio", 4, None)
    assert m.galho_em("J2", 490)[0] == 1 and m.rng_sacode.getstate() == estado     # o galho fica e nada se sorteia
    m.arvores[2]["parada"] = True                              # o J5 (adendo 8): a arvore parada nao da fruta
    assert m.arvores[2]["id"] == "J3" and m.sacudir("J3", 490)["motivo"] == "parada"


def test_a_queda_natural_nao_muda():
    """os sorteios do fluxo `mundo-arvores` sao os mesmos com e sem sacudidas (so as colocadas dependem do chao)"""
    sem, com = _mundo(202), _mundo(202)
    for t in range(0, 6 * 1440, 53):
        sem.atualizar(t)
        com.atualizar(t)
        com.sacudir(("J1", "J2", "J3")[t % 3], t)
    chaves = ("tick", "arvore", "sorteadas", "pontos")
    assert sem.quedas and [{k: q[k] for k in chaves} for q in sem.quedas] == [{k: q[k] for k in chaves} for q in com.quedas]
    assert sem.rng_arvores.getstate() == com.rng_arvores.getstate() and sem.rng_bola.getstate() == com.rng_bola.getstate()


def test_o_mundo_falha_alto():
    m = Mundo(CM, 101)
    m.atualizar(0)
    with pytest.raises(SacudirSemChave):
        m.sacudir("J1", 0)
    with pytest.raises(SacudirSemChave):
        m.ligar_sacudir(CONFIG_SACUDIR)
    m.ligar_sacudir(CS)
    with pytest.raises(RuntimeError, match="ja esta ligado"):
        m.ligar_sacudir(CS)
    with pytest.raises(ValueError, match="nao existe"):
        m.sacudir("M1", 0)
    with pytest.raises(RuntimeError, match="atualizado"):
        m.sacudir("J1", 15)


# ------------------------------------------------------------------ o motor
def test_sem_o_mundo_ou_sem_a_chave_falha_alto():
    with pytest.raises(SacudirSemChave):
        MotorMundo(PoliticaInstinto(CONFIG_PADRAO), CONFIG_PADRAO, 101, cfg_sacudir=CS)
    fp, fm = fabricas_mundo(CM, politica_fabrica=lambda cfg=None: Espiao(cfg))
    m = fm(fp(CONFIG_PADRAO), CONFIG_PADRAO, 101)
    with pytest.raises(SacudirSemChave):
        m.sacudir_arvore("J1")
    with pytest.raises(SacudirSemChave):
        m.no_galho()
    assert len(m.log) == 0
    with pytest.raises(SacudirSemChave, match="fora do grupo"):
        MotorMundo(PoliticaInstinto(CONFIG_PADRAO), CONFIG_PADRAO, 101, cfg_mundo=CM, cfg_sacudir=CS, mundo=Mundo(CM, 101))


def test_a_arvore_que_nao_existe_falha_antes_do_log():
    _, _, m = _motor(101)
    m.avancar(30)
    n, antes = len(m.log), _resumo(m)
    for ident in ("M1", "J4", "j1"):
        with pytest.raises(ValueError, match="nao existe"):
            m.sacudir_arvore(ident)
    with pytest.raises(ValueError, match="sacudir_arvore"):
        m.sacudir_arvore("J 1")
    assert len(m.log) == n and _resumo(m) == antes


@pytest.mark.parametrize("semente", SEMENTES)
def test_nao_e_cuidado(semente):
    _, _, m = _motor(semente)
    m.avancar(200)
    estado, n, chamadas, n_eventos = m._estado, len(m.log), list(m.politica.chamadas), m._n_eventos
    decisoes, pet = len(m.decisoes_mundo), m.pet
    m.sacudir_arvore("J3")
    assert [e.para_dict() for e in list(m.log)[n:]] == [sacudir_arvore(estado.tick, "J3").para_dict()]
    assert m._estado == estado and m.pet == pet                  # o estado e a posicao do pet nao mudam
    assert m.politica.chamadas == chamadas                       # nenhum gancho do cerebro
    assert len(m.decisoes_mundo) == decisoes and m._n_eventos == n_eventos + 1
    assert m.mundo.sacudidas[-1]["motivo"] == "caiu" and m.estado()["sacudir"] == {"no_galho": {"J1": 3, "J2": 3, "J3": 2},
                                                                                   "sacudidas": 1}


def test_vale_com_o_pet_dormindo():
    _, _, m = _motor(101)
    m.avancar(30)
    m._estado = replace(m._estado, dormindo=True)
    m.sacudir_arvore("J1")
    assert m.mundo.sacudidas[-1]["motivo"] == "caiu"


@pytest.mark.parametrize("semente", SEMENTES)
def test_o_replay_refaz_a_vida(semente):
    fp, fm, m = _motor(semente)
    for i in range(40):
        for _ in range(1 + i % 4):
            m.sacudir_arvore(("J1", "J2", "J3")[i % 3])
        m.avancar(61)
    assert {s["motivo"] for s in m.mundo.sacudidas} >= {"caiu", "galho_vazio"}
    r = reproduzir_mundo(m.log, fp, CONFIG_PADRAO, semente, fabrica_motor=fm)
    assert _resumo(r) == _resumo(m)


def test_desligada_nenhuma_chave_nova():
    fp, fm = fabricas_mundo(CM, politica_fabrica=lambda cfg=None: Espiao(cfg))
    m = fm(fp(CONFIG_PADRAO), CONFIG_PADRAO, 101)
    m.avancar(200)
    assert not {"galhos", "sacudidas", "rng_sacode"} & set(m.resumo_mundo_fisico()) and "sacudir" not in m.estado()
    assert m.mundo.galhos is None and not {"galhos", "sacudidas"} & set(m.mundo.resumo())


# ------------------------------------------------------------------ a fruta do mundo como comida (AS-11)
def test_a_fruta_como_comida_nao_entrega_o_aviso():
    for cfc, esperado in ((None, True), (CONFIG_FRUTA_COMO_COMIDA_LIGADA, False)):
        kw = {} if cfc is None else {"cfg_fruta_comida": cfc}
        _, _, m = _motor(101, **kw)
        for i in range(60):
            m.sacudir_arvore(("J1", "J2", "J3")[i % 3])
            m.avancar(60)
        assert any(c["tipo"] in FRUTAS for c in m.consumos_mundo)
        assert ("fruta_comida" in m.politica.chamadas) is esperado


@pytest.mark.parametrize("semente", (202, 404, 505))
def test_o_a_do_v11_come_a_fruta_sem_quebrar(semente):
    """as tres vidas que quebram hoje no mundo da ilha (o gabarito de hoje) passam com a fruta como comida"""
    assert "erro" in json.loads(H.ARQUIVO.read_text(encoding="utf-8"))[f"ilha|a_v11|aleatorio|perto|{semente}"]
    b = e0._bancada()
    espec = bv.EspecVida("aleatorio", e0.gl.BRACO_V11, semente)
    cc = b.cfg_corpo_de(espec)
    fm = (lambda p, cfg, s: e0.MotorMundoCorpoGravado(p, cfg, s, obediencia_desligada=True, cfg_mundo=CM, cfg_corpo=cc,  # noqa: E731
                                                      cfg_fruta_comida=CONFIG_FRUTA_COMO_COMIDA_LIGADA))
    d = e0.DonoComLugar(e0.criar_dono("aleatorio"), "perto", semente, "aleatorio", CM)
    m = e0.simular_vida_mundo("aleatorio", d, b.politica(espec, CONFIG_PADRAO), semente, e0.DIAS, 16 * e0.DIAS, fm,
                              rotulo_dono="aleatorio").motor
    assert any(c["tipo"] in FRUTAS for c in m.consumos_mundo)
    # como a racao (AS-11, opcao 1): sem a E2 (nenhuma consequencia de fruta, o humor fora dos drives do sinal do corpo)
    pm = m.politica
    assert pm._n_recompensas.get("consequencia_fruta", 0) == 0
    sinais = [mt["sinal_corpo"] for mt in pm.motivos if "sinal_corpo" in mt]
    assert sinais and not any("humor" in s["drives"] for s in sinais)


# ------------------------------------------------------------------ o gabarito do G-PAR do TS
def test_o_gabarito_esta_em_dia_byte_a_byte():
    assert TEXTO == json.dumps(G.gerar(), sort_keys=True, separators=(",", ":")) + "\n"
    assert all(v["semente"] in bv.SEMENTES_TESTE for v in GRAVADO["vidas"])
    for v in GRAVADO["vidas"]:
        sac = v["resumo"]["sacudidas"]
        assert len(sac) == v["sacudidas"] and {s["motivo"] for s in sac} >= set(G.MOTIVOS) and v["dormindo_em"]
        assert v["frutas_comidas"] >= 1 and all(e["tipo"] in ("avanco", "deixar_comida", "sacudir_arvore") for e in v["log"])
