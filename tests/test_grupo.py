"""O grupo: N pets de verdade no mesmo mundo fisico (docs/TAREFA_V2_DOIS_PETS.md, etapa 2; docs/futuro/dois_pets.md, secoes 2 a 4).

- G2: um pet no grupo e a vida de hoje byte a byte. As 48 vidas diretas do gabarito da etapa 0 (o corpo inteiro da etapa 6 incluido), e o
  `simular_vida_mundo` de hoje com os quatro donos, os tres lugares, os dois cerebros e o canal dos gestos; a projecao do registro e o log
  do motor; o grupo desligado recusa.
- G1-GRUPO: o replay do texto do registro refaz o grupo bit a bit (os pets, o mundo, as vezes sorteadas e as rngs), com a entrada tardia e o
  corpo; e falha alto com o registro errado.
- G-ORDEM: a ordem da lista dos pets e a ordem de entrada no codigo nao mudam nada; o sorteio e o `random.shuffle` do CPython no fluxo
  `mundo-ordem`, so nos ticks com dois pets decidindo.
- G-NUMS-GRUPO: um B passivo deixa o A igual ao A sozinho; com um B que age, as quedas e as vezes sorteadas sao as mesmas com qualquer
  cerebro do B, e o rastro do A e o do A sozinho ate o primeiro evento fisico do B.
- A entrada tardia (o A vive K dias antes do B; o mundo passa dias sem pet) e a guarda da MRO do `_avancar`.
Sementes: so as dos testes (101, 202).
"""
from __future__ import annotations

import json
import random
import sys
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import gabarito_dois_pets as gdp  # noqa: E402
from digilab.config import (CONFIG_CORPO_DRIVES, CONFIG_GRUPO, CONFIG_GRUPO_LIGADA, CONFIG_MUNDO, CONFIG_PADRAO, TICKS_POR_DIA,  # noqa: E402
                            ConfigGrupo)
from digilab.donos import criar_dono  # noqa: E402
from digilab.engine import Motor  # noqa: E402
from digilab.events import AcaoPet, AcaoUsuario  # noqa: E402
from digilab.gestos import CanalMundoComGestos, DonoComGestos  # noqa: E402
from digilab.grupo import (Grupo, GrupoSemChave, PetDoGrupo, RegistroDivergente, RegistroGrupo, reproduzir_grupo,  # noqa: E402
                           sementes_do_grupo, simular_grupo)
from digilab.instinto_mundo import PoliticaInstintoMundo  # noqa: E402
from digilab.config import CONFIG_LOBOS_APRENDIZ  # noqa: E402
from digilab.policies.lobos import PoliticaLobos  # noqa: E402
from digilab.motor_corpo import MotorCorpo, com_corpo  # noqa: E402
from digilab.mundo import DonoComLugar, MotorMundo, Mundo, simular_vida_mundo  # noqa: E402
from digilab.protocol import ENGINE_SHA256_V0, derivar_semente, sha256_engine  # noqa: E402

CM = gdp.LAYOUTS["padrao"]
DIAS = gdp.DIAS
DONOS = ("atencioso", "relapso", "aleatorio", "incoerente")


def _texto(obj) -> str:
    return json.dumps(obj, sort_keys=True, default=repr)


