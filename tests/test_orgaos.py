"""Os orgaos do Olfato e da Audicao no corpo (docs/TAREFA_V2_DOIS_PETS.md, etapa 8b; docs/futuro/dois_pets.md, secoes 5.3, 5.4 e 5.6;
DP-13 e DP-14, duas narinas e dois ouvidos), a parte do B: o receptor com limiar, adaptacao e saturacao no grafo do corpo, os emissores
externos do cheiro proprio e do rastro, e o motor do corpo entregando o estimulo.

- G2: com a ConfigOlfato e a ConfigOuvido desligadas, as vidas e o corpo de tests/gabaritos/orgaos_vidas_de_hoje.json (gravado antes, num
  commit proprio), byte a byte;
- G-ORGAO-MEC: a conta exata do limiar, da adaptacao (um cheiro constante cai a 0; a metade na meia-vida declarada no grafo) e da
  saturacao;
- G-SEM-DIRECAO (o lado do corpo): o corpo so recebe numeros por nome de receptor; pelo AST ele nao toca direcao nem o mundo; com as
  mesmas intensidades, a mesma percepcao;
- o grafo: as quatro checagens (e a 2b e a 3b) passam com os quimicos de adaptacao e os emissores externos, sem laco novo; as tabelas
  feitas para falhar falham;
- G1: o replay refaz a adaptacao (no corpo, por uma sequencia de operacoes; no motor, com um lado do mundo de teste);
- o custo em pesos (experiments/custo_orgaos.py) reproduz o artefato.
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
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import gabarito_dois_pets as gdp  # noqa: E402
import gabarito_orgaos as gor  # noqa: E402

from digilab.config import (CONFIG_CORPO_BANHEIRO, CONFIG_CORPO_DRIVES, CONFIG_CORPO_METABOLISMO, CONFIG_LOBOS_APRENDIZ,  # noqa: E402
                            CONFIG_MUNDO_LIGADA, CONFIG_OLFATO, CONFIG_OUVIDO, CONFIG_PADRAO, ConfigCorpo, ConfigOlfato,
                            ConfigOuvido)
from digilab.corpo import (PARAMETROS_OLFATO, PARAMETROS_OUVIDO, PREFIXO_ADAPTACAO, SONS, Corpo, div_arred, grafo_do_corpo,  # noqa: E402
                           k_meia_vida, leitura_orgao, orgaos_de, passo_adaptacao, passo_meia_vida, quimicos_de, taxas_de,
                           todos_receptores_orgaos)
from digilab.corpo_grafo import Emissor, Grafo, GrafoInvalido, Leitura, checar  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.events import AcaoPet, AcaoUsuario  # noqa: E402
from digilab.instinto_mundo import PoliticaInstintoMundo  # noqa: E402
from digilab.motor_corpo import PercepcaoCorpo, com_corpo  # noqa: E402
from digilab.mundo import DonoComLugar, MotorMundo, cheiro_em, reproduzir_mundo, simular_vida_mundo  # noqa: E402
from digilab.policies.lobos import PoliticaLobos  # noqa: E402
from digilab.state import Estado  # noqa: E402

S = 1024
CM = CONFIG_MUNDO_LIGADA
QUIMICA = ConfigCorpo(ligada=True, digestao=True, vida=True)
OLFATO_2 = ConfigOlfato(ligada=True, narinas=2, comida=True, outro_pet=True)
OUVIDO_2 = ConfigOuvido(ligada=True, ouvidos=2)
COMBOS = {"ligada": ConfigCorpo(ligada=True), "quimica": QUIMICA, "drives": CONFIG_CORPO_DRIVES, "banheiro": CONFIG_CORPO_BANHEIRO,
          "metabolismo": CONFIG_CORPO_METABOLISMO}
ORGAOS = {  # (olfato, ouvido)
    "comida_1": (ConfigOlfato(ligada=True, narinas=1, comida=True), None),
    "comida_2": (ConfigOlfato(ligada=True, narinas=2, comida=True), None),
    "outro_1": (ConfigOlfato(ligada=True, narinas=1, outro_pet=True), None),
    "olfato_2": (OLFATO_2, None),
    "ouvido_1": (None, ConfigOuvido(ligada=True, ouvidos=1)),
    "ouvido_2": (None, OUVIDO_2),
    "tudo_2": (OLFATO_2, OUVIDO_2),
}


def corpo(cc: ConfigCorpo = QUIMICA, co=None, cv=None) -> Corpo:
    return Corpo.de_estado(Estado(), CONFIG_PADRAO, cc, com_mundo=True, cfg_olfato=co, cfg_ouvido=cv)


def zeros(c: Corpo) -> dict[str, int]:
    return {o.receptor: 0 for o in c.orgaos}


# ================================================================== G2
def test_g2_o_gabarito_da_etapa_0_byte_a_byte():
    """as vidas de um pet (quimica, etapa 6, metabolismo; instinto e lobos, com as leituras da PercepcaoCorpo decisao a decisao), os
    grupos de dois pets com o corpo e o corpo sozinho (a tabela, o relato e uma sequencia), com os orgaos desligados"""
    assert gor.gerar() == json.loads(gor.ARQUIVO.read_text(encoding="utf-8"))


def test_g2_desligado_nada_existe():
    assert not CONFIG_OLFATO.ligada and not CONFIG_OUVIDO.ligada
    for nome, cc in COMBOS.items():
        for com_mundo in (False, True):
            c = Corpo.de_estado(Estado(), CONFIG_PADRAO, cc, com_mundo=com_mundo)
            assert c.orgaos == () and c.emissoes_externas() == {} and "orgaos" not in c.para_dict()
            assert not any(n.startswith(PREFIXO_ADAPTACAO) for n in c.quimicos)
            g = c.grafo
            assert g.orgaos == () and g.externos() == () and "orgaos" not in c.relato_grafo and "externos" not in c.relato_grafo
            with pytest.raises(ValueError, match="sem orgao"):
                c.sentir({})


# ================================================================== a config e os nomes
def test_config_registro_de_status_e_k_da_meia_vida():
    for cls, reg in ((ConfigOlfato, PARAMETROS_OLFATO), (ConfigOuvido, PARAMETROS_OUVIDO)):
        assert set(reg) == {f.name for f in fields(cls)}
        assert {s for s, _ in reg.values()} <= {"DECIDIDO", "PROPOSTO"}
    for c in (CONFIG_OLFATO, CONFIG_OUVIDO):
        assert c.k_adaptacao == k_meia_vida(c.meia_vida_adaptacao, 16)
    assert CONFIG_OLFATO.narinas == 2 and CONFIG_OUVIDO.ouvidos == 2                # DP-13 e DP-14: a opcao (b)


@pytest.mark.parametrize("kw,erro", [
    ({"ligada": True}, "sem sub-chave"), ({"ligada": True, "comida": True, "narinas": 3}, "narinas"),
    ({"limiar": -1}, "limiar"), ({"meia_saturacao": 0}, "meia_saturacao"), ({"k_adaptacao": 0}, "k_adaptacao"),
    ({"cheiro_pet": 0}, "cheiro_pet"), ({"comida": 1}, "bool")])
def test_config_olfato_falha_alto(kw, erro):
    with pytest.raises((ValueError, TypeError), match=erro):
        ConfigOlfato(**kw)


def test_config_ouvido_falha_alto():
    with pytest.raises(ValueError, match="ouvidos"):
        ConfigOuvido(ouvidos=0)
    with pytest.raises(ValueError, match="som"):
        ConfigOuvido(som=0)


def test_os_nomes_sao_os_campos_da_percepcao():
    campos = [f.name for f in fields(PercepcaoCorpo)]
    i = campos.index("conforto") + 1                                               # depois dos orgaos, o Paladar (paladar, secao 3.2)
    assert campos[i:i + len(todos_receptores_orgaos())] == list(todos_receptores_orgaos())
    assert len(todos_receptores_orgaos()) == 2 * 3 + len(SONS) * 3
    assert [o.receptor for o in orgaos_de(*ORGAOS["tudo_2"])] == [
        "olfato_comida_esq", "olfato_comida_dir", "olfato_outro_esq", "olfato_outro_dir"] + [
        f"ouvido_{s}_{lado}" for s in SONS for lado in ("esq", "dir")]
    assert [o.receptor for o in orgaos_de(*ORGAOS["comida_1"])] == ["olfato_comida"]
    # as sub-chaves sao separadas: ligar so a social nao cria o canal da comida, e vice-versa
    assert {o.canal for o in orgaos_de(*ORGAOS["outro_1"])} == {"outro"}
    assert {o.canal for o in orgaos_de(*ORGAOS["comida_2"])} == {"comida"}


def test_o_corpo_exige_o_mundo_e_confere_a_k_e_a_saturacao():
    with pytest.raises(ValueError, match="mundo fisico"):
        Corpo.de_estado(Estado(), CONFIG_PADRAO, QUIMICA, com_mundo=False, cfg_olfato=OLFATO_2)
    with pytest.raises(ValueError, match="mundo fisico"):
        Corpo.de_estado(Estado(), CONFIG_PADRAO, QUIMICA, com_mundo=False, cfg_ouvido=OUVIDO_2)
    with pytest.raises(ValueError, match="k_adaptacao"):
        corpo(co=replace(OLFATO_2, k_adaptacao=754))
    with pytest.raises(ValueError, match="saturacao"):
        corpo(cv=replace(OUVIDO_2, teto_intensidade=10 ** 6))


# ================================================================== G-ORGAO-MEC
def test_g_orgao_mec_o_passo_da_adaptacao():
    rng = random.Random(5601)
    for _ in range(5000):
        a, k = rng.randrange(0, 70000), rng.randrange(1, 65537)
        # com o estimulo 0, a adaptacao e a meia-vida do grafo, passo a passo
        assert passo_adaptacao(a, 0, k) == passo_meia_vida(a, k)
        i = rng.randrange(0, 70000)
        b = passo_adaptacao(a, i, k)
        assert min(a, i) <= b <= max(a, i)                         # nunca passa do estimulo
        assert (b == a) == (a == i)                                 # anda pelo menos 1 enquanto nao chega
        assert b - a == ((1 if i > a else -1) * max(1, abs(div_arred((i - a) * k, 2 ** 16))) if i != a else 0)


def test_g_orgao_mec_limiar_e_saturacao():
    for limiar in (0, 4, 30):
        for K in (1, 32, 500):
            for i in range(0, 300, 7):
                for a in range(0, 300, 13):
                    e = max(0, i - a - limiar)
                    r = leitura_orgao(i, a, limiar, K, S)
                    assert r == (div_arred(S * e, e + K) if e else 0)
                    assert 0 <= r < S
            assert leitura_orgao(limiar + K, 0, limiar, K, S) == S // 2          # na meia saturacao, S/2
            assert leitura_orgao(limiar, 0, limiar, K, S) == 0                  # no limiar, nada
    # monotono no estimulo
    assert [leitura_orgao(i, 0, 4, 32, S) for i in range(0, 4096)] == sorted(leitura_orgao(i, 0, 4, 32, S) for i in range(0, 4096))


def test_g_orgao_mec_um_cheiro_constante_cai_a_zero_na_meia_vida_declarada():
    """um cheiro constante: o receptor comeca na conta exata, cai a metade do estimulo menos a adaptacao na meia-vida declarada no
    grafo (a k do quimico da adaptacao, a regra da secao 3) e chega a 0, e fica em 0"""
    co = replace(ConfigOlfato(ligada=True, narinas=1, comida=True), teto_intensidade=60000)
    c = corpo(co=co)
    o = c.orgaos[0]
    qm = c.grafo.quimico(o.adaptacao)
    assert (qm.meia_vida, qm.k_meia_vida) == (co.meia_vida_adaptacao, k_meia_vida(co.meia_vida_adaptacao))
    I = 50000
    c.sentir({o.receptor: I})
    assert c.receptores()[o.receptor] == div_arred(S * (I - co.limiar), I - co.limiar + co.meia_saturacao)
    falta = []
    for t in range(2000):
        falta.append(I - c.q[o.adaptacao])
        c.passo(Estado(tick=t))
        c.sentir({o.receptor: I})
    h = co.meia_vida_adaptacao
    # a metade na meia-vida (o arredondamento por tick fica abaixo de h/2 unidades na soma)
    assert abs(falta[h] - I / 2) <= h / 2
    assert abs(falta[2 * h] - I / 4) <= h / 2
    zero = next(t for t, f in enumerate(falta) if f <= co.limiar)
    assert all(f <= co.limiar for f in falta[zero:])
    assert c.receptores()[o.receptor] == 0 and c.q[o.adaptacao] == I               # chegou ao estimulo, exato
    # tirado o cheiro, a adaptacao cai pela meia-vida do grafo, passo a passo
    a = c.q[o.adaptacao]
    for t in range(200):
        c.sentir({o.receptor: 0})
        c.passo(Estado(tick=2000 + t))
        a = passo_meia_vida(a, qm.k_meia_vida)
        assert c.q[o.adaptacao] == a


def test_g_orgao_mec_um_som_que_se_repete_habitua():
    """a habituacao: o mesmo som a cada 15 ticks pesa cada vez menos; sem o som, a adaptacao decai e o som volta a pesar"""
    c = corpo(cv=ConfigOuvido(ligada=True, ouvidos=1))
    nome = "ouvido_comendo"
    leituras, t = [], 0
    for decisao in range(12):
        for k in range(15):
            sons = zeros(c)
            sons[nome] = 64 if k < 15 else 0
            c.sentir(sons)
            if k == 0:
                leituras.append(c.receptores()[nome])
            c.passo(Estado(tick=t))
            t += 1
    assert leituras[0] > leituras[3] > leituras[-1]
    for _ in range(600):
        c.sentir(zeros(c))
        c.passo(Estado(tick=t))
        t += 1
    sons = zeros(c)
    sons[nome] = 64
    c.sentir(sons)
    assert c.receptores()[nome] == leituras[0]


def test_sentir_falha_alto_e_corta_no_teto():
    c = corpo(co=ORGAOS["comida_2"][0])
    with pytest.raises(ValueError, match="receptores dos orgaos"):
        c.sentir({"olfato_comida_esq": 1})
    with pytest.raises(ValueError, match="inteiro"):
        c.sentir({"olfato_comida_esq": 1.0, "olfato_comida_dir": 0})
    with pytest.raises(ValueError, match="inteiro"):
        c.sentir({"olfato_comida_esq": (3, 4), "olfato_comida_dir": 0})            # uma direcao nao entra
    with pytest.raises(ValueError, match="inteiro"):
        c.sentir({"olfato_comida_esq": -1, "olfato_comida_dir": 0})
    c.sentir({"olfato_comida_esq": 10 ** 9, "olfato_comida_dir": 7})
    assert c.estimulo == {"olfato_comida_esq": c.co.teto_intensidade, "olfato_comida_dir": 7}
    c.passo(Estado())
    with pytest.raises(RuntimeError, match="sem `sentir`"):                          # o estimulo de um tick nao serve ao seguinte
        c.passo(Estado(tick=1))


def test_as_narinas_sao_independentes():
    c = corpo(co=ORGAOS["comida_2"][0])
    for t in range(100):
        c.sentir({"olfato_comida_esq": 200, "olfato_comida_dir": 40})
        c.passo(Estado(tick=t))
    assert c.q["adaptacao_olfato_comida_esq"] > c.q["adaptacao_olfato_comida_dir"]
    c.sentir({"olfato_comida_esq": 40, "olfato_comida_dir": 200})
    r = c.receptores()
    assert r["olfato_comida_dir"] > r["olfato_comida_esq"] == 0                    # a narina adaptada ao forte nao sente o fraco


def test_os_orgaos_nao_mexem_no_resto_do_corpo():
    """com os mesmos estimulos de hoje, os quimicos de antes e os receptores de antes sao os de sem orgao, tick a tick"""
    rng = random.Random(77)
    for cc in (QUIMICA, CONFIG_CORPO_DRIVES, CONFIG_CORPO_METABOLISMO):
        a, b = corpo(cc), corpo(cc, *ORGAOS["tudo_2"])
        for t in range(400):
            k = rng.randrange(4)
            for x in (a, b):
                if k == 0:
                    x.acao_dono(AcaoUsuario.ALIMENTAR)
                elif k == 1:
                    x.acao_pet(AcaoPet.EXPLORAR, com_mundo=True)
            b.sentir({n: rng.randrange(0, 500) for n in b.estimulo})
            e = Estado(tick=t, dormindo=t % 7 == 0, sujeira=t % 3)
            a.passo(e)
            b.passo(e)
            assert {n: v for n, v in b.q.items() if not n.startswith(PREFIXO_ADAPTACAO)} == a.q
            rb = b.receptores()
            assert {n: v for n, v in rb.items() if n not in b.estimulo} == a.receptores()


# ================================================================== os emissores externos
def test_os_emissores_externos_so_com_o_olfato_social_e_constantes():
    assert corpo(co=ORGAOS["comida_2"][0]).emissoes_externas() == {}
    assert corpo(cv=OUVIDO_2).emissoes_externas() == {}
    co = OLFATO_2
    c = corpo(CONFIG_CORPO_DRIVES, co)
    esperado = {"cheiro_proprio": ("posicao", co.cheiro_pet), "rastro": ("decisao", co.cheiro_marca)}
    assert c.emissoes_externas() == esperado
    for e in c.grafo.externos():
        assert e.destino == "mundo" and e.le == () and e.fase == 0
    # a intensidade nao le o estado: depois de uma vida de estimulos, a mesma
    rng = random.Random(3)
    for t in range(300):
        c.acao_dono(rng.choice([AcaoUsuario.ACARICIAR, AcaoUsuario.BRINCAR, AcaoUsuario.TAPA]))
        c.sentir({n: rng.randrange(0, 300) for n in c.estimulo})
        c.passo(Estado(tick=t))
    assert c.emissoes_externas() == esperado
    # o emissor externo nao produz quimico: ele nao esta em nenhuma fase do tick nem nas fontes
    assert all(not e.externo for f in (1, 2) for e in c.grafo.da_fase(f))
    assert not any("cheiro_proprio" in s or "rastro" in s for fs in c.relato_grafo["fontes"].values() for s in fs)


# ================================================================== o grafo
@pytest.mark.parametrize("nome", list(COMBOS))
@pytest.mark.parametrize("orgaos", list(ORGAOS))
def test_grafo_as_quatro_checagens_passam_com_os_orgaos(nome, orgaos):
    cc = COMBOS[nome]
    co, cv = ORGAOS[orgaos]
    g = grafo_do_corpo(CONFIG_PADRAO, cc, taxas_de(CONFIG_PADRAO, cc), True, co, cv)
    rel = checar(g)
    base = checar(grafo_do_corpo(CONFIG_PADRAO, cc, taxas_de(CONFIG_PADRAO, cc), True))
    assert rel["lacos"] == base["lacos"]                                             # nenhum laco novo
    assert rel["pares_meia_vida_mesma_ordem"] == base["pares_meia_vida_mesma_ordem"]
    assert rel["orgaos"] == [o.receptor for o in orgaos_de(co, cv)]
    for o in g.orgaos:
        assert rel["sumidouros"][o.adaptacao] == ["meia_vida", "teto"]
        assert rel["fontes"][o.adaptacao] == [f"orgao:{o.receptor}"]
    assert g.nomes == quimicos_de(cc, True, co, cv)
    assert ("externos" in rel) == bool(co is not None and co.outro_pet)


def _grafo_com_orgao(**kw) -> Grafo:
    c = corpo(co=ORGAOS["comida_1"][0])
    g = c.grafo
    return Grafo(kw.get("quimicos", g.quimicos), kw.get("reacoes", g.reacoes), kw.get("emissores", g.emissores),
                 kw.get("orgaos", g.orgaos))


def test_grafo_as_tabelas_feitas_para_falhar():
    g = _grafo_com_orgao()
    o = g.orgaos[0]
    checar(g)
    with pytest.raises(GrafoInvalido, match="nao fechado"):
        checar(_grafo_com_orgao(orgaos=(replace(o, adaptacao="adaptacao_nada"),)))
    sem_meia = tuple(replace(q, meia_vida=None, k_meia_vida=None) if q.nome == o.adaptacao else q for q in g.quimicos)
    with pytest.raises(GrafoInvalido, match="meia-vida"):
        checar(_grafo_com_orgao(quimicos=sem_meia))
    com_receptor = tuple(replace(q, receptor="x", leitura="falta") if q.nome == o.adaptacao else q for q in g.quimicos)
    with pytest.raises(GrafoInvalido, match="nenhum receptor"):
        checar(_grafo_com_orgao(quimicos=com_receptor))
    mexe = g.emissores + (Emissor("mexe", "tick", 1, ((o.adaptacao, 1),)),)
    with pytest.raises(GrafoInvalido, match="so o orgao move"):
        checar(_grafo_com_orgao(emissores=mexe))
    with pytest.raises(GrafoInvalido, match="ja e de outro orgao"):
        checar(_grafo_com_orgao(orgaos=(o, replace(o, receptor="olfato_comida_bis"))))
    with pytest.raises(GrafoInvalido, match="receptor repetido"):
        checar(_grafo_com_orgao(orgaos=(replace(o, receptor="fome"),)))
    with pytest.raises(GrafoInvalido, match="meia saturacao"):
        checar(_grafo_com_orgao(orgaos=(replace(o, meia_saturacao=0),)))
    with pytest.raises(GrafoInvalido, match="sentido"):
        checar(_grafo_com_orgao(orgaos=(replace(o, sentido="tato"),)))
    # os emissores externos
    ext = Emissor("cheiro_proprio", "posicao", 0, (("cheiro_proprio", 32),), destino="mundo")
    checar(_grafo_com_orgao(emissores=g.emissores + (ext,)))
    for ruim, erro in ((replace(ext, le=(Leitura("fome", 1, 2),)), "degrau 3"),
                       (replace(ext, gatilho="tick", fase=1), "gatilho"), (replace(ext, efeitos=(("fome", 32),)), "canal"),
                       (replace(ext, efeitos=(("rastro", 0),)), "intensidade"), (replace(ext, variavel=True), "constante"),
                       (replace(ext, destino="lua"), "destino")):
        with pytest.raises(GrafoInvalido, match=erro):
            checar(_grafo_com_orgao(emissores=g.emissores + (ruim,)))
    with pytest.raises(GrafoInvalido, match="destino"):
        checar(_grafo_com_orgao(emissores=g.emissores + (Emissor("x", "tick", 1, (("fome", 1),), destino="lua"),)))
    with pytest.raises(GrafoInvalido, match="gatilho"):                              # gatilho externo num emissor do corpo
        checar(_grafo_com_orgao(emissores=g.emissores + (Emissor("x", "posicao", 0, (("fome", 1),)),)))


def test_o_quimico_da_adaptacao_nao_e_um_estimulo_do_resto():
    """no tick, os quimicos da adaptacao nao passam pela meia-vida generica (andariam para 0 duas vezes)"""
    c = corpo(co=ORGAOS["comida_1"][0])
    c.sentir({"olfato_comida": 300})
    c.passo(Estado())
    assert c.q["adaptacao_olfato_comida"] == passo_adaptacao(0, 300, c.co.k_adaptacao)


# ================================================================== G-SEM-DIRECAO (o lado do corpo)
def test_g_sem_direcao_o_corpo_nao_toca_direcao_nem_o_mundo():
    for arquivo in ("digilab/corpo.py", "digilab/corpo_grafo.py"):
        arvore = ast.parse((RAIZ / arquivo).read_text(encoding="utf-8"))
        nomes = {n.id for n in ast.walk(arvore) if isinstance(n, ast.Name)} | {
            n.attr for n in ast.walk(arvore) if isinstance(n, ast.Attribute)}
        assert not {x for x in nomes if "direcao" in x.lower() or x in ("DIR16", "PercepcaoMundo", "cheiro_em")}, arquivo
        modulos = {n.module for n in ast.walk(arvore) if isinstance(n, ast.ImportFrom)} | {
            a.name for n in ast.walk(arvore) if isinstance(n, ast.Import) for a in n.names}
        assert not {m for m in modulos if m and ("mundo" in m or "grupo" in m)}, arquivo


def test_g_sem_direcao_as_mesmas_intensidades_a_mesma_percepcao():
    """dois corpos com a mesma sequencia de intensidades por nome tem os mesmos receptores, decisao a decisao: o que o corpo sente e so
    o numero por receptor (de onde ele veio no mundo nao entra)"""
    rng = random.Random(91)
    a, b = corpo(CONFIG_CORPO_DRIVES, *ORGAOS["tudo_2"]), corpo(CONFIG_CORPO_DRIVES, *ORGAOS["tudo_2"])
    for t in range(500):
        sons = {n: rng.choice([0, 0, 0, rng.randrange(0, 200)]) for n in a.estimulo}
        a.sentir(dict(sons))
        b.sentir(dict(reversed(list(sons.items()))))                                 # a ordem da entrega nao importa
        assert PercepcaoCorpo(**a.receptores()) == PercepcaoCorpo(**b.receptores())
        a.passo(Estado(tick=t))
        b.passo(Estado(tick=t))
    assert a.para_dict() == b.para_dict()


# ================================================================== o motor do corpo, com um lado do mundo de teste
class MotorComNariz(com_corpo(MotorMundo)):
    """Um lado do mundo DE TESTE (o de verdade e do A): a narina esquerda e a direita a +-afastamento em x do pet, a mesma `cheiro_em`
    das comidas; o cheiro do outro e os sons em 0 (um pet so). Conta as entregas."""

    entregas = 0

    def _intensidades_do_orgao(self) -> dict[str, int]:
        type(self).entregas += 1
        x, y = self.pet
        fontes = self._fontes_de_cheiro(self._estado.tick)
        af = self.co.afastamento_narinas
        d = {o.receptor: 0 for o in self.corpo.orgaos}
        if self.co.comida:
            d["olfato_comida_esq"] = cheiro_em(x - af, y, fontes, self.cmf)
            d["olfato_comida_dir"] = cheiro_em(x + af, y, fontes, self.cmf)
        return d


def fabrica(co=OLFATO_2, cv=OUVIDO_2, cc=CONFIG_CORPO_DRIVES, motor=MotorComNariz):
    return lambda p, cfg, s, **kw: motor(p, cfg, s, obediencia_desligada=True, cfg_mundo=CM, cfg_corpo=cc, cfg_olfato=co,  # noqa: E731
                                         cfg_ouvido=cv, **kw)


class Espiao(gor.Espiao):
    def agir(self, obs, rng):
        self.leituras.append(obs.corpo)
        return self._p.agir(obs, rng)


def vida(cerebro: str = "lobos", semente: int = 101, dias: int = 2, **kw):
    p = (PoliticaInstintoMundo(CONFIG_PADRAO) if cerebro == "instinto"
         else PoliticaLobos(CONFIG_PADRAO, CONFIG_LOBOS_APRENDIZ, cfg_mundo=CM, cfg_corpo=kw.get("cc", CONFIG_CORPO_DRIVES)))
    esp = Espiao(p)
    dono = gdp.DonoComBolaPerto(DonoComLugar(criar_dono("atencioso"), "perto", semente, "atencioso", CM))
    return simular_vida_mundo("atencioso", dono, esp, semente, dias, 16 * dias, fabrica(**kw), rotulo_dono="atencioso"), esp


def test_o_motor_falha_alto_sem_o_que_o_orgao_exige():
    p = PoliticaInstintoMundo(CONFIG_PADRAO)
    MotorMundoCorpo = com_corpo(MotorMundo)
    # o lado do mundo (o gancho `_intensidades_do_orgao`) agora existe no MotorMundo (etapa 8, do A): o motor de verdade nasce com o orgao
    m = MotorMundoCorpo(p, CONFIG_PADRAO, 1, obediencia_desligada=True, cfg_mundo=CM, cfg_corpo=QUIMICA, cfg_olfato=OLFATO_2)
    assert callable(m._intensidades_do_orgao)
    with pytest.raises(ValueError, match="ConfigCorpo.ligada"):
        MotorComNariz(p, CONFIG_PADRAO, 1, obediencia_desligada=True, cfg_mundo=CM, cfg_olfato=OLFATO_2)
    with pytest.raises(ValueError, match="mundo fisico"):
        MotorComNariz(p, CONFIG_PADRAO, 1, obediencia_desligada=True, cfg_corpo=QUIMICA, cfg_ouvido=OUVIDO_2)


@pytest.mark.parametrize("cerebro", ["instinto", "lobos"])
def test_o_motor_entrega_o_estimulo_e_a_percepcao_le_os_orgaos(cerebro):
    MotorComNariz.entregas = 0
    v, esp = vida(cerebro)
    m = v.motor
    ticks = m._estado.tick
    assert MotorComNariz.entregas >= ticks                                          # pelo menos uma entrega por tick
    nomes = [o.receptor for o in m.corpo.orgaos]
    assert len(nomes) == 12
    sentiu = 0
    for pc in esp.leituras:
        for n in todos_receptores_orgaos():
            assert (getattr(pc, n) is None) == (n not in nomes)
        sentiu += any(getattr(pc, n) for n in nomes)
    assert sentiu > 0                                                               # a comida foi sentida de verdade
    # o corpo do motor e o da quimica de sempre nos quimicos de antes (a percepcao de hoje intacta nos campos de antes)
    assert all(getattr(pc, "fome") is not None for pc in esp.leituras)


@pytest.mark.parametrize("cerebro", ["instinto", "lobos"])
def test_g1_o_replay_refaz_a_adaptacao(cerebro):
    """o replay de sempre do mundo fisico, pelo texto do log, refaz o corpo com os orgaos (a adaptacao, o estimulo) e a percepcao de
    cada decisao"""
    from digilab.events import LogDeEventos
    v, esp = vida(cerebro, 202)
    cc = CONFIG_CORPO_DRIVES
    fp = (lambda cfg=None: Espiao(PoliticaInstintoMundo(CONFIG_PADRAO) if cerebro == "instinto"  # noqa: E731
                                  else PoliticaLobos(CONFIG_PADRAO, CONFIG_LOBOS_APRENDIZ, cfg_mundo=CM, cfg_corpo=cc)))
    r = reproduzir_mundo(LogDeEventos.de_jsonl(v.motor.log.para_jsonl()), fp, CONFIG_PADRAO, 202, fabrica_motor=fabrica())
    assert r.corpo.para_dict() == v.motor.corpo.para_dict()
    assert any(n.startswith(PREFIXO_ADAPTACAO) and q for n, q in r.corpo.q.items())   # a adaptacao andou de verdade
    assert gdp.impressao(r) == gdp.impressao(v.motor)
    assert r.politica.leituras == esp.leituras


# ================================================================== o custo em pesos
def test_o_custo_em_pesos_reproduz_o_artefato():
    import custo_orgaos
    gravado = json.loads(custo_orgaos.ARQUIVO.read_text(encoding="utf-8"))
    agora = custo_orgaos.medir()
    assert {k: v for k, v in agora.items() if k != "codigo"} == {k: v for k, v in gravado.items() if k != "codigo"}
    c = agora["cerebros"]["dois_pets_degrau1"]
    assert c["pesos_sem_orgao"] == 990 and c["custo_por_receptor"] == 21
    assert c["conjuntos"]["dp13_dp14"]["total"] == 990 + 12 * 21
