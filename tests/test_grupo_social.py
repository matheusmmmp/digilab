"""Os sentidos sobre o outro: visao, toque e disputa (docs/TAREFA_V2_DOIS_PETS.md, etapa 3; docs/futuro/dois_pets.md, secoes 3, 5 e 6).

- G-RECEPTOR-SOCIAL: nenhum cerebro importa o grupo nem os motores; a `PercepcaoSocial` nao tem campo de estado interno; mudar o estado
  interno do outro sem mudar o que ele faz e onde esta nao muda nada do que se percebe dele.
- G-SENTIDOS (visao e toque): o toque nos casos da secao 5.2 (disputa, encostar, esbarrar, nenhum contato a duas celulas) e a direcao; a
  visao so no raio, em ordem, com a acao visivel; o consumo visto so dentro do raio, no momento.
- G-MEC-SOCIAL: a disputa (o primeiro na vez come, o segundo nao acha); o `onde_comeu` so depois de um consumo visto; os candidatos
  sociais so no explorar, com o outro visto; o padrao do motor nunca os escolhe; os registros (idas, tempo a vista).
- G2: sem o grupo, ou com um pet so nele, nenhuma percepcao social e nenhum candidato a mais (o resto do G2 esta em tests/test_grupo.py).
- G1-GRUPO com os sentidos e os cerebros que escolhem os alvos sociais; no prior, o P0 com lobos e o instinto do mundo, com o outro a vista.
Sementes: so as dos testes (101, 202, 303, 404).
"""
from __future__ import annotations

import ast
import json
import sys
from dataclasses import fields, replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "tests"))
sys.path.insert(0, str(RAIZ / "experiments"))

import gabarito_dois_pets as gdp  # noqa: E402
from test_grupo import CM, DIAS, fabricas, pet  # noqa: E402
from digilab.config import CONFIG_LOBOS, CONFIG_LOBOS_APRENDIZ, CONFIG_PADRAO, TICKS_POR_DIA, ConfigGrupo  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.events import AcaoPet  # noqa: E402
from digilab.grupo import Grupo, PetDoGrupo, RegistroGrupo, reproduzir_grupo, sementes_do_grupo, simular_grupo  # noqa: E402
from digilab.instinto_mundo import PoliticaInstintoMundo  # noqa: E402
from digilab.mundo import (TIPOS_TOQUE, Alvo, DonoComLugar, MotorMundo, PercepcaoMundo, PercepcaoSocial, alvo_padrao_de,  # noqa: E402
                           celula_de, direcao_vizinha, distancia, em_contato, perceber_social, simular_vida_mundo,
                           tipos_do_contato)
from digilab.policies.lobos import PoliticaLobos  # noqa: E402
from digilab.protocol import ENGINE_SHA256_V0, sha256_engine  # noqa: E402

SOCIAIS = ("seguir", "onde_comeu")
RAIO = CM.raio_visao_celulas * CM.sub


def _texto(obj) -> str:
    return json.dumps(obj, sort_keys=True, default=repr)


class Espiao(PoliticaInstintoMundo):
    """o instinto do mundo que anota o `obs.social` e os candidatos de cada alvo. Com `escolha`, troca o ocioso e o brincar por explorar
    quando ha outro pet e escolhe o primeiro candidato da classe pedida (um cerebro que segue, ou que vai onde viu comer)."""

    def __init__(self, cfg=None, escolha: str | None = None) -> None:
        super().__init__(cfg or CONFIG_PADRAO)
        self.escolha = escolha
        self.sociais: list = []
        self.alvos: list = []
        self._obs = None

    def agir(self, obs, rng):
        a = super().agir(obs, rng)
        if self.escolha is not None and obs.social is not None and a in (AcaoPet.OCIOSO, AcaoPet.BRINCAR):
            a = AcaoPet.EXPLORAR
        self.sociais.append(obs.social)
        self._obs = obs
        return a

    def escolher_alvo(self, acao, cands, percepcao, u):
        self.alvos.append((acao, list(cands), self._obs.social, percepcao))
        if self.escolha is None:
            return None
        return next((c for c in cands if c.tipo == self.escolha), None)