def fabricas(cerebro: str = "lobos", corpo: str = "sem", layout: str = "padrao", corpo_no_cerebro: bool = True):
    """as fabricas da etapa 0 (tests/gabarito_dois_pets.py), com o motor aceitando o `mundo` e a `entrada_mundo` do grupo. Com
    `corpo_no_cerebro`, os lobos num corpo ligado recebem a chave do corpo (o carinho chega pelo `mudanca_no_corpo`); sem ela, as
    fabricas do gabarito como estao"""
    fp, _ = gdp.fabricas_diretas(layout, corpo, cerebro)
    cm, cc = gdp.LAYOUTS[layout], gdp.CORPOS[corpo]
    if corpo_no_cerebro and cerebro == "lobos" and cc is not None:
        fp = lambda cfg=None: PoliticaLobos(cfg or CONFIG_PADRAO, CONFIG_LOBOS_APRENDIZ, cfg_mundo=cm, cfg_corpo=cc)  # noqa: E731
    if cc is None:
        fm = lambda p, cfg, s, **kw: MotorMundo(p, cfg, s, obediencia_desligada=True, cfg_mundo=cm, **kw)  # noqa: E731
    else:
        fm = lambda p, cfg, s, **kw: gdp.MotorMundoCorpo(p, cfg, s, obediencia_desligada=True, cfg_mundo=cm,  # noqa: E731
                                                          cfg_corpo=cc, **kw)
    return fp, fm


class Passivo(PoliticaInstintoMundo):
    """um parceiro que nao mexe no mundo: so fica ocioso ou dorme (nunca anda, come nem brinca)"""

    def agir(self, obs, rng):
        a = super().agir(obs, rng)
        return a if a is AcaoPet.DORMIR else AcaoPet.OCIOSO


def fp_passivo(cfg=None):
    return Passivo(cfg or CONFIG_PADRAO)


def pet(ident: str, entrada: int, semente_grupo: int, cerebro: str = "lobos", corpo: str = "sem", dono: str | None = "atencioso",
        lugar: str = "perto", layout: str = "padrao") -> PetDoGrupo:
    fp, fm = fabricas("lobos" if cerebro == "passivo" else cerebro, corpo, layout)
    if cerebro == "passivo":
        fp = fp_passivo
    d = None
    if dono is not None:
        s = sementes_do_grupo(semente_grupo, CONFIG_GRUPO_LIGADA.ids)[ident]
        d = DonoComLugar(criar_dono(dono), lugar, s, dono, gdp.LAYOUTS[layout])
    return PetDoGrupo(ident, entrada, fp, fm, d, dono or "", cerebro)


def _resumo(g: Grupo) -> str:
    return _texto(g.resumo())


# ================================================================== G2: um pet no grupo
def test_g2_um_pet_no_grupo_e_o_gabarito_da_etapa_0():
    """as 48 vidas diretas de tests/gabaritos/dois_pets_vidas_de_hoje.json, pelo simular_grupo com um pet: o log, o estado, o estado() (com
    o corpo), as acoes, as rngs, a politica, o resumo do mundo fisico inteiro e o registro da novidade"""
    gravado = json.loads(gdp.ARQUIVO.read_text(encoding="utf-8"))
    vistos, difs = 0, []
    for chave, (layout, corpo, cerebro, lugar, s) in gdp.casos_diretos():
        fp, fm = fabricas(cerebro, corpo, layout, corpo_no_cerebro=False)
        dono = gdp.DonoComBolaPerto(DonoComLugar(criar_dono("atencioso"), lugar, s, "atencioso", gdp.LAYOUTS[layout]))
        g = simular_grupo(gdp.LAYOUTS[layout], s, [PetDoGrupo("A", 0, fp, fm, dono, "atencioso", cerebro)], DIAS)
        vistos += 1
        if gdp.impressao(g.motores["A"], g.interacoes["A"]) != gravado[chave]:
            difs.append(chave)
        assert g._rng_ordem is None and g.ordens == []          # um pet: nao ha sorteio, e o fluxo nem e criado
    assert vistos == 48 and difs == []


