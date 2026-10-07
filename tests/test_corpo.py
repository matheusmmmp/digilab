"""V2, corpo, etapa 2: o corpo por baixo dos drives, no motor (docs/TAREFA_V2_CORPO_DRIVES.md, secoes 2, 9, 10 e 12).

G2: com a chave desligada, as vidas de hoje byte a byte (tests/gabaritos/corpo_vidas_de_hoje.json, gravado antes, PR #217), com o
MotorCorpo desligado na frente dos tres motores. G-HOJE (a): a quimica ligada, em malha aberta, contra o motor de hoje, tick a tick.
G-BYPASS: um drive mudado por fora do corpo falha alto. G-RECEPTOR: sem acesso privilegiado. G-ENGINE: engine.py e as classes do meio
sem mudanca. E o gancho `consequencia_corpo`, uma chamada por decisao, e o G1 com o corpo. So as sementes dos testes.
"""
from __future__ import annotations

import ast
import hashlib
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
import gabarito_corpo as gc  # noqa: E402
import gabarito_mundo as gm  # noqa: E402
from digilab.ambiente import DonoComBola, MotorAmbiente, PoliticaInstintoBola  # noqa: E402
from digilab.config import (CONFIG_BOLA_LIGADA, CONFIG_CONSEQUENCIA, CONFIG_EDUCACAO, CONFIG_FRUTAS_LIGADA,  # noqa: E402
                            CONFIG_LOBOS_APRENDIZ, CONFIG_MUNDO_LIGADA, CONFIG_PADRAO, ConfigCorpo)
from digilab.corpo import Corpo, div_arred  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.educacao import reproduzir_educacao  # noqa: E402
from digilab.events import AcaoPet, AcaoUsuario  # noqa: E402
from digilab.frutas import MotorFrutas, OfertasFrutas, PoliticaInstintoFrutas, simular_vida_frutas  # noqa: E402
from digilab.motor_corpo import ForaDoCorpo, MotorCorpo, PercepcaoCorpo, com_corpo  # noqa: E402
from digilab.mundo import MotorMundo  # noqa: E402
from digilab.obediencia import MotorPersonalidade  # noqa: E402
from digilab.policies import lobos  # noqa: E402
from digilab.policies.lobos import PoliticaLobos  # noqa: E402
from digilab.policy import PoliticaInstinto  # noqa: E402
from digilab.protocol import ENGINE_SHA256_V0, sha256_engine  # noqa: E402
from digilab.treino import MotorComFeedback, reproduzir_com_feedback, simular_vida  # noqa: E402
from digilab.treino_stats import estagio_no_tick  # noqa: E402

CFG = CONFIG_PADRAO
SO_QUIMICA = ConfigCorpo(ligada=True)
COM_ORGAOS = ConfigCorpo(ligada=True, digestao=True, vida=True)
DONOS = ("atencioso", "relapso", "aleatorio", "incoerente")
SEMENTES = (101, 202, 303)                 # so dos testes
TOL = 1e-9                                  # secao 12, G-HOJE (a)
DRIVES = ("fome", "higiene", "energia", "humor")
# as classes do meio e o estado nao mudam na etapa 2 (G-ENGINE). Quem mudar estes arquivos depois atualiza a constante, com o motivo.
SHA = {
    "digilab/ambiente.py": "e21799de3c2c24266fc4239ba76217f16488a4e393ed3d8ce263150dabeec3dd",
    "digilab/frutas.py": "d0b248d2bbbd1e64ec4901aa74b84610763064c266a1a839214ed7bd88bdc808",
    "digilab/educacao.py": "14e26d8224c60b097693c4fa96b44fe367a1b1dbeef303fe6859a5217a05aa2c",
    "digilab/obediencia.py": "43375b86cd78bedb7084f9a582771ed13032851e6e8581a0af0aed26b0777fda",
    "digilab/treino.py": "19e101d69efffa24e6451fcd5f814403fe87e11b7ce8057ff0b636492bfc638c",
    "digilab/treino_vida.py": "096da0a013fd3bfbac1b382accfd49750e35da0e24e6a45ea21015b4ca3c8e3f",
    "digilab/state.py": "dc016fda76d5e4a6a21f265450e9f02faaa9b6344fd081366b5f817596a6b9af",
}


# ================================================================== os tres motores
def _fp_padrao(cfg=None):
    return PoliticaInstinto(cfg or CFG)