class Comilao(PoliticaInstintoMundo):
    """come sempre que ve comida boa (para a disputa acontecer)"""

    def agir(self, obs, rng):
        a = super().agir(obs, rng)
        if obs.mundo is not None and any(t in ("racao", "a", "b", "c") for _, t, *_ in obs.mundo.vistos):
            return AcaoPet.COMER
        return a


def _pet_com(ident: str, entrada: int, s: int, fp, dono: str | None = "atencioso", lugar: str = "perto", corpo: str = "sem") -> PetDoGrupo:
    base = pet(ident, entrada, s, "instinto", corpo, dono=dono, lugar=lugar)
    return PetDoGrupo(ident, entrada, fp, base.fabrica_motor, base.dono, base.rotulo_dono, "teste")


def _cerebro(g: Grupo, ident: str):
    return g.motores[ident].politica._pm


# ================================================================== G-RECEPTOR-SOCIAL
def test_a_percepcao_social_nao_tem_estado_interno():
    # o quarto campo, `sentidos`, e o degrau 1b (a etapa 8, tests/test_sentidos_mundo.py): None com a ConfigSentidos desligada
    assert [f.name for f in fields(PercepcaoSocial)] == ["outros", "onde_comeu", "toque", "sentidos"]
    g = simular_grupo(CM, 101, [pet("A", 0, 101), pet("B", 0, 101)], 1)
    p = g.perceber_social("A")
    assert p.sentidos is None
    for campo in (p.outros, p.onde_comeu, p.toque):
        for item in campo:
            assert all(type(v) in (int, str) for v in item), item     # so numeros e nomes: posicao, acao, tipo, direcao, idade


def _modulos_cerebro() -> list[Path]:
    d = RAIZ / "digilab"
    return sorted((d / "policies").glob("*.py")) + sorted(d.glob("instinto*.py")) + [d / "motivo.py", d / "expressao.py"]


def test_nenhum_cerebro_importa_o_grupo_nem_os_motores():
    """os cerebros so leem o `obs` (e as funcoes puras do mundo, como o alvo padrao); nunca o Grupo, o Mundo ou um motor"""
    proibidos = {"Grupo", "PetNoGrupo", "MotorMundo", "Mundo", "Motor"}
    for arq in _modulos_cerebro():
        arvore = ast.parse(arq.read_text(encoding="utf-8"))
        for no in ast.walk(arvore):
            if isinstance(no, ast.ImportFrom):
                mod = (no.module or "").split(".")[-1]
                assert mod not in ("grupo", "engine"), (arq.name, mod)
                if mod in ("mundo", "motor_corpo"):
                    assert not {a.name for a in no.names} & proibidos, (arq.name, [a.name for a in no.names])
            elif isinstance(no, ast.Import):
                assert not any(a.name.endswith((".grupo", ".mundo", ".engine")) for a in no.names), arq.name


def test_mudar_o_estado_interno_do_outro_nao_muda_o_que_se_percebe():
    """o B com outra fome, outro humor, outros pesos e outras memorias, no mesmo lugar e fazendo o mesmo: o A percebe o mesmo. Mudar a
    posicao ou a acao do B muda (o controle positivo)."""
    fp = lambda cfg=None: PoliticaLobos(cfg or CONFIG_PADRAO, CONFIG_LOBOS_APRENDIZ, cfg_mundo=CM)  # noqa: E731
    g = simular_grupo(CM, 202, [pet("A", 0, 202), _pet_com("B", 0, 202, fp)], 1)
    antes = g.perceber_social("A")
    mb = g.motores["B"]
    assert antes.outros, "o B tem de estar a vista para o teste valer"
    mb._estado = replace(mb._estado, fome=0.01, humor=0.99, energia=0.5, higiene=0.2)
    cerebro = _cerebro(g, "B")
    for tabela in cerebro._pesos.values():
        for linha in tabela.values():
            for k in range(len(linha)):
                linha[k] += 777
    mb._viu_comer.clear()
    mb._toques["A"] = ("disputa_ganhou", 3, 0)
    mb.consumos_mundo.clear()
    assert g.perceber_social("A") == antes
    acao, pos = mb._acao_atual, mb.pet
    mb._acao_atual = AcaoPet.DORMIR if acao is not AcaoPet.DORMIR else AcaoPet.OCIOSO
    assert g.perceber_social("A") != antes
    mb._acao_atual, mb.pet = acao, (pos[0] + 1, pos[1])
    assert g.perceber_social("A") != antes