@pytest.mark.parametrize("cerebro", ["instinto", "lobos"])
@pytest.mark.parametrize("dono", DONOS)
def test_g2_um_pet_e_o_simular_vida_mundo_de_hoje(dono, cerebro):
    """os quatro donos, os tres lugares e as duas sementes: a vida do pet A sozinho no grupo e a do simular_vida_mundo, byte a byte"""
    for lugar in ("comedouro", "perto", "longe"):
        for s in (101, 202):
            fp, fm = fabricas(cerebro)
            fm_hoje = lambda p, cfg, s_: MotorMundo(p, cfg, s_, obediencia_desligada=True, cfg_mundo=CM)  # noqa: E731
            v = simular_vida_mundo(dono, DonoComLugar(criar_dono(dono), lugar, s, dono, CM), fp(CONFIG_PADRAO), s, DIAS, 16 * DIAS,
                                   fm_hoje, rotulo_dono=dono)
            g = simular_grupo(CM, s, [PetDoGrupo("A", 0, fp, fm, DonoComLugar(criar_dono(dono), lugar, s, dono, CM), dono, cerebro)],
                              DIAS)
            assert gdp.impressao(g.motores["A"], g.interacoes["A"]) == gdp.impressao(v.motor, v.interacoes), (dono, lugar, s)


def test_g2_um_pet_com_o_corpo_inteiro_e_os_gestos():
    """o canal dos gestos (o carinho e o tapa no corpo da etapa 6, com o dono aleatorio, que da os dois) passa pela porta do grupo do mesmo jeito"""
    for modo in ("tapa", "sem_tapa"):
        fp, fm = fabricas("lobos", "drives")
        fm_hoje = lambda p, cfg, s_: gdp.MotorMundoCorpo(p, cfg, s_, obediencia_desligada=True, cfg_mundo=CM,  # noqa: E731
                                                         cfg_corpo=CONFIG_CORPO_DRIVES)
        d = lambda: DonoComGestos(DonoComLugar(criar_dono("aleatorio"), "perto", 101, "aleatorio", CM), modo)  # noqa: E731
        v = simular_vida_mundo("aleatorio", d(), fp(CONFIG_PADRAO), 101, DIAS, 16 * DIAS, fm_hoje, rotulo_dono="aleatorio",
                               canal_classe=CanalMundoComGestos)
        g = simular_grupo(CM, 101, [PetDoGrupo("A", 0, fp, fm, d(), "aleatorio", "lobos")], DIAS, canal_classe=CanalMundoComGestos)
        assert gdp.impressao(g.motores["A"], g.interacoes["A"]) == gdp.impressao(v.motor, v.interacoes), modo
        if modo == "tapa":
            assert any(e.valor == AcaoUsuario.TAPA.value for e in g.registro.eventos)
        assert any(e.valor == AcaoUsuario.ACARICIAR.value for e in g.registro.eventos)


def test_g_engine():
    assert sha256_engine() == ENGINE_SHA256_V0


def test_o_grupo_desligado_recusa():
    with pytest.raises(GrupoSemChave):
        Grupo(CM, 101, CONFIG_GRUPO)
    with pytest.raises(GrupoSemChave):
        simular_grupo(CM, 101, [pet("A", 0, 101)], DIAS, cfg_grupo=CONFIG_GRUPO)


def test_o_motor_so_aceita_o_mundo_do_grupo_com_o_mundo_ligado():
    fp, _ = fabricas()
    m = Mundo(CM, 101)
    with pytest.raises(ValueError):
        MotorMundo(fp(), CONFIG_PADRAO, 101, obediencia_desligada=True, cfg_mundo=CONFIG_MUNDO, mundo=m)
    with pytest.raises(ValueError):                                                  # a entrada sem o mundo do grupo
        MotorMundo(fp(), CONFIG_PADRAO, 101, obediencia_desligada=True, cfg_mundo=CM, entrada_mundo=TICKS_POR_DIA)
    with pytest.raises(ValueError):                                                  # fora de um inicio de dia
        MotorMundo(fp(), CONFIG_PADRAO, 101, obediencia_desligada=True, cfg_mundo=CM, mundo=m, entrada_mundo=15)
    with pytest.raises(ValueError):                                                  # outro mundo
        MotorMundo(fp(), CONFIG_PADRAO, 101, obediencia_desligada=True, cfg_mundo=CM, mundo=Mundo(gdp.LAYOUTS["afastado"], 101))
    mm = MotorMundo(fp(), CONFIG_PADRAO, 101, obediencia_desligada=True, cfg_mundo=CM, mundo=m, entrada_mundo=TICKS_POR_DIA)
    assert mm.mundo is m and mm.entrada_mundo == TICKS_POR_DIA


