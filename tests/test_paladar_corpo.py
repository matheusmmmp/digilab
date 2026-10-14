"""O Paladar, etapa 2 (o corpo; docs/futuro/paladar.md, secoes 3.2, 3.3 e 4; PL-1 a PL-9 pela recomendacao): o orgao no grafo do corpo
(`sabor_q`, `saciedade_q`, os receptores `paladar_q`), o `GenomaPaladar` (rng `paladar-ovo`) e o motor do corpo levando o perfil do mundo.

- G2: com a sub-chave desligada, tests/gabaritos/paladar_vidas_de_hoje.json (gravado antes, num commit proprio) byte a byte;
- a conta exata de um consumo e das meias-vidas; G-SSS (a ração repetida satura o salgado e nao mexe no doce; sem comer, volta pela
  meia-vida); G-FOME (o gosto nao le a fome); sem quimico de prazer (PL-1);
- G-GRAFO: as checagens com o orgao, sem laco novo, e tabelas feitas para falhar;
- G-INT: o genoma e o orgao so com inteiros;
- o genoma: a rng propria, a faixa, a favorita uniforme entre os pets;
- o motor (com um lado do mundo DE TESTE: o `cpal` e o perfil no `ocorrido`, como o A combinou): as falhas altas, a percepcao e o G1.
"""
from __future__ import annotations

import ast
import json
import random
import sys
from dataclasses import fields, replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "tests"))

import gabarito_dois_pets as gdp  # noqa: E402
import gabarito_paladar as gpa  # noqa: E402

from digilab.config import (CONFIG_CORPO, CONFIG_CORPO_BANHEIRO, CONFIG_CORPO_DRIVES, CONFIG_CORPO_METABOLISMO,  # noqa: E402
                            CONFIG_LOBOS_APRENDIZ, CONFIG_MUNDO_LIGADA, CONFIG_PADRAO, ConfigCorpo, ConfigOlfato)
from digilab.corpo import (PALADAR, QUALIDADES, Corpo, div_arred, grafo_do_corpo, k_meia_vida, passo_meia_vida,  # noqa: E402
                           quimicos_de, taxas_de)
from digilab.corpo_grafo import Emissor, Grafo, GrafoInvalido, Leitura, checar  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.events import FRUTAS, AcaoUsuario, LogDeEventos  # noqa: E402
from digilab.frutas import genoma_frutas  # noqa: E402
from digilab.genoma_paladar import FLUXO, GenomaPaladar, genoma_paladar  # noqa: E402
from digilab.instinto_mundo import PoliticaInstintoMundo  # noqa: E402
from digilab.motor_corpo import PercepcaoCorpo, com_corpo  # noqa: E402
from digilab.mundo import DonoComLugar, MotorMundo, reproduzir_mundo, simular_vida_mundo  # noqa: E402
from digilab.policies.lobos import PoliticaLobos  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402
from digilab.state import Estado  # noqa: E402

S = 1024
C = CONFIG_CORPO.escala
CM = CONFIG_MUNDO_LIGADA
QUIMICA_P = replace(ConfigCorpo(ligada=True, digestao=True, vida=True), paladar=True)
DRIVES_P = replace(CONFIG_CORPO_DRIVES, paladar=True)
COMBOS = {"ligada": replace(ConfigCorpo(ligada=True), paladar=True), "quimica": QUIMICA_P, "drives": DRIVES_P,
          "banheiro": replace(CONFIG_CORPO_BANHEIRO, paladar=True), "metabolismo": replace(CONFIG_CORPO_METABOLISMO, paladar=True)}