# ================================================================== G-SENTIDOS: o toque
def test_toque_os_tipos_da_secao_5_2():
    assert tipos_do_contato("A", "B", {"vencedor": "B", "perdedor": "A"}, {"A": "B", "B": None}) == {"B": "disputa_ganhou",
                                                                                                        "A": "disputa_perdeu"}
    assert tipos_do_contato("A", "B", None, {"A": "B", "B": None}) == {"A": "encostou", "B": "encostaram"}
    assert tipos_do_contato("A", "B", None, {"A": None, "B": "A"}) == {"A": "encostaram", "B": "encostou"}
    assert tipos_do_contato("A", "B", None, {"A": "B", "B": "A"}) == {"A": "encostou", "B": "encostou"}
    assert tipos_do_contato("A", "B", None, {"A": None, "B": None}) == {"A": "esbarrou", "B": "esbarrou"}
    assert set(TIPOS_TOQUE) == {"disputa_ganhou", "disputa_perdeu", "encostou", "encostaram", "esbarrou"}


def test_toque_o_contato_na_mesma_celula_ou_na_vizinha():
    s = CM.sub
    base = (10 * s + 3, 7 * s + 9)
    for dcx in (-2, -1, 0, 1, 2):
        for dcy in (-2, -1, 0, 1, 2):
            outro = (base[0] + dcx * s, base[1] + dcy * s)
            assert em_contato(base, outro, CM, 1) == (max(abs(dcx), abs(dcy)) <= 1), (dcx, dcy)
    assert em_contato((0, 0), (s - 1, s - 1), CM, 1) and not em_contato((0, 0), (2 * s, 0), CM, 1)


def test_toque_a_direcao_e_a_tabela_do_cheiro():
    esperado = {(1, 0): 1, (1, -1): 2, (0, -1): 3, (-1, -1): 4, (-1, 0): 5, (-1, 1): 6, (0, 1): 7, (1, 1): 8, (0, 0): 0}
    assert {k: direcao_vizinha(*k) for k in esperado} == esperado
    with pytest.raises(ValueError):
        direcao_vizinha(2, 0)


def _seguidor(s: int = 101, dias: int = DIAS) -> Grupo:
    return simular_grupo(CM, s, [_pet_com("A", 0, s, lambda c=None: Espiao(c, "seguir")),
                                 _pet_com("B", 0, s, lambda c=None: Comilao(c or CONFIG_PADRAO), lugar="comedouro")], dias)