# ================================================================== as sementes e a configuracao
def test_as_sementes_do_grupo():
    assert sementes_do_grupo(101, ("A", "B")) == {"A": 101, "B": derivar_semente("segundo-pet", 101)}
    g = simular_grupo(CM, 202, [pet("A", 0, 202), pet("B", 0, 202)], 1)
    assert g.mundo.semente == 202 and g.motores["A"].semente == 202
    assert g.motores["B"].semente == derivar_semente("segundo-pet", 202)
    assert g.registro.cabecalho["pets"]["B"] == {"semente": derivar_semente("segundo-pet", 202), "entrada": 0, "cerebro": "lobos",
                                                 "dono": "atencioso"}
    assert g.mundo.rng_arvores is not None and all(m.mundo is g.mundo for m in g.motores.values())


def test_config_grupo_valida():
    for ruim in ({"ids": ()}, {"ids": ("A", "A")}, {"ids": ("B", "A")}, {"ids": ("A", "")}, {"ids": ("A", "B", "C")},
                 {"orcamento_por_dia": 0}, {"orcamento_por_dia": 1.5}):
        with pytest.raises(ValueError):
            ConfigGrupo(ligada=True, **ruim)
    assert CONFIG_GRUPO_LIGADA.ids == ("A", "B") and CONFIG_GRUPO_LIGADA.orcamento_por_dia == 16 and not CONFIG_GRUPO.ligada


def test_a_entrada_falha_alto():
    fp, fm = fabricas()
    g = Grupo(CM, 101)
    with pytest.raises(ValueError, match="fora do grupo"):
        g.entrar("C", fp(), fm, "lobos", "")
    g.entrar("A", fp(), fm, "lobos", "")
    with pytest.raises(ValueError, match="ja entrou"):
        g.entrar("A", fp(), fm, "lobos", "")
    g.avancar(15)
    with pytest.raises(ValueError, match="inicio de dia"):
        g.entrar("B", fp(), fm, "lobos", "")
    g.avancar(TICKS_POR_DIA - 15)
    proprio = lambda p, cfg, s, **kw: MotorMundo(p, cfg, s, obediencia_desligada=True, cfg_mundo=CM)  # noqa: E731
    with pytest.raises(ValueError, match="mundo do grupo"):                            # a fabrica que ignora o mundo do grupo
        g.entrar("B", fp(), proprio, "lobos", "")
    outro_efeito = lambda p, cfg, s, **kw: MotorMundo(p, cfg, s, obediencia_desligada=True, cfg_mundo=CM,  # noqa: E731
                                                      efeito_frutas={"a": 0.1, "b": 0.0, "c": 0.0}, **kw)
    with pytest.raises(ValueError, match="efeito_frutas"):
        g.entrar("B", fp(), outro_efeito, "lobos", "")
    with pytest.raises(KeyError):
        g.pet("B")
    with pytest.raises(ValueError, match="fora da vida"):
        simular_grupo(CM, 101, [pet("A", DIAS * TICKS_POR_DIA, 101)], DIAS)
    with pytest.raises(ValueError, match="repetido"):
        simular_grupo(CM, 101, [pet("A", 0, 101), pet("A", 0, 101)], DIAS)


# ================================================================== G1-GRUPO
CENARIOS = [  # (entrada do B, corpo, cerebro do A, cerebro do B, layout)
    (0, "sem", "lobos", "lobos", "padrao"),
    (TICKS_POR_DIA, "drives", "instinto", "lobos", "padrao"),
    (2 * TICKS_POR_DIA, "quimica", "lobos", "instinto", "afastado"),
]