def _fp_bola(cfg=None):
    return PoliticaInstintoBola(cfg or CFG, CONFIG_BOLA_LIGADA)


def _fp_frutas(cfg=None):
    return PoliticaInstintoFrutas(cfg or CFG, None, CONFIG_FRUTAS_LIGADA)


def _fabrica(mundo: str, cc: ConfigCorpo | None, corpo: bool = True):
    """a fabrica do motor de hoje (corpo=False) ou do mesmo motor com o MotorCorpo na frente"""
    if mundo == "padrao":
        cls, kw = MotorComFeedback, {}
    elif mundo == "bola":
        cls, kw = MotorAmbiente, dict(obediencia_desligada=True, cfg_bola=CONFIG_BOLA_LIGADA)
    else:
        cls, kw = MotorFrutas, dict(obediencia_desligada=True, cfg_frutas=CONFIG_FRUTAS_LIGADA)
    if not corpo:
        return lambda p, cfg, s: cls(p, cfg, s, **kw)
    C = com_corpo(cls)
    return lambda p, cfg, s: C(p, cfg, s, cfg_corpo=cc, **kw)


def _vida(mundo: str, dono: str, semente: int, cc: ConfigCorpo | None, politica_fabrica=None, corpo: bool = True, dias: int = 3):
    fm = _fabrica(mundo, cc, corpo)
    fp = politica_fabrica or {"padrao": _fp_padrao, "bola": _fp_bola, "frutas": _fp_frutas}[mundo]
    if mundo == "frutas":
        v = simular_vida_frutas(dono, criar_dono(dono), fp(CFG), semente, dias, 16 * dias, fm, OfertasFrutas(CONFIG_FRUTAS_LIGADA))
    else:
        d = DonoComBola(dono, CONFIG_BOLA_LIGADA) if mundo == "bola" else criar_dono(dono)
        v = simular_vida(dono, d, fp(CFG), semente, dias, 16 * dias, fabrica_motor=fm, rotulo_dono=dono)
    return v.motor, fp, fm


def _rejogar(mundo: str, motor, fp, fm, semente: int):
    if mundo == "padrao":
        return reproduzir_com_feedback(motor.log, fp, CFG, semente, fabrica_motor=fm)
    return reproduzir_educacao(motor.log, fp, CFG, semente, fabrica_motor=fm)