def test_toque_numa_vida_encostar_e_esbarrar_so_com_as_celulas_vizinhas():
    g = _seguidor()
    tipos = {t for c in g.contatos for t in c["tipos"].values()}
    assert {"encostou", "encostaram", "esbarrou"} <= tipos
    for c in g.contatos:
        (a, b) = c["pets"]
        ca, cb = c["celulas"][a], c["celulas"][b]
        assert max(abs(ca[0] - cb[0]), abs(ca[1] - cb[1])) <= 1
        assert c["direcoes"][a] == direcao_vizinha((cb[0] > ca[0]) - (cb[0] < ca[0]), (cb[1] > ca[1]) - (cb[1] < ca[1]))
        assert {c["tipos"][a], c["tipos"][b]} <= set(TIPOS_TOQUE)
        if "encostou" in c["tipos"].values():                 # quem encostou seguiu o outro neste tick
            quem = next(i for i, t in c["tipos"].items() if t == "encostou")
            d = next(d for d in g.motores[quem].decisoes_mundo if d["tick"] == c["tick"])
            assert d["alvo"] in ("seguir", "continuar")
    # um contato por par e por tick; a memoria do toque e o ultimo contato
    assert len({c["tick"] for c in g.contatos}) == len(g.contatos)
    ultimo = g.contatos[-1]
    for eu, outro in (("A", "B"), ("B", "A")):
        assert g.motores[eu]._toques[outro] == (ultimo["tipos"][eu], ultimo["direcoes"][eu], ultimo["tick"])


def test_toque_nenhum_contato_a_duas_celulas():
    """os ticks com os dois pets a duas celulas ou mais (Chebyshev) nao tem contato"""
    g = Grupo(CM, 303)
    fp = lambda c=None: Espiao(c)  # noqa: E731
    _, fm = fabricas("instinto")
    g.entrar("A", fp(), fm, "", "")
    g.entrar("B", fp(), fm, "", "")
    vistos = 0
    for _ in range(4 * 96):
        ma, mb = g.motores["A"], g.motores["B"]
        antes = len(g.contatos)
        g.avancar(15)
        ca, cb = celula_de(*ma.pet, CM), celula_de(*mb.pet, CM)
        perto = max(abs(ca[0] - cb[0]), abs(ca[1] - cb[1])) <= 1
        assert (len(g.contatos) > antes) == perto
        vistos += not perto
    assert vistos                                              # houve ticks longe


# ================================================================== G-SENTIDOS: a visao
def test_visao_so_no_raio_em_ordem_com_a_acao_visivel():
    p = perceber_social(100, 100, 50, [("B", 100 + RAIO, 100, "comer"), ("C", 100 + RAIO + 1, 100, "dormir"),
                                       ("D", 90, 100, "explorar")], {"B": (5, 6, 40)}, {"D": ("esbarrou", 0, 45)}, RAIO)
    assert p.outros == (("D", -10, 0, 10, "explorar"), ("B", RAIO, 0, RAIO, "comer"))
    assert p.onde_comeu == (("B", 5, 6, 10),) and p.toque == (("D", "esbarrou", 0, 5),)


def test_visao_numa_vida_a_acao_e_a_da_ultima_decisao_do_outro():
    g = _seguidor(202, 2)
    for obs in _cerebro(g, "A").sociais:
        assert obs is not None
        assert all(o[3] <= RAIO for o in obs.outros) and [o[3] for o in obs.outros] == sorted(o[3] for o in obs.outros)
        assert all(o[4] in {a.value for a in AcaoPet} for o in obs.outros)
    vistos = [s for s in _cerebro(g, "A").sociais if s.outros]
    assert vistos and all(s.outros[0][0] == "B" for s in vistos)
    # decisao a decisao: o A ve a acao da ultima decisao do B (a deste tick, se o B veio antes na vez; senao a do tick anterior)
    acao_b = {d["tick"]: d["acao"] for d in g.motores["B"].decisoes_mundo}
    vez = {o["tick"]: o["ordem"] for o in g.ordens}
    for k, soc in enumerate(_cerebro(g, "A").sociais):
        t = 15 * k
        ultima = t if vez[t].index("B") < vez[t].index("A") else t - 15
        esperado = acao_b.get(ultima, AcaoPet.OCIOSO.value)
        for o in soc.outros:
            assert o[4] == esperado, (t, o, esperado)