@pytest.mark.parametrize("entrada_b,corpo,ca,cb,layout", CENARIOS)
def test_g1_grupo_o_replay_do_texto_refaz_o_grupo(entrada_b, corpo, ca, cb, layout):
    g = simular_grupo(gdp.LAYOUTS[layout], 101, [pet("A", 0, 101, ca, corpo, layout=layout),
                                                 pet("B", entrada_b, 101, cb, corpo, "aleatorio", "longe", layout)], DIAS)
    texto = g.registro.para_jsonl()
    lido = RegistroGrupo.de_jsonl(texto)
    assert lido.para_jsonl() == texto
    r = reproduzir_grupo(lido, {"A": fabricas(ca, corpo, layout), "B": fabricas(cb, corpo, layout)}, gdp.LAYOUTS[layout])
    assert _resumo(r) == _resumo(g)
    assert r.registro.para_jsonl() == texto
    for i in ("A", "B"):
        assert gdp.impressao(r.motores[i]) == gdp.impressao(g.motores[i])
        # a projecao do registro e o log de hoje do pet, no relogio dele
        assert lido.projecao(i).para_jsonl() == g.motores[i].log.para_jsonl()
    assert g.ordens and g.motores["B"].consumos_mundo                  # o B agiu de verdade e as vezes foram sorteadas


def test_g1_o_registro_tem_cabecalho_destino_e_origem():
    g = simular_grupo(CM, 101, [pet("A", 0, 101), pet("B", TICKS_POR_DIA, 101)], 2)
    cab = g.registro.cabecalho
    assert cab["versao"] == 1 and cab["semente"] == 101 and cab["ids"] == ["A", "B"] and cab["layout"] == CM.layout.nome
    assert cab["pets"]["B"]["entrada"] == TICKS_POR_DIA
    tipos = {(e.tipo, e.destino, e.origem) for e in g.registro.eventos}
    assert ("entrada", "grupo", None) in tipos and ("avanco", "grupo", None) in tipos
    assert ("deixar_comida", "mundo", "dono") in tipos                  # o dono perto deixa a comida no mapa
    assert all(e.destino == f"pet:{e.pet}" for e in g.registro.eventos if e.tipo == "acao_usuario")
    assert all(e.pet in ("A", "B") and e.origem == "dono" for e in g.registro.eventos if e.tipo not in ("entrada", "avanco"))
    # um avanco so, do grupo: um por passo do dono, com os dois pets ou sem nenhum
    assert sum(e.tipo == "avanco" for e in g.registro.eventos) == 2 * TICKS_POR_DIA // 15
    # nada do que os pets fazem entra no registro (sai do replay)
    assert {e.tipo for e in g.registro.eventos} <= {"entrada", "avanco", "acao_usuario", "deixar_comida", "deixar_bola"}


def _registro_curto() -> RegistroGrupo:
    g = simular_grupo(CM, 101, [pet("A", 0, 101), pet("B", 0, 101)], 1)
    return RegistroGrupo.de_jsonl(g.registro.para_jsonl())


def _troca(reg: RegistroGrupo, k: int, **mudar) -> RegistroGrupo:
    eventos = list(reg.eventos)
    eventos[k] = replace(eventos[k], **mudar)
    return RegistroGrupo(json.loads(json.dumps(reg.cabecalho)), eventos)