# os perfis PROPOSTOS do desenho (secao 3.1); os do mundo sao do A (a ConfigPaladar)
PERFIS = {"a": (3 * C // 4, C // 4, 0, 0), "b": (0, 3 * C // 4, C // 4, 0), "c": (C // 4, 0, 3 * C // 4, 0), "racao": (0, 0, 0, C // 4)}
PERFIS = {k: dict(zip(QUALIDADES, v)) for k, v in PERFIS.items()}
ZERO = dict.fromkeys(QUALIDADES, 0)


def corpo(cc: ConfigCorpo = QUIMICA_P) -> Corpo:
    return Corpo.de_estado(Estado(), CONFIG_PADRAO, cc, com_mundo=True)


def ler(c: Corpo) -> dict[str, int]:
    r = c.receptores()
    return {q: r[f"paladar_{q}"] for q in QUALIDADES}


# ================================================================== G2
def test_g2_o_gabarito_da_etapa_0_byte_a_byte():
    """o mundo fisico com e sem o corpo (vidas, grupos e o corpo sozinho) e os bracos do J5, com o paladar desligado"""
    assert gpa.gerar() == json.loads(gpa.ARQUIVO.read_text(encoding="utf-8"))


def test_g2_desligado_nada_existe():
    assert not CONFIG_CORPO.paladar
    for cc in (ConfigCorpo(ligada=True), CONFIG_CORPO_DRIVES, CONFIG_CORPO_METABOLISMO):
        c = Corpo.de_estado(Estado(), CONFIG_PADRAO, cc, com_mundo=True)
        assert not set(PALADAR) & set(c.quimicos) and not any(k.startswith("paladar_") for k in c.receptores())
        with pytest.raises(ValueError, match="sem a sub-chave paladar"):
            c.estimulo_gosto(PERFIS["a"])
        with pytest.raises(ValueError, match="sem a sub-chave paladar"):
            c.estimulo_consumo_mundo("a", "madura", CM, 0.0, perfil=PERFIS["a"])


# ================================================================== a config, os nomes e a percepcao
def test_config_constantes_e_falhas():
    cc = QUIMICA_P
    assert cc.k_meia_vida_sabor == k_meia_vida(cc.meia_vida_sabor) and cc.k_meia_vida_saciedade == k_meia_vida(cc.meia_vida_saciedade)
    assert (cc.meia_vida_sabor, cc.meia_vida_saciedade, cc.saciedade_num, cc.saciedade_den) == (4, 720, 1, 2)
    assert (cc.paladar_h_min, cc.paladar_h_max, cc.paladar_h_salgado) == (-S // 2, S, S // 4)
    with pytest.raises(ValueError, match="exige ConfigCorpo.ligada"):
        ConfigCorpo(paladar=True)
    with pytest.raises(ValueError, match="saciedade_den"):
        replace(cc, saciedade_den=0)
    with pytest.raises(ValueError, match=r"\[-S, S\]"):
        replace(cc, paladar_h_max=2 * S)
    with pytest.raises(ValueError, match="h_min > paladar_h_max"):
        replace(cc, paladar_h_min=10, paladar_h_max=0)
    with pytest.raises(TypeError, match="bool"):
        replace(cc, paladar=1)


def test_os_quimicos_os_receptores_e_a_percepcao():
    c = corpo()
    assert c.quimicos[-8:] == PALADAR
    rec = {qm.nome: (qm.receptor, qm.leitura, qm.meia_vida) for qm in c.grafo.quimicos if qm.nome in PALADAR}
    for q in QUALIDADES:
        assert rec[f"sabor_{q}"] == (f"paladar_{q}", "falta", 4)                  # a concentracao, como a dor
        assert rec[f"saciedade_{q}"] == (None, None, 720)                          # sem receptor: o cerebro nao le a saciedade
    campos = {f.name for f in fields(PercepcaoCorpo)}
    assert {f"paladar_{q}" for q in QUALIDADES} <= campos
    PercepcaoCorpo(**c.receptores())                                              # os receptores cabem na percepcao
    # sem quimico nem receptor de prazer (PL-1)
    assert not [n for n in c.quimicos + tuple(c.receptores()) if "prazer" in n or "gost" in n]
    with pytest.raises(ValueError, match="mundo fisico"):
        Corpo.de_estado(Estado(), CONFIG_PADRAO, QUIMICA_P, com_mundo=False)


# ================================================================== a conta exata
def test_a_conta_exata_de_um_consumo_e_das_meias_vidas():
    c = corpo()
    sac = {"doce": 100000, "azedo": 0, "amargo": 7, "salgado": 450000}
    for q, v in sac.items():
        c.q[f"saciedade_{q}"] = v
    p = PERFIS["a"]
    c.estimulo_gosto(p)
    for q in QUALIDADES:
        assert c.q[f"sabor_{q}"] == min(C, max(0, p[q] - sac[q]))
        assert c.q[f"saciedade_{q}"] == min(C, sac[q] + div_arred(p[q], 2))
    assert ler(c) == {q: div_arred(c.q[f"sabor_{q}"] * S, C) for q in QUALIDADES}
    assert ler(c)["doce"] == div_arred((337500 - 100000) * S, C) and ler(c)["salgado"] == 0
    # o corte em C
    d = corpo()
    for _ in range(3):
        d.estimulo_gosto(dict.fromkeys(QUALIDADES, C))
    assert all(d.q[n] == C for n in PALADAR if n.startswith("saciedade_")) and d.q["sabor_doce"] == C
    # as meias-vidas do grafo, tick a tick
    sabor, saci = c.q["sabor_doce"], c.q["saciedade_doce"]
    for t in range(800):
        c.passo(Estado(tick=t))
        sabor, saci = passo_meia_vida(sabor, QUIMICA_P.k_meia_vida_sabor), passo_meia_vida(saci, QUIMICA_P.k_meia_vida_saciedade)
        assert (c.q["sabor_doce"], c.q["saciedade_doce"]) == (sabor, saci)
    assert ler(c)["doce"] == 0                                                     # o sinal na boca acabou


def test_o_sabor_acaba_antes_da_decisao_seguinte():
    c = corpo()
    c.estimulo_gosto(PERFIS["a"])
    for t in range(15):                                                           # uma decisao: 15 ticks
        c.passo(Estado(tick=t))
    inicial = div_arred(PERFIS["a"]["doce"] * S, C)
    assert ler(c)["doce"] * 10 < inicial                                          # caiu a menos de 1/10 do inicial


# ================================================================== G-SSS e G-FOME
def test_g_sss_a_racao_repetida_satura_o_salgado_e_nao_mexe_no_doce():
    com, sem = corpo(), corpo()
    respostas = []
    t = 0
    for _ in range(8):                                                            # oito racoes, uma por decisao
        com.estimulo_gosto(PERFIS["racao"])
        respostas.append(ler(com)["salgado"])
        for _ in range(15):
            com.passo(Estado(tick=t))
            sem.passo(Estado(tick=t))
            t += 1
    # cada racao responde menos; com os numeros PROPOSTOS (perfil C/4, k_sac 1/2) da quarta em diante quase nada
    assert respostas[0] > respostas[1] > respostas[2] and all(a >= b for a, b in zip(respostas, respostas[1:]))
    assert respostas[4:] == [0] * 4 and respostas[3] <= 1
    # a fruta `a` depois das racoes responde como sem elas no doce e no azedo (as qualidades que a racao nao tem)
    com.estimulo_gosto(PERFIS["a"])
    sem.estimulo_gosto(PERFIS["a"])
    assert ler(com)["doce"] == ler(sem)["doce"] > 0 and ler(com)["azedo"] == ler(sem)["azedo"]
    # sem comer, a saciedade do salgado cai pela meia-vida: a metade em 720 ticks (o passo inteiro, exato); com oito racoes ela passou de 3C/4,
    # e a racao so volta a responder depois de quase duas meias-vidas (a saciedade abaixo do perfil, C/4)
    s0 = com.q["saciedade_salgado"]
    assert s0 > 3 * C // 4
    esperado = s0
    for i in range(1, 1600):
        com.passo(Estado(tick=t))
        t += 1
        esperado = passo_meia_vida(esperado, QUIMICA_P.k_meia_vida_saciedade)
        assert com.q["saciedade_salgado"] == esperado
        if i == 720:
            assert abs(esperado - s0 / 2) <= 720 / 2
    assert esperado < PERFIS["racao"]["salgado"]
    com.estimulo_gosto(PERFIS["racao"])
    assert ler(com)["salgado"] > 0                                                # a racao volta a responder


def test_as_qualidades_compartilhadas_generalizam():
    """a `a` e a `c` dividem o doce: muita `c` baixa um pouco a resposta da `a`, e nada a da `b`"""
    com, sem = corpo(), corpo()
    for _ in range(4):
        com.estimulo_gosto(PERFIS["c"])
    for x in (com, sem):
        x.q["sabor_doce"] = x.q["sabor_azedo"] = x.q["sabor_amargo"] = 0
    com.estimulo_gosto(PERFIS["a"])
    sem.estimulo_gosto(PERFIS["a"])
    assert 0 < ler(com)["doce"] < ler(sem)["doce"] and ler(com)["azedo"] == ler(sem)["azedo"]


def test_g_fome_o_gosto_nao_le_a_fome():
    """a mesma saciedade e a fome diferente dao o mesmo sabor, no estimulo do gosto e no consumo do mapa (com a digestao)"""
    rng = random.Random(4)
    for _ in range(50):
        sac = {q: rng.randrange(C + 1) for q in QUALIDADES}
        perfil = {q: rng.randrange(C + 1) for q in QUALIDADES}
        saidas = []
        for fome in (0, C // 3, C):
            c = corpo()
            c.q["fome"] = fome
            for q in QUALIDADES:
                c.q[f"saciedade_{q}"] = sac[q]
            c.estimulo_consumo_mundo("a", "madura", CM, 0.0, perfil=perfil)
            saidas.append(({n: c.q[n] for n in PALADAR}, ler(c)))
        assert saidas[0] == saidas[1] == saidas[2]


def test_o_consumo_do_mapa_leva_o_perfil():
    c = corpo()
    c.estimulo_consumo_mundo("a", "madura", CM, -0.1, perfil=PERFIS["a"])
    d2 = corpo()
    d2.estimulo_fruta(CM.nutricao_fruta, -0.1)
    d2.estimulo_gosto(PERFIS["a"])
    assert c.q == d2.q                                                            # a nutricao, o humor e o gosto
    with pytest.raises(ValueError, match="madura leva o perfil"):
        corpo().estimulo_consumo_mundo("racao", "madura", CM)
    with pytest.raises(ValueError, match="podre nao"):
        corpo().estimulo_consumo_mundo("racao", "podre", CM, perfil=PERFIS["racao"])
    e = corpo()
    e.estimulo_consumo_mundo("c", "podre", CM)                                    # a podre: sem perfil, sem gosto
    assert all(e.q[n] == 0 for n in PALADAR)
    for ruim, erro in (({"doce": 1}, "qualidades"), ({**ZERO, "doce": C + 1}, "fora"), ({**ZERO, "doce": 1.0}, "fora"),
                       ({**ZERO, "doce": -1}, "fora")):
        with pytest.raises(ValueError, match=erro):
            corpo().estimulo_gosto(ruim)


# ================================================================== G-GRAFO
@pytest.mark.parametrize("nome", list(COMBOS))
@pytest.mark.parametrize("com_orgaos", [False, True])
def test_g_grafo_as_checagens_passam_com_o_paladar(nome, com_orgaos):
    cc = COMBOS[nome]
    co = ConfigOlfato(ligada=True, comida=True, outro_pet=True) if com_orgaos else None
    g = grafo_do_corpo(CONFIG_PADRAO, cc, taxas_de(CONFIG_PADRAO, cc), True, co)
    rel = checar(g)
    base = checar(grafo_do_corpo(CONFIG_PADRAO, replace(cc, paladar=False), taxas_de(CONFIG_PADRAO, cc), True, co))
    assert rel["lacos"] == base["lacos"]                                          # nenhum laco novo
    for q in QUALIDADES:
        for n in (f"sabor_{q}", f"saciedade_{q}"):
            assert rel["sumidouros"][n] == ["meia_vida", "teto"] and rel["fontes"][n] == [f"emissor:paladar:{q}"]
    assert g.nomes == quimicos_de(cc, True, co)


def _grafo(**kw) -> Grafo:
    g = corpo().grafo
    return Grafo(kw.get("quimicos", g.quimicos), g.reacoes, kw.get("emissores", g.emissores), g.orgaos)


def test_g_grafo_as_tabelas_feitas_para_falhar():
    g = corpo().grafo
    checar(_grafo())
    # a saciedade que reforcasse a si mesma (leitura positiva): laco de ganho 1
    reforco = tuple(replace(e, le=(Leitura("saciedade_doce", 1, 1, 1),), efeitos=(("saciedade_doce", 1),)) if e.nome == "paladar:doce"
                    else e for e in g.emissores)
    with pytest.raises(GrafoInvalido, match="laco"):
        checar(_grafo(emissores=reforco))
    with pytest.raises(GrafoInvalido, match="nao fechado"):
        checar(_grafo(emissores=g.emissores + (Emissor("paladar:umami", "estimulo", 0, (("sabor_umami", 1),), variavel=True),)))
    # o sabor sem a meia-vida e sem teto com descarte nao tem sumidouro
    sem_saida = tuple(replace(q, meia_vida=None, k_meia_vida=None, descarte=False) if q.nome == "sabor_doce" else q for q in g.quimicos)
    with pytest.raises(GrafoInvalido, match="sem sumidouro"):
        checar(_grafo(quimicos=sem_saida))


# ================================================================== G-INT
def test_g_int_o_genoma_e_o_orgao_so_com_inteiros():
    arvore = ast.parse((RAIZ / "digilab" / "genoma_paladar.py").read_text(encoding="utf-8"))
    assert not [n for n in ast.walk(arvore) if isinstance(n, ast.Constant) and type(n.value) is float]
    assert not [n for n in ast.walk(arvore) if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Div)]
    assert not [n for n in ast.walk(arvore) if isinstance(n, ast.Attribute) and n.attr in ("random", "uniform", "gauss")]
    # no corpo, as funcoes do paladar
    arvore = ast.parse((RAIZ / "digilab" / "corpo.py").read_text(encoding="utf-8"))
    fn = next(n for n in ast.walk(arvore) if isinstance(n, ast.FunctionDef) and n.name == "estimulo_gosto")
    assert not [n for n in ast.walk(fn) if isinstance(n, ast.Constant) and type(n.value) is float]
    assert not [n for n in ast.walk(fn) if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Div)]
    rng = random.Random(9)
    c = corpo(DRIVES_P)
    for t in range(500):
        if rng.random() < 0.2:
            c.estimulo_gosto({q: rng.randrange(C + 1) for q in QUALIDADES})
        c.passo(Estado(tick=t))
        assert all(type(c.q[n]) is int for n in PALADAR) and all(type(v) is int for v in ler(c).values())


# ================================================================== o genoma
def test_o_genoma_pela_rng_propria_e_na_faixa():
    estado = random.getstate()
    gs = [genoma_paladar(s, QUIMICA_P) for s in range(900)]
    assert random.getstate() == estado                                            # nao toca o random global
    s = 4242
    rng = random.Random(derivar_semente(FLUXO, s))
    esperado = {q: rng.randint(-512, 1024) for q in ("doce", "azedo", "amargo")}
    assert genoma_paladar(s, QUIMICA_P).h == {**esperado, "salgado": 256}
    assert FLUXO == "paladar-ovo"
    for g in gs:
        assert g.h["salgado"] == 256 and all(-512 <= g.h[q] <= 1024 for q in ("doce", "azedo", "amargo"))
    assert genoma_frutas(s) == genoma_frutas(s)                                    # o genoma das frutas e outra rng (nao muda)
    assert genoma_paladar(s, QUIMICA_P) == genoma_paladar(s, QUIMICA_P)
    # a fruta favorita e uniforme entre a, b e c sobre os pets (as frutas sao a mesma forma girada)
    favs = [g.favorita(PERFIS, C) for g in gs]
    assert sum(len(f) > 1 for f in favs) < 10                                      # empates sao raros
    for f in FRUTAS:
        assert 250 < sum(x[0] == f for x in favs) < 350


def test_o_valor_inato_conta_exata():
    g = GenomaPaladar({"doce": 1000, "azedo": -300, "amargo": 7, "salgado": 256})
    assert g.valor_inato(PERFIS["a"], C) == div_arred(1000 * 337500 - 300 * 112500, C)
    assert g.valor_inato(PERFIS["racao"], C) == div_arred(256 * 112500, C) == 64
    assert g.favorita(PERFIS, C) == ["a"]
    with pytest.raises(ValueError):
        GenomaPaladar({"doce": 1})
    with pytest.raises(ValueError):
        GenomaPaladar({"doce": 1.0, "azedo": 0, "amargo": 0, "salgado": 0})


# ================================================================== o motor, com um lado do mundo DE TESTE
class CpalTeste:
    """a ConfigPaladar do A, de teste: ligada e os perfis do desenho"""
    ligada = True
    perfis = PERFIS


class MundoComPerfil(MotorMundo):
    """O lado do mundo DE TESTE (o de verdade e do A, etapa 1): `cpal` no motor e o perfil no `ocorrido["comeu"]` (None na podre)."""

    sem_perfil = False

    def __init__(self, *a, **kw) -> None:
        super().__init__(*a, **kw)
        self.cpal = CpalTeste()

    def _consequencia(self, acao):
        ocorrido = super()._consequencia(acao)
        comeu = None if ocorrido is None else ocorrido["comeu"]
        if comeu is not None and not self.sem_perfil:
            comeu["perfil"] = dict(self.cpal.perfis[comeu["tipo"]]) if comeu["situacao"] == "madura" else None
        return ocorrido


MotorPaladar = com_corpo(MundoComPerfil)


def fabrica(cc=DRIVES_P, motor=MotorPaladar):
    return lambda p, cfg, s, **kw: motor(p, cfg, s, obediencia_desligada=True, cfg_mundo=CM, cfg_corpo=cc, **kw)  # noqa: E731


class Espiao:
    def __init__(self, p) -> None:
        self._p = p
        self.leituras: list = []

    def agir(self, obs, rng):
        self.leituras.append(obs.corpo)
        return self._p.agir(obs, rng)

    def __getattr__(self, nome):
        return getattr(self._p, nome)


def politica(cerebro: str, cc=DRIVES_P):
    return (PoliticaInstintoMundo(CONFIG_PADRAO) if cerebro == "instinto"
            else PoliticaLobos(CONFIG_PADRAO, CONFIG_LOBOS_APRENDIZ, cfg_mundo=CM, cfg_corpo=replace(cc, paladar=False)))


def vida(cerebro: str = "instinto", semente: int = 101, dias: int = 2):
    esp = Espiao(politica(cerebro))
    dono = gdp.DonoComBolaPerto(DonoComLugar(criar_dono("atencioso"), "perto", semente, "atencioso", CM))
    return simular_vida_mundo("atencioso", dono, esp, semente, dias, 16 * dias, fabrica(), rotulo_dono="atencioso"), esp


def test_o_motor_falha_alto_sem_o_que_o_paladar_exige():
    p = PoliticaInstintoMundo(CONFIG_PADRAO)
    with pytest.raises(ValueError, match="mundo com o paladar"):
        com_corpo(MotorMundo)(p, CONFIG_PADRAO, 1, obediencia_desligada=True, cfg_mundo=CM, cfg_corpo=DRIVES_P)

    class Desligado(MundoComPerfil):
        def __init__(self, *a, **kw) -> None:
            super().__init__(*a, **kw)
            self.cpal = type("C", (), {"ligada": False, "perfis": PERFIS})()
    with pytest.raises(ValueError, match="mundo com o paladar"):
        com_corpo(Desligado)(p, CONFIG_PADRAO, 1, obediencia_desligada=True, cfg_mundo=CM, cfg_corpo=DRIVES_P)
    with pytest.raises(ValueError, match="mundo fisico"):
        MotorPaladar(p, CONFIG_PADRAO, 1, obediencia_desligada=True, cfg_corpo=DRIVES_P)
    # o consumo sem o perfil do mundo
    MundoComPerfil.sem_perfil = True
    try:
        with pytest.raises(RuntimeError, match="sem perfil do mundo"):
            vida()
    finally:
        MundoComPerfil.sem_perfil = False


@pytest.mark.parametrize("cerebro", ["instinto", "lobos"])
def test_o_motor_leva_o_perfil_e_a_percepcao_le_o_paladar(cerebro):
    v, esp = vida(cerebro)
    m = v.motor
    assert all(all(getattr(pc, f"paladar_{q}") is not None for q in QUALIDADES) for pc in esp.leituras)
    madura = [c for c in m.consumos_mundo if c["situacao"] == "madura"]
    assert madura                                                                 # comeu de verdade
    assert any(m.corpo.q[f"saciedade_{q}"] > 0 for q in QUALIDADES)
    # a saciedade de cada qualidade e a soma do que se comeu, pelas meias-vidas: refeita por fora a partir dos consumos e dos ticks
    tipos = {c["tipo"] for c in madura}
    for q in QUALIDADES:
        if all(PERFIS[t][q] == 0 for t in tipos):
            assert m.corpo.q[f"saciedade_{q}"] == 0


def test_a_fruta_na_mao_leva_o_perfil():
    from digilab.config import CONFIG_PQP_MUNDO_LIGADA
    p = PoliticaInstintoMundo(CONFIG_PADRAO)
    m = MotorPaladar(p, CONFIG_PADRAO, 7, obediencia_desligada=True, cfg_mundo=CM, cfg_corpo=DRIVES_P, cfg_pqp=CONFIG_PQP_MUNDO_LIGADA)
    m.avancar(30)
    antes = dict(m.corpo.q)
    m.observar(AcaoUsuario.DAR_FRUTA_B)
    c = Corpo.de_estado(Estado(), CONFIG_PADRAO, DRIVES_P, com_mundo=True)
    c.q = dict(antes)
    c.estimulo_consumo_mundo("b", "madura", CM, m.efeito_frutas["b"], perfil=PERFIS["b"])
    assert {n: m.corpo.q[n] for n in PALADAR} == {n: c.q[n] for n in PALADAR}
    assert m.corpo.q["saciedade_azedo"] > 0


@pytest.mark.parametrize("cerebro", ["instinto", "lobos"])
def test_g1_o_replay_refaz_o_paladar(cerebro):
    v, esp = vida(cerebro, 202)
    fp = lambda cfg=None: Espiao(politica(cerebro))  # noqa: E731
    r = reproduzir_mundo(LogDeEventos.de_jsonl(v.motor.log.para_jsonl()), fp, CONFIG_PADRAO, 202, fabrica_motor=fabrica())
    assert r.corpo.para_dict() == v.motor.corpo.para_dict()
    assert any(r.corpo.q[n] for n in PALADAR)
    assert gdp.impressao(r) == gdp.impressao(v.motor)
    assert r.politica.leituras == esp.leituras