def test_consumo_visto_so_dentro_do_raio_no_momento():
    def grupo(longe: bool) -> Grupo:
        g = Grupo(CM, 101)
        fp = lambda c=None: Comilao(c or CONFIG_PADRAO)  # noqa: E731
        _, fm = fabricas("instinto")
        g.entrar("A", fp(), fm, "", "")
        g.entrar("B", Espiao(), fm, "", "")
        nx, ny = g.mundo.ninho
        g.deixar_comida("A", "racao", nx + 40, ny)
        if longe:                                              # o observador longe, fora do raio
            g.motores["B"].pet = (nx + 40 + RAIO + 40, ny)
        for _ in range(3):
            g.avancar(15)
        return g
    perto, longe = grupo(False), grupo(True)
    assert perto.motores["A"].consumos_mundo and longe.motores["A"].consumos_mundo
    assert perto.motores["B"].vistos_comer and set(perto.motores["B"]._viu_comer) == {"A"}
    v = perto.motores["B"].vistos_comer[0]
    assert v["d"] <= RAIO and (v["x"], v["y"]) == (perto.mundo.ninho[0] + 40, perto.mundo.ninho[1])
    assert not longe.motores["B"].vistos_comer and not longe.motores["B"]._viu_comer


# ================================================================== G-MEC-SOCIAL
@pytest.mark.parametrize("s", [101, 202, 303, 404])
def test_disputa_o_primeiro_na_vez_come_o_segundo_nao_acha(s):
    """os dois veem a mesma comida longe (alem do alcance de uma decisao) e vao a ela; na decisao seguinte, quem vem primeiro na vez
    chega e come, e o outro nao acha: o alvo que ele trazia sumiu e ele nao come (MF-2)"""
    g = Grupo(CM, s)
    fp = lambda c=None: Comilao(c or CONFIG_PADRAO)  # noqa: E731
    _, fm = fabricas("instinto")
    g.entrar("A", fp(), fm, "", "")
    g.entrar("B", fp(), fm, "", "")
    nx, ny = g.mundo.ninho
    g.deixar_comida("A", "racao", nx + 80, ny)
    for _ in range(4):
        g.avancar(15)
    assert len(g.disputas) == 1
    d = g.disputas[0]
    assert d["vencedor_primeiro"] is True and d["perdedor_decidiu"] is True
    vez = next(o["ordem"] for o in g.ordens if o["tick"] == d["tick"])
    assert vez[0] == d["vencedor"]
    perdedor = g.motores[d["perdedor"]]
    dec = next(x for x in perdedor.decisoes_mundo if x["tick"] == d["tick"])
    assert dec["comeu"] is None and not perdedor.consumos_mundo
    assert [c["id"] for c in g.motores[d["vencedor"]].consumos_mundo] == [d["comida"]]
    if d["contato"]:
        c = next(c for c in g.contatos if c["tick"] == d["tick"])
        assert c["tipos"] == {d["vencedor"]: "disputa_ganhou", d["perdedor"]: "disputa_perdeu"}


def test_onde_comeu_so_depois_de_um_consumo_visto():
    g = simular_grupo(CM, 101, [_pet_com("A", 0, 101, lambda c=None: Espiao(c, "onde_comeu")),
                                _pet_com("B", 0, 101, lambda c=None: Comilao(c or CONFIG_PADRAO), lugar="comedouro")], DIAS)
    ma, esp = g.motores["A"], _cerebro(g, "A")
    primeiro_visto = ma.vistos_comer[0]["tick"]
    com_onde = [(acao, cands, soc) for acao, cands, soc, _ in esp.alvos if any(c.tipo == "onde_comeu" for c in cands)]
    assert com_onde
    for acao, cands, soc in com_onde:
        assert acao is AcaoPet.EXPLORAR
        pontos = {(c.x, c.y) for c in cands if c.tipo == "onde_comeu"}
        assert pontos == {(x, y) for _, x, y, _ in soc.onde_comeu}
    ticks = [d["tick"] for d in ma.decisoes_mundo if d["alvo"] == "onde_comeu"]
    assert ticks and min(ticks) > primeiro_visto - 1
    # as idas a onde_comeu ficam registradas (a confianca da secao 8 sai delas)
    assert ma.idas_onde_comeu and all(i["outro"] == "B" for i in ma.idas_onde_comeu)
    assert any(i["chegou"] for i in ma.idas_onde_comeu)
    for i in ma.idas_onde_comeu:
        assert (i["boas_a_vista"] is None) == (not i["chegou"])