# ================================================================== G-ENGINE
def _sha_arquivo(rel: str) -> str:
    return hashlib.sha256((RAIZ / rel).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def test_g_engine_engine_e_classes_do_meio_intocados():
    assert sha256_engine() == ENGINE_SHA256_V0
    for rel, sha in SHA.items():
        assert _sha_arquivo(rel) == sha, rel


# ================================================================== G2
def test_g2_vidas_de_hoje_com_o_corpo_desligado(monkeypatch):
    """as 156 vidas do gabarito do corpo (os tres motores, P0 a P3, cinco mundos, montagem simples e completa, o so cuidado), com o
    MotorCorpo desligado na frente do MotorComFeedback, do MotorAmbiente e do MotorFrutasMundo"""
    monkeypatch.setattr(bv, "MotorComFeedback", com_corpo(MotorComFeedback))
    monkeypatch.setattr(bv, "MotorAmbiente", com_corpo(MotorAmbiente))
    monkeypatch.setattr(bv, "MotorFrutasMundo", com_corpo(bv.MotorFrutasMundo))
    gravado = json.loads(gc.ARQUIVO.read_text(encoding="utf-8"))
    vistos: dict[str, int] = {}
    difs = []
    for chave, caso in gc.casos():
        tipo, nome_b, espec = caso
        b = gc.BANCADAS[nome_b]
        v = b.vida(espec)
        if tipo == "acoplado":
            v = b.acoplar(v, "P0", "sem_ensino")
        m = v.motor
        assert isinstance(m, MotorCorpo) and not m.cc.ligada and not hasattr(m, "corpo") and "corpo" not in m.estado()
        vistos[type(m).__name__] = vistos.get(type(m).__name__, 0) + 1
        atual = gm.impressao(m, v.interacoes)
        if {k: x for k, x in atual.items() if k != "motor"} != {k: x for k, x in gravado[chave].items() if k != "motor"}:
            difs.append(chave)
    assert not difs, difs[:10]
    assert set(vistos) == {"MotorComFeedbackCorpo", "MotorAmbienteCorpo", "MotorFrutasMundoCorpo"}, vistos
    assert sum(vistos.values()) == 156


def test_desligado_nao_injeta_nem_cria_nada():
    vistas = []

    class Espiao(PoliticaInstinto):
        def agir(self, obs, rng):
            vistas.append(obs)
            return super().agir(obs, rng)

    m, _, _ = _vida("padrao", "atencioso", 101, None, politica_fabrica=lambda cfg=None: Espiao(cfg or CFG))
    hoje, _, _ = _vida("padrao", "atencioso", 101, None, corpo=False)
    assert all(o.corpo is None for o in vistas) and vistas
    assert m.estado() == hoje.estado() and m.log.para_jsonl() == hoje.log.para_jsonl()
    assert m._rng_ambiente.getstate() == hoje._rng_ambiente.getstate()


# ================================================================== G-HOJE (a), malha aberta
class Forcada:
    """O pet de teste: as acoes de uma vida de hoje, na ordem; nao sorteia. Guarda as transicoes (o sinal do N3)."""

    nome = "forcada"

    def __init__(self, acoes) -> None:
        self._acoes = list(acoes)
        self.transicoes = []

    def agir(self, obs, rng):
        return self._acoes.pop(0)

    def observar(self, t) -> None:
        self.transicoes.append(t)

    def receber_acao_dono(self, acao, tick) -> None:
        return None

    def estado_interno(self) -> dict:
        return {"nome": self.nome}


def _malha_aberta(mundo: str, dono: str, semente: int, cc: ConfigCorpo) -> dict:
    """A vida de hoje, rejogada com as acoes do pet forcadas em dois motores lado a lado: o de hoje (float) e o mesmo com o corpo,
    tick a tick, com as mesmas acoes do dono no mesmo lugar."""
    hoje, _, _ = _vida(mundo, dono, semente, None, corpo=False)
    acoes = [a for _, a in hoje.acoes_recentes(10**9)]
    fa, fb = Forcada(acoes), Forcada(acoes)
    a = _fabrica(mundo, None, corpo=False)(fa, CFG, semente)
    b = _fabrica(mundo, cc)(fb, CFG, semente)
    t = b.corpo.t
    erro = {d: 0.0 for d in DRIVES + ("saude",)}
    viradas = []

    def confere(no_tick: bool) -> None:
        ea, eb = a._estado, b._estado
        assert (ea.tick, ea.sujeira, ea.dormindo) == (eb.tick, eb.sujeira, eb.dormindo)
        for d in erro:
            erro[d] = max(erro[d], abs(getattr(ea, d) - getattr(eb, d)))
        if no_tick and ea.em_privacao(CFG) != b.corpo.em_privacao():
            viradas.append((ea.tick, dict(b.corpo.q)))
        for d in DRIVES:
            assert abs(getattr(ea, d) - getattr(eb, d)) <= TOL, (mundo, dono, semente, ea.tick, d)
        limite = TOL + len(viradas) * (t.dano_privacao - t.dano_cura) / b.corpo.C
        assert abs(ea.saude - eb.saude) <= limite, (mundo, dono, semente, ea.tick)
        if cc.vida:
            assert b.corpo.estagio() == estagio_no_tick(eb.tick, b._cfg_evo or b.corpo.cfg_evo)

    for ev in hoje.log:
        if ev.tipo == "avanco":
            for _ in range(int(ev.valor)):
                a._avancar(1)
                b._avancar(1)
                confere(True)
        elif ev.tipo == "acao_usuario":
            acao = AcaoUsuario(ev.valor)
            a._aplicar_acao_usuario(acao)
            b._aplicar_acao_usuario(acao)
            confere(False)
        else:
            raise ValueError(ev.tipo)
    assert a._estado == hoje._estado, "o motor de hoje com as acoes forcadas tem de ser a vida de hoje"
    assert a._rng_ambiente.getstate() == b._rng_ambiente.getstate(), "o corpo nao sorteia"
    if mundo == "frutas":
        assert a._rng_fruta.getstate() == b._rng_fruta.getstate()
        assert [c["fruta"] for c in a.consumos] == [c["fruta"] for c in b.consumos]
    if mundo == "bola":
        assert a.contagem_bola == b.contagem_bola
    S, ganho = 1024, CONFIG_CONSEQUENCIA.ganho
    sinais = [(lobos.sinal_homeostatico(x, S, CONFIG_CONSEQUENCIA), lobos.sinal_homeostatico(y, S, CONFIG_CONSEQUENCIA))
              for x, y in zip(fa.transicoes, fb.transicoes)]
    return {"erro": erro, "viradas": viradas, "limiar": t.limiar_privacao, "sinais": sinais, "folga": 3 * div_arred(ganho * (2 * S + 1), S),
            "motor": b}


@pytest.mark.parametrize("cc", [SO_QUIMICA, COM_ORGAOS], ids=["quimica", "orgaos"])
@pytest.mark.parametrize("mundo", ["padrao", "bola", "frutas"])
def test_g_hoje_a_malha_aberta(mundo, cc):
    total = iguais = 0
    for dono in DONOS:
        for semente in SEMENTES:
            r = _malha_aberta(mundo, dono, semente, cc)
            assert all(r["erro"][d] <= TOL for d in DRIVES), r["erro"]
            for _, q in r["viradas"]:              # toda virada do receptor de privacao e um quimico exatamente no limiar
                assert any(q[n] == r["limiar"] for n in ("fome", "desconforto", "cansaco")), q
            for x, y in r["sinais"]:
                assert abs(x - y) <= r["folga"], (x, y)
            total += len(r["sinais"])
            iguais += sum(x == y for x, y in r["sinais"])
    assert total and iguais / total >= 0.99, (iguais, total)


def test_g_hoje_a_cobre_bola_fruta_e_viradas():
    r = _malha_aberta("bola", "atencioso", 101, COM_ORGAOS)
    assert r["motor"].contagem_bola["usadas"] > 0
    r = _malha_aberta("frutas", "atencioso", 101, COM_ORGAOS)
    assert r["motor"].consumos and r["motor"].corpo.digerido_total > 0
    assert any(_malha_aberta("padrao", d, s, SO_QUIMICA)["viradas"] for d in ("relapso", "aleatorio") for s in SEMENTES)


# ================================================================== G-BYPASS
def _motor(mundo: str, cc=COM_ORGAOS, politica=None, semente: int = 101):
    fp = {"padrao": _fp_padrao, "bola": _fp_bola, "frutas": _fp_frutas}[mundo]
    return _fabrica(mundo, cc)(politica or fp(CFG), CFG, semente)


@pytest.mark.parametrize("mundo", ["padrao", "bola", "frutas"])
def test_g_bypass_estado_mudado_por_fora_falha_alto(mundo):
    m = _motor(mundo)
    m.avancar(30)
    m._estado = replace(m._estado, fome=m._estado.fome - 0.01)
    with pytest.raises(ForaDoCorpo):
        m.avancar(1)
    m = _motor(mundo)
    m.avancar(30)
    m._estado = replace(m._estado, humor=0.5)
    with pytest.raises(ForaDoCorpo):
        m.observar(AcaoUsuario.LIMPAR)


@pytest.mark.parametrize("mundo", ["padrao", "bola", "frutas"])
def test_entre_os_passos_o_estado_e_a_leitura_da_quimica(mundo):
    for dono in ("atencioso", "aleatorio"):
        m, _, _ = _vida(mundo, dono, 202, COM_ORGAOS)
        d = m.corpo.drives()
        assert all(getattr(m._estado, k) == d[k] for k in d)
        assert m.estado()["corpo"]["q"] == m.corpo.q


def test_escritor_desconhecido_falha_alto():
    """o petisco do MotorEducacao escreve a fome e nao e estimulo do corpo; um motor que escreve o humor na decisao tambem falha"""
    m = _motor("bola")
    m.avancar(15)
    with pytest.raises(ForaDoCorpo):
        m.observar(AcaoUsuario.PETISCO)

    class Intruso(MotorAmbiente):
        def _decisao_observada(self, transicao) -> None:
            super()._decisao_observada(transicao)
            self._estado = replace(self._estado, humor=min(1.0, self._estado.humor + 0.01))

    m = com_corpo(Intruso)(_fp_bola(CFG), CFG, 101, obediencia_desligada=True, cfg_bola=CONFIG_BOLA_LIGADA, cfg_corpo=SO_QUIMICA)
    with pytest.raises(ForaDoCorpo):
        m.avancar(1)


def test_o_que_o_corpo_nao_cobre_falha_alto():
    with pytest.raises(ValueError):
        com_corpo(MotorPersonalidade)(_fp_bola(CFG), CFG, 101, cfg_corpo=SO_QUIMICA)          # obediencia ligada
    with pytest.raises(ValueError):
        com_corpo(MotorAmbiente)(_fp_bola(CFG), CFG, 101, obediencia_desligada=True, cfg_corpo=SO_QUIMICA,
                                 cfg_educacao=replace(CONFIG_EDUCACAO, ligada=True))
    with pytest.raises(NotImplementedError):
        com_corpo(MotorMundo)(_fp_bola(CFG), CFG, 101, obediencia_desligada=True, cfg_mundo=CONFIG_MUNDO_LIGADA, cfg_corpo=SO_QUIMICA)
    m = _motor("bola")
    with pytest.raises(ValueError):
        m.observar(AcaoUsuario.TREINAR_CORRIDA)

    class AvancoProprio(MotorAmbiente):
        def _avancar(self, ticks):
            return super()._avancar(ticks)

    with pytest.raises(TypeError):
        com_corpo(AvancoProprio)(_fp_bola(CFG), CFG, 101, obediencia_desligada=True, cfg_corpo=SO_QUIMICA)


# ================================================================== G-RECEPTOR
def test_g_receptor_quimico_sem_receptor_nao_muda_a_observacao():
    m = _motor("frutas")
    m.avancar(200)
    antes = m._observacao()
    m.corpo.q["alimento"] = 12345
    m.corpo.q["vida"] = m.corpo.q["vida"] - 999
    assert m._observacao() == antes and m.percepcao_corpo() == antes.corpo
    m.corpo.q["fome"] = m.corpo.q["fome"] + 4500                 # com receptor: a percepcao muda
    assert m.percepcao_corpo() != antes.corpo


def test_g_receptor_percepcao_e_os_receptores_na_escala_s():
    vistas = []

    class Espiao(PoliticaInstinto):
        def agir(self, obs, rng):
            vistas.append(obs)
            return super().agir(obs, rng)

    m = _motor("padrao", politica=Espiao(CFG))
    m.avancar(600)
    assert vistas and all(isinstance(o.corpo, PercepcaoCorpo) for o in vistas)
    for o in vistas:
        for d in ("fome", "higiene", "energia", "humor", "saude"):
            v = getattr(o.corpo, d)
            assert type(v) is int and 0 <= v <= 1024
            assert abs(v / 1024 - o.vetor_estado[("fome", "higiene", "energia", "humor", "saude").index(d)]) <= 1 / 1024
        assert o.corpo.tedio is None and o.corpo.dor is None


def test_g_receptor_nenhum_cerebro_importa_o_corpo():
    arquivos = sorted((RAIZ / "digilab" / "policies").glob("*.py")) + [RAIZ / "digilab" / "policy.py", RAIZ / "digilab" / "motivo.py"]
    for arq in arquivos:
        arvore = ast.parse(arq.read_text(encoding="utf-8"))
        for no in ast.walk(arvore):
            nomes = []
            if isinstance(no, ast.Import):
                nomes = [a.name for a in no.names]
            elif isinstance(no, ast.ImportFrom):
                nomes = [no.module or ""] + [a.name for a in no.names]
            assert not any(n.split(".")[-1] in ("corpo", "motor_corpo") for n in nomes), (arq.name, nomes)


def _alcanca_corpo(obj, vistos: set, profundidade: int = 0) -> bool:
    """procura um Corpo no grafo do objeto, sem entrar nos motores (os embrulhos do motor guardam o motor, que tem o corpo)"""
    if id(obj) in vistos or profundidade > 6:
        return False
    vistos.add(id(obj))
    if isinstance(obj, Corpo):
        return True
    if isinstance(obj, MotorCorpo) or isinstance(obj, (str, int, float, bytes, type(None))):
        return False
    filhos = []
    if isinstance(obj, dict):
        filhos = list(obj.values())
    elif isinstance(obj, (list, tuple, set)):
        filhos = list(obj)
    elif hasattr(obj, "__dict__"):
        filhos = list(vars(obj).values())
    return any(_alcanca_corpo(f, vistos, profundidade + 1) for f in filhos)


def test_g_receptor_o_cerebro_nao_tem_o_objeto_do_corpo():
    cerebro = PoliticaLobos(CFG, CONFIG_LOBOS_APRENDIZ)
    m = _motor("padrao", politica=cerebro)
    m.avancar(1200)
    m.observar(AcaoUsuario.ELOGIAR)
    m.avancar(60)
    assert not _alcanca_corpo(cerebro, set())


# ================================================================== o gancho consequencia_corpo
class ComGancho(PoliticaInstintoFrutas):
    def __init__(self, *a, **kw) -> None:
        super().__init__(*a, **kw)
        self.chamadas = []
        self.decisoes = 0

    def agir(self, obs, rng):
        self.decisoes += 1
        return super().agir(obs, rng)

    def consequencia_corpo(self, acao, ocorrido, obs_depois) -> None:
        self.chamadas.append((acao, ocorrido, obs_depois))

    def receber_acao_dono(self, acao, tick) -> None:
        return None


def test_consequencia_corpo_uma_chamada_por_decisao_com_tudo_aplicado():
    m, fp, fm = _vida("frutas", "atencioso", 101, COM_ORGAOS,
                      politica_fabrica=lambda cfg=None: ComGancho(cfg or CFG, None, CONFIG_FRUTAS_LIGADA), dias=2)
    cerebro = m.politica._pf._pb._p                 # MotorFrutas > MotorAmbiente > MotorPersonalidade > o cerebro
    assert cerebro.decisoes == len(cerebro.chamadas) == m.consequencias == len(m.acoes_recentes(10**9)) > 0
    frutas = [c for c in cerebro.chamadas if any(e[0] == "fruta" for e in c[1]["estimulos"])]
    assert frutas and len(frutas) == len(m.consumos)
    for acao, oc, depois in cerebro.chamadas:
        assert oc["acao"] == acao.value and oc["estimulos"][0] == ("pet", acao.value)
        assert isinstance(depois.corpo, PercepcaoCorpo)
    # o obs_depois de um consumo ja tem a fruta: a fome e a de depois da nutricao, na grade (o tempo ainda nao passou)
    C = m.corpo.C
    for consumo, (acao, oc, depois) in zip(m.consumos, frutas):
        q_antes = round((1.0 - consumo["fome_antes"]) * C)
        assert depois.vetor_estado[0] == (C - max(0, q_antes - round(0.10 * C))) / C


def test_consequencia_corpo_com_a_bola():
    chamadas = []

    class Bola(PoliticaInstintoBola):
        def consequencia_corpo(self, acao, ocorrido, obs_depois) -> None:
            chamadas.append(ocorrido)

    m, _, _ = _vida("bola", "atencioso", 101, SO_QUIMICA, politica_fabrica=lambda cfg=None: Bola(cfg or CFG, CONFIG_BOLA_LIGADA))
    assert sum(("bola",) in c["estimulos"] for c in chamadas) == m.contagem_bola["usadas"] > 0


# ================================================================== G1 com o corpo
@pytest.mark.parametrize("mundo", ["padrao", "bola", "frutas"])
def test_g1_replay_bit_a_bit_com_o_corpo(mundo):
    fp = {"padrao": lambda cfg=None: PoliticaLobos(cfg or CFG, CONFIG_LOBOS_APRENDIZ), "bola": None, "frutas": None}[mundo]
    for cc in (SO_QUIMICA, COM_ORGAOS):
        for dono in ("atencioso", "aleatorio"):
            m, fpx, fm = _vida(mundo, dono, 202, cc, politica_fabrica=fp)
            r = _rejogar(mundo, m, fpx, fm, 202)
            for x in (m, r):
                x._resumo = json.dumps({"estado": x.estado(), "q": x.corpo.q, "bruto": repr(x._estado),
                                        "politica": x.politica.estado_interno(), "rng": x._rng_ambiente.getstate(),
                                        "acoes": x.acoes_recentes(10**9)}, sort_keys=True, default=repr)
            assert m._resumo == r._resumo, (mundo, dono)


def test_malha_fechada_sem_falso_bypass():
    """regressao: o estimulo da bola deixava o float de baixo e a leitura diferentes no ultimo bit (0,8775000000000001 x 0,8775), e a
    conferencia depois do estimulo acusava um bypass que nao existia. Toda vida da bola e das frutas, nos quatro donos e nas cinco
    sementes, roda inteira com o corpo"""
    for mundo in ("bola", "frutas"):
        for dono in DONOS:
            for semente in (101, 202, 303, 404, 505):
                m, _, _ = _vida(mundo, dono, semente, SO_QUIMICA)
                assert m.corpo.drives()["humor"] == m._estado.humor