def test_g1_o_replay_falha_alto():
    reg = _registro_curto()
    fab = {"A": fabricas(), "B": fabricas()}
    k_acao = next(k for k, e in enumerate(reg.eventos) if e.tipo == "acao_usuario")
    k_avanco = next(k for k, e in enumerate(reg.eventos) if e.tipo == "avanco")
    with pytest.raises(RegistroDivergente):                    # o destino gravado nao e o que o grupo grava
        reproduzir_grupo(_troca(reg, k_acao, destino="mundo"), fab, CM)
    with pytest.raises(ValueError, match="desconhecido"):
        reproduzir_grupo(_troca(reg, k_acao, tipo="pular"), fab, CM)
    with pytest.raises(ValueError, match="no tick"):           # um avanco maior empurra os eventos seguintes para fora do tick
        reproduzir_grupo(_troca(reg, k_avanco, valor=30), fab, CM)
    with pytest.raises(KeyError):                              # o pet do evento nao entrou
        reproduzir_grupo(_troca(reg, k_acao, pet="C", destino="pet:C"), fab, CM)
    with pytest.raises(ValueError, match="fabricas"):
        reproduzir_grupo(reg, {"A": fabricas()}, CM)
    with pytest.raises(ValueError, match="cabecalho"):
        reproduzir_grupo(reg, fab, gdp.LAYOUTS["afastado"])
    ruim = RegistroGrupo(dict(reg.cabecalho, versao=99), reg.eventos)
    with pytest.raises(ValueError, match="versao"):
        reproduzir_grupo(ruim, fab, CM)
    with pytest.raises(ValueError):
        RegistroGrupo.de_jsonl('{"tick": 0}\n')
    linhas = reg.para_jsonl().splitlines()
    with pytest.raises(ValueError, match="campos"):
        RegistroGrupo.de_jsonl("\n".join([linhas[0], json.dumps({"tick": 0, "tipo": "avanco", "valor": 15})]))


# ================================================================== G-ORDEM
def test_g_ordem_a_lista_dos_pets_nao_importa():
    def pets():   # novos a cada grupo: o dono com lugar tem rng propria (`dono-lugar`)
        return [pet("A", 0, 202, "lobos", lugar="perto"), pet("B", TICKS_POR_DIA, 202, "instinto", dono="relapso", lugar="comedouro")]
    g1 = simular_grupo(CM, 202, pets(), DIAS)
    g2 = simular_grupo(CM, 202, list(reversed(pets())), DIAS)
    assert g1.registro.para_jsonl() == g2.registro.para_jsonl() and _resumo(g1) == _resumo(g2)