def test_candidatos_sociais_so_no_explorar_com_o_outro_visto():
    g = _seguidor(101)
    for acao, cands, soc, p in _cerebro(g, "A").alvos:
        sociais = [c for c in cands if c.tipo in SOCIAIS]
        if acao is not AcaoPet.EXPLORAR:
            assert not sociais
            continue
        seguir = {(c.x, c.y) for c in sociais if c.tipo == "seguir"}
        assert seguir == {(p.x + dx, p.y + dy) for _, dx, dy, _, _ in soc.outros}
        # depois dos de hoje, na ordem
        k = next((i for i, c in enumerate(cands) if c.tipo in SOCIAIS), len(cands))
        assert all(c.tipo in SOCIAIS for c in cands[k:])


def test_o_padrao_do_motor_nunca_escolhe_os_sociais():
    g = simular_grupo(CM, 202, [_pet_com("A", 0, 202, lambda c=None: Espiao(c)), _pet_com("B", 0, 202, lambda c=None: Espiao(c))], DIAS)
    houve = 0
    for i in "AB":
        for acao, cands, soc, p in _cerebro(g, i).alvos:
            houve += any(c.tipo in SOCIAIS for c in cands)
            padrao = alvo_padrao_de(acao, cands, p, CM)
            assert padrao is None or padrao.tipo not in SOCIAIS
        assert not any(d["alvo"] in SOCIAIS for d in g.motores[i].decisoes_mundo)
        assert not g.motores[i].idas_onde_comeu
    assert houve
    # o explorar so com os sociais e o vagar: o padrao fica no vagar
    p = PercepcaoMundo(10, 10, 0, (), 0, 0, None)
    cands = [Alvo("vagar", 1, 1), Alvo("casa", 2, 2), Alvo("seguir", 3, 3), Alvo("onde_comeu", 4, 4)]
    assert alvo_padrao_de(AcaoPet.EXPLORAR, cands, p, CM).tipo == "vagar"


def test_tempo_a_vista_conta_as_decisoes_com_o_outro_visto():
    g = _seguidor(202, 2)
    ma, esp = g.motores["A"], _cerebro(g, "A")
    assert ma.a_vista.get("B", 0) == sum(1 for s in esp.sociais if any(o[0] == "B" for o in s.outros))
    assert ma.decisoes_no_grupo == len(esp.sociais)


