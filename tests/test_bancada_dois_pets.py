"""V2, W-BANCADA-DOIS-PETS (rodada 26): as faixas da rede de si (docs/PLANO_ANALISE_V2_REDE_DE_SI.md, secao 8, RS-6) e a bancada do grupo,
so o que ja da (docs/TAREFA_V2_DOIS_PETS.md, etapa 5; docs/PLANO_ANALISE_V2_DOIS_PETS.md, secoes 2 a 4), com o Grupo do #257 e o alvo
aprendido do #255.

O que se confere:
- as duas faixas da rede de si em FAIXAS_RESERVADAS com a fonte, sem colidir com as de antes, com as queimadas nem com as configs; o
  prefixo "rede_de_si" pela regra E3; as unidades dos nove prefixos sem colisao entre planos e fases;
- o mundo da unidade (o tipo ruim, o desarranjo do embaralhado, o efeito por tipo) e os cinco bracos (B so, B + Ainf, B + Aemb, B + Aing e
  o A so da calibracao do K) declarados como o plano pede;
- a fabrica do grupo pelo simular_grupo: o G1 de todo grupo (do texto do registro, e o replay que falha alto), o pet sozinho do grupo e a
  vida de hoje da bancada byte a byte, as mesmas vezes sorteadas nos bracos com os dois pets, as mesmas quedas em todo braco, o chao do dia
  K igual no B so e no B + Aing, a troca do A embaralhado no dia K, o orcamento por pet e o cuidado so (PMF-3);
- as medidas que ja tem dado no registro do grupo (a R por janela com o efeito vigente, o D_FE, o alvo aprendido por dia, a vez no tick)
  e as sociais da etapa 3 do A, #263 (o uso do seguir e do onde_comeu, o que o pet viu comer, a disputa, o toque, o tempo a vista),
  conferidas contra os registros do grupo e dos motores;
- o que espera o cerebro (as entradas sociais e o modelo dos outros, a segunda metade da etapa 4 do B) falha alto com o no `cerebro_social`,
  e os canais no mundo dos dois pets com o no `canais_fruta_mundo`; a trava e so a tabela.
So as sementes dos testes.
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

import bancada_v2 as bv  # noqa: E402
from digilab.config import CONFIG_FRUTAS_LIGADA, CONFIG_GRUPO_LIGADA, CONFIG_PADRAO, TICKS_POR_DIA  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.events import FRUTAS  # noqa: E402
from digilab.grupo import Grupo, RegistroDivergente, RegistroGrupo  # noqa: E402
from digilab.metrics import vez_no_grupo  # noqa: E402
from digilab.mundo import DonoComLugar  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402

T = TICKS_POR_DIA
CFG = {"tipo": "grupo", "bracos": ["B-so", "B+Ainf", "B+Aemb", "B+Aing", "A-so"], "sementes": [101], "k_dias": 1, "dias": 2,
       "orcamento_por_dia": 16, "ponto": "T3", "consequencia": {"ganho": 4}}
DOIS_PETS = ("B+Ainf", "B+Aemb", "B+Aing")


def _bancada(**troca) -> bv.Bancada:
    cfg = {**CFG, **troca}
    return bv.bancada_da_config({**cfg, "orcamento": cfg["orcamento_por_dia"] * cfg["dias"]})


_CACHE: dict = {}


def _grupo(braco: str, s: int = 101, k: int | None = None):
    k = (0 if not bv.BRACOS_GRUPO[braco].b else 1) if k is None else k
    chave = (braco, s, k)
    if chave not in _CACHE:
        _CACHE[chave] = _bancada().grupo(bv.EspecGrupo(braco, s, k))
    return _CACHE[chave]


# ------------------------------------------------------------------ 1. as faixas da rede de si

BASES = {
    "experimento-maior": bv.BASES_EXPERIMENTO_MAIOR, "n6": bv.BASES_N6, "n7": bv.BASES_N7, "comparacao-cerebros": bv.BASES_COMPARACAO,
    "mundo": {"calibracao": (31101, 31202, 31303, 31404, 31505), "validacao": (32101, 32202, 32303, 32404, 32505)},
    "corpo": {"calibracao": (33101, 33202, 33303, 33404, 33505), "validacao": (34101, 34202, 34303, 34404, 34505)},
    "banheiro": {"calibracao": (37101, 37202, 37303, 37404, 37505), "validacao": (38101, 38202, 38303, 38404, 38505)},
    "dois_pets": {"calibracao": (39101, 39202, 39303, 39404, 39505), "validacao": (40101, 40202, 40303, 40404, 40505),
                  "degrau_1b": (41101, 41202, 41303, 41404, 41505), "dois_donos": (42101, 42202, 42303, 42404, 42505)},
    "rede_de_si": {"calibracao": (43101, 43202, 43303, 43404, 43505), "validacao": (44101, 44202, 44303, 44404, 44505)},
}
NOVAS = {(43101, 43505): "calibracao e piloto", (44101, 44505): "validacao"}
K_UNIDADES = 40


def _numeros_das_configs() -> set[int]:
    achados: set[int] = set()

    def andar(o, chave=""):
        marca = "semente" in chave.lower() or "base" in chave.lower()
        if isinstance(o, dict):
            for k, v in o.items():
                andar(v, k)
        elif isinstance(o, list):
            for v in o:
                andar(v, chave)
        elif isinstance(o, int) and not isinstance(o, bool) and marca:
            achados.add(o)

    for p in (RAIZ / "experiments" / "configs").rglob("*.json"):
        andar(json.loads(p.read_text(encoding="utf-8")))
    return achados


def test_faixas_da_rede_de_si_reservadas_com_fonte():
    faixas = {(lo, hi): fonte for lo, hi, fonte in bv.FAIXAS_RESERVADAS}
    for (lo, hi), uso in NOVAS.items():
        assert "PLANO_ANALISE_V2_REDE_DE_SI" in faixas[(lo, hi)] and "RS-6" in faixas[(lo, hi)] and uso in faixas[(lo, hi)]
    for fase, bs in BASES["rede_de_si"].items():
        for b in bs:
            assert "rede de si" in bv.na_faixa_reservada(b), (fase, b)


def test_faixas_disjuntas_fora_das_queimadas_e_das_configs():
    los = sorted((lo, hi) for lo, hi, _ in bv.FAIXAS_RESERVADAS)
    assert all(a[1] < b[0] for a, b in zip(los, los[1:]))
    numeros = _numeros_das_configs()
    assert numeros
    for lo, hi in NOVAS:
        assert not any(q_lo <= hi and lo <= q_hi for q_lo, q_hi, _ in bv.FAIXAS_QUEIMADAS)
        assert not [n for n in numeros if lo <= n <= hi], (lo, hi)


def test_o_prefixo_da_rede_de_si_segue_a_regra():
    assert "rede_de_si" in bv.PREFIXOS_UNIDADES and set(BASES) == set(bv.PREFIXOS_UNIDADES)
    u = bv.unidades_derivadas(BASES["rede_de_si"]["calibracao"], 4, "rede_de_si")[6]
    assert (u["base"], u["k"]) == (43202, 2)
    assert u["semente"] == derivar_semente("rede_de_si", 43202, 2) and u["genoma"] == derivar_semente("rede_de_si-genoma", 43202, 2)


def test_unidades_sem_colisao_entre_planos_e_fases():
    por = {}
    for prefixo, fases in BASES.items():
        for fase, bases in fases.items():
            us = bv.unidades_derivadas(bases, K_UNIDADES, prefixo)
            por[(prefixo, fase)] = [x["semente"] for x in us] + [x["genoma"] for x in us]
    todos = [v for vs in por.values() for v in vs]
    assert len(set(todos)) == len(todos)
    numeros = _numeros_das_configs()
    for (prefixo, _), vs in por.items():
        if prefixo == "rede_de_si":
            assert all(bv.na_faixa_reservada(v) is None and v not in numeros and v not in bv.SEMENTES_TESTE for v in vs)


# ------------------------------------------------------------------ 2. o mundo da unidade e os bracos


def test_o_tipo_ruim_e_uniforme_pela_rng_propria():
    estado = random.getstate()
    contagem = {f: 0 for f in FRUTAS}
    for s in range(600):
        r = bv.tipo_ruim(s)
        assert r == FRUTAS[random.Random(derivar_semente("dois-pets-ruim", s)).randrange(3)]
        contagem[r] += 1
    assert random.getstate() == estado
    assert all(150 <= n <= 250 for n in contagem.values()), contagem


def test_o_desarranjo_do_embaralhado():
    vistos = set()
    for s in range(200):
        pi = bv.desarranjo_dois_pets(s)
        assert sorted(pi) == sorted(pi.values()) == sorted(FRUTAS) and all(pi[f] != f for f in FRUTAS)
        vistos.add(tuple(pi[f] for f in FRUTAS))
    assert len(vistos) == 2          # os dois ciclos de {a, b, c}


def test_o_efeito_por_tipo():
    cf = CONFIG_FRUTAS_LIGADA
    for ruim in FRUTAS:
        e = bv.efeito_dois_pets(ruim, cf)
        assert e[ruim] == cf.efeito_humor_ruim < 0 and all(e[f] == cf.efeito_humor_neutro for f in FRUTAS if f != ruim)
    with pytest.raises(ValueError):
        bv.efeito_dois_pets("racao", cf)


def test_os_bracos_do_plano():
    b = bv.BRACOS_GRUPO
    assert set(b) == {"B-so", "B+Ainf", "B+Aemb", "B+Aing", "A-so"}
    k = 3
    entradas = {r: bv._entradas(bv.EspecGrupo(r, 101, 0 if r == "A-so" else k)) for r in b}
    assert entradas["B-so"] == [("B", "P1", k * T)]
    assert entradas["B+Ainf"] == entradas["B+Aemb"] == [("A", "P1", 0), ("B", "P1", k * T)]
    assert entradas["B+Aing"] == [("A", "P0", k * T), ("B", "P1", k * T)]
    assert entradas["A-so"] == [("A", "P1", 0)]
    assert [b[r].companheiro for r in ("B+Ainf", "B+Aemb", "B+Aing")] == ["informativo", "embaralhado", "ingenuo"]
    bc = _bancada()
    assert bc.dias_do_grupo(bv.EspecGrupo("B+Ainf", 101, k)) == k + 2 and bc.dias_do_grupo(bv.EspecGrupo("A-so", 101, 0)) == 2
    # a semente de cada pet: o A com a do grupo, o B pela derivacao do segundo pet (o desenho)
    eg = bv.EspecGrupo("B+Ainf", 101, k)
    assert bc.espec_do_pet(eg, "A").semente == 101 and bc.espec_do_pet(eg, "B").semente == derivar_semente("segundo-pet", 101)


@pytest.mark.parametrize("braco,k", [("B+Ainf", 0), ("B+Aemb", 0), ("A-so", 1), ("B-so", -1), ("XX", 1)])
def test_k_e_braco_invalidos_falham_alto(braco, k):
    with pytest.raises((ValueError, KeyError)):
        bv._validar_espec_grupo(bv.EspecGrupo(braco, 101, k))


def test_o_grupo_vive_no_mundo_fisico_e_com_orcamento_por_dia():
    with pytest.raises(ValueError):
        bv._validar_espec_grupo(bv.EspecGrupo("B-so", 101, 1, mundo="descasado"))
    with pytest.raises(ValueError):
        bv._validar_espec_grupo(bv.EspecGrupo("B-so", 101, 1, lugar="sofa"))
    with pytest.raises(ValueError):
        bv.Bancada(2, 33).orcamento_por_dia()


# ------------------------------------------------------------------ 3. a fabrica do grupo pelo simular_grupo


@pytest.mark.parametrize("braco", sorted(bv.BRACOS_GRUPO))
@pytest.mark.parametrize("s", [101, 202])
def test_g1_de_todo_grupo(braco, s):
    v = _grupo(braco, s)
    bc = _bancada()
    texto = v.grupo.registro.para_jsonl()
    bc.conferir_replay_grupo(v, texto)                      # do texto, de novo
    assert v.grupo.registro.cabecalho["pets"].keys() == {i for i, _, _ in bv._entradas(v.espec)}
    with pytest.raises(bv.ReplayDivergiu):
        bc.conferir_replay_grupo(v, texto.replace('"avanco"', '"avanco" ', 1))
    # um registro adulterado (um avanco a menos no fim) nao reproduz o grupo
    reg = RegistroGrupo.de_jsonl(texto)
    curto = RegistroGrupo(reg.cabecalho, reg.eventos[:-1])
    with pytest.raises((RegistroDivergente, bv.ReplayDivergiu)):
        r = bc.rejogar_grupo(curto, v.espec)
        if bv._resumo_grupo(r) != bv._resumo_grupo(v.grupo):
            raise bv.ReplayDivergiu("o grupo curto diverge")


@pytest.mark.parametrize("s", [101, 202])
@pytest.mark.parametrize("lugar", ["comedouro", "perto"])
def test_o_pet_sozinho_do_grupo_e_a_vida_de_hoje(s, lugar):
    """O gate da bancada (etapa 5): um pet so no grupo, entrando no tick 0 com a semente do grupo, e a vida de hoje da bancada no mundo
    fisico (o simular_vida_fisico, o cuidado so) com a mesma semente, o mesmo braco, o mesmo dono, o mesmo lugar e o mesmo efeito, byte a
    byte. (O "B so" do plano nao e a vida de hoje: e o B, com a semente dele, entrando no dia K de um mundo sem ninguem, secao 3.)"""
    bc = _bancada()
    eg = bv.EspecGrupo("A-so", s, 0, lugar=lugar)
    v = bc.grupo(eg)
    a = v.grupo.motores["A"]
    espec = bc.espec_do_pet(eg, "A")
    dono = DonoComLugar(criar_dono("atencioso"), lugar, s, "atencioso", bc.cfg_mundo_de(bv.mundo_de("fisico")))
    fm = bc.fabrica_motor_do_grupo(eg, "A")
    hoje, retirados = bv.simular_vida_fisico(dono, bc.bancada_grupo().politica(espec, CONFIG_PADRAO), s, bc.dias, bc.orcamento,
                                             "atencioso", lambda p, c, sem: fm(p, c, sem))
    assert bv.resumo_motor(a) == bv.resumo_motor(hoje)
    assert bv._interno(a) == bv._interno(hoje)
    assert retirados == v.retirados["A"] and v.interacoes["A"] == bc.orcamento


def test_as_mesmas_vezes_sorteadas_nos_bracos_com_os_dois_pets():
    g = {b: _grupo(b).grupo for b in DOIS_PETS}
    for b in DOIS_PETS:
        assert g[b].ordens and all(o["tick"] >= T for o in g[b].ordens)            # so do dia K em diante
    assert g["B+Ainf"].ordens == g["B+Aemb"].ordens == g["B+Aing"].ordens
    assert g["B+Ainf"].resumo()["rng_ordem"] == g["B+Aemb"].resumo()["rng_ordem"] == g["B+Aing"].resumo()["rng_ordem"]
    for b in ("B-so", "A-so"):
        assert _grupo(b).grupo.ordens == [] and _grupo(b).grupo.resumo()["rng_ordem"] is None


def _sorteio(quedas) -> list:
    """o que sai do fluxo das arvores (o tick, a arvore, quantas e onde); os ids das comidas colocadas dependem do que o dono deixou"""
    return [(q["tick"], q["arvore"], q["sorteadas"], q["pontos"]) for q in quedas]


def test_as_mesmas_quedas_em_todo_braco():
    quedas = {b: _sorteio(_grupo(b).grupo.mundo.quedas) for b in ("B-so", *DOIS_PETS)}
    assert all(q == quedas["B-so"] for q in quedas.values()) and quedas["B-so"]
    assert _sorteio(_grupo("A-so").grupo.mundo.quedas) == [q for q in quedas["B-so"] if q[0] < 2 * T]


def test_o_chao_do_dia_k():
    """R-3: o B so e o B + Aing entram num mundo sem consumo nos K dias, entao o chao do dia K e o mesmo; no B + Ainf e no B + Aemb o A
    viveu os K dias, e o chao difere pelo que ele comeu e pelo que o dono dele deixou."""
    bc = _bancada()
    chao = {b: bc.chao_na_entrada(_grupo(b)) for b in ("B-so", *DOIS_PETS)}
    assert all(c["tick"] == T for c in chao.values())
    assert chao["B-so"] == chao["B+Aing"]
    assert chao["B+Ainf"] != chao["B-so"] and "racao/madura" in chao["B+Ainf"]["comidas"]
    with pytest.raises(ValueError):
        bc.chao_na_entrada(_grupo("A-so"))


def test_a_troca_do_a_embaralhado_no_dia_k():
    v = _grupo("B+Aemb")
    a, b = v.grupo.motores["A"], v.grupo.motores["B"]
    ef = _bancada().efeitos_do_grupo(v.espec)
    assert isinstance(a, bv.MotorMundoTroca) and not isinstance(b, bv.MotorMundoTroca)
    assert ef["ruim_embaralhado"] == ef["pi"][ef["ruim"]] != ef["ruim"]
    assert a.troca == {"tick": T, "antes": ef["embaralhado"], "depois": ef["verdadeiro"]}
    assert a.efeito_frutas == b.efeito_frutas == ef["verdadeiro"]
    assert a.efeito_no_tick(T - 1) == ef["embaralhado"] and a.efeito_no_tick(T) == ef["verdadeiro"]
    # no informativo, o mesmo A sem troca
    assert not isinstance(_grupo("B+Ainf").grupo.motores["A"], bv.MotorMundoTroca)
    assert _grupo("B+Ainf").grupo.motores["A"].efeito_frutas == ef["verdadeiro"]


def test_a_troca_falha_alto_fora_do_grupo_e_num_avanco_que_passa_dela():
    bc = _bancada()
    eg = bv.EspecGrupo("B+Aemb", 101, 1)
    fm = bc.fabrica_motor_do_grupo(eg, "A")
    pol = bc.bancada_grupo().politica(bc.espec_do_pet(eg, "A"), CONFIG_PADRAO)
    with pytest.raises(ValueError):
        fm(pol, CONFIG_PADRAO, 101)                          # sem o Mundo do grupo
    g = Grupo(bc.cfg_mundo_de(bv.mundo_de("fisico")), 101, replace(CONFIG_GRUPO_LIGADA), CONFIG_PADRAO)
    g.entrar("A", pol, fm, "lobos/P1", "atencioso")
    with pytest.raises(RuntimeError, match="passou da troca"):
        g.avancar(T + 15)


def test_o_orcamento_por_pet_e_o_cuidado_so():
    for b in ("B-so", *DOIS_PETS, "A-so"):
        v = _grupo(b)
        for i, m in v.grupo.motores.items():
            dias = (v.grupo.tick - m.entrada_mundo) // T
            assert v.interacoes[i] == 16 * dias
            projecao = v.grupo.registro.projecao(i)
            sinais = [e for e in projecao if e.tipo == "acao_usuario" and str(e.valor) in bv.SINAIS]
            assert sinais == []                              # PMF-3: o elogio e a bronca nao chegam (ficam em `retirados`)
            gestos = sum(1 for e in projecao if e.tipo in ("deixar_comida", "deixar_bola"))
            acoes = sum(1 for e in projecao if e.tipo == "acao_usuario")
            assert gestos + acoes + v.retirados[i] == v.interacoes[i]


def test_o_cerebro_do_plano_tem_o_alvo_aprendido():
    v = _grupo("B+Aing")
    for i, m in v.grupo.motores.items():
        cerebro = m.politica.estado_interno()
        # os dois tem a tabela do alvo; o P1 aprende, o P0 (o aprendizado desligado) fica no prior e usa o alvo padrao do motor
        assert ("pesos_alvo_mundo" in cerebro) and (cerebro["pesos_alvo_mundo"] != cerebro["pesos_alvo_mundo_prior"]) == (i == "B")
    assert v.grupo.registro.cabecalho["pets"]["A"]["cerebro"] == "lobos/P0"
    assert v.grupo.registro.cabecalho["pets"]["B"]["cerebro"] == "lobos/P1"


# ------------------------------------------------------------------ 4. as medidas que ja tem dado


def test_vez_no_grupo_com_resposta_conhecida():
    ordens = [{"tick": 0, "decidem": ["A", "B"], "ordem": ["B", "A"]}, {"tick": 15, "decidem": ["A", "B"], "ordem": ["A", "B"]},
              {"tick": 30, "decidem": ["A", "B"], "ordem": ["B", "A"]}, {"tick": 1500, "decidem": ["A", "B"], "ordem": ["B", "A"]}]
    assert vez_no_grupo(ordens, "B") == {"juntos": 4, "primeiro": 3, "fracao_primeiro": 0.75}
    assert vez_no_grupo(ordens, "A", (0, 1440)) == {"juntos": 3, "primeiro": 1, "fracao_primeiro": 1 / 3}
    assert vez_no_grupo([], "A") == {"juntos": 0, "primeiro": 0, "fracao_primeiro": None}
    with pytest.raises(ValueError):
        vez_no_grupo([{"tick": 0, "decidem": ["A", "B"], "ordem": ["A", "A"]}], "A")


@pytest.mark.parametrize("braco", sorted(bv.BRACOS_GRUPO))
def test_as_medidas_saem_do_registro_do_grupo(braco):
    bc = _bancada()
    v = _grupo(braco)
    m = bc.medir_grupo(v)
    assert m["braco"] == braco and m["ruim"] == bv.tipo_ruim(101) and m["ordens"] == len(v.grupo.ordens)
    assert set(m["sociais"]) == set(v.grupo.motores) and m["modelo_dos_outros"]["pendente"] == "cerebro_social"
    for i, p in m["pets"].items():
        mt = v.grupo.motores[i]
        ini = mt.entrada_mundo
        janelas = p["taxa_fruta_ruim"]
        assert janelas["vida"]["inicio"] == ini and janelas["vida"]["fim"] == v.grupo.tick
        assert janelas["primeiros_7"] == {**janelas["primeiros_7"], "inicio": ini, "fim": ini + min(7, p["dias_vividos"]) * T}
        assert [janelas[f"dia_{d + 1}"]["inicio"] for d in range(p["dias_vividos"])] == [ini + d * T for d in range(p["dias_vividos"])]
        assert ("ate_k" in janelas) == (ini < v.espec.k * T)
        frutas = [c for c in mt.consumos_mundo if c["tipo"] in FRUTAS and c["situacao"] == "madura"]
        assert janelas["vida"]["n"] == p["consumos_fruta_madura"] == len(frutas)
        assert sum(p["consumos"].values()) == len(mt.consumos_mundo)
        assert p["d_fe"]["vida"]["n"] == len(mt.decisoes_mundo) and 0.0 <= p["d_fe"]["primeiros_7"]["d_fe"] <= 1.0
        assert p["vez"] == vez_no_grupo(v.grupo.ordens, i)
        # o alvo aprendido no fim de cada dia (o P1 aprende, com as classes seguir e onde_comeu; o P0 fica no prior)
        assert len(p["pesos_alvo_por_dia"]) == p["dias_vividos"]
        if p["braco"] == "P1":
            assert p["pesos_alvo_por_dia"][-1] == mt.politica.estado_interno()["pesos_alvo_mundo"]
            assert "seguir" in p["pesos_alvo_por_dia"][-1]["tempo_livre:explorar"]
        else:                                               # o P0: o prior todos os dias
            prior = mt.politica.estado_interno()["pesos_alvo_mundo_prior"]
            assert p["pesos_alvo_por_dia"] == [prior] * p["dias_vividos"]


def test_a_r_do_a_embaralhado_usa_o_efeito_de_cada_lado_da_troca(monkeypatch):
    """A R de cada consumo usa o efeito vigente no tick: o desarranjado antes do dia K e o verdadeiro depois (no A embaralhado); o
    verdadeiro sempre nos outros. Conferido trocando os consumos do motor por consumos com a resposta conhecida."""
    bc = _bancada()
    v = _grupo("B+Aemb")
    ef = bc.efeitos_do_grupo(v.espec)
    ruim, ruim_e = ef["ruim"], ef["ruim_embaralhado"]
    neutro = next(f for f in FRUTAS if f not in (ruim, ruim_e))
    sinteticos = [(10, ruim_e), (20, ruim), (30, neutro), (T + 10, ruim_e), (T + 20, ruim), (T + 30, ruim)]
    original = bv.Bancada.rejogar_grupo

    def rejogar(self, registro, eg, envolver=None):
        g = original(self, registro, eg, envolver)
        if envolver is not None:                             # so no replay de medicao
            g.motores["A"].consumos_mundo[:] = [{"tick": t, "tipo": f, "situacao": "madura", "como": "comer"} for t, f in sinteticos]
        return g

    monkeypatch.setattr(bv, "_resumo_grupo", lambda g: ())
    monkeypatch.setattr(bv.Bancada, "rejogar_grupo", rejogar)
    taxa = bc.medir_grupo(v)["pets"]["A"]["taxa_fruta_ruim"]
    assert (taxa["ate_k"]["n"], taxa["ate_k"]["ruins"]) == (3, 1)        # antes de K, so o pi(ruim) faz mal
    assert (taxa["depois_k"]["n"], taxa["depois_k"]["ruins"]) == (3, 2)  # depois, o ruim verdadeiro


# ------------------------------------------------------------------ 5. as medidas sociais (etapa 3 do A), o que espera o B e os canais


def _conferir_sociais(v, sociais: dict) -> None:
    """As medidas sociais contra os registros do grupo e dos motores, contadas por fora."""
    g = v.grupo
    ruim = bv.tipo_ruim(v.espec.semente)
    for i, m in g.motores.items():
        so = sociais[i]
        exp = [d for d in m.decisoes_mundo if d["acao"] == "explorar"]
        assert sum(u["explorar"] for u in so["uso_candidatos"]) == len(exp)
        for c in ("seguir", "onde_comeu"):
            assert sum(u[c] for u in so["uso_candidatos"]) == sum(1 for d in exp if d["alvo"] == c)
        for u in so["uso_candidatos"]:
            assert u["fracao_seguir"] == (u["seguir"] / u["explorar"] if u["explorar"] else None)
        assert so["vistos_comer"]["n"] == len(m.vistos_comer) == sum(so["vistos_comer"]["por_tipo"].values())
        comidos = {c["tick"]: c for o, mo in g.motores.items() if o != i for c in mo.consumos_mundo}
        assert so["vistos_comer"]["ruins_maduros"] == sum(1 for x in m.vistos_comer if comidos[x["tick"]]["tipo"] == ruim
                                                          and comidos[x["tick"]]["situacao"] == "madura")
        minhas = [d for d in g.disputas if i in (d["vencedor"], d["perdedor"])]
        assert so["disputas"]["n"] == len(minhas) and so["disputas"]["ganhou"] == sum(d["vencedor"] == i for d in minhas)
        for x, d in zip(so["disputas"]["lista"], minhas):
            assert (x["d_eu"], x["d_outro"]) == ((d["d_vencedor"], d["d_perdedor"]) if x["ganhou"] else (d["d_perdedor"], d["d_vencedor"]))
        toques = [c["tipos"][i] for c in g.contatos if i in c["pets"]]
        assert sum(n for t in so["toque_por_dia"] for k, n in t.items() if k != "dia") == len(toques)
        assert so["a_vista"] == dict(m.resumo_social()["a_vista"]) and so["idas_onde_comeu"]["n"] == len(m.idas_onde_comeu)


@pytest.mark.parametrize("braco", sorted(bv.BRACOS_GRUPO))
def test_as_medidas_sociais_saem_dos_registros(braco):
    v = _grupo(braco)
    sociais = _bancada().medidas_sociais(v)
    _conferir_sociais(v, sociais)
    if len(v.grupo.motores) == 1:                            # sozinho: nada social
        so = next(iter(sociais.values()))
        assert so["vistos_comer"]["n"] == so["disputas"]["n"] == 0 and so["a_vista"] == {}
    else:                                                    # com os dois: eles se veem e se tocam
        assert all(so["a_vista"] and so["vistos_comer"]["n"] for so in sociais.values()) and v.grupo.contatos


def test_a_disputa_e_o_uso_dos_candidatos_sociais():
    """Numa vida com disputa (B + Aing, semente 303): o vencedor e o perdedor, as distancias de cada um e o uso do seguir e do onde_comeu."""
    v = _grupo("B+Aing", 303)
    sociais = _bancada().medidas_sociais(v)
    _conferir_sociais(v, sociais)
    assert len(v.grupo.disputas) == 1 and sum(so["disputas"]["n"] for so in sociais.values()) == 2
    assert sum(so["disputas"]["ganhou"] for so in sociais.values()) == 1
    assert sum(u["seguir"] + u["onde_comeu"] for so in sociais.values() for u in so["uso_candidatos"]) > 0


def test_o_modelo_dos_outros_falha_alto_com_o_no():
    v = _grupo("B+Ainf")
    with pytest.raises(NotImplementedError, match="modelo dos outros"):
        _bancada().modelo_dos_outros(v)
    assert "sentidos_grupo" not in bv.NOS_PENDENTES and "segunda metade" in bv.NOS_PENDENTES["cerebro_social"]


def _cfg_plano(**troca) -> dict:
    return {**CFG, "bracos": ["B+Ainf", "B+Aemb"], "unidades": {"bases": [39101], "k": 1, "prefixo": "dois_pets"},
            "plano": "docs/PLANO_ANALISE_V2_DOIS_PETS.md", **{k: v for k, v in troca.items()}}


def test_a_run_do_plano_falha_alto_com_o_no():
    cfg = {k: v for k, v in _cfg_plano().items() if k != "sementes"}
    with pytest.raises(NotImplementedError, match="entradas sociais"):
        bv.validar_config_grupo(cfg)
    sem_plano = {k: v for k, v in cfg.items() if k != "plano"}
    with pytest.raises(bv.SementeSemPlano):
        bv.validar_config_grupo(sem_plano)
    bv.validar_config_grupo({**CFG, "sementes": [101, 202]})                    # as sementes dos testes rodam


def test_a_trava_do_cerebro_social_e_so_a_tabela(monkeypatch):
    monkeypatch.setattr(bv, "NOS_PENDENTES", {k: v for k, v in bv.NOS_PENDENTES.items() if k != "cerebro_social"})
    cfg = {k: v for k, v in _cfg_plano().items() if k != "sementes"}
    bv.validar_config_grupo(cfg)
    with pytest.raises(NotImplementedError, match="entra com a segunda metade"):   # a segunda trava: o cerebro ainda nao o tem
        _bancada().modelo_dos_outros(_grupo("B+Ainf"))


@pytest.mark.parametrize("troca", [{"montagem": "completa"}, {"consequencia": {"ganho": 4, "canais_ligados": True}}])
def test_os_canais_falham_alto_com_o_no(troca):
    with pytest.raises(NotImplementedError, match="canal do humor"):
        bv.validar_config_grupo({**CFG, **troca})
    bc = _bancada(**troca)
    with pytest.raises(NotImplementedError, match="canal do humor"):
        bc.grupo(bv.EspecGrupo("B+Aing", 101, 1))
    # o P0 nao aprende: sem canais nele (o A ingenuo); no B, P1, com
    eg = bv.EspecGrupo("B+Aing", 101, 1)
    assert not bc.canais_no_pet(bc.espec_do_pet(eg, "A")) and bc.canais_no_pet(bc.espec_do_pet(eg, "B"))


def test_a_trava_dos_canais_e_so_a_tabela_e_guarda_uma_falha_real(monkeypatch):
    """Sem a entrada `canais_fruta_mundo`, o grupo com a montagem completa monta, e o cerebro do mundo fisico falha alto quando o pet come
    a fruta que mexe no humor (CANAIS-REFORCO): o no guarda uma falha real, do B, e nao so uma escolha da bancada. Com um pet so (o A so,
    semente 505), sem nada social no caminho: a falha e do canal do humor, nao do grupo."""
    monkeypatch.setattr(bv, "NOS_PENDENTES", {k: v for k, v in bv.NOS_PENDENTES.items() if k != "canais_fruta_mundo"})
    bv.validar_config_grupo({**CFG, "montagem": "completa"})
    bc = _bancada(montagem="completa")
    assert len(bc.pets_do_grupo(bv.EspecGrupo("B+Aing", 101, 1))) == 2
    with pytest.raises(RuntimeError, match="CANAIS-REFORCO"):
        bc.grupo(bv.EspecGrupo("A-so", 505, 0))


# ------------------------------------------------------------------ 6. a config e o rodar


def test_config_do_grupo_falha_alto():
    for ruim in ({**CFG, "bracos": ["P1"]}, {**CFG, "bracos": ["B-so", "B-so"]}, {**CFG, "tipo": "vida"}, {**CFG, "sobra": 1},
                 {**{k: v for k, v in CFG.items() if k != "sementes"}},
                 {**{k: v for k, v in CFG.items() if k != "sementes"}, "unidades": {"bases": [101], "k": 1, "prefixo": "mundo"}},
                 {**CFG, "k_dias": 0}, {**CFG, "sementes": [15101], "plano": "docs/PLANO_ANALISE_V2_DOIS_PETS.md"}):
        with pytest.raises((ValueError, KeyError, bv.SementeSemPlano)):
            bv.validar_config_grupo(ruim)


def test_rodar_grupo_e_a_fumaca(tmp_path):
    cfg = json.loads((RAIZ / "experiments" / "configs" / "v2_dois_pets" / "fumaca.json").read_text(encoding="utf-8"))
    bv.validar_config_grupo(cfg)
    assert set(cfg["bracos"]) == set(bv.BRACOS_GRUPO) and set(cfg["sementes"]) <= bv.SEMENTES_TESTE
    pequeno = {**cfg, "sementes": [101], "bracos": ["B-so", "B+Ainf"]}
    assert bv.main(["--config", str(_gravar(tmp_path / "c.json", pequeno)), "--saida", str(tmp_path / "saida")]) == 0
    medidas = json.loads((tmp_path / "saida" / "medidas.json").read_text(encoding="utf-8"))
    assert sorted(m["braco"] for m in medidas.values()) == ["B+Ainf", "B-so"]
    assert len(list((tmp_path / "saida" / "grupos").glob("*.jsonl"))) == 2
    meta = json.loads((tmp_path / "saida" / "meta.json").read_text(encoding="utf-8"))
    assert "grupo_sha256" in meta and meta["engine_sha256"]


def _gravar(caminho: Path, cfg: dict) -> Path:
    caminho.write_text(json.dumps(cfg), encoding="utf-8")
    return caminho