def test_g_ordem_a_ordem_de_entrada_no_codigo_nao_importa():
    """os dois pets entram no tick 0 em ordens diferentes no codigo: o grupo e o mesmo (o registro guarda a ordem das chamadas, so)"""
    def grupo(ordem):
        g = Grupo(CM, 101)
        for i in ordem:
            fp, fm = fabricas("lobos" if i == "A" else "instinto")
            g.entrar(i, fp(), fm, "", "")
        for _ in range(DIAS * TICKS_POR_DIA // 15):
            g.avancar(15)
        return g
    g1, g2 = grupo(("A", "B")), grupo(("B", "A"))
    assert _resumo(g1) == _resumo(g2) and g1.ordens
    assert g1.registro.para_jsonl() != g2.registro.para_jsonl()       # so a ordem das duas entradas no tick 0
    assert sorted(g1.registro.para_jsonl().splitlines()) == sorted(g2.registro.para_jsonl().splitlines())


def test_g_ordem_o_sorteio_e_o_shuffle_do_cpython():
    g = Grupo(CM, 303)
    ref = random.Random(derivar_semente("mundo-ordem", 303))
    for _ in range(500):
        esperado = ["A", "B"]
        ref.shuffle(esperado)
        assert g._sortear(["A", "B"]) == esperado
    primeiros = [o["ordem"][0] for o in g.ordens]
    assert 200 < primeiros.count("A") < 300                            # as duas ordens aparecem


def test_g_ordem_um_sorteio_so_nos_ticks_com_dois_pets_decidindo():
    g = simular_grupo(CM, 101, [pet("A", 0, 101), pet("B", TICKS_POR_DIA, 101)], DIAS)
    ticks = [o["tick"] for o in g.ordens]
    assert ticks == list(range(TICKS_POR_DIA, DIAS * TICKS_POR_DIA, 15))     # o B decide de 15 em 15 desde que entrou, junto com o A
    assert all(o["decidem"] == ["A", "B"] and sorted(o["ordem"]) == ["A", "B"] for o in g.ordens)
    assert {tuple(o["ordem"]) for o in g.ordens} == {("A", "B"), ("B", "A")}
    so_a = simular_grupo(CM, 101, [pet("A", 0, 101)], DIAS)
    assert so_a.ordens == [] and so_a._rng_ordem is None


# ================================================================== G-NUMS-GRUPO
def _sorteios(quedas):
    return [(q["tick"], q["arvore"], q["sorteadas"], q["pontos"]) for q in quedas]


@pytest.mark.parametrize("entrada_b", [0, TICKS_POR_DIA])
@pytest.mark.parametrize("cerebro_a", ["instinto", "lobos"])
def test_g_nums_um_b_passivo_deixa_o_a_igual_ao_a_sozinho(entrada_b, cerebro_a):
    for s in (101, 202):
        so_a = simular_grupo(CM, s, [pet("A", 0, s, cerebro_a)], DIAS)
        com_b = simular_grupo(CM, s, [pet("A", 0, s, cerebro_a), pet("B", entrada_b, s, "passivo", dono=None)], DIAS)
        assert gdp.impressao(com_b.motores["A"], com_b.interacoes["A"]) == gdp.impressao(so_a.motores["A"], so_a.interacoes["A"])
        assert _texto(com_b.mundo.resumo()) == _texto(so_a.mundo.resumo())
        mb = com_b.motores["B"]
        assert com_b.ordens and not mb.consumos_mundo and {a for _, a in mb.acoes_recentes(10 ** 9)} <= {AcaoPet.OCIOSO, AcaoPet.DORMIR}


def _primeiro_evento_fisico(g: Grupo, ident: str) -> int:
    """o primeiro tick (do mundo) em que o pet muda o mundo que o outro percebe: come, brinca com a bola, ou o dono dele deixa algo"""
    m = g.motores[ident]
    ticks = [c["tick"] for c in m.consumos_mundo]
    ticks += [d["tick"] for d in m.decisoes_mundo if d["brincou_com_bola"]]
    ticks += [e.tick for e in g.registro.eventos if e.pet == ident and e.destino == "mundo"]
    return min(ticks)


def _rastro(m: MotorMundo, ate: int) -> list:
    return ([d for d in m.decisoes_mundo if d["tick"] < ate], [c for c in m.consumos_mundo if c["tick"] < ate],
            [r for r in m.regioes if r["tick"] < ate])


@pytest.mark.parametrize("s", [101, 202])
def test_g_nums_um_b_que_age_as_quedas_e_as_vezes_nao_dependem_do_cerebro_do_b(s):
    so_a = simular_grupo(CM, s, [pet("A", 0, s)], DIAS)
    grupos = {cb: simular_grupo(CM, s, [pet("A", 0, s), pet("B", 0, s, cb, dono="atencioso" if cb != "passivo" else None)], DIAS)
              for cb in ("instinto", "lobos", "passivo")}
    for cb, g in grupos.items():
        assert _sorteios(g.mundo.quedas) == _sorteios(so_a.mundo.quedas), cb
        assert [(o["tick"], o["ordem"]) for o in g.ordens] == [(o["tick"], o["ordem"]) for o in grupos["lobos"].ordens], cb
    divergiu = False
    for cb in ("instinto", "lobos"):
        g = grupos[cb]
        t_b = _primeiro_evento_fisico(g, "B")
        assert 0 <= t_b < DIAS * TICKS_POR_DIA
        assert _rastro(g.motores["A"], t_b) == _rastro(so_a.motores["A"], t_b), cb
        divergiu |= _rastro(g.motores["A"], DIAS * TICKS_POR_DIA) != _rastro(so_a.motores["A"], DIAS * TICKS_POR_DIA)
    assert divergiu                                                    # o B que age muda a vida do A depois do primeiro evento dele


# ================================================================== a entrada depois do tick 0
@pytest.mark.parametrize("corpo", ["sem", "drives"])
def test_o_a_vive_k_dias_antes_do_b(corpo):
    k = TICKS_POR_DIA
    g = simular_grupo(CM, 202, [pet("A", 0, 202, corpo=corpo), pet("B", k, 202, corpo=corpo)], DIAS)
    ma, mb = g.motores["A"], g.motores["B"]
    assert g.tick == DIAS * TICKS_POR_DIA and ma._estado.tick == g.tick and mb._estado.tick == g.tick - k
    assert mb.entrada_mundo == k and mb._estado.tick_do_dia == g.tick % TICKS_POR_DIA      # a mesma hora do dia
    # o relogio do B (o log, o Estado) comeca em 0; os registros do mundo fisico dele estao no relogio do mundo
    assert mb.log[0].tipo == "avanco" and mb.log[0].tick == 0
    assert min(d["tick"] for d in mb.decisoes_mundo) == k and all(c["tick"] >= k for c in mb.consumos_mundo)
    assert all(d["tick"] >= k for d in mb.deixadas)
    assert all(e.tick >= k for e in g.registro.eventos if e.pet == "B") and any(e.pet == "B" for e in g.registro.eventos)
    assert g.interacoes == {"A": 16 * DIAS, "B": 16 * (DIAS - 1)}           # o orcamento por dia vivido
    assert g.registro.projecao("B").para_jsonl() == mb.log.para_jsonl()


def test_o_mundo_passa_dias_sem_pet():
    """'B so' (secao 11 do plano): o B entra no dia K sem o A; o mundo andou K dias sem pet, com as mesmas quedas do grupo com o A"""
    k = 2 * TICKS_POR_DIA
    so_b = simular_grupo(CM, 101, [pet("B", k, 101)], DIAS + 1)
    a_e_b = simular_grupo(CM, 101, [pet("A", 0, 101), pet("B", k, 101)], DIAS + 1)
    ingenuo = simular_grupo(CM, 101, [pet("A", k, 101), pet("B", k, 101)], DIAS + 1)          # "B + Aing": entram juntos no dia K
    assert _sorteios(so_b.mundo.quedas) == _sorteios(a_e_b.mundo.quedas) == _sorteios(ingenuo.mundo.quedas)
    assert so_b.mundo.quedas[0]["tick"] < k                            # as arvores sorteiam os dias sem pet
    assert so_b.motores["B"]._estado.tick == (DIAS + 1) * TICKS_POR_DIA - k and so_b.ordens == []
    assert [o["tick"] for o in ingenuo.ordens][0] == k
    assert sum(e.tipo == "avanco" for e in so_b.registro.eventos) == (DIAS + 1) * TICKS_POR_DIA // 15
    assert so_b.registro.projecao("B").para_jsonl() == so_b.motores["B"].log.para_jsonl()
    r = reproduzir_grupo(RegistroGrupo.de_jsonl(so_b.registro.para_jsonl()), {"B": fabricas()}, CM)
    assert _resumo(r) == _resumo(so_b)


# ================================================================== a guarda do laco partido
def test_a_mro_do_avancar_e_a_que_o_grupo_parte():
    """o grupo troca o `_avancar(n)` por `_abrir_avanco`, `_um_tick` n vezes e `_fechar_avanco` (digilab/mundo.py). Se outra classe da
    cadeia ganhar um `_avancar`, as tres partes precisam ser revistas: este teste falha antes."""
    def com(nome, cls):
        return {c for c in cls.__mro__ if nome in vars(c)}
    from digilab.educacao import MotorEducacao
    from digilab.obediencia import MotorPersonalidade
    corpo = com_corpo(MotorMundo)
    assert com("_avancar", MotorMundo) == {MotorEducacao, MotorPersonalidade, Motor}
    assert com("_avancar", corpo) == {MotorCorpo, MotorEducacao, MotorPersonalidade, Motor}
    assert com("_um_tick", MotorMundo) == {MotorMundo} and com("_um_tick", corpo) == {MotorCorpo, MotorMundo}
    assert com("_abrir_avanco", corpo) == com("_fechar_avanco", corpo) == {MotorMundo}