# ================================================================== G2: sem o grupo, ou com um pet so
def test_g2_sem_o_grupo_e_com_um_pet_so_nada_de_social():
    fp, fm_g = fabricas("instinto")
    fm = lambda p, cfg, s: MotorMundo(p, cfg, s, obediencia_desligada=True, cfg_mundo=CM)  # noqa: E731
    esp = Espiao()
    simular_vida_mundo("atencioso", DonoComLugar(criar_dono("atencioso"), "perto", 101, "atencioso", CM), esp, 101, 1, 16, fm,
                       rotulo_dono="atencioso")
    assert esp.sociais and all(s is None for s in esp.sociais)
    assert all(not any(c.tipo in SOCIAIS for c in cands) and soc is None for _, cands, soc, _ in esp.alvos)
    g = simular_grupo(CM, 101, [_pet_com("A", 0, 101, lambda c=None: Espiao(c, "seguir"))], 1)
    esp = _cerebro(g, "A")
    assert all(s is None for s in esp.sociais) and not g.contatos and not g.disputas
    assert g.perceber_social("A") is None
    # o B so entra no dia 1: antes disso, o A nao tem percepcao social
    g = simular_grupo(CM, 101, [_pet_com("A", 0, 101, lambda c=None: Espiao(c)), pet("B", TICKS_POR_DIA, 101)], 2)
    sociais = _cerebro(g, "A").sociais
    assert all(s is None for s in sociais[:TICKS_POR_DIA // 15]) and all(s is not None for s in sociais[TICKS_POR_DIA // 15:])


def test_g_engine():
    assert sha256_engine() == ENGINE_SHA256_V0


# ================================================================== G1-GRUPO com os sentidos
CEREBROS_G1 = {
    "seguir": lambda c=None: Espiao(c, "seguir"),
    "onde": lambda c=None: Espiao(c, "onde_comeu"),
    "comilao": lambda c=None: Comilao(c or CONFIG_PADRAO),
    "lobos_alvo": lambda c=None: PoliticaLobos(c or CONFIG_PADRAO, replace(CONFIG_LOBOS_APRENDIZ, alvo_aprendido=True), cfg_mundo=CM),
}


@pytest.mark.parametrize("ca,cb,entrada_b", [("seguir", "comilao", 0), ("onde", "lobos_alvo", TICKS_POR_DIA),
                                             ("lobos_alvo", "lobos_alvo", 0)])
def test_g1_grupo_com_os_sentidos(ca, cb, entrada_b):
    _, fm = fabricas("instinto")
    pets = [_pet_com("A", 0, 101, CEREBROS_G1[ca], lugar="comedouro"), _pet_com("B", entrada_b, 101, CEREBROS_G1[cb], lugar="perto")]
    g = simular_grupo(CM, 101, pets, DIAS)
    r = reproduzir_grupo(RegistroGrupo.de_jsonl(g.registro.para_jsonl()), {"A": (CEREBROS_G1[ca], fm), "B": (CEREBROS_G1[cb], fm)}, CM)
    assert _texto(r.resumo()) == _texto(g.resumo())
    assert g.contatos and {k for k in g.resumo()} >= {"contatos", "disputas"}


def test_os_lobos_com_o_alvo_aprendido_escolhem_os_sociais():
    g = simular_grupo(CM, 202, [_pet_com("A", 0, 202, CEREBROS_G1["lobos_alvo"]), _pet_com("B", 0, 202, CEREBROS_G1["lobos_alvo"])],
                      DIAS)
    classes = {c for i in "AB" for m in _cerebro(g, i).motivos if "alvo_aprendido" in m for c in m["alvo_aprendido"]["classes"]}
    assert "seguir" in classes
    escolhidos = [d["alvo"] for i in "AB" for d in g.motores[i].decisoes_mundo]
    assert "seguir" in escolhidos


def test_no_prior_o_p0_com_lobos_e_o_instinto_do_mundo_com_o_outro_a_vista():
    """o P0 com lobos (o aprendizado desligado) e o instinto do mundo dao o mesmo grupo, com os dois pets se vendo e se tocando"""
    p0 = lambda c=None: PoliticaLobos(c or CONFIG_PADRAO, CONFIG_LOBOS, cfg_mundo=CM)  # noqa: E731
    inst = lambda c=None: PoliticaInstintoMundo(c or CONFIG_PADRAO)  # noqa: E731
    for s in (101, 202):
        resumos = []
        for fp in (p0, inst):
            g = simular_grupo(CM, s, [_pet_com("A", 0, s, fp, lugar="comedouro"), _pet_com("B", 0, s, inst)], DIAS)
            r = g.resumo()
            for i in r["pets"]:
                r["pets"][i].pop("politica")
            resumos.append(_texto(r))
        assert resumos[0] == resumos[1]
        assert g.contatos and g.motores["A"].a_vista.get("B")


def test_config_do_toque():
    with pytest.raises(ValueError):
        ConfigGrupo(ligada=True, raio_toque_celulas=-1)
    assert ConfigGrupo(ligada=True).raio_toque_celulas == 1
    assert sementes_do_grupo(101, ("A", "B"))["A"] == 101
